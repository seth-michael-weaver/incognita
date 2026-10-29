/* Keeping it critical: the chain reaction. Scenes (S.mode):
 *   "gen"   = neutron population generation by generation, N_g = N_0 k^g (k = 0.95, 1.00, 1.05); in the core each generation's
 *             neutrons cause fissions (nu = 2.43 for U-235 thermal fission) and are replaced by about k times as many
 *             (stochastic rounding, so k = 1 wanders a little);
 *   "time"  = point kinetics with one delayed group: dn/dt = (rho - beta)/Lambda n + lambda C, dC/dt = beta/Lambda n - lambda C,
 *             rho = (k - 1)/k, beta = 0.0065 (U-235), lambda = 0.0767 /s (mean delay ~13 s), Lambda = 1e-4 s (illustrative
 *             prompt generation time), starting from equilibrium precursors; solved exactly (2x2 matrix exponential).
 *             Without delayed neutrons n = exp(rho t / Lambda). Small reactivities only (well below beta = prompt critical);
 *   "crit"  = a critical experiment: rods set the multiplication; at k = 1 the power stays flat. Rod worth illustrative.
 * Amber specks are the delayed-neutron precursors (fission fragments that emit a neutron seconds after the fission). */
(function () {
  const { TAU, clamp, lerp, smooth, rng } = WT.util;
  const BETA = 0.0065, LAM = 0.0767, LAMBDA = 1e-4, NU = 2.43, N0 = 40, GMAX = 60, TMAX = 60, CRIT_INS = 55, WORTH = 4e-5;
  const log10 = (x) => Math.log(x) / Math.LN10;
  const r = rng(13);
  /** n(t)/n(0) for reactivity rho; delayed on: one-group point kinetics from equilibrium */
  function nOf(rho, t, delayed) {
    if (!delayed) return Math.exp(Math.min(700, rho / LAMBDA * t));
    const a = (rho - BETA) / LAMBDA, b = LAM, c = BETA / LAMBDA, d = -LAM, tr = a + d, det = a * d - b * c, disc = Math.sqrt(tr * tr / 4 - det);
    const w1 = tr / 2 + disc, w2 = tr / 2 - disc, x0 = [1, BETA / (LAM * LAMBDA)];
    // n(t) = e^{w1 t} [(M - w2 I) x0]_0/(w1 - w2) + e^{w2 t} [(w1 I - M) x0]_0/(w1 - w2)
    const p1 = ((a - w2) * x0[0] + b * x0[1]) / (w1 - w2), p2 = ((w1 - a) * x0[0] - b * x0[1]) / (w1 - w2);
    return p1 * Math.exp(Math.min(700, w1 * t)) + p2 * Math.exp(w2 * t);
  }
  /** asymptotic growth rate (1/s) */
  function omega(rho, delayed) { if (!delayed) return rho / LAMBDA; const a = (rho - BETA) / LAMBDA, d = -LAM, tr = a + d, det = a * d - LAM * BETA / LAMBDA; return tr / 2 + Math.sqrt(tr * tr / 4 - det); }
  const fmtT = (s) => (s < 1 ? `${(s * 1000).toFixed(0)} ms` : s < 120 ? `${s.toFixed(s < 10 ? 1 : 0)} s` : `${(s / 60).toFixed(0)} min`);

  // ---------- the core ----------
  const parts = [], fl = [], prec = [];
  const sim = { g: 0, N: N0, hist: [N0], u: 0, k: 1 };
  function resetGen(S) { sim.g = 0; sim.N = N0; sim.hist = [N0]; sim.u = 0; sim.k = S.k; parts.length = 0; spawn(S, N0, null); }
  function rods(core, phone) {
    const nx = phone ? 7 : 10, ny = phone ? 3 : 4, out = [];
    for (let j = 0; j < ny; j++) for (let i = 0; i < nx; i++) out.push([core.x + core.w * (i + 0.5) / nx, core.y + core.h * (j + 0.5) / ny]);
    return { list: out, nx, ny, R: Math.min(core.w / nx, core.h / ny) * 0.2 };
  }
  let lastRods = null;
  function spawn(S, n, sites) {
    const RD = lastRods; if (!RD) return;
    for (let i = 0; i < n && parts.length < 420; i++) {
      const s = sites && sites.length ? sites[Math.floor(r() * sites.length)] : RD.list[Math.floor(r() * RD.list.length)], a = r() * TAU, sp = 30 + 50 * r();
      parts.push({ x: s[0], y: s[1], vx: Math.cos(a) * sp, vy: Math.sin(a) * sp, t0: S.time });
    }
  }

  WT.chapter("critical", {
    num: "Chapter 20", title: "Keeping it critical", short: "Criticality",
    html: `
<div class="step">
  <h3>The multiplication factor</h3>
  <p>Each fission frees a few neutrons; some cause the next fissions, the rest are lost. The <b>multiplication factor</b> <i>k</i> is how many new fissions one fission leads to: each generation multiplies the neutrons by <i>k</i>. Above 1 the chain grows, below 1 it dies away.</p>
  <div class="ctl"><label for="cri-k">Multiplication k</label><input id="cri-k" type="range" data-bind="k" data-instant min="0.95" max="1.05" step="0.05" value="1.05"><output data-show="k" data-fmt="2"></output></div>
</div>
<div class="step">
  <h3>Delayed neutrons</h3>
  <p>A small share of the neutrons (0.65 %) arrive seconds late, from fission fragments that decay first. Those late ones set the pace, so growth slows from a blink to minutes. The plot runs at ×10 speed.</p>
  <div class="ctl"><label for="cri-k2">Multiplication k</label><input id="cri-k2" type="range" data-bind="kd" data-instant min="0.998" max="1.002" step="0.0005" value="1.001"><output data-show="kd" data-fmt="4"></output></div>
  <div class="btns"><button class="btn ghost" data-act="delayed" aria-pressed="true">Delayed neutrons</button></div>
</div>
<div class="step">
  <h3>Criticality</h3>
  <p>A critical experiment: move the control rods until the power stays flat. At that setting <i>k</i> is exactly 1, and that rod position is the measurement. Find it: the readout shows <i>k</i> to five decimals.</p>
  <div class="ctl"><label for="cri-rod">Control rods in (%)</label><input id="cri-rod" type="range" data-bind="ins" data-instant min="35" max="75" step="1" value="45"><output data-show="ins" data-fmt="0"></output></div>
</div>`,
    setup(S) {
      S.set("mode", "gen"); S.set("k", 1.05); S.set("kd", 1.001); S.set("ins", 45); S.set("delayed", 1); S.to("delV", 1, true); S.cur = 0;
      S.on("delayed", () => { S.set("delayed", S.delayed ? 0 : 1); S.to("delV", S.delayed); S.cur = 0; document.querySelectorAll('#critical [data-act="delayed"]').forEach((b) => b.setAttribute("aria-pressed", String(!!S.delayed))); });
    },
    steps: [
      (S) => { S.set("mode", "gen"); resetGen(S); },
      (S) => { S.set("mode", "time"); S.cur = 0; },
      (S) => { S.set("mode", "crit"); S.set("delayed", 1); S.to("delV", 1); S.cur = 0; document.querySelectorAll('#critical [data-act="delayed"]').forEach((b) => b.setAttribute("aria-pressed", "true")); },
    ],
    frame(g, S, dt) {
      const { W, H, c, ctx } = g, phone = W < 600, fs = phone ? 11 : 13, snap = document.body.classList.contains("shot");
      const core = { x: W * 0.05, y: H * 0.07, w: W * 0.9, h: H * (phone ? 0.3 : 0.32) };
      const RD = rods(core, phone); lastRods = RD;
      const mode = S.mode;
      // ---------- state per scene ----------
      let level = 1, rho = 0, kNow = 1;
      if (mode === "gen") {
        if (Math.abs(S.k - sim.k) > 1e-6) resetGen(S);
        if (!parts.length && sim.N > 0) spawn(S, Math.min(sim.N, 400), null);
        const GT = snap ? 0 : 0.55; sim.u += dt;
        if (snap && sim.g < 24) { while (sim.g < 24) { sim.N = Math.max(0, Math.floor(sim.N * S.k + r())); sim.g++; sim.hist.push(sim.N); } parts.length = 0; spawn(S, Math.min(sim.N, 400), null); }
        if (!snap && sim.u >= GT) {
          sim.u = 0; const M = Math.max(0, Math.floor(sim.N * S.k + r()));
          const F = Math.max(M > 0 ? 1 : 0, Math.round(M / NU)), sites = [];
          for (let i = 0; i < Math.min(F, 26); i++) { const s = RD.list[Math.floor(r() * RD.list.length)]; sites.push(s); fl.push({ x: s[0], y: s[1], t: S.time }); }
          parts.length = 0; spawn(S, Math.min(M, 400), sites);
          sim.N = M; sim.g++; sim.hist.push(M);
          if (sim.g >= GMAX || M === 0 || M > 4000) { if (M === 0 || sim.g >= GMAX || M > 4000) setTimeout(() => S.mode === "gen" && resetGen(S), 900); sim.g = Math.min(sim.g, GMAX); }
        }
        level = clamp(sim.N / N0, 0, 30); kNow = S.k;
      } else {
        const k = mode === "crit" ? 1 + WORTH * (CRIT_INS - S.ins) : S.kd; kNow = k; rho = (k - 1) / k;
        if (!snap) S.cur += dt * 10; else S.cur = 30;
        if (S.cur > TMAX + 8) S.cur = 0;
        level = clamp(nOf(rho, Math.min(S.cur, TMAX), S.delayed || mode === "crit"), 0, 1e6);
      }
      // ---------- draw the core ----------
      const glowLv = clamp(log10(Math.max(level, 1e-3)) / 2 + 0.5, 0.05, 1.3);
      ctx.save(); const wg = ctx.createLinearGradient(0, core.y, 0, core.y + core.h); wg.addColorStop(0, g.rgba(c.cool, 0.05)); wg.addColorStop(0.5, g.rgba(c.cool, 0.12)); wg.addColorStop(1, g.rgba(c.cool, 0.05)); ctx.fillStyle = wg;
      if (ctx.roundRect) { ctx.beginPath(); ctx.roundRect(core.x, core.y, core.w, core.h, 16); ctx.fill(); } else ctx.fillRect(core.x, core.y, core.w, core.h); ctx.restore();
      g.clip(core.x, core.y, core.w, core.h); g.glow(core.x + core.w / 2, core.y + core.h / 2, core.w * 0.45, c.cool, 0.1 + 0.25 * clamp(glowLv, 0, 1)); g.ctx.restore();
      for (const [x, y] of RD.list) { g.glow(x, y, RD.R * 3.2, c.warm, 0.12 + 0.4 * clamp(glowLv, 0, 1)); g.ball(x, y, RD.R, c.warm, 0.95); }
      // precursors: amber specks inside the fuel that release a neutron seconds later
      const showPrec = mode !== "gen" ? S.delV : 0;
      if (showPrec > 0.02) {
        while (prec.length < 46) { const k = Math.floor(r() * RD.list.length); prec.push({ k, a: r() * TAU, d: 0.4 + 0.9 * r(), t0: S.time, life: 1.5 + 5 * r() }); }
        for (let i = prec.length - 1; i >= 0; i--) {
          const p = prec[i], s = RD.list[p.k], age = S.time - p.t0; if (!s) { prec.splice(i, 1); continue; }
          const x = s[0] + Math.cos(p.a + age * 0.6) * RD.R * p.d, y = s[1] + Math.sin(p.a + age * 0.6) * RD.R * p.d;
          if (age > p.life) { fl.push({ x, y, t: S.time, late: true }); prec.splice(i, 1); continue; }
          g.dot(x, y, 2.2, c.photon, showPrec * 0.95); g.glow(x, y, 6, c.photon, 0.35 * showPrec);
        }
      }
      // fission flashes
      for (let i = fl.length - 1; i >= 0; i--) { const f = fl[i], a = S.time - f.t; if (a > 0.6) { fl.splice(i, 1); continue; } g.glow(f.x, f.y, (f.late ? 8 : 12) + 34 * a, f.late ? c.photon : "#ffffff", (f.late ? 0.6 : 0.7) * (1 - a / 0.6)); if (f.late && a < 0.5) g.ball(f.x + a * 60, f.y - a * 20, 3, c.neutron, 1 - a / 0.5); }
      while (fl.length > 60) fl.shift();
      // neutrons
      if (mode === "gen") {
        for (const p of parts) {
          p.x += p.vx * dt; p.y += p.vy * dt;
          if (p.x < core.x + 6 || p.x > core.x + core.w - 6) p.vx *= -1; if (p.y < core.y + 6 || p.y > core.y + core.h - 6) p.vy *= -1;
          p.x = clamp(p.x, core.x + 6, core.x + core.w - 6); p.y = clamp(p.y, core.y + 6, core.y + core.h - 6);
          g.ball(p.x, p.y, 3, c.neutron, 0.9);
        }
      } else {
        const n = Math.round(clamp(28 * Math.sqrt(level), 0, 380)), rr = rng(7);
        for (let i = 0; i < n; i++) { const x = core.x + 8 + (core.w - 16) * ((rr() + S.time * (0.05 + 0.1 * rr())) % 1), y = core.y + 8 + (core.h - 16) * ((rr() + 0.5 * Math.sin(S.time * (0.5 + rr()) + i)) * 0.5 + 0.25 + 0.25 * rr()); g.ball(x, clamp(y, core.y + 6, core.y + core.h - 6), 3, c.neutron, 0.85); }
      }
      // control rods
      if (mode === "crit") {
        const ins = S.ins / 100;
        for (let i = 0; i < RD.nx - 1; i++) { const x = core.x + core.w * (i + 1) / RD.nx; ctx.save(); ctx.fillStyle = g.rgba(c.ink, 0.75); ctx.fillRect(x - 3, core.y - 10, 6, 10 + core.h * ins); ctx.restore(); }
        g.label(`rods ${S.ins.toFixed(0)} % in`, core.x + core.w - 8, core.y - 18 < 6 ? core.y + 12 : core.y - 4, { color: c.soft, size: fs - 1, align: "right", bg: true });
      }
      if (mode !== "gen" && S.delV > 0.5) g.label(phone ? "amber: delayed-neutron emitters" : "amber: fission fragments that emit a neutron seconds later", core.x + 10, core.y + core.h + 14, { color: c.photon, size: fs - 1, align: "left" });

      // ---------- population plot ----------
      const px0 = W * (phone ? 0.13 : 0.1), px1 = W * 0.95, py0 = H * (phone ? 0.5 : 0.5), py1 = H * 0.84;
      const LO = mode === "gen" ? -2 : -1, HI = mode === "gen" ? 2 : 3, Y = (v) => lerp(py1, py0, (log10(Math.max(v, 10 ** (LO - 1))) - LO) / (HI - LO));
      g.line(px0, py1, px1, py1, c.line, 1); g.line(px0, py0, px0, py1, c.line, 1);
      for (let e = LO; e <= HI; e++) { g.line(px0, Y(10 ** e), px1, Y(10 ** e), c.line, 1, e === 0 ? 0.9 : 0.4, e === 0 ? null : [2, 5]); g.label(e === 0 ? "×1" : e < 0 ? `×${10 ** e}` : `×${10 ** e}`, px0 - 6, Y(10 ** e), { color: c.faint, size: fs - 2, align: "right" }); }
      g.label("neutrons", px0, py0 - 12, { color: c.soft, size: fs - 1, align: "left" });
      g.clip(px0, py0 - 2, px1 - px0 + 2, py1 - py0 + 4);
      if (mode === "gen") {
        const X = (gg) => px0 + (px1 - px0) * gg / GMAX;
        [[0.95, c.cool], [1, c.soft], [1.05, c.warm]].forEach(([k, col]) => { const pts = []; for (let gg = 0; gg <= GMAX; gg++) pts.push([X(gg), Y(k ** gg)]); g.poly(pts, col, Math.abs(k - S.k) < 1e-6 ? 2.6 : 1.4, Math.abs(k - S.k) < 1e-6 ? 1 : 0.35, Math.abs(k - S.k) < 1e-6 ? null : [4, 4]); });
        sim.hist.forEach((N, gg) => g.dot(X(gg), Y(Math.max(N, 0.02) / N0), phone ? 2.2 : 3, c.ink, 0.85));
        g.ctx.restore();
        [0, 20, 40, 60].forEach((gg) => g.label(phone && gg === 60 ? "60 gen." : String(gg), X(gg), py1 + 12, { color: c.faint, size: fs - 2 }));
        if (!phone) g.label("generations →", px1, py1 + 28, { color: c.soft, size: fs - 1, align: "right" });
        [[0.95, "k = 0.95: dies away", c.cool], [1, "k = 1: steady", c.soft], [1.05, "k = 1.05: grows", c.warm]].forEach(([k, s, col], i) => g.label(s, px1 - 4, Y(k ** GMAX) + (k === 1 ? -11 : k > 1 ? 12 : -12), { color: col, size: fs - 1, align: "right", weight: Math.abs(k - S.k) < 1e-6 ? 600 : 500, bg: true }));
        g.label(phone ? "60 generations: under 0.01 s" : "60 generations last under 0.01 s in a water reactor", W * 0.5, H * 0.93, { color: c.ink, size: fs + 1, weight: 600, serif: true });
      } else {
        const X = (t) => px0 + (px1 - px0) * t / TMAX, del = mode === "crit" ? 1 : S.delayed;
        const curve = (d) => { const pts = []; for (let i = 0; i <= 240; i++) { const t = TMAX * i / 240, v = nOf(rho, t, d); pts.push([X(t), Y(v)]); if (v > 10 ** (HI + 1)) break; } return pts; };
        if (mode === "time") { g.poly(curve(0), c.warm, del ? 1.4 : 2.6, del ? 0.45 : 1, del ? [4, 4] : null); }
        g.poly(curve(1), c.accent, del ? 2.6 : 1.4, del ? 1 : 0.45, del ? null : [4, 4]);
        const tc = Math.min(S.cur, TMAX), vc = nOf(rho, tc, del);
        if (vc < 10 ** (HI + 0.2)) { g.line(X(tc), py0, X(tc), py1, c.ink, 1, 0.25); g.dot(X(tc), Y(vc), 4.5, del ? c.accent : c.warm); }
        g.ctx.restore();
        [0, 20, 40, 60].forEach((t) => g.label(`${t} s`, X(t), py1 + 12, { color: c.faint, size: fs - 2 }));
        if (!phone) g.label("time →", px1, py1 + 28, { color: c.soft, size: fs - 1, align: "right" });
        g.label("×10 speed", px0 + 6, py0 + 10, { color: c.soft, size: fs - 1, align: "left", bg: true });
        const wD = omega(rho, 1), wP = omega(rho, 0), dbl = (w) => Math.log(2) / Math.abs(w);
        const desc = (w) => (Math.abs(w) < 1e-5 ? "flat" : w > 0 ? `doubles every ${fmtT(dbl(w))}` : `halves every ${fmtT(dbl(w))}`);
        if (mode === "time") {
          g.label(`with delayed: ${desc(wD)}`, px1 - 4, py0 + 10, { color: c.accent, size: fs, weight: 600, align: "right", bg: true });
          g.label(`prompt only: ${desc(wP)}`, px1 - 4, py0 + 32, { color: c.warm, size: fs, weight: 600, align: "right", bg: true });
          g.label(phone ? `k = ${kNow.toFixed(4)} · 0.65 % delayed ≈ 13 s` : `k = ${kNow.toFixed(4)} · 0.65 % of neutrons delayed about 13 s (one-group average)`, W * 0.5, H * 0.93, { color: c.ink, size: fs + 1, weight: 600, serif: true });
        } else {
          const crit = Math.abs(S.ins - CRIT_INS) < 0.5;
          g.label(crit ? "critical: k = 1.00000, power flat" : `k = ${kNow.toFixed(5)} · ${desc(wD)}`, W * 0.5, H * 0.93, { color: crit ? c.fission : c.ink, size: fs + 2, weight: 600, serif: true });
          if (crit) g.glow(W * 0.5, H * 0.93, 90, c.fission, 0.18);
        }
      }
      g.label("illustration", W - 6, H - 10, { color: c.faint, size: 10, align: "right" });
    },
  });
})();
