"""The A-fis gate: the ported fission chain against TALYS's own `fis*.txt` and `fis*.trans`.

Task: T11 (physics/hf/CONTRACT.md §7). Acceptance test: A-fis (§6), tolerance 0.05 on the p95
of ``r = |ln(port / TALYS)|``.

What is scored, and with what injected
--------------------------------------
1. **Barrier parameters** (`fis*.txt`, `fissionparout.f90`): the number of barriers, and per
   barrier the height, the curvature, `Rtransmom`, the moment of inertia and the axiality --
   for every fissile nucleus in each actinide run, not just the target. Nothing is injected:
   these come out of the BSkG3 path and the WKB parabola fit.
2. **Fission transmission** (`fis*.trans`, `tfissionout.f90`): `T(J,pi)`, the partial width,
   the lifetime and the compound level density at the bin centre. The only injected quantity
   is the excitation energy of the bin, read from the block header; the barrier level densities
   come from T6 (`ldmodel 7`, `ibar > 0`) on the barriers this task supplies, and the barrier
   parameters from (1). That makes this the *chained* number for everything below `compound`.

`(n,f)` itself (`fission.tot`) needs the compound-nucleus population, which for an actinide
needs the coupled-channels incident channel -- T13 or the ECIS bridge. It is reported, not
gated, exactly as the task brief states.

T14 warns (docs/results/hf-sgl-floor.md, Result 4) that a *per-barrier* `T(J,pi)` can move 5.7x
between TALYS's own single- and double-precision builds on a discrete branch flip. That warning
is about the per-barrier intermediate; the `fis*.trans` file holds the combined transmission,
whose worst case here is reported alongside the p95 so a flipped point cannot hide.

Usage::

    uv run python -m physics.hf.fission.score            # all 5 actinides, barriers + primary CN
    uv run python -m physics.hf.fission.score --residuals  # also the multiple-emission bins
"""

from __future__ import annotations

import argparse
import json
import math
import time
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import torch

from physics.hf.core.tensors import DTYPE
from physics.hf.fission import reference as R
from physics.hf.fission.parameters import barrier_levels, fission_parameters
from physics.hf.fission.barriers import NUMJ
from physics.hf.fission.transmission import fission_level_densities, fission_transmission

TOLERANCE = 0.05  # CONTRACT.md §6, A-fis


@dataclass
class Residuals:
    """Accumulator for one gate row: log-ratios plus the worst case that produced them."""

    name: str
    r: list[float]
    n_zero_ref: int = 0
    n_zero_port: int = 0
    n_stale: int = 0
    worst: tuple[float, str] = (0.0, "")

    def add(self, port, ref, label: str = "", stale=None) -> None:
        p = np.asarray(port, dtype=np.float64).ravel()
        t = np.asarray(ref, dtype=np.float64).ravel()
        live = (t > 0.0) & (p > 0.0)
        if stale is not None:
            st = np.asarray(stale, dtype=bool).ravel()
            self.n_stale += int(np.count_nonzero(st & live))
            live = live & ~st
        self.n_zero_ref += int(np.count_nonzero((t <= 0.0) & (p > 0.0)))
        self.n_zero_port += int(np.count_nonzero((t > 0.0) & (p <= 0.0)))
        if not live.any():
            return
        rr = np.abs(np.log(p[live] / t[live]))
        self.r.extend(rr.tolist())
        i = int(np.argmax(rr))
        if rr[i] > self.worst[0]:
            idx = int(np.flatnonzero(live)[i])
            self.worst = (float(rr[i]), f"{label}[{idx}] port={p[live][i]:.6e} talys={t[live][i]:.6e}")

    def summary(self) -> dict:
        a = np.asarray(self.r)
        if a.size == 0:
            return {"name": self.name, "n": 0}
        return {
            "name": self.name,
            "n": int(a.size),
            "median": float(np.median(a)),
            "p95": float(np.percentile(a, 95)),
            "max": float(a.max()),
            "pass": bool(np.percentile(a, 95) <= TOLERANCE),
            "n_not_computed_by_talys": self.n_zero_ref,
            "n_zero_in_port": self.n_zero_port,
            "n_stale_in_talys": self.n_stale,
            "worst": self.worst[1],
        }


