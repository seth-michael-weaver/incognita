"""Reader for the fission reference dumps: `fis<ZZZAAA>.txt` (barrier and transition-state
parameters, `fissionparout.f90`) and `fis<ZZZAAA>.trans` (fission transmission coefficients,
`tfissionout.f90`).

Task: T11 (physics/hf/CONTRACT.md §7). Acceptance test: A-fis (§6).

`FAMILIES["fission"]` in the T0 harness matches only `fission.tot`, so none of the per-nucleus
fission files reach `features/hf_reference/*.parquet` (T14 reported the same gap). This module
reads them straight out of the `features/hf_reference/raw/*.tar.gz` archives, the way T5 gated
A-trans off the tarballs, so A-fis does not depend on a harness change.

Two traps in `fis*.trans`, both TALYS's and both preserved here under honest names:

* the `Gamma(J,+-)` columns are labelled `[eV]` but hold `tfis / (2 pi rho)` in **MeV**
  (tfission.f90:333, tfissionout.f90:80-83), so `gamma_mev` is the field name here;
* the file is opened in append mode and never rewound, so one nucleus's blocks run
  ``nex = maxex -> 1`` for incident energy 1, then again for incident energy 2, and so on
  (multiple.f90:486). :func:`transmission_groups` splits on the energy going back up, which is
  what recovers `Ex(maxex)` -- the energy at which `densprepare` built that nucleus's fission
  level-density grid.
"""

from __future__ import annotations

import re
import tarfile
from dataclasses import dataclass
from pathlib import Path

import numpy as np

REFERENCE_ROOT = Path("features/hf_reference/raw")
ACTINIDE_TARGETS = ("Am241", "Pu239", "Th232", "U235", "U238")


def raw_dir() -> Path:
    """The directory holding the reference tarballs (`features/hf_reference/raw`)."""
    import os

    return Path(os.environ.get("INCOGNITA_HF_REFERENCE_RAW", REFERENCE_ROOT)).expanduser()


def available(target: str, variant: str = "default") -> bool:
    return (raw_dir() / f"{variant}__{target}.tar.gz").exists()


def extract(target: str, variant: str, workdir: Path) -> Path:
    """Unpack the `fis*` and barrier `ld*.b0N` members of one reference archive, once."""
    out = workdir / f"{variant}__{target}"
    if out.is_dir() and any(out.glob("fis*")) and any(out.glob("ld*.b0*")):
        return out
    out.mkdir(parents=True, exist_ok=True)
    with tarfile.open(raw_dir() / f"{variant}__{target}.tar.gz") as tf:
        for m in tf.getmembers():
            name = Path(m.name).name
            keep = name.startswith("fis") or (name.startswith("ld") and ".b0" in name)
            if keep and m.isfile():
                src = tf.extractfile(m)
                if src is not None:
                    (out / name).write_bytes(src.read())
    return out


# ----------------------------------------------------------------------------- fis*.txt

_KV = re.compile(r"^#\s*(.*?):\s*(.*?)\s*$")
_FIS_NAME = re.compile(r"^fis(\d{3})(\d{3})\.(txt|trans)$")


def nuclide_of(path: Path) -> tuple[int, int]:
    """(Z, A) from a `fis<ZZZ><AAA>.{txt,trans}` file name (tfissionout.f90:65-67)."""
    m = _FIS_NAME.match(path.name)
    if not m:
        raise ValueError(f"not a fission dump name: {path.name}")
    return int(m.group(1)), int(m.group(2))


@dataclass(frozen=True)
class BarrierReference:
    """One barrier or class-II well of `fis*.txt`: the scalars TALYS prints for it, its head
    states and the rotational band built on them.

    `states` and `rotational` are ``(energy [MeV], spin, parity)`` triples in file order.

    TALYS: fissionparout.f90:1 (fissionparout)
    """

    kind: str  # "Head band transition states" | "Class 2 states"
    index: int
    values: dict[str, float]
    states: list[tuple[float, float, int]]
    rotational: list[tuple[float, float, int]]


