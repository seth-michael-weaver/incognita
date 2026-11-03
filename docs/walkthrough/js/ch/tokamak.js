/* Chapter 31 (part three, Advanced): a magnetic bottle. Physics explanation (no INCOGNITA computation). Scenes:
 *   "gyro"  = charged particles in a uniform field B (along x), moved by the Boris pusher, drawn in 3D perspective that
 *             the reader turns by dragging. Lengths are in units of the gyro-radius at 5 T and time is slowed by a
 *             different factor per species, so the geometry (radius ~ 1/B, pitch / radius = 2 pi v_par / v_perp) is exact.
 *             Readout: rho = sqrt(2 m E) / (|q| B) for the whole speed across the field, f = |q| B / (2 pi m).
 *   "torus" = a torus (aspect ratio ~3) with one field line on a flux surface winding at safety factor q: the poloidal
 *             angle advances 2 pi / q per toroidal turn. Each pass through the cut (phi = 0) leaves a dot on the
 *             cross-section: a Poincare section. Rational q = m/n closes after m toroidal turns.
 *   "map"   = the tokamap (Balescu, Vlad & Spineanu, Phys. Rev. E 58 (1998) 951), an area-preserving map for field lines:
 *             psi' = psi - (K/2pi) psi'/(1+psi') sin(theta) (solved exactly as a quadratic),
 *             theta' = theta + 2 pi W(psi') - (K/2pi) cos(theta) / (1+psi')^2, W = 1/q = (1/4)(2-psi)(2-2psi+psi^2),
 *             so q runs from 1 on the axis to 4 at psi = 1. Radius on the picture: sqrt(psi). K = 0: nested surfaces;
 *             K > 0: island chains at rational q (2, 3/2, 3, ...), then a chaotic edge. Lines with psi > 1 are lost. */
