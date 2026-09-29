"""SPEED50B CCFUSED: `ccgpu._Side`'s radial loops as one fused CUDA kernel per bucket.

CCGPU (SPEED50) enqueued each radial step as a handful of batched torch operations: tens of
thousands of small launches per nuclide, whose host cost was close to the C kernel's own. Here the
whole loop of every (block, energy row) pair -- M(r) build, step, stabilisation, matching -- is one
kernel launch per bucket (`ccfused.cu`), compiled at run time by NVRTC through torch (no nvcc on
these boxes), the PTX cached on disk.

Differences from `ccgpu._run_*` (none is a physics change):
  * no padding: each pair runs at its own channel count;
  * the deformed side's implicit system is solved by Gauss-Jordan with partial pivoting (exact to
    rounding) instead of Jacobi sweeps, so no pair is refused on a truncation bound;
  * summation order.

Opt-in: `HF_CCGPU=1 HF_CCGPU_FUSED=1`. `HF_CCFUSED_FP32=1` compiles the propagation in float32
(the mixed-precision experiment; see SPEED50B.md for whether it passes the accuracy rule).

Test: scripts/speed50b_fused_check.py (fused vs torch CCGPU vs ccfast.c per block),
scripts/speed50_compare.py (engine outputs).
"""
from __future__ import annotations

import ctypes
from functools import lru_cache
import hashlib
import os
from pathlib import Path

import torch

from physics.hf.core.tensors import DTYPE

_SRC = Path(__file__).with_name("ccfused.cu")
_KERN: dict = {}
THREADS = int(os.environ.get("HF_CCFUSED_THREADS", "128"))
BLOCKS_PER_SM = int(os.environ.get("HF_CCFUSED_BPSM", "4"))
SLOTS = {"cc_modnum": 8, "cc_deformed": 25}
# nominal FLOPs queued (complex product 8 N^3, real x complex 4 N^3, Gauss-Jordan with N right-hand
# sides ~12 N^3, per radial step; stabilisations not counted), for the throughput figure
STATS = {"flops": 0.0, "pairs": 0, "launches": 0}


_STREAMS: list = []
_NEXT = [0]
N_STREAMS = int(os.environ.get("HF_CCFUSED_STREAMS", "4"))


def stream(dev):
    """The next stream of the pool (round robin)."""
    if not _STREAMS:
        _STREAMS.extend(torch.cuda.Stream(device=dev) for _ in range(max(1, N_STREAMS)))
    s = _STREAMS[_NEXT[0] % len(_STREAMS)]
    _NEXT[0] += 1
    return s


def enabled() -> bool:
    return os.environ.get("HF_CCGPU_FUSED", "0") == "1"


def fp32() -> bool:
    return os.environ.get("HF_CCFUSED_FP32", "0") == "1"


def _kernel(name: str):
    key = (name, fp32())
    k = _KERN.get(key)
    if k is not None:
        return k
    from torch.cuda._utils import _cuda_load_module, _nvrtc_compile

    src = _SRC.read_text()
    opts = ["-DREAL_FLOAT"] if fp32() else []
    cc = "%d%d" % torch.cuda.get_device_capability()
    tag = hashlib.sha256((src + repr(opts) + cc + name + torch.__version__).encode()).hexdigest()[:24]
    cache = Path(os.environ.get("HF_CCFUSED_CACHE", os.path.expanduser("~/.cache/ccfused")))
    ptx_path = cache / f"{tag}.ptx"
    mangled_path = cache / f"{tag}.name"
    if ptx_path.is_file() and mangled_path.is_file():
        ptx, mangled = ptx_path.read_bytes(), mangled_path.read_text()
    else:
        # torch's NVRTC helper wants CUDA_HOME/include; with no toolkit installed, the headers
        # of the pip `nvidia-cuda-runtime` wheel torch depends on are enough
        from torch.utils import cpp_extension

        if cpp_extension.CUDA_HOME is None:
            import nvidia.cuda_runtime as _rt

            cpp_extension.CUDA_HOME = str(Path(list(_rt.__path__)[0]))
        ptx, mangled = _nvrtc_compile(src, name, cc, None, opts + ["-std=c++17"])
        cache.mkdir(parents=True, exist_ok=True)
        tmp = ptx_path.with_suffix(".tmp")
        tmp.write_bytes(ptx if isinstance(ptx, bytes) else ptx.encode())
        tmp.replace(ptx_path)
        mangled_path.write_text(mangled)
    mod = _cuda_load_module(ptx, [mangled])
    k = mod[mangled] if isinstance(mod, dict) else getattr(mod, mangled)
    _KERN[key] = k
    return k


