"""The CPU half of `capture_gpu`: everything the capture fast path computes that does NOT depend
on the photon strength, extracted per (nuclide, incident energy) as plain float64 arrays.

Task: SPEEDG (the GPU (nuclide, energy) batch axis). No physics of its own: every array is the
output of the statements `capture_fast_batch.capture_xs` runs, in the same order, stopped just
before the first number that reads the photon strength function.

What is extracted, per in-domain point:

* **comptarget** (`target_batch.case_moldauer` / `case_nowfc`): the compound (J, parity) cells,
  each cell's particle widths `D_t` (t = 1..6, in the order `denom` adds them), its incident
  channels, the Moldauer weight sums `r_exit` of the open particle exit channels and their
  transmissions; and of the photon residual (the compound nucleus's own bins) the masked `rho0`
  (continuum and discrete levels) and the photon energies `Etotal - Ex`.
* **the compound nucleus's decay** (`capture_fast_batch.CaptureDecay` / `_cascade_cn`): the
  excitation grid, `rhogrid`, `maxJ`, the discrete levels (spin, parity, half-life, branching),
  and every particle exit's summed width `D_t` for each mother bin that can decay by emission.

The photon transmissions, the photon widths, Moldauer's integral (its total width contains the
photon width), the populations and the cascade are `capture_gpu`'s, on the batch axis.

Test: SPEEDG / tests/hf/test_capture_gpu.py
"""

from __future__ import annotations

from types import SimpleNamespace

import numpy as np
import torch

from physics.hf.compound.prepare import NUMJ, PARSPIN2
from physics.hf.core.tensors import DTYPE

PARZ = (0, 0, 1, 1, 1, 2, 2)
PARN = (0, 1, 0, 1, 2, 1, 2)


class Unsupported(RuntimeError):
    """A point outside what the GPU path reproduces (the caller keeps the CPU path for it)."""


# ------------------------------------------------------------------------------ comptarget


def _comptarget_setup(ci) -> dict:
    """`target._case` -> `case_moldauer` / `case_nowfc` up to the photon strength.

    TALYS: comptarget.f90:1 (comptarget), molprepare.f90:1 (molprepare)
    Test: SPEEDG / tests/hf/test_capture_gpu.py
    """
    from physics.hf.compound.prepare import incident_channels
    from physics.hf.compound.target import _exact_incident_channel
    from physics.hf.compound.target_batch import _cells, _prepare

    inp = _exact_incident_channel(ci)
    use_wfc = inp.flagwidth and inp.wmode >= 1
    if use_wfc and inp.wmode != 1:
        raise Unsupported(f"widthmode {inp.wmode}")
    if inp.flagfission and inp.nfisbar != 0:
        raise Unsupported("fission")
    cells = _cells(inp)
    if not cells:
        raise Unsupported("no compound cells")
    k0, lt = inp.k0, inp.ltarget
    if use_wfc and k0 in inp.residuals and lt > inp.residuals[k0].nlast:
        raise Unsupported("target level not discrete")
    got = _prepare(inp, cells)
    if got is None:
        raise Unsupported("J-dependent photon transmission")
    prep, pidx = got
    K = len(cells)
    if sorted(prep) != list(range(7)):
        raise Unsupported(f"exit types {sorted(prep)}")
    dpart = np.stack([prep[t]["D"].numpy() for t in range(1, 7)], axis=1)  # (K, 6)
    incs = [incident_channels(inp, *c) for c in cells]
    na = max(1, max(len(ch) for ch, _ in incs))
    tinc = np.zeros((K, na))
    feedsum = np.zeros(K)
    for i, (_ch, tv) in enumerate(incs):
        if len(tv):
            tinc[i, : len(tv)] = tv
        feedsum[i] = float(torch.as_tensor(tv, dtype=DTYPE).sum())  # case_nowfc's `feed`
    out = dict(J2=np.array([c[0] for c in cells], dtype=np.int64), pidx=pidx.numpy(),
               dpart=dpart, tinc=tinc, feedsum=feedsum, cn=float(inp.cnfactor_mb),
               wfc=bool(use_wfc), wfcfactor=int(inp.wfcfactor))
    if use_wfc:
        parts = list(range(1, 7))
        t_exit = torch.cat([torch.where(prep[t]["raw"] > 1.0e-30, prep[t]["raw"], 0.0).reshape(-1)
                            for t in parts])
        nz = torch.nonzero(t_exit > 0.0).flatten()
        pk = pidx
        r_list = []
        for t in parts:  # case_moldauer's weight sums, for every cell
            p = prep[t]
            A = torch.einsum("niq,kilu->kqnlu", p["rho_c"], p["M"])
            par = ((torch.arange(p["L"]) % 2)[None, None, :]
                   == (pk[:, None] != torch.arange(2)[None, :]).to(torch.int64)[..., None])
            Rw = (A * par[:, :, None, :, None].to(DTYPE)).sum(1)
            d = p["disc"]
            if d is not None:
                Rd = d["rho_d"][None, :, None, None] * d["Md"] * d["parm"][..., None]
                Rw = torch.cat([Rw[:, : d["nd"]] + Rd, Rw[:, d["nd"]:]], dim=1)
            Rw = Rw * p["lm"][None, :, :, None].to(DTYPE)
            r_list.append(Rw.reshape(K, -1))
        out["r_exit"] = torch.cat(r_list, dim=1)[:, nz].numpy()  # (K, nch)
        out["t_nz"] = t_exit[nz].numpy()  # (nch,)
    else:
        out["r_exit"] = np.zeros((K, 0))
        out["t_nz"] = np.zeros(0)
    # the photon residual: the compound nucleus's own bins (primary decay, Rboundary = 1)
    r = inp.residuals[0]
    p0 = prep[0]
    out["rho_c0"] = p0["rho_c"].numpy()  # (R0, numJ+1, 2)
    d = p0["disc"]
    if d is None:
        raise Unsupported("no discrete photon residual rows")
    out["rho_d0"] = d["rho_d"].numpy()
    out["ird0"] = d["ird"].numpy()
    out["pd0"] = d["pd"].numpy()
    out["okd0"] = d["ok"].numpy()
    out["jd2_0"] = np.asarray(r.jdis2[: d["nd"]], dtype=np.int64)
    out["nrow0"] = int(r.maxex + 1)
    return out, inp