@dataclass(frozen=True)
class FissionParametersReference:
    Z: int
    A: int
    nfisbar: int
    nclass2: int
    scalars: dict[str, float]
    blocks: list[BarrierReference]

    def barrier(self, i: int) -> BarrierReference | None:
        for b in self.blocks:
            if b.kind.startswith("Head band") and b.index == i:
                return b
        return None

    def well(self, i: int) -> BarrierReference | None:
        for b in self.blocks:
            if b.kind.startswith("Class") and b.index == i:
                return b
        return None


# YANDF bookkeeping keys that are not fission parameters.
_SKIP = frozenset({"columns", "entries", "Z", "A"})


def _state_row(line: str) -> tuple[float, float, int] | None:
    tok = line.split()
    if len(tok) != 4 or tok[3] not in ("+", "-"):
        return None
    return float(tok[1]), float(tok[2]), 1 if tok[3] == "+" else -1


def read_fission_parameters(path: Path) -> FissionParametersReference:
    """Parse a `fis*.txt` barrier-parameter dump.

    The file interleaves three kinds of `quantity:` block -- head-band states, class-II states
    and the `Rotational bands` built on either -- and puts the class-II scalars *before* their
    quantity header while the barrier scalars come *after* it (fissionparout.f90:122-131 vs
    :160-164). Both orders are handled by carrying a `pending` scalar dict.

    TALYS: fissionparout.f90:1 (fissionparout)
    """
    Z, A = nuclide_of(path)
    blocks: list[BarrierReference] = []
    pending: dict[str, float] = {}
    cur: dict | None = None
    target = "states"
    nfisbar = nclass2 = 0

    def flush() -> None:
        nonlocal cur
        if cur is not None:
            blocks.append(
                BarrierReference(cur["kind"], cur["i"], cur["v"], cur["states"], cur["rot"])
            )
            cur = None

    for line in path.read_text().splitlines():
        if not line.startswith("#"):
            row = _state_row(line)
            if row is not None and cur is not None:
                cur[target].append(row)
            continue
        m = _KV.match(line)
        if not m:
            continue
        key, val = m.group(1).strip(), m.group(2)
        if key == "type":
            if val in ("Head band transition states", "Class 2 states"):
                flush()
                cur = {"kind": val, "i": 0, "v": dict(pending), "states": [], "rot": []}
                pending = {}
                target = "states"
            elif val == "Rotational bands":
                target = "rot"
            continue
        if key == "Number of fission barriers":
            nfisbar = int(val)
            continue
        if key == "Number of sets of class2 states":
            nclass2 = int(val)
            continue
        if key in _SKIP:
            continue
        try:
            fval = float(val)
        except ValueError:
            continue
        if key in ("Fission barrier", "Set  of class2 states", "Set of class2 states"):
            if cur is not None and target == "states":
                cur["i"] = int(fval)
            else:
                pending["_index"] = fval
            continue
        if cur is not None and target == "states":
            cur["v"][key] = fval
        else:
            pending[key] = fval
    flush()
    for b in blocks:
        if b.kind.startswith("Class") and b.index == 0 and "_index" in b.values:
            object.__setattr__(b, "index", int(b.values.pop("_index")))
    return FissionParametersReference(Z, A, nfisbar, nclass2, dict(pending), blocks)


# ----------------------------------------------------------------------------- fis*.trans


@dataclass(frozen=True)
class TransmissionBlock:
    """One excitation-energy block of `fis*.trans`: T, Gamma, tau and rho over J and parity.

    Arrays are `(nJ, 2)` with the parity axis ordered `(-1, +1)` (contract §4.2). `spin[j]` is
    the physical spin `J + odd/2`.
    """

    Z: int
    A: int
    exinc_mev: float
    spin: np.ndarray
    tfis: np.ndarray
    gamma_mev: np.ndarray
    tau_s: np.ndarray
    density_per_mev: np.ndarray


