"""KWCOV B4b (COMPOOBS): `components y`, the direct / pre-equilibrium / compound split per residual, OUTPUT ONLY.

Ported from TALYS-2.x (https://github.com/arjankoning1/talys), MIT License,
Copyright (c) A.J. Koning. See physics/hf/NOTICE-TALYS.md.

What it gives (Results.extras keys, (C,) mb on the run's energies):

    xs<nnnnnn>.tot:direct|:preeq|:compound    Fdir / Fpreeq / Fcomp of the channel's residual x xschannel
                                              (channelsout.f90 columns 5-7 of xs*.tot with components y)
    rp<ZZZ><AAA>.tot:direct|:preeq|:compound  xspopdir / xspoppreeq / xspopcomp (residualout.f90 columns 3-5)

The binary.tot-like split of binaryout.f90 is printed to talys.out only (no file) and is not given.

Physics (multiple.f90:649-668, at the end of each nucleus' decay): xspopdir = xsdirdisctot of the binary ejectile that
leads to the nucleus (binary.f90:214); xspoppreeq = the multiple pre-equilibrium flux it received (multipreeq.f90:291)
+ preeqpopex summed over its bins up to the separation energy of the ejectile it emits most (Smax, the first bin
above it ends the sum), preeqpopex being the binary pre-equilibrium population (target level zeroed, binary.f90:506)
plus the multiple pre-equilibrium population it received minus what each of its bins emitted that way
(multipreeq.f90:275, :312); then xspoppreeq = min(xspoppreeq, xspopnuc - xspopdir) and, as TALYS writes it,
xspopcomp = max(xspopnuc - (xspoppreeq - xspopdir), 0) (the direct part is ADDED back: kept); F* = xspop* / xspopnuc.
The multiple pre-equilibrium matrices come from the SPECOUT recorders (`mpe` per mother bin -> daughter bin), which
`components y` turns on for the run.

Switch: the deck's `components y` (Options.flagcompo). Default: nothing is computed and every array is unchanged.

TALYS routines ported here (file:line of the subroutine statement):
    multiple.f90:1 (multiple)        lines 649-668: xspoppreeq, xspopcomp, Fdir, Fpreeq, Fcomp
    channelsout.f90:1 (channelsout)  lines 299-345: the xs*.tot columns
    residualout.f90:1 (residualout)  lines 199-233: the rp*.tot columns
Task: T10 (physics/hf/CONTRACT.md section 7; KWCOV batch B4b, output only). Acceptance test: KWCOV-B4B
(tests/hf/test_kwcov_b4b.py, docs/hf/COVERAGE_PLAN.md).
"""

from __future__ import annotations

import numpy as np

PARZ = (0, 0, 1, 1, 1, 2, 2)
PARN = (0, 1, 0, 1, 2, 1, 2)
COLS = ("direct", "preeq", "compound")

_ON: dict | None = None
ENERGIES: list[dict] = []


def wanted() -> bool:
    """`components y` on the active deck lines, before a Cascade exists (SPECOUT asks this to record).

    TALYS: (none -- a port switch)
    Test: tests/hf/test_kwcov_b4b.py
    """
    if _ON is not None:
        return True
    try:
        from physics.hf.input import fitlib

        ov = {str(k).lower(): v for k, v in fitlib.option_overrides().items()}
    except Exception:  # noqa: BLE001
        return False
    return str(ov.get("components", "n")).strip().lower()[:1] in ("y", "1", "t")


def begin_run(cas) -> bool:
    """A new engine run: on with `components y`.

    TALYS: (none -- a port switch)
    Test: tests/hf/test_kwcov_b4b.py
    """
    global _ON
    ENERGIES.clear()
    _ON = dict(Zc=int(cas.Zt) + PARZ[int(cas.k0)], Ac=int(cas.At) + PARZ[int(cas.k0)] + PARN[int(cas.k0)]) \
        if bool(getattr(cas.options, "flagcompo", False)) else None
    return _ON is not None


def active() -> bool:
    """True while a run records the components.

    TALYS: (none -- a port switch)
    Test: tests/hf/test_kwcov_b4b.py
    """
    return _ON is not None