# ------------------------------------------------------------------------------ cascade


def _particle_widths(cas, st, sp, bins: list[int]) -> list[np.ndarray | None]:
    """`CaptureDecay`'s summed widths `D` (m, nj, 2) of the particle exits t = 1..6 for mother
    bins `bins` (None for an exit with nothing open). The statements of `CaptureDecay.__init__`
    for t >= 1, unchanged; the photon exit is `capture_gpu`'s.

    TALYS: densprepare.f90:1 (densprepare), compound.f90:1 (compound)
    Test: SPEEDG / tests/hf/test_capture_gpu.py
    """
    from physics.hf.compound.continuum import _spin_l_mask
    from physics.hf.compound.decay_batch import _interp_tl
    from physics.hf.compound.dens_reference import _eendmax

    odd = sp.A % 2
    exinc = np.array([float(sp.ex_mev[b]) for b in bins])
    dexinc = np.array([float(sp.dex_mev[b]) for b in bins])
    maxj = np.array([int(sp.maxj[b]) for b in bins], dtype=np.int64)
    nj = int(maxj.max()) + 1
    nxm = [cas.nexmax(st, sp, b) for b in bins]
    eendmax = _eendmax(cas.Zt, cas.At, cas.enincmax)
    fnorm = cas.fisom(sp.zix, sp.nix)
    ex0plus = exinc + 0.5 * dexinc
    ex0min = exinc - 0.5 * dexinc
    out: list[np.ndarray | None] = []
    for t in range(1, 7):
        d = cas.spec(st, sp.zix + PARZ[t], sp.nix + PARN[t])
        nexmax = np.array([max(x[t], 0) for x in nxm], dtype=np.int64)
        n = int(nexmax.max()) + 1
        ss = sp.sep_mev[t]
        rows = np.arange(n)
        inrow = rows[None, :] <= nexmax[:, None]
        ex = np.asarray(d.ex_mev[:n], dtype=np.float64)[None, :]
        dexhalf = 0.5 * np.asarray(d.dex_mev[:n], dtype=np.float64)[None, :]
        nl = d.nlast
        ex1min = ex - dexhalf
        top = rows[None, :] == nexmax[:, None]
        ex1plus = np.where(top, (ex0plus - ss)[:, None], ex + dexhalf)
        emax = (ex0plus - ss)[:, None] - ex1min
        emin = (ex0min - ss)[:, None] - ex1plus
        eout_mid = 0.5 * (emin + emax)
        below = emin < 0.0
        half = 0.5 * (emax - emin)
        with np.errstate(divide="ignore", invalid="ignore"):
            rb_c = np.where(below, np.where(eout_mid > 0.0, 1.0 - 0.5 * (emin / half) ** 2,
                                            0.5 * (emax / half) ** 2), 1.0)
        eout_c = 0.5 * (np.where(below, 0.0, emin) + emax)
        exm = ex + ss
        part = (ex0min[:, None] < exm) & (exm <= ex0plus[:, None])
        with np.errstate(divide="ignore", invalid="ignore"):
            rb_d = np.where(part, (ex0plus[:, None] - exm) / dexinc[:, None], 1.0)
        eout_d = np.where(part, 0.5 * (ex0plus[:, None] + exm) - ss - ex,
                          (exinc - ss)[:, None] - ex)
        cont_row = rows[None, :] > nl
        eout = np.where(cont_row, eout_c, eout_d)
        rb = np.where(cont_row, rb_c, rb_d)
        eout = np.where(inrow, eout, 0.0)
        _tjl, tl, _lmax = cas.trans[t]
        eend = min(int(eendmax[t]), cas.rg.maxen)
        tlm, lm = _interp_tl(eout, cas.rg.egrid, cas.rg.ebegin[t], eend, cas.rg.maxen,
                             tl, _lmax, float(fnorm[t + 1]), cas.transeps)
        L = tl.shape[1]
        lmaxhf = np.where(inrow, lm, 0)
        lp = np.arange(L)
        Tn = np.stack([np.where(lp % 2 == c, tlm, 0.0) for c in (0, 1)], axis=1)
        sfac = float(PARSPIN2[t] + 1)
        ii = np.nonzero(nexmax > 0)[0]
        lmaxhf[ii, nexmax[ii]] = lmaxhf[ii, nexmax[ii] - 1]
        if t == cas.k0:
            lmaxhf[:, 0] = st.lmaxinc
        lmask = np.arange(L)[None, None, None, :] <= lmaxhf[:, None, :, None]
        Tn = np.where(lmask, Tn, 0.0)
        open_l = np.flatnonzero(Tn.any(axis=(0, 1, 2)))
        if open_l.size == 0:
            out.append(None)
            continue
        L = int(open_l[-1]) + 1
        Tn = Tn[..., :L]
        maxj_d = np.asarray(d.maxj[:n], dtype=np.int64)
        keepj = (np.arange(NUMJ + 1)[None, :] <= maxj_d[:, None]) & (rows > nl)[:, None]
        rho = np.where(keepj[None, :, :, None],
                       rb[:, :, None, None] * np.asarray(d.rhogrid[:n], dtype=np.float64)[None],
                       0.0)
        discfactor = (min(max((d.ncum_nl - d.ntop) / (d.nlast - d.ntop), 0.5), 2.0)
                      if d.nlast > d.ntop else 1.0)
        ndk = min(nl, n - 1) + 1
        for k in range(ndk):
            ir = int(d.jdis[k])
            if 0 <= ir <= NUMJ:
                pidx = 0 if int(d.parlev[k]) == -1 else 1
                v = rb[:, k] * discfactor if k > d.ntop else rb[:, k]
                rho[:, k, ir, pidx] = v
        rho = np.where(inrow[:, :, None, None], rho, 0.0)
        base = (odd + PARSPIN2[t]) % 2
        irs2 = 2 * np.arange(NUMJ + 1) + base
        valid_c = irs2[None, :] <= 2 * maxj_d[:, None]
        jdis2 = (2.0 * np.float32(np.asarray(d.jdis[:n]))).astype(np.int64)
        disc_row = rows <= nl
        rho_t = torch.as_tensor(rho, dtype=DTYPE)
        rho_t = torch.where(rho_t >= 1.0e-20, rho_t, 0.0)
        if nl == 0:
            rho_t[:, 0] = 0.0
        vc = torch.as_tensor(valid_c & ~disc_row[:, None])
        rho_c = torch.where(vc[None, :, :, None], rho_t, 0.0)
        T = torch.as_tensor(Tn, dtype=DTYPE)
        M = _spin_l_mask(odd, PARSPIN2[t], nj, L).to(DTYPE)
        R = torch.einsum("mnip,mcnl->mcipl", rho_c, T)
        MR = torch.einsum("jil,mcipl->mjcp", M, R)
        D = torch.stack([MR[..., 0, 0] + MR[..., 1, 1], MR[..., 1, 0] + MR[..., 0, 1]],
                        dim=-1) * sfac
        ndd = min(nl, n - 1) + 1
        if ndd > 0:
            jd2 = torch.as_tensor(jdis2[:ndd])
            j2 = 2 * torch.arange(nj) + odd
            sp2 = PARSPIN2[t]
            lbeg = torch.div(((j2[:, None] - jd2[None, :]).abs() - sp2).abs(), 2,
                             rounding_mode="floor")
            lend = torch.div(j2[:, None] + jd2[None, :] + sp2, 2, rounding_mode="floor")
            lpd = torch.arange(L)
            Md = ((lpd >= lbeg[..., None]) & (lpd <= lend[..., None])).to(DTYPE)
            tot_d = torch.einsum("jnl,mcnl->mjcn", Md, T[:, :, :ndd])
            ird = torch.div(jd2, 2, rounding_mode="floor")
            pd = torch.as_tensor((np.asarray(d.parlev[:ndd]) > 0).astype(np.int64))
            ok = (ird >= 0) & (ird <= NUMJ)
            irc = ird.clamp(0, NUMJ)
            ar = torch.arange(ndd)
            rho_d = torch.where(ok[None, :], rho_t[:, ar, irc, pd], 0.0)
            cmat = (torch.arange(2)[:, None] != pd[None, :]).to(torch.int64)
            tot_dp = torch.stack([tot_d[:, :, cmat[p], ar] for p in (0, 1)], dim=2)
            D = D + sfac * torch.einsum("mjpn,mn->mjp", tot_dp, rho_d)
        out.append(D.numpy())
    return out


