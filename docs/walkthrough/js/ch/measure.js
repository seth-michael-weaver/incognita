/* Chapter 11: what comes out. Scenes (S.mode):
 *   "area"    = cross section as the effective target area: a beam through a foil of nuclei, each with its disc;
 *   "doors"   = a ring of exit doors round the nucleus, one per channel, padlocked below threshold; particles spray out at
 *               rates set by the channel shares and fall into buckets; a threshold strip with the energy marker;
 *   "detect"  = what an experiment sees: a pulsed beam, neutrons flying out at speeds set by their energy (time of flight)
 *               to a ring of detectors; forward and backward halves each build their own energy pile
 *               (evaporation isotropic, pre-equilibrium forward-peaked by Kalbach);
 *   "angle"   = angular distribution: Kalbach forward peaking, petal plus particles;
 *   "star"    = a Maxwellian gas of neutrons among target nuclei; captures flash and drop into a pile of captured energies;
 *   "hot"     = thermally populated target levels as separate entrances (stellar enhancement);
 *   "tmc"     = Total Monte Carlo: three input knobs jitter per variant; translucent capture discs at three energies.
 * Shapes follow specout.py / specang.py (Kalbach a(E_in, E_out), K = a e^{a cos} / 4 pi sinh a), astro/stellar.py
 * (int E sigma e^{-E/kT} dE, partition function sum (2J+1) e^{-E/kT}) and tmc.py (TASMAN factors: 1 + RR d for RR >= 0,
 * 1/(1 + |RR| d) for RR < 0, truncated at |RR| <= 3). Numbers are illustrative. */
