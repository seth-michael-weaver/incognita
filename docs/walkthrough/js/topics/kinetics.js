/* Reactor kinetics: six groups and the inhour equation. Scenes (S.mode):
 *   "groups" = the six delayed-neutron precursor groups of U-235 thermal fission (Keepin): half-lives 55.72, 22.72, 6.22,
 *              2.30, 0.610, 0.230 s; relative yields a_i = beta_i/beta = 0.033, 0.219, 0.196, 0.395, 0.115, 0.042; beta = 0.0065.
 *              At equilibrium group i emits in proportion to a_i and holds an inventory in proportion to a_i/lambda_i
 *              (mean delay sum a_i/lambda_i = 13.0 s). "Stop fissions" lets each group decay as exp(-lambda_i t), in real time.
 *   "inhour" = rho(omega) = omega Lambda + sum beta_i omega/(omega + lambda_i), Lambda = 2e-5 s (prompt neutron generation
 *              time, typical light-water-reactor value). The seven roots for a given rho are found by bisection between the
 *              poles -lambda_i (rho is increasing on each branch); the largest sets the stable period T = 1/omega_1.
 *   "jump"   = exact point-kinetics response to a step rho from equilibrium:
 *              n(t)/n0 = sum_j A_j exp(omega_j t), A_j = [Lambda + sum beta_i/(omega_j + lambda_i)] / rho'(omega_j)
 *              (residues of the Laplace solution N(s) = n0 [Lambda + sum beta_i/(s + lambda_i)] / (rho(s) - rho)).
 *              Prompt jump P1/P0 ~ beta/(beta - rho); prompt critical at rho = beta = 1 $.
 *   "scram"  = the same for large negative steps: prompt drop to ~ beta/(beta - rho), then a period that tends to
 *              -1/lambda_1 = -80.4 s (the 55.7 s group). Feedback, rod motion time and source neutrons are ignored.
 * Source: G. R. Keepin, Physics of Nuclear Kinetics (1965), six-group data for U-235 thermal fission. */