def _cascade_setup(cas, st, sp, popeps_mb: float) -> dict:
    """The compound nucleus's grid, levels and particle widths for `_cascade_cn`.

    TALYS: multiple.f90:1 (multiple), cascade.f90:1 (cascade)
    Test: SPEEDG / tests/hf/test_capture_gpu.py
    """
    R = sp.maxex + 1
    ng = sp.nlast_grid
    smin = sp.sep_mev.get(1, 0.0)
    mode = np.zeros(R, dtype=np.int64)  # 0 nothing, 1 gamma cascade, 2 decay by emission
    nbr = max([len(v) for v in sp.branch.values()] + [1])
    br_k = np.zeros((R, nbr), dtype=np.int64)
    br_r = np.zeros((R, nbr))
    bins = []
    for nex in range(sp.maxex, 0, -1):
        exinc = float(sp.ex_mev[nex])
        if nex <= ng and exinc <= smin:
            if float(sp.tau_s[nex]) == 0.0:
                mode[nex] = 1
                for i, (k, ratio) in enumerate(sp.branch.get(nex, [])):
                    br_k[nex, i], br_r[nex, i] = k, ratio
            continue
        mode[nex] = 2
        bins.append(nex)
    widths = _particle_widths(cas, st, sp, bins) if bins else []
    popeps_a = popeps_mb / max(5 * sp.maxex, 1)  # multiple.f90:467
    maxj_b = np.array([int(sp.maxj[b]) for b in bins], dtype=np.int64)
    popeps_b = np.array([popeps_a / (5 * max(int(mj), 1)) * 0.5 for mj in maxj_b])
    d = sp  # the photon residual of a compound-nucleus bin is the compound nucleus
    discfactor = (min(max((d.ncum_nl - d.ntop) / (d.nlast - d.ntop), 0.5), 2.0)
                  if d.nlast > d.ntop else 1.0)
    iso = np.zeros(R, dtype=bool)
    for nex in range(1, ng + 1):
        iso[nex] = float(sp.tau_s[nex]) != 0.0
    return dict(
        R=R, ng=ng, nl=int(sp.nlast), ntop=int(sp.ntop), discfactor=float(discfactor),
        odd=int(sp.A % 2), sep0=float(sp.sep_mev[0]), sn=float(sp.sep_mev[1]),
        ex=np.asarray(sp.ex_mev, dtype=np.float64)[:R], dex=np.asarray(sp.dex_mev, np.float64)[:R],
        maxj=np.asarray(sp.maxj, dtype=np.int64)[:R],
        jdis2=(2.0 * np.float32(np.asarray(sp.jdis[:R]))).astype(np.int64),
        jdis_int=np.array([int(sp.jdis[k]) for k in range(R)], dtype=np.int64),
        parlev=np.asarray(sp.parlev, dtype=np.int64)[:R], iso=iso,
        rhogrid=np.asarray(sp.rhogrid, dtype=np.float64)[:R],
        mode=mode, br_k=br_k, br_r=br_r, bins=np.array(bins, dtype=np.int64),
        widths=[(t + 1, w) for t, w in enumerate(widths) if w is not None],
        popeps_a=float(popeps_a), popeps_b=popeps_b, popeps_mb=float(popeps_mb),
        fn1=float(cas.fisom(sp.zix, sp.nix)[1]))


