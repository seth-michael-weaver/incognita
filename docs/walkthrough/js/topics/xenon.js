/* Xenon poisoning. Scenes (S.mode):
 *   "up"   = start-up of a clean core at power P: iodine and xenon build to equilibrium (about two days);
 *   "pit"  = shutdown from equilibrium at power P; the reader scrubs the hours after shutdown (the "xenon pit");
 *   "live" = the same equations run live (3 h per second): shut down, try to restart, change power;
 *   "osc"  = two loosely coupled halves of a large core: spatial xenon oscillation after a rod push.
 * Equations (per unit Sigma_f, so x = sigma_X X / Sigma_f and y = sigma_X I / Sigma_f are dimensionless):
 *   dy/dt = gamma_I s p - lambda_I y,   dx/dt = gamma_X s p + lambda_I y - (lambda_X + s p) x,   s = sigma_X phi_0,
 *   xenon worth rho_X = -x / nu (one-group: k = nu Sigma_f / (Sigma_a + sigma_X X) with nu Sigma_f = Sigma_a at critical).
 * Constants: I-135 half-life 6.57 h, Xe-135 half-life 9.14 h, cumulative I-135 yield 6.39 % and direct Xe-135 yield 0.23 %
 * (U-235 thermal fission, ENDF/B), sigma_X = 2.65e6 b (thermal, 2200 m/s), nu = 2.43.
 * Illustrative: full-power thermal flux phi_0 = 5e13 n/cm2/s (typical light-water-reactor order) giving an equilibrium worth
 * of -2.35 % and a peak of about -6.2 % some 9 h after shutdown from full power; the 4 % "spare reactivity" line (what the
 * rods and boron can still give back) is illustrative; real values depend on the core and the time in the cycle.
 * Oscillation model (illustrative): power shares p_L,R = 1 +/- a with tilt a = 0.6 tanh(G (rho_L - rho_R)/0.6), G growing
 * with core size (weaker coupling between the halves); it gives a period of about 25 h, damped for small G, growing for large. */
