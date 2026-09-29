"""The incident-channel inputs T13 injects: the optical-model parameters TALYS hands ECIS at each
incident energy, and the coupled band, read straight out of the reference dump archives.

`omppar_n.out` is the *emission*-grid neutron OMP, so it cannot be read at the 23 incident
energies. What can is the `OPTICAL MODEL PARAMETERS FOR INCIDENT CHANNEL` block that
`incidentecis.f90:342` writes into `talys.out` once per incident energy -- the same 20 numbers
`ecisinput.f90:140-160` writes onto ECIS's cards. It is printed with the `f6.2/f6.3` format of
incidentecis.f90:347, i.e. two or three decimals, which is coarser than ECIS's own `f10.5` card
and puts a floor of about 1e-4 relative on anything injected from it.

This is a T13-local reader, not a change to T0's loader (T0 has finished; see
`<lab-run>/requests.md`). The proposed loader patch is on the board.

Task: T13 (physics/hf/CONTRACT.md §7). Acceptance test: A-inc (§6).
"""

from __future__ import annotations

import os
import re
import tarfile
from pathlib import Path

import torch
from torch import Tensor

from physics.hf.core.tensors import DTYPE

RAW = Path(__file__).resolve().parents[3] / "features" / "hf_reference" / "raw"
CACHE = Path(os.environ.get("HF_RAW_CACHE", Path.home() / ".cache" / "incognita" / "hf_raw"))

# the 20 columns of incidentecis.f90:344-348, in the order they are printed
COLUMNS: tuple[str, ...] = (
    "v_mev", "rv_fm", "av_fm", "w_mev", "rw_fm", "aw_fm",
    "vd_mev", "rvd_fm", "avd_fm", "wd_mev", "rwd_fm", "awd_fm",
    "vso_mev", "rvso_fm", "avso_fm", "wso_mev", "rwso_fm", "awso_fm", "rc_fm", "ef_mev",
)  # fmt: skip

_HEAD = "OPTICAL MODEL PARAMETERS FOR INCIDENT CHANNEL"


class InjectedOMP:
    """OMP parameters on the incident energy axis (E,), one attribute per entry of `COLUMNS` plus
    `e_inc_mev`. Shaped exactly like T4's `OMPParameters` as far as the solver is concerned.
    """

    __slots__ = ("e_inc_mev", *COLUMNS)

    def __init__(self, e_inc_mev: Tensor, **cols: Tensor) -> None:
        self.e_inc_mev = e_inc_mev
        for k in COLUMNS:
            setattr(self, k, cols[k])

    def select(self, mask: Tensor) -> InjectedOMP:
        """The same parameters on a subset of the energy axis. `mask` is a boolean (E,) tensor or an
        index tensor -- whatever indexes a 1-D tensor.

        Needed because `incident_coupled` only accepts E <= soswitch, so a reference target's 23
        energies have to be cut to the 18 below it (board note `[T12 -> T13]`).
        """
        return InjectedOMP(
            self.e_inc_mev[mask].contiguous(),
            **{k: getattr(self, k)[mask].contiguous() for k in COLUMNS},
        )


def talys_out(target: str, variant: str = "default") -> list[str]:
    """`talys.out` of one reference run, extracted to the shared raw cache on first use."""
    d = CACHE / f"{variant}__{target}"
    p = d / "talys.out"
    if not p.is_file():
        src = RAW / f"{variant}__{target}.tar.gz"
        if not src.is_file():
            raise FileNotFoundError(src)
        CACHE.mkdir(parents=True, exist_ok=True)
        with tarfile.open(src) as tf:
            m = tf.getmember(f"{variant}__{target}/talys.out")
            tf.extract(m, CACHE, filter="data")
        (CACHE / f"{variant}__{target}").rename(d) if not d.is_dir() else None
    return p.read_text().splitlines()


def incident_omp(target: str, variant: str = "default"):
    """The incident-channel OMP parameters at every incident energy, as TALYS prints them.

    Returns an object with `e_inc_mev` (E,) and one (E,) tensor per entry of `COLUMNS`, ready to
    hand to `physics.hf.ecis.solver.solve_rotational` as its `p`.
    """
    lines = talys_out(target, variant)
    rows: list[list[float]] = []
    for i, ln in enumerate(lines):
        if _HEAD not in ln:
            continue
        for j in range(i + 1, min(i + 10, len(lines))):
            s = lines[j]
            if not s.strip() or "Energy" in s or "on" in s.split()[:3]:
                continue
            vals = _split_fixed(s)
            if len(vals) == 21:
                rows.append(vals)
                break
    if not rows:
        raise KeyError(f"no {_HEAD!r} block in talys.out for {target}/{variant}")
    a = torch.tensor(rows, dtype=DTYPE)
    return InjectedOMP(
        a[:, 0].contiguous(),
        **{name: a[:, k + 1].contiguous() for k, name in enumerate(COLUMNS)},
    )


