/* Chapter 3: direct reactions (ecis/, direct/). One-step reactions at the surface.
 * Scenes (S.mode): "graze" = a neutron at impact parameter b: swallowed, grazing kick, or miss;
 *                   "rotor" = a football spun up its rotational band, coupled channels drawn as a web of couplings;
 *                   "vib"   = surface ripples (phonons) of a round nucleus, one or two quanta;
 *                   "dwba"  = the single kick at the surface, strength ~ beta^2, where the potential changes;
 *                   "giant" = the whole nucleus breathing / squashing / pear-shaped, strength spread as humps;
 *                   "capture" = the neutron drops straight into a bound orbit and emits a photon;
 *                   "ledger"  = the reaction flux split: direct slices peel off first.
 * Shapes follow ecis/formfactor.py (deformed Woods-Saxon, dU/dr form factor), ecis/coupling.py + solver.py
 * (all band states solved together), direct/dwba.py (beta^2 scaling, GMR/GQR/LEOR/HEOR as Gaussians),
 * direct/racapcalc.py (direct capture, opt-in), compound/normalization.py (flux ledger). Numbers illustrative. */
(function () {
  const { TAU, clamp, lerp, smooth, rng } = WT.util;
  const A_GR = 100;
  const GR = [
    { k: "mono", name: "breathing (monopole)", E: 18.7 - 0.025 * A_GR, G: 3.0, h: 0.5 },
    { k: "quad", name: "squash and stretch (quadrupole)", E: 65 / Math.cbrt(A_GR), G: 85 / Math.pow(A_GR, 2 / 3), h: 1.0 },
    { k: "oct", name: "pear-shaped (octupole), low and high", E: 31 / Math.cbrt(A_GR), G: 5.0, h: 0.3, E2: 115 / Math.cbrt(A_GR), G2: 9.3 - A_GR / 48, h2: 0.45 },
  ];
  let kickT = -10, capT = -10;
  /** Ground fill under a profile with its two x-ends faded into the page (no hard box edges). Draw it first in a scene:
   *  the fade erases (destination-out) whatever lies under the ends. */
  function fground(g, pts, color, depth = 140, alpha = 0.3, fade = 60) {
    if (pts.length < 2) return; const ctx = g.ctx; let top = Infinity, bot = -Infinity;
    for (const p of pts) { top = Math.min(top, p[1]); bot = Math.max(bot, p[1]); }
    const maxY = bot + depth, xa = pts[0][0], xb = pts[pts.length - 1][0], f = Math.min(fade, (xb - xa) * 0.3);
    ctx.save(); ctx.beginPath(); ctx.moveTo(xa, maxY); for (const p of pts) ctx.lineTo(p[0], p[1]); ctx.lineTo(xb, maxY); ctx.closePath(); ctx.clip();
    const gr = ctx.createLinearGradient(0, top, 0, maxY); gr.addColorStop(0, g.rgba(color, alpha)); gr.addColorStop(1, g.rgba(color, 0)); ctx.fillStyle = gr;
    ctx.fillRect(xa, top, xb - xa, maxY - top);
    ctx.globalCompositeOperation = "destination-out";
    const gl = ctx.createLinearGradient(xa, 0, xa + f, 0); gl.addColorStop(0, "rgba(0,0,0,1)"); gl.addColorStop(1, "rgba(0,0,0,0)"); ctx.fillStyle = gl; ctx.fillRect(xa, top, f, maxY - top);
    const gq = ctx.createLinearGradient(xb, 0, xb - f, 0); gq.addColorStop(0, "rgba(0,0,0,1)"); gq.addColorStop(1, "rgba(0,0,0,0)"); ctx.fillStyle = gq; ctx.fillRect(xb - f, top, f, maxY - top);
    ctx.restore();
  }



  WT.chapter("direct", {
    num: "Chapter 3", title: "A glancing blow", short: "Direct reactions",
    lead: "Not every neutron that reaches the nucleus is swallowed. Some brush its surface, give it one push, and fly on.",
    html: `
<div class="step">
  <p>A neutron that only grazes the nucleus can push it once into an excited level and fly on, mostly forward and only a little slower. That is a <b>direct reaction</b>: one step, over in about 10⁻²² seconds. Here a neutron flies past at distance <i>b</i>, the <b>impact parameter</b>, in nuclear radii <i>R</i>; the dotted ring is the nucleus's skin.</p>
  <div class="ctl"><label for="di-b">Aim b (in radii)</label><input id="di-b" type="range" data-bind="b" min="0" max="1.5" step="0.01" value="1.0"><output data-show="b" data-fmt="2"></output></div>
  <p>Drag <i>b</i>. Below about 0.8 the neutron is swallowed. Near 1 it grazes and leaves the nucleus on its first excited level, 2⁺. Above about 1.2 it misses and only bends: <b>elastic scattering</b>, nucleus unchanged.</p>
</div>
<div class="step">
  <h3>Setting a stretched nucleus spinning</h3>
  <p>A push sets a stretched nucleus (Chapter 1) rotating, up the ladder of its <b>rotational band</b>: 0⁺, 2⁺, 4⁺, 6⁺, 8⁺. The neutron can push the nucleus up and the nucleus can push back, so no level can be worked out alone. The engine solves them all together: <b>coupled channels</b>, where each channel is one outcome, here one level of the band.</p>
  <div class="btns"><button class="btn" data-act="kick">Push it up a level</button><button class="btn ghost" data-act="rpause">Pause / resume</button></div>
  <div class="ctl"><label for="di-beta">Deformation β₂</label><input id="di-beta" type="range" data-bind="beta2" min="0.05" max="0.4" step="0.01" value="0.25"><output data-show="beta2" data-fmt="2"></output></div>
  <p>The arcs show which levels are linked: <i>λ</i> = 2, the overall stretch, links neighbours; <i>λ</i> = 4, a finer bulge, jumps two. Drag <i>β₂</i>: a more stretched nucleus links its levels more strongly, and the arcs thicken. Since the band is solved with the incoming wave, the transmission coefficients already leave out what it takes.</p>
</div>
<div class="step">
  <h3>Ripples on a sphere</h3>
  <p>A round nucleus can ripple, and ripple energy comes in equal packets called <b>phonons</b>. One phonon of the football-to-disc ripple (<i>λ</i> = 2) gives the 2⁺ level; two give three levels, 0⁺, 2⁺ and 4⁺, at twice the energy. Reaching them takes two pushes in a row. The engine solves these levels together with the ground state.</p>
  <div class="ctl"><label for="di-lam">Ripple shape λ</label><input id="di-lam" type="range" data-bind="lam" min="2" max="3" step="1" value="2" data-instant><output data-show="lam" data-fmt="0"></output></div>
  <div class="btns"><button class="btn ghost" data-act="ph1">One phonon</button><button class="btn ghost" data-act="ph2">Two phonons</button></div>
  <p>Set <i>λ</i> = 3 for a pear-shaped ripple, whose first level is 3⁻. Press the buttons to add one or two phonons.</p>
</div>
<div class="step">
  <h3>One push, once</h3>
  <p>For most levels the link is weak, and one push is enough: <b>DWBA</b> (distorted-wave Born approximation). The incoming wave of Chapter 2 pushes the nucleus once, at the rim, where the potential drops from deep to zero; the rim glows where the crests strike. The circular wave spreading out is the neutrons that left the nucleus excited.</p>
  <div class="ctl"><label for="di-bd">Level's deformation β</label><input id="di-bd" type="range" data-bind="bd" min="0.02" max="0.4" step="0.01" value="0.2"><output data-show="bd" data-fmt="2"></output></div>
  <p>Drag <i>β</i>: the rim wobbles harder and the circles brighten, as <i>β</i>²: twice the deformation, four times as many. The engine takes each level's <i>β</i> from measured values, or from systematics where none is known. How the scattered neutrons spread over angles is an optional extra output.</p>
</div>
<div class="step">
  <h3>The whole nucleus moves</h3>
  <p>All the nucleons can move together: breathe, squash and stretch, or swing into a pear shape. These are <b>giant resonances</b>. In this medium-mass nucleus they sit about 7 to 25 MeV up, each several MeV wide, too broad to count as one level; the humps mark each one's <b>excitation energy</b>.</p>
  <p>The engine sets each one's total strength from a <b>sum rule</b>, a limit from basic physics on how strongly a nucleus can respond, and spreads it as a hump above the last known level. These humps, plus pushes to high levels, make up the <b>collective continuum</b>.</p>
  <div class="btns"><button class="btn ghost" data-act="mono">Breathing</button><button class="btn ghost" data-act="quad">Squash</button><button class="btn ghost" data-act="oct">Pear</button></div>
  <p>The best-known one, protons sloshing against neutrons (the giant dipole resonance), mainly absorbs and emits light, so it belongs to Chapter 7.</p>
</div>
<div class="step">
  <h3>Straight into an orbit</h3>
  <p>A free neutron can drop straight into an empty <b>orbit</b> of the well (an allowed energy for one neutron inside) and send the spare energy out as a <em class="g">photon</em>. The nucleus never heats up. This is <b>direct capture</b>. The engine can compute it from the same well as Chapter 2: the free wave outside, the bound orbit inside, the photon linking them. It is optional and off by default.</p>
  <div class="btns"><button class="btn" data-act="drop">Drop a neutron in</button></div>
  <p>Direct capture matters most where the usual route, sharing the neutron's energy, is weak: light nuclei and nuclei far from stability, with few, widely spaced levels.</p>
</div>
<div class="step">
  <h3>Direct takes its share first</h3>
  <p>The engine splits the reaction cross section of Chapter 2 in order: direct reactions first, then fast collisions, and only the remainder forms a compound nucleus. In the picture each neutron meets one of three fates: <b>direct</b> (grazes and flies on), fast (knocks a nucleon out before the energy spreads: <b>pre-equilibrium</b>, Chapter 4) or swallowed (a <b>compound nucleus</b>, Chapter 5). The piles count them.</p>
  <div class="ctl"><label for="di-e">Neutron energy (MeV)</label><input id="di-e" type="range" data-bind="E" min="1" max="60" step="0.5" value="14"><output data-show="E" data-fmt="1"></output></div>
  <p>Drag the energy and watch the piles refill. At a few MeV almost every neutron is swallowed. At tens of MeV, direct reactions and fast collisions together take a large part.</p>
  <div class="aside">In the code: <code>ecis/formfactor.py</code>, <code>ecis/coupling.py</code>, <code>ecis/solver.py</code> (deformed potential, coupled channels for rotors and vibrators), <code>ecis/dwba.py</code> and <code>direct/dwba.py</code> (single push, giant resonances, collective continuum), <code>direct/racapcalc.py</code> (direct capture, optional, off by default), <code>compound/normalization.py</code> (the ledger).</div>
</div>`,
    setup(S) {
      S.set("mode", "graze"); S.to("b", 1.0, true); S.to("beta2", 0.25, true); S.set("J", 0); S.to("lam", 2, true); S.to("nph", 1, true);
      S.to("bd", 0.2, true); S.set("gr", "quad"); S.to("E", 14, true);
      S.on("rpause", () => { S.rotPaused = !S.rotPaused; });
      S.on("kick", () => { S.set("J", S.J >= 8 ? 0 : S.J + 2); kickT = S.time; });
      S.on("ph1", () => S.to("nph", 1)); S.on("ph2", () => S.to("nph", 2));
      S.on("mono", () => S.set("gr", "mono")); S.on("quad", () => S.set("gr", "quad")); S.on("oct", () => S.set("gr", "oct"));
      S.on("drop", () => { capT = S.time; });
    },
    steps: [
      (S) => S.set("mode", "graze"),
      (S) => { S.set("mode", "rotor"); if (S.J === 0) { S.set("J", 2); kickT = S.time; } },
      (S) => S.set("mode", "vib"),
      (S) => S.set("mode", "dwba"),
      (S) => S.set("mode", "giant"),
      (S) => { S.set("mode", "capture"); capT = S.time - 1.7; },
      (S) => { S.set("mode", "ledger"); seedBeam(S); },
    ],
    frame(g, S, dt) {
      switch (S.mode) {
        case "graze": return drawGraze(g, S);
        case "rotor": return drawRotor(g, S);
        case "vib": return drawVib(g, S);
        case "dwba": return drawDwba(g, S);
        case "giant": return drawGiant(g, S);
        case "capture": return drawCapture(g, S);
        default: return drawLedger(g, S, dt);
      }
    },
  });

  // ---------- scene 1: aim ----------
  function drawGraze(g, S) {
    const { W, H, c } = g; const phone = W < 600;
    const cx = W * 0.52, cy = H * 0.5, R = Math.min(W, H) * 0.19;
    const b = S.b; const kind = b < 0.82 ? "in" : b < 1.18 ? "graze" : "miss";
    const P = 2.6, t = S.time % P, u = t / P; // one neutron per period
    const xs = cx - R * 3.2, xe = cx + R * 3.2;
    // nucleus: heats if swallowed, wobbles if grazed
    const hit = smooth(0.42, 0.5, u);
    const heat = kind === "in" ? hit * (1 - smooth(0.85, 1, u)) : 0;
    const wob = kind === "graze" ? hit * Math.sin((u - 0.45) * 30) * Math.exp(-(u - 0.45) * 6) * 0.12 : 0;
    g.nucleus(cx, cy, R, { N: 56, Z: 26, seed: 9, t: S.time, beta: wob, heat: 1 + 2.5 * heat, jiggle: 0.5, halo: c.warm, haloAlpha: 0.05 + heat * 0.4 });
    g.ring(cx, cy, R * 1.18, c.faint, 1, 0.5, [3, 5]);
    g.label("skin (surface)", cx + R * 1.18 * 0.72, cy - R * 1.18 * 0.72 - 8, { color: c.faint, size: 11 });
    // the aiming line
    const yb = cy - b * R;
    g.line(xs - 30, yb, cx - R * 1.3, yb, c.faint, 1, 0.5, [2, 6]);
    g.label(`b = ${b.toFixed(2)} R`, xs - 30, yb - 12, { color: c.faint, size: 11, align: "left" });
    // the neutron's path
    let x, y, alpha = 1;
    if (kind === "in") {
      const uu = Math.min(u, 0.46) / 0.46; x = lerp(xs, cx - Math.sqrt(Math.max(0, R * R - (b * R) ** 2)) * 0.6, uu); y = yb; alpha = 1 - hit;
      for (let i = 1; i < 8; i++) g.dot(x - i * 9, y, 5 - i * 0.5, c.neutron, alpha * (0.22 - i * 0.025));
      if (alpha > 0.02) g.ball(x, y, 7, c.neutron, alpha);
      g.label("absorbed: its energy is shared by all nucleons", cx, cy + R + 44, { color: c.warm, size: phone ? 13 : 15, serif: true, italic: true, alpha: hit });
    } else {
      const bend = kind === "graze" ? 0.55 : clamp(0.25 - (b - 1.18) * 0.8, 0, 0.25);
      const dx = lerp(xs, xe, u); const past = smooth(0.42, 0.75, u);
      y = yb + past * bend * R * (kind === "graze" ? 1 : 0.5); x = dx;
      const slow = kind === "graze" ? 1 - 0.25 * past : 1;
      for (let i = 1; i < 8; i++) { const uu = Math.max(0, u - i * 0.012); g.dot(lerp(xs, xe, uu), yb + smooth(0.42, 0.75, uu) * bend * R * (kind === "graze" ? 1 : 0.5), 5 - i * 0.5, c.neutron, 0.22 - i * 0.025); }
      g.ball(x, y, 7 * slow + 0.5, c.neutron, 1);
      if (kind === "graze") {
        if (past > 0.05) g.label("2⁺ level", cx, cy - R - 16, { color: c.warm, size: 14, weight: 600, alpha: past });
        g.label("one push leaves the nucleus on 2⁺; neutron flies on", cx, cy + R + 44, { color: c.ink, size: phone ? 13 : 15, serif: true, italic: true, alpha: past });
      } else g.label("a miss: deflected, nucleus unchanged (elastic)", cx, cy + R + 44, { color: c.soft, size: phone ? 13 : 15, serif: true, italic: true, alpha: past });
    }
  }

  // ---------- scene 2: rotor and coupled channels ----------
  function drawRotor(g, S) {
    const { W, H, c } = g; const phone = W < 600;
    const J = S.J, beta = S.beta2;
    const cx = phone ? W * 0.33 : W * 0.36, cy = H * 0.5, R = Math.min(W, H) * 0.19;
    // rotation rate grows with J (0⁺ does not rotate); slow enough to follow, real-time, pausable
    const w = 0.13 * J, dtr = S.rotT == null ? 0 : Math.min(0.1, Math.max(0, S.time - S.rotT)); S.rotT = S.time;
    if (!S.rotPaused) S.rotPhase = (S.rotPhase || 0) + w * dtr;
    const kickAge = S.time - kickT, flash = Math.max(0, 1 - kickAge / 0.8);
    g.nucleus(cx, cy, R, { N: 150, Z: 62, seed: 5, t: S.time, beta, rot: S.rotPhase, jiggle: 0.35, halo: c.warm, haloAlpha: flash * 0.4 });
    if (flash > 0) { const a = -0.8; g.ball(cx + Math.cos(a) * (R * 1.3 + kickAge * 220), cy + Math.sin(a) * (R * 1.3 + kickAge * 220), 6, c.neutron, flash); }
    g.label(J === 0 ? "at rest: 0⁺" : `rotating: ${J}⁺${S.rotPaused ? " (paused)" : ""}`, cx, cy + R * 1.45 + 24, { color: c.ink, size: phone ? 13 : 16, weight: 600, serif: true });
    // band ladder + coupling web
    const x0 = phone ? W * 0.68 : W * 0.7, x1 = phone ? W * 0.84 : W * 0.86, yb = H * 0.86, yt = H * 0.12;
    const k = (yb - yt) / 74 * clamp(0.25 / beta, 0.6, 1.6);
    const ys = {}; for (let j = 0; j <= 8; j += 2) ys[j] = yb - k * j * (j + 1);
    const vis = (j) => ys[j] >= yt - 4;
    // couplings: lambda=2 neighbours (thick), lambda=4 skip-one (thin)
    for (let j = 0; j <= 6; j += 2) if (vis(j + 2)) arc(g, x0 - 8, ys[j], ys[j + 2], -16 - 40 * beta, c.cool, 1 + 10 * beta, 0.75);
    for (let j = 0; j <= 4; j += 2) if (vis(j + 4)) arc(g, x0 - 8, ys[j], ys[j + 4], -70 - 120 * beta, c.alpha, 0.6 + 40 * beta * beta, 0.6);
    for (let j = 0; j <= 8; j += 2) { if (!vis(j)) continue; const on = j === J; g.line(x0, ys[j], x1, ys[j], on ? c.warm : c.soft, on ? 3 : 1.6); g.label(`${j}⁺`, x1 + 28 + (j >= 4 ? 10 : 0), ys[j], { color: on ? c.warm : c.soft, size: 12, align: "left", bg: true }); }
    if (vis(J)) { g.glow((x0 + x1) / 2, ys[J] - 8, 20, c.warm, 0.4); g.ball((x0 + x1) / 2, ys[J] - 8, 8, c.warm); }
    g.label("λ = 2", x0 - 16 - 20 * beta, (ys[0] + ys[2]) / 2, { color: c.cool, size: 11, bg: true });
    if (vis(4)) g.label("λ = 4", x0 - 44 - 60 * beta, (ys[0] + ys[4]) / 2, { color: c.alpha, size: 11, bg: true });
    g.label("levels solved together", (x0 + x1) / 2, yt - 18, { color: c.soft, size: phone ? 11 : 12, bg: true });
  }
  function arc(g, x, y0, y1, bulge, color, w, alpha) {
    const ctx = g.ctx; ctx.save(); ctx.globalAlpha = alpha; ctx.strokeStyle = color; ctx.lineWidth = w; ctx.lineCap = "round";
    ctx.beginPath(); ctx.moveTo(x, y0); ctx.quadraticCurveTo(x + bulge, (y0 + y1) / 2, x, y1); ctx.stroke(); ctx.restore();
  }

  // ---------- scene 3: vibrations ----------
  function drawVib(g, S) {
    const { W, H, c } = g; const phone = W < 600;
    const lam = Math.round(S.lam), nph = S.nph;
    const cx = phone ? W * 0.23 : W * 0.3, cy = H * 0.48, R = Math.min(W, H) * (phone ? 0.15 : 0.18);
    const amp = 0.13 * Math.sqrt(nph) * Math.sin(S.time * 3.6);
    const pts = []; for (let i = 0; i <= 120; i++) { const th = i / 120 * TAU; const r = R * (1 + amp * Math.cos(lam * th)); pts.push([cx + Math.cos(th) * r, cy + Math.sin(th) * r]); }
    g.glow(cx, cy, R * 1.5, c.neutron, 0.12);
    g.area(pts, c.neutron, 0.22); g.poly(pts, c.ink, 2, 0.9, null, true);
    // a few nucleons inside that follow the surface motion
    const r = rng(23); for (let i = 0; i < 28; i++) { const th = r() * TAU, rr = Math.sqrt(r()) * 0.85; const sc = 1 + amp * Math.cos(lam * th) * rr; g.ball(cx + Math.cos(th) * rr * R * sc, cy + Math.sin(th) * rr * R * sc, R * 0.11, i % 2 ? c.proton : c.neutron, 0.8); }
    g.ring(cx, cy, R, c.faint, 1, 0.6, [3, 5]);
    g.label(lam === 2 ? "quadrupole ripple: football ↔ disc" : "octupole ripple: pear ↔ pear", phone ? W / 2 : cx, phone ? H * 0.94 : cy + R * 1.3 + 26, { color: c.ink, size: phone ? 13 : 15, weight: 600, serif: true });
    // phonon ladder
    const x0 = phone ? W * 0.52 : W * 0.68, x1 = phone ? W * 0.64 : W * 0.8, yb = H * 0.82, yt = H * 0.18, dy = (yb - yt) / 2;
    const one = lam === 2 ? "2⁺" : "3⁻", two = lam === 2 ? "0⁺ 2⁺ 4⁺" : "0⁺ 2⁺ 4⁺ 6⁺", ls = phone ? 11 : 12;
    g.line(x0, yb, x1, yb, c.ink, 2.5); g.label("0⁺  no phonon", x1 + 8, yb, { color: c.ink, size: ls, align: "left" });
    const on1 = Math.abs(nph - 1) < 0.5, on2 = nph > 1.5;
    g.line(x0, yb - dy, x1, yb - dy, on1 ? c.warm : c.soft, on1 ? 3 : 1.6); g.label(`${one}  one phonon`, x1 + 8, yb - dy, { color: on1 ? c.warm : c.soft, size: ls, align: "left" });
    for (let k = -1; k <= 1; k++) g.line(x0, yb - 2 * dy + k * 6, x1, yb - 2 * dy + k * 6, on2 ? c.warm : c.soft, on2 ? 2.5 : 1.4);
    if (phone) { g.label(two, x1 + 8, yb - 2 * dy - 9, { color: on2 ? c.warm : c.soft, size: ls, align: "left" }); g.label("two phonons", x1 + 8, yb - 2 * dy + 9, { color: on2 ? c.warm : c.soft, size: ls, align: "left" }); }
    else g.label(`${two}  two phonons`, x1 + 8, yb - 2 * dy, { color: on2 ? c.warm : c.soft, size: 12, align: "left" });
    arc(g, x0 - 8, yb, yb - dy, -26, c.cool, 3, 0.7); arc(g, x0 - 8, yb - dy, yb - 2 * dy, -26, c.cool, 3, 0.7); arc(g, x1 + 4, yb, yb - 2 * dy, 30, c.alpha, 1.2, 0.6);
    if (phone) g.label("one push", x0 - 24, yb + 16, { color: c.cool, size: 11 });
    else g.label("one push", x0 - 38, yb - dy, { color: c.cool, size: 11, align: "right" });
    g.label("two pushes", x1 + 34, yb - dy - 24, { color: c.alpha, size: 11, align: "left", bg: true });
    g.label("equal energy steps", (x0 + x1) / 2, yt - (phone ? 32 : 16), { color: c.soft, size: 12, bg: true });
  }

  // ---------- scene 4: DWBA single push at a wobbling rim ----------
  let dfield = null, dfctx = null;
  function hexRgb(h) { h = (h || "#888888").replace("#", ""); if (h.length === 3) h = h.split("").map((x) => x + x).join(""); const n = parseInt(h, 16); return [(n >> 16) & 255, (n >> 8) & 255, n & 255]; }
  function drawDwba(g, S) {
    const { W, H, c } = g, ctx = g.ctx; const phone = W < 600;
    const bd = S.bd, str = clamp((bd / 0.2) ** 2, 0, 4);
    const cx = W * 0.5, cy = H * 0.44, R = Math.min(W, H) * 0.17;
    const k = TAU / (R * 0.62), om = 2.4, t = S.time;
    const wob = Math.sin(t * 3.1);
    const rim = (th) => R * (1 + bd * 0.9 * (1.5 * Math.cos(th) ** 2 - 0.5) * (0.55 + 0.45 * wob));
    // incoming plane wave as a field (like Chapter 2), slightly faster crests inside the nucleus
    const NX = 170, NY = Math.round(170 * H / W);
    if (!dfield || dfield.width !== NX || dfield.height !== NY) { dfield = document.createElement("canvas"); dfield.width = NX; dfield.height = NY; dfctx = dfield.getContext("2d"); }
    const img = dfctx.createImageData(NX, NY), d = img.data, col = hexRgb(c.neutron), bg = hexRgb(c.paper);
    for (let j = 0; j < NY; j++) {
      const y = (j + 0.5) / NY * H - cy;
      for (let i = 0; i < NX; i++) {
        const x = (i + 0.5) / NX * W - cx, r = Math.hypot(x, y);
        const inside = r < R, ph = k * x * (inside ? 1.35 : 1) - om * t;
        const v = 0.5 + 0.5 * Math.cos(ph), sh = x > 0 ? 1 - 0.35 * Math.exp(-((y / R) ** 4)) * smooth(0, R, x) : 1, a = v * v * (inside ? 0.4 : 0.7 * sh) * 0.62;
        const p = (j * NX + i) * 4; d[p] = lerp(bg[0], col[0], a); d[p + 1] = lerp(bg[1], col[1], a); d[p + 2] = lerp(bg[2], col[2], a); d[p + 3] = 255;
      }
    }
    dfctx.putImageData(img, 0, 0); ctx.save(); ctx.imageSmoothingEnabled = true; ctx.drawImage(dfield, 0, 0, W, H); ctx.restore();
    g.vignette(0.16);
    // the outgoing (inelastic) wave: circles from the rim, forward-peaked, strength ~ beta^2
    const lam = 2 * Math.PI / k;
    for (let n = 0; n < 6; n++) {
      const rr = R * 1.05 + ((t * om / k + n * lam) % (6 * lam));
      const fadeR = Math.max(0, 1 - (rr - R) / (6 * lam));
      for (let sgm = 0; sgm < 24; sgm++) {
        const a0 = sgm / 24 * TAU, a1 = (sgm + 1) / 24 * TAU, th = (a0 + a1) / 2;
        const al = clamp(0.35 * str, 0, 0.9) * fadeR * (0.35 + 0.65 * (0.5 + 0.5 * Math.cos(th)));
        ctx.save(); ctx.globalAlpha = al; ctx.strokeStyle = c.neutron; ctx.lineWidth = 3; ctx.beginPath(); ctx.arc(cx, cy, rr, a0, a1); ctx.stroke(); ctx.restore();
      }
    }
    // the nucleus and its rim; the rim lights up where a crest strikes it (the steep edge is where the push acts)
    g.nucleus(cx, cy, R * 0.86, { N: 56, Z: 26, seed: 9, t, alpha: 0.5, jiggle: 0.3, beta: bd * 0.6 * (0.55 + 0.45 * wob) });
    const pts = []; for (let i = 0; i <= 90; i++) { const th = i / 90 * TAU, r = rim(th); pts.push([cx + Math.cos(th) * r, cy + Math.sin(th) * r]); }
    g.poly(pts, c.ink, 1.6, 0.7, null, true);
    for (let i = 0; i < 40; i++) {
      const th = i / 40 * TAU, r = rim(th), x = Math.cos(th) * r, y = Math.sin(th) * r;
      const crest = Math.pow(Math.max(0, Math.cos(k * x - om * t)), 6) * (x < R * 0.3 ? 1 : 0.35);
      if (crest > 0.05) g.glow(cx + x, cy + y, 12 + 12 * clamp(str, 0, 2), c.warm, crest * (0.35 + 0.35 * clamp(str, 0, 1.5)));
    }
    const lab = phone ? 11 : 13;
    g.label("rim: the push happens here", cx, cy - R * (1 + bd) - 26, { color: c.warm, size: lab, bg: true });
    g.label("incoming wave", W * 0.12, cy + R * 1.5, { color: c.neutron, size: lab, align: "left", bg: true });
    if (str > 0.05) g.label(phone ? "outgoing: nucleus left excited" : "outgoing circles: the nucleus left on an excited level", cx + R * 0.5, cy + R * 2.2, { color: c.soft, size: lab, bg: true });
    g.label(`push strength ∝ β²: ${str.toFixed(1)}× that at β = 0.20`, cx, H * 0.9, { color: c.ink, size: phone ? 13 : 16, weight: 600, serif: true, bg: true });
  }

  // ---------- scene 5: giant resonances, the whole nucleus moving ----------
  function modeF(mode, th, osc) { const ct = Math.cos(th); if (mode === "mono") return 1 + 0.13 * osc; if (mode === "quad") return 1 + 0.2 * osc * (3 * ct * ct - 1) / 2; return 1 + 0.2 * osc * (5 * ct ** 3 - 3 * ct) / 2; }
  function drawGiant(g, S) {
    const { W, H, c } = g; const phone = W < 600;
    const modes = ["mono", "quad", "oct"], short = ["breathing", "squash and stretch", "pear"];
    const cy = H * 0.36, base = Math.min(W * 0.11, H * 0.12);
    modes.forEach((m, i) => {
      const on = m === S.gr, cx = W * (0.2 + 0.3 * i), R = base * (on ? 1.3 : 0.85), osc = Math.sin(S.time * (on ? 4.2 : 2.6) + i);
      const al = on ? 1 : 0.5;
      if (on) g.glow(cx, cy, R * 2, c.warm, 0.18);
      const pts = []; for (let k = 0; k <= 90; k++) { const th = k / 90 * TAU, r = R * modeF(m, th, osc); pts.push([cx + Math.cos(th) * r, cy + Math.sin(th) * r]); }
      g.poly(pts, c.ink, on ? 2.2 : 1.4, al, null, true);
      const r = rng(31 + i); for (let k = 0; k < (on ? 44 : 26); k++) { const th = r() * TAU, rr = Math.sqrt(r()) * 0.86, f = modeF(m, th, osc); g.ball(cx + Math.cos(th) * rr * R * f, cy + Math.sin(th) * rr * R * f, R * (on ? 0.1 : 0.12), k % 2 ? c.proton : c.neutron, on ? 0.9 : 0.45); }
      // arrows showing the motion
      const arr = m === "mono" ? [0, 1.57, 3.14, 4.71] : m === "quad" ? [0, 3.14] : [0];
      arr.forEach((th) => { const s = osc > 0 ? 1 : -1, r1 = R * 1.25, r2 = R * (1.25 + 0.22 * s); g.arrow(cx + Math.cos(th) * r1, cy + Math.sin(th) * r1, cx + Math.cos(th) * r2, cy + Math.sin(th) * r2, c.soft, 1.4, al * 0.8, 6); });
      g.label(short[i], cx, cy + base * 1.3 * 1.45 + 16, { color: on ? c.ink : c.faint, size: phone ? 11 : 14, weight: on ? 600 : 500, serif: on });
    });
    const info = GR.find((x) => x.k === S.gr);
    g.label(info.name, W * 0.5, H * 0.08, { color: c.ink, size: phone ? 13 : 16, weight: 600, serif: true, bg: true });
    // secondary: where each sits in excitation energy, small humps on a faded floor
    const x0 = W * 0.1, x1 = W * 0.9, yB = H * 0.9, hT = H * 0.13, Emax = 32, X = (E) => lerp(x0, x1, E / Emax);
    g.line(x0, yB, x1, yB, c.line, 1.5);
    const humps = []; GR.forEach((gr) => { humps.push([gr.E, gr.G, gr.h, gr.k]); if (gr.E2) humps.push([gr.E2, gr.G2, gr.h2, gr.k]); });
    humps.forEach(([E, G, h, k]) => {
      const on = k === S.gr, sig = 0.42 * G, p = [[X(E - 3 * sig), yB]];
      for (let i = 0; i <= 60; i++) { const e = E - 3 * sig + 6 * sig * i / 60; p.push([X(e), yB - hT * h * Math.exp(-((e - E) ** 2) / (2 * sig * sig))]); }
      p.push([X(E + 3 * sig), yB]);
      if (on) g.area(p, c.warm, 0.3);
      g.poly(p.slice(1, -1), on ? c.warm : c.faint, on ? 2 : 1.2, on ? 1 : 0.7);
      if (on) g.label(`about ${E.toFixed(0)} MeV up`, X(E), yB - hT * h - 14, { color: c.warm, size: 12, bg: true });
    });
    g.line(X(4), yB, X(4), yB - hT * 0.8, c.faint, 1, 0.7, [3, 4]);
    g.label("last known level", X(4), yB - hT * 0.8 - 10, { color: c.faint, size: 11 });
    g.label("excitation energy (MeV) →", x1, yB + 14, { color: c.faint, size: 11, align: "right" });
  }

  // ---------- scene 6: direct capture ----------
  function drawCapture(g, S) {
    const { W, H, c } = g; const phone = W < 600;
    const x0 = W * 0.2, x1 = W * 0.8, yFree = H * 0.28, yFloor = H * 0.88;
    const xm = (x0 + x1) / 2, hw = (x1 - x0) / 2;
    const pts = []; for (let i = 0; i <= 80; i++) { const u = -1 + 2 * i / 80; const depth = 1 / (1 + Math.exp((Math.abs(u) - 0.78) / 0.07)); pts.push([xm + u * hw * 1.25, yFree + (yFloor - yFree) * depth]); }
    g.clip(0, 0, W, H);
    fground(g, pts, c.soft, 60, 0.28, 70); g.poly(pts, c.ink, 2);
    g.line(x0 - 30, yFree, x1 + 30, yFree, c.faint, 1.2, 0.9, [5, 5]); g.label("free: outside the nucleus", x0 - 30, yFree - 14, { color: c.faint, size: 12, align: "left" });
    // orbits: filled ones low, an empty one near the top
    const orbs = [0.9, 0.78, 0.66, 0.54, 0.4, 0.26];
    orbs.forEach((f, i) => { const y = yFree + (yFloor - yFree) * f; const empty = i >= 4; g.line(xm - hw * 0.55, y, xm + hw * 0.55, y, empty ? c.soft : c.line, empty ? 1.6 : 1.2, 0.9, empty ? [4, 4] : null); if (!empty) { g.ball(xm - 11, y - 7, 6.5, c.neutron); g.ball(xm + 11, y - 7, 6.5, c.neutron); } });
    g.label("empty orbit", xm + hw * 0.6, yFree + (yFloor - yFree) * 0.4, { color: c.soft, size: 12, align: "left" });
    // the incoming free wave above, then the drop
    const age = S.time - capT, P = 4;
    const t = age < 0 ? -1 : age % P;
    const yOrb = yFree + (yFloor - yFree) * 0.4 - 7;
    if (t >= 0) {
      const come = smooth(0, 1.2, t), drop = smooth(1.3, 2.0, t), gone = smooth(3.2, 4, t);
      const yArr = yFree - 40;
      // wave crests riding in from the right at height yArr
      if (drop < 1) for (let i = 0; i < 6; i++) { const x = x1 + 80 - i * 22 - come * (x1 + 80 - xm) + 0; g.line(x, yArr - 12, x, yArr + 12, c.neutron, 1.5, (1 - drop) * 0.5); }
      const y = lerp(yArr, yOrb, drop), x = lerp(x1 + 80, xm, come);
      g.ball(x, y, 8, c.neutron, 1 - gone * 0.3);
      if (drop > 0.2) { const u = smooth(0.2, 1, drop) * 0.7 + smooth(2, 3.2, t) * 0.3; const a = -0.9; g.photon(xm + 20 + Math.cos(a) * u * W * 0.32, yOrb - 10 + Math.sin(a) * u * H * 0.32, a, 28, 1 - gone); }
      if (drop > 0.5) g.label("drops straight in; a photon carries off the spare energy", xm, yFloor + 24, { color: c.ink, size: phone ? 12 : 15, serif: true, italic: true, alpha: smooth(0.5, 1, drop) * (1 - gone) });
    }
    g.restore();
  }

  // ---------- scene 7: a beam, three fates ----------
  const beam = [], ejecta = [], ghosts = []; let fates = [], beamAcc = 0, beamE = -1, nucGlow = 0, flashes = [];
  const bRand = rng(404);
  function shares(E) {
    const dir = clamp(0.015 + 0.06 * Math.log10(1 + E / 2), 0, 0.2) * (E > 0.8 ? 1 : 0);
    const pre = E < 1 ? 0 : clamp(0.42 * (1 - Math.exp(-(E - 1) / 14)), 0, 0.5);
    return [dir, pre, 1 - dir - pre];
  }
  const pick = (sh) => { const u = bRand(); return u < sh[0] ? 0 : u < sh[0] + sh[1] ? 1 : 2; };
  let seedReq = false;
  function seedBeam(S) { beamE = S.E; const sh = shares(S.E); fates = []; for (let i = 0; i < 30; i++) fates.push(pick(sh)); seedReq = true; nucGlow = 0.7; }
  function drawLedger(g, S, dt) {
    const { W, H, c } = g; const phone = W < 600;
    const E = S.E, sh = shares(E);
    if (Math.abs(E - beamE) > 1.5) { beamE = E; const keep = fates.slice(-6); fates = keep; }
    const cx = W * 0.5, cy = H * 0.36, R = Math.min(W, H) * 0.14, v = W * 0.42;
    if (seedReq) {   // open with neutrons already in flight, one of each fate
      seedReq = false; beam.length = 0; ejecta.length = 0;
      [[0.1, 0.3, 2], [0.25, -0.5, 2], [0.18, 1.0, 0], [0.33, 0.1, 1], [0.05, -0.2, 2]].forEach(([fx, fb, f]) => beam.push({ x: W * fx, y: cy + fb * R, b: fb * R, f, st: 0, vy: 0, vx: v }));
      beam.push({ x: cx + R * 1.6, y: cy - R * 1.5, b: -R, f: 0, st: 1, vy: -v * 0.32, vx: v * 0.88 });
      ejecta.push({ x: cx + R * 1.8, y: cy + R * 0.5, vx: v * 1.8, vy: v * 0.4, pro: true });
    }
    for (let k = -1; k <= 1; k++) g.line(0, cy + k * R * 0.9, cx - R * 1.6, cy + k * R * 0.9, c.faint, 1, 0.25, [2, 8]);
    // spawn
    beamAcc += dt; while (beamAcc > 0.22) { beamAcc -= 0.22; if (beam.length < 24) { const f = pick(sh), s = bRand() < 0.5 ? -1 : 1; const b = f === 0 ? s * R * (0.92 + 0.2 * bRand()) : s * R * 0.7 * bRand(); beam.push({ x: -10, y: cy + b, b, f, st: 0, vy: 0, vx: v }); } }
    nucGlow *= Math.exp(-dt * 0.6);
    for (let i = beam.length - 1; i >= 0; i--) {
      const p = beam[i]; p.x += p.vx * dt; p.y += p.vy * dt; (p.tr || (p.tr = [])).push([p.x, p.y]); if (p.tr.length > 90) p.tr.shift();
      const contact = cx - Math.sqrt(Math.max(0, R * R - p.b * p.b * 0.8));
      if (p.st === 0 && p.x >= contact) {
        if (p.f === 0) { p.st = 1; p.vy = Math.sign(p.b) * v * 0.32; p.vx = v * 0.88; flashes.push({ x: p.x, y: p.y, t: S.time }); fates.push(0); }
        else if (p.f === 1) { p.st = 2; const ang = (bRand() - 0.5) * 1.2; ejecta.push({ x: p.x + R * 0.2, y: p.y, vx: Math.cos(ang) * v * 1.9, vy: Math.sin(ang) * v * 1.9, pro: bRand() < 0.45 }); nucGlow = Math.min(1.5, nucGlow + 0.08); fates.push(1); }
        else { p.st = 3; p.tx = cx + (bRand() - 0.5) * R * 0.6; p.ty = cy + (bRand() - 0.5) * R * 0.6; }
      }
      if (p.st === 2) { ghosts.push({ tr: p.tr, t: S.time, col: c.neutron }); beam.splice(i, 1); continue; }
      if (p.st === 3) { p.vx = 0; p.x += (p.tx - p.x) * Math.min(1, dt * 6); p.y += (p.ty - p.y) * Math.min(1, dt * 6); if (Math.hypot(p.tx - p.x, p.ty - p.y) < 2) { nucGlow = Math.min(1.5, nucGlow + 0.25); fates.push(2); ghosts.push({ tr: p.tr, t: S.time, col: c.neutron }); beam.splice(i, 1); continue; } }
      if (p.x > W + 20 || p.y < -20 || p.y > H + 20) { ghosts.push({ tr: p.tr, t: S.time, col: c.neutron }); beam.splice(i, 1); }
    }
    for (let i = ejecta.length - 1; i >= 0; i--) { const e = ejecta[i]; e.x += e.vx * dt; e.y += e.vy * dt; (e.tr || (e.tr = [[e.x, e.y]])).push([e.x, e.y]); if (e.x > W + 20 || e.y < -20 || e.y > H + 20) { ghosts.push({ tr: e.tr, t: S.time, col: e.pro ? c.proton : c.neutron }); ejecta.splice(i, 1); } }
    for (let i = ghosts.length - 1; i >= 0; i--) { const a = 1 - (S.time - ghosts[i].t) / 1.6; if (a <= 0 || ghosts.length > 40) { ghosts.splice(i, 1); continue; } g.poly(ghosts[i].tr, ghosts[i].col, 1.4, 0.35 * a); }
    beam.forEach((p) => p.tr && g.poly(p.tr, c.neutron, 1.4, 0.35)); ejecta.forEach((e) => e.tr && g.poly(e.tr, e.pro ? c.proton : c.neutron, 1.4, 0.4));
    if (fates.length > 60) fates = fates.slice(-60);
    // draw: nucleus glowing with the swallowed energy
    g.nucleus(cx, cy, R, { N: 56, Z: 26, seed: 9, t: S.time, jiggle: 0.5, heat: 1 + nucGlow * 1.5, halo: c.warm, haloAlpha: 0.08 + nucGlow * 0.35 });
    for (let i = flashes.length - 1; i >= 0; i--) { const f = flashes[i], a = 1 - (S.time - f.t) / 0.6; if (a <= 0) { flashes.splice(i, 1); continue; } g.glow(f.x, f.y, 16, c.warm, 0.6 * a); }
    beam.forEach((p) => { for (let k = 1; k < 6; k++) g.dot(p.x - p.vx * 0.012 * k, p.y - p.vy * 0.012 * k, 4 - k * 0.5, c.neutron, 0.22 - k * 0.03); g.ball(p.x, p.y, 5, c.neutron); });
    ejecta.forEach((e) => { const col = e.pro ? c.proton : c.neutron; for (let k = 1; k < 8; k++) g.dot(e.x - e.vx * 0.01 * k, e.y - e.vy * 0.01 * k, 4 - k * 0.4, col, 0.3 - k * 0.035); g.ball(e.x, e.y, 5, col); });
    // the three piles, built from the fates seen (last 60)
    const names = phone ? ["direct", "fast (pre-eq.)", "compound"] : ["direct: grazed, flew on", "fast collision: one out at once", "compound: swallowed"];
    const cnt = [0, 0, 0]; fates.forEach((f) => cnt[f]++);
    const yb = H * 0.84, dr = phone ? 3 : 5, per = phone ? 7 : 8;
    for (let k = 0; k < 3; k++) {
      const px = W * (0.2 + 0.3 * k);
      for (let n = 0; n < cnt[k]; n++) { const row = Math.floor(n / per), col = n % per; g.dot(px + (col - (per - 1) / 2) * dr * 2.4, yb - dr - row * dr * 2.4, dr, k === 2 ? c.ink : c.soft, 0.85); }
      g.line(px - per * dr * 1.3, yb + 2, px + per * dr * 1.3, yb + 2, c.line, 2);
      g.label(names[k], px, yb + 16, { color: c.ink, size: phone ? 10.5 : 12, weight: 600 });
      g.label(phone ? `${fates.length ? Math.round(100 * cnt[k] / fates.length) : 0}% (model ${Math.round(sh[k] * 100)}%)` : `${fates.length ? Math.round(100 * cnt[k] / fates.length) : 0}% seen · model ${Math.round(sh[k] * 100)}%`, px, yb + 32, { color: c.soft, size: phone ? 10 : 11 });
    }
    g.label(`${E.toFixed(1)} MeV neutrons on a medium-mass nucleus (illustrative shares)`, W * 0.5, H * 0.07, { color: c.faint, size: phone ? 10.5 : 12, bg: true });
  }
})();
