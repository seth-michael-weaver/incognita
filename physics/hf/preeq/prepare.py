"""Assemble a `PreeqInputs` for the reference cases: grids, separation energies, pairing,
single-particle densities, and the injected inverse cross sections.

Ported from TALYS-2.x (https://github.com/arjankoning1/talys), MIT License,
Copyright (c) A.J. Koning. See physics/hf/NOTICE-TALYS.md.

Task: T8 (physics/hf/CONTRACT.md §7). Acceptance test: A-pe (§6).

TALYS routines ported here (file:line of the subroutine/function statement):
    densitypar.f90:1 (densitypar)   -- only the exciton-model g/gp/gn at :525-541
    excitoninit.f90:1 (excitoninit) -- only wfac at :64-72

Everything this module does not own is *injected* (contract §5): the inverse cross sections
`xsreac` come from `cross_<p>.tot`, the photo-absorption `xsreac(0, .)` from `cross_g.tot`
(extended with T7's `gammaxs` above the dumped range), the pairing energies from the
`ld<ZZZ><AAA>.gs` headers, and the flux `xsreacinc - xsdirdiscsum - xsgrsum` from the incident
scalars and the `directE*.out` headers. That separates "pre-equilibrium is wrong" from "an
input is wrong".
"""

from __future__ import annotations

import json
from functools import lru_cache

import numpy as np
import torch

from physics.hf import reference as ref
from physics.hf.core.constants import NUC, talys_constants
from physics.hf.core.grids import (
    charged_particle_begin,
    discrete_emission_begin,
    egrid_values,
    emission_bins,
    emission_end,
    emission_limit,
    incident_kinematics,
    number_of_bins,
    total_energy,
)
from physics.hf.core.tensors import DTYPE
from physics.hf.input.defaults import default_options, default_params
from physics.hf.input.nuclides import coulomb_barriers
from physics.hf.preeq.exciton import DiscreteInputs, PreeqInputs, esurf
from physics.hf.structure.levels import discrete_levels
from physics.hf.structure.masses import masses

NUMEN = 250  # A0_talys_mod.f90 numen
PARSYM = ("g", "n", "p", "d", "t", "h", "a")


def parse_target(target: str) -> tuple[int, int]:
    """ "Fe056" -> (26, 56).

    TALYS: constants.f90:1 (constants)
    Test: A-pe
    """
    sym, mass = target[:-3], int(target[-3:])
    for z, s in enumerate(NUC, start=1):
        if s.strip().lower() == sym.strip().lower():
            return z, mass
    raise KeyError(f"unknown element symbol in {target!r}")


def energies_for(target: str, variant: str = "default") -> list[float]:
    """The incident energies whose `exciton*.out` this run dumped (above the preeq onset).

    TALYS: preeq.f90:1 (preeq)
    Test: A-pe
    """
    import pandas as pd

    idx = pd.read_parquet(ref.reference_dir() / "block_index.parquet")
    s = idx[(idx.target == target) & (idx.variant == variant) & idx.file.str.startswith("exciton")]
    return sorted({float(f[7:-4]) for f in s.file.unique()})


@lru_cache(maxsize=64)
def _structure(target: str):
    Z, A = parse_target(target)
    options = default_options(Z, A)
    params = default_params(Z, A, options)
    return Z, A, options, params, masses(options, params)


def _meta_of(family: str, target: str, file: str, variant: str, block: int = 0) -> dict:
    """The meta dict of one block, as `ref.blocks(...)[block][0]` gives it, without pivoting
    every block of the file into a wide table first (that pivot was 25% of a chained run)."""
    return dict(_meta_cached(family, target, file, variant, block))


@lru_cache(maxsize=4096)
def _meta_cached(family: str, target: str, file: str, variant: str, block: int) -> dict:
    metas = _meta_table(family, target, variant)
    key = (file, int(block))
    if key not in metas:
        raise KeyError(block)
    return json.loads(metas[key])


@lru_cache(maxsize=64)
def _meta_table(family: str, target: str, variant: str) -> dict:
    """(file, block) -> the block's meta string (its first row's, as `_wide_blocks` reads it),
    for one target: three columns of one family, filtered at read."""
    import pyarrow.parquet as pq

    tab = pq.read_table(ref.reference_dir() / f"{family}.parquet",
                        columns=["file", "block", "meta"],
                        filters=[("target", "==", target), ("variant", "==", variant)])
    df = tab.to_pandas()
    df = df.assign(file=df["file"].astype(str), block=df["block"].astype(int))
    first = df.drop_duplicates(["file", "block"], keep="first")
    return dict(zip(zip(first["file"], first["block"]), first["meta"].astype(str)))