def read_transmission(path: Path) -> list[TransmissionBlock]:
    """Parse every block of a `fis*.trans` dump, in file order.

    TALYS: tfissionout.f90:1 (tfissionout)
    """
    Z, A = nuclide_of(path)
    out: list[TransmissionBlock] = []
    exinc: float | None = None
    rows: list[list[float]] = []

    def flush():
        if exinc is None or not rows:
            return
        a = np.asarray(rows, dtype=np.float64)
        out.append(
            TransmissionBlock(
                Z=Z,
                A=A,
                exinc_mev=exinc,
                spin=a[:, 0],
                tfis=a[:, [1, 2]],
                gamma_mev=a[:, [3, 4]],
                tau_s=a[:, [5, 6]],
                density_per_mev=a[:, [7, 8]],
            )
        )

    for line in path.read_text().splitlines():
        if line.startswith("#"):
            m = _KV.match(line)
            if m and m.group(1).strip() == "Excitation energy [MeV]":
                flush()
                rows = []
                exinc = float(m.group(2))
            continue
        tok = line.split()
        if len(tok) == 9:
            rows.append([float(x) for x in tok])
    flush()
    return out


def transmission_groups(blocks: list[TransmissionBlock]) -> list[list[TransmissionBlock]]:
    """Split a `fis*.trans` block list into one group per incident energy.

    TALYS appends to the file while walking ``nex = maxex -> 1`` for each incident energy
    (multiple.f90:486), so a group ends as soon as the excitation energy stops decreasing. The
    first block of a group is the top bin, which is where `densprepare` built that nucleus's
    fission level-density grid (densprepare.f90:411).
    """
    groups: list[list[TransmissionBlock]] = []
    for b in blocks:
        if groups and b.exinc_mev < groups[-1][-1].exinc_mev:
            groups[-1].append(b)
        else:
            groups.append([b])
    return groups


_QUANTITIES = ("tfis", "gamma_mev", "tau_s", "density_per_mev")


def stale_masks(blocks: list[TransmissionBlock]) -> list[dict[str, np.ndarray]]:
    """Per block, the cells TALYS did not recompute, as boolean `(nJ, 2)` masks.

    `tfis`, `gamfis`, `taufis` and `denfis` are module arrays that `tfission` overwrites only
    for the (J, parity) pairs its caller visits: `comptarget` restricts J to the window the
    compound nucleus is formed in, and `multiple` skips a (J, parity) whose bin population is
    below `popepsB` (multiple.f90:508). `tfissionout` then prints the whole array, so an
    untouched cell carries whatever was last written into it -- possibly at a different
    excitation energy, a different bin, or a different incident energy.

    All four quantities fall steeply with excitation energy and are printed to six significant
    digits, so a cell whose value is *bit identical* to the last value printed for that same
    cell earlier in the file was not recomputed. That is the test used here. It can only ever
    discard points, never manufacture agreement.
    """
    last: dict[str, np.ndarray] = {}
    out: list[dict[str, np.ndarray]] = []
    for b in blocks:
        masks: dict[str, np.ndarray] = {}
        for name in _QUANTITIES:
            arr = getattr(b, name)
            prev = last.get(name)
            mask = np.zeros(arr.shape, dtype=bool)
            if prev is not None:
                n = min(arr.shape[0], prev.shape[0])
                mask[:n] = arr[:n] == prev[:n]
            masks[name] = mask
            carry = np.zeros((max(arr.shape[0], 0 if prev is None else prev.shape[0]), 2))
            if prev is not None:
                carry[: prev.shape[0]] = prev
            carry[: arr.shape[0]] = arr
            last[name] = carry
        out.append(masks)
    return out


__all__ = [
    "ACTINIDE_TARGETS",
    "BarrierReference",
    "FissionParametersReference",
    "TransmissionBlock",
    "available",
    "extract",
    "nuclide_of",
    "raw_dir",
    "read_fission_parameters",
    "read_transmission",
    "stale_masks",
    "transmission_groups",
]
