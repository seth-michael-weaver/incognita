/* Decay chains and equilibrium. Scenes (S.mode):
 *   "gen"   = parent -> daughter -> stable granddaughter, a live sample (each atom decays with chance 1 - 2^(-dt/T) per frame)
 *             over the Bateman solution N1 = e^(-l1 t), N2 = l1/(l2 - l1) (e^(-l1 t) - e^(-l2 t)), N3 = 1 - N1 - N2.
 *             Half-lives here are illustrative seconds of animation.
 *   "sec"   = secular equilibrium: Ra-226 (1600 y) -> Rn-222 (3.8235 d) in a sealed jar. The radium activity is constant on
 *             this time scale; radon activity A_Rn = A_Ra (1 - e^(-l t)) reaches 97 % after five radon half-lives (19 d).
 *             Venting the jar lets the radon out and the growth starts again. Number of gas atoms drawn ~ A_Rn/A_Ra (picture).
 *   "tra"   = transient equilibrium in a Mo-99/Tc-99m generator: Mo-99 65.98 h -> Tc-99m 6.007 h, with 87.6 % of Mo-99 decays
 *             feeding Tc-99m (the rest go straight to the ground state). dN_Tc/dt = b l_Mo N_Mo - l_Tc N_Tc, integrated in
 *             small steps; elution ("milking") removes all Tc-99m (real columns give ~80-90 %). Tc activity peaks ~23 h after
 *             an elution, then follows the Mo down at b l_Tc/(l_Tc - l_Mo) = 0.96 of its activity.
 *   "chart" = the U-238 series on a chart of nuclides (N across, Z up): alpha = 2 down and 2 left, beta-minus = 1 up and
 *             1 left. Main branch only (Po-218 beta 0.02 %, Bi-214 alpha 0.02 %, Bi-210 alpha 1e-4 % ignored). Half-lives:
 *             NNDC NuDat 3 (ENSDF): U-238 4.468e9 y, Th-234 24.10 d, Pa-234m 1.159 min, U-234 2.455e5 y, Th-230 7.54e4 y,
 *             Ra-226 1600 y, Rn-222 3.8235 d, Po-218 3.098 min, Pb-214 27.06 min, Bi-214 19.9 min, Po-214 164.3 us,
 *             Pb-210 22.2 y, Bi-210 5.012 d, Po-210 138.38 d, Pb-206 stable. */
