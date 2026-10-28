/* Catching a resonance: a time-of-flight transmission measurement of one resonance. Scene: a pulsed neutron source, a flight
 * path of length L, a sample of thickness d, a detector; below, the transmission the experiment records against energy.
 * Physics: the neutron's energy from its flight time, E = (72.3 L[m] / t[us])^2 eV. One isolated resonance (illustrative
 * heavy target, A = 238, E0 = 6.7 eV, Gn = 1.5 meV, Gg = 23.5 meV, g = 1, potential scattering 9 b), single-level shape with
 * peak 4 pi lambdabar^2 g Gn / G, Doppler-broadened by a Gaussian of width Delta = sqrt(4 E kT / A) (room temperature).
 * Transmission T = exp(-n sigma), n = 4.8e-6 atoms/b per um of a uranium-dense metal. Resolution: Gaussian in energy with
 * FWHM 2 E sqrt((dt/t)^2 + (dL/L)^2), dL = 2 cm, applied to the transmission (not to sigma), as in a real experiment.
 * The dots are a Monte Carlo of the experiment itself: neutrons with true energies, a random emission time within the pulse
 * and a random path length; energy assigned from the arrival time; transmitted with probability T(true E); sample-in counts
 * over open-beam counts per bin. Thin sample: dip = 1 - n sigma, the cross section's shape. Thick: the centre goes black and
 * the dip widens (self-shielding). */