def split(cinp, st, b2, walks: dict) -> dict:
    """{(Z, A): (xspopnuc, xspopdir, xspoppreeq, xspopcomp)} of every nucleus with a population, one energy.

    `walks` = the SPECOUT records of the energy ({(zc, nc): rec with types[t]['mpe'] (mother bins, daughter bins)}).

    TALYS: multiple.f90:1 (multiple) lines 649-668
    Test: tests/hf/test_kwcov_b4b.py
    """
    nuc = cinp.nuclei
    recv: dict = {}
    emit: dict = {}
    sumin: dict = {}
    for key, rec in (walks or {}).items():
        if rec.get("lines_only"):
            continue
        for t, e in (rec.get("types") or {}).items():
            t = int(t)
            if t == 0 or "mpe" not in e:
                continue
            m = np.asarray(e["mpe"], float)
            if not m.any():
                continue
            dk = (key[0] + PARZ[t], key[1] + PARN[t])
            r = recv.setdefault(dk, np.zeros(0))
            v = m.sum(axis=0)
            if len(r) < len(v):
                r = np.pad(r, (0, len(v) - len(r)))
            r[: len(v)] += v
            recv[dk] = r
            em = emit.setdefault(key, np.zeros(0))
            w = m.sum(axis=1)
            if len(em) < len(w):
                em = np.pad(em, (0, len(w) - len(em)))
            em[: len(w)] += w
            emit[key] = em
            sumin[dk] = sumin.get(dk, 0.0) + float(m.sum())
    k0 = int(cinp.k0)
    lt = int(getattr(cinp, "ltarget", 0))
    binres = {(PARZ[t], PARN[t]): t for t in range(7)}
    out = {}
    for key, n in nuc.items():
        pop = float(n.xspopnuc_mb)
        sp = getattr(st, "spec", {}).get(key)
        if sp is None:
            continue
        ex = np.asarray(sp.ex_mev, float)
        nr = int(sp.maxex) + 1
        ppx = np.zeros(nr)
        xspopdir = 0.0
        t = binres.get(key)
        if t is not None and t in getattr(b2, "grids", {t: None}):
            v = (getattr(b2, "preeqpopex_mb", {}) or {}).get(t)
            if v is not None:
                a = np.asarray(v.detach().cpu().numpy() if hasattr(v, "detach") else v, float)
                k = min(nr, len(a))
                ppx[:k] += a[:k]
                if t == k0 and 0 <= lt < nr:
                    ppx[lt] = 0.0  # binary.f90:506
            xspopdir = float((getattr(b2, "xsdirdisctot_mb", {}) or {}).get(t, 0.0))
        if key in recv:
            k = min(nr, len(recv[key]))
            ppx[:k] += recv[key][:k]
        if key in emit:
            k = min(nr, len(emit[key]))
            ppx[:k] -= emit[key][:k]
        xsmax, smax = 0.0, 0.0
        for t2 in range(1, 7):
            f = float(n.xsfeed_mb.get(t2, 0.0))
            if f > xsmax:
                xsmax, smax = f, float(n.sep_mev.get(t2, 0.0))
        pe = sumin.get(key, 0.0)
        for nex in range(nr):
            if ex[nex] > smax:
                break
            pe += ppx[nex]
        pe = min(pe, pop - xspopdir)
        comp = max(pop - (pe - xspopdir), 0.0)
        if pop == 0.0 and xspopdir == 0.0:
            continue
        out[(int(n.Z), int(n.A))] = (pop, xspopdir, pe, comp)
    return out


def record(cinp, st, b2) -> None:
    """After specout.end_energy: the components of this energy (output only; errors recorded, not raised).

    TALYS: multiple.f90:1 (multiple)
    Test: tests/hf/test_kwcov_b4b.py
    """
    if _ON is None:
        return
    from physics.hf import specout

    cur = specout.ENERGIES[-1] if specout.ENERGIES else None
    rec = dict(e_inc_mev=float(cinp.e_inc_mev))
    try:
        walks = cur.get("walks", {}) if (cur is not None and abs(float(cur["e_inc_mev"]) - rec["e_inc_mev"]) < 1e-9) \
            else {}
        rec["split"] = split(cinp, st, b2, walks)
    except Exception as exc:  # noqa: BLE001 -- output only
        rec["error"] = f"{type(exc).__name__}: {exc}"
    ENERGIES.append(rec)


def add_to_results(res):
    """Results.extras with the components columns (xs*.tot, rp*.tot) of the run; unchanged when off.

    TALYS: channelsout.f90:1 (channelsout), residualout.f90:1 (residualout)
    Test: tests/hf/test_kwcov_b4b.py
    """
    global _ON
    if _ON is None:
        return res
    from dataclasses import replace

    import torch

    from physics.hf.emission.chanobs import residual_of

    try:
        E = [float(x) for x in res.e_inc_mev.detach().cpu().numpy()]
        byE = {round(r["e_inc_mev"], 6): r for r in ENERGIES}
        C = len(E)
        out: dict[str, np.ndarray] = {}
        for i, e in enumerate(E):
            r = byE.get(round(e, 6))
            if r is None or "split" not in r:
                continue
            sp = r["split"]
            for (Z, A), (pop, d, p, c) in sp.items():
                for name, v in zip(COLS, (d, p, c)):  # noqa: B905
                    out.setdefault(f"rp{Z:03d}{A:03d}.tot:{name}", np.zeros(C))[i] = v
            for key, t in res.channels_mb.items():
                code = int(key[2:])
                xs = float(t[i])
                Z, A = residual_of(code, _ON["Zc"], _ON["Ac"])
                pop, d, p, c = sp.get((Z, A), (0.0, 0.0, 0.0, 0.0))
                f = (d / pop, p / pop, c / pop) if pop > 0.0 else (0.0, 0.0, 0.0)
                for name, v in zip(COLS, f):  # noqa: B905
                    out.setdefault(f"{key}.tot:{name}", np.zeros(C))[i] = v * xs
        ex = dict(res.extras or {})
        ex.update({k: torch.as_tensor(v, dtype=torch.float64) for k, v in out.items()})
        res = replace(res, extras=ex)
    finally:
        _ON = None
        ENERGIES.clear()
        from physics.hf import specout

        if not specout.env_enabled():  # specobs (if on) has read the recorders already
            specout.clear_run()
    return res


__all__ = ["COLS", "ENERGIES", "active", "add_to_results", "begin_run", "record", "split", "wanted"]
