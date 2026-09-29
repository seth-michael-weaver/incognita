"""NATIVEX2 lever `ld`: the level-density set-up of a residual nucleus and its rhogrid in C
(`native/nx2_ld.c`), for the calls where nothing carries a gradient and the model is the
analytical constant-temperature + Fermi gas without collective enhancement (ldmodel 1, every
nucleus with A <= 215 under TALYS's defaults).

Ported from TALYS-2.x (https://github.com/arjankoning1/talys), MIT License,
Copyright (c) A.J. Koning. See physics/hf/NOTICE-TALYS.md.

Task: NATIVEX2 (the speed work; no physics of its own). Acceptance test: `tests/hf/test_nx2_ld.py`
(each kernel against the torch/numpy path it replaces) and the G-NATIVEX2 closeness gate.

Where the time went (spherical 12, in-process): `Cascade.spec` 1.0 CPU-s of 6.5, of which the
matching root (zbrak's 101 energies and rtbis's bisection, one torch `match_vec` per energy)
0.26, `rhogrid_of` 0.25 (a torch `density` of every bin bottom, centre and top), the Fermi-gas
tables 0.09 and `Ncum(NL)` 0.04; `densitypar` 0.19 (its ~40 `Params.at` lookups and zero-dim torch
operations, and a whole `deformation` for two moments of inertia), which `densitypar_floats`
redoes on Python floats (no C).

The kernels do the same +, -, *, / in the same order as the torch expressions (contraction off);
only libm's exp/log/pow may differ from torch's in a last bit, so they are held to closeness, not
bits. Each function returns None when the kernel is not built, `HF_NX2_LD=0`, the model is not
the one the kernel carries, or a level-density tensor asks for a gradient; the caller then runs
its own path.

TALYS routines the kernels compute:
    densitymatch.f90:118-160, matching.f90:1 (matching), match.f90:1 (match),
    zbrak.f90:1 (zbrak), rtbis.f90:1 (rtbis), densitycum.f90:130-150, exgrid.f90:241-285,
    density.f90:1 (density), densitytot.f90:1 (densitytot), gilcam.f90:1 (gilcam),
    fermi.f90:1 (fermi), ignatyuk.f90:1 (ignatyuk), spincut.f90:1 (spincut), spindis.f90:1 (spindis)
"""

from __future__ import annotations

import os

import numpy as np
import torch
from torch import Tensor

from physics.hf.native import nx2

__all__ = ["densitypar_floats", "densitypar_key", "fermi_tables", "match_roots", "ncum", "retarget",
           "rhogrid", "shared_record"]

_LEVER = "ld"
_P, _I, _D = nx2.P, nx2.I64, nx2.DBL


def _k(name: str, args: list, res=nx2.INT):
    return nx2.kernel(name, args, res, lever=_LEVER)


def _par(ld) -> np.ndarray | None:
    """The scalars of `ld` the kernels read (nx2_ld.c's `P_*` order), memoised per object; None
    when the kernel does not carry this nucleus's model or any of its tensors asks for a
    gradient."""
    from physics.hf.density.parameters import _ign_floats, _ld_memo, _sc_floats

    memo = _ld_memo(ld)
    got = memo.get("nx2_ld", False)
    if got is not False:
        return got
    # CENGLD: "nograd" marks a record built on floats (every tensor fresh, none on a graph)
    ok = (not ld.flagcol and ld.ldmodel not in (2, 3) and not ld.has_table(0)
          and (memo.get("nograd", False)
               or not any(isinstance(v, Tensor) and v.requires_grad for v in vars(ld).values())))
    par = None
    if ok:
        delta, alimit, gam, dW, colldamp, aldlow, uf, cf = _ign_floats(ld, 0)
        scutconst, Em, Ed, sdisc, s2m, colld, _delta = _sc_floats(ld, 0, 0, 4.0)
        par = np.array([
            delta, alimit, gam, dW, 1.0 if colldamp else 0.0, aldlow, uf, cf,
            scutconst, Em, Ed, sdisc, s2m, 0.0 if colld is None else 1.0,
            0.0 if colld is None else colld, 1.0 if ld.spincutmodel == 1 else 0.0,
            float(ld.T_mev[0]), float(ld.E0_mev[0]), float(ld.Exmatch_mev[0]),
            float(ld.ctable[0]), float(ld.ptable_mev[0]), float(ld.pair_mev),
        ], dtype=np.float64)
    memo["nx2_ld"] = par
    return par


