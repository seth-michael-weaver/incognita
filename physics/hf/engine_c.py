"""CENGDECAY (ROUTE100 WP5): the chart's dump-free run with the warm decay core in C.

Ported from TALYS-2.x (https://github.com/arjankoning1/talys), MIT License,
Copyright (c) A.J. Koning. See physics/hf/NOTICE-TALYS.md.

Task: CENGDECAY (the speed work; no physics of its own). Acceptance test:
`tests/hf/test_engine_c.py` (every array against `engine.run(injection=ChainedFull(...))`) and the
WP5 gate (docs/results/hf-cengdecay.md).

TALYS routines computed here, in `engine.ChainedFull`'s arrangement:
    talysreaction.f90:1 (talysreaction) -- the per-energy loop
    multiple.f90:1 (multiple), cascade.f90:1 (cascade), compound.f90:1 (compound),
    densprepare.f90:1 (densprepare)     -- `native/engine_decay.c`'s `ce_cascade`

`run` is `engine.run(injection=ChainedFull(Z, A, declared_energies, cascade, params))` for a
nucleon-induced chart run, statement for statement, except that per incident energy

* the whole multiple emission -- the nucleus set, the widths of every cascade nucleus, the walk,
  the discrete gamma cascades and the records `channels` reads -- is one C call over arrays packed
  once per cascade nucleus (`_Cascade`); Python keeps the excitation grids and rhogrid
  (`Cascade.spec`, the level densities) and the fission ladder, which the C side calls back into;
* `binary`'s result is the one the energy loop already formed, not a second call.

An energy the C call does not take (multiple pre-equilibrium at `emulpre`, a tensor on the way,
an uncovered fission ladder, a nucleus without a photon-strength pack, no build) runs the Python
path of `ChainedFull.cases` for that energy, so every energy gives the nx path's numbers.

Selection: no build, `HF_NATIVE=0`, `HF_NATIVEX=0` or `HF_ENGINE_C=0` -> `engine.run` itself.
"""

from __future__ import annotations

import ctypes
import os
import sys
from functools import lru_cache
from pathlib import Path

import numpy as np
import torch

from physics.hf.core.tensors import DTYPE

_DIR = Path(__file__).resolve().parent / "native" / "lib"
_P = ctypes.c_void_p
_I64 = np.int64
NJ = 41
SI, SD, SP, SO = 16, 18, 14, 8
PARZ = (0, 0, 1, 1, 1, 2, 2)
PARN = (0, 1, 0, 1, 2, 1, 2)
_FIS_CB = ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_int64, ctypes.c_int64,
                           ctypes.POINTER(ctypes.c_int64), ctypes.POINTER(ctypes.c_uint64),
                           ctypes.POINTER(ctypes.c_int64))


def enabled() -> bool:
    env = os.environ
    return not any(env.get(k, "1") == "0" for k in ("HF_NATIVE", "HF_NATIVEX", "HF_ENGINE_C"))


@lru_cache(maxsize=1)
def lib():
    """The loaded engine with its kernel pointers set, or None."""
    if not enabled():
        return None
    from physics.hf.native import nativex, nx2

    path = _DIR / ("libengdecay.dylib" if sys.platform == "darwin" else "libengdecay.so")
    nxl, n2 = nativex.lib(), nx2.lib()
    if not path.is_file() or nxl is None or n2 is None:
        return None
    try:
        so = ctypes.CDLL(str(path))
        if so.ce_version() != 2:
            return None
    except (OSError, AttributeError):
        return None
    so.ce_set_kernels.argtypes = [_P, _P, _P]
    so.ce_set_kernels.restype = None
    so.ce_cascade.argtypes = [_P, _P, _P]
    so.ce_cascade.restype = ctypes.c_int64

    def addr(fn) -> int:
        fp = getattr(fn, "_fp", fn)  # a timing wrapper (harness/route100_costmap) keeps the function
        return ctypes.cast(fp, ctypes.c_void_p).value

    so.ce_set_kernels(addr(nxl.nx_widths), addr(nxl.nx_walk), addr(n2.nx2_psf_photon))
    so.ce_densprepare.argtypes = [_P, _P, _P]
    so.ce_densprepare.restype = ctypes.c_int64
    so.ce_set_front_kernels.argtypes = [_P]
    so.ce_set_front_kernels.restype = None
    from physics.hf.compound.psf_nx2 import _args

    pts = nx2.kernel("nx2_psf_points", _args() + [nx2.I64, nx2.P, nx2.P, nx2.DBL, nx2.P],
                     lever="psf")
    so.front_ok = (pts is not None and nxl is not None
                   and os.environ.get("HF_ENGINE_C_FRONT", "1") != "0")
    if so.front_ok:
        so.ce_set_front_kernels(addr(pts))
    so.ce_set_blas.argtypes = [_P, _P, _P]
    so.ce_set_blas.restype = None
    so.ce_channels.argtypes = [_P, _P, _P]
    so.ce_channels.restype = ctypes.c_int64
    blas = _blas() if os.environ.get("HF_ENGINE_C_CHANNELS", "1") != "0" else None
    so.channels_ok = blas is not None
    if blas is not None:
        so.ce_set_blas(*blas)
    return so


_BLAS: list = []


def _blas():
    """`_blas_check`'s pointers, checked once per process (`lib`'s cache is dropped with the
    target caches, this is not)."""
    if not _BLAS:
        _BLAS.append(_blas_check())
    return _BLAS[0]


def _blas_check():
    """CENGBOOK: the (dgemv, ddot, dtrtrs) function pointers `ce_channels` calls, or None.

    They are scipy's cython_blas / cython_lapack entries, and they are taken only if they give
    numpy's `x @ R`, `U @ x` and scipy's `dtrtrs` to the bit on this box (checked once here over the
    shapes the channels meet, numpy's 1-row / 1-column special cases included): the channels' sums
    are then the Python body's.
    """
    try:
        from scipy.linalg import cython_blas, cython_lapack
        from scipy.linalg.lapack import dtrtrs

        api = ctypes.pythonapi
        api.PyCapsule_GetName.restype = ctypes.c_char_p
        api.PyCapsule_GetName.argtypes = [ctypes.py_object]
        api.PyCapsule_GetPointer.restype = ctypes.c_void_p
        api.PyCapsule_GetPointer.argtypes = [ctypes.py_object, ctypes.c_char_p]

        def cap(mod, name):
            c = mod.__pyx_capi__[name]
            return api.PyCapsule_GetPointer(c, api.PyCapsule_GetName(c))

        ptrs = (cap(cython_blas, "dgemv"), cap(cython_blas, "ddot"), cap(cython_lapack, "dtrtrs"))
        P, d, i, ch = ctypes.POINTER, ctypes.c_double, ctypes.c_int, ctypes.c_char
        gemv = ctypes.CFUNCTYPE(None, P(ch), P(i), P(i), P(d), P(d), P(i), P(d), P(i), P(d),
                                P(d), P(i))(ptrs[0])
        ddot = ctypes.CFUNCTYPE(d, P(i), P(d), P(i), P(d), P(i))(ptrs[1])
        trtrs = ctypes.CFUNCTYPE(None, P(ch), P(ch), P(ch), P(i), P(i), P(d), P(i), P(d), P(i),
                                 P(i))(ptrs[2])

        def pd(a):
            return a.ctypes.data_as(P(d))

        def ref(v, t=i):
            return ctypes.byref(t(v))

        rng = np.random.default_rng(20260915)
        shapes = [(1, 1), (1, 7), (7, 1), (2, 2), (3, 40)] + [
            (int(a), int(b)) for a, b in rng.integers(2, 96, size=(40, 2))]
        for k, n in shapes:
            x = rng.random(k) * 10.0 ** rng.uniform(-6, 3, k)
            R = np.ascontiguousarray(rng.random((k, n)) * (rng.random((k, n)) < 0.6))
            y = np.zeros(n)
            if n == 1:
                y[0] = ddot(ref(k), pd(x), ref(1), pd(R), ref(1))
            elif k == 1:
                y = 0.0 + x[0] * R[0]
            else:
                gemv(ctypes.byref(ch(b"N")), ref(n), ref(k), ref(1.0, d), pd(R), ref(n), pd(x),
                     ref(1), ref(0.0, d), pd(y), ref(1))
            if not np.array_equal(y, x @ R):
                return None
            U = np.triu(rng.random((n, n)) * (rng.random((n, n)) < 0.5), 1)
            v = rng.random(n)
            y = np.zeros(n)
            if n == 1:
                y[0] = ddot(ref(1), pd(U), ref(1), pd(v), ref(1))
            else:
                gemv(ctypes.byref(ch(b"T")), ref(n), ref(n), ref(1.0, d), pd(U), ref(n), pd(v),
                     ref(1), ref(0.0, d), pd(y), ref(1))
            if not np.array_equal(y, U @ v):
                return None
            A = np.eye(n) - U
            want, _ = dtrtrs(A.T, v, lower=1, trans=1, unitdiag=1)
            got = v.copy()
            info = i(0)
            trtrs(ctypes.byref(ch(b"L")), ctypes.byref(ch(b"T")), ctypes.byref(ch(b"U")), ref(n),
                  ref(1), pd(A), ref(n), pd(got), ref(n), ctypes.byref(info))
            if not np.array_equal(got, want):
                return None
        return ptrs
    except Exception:  # noqa: BLE001 -- no scipy capsule / no BLAS: the Python channels
        return None


