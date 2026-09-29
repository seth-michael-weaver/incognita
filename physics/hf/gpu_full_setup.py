"""The CPU half of `gpu_full`: everything one dump-free run computes that does NOT depend on a
population, per (nuclide, incident energy), as plain numpy arrays.

Task: GPUFULL (the full dump-free cascade on a (nuclide, energy) GPU batch axis). No physics of
its own: every array is the output of a statement `engine.ChainedFull.cases` runs, called in the
same order on the same objects, stopped before the first number that reads a population.

**The split.** Set-up (here, on CPU, once per nuclide) is the run's STRUCTURE and TABLES:

* the run grid (`egrid`, `ebegin`, `eendmax`) and T5's emission-grid transmission tables
  `Tjl`/`Tl`/`lmax` (one set for the whole cascade, `flagompall` false);
* per incident energy: the incident channel (`Tjlinc`, sigma_reac, shape elastic), compnorm's
  `CNfactor`/`J2beg`/`J2end`, T8/T12's addends, `_BuiltInputs.shell`'s direct-discrete and
  pre-equilibrium totals, `population.f90`'s `preeqpopex`, the binary grids' `ald`/`spincut`;
* per incident energy, every cascade nucleus `exgrid` builds (`Cascade.spec`): its excitation
  grid, `maxJ`, `rhogrid`, discrete levels, branching ratios, separation energies, and the
  cascade tree (`Cascade.populations`), with `nexmax(type)` of every decayable mother bin;
* the photon transmissions `Tgam = 2 pi Egamma^(2l+1) f(Efs, Egamma) Fnorm` of the primary decay
  and of every decayable mother bin (T7's strength function stays on CPU);
* at `Einc >= emulpre` the particle-hole half of `multipreeq2` (its flux never reads a compound
  population; see `_mpe_walk`).

What `gpu_full` computes from these, on the batch axis, is everything that reads or writes a
population: densprepare's interpolated `Tjlnex`/`Tlnex` and `rho0`, the width sums, comptarget with
Moldauer width fluctuations, binary, the multiple-emission cascade with its popeps gates and gamma
cascades, and channels.f90's exclusive channels.

Test: GPUFULL / tests/hf/test_gpu_full.py
"""

from __future__ import annotations

import time
from types import SimpleNamespace

import numpy as np
import torch

from physics.hf.compound.prepare import NUMJ
from physics.hf.core.tensors import DTYPE

PARZ = (0, 0, 1, 1, 1, 2, 2)
PARN = (0, 1, 0, 1, 2, 1, 2)


def _f(x) -> float:
    return float(x.detach()) if isinstance(x, torch.Tensor) else float(x)


def _np(x, dtype=np.float64):
    if isinstance(x, torch.Tensor):
        x = x.detach().numpy()
    return np.asarray(x, dtype=dtype)


def _spec_record(cas, sp) -> dict:
    """One `NucleusSpec` as arrays, with densprepare's `discfactor` resolved."""
    from physics.hf.compound.prepare import _discfactor

    n = sp.maxex + 1
    rg = np.asarray(sp.rhogrid, dtype=np.float64)[:n]
    nz = np.flatnonzero(rg.any(axis=(0, 2)))
    jx = int(nz[-1]) + 1 if nz.size else 1
    br_k, br_r = [], []
    for k in range(n):
        rows = sp.branch.get(k, [])
        br_k.append([int(a) for a, _ in rows])
        br_r.append([float(b) for _, b in rows])
    nbr = max([len(x) for x in br_k] + [1])
    bk = np.full((n, nbr), -1, dtype=np.int64)
    bv = np.zeros((n, nbr))
    for k in range(n):
        bk[k, : len(br_k[k])] = br_k[k]
        bv[k, : len(br_r[k])] = br_r[k]
    df = _discfactor(SimpleNamespace(nlast=sp.nlast, ntop=sp.ntop, ncum_nl=sp.ncum_nl))
    return dict(
        Z=int(sp.Z), A=int(sp.A), zix=int(sp.zix), nix=int(sp.nix), maxex=int(sp.maxex),
        nlast=int(sp.nlast), nlast_grid=int(sp.nlast_grid), ntop=int(sp.ntop),
        discfactor=_f(df), exmax=float(sp.exmax_mev),
        ex=np.asarray(sp.ex_mev, dtype=np.float64)[:n].copy(),
        dex=np.asarray(sp.dex_mev, dtype=np.float64)[:n].copy(),
        maxj=np.asarray(sp.maxj, dtype=np.int64)[:n].copy(),
        parlev=np.asarray(sp.parlev, dtype=np.int64)[:n].copy(),
        jdis=np.asarray(sp.jdis, dtype=np.float64)[:n].copy(),
        tau=np.asarray(sp.tau_s, dtype=np.float64)[:n].copy(),
        rhogrid=np.ascontiguousarray(rg[:, :jx]), br_k=bk, br_r=bv,
        sep=np.array([float(sp.sep_mev[t]) for t in range(7)]))


