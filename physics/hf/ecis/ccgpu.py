"""SPEED50 CCGPU: the coupled-channels radial loops of a nuclide, integrated on a GPU ahead of time.

The incident coupled-channels solve (`incident_coupled` -> `sum_blocks`) is ~45 % of a batch of
rotational nuclides, all of it in `ccfast.c`'s radial loop, one (J, parity) block and one core at a
time. This module moves that loop to the GPU and OFF the critical path:

  * `plan(Z, A, energies)` replays the target's `direct.chain._coupled` call with
    `solver._PLAN` set, so each `_sum_blocks_tasks` side only RECORDS its inputs (channels, form
    factors, kinematics, grid). For every energy row it takes the blocks of total J up to
    `k R_match + I + J_MARGIN` (the observed last J is <= k R + I + 5 on the bench nuclides; a block
    beyond the bound is simply not precomputed), and enqueues their radial loops on the GPU,
    asynchronously. Nothing is solved on the CPU and nothing is cached as a result.
  * The real run of the target, later, reaches `solver.run_cc_tasks`, which asks `lookup(ch, sub)`
    for each block: when every row of the block was precomputed, the GPU's matching-point
    logarithmic derivative L = U' U^-1 comes back as an equivalent `keep` (u_m = 1,
    u_{m+1} = 2 h L, the rest 0: `cc_match_acc` then reads exactly L) and only the C matching runs.
    Anything else -- a J beyond the bound, a row the plan never saw, a different input -- misses
    and runs `ccfast.c` as before. The J loop, its convergence test and its order of addition are
    untouched.

Keys are VALUE hashes of everything the radial loop reads (the block's channels and couplings;
each row's form factors, kinematics, step, matching index and radii up to its matching point), so a
hit is the same integration, never a neighbour's.

The GPU recurrence is `ccfast.c`'s: the modified Numerov step below `soswitch` (`cc_block_mn`) and
the implicit derivative-coupling step above it (`cc_block_d`, CCBLOCKD arm 1), same grid, same
matching point. It differs in three places, none of which is a physics change:
  * channels are padded to the largest block of a bucket with DECOUPLED dummy channels (zero
    potential and coupling); M is block diagonal, so the real channels never see them;
  * the stabilisation every `STAB` steps multiplies by u_i^-1 (one batched LU solve; u_i <- 1)
    instead of a Householder QR -- any invertible right factor spans the same solutions and L is
    invariant under it (ccfast.c point 4); batched QR is ~20x slower on the GPU;
  * cuBLAS's summation order. Summed over J per energy the cross sections and T_lj agree with the C
    kernel to ~1e-12; end to end every engine output is within 3e-12 of the CPU path on
    120 nuclides (scripts/speed50_compare.py, see incognita/bench/speed).

Enable with `HF_CCGPU=1` (off by default); `HF_CCGPU_DEVICE` picks the device (`cpu` runs the same
batched recurrence without a GPU, for tests).

TALYS: ecist.f:20513 (resu) -- the radial loop ECIS runs per (J, parity), as ccfast.c
Test: scripts/speed50_compare.py (engine_curves outputs, HF_CCGPU=1 against the CPU path)
"""
from __future__ import annotations

import hashlib
import os
import time

import torch
from torch import Tensor

from physics.hf.core.tensors import DTYPE

STAB = 15  # ccnative.STABILISE_EVERY
J_MARGIN = 6.0  # total J planned per row: k R_match + I_target + J_MARGIN
BUCKET_RATIO = 0.4  # a block joins the bucket of a larger one while N >= BUCKET_RATIO * Nmax:
# few buckets (each is a whole radial loop of launches) at the price of padded products

_DEV: torch.device | None = None
_TRIED = False
_STORE: dict = {}  # (block hash, row hash) -> (_Side, p)
_BLOCK_HASH: dict = {}  # id(ch) -> (ch, hash)
STATS = {"hit": 0, "miss": 0, "pairs": 0}


def device() -> torch.device | None:
    """The device CCGPU runs on, or None (`HF_CCGPU` unset/0, or no CUDA)."""
    global _DEV, _TRIED
    if _TRIED:
        return _DEV
    _TRIED = True
    if os.environ.get("HF_CCGPU", "0") == "0":
        return None
    want = os.environ.get("HF_CCGPU_DEVICE", "cuda")
    if want == "cpu":
        _DEV = torch.device("cpu")
        return _DEV
    try:
        if torch.cuda.is_available():
            _DEV = torch.device(want)
    except Exception:  # noqa: BLE001
        _DEV = None
    return _DEV


def _fused() -> bool:
    """SPEED50B: `HF_CCGPU_FUSED=1` runs each bucket as one fused CUDA kernel (ccfused.py)."""
    return os.environ.get("HF_CCGPU_FUSED", "0") == "1"


def active() -> bool:
    return bool(_STORE)


