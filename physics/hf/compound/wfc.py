"""Width fluctuation corrections: Moldauer (widthmode 1, default for neutrons) with TALYS's
Gauss-Laguerre integral, HRTW (2), and GOE (3) with TALYS's 50x50x50 Gauss-Legendre triple
integral and its many-channel asymptotic expansion.

Ported from TALYS-2.x (https://github.com/arjankoning1/talys), MIT License,
Copyright (c) A.J. Koning. See physics/hf/NOTICE-TALYS.md.

Task: T9 (physics/hf/CONTRACT.md §7). Acceptance test: A-cn2 (§6).

TALYS routines ported here (file:line of the subroutine/function statement):
    gaulag.f90:1 (gaulag)
    compoundinit.f90:1 (compoundinit)  -- nmold = 32 for wmode 1
    molprepare.f90:1 (molprepare)
    moldauer.f90:1 (moldauer)
    widthfluc.f90:1 (widthfluc)
    hrtw.f90:1 (hrtw)
    hrtwprepare.f90:1 (hrtwprepare)
    goe.f90:1 (goe)
    goeprepare.f90:1 (goeprepare)
    func1.f90:1 (func1)
    prodm.f90:1 (prodm)
    prodp.f90:1 (prodp)
    gauleg.f90:1 (gauleg)

How the port is vectorised. TALYS evaluates the Moldauer integral once per (incident channel a,
exit channel b) pair inside six nested loops:

    W(a,b) = sum_m P_m * (1 + 2 d_ab / nu_a) / ((1 + x_m f_a) (1 + x_m f_b)),   f = 2 T / (st nu)
    W(a,gamma) = sum_m P_m / (1 + x_m f_a)
    P_m = w_m^2 e^{x_m} exp(-T_gamma x_m / st) prod_i (1 + x_m f_i)^(-nu_i rho_i / 2)

The population sums sum_a T_a W(a,b), which factorises: G_b = sum_m P_m/(1 + x_m f_b) H_m with
H_m = sum_a T_a/(1 + x_m f_a), plus the elastic diagonal a = b. The cost is O(M (A + B)) instead
of O(M A B), and the product over channels depends only on the distinct transmission values,
each weighted by its summed level density (channels that differ only in residual spin/parity
share T and nu). Nothing here depends on the order TALYS enumerates channels in.
"""

from __future__ import annotations

import math

import torch
from torch import Tensor

from physics.hf.core.numerics import gauleg
from physics.hf.core.tensors import DTYPE

# gaulag.f90:10-73. TALYS stores these in real(sgl); the float64 literals are kept and the
# conversion to single precision is applied (as TALYS does on assignment) so the nodes are the
# ones TALYS integrates with.
_GAULAG_X = (
    4.4489365833267018e-02, 2.3452610951961854e-01, 5.7688462930188643e-01,
    1.0724487538178176e00, 1.7224087764446454e00, 2.5283367064257949e00,
    3.4922132730219945e00, 4.6164567697497674e00, 5.9039585041742439e00,
    7.3581267331862411e00, 8.9829409242125961e00, 1.0783018632539972e01,
    1.2763697986742725e01, 1.4931139755522557e01, 1.7292454336715315e01,
    1.9855860940336055e01, 2.2630889013196774e01, 2.5628636022459248e01,
    2.8862101816323475e01, 3.2346629153964737e01, 3.6100494805751974e01,
    4.0145719771539442e01, 4.4509207995754938e01, 4.9224394987308639e01,
    5.4333721333396907e01, 5.9892509162134018e01, 6.5975377287935053e01,
    7.2687628090662709e01, 8.0187446977913523e01, 8.8735340417892399e01,
    9.8829542868283973e01, 1.1175139809793770e02,
)
_GAULAG_W = (
    0.3304819843083507, 0.4587407851268658, 0.4849878654872182, 0.4426096880693881,
    0.3605326424695436, 0.2656663769951280, 0.1782159154205232, 0.1091705767816519,
    6.1145860813398685e-02, 3.1317779401083899e-02, 1.4658271344239885e-02,
    6.2612634252105599e-03, 2.4360914623364682e-03, 8.6118549562028460e-04,
    2.7576380979237979e-04, 7.9690665868882078e-05, 2.0691503017038005e-05,
    4.8019782297417133e-06, 9.8991814251114182e-07, 1.7993892457523653e-07,
    2.8586401388458671e-08, 3.9270011884309682e-09, 4.6041202092947340e-10,
    4.5325816857372190e-11, 3.6701261376652915e-12, 2.3793474169186305e-13,
    1.1910333939327800e-14, 4.3742147803396949e-16, 1.0919014424838086e-17,
    1.6344758239998953e-19, 1.1569861460303905e-21, 2.1238022963305632e-24,
)


def gauss_laguerre(device=None) -> tuple[Tensor, Tensor]:
    """The 32-point Gauss-Laguerre nodes and the SQUARE ROOTS of the weights, exactly as gaulag.f90
    stores them (sgl); molprepare squares them.

    TALYS: gaulag.f90:1 (gaulag), compoundinit.f90:1 (compoundinit)
    Test: A-cn2
    """
    x = torch.tensor(_GAULAG_X, dtype=torch.float32).to(DTYPE)
    w = torch.tensor(_GAULAG_W, dtype=torch.float32).to(DTYPE)
    return x.to(device), w.to(device)


