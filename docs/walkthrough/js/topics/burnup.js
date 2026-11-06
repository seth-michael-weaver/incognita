/* Fuel burnup. Scenes (S.mode):
 *   "rod"  = 1000 heavy-metal atoms of a 4.5 %-enriched UO2 pellet (each dot = one atom in a thousand) and their fate over
 *            days at full power; composition bars. Steps 1-3 share the slider (days at power, 0-1400).
 *   "pu"   = the same with fission flashes coloured by nuclide and the share of fissions (and of energy so far) in plutonium.
 *   "k"    = k-infinity against burnup, drawn as a landscape, with the fission-product share of absorptions.
 *   "core" = a three-batch core: each cycle a third of the assemblies is replaced; soluble boron holds k_eff = 1 and is
 *            diluted as the fuel burns (sawtooth). Time in months at full power.
 * Depletion model (ILLUSTRATIVE, one energy group, constant cross sections, constant power): nuclides U-235, U-236,
 * U-238, Np-239 (T1/2 2.356 d), Pu-239, Pu-240, Pu-241, Pu-242 and lumped fission-product pairs, integrated in 0.5-day
 * steps at a specific power of 38 MW per tonne of heavy metal (a typical PWR value), 200 MeV per fission
 * (3.204e-11 J), 2.53e27 heavy-metal atoms per tonne, so burnup (GWd/tHM) = 0.038 x days. One-group cross sections
 * (barns, illustrative but with LWR-like ratios): U-235 sf 48 sc 10; U-238 sf 0.12 sc 1.0; Pu-239 sf 90 sc 48;
 * Pu-240 sc 100; Pu-241 sf 105 sc 36; fission products 6 per pair; other absorbers (water, cladding, structure) a constant
 * 0.40 b per heavy atom; Xe-135 + Sm-149 as a 3 % equilibrium reactivity loss reached in a few days; nu: 2.43, 2.8,
 * 2.88, 2.95. Results: k-inf 1.32 fresh, ~0.91 at 50 GWd/t; at 50 GWd/t ~0.7 % U-235 and ~1.2 % Pu left, more than half
 * of fissions in plutonium. Real ballparks (WNA, IAEA, NEA): LWR discharge 45-55 GWd/tU at 4-5 % enrichment, ~0.8 % U-235
 * and ~1 % Pu in spent fuel, about a third of the energy over a fuel's life from plutonium fission.
 * Core: k_core = sum production / sum absorption over three equal batches, times an illustrative non-leakage
 * probability 0.96; boron worth an illustrative 10 pcm/ppm (typical PWRs: 6-10 pcm/ppm); cycle length solved so that
 * boron reaches zero at the end of the cycle. No burnable absorbers (real cores use them to cut the start-of-cycle boron). */