(function () {
  const { TAU, clamp, lerp, smooth, rng } = WT.util;
  const R = rng(19);
  // ---------- generic chain sample ----------
  const N0 = 170, P = [], st = new Uint8Array(N0); // 0 parent, 1 daughter, 2 granddaughter
  for (let i = 0; i < N0; i++) { const a = i * 2.39996 + R() * 0.25, rr = Math.sqrt((i + 0.5) / N0); P.push([rr * Math.cos(a), rr * Math.sin(a), R() * TAU]); }
  const sim = { t: 0, n: [N0, 0, 0], hist: [], acc: 0, pause: 0 }, fl = [];
  function refill() { st.fill(0); sim.t = 0; sim.n = [N0, 0, 0]; sim.hist = [[0, N0, 0, 0]]; sim.acc = 0; sim.pause = 0; }
  refill();
  function bate(t, T1, T2) {
    const l1 = Math.LN2 / T1, l2 = Math.LN2 / T2, n1 = Math.exp(-l1 * t);
    const n2 = Math.abs(l2 - l1) < 1e-6 ? l1 * t * Math.exp(-l1 * t) : l1 / (l2 - l1) * (Math.exp(-l1 * t) - Math.exp(-l2 * t));
    return [n1, n2, 1 - n1 - n2];
  }
  function advance(S, h, geo) {
    const p1 = 1 - 2 ** (-h / S.T1), p2 = 1 - 2 ** (-h / S.T2);
    for (let i = 0; i < N0; i++) {
      if (st[i] === 1 && R() < p2) { st[i] = 2; sim.n[1]--; sim.n[2]++; if (geo) fl.push({ x: geo.x + P[i][0] * geo.r, y: geo.y + P[i][1] * geo.r, t: S.time, k: 1 }); }
      else if (st[i] === 0 && R() < p1) { st[i] = 1; sim.n[0]--; sim.n[1]++; if (geo) fl.push({ x: geo.x + P[i][0] * geo.r, y: geo.y + P[i][1] * geo.r, t: S.time, k: 0 }); }
    }
    while (fl.length > 60) fl.shift();
    sim.t += h; sim.acc += h; if (sim.acc >= 0.1) { sim.acc = 0; sim.hist.push([sim.t, ...sim.n]); }
  }
  // ---------- radium jar ----------
  const LRN = Math.LN2 / 3.8235; // per day
  const GAS = []; for (let i = 0; i < 70; i++) GAS.push([R(), R(), R() * TAU, 0.5 + R()]);
  // ---------- Mo/Tc generator ----------
  const LMO = Math.LN2 / 65.98, LTC = Math.LN2 / 6.007, BR = 0.876, TEND = 168;
  const gen = { t: 0, nTc: 0, hist: [], milks: [], acc: 0 };
  function genReset() { gen.t = 0; gen.nTc = 0; gen.hist = [[0, 0]]; gen.milks = []; gen.acc = 0; }
  genReset();
  function genStep(h) { // hours
    const nMo = Math.exp(-LMO * gen.t) / LMO; // N_Mo with A_Mo(0) = 1
    gen.nTc += (BR * LMO * nMo - LTC * gen.nTc) * h; gen.t += h; gen.acc += h;
    if (gen.acc >= 0.5) { gen.acc = 0; gen.hist.push([gen.t, LTC * gen.nTc]); }
  }
  // ---------- U-238 series ----------
  const U = [
    [92, 146, "U", 238, "4.5 billion yr", "a"], [90, 144, "Th", 234, "24 days", "b"], [91, 143, "Pa", 234, "1.2 min", "b"], [92, 142, "U", 234, "245,000 yr", "a"],
    [90, 140, "Th", 230, "75,000 yr", "a"], [88, 138, "Ra", 226, "1600 yr", "a"], [86, 136, "Rn", 222, "3.8 days", "a"], [84, 134, "Po", 218, "3.1 min", "a"],
    [82, 132, "Pb", 214, "27 min", "b"], [83, 131, "Bi", 214, "20 min", "b"], [84, 130, "Po", 214, "164 µs", "a"], [82, 128, "Pb", 210, "22 years", "b"],
    [83, 127, "Bi", 210, "5 days", "b"], [84, 126, "Po", 210, "138 days", "a"], [82, 124, "Pb", 206, "stable", ""],
  ];
  const EM = []; // emitted alphas and electrons
  const STABLE = [[82, 124], [82, 125], [82, 126], [83, 126]]; // Pb-206/207/208, Bi-209 (half-life 2e19 y)

  WT.chapter("chains", {
    level: 1, num: "Lesson 4", title: "Decay chains and equilibrium", short: "Decay chains",
    html: `
<div class="step">
  <h3>Parent, daughter, granddaughter</h3>
  <p>Often the new nucleus is unstable too. The parent decays into a daughter, which decays into a stable granddaughter. Daughters pile up and then fade; how high they pile depends on how quickly they decay compared with the parent.</p>
  <div class="ctl"><label for="ch-t2">Daughter half-life (s)</label><input id="ch-t2" type="range" data-bind="T2" data-instant min="0.5" max="9" step="0.5" value="1.5"><output data-show="T2" data-fmt="1"></output></div>
  <div class="btns"><button class="btn ghost" data-act="refill">Fresh sample</button></div>
</div>
<div class="step">
  <h3>Secular equilibrium: radium and radon</h3>
  <p>Radium-226 lasts 1600 years; its daughter, radon-222 gas, only 3.8 days. In a sealed jar the radon builds up until it decays as fast as it is made: <i>A</i><sub>Rn</sub> = <i>A</i><sub>Ra</sub>(1 − e<sup>−λt</sup>), with λ the radon decay rate. After a few weeks both pop at the same rate.</p>
  <div class="btns"><button class="btn" data-act="vent">Open the jar</button></div>
</div>
<div class="step">
  <h3>Transient equilibrium: the technetium cow</h3>
  <p>Hospitals get a column of molybdenum-99 (66 hours) that keeps making technetium-99m (6 hours), the most used medical tracer. Wash the technetium out each morning and it grows back, following the slowly fading molybdenum.</p>
  <div class="btns"><button class="btn" data-act="milk">Milk the generator</button><button class="btn ghost" data-act="genre">New generator</button></div>
</div>
<div class="step">
  <h3>Down the uranium chain</h3>
  <p>Uranium-238 takes fourteen steps to become stable lead. An alpha decay moves two steps down and two left on this chart, a beta decay one up and one left. In old, undisturbed uranium ore every member pops at the same rate.</p>
  <div class="btns"><button class="btn" data-act="next">Next decay</button><button class="btn ghost" data-act="restart">Start again</button></div>
</div>`,
    setup(S) {
      S.set("mode", "gen"); S.set("T1", 3); S.set("T2", 1.5); S.ts = 0; S.vent = -9; S.set("cs", 0); S.cur = 0;
      S.on("refill", () => refill());
      S.on("vent", () => { S.ts = 0; S.vent = S.time; });
      S.on("milk", () => { const a = LTC * gen.nTc; gen.milks.push([gen.t, a, S.time]); gen.nTc = 0; gen.hist.push([gen.t, 0]); });
      S.on("genre", () => genReset());
      S.on("next", () => { S.cur = Math.min(U.length - 1, S.cur + 1); S.to("cs", S.cur); S._lastT = S.time; });
      S.on("restart", () => { S.cur = 0; S.to("cs", 0); S._last = 0; S._lastT = S.time; });
    },
    steps: [
      (S) => { S.set("mode", "gen"); },
      (S) => { S.set("mode", "sec"); S.ts = 0; },
      (S) => { S.set("mode", "tra"); },
      (S) => { S.set("mode", "chart"); },
    ],
    frame(g, S, dt) {
      const { W, H, c, ctx } = g, phone = W < 600, fs = phone ? 11 : 13, snap = document.body.classList.contains("shot"), mode = S.mode;
      const COL = [c.warm, c.alpha, c.soft];
      if (!S._cv) { S._cv = ctx.canvas; const cv = S._cv;
        const inBox = (b, x, y) => b && x > b.x - 8 && x < b.x + b.w + 8 && y > b.y - 24 && y < b.y + b.h + 8;
        const onNuc = (x, y) => { if (S.mode !== "chart" || !S._ch) return false; const { PX, PY, rn } = S._ch, cu = U[S.cur]; return Math.hypot(x - PX(cu[1]), y - PY(cu[0])) < rn * 3 + 10; };
        const what = (x, y) => (S.mode === "sec" && inBox(S._jar, x, y) ? "vent" : S.mode === "tra" && inBox(S._col, x, y) ? "milk" : onNuc(x, y) ? "next" : S.mode === "gen" && S._smp && Math.hypot(x - S._smp.x, y - S._smp.y) < S._smp.r ? "refill" : "");
        WT.grab(cv, { down: (x, y) => { const w = what(x, y); if (w && S.handlers[w]) S.handlers[w](); return false; }, hover: (x, y) => { cv.style.cursor = what(x, y) ? "pointer" : ""; } });
      }


      if (mode === "gen") {
        // ---------- parent, daughter, granddaughter ----------
        const sr = Math.min(W * (phone ? 0.27 : 0.22), H * 0.2), sx = W * 0.5, sy = H * 0.07 + sr, geo = { x: sx, y: sy, r: sr }, _sm = (S._smp = geo), br = Math.max(2.4, sr / Math.sqrt(N0) * 0.86), TM = 24;
        if (snap && sim.t === 0) while (sim.t < 4.5) advance(S, 0.05, null);
        if (!snap) { if (sim.t > TM) { sim.pause += dt; if (sim.pause > 1.2) refill(); } else { let l = dt; while (l > 1e-6) { const h = Math.min(l, 0.02); advance(S, h, geo); l -= h; } } }
        g.glow(sx, sy, sr * 1.5, c.warm, 0.06 + 0.18 * sim.n[0] / N0); g.glow(sx, sy, sr * 1.3, c.alpha, 0.2 * sim.n[1] / N0);
        for (let i = 0; i < N0; i++) {
          const x = sx + P[i][0] * sr, y = sy + P[i][1] * sr, s = st[i], j = s < 2 ? Math.sin(S.time * 7 + P[i][2] * 9) * 0.6 : 0;
          if (s < 2) g.ball(x + j, y - j * 0.5, br, COL[s], 0.96); else g.dot(x, y, br * 0.6, c.soft, 0.35);
        }
        for (const f of fl) { const a = S.time - f.t; if (a < 0.45) g.glow(f.x, f.y, br * 2 + a * 36, f.k ? c.alpha : c.photon, 0.7 * (1 - a / 0.45)); }
        // legend
        const ly = sy + sr + (phone ? 14 : 22), names = [`parent (${S.T1.toFixed(0)} s)`, `daughter (${S.T2.toFixed(1)} s)`, "granddaughter (stable)"];
        const xs = phone ? [W * 0.17, W * 0.5, W * 0.83] : [W * 0.25, W * 0.5, W * 0.75];
        names.forEach((s, k) => { g.ball(xs[k] - (phone ? 0 : 0), ly, 4.5, COL[k], k === 2 ? 0.5 : 1); g.label(phone ? [`parent ${sim.n[0]}`, `daughter ${sim.n[1]}`, `stable ${sim.n[2]}`][k] : [`parent (${S.T1.toFixed(0)} s): ${sim.n[0]}`, `daughter (${S.T2.toFixed(1)} s): ${sim.n[1]}`, `granddaughter (stable): ${sim.n[2]}`][k], xs[k], ly + 14, { color: k === 2 ? c.soft : COL[k], size: fs - 1, weight: 600 }); });
        // landscape: amounts over time, expected (lines and ground) and counted (dots)
        const x0 = W * 0.08, x1 = W * 0.95, yT = H * (phone ? 0.64 : 0.6), yB = H * 0.88, X = (t) => x0 + (x1 - x0) * t / TM, Y = (f) => lerp(yB, yT, f);
        const curves = [[], [], []]; for (let i = 0; i <= 120; i++) { const t = TM * i / 120, b = bate(t, S.T1, S.T2); for (let k = 0; k < 3; k++) curves[k].push([X(t), Y(b[k])]); }
        g.line(x0, yB, x1, yB, c.line, 1);
        g.clip(0, 0, W, yB); g.ground(curves[1], c.alpha, (yB - yT) * 0.8, 0.3); ctx.restore();
        curves.forEach((p, k) => g.poly(p, COL[k], k === 1 ? 2.6 : 1.8, k === 2 ? 0.6 : 0.95));
        for (let i = 0; i < sim.hist.length; i += 3) { const h = sim.hist[i]; for (let k = 0; k < 2; k++) g.dot(X(h[0]), Y(h[k + 1] / N0), 1.8, COL[k], 0.7); }
        const tn = Math.min(sim.t, TM); g.line(X(tn), yT, X(tn), yB, c.ink, 1, 0.25);
        // where the daughter peaks
        const l1 = Math.LN2 / S.T1, l2 = Math.LN2 / S.T2, tp = Math.abs(l2 - l1) < 1e-6 ? 1 / l1 : Math.log(l2 / l1) / (l2 - l1), pk = bate(tp, S.T1, S.T2)[1];
        if (tp < TM) { g.dot(X(tp), Y(pk), 4, c.alpha); g.label(`daughter peaks: ${Math.round(pk * 100)} %`, X(tp) + 8, Y(pk) - 12, { color: c.alpha, size: fs - 1, weight: 600, align: "left", bg: true }); }
        [0, 6, 12, 18, 24].forEach((t) => g.label(`${t} s`, X(t), yB + 12, { color: c.soft, size: fs - 2 }));
        g.label("illustrative half-lives", W - 6, H - 10, { color: c.faint, size: 10, align: "right" });
        return;
      }

      if (mode === "sec") {
        // ---------- radium jar ----------
        if (!snap) S.ts = Math.min(40, S.ts + dt * 2); else if (S.ts === 0) S.ts = 8;
        const f = 1 - Math.exp(-LRN * S.ts);
        const jx = W * (phone ? 0.05 : 0.06), jw = W * (phone ? 0.36 : 0.36), jy = H * 0.1, jh = H * (phone ? 0.62 : 0.62);
        S._jar = { x: jx, y: jy, w: jw, h: jh };
        ctx.save(); ctx.beginPath(); if (ctx.roundRect) ctx.roundRect(jx, jy, jw, jh, 18); else ctx.rect(jx, jy, jw, jh);
        ctx.fillStyle = g.rgba(c.alpha, 0.04 + 0.08 * f); ctx.fill(); ctx.strokeStyle = g.rgba(c.soft, 0.6); ctx.lineWidth = 2; ctx.stroke(); ctx.restore();
        // lid (lifts when vented)
        const lift = clamp(1 - (S.time - S.vent) / 1.4, 0, 1) * 18;
        ctx.save(); ctx.fillStyle = g.rgba(c.soft, 0.55); ctx.fillRect(jx + jw * 0.2, jy - 8 - lift, jw * 0.6, 8); ctx.restore();
        // radium salt at the bottom
        const q = rng(3);
        g.glow(jx + jw / 2, jy + jh - 14, jw * 0.6, c.warm, 0.3 + 0.05 * Math.sin(S.time * 2));
        for (let i = 0; i < 34; i++) { const x = jx + 14 + q() * (jw - 28), y = jy + jh - 12 - q() * 22, br = phone ? 4 : 5.5; g.glow(x, y, br * 2.6, c.warm, 0.3); g.ball(x, y, br, c.warm); }
        // fresh radon atoms rising out of the salt, and radon atoms popping in the gas (rate grows with the radon activity)
        for (let i = 0; i < 8; i++) { const u = ((S.time * 0.35 + i / 8) % 1), x = jx + jw * (0.15 + 0.7 * ((i * 0.37) % 1)) + Math.sin(S.time * 2 + i) * 4; g.ball(x, jy + jh - 30 - u * jh * 0.3, 3.4, c.alpha, 1 - u); }
        g.clip(jx, jy, jw, jh); g.glow(jx + jw / 2, jy + jh * 0.45, jw * 0.8, c.alpha, 0.22 * f); g.ctx.restore();
        // radon gas atoms
        const ng = Math.round(GAS.length * f);
        for (let i = 0; i < ng; i++) { const [a, b, ph, sp] = GAS[i]; const x = jx + 12 + (jw - 24) * (0.5 + 0.45 * Math.sin(S.time * 0.5 * sp + ph + a * 6)), y = jy + 14 + (jh - 50) * (0.5 + 0.45 * Math.cos(S.time * 0.4 * sp + ph * 1.7 + b * 5)); const br = phone ? 3.6 : 4.8, pop = ((S.time * 0.7 + a * 7.3) % 1) < 0.06 * f; g.glow(x, y, br * (pop ? 5 : 2.4), pop ? "#ffffff" : c.alpha, pop ? 0.7 : 0.35); g.ball(x, y, br, c.alpha); }
        // escaping gas after a vent
        const va = S.time - S.vent; if (va < 1.6) for (let i = 0; i < 24; i++) { const [a, , ph] = GAS[i]; g.ball(jx + jw * (0.3 + 0.4 * a), jy - va * 120 * (0.6 + a) - 10, 3, c.alpha, 1 - va / 1.6); }
        g.label("radium-226", jx + jw / 2, jy + jh + 14, { color: c.warm, size: fs, weight: 600 });
        g.label("radon-222 gas", jx + jw / 2, jy + 22, { color: c.alpha, size: fs - 1, weight: 600, alpha: f > 0.05 ? 1 : 0.4, bg: true });
        // landscape: activities
        const x0 = jx + jw + (phone ? 30 : 46), x1 = W * 0.95, yT = H * 0.2, yB = H * 0.72, TD = 40, X = (t) => x0 + (x1 - x0) * t / TD, Y = (v) => lerp(yB, yT, v);
        const pts = []; for (let i = 0; i <= 100; i++) { const t = TD * i / 100; pts.push([X(t), Y(1 - Math.exp(-LRN * t))]); }
        g.line(x0, yB, x1, yB, c.line, 1);
        const now = pts.filter((p) => p[0] <= X(S.ts)); now.push([X(S.ts), Y(f)]);
        g.clip(0, 0, W, yB); g.ground(now, c.alpha, (yB - yT) * 0.9, 0.32); ctx.restore(); g.poly(pts, c.alpha, 1.3, 0.35, [4, 4]); g.poly(now, c.alpha, 2.6, 1);
        g.line(x0, Y(1), x1, Y(1), c.warm, 2.4, 0.95); g.label(phone ? "radium" : "radium activity", x1, Y(1) - 11, { color: c.warm, size: fs - 1, weight: 600, align: "right" });
        g.dot(X(S.ts), Y(f), 5, c.alpha); g.glow(X(S.ts), Y(f), 16, c.alpha, 0.5);
        for (let k = 1; k <= 5; k++) { const t = 3.8235 * k; if (t < TD) g.line(X(t), yB, X(t), yB + 4, c.soft, 1, 0.6); }
        [0, 10, 20, 30, 40].forEach((t) => g.label(phone && t === 40 ? "40 d" : `${t}`, X(t), yB + 14, { color: c.soft, size: fs - 2 }));
        if (!phone) g.label("days →", x1, yB + 30, { color: c.soft, size: fs - 1, align: "right" });
        g.label(phone ? "radon" : "radon activity", X(Math.min(S.ts, 30)) + 4, Y(f) + 16, { color: c.alpha, size: fs - 1, weight: 600, align: "left", bg: true });
        g.label(`day ${Math.floor(S.ts)}: radon at ${Math.round(100 * f)} % of radium`, W * 0.5, H * 0.86, { color: c.ink, size: fs + 2, weight: 600, serif: true });
        g.label(phone ? "A(Rn) = A(Ra) × (1 − exp(−λt))" : "A(radon) = A(radium) × (1 − exp(−λt))", W * 0.5, H * 0.93, { color: c.soft, size: fs, italic: true, serif: true });
        return;
      }

      if (mode === "tra") {
        // ---------- Mo-99 / Tc-99m generator ----------
        if (snap && gen.t === 0) { for (let i = 0; i < 400; i++) { genStep(0.1); if (Math.abs(gen.t - 24) < 0.05 || Math.abs(gen.t - 48) < 0.05) { gen.milks.push([gen.t, LTC * gen.nTc, -9]); gen.nTc = 0; gen.hist.push([gen.t, 0]); } } }
        if (!snap) { let l = dt * 4; while (l > 1e-6) { const h = Math.min(l, 0.1); genStep(h); l -= h; } if (gen.t > TEND) genReset(); }
        const aMo = Math.exp(-LMO * gen.t), aTc = LTC * gen.nTc;
        const cx = W * (phone ? 0.17 : 0.2), cw = W * (phone ? 0.2 : 0.2), cy0 = H * 0.1, ch = H * (phone ? 0.5 : 0.52);
        S._col = { x: cx - cw / 2, y: cy0, w: cw, h: ch };
        // column
        { const sh = phone ? 7 : 11; ctx.save(); const lg = ctx.createLinearGradient(cx - cw / 2 - sh, 0, cx + cw / 2 + sh, 0); lg.addColorStop(0, g.rgba(c.faint, 0.9)); lg.addColorStop(0.25, g.rgba("#ffffff", 0.35)); lg.addColorStop(0.5, g.rgba(c.faint, 0.75)); lg.addColorStop(1, g.rgba("#000000", 0.35));
          ctx.fillStyle = lg; ctx.beginPath(); if (ctx.roundRect) ctx.roundRect(cx - cw / 2 - sh, cy0 - sh, cw + 2 * sh, ch + 2 * sh, 14); else ctx.rect(cx - cw / 2 - sh, cy0 - sh, cw + 2 * sh, ch + 2 * sh); ctx.fill(); ctx.restore(); } // lead pot
        ctx.save(); ctx.beginPath(); if (ctx.roundRect) ctx.roundRect(cx - cw / 2, cy0, cw, ch, 10); else ctx.rect(cx - cw / 2, cy0, cw, ch);
        ctx.fillStyle = c.paper; ctx.fill(); ctx.fillStyle = g.rgba(c.cool, 0.08); ctx.fill(); ctx.strokeStyle = g.rgba(c.soft, 0.6); ctx.lineWidth = 1.6; ctx.stroke(); ctx.restore();
        g.clip(cx - cw / 2, cy0, cw, ch); g.glow(cx, cy0 + ch * 0.6, cw * 1.1, c.warm, 0.12 + 0.25 * aMo); g.glow(cx, cy0 + ch * 0.6, cw, c.fission, 0.25 * aTc); g.ctx.restore();
        const q = rng(8), nMoD = Math.round(30 * aMo + 4), nTcD = Math.round(26 * aTc / 0.96);
        for (let i = 0; i < 34; i++) { const x = cx - cw / 2 + 8 + q() * (cw - 16), y = cy0 + ch * 0.3 + q() * ch * 0.62; if (i < nMoD) { const fl = ((S.time * 1.3 + i * 0.618) % 1) < 0.05 * aMo; g.glow(x, y, fl ? 18 : 10, fl ? "#ffffff" : c.warm, fl ? 0.7 : 0.3); g.ball(x, y, phone ? 4 : 5.5, c.warm); } }
        for (let i = 0; i < Math.min(40, nTcD); i++) { const x = cx - cw / 2 + 8 + q() * (cw - 16), y = cy0 + ch * 0.3 + q() * ch * 0.62 + Math.sin(S.time * 2 + i) * 1.5; g.glow(x, y, 9, c.fission, 0.4); g.ball(x, y, phone ? 3 : 4, c.fission); }
        // last elution flowing into a vial
        const vx = cx, vy = cy0 + ch + (phone ? 30 : 46), lastM = gen.milks[gen.milks.length - 1], ma = lastM ? S.time - lastM[2] : 9;
        if (ma < 1.5) for (let i = 0; i < 12; i++) { const s = ((ma * 1.6 + i / 12) % 1); g.ball(vx, lerp(cy0 + ch, vy - 10, s), 2.6, c.fission, 1 - ma / 1.5); }
        ctx.save(); ctx.beginPath(); if (ctx.roundRect) ctx.roundRect(vx - 16, vy - 14, 32, 30, 7); else ctx.rect(vx - 16, vy - 14, 32, 30); ctx.fillStyle = g.rgba(c.fission, lastM ? 0.35 : 0.08); ctx.fill(); ctx.strokeStyle = g.rgba(c.soft, 0.6); ctx.stroke(); ctx.restore();
        if (lastM) g.glow(vx, vy, 30, c.fission, 0.3 * Math.exp(-LTC * (gen.t - lastM[0])));
        g.label("Mo-99", cx, cy0 - (phone ? 7 : 11) - 12, { color: c.warm, size: fs, weight: 600, bg: true });
        g.label(phone ? "Tc-99m out" : "Tc-99m to the patient", vx, vy + 26, { color: c.fission, size: fs - 1, weight: 600 });
        // landscape: activities over a week
        const x0 = W * (phone ? 0.38 : 0.4), x1 = W * 0.95, yT = H * 0.14, yB = H * 0.7, X = (t) => x0 + (x1 - x0) * t / TEND, Y = (v) => lerp(yB, yT, v);
        const mo = []; for (let i = 0; i <= 100; i++) { const t = TEND * i / 100; mo.push([X(t), Y(Math.exp(-LMO * t))]); }
        g.line(x0, yB, x1, yB, c.line, 1);
        g.poly(mo, c.warm, 2.4, 0.95);
        const tc = gen.hist.map(([t, a]) => [X(t), Y(a)]); tc.push([X(gen.t), Y(aTc)]);
        g.clip(0, 0, W, yB); g.ground(tc, c.fission, (yB - yT) * 0.8, 0.3); ctx.restore(); g.poly(tc, c.fission, 2.4, 1);
        // no-milking reference: Tc follows Mo down (transient equilibrium)
        const ref = []; for (let i = 0; i <= 100; i++) { const t = TEND * i / 100; ref.push([X(t), Y(BR * LTC / (LTC - LMO) * (Math.exp(-LMO * t) - Math.exp(-LTC * t)))]); }
        g.poly(ref, c.fission, 1.2, 0.45, [4, 4]);
        g.dot(X(gen.t), Y(aTc), 4.5, c.fission); g.glow(X(gen.t), Y(aTc), 14, c.fission, 0.5); g.dot(X(gen.t), Y(aMo), 4, c.warm);
        g.label(phone ? "Mo-99" : "molybdenum-99", X(TEND * 0.3) + 6, Y(Math.exp(-LMO * TEND * 0.3)) - 6, { color: c.warm, size: fs - 1, weight: 600, align: "left" });
        if (!phone) g.label("dashed: never milked", X(TEND * 0.62), Y(0.96 * Math.exp(-LMO * TEND * 0.62)) + 14, { color: c.fission, size: fs - 2, align: "left" });
        [0, 1, 2, 3, 4, 5, 6, 7].forEach((d) => { if (!phone || d % 2 === 0 || d === 7) g.label(phone && d === 7 ? "7 d" : `${d}`, X(d * 24), yB + 12, { color: c.soft, size: fs - 2 }); });
        if (!phone) g.label("days →", x1, yB + 28, { color: c.soft, size: fs - 1, align: "right" });
        g.label("activity", x0, yT - 12, { color: c.soft, size: fs - 1, align: "left" });
        const hs = gen.milks.length ? gen.t - gen.milks[gen.milks.length - 1][0] : gen.t;
        g.label(`${hs.toFixed(0)} h since last milking · Tc-99m at ${Math.round(100 * aTc / aMo)} % of Mo-99`, W * 0.5, H * (phone ? 0.88 : 0.86), { color: c.ink, size: fs + 1, weight: 600, serif: true });
        if (!phone) g.label("regrows to its peak in about 23 hours", W * 0.5, H * 0.92, { color: c.soft, size: fs - 1 });
        return;
      }

      // ---------- the U-238 series on the chart of nuclides: a nucleus walking down, spitting alphas and electrons ----------
      if (snap && S.cur === 0) { S.cur = 6; S.set("cs", 6); S._last = 6; EM.push({ k: "a", i: 5, t: S.time - 0.35 }); }
      const n0 = 123, n1 = 147, z0 = 81, z1 = 93, mx = W * 0.07;
      const cx = (W - 2 * mx) / (n1 - n0), cyS = H * (phone ? 0.6 : 0.64) / (z1 - z0), ox = mx, oy = H * 0.05;
      const PX = (n) => ox + (n - n0) * cx, PY = (z) => oy + (z1 - z) * cyS, rn = Math.max(3.6, Math.min(cx, cyS) * 0.44);
      S._ch = { PX, PY, rn };
      // auto-walk when left alone; tapping the nucleus or "Next decay" steps it by hand
      if (S._last === undefined) { S._last = S.cur; S._lastT = S.time; }
      if (!snap && S.time - S._lastT > (S.cur === U.length - 1 ? 4 : 2.4)) { if (S.cur === U.length - 1) { S.cur = 0; S.set("cs", 0); S._last = 0; } else { S.cur++; S.to("cs", S.cur); } S._lastT = S.time; }
      if (S.cur !== S._last) { if (S.cur > S._last) EM.push({ k: U[S._last][5], i: S._last, t: S.time }); S._last = S.cur; S._lastT = S.time; if (S.cur === U.length - 1) S._endT = S.time; }
      while (EM.length > 12) EM.shift();
      if (snap && EM.length) EM[EM.length - 1].t = S.time - 0.32;
      // rows and a faint valley of stability
      for (let z = z0 + 1; z < z1; z++) { g.line(PX(n0 + 0.5), PY(z), PX(n1 - 0.5), PY(z), c.line, 1, 0.45); g.label(["Pb", "Bi", "Po", "At", "Rn", "Fr", "Ra", "Ac", "Th", "Pa", "U"][z - 82], ox - 4, PY(z), { color: c.soft, size: fs - 2, align: "right" }); }
      for (const [z, n] of STABLE) { g.glow(PX(n), PY(z), rn * 2, c.soft, 0.25); g.ball(PX(n), PY(z), rn * 0.8, c.faint, 0.8); }
      // the path
      for (let i = 0; i < U.length - 1; i++) {
        const [za, na] = U[i], [zb, nb] = U[i + 1], done = i < S.cs - 0.01, col = U[i][5] === "a" ? c.alpha : c.accent;
        g.line(PX(na), PY(za), PX(nb), PY(zb), col, done ? 2.4 : 1.2, done ? 0.8 : 0.3, done ? null : [3, 4]);
      }
      // each member as a lit nucleus; visited ones glow, unstable ones shimmer
      U.forEach(([z, n, sym, a, ht, m], i) => {
        const on = i <= S.cs + 0.01, col = m === "a" ? c.alpha : m === "b" ? c.accent : c.fission, x = PX(n), y = PY(z);
        if (on) g.glow(x, y, rn * 2.4, col, 0.25 + 0.1 * Math.sin(S.time * 4 + i));
        g.ball(x, y, rn, col, on ? 1 : 0.4);
        if (!phone && cx > 22) g.label(`${a}`, x, y + rn + 8, { color: on ? c.ink : c.soft, size: 10, weight: 600, alpha: on ? 1 : 0.6 });
      });
      // emitted particles: alpha = a helium nucleus flying off, beta = a fast electron streak
      for (const e of EM) {
        const a = S.time - e.t, [z, n] = U[e.i], x = PX(n), y = PY(z); if (a > 1.6) continue;
        if (a < 0.6) { g.ring(x, y, rn + a * 90, e.k === "a" ? c.alpha : c.accent, 3 * (1 - a / 0.6), 1 - a / 0.6); g.glow(x, y, rn * 3 + a * 40, "#ffffff", 0.5 * (1 - a / 0.6)); }
        if (e.k === "a") { const d = a * (phone ? 110 : 170); g.nucleus(x + d * 0.7, y - d * 0.7, rn * 1.0, { N: 4, Z: 2, seed: 3, jiggle: 0, alpha: 1 - a / 1.6 }); g.glow(x + d * 0.7, y - d * 0.7, rn * 2, c.alpha, 0.4 * (1 - a / 1.6)); }
        else { const d = a * (phone ? 300 : 460); if (a < 0.9) { g.line(x + (d - 40) * 0.8, y + (d - 40) * 0.6, x + d * 0.8, y + d * 0.6, c.accent, 2.5, 1 - a / 0.9); g.dot(x + d * 0.8, y + d * 0.6, 3, c.accent, 1 - a / 0.9); g.glow(x + d * 0.8, y + d * 0.6, 10, c.accent, 0.5 * (1 - a / 0.9)); } }
      }
      // the walking nucleus
      const k = clamp(S.cs, 0, U.length - 1), i0 = Math.floor(k), i1 = Math.min(U.length - 1, i0 + 1), s = k - i0;
      const bx = lerp(PX(U[i0][1]), PX(U[i1][1]), s), by = lerp(PY(U[i0][0]), PY(U[i1][0]), s), cu = U[S.cur], fin = cu[5] === "";
      g.glow(bx, by, rn * 4.5, fin ? c.fission : c.warm, 0.4 + 0.12 * Math.sin(S.time * 5)); g.nucleus(bx, by, rn * 1.5, { N: 26, Z: 11, seed: 5, t: S.time, jiggle: fin ? 0.2 : 0.8, heat: fin ? 0.5 : 1.4 });
      g.ring(bx, by, rn * 1.5 + 5 + 2 * Math.sin(S.time * 3), c.ink, 1.2, 0.5);
      if (fin && S._endT !== undefined) { const a = S.time - S._endT; if (a < 1.5) { g.ring(bx, by, rn * 2 + a * W * 0.4, c.fission, 4 * (1 - a / 1.5), 1 - a / 1.5); g.glow(bx, by, 40 + a * 220, c.fission, 0.35 * (1 - a / 1.5)); } }
      // axes and legend
      const yAx = PY(z0 + 0.35);
      g.label("neutrons →", PX(n1 - 1), yAx, { color: c.soft, size: fs - 1, align: "right" });
      g.label("protons ↑", ox - 4, PY(z1 - 0.4), { color: c.soft, size: fs - 1, align: "left" });
      const LGY = yAx + (phone ? 22 : 30);
      g.dot(W * 0.1, LGY, 5, c.alpha); g.label(phone ? "alpha: −2 p, −2 n" : "alpha: loses 2 protons and 2 neutrons", W * 0.1 + 10, LGY, { color: c.alpha, size: fs - 1, weight: 600, align: "left" });
      g.dot(W * 0.58, LGY, 5, c.accent); g.label(phone ? "beta: n → p" : "beta: a neutron becomes a proton", W * 0.58 + 10, LGY, { color: c.accent, size: fs - 1, weight: 600, align: "left" });
      // stable ends: a legend line of its own (beside the Pb row it sat on lead-206's mass number)
      g.dot(W * 0.1, LGY + (phone ? 18 : 22), 5, c.faint); g.label("grey: stable", W * 0.1 + 10, LGY + (phone ? 18 : 22), { color: c.soft, size: fs - 1, weight: 600, align: "left" });
      // the current member, written large below
      const name = `${cu[2]}-${cu[3]}${cu[2] === "Pa" ? "m" : ""}`;
      g.label(fin ? `${name}: stable, the chain ends` : cu[5] === "a" ? `${name} · half-life ${cu[4]} · alpha next` : `${name} · half-life ${cu[4]} · beta next`, W * 0.5, H * (phone ? 0.87 : 0.86), { color: fin ? c.fission : c.ink, size: fs + 3, weight: 700, serif: true });
      g.label(`step ${S.cur} of ${U.length - 1} · tap the nucleus`, W * 0.5, H * (phone ? 0.94 : 0.92), { color: c.soft, size: fs - 1 });
    },
  });
})();