(function () {
  const { TAU, clamp, lerp, smooth, rng } = WT.util;
  const TH = [55.72, 22.72, 6.22, 2.30, 0.610, 0.230], AI = [0.033, 0.219, 0.196, 0.395, 0.115, 0.042], BETA = 0.0065, LAMBDA = 2e-5;
  const LI = TH.map((t) => Math.LN2 / t), BI = AI.map((a) => a * BETA);
  const INV = AI.map((a, i) => a / LI[i]), INVS = INV.reduce((s, v) => s + v, 0); // inventory share, mean delay = INVS (s)
  const log10 = (x) => Math.log(x) / Math.LN10;
  const r = rng(23);
  const rhoOf = (w) => { let s = w * LAMBDA; for (let i = 0; i < 6; i++) s += BI[i] * w / (w + LI[i]); return s; };
  const drho = (w) => { let s = LAMBDA; for (let i = 0; i < 6; i++) s += BI[i] * LI[i] / (w + LI[i]) ** 2; return s; };
  const POLES = LI.map((l) => -l).sort((a, b) => a - b); // -3.01 ... -0.0124
  const cache = new Map();
  /** the seven roots (ascending) and amplitudes for a step of rho (absolute) */
  function roots(rho) {
    const key = rho.toFixed(7); if (cache.has(key)) return cache.get(key);
    if (Math.abs(rho) < 1e-10) rho = 1e-10;
    const ed = [-1e7, ...POLES, 1e6], out = [];
    for (let k = 0; k < 7; k++) {
      let lo = ed[k] + (k ? 1e-12 : 0), hi = ed[k + 1] - (k < 6 ? 1e-12 : 0);
      for (let it = 0; it < 200; it++) { const m = (lo + hi) / 2; if (rhoOf(m) < rho) lo = m; else hi = m; }
      const w = (lo + hi) / 2; let num = LAMBDA; for (let i = 0; i < 6; i++) num += BI[i] / (w + LI[i]);
      out.push({ w, A: num / drho(w) });
    }
    const res = { rho, list: out, w1: out[6].w }; cache.set(key, res); if (cache.size > 400) cache.delete(cache.keys().next().value); return res;
  }
  const nOf = (R, t) => { let s = 0; for (const { w, A } of R.list) s += A * Math.exp(Math.min(60, w * t)); return s; };
  const fmtT = (s) => { const a = Math.abs(s); return a < 1 ? `${(1000 * a).toFixed(a < 0.01 ? 1 : 0)} ms` : a < 100 ? `${a.toFixed(a < 10 ? 1 : 0)} s` : a < 7200 ? `${(a / 60).toFixed(0)} min` : `${(a / 3600).toFixed(0)} h`; };

  // ---------- precursor lanes ----------
  const lanes = AI.map((a, i) => ({ C: 1, sp: [], pops: [], acc: 0 }));
  { const q = rng(5); lanes.forEach((L, i) => { const n = Math.max(1, Math.round(70 * INV[i] / INVS)); for (let k = 0; k < n; k++) L.sp.push([q(), q(), q() * TAU]); }); }
  /** the core: rows of lit fuel pins, neutrons ~ power, control rods (ins 0..1); flashT = time of a flash ring */
  const glowCore = (g, S, box, lv, ins = 0.45, grab = false, flashA = -1, flashCol) => {
    const { c, ctx } = g, f = clamp(lv, 0, 1.3), phone = g.W < 600, n = phone ? 8 : 12, rows = 3, R = Math.min(box.w / n, box.h / rows) * 0.2;
    const br = 1 + 0.06 * Math.sin(S.time * 2.3) * f;
    ctx.save(); const wg = ctx.createLinearGradient(0, box.y, 0, box.y + box.h); wg.addColorStop(0, g.rgba(c.cool, 0.05)); wg.addColorStop(0.5, g.rgba(c.cool, 0.1 + 0.22 * f)); wg.addColorStop(1, g.rgba(c.cool, 0.05)); ctx.fillStyle = wg;
    ctx.beginPath(); if (ctx.roundRect) ctx.roundRect(box.x, box.y, box.w, box.h, 14); else ctx.rect(box.x, box.y, box.w, box.h); ctx.fill(); ctx.restore();
    g.clip(box.x, box.y, box.w, box.h);
    g.glow(box.x + box.w / 2, box.y + box.h / 2, box.w * 0.55, f > 1.05 ? c.proton : c.warm, 0.08 + 0.25 * clamp(f, 0, 1.3) * br);
    for (let j = 0; j < rows; j++) for (let i = 0; i < n; i++) { const x = box.x + box.w * (i + 0.5) / n, y = box.y + box.h * (j + 0.5) / rows; g.glow(x, y, R * 3.4 * br, c.warm, 0.05 + 0.42 * clamp(f, 0, 1.2)); g.ball(x, y, R, c.warm, 0.95); }
    const k = Math.round(70 * clamp(f, 0, 1.2)); for (let i = 0; i < k; i++) { const u = (i * 0.618 + S.time * (0.12 + 0.06 * (i % 5))) % 1, v = 0.5 + 0.44 * Math.sin(i * 2.1 + S.time * (0.9 + 0.3 * (i % 3))); g.ball(box.x + 6 + (box.w - 12) * u, box.y + box.h * v, 2.6, c.neutron, 0.85); }
    ctx.restore();
    // control rods between the pin columns, with a lit tip as the drag handle
    for (let i = 1; i < n; i += 2) { const x = box.x + box.w * i / n, len = 8 + (box.h - 8) * clamp(ins, 0, 1); ctx.save(); ctx.fillStyle = g.rgba(c.soft, 0.6); ctx.fillRect(x - 3, box.y - 8, 6, len); ctx.restore();
      if (grab) { g.glow(x, box.y - 8 + len, 10 + 2 * Math.sin(S.time * 3), c.accent, 0.55); g.dot(x, box.y - 8 + len, 3.5, c.accent); } }
    if (flashA >= 0 && flashA < 1) { const cx = box.x + box.w / 2, cy = box.y + box.h / 2; g.glow(cx, cy, box.w * (0.2 + 0.5 * flashA), flashCol || "#ffffff", 0.6 * (1 - flashA)); g.ring(cx, cy, 20 + box.w * 0.6 * flashA, flashCol || c.ink, 3 * (1 - flashA), 0.8 * (1 - flashA)); }
  };
  const LAY = { used: false, drag: null };
  const syncIn = (id, v) => { const el = document.getElementById(id); if (el) el.value = v; };
  const inB = (b, x, y, p = 0) => b && x >= b.x - p && x <= b.x + b.w + p && y >= b.y - p && y <= b.y + b.h + p;
  // rods: jump scene ins 0.7 (0.05 $) .. 0.15 (1.3 $); scram scene ins 0.3 (-0.5 $) .. 1 (-30 $)
  const insJ = (r) => 0.7 - 0.55 * (r - 0.05) / 1.25, rJ = (ins) => clamp(0.05 + (0.7 - ins) / 0.55 * 1.25, 0.05, 1.3);
  const insS = (r) => 0.3 + 0.7 * (-r - 0.5) / 29.5, rS = (ins) => clamp(-(0.5 + (ins - 0.3) / 0.7 * 29.5), -30, -0.5);
  const GRAB = {
    down(x, y) { const S = LAY.S, m = LAY.mode; if (!S) return false;
      if (m === "inhour" && inB(LAY.bx, x, y, 10)) { LAY.drag = "rho"; }
      else if ((m === "jump" || m === "scram") && inB(LAY.core, x, y, 14)) { LAY.drag = "rod"; }
      else return false; LAY.used = true; GRAB.move(x, y); return true; },
    move(x, y) { const S = LAY.S, m = LAY.mode; if (!S || !LAY.drag) return;
      if (LAY.drag === "rho") { const v = Math.round(clamp(LAY.yR(y), -2, 1.3) * 100) / 100; S.set("rd", v); syncIn("ki-r1", v); }
      else { const ins = clamp((y - LAY.core.y) / LAY.core.h, 0, 1);
        if (m === "jump") { const v = Math.round(rJ(ins) * 100) / 100; if (v !== S.rj) { S.set("rj", v); syncIn("ki-r2", v); } }
        else { const v = Math.round(rS(ins) * 2) / 2; if (v !== S.rs) { S.set("rs", v); syncIn("ki-r3", v); } } } },
    up() { const S = LAY.S; if (LAY.drag === "rod" && S) { S.cur = 0; S.flashT = S.time; } LAY.drag = null; }, cancel() { LAY.drag = null; },
    hover(x, y, e) { const m = LAY.mode; e.target.style.cursor = (m === "inhour" && inB(LAY.bx, x, y, 10)) || ((m === "jump" || m === "scram") && inB(LAY.core, x, y, 14)) ? "grab" : ""; },
  };
  // a log-power landscape over time
  function powerPlot(g, box, R, T, lo, hi, tcur, fs, col) {
    const { c } = g, X = (t) => box.x + box.w * t / T, Y = (v) => lerp(box.y + box.h, box.y, (log10(Math.max(v, 10 ** (lo - 1))) - lo) / (hi - lo));
    g.line(box.x, box.y + box.h, box.x + box.w, box.y + box.h, c.line, 1);
    for (let e = lo; e <= hi; e++) { g.line(box.x, Y(10 ** e), box.x + box.w, Y(10 ** e), c.line, 1, e === 0 ? 0.9 : 0.35, e === 0 ? null : [2, 5]); g.label(e === 0 ? "×1" : `10${e < 0 ? "⁻" : ""}${"⁰¹²³⁴⁵⁶⁷⁸⁹"[Math.abs(e)]}`, box.x - 6, Y(10 ** e), { color: c.faint, size: fs - 2, align: "right" }); }
    const pts = [[X(0), Y(1)]]; let t = 0;
    // fine steps early (the prompt jump takes milliseconds), coarser later
    for (let i = 1; i <= 400; i++) { t = T * (i / 400) ** 1.6; const v = nOf(R, Math.max(t, 1e-4)); pts.push([X(t), Y(v)]); if (v > 10 ** (hi + 0.5) || v < 10 ** (lo - 0.5)) break; }
    g.clip(box.x, box.y - 2, box.w + 2, box.h + 4); g.ground(pts, col, box.h, 0.32); g.poly(pts, col, 2.6); g.ctx.restore();
    const tc = Math.min(tcur, T), vc = nOf(R, Math.max(tc, 1e-4));
    if (vc < 10 ** (hi + 0.1) && vc > 10 ** (lo - 0.1)) { g.line(X(tc), box.y, X(tc), box.y + box.h, c.ink, 1, 0.25); g.dot(X(tc), Y(vc), 4.5, col); g.glow(X(tc), Y(vc), 16, col, 0.4); }
    return { X, Y, vc };
  }
  const W0 = 0.005, WMAX = 400, wx = (w) => Math.asinh(w / W0) / Math.asinh(WMAX / W0);
  const actBtn = (on) => document.querySelectorAll('#kinetics [data-act="kistop"]').forEach((b) => { b.setAttribute("aria-pressed", String(!!on)); });

  WT.chapter("kinetics", {
    level: 3, num: "Lesson 1", title: "Reactor kinetics: six groups and the inhour equation", short: "Kinetics",
    html: `
<div class="step">
  <h3>Six groups of late neutrons</h3>
  <p>Delayed neutrons come from about six groups of fission products, with half-lives from 0.23 s to 56 s (Keepin, U-235). The 2-s and 22-s groups emit most of them, while the long-lived groups hold most of the waiting stock: mean delay Σ <i>a</i><sub>i</sub>/<i>λ</i><sub>i</sub> ≈ 13 s. Stop the fissions and watch each group run down at its own pace.</p>
  <div class="btns"><button class="btn" data-act="kistop" aria-pressed="false">Stop fissions</button></div>
</div>
<div class="step">
  <h3>The inhour equation</h3>
  <p>Try <i>n</i> ∝ e<sup><i>ωt</i></sup> in the six-group point kinetics and you get <i>ρ</i> = <i>ω</i>Λ + Σ <i>β</i><sub>i</sub><i>ω</i>/(<i>ω</i> + <i>λ</i><sub>i</sub>): seven branches split by the poles at −<i>λ</i><sub>i</sub>. A step in <i>ρ</i> meets each branch once; the rightmost root is the stable period <i>T</i> = 1/<i>ω</i><sub>1</sub>, the other six die away.</p>
  <div class="ctl"><label for="ki-r1">Reactivity ρ ($)</label><input id="ki-r1" type="range" data-bind="rd" data-instant min="-2" max="1.3" step="0.01" value="0.3"><output data-show="rd" data-fmt="2"></output></div>
</div>
<div class="step">
  <h3>Prompt jump and prompt critical</h3>
  <p>A step of reactivity first lifts the power within milliseconds by <i>P</i><sub>1</sub>/<i>P</i><sub>0</sub> ≈ <i>β</i>/(<i>β</i> − <i>ρ</i>), then it rises on the stable period. At <i>ρ</i> = 1 $ the prompt neutrons alone are critical and the period collapses toward Λ/(<i>ρ</i> − <i>β</i>).</p>
  <div class="ctl"><label for="ki-r2">Reactivity ρ ($)</label><input id="ki-r2" type="range" data-bind="rj" data-instant min="0.05" max="1.3" step="0.01" value="0.5"><output data-show="rj" data-fmt="2"></output></div>
</div>
<div class="step">
  <h3>After a scram</h3>
  <p>Insert large negative reactivity: the power drops promptly to about <i>β</i>/(<i>β</i> − <i>ρ</i>), and then can fall no faster than the longest-lived group decays. However deep the scram, the period tends to −1/<i>λ</i><sub>1</sub> ≈ −80 s.</p>
  <div class="ctl"><label for="ki-r3">Reactivity ρ ($)</label><input id="ki-r3" type="range" data-bind="rs" data-instant min="-30" max="-0.5" step="0.5" value="-10"><output data-show="rs" data-fmt="1"></output></div>
</div>`,
    setup(S) {
      S.set("mode", "groups"); S.set("rd", 0.3); S.set("rj", 0.5); S.set("rs", -10); S.stopped = false; S.tStop = 0; S.cur = 0;
      S.on("kistop", () => { S.stopped = !S.stopped; S.tStop = S.time; if (!S.stopped) lanes.forEach((L) => (L.C = 1)); actBtn(S.stopped); document.querySelectorAll('#kinetics [data-act="kistop"]').forEach((b) => (b.textContent = WT.tr ? WT.tr(S.stopped ? "Restart fissions" : "Stop fissions") : S.stopped ? "Restart fissions" : "Stop fissions")); });
    },
    steps: [
      (S) => { S.set("mode", "groups"); },
      (S) => { S.set("mode", "inhour"); S.cur = 0; },
      (S) => { S.set("mode", "jump"); S.cur = 0; },
      (S) => { S.set("mode", "scram"); S.cur = 0; },
    ],
    frame(g, S, dt) {
      if (g.W < 40 || g.H < 40) return;
      LAY.mode = S.mode;
      const { W, H, c, ctx } = g, phone = W < 600, fs = phone ? 11 : 13, snap = document.body.classList.contains("shot"), mode = S.mode;
      const rd = { color: c.ink, size: fs + 1, weight: 600, serif: true }, yRd = H * 0.93;
      if (mode === "groups") {
        const y0 = H * 0.1, y1 = H * 0.8, lh = (y1 - y0) / 6, lx = W * (phone ? 0.05 : 0.05), bx0 = W * (phone ? 0.3 : 0.26), bx1 = W * (phone ? 0.66 : 0.66), ex = W * 0.95;
        const ts = S.time - S.tStop;
        g.label("half-life · share emitted", lx, y0 - 16, { color: c.soft, size: fs - 1, align: "left" });
        g.label("waiting stock", (bx0 + bx1) / 2, y0 - 16, { color: c.photon, size: fs - 1 });
        if (!phone) g.label("delayed neutrons out", (bx1 + ex) / 2 + 10, y0 - 16, { color: c.neutron, size: fs - 1 });
        let tot = 0;
        lanes.forEach((L, i) => {
          const yc = y0 + lh * (i + 0.5), C = S.stopped ? Math.exp(-LI[i] * ts) : 1; L.C = C; tot += AI[i] * C;
          g.label(`${TH[i] < 1 ? TH[i].toFixed(2) : TH[i].toFixed(1)} s`, lx, yc - (phone ? 7 : 8), { color: c.ink, size: fs, weight: 600, align: "left" });
          g.label(`${(100 * AI[i]).toFixed(1)} %`, lx, yc + (phone ? 8 : 10), { color: c.soft, size: fs - 1, align: "left" });
          // stock: amber precursors, number ~ inventory share
          ctx.save(); ctx.fillStyle = g.rgba(c.photon, 0.06); ctx.beginPath(); if (ctx.roundRect) ctx.roundRect(bx0, yc - lh * 0.36, bx1 - bx0, lh * 0.72, 8); else ctx.rect(bx0, yc - lh * 0.36, bx1 - bx0, lh * 0.72); ctx.fill(); ctx.restore();
          L.sp.forEach(([u, v, ph], k) => { if (k / L.sp.length >= C + 1e-9 && !(k === 0 && C > 0.02)) return; const x = bx0 + 8 + (bx1 - bx0 - 16) * u * 0.82 + 2 * Math.sin(S.time * 2 + ph), y = yc + lh * 0.28 * (2 * v - 1); g.dot(x, y, phone ? 2.2 : 2.8, c.photon, 0.95); g.glow(x, y, 6, c.photon, 0.3); });
          g.label(`${(100 * INV[i] / INVS * C).toFixed(INV[i] / INVS * C < 0.01 ? 1 : 0)} %`, bx1 - 6, yc - lh * 0.36 + 9, { color: c.photon, size: fs - 2, align: "right" });
          // emissions: rate ~ a_i C (scaled to ~22 per second in total)
          L.acc += (snap ? 0 : dt) * 22 * AI[i] * C;
          while (L.acc > 1) { L.acc -= 1; L.pops.push({ t: S.time, y: yc + lh * 0.25 * (2 * r() - 1) }); }
          if (snap && !L.pops.length) for (let k = 0; k < Math.round(6 * AI[i] / 0.395 * C); k++) L.pops.push({ t: S.time - 0.9 * r(), y: yc + lh * 0.25 * (2 * r() - 1) });
          for (let k = L.pops.length - 1; k >= 0; k--) { const p = L.pops[k], a = S.time - p.t; if (a > 1) { L.pops.splice(k, 1); continue; } const x = lerp(bx1, ex, a); if (a < 0.15) g.glow(bx1, p.y, 10 + 30 * a, c.photon, 0.6 * (1 - a / 0.15)); g.ball(x, p.y, 3, c.neutron, 1 - a * 0.7); }
        });
        g.label(S.stopped ? `${ts.toFixed(0)} s after stopping · delayed emission ${(100 * tot).toFixed(tot < 0.1 ? 1 : 0)} % of the start` : `mean delay Σ aᵢ/λᵢ = ${INVS.toFixed(1)} s · β = 0.0065 (U-235)`, W / 2, yRd, rd);
        g.label("Keepin six-group data", W - 6, H - 10, { color: c.faint, size: 10, align: "right" });
        return;
      }
      const core = { x: W * 0.05, y: H * 0.05, w: W * 0.9, h: H * (phone ? 0.21 : 0.24) };
      LAY.S = S; LAY.mode = mode; LAY.core = core; if (!g.ctx.canvas._kig) { g.ctx.canvas._kig = 1; WT.grab(g.ctx.canvas, GRAB); }
      if (S.lastRho !== mode + (mode === "jump" ? S.rj : S.rs)) { if (S.lastRho !== undefined && mode !== "inhour" && !LAY.drag) { S.cur = 0; S.flashT = S.time; } S.lastRho = mode + (mode === "jump" ? S.rj : S.rs); }
      const flashA = S.flashT != null ? (S.time - S.flashT) / 0.9 : -1;
      if (mode === "inhour") {
        const rho = S.rd * BETA, R = roots(rho), w1 = R.w1;
        // core pulse: brightness grows/decays on the stable period, loop every few seconds
        if (!snap) S.cur += dt; const lv = clamp(0.55 + 0.25 * Math.sign(w1) * Math.min(1, Math.abs(w1) * (S.cur % 4)), 0, 1.2); glowCore(g, S, core, lv);
        const bx = { x: W * (phone ? 0.12 : 0.1), y: H * 0.36, w: W * (phone ? 0.84 : 0.86), h: H * 0.44 }, LO = -3, HI = 2;
        LAY.bx = bx; LAY.yR = (y) => LO + (HI - LO) * (bx.y + bx.h - y) / bx.h;
        const X = (w) => bx.x + bx.w * (0.5 + 0.5 * wx(w)), Y = (p) => lerp(bx.y + bx.h, bx.y, (p - LO) / (HI - LO));
        g.line(bx.x, Y(0), bx.x + bx.w, Y(0), c.line, 1); g.line(X(0), bx.y, X(0), bx.y + bx.h, c.line, 1);
        [-2, -1, 1].forEach((v) => g.label(`${v} $`, bx.x - 4, Y(v), { color: c.faint, size: fs - 2, align: "right" })); g.label("0", bx.x - 4, Y(0), { color: c.faint, size: fs - 2, align: "right" });
        g.line(bx.x, Y(1), bx.x + bx.w, Y(1), c.proton, 1, 0.5, [2, 5]); if (!phone) g.label("prompt critical", bx.x + 4, Y(1) - 9, { color: c.proton, size: fs - 2, align: "left" });
        // poles
        POLES.forEach((p, i) => { g.line(X(p), bx.y, X(p), bx.y + bx.h, c.soft, 1, 0.3, [3, 5]); if (!phone || i === 0 || i === 2 || i === 5) g.label(`−λ${6 - i}`, X(p), bx.y + bx.h + 12, { color: c.faint, size: fs - 2 }); });
        // branches
        const ed = [-WMAX, ...POLES, WMAX];
        g.clip(bx.x, bx.y, bx.w, bx.h);
        for (let k = 0; k < 7; k++) {
          const a = wx(ed[k]), b = wx(ed[k + 1]), pts = [];
          for (let i = 1; i < 160; i++) { const s = lerp(a, b, i / 160), w = W0 * Math.sinh(s * Math.asinh(WMAX / W0)), p = rhoOf(w) / BETA; if (p < LO - 1 || p > HI + 1) { if (pts.length > 1) { g.poly(pts, c.accent, 2, k === 6 ? 1 : 0.75); } pts.length = 0; continue; } pts.push([X(w), Y(p)]); }
          if (k === 6) g.ground(pts, c.accent, bx.h * 0.6, 0.18);
          g.poly(pts, c.accent, k === 6 ? 2.6 : 2, k === 6 ? 1 : 0.75);
        }
        g.ctx.restore();
        g.line(bx.x, Y(S.rd), bx.x + bx.w, Y(S.rd), c.warm, LAY.drag ? 2.4 : 1.6, 0.9);
        { const hx = bx.x + bx.w - 8, hy = Y(S.rd); g.glow(hx, hy, 14 + 2 * Math.sin(S.time * 3), c.warm, 0.5); g.dot(hx, hy, 5, c.warm); g.line(hx, hy - 7, hx, hy + 7, c.paper, 1.5, 0.9); if (!LAY.used) g.label("drag ρ", hx, hy + 16, { color: c.warm, size: fs - 2, weight: 600, align: "right", bg: true }); }
        g.label(`ρ = ${S.rd.toFixed(2)} $`, bx.x + bx.w - 24, Y(S.rd) + (S.rd > 1.5 ? 12 : -11), { color: c.warm, size: fs - 1, weight: 600, align: "right", bg: true });
        R.list.forEach((q, j) => { if (Math.abs(q.w) > WMAX) return; const x = X(q.w), y = Y(S.rd); if (j === 6) { g.glow(x, y, 22, c.fission, 0.55); g.dot(x, y, 6, c.fission); } else g.dot(x, y, 4, c.warm); });
        if (R.list[0].w > -WMAX) g.label(phone ? "prompt root" : "prompt root ≈ −(β−ρ)/Λ", X(R.list[0].w) + 6, Y(S.rd) + 14, { color: c.soft, size: fs - 2, align: "left" });
        g.label(phone ? "ω (1/s), stretched" : "ω (1/s), axis stretched (asinh)", bx.x + bx.w, bx.y + bx.h + 28, { color: c.faint, size: fs - 2, align: "right" });
        const T1 = 1 / w1;
        g.label(Math.abs(w1) < 1e-6 ? "ρ = 0: power stays flat" : `stable period T = 1/ω₁ = ${T1 > 0 ? "" : "−"}${fmtT(T1)}`, W / 2, yRd, { ...rd, color: S.rd >= 1 ? c.proton : c.ink });
      } else if (mode === "jump") {
        const rho = S.rj * BETA, R = roots(rho), T = 20; S.cur = snap ? 6 : (S.cur + dt) % (T + 3);
        const bx = { x: W * (phone ? 0.13 : 0.1), y: H * 0.38, w: W * (phone ? 0.83 : 0.86), h: H * 0.42 };
        const P = powerPlot(g, bx, R, T, -0, 4, S.cur, fs, S.rj >= 1 ? c.proton : c.accent);
        glowCore(g, S, core, clamp(log10(P.vc) / 3 + 0.3, 0, 1.3), insJ(S.rj), true, S.rj >= 1 ? flashA : -1, c.proton);
        if (!LAY.used) g.label("drag the rods out", core.x + core.w / 2, core.y + core.h + 12, { color: c.accent, size: fs - 1, weight: 600, bg: true });
        if (S.rj < 0.98) { const pj = BETA / (BETA - rho); g.line(bx.x, P.Y(pj), bx.x + bx.w, P.Y(pj), c.warm, 1.2, 0.8, [4, 4]); g.label(`prompt jump β/(β−ρ) = ${pj.toFixed(2)}`, bx.x + 10, P.Y(pj) - 11, { color: c.warm, size: fs - 1, weight: 600, align: "left", bg: true }); }
        [0, 5, 10, 15, 20].forEach((t) => g.label(`${t} s`, P.X(t), bx.y + bx.h + 12, { color: c.faint, size: fs - 2 }));
        g.label("power", bx.x, bx.y - 12, { color: c.soft, size: fs - 1, align: "left" });
        const T1 = 1 / R.w1;
        g.label(S.rj >= 1 ? `prompt critical · period ${fmtT(T1)} (Λ = 20 µs)` : `ρ = ${S.rj.toFixed(2)} $ · stable period ${fmtT(T1)}`, W / 2, yRd, { ...rd, color: S.rj >= 1 ? c.proton : c.ink });
      } else {
        const rho = S.rs * BETA, R = roots(rho), T = 300; S.cur = snap ? 150 : (S.cur + dt * 10) % (T + 30);
        const bx = { x: W * (phone ? 0.13 : 0.1), y: H * 0.38, w: W * (phone ? 0.83 : 0.86), h: H * 0.42 };
        const P = powerPlot(g, bx, R, T, -5, 0, S.cur, fs, c.cool);
        glowCore(g, S, core, clamp(1 + log10(P.vc) / 4, 0.02, 1), insS(S.rs), true, flashA, c.cool);
        if (!LAY.used) g.label("drag the rods in", core.x + core.w / 2, core.y + core.h + 12, { color: c.accent, size: fs - 1, weight: 600, bg: true });
        // the -80 s asymptote through the late curve
        const t2 = 200, v2 = nOf(R, t2), ref = []; for (let i = 0; i <= 40; i++) { const t = 40 + 260 * i / 40; ref.push([P.X(t), P.Y(v2 * Math.exp(-(t - t2) * LI[0]))]); }
        g.poly(ref, c.warm, 1.4, 0.9, [5, 4]);
        const pj = BETA / (BETA - rho); g.label(`prompt drop to ${pj < 0.1 ? pj.toFixed(3) : pj.toFixed(2)}`, P.X(4) + 4, P.Y(pj) - 12, { color: c.cool, size: fs - 1, weight: 600, align: "left", bg: true });
        g.label(phone ? "slope e^(−t/80 s)" : "slope e^(−t / 80 s): the 55.7 s group", P.X(150), P.Y(v2 * Math.exp((t2 - 150) * LI[0])) - 14, { color: c.warm, size: fs - 1, align: "left", bg: true });
        [0, 100, 200, 300].forEach((t) => g.label(`${t} s`, P.X(t), bx.y + bx.h + 12, { color: c.faint, size: fs - 2 }));
        g.label("power ×10 speed", bx.x, bx.y - 12, { color: c.soft, size: fs - 1, align: "left" });
        g.label(`ρ = ${S.rs.toFixed(1)} $ · stable period −${fmtT(-1 / R.w1)} (limit −${fmtT(1 / LI[0])})`, W / 2, yRd, rd);
      }
      g.label("Keepin six-group data", W - 6, H - 10, { color: c.faint, size: 10, align: "right" });
    },
  });
})();