(function () {
  const { TAU, clamp, lerp, smooth, rng } = WT.util;
  const LI = Math.LN2 / 6.57, LX = Math.LN2 / 9.14, GI = 0.0639, GX = 0.0023, NU = 2.43, SX = 2.65e-18 * 5e13 * 3600; // per hour
  const MARGIN = 4.0; // % spare reactivity (illustrative)
  const r = rng(31);
  const eqY = (p) => GI * SX * p / LI, eqX = (p) => (GI + GX) * SX * p / (LX + SX * p);
  const pc = (x) => 100 * x / NU; // xenon worth in % (magnitude)
  function step(st, p, h) { // explicit midpoint step, h in hours
    const dy = GI * SX * p - LI * st.y, dx = GX * SX * p + LI * st.y - (LX + SX * p) * st.x;
    const y1 = st.y + dy * h / 2, x1 = st.x + dx * h / 2;
    st.y += (GI * SX * p - LI * y1) * h; st.x += (GX * SX * p + LI * y1 - (LX + SX * p) * x1) * h;
  }
  function adv(st, p, H) { const n = Math.max(1, Math.ceil(H / 0.05)); for (let i = 0; i < n; i++) step(st, p, H / n); }
  // ---------- precomputed curves ----------
  let upC = null, pitC = null;
  function upCurve(P) { if (upC && upC.P === P) return upC; const st = { x: 0, y: 0 }, pts = [[0, 0, 0]]; for (let i = 1; i <= 240; i++) { adv(st, P / 100, 0.25); pts.push([i * 0.25, pc(st.x), st.y]); } return (upC = { P, pts }); }
  function pitCurve(P) {
    if (pitC && pitC.P === P) return pitC; const p = P / 100, st = { x: eqX(p), y: eqY(p) }, pts = [];
    for (let i = -48; i < 0; i++) pts.push([i * 0.25, pc(st.x), st.y]);
    let pk = 0, tp = 0, a = -1, b = -1;
    for (let i = 0; i <= 288; i++) { if (i) adv(st, 0, 0.25); const v = pc(st.x); pts.push([i * 0.25, v, st.y]); if (v > pk) { pk = v; tp = i * 0.25; } if (v > MARGIN && a < 0) a = i * 0.25; if (v > MARGIN) b = i * 0.25; }
    return (pitC = { P, pts, pk, tp, a, b });
  }
  const at = (C, t) => { const p = C.pts, t0 = p[0][0], k = clamp((t - t0) / 0.25, 0, p.length - 1), i = Math.floor(k), j = Math.min(p.length - 1, i + 1), f = k - i; return [lerp(p[i][1], p[j][1], f), lerp(p[i][2], p[j][2], f)]; };
  // ---------- live run ----------
  const live = { t: 0, x: 0, y: 0, p: 1, on: true, hist: [], msg: "", msgT: -9, init: false, rod: 0 };
  function liveReset(S) { const p = S.P / 100; live.t = 0; live.x = eqX(p); live.y = eqY(p); live.p = p; live.on = true; live.hist = [[0, pc(live.x), p]]; live.init = true; }
  // ---------- oscillation ----------
  const osc = { t: 0, L: { x: 0, y: 0 }, R: { x: 0, y: 0 }, a: 0, hist: [], push: -1, init: false, side: 1 };
  function oscReset() { const p = 1; osc.t = 0; osc.L = { x: eqX(p), y: eqY(p) }; osc.R = { x: eqX(p), y: eqY(p) }; osc.a = 0; osc.hist = [[0, 0]]; osc.push = 0; osc.init = true; }
  function oscStep(S, H) {
    const G = 12 * S.wd, n = Math.max(1, Math.ceil(H / 0.05)), h = H / n;
    for (let i = 0; i < n; i++) {
      const rod = osc.push >= 0 && osc.t - osc.push < 2 ? -0.003 * osc.side : 0;
      const d = (osc.R.x - osc.L.x) / NU + rod; osc.a = 0.6 * Math.tanh(G * d / 0.6);
      step(osc.L, 1 + osc.a, h); step(osc.R, 1 - osc.a, h); osc.t += h;
      const lh = osc.hist[osc.hist.length - 1]; if (!lh || osc.t - lh[0] >= 0.25) osc.hist.push([osc.t, osc.a]);
    }
    while (osc.hist.length > 2 && osc.hist[1][0] < osc.t - 100) osc.hist.shift();
  }
  const LAY = { drag: false, used: false };
  const inBox = (b, x, y, pad = 0) => b && x >= b.x - pad && x <= b.x + b.w + pad && y >= b.y - pad && y <= b.y + b.h + pad;
  const syncIn = (id, v) => { const el = document.getElementById(id); if (el) el.value = v; };
  const GRAB = {
    down(x, y) {
      const S = LAY.S; if (!S) return false; const m = LAY.mode;
      if ((m === "pit" || m === "up") && inBox(LAY.pb, x, y, 24) && LAY.tX) { LAY.drag = true; LAY.used = true; GRAB.move(x, y); return true; }
      if (m === "live" && inBox(LAY.box, x, y)) { LAY.used = true; const h = S.handlers[live.on ? "xeshut" : "xerestart"]; h && h(); return false; }
      if (m === "osc" && inBox(LAY.box, x, y)) { LAY.used = true; if (!osc.init) oscReset(); osc.side = x < LAY.box.x + LAY.box.w / 2 ? 1 : -1; osc.push = osc.t; return false; }
      return false;
    },
    move(x) { const S = LAY.S; if (!LAY.drag || !S) return; const t = LAY.tX(x); if (LAY.mode === "pit") { const v = Math.round(t * 2) / 2; S.set("th", v); syncIn("xe-th", v); } else S.cur = t; },
    up() { LAY.drag = false; }, cancel() { LAY.drag = false; },
    hover(x, y, e) { const m = LAY.mode, cv = e.target; cv.style.cursor = ((m === "pit" || m === "up") && inBox(LAY.pb, x, y, 24)) ? "grab" : ((m === "live" || m === "osc") && inBox(LAY.box, x, y)) ? "pointer" : ""; },
  };
  const btn = (act, on) => document.querySelectorAll(`#xenon [data-act="${act}"]`).forEach((b) => b.setAttribute("aria-pressed", String(!!on)));

  // ---------- core picture: fuel pins, flux glow, iodine specks, xenon fog ----------
  const FOG = [], SPK = []; { const q = rng(8); for (let i = 0; i < 70; i++) FOG.push([q(), q(), q() * TAU, 0.4 + 0.8 * q(), q()]); for (let i = 0; i < 90; i++) SPK.push([q(), q(), q() * TAU, q()]); }
  const hits = [];
  function rodsIn(g, box, f, side) { // f = 0 out .. 1 fully in; side: 0 both, -1 left only, +1 right only
    const { c } = g, n = g.W < 600 ? 6 : 10;
    for (let i = 0; i < n; i++) { const x = box.x + box.w * (i + 0.5) / n; if (side < 0 && x > box.x + box.w / 2) continue; if (side > 0 && x < box.x + box.w / 2) continue;
      const len = 10 + box.h * 0.85 * clamp(f, 0, 1); g.ctx.save(); g.ctx.fillStyle = g.rgba(c.soft, 0.5); g.ctx.fillRect(x - 2.5, box.y - 10, 5, len); g.ctx.restore(); g.dot(x, box.y - 10 + len, 2.5, c.soft, 0.7); }
  }
  function ring(g, x, y, a, col) { if (a < 0 || a > 1) return; g.ring(x, y, 20 + 260 * a, col, 3 * (1 - a), 0.8 * (1 - a)); g.glow(x, y, 60 + 120 * a, col, 0.35 * (1 - a)); }
  function core(g, S, box, fluxL, fluxR, xL, xR, yL, yR) {
    const { c, ctx } = g, phone = g.W < 600, nx = phone ? 8 : 12, ny = phone ? 3 : 4, R = Math.min(box.w / nx, box.h / ny) * 0.17;
    ctx.save(); const wg = ctx.createLinearGradient(0, box.y, 0, box.y + box.h); wg.addColorStop(0, g.rgba(c.cool, 0.05)); wg.addColorStop(0.5, g.rgba(c.cool, 0.11)); wg.addColorStop(1, g.rgba(c.cool, 0.05)); ctx.fillStyle = wg;
    ctx.beginPath(); if (ctx.roundRect) ctx.roundRect(box.x, box.y, box.w, box.h, 16); else ctx.rect(box.x, box.y, box.w, box.h); ctx.fill(); ctx.restore();
    g.clip(box.x, box.y, box.w, box.h);
    const half = (L) => (L ? fluxL : fluxR);
    for (let s = 0; s < 2; s++) g.glow(box.x + box.w * (0.25 + 0.5 * s), box.y + box.h / 2, box.w * 0.42, c.cool, 0.04 + 0.3 * clamp(half(s === 0), 0, 1.6) / 1.6);
    for (let j = 0; j < ny; j++) for (let i = 0; i < nx; i++) {
      const x = box.x + box.w * (i + 0.5) / nx, y = box.y + box.h * (j + 0.5) / ny, f = half(i < nx / 2);
      g.glow(x, y, R * 3, c.warm, 0.06 + 0.32 * clamp(f, 0, 1.6) / 1.6); g.ball(x, y, R, c.warm, 0.95);
    }
    // iodine: amber specks in the fuel, number ~ inventory
    const yMax = eqY(1);
    for (let k = 0; k < SPK.length; k++) { const [u, v, ph, w] = SPK[k], L = u < 0.5, n = (L ? yL : yR) / yMax; if (w > n * 0.75) continue;
      g.dot(box.x + box.w * u + 3 * Math.sin(S.time * 0.8 + ph), box.y + box.h * (0.08 + 0.84 * v) + 3 * Math.cos(S.time * 0.7 + ph), 2, c.photon, 0.9); }
    // xenon fog: violet haze, thickness ~ xenon worth
    const xMax = 6.4;
    const t = S.time;
    // slow swells: a few large soft banks that breathe
    for (let k = 0; k < 6; k++) { const L = k < 3, d = clamp(pc(L ? xL : xR) / xMax, 0, 1.2); if (d < 0.02) continue;
      const u = (L ? 0.08 : 0.58) + 0.17 * (k % 3) + 0.05 * Math.sin(t * 0.11 + k * 1.7), v = 0.5 + 0.22 * Math.sin(t * 0.09 + k * 2.3);
      g.glow(box.x + box.w * u, box.y + box.h * v, box.h * (0.75 + 0.18 * Math.sin(t * 0.35 + k)), c.alpha, 0.12 * d * (0.8 + 0.25 * Math.sin(t * 0.5 + k * 0.9))); }
    // billows: puffs that drift, swell and thin out
    for (const [u, v, ph, sz, w] of FOG) { const L = u < 0.5, d = clamp(pc(L ? xL : xR) / xMax, 0, 1.2); if (d < 0.02) continue;
      const br = 1 + 0.3 * Math.sin(t * (0.45 + 0.4 * w) + ph * 3);
      const fx = box.x + box.w * (u + 0.05 * Math.sin(t * 0.19 + ph) + 0.025 * Math.sin(t * 0.47 + ph * 2)), fy = box.y + box.h * (v + 0.09 * Math.cos(t * 0.16 + ph * 1.3) + 0.04 * Math.sin(t * 0.39 + ph));
      g.glow(fx, fy, box.h * 0.36 * sz * br * (0.7 + 0.45 * d), c.alpha, (0.19 * d + 0.08 * d * w) * (0.78 + 0.3 * Math.sin(t * 0.7 + ph))); }
    for (let k = 0; k < 60; k++) { const [u, v, ph, sz, w] = FOG[k], L = u < 0.5, d = pc(L ? xL : xR) / xMax; if (w > d * 1.1) continue;
      g.ball(box.x + box.w * (u + 0.03 * Math.sin(t * 0.27 + ph)), box.y + box.h * (0.1 + 0.8 * v + 0.05 * Math.cos(t * 0.23 + ph * 1.7)), phone ? 2.6 : 3.2, c.alpha, 0.9); }
    // neutrons swallowed by xenon: flashes ~ flux x xenon
    for (let s = 0; s < 2; s++) { const rate = 7 * half(s === 0) * pc(s ? xR : xL) / 2.35; if (r() < rate * 0.016) hits.push({ x: box.x + box.w * (s * 0.5 + 0.05 + 0.4 * r()), y: box.y + box.h * (0.1 + 0.8 * r()), t: S.time }); }
    for (let i = hits.length - 1; i >= 0; i--) { const h = hits[i], a = S.time - h.t; if (a > 0.5) { hits.splice(i, 1); continue; } g.glow(h.x, h.y, 6 + 20 * a, c.alpha, 0.7 * (1 - a / 0.5)); if (a < 0.25) g.ball(h.x - 30 * (0.25 - a), h.y - 12 * (0.25 - a), 2.6, c.neutron, 1 - a / 0.25); }
    while (hits.length > 40) hits.shift();
    ctx.restore();
  }
  function chain(g, y, fs) {
    const { c, W } = g, phone = W < 600;
    if (phone) {
      g.label("fission → iodine-135 (6.6 h) → xenon-135 (9.1 h) → Cs-135", W / 2, y, { color: c.soft, size: fs - 1 });
      g.label("xenon-135 + n → Xe-136: 2.6 million barns", W / 2, y + fs + 5, { color: c.alpha, size: fs - 1, weight: 600 });
    } else g.label("fission → iodine-135 (6.6 h) → xenon-135 (9.1 h) → Cs-135  ·  Xe-135 swallows neutrons: 2.6 million barns", W / 2, y, { color: c.soft, size: fs - 1 });
  }
  // a time landscape: xenon worth (%) against hours
  function plot(g, box, t0, t1, ymax, fs, opts) {
    const { c } = g, X = (t) => box.x + box.w * (t - t0) / (t1 - t0), Y = (v) => box.y + box.h * (1 - v / ymax);
    g.line(box.x, box.y + box.h, box.x + box.w, box.y + box.h, c.line, 1);
    if (opts.margin) {
      g.line(box.x, Y(MARGIN), box.x + box.w, Y(MARGIN), c.proton, 1.2, 0.8, [5, 4]);
      g.label(g.W < 600 ? "spare reactivity" : "spare reactivity the rods can give", box.x + box.w - 2, Y(MARGIN) - 10, { color: c.proton, size: fs - 2, align: "right", bg: true });
    }
    return { X, Y };
  }
  const land = (g, pts, col, box, a = 0.34) => { g.clip(box.x - 2, box.y - 30, box.w + 6, box.h + 30); g.ground(pts, col, box.h, a); g.ctx.restore(); };
  const yTicks = (g, P, box, list, fs) => list.forEach((v) => { g.line(box.x - 4, P.Y(v), box.x, P.Y(v), g.c.faint, 1); g.label(v ? `−${v}` : "0", box.x - 7, P.Y(v), { color: g.c.faint, size: fs - 2, align: "right" }); });
  const ticks = (g, P, box, list, fs, unit) => list.forEach((t, i) => g.label(i === list.length - 1 ? `${t} ${unit}` : String(t), P.X(t), box.y + box.h + 12, { color: g.c.faint, size: fs - 2 }));

  WT.chapter("xenon", {
    level: 2, num: "Lesson 1", title: "Xenon poisoning", short: "Xenon",
    html: `
<div class="step">
  <h3>A poison made by fission</h3>
  <p>About 6.6 % of fissions lead, through iodine-135, to xenon-135: the strongest neutron absorber known. It builds up for about two days until neutrons burn it and decay removes it as fast as it forms. Higher power burns it faster too, so the level saturates.</p>
  <div class="ctl"><label for="xe-p1">Power (%)</label><input id="xe-p1" type="range" data-bind="P" data-instant min="10" max="100" step="5" value="100"><output data-show="P" data-fmt="0"></output></div>
</div>
<div class="step">
  <h3>The xenon pit</h3>
  <p>Shut down and the burning stops, but the iodine already made keeps turning into xenon. The poison peaks about nine hours later, more than the rods can give back, so the reactor cannot restart; it fades over two to three days.</p>
  <div class="ctl"><label for="xe-th">Hours after shutdown</label><input id="xe-th" type="range" data-bind="th" data-instant min="0" max="72" step="0.5" value="9"><output data-show="th" data-fmt="1"></output></div>
</div>
<div class="step">
  <h3>Shut down, restart</h3>
  <p>Now it runs live, three hours per second. Shut down, then try to restart: inside the pit it is refused; later the neutrons burn the xenon off. A power change alone also swings the xenon for hours.</p>
  <div class="ctl"><label for="xe-p3">Power (%)</label><input id="xe-p3" type="range" data-bind="P" data-instant min="10" max="100" step="5" value="100"><output data-show="P" data-fmt="0"></output></div>
  <div class="btns"><button class="btn" data-act="xeshut">Shut down</button><button class="btn ghost" data-act="xerestart">Restart</button></div>
</div>
<div class="step">
  <h3>Xenon oscillations</h3>
  <p>In a large core the two sides are only loosely coupled. Push rods into one side: less flux there burns less xenon, so the power drifts across, then swings back, about once a day. In bigger cores the swing grows unless operators damp it.</p>
  <div class="ctl"><label for="xe-wd">Core size (m)</label><input id="xe-wd" type="range" data-bind="wd" data-instant min="1.5" max="3.5" step="0.1" value="3"><output data-show="wd" data-fmt="1"></output></div>
  <div class="btns"><button class="btn" data-act="xepush">Push rods into the left side</button></div>
</div>`,
    setup(S) {
      S.set("mode", "up"); S.set("P", 100); S.set("th", 9); S.set("wd", 3); S.cur = 0;
      S.on("xeshut", () => { if (!live.on) return; live.on = false; live.msg = "shut down"; live.msgT = S.time; });
      S.on("xerestart", () => {
        if (live.on) return;
        if (pc(live.x) > MARGIN) { live.msg = "refused: more xenon than spare reactivity"; live.msgT = S.time; return; }
        live.on = true; live.msg = "restarted"; live.msgT = S.time;
      });
      S.on("xepush", () => { if (!osc.init) oscReset(); osc.side = 1; osc.push = osc.t; });
    },
    steps: [
      (S) => { S.set("mode", "up"); S.cur = 0; },
      (S) => { S.set("mode", "pit"); },
      (S) => { S.set("mode", "live"); liveReset(S); },
      (S) => { S.set("mode", "osc"); oscReset(); },
    ],
    frame(g, S, dt) {
      if (g.W < 40 || g.H < 40) return;
      const { W, H, c } = g, phone = W < 600, fs = phone ? 11 : 13, snap = document.body.classList.contains("shot"), mode = S.mode;
      const box = { x: W * 0.05, y: H * (phone ? 0.05 : 0.06), w: W * 0.9, h: H * (phone ? 0.3 : 0.37) };
      const pb = { x: W * (phone ? 0.12 : 0.1), y: H * (phone ? 0.55 : 0.6), w: W * (phone ? 0.84 : 0.86), h: H * (phone ? 0.25 : 0.23) };
      LAY.box = box; LAY.pb = pb; LAY.S = S; LAY.mode = mode;
      if (!g.ctx.canvas._xeg) { g.ctx.canvas._xeg = 1; WT.grab(g.ctx.canvas, GRAB); }
      const rd = { color: c.ink, size: fs + 1, weight: 600, serif: true }, yRd = H * 0.93;
      chain(g, box.y + box.h + (phone ? 14 : 18), fs);
      const yLab = (s) => g.label(s, pb.x, pb.y - 14, { color: c.soft, size: fs - 1, align: "left" });

      if (mode === "up") {
        const C = upCurve(S.P); S.cur = snap ? 48 : LAY.drag ? S.cur : S.cur + dt * 4; if (S.cur > 66) S.cur = 0; const tc = Math.min(S.cur, 60); LAY.tX = (x) => clamp(60 * (x - pb.x) / pb.w, 0, 60);
        const [xv, yv] = at(C, tc), p = S.P / 100;
        core(g, S, box, p, p, xv * NU / 100, xv * NU / 100, yv, yv);
        const P = plot(g, pb, 0, 60, 3, fs, {}), pts = C.pts.filter((q) => q[0] <= tc).map((q) => [P.X(q[0]), P.Y(q[1])]);
        const full = C.pts.map((q) => [P.X(q[0]), P.Y(q[1])]);
        g.poly(full, c.alpha, 1.2, 0.35, [4, 4]); land(g, pts, c.alpha, pb, 0.4); g.poly(pts, c.alpha, 2.6); yTicks(g, P, pb, [0, 1, 2, 3], fs);
        g.dot(P.X(tc), P.Y(xv), 4.5, c.alpha); g.glow(P.X(tc), P.Y(xv), 16, c.alpha, 0.4);
        const eq = pc(eqX(p)); g.line(pb.x, P.Y(eq), pb.x + pb.w, P.Y(eq), c.soft, 1, 0.5, [2, 4]);
        g.label(`equilibrium −${eq.toFixed(2)} %`, pb.x + pb.w - 2, P.Y(eq) - 11, { color: c.alpha, size: fs - 1, weight: 600, align: "right", bg: true });
        yLab("xenon worth (% of k)"); ticks(g, P, pb, [0, 20, 40, 60], fs, "h");
        g.label(`${S.P.toFixed(0)} % power · ${tc.toFixed(0)} h after start-up · xenon −${xv.toFixed(2)} %`, W / 2, yRd, rd);
      } else if (mode === "pit") {
        const C = pitCurve(S.P), th = S.th, [xv, yv] = at(C, th), pre = at(C, -1);
        core(g, S, box, 0.015, 0.015, xv * NU / 100, xv * NU / 100, yv, yv); rodsIn(g, box, 1, 0);
        const ym = Math.max(7, C.pk * 1.12), P = plot(g, pb, -12, 72, ym, fs, { margin: true }); LAY.tX = (x) => clamp(-12 + 84 * (x - pb.x) / pb.w, 0, 72); const P2 = P, all = C.pts.map((q) => [P.X(q[0]), P.Y(q[1])]);
        if (C.a >= 0) { g.area([[P.X(C.a), pb.y + pb.h], [P.X(C.a), pb.y], [P.X(C.b), pb.y], [P.X(C.b), pb.y + pb.h]], c.proton, 0.08);
          g.label(phone ? "no restart" : "too poisoned to restart", P.X((C.a + C.b) / 2), pb.y + pb.h - 12, { color: c.proton, size: fs - 1, weight: 600, bg: true }); }
        land(g, all, c.alpha, pb); g.poly(all, c.alpha, 2.4); yTicks(g, P, pb, ym > 9 ? [0, 4, 8] : [0, 2, 4, 6], fs);
        g.line(P.X(0), pb.y + 18, P.X(0), pb.y + pb.h, c.soft, 1, 0.5, [2, 4]); g.label("shutdown", P.X(0), pb.y + pb.h + 26, { color: c.soft, size: fs - 2 });
        g.line(P.X(th), pb.y, P.X(th), pb.y + pb.h, c.ink, 1, 0.3); g.ring(P.X(th), P.Y(xv), 10 + 2 * Math.sin(S.time * 3), c.alpha, 1.5, LAY.drag ? 0.9 : 0.55); g.dot(P.X(th), P.Y(xv), 5.5, c.alpha); g.glow(P.X(th), P.Y(xv), 22, c.alpha, 0.5); void P2;
        if (!LAY.used) { const up = P.Y(xv) - 24 > pb.y - 4; g.label("drag", P.X(th) + (up ? 0 : 18), up ? P.Y(xv) - 24 : P.Y(xv), { color: c.alpha, size: fs - 2, weight: 600, bg: true, align: up ? "center" : "left" }); } // near the top, beside the point (above it ran into the axis title)
        if (Math.abs(th - C.tp) > 4) g.label(`peak −${C.pk.toFixed(1)} % at ${C.tp.toFixed(0)} h`, P.X(C.tp) + 8, P.Y(C.pk) - 12, { color: c.alpha, size: fs - 1, align: "left", bg: true });
        yLab("xenon worth (% of k)"); ticks(g, P, pb, [0, 24, 48, 72], fs, "h");
        const can = xv <= MARGIN;
        g.label(`${th.toFixed(1)} h after shutdown · xenon −${xv.toFixed(2)} % · ${can ? "restart possible" : "cannot restart"}`, W / 2, yRd, { ...rd, color: can ? c.ink : c.proton });
        void pre;
      } else if (mode === "live") {
        if (!live.init) liveReset(S);
        const H3 = snap ? 0 : dt * 3, tgt = live.on ? S.P / 100 : 0;
        if (snap && live.hist.length < 3) { // representative still: shut down at 6 h, refused restart, look at 20 h
          const st = { x: live.x, y: live.y }; for (let t = 0.25; t <= 18; t += 0.25) { adv(st, t < 6 ? 1 : 0, 0.25); live.hist.push([t, pc(st.x), t < 6 ? 1 : 0]); } live.t = 18; live.x = st.x; live.y = st.y; live.p = 0; live.on = false; live.msg = "refused: more xenon than spare reactivity"; live.msgT = S.time;
        }
        if (H3 > 0) { const n = Math.ceil(H3 / 0.05); for (let i = 0; i < n; i++) { live.p += (tgt - live.p) * Math.min(1, (H3 / n) / 0.5); const st = { x: live.x, y: live.y }; step(st, live.p, H3 / n); live.x = st.x; live.y = st.y; live.t += H3 / n; }
          const lh = live.hist[live.hist.length - 1]; if (live.t - lh[0] >= 0.2) live.hist.push([live.t, pc(live.x), live.p]); while (live.hist.length > 2 && live.hist[1][0] < live.t - 75) live.hist.shift(); }
        core(g, S, box, live.p + 0.015, live.p + 0.015, live.x, live.x, live.y, live.y);
        live.rod += ((live.on ? 0 : 1) - live.rod) * Math.min(1, (dt || 0.05) * (live.on ? 2 : 9)); if (snap) live.rod = live.on ? 0 : 1; rodsIn(g, box, live.rod, 0);
        if (live.msg === "restarted") ring(g, box.x + box.w / 2, box.y + box.h / 2, (S.time - live.msgT) / 1.4, c.cool);
        if (live.msg.startsWith("refused")) { const a = S.time - live.msgT; if (a < 1.2) { g.ctx.save(); g.ctx.strokeStyle = g.rgba(c.proton, 0.9 * (1 - a / 1.2)); g.ctx.lineWidth = 4; g.ctx.strokeRect(box.x, box.y, box.w, box.h); g.ctx.restore(); } }
        if (!LAY.used && S.time - live.msgT > 2.5) g.label(live.on ? "tap the core to shut down" : "tap the core to restart", box.x + box.w / 2, box.y + box.h - 14, { color: c.ink, size: fs - 1, weight: 600, bg: true, alpha: 0.85 });
        const t1 = Math.max(72, live.t), t0 = t1 - 72, P = plot(g, pb, t0, t1, 7, fs, { margin: true });
        const pts = live.hist.map((q) => [P.X(q[0]), P.Y(Math.min(q[1], 7))]);
        g.clip(pb.x, pb.y - 4, pb.w + 4, pb.h + 8);
        // power history as a faint band at the floor
        const pw = live.hist.map((q) => [P.X(q[0]), pb.y + pb.h - q[2] * pb.h * 0.16]);
        g.area([[pw[0][0], pb.y + pb.h], ...pw, [pw[pw.length - 1][0], pb.y + pb.h]], c.warm, 0.18);
        g.ctx.restore(); land(g, pts, c.alpha, pb); g.poly(pts, c.alpha, 2.4); yTicks(g, P, pb, [0, 2, 4, 6], fs);
        const lx = P.X(live.t), ly = P.Y(Math.min(pc(live.x), 7)); g.dot(lx, ly, 5, c.alpha); g.glow(lx, ly, 18, c.alpha, 0.45);
        g.label("power", pb.x + 4, pb.y + pb.h - 10, { color: c.warm, size: fs - 2, align: "left" });
        yLab("xenon worth (% of k)");
        const tk = [0, 24, 48, 72].map((d) => t0 + d); tk.forEach((t, i) => g.label(i === 3 ? `${t.toFixed(0)} h` : t.toFixed(0), P.X(t), pb.y + pb.h + 12, { color: c.faint, size: fs - 2 }));
        if (S.time - live.msgT < 2.5 && live.msg) g.label(live.msg, W / 2, box.y + box.h / 2, { color: live.msg.startsWith("refused") ? c.proton : c.ink, size: fs + 1, weight: 700, bg: true, alpha: clamp(2.5 - (S.time - live.msgT), 0, 1) });
        const st = live.on ? `running at ${(100 * live.p).toFixed(0)} %` : pc(live.x) > MARGIN ? "shut down · in the pit" : "shut down · restart possible";
        g.label(`${st} · xenon −${pc(live.x).toFixed(2)} %`, W / 2, yRd, { ...rd, color: !live.on && pc(live.x) > MARGIN ? c.proton : c.ink });
      } else {
        if (!osc.init) oscReset();
        if (snap && osc.hist.length < 3) { osc.push = 0; oscStep(S, 70); }
        else if (!snap) oscStep(S, dt * 4);
        core(g, S, box, 1 + osc.a, 1 - osc.a, osc.L.x, osc.R.x, osc.L.y, osc.R.y);
        g.line(box.x + box.w / 2, box.y + 6, box.x + box.w / 2, box.y + box.h - 6, c.soft, 1, 0.35, [3, 5]);
        g.label(`left ${(50 * (1 + osc.a)).toFixed(0)} %`, box.x + box.w * 0.25, box.y + box.h - 12, { color: c.ink, size: fs - 1, weight: 600, bg: true });
        g.label(`right ${(50 * (1 - osc.a)).toFixed(0)} %`, box.x + box.w * 0.75, box.y + box.h - 12, { color: c.ink, size: fs - 1, weight: 600, bg: true });
        if (osc.push >= 0 && osc.t - osc.push < 2) rodsIn(g, box, 0.65, osc.side > 0 ? -1 : 1);
        if (osc.push >= 0) ring(g, box.x + box.w * (osc.side > 0 ? 0.25 : 0.75), box.y + box.h / 2, (osc.t - osc.push) / 3, c.ink);
        if (!LAY.used) g.label("tap a side to push rods in", box.x + box.w / 2, box.y + 14, { color: c.ink, size: fs - 1, weight: 600, bg: true, alpha: 0.85 });
        const t1 = Math.max(96, osc.t), t0 = t1 - 96, P = { X: (t) => pb.x + pb.w * (t - t0) / 96, Y: (a) => pb.y + pb.h / 2 - a / 0.6 * pb.h / 2 };
        g.line(pb.x, P.Y(0), pb.x + pb.w, P.Y(0), c.line, 1);
        const pts = osc.hist.map((q) => [P.X(q[0]), P.Y(q[1])]);
        g.clip(pb.x, pb.y - 4, pb.w + 4, pb.h + 8);
        g.ctx.save(); g.ctx.beginPath(); g.ctx.rect(pb.x, pb.y - 4, pb.w + 4, P.Y(0) - pb.y + 4); g.ctx.clip(); g.area([[pts[0][0], P.Y(0)], ...pts, [pts[pts.length - 1][0], P.Y(0)]], c.warm, 0.3); g.ctx.restore();
        g.ctx.save(); g.ctx.beginPath(); g.ctx.rect(pb.x, P.Y(0), pb.w + 4, pb.h); g.ctx.clip(); g.area([[pts[0][0], P.Y(0)], ...pts, [pts[pts.length - 1][0], P.Y(0)]], c.cool, 0.3); g.ctx.restore();
        g.poly(pts, c.ink, 2); g.ctx.restore();
        g.dot(P.X(osc.t), P.Y(osc.a), 4.5, c.ink);
        g.label("more power left", pb.x + 4, pb.y + 6, { color: c.warm, size: fs - 2, align: "left" }); g.label("more power right", pb.x + 4, pb.y + pb.h - 6, { color: c.cool, size: fs - 2, align: "left" });
        [0, 24, 48, 72, 96].forEach((d, i) => g.label(i === 4 ? `${(t0 + d).toFixed(0)} h` : (t0 + d).toFixed(0), P.X(t0 + d), pb.y + pb.h + 12, { color: c.faint, size: fs - 2 }));
        // measured period and trend from the last swings
        const zc = []; for (let i = 1; i < osc.hist.length; i++) if (osc.hist[i - 1][1] < 0 && osc.hist[i][1] >= 0) zc.push(osc.hist[i][0]);
        const per = zc.length > 1 ? zc[zc.length - 1] - zc[zc.length - 2] : 0, G = 12 * S.wd;
        const trend = G < 27 ? "dies away" : G < 30.5 ? "dies away slowly" : "grows";
        g.label(per ? `swing period ${per.toFixed(0)} h · ${S.wd.toFixed(1)} m core: the swing ${trend}` : `${S.wd.toFixed(1)} m core: push the rods to start a swing`, W / 2, yRd, rd);
      }
      g.label("illustration", W - 6, H - 10, { color: c.faint, size: 10, align: "right" });
    },
  });
})();