def _ptr(a) -> int:
    return 0 if a is None else a.__array_interface__["data"][0]


class _Unsupported(Exception):
    """The energy is not the C call's; run the Python path."""


class _Run:
    """What `ce_cascade` reads that is fixed for the run (one `Cascade`)."""

    def __init__(self, cas):
        from physics.hf.compound.decay_fast import _tl_stack
        from physics.hf.compound.dens_reference import _eendmax
        from physics.hf.compound.psf_nx2 import _args
        from physics.hf.native import nx2

        self.cas = cas
        self.ok = True
        tls = [cas.trans[t] for t in range(1, 7)]
        Ltl = tls[0][1].shape[1]
        if any(isinstance(x[1], torch.Tensor) or x[1].shape[1] != Ltl for x in tls):
            self.ok = False
            return
        if (nx2.kernel("nx2_psf_photon", _args() + [nx2.I64, nx2.P, nx2.I64, nx2.P, nx2.P,
                                                    nx2.DBL, nx2.DBL, nx2.P], lever="psf")
                is None or os.environ.get("HF_NATIVEX_WIDTHS", "1") == "0"):
            self.ok = False
            return
        TL, LM, head0 = _tl_stack(cas, tls)
        rg = cas.rg
        self.keep = []
        self.TL = np.ascontiguousarray(TL, dtype=np.float64)
        self.LM = np.ascontiguousarray(LM, dtype=_I64)
        self.head0 = np.ascontiguousarray(head0, dtype=_I64)
        egrid = np.ascontiguousarray(np.asarray(rg.egrid, dtype=np.float64))
        self.egrid = egrid
        self.egrid32 = np.ascontiguousarray(egrid[: rg.maxen + 1], dtype=np.float32)
        self.egrid32f = np.ascontiguousarray(egrid, dtype=np.float32)
        eendmax = _eendmax(cas.Zt, cas.At, cas.enincmax)
        self.ebegin = np.array([int(rg.ebegin[t]) for t in range(1, 7)], dtype=_I64)
        self.eend = np.array([min(int(eendmax[t]), rg.maxen) for t in range(1, 7)], dtype=_I64)
        self.Ltl, self.tlrows = Ltl, TL.shape[1]
        self.psf_index: dict[tuple[int, int], int] = {}
        self.psf_packs: list = []
        self.psf_table = np.zeros((0, 7), dtype=np.uint64)
        self.branch: dict[tuple[int, int], tuple] = {}
        from physics.hf.compound.decay_batch import _twopi

        self.twopi = _twopi()
        self.eendmax = eendmax
        self.front_trans: dict[int, tuple] = {}

    def trans_pack(self, t: int):
        """CENGBOOK: type t's (Tjl, lmax) as `ce_densprepare` reads them, once per run."""
        got = self.front_trans.get(t)
        if got is None:
            tjl, _tl, lmax = self.cas.trans[t]
            if isinstance(tjl, torch.Tensor) or np.ndim(tjl) != 3 or np.shape(tjl)[2] != 3:
                raise _Unsupported("Tjl")
            got = self.front_trans[t] = (np.ascontiguousarray(tjl, dtype=np.float64),
                                         np.ascontiguousarray(lmax, dtype=_I64))
        return got

    def psf(self, Z: int, A: int) -> int:
        """The PSF pack index of `cas.gamma_params(Z, A)`, or -1."""
        key = (Z, A)
        got = self.psf_index.get(key)
        if got is not None:
            return got
        from physics.hf.compound.psf_nx2 import _pack

        gp = self.cas.gamma_params(Z, A)
        pack = None if gp is None or gp.gammax != self.cas.gammax else _pack(gp)
        idx = -1
        if pack is not None:
            idx = len(self.psf_packs)
            self.psf_packs.append((gp, pack))
            row = np.array([[_ptr(a) for a in pack]], dtype=np.uint64)
            self.psf_table = np.ascontiguousarray(np.concatenate([self.psf_table, row]))
        self.psf_index[key] = idx
        return idx

    def csr(self, sp, xrows: int):
        key = (id(sp.branch), xrows)
        got = self.branch.get(key)
        if got is not None and got[0] is sp.branch:
            return got[1:]
        off = np.zeros(xrows + 1, dtype=_I64)
        bk, br = [], []
        br_of = sp.branch
        for nex in range(xrows):
            for k, ratio in br_of.get(nex, ()):
                bk.append(int(k))
                br.append(float(ratio))
            off[nex + 1] = len(bk)
        got = (sp.branch, off, np.asarray(bk, dtype=_I64).reshape(-1),
               np.asarray(br, dtype=np.float64).reshape(-1))
        self.branch[key] = got
        return got[1:]


def _discfactor(sp) -> float:
    if sp.nlast <= sp.ntop:
        return 1.0
    ratio = (sp.ncum_nl - sp.ntop) / (sp.nlast - sp.ntop)
    if isinstance(ratio, torch.Tensor):
        raise _Unsupported("a level-density parameter on a graph")
    return min(max(ratio, 0.5), 2.0)


def cascade(run: _Run, st, maxz: int, maxn: int, seed: dict, popeps_mb: float, k0: int,
            xsreacinc_mb: float, xsbinary_mb: dict, feedbinary_mb, flagfission: bool, fis, prq):
    """`cas.populations` twice with `propagate_exmax` between, `_seed_mulpre` and
    `multiple_emission` (NATIVEX's walk, multiple pre-equilibrium included) in one `ce_cascade`
    call: the `MultipleResult` the Python path returns, with `st.spec` as it leaves it; or raises
    `_Unsupported` before anything but `st.spec` entries the Python path also makes is touched.

    TALYS: multiple.f90:1 (multiple), cascade.f90:1 (cascade), compound.f90:1 (compound)
    Test: tests/hf/test_engine_c.py
    """
    from physics.hf.density.overrides import torch_path
    from physics.hf.emission import multiple as M
    from physics.hf.emission.feeding import NUMN, NUMZ

    cas = run.cas
    so = lib()
    if so is None or not run.ok or cas.flagfullhf or not cas.batched or \
            cas.DECAY_CHUNK is not None or cas.diff_params or torch_path(cas.gamma_overrides):
        raise _Unsupported("engine")
    mulpre = {t: bool(on) for t, on in prq.mulpre.items() if on}
    P1 = 0
    if mulpre:
        if bool(cas.options.flaggshell):
            raise _Unsupported("flaggshell multiple pre-equilibrium")
        for t in mulpre:
            arr = prq.xspopph2_mb.get(t)
            if arr is not None:
                if isinstance(arr, torch.Tensor) and arr.requires_grad or np.ndim(arr) != 5:
                    raise _Unsupported("particle-hole population shape")
                P1 = int(arr.shape[1])
        if any(isinstance(x, torch.Tensor) for x in (cas.trans[1][0], cas.trans[2][0])):
            raise _Unsupported("tensor Tjl")

    def grid_set():
        return [(zc, nc) for zc in range(maxz + 1) for nc in range(maxn + 1)
                if zc <= NUMZ and nc <= NUMN
                and (float(st.exmax[zc, nc]) > 0.0 or (zc, nc) == (0, 0))]

    first = grid_set()
    for key in first:
        cas.spec(st, *key)
    for key in first:
        cas.propagate_exmax(st, *key)
    nuclei = grid_set()
    return _Packed(run, so, st, nuclei, maxz, maxn, P1).run(
        seed, mulpre, prq, popeps_mb, k0, xsreacinc_mb, xsbinary_mb, feedbinary_mb,
        flagfission, fis, M)