# ------------------------------------------------------------------------------ per point


def setup_point(tg, e_inc_mev: float) -> dict:
    """Every photon-strength-independent array of one in-domain capture point.

    TALYS: comptarget.f90:1 (comptarget), multiple.f90:1 (multiple) for (Zcomp, Ncomp) = (0, 0)
    Test: SPEEDG / tests/hf/test_capture_gpu.py
    """
    from physics.hf import capture_fast as CF
    from physics.hf import capture_fast_batch as CB
    from physics.hf.compound.chain import compound_inputs
    from physics.hf.emission.feed_reference import etotal_of

    cas = tg.cas
    if not (cas.batched and not cas.flagfullhf):
        raise Unsupported("per-bin decay path")
    e = CF._f32(e_inc_mev)
    k0 = cas.k0
    etot = etotal_of(tg.Z, tg.A, tg.enincmax, e, k0)
    inc = cas.incident(e)
    st = cas.new_energy(etot, lmaxinc=int(inc.lmax[0]))
    cas.propagate_exmax(st, 0, 0)
    binp = SimpleNamespace(e_inc_mev=e, k0=k0, targetspin2=tg.targetspin2,
                           target_parity=tg.target_parity, ltarget=0, popeps_mb=tg.popeps_mb,
                           flagpreeq=False)
    ci = compound_inputs(cas, st, binp, SimpleNamespace(flagfission=False), etot,
                         CF.ZERO_ADDENDS)
    ci = CB._trim_tjl(ci)
    ct, inp = _comptarget_setup(ci)
    sp = cas.spec(st, 0, 0)
    if ct["nrow0"] != sp.maxex + 1:
        raise Unsupported("photon residual rows != compound nucleus bins")
    r0 = inp.residuals[0]
    ex0 = np.asarray(r0.ex_mev, dtype=np.float64)
    ct["eg0"] = float(etot) - ex0  # densprepare's `exinc_mev - exout` (primary: Exout = Ex)
    ct["efs0"] = float(etot) - sp.sep_mev[1]
    ct["fn1_0"] = float(cas.fiso()[1])
    cs = _cascade_setup(cas, st, sp, tg.popeps_mb)
    out = dict(e_inc_mev=e, etot=float(etot), ct=ct, cs=cs)
    # the spin axis beyond the last populated J holds exact zeros only (see `capture_gpu.jcut_of`)
    from physics.hf.capture_gpu import jcut_of

    j = jcut_of(out)
    ct["rho_c0"] = np.ascontiguousarray(ct["rho_c0"][:, :j])
    cs["rhogrid"] = np.ascontiguousarray(cs["rhogrid"][:, :j])
    return out


