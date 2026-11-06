/* Spent fuel, nuclide by nuclide (idea from a reader, Niels Harkson). One tonne of PWR UO2 fuel (4.2 % U-235, 50 GWd/t),
 * decayed nuclide by nuclide with proper chains, from 1 to 10^6 years. Everything on the canvas is COMPUTED here, in this file.
 *
 * INVENTORY (per tonne of initial heavy metal)
 *   Actinides and long-lived fission products: OECD-NEA (1999), "Actinide and Fission Product Partitioning and Transmutation:
 *   Status and Assessment Report", Annex E (data CEA/DRN/SPRC), Tables E.2 and E.6: UOX 4.2 %, 50.05 GWd/tHM, four years
 *   after discharge: Pu 12.00 kg (Pu-238 3.5 %, Pu-239 51.9 %, Pu-240 23.8 %, Pu-241 12.9 %, Pu-242 7.9 %); Np 0.72 kg
 *   (taken as all Np-237); Am 0.66 kg (Am-241 58.1 %, Am-242m 0.2 %, Am-243 41.7 %); Cm 0.11 kg (Cm-243 0.8 %, Cm-244
 *   91.2 %, Cm-245 6.5 %, Cm-246 1.5 %); U 935 kg; fission products 51.3 kg, of which Tc-99 1.2 kg, I-129 0.26 kg,
 *   Zr-93 1.05 kg, Cs-135 0.59 kg, Pd-107 0.34 kg, Sn-126 0.03 kg, Se-79 0.007 kg. (The PDF's text layer is scrambled;
 *   these column assignments are the ones whose sums reproduce the table's own totals at 33 and 41.2 GWd/t.)
 *   The uranium split is a typical one, not from that table: U-235 7.5 kg, U-236 5.5 kg, U-234 0.20 kg, rest U-238.
 *   Cs-137, Sr-90 and Pm-147 are computed from the burnup: 50 GWd/t at 200 MeV per fission = 1.35e26 fissions; fissions
 *   split U-235 58 % / Pu-239 30 % / U-238 8 % / Pu-241 4 % (an assumed typical split); cumulative yields (ENDF/B-VII.1,
 *   thermal; U-238 fast) Cs-137 6.19 / 6.59 / 6.0 / 6.7 %, Sr-90 5.78 / 2.10 / 3.2 / 1.6 %, Pm-147 2.25 / 2.04 / 2.5 /
 *   2.3 %; constant power over 3.6 full-power years. Result at unloading: Cs-137 1.86 kg (6.0e15 Bq), Sr-90 0.83 kg
 *   (4.2e15 Bq), Pm-147 1.6e16 Bq (constant power overstates short-lived nuclides a little).
 *   Other short-lived fission products (Cs-134, Ce-144, Ru-106, Sb-125, Eu-154, Eu-155, Kr-85): their activity ratio to
 *   Cs-137 at 5 years in an ORIGEN calculation for 50 GWd/MTU PWR fuel (L. Sowko 2017, "Hypothetical Case and Scenario
 *   Description for International Transportation of Spent Nuclear Fuel", OSTI 1414893, Appendix C Table 7), scaled to the
 *   Cs-137 above. Activation products in cladding and structure (Co-60, C-14, Ni-63 ...) are not included: fuel only.
 *   The clock starts at unloading: the 4-year table is decayed backwards to t = 0 with the same chains (exact for the
 *   nuclides listed; Cm-242, 163 d, is not in the table and is left out; it matters only in the first year or two).
 *   At unloading this gives Pu-241 1.88 kg, Am-241 0.053 kg, Cm-244 0.117 kg, Pu-238 0.43 kg.
 *
 * DECAY: Bateman solution summed over every linear path of the chains below (branchings split into paths). Half-lives from
 *   ENSDF (NNDC NuDat 3). Chains: Pu-241 -> Am-241 -> Np-237 (-> Pa-233) -> U-233 -> Th-229; Cm-244 -> Pu-240 -> U-236;
 *   Cm-243 -> Pu-239; Cm-245 -> Pu-241; Cm-246 -> Pu-242 -> U-238; Am-243 (-> Np-239) -> Pu-239 -> U-235 (-> Th-231) ->
 *   Pa-231 -> Ac-227; Am-242m -> (Am-242 -> Cm-242 82.3 %) -> Pu-238, (17.2 %) -> Pu-242; Pu-238 -> U-234 -> Th-230 ->
 *   Ra-226 -> Pb-210; U-238 (-> Th-234, Pa-234m) -> U-234. Daughters in brackets live days or less and are folded into
 *   their parent in secular equilibrium (their activity and dose added at the parent's rate). Likewise Ra-226 carries
 *   Rn-222, Po-218, Pb-214, Bi-214, Po-214; Pb-210 carries Bi-210 and Po-210; Th-229 carries Ra-225, Ac-225, Fr-221,
 *   At-217, Bi-213, Po-213, Pb-209; Ac-227 carries Th-227 (Fr-223), Ra-223, Rn-219, Po-215, Pb-211, Bi-211, Tl-207;
 *   Sr-90 carries Y-90; Cs-137 carries Ba-137m (94.4 %); Ce-144 Pr-144; Ru-106 Rh-106; Zr-93 Nb-93m; Sn-126 Sb-126m/Sb-126.
 * RADIOTOXICITY = sum over nuclides of activity x ICRP-72 adult ingestion dose coefficient e(50) (Sv/Bq), with the
 *   equilibrium daughters above added as separate ingested nuclides (as the NEA radiotoxicity curves do). Gases (Kr-85,
 *   Rn) get no ingestion dose. Coefficients used: Sr-90 2.8e-8, Y-90 2.7e-9, Cs-137 1.3e-8, Cs-134 1.9e-8, Tc-99 6.4e-10,
 *   I-129 1.1e-7, Ce-144 5.2e-9, Ru-106 7.0e-9, Pm-147 2.6e-10, U-234 4.9e-8, U-235 4.7e-8, U-238 4.5e-8, Np-237 1.1e-7,
 *   Pu-238 2.3e-7, Pu-239/240 2.5e-7, Pu-241 4.8e-9, Pu-242 2.4e-7, Am-241/243 2.0e-7, Cm-244 1.2e-7, Th-230 2.1e-7,
 *   Ra-226 2.8e-7, Pb-210 6.9e-7, Po-210 1.2e-6, Pa-231 7.1e-7, Ac-227 1.1e-6, Th-229 4.9e-7 (full list in NUC below).
 * THE ORE: natural uranium needed for this tonne = (4.2 - 0.25) / (0.711 - 0.25) = 8.57 t (0.25 % tails), with ALL its
 *   decay daughters in secular equilibrium (the whole U-238 series to Po-210 and the U-235 series to Tl-207), as in the
 *   NEA curves ("natural uranium and decay products as occurs in natural uranium ore"; the uranium only, no rock).
 *   Computed: 2.7e5 Sv (ingestion) and 1.5e12 Bq.
 * SEPARATION (steps 4-5): reprocessing at 4 years (when the inventory above is given) takes out a fraction of the
 *   plutonium, with the uranium (it leaves with the plutonium), and/or of the minor actinides Np + Am + Cm. Whatever is
 *   taken out is assumed burned elsewhere; only what is left behind is followed here.
 * RESULTS (computed, radiotoxicity): once-through below the ore after ~230 000 years (then mostly Pb-210 + Po-210, grown
 *   from Pu-238 via U-234, Th-230, Ra-226); Pu removed 99.9 %: ~13 000 y (Am-243, Pu-239, Pu-240); Pu and minor actinides
 *   99.9 %: ~290 y (Sr-90, Cs-137); 99 % each: ~680 y (Am-241). OECD-NEA (2011) "Potential Benefits and Impacts of
 *   Advanced Nuclear Fuel Cycles with Actinide Partitioning and Transmutation" (NEA No. 6894), section 2.1.1, gives
 *   ~250 000 y for 51 GWd/t fuel and 350-400 y with 0.1 % actinide losses. The Intermediate lesson "Spent fuel over time"
 *   (waste.js) draws an illustrative curve reaching the ore at ~150 000 y; the numbers here are the computed ones.
 * DRAWING: stacked areas; the top edge is the true total on a log scale, and the total's height is split among the
 *   nuclides in proportion to their share (band height = share of the total, not its own log value). */