def single_particle_densities(Z: int, N: int, kph: float = 15.0) -> tuple[float, float, float]:
    """`g`, `gp`, `gn` [MeV^-1] for a nucleus: A/Kph, Z/Kph, N/Kph (densitypar.f90:533-541).

    The `gadjust`/`gpadjust`/`gnadjust` factors are 1 by default; pass an adjusted `kph` or
    scale the result to differentiate (§4.4).

    TALYS: densitypar.f90:1 (densitypar)
    Test: A-pe
    """
    return (Z + N) / kph, Z / kph, N / kph


def wfac(m, options, parskip=(False,) * 7) -> np.ndarray:
    """`wfac(type)` (excitoninit.f90:64-72): pi2h3c2 for photons, and
    amupi2h3c2 * (2s+1) * redumass for particles. Units mb^-1 MeV^-3 s^-1 / MeV^-2 s^-1.

    TALYS: excitoninit.f90:1 (excitoninit)
    Test: A-pe
    """
    c = talys_constants()
    out = np.zeros(7)
    out[0] = c["pi2h3c2"]
    for t in range(1, 7):
        if parskip[t]:
            continue
        Zix, Nix = c["parZ"][t], c["parN"][t]
        out[t] = (
            c["amupi2h3c2"] * (2.0 * c["parspin"][t] + 1.0) * float(m.redumass_amu[Zix, Nix, t])
        )
    return out


def _xsreac_rows(target: str, variant: str, particle: str, col: str) -> np.ndarray:
    w = ref.table("inverse_xs", target, f"cross_{particle}.tot", variant)[1]
    return w[col].to_numpy()


@lru_cache(maxsize=32)
def _gamma_parameters(target: str, variant: str):
    """T7's `GammaParameters` for the compound nucleus, built from the dumped level-density and
    PSF headers exactly as `physics.hf.gamma.score` does."""
    from physics.hf.gamma.parameters import gamma_parameters

    Z, A, options, _params, _m = _structure(target)
    tag = f"{Z:03d}{A + 1:03d}"
    md = _meta_of("level_density", target, f"ld{tag}.gs", variant)
    f = lambda k, d=0.0: float(str(md.get(k, d)).split()[0])  # noqa: E731
    mh = _meta_of("psf", target, f"psf{tag}.M1", variant)
    beta2 = float(str(mh.get("pygmy tpr [mb]", 0.0)).split()[0]) / (1.0e-2 * (A + 1) ** 0.9)
    return gamma_parameters(
        Z,
        A + 1,
        options,
        S_k0_mev=f("separation energy [MeV]"),
        delta_mev=f("pairing energy [MeV]"),
        alev_per_mev=f("a(Sn) [MeV^-1]"),
        beta2=beta2,
        flagcol=str(md.get("collective enhancement", "n")).strip() == "y",
    )


def _photoabsorption(
    target: str, variant: str, egrid: np.ndarray, nmax: int, energies: list[float]
) -> np.ndarray:
    """xsreac(0, nen) per incident energy, shape (C, nmax+1) [mb].

    `tgamma.f90:73` sets `xsreac(0, nen) = xsgamma`, and `gammaxs` reads `fstrength(..., Einc,
    Egamma, ...)`, so the photo-absorption the exciton model sees moves with the *incident*
    energy. `cross_g.tot` is dumped once, at the first incident energy and only up to `eend(0)`
    there, so it cannot be used as the injected value except as a cross-check; T7's ported
    `gammaxs` supplies the rest (A-psf holds it to ~1e-6).

    TALYS: gammaxs.f90:1 (gammaxs), tgamma.f90:1 (tgamma)
    """
    Z, A, _o, _p, _m = _structure(target)
    C = len(energies)
    out = np.zeros((C, nmax + 1))
    try:
        from physics.hf.gamma.transmission import gammaxs

        gp = _gamma_parameters(target, variant)
        e = torch.tensor(egrid[1 : nmax + 1], dtype=DTYPE)
        for i, einc in enumerate(energies):
            out[i, 1:] = gammaxs(gp, e, einc, Z, A)[0].numpy()
    except Exception:  # pragma: no cover - T7 parameters unavailable for this nuclide
        w = ref.table("inverse_xs", target, "cross_g.tot", variant)[1]
        dumped = w["cross section"].to_numpy()
        n = min(len(dumped), nmax)
        out[:, 1 : n + 1] = dumped[:n]
        out[:, n + 1 :] = dumped[-1] if len(dumped) else 0.0
    return out