def _split_fixed(s: str) -> list[float]:
    """`(1x, f8.3, 1x, 6(f6.2, f6.3, f6.3), f6.3, f8.3)` -- fields abut, so split by width, not by
    whitespace (the same trap T9 hit with es17.9e3)."""
    widths = [1, 8, 1] + [6] * 18 + [6, 8]
    out, pos = [], 0
    for w in widths:
        chunk = s[pos : pos + w]
        pos += w
        if w == 1:
            continue
        try:
            out.append(float(chunk))
        except ValueError:
            return []
    return out


def coupled_band(Z: int, A: int):
    """The coupled band TALYS builds at `incidentecis.f90:234-250`, from T2's ported levels and
    deformation: level energies, spins and parities, plus `rotpar` and K for the rotational model
    and the per-band multipolarity `lband` and deformation `defpar` for the vibrational one, and
    `deftype == 'D'` (ECIS `lo(6)`).
    """
    from physics.hf.input.defaults import default_options
    from physics.hf.structure.deformation import deformation
    from physics.hf.structure.levels import discrete_levels
    from physics.hf.structure.masses import masses as get_masses

    o = default_options(Z, A)
    ms = get_masses(o)
    lv = discrete_levels(Z, A, o, ms)
    d = deformation(Z, A, o, lv, ms)
    e, sp, pa, lam, beta, iph = [], [], [], [], [], []
    vb, jb, km, bb = [], [], [], []
    for i in range(1, d.ndef + 1):
        ii = int(d.indexlevel[i])
        if d.leveltype[ii] not in ("V", "R"):
            continue
        if d.colltype == "R" and int(d.vibband[i]) > o.maxband:
            continue
        e.append(float(lv.all_e_mev[ii]))
        sp.append(float(lv.all_spin[ii]))
        pa.append(int(lv.all_parity[ii]))
        # incidentecis.f90:245-249 reads `lband`/`Kband`/`defpar` at the level's own BAND index
        # (`vibband`), which for the vibrational model is what ecisinput.f90:122 then writes onto
        # ECIS's one card per band. The ground state has `vibband == 0` and no phonon.
        b = int(d.vibband[i])
        lam.append(0.0 if b == 0 else float(d.lband[b]))
        iph.append(int(d.iphonon[i]))
        vb.append(b)
        # incidentecis.f90:246-250 writes the band cards from `lband`/`Kband`/`defpar` indexed by
        # the DEFORMATION ROW i, not by the band -- `Jband(i1) = lband(Zix, Nix, i)` -- and then
        # writes cards 1..Nband of those. `deformpar.f90:198-201` fills those three arrays by
        # BAND. The two agree whenever the first Nband rows are the first Nband bands, which is
        # what every `.def` block the port meets looks like; this reproduces TALYS either way.
        jb.append(int(d.lband[i]))
        km.append(int(d.Kband[i]))
        bb.append(float(d.defpar[i]))
        if b != 0:
            beta.append(float(d.defpar[b]))
    nband = max(vb) if vb else 0
    return {
        "e_mev": torch.tensor(e, dtype=DTYPE),
        "spin": torch.tensor(sp, dtype=DTYPE),
        "parity": torch.tensor(pa, dtype=torch.int64),
        "rotbeta": torch.tensor(list(d.rotpar[1 : d.nrot + 1]), dtype=DTYPE),
        "deformation_length": d.deftype == "D",
        "colltype": d.colltype,
        "kband": float(sp[0]) if sp else 0.0,
        "vib_lambda": torch.tensor(lam, dtype=DTYPE),
        "vib_beta": torch.tensor(beta, dtype=DTYPE),
        "iphonon": torch.tensor(iph, dtype=torch.int64),
        # the ECIS deck's band structure, which the two-phonon (`lo(2)`) branch needs and the
        # harmonic one does not: `vibband` is `iband(i)` per coupled level (0 for the ground
        # state), and `jband`/`kmag`/`band_beta` are the `Nband` phonon cards, 1-based with
        # entry 0 unused.
        "vibband": torch.tensor(vb, dtype=torch.int64),
        "nband": int(nband),
        "jband": torch.tensor([0] + jb[:nband], dtype=torch.int64),
        "kmag": torch.tensor([0] + km[:nband], dtype=torch.int64),
        "band_beta": torch.tensor([0.0] + bb[:nband], dtype=DTYPE),
        "options": o,
    }


__all__ = ["COLUMNS", "InjectedOMP", "coupled_band", "incident_omp", "talys_out"]
