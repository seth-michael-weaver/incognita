/* Chapter 17 (Expert): the optical model, solved (omp/parameters.py, omp/potential.py, omp/schrodinger.py).
 * Scenes (S.mode): "pot"    = the Koning-Delaroche potential against r: real volume well, imaginary volume and surface terms,
 *                              spin-orbit; probe neutrons cross at the incident energy, fading with the local mean free path;
 *                              a strip shows how the depths V_V, W_V, W_D change with energy;
 *                   "wave"   = the radial wave u_lj(r), Numerov-integrated through the complex potential, animated as
 *                              Re[u e^(-i w t)], with the free wave F_l dashed;
 *                   "smat"   = the S-matrix element in the complex plane, its path as the energy sweeps, T = 1 - |S|^2;
 *                   "so"     = T_lj for every l, j = l +- 1/2 (spin-orbit on/off);
 *                   "sums"   = sigma_R, sigma_tot, shape elastic against energy;
 *                   "s0"     = T_0 at low energy: slope 1/2 on log-log, the s-wave strength function S_0.
 * Everything is computed here: KD03 global neutron parameters (Koning & Delaroche, Nucl. Phys. A 713 (2003) 231) for
 * A = 56, Z = 26; U = -V_V f - i W_V f + 4 i a_D W_D df_D/dr + 2 (V_so + i W_so) (1/r) df_so/dr <l.sigma>; Numerov on h = 0.04 fm
 * to 15 fm; S from the ratio u(r1)/u(r2) against H(+-) = G +- iF (Riccati-Bessel, F by downward recursion). Non-relativistic
 * kinematics (the engine uses ECIS's relativistic ones), so numbers differ from the engine's by a few per cent. */