@lru_cache(maxsize=8)
def _block_meta(target: str, variant: str) -> dict:
    """{(file, block): meta} from `block_index.parquet`, the only place some headers survive."""
    import pandas as pd

    idx = pd.read_parquet(ref.reference_dir() / "block_index.parquet")
    idx = idx[(idx.target == target) & (idx.variant == variant)]
    return {(r["file"], int(r["block"])): json.loads(r["meta"]) for _, r in idx.iterrows()}


def _flux(target: str, variant: str, energies: list[float]) -> np.ndarray:
    """`xsflux = xsreacinc - xsdirdiscsum - xsgrsum` [mb] (preeq.f90:105-106), injected.

    `xsreacinc` is the ECIS reaction cross section from `talys.out`; `xsdirdiscsum` and the two
    parts of `xsgrsum` (`xsgrtot(k0) + xscollconttot(k0)`, giant.f90:125-131) are the header
    fields of the two blocks of `directE*.out`. All three belong to the direct/giant-resonance
    tasks (T12, T13), so the exciton model takes them as given (contract §5).
    """
    inc = ref.incident_scalars(target, variant)
    reac = {round(float(r.e_inc_mev), 6): float(r.sigma_reac_omp_mb) for _, r in inc.iterrows()}
    meta = _block_meta(target, variant)
    out = np.zeros(len(energies))
    for i, e in enumerate(energies):
        x = reac[round(e, 6)]
        f = f"directE{e:08.3f}.out"
        g = lambda md, k: float(str(md.get(k, 0.0)).split()[0])  # noqa: E731
        if (f, 0) in meta:
            x -= g(meta[(f, 0)], "total discrete direct inelastic cross section [mb]")
            x -= g(meta[(f, 0)], "collective continuum inelastic cross section [mb]")
        if (f, 1) in meta:
            x -= g(meta[(f, 1)], "total GR cross section")
        out[i] = max(x, 0.0)
    return out


def _pairing_energy(target, variant, Zr, Ar, options, params, m) -> float:
    """`pair(Zix, Nix)` [MeV], the ground-state pairing energy `preeqpair` starts from.

    Read from the `ld<ZZZ><AAA>.gs` header where TALYS printed it; the tabulated level-density
    models (`ldmodel` 5-7, which every actinide resolves to) print no pairing energy at all,
    so those fall back to T6's `densitypar`, which computes it the same way for every model
    (densitypar.f90:397-405).

    TALYS: densitypar.f90:1 (densitypar)
    Test: A-pe
    """
    try:
        md = _meta_of("level_density", target, f"ld{Zr:03d}{Ar:03d}.gs", variant)
        return float(str(md["pairing energy [MeV]"]).split()[0])
    except (KeyError, IndexError, ValueError):
        pass
    try:
        from physics.hf.density.parameters import densitypar

        lv = discrete_levels(Zr, Ar, options, m, params)
        return float(densitypar(Zr, Ar, options, params, m, lv).pair_mev)
    except Exception:  # pragma: no cover - nucleus outside the structure database
        return 0.0


def _direct_discrete(target, variant, energies, k0, nlast):
    """`xsdirdisc(type, i)` [mb], injected from the rows of `directE*.out` (T12/T13's quantity).

    Only the inelastic channel has direct discrete cross sections for a neutron projectile on a
    spherical target; every other entry is zero. `preeqcorrect` skips any level that already has
    one (preeqcorrect.f90:54).
    """
    import pandas as pd

    raw = pd.read_parquet(ref.reference_dir() / "raw_rows.parquet")
    raw = raw[(raw.target == target) & (raw.variant == variant)]
    out = []
    for e in energies:
        per = [np.zeros(nlast[t] + 1) for t in range(7)]
        sub = raw[(raw.file == f"directE{e:08.3f}.out") & (raw.block.astype(int) == 0)]
        for line in sub["line"]:
            # level, energy, E-out, J, P, cross section, def. type, def. par. (directout.f90)
            f = line.split()
            if len(f) < 6:
                continue
            try:
                i, xs = int(f[0]), float(f[5])
            except ValueError:
                continue
            if i <= nlast[k0]:
                per[k0][i] = xs
        out.append(per)
    return out