class _Packed:
    """One energy's `ce_cascade` arguments: the spec tables (capacity for every daughter), the
    populations and the output arena."""

    def __init__(self, run, so, st, nuclei, maxz, maxn, P1):
        cas = run.cas
        self.run_, self.so, self.st, self.cas = run, so, st, cas
        self.nuclei, self.in_set = nuclei, set(nuclei)
        self.maxz, self.maxn, self.P1 = maxz, maxn, P1
        cap = 7 * len(nuclei) + 1
        self.W = W = maxn + 3
        self.idx = np.full((maxz + 3) * W, -1, dtype=_I64)
        self.si = np.zeros((cap, SI), dtype=_I64)
        self.sd = np.zeros((cap, SD))
        self.spt = np.zeros((cap, SP), dtype=np.uint64)
        self.sot = np.zeros((cap, SO), dtype=np.uint64)
        self.keep, self.specs, self.keys = [], [], []
        self.fiso0 = cas.fisom(0, 0, st) if st.first_energy else None
        self.pops = {}
        for key in nuclei:
            self.add(key)
        self.error = None

    def add(self, key) -> int:
        cas, st = self.cas, self.st
        zc, nc = key
        sp = cas.spec(st, zc, nc)
        s = len(self.specs)
        self.specs.append(sp)
        self.keys.append(key)
        self.idx[zc * self.W + nc] = s
        rhog = sp.rhogrid
        if not (isinstance(rhog, np.ndarray) and rhog.dtype == np.float64 and rhog.ndim == 3
                and rhog.shape[1] == NJ and rhog.flags.c_contiguous):
            rhog = np.asarray(rhog, dtype=np.float64)
            if rhog.ndim != 3 or rhog.shape[1] != NJ:
                raise _Unsupported("rhogrid shape")
            rhog = np.ascontiguousarray(rhog)
        arrs = (np.asarray(sp.ex_mev, dtype=np.float64), np.asarray(sp.dex_mev, dtype=np.float64),
                np.asarray(sp.maxj, dtype=_I64), np.asarray(sp.parlev, dtype=_I64),
                np.asarray(sp.jdis, dtype=np.float64), np.asarray(sp.tau_s, dtype=np.float64), rhog)
        if any(not a.flags.c_contiguous for a in arrs):
            arrs = tuple(np.ascontiguousarray(a) for a in arrs)
        maxex = int(sp.maxex)
        inset = key in self.in_set
        self.si[s, :11] = (zc, nc, sp.Z, sp.A, maxex, sp.nlast, sp.nlast_grid, sp.ntop,
                           rhog.shape[0], inset, len(arrs[0]))
        d = self.sd[s]
        d[0] = float(sp.exmax_mev)
        d[1] = _discfactor(sp)
        sep = sp.sep_mev
        d[2:9] = (sep[0], sep[1], sep[2], sep[3], sep[4], sep[5], sep[6])
        d[9:17] = self.fiso0 if key == (0, 0) and self.fiso0 is not None else 1.0
        p = self.spt[s]
        p[:7] = [a.__array_interface__["data"][0] for a in arrs]
        self.keep.append(arrs)
        if inset:
            xrows = maxex + 1
            off, bk, br = self.run_.csr(sp, xrows)
            X = np.zeros((xrows, NJ, 2))
            XE = np.zeros(xrows)
            got = [off, bk, br, X, XE]
            if self.P1:
                ph = np.zeros((xrows, self.P1 ** 4))
                phf = np.zeros(xrows, dtype=np.uint8)
                got += [ph, phf]
            p[7: 7 + len(got)] = [_ptr(a) for a in got]
            self.keep.append(got)
            self.pops[s] = got
        return s

    # ---- callbacks (exceptions become refusals; the energy then runs the Python path)
    def spec_cb(self, zix, nix):
        try:
            from physics.hf.emission.feeding import NUMN, NUMZ

            if zix > NUMZ or nix > NUMN or zix >= self.maxz + 3 or nix >= self.W:
                return -1
            return self.add((zix, nix))
        except Exception as ex:  # noqa: BLE001
            self.error = ex
            return -1

    def psf_cb(self, s, out):
        try:
            sp = self.specs[s]
            i = self.run_.psf(int(sp.Z), int(sp.A) - 1)
            if i < 0:
                return 1
            for k, a in enumerate(self.run_.psf_packs[i][1]):
                out[k] = _ptr(a)
            return 0
        except Exception as ex:  # noqa: BLE001
            self.error = ex
            return 1

    def fis_cb(self, s, m, bins, out, nj):
        try:
            sp = self.specs[s]
            nb = self.fis.nfisbar(int(sp.Z), int(sp.A))
            if not nb:
                return 2
            from physics.hf.compound.fission_batch_decay import FissionLadder

            lad = FissionLadder(self.fis, int(sp.Z), int(sp.A), float(self.cas.fiso()[0]))
            if not lad.covered():
                return 1
            b = np.ctypeslib.as_array(bins, shape=(m,)).copy()
            w = np.ascontiguousarray(lad.widths(sp, b), dtype=np.float64)
            self.keep.append(w)
            out[0] = _ptr(w)
            nj[0] = w.shape[1]
            return 0
        except Exception as ex:  # noqa: BLE001
            self.error = ex
            return 1

    def mpe_cb(self, s, arrs, block):
        try:
            return self._mpe(s, arrs, block)
        except Exception as ex:  # noqa: BLE001
            self.error = ex
            return 1

    def _mpe(self, s, arrs, block):
        """`multiple_native._Walk.attach_mpe` less the arrays the C side owns."""
        from physics.hf.compound.decay_fast import nexmax_rows
        from physics.hf.compound.prepare import NUMJ
        from physics.hf.core.grids import emission_end
        from physics.hf.density.particle_hole import EFERMI_MEV
        from physics.hf.preeq.prepare import single_particle_densities
        from physics.hf.preeq.spin import preeq_spin_distribution

        cas, st = self.cas, self.st
        sp = self.specs[s]
        P1 = self.P1
        zc, nc = self.keys[s]
        xrows = int(sp.maxex) + 1
        tj = [cas.trans[t][0] for t in (1, 2)]
        dsp = [cas.spec(st, sp.zix + PARZ[t], sp.nix + PARN[t]) for t in (1, 2)]
        nb = max(d.maxex for d in dsp) + 1
        flags = np.ctypeslib.as_array(ctypes.cast(int(arrs[1]), ctypes.POINTER(ctypes.c_uint8)),
                                      shape=(xrows,))
        bins = np.flatnonzero(flags)
        nxm = np.zeros((xrows, 7), dtype=_I64)
        nxm[bins] = nexmax_rows(cas, st, sp, bins)
        key = ("_nativex_eend", round(float(self.etot), 9))
        eend = st.__dict__.get(key)
        if eend is None:
            eend, _ = emission_end(cas.rg.egrid, cas.rg.maxen, self.etot,
                                   {t: cas.rg.s0[t] for t in range(7)}, cas.rg.ebegin,
                                   {t: False for t in range(7)})
            st.__dict__[key] = eend
        kph = float(cas.params.at("kph"))
        rnj = cas.__dict__.get("_nativex_rnj")
        nj1 = NUMJ + 1
        if rnj is None:
            r = preeq_spin_distribution(cas.options, cas.params, cas.At)
            v = np.zeros(nj1)
            row = r["RnJ"][2].detach().numpy()
            v[: min(nj1, row.shape[0])] = row[:nj1]
            jj = np.arange(nj1, dtype=np.float64)
            rnj = cas.__dict__["_nativex_rnj"] = 0.5 * (2.0 * jj + 1.0) * v / float(r["RnJsum"][2])
        jw = np.zeros((2, nb, nj1))
        dex = np.zeros((2, nb))
        dx = np.zeros((2, nb))
        for di, d in enumerate(dsp):
            k = min(nb, d.maxex + 1, len(d.ex_mev))
            dx[di, :k] = np.asarray(d.ex_mev[:k], dtype=np.float64)
            dex[di, :k] = np.asarray(d.dex_mev[:k], dtype=np.float64)
            for nexout in range(nb):
                mj = int(d.maxj[nexout]) if nexout <= d.maxex else 0
                jw[di, nexout, : min(mj, NUMJ) + 1] = rnj[: min(mj, NUMJ) + 1]
        _, gpc, gnc = single_particle_densities(sp.Z, sp.A - sp.Z, kph)
        c0 = cas.spec(st, 0, 0)
        _, gp0, gn0 = single_particle_densities(c0.Z, c0.A - c0.Z, kph)
        dg = [single_particle_densities(d.Z, d.A - d.Z, kph) for d in dsp]
        rg = cas.rg
        mi = np.array([P1 - 1, nb, dsp[0].nlast_grid, dsp[1].nlast_grid, dsp[0].zix, dsp[1].zix,
                       dsp[0].nix, dsp[1].nix, dsp[0].maxex, dsp[1].maxex, rg.ebegin[1],
                       rg.ebegin[2], eend[1], eend[2], rg.maxen, xrows], dtype=_I64)
        md = np.array([gpc, gnc, gp0, gn0, EFERMI_MEV, sp.sep_mev[1], sp.sep_mev[2], dg[0][1],
                       dg[1][1], dg[0][2], dg[1][2]], dtype=np.float64)
        own = [np.ascontiguousarray(np.asarray(rg.egrid, dtype=np.float64)[: rg.maxen + 1],
                                    dtype=np.float32),
               np.ascontiguousarray(np.asarray(tj[0])[:, 0, 2], dtype=np.float64),
               np.ascontiguousarray(np.asarray(tj[1])[:, 0, 2], dtype=np.float64),
               np.zeros(2 * nb), np.zeros(2 * nb), np.zeros(2 * nb * nj1), np.zeros(2 * nb)]
        mp = np.array([arrs[0], arrs[1], _ptr(nxm), _ptr(jw), _ptr(dx), _ptr(dex), _ptr(own[0]),
                       _ptr(own[1]), _ptr(own[2]), arrs[2], arrs[3], arrs[4], arrs[5], arrs[6],
                       _ptr(own[3]), _ptr(own[4]), _ptr(own[5]), _ptr(own[6])], dtype=np.uint64)
        blk = np.array([_ptr(mi), _ptr(md), _ptr(mp)], dtype=np.uint64)
        self.keep.append((nxm, jw, dx, dex, mi, md, mp, blk, own))
        block[0] = _ptr(blk)
        return 0

    def run(self, seed, mulpre, prq, popeps_mb, k0, xsreacinc_mb, xsbinary_mb, feedbinary_mb,
            flagfission, fis, M):
        from physics.hf.emission.feed_table import FeedTable

        cas, st, run_ = self.cas, self.st, self.run_
        self.fis = fis if flagfission else None
        self.etot = float(st.exmax0[0, 0])
        in_set, idx, W = self.in_set, self.idx, self.W
        # the binary seed (populations' second call) and `_seed_mulpre`
        for t, (xspop, xspopex, xspopnuc) in seed.items():
            key = (PARZ[t], PARN[t])
            if key not in in_set:
                continue
            s = int(idx[key[0] * W + key[1]])
            got = self.pops[s]
            X, XE = got[3], got[4]
            k = min(X.shape[0], xspop.shape[0])
            X[:k] = np.asarray(xspop)[:k]
            XE[:k] = np.asarray(xspopex)[:k]
            self.sd[s, 17] = float(xspopnuc)
        for t in mulpre:
            key = (PARZ[t], PARN[t])
            if key not in in_set:
                continue
            s = int(idx[key[0] * W + key[1]])
            self.si[s, 13] = 1
            arr = prq.xspopph2_mb.get(t)
            if arr is None or not self.P1:
                continue
            got = self.pops[s]
            ph, phf = got[5], got[6]
            for nex in range(min(arr.shape[0], got[4].shape[0])):
                row = arr[nex]
                if float(row.sum()) != 0.0:
                    ph[nex] = np.asarray(row, dtype=np.float64).reshape(-1)
                    phf[nex] = 1
        # the output arena: per nucleus its feed tables, popexcl, fisfeed, xsfeed, doubles
        views = []
        f_off = u_off = 0
        for s, key in enumerate(self.nuclei):
            zc, nc = key
            xrows = int(self.si[s, 4]) + 1
            tl = []
            for t in range(7):
                dk = (zc + PARZ[t], nc + PARN[t])
                if dk in in_set and M._records_feedexcl(zc, nc, t):
                    drows = int(self.si[int(idx[dk[0] * W + dk[1]]), 4]) + 1
                    tl.append((t, drows, f_off, u_off))
                    f_off += (xrows + 1) * drows
                    u_off += (xrows + 1) * drows
            views.append((xrows, f_off, u_off, tl))
            f_off += 2 * (xrows + 1) + 16
            u_off += (xrows + 1) + 8
        F = np.zeros(f_off)
        U = np.zeros(u_off, dtype=np.uint8)
        nset = len(self.nuclei)
        ptrtabs = np.zeros((nset, 14), dtype=np.uint64)
        fb, ub, pb = _ptr(F), _ptr(U), _ptr(ptrtabs)
        sot = self.sot
        for s, (xrows, fo, uo, tl) in enumerate(views):
            o = sot[s]
            o[0], o[1] = fb + 8 * fo, fb + 8 * (fo + xrows + 1)
            o[3], o[7] = fb + 8 * (fo + 2 * (xrows + 1)), fb + 8 * (fo + 2 * (xrows + 1) + 8)
            o[2], o[4] = ub + uo, ub + uo + xrows + 1
            for t, drows, tf, tu in tl:
                ptrtabs[s, t] = fb + 8 * tf
                ptrtabs[s, 7 + t] = ub + tu
            o[5], o[6] = pb + 8 * 14 * s, pb + 8 * (14 * s + 7)
        cbs = (_SPEC_CB(self.spec_cb), _PSF_CB(self.psf_cb),
               _FIS_CB(self.fis_cb) if self.fis is not None else None,
               _MPE_CB(self.mpe_cb) if self.P1 else None)
        cp = [ctypes.cast(c, ctypes.c_void_p).value if c is not None else 0 for c in cbs]
        ip = np.array([self.maxz, self.maxn, nset, k0, st.lmaxinc, cas.rg.maxen, run_.Ltl,
                       run_.tlrows, run_.egrid.size, cas.gammax + 1, W, self.P1], dtype=_I64)
        dp = np.array([cas.transeps, popeps_mb, run_.twopi])
        pp = np.array([_ptr(run_.TL), _ptr(run_.LM), _ptr(run_.head0), _ptr(run_.egrid),
                       _ptr(run_.egrid32), _ptr(run_.ebegin), _ptr(run_.eend), _ptr(idx),
                       _ptr(self.si), _ptr(self.sd), _ptr(self.spt), 0, _ptr(sot), cp[2], cp[0],
                       cp[1], cp[3]], dtype=np.uint64)
        rc = self.so.ce_cascade(_ptr(ip), _ptr(dp), _ptr(pp))
        del cbs
        if rc != 0:
            raise _Unsupported(f"ce_cascade refused {self.keys[rc - 1]}: {self.error!r}")
        self.views, self.F, self.U, self.ptrtabs = views, F, U, ptrtabs
        self.k0, self.xsreacinc_mb, self.xsbinary_mb = k0, xsreacinc_mb, xsbinary_mb
        self.feedbinary_mb, self.flagfission = feedbinary_mb, flagfission
        return self

    def result(self):
        """The `MultipleResult` `multiple_emission` returns, off the arena."""
        from physics.hf.emission import multiple as M
        from physics.hf.emission.feed_table import FeedTable

        views, F, U = self.views, self.F, self.U
        k0, xsreacinc_mb, xsbinary_mb = self.k0, self.xsreacinc_mb, self.xsbinary_mb
        feedbinary_mb, flagfission = self.feedbinary_mb, self.flagfission
        res = M.MultipleResult(popexcl_mb={}, feedexcl_mb={})
        si, sd = self.si, self.sd
        for s, key in enumerate(self.nuclei):
            xrows, fo, uo, tl = views[s]
            maxex = xrows - 1
            popexcl, feedexcl, fisfeed, xsfeed = {}, {}, {}, {}
            res.popexcl_mb[key] = popexcl
            res.feedexcl_mb[key] = feedexcl
            res.fisfeedex_mb[key] = fisfeed
            res.xsfeed_mb[key] = xsfeed
            res.xspartial_mb[key] = {}
            status = int(si[s, 12])
            if status != 1:
                popexcl.update(zip(range(maxex, 0, -1), F[fo + maxex: fo: -1].tolist()))  # noqa: B905
                dq = fo + 2 * (xrows + 1) + 8
                for t, drows, tf, tu in tl:
                    if status == 3 and not (t == 0 and F[dq + 1]):
                        continue
                    fe = FeedTable.__new__(FeedTable)
                    fe.val = F[tf: tf + (xrows + 1) * drows].reshape(xrows + 1, drows)
                    fe.present = U[tu: tu + (xrows + 1) * drows].reshape(xrows + 1, drows).view(bool)
                    fe.extra = {}
                    feedexcl[t] = fe
                if status == 2:
                    ff = U[uo: uo + xrows]
                    if ff.any():
                        for nex in np.flatnonzero(ff)[::-1].tolist():
                            fisfeed[nex] = float(F[fo + xrows + 1 + nex])
                    xq = fo + 2 * (xrows + 1)
                    for t, fl in enumerate(U[uo + xrows + 1: uo + xrows + 9].tolist(), start=-1):
                        if fl:
                            xsfeed[t] = float(F[xq + t + 1])
                res.xsgamdistot_mb[key] = float(F[dq])
            else:
                res.xsgamdistot_mb[key] = 0.0
            res.xspopnuc_mb[key] = float(sd[s, 17])
            if key == (0, 0):
                M._binary_feed(res, key, 0, 0, k0, xsreacinc_mb, xsbinary_mb, feedbinary_mb,
                               _Top(maxex), flagfission)
        return res

    def channels(self, cinp, b, xsbinary, chst: "_ChanState", keys: "_Keys"):
        """CENGBOOK: `exclusive_channels(built.channels(cinp, st, self.result(), b, xsbinary))`
        as `run` reads it, in one `ce_channels` call over the arena.

        TALYS: channels.f90:1 (channels), totalxs.f90:1 (totalxs), residual.f90:1 (residual)
        Test: tests/hf/test_engine_c.py
        """
        from physics.hf.emission.channels import NUMCHANTOT

        cas, st = self.cas, self.st
        if not getattr(self.so, "channels_ok", False):
            raise _Unsupported("no BLAS pointers for the channels")
        maxz, maxn = int(cinp.maxz), int(cinp.maxn)
        if maxz != self.maxz or maxn != self.maxn:
            raise _Unsupported("channel grid")
        W = self.W
        for key in st.spec:  # a nucleus with a grid but outside the cascade set: its record
            zc, nc = key
            if zc <= maxz and nc <= maxn and self.idx[zc * W + nc] < 0:
                if len(self.specs) >= self.si.shape[0]:
                    raise _Unsupported("spec capacity")
                self.add(key)
        e0 = st.exmax0
        if not (isinstance(e0, np.ndarray) and e0.dtype == np.float32 and e0.flags.c_contiguous):
            raise _Unsupported("exmax0")
        fbp = np.zeros(7, dtype=np.uint64)
        fbn = np.zeros(7, dtype=_I64)
        keep = []
        for t, arr in (b.feedbinary_mb or {}).items():
            if isinstance(arr, torch.Tensor):
                if arr.requires_grad:
                    raise _Unsupported("feedbinary on a graph")
                arr = arr.numpy()
            a = np.ascontiguousarray(arr, dtype=np.float64)
            keep.append(a)
            fbp[t], fbn[t] = _ptr(a), a.shape[0]
        nch = NUMCHANTOT + 1
        ocode = np.zeros(nch, dtype=_I64)
        oxs = np.zeros(nch)
        ores = np.zeros((maxz + 1) * (maxn + 1))
        oint = np.zeros(2, dtype=_I64)
        odbl = np.zeros(2)
        ip = np.zeros(25, dtype=_I64)
        ip[:11] = (maxz, maxn, cinp.zinit, cinp.ninit, cinp.maxchannel, cinp.k0,
                   bool(cinp.flagfission), W, NUMCHANTOT, chst.idnumfull, chst.opennum)
        ip[11:18] = [bool(x) for x in cinp.parskip]
        ip[18:24] = [bool(cinp.parinclude[t + 1]) for t in range(1, 7)]
        ip[24] = e0.shape[1]
        dp = np.array([cinp.xseps_mb, cinp.targete_mev, float(cas.m.s_mev[0, 0, cas.k0]),
                       float(e0[0, 0]), float(xsbinary[0]) if xsbinary is not None else 0.0,
                       1.0 if xsbinary is not None else 0.0])
        pp = np.array([_ptr(self.idx), _ptr(self.si), _ptr(self.sd), _ptr(self.spt),
                       _ptr(self.sot), _ptr(e0), _ptr(chst.open), _ptr(fbp), _ptr(fbn),
                       _ptr(ocode), _ptr(oxs), _ptr(ores), _ptr(oint), _ptr(odbl)],
                      dtype=np.uint64)
        rc = self.so.ce_channels(_ptr(ip), _ptr(dp), _ptr(pp))
        if rc != 0:
            raise _Unsupported(f"ce_channels refused ({rc})")
        chst.idnumfull, chst.opennum = int(ip[9]), int(ip[10])
        n = int(oint[0])
        xsch = dict(zip(ocode[:n].tolist(), oxs[:n].tolist()))  # noqa: B905
        return _Chan(xsch, keys.resid(ores), float(odbl[0]), float(odbl[1]))