(function () {
  const { TAU, clamp, lerp, smooth, rng } = WT.util;
  const sigR = (E) => Math.PI * Math.pow(7.4 + 4.57 / Math.sqrt(Math.max(E, 0.01)), 2) / 100; // b, A ~ 238
  const FACE = Math.PI * 7.4 * 7.4 / 100;                                                       // b, the nucleus's own face

  // channel shares (b) of an illustrative heavy, non-fissile target; th = where the door opens (MeV)
  const CH = [
    { k: "el", name: "elastic", col: "neutron", n: 1, th: 0, f: (E) => 1.2 * (1 - smooth(0.05, 2.5, E)) },
    { k: "in", name: "n′ inelastic", col: "neutron", n: 1, th: 0.08, f: (E) => 1.7 * smooth(0.08, 1.6, E) * (1 - 0.75 * smooth(7.5, 12, E)) },
    { k: "2n", name: "2n", col: "neutron", n: 2, th: 7.5, f: (E) => 1.5 * smooth(7.5, 12, E) * (1 - 0.55 * smooth(14, 20, E)) },
    { k: "3n", name: "3n", col: "neutron", n: 3, th: 14, f: (E) => 0.7 * smooth(14, 20, E) },
    { k: "g", name: "γ capture", col: "photon", n: 1, th: 0, f: (E) => 0.35 / Math.sqrt(Math.max(E, 0.02)) / (1 + Math.pow(E / 1.0, 1.5)) },
    { k: "p", name: "p", col: "proton", n: 1, th: 3, f: (E) => 0.06 * smooth(3, 10, E) },
    { k: "a", name: "α", col: "alpha", n: 1, th: 5, f: (E) => 0.025 * smooth(5, 14, E) },
  ];
  function kalbachA(Ein, Eout) { const ea = Ein + 8, eb = Eout + 8, x1 = Math.min(ea, 130) * eb / ea, x3 = Math.min(ea, 41) * eb / ea; return 0.04 * x1 + 1.8e-6 * x1 ** 3 + 6.7e-7 * 0.5 * x3 ** 4; }
  const kal = (a, th) => (a < 1e-3 ? 1 / (4 * Math.PI) : a / (4 * Math.PI * Math.sinh(a)) * Math.exp(a * Math.cos(th)));
  const preeqFrac = (Ein) => 0.06 + 0.5 * smooth(5, 55, Ein);
  const sigStar = (E) => 60 * Math.sqrt(30 / Math.max(E, 0.5)) * (1 + 0.45 * Math.exp(-((E - 140) ** 2) / (2 * 50 * 50))); // mb, E keV
  const LEVELS = [[0, 0], [0.045, 2], [0.148, 4], [0.307, 6], [0.52, 8], [0.78, 10]];
  const sigTmc = (E, v) => { const base = 0.9 * Math.pow(E, -0.45) / (1 + Math.pow(E / 1.2, 1.3)) * (1 + 0.1 * smooth(6, 10, E)); if (!v) return base; return base * v.psf * Math.pow(Math.max(E, 1e-3) / 0.3, v.ld * 0.25) * (1 + v.omp * smooth(0.3, 3, E)); };
  const nrm = (r) => Math.sqrt(-2 * Math.log(1 - r())) * Math.cos(TAU * r());

  const beam = [], shots = [], variants = [];
  let spawn = 0;
  const doors = CH.map(() => ({ open: false, flash: -9, gap: 0 })), parts = [], fill = CH.map(() => 0);
  const det = { fl: [], fwd: [], bwd: [], pulse: 0, pT: -9, r: rng(5) };
  const star = { gas: [], nuc: [], caps: [], flashes: [], n: 0, kT: 0, r: rng(23) };
  const tmc = { knobs: { psf: 1, ld: 0, omp: 0 }, show: { psf: 0, ld: 0, omp: 0 }, queue: 0, qT: 0, grow: [] };

  WT.chapter("measure", {
    num: "Chapter 11", title: "What comes out", short: "Observables",
    lead: "Everything so far happened inside the nucleus. An experiment, a reactor or a star sees only a handful of numbers. This chapter shows how the engine assembles them.",
    html: `
<div class="step">
  <p>A beam of neutrons, coming from the left, passes through a thin foil of nuclei. The pale disc around each nucleus is its <b>cross section</b>: the area a neutron must hit for a reaction to happen. It is not the nucleus's real size. It is measured in barns (10⁻²⁴ cm², about the face of a uranium nucleus). The share of the beam that reacts is that area times how many nuclei the beam meets.</p>
  <div class="ctl"><label for="mea-e">Neutron energy (MeV)</label><input id="mea-e" type="range" data-bind="E" min="0.1" max="20" step="0.1" value="2"><output data-show="E" data-fmt="1"></output></div>
  <p>Lower the energy and the discs swell: a slow neutron behaves as a wide wave, so it can react from farther away. At high energy the disc shrinks toward the size of the nucleus itself.</p>
</div>
<div class="step">
  <h3>New exits open with energy</h3>
  <p>Each door around the nucleus is one exit, or <b>channel</b>: the neutron bounces back out (elastic), leaves the target excited (n′, inelastic), knocks out a second or third neutron (2n, 3n), is captured with only photons coming out (γ), or a proton or an α particle leaves instead. A padlocked door has a <b>threshold</b>: the reaction costs more energy than the neutron brings. The strip at the bottom marks where each door opens.</p>
  <div class="ctl"><label for="mea-e2">Neutron energy (MeV)</label><input id="mea-e2" type="range" data-bind="E" min="0.1" max="20" step="0.1" value="2"><output data-show="E" data-fmt="1"></output></div>
  <p>Drag the energy past a threshold and that door flashes open. Particles stream out through each door at a rate set by its share, and the buckets below fill to those shares; every new door takes share from the others. Inelastic scattering opens at the first excited level, a second neutron costs about 7.5 MeV, a third about 14. The thresholds come from measured masses; the shares come from the competition of Chapter 6.</p>
</div>
<div class="step">
  <h3>What a detector sees</h3>
  <p>An experiment cannot watch the nucleus. It pulses the beam, and a ring of detectors around the target times each neutron's flight: fast neutrons arrive first, slow ones later, so the arrival time gives the energy. The two halves of the ring each build a pile of neutrons sorted by energy.</p>
  <div class="ctl"><label for="mea-ein">Incident energy (MeV)</label><input id="mea-ein" type="range" data-bind="Ein" min="5" max="60" step="0.5" value="30"><output data-show="Ein" data-fmt="0"></output></div>
  <p>Both piles show a hump of slow neutrons around 1 to 2 MeV. These are <b>evaporated</b>: they boil off the compound nucleus after the energy has been shared among all its nucleons, and they leave in every direction alike. Only the forward pile has a long tail of fast neutrons. These leave from the first collisions, before the energy is shared, still moving roughly the way the beam was going: the <b>pre-equilibrium</b> part. Raise the incident energy and the tail grows.</p>
</div>
<div class="step">
  <h3>Which way they go</h3>
  <p>The petal shape shows how many neutrons leave in each direction; the beam comes from the left. Evaporated neutrons have forgotten the beam's direction and leave equally every way. Fast pre-equilibrium ones remember it and lean forward. The engine uses Kalbach's rule: one slope <i>a</i>, growing with the outgoing energy, sets how far forward they lean.</p>
  <div class="ctl"><label for="mea-eo">Outgoing energy (MeV)</label><input id="mea-eo" type="range" data-bind="Eout" min="1" max="45" step="0.5" value="25"><output data-show="Eout" data-fmt="1"></output></div>
  <p>Lower the outgoing energy and the petal rounds out: slow neutrons are mostly evaporated.</p>
  <div class="formula">dσ/dΩ ∝ e<sup>a cos θ</sup></div>
</div>
<div class="step">
  <h3>In a star</h3>
  <p>Inside a star the neutrons form a hot gas among the target nuclei. Their speeds follow a Maxwell distribution set by the temperature, written as an energy <i>kT</i> (30 keV is about 350 million degrees). The longer a neutron's trail, the faster it moves. Each time one passes a nucleus it may be captured, a flash, with a chance set by the cross section at its energy.</p>
  <div class="ctl"><label for="mea-kt">Temperature kT (keV)</label><input id="mea-kt" type="range" data-bind="kT" min="5" max="100" step="1" value="30"><output data-show="kT" data-fmt="0"></output></div>
  <p>Each captured neutron drops into the pile below, by its energy. The pile is the window that counts: slow neutrons are captured easily but are few and pass by rarely, the fastest are rare, so most captures come from a band around a few <i>kT</i>. The capture rate over the whole gas is the <b>Maxwellian-averaged cross section</b> (MACS), here in millibarns (mb). Heat the gas and the window slides to higher energy, where the nucleus is a smaller target.</p>
</div>
<div class="step">
  <h3>The target is hot too</h3>
  <p>The shelves are the target's lowest energy levels, labelled with spin and energy, and the balls show what share of target nuclei sit on each at this temperature. In a star some targets are already excited. Hotter means more on the upper shelves, and a level with spin <i>J</i> holds more because it has 2<i>J</i>+1 orientations. Each excited level is a different entrance to the same compound nucleus.</p>
  <div class="ctl"><label for="mea-kt2">Temperature kT (keV)</label><input id="mea-kt2" type="range" data-bind="kT" min="5" max="100" step="1" value="30"><output data-show="kT" data-fmt="0"></output></div>
  <p>Raise the temperature and watch nuclei move up. The engine runs the reaction from each populated level and adds the results with these shares; the weights sum to the partition function <i>G</i>. The ratio to the rate from the ground state alone is the <b>stellar enhancement factor</b>.</p>
</div>
<div class="step">
  <h3>How sure is any of this?</h3>
  <p>The three knobs are model inputs, each known only to within some percent: the depth of the optical well (the potential the neutron feels), the level density (how many states per MeV) and the photon strength (how readily the nucleus emits light). Each run of the engine turns them to random settings within those limits and adds one faint disc, its capture cross section, at three neutron energies. Reading the spread of many runs gives an honest uncertainty: <b>Total Monte Carlo</b>.</p>
  <div class="btns"><button class="btn" data-act="tmc1">Run a variant</button><button class="btn ghost" data-act="tmc">Run 10</button><button class="btn ghost" data-act="clear">Clear</button></div>
  <p>A crisp rim means the inputs pin the answer; a fuzzy rim means they do not. At 10 MeV the optical well matters too and the rim blurs most. That is where new measurements would help most.</p>
  <div class="aside">In the code: <code>emission/channels.py</code> (exclusive channels and residuals), <code>specout.py</code> and <code>specang.py</code> (spectra, Kalbach angular distributions), <code>astro/stellar.py</code> (Maxwellian averages, thermally populated targets, partition function), <code>tmc.py</code> (the Total Monte Carlo sampler).</div>
</div>`,
    setup(S) {
      S.set("mode", "area"); S.to("E", 2, true); S.to("Ein", 30, true); S.to("Eout", 25, true); S.to("kT", 30, true);
      S.r = rng(17); S.rT = rng(99);
      S.on("tmc1", () => { tmc.queue += 1; tmc.qT = 9; }); S.on("tmc", () => { tmc.queue += 10; }); S.on("clear", () => { variants.length = 0; tmc.grow.length = 0; });
    },
    steps: [
      (S) => { S.set("mode", "area"); },
      (S) => { S.set("mode", "doors"); doors.forEach((d, i) => (d.open = S.E > CH[i].th)); },
      (S) => { S.set("mode", "detect"); if (!det.fwd.length) seedDetect(S); det.pT = S.time + 0.35; det.pulse = 0; det.fired = false; },
      (S) => { S.set("mode", "angle"); },
      (S) => { S.set("mode", "star"); if (!star.gas.length) seedStar(S); },
      (S) => { S.set("mode", "hot"); },
      (S) => { S.set("mode", "tmc"); if (!variants.length) for (let i = 0; i < 14; i++) addVariant(S, true); },
    ],
    frame(g, S, dt) {
      switch (S.mode) {
        case "area": return sceneArea(g, S, dt);
        case "doors": return sceneDoors(g, S, dt);
        case "detect": return sceneDetect(g, S, dt);
        case "angle": return sceneAngle(g, S, dt);
        case "star": return sceneStar(g, S, dt);
        case "hot": return sceneHot(g, S);
        default: return sceneTmc(g, S, dt);
      }
    },
  });

  // ---------- scene: effective area ----------
  function sceneArea(g, S, dt) {
    const { W, H, c } = g, fs = W < 600 ? 11 : 13, E = S.E, sig = sigR(E), phone = W < 600, ctx = g.ctx;
    const cols = phone ? 3 : 4, rows = 4, gx = W * (phone ? 0.2 : 0.13), gy = Math.min(H * 0.17, 100);
    const fx0 = W * 0.52 - gx * (cols - 1) / 2, fy0 = H * 0.45 - gy * (rows - 1) / 2, Rn = phone ? 8 : 11;
    const rDisc = Math.min(gx * 0.5, gy * 0.5, Rn * Math.sqrt(sig / FACE)), nuclei = [];
    for (let i = 0; i < cols; i++) for (let j = 0; j < rows; j++) nuclei.push([fx0 + i * gx + (j % 2) * gx * 0.35, fy0 + j * gy]);
    // the foil: a soft metallic slab, its top and bottom fading into the page
    const fl = fx0 - gx * 0.55, fr = fx0 + gx * (cols - 1) + gx * 0.9, ft = fy0 - gy * 0.85, fb = fy0 + gy * (rows - 1) + gy * 0.85;
    ctx.save(); const vg = ctx.createLinearGradient(0, ft, 0, fb); vg.addColorStop(0, g.rgba(c.soft, 0)); vg.addColorStop(0.18, g.rgba(c.soft, 0.07)); vg.addColorStop(0.82, g.rgba(c.soft, 0.07)); vg.addColorStop(1, g.rgba(c.soft, 0));
    ctx.fillStyle = vg; ctx.fillRect(fl, ft, fr - fl, fb - ft); ctx.restore();
    [fl, fr].forEach((x) => { ctx.save(); const lg = ctx.createLinearGradient(0, ft, 0, fb); lg.addColorStop(0, g.rgba(c.soft, 0)); lg.addColorStop(0.2, g.rgba(c.soft, 0.45)); lg.addColorStop(0.8, g.rgba(c.soft, 0.45)); lg.addColorStop(1, g.rgba(c.soft, 0)); ctx.strokeStyle = lg; ctx.lineWidth = 1.5; ctx.beginPath(); ctx.moveTo(x, ft); ctx.lineTo(x, fb); ctx.stroke(); ctx.restore(); });
    for (const [x, y] of nuclei) { g.dot(x, y, rDisc, c.neutron, 0.2); g.ring(x, y, rDisc, c.neutron, 1.4, 0.7); g.nucleus(x, y, Rn, { N: 36, Z: 14, t: S.time, jiggle: 0.35, seed: Math.round(x * 3 + y) }); }
    // the beam
    const yb0 = fy0 - gy * 0.55, yb1 = fy0 + gy * (rows - 1) + gy * 0.55;
    spawn += dt; while (spawn > 0.05) { spawn -= 0.05; if (beam.length < 120) beam.push({ x: -10, y: yb0 + S.r() * (yb1 - yb0), v: 260, hit: 0 }); }
    for (const b of beam) {
      if (!b.hit) { b.x += b.v * dt; for (const [x, y] of nuclei) { if (Math.abs(b.x - x) < 4 && Math.abs(b.y - y) < rDisc) { b.hit = S.time; b.hx = x; b.hy = y; break; } } if (b.x > W + 10) b.dead = true; }
      else if (S.time - b.hit > 0.8) b.dead = true;
    }
    for (let i = beam.length - 1; i >= 0; i--) if (beam[i].dead) beam.splice(i, 1);
    for (const b of beam) { if (!b.hit) { for (let k = 1; k < 5; k++) g.dot(b.x - k * 7, b.y, 3 - k * 0.5, c.neutron, 0.25 - k * 0.05); g.ball(b.x, b.y, 4, c.neutron); } else g.glow(b.hx, b.hy, 24, c.warm, 0.8 * (1 - (S.time - b.hit) / 0.8)); }
    // share of the beam that meets a disc: union of the discs' heights across the beam (exact for this foil)
    const iv = []; for (let j = 0; j < rows; j++) { const y = fy0 + j * gy; iv.push([Math.max(yb0, y - rDisc), Math.min(yb1, y + rDisc)]); }
    let cov = 0; iv.forEach(([a, b]) => (cov += Math.max(0, b - a))); const frac = cov / (yb1 - yb0);
    g.label(phone ? `each disc: σ ≈ ${sig.toFixed(1)} b` : `each disc: cross section σ ≈ ${sig.toFixed(1)} b, the area a neutron must hit`, W * 0.52, ft - 4, { color: c.ink, size: fs, bg: true });
    g.label("beam →", W * 0.05, yb0 - 14, { color: c.neutron, size: fs, align: "left" });
    g.label(phone ? `nucleus's own face ≈ ${FACE.toFixed(1)} b · ${(100 * frac).toFixed(0)} % reacts` : `the nucleus's own face ≈ ${FACE.toFixed(1)} b · ${(100 * frac).toFixed(0)} % of the beam reacts in this foil`, W * 0.52, fb + 6, { color: c.soft, size: fs, bg: true });
    g.label(E < 0.5 ? "slow: the neutron's wave reaches well past the surface" : E < 5 ? "the target still looks bigger than the nucleus" : "fast: close to the nucleus's own size", W * 0.5, H * 0.92, { color: c.ink, size: fs + 2, weight: 600, serif: true });
  }

  // ---------- scene: doors ----------
  function door(g, x, y, w, h, open, gap, col, flash, t) {
    const ctx = g.ctx, c = g.c;
    ctx.save(); ctx.fillStyle = g.rgba(c.ink, open ? 0.05 : 0.1); ctx.fillRect(x - w / 2, y - h / 2, w, h); ctx.restore();
    if (open) {
      const gw = Math.max(2, (w - 6) * gap);
      g.glow(x, y, h * 0.7, col, 0.18 + 0.25 * gap + 0.5 * Math.max(0, 1 - (t - flash) / 0.8));
      ctx.save(); ctx.fillStyle = g.rgba(col, 0.55); ctx.fillRect(x - gw / 2, y - h / 2 + 3, gw, h - 3); ctx.restore();
    }
    g.poly([[x - w / 2, y + h / 2], [x - w / 2, y - h / 2], [x + w / 2, y - h / 2], [x + w / 2, y + h / 2]], c.soft, 2.2, open ? 0.9 : 0.5);
    g.line(x - w / 2 - 4, y + h / 2, x + w / 2 + 4, y + h / 2, c.soft, 2, open ? 0.7 : 0.4);
    if (!open) { // padlock
      const ly = y + 2; ctx.save(); ctx.strokeStyle = c.faint; ctx.lineWidth = 2; ctx.beginPath(); ctx.arc(x, ly - 4, 4.5, Math.PI, 0); ctx.stroke(); ctx.fillStyle = c.faint; ctx.fillRect(x - 6.5, ly - 4, 13, 10); ctx.restore();
    }
  }
  function sceneDoors(g, S, dt) {
    const { W, H, c } = g, phone = W < 600, fs = phone ? 10.5 : 13, E = S.E;
    const nx = W * 0.5, ny = H * 0.36, R = Math.min(W, H) * (phone ? 0.06 : 0.065), Rr = Math.min(W * 0.36, H * 0.25), dw = phone ? 22 : 30, dh = phone ? 32 : 44;
    const shares = CH.map((ch) => (E > ch.th ? ch.f(E) : 0)), sum = shares.reduce((a, b) => a + b, 0), mx = Math.max(...shares);
    const pos = CH.map((_, i) => { const a = -Math.PI / 2 + i * TAU / CH.length; return [nx + Math.cos(a) * Rr, ny + Math.sin(a) * Rr, a]; });
    const bY = H * 0.8, bH = H * 0.09, bx0 = W * 0.08, bx1 = W * 0.92, bStep = (bx1 - bx0) / CH.length, bW = bStep * 0.62, bX = (i) => bx0 + (i + 0.5) * bStep;
    // nucleus and doors
    g.nucleus(nx, ny, R, { N: 40, Z: 18, t: S.time, heat: 1.6, jiggle: 0.5, halo: c.warm, haloAlpha: 0.25 });
    CH.forEach((ch, i) => {
      const d = doors[i], open = E > ch.th; if (open && !d.open) d.flash = S.time; d.open = open;
      const tgt = open ? 0.18 + 0.82 * Math.sqrt(shares[i] / mx) : 0; d.gap += (tgt - d.gap) * (1 - Math.exp(-6 * dt));
      const [x, y, a] = pos[i]; door(g, x, y, dw, dh, open, d.gap, c[ch.col], d.flash, S.time);
      const ox = x + Math.cos(a) * (dw * 0.5 + 18), oy = y + Math.sin(a) * (dh * 0.5 + 14), al = Math.abs(Math.cos(a)) < 0.3 ? "center" : Math.cos(a) > 0 ? "left" : "right";
      g.label(ch.name, ox, oy, { color: open ? c.ink : c.faint, size: fs, weight: 600, align: al });
      if (!open) g.label(`opens at ${ch.th} MeV`, ox, oy + fs + 3, { color: c.faint, size: fs - 2, align: al });
    });
    // particles: out through a door, then down into the bucket
    spawn += dt; const rate = 0.09;
    while (spawn > rate) { spawn -= rate; if (sum <= 0) break; let u = S.r() * sum, k = 0; while (k < CH.length - 1 && u > shares[k]) { u -= shares[k]; k++; } if (parts.length < 60) parts.push({ k, t0: S.time, j: (S.r() - 0.5) * 0.5 }); }
    for (let i = parts.length - 1; i >= 0; i--) {
      const p = parts[i], age = S.time - p.t0, ch = CH[p.k], [dx, dy, a] = pos[p.k]; let x, y, ang;
      if (age < 0.5) { const f = age / 0.5; x = lerp(nx + Math.cos(a + p.j) * R, dx, f); y = lerp(ny + Math.sin(a + p.j) * R, dy, f); ang = a; }
      else if (age < 1.5) { const f = (age - 0.5) / 1.0, cxp = dx + Math.cos(a) * 50, cyp = dy + Math.sin(a) * 50, tx = bX(p.k), ty = bY - bH * 0.5; x = (1 - f) * (1 - f) * dx + 2 * f * (1 - f) * cxp + f * f * tx; y = (1 - f) * (1 - f) * dy + 2 * f * (1 - f) * cyp + f * f * ty; ang = Math.atan2(ty - cyp, tx - cxp); }
      else { parts.splice(i, 1); continue; }
      if (ch.k === "g") g.photon(x, y, ang, 16, 1);
      else if (ch.k === "a") { for (let q = 0; q < 4; q++) g.ball(x + (q % 2) * 6 - 3, y + (q > 1 ? 6 : 0) - 3, 3.6, q < 2 ? c.proton : c.neutron); }
      else if (ch.k === "p") g.ball(x, y, 4.5, c.proton);
      else for (let q = 0; q < ch.n; q++) g.ball(x + (q - (ch.n - 1) / 2) * 8, y, 4.5, c.neutron);
    }
    // buckets filled to the shares
    CH.forEach((ch, i) => {
      const p = sum > 0 ? shares[i] / sum : 0; fill[i] += (p - fill[i]) * (1 - Math.exp(-4 * dt));
      const x = bX(i), col = c[ch.col], h = bH * fill[i];
      g.ctx.save(); g.ctx.fillStyle = g.rgba(col, 0.5); g.ctx.fillRect(x - bW / 2 + 2, bY - h, bW - 4, h); g.ctx.restore();
      g.poly([[x - bW / 2 - 2, bY - bH - 4], [x - bW / 2, bY], [x + bW / 2, bY], [x + bW / 2 + 2, bY - bH - 4]], c.soft, 1.5, 0.7);
      g.label(ch.name, x, bY + 12, { color: fill[i] > 0.003 ? c.soft : c.faint, size: fs - 2 });
      if (fill[i] > 0.003) g.label(`${(100 * fill[i]).toFixed(fill[i] < 0.1 ? 1 : 0)} %`, x, bY - h - 10, { color: c.ink, size: fs - 1, weight: 600 });
    });
    // threshold strip
    const sx0 = W * 0.08, sx1 = W * 0.92, sy = H * 0.94, X = (e) => sx0 + (sx1 - sx0) * Math.sqrt(e / 20);
    g.line(sx0, sy, sx1, sy, c.line, 3);
    g.line(sx0, sy, X(E), sy, c.neutron, 3, 0.6);
    const ticks = CH.filter((ch) => ch.th > 0).sort((a, b) => a.th - b.th);
    ticks.forEach((ch, i) => { const x = X(ch.th), on = E > ch.th; g.line(x, sy - 5, x, sy + 5, on ? c.ink : c.faint, 1.5); g.label(ch.name.split(" ")[0], x, sy + (i % 2 ? 14 : -13), { color: on ? c.soft : c.faint, size: fs - 2 }); });
    const ex = X(E); g.poly([[ex - 6, sy - 16], [ex + 6, sy - 16], [ex, sy - 6]], c.ink, 2, 1, undefined, true);
    g.label(`${E.toFixed(1)} MeV`, clamp(ex, sx0 + 30, sx1 - 30), sy - 27, { color: c.ink, size: fs, weight: 600, bg: true });
  }

  // ---------- scene: detectors and time of flight ----------
  function sampleOut(Ein, r) {
    const pe = r() < preeqFrac(Ein); let E, mu;
    if (pe) { E = Math.max(0.2, Ein * Math.pow(r(), 1 / 1.3) - 0.5); const a = kalbachA(Ein, E); mu = Math.log(Math.exp(-a) + r() * (Math.exp(a) - Math.exp(-a))) / a; }
    else { const T = 0.75 * Math.sqrt(Ein / 10); E = Math.min(Ein, -T * Math.log((1 - r()) * (1 - r()))); mu = 2 * r() - 1; }
    return { E, th: Math.acos(clamp(mu, -1, 1)) * (r() < 0.5 ? 1 : -1) };
  }
  function seedDetect(S) { for (let i = 0; i < 260; i++) { const o = sampleOut(S.Ein, det.r); (Math.abs(o.th) < Math.PI / 2 ? det.fwd : det.bwd).push(o.E); } det.Ein = S.Ein; }
  function sceneDetect(g, S, dt) {
    const { W, H, c } = g, phone = W < 600, fs = phone ? 10.5 : 13, Ein = S.Ein;
    const tx = W * 0.5, ty = H * 0.33, L = Math.min(W * 0.4, H * 0.25);
    if (Math.abs(Ein - (det.Ein ?? Ein)) > 2) { det.fwd.length = 0; det.bwd.length = 0; seedDetect(S); }
    // detector ring: tiles, forward half and backward half
    const NT = 28;
    for (let i = 0; i < NT; i++) {
      const a = (i + 0.5) * TAU / NT, fw = Math.cos(a) > 0, x = tx + Math.cos(a) * L, y = ty + Math.sin(a) * L;
      g.ctx.save(); g.ctx.translate(x, y); g.ctx.rotate(a); g.ctx.fillStyle = g.rgba(fw ? c.accent : c.soft, fw ? 0.4 : 0.25); g.ctx.fillRect(-4, -L * TAU / NT * 0.42, 8, L * TAU / NT * 0.84); g.ctx.restore();
    }
    g.label("forward half", tx + L * 0.78, ty - L * 0.78 - 10, { color: c.accent, size: fs, weight: 600, align: "left" });
    g.label("backward half", tx - L * 0.78, ty - L * 0.78 - 10, { color: c.soft, size: fs, weight: 600, align: "right" });
    // beam pulses
    det.pulse += dt; const PER = 1.3;
    if (det.pulse > PER) { det.pulse -= PER; det.pT = S.time + 0.35; }
    const bAge = S.time - (det.pT - 0.35);
    if (bAge >= 0 && bAge < 0.35) { const x = lerp(W * 0.02, tx - 10, bAge / 0.35); for (let k = 0; k < 4; k++) g.ball(x - k * 9, ty + (k % 2 ? 3 : -3), 3.5, c.neutron, 1 - k * 0.2); }
    g.line(W * 0.02, ty, tx - L - 6, ty, c.neutron, 1, 0.3, [3, 4]); g.label(phone ? "pulsed beam" : "pulsed beam →", W * 0.03, ty - 14, { color: c.neutron, size: fs - 1, align: "left" });
    if (S.time >= det.pT && !det.fired) { det.fired = true; for (let i = 0; i < 12; i++) { const o = sampleOut(Ein, det.r); if (det.fl.length < 70) det.fl.push({ E: o.E, th: o.th, t0: det.pT }); } }
    if (S.time < det.pT) det.fired = false;
    const fAge = S.time - det.pT; if (fAge >= 0 && fAge < 0.5) g.glow(tx, ty, 30, c.warm, 0.6 * (1 - fAge / 0.5));
    g.nucleus(tx, ty, 11, { N: 30, Z: 12, t: S.time, jiggle: 0.4 });
    for (let i = det.fl.length - 1; i >= 0; i--) {
      const p = det.fl[i], d = (S.time - p.t0) * 62 * Math.sqrt(p.E), x = tx + Math.cos(p.th) * (14 + d), y = ty + Math.sin(p.th) * (14 + d);
      if (14 + d >= L) { (Math.abs(p.th) < Math.PI / 2 ? det.fwd : det.bwd).push(p.E); det.fl.splice(i, 1); p.hit = true; g.glow(x, y, 14, c.neutron, 0.7); continue; }
      const tl = Math.min(22, 3 * Math.sqrt(p.E)); g.line(x - Math.cos(p.th) * tl, y - Math.sin(p.th) * tl, x, y, c.neutron, 2, 0.25); g.ball(x, y, 3.8, c.neutron);
    }
    while (det.fwd.length > 600) det.fwd.shift(); while (det.bwd.length > 600) det.bwd.shift();
    // the two piles, by energy
    const NB = phone ? 16 : 22, pY = H * 0.9, pH = H * 0.24, pile = (vals, x0, x1, label, col) => {
      const bw = (x1 - x0) / NB, cnt = new Array(NB).fill(0); for (const e of vals) cnt[Math.min(NB - 1, Math.floor(e / Ein * NB))]++;
      const mx = Math.max(10, ...cnt), r = clamp(bw * 0.36, 1.4, 3.2), pitch = Math.min(2 * r + 0.6, pH / mx * 1.0);
      for (let b = 0; b < NB; b++) { const x = x0 + (b + 0.5) * bw; for (let k = 0; k < cnt[b]; k++) g.dot(x, pY - r - k * pitch, r, col, 0.8); }
      g.line(x0, pY + 2, x1, pY + 2, c.line, 1);
      [0, 0.5, 1].forEach((f) => g.label(`${(f * Ein).toFixed(0)}`, x0 + (x1 - x0) * f, pY + 13, { color: c.faint, size: fs - 2 }));
      g.label(label, (x0 + x1) / 2, pY - pH - 18, { color: c.ink, size: fs, weight: 600 });
      return { bw, cnt, pitch, r };
    };
    const bx = [W * 0.05, W * 0.47], fx = [W * 0.53, W * 0.95];
    pile(det.bwd, bx[0], bx[1], phone ? "backward" : "backward detectors", c.neutron);
    const P = pile(det.fwd, fx[0], fx[1], phone ? "forward" : "forward detectors", c.neutron);
    if (!phone) g.label("outgoing neutron energy from the flight time (MeV) →", W * 0.95, pY + 28, { color: c.faint, size: fs - 1, align: "right" });
    const tb = Math.floor(NB * 0.62), tyl = pY - P.r - P.cnt[tb] * P.pitch - 22;
    g.label(phone ? "fast tail" : "fast tail: pre-equilibrium", fx[0] + (tb + 0.5) * P.bw, Math.min(tyl, pY - 40), { color: c.ink, size: fs - 1, bg: true });
    g.label(phone ? "evaporated hump" : "hump: evaporated, every way alike", bx[0] + (bx[1] - bx[0]) * 0.18, pY - pH * 0.55, { color: c.soft, size: fs - 1, bg: true, align: "left" });
    g.label(`${(100 * preeqFrac(Ein)).toFixed(0)} % leave before the energy is shared`, W * 0.5, H * 0.97, { color: c.ink, size: fs + 1, weight: 600, serif: true });
  }

  // ---------- scene: angular distribution ----------
  function sceneAngle(g, S, dt) {
    const { W, H, c } = g, fs = W < 600 ? 11 : 13, Ein = 50, Eout = S.Eout, a = kalbachA(Ein, Eout), f = 0.97 * smooth(2, 28, Eout);
    const cx = W * 0.42, cy = H * 0.47, R = Math.min(W, H) * 0.07, Rp = Math.min(W * 0.46, H * 0.36);
    const Wth = (th) => (1 - f) / (4 * Math.PI) + f * kal(a, th), wMax = Wth(0);
    const petal = []; for (let i = 0; i <= 120; i++) { const th = (i / 120) * TAU, rr = R + 6 + (Rp - R - 6) * Wth(th) / wMax; petal.push([cx + Math.cos(th) * rr, cy + Math.sin(th) * rr]); }
    g.area(petal, c.neutron, 0.14); g.poly(petal, c.neutron, 1.5, 0.9, undefined, true);
    g.arrow(W * 0.03, cy, cx - R - 10, cy, c.neutron, 2, 0.8); g.label("beam", W * 0.03, cy - 14, { color: c.neutron, size: fs, align: "left" });
    g.nucleus(cx, cy, R, { N: 40, Z: 18, t: S.time, heat: 1.4, jiggle: 0.5, halo: c.warm, haloAlpha: 0.2 });
    spawn += dt; while (spawn > 0.08) { spawn -= 0.08; let th; for (let k = 0; k < 40; k++) { th = S.r() * Math.PI; if (S.r() * wMax < Wth(th)) break; } shots.push({ a: S.r() < 0.5 ? th : -th, t0: S.time }); if (shots.length > 60) shots.shift(); }
    for (const sh of shots) { const age = S.time - sh.t0, d = R + 4 + age * 150, fade = 1 - smooth(1.2, 1.7, age); g.ball(cx + Math.cos(sh.a) * d, cy + Math.sin(sh.a) * d, 4.5, c.neutron, fade); }
    g.label(`forward-to-backward ratio ≈ ${(Wth(0) / Wth(Math.PI)).toFixed(1)}  ·  slope a ≈ ${a.toFixed(2)}`, W * 0.5, H * 0.9, { color: c.ink, size: fs + 2, weight: 600, serif: true });
    g.label(f < 0.3 ? "mostly evaporated: every direction alike" : f < 0.7 ? "a mix: the fast share leans forward" : "mostly pre-equilibrium: strongly forward", W * 0.5, H * 0.9 + 22, { color: c.soft, size: fs });
    g.label("forward →", Math.min(cx + Rp + 6, W - 70), cy - 16, { color: c.faint, size: fs - 1, align: "left" });
  }

  // ---------- scene: a star's gas ----------
  function seedStar(S) {
    const r = star.r;
    for (let i = 0; i < 64; i++) { const x = gam15(r); star.gas.push({ x: r(), y: r(), a: r() * TAU, e: x, near: -1 }); }
    for (let i = 0; i < 9; i++) star.nuc.push({ x: 0.1 + 0.8 * ((i * 0.618) % 1), y: 0.15 + 0.7 * ((i * 0.381 + 0.2) % 1) });
    star.kT = S.kT; for (let i = 0; i < 70; i++) star.caps.push(sampleCap(S.kT, r));
  }
  /** Maxwell gas: E/kT ~ Gamma(3/2) */
  function gam15(r) { const z = nrm(r); return -Math.log(1 - r()) + 0.5 * z * z; }
  /** energy of a captured neutron: E sigma(E) e^{-E/kT}, by rejection */
  function sampleCap(kT, r) { for (let k = 0; k < 200; k++) { const e = -kT * Math.log((1 - r()) * (1 - r())); if (r() < sigStar(e) / sigStar(0.5)) return e; } return kT; }
  function sceneStar(g, S, dt) {
    const { W, H, c } = g, phone = W < 600, fs = phone ? 11 : 13, kT = S.kT, r = star.r;
    const gx0 = W * 0.04, gx1 = W * 0.96, gy0 = H * 0.06, gy1 = H * 0.56, gw = gx1 - gx0, gh = gy1 - gy0, Rn = phone ? 9 : 12, enc = Rn + (phone ? 14 : 20);
    if (Math.abs(kT - star.kT) > 3) { star.caps.length = 0; for (let i = 0; i < 40; i++) star.caps.push(sampleCap(kT, r)); star.kT = kT; }
    g.glow((gx0 + gx1) / 2, (gy0 + gy1) / 2, Math.max(gw, gh) * 0.6, c.warm, 0.1 + 0.1 * kT / 100);
    const nucP = star.nuc.map((n) => [gx0 + n.x * gw, gy0 + n.y * gh]);
    for (const [x, y] of nucP) g.nucleus(x, y, Rn, { N: 28, Z: 11, t: S.time, jiggle: 0.35, seed: Math.round(x) });
    const sRef = sigStar(10);
    for (const p of star.gas) {
      const E = p.e * kT, v = gw * 0.1 * Math.sqrt(E / 10);                     // px/s: speed ~ sqrt(E)
      p.x += Math.cos(p.a) * v * dt / gw; p.y += Math.sin(p.a) * v * dt / gh;
      if (p.x < 0 || p.x > 1) { p.a = Math.PI - p.a; p.x = clamp(p.x, 0, 1); } if (p.y < 0 || p.y > 1) { p.a = -p.a; p.y = clamp(p.y, 0, 1); }
      const x = gx0 + p.x * gw, y = gy0 + p.y * gh;
      // passing a nucleus: capture with chance set by sigma(E); faster neutrons pass nuclei more often
      let near = -1; for (let k = 0; k < nucP.length; k++) { const dx = x - nucP[k][0], dy = y - nucP[k][1]; if (dx * dx + dy * dy < enc * enc) { near = k; break; } }
      if (near >= 0 && p.near !== near && r() < 0.9 * sigStar(E) / sRef) {
        star.flashes.forEach((f) => { if (f.k === near) f.quiet = true; }); star.flashes.push({ k: near, t: S.time, E }); star.caps.push(E); star.n++; if (star.caps.length > 220) star.caps.shift();
        p.e = gam15(r); p.x = r() < 0.5 ? 0 : 1; p.y = r(); p.a = r() * TAU; p.near = -1; continue;   // a fresh neutron enters the gas
      }
      p.near = near;
      const tl = Math.min(34, v * 0.12); g.line(x - Math.cos(p.a) * tl, y - Math.sin(p.a) * tl, x, y, c.neutron, 2, 0.22);
      g.ball(x, y, 3.6, c.neutron, 0.9);
    }
    for (let i = star.flashes.length - 1; i >= 0; i--) {
      const f = star.flashes[i], age = S.time - f.t; if (age > 1.4) { star.flashes.splice(i, 1); continue; } f.x = nucP[f.k][0]; f.y = nucP[f.k][1];
      g.glow(f.x, f.y, 18 + age * 20, c.warm, 0.7 * (1 - age / 1.4)); g.ring(f.x, f.y, Rn + 4 + age * 10, c.neutron, 2, 0.8 * (1 - age / 1.4));
      if (age < 0.9) for (let k = 0; k < 2; k++) { const a = f.t * 7 + k * Math.PI, d = Rn + age * 70; g.photon(f.x + Math.cos(a) * d, f.y + Math.sin(a) * d, a, 14, 1 - age / 0.9); }
      if (!phone && !f.quiet && age < 0.8) g.label(`${f.E.toFixed(0)} keV`, f.x, f.y - Rn - 14 - age * 10, { color: c.ink, size: fs - 2, alpha: 1 - age / 0.8 });
    }
    // pile of captured energies
    const px0 = W * 0.06, px1 = W * 0.94, pY = H * 0.86, EM = 300, NB = phone ? 24 : 36, bw = (px1 - px0) / NB, rr = clamp(bw * 0.38, 1.5, 3.4);
    const cnt = new Array(NB).fill(0), c0 = new Array(NB).fill(0); for (const e of star.caps) c0[Math.min(NB - 1, Math.floor(e / EM * NB))]++;
    const pitch = Math.min(2 * rr + 0.5, (pY - H * 0.68) / Math.max(1, ...c0));
    for (const e of star.caps) { const b = Math.min(NB - 1, Math.floor(e / EM * NB)); g.dot(px0 + (b + 0.5) * bw, pY - rr - cnt[b]++ * pitch, rr, c.neutron, 0.85); }
    g.line(px0, pY + 2, px1, pY + 2, c.line, 1);
    [0, 100, 200, 300].forEach((e) => g.label(`${e} keV`, px0 + (px1 - px0) * e / EM, pY + 14, { color: c.faint, size: fs - 2 }));
    const kx = px0 + (px1 - px0) * kT / EM; g.line(kx, pY + 2, kx, H * 0.66, c.warm, 1, 0.6, [3, 3]); g.label(`kT = ${kT.toFixed(0)} keV`, kx + 5, H * 0.66, { color: c.warm, size: fs - 1, align: "left", bg: true });
    g.label(phone ? "energies of captured neutrons" : "each capture drops here, by the neutron's energy: the window that counts", (px0 + px1) / 2, H * 0.6, { color: c.soft, size: fs - 1 });
    // MACS = (2/sqrt pi) int E sigma e^{-E/kT} dE / (kT)^2
    let num = 0, prev = null; for (let i = 0; i <= 200; i++) { const e = 0.5 + 400 * i / 200, v = e * sigStar(e) * Math.exp(-e / kT); if (prev) num += 0.5 * (v + prev[1]) * (e - prev[0]); prev = [e, v]; }
    const macs = 2 / Math.sqrt(Math.PI) * num / (kT * kT);
    g.label(`MACS ≈ ${macs.toFixed(0)} mb at kT = ${kT.toFixed(0)} keV · captures watched: ${star.n}`, W * 0.5, H * 0.95, { color: c.ink, size: fs + 1, weight: 600, serif: true });
  }

  // ---------- scene: a hot target ----------
  function sceneHot(g, S) {
    const { W, H, c } = g, fs = W < 600 ? 11 : 13, kT = S.kT / 1000, phone = W < 600;
    const w = LEVELS.map(([e, j]) => (2 * j + 1) * Math.exp(-e / kT)), G = w.reduce((a, b) => a + b, 0);
    const x0 = W * (phone ? 0.3 : 0.32), yBot = H * 0.78, yTop = H * 0.1, Y = (e) => yBot - (yBot - yTop) * e / 0.85, shelf = Math.min(W * 0.5, 260);
    g.line(x0 - 20, yBot + 2, x0 - 20, yTop - 10, c.line, 1.5);
    LEVELS.forEach(([e, j], i) => {
      const y = Y(e), p = w[i] / G; g.line(x0 - 20, y, x0 + shelf, y, c.ink, 1.5, 0.8);
      g.label(`${j}⁺  ${e === 0 ? "ground state" : (1000 * e).toFixed(0) + " keV"}`, x0 - 28, y, { color: c.soft, size: fs, align: "right" });
      const n = Math.round(p * 40), r = 5; for (let k = 0; k < n; k++) g.ball(x0 + 8 + k * (2 * r + 1.5), y - r - 1, r, c.proton);
      if (p > 0.004) g.label(`${(100 * p).toFixed(p < 0.1 ? 1 : 0)} %`, x0 + 8 + Math.max(n, 0) * (2 * r + 1.5) + 8, y - r - 1, { color: c.ink, size: fs - 1, align: "left" });
    });
    g.label(`kT = ${(1000 * kT).toFixed(0)} keV`, x0 + shelf, yTop - 14, { color: c.warm, size: fs, align: "right", bg: true });
    g.label("target levels, with the share of nuclei sitting on each", W * 0.5, yBot + 26, { color: c.soft, size: fs, bg: true });
    g.label(`${(100 * w[0] / G).toFixed(0)} % start from the ground state · partition function G ≈ ${G.toFixed(2)}`, W * 0.5, H * 0.92, { color: c.ink, size: fs + 1, weight: 600, serif: true });
  }

  // ---------- scene: Total Monte Carlo ----------
  function addVariant(S, instant) {
    const r = S.rT, z = () => clamp(nrm(r), -3, 3), fac = (RR, d) => (RR >= 0 ? 1 + RR * d : 1 / (1 + Math.abs(RR) * d));
    const v = { psf: fac(z(), 0.3), ld: z() * 0.3, omp: z() * 0.25, t0: instant ? -99 : S.time };
    if (variants.length >= 150) variants.shift(); variants.push(v); tmc.knobs = v;
  }
  function knob(g, x, y, R, ang, label, val, fs) {
    const c = g.c; g.dot(x, y, R, c.card, 1); g.ring(x, y, R, c.soft, 2, 0.8);
    for (let k = -4; k <= 4; k++) { const a = -Math.PI / 2 + k * 0.32; g.line(x + Math.cos(a) * (R + 3), y + Math.sin(a) * (R + 3), x + Math.cos(a) * (R + (k ? 6 : 9)), y + Math.sin(a) * (R + (k ? 6 : 9)), c.faint, 1.2); }
    const a = -Math.PI / 2 + ang; g.line(x, y, x + Math.cos(a) * R * 0.82, y + Math.sin(a) * R * 0.82, c.ink, 3); g.dot(x, y, 3, c.ink);
    g.label(label, x, y + R + 16, { color: c.soft, size: fs }); g.label(val, x, y + R + 16 + fs + 4, { color: c.ink, size: fs, weight: 600 });
  }
  function sceneTmc(g, S, dt) {
    const { W, H, c } = g, phone = W < 600, fs = phone ? 10.5 : 13;
    tmc.qT += dt; if (tmc.queue > 0 && tmc.qT > 0.35) { addVariant(S); tmc.queue--; tmc.qT = 0; }
    // knobs: ease toward the latest variant's settings, with a small idle tremble
    const k = tmc.knobs, sh = tmc.show, a = 1 - Math.exp(-8 * dt);
    const tgt = { psf: Math.log(k.psf) / Math.log(1.9), ld: k.ld / 0.9, omp: k.omp / 0.75 };
    for (const key in tgt) sh[key] += (tgt[key] - sh[key]) * a;
    const ky = H * 0.16, KR = Math.min(W * 0.07, H * 0.06), kx = [W * 0.2, W * 0.5, W * 0.8], tr = (i) => Math.sin(S.time * 2 + i * 2) * 0.03;
    knob(g, kx[0], ky, KR, clamp(sh.omp, -1, 1) * 1.28 + tr(0), phone ? "optical well" : "optical well depth", `${k.omp >= 0 ? "+" : "−"}${Math.abs(4 * k.omp).toFixed(1)} %`, fs);
    knob(g, kx[1], ky, KR, clamp(sh.ld, -1, 1) * 1.28 + tr(1), "level density", `${k.ld >= 0 ? "+" : "−"}${Math.abs(30 * k.ld).toFixed(0)} %`, fs);
    knob(g, kx[2], ky, KR, clamp(sh.psf, -1, 1) * 1.28 + tr(2), "photon strength", `×${k.psf.toFixed(2)}`, fs);
    // capture discs at three energies; each variant adds one faint disc of area proportional to its cross section
    const E3 = [[0.01, "10 keV"], [0.5, "500 keV"], [10, "10 MeV"]], dy = H * 0.6, R0 = Math.min(W * 0.11, H * 0.13), dxs = [W * 0.2, W * 0.5, W * 0.8];
    E3.forEach(([e, name], i) => {
      const nom = sigTmc(e), x = dxs[i];
      for (const v of variants) { const grow = smooth(0, 0.5, S.time - v.t0), r = R0 * Math.sqrt(sigTmc(e, v) / nom) * grow; g.dot(x, dy, r, c.neutron, 0.04); g.ring(x, dy, r, c.neutron, 1, 0.25); }
      g.ring(x, dy, R0, c.ink, 1, 0.5, [3, 4]);
      g.nucleus(x, dy, phone ? 8 : 11, { N: 30, Z: 12, t: S.time, jiggle: 0.35, seed: 5 + i });
      let txt = "";
      if (variants.length >= 4) { const vals = variants.map((v) => Math.log(sigTmc(e, v))), m = vals.reduce((p, q) => p + q, 0) / vals.length, sd = Math.sqrt(vals.reduce((p, q) => p + (q - m) ** 2, 0) / vals.length); txt = `±${(100 * sd).toFixed(0)} %`; }
      g.label(name, x, dy + R0 * 1.7 + 6, { color: c.ink, size: fs + 1, weight: 600 });
      g.label(`σ ≈ ${nom >= 1 ? nom.toFixed(1) + " b" : (1000 * nom).toFixed(0) + " mb"} ${txt}`, x, dy + R0 * 1.7 + 8 + fs + 6, { color: c.soft, size: fs });
    });
    g.label(phone ? "dashed: best inputs · each disc drawn at its own scale" : "dashed ring: the best-value inputs · each energy drawn at its own scale (disc area ∝ σ)", W * 0.5, dy - R0 * 1.7 - 10, { color: c.faint, size: fs - 1 });
    g.label(`${variants.length} runs of the engine, each with its inputs nudged at random`, W * 0.5, H * 0.95, { color: c.ink, size: fs + 1, weight: 600, serif: true });
  }
})();