def prepare(
    target: str,
    variant: str = "default",
    energies: list[float] | None = None,
    *,
    ecomp_from_dump: bool = True,
    chained: bool = False,
    enincmax_mev: float | None = None,
    direct_grid: tuple[float, ...] | None = None,
    fit: tuple = (),
) -> tuple[PreeqInputs, dict]:
    """A `PreeqInputs` and `DiscreteInputs` covering every dumped incident energy of one target,
    plus the reference header values (`Ecomp`, `Esurf`) the gate cross-checks against.

    With `chained=True` (NODUMP) the five injected inputs -- `xsreac` for the particles, the
    `GammaParameters` behind `xsreac(0, .)`, the residual pairing energies, `xsflux` and
    `xsdirdisc` -- come from `preeq.chain` instead of from a reference run (PARAMWIRE: with the
    parameter set `fit` applied to the photon strength and the residuals' `Params`), `energies` is
    required (nothing can ask a dump which energies exist), and `Ecomp` is the port's own.
    `enincmax_mev` is the run's highest incident energy; it fixes the emission grid and defaults
    to `max(energies)`. `direct_grid` is the energy axis T12/T13's direct calculation belongs to,
    which is the WHOLE run's pre-equilibrium energy list even when `energies` is the subset this
    call computes (SPEEDP); it defaults to `energies`. Everything else -- the grids, the masks, the levels, `esurf`, `wfac` --
    is identical in the two arms, which is the point: the A/B isolates the inputs.

    TALYS: preeq.f90:1 (preeq)
    Test: A-pe
    """
    from physics.hf.preeq import chain as PC

    Z, A, options, params, m = _structure(target)
    if chained:
        if not energies:
            raise ValueError("prepare(chained=True) needs the declared incident energy grid")
        ecomp_from_dump = False
    c = talys_constants()
    k0 = options.k0
    parskip = (False,) * 7
    energies = energies or energies_for(target, variant)
    C = len(energies)

    s0 = [float(m.s_mev[0, 0, t]) for t in range(7)]
    enincmax = float(enincmax_mev) if enincmax_mev is not None else max(energies)
    elimit = emission_limit(enincmax, s0[k0], 0.0)
    eg, maxen = egrid_values(elimit, options.segment, NUMEN, options.flagequispec, None)
    de, etop, ebot = emission_bins(eg, maxen)
    coulbar = coulomb_barriers(options)
    ebegin, _ = charged_particle_begin(
        eg, maxen, A, {t: coulbar[t] for t in range(7)}, {t: parskip[t] for t in range(7)}
    )

    E = maxen + 1
    xsreac = np.zeros((C, 7, E))
    if chained:
        xsreac[:, 0, : maxen + 1] = PC.chained_photoabsorption(Z, A, eg, maxen, energies, fit)
        inv = PC.inverse_reaction_xs(Z, A, enincmax)
        for t in range(1, 7):
            xsreac[:, t, :] = inv[t][:E]
    else:
        xsreac[:, 0, : maxen + 1] = _photoabsorption(target, variant, eg, maxen, energies)
        for t in range(1, 7):
            col = "reaction"
            rows = _xsreac_rows(target, variant, PARSYM[t], col)
            b = ebegin[t]
            k = min(len(rows), E - b)
            xsreac[:, t, b : b + k] = rows[:k]
        # Nothing above `eendmax(type)`: `inverse` fills xsreac only over
        # [ebegin, eendmax] (inverseecis.f90:402), and `eend(type)` of a *lower* incident
        # energy can reach past it -- TALYS then reads a zero there. Padding with the last
        # value instead makes `knockout`'s `sigav = xsreac(type2, eend(type2))` (knockout.f90:124)
        # finite where TALYS has 0, which inflates denomki and shrinks the alpha knockout ~25x.

    # per-nucleus pairing energy, from the ld*.gs headers of the residuals
    pair = np.zeros(7)
    gp_res = np.zeros(7)
    gn_res = np.zeros(7)
    if chained and fit:
        from physics.hf.density.overrides import aadjust_entries, with_aadjust

        pparams = with_aadjust(params, options, aadjust_entries(fit))
    else:
        pparams = params
    for t in range(7):
        Zr, Ar = Z - c["parZ"][t], A + 1 - c["parA"][t]
        pair[t] = (PC.chained_pairing(Zr, Ar, options, pparams, m) if chained
                   else _pairing_energy(target, variant, Zr, Ar, options, params, m))
        _, gp_res[t], gn_res[t] = single_particle_densities(Zr, Ar - Zr, float(params.at("kph")))

    ecomp = np.zeros(C)
    emask = np.zeros((C, 7, E), dtype=bool)
    for i, e in enumerate(energies):
        eninccm, _ = incident_kinematics(
            e,
            k0,
            float(m.mass_amu[0, 1]),
            float(m.specmass[c["parZ"][k0], c["parN"][k0], k0]),
            float(m.redumass_amu[c["parZ"][k0], c["parN"][k0], k0]),
            options.flagrel,
        )
        ecomp[i] = total_energy(eninccm, s0[k0], 0.0)
        eend, _ = emission_end(
            eg,
            maxen,
            ecomp[i],
            {t: s0[t] for t in range(7)},
            ebegin,
            {t: parskip[t] for t in range(7)},
        )
        for t in range(7):
            emask[i, t, ebegin[t] : min(eend[t], maxen) + 1] = True

    # --- discrete levels of each residual, for preeqcorrect/preeqtotal
    lev = {}
    for t in range(7):
        Zr, Ar = Z - c["parZ"][t], A + 1 - c["parA"][t]
        lev[t] = discrete_levels(Zr, Ar, options, m, params)
    nlast = tuple(int(lev[t].nlev) for t in range(7))
    edis = {t: lev[t].e_mev[: nlast[t] + 1].numpy().astype(float) for t in range(7)}
    dgrid = tuple(direct_grid) if direct_grid else tuple(energies)
    dirdisc = (PC.chained_direct_discrete(Z, A, tuple(energies), k0, nlast, grid=dgrid) if chained
               else _direct_discrete(target, variant, energies, k0, nlast))
    eoutdis_all, nendisc_all, eend_all = [], [], []
    for i in range(C):
        eend, _ = emission_end(
            eg,
            maxen,
            ecomp[i],
            {t: s0[t] for t in range(7)},
            ebegin,
            {t: parskip[t] for t in range(7)},
        )
        nd, eo = discrete_emission_begin(
            ebot,
            ecomp[i],
            {t: s0[t] for t in range(7)},
            edis,
            {t: nlast[t] for t in range(7)},
            ebegin,
            eend,
            {t: parskip[t] for t in range(7)},
        )
        eoutdis_all.append([eo.get(t) for t in range(7)])
        nendisc_all.append([nd[t] for t in range(7)])
        eend_all.append([eend[t] for t in range(7)])
    disc = DiscreteInputs(
        eoutdis_mev=eoutdis_all,
        nendisc=nendisc_all,
        nlast=nlast,
        xsdirdisc_mb=dirdisc,
        etop_mev=torch.tensor(etop[:E], dtype=DTYPE).expand(C, E).contiguous(),
        ebegin=tuple(ebegin[t] for t in range(7)),
        eend=eend_all,
    )

    hdr = {}
    if ecomp_from_dump:
        ec = []
        for e in energies:
            md = _meta_of("exciton", target, f"exciton{e:08.3f}.out", variant)
            ec.append(float(str(md["E-compound [MeV]"]).split()[0]))
            hdr.setdefault("esurf_dump", []).append(
                float(str(md["Surface effective well depth [MeV]"]).split()[0])
            )
        hdr["ecomp_port"] = ecomp.copy()
        ecomp = np.array(ec)

    t_ = lambda x: torch.tensor(np.asarray(x), dtype=DTYPE)  # noqa: E731
    einc = t_(energies)
    _, gp_cn, gn_cn = single_particle_densities(Z, A + 1 - Z, float(params.at("kph")))
    inp = PreeqInputs(
        Z=Z,
        A=A,
        k0=k0,
        einc_mev=einc,
        ecomp_mev=t_(ecomp),
        esurf_mev=esurf(options, params, k0, einc, A + 1),
        egrid_mev=t_(eg[:E]).expand(C, E).contiguous(),
        deltae_mev=t_(de[:E]).expand(C, E).contiguous(),
        emask=torch.tensor(emask),
        xsreac_mb=t_(xsreac),
        s_mev=t_(s0).expand(C, 7).contiguous(),
        wfac=t_(wfac(m, options, parskip)).expand(C, 7).contiguous(),
        gp_cn=torch.full((C,), gp_cn, dtype=DTYPE),
        gn_cn=torch.full((C,), gn_cn, dtype=DTYPE),
        pair_cn_mev=torch.full((C,), float(pair[0]), dtype=DTYPE),
        gp_res=t_(gp_res).expand(C, 7).contiguous(),
        gn_res=t_(gn_res).expand(C, 7).contiguous(),
        pair_res_mev=t_(pair).expand(C, 7).contiguous(),
        xsflux_mb=t_(PC.chained_flux(Z, A, tuple(energies), grid=dgrid) if chained
                     else _flux(target, variant, energies)),
        a_init=A + 1,
        nbins=number_of_bins(enincmax, options.nbins0),
        primary=True,
    )
    hdr["energies"] = energies
    hdr["ebegin"] = ebegin
    hdr["maxen"] = maxen
    hdr["discrete"] = disc
    hdr["levels"] = lev
    hdr["options"] = options
    hdr["params"] = params
    return inp, hdr
