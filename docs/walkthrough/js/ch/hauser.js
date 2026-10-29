/* Chapter 22 (Expert): Hauser-Feshbach channel by channel, with width fluctuations (compound/prepare.py, compound/wfc.py).
 * Scenes (S.mode): "tlj"    = incident transmission T_lj per (l, j) as lit columns; neutrons enter through them into the compound nucleus;
 *                   "group"  = one J^pi: the incident channel, every exit (log T, summed per level), the flux split T_b / sum T;
 *                   "wfc"    = summed over J^pi: compound elastic, inelastic to the first 2+, to higher levels and the continuum, capture;
 *                              HF against Moldauer, ratio badges, particles leaving at the shares;
 *                   "curves" = the ratio sigma(WFC)/sigma(HF) against incident energy for Moldauer and HRTW;
 *                   "limit"  = elastic enhancement W_aa against the total transmission sum T (= 2 pi Gamma/D) for N equal channels;
 *                              an inset ladder shows isolated -> overlapping resonances.
 * The numbers are computed here with the formulas of compound/wfc.py: Moldauer's nu (molprepare.f90), TALYS's 32-point
 * Gauss-Laguerre integral (gaulag.f90), HRTW with its 60 fixed-point iterations (hrtwprepare.f90); continuum channels carry a
 * multiplicity rho dE (the product exponent -nu rho / 2), as in TALYS. The ingredients are illustrative: n + an even-even
 * target (I = 0+, A = 56) with seven excited levels up to 3.45 MeV and a constant-temperature continuum above 3.6 MeV;
 * T_l from hard-sphere penetrabilities (T_l = 1 - exp(-4 kappa P_l), kappa set so that S0 ~ 2.5e-4) with a small
 * spin-orbit split; capture lumped into one channel T_gamma = 2 pi Gamma_gamma / D (about 2.5e-4 at threshold). */