(function () {
  const { TAU, clamp, lerp, smooth, rng } = WT.util;
  const E0 = 6.7, GN = 0.0015, GG = 0.0235, GT = GN + GG, A = 238, KT = 0.0253, SPOT = 9, NAT = 4.8e-6, DL = 0.02;
  const ELO = 5.9, EHI = 7.5, NG = 641, dE = (EHI - ELO) / (NG - 1);
  const s0of = (gn) => 2.608e6 / E0 * ((A + 1) / A) ** 2 * gn / (gn + GG);   // 4 pi lambdabar^2 g Gn/G, barns
  const s0 = s0of(GN);
  const DOP = Math.sqrt(4 * E0 * KT / A);
  /** Doppler-broadened cross section on the grid for a neutron width gn (the true one, or a fit's trial) */
  function sigTab(gn) {
    const sp = s0of(gn), gt = gn + GG;
    const cold = [], ext = 160; for (let i = -ext; i < NG + ext; i++) { const e = ELO + i * dE, x = 2 * (e - E0) / gt; cold.push(sp * Math.sqrt(E0 / Math.max(e, 0.1)) / (1 + x * x)); }
    const k = Math.ceil(3 * DOP / dE), w = []; let ws = 0; for (let j = -k; j <= k; j++) { const v = Math.exp(-((j * dE) ** 2) / (DOP * DOP)); w.push(v); ws += v; }
    const out = new Float64Array(NG); for (let i = 0; i < NG; i++) { let s = 0; for (let j = -k; j <= k; j++) s += w[j + k] * cold[clamp(i + ext + j, 0, cold.length - 1)]; out[i] = s / ws + SPOT; }
    return out;
  }
  const SIG = sigTab(GN);
  const SMAX = Math.max(...SIG);
  const sigAt = (e, tab = SIG) => { const f = (e - ELO) / dE; if (f <= 0) return tab[0]; if (f >= NG - 1) return tab[NG - 1]; const i = Math.floor(f), u = f - i; return tab[i] * (1 - u) + tab[i + 1] * u; };
  /** anywhere (the animated pulse spans 3-30 eV): the grid inside the chart's window, the cold single-level shape outside */
  const sigAny = (e) => (e >= ELO && e <= EHI ? sigAt(e) : s0 * Math.sqrt(E0 / e) / (1 + (2 * (e - E0) / GT) ** 2) + SPOT);
  const tUs = (L, E) => 72.3 * L / Math.sqrt(E);
  const fwhmE = (L, dt, E) => 2 * E * Math.hypot(dt / tUs(L, E), DL / L);
  /** the experiment's expected curve: resolution applied to exp(-n sigma) */
  function curve(n, fw, tab = SIG) {
    const T = tab.map((s) => Math.exp(-n * s)), sg = Math.max(fw / 2.3548, 1e-6), k = Math.min(400, Math.ceil(3.5 * sg / dE));
    if (k < 1) return T;
    const w = []; let ws = 0; for (let j = -k; j <= k; j++) { const v = Math.exp(-0.5 * ((j * dE) / sg) ** 2); w.push(v); ws += v; }
    const out = new Float64Array(NG); for (let i = 0; i < NG; i++) { let s = 0; for (let j = -k; j <= k; j++) s += w[j + k] * Math.exp(-n * sigAt(ELO + (i + j) * dE, tab)); out[i] = s / ws; }
    return out;
  }

  // ---------- the Monte Carlo experiment ----------
  const NB = 64, r = rng(61);
  const nrm = () => Math.sqrt(-2 * Math.log(1 - r())) * Math.cos(TAU * r());
  const mc = { key: "", open: new Float64Array(NB), inn: new Float64Array(NB), cur: null, fw: 0 };
  function shoot(S, k) {
    const L = S.L, dt = S.dt, n = S.thk * NAT;
    for (let i = 0; i < k; i++) {
      const E = (ELO - 0.15) + (EHI - ELO + 0.3) * r(), Lt = L + DL * nrm() * 0.5, t = tUs(Lt, E) + dt * (r() - 0.5);
      const Em = (72.3 * L / t) ** 2, b = Math.floor((Em - ELO) / (EHI - ELO) * NB); if (b < 0 || b >= NB) continue;
      mc.open[b]++; if (r() < Math.exp(-n * sigAt(E))) mc.inn[b]++;
    }
  }
  function sync(S) {
    S.L = S.Lv; S.thk = Math.pow(10, S.lgT); S.dt = Math.pow(10, S.lgDt);
    const key = [S.L.toFixed(0), S.lgT.toFixed(2), S.lgDt.toFixed(2)].join("|");
    if (key !== mc.key) { mc.key = key; mc.open.fill(0); mc.inn.fill(0); mc.fw = fwhmE(S.L, S.dt, E0); mc.cur = curve(S.thk * NAT, mc.fw); shoot(S, 12000); }
  }

  /** misfit of a curve against the simulated counts: chi-square per point (about 1 = as close as the counting noise allows) */
  function chi2(cur) {
    let s = 0, n = 0;
    for (let b = 0; b < NB; b++) { if (mc.open[b] < 20) continue; const t = mc.inn[b] / mc.open[b], e = ELO + (b + 0.5) * (EHI - ELO) / NB, er2 = Math.max(t * (1 - t), 1e-4) / mc.open[b];
      const f = clamp((e - ELO) / dE, 0, NG - 1.001), i = Math.floor(f), m = cur[i] * (1 - (f - i)) + cur[i + 1] * (f - i); s += (t - m) ** 2 / er2; n++; }
    return n ? s / n : 0;
  }
  // ---------- the fit (step 5): a one-number search for the neutron width, starting nearly four times too large ----------
  const fit = { key: "", x: 0, step: 0, dir: -1, tried: false, chi: 0, cur: null, done: false, T: 0 };
  function fitTick(S) {
    const n = S.thk * NAT, make = (x) => curve(n, mc.fw, sigTab(Math.exp(x)));
    if (fit.key !== mc.key) { fit.key = mc.key; fit.x = Math.log(3.7 * GN); fit.step = Math.LN2; fit.dir = -1; fit.tried = false; fit.done = false; fit.cur = make(fit.x); fit.chi = chi2(fit.cur); return; }
    if (fit.done) { fit.chi = chi2(fit.cur); return; }
    fit.chi = chi2(fit.cur);                                 // the counts keep growing: re-score the current guess
    const xc = fit.x + fit.dir * fit.step, cc = make(xc), cchi = chi2(cc);
    if (cchi < fit.chi) { fit.x = xc; fit.cur = cc; fit.chi = cchi; fit.tried = false; }
    else if (!fit.tried) { fit.dir = -fit.dir; fit.tried = true; }
    else { fit.step /= 2; fit.tried = false; if (fit.step < 0.015) fit.done = true; }
  }

  // ---------- the beamline animation ----------
  // animated flight time is proportional to L (and to 1/speed): TA seconds per metre at 6.7 eV, i.e. the real flight slowed SLOW times
  const TA = 2.0 / 50, SLOW = TA / (72.3 / Math.sqrt(E0) * 1e-6), EF0 = 3, EF1 = 30;
  const fly = [], arrivals = []; let pulseT = -9, pulseN = 0;
  const fmtUs = (t) => (t >= 1000 ? `${(t / 1000).toFixed(2)} ms` : `${t.toFixed(0)} µs`);

  WT.chapter("tof", {
    num: "Chapter 16", title: "Catching a resonance", short: "Measuring peaks",
    html: `
<div class="step">
  <p>A neutron's flight time tells its energy. A short pulse of neutrons with all sorts of energies leaves the source and races down an empty tube to the detector; the fast ones arrive first. The tube's length <i>L</i> is known, so each arrival time <i>t</i> gives the neutron's speed, and the speed gives its energy:</p>
  <div class="formula">E = (72.3 · L / t)²   (E in eV, L in metres, t in microseconds)</div>
  <p>The clock above the tube counts real time since the pulse; the flight is drawn about ${Math.round(SLOW / 100) * 100} times slower. Under the tube, the last arrival is turned into an energy. Drag the flight path: a longer tube spreads the same energies over a longer time, so each one is told apart more finely.</p>
  <div class="ctl"><label for="tof-l1">Flight path (m)</label><input id="tof-l1" type="range" data-bind="Lv" data-instant min="5" max="200" step="1" value="50"><output data-show="Lv" data-fmt="0"></output></div>
</div>
<div class="step">
  <p>Thin sample: the dip traces the cross section. A sample now sits in the beam. Near 6.7 eV its nuclei have a resonance and grab neutrons (the flashes), so fewer arrive at the matching time. The chart compares the counts with and without the sample: the <b>transmission</b>, 1 when every neutron gets through.</p>
  <p>The dots are simulated counts, with their scatter; the solid line is what the detector records on average; the dashed line is the shape of the cross section itself. With a thin sample the dip copies that shape.</p>
  <div class="ctl"><label for="tof-d1">Sample thickness (µm)</label><input id="tof-d1" type="range" data-bind="lgT" data-instant min="0" max="3.5" step="0.01" value="0.5"><output data-show="thk" data-fmt="0"></output></div>
</div>
<div class="step">
  <p>Thick sample: the dip saturates. At the peak energy the front of the sample catches every neutron, so the centre goes black and stays black however thick you make it; the dip can only grow by widening into its sides. This is <b>self-shielding</b>: the front layers shield the back. A thick sample then tells more about the resonance's wings than about its peak.</p>
  <div class="ctl"><label for="tof-d2">Sample thickness (µm)</label><input id="tof-d2" type="range" data-bind="lgT" data-instant min="0" max="3.5" step="0.01" value="3"><output data-show="thk" data-fmt="0"></output></div>
</div>
<div class="step">
  <p>Longer pulses, shorter flights: the dip blurs. Three things set a dip's width, all written under the chart: the resonance's own width; the sample's atoms jiggling with heat, which smears each collision's energy a little (<b>Doppler</b> broadening); and the timing blur, because a longer pulse or a shorter tube makes each arrival time, and so each energy, less certain.</p>
  <p>Lengthen the pulse or shorten the tube: the dip gets wider and shallower, though the share of neutrons it removes stays about the same.</p>
  <div class="ctl"><label for="tof-p1">Pulse width (µs)</label><input id="tof-p1" type="range" data-bind="lgDt" data-instant min="-2" max="1" step="0.01" value="0.3"><output data-show="dt" data-fmt="2"></output></div>
  <div class="ctl"><label for="tof-l2">Flight path (m)</label><input id="tof-l2" type="range" data-bind="Lv" data-instant min="5" max="200" step="1" value="20"><output data-show="Lv" data-fmt="0"></output></div>
</div>
<div class="step">
  <p>INCOGNITA works backwards: it takes measured counts like these and asks which resonance, put through this same experiment (thickness, heat, timing blur), reproduces them. Here the fit starts from a guess whose neutron width Γ<sub>n</sub> (how strongly the level holds on to neutrons) is nearly four times too large (the blue curve), and changes it step by step until the curve runs through the dots.</p>
  <p>The readout shows the current guess and the <b>misfit</b>: about 1 means the curve is as close to the dots as their counting scatter allows. Change the experiment and the fit starts again, from new counts, and lands close to the same width; where it cannot match the dots well, the misfit says so.</p>
  <div class="ctl"><label for="tof-l3">Flight path (m)</label><input id="tof-l3" type="range" data-bind="Lv" data-instant min="5" max="200" step="1" value="50"><output data-show="Lv" data-fmt="0"></output></div>
  <div class="ctl"><label for="tof-d3">Sample thickness (µm)</label><input id="tof-d3" type="range" data-bind="lgT" data-instant min="0" max="3.5" step="0.01" value="1.5"><output data-show="thk" data-fmt="0"></output></div>
  <div class="ctl"><label for="tof-p2">Pulse width (µs)</label><input id="tof-p2" type="range" data-bind="lgDt" data-instant min="-2" max="1" step="0.01" value="-1"><output data-show="dt" data-fmt="2"></output></div>
</div>`,
    setup(S) {
      S.set("Lv", 50); S.set("lgT", 1.5); S.set("lgDt", -1); S.set("mode", 0); sync(S);
    },
    steps: [
      (S) => { S.set("mode", 0); S.set("Lv", 50); S.set("lgT", 1.5); S.set("lgDt", -1); },
      (S) => { S.set("mode", 1); S.set("lgT", 0.5); S.set("lgDt", -1); S.set("Lv", 50); },
      (S) => { S.set("mode", 2); S.set("lgT", 3); S.set("lgDt", -1); S.set("Lv", 50); },
      (S) => { S.set("mode", 3); S.set("lgT", 1.5); S.set("lgDt", 0.3); S.set("Lv", 20); },
      (S) => { S.set("mode", 4); S.set("lgT", 1.5); S.set("lgDt", -1); S.set("Lv", 50); fit.key = ""; fit.T = 0; },
    ],
    frame(g, S, dt) {
      sync(S);
      if (dt > 0) { let tot = 0; for (let b = 0; b < NB; b++) tot += mc.open[b]; if (tot < NB * 4000) shoot(S, 900); }
      const { W, H, c, ctx } = g, phone = W < 600, fs = phone ? 11 : 13;
      // ---------- beamline ----------
      const by = H * (phone ? 0.17 : 0.15), xs = W * (phone ? 0.08 : 0.07), len = W * lerp(0.36, 0.84, Math.log(S.L / 5) / Math.log(40)), xd = xs + len, xsm = xs + Math.min(len * 0.22, W * 0.16);
      const pA = S.time - pulseT, tA = (E) => TA * S.L * Math.sqrt(E0 / E);   // animated flight time, proportional to L
      if (pA > tA(EF0) + 1.0 || pulseT < 0) {
        pulseT = S.time; pulseN++;
        // energies from 3 to 30 eV (evenly on a log scale), with extra ones in the chart's window around the resonance
        for (let i = 0; i < (phone ? 12 : 18); i++) { const E = r() < 0.4 ? ELO + (EHI - ELO) * r() : EF0 * Math.pow(EF1 / EF0, r()); fly.push({ E, y: (r() - 0.5) * 10, t0: S.time, dead: false, abs: false }); }
        while (fly.length > 60) fly.shift();
      }
      // tube
      ctx.save(); const tg = ctx.createLinearGradient(xs, 0, xd, 0); tg.addColorStop(0, g.rgba(c.soft, 0.2)); tg.addColorStop(1, g.rgba(c.soft, 0.08)); ctx.fillStyle = tg; ctx.fillRect(xs + 14, by - 11, xd - xs - 22, 22); ctx.restore();
      g.line(xs + 14, by - 11, xd - 8, by - 11, c.soft, 1, 0.5); g.line(xs + 14, by + 11, xd - 8, by + 11, c.soft, 1, 0.5);
      // source: a target struck by a short proton pulse
      g.glow(xs, by, 34, c.warm, 0.25 + 0.6 * Math.max(0, 1 - pA / 0.35));
      ctx.save(); ctx.fillStyle = g.rgba(c.warm, 0.85); if (ctx.roundRect) { ctx.beginPath(); ctx.roundRect(xs - 9, by - 16, 18, 32, 5); ctx.fill(); } else ctx.fillRect(xs - 9, by - 16, 18, 32); ctx.restore();
      g.label(phone ? "source" : "pulsed source", xs, by + 30, { color: c.warm, size: fs - 1, weight: 600 });
      // sample: a slab whose width shows the thickness (from step 2 on)
      if (S.mode > 0) {
      const sw = clamp(2 + 3.2 * S.lgT, 2, 14);
      ctx.save(); const sg = ctx.createLinearGradient(xsm - sw / 2, 0, xsm + sw / 2, 0); sg.addColorStop(0, g.rgba(c.alpha, 0.55)); sg.addColorStop(0.5, g.rgba(c.alpha, 0.95)); sg.addColorStop(1, g.rgba(c.alpha, 0.55)); ctx.fillStyle = sg; ctx.fillRect(xsm - sw / 2, by - 19, sw, 38); ctx.restore();
      g.label("sample", xsm, by - 30, { color: c.alpha, size: fs - 1, weight: 600 }); }
      // detector
      let hit = 0;
      // neutrons: each covers the drawn path in its own flight time (proportional to L / speed)
      for (const f of fly) {
        if (f.dead) continue; const a = S.time - f.t0; if (a < 0) continue;
        const x = xs + 10 + (xd - xs - 16) * a / tA(f.E);
        if (!f.abs && !f.chk && x >= xsm) { f.chk = true; if (S.mode > 0 && r() > Math.exp(-S.thk * NAT * sigAny(f.E))) { f.abs = true; f.ax = xsm; f.at = S.time; } }
        if (f.abs) { const q = S.time - f.at; if (q > 0.8) { f.dead = true; continue; } g.glow(f.ax, by + f.y, 10 + 26 * q, c.photon, 0.7 * (1 - q / 0.8)); if (q < 0.5) for (let k = 0; k < 2; k++) { const an = f.t0 * 9 + k * Math.PI + 0.8; g.photon(f.ax + Math.cos(an) * (6 + q * 60), by + f.y + Math.sin(an) * (6 + q * 60), an, 12, 1 - q / 0.5); } continue; }
        if (x >= xd - 6) { f.dead = true; hit = 1; arrivals.push({ E: f.E, t: tUs(S.L, f.E), at: S.time }); while (arrivals.length > 12) arrivals.shift(); continue; }
        const col = c.neutron; g.line(x - 12, by + f.y, x, by + f.y, col, 2, 0.25); g.ball(x, by + f.y, 3.6, col);
      }
      if (hit) mc.hitT = S.time;
      g.glow(xd, by, 30, c.accent, 0.2 + 0.5 * Math.max(0, 1 - (S.time - (mc.hitT || -9)) / 0.4));
      ctx.save(); ctx.fillStyle = g.rgba(c.accent, 0.9); if (ctx.roundRect) { ctx.beginPath(); ctx.roundRect(xd - 6, by - 18, 14, 36, 4); ctx.fill(); } else ctx.fillRect(xd - 6, by - 18, 14, 36); ctx.restore();
      g.label("detector", xd + 1, by + 30, { color: c.accent, size: fs - 1, weight: 600 });
      // the flight path and flight time
      const ly = by - (phone ? 46 : 52), t0 = tUs(S.L, E0);
      g.line(xs, ly + 8, xd, ly + 8, c.faint, 1, 0.7); g.line(xs, ly + 3, xs, ly + 13, c.faint, 1, 0.7); g.line(xd, ly + 3, xd, ly + 13, c.faint, 1, 0.7);
      if (S.mode === 0) {
        const clock = Math.min(pA, tA(EF0) + 0.6) / SLOW * 1e6, last = arrivals[arrivals.length - 1];
        g.label(`L = ${S.L.toFixed(0)} m · clock: ${fmtUs(clock)} since the pulse`, (xs + xd) / 2, ly - 4, { color: c.ink, size: fs, weight: 600, bg: true });
        if (last) { const fresh = 1 - smooth(1.2, 2.5, S.time - last.at);
          g.label(phone ? `arrived at ${fmtUs(last.t)} → E = ${last.E.toFixed(1)} eV` : `last arrival: t = ${fmtUs(last.t)} → E = (72.3 × ${S.L.toFixed(0)} / ${last.t.toFixed(0)})² = ${last.E.toFixed(1)} eV`, (xs + xd) / 2, by + 50, { color: c.accent, size: fs, weight: 600, bg: true, alpha: 0.45 + 0.55 * fresh }); }
      } else g.label(`L = ${S.L.toFixed(0)} m · ${E0} eV arrives after ${fmtUs(t0)}`, (xs + xd) / 2, ly - 4, { color: c.ink, size: fs, weight: 600, bg: true });

      // ---------- transmission against energy ----------
      const px0 = W * (phone ? 0.13 : 0.1), px1 = W * 0.96, py0 = H * (phone ? 0.4 : 0.33), py1 = H * (phone ? 0.84 : 0.84);
      const X = (e) => px0 + (px1 - px0) * (e - ELO) / (EHI - ELO), Y = (t) => lerp(py1, py0, t / 1.08);
      g.line(px0, py1, px1, py1, c.line, 1); g.line(px0, py0, px0, py1, c.line, 1);
      g.line(px0, Y(1), px1, Y(1), c.line, 1, 0.9, [3, 4]);
      [[0, "0"], [0.5, "0.5"], [1, "1"]].forEach(([t, s]) => g.label(s, px0 - 7, Y(t), { color: c.faint, size: fs - 2, align: "right" }));
      [6, 6.5, 7, 7.5].forEach((e) => g.label(phone && e === 7.5 ? "7.5 eV" : `${e}`, X(e), py1 + 12, { color: c.faint, size: fs - 2 }));
      if (!phone) g.label("neutron energy (eV) →", px1, py1 + 28, { color: c.soft, size: fs - 1, align: "right" });
      g.label("transmission", px0, py0 - 12, { color: c.soft, size: fs - 1, align: "left" });
      // cross-section shape, scaled to the dip's depth
      const cur = mc.cur; let tmin = 1; for (let i = 0; i < NG; i++) tmin = Math.min(tmin, cur[i]);
      const depth = 1 - tmin, shape = []; for (let i = 0; i < NG; i += 2) shape.push([X(ELO + i * dE), Y(1 - depth * (SIG[i] - SPOT) / (SMAX - SPOT))]);
      g.poly(shape, c.alpha, 1.6, 0.85, [5, 4]);
      // the expected measurement
      const ex = []; for (let i = 0; i < NG; i += 2) ex.push([X(ELO + i * dE), Y(cur[i])]);
      g.ground(ex, c.accent, H * 0.05, 0.12); g.poly(ex, c.accent, 2.6, 1);
      // step 1: arrivals inside the chart's window mark their energy on it
      if (S.mode === 0) for (const a of arrivals) { const q = S.time - a.at; if (q > 1.5 || a.E < ELO || a.E > EHI) continue; g.line(X(a.E), py0, X(a.E), py1, c.neutron, 1.5, 0.7 * (1 - q / 1.5)); }
      // step 5: the fit's current curve
      if (S.mode === 4) {
        fit.T -= dt; if (fit.T <= 0 || fit.key !== mc.key) { fitTick(S); fit.T = 0.35; }
        if (fit.cur) { const fp = []; for (let i = 0; i < NG; i += 2) fp.push([X(ELO + i * dE), Y(fit.cur[i])]); g.poly(fp, c.cool, 2.2, 0.9); }
      }
      // Monte Carlo counts
      for (let b = 0; b < NB; b++) { if (mc.open[b] < 20) continue; const t = mc.inn[b] / mc.open[b], e = ELO + (b + 0.5) * (EHI - ELO) / NB, er = Math.sqrt(Math.max(t * (1 - t), 1e-4) / mc.open[b]); g.line(X(e), Y(t - er), X(e), Y(t + er), c.ink, 1, 0.45); g.dot(X(e), Y(t), phone ? 2.2 : 2.8, c.ink, 0.85); }
      // legend
      const lgx = px0 + 10, lgy = Y(0.3);
      g.line(lgx, lgy, lgx + 22, lgy, c.alpha, 1.6, 0.85, [5, 4]); g.label(phone ? "σ shape" : "cross-section shape (scaled)", lgx + 28, lgy, { color: c.alpha, size: fs - 1, align: "left" });
      g.line(lgx, lgy + 18, lgx + 22, lgy + 18, c.accent, 2.6); g.label(phone ? "expected" : "what the detector records", lgx + 28, lgy + 18, { color: c.accent, size: fs - 1, align: "left" });
      g.dot(lgx + 11, lgy + 36, 2.8, c.ink); g.label(phone ? "counts" : "simulated counts", lgx + 28, lgy + 36, { color: c.ink, size: fs - 1, align: "left" });
      if (S.mode === 4) { g.line(lgx, lgy + 54, lgx + 22, lgy + 54, c.cool, 2.2); g.label(phone ? "the fit" : "the fit's current guess", lgx + 28, lgy + 54, { color: c.cool, size: fs - 1, align: "left" }); }
      // readout
      const fw = mc.fw, ry = H * 0.93;
      const meV = (v) => (v >= 0.1 ? `${v.toFixed(2)} eV` : `${(1000 * v).toFixed(v < 0.002 ? 1 : 0)} meV`);
      const rd = { color: c.ink, size: fs + 1, weight: 600, serif: true };
      if (S.mode === 0) g.label(phone ? "fast neutrons first, slow ones later" : "fast neutrons arrive first, slow ones later: the clock sorts them by energy", W * 0.5, ry, rd);
      else if (S.mode === 4) g.label(phone ? `guess Γn ${(1000 * Math.exp(fit.x)).toFixed(2)} meV (true ${1000 * GN}) · misfit ${fit.chi.toFixed(1)}` : `fit: Γn = ${(1000 * Math.exp(fit.x)).toFixed(2)} meV (put into the simulation: ${1000 * GN}) · misfit ${fit.chi.toFixed(1)}${fit.done ? " · done" : ""}`, W * 0.5, ry, rd);
      else if (S.mode === 3) g.label(phone ? `timing ${meV(fw)} · heat ${meV(DOP)} · own ${meV(GT)}` : `width from timing ${meV(fw)} · from heat (Doppler) ${meV(DOP)} · the resonance's own ${meV(GT)}`, W * 0.5, ry, rd);
      else g.label(`sample ${S.thk.toFixed(0)} µm · dip ${(100 * depth).toFixed(0)} % deep${depth > 0.97 ? ": black in the centre" : ""}`, W * 0.5, ry, rd);
      g.label("illustration", W - 6, H - 10, { color: c.faint, size: 10, align: "right" });
    },
  });
})();