def clear() -> None:
    _STORE.clear()
    _BLOCK_HASH.clear()


_LAUNCHER = None


def _launch(side) -> None:
    """Hand `side` to the launcher thread (CUDA: its host work then overlaps the engine's), or run
    it here (CPU device)."""
    global _LAUNCHER
    if side.dev.type != "cuda" or os.environ.get("HF_CCGPU_THREAD", "1") == "0":
        side.run()
        return
    if _LAUNCHER is None:
        import atexit

        _LAUNCHER = _Launcher()
        atexit.register(shutdown)
    _LAUNCHER.put(side)


def shutdown() -> None:
    """Stop the launcher thread (a daemon thread still inside CUDA at interpreter exit aborts the
    process)."""
    global _LAUNCHER
    if _LAUNCHER is not None:
        _LAUNCHER.stop()
        _LAUNCHER = None


class _Launcher:
    """One daemon thread that enqueues the sides' device work in order. torch releases the GIL
    inside its operators and the thread sleeps (never spins) while the device queue is full, so the
    engine keeps the core; what the thread does cost is counted in the process's CPU time."""

    def __init__(self):
        import queue
        import threading

        self.q = queue.Queue()
        self.t = threading.Thread(target=self._loop, name="ccgpu", daemon=True)
        self.t.start()

    def put(self, side) -> None:
        self.q.put(side)

    def stop(self) -> None:
        self.q.put(None)
        self.t.join()

    def _loop(self) -> None:
        while True:
            side = self.q.get()
            if side is None:
                if self.t is not None and torch.cuda.is_initialized():
                    torch.cuda.synchronize()
                return
            try:
                side.run()
            except Exception as exc:  # noqa: BLE001 -- the side's pairs then miss
                side.failed = exc
            finally:
                side.launched.set()


def forget(Z: int, A: int) -> None:
    """Drop what was planned for (Z, A) once its run is over (memory)."""
    _CHANNELS_OF.pop((Z, A), None)
    for k in [k for k, v in _STORE.items() if v[0].target == (Z, A)]:
        del _STORE[k]
    if not _STORE:
        _BLOCK_HASH.clear()


# ----------------------------------------------------------------------------------- keys

def _h(*ts) -> bytes:
    m = hashlib.blake2b(digest_size=16)
    for t in ts:
        if t is None:
            m.update(b"\0")
        elif isinstance(t, Tensor):
            t = t.detach()
            m.update(str(t.dtype).encode() + str(tuple(t.shape)).encode())
            m.update(t.contiguous().cpu().numpy().tobytes())
        else:
            m.update(repr(t).encode())
    return m.digest()


def _block_key(ch) -> bytes:
    got = _BLOCK_HASH.get(id(ch))
    if got is not None and got[0] is ch:
        return got[1]
    key = _h(int(ch.twoJ), int(ch.parity), ch.level, ch.l, ch.ls2, ch.coupling, ch.so_grad_coef,
             ch.so_r2_coef, ch.so_deriv_coef)
    _BLOCK_HASH[id(ch)] = (ch, key)
    return key


def _row_keys(ff, kin, h: Tensor, nmatch: Tensor, r: Tensor) -> list[bytes]:
    """One key per energy row: everything the radial loop and the matching read, up to the row's
    own matching point (+2 radial points, the last the loop builds M at)."""
    out = []
    for e in range(int(h.shape[0])):
        n = int(nmatch[e]) + 3
        out.append(_h(ff.central[e, :, :n], ff.spin_orbit[e, :, :n], ff.coulomb[e, :n],
                      None if ff.so_grad is None else ff.so_grad[e, :, :n],
                      None if ff.so_r2 is None else ff.so_r2[e, :, :n], kin.kappa2[e],
                      kin.mu_coef[e], h[e], nmatch[e], r[e, :n]))
    return out


_ROWKEY_MEMO: dict = {}


def lookup(ch, sub) -> Tensor | None:
    """`solver.run_cc_tasks`'s hook: an equivalent (7, E, N, N) `keep` for block `ch` on the rows
    of `sub = (ff, kin, h, nmatch, r)` when every row was precomputed, else None."""
    ff, kin, h, nmatch, r = sub
    got = _ROWKEY_MEMO.get(id(h))
    if got is None or got[0] is not h:
        got = (h, _row_keys(ff, kin, h, nmatch, r))
        _ROWKEY_MEMO.clear()
        _ROWKEY_MEMO[id(h)] = got
    rk = got[1]
    bk = _block_key(ch)
    hits = [_STORE.get((bk, k)) for k in rk]
    if any(x is None for x in hits) or not all(side.host()[1][p] for side, p in hits):
        STATS["miss"] += 1
        return None
    STATS["hit"] += 1
    N = int(ch.level.numel())
    E = len(rk)
    # u_m = U and u_{m+1} = 2 h U' with M_{m+-1} = s_{m+-1} = u_{m-1} = 0: `cc_match_acc` forms
    # exactly (U, U') again (U's columns are already normalised to 1) and solves L = U' U^-1 itself
    keep = torch.zeros((7, E, N, N), dtype=torch.complex128)
    for e, (side, p) in enumerate(hits):
        uu = side.host()[0][p]
        keep[1, e] = uu[0, :N, :N]
        keep[2, e] = (2.0 * float(h[e])) * uu[1, :N, :N]
    return keep


