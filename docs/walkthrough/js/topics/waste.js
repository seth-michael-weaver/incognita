/* Spent fuel over time. Scenes (S.mode):
 *   "mix"  = what comes out of a light-water reactor after ~50 GWd/t: about 94 % uranium, 5 % fission products, 1 % plutonium,
 *            0.1 % minor actinides (Np, Am, Cm) by mass (OECD-NEA 2011, "Potential Benefits and Impacts of Advanced Nuclear
 *            Fuel Cycles with Actinide Partitioning and Transmutation", NEA No. 6894). 400 atoms drawn: 376 / 19 / 4 / 1.
 *   "time" = radiotoxicity (ingestion dose, Sv) of one tonne of spent fuel divided by that of the natural uranium ore mined to
 *            make it, against time on a log axis from 1 to 10^6 years. Illustrative shape: sums of decays with real half-lives,
 *            amplitudes chosen to reproduce the published curves (OECD-NEA 2011, fig. 2.x; also NEA 2006 "Physics and Safety
 *            of Transmutation Systems"): fission products (Cs-137 30.1 y, Sr-90 28.8 y, short-lived ~1 y, Tc-99 / I-129 long
 *            tail) dominate the first ~300 years; then Pu (Pu-238 87.7 y, Pu-239 24 110 y, Pu-240 6561 y, Pu-242 375 000 y) and
 *            Am-241 (432 y, grown in from Pu-241 14.3 y) take over; the total falls to the ore level after ~150 000 years.
 *            Recycling Pu (0.1 % loss): ~10 000 years (Am-243 7370 y, Am-241 left). Also transmuting the minor actinides:
 *            ~300-500 years, set by the fission products. In ore units at discharge: FP 2e4 (1 y) + 1000 (30 y) + 1e-3;
 *            Pu-238 200, Pu-239 70, Pu-240 100, Pu-242 0.5; Am-241 20 + 300 ingrowth; Am-243 2.5; Cm-244 100 (18.1 y);
 *            Np-237 0.05 (2.14e6 y). Daughter ingrowth beyond Am-241 ignored. */