def degrees_of_freedom(tav: Tensor, st: Tensor, wfcfactor: int = 1) -> Tensor:
    """Moldauer's nu for channels with average transmission `tav` and total width `st`.

    TALYS: molprepare.f90:72-106 (inside molprepare)
    Test: A-cn2
    """
    if wfcfactor == 1:
        return torch.clamp(1.78 + (tav**1.212 - 0.78) * torch.exp(-0.228 * st), max=2.0)
    alpha, beta, gamma = 0.177, 20.337, 3.148
    if wfcfactor == 2:
        fT = alpha / (1.0 - tav**beta)
        gT = 1.0 + gamma * tav * (1.0 - tav)
        return torch.clamp(2.0 - 1.0 / (1.0 + fT * st**gT), min=1.0, max=2.0)
    if wfcfactor == 3:
        alpha1 = 0.0287892 * tav + 0.245856
        beta1 = 1.0 + 2.5 * tav * (1.0 - tav) * torch.exp(-2.0 * st)
        gamma1 = tav * tav - (st - 2.0 * tav) ** 2
        ok = (gamma1 > 0) & (st < 2 * tav)
        delta1 = torch.where(ok, torch.sqrt(torch.clamp(gamma1, min=0.0)) / torch.where(tav > 0, tav, 1.0), 1.0)
        f = alpha1 * (st + tav) / (1.0 - tav) * beta1 * delta1
        return 2.0 - 1.0 / (1.0 + f)
    raise ValueError(f"WFCfactor {wfcfactor} is not a TALYS option")


def moldauer_product(
    x: Tensor,
    w: Tensor,
    st: Tensor,
    t_exit: Tensor,
    rho_exit: Tensor,
    nu_exit: Tensor,
    t_gamma: Tensor,
) -> Tensor:
    """P_m for each Gauss-Laguerre node: w^2 e^x exp(-T_gamma x/st) prod_i (1 + 2 T_i x/(st nu_i))^(-nu_i rho_i/2).

    `t_exit`, `rho_exit`, `nu_exit` are flat over every exit particle/fission channel (group
    duplicates by summing rho: the product only depends on T and nu). Channels with
    eps = 2 T x/(st nu) <= 1e-30 are skipped as in TALYS.

    TALYS: molprepare.f90:112-139 (inside molprepare)
    Test: A-cn2
    """
    eps = 2.0 * t_exit[None, :] * x[:, None] / (st * nu_exit[None, :])
    live = eps > 1.0e-30
    logterm = torch.where(live, torch.log1p(torch.where(live, eps, 0.0)), 0.0)
    factor = (-nu_exit * 0.5 * rho_exit)[None, :] * logterm
    expo = t_gamma * x / st
    capt = torch.where(expo > 80.0, 0.0, torch.exp(-torch.clamp(expo, max=80.0)))
    # molprepare.f90:134-136: fxmsqrt = wmo * exp(0.5 x); fxmold = fxmsqrt * prod * fxmsqrt. The
    # gaulag table stores sqrt(weight) (wgl(1) = 0.3305 = sqrt(0.10922)), so the weight is w**2.
    return w * w * torch.exp(x) * torch.exp(factor.sum(1)) * capt


def moldauer_sums(
    x: Tensor,
    product: Tensor,
    st: Tensor,
    t_inc: Tensor,
    nu_inc: Tensor,
    t_b: Tensor,
    nu_b: Tensor,
) -> tuple[Tensor, Tensor, Tensor]:
    """The three incident-summed Moldauer quantities a block of exit channels needs.

    Returns
      G_b     = sum_a T_a W(a,b) without the elastic term, shape t_b.shape
      G_gamma = sum_a T_a W(a,gamma), scalar
      E_a     = sum_m P_m (2/nu_a) / (1 + x f_a)^2, shape (A,): the elastic extra for b = a,
                so the elastic diagonal contributes T_a (W(a,a) + E_a) -- moldauer.f90:52
    TALYS: moldauer.f90:1 (moldauer)
    Test: A-cn2
    """
    fa = 2.0 * t_inc / (st * nu_inc)  # (A,)
    da = 1.0 + x[:, None] * fa[None, :]  # (M, A)
    H = (t_inc[None, :] / da).sum(1)  # (M,)
    shape = t_b.shape
    fb = (2.0 * t_b / (st * nu_b)).reshape(-1)
    Gb = ((product * H)[:, None] / (1.0 + x[:, None] * fb[None, :])).sum(0).reshape(shape)
    Gg = (product * H).sum()
    Ea = (product[:, None] * (2.0 / nu_inc)[None, :] / da**2).sum(0)
    return Gb, Gg, Ea


def moldauer(
    tjl: Tensor,
    degeneracy: Tensor,
    nodes: Tensor,
    weights: Tensor,
    a: Tensor,
    b: Tensor,
    options=None,
) -> Tensor:
    """Moldauer width-fluctuation factor W(a,b), batched over (a, b) pairs, for a single (J, parity)
    whose flat channel list is `tjl` (rho*T values in TALYS's transjl(1,.) sense is NOT used here:
    `tjl` are the channel transmission coefficients) with level-density weights `degeneracy`.
    Index `b == len(tjl)` denotes the lumped capture channel, as `nb == numtjl + 1` in TALYS.
    `a` must index incident channels, which are the first entries and not part of the product
    (molprepare.f90 loops i = Ninc + 1, numtjl): pass `options={"ninc": n, "st": st, "tgamma": Tg}`.

    This scalar-pair form exists for tests and diagnosis; the production path is moldauer_sums.

    TALYS: moldauer.f90:1 (moldauer), molprepare.f90:1 (molprepare)
    Test: A-cn2
    """
    ninc = int(options["ninc"])
    st = torch.as_tensor(options["st"], dtype=DTYPE)
    tg = torch.as_tensor(options["tgamma"], dtype=DTYPE)
    wfcf = int(options.get("wfcfactor", 1))
    elastic = options.get("elastic")
    nu = degrees_of_freedom(tjl, st, wfcf)
    prod = moldauer_product(nodes, weights, st, tjl[ninc:], degeneracy[ninc:], nu[ninc:], tg)
    fa = 2.0 * tjl[a] / (st * nu[a])
    capture = b >= tjl.shape[0]
    bb = torch.where(capture, 0, b)
    fb = torch.where(capture, 0.0, 2.0 * tjl[bb] / (st * nu[bb]))
    dab = torch.zeros_like(fa) if elastic is None else elastic.to(DTYPE)
    fac = 1.0 + 2.0 * dab / nu[a]
    num = torch.where(capture[:, None], 1.0, fac[:, None])
    den = (1.0 + nodes[None, :] * fa[:, None]) * torch.where(
        capture[:, None], 1.0, 1.0 + nodes[None, :] * fb[:, None]
    )
    return (prod[None, :] * num / den).sum(1)