# ------------------------------------------------------------------------------- planning

class _Recorder:
    """`solver._PLAN` during `plan`: keeps each side's inputs."""

    def __init__(self):
        self.sides = []

    def __call__(self, make_channels, ff, kin, h, nmatch, r, target_spin, two_j0, j_cap):
        self.sides.append((make_channels, ff, kin, h, nmatch, r, float(target_spin), int(two_j0),
                           int(j_cap)))


def plan(Z: int, A: int, energies: tuple[float, ...], k0: int = 1) -> int:
    """Record target (Z, A)'s coupled-channels sides as `direct.chain._coupled` would solve them and
    enqueue their radial loops on the device. Returns the number of (block, row) pairs enqueued
    (0: no device, no coupled channels, or everything already solved)."""
    if device() is None:
        return 0
    from physics.hf.ecis import solver
    from physics.hf.ecis.incident import incident_coupled, njmax_incident
    from physics.hf.ecis.reference import coupled_band
    from physics.hf.input.defaults import default_options
    from physics.hf.omp.schrodinger import PARMASS_AMU
    from physics.hf.preeq.chain import energy_subset

    try:
        band = coupled_band(Z, A)
    except Exception:  # noqa: BLE001
        return 0
    if band is None or band.get("colltype") not in ("R", "V"):
        return 0
    # the arguments `direct.chain._coupled_cached` gives `incident_coupled`
    e_ax = torch.tensor(list(energies), dtype=DTYPE)
    nj = njmax_incident(A, PARMASS_AMU[k0], float(e_ax.max()))
    wanted = energy_subset(Z, A, energies)
    keep = None
    if wanted is not None:
        w = set(wanted)
        keep = torch.tensor([round(float(e), 6) in w for e in energies])
        if bool(keep.all()):
            keep = None
    rec = _Recorder()
    # SPEED50C: the `_CHANNELS` keys this target uses (hit or built), recorded by wrapping
    # `solver._channels_cached` for the planning pass (solver.py itself untouched: it keys the
    # CC disk cache's version)
    touched: set = set()
    cc_orig = solver._channels_cached

    def cc_touch(kind, twoJ, parity, spins, spin_dtype, parities, parity_dtype, extra, lmax,
                 proj_spin, ahead=()):
        base = (kind, spins, spin_dtype, parities, parity_dtype, extra, lmax, proj_spin)
        touched.add((twoJ, parity, base))
        touched.update((q[0], q[1], base) for q in ahead)
        return cc_orig(kind, twoJ, parity, spins, spin_dtype, parities, parity_dtype, extra, lmax,
                       proj_spin, ahead)

    solver._channels_cached = cc_touch
    solver._PLAN = rec
    try:
        with torch.inference_mode():
            incident_coupled(None, Z, A, e_ax, band, particle=k0, lmax=nj, energy_mask=keep,
                             options=band.get("options") or default_options(Z, A))
    except solver.Planned:
        pass
    except BaseException:
        solver._channels_cached = cc_orig
        raise
    finally:
        solver._PLAN = None
    n = 0
    try:
        with torch.inference_mode():
            for side in rec.sides:
                n += _enqueue_side((Z, A), *side)
    finally:
        solver._channels_cached = cc_orig
    # the channel sets used here are the run's own (value-keyed memo); keep them for `restore`,
    # since the previous target's `drop_target_caches` clears the memo before this target runs.
    # SPEED50C: every set the target used, not only the ones it built: sets depend on the band's
    # spins and lmax only, so an earlier target with the same band (e.g. U-238 before Sm-154)
    # built them, and the run rebuilt them after the drop (264 of 558 sets on the 20 nuclides)
    _CHANNELS_OF[(Z, A)] = {k: solver._CHANNELS[k] for k in touched if k in solver._CHANNELS}
    STATS["pairs"] += n
    return n


_CHANNELS_OF: dict = {}


def restore(Z: int, A: int) -> None:
    """Put the channel sets `plan(Z, A)` built back into `solver._CHANNELS` before (Z, A) runs."""
    from physics.hf.ecis import solver

    for k, v in _CHANNELS_OF.get((Z, A), {}).items():
        solver._CHANNELS.setdefault(k, v)