def fermi_tables(ld, ibar: int, nEx: int, dEx: float) -> tuple[Tensor, Tensor, int] | None:
    """`matching._fermi_tables`'s logrho(0..nEx+1), temprho(0..nEx+1) and Nstart, or None.

    TALYS: densitymatch.f90:118-160
    Test: tests/hf/test_nx2_ld.py
    """
    if ibar != 0:
        return None
    fn = _k("nx2_ld_fermi_tables", [_P, _I, _D, _P, _P], _I)
    par = _par(ld) if fn is not None else None
    if par is None:
        return None
    logrho = np.zeros(nEx + 2)
    temprho = np.zeros(nEx + 2)
    nstart = int(fn(nx2.ptr(par), nEx, dEx, nx2.ptr(logrho), nx2.ptr(temprho)))
    return torch.from_numpy(logrho), torch.from_numpy(temprho), nstart


def match_roots(logrho: Tensor, temprho: Tensor, x1: float, x2: float, nseg: int, E0save: float,
                NLo: int, NP: int, EL: float, EP: float, sentinel: float,
                xacc: float) -> list[float] | None:
    """`matching`'s zbrak (at most 2 brackets on [x1, x2] in `nseg` steps) and rtbis to `xacc` on
    match.f90's condition: the roots in bracket order, or None (the caller runs the torch path).
    Only the tables enter, so any barrier and any model with tables works.

    TALYS: matching.f90:1 (matching), zbrak.f90:1 (zbrak), rtbis.f90:1 (rtbis), match.f90:1 (match)
    Test: tests/hf/test_nx2_ld.py
    """
    if logrho.requires_grad or temprho.requires_grad:
        return None
    fn = _k("nx2_ld_match_root",
            [_P, _P, _I, _D, _D, _I, _D, _D, _D, _D, _D, _D, _D, _P], _I)
    if fn is None:
        return None
    lr = np.ascontiguousarray(logrho.numpy(), dtype=np.float64)
    tr = np.ascontiguousarray(temprho.numpy(), dtype=np.float64)
    roots = np.zeros(2)
    nb = int(fn(nx2.ptr(lr), nx2.ptr(tr), lr.shape[0], float(x1), float(x2), int(nseg),
                float(E0save), float(NLo), float(NP), float(EL), float(EP), float(sentinel),
                float(xacc), nx2.ptr(roots)))
    return [float(roots[k]) for k in range(nb)]


def ncum(ld, NL: int, index: int) -> float | None:
    """`densitycum(ld)["Ncum"][index]` (`dens_reference._ncum_no_grad`), or None.

    TALYS: densitycum.f90:130-150
    Test: tests/hf/test_nx2_ld.py
    """
    fn = _k("nx2_ld_ncum", [_P, _P, _I, _I], _D)
    par = _par(ld) if fn is not None else None
    if par is None:
        return None
    edis = np.ascontiguousarray(ld.edis_mev.numpy(), dtype=np.float64)
    if index >= edis.shape[0]:
        return None
    return float(fn(nx2.ptr(par), nx2.ptr(edis), int(NL), int(index)))


_RHOGRID_FN = None