def hrtw_prepare(
    t: Tensor,
    rho: Tensor,
    st: Tensor,
    n_inc: int,
    wfcfactor: int = 1,
    niter: int = 60,
) -> tuple[Tensor, Tensor, Tensor]:
    """(v, w, sv) of the HRTW correction for one (J, parity): `t` and `rho` are the flat channel
    lists in TALYS's `transjl` order -- the `n_inc` incident channels first (rho = 1), then every
    exit channel, with the lumped capture channel last (rho = 1, T = gamwidth).

    `transjl(0,i) = rho`, `transjl(i,.) = rho T^i`, so `tav = transjl(1,.)/transjl(0,.) = T` and
    `st2 = sum_{exit} rho T^2`; the 60 fixed-point iterations are TALYS's own.

    TALYS: hrtwprepare.f90:1 (hrtwprepare)
    Test: A-cn2
    """
    tav = t
    st2 = (rho[n_inc:] * t[n_inc:] ** 2).sum()
    if wfcfactor == 1:
        factor = 4.0 * st2 / (st * st + 3.0 * st2)
        f = factor * (1.0 + tav / st)
        small = tav < st
        pw = torch.where(small, tav, torch.zeros_like(tav)) ** torch.where(small, f, torch.ones_like(f))
        w = torch.where(
            small,
            1.0 + 2.0 / (1.0 + pw) + 87.0 * (((tav - st2 / st) / st) ** 2) * (tav / st) ** 5,
            torch.full_like(tav, 3.0),
        )
    else:
        alpha, beta, gamma = 0.139, 15.247, 4.081
        fT = alpha / (1.0 - tav ** beta)
        gT = 1.0 + gamma * tav * (1.0 - tav)
        va = 2.0 - 1.0 / (1.0 + fT * st ** gT)
        w = 1.0 + 2.0 / va
    v = tav / (1.0 + tav / st * (w - 1.0))
    sv = torch.zeros((), dtype=DTYPE, device=t.device)
    for _ in range(niter):
        sv = (v[n_inc:] * rho[n_inc:]).sum()
        v = tav / (1.0 + v / sv * (w - 1.0))
    return v, w, sv


def hrtw_sums(
    v: Tensor,
    w: Tensor,
    sv: Tensor,
    st: Tensor,
    t_inc: Tensor,
    v_inc: Tensor,
    t_b: Tensor,
    v_b: Tensor,
) -> tuple[Tensor, Tensor]:
    """The incident-summed HRTW quantities, the counterpart of `moldauer_sums`.

    `hrtw.f90:21-24` is `W(a,b) = v_a v_b st / (sv T_a T_b) (1 + d_ab (w_a - 1))`, which
    factorises exactly, so `G_b = sum_a T_a W(a,b) = (st / sv) (v_b / T_b) sum_a v_a`.

    `E_a` is the ELASTIC EXTRA in the same convention as `moldauer_sums`: the `d_ab` part of
    W(a,a) itself, so the caller forms the diagonal term as `T_a T_b E_a` exactly as it forms
    `T_b G_b`. That is `E_a = (st / sv) (v_a / T_a)^2 (w_a - 1)` -- BOTH factors of `T_a`, since
    comptarget.f90:635 weights the width fluctuation factor by `Tinc * Tout`. Dropping one of
    them leaves the elastic enhancement short by exactly `T_a`, which is invisible at high
    energy and costs a factor `w_a` (up to 3) on compound elastic in the keV range, where the
    elastic channel is nearly all of `st`.

    TALYS: hrtw.f90:1 (hrtw)
    Test: A-cn2
    """
    vsum = v_inc.sum()
    scale = st / sv
    gb = torch.where(t_b > 0, scale * v_b / torch.where(t_b > 0, t_b, 1.0) * vsum, 0.0)
    ratio = v_inc / torch.where(t_inc > 0, t_inc, torch.ones_like(t_inc))
    ea = torch.where(t_inc > 0, scale * ratio * ratio * (w - 1.0), torch.zeros_like(ratio))
    return gb, ea


def hrtw(
    tjl: Tensor,
    degeneracy: Tensor,
    a: Tensor,
    b: Tensor,
    options=None,
) -> Tensor:
    """HRTW width-fluctuation factor W(a,b) (widthmode 2), batched over (a, b) pairs of one
    (J, parity). Index `b == len(tjl)` is the lumped capture channel, as in `moldauer`.
    `options = {"ninc": n, "st": st, "tgamma": Tg, "wfcfactor": 1|2, "elastic": mask}`.

    Scalar-pair form for tests and diagnosis; the production path is hrtw_prepare/hrtw_sums.

    TALYS: hrtw.f90:1 (hrtw), hrtwprepare.f90:1 (hrtwprepare)
    Test: A-cn2
    """
    ninc = int(options["ninc"])
    st = torch.as_tensor(options["st"], dtype=DTYPE)
    tg = torch.as_tensor(options["tgamma"], dtype=DTYPE)
    t_all = torch.cat([tjl, tg.reshape(1)])
    rho_all = torch.cat([degeneracy, torch.ones(1, dtype=DTYPE, device=tjl.device)])
    v, w, sv = hrtw_prepare(t_all, rho_all, st, ninc, int(options.get("wfcfactor", 1)))
    dab = torch.zeros(a.shape, dtype=DTYPE) if options.get("elastic") is None else options["elastic"].to(DTYPE)
    ta, tb = t_all[a], t_all[b]
    live = (ta > 0) & (tb > 0)
    num = v[a] * v[b] * st * (1.0 + dab * (w[a] - 1.0))
    den = sv * torch.where(live, ta * tb, torch.ones_like(ta))
    return torch.where(live, num / den, torch.zeros_like(num))