def gamma_pack(Z: int, A: int) -> dict:
    """The compound nucleus's photon-strength parameters `capture_gpu.psf` evaluates, for the
    model family it covers (strength 9 SMLO tables with temperature, strengthM1 3 with the
    scissors term and the upbend, gammax 2). Raises `Unsupported` for anything else.

    TALYS: gammapar.f90:1 (gammapar), fstrength.f90:1 (fstrength)
    Test: SPEEDG / tests/hf/test_capture_gpu.py
    """
    from physics.hf.compound.dens_reference import _gamma_parameters

    gp, _o = _gamma_parameters(Z, A)
    ok = (gp.strength == 9 and gp.strengthM1 == 3 and gp.gammax == 2 and gp.flagupbend
          and not gp.flagpsfglobal and sorted(gp.tables) == [(1, 1)] and gp.n_tqrpa == 11
          and gp.ngr[0][1] == 1 and gp.ngr[0][2] == 1 and gp.ngr[1][2] == 1)
    tpr = gp.tpr_mb.numpy()
    upb = gp.upbend.numpy()
    ok = ok and not tpr[1].any() and not tpr[0, 2].any() and tpr[0, 1, 2] == 0.0
    ok = ok and upb[1, 1, 1] == 0.0 and not upb[0, 2].any() and not upb[1, 2].any()
    ok = ok and float(gp.etable_mev[1, 1]) == 0.0
    if not ok:
        raise Unsupported(f"photon strength model of {Z}-{A + 1}")
    tab = gp.tables[(1, 1)]
    e_raw = tab.e_raw_mev.numpy()
    if not np.all(np.diff(e_raw[1:]) > 0) or not e_raw[1] > 0.0:
        raise Unsupported("E1 table energies do not ascend")
    f = lambda t: float(t.detach()) if isinstance(t, torch.Tensor) else float(t)  # noqa: E731
    return dict(
        e_raw=e_raw, f_raw=tab.f_raw_mev3.numpy(), tq=gp.tqrpa_mev.numpy(),
        ftable=f(gp.ftable[1, 1]), wtable=f(gp.wtable[1, 1]),
        S=f(gp.S_k0_mev), delta=f(gp.delta_mev), alev=f(gp.alev_per_mev),
        beta2=f(gp.beta2),
        # M1: SLO + scissors + upbend; E2, M2: SLO. (sgr, egr, ggr) per multipole
        m1=(f(gp.sgr_mb[0, 1, 1]), f(gp.egr_mev[0, 1, 1]), f(gp.ggr_mev[0, 1, 1])),
        e2=(f(gp.sgr_mb[1, 2, 1]), f(gp.egr_mev[1, 2, 1]), f(gp.ggr_mev[1, 2, 1])),
        m2=(f(gp.sgr_mb[0, 2, 1]), f(gp.egr_mev[0, 2, 1]), f(gp.ggr_mev[0, 2, 1])),
        scissors=(f(gp.tpr_mb[0, 1, 1]), f(gp.epr_mev[0, 1, 1]), f(gp.gpr_mev[0, 1, 1])),
        upbend=(f(gp.upbend[0, 1, 1]), f(gp.upbend[0, 1, 2]), f(gp.upbend[0, 1, 3])),
    )


