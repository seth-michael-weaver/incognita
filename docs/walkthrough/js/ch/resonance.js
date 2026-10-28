/* Chapter 15: the resonance peaks (physics/resonance/). Scenes (S.mode):
 *   "forest"  = one statistical ladder drawn as Breit-Wigner peaks (at E_i, width = Gamma, height = log of the
 *               peak capture cross section); a neutron hops along in energy and is caught with probability set by sigma;
 *   "spacing" = three rows of peaks: Poisson, random-matrix (Wigner/GOE), two GOE sequences mixed;
 *   "widths"  = Porter-Thomas: peaks of LINEAR height = Gn, a yellow Gg cap; "roll a width" squares a bell-curve number;
 *   "params"  = the ladder regrown live from D0, S0, <Gg> (S1 fixed); p-wave (negative parity) peaks hollow;
 *   "thermal" = log-energy ground: neutrons slowing down in equal log steps through the peaks to thermal;
 *   "ensemble"= one row per ladder: peaks near 0 eV, the thermal neutron, a disc of area sigma_th, a pile of values.
 * Follows physics/resonance/ladder.py: spin groups for I = 0 (one s-wave sequence J = 1/2, two p-wave sequences),
 * reduced widths at 1 eV, Gn = Gn^l sqrt(E) V_l, Porter-Thomas chi^2_1, <Gg> with ~100 dof, SLBW capture with
 * pi/k^2 in barns, k = 2.196807e-3 awri/(awri+1) sqrt(E). Spacings are real GOE levels: the Dumitriu-Edelman
 * tridiagonal ensemble, eigenvalues by Sturm bisection, middle 60 % unfolded with the semicircle (goe_unit_levels).
 * Illustrative target: A = 238, I = 0. */
