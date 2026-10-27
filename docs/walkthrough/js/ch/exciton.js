/* Chapter 20 (Expert): the exciton model in numbers (preeq/exciton.py, density/particle_hole.py, preeq/multi.py).
 * Scenes (S.mode): "omega"  = particle-hole state densities omega(p, h, E) with and without the Pauli correction; a Fermi-sea
 *                              sketch resamples one configuration of the chosen exciton number;
 *                   "rates"  = per stage n: the internal transition rate lambda+ and the neutron emission rate W, log scale;
 *                   "master" = the never-come-back master equation in time: populations P(n, t) flow down the chain, the
 *                              emitted share accumulates; a clock in 10^-22 s;
 *                   "spec"   = the neutron spectrum by stage (3, 5, 7, ...) plus evaporation, log scale;
 *                   "frac"   = the pre-equilibrium share of the emission against incident energy, for the matrix-element constant;
 *                   "multi"  = a toy estimate of a second fast emission from the residual's leftover excitons (multiple PE).
 * Formulas, one-component for clarity (the engine is two-component, protons and neutrons apart): Williams densities with
 * TALYS's Pauli term A(p,h) = max(p,h)^2/g - (p^2 + h^2 + p + h)/(4g), g = A/15; M^2 = C1 A_p / A^3 (7.48 + 4.62e5 / (E/(n A_p)
 * + 10.7)^3) MeV^2 (Koning-Duijvestijn, matrix.f90); lambda+ = (2 pi/hbar) M^2 g^3 (E - A(p+1,h+1))^(n+1) / (2 (n+1) (E - A(p,h))^(n-1));
 * W(p,h,eps) = (2s+1) mu eps sigma_inv(eps) / (pi^2 hbar^3) omega(p-1,h,U) / omega(p,h,E). Illustrative: n + an iron-56-like target
 * (compound A = 57, S_n = 7.65 MeV), a schematic inverse cross section, sigma_CN = 1.3 b, 85 % of the evaporation as neutrons. */
