"""SPEEDT3: every compiled kernel (physics/hf/native) is bit-identical to the Python path
it replaces.

Run on each machine that builds the kernels (`scripts/build_native.sh`) before trusting them there;
without a build every test here skips and the port runs the Python path.
"""

from __future__ import annotations

import os
import platform

import numpy as np
import pytest
import torch

from physics.hf import native
from physics.hf.omp import schrodinger as S

pytestmark = [
    pytest.mark.skipif(not native.available(), reason="physics/hf/native not built"),
    # CCFAST2: the kernels build on arm64 too (scalar paths, libm hypot, Accelerate through torch),
    # but "bit-identical to torch" is a statement about torch's x86 kernels (fused multiply-adds,
    # MKL at one thread); on the Mac they are held to the closeness rule instead
    # (docs/results/hf-speed-profile.md, "Coupled channels without bit-identity").
    pytest.mark.skipif(platform.machine().lower() not in ("x86_64", "amd64"),
                       reason="bitwise against torch's x86 kernels only"),
]


@pytest.fixture(autouse=True)
def _one_thread():
    prev = torch.get_num_threads()
    torch.set_num_threads(1)
    yield
    torch.set_num_threads(prev)


def _python(fn, *args, **kw):
    """`fn` with the compiled kernels switched off."""
    old = os.environ.get("HF_NATIVE")
    os.environ["HF_NATIVE"] = "0"
    try:
        return fn(*args, **kw)
    finally:
        if old is None:
            del os.environ["HF_NATIVE"]
        else:
            os.environ["HF_NATIVE"] = old


def _bits(a) -> np.ndarray:
    a = a.numpy() if isinstance(a, torch.Tensor) else np.asarray(a)
    if np.iscomplexobj(a):
        a = np.ascontiguousarray(a).view(np.float64)
    return np.ascontiguousarray(a, dtype=np.float64).view(np.uint64)


def _same(a, b) -> bool:
    return np.array_equal(_bits(a), _bits(b))


def _complex(rng, shape, scale=1.0):
    return torch.from_numpy(rng.normal(size=shape) * scale + 1j * rng.normal(size=shape) * scale)


def test_switch():
    assert _python(native.available) is False
    assert native.available() is True


@pytest.mark.parametrize("groups", [0, 1, 3, 40])
def test_numerov_inward(groups):
    rng = np.random.default_rng(groups)
    m = 25_000 if groups else 2_000
    ee = rng.uniform(0.05, 40.0, m)
    ra = rng.uniform(0.5, 30.0, m)
    rb = np.maximum(ra, 2.0 * ee + 20.0) + rng.uniform(0.0, 2.0, m)
    n = (rng.choice(rng.integers(200, 1_500, max(groups, 1)), m) if groups
         else rng.integers(200, 1_500, m))
    gb = rng.uniform(1e-3, 50.0, m)
    gb1 = gb * rng.uniform(0.9, 1.1, m)
    ref = _python(S._numerov_inward_many, ee, ra, rb, gb, gb1, n)
    got = S._numerov_inward_many(ee, ra, rb, gb, gb1, n)
    assert all(_same(x, y) for x, y in zip(ref, got, strict=True))


def test_cf1():
    rng = np.random.default_rng(7)
    m = 100_000
    eta = np.where(rng.random(m) < 0.2, 0.0, rng.uniform(0.0, 60.0, m))
    rho = rng.uniform(0.05, 90.0, m)
    lmax = 30
    lcol = rng.integers(0, lmax + 1, m)
    ltop = lcol + rho.astype(np.int64) + 60
    ref = _python(S._cf1_many, eta, rho, lmax, ltop, lcol)
    got = S._cf1_many(eta, rho, lmax, ltop, lcol)
    assert _same(ref[1], got[1])
    # orders above a column's own ltop are never written (and never read)
    ok = np.arange(lmax + 1)[None, :] <= lcol[:, None]
    assert _same(ref[0][ok], got[0][ok])


def test_coulomb_functions_many():
    rng = np.random.default_rng(8)
    etas = [torch.from_numpy(rng.uniform(0.0, 25.0, k)) for k in (1, 17, 60)]
    etas[1][:3] = 0.0
    rhos = [torch.from_numpy(rng.uniform(0.5, 40.0, k)) for k in (1, 17, 60)]
    ref = _python(S.coulomb_functions_many, etas, rhos, [5, 20, 33])
    got = S.coulomb_functions_many(etas, rhos, [5, 20, 33])
    for a, b in zip(ref, got, strict=True):
        assert all(_same(x, y) for x, y in zip(a, b, strict=True))