class _Args(ctypes.Structure):
    _fields_ = [("P", ctypes.c_int), ("nlam", ctypes.c_int), ("Rn", ctypes.c_int),
                ("Np", ctypes.c_int)] + \
        [(n, ctypes.c_void_p) for n in ("pb", "pe", "nm", "bN", "pOff", "bOffS", "bOffV", "S",
                                        "ll", "ls2", "kapP", "u1P", "cen", "so0", "cou", "ir2",
                                        "g", "qq", "cst", "hh", "WW", "ws")] + \
        [("wsPer", ctypes.c_longlong), ("UU", ctypes.c_void_p), ("rho", ctypes.c_void_p)]


@lru_cache(maxsize=None)
def _ww(nmax: int) -> torch.Tensor:
    """The deformed side's derivative weights per matching point (a pure function of nmax)."""
    from physics.hf.ecis.ccgpu import _fdw_rows

    fdw = _fdw_rows()
    WW = torch.zeros((nmax + 1, 3, 7), dtype=DTYPE)
    for i in range(nmax + 1):
        npts = min(i + 3, 7)
        w = fdw[npts - 3]
        fac = (i + 2.0, 10.0 * (i + 1.0), float(i) if i else 0.0)
        top = min(npts - 1, i + 1, 6)
        for k in range(3):
            if fac[k] == 0.0:
                continue
            WW[i, k, 0] = fac[k] * w[k][0]
            for m in range(1, top + 1):
                WW[i, k, m] = fac[k] * w[k][m]
    return WW