_SPEC_CB = ctypes.CFUNCTYPE(ctypes.c_int64, ctypes.c_int64, ctypes.c_int64)
_PSF_CB = ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_int64, ctypes.POINTER(ctypes.c_uint64))
_MPE_CB = ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_int64, ctypes.POINTER(ctypes.c_uint64),
                           ctypes.POINTER(ctypes.c_uint64))


class _ChanState:
    """CENGBOOK: `ExclusiveState` as the byte map `ce_channels` reads (one byte per channel key
    (n, p, d, t, h, alpha) within channels.f90's caps), convertible both ways for an energy that
    runs the Python channels."""

    DIMS = (9, 5, 3, 2, 2, 4)

    def __init__(self):
        self.open = np.zeros(int(np.prod(self.DIMS)), dtype=np.uint8)
        self.idnumfull = False
        self.opennum = 0

    def to_py(self):
        from physics.hf.emission.channels import ExclusiveState

        keys = {tuple(int(v) for v in np.unravel_index(q, self.DIMS))
                for q in np.flatnonzero(self.open).tolist()}
        return ExclusiveState(keys, bool(self.idnumfull))

    def from_py(self, st) -> None:
        self.open[:] = 0
        for key in st.chanopen:
            self.open[np.ravel_multi_index(key, self.DIMS)] = 1
        self.idnumfull, self.opennum = bool(st.idnumfull), len(st.chanopen)