def _decayable_bins(sp) -> list[int]:
    smin = sp.sep_mev.get(1, 0.0)
    return [b for b in range(sp.maxex, 0, -1)
            if not (b <= sp.nlast_grid and float(sp.ex_mev[b]) <= smin)]


def _nucleus_record(cas, st, sp) -> dict:
    """The decayable mother bins of one cascade nucleus: `nexmax(type)` and the photon exit's
    transmissions, as `compound.decay_fast.NucleusWidths` builds them for its whole nucleus."""
    from physics.hf.compound.decay_fast import NucleusWidths, _Geometry, nexmax_rows

    bins = _decayable_bins(sp)
    rec = dict(key=(sp.zix, sp.nix), bins=np.array(bins, dtype=np.int64),
               fnorm=np.asarray(cas.fisom(sp.zix, sp.nix, st), dtype=np.float64))
    daughters = [cas.spec(st, sp.zix + PARZ[t], sp.nix + PARN[t]) for t in range(7)]
    rec["daughters"] = [(d.zix, d.nix) for d in daughters]
    if not bins:
        rec["nxm"] = np.zeros((0, 7), dtype=np.int64)
        rec["tg"] = dict(shape=(0, 0, 0), flat=np.zeros(0))
        return rec
    barr = np.asarray(bins, dtype=np.int64)
    nxm = nexmax_rows(cas, st, sp, barr)
    rec["nxm"] = nxm
    exinc = np.asarray(sp.ex_mev, dtype=np.float64)[barr]
    dexinc = np.asarray(sp.dex_mev, dtype=np.float64)[barr]
    sep = np.array([sp.sep_mev[t] for t in range(7)])
    g = _Geometry(exinc, dexinc, nxm, daughters, sep)
    T0, T1 = NucleusWidths._photon(None, cas, st, sp, g, exinc, rec["fnorm"])
    # T0[.., l] = Tgam(l, irad = 1 - l%2), T1[.., l] = Tgam(l, irad = l%2): keep the (l, c) pair
    rec["tg"] = pack_tg(np.stack([T0, T1], axis=1), barr)  # (m, 2, n0, Lc) packed
    return rec


def pack_tg(tg: np.ndarray, bins: np.ndarray) -> dict:
    """The photon exit's (bin, c, row, l') transmissions stored on their support only: rows below
    the mother bin (a photon cannot reach a higher one, `nexmax(0) = nex - 1`) and l' >= 1
    (`fstrength` has no l' = 0). `unpack_tg` restores the dense array bit for bit."""
    m, _, n0, Lc = tg.shape
    if m == 0 or Lc == 0:
        return dict(shape=(m, n0, Lc), flat=np.zeros(0))
    mask = np.arange(n0)[None, :] < np.asarray(bins)[:, None]  # (m, n0)
    dense = tg.transpose(0, 2, 1, 3)  # (m, n0, 2, Lc)
    if np.any(dense[~mask]) or np.any(dense[..., 0]):
        raise ValueError("photon transmission outside its support")
    return dict(shape=(m, n0, Lc), flat=np.ascontiguousarray(dense[mask][:, :, 1:]).reshape(-1))