(function () {
  const { TAU, clamp, lerp, smooth, rng } = WT.util;
  const log10 = (x) => Math.log(x) / Math.LN10;
  const A = 57, G = A / 15, SN = 7.646, HBAR = 6.582e-22, HC2 = 38938, MU = 939.565 * 56 / 57, R = 1.25 * Math.cbrt(56), SIGCN = 1300, BN = 0.85;
  const fact = (n) => { let f = 1; for (let i = 2; i <= n; i++) f *= i; return f; };
  const pauli = (p, h, on) => (on ? Math.max(p, h) ** 2 / G - (p * p + h * h + p + h) / (4 * G) : 0);
  function omega(p, h, E, on = true) { const n = p + h, a = pauli(p, h, on); if (n === 0) return 0; if (E <= a) return 0; return Math.pow(G, n) * Math.pow(E - a, n - 1) / (fact(p) * fact(h) * fact(n - 1)); }
  const M2 = (E, n, c1) => c1 / (A * A * A) * (7.48 + 4.62e5 / Math.pow(E / n + 10.7, 3));
  function lamPlus(p, h, E, c1, on = true) { const n = p + h, a0 = pauli(p, h, on), a1 = pauli(p + 1, h + 1, on); if (E <= a1) return 0; return TAU / HBAR * M2(E, n, c1) * G ** 3 * Math.pow(E - a1, n + 1) / (2 * (n + 1) * Math.pow(E - a0, n - 1)); }
  const sigInv = (e) => Math.PI * (R + 4.55 / Math.sqrt(Math.max(e, 1e-3))) ** 2 * (1 - Math.exp(-2 * Math.sqrt(Math.max(e, 0))));   // fm^2
  const PRE = 2 * MU / (Math.PI * Math.PI * HC2 * HBAR);
  /** neutron emission rate (s^-1 MeV^-1) from (p, h) at total energy E into channel energy e */
  function Wn(p, h, E, e, on = true) { const U = E - SN - e; if (U <= 0 || p < 1) return 0; const w0 = omega(p, h, E, on); if (!w0) return 0; return PRE * e * sigInv(e) * omega(p - 1, h, U, on) / w0; }
  const NE = 90;
  /** the never-come-back chain from (1,0) at incident energy Ein: per stage n = 3, 5, ... (p <= 6): P, tau, lambda+, W, spectrum */
  function chain(Ein, c1 = 1, on = true) {
    const E = Ein + SN, emax = E - SN, de = emax / NE, st = []; let P = 1;
    // the first collision: (1,0) -> (2,1) always (emission from (1,0) is the elastic channel, handled by the optical model)
    for (let p = 2; p <= 6; p++) {
      const h = p - 1, n = p + h, lp = lamPlus(p, h, E, c1, on); let Wt = 0; const sp = new Float64Array(NE);
      for (let i = 0; i < NE; i++) { const e = (i + 0.5) * de, w = Wn(p, h, E, e, on); sp[i] = w; Wt += w * de; }
      const tau = 1 / (lp + Wt); st.push({ p, h, n, P, tau, lp, W: Wt, sp, emit: P * Wt * tau });
      P = P * lp * tau;
    }
    const emitted = st.reduce((s, q) => s + q.emit, 0);
    // evaporation: Weisskopf-Ewing shape e sigma_inv rho(U), rho ~ exp(2 sqrt(aU)), normalised to the flux left
    const ev = new Float64Array(NE); let evs = 0; for (let i = 0; i < NE; i++) { const e = (i + 0.5) * de, U = Math.max(emax - e - 1.5, 0); ev[i] = e * sigInv(e) * Math.exp(2 * Math.sqrt(7.5 * U)); evs += ev[i] * de; }
    const left = 1 - emitted; for (let i = 0; i < NE; i++) ev[i] *= SIGCN * left * BN / evs;
    return { E, emax, de, st, emitted, left, ev };
  }
  /** toy multiple pre-equilibrium: after a primary emission from (2,1) the residual keeps (1,1) at U; chance it emits again first */
  function secondChance(Ein, c1 = 1) {
    const C = chain(Ein, c1), s = C.st[0]; let num = 0, den = 0;
    for (let i = 0; i < NE; i++) { const e = (i + 0.5) * C.de, w = s.sp[i]; if (!w) continue; const U = C.E - SN - e; let W2 = 0; for (let k = 0; k < 40; k++) { const e2 = (k + 0.5) * Math.max(U - SN, 0) / 40; W2 += Wn(1, 1, U, e2) * Math.max(U - SN, 0) / 40; } const l2 = lamPlus(1, 1, U, c1); den += w; num += w * (W2 / (W2 + l2 + 1e-30)); }
    return den ? num / den : 0;
  }
  const SHOT = /[?&]shot=/.test(location.search);
  const sup = (n) => String(n).replace(/[-0-9]/g, (ch) => "⁻⁰¹²³⁴⁵⁶⁷⁸⁹"["-0123456789".indexOf(ch)]);

  Object.assign(WT.glossary || (WT.glossary = {}), {
    neverComeBack: {
      term: "Never-come-back approximation", aliases: ["never-come-back approximation", "never-come-back"],
      short: "The approximation that, early in the equilibration, collisions only add particle–hole pairs and never remove them.",
      more: "It turns the master equation into a simple chain that can be integrated stage by stage. It holds while the exciton number is far below its equilibrium value, which is where pre-equilibrium emission happens.",
      chapter: "exciton",
    },
  });

  WT.chapter("exciton", {
    num: "Chapter 20", title: "The exciton model, in numbers", short: "Exciton model",
    lead: "Chapter 4 followed one fast neutron through a few collisions. Here are the rates that decide, at each stage, whether the next thing is another collision or an escape, and the spectrum they add up to.",
    html: `
<div class="step">
  <h3>Counting particle–hole states</h3>
  <p>The exciton model classifies the nucleus on its way to equilibrium by its number of excited particles <i>p</i> and holes <i>h</i>, <i>n</i> = <i>p</i> + <i>h</i>. A neutron entering a target starts at <i>p</i> = 1, <i>h</i> = 0; each collision adds a pair. What matters at each stage is how many ways the energy can be shared among the <i>n</i> excitons: the particle–hole state density.</p>
  <div class="formula">ω(p,h,E) = g<sup>n</sup> (E − A<sub>p,h</sub>)<sup>n−1</sup> / (p! h! (n−1)!) ,  A<sub>p,h</sub> = max(p,h)²/g − (p² + h² + p + h)/4g</div>
  <div class="ctl"><label for="ex-n">Particles p (holes p − 1)</label><input id="ex-n" type="range" data-bind="pp" min="2" max="6" step="1" value="3" data-instant><output data-show="pp" data-fmt="0"></output></div>
  <div class="btns"><button class="btn ghost" data-act="pauli" aria-pressed="true">Pauli correction</button></div>
  <p><i>g</i> ≈ <i>A</i>/15 MeV⁻¹ is the density of single-particle levels near the Fermi energy. <i>A<sub>p,h</sub></i> is the <b>Pauli</b> correction: two particles cannot share a level, so the lowest configurations cost energy and the density near the threshold drops. The sketch shows one configuration at a time with the chosen <i>p</i>, drawn at random.</p>
</div>
<div class="step">
  <h3>Going deeper or getting out</h3>
  <p>From each stage two things can happen. A collision creates another pair, at the rate λ<sup>+</sup>, which by Fermi's golden rule is the squared matrix element times the density of states it can reach. Or a particle leaves, at the rate <i>W</i>, given by detailed balance from the inverse cross section and the ratio of state densities with and without the escaping particle.</p>
  <div class="formula">λ<sup>+</sup>(n) = (2π/ħ) M² ω<sub>acc</sub> ,  W(p,h,ε) = (2s+1)/(π²ħ³) με σ<sub>inv</sub>(ε) ω(p−1,h,U) / ω(p,h,E)</div>
  <div class="ctl"><label for="ex-e">Neutron energy (MeV)</label><input id="ex-e" type="range" data-bind="Ein" min="5" max="60" step="0.5" value="20"><output data-show="Ein" data-fmt="1"></output></div>
  <p>The bars are the two rates at each stage, on a log scale: λ<sup>+</sup> of order 10²² s⁻¹, <i>W</i> about a tenth of it at the first stage and falling with every stage, since each new pair thins the energy the leading particle can carry. The engine takes M² from the Koning–Duijvestijn form, which falls with the energy per exciton:</p>
  <div class="formula">M² = (C₁ A<sub>p</sub> / A³) · [7.48 + 4.62×10⁵ / (E/(n A<sub>p</sub>) + 10.7)³]  MeV²</div>
</div>
<div class="step">
  <h3>The chain in time</h3>
  <p>Ignoring the rare collisions that remove a pair (the never-come-back approximation), the populations obey a simple chain: each stage fills from the one before and empties into the next and into the continuum. The bars run that master equation; time is in units of 10⁻²² s.</p>
  <div class="formula">dP(n)/dt = λ<sup>+</sup>(n−2) P(n−2) − [λ<sup>+</sup>(n) + W(n)] P(n)</div>
  <div class="ctl"><label for="ex-e2">Neutron energy (MeV)</label><input id="ex-e2" type="range" data-bind="Ein" min="5" max="60" step="0.5" value="20"><output data-show="Ein" data-fmt="1"></output></div>
  <p>The whole chain is over in a few 10⁻²² s. The share that escapes on the way is the pre-equilibrium emission; the rest, after at most six particles in the engine, as in TALYS, is handed to the compound nucleus. Time integration gives each stage a strength τ(<i>n</i>)·<i>P</i>(<i>n</i>), and that product is what the engine computes.</p>
</div>
<div class="step">
  <h3>Where the hard tail comes from</h3>
  <p>The emission spectrum is the sum over stages of population times lifetime times emission rate, then the evaporation of what is left. Stage <i>n</i> = 3 alone, two particles and a hole, reaches the highest outgoing energies: its spectrum falls only linearly toward the end point. Each later stage is softer.</p>
  <div class="formula">dσ/dε = σ<sub>CN</sub> Σ<sub>n</sub> P(n) τ(n) W(n,ε) + evaporation</div>
  <div class="ctl"><label for="ex-e3">Neutron energy (MeV)</label><input id="ex-e3" type="range" data-bind="Ein" min="5" max="60" step="0.5" value="20"><output data-show="Ein" data-fmt="1"></output></div>
  <p>Raise the energy and the spectrum hardens: the pre-equilibrium tail stretches to the end point while the evaporation hump stays at 1 to 2 MeV. Above about 10 MeV the measured high-energy neutrons can only be reproduced with this tail.</p>
</div>
<div class="step">
  <h3>How large a share</h3>
  <p>The share of the emission that is pre-equilibrium grows with incident energy, from a few per cent near 5 MeV to about 40 per cent at 40 MeV here. It depends on one adjustable constant, the overall size of the matrix element: a weaker interaction means slower equilibration and more early emission.</p>
  <div class="ctl"><label for="ex-c">Matrix-element constant C₁</label><input id="ex-c" type="range" data-bind="c1" min="0.3" max="3" step="0.05" value="1"><output data-show="c1" data-fmt="2"></output></div>
  <p>The dashed curve is C₁ = 1, the engine's default; the solid one follows the slider. Halving C₁ raises the share by a factor of 1.5 to 1.9, not 2: the escape probability of each stage is W/(λ<sup>+</sup> + W), not W/λ<sup>+</sup>, and fewer nuclei survive to the later stages.</p>
</div>
<div class="step">
  <h3>Two components, and a second escape</h3>
  <p>The engine follows protons and neutrons separately (<i>p</i><sub>π</sub>, <i>h</i><sub>π</sub>, <i>p</i><sub>ν</sub>, <i>h</i><sub>ν</sub>), with different matrix elements for like and unlike pairs, a reduced well depth for the first collision near the surface, and Kalbach's rules for clusters. Above 20 MeV it also lets the residual nucleus, which still holds excitons, emit a second fast particle before it equilibrates.</p>
  <div class="ctl"><label for="ex-e4">Neutron energy (MeV)</label><input id="ex-e4" type="range" data-bind="Ein" min="5" max="60" step="0.5" value="20"><output data-show="Ein" data-fmt="1"></output></div>
  <p>The curve is a toy version of that: after a first emission from the three-exciton stage, the chance that the residual's leftover particle escapes before its next collision. It stays small below 20 MeV and grows above, which is where the engine switches multiple pre-equilibrium on.</p>
  <div class="aside">In the code: <code>density/particle_hole.py</code> (Williams densities, Pauli and finite-well corrections, one and two components), <code>preeq/exciton.py</code> (matrix elements, emission and transition rates, lifetimes, the never-come-back solution), <code>preeq/complex.py</code> (Kalbach pickup, stripping and knockout), <code>preeq/multi.py</code> (multiple pre-equilibrium, from 20 MeV by default). The picture is one-component with a schematic inverse cross section, for an iron-56-like target.</div>
</div>`,
    setup(S) {
      S.set("mode", "omega"); S.to("pp", 3, true); S.to("Ein", 20, true); S.to("c1", 1, true); S.to("pauliOn", 1, true);
      S.cfg = null; S.cfgT = 0; S.t0 = 0;
      const press = (on) => document.querySelectorAll('#exciton [data-act="pauli"]').forEach((b) => b.setAttribute("aria-pressed", String(on)));
      S.on("pauli", () => { const on = S.target.pauliOn < 0.5; S.to("pauliOn", on ? 1 : 0); press(on); });
    },
    steps: [
      (S) => { S.set("mode", "omega"); },
      (S) => { S.set("mode", "rates"); },
      (S) => { S.set("mode", "master"); S.t0 = S.time - (SHOT ? 2.2 : 0); },
      (S) => { S.set("mode", "spec"); },
      (S) => { S.set("mode", "frac"); },
      (S) => { S.set("mode", "multi"); S.to("Ein", 30); },
    ],
    frame(g, S, dt) {
      if (S.mode === "omega") drawOmega(g, S, dt);
      else if (S.mode === "rates") drawRates(g, S);
      else if (S.mode === "master") drawMaster(g, S, dt);
      else if (S.mode === "spec") drawSpec(g, S);
      else if (S.mode === "frac") drawFrac(g, S, dt);
      else drawMulti(g, S, dt);
    },
  });
  WT.mods.exciton.calc = { omega, lamPlus, Wn, chain, secondChance, M2 };
  const chainOf = (S, Ein, c1) => { const k = `${Ein.toFixed(2)}|${(c1 ?? 1).toFixed(3)}`; if (!S.ch || S.ch.k !== k) S.ch = { k, C: chain(Ein, c1 ?? 1) }; return S.ch.C; };
  const COL = (c, i) => [c.neutron, c.accent, c.alpha, c.cool, c.fission][i % 5];

  // ---------- scene 1: state densities and one configuration ----------
  function drawOmega(g, S, dt) {
    const { W, H, c } = g, phone = W < 600, pSel = Math.round(S.pp), on = S.pauliOn;
    const x0 = W * (phone ? 0.14 : 0.1), x1 = W * (phone ? 0.95 : 0.62), yT = H * 0.1, yB = H * (phone ? 0.5 : 0.82), Emax = 40, X = (e) => lerp(x0, x1, e / Emax), Y = (v) => lerp(yB, yT, (log10(Math.max(v, 1e-3)) + 1) / 11);
    for (let d = 0; d <= 10; d += 2) { const y = lerp(yB, yT, (d + 1) / 11); g.line(x0, y, x1, y, c.line, 1, 0.8); g.label(d === 0 ? "1" : `10${sup(d)}`, x0 - 6, y, { color: c.faint, size: 10, align: "right" }); }
    for (let e = 0; e <= Emax; e += 10) g.label(`${e}`, X(e), yB + 12, { color: c.faint, size: 10 });
    g.label("E (MeV)", x1, yB + 26, { color: c.faint, size: 10, align: "right" });
    g.label("ω(p, h, E) per MeV", x0, yT - 14, { color: c.ink, size: 12, weight: 600, align: "left" });
    g.clip(x0 - 2, yT - 4, x1 - x0 + 4, yB - yT + 6);
    for (let p = 2; p <= 6; p++) {
      const h = p - 1, sel = p === pSel, pts = [], ghost = [];
      for (let i = 0; i <= 200; i++) { const e = Emax * i / 200, v1 = omega(p, h, e, true), v0 = omega(p, h, e, false), v = lerp(v0, v1, on); if (v > 1e-3) pts.push([X(e), Y(v)]); if (v0 > 1e-3) ghost.push([X(e), Y(v0)]); }
      if (sel && on > 0.5) g.poly(ghost, COL(c, p), 1.2, 0.6, [4, 4]);
      g.poly(pts, COL(c, p), sel ? 3 : 1.4, sel ? 1 : 0.55);
      const lab = pts[Math.floor(pts.length * 0.82)]; if (lab) g.label(`${p}p${h}h`, lab[0], lab[1] - 12, { color: COL(c, p), size: sel ? 12 : 10, weight: sel ? 600 : 500, bg: sel });
    }
    g.restore();
    if (on > 0.5) g.label("dashed: no Pauli correction", x1, yB - 14, { color: c.soft, size: 11, align: "right", bg: true });
    // a Fermi sea with one random configuration of pSel particles and pSel - 1 holes, resampled every 0.6 s
    const fx = phone ? W * 0.5 : W * 0.82, fy = phone ? H * 0.8 : H * 0.5, rungs = 14, dy = (phone ? H * 0.019 : H * 0.045), hw = phone ? W * 0.32 : W * 0.12;
    S.cfgT += dt; if (!S.cfg || S.cfg.p !== pSel || S.cfgT > 0.6) {
      S.cfgT = 0; const r = Math.random, used = new Set(), pick = (lo, hi) => { let k; do { k = lo + Math.floor(r() * (hi - lo)); } while (used.has(k)); used.add(k); return k; };
      const parts = [], holes = []; for (let i = 0; i < pSel; i++) parts.push(pick(0, 7)); for (let i = 0; i < pSel - 1; i++) holes.push(pick(-7, 0));
      S.cfg = { p: pSel, parts, holes };
    }
    for (let k = -7; k < 7; k++) { const y = fy - (k + 0.5) * dy; g.line(fx - hw, y, fx + hw, y, c.soft, 1, 0.5); }
    g.line(fx - hw - 8, fy, fx + hw + 8, fy, c.warm, 1.6, 0.8, [5, 4]); g.label("Fermi level", fx + hw + 10, fy, { color: c.warm, size: 11, align: phone ? "right" : "left" });
    for (let k = -7; k < 0; k++) { if (S.cfg.holes.includes(k)) { g.ring(fx, fy - (k + 0.5) * dy, dy * 0.32, c.neutron, 1.6); continue; } g.dot(fx - hw * 0.4, fy - (k + 0.5) * dy, dy * 0.26, c.neutron, 0.7); g.dot(fx + hw * 0.4, fy - (k + 0.5) * dy, dy * 0.26, c.neutron, 0.7); g.dot(fx, fy - (k + 0.5) * dy, dy * 0.26, c.neutron, 0.7); }
    for (const k of S.cfg.parts) { const y = fy - (k + 0.5) * dy; g.glow(fx, y, dy * 0.8, c.warm, 0.4); g.ball(fx, y, dy * 0.3, c.neutron); }
    g.label(`${pSel} particles, ${pSel - 1} holes`, fx, fy - 7.5 * dy - 14, { color: c.ink, size: 12, weight: 600, bg: true });
  }

  // ---------- scene 2: rates per stage ----------
  function drawRates(g, S) {
    const { W, H, c } = g, phone = W < 600, C = chainOf(S, S.Ein);
    const x0 = W * (phone ? 0.14 : 0.12), x1 = W * 0.95, yT = H * 0.12, yB = H * (phone ? 0.74 : 0.78), Y = (v) => lerp(yB, yT, (log10(Math.max(v, 1e17)) - 17) / 6);
    for (let d = 17; d <= 23; d++) { const y = Y(Math.pow(10, d)); g.line(x0, y, x1, y, c.line, 1, 0.8); g.label(`10${sup(d)}`, x0 - 6, y, { color: c.faint, size: 10, align: "right" }); }
    g.label("rate (s⁻¹)", x0, yT - 14, { color: c.ink, size: 12, weight: 600, align: "left" });
    const n = C.st.length, slot = (x1 - x0) / n, bw = slot * 0.28;
    C.st.forEach((q, i) => {
      const xc = x0 + (i + 0.5) * slot;
      const bar = (x, v, col) => { const y = Y(v), ctx = g.ctx; ctx.save(); const gr = ctx.createLinearGradient(0, y, 0, yB); gr.addColorStop(0, g.rgba(col, 0.95)); gr.addColorStop(1, g.rgba(col, 0.35)); ctx.fillStyle = gr; ctx.fillRect(x, y, bw, yB - y); ctx.restore(); };
      bar(xc - bw - 2, q.lp, c.neutron); bar(xc + 2, q.W, c.photon);
      g.label(`n = ${q.n}`, xc, yB + 13, { color: c.ink, size: 12, weight: 600 });
      g.label(`${q.p}p${q.h}h`, xc, yB + 28, { color: c.faint, size: 10 });
      if (!phone || i % 2 === 0) g.label(`W/λ⁺ = ${(q.W / q.lp).toFixed(q.W / q.lp < 0.01 ? 4 : 3)}`, xc, Y(q.lp) - 12, { color: c.ink, size: 10, bg: true });
    });
    // a pulse runs down the chain; at each stage a share W/(λ⁺ + W) of it sparks away as a neutron
    { const ph = (((S.time * 0.4) % 1) + 1) % 1, fi = ph * n, i = Math.min(n - 1, Math.floor(fi)), f = fi - i, q = C.st[i];
      const xa = x0 + (i + 0.5) * slot, xb = x0 + (Math.min(n - 1, i + 1) + 0.5) * slot, xp = lerp(xa, xb, smooth(0.4, 1, f)), yp = yB - 10;
      g.glow(xp, yp, 16, c.neutron, 0.55); g.dot(xp, yp, 4, c.neutron);
      const sp = q.W / (q.lp + q.W); if (f < 0.4) { const u = f / 0.4; g.dot(xa + u * slot * 0.3, Y(q.W) - u * 40, 3.2, c.photon, (1 - u) * clamp(sp * 6, 0.15, 1)); } }
    g.label("blue: λ⁺, the next collision · yellow: W, neutron escape", W / 2, H * (phone ? 0.88 : 0.9), { color: c.soft, size: 12, bg: true });
    g.label(`E = ${S.Ein.toFixed(1)} + Sₙ = ${C.E.toFixed(1)} MeV · τ(n=3) = ${(C.st[0].tau / 1e-22).toFixed(2)} × 10⁻²² s`, W / 2, H * (phone ? 0.94 : 0.95), { color: c.ink, size: phone ? 11 : 13, weight: 600, bg: true });
  }

  // ---------- scene 3: the master equation in time ----------
  function drawMaster(g, S, dt) {
    const { W, H, c } = g, phone = W < 600, C = chainOf(S, S.Ein), st = C.st;
    if (S.mk !== C) { S.mk = C; S.t0 = S.time; }
    // integrate from t = 0 to the current (looping) time, in 1e-24 s steps (exact enough for the picture)
    const tScale = 1e-22, period = 6, tNow = Math.max(0, ((S.time - S.t0) % period) / period) * 8 * tScale, NS = 240, h = tNow / NS;
    const P = new Float64Array(st.length + 1), out = new Float64Array(st.length); P[0] = 1;
    for (let k = 0; k < NS; k++) { const d = new Float64Array(st.length + 1); for (let i = 0; i < st.length; i++) { const loss = (st[i].lp + st[i].W) * P[i] * h; d[i] -= loss; d[i + 1] += st[i].lp * P[i] * h; out[i] += st[i].W * P[i] * h; } for (let i = 0; i <= st.length; i++) P[i] = Math.max(0, P[i] + d[i]); }
    const x0 = W * 0.1, x1 = W * 0.95, yT = H * 0.16, yB = H * (phone ? 0.62 : 0.64), n = st.length + 1, slot = (x1 - x0) / n, bw = slot * 0.5;
    g.line(x0, yB, x1, yB, c.soft, 1.2, 0.8);
    for (let i = 0; i < n; i++) {
      const xc = x0 + (i + 0.5) * slot, v = P[i], hgt = (yB - yT) * v, col = i < st.length ? COL(c, i + 2) : c.warm;
      g.ctx.save(); g.ctx.fillStyle = g.rgba(col, 0.85); g.ctx.fillRect(xc - bw / 2, yB - hgt, bw, hgt); g.ctx.restore();
      g.label(i < st.length ? `n = ${st[i].n}` : "compound", xc, yB + 13, { color: c.ink, size: phone ? 10 : 12, weight: 600 });
      if (v > 0.02) g.label(`${(100 * v).toFixed(0)} %`, xc, yB - hgt - 10, { color: c.soft, size: 10 });
      // arrows of flow between stages
      if (i < st.length && v > 0.01) { const a = clamp(v * 3, 0.15, 1); g.arrow(xc + bw / 2 + 2, yB - 20, xc + slot - bw / 2 - 4, yB - 20, col, 1.6, a, 7); }
    }
    // the emitted share
    const em = out.reduce((s, v) => s + v, 0), ey = H * (phone ? 0.78 : 0.8), ew = (x1 - x0);
    g.ctx.save(); g.ctx.fillStyle = g.rgba(c.line, 0.8); g.ctx.fillRect(x0, ey, ew, 12); g.ctx.fillStyle = g.rgba(c.photon, 0.9); g.ctx.fillRect(x0, ey, ew * em / Math.max(C.emitted, 1e-9) * C.emitted, 12); g.ctx.restore();
    g.label(`emitted before equilibrium: ${(100 * em).toFixed(1)} % (of ${(100 * C.emitted).toFixed(1)} % in the end)`, x0, ey - 12, { color: c.photon, size: 12, weight: 600, align: "left" });
    g.label(`t = ${(tNow / tScale).toFixed(2)} × 10⁻²² s`, W / 2, H * 0.08, { color: c.ink, size: phone ? 14 : 16, weight: 600, serif: true, bg: true });
    // escaping neutrons from the bars, rate ~ W P
    if (!S.esc) S.esc = []; for (let i = 0; i < st.length; i++) if (Math.random() < st[i].W * P[i] * dt * 5e-21) S.esc.push({ x: x0 + (i + 0.5) * slot, y: yB - (yB - yT) * P[i], t0: S.time });
    for (let k = S.esc.length - 1; k >= 0; k--) { const q = S.esc[k], u = (S.time - q.t0) / 1; if (u > 1) { S.esc.splice(k, 1); continue; } g.ball(q.x + u * 20, q.y - u * H * 0.12, 4, c.neutron, 1 - u); }
  }

  // ---------- scene 4: the spectrum by stage ----------
  function drawSpec(g, S) {
    const { W, H, c } = g, phone = W < 600, C = chainOf(S, S.Ein);
    const x0 = W * (phone ? 0.14 : 0.12), x1 = W * 0.95, yT = H * 0.1, yB = H * (phone ? 0.78 : 0.8), X = (e) => lerp(x0, x1, e / C.emax), Y = (v) => lerp(yB, yT, (log10(Math.max(v, 1e-3)) + 2) / 5);
    for (let d = -2; d <= 3; d++) { const y = Y(Math.pow(10, d)); g.line(x0, y, x1, y, c.line, 1, 0.8); g.label(d === 0 ? "1" : `10${sup(d)}`, x0 - 6, y, { color: c.faint, size: 10, align: "right" }); }
    const step = C.emax > 30 ? 10 : 5; for (let e = 0; e <= C.emax; e += step) g.label(`${e}`, X(e), yB + 12, { color: c.faint, size: 10 });
    g.label("outgoing neutron energy ε (MeV)", x1, yB + 26, { color: c.faint, size: 10, align: "right" });
    g.label("dσ/dε (mb/MeV)", x0, yT - 14, { color: c.ink, size: 12, weight: 600, align: "left" });
    const tot = new Float64Array(NE); for (let i = 0; i < NE; i++) tot[i] = C.ev[i];
    g.clip(x0 - 2, yT - 6, x1 - x0 + 4, yB - yT + 8);
    C.st.forEach((q, k) => { const pts = []; for (let i = 0; i < NE; i++) { const v = SIGCN * q.P * q.tau * q.sp[i]; tot[i] += v; if (v > 1e-3) pts.push([X((i + 0.5) * C.de), Y(v)]); } g.poly(pts, COL(c, k + 2), 1.6, 0.9, [5, 3]); if (pts.length > 4) { const p = pts[Math.floor(pts.length * (k === 0 ? 0.75 : 0.45))]; g.label(`n = ${q.n}`, p[0], p[1] - 12, { color: COL(c, k + 2), size: 11, bg: true }); } });
    const pe = []; for (let i = 0; i < NE; i++) if (C.ev[i] > 1e-3) pe.push([X((i + 0.5) * C.de), Y(C.ev[i])]); g.poly(pe, c.warm, 1.8, 0.9, [2, 3]);
    if (pe.length) g.label("evaporation", pe[Math.min(pe.length - 1, 6)][0] + 8, pe[Math.min(pe.length - 1, 6)][1] - 14, { color: c.warm, size: 11, align: "left", bg: true });
    const pt = []; for (let i = 0; i < NE; i++) pt.push([X((i + 0.5) * C.de), Y(tot[i])]);
    g.ground(pt, c.neutron, H * 0.12, 0.2); g.poly(pt, c.ink, 2.6);
    g.restore();
    // a marker sweeps the outgoing energy and reads the share of stage n = 3 in the total there
    { const u = (((S.time * 0.09) % 1) + 1) % 1, i = Math.min(NE - 1, Math.floor(u * NE)), e = (i + 0.5) * C.de, v3 = SIGCN * C.st[0].P * C.st[0].tau * C.st[0].sp[i], tt = tot[i];
      g.line(X(e), yT, X(e), yB, c.warm, 1, 0.45); g.glow(X(e), Y(tt), 14, c.ink, 0.35); g.dot(X(e), Y(tt), 4.5, c.ink);
      g.label(`ε = ${e.toFixed(1)} MeV: ${(100 * v3 / Math.max(tt, 1e-9)).toFixed(0)} % from n = 3`, X(e) + (u > 0.6 ? -8 : 8), Y(tt) - 16, { color: c.ink, size: 11, align: u > 0.6 ? "right" : "left", bg: true }); }
    g.label(`pre-equilibrium ${(100 * C.emitted).toFixed(0)} % of the emission · solid: total`, W / 2, H * (phone ? 0.9 : 0.92), { color: c.ink, size: phone ? 12 : 14, weight: 600, serif: true, bg: true });
  }

  // ---------- scene 5: the share against energy ----------
  function drawFrac(g, S, dt) {
    const { W, H, c } = g, phone = W < 600, c1 = S.c1;
    const x0 = W * (phone ? 0.14 : 0.12), x1 = W * 0.95, yT = H * 0.12, yB = H * (phone ? 0.76 : 0.8), X = (e) => lerp(x0, x1, (e - 5) / 55), Y = (f) => lerp(yB, yT, f);
    [0, 0.25, 0.5, 0.75, 1].forEach((f) => { g.line(x0, Y(f), x1, Y(f), c.line, 1, 0.8); g.label(`${(100 * f).toFixed(0)} %`, x0 - 6, Y(f), { color: c.faint, size: 10, align: "right" }); });
    [5, 20, 40, 60].forEach((e) => g.label(`${e} MeV`, X(e), yB + 12, { color: c.faint, size: 10 }));
    g.label("pre-equilibrium share of the emission", x0, yT - 14, { color: c.ink, size: 12, weight: 600, align: "left" });
    const key = c1.toFixed(3); if (!S.fr || S.fr.k !== key) { const a = [], b = []; for (let e = 5; e <= 60; e += 1.25) { a.push([X(e), Y(chain(e, c1).emitted)]); if (!S.fr0) b.push([X(e), Y(chain(e, 1).emitted)]); } S.fr = { k: key, a }; if (!S.fr0) S.fr0 = b; }
    g.poly(S.fr0, c.soft, 1.6, 0.9, [6, 5]); g.ground(S.fr.a, c.neutron, H * 0.1, 0.18); g.poly(S.fr.a, c.neutron, 2.8);
    const u = (((S.time * 0.08) % 1) + 1) % 1, e = 5 + 55 * u, f = chain(e, c1).emitted; g.glow(X(e), Y(f), 14, c.neutron, 0.6); g.dot(X(e), Y(f), 5, c.neutron);
    g.label(`${e.toFixed(0)} MeV: ${(100 * f).toFixed(0)} %`, X(e), Y(f) - 18, { color: c.neutron, size: 12, weight: 600, bg: true });
    g.label(`C₁ = ${c1.toFixed(2)} (dashed: 1)`, x1, yB - 14, { color: c.soft, size: 12, align: "right", bg: true });
  }

  // ---------- scene 6: a toy second escape ----------
  function drawMulti(g, S, dt) {
    const { W, H, c } = g, phone = W < 600;
    if (!S.mp) { const a = []; for (let e = 5; e <= 60; e += 2.5) a.push([e, secondChance(e)]); S.mp = a; }
    const x0 = W * (phone ? 0.14 : 0.12), x1 = W * 0.95, yT = H * 0.36, yB = H * (phone ? 0.8 : 0.82), mx = Math.max(...S.mp.map((p) => p[1])) * 1.15 || 1;
    const X = (e) => lerp(x0, x1, (e - 5) / 55), Y = (f) => lerp(yB, yT, f / mx);
    for (let k = 0; k <= 4; k++) { const f = mx * k / 4; g.line(x0, Y(f), x1, Y(f), c.line, 1, 0.8); g.label(`${(100 * f).toFixed(f * 100 < 10 ? 1 : 0)} %`, x0 - 6, Y(f), { color: c.faint, size: 10, align: "right" }); }
    [5, 20, 40, 60].forEach((e) => g.label(`${e} MeV`, X(e), yB + 12, { color: c.faint, size: 10 }));
    g.line(X(20), yT, X(20), yB, c.warm, 1.2, 0.7, [4, 4]); g.label("20 MeV: multiple pre-equilibrium on", X(20) + 6, yT + 10, { color: c.warm, size: 11, align: "left", bg: true });
    const pts = S.mp.map(([e, f]) => [X(e), Y(f)]); g.ground(pts, c.alpha, H * 0.1, 0.2); g.poly(pts, c.alpha, 2.6);
    g.label("chance of a second fast emission (toy estimate)", x0, yT - 14, { color: c.ink, size: 12, weight: 600, align: "left" });
    const E = clamp(S.Ein, 5, 60), f = secondChance(E); g.glow(X(E), Y(f), 14, c.alpha, 0.6); g.dot(X(E), Y(f), 5, c.alpha);
    g.label(`${E.toFixed(0)} MeV: ${(100 * f).toFixed(1)} %`, X(E), Y(f) - 18, { color: c.alpha, size: 12, weight: 600, bg: true });
    // the two-step picture above: residual with leftover excitons, a second neutron leaving
    const ty = H * 0.15, cx1 = W * 0.25, cx2 = W * 0.6, t = (((S.time % 3) + 3) % 3) / 3;
    g.glow(cx1, ty, 26, c.warm, 0.45); g.ball(cx1, ty, 9, c.warm); g.label("2p1h", cx1, ty + 24, { color: c.soft, size: 11 });
    g.glow(cx2, ty, 22, c.warm, 0.3); g.ball(cx2, ty, 8, c.warm); g.label("residual: 1p1h", cx2, ty + 24, { color: c.soft, size: 11 });
    const u1 = smooth(0, 0.45, t), u2 = smooth(0.5, 0.95, t);
    g.ball(lerp(cx1, cx2 - 30, u1), ty - 30 * Math.sin(Math.PI * u1), 5, c.neutron, 1 - smooth(0.4, 0.5, t));
    if (t > 0.5) g.ball(lerp(cx2, W * 0.92, u2), ty - 30 * Math.sin(Math.PI * u2), 5, c.neutron, 1 - smooth(0.9, 1, t));
    g.arrow(cx1 + 14, ty, cx2 - 14, ty, c.soft, 1.2, 0.6, 7);
  }
})();