def rhogrid(ld, A: int, ex_mev, dex_mev, maxj, nlast: int, numj: int) -> np.ndarray | None:
    """`dens_reference.rhogrid_of`'s numpy result, (n, numj+1, 2), or None.

    TALYS: exgrid.f90:241-285 (exgrid), density.f90:1 (density)
    Test: tests/hf/test_nx2_ld.py
    """
    global _RHOGRID_FN
    if os.environ.get("HF_NX2_LD", "1") == "0":
        return None
    fn = _RHOGRID_FN
    if fn is None:
        fn = _RHOGRID_FN = _k("nx2_ld_rhogrid", [_P, _P, _P, _P, _P, _I, _I, _D, _P])
    if fn is not None and nlast + 1 >= len(ex_mev):
        # CENGLD: no continuum bin, whatever the model: `rhogrid_of`'s empty selection
        return np.zeros((len(ex_mev), numj + 1, 2))
    par = _par(ld) if fn is not None else None
    if par is None:
        return None
    got = _ceng_rhogrid(par, A, ex_mev, dex_mev, maxj, nlast, numj)  # CENGLD: rows to maxJ only
    if got is not None:
        return got
    n = len(ex_mev)
    out = np.zeros((n, numj + 1, 2))
    if nlast + 1 >= n:  # no continuum bin: `rhogrid_of`'s empty selection
        return out
    ex = np.ascontiguousarray(ex_mev, dtype=np.float64)
    dex = np.ascontiguousarray(dex_mev, dtype=np.float64)
    mj = np.ascontiguousarray(maxj, dtype=np.int64)
    if dex.shape[0] < n or mj.shape[0] < n:
        return None
    sel = np.zeros(n, np.uint8)
    sel[nlast + 1:] = mj[nlast + 1: n] >= 0
    if fn(nx2.ptr(par), nx2.ptr(ex), nx2.ptr(dex), nx2.ptr(mj), nx2.ptr(sel), n, numj,
          0.5 * (A % 2), nx2.ptr(out)) != 0:
        return None
    return out


class _Graph(Exception):
    """A parameter `densitypar_floats` would read carries a gradient."""


#: numpy views of `Params` tensors by id, with a weak reference that must resolve to the same
#: tensor (a recycled id never hits); dropped with the tensor
_NPV: dict[int, tuple] = {}


def _view(t: Tensor) -> np.ndarray:
    import weakref

    ent = _NPV.get(id(t))
    if ent is not None and ent[0]() is t:
        return ent[1]
    v = t.numpy()
    key = id(t)
    _NPV[key] = (weakref.ref(t, lambda _r, k=key: _NPV.pop(k, None)), v)
    return v


def densitypar_floats(Z: int, A: int, options, params, masses, levels, deformation=None,
                      barriers=None):
    """`parameters.densitypar` on Python floats, for the default case: no fission barriers, not
    the generalised superfluid model, and no parameter carrying a gradient (else None, and the
    caller runs its tensor code). Every `+ - * /` is the tensor code's, in its order, on the same
    doubles; `exp`/`log` are libm's, so a value may move in its last bit.

    Where the time went: ~40 `Params.at` lookups (three `select`s each) and ~40 zero-dim torch
    operations per nucleus, 250 us of Python per call, 553 calls on the spherical 12.

    TALYS: densitypar.f90:1 (densitypar)
    Test: tests/hf/test_nx2_ld.py
    """
    import math
    import os

    from physics.hf.core.constants import talys_constants
    from physics.hf.core.tensors import DTYPE
    from physics.hf.density import parameters as P

    if os.environ.get("HF_NX2_LD", "1") == "0":
        return None
    Zix, Nix = options.Zinit - Z, options.Ninit - (A - Z)
    ldmod = options.ldmodel_of(Zix, Nix)
    bar = barriers or P.BarrierLevels()
    nbar = bar.nfisbar if options.flagfission else 0
    if nbar != 0 or ldmod == 3:
        return None
    vals = params.values

    def pf(k: str, *extra: int) -> float:
        plan = P._AT_PLAN.get(k)
        if plan is None:
            from physics.hf.input.defaults import PARAM_SPECS

            spec = PARAM_SPECS[k]
            plan = P._AT_PLAN[k] = (spec.keyword, spec.dims, spec.offsets)
        kw, dims, offs = plan
        t = vals[kw]
        if t.requires_grad:
            raise _Graph
        nd = len(dims)
        if nd >= 2 and dims[0][0] <= Zix <= dims[0][1] and dims[1][0] <= Nix <= dims[1][1]:
            if nd == 2 and not extra:
                return float(_view(t)[Zix + offs[0], Nix + offs[1]])
            if nd == 3 and len(extra) == 1 and dims[2][0] <= extra[0] <= dims[2][1]:
                return float(_view(t)[Zix + offs[0], Nix + offs[1], extra[0] + offs[2]])
        return float(params.at(k, Zix, Nix, *extra))  # raises IndexError as the tensor code does

    def pg(k: str) -> float:
        t = params[k]
        if t.requires_grad:
            raise _Graph
        return float(t)

    try:
        ld = _densitypar_floats(Z, A, options, params, masses, levels, deformation, bar,
                                ldmod, Zix, Nix, pf, pg, math, talys_constants(), DTYPE, P)
    except _Graph:
        return None
    P._ld_memo(ld)["nograd"] = True
    return ld


