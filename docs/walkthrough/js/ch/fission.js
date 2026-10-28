/* Chapter 12: fission (fission/). Scenes (S.mode):
 *   "drop"   = a charged liquid drop stretched by the reader until it necks and splits;
 *   "path"   = the deformation-energy landscape (one liquid-drop hill, then the shell-carved double hump);
 *   "tunnel" = a nucleus at excitation E tunnelling the inner hump; Hill-Wheeler parabola vs the real shape (WKB);
 *   "gates"  = transition states on the hilltop as gates, continuum above them;
 *   "series" = two humps in series, T = Ta Tb / (Ta + Tb), a stream of flux knocking on both doors;
 *   "chance" = multi-chance fission down the neutron-emission chain, and the staircase it leaves in sigma_f.
 * Shapes follow fission/wkb.py (deformation path, T = 1/(1+exp 2K)), fission/barriers.py (thill, t1barrier),
 * fission/transmission.py (nfisbar == 2 combination) and fission/chain.py (every residual has its own barriers).
 * Numbers are illustrative (U-238-like: inner hump 6.0 MeV, outer 5.6 MeV, hbar-omega 0.8 MeV). */
(function () {
  const { TAU, clamp, lerp, smooth, rng } = WT.util;
  const HW = 0.8, B_IN = 6.0, B_OUT = 5.6;
  const X_IN = 0.34, X_OUT = 0.66, X_GS = 0.12, X_W2 = 0.5;
  const CP_LD = [[0, 0], [0.55, 6.8], [1, -7]];
  function herm(cp, x) {
    x = clamp(x, 0, 1); let i = 0; while (i < cp.length - 2 && x > cp[i + 1][0]) i++;
    const [x0, y0] = cp[i], [x1, y1] = cp[i + 1], t = (x - x0) / (x1 - x0); return y0 + (y1 - y0) * t * t * (3 - 2 * t);
  }
  const cpShell = (bout) => [[0, 2.5], [X_GS, 0], [X_IN, B_IN], [X_W2, 2.6], [X_OUT, bout], [0.82, 2.0], [1, -7]];
  function Vof(S, x) { const vs = herm(cpShell(S.Bb ?? B_OUT), x); const m = S.shellMix ?? 1; return m > 0.999 ? vs : lerp(herm(CP_LD, x), vs, m); }
  const snap = () => document.body.classList.contains("shot");
  const thill = (e, b) => 1 / (1 + Math.exp(clamp(-TAU * (e - b) / HW, -80, 80)));
  const fmtT = (T) => (T >= 0.01 ? T.toFixed(2) : T.toExponential(1).replace("e-", "·10⁻"));
  /** WKB through the inner hump along the real landscape; the scale is fixed so a parabola would give Hill-Wheeler exactly. */
  function wkbT(S, E) {
    if (E >= B_IN) return thill(E, B_IN);
    const h = 0.004, k = Math.abs((Vof(S, X_IN + h) - 2 * Vof(S, X_IN) + Vof(S, X_IN - h)) / (h * h));
    const c = Math.sqrt(2 * k) / HW; let K = 0; const n = 160, dx = (X_W2 - X_GS) / n;
    for (let i = 0; i <= n; i++) { const v = Vof(S, X_GS + i * dx) - E; if (v > 0) K += Math.sqrt(v) * dx * (i === 0 || i === n ? 0.5 : 1); }
    return 1 / (1 + Math.exp(Math.min(80, 2 * c * K)));
  }
  function turning(S, E) { let xa = X_IN, xb = X_IN; for (let x = X_GS; x < X_IN; x += 0.002) if (Vof(S, x) > E) { xa = x; break; } for (let x = X_IN; x < X_W2; x += 0.002) if (Vof(S, x) <= E) { xb = x; break; } return [xa, xb]; }

  // ---------- the drop: packed nucleons, stretched, necked and torn apart by one parameter d ----------
  const NB = 96, base = [];
  { const r = rng(11); for (let i = 0; i < NB; i++) { const a = i * 2.39996 + r() * 0.3, rr = Math.sqrt((i + 0.5) / NB) * 0.9; base.push([rr * Math.cos(a), rr * Math.sin(a), r(), r() < 0.39]); } base.sort((a, b) => a[2] - b[2]); }
  function drop(g, cx, cy, R, d, t, alpha = 1, heat = 1) {
    const sx = 1 + 1.3 * d, sy = 1 - 0.4 * d, n = smooth(0.42, 0.92, d), sep = smooth(0.84, 1, d) * 0.55, rb = R / Math.sqrt(NB) * 1.05;
    for (const [px, py, ph, isP] of base) {
      let X = px * sx; const neck = 1 - 0.96 * n * Math.exp(-(X * X) / 0.1); let Y = py * sy * neck;
      X += Math.sign(X) * sep * (1 - Math.exp(-Math.abs(X) * 4));
      X += Math.sin(t * 3 + ph * 20) * 0.012 * heat; Y += Math.cos(t * 2.6 + ph * 17) * 0.012 * heat;
      g.ball(cx + X * R, cy + Y * R, rb, isP ? g.c.proton : g.c.neutron, alpha);
    }
  }

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

  const GATES = [[0, "0⁺"], [0.2, "2⁻"], [0.42, "1⁻"], [0.6, "0⁺"], [0.8, "3⁻"], [1.0, "2⁺"]];
  const FECONT = 1.22;
  const dots = []; let spawnAcc = 0; const tally = { through: 0, back: 0 };

  WT.chapter("fission", {
    num: "Chapter 12", title: "Splitting", short: "Fission",
    lead: "The heaviest nuclei have an exit lighter ones lack: instead of throwing out one particle, the whole nucleus tears in two. This is fission.",
    html: `
<div class="step">
  <p>A heavy nucleus behaves like a drop of charged liquid. Surface tension (grey arrows) pulls it round; the protons, all positively charged, push it apart (red arrows). For uranium the two nearly balance.</p>
  <div class="ctl"><label for="fis-d">Stretch the drop</label><input id="fis-d" type="range" data-bind="def" min="0" max="1" step="0.01" value="0"><output data-show="def" data-fmt="2"></output></div>
  <p>Drag to stretch it and watch the dot on the small energy curve below. Stretching adds surface, which costs energy, but spreads the charge, which releases energy. Past the top of the curve the charge wins: a neck forms and the halves fly apart with about 200 MeV.</p>
</div>
<div class="step">
  <h3>The landscape of shapes</h3>
  <p>The curve is the energy for every shape, from round (left) to split (right). A smooth liquid drop gives one hill, but nucleons fill energy levels in groups, called <b>shells</b>, and in the heaviest elements this carves a well into it: a <b>double-humped barrier</b>, where the nucleus can linger in a stretched shape.</p>
  <p>The engine does not assume this curve: it reads it point by point from a microscopic calculation of the energy at each deformation (amount of stretch).</p>
</div>
<div class="step">
  <h3>Tunnelling through the hill</h3>
  <p>The ball is the excited nucleus in the first valley, at the excitation energy of the orange dashed line, below the 6 MeV hilltop. Classically it can never cross; quantum mechanics lets it <b>tunnel</b> through the darker, forbidden part, with a chance <i>T</i> that falls exponentially as that part thickens.</p>
  <div class="ctl"><label for="fis-e">Excitation energy</label><input id="fis-e" type="range" data-bind="E" min="3" max="8" step="0.05" value="5"><output data-show="E" data-fmt="2"></output></div>
  <p>Raise the energy and watch <i>T</i> climb as the forbidden part thins. The textbook shortcut (Hill–Wheeler) treats the hilltop as a parabola (blue dashed). The engine follows the real shape, wider lower down, so far below the top its chance is smaller. <i>K</i> measures how much hill is in the way.</p>
  <div class="formula">T = 1 / (1 + e<sup>2K</sup>),  K = ∫ √(2μ(V−E)) dβ / ħ</div>
</div>
<div class="step">
  <h3>Gates on the hilltop</h3>
  <p>The doors on the hilltop are the <b>transition states</b>, the quantum states of the nucleus stretched over the barrier. Each has a spin and parity (0⁺, 2⁻, …) and acts as a gate; its lit gap shows how open it is. A nucleus passes only through gates matching its own spin and parity, and each opens gradually as the energy passes its height.</p>
  <div class="ctl"><label for="fis-e2">Excitation energy</label><input id="fis-e2" type="range" data-bind="E" min="3" max="8" step="0.05" value="5"><output data-show="E" data-fmt="2"></output></div>
  <div class="btns"><button class="btn ghost" data-act="jpAll">Any spin</button><button class="btn ghost" data-act="jp0">Compound 0⁺</button><button class="btn ghost" data-act="jp1">Compound 1⁻</button></div>
  <p>Pick one spin and parity: only matching gates count, and the total opening drops. Higher up, the gates crowd into a <b>continuum</b>, and the engine counts them by their density, as it does for ordinary levels.</p>
</div>
<div class="step">
  <h3>Two hills in series</h3>
  <p>Now both hills, each with a gate (the circle; its filled part is how open it is). Nuclei arrive from the left; those that cross the first hill are trapped in the well, bouncing between the gates until they leave one way or the other. The chances combine like resistors in series, so the harder hill mostly decides.</p>
  <div class="ctl"><label for="fis-b">Outer hill height</label><input id="fis-b" type="range" data-bind="Bb" min="3.5" max="7.5" step="0.05" value="5.6"><output data-show="Bb" data-fmt="2"></output></div>
  <div class="formula">1/T = 1/T<sub>A</sub> + 1/T<sub>B</sub></div>
  <p>Drag the outer hill up and watch the flow to fission choke, however open the inner gate is.</p>
</div>
<div class="step">
  <h3>More than one chance</h3>
  <p>Uranium-238 absorbs the neutron and becomes uranium-239 with excitation <i>E</i>* (dashed line). If it does not split, it may emit a neutron instead; the line drops, and the uranium-238 left behind, still hot, tries its own barrier: <b>second-chance</b> fission, (n,n′f). The piles collect how each nucleus ended.</p>
  <div class="ctl"><label for="fis-en">Neutron energy</label><input id="fis-en" type="range" data-bind="En" min="0" max="25" step="0.1" value="7"><output data-show="En" data-fmt="1"></output></div>
  <p>Raise the energy and later attempts start to succeed; a third chance opens near 12 MeV. Each new chance shows up as a step in the measured <b>fission cross section</b>, how likely the nucleus is to split: the small graph at the top right draws those steps, with your energy marked. The engine computes how often it splits, not which pieces it splits into.</p>
  <div class="aside">In the code: <code>fission/wkb.py</code> (the deformation-energy path and the WKB integrals), <code>fission/barriers.py</code> (Hill–Wheeler, transition states, the barrier level density), <code>fission/transmission.py</code> (humps in series, T<sub>fis</sub> per spin and parity), <code>fission/chain.py</code> (barriers for every nucleus of the cascade).</div>
</div>`,
    setup(S) {
      S.set("mode", "drop"); S.to("def", 0, true); S.to("E", 5, true); S.to("Bb", B_OUT, true); S.to("En", 7, true); S.to("shellMix", 0, true);
      S.set("jp", "all"); S.rngS = rng(5);
      S.on("jpAll", () => S.set("jp", "all")); S.on("jp0", () => S.set("jp", "0⁺")); S.on("jp1", () => S.set("jp", "1⁻"));
    },
    steps: [
      (S) => { S.set("mode", "drop"); S.to("shellMix", 0, snap()); },
      (S) => { S.set("mode", "path"); S.to("shellMix", 1, snap()); S.to("Bb", B_OUT, snap()); },
      (S) => { S.set("mode", "tunnel"); S.to("shellMix", 1, snap()); S.to("Bb", B_OUT, snap()); S.to("E", 5, snap()); },
      (S) => { S.set("mode", "gates"); S.to("shellMix", 1, snap()); S.to("Bb", B_OUT, snap()); S.to("E", 6.5, snap()); },
      (S) => { S.set("mode", "series"); S.to("shellMix", 1, snap()); tally.through = 0; tally.back = 0; S.tallyBb = S.target.Bb; },
      (S) => { S.set("mode", "chance"); S.to("shellMix", 1, snap()); S.to("Bb", B_OUT, snap()); },
    ],
    frame(g, S, dt) {
      if (S.mode === "drop") sceneDrop(g, S);
      else if (S.mode === "path") scenePath(g, S);
      else if (S.mode === "tunnel") sceneTunnel(g, S);
      else if (S.mode === "gates") sceneGates(g, S);
      else if (S.mode === "series") sceneSeries(g, S, dt);
      else sceneChance(g, S);
    },
  });

  // ---------- shared landscape frame ----------
  function frameOf(g, o = {}) {
    const { W, H } = g; const x0 = W * (o.x0 ?? 0.05), x1 = W * (o.x1 ?? 0.97), yTop = H * (o.yTop ?? 0.1), yBot = H * (o.yBot ?? 0.76);
    const vMin = o.vMin ?? -7, vMax = o.vMax ?? 9, bMin = o.bMin ?? 0, bMax = o.bMax ?? 1;
    return { vMin, vMax, X: (x) => x0 + (x1 - x0) * (x - bMin) / (bMax - bMin), Y: (v) => yBot - (yBot - yTop) * (v - vMin) / (vMax - vMin), x0, x1, yTop, yBot, bMin, bMax };
  }
  function landscape(g, S, F, color, depth = 170) {
    const pts = []; for (let i = 0; i <= 240; i++) { const x = F.bMin + (F.bMax - F.bMin) * i / 240; pts.push([F.X(x), F.Y(Vof(S, x))]); }
    fground(g, pts, color, depth, 0.3, 80); g.poly(pts, g.c.ink, 2.2); return pts;
  }

  // ---------- scene: the drop ----------
  function sceneDrop(g, S) {
    const { W, H, c } = g, d = S.def, fs = W < 600 ? 11 : 13, cx = W * 0.5, cy = H * 0.42, R = Math.min(W, H) * (W < 600 ? 0.17 : 0.2);
    const heat = 1 + smooth(0.84, 1, d) * 2; g.glow(cx, cy, R * (1.5 + d), c.warm, 0.08 + 0.1 * smooth(0.5, 1, d));
    drop(g, cx, cy, R, d, S.time, 1, heat);
    const sx = R * (1 + 1.3 * d), sy = R * (1 - 0.4 * d), sep = smooth(0.84, 1, d) * 0.55 * R;
    for (let i = 0; i < 10; i++) { const a = i / 10 * TAU + 0.3, ex = Math.cos(a) * (sx + sep + 36), ey = Math.sin(a) * (sy + 36); g.arrow(cx + ex, cy + ey, cx + Math.cos(a) * (sx + sep + 14), cy + Math.sin(a) * (sy + 14), c.soft, 1.4, 0.5, 6); }
    const cl = 24 + 28 * d; g.arrow(cx + sx + sep + 6, cy, cx + sx + sep + 6 + cl, cy, c.proton, 2.2, 0.9); g.arrow(cx - sx - sep - 6, cy, cx - sx - sep - 6 - cl, cy, c.proton, 2.2, 0.9);
    g.label("surface tension pulls it round", cx, cy - sy - 60, { color: c.soft, size: fs, bg: true });
    g.label("the protons push it apart", cx, cy + sy + 58, { color: c.proton, size: fs, bg: true });
    const cap = d < 0.3 ? "a charged drop, nearly round" : d < 0.6 ? "stretched: more surface, charge further apart" : d < 0.88 ? "a neck forms" : "two fragments, carrying about 200 MeV";
    g.label(cap, cx, H * 0.78, { color: c.ink, size: fs + 3, weight: 600, serif: true });
    // the drop's energy along the way, a small hill below
    const F = frameOf(g, { x0: 0.25, x1: 0.75, yTop: 0.85, yBot: 0.97, vMin: -7, vMax: 8 });
    const pts = []; for (let i = 0; i <= 100; i++) pts.push([F.X(i / 100), F.Y(herm(CP_LD, i / 100))]);
    fground(g, pts, c.soft, 40, 0.25, 50); g.poly(pts, c.soft, 1.5, 0.8);
    g.dot(F.X(d), F.Y(herm(CP_LD, d)), 5, c.warm); g.label("energy of the drop", F.x0 - 10, F.Y(2), { color: c.faint, size: fs - 1, align: "right" });
  }

  // ---------- scene: the landscape ----------
  function scenePath(g, S) {
    const { W, H, c } = g, fs = W < 600 ? 11 : 13, F = frameOf(g);
    landscape(g, S, F, c.soft);
    const m = S.shellMix;
    const lab = (x, v, s, dy, col) => g.label(s, F.X(x), F.Y(v) + dy, { color: col || c.soft, size: fs, bg: true });
    if (m > 0.6) { lab(X_GS, 0, "ground state", 22); lab(X_IN, B_IN, "inner barrier", -18); lab(X_W2, 2.6, "second well", 22); lab(X_OUT, S.Bb, "outer barrier", -18); lab(0.93, -4.5, "split (scission)", -18); }
    else lab(0.55, 6.8, "one smooth hill", -18);
    if (m > 0.3 && m < 0.98) g.label("shell effects carving the second well", F.X(X_W2), F.yTop + 10, { color: c.fission, size: fs, bg: true, alpha: Math.sin(m * Math.PI) });
    // a marker drop rolling along the road, showing the shape at each point
    const u = (S.time * 0.07) % 1, R = Math.min(W, H) * 0.055;
    const px = F.X(u), py = F.Y(Vof(S, u)) - R * 1.5 - 14;
    drop(g, px, py, R, u, S.time, 0.95, 0.6); g.line(px, py + R, px, F.Y(Vof(S, u)) - 4, c.faint, 1, 0.6, [3, 3]);
    g.label("round → stretched → necked → split", W * 0.5, F.yBot + 30, { color: c.ink, size: fs + 2, serif: true, italic: true });
    g.label("stretch (deformation) →", F.x1, F.yBot + (g.W < 600 ? 52 : 30), { color: c.faint, size: fs - 1, align: "right" });
  }

  // ---------- scene: tunnelling ----------
  function sceneTunnel(g, S) {
    const { W, H, c } = g, fs = W < 600 ? 11 : 13, F = frameOf(g), E = S.E;
    landscape(g, S, F, c.soft);
    const over = E >= B_IN, T = wkbT(S, E), Thw = thill(E, B_IN), [xa, xb] = turning(S, E);
    const ey = F.Y(E);
    if (!over) {
      const poly = [[F.X(xa), ey]]; for (let x = xa; x <= xb; x += 0.004) poly.push([F.X(x), F.Y(Vof(S, x))]); poly.push([F.X(xb), ey]);
      g.area(poly, c.ink, 0.14);
      const fx = F.X((xa + xb) / 2), fy = ey - Math.min(10, (ey - F.Y(B_IN)) * 0.3), lx = F.X(xa) - 34, ly = F.Y(B_IN) - 4;
      g.line(fx, fy, lx + 4, ly + 8, c.soft, 1, 0.7); g.label("forbidden zone", lx, ly, { color: c.ink, size: fs - 1, align: "right", bg: true });
    }
    g.line(F.X(0.02), ey, F.X(over ? 1 : xa), ey, c.warm, 1.5, 0.8, [6, 4]);
    g.label(`excitation ${E.toFixed(2)} MeV`, F.X(0.02), ey + 16, { color: c.warm, size: fs, align: "left", bg: true });
    g.label(`hilltop ${B_IN.toFixed(1)} MeV`, F.X(X_IN), F.Y(B_IN) - 18, { color: c.soft, size: fs, bg: true });
    // the parabola Hill-Wheeler fits to the top
    const k = 2 * (B_IN - Vof(S, X_IN + 0.06)) / (0.06 * 0.06), par = []; for (let x = X_IN - 0.11; x <= X_IN + 0.11; x += 0.005) par.push([F.X(x), F.Y(B_IN - 0.5 * k * (x - X_IN) ** 2)]);
    g.poly(par, c.accent, 1.4, 0.8, [4, 4]); g.label("parabola fit", F.X(X_IN + 0.1), F.Y(B_IN - 0.5 * k * 0.01) + 4, { color: c.accent, size: fs - 1, align: "left", bg: true });
    // the nucleus: rolls to the hill, reflects or tunnels
    const P = 3.4, u = (S.time % P) / P, aT = clamp(0.1 + 0.9 * Math.pow(T, 0.25), 0.1, 1);
    const ballAt = (x, a, glow) => { const y = Math.min(ey, F.Y(Vof(S, x))) - 9; g.ball(F.X(x), y, 9, c.neutron, a); if (glow) g.glow(F.X(x), y, 22, c.warm, 0.4 * a); };
    if (over) { const x = u < 0.5 ? lerp(X_GS, X_IN, smooth(0, 0.5, u)) : lerp(X_IN, 1, smooth(0.5, 1, u)); ballAt(x, 1 - smooth(0.9, 1, u), true); }
    else {
      if (u < 0.4) ballAt(lerp(X_GS, xa, smooth(0, 0.4, u)), 1, true);
      else ballAt(lerp(xa, X_GS, smooth(0.4, 0.95, u)), 1 - aT * 0.6, false);
      if (u >= 0.4) { const x = u < 0.62 ? lerp(xa, xb, (u - 0.4) / 0.22) : lerp(xb, 1, smooth(0.62, 1, u)); ballAt(x, aT * (1 - smooth(0.92, 1, u)), u > 0.62); }
    }
    const msg = over ? "passes over the top" : W < 600 ? `T ≈ ${fmtT(T)} real shape · ${fmtT(Thw)} parabola` : `chance to tunnel T ≈ ${fmtT(T)} on the real shape, ${fmtT(Thw)} on the parabola`;
    g.label(msg, W * 0.5, F.yBot + 30, { color: c.ink, size: W < 600 ? 12 : 15, weight: 600, serif: true });
  }

  // ---------- scene: gates on the hilltop ----------
  function sceneGates(g, S) {
    const { W, H, c } = g, fs = W < 600 ? 11 : 13, E = S.E, phone = W < 600;
    const F = frameOf(g, { x0: 0.04, x1: 0.96, yTop: 0.08, yBot: 0.8, vMin: 1.6, vMax: 9.8, bMin: 0.19, bMax: 0.5 });
    landscape(g, S, F, c.soft, 90);
    const ax = F.X(X_IN), sp = Math.min(W * 0.12, 74), dh = Math.min(48, sp * 0.95, (F.Y(0) - F.Y(1)) * 0.75);
    // continuum: lines crowding upward above fecont, fading out before the top of the stage
    const fc = B_IN + FECONT, half = sp * 3.4;
    for (let i = 0; i < 46; i++) {
      const e = fc + 2.4 * Math.pow(i / 46, 0.7); if (e > F.vMax - 0.15) break;
      const fade = 1 - smooth(F.vMax - 1.2, F.vMax - 0.15, e), open = E > e ? 1 : thill(E, e);
      g.line(ax - half, F.Y(e), ax + half, F.Y(e), c.fission, 1, (0.15 + 0.45 * open) * fade);
    }
    g.label(phone ? "continuum: a density" : "continuum of gates: counted as a density", ax, F.Y(fc + 1.1), { color: c.fission, size: fs, bg: true });
    // the gates: one door per transition state, standing at its own height on the hilltop
    let open = 0;
    GATES.forEach(([e, jp], i) => {
      const x = ax + (i - (GATES.length - 1) / 2) * sp, y = F.Y(B_IN + e), T = thill(E, B_IN + e), ok = S.jp === "all" || jp === S.jp;
      if (ok) open += T;
      g.line(x - sp * 0.42, y, x + sp * 0.42, y, c.soft, 1.5, ok ? 0.8 : 0.3);
      g.door(x, y, dh, T, c.fission, jp, { alpha: ok ? 1 : 0.28, size: fs - 1 });
    });
    if (!phone) g.label("gates: transition states", ax - 3.1 * sp, F.Y(B_IN + 0.5) - dh * 0.5, { color: c.fission, size: fs, align: "right", bg: true });
    let cont = 0; for (let e = fc; e < fc + 4; e += 0.02) cont += 3 * Math.exp((e - fc) / 0.4) * thill(E, e) * 0.02;
    const ey = F.Y(clamp(E, F.vMin, F.vMax)); g.line(F.x0, ey, F.x1, ey, c.warm, 1.5, 0.85, [6, 4]);
    g.label(phone ? `E = ${E.toFixed(2)} MeV` : `excitation ${E.toFixed(2)} MeV`, phone ? F.x0 : F.x1, ey - 13, { color: c.warm, size: fs, align: phone ? "left" : "right", bg: true });
    g.label(`hilltop ${B_IN.toFixed(1)} MeV`, ax, F.Y(B_IN) + dh * 0.5 + 22, { color: c.soft, size: fs, bg: true });
    const who = S.jp === "all" ? "all gates" : `${S.jp} gates only`;
    g.label(`${who}: total opening ${open.toFixed(2)}` + (cont > 0.005 ? ` + ${cont.toFixed(2)} from the continuum` : ""), W * 0.5, H * 0.9, { color: c.ink, size: W < 600 ? 12 : 15, weight: 600, serif: true, bg: true });
  }

  // ---------- scene: two humps in series ----------
  function sceneSeries(g, S, dt) {
    const { W, H, c } = g, fs = W < 600 ? 11 : 13, F = frameOf(g), E = 5.8;
    const Ta = thill(E, B_IN), Tb = thill(E, S.Bb), T = Ta * Tb / (Ta + Tb);
    if (Math.abs(S.target.Bb - (S.tallyBb ?? -1)) > 1e-6) { S.tallyBb = S.target.Bb; tally.through = 0; tally.back = 0; }   // a new hill: count afresh
    landscape(g, S, F, c.soft);
    const ey = F.Y(E); g.line(F.X(0), ey, F.X(X_OUT), ey, c.warm, 1.2, 0.5, [6, 4]);
    // doors: an aperture at each hilltop whose open area is T
    const door = (x, T, name) => { const px = F.X(x), py = Math.min(ey, F.Y(Vof(S, x))) - 9; g.ring(px, py, 13, c.ink, 1.4, 0.8); g.dot(px, py, 13 * Math.sqrt(T), c.fission, 0.85); g.label(`${name} ≈ ${fmtT(T)}`, px, py - 26, { color: c.ink, size: fs, bg: true }); };
    door(X_IN, Ta, "inner gate T"); door(X_OUT, Tb, "outer gate T");
    // the stream
    spawnAcc += dt; while (spawnAcc > 0.09) { spawnAcc -= 0.09; if (dots.length < 90) dots.push({ x: 0, v: 0.3, z: 0 }); }
    const r = S.rngS;
    for (const d of dots) {
      d.x += d.v * dt;
      if (d.z === 0 && d.v > 0 && d.x >= X_IN) { if (r() < Ta) d.z = 1; else d.v = -d.v; }
      else if (d.z === 1 && d.v > 0 && d.x >= X_OUT) { if (r() < Tb) { d.z = 2; tally.through++; } else d.v = -d.v; }
      else if (d.z === 1 && d.v < 0 && d.x <= X_IN) { if (r() < Ta) { d.z = 0; tally.back++; } else d.v = -d.v; }
      if (d.z === 2) d.v = Math.min(0.7, d.v + dt * 0.5);
    }
    for (let i = dots.length - 1; i >= 0; i--) if (dots[i].x < -0.02 || dots[i].x > 1.04) dots.splice(i, 1);
    for (const d of dots) {
      const yv = F.Y(Vof(S, d.x)), inside = yv < ey;                 // inside a hill: the energy line runs through it (tunnelling)
      const y = (d.z === 2 && !inside ? Math.max(ey, yv - 7) : ey - 4) + Math.sin(d.x * 60) * 1.5;
      g.dot(F.X(d.x), y, 3.4, d.z === 2 ? c.fission : d.z === 1 ? c.warm : c.neutron, inside ? 0.45 : 0.9); if (d.z === 2) g.glow(F.X(d.x), y, 10, c.fission, 0.35);
    }
    g.label("nuclei arriving →", F.X(0.01), ey - 14, { color: c.neutron, size: fs, align: "left", bg: true });
    g.label("trapped in the well", F.X(X_W2), F.Y(2.6) + 24, { color: c.warm, size: fs, bg: true });
    g.label("fission", Math.min(F.X(0.9), W - 34), F.Y(-3) + 20, { color: c.fission, size: fs, bg: true });
    g.label(`both hills: T ≈ ${fmtT(T)}, ${(100 * T).toFixed(T < 0.01 ? 2 : 0)} % of what arrives gets through`, W * 0.5, F.yBot + 30, { color: c.ink, size: W < 600 ? 12 : 15, weight: 600, serif: true });
    g.label(`so far: ${tally.through} through, ${tally.back} turned back`, W * 0.5, F.yBot + 52, { color: c.faint, size: fs - 1 });
  }

  // ---------- scene: multi-chance fission, one nucleus at a time ----------
  const PF = 0.62;  // illustrative fission share when the barrier is wide open (vs neutron emission)
  const CH = [{ name: "²³⁹U*", Sn: 4.8, B: 6.2, lab: "1st chance (n,f)" }, { name: "²³⁸U*", Sn: 6.15, B: 6.0, lab: "2nd chance (n,n′f)" }, { name: "²³⁷U*", Sn: 5.1, B: 6.2, lab: "3rd chance (n,2nf)" }];
  // kinetic energy an evaporated neutron takes (MeV): the slow end of the spectrum, which sets where each new chance
  // starts (measured: the 2nd chance near 6 MeV, the 3rd near 12 MeV); never more than half of what is left above S_n,
  // so the nucleus left behind always has E* > 0. A neutron can leave only when E* is above its separation energy.
  const EPS = 0.7;
  function chances(En) { const out = []; let ex = CH[0].Sn + En; for (let k = 0; k < 3; k++) { const f = smooth(CH[k].B - 1.6, CH[k].B + 0.8, ex), spare = ex - CH[k].Sn; out.push({ ex, f, canEmit: spare > 0.05 }); ex = spare > 0.05 ? spare - Math.min(EPS, 0.5 * spare) : 0; } return out; }
  /** The chance that a nucleus splits at all (first, second or third chance): the shape of the fission cross section. */
  function pFis(En) { const ch = chances(En); let alive = 1, p = 0; for (let k = 0; k < 3; k++) { const q = ch[k]; p += alive * PF * q.f; alive *= 1 - PF * q.f; if (!(q.canEmit && k < 2)) break; } return p; }
  /** One nucleus's history: list of {k, out: "fis" | "emit" | "gamma"}. */
  function history(En, r) { const ch = chances(En), h = []; for (let k = 0; k < 3; k++) { const q = ch[k]; if (r() < PF * q.f) { h.push({ k, out: "fis" }); return h; } if (q.canEmit && k < 2) h.push({ k, out: "emit" }); else { h.push({ k, out: "gamma" }); return h; } } return h; }
  const chRand = rng(2024); let piles = [0, 0, 0, 0], pileEn = -1, hist = null;
  function resultOf(h) { const l = h[h.length - 1]; return l.out === "fis" ? l.k : 3; }
  function seedPiles(En) { piles = [0, 0, 0, 0]; for (let i = 0; i < 40; i++) piles[resultOf(history(En, chRand))]++; pileEn = En; }
  function sceneChance(g, S) {
    const { W, H, c } = g, fs = W < 600 ? 11 : 13, En = S.En, phone = W < 600, ch = chances(En);
    if (Math.abs(En - pileEn) > 0.4) { seedPiles(En); hist = null; }
    if (!hist) hist = { h: history(En, chRand), t0: S.time, i: 0, ti: S.time };
    const F = frameOf(g, { x0: 0.05, x1: 0.95, yTop: 0.1, yBot: 0.6, vMin: -7, vMax: 14 });
    landscape(g, S, F, c.soft, 80);
    // the current attempt
    const st = hist.h[hist.i], q = ch[st.k], dur = { fis: 3.0, emit: 2.6, gamma: 2.4 }[st.out], u = (S.time - hist.ti) / dur;
    let ex = q.ex;
    if (st.out === "emit" && u > 0.55) ex = lerp(q.ex, ch[st.k + 1].ex, smooth(0.55, 0.85, u));
    const ey = F.Y(clamp(ex, F.vMin, F.vMax));
    const [xa] = turning(S, Math.min(ex, B_IN - 0.01)), xTop = ex >= B_IN ? X_IN : xa;
    let bx = X_GS, ba = 1;
    const climb = smooth(0, 0.35, u);
    if (st.out === "fis") { bx = u < 0.35 ? lerp(X_GS, xTop, climb) : lerp(xTop, 0.9, smooth(0.35, 0.7, u)); if (ex < B_IN && u > 0.35 && u < 0.6) ba = 0.55; }
    else bx = u < 0.35 ? lerp(X_GS, xTop, climb) : lerp(xTop, X_GS, smooth(0.35, 0.55, u));
    g.line(F.X(0.02), ey, F.X(0.62), ey, c.warm, 1.4, 0.8, [6, 4]); g.line(F.X(bx), ey, F.X(bx), F.Y(Vof(S, bx)) - 18, c.warm, 1, 0.35, [2, 3]);
    g.label(`${CH[st.k].name}  E* = ${ex.toFixed(1)} MeV`, F.X(0.02), ey - 14, { color: c.warm, size: fs, align: "left", bg: true });
    const by = F.Y(Vof(S, bx)) - 9;
    if (ex > F.vMax) g.label(`↑ E* above the picture`, F.X(0.3), F.yTop - 4, { color: c.warm, size: fs - 1, bg: true });
    const split = st.out === "fis" ? smooth(0.7, 0.85, u) : 0;
    if (split < 0.05) { g.glow(F.X(bx), by, 24, c.warm, 0.35); g.ball(F.X(bx), by, 9, c.neutron, ba); }
    else { const d = split * 46 + (u - 0.85) * 60; g.glow(F.X(0.9), by, 30, c.fission, 0.5 * (1 - smooth(0.9, 1, u))); g.ball(F.X(0.9) - d, by - d * 0.4, 7, c.fission); g.ball(F.X(0.9) + d * 0.7, by + d * 0.2, 6, c.fission); if (u > 0.75) g.label("fission!", F.X(0.9), by - 30, { color: c.fission, size: fs + 1, weight: 600, bg: true }); }
    if (st.out === "emit" && u > 0.5) { const v = smooth(0.5, 1, u); g.ball(F.X(X_GS) + v * W * 0.18, by - v * H * 0.25, 6, c.neutron, 1 - smooth(0.85, 1, u)); if (u < 0.9) g.label("emits a neutron, cools, tries again", F.X(X_GS) + 30, by - 40 - v * 20, { color: c.neutron, size: fs, align: "left", bg: true }); }
    if (st.out === "gamma" && u > 0.45) { const v = smooth(0.45, 1, u); g.photon(F.X(X_GS) + 20 + v * W * 0.2, by - v * H * 0.2, -0.8, 24, 1 - v); g.label("too cool to split: a photon, no fission", F.X(X_GS) + 30, by - 44, { color: c.soft, size: fs, align: "left", bg: true }); }
    g.label(`attempt ${st.k + 1}: barrier ${(100 * q.f).toFixed(0)} % open`, F.X(X_IN), F.Y(B_IN) - 22, { color: c.ink, size: fs, bg: true });
    if (u >= 1) { hist.i++; hist.ti = S.time; if (hist.i >= hist.h.length) { piles[resultOf(hist.h)]++; hist = null; } }
    // piles of outcomes, built from the nuclei fired
    const names = phone ? ["1st (n,f)", "2nd (n,n′f)", "3rd (n,2nf)", "no fission"] : [CH[0].lab, CH[1].lab, CH[2].lab, "no fission"];
    const tot = piles.reduce((a, b) => a + b, 0), yb = H * 0.86, dr = phone ? 2.6 : 4.2, per = phone ? 6 : 7, mxRows = Math.floor(H * 0.17 / (dr * 2.3));
    const capN = per * mxRows, mxP = Math.max(...piles), psc = mxP > capN ? capN / mxP : 1;   // a full pile shrinks them all alike
    for (let k = 0; k < 4; k++) {
      const px = W * (0.13 + 0.245 * k), n = piles[k], show = Math.round(n * psc), col = k < 3 ? c.fission : c.soft;
      for (let m = 0; m < show; m++) g.dot(px + (m % per - (per - 1) / 2) * dr * 2.3, yb - dr - Math.floor(m / per) * dr * 2.3, dr, col, 0.85);
      g.line(px - per * dr * 1.2, yb + 2, px + per * dr * 1.2, yb + 2, c.line, 2);
      g.label(names[k], px, yb + 16, { color: c.ink, size: phone ? 10 : 12, weight: 600 });
      g.label(`${n} · ${tot ? Math.round(100 * n / tot) : 0}%`, px, yb + 31, { color: c.soft, size: phone ? 10 : 11 });
    }
    // the staircase: the chance to split at each neutron energy (the fission cross section's shape), with the slider's energy marked
    const gx0 = W * (phone ? 0.6 : 0.68), gx1 = W * 0.95, gy0 = H * 0.08, gy1 = H * (phone ? 0.23 : 0.26);
    const GX = (e) => gx0 + (gx1 - gx0) * e / 25, GY = (p) => gy1 - (gy1 - gy0) * p;
    const sp = []; for (let i = 0; i <= 125; i++) { const e = i * 0.2; sp.push([GX(e), GY(pFis(e))]); }
    g.line(gx0, gy1, gx1, gy1, c.line, 1); g.line(gx0, gy1, gx0, gy0, c.line, 1);
    g.area([[gx0, gy1], ...sp, [gx1, gy1]], c.fission, 0.12); g.poly(sp, c.fission, 2);
    g.line(GX(clamp(En, 0, 25)), gy1, GX(clamp(En, 0, 25)), gy0, c.warm, 1, 0.7, [3, 3]); g.dot(GX(clamp(En, 0, 25)), GY(pFis(En)), 4, c.warm);
    g.label(phone ? "chance to split" : "chance to split vs neutron energy", gx0, gy0 - 10, { color: c.ink, size: phone ? 10 : 12, weight: 600, align: "left" });
    g.label("0", gx0, gy1 + 10, { color: c.faint, size: 10 }); g.label("25 MeV", gx1, gy1 + 10, { color: c.faint, size: 10, align: "right" });
    if (!phone) { g.label("2nd", GX(6.3), GY(pFis(9)) - 10, { color: c.fission, size: 10 }); g.label("3rd", GX(12.6), GY(pFis(15)) - 10, { color: c.fission, size: 10 }); }
  }
})();