def _x_reference(pieces):
    """`_ecis_setup`'s no-grad x from the pieces `native.ecis_job` takes."""
    so, central, coul, ls2, L, kh, mhh = pieces
    nmax = so.shape[1]
    n_idx = torch.arange(1, nmax + 1, dtype=torch.float64)
    g = so[:, None, None, :] * ls2[None, :, :, None].to(so.dtype)
    g.add_(central[:, None, None, :]).add_(coul[:, None, None, :])
    g.mul_(mhh[:, None, None, None])
    ab = (kh[:, None, None, None] - (L * (L + 1))[None, :, None, None]
          / (n_idx[None, None, None, :] ** 2))
    torch.sub(ab, g, out=g)
    gg = g * g
    return torch.sub(g, gg.div_(12.0), out=gg)


def _radial_reference(x, ism, nmax):
    """The radial loop of `_integrate_ecis_many` for one job (its Python branch, verbatim)."""
    shape = x.shape[:3]
    u_prev = torch.zeros(shape, dtype=torch.complex128)
    u_cur = torch.ones(shape, dtype=torch.complex128)
    u_am = torch.zeros(shape, dtype=torch.complex128)
    u_ap = torch.zeros(shape, dtype=torch.complex128)
    cap_m = {int(v) - 1: torch.nonzero(ism == v).flatten() for v in torch.unique(ism)}
    cap_p = {int(v) + 1: torch.nonzero(ism == v).flatten() for v in torch.unique(ism)}
    ism_m1, ism_p1 = (ism - 1)[:, None, None], (ism + 1)[:, None, None]
    for n in range(1, nmax + 1):
        u_next = 2.0 * u_cur - u_prev - x[..., n - 1] * u_cur
        idx = cap_m.get(n)
        if idx is not None:
            u_am[idx] = u_cur[idx]
        idx = cap_p.get(n + 1)
        if idx is not None:
            u_ap[idx] = u_next[idx]
        u_prev, u_cur = u_cur, u_next
        if n % 25 == 0:
            s = u_cur.abs().clamp_min(1.0e-300)
            u_prev, u_cur = u_prev / s, u_cur / s
            u_am = torch.where(ism_m1 <= n, u_am / s, u_am)
            u_ap = torch.where(ism_p1 <= n + 1, u_ap / s, u_ap)
    return u_am, u_ap


@pytest.mark.skipif(not native.vhypot(), reason="torch's vector hypot not found")
@pytest.mark.parametrize("shape", [(1, 1, 1, 30), (3, 5, 2, 77), (7, 21, 3, 101), (13, 41, 2, 160)])
def test_ecis_job(shape):
    n_e, n_l, n_j, nmax = shape
    rng = np.random.default_rng(sum(shape))
    so = _complex(rng, (n_e, nmax), 0.3)
    central = _complex(rng, (n_e, nmax), 40.0)
    coul = torch.from_numpy(rng.uniform(0.0, 15.0, (n_e, nmax)))
    L = torch.arange(n_l, dtype=torch.float64)
    ls2 = torch.from_numpy(rng.choice([-2.0, 0.0, 1.0, 2.0], (n_l, n_j)))
    h = torch.from_numpy(rng.uniform(0.05, 0.2, n_e))
    kh = torch.from_numpy(rng.uniform(0.1, 3.0, n_e)) * h * h
    mhh = torch.from_numpy(rng.uniform(0.02, 0.05, n_e)) * h * h
    ism = torch.from_numpy(rng.integers(4, nmax, n_e))
    pieces = (so, central, coul, ls2, L, kh, mhh)
    ref = _radial_reference(_x_reference(pieces), ism, int(ism.max()) + 1)
    got = native.ecis_job(pieces, ism, int(ism.max()) + 1)
    assert all(_same(a, b) for a, b in zip(ref, got, strict=True))