(function () {
  const { TAU, clamp, lerp, smooth, rng } = WT.util;
  const SHOT = () => document.body.classList.contains("shot");
  const LN2 = Math.LN2, hl = (A, T, t) => A * Math.exp(-LN2 * t / T), LOSS = 0.001;
  function comp(t, rp, tm) {
    const kp = lerp(1, LOSS, rp), km = lerp(1, LOSS, tm);
    const fp = hl(2e4, 1, t) + hl(1000, 30, t) + hl(1e-3, 2.1e5, t);
    const pu = kp * (hl(200, 87.7, t) + hl(70, 24110, t) + hl(100, 6561, t) + hl(0.5, 3.75e5, t));
    const am1 = 20 * Math.exp(-t / 623) + kp * 300 * (Math.exp(-t / 623) - Math.exp(-t / 20.6));
    const ma = km * (am1 + hl(2.5, 7370, t) + hl(100, 18.1, t) + hl(0.05, 2.14e6, t));
    return { fp, pu, ma, tot: fp + pu + ma };
  }
  function crossing(rp, tm) { let lo = 0, hi = 6.3; if (comp(10 ** hi, rp, tm).tot > 1) return null; for (let i = 0; i < 40; i++) { const mid = (lo + hi) / 2; if (comp(10 ** mid, rp, tm).tot > 1) lo = mid; else hi = mid; } return 10 ** hi; }
  const fmtY = (y) => (y >= 1e4 ? `${(Math.round(y / 1e4) * 10).toLocaleString("en")},000` : y >= 1000 ? `${(Math.round(y / 1000)).toLocaleString("en")},000` : `${Math.round(y / 10) * 10}`);
  // the pellet: 400 atoms
  const KINDS = [["uranium", 376, "~94 %"], ["fission products", 19, "~5 %"], ["plutonium", 4, "~1 %"], ["minor actinides", 1, "~0.1 %"]];
  const atoms = []; { const q = rng(8), list = []; KINDS.forEach(([, n], k) => { for (let i = 0; i < n; i++) list.push(k); });
    for (let i = list.length - 1; i > 0; i--) { const j = Math.floor(q() * (i + 1)); [list[i], list[j]] = [list[j], list[i]]; }
    const idx = [0, 0, 0, 0]; list.forEach((k, i) => { const a = i * 2.39996, rr = Math.sqrt((i + 0.5) / list.length); atoms.push({ k, px: rr * Math.cos(a), py: rr * Math.sin(a), j: idx[k]++, ph: q() * TAU }); }); }

  WT.chapter("waste", {
    level: 1, num: "Lesson 1", title: "Spent fuel over time", short: "Spent fuel",
    html: `
<div class="step">
  <h3>What comes out</h3>
  <p>After four or five years in the core, a fuel pellet is still mostly uranium. A few percent is <b>fission products</b>, the split atoms. About 1 % is plutonium, and a trace is heavier <b>minor actinides</b> such as americium.</p>
  <div class="btns"><button class="btn" data-act="sort">Sort the atoms</button></div>
</div>
<div class="step">
  <h3>The first centuries</h3>
  <p>The curve compares the spent fuel's hazard if swallowed with that of the uranium ore it was made from. At first the fission products dominate, but most have half-lives of about 30 years: after some 300 years they have faded below the ore.</p>
  <div class="ctl"><label for="wst-t1">Years after unloading</label><input id="wst-t1" type="range" data-bind="lt" data-instant min="0" max="6" step="0.01" value="1.5"><output data-show="yr" data-fmt="0"></output></div>
</div>
<div class="step">
  <h3>Then plutonium</h3>
  <p>What stays is plutonium and americium, with half-lives of centuries to tens of thousands of years. They keep spent fuel above the ore level for over a hundred thousand years.</p>
  <div class="ctl"><label for="wst-t2">Years after unloading</label><input id="wst-t2" type="range" data-bind="lt" data-instant min="0" max="6" step="0.01" value="4"><output data-show="yr" data-fmt="0"></output></div>
</div>
<div class="step">
  <h3>Recycle and transmute</h3>
  <p>Take the plutonium out and burn it as new fuel, and the time drops to about ten thousand years. Also split the minor actinides in fast reactors, and only the fission products are left: a few hundred years.</p>
  <div class="btns"><button class="btn ghost" data-act="rp" aria-pressed="false">Recycle plutonium</button><button class="btn ghost" data-act="tm" aria-pressed="false">Transmute minor actinides</button></div>
</div>`,
    setup(S) {
      S.set("mode", "mix"); S.set("sort", 0); S.set("lt", 1.5); S.set("rp", 0); S.set("tm", 0); S.set("yr", 30); S.rpOn = 0; S.tmOn = 0;
      const press = () => { document.querySelectorAll('#waste [data-act="rp"]').forEach((b) => b.setAttribute("aria-pressed", String(!!S.rpOn))); document.querySelectorAll('#waste [data-act="tm"]').forEach((b) => b.setAttribute("aria-pressed", String(!!S.tmOn))); };
      S.press = press;
      S.on("sort", () => { S.to("sort", S.target.sort > 0.5 ? 0 : 1); document.querySelectorAll('#waste [data-act="sort"]').forEach((b) => (b.textContent = WT.tr ? WT.tr(S.target.sort > 0.5 ? "Mix them again" : "Sort the atoms") : S.target.sort > 0.5 ? "Mix them again" : "Sort the atoms")); });
      S.on("rp", () => { S.rpOn = S.rpOn ? 0 : 1; S.to("rp", S.rpOn); press(); });
      S.on("tm", () => { S.tmOn = S.tmOn ? 0 : 1; S.to("tm", S.tmOn); press(); });
    },
    steps: [
      (S) => { S.set("mode", "mix"); if (document.body.classList.contains("shot")) S.set("sort", 1); },
      (S) => { S.set("mode", "time"); const n = SHOT(); S.to("lt", 1.5, n); S.to("rp", 0, n); S.to("tm", 0, n); },
      (S) => { S.set("mode", "time"); const n = SHOT(); S.to("lt", 4, n); S.to("rp", 0, n); S.to("tm", 0, n); },
      (S) => { S.set("mode", "time"); const n = SHOT(); S.rpOn = 1; S.tmOn = n ? 1 : 0; S.to("rp", S.rpOn, n); S.to("tm", S.tmOn, n); S.press && S.press(); },
    ],
    frame(g, S, dt) {
      const { W, H, c, ctx } = g, phone = W < 600, fs = phone ? 11 : 13, st = Math.max(0, S.step);
      const COLS = [c.soft, c.warm, c.proton, c.alpha];
      if (S.mode === "mix") {
        const R = Math.min(W * 0.36, H * (phone ? 0.36 : 0.3)), cx = W / 2, cy = H * (phone ? 0.44 : 0.42), so = smooth(0, 1, S.sort);
        WT.grab(g.ctx.canvas, { down(x, y) { if (S.mode !== "mix" || Math.hypot(x - cx, y - cy) > R * 1.2) return false; S.handlers.sort(); return true; },
          hover(x, y) { g.ctx.canvas.style.cursor = S.mode === "mix" && Math.hypot(x - cx, y - cy) < R * 1.2 ? "pointer" : "default"; } });
        g.glow(cx, cy, R * 1.25, c.warm, (0.12 + 0.04 * Math.sin(S.time * 2)) * (1 - so));
        g.ring(cx, cy, R * 1.04, c.soft, 1.2, 0.4 * (1 - so));
        const br = R / Math.sqrt(400) * 0.9;
        // sorted piles: four columns, uranium a big block
        const d = W * (phone ? 0.44 : 0.4) / 20, colX = [W * (phone ? 0.28 : 0.27), W * 0.62, W * 0.77, W * 0.9], baseY = cy + d * 9.5;
        for (const a of atoms) {
          let tx, ty;
          if (a.k === 0) { const i = a.j % 20, j = Math.floor(a.j / 20); tx = colX[0] + (i - 9.5) * d; ty = baseY - j * d; }
          else { const i = a.j % 3, j = Math.floor(a.j / 3); tx = colX[a.k] + (i - (a.k === 3 ? 0 : 1)) * d; ty = baseY - j * d; }
          const x = lerp(cx + a.px * R, tx, so), y = lerp(cy + a.py * R, ty, so), col = COLS[a.k];
          if (a.k === 1) g.glow(x, y, br * 3, c.warm, 0.25 + 0.15 * Math.sin(S.time * 3 + a.ph));
          if (a.k >= 2) g.glow(x, y, br * 3.5, col, 0.3);
          g.ball(x, y, lerp(br * (a.k === 0 ? 0.92 : 1.05), d * 0.46, so), col, a.k === 0 ? 0.6 : 1);
        }
        // a few gamma rays from the fission products while mixed
        if (so < 0.5) for (let i = 0; i < 3; i++) { const u = (S.time * 0.7 + i / 3) % 1, a = i * 2.1 + Math.floor(S.time * 0.7 + i / 3) * 1.3; g.photon(cx + Math.cos(a) * R * (0.4 + 0.9 * u), cy + Math.sin(a) * R * (0.4 + 0.9 * u), a, 22, 1 - u); }
        if (so > 0.6) KINDS.forEach(([name, , pct], k) => {
          const x = colX[k], top = k === 0 ? baseY - 19 * d - 4 : baseY - (Math.ceil(KINDS[k][1] / 3) - 1) * d - 12;
          g.label(pct, x, top - (phone ? 26 : 30), { color: k === 0 ? c.ink : COLS[k], size: fs + 2, weight: 700, alpha: so });
          g.label(phone && k === 1 ? "fission prod." : phone && k === 3 ? "minor act." : name, x, top - (phone ? 10 : 12), { color: c.soft, size: fs - 1, alpha: so });
        });
        else g.label(phone ? "a used fuel pellet, 400 atoms" : "a used fuel pellet, 400 atoms shown", cx, cy + R * 1.04 + 18, { color: c.soft, size: fs, alpha: 1 - so });
        g.label(phone ? "the glow: fission products are the most radioactive" : "the glow: the fission products are by far the most radioactive part", W / 2, H * 0.92, { color: c.ink, size: fs + 1, weight: 600, serif: true });
        return;
      }
      // ---------- time landscape ----------
      const lt = clamp(S.lt, 0, 6), t = 10 ** lt; S.yr = Math.round(t);
      const rp = st === 3 ? S.rp : 0, tm = st === 3 ? S.tm : 0;
      const x0 = W * (phone ? 0.11 : 0.1), x1 = W * 0.95, yT = H * (phone ? 0.36 : 0.36), yB = H * (phone ? 0.77 : 0.8), LO = -2.5, HI = 4.5;
      const X = (l) => lerp(x0, x1, l / 6), Y = (v) => lerp(yB, yT, (Math.log10(Math.max(v, 10 ** (LO - 1))) - LO) / (HI - LO));
      const N = 160, tot = [], fp = [], pu = [], ma = [];
      for (let i = 0; i <= N; i++) { const l = 6 * i / N, cc = comp(10 ** l, rp, tm), x = X(l); tot.push([x, Y(cc.tot)]); fp.push([x, Y(cc.fp)]); pu.push([x, Y(cc.pu)]); ma.push([x, Y(cc.ma)]); }
      g.clip(x0 - 2, yT - 30, x1 - x0 + 4, yB - yT + 30);
      g.ground(tot, c.accent, (yB - yT) * 0.8, 0.3);
      const em = (k) => (st === 1 ? (k === "fp" ? 1 : 0.4) : st === 2 ? (k === "fp" ? 0.4 : 1) : 0.75);
      g.poly(fp, c.warm, 2, em("fp")); g.poly(pu, c.proton, 2, em("pu")); g.poly(ma, c.alpha, 2, em("ma"));
      g.poly(tot, c.ink, 2.6, 0.95);
      g.ctx.restore();
      // ---------- the spent fuel and the ore it came from, lit by what is still radioactive at this time ----------
      const shot = document.body.classList.contains("shot");
      if (st === 3 && !S.drag && S.time > (S.holdT || 0)) S.sweep = ((S.sweep ?? 0) + dt * 0.45) % 6.6;
      const ltO = st === 3 ? (shot ? 2.5 : S.sweep ?? 0) : lt, cc = comp(10 ** Math.min(ltO, 6), rp, tm);
      {
        const oy = H * (phone ? 0.12 : 0.13), pR = Math.min(H * (phone ? 0.1 : 0.095), W * 0.12), px = W * 0.24, rx = W * 0.76;
        const bOf = (v) => clamp((Math.log10(Math.max(v, 1e-4)) + 2) / 6.3, 0, 1), B = [0.06, bOf(cc.fp), bOf(cc.pu), bOf(cc.ma)], COLS2 = [c.soft, c.warm, c.proton, c.alpha];
        g.glow(px, oy, pR * 1.9, c.warm, 0.05 + 0.3 * bOf(cc.tot));
        const br = pR / 20 * 0.95;
        for (const a of atoms) { const x = px + a.px * pR, y = oy + a.py * pR, b = B[a.k];
          if (a.k && b > 0.05) g.glow(x, y, br * (2 + 3 * b), COLS2[a.k], 0.15 + 0.45 * b * (0.8 + 0.2 * Math.sin(S.time * 4 + a.ph)));
          g.ball(x, y, br, COLS2[a.k], a.k ? 0.3 + 0.7 * b : 0.45); }
        // decay sparks, more of them while the fuel is hotter
        if (!S.sparks) S.sparks = [];
        const rate = shot ? 0 : 6 * bOf(cc.tot) ** 2, sp = S.sparks;
        if (Math.random() < rate * dt * 4) { const a = atoms[Math.floor(Math.random() * atoms.length)]; if (a.k) sp.push({ x: px + a.px * pR, y: oy + a.py * pR, t: S.time, a: Math.random() * TAU, col: COLS2[a.k] }); }
        if (Math.random() < 0.6 * dt) sp.push({ x: rx + (Math.random() - 0.5) * pR, y: oy + (Math.random() - 0.5) * pR * 0.7, t: S.time, a: Math.random() * TAU, col: c.fission });
        for (let i = sp.length - 1; i >= 0; i--) { const q = sp[i], u = (S.time - q.t) / 0.5; if (u > 1 || u < 0) { sp.splice(i, 1); continue; } g.glow(q.x, q.y, 6 + 14 * u, "#ffffff", 0.5 * (1 - u)); g.line(q.x, q.y, q.x + Math.cos(q.a) * 26 * u, q.y + Math.sin(q.a) * 26 * u, q.col, 1.6, 1 - u); }
        while (sp.length > 40) sp.shift();
        // the ore: a lumpy rock with a steady faint glow
        g.glow(rx, oy, pR * 1.6, c.fission, 0.18);
        const ctx2 = g.ctx; ctx2.save(); const rg = ctx2.createRadialGradient(rx - pR * 0.3, oy - pR * 0.35, pR * 0.1, rx, oy, pR); rg.addColorStop(0, g.rgba(c.fission, 0.55)); rg.addColorStop(0.6, g.rgba(c.soft, 0.35)); rg.addColorStop(1, g.rgba(c.soft, 0.15)); ctx2.fillStyle = rg;
        ctx2.beginPath(); for (let i = 0; i <= 14; i++) { const a = i / 14 * TAU, rr = pR * (0.78 + 0.14 * Math.sin(a * 3 + 1) + 0.08 * Math.cos(a * 5)); const x = rx + Math.cos(a) * rr * 1.15, y = oy + Math.sin(a) * rr * 0.8; i ? ctx2.lineTo(x, y) : ctx2.moveTo(x, y); } ctx2.closePath(); ctx2.fill(); ctx2.restore();
        for (let i = 0; i < 9; i++) g.ball(rx + Math.cos(i * 2.3) * pR * 0.55 * ((i % 3) / 3 + 0.3), oy + Math.sin(i * 2.3) * pR * 0.35 * ((i % 3) / 3 + 0.4), br * 1.2, c.fission, 0.75);
        g.label(phone ? "spent fuel" : "spent fuel, one tonne", px, oy + pR + (phone ? 10 : 14), { color: c.soft, size: fs - 1 });
        g.label(phone ? "the ore" : "the ore it was made from", rx, oy + pR + (phone ? 10 : 14), { color: c.fission, size: fs - 1 });
        const more = cc.tot >= 1, gc = more ? c.warm : c.fission;
        g.glow(W / 2, oy, pR * 0.9, gc, 0.2);
        g.label(more ? ">" : "<", W / 2, oy - 2, { color: gc, size: phone ? 30 : 40, weight: 700, serif: true });
        g.label(`${Math.round(10 ** Math.min(ltO, 6))} yr`, W / 2, oy + (phone ? 22 : 30), { color: c.ink, size: fs, weight: 600 });
      }
      // drag time along the curve
      const inPlot = (x, y) => x > x0 - 10 && x < x1 + 10 && y > yT - 30 && y < yB + 20;
      WT.grab(g.ctx.canvas, {
        down(x, y) { if (S.mode !== "time" || !inPlot(x, y)) return false; S.drag = true; this.move(x, y); return true; },
        move(x, y) { const l = clamp((x - x0) / (x1 - x0) * 6, 0, 6); if (S.step === 3) { S.sweep = l; S.holdT = S.time + 4; } else { S.set("lt", l); document.querySelectorAll('#waste [data-bind="lt"]').forEach((i) => (i.value = l)); } },
        up() { S.drag = false; }, cancel() { S.drag = false; },
        hover(x, y) { g.ctx.canvas.style.cursor = S.mode === "time" && inPlot(x, y) ? "ew-resize" : "default"; },
      });
      if (st === 3 && ltO <= 6) { const xx = X(ltO), yy = Math.min(Y(cc.tot), yB); g.line(xx, yT, xx, yB, c.ink, 1, 0.25); g.dot(xx, yy, 4.5, c.ink, 0.9); g.glow(xx, yy, 14, c.accent, 0.5); }
      // ore level
      g.line(x0, Y(1), x1, Y(1), c.fission, 1.6, 0.9, [6, 5]);
      g.label(phone ? "uranium ore level" : "the uranium ore it was made from", x1 - 4, Y(1) + 12, { color: c.fission, size: fs - 1, weight: 600, align: "right", bg: true });
      // axes
      ["1 yr", "10", "100", "1000", "10⁴", "10⁵", phone ? "10⁶" : "1 million"].forEach((s, l) => g.label(s, X(l), yB + 12, { color: c.faint, size: fs - 2 }));
      if (!phone) g.label("years after unloading (log scale) →", x1, yB + 28, { color: c.soft, size: fs - 1, align: "right" });
      g.label(phone ? "hazard vs ore (log)" : "hazard if swallowed, relative to the ore (log scale)", x0, yT - 16, { color: c.soft, size: fs - 1, align: "left" });
      [-2, 0, 2, 4].forEach((e) => g.label(e === 0 ? "×1" : e < 0 ? "×0.01" : `×${10 ** e}`, x0 - 5, Y(10 ** e), { color: c.faint, size: fs - 2, align: "right" }));
      // component labels on the right side of their curves, placed where each is visible
      const lab = (pts, s, col, li) => { const i = Math.round(li / 6 * N), p = pts[i]; if (p[1] > yB - 6 || p[1] < yT) return; g.label(s, p[0], p[1] - 11, { color: col, size: fs - 1, weight: 600, bg: true }); };
      lab(fp, phone ? "fission prod." : "fission products", c.warm, phone ? 0.7 : 1.2);
      if (rp < 0.5) lab(pu, "plutonium", c.proton, 3.3);
      if (tm < 0.5) lab(ma, phone ? "Am, Cm, Np" : "americium, curium…", c.alpha, rp > 0.5 ? 3.3 : phone ? 3.1 : 1.9);
      // now marker (steps 2-3) or crossing (step 4)
      const now = comp(t, rp, tm);
      if (st !== 3) {
        g.line(X(lt), yT, X(lt), yB, c.ink, 1, 0.3);
        g.dot(X(lt), Y(now.tot), 5, c.ink); g.glow(X(lt), Y(now.tot), 16, c.accent, 0.5);
        const lead = now.fp >= now.pu && now.fp >= now.ma ? ["fission products", c.warm] : now.pu >= now.ma ? ["plutonium", c.proton] : ["americium", c.alpha];
        const ratio = now.tot, rs = ratio >= 10 ? `${Math.round(ratio)} ×` : ratio >= 1 ? `${ratio.toFixed(1)} ×` : `${ratio.toFixed(ratio < 0.1 ? 3 : 2)} ×`;
        g.label(`${Math.round(t)} years: ${rs} the ore`, W / 2, H * (phone ? 0.87 : 0.9), { color: c.ink, size: fs + 2, weight: 600, serif: true });
        g.label(ratio < 1 ? "below the ore it came from" : `mostly from ${lead[0]}`, W / 2, H * (phone ? 0.87 : 0.9) + fs + 9, { color: ratio < 1 ? c.fission : lead[1], size: fs, weight: 600 });
      } else {
        const tc = crossing(rp, tm);
        if (tc) { const lc = Math.log10(tc), pa = (S.sweep ?? 0) - lc; if (pa > 0 && pa < 0.8) g.ring(X(lc), Y(1), 6 + 60 * pa, c.fission, 2, 1 - pa / 0.8); g.dot(X(lc), Y(1), 6, c.fission); g.glow(X(lc), Y(1), 22, c.fission, 0.55); g.line(X(lc), Y(1), X(lc), yB, c.fission, 1, 0.5, [2, 4]); }
        const what = rp > 0.5 && tm > 0.5 ? (phone ? "recycle + transmute" : "recycle Pu and transmute minor actinides") : rp > 0.5 ? (phone ? "plutonium recycled" : "plutonium recycled, minor actinides in the waste") : tm > 0.5 ? (phone ? "only minor actinides removed" : "minor actinides removed, plutonium left in") : (phone ? "spent fuel as it is" : "spent fuel kept as it is");
        g.label(tc ? `reaches the ore level after ~${fmtY(tc)} years` : "", W / 2, H * (phone ? 0.87 : 0.9), { color: c.ink, size: fs + 2, weight: 600, serif: true });
        g.label(what, W / 2, H * (phone ? 0.87 : 0.9) + fs + 9, { color: c.soft, size: fs });
      }
      g.label("illustrative shape (after OECD-NEA)", W - 6, H - 8, { color: c.faint, size: 10, align: "right" });
    },
  });
})();