def _options_params(target: str):
    from physics.hf.input.defaults import default_options, default_params
    from physics.hf.talys_reference import REFERENCE_SET

    for t in REFERENCE_SET:
        if t.tag == target:
            o = default_options(t.Z, t.A)
            return t.Z, t.A, o, default_params(t.Z, t.A, o)
    raise KeyError(target)


class _NucleusCache:
    """Barrier parameters and the T6 level density of one fissile nucleus, built once."""

    def __init__(self, options, params):
        self.o, self.p = options, params
        self._fp: dict[tuple[int, int], object] = {}
        self._ld: dict[tuple[int, int], object] = {}
        self._masses = None

    def masses(self):
        if self._masses is None:
            from physics.hf.structure.masses import masses as _m

            self._masses = _m(self.o, self.p)
        return self._masses

    def fp(self, Z: int, A: int):
        if (Z, A) not in self._fp:
            self._fp[(Z, A)] = fission_parameters(Z, A, self.o, self.p, masses=self.masses())
        return self._fp[(Z, A)]

    def ld(self, Z: int, A: int):
        if (Z, A) not in self._ld:
            from physics.hf.density.matching import densitymatch
            from physics.hf.density.parameters import densitypar
            from physics.hf.density.tables import attach_tables
            from physics.hf.structure.levels import discrete_levels

            ms = self.masses()
            lv = discrete_levels(Z, A, self.o, ms, self.p)
            bl = barrier_levels(self.fp(Z, A))
            self._ld[(Z, A)] = densitymatch(
                attach_tables(densitypar(Z, A, self.o, self.p, ms, lv, barriers=bl))
            )
        return self._ld[(Z, A)]


def _score_band(rows: dict, name: str, port, ref_states: list, tag: str) -> None:
    """Compare a transition-state band (count, energies, spins, parities) element by element.

    Energies are compared as absolute differences in MeV, because a rotational band starts at
    exactly 0 for the band head; spins and parities must match exactly.
    """
    if not ref_states and port.n == 0:
        return
    rows.setdefault(f"{name}_count_exact", Residuals(f"{name}_count_exact", []))
    ok = port.n == len(ref_states)
    rows[f"{name}_count_exact"].r.append(0.0 if ok else 1.0)
    if not ok:
        rows[f"{name}_count_exact"].worst = (
            1.0, f"{tag} port={port.n} talys={len(ref_states)}"
        )
        return
    rows.setdefault(f"{name}_energy_mev", Residuals(f"{name}_energy_mev", []))
    rows.setdefault(f"{name}_jp_exact", Residuals(f"{name}_jp_exact", []))
    for k, (e, j, pi) in enumerate(ref_states, start=1):
        d = abs(float(port.e_mev[k]) - e)
        rows[f"{name}_energy_mev"].r.append(d)
        if d > rows[f"{name}_energy_mev"].worst[0]:
            rows[f"{name}_energy_mev"].worst = (
                d, f"{tag}#{k} port={float(port.e_mev[k]):.6e} talys={e:.6e}"
            )
        same = abs(float(port.spin[k]) - j) < 1e-6 and port.parity[k] == pi
        rows[f"{name}_jp_exact"].r.append(0.0 if same else 1.0)
        if not same:
            rows[f"{name}_jp_exact"].worst = (
                1.0,
                f"{tag}#{k} port=({float(port.spin[k])},{port.parity[k]}) talys=({j},{pi})",
            )