def _enqueue_side(target, make_channels, ff, kin, h, nmatch, r, target_spin, two_j0,
                  j_cap) -> int:
    """The blocks of one side up to each row's J bound, bucketed by channel count, enqueued."""
    n_e = int(h.shape[0])
    rm = h * (nmatch.to(DTYPE) + 1.0)
    jb = (kin.k_fm[:, 0].real * rm + target_spin + J_MARGIN).tolist()
    jmax = max(jb)
    pairs = []  # (twoJ, parity, rows)
    tj = two_j0
    while tj / 2.0 <= jmax and (tj - two_j0) // 2 < j_cap:
        rows = [e for e in range(n_e) if tj / 2.0 <= jb[e]]
        for par in (-1, 1):
            pairs.append((tj, par, rows))
        tj += 2
    if hasattr(make_channels, "prefill"):
        make_channels.prefill([(tj, par) for tj, par, _ in pairs])
    blocks = []
    for tj, par, rows in pairs:
        ch = make_channels(tj, par)
        if ch.level.numel() == 0 or not bool(ch.elastic.any()):
            continue
        blocks.append((ch, rows))
    if not blocks:
        return 0
    rkeys = _row_keys(ff, kin, h, nmatch, r)
    blocks.sort(key=lambda b: -int(b[0].level.numel()))
    n = 0
    while blocks:
        nmax = int(blocks[0][0].level.numel())
        cut = next((k for k, b in enumerate(blocks) if b[0].level.numel() < BUCKET_RATIO * nmax),
                   len(blocks))
        bucket, blocks = blocks[:cut], blocks[cut:]
        side = _Side(target, bucket, ff, kin, h, nmatch, r)
        _launch(side)
        for (ch, _rows), (_b, e_list) in zip(bucket, side.pairs_of_block, strict=True):
            bk = _block_key(ch)
            for e, p in e_list:
                _STORE[(bk, rkeys[e])] = (side, p)
        n += side.P
    return n


# ------------------------------------------------------------------------------ the kernel

def _fdw_rows() -> list:
    """`solver._fd_weights(npts)` real parts, npts = 3..7, as (3, npts) float lists."""
    from physics.hf.ecis.solver import _fd_weights

    return [_fd_weights(k).real.to(DTYPE).tolist() for k in range(3, 8)]


def _pad2(t: Tensor, n: int) -> Tensor:
    N = t.shape[-1]
    return t if N == n else torch.nn.functional.pad(t, (0, n - N, 0, n - N))


def _rmm(D: Tensor, B: Tensor) -> Tensor:
    """D (P, N, N) real times B (P, N, N) complex: one real bmm on the interleaved columns."""
    P, N, _ = B.shape
    br = torch.view_as_real(B).reshape(P, N, 2 * N)
    return torch.view_as_complex(torch.bmm(D, br).reshape(P, N, N, 2))


def _qr_cgs2(A: Tensor) -> tuple[Tensor, Tensor]:
    """Batched thin QR of A (P, N, N) by classical Gram-Schmidt with one re-orthogonalisation,
    column by column: only products and element-wise kernels, so nothing waits for the device
    (torch's batched QR and LU synchronise with the host on CUDA, and under WSL a synchronisation
    spins a CPU core). Returns Q, R (R upper triangular, real positive diagonal)."""
    P, N, _ = A.shape
    Q = torch.empty_like(A)
    R = torch.zeros_like(A)
    for j in range(N):
        v = A[:, :, j:j + 1]
        if j:
            Qj = Q[:, :, :j]
            r1 = torch.linalg.vecdot(Qj, v, dim=1)[:, :, None]  # Q^H v, no conjugate copy
            v = torch.baddbmm(v, Qj, r1, alpha=-1.0)
            r2 = torch.linalg.vecdot(Qj, v, dim=1)[:, :, None]
            v = torch.baddbmm(v, Qj, r2, alpha=-1.0)
            R[:, :j, j:j + 1] = r1 + r2
        nrm = torch.linalg.vector_norm(v, dim=1, keepdim=True)  # (P, 1, 1)
        R[:, j:j + 1, j:j + 1] = nrm
        Q[:, :, j:j + 1] = v / nrm
    return Q, R


def _right_tri(R: Tensor, X: Tensor) -> Tensor:
    """X R^-1 for upper-triangular R (cuBLAS trsm, asynchronous)."""
    return torch.linalg.solve_triangular(R, X, upper=True, left=False)


SWEEPS = 8  # Jacobi sweeps per implicit step (deformed side) ...
SWEEPS_START = 30  # ... and on the first steps, where the one-sided stencil's start-up weights make
# the contraction large (Sm-154: 0.22 at step 1, 0.12 at step 3, <= 0.02 from step 5 on)
BOUND_MAX = 1.0e-13  # a pair whose truncation bound rho^(sweeps+1) ever exceeds this is refused


