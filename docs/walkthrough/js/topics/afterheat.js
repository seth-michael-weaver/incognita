/* Heat after shutdown (decay heat). Scenes (S.mode):
 *   "drop"  = a core at full power; "Drop the rods" stops the chain. Heat after the drop = fission part + decay part.
 *             Decay part: Way-Wigner, P/P0 = 0.066 [t^-0.2 - (t + T)^-0.2], t = seconds since shutdown, T = operating
 *             time (one year, 3.156e7 s) (K. Way & E. Wigner, Phys. Rev. 73 (1948) 1318; the 0.066 form as in Glasstone &
 *             Sesonske, Nuclear Reactor Engineering). Gives 6.4 % at 1 s, 1.1 % at 1 h, 0.47 % at 1 day, 0.25 % at 1 week.
 *             Fission part (illustrative shape): prompt drop to ~11 % of full power, then dying away with the delayed-
 *             neutron precursors, 0.11 (0.967 e^-t/6s + 0.033 e^-t/80s); the 80 s tail is the longest-lived precursor group.
 *             Time runs at 1x (real seconds).
 *   "fade"  = the same core; slider over time since shutdown, 1 s to 1 year (log scale), Way-Wigner curve drawn as a
 *             landscape; heat in % and in MW for a 3000 MW (thermal) core, and in 2 kW kettles.
 *   "cool"  = a lumped energy balance C dT/dt = P(t) - K (T - T0) with three choices of K: pumps (large), a passive
 *             natural-circulation loop to a raised pool (smaller), none (near zero). Temperatures are drawn without
 *             numbers on a thermometer with a "normal" band; C and K are illustrative. Sim clock 10 min per second,
 *             starting 1 h after shutdown.
 * Several newer designs remove decay heat passively for days (e.g. AP1000: 72 h; ESBWR: 7 days, vendor design data). */