def unpack_tg(rec: dict, bins: np.ndarray) -> np.ndarray:
    m, n0, Lc = rec["shape"]
    out = np.zeros((m, n0, 2, Lc))
    if m == 0 or Lc <= 1:
        return out.transpose(0, 2, 1, 3)
    mask = np.arange(n0)[None, :] < np.asarray(bins)[:, None]
    sub = np.zeros((int(mask.sum()), 2, Lc))
    sub[:, :, 1:] = rec["flat"].reshape(-1, 2, Lc - 1)
    out[mask] = sub
    return out.transpose(0, 2, 1, 3)


def _mpe_walk(cas, st, nuclei: dict, etot: float, maxz: int, maxn: int) -> dict:
    """`multipreeq2` for every mother bin it reaches, run on the particle-hole chain alone.

    multiple.f90 calls multipreeq2 for a bin of a `mulpreZN` nucleus after the bin passed the
    popeps gates; what it computes from the bin's particle-hole population `xspopph2` never reads
    the compound population (`dmulti` does, and the decay ignores it: `Cascade.decay` passes
    Dmulti = 0 to the numpy path). The only coupling is WHICH bins run: this walk assumes every
    bin it reaches passes the gates, and `gpu_full` checks that assumption bin by bin and flags a
    run where it fails. The walk reproduces `_apply_mpe`'s particle-hole side exactly (the
    mother's `xspopph2` replaced, the daughters' accumulated, `mulpre` set on a daughter that
    received flux) in the nucleus and bin order of `multiple_emission`.

    TALYS: multipreeq2.f90:1 (multipreeq2), multiple.f90:549 (the call)
    Test: GPUFULL / tests/hf/test_gpu_full.py
    """
    out = {}
    for zc in range(maxz + 1):
        for nc in range(maxn + 1):
            nuc = nuclei.get((zc, nc))
            if nuc is None or nuc.skipcn:
                continue
            smin = nuc.sep_mev.get(1, 0.0)
            daughters = {t: nuclei[(zc + PARZ[t], nc + PARN[t])]
                         for t in range(7) if (zc + PARZ[t], nc + PARN[t]) in nuclei}
            for nex in range(nuc.maxex, 0, -1):
                if nex <= nuc.nlast and float(nuc.ex_mev[nex]) <= smin:
                    continue
                if not nuc.mulpre:
                    continue
                m = cas.mpe(st, nuclei, zc, nc, nex, etotal_mev=etot)
                if m is None:
                    continue
                rec = dict(summpe=float(m.summpe_mb), sumtype={}, term={}, add={})
                if m.ph_mother_mb is not None:
                    nuc.xspopph2_mb[nex] = m.ph_mother_mb
                for t, term in m.term_mb.items():
                    d = daughters.get(t)
                    if d is None:
                        continue
                    n = min(term.shape[0], d.xspop_mb.shape[0])
                    rec["term"][t] = _np(term)[:n].copy()
                    rec["add"][t] = _np(m.xspop_add_mb[t])[:n].copy()
                    rec["sumtype"][t] = float(m.sumtype_mb.get(t, 0.0))
                    if rec["sumtype"][t] != 0.0:
                        d.mulpre = True
                for (t, ipp, ihp, ipn, ihn), col in m.ph_add.items():
                    d = daughters.get(t)
                    if d is None:
                        continue
                    n = min(col.shape[0], d.xspop_mb.shape[0])
                    cn = _np(col)[:n]
                    for nexout in np.flatnonzero(cn).tolist():
                        cur = d.xspopph2_mb.get(nexout)
                        if cur is None:
                            p = m.ph_mother_mb.shape[0] - 1 if m.ph_mother_mb is not None else 6
                            cur = torch.zeros(p + 1, p + 1, p + 1, p + 1, dtype=DTYPE)
                            d.xspopph2_mb[nexout] = cur
                        a = cur.numpy()
                        a[ipp, ihp, ipn, ihn] = a[ipp, ihp, ipn, ihn] + cn[nexout]
                out[(zc, nc, nex)] = rec
    return out