_KEY_PLAN = None


def _key_plan():
    """What `_densitypar_floats` reads, taken from its own source: every `pf`/`pg` keyword (with
    its extra indices) and every `options.` field. Parsed once, so a read added to the body is a
    read of the key without a second list to keep in step (tests/hf/test_cengld2.py)."""
    global _KEY_PLAN
    if _KEY_PLAN is None:
        import inspect
        import re

        src = inspect.getsource(_densitypar_floats)
        pfs = tuple(dict.fromkeys(
            (k, tuple(int(x) for x in re.findall(r"\d+", extra)))
            for k, extra in re.findall(r'\bpf\("(\w+)"((?:,\s*\d+)*)\)', src)))
        pgs = tuple(dict.fromkeys(re.findall(r'\bpg\("(\w+)"\)', src)))
        opts = tuple(sorted(set(re.findall(r"\boptions\.(\w+)", src))
                            | {"ldmodel_of", "flagfission"}))
        _KEY_PLAN = (pfs, pgs, opts)
    return _KEY_PLAN


def densitypar_key(Z: int, A: int, options, params, masses, levels, deformation=None,
                   barriers=None) -> tuple | None:
    """CENGLD2: every value `densitypar_floats` reads for (Z, A), as a hashable float record, or
    None where it would not run (a barrier set, a gradient, a read it would raise on).

    `densitypar_floats` is a function of (Z, A) and these values alone -- the target enters only as
    the (Zix, Nix) at which `Params`, `Masses` and the options' per-nucleus methods are read, and
    those reads are the key's -- so two targets whose records have equal keys get the same record
    up to its `Zix`/`Nix` fields. The chart builds each cascade nucleus's level density once per
    target (12,677 builds for ~5,000 distinct records); `parameters.densitypar` and
    `dens_reference._ld_build` share them across targets by this key. A fit's `aadjust` (PARAMWIRE)
    is a `pf` read, so a new parameter point is a new key.

    TALYS: densitypar.f90:1 (densitypar)
    Test: tests/hf/test_cengld2.py
    """
    if barriers is not None or os.environ.get("HF_NX2_LD", "1") == "0":
        return None
    last = _LAST_KEY[0]
    if (last is not None and last[0] == Z and last[1] == A and last[2] is options
            and last[3] is params and last[4] is masses and last[5] is levels
            and last[6] is deformation):
        return last[7]  # `_ld_build` then its `densitypar`: the same objects, one gather
    key = _gather_key(Z, A, options, params, masses, levels, deformation)
    _LAST_KEY[0] = (Z, A, options, params, masses, levels, deformation, key)
    return key


_LAST_KEY: list = [None]
#: per `Params` object: its `pf` reads as (tensor, numpy view, bounds, flat offsets) and its `pg`
#: floats, planned once (a fit's new `Params` is a new plan)
_READS: dict = {}