def run(side, bucket, Ns, ff, kin, h, r, pb, pe, nm, deformed: bool) -> None:
    """Integrate every pair of `side` in one launch; sets side.UU (P, 2, Np, Np) complex128 and
    side.rho (P,) on the device (rho = inf: the pair failed and will miss)."""
    dev = side.dev
    rdt = torch.float32 if fp32() else DTYPE
    cdt = torch.complex64 if fp32() else torch.complex128
    P, Np = side.P, side.Np
    nmax = max(nm)
    Rn = nmax + 2
    mu = kin.mu_coef.to(DTYPE)
    hh = h.to(DTYPE)
    cst = hh * hh / 12.0
    nl = int(ff.central.shape[1])
    keep: list = []  # device tensors the launch reads

    def D(t, dt=None):
        # SPEED50C: through pinned memory, non-blocking. A pageable host->device copy syncs the
        # stream first, so every input copy of this side waited (spinning a core under WSL) for
        # the kernel queued before it on the same stream. torch's host allocator keeps the pinned
        # block alive until the copy has run.
        t = t.contiguous()
        if dt is not None and t.dtype != dt:
            t = t.to(dtype=dt)
        if t.device.type == "cpu" and dev.type == "cuda":
            t = t.pin_memory().to(device=dev, non_blocking=True)
        else:
            t = t.to(device=dev)
        keep.append(t)
        return t

    cen = D(ff.central[:, :, :Rn].to(torch.complex128) * mu[:, None, None], cdt)
    so0 = D(ff.spin_orbit[:, 0, :Rn].to(torch.complex128) * mu[:, None], cdt)
    cou = D(ff.coulomb[:, :Rn].to(DTYPE) * mu[:, None], rdt)
    ir2 = D(1.0 / r[:, :Rn].to(DTYPE) ** 2, rdt)
    if deformed:
        g = D(ff.so_grad.real[:, :, :Rn].to(DTYPE) * mu[:, None, None], rdt)
        qq = D(ff.so_r2.real[:, :, :Rn].to(DTYPE) * mu[:, None, None], rdt)
    else:
        g = qq = cou  # unread
    k2 = kin.kappa2.to(DTYPE)
    S_parts, ll_parts, ls2_parts, bN, offS, offV = [], [], [], [], [], []
    os_, ov = 0, 0
    for (ch, _rows), N in zip(bucket, Ns, strict=True):
        mats = [ch.coupling.to(DTYPE)]
        if deformed:
            mats += [ch.so_grad_coef.to(DTYPE), ch.so_r2_coef.to(DTYPE),
                     ch.so_deriv_coef.to(DTYPE)]
        s = torch.cat(mats, 0).reshape(-1)
        S_parts.append(s)
        offS.append(os_)
        os_ += s.numel()
        lf = ch.l.to(DTYPE)
        ll_parts.append(lf * (lf + 1.0))
        ls2_parts.append(ch.ls2.to(DTYPE))
        offV.append(ov)
        ov += N
        bN.append(N)
    kap_parts, u1_parts, pOff = [], [], []
    op = 0
    for b, e in zip(pb, pe, strict=True):
        ch = bucket[b][0]
        kap_parts.append(k2[e, ch.level])
        lf = ch.l.to(DTYPE)
        u1_parts.append(hh[e] ** (lf + 1.0))
        pOff.append(op)
        op += Ns[b]
    S = D(torch.cat(S_parts), rdt)
    llv = D(torch.cat(ll_parts), rdt)
    ls2v = D(torch.cat(ls2_parts), rdt)
    kapP = D(torch.cat(kap_parts), rdt)
    u1P = D(torch.cat(u1_parts), rdt)
    I32 = torch.int32
    # longest pairs first (static round-robin over thread blocks)
    order = sorted(range(P), key=lambda p: -(Ns[pb[p]] ** 3) * (nm[p] + 1))
    pb_t = D(torch.tensor([pb[p] for p in order], dtype=I32))
    pe_t = D(torch.tensor([pe[p] for p in order], dtype=I32))
    nm_t = D(torch.tensor([nm[p] for p in order], dtype=I32))
    pOff_t = D(torch.tensor([pOff[p] for p in order], dtype=I32))
    bN_t = D(torch.tensor(bN, dtype=I32))
    offS_t = D(torch.tensor(offS, dtype=torch.int64))
    offV_t = D(torch.tensor(offV, dtype=I32))
    cst_d = D(cst, rdt)
    hh_d = D(hh, rdt)
    if deformed:
        WW_d = D(_ww(nmax), rdt)
    else:
        WW_d = cst_d
    name = "cc_deformed" if deformed else "cc_modnum"
    per = 32.0 if deformed else 16.0
    STATS["flops"] += sum(per * Ns[pb[p]] ** 3 * (nm[p] + 1) for p in range(P))
    STATS["pairs"] += P
    STATS["launches"] += 1
    sm = torch.cuda.get_device_properties(dev).multi_processor_count
    G = min(P, sm * BLOCKS_PER_SM)
    wsPer = SLOTS[name] * Np * Np
    ws = torch.empty(G * wsPer * 2, dtype=rdt, device=dev)
    keep.append(ws)
    UU = torch.zeros((P, 2, Np, Np), dtype=torch.complex128, device=dev)
    rho = torch.zeros((P,), dtype=DTYPE, device=dev)  # the kernel sets inf on a failed pair
    a = _Args(P, nl, Rn, Np, *[t.data_ptr() for t in (
        pb_t, pe_t, nm_t, bN_t, pOff_t, offS_t, offV_t, S, llv, ls2v, kapP, u1P, cen, so0, cou,
        ir2, g, qq, cst_d, hh_d, WW_d, ws)], wsPer, UU.data_ptr(), rho.data_ptr())
    raw = torch.frombuffer(bytearray(bytes(a)), dtype=torch.uint8)
    argt = D(raw)
    # back to the caller's pair order. SPEED50C: the permutation goes to the device BEFORE the
    # launch: a pageable host->device copy queued behind the kernel blocked this (launcher) thread
    # until the kernel finished, spinning a core under WSL (2.4 CPU-s over the 20-nuclide batch)
    _kernel(name)(grid=(G, 1, 1), block=(THREADS, 1, 1), args=[argt])
    # back to the caller's pair order: on the host, once the results are there (`_Side.host`).
    # SPEED50C: two device gathers after the launch cost the launcher thread ~0.3 CPU-s a batch
    inv = torch.empty(P, dtype=torch.int64)
    inv[torch.tensor(order, dtype=torch.int64)] = torch.arange(P)
    side.UU = UU
    side.rho = rho
    side.perm = inv
    # `keep` is dropped here: the caching allocator reuses its memory only for work queued after
    # this launch on the same stream