def _binary_shell(built, nin: int, e: float, binp) -> dict:
    """What `binary` reads from `_BuiltInputs.shell` besides the populations."""
    grids = {}
    for t, g in binp.grids.items():
        grids[t] = dict(key=(g.zix, g.nix), maxex=int(g.maxex), nlast=int(g.nlast),
                        ald=_np(g.ald), spincut=_np(g.spincut),
                        xsdirdisc=_np(binp.xsdirdisc_mb[t]))
    return dict(
        grids=grids, ltarget=int(binp.ltarget), targetspin2=int(binp.targetspin2),
        target_parity=int(binp.target_parity), pespinmodel=int(binp.pespinmodel),
        maxjph=int(binp.maxjph), numj=int(binp.numj), popeps=float(binp.popeps_mb),
        xseps=float(binp.xseps_mb), xsreacinc=float(binp.xsreacinc_mb),
        xselasinc=float(binp.xselasinc_mb), xsdirdiscsum=float(binp.xsdirdiscsum_mb),
        xspreeqsum=float(binp.xspreeqsum_mb), xsgrsum=float(binp.xsgrsum_mb),
        xsracape=float(binp.xsracape_mb), flagpreeq=bool(binp.flagpreeq),
        xsdirdisctot=np.array([float(binp.xsdirdisctot_mb.get(t, 0.0)) for t in range(7)]),
        xspreeqtot=np.array([float(binp.xspreeqtot_mb.get(t, 0.0)) for t in range(7)]),
        xsgrtot=np.array([float(binp.xsgrtot_mb.get(t, 0.0)) for t in range(7)]))