(function () {
  const { clamp, lerp } = WT.util;
  const LN2 = Math.LN2, YR = 365.25 * 86400, NA = 6.02214e23;
  // [id, half-life (y), A, e Sv/Bq incl. folded daughters, decays per decay incl. folded daughters, band, group, children]
  const NUC = [
    ["Sr90", 28.79, 90, 2.8e-8 + 2.7e-9, 2, "sr", "fp", []],
    ["Cs137", 30.08, 137, 1.3e-8, 1.944, "cs", "fp", []],
    ["Tc99", 2.111e5, 99, 6.4e-10, 1, "tc", "fp", []],
    ["I129", 1.57e7, 129, 1.1e-7, 1, "i", "fp", []],
    ["Cs134", 2.065, 134, 1.9e-8, 1, "ofp", "fp", []],
    ["Ce144", 284.9 / 365.25, 144, 5.2e-9 + 5.0e-11, 2, "ofp", "fp", []],
    ["Ru106", 371.8 / 365.25, 106, 7.0e-9, 2, "ofp", "fp", []],
    ["Sb125", 2.759, 125, 1.1e-9 + 0.24 * 8.7e-10, 1.24, "ofp", "fp", []],
    ["Eu154", 8.601, 154, 2.0e-9, 1, "ofp", "fp", []],
    ["Eu155", 4.753, 155, 3.2e-10, 1, "ofp", "fp", []],
    ["Kr85", 10.739, 85, 0, 1, "ofp", "fp", []],
    ["Pm147", 2.6234, 147, 2.6e-10, 1, "ofp", "fp", []],
    ["Zr93", 1.61e6, 93, 1.1e-9 + 0.975 * 1.2e-10, 1.975, "ofp", "fp", []],
    ["Cs135", 2.3e6, 135, 2.0e-9, 1, "ofp", "fp", []],
    ["Se79", 3.27e5, 79, 2.9e-9, 1, "ofp", "fp", []],
    ["Sn126", 2.3e5, 126, 4.7e-9 + 3.6e-11 + 0.14 * 2.4e-9, 2.14, "ofp", "fp", []],
    ["Pd107", 6.5e6, 107, 3.7e-11, 1, "ofp", "fp", []],
    ["Cm246", 4706, 246, 2.1e-7, 1, "oa", "ma", [["Pu242", 1]]],
    ["Cm245", 8423, 245, 2.1e-7, 1, "oa", "ma", [["Pu241", 1]]],
    ["Cm244", 18.11, 244, 1.2e-7, 1, "cm", "ma", [["Pu240", 1]]],
    ["Cm243", 29.1, 243, 1.5e-7, 1, "oa", "ma", [["Pu239", 0.9971]]],
    ["Am243", 7364, 243, 2.0e-7 + 8.0e-10, 2, "am3", "ma", [["Pu239", 1]]],
    ["Am242m", 141, 242, 1.9e-7 + 0.9955 * 3.0e-10 + 0.823 * 1.2e-8, 2.82, "oa", "ma", [["Pu238", 0.823], ["Pu242", 0.172]]],
    ["Am241", 432.6, 241, 2.0e-7, 1, "am1", "ma", [["Np237", 1]]],
    ["Np237", 2.144e6, 237, 1.1e-7 + 8.7e-10, 2, "np", "ma", [["U233", 1]]],
    ["Pu241", 14.29, 241, 4.8e-9, 1, "pu1", "pu", [["Am241", 1]]],
    ["Pu242", 3.75e5, 242, 2.4e-7, 1, "pu2", "pu", [["U238", 1]]],
    ["Pu240", 6561, 240, 2.5e-7, 1, "pu0", "pu", [["U236", 1]]],
    ["Pu239", 24110, 239, 2.5e-7, 1, "pu9", "pu", [["U235", 1]]],
    ["Pu238", 87.7, 238, 2.3e-7, 1, "pu8", "pu", [["U234", 1]]],
    ["U238", 4.468e9, 238, 4.5e-8 + 3.4e-9, 3, "u", "pu", [["U234", 1]]],
    ["U236", 2.342e7, 236, 4.7e-8, 1, "u", "pu", []],
    ["U235", 7.04e8, 235, 4.7e-8 + 3.4e-10, 2, "u", "pu", [["Pa231", 1]]],
    ["U234", 2.455e5, 234, 4.9e-8, 1, "u", "pu", [["Th230", 1]]],
    ["U233", 1.592e5, 233, 5.1e-8, 1, "u", "pu", [["Th229", 1]]],
    ["Th229", 7932, 229, 4.9e-7 + 9.9e-8 + 2.4e-8 + 2.0e-10 + 5.7e-11, 8, "d", "pu", []],
    ["Th230", 7.538e4, 230, 2.1e-7, 1, "d", "pu", [["Ra226", 1]]],
    ["Ra226", 1600, 226, 2.8e-7 + 1.4e-10 + 1.1e-10, 6, "d", "pu", [["Pb210", 1]]],
    ["Pb210", 22.2, 210, 6.9e-7 + 1.3e-9 + 1.2e-6, 3, "d", "pu", []],
    ["Pa231", 3.276e4, 231, 7.1e-7, 1, "d", "pu", [["Ac227", 1]]],
    ["Ac227", 21.772, 227, 1.1e-6 + 0.9862 * 8.8e-9 + 0.0138 * 2.4e-9 + 1.0e-7 + 1.8e-10, 8, "d", "pu", []],
  ];
  const NAME = { Pb210: "Pb-210 + Po-210", Ra226: "Ra-226", Th230: "Th-230", Th229: "Th-229", Ac227: "Ac-227", Pa231: "Pa-231", Sr90: "Sr-90 + Y-90", Cs137: "Cs-137", Am242m: "Am-242m" };
  const nm = (id) => NAME[id] || id.replace(/^([A-Z][a-z]?)(\d+m?)$/, "$1-$2");
  // bands, bottom to top: [id, label, phone label, light colour, dark colour]
  const BANDS = [
    ["sr", "Sr-90 + Y-90", "Sr-90", "#e8823a", "#ff9b55"], ["cs", "Cs-137", "Cs-137", "#e3a21a", "#f5c04d"],
    ["ofp", "other fission products", "other FP", "#c9a77a", "#a98c66"], ["tc", "Tc-99", "Tc-99", "#9a5b2e", "#c98a5a"], ["i", "I-129", "I-129", "#6e4a2a", "#e0b48a"],
    ["pu8", "Pu-238", "Pu-238", "#1f4fbf", "#7f9bff"], ["pu1", "Pu-241", "Pu-241", "#a9c2f5", "#3d5aa8"], ["pu9", "Pu-239", "Pu-239", "#3a74e0", "#5d86f0"],
    ["pu0", "Pu-240", "Pu-240", "#7aa4ef", "#a9c0ff"], ["pu2", "Pu-242", "Pu-242", "#1d3270", "#c9d6ff"],
    ["am1", "Am-241", "Am-241", "#c2408f", "#f07cc0"], ["am3", "Am-243", "Am-243", "#e597c3", "#b85c94"], ["cm", "Cm-244", "Cm-244", "#d8483c", "#ff7e72"],
    ["oa", "other Am, Cm", "other Am, Cm", "#f0aaa2", "#a8574f"], ["np", "Np-237", "Np-237", "#8b5cf6", "#b392ff"],
    ["u", "uranium", "uranium", "#8b93a5", "#7d879a"], ["d", "decay daughters (Ra, Pb, Po, Th…)", "daughters", "#5f6b52", "#a3b38f"],
  ];
  const NB = BANDS.length, BI = {}; BANDS.forEach((b, i) => (BI[b[0]] = i));
  const ID = {}; NUC.forEach((n, i) => (ID[n[0]] = i));
  const lam = NUC.map((n) => LN2 / n[1]);
  const GR = { fp: 0, pu: 1, ma: 2 };
  // every linear decay path, with the product of its branchings
  const PATHS = [];
  (function dfs() { const go = (ch, w) => { PATHS.push({ ch: ch.slice(), w, s: ch[0], e: ch[ch.length - 1] }); for (const [c, b] of NUC[ch[ch.length - 1]][7]) { ch.push(ID[c]); go(ch, w * b); ch.pop(); } }; NUC.forEach((_, i) => go([i], 1)); })();
  PATHS.forEach((p) => { let pre = p.w; for (let i = 0; i < p.ch.length - 1; i++) pre *= lam[p.ch[i]]; p.pre = pre;
    p.den = p.ch.map((ci, i) => { let d = 1; p.ch.forEach((cj, j) => { if (j !== i) d *= lam[cj] - lam[ci]; }); return d; }); });
  const bate = (p, t) => { let s = 0; for (let i = 0; i < p.ch.length; i++) s += Math.exp(-lam[p.ch[i]] * t) / p.den[i]; return p.pre * s; };

  // ---------- inventory four years after unloading (atoms per tonne) ----------
  const N4 = new Float64Array(NUC.length), g2a = (k, g) => (g / NUC[ID[k]][2]) * NA;
  const G4 = { Pu238: 420, Pu239: 6228, Pu240: 2856, Pu241: 1548, Pu242: 948, Np237: 720, Am241: 383.5, Am242m: 1.32, Am243: 275.2,
    Cm243: 0.88, Cm244: 100.3, Cm245: 7.15, Cm246: 1.65, U234: 203, U235: 7500, U236: 5500, U238: 921797,
    Tc99: 1200, I129: 260, Zr93: 1050, Cs135: 590, Se79: 7, Sn126: 30, Pd107: 340 };
  for (const k in G4) N4[ID[k]] = g2a(k, G4[k]);
  { const FIS = 50e9 * 86400 / (200 * 1.602177e-13), TIRR = 3.6, SPL = [0.58, 0.30, 0.08, 0.04];
    const YLD = { Cs137: [6.19, 6.59, 6.0, 6.7], Sr90: [5.78, 2.10, 3.2, 1.6], Pm147: [2.25, 2.04, 2.5, 2.3] };
    const at0 = {}; for (const k in YLD) { const l = lam[ID[k]], y = YLD[k].reduce((s, v, i) => s + v * SPL[i], 0) / 100; at0[k] = (FIS / TIRR) * y * (1 - Math.exp(-l * TIRR)) / l; }
    const cs5 = at0.Cs137 * lam[ID.Cs137] * Math.exp(-lam[ID.Cs137] * 5); // activity (atoms/yr) at 5 years
    const SOW = { Cs134: 851.21, Ce144: 181.69, Ru106: 281.49, Sb125: 52.476, Eu154: 111.28, Eu155: 48.909, Kr85: 181.37 }; // TBq/assembly at 5 y, Cs-137 2389.1
    for (const k in SOW) { const l = lam[ID[k]]; at0[k] = (cs5 * SOW[k] / 2389.1) * Math.exp(l * 5) / l; }
    for (const k in at0) N4[ID[k]] = at0[k] * Math.exp(-lam[ID[k]] * 4); }
  /** per-nuclide atoms at time t (years after unloading), with separation factors kp, km (fraction left) applied at 4 y */
  function nucAt(t, kp, km) {
    const out = new Float64Array(NUC.length), dt = t - 4, sep = t >= 4;
    for (const p of PATHS) { const n0 = N4[p.s]; if (!n0) continue; const g = NUC[p.s][6], k = !sep || g === "fp" ? 1 : g === "pu" ? kp : km; if (!k) continue; out[p.e] += n0 * k * bate(p, dt); }
    for (let i = 0; i < out.length; i++) if (out[i] < 0) out[i] = 0;
    return out;
  }
  const valOf = (N, i, m) => (N[i] * lam[i] / YR) * (m ? NUC[i][3] : NUC[i][4]); // m: 0 activity (Bq), 1 radiotoxicity (Sv)
  // the ore: 8.57 t natural uranium with all daughters in equilibrium
  const NATU = (4.2 - 0.25) / (0.711 - 0.25);
  const ORE = (() => { const a8 = (0.992745e6 / 238.05) * NA * lam[ID.U238] / YR, a5 = (0.0072e6 / 235.04) * NA * lam[ID.U235] / YR, f = (k, m) => (m ? NUC[ID[k]][3] : NUC[ID[k]][4]);
    return [0, 1].map((m) => NATU * (a8 * ["U238", "U234", "Th230", "Ra226", "Pb210"].reduce((s, k) => s + f(k, m), 0) + a5 * ["U235", "Pa231", "Ac227"].reduce((s, k) => s + f(k, m), 0))); })();

  // ---------- grid: band values per source group (fp, pu+U, ma), for both measures, 1 .. 10^6 years ----------
  const NT = 301, LT = (k) => (6 * k) / (NT - 1), L4 = Math.log10(4);
  let GRID = null; // GRID[m][g][k*NB+b] (unseparated contributions; the separation factor multiplies groups pu, ma for t >= 4)
  function buildGrid() {
    GRID = [0, 1].map(() => [0, 1, 2].map(() => new Float64Array(NT * NB)));
    for (let k = 0; k < NT; k++) {
      const dt = 10 ** LT(k) - 4;
      for (const p of PATHS) { const n0 = N4[p.s]; if (!n0) continue; const n = n0 * bate(p, dt); if (n <= 0) continue;
        const e = p.e, a = (n * lam[e]) / YR, g = GR[NUC[p.s][6]], b = BI[NUC[e][5]];
        GRID[0][g][k * NB + b] += a * NUC[e][4]; GRID[1][g][k * NB + b] += a * NUC[e][3]; }
    }
  }
  /** band values (ratio to the ore) at grid k for measure m, separation factors kp, km */
  function bandsAt(k, m, kp, km, out) {
    const sep = LT(k) >= L4 - 1e-9, fp = 1, pp = sep ? kp : 1, mm = sep ? km : 1, G = GRID[m], o = ORE[m];
    let tot = 0; for (let b = 0; b < NB; b++) { const v = (G[0][k * NB + b] * fp + G[1][k * NB + b] * pp + G[2][k * NB + b] * mm) / o; out[b] = v; tot += v; }
    return tot;
  }
  function totalAt(t, m, kp, km) { const N = nucAt(t, kp, km); let s = 0; for (let i = 0; i < NUC.length; i++) s += valOf(N, i, m); return s / ORE[m]; }
  /** last time the total is above the ore, and the nuclide that dominates then */
  function crossing(m, kp, km) {
    let lo = null; const tmp = new Float64Array(NB);
    for (let k = NT - 1; k >= 0; k--) if (bandsAt(k, m, kp, km, tmp) > 1) { lo = k; break; }
    if (lo === null) return { t: 1, who: "" }; if (lo === NT - 1) return null;
    let a = LT(lo), b = LT(lo + 1); if (a < L4 && b > L4 && totalAt(4, m, kp, km) <= 1) return { t: 4, who: "" };
    for (let i = 0; i < 40; i++) { const mid = (a + b) / 2; if (totalAt(10 ** mid, m, kp, km) > 1) a = mid; else b = mid; }
    const t = 10 ** b, N = nucAt(t, kp, km); let best = -1, bv = 0, tot = 0;
    for (let i = 0; i < NUC.length; i++) { const v = valOf(N, i, m); tot += v; if (v > bv) { bv = v; best = i; } }
    return { t, who: nm(NUC[best][0]), share: bv / tot, band: NUC[best][5] };
  }
  // inventory one year after unloading for step 1 (very short-lived fission products, not in the tables, are gone by then): rows [label, nuclide ids, band, mass override (g)]
  const ROWS = [["uranium", ["U238", "U235", "U236", "U234"], "u"], ["other fission products", null, "ofp", 0], ["Pu-239", ["Pu239"], "pu9"], ["Pu-240", ["Pu240"], "pu0"],
    ["Pu-241", ["Pu241"], "pu1"], ["Cs-137", ["Cs137"], "cs"], ["Tc-99", ["Tc99"], "tc"], ["Pu-242", ["Pu242"], "pu2"], ["Sr-90", ["Sr90"], "sr"], ["Np-237", ["Np237"], "np"],
    ["Pu-238", ["Pu238"], "pu8"], ["Am-243", ["Am243"], "am3"], ["I-129", ["I129"], "i"], ["Cm-244", ["Cm244"], "cm"], ["Am-241", ["Am241"], "am1"]];
  let INV = null;
  function buildInv() {
    const N = nucAt(1, 1, 1); // one year after unloading (the table, decayed back from 4 years)
    INV = ROWS.map(([lab, ids, band]) => {
      let g = 0, a = 0;
      if (ids) ids.forEach((k) => { const i = ID[k]; g += (N[i] * NUC[i][2]) / NA; a += valOf(N, i, 0); });
      else { NUC.forEach((n, i) => { if (n[5] === "ofp") a += valOf(N, i, 0); }); g = 51300 - ["Sr90", "Cs137", "Tc99", "I129"].reduce((s, k) => s + (N[ID[k]] * NUC[ID[k]][2]) / NA, 0); }
      return { lab, band, g, a };
    });
  }
  const SUP = "⁰¹²³⁴⁵⁶⁷⁸⁹", sup = (n) => String(n).replace("-", "⁻").replace(/\d/g, (d) => SUP[d]);
  const fmtE = (v) => { if (!(v > 0)) return "0"; const e = Math.floor(Math.log10(v)), m = v / 10 ** e; return m.toFixed(1) === "10.0" ? `1×10${sup(e + 1)}` : `${m.toFixed(1)}×10${sup(e)}`; };
  const fmtMass = (g) => (g >= 1000 ? `${g >= 1e5 ? Math.round(g / 1000) : (g / 1000).toFixed(g >= 1e4 ? 0 : 1)} kg` : `${g >= 100 ? Math.round(g) : g.toFixed(0)} g`);
  const fmtY = (y) => { if (y < 10) return y.toFixed(0); const p = Number(y.toPrecision(2)); return p.toLocaleString("en"); };
  const SHOT = () => document.body.classList.contains("shot"), snap = (S) => { S.kp = S.target.kp; S.km = S.target.km; S.mx = S.target.mx; };
  const PRESS = { pu: [0, 0.99, 0.999], ma: [0, 0.99, 0.999] };

  WT.chapter("spentfuel", {
    level: 2, num: "Lesson 1", title: "Spent fuel, nuclide by nuclide", short: "Nuclide by nuclide",
    html: `
<div class="step">
  <h3>What's inside</h3>
  <p>One tonne of PWR fuel a year after unloading (4.2 % enriched, 50 GWd/t): nearly all the mass is uranium, nearly all the activity sits in a few kilograms.</p>
</div>
<div class="step">
  <h3>Activity or radiotoxicity</h3>
  <p>Becquerels count decays; sieverts weight each decay by its harm if swallowed, which raises the alpha emitters.</p>
  <div class="btns"><button class="btn ghost" data-act="mA" aria-pressed="false">Activity (Bq)</button> <button class="btn ghost" data-act="mT" aria-pressed="true">Radiotoxicity (Sv)</button></div>
</div>
<div class="step">
  <h3>Who dominates when</h3>
  <p>Hover or tap a band to name it; drag along the time axis to rank them.</p>
</div>
<div class="step">
  <h3>Recycle the plutonium</h3>
  <p>Reprocessing at four years takes the plutonium out (and the uranium with it). How much is left behind?</p>
  <div class="btns"><span class="sf-k" style="font:600 13px var(--sans);color:var(--soft);margin-right:4px;align-self:center">Pu removed</span> <button class="btn ghost" data-act="pu0" aria-pressed="true">0 %</button> <button class="btn ghost" data-act="pu99" aria-pressed="false">99 %</button> <button class="btn ghost" data-act="pu999" aria-pressed="false">99.9 %</button></div>
</div>
<div class="step">
  <h3>Remove the minor actinides too</h3>
  <p>Take out americium, curium and neptunium as well: then the 1 % or 0.1 % left behind decides the time.</p>
  <div class="btns"><span class="sf-k" style="font:600 13px var(--sans);color:var(--soft);margin-right:4px;align-self:center">Pu removed</span> <button class="btn ghost" data-act="pu0" aria-pressed="true">0 %</button> <button class="btn ghost" data-act="pu99" aria-pressed="false">99 %</button> <button class="btn ghost" data-act="pu999" aria-pressed="false">99.9 %</button></div>
  <div class="btns"><span class="sf-k" style="font:600 13px var(--sans);color:var(--soft);margin-right:4px;align-self:center">Am, Cm, Np removed</span> <button class="btn ghost" data-act="ma0" aria-pressed="true">0 %</button> <button class="btn ghost" data-act="ma99" aria-pressed="false">99 %</button> <button class="btn ghost" data-act="ma999" aria-pressed="false">99.9 %</button></div>
</div>`,
    setup(S) {
      S.set("mx", 1); S.set("kp", 0); S.set("km", 0); S.set("cur", 3); S.set("inv", 1); S.meas = 1; S.fPu = 0; S.fMA = 0; S.hov = null;
      const root = () => document.querySelectorAll("#spentfuel [data-act]");
      const press = () => root().forEach((b) => { const a = b.dataset.act; let on = false;
        if (a === "mA") on = S.meas === 0; else if (a === "mT") on = S.meas === 1;
        else if (a.startsWith("pu")) on = PRESS.pu[{ pu0: 0, pu99: 1, pu999: 2 }[a]] === S.fPu; else if (a.startsWith("ma")) on = PRESS.ma[{ ma0: 0, ma99: 1, ma999: 2 }[a]] === S.fMA;
        b.setAttribute("aria-pressed", String(on)); });
      S.press = press;
      S.apply = (i) => { const st = Math.max(0, i ?? S.step), fp = st >= 3 ? S.fPu : 0, fm = st >= 4 ? S.fMA : 0;
        S.to("kp", Math.log10(Math.max(1 - fp, 1e-6))); S.to("km", Math.log10(Math.max(1 - fm, 1e-6))); S.to("mx", S.meas); press(); };
      S.on("mA", () => { S.meas = 0; S.apply(); }); S.on("mT", () => { S.meas = 1; S.apply(); });
      [["pu0", 0], ["pu99", 0.99], ["pu999", 0.999]].forEach(([a, v]) => S.on(a, () => { S.fPu = v; S.apply(); }));
      [["ma0", 0], ["ma99", 0.99], ["ma999", 0.999]].forEach(([a, v]) => S.on(a, () => { S.fMA = v; S.apply(); }));
    },
    steps: [
      (S) => { S.set("mode", "inv"); },
      (S) => { S.set("mode", "chart"); S.hov = null; S.apply(1); },
      (S) => { S.set("mode", "chart"); if (SHOT()) { S.cur = 3; S.meas = 1; } S.apply(2); },
      (S) => { S.set("mode", "chart"); S.hov = null; if (SHOT()) { S.meas = 1; S.fPu = 0.999; } S.apply(3); if (SHOT()) snap(S); },
      (S) => { S.set("mode", "chart"); S.hov = null; if (SHOT()) { S.meas = 1; S.fPu = 0.999; S.fMA = 0.999; } S.apply(4); if (SHOT()) snap(S); },
    ],
    frame(g, S, dt) {
      const { W, H, c } = g, phone = W < 600, fs = phone ? 11 : 13, st = Math.max(0, S.step), dark = isDark(c.paper);
      const BC = BANDS.map((b) => (dark ? b[4] : b[3]));
      if (!GRID) { buildGrid(); buildInv(); }
      if (S.mode === "inv") return drawInv(g, S, BC, phone, fs);
      // ---------- the chart ----------
      const x0 = phone ? 40 : Math.max(64, W * 0.07), x1 = W - (phone ? 10 : 22), yT = phone ? 58 : Math.max(86, H * 0.15), yB = H - (phone ? 34 : 50), LO = -3, HI = lerp(5.2, 3.8, clamp(S.mx, 0, 1));
      const X = (l) => lerp(x0, x1, l / 6), Yr = (lr) => lerp(yB, yT, (clamp(lr, LO - 0.5, HI + 0.5) - LO) / (HI - LO));
      const kp = 10 ** S.kp, km = 10 ** S.km, mx = clamp(S.mx, 0, 1);
      const tA = new Float64Array(NB), tT = new Float64Array(NB);
      const top = [], cum = []; // per k: top y, cumulative shares
      for (let k = 0; k < NT; k++) {
        const a = bandsAt(k, 0, kp, km, tA), t = bandsAt(k, 1, kp, km, tT);
        const lr = lerp(Math.log10(Math.max(a, 1e-9)), Math.log10(Math.max(t, 1e-9)), mx);
        top.push(Yr(lr)); const cs = new Float64Array(NB + 1); let s = 0;
        for (let b = 0; b < NB; b++) { s += lerp(tA[b] / a, tT[b] / t, mx); cs[b + 1] = s; }
        for (let b = 0; b <= NB; b++) cs[b] /= s || 1; cum.push(cs);
      }
      const yOf = (k, f) => yB + (Math.min(top[k], yB) - yB) * f;
      g.clip(x0, yT - 4, x1 - x0, yB - yT + 4);
      for (let b = 0; b < NB; b++) {
        const pts = []; for (let k = 0; k < NT; k++) pts.push([X(LT(k)), yOf(k, cum[k][b + 1])]);
        for (let k = NT - 1; k >= 0; k--) pts.push([X(LT(k)), yOf(k, cum[k][b])]);
        const hl = S.hov && S.hov.b === b; g.area(pts, BC[b], S.hov ? (hl ? 0.95 : 0.4) : 0.86);
      }
      const tpts = top.map((y, k) => [X(LT(k)), y]); g.poly(tpts, c.ink, 1.6, 0.85);
      // once-through total for comparison (steps 4-5)
      const sepOn = st >= 3 && (S.kp < -0.05 || S.km < -0.05); let gp = null;
      if (sepOn) { gp = []; for (let k = 0; k < NT; k++) { const a = bandsAt(k, 0, 1, 1, tA), t = bandsAt(k, 1, 1, 1, tT); gp.push([X(LT(k)), Yr(lerp(Math.log10(a), Math.log10(t), mx))]); } g.poly(gp, c.soft, 1.4, 0.8, [5, 4]); }
      g.ctx.restore();
      if (gp) { const k = Math.round((NT - 1) * (phone ? 0.62 : 0.66)); g.label(phone ? "once-through" : "once-through (no recycling)", gp[k][0], gp[k][1] - 12, { color: c.soft, size: fs - 2, bg: true }); }
      // ore level
      const oreRight = !(S._cx && Math.log10(S._cx.t) > 3.4) || st === 2, yo = Yr(0); g.line(x0, yo, x1, yo, c.fission, 2, 0.95, [7, 5]);
      g.label(phone ? `ore: ${fmtE(ORE[S.meas])} ${S.meas ? "Sv" : "Bq"}` : `the ore it came from: ${NATU.toFixed(1)} t natural uranium + daughters = ${fmtE(ORE[S.meas])} ${S.meas ? "Sv" : "Bq"}`, oreRight ? x1 - 4 : x0 + 6, yo - (phone ? 11 : 13), { color: c.fission, size: fs - 2, weight: 600, align: oreRight ? "right" : "left", bg: true });
      // separation marker
      if (sepOn) { const xs = X(L4); g.line(xs, yT, xs, yB, c.ink, 1, 0.35, [2, 3]); g.label(phone ? "4 yr" : "reprocessing at 4 yr", xs + 4, yB - 10, { color: c.soft, size: fs - 3, align: "left", bg: true }); }
      // axes
      ["1 yr", "10", "100", "1000", "10⁴", "10⁵", phone ? "10⁶" : "1 million"].forEach((s, l) => g.label(s, X(l), yB + 12, { color: c.faint, size: fs - 2 }));
      if (!phone) g.label("years after unloading (log scale) →", x1, yB + 30, { color: c.soft, size: fs - 1, align: "right" });
      [-2, 0, 2, 4].filter((e) => e <= HI).forEach((e) => { g.line(x0 - 4, Yr(e), x0, Yr(e), c.faint, 1); g.label(e === 0 ? "×1" : e < 0 ? "×0.01" : `×${e === 2 ? 100 : "10⁴"}`, x0 - 7, Yr(e), { color: c.faint, size: fs - 2, align: "right" }); });
      const yl = S.meas ? (phone ? "radiotoxicity ÷ ore" : "radiotoxicity if swallowed (Sv), relative to the ore") : phone ? "activity ÷ ore" : "activity (Bq), relative to the ore";
      g.label(yl, x0, yT - (phone ? 10 : 14), { color: c.soft, size: fs - 1, align: "left" });
      // direct labels on the biggest bands (where each is thickest)
      const placed = [];
      if (!S.hov) for (let b = 0; b < NB; b++) {
        let bk = -1, bh = 0; for (let k = 8; k < NT - 2; k += 2) { const h = yOf(k, cum[k][b]) - yOf(k, cum[k][b + 1]); if (h > bh) { bh = h; bk = k; } }
        if (bh < (phone ? 15 : 19) || bk < 0) continue;
        const s = phone ? BANDS[b][2] : BANDS[b][1], w = s.length * (fs - 2) * 0.56 + 14; let y = (yOf(bk, cum[bk][b]) + yOf(bk, cum[bk][b + 1])) / 2; if (Math.abs(y - yo) < 13 && bh > 50) y += y < yo ? -14 : 14; const x = clamp(X(LT(bk)), x0 + w / 2 + 2, x1 - w / 2 - 2);
        if (y < yT + 6 || Math.abs(y - yo) < 11 || placed.some((p) => Math.abs(p[0] - x) < (p[2] + w) / 2 + 4 && Math.abs(p[1] - y) < 18)) continue; placed.push([x, y, w]);
        g.label(s, x, y, { color: c.ink, size: fs - 2, weight: 600, bg: true });
      }
      // ---------- readouts ----------
      const key = `${S.meas}|${S.target.kp}|${S.target.km}`;
      if (S._ck !== key) { S._ck = key; S._cx = crossing(S.meas, 10 ** S.target.kp, 10 ** S.target.km); }
      const cx = S._cx, ry = phone ? 16 : Math.max(26, yT * 0.3);
      if (st === 2) {
        // ranked shares at the cursor
        const L = clamp(S.cur, 0, 6), k = Math.round((L / 6) * (NT - 1)), xx = X(LT(k));
        g.line(xx, yT, xx, yB, c.ink, 1.2, 0.5); g.dot(xx, top[k], 5, c.ink); g.glow(xx, top[k], 16, c.accent, 0.45);
        const rank = []; for (let b = 0; b < NB; b++) rank.push([b, cum[k][b + 1] - cum[k][b]]); rank.sort((a, q) => q[1] - a[1]);
        const t = 10 ** LT(k), tt = t < 10 ? t.toFixed(1) : fmtY(t);
        g.label(`${tt} years:`, phone ? 8 : x0, ry, { color: c.ink, size: fs + 1, weight: 700, serif: true, align: "left" });
        let xr = (phone ? 8 : x0) + (phone ? 76 : 110); const r2 = phone ? rank.slice(0, 3) : rank.slice(0, 4);
        g.ctx.save(); g.ctx.font = `600 ${fs}px ${getComputedStyle(document.documentElement).getPropertyValue("--sans") || "sans-serif"}`;
        r2.forEach(([b, sh]) => { if (sh < 0.005) return; const s = `${phone ? BANDS[b][2] : BANDS[b][1]} ${Math.round(sh * 100)} %`; g.dot(xr + 5, ry, 5, BC[b]); g.label(s, xr + 14, ry, { color: c.ink, size: fs, weight: 600, align: "left" }); xr += g.ctx.measureText(s).width + 34; });
        g.ctx.restore();
        g.label(phone ? "drag the time · tap a band" : "drag along the time axis · hover a band", W / 2, ry + fs + 10, { color: c.soft, size: fs - 1 });
      } else if (cx) {
        const lc = Math.log10(cx.t), xc = X(lc);
        if (lc > 0.01) { g.line(xc, yo, xc, yB, c.fission, 1.2, 0.7, [2, 4]); g.glow(xc, yo, 20, c.fission, 0.5 + 0.15 * Math.sin(S.time * 3)); g.dot(xc, yo, 6, c.fission); }
        g.label(`below the ore after ≈ ${fmtY(cx.t)} years`, W / 2, ry, { color: c.ink, size: fs + (phone ? 2 : 4), weight: 600, serif: true });
        if (cx.who) g.label(`then mostly ${cx.who} (${Math.round(cx.share * 100)} %)`, W / 2, ry + fs + (phone ? 8 : 12), { color: c.soft, size: fs, weight: 600 });
      } else g.label("still above the ore after a million years", W / 2, ry, { color: c.ink, size: fs + 3, weight: 600, serif: true });
      // ---------- hover / tap a band ----------
      const inPlot = (x, y) => x > x0 - 2 && x < x1 + 2 && y > yT - 8 && y < yB + 22;
      const pick = (x, y) => { const k = clamp(Math.round(((x - x0) / (x1 - x0)) * (NT - 1)), 0, NT - 1), hT = Math.min(top[k], yB); if (y < hT - 2 || y > yB) return null;
        const f = (yB - y) / Math.max(1, yB - hT); for (let b = 0; b < NB; b++) if (f >= cum[k][b] && f <= cum[k][b + 1]) return { k, b }; return null; };
      WT.grab(g.ctx.canvas, {
        down(x, y) { if (S.mode !== "chart" || !inPlot(x, y)) return false; S.hov = pick(x, y); if (S.step === 2) S.cur = clamp(((x - x0) / (x1 - x0)) * 6, 0, 6); S.drag = true; return true; },
        move(x, y) { if (S.step === 2) S.cur = clamp(((x - x0) / (x1 - x0)) * 6, 0, 6); S.hov = pick(x, y); },
        up() { S.drag = false; }, cancel() { S.drag = false; },
        hover(x, y) { if (S.mode !== "chart") return; const ins = inPlot(x, y); g.ctx.canvas.style.cursor = ins ? (S.step === 2 ? "ew-resize" : "crosshair") : "default"; S.hov = ins ? pick(x, y) : null; },
      });
      if (S.hov) {
        const { k, b } = S.hov, m = S.meas, v = (m ? bandsAt(k, 1, kp, km, tT) && tT[b] : bandsAt(k, 0, kp, km, tA) && tA[b]) * ORE[m], sh = cum[k][b + 1] - cum[k][b], t = 10 ** LT(k);
        const xh = X(LT(k)), yh = (yOf(k, cum[k][b]) + yOf(k, cum[k][b + 1])) / 2;
        g.dot(xh, yh, 4, c.ink); g.ring(xh, yh, 8, c.ink, 1.5, 0.8);
        const l1 = BANDS[b][1], l2 = `${fmtE(v)} ${m ? "Sv" : "Bq"} · ${sh < 0.01 ? "<1" : Math.round(sh * 100)} % · ${t < 10 ? t.toFixed(1) : fmtY(t)} yr`;
        const bx = clamp(xh, x0 + 90, x1 - 90), by = yh - 34 < yT ? yh + 34 : yh - 34;
        g.label(l1, bx, by - 9, { color: c.ink, size: fs, weight: 700, bg: true }); g.label(l2, bx, by + 10, { color: c.soft, size: fs - 1, bg: true });
      }
      g.label(phone ? "computed · band height = share" : "computed (Bateman decay, ICRP-72) · band height = share of the total", W - 6, H - 8, { color: c.faint, size: 10, align: "right" });
    },
  });

  function isDark(hex) { const h = (hex || "#ffffff").replace("#", ""); const n = parseInt(h.length === 3 ? h.split("").map((x) => x + x).join("") : h, 16); return ((n >> 16) & 255) + ((n >> 8) & 255) + (n & 255) < 300; }

  // ---------- step 1: mass against activity, row by row ----------
  function drawInv(g, S, BC, phone, fs) {
    const { W, H, c } = g, sorted = INV.slice().sort((a, b) => b.g - a.g), rows = phone ? sorted.slice(0, 13) : sorted, n = rows.length;
    const top = phone ? 46 : Math.max(70, H * 0.13), bot = H - (phone ? 26 : 40), rh = Math.min(phone ? 22 : 38, (bot - top) / n);
    const nameW = phone ? 74 : 150, cxm = W / 2, xa = cxm + nameW / 2 + 6, xm = cxm - nameW / 2 - 6, side = Math.min(phone ? (W - nameW) / 2 - 14 : 420, (W - nameW) / 2 - 30);
    const MLO = 1, MHI = 6.5, ALO = 9, AHI = 17.4; // log10 g, log10 Bq
    const mX = (gr) => xm - side * clamp((Math.log10(Math.max(gr, 1)) - MLO) / (MHI - MLO), 0, 1), aX = (a) => xa + side * clamp((Math.log10(Math.max(a, 1)) - ALO) / (AHI - ALO), 0, 1);
    g.label(phone ? "mass" : "mass (log scale)", xm, top - (phone ? 26 : 34), { color: c.ink, size: fs + 1, weight: 700, align: "right" });
    g.label(phone ? "activity" : "activity after 1 year (log scale)", xa, top - (phone ? 26 : 34), { color: c.ink, size: fs + 1, weight: 700, align: "left" });
    if (!phone) { [1, 3, 5].forEach((e) => g.label(["", "10 g", "", "1 kg", "", "100 kg"][e], mX(10 ** e), top - 12, { color: c.faint, size: fs - 3 }));
      [10, 13, 16].forEach((e) => g.label(`10${sup(e)} Bq`, aX(10 ** e), top - 12, { color: c.faint, size: fs - 3 })); }
    const t = S.time;
    rows.forEach((r, i) => {
      const y = top + rh * (i + 0.5), col = BC[BI[r.band]], bh = Math.max(6, rh * 0.56);
      const xl = mX(r.g), xr = aX(r.a);
      const rr = (x, w) => { const ctx = g.ctx; ctx.save(); ctx.fillStyle = col; ctx.globalAlpha = 0.85; ctx.beginPath(); if (ctx.roundRect) ctx.roundRect(x, y - bh / 2, Math.max(1, w), bh, 3); else ctx.rect(x, y - bh / 2, Math.max(1, w), bh); ctx.fill(); ctx.restore(); };
      rr(xl, xm - xl); rr(xa, xr - xa);
      // the activity end shimmers: brighter for more decays per second
      const life = clamp((Math.log10(r.a) - 10) / 6, 0, 1);
      g.glow(xr, y, bh * (0.9 + 1.4 * life), col, 0.1 + 0.3 * life * (0.75 + 0.25 * Math.sin(t * (3 + i) + i)));
      g.label(r.lab === "other fission products" && phone ? "other FP" : r.lab, cxm, y, { color: c.ink, size: fs - (phone ? 1 : 0), weight: 600 });
      g.label(fmtMass(r.g), xl - 5, y, { color: c.soft, size: fs - 2, align: "right" });
      g.label(`${fmtE(r.a)}`, xr + 6 + bh * 0.6, y, { color: c.soft, size: fs - 2, align: "left" });
    });
    g.label(phone ? "other FP: mostly stable" : "most of the 51 kg of fission products is stable; activity includes short-lived daughters", W / 2, bot + (phone ? 10 : 18), { color: c.soft, size: fs - 2 });
    g.label(phone ? "NEA 1999 + computed" : "inventory: OECD-NEA 1999 (4.2 %, 50 GWd/t) + computed fission products", W - 6, H - 8, { color: c.faint, size: 10, align: "right" });
  }
})();