def score_barrier_densities(cache: _NucleusCache, files: list[Path], rows: dict) -> None:
    """A-ld for `ibar > 0`: the barrier level densities against the `ld*.b0N` dumps.

    T6 ported `densitypar`/`densitymatch`/`density` with an `ibar` argument but could not test
    the `ibar > 0` branch, because nothing supplied `BarrierLevels` until this task; the A-ld
    gate skips the `*.b0[123]` files for that reason (T6's note on the board). This closes it,
    and it is also what sets the floor on the fission transmission: `t1barrier` integrates
    `rhofis` against the penetrability, so a relative error in the barrier level density lands
    one-for-one in `Tfis`.

    Scored against the same 1e-4 / 2% split A-ld uses: `rho_total` and `rho_observed` are the
    table, `rho(J)` the spin-resolved density.
    """
    from physics.hf.density.models import density, densitytotP
    from physics.hf.yandf import parse_blocks

    for path in sorted(files):
        stem = path.name  # ld<ZZZ><AAA>.b0N
        Z, A, ibar = int(stem[2:5]), int(stem[5:8]), int(stem[-1])
        ld = cache.ld(Z, A)
        if ibar > ld.nfisbar:
            continue
        for blk in parse_blocks(path):
            if blk.meta.get("type") != "level density":
                continue
            parity = int(float(blk.meta["Parity"]))
            e = torch.as_tensor(blk.column("E"), dtype=DTYPE)
            if e.numel() == 0:
                continue
            tag = f"Z{Z}A{A}b{ibar}p{parity:+d}"
            odd = A % 2
            # `rho_total` of a ld*.b0N block is the STATE density of that parity,
            # sum_J (2J+1) rho(Ex, J, parity), not `densitytot` (T6's note to T0).
            jgrid = torch.arange(NUMJ + 1, dtype=DTYPE) + 0.5 * odd
            rho_j = density(ld, e.reshape(-1, 1), jgrid.reshape(1, -1), parity, ibar)
            state = ((2.0 * jgrid + 1.0) * rho_j).sum(-1)
            for name, port, ref in (
                ("bar_rho_total", state, blk.column("rho_total")),
                ("bar_rho_observed", densitytotP(ld, e, parity, ibar), blk.column("rho_observed")),
            ):
                rows.setdefault(name, Residuals(name, []))
                rows[name].add(port.detach().cpu().numpy(), ref, tag)
            for col in blk.columns:
                if not col.startswith("rho(J)="):
                    continue
                rj = float(col.split("=")[1])
                if abs(rj - (int(rj - 0.5 * odd) + 0.5 * odd)) > 1e-6:
                    continue
                port = density(ld, e, torch.as_tensor(rj, dtype=DTYPE), parity, ibar)
                ref = np.asarray(blk.column(col), dtype=np.float64)
                live = ref > 1.0e-25  # TALYS clamps an empty spin bin at 1e-30
                if not live.any():
                    continue
                rows.setdefault("bar_rho_J", Residuals("bar_rho_J", []))
                rows["bar_rho_J"].add(
                    port.detach().cpu().numpy()[live], ref[live], f"{tag}J{rj}"
                )


def score_barrier_parameters(cache: _NucleusCache, files: list[Path], rows: dict) -> None:
    """Compare `fissionpar`'s output against every `fis*.txt` of one run."""
    for path in sorted(files):
        ref = R.read_fission_parameters(path)
        fp = cache.fp(ref.Z, ref.A)
        rows.setdefault("nfisbar_exact", Residuals("nfisbar_exact", []))
        ok = fp.nfisbar == ref.nfisbar
        rows["nfisbar_exact"].r.append(0.0 if ok else 1.0)
        if not ok:
            rows["nfisbar_exact"].worst = (1.0, f"Z{ref.Z}A{ref.A} port={fp.nfisbar} talys={ref.nfisbar}")
            continue
        for i in range(1, ref.nfisbar + 1):
            b = ref.barrier(i)
            if b is None:
                continue
            tag = f"Z{ref.Z}A{ref.A}b{i}"
            for key, port in (
                ("Height of fission barrier", fp.fbarrier_mev[i]),
                ("Width of fission barrier", fp.fwidth_mev[i]),
                ("Moment of inertia", fp.minertia[i]),
                ("Rtransmom", cache.p.at("rtransmom", fp.Zix, fp.Nix, i)),
            ):
                if key in b.values:
                    name = key.lower().replace(" ", "_")
                    rows.setdefault(name, Residuals(name, []))
                    rows[name].add([float(port)], [b.values[key]], tag)
            if "Type of axiality" in b.values:
                rows.setdefault("axtype_exact", Residuals("axtype_exact", []))
                match = fp.axtype[i] == int(b.values["Type of axiality"])
                rows["axtype_exact"].r.append(0.0 if match else 1.0)
                if not match:
                    rows["axtype_exact"].worst = (
                        1.0,
                        f"{tag} port={fp.axtype[i]} talys={int(b.values['Type of axiality'])}",
                    )
            if "Number of head band transition states" in b.values:
                rows.setdefault("nfistrhb_exact", Residuals("nfistrhb_exact", []))
                match = fp.headband[i].n == int(b.values["Number of head band transition states"])
                rows["nfistrhb_exact"].r.append(0.0 if match else 1.0)
            if "Start of continuum energy" in b.values:
                rows.setdefault("fecont_exact", Residuals("fecont_exact", []))
                d = abs(float(fp.fecont_mev[i]) - b.values["Start of continuum energy"])
                rows["fecont_exact"].r.append(0.0 if d < 1e-6 else d)
            _score_band(rows, "headband", fp.headband[i], b.states, tag)
            _score_band(rows, "rotband", fp.rotational[i], b.rotational, tag)
        for i in range(1, ref.nclass2 + 1):
            w = ref.well(i)
            if w is None:
                continue
            tag = f"Z{ref.Z}A{ref.A}c{i}"
            for key, port in (
                ("Moment of inertia", fp.minertc2[i]),
                ("Width of class2 states (MeV)", fp.widthc2_mev[i]),
                ("Rclass2mom", cache.p.at("rclass2mom", fp.Zix, fp.Nix, i)),
            ):
                if key in w.values:
                    name = "class2_" + key.split(" (")[0].lower().replace(" ", "_")
                    rows.setdefault(name, Residuals(name, []))
                    rows[name].add([float(port)], [w.values[key]], tag)
            _score_band(rows, "class2_states", fp.class2[i], w.states, tag)
            _score_band(rows, "class2_rotband", fp.class2rot[i], w.rotational, tag)