# ================================================================================================
# GOE (widthmode 3) -- the triple integral
# ================================================================================================
#
# TALYS routines ported below (file:line of the subroutine/function statement):
#     gauleg.f90:1 (gauleg)        goeprepare.f90:1 (goeprepare)   goe.f90:1 (goe)
#     func1.f90:1 (func1)          prodm.f90:1 (prodm)             prodp.f90:1 (prodp)
#     compoundinit.f90:66-76       -- wpower = 5, ngoep = ngoes = ngoet = 50
#
# What the model is. GOE replaces Moldauer's one-dimensional Gauss-Laguerre integral by the
# Verbaarschot-Weidenmueller-Zirnbauer triple integral over (p, s, t), evaluated on a 50 x 50 x 50
# Gauss-Legendre product grid -- 125000 nodes, each carrying a product over every open channel.
# Above `st = denomhf = 20` TALYS abandons the grid for an asymptotic expansion in the channel
# strength moments s1..s5 (goeprepare.f90:197-213, goe.f90:136-179). That switch is what makes
# the model affordable: the grid branch only ever runs where few channels are open.
#
# How the port is vectorised, and why it is exact. TALYS calls `goe` once per (incident a, exit b)
# pair, so the grid branch costs O(M A B) with M = 125000. Both branches factorise over `a`:
#
#  * Grid branch (goe.f90:102-135). With `ielas = 0`, func1.f90:30-32 leaves only
#      f2 = A(1+A)/((1+ta A)(1+tb A)) + B(1+B)/((1+ta B)(1+tb B)) + 2C(1-C)/((1-ta C)(1-tb C)),
#    and `res1 = ta rhob sum_g (fpst1 f2 + fpst2 f2')`. Each of the six terms splits into a factor
#    in (grid, ta) and one in (grid, tb), so
#      sum_a T_a W(a,b) = st sum_g [ fpst1_g ( A(1+A)/(1+tb A) H^A_g + ... ) + fpst2_g ( ... ) ],
#      H^A_g = sum_a T_a / (1 + T_a A_g)   -- six such sums, one per x-array.
#    The cost falls to O(M (A + B)). `rhob = tjl(1,nb)` cancels against `tt` at goe.f90:180, so
#    here W(a,b) depends on the exit channel ONLY through `tav(nb)`, and lumping the (Ir, P')
#    cells that share a transmission coefficient is exact, exactly as it is for Moldauer.
#
#  * Moment branch (goe.f90:143-178). `res1` is a degree-5 polynomial in `ta` with tb-dependent
#    coefficients. A <= ~40 and the whole (A, B) outer product is a few 1e5 numbers, so this
#    branch is evaluated pair by pair as the Fortran writes it, chunked over b.
#
# The one place lumping is NOT free is `tb6` (goe.f90:157):
#     tb6 = tjl(1,nb) tjl(5,nb) / max(tjl(0,nb), 1) = rho^2 T^6 / max(rho, 1),
# which is linear in rho only for rho >= 1. Every other tb-term is a single `tjl(i,nb) = rho T^i`
# and no ta-term carries rho, so `res1` is linear in rho except through tb6. Summing the lumped
# cells therefore needs BOTH sum(rho) and `kappa = sum(rho^2 / max(rho, 1))`. Passing sum(rho) for
# both would misplace the -1348 taptb5 / s1^5 term of c2s5 by at most 1348 (1-rho) T^5 / st^5,
# i.e. 4e-4 relative at the st = 20 switch and falling as st^-5 -- small, but free to get right.
#
# Deviations from TALYS, stated rather than silent:
#  * float64 throughout (contract 4.1). TALYS holds the grid arrays (fpst1, fpst2, x02, ...) and
#    `res` in real(sgl), rounds every prodm/prodp factor to sgl, and rounds each of the 125000
#    grid terms to sgl before adding it to a real(dbl) sum. Those roundings are ~1e-7 apiece; the
#    random walk over the grid is ~3e-5 relative, orders under the 2% A-cn2 tolerance.
#  * `x1rat ** 10` underflows real(sgl) to zero once x1rat < 1e-3.8, which is most of the grid
#    when many channels are open. float64 keeps those terms; they are <= 1e-38 relative.
#  * The Gauss-Legendre nodes come from gauleg.f90's own Newton iteration -- including its
#    off-by-one `p2`, which is the derivative at the PREVIOUS iterate -- run in float64 and cast
#    through float32, the precision TALYS stores them in.

GOE_NGOE = 50  # compoundinit.f90:70-72
GOE_STSWITCH = 20.0  # goeprepare.f90:111, goe.f90:102
_GAULEG: dict[int, tuple[Tensor, Tensor]] = {}
# Both hot loops build a (nodes x channels) temporary and reduce it. They are bandwidth bound,
# not flop bound, so the temporary is written in place and kept small enough to stay in cache --
# together worth ~2x on the grid branch, which is most of the port's runtime. The two optima
# differ because one is a transcendental (few, large passes) and the other a division (many,
# small ones); both were measured on this box, not guessed.
_LOG_CHUNK = 1 << 19
_SUM_CHUNK = 1 << 22