(function () {
  const { TAU, clamp, lerp, smooth } = WT.util;
  const A = 56, Z = 26, N = A - Z, ASYM = (N - Z) / A, A3 = Math.cbrt(A), HB2M = 20.7355, CM = A / (A + 1);
  const KD = {
    v1: 59.30 - 21.0 * ASYM - 0.024 * A, v2: 0.007228 - 1.48e-6 * A, v3: 1.994e-5 - 2.0e-8 * A, v4: 7e-9,
    w1: 12.195 + 0.0167 * A, w2: 73.55 + 0.0795 * A, d1: 16.0 - 16.0 * ASYM, d2: 0.0180 + 0.003802 / (1 + Math.exp((A - 156) / 8)), d3: 11.5,
    vso1: 5.922 + 0.0030 * A, vso2: 0.0040, wso1: -3.1, wso2: 160, ef: -11.2814 + 0.02646 * A,
    RV: (1.3039 - 0.4054 / A3) * A3, aV: 0.6778 - 1.487e-4 * A, RD: (1.3424 - 0.01585 * A3) * A3, aD: 0.5446 - 1.656e-4 * A,
    RS: (1.1854 - 0.647 / A3) * A3, aS: 0.59,
  };
  function depths(E) {
    const f = E - KD.ef;
    return {
      VV: KD.v1 * (1 - KD.v2 * f + KD.v3 * f * f - KD.v4 * f * f * f), WV: KD.w1 * f * f / (f * f + KD.w2 * KD.w2),
      WD: KD.d1 * f * f * Math.exp(-KD.d2 * f) / (f * f + KD.d3 * KD.d3), VS: KD.vso1 * Math.exp(-KD.vso2 * f), WS: KD.wso1 * f * f / (f * f + KD.wso2 * KD.wso2),
    };
  }
  const ws = (r, R, a) => 1 / (1 + Math.exp((r - R) / a));
  const gsurf = (r, R, a) => { const e = Math.exp((r - R) / a); return e / ((1 + e) * (1 + e)); };   // = -a df/dr, peak 1/4 at R
  /** complex potential pieces at r (MeV): real, imaginary, and the spin-orbit form (1/r) df_so/dr times 2 fm^2 */
  function potAt(r, d, so) {
    const fv = ws(r, KD.RV, KD.aV), gd = gsurf(r, KD.RD, KD.aD), dso = -gsurf(r, KD.RS, KD.aS) / KD.aS / Math.max(r, 1e-3) * 2.0;
    return { re: -d.VV * fv, imV: -d.WV * fv, imD: -4 * d.WD * gd, soR: d.VS * dso * so, soI: d.WS * dso * so };   // 4 a_D W_D df/dr = -4 W_D g
  }
  const kOf = (E) => Math.sqrt(E) * CM / Math.sqrt(HB2M);           // fm^-1 (non-relativistic)
  const HS = 0.04, RMAX = 15, NR = Math.round(RMAX / HS);
  /** Riccati-Bessel F_l (downward recursion, normalised on F_0 or F_1) and G_l (upward) at rho */
  function riccati(l, rho) {
    let G0 = Math.cos(rho), G1 = Math.cos(rho) / rho + Math.sin(rho), G = l === 0 ? G0 : G1;
    for (let k = 1; k < l; k++) { const g2 = (2 * k + 1) / rho * G1 - G0; G0 = G1; G1 = g2; G = g2; }
    const Ls = l + 30 + Math.ceil(rho); let fp = 0, fc = 1e-30, Fl = 0, F0 = 0, F1 = 0;
    for (let k = Ls; k >= 1; k--) { const fm = (2 * k + 1) / rho * fc - fp; fp = fc; fc = fm; if (k - 1 === l) Fl = fc; if (k - 1 === 1) F1 = fc; if (k - 1 === 0) F0 = fc; if (Math.abs(fc) > 1e200) { fp *= 1e-200; fc *= 1e-200; Fl *= 1e-200; F1 *= 1e-200; F0 *= 1e-200; } }
    if (l === 0) Fl = F0;
    const s0 = Math.sin(rho), s1 = Math.sin(rho) / rho - Math.cos(rho);
    const sc = Math.abs(s0) > Math.abs(s1) ? s0 / F0 : s1 / F1;
    return { F: Fl * sc, G };
  }
  /** integrate one (l, j) at lab energy E: returns S (complex), the scaled wave u(r) (arrays re, im) and the free F_l(kr).
   *  opts: noAbs (imaginary parts off), noSO (spin-orbit off), keep (store the wave). */
  function solve(l, j, E, opts = {}) {
    const d = depths(E), k = kOf(E), k2 = k * k, c2 = CM / HB2M, ls = l === 0 ? 0 : j > l ? l : -(l + 1);
    const ur = new Float64Array(NR + 1), ui = new Float64Array(NR + 1), qr = new Float64Array(NR + 1), qi = new Float64Array(NR + 1);
    for (let n = 1; n <= NR; n++) {
      const r = n * HS, p = potAt(r, d, opts.noSO ? 0 : ls), im = opts.noAbs ? 0 : p.imV + p.imD + p.soI;
      qr[n] = l * (l + 1) / (r * r) + c2 * (p.re + p.soR) - k2; qi[n] = c2 * im;
    }
    if (l === 0) { const p = potAt(0, d, 0); qr[0] = c2 * p.re - k2; qi[0] = opts.noAbs ? 0 : c2 * (p.imV + p.imD); }
    ur[1] = Math.pow(HS, l + 1); const h12 = HS * HS / 12;
    for (let n = 1; n < NR; n++) {
      // (1 - h2/12 Q_{n+1}) u_{n+1} = 2 (1 + 5 h2/12 Q_n) u_n - (1 - h2/12 Q_{n-1}) u_{n-1}
      const ar = 1 + 5 * h12 * qr[n], ai = 5 * h12 * qi[n];
      let br = 2 * (ar * ur[n] - ai * ui[n]), bi = 2 * (ar * ui[n] + ai * ur[n]);
      if (n > 1 || l === 0) { const cr = 1 - h12 * qr[n - 1], ci = -h12 * qi[n - 1]; br -= cr * ur[n - 1] - ci * ui[n - 1]; bi -= cr * ui[n - 1] + ci * ur[n - 1]; }
      const dr = 1 - h12 * qr[n + 1], di = -h12 * qi[n + 1], dd = dr * dr + di * di;
      ur[n + 1] = (br * dr + bi * di) / dd; ui[n + 1] = (bi * dr - br * di) / dd;
      if (Math.abs(ur[n + 1]) + Math.abs(ui[n + 1]) > 1e150) for (let m = 0; m <= n + 1; m++) { ur[m] *= 1e-150; ui[m] *= 1e-150; }
    }
    const na = NR - 12, nb = NR, A1 = riccati(l, k * na * HS), B1 = riccati(l, k * nb * HS);
    // R = u(a) / u(b);  S = (Hm_a - R Hm_b) / (Hp_a - R Hp_b),  H(+-) = G +- iF
    const ubr = ur[nb], ubi = ui[nb], ubb = ubr * ubr + ubi * ubi, Rr = (ur[na] * ubr + ui[na] * ubi) / ubb, Ri = (ui[na] * ubr - ur[na] * ubi) / ubb;
    const numr = A1.G - (Rr * B1.G + Ri * B1.F), numi = -A1.F - (Ri * B1.G - Rr * B1.F);
    const denr = A1.G - (Rr * B1.G - Ri * B1.F), deni = A1.F - (Ri * B1.G + Rr * B1.F);
    const dn = denr * denr + deni * deni, Sr = (numr * denr + numi * deni) / dn, Si = (numi * denr - numr * deni) / dn;
    const out = { Sr, Si, T: clamp(1 - (Sr * Sr + Si * Si), 0, 1), k };
    if (opts.keep) {
      // scale so that outside u = (i/2)(H- - S H+): at b, target = (i/2)[(G - iF) - S (G + iF)]
      const hr = B1.G - (Sr * B1.G - Si * B1.F), hi = -B1.F - (Sr * B1.F + Si * B1.G), tr = -hi / 2, ti = hr / 2;
      const Cr = (tr * ubr + ti * ubi) / ubb, Ci = (ti * ubr - tr * ubi) / ubb;
      const wr = new Float64Array(NR + 1), wi = new Float64Array(NR + 1), fr = new Float64Array(NR + 1);
      for (let n = 0; n <= NR; n++) { wr[n] = Cr * ur[n] - Ci * ui[n]; wi[n] = Cr * ui[n] + Ci * ur[n]; fr[n] = n ? riccati(l, k * n * HS).F : 0; }
      Object.assign(out, { wr, wi, fr });
    }
    return out;
  }
  /** all partial waves at E: T and S per (l, j), and the cross sections in barns */
  function allWaves(E, opts = {}) {
    const k = kOf(E), pk = Math.PI / (k * k) / 100, L = [];
    let sR = 0, sT = 0;
    for (let l = 0; l <= 24; l++) {
      const p = solve(l, l + 0.5, E, opts), m = l ? solve(l, l - 0.5, E, opts) : null;
      L.push({ l, Tp: p.T, Tm: m ? m.T : 0 });
      sR += (l + 1) * p.T + (m ? l * m.T : 0); sT += (l + 1) * (1 - p.Sr) + (m ? l * (1 - m.Sr) : 0);
      if (l > 3 && p.T < 1e-7) break;
    }
    return { L, sR: pk * sR, sT: 2 * pk * sT, sE: 2 * pk * sT - pk * sR };
  }
  let SUMS = null;
  function sums() {
    if (SUMS) return SUMS; const out = [];
    for (let i = 0; i <= 56; i++) { const lg = -2 + 3.7 * i / 56, E = Math.pow(10, lg), a = allWaves(E); out.push({ lg, sR: a.sR, sT: a.sT, sE: a.sE }); }
    return (SUMS = out);
  }
  const log10 = (x) => Math.log(x) / Math.LN10;
  const SHOT = /[?&]shot=/.test(location.search);

  Object.assign(WT.glossary || (WT.glossary = {}), {
    koningDelaroche: {
      term: "Koning–Delaroche potential", aliases: ["Koning–Delaroche", "KD03"],
      short: "The global optical potential for neutrons and protons of A. J. Koning and J.-P. Delaroche (2003), from 1 keV to 200 MeV and mass 24 to 209.",
      more: "Its depths, radii and diffusenesses are smooth functions of energy, mass and neutron excess, fitted once to a large body of measured cross sections and angular distributions. It is the default for nucleons in TALYS and in the engine.",
      chapter: "optical",
    },
    numerov: {
      term: "Numerov method", aliases: ["Numerov method", "Numerov"],
      short: "A three-point rule for integrating second-order equations without a first-derivative term, such as the radial Schrödinger equation, with an error of order h⁶ per step.",
      formula: "(1 − h²Q_n+1/12) u_n+1 = 2(1 + 5h²Q_n/12) u_n − (1 − h²Q_n−1/12) u_n−1",
      chapter: "optical",
    },
    sMatrix: {
      term: "S-matrix", aliases: ["S-matrix"],
      short: "The amplitudes that connect incoming and outgoing waves; for elastic scattering in one partial wave, a single complex number S = η e^(2iδ).",
      more: "|S| = 1 means nothing is absorbed and only the phase δ changes; the shortfall 1 − |S|² is the transmission coefficient, the flux taken into reactions.",
      chapter: "optical",
    },
    spinOrbit: {
      term: "Spin–orbit term", aliases: ["spin–orbit", "spin-orbit"],
      short: "The part of the nuclear potential that depends on whether the nucleon's spin is parallel or antiparallel to its orbital angular momentum.",
      more: "It is attractive for j = l + ½ and repulsive for j = l − ½, peaked at the nuclear surface. The same interaction produces the magic numbers of the shell model.",
      chapter: "optical",
    },
  });

  WT.chapter("optical", {
    num: "Chapter 17", title: "The optical model, solved", short: "Optical model, solved",
    lead: "Chapter 2 drew the optical potential as a cloudy glass ball. Here it is as the engine uses it: a global parameterisation, a radial Schrödinger equation integrated step by step, and a matching condition that turns the wave into transmission coefficients.",
    html: `
<div class="step">
  <h3>The Koning–Delaroche potential</h3>
  <p>For neutrons and protons on spherical targets the default is the potential of <b>Koning–Delaroche</b> (KD03): Woods–Saxon shapes whose depths change smoothly with energy and with the target's mass and neutron excess, from a global formula or, for the nuclei KD03 fitted one by one, such as iron-56, from a local fit of the same form. The picture uses the global formula for neutrons on iron-56. The real well (blue) binds; the imaginary parts (red) absorb, in the volume and, at low energy mostly, in a thin shell at the surface.</p>
  <div class="ctl"><label for="op-e">Neutron energy (MeV)</label><input id="op-e" type="range" data-bind="E" min="0.1" max="80" step="0.1" value="5"><output data-show="E" data-fmt="1"></output></div>
  <div class="formula">U(r) = −V<sub>V</sub> f(r) − iW<sub>V</sub> f(r) + 4i a<sub>D</sub>W<sub>D</sub> df<sub>D</sub>/dr + 2(V<sub>so</sub> + iW<sub>so</sub>) (1/r) df<sub>so</sub>/dr ⟨l·σ⟩</div>
  <p>The probe neutrons cross at the energy you set and fade where the absorption bites: their mean free path is ħ<i>v</i>/2|<i>W</i>|. Each depth is a function of <i>E</i> − <i>E</i><sub>F</sub>, measured from the Fermi energy: the real depth falls slowly, the surface absorption <i>W</i><sub>D</sub> peaks near 10 MeV, and the volume absorption <i>W</i><sub>V</sub> grows steadily until it takes over, above about 45 MeV here.</p>
</div>
<div class="step">
  <h3>Integrating the radial equation</h3>
  <p>Each partial wave obeys its own radial equation. The engine integrates it outward from <i>r</i> = 0 with the <b>Numerov method</b>, a three-point rule accurate to the sixth power of the step, through the full complex potential.</p>
  <div class="formula">u″<sub>lj</sub>(r) = [ l(l+1)/r² + (2μ/ħ²) U<sub>lj</sub>(r) − k² ] u<sub>lj</sub>(r)</div>
  <div class="ctl"><label for="op-l">Partial wave l</label><input id="op-l" type="range" data-bind="L" min="0" max="10" step="1" value="1" data-instant><output data-show="L" data-fmt="0"></output></div>
  <div class="ctl"><label for="op-e2">Neutron energy (MeV)</label><input id="op-e2" type="range" data-bind="E" min="0.1" max="80" step="0.1" value="5"><output data-show="E" data-fmt="1"></output></div>
  <p>The solid line is the wave in time, Re[<i>u</i> e<sup>−iωt</sup>]; the dashed line is the free wave, as if the nucleus were not there. Inside the well the wave is shorter (the neutron is faster) and smaller (absorbed); outside, it comes back shifted in phase.</p>
</div>
<div class="step">
  <h3>From the wave to S and T</h3>
  <p>Beyond about 12 fm the potential has vanished and the wave must be a mix of an incoming and an outgoing free wave, <i>u</i> ∝ <i>H</i><sup>−</sup> − <i>S</i> <i>H</i><sup>+</sup>. Matching the integrated <i>u</i> at two radii fixes the <b>S-matrix</b> element <i>S<sub>lj</sub></i>: the outgoing amplitude, with its phase.</p>
  <div class="btns"><button class="btn ghost" data-act="abs" aria-pressed="false">Switch off absorption</button></div>
  <div class="formula">S<sub>lj</sub> = η<sub>lj</sub> e<sup>2iδ<sub>lj</sub></sup> ,  T<sub>lj</sub> = 1 − |S<sub>lj</sub>|²</div>
  <p>The dot is <i>S</i> in the complex plane, inside the unit circle; its trail is the path as the energy sweeps from 0.1 to 40 MeV. Without absorption |<i>S</i>| = 1: the dot runs on the circle, the wave only changes phase, and <i>T</i> = 0. The distance inside the circle is what the compound nucleus and every other reaction receive.</p>
</div>
<div class="step">
  <h3>Spin–orbit splits j</h3>
  <p>The <b>spin–orbit</b> term is attractive for <i>j</i> = <i>l</i> + ½ and repulsive for <i>j</i> = <i>l</i> − ½. It is small, a few MeV at the surface, but it moves the two transmissions of each <i>l</i> apart, most near the partial wave that grazes the surface.</p>
  <div class="ctl"><label for="op-e3">Neutron energy (MeV)</label><input id="op-e3" type="range" data-bind="E" min="0.1" max="80" step="0.1" value="5"><output data-show="E" data-fmt="1"></output></div>
  <div class="btns"><button class="btn ghost" data-act="so" aria-pressed="false">Switch off spin–orbit</button></div>
  <p>Hauser–Feshbach (Chapter 16) uses the two separately; summed with their weights, (<i>l</i>+1)<i>T</i><sub>l,l+½</sub> + <i>l</i> <i>T</i><sub>l,l−½</sub>, they give the reaction cross section almost unchanged, which is why total cross sections barely constrain the spin–orbit strength and polarisation data are needed.</p>
</div>
<div class="step">
  <h3>The cross sections</h3>
  <p>Summing the partial waves gives the observables the potential is fitted to. The reaction cross section counts the flux removed, the total cross section follows from the forward amplitude, and their difference is shape elastic scattering.</p>
  <div class="formula">σ<sub>R</sub> = (π/k²) Σ<sub>l</sub> [(l+1)T<sub>l,l+½</sub> + l T<sub>l,l−½</sub>] ,  σ<sub>tot</sub> = (2π/k²) Σ<sub>lj</sub> (j+½)(1 − Re S<sub>lj</sub>)</div>
  <div class="ctl"><label for="op-e4">Neutron energy (MeV)</label><input id="op-e4" type="range" data-bind="E" min="0.2" max="50" step="0.1" value="5"><output data-show="E" data-fmt="1"></output></div>
  <p>KD03 was fitted to such data for many nuclei, from 1 keV to 200 MeV; the total cross section of iron, between 3.5 and 4 b at a few MeV and 2.5 b at 14 MeV, comes out within about 5 per cent without adjustment to this nucleus, broad maxima included: they are the nuclear size seen against the neutron wavelength.</p>
</div>
<div class="step">
  <h3>The low-energy end</h3>
  <p>Below a few keV only the s-wave matters, and <i>T</i><sub>0</sub> grows as √<i>E</i>: a slope of one half on this log–log plot. The constant is the <b>strength function</b> <i>S</i><sub>0</sub> = <i>T</i><sub>0</sub>/(2π√<i>E</i>), with <i>E</i> in eV, the same quantity resonance analyses measure as Σ Γ<sub>n</sub><sup>0</sup>/Δ<i>E</i>.</p>
  <p>A global potential is fitted mostly at MeV energies, and its low-energy end is its weakest point. For iron-56 this one gives <i>S</i><sub>0</sub> ≈ 5.5 × 10⁻⁴, and the local KD03 fit nearly the same, while the measured value (RIPL) is 2.3 ± 0.6 × 10⁻⁴: iron sits near the peak of the 3s size resonance around <i>A</i> ≈ 55, where <i>S</i><sub>0</sub> is most sensitive to the potential. That is why the measured <i>S</i><sub>0</sub> and <i>S</i><sub>1</sub> are a separate, optional input to the engine.</p>
  <div class="aside">In the code: <code>omp/parameters.py</code> (KD03 and the other global potentials), <code>omp/potential.py</code> (the radial form factors), <code>omp/schrodinger.py</code> (Numerov integration and matching, with Coulomb functions by Steed's method for charged particles; it replaces ECIS for spherical targets and is checked against ECIS's T<sub>lj</sub>), <code>ecis/</code> (the coupled-channels port for deformed targets), <code>omp/sfunc.py</code> (optional: measured S₀, S₁). The picture solves the equation itself, non-relativistically, for neutrons on iron-56.</div>
</div>`,
    setup(S) {
      S.set("mode", "pot"); S.to("E", 5, true); S.to("L", 1, true); S.to("absOn", 1, true); S.to("soOn", 1, true);
      S.probes = []; S.spawn = 0; S.sweep = 0;
      const press = (act, on) => document.querySelectorAll(`#optical [data-act="${act}"]`).forEach((b) => b.setAttribute("aria-pressed", String(on)));
      S.on("abs", () => { const off = S.target.absOn > 0.5; S.to("absOn", off ? 0 : 1); press("abs", off); S.path = null; });
      S.on("so", () => { const off = S.target.soOn > 0.5; S.to("soOn", off ? 0 : 1); press("so", off); });
    },
    steps: [
      (S) => { S.set("mode", "pot"); },
      (S) => { S.set("mode", "wave"); },
      (S) => { S.set("mode", "smat"); if (SHOT) S.sweep = 0.35; },
      (S) => { S.set("mode", "so"); },
      (S) => { S.set("mode", "sums"); },
      (S) => { S.set("mode", "s0"); },
    ],
    frame(g, S, dt) {
      if (S.mode === "pot") drawPot(g, S, dt);
      else if (S.mode === "wave") drawWave(g, S);
      else if (S.mode === "smat") drawSmat(g, S, dt);
      else if (S.mode === "so") drawSO(g, S);
      else if (S.mode === "sums") drawSums(g, S);
      else drawS0(g, S);
    },
  });
  WT.mods.optical.calc = { depths, solve, allWaves, KD };

  // radial frame shared by the first two scenes
  function rFrame(g, phone, top, bot) { const x0 = g.W * (phone ? 0.1 : 0.09), x1 = g.W * 0.96; return { x0, x1, X: (r) => lerp(x0, x1, r / RMAX), top, bot }; }
  function rAxis(g, F, y) { const { c } = g; g.line(F.x0, y, F.x1, y, c.soft, 1.2, 0.7); [0, 5, 10, 15].forEach((r) => g.label(`${r} fm`, F.X(r), y + 13, { color: c.faint, size: 10 })); }

  // ---------- scene 1: the potential ----------
  function drawPot(g, S, dt) {
    const { W, H, c } = g, phone = W < 600, E = clamp(S.E, 0.1, 80), d = depths(E);
    const F = rFrame(g, phone, H * 0.05, H * 0.56), y0 = H * (phone ? 0.2 : 0.2), sc = (F.bot - y0) / 56, Y = (u) => y0 - u * sc;
    g.line(F.x0, y0, F.x1, y0, c.soft, 1.2, 0.7);
    g.label("0 MeV", F.x0 - 4, y0, { color: c.faint, size: 10, align: "right" });
    [0, 5, 10, 15].forEach((r) => g.label(`${r} fm`, F.X(r), F.bot + 14, { color: c.faint, size: 10 }));
    // real well, imaginary volume + surface, spin-orbit (for l = 3, j = l + 1/2, as an example of its size)
    const re = [], im = [], ims = [], so = [];
    for (let i = 0; i <= 150; i++) { const r = RMAX * i / 150, p = potAt(r, d, 3); re.push([F.X(r), Y(p.re)]); im.push([F.X(r), Y(p.imV + p.imD)]); ims.push([F.X(r), Y(p.imD)]); if (r > 1) so.push([F.X(r), Y(p.soR)]); }
    g.area([[F.X(0), y0]].concat(re, [[F.X(RMAX), y0]]), c.neutron, 0.14); g.poly(re, c.neutron, 2.6);
    g.area([[F.X(0), y0]].concat(im, [[F.X(RMAX), y0]]), c.proton, 0.2); g.poly(im, c.proton, 2.2); g.poly(ims, c.proton, 1.2, 0.6, [3, 3]);
    g.poly(so, c.alpha, 1.6, 0.9);
    g.label(`real well, depth ${d.VV.toFixed(1)} MeV`, F.X(0.4), Y(-d.VV) - 14, { color: c.neutron, size: phone ? 11 : 12, weight: 600, align: "left", bg: true });
    g.label(`surface absorption, peak ${d.WD.toFixed(1)} MeV`, F.X(KD.RD) + 14, Y(-d.WD) + 16, { color: c.proton, size: phone ? 11 : 12, weight: 600, align: "left", bg: true });
    g.label(`volume absorption ${d.WV.toFixed(1)} MeV`, F.X(0.4), Y(-d.WV) + 16, { color: c.proton, size: phone ? 10 : 11, align: "left", bg: true });
    if (!phone) { const v = potAt(KD.RS + 0.4, d, 3).soR; g.label(`spin–orbit for l = 3, j = 7/2: ${(-v).toFixed(1)} MeV`, F.X(KD.RS + 0.4) + 14, Math.max(Y(v) + 38, Y(-d.WD) + 40), { color: c.alpha, size: 11, align: "left", bg: true }); }
    // probe neutrons at the incident energy: speed from E - Re U, survival from the local mean free path hbar v / 2|W|
    const yE = y0 - 16 - Math.min(E, 40) / 40 * (y0 - F.top - 26); g.line(F.x0, yE, F.x1, yE, c.warm, 1, 0.6, [4, 4]);
    g.label(`E = ${E.toFixed(1)} MeV`, F.x0, yE - 12, { color: c.warm, size: 11, align: "left", bg: true });
    S.spawn += dt * 1.6; if (S.spawn > 1 && S.probes.length < 7) { S.spawn = 0; S.probes.push({ r: RMAX, surv: 1, dir: -1, b: Math.random() }); }
    for (let i = S.probes.length - 1; i >= 0; i--) {
      const q = S.probes[i], p = potAt(Math.max(q.r, 0.05), d, 0), Tk = Math.max(0.05, E - p.re), v = Math.sqrt(2 * Tk / 939.565);   // v / c
      const Wabs = -(p.imV + p.imD), mfp = 197.327 * v / (2 * Math.max(Wabs, 1e-6));       // fm
      const step = dt * 3.2 * (0.35 + v / 0.15);                                           // drawn speed follows v
      q.surv *= Math.exp(-step / mfp); q.r += q.dir * step; if (q.r < 0) { q.r = -q.r; q.dir = 1; }
      if (q.r > RMAX + 0.5 || q.surv < 0.02) { S.probes.splice(i, 1); continue; }
      const x = F.X(Math.abs(q.r)), y = yE + 2 - q.b * 5;
      g.glow(x, y, 12, c.neutron, 0.35 * q.surv); g.ball(x, y, 4.5, c.neutron, q.surv);
      if (q.surv < 0.6 && q.surv > 0.05) g.glow(x, y, 16, c.warm, 0.4 * (1 - q.surv));
    }
    const mfp0 = 197.327 * Math.sqrt(2 * (E + d.VV) / 939.565) / (2 * Math.max(d.WV + 4 * d.WD * gsurf(0, KD.RD, KD.aD), 1e-6));
    const pS = potAt(KD.RD, d, 0), mfpS = 197.327 * Math.sqrt(2 * Math.max(0.05, E - pS.re) / 939.565) / (2 * Math.max(-(pS.imV + pS.imD), 1e-6));
    g.label(`mean free path: ${mfpS < 100 ? mfpS.toFixed(1) : "> 100"} fm at the surface, ${mfp0 < 100 ? mfp0.toFixed(0) : "> 100"} fm in the centre`, W / 2, H * 0.64, { color: c.ink, size: phone ? 11 : 13, weight: 600, bg: true });
    // the depths against energy
    const sy0 = H * (phone ? 0.95 : 0.95), sh = H * (phone ? 0.18 : 0.2), sx0 = W * 0.1, sx1 = W * (phone ? 0.8 : 0.86), EX = (e) => lerp(sx0, sx1, e / 80), DY = (v) => sy0 - v / 60 * sh;
    const lines = [["VV", c.neutron, "real"], ["WV", c.proton, "volume"], ["WD", c.proton, "surface"]];
    lines.forEach(([k, col, nm]) => { const pts = []; for (let e = 0.2; e <= 80; e += 0.8) pts.push([EX(e), DY(depths(e)[k])]); g.poly(pts, col, k === "WD" ? 1.6 : 2, k === "WD" ? 0.7 : 1, k === "WD" ? [5, 4] : null); g.label(nm, sx1 + 6, DY(depths(80)[k]) + (k === "WD" ? 6 : k === "WV" ? -6 : 0), { color: col, size: 10, align: "left" }); });
    g.line(sx0, sy0, sx1, sy0, c.soft, 1, 0.6); [0, 20, 40, 60, 80].forEach((e) => g.label(`${e}`, EX(e), sy0 + 10, { color: c.faint, size: 10 }));
    const xe = EX(E); g.line(xe, sy0 - sh, xe, sy0, c.warm, 1.2, 0.8); [["VV", c.neutron], ["WV", c.proton], ["WD", c.proton]].forEach(([k, col]) => { g.glow(xe, DY(d[k]), 10 + 2 * Math.sin(S.time * 3), col, 0.35); g.dot(xe, DY(d[k]), 4, col); });
    g.label("depths (MeV) against energy (MeV)", sx0, sy0 - sh - 8, { color: c.soft, size: 11, align: "left" });
  }

  // ---------- scene 2: the radial wave ----------
  function waveOf(S) {
    const l = Math.round(S.L), E = clamp(S.E, 0.1, 80), key = `${l}|${E.toFixed(2)}|${S.target.absOn}`;
    if (!S.wv || S.wv.key !== key) S.wv = { key, l, E, s: solve(l, l + 0.5, E, { keep: true, noAbs: S.target.absOn < 0.5 }) };
    return S.wv;
  }
  function drawWave(g, S) {
    const { W, H, c } = g, phone = W < 600, w = waveOf(S), s = w.s, d = depths(w.E);
    const F = rFrame(g, phone, H * 0.1, H * 0.9);
    // potential, faint, in the upper band
    const py0 = H * (phone ? 0.2 : 0.18), psc = H * 0.1 / 55, re = [], im = [];
    for (let i = 0; i <= 120; i++) { const r = RMAX * i / 120, p = potAt(r, d, 0); re.push([F.X(r), py0 - p.re * psc]); im.push([F.X(r), py0 - (p.imV + p.imD) * psc]); }
    g.poly(re, c.neutron, 1.4, 0.45); g.poly(im, c.proton, 1.4, 0.45);
    g.line(F.x0, py0, F.x1, py0, c.line, 1);
    g.label("potential: real (blue), imaginary (red)", F.x0, py0 - H * 0.12, { color: c.faint, size: 11, align: "left" });
    // the wave
    const yc = H * (phone ? 0.6 : 0.58), amp = H * (phone ? 0.17 : 0.2);
    let mx = 0; for (let n = 0; n <= NR; n++) mx = Math.max(mx, Math.hypot(s.wr[n], s.wi[n]), Math.abs(s.fr[n]));
    const sc = amp / Math.max(mx, 1e-9), om = 2.4 * S.time, co = Math.cos(om), si = Math.sin(om);
    const wave = [], env = [], envm = [], free = [];
    for (let n = 0; n <= NR; n += 2) { const x = F.X(n * HS); wave.push([x, yc - sc * (s.wr[n] * co + s.wi[n] * si)]); const m = Math.hypot(s.wr[n], s.wi[n]); env.push([x, yc - sc * m]); envm.push([x, yc + sc * m]); free.push([x, yc - sc * s.fr[n] * co]); }
    g.area(env.concat(envm.slice().reverse()), c.neutron, 0.08);
    g.poly(free, c.faint, 1.4, 0.9, [5, 4]); g.poly(wave, c.neutron, 2.6);
    g.line(F.X(KD.RV), yc - amp - 8, F.X(KD.RV), yc + amp + 8, c.ink, 1, 0.35, [2, 4]);
    g.label("nuclear surface", F.X(KD.RV), yc - amp - 16, { color: c.soft, size: 11 });
    rAxis(g, F, yc + amp + 22);
    const eta = Math.sqrt(s.Sr * s.Sr + s.Si * s.Si), del = 0.5 * Math.atan2(s.Si, s.Sr) * 180 / Math.PI;
    g.label(`l = ${w.l}, j = ${w.l}+½ · E = ${w.E.toFixed(1)} MeV · |S| = ${eta.toFixed(3)} · δ = ${del.toFixed(0)}° · T = ${s.T.toFixed(3)}`, W / 2, H * (phone ? 0.96 : 0.95), { color: c.ink, size: phone ? 11 : 13, weight: 600, bg: true });
    g.label("solid: the wave now · shaded: its size |u| · dashed: free wave", F.x1, yc - amp - 34, { color: c.soft, size: 11, align: "right" });
  }

  // ---------- scene 3: S in the complex plane ----------
  function drawSmat(g, S, dt) {
    const { W, H, c } = g, phone = W < 600, l = Math.round(S.L), noAbs = S.target.absOn < 0.5;
    const key = `${l}|${noAbs}`;
    if (!S.path || S.path.key !== key) { const pts = []; for (let i = 0; i <= 140; i++) { const lg = -1 + (log10(40) + 1) * i / 140, E = Math.pow(10, lg), s = solve(l, l + 0.5, E, { noAbs }); pts.push({ E, Sr: s.Sr, Si: s.Si, T: s.T }); } S.path = { key, pts }; }
    const cx = W * (phone ? 0.5 : 0.42), cy = H * (phone ? 0.4 : 0.47), R = Math.min(W * (phone ? 0.34 : 0.3), H * (phone ? 0.28 : 0.36));
    g.ring(cx, cy, R, c.soft, 1.6, 0.8); g.line(cx - R - 10, cy, cx + R + 10, cy, c.line, 1); g.line(cx, cy - R - 10, cx, cy + R + 10, c.line, 1);
    g.label("Re S", cx + R + 12, cy + 12, { color: c.faint, size: 11, align: "left" }); g.label("Im S", cx + 6, cy - R - 12, { color: c.faint, size: 11, align: "left" });
    g.label("|S| = 1: nothing absorbed", cx, cy + R + 18, { color: c.soft, size: 11 });
    const P = S.path.pts, map = (p) => [cx + R * p.Sr, cy - R * p.Si];
    g.poly(P.map(map), c.neutron, 1.6, 0.5);
    // the sweep: a dot runs along the path, with the T-annulus drawn as the gap to the circle
    S.sweep = (((S.sweep + dt / 8) % 1) + 1) % 1;
    const fi = S.sweep * (P.length - 1), i0 = Math.floor(fi), f = fi - i0, p0 = P[i0], p1 = P[Math.min(i0 + 1, P.length - 1)];
    const p = { Sr: lerp(p0.Sr, p1.Sr, f), Si: lerp(p0.Si, p1.Si, f), T: lerp(p0.T, p1.T, f), E: Math.exp(lerp(Math.log(p0.E), Math.log(p1.E), f)) };
    const [xs, ys] = map(p), ang = Math.atan2(-p.Si, p.Sr);
    g.line(cx, cy, xs, ys, c.neutron, 1.4, 0.6);
    g.line(xs, ys, cx + R * Math.cos(ang), cy + R * Math.sin(ang), c.proton, 3, 0.8);
    g.glow(xs, ys, 18, c.neutron, 0.5); g.dot(xs, ys, 6, c.neutron);
    // the energy set in the text, as a fixed ring on the path
    const Ecur = clamp(S.E, 0.1, 40), sc = solve(l, l + 0.5, Ecur, { noAbs }), [xc, yc2] = map(sc);
    g.ring(xc, yc2, 8, c.warm, 2); g.label(`${Ecur.toFixed(1)} MeV`, xc + 12, yc2 - 10, { color: c.warm, size: 11, align: "left", bg: true });
    if (phone) {
      g.label(`l = ${l}, j = ${l}+½ · E = ${p.E.toFixed(2)} MeV`, W / 2, H * 0.8, { color: c.ink, size: 12, weight: 600, bg: true });
      g.label(`|S| = ${Math.hypot(p.Sr, p.Si).toFixed(3)} · T = 1 − |S|² = ${p.T.toFixed(3)}`, W / 2, H * 0.87, { color: c.proton, size: 12, weight: 600, bg: true });
    } else {
      const tx = W * 0.85, ty = H * 0.2;
      g.label(`l = ${l}, j = ${l}+½`, tx, ty, { color: c.ink, size: 14, weight: 600, serif: true, bg: true });
      g.label(`E = ${p.E.toFixed(2)} MeV`, tx, ty + 20, { color: c.neutron, size: 12, bg: true });
      g.label(`|S| = ${Math.hypot(p.Sr, p.Si).toFixed(3)}`, tx, ty + 38, { color: c.neutron, size: 12, bg: true });
      g.label(`T = 1 − |S|² = ${p.T.toFixed(3)}`, tx, ty + 56, { color: c.proton, size: 12, weight: 600, bg: true });
      g.label("trail: S as E runs 0.1 → 40 MeV", tx, ty + 80, { color: c.soft, size: 11 });
    }
    if (noAbs) g.label("no absorption: S stays on the circle", W / 2, H * (phone ? 0.94 : 0.92), { color: c.proton, size: 13, weight: 600, bg: true });
  }

  // ---------- scene 4: spin-orbit ----------
  function drawSO(g, S) {
    const { W, H, c } = g, phone = W < 600, E = clamp(S.E, 0.1, 80), so = S.soOn;
    const key = `${E.toFixed(2)}`;
    if (!S.sob || S.sob.key !== key) { const on = allWaves(E), off = allWaves(E, { noSO: true }); S.sob = { key, on, off }; }
    const { on, off } = S.sob, n = Math.min(14, Math.max(on.L.length, 6));
    const x0 = W * 0.08, x1 = W * 0.96, yB = H * (phone ? 0.7 : 0.72), yT = H * 0.14, hh = yB - yT, slot = (x1 - x0) / n, bw = slot * 0.32;
    g.line(x0, yT, x1, yT, c.faint, 1, 0.6, [4, 5]); g.label("T = 1", x1, yT - 10, { color: c.faint, size: 11, align: "right" });
    g.line(x0, yB, x1, yB, c.soft, 1.4, 0.8);
    for (let l = 0; l < n; l++) {
      const a = on.L[l] || { Tp: 0, Tm: 0 }, b = off.L[l] || { Tp: 0, Tm: 0 }, xs = x0 + l * slot + slot * 0.15;
      const Tp = lerp(b.Tp, a.Tp, so), Tm = lerp(b.Tp, a.Tm, so);
      const bar = (x, T, col, hol) => { const ctx = g.ctx; ctx.save(); ctx.fillStyle = g.rgba(col, hol ? 0.15 : 0.8); ctx.strokeStyle = col; ctx.lineWidth = 1.3; ctx.fillRect(x, yB - T * hh, bw, T * hh); if (hol) ctx.strokeRect(x + 0.5, yB - T * hh + 0.5, bw - 1, T * hh); ctx.restore(); };
      if (l > 0) bar(xs, Tm, c.alpha, true);
      bar(xs + bw + 2, Tp, c.neutron, false);
      g.label(`${l}`, xs + bw, yB + 13, { color: c.ink, size: 11, weight: 600 });
    }
    g.label("l", x0 - 4, yB + 13, { color: c.faint, size: 11, align: "right" });
    g.label(phone ? "hollow: j = l − ½ · solid: j = l + ½" : "hollow (purple): j = l − ½ · solid (blue): j = l + ½", W / 2, yB + 32, { color: c.soft, size: 12 });
    const rOn = on.sR, rOff = off.sR, rr = lerp(rOff, rOn, so);
    g.label(`reaction cross section ${rr.toFixed(3)} b ${so > 0.5 ? `(without spin–orbit ${rOff.toFixed(3)} b)` : "(spin–orbit off)"}`, W / 2, H * (phone ? 0.88 : 0.88), { color: c.ink, size: phone ? 12 : 14, weight: 600, serif: true, bg: true });
    // a grazing marker: l ~ kR
    const lg = kOf(E) * KD.RV; if (lg < n) { const x = x0 + lg * slot + slot * 0.5; g.line(x, yT, x, yB, c.warm, 1, 0.6, [2, 4]); g.label(`grazing l ≈ kR = ${lg.toFixed(1)}`, x + 4, yT + 12 + 6 * Math.sin(S.time * 2), { color: c.warm, size: 11, align: "left", bg: true }); }
  }

  // ---------- scene 5: the cross sections against energy ----------
  function drawSums(g, S) {
    const { W, H, c } = g, phone = W < 600, P = sums();
    const x0 = W * (phone ? 0.12 : 0.1), x1 = W * 0.95, yT = H * 0.12, yB = H * (phone ? 0.74 : 0.78), lo = -0.7, hi = P[P.length - 1].lg, X = (lg) => lerp(x0, x1, (lg - lo) / (hi - lo));
    const ymax = 8, Y = (b) => lerp(yB, yT, b / ymax);
    [0, 2, 4, 6, 8].forEach((b) => { g.line(x0, Y(b), x1, Y(b), b ? c.line : c.soft, 1, 0.9); g.label(`${b} b`, x0 - 6, Y(b), { color: c.faint, size: 10, align: "right" }); });
    [log10(0.3), 0, 1].forEach((dd) => g.label(dd < -0.1 ? "300 keV" : dd === 0 ? "1 MeV" : "10 MeV", X(dd), yB + 14, { color: c.faint, size: 10 }));
    const L = (k) => P.filter((p) => p.lg >= lo).map((p) => [X(p.lg), Y(Math.min(p[k], ymax))]);
    const tot = L("sT"); g.ground(tot, c.neutron, H * 0.15, 0.18); g.poly(tot, c.neutron, 2.6); g.poly(L("sR"), c.proton, 2.4); g.poly(L("sE"), c.alpha, 2, 0.9, [6, 4]);
    const E = clamp(S.E, 0.2, 50), key = E.toFixed(2); if (!S.sm || S.sm.key !== key) S.sm = { key, a: allWaves(E) };
    const a = S.sm.a, x = X(log10(E)); g.line(x, yT, x, yB, c.warm, 1.2, 0.7);
    [["sT", c.neutron], ["sR", c.proton], ["sE", c.alpha]].forEach(([k, col]) => { g.glow(x, Y(a[k]), 14 + 3 * Math.sin(S.time * 3), col, 0.4); g.dot(x, Y(a[k]), 5, col); });
    g.label(`total ${a.sT.toFixed(2)} b`, x + 8, Y(a.sT) - 12, { color: c.neutron, size: 12, weight: 600, align: "left", bg: true });
    g.label(`reaction ${a.sR.toFixed(2)} b`, x + 8, Y(a.sR) + 14, { color: c.proton, size: 12, weight: 600, align: "left", bg: true });
    g.label(`shape elastic ${a.sE.toFixed(2)} b`, x - 8, Y(a.sE) + (a.sE > a.sR ? -14 : 14), { color: c.alpha, size: 12, weight: 600, align: "right", bg: true });
    g.label("n + ⁵⁶Fe, KD03, computed here", x0, yT - 16, { color: c.soft, size: 11, align: "left" });
  }

  // ---------- scene 6: T0 at low energy, S0 ----------
  function drawS0(g, S) {
    const { W, H, c } = g, phone = W < 600;
    if (!S.t0c) { const pts = []; for (let i = 0; i <= 50; i++) { const lg = -6 + 5.5 * i / 50, E = Math.pow(10, lg); pts.push({ lg, T: solve(0, 0.5, E).T, T1: solve(1, 1.5, E).T }); } S.t0c = pts; }
    const P = S.t0c, x0 = W * (phone ? 0.14 : 0.12), x1 = W * 0.95, yT = H * 0.12, yB = H * (phone ? 0.74 : 0.78);
    const X = (lg) => lerp(x0, x1, (lg + 6) / 5.5), Y = (lt) => lerp(yB, yT, (lt + 9) / 9);
    [-8, -6, -4, -2, 0].forEach((d) => { g.line(x0, Y(d), x1, Y(d), c.line, 1, 0.9); g.label(d === 0 ? "1" : `10${String(d).replace(/[-0-9]/g, (ch) => "⁻⁰¹²³⁴⁵⁶⁷⁸⁹"["-0123456789".indexOf(ch)])}`, x0 - 6, Y(d), { color: c.faint, size: 10, align: "right" }); });
    [-6, -5, -4, -3, -2, -1].forEach((d) => g.label(["1 eV", "10 eV", "100 eV", "1 keV", "10 keV", "100 keV"][d + 6], X(d), yB + 14, { color: c.faint, size: 10 }));
    const p0 = P.map((p) => [X(p.lg), Y(log10(Math.max(p.T, 1e-12)))]), p1 = P.map((p) => [X(p.lg), Y(log10(Math.max(p.T1, 1e-12)))]);
    g.poly(p1, c.alpha, 2, 0.9); g.poly(p0, c.neutron, 2.8);
    // S0 from the lowest point
    const e1 = Math.pow(10, -3), t1 = solve(0, 0.5, e1).T, S0 = t1 / (TAU * Math.sqrt(e1 * 1e6));
    const sl = [[X(-6), Y(log10(TAU * S0 * Math.sqrt(1)))], [X(-1), Y(log10(TAU * S0 * Math.sqrt(1e5)))]];
    g.poly(sl, c.warm, 1.4, 0.8, [5, 4]);
    g.label("T₀ (s-wave)", X(-1.2), Y(log10(P[P.length - 6].T)) - 14, { color: c.neutron, size: 12, weight: 600, align: "right", bg: true });
    g.label("T₁ (p-wave, j = 3/2): slope 3/2", X(-1.6), Y(log10(Math.max(P[P.length - 8].T1, 1e-12))) + 16, { color: c.alpha, size: 12, weight: 600, align: "right", bg: true });
    g.label("dashed: 2πS₀√E, slope ½", X(-5.8), Y(log10(TAU * S0 * Math.sqrt(10))) - 16, { color: c.warm, size: 11, align: "left", bg: true });
    // a dot climbing the s-wave line
    const u = (((S.time * 0.1) % 1) + 1) % 1, fi = u * (P.length - 1), i0 = Math.floor(fi), q = P[i0], q1 = P[Math.min(i0 + 1, P.length - 1)], ff = fi - i0;
    const xx = X(lerp(q.lg, q1.lg, ff)), yy = Y(lerp(log10(q.T), log10(q1.T), ff)); g.glow(xx, yy, 16, c.neutron, 0.5); g.dot(xx, yy, 4, c.neutron);
    g.label(`S₀ = ${(S0 * 1e4).toFixed(2)} × 10⁻⁴ from this potential`, W / 2, H * (phone ? 0.88 : 0.9), { color: c.ink, size: phone ? 13 : 15, weight: 600, serif: true, bg: true });
  }
})();