def _jacobi(L: Tensor, W: Tensor, rho_max: Tensor, sweeps: int = SWEEPS) -> Tensor:
    """X = L^-1 W for the strongly diagonal implicit Numerov matrix L = 1 - c M - c G, by SWEEPS
    Jacobi sweeps X <- D^-1 W - (D^-1 O) X (ccfast.c `nm_solve_split`, NATIVEX2 ccx): products
    only. The contraction rho = max_a sum_b |O_ab| / |D_a| (|Re| + |Im|, as ccfast.c) of every pair
    raised to sweeps + 1 (the truncation bound) is folded into `rho_max`, so that a pair where the
    sweeps are not converged to rounding can be refused afterwards."""
    d = torch.diagonal(L, dim1=1, dim2=2)  # (P, N)
    dinv = 1.0 / d
    off = L.real.abs() + L.imag.abs()
    rows = off.sum(dim=2) - (d.real.abs() + d.imag.abs())
    torch.maximum(rho_max, ((rows / d.abs()).amax(dim=1)) ** (sweeps + 1), out=rho_max)
    F = L * dinv[:, :, None]
    F.diagonal(dim1=1, dim2=2).zero_()
    G = W * dinv[:, :, None]
    X = G
    for _ in range(sweeps):
        X = torch.baddbmm(G, F, X, alpha=-1.0)
    return X