class _Chan:
    """What `run` reads of a `ChannelResult`."""

    __slots__ = ("xschannel_mb", "residual", "xsfistot_mb", "xsresprod_mb")

    def __init__(self, xschannel_mb, residual, xsfistot_mb, xsresprod_mb):
        self.xschannel_mb, self.residual = xschannel_mb, residual
        self.xsfistot_mb, self.xsresprod_mb = xsfistot_mb, xsresprod_mb

    @classmethod
    def of(cls, ch):
        from physics.hf.results import residual_key

        return cls(ch.xschannel_mb, {residual_key(Z, A): v for (Z, A), v in ch.residual_mb.items()},
                   ch.xsfistot_mb, ch.xsresprod_mb)


class _Keys:
    """The run's result names, formatted once."""

    def __init__(self, cas, cinp):
        from physics.hf.results import residual_key

        maxz, maxn = int(cinp.maxz), int(cinp.maxn)
        self.live_t = [t for t in range(7) if not cinp.parskip[t]]
        self.rkeys = [residual_key(*cas.zn(zc, nc)) for zc in range(maxz + 1)
                      for nc in range(maxn + 1)]
        self.ckeys: dict[int, str] = {}
        self.lkeys: dict[tuple[int, int], list[str]] = {}

    def levels(self, k0: int, xsdisc: dict) -> dict:
        """`{level_key(k0, t, nex): float(v[nex])}` over `binary`'s `xsdisc`."""
        from physics.hf.results import level_key

        out = {}
        lk = self.lkeys
        for t, v in xsdisc.items():
            n = v.shape[0]
            names = lk.get((t, n))
            if names is None:
                names = lk[(t, n)] = [level_key(k0, t, nex) for nex in range(n)]
            out.update(zip(names, v.tolist()))  # noqa: B905
        return out

    def resid(self, pops: np.ndarray) -> dict:
        return dict(zip(self.rkeys, pops.tolist()))  # noqa: B905

    def chans(self, xsch: dict) -> dict:
        ck = self.ckeys
        out = {}
        for code, v in xsch.items():
            k = ck.get(code)
            if k is None:
                k = ck[code] = f"xs{code:06d}"
            out[k] = v
        return out