def gauss_legendre(n: int = GOE_NGOE, device=None) -> tuple[Tensor, Tensor]:
    """`core.numerics.gauleg(n)` -- TALYS's gauleg.f90 table, in its own node order, with its
    HALF-sized weights and **in its own single precision** -- cached per n and moved to `device`.

    Both of those are load-bearing here. The halving is undone by hand in goeprepare.f90
    (`wp1 = 2 wp`, `ws1 = 0.5 sqrt(2) ws`, ...), so a textbook table would double the integral.
    And `gauleg.f90:50` builds the weight from `P_{n-1}` computed by an (n-1)-term real(sgl)
    recurrence, which for n = 50 leaves the OUTERMOST weight 9.8e-4 high -- the node this
    integrand is dominated by, since `p -> -1` drives `p2 = (3 - pp)/pp` to ~5e3. `gauleg`'s
    float64 mode is a different answer, not a better one; see its docstring.

    TALYS: gauleg.f90:1 (gauleg)
    Test: A-cn2
    """
    if n not in _GAULEG:
        _GAULEG[n] = gauleg(n)
    x, w = _GAULEG[n]
    return x.to(device), w.to(device)


def _log_channel_product(y: Tensor, tav: Tensor, rho: Tensor, sign: float) -> Tensor:
    """`sum_i rho_i log(1 + sign tav_i y)` at every node of `y`: the logarithm of `prodm`
    (sign = -1, exponent rho/10) and `prodp` (sign = +1, exponent rho/20), with the exponents left
    out so the caller can combine the three logarithms before exponentiating.

    prodm.f90:40 SKIPS a factor whose `1 - tav sx` has gone <= 0 instead of letting it turn
    negative; reproduced here. prodp has no such branch -- its argument is >= 1 for tav, sx >= 0.

    TALYS: prodm.f90:1 (prodm), prodp.f90:1 (prodp)
    Test: A-cn2
    """
    n, c = y.numel(), max(int(tav.numel()), 1)
    out = torch.empty_like(y)
    rows = max(1, _LOG_CHUNK // c)
    for lo in range(0, n, rows):
        d = y[lo:lo + rows, None] * tav[None, :]
        if sign < 0:
            d.neg_()
        d.add_(1.0)
        d.masked_fill_(d <= 0.0, 1.0)  # prodm.f90:40 skips the factor instead of going negative
        out[lo:lo + rows] = d.log_().mul_(rho[None, :]).sum(1)
    return out


def transjl_powers(t: Tensor, rho: Tensor, kappa: Tensor | None = None,
                   guard: Tensor | None = None, gamma: bool = False) -> Tensor:
    """`transjl(1..5, ch)` and goe.f90:157's `tb6`, stacked on a trailing axis of length 6, for
    channels of bare transmission `t` and level-density weight `rho`.

    `wpower = 5` for GOE (compoundinit.f90:69), and compprepare.f90:361-362 zeroes power `i`
    unless the channel's width exceeds `1e-30 ** (1/i)` -- a per-power floor of 1e-30, 1e-15,
    1e-10, 1e-7.5, 1e-6. That test is on `Tout` for particles, on `tfishill = rho T` for fission
    (compprepare.f90:407) and on `gamwidth` for photons, which also carry an upper cut
    (compprepare.f90:417); pass the tested quantity as `guard`.

    `kappa` is `sum(rho^2 / max(rho, 1))` over the (Ir, P') cells lumped into one channel, which
    is what their tb6 sums to; it defaults to the single-cell value.

    TALYS: compprepare.f90:359-363, :404-407, :414-417
    Test: A-cn2
    """
    g = t if guard is None else guard
    cols = []
    for i in range(1, 6):
        ok = g > 1.0e-30 ** (1.0 / i)
        if gamma:
            ok = ok & (g < 1.0e30 ** (1.0 / i))
        cols.append(torch.where(ok, rho * t ** i, torch.zeros_like(t)))
    if kappa is None:
        kappa = rho * rho / torch.clamp(rho, min=1.0)
    cols.append(torch.where((cols[0] > 0) & (cols[4] > 0), kappa * t ** 6, torch.zeros_like(t)))
    return torch.stack(cols, dim=-1)


def goe_prepare(t_exit: Tensor, rho_exit: Tensor, st: Tensor, t_gamma: Tensor,
                device=None, ngoe: int = GOE_NGOE, guard: Tensor | None = None) -> dict:
    """Everything `goe` needs that depends on (J, parity) but not on the channel pair: either the
    eight grid arrays of goeprepare.f90:111-196 or the five channel-strength moments of
    goeprepare.f90:197-213.

    `t_exit` / `rho_exit` are the flat exit-channel list (particles then fission, capture
    excluded). Channels with T = 0 or rho = 0 contribute a factor 1 to prodm/prodp and 0 to every
    moment, and channels sharing a transmission coefficient enter only through `sum(rho)`, so the
    list is collapsed to its distinct live transmissions first. That is exact and it is what makes
    the grid branch affordable: `comptarget` hands over one entry per (nexout, l', j') cell, which
    is ~2e4 above a few MeV, against ~1e3 distinct live values.
    `guard` is the quantity compprepare.f90 tests each `transjl` power against (`Tout` for
    particles, `tfishill` for fission); it defaults to `t_exit`.

    TALYS: goeprepare.f90:1 (goeprepare)
    Test: A-cn2
    """
    st = torch.as_tensor(st, dtype=DTYPE, device=device)
    tg = torch.as_tensor(t_gamma, dtype=DTYPE, device=device).reshape(())
    keep = (t_exit != 0) & (rho_exit != 0)
    t_exit, rho_exit = t_exit[keep], rho_exit[keep]
    guard = None if guard is None else guard[keep]
    if guard is None:
        t_exit, inv = torch.unique(t_exit, return_inverse=True)
        rho_exit = torch.zeros_like(t_exit).index_add_(0, inv, rho_exit)
    if float(st.detach()) >= GOE_STSWITCH:
        # goeprepare.f90:206-212: the moments run over the exit channels AND the capture channel.
        one = torch.ones(1, dtype=DTYPE, device=device)
        s = transjl_powers(t_exit, rho_exit, guard=guard).sum(0) \
            + transjl_powers(tg.reshape(1), one, guard=tg.reshape(1), gamma=True).reshape(6)
        return {"mode": "moments", "s": s, "st": st}

    p, wp = gauss_legendre(ngoe, device)
    sq, ws = gauss_legendre(ngoe, device)
    tq, wt = gauss_legendre(ngoe, device)
    # --- loop over p (goeprepare.f90:115-132) -------------------------------------------------
    p1 = p + 1.0
    pp = 0.5 * p1
    p2 = (3.0 - pp) / pp
    d = torch.sqrt(0.5 * p2)
    ds2 = 0.5 * d
    wpspp2 = 3.0 * wp / (pp * pp)
    if float(tg.detach()) == 0.0:
        ex02 = ex2i = torch.ones_like(p1)
    else:
        ex02, ex2i = torch.exp(-p1 * tg * 0.5), torch.exp(-p2 * tg * 0.5)
    # --- loop over s (goeprepare.f90:136-163) -------------------------------------------------
    r2 = math.sqrt(2.0)
    s1 = 0.25 * r2 * (sq + 1.0)  # (S,)
    s2 = ds2[:, None] * (sq + 1.0)[None, :]  # (P, S)
    s21, s22 = s1 * s1, s2 * s2
    ums21, ums22 = 1.0 - s21, 1.0 - s22
    ps21 = p1[:, None] * s21[None, :]
    umps21 = 1.0 - ps21
    pm2ps21 = p1[:, None] - ps21 - ps21
    um2s21 = ums21 - s21  # (S,)
    pums212 = p1[:, None] * (ums21 * ums21)[None, :]
    uppm2ps2 = pm2ps21 + 1.0
    pm2s22 = p2[:, None] - s22 - s22
    uppm2s2 = 1.0 + pm2s22
    pms222 = (p2[:, None] - s22) ** 2
    big = s2 > 1.0
    s22safe = torch.where(big, s22, torch.ones_like(s22))
    e = torch.where(big, torch.sqrt(torch.clamp(1.0 - 1.0 / s22safe, min=0.0)),
                    torch.zeros_like(s22))
    ume = 1.0 - e
    umes2, upes2 = 0.5 * ume, 0.5 + 0.5 * e
    wpws1 = (2.0 * wp)[:, None] * (0.5 * r2 * ws)[None, :]
    wpws2 = wpspp2[:, None] * (d[:, None] * ws[None, :])
    # --- loop over t (goeprepare.f90:169-194) -------------------------------------------------
    t1 = 0.5 * tq + 0.5  # (T,)
    t2 = umes2[..., None] * tq + upes2[..., None]  # (P, S, T)
    wt2 = ume[..., None] * wt
    t21, t22 = t1 * t1, t2 * t2
    s2t22 = s22[..., None] * t22
    s2t21 = s21[None, :, None] * t21[None, None, :]
    umt21, umt22 = 1.0 - t21, 1.0 - t22
    ps2t21 = ps21[..., None] * t21
    grid = (ps21[..., None] - ps2t21,              # x02
            ps2t21 + torch.zeros_like(s2t22),      # x102
            pm2ps21[..., None] + ps2t21,           # x202
            s22[..., None] - s2t22,                # x2i
            s2t22,                                 # x12i
            pm2s22[..., None] + s2t22)             # x22i
    flat = [v.reshape(-1) for v in grid]
    # goeprepare.f90:186-192: x1rat = prodm(x02)/prodp(x102)/prodp(x202), then x1rat ** 10. The
    # 1/10 and 1/20 exponents of prodm/prodp cancel that power exactly, so the logarithms combine.
    lr = []
    for k in (0, 3):
        lr.append(torch.exp(_log_channel_product(flat[k], t_exit, rho_exit, -1.0)
                            - 0.5 * _log_channel_product(flat[k + 1], t_exit, rho_exit, 1.0)
                            - 0.5 * _log_channel_product(flat[k + 2], t_exit, rho_exit, 1.0)
                            ).reshape(ngoe, ngoe, ngoe))
    fpst1 = (wpws1[..., None] * wt * (ps2t21 + umps21[..., None]) * um2s21[None, :, None] * umt21
             * ex02[:, None, None] * lr[0] / pums212[..., None]
             / torch.sqrt((um2s21[None, :, None] + s2t21) * (1.0 + ps2t21)
                          * (ps2t21 + uppm2ps2[..., None])))
    fpst2 = (wpws2[..., None] * wt2 * umt22 * (ums22[..., None] + s2t22) * pm2s22[..., None]
             * ex2i[:, None, None] * lr[1] / pms222[..., None]
             / torch.sqrt((1.0 + s2t22) * (pm2s22[..., None] + s2t22)
                          * (uppm2s2[..., None] + s2t22)))
    f1, f2 = fpst1.reshape(-1), fpst2.reshape(-1)
    live = (f1 != 0.0) | (f2 != 0.0)  # nodes where TALYS's sgl x1rat ** 10 is zero too
    if not bool(live.all()):
        f1, f2, flat = f1[live], f2[live], [v[live] for v in flat]
    return {"mode": "grid", "st": st, "fpst1": f1, "fpst2": f2, "x": tuple(flat)}


def goe_incident(prep: dict, t_inc: Tensor) -> dict:
    """The incident-channel sums the grid branch factorises into: `H_g = sum_a T_a / (1 -+ T_a x_g)`
    for each of the six x-arrays, already folded into func1.f90:31-32's grid-only factors.

    TALYS: goe.f90:110-135 summed over `na`, func1.f90:1 (func1)
    Test: A-cn2
    """
    if prep["mode"] == "moments":
        return {"t_inc": t_inc}
    ta = t_inc.reshape(-1)
    u, m = [], prep["x"][0].numel()
    rows = max(1, _SUM_CHUNK // max(int(ta.numel()), 1))
    fps = (prep["fpst1"],) * 3 + (prep["fpst2"],) * 3
    for k, (x, fp) in enumerate(zip(prep["x"], fps, strict=True)):
        sg = -1.0 if k % 3 == 0 else 1.0  # x02 and x2i are func1's `c`, which enters as (1 - t c)
        h = torch.empty(m, dtype=DTYPE, device=ta.device)
        for lo in range(0, m, rows):
            xx = x[lo:lo + rows, None]
            h[lo:lo + rows] = (ta[None, :] / (1.0 + sg * ta[None, :] * xx)).sum(1)
        u.append(fp * (2.0 * x * (1.0 - x) if sg < 0 else x * (1.0 + x)) * h)
    return {"u": u, "t_inc": t_inc}


def _goe_moment_res1(prep: dict, ta: Tensor, jl: Tensor) -> Tensor:
    """goe.f90:143-178 for one (a, b) pair set: returns `(c1_block, c2_block)` so both the
    ordinary and the `ielas = 1` caller can assemble `res1` from them.

    TALYS: goe.f90:136-179
    Test: A-cn2
    """
    s1, s2, s3, s4, s5 = (prep["s"][i] for i in range(5))
    s12 = s1 * s1
    s13, s14, s15 = s12 * s1, s12 * s12, s12 * s12 * s1
    ta2 = ta * ta
    ta3, ta4, ta5 = ta2 * ta, ta2 * ta2, ta2 * ta2 * ta
    c1 = 1.0 + (-2.0 - 4.0 * ta) / s1 \
        + (6.0 + 3.0 * s2 + 12.0 * ta + 34.0 * ta2) / s12 \
        + (-32.0 - 12.0 * s2 - 16.0 * s3 - 64.0 * ta - 40.0 * ta * s2 - 136.0 * ta2
           - 304.0 * ta3) / s13 \
        + (240.0 + 80.0 * s2 + 25 * s2 * s2 + 80 * s3 + 100.0 * s4 + 480.0 * ta + 200.0 * ta * s2
           + 240.0 * ta * s3 + 864.0 * ta2 + 524.0 * ta2 * s2 + 1520.0 * ta3 + 3508.0 * ta4) / s14
    tb, tb2, tb3, tb4, tb5, tb6 = (jl[..., i] for i in range(6))
    taptb = ta * tb + tb2
    taptb2 = ta2 * tb + ta * tb2 + tb3
    taptb3 = ta3 * tb + ta2 * tb2 + ta * tb3 + tb4
    taptb4 = ta4 * tb + ta3 * tb2 + ta2 * tb3 + ta * tb4 + tb5
    taptb5 = ta5 * tb + ta4 * tb2 + ta3 * tb3 + ta2 * tb4 + ta * tb5 + tb6
    c2 = tb - taptb / s1 \
        + (s2 * tb - 2.0 * taptb + 4.0 * taptb2) / s12 \
        + (s2 * (2.0 * tb - 5.0 * taptb) - 4.0 * s3 * tb + 4.0 * taptb + 8.0 * taptb2
           - 20.0 * taptb3) / s13 \
        + (s2 * (-4.0 * tb - 16.0 * taptb + 36.0 * taptb2) + s3 * (-8.0 * tb + 24.0 * taptb)
           + 20.0 * s4 * tb - 12.0 * taptb + 5.0 * s2 * s2 * tb - 20.0 * taptb2
           - 68.0 * taptb3 + 148.0 * taptb4) / s14 \
        + (s2 * (12.0 * tb + 48.0 * taptb + 156.0 * taptb2 - 336.0 * taptb3) - 60.0 * s2 * s3 * tb
           - 148.0 * s5 * tb + s3 * (20.0 * tb + 108.0 * taptb - 228.0 * taptb2)
           + s4 * (68.0 * tb - 168.0 * taptb) + s2 * s2 * (16.0 * tb - 41.0 * taptb)
           + 64.0 * taptb + 88.0 * taptb2 + 204.0 * taptb3 + 608.0 * taptb4
           - 1348.0 * taptb5) / s15
    return 2.0 * ta2 * (1.0 - ta) / s12 * c1, ta / s1 * c2


def goe_sums(prep: dict, inc: dict, t_b: Tensor, tjl_b: Tensor | None = None,
             capture: bool = False) -> Tensor:
    """`G_b = sum_a T_a W(a,b)` for a whole block of exit channels at once -- the GOE counterpart
    of `moldauer_sums` and `hrtw_sums`, and the production path.

    `t_b` is each channel's bare transmission; `tjl_b` is its `transjl(1..5)` plus `tb6` (see
    `transjl_powers`) and is used only by the moment branch. `capture=True` is goe.f90:106, which
    zeroes `tav` for the lumped photon channel while leaving `tjl(1,.) = gamwidth`.

    TALYS: goe.f90:1 (goe)
    Test: A-cn2
    """
    st, shape = prep["st"], t_b.shape
    tb = t_b.reshape(-1)
    if prep["mode"] == "grid":
        if capture:
            tb = torch.zeros_like(tb)
        # W depends on the exit channel only through `tav(nb)` here, so distinct values suffice --
        # and the caller's (nexout, l', j') block is mostly repeats and zeros.
        tb, inv = torch.unique(tb, return_inverse=True)
        xs, u = prep["x"], inc["u"]
        m = xs[0].numel()
        out = torch.zeros(tb.numel(), dtype=DTYPE, device=tb.device)
        rows = max(1, _SUM_CHUNK // max(m, 1))
        for lo in range(0, tb.numel(), rows):
            t = tb[lo:lo + rows, None]
            for k, (x, uu) in enumerate(zip(xs, u, strict=True)):
                d = t * x[None, :]
                if k % 3 == 0:  # func1's `c` slot enters as (1 - t c)
                    d.neg_()
                out[lo:lo + rows] += d.add_(1.0).reciprocal_().mul_(uu[None, :]).sum(1)
        return (st * out[inv]).reshape(shape)
    ta = inc["t_inc"].reshape(-1)
    jl = tjl_b.reshape(-1, 6)
    out = torch.zeros(jl.shape[0], dtype=DTYPE, device=tb.device)
    rows = max(1, _SUM_CHUNK // max(int(ta.numel()), 1))
    for lo in range(0, jl.shape[0], rows):
        _, c2 = _goe_moment_res1(prep, ta[None, :], jl[lo:lo + rows, None, :])
        out[lo:lo + rows] = c2.sum(1)
    # goe.f90:180-185: W = res1 st / tt with tt = tjl(1,na) tjl(1,nb) / tjl(0,na). Summing T_a W
    # over `a` cancels the tjl(1,na) that `res1` is proportional to and leaves one 1/tjl(1,nb).
    den = jl[:, 0]
    ok = den != 0
    return torch.where(ok, st * out / torch.where(ok, den, torch.ones_like(den)),
                       torch.zeros_like(den)).reshape(shape)


def goe_elastic(prep: dict, inc: dict, t_el: Tensor, tjl_el: Tensor | None = None) -> Tensor:
    """The elastic extra `E_a = W(a,a | ielas=1) - W(a,a | ielas=0)`, in the same convention as
    `moldauer_sums` and `hrtw_sums`: the caller adds `T_a T_b E_a` to the elastic cell.

    `t_el` / `tjl_el` describe, per incident channel, the exit channel with the SAME (l, j) at the
    target's own level -- the only pair comptarget.f90:630-632 sets `ielas = 1` for.

    TALYS: goe.f90:1 (goe) with ielas = 1, func1.f90:30 (the f1 term, which `ielas = 0` kills)
    Test: A-cn2
    """
    st, ta = prep["st"], inc["t_inc"].reshape(-1)
    if prep["mode"] == "grid":
        tb = t_el.reshape(-1)
        acc = torch.zeros_like(ta)
        xs = prep["x"]
        rows = max(1, _SUM_CHUNK // max(int(ta.numel()), 1))
        for k, fp in ((0, prep["fpst1"]), (3, prep["fpst2"])):
            # func1 is called as func1(x102, x202, x02) and func1(x12i, x22i, x2i): the
            # `c` slot -- the one entering as (1 - t c) -- is the FIRST of each triple.
            a, b, c = xs[k + 1], xs[k + 2], xs[k]
            for lo in range(0, a.numel(), rows):
                aa, bb, cc = a[None, lo:lo + rows], b[None, lo:lo + rows], c[None, lo:lo + rows]
                da = 1.0 + ta[:, None] * aa
                db = 1.0 + ta[:, None] * bb
                dc = 1.0 - ta[:, None] * cc
                f1 = (1.0 - ta)[:, None] * (aa / da + bb / db + 2.0 * cc / dc) ** 2
                f2 = (aa * (1.0 + aa) / (da * (1.0 + tb[:, None] * aa))
                      + bb * (1.0 + bb) / (db * (1.0 + tb[:, None] * bb))
                      + 2.0 * cc * (1.0 - cc) / (dc * (1.0 - tb[:, None] * cc)))
                acc += (fp[None, lo:lo + rows] * (f1 + f2)).sum(1)
        return st * acc
    jl = tjl_el.reshape(-1, 6)
    c1, c2 = _goe_moment_res1(prep, ta, jl)
    den = ta * jl[:, 0]
    ok = den != 0
    return torch.where(ok, st * (c1 + c2) / torch.where(ok, den, torch.ones_like(den)),
                       torch.zeros_like(den))


def goe(tjl: Tensor, degeneracy: Tensor, a: Tensor, b: Tensor, options=None) -> Tensor:
    """GOE width-fluctuation factor W(a,b) (widthmode 3), pair by pair, in the same shape as
    `moldauer` and `hrtw`: index `b == len(tjl)` is the lumped capture channel.
    `options = {"ninc": n, "st": st, "tgamma": Tg, "elastic": mask}`.

    Scalar-pair form for tests and diagnosis; the production path is goe_prepare/goe_incident/
    goe_sums, which this function is checked against in `tests/hf/test_compound.py`.

    TALYS: goe.f90:1 (goe), goeprepare.f90:1 (goeprepare)
    Test: A-cn2
    """
    ninc = int(options["ninc"])
    st = torch.as_tensor(options["st"], dtype=DTYPE)
    tg = torch.as_tensor(options["tgamma"], dtype=DTYPE)
    rho = degeneracy.to(DTYPE)
    prep = goe_prepare(tjl[ninc:], rho[ninc:], st, tg)
    el = options.get("elastic")
    dab = torch.zeros(a.shape, dtype=DTYPE) if el is None else el.to(DTYPE)
    cap = b >= tjl.shape[0]
    bb = torch.where(cap, 0, b)
    t_b = torch.where(cap, tg, tjl[bb])
    r_b = torch.where(cap, torch.ones_like(rho[bb]), rho[bb])
    jl_b = transjl_powers(t_b, r_b, guard=torch.where(cap, tg, t_b))
    out = torch.zeros(a.shape, dtype=DTYPE)
    for i in range(a.numel()):
        inc = goe_incident(prep, tjl[a[i]].reshape(1))
        w = goe_sums(prep, inc, t_b[i].reshape(1), jl_b[i].reshape(1, 6), capture=bool(cap[i]))
        w = w.reshape(()) / tjl[a[i]]
        if float(dab[i]) != 0.0:
            w = w + goe_elastic(prep, inc, t_b[i].reshape(1), jl_b[i].reshape(1, 6)).reshape(())
        out[i] = w
    return out