(function () {
  const { TAU, clamp, lerp, smooth, rng } = WT.util;
  const KC = 2.196807e-3 * 238 / 239, RAD = 0.123 * Math.cbrt(238) + 0.08, S1 = 1.6e-4, EMAX = 300, ETH = 0.0253, ECUT = 0.5;
  const fJ = (j) => (2 * j + 1) * Math.exp(-((j + 0.5) ** 2) / 20), D_P32 = fJ(0.5) / fJ(1.5);
  const log10 = (x) => Math.log(x) / Math.LN10;

  /** eigenvalues of a symmetric tridiagonal matrix (diagonal d, off-diagonal e) by Sturm-sequence bisection */
  function tridiagEig(d, e) {
    const n = d.length, e2 = Array.from(e, (v) => v * v); let lo = Infinity, hi = -Infinity;
    for (let i = 0; i < n; i++) { const rad = (i > 0 ? Math.abs(e[i - 1]) : 0) + (i < n - 1 ? Math.abs(e[i]) : 0); lo = Math.min(lo, d[i] - rad); hi = Math.max(hi, d[i] + rad); }
    const count = (x) => { let c = 0, q = 1; for (let i = 0; i < n; i++) { q = d[i] - x - (i > 0 ? e2[i - 1] / (q === 0 ? 1e-300 : q) : 0); if (q < 0) c++; } return c; };
    const out = []; let a0 = lo;
    for (let k = 0; k < n; k++) { let a = a0, b = hi; for (let it = 0; it < 60; it++) { const mid = 0.5 * (a + b); if (count(mid) > k) b = mid; else a = mid; if (b - a < 1e-9 * (Math.abs(hi) + 1)) break; } out.push(0.5 * (a + b)); a0 = a; }
    return out;
  }
  /** n GOE levels with unit mean spacing, starting at 0 (ladder.py goe_unit_levels, one block) */
  function goeUnit(n, r) {
    const m = Math.max(40, Math.ceil(n / 0.6) + 6), nrm = () => Math.sqrt(-2 * Math.log(1 - r())) * Math.cos(TAU * r());
    const chi = (k) => { if (k < 30) { let s = 0; for (let i = 0; i < k; i++) { const z = nrm(); s += z * z; } return s; } const z = nrm(); return k * Math.pow(1 - 2 / (9 * k) + z * Math.sqrt(2 / (9 * k)), 3); };
    const d = [], e = []; for (let i = 0; i < m; i++) d.push(nrm()); for (let i = 0; i < m - 1; i++) e.push(Math.sqrt(chi(m - 1 - i) / 2));
    const R = Math.sqrt(2 * m), out = [];
    for (const v of tridiagEig(d, e)) { const x = clamp(v / R, -1, 1), cdf = m * (0.5 + (x * Math.sqrt(1 - x * x) + Math.asin(x)) / Math.PI); if (cdf > 0.2 * m && cdf < 0.8 * m) out.push(cdf); }
    const u0 = out[0]; return out.map((v) => v - u0).slice(0, n);
  }
  function makeDraws(sd, nS = 300, nP = 160) {
    const r = rng(sd);
    const poi = (n) => { const a = []; let s = 0; for (let i = 0; i < n; i++) { s += -Math.log(1 - r()); a.push(s); } return a; };
    const nrm = (n) => { const a = []; for (let i = 0; i < n; i++) a.push(Math.sqrt(-2 * Math.log(1 - r())) * Math.cos(TAU * r())); return a; };
    return { lvS: goeUnit(nS, r), lvP1: goeUnit(nP, r), lvP2: goeUnit(nP, r), poi: poi(nS), z: nrm(nS), zp: nrm(2 * nP), zg: nrm(nS + 2 * nP), u0: r() };
  }
  /** one ladder: {l, g, er, gnr (reduced width at 1 eV), gg} sorted by energy */
  function ladder(dr, D0, S0, Gg, ptMix) {
    const res = [], emin = -Math.min(150, 50 * D0), nS = dr.lvS.length, nP = dr.lvP1.length;
    for (let i = 0; i < nS; i++) { const e = emin + (dr.lvS[i] - dr.u0) * D0; if (e < emin) continue; if (e > EMAX) break; const z = dr.z[i]; res.push({ id: "s" + i, l: 0, g: 1, er: e, gnr: S0 * D0 * lerp(1, z * z, ptMix), gg: Gg * (1 + 0.14 * dr.zg[i]) }); }
    [[dr.lvP1, 1, 1], [dr.lvP2, 2, D_P32]].forEach(([lv, gJ, dJ], q) => {
      for (let i = 0; i < nP; i++) { const e = (lv[i] - 0.3 - q * 0.41) * D0 * dJ; if (e < 0) continue; if (e > EMAX) break; const z = dr.zp[q * nP + i]; res.push({ id: "p" + q + "_" + i, l: 1, g: gJ, er: e, gnr: S1 * D0 * dJ * lerp(1, z * z, ptMix), gg: Gg * (1 + 0.14 * dr.zg[nS + q * nP + i]) }); }
    });
    return res.sort((a, b) => a.er - b.er);
  }
  function sigma(lad, E, onlyL) {
    const k = KC * Math.sqrt(E), pk = Math.PI / (k * k), rho = k * RAD, v1 = rho * rho / (1 + rho * rho), sq = Math.sqrt(E); let s = 0;
    for (const r of lad) { if (onlyL !== undefined && r.l !== onlyL) continue; const gn = r.gnr * sq * (r.l ? v1 : 1), G = gn + r.gg, d = E - r.er; s += pk * r.g * gn * r.gg / (d * d + 0.25 * G * G); }
    return s;
  }
  const widthAt = (r) => { const e = Math.abs(r.er), rho = KC * Math.sqrt(e) * RAD; return r.gnr * Math.sqrt(e) * (r.l ? rho * rho / (1 + rho * rho) : 1) + r.gg; };
  function grid(lad, lo, hi, n, logx) {
    const xs = []; for (let i = 0; i <= n; i++) xs.push(logx ? lo * Math.pow(hi / lo, i / n) : lo + (hi - lo) * i / n);
    for (const r of lad) { if (r.er <= lo || r.er >= hi) continue; const G = widthAt(r); for (const f of [-5, -2, -1, -0.5, 0, 0.5, 1, 2, 5]) { const e = r.er + f * G; if (e > lo && e < hi) xs.push(e); } }
    return xs.sort((a, b) => a - b);
  }
  function resInt(lad) { const xs = grid(lad, ECUT, EMAX, 300, true); let s = 0, prev = null; for (const e of xs) { const v = sigma(lad, e); if (prev) s += 0.5 * (v + prev[1]) * Math.log(e / prev[0]); prev = [e, v]; } return s; }
  function meanRatio(lv) { const s = []; for (let i = 1; i < lv.length; i++) s.push(lv[i] - lv[i - 1]); let t = 0, n = 0; for (let i = 1; i < s.length; i++) { t += Math.min(s[i], s[i - 1]) / Math.max(s[i], s[i - 1]); n++; } return t / n; }

  const snap = () => document.body.classList.contains("shot");
  const fmtB = (v) => (v >= 1e4 ? `${(v / 1000).toFixed(0)}k b` : v >= 1000 ? `${(v / 1000).toFixed(1)}k b` : v >= 10 ? `${v.toFixed(0)} b` : v >= 1 ? `${v.toFixed(1)} b` : `${v.toFixed(2)} b`);
  const fmt = (v) => (v >= 10 ? v.toFixed(0) : v >= 1 ? v.toFixed(1) : v.toFixed(2));
  const WX = 110;                       // peak widths are drawn this many times wider than the true resonance width
  const nrmOf = (r) => Math.sqrt(-2 * Math.log(1 - r())) * Math.cos(TAU * r());
  function erf(x) { const t = 1 / (1 + 0.3275911 * Math.abs(x)), y = 1 - ((((1.061405429 * t - 1.453152027) * t + 1.421413741) * t - 0.284496736) * t + 0.254829592) * t * Math.exp(-x * x); return x >= 0 ? y : -y; }
  const chi1cdf = (x) => erf(Math.sqrt(Math.max(x, 0) / 2));

  let seed = 3, draws = makeDraws(seed), fc = null;
  /** the current ladder as peaks: peak cross section on top of each level, total width */
  function forestOf(S) {
    const key = [S.D0.toFixed(2), S.S0.toFixed(3), S.Gg.toFixed(1), S.ptMix.toFixed(3), seed].join("|");
    if (fc && fc.key === key) return fc;
    const lad = ladder(draws, S.D0, S.S0 * 1e-4, S.Gg * 1e-3, S.ptMix);
    const trees = lad.filter((r) => r.er > 0.3 && r.er < EMAX).map((r) => ({ r, peak: sigma(lad, r.er), G: widthAt(r) }));
    trees.sort((a, b) => b.peak - a.peak);
    fc = { key, lad, trees, th: null, ri: null, terr: null }; return fc;
  }
  const thOf = (F) => (F.th ??= sigma(F.lad, ETH));
  const riOf = (F) => (F.ri ??= resInt(F.lad));

  // ---------- drawing helpers ----------
  /** A strip of ground: a soft line whose ends fade into the page, a faint fill below. */
  function groundStrip(g, x0, x1, y, depth) {
    const ctx = g.ctx, c = g.c, fw = (x1 - x0) * 0.06; ctx.save();
    const gr = ctx.createLinearGradient(0, y, 0, y + depth); gr.addColorStop(0, g.rgba(c.soft, 0.14)); gr.addColorStop(1, g.rgba(c.soft, 0));
    ctx.fillStyle = gr; ctx.fillRect(x0, y, x1 - x0, depth);
    for (const [a, b] of [[x0, x0 + fw], [x1, x1 - fw]]) { const fg = ctx.createLinearGradient(a, 0, b, 0); fg.addColorStop(0, g.rgba(c.paper, 1)); fg.addColorStop(1, g.rgba(c.paper, 0)); ctx.fillStyle = fg; ctx.fillRect(Math.min(a, b), y + 1, fw, depth); }
    const lg = ctx.createLinearGradient(x0, 0, x1, 0); lg.addColorStop(0, g.rgba(c.soft, 0)); lg.addColorStop(0.06, g.rgba(c.soft, 0.6)); lg.addColorStop(0.94, g.rgba(c.soft, 0.6)); lg.addColorStop(1, g.rgba(c.soft, 0));
    ctx.strokeStyle = lg; ctx.lineWidth = 1.5; ctx.beginPath(); ctx.moveTo(x0, y); ctx.lineTo(x1, y); ctx.stroke(); ctx.restore();
  }
  /** One resonance as its peak: the Breit-Wigner (Lorentzian) shape h / (1 + (2d/w)^2), full width w at half height.
   *  Solid = positive parity, hollow (outline only) = negative. o.down hangs it below ground. Returns the tip's y. */
  function peak(g, x, yG, h, w, o = {}) {
    const ctx = g.ctx, c = g.c, col = o.col || c.cool, a = o.alpha ?? 1, s = o.down ? -1 : 1;
    if (h < 2) { g.dot(x, yG - s * 1.5, 1.4, col, 0.45 * a); return yG; }
    const hw = Math.max(1.2, w / 2), span = Math.max(hw * 4, 4), n = 28, pts = [];
    for (let i = 0; i <= n; i++) { const d = (i / n * 2 - 1) * span, u = d / hw; pts.push([x + d, yG - s * h / (1 + u * u)]); }
    ctx.save(); ctx.globalAlpha = a; ctx.beginPath(); ctx.moveTo(x - span, yG); pts.forEach((p) => ctx.lineTo(p[0], p[1])); ctx.lineTo(x + span, yG); ctx.closePath();
    const gr = ctx.createLinearGradient(0, yG - s * h, 0, yG); gr.addColorStop(0, g.rgba(col, o.hollow ? 0.1 : 0.55)); gr.addColorStop(1, g.rgba(col, o.hollow ? 0.02 : 0.12));
    ctx.fillStyle = gr; ctx.fill();
    ctx.beginPath(); pts.forEach((p, i) => (i ? ctx.lineTo(p[0], p[1]) : ctx.moveTo(p[0], p[1])));
    ctx.strokeStyle = col; ctx.lineWidth = o.hollow ? 1.3 : 1.5; ctx.lineJoin = "round"; ctx.stroke(); ctx.restore();
    if (!o.hollow && h > 12) g.dot(x, yG - s * h, Math.min(2.4, 1 + hw * 0.25), col, a);
    return yG - s * h;
  }
  function burst(g, x, y, age, seedA) {
    const f = 1 - smooth(0.5, 0.9, age);
    g.glow(x, y, 16 + 30 * age, g.c.warm, 0.7 * (1 - age / 0.9));
    for (let k = 0; k < 4; k++) { const a = seedA + k * TAU / 4, d = 10 + age * 110; g.photon(x + Math.cos(a) * d, y + Math.sin(a) * d, a, 16, f); }
  }

  // ---------- chapter ----------
  const walk = { hop: 0, catchT: -9, catchX: 0, catchY: 0, nC: 0, nH: 0, auto: true, last: 0, r: rng(11) };
  const pt = { trees: [], pile: [], roll: null, auto: 0, r: rng(41) };
  const sd = { ns: [], down: 0, reached: 0, spawn: 2, queue: 0, r: rng(77) };
  const ens = { rows: [], pile: [], ri: [], queue: 0, qT: 0, auto: 0, k: 0 };

  WT.chapter("resonance", {
    num: "Chapter 15", title: "Sharp peaks", short: "Resonances",
    lead: "At low enough energy a neutron no longer sees a smooth, averaged nucleus. It sees the compound nucleus's individual energy levels, one at a time.",
    html: `
<div class="step">
  <p>Each peak is one <b>resonance</b>: an energy level of the compound nucleus that a neutron of exactly that energy can drop into. Its height is the <b>capture</b> cross section there (neutron absorbed, photons out) on a logarithmic scale; its width is the resonance width Γ, drawn about a hundred times wider than it is.</p>
  <div class="ctl"><label for="res-e">Neutron energy (eV)</label><input id="res-e" type="range" data-bind="En" min="0.5" max="300" step="0.1" value="30"><output data-show="En" data-fmt="1"></output></div>
  <p>The neutron hops along in energy; where it lands it may be captured, in a flash of photons. On a peak the cross section is thousands of barns and capture is almost certain; between peaks it is a few barns. Drag the energy to park it on a peak, then between two.</p>
</div>
<div class="step">
  <h3>Peaks keep their distance</h3>
  <p>The middle row shows how real levels sit: two levels with the same spin and parity repel, so near-coincidences are rare. <b>Random-matrix theory</b> describes this pattern. Truly random positions (top row) clump and leave gaps.</p>
  <div class="btns"><button class="btn" data-act="again">Draw again</button></div>
  <p>Draw again for a new sample. ⟨r̃⟩ compares each spacing with the next: about 0.39 for random, 0.53 for repelling levels; the code uses the repelling pattern. Mixing two sequences, say two spins (bottom row), partly hides the repulsion.</p>
</div>
<div class="step">
  <h3>Heights scatter wildly</h3>
  <p>Now each peak's height is its <b>neutron width</b> Γ<sub>n</sub> on a linear scale: how strongly the level couples to a neutron. The yellow cap is its γ width Γ<sub>γ</sub>, how fast it emits photons; it sums hundreds of photon paths, so it is nearly the same for every level.</p>
  <div class="btns"><button class="btn" data-act="roll">Roll a width</button><button class="btn ghost" data-act="equal">Equal widths</button><button class="btn ghost" data-act="pt">Porter–Thomas</button></div>
  <p>A level has only one way to break up into neutron plus target, so its width behaves like the square of one bell-curve number. Roll one: the ball lands at <i>x</i>, <i>x</i>² becomes the next peak's height, and a dot drops into the pile. The pile crowds near zero with a long tail, the <b>Porter–Thomas</b> law: most levels are weak, a few enormous. Equal widths shows a row of average peaks instead.</p>
</div>
<div class="step">
  <h3>A ladder from four numbers</h3>
  <p>The peaks now come from four averages you can set. For an unmeasured nucleus only these averages can be predicted: the mean spacing <i>D</i><sub>0</sub>; the <b>strength functions</b> <i>S</i><sub>0</sub> and <i>S</i><sub>1</sub>, the average neutron width per unit spacing for s-wave (head-on) and p-wave (off-centre) neutrons; and the average γ width. From these the code builds a <b>ladder</b>: one random set of levels with those averages. Three have sliders here; <i>S</i><sub>1</sub> stays fixed (its value is written under the peaks).</p>
  <div class="ctl"><label for="res-d0">Spacing D₀ (eV)</label><input id="res-d0" type="range" data-bind="D0" min="3" max="60" step="0.5" value="20"><output data-show="D0" data-fmt="1"></output></div>
  <div class="ctl"><label for="res-s0">Strength S₀ (×10⁻⁴)</label><input id="res-s0" type="range" data-bind="S0" min="0.2" max="3" step="0.05" value="1"><output data-show="S0" data-fmt="2"></output></div>
  <div class="ctl"><label for="res-gg">γ width ⟨Γγ⟩ (meV)</label><input id="res-gg" type="range" data-bind="Gg" min="10" max="80" step="1" value="23"><output data-show="Gg" data-fmt="0"></output></div>
  <p>Drag <i>D</i><sub>0</sub> and the peaks spread out or crowd together. Solid peaks are s-wave levels (positive parity), outlined peaks p-wave (negative parity). Neutron widths grow as √<i>E</i> for s-waves and as <i>E</i><sup>3/2</sup> for p-waves, so the outlined peaks start short and grow toward the right.</p>
</div>
<div class="step">
  <h3>Down at thermal</h3>
  <p>The same peaks on a logarithmic energy scale, down to thousandths of an eV. Reactor neutrons slow down by bouncing off light nuclei, losing about the same fraction of their energy each time, so every hop here is the same length. Some are caught by the peaks on the way.</p>
  <div class="btns"><button class="btn" data-act="slow">Slow down 10 neutrons</button></div>
  <p>Those that get through settle at room temperature, 0.025 eV, the <b>thermal</b> energy, far below the first peak. There the cross section, the disc's area, is the sum of the resonances' tails, including bound levels just below zero; the tails grow as 1/<i>v</i> (<i>v</i> the neutron's speed), so the ground rises to the left. The catch on the way down is measured by the <b>resonance integral</b>: the cross section above 0.5 eV, each energy weighted by 1/<i>E</i>.</p>
</div>
<div class="step">
  <h3>Only the statistics are predictable</h3>
  <p>Each row is one ladder drawn from the same four numbers, with a disc whose area is its thermal capture cross section. The bracket reaches to the peak that sets that value, usually the nearest; its distance changes from ladder to ladder, and the disc swings by a factor of ten or more.</p>
  <div class="btns"><button class="btn" data-act="draw1">Draw a ladder</button><button class="btn ghost" data-act="more">Draw 20</button></div>
  <p>Each value drops into the pile on the right. For an unmeasured nucleus the answer is a spread of values, not one number, and no better model can narrow it. The resonance integral, a sum over many peaks, spreads less. Where levels are more than about 10 keV apart, as in light nuclei, none is near thermal: capture there is direct, and the code refuses to answer.</p>
  <div class="aside">In the code: <code>physics/resonance/ladder.py</code> (random-matrix spacings, Porter–Thomas widths, Breit–Wigner cross sections, thermal capture and resonance integral over an ensemble), <code>ladder_statistics.py</code> (the same laws tested on measured ladders), <code>ensemble_runner.py</code>. These run beside the reaction engine, not inside it.</div>
</div>`,
    setup(S) {
      S.set("mode", "forest"); S.to("En", 30, true); S.to("D0", 20, true); S.to("S0", 1, true); S.to("Gg", 23, true); S.to("ptMix", 1, true);
      S.on("again", () => { seed += 1; draws = makeDraws(seed); });
      S.on("equal", () => S.to("ptMix", 0)); S.on("pt", () => S.to("ptMix", 1));
      S.on("roll", () => startRoll(S));
      S.on("slow", () => { sd.queue += 10; });
      S.on("draw1", () => { ens.queue += 1; ens.qT = 9; });
      S.on("more", () => { ens.queue += 20; });
    },
    steps: [
      (S) => { S.set("mode", "forest"); S.to("ptMix", 1); walk.auto = true; walk.last = NaN; },
      (S) => { S.set("mode", "spacing"); },
      (S) => { S.set("mode", "widths"); S.to("ptMix", 1); if (!pt.trees.length) seedPT(); },
      (S) => { S.set("mode", "params"); S.to("ptMix", 1); },
      (S) => { S.set("mode", "thermal"); S.to("ptMix", 1); if (!sd.ns.length) seedSlow(S); },
      (S) => { S.set("mode", "ensemble"); S.to("ptMix", 1); if (!ens.rows.length) for (let i = 0; i < 18; i++) addRow(S, true); },
    ],
    frame(g, S, dt) {
      if (S.mode === "spacing") sceneSpacing(g, S);
      else if (S.mode === "widths") scenePT(g, S, dt);
      else if (S.mode === "thermal") sceneThermal(g, S, dt);
      else if (S.mode === "ensemble") sceneEnsemble(g, S, dt);
      else sceneForest(g, S, dt);
    },
  });

  /** cross section as the drawing shows it: each peak spread over its (exaggerated) width, plus the true background */
  function sigVis(F, E, x, xs, ws) {
    let s = sigma(F.lad, E);
    for (let i = 0; i < F.trees.length; i++) { const d = 2 * (x - xs[i]) / ws[i]; if (Math.abs(d) < 6) s = Math.max(s, F.trees[i].peak / (1 + d * d)); }
    return s;
  }

  // ---------- scene: the peaks (steps 0 and 3) ----------
  const fx = [], fw = [];
  function sceneForest(g, S, dt) {
    const { W, H, c } = g, phone = W < 600, fs = phone ? 11 : 13, params = S.mode === "params";
    const x0 = W * 0.05, x1 = W * 0.96, yG = H * (params ? 0.72 : 0.7), hMax = H * (params ? 0.58 : 0.56);
    const X = (e) => x0 + (x1 - x0) * e / EMAX, ppe = (x1 - x0) / EMAX, F = forestOf(S);
    const hOf = (pk) => hMax * clamp(log10(Math.max(pk, 1e-6)) / 5, 0, 1);
    groundStrip(g, x0 - 12, x1 + 12, yG, H * 0.07);
    F.trees.forEach((t, i) => {
      const x = X(t.r.er), h = hOf(t.peak), w = clamp(t.G * ppe * WX, 3.5, 34); fx[i] = x; fw[i] = w;
      peak(g, x, yG, h, w, { hollow: t.r.l === 1, sway: Math.sin(S.time * 1.1 + x * 0.07) * (0.6 + h / 140) });
    });
    [0, 100, 200, 300].forEach((e) => g.label(`${e} eV`, clamp(X(e), x0 + 16, x1 - 16), yG + 14, { color: c.faint, size: fs - 2 }));
    g.label(phone ? "height: peak capture (log) · width Γ ×110" : "peak height: capture cross section (log scale) · width: resonance width Γ, drawn 110× wide", x0, H * 0.06, { color: c.faint, size: fs - 1, align: "left" });
    if (params) {
      g.label(`D₀ ${S.D0.toFixed(0)} eV · S₀ ${S.S0.toFixed(2)}×10⁻⁴ · S₁ ${(S1 * 1e4).toFixed(1)}×10⁻⁴ · ⟨Γγ⟩ ${S.Gg.toFixed(0)} meV`, W * 0.5, yG + 40, { color: c.ink, size: fs + 1, weight: 600, serif: true });
      const ly = H * 0.9; peak(g, W * 0.5 - (phone ? 120 : 150), ly + 8, 22, 9, {}); g.label("s-wave (+ parity)", W * 0.5 - (phone ? 110 : 140), ly - 3, { color: c.soft, size: fs, align: "left" });
      peak(g, W * 0.5 + (phone ? 14 : 30), ly + 8, 22, 9, { hollow: true }); g.label("p-wave (− parity)", W * 0.5 + (phone ? 24 : 40), ly - 3, { color: c.soft, size: fs, align: "left" });
      return;
    }
    // the walking neutron
    if (walk.auto && S.target.En !== walk.last && !Number.isNaN(walk.last)) walk.auto = false;
    if (walk.auto) { let e = S.En + 7 * dt; if (e > EMAX - 1) e = 1; S.set("En", e); walk.last = e; const inp = document.getElementById("res-e"); if (inp) inp.value = e; }   // the slider's thumb follows the walk
    const E = clamp(S.En, 0.5, EMAX - 0.5), wx = X(E), HOP = 0.34, sv = sigVis(F, E, wx, fx, fw), P = sv / (sv + 300);
    walk.hop += dt;
    if (walk.hop >= HOP) { walk.hop -= HOP; if (S.time - walk.catchT > 0.9) { walk.nH++; if (walk.r() < P) { walk.catchT = S.time; walk.catchX = wx; walk.catchY = yG - 10; walk.nC++; } } }
    const age = S.time - walk.catchT;
    if (age < 0.9) burst(g, walk.catchX, walk.catchY, age, walk.nC * 0.7);
    else { const u = walk.hop / HOP, by = yG - 7 - Math.sin(Math.PI * u) * 12; g.ball(wx, by, 6.5, c.neutron); }
    const lx = clamp(wx, x0 + (phone ? 80 : 120), x1 - (phone ? 80 : 120));
    g.line(wx, yG + 3, wx, yG + 24, c.neutron, 1, 0.5, [2, 3]);
    g.label(`σ ≈ ${fmtB(sv)} · caught on ${P < 0.01 ? "<1" : (100 * P).toFixed(0)} % of landings`, lx, yG + 36, { color: c.ink, size: fs, weight: 600, bg: true });
    g.label(`caught ${walk.nC} times in ${walk.nH} landings`, W * 0.5, yG + 62, { color: c.soft, size: fs });
    g.label(phone ? "each peak: one level of the compound nucleus" : `each peak: one level of the compound nucleus · about ${S.D0.toFixed(0)} eV apart`, W * 0.5, H * 0.92, { color: c.soft, size: fs + 1, serif: true, italic: true });
  }

  // ---------- scene: spacing rows ----------
  function sceneSpacing(g, S) {
    const { W, H, c } = g, fs = W < 600 ? 11 : 13, x0 = W * 0.06, x1 = W * 0.96, nShow = 26;
    const rows = [
      { name: "random positions (Poisson)", lv: draws.poi, col: c.faint, expect: "clumps and gaps" },
      { name: "repelling levels (random-matrix)", lv: draws.lvS, col: c.cool, expect: "evenly kept apart" },
      { name: "two repelling sequences mixed", lv: draws.lvP1.map((v) => 2 * v).concat(draws.lvP2.map((v) => 2 * v + 0.37)).sort((a, b) => a - b), col: c.accent, expect: "repulsion half hidden" },
    ];
    rows.forEach((row, i) => {
      const y = H * (0.24 + 0.27 * i), hT = H * 0.09, px = (x1 - x0) / nShow, r = meanRatio(row.lv.slice(0, 300));
      groundStrip(g, x0 - 10, x1 + 10, y, H * 0.04);
      for (const v of row.lv) { const x = x0 + (v - row.lv[0]) * px; if (x > x1) break; peak(g, x, y, hT, 9, { col: row.col, sway: Math.sin(S.time * 1.1 + x * 0.07) * 0.8 }); }
      const ph = W < 600;                                   // phones: name and result on two lines, so they never touch
      g.label(row.name, x0, y - hT - (ph ? 30 : 14), { color: row.col === c.faint ? c.soft : row.col, size: fs, align: "left", weight: 600 });
      g.label(ph ? `${row.expect} · ⟨r̃⟩ ≈ ${r.toFixed(2)}` : `${row.expect} · spacing ratio ⟨r̃⟩ ≈ ${r.toFixed(2)}`, ph ? x0 : x1, y - hT - 14, { color: c.soft, size: fs - 1, align: ph ? "left" : "right", bg: true });
    });
    g.label(W < 600 ? "⟨r̃⟩: 0.39 if random, 0.53 for random-matrix" : "same average spacing in every row · ⟨r̃⟩: 0.39 if random, 0.53 for random-matrix", W * 0.5, H * 0.93, { color: c.ink, size: fs + 1, serif: true, italic: true });
  }

  // ---------- scene: Porter-Thomas ----------
  function seedPT() { for (let i = 0; i < 16; i++) { const z = nrmOf(pt.r); pt.trees.push({ z2: z * z, gg: 1 + 0.07 * nrmOf(pt.r), pos: i + 2 }); pt.pile.push(z * z); } }
  function commitTree() { const rl = pt.roll; if (!rl || rl.done) return; pt.trees.push({ z2: rl.z * rl.z, gg: 1 + 0.07 * nrmOf(pt.r), pos: 99, born: true }); rl.done = true; }
  function startRoll(S) { if (pt.roll) { commitTree(); pt.pile.push(pt.roll.z * pt.roll.z); } pt.roll = { z: nrmOf(pt.r), t0: S.time, done: false }; pt.auto = 0; }
  function scenePT(g, S, dt) {
    const { W, H, c } = g, phone = W < 600, fs = phone ? 11 : 13, NT = phone ? 12 : 18;
    const rx0 = W * 0.04, rx1 = W * (phone ? 0.63 : 0.65), slot = (rx1 - rx0) / NT, yG = H * 0.55, hMean = H * 0.085, hCap = Math.max(4, H * 0.011);
    const maxH = yG - H * 0.14 - hCap, slotX = (p) => rx0 + (p + 0.5) * slot;
    // roll timeline
    pt.auto += dt; if (!pt.roll && pt.auto > 2.6 && pt.pile.length < 70) startRoll(S);
    const rl = pt.roll, age = rl ? S.time - rl.t0 : 0;
    if (rl && age >= 1.9) commitTree();
    if (rl && age >= 2.5) { pt.pile.push(rl.z * rl.z); pt.roll = null; }
    while (pt.trees.length > NT) pt.trees.shift();
    while (pt.pile.length > 160) pt.pile.shift();
    const a = 1 - Math.exp(-6 * dt);
    groundStrip(g, rx0 - 10, rx1 + 10, yG, H * 0.05);
    const off = NT - pt.trees.length;
    pt.trees.forEach((t, i) => {
      const p = i + off; if (t.pos === 99) t.pos = p; t.pos += (p - t.pos) * a;
      const raw = lerp(1, t.z2, S.ptMix) * hMean, h = Math.min(maxH, raw), x = slotX(t.pos), w = slot * 0.62;
      const top = peak(g, x, yG, h, w, { sway: Math.sin(S.time * 1.2 + i) * 0.8 });
      g.ctx.save(); g.ctx.fillStyle = g.rgba(c.photon, 0.95); g.ctx.beginPath(); const cw = w * 0.75, chh = hCap * t.gg;
      if (g.ctx.roundRect) g.ctx.roundRect(x - cw / 2, top - chh, cw, chh, 3); else g.ctx.rect(x - cw / 2, top - chh, cw, chh); g.ctx.fill(); g.ctx.restore();
      if (raw > maxH + 1) g.label("↑", x, top - hCap - 9, { color: c.soft, size: 12 });
    });
    g.label(phone ? "height: neutron width Γn (linear)" : "peak height: neutron width Γn, linear scale", rx0, H * 0.05, { color: c.soft, size: fs, align: "left" });
    g.label(phone ? "yellow: γ width" : "yellow cap: γ width, nearly the same on every peak", rx0, H * 0.05 + fs + 6, { color: c.photon, size: fs, align: "left" });
    if (S.ptMix < 0.5) g.label("equal widths: every peak the average", (rx0 + rx1) / 2, yG - hMean - hCap - 26, { color: c.ink, size: fs + 1, weight: 600, bg: true });
    // the pile of rolled widths
    const px0 = W * (phone ? 0.69 : 0.71), px1 = W * 0.97, NB = 13, bw = (px1 - px0) / NB, dr = clamp(bw / 4.6, 1.4, 3.4), pitch = 2 * dr + 0.7;
    const cnt = new Array(NB).fill(0), binOf = (v) => Math.min(NB - 1, Math.floor(v / 0.5));
    for (const v of pt.pile) { const b = binOf(v), k = cnt[b]++; g.dot(px0 + (b + 0.5) * bw + ((k % 2) - 0.5) * (2 * dr + 0.5), yG - dr - 1 - Math.floor(k / 2) * pitch, dr, c.accent, 0.85); }
    const N = pt.pile.length, ref = [];
    for (let b = 0; b < NB; b++) { const p = b < NB - 1 ? chi1cdf((b + 1) * 0.5) - chi1cdf(b * 0.5) : 1 - chi1cdf(6), hh = Math.min(yG - H * 0.08, (N * p / 2) * pitch); ref.push([px0 + b * bw, yG - hh], [px0 + (b + 1) * bw, yG - hh]); }
    g.poly(ref, c.soft, 1, 0.55, [3, 3]);
    g.line(px0 - 4, yG, px1 + 4, yG, c.line, 1);
    [0, 2, 4, 6].forEach((v) => g.label(v === 6 ? "6+" : String(v), px0 + v * 2 * bw, yG + 12, { color: c.faint, size: fs - 2 }));
    g.label(phone ? "rolled widths" : "pile of rolled widths", (px0 + px1) / 2, yG + 28, { color: c.soft, size: fs - 1 });
    g.label(phone ? "× average" : "(in units of the average)", (px0 + px1) / 2, yG + 28 + fs + 2, { color: c.faint, size: fs - 2 });
    g.label(phone ? "dashed: Porter–Thomas" : "dashed: the Porter–Thomas law", px1, H * 0.12, { color: c.soft, size: fs - 1, align: "right" });
    // the bell and the square
    const bx0 = W * 0.05, bx1 = W * (phone ? 0.45 : 0.42), by = H * 0.9, bh = H * 0.11, u = (bx1 - bx0) / 7, bcx = (bx0 + bx1) / 2;
    const bell = []; for (let i = 0; i <= 60; i++) { const x = -3.5 + 7 * i / 60; bell.push([bcx + x * u, by - bh * Math.exp(-x * x / 2)]); }
    g.area([[bx0, by], ...bell, [bx1, by]], c.soft, 0.1); g.poly(bell, c.soft, 1.5, 0.8); g.line(bx0, by, bx1, by, c.line, 1);
    [-2, 0, 2].forEach((v) => g.label(String(v).replace("-", "−"), bcx + v * u, by + 12, { color: c.faint, size: fs - 2 }));
    g.label("bell-curve number x", bcx, by - bh - 14, { color: c.soft, size: fs - 1 });
    const sqX = W * (phone ? 0.5 : 0.48);
    if (rl) {
      const z = clamp(rl.z, -3.4, 3.4), lx = bcx + z * u, ly = by - bh * Math.exp(-z * z / 2), s = Math.min(Math.abs(z) * u, H * 0.3);
      if (age < 0.6) { const f = smooth(0, 0.6, age); g.dot(lx, lerp(by - bh - 40, ly - 5, f * f), 5, c.ink); }
      else if (age < 1.9) g.dot(lx, ly - 5, 5, c.ink, 1 - smooth(1.4, 1.9, age));
      if (age >= 0.6 && age < 1.9) {
        const k = age < 1.2 ? smooth(0.6, 1.2, age) : 1, m = smooth(1.2, 1.9, age);
        const tx = slotX(NT - 1), th = Math.min(maxH, lerp(1, z * z, S.ptMix) * hMean), tw = slot * 0.3;
        const rx = lerp(sqX, tx - tw / 2, m), rw = lerp(s * k, tw, m), rh = lerp(s * k, th, m), ry = lerp(by, yG, m) - rh;
        g.ctx.save(); g.ctx.fillStyle = g.rgba(c.accent, 0.18); g.ctx.strokeStyle = c.accent; g.ctx.lineWidth = 1.5; g.ctx.fillRect(rx, ry, rw, rh); g.ctx.strokeRect(rx, ry, rw, rh); g.ctx.restore();
        if (m < 0.3) { g.line(lx, ly, sqX, by, c.faint, 1, 0.5 * k, [2, 3]); g.label(`x = ${z.toFixed(2).replace("-", "−")}  →  x² = ${(z * z).toFixed(2)}`, sqX + Math.max(s, 40) * k + 8, by - 10, { color: c.ink, size: fs, align: "left", bg: true }); }
      }
      if (age >= 1.9) { const f = smooth(1.9, 2.5, age), b = binOf(z * z), tx = slotX(NT - 1), th = Math.min(maxH, lerp(1, z * z, S.ptMix) * hMean); g.dot(lerp(tx, px0 + (b + 0.5) * bw, f), lerp(yG - th - hCap, yG - 20, f) - Math.sin(Math.PI * f) * 40, dr + 1, c.accent); }
    } else g.label("press Roll a width", sqX + 10, by - 10, { color: c.faint, size: fs - 1, align: "left" });
  }

  // ---------- scene: slowing down to thermal ----------
  function seedSlow(S) { for (let i = 0; i < 3; i++) spawnSlow(S, 300 * Math.pow(0.12, i)); sd.ns.push({ st: "thermal", t: S.time - 1, dx: 6, j: 1 }); sd.reached++; sd.spawn = 0; }
  function spawnSlow(S, E0) { const E = E0 || 300; sd.ns.push({ E0: E, E1: E * (0.62 + 0.38 * sd.r()), u: 0, st: "hop", t: S.time, j: sd.r() * TAU }); }
  function sceneThermal(g, S, dt) {
    const { W, H, c } = g, phone = W < 600, fs = phone ? 11 : 13, lo = 0.003, hi = EMAX;
    const x0 = W * 0.06, x1 = W * 0.96, yG = H * 0.7, hMax = H * 0.46, LN = Math.log(hi / lo);
    const X = (e) => x0 + (x1 - x0) * Math.log(e / lo) / LN, F = forestOf(S), hOf = (pk) => hMax * clamp(log10(Math.max(pk, 1e-6)) / 5, 0, 1);
    // ground rising toward low energy: the 1/v tails (capped where the peaks take over)
    if (!F.terr || F.terr.W !== W) { const pts = []; for (let i = 0; i <= 90; i++) { const e = lo * Math.pow(10, i * log10(3 / lo) / 90); pts.push([e, Math.min(sigma(F.lad, e), e < 1 ? 1e4 : 60)]); } F.terr = { W, pts }; }
    const terr = F.terr.pts.map(([e, s]) => [X(e), yG - hOf(s)]);
    g.ground([[terr[0][0], yG], ...terr, [terr[terr.length - 1][0], yG]], c.soft, 40, 0.26); g.poly(terr, c.soft, 1.6, 0.75);
    const yAt = (e) => { if (e >= 3) return yG; const i = clamp(Math.round(log10(e / lo) / log10(3 / lo) * 90), 0, 90); return terr[i][1]; };
    groundStrip(g, x0 - 12, x1 + 12, yG, H * 0.06);
    F.trees.forEach((t, i) => { const e = t.r.er, x = X(e), ppe = (x1 - x0) / LN / e, w = clamp(t.G * ppe * 30, 3, 26); fx[i] = x; fw[i] = w; peak(g, x, yG, hOf(t.peak), w, { hollow: t.r.l === 1, sway: Math.sin(S.time + x * 0.05) * 0.6 }); });
    // bound level below zero energy, drawn sunk under the left edge
    const bound = F.lad.filter((r) => r.l === 0 && r.er < 0).pop();
    if (bound) { peak(g, x0 + 4, yG, H * 0.09, 10, { down: true, alpha: 0.55 }); g.label(phone ? `bound level −${(-bound.er).toFixed(1)} eV` : `a bound level at −${(-bound.er).toFixed(1)} eV: its tail lifts this end`, x0 + 16, yG + H * 0.07, { color: c.soft, size: fs - 1, align: "left" }); }
    // resonance-integral stretch
    const yb = H * 0.16; g.line(X(ECUT), yb, x1, yb, c.photon, 2, 0.7); g.line(X(ECUT), yb - 5, X(ECUT), yb + 5, c.photon, 2, 0.7); g.line(x1, yb - 5, x1, yb + 5, c.photon, 2, 0.7);
    g.label(phone ? `resonance integral ≈ ${riOf(F).toFixed(0)} b` : `resonance integral above 0.5 eV ≈ ${riOf(F).toFixed(0)} b`, (X(ECUT) + x1) / 2, yb - 14, { color: c.photon, size: fs, weight: 600, bg: true });
    // thermal point and its target disc
    const th = thOf(F), xt = X(ETH), rD = clamp(14 * Math.sqrt(th / 10), 5, H * 0.12), yD = yAt(ETH) - rD - H * 0.09;
    g.line(xt, yD + rD, xt, yAt(ETH) - 14, c.neutron, 1, 0.45, [2, 3]);
    g.dot(xt, yD, rD, c.neutron, 0.12); g.ring(xt, yD, rD, c.neutron, 1.2, 0.6); g.nucleus(xt, yD, Math.min(8, rD * 0.6), { N: 20, Z: 8, t: S.time, jiggle: 0.3 });
    g.label(`thermal, 0.025 eV: σ ≈ ${fmtB(th)}`, clamp(xt, x0 + 90, x1), yD - rD - 14, { color: c.ink, size: fs, weight: 600, bg: true });
    g.label("1/v", X(0.006), yAt(0.006) - 14, { color: c.soft, size: fs, bg: true });
    [0.01, 0.1, 1, 10, 100].forEach((e) => g.label(`${e} eV`, X(e), yG + 14, { color: c.faint, size: fs - 2 }));
    // neutrons slowing down
    sd.spawn += dt; if (sd.queue > 0 && sd.spawn > 0.35) { spawnSlow(S); sd.queue--; sd.spawn = 0; } else if (sd.spawn > 2.4 && sd.ns.length < 4) { spawnSlow(S); sd.spawn = 0; }
    const HOP = 0.2;
    for (let i = sd.ns.length - 1; i >= 0; i--) {
      const n = sd.ns[i], age = S.time - n.t;
      if (n.st === "hop") {
        n.u += dt / HOP;
        if (n.u >= 1) {
          n.u = 0; const E = n.E1;
          if (E > ECUT) { const x = X(E), sv = sigVis(F, E, x, fx, fw); if (sd.r() < sv / (sv + 300)) { n.st = "caught"; n.t = S.time; n.x = x; n.y = yG - 10; sd.down++; continue; } }
          if (E < 0.035) { n.st = "thermal"; n.t = S.time; n.dx = (sd.r() - 0.5) * 30; sd.reached++; continue; }
          n.E0 = E; n.E1 = E * (0.62 + 0.38 * sd.r());
        }
        const xa = X(n.E0), xb = X(n.E1), x = lerp(xa, xb, n.u), y = lerp(yAt(n.E0), yAt(n.E1), n.u) - 6 - Math.sin(Math.PI * n.u) * 14;
        g.ball(x, y, 5.5, c.neutron);
      } else if (n.st === "caught") { if (age > 0.9) { sd.ns.splice(i, 1); continue; } burst(g, n.x, n.y, age, n.j); }
      else { if (age > 4) { sd.ns.splice(i, 1); continue; } const f = 1 - smooth(3.4, 4, age); g.ball(xt + n.dx + Math.sin(S.time * 7 + n.j) * 4, yAt(ETH) - 6 - Math.abs(Math.sin(S.time * 9 + n.j)) * 4, 5.5, c.neutron, f); }
    }
    g.label(`caught by a peak on the way down: ${sd.down} · reached thermal: ${sd.reached}`, W * 0.5, H * 0.86, { color: c.ink, size: fs + 1, weight: 600, serif: true });
    g.label("each hop: one bounce, the same fraction of energy lost", W * 0.5, H * 0.92, { color: c.soft, size: fs, serif: true, italic: true });
  }

  // ---------- scene: one row per ladder ----------
  function addRow(S, instant) {
    const D0 = S.target.D0 ?? S.D0, S0 = (S.target.S0 ?? S.S0) * 1e-4, Gg = (S.target.Gg ?? S.Gg) * 1e-3, k = ens.k++;
    const lad = ladder(makeDraws(1000 + k * 7, Math.ceil(450 / D0) + 4, Math.ceil(300 / (D0 * D_P32)) + 4), D0, S0, Gg, 1);
    let best = null, bc = -1; for (const r of lad) { const v = sigma([r], ETH); if (v > bc) { bc = v; best = r; } }
    const th = sigma(lad, ETH), trees = lad.filter((r) => r.er > -25 && r.er < 70).map((r) => ({ er: r.er, l: r.l, pk: r.er > 0 ? sigma([r], r.er) : 0, w: r.gnr / (S0 * D0) }));
    ens.rows.unshift({ trees, th, best: best.er, t0: instant ? -99 : S.time, done: !!instant, y: instant ? null : -1 });
    if (instant) ens.pile.push(th);
    ens.ri.push(resInt(lad));
    if (ens.rows.length > 24) ens.rows.pop();
    if (ens.pile.length > 200) { ens.pile.shift(); ens.ri.shift(); }
  }
  function sceneEnsemble(g, S, dt) {
    const { W, H, c } = g, phone = W < 600, fs = phone ? 10.5 : 13, NR = phone ? 11 : 18;
    const rx0 = W * 0.04, rx1 = W * (phone ? 0.52 : 0.58), top = H * 0.1, rh = (H * 0.8 - top) / NR, eLo = -25, eHi = 70;
    const X = (e) => rx0 + (rx1 - rx0) * (e - eLo) / (eHi - eLo), xt = X(ETH), dX = W * (phone ? 0.66 : 0.65);
    const px0 = W * (phone ? 0.74 : 0.72), px1 = W * 0.97, pY = H * (phone ? 0.8 : 0.86), LO = 0.1, HI = 1000, NB = 16, bw = (px1 - px0) / NB, dr = clamp(bw / 4.6, 1.3, 3), pitch = 2 * dr + 0.6;
    const PX = (v) => px0 + (px1 - px0) * Math.log(clamp(v, LO, HI * 0.999) / LO) / Math.log(HI / LO), binOf = (v) => clamp(Math.floor((PX(v) - px0) / bw), 0, NB - 1);
    ens.qT += dt; ens.auto += dt;
    if (ens.queue > 0 && ens.qT > 0.3) { addRow(S); ens.queue--; ens.qT = 0; ens.auto = 0; }
    else if (ens.auto > 3.2 && ens.pile.length < 40) { addRow(S); ens.auto = 0; }
    const a = 1 - Math.exp(-7 * dt), rd = (v) => clamp(1.6 + 3.3 * Math.sqrt(v / 10), 1.5, rh * 1.3);
    g.label("−20", X(-20), top - 14, { color: c.faint, size: fs - 2 }); g.label("0 eV", xt, top - 14, { color: c.faint, size: fs - 2 }); g.label("+60 eV", X(60), top - 14, { color: c.faint, size: fs - 2 });
    ens.rows.forEach((row, i) => {
      if (i >= NR) return;
      const ty = top + (i + 0.78) * rh; if (row.y === null) row.y = ty; row.y += (ty - row.y) * a;
      const y = row.y, age = S.time - row.t0, fin = smooth(0, 0.4, age), al = fin * (i > NR - 3 ? 1 - (i - (NR - 3)) / 3 : 1);
      if (al <= 0.01) return;
      g.line(rx0, y, rx1, y, c.line, 1, al);
      for (const t of row.trees) {
        const x = X(t.er);
        if (t.er > 0) peak(g, x, y, rh * 0.82 * clamp(log10(Math.max(t.pk, 1)) / 4.6, 0.06, 1), 5, { hollow: t.l === 1, alpha: al });
        else if (t.l === 0) peak(g, x, y, rh * 0.35 * clamp(Math.sqrt(t.w), 0.3, 1.4), 5, { down: true, alpha: 0.45 * al });
      }
      // bracket to the peak that sets the thermal value
      const xb = X(row.best), by = y + rh * 0.12;
      g.line(xt, by, xb, by, c.ink, 1, 0.55 * al); g.line(xb, by - 3, xb, by + 3, c.ink, 1, 0.55 * al);
      g.label(`${Math.abs(row.best).toFixed(1)} eV`, rx1 + 4, y - 4, { color: c.soft, size: fs - 3, alpha: al, align: "left" });
      const ball = smooth(0.4, 0.8, age); g.ball(xt + Math.sin(S.time * 6 + i) * 1.2, lerp(y - rh, y - 4, ball), 3.6, c.neutron, al);
      const grow = smooth(0.8, 1.2, age), r = rd(row.th) * grow;
      g.line(xt, y - 4, dX, y - 4, c.neutron, 1, 0.12 * al, [2, 3]);
      g.dot(dX, y - 4, r, c.neutron, 0.22 * al); g.ring(dX, y - 4, r, c.neutron, 1, 0.7 * al);
      if (!row.done && age > 1.2) { const f = smooth(1.2, 1.8, age), b = binOf(row.th); g.dot(lerp(dX, px0 + (b + 0.5) * bw, f), lerp(y, pY - 10, f) - Math.sin(Math.PI * f) * 30, dr + 1, c.neutron); if (age > 1.8) { row.done = true; ens.pile.push(row.th); } }
    });
    g.label("thermal neutron", xt, top + NR * rh + 12, { color: c.neutron, size: fs - 1 });
    g.label(phone ? "σ disc" : "disc area = σ at 0.025 eV", dX, top - 14, { color: c.soft, size: fs - 2 });
    // pile
    const cnt = new Array(NB).fill(0);
    for (const v of ens.pile) { const b = binOf(v), k = cnt[b]++; g.dot(px0 + (b + 0.5) * bw + ((k % 2) - 0.5) * (2 * dr + 0.4), pY - dr - 1 - Math.floor(k / 2) * pitch, dr, c.neutron, 0.85); }
    g.line(px0 - 3, pY, px1 + 3, pY, c.line, 1);
    (phone ? [1, 10, 100] : [1, 10, 100, 1000]).forEach((v) => g.label(v >= 1000 ? "1k" : String(v), clamp(PX(v), px0, px1 - 6), pY + 12, { color: c.faint, size: fs - 2 }));
    g.label(phone ? "thermal σ (b)" : "thermal σ, barns", (px0 + px1) / 2, pY + 28, { color: c.soft, size: fs - 1 });
    const so = [...ens.pile].sort((p, q) => p - q), n = so.length;
    if (n > 5) {
      const med = so[n >> 1], q1 = so[Math.floor(n * 0.16)], q3 = so[Math.floor(n * 0.84)], ri = [...ens.ri].sort((p, q) => p - q), m = ri.length, rs = ri[Math.floor(m * 0.84)] / ri[Math.floor(m * 0.16)];
      g.line(PX(med), pY + 2, PX(med), pY - 10, c.ink, 2);
      g.label(phone ? `${n} ladders · thermal ×${(q3 / q1).toFixed(0)} · res. integral ×${rs.toFixed(1)}` : `${n} ladders · thermal σ median ${fmtB(med)}, middle two thirds ×${(q3 / q1).toFixed(0)} · resonance integral only ×${rs.toFixed(1)}`, W * 0.5, H * 0.95, { color: c.ink, size: fs + 1, weight: 600, serif: true });
    }
  }
})();