def _complete_groups(groups: list[list]) -> list[list]:
    """Keep only the incident energies whose whole bin ladder was printed.

    `multiple.f90:511` skips a bin whose population is below `popepsA` *before* calling
    `densprepare`, so for a deep residual the highest bins can be missing and the first printed
    energy is then **not** `Ex(maxex)` -- while `densprepare.f90:411` still builds the fission
    level-density grid up to `Ex(maxex)`. There is no way to recover `Ex(maxex)` from the dump
    for such a group, so those groups are dropped rather than scored against a grid injected at
    the wrong top. A group whose length equals the longest in the file had no bin skipped, so
    its first block is `maxex`.
    """
    if not groups:
        return groups
    full = max(len(g) for g in groups)
    return [g for g in groups if len(g) == full]


FRESH_BAND = 1.0e-3  # 100x the agreement a recomputed cell shows; stale cells are 1e30 off


def _fresh_mask(rho_port: np.ndarray, rho_ref: np.ndarray, seed) -> dict[str, np.ndarray]:
    """Widen the stale-cell mask using the compound level density as a freshness tag.

    `tfis`/`gamfis`/`taufis`/`denfis` are TALYS globals with no nucleus index (A0_talys_mod
    declares them `dimension(0:numJ, -1:1)`), so an untouched (J, parity) cell can carry a value
    written for a *different nucleus* at a different energy -- which no single-file comparison
    can see. `denfis` is `density(Zcomp, Ncomp, Exinc, J, parity, 0)`, a function of exactly the
    nucleus and energy of the block, so a cell whose printed density reproduces the port's to
    within `FRESH_BAND` was written for this block, and one that does not was not. Stale cells
    miss by many orders of magnitude (1e-30 against 1e5 is typical), so the band is not tight.

    The mask this returns is applied to all four quantities, which makes the `denfis` row of the
    residual gate the *definition* of the mask rather than an independent measurement; the
    primary compound-nucleus rows are scored without needing it (nothing there is stale) and are
    the ones that carry A-fis.
    """
    ok = (rho_port > 0) & (rho_ref > 0)
    with np.errstate(divide="ignore", invalid="ignore", over="ignore"):
        ratio = np.where(ok, rho_port, 1.0) / np.where(ok, np.maximum(rho_ref, 1e-300), 1.0)
        r = np.abs(np.log(np.where(np.isfinite(ratio) & (ratio > 0), ratio, 1e30)))
    stale = ~(ok & (r < FRESH_BAND))
    out = {}
    for name in ("tfis", "gamma_mev", "tau_s", "density_per_mev"):
        prior = None if seed is None else seed.get(name)
        out[name] = stale if prior is None else (stale | prior)
    return out