(function () {
  const { TAU, clamp, lerp, smooth, rng } = WT.util;
  const QE = 1.602176634e-19;
  const SPECIES = {
    d: { lab: "deuteron 10 keV", m: 3.3436e-27, q: 1, E: 1e4, key: "warm" },
    a: { lab: "alpha 3.5 MeV", m: 6.6447e-27, q: 2, E: 3.5e6, key: "alpha" },
    e: { lab: "electron 10 keV", m: 9.1094e-31, q: -1, E: 1e4, key: "neutron" },
  };
  const rhoOf = (sp, B) => Math.sqrt(2 * sp.m * sp.E * QE) / (Math.abs(sp.q) * QE * B);
  const fmtLen = (m) => (m >= 0.01 ? (m * 100).toFixed(m >= 0.1 ? 0 : 1) + " cm" : m >= 1e-3 ? (m * 1000).toFixed(1) + " mm" : (m * 1e6).toFixed(0) + " µm");
  const sup = (n) => String(n).replace(/-/g, "⁻").replace(/\d/g, (d) => "⁰¹²³⁴⁵⁶⁷⁸⁹"[d]);
  const sci = (v) => { const e = Math.floor(Math.log10(v)); return `${(v / 10 ** e).toFixed(1)}·10${sup(e)}`; };

  // ---------- 3D camera ----------
  function cam(S, W, H, scale, cx, cy, D = 6) {
    const cy_ = Math.cos(S.yaw), sy = Math.sin(S.yaw), cp = Math.cos(S.pitch), sp = Math.sin(S.pitch);
    return (x, y, z) => {
      const X = x * cy_ - z * sy, Z0 = x * sy + z * cy_;           // yaw about the vertical axis
      const Y = y * cp - Z0 * sp, Z = y * sp + Z0 * cp;              // pitch
      const k = D / (D + Z); return [cx + X * scale * k, cy - Y * scale * k, Z, k];
    };
  }
  function grabRotate(g, S, mode) {
    let last = null;
    WT.grab(g.ctx.canvas, {
      down(x, y) { if (S.mode !== mode) return false; last = [x, y]; S.touched = true; return true; },
      move(x, y) { if (!last) return; S.yaw += (x - last[0]) * 0.008; S.pitch = clamp(S.pitch + (y - last[1]) * 0.006, -1.2, 1.2); last = [x, y]; },
      up() { last = null; }, cancel() { last = null; },
      hover() { g.ctx.canvas.style.cursor = S.mode === mode ? "grab" : "default"; },
    });
  }

  // ---------- scene 1: gyration ----------
  const parts = []; let partsSp = null;
  function initParts(sp) {
    parts.length = 0; partsSp = sp; const r = rng(21);
    for (let i = 0; i < 14; i++) {
      const al = 0.35 + 1.1 * r(), ph = r() * TAU, sgn = Math.sign(SPECIES[sp].q);
      parts.push({ x: -6 + 12 * r(), y: (r() - 0.5) * 5, z: (r() - 0.5) * 5, vx: Math.cos(al) * (r() < 0.5 ? 1 : -1) * 0.45, vy: Math.sin(al) * Math.cos(ph), vz: Math.sin(al) * Math.sin(ph), sgn, trail: [] });
    }
  }
  /** Boris push in a uniform field along x; b = omega dt (signed by the charge). */
  function boris(p, b) {
    const t = Math.tan(b / 2), s = (2 * t) / (1 + t * t);
    const vy1 = p.vy + p.vz * t, vz1 = p.vz - p.vy * t;            // v' = v + v x t  (t along x)
    p.vy += vz1 * s; p.vz -= vy1 * s;                                // v+ = v + v' x s
  }

  // ---------- scene 2: one field line on a torus ----------
  const R0 = 1, A0 = 0.36, RS = 0.27;
  const tor = { q: -1, phi: 0, pts: [], cuts: [], th0: 0.4 };
  function ratOf(q) { for (let m = 1; m <= 7; m++) { const n = Math.round(q * m); if (Math.abs(q - n / m) < 0.006 / m) return [n, m]; } return null; }

  // ---------- scene 3: the tokamap ----------
  const Wq = (p) => 0.25 * (2 - p) * (2 - 2 * p + p * p);
  function tmap(s, K) {
    const k = K / TAU, P = 1 - s.p + k * Math.sin(s.t), pn = 0.5 * (-P + Math.sqrt(P * P + 4 * s.p));
    s.t = s.t + TAU * Wq(pn) - (k * Math.cos(s.t)) / ((1 + pn) * (1 + pn)); s.p = pn;
  }
  const mp = { K: -1, lines: [], acc: null, lost: 0, n: 0 };
  function psiOfQ(q) { let lo = 0, hi = 1; for (let i = 0; i < 40; i++) { const m = (lo + hi) / 2; if (1 / Wq(m) < q) lo = m; else hi = m; } return (lo + hi) / 2; }

  WT.chapter("tokamak", {
    num: "Chapter 31", title: "Magnetic confinement", short: "Confinement",
    lead: "No wall can touch a 100-million-degree gas. A magnetic field can hold it, because charged particles cannot cross field lines.",
    html: `
<div class="step">
  <h3>Gyration in a magnetic field</h3>
  <p>Across the field a charge can only circle; along it, it slides. Drag the picture to turn it.</p>
  <div class="ctl"><label for="tk-b">Field B (tesla)</label><input id="tk-b" type="range" data-bind="B" min="1" max="12" step="0.1" value="5"><output data-show="B" data-fmt="1"></output></div>
  <div class="btns tk-sp"><button class="btn ghost" data-act="spd" aria-pressed="true">Deuteron</button> <button class="btn ghost" data-act="spa" aria-pressed="false">Alpha</button> <button class="btn ghost" data-act="spe" aria-pressed="false">Electron</button></div>
  <div class="formula">ρ = √(2mE) / (|q| B)</div>
</div>
<div class="step">
  <h3>Toroidal field lines and the safety factor</h3>
  <p>A straight field has open ends, so bend it into a ring and twist it: a tokamak. Each lap leaves a dot where the line crosses the cut.</p>
  <div class="ctl"><label for="tk-q">Safety factor q</label><input id="tk-q" type="range" data-bind="q" min="1" max="4" step="0.01" value="2.62" data-instant><output data-show="q" data-fmt="2"></output></div>
  <div class="btns"><button class="btn ghost" data-act="q32">q = 3/2</button> <button class="btn ghost" data-act="q2">q = 2</button> <button class="btn ghost" data-act="qg">q = golden</button></div>
</div>
<div class="step">
  <h3>Magnetic islands and field-line chaos</h3>
  <p>Ripples in the field tear the surfaces into islands where q is a simple fraction, then into chaos. Click to start a field line.</p>
  <div class="ctl"><label for="tk-k">Perturbation K</label><input id="tk-k" type="range" data-bind="K" min="0" max="6" step="0.05" value="1.5" data-instant><output data-show="K" data-fmt="2"></output></div>
  <div class="formula">ψ′ = ψ − (K/2π) ψ′/(1+ψ′) sin θ<br>θ′ = θ + 2π/q(ψ′) − (K/2π) cos θ/(1+ψ′)²</div>
</div>`,
    setup(S) {
      S.set("mode", "gyro"); S.set("B", 5); S.set("q", 2.62); S.set("K", 1.5); S.yaw = -0.55; S.pitch = 0.35; S.sp = "d";
      const pick = (k) => () => { S.sp = k; document.querySelectorAll(".tk-sp .btn").forEach((b) => b.setAttribute("aria-pressed", String(b.dataset.act === "sp" + k))); };
      S.on("spd", pick("d")); S.on("spa", pick("a")); S.on("spe", pick("e"));
      const setq = (v) => () => { S.set("q", v); const i = document.getElementById("tk-q"); if (i) i.value = v; };
      S.on("q32", setq(1.5)); S.on("q2", setq(2)); S.on("qg", setq(1.618034));
    },
    steps: [
      (S) => { S.set("mode", "gyro"); S.yaw = -0.55; S.pitch = 0.35; },
      (S) => { S.set("mode", "torus"); S.yaw = 0.2; S.pitch = 0.75; },
      (S) => { S.set("mode", "map"); },
    ],
    frame(g, S, dt) {
      if (S.mode === "gyro") drawGyro(g, S, dt);
      else if (S.mode === "torus") drawTorus(g, S, dt);
      else drawMap(g, S, dt);
    },
  });

  function drawGyro(g, S, dt) {
    const { W, H, c } = g, phone = W < 600, sp = SPECIES[S.sp], col = c[sp.key];
    grabRotate(g, S, "gyro");
    if (partsSp !== S.sp) initParts(S.sp);
    if (!S.touched) S.yaw += dt * 0.05;
    const scale = Math.min(W * 0.075, H * 0.085), P = cam(S, W, H, scale, W * 0.5, H * 0.5, 30);
    // field lines: a 5 x 5 bundle along x
    for (let i = -1; i <= 1; i++) for (let j = -1; j <= 1; j++) {
      const a = P(-7, i * 2.2, j * 2.2), b = P(7, i * 2.2, j * 2.2); g.line(a[0], a[1], b[0], b[1], c.soft, 1, 0.16 + 0.08 * a[3]);
      const m = P(4.5, i * 2.2, j * 2.2), m2 = P(5, i * 2.2, j * 2.2); if (!i && !j) g.arrow(m[0], m[1], m2[0], m2[1], c.soft, 1.4, 0.6, 7);
    }
    { const m = P(6.2, 0, 0); g.label("B", m[0], m[1] - 14, { color: c.ink, size: 14, weight: 700, serif: true, italic: true }); }
    // push the particles: omega in display units ~ B (radius 1 at 5 T for the whole speed across the field)
    const b = S.B / 5, sub = 6, h = (dt * 2.2) / sub;
    for (const p of parts) {
      for (let k = 0; k < sub; k++) { boris(p, p.sgn * b * h); p.x += p.vx * h; p.y += (p.vy * h) * 1; p.z += p.vz * h; }
      // the guiding centre does not move across B; the radius follows v_perp / omega
      if (p.x > 7) { p.x -= 14; p.trail = []; } if (p.x < -7) { p.x += 14; p.trail = []; }
      p.trail.push([p.x, p.y, p.z]); if (p.trail.length > 320) p.trail.shift();
    }
    // depth-sorted drawing: trails then heads
    const heads = parts.map((p) => ({ p, s: P(p.x, p.y, p.z) })).sort((u, v) => v.s[2] - u.s[2]);
    for (const { p } of heads) { const pts = p.trail.map((q) => P(q[0], q[1], q[2])); for (let i = 1; i < pts.length; i++) g.line(pts[i - 1][0], pts[i - 1][1], pts[i][0], pts[i][1], col, 1.8 * pts[i][3], 0.08 + 0.75 * (i / pts.length)); }
    for (const { s } of heads) { g.glow(s[0], s[1], 12 * s[3], col, 0.35); g.ball(s[0], s[1], 5 * s[3], col); }
    // scale bar: 1 display unit = rho at 5 T
    const rho5 = rhoOf(sp, 5), rho = rhoOf(sp, S.B), bx = phone ? 16 : 30, by = H - (phone ? 18 : 30);
    g.line(bx, by, bx + scale, by, c.ink, 2); g.line(bx, by - 4, bx, by + 4, c.ink, 1.5); g.line(bx + scale, by - 4, bx + scale, by + 4, c.ink, 1.5);
    g.label(WT.dec(fmtLen(rho5)), bx + scale + 8, by, { color: c.ink, size: 12, align: "left", raw: true });
    const f = (Math.abs(sp.q) * QE * S.B) / (TAU * sp.m);
    g.label(WT.trf("{a} · ρ up to {b} · {c} turns a second", WT.trf(sp.lab), fmtLen(rho), sci(f)), W / 2, phone ? 14 : 24, { color: c.ink, size: phone ? 12 : 14, weight: 600, bg: true, raw: true });
    g.label(sp.q < 0 ? WT.trf("negative: turns the other way") : WT.trf("time slowed {a}×", sci(f / (0.35 * S.B / 5))), W / 2, phone ? 32 : 46, { color: c.faint, size: 11, raw: true });
  }

  function drawTorus(g, S, dt) {
    const { W, H, c } = g, phone = W < 600, ctx = g.ctx;
    grabRotate(g, S, "torus");
    if (!S.touched) S.yaw += dt * 0.06;
    const q = S.q;
    if (Math.abs(q - tor.q) > 1e-6) { tor.q = q; tor.phi = 0; tor.pts = []; tor.cuts = []; }
    const cx = phone ? W * 0.5 : W * 0.37, cyy = phone ? H * 0.4 : H * 0.5, scale = Math.min(W * (phone ? 0.34 : 0.235), H * (phone ? 0.28 : 0.34));
    const P = cam(S, W, H, scale, cx, cyy);
    const pt = (phi, th, r) => { const R = R0 + r * Math.cos(th); return P(R * Math.cos(phi), r * Math.sin(th), R * Math.sin(phi)); };
    // wireframe: poloidal rings and toroidal circles, faded by depth
    for (let i = 0; i < 28; i++) { const phi = (i / 28) * TAU, pts = []; for (let j = 0; j <= 30; j++) pts.push(pt(phi, (j / 30) * TAU, A0)); g.poly(pts, c.soft, 1, 0.07 + 0.12 * pts[0][3] * (pts[0][2] < 0 ? 1.4 : 0.6)); }
    for (let j = 0; j < 8; j++) { const th = (j / 8) * TAU, pts = []; for (let i = 0; i <= 80; i++) pts.push(pt((i / 80) * TAU, th, A0)); g.poly(pts, c.soft, 1, 0.12); }
    // the cut at phi = 0: a translucent disc
    { const pts = []; for (let j = 0; j <= 40; j++) pts.push(pt(0, (j / 40) * TAU, A0 * 1.12)); g.area(pts, c.cool, 0.12); g.poly(pts, c.cool, 1.2, 0.6); }
    // trace the line: theta = th0 + phi / q
    const speed = 7, steps = 60, dphi = (speed * dt) / steps;
    for (let k = 0; k < steps && tor.cuts.length < 400; k++) {
      const before = Math.floor(tor.phi / TAU); tor.phi += dphi; const after = Math.floor(tor.phi / TAU);
      const th = tor.th0 + tor.phi / q; tor.pts.push([tor.phi, th]); if (tor.pts.length > 2600) tor.pts.shift();
      if (after > before) tor.cuts.push(tor.th0 + (after * TAU) / q);
    }
    const linePts = tor.pts.map(([phi, th]) => pt(phi, th, RS));
    for (let i = 1; i < linePts.length; i++) { const a = linePts[i - 1], b = linePts[i]; g.line(a[0], a[1], b[0], b[1], c.photon, 2 * b[3], (0.15 + 0.85 * (i / linePts.length)) * (b[2] < 0 ? 1 : 0.55)); }
    const head = linePts[linePts.length - 1]; if (head) { g.glow(head[0], head[1], 16, c.photon, 0.6); g.ball(head[0], head[1], 4.5, c.photon); }
    tor.cuts.forEach((th, i) => { const p = pt(0, th, RS); g.dot(p[0], p[1], 2.6, c.warm, 0.5 + 0.5 * (i / tor.cuts.length)); });
    // the cross-section, flat (the Poincare section)
    const sr = phone ? Math.min(W * 0.17, H * 0.17) : Math.min(W * 0.15, H * 0.2), sx = phone ? W - sr - 18 : W * 0.83, sy = phone ? H * 0.8 : H * 0.42;
    g.dot(sx, sy, sr * 1.05, c.card, 0.9); g.ring(sx, sy, sr, c.soft, 1.2, 0.6); g.ring(sx, sy, (sr * RS) / A0, c.soft, 1, 0.3, [3, 4]);
    tor.cuts.forEach((th, i) => { const r = (sr * RS) / A0; g.dot(sx + r * Math.cos(th), sy - r * Math.sin(th), 3.2, c.warm, 0.45 + 0.55 * (i / tor.cuts.length)); });
    g.label("the cut, flat", sx, sy - sr - 14, { color: c.soft, size: 11 });
    const rat = ratOf(q), laps = tor.cuts.length;
    g.label(rat ? `q = ${rat[0]}/${rat[1]}: closes after ${rat[1]} lap${rat[1] > 1 ? "s" : ""}` : `q = ${q.toFixed(2)}: no simple fraction, the dots fill the circle`, W / 2, phone ? 14 : 24, { color: c.ink, size: phone ? 12 : 14, weight: 600, bg: true });
    g.label(`laps ${laps}`, sx, sy + sr + 16, { color: c.soft, size: 11 });
  }

  function drawMap(g, S, dt) {
    const { W, H, c } = g, phone = W < 600, ctx = g.ctx;
    const R = Math.min(W * (phone ? 0.44 : 0.4), H * (phone ? 0.42 : 0.4)), cx = W * 0.5, cy = H * (phone ? 0.5 : 0.52);
    const dpr = Math.min(2, window.devicePixelRatio || 1), aw = Math.round(2 * R * dpr) + 4;
    if (!mp.acc || mp.acc.width !== aw) { mp.acc = document.createElement("canvas"); mp.acc.width = mp.acc.height = aw; mp.K = -1; }
    const actx = mp.acc.getContext("2d");
    const palette = [c.cool, c.neutron, c.alpha, c.proton, c.warm, c.photon, c.fission];
    const reset = () => { mp.K = S.K; actx.clearRect(0, 0, aw, aw); mp.lost = 0; mp.n = 0;
      const keep = mp.lines.filter((l) => l.user).map((l) => ({ p: l.p0, t: l.t0, p0: l.p0, t0: l.t0, user: true, col: l.col, it: 0, lost: false }));
      mp.lines = []; for (let i = 0; i < 26; i++) { const p0 = 0.012 + (i / 25) * 0.97; mp.lines.push({ p: p0, t: 0.3, p0, t0: 0.3, col: palette[Math.floor((i / 26) * palette.length)], it: 0, lost: false }); }
      mp.lines.push(...keep); };
    if (Math.abs(S.K - mp.K) > 1e-6) reset();
    WT.grab(ctx.canvas, {
      down(x, y) { if (S.mode !== "map") return false; const dx = (x - cx) / R, dy = -(y - cy) / R, p = dx * dx + dy * dy; if (p > 1.15) return false;
        mp.lines.push({ p: Math.max(1e-4, p), t: Math.atan2(dy, dx), p0: Math.max(1e-4, p), t0: Math.atan2(dy, dx), col: c.ink, it: 0, lost: false, user: true, born: S.time }); if (mp.lines.filter((l) => l.user).length > 8) mp.lines.splice(mp.lines.findIndex((l) => l.user), 1); return false; },
      hover(x, y) { ctx.canvas.style.cursor = S.mode === "map" && Math.hypot(x - cx, y - cy) < R * 1.07 ? "crosshair" : "default"; },
    });
    // iterate: a few hundred map steps per frame, each one a dot on the section
    const per = dt > 0 ? 24 : 0, s = aw / 2 - 2;
    for (const l of mp.lines) {
      if (l.lost || l.it > 3000) continue;
      actx.fillStyle = l.col; actx.globalAlpha = l.user ? 0.95 : 0.7;
      for (let k = 0; k < per; k++) {
        tmap(l, S.K); l.it++; mp.n++;
        if (l.p > 1.0) { l.lost = true; mp.lost++; break; }
        const r = Math.sqrt(l.p); actx.fillRect(aw / 2 + r * Math.cos(l.t) * s - 0.6 * dpr, aw / 2 - r * Math.sin(l.t) * s - 0.6 * dpr, 1.3 * dpr, 1.3 * dpr);
      }
    }
    actx.globalAlpha = 1;
    // the vessel and the section
    g.glow(cx, cy, R * 1.25, c.cool, 0.1); g.dot(cx, cy, R * 1.03, c.card, 0.75);
    ctx.drawImage(mp.acc, cx - aw / dpr / 2, cy - aw / dpr / 2, aw / dpr, aw / dpr);
    g.ring(cx, cy, R, c.soft, 1.6, 0.7); g.label("edge: q = 4 · lines that cross it are lost", cx, cy + R + 16, { color: c.soft, size: 11, bg: true });
    [[2, "q = 2"], [3, "q = 3"]].forEach(([qq, lab]) => { const r = Math.sqrt(psiOfQ(qq)) * R; g.ring(cx, cy, r, c.ink, 1, 0.25, [3, 5]); g.label(lab, cx + r * 0.71 + 4, cy - r * 0.71 - 4, { color: c.ink, size: 11, weight: 600, align: "left", bg: true }); });
    g.dot(cx, cy, 3, c.ink); g.label("axis, q = 1", cx, cy + 14, { color: c.soft, size: 10 });
    mp.lines.filter((l) => l.user && S.time - l.born < 1.2).forEach((l) => { const r = Math.sqrt(l.p0) * R; g.glow(cx + r * Math.cos(l.t0), cy - r * Math.sin(l.t0), 26, c.photon, 0.8 * (1 - (S.time - l.born) / 1.2)); });
    g.label(`K ${S.K.toFixed(2)} · field lines lost to the wall: ${mp.lost}`, W / 2, phone ? 14 : 24, { color: c.ink, size: phone ? 12 : 14, weight: 600, bg: true });
  }
})();