def setup_nuclide(Z: int, A: int, declared: tuple[float, ...], cascade=None) -> dict:
    """Every population-independent array of one dump-free run over `declared` (module docstring).

    Mirrors `engine.ChainedFull.cases` with `inject=()`, `energies=None`, statement for statement
    up to `compound_inputs`, then the structure the cascade reads.

    `cascade`: a `Cascade` already built for this run, e.g. seeded from a CREC record
    (`record.caches.seed`), as `engine_c.run` takes it (GPUC); None builds a cold one.

    TALYS: talysreaction.f90:1 (talysreaction)
    Test: GPUFULL / tests/hf/test_gpu_full.py
    """
    from physics.hf.compound.chain import _NormView
    from physics.hf.compound.dens_reference import _eendmax, _to_updown_axis
    from physics.hf.compound.norm_reference import addends, chained_formation
    from physics.hf.compound.population import population
    from physics.hf.compound.prepare import DensPrepareInputs, _tgam_rows
    from physics.hf.emission.feed_reference import etotal_of, pop_inputs_of
    from physics.hf.emission.feeding import Cascade
    from physics.hf.engine import _BuiltInputs, _seed_mulpre
    from physics.hf.preeq.chain import lend_cascade, set_energy_subset, target_tag

    t0 = time.perf_counter()
    target = target_tag(Z, A)
    declared = tuple(float(np.float32(e)) for e in declared)
    enincmax = max(declared)
    e_axis = list(declared)
    cas = cascade if cascade is not None else Cascade(Z, A, enincmax, energies=declared)
    if (int(cas.Zt), int(cas.At), float(cas.enincmax), tuple(cas.energies)) != (
            Z, A, float(enincmax), tuple(declared)):
        raise ValueError("setup_nuclide(cascade=...) was built for another run")
    set_energy_subset(Z, A, declared, None)
    lend_cascade(cas)
    add = addends(target, Z, A, e_axis, declared)
    built = _BuiltInputs(cas, target, declared, add)
    sc = built.sc
    o = cas.options
    tr = [cas.trans[t] for t in range(1, 7)]
    L = max(x[0].shape[1] for x in tr)
    maxen = int(cas.rg.maxen)
    tjl = np.zeros((6, maxen + 1, L, 3))
    tl = np.zeros((6, maxen + 1, L))
    lmx = np.zeros((6, maxen + 1), dtype=np.int64)
    for i, (a, b, c) in enumerate(tr):
        a, b, c = _np(a), _np(b), _np(c, np.int64)
        tjl[i, : a.shape[0], : a.shape[1]] = a[: maxen + 1]
        tl[i, : b.shape[0], : b.shape[1]] = b[: maxen + 1]
        lmx[i, : c.shape[0]] = c[: maxen + 1]
    eendmax = _eendmax(Z, A, enincmax)
    run = dict(
        Z=Z, A=A, k0=int(cas.k0), declared=declared, enincmax=enincmax, gammax=int(o.gammax),
        wmode=int(o.wmode), wfcfactor=int(o.WFCfactor), transeps=float(cas.transeps),
        egrid=np.asarray(cas.rg.egrid, dtype=np.float64)[: maxen + 3].copy(), maxen=maxen,
        ebegin=np.array([int(cas.rg.ebegin[t]) for t in range(7)], dtype=np.int64),
        eendmax=np.array([int(eendmax[t]) for t in range(7)], dtype=np.int64),
        tjl=tjl, tl=tl, lmax=lmx, ewfc=float(cas.ewfc_mev), fiso=np.asarray(cas.fiso()),
        sc=dict(popeps=sc.popeps_mb, xseps=sc.xseps_mb, maxz=sc.maxz, maxn=sc.maxn,
                zinit=sc.zinit, ninit=sc.ninit, maxchannel=sc.maxchannel,
                parinclude=list(sc.parinclude), parskip=list(sc.parskip),
                targete=sc.targete_mev, ltarget=sc.ltarget, targetspin2=sc.targetspin2,
                target_parity=sc.target_parity, flagfission=bool(sc.flagfission),
                s_k0=float(cas.m.s_mev[0, 0, cas.k0])),
        E=[])
    for nin, e in enumerate(e_axis, start=1):
        binp, cinp = built.shell(nin, e)
        etot = etotal_of(Z, A, enincmax, binp.e_inc_mev, binp.k0)
        inc = cas.incident(binp.e_inc_mev)
        st = cas.new_energy(etot, lmaxinc=int(inc.lmax[0]), e_inc_mev=binp.e_inc_mev)
        cas.propagate_exmax(st, 0, 0)
        a = add[round(binp.e_inc_mev, 6)]
        # compound_inputs, without densprepare (gpu_full builds rho0/Tjlnex itself)
        cf, lmaxinc = chained_formation(cas, _NormView(binp), a)
        tjl_t = _to_updown_axis(inc.tjl_inc[0], cas.k0)[: lmaxinc + 1]
        rec = dict(
            e=float(binp.e_inc_mev), etot=float(etot), lmaxinc_st=int(st.lmaxinc),
            lmaxinc=int(lmaxinc), tjlinc=_np(tjl_t).copy(), cnfactor=_f(cf.cn_factor_mb),
            j2beg=int(cf.j2beg), j2end=int(cf.j2end),
            flagwidth=bool(binp.e_inc_mev <= cas.ewfc_mev), first_energy=bool(st.first_energy),
            sigma_reac=float(inc.sigma_reac_mb[0]))
        # primary_dens_inputs: the compound nucleus and the seven binary residuals
        sp0 = cas.spec(st, 0, 0)
        for t in range(7):
            cas.spec(st, PARZ[t], PARN[t])
        dpi = DensPrepareInputs(
            exinc_mev=float(etot), dexinc_mev=0.0, s_n_mev=sp0.sep_mev[1], gammax=o.gammax,
            lmaxinc=st.lmaxinc, k0=cas.k0, fnorm=cas.fiso(), residuals={}, trans={},
            gamma_strength=cas.gamma_strength(Z, A), primary=True, flagfullhf=False,
            transeps=cas.transeps, gamma_params=_default_gamma_params(Z, A))
        rec["tgam0"] = _tgam_rows(dpi, float(etot) - np.asarray(sp0.ex_mev[: sp0.maxex + 1],
                                                                 dtype=np.float64))
        rec["binary"] = _binary_shell(built, nin, e, binp)
        prq = population(pop_inputs_of(cas, binp, target, etot, add, declared))
        rec["pex"] = {t: _np(prq.preeqpopex_mb[t]).copy() for t in prq.preeqpopex_mb}
        # the cascade tree (cases(): populations, propagate_exmax over it, populations again)
        nuclei = cas.populations(st, cinp.maxz, cinp.maxn, {})
        for zc in range(cinp.maxz + 1):
            for nc in range(cinp.maxn + 1):
                if (zc, nc) in nuclei:
                    cas.propagate_exmax(st, zc, nc)
        nuclei = cas.populations(st, cinp.maxz, cinp.maxn, {})
        rec["static_reach"] = sorted(st.spec)
        order = [(zc, nc) for zc in range(cinp.maxz + 1) for nc in range(cinp.maxn + 1)
                 if (zc, nc) in nuclei]
        rec["nuclei"] = order
        rec["cascade"] = {k: _nucleus_record(cas, st, cas.spec(st, *k)) for k in order}
        rec["specs"] = {k: _spec_record(cas, sp) for k, sp in st.spec.items()}
        _seed_mulpre(nuclei, prq)
        rec["mulpre0"] = [k for k in order if nuclei[k].mulpre]
        rec["mpe"] = (_mpe_walk(cas, st, nuclei, float(etot), cinp.maxz, cinp.maxn)
                      if any(n.mulpre for n in nuclei.values()) else {})
        # a spec multipreeq2's inputs built (daughters of a mulpre nucleus) is structure too
        for k, sp in st.spec.items():
            if k not in rec["specs"]:
                rec["specs"][k] = _spec_record(cas, sp)
        rec["maxz"], rec["maxn"] = int(cinp.maxz), int(cinp.maxn)
        run["E"].append(rec)
    set_energy_subset(Z, A, declared, None)
    run["seconds"] = time.perf_counter() - t0
    return run