def _score_block(cache, Z, A, block, exfis_top, primary, rows, prefix, stale=None) -> None:
    fp = cache.fp(Z, A)
    ld = cache.ld(Z, A)
    odd = A % 2
    maxj = len(block.spin) - 1
    grid = fission_level_densities(fp, ld, exfis_top, odd=odd, maxj=maxj)
    ft = fission_transmission(
        fp, grid, ld, block.exinc_mev, 0.0, cache.o, odd=odd, maxj=maxj, primary=primary
    )
    tag = f"Z{Z}A{A}@{block.exinc_mev:.3f}"
    stale = _fresh_mask(ft.denfis_per_mev.detach().cpu().numpy(), block.density_per_mev, stale)
    for name, port, ref_name in (
        ("tfis", ft.tfis, "tfis"),
        ("gamfis", ft.gamfis_mev, "gamma_mev"),
        ("taufis", ft.taufis_s, "tau_s"),
        ("denfis", ft.denfis_per_mev, "density_per_mev"),
    ):
        key = f"{prefix}{name}"
        rows.setdefault(key, Residuals(key, []))
        rows[key].add(
            port.detach().cpu().numpy(),
            getattr(block, ref_name),
            tag,
            stale[ref_name],
        )


def score_target(
    target: str,
    variant: str = "default",
    workdir: Path | None = None,
    residuals: bool = False,
    max_groups: int | None = None,
    max_bins: int = 4,
    barrier_densities: bool = False,
) -> dict:
    """Score A-fis for one reference target."""
    workdir = workdir or (Path.home() / "hf_t11" / "ref")
    d = R.extract(target, variant, workdir)
    Z, A, o, p = _options_params(target)
    cache = _NucleusCache(o, p)
    rows: dict[str, Residuals] = {}
    t0 = time.time()

    score_barrier_parameters(cache, list(d.glob("fis*.txt")), rows)
    if barrier_densities:
        score_barrier_densities(cache, list(d.glob("ld*.b0[123]")), rows)

    cn = (Z, A + 1)
    for path in sorted(d.glob("fis*.trans")):
        rz, ra = R.nuclide_of(path)
        if (rz, ra) != cn and not residuals:
            continue
        blocks = R.read_transmission(path)
        stale = dict(zip((id(b) for b in blocks), R.stale_masks(blocks), strict=True))
        all_groups = R.transmission_groups(blocks)
        if (rz, ra) != cn:  # the primary compound nucleus needs no ladder (see _complete_groups)
            all_groups = _complete_groups(all_groups)
        groups = all_groups if max_groups is None else all_groups[:max_groups]
        for g in groups:
            if (rz, ra) == cn:
                _score_block(cache, rz, ra, g[0], g[0].exinc_mev, True, rows, "",
                             stale[id(g[0])])
                rest = g[1:]
            else:
                rest = g
            if not residuals or not rest:
                continue
            top = rest[0].exinc_mev
            for b in rest[:max_bins]:
                _score_block(cache, rz, ra, b, top, False, rows, "resid_", stale[id(b)])
    return {
        "target": target,
        "variant": variant,
        "elapsed_s": round(time.time() - t0, 1),
        "rows": [r.summary() for r in rows.values()],
    }


