"""INGRED: the physics ingredients behind a run's curves, as TALYS prints them.

`scripts/bestfit/engine_curves.py` saves every channel a run computes; this module saves the
inputs those channels were computed FROM -- the numbers TALYS writes to `ld*.gs`, `psf*.E1`,
`spr.opt` and its `Fission information` block -- so a later analysis can put a chart arm next to
measured D0 / <Gamma_gamma> / S0 (RIPL, Koning's resonance tables) nucleus by nucleus without
re-running anything.

Everything here is READ OFF the run. `ingredients(cas)` is called on the `Cascade` the run used,
after `engine_c.run` returned, so `cas.ld_of`, `cas.gamma_params` and `cas.incident` are cache
hits and no reaction is recomputed. Three quantities TALYS computes for output only, and the
engine therefore never builds, are computed here:

* ``dtheory`` -- the theoretical spacings D_l (densitymatch.f90:292 calls it for every nucleus;
  the engine's `densitymatch` has no reason to).
* ``radwidtheory`` -- the theoretical <Gamma_gamma> and the s-wave strength sum. With the default
  ``gnorm n`` nothing in TALYS's reaction reads them either (radwidtheory.f90:254 is the `gnorm`
  branch), so this is output, not physics that was skipped.
* ``resonancepar``'s ``Eavres`` -- see :func:`eavres_mev`.

Both are integrals over one level density, not a reaction: measured overhead is ~1-3 % of a
64-energy run (docs/results/ingred.md).

TALYS routines whose printed values these keys reproduce (file:line of the write):
    densityout.f90:261 (theoretical D0 [eV]), densityout.f90:257 (experimental D0 [eV])
    gammaout.f90:243 (theoretical Gamma_gamma [eV]), gammaout.f90:246 (S-wave strength [e-4])
    gammaout.f90:245 (average resonance energy [eV])
    spr.f90:72/78/82 (S0, S1, Rprime [fm])
    densityout.f90 header (a(Sn), pairing, shift, spin cutoff, Sn, ldmodel, ...)
    fissionparout.f90:126-131 (barrier height, width, axiality, continuum start)
Test: tests/hf/test_ingredients.py
"""

from __future__ import annotations

import json

import numpy as np

__all__ = ["ingredients", "eavres_mev", "PREFIX"]

PREFIX = "ing_"


def eavres_mev(options) -> float:
    """TALYS's `Eavres` at the moment `nuclides.f90:229` calls `radwidtheory(0, 0, Eavres)`.

    Two lines of `resonancepar.f90` decide this and they pull opposite ways: :74 resets `Eavres`
    to 0.01 MeV at the top of EVERY call, and :100-102 sets it to `0.5 (Nrr - 1) D0` only for the
    compound nucleus (`Zix == 0 .and. Nix == 0`). `nuclides.f90:219-228` calls `structure` -- and
    so `resonancepar` -- for the binary residuals of types 0..6 in order, the compound nucleus
    FIRST (type 0) and the alpha residual last, and only then calls `radwidtheory`. The compound
    nucleus's own value is therefore always overwritten: in a normal run TALYS integrates
    <Gamma_gamma> at exactly 0.01 MeV, whatever the resonance table says.

    That matters at the 1 % level and is the whole difference between the dumped <Gamma_gamma>
    and stock TALYS's printed one (Fe-56: 0.0381 MeV -- the compound nucleus's own Eavres --
    gives 1.3359 eV, 0.01 MeV gives 1.3037, which is what TALYS prints).

    `structure.resonances.resonance_parameters` keeps a per-nucleus `eavres_mev` that reports
    :100-102 alone; it is gated by A-struct against that line and is left alone.

    TALYS: resonancepar.f90:74, :100-102 (resonancepar), nuclides.f90:219-229 (nuclides)
    """
    from physics.hf.input.nuclides import binary_residuals
    from physics.hf.structure.files import read_resonance_file

    ev = 0.01
    for zix, nix in binary_residuals(options):
        ev = 0.01  # resonancepar.f90:74, every call
        if (zix, nix) != (0, 0):
            continue  # resonancepar.f90:100, only the compound nucleus may set it
        Z, A = options.Zinit - zix, (options.Zinit + options.Ninit) - zix - nix
        d0 = 0.0
        for ia, L, Df, _dDf, _Sf, _dSf, _ggf, _dggf, _Rf, _dRf, nrrf in read_resonance_file(Z):
            if ia != A or L != 0:
                continue
            Df = float(np.float32(Df))
            if Df != 0.0 and d0 == 0.0:
                d0 = Df
            if nrrf > 0 and d0 > 0.0:
                ev = float(np.float32(np.float32(0.5) * (np.float32(nrrf - 1) * np.float32(d0))
                                      * np.float32(1.0e-6)))
    return ev