class _Top:
    __slots__ = ("maxex",)

    def __init__(self, maxex: int):
        self.maxex = maxex



def front(run: _Run, st, binp, cinp, etot: float, a_e: dict, fkw: dict):
    """CENGBOOK: `compound_target_inputs(compound_inputs(cas, st, binp, cinp, etot, a_e, **fkw))`
    and the `CompoundInputs` fields `binary_cross_sections` reads, with the primary `densprepare`
    and `_exact_incident_channel` in `ce_densprepare` writing straight into `nx_target`'s arrays
    (`target_native.target`'s packing), or raises `_Unsupported` before anything is changed.

    TALYS: densprepare.f90:1 (densprepare), compnorm.f90:1 (compnorm), comptarget.f90:1 (comptarget)
    Test: tests/hf/test_engine_c.py
    """
    from types import SimpleNamespace

    from physics.hf.compound import fission_batch_target as fbt
    from physics.hf.compound.chain import _NormView
    from physics.hf.compound.dens_reference import _to_updown_axis
    from physics.hf.compound.norm_reference import chained_formation
    from physics.hf.compound.prepare import PARSPIN2, SPIN2
    from physics.hf.compound.psf_nx2 import _pack
    from physics.hf.compound.target import BinaryPopulation
    from physics.hf.compound.target_native import _nodes
    from physics.hf.core.constants import talys_constants
    from physics.hf.emission.emit_nx2 import glue_enabled
    from physics.hf.native import nativex

    cas = run.cas
    so = lib()
    if (so is None or not getattr(so, "front_ok", False) or not run.ok or cas.diff_params
            or cas.flagfullhf or not glue_enabled()):
        raise _Unsupported("front")
    o = cas.options
    k0, lt = int(binp.k0), int(binp.ltarget)
    use_wfc = bool(binp.e_inc_mev <= cas.ewfc_mev) and o.wmode >= 1
    if use_wfc and (o.wmode != 1 or o.WFCfactor not in (1, 2, 3)):
        raise _Unsupported("width fluctuation mode")
    gammax = int(o.gammax)
    gs = cas.gamma_strength(cas.Zt, cas.At)
    gp = cas.gamma_params(cas.Zt, cas.At)
    if (gs is None or getattr(gs, "batch", None) is None or getattr(gs, "differentiable", False)
            or gp is None or gp.gammax != gammax):
        raise _Unsupported("photon strength")
    pack = _pack(gp)
    if pack is None:
        raise _Unsupported("photon strength pack")
    cf, lmaxinc = chained_formation(cas, _NormView(binp), a_e)
    inc = cas.incident(binp.e_inc_mev)
    tjlinc = _to_updown_axis(inc.tjl_inc[0], k0)[: lmaxinc + 1]
    if isinstance(tjlinc, torch.Tensor):
        if tjlinc.requires_grad:
            raise _Unsupported("Tjlinc on a graph")
        tjlinc = tjlinc.numpy()
    tjlinc = np.ascontiguousarray(tjlinc, dtype=np.float64)
    fnorm = cas.fiso()
    sp0 = cas.spec(st, 0, 0)
    rg = cas.rg
    ti = np.zeros((7, 12), dtype=_I64)
    td = np.zeros((7, 4))
    tp = np.zeros((7, 10), dtype=np.uint64)
    to = np.zeros((7, 4), dtype=np.uint64)
    keep, outs = [], []
    ninc = min(lmaxinc + 1, tjlinc.shape[0])
    for t in range(7):
        d = cas.spec(st, PARZ[t], PARN[t])
        nex = int(d.maxex) + 1
        arrs = (np.ascontiguousarray(d.ex_mev, dtype=np.float64),
                np.ascontiguousarray(d.maxj, dtype=_I64),
                np.ascontiguousarray(d.parlev, dtype=_I64),
                np.ascontiguousarray(d.jdis, dtype=np.float64),
                np.ascontiguousarray(d.rhogrid, dtype=np.float64))
        if (min(a.shape[0] for a in arrs[:4]) < nex or arrs[4].ndim != 3
                or arrs[4].shape[1:] != (NJ, 2)):
            raise _Unsupported("residual arrays")
        keep.append(arrs)
        rho = np.zeros((nex, NJ, 2))
        lmaxhf = np.zeros(nex, dtype=_I64)
        jdis2 = np.zeros(nex, dtype=_I64)
        ti[t, :4] = (nex, d.nlast, d.ntop, arrs[4].shape[0])
        td[t, :3] = (_discfactor(d), sp0.sep_mev[t], float(fnorm[t + 1]))
        tp[t, :5] = [_ptr(a) for a in arrs]
        if t == 0:
            L = gammax + 1
            T = np.zeros((nex, L, 2))
        else:
            tjl, lmax = run.trans_pack(t)
            L = tjl.shape[1]
            Lo = max(L, ninc) if (t == k0 and 0 <= lt <= nex - 1) else L
            T = np.zeros((nex, Lo, 3))
            ti[t, 4:11] = (int(rg.ebegin[t]), min(int(run.eendmax[t]), rg.maxen), rg.maxen, L,
                           run.egrid.size, Lo, tjl.shape[0])
            tp[t, 5:9] = (_ptr(run.egrid), _ptr(run.egrid32f), _ptr(tjl), _ptr(lmax))
            L = Lo
        to[t] = (_ptr(rho), _ptr(lmaxhf), _ptr(jdis2), _ptr(T))
        outs.append((nex, int(d.nlast), L, rho, lmaxhf, np.ascontiguousarray(arrs[1][:nex]),
                     jdis2, np.ascontiguousarray(arrs[2][:nex]), T))
    ip = np.array([k0, lt, lmaxinc, gammax, tjlinc.shape[0], 1], dtype=_I64)
    dp = np.array([float(etot), cas.transeps, float(etot) - sp0.sep_mev[1],
                   float(talys_constants()["twopi"]) * float(fnorm[1])])
    pk = np.array([_ptr(a) for a in pack], dtype=np.uint64)
    pp = np.array([_ptr(ti), _ptr(td), _ptr(tp), _ptr(to), _ptr(pk), _ptr(tjlinc)],
                  dtype=np.uint64)
    rc = so.ce_densprepare(_ptr(ip), _ptr(dp), _ptr(pp))
    if rc != 0:
        raise _Unsupported(f"ce_densprepare refused type {rc - 1}")
    # target_native.target on those arrays
    nexmax = max(x[0] for x in outs)
    cells = [(J2, p) for p in (-1, 1) for J2 in range(cf.j2beg, cf.j2end + 1, 2)]
    pop = np.zeros((7, nexmax, NJ, 2))
    xsfis = torch.zeros((), dtype=DTYPE)
    if cells:
        if use_wfc and lt > outs[k0][1]:
            raise _Unsupported("target level above Nlast")
        nxl = nativex.lib()
        tip = np.zeros(20 + 8 * 7, dtype=_I64)
        tpp = np.zeros(10 + 6 * 7, dtype=np.uint64)
        for t, (nex, nlast, L, rho, lmaxhf, maxj, jdis2, parlev, T) in enumerate(outs):
            tip[20 + 8 * t: 26 + 8 * t] = (1, nex, nlast, L, SPIN2[t], PARSPIN2[t])
            tpp[10 + 6 * t: 16 + 6 * t] = [_ptr(a) for a in (rho, lmaxhf, maxj, jdis2, parlev, T)]
        j2 = np.array([c[0] for c in cells], dtype=_I64)
        pidx = np.array([0 if c[1] == -1 else 1 for c in cells], dtype=_I64)
        tpp[0], tpp[1], tpp[2] = _ptr(j2), _ptr(pidx), _ptr(tjlinc)
        view = SimpleNamespace(flagfission=bool(cinp.flagfission), nfisbar=fkw.get("nfisbar", 0),
                               tfis=fkw.get("tfis") or {}, tfisA=fkw.get("tfisA") or {},
                               rhofisA=fkw.get("rhofisA") or {})
        fis = fbt.cell_fission_widths(view, cells)
        if fis is not None:
            fa = np.ascontiguousarray(fis.numpy(), dtype=np.float64)
            keep.append(fa)
            tpp[3] = _ptr(fa)
            if use_wfc:
                hum = [np.ascontiguousarray(x.numpy()) for x in fbt.hump_channels(view, cells, fis)]
                hum[3] = hum[3].astype(_I64)
                keep.append(hum)
                tpp[4:8] = [_ptr(x) for x in hum]
        x, w = _nodes()
        tpp[8], tpp[9] = _ptr(x), _ptr(w)
        tip[:12] = (len(cells), int(use_wfc), o.WFCfactor if use_wfc else 1, k0, lt, nexmax,
                    int(fis is not None), binp.targetspin2, binp.target_parity, lmaxinc,
                    tjlinc.shape[0], 7)
        tip[12:19] = range(7)
        tdp = np.array([float(cf.cn_factor_mb)])
        out = np.zeros(2)
        if nxl.nx_target(_ptr(tip), _ptr(tpp), _ptr(tdp), _ptr(pop), _ptr(out)) != 0:
            raise _Unsupported("nx_target refused")
        xsfis = torch.tensor(out[0], dtype=DTYPE)
    popt = torch.from_numpy(pop)
    el = popt[k0, lt].sum() if lt <= outs[k0][0] - 1 else torch.zeros((), dtype=DTYPE)
    return (BinaryPopulation(popt[None], el.reshape(1), xsfis.reshape(1)),
            SimpleNamespace(k0=k0, ltarget=lt))


