/* Chapter 27 (Expert): from resonances to averages (physics/resonance/, compound/wfc.py).
 * Scenes (S.mode): "rmat"   = one sampled s-wave ladder: total and capture cross sections, Reich-Moore against single-level
 *                              Breit-Wigner (interference between levels only in Reich-Moore); a probe sweeps the energy;
 *                   "stats"  = spacing and reduced-width histograms that fill as ladders are drawn (Wigner, Porter-Thomas);
 *                   "doppler"= one resonance magnified: capture with the psi function at temperature T, the cold shape dashed,
 *                              area kept; thermal motion of target nuclei sketched;
 *                   "avg"    = a window glides over the ladder; its average capture against Hauser-Feshbach without and with
 *                              the width-fluctuation correction (exact for one Porter-Thomas neutron channel);
 *                   "regions"= resolution broadening growing with energy: resolved, unresolved, smooth.
 * Physics: Reich-Moore with one neutron channel and the capture channel eliminated, R = sum gamma^2 / (E_l - E - i Gg/2),
 * U = e^(-2i phi) (1 + iPR)/(1 - iPR), sigma_tot = 2 pi/k^2 g (1 - Re U), sigma_abs = pi/k^2 g (1 - |U|^2); SLBW in the ENDF form;
 * Doppler: psi/chi via the Faddeeva function (Humlicek's W4), Delta = sqrt(4 E kT / A); GOE spacings as in resonance.js
 * (Dumitriu-Edelman tridiagonal ensemble), Porter-Thomas neutron widths, Gg fixed. k in 1e12 cm^-1 as in ENDF so pi/k^2 is in barns.
 * Illustrative uranium-238-like parameters: D0 = 20.9 eV, <Gg> = 23 meV, S0 = 1.1e-4, a = 8.3 fm, R' = 9.4 fm, I = 0 (J = 1/2+). */