(function () {
  const { TAU, clamp, lerp, smooth, rng } = WT.util;
  const A = 56, MU = A / (A + 1), RF = 1.35 * Math.cbrt(A), KAP = 0.35, LMAX = 8;
  // levels of an iron-like even-even nucleus (MeV, spin, all + parity here); continuum above EC
  const LEV = [{ e: 0, I: 0 }, { e: 0.847, I: 2 }, { e: 2.085, I: 4 }, { e: 2.658, I: 2 }, { e: 2.942, I: 0 }, { e: 3.123, I: 4 }, { e: 3.37, I: 2 }, { e: 3.445, I: 3 }];
  const EC = 3.6, DEB = 0.25, TCT = 1.1, E0CT = 0.65, SIGR2 = 6;
  const rhoCT = (ex) => Math.exp((ex - E0CT) / TCT) / TCT;
  const fI = (I) => (2 * I + 1) / (2 * SIGR2) * Math.exp(-((I + 0.5) ** 2) / (2 * SIGR2));
  // gaulag.f90 nodes and square roots of the weights (TALYS stores sqrt(w); compound/wfc.py)
  const GLX = [0.044489365833267, 0.234526109519619, 0.576884629301886, 1.072448753817818, 1.722408776444645, 2.528336706425795, 3.492213273021994, 4.616456769749767, 5.903958504174244, 7.358126733186241, 8.982940924212596, 10.78301863253997, 12.76369798674273, 14.93113975552256, 17.29245433671532, 19.85586094033606, 22.63088901319677, 25.62863602245925, 28.86210181632348, 32.34662915396474, 36.10049480575197, 40.14571977153944, 44.50920799575494, 49.22439498730864, 54.33372133339691, 59.89250916213402, 65.97537728793505, 72.68762809066271, 80.18744697791352, 88.7353404178924, 98.82954286828397, 111.7513980979377];
  const GLW = [0.3304819843083507, 0.4587407851268658, 0.4849878654872182, 0.4426096880693881, 0.3605326424695436, 0.265666376995128, 0.1782159154205232, 0.1091705767816519, 6.1145860813398685e-2, 3.1317779401083899e-2, 1.4658271344239885e-2, 6.2612634252105599e-3, 2.4360914623364682e-3, 8.611854956202846e-4, 2.7576380979237979e-4, 7.9690665868882078e-5, 2.0691503017038005e-5, 4.8019782297417133e-6, 9.8991814251114182e-7, 1.7993892457523653e-7, 2.8586401388458671e-8, 3.9270011884309682e-9, 4.604120209294734e-10, 4.532581685737219e-11, 3.6701261376652915e-12, 2.3793474169186305e-13, 1.19103339393278e-14, 4.3742147803396949e-16, 1.0919014424838086e-17, 1.6344758239998953e-19, 1.1569861460303905e-21, 2.1238022963305632e-24];
  const GLQ = GLX.map((x, m) => GLW[m] * GLW[m] * Math.exp(x));
  const log10 = (x) => Math.log(x) / Math.LN10;

  /** hard-sphere penetrability P_l(rho) by the standard recursion */
  function penet(l, rho) { let P = rho, Sh = 0; for (let k = 1; k <= l; k++) { const d = (k - Sh) * (k - Sh) + P * P; const Pn = rho * rho * P / d; Sh = rho * rho * (k - Sh) / d - k; P = Pn; } return P; }
  /** neutron transmission for orbital l, total j, channel energy eps (MeV) */
  function Tlj(l, j, eps) {
    if (eps <= 0) return 0;
    const rho = 0.2197 * MU * Math.sqrt(eps) * RF, T = 1 - Math.exp(-4 * KAP * penet(l, rho));
    return l === 0 ? T : clamp(T * (1 + (j > l ? 0.06 : -0.06) * (1 - T)), 0, 1);
  }
  const wJ = (J) => (2 * J + 1) / 2 * Math.exp(-((J + 0.5) ** 2 - 1) / 18);
  const Tgam = (J, E) => 2.5e-4 * Math.exp(E / 1.15) * wJ(J);
  const jName = (J2) => `${J2}/2`;
  const sup = (n) => String(n).replace(/[-0-9]/g, (ch) => "⁻⁰¹²³⁴⁵⁶⁷⁸⁹"["-0123456789".indexOf(ch)]);
  const parOf = (l) => (l % 2 === 0 ? 1 : -1);

  /** W factors of one J^pi block. T[b], m[b]: transmission and multiplicity (1 for a discrete-level channel, rho dE for a
   *  continuum bin) of every exit particle channel; ia = the incident (= elastic) channel; Tg = lumped capture.
   *  method 0 = none, 1 = Moldauer (molprepare/moldauer.f90), 2 = HRTW (hrtwprepare/hrtw.f90). Returns W[b], Wg, st. */
  function wfc(T, m, Tg, ia, method) {
    const n = T.length; let st = Tg; for (let i = 0; i < n; i++) st += m[i] * T[i];
    if (method === 0 || st <= 0) return { W: T.map(() => 1), Wg: 1, st };
    if (method === 1) {
      const nu = T.map((t) => Math.min(2, 1.78 + (Math.pow(t, 1.212) - 0.78) * Math.exp(-0.228 * st)));
      const f = T.map((t, i) => 2 * t / (st * nu[i])), W = new Array(n).fill(0); let Wg = 0;
      for (let q = 0; q < 32; q++) {
        const x = GLX[q]; let lp = -Tg * x / st; for (let i = 0; i < n; i++) lp -= 0.5 * nu[i] * m[i] * Math.log1p(x * f[i]);
        if (lp < -700) continue;
        const P = GLQ[q] * Math.exp(lp), da = 1 + x * f[ia];
        for (let b = 0; b < n; b++) W[b] += P * (b === ia ? 1 + 2 / nu[ia] : 1) / (da * (1 + x * f[b]));
        Wg += P / da;
      }
      return { W, Wg, st };
    }
    let st2 = Tg * Tg; for (let i = 0; i < n; i++) st2 += m[i] * T[i] * T[i];
    const fac = 4 * st2 / (st * st + 3 * st2), all = T.concat([Tg]), mm = m.concat([1]);
    const w = all.map((t) => (t < st ? 1 + 2 / (1 + Math.pow(t, fac * (1 + t / st))) + 87 * ((t - st2 / st) / st) ** 2 * (t / st) ** 5 : 3));
    let v = all.map((t, i) => t / (1 + t / st * (w[i] - 1))), sv = 0;
    for (let it = 0; it < 60; it++) { sv = 0; for (let i = 0; i < v.length; i++) sv += mm[i] * v[i]; v = all.map((t, i) => t / (1 + v[i] / sv * (w[i] - 1))); }
    const Ta = all[ia], Wf = (b) => (all[b] > 0 ? v[ia] * v[b] * st / (sv * Ta * all[b]) * (b === ia ? w[ia] : 1) : 0);
    return { W: T.map((_, b) => Wf(b)), Wg: Wf(n), st };
  }
  /** every J^pi block at incident energy E: incident (l, j) and the exit channels {lev (0.. discrete, -1 continuum), l, j, T, m} */
  function blocks(E) {
    const out = [];
    for (let J2 = 1; J2 <= 2 * LMAX + 1; J2 += 2) for (const par of [1, -1]) {
      const J = J2 / 2, lA = J - 0.5, l = parOf(lA) === par ? lA : lA + 1; if (l > LMAX) continue;
      const ch = [{ lev: 0, l, j: J, T: Tlj(l, J, E), m: 1 }];
      const couple = (I, pr, eps, lev, m) => {
        for (let j2 = Math.max(1, Math.abs(J2 - 2 * I)); j2 <= J2 + 2 * I; j2 += 2) for (const lp of [j2 / 2 - 0.5, j2 / 2 + 0.5]) {
          if (lp < 0 || lp > LMAX || parOf(lp) * pr !== par) continue;
          const T = Tlj(lp, j2 / 2, eps); if (T <= 1e-12) continue;
          const old = lev < 0 && ch.find((c) => c.lev === lev && c.l === lp && c.j === j2 / 2 && c.eps === eps);
          if (old) old.m += m; else ch.push({ lev, l: lp, j: j2 / 2, T, m, eps });
        }
      };
      for (let L = 1; L < LEV.length; L++) { const eps = E - LEV[L].e; if (eps > 0) couple(LEV[L].I, 1, eps, L, 1); }
      for (let ex = EC + DEB / 2; ex < E; ex += DEB) { const eps = E - ex; for (let I = 0; I <= 7; I++) for (const pr of [1, -1]) couple(I, pr, eps, -1, rhoCT(ex) * DEB * fI(I) / 2); }
      out.push({ J, J2, par, l, ch, Tg: Tgam(J, E) });
    }
    return out;
  }
  /** summed cross sections (mb): compound elastic, inelastic to the first 2+, to higher levels and the continuum, capture, formation */
  function hf(E, method) {
    const k = 0.2197 * MU * Math.sqrt(E), pk = 10 * Math.PI / (k * k), r = { ce: 0, n1: 0, n2: 0, g: 0, cn: 0 };
    for (const B of blocks(E)) {
      const T = B.ch.map((c) => c.T), m = B.ch.map((c) => c.m), res = wfc(T, m, B.Tg, 0, method), gJ = (2 * B.J + 1) / 2, Ta = T[0]; if (Ta <= 0) continue;
      r.cn += pk * gJ * Ta;
      B.ch.forEach((c, b) => { const s = pk * gJ * Ta * c.m * c.T * res.W[b] / res.st; if (c.lev === 0) r.ce += s; else if (c.lev === 1) r.n1 += s; else r.n2 += s; });
      r.g += pk * gJ * Ta * B.Tg * res.Wg / res.st;
    }
    return r;
  }
  // energy curves of the ratios, computed once
  let CURVES = null;
  function curves() {
    if (CURVES) return CURVES;
    const n = 64, lo = -3, hi = log10(5), C = { lg: [], m: [], h: [] };
    for (let i = 0; i <= n; i++) {
      const lg = lo + (hi - lo) * i / n, E = Math.pow(10, lg), h0 = hf(E, 0), h1 = hf(E, 1), h2 = hf(E, 2);
      const rat = (h) => ({ ce: h.ce / h0.ce, g: h.g / h0.g, n1: h0.n1 > 1e-9 ? h.n1 / h0.n1 : NaN });
      C.lg.push(lg); C.m.push(rat(h1)); C.h.push(rat(h2));
    }
    return (CURVES = C);
  }
  /** elastic enhancement for N equal channels with sum T = st (no capture) */
  function limitW(N, st, method) { const t = st / N, T = new Array(N).fill(t), m = new Array(N).fill(1); return wfc(T, m, 0, 0, method).W[0]; }
  const fmtMb = (v) => (v >= 100 ? v.toFixed(0) : v >= 10 ? v.toFixed(1) : v >= 1 ? v.toFixed(2) : v.toFixed(3));
  const COLS = (c) => [c.neutron, c.fission, c.alpha, c.photon];
  const EXIT = ["compound elastic", "first 2⁺ level", "higher levels", "capture"];
  const EXIT2 = [["compound", "elastic"], ["first 2⁺", "level"], ["higher", "levels"], ["capture"]];
  const SHOT = /[?&]shot=/.test(location.search);

  // glossary terms introduced in this chapter (js/glossary.js holds the rest; translations add theirs in js/i18n/<lang>-hauser.js)
  Object.assign(WT.glossary || (WT.glossary = {}), {
    hrtw: {
      term: "HRTW", aliases: ["HRTW"],
      short: "A width-fluctuation recipe of Hofmann, Richert, Tepel and Weidenmüller: an elastic factor per channel and effective transmissions found by iteration.",
      more: "It was fitted, like Moldauer's, to numerical random-matrix calculations. TALYS offers it as widthmode 2; Moldauer (1) is the default and the exact GOE triple integral (3) the reference.",
      chapter: "hauser",
    },
    ericson: {
      term: "Ericson fluctuations", aliases: ["Ericson fluctuations"],
      short: "Random fluctuations of a cross section with energy when many resonances overlap, on an energy scale set by their average total width.",
      more: "They are the strong-overlap limit of the same statistics that give Porter–Thomas widths for isolated resonances. There the elastic enhancement factor tends to 2.",
      chapter: "hauser",
    },
  });

  WT.chapter("hauser", {
    num: "Chapter 22", title: "Hauser–Feshbach, channel by channel", short: "Hauser–Feshbach",
    lead: "Chapter 9 told the competition between exits as doors. Here is the formula behind the doors, one channel at a time, and the correction it needs when only a few channels are open.",
    html: `
<div class="step">
  <h3>A transmission for every channel</h3>
  <p>A <b>channel</b> is a complete exit address: which particle, which state the residual nucleus is left in, the orbital angular momentum <i>l</i> and the total <i>j</i> = <i>l</i> ± ½ of the particle. The optical model of Chapter 5 gives each one a <b>transmission coefficient</b> <i>T<sub>lj</sub></i>. The columns are the incident neutron's, for a spin-0 target.</p>
  <div class="ctl"><label for="hf-e">Neutron energy (MeV)</label><input id="hf-e" type="range" data-bind="lgE" min="-3" max="0.7" step="0.01" value="-0.3"><output data-show="Eshow" data-fmt="3"></output></div>
  <p>At 1 keV only <i>l</i> = 0 is open, with <i>T</i> ≈ 2π<i>S</i><sub>0</sub>√<i>E</i>, a few per cent. Each extra unit of <i>l</i> costs about a factor (<i>kR</i>)² at low energy, so the columns open one by one as the energy rises. Every column feeds the compound nucleus with the weight g<sub>J</sub><i>T</i>:</p>
  <div class="formula">σ<sub>CN</sub> = (π/k²) Σ<sub>J,π</sub> g<sub>J</sub> Σ<sub>lj</sub> T<sub>lj</sub> ,  g<sub>J</sub> = (2J+1) / [(2s+1)(2I+1)]</div>
</div>
<div class="step">
  <h3>One spin and parity at a time</h3>
  <p>Angular momentum and parity are conserved, so the compound nucleus decays independently in each <i>J</i><sup>π</sup>. Inside one block every open exit channel competes with its own <i>T</i>: elastic back to the ground state, inelastic to each excited level (a column sums the (<i>l</i>, <i>j</i>) that couple to the same <i>J</i>), the continuum above 3.6 MeV, whose bins count as many channels, weighted by the level density, and capture, lumped into one tiny <i>T</i><sub>γ</sub> = 2π⟨Γ<sub>γ</sub>⟩/<i>D</i>. Heights are on a logarithmic scale.</p>
  <div class="ctl"><label for="hf-j">Spin and parity block</label><input id="hf-j" type="range" data-bind="jb" min="0" max="9" step="1" value="2" data-instant><output data-show="jbShow" data-fmt="0"></output></div>
  <div class="ctl"><label for="hf-e2">Neutron energy (MeV)</label><input id="hf-e2" type="range" data-bind="lgE" min="-3" max="0.7" step="0.01" value="-0.3"><output data-show="Eshow" data-fmt="3"></output></div>
  <p>The bar at the bottom is the <b>Hauser–Feshbach</b> split: each exit takes the share <i>T<sub>b</sub></i>/Σ<i>T<sub>c</sub></i> of what came in through channel <i>a</i>. Below 0.85 MeV only elastic and capture are open, and elastic takes almost everything.</p>
  <div class="formula">σ<sub>ab</sub> = (π/k²) Σ<sub>J,π</sub> g<sub>J</sub> T<sub>a</sub> T<sub>b</sub> / Σ<sub>c</sub> T<sub>c</sub> · W<sub>ab</sub></div>
</div>
<div class="step">
  <h3>Width fluctuations</h3>
  <p>The plain formula slightly underestimates elastic scattering, and the correction moves a little flux back into it from the other exits. Here is why.</p>
  <p>With <i>W<sub>ab</sub></i> = 1 the formula multiplies averages. The resonances behind the averages have widths that scatter (Porter–Thomas, Chapter 15), and for elastic scattering the width that lets the neutron in is the same width that lets it out, so the two are correlated. The average of the products then exceeds the product of the averages for elastic, and the other exits lose what elastic gains.</p>
  <div class="btns"><button class="btn ghost" data-act="w0" aria-pressed="false">Without correction</button><button class="btn ghost" data-act="w1" aria-pressed="true">Moldauer</button></div>
  <div class="ctl"><label for="hf-e3">Neutron energy (MeV)</label><input id="hf-e3" type="range" data-bind="lgE" min="-3" max="0.7" step="0.01" value="-0.3"><output data-show="Eshow" data-fmt="3"></output></div>
  <p>The badges give σ with the correction divided by σ without. Below the first inelastic threshold, elastic already takes nearly all the flux and barely changes, while capture loses 10 to 25 per cent. Between 1 and 1.5 MeV, compound elastic gains 15 to 35 per cent and the first 2⁺ level loses about a third. As more levels and the continuum open, compound elastic becomes a small share of the flux: its own factor rises toward 2, but what it takes from the others shrinks, and their factors return toward 1. In Moldauer's recipe each channel gets a number of degrees of freedom ν<sub>c</sub>, and <i>W</i> is a one-dimensional integral, done with TALYS's 32-point Gauss–Laguerre rule.</p>
  <div class="formula">W<sub>ab</sub> = (1 + 2δ<sub>ab</sub>/ν<sub>a</sub>) ∫₀^∞ dx Π<sub>c</sub> (1 + 2T<sub>c</sub>x / ν<sub>c</sub>ΣT)<sup>−(δ<sub>ac</sub>+δ<sub>bc</sub>+ν<sub>c</sub>/2)</sup></div>
  <div class="formula">ν<sub>c</sub> = 1.78 + (T<sub>c</sub><sup>1.212</sup> − 0.78) e<sup>−0.228 ΣT</sup></div>
</div>
<div class="step">
  <h3>Moldauer and HRTW</h3>
  <p>The curves run the same calculation over the whole energy range: the ratio for compound elastic, for the first 2⁺ level and for capture, with Moldauer solid and the <b>HRTW</b> recipe dashed. HRTW replaces the integral by an elastic factor <i>W<sub>a</sub></i> and effective transmissions <i>V<sub>a</sub></i> found by iteration.</p>
  <div class="ctl"><label for="hf-e4">Neutron energy (MeV)</label><input id="hf-e4" type="range" data-bind="lgE" min="-3" max="0.7" step="0.01" value="-0.3"><output data-show="Eshow" data-fmt="3"></output></div>
  <div class="formula">σ<sub>ab</sub> ∝ V<sub>a</sub>V<sub>b</sub> / ΣV<sub>c</sub> · [1 + δ<sub>ab</sub>(W<sub>a</sub> − 1)] ,  V<sub>a</sub> = T<sub>a</sub> / [1 + (W<sub>a</sub> − 1) V<sub>a</sub>/ΣV]</div>
  <p>The two agree closely for elastic and inelastic; for capture in the keV range HRTW removes up to 10 per cent more. Between 0.85 and 2 MeV capture even gains: there the total width is dominated by a few fluctuating neutron widths, and the average of 1/Γ exceeds 1/⟨Γ⟩. Both recipes are fits to the exact random-matrix (GOE) result, which TALYS also offers as a triple integral. INCOGNITA ports all three (<code>widthmode</code> 1, 2, 3); Moldauer is the default, applied for incident neutrons up to the target's neutron separation energy.</p>
</div>
<div class="step">
  <h3>Limits of the elastic enhancement</h3>
  <p>How big can the elastic boost get? Between two and three times, depending on whether the resonances stand apart or overlap.</p>
  <p>The limits explain the size of the effect. Take <i>N</i> equal channels and no capture, and vary their total ΣT, which is 2π times the ratio of the average total width to the level spacing, Γ/<i>D</i>. With isolated resonances (ΣT ≪ 1) and many channels, each width follows Porter–Thomas with one degree of freedom and the elastic enhancement is ⟨Γ<sub>a</sub>²⟩/⟨Γ<sub>a</sub>⟩² = 3. When resonances overlap strongly (ΣT ≫ 2π) the cross section fluctuates like a random wave (Ericson fluctuations) and the enhancement falls to 2.</p>
  <div class="ctl"><label for="hf-n">Open channels N</label><input id="hf-n" type="range" data-bind="nch" min="2" max="60" step="1" value="30" data-instant><output data-show="nch" data-fmt="0"></output></div>
  <p>For <i>N</i> isolated channels the exact value is 3<i>N</i>/(<i>N</i>+2) (the diamond): with only two channels the enhancement cannot pass 1.5, because the total width then fluctuates as much as the elastic one. Moldauer's recipe reproduces this limit; HRTW falls short of it when many weak channels are open. The inset draws resonances with the width that goes with the moving point. In Moldauer's formula the many-channel limit is 1 + 2/ν: ν → 1 for isolated resonances and ν → 1.78 when they overlap. That gives 2.12 at full overlap instead of 2: a small error of the fit.</p>
  <div class="aside">In the code: <code>compound/prepare.py</code> (exit channels and their transmissions per <i>J</i><sup>π</sup>), <code>compound/target.py</code> (the Hauser–Feshbach sums), <code>compound/wfc.py</code> (Moldauer, HRTW and GOE, ported from TALYS). The picture evaluates the same formulas with illustrative ingredients: hard-sphere transmissions for an iron-like target, seven levels, a constant-temperature continuum and one lumped capture channel.</div>
</div>`,
    setup(S) {
      S.set("mode", "tlj"); S.to("lgE", -0.3, true); S.to("jb", 2, true); S.to("nch", 30, true); S.to("withW", 1, true);
      S.Eshow = 0.5; S.jbShow = ""; S.parts = []; S.spawn = 0; S.lim = 0;
      const press = (on) => document.querySelectorAll('#hauser [data-act="w0"], #hauser [data-act="w1"]').forEach((b) => b.setAttribute("aria-pressed", String(b.dataset.act === on)));
      S.on("w0", () => { S.to("withW", 0); press("w0"); });
      S.on("w1", () => { S.to("withW", 1); press("w1"); });
    },
    steps: [
      (S) => { S.set("mode", "tlj"); },
      (S) => { S.set("mode", "group"); },
      (S) => { S.set("mode", "wfc"); },
      (S) => { S.set("mode", "curves"); },
      (S) => { S.set("mode", "limit"); if (SHOT) S.lim = 0.3; },
    ],
    frame(g, S, dt) {
      S.Eshow = Math.pow(10, S.lgE);
      showBlock(S);
      if (S.mode === "tlj") drawTlj(g, S, dt);
      else if (S.mode === "group") drawGroup(g, S, dt);
      else if (S.mode === "wfc") drawWfc(g, S, dt);
      else if (S.mode === "curves") drawCurves(g, S);
      else drawLimit(g, S, dt);
    },
  });
  WT.mods.hauser.calc = { hf, wfc, Tlj, limitW, blocks };

  // a lit column standing on a baseline
  function column(g, x, y0, w, h, color, alpha = 1, hollow) {
    const ctx = g.ctx; if (h < 0.5) { g.line(x, y0, x + w, y0, color, 2, 0.5 * alpha); return; }
    ctx.save(); ctx.globalAlpha = alpha;
    const gr = ctx.createLinearGradient(0, y0 - h, 0, y0); gr.addColorStop(0, g.rgba(color, hollow ? 0.22 : 0.95)); gr.addColorStop(1, g.rgba(color, hollow ? 0.08 : 0.45));
    ctx.fillStyle = gr; ctx.beginPath(); if (ctx.roundRect) ctx.roundRect(x, y0 - h, w, h, [3, 3, 0, 0]); else ctx.rect(x, y0 - h, w, h); ctx.fill();
    if (hollow) { ctx.strokeStyle = g.rgba(color, 0.9); ctx.lineWidth = 1.4; ctx.stroke(); }
    ctx.restore();
  }
  // moving particles: {x, y, tx, ty, t0, dur, col, arc, r}
  function stepParts(g, S) {
    for (let i = S.parts.length - 1; i >= 0; i--) {
      const p = S.parts[i], u = (S.time - p.t0) / p.dur; if (u >= 1) { S.parts.splice(i, 1); continue; } if (u < 0) continue;
      const e = smooth(0, 1, u), x = lerp(p.x, p.tx, e), y = lerp(p.y, p.ty, e) - (p.arc || 0) * Math.sin(Math.PI * e);
      g.dot(x, y, p.r || 3, p.col, 0.9 * (1 - smooth(0.8, 1, u)));
    }
  }
  const eTxt = (E) => (E < 0.1 ? `${(E * 1000).toFixed(0)} keV` : `${E.toFixed(2)} MeV`);

  // ---------- scene 1: incident T_lj columns ----------
  function drawTlj(g, S, dt) {
    const { W, H, c } = g, phone = W < 600, E = Math.pow(10, S.lgE);
    const x0 = W * 0.08, x1 = W * (phone ? 0.92 : 0.66), yB = H * (phone ? 0.78 : 0.78), yT = H * (phone ? 0.3 : 0.2), hh = yB - yT;
    const n = 7, slot = (x1 - x0) / n, bw = slot * 0.3;
    g.line(x0 - 6, yT, x1, yT, c.faint, 1, 0.6, [4, 5]);
    g.label("T = 1", x1, yT - 10, { color: c.faint, size: 11, align: "right" });
    g.line(x0 - 6, yB, x1, yB, c.soft, 1.6, 0.8);
    const cnx = phone ? W * 0.88 : W * 0.83, cny = phone ? H * 0.12 : H * 0.42;
    let tot = 0; const chans = [];
    for (let l = 0; l < n; l++) {
      const xs = x0 + l * slot + slot * 0.12;
      [l - 0.5, l + 0.5].forEach((j, q) => {
        if (j < 0) return; const T = Tlj(l, j, E), x = xs + q * (bw + 3);
        column(g, x, yB, bw, T * hh, c.neutron, 1, q === 0 && l > 0);
        chans.push({ x: x + bw / 2, T, w: (2 * j + 1) * T }); tot += (2 * j + 1) * T;
        if (T > 0.004 && !phone) g.label(T >= 0.1 ? T.toFixed(2) : T.toFixed(3), x + bw / 2, yB - T * hh - (q === 0 ? 10 : 24), { color: c.soft, size: 12 }); // the j pair stands side by side: stagger their numbers
      });
      g.label(`l=${l}`, xs + bw + 1, yB + 14, { color: c.ink, size: 12, weight: 600 });
    }
    g.label("hollow: j = l − ½ · solid: j = l + ½", (x0 + x1) / 2, yB + 34, { color: c.soft, size: 12 });
    // neutrons rising through the columns into the compound nucleus, at rates set by (2j+1) T
    S.spawn += dt * 14;
    while (S.spawn > 1) {
      S.spawn -= 1; let u = Math.random() * tot, ch = chans[0]; for (const q of chans) { u -= q.w; if (u <= 0) { ch = q; break; } }
      if (ch && ch.T > 0) { S.parts.push({ x: ch.x, y: yB, tx: ch.x, ty: yB - ch.T * hh, t0: S.time, dur: 0.7, col: c.neutron }); S.parts.push({ x: ch.x, y: yB - ch.T * hh, tx: cnx, ty: cny, t0: S.time + 0.7, dur: 0.8, col: c.neutron, arc: 30 }); }
    }
    if (S.parts.length > 260) S.parts.splice(0, S.parts.length - 260);
    stepParts(g, S);
    const k = 0.2197 * MU * Math.sqrt(E), sig = 10 * Math.PI / (k * k) * tot / 2 / 1000;   // barns (g_J = (2j+1)/2 for I = 0)
    const R = clamp(10 + 8 * Math.sqrt(sig), 10, phone ? 18 : 46);
    g.glow(cnx, cny, R * 2.2, c.warm, 0.35 + 0.05 * Math.sin(S.time * 3)); g.ball(cnx, cny, R * 0.55, c.warm);
    if (phone) g.label(`compound nucleus · σ(CN) ≈ ${sig.toFixed(2)} b`, cnx - R - 4, cny, { color: c.warm, size: 12, weight: 600, align: "right", bg: true });
    else { g.label("compound nucleus", cnx, cny + R + 12, { color: c.warm, size: 12, weight: 600, bg: true }); g.label(`σ(CN) ≈ ${sig.toFixed(2)} b`, cnx, cny + R + 32, { color: c.ink, size: 15, weight: 600, serif: true, bg: true }); }
    g.label(`E = ${eTxt(E)} · kR = ${(k * RF).toFixed(2)}`, x0, H * (phone ? 0.95 : 0.93), { color: c.soft, size: 12, align: "left" });
    g.label("transmission Tₗⱼ of the incident neutron", x0, phone ? H * 0.24 : yT - 46, { color: c.ink, size: 13, weight: 600, align: "left" });
  }

  // ---------- scene 2: one J^pi block ----------
  function blockOf(S, E) {
    const all = blocks(E), idx = clamp(Math.round(S.jb), 0, 9), J2 = 2 * Math.floor(idx / 2) + 1, par = idx % 2 ? -1 : 1;
    return all.find((b) => b.J2 === J2 && b.par === par) || all[0];
  }
  // the block slider shows J and parity as text (kit outputs only print numbers, so this one is written here)
  let shownBlock = "";
  function showBlock(S) {
    const idx = clamp(Math.round(S.jb), 0, 9), t = `${jName(2 * Math.floor(idx / 2) + 1)}${idx % 2 ? "⁻" : "⁺"}`; if (t === shownBlock) return; shownBlock = t;
    const o = document.querySelector('#hauser output[data-show="jbShow"]'); if (o) o.textContent = t;
  }
  function drawGroup(g, S, dt) {
    const { W, H, c } = g, phone = W < 600, E = Math.pow(10, S.lgE), cols = COLS(c);
    const key = S.lgE.toFixed(3) + "|" + Math.round(S.jb);
    if (!S.gb || S.gb.key !== key) S.gb = { key, B: blockOf(S, E) };
    const B = S.gb.B;
    // one column per exit level (sum over its l, j), one for the continuum, one for capture
    const cols2 = [];
    for (let L = 0; L < LEV.length; L++) { const T = B.ch.filter((q) => q.lev === L).reduce((s, q) => s + q.T, 0); const nc = B.ch.filter((q) => q.lev === L).length; cols2.push({ L, T, nc, open: E > LEV[L].e }); }
    const Tcont = B.ch.filter((q) => q.lev < 0).reduce((s, q) => s + q.m * q.T, 0);
    cols2.push({ L: -1, T: Tcont, open: E > EC }); cols2.push({ L: -2, T: B.Tg, open: true });
    const st = cols2.reduce((s, q) => s + q.T, 0), colOf = (L) => (L === 0 ? cols[0] : L === 1 ? cols[1] : L === -2 ? cols[3] : cols[2]);
    const yB = H * (phone ? 0.64 : 0.64), yT = H * (phone ? 0.24 : 0.18), hh = yB - yT, LT = (t) => clamp((log10(Math.max(t, 1e-5)) + 5) / (5 + log10(30)), 0, 1);
    const x0 = W * 0.06 + 40, x1 = W * 0.96;
    for (let d = 1; d >= -4; d--) { const y = yB - LT(Math.pow(10, d)) * hh; g.line(x0, y, x1, y, c.line, 1, 0.9); g.label(d === 0 ? "1" : d === 1 ? "10" : `10${sup(d)}`, x0 - 6, y, { color: c.faint, size: 10, align: "right" }); }
    const n = cols2.length, slot = (x1 - x0) / n, bw = Math.min(30, slot * 0.62), centers = [];
    cols2.forEach((q, i) => {
      const xc = x0 + (i + 0.5) * slot; centers.push(xc);
      if (q.open && q.T > 0) column(g, xc - bw / 2, yB, bw, LT(q.T) * hh, colOf(q.L), 1);
      else g.line(xc - bw / 2, yB, xc + bw / 2, yB, c.faint, 2, 0.6);
      const nm = q.L === 0 ? "elastic" : q.L === -1 ? "cont." : q.L === -2 ? "γ" : `${LEV[q.L].I}⁺`;
      g.label(nm, xc, yB + 13, { color: q.open ? colOf(q.L) : c.faint, size: phone ? 10 : 12, weight: 600 });
      if (q.L > 0) g.label(LEV[q.L].e.toFixed(2), xc, yB + 27, { color: c.faint, size: phone ? 10 : 12 });
      if (q.L > 0 && q.open && q.T > 0 && slot > 22) g.label(`${q.nc}×`, xc, yB - LT(q.T) * hh - 10, { color: c.soft, size: 10 });
    });
    g.label(phone ? "level energy (MeV) under each column" : "residual level (energy in MeV) · n×: number of (l, j) channels summed", x0, yB + 44, { color: c.faint, size: phone ? 10 : 12, align: "left" });
    // the compound nucleus and particles leaving through the exits at the HF shares
    const cnx = W * (phone ? 0.12 : 0.1), cny = H * (phone ? 0.11 : 0.08);
    g.glow(cnx, cny, 30, c.warm, 0.4); g.ball(cnx, cny, 8, c.warm);
    g.label(`${jName(B.J2)}${B.par > 0 ? "⁺" : "⁻"} block · in through l = ${B.l}, Tₐ = ${B.ch[0].T.toFixed(3)}`, cnx + 20, cny, { color: c.ink, size: phone ? 11 : 13, weight: 600, align: "left", bg: true });
    S.spawn += dt * 16;
    while (S.spawn > 1) {
      S.spawn -= 1; let u = Math.random() * st, k = n - 1; for (let i = 0; i < n; i++) { u -= cols2[i].T; if (u <= 0) { k = i; break; } }
      S.parts.push({ x: cnx, y: cny, tx: centers[k], ty: yB - 4, t0: S.time, dur: 1.1, col: colOf(cols2[k].L), arc: 10 });
    }
    if (S.parts.length > 220) S.parts.splice(0, S.parts.length - 220);
    stepParts(g, S);
    // the split
    const by = H * (phone ? 0.84 : 0.84), bx0 = x0 - 30, bx1 = x1 - 10, bh = phone ? 14 : 18; let acc = 0;
    const share = [0, 0, 0, 0]; cols2.forEach((q) => { const s = q.T / st; if (q.L === 0) share[0] += s; else if (q.L === 1) share[1] += s; else if (q.L === -2) share[3] += s; else share[2] += s; });
    share.forEach((s, L) => { if (s <= 0) return; const xa = lerp(bx0, bx1, acc), xb = lerp(bx0, bx1, acc + s); g.ctx.fillStyle = g.rgba(cols[L], 0.8); g.ctx.fillRect(xa, by, Math.max(1.5, xb - xa), bh); acc += s; });
    let lx = bx0, ly = by + bh + 14; share.forEach((s, L) => { if (s <= 0) return; const t = `${["elastic", "2⁺", "higher", "γ"][L]} ${s >= 0.1 ? (100 * s).toFixed(0) : s >= 0.001 ? (100 * s).toFixed(1) : (100 * s).toFixed(3)} %`; g.ctx.font = "600 12px sans-serif"; const tw = g.ctx.measureText(WT.tr ? WT.tr(t) : t).width;
      if (lx > bx0 && lx + tw > W - 6) { lx = bx0; ly += 16; } // wrap rather than run off a phone
      g.label(t, lx, ly, { color: cols[L], size: 12, weight: 600, align: "left" }); lx += Math.max(phone ? 62 : 80, tw + 18); });
    g.label("Hauser–Feshbach split: T / ΣT for each exit", bx0, by - 12, { color: c.ink, size: 12, weight: 600, align: "left" });
  }

  // ---------- scene 3: HF vs WFC, summed ----------
  function drawWfc(g, S, dt) {
    const { W, H, c } = g, phone = W < 600, E = Math.pow(10, S.lgE), cols = COLS(c);
    const key = S.lgE.toFixed(3);
    if (!S.wc || S.wc.key !== key) S.wc = { key, h0: hf(E, 0), h1: hf(E, 1) };
    const { h0, h1 } = S.wc, v0 = [h0.ce, h0.n1, h0.n2, h0.g], v1 = [h1.ce, h1.n1, h1.n2, h1.g], wv = S.withW;
    const x0 = W * 0.1, x1 = W * 0.95, cw = (x1 - x0) / 4;
    const yM = H * 0.38, span = H * (phone ? 0.17 : 0.2), RY = (r) => yM - clamp(log10(r) / log10(2), -1, 1) * span;
    g.line(x0, yM, x1, yM, c.soft, 1.4, 0.8);
    g.label("×1", x0 - 6, yM, { color: c.soft, size: 11, align: "right" });
    [1.5, 2, 0.75, 0.5].forEach((r) => { g.line(x0, RY(r), x1, RY(r), c.line, 1, 0.9, [3, 4]); g.label(`×${r}`, x0 - 6, RY(r), { color: c.faint, size: 10, align: "right" }); });
    for (let L = 0; L < 4; L++) {
      const xc = x0 + (L + 0.5) * cw, open = v0[L] > 1e-9, rTrue = open ? v1[L] / v0[L] : 1, r = Math.exp(Math.log(rTrue) * wv), yR = RY(r);
      if (open) {
        const top = Math.min(yR, yM), hgt = Math.abs(yR - yM), bw = Math.min(46, cw * 0.4);
        g.ctx.save(); g.ctx.fillStyle = g.rgba(cols[L], 0.75); g.ctx.fillRect(xc - bw / 2, top, bw, Math.max(1.5, hgt)); g.ctx.restore();
        g.label(`×${rTrue.toFixed(2)}`, xc, yR + (rTrue >= 1 ? -14 : 14), { color: cols[L], size: phone ? 13 : 15, weight: 600, serif: true, bg: true, alpha: 0.25 + 0.75 * wv });
      } else g.label("closed", xc, yM - 14, { color: c.faint, size: 11 });
      const nm2 = phone ? EXIT2[L] : [EXIT[L]]; // phone columns are ~80 px wide: names on two short lines
      nm2.forEach((t, i) => g.label(t, xc, H * 0.08 + i * 13, { color: cols[L], size: phone ? 11 : 13, weight: 600 }));
      if (open) g.label(`${fmtMb(lerp(v0[L], v1[L], wv))} mb`, xc, H * 0.08 + (phone ? 30 : 18), { color: c.ink, size: 12 });
    }
    // particles: shares of the compound flux per exit, with or without the correction
    const shares = [0, 1, 2, 3].map((L) => lerp(v0[L], v1[L], wv)), tot = shares.reduce((s, v) => s + v, 0);
    const yb = H * 0.8, cnx = W * 0.5, cny = H * 0.66;
    g.glow(cnx, cny, 34, c.warm, 0.38); g.ball(cnx, cny, 9, c.warm);
    S.spawn += dt * 22;
    while (S.spawn > 1) { S.spawn -= 1; let u = Math.random() * tot, L = 0; for (let k = 0; k < 4; k++) { u -= shares[k]; if (u <= 0) { L = k; break; } } S.parts.push({ x: cnx, y: cny, tx: x0 + (L + 0.5) * cw + (Math.random() - 0.5) * 30, ty: yb, t0: S.time, dur: 0.9, col: cols[L], arc: 26, r: 2.6 }); }
    if (S.parts.length > 260) S.parts.splice(0, S.parts.length - 260);
    stepParts(g, S);
    g.line(x0, yb + 6, x1, yb + 6, c.soft, 1.2, 0.6);
    g.label(wv > 0.5 ? "with Moldauer's correction" : "Hauser–Feshbach without correction", W / 2, yb + 26, { color: c.ink, size: phone ? 12 : 14, weight: 600, serif: true, bg: true });
    g.label(`compound formation ${fmtMb(h0.cn)} mb at ${eTxt(E)}`, W / 2, yb + 46, { color: c.soft, size: 12, bg: true });
  }

  // ---------- scene 4: ratio curves against energy ----------
  function drawCurves(g, S) {
    const { W, H, c } = g, phone = W < 600, C = curves(), cols = COLS(c);
    const x0 = W * (phone ? 0.12 : 0.1), x1 = W * 0.95, yT = H * 0.12, yB = H * (phone ? 0.76 : 0.8);
    const lo = C.lg[0], hi = C.lg[C.lg.length - 1], X = (lg) => lerp(x0, x1, (lg - lo) / (hi - lo));
    const rmin = 0.5, rmax = 2.5, Y = (r) => lerp(yB, yT, (log10(r) - log10(rmin)) / (log10(rmax) - log10(rmin)));
    [0.5, 0.75, 1, 1.5, 2, 2.5].forEach((r) => { g.line(x0, Y(r), x1, Y(r), r === 1 ? c.soft : c.line, r === 1 ? 1.4 : 1, 0.9, r === 1 ? null : [3, 4]); g.label(`×${r}`, x0 - 6, Y(r), { color: c.faint, size: 10, align: "right" }); });
    [-3, -2, -1, 0].forEach((d) => { g.line(X(d), yB, X(d), yB + 5, c.soft, 1); g.label(d === -3 ? "1 keV" : d === -2 ? "10 keV" : d === -1 ? "100 keV" : "1 MeV", X(d), yB + 16, { color: c.faint, size: 10 }); });
    { const x = X(log10(LEV[1].e)); g.line(x, yT, x, yB, cols[1], 1, 0.5, [2, 4]); g.label("2⁺ opens", x - 4, yT + 8, { color: cols[1], size: 11, align: "right", bg: true }); }
    { const x = X(log10(EC)); g.line(x, yT, x, yB, cols[2], 1, 0.5, [2, 4]); g.label(phone ? "continuum" : "continuum opens", x - 4, yT + 26, { color: cols[2], size: 11, align: "right", bg: true }); }
    const line = (arr, k, col, dash, w) => { const pts = []; C.lg.forEach((lg, i) => { const v = arr[i][k]; if (isFinite(v) && v > 0) pts.push([X(lg), Y(clamp(v, rmin, rmax))]); }); g.poly(pts, col, w, 1, dash); };
    line(C.m, "ce", cols[0], null, 2.6); line(C.h, "ce", cols[0], [6, 5], 2);
    line(C.m, "g", cols[3], null, 2.6); line(C.h, "g", cols[3], [6, 5], 2);
    line(C.m, "n1", cols[1], null, 2); line(C.h, "n1", cols[1], [6, 5], 1.6);
    // a tracer runs along the Moldauer curves, low energy to high, so the eye follows each one through the thresholds
    { const u = (((S.time * 0.12) % 1) + 1) % 1, fi = u * (C.lg.length - 1), i0 = Math.floor(fi), f = fi - i0, i1 = Math.min(i0 + 1, C.lg.length - 1);
      [["ce", 0], ["g", 3], ["n1", 1]].forEach(([k, L]) => { const a = C.m[i0][k], b = C.m[i1][k]; if (!(a > 0) || !(b > 0)) return; const xx = X(lerp(C.lg[i0], C.lg[i1], f)), yy = Y(clamp(lerp(a, b, f), rmin, rmax)); g.glow(xx, yy, 16, cols[L], 0.55); g.dot(xx, yy, 3.2, cols[L]); }); }
    // the current energy
    const lg = clamp(S.lgE, lo, hi), x = X(lg), E = Math.pow(10, lg);
    const key = lg.toFixed(3); if (!S.cv || S.cv.key !== key) S.cv = { key, r0: hf(E, 0), r1: hf(E, 1), r2: hf(E, 2) };
    const { r0, r1, r2 } = S.cv;
    g.line(x, yT, x, yB, c.ink, 1.2, 0.5);
    [["ce", 0], ["g", 3], ["n1", 1]].forEach(([k, L]) => { if (!(r0[k] > 1e-9)) return; g.dot(x, Y(clamp(r1[k] / r0[k], rmin, rmax)), 5, cols[L]); g.ring(x, Y(clamp(r2[k] / r0[k], rmin, rmax)), 5, cols[L], 1.6); });
    g.label(`elastic ×${(r1.ce / r0.ce).toFixed(2)} (Moldauer) · ×${(r2.ce / r0.ce).toFixed(2)} (HRTW)`, W / 2, H * (phone ? 0.86 : 0.88), { color: cols[0], size: phone ? 11 : 13, weight: 600, bg: true });
    g.label(`capture ×${(r1.g / r0.g).toFixed(2)} (Moldauer) · ×${(r2.g / r0.g).toFixed(2)} (HRTW)`, W / 2, H * (phone ? 0.91 : 0.92), { color: cols[3], size: phone ? 11 : 13, weight: 600, bg: true });
    if (r0.n1 > 1e-9) g.label(`first 2⁺ ×${(r1.n1 / r0.n1).toFixed(2)} (Moldauer) · ×${(r2.n1 / r0.n1).toFixed(2)} (HRTW)`, W / 2, H * (phone ? 0.96 : 0.96), { color: cols[1], size: phone ? 11 : 13, weight: 600, bg: true });
    g.label("solid: Moldauer · dashed: HRTW", x1, yT - 16, { color: c.soft, size: 11, align: "right" });
    if (!phone) g.label("σ with correction / σ without", x0, yT - 16, { color: c.ink, size: 12, weight: 600, align: "left" });
  }

  // ---------- scene 5: the limits 3 and 2 ----------
  function drawLimit(g, S, dt) {
    const { W, H, c } = g, phone = W < 600, N = Math.round(clamp(S.nch, 2, 60));
    const x0 = W * (phone ? 0.12 : 0.1), x1 = W * 0.95, yT = H * (phone ? 0.15 : 0.1), yB = H * (phone ? 0.56 : 0.6);
    const lo = -2, hi = 2.2, X = (lg) => lerp(x0, x1, (lg - lo) / (hi - lo)), Y = (w) => lerp(yB, yT, (w - 1) / 2.3);
    [1, 1.5, 2, 3].forEach((w) => { g.line(x0, Y(w), x1, Y(w), w === 1 ? c.soft : c.line, 1, 0.9, w === 1 ? null : [3, 4]); g.label(`${w}`, x0 - 6, Y(w), { color: c.faint, size: 11, align: "right" }); });
    [-2, -1, 0, 1, 2].forEach((d) => g.label(d === 0 ? "1" : d === 1 ? "10" : d === 2 ? "100" : `10${sup(d)}`, X(d), yB + 14, { color: c.faint, size: 10 }));
    g.label("ΣT = 2πΓ/D →", x1, yB + 30, { color: c.faint, size: 11, align: "right" });
    g.label("elastic enhancement Wₐₐ", x0, yT - (phone ? 34 : 16), { color: c.ink, size: 12, weight: 600, align: "left" });
    const top = Math.min(hi, log10(0.97 * N));
    if (!S.lc || S.lc.N !== N) {
      const m = [], h = []; for (let i = 0; i <= 90; i++) { const lg = lo + (top - lo) * i / 90, st = Math.pow(10, lg); m.push([lg, limitW(N, st, 1)]); h.push([lg, limitW(N, st, 2)]); }
      S.lc = { N, m, h };
    }
    const pts = (arr) => arr.map((p) => [X(p[0]), Y(clamp(p[1], 1, 3.3))]);
    g.poly(pts(S.lc.m), c.neutron, 2.8); g.poly(pts(S.lc.h), c.neutron, 2, 0.8, [6, 5]);
    if (top < hi) { g.line(X(top), yT, X(top), yB, c.faint, 1, 0.6, [2, 4]); g.label("T → 1 per channel", X(top) - 4, yB - 12, { color: c.faint, size: 10, align: "right", bg: true }); }
    { const ex = 3 * N / (N + 2), xd = X(lo), yd = Y(ex), ctx = g.ctx; ctx.save(); ctx.fillStyle = c.warm; ctx.beginPath(); ctx.moveTo(xd, yd - 7); ctx.lineTo(xd + 6, yd); ctx.lineTo(xd, yd + 7); ctx.lineTo(xd - 6, yd); ctx.closePath(); ctx.fill(); ctx.restore(); g.label(`exact, isolated: 3N/(N+2) = ${ex.toFixed(2)}`, xd + 12, yd + 16, { color: c.warm, size: 11, align: "left", bg: true }); }
    g.label("Porter–Thomas: 3", X(lo) + 6, Y(3) - 12, { color: c.ink, size: 11, align: "left", bg: true });
    g.label("Ericson: 2", X(hi) - 6, Y(2) + 14, { color: c.ink, size: 11, align: "right", bg: true });
    g.label("solid: Moldauer · dashed: HRTW", x1, yT - 16, { color: c.soft, size: 11, align: "right" });
    // the moving point: a slow sweep in sum T
    S.lim = (((S.lim + dt / 10) % 1) + 1) % 1;
    const u = 0.5 - 0.5 * Math.cos(TAU * S.lim), lgx = lerp(lo + 0.05, top - 0.02, u), stx = Math.pow(10, lgx), w = limitW(N, stx, 1);
    g.glow(X(lgx), Y(w), 18, c.warm, 0.5); g.dot(X(lgx), Y(w), 6, c.warm);
    g.label(`${N} channels · ΣT = ${stx < 1 ? stx.toFixed(2) : stx.toFixed(1)} · Wₐₐ = ${w.toFixed(2)}`, W / 2, yB + (phone ? 50 : 56), { color: c.warm, size: phone ? 12 : 14, weight: 600, bg: true });
    // inset: resonances with Gamma/D = sum T / 2 pi on a ladder of unit mean spacing
    const iy = H * 0.92, ih = H * (phone ? 0.16 : 0.17), ix0 = W * 0.08, ix1 = W * 0.92, G = stx / TAU, nL = 14;
    if (!S.lad) { const r = rng(5), lev = []; let e = -2; for (let i = 0; i < nL + 8; i++) { e += 0.45 + 1.1 * r(); const z = Math.sqrt(-2 * Math.log(1 - r())) * Math.cos(TAU * r()); lev.push({ e, h: z * z + 0.02 }); } S.lad = lev; }
    const XE = (x) => lerp(ix0, ix1, x / nL), prof = [];
    for (let i = 0; i <= 320; i++) { const x = nL * i / 320; let s = 0; for (const q of S.lad) s += q.h * (G * G / 4) / ((x - q.e) ** 2 + G * G / 4); prof.push(s); }
    const mx = Math.max(...prof), pts2 = prof.map((v, i) => [XE(nL * i / 320), iy - ih * v / mx]);
    g.ground(pts2, c.neutron, ih * 0.6, 0.25); g.poly(pts2, c.neutron, 1.8);
    g.label(G < 0.12 ? "isolated resonances: Γ ≪ D" : G < 1.2 ? "resonances begin to overlap" : "strongly overlapping: Γ ≫ D", W / 2, iy + 14, { color: c.soft, size: 12, bg: true });
  }
})();