@pytest.mark.skipif(not native.vhypot(), reason="torch's vector hypot not found")
@pytest.mark.parametrize("particle", [1, 2, 6])
def test_solve_spherical_many(particle):
    """The whole `_integrate_ecis_many` (set-up, kernels, Coulomb functions, matching) on real
    optical-model parameters."""
    from physics.hf.omp.parameters import OMPParameters

    rng = np.random.default_rng(particle)
    e = torch.from_numpy(np.sort(rng.uniform(0.01, 25.0, 24)))
    fields = dict(v_mev=50.0, rv_fm=1.2, av_fm=0.65, w_mev=2.0, rw_fm=1.25, aw_fm=0.6,
                  vd_mev=0.0, rvd_fm=1.28, avd_fm=0.55, wd_mev=6.0, rwd_fm=1.28, awd_fm=0.55,
                  vso_mev=6.0, rvso_fm=1.1, avso_fm=0.59, wso_mev=-0.1, rwso_fm=1.1, awso_fm=0.59,
                  rc_fm=1.3)
    p = OMPParameters(**{k: torch.full((24,), v, dtype=torch.float64) for k, v in fields.items()})
    specs = [(p, 40, 90, particle, e, None, None)]
    ref = _python(S.solve_spherical_many, specs)[0]
    got = S.solve_spherical_many(specs)[0]
    for f in ("tjl", "sigma_reac_mb", "sigma_tot_mb", "sigma_shape_el_mb", "lmax"):
        assert _same(getattr(ref, f), getattr(got, f)), f


def _numerov_blocks_reference(mmat, nmat, u1, h, nmatch):
    from physics.hf.ecis.solver import _numerov_blocks

    mm = mmat.transpose(0, 1)[:, None].contiguous()
    nm = nmat.transpose(0, 1)[:, None].contiguous() if nmat is not None else None
    keep = _numerov_blocks(mm, nm, u1[None].contiguous(), h, nmatch)
    return {k: v[0] for k, v in keep.items()}


@pytest.mark.skipif(not native.lapack_symbols(), reason="torch's MKL symbols not found")
@pytest.mark.parametrize("n", [1, 3, 7, 8, 13, 24])
@pytest.mark.parametrize("n_e", [1, 3])
@pytest.mark.parametrize("deformed", [False, True])
def test_cc_block(n, n_e, deformed):
    from physics.hf.ecis.solver import _fd_weights

    rng = np.random.default_rng(100 * n + 10 * n_e + deformed)
    nmatch = torch.from_numpy(rng.integers(12, 40, n_e))
    n_r = int(nmatch.max()) + 3
    h = torch.from_numpy(rng.uniform(0.08, 0.15, n_e))
    r = h[:, None] * torch.arange(1, n_r + 1, dtype=torch.float64)[None, :]
    cent = torch.from_numpy(rng.integers(0, 8, n).astype(np.float64))
    diag = (cent * (cent + 1))[None, None, :] / r[:, :, None] ** 2 - 1.5
    mmat = _complex(rng, (n_e, n_r, n, n), 0.5) + torch.diag_embed(diag.to(torch.complex128))
    nmat = _complex(rng, (n_e, n_r, n, n), 0.05) if deformed else None
    l_pow = torch.from_numpy(rng.integers(0, 6, n).astype(np.float64))
    u1 = torch.diag_embed(h[:, None] ** (l_pow + 1.0)[None, :]).to(torch.complex128)
    ref = _numerov_blocks_reference(mmat, nmat, u1, h, nmatch)
    got = native.cc_block(mmat, nmat, u1, h, nmatch, _fd_weights)
    for k in ref:
        assert bool(torch.isfinite(ref[k]).all()), k
        assert _same(ref[k], got[k]), k


def test_coupling_tables_batch_invariant():
    """SPEEDT3's batched 6j symbols and the global dcgs table give the per-multipole values."""
    from physics.hf.ecis import coupling as C

    spins = torch.tensor([3.5, 4.5, 5.5, 6.5], dtype=torch.float64)
    for twoJ in (1, 7, 31):
        lev, orb, jj = C.channel_list(twoJ, 1, spins, torch.ones(4, dtype=torch.int64), 20, 0.5)
        n = lev.numel()
        jr, jc = jj[:, None], jj[None, :]
        ir, ic = spins[lev][:, None], spins[lev][None, :]
        lam = C._t(C.LAMBDAS)
        tj2 = C._t(0.5 * twoJ).expand(n, n)
        batched = C.sixj(jc, lam[1:, None, None].expand(-1, n, n), jr, ir, tj2, ic)
        for k in range(1, lam.numel()):
            one = C.sixj(jc, C._t(float(lam[k])).expand(n, n), jr, ir, tj2, ic)
            assert _same(batched[k - 1], one)
            jvals, inv = torch.unique(jj, sorted=True, return_inverse=True)
            ref = C._dcgs_table(float(lam[k]), tuple(jvals.tolist()))[inv[:, None], inv[None, :]]
            assert _same(C._dcgs_lookup(float(lam[k]), jj), ref)