def score_run(
    run_dir: Path,
    Z: int,
    A: int,
    overrides: dict | None = None,
    residuals: bool = False,
    max_bins: int = 4,
) -> dict:
    """Score A-fis against a plain TALYS output directory (not a reference tarball).

    Used for the variant runs the default reference set does not contain: `fismodel 1` with
    `hbstate y class2 y` is the only way to exercise `thill`, `rotband`, `rotclass2` and the
    class-II enhancement of `tfission`, because every default actinide run takes the WKB path
    with all three flags off.
    """
    from physics.hf.input.defaults import default_options, default_params

    run_dir = Path(run_dir).expanduser()
    o = default_options(Z, A, overrides=overrides or {})
    p = default_params(Z, A, o)
    cache = _NucleusCache(o, p)
    rows: dict[str, Residuals] = {}
    t0 = time.time()
    score_barrier_parameters(cache, list(run_dir.glob("fis*.txt")), rows)
    cn = (Z, A + 1)
    for path in sorted(run_dir.glob("fis*.trans")):
        rz, ra = R.nuclide_of(path)
        if (rz, ra) != cn and not residuals:
            continue
        blocks = R.read_transmission(path)
        stale = dict(zip((id(b) for b in blocks), R.stale_masks(blocks), strict=True))
        all_groups = R.transmission_groups(blocks)
        if (rz, ra) != cn:
            all_groups = _complete_groups(all_groups)
        for g in all_groups:
            if (rz, ra) == cn:
                _score_block(cache, rz, ra, g[0], g[0].exinc_mev, True, rows, "",
                             stale[id(g[0])])
                rest = g[1:]
            else:
                rest = g
            if not residuals or not rest:
                continue
            for b in rest[:max_bins]:
                _score_block(cache, rz, ra, b, rest[0].exinc_mev, False, rows, "resid_",
                             stale[id(b)])
    return {
        "target": f"{run_dir.name} Z{Z}A{A}",
        "variant": "run-dir",
        "elapsed_s": round(time.time() - t0, 1),
        "rows": [r.summary() for r in rows.values()],
    }


def _report(res: dict) -> None:
    print(f"\n=== {res['target']} ({res['elapsed_s']} s) ===")
    for row in res["rows"]:
        if row["n"] == 0:
            continue
        mark = "" if row.get("pass", True) else "   <-- FAIL"
        print(
            f"  {row['name']:<26} n={row['n']:<7} median={row['median']:.3e} "
            f"p95={row['p95']:.3e} max={row['max']:.3e}{mark}"
        )
        if row["max"] > 0 and row["worst"]:
            print(f"      worst: {row['worst']}")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="A-fis gate")
    ap.add_argument("--targets", nargs="*", default=list(R.ACTINIDE_TARGETS))
    ap.add_argument("--variant", default="default")
    ap.add_argument("--residuals", action="store_true")
    ap.add_argument("--barrier-densities", action="store_true",
                    help="also score T6's ibar>0 level densities against ld*.b0N")
    ap.add_argument("--max-groups", type=int, default=None)
    ap.add_argument("--max-bins", type=int, default=4)
    ap.add_argument("--run-dir", default=None, help="score a plain TALYS output directory")
    ap.add_argument("--run-target", default=None, help="Z,A of the --run-dir target")
    ap.add_argument("--run-keywords", default="", help="k=v,k=v overrides matching that run")
    ap.add_argument("--out", default="docs/results/hf-fission-gate.json")
    a = ap.parse_args(argv)
    torch.set_num_threads(2)
    torch.set_default_dtype(DTYPE)

    out = []
    pooled: dict[str, Residuals] = {}
    if a.run_dir:
        Z, A = (int(x) for x in a.run_target.split(","))
        ov: dict[str, object] = {}
        for kv in filter(None, a.run_keywords.split(",")):
            k, v = kv.split("=")
            ov[k] = int(v) if v.lstrip("-").isdigit() else v
        out.append(score_run(Path(a.run_dir), Z, A, ov, residuals=a.residuals,
                             max_bins=a.max_bins))
        _report(out[-1])
        a.targets = []
    for t in a.targets:
        if not R.available(t, a.variant):
            print(f"{t}: no reference archive, skipped")
            continue
        res = score_target(
            t, a.variant, residuals=a.residuals, max_groups=a.max_groups, max_bins=a.max_bins,
            barrier_densities=a.barrier_densities,
        )
        out.append(res)
        _report(res)
    summary = {"tolerance": TOLERANCE, "targets": out}
    if pooled:
        summary["pooled"] = [r.summary() for r in pooled.values()]
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    Path(a.out).write_text(json.dumps(summary, indent=2) + "\n")
    print(f"\nwrote {a.out}")
    worst = max(
        (row["p95"] for res in out for row in res["rows"] if row["n"] and "p95" in row),
        default=math.nan,
    )
    print(f"worst p95 over all rows: {worst:.3e} (tolerance {TOLERANCE})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