(function () {
  const { TAU, clamp, lerp, smooth, rng } = WT.util;
  const X = { f25: 48, c25: 10, f28: 0.12, c28: 1.0, f49: 90, c49: 48, c40: 100, f41: 105, c41: 36, fp: 6, oth: 0.4 };
  const NU = { 25: 2.43, 28: 2.8, 49: 2.88, 41: 2.95 }, POIS = 0.03, SP = 0.038, DMAX = 1400, PNL = 0.96, BW = 1e-4;
  const FR = 38e6 / (3.204e-11 * 2.53e27); // fissions per heavy atom per second
  // ---------- depletion table, one row per day ----------
  const T = [];
  (function deplete() {
    const N = { 25: 0.045, 36: 0, 28: 0.955, np: 0, 49: 0, 40: 0, 41: 0, 42: 0, fp: 0, f25: 0, fpu: 0, f28: 0, e: 0, epu: 0 };
    const h = 0.5 * 86400;
    for (let d = 0; d <= DMAX + 0.01; d += 0.5) {
      const fis = X.f25 * N[25] + X.f28 * N[28] + X.f49 * (N[49]) + X.f41 * N[41];
      const prod = NU[25] * X.f25 * N[25] + NU[28] * X.f28 * N[28] + NU[49] * X.f49 * N[49] + NU[41] * X.f41 * N[41];
      const abFP = X.fp * N.fp, ab = (X.f25 + X.c25) * N[25] + (X.f28 + X.c28) * N[28] + (X.f49 + X.c49) * N[49] + X.c40 * N[40] + (X.f41 + X.c41) * N[41] + abFP + X.oth;
      const puShare = (X.f49 * N[49] + X.f41 * N[41]) / fis;
      if (Math.abs(d - Math.round(d)) < 1e-6) T.push({ n25: N[25], n36: N[36], n28: N[28], n49: N[49] + N.np, n40: N[40], n41: N[41], n42: N[42], f25: N.f25, fpu: N.fpu, f28: N.f28, prod, ab, abFP, pu: puShare, epu: N.e > 0 ? N.epu / N.e : 0 });
      const phi = FR / fis, R = (s) => s * phi * h;
      const a25 = R(X.f25 + X.c25) * N[25], f25 = R(X.f25) * N[25], c25 = R(X.c25) * N[25], c28 = R(X.c28) * N[28], f28 = R(X.f28) * N[28], np = N.np * (1 - Math.exp(-0.2943 * 0.5));
      const a49 = R(X.f49 + X.c49) * N[49], f49 = R(X.f49) * N[49], c49 = R(X.c49) * N[49], c40 = R(X.c40) * N[40], a41 = R(X.f41 + X.c41) * N[41], f41 = R(X.f41) * N[41], c41 = R(X.c41) * N[41];
      N[25] -= a25; N[36] += c25; N[28] -= c28 + f28; N.np += c28 - np; N[49] += np - a49; N[40] += c49 - c40; N[41] += c40 - a41; N[42] += c41;
      N.fp += f25 + f28 + f49 + f41; N.f25 += f25; N.fpu += f49 + f41; N.f28 += f28; N.e += f25 + f28 + f49 + f41; N.epu += f49 + f41;
    }
  })();
  const row = (d) => T[clamp(Math.round(d), 0, T.length - 1)];
  const kinf = (d, pois = 1) => { const q = row(d); return (q.prod / q.ab) * (1 - POIS * pois); };
  const kOfB = (b) => kinf(b / SP);
  // ---------- three-batch core: cycle length so boron is zero at end of cycle ----------
  function kCore(bc, b) { let P = 0, A = 0; for (let i = 0; i < 3; i++) { const q = row((b + i * bc) / SP); P += q.prod; A += q.ab; } return (P / A) * (1 - POIS) * PNL; }
  let BC = 10; { let lo = 3, hi = 30; for (let i = 0; i < 40; i++) { const m = (lo + hi) / 2; if (kCore(m, m) > 1) lo = m; else hi = m; } BC = (lo + hi) / 2; }
  const CYC_D = BC / SP, CYC_M = CYC_D / 30.44; // cycle length in days and months at full power
  // ---------- the pellet: 1000 atoms; A = the 45 U-235 slots, B = the U-238 slots that get touched first ----------
  const PERM = []; { const q = rng(17); const idx = [...Array(1000).keys()]; for (let i = 999; i > 0; i--) { const j = Math.floor(q() * (i + 1)); [idx[i], idx[j]] = [idx[j], idx[i]]; } PERM.push(...idx); }
  const type = new Uint8Array(1000); // 0 U-238, 1 U-235, 2 U-236, 3 Pu-239, 4 other Pu, 5 fission products
  function assign(d) {
    const q = row(d), A = PERM.slice(0, 45), n5 = Math.round(1000 * q.n25), n6 = Math.round(1000 * q.n36);
    type.fill(0);
    A.forEach((s, k) => (type[s] = k < n5 ? 1 : k < n5 + n6 ? 2 : 5));
    const nF = Math.round(1000 * (q.fpu + q.f28)), nO = Math.round(1000 * (q.n40 + q.n41 + q.n42)), n9 = Math.round(1000 * q.n49);
    for (let k = 0; k < nF + nO + n9 && 45 + k < 1000; k++) type[PERM[45 + k]] = k < nF ? 5 : k < nF + nO ? 4 : 3;
    return q;
  }
  const flashes = []; let flT = 0;
  const geo = {};
  function grabSetup(cv, S) {
    let drag = null;
    const inR = (b, x, y, m = 12) => b && x > b.x - m && x < b.x + b.w + m && y > b.y - m && y < b.y + b.h + m;
    const sync = (k, v) => { S.set(k, v); document.querySelectorAll(`#burnup [data-bind="${k}"]`).forEach((i) => (i.value = v)); };
    const apply = (x) => {
      if (drag === "box") sync("d", Math.round(clamp((x - geo.box.x) / geo.box.w, 0, 1) * DMAX / 10) * 10);
      else if (drag === "k") sync("d", Math.round(clamp((x - geo.k.x0) / (geo.k.x1 - geo.k.x0), 0, 1) * DMAX / 10) * 10);
      else if (drag === "core") sync("m", Math.round(clamp((x - geo.core.x) / geo.core.w, 0, 1) * 108) / 2);
    };
    const which = (x, y) => S.mode === "core" ? (inR(geo.core, x, y, 20) ? "core" : null) : inR(geo.box, x, y) ? "box" : geo.k && y > geo.k.y0 - 20 && y < geo.k.y1 + 20 && x > geo.k.x0 - 10 && x < geo.k.x1 + 10 ? "k" : null;
    WT.grab(cv, {
      down(x, y) { drag = which(x, y); if (!drag) return false; apply(x); return true; },
      move(x) { if (drag) apply(x); }, up() { drag = null; }, cancel() { drag = null; },
      hover(x, y) { cv.style.cursor = which(x, y) ? "ew-resize" : ""; },
    });
  }
  const fmtBu = (d) => (SP * d).toFixed(0);

  WT.chapter("burnup", {
    level: 1, num: "Lesson 1", title: "Fuel burnup", short: "Burnup",
    html: `
<div class="step">
  <h3>A pellet over its life</h3>
  <p>Here are a thousand atoms from a fresh fuel pellet: 45 are uranium-235, the rest uranium-238. Run the reactor and watch the uranium-235 split while new atoms appear. <b>Burnup</b> counts the energy taken out, in gigawatt-days per tonne of uranium; water reactors stop at about 45–55.</p>
  <div class="ctl"><label for="bu-d1">Days at full power</label><input id="bu-d1" type="range" data-bind="d" data-instant min="0" max="1400" step="10" value="400"><output data-show="d" data-fmt="0"></output></div>
</div>
<div class="step">
  <h3>Plutonium joins in</h3>
  <p>Uranium-238 catches neutrons and becomes plutonium-239, which splits too. Late in life more than half of the fissions are in plutonium; over the whole life about a third of the energy comes from it.</p>
  <div class="ctl"><label for="bu-d2">Days at full power</label><input id="bu-d2" type="range" data-bind="d" data-instant min="0" max="1400" step="10" value="1000"><output data-show="d" data-fmt="0"></output></div>
</div>
<div class="step">
  <h3>Poisons pile up</h3>
  <p>Every fission leaves two fission products, and some of them soak up neutrons. With less uranium-235 and more poison, <i>k</i><sub>∞</sub> (new fissions per fission in an endless lattice of this fuel) drifts down until the fuel can no longer keep a chain going alone.</p>
  <div class="ctl"><label for="bu-d3">Days at full power</label><input id="bu-d3" type="range" data-bind="d" data-instant min="0" max="1400" step="10" value="700"><output data-show="d" data-fmt="0"></output></div>
</div>
<div class="step">
  <h3>Boron and reloads</h3>
  <p>A core mixes fresh, middle-aged and old fuel. Fresh fuel has too much reactivity, so boron dissolved in the cooling water soaks up the surplus and is slowly diluted. When it reaches zero, the oldest third goes out and fresh fuel comes in.</p>
  <div class="ctl"><label for="bu-m">Months at full power</label><input id="bu-m" type="range" data-bind="m" data-instant min="0" max="54" step="0.5" value="8"><output data-show="m" data-fmt="1"></output></div>
</div>`,
    setup(S) { S.set("mode", "rod"); S.set("d", 400); S.set("m", 8); },
    steps: [
      (S) => { S.set("mode", "rod"); S.set("d", 400); },
      (S) => { S.set("mode", "pu"); S.set("d", 1000); },
      (S) => { S.set("mode", "k"); S.set("d", 700); },
      (S) => { S.set("mode", "core"); S.set("m", 8); },
    ],
    frame(g, S, dt) {
      const { W, H, c } = g, phone = W < 600, fs = phone ? 11 : 13, snap = document.body.classList.contains("shot");
      if (!S.grabbed) { S.grabbed = true; grabSetup(g.ctx.canvas, S); }
      if (S.mode === "core") drawCore(g, S, phone, fs);
      else drawRod(g, S, dt, phone, fs, snap);
      g.label("illustrative model", W - 6, H - 10, { color: c.faint, size: 10, align: "right" });
    },
  });

  // ---------- scenes 1-3 ----------
  function drawRod(g, S, dt, phone, fs, snap) {
    const { W, H, c, ctx } = g, d = clamp(S.d, 0, DMAX), q = assign(d);
    const box = { x: W * 0.05, y: H * (phone ? 0.1 : 0.1), w: W * 0.9, h: H * (phone ? 0.36 : 0.42) };
    const nx = phone ? 50 : 40, ny = Math.ceil(1000 / nx), sp = Math.min(box.w / nx, box.h / ny);
    const ox = box.x + (box.w - sp * nx) / 2 + sp / 2, oy = box.y + (box.h - sp * ny) / 2 + sp / 2;
    const P = (i) => [ox + (i % nx) * sp, oy + Math.floor(i / nx) * sp];
    geo.box = box; geo.k = null;
    // pellet backing: warm, dimmer as the fissile atoms run down
    const heat = clamp(q.prod / T[0].prod, 0.3, 1);
    ctx.save(); const gr = ctx.createRadialGradient(box.x + box.w / 2, box.y + box.h / 2, 10, box.x + box.w / 2, box.y + box.h / 2, Math.max(box.w, box.h) * 0.7);
    gr.addColorStop(0, g.rgba(c.warm, 0.13 * heat + 0.03)); gr.addColorStop(1, g.rgba(c.warm, 0.02)); ctx.fillStyle = gr;
    ctx.beginPath(); if (ctx.roundRect) ctx.roundRect(box.x - 6, box.y - 6, box.w + 12, box.h + 12, 14); else ctx.rect(box.x - 6, box.y - 6, box.w + 12, box.h + 12); ctx.fill(); ctx.restore();
    // U-238: one path of small dots
    ctx.save(); ctx.fillStyle = g.rgba(c.faint, 0.55); ctx.beginPath();
    for (let i = 0; i < 1000; i++) if (type[i] === 0) { const [x, y] = P(i); ctx.moveTo(x + sp * 0.16, y); ctx.arc(x, y, sp * 0.16, 0, TAU); }
    ctx.fill(); ctx.restore();
    const rb = sp * 0.42;
    for (let i = 0; i < 1000; i++) {
      const t = type[i]; if (!t) continue; const [x, y] = P(i);
      if (t === 1) { g.glow(x, y, rb * 2.6, c.warm, 0.35); g.ball(x, y, rb, c.warm); }
      else if (t === 2) g.ring(x, y, rb * 0.75, c.warm, 1.2, 0.7);
      else if (t === 3) { g.glow(x, y, rb * 2.6, c.alpha, 0.3); g.ball(x, y, rb, c.alpha); }
      else if (t === 4) g.ball(x, y, rb * 0.8, c.alpha, 0.5);
      else { g.dot(x - rb * 0.4, y - rb * 0.15, rb * 0.42, c.soft, 0.85); g.dot(x + rb * 0.42, y + rb * 0.2, rb * 0.36, c.soft, 0.85); }
    }
    // fission flashes on the fissile atoms, split U / Pu by the current share
    if (!snap && dt > 0) {
      flT += dt * 7;
      while (flT > 1) { flT -= 1; const pu = Math.random() < q.pu, want = pu ? 3 : 1; for (let k = 0; k < 40; k++) { const i = Math.floor(Math.random() * 1000); if (type[i] === want) { flashes.push({ i, t: S.time, pu }); break; } } }
    }
    for (let k = flashes.length - 1; k >= 0; k--) { const f = flashes[k], a = S.time - f.t; if (a > 0.5) { flashes.splice(k, 1); continue; } const [x, y] = P(f.i); g.glow(x, y, sp * (1 + 4 * a), f.pu ? c.alpha : c.warm, 0.8 * (1 - a / 0.5)); }
    while (flashes.length > 40) flashes.shift();
    // a time scrubber along the pellet's lower edge: drag anywhere on the pellet
    { const sy = box.y + box.h + 4, sx = lerp(box.x, box.x + box.w, d / DMAX), pulse = 0.5 + 0.5 * Math.sin(S.time * 3);
      g.line(box.x, sy, box.x + box.w, sy, c.soft, 2, 0.25); g.line(box.x, sy, sx, sy, c.warm, 2.5, 0.8);
      g.glow(sx, sy, 14 + 4 * pulse, c.warm, 0.5); g.ball(sx, sy, phone ? 5 : 6, c.warm); }
    // ---------- right / lower panel ----------
    const pan = { x: W * 0.05, y: box.y + box.h + (phone ? 34 : 44), w: W * 0.9, h: H * 0.92 - (box.y + box.h + (phone ? 34 : 44)) };
    const bu = SP * d;
    g.label(WT.trf("{a} days · burnup {b} GWd/t", d.toFixed(0), bu.toFixed(1)), box.x, H * 0.045, { color: c.ink, size: fs + 1, weight: 700, align: "left", raw: true });
    if (S.mode === "k") drawK(g, S, d, q, pan, phone, fs);
    else {
      const rows = [[c.warm, "uranium-235", 1000 * q.n25, 45], [c.alpha, "plutonium-239", 1000 * q.n49, 12], [c.alpha, phone ? "other Pu" : "other plutonium", 1000 * (q.n40 + q.n41 + q.n42), 12], [c.soft, phone ? "fission products" : "fission products (pairs)", 1000 * (q.f25 + q.fpu + q.f28), 60]];
      const pu = S.mode === "pu", rh = pan.h / (rows.length + 0.6), lw = pan.w * (phone ? 0.3 : 0.26), bw = pan.w * (pu ? (phone ? 0.3 : 0.36) : (phone ? 0.5 : 0.56));
      rows.forEach(([col, nm, v, mx], i) => {
        const y = pan.y + rh * (i + 0.5), x0 = pan.x + lw, f = clamp(v / 60, 0, 1);
        g.label(nm, pan.x + lw - 10, y, { color: c.soft, size: fs - 1, align: "right" });
        ctx.save(); ctx.fillStyle = g.rgba(c.soft, 0.08); ctx.fillRect(x0, y - 7, bw, 14); ctx.fillStyle = g.rgba(col, i === 2 ? 0.55 : 0.9); ctx.fillRect(x0, y - 7, bw * f, 14); ctx.restore();
        if (i < 3) g.glow(x0 + bw * f, y, 14, col, 0.4);
        g.label(WT.trf("{a} in 1000", v.toFixed(v < 10 ? 1 : 0)), x0 + bw * f + 10, y, { color: col === c.soft ? c.ink : col, size: fs - 2, align: "left", raw: true, weight: 600 });
      });
      if (!phone && !pu) g.label("uranium-238: the remaining ~94–95 %", pan.x + lw, pan.y + rh * 4.3, { color: c.soft, size: fs - 1, align: "left" });
      if (S.mode === "pu") {
        const R = Math.min(pan.h * 0.26, phone ? 22 : 34), cy = pan.y + pan.h * 0.42, x1 = pan.x + pan.w * (phone ? 0.68 : 0.72), x2 = pan.x + pan.w * (phone ? 0.92 : 0.9);
        g.label(phone ? "plutonium's share" : "plutonium's share", (x1 + x2) / 2, cy - R - 20, { color: c.alpha, size: fs, weight: 600 });
        dial(g, x1, cy, R, q.pu, c.alpha, phone ? "fissions" : "fissions now", `${(100 * q.pu).toFixed(0)} %`, fs);
        dial(g, x2, cy, R, q.epu, c.alpha, "energy so far", `${(100 * q.epu).toFixed(0)} %`, fs);
      }
    }
    // legend under the pellet (desktop) / caption
    const ly = box.y + box.h + (phone ? 18 : 22);
    const leg = phone ? [[c.warm, "U-235"], [c.alpha, "Pu"], [c.soft, "split"], [c.faint, "U-238"]] : [[c.warm, "U-235"], [c.alpha, "plutonium"], [c.soft, "fission products"], [c.faint, "U-238"]];
    leg.forEach(([col, s], i) => { const x = box.x + box.w * (i + 0.5) / leg.length; g.dot(x - (phone ? 24 : 40), ly, 4, col); g.label(s, x - (phone ? 17 : 32), ly, { color: c.soft, size: fs - 2, align: "left" }); });
    g.label(phone ? "each dot: 1 atom in 1000" : "each dot: one atom in a thousand", box.x + box.w, H * 0.045, { color: c.soft, size: fs - 1, align: "right" });
  }
  function dial(g, x, y, R, f, col, title, val, fs) {
    const c = g.c, a0 = Math.PI * 0.85, a1 = Math.PI * 2.15, ctx = g.ctx;
    ctx.save(); ctx.lineCap = "round"; ctx.lineWidth = Math.max(5, R * 0.16); ctx.strokeStyle = g.rgba(c.soft, 0.18); ctx.beginPath(); ctx.arc(x, y, R, a0, a1); ctx.stroke();
    ctx.strokeStyle = col; ctx.beginPath(); ctx.arc(x, y, R, a0, lerp(a0, a1, clamp(f, 0.001, 1))); ctx.stroke(); ctx.restore();
    const an = lerp(a0, a1, clamp(f, 0, 1)); g.glow(x + Math.cos(an) * R, y + Math.sin(an) * R, R * 0.45, col, 0.45);
    g.label(val, x, y + 1, { color: c.ink, size: fs + 2, weight: 700 });
    g.label(title, x, y + R + 6, { color: c.soft, size: fs - 1 });
  }
  function drawK(g, S, d, q, pan, phone, fs) {
    const { c } = g, KLO = 0.85, KHI = 1.4, BMAX = SP * DMAX;
    const x0 = pan.x + (phone ? 26 : 34), x1 = pan.x + pan.w, y0 = pan.y + 16, y1 = pan.y + pan.h - 26;
    geo.k = { x0, x1, y0, y1, BMAX }; const Xb = (b) => lerp(x0, x1, b / BMAX), Yk = (k) => lerp(y1, y0, (k - KLO) / (KHI - KLO));
    const pts = []; for (let dd = 0; dd <= DMAX; dd += 10) pts.push([Xb(SP * dd), Yk(kinf(dd, clamp(dd / 3, 0, 1)))]);
    g.clip(x0, y0 - 40, x1 - x0, y1 - y0 + 40); g.ground(pts, c.accent, (y1 - y0) * 0.9, 0.3); g.ctx.restore(); g.poly(pts, c.accent, 2.4); g.line(x0, y1, x1, y1, c.line, 1);
    g.line(x0, Yk(1), x1, Yk(1), c.ink, 1.2, 0.7, [4, 4]); g.label("k = 1", x1, Yk(1) - 10, { color: c.ink, size: fs - 1, align: "right" });
    [0, 20, 40].forEach((b) => g.label(String(b), Xb(b), y1 + 14, { color: c.faint, size: fs - 2 }));
    g.label(phone ? "GWd/t →" : "burnup (GWd/t) →", x1, y1 + 14, { color: c.soft, size: fs - 2, align: "right" });
    [1.0, 1.2, 1.4].forEach((k) => g.label(k.toFixed(1), x0 - 6, Yk(k), { color: c.faint, size: fs - 2, align: "right" }));
    // the discharge band
    g.ctx.save(); g.ctx.fillStyle = g.rgba(c.soft, 0.08); g.ctx.fillRect(Xb(45), y0, Xb(55) - Xb(45), y1 - y0); g.ctx.restore();
    g.label(phone ? "typical discharge" : "typical discharge 45–55", (Xb(45) + Xb(55)) / 2, y0 - 6, { color: c.soft, size: fs - 2 });
    const k = kinf(d, clamp(d / 3, 0, 1)), mx = Xb(SP * d), my = Yk(k);
    g.line(mx, my, mx, y1, c.accent, 1, 0.4); g.glow(mx, my, 18, c.accent, 0.55); g.dot(mx, my, 5, c.accent);
    if (k < 1.012) { const p = (S.time * 0.8) % 1; g.ring(mx, my, 8 + 40 * p, k < 1 ? c.proton : c.accent, 2, 0.8 * (1 - p)); g.label(k < 1 ? (phone ? "can't keep a chain going alone" : "this fuel alone can no longer keep a chain going") : "k∞ reaches 1", (x0 + x1) / 2, y0 + 8, { color: c.proton, size: fs - 1, weight: 600, bg: true }); }
    g.label(WT.trf("k∞ = {a}", k.toFixed(3)), mx + (SP * d > 40 ? -10 : 10), my - 16, { color: c.accent, size: fs + 1, weight: 700, align: SP * d > 40 ? "right" : "left", bg: true, raw: true });
    const share = q.abFP / q.ab;
    g.label(WT.trf("fission products catch {a} % of neutrons", (100 * share).toFixed(1)), pan.x, pan.y + pan.h + 10, { color: c.soft, size: fs - 1, raw: true, align: "left" });
  }

  // ---------- scene 4: three-batch core with boron ----------
  const CORE = []; { for (let j = -3; j <= 3; j++) for (let i = -3; i <= 3; i++) if (Math.abs(i) + Math.abs(j) <= 4 && !(Math.abs(i) === 3 && Math.abs(j) === 3)) CORE.push([i, j, ((i + 3) * 2 + (j + 3) * 1 + ((i * j) & 1)) % 3]); }
  function drawCore(g, S, phone, fs) {
    const { W, H, c, ctx } = g, m = clamp(S.m, 0, 54), days = m * 30.44, cyc = Math.floor(days / CYC_D), inC = days - cyc * CYC_D, b = SP * inC;
    const kc = kCore(BC, b), ppm = Math.max(0, (kc - 1) / kc / BW);
    const cx = W * 0.5, cy = H * (phone ? 0.2 : 0.21), cell = Math.min(W * (phone ? 0.1 : 0.06), H * (phone ? 0.05 : 0.042));
    // water + boron tint
    g.glow(cx, cy, cell * 5.2, c.cool, 0.12 + 0.18 * clamp(ppm / 2000, 0, 1));
    const sinceRe = inC / CYC_D;
    CORE.forEach(([i, j, bt]) => {
      const age = (bt + cyc) % 3, bAss = b + age * BC, x = cx + i * cell, y = cy + j * cell, kk = kOfB(bAss), hot = clamp((kk - 0.85) / 0.5, 0.1, 1);
      g.glow(x, y, cell * 0.9, c.warm, 0.12 + 0.28 * hot);
      ctx.save(); ctx.fillStyle = g.rgba(age === 0 ? c.warm : age === 1 ? c.photon : c.soft, 0.25 + 0.55 * hot); ctx.strokeStyle = g.rgba(c.ink, 0.25); ctx.lineWidth = 1;
      ctx.beginPath(); if (ctx.roundRect) ctx.roundRect(x - cell * 0.44, y - cell * 0.44, cell * 0.88, cell * 0.88, 3); else ctx.rect(x - cell * 0.44, y - cell * 0.44, cell * 0.88, cell * 0.88); ctx.fill(); ctx.stroke(); ctx.restore();
      if (age === 0 && sinceRe < 0.06 && cyc > 0) g.glow(x, y, cell * 1.4, c.fission, 0.6 * (1 - sinceRe / 0.06));
    });
    const ly = cy + cell * 4.3;
    [[c.warm, "fresh"], [c.photon, phone ? "1 cycle" : "one cycle old"], [c.soft, phone ? "2 cycles" : "two cycles old"]].forEach(([col, s], i) => {
      const x = cx + (i - 1) * (phone ? W * 0.27 : W * 0.22); ctx.save(); ctx.fillStyle = g.rgba(col, 0.75); ctx.fillRect(x - 30, ly - 5, 10, 10); ctx.restore(); g.label(s, x - 16, ly, { color: c.soft, size: fs - 2, align: "left" });
    });
    // boron sawtooth landscape
    const pan = { x: W * 0.12, y: H * (phone ? 0.52 : 0.5), w: W * 0.82, h: H * (phone ? 0.24 : 0.28) };
    geo.core = pan; const PMAX = 2400, Xm = (mm) => lerp(pan.x, pan.x + pan.w, mm / 54), Yp = (p) => lerp(pan.y + pan.h, pan.y, p / PMAX);
    const pts = []; for (let mm = 0; mm <= 54.001; mm += 0.25) { const dd = mm * 30.44, cc = Math.floor(dd / CYC_D), bb = SP * (dd - cc * CYC_D), k2 = kCore(BC, bb); pts.push([Xm(mm), Yp(Math.max(0, (k2 - 1) / k2 / BW))]); if (cc !== Math.floor((mm + 0.25) * 30.44 / CYC_D)) pts.push([Xm(mm + 0.001), Yp(0)]); }
    g.clip(pan.x, pan.y - 10, pan.w, pan.h + 10); g.ground(pts, c.cool, pan.h, 0.32); ctx.restore(); g.poly(pts, c.cool, 2.2);
    g.line(pan.x, pan.y + pan.h, pan.x + pan.w, pan.y + pan.h, c.line, 1);
    for (let k = 1; k * CYC_M < 54; k++) { const x = Xm(k * CYC_M); g.line(x, pan.y + pan.h, x, pan.y + pan.h + 6, c.fission, 2); g.label(phone ? "reload" : "reload", x, pan.y + pan.h + 16, { color: c.fission, size: fs - 2 }); }
    [0, 1000, 2000].forEach((p) => g.label(String(p), pan.x - 6, Yp(p), { color: c.faint, size: fs - 2, align: "right" }));
    g.label(phone ? "boron (ppm)" : "boron in the water (ppm)", pan.x, pan.y - 14, { color: c.cool, size: fs - 1, align: "left", weight: 600 });
    g.label(phone ? "months →" : "months at full power →", pan.x + pan.w, pan.y + pan.h + 32, { color: c.soft, size: fs - 2, align: "right" });
    const mx = Xm(m), my = Yp(ppm); g.line(mx, my, mx, pan.y + pan.h, c.cool, 1, 0.4); g.glow(mx, my, 18, c.cool, 0.6); g.dot(mx, my, 5, c.cool);
    g.label(WT.trf("{a} ppm", ppm.toFixed(0)), mx + (m > 40 ? -10 : 10), my - 16, { color: c.cool, size: fs + 1, weight: 700, align: m > 40 ? "right" : "left", bg: true, raw: true });
    g.label(WT.trf("cycle {a} months · fuel leaves at {b} GWd/t", CYC_M.toFixed(0), (3 * BC).toFixed(0)), W * 0.5, H * 0.9, { color: c.ink, size: fs + 1, weight: 600, serif: true, raw: true });
  }
})();