(function () {
  const { TAU, clamp, lerp, smooth, rng } = WT.util;
  const log10 = (x) => Math.log(x) / Math.LN10;
  const AW = 238, KC = 2.196807e-3 * AW / (AW + 1), D0 = 20.9, GG = 0.023, S0 = 1.1e-4, RCH = 0.83, RSC = 0.94, KB = 8.617e-5;
  const kOf = (E) => KC * Math.sqrt(E);
  // ---- GOE levels (as in resonance.js: Sturm bisection of the Dumitriu-Edelman tridiagonal matrix, unfolded) ----
  function tridiagEig(d, e) {
    const n = d.length, e2 = Array.from(e, (v) => v * v); let lo = Infinity, hi = -Infinity;
    for (let i = 0; i < n; i++) { const rad = (i > 0 ? Math.abs(e[i - 1]) : 0) + (i < n - 1 ? Math.abs(e[i]) : 0); lo = Math.min(lo, d[i] - rad); hi = Math.max(hi, d[i] + rad); }
    const count = (x) => { let c = 0, q = 1; for (let i = 0; i < n; i++) { q = d[i] - x - (i > 0 ? e2[i - 1] / (q === 0 ? 1e-300 : q) : 0); if (q < 0) c++; } return c; };
    const out = []; let a0 = lo;
    for (let k = 0; k < n; k++) { let a = a0, b = hi; for (let it = 0; it < 60; it++) { const mid = 0.5 * (a + b); if (count(mid) > k) b = mid; else a = mid; if (b - a < 1e-9 * (Math.abs(hi) + 1)) break; } out.push(0.5 * (a + b)); a0 = a; }
    return out;
  }
  function goeUnit(n, r) {
    const m = Math.max(40, Math.ceil(n / 0.6) + 6), nrm = () => Math.sqrt(-2 * Math.log(1 - r())) * Math.cos(TAU * r());
    const chi = (k) => { if (k < 30) { let s = 0; for (let i = 0; i < k; i++) { const z = nrm(); s += z * z; } return s; } const z = nrm(); return k * Math.pow(1 - 2 / (9 * k) + z * Math.sqrt(2 / (9 * k)), 3); };
    const d = [], e = []; for (let i = 0; i < m; i++) d.push(nrm()); for (let i = 0; i < m - 1; i++) e.push(Math.sqrt(chi(m - 1 - i) / 2));
    const R = Math.sqrt(2 * m), out = [];
    for (const v of tridiagEig(d, e)) { const x = clamp(v / R, -1, 1), cdf = m * (0.5 + (x * Math.sqrt(1 - x * x) + Math.asin(x)) / Math.PI); if (cdf > 0.2 * m && cdf < 0.8 * m) out.push(cdf); }
    const u0 = out[0]; return out.map((v) => v - u0).slice(0, n);
  }
  /** a ladder of s-wave levels up to Emax: {e, gn0 (reduced width at 1 eV, eV), gg} */
  function makeLadder(seed, n = 300) {
    const r = rng(seed), lv = goeUnit(n, r), off = 0.2 + 0.6 * r(), nrm = () => Math.sqrt(-2 * Math.log(1 - r())) * Math.cos(TAU * r());
    return lv.map((u) => { const z = nrm(); return { e: (u + off) * D0, gn0: S0 * D0 * z * z, gg: GG, z }; }).filter((q) => q.e > 0.5);
  }
  const gnAt = (q, E) => q.gn0 * Math.sqrt(E);            // s-wave: Gamma_n = Gamma_n^0 sqrt(E), penetrability ~ rho
  /** Reich-Moore (one neutron channel, capture eliminated) at E: total, elastic, capture in barns */
  function rm(lad, E) {
    const k = kOf(E), pk = Math.PI / (k * k), phi = k * RSC;
    let Rr = 0, Ri = 0; for (const q of lad) { const gh = 0.5 * gnAt(q, E), d = q.e - E, h = q.gg / 2, den = d * d + h * h; Rr += gh * d / den; Ri += gh * h / den; }
    // PR is already sum (Gn/2)/(E_l - E - i Gg/2); U = e^{-2i phi} (1 + i PR)/(1 - i PR)
    const nr = 1 - Ri, ni = Rr, dr = 1 + Ri, di = -Rr, dd = dr * dr + di * di, qr = (nr * dr + ni * di) / dd, qi = (ni * dr - nr * di) / dd;
    const c2 = Math.cos(2 * phi), s2 = Math.sin(2 * phi), Ur = qr * c2 + qi * s2, Ui = qi * c2 - qr * s2;
    const tot = 2 * pk * (1 - Ur), el = pk * ((1 - Ur) ** 2 + Ui * Ui); return { tot, el, cap: Math.max(0, tot - el) };
  }
  // Faddeeva w(z), z = x + i y (y >= 0), Humlicek W4
  function wofz(x, y) {
    const tr = y, ti = -x, s = Math.abs(x) + y, mul = (a, b, c, d) => [a * c - b * d, a * d + b * c], div = (a, b, c, d) => { const q = c * c + d * d; return [(a * c + b * d) / q, (b * c - a * d) / q]; };
    if (s >= 15) { const [ur, ui] = mul(tr, ti, tr, ti); return div(tr * 0.5641896, ti * 0.5641896, 0.5 + ur, ui); }
    if (s >= 5.5) { const [ur, ui] = mul(tr, ti, tr, ti); const [nr, ni] = mul(tr, ti, 1.410474 + ur * 0.5641896, ui * 0.5641896); const [dr, di] = [0.75 + ur * 3 + (ur * ur - ui * ui), ui * 3 + 2 * ur * ui]; return div(nr, ni, dr, di); }
    const poly = (cs) => { let pr = cs[cs.length - 1], pi = 0; for (let i = cs.length - 2; i >= 0; i--) { const m = mul(pr, pi, tr, ti); pr = m[0] + cs[i]; pi = m[1]; } return [pr, pi]; };
    if (y >= 0.195 * Math.abs(x) - 0.176) { const [nr, ni] = poly([16.4955, 20.20933, 11.96482, 3.778987, 0.5642236]), [dr, di] = poly([16.4955, 38.82363, 39.27121, 21.69274, 6.699398, 1]); return div(nr, ni, dr, di); }
    const [ur, ui] = mul(tr, ti, tr, ti), polyU = (cs) => { let pr = cs[cs.length - 1], pi = 0; for (let i = cs.length - 2; i >= 0; i--) { const m = mul(pr, pi, ur, ui); pr = m[0] + cs[i]; pi = m[1]; } return [pr, pi]; };
    const [nr0, ni0] = polyU([36183.31, -3321.9905, 1540.787, -219.0313, 35.76683, -1.320522, 0.56419]), [nr, ni] = mul(tr, ti, nr0, ni0), [dr, di] = polyU([32066.6, -24322.84, 9022.228, -2186.181, 364.2191, -61.57037, 1.841439, -1]);
    const [qr, qi] = div(nr, ni, dr, di), ex = Math.exp(ur); return [ex * Math.cos(ui) - qr, ex * Math.sin(ui) - qi];
  }
  /** psi and chi at x = 2(E - E0)/Gamma, xi = Gamma/Delta (xi = Infinity: cold) */
  function psichi(x, xi) { if (!isFinite(xi) || xi > 200) return [1 / (1 + x * x), x / (1 + x * x)]; const [wr, wi] = wofz(xi * x / 2, xi / 2), f = Math.sqrt(Math.PI) * xi / 2; return [f * wr, f * wi]; }
  /** SLBW at E with Doppler (or resolution) width Delta (eV, 0 = cold): total, capture */
  function slbw(lad, E, Delta) {
    const k = kOf(E), pk = Math.PI / (k * k), phi = k * RSC, s2p = Math.sin(phi) ** 2, sp2 = Math.sin(2 * phi); let tot = 4 * pk * s2p, cap = 0;
    for (const q of lad) {
      const gn = gnAt(q, Math.max(q.e, 1e-3)), G = gn + q.gg, x = 2 * (E - q.e) / G; if (Math.abs(x) > 4e4) continue;
      const [ps, ch] = psichi(x, Delta > 0 ? G / Delta : Infinity), s0 = 4 * pk * gn / G;
      cap += s0 * (q.gg / G) * ps; tot += s0 * ((gn / G - 2 * s2p) * ps + sp2 * ch) + s0 * (q.gg / G) * ps;
    }
    return { tot, cap };
  }
  const areaCap = (q) => { const k = kOf(q.e), gn = gnAt(q, q.e); return 2 * Math.PI * Math.PI / (k * k) * gn * q.gg / (gn + q.gg); };   // b eV
  /** Hauser-Feshbach average capture at E: without and with the width-fluctuation correction (PT neutron, fixed Gg) */
  function hfCap(E) {
    const k = kOf(E), gn = S0 * D0 * Math.sqrt(E), pre = 2 * Math.PI * Math.PI / (k * k * D0);
    let ex = 0; const n = 400; for (let i = 0; i < n; i++) { const u = (i + 0.5) / n, y = inverseChi1(u); ex += gn * y * GG / (gn * y + GG); } ex /= n;
    return { noW: pre * gn * GG / (gn + GG), W: pre * ex };
  }
  // quantile of chi-squared with one degree of freedom (mean 1): y = 2 erfinv(u)^2
  function inverseChi1(u) { const x = erfinv(u); return 2 * x * x; }
  function erfinv(y) { const a = 0.147, ln = Math.log(1 - y * y), t = 2 / (Math.PI * a) + ln / 2; let x = Math.sign(y) * Math.sqrt(Math.sqrt(t * t - ln / a) - t); for (let i = 0; i < 2; i++) { const e = erf(x) - y; x -= e / (2 / Math.sqrt(Math.PI) * Math.exp(-x * x)); } return x; }
  function erf(x) { const t = 1 / (1 + 0.3275911 * Math.abs(x)), y = 1 - ((((1.061405429 * t - 1.453152027) * t + 1.421413741) * t - 0.284496736) * t + 0.254829592) * t * Math.exp(-x * x); return x >= 0 ? y : -y; }
  /** sampled grid around each level (log spaced) for drawing the ladder */
  function grid(lad, lo, hi, n, widthOf) {
    const xs = []; for (let i = 0; i <= n; i++) xs.push(lo * Math.pow(hi / lo, i / n));
    for (const q of lad) { if (q.e <= lo || q.e >= hi) continue; const G = widthOf(q); for (const f of [-6, -3, -1.5, -0.8, -0.4, 0, 0.4, 0.8, 1.5, 3, 6]) { const e = q.e + f * G; if (e > lo && e < hi) xs.push(e); } }
    return xs.sort((a, b) => a - b);
  }
  const SHOT = /[?&]shot=/.test(location.search);
  const sup = (n) => String(n).replace(/[-0-9]/g, (ch) => "⁻⁰¹²³⁴⁵⁶⁷⁸⁹"["-0123456789".indexOf(ch)]);
  const fmtB = (v) => (v >= 1000 ? `${(v / 1000).toFixed(v >= 1e4 ? 0 : 1)}k b` : v >= 10 ? `${v.toFixed(0)} b` : `${v.toFixed(2)} b`);

  Object.assign(WT.glossary || (WT.glossary = {}), {
    rMatrix: {
      term: "R-matrix theory", aliases: ["R-matrix"],
      short: "The exact description of resonance reactions by level energies and reduced widths inside a channel radius, matched to free waves outside it.",
      more: "Evaluations fit its parameters to measured resonances. The single- and multi-level Breit–Wigner and the Reich–Moore forms are approximations to the full theory.",
      chapter: "averages",
    },
    reichMoore: {
      term: "Reich–Moore", aliases: ["Reich–Moore"],
      short: "The R-matrix approximation used in most evaluations of heavy nuclei: the neutron channels are treated exactly, the many photon channels as one absorptive width per level.",
      chapter: "averages",
    },
    doppler: {
      term: "Doppler broadening", aliases: ["Doppler broadening"],
      short: "The smearing of resonances by the thermal motion of the target nuclei: the peak drops and the wings widen, while the area of an isolated peak stays the same.",
      formula: "Δ = √(4 E kT / A)",
      chapter: "averages",
    },
    resolvedRegion: {
      term: "Resolved and unresolved resonance regions", aliases: ["resolved resonance region", "unresolved region"],
      short: "Below some energy each resonance is measured on its own (resolved); above it, only their average parameters are known (unresolved), until the averages become smooth.",
      more: "In the unresolved region self-shielding is handled with probability tables, distributions of the cross section built from sampled resonance ladders.",
      chapter: "averages",
    },
  });

  WT.chapter("averages", {
    num: "Chapter 27", title: "From resonances to averages", short: "Resonances to averages",
    lead: "Chapter 15 drew resonance ladders. Here they are as cross sections: the R-matrix formula, the statistics behind the parameters, the effect of temperature, and how an average over many resonances turns into Hauser–Feshbach.",
    html: `
<div class="step">
  <h3>R-matrix, level by level</h3>
  <p>Below a few keV in a heavy nucleus each compound level shows up on its own, and the cross section is written exactly in terms of level parameters: energies <i>E</i><sub>λ</sub>, reduced neutron widths and capture widths. Evaluations use <b>R-matrix</b> theory, most often in the <b>Reich–Moore</b> form, which keeps the interference between levels in the neutron channel and treats the many capture channels as one absorptive width.</p>
  <div class="formula">R(E) = Σ<sub>λ</sub> γ<sub>λ</sub>² / (E<sub>λ</sub> − E − iΓ<sub>λγ</sub>/2) ,  U = e<sup>−2iφ</sup> (1 + iPR) / (1 − iPR)</div>
  <div class="formula">σ<sub>tot</sub> = (2π/k²) g (1 − Re U) ,  σ<sub>γ</sub> = (π/k²) g (1 − |U|²)</div>
  <div class="btns"><button class="btn ghost" data-act="rm" aria-pressed="true">Reich–Moore</button><button class="btn ghost" data-act="bw" aria-pressed="false">Single-level Breit–Wigner</button></div>
  <p>The upper line is the total cross section, the lower one capture, for one ladder of s-wave levels on a spin-0 target, uranium-238-like. Between levels the total falls below the potential scattering where resonance and potential amplitudes cancel. The single-level form adds the levels' cross sections instead of their amplitudes; it is close at the peaks and wrong in the valleys, where the tails of many levels add up and the total can even turn negative.</p>
</div>
<div class="step">
  <h3>The statistics behind the parameters</h3>
  <p>An unmeasured nucleus has no ladder, only its averages: <i>D</i>₀, the strength function <i>S</i>₀ = ⟨Γ<sub>n</sub>⁰⟩/<i>D</i>₀ and ⟨Γ<sub>γ</sub>⟩. Random-matrix theory gives the rest: spacings of levels of one spin and parity follow the Wigner distribution, reduced neutron widths follow Porter–Thomas, a χ² with one degree of freedom.</p>
  <div class="formula">P(s) = (πs/2) e<sup>−πs²/4</sup> ,  P(y) = e<sup>−y/2</sup> / √(2πy) ,  s = spacing/D₀, y = Γ<sub>n</sub>⁰/⟨Γ<sub>n</sub>⁰⟩</div>
  <div class="btns"><button class="btn" data-act="more">Draw ten more ladders</button></div>
  <p>The histograms collect the spacings and widths of every ladder drawn so far; the curves are the two laws. The capture width, a sum over hundreds of photon channels, hardly fluctuates, so it is taken as fixed.</p>
</div>
<div class="step">
  <h3>Heat smears the peaks</h3>
  <p>The target nuclei move. A neutron of energy <i>E</i> meets them with a spread of relative energies of width Δ = √(4<i>E</i> <i>kT</i>/<i>A</i>), and each resonance is seen through that spread: <b>Doppler broadening</b>. For a single level the result is the ψ function, a Lorentzian convolved with a Gaussian.</p>
  <div class="formula">σ<sub>γ</sub>(E,T) = σ₀ (Γ<sub>γ</sub>/Γ) ψ(x, ξ) ,  x = 2(E − E<sub>λ</sub>)/Γ ,  ξ = Γ/Δ</div>
  <div class="ctl"><label for="av-t">Temperature (K)</label><input id="av-t" type="range" data-bind="TK" min="0" max="3000" step="10" value="300"><output data-show="TK" data-fmt="0"></output></div>
  <p>The magnified resonance is the strongest of the lowest few in the ladder; the dashed line is its shape at 0 K. Heat lowers the peak and widens the wings, and the area under the capture peak stays the same. In a thick sample that is not neutral: the peak is self-shielded and the wings are not, so a hotter fuel captures more. This is the Doppler feedback of a reactor.</p>
</div>
<div class="step">
  <h3>The average is Hauser–Feshbach</h3>
  <p>Averaged over many resonances, capture becomes a smooth function of energy. The window glides over the ladder and its average is plotted as it goes; the smooth lines are the Hauser–Feshbach value with the transmissions <i>T<sub>n</sub></i> = 2π⟨Γ<sub>n</sub>⟩/<i>D</i> and <i>T<sub>γ</sub></i> = 2π⟨Γ<sub>γ</sub>⟩/<i>D</i>.</p>
  <div class="ctl"><label for="av-w">Window width (levels)</label><input id="av-w" type="range" data-bind="win" min="2" max="40" step="1" value="12" data-instant><output data-show="win" data-fmt="0"></output></div>
  <div class="btns"><button class="btn ghost" data-act="ladder">Another ladder</button></div>
  <p>A narrow window scatters widely: a few resonances, Porter–Thomas widths. A wide one settles on the lower line, the one with the width-fluctuation correction. The upper line, the product of averages, is 25 to 47 per cent too high here, most where ⟨Γ<sub>n</sub>⟩ is one to three times ⟨Γ<sub>γ</sub>⟩, from about 100 eV to 1 keV. (With p-waves and more open channels the correction is smaller.) For one neutron channel with Porter–Thomas widths and a fixed capture width, the corrected value is exact: (2π²/k²<i>D</i>) <i>g</i> ⟨Γ<sub>n</sub>Γ<sub>γ</sub>/Γ⟩.</p>
</div>
<div class="step">
  <h3>Resolved, unresolved, smooth</h3>
  <p>What a measurement resolves depends on its energy resolution, which worsens as the energy rises. The line is the cross section as an instrument sees it, broadened by a resolution that grows as <i>E</i><sup>3/2</sup>, as in time-of-flight. At low energy each level stands alone and its parameters can be fitted: the resolved resonance region. Higher up the levels merge into a fluctuating band whose statistics are known but whose individual peaks are not: the unresolved region, described by average parameters and, for self-shielding, by probability tables built from sampled ladders. Above it, Hauser–Feshbach and the optical model take over.</p>
  <div class="ctl"><label for="av-r">Instrument resolution (relative)</label><input id="av-r" type="range" data-bind="res" min="0.2" max="3" step="0.05" value="1"><output data-show="res" data-fmt="2"></output></div>
  <p>INCOGNITA's library has no resolved resonance region yet. Its curves are Hauser–Feshbach averages down to the lowest energies; where measured resonances are resolved, the <a href="data.html" data-keep-lang>Every nuclide</a> page marks the curve as an average. Resonance parameters, and the Doppler-broadened pointwise cross sections built from them, are work in progress.</p>
  <div class="aside">In the code: <code>physics/resonance/ladder.py</code> (random-matrix spacings, Porter–Thomas widths, single-level cross sections, ensembles), <code>ladder_statistics.py</code> (the laws tested on measured ladders), <code>compound/wfc.py</code> (the width-fluctuation correction the averages converge to). The Reich–Moore, ψ–χ and resolution formulas in the picture are evaluated here, with illustrative uranium-238-like parameters; the Hauser–Feshbach engine, and so the library, does not yet compute resonance-region cross sections.</div>
</div>`,
    setup(S) {
      S.set("mode", "rmat"); S.to("TK", 300, true); S.to("win", 12, true); S.to("res", 1, true); S.set("form", 1);
      S.seed = 21; S.lad = makeLadder(S.seed); S.hs = new Float64Array(30); S.hw = new Float64Array(30); S.nL = 0; S.glide = 0; S.trace = []; S.probe = 0;
      S.addStats = (lad) => { for (let i = 1; i < lad.length; i++) { const s = (lad[i].e - lad[i - 1].e) / D0, b = Math.floor(s / 0.12); if (b < 30) S.hs[b]++; } for (const q of lad) { const y = q.z * q.z, b = Math.floor(y / 0.15); if (b < 30) S.hw[b]++; } S.nL++; };
      S.addStats(S.lad);
      const press = (on) => document.querySelectorAll('#averages [data-act="rm"], #averages [data-act="bw"]').forEach((b) => b.setAttribute("aria-pressed", String(b.dataset.act === on)));
      S.on("rm", () => { S.set("form", 1); press("rm"); S.cache = null; });
      S.on("bw", () => { S.set("form", 0); press("bw"); S.cache = null; });
      S.on("more", () => { S.queue = (S.queue || 0) + 10; });
      S.on("ladder", () => { S.seed++; S.lad = makeLadder(S.seed); S.cache = null; S.trace = []; S.glide = 0; S.addStats(S.lad); });
    },
    steps: [
      (S) => { S.set("mode", "rmat"); },
      (S) => { S.set("mode", "stats"); if (SHOT) S.queue = 20; },
      (S) => { S.set("mode", "doppler"); },
      (S) => { S.set("mode", "avg"); S.trace = []; S.glide = SHOT ? 0.9 : 0; },
      (S) => { S.set("mode", "regions"); },
    ],
    frame(g, S, dt) {
      if (S.mode === "rmat") drawRmat(g, S, dt);
      else if (S.mode === "stats") drawStats(g, S, dt);
      else if (S.mode === "doppler") drawDoppler(g, S, dt);
      else if (S.mode === "avg") drawAvg(g, S, dt);
      else drawRegions(g, S, dt);
    },
  });
  WT.mods.averages.calc = { makeLadder, rm, slbw, psichi, hfCap, areaCap, wofz };

  // log-log frame for cross sections
  function frame(g, phone, yT, yB, e0, e1, d0, d1) {
    const { W, c } = g, x0 = W * (phone ? 0.14 : 0.1), x1 = W * 0.95, X = (e) => lerp(x0, x1, (log10(e) - log10(e0)) / (log10(e1) - log10(e0))), Y = (s) => lerp(yB, yT, (log10(Math.max(s, 10 ** (d0 - 1))) - d0) / (d1 - d0));
    for (let d = d0; d <= d1; d++) { const y = lerp(yB, yT, (d - d0) / (d1 - d0)); g.line(x0, y, x1, y, c.line, 1, 0.8); g.label(d === 0 ? "1 b" : `10${sup(d)} b`, x0 - 6, y, { color: c.faint, size: 10, align: "right" }); }
    for (let d = Math.ceil(log10(e0)); d <= log10(e1); d++) g.label(d === 0 ? "1 eV" : d === 1 ? "10 eV" : d === 2 ? "100 eV" : d === 3 ? "1 keV" : d === 4 ? "10 keV" : "100 keV", X(10 ** d), yB + 12, { color: c.faint, size: 10 });
    return { X, Y, x0, x1, yT, yB };
  }

  // ---------- scene 1: Reich-Moore vs SLBW ----------
  function drawRmat(g, S, dt) {
    const { W, H, c } = g, phone = W < 600, e0 = 1, e1 = 300;
    const F = frame(g, phone, H * 0.1, H * (phone ? 0.82 : 0.84), e0, e1, -1, 4);
    if (!S.cache || S.cache.k !== `r${S.form}|${S.seed}`) {
      const xs = grid(S.lad, e0, e1, 700, (q) => gnAt(q, q.e) + q.gg), tot = [], cap = [], tot2 = [];
      for (const e of xs) { const a = S.form ? rm(S.lad, e) : slbw(S.lad, e, 0), b = S.form ? slbw(S.lad, e, 0) : rm(S.lad, e); tot.push([F.X(e), F.Y(a.tot)]); cap.push([F.X(e), F.Y(a.cap)]); tot2.push([F.X(e), F.Y(Math.max(b.tot, 0.01))]); }
      S.cache = { k: `r${S.form}|${S.seed}`, tot, cap, tot2, X: F.X, Y: F.Y };
    }
    const C = S.cache;
    g.clip(F.x0 - 2, F.yT - 30, F.x1 - F.x0 + 4, F.yB - F.yT + 32);
    g.poly(C.tot2, c.faint, 1, 0.6, [3, 3]);
    g.ground(C.cap, c.photon, H * 0.1, 0.18); g.poly(C.cap, c.photon, 1.6); g.poly(C.tot, c.neutron, 1.8);
    g.restore();
    const pot = 4 * Math.PI * RSC * RSC;   // 4 pi R^2 in barns (R in 1e-12 cm)
    g.line(F.x0, F.Y(pot), F.x1, F.Y(pot), c.soft, 1, 0.6, [6, 4]); g.label(`potential scattering 4πR′² ≈ ${pot.toFixed(1)} b`, F.x1, F.Y(pot) + 12, { color: c.soft, size: 11, align: "right", bg: true });
    g.label(S.form ? "Reich–Moore (dashed: single-level)" : "single-level Breit–Wigner (dashed: Reich–Moore)", F.x0, F.yT - 14, { color: c.ink, size: 12, weight: 600, align: "left" });
    g.label("total", F.X(1.3), F.Y(rm(S.lad, 1.3).tot) - 12, { color: c.neutron, size: 11, align: "left", bg: true });
    g.label("capture", F.X(1.3), F.Y(rm(S.lad, 1.3).cap) - 12, { color: c.photon, size: 11, align: "left", bg: true });
    // a probe neutron sweeping the energy, with the two values at its position
    S.probe = (((S.probe + dt / 12) % 1) + 1) % 1; const e = Math.pow(10, lerp(0.05, log10(e1) - 0.05, S.probe)), a = S.form ? rm(S.lad, e) : slbw(S.lad, e, 0);
    g.line(F.X(e), F.yT, F.X(e), F.yB, c.warm, 1, 0.45);
    g.glow(F.X(e), F.Y(a.tot), 12, c.neutron, 0.5); g.dot(F.X(e), F.Y(a.tot), 4, c.neutron); g.dot(F.X(e), F.Y(a.cap), 4, c.photon);
    g.label(`${e.toFixed(1)} eV · total ${fmtB(a.tot)} · capture ${fmtB(a.cap)}`, W / 2, H * (phone ? 0.94 : 0.95), { color: c.ink, size: phone ? 11 : 13, weight: 600, bg: true });
  }

  // ---------- scene 2: statistics ----------
  function drawStats(g, S, dt) {
    const { W, H, c } = g, phone = W < 600;
    if (S.queue > 0 && (S.sacc = (S.sacc || 0) + dt) > 0.12) { S.sacc = 0; S.queue--; S.addStats(makeLadder(1000 + S.nL * 7)); }
    const panel = (x0, x1, yT, yB, hist, bw, pdf, title, col, xlab) => {
      let tot = 0; for (const v of hist) tot += v; const nb = hist.length, w = (x1 - x0) / nb; let mx = 0; for (let i = 0; i < nb; i++) mx = Math.max(mx, hist[i] / Math.max(tot, 1) / bw, pdf((i + 0.5) * bw)); mx = Math.min(mx * 1.1, 3);
      for (let i = 0; i < nb; i++) { const h = (yB - yT) * Math.min(1, hist[i] / Math.max(tot, 1) / bw / mx); g.ctx.fillStyle = g.rgba(col, 0.55); g.ctx.fillRect(x0 + i * w + 0.5, yB - h, w - 1, h); }
      const p = []; for (let i = 1; i <= 120; i++) { const s = nb * bw * i / 120; p.push([lerp(x0, x1, i / 120), yB - (yB - yT) * Math.min(1.05, pdf(s) / mx)]); } g.poly(p, c.ink, 2.2);
      g.line(x0, yB, x1, yB, c.soft, 1.2, 0.8); g.label(title, x0, yT - 12, { color: c.ink, size: 12, weight: 600, align: "left" });
      [0, 1, 2, 3].forEach((v) => { const xx = lerp(x0, x1, v / (nb * bw)); if (xx <= x1) g.label(`${v}`, xx, yB + 12, { color: c.faint, size: 10 }); });
      g.label(xlab, x1, yB + 26, { color: c.faint, size: 10, align: "right" });
    };
    const wig = (s) => Math.PI * s / 2 * Math.exp(-Math.PI * s * s / 4), pt = (y) => Math.exp(-y / 2) / Math.sqrt(TAU * Math.max(y, 1e-3));
    if (phone) { panel(W * 0.08, W * 0.94, H * 0.1, H * 0.39, S.hs, 0.12, wig, "spacings: Wigner", c.neutron, "s = spacing / D₀"); panel(W * 0.08, W * 0.94, H * 0.58, H * 0.86, S.hw, 0.15, pt, "reduced neutron widths: Porter–Thomas", c.photon, "y = Γn⁰ / ⟨Γn⁰⟩"); }
    else { panel(W * 0.08, W * 0.47, H * 0.18, H * 0.7, S.hs, 0.12, wig, "spacings: Wigner", c.neutron, "s = spacing / D₀"); panel(W * 0.55, W * 0.95, H * 0.18, H * 0.7, S.hw, 0.15, pt, "reduced neutron widths: Porter–Thomas", c.photon, "y = Γn⁰ / ⟨Γn⁰⟩"); }
    let n = 0; for (const v of S.hs) n += v;
    g.label(`${S.nL} ladders · ${n} spacings`, W / 2, H * (phone ? 0.95 : 0.86), { color: c.ink, size: phone ? 12 : 14, weight: 600, serif: true, bg: true });
    // the newest ladder as a strip of ticks
    const ly = H * (phone ? 0.5 : 0.08), lx0 = W * 0.08, lx1 = W * 0.94;
    for (const q of S.lad) { const x = lerp(lx0, lx1, q.e / (D0 * 40)); if (x > lx1) break; g.line(x, ly, x, ly - 6 - 14 * Math.min(1, q.z * q.z / 3), c.neutron, 1.6, 0.8); }
    // a cursor steps along the strip, one spacing at a time
    { const n = S.lad.filter((q) => q.e < D0 * 40).length; if (n > 2) { const k = 1 + Math.floor((((S.time * 1.5) % (n - 1)) + (n - 1)) % (n - 1)), a = S.lad[k - 1], b = S.lad[k], xa = lerp(lx0, lx1, a.e / (D0 * 40)), xb = lerp(lx0, lx1, b.e / (D0 * 40));
      g.ctx.save(); g.ctx.fillStyle = g.rgba(c.warm, 0.25); g.ctx.fillRect(xa, ly - 22, xb - xa, 24); g.ctx.restore(); g.label(`s = ${((b.e - a.e) / D0).toFixed(2)}`, (xa + xb) / 2, ly + 12, { color: c.warm, size: 11, weight: 600, bg: true }); } }
  }

  // ---------- scene 3: Doppler broadening of one resonance ----------
  function drawDoppler(g, S, dt) {
    const { W, H, c } = g, phone = W < 600, q = S.lad.slice(0, 6).reduce((b, x) => (areaCap(x) > areaCap(b) ? x : b), S.lad[0]), T = S.TK, Delta = Math.sqrt(4 * q.e * KB * T / AW), Gt = gnAt(q, q.e) + q.gg;
    const span = Math.max(8 * Gt, 6 * Delta, 0.3), e0 = q.e - span, e1 = q.e + span, x0 = W * (phone ? 0.14 : 0.1), x1 = W * 0.95, yT = H * 0.14, yB = H * (phone ? 0.72 : 0.74);
    const one = [q], cold = slbw(one, q.e, 0).cap, X = (e) => lerp(x0, x1, (e - e0) / (e1 - e0)), Y = (s) => lerp(yB, yT, s / (cold * 1.08));
    const pc = [], ph = []; let area0 = 0, area1 = 0; const n = 400, de = (e1 - e0) / n;
    for (let i = 0; i <= n; i++) { const e = e0 + i * de, a = slbw(one, e, 0).cap, b = T > 0 ? slbw(one, e, Delta).cap : a; pc.push([X(e), Y(a)]); ph.push([X(e), Y(b)]); area0 += a * de; area1 += b * de; }
    g.ground(ph, c.photon, H * 0.1, 0.25); g.poly(pc, c.soft, 1.4, 0.9, [5, 4]); g.poly(ph, c.photon, 2.8);
    g.line(x0, yB, x1, yB, c.soft, 1.2, 0.8);
    [-1, 0, 1].forEach((k) => { const e = q.e + k * span * 0.6; g.label(`${e.toFixed(2)} eV`, X(e), yB + 12, { color: c.faint, size: 10 }); });
    g.label(`capture near the ${q.e.toFixed(2)} eV resonance`, x0, yT - 14, { color: c.ink, size: 12, weight: 600, align: "left" });
    const peak = T > 0 ? slbw(one, q.e, Delta).cap : cold;
    if (phone) { g.label(`Γ = ${(Gt * 1000).toFixed(1)} meV · Δ = ${(Delta * 1000).toFixed(1)} meV`, W / 2, yB + 26, { color: c.ink, size: 12, weight: 600, bg: true }); g.label(`peak ${fmtB(peak)} (0 K: ${fmtB(cold)})`, W / 2, yB + 44, { color: c.ink, size: 12, weight: 600, bg: true }); }
    else g.label(`Γ = ${(Gt * 1000).toFixed(1)} meV · Δ = ${(Delta * 1000).toFixed(1)} meV · peak ${fmtB(peak)} (0 K: ${fmtB(cold)})`, W / 2, yB + 38, { color: c.ink, size: 13, weight: 600, bg: true });
    { const k = `${q.e}|${T.toFixed(1)}`; if (!S.dpA || S.dpA.k !== k) S.dpA = { k, ...wideAreas(q, Delta) }; area0 = S.dpA.a0; area1 = S.dpA.a1; } // the drawn window cuts the wings: integrate wide
    g.label(`area ${(area1).toFixed(0)} b·eV (0 K: ${(area0).toFixed(0)})`, W / 2, yB + (phone ? 62 : 58), { color: c.soft, size: 12, bg: true });
    // thermal motion: target nuclei jittering with speed ~ sqrt(T)
    const ny = H * (phone ? 0.92 : 0.92), amp = 2 + 10 * Math.sqrt(T / 3000);
    for (let i = 0; i < 9; i++) { const x = lerp(W * 0.2, W * 0.8, i / 8) + Math.sin(S.time * (4 + i) + i * 1.7) * amp, y = ny + Math.cos(S.time * (3.3 + i * 0.7) + i) * amp * 0.4; g.ball(x, y, 6, c.neutron, 0.85); }
    g.label(T > 0 ? `target nuclei at ${T.toFixed(0)} K` : "target nuclei at rest", W / 2, ny - 18 - amp, { color: c.soft, size: 11 });
  }

  /** capture areas of one level, cold and broadened, over +-400 widths (or to 0.9 E): a sinh grid, dense at the peak */
  function wideAreas(q, Delta) {
    const Gt = gnAt(q, q.e) + q.gg, w = Math.max(1e-4, Math.min(Gt, Delta > 0 ? Delta : Gt) / 2), reach = Math.min(400 * Math.max(Gt, Delta), 0.9 * q.e), umax = Math.asinh(reach / w), n = 1200, du = 2 * umax / n;
    let a0 = 0, a1 = 0;
    for (let i = 0; i <= n; i++) { const u = -umax + i * du, e = q.e + w * Math.sinh(u), jac = w * Math.cosh(u) * du * (i === 0 || i === n ? 0.5 : 1); const c0 = slbw([q], e, 0).cap; a0 += c0 * jac; a1 += (Delta > 0 ? slbw([q], e, Delta).cap : c0) * jac; }
    return { a0, a1 };
  }

  // ---------- scene 4: window averages against Hauser-Feshbach ----------
  function drawAvg(g, S, dt) {
    const { W, H, c } = g, phone = W < 600, lad = S.lad, emax = lad[lad.length - 1].e, e0 = 5;
    const x0 = W * (phone ? 0.14 : 0.1), x1 = W * 0.95, yT = H * 0.12, yB = H * (phone ? 0.6 : 0.62), X = (e) => lerp(x0, x1, (log10(e) - log10(e0)) / (log10(emax) - log10(e0)));
    // HF curves
    if (!S.hf) { const a = []; for (let i = 0; i <= 80; i++) { const e = e0 * Math.pow(emax / e0, i / 80), h = hfCap(e); a.push([e, h.noW, h.W]); } S.hf = a; }
    const lo = 0.3, hi = 300, Y = (s) => lerp(yB, yT, (log10(clamp(s, lo, hi)) - log10(lo)) / (log10(hi) - log10(lo)));
    [0.3, 1, 3, 10, 30, 100, 300].forEach((s) => { g.line(x0, Y(s), x1, Y(s), c.line, 1, 0.8); g.label(`${s} b`, x0 - 6, Y(s), { color: c.faint, size: 10, align: "right" }); });
    [10, 100, 1000].forEach((e) => { if (e < emax) g.label(e === 10 ? "10 eV" : e === 100 ? "100 eV" : "1 keV", X(e), yB + 12, { color: c.faint, size: 10 }); });
    g.poly(S.hf.map((p) => [X(p[0]), Y(p[1])]), c.proton, 2, 0.9, [6, 5]); g.poly(S.hf.map((p) => [X(p[0]), Y(p[2])]), c.fission, 2.6);
    g.label("Hauser–Feshbach, no correction", X(300), Y(hfCap(300).noW) - 14, { color: c.proton, size: 11, bg: true });
    g.label("with width fluctuations", X(300), Y(hfCap(300).W) + 16, { color: c.fission, size: 11, bg: true });
    g.label("average capture cross section", x0, yT - 14, { color: c.ink, size: 12, weight: 600, align: "left" });
    // ladder ticks at the bottom
    const ly = H * (phone ? 0.74 : 0.76);
    for (const q of lad) { if (q.e < e0) continue; const h = 4 + 16 * Math.min(1, areaCap(q) / 4000); g.line(X(q.e), ly, X(q.e), ly - h, c.photon, 1.4, 0.8); }
    // the gliding window: N levels; its average = sum of peak areas / energy span
    const N = Math.round(S.win), idx0 = lad.findIndex((q) => q.e >= e0), nmax = lad.length - idx0 - N;
    S.glide = (((S.glide + dt / 14) % 1) + 1) % 1; const i0 = idx0 + Math.floor(S.glide * Math.max(1, nmax)), A0 = lad[i0], A1 = lad[Math.min(lad.length - 1, i0 + N)];
    const span = A1.e - A0.e; let ar = 0; for (let i = i0; i < i0 + N; i++) ar += areaCap(lad[i]); const avg = ar / span, ec = Math.sqrt(A0.e * A1.e);
    g.ctx.save(); g.ctx.fillStyle = g.rgba(c.warm, 0.12); g.ctx.fillRect(X(A0.e), yT, X(A1.e) - X(A0.e), ly - yT); g.ctx.restore();
    if (!S.trace.length || S.trace[S.trace.length - 1][0] > ec || S.trace.N !== N) { S.trace = []; S.trace.N = N; }
    S.trace.push([ec, avg]);
    S.trace.forEach(([e, v]) => g.dot(X(e), Y(v), 2.6, c.warm, 0.85));
    g.glow(X(ec), Y(avg), 14, c.warm, 0.6); g.dot(X(ec), Y(avg), 5, c.warm);
    const h = hfCap(ec);
    if (phone) { g.label(`${N} levels around ${ec.toFixed(0)} eV: ${avg.toFixed(2)} b`, W / 2, H * 0.84, { color: c.warm, size: 12, weight: 600, bg: true }); g.label(`HF ${h.noW.toFixed(2)} b without, ${h.W.toFixed(2)} b with the correction`, W / 2, H * 0.84 + 18, { color: c.ink, size: 11, bg: true }); }
    else g.label(`${N} levels around ${ec.toFixed(0)} eV: ${avg.toFixed(2)} b · HF ${h.noW.toFixed(2)} b without, ${h.W.toFixed(2)} b with the correction`, W / 2, H * 0.86, { color: c.ink, size: 12, weight: 600, bg: true });
  }

  // ---------- scene 5: resolution: resolved, unresolved, smooth ----------
  function drawRegions(g, S, dt) {
    const { W, H, c } = g, phone = W < 600, e0 = 2, e1 = 6000, lad = S.lad;
    const F = frame(g, phone, H * 0.14, H * (phone ? 0.72 : 0.74), e0, e1, -1, 4);
    const key = `${S.res.toFixed(2)}|${S.seed}`;
    if (!S.rg || S.rg.k !== key) {
      const xs = grid(lad, e0, e1, 600, (q) => Math.max(gnAt(q, q.e) + q.gg, resW(q.e, S.res))), pts = [], hf = [];
      for (const e of xs) { const a = slbw(lad, e, resW(e, S.res)); pts.push([F.X(e), F.Y(a.cap)]); }
      for (let i = 0; i <= 60; i++) { const e = e0 * Math.pow(e1 / e0, i / 60); hf.push([F.X(e), F.Y(hfCap(e).W)]); }
      // where the resolution width reaches about a third of the spacing: the end of the resolved region
      let er = e1; for (let e = e0; e < e1; e *= 1.02) if (resW(e, S.res) > D0 / 3) { er = e; break; }
      S.rg = { k: key, pts, hf, er };
    }
    const R = S.rg;
    g.clip(F.x0 - 2, F.yT - 2, F.x1 - F.x0 + 4, F.yB - F.yT + 4);
    const xr = F.X(R.er), xu = F.X(Math.min(e1, R.er * 4));
    g.ctx.save(); g.ctx.fillStyle = g.rgba(c.fission, 0.07); g.ctx.fillRect(F.x0, F.yT, xr - F.x0, F.yB - F.yT); g.ctx.fillStyle = g.rgba(c.photon, 0.07); g.ctx.fillRect(xr, F.yT, xu - xr, F.yB - F.yT); g.ctx.fillStyle = g.rgba(c.accent, 0.06); g.ctx.fillRect(xu, F.yT, F.x1 - xu, F.yB - F.yT); g.ctx.restore();
    g.poly(R.pts, c.photon, 1.6); g.poly(R.hf, c.fission, 2, 0.8, [6, 5]);
    g.restore();
    g.label("resolved", (F.x0 + xr) / 2, F.yT + 12, { color: c.fission, size: 12, weight: 600, bg: true });
    if (xu - xr > 50) g.label("unresolved", (xr + xu) / 2, F.yT + 12, { color: c.photon, size: 12, weight: 600, bg: true });
    if (F.x1 - xu > 50) g.label("averaged", (xu + F.x1) / 2, F.yT + 12, { color: c.accent, size: 12, weight: 600, bg: true });
    if (phone) { g.label("capture as measured, finite resolution", F.x0, F.yT - 30, { color: c.ink, size: 12, weight: 600, align: "left" }); g.label("dashed: Hauser–Feshbach with fluctuations", F.x0, F.yT - 14, { color: c.soft, size: 11, align: "left" }); }
    else g.label("capture as measured with finite resolution · dashed: Hauser–Feshbach with fluctuations", F.x0, F.yT - 14, { color: c.ink, size: 12, weight: 600, align: "left" });
    g.label(`resolution reaches D₀/3 at ${R.er < 1000 ? R.er.toFixed(0) + " eV" : (R.er / 1000).toFixed(1) + " keV"}`, W / 2, F.yB + (phone ? 34 : 38), { color: c.ink, size: phone ? 12 : 14, weight: 600, serif: true, bg: true });
    // a pulse of neutrons racing down a flight path: slow ones arrive late, spread in time = spread in energy
    const fy = H * 0.9, fx0 = W * 0.1, fx1 = W * 0.9, t = (((S.time % 2.4) + 2.4) % 2.4) / 2.4;
    g.line(fx0, fy, fx1, fy, c.soft, 1.2, 0.5, [3, 4]);
    for (let i = 0; i < 12; i++) { const v = 0.35 + 0.65 * ((i * 0.6180339) % 1), x = fx0 + (fx1 - fx0) * Math.min(1, t * v * 1.6); g.ball(x, fy - 2 - (i % 3) * 5, 3.5, c.neutron, x >= fx1 ? 0.3 : 0.9); }
    g.label("time of flight: the arrival time measures the energy", W / 2, fy + 16, { color: c.soft, size: 11 });
  }
  const resW = (E, s) => s * 2.5e-4 * Math.pow(E, 1.5);    // eV, illustrative time-of-flight resolution
})();