def setup_target(Z: int, A: int, energies, enincmax: float = 20.0,
                 tables_path: str | None = None) -> dict:
    """`setup_point` over one target's energies, with `run_task`'s domain and error semantics:
    the domain is marked energy by energy and the first error stops the target."""
    import time
    import traceback

    from physics.hf import capture_fast as CF
    from physics.hf import capture_fast_batch as CB

    t0 = time.perf_counter()
    dom = [False] * len(energies)
    points: dict[int, dict] = {}
    err = ""
    gpk = None
    try:
        tg = CF.target(Z, A, enincmax)
        if tables_path:
            from pathlib import Path

            if Path(tables_path).exists():
                CB.install_tables(tg, torch.load(tables_path, weights_only=False))
        for i, e in enumerate(energies):
            dom[i] = CF.in_domain(tg, float(e))
            if not dom[i]:
                continue
            points[i] = setup_point(tg, float(e))
        if points:
            gpk = gamma_pack(Z, A)
    except Exception as exc:
        err = f"{type(exc).__name__}: {exc}"[:300] + " | " + traceback.format_exc(limit=3)[-300:]
    finally:
        CB.forget_tables()
    return dict(Z=Z, A=A, energies=[float(e) for e in energies], domain=dom, points=points,
                gamma=gpk, err=err, seconds=time.perf_counter() - t0)