def binary_lean(inp, state):
    """CENGBOOK: `emission.binary.binary(inp, state)` (NATIVEX2's `emit_nx2.binary`, the per-type
    C kernel) for what `cases`/`run` read of it -- `xspop`, `xspopex`, `feedbinary`, `xsdisc`,
    `xscompel`, `xselastot`, `xsnonel` -- and the run-scoped `sfactor` it writes; or raises
    `_Unsupported` (the kernel's refusal; its sfactor writes are idempotent, so the full `binary`
    then redoes them to the same values).

    TALYS: binary.f90:1 (binary)
    Test: tests/hf/test_engine_c.py
    """
    from types import SimpleNamespace

    from physics.hf.emission import emit_nx2 as E
    from physics.hf.emission.binary import PARDIS, _pi

    kern = E._kernel()
    if kern is None or not E.enabled() or torch.is_grad_enabled():
        raise _Unsupported("binary kernel")
    tn = torch.from_numpy
    nj = inp.numj
    k0, lt = inp.k0, inp.ltarget
    pops, pexs, x0s, discs = {}, {}, {}, {}
    for t in sorted(inp.grids):
        g = inp.grids[t]
        nmax = g.maxex
        nl = min(g.nlast, nmax)
        pop = inp.xspop_mb[t].numpy().copy()
        pex = inp.xspopex_mb[t].numpy().copy()
        dd = inp.xsdirdisc_mb[t].numpy()
        sfglobal = state.get(g.zix, g.nix, nj).numpy()
        sfac = sfglobal[: nmax + 1].copy()
        ppx = inp.preeqpopex_mb[t].numpy().copy()
        do_pe = inp.flagpreeq and nmax - nl > 0 and inp.pespinmodel <= 2
        if not E._binary_type_c(kern, pop, pex, dd, g, ppx, sfglobal, sfac, nl, nmax,
                                inp.maxjph + 1, do_pe, inp.pespinmodel,
                                inp.popeps_mb / max(5 * nmax, 1), PARDIS):
            raise _Unsupported("binary kernel refused")
        x0 = pex[: nl + 1].copy()
        disc = x0.copy()
        if t == k0 and lt <= nl:
            disc[lt] = 0.0
        pops[t], pexs[t], x0s[t], discs[t] = pop, pex, x0, disc
    ltok = k0 in x0s and lt < x0s[k0].shape[0]
    xscompel = tn(x0s[k0])[lt] if ltok else torch.zeros((), dtype=DTYPE)
    if ltok:
        pexs[k0][lt] = 0.0  # `feedbinary` and `xspopex` hold the same values: one array
        pops[k0][lt, inp.targetspin2 // 2, _pi(inp.target_parity)] = 0.0
    xspopex = {t: tn(v) for t, v in pexs.items()}
    return SimpleNamespace(
        xspop_mb={t: tn(v) for t, v in pops.items()}, xspopex_mb=xspopex, feedbinary_mb=xspopex,
        xsdisc_mb={t: tn(v) for t, v in discs.items()}, xscompel_mb=xscompel,
        xselastot_mb=inp.xselasinc_mb + xscompel,
        xsnonel_mb=torch.clamp(inp.xsreacinc_mb - xscompel, min=0.0))


def _bin_decay_kw():
    from physics.hf import engine

    return engine._bin_decay, engine._seed_mulpre


def cases(zf, stats: dict | None = None):
    """`engine.ChainedFull.cases` for the dump-free chain (`inject=()`), with `cascade` above in
    place of `populations` + `multiple_emission` wherever it applies, and the energy's exclusive
    channels with it (CENGBOOK: `_Packed.channels` in C, else `built.channels` +
    `exclusive_channels`, one channel state through the ascending loop either way). Returns, per
    kept energy, `(BinaryInputs, _Chan, binary result)`; `run` reuses that `binary` result.

    TALYS: talysreaction.f90:1 (talysreaction)
    Test: tests/hf/test_engine_c.py
    """
    from dataclasses import replace

    from physics.hf.compound.chain import compound_inputs
    from physics.hf.compound.norm_reference import addends
    from physics.hf.compound.population import population
    from physics.hf.compound.target import binary_cross_sections, compound_target_inputs
    from physics.hf.emission.binary import BinaryState, binary
    from physics.hf.emission.feed_reference import etotal_of, pop_inputs_of
    from physics.hf.emission.feeding import Cascade
    from physics.hf.emission.multiple import multiple_emission
    from physics.hf.engine import _BuiltInputs
    from physics.hf.fission.chain import fission_chain
    from physics.hf.preeq.chain import lend_cascade, set_energy_subset, target_tag

    _bin_decay, _seed_mulpre = _bin_decay_kw()
    if zf.inject or zf.run_dir is not None and zf.declared_energies is None:
        raise ValueError("engine_c runs the dump-free chain with declared_energies")
    stats = stats if stats is not None else {}
    target = target_tag(zf.Z, zf.A)
    declared = tuple(float(np.float32(e)) for e in zf.declared_energies)
    enincmax = max(declared)
    want = None if zf.energies is None else {round(e, 6) for e in zf.energies}
    run_axis = list(declared)
    keep = [want is None or round(e, 6) in want for e in run_axis]
    n_run = max((i + 1 for i, k in enumerate(keep) if k), default=0)
    run_axis, keep = run_axis[:n_run], keep[:n_run]
    cas = zf.cascade
    if cas is None:
        cas = Cascade(zf.Z, zf.A, enincmax, energies=declared)
    elif (int(cas.Zt), int(cas.At), float(cas.enincmax), tuple(cas.energies)) != (
            zf.Z, zf.A, float(enincmax), tuple(declared)):
        raise ValueError("ChainedFull(cascade=...) was built for another run")
    cas.set_fit_params(zf.params)
    trim = zf.trim_batches
    fis = fission_chain(zf.Z, zf.A, cas.options, fit=cas.fit + cas.fission_fit)
    set_energy_subset(zf.Z, zf.A, declared, run_axis if trim else None)
    lend_cascade(cas)
    rn = _Run(cas) if lib() is not None else None
    chst = _ChanState()
    keys = None
    try:
        add = addends(target, zf.Z, zf.A, run_axis, declared, fit=cas.fit)
        built = _BuiltInputs(cas, target, declared, add)
        out = []
        bstate = BinaryState()
        for nin in range(1, n_run + 1):
            binp, cinp = built.shell(nin, run_axis[nin - 1])
            etot = etotal_of(zf.Z, zf.A, enincmax, binp.e_inc_mev, binp.k0)
            inc = cas.incident(binp.e_inc_mev)
            st = cas.new_energy(etot, lmaxinc=int(inc.lmax[0]), e_inc_mev=binp.e_inc_mev)
            cas.propagate_exmax(st, 0, 0)
            fkw = {}
            if fis is not None and cinp.flagfission:
                cn = cas.spec(st, 0, 0)
                fkw = fis.compound_target(int(cn.Z), int(cn.A), etot, fnorm=float(cas.fiso()[0]))
            a_e = add[round(binp.e_inc_mev, 6)]
            got = None
            if rn is not None:
                try:
                    got = front(rn, st, binp, cinp, etot, a_e, fkw)
                    stats["front_c"] = stats.get("front_c", 0) + 1
                except _Unsupported as ex:
                    stats.setdefault("front_fallback", []).append((binp.e_inc_mev, str(ex)))
            if got is not None:
                pop, ci = got
            else:
                ci = compound_inputs(cas, st, binp, cinp, etot, a_e, **fkw)
                pop = compound_target_inputs(ci)
            xsb = binary_cross_sections(pop, [ci])[0]
            p = pop.pop_mb[0]
            xspop, xspopex, xspopnuc = {}, {}, {}
            for t, g in binp.grids.items():
                n = g.ex_mev.shape[0]
                xspop[t] = p[t, :n].clone()
                xspopex[t] = xspop[t].sum((-2, -1))
                xspopnuc[t] = float(xspop[t].sum())
            xsbinary = binp.xsbinary_mb.clone() if binp.xsbinary_mb is not None else None
            if xsbinary is not None:
                for t in range(7):
                    xsbinary[t + 1] = xsb[t]
                if fis is not None and cinp.flagfission:
                    xsbinary[0] = pop.xs_fission_mb[0]
            prq = (population(pop_inputs_of(cas, binp, target, etot, add, declared))
                   if keep[nin - 1] else None)
            pex = {}
            for t, g in binp.grids.items():
                n = g.ex_mev.shape[0]
                col = prq.preeqpopex_mb.get(t) if prq is not None else None
                v = torch.zeros(n, dtype=DTYPE)
                if col is not None:
                    k = min(n, len(col))
                    v[:k] = torch.as_tensor(col[:k], dtype=DTYPE)
                pex[t] = v
            extra = {"xscompcont_mb": {
                t: float(xspop[t][binp.grids[t].nlast + 1:].sum()) for t in xspop}}
            b2 = replace(binp, xspop_mb=xspop, xspopex_mb=xspopex, xspopnuc_mb=xspopnuc,
                         xsbinary_mb=xsbinary, preeqpopex_mb=pex, **extra,
                         xsreacinc_mb=float(inc.sigma_reac_mb[0]),
                         xsdirdiscsum_mb=a_e["xsdirdiscsum_mb"],
                         xspreeqsum_mb=a_e["xspreeqsum_mb"], xsgrsum_mb=a_e["xsgrsum_mb"])
            b = None
            if rn is not None and keep[nin - 1]:
                try:
                    b = binary_lean(b2, bstate)
                except _Unsupported as ex:
                    stats.setdefault("binary_fallback", []).append((binp.e_inc_mev, str(ex)))
            if b is None:
                b = binary(b2, bstate)
            if not keep[nin - 1]:
                continue
            seed = {t: (b.xspop_mb[t].detach().numpy(), b.xspopex_mb[t].detach().numpy(),
                        float(b.xspop_mb[t].sum())) for t in b.xspop_mb}
            xsb_by_type = ({t - 1: float(v) for t, v in enumerate(xsbinary)}
                           if xsbinary is not None else {})
            mres = packed = chan = None
            if keys is None:
                keys = _Keys(cas, cinp)
            if rn is not None:
                try:
                    packed = cascade(rn, st, cinp.maxz, cinp.maxn, seed, binp.popeps_mb, binp.k0,
                                     float(inc.sigma_reac_mb[0]), xsb_by_type, b.feedbinary_mb,
                                     cinp.flagfission, fis if cinp.flagfission else None, prq)
                    stats["c"] = stats.get("c", 0) + 1
                except _Unsupported as ex:
                    stats.setdefault("fallback", []).append((binp.e_inc_mev, str(ex)))
            if packed is not None:
                try:
                    chan = packed.channels(cinp, b, xsbinary, chst, keys)
                    stats["channels_c"] = stats.get("channels_c", 0) + 1
                except _Unsupported as ex:
                    stats.setdefault("channels_fallback", []).append((binp.e_inc_mev, str(ex)))
                    mres = packed.result()
            if packed is None:
                nuclei = cas.populations(st, cinp.maxz, cinp.maxn, seed)
                for zc in range(cinp.maxz + 1):
                    for nc in range(cinp.maxn + 1):
                        if (zc, nc) in nuclei:
                            cas.propagate_exmax(st, zc, nc)
                nuclei = cas.populations(st, cinp.maxz, cinp.maxn, seed)
                _seed_mulpre(nuclei, prq)
                decay = _bin_decay(cas, st, nuclei, binp.popeps_mb,
                                   fis if cinp.flagfission else None)
                mpe_cb = None
                if any(n.mulpre for n in nuclei.values()):
                    def mpe_cb(zc, nc, nex, cas=cas, st=st, nuclei=nuclei, etot=etot):
                        return cas.mpe(st, nuclei, zc, nc, nex, etotal_mev=etot)

                    mpe_cb.context = (cas, st, nuclei, etot)
                mres = multiple_emission(
                    nuclei, decay,
                    popeps_mb=binp.popeps_mb, maxz=cinp.maxz, maxn=cinp.maxn, k0=binp.k0,
                    xsreacinc_mb=float(inc.sigma_reac_mb[0]), xsbinary_mb=xsb_by_type,
                    feedbinary_mb=b.feedbinary_mb, flagfission=cinp.flagfission,
                    mpe=mpe_cb)
            if chan is None:
                from physics.hf.emission.channels import exclusive_channels

                py = chst.to_py()
                chan = _Chan.of(exclusive_channels(built.channels(cinp, st, mres, b, xsbinary), py))
                chst.from_py(py)
            out.append((b2, chan, b, keys))
        return out
    finally:
        set_energy_subset(zf.Z, zf.A, declared, None)


def run(injection, stats: dict | None = None):
    """`engine.run(injection=ChainedFull(...))` for the dump-free chain, through `cases`.

    TALYS: talysreaction.f90:1 (talysreaction)
    Test: tests/hf/test_engine_c.py
    """
    from physics.hf import engine
    from physics.hf.emission.binary import BinaryState, binary
    from physics.hf.results import Results

    if lib() is None or injection.inject:
        return engine.run(injection=injection)
    per_case = cases(injection, stats)
    e_inc, chans, levels, resid, totals = [], [], [], [], []
    reuse = os.environ.get("HF_ENGINE_C_REBINARY", "0") != "1"
    bstate = None if reuse else BinaryState()
    PARSYM = engine.PARSYM
    for binp, ch, b0, keys in per_case:
        e_inc.append(binp.e_inc_mev)
        b = b0 if reuse else binary(binp, bstate)
        xsch = ch.xschannel_mb
        chans.append(keys.chans(xsch))
        levels.append(keys.levels(binp.k0, b.xsdisc_mb))
        resid.append(ch.residual)
        # totalxs.f90's xsexclusive: the one-particle channel of each ejectile (parskip off)
        excl = {t: xsch.get(0 if t == 0 else 10 ** (6 - t), 0.0) for t in keys.live_t}
        totals.append({
            "elastic": float(b.xselastot_mb), "nonelastic": float(b.xsnonel_mb),
            "total": float(b.xselastot_mb + b.xsnonel_mb),
            "reaction": binp.xsreacinc_mb, "compound_elastic": float(b.xscompel_mb),
            "fission": ch.xsfistot_mb, "residual_production": ch.xsresprod_mb,
            **{f"{PARSYM[binp.k0]}{PARSYM[t]}": v for t, v in excl.items()},
        })
    res = Results(
        e_inc_mev=torch.tensor(e_inc, dtype=DTYPE),
        channels_mb=_stack(chans), levels_mb=_stack(levels),
        residual_production_mb=_stack(resid), totals_mb=_stack(totals),
        injected=injection.families,
    )
    # DIRECTCAP: direct radiative capture (racap), off unless INCOGNITA_DIRECT_CAPTURE is set
    from physics.hf.direct.racapcalc import add_to_results

    return add_to_results(res, injection)


def _stack(per_case: list[dict[str, float]]) -> dict[str, torch.Tensor]:
    """`engine._stack` as one (keys, cases) tensor split into its rows."""
    keys = sorted(set().union(*per_case))
    if not per_case or not keys:
        return {k: torch.zeros(len(per_case), dtype=DTYPE) for k in keys}
    table = torch.tensor([[d.get(k, 0.0) for d in per_case] for k in keys], dtype=DTYPE)
    return dict(zip(keys, table.unbind(0)))  # noqa: B905
