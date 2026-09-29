"""The WKB fission path (`fismodel` 5 and 6, the TALYS default): the HFB deformation-energy
curve, its parabola fits and the momentum integrals that give the barrier penetrabilities.

Ported from TALYS-2.x (https://github.com/arjankoning1/talys), MIT License,
Copyright (c) A.J. Koning. See physics/hf/NOTICE-TALYS.md.

Task: T11 (physics/hf/CONTRACT.md §7). Acceptance test: A-fis (§6).

TALYS routines ported here (file:line of the subroutine/function statement):
    wkb.f90:1 (wkb)
    wkb.f90:212 (wkbfis)
    wkb.f90:445 (Vdef)
    wkb.f90:505 (rmiudef)
    wkb.f90:534 (FindIntersect)
    wkb.f90:613 (Find_Extrem)
    twkbint.f90:1 (twkbint)
    twkbtransint.f90:1 (twkbtransint)
    twkbphaseint.f90:1 (twkbphaseint)

`wkbfunctions.f` is fixed-form Fortran 77 without `subroutine`/`function` statements the
contract test can anchor, so its four routines are named in the docstrings that use them:
`Fmoment` (wkbfunctions.f:1), `GaussLegendre41` (wkbfunctions.f:33), `ParabFit`
(wkbfunctions.f:135) and `WPLFT` (wkbfunctions.f:185).

Two notes on faithfulness.

* `ParabFit` calls `WPLFT`, a standardised-variable formulation of an unweighted
  least-squares fit of ``y = a1 + a2 x + a3 x^2``. :func:`parab_fit` solves the same normal
  equations directly (`torch.linalg.lstsq`), which is the same estimator, so that the fitted
  half-width stays differentiable in the path energies. Only ``a3`` reaches the physics: the
  barrier *height* TALYS uses is the tabulated ``vfis`` at the extremum, not the fitted ``a1``
  (wkb.f90:122).
* TALYS runs the whole WKB path in `real(sgl)`. This port is float64 (contract §4.1), so the
  penetrabilities differ from TALYS at the single-precision floor; `docs/results/hf-sgl-floor.md`
  Result 4 measures how far that moves a per-barrier T(J,pi).
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import torch
from torch import Tensor

from physics.hf.core.constants import nuclide_symbol, talys_constants
from physics.hf.core.numerics import locate, pol1
from physics.hf.core.tensors import DTYPE
from physics.hf.structure.files import talys_structure_dir

NUMBAR = 3  # A0_talys_mod.f90:36
NUMBETA = 200  # A0_talys_mod.f90:76


def _t(x, device=None) -> Tensor:
    return torch.as_tensor(x, dtype=DTYPE, device=device)


# ----------------------------------------------------------------------------- deformation path


@dataclass(frozen=True)
class FissionPath:
    """The deformation-energy curve of one nucleus, as `fissionpar.f90:245-305` leaves it.

    `betafis`, `vfis` [MeV] and `rmiufis` are 1-based with a dummy element 0, exactly as the
    Fortran arrays. `iiextr[k]` is the path index of the k-th extremum (odd k = barrier, even
    k = well), with `iiextr[0] = 1` and `iiextr[nextr + 1] = nbeta`.
    """

    Z: int
    A: int
    nbeta: int
    betafis: Tensor  # (nbeta + 1,)
    vfis_mev: Tensor  # (nbeta + 1,)
    rmiufis: Tensor  # (nbeta + 1,)
    nextr: int
    iiextr: tuple[int, ...]  # (nextr + 2,)


def hfbpath_file(Z: int, fismodel: int) -> Path:
    """Path of the HFB fission-path file TALYS reads for `fismodel` 5 or 6.

    TALYS: fissionpar.f90:248-250
    Test: A-fis
    """
    sub = "hfbpath" if fismodel == 5 else "hfbpath_bskg3"
    return talys_structure_dir() / "fission" / sub / f"{nuclide_symbol(Z)}.fis"


def _blocks(path: Path, fismodel: int):
    """Yield (A, nbeta, rows) for every nuclide block of an `<Sym>.fis` file.

    TALYS reads these with ``read(2,'(/11x,i4,12x,i4//)')`` (fismodel 5) or ``'(/11x,i5,12x,i4//)'``
    (fismodel 6) and then `nbeta` free-format rows (fissionpar.f90:254-293).
    """
    lines = path.read_text().splitlines()
    i = 0
    awidth = 4 if fismodel == 5 else 5
    while i + 3 < len(lines):
        head = lines[i + 1].ljust(40)
        ia = int(head[11 : 11 + awidth])
        nbeta = int(head[11 + awidth + 12 : 11 + awidth + 12 + 4])
        rows = lines[i + 4 : i + 4 + nbeta]
        yield ia, nbeta, rows
        i += 4 + nbeta


_PARSED: dict[tuple[str, int], tuple] = {}


def _parsed_blocks(path: str, fismodel: int) -> tuple:
    """CENGFIS: `_blocks` of one `<Sym>.fis` file with its rows' numbers read (as `read_hfbpath`
    reads them, float32), once per file per process instead of once per nucleus: `(A, nbeta,
    rows)` with rows `(beta2, V)` (fismodel 5) or `(beta2, V, MI_ATD, IP)` (fismodel 6). A plain
    dict, not an `lru_cache`, so `chartrun.drop_target_caches` keeps it: the result is a pure
    function of a structure-database file."""
    got = _PARSED.get((path, fismodel))
    if got is not None:
        return got
    f32 = np.float32
    out = []
    for ia, nbeta, rows in _blocks(Path(path), fismodel):
        if fismodel == 5:
            parsed = tuple((float(f32(line[0:10])), float(f32(line[30:40]))) for line in rows)
        else:
            parsed = []
            for line in rows:
                tok = line.split()
                parsed.append((float(f32(tok[0])), float(f32(tok[3])), float(f32(tok[4])),
                               int(tok[5])))
            parsed = tuple(parsed)
        out.append((ia, nbeta, parsed))
    got = _PARSED[(path, fismodel)] = tuple(out)
    return got


def read_hfbpath(
    Z: int,
    A: int,
    fismodel: int,
    *,
    betafiscor: float = 1.0,
    betafiscoradjust: float = 1.0,
    vfiscor: float = 1.0,
    vfiscoradjust: float = 1.0,
    rmiufiscor: float = 1.0,
    rmiufiscoradjust: float = 1.0,
    Cbarrier: float = 1.0,
    device=None,
) -> FissionPath | None:
    """Read `structure/fission/hfbpath{,_bskg3}/<Sym>.fis` and build the scaled fission path.

    Returns None when the file or the nuclide block is absent, which is what makes TALYS fall
    back to `fismodelalt` (fissionpar.f90:307-316).

    For `fismodel` 6 the abscissa is the *row index*, not beta2 (fissionpar.f90:279), the
    collective mass comes from the file's `MI_ATD` column and the extrema are the rows flagged
    `IP = 1` (maximum) or `2` (minimum). For `fismodel` 5 the abscissa is beta2, the mass is
    `0.0063 A^(5/3)` and the extrema are found afterwards by :func:`find_extrem`.

    TALYS: fissionpar.f90:245-305 (fissionpar)
    Test: A-fis
    """
    path = hfbpath_file(Z, fismodel)
    if not path.exists():
        return None
    f32 = np.float32
    for ia, nbeta, parsed in _parsed_blocks(str(path), fismodel):
        if ia != A:
            continue
        beta = np.zeros(nbeta + 1, dtype=np.float64)
        vv = np.zeros(nbeta + 1, dtype=np.float64)
        rm = np.zeros(nbeta + 1, dtype=np.float64)
        nextr, iiextr = 0, [1] + [0] * (2 * NUMBAR + 1)
        for i, row in enumerate(parsed, start=1):
            if fismodel == 5:
                bb, v = row
                rmiu = float(f32(rmiufiscor * 0.0063 * A ** (5.0 / 3.0)))
                beta[i] = float(f32(betafiscoradjust * betafiscor * bb))
            else:
                bb, v, rmiu, ib = row
                beta[i] = float(f32(betafiscoradjust * betafiscor * i))
                if ib in (1, 2) and nextr <= 2 * NUMBAR - 1:
                    nextr += 1
                    iiextr[nextr] = i
            vv[i] = float(f32(Cbarrier * vfiscoradjust * vfiscor * v))
            rm[i] = float(f32(rmiufiscoradjust * rmiufiscor * rmiu))
        p = FissionPath(
            Z=Z,
            A=A,
            nbeta=nbeta,
            betafis=_t(beta, device),
            vfis_mev=_t(vv, device),
            rmiufis=_t(rm, device),
            nextr=nextr,
            iiextr=tuple(iiextr),
        )
        if fismodel == 6:
            ii = list(p.iiextr)
            ii[nextr + 1] = nbeta  # fissionpar.f90:300
            p = FissionPath(**{**p.__dict__, "iiextr": tuple(ii)})
        return p
    return None


def find_extrem(path: FissionPath, nsmooth: int = 5) -> FissionPath:
    """Locate the maxima and minima of the deformation-energy curve (`fismodel` 5).

    TALYS: wkb.f90:613 (Find_Extrem)
    Test: A-fis
    """
    v = path.vfis_mev
    n = path.nbeta
    iext, ii = 0, [1] + [0] * (2 * NUMBAR + 1)
    for j in range(2, n - nsmooth + 1):
        if float(v[j]) == float(v[j - 1]):  # wkb.f90:657, SCAMPS fix
            continue
        rng = [k for k in range(j - nsmooth, j + nsmooth + 1) if k != j and k >= 1]
        if all(float(v[k]) <= float(v[j]) for k in rng):
            iext += 1
            ii[iext] = j
        if iext == 2 * NUMBAR - 1:
            break
        if all(float(v[k]) >= float(v[j]) for k in rng):
            iext += 1
            ii[iext] = j
        if iext == 2 * NUMBAR - 1:
            break
    ii[iext + 1] = n
    return FissionPath(**{**path.__dict__, "nextr": iext, "iiextr": tuple(ii)})


# ----------------------------------------------------------------------------- parabola fit


def parab_fit(imax: int, npfit: int, rmiu: float, path: FissionPath) -> tuple[Tensor, Tensor]:
    """Half-width and height of the parabola through `2*npfit+1` path points around `imax`.

    Returns ``(height, width)`` in MeV. `width` is ``sqrt(2 |a3| / rmiu)`` with `a3` the
    quadratic coefficient of an unweighted least-squares fit of the deformation energy against
    ``beta - beta(imax)``; `height` is the fitted constant term (TALYS prints it but uses the
    tabulated `vfis(imax)` instead, wkb.f90:122).

    TALYS: wkbfunctions.f:135 (ParabFit) via wkbfunctions.f:185 (WPLFT)
    Test: A-fis
    """
    lo, hi = max(imax - npfit, 1), min(imax + npfit, path.nbeta)
    idx = torch.arange(lo, hi + 1, device=path.vfis_mev.device)
    x = path.betafis[idx] - path.betafis[imax]
    y = path.vfis_mev[idx]
    design = torch.stack([torch.ones_like(x), x, x * x], dim=1)
    a = torch.linalg.lstsq(design, y.unsqueeze(1)).solution.squeeze(1)
    width = torch.sqrt(2.0 * torch.abs(a[2]) / _t(rmiu, x.device))
    return a[0], width


# ----------------------------------------------------------------------------- momentum integrals

# Gauss-Kronrod 41-point rule (wkbfunctions.f:56-109). XGK[20] is the centre node.
_WG = (
    0.017614007139152118,
    0.040601429800386941,
    0.062672048334109064,
    0.083276741576704749,
    0.101930119817240435,
    0.118194531961518417,
    0.131688638449176627,
    0.142096109318382051,
    0.149172986472603747,
    0.152753387130725851,
)
_XGK = (
    0.998859031588277664,
    0.993128599185094925,
    0.981507877450250259,
    0.963971927277913791,
    0.940822633831754754,
    0.912234428251325906,
    0.878276811252281976,
    0.839116971822218823,
    0.795041428837551198,
    0.746331906460150793,
    0.693237656334751385,
    0.636053680726515025,
    0.575140446819710315,
    0.510867001950827098,
    0.443593175238725103,
    0.373706088715419561,
    0.301627868114913004,
    0.227785851141645078,
    0.152605465240922676,
    0.076526521133497333,
    0.0,
)
_WGK = (
    0.003073583718520531,
    0.008600269855642942,
    0.014626169256971253,
    0.020388373461266524,
    0.025882133604951159,
    0.031287306777296735,
    0.036600169758200798,
    0.041668873327973686,
    0.046434821867497674,
    0.050944573923728692,
    0.055195105348285994,
    0.059111400880639572,
    0.062653237554781168,
    0.065834597133618422,
    0.068648672928521888,
    0.071054423553440407,
    0.073030690332786675,
    0.074582875400499188,
    0.075704497684556667,
    0.076377867672080737,
    0.076600711917999656,
)


def _interp1(xs: Tensor, ys: Tensor, nbeta: int, eps: Tensor) -> Tensor:
    """TALYS's linear interpolation over the fission path (`Vdef`/`rmiudef`, wkb.f90:487-502).

    The Fortran search walks up from index 1 while ``eps > betafis(idef)``, then steps back one,
    so the bracket is ``[idef, idef+1]`` and is clamped to 1 at the bottom and to `nbeta` at the
    top (the arrays carry one element past `nbeta`).
    """
    beta = xs[1 : nbeta + 1]
    idef = torch.clamp(torch.searchsorted(beta.contiguous(), eps.contiguous(), right=True), 1, nbeta)
    ei, eip = xs[idef], xs[idef + 1]
    vi, vip = ys[idef], ys[idef + 1]
    same = ei == eip
    denom = torch.where(same, torch.ones_like(ei), eip - ei)
    return torch.where(same, vi, vi + (eps - ei) / denom * (vip - vi))


def _vdef(path: FissionPath, eps: Tensor) -> Tensor:
    """Deformation energy at `eps` by linear interpolation. TALYS: wkb.f90:445 (Vdef)."""
    return _interp1(path.betafis, path.vfis_mev, path.nbeta, eps)


def _rmiudef(path: FissionPath, eps: Tensor) -> Tensor:
    """Collective mass at `eps` by linear interpolation. TALYS: wkb.f90:505 (rmiudef)."""
    return _interp1(path.betafis, path.rmiufis, path.nbeta, eps)


def _gauss_legendre41(f, ea: Tensor, eb: Tensor) -> tuple[Tensor, Tensor]:
    """41-point Gauss-Kronrod integral of `f` over `[ea, eb]` and its 20-point error estimate.

    TALYS: wkbfunctions.f:33 (GaussLegendre41)
    """
    centr = 0.5 * (ea + eb)
    hlgth = 0.5 * (eb - ea)
    # FISSB: `f` is elementwise, so the 41 abscissae go through it in one call (the same values
    # as 41 calls); the sums below are TALYS's, term by term in its order
    absc = [hlgth * _XGK[j] for j in range(20)]
    fv = f(torch.stack([centr] + [centr - a for a in absc] + [centr + a for a in absc]))
    fm, fp = fv[1:21], fv[21:41]
    resg = torch.zeros_like(centr)
    resk = _t(_WGK[20], centr.device) * fv[0]
    for j in range(1, 11):
        jtw, jtwm1 = 2 * j - 1, 2 * j - 2  # 0-based _XGK indices for JTW, JTWM1
        fsum = fm[jtw] + fp[jtw]
        resg = resg + _WG[j - 1] * fsum
        resk = resk + _WGK[jtw] * fsum + _WGK[jtwm1] * (fm[jtwm1] + fp[jtwm1])
    return resk * hlgth, torch.abs((resk - resg) * hlgth)


def _find_intersect(path: FissionPath, uexc: float, ja: int, jb: int, iswell: bool) -> Tensor:
    """Deformation at which ``V(beta) = uexc`` between path indices `ja` and `jb`.

    TALYS: wkb.f90:534 (FindIntersect)
    """
    v = path.vfis_mev
    beta = path.betafis
    is0 = 1 if uexc - float(v[ja]) >= 0.0 else -1
    for j in range(ja, jb + 1):
        is1 = 1 if uexc - float(v[j]) >= 0.0 else -1
        if is1 == is0:
            continue
        return beta[j - 1] + (beta[j] - beta[j - 1]) * (uexc - v[j - 1]) / (v[j] - v[j - 1])
    slope = float(v[jb]) - float(v[ja])
    if iswell:
        return beta[jb] if slope >= 0 else beta[ja]
    return beta[ja] if slope >= 0 else beta[jb]


def wkbfis(
    path: FissionPath, uexcit: float, vheight: Tensor, vwidth: Tensor
) -> tuple[Tensor, Tensor, Tensor]:
    """Momentum integrals and penetrabilities of every extremum at excitation energy `uexcit`.

    Returns ``(tff, phase, tdir)``: `tff[k]` and `phase[k]` are 1-based over the `nextr`
    extrema (odd k = barrier, even k = well), `tdir` is the direct (through-all-barriers)
    transmission of the coupled system. Above a barrier top the Hill-Wheeler form is used with
    the fitted parabola; below it the phase integral of the *real* shape is integrated by
    Gauss-Kronrod between the two classical turning points.

    TALYS: wkb.f90:212 (wkbfis), integrand `Fmoment` (wkbfunctions.f:1)
    Test: A-fis
    """
    dev = path.vfis_mev.device
    pi = talys_constants()["pi"]
    n = 2 * NUMBAR
    tff = [torch.zeros((), dtype=DTYPE, device=dev) for _ in range(n + 1)]
    phase = [torch.zeros((), dtype=DTYPE, device=dev) for _ in range(n + 1)]
    tdirv = [torch.zeros((), dtype=DTYPE, device=dev) for _ in range(n + 1)]
    u = _t(uexcit, dev)

    def fmoment(eps: Tensor) -> Tensor:
        return 2.0 * torch.sqrt(_rmiudef(path, eps) / 2.0) * torch.sqrt(torch.abs(u - _vdef(path, eps)))

    for k in range(1, path.nextr + 1):
        if k % 2 == 1:  # barrier
            if uexcit >= float(vheight[k]):
                if float(vwidth[k]) > 0:
                    dmom = pi * (vheight[k] - u) / vwidth[k]
                else:
                    dmom = _t(-50.0, dev)
                phase[k] = torch.clamp(dmom, max=50.0)
                tff[k] = 1.0 / (1.0 + torch.exp(2.0 * dmom))
            else:
                epsa = _find_intersect(path, uexcit, path.iiextr[k - 1], path.iiextr[k], False)
                epsb = _find_intersect(path, uexcit, path.iiextr[k], path.iiextr[k + 1], False)
                dmom, _ = _gauss_legendre41(fmoment, epsa, epsb)
                phase[k] = torch.clamp(dmom, max=50.0)
                tff[k] = 1.0 / (1.0 + torch.exp(2.0 * phase[k]))
        else:  # well
            if uexcit > float(vheight[k]):
                epsa = _find_intersect(path, uexcit, path.iiextr[k - 1], path.iiextr[k], True)
                epsb = _find_intersect(path, uexcit, path.iiextr[k], path.iiextr[k + 1], True)
                dmom, _ = _gauss_legendre41(fmoment, epsa, epsb)
                phase[k] = torch.clamp(dmom, max=50.0)

    if path.nextr > 0:
        tdirv[path.nextr] = tff[path.nextr]
    for k in range(path.nextr - 2, 0, -2):
        dmom = (1.0 - tff[k]) * (1.0 - tdirv[k + 2])
        tdirv[k] = tff[k] * tdirv[k + 2] / (1.0 + dmom)
    return torch.stack(tff), torch.stack(phase), tdirv[1]


def _wkbfis_native(path: FissionPath, uexcs: list[float], vheight: Tensor, vwidth: Tensor):
    """NATIVEX2: `wkbfis`' (tff, tdir) at every energy of `uexcs` from `native/nx2_fis.c`, as
    numpy ((len, 2*NUMBAR+1), (len,)), or None (no build, `HF_NX2_FIS=0`, anything on a graph).

    TALYS: wkb.f90:212 (wkbfis), wkbfunctions.f:33 (GaussLegendre41)
    Test: tests/hf/test_nx2.py
    """
    from physics.hf.native import nx2

    fn = nx2.kernel("nx2_fis_wkb", [nx2.P, nx2.P, nx2.P, nx2.I64, nx2.P, nx2.I64, nx2.P, nx2.P,
                                    nx2.I64, nx2.P, nx2.DBL, nx2.P, nx2.P, nx2.P, nx2.P, nx2.P,
                                    nx2.P], lever="fis")
    arrays = (path.betafis, path.vfis_mev, path.rmiufis, vheight, vwidth)
    if fn is None or path.nextr > 2 * NUMBAR or any(t.device.type != "cpu" for t in arrays) or (
            torch.is_grad_enabled() and any(t.requires_grad for t in arrays)):
        return None
    vh, vw = (np.ascontiguousarray(t.detach().numpy(), dtype=np.float64) for t in arrays[3:])
    if path.betafis.numel() < path.nbeta + 1 or len(path.iiextr) < path.nextr + 2:
        return None
    # the path arrays padded by their last entry: `_interp1` never brackets past nbeta on the
    # paths TALYS ships (torch would raise there); the pad makes that bracket flat
    beta, vfis, rmiu = (np.ascontiguousarray(np.append(t.detach().numpy()[: path.nbeta + 1],
                                                       t.detach().numpy()[path.nbeta]),
                                             dtype=np.float64) for t in arrays[:3])
    ii = np.ascontiguousarray(path.iiextr, dtype=np.int64)
    u = np.ascontiguousarray(uexcs, dtype=np.float64)
    tff = np.zeros((u.size, 2 * NUMBAR + 1))
    phase = np.zeros_like(tff)
    tdir = np.zeros(u.size)
    xgk, wgk, wg = (np.ascontiguousarray(c, dtype=np.float64) for c in (_XGK, _WGK, _WG))
    rc = fn(nx2.ptr(beta), nx2.ptr(vfis), nx2.ptr(rmiu), path.nbeta, nx2.ptr(ii), path.nextr,
            nx2.ptr(vh), nx2.ptr(vw), u.size, nx2.ptr(u), float(talys_constants()["pi"]),
            nx2.ptr(xgk), nx2.ptr(wgk), nx2.ptr(wg), nx2.ptr(tff), nx2.ptr(phase), nx2.ptr(tdir))
    return None if rc != 0 else (tff, tdir)


# ----------------------------------------------------------------------------- driver


@dataclass(frozen=True)
class WKBResult:
    """Everything `wkb.f90` leaves behind for one nucleus.

    `uwkb_mev[i]`, `twkb[i, ibar]` (i = 0..nbinswkb, ibar = 1..nbar) is the penetrability table
    `twkbint` interpolates; `fbarrier_mev`/`fwidth_mev` are the barrier heights and curvatures
    `t1barrier` uses, 1-based with a dummy element 0.
    """

    nbar: int
    nextr: int
    fbarrier_mev: Tensor  # (NUMBAR + 1,)
    fwidth_mev: Tensor  # (NUMBAR + 1,)
    vheight_mev: Tensor  # (2*NUMBAR + 1,)
    vwidth_mev: Tensor
    vpos: Tensor
    uwkb_mev: Tensor  # (nbinswkb + 1,)
    twkb: Tensor  # (nbinswkb + 1, NUMBAR + 1)
    twkbdir: Tensor
    twkbtrans: Tensor
    twkbphase: Tensor


def wkb(
    Z: int,
    A: int,
    path: FissionPath,
    *,
    fismodel: int = 6,
    nbinswkb: int = 40,
    rmiufiscor: float = 1.0,
    bdamp: tuple[float, float] = (0.01, 0.01),
    flagfispartdamp: bool = False,
) -> WKBResult:
    """Fit the barriers of the fission path and tabulate their penetrability against energy.

    TALYS: wkb.f90:1 (wkb)
    Test: A-fis
    """
    dev = path.vfis_mev.device
    if fismodel != 6:
        path = find_extrem(path, 5)
    nextr = min(path.nextr, 2 * NUMBAR - 1)
    nbar = nextr // 2 + 1

    rmiu_default = rmiufiscor * 0.054 * A ** (5.0 / 3.0)
    vheight = [torch.zeros((), dtype=DTYPE, device=dev) for _ in range(2 * NUMBAR + 2)]
    vwidth = [torch.zeros((), dtype=DTYPE, device=dev) for _ in range(2 * NUMBAR + 2)]
    vpos = [torch.zeros((), dtype=DTYPE, device=dev) for _ in range(2 * NUMBAR + 2)]
    fbar = [torch.zeros((), dtype=DTYPE, device=dev) for _ in range(NUMBAR + 1)]
    fwid = [torch.zeros((), dtype=DTYPE, device=dev) for _ in range(NUMBAR + 1)]
    for j in range(1, nextr + 1):
        i = path.iiextr[j]
        rrmiu = float(path.rmiufis[i]) if fismodel >= 5 else rmiu_default
        _height, width = parab_fit(i, 3, rrmiu, path)
        if float(width) < 0.05:  # wkb.f90:109, skip very narrow peaks
            continue
        vheight[j] = path.vfis_mev[i]  # the real height, not the fitted one (wkb.f90:122)
        vwidth[j] = width
        if j % 2 == 1:
            ii = (j + 1) // 2
            fbar[ii] = path.vfis_mev[i]
            fwid[ii] = width
        vpos[j] = path.betafis[i]
    vpos[nextr + 1] = _t(100.0, dev)

    uexc1 = torch.maximum(vheight[1], vheight[3]) if nextr >= 3 else vheight[1]
    if nextr == 5:
        uexc1 = torch.maximum(uexc1, vheight[5])
    n1 = 3 * nbinswkb // 4

    uwkb = [torch.zeros((), dtype=DTYPE, device=dev)]
    twkb = [[torch.zeros((), dtype=DTYPE, device=dev) for _ in range(NUMBAR + 1)]]
    tdir_l = [torch.zeros((), dtype=DTYPE, device=dev)]
    ttrans = [[torch.zeros((), dtype=DTYPE, device=dev) for _ in range(NUMBAR + 1)]]
    tphase = [[torch.zeros((), dtype=DTYPE, device=dev) for _ in range(NUMBAR + 1)]]

    vh = torch.stack(vheight)
    vw = torch.stack(vwidth)
    if not flagfispartdamp:
        # NATIVEX2: `wkbfis` at every tabulation energy in one C call (native/nx2_fis.c)
        uexcs, uexc = [], 0.0
        for i in range(1, nbinswkb + 1):
            uexc += float(uexc1) / n1 if i <= n1 else 0.2
            uexcs.append(uexc)
        got = _wkbfis_native(path, uexcs, vh, vw)
        if got is not None:
            tff, tdir = got
            twkb_t = torch.zeros((nbinswkb + 1, NUMBAR + 1), dtype=DTYPE, device=dev)
            twkb_t[1:, 1 : nbar + 1] = torch.from_numpy(tff[:, 1 : 2 * nbar : 2]).to(dev)
            zeros = torch.zeros((nbinswkb + 1, NUMBAR + 1), dtype=DTYPE, device=dev)
            return WKBResult(
                nbar=nbar, nextr=nextr, fbarrier_mev=torch.stack(fbar),
                fwidth_mev=torch.stack(fwid), vheight_mev=vh, vwidth_mev=vw,
                vpos=torch.stack(vpos), uwkb_mev=_t([0.0] + uexcs, dev), twkb=twkb_t,
                twkbdir=_t(np.concatenate(([0.0], tdir)), dev), twkbtrans=zeros,
                twkbphase=zeros.clone(),
            )
    uexc = 0.0
    for i in range(1, nbinswkb + 1):
        de = float(uexc1) / n1 if i <= n1 else 0.2
        uexc += de
        tff, phase, tdir = wkbfis(path, uexc, vh, vw)
        uwkb.append(_t(uexc, dev))
        row = [torch.zeros((), dtype=DTYPE, device=dev)] * (NUMBAR + 1)
        prow = [torch.zeros((), dtype=DTYPE, device=dev)] * (NUMBAR + 1)
        for j in range(1, nbar + 1):
            row[j] = tff[2 * j - 1]
            if flagfispartdamp:
                prow[j] = phase[2 * j]
        twkb.append(row)
        tphase.append(prow)
        trow = [torch.zeros((), dtype=DTYPE, device=dev)] * (NUMBAR + 1)
        if flagfispartdamp:
            trow, tdir = _partdamp(path, nbar, uexc, vh, tdir, bdamp, dev)
        tdir_l.append(tdir)
        ttrans.append(trow)

    stack = lambda rows: torch.stack([torch.stack(r) for r in rows])  # noqa: E731
    return WKBResult(
        nbar=nbar,
        nextr=nextr,
        fbarrier_mev=torch.stack(fbar),
        fwidth_mev=torch.stack(fwid),
        vheight_mev=vh,
        vwidth_mev=vw,
        vpos=torch.stack(vpos),
        uwkb_mev=torch.stack(uwkb),
        twkb=stack(twkb),
        twkbdir=torch.stack(tdir_l),
        twkbtrans=stack(ttrans),
        twkbphase=stack(tphase),
    )


def _partdamp(path, nbar, uexc, vheight, tdir, bdamp, dev):
    """The `fispartdamp` well-damping factors of wkb.f90:174-202 (`Twkbtrans`)."""
    row = [torch.zeros((), dtype=DTYPE, device=dev)] * (NUMBAR + 1)
    if nbar <= 1:
        return [torch.zeros((), dtype=DTYPE, device=dev), _t(1.0, dev), _t(1.0, dev), row[3]], _t(
            0.0, dev
        )
    vwell = path.vfis_mev[path.iiextr[2]] if path.iiextr[2] > 0 else _t(0.0, dev)
    vwell2 = path.vfis_mev[path.iiextr[4]] if len(path.iiextr) > 4 and path.iiextr[4] > 0 else _t(0.0, dev)
    vtop = torch.minimum(vheight[1], vheight[3])
    vtop2 = torch.minimum(vheight[3], vheight[5])
    out = list(row)
    for idx, (vw_, vt, b) in enumerate(((vwell, vtop, bdamp[0]), (vwell2, vtop2, bdamp[1])), start=1):
        u = _t(uexc, dev)
        if uexc < float(vw_):
            out[idx] = _t(0.0, dev)
        elif uexc > float(vt):
            out[idx] = _t(1.0, dev)
        else:
            out[idx] = (u**2 - vw_**2) / ((vt**2 - vw_**2) * torch.exp(-(u - vt) / b))
    return out, tdir


# ----------------------------------------------------------------------------- interpolation


def _wkb_interp(uwkb: Tensor, tab: Tensor, efis: Tensor, log_interp: bool) -> Tensor:
    nbins = uwkb.shape[0] - 1
    e = torch.as_tensor(efis, dtype=DTYPE, device=uwkb.device)
    nen = locate(uwkb, e, 0, nbins).clamp(0, nbins - 1)
    ea, eb = uwkb[nen], uwkb[nen + 1]
    ta, tb = tab[nen], tab[nen + 1]
    flat = ea == eb
    safe_b = torch.where(flat, eb + 1.0, eb)
    lin = pol1(ea, safe_b, ta, tb, e)
    if log_interp:
        pos = (ta > 0) & (tb > 0)
        lo = torch.clamp(ta, min=1e-300)
        hi = torch.clamp(tb, min=1e-300)
        logv = torch.exp(pol1(ea, safe_b, torch.log(lo), torch.log(hi), e))
        out = torch.where(pos, logv, lin)
    else:
        out = lin
    out = torch.where(flat, ta, out)
    return torch.where(e > uwkb[nbins], torch.ones_like(out), out)


def twkbint(res: WKBResult, efis: Tensor, ibar: int) -> Tensor:
    """Interpolate the tabulated WKB penetrability of barrier `ibar` at energy `efis` [MeV].

    Log-linear where both bracketing values are positive, linear otherwise, and 1 above the
    top of the table.

    TALYS: twkbint.f90:1 (twkbint)
    Test: A-fis
    """
    return _wkb_interp(res.uwkb_mev, res.twkb[:, ibar], efis, True)


def twkbtransint(res: WKBResult, efis: Tensor, ibar: int) -> Tensor:
    """Interpolate the class-II damping factor of well `ibar` (`fispartdamp` only).

    TALYS: twkbtransint.f90:1 (twkbtransint)
    Test: A-fis
    """
    return _wkb_interp(res.uwkb_mev, res.twkbtrans[:, ibar], efis, True)


def twkbphaseint(res: WKBResult, efis: Tensor, ibar: int) -> Tensor:
    """Interpolate the well phase integral of barrier `ibar` (`fispartdamp` only).

    TALYS: twkbphaseint.f90:1 (twkbphaseint)
    Test: A-fis
    """
    return _wkb_interp(res.uwkb_mev, res.twkbphase[:, ibar], efis, False)


__all__ = [
    "FissionPath",
    "WKBResult",
    "find_extrem",
    "hfbpath_file",
    "parab_fit",
    "read_hfbpath",
    "twkbint",
    "twkbphaseint",
    "twkbtransint",
    "wkb",
    "wkbfis",
]