def _f(x) -> float:
    return float(x.detach().reshape(-1)[0]) if hasattr(x, "detach") else float(x)


def _a(x) -> np.ndarray:
    return np.asarray(x.detach().cpu().numpy() if hasattr(x, "detach") else x, dtype=np.float64)


def _ld_block(cas, Z: int, A: int, tspin: float, tpar: int) -> tuple[dict, dict]:
    """(flat scalars, the whole ld*.gs header) for one nucleus of this run."""
    from physics.hf.density.models import dtheory, ld_header

    ld = cas.ld_of(Z, A)[0]
    hdr = ld_header(ld, 0)
    D = dtheory(ld, tspin, tpar, 0.0, 0)
    flat = {
        "sn_mev": _f(ld.S_mev),
        "d0theo_ev": float(D[0]),
        "d1theo_ev": float(D[1]),
        "ldmodel": int(ld.ldmodel),
        "flagcol": int(bool(ld.flagcol)),
        "alev_mev1": _f(ld.alev),
        "alimit_mev1": _f(ld.alimit),
        "gammald": _f(ld.gammald),
        "deltaw_mev": _f(ld.deltaW_mev[0]),
        "pair_mev": _f(ld.pair_mev),
        "pshift_mev": _f(ld.Pshift_mev[0]),
        "delta_mev": _f(ld.delta_mev[0]),
        "scutoffdisc": _f(ld.scutoffdisc[0]),
        "exmatch_mev": _f(ld.Exmatch_mev[0]),
        "t_mev": _f(ld.T_mev[0]),
        "e0_mev": _f(ld.E0_mev[0]),
        "ctable": _f(ld.ctable[0]),
        "ptable_mev": _f(ld.ptable_mev[0]),
        "s2adjust": _f(ld.s2adjust[0]),
        "beta2": _f(ld.beta2[0]),
        "krotconstant": _f(ld.Krotconstant[0]),
        "nlow": int(ld.Nlow[0]),
        "ntop": int(ld.Ntop[0]),
        "nlast": int(ld.Nlast[0]),
        "nlevmax2": int(ld.nlevmax2),
        "nfisbar": int(ld.nfisbar),
        "has_ld_table": int(ld.has_table(0)),
    }
    # `ld_header` prints the analytical-model block only for ldmodel <= 3 (densityout.f90); the
    # spin cut-off at Sn and Rhotot(Sn) are the two that are always worth having, so take them
    # from the header when it has them and compute them when it does not.
    flat["spincut_sn"] = hdr.get("spin cutoff parameter(Sn)")
    flat["rhotot_sn_permev"] = hdr.get("Rhotot(Sn) [MeV^-1]")
    if flat["spincut_sn"] is None:
        from physics.hf.density.parameters import ignatyuk, spincut

        flat["spincut_sn"] = _f(spincut(ld, ignatyuk(ld, ld.S_mev, 0), ld.S_mev, 0))
    if flat["rhotot_sn_permev"] is None:
        from physics.hf.density.models import densitytot

        flat["rhotot_sn_permev"] = _f(densitytot(ld, ld.S_mev, 0))
    return flat, hdr


def _fission_block(cas, Z: int, A: int) -> tuple[dict, dict]:
    """Barrier heights/widths per barrier for one nucleus, or ({}, {}) if it has none.

    `fission.parameters.fission_parameters` is `fissionpar.f90`: barrier files, Sierk/RLDM
    systematics and the transition-state bands. It reads no reaction quantity and the run's own
    `FissionChain` builds the same object from the same `(options, params, masses)`.
    """
    from physics.hf.fission.parameters import fission_parameters

    if not bool(cas.options.flagfission):
        return {}, {}
    try:
        fp = fission_parameters(Z, A, cas.options, cas.params, masses=cas.m)
    except Exception:  # a nucleus fissionpar declines is not an error
        return {}, {}
    n = int(fp.nfisbar)
    if n <= 0:
        return {}, {}
    sl = slice(1, n + 1)  # per-barrier arrays are 1-based with a dummy element 0
    flat = {
        "nfisbar": n,
        "fismodelx": int(fp.fismodelx),
        "nclass2": int(fp.nclass2),
        "fbarrier_mev": _a(fp.fbarrier_mev)[sl],
        "fwidth_mev": _a(fp.fwidth_mev)[sl],
        "fecont_mev": _a(fp.fecont_mev)[sl],
        "minertia": _a(fp.minertia)[sl],
        "axtype": np.asarray(fp.axtype[sl], dtype=np.int64),
    }
    meta = {
        "nfisbar": n,
        "fismodelx": int(fp.fismodelx),
        "nclass2": int(fp.nclass2),
        "barriers": [
            {"barrier": i, "height_mev": float(flat["fbarrier_mev"][i - 1]),
             "width_mev": float(flat["fwidth_mev"][i - 1]),
             "fecont_mev": float(flat["fecont_mev"][i - 1]),
             "axtype": int(flat["axtype"][i - 1]),
             "minertia": float(flat["minertia"][i - 1]),
             "nheadband": int(fp.headband[i].n) if i < len(fp.headband) else 0}
            for i in range(1, n + 1)
        ],
    }
    return flat, meta