def _default_gamma_params(Zt: int, At: int):
    from physics.hf.compound.dens_reference import _gamma_parameters

    return _gamma_parameters(Zt, At)[0]


# ------------------------------------------------------------------------------ stacked layout

R_ROWS = 71  # numex's excitation rows (maxex <= 70 on the sweep grid)


def _mpe_spin_weights(Z: int, A: int) -> np.ndarray:
    """multipreeq2's `Jterm` weights 0.5 (2J + 1) RnJ(J) / RnJsum, as `preeq.mpe_fast` forms them:
    `xspop_add(t, nexout, J) = term(t, nexout) * w(J)` for J <= maxJ(daughter, nexout)."""
    from physics.hf.compound.dens_reference import structure_of
    from physics.hf.preeq.spin import preeq_spin_distribution

    o, p, _m = structure_of(Z, A, None)
    rnj = preeq_spin_distribution(o, p, A)
    v = _np(rnj["RnJ"][2])
    out = np.zeros(NUMJ + 1)
    out[: min(NUMJ + 1, v.size)] = v[: NUMJ + 1]
    return 0.5 * (2.0 * np.arange(NUMJ + 1) + 1.0) * out / _f(rnj["RnJsum"][2])


def stack_run(run: dict) -> None:
    """Add `e["st"]` to every energy record of `run`: its specs, cascade rows, photon
    transmissions and multiple pre-equilibrium records as stacked arrays (one array per field, a
    row per spec / nucleus / record), which is what `gpu_full_cascade.Bucket` concatenates. The
    numbers are the records', copied; `rhogrid` keeps only the spins a rho0 can reach
    (`gpu_full_cascade._rho_columns`) and `xspop_add` becomes `term x w`.

    Test: GPUFULL / tests/hf/test_gpu_full.py
    """
    from physics.hf.gpu_full_cascade import _rho_columns, _row_nj

    R = R_ROWS
    w = None
    for e in run["E"]:
        if "st" in e:
            continue
        skeys = sorted(e["specs"])
        sid = {k: i for i, k in enumerate(skeys)}
        S = len(skeys)
        s_int = np.zeros((S, 6), dtype=np.int64)
        s_f = np.zeros((S, 2))
        s_sep = np.zeros((S, 7))
        s_row = np.zeros((S, 4, R))
        s_rowi = np.zeros((S, 2, R), dtype=np.int64)
        rho, rho_off = [], np.zeros(S, dtype=np.int64)
        off = 0
        for i, k in enumerate(skeys):
            sp = e["specs"][k]
            n = sp["maxex"] + 1
            jx = min(_rho_columns(sp, R), sp["rhogrid"].shape[1])
            s_int[i] = (sp["maxex"], sp["nlast"], sp["nlast_grid"], sp["ntop"], sp["A"], jx)
            s_f[i] = (sp["discfactor"], sp["exmax"])
            s_sep[i] = sp["sep"]
            s_row[i, 0, :n], s_row[i, 1, :n] = sp["ex"], sp["dex"]
            s_row[i, 2, :n], s_row[i, 3, :n] = sp["jdis"], sp["tau"]
            s_rowi[i, 0, :n], s_rowi[i, 1, :n] = sp["maxj"], sp["parlev"]
            a = np.ascontiguousarray(sp["rhogrid"][:n, :jx])
            rho.append(a.reshape(-1))
            rho_off[i] = off
            off += a.size
        nuclei = [tuple(k) for k in e["nuclei"]]
        nid = {k: i for i, k in enumerate(nuclei)}
        Nn = len(nuclei)
        n_int = np.zeros((Nn, 8), dtype=np.int64)
        bins = np.zeros((Nn, R), dtype=np.int64)
        nxm = np.full((Nn, R, 7), -1, dtype=np.int64)
        fnorm = np.zeros((Nn, 8))
        dspec = np.zeros((Nn, 7), dtype=np.int64)
        drow = np.full((Nn, 7), -1, dtype=np.int64)
        nlb = max([e["specs"][k]["br_k"].shape[0] for k in nuclei] + [1])
        nb = max([e["specs"][k]["br_k"].shape[1] for k in nuclei] + [1])
        br_k = np.full((Nn, nlb, nb), -1, dtype=np.int64)
        br_r = np.zeros((Nn, nlb, nb))
        tg, tg_off = [], np.zeros(Nn, dtype=np.int64)
        tg_shape = np.zeros((Nn, 3), dtype=np.int64)
        toff = 0
        for j, k in enumerate(nuclei):
            sp = e["specs"][k]
            c = e["cascade"][k]
            m = len(c["bins"])
            n_int[j] = (sid[k], m, _row_nj(sp, c["bins"]), k[0] + k[1], sp["A"] % 2, k[0], k[1],
                        0)
            bins[j, :m] = c["bins"]
            nxm[j, :m] = c["nxm"]
            fnorm[j] = c["fnorm"]
            for t in range(7):
                dk = tuple(c["daughters"][t])
                dspec[j, t] = sid[dk]
                drow[j, t] = nid.get(dk, -1)
            a, b_ = sp["br_k"], sp["br_r"]
            br_k[j, : a.shape[0], : a.shape[1]] = a
            br_r[j, : b_.shape[0], : b_.shape[1]] = b_
            tg_shape[j] = c["tg"]["shape"]
            tg_off[j] = toff
            tg.append(c["tg"]["flat"])
            toff += c["tg"]["flat"].size
        recs = list(e["mpe"].items())
        M = len(recs)
        m_int = np.zeros((M, 2), dtype=np.int64)
        m_term = np.zeros((M, 2, R))
        m_sum = np.zeros((M, 3))
        m_has = np.zeros((M, 2), dtype=bool)
        for q, ((zc, nc, nex), rec) in enumerate(recs):
            m_int[q] = (nid[(zc, nc)], nex)
            m_sum[q, 2] = rec["summpe"]
            for t, term in rec["term"].items():
                m_term[q, t - 1, : len(term)] = term
                m_sum[q, t - 1] = rec["sumtype"][t]
                m_has[q, t - 1] = True
        if M and w is None:
            w = _mpe_spin_weights(run["Z"], run["A"])
        e["st"] = dict(
            S=S, s_int=s_int, s_f=s_f, s_sep=s_sep, s_row=s_row, s_rowi=s_rowi,
            rho=np.concatenate(rho) if rho else np.zeros(0), rho_off=rho_off, skeys=skeys,
            static=np.array([sid[tuple(k)] for k in e["static_reach"]], dtype=np.int64),
            Nn=Nn, n_int=n_int, bins=bins, nxm=nxm, fnorm=fnorm, dspec=dspec, drow=drow,
            br_k=br_k, br_r=br_r, tg=np.concatenate(tg) if tg else np.zeros(0), tg_off=tg_off,
            tg_shape=tg_shape, M=M, m_int=m_int, m_term=m_term, m_sum=m_sum, m_has=m_has,
            mpe_w=(w if M else np.zeros(NUMJ + 1)))