def _reads(params):
    from physics.hf.density import parameters as P
    from physics.hf.input.defaults import PARAM_SPECS

    got = _READS.get(id(params))
    if got is not None and got[0] is params:
        return got[1]
    pfs, pgs, _ = _key_plan()
    vals = params.values
    ents = []
    for k, extra in pfs:
        plan = P._AT_PLAN.get(k)
        if plan is None:
            spec = PARAM_SPECS[k]
            plan = P._AT_PLAN[k] = (spec.keyword, spec.dims, spec.offsets)
        kw, dims, offs = plan
        t = vals[kw]
        nd = len(dims)
        if nd < 2 or not (nd == 2 and not extra) and not (
                nd == 3 and len(extra) == 1 and dims[2][0] <= extra[0] <= dims[2][1]):
            nd = 0  # not a direct cell read: `params.at` below, as the builder does
        ents.append((t, nd, dims[0] if nd else None, dims[1] if nd else None,
                     offs[0] if nd else 0, offs[1] if nd else 0,
                     (extra[0] + offs[2]) if nd == 3 else 0, k, extra))
    pg = tuple(params[k] for k in pgs)
    out = (tuple(ents), pg)
    if len(_READS) >= 64:
        _READS.clear()
    _READS[id(params)] = (params, out)
    return out


def _gather_key(Z, A, options, params, masses, levels, deformation):
    from physics.hf.density import parameters as P

    pfs, pgs, opts = _key_plan()
    Zix, Nix = options.Zinit - Z, options.Ninit - (A - Z)
    if options.ldmodel_of(Zix, Nix) == 3:  # the generalised superfluid model: densitypar's tensors
        return None
    out: list = [Z, A]
    fl: list = []  # every float read, keyed by its bits (so -0.0 and 0.0 are two keys)
    try:
        for name in opts:
            if name in ("Zinit", "Ninit"):  # the target: only through (Zix, Nix) below
                continue
            v = getattr(options, name)
            out.append(v(Zix, Nix) if callable(v) else v)
        ents, pg = _reads(params)
        for t, nd, dz, dn, oz, on, e3, k, extra in ents:
            if t.requires_grad:
                return None
            if nd and dz[0] <= Zix <= dz[1] and dn[0] <= Nix <= dn[1]:
                v = _view(t)
                fl.append(v[Zix + oz, Nix + on] if nd == 2 else v[Zix + oz, Nix + on, e3])
            else:
                fl.append(float(params.at(k, Zix, Nix, *extra)))
        for t in pg:
            if t.requires_grad:
                return None
            fl.append(float(t))
        b2 = masses.beta2
        for arr, idx in ((masses.mass_amu, (Zix, Nix)), (masses.s_mev, (Zix, Nix, 1)),
                         (b2, (Zix, Nix))):
            fl.append(_view(arr)[idx] if isinstance(arr, Tensor) else float(arr[idx]))
        if deformation is None:  # rigid_moments(..., 0): A and the ground-state beta2 (or 0)
            out.append(Zix < b2.shape[0] and Nix < b2.shape[1])
        else:
            fl += [float(deformation.irigid0), float(deformation.irigid[0])]
        n2 = min(int(levels.nlevmax2), P.NUMLEV2)
        e, j = levels.all_e_mev, levels.all_spin
        if e.requires_grad or j.requires_grad:
            return None
        out += [int(levels.nlev), int(levels.nlevmax2), str(e.dtype), str(j.dtype),
                _view(e)[: n2 + 1].tobytes(), _view(j)[: n2 + 1].tobytes(),
                np.array(fl, dtype=np.float64).tobytes()]
    except Exception:  # a read the build would raise on (or a non-tensor record): no key
        return None
    return tuple(out)


#: CENGLD2: records by `densitypar_key` (and the matched `_ld_build` results by that key and the
#: matching inputs), across targets. Pure: a key holds every value its record was made from. Kept
#: over `chartrun.drop_target_caches` (a plain dict); bounded.
_SHARED: dict = {}
_SHARED_MAX = 40000


def _xt_on() -> bool:
    return os.environ.get("HF_CENGLD2_XT", "1") != "0"