def ingredients(cas, res=None) -> dict:
    """Every `ing_*` key for the run `cas` just finished.

    Scalars are float64 (ints stay ints); per-energy quantities are float64 arrays over the run's
    declared grid `cas.energies`, in that order (a `Cascade` built without one is a one-energy
    run and the per-energy block is skipped). `ing_*_json` keys carry the complete blocks -- the
    whole ld*.gs header, the photon-strength parameters, the fission barriers -- as JSON text, so
    nothing the run knew is dropped for want of a flat key.

    `res` is the `engine_c.run` result. Nothing here needs it: every ingredient is an input to
    that result, not a part of it. It is accepted so a later ingredient that does need one (a
    normalisation, say) does not change every caller.
    """
    from physics.hf.density.models import density_callable
    from physics.hf.gamma.transmission import radwidtheory
    from physics.hf.structure.resonances import resonance_parameters

    o = cas.options
    Zt, At = int(cas.Zt), int(cas.At)
    Zc, Ac = int(cas.Zc), int(cas.Ac)
    lv_cn = cas._levels(0, 0)
    lv_tg = cas._levels(0, 1)
    tspin = float(lv_tg.all_spin[o.Ltarget])
    tpar = int(lv_tg.all_parity[o.Ltarget])
    # the target's own D0theo is the spacing of ITS compound nucleus, so TALYS's dtheory(0, 1, 0)
    # uses the ground state of (Zt, At - 1) as the "target" (dtheory.f90:81-84, L0 = 0)
    lv_tg_daughter = cas._levels(0, 2)

    out: dict = {"Zt": Zt, "At": At, "Zc": Zc, "Ac": Ac,
                 "projectile": int(o.k0), "ltarget": int(o.Ltarget),
                 "target_spin": tspin, "target_parity": tpar}

    cn_flat, cn_hdr = _ld_block(cas, Zc, Ac, tspin, tpar)
    tg_flat, tg_hdr = _ld_block(cas, Zt, At,
                                float(lv_tg_daughter.all_spin[0]),
                                int(lv_tg_daughter.all_parity[0]))
    out.update(cn_flat)
    out.update({"tgt_" + k: v for k, v in tg_flat.items()})

    # measured resonance data TALYS read for the same two nuclei (ld*.gs / psf* 'experimental')
    rd_cn = resonance_parameters(Zc, Ac, o, cas.params)
    rd_tg = resonance_parameters(Zt, At, o, cas.params)
    out.update({
        "d0_exp_ev": float(rd_cn.d0_ev), "d0_exp_unc_ev": float(rd_cn.dd0_ev),
        "d0global_ev": float(rd_cn.d0global_ev),
        "d1_exp_ev": float(rd_cn.d1_ev),
        "s0_exp_e4": float(rd_cn.s0), "s0_exp_unc_e4": float(rd_cn.ds0),
        "s1_exp_e4": float(rd_cn.s1), "s1_exp_unc_e4": float(rd_cn.ds1),
        "rprime_exp_fm": float(rd_cn.r_scat_fm),
        "gamgam_exp_ev": float(rd_cn.gamgam_ev),
        "gamgam_exp_unc_ev": float(rd_cn.dgamgam_talys) * 1.0e3,
        "gamgam_exp_talys": float(rd_cn.gamgam_talys),
        "nrr": int(rd_cn.nrr),
        "tgt_d0_exp_ev": float(rd_tg.d0_ev), "tgt_s0_exp_e4": float(rd_tg.s0),
    })

    # theoretical <Gamma_gamma> and the s-wave strength sum, at TALYS's surviving Eavres
    gp = cas.gamma_params(Zt, At)
    ld_cn = cas.ld_of(Zc, Ac)[0]
    eav = eavres_mev(o)
    out["eavres_mev"] = eav
    if gp is None:
        # `Cascade.gamma_params` returns None only for a TENSOR photon-strength override, where
        # nothing may run the numpy path; the curves still land, the widths are simply not known
        out.update({"strength": -1, "strengthM1": -1, "gammax": -1,
                    "gamgam_th_ev": float("nan"), "gamgam_th_p_ev": float("nan"),
                    "swaveth": float("nan"), "swaveth_e4": float("nan")})
    else:
        out["strength"] = int(gp.strength)
        out["strengthM1"] = int(gp.strengthM1)
        out["gammax"] = int(gp.gammax)
        rw = radwidtheory(
            gp, eav, _f(ld_cn.S_mev),
            lv_cn.all_e_mev, lv_cn.all_spin, lv_cn.all_parity, tspin, tpar,
            density_callable(ld_cn, 0),
            out["d0theo_ev"], out["d1theo_ev"], nlast=int(ld_cn.Nlast[0]),
        )
        out["gamgam_th_ev"] = _f(rw.gamgamth0_ev)
        out["gamgam_th_p_ev"] = _f(rw.gamgamth1_ev)
        out["swaveth"] = _f(rw.swaveth)
        out["swaveth_e4"] = _f(rw.swaveth) * 1.0e4

    # S0 / S1 / R' and the incident-channel cross sections, per declared energy (spr.f90)
    energies = list(cas.energies or ())
    if energies:
        s0 = np.empty(len(energies)); s1 = np.empty(len(energies))
        rp = np.empty(len(energies)); tot = np.empty(len(energies))
        rea = np.empty(len(energies)); ela = np.empty(len(energies))
        lmx = np.zeros(len(energies), dtype=np.int64)
        for i, e in enumerate(energies):
            inc = cas.incident(float(e))
            s0[i] = _f(inc.s0) * 1.0e4
            s1[i] = _f(inc.s1) * 1.0e4
            rp[i] = _f(inc.r_prime_fm)
            tot[i] = _f(inc.sigma_tot_mb)
            rea[i] = _f(inc.sigma_reac_mb)
            ela[i] = _f(inc.sigma_shape_el_mb)
            lmx[i] = int(_f(inc.lmax)) if inc.lmax is not None else -1
        out.update({"e_inc_mev": np.asarray(energies, float), "s0_e4": s0, "s1_e4": s1,
                    "rprime_fm": rp, "sigma_tot_mb": tot, "sigma_reac_mb": rea,
                    "sigma_shape_el_mb": ela, "lmaxinc": lmx})
        out["s0_e4_first"] = float(s0[0])
        out["s1_e4_first"] = float(s1[0])
        out["rprime_fm_first"] = float(rp[0])

    fis_cn, fis_cn_meta = _fission_block(cas, Zc, Ac)
    fis_tg, fis_tg_meta = _fission_block(cas, Zt, At)
    out.update({"fis_" + k: v for k, v in fis_cn.items()})
    out.update({"tgt_fis_" + k: v for k, v in fis_tg.items()})

    out["ld_cn_json"] = json.dumps(cn_hdr, default=float)
    out["ld_tgt_json"] = json.dumps(tg_hdr, default=float)
    out["psf_json"] = json.dumps(_psf_meta(gp), default=float)
    out["fis_json"] = json.dumps({"compound": fis_cn_meta, "target": fis_tg_meta}, default=float)

    return {PREFIX + k: v for k, v in out.items()}


def _psf_meta(gp) -> dict:
    """The photon-strength parameters TALYS prints in the psf* header, as far as `gp` holds
    them (gammaout.f90:196-239). Tables (strength 4-13) have no Lorentzian parameters."""
    if gp is None:
        return {}
    m: dict = {"strength": int(gp.strength), "strengthM1": int(gp.strengthM1),
               "gammax": int(gp.gammax)}
    for name in ("egr_mev", "ggr_mev", "sgr_mb", "epr_mev", "gpr_mev", "tpr_mb",
                 "ftable", "etable", "wtable", "upbend", "upbendadjust",
                 "S_k0_mev", "delta_mev", "alev_per_mev", "beta2", "flagupbend", "flagcol"):
        v = getattr(gp, name, None)
        if v is None:
            continue
        if hasattr(v, "detach"):
            m[name] = _a(v).tolist()
        elif isinstance(v, (int, float, bool)):
            m[name] = v
    return m
