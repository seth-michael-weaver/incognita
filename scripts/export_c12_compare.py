"""Export the comparison layer of the C-12 Elastic tab (Every nuclide page) to data/light_evals/cmp/C12RM9.json.

What it writes (all display data; scripts/add_light_evals.py copies it into docs/walkthrough/data/n/6/12.json as rm.cmp):
  natc   INCOGNITA's frozen C-12 R-matrix curve composed to natural carbon, natC = 0.9893 sigma_C12(ours) + 0.0107 sigma_C13,
         where the C-13 part (1.07 %) is ENDF/B-VIII.1 n-006_C_013 MT2 -- the composition the fixed-in-advance checks used
         (gate_rm9.natc_fn). The site labels it as such; the pure C-12 curve stays in data/light_evals/C12RM9.json.
  endf   ENDF/B-VIII.1 natC elastic on the same grid (gate_rm9.natc_fn(b81el)): a COMPARATOR, drawn by the page only when
         the evaluated-library overlay is ticked, never used by INCOGNITA and not in the downloads.
  ds/ho  the unfitted validation natC total cross sections (EXFOR 13759004, 13761002, 13761003, 22610002; 1,742 points, read once
         after the fit was frozen), exactly as the check read them (gate_rm9.heldout_tot: sets over 300 points rebinned 1 %).
  bins   the same points averaged in log-energy bins (mean, standard error), the bins of the evaluator figure extended
         down with the same ratio to cover 10 eV.
  std    the IAEA neutron standard 2017 natC elastic points 1e-5 eV - 1.8 MeV with their 1 sigma (gate_rm9.std_setup) and
         INCOGNITA natC / standard - 1 at each.
  stats  max |dev| and max |z| against the standard, validation chi2/N (gate_rm9.g3), and the offset of each validation set
         against INCOGNITA and ENDF/B-VIII.1.

Needs inputs that are not part of this repository (the frozen fit, the R-matrix toolkit, ENDF files):
  nice -n 10 python scripts/export_c12_compare.py
"""
import json, os, re, sys

CARD = os.path.expanduser("~/nucleus/research/rl/c12rm9")
sys.path.insert(0, os.path.join(CARD, "code"))
import numpy as np  # noqa: E402
import gate_rm9 as G  # noqa: E402
import c12_5  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTF = os.path.join(ROOT, "data", "light_evals", "cmp", "C12RM9.json")
g5 = lambda v: float(f"{float(v):.5g}")


def main():
    S, _ = c12_5.load(os.path.join(CARD, "out", "real", "real_c12_a4.0.json"))
    sig12, _ = c12_5.model_fns(S)
    ours = G.natc_fn(sig12)
    b81el, _, s13 = G.b81_fns()
    b81 = G.natc_fn(b81el)
    # grid (MeV): log-spaced over the whole range, dense across the 153 keV C-13 resonance
    E = np.unique(np.concatenate([np.geomspace(1e-11, 1.8, 360), np.linspace(0.135, 0.175, 161)]))
    natc, endf = ours(E), b81(E)
    # pure C-12 check: the site curve (C12RM9.json) is sigma_C12 alone
    ev = json.load(open(os.path.join(ROOT, "data", "light_evals", "C12RM9.json"), encoding="utf-8"))
    e12 = np.asarray(ev["energy_ev"]) / 1e6
    pure = float(np.max(np.abs(sig12(e12) / np.asarray(ev["sigma_b"]) - 1)))
    assert pure < 1e-4, pure

    sets = G.heldout_tot(os.path.join(CARD, "code", "draws", "c12_heldout_draw12.json"), S)
    mods, refs = G.tot_models(S, sets)
    g3 = G.g3(S, sets)
    ds, ho, off = [], [], {}
    for i, d in enumerate(sets):
        sid = str(d.sid)
        lab = re.sub(r"\s+\d{4}\s+\d+$", "", str(getattr(d, "label", "") or "")).replace(",", ", ").replace(",  ", ", ")   # "J.A.Harvey,D.C.Larson 1974 13759004" -> authors
        ds.append([f"{sid[:5]}/{sid}/", lab, int(d.year) if getattr(d, "year", None) else None, "natC"])
        fb = int(d.meta.get("dy_missing_fallback") or 0) > 0   # the set gives no uncertainty: the check's fallback is not shown
        dy = np.asarray(d.dy, float)
        for x, y, u in zip(d.Elab, d.y, dy):
            ho.append([g5(x * 1e6), g5(y), None if fb or not (u > 0) else g5(u / y), i])
        m, b = np.asarray(mods[i], float), np.asarray(refs[i], float)
        off[sid] = dict(vs_incognita_pct=round(float(np.mean(d.y / m) - 1) * 100, 2), vs_endf_pct=round(float(np.mean(d.y / b) - 1) * 100, 2), n=int(len(d.y)))
    Ex = np.concatenate([d.Elab for d in sets]); Yx = np.concatenate([d.y for d in sets])
    r = (1.8 / 1e-3) ** (1 / 25)                     # the evaluator figure's bins (1 keV - 1.8 MeV, 25 bins), extended down
    edges = 1e-3 * r ** np.arange(-16, 26)
    k = np.digitize(Ex, edges); bins = []
    for j in range(1, len(edges)):
        w = k == j
        if w.sum() >= 5:
            bins.append([g5(np.exp(np.mean(np.log(Ex[w]))) * 1e6), g5(np.mean(Yx[w])), g5(np.std(Yx[w]) / np.sqrt(w.sum())), int(w.sum())])

    st = G.std_setup()
    t = st["t1"][st["m"]]; Es, Ss, dcs = t[:, 0], t[:, 1], st["dcs"]
    dev = ours(Es) / Ss - 1; devb = b81(Es) / Ss - 1
    std = [[g5(e * 1e6), g5(s), g5(c * s), round(float(v), 6)] for e, s, c, v in zip(Es, Ss, dcs, dev)]
    stats = dict(std_max_dev_pct=round(float(np.max(np.abs(dev))) * 100, 2), std_max_z=round(float(np.max(np.abs(dev / dcs))), 2),
                 endf_std_max_dev_pct=round(float(np.max(np.abs(devb))) * 100, 2),
                 heldout_chi2=round(float(g3["chi2"]), 1), heldout_n=int(g3["N"]), heldout_chi2n=round(float(g3["chi2N"]), 2),
                 heldout_pass=bool(g3["pass_"]), offsets=off, pure_c12_check=pure)
    out = dict(id="C12RM9", what="comparison layer of the C-12 elastic tab; see scripts/export_c12_compare.py",
               natc_note="natC = 0.9893 x INCOGNITA C-12 (C12RM9) + 0.0107 x ENDF/B-VIII.1 C-13 elastic (MT2), 0 K",
               endf_note="ENDF/B-VIII.1 natC elastic (0.9893 C-12 + 0.0107 C-13, MT2, 0 K): comparator only, not used by INCOGNITA",
               e_ev=[g5(x * 1e6) for x in E], natc_b=[g5(v) for v in natc], endf_b=[g5(v) for v in endf],
               ds=ds, ho=ho, bins=bins, std=std, stats=stats)
    os.makedirs(os.path.dirname(OUTF), exist_ok=True)
    with open(OUTF, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, separators=(",", ":"))
    print(json.dumps(dict(stats, ds=ds, n_ho=len(ho), n_bins=len(bins), n_std=len(std), n_grid=len(E)), indent=1))


if __name__ == "__main__":
    main()