def shared_record(key, Zix: int, Nix: int, make):
    """The record stored under `key`, retargeted to (Zix, Nix), else `make()` stored under it.
    `HF_CENGLD2_XT_CHECK=1` builds every hit afresh as well and raises unless the two are equal
    field for field (bitwise)."""
    got = _SHARED.get(key)
    if got is not None:
        rec = _retarget_value(got, Zix, Nix)
        if os.environ.get("HF_CENGLD2_XT_CHECK") == "1":
            _check_same(rec, make(), key)
        return rec
    rec = make()
    if rec is not None:
        if len(_SHARED) >= _SHARED_MAX:
            _SHARED.pop(next(iter(_SHARED)))
        _SHARED[key] = rec
    return rec


def _retarget_value(v, Zix, Nix):
    if isinstance(v, tuple):  # `_ld_build`'s (ld, Ntop, Nlast, Ncum)
        return (retarget(v[0], Zix, Nix), *v[1:])
    return retarget(v, Zix, Nix)


def _check_same(a, b, key) -> None:
    def same(x, y) -> bool:
        if isinstance(x, Tensor) or isinstance(y, Tensor):
            return (isinstance(x, Tensor) and isinstance(y, Tensor) and x.shape == y.shape
                    and x.dtype == y.dtype and x.numpy().tobytes() == y.numpy().tobytes())
        if isinstance(x, (tuple, list)):
            return type(x) is type(y) and len(x) == len(y) and all(map(same, x, y))
        if isinstance(x, float) and isinstance(y, float):
            return np.float64(x).tobytes() == np.float64(y).tobytes()
        if hasattr(x, "__dataclass_fields__") and type(x) is type(y):
            return all(same(getattr(x, f), getattr(y, f)) for f in x.__dataclass_fields__)
        return x == y

    if not same(a, b):
        CHECK["bad"] += 1
        raise AssertionError(f"CENGLD2 shared record differs from a fresh build: Z,A={key[:2]}")
    CHECK["ok"] += 1


CHECK = {"ok": 0, "bad": 0}


def retarget(ld, Zix: int, Nix: int):
    """CENGLD2: `ld` for another target: the same tensors and floats (nothing writes into a
    record), its own `Zix`/`Nix`, and a copy of the memoised floats (`parameters._ld_memo`: none of
    them reads Zix or Nix)."""
    from physics.hf.density.parameters import _ld_memo

    if ld.Zix == Zix and ld.Nix == Nix:
        return ld
    new = object.__new__(type(ld))
    d = new.__dict__
    d.update(ld.__dict__)
    d["Zix"], d["Nix"] = Zix, Nix
    _ld_memo(new).update(_ld_memo(ld))
    return new