class _Side:
    """One bucket of blocks of one side: (block, row) pairs P, padded to Np channels, integrated on
    the device when `run()` is called (asynchronously on CUDA); `host()` waits and returns L
    (P, Np, Np).

    Launch economy (the loop is host-bound otherwise): M(r) is built CHUNK radial points at a time
    in one batched product per chunk, already scaled per row by the step constant the recurrence
    multiplies it with, so a modified-Numerov step is two products and two element-wise kernels."""

    CHUNK = 8

    def __init__(self, target, bucket, ff, kin, h, nmatch, r):
        dev = device()
        self.dev, self.target = dev, target
        Ns = [int(ch.level.numel()) for ch, _ in bucket]
        Np = max(Ns)
        self.Np = Np
        self.deformed = ff.so_r2 is not None and bucket[0][0].so_deriv_coef is not None
        n_e, R = int(h.shape[0]), int(r.shape[1])
        pb, pe, self.pairs_of_block = [], [], []
        for b, (_ch, rows) in enumerate(bucket):
            lst = []
            for e in rows:
                lst.append((e, len(pb)))
                pb.append(b)
                pe.append(e)
            self.pairs_of_block.append((b, lst))
        self.P = len(pb)
        nm = nmatch[torch.tensor(pe)].tolist()
        self.nmax = max(nm)
        if self.nmax + 2 >= R:
            raise ValueError("radial axis shorter than a matching point needs")
        self._in = (bucket, Ns, ff, kin, h, r, pb, pe, nm, n_e)
        self._host = None
        self.failed = None
        import threading

        self.launched = threading.Event()
        self._pending: list = []

    def _throttle(self, depth: int = 3) -> None:
        """Keep at most `depth` recorded steps outstanding on the device, waiting by polling: a
        full device queue would otherwise block the launching thread in the driver, spinning."""
        if self.dev.type != "cuda":
            return
        ev = torch.cuda.Event()
        ev.record()
        self._pending.append(ev)
        while len(self._pending) > depth:
            first = self._pending[0]
            while not first.query():
                time.sleep(0.0002)
            self._pending.pop(0)

    def run(self) -> None:
        """Move the inputs to the device and enqueue the whole integration."""
        with torch.inference_mode():
            self._run()
        self._pending = []

    def _run(self) -> None:
        bucket, Ns, ff, kin, h, r, pb, pe, nm, n_e = self._in
        self._in = None
        dev, Np, P = self.dev, self.Np, self.P
        if dev.type == "cuda" and _fused():
            # SPEED50B CCFUSED: the whole loop of every pair in one kernel launch
            from physics.hf.ecis import ccfused

            # sides on a small pool of streams, so that one side's tail (a few long pairs on a
            # few SMs) overlaps the next side's launch
            with torch.cuda.stream(ccfused.stream(dev)):
                ccfused.run(self, bucket, Ns, ff, kin, h, r, pb, pe, nm, self.deformed)
                self._to_host()
            return
        f = dict(device=dev)
        pb_t = torch.tensor(pb, dtype=torch.int64)
        pe_t = torch.tensor(pe, dtype=torch.int64)
        mu = kin.mu_coef.to(DTYPE)
        hh = h.to(DTYPE)
        cst = (hh * hh / 12.0)  # (E,) the Numerov constant c of each row
        # per-pair row data, radial axis cut to what the loop reads
        Rn = self.nmax + 2
        self.nlam = nl = int(ff.central.shape[1])
        cen = ff.central[:, :, :Rn].to(torch.complex128) * mu[:, None, None]
        so0 = ff.spin_orbit[:, 0, :Rn].to(torch.complex128) * mu[:, None]
        cou = ff.coulomb[:, :Rn].to(DTYPE) * mu[:, None]
        ir2 = 1.0 / r[:, :Rn].to(DTYPE) ** 2
        mats_of = []
        ll, ls2, kap, mask, u1 = [], [], [], [], []
        k2 = kin.kappa2.to(DTYPE)
        for (ch, _rows), N in zip(bucket, Ns, strict=True):
            mats = [ch.coupling.to(DTYPE)]
            if self.deformed:
                mats += [ch.so_grad_coef.to(DTYPE), ch.so_r2_coef.to(DTYPE),
                         ch.so_deriv_coef.to(DTYPE)]
            mats_of.append(_pad2(torch.cat(mats, 0), Np).reshape(len(mats) * nl, Np * Np))
            lf = ch.l.to(DTYPE)
            ll.append(torch.nn.functional.pad(lf * (lf + 1.0), (0, Np - N)))
            ls2.append(torch.nn.functional.pad(ch.ls2.to(DTYPE), (0, Np - N)))
            kap.append(torch.nn.functional.pad(k2[:, ch.level], (0, Np - N)))
            m = torch.zeros(Np, dtype=DTYPE)
            m[:N] = 1.0
            mask.append(m)
            ue = torch.zeros((n_e, Np), dtype=DTYPE)
            ue[:, :N] = hh[:, None] ** (lf + 1.0)[None, :]
            ue[:, N:] = hh[:, None]
            u1.append(ue)
        Sb = torch.stack(mats_of).to(**f)  # (Bk, k NLAM, Np^2)
        self.SP = Sb.index_select(0, pb_t.to(dev))  # (P, k NLAM, Np^2)
        pe_d = pe_t.to(dev)
        self.cenP = cen.to(**f).index_select(0, pe_d)  # (P, NLAM, Rn) complex
        self.so0P = so0.to(**f).index_select(0, pe_d)  # (P, Rn) complex
        self.couP = cou.to(**f).index_select(0, pe_d)  # (P, Rn)
        self.ir2P = ir2.to(**f).index_select(0, pe_d)  # (P, Rn)
        if self.deformed:
            self.gP = (ff.so_grad.real[:, :, :Rn].to(DTYPE) * mu[:, None, None]).to(**f) \
                .index_select(0, pe_d)
            self.qP = (ff.so_r2.real[:, :, :Rn].to(DTYPE) * mu[:, None, None]).to(**f) \
                .index_select(0, pe_d)
        self.llP = torch.stack(ll)[pb_t].to(**f)  # (P, Np)
        self.ls2P = torch.stack(ls2)[pb_t].to(**f)
        self.kapP = torch.stack(kap)[pb_t, pe_t].to(**f)
        self.maskP = torch.stack(mask)[pb_t].to(**f)
        u1d = torch.diag_embed(torch.stack(u1)[pb_t, pe_t]).to(torch.complex128).to(**f)
        self.eye = torch.eye(Np, dtype=torch.complex128, device=dev)
        self.cP = cst[pe_t].to(**f)  # (P,)
        self.hP = hh[pe_t].to(**f)
        at: dict[int, list[int]] = {}
        for p, v in enumerate(nm):
            at.setdefault(int(v), []).append(p)
        self.at = {k: torch.tensor(v, dtype=torch.int64, device=dev) for k, v in at.items()}
        # per pair at its matching point: U = u_m and U' (both column-normalised, cc_match_acc's)
        self.UU = torch.zeros((P, 2, Np, Np), dtype=torch.complex128, device=dev)
        self.rho = torch.zeros(P, dtype=DTYPE, device=dev)
        self._chunk0 = -1
        if self.deformed:
            self._run_deformed(u1d)
        else:
            self._run_modnum(u1d)
        self.SP = self.cenP = self.so0P = self.couP = self.ir2P = None
        self.llP = self.ls2P = self.kapP = self.maskP = self._Mc = self._NHc = None
        self.gP = self.qP = None
        if dev.type == "cuda":
            self._to_host()

    def _to_host(self) -> None:
        """Queue the device -> pinned host copy of UU and rho, and the event `host()` polls."""
        if True:
            self._buf = torch.empty(self.UU.shape, dtype=self.UU.dtype, pin_memory=True)
            self._buf.copy_(self.UU, non_blocking=True)
            self._rbuf = torch.empty(self.rho.shape, dtype=self.rho.dtype, pin_memory=True)
            self._rbuf.copy_(self.rho, non_blocking=True)
            self._event = torch.cuda.Event()
            self._event.record()
            self.UU = self.rho = None

    def done(self) -> bool:
        return self._host is not None or (self.dev.type == "cuda" and hasattr(self, "_event")
                                          and self._event.query())

    def host(self) -> tuple[Tensor, Tensor]:
        """(UU (P, 2, Np, Np), ok (P,) bool) on the host, waiting for the device by polling (an
        event wait spins a core under WSL, even a blocking one)."""
        if self._host is None:
            if self.dev.type == "cuda":
                while not self.launched.wait(0.001):
                    pass
                if self.failed is not None:
                    self._host = (None, torch.zeros(self.P, dtype=torch.bool))
                    return self._host
                while not self._event.query():
                    time.sleep(0.0005)
                uu, rho = self._buf, self._rbuf
                perm = getattr(self, "perm", None)
                if perm is not None:  # SPEED50C CCFUSED: launch order -> the caller's pair order
                    uu, rho = uu.index_select(0, perm), rho.index_select(0, perm)
            else:
                uu, rho = self.UU, self.rho
            ok = torch.isfinite(torch.view_as_real(uu)).reshape(uu.shape[0], -1).all(dim=1) \
                & (rho <= BOUND_MAX)
            self._host = (uu, ok)
        return self._host

    def _chunk(self, lo: int) -> None:
        """M(r_i) (unscaled) for i in [lo, lo + CHUNK + 2), and NH(r_i) when deformed."""
        P, Np = self.P, self.Np
        hi = min(lo + self.CHUNK + 2, self.cenP.shape[2])
        K = hi - lo
        c = self.cenP[:, :, lo:hi].transpose(1, 2)  # (P, K, NLAM) complex
        if self.deformed:
            g = self.gP[:, :, lo:hi].transpose(1, 2)
            q = self.qP[:, :, lo:hi].transpose(1, 2)
            z = torch.zeros_like(g)
            coef = torch.cat([torch.cat([c.real, g, q, z], 2), torch.cat([c.imag, z, z, z], 2),
                              torch.cat([z, z, z, q], 2)], 1)  # (P, 3K, 4 NLAM)
        else:
            coef = torch.cat([c.real, c.imag], 1)  # (P, 2K, NLAM)
        out = torch.bmm(coef, self.SP).reshape(P, -1, K, Np, Np)
        M = torch.complex(out[:, 0], out[:, 1])  # (P, K, Np, Np)
        dg = (self.llP[:, None, :] * self.ir2P[:, lo:hi, None] - self.kapP[:, None, :]
              + self.couP[:, lo:hi, None]) * self.maskP[:, None, :]
        so = self.so0P[:, lo:hi, None] * self.ls2P[:, None, :]
        M.diagonal(dim1=2, dim2=3).add_(torch.complex(dg + so.real, so.imag))
        self._Mc = M
        self._NHc = out[:, 2] if self.deformed else None
        self._lo, self._hi = lo, hi

    def window(self, i: int) -> None:
        """Make M (and NH) at i - 1, i and i + 1 available (one chunk build per CHUNK steps)."""
        if self._chunk0 < 0 or not (self._lo <= max(i - 1, 0) and i + 1 < self._hi):
            self._chunk0 = 0
            self._chunk(max(i - 1, 0))

    def M(self, i: int) -> Tensor:
        return self._Mc[:, i - self._lo]

    def NH(self, i: int) -> Tensor:
        return self._NHc[:, i - self._lo]

    def _match(self, idx: Tensor, ummb, umb, umpb, mmmb, mmpb, spb, smb) -> None:
        """`cc_match_acc`'s L = U' U^-1 for the pairs `idx` (column-normalised U, U')."""
        cc = self.cP.index_select(0, idx)[:, None, None]
        he = self.hP.index_select(0, idx)[:, None, None]
        ddp1 = torch.bmm(mmpb, umpb)
        ddm1 = torch.bmm(mmmb, ummb)
        if spb is not None:
            ddp1 = ddp1 + spb
        if smb is not None:
            ddm1 = ddm1 + smb
        du = ((umpb - 2.0 * cc * ddp1) - (ummb - 2.0 * cc * ddm1)) / (2.0 * he)
        cn = umb.abs().amax(dim=1, keepdim=True).clamp_min(1.0e-300)
        self.UU.index_copy_(0, idx, torch.stack([umb / cn, du / cn], 1))

    def _run_modnum(self, u1: Tensor) -> None:
        """`ccfast.c::cc_block_mn`: u_{i+1} = 2 u_i - u_{i-1} + h^2 M_i u_i + (h^4/12) M_i^2 u_i,
        as y = h^2 M u_i, u_{i+1} = (y + 2 u_i - u_{i-1}) + (h^2 M) y / 12 (c12 = h^2)."""
        c12 = (12.0 * self.cP)[:, None, None]
        uc = u1
        up = torch.zeros_like(uc)
        for i in range(self.nmax + 1):
            self.window(i)
            Mi = self.M(i)
            Ms = Mi * c12  # h^2 M_i
            y = torch.bmm(Ms, uc)
            t = torch.add(y, uc, alpha=2.0).sub_(up)
            un = torch.baddbmm(t, Ms, y, alpha=1.0 / 12.0)
            if i % 2 == 1:
                self._throttle()
            idx = self.at.get(i)
            if idx is not None:
                s = lambda t_, ix=idx: t_.index_select(0, ix)  # noqa: E731
                self._match(idx, s(up), s(uc), s(un), s(self.M(i - 1) if i > 0 else Mi),
                            s(self.M(i + 1)), None, None)
            if i == self.nmax:
                break
            up, uc = uc, un
            if i % STAB == STAB - 1:
                uc, R = _qr_cgs2(uc)
                up = _right_tri(R, up)

    def _run_deformed(self, u1: Tensor) -> None:
        """`ccfast.c::cc_block_d` (CCBLOCKD arm 1): the implicit Numerov step with r du/dr on the
        one-sided 7-point stencil, M_i u_i formed, one solve per step."""
        fdw = _fdw_rows()
        c = self.cP.to(torch.complex128)[:, None, None]
        cr = self.cP[:, None, None]
        hist: list[Tensor] = [u1]
        mu_p = None
        # the stencil weights of every step, on the device once (a per-step host -> device copy
        # would wait for the device)
        w_host = torch.zeros((self.nmax + 1, 3, 6), dtype=DTYPE)
        for i in range(self.nmax + 1):
            npts = min(i + 3, 7)
            w = fdw[npts - 3]
            fac = (i + 2.0, 10.0 * (i + 1.0), float(i) if i else 0.0)
            for k in range(3):
                for m in range(1, npts):
                    w_host[i, k, m - 1] = fac[k] * w[k][m]
        w_all = w_host.to(self.dev)
        for i in range(self.nmax + 1):
            use_m1 = i != 0
            npts = min(i + 3, 7)
            w = fdw[npts - 3]
            top = min(npts - 1, len(hist))
            fac = (i + 2.0, 10.0 * (i + 1.0), float(i) if use_m1 else 0.0)
            self.window(i)
            Mc, NHc = self.M(i), self.NH(i)
            Mn, NHn = self.M(i + 1), self.NH(i + 1)
            if use_m1:
                Mp, NHp = self.M(i - 1), self.NH(i - 1)
            else:
                Mp, NHp = Mc, NHc
            nh3 = (NHn, NHc, NHp)
            uc = hist[0]
            # v_k = fac_k sum_m w[k, m] u_{i+1-m}, the three at once: (3, top) x (top, P N N)
            wm = w_all[i, :, :top]
            hs = torch.view_as_real(torch.stack(hist[:top])).reshape(top, -1)
            V = torch.view_as_complex(torch.mm(wm, hs).reshape(3, *uc.shape, 2))
            ps = [None if fac[k] == 0.0 else _rmm(nh3[k], V[k]) for k in range(3)]
            mu_c = torch.bmm(Mc, uc)
            rhs = 2.0 * uc + (10.0 * c) * mu_c
            if use_m1:
                up = hist[1]
                if mu_p is None:
                    mu_p = torch.bmm(Mp, up)
                rhs.sub_(up).add_(c * mu_p)
            psum = None
            for k in range(3):
                if ps[k] is not None:
                    psum = ps[k].clone() if psum is None else psum.add_(ps[k])
            rhs.add_(c * psum)
            G = None
            for k in range(3):
                f = fac[k] * w[k][0]
                if f == 0.0:
                    continue
                G = nh3[k] * f if G is None else G.add_(nh3[k], alpha=f)
            L = torch.sub(self.eye, Mn * c)
            if G is not None:
                L.sub_(G * cr)
            un = _jacobi(L, rhs, self.rho, SWEEPS_START if i < 5 else SWEEPS)
            self._throttle()
            idx = self.at.get(i)
            if idx is not None:
                s = lambda t_, ix=idx: t_.index_select(0, ix)  # noqa: E731
                s3 = [None, None, None]
                for k in (0, 2):
                    if fac[k] != 0.0:
                        s3[k] = (fac[k] * w[k][0]) * _rmm(s(nh3[k]), s(un)) + s(ps[k])
                umm1 = s(hist[1]) if len(hist) > 1 else torch.zeros_like(s(uc))
                self._match(idx, umm1, s(uc), s(un), s(Mp if use_m1 else Mc), s(Mn), s3[0], s3[2])
            if i == self.nmax:
                break
            hist = [un] + hist[:5]
            mu_p = mu_c
            if i % STAB == STAB - 1:
                Q, R = _qr_cgs2(hist[0])
                hist = [Q] + [_right_tri(R, x) for x in hist[1:]]
                mu_p = _right_tri(R, mu_p)


__all__ = ["STATS", "active", "clear", "device", "forget", "lookup", "plan", "restore", "shutdown"]