(function () {
  const { TAU, clamp, lerp, smooth, rng } = WT.util;
  const TOP = 3.156e7, PTH = 3000;
  const decay = (t) => 0.066 * (Math.pow(Math.max(t, 1), -0.2) - Math.pow(Math.max(t, 1) + TOP, -0.2));
  const fis = (t) => 0.11 * (0.967 * Math.exp(-t / 6) + 0.033 * Math.exp(-t / 80));
  const log10 = (x) => Math.log(x) / Math.LN10;
  const vis = (p) => clamp(0.25 + 0.75 * (log10(Math.max(p, 1e-5)) + 3) / 3, 0.04, 1); // glow brightness for a heat fraction
  const r = rng(41);
  const fmtT = (t) => t < 90 ? WT.trf("{a} s", t.toFixed(0)) : t < 5400 ? WT.trf("{a} min", (t / 60).toFixed(0)) : t < 1.5 * 86400 ? WT.trf("{a} hours", (t / 3600).toFixed(t < 36000 ? 1 : 0)) : t < 60 * 86400 ? WT.trf("{a} days", (t / 86400).toFixed(t < 10 * 86400 ? 1 : 0)) : WT.trf("{a} months", (t / 2.63e6).toFixed(0));
  const pct = (p) => (p >= 0.0995 ? (100 * p).toFixed(0) : p >= 0.00995 ? (100 * p).toFixed(1) : (100 * p).toFixed(2));
  const sparks = [], neutrons = [];
  for (let i = 0; i < 60; i++) neutrons.push({ u: r(), v: r(), a: r() * TAU, s: 0.4 + 0.6 * r() });
  const flow = []; for (let i = 0; i < 40; i++) flow.push(r());
  const pflow = []; for (let i = 0; i < 22; i++) pflow.push(r());

  const geo = {};
  function grabSetup(cv, S) {
    let drag = false;
    const inR = (b, x, y) => b && x > b.x && x < b.x + b.w && y > b.y && y < b.y + b.h;
    const setT = (x) => { const c = geo.curve; if (!c) return; const v = clamp((x - c.x0) / (c.x1 - c.x0) * 7.5, 0, 7.5); S.set("lt", v); document.querySelectorAll('#afterheat [data-bind="lt"]').forEach((i) => (i.value = v)); };
    WT.grab(cv, {
      down(x, y) {
        if (S.mode === "fade") { drag = true; setT(x); return true; }
        if (S.mode === "drop" && inR(geo.core, x, y)) { S.handlers[S.dropT < 0 ? "ahDrop" : "ahUp"](); return false; }
        if (S.mode === "cool") { const p = geo.pump; if (p && Math.hypot(x - p.x, y - p.y) < p.r) S.handlers.ahPump(); else if (inR(geo.pool, x, y)) S.handlers.ahPass(); }
        return false;
      },
      move(x) { if (drag) setT(x); }, up() { drag = false; }, cancel() { drag = false; },
      hover(x, y) { const p = geo.pump; cv.style.cursor = S.mode === "fade" ? "ew-resize" : S.mode === "drop" && inR(geo.core, x, y) ? "pointer" : S.mode === "cool" && ((p && Math.hypot(x - p.x, y - p.y) < p.r) || inR(geo.pool, x, y)) ? "pointer" : ""; },
    });
  }
  function setBtn(S) {
    document.querySelectorAll('#afterheat [data-act="ahPump"]').forEach((b) => b.setAttribute("aria-pressed", String(!!S.pump)));
    document.querySelectorAll('#afterheat [data-act="ahPass"]').forEach((b) => b.setAttribute("aria-pressed", String(!!S.pass)));
  }
  function resetCool(S) { S.tsim = 3600; S.Tc = 0.25; S.trace = []; }

  WT.chapter("afterheat", {
    level: 0, num: "Lesson 1", title: "Heat after shutdown", short: "Afterheat",
    html: `
<div class="step">
  <h3>The chain stops</h3>
  <p>Dropping the control rods stops the splitting of atoms within about a minute. But the fuel keeps glowing: the fragments left by earlier splits are radioactive, and their decays still give off heat.</p>
  <div class="btns"><button class="btn" data-act="ahDrop">Drop the rods</button> <button class="btn ghost" data-act="ahUp">Restart</button></div>
</div>
<div class="step">
  <h3>It fades, slowly</h3>
  <p>Right after shutdown this heat is about 6–7 % of full power. After an hour it is about 1 %, after a day about half a percent, after a week a quarter. Small shares, but of a very big number.</p>
  <div class="ctl"><label for="ah-t">Time since shutdown</label><input id="ah-t" type="range" data-bind="lt" data-instant min="0" max="7.5" step="0.01" value="3.56"></div>
</div>
<div class="step">
  <h3>Keep the water moving</h3>
  <p>So the core is cooled after shutdown too. Pumps keep water flowing past the fuel and carry the heat away. Switch them off and the temperature climbs, because the heat has nowhere to go.</p>
  <div class="btns"><button class="btn ghost" data-act="ahPump" aria-pressed="true">Pumps</button></div>
</div>
<div class="step">
  <h3>Cooling without pumps</h3>
  <p>Hot water rises and cool water sinks. A loop up to a pool placed higher than the core keeps water moving with no pumps at all. Several newer designs rely on this for days.</p>
  <div class="btns"><button class="btn ghost" data-act="ahPump" aria-pressed="false">Pumps</button> <button class="btn ghost" data-act="ahPass" aria-pressed="true">Passive loop</button></div>
</div>`,
    setup(S) {
      S.set("mode", "drop"); S.set("lt", 3.56); S.dropT = -1; S.pump = 1; S.pass = 0; resetCool(S);
      S.on("ahDrop", () => { if (S.dropT < 0) S.dropT = S.time; });
      S.on("ahUp", () => { S.dropT = -1; });
      S.on("ahPump", () => { S.pump = S.pump ? 0 : 1; setBtn(S); });
      S.on("ahPass", () => { S.pass = S.pass ? 0 : 1; setBtn(S); });
    },
    steps: [
      (S) => { S.set("mode", "drop"); S.dropT = -1; },
      (S) => { S.set("mode", "fade"); S.set("lt", 3.56); },
      (S) => { S.set("mode", "cool"); S.pump = 1; S.pass = 0; resetCool(S); setBtn(S); },
      (S) => { S.set("mode", "cool"); S.pump = 0; S.pass = 1; resetCool(S); setBtn(S); },
    ],
    frame(g, S, dt) {
      const { W, H, c } = g, phone = W < 600, fs = phone ? 11 : 13, snap = document.body.classList.contains("shot");
      if (!S.grabbed) { S.grabbed = true; grabSetup(g.ctx.canvas, S); }
      if (S.mode === "cool") drawCool(g, S, dt, phone, fs, snap);
      else drawCoreScene(g, S, dt, phone, fs, snap);
    },
  });

  // ---------- the core (shared drawing) ----------
  function core(g, S, cx, cy, w, h, P, fisP, rodIn, phone, dt) {
    const { c, ctx } = g, v = vis(P), nF = phone ? 7 : 9;
    ctx.save(); const wg = ctx.createLinearGradient(0, cy - h / 2, 0, cy + h / 2); wg.addColorStop(0, g.rgba(c.cool, 0.06)); wg.addColorStop(1, g.rgba(c.cool, 0.16)); ctx.fillStyle = wg; ctx.strokeStyle = g.rgba(c.soft, 0.5); ctx.lineWidth = 1.5;
    ctx.beginPath(); if (ctx.roundRect) ctx.roundRect(cx - w / 2, cy - h / 2, w, h, Math.min(w, h) * 0.18); else ctx.rect(cx - w / 2, cy - h / 2, w, h); ctx.fill(); ctx.stroke(); ctx.restore();
    g.glow(cx, cy, Math.max(w, h) * 0.75, c.warm, 0.35 * v);
    const fx0 = cx - w * 0.38, fx1 = cx + w * 0.38, fy0 = cy - h * 0.32, fy1 = cy + h * 0.36, fw = Math.max(3, (fx1 - fx0) / nF * 0.4);
    for (let i = 0; i < nF; i++) {
      const x = lerp(fx0, fx1, (i + 0.5) / nF);
      ctx.save(); const fv = v * (0.88 + 0.12 * Math.sin(S.time * (5 + i * 1.3) + i * 2.1)), fg = ctx.createLinearGradient(x - fw, 0, x + fw, 0); fg.addColorStop(0, g.rgba(c.warm, 0.35 + 0.5 * fv)); fg.addColorStop(0.5, g.rgba(c.photon, 0.3 + 0.7 * v)); fg.addColorStop(1, g.rgba(c.warm, 0.35 + 0.5 * v));
      ctx.fillStyle = fg; ctx.fillRect(x - fw / 2, fy0, fw, fy1 - fy0); ctx.restore();
      g.glow(x, (fy0 + fy1) / 2, fw * 4, c.photon, 0.18 * v);
      if (i < nF - 1) { const rx = lerp(fx0, fx1, (i + 1) / nF), rl = fy1 - fy0, top = lerp(cy - h / 2 - rl * 0.55, fy0, rodIn); ctx.save(); ctx.fillStyle = g.rgba(c.faint, 0.9); ctx.fillRect(rx - 2.5, top, 5, rl); ctx.restore(); }
    }
    // neutrons while the chain runs
    const nN = Math.round(60 * clamp(fisP / 0.5, 0, 1) ** 0.5);
    for (let i = 0; i < nN; i++) { const n = neutrons[i], x = lerp(fx0, fx1, (n.u + S.time * 0.15 * n.s) % 1), y = lerp(fy0, fy1, 0.5 + 0.45 * Math.sin(S.time * n.s * 2 + n.a) * (n.v - 0.5) * 2); g.ball(x, y, phone ? 2.4 : 3, c.neutron, 0.85); }
    // fission flashes while splitting
    if (fisP > 0.02 && r() < fisP * 0.9) sparks.push({ x: lerp(fx0, fx1, r()), y: lerp(fy0, fy1, r()), t: S.time, f: 1 });
    // decays of the fission fragments: beta streaks and gamma flickers on the rods, rate growing with the decay heat
    const pd = Math.max(P - fisP, 1e-5), vd = vis(pd);
    S.dAcc = (S.dAcc || 0) + (dt || 0) * (4 + 80 * vd * vd);
    while (S.dAcc > 1) { S.dAcc -= 1; const k = Math.floor(r() * nF); sparks.push({ x: lerp(fx0, fx1, (k + 0.5) / nF) + (r() - 0.5) * fw, y: lerp(fy0, fy1, r()), t: S.time, f: 0, g: r() < 0.4, a: r() * TAU, l: 0.35 + 0.4 * r() }); }
    for (let i = sparks.length - 1; i >= 0; i--) {
      const s = sparks[i], a = S.time - s.t, life = s.f ? 0.45 : s.l; if (a > life) { sparks.splice(i, 1); continue; }
      const q = a / life;
      if (s.f) { g.glow(s.x, s.y, 8 + 30 * a, c.fission, 0.75 * (1 - q)); continue; }
      g.glow(s.x, s.y, (phone ? 9 : 14) + 10 * (1 - q), c.photon, 0.85 * (1 - q)); g.dot(s.x, s.y, 1.6, "#ffffff", 0.9 * (1 - q));
      if (s.g) g.photon(s.x + Math.cos(s.a) * q * w * 0.25, s.y + Math.sin(s.a) * q * w * 0.25, s.a, phone ? 12 : 16, 0.8 * (1 - q));
      else { const d = q * (phone ? 18 : 40), x2 = s.x + Math.cos(s.a) * d, y2 = s.y + Math.sin(s.a) * d; g.line(s.x + Math.cos(s.a) * d * 0.3, s.y + Math.sin(s.a) * d * 0.3, x2, y2, c.cool, 2, 0.9 * (1 - q)); g.dot(x2, y2, 1.8, c.cool, 1 - q); }
    }
    while (sparks.length > 140) sparks.shift();
    // heat shimmer rising off the core
    const sh = vis(P);
    if (sh > 0.08) for (let k = 0; k < 6; k++) {
      const x = lerp(cx - w * 0.35, cx + w * 0.35, (k + 0.5) / 6), pts = [];
      for (let j = 0; j <= 14; j++) { const yy = cy - h / 2 - 6 - j * h * 0.03; pts.push([x + Math.sin(j * 0.9 - S.time * 3.2 + k * 1.7) * (2 + j * 0.35), yy]); }
      g.poly(pts, c.warm, 1.6, 0.22 * sh * (0.6 + 0.4 * Math.sin(S.time * 1.3 + k)));
    }
  }

  // ---------- scenes 1 and 2 ----------
  function drawCoreScene(g, S, dt, phone, fs, snap) {
    const { W, H, c, ctx } = g, fade = S.mode === "fade";
    let t, P, Pf, rodIn;
    if (fade) { t = Math.pow(10, S.lt); Pf = 0; P = decay(t); rodIn = 1; }
    else {
      if (snap && S.dropT < 0) S.dropT = S.time - 20 - 1e-3, S.snapDrop = true;
      if (S.dropT < 0 && !S.snapDrop) { t = -1; P = 1; Pf = 1 - 0.066; rodIn = 0; }
      else { t = S.time - S.dropT; rodIn = smooth(0, 0.7, t); Pf = t < 0.7 ? lerp(0.934, fis(0), smooth(0, 0.7, t)) : fis(t - 0.7); P = Pf + decay(Math.max(1, t)); }
    }
    const cx = W * 0.5, cy = H * (phone ? 0.22 : fade ? 0.22 : 0.27), cw = W * (phone ? 0.5 : fade ? 0.6 : 0.72), ch = H * (phone ? 0.24 : fade ? 0.27 : 0.38);
    core(g, S, cx, cy, cw, ch, P, Pf, rodIn, phone, dt); geo.core = { x: cx - cw / 2, y: cy - ch / 2, w: cw, h: ch };
    // heat gauge: two parts stacked
    const gx = W * 0.1, gw = W * 0.8, gy = H * (phone ? 0.47 : 0.58), ph2 = true;
    if (!fade) {
      g.label("illustration", W - 6, H - 10, { color: c.faint, size: 10, align: "right" });
      const rows = [[c.fission, phone ? "splitting atoms" : "heat from splitting atoms", Pf], [c.photon, phone ? "decaying fragments" : "heat from decaying fragments", P - Pf]];
      rows.forEach(([col, nm, v], i) => {
        const y = gy + i * (phone ? 46 : 58), f = clamp(v, 0, 1);
        g.label(nm, gx, y - 14, { color: c.soft, size: fs, align: "left" });
        ctx.save(); ctx.fillStyle = g.rgba(c.soft, 0.1); ctx.fillRect(gx, y - 6, gw, 12); ctx.fillStyle = col; ctx.fillRect(gx, y - 6, Math.max(1.5, gw * f), 12); ctx.restore(); g.glow(gx + gw * f, y, 16, col, 0.5);
        g.label(`${pct(v)} %`, gx + gw, y - 14, { color: col, size: fs + 1, weight: 700, align: "right" });
      });
      const msg = t < 0 ? (phone ? "full power" : "running at full power") : WT.trf(phone ? "{a} after the rods dropped" : "{a} after the rods dropped", fmtT(t));
      g.label(msg, W * 0.5, gy + (phone ? 100 : 130), { color: c.ink, size: fs + 2, weight: 600, serif: true, align: "center", raw: true });
      g.label(WT.trf("total heat: {a} % of full power", pct(P)), W * 0.5, gy + (phone ? 122 : 156), { color: c.soft, size: fs, align: "center", raw: true });
      if (t > 0 && t < 70) g.label(phone ? "the splitting dies away in about a minute" : "the splitting dies away within about a minute", W * 0.5, gy + (phone ? 144 : 182), { color: c.fission, size: fs - 1, align: "center" });
      if (t > 70) g.label(phone ? "the decay heat stays and fades slowly" : "the decay heat stays, and fades only slowly", W * 0.5, gy + (phone ? 144 : 182), { color: c.photon, size: fs - 1, align: "center" });
      return;
    }
    // ---------- scene 2: the fading curve, log time ----------
    const x0 = W * 0.1, x1 = W * 0.94, y0 = H * 0.46, y1 = H * 0.74;
    geo.curve = { x0, x1 }; const LMAX = 7.5, Xt = (lt) => lerp(x0, x1, lt / LMAX), Yp = (p) => lerp(y1, y0, (log10(p) + 4) / (log10(0.08) + 4));
    const pts = []; for (let lt = 0; lt <= LMAX + 1e-6; lt += 0.05) pts.push([Xt(lt), Yp(decay(Math.pow(10, lt)))]);
    g.clip(x0, y0 - 30, x1 - x0, y1 - y0 + 30); g.ground(pts, c.photon, (y1 - y0) * 0.9, 0.3); ctx.restore(); g.poly(pts, c.photon, 2.4);
    g.line(x0, y1, x1, y1, c.line, 1);
    [[60, "1 min"], [3600, "1 hour"], [86400, "1 day"], [604800, "1 week"], [2.63e6 * 12, "1 year"]].forEach(([tt, s], i) => { const x = Xt(log10(tt)); g.line(x, y1, x, y1 + (i === 3 ? 18 : 5), c.faint, 1); g.label(s, x, y1 + (i === 3 ? 28 : 15), { color: c.soft, size: fs - 2 }); });
    [[0.01, "1 %"], [0.001, "0.1 %"]].forEach(([p, s]) => { g.line(x0, Yp(p), x1, Yp(p), c.line, 1, 0.6, [2, 5]); g.label(s, x0 + 2, Yp(p) - 9, { color: c.faint, size: fs - 2, align: "left" }); });
    const mx = Xt(S.lt), my = Yp(P); g.line(mx, my, mx, y1, c.photon, 1, 0.45); g.glow(mx, my, 20, c.photon, 0.6); g.dot(mx, my, 5.5, c.photon);
    g.label(phone ? "heat, share of full power" : "heat, as a share of full power", x0, y0 - 12, { color: c.soft, size: fs - 1, align: "left" });
    const ty = H * 0.85, tx = W * 0.5, al = "center";
    g.label(WT.trf("{a} after shutdown: {b} % of full power", fmtT(t), pct(P)), tx, ty, { color: c.ink, size: fs + 2, weight: 600, serif: true, align: al, raw: true });
    const mw = P * PTH, kettles = mw * 500;
    g.label(WT.trf(phone ? "3000 MW core: {a} MW, like {b} kettles" : "for a 3000 MW core: {a} MW, as much as {b} electric kettles", mw >= 10 ? mw.toFixed(0) : mw.toFixed(1), kettles >= 1e4 ? (Math.round(kettles / 1000) * 1000).toLocaleString("en-US") : Math.round(kettles / 100) * 100), tx, ty + fs + 12, { color: c.soft, size: fs, align: al, raw: true });
  }

  // ---------- scenes 3 and 4: cooling ----------
  function drawCool(g, S, dt, phone, fs, snap) {
    const { W, H, c, ctx } = g;
    const P0 = decay(3600), Cth = P0 * 3600 / 0.45, Kp = P0 / 0.08, Kn = P0 / 0.42, K0 = P0 / 40;
    const K = S.pump ? Kp + (S.pass ? Kn : 0) : S.pass ? Kn : K0, TMAX = 1.25;
    const adv = (sec) => { const n = Math.ceil(sec / 60); for (let i = 0; i < n; i++) { const h = sec / n; S.Tc += h * (decay(S.tsim) - K * S.Tc) / Cth; S.tsim += h; } S.Tc = clamp(S.Tc, 0, TMAX); };
    if (snap && S.tsim <= 3600) { adv(6 * 3600); }
    else if (dt > 0) { adv(600 * dt); }
    if (S.tsim > 2 * 86400) resetCool(S);
    if (!S.trace.length || S.tsim - S.trace[S.trace.length - 1][0] > 600) { S.trace.push([S.tsim, S.Tc]); if (S.trace.length > 400) S.trace.shift(); }
    const P = decay(S.tsim), hot = clamp(S.Tc / 1.0, 0, 1.3);
    // geometry
    const cx = phone ? W * 0.2 : W * 0.2, cy = phone ? H * 0.42 : H * 0.55, cw = phone ? W * 0.26 : W * 0.22, ch = phone ? H * 0.3 : H * 0.36;
    const hx = phone ? W * 0.62 : W * 0.56, hy = cy + ch * 0.12, hw = phone ? W * 0.16 : W * 0.08, hh = ch * 0.5;
    const px = phone ? W * 0.6 : W * 0.52, py = phone ? H * 0.1 : H * 0.12, pw = phone ? W * 0.34 : W * 0.22, ph = phone ? H * 0.09 : H * 0.12;
    // passive pool + loop (behind)
    const pOn = S.pass ? 1 : 0;
    ctx.save(); ctx.fillStyle = g.rgba(c.cool, 0.1 + 0.12 * pOn); ctx.strokeStyle = g.rgba(c.cool, 0.35 + 0.4 * pOn); ctx.lineWidth = 1.4;
    ctx.beginPath(); if (ctx.roundRect) ctx.roundRect(px - pw / 2, py - ph / 2, pw, ph, 8); else ctx.rect(px - pw / 2, py - ph / 2, pw, ph); ctx.fill(); ctx.stroke(); ctx.restore();
    g.label(phone ? "pool, up high" : "water pool, placed higher", px, py - ph / 2 - 12, { color: c.cool, size: fs - 1, alpha: 0.5 + 0.5 * pOn });
    const pLoop = [[cx + cw * 0.15, cy - ch / 2], [cx + cw * 0.15, py], [px - pw * 0.3, py], [px + pw * 0.3, py], [px + pw * 0.3, py + ph * 0.25], [cx + cw * 0.38, py + ph * 0.25 + 0.001], [cx + cw * 0.38, cy - ch / 2]];
    // hot leg rises (warm), cold leg returns (cool)
    g.poly([pLoop[0], pLoop[1], pLoop[2]], c.warm, 3, 0.25 + 0.45 * pOn); g.poly([pLoop[3], pLoop[4], pLoop[5], pLoop[6]], c.cool, 3, 0.25 + 0.45 * pOn);
    // main loop to the heat exchanger, with a pump
    const mLoop = [[cx + cw / 2, cy - ch * 0.15], [hx - hw / 2, cy - ch * 0.15], [hx - hw / 2, hy - hh / 2], [hx + hw / 2, hy - hh / 2], [hx + hw / 2, hy + hh / 2], [hx - hw * 0.2, cy + ch * 0.38], [cx + cw / 2, cy + ch * 0.38]];
    const mOn = S.pump ? 1 : 0;
    g.poly([mLoop[0], mLoop[1]], c.warm, 4, 0.35 + 0.5 * mOn); g.poly([[hx, cy + ch * 0.38], mLoop[6]], c.cool, 4, 0.35 + 0.5 * mOn);
    ctx.save(); ctx.fillStyle = g.rgba(c.soft, 0.12); ctx.strokeStyle = g.rgba(c.soft, 0.5); ctx.lineWidth = 1.2; ctx.beginPath(); if (ctx.roundRect) ctx.roundRect(hx - hw / 2, hy - hh / 2, hw, hh, 6); else ctx.rect(hx - hw / 2, hy - hh / 2, hw, hh); ctx.fill(); ctx.stroke(); ctx.restore();
    g.label(phone ? "cooler" : "heat exchanger", hx, hy + hh / 2 + 14, { color: c.soft, size: fs - 1 });
    g.line(hx, hy + hh / 2, hx, cy + ch * 0.38, c.cool, 4, 0.35 + 0.5 * mOn);
    const pmx = (cx + cw / 2 + hx) / 2, pmy = cy + ch * 0.38, pr = phone ? 11 : 14;
    geo.pump = { x: pmx, y: pmy, r: pr * 2.2 }; geo.pool = { x: px - pw / 2, y: py - ph / 2, w: pw, h: ph };
    g.glow(pmx, pmy, pr * 2, c.accent, 0.12 + 0.08 * Math.sin(S.time * 3));
    g.dot(pmx, pmy, pr, c.paper); g.ring(pmx, pmy, pr, mOn ? c.accent : c.faint, 2);
    S.pAng = (S.pAng || 0) + (mOn ? 9 : 0) * dt; for (let k = 0; k < 3; k++) { const a = S.pAng + k * TAU / 3; g.line(pmx, pmy, pmx + Math.cos(a) * pr * 0.75, pmy + Math.sin(a) * pr * 0.75, mOn ? c.accent : c.faint, 2); }
    g.label(mOn ? (phone ? "pump on" : "pump running") : (phone ? "pump off" : "pump stopped"), pmx, pmy + pr + 13, { color: mOn ? c.accent : c.soft, size: fs - 1, weight: 600 });
    // water in motion
    const along = (pts, f) => { let L = 0; const seg = []; for (let i = 1; i < pts.length; i++) { const l = Math.hypot(pts[i][0] - pts[i - 1][0], pts[i][1] - pts[i - 1][1]); seg.push(l); L += l; } let s = f * L; for (let i = 0; i < seg.length; i++) { if (s <= seg[i]) { const q = s / seg[i]; return [lerp(pts[i][0], pts[i + 1][0], q), lerp(pts[i][1], pts[i + 1][1], q), i / seg.length]; } s -= seg[i]; } return pts[pts.length - 1].concat(1); };
    S.fm = ((S.fm || 0) + dt * 0.22 * mOn) % 1; S.fp = ((S.fp || 0) + dt * 0.05 * pOn * clamp(0.4 + hot, 0.4, 1.2)) % 1;
    if (mOn) flow.forEach((u) => { const [x, y, q] = along(mLoop, (u + S.fm) % 1), col = q < 0.4 ? c.warm : c.cool; g.glow(x, y, 7, col, 0.35); g.dot(x, y, 2.8, col, 0.95); });
    if (pOn) pflow.forEach((u) => { for (let k = 0; k < 4; k++) { const [x, y, q] = along(pLoop, (u + S.fp - k * 0.006 + 1) % 1), col = q < 0.4 ? c.warm : c.cool; if (!k) g.glow(x, y, 10, col, 0.45); g.dot(x, y, 3 - k * 0.6, col, 0.95 - k * 0.2); } });
    // the core, glowing with decay heat
    core(g, S, cx, cy, cw, ch, P, 0, 1, phone, dt);
    // water moving up through the hot core (fast with pumps, a slow steady rise with natural circulation)
    { const fv = mOn ? 0.5 : pOn ? 0.16 : 0.02, q = rng(12); S.fi = ((S.fi || 0) + dt * fv) % 1;
      for (let k = 0; k < 34; k++) { const u = (q() + S.fi * (0.8 + 0.4 * q())) % 1, x = cx + (q() - 0.5) * cw * 0.84, yy = cy + ch * 0.44 - u * ch * 0.88, warm = u > 0.5;
        g.dot(x + Math.sin(S.time * 2 + k) * 1.5, yy, 2, warm ? c.warm : c.cool, (0.25 + 0.6 * fv / 0.5) * Math.sin(Math.PI * u)); } }
    g.glow(cx, cy, cw * 1.3, c.proton, 0.25 * smooth(0.6, 1.2, S.Tc));
    // boiling: bubbles rise through the vessel and steam wisps leave the top once the water gets too hot
    const boil = smooth(0.75, 1.15, S.Tc);
    if (boil > 0.01) {
      const nb = Math.round(40 * boil), q = rng(9);
      for (let k = 0; k < nb; k++) { const sp = 0.25 + 0.5 * q(), ph = q(), x = cx + (q() - 0.5) * cw * 0.8, yy = cy + ch * 0.45 - ((ph + S.time * sp) % 1) * ch * 0.9; g.ring(x + Math.sin(S.time * 4 + k) * 2, yy, 1.5 + 2.5 * q(), c.ink, 1, 0.55 * boil); }
      for (let k = 0; k < 10; k++) { const ph = (k / 10 + S.time * 0.18) % 1, x = cx + (k % 3 - 1) * cw * 0.25 + Math.sin(S.time + k) * 8, yy = cy - ch / 2 - ph * H * 0.22; g.glow(x, yy, 12 + 26 * ph, c.soft, 0.3 * boil * (1 - ph)); }
      g.label(phone ? "boiling" : "the water starts to boil", cx, cy - ch / 2 - 14, { color: c.proton, size: fs - 1, weight: 600, bg: true, alpha: boil });
    }
    // thermometer
    const tx = phone ? W * 0.9 : W * 0.8, tt = phone ? H * 0.3 : H * 0.2, tb = phone ? H * 0.66 : H * 0.74, ty = (v) => lerp(tb, tt, clamp(v / TMAX, 0, 1));
    ctx.save(); ctx.fillStyle = g.rgba(c.fission, 0.14); ctx.fillRect(tx - 16, ty(0.6), 32, ty(0) - ty(0.6)); ctx.restore();
    g.label("normal", tx - 20, ty(0.3), { color: c.fission, size: fs - 1, align: "right" });
    g.line(tx - 16, ty(1), tx + 16, ty(1), c.proton, 1.4, 0.8, [3, 3]); g.label(phone ? "too hot" : "too hot", tx - 20, ty(1), { color: c.proton, size: fs - 1, align: "right" });
    ctx.save(); ctx.strokeStyle = g.rgba(c.soft, 0.55); ctx.lineWidth = 11; ctx.lineCap = "round"; ctx.beginPath(); ctx.moveTo(tx, tt); ctx.lineTo(tx, tb); ctx.stroke(); const col = S.Tc > 1 ? c.proton : S.Tc > 0.6 ? c.warm : c.cool; ctx.strokeStyle = col; ctx.lineWidth = 6; ctx.beginPath(); ctx.moveTo(tx, tb); ctx.lineTo(tx, ty(S.Tc)); ctx.stroke(); ctx.restore();
    g.dot(tx, tb + 7, 10, col); g.glow(tx, ty(S.Tc), 16, col, 0.6);
    g.label(phone ? "temperature" : "core temperature", tx, tt - 16, { color: c.soft, size: fs - 1 });
    // trace of the last hours under the thermometer (desktop) / readouts
    const rd = { color: c.ink, size: fs + 1, weight: 600, serif: true, raw: true };
    const ly = phone ? H * 0.8 : H * 0.88;
    g.label(WT.trf("{a} after shutdown · heat {b} % of full power", fmtT(S.tsim), pct(P)), W * 0.5, ly, rd);
    const rising = S.trace.length > 2 && S.Tc - S.trace[Math.max(0, S.trace.length - 4)][1] > 0.004;
    const state = S.Tc >= TMAX - 0.01 ? (phone ? "too hot: cooling must be restored" : "too hot: the water would start to boil away; cooling must be restored") : rising ? (phone ? "temperature climbing" : "temperature climbing: the heat has nowhere to go") : S.pump ? (phone ? "pumps carry the heat away" : "steady: the pumps carry the heat away") : S.pass ? (phone ? "steady, with no pumps" : "steady: natural circulation carries the heat away") : "steady";
    g.label(state, W * 0.5, ly + fs + 12, { color: S.Tc > 1 ? c.proton : rising ? c.warm : c.fission, size: fs, weight: 600 });
    g.label("illustration", W - 6, H - 10, { color: c.faint, size: 10, align: "right" });
  }
})();