def _densitypar_floats(Z, A, options, params, masses, levels, deformation, bar, ldmod, Zix, Nix,
                       pf, pg, math, c, DTYPE, P):
    """The body of `densitypar_floats`, line for line densitypar's with nbar = 0."""
    amu = c["amu"]
    twothird, onethird = c["twothird"], c["onethird"]
    N = A - Z
    flagcol = options.flagcol_of(Zix, Nix)
    SENTINEL = P.SENTINEL

    # --- parameter files (densitypar.f90:203-339)
    s2a0 = pf("s2adjust", 0)
    found, nlow0, ntop0, ald0, pshift0 = P.ld_parameter_file(
        Z, A, ldmod, flagcol and ldmod <= 3, s2a0)
    alev = pf("a")
    Pshift = pf("pshift", 0)
    ctable = pf("ctable", 0)
    ptable = pf("ptable", 0)
    Nlow = options.nlow_default
    Ntop = options.ntop_default
    ldparexist = False
    if found:
        ldparexist = True
        if Nlow == -1:
            Nlow = nlow0
        if Ntop == -1:
            Ntop = min(ntop0, 50)
        if not options.flagasys and not options.flagldglobal:
            if ldmod <= 3:
                if alev == 0.0:
                    alev = pf("aadjust") * ald0
                if Pshift == SENTINEL:
                    Pshift = pshift0 + pf("pshiftadjust", 0)
            else:
                if ctable == SENTINEL:
                    ctable = ald0
                if ptable == SENTINEL:
                    ptable = pshift0
            ctable = ctable + pf("ctableadjust", 0)
            ptable = ptable + pf("ptableadjust", 0)

    # --- discrete levels padded as TALYS's edis/jdis (0 beyond nlevmax2)
    edis = torch.zeros(P.NUMLEV2 + 1, dtype=DTYPE)
    jdis = torch.zeros(P.NUMLEV2 + 1, dtype=DTYPE)
    n2 = min(int(levels.nlevmax2), P.NUMLEV2)
    edis[: n2 + 1] = levels.all_e_mev[: n2 + 1].to(DTYPE)
    jdis[: n2 + 1] = levels.all_spin[: n2 + 1].to(DTYPE)
    if edis.requires_grad or jdis.requires_grad:
        raise _Graph

    # --- Nlast/Ntop/Nlow (densitypar.f90:344-355)
    Nlast = int(levels.nlev)
    if Ntop == -1:
        Ntop = Nlast
    if Nlow == -1:
        Nlow = 2
    if Ntop <= 2:
        Nlow = 0

    # --- discrete spin cutoff (densitypar.f90:363-389)
    scutoffsys = (P._f32(0.83) * (A ** P._f32(0.26))) ** 2
    s = scutoffsys
    ed = 0.0
    if ldparexist:
        e_np, j_np = edis.numpy(), jdis.numpy()
        ed = 0.5 * (float(e_np[Nlow]) + float(e_np[Ntop]))
        rj = j_np[Nlow : Ntop + 1]
        # spins are multiples of 1/2, so both sums are exact in any order
        sigsum = float((rj * (rj + 1) * (2 * rj + 1)).sum())
        denom = float((2 * rj + 1).sum())
        sd = sigsum / (3.0 * denom) if denom != 0.0 else 0.0
        if scutoffsys / 3.0 < sd < scutoffsys * 3.0:
            s = sd

    # --- a, deltaW, alimit, gammald (densitypar.f90:398-431)
    alimit = pf("alimit")
    inpalev = alev != 0.0
    deltaW = pf("deltaw", 0)
    inpdeltaW = True
    if deltaW == 0.0:
        inpdeltaW = False
        from physics.hf.structure.masses import mliquid1, mliquid2

        mldm = mliquid1(Z, A) if options.shellmodel == 1 else mliquid2(Z, A)
        deltaW = (float(masses.mass_amu[Zix, Nix]) - mldm) * amu
    inpalimit = True
    if alimit == 0.0:
        inpalimit = False
        alimit = pf("alphald") * A + pf("betald") * (A**twothird)
    gammald = pf("gammald")
    inpgammald = True
    if gammald == -1.0:
        inpgammald = False
        gammald = pf("gammashell1") / (A**onethird) + pg("gammashell2")
    if inpalev and inpdeltaW and inpalimit and inpgammald:
        inpalev = False
        alev = 0.0

    # --- pairing (densitypar.f90:437-453)
    oddZ, oddN = Z % 2, N % 2
    delta0 = pg("pairconstant") / math.sqrt(float(A))
    pair = pf("pair")
    if pair == SENTINEL:
        if ldmod == 2:
            pair = (1 - oddZ - oddN) * delta0
        else:
            pair = (2 - oddZ - oddN) * delta0
    if Pshift == SENTINEL:
        Pshift = pf("pshiftconstant") + pf("pshiftadjust", 0)

    # --- delta (densitypar.f90:485-520), not the generalised superfluid model
    S = float(masses.s_mev[Zix, Nix, 1])
    delta = pair + Pshift

    # --- a(Sn) or the parameter it leaves free (densitypar.f90:524-556)
    Spair = max(S - delta, 1.0)
    if not inpalev:
        fU = 1.0 - math.exp(-gammald * Spair)
        factor = 1.0 + fU * deltaW / Spair
        alev = max(pf("aadjust") * alimit * factor, 1.0)
    else:
        fU = 1.0 - math.exp(-gammald * Spair)
        if not inpalimit:
            factor = 1.0 + fU * deltaW / Spair
            alimit = alev / factor
        elif not inpdeltaW:
            factor = alev / alimit - 1.0
            deltaW = Spair * factor / fU
        else:
            argum = 1.0 - Spair / deltaW * (alev / alimit - 1.0)
            if 0.0 < argum < 1.0:
                gammald = -1.0 / Spair * math.log(argum)
            else:
                factor = alev / alimit - 1.0
                deltaW = Spair * factor / fU

    # --- exciton single-particle densities (densitypar.f90:560-567)
    kph = pg("kph")
    g = pf("g")
    if g == 0.0:
        g = A / kph
    g = pf("gadjust") * g
    gp = pf("gp")
    if gp == 0.0:
        gp = Z / kph
    gn = pf("gn")
    if gn == 0.0:
        gn = N / kph
    gn = pf("gadjust") * pf("gnadjust") * gn
    gp = pf("gadjust") * pf("gpadjust") * gp

    # --- moments of inertia (deformpar.f90, T2) and the ground-state beta2
    if deformation is None:
        from physics.hf.structure.deformation import rigid_moments

        irigid0, irigid = rigid_moments(Z, A, options, masses, params, 0)
    else:
        irigid0, irigid = deformation.irigid0, deformation.irigid

    # CENGLD: the zero-dim and (1,) tensors as views of two float64 buffers, one tensor each
    # instead of one per field (nothing writes into a record's tensors in place)
    s0 = torch.from_numpy(np.array([
        alev, alimit, gammald, pair, delta0, pg("rspincut"), irigid0, S, 0.0, g, gn, gp,
    ], dtype=np.float64)).unbind()
    v1 = torch.from_numpy(np.array([
        deltaW, Pshift, delta, s, ed, ctable, ptable, pf("s2adjust", 0), pf("krotconstant", 0),
        pf("ufermi", 0), pf("cfermi", 0), irigid[0], float(masses.beta2[Zix, Nix]),
        0.0, 0.0, 0.0, 0.0, 0.0, pf("t", 0), pf("e0", 0), pf("exmatch", 0), pf("tadjust", 0),
        pf("e0adjust", 0), pf("exmatchadjust", 0),
    ], dtype=np.float64)).split(1)

    return P.LDNucleus(
        Z=Z, A=A, Zix=Zix, Nix=Nix, ldmodel=ldmod, flagcol=flagcol, nfisbar=0,
        spincutmodel=options.spincutmodel, kvibmodel=options.kvibmodel,
        flagcolldamp=options.flagcolldamp, fismodel=options.fismodel,
        flagparity=options.flagparity, ldparexist=ldparexist,
        alev=s0[0], alimit=s0[1], gammald=s0[2], deltaW_mev=v1[0],
        pair_mev=s0[3], delta0_mev=s0[4], Pshift_mev=v1[1], delta_mev=v1[2],
        scutoffdisc=v1[3], Ediscrete_mev=v1[4], Nlow=(Nlow,), Ntop=(Ntop,), Nlast=(Nlast,),
        ctable=v1[5], ptable_mev=v1[6], s2adjust=v1[7],
        Rspincut=s0[5], Krotconstant=v1[8],
        Ufermi_mev=v1[9], cfermi_mev=v1[10],
        Irigid0=s0[6], Irigid=v1[11], beta2=v1[12],
        axtype=(1,), S_mev=s0[7], Tcrit_mev=s0[8], aldcrit=v1[13], Econd_mev=v1[14],
        Ucrit_mev=v1[15], Scrit=v1[16], Dcrit=v1[17],
        T_mev=v1[18], E0_mev=v1[19], Exmatch_mev=v1[20],
        Tadjust=v1[21], E0adjust=v1[22],
        Exmatchadjust=v1[23],
        g=s0[9], gn=s0[10], gp=s0[11], edis_mev=edis, jdis=jdis, nlev=int(levels.nlev),
        nlevmax2=int(levels.nlevmax2), barriers=bar, ldexist=(False,), tables=(None,),
    )


from physics.hf.density.ld_ceng import rhogrid as _ceng_rhogrid  # noqa: E402  (CENGLD)
