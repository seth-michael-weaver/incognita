/* Neutron transport and Monte Carlo. Scenes (S.mode):
 *   "free"  = analog Monte Carlo histories in a slab (one speed, isotropic scattering, infinite in y and z; y is drawn with
 *             wrap-around, which translation symmetry allows). Flight length s = -ln(xi)/Sigma_t; at a collision: scatter with
 *             probability Sigma_s/Sigma_t, else absorbed: fission with probability Sigma_f/Sigma_a, else capture.
 *   "diff"  = fixed uniform source in a slab 8 mean free paths thick, no fission, absorption share Sigma_a/Sigma_t set by the
 *             reader. Monte Carlo flux = track-length tally in 32 bins (per source neutron, per unit area). One-group diffusion
 *             with D = 1/(3 Sigma_t) and the extrapolated edge 0.7104/Sigma_t: phi = (S/Sigma_a)[1 - cosh(x/L)/cosh(a'/L)].
 *   "power" = power iteration for k_eff in a bare slab 20 mean free paths thick, Sigma_a/Sigma_t = 0.1, nu Sigma_f/Sigma_a = 1.2
 *             (k_inf = 1.2). At each absorption floor(1.2 + xi) fission sites are banked; k_gen = banked / started; the next
 *             source is N sites resampled from the bank. Starts from a bad guess (all sites in the first 1 cm).
 *   "conv"  = Shannon entropy H = -sum p_b log2 p_b of the source on 20 bins per generation; k averaged over active generations
 *             (after 20 inactive ones) with standard error sigma/sqrt(n). Diffusion estimate for this slab (L^2 = 1/(3*0.1) cm^2,
 *             extrapolated width 21.42 cm): k = 1.2/(1 + L^2 B^2) = 1.120; a long run of this code gives 1.1185 +/- 0.0009.
 * All data illustrative one-group numbers in units of the mean free path (Sigma_t = 1 per cm). */
(function () {
  const { TAU, clamp, lerp, smooth, rng } = WT.util;
  const r = rng(41), log2 = (x) => Math.log(x) / Math.LN2;
  const FIS = 0.494; // Sigma_f / Sigma_a for nu = 2.43 and nu Sigma_f / Sigma_a = 1.2
  const dir = () => { const mu = 2 * r() - 1, ph = TAU * r(); return [mu, Math.sqrt(1 - mu * mu) * Math.cos(ph)]; }; // x and y cosines
  const flight = () => -Math.log(1 - r());
  /** one history from x0: returns {pts:[[x,y,kind]], end:'leak'|'cap'|'fis', n:sites, sites:[]}; kinds: 0 start, 1 scatter, 2 cap, 3 fis, 4 leak */
  function history(x0, T, pa, fisMode, rec, tally, bins, y0) {
    let x = x0, y = y0 == null ? r() * 100 : y0; const pts = rec ? [[x, y, 0]] : null; let sites = 0, sl = null;
    for (let guard = 0; guard < 4000; guard++) {
      const [mx, my] = dir(), s = flight(); let x1 = x + mx * s, y1 = y + my * s, end = null;
      if (x1 < 0 || x1 > T) { const f = ((x1 < 0 ? 0 : T) - x) / (mx * s); x1 = x + mx * s * f; y1 = y + my * s * f; end = "leak"; }
      x = x1; y = y1;
      if (end) { rec && pts.push([x, y, 4]); return { pts, end, sites, sl }; }
      if (r() < pa) {
        if (fisMode === 1) { const n = Math.floor(1.2 + r()); sites = n; sl = x; rec && pts.push([x, y, n ? 3 : 2]); return { pts, end: n ? "fis" : "cap", sites, sl }; }
        if (fisMode === 2 && r() < FIS) { rec && pts.push([x, y, 3]); return { pts, end: "fis", sites: r() < 0.43 ? 3 : 2, sl: x }; }
        rec && pts.push([x, y, 2]); return { pts, end: "cap", sites: 0, sl };
      }
      rec && pts.push([x, y, 1]);
    }
    return { pts, end: "cap", sites: 0, sl };
  }
  /** add track length to the bins: the segment x0->x1 in x, times the 3D path length per unit x (t._ratio) */
  function trackTally(t, nb, T, x0, x1) {
    const a = Math.min(x0, x1), b = Math.max(x0, x1), bw = T / nb, ratio = t._ratio; if (b - a < 1e-12) return;
    const i0 = clamp(Math.floor(a / bw), 0, nb - 1), i1 = clamp(Math.floor(b / bw), 0, nb - 1);
    for (let i = i0; i <= i1; i++) { const lo = Math.max(a, i * bw), hi = Math.min(b, (i + 1) * bw); if (hi > lo) t.v[i] += (hi - lo) * ratio; }
  }
  /** a fixed-source history for the flux tally (no drawing) */
  function historyT(x0, T, pa, tally, bins) {
    let x = x0;
    for (let guard = 0; guard < 4000; guard++) {
      const mu = 2 * r() - 1, s = flight(); let x1 = x + mu * s, end = false, sl = s;
      if (x1 < 0 || x1 > T) { const xb = x1 < 0 ? 0 : T; sl = (xb - x) / mu; x1 = xb; end = true; }
      tally._ratio = 1 / Math.max(1e-6, Math.abs(mu)); trackTally(tally, bins, T, x, x1);
      if (Math.abs(mu) <= 1e-6) { const i = clamp(Math.floor(x / (T / bins)), 0, bins - 1); tally.v[i] += sl; }
      x = x1; if (end) return; if (r() < pa) return;
    }
  }

  // ---------- scene state ----------
  const SL0 = 20; // slab thickness for the "free" and power scenes (mean free paths)
  const free = { live: [], done: [], cnt: { sc: 0, cap: 0, fis: 0, leak: 0 }, last: null, spawnT: 0 };
  function newFree(x, y) { const h = history(x == null ? SL0 * (0.3 + 0.4 * r()) : x, SL0, 0.1, 2, true, null, 0, y); free.live.push({ h, u: 0, kids: false }); while (free.live.length > 26) free.done.push(free.live.shift()); while (free.done.length > 14) free.done.shift(); }
  // collision density on a grid over the slab (x across, y wrapped), from many silent histories
  const GX = 80, GY = 24, grid = new Float32Array(GX * GY); let gridMax = 1, gridYH = 1;
  function silent(n, yH) { gridYH = yH; for (let k = 0; k < n; k++) { const h = history(r() * SL0, SL0, 0.1, 2, true, null, 0); for (let i = 1; i < h.pts.length; i++) { const p = h.pts[i]; if (p[2] === 4) continue;
      const gx = clamp(Math.floor(p[0] / SL0 * GX), 0, GX - 1), gy = clamp(Math.floor((((p[1] % yH) + yH) % yH) / yH * GY), 0, GY - 1), v = (grid[gy * GX + gx] += 1); if (v > gridMax) gridMax = v; } } }
  const HOFF = document.createElement("canvas"), HX = HOFF.getContext("2d"); HOFF.width = GX; HOFF.height = GY; let hImg = null, hFrame = 0;
  function drawGrid(g, box, col, data, nx, ny, mx, alpha, pw = 0.5) {
    if (HOFF.width !== nx || HOFF.height !== ny) { HOFF.width = nx; HOFF.height = ny; hImg = null; }
    if (!hImg) hImg = HX.createImageData(nx, ny); const [R, G, B] = WT.rgb01(col).map((v) => Math.round(255 * v));
    for (let i = 0; i < nx * ny; i++) { const v = Math.pow(data[i] / mx, pw); hImg.data[4 * i] = R; hImg.data[4 * i + 1] = G; hImg.data[4 * i + 2] = B; hImg.data[4 * i + 3] = Math.round(255 * alpha * clamp(v, 0, 1)); }
    HX.putImageData(hImg, 0, 0); g.ctx.save(); g.ctx.imageSmoothingEnabled = true; g.ctx.drawImage(HOFF, box.x, box.y, box.w, box.h); g.ctx.restore();
  }
  const flashes = [];
  const LAY = { used: false };
  const GRAB = {
    down(x, y) { const S = LAY.S, b = LAY.box; if (!S || !b || x < b.x || x > b.x + b.w || y < b.y || y > b.y + b.h) return false; LAY.used = true; const cx = (x - b.x) / b.w * LAY.T;
      if (LAY.mode === "free") { for (let k = 0; k < 3; k++) newFree(cx, (y - b.y) / b.w * LAY.T); flashes.push({ x, y, t: S.time, big: true }); }
      else if (LAY.mode === "power" || LAY.mode === "conv") { S.pwStart(S); for (let i = 0; i < pw.src.length; i++) pw.src[i] = clamp(cx + 0.5 * (r() - 0.5), 0, SL0); binSrc(); pw.Hs = [entropy(pw.src)]; flashes.push({ x, y, t: S.time, big: true }); }
      return false; },
    hover(x, y, e) { const b = LAY.box; e.target.style.cursor = b && LAY.mode !== "diff" && x >= b.x && x <= b.x + b.w && y >= b.y && y <= b.y + b.h ? "pointer" : ""; },
  };
  function drawFlashes(g, S) { for (let i = flashes.length - 1; i >= 0; i--) { const fl = flashes[i], a = (S.time - fl.t) / (fl.big ? 1.1 : 0.6); if (a > 1) { flashes.splice(i, 1); continue; }
      g.glow(fl.x, fl.y, (fl.big ? 30 : 10) + (fl.big ? 90 : 30) * a, g.c.fission, 0.75 * (1 - a)); if (fl.big) g.ring(fl.x, fl.y, 10 + 80 * a, g.c.fission, 2.5 * (1 - a), 0.8 * (1 - a)); }
    while (flashes.length > 80) flashes.shift(); }
  const DT = 8, NB = 32; const dif = { pa: -1, tally: { v: new Float64Array(NB), _ratio: 1 }, n: 0, show: [] };
  function difReset(pa) { dif.pa = pa; dif.tally.v.fill(0); dif.n = 0; dif.show.length = 0; for (let i = 0; i < 40000; i++) historyT(r() * DT, DT, pa, dif.tally, NB); dif.n = 40000; } // pre-converged: no early noise
  const pw = { N: 400, gen: 0, src: [], k: [], Hs: [], hist: new Float64Array(40), show: [], u: 0, inact: 20 };
  function pwReset(N) { pw.N = N; pw.gen = 0; pw.src = []; for (let i = 0; i < N; i++) pw.src.push(r()); pw.k = []; pw.Hs = [entropy(pw.src)]; pw.show = []; binSrc(); }
  function entropy(src) { const nb = 20, h = new Array(nb).fill(0); src.forEach((x) => h[clamp(Math.floor(x / SL0 * nb), 0, nb - 1)]++); let H = 0; h.forEach((v) => { if (v) { const p = v / src.length; H -= p * log2(p); } }); return H; }
  function binSrc() { pw.hist.fill(0); pw.src.forEach((x) => pw.hist[clamp(Math.floor(x / SL0 * 40), 0, 39)]++); }
  function generation() {
    const bank = [], show = [];
    for (let i = 0; i < pw.src.length; i++) { const h = history(pw.src[i], SL0, 0.1, 1, i < 8, null, 0); if (h.sites) for (let k = 0; k < h.sites; k++) bank.push(h.sl); if (i < 8) show.push(h); }
    pw.k.push(bank.length / pw.src.length); const N = pw.N, nx = [];
    for (let i = 0; i < N; i++) nx.push(bank.length ? bank[Math.floor(r() * bank.length)] : r() * SL0);
    pw.src = nx; pw.gen++; pw.Hs.push(entropy(nx)); pw.show = show; binSrc();
  }
  const stats = () => { const a = pw.k.slice(pw.inact); if (a.length < 2) return null; const m = a.reduce((s, v) => s + v, 0) / a.length, sd = Math.sqrt(a.reduce((s, v) => s + (v - m) ** 2, 0) / (a.length - 1)); return { m, se: sd / Math.sqrt(a.length), n: a.length }; };

  // ---------- drawing ----------
  function slab(g, box, T, S, bare) {
    const { c, ctx } = g; ctx.save(); const gr = ctx.createLinearGradient(box.x, 0, box.x + box.w, 0); gr.addColorStop(0, g.rgba(c.cool, 0.08)); gr.addColorStop(0.5, g.rgba(c.cool, 0.18)); gr.addColorStop(1, g.rgba(c.cool, 0.08)); ctx.fillStyle = gr;
    ctx.fillRect(box.x, box.y, box.w, box.h); ctx.restore();
    // fuel pins in water, as a backdrop (the physics uses the homogenised mixture)
    const pitch = Math.max(14, box.w / (T * 1.25)), nx = Math.floor(box.w / pitch), ny = Math.max(2, Math.floor(box.h / pitch)), pr = pitch * 0.26, br = S ? 0.06 * Math.sin(S.time * 1.7) : 0;
    if (!bare) for (let j = 0; j < ny; j++) for (let i = 0; i < nx; i++) { const x = box.x + (i + 0.5) * box.w / nx, y = box.y + (j + 0.5) * box.h / ny; g.glow(x, y, pr * 2.4, c.warm, 0.1 + br * 0.5); g.ball(x, y, pr, c.warm, 0.55); }
    g.line(box.x, box.y, box.x, box.y + box.h, c.warm, 1.6, 0.8); g.line(box.x + box.w, box.y, box.x + box.w, box.y + box.h, c.warm, 1.6, 0.8);
    if (g.W >= 600) g.label("vacuum", box.x - 6, box.y + box.h / 2, { color: c.faint, size: 11, align: "right" });
  }
  const KIND = (c, k) => [c.ink, c.neutron, c.soft, c.fission, c.proton][k];
  function drawTrack(g, box, T, h, u, alpha, yH) {
    const { c } = g, sx = box.w / T, P = (x, y) => [box.x + x * sx, box.y + (((y % yH) + yH) % yH) * sx];
    const n = h.pts.length, upto = Math.min(n - 1, Math.floor(u)), f = u - Math.floor(u);
    for (let i = 0; i < upto + (upto < n - 1 ? 1 : 0); i++) {
      const a = h.pts[i], b = h.pts[i + 1], t = i < upto ? 1 : f; let [x0, y0] = P(a[0], a[1]); const bx = lerp(a[0], b[0], t), by = lerp(a[1], b[1], t);
      let [x1, y1] = P(bx, by);
      if (Math.abs(y1 - y0) > box.h * 0.5) { y0 = y1; x0 = x1; } // wrapped: skip the jump
      g.line(x0, y0, x1, y1, c.neutron, 1.2, 0.55 * alpha);
      if (i < upto) { const [px, py] = P(b[0], b[1]); const k = b[2]; if (k === 3) { g.glow(px, py, 12, c.fission, 0.6 * alpha); g.dot(px, py, 3.2, c.fission, alpha); } else if (k === 2) g.dot(px, py, 3, c.soft, alpha); else if (k === 4) g.dot(px, py, 3, c.proton, alpha); else g.dot(px, py, 1.8, c.neutron, 0.8 * alpha); }
      if (i === upto && upto < n - 1 && alpha > 0.9) g.ball(x1, y1, 3.4, c.neutron, 1);
    }
  }

  WT.chapter("transport", {
    level: 3, num: "Lesson 1", title: "Neutron transport and Monte Carlo", short: "Monte Carlo",
    html: `
<div class="step">
  <h3>The transport equation</h3>
  <p>Exactly, the neutrons obey the Boltzmann equation for the angular flux <i>ψ</i>(<b>r</b>, <b>Ω</b>, <i>E</i>): <b>Ω</b>·∇<i>ψ</i> + Σ<sub>t</sub><i>ψ</i> = ∫∫Σ<sub>s</sub><i>ψ</i>′ d<b>Ω</b>′d<i>E</i>′ + (<i>χ</i>/4π<i>k</i>)∫<i>ν</i>Σ<sub>f</sub><i>φ</i>′ d<i>E</i>′. Monte Carlo solves it by playing neutrons one at a time: fly <i>s</i> = −ln <i>ξ</i> / Σ<sub>t</sub>, then scatter, be captured, or cause fission.</p>
  <div class="btns"><button class="btn" data-act="trnew">New neutron</button></div>
</div>
<div class="step">
  <h3>Where diffusion fails</h3>
  <p>Diffusion assumes nearly the same flux in every direction. That fails within a free path or two of a surface and in strong absorbers. Compare it with the Monte Carlo flux in a slab with a uniform source while you raise the absorption.</p>
  <div class="ctl"><label for="tr-pa">Absorption Σ<sub>a</sub>/Σ<sub>t</sub></label><input id="tr-pa" type="range" data-bind="pa" data-instant min="0.05" max="0.8" step="0.05" value="0.5"><output data-show="pa" data-fmt="2"></output></div>
</div>
<div class="step">
  <h3>Power iteration</h3>
  <p>For <i>k</i><sub>eff</sub>, each generation's fission sites become the next generation's source; <i>k</i> is the number of sites banked per neutron started. Start from a bad guess, every neutron at one edge, and watch the source spread into the fundamental mode.</p>
  <div class="btns"><button class="btn" data-act="trbad">Restart from a bad guess</button></div>
</div>
<div class="step">
  <h3>Is the source converged?</h3>
  <p>The Shannon entropy <i>H</i> = −Σ <i>p</i><sub>b</sub> log<sub>2</sub> <i>p</i><sub>b</sub> of the binned source levels off once the source has settled; only then are generations averaged. The error bar on <i>k</i> shrinks as 1/√<i>N</i> with the histories counted.</p>
  <div class="ctl"><label for="tr-n">Histories per generation</label><input id="tr-n" type="range" data-bind="nh" data-instant min="100" max="2000" step="100" value="400"><output data-show="nh" data-fmt="0"></output></div>
</div>`,
    setup(S) {
      S.set("mode", "free"); S.set("pa", 0.5); S.set("nh", 400); S.u = 0;
      S.on("trnew", () => { newFree(); });
      S.on("trbad", () => { pwStart(S); });
      function pwStart(S) { pwReset(Math.round(S.nh)); for (let i = 0; i < pw.src.length; i++) pw.src[i] = r(); binSrc(); pw.Hs = [entropy(pw.src)]; pw.u = 0; }
      S.pwStart = pwStart;
    },
    steps: [
      (S) => { S.set("mode", "free"); if (!free.live.length) { newFree(); newFree(); } },
      (S) => { S.set("mode", "diff"); difReset(S.pa); },
      (S) => { S.set("mode", "power"); if (!pw.gen) S.pwStart(S); },
      (S) => { S.set("mode", "conv"); if (!pw.gen || pw.N !== Math.round(S.nh)) S.pwStart(S); },
    ],
    frame(g, S, dt) {
      if (g.W < 40 || g.H < 40) return;
      const { W, H, c } = g, phone = W < 600, fs = phone ? 11 : 13, snap = document.body.classList.contains("shot"), mode = S.mode;
      const rd = { color: c.ink, size: fs + 1, weight: 600, serif: true }, yRd = H * 0.93;
      const box = { x: W * 0.08, y: H * 0.05, w: W * 0.84, h: H * (mode === "free" ? 0.56 : phone ? 0.24 : 0.26) };
      if (!g.ctx.canvas._trg) { g.ctx.canvas._trg = 1; WT.grab(g.ctx.canvas, GRAB); }
      LAY.S = S; LAY.mode = mode; LAY.box = box; LAY.T = mode === "diff" ? DT : SL0;
      if (mode === "free") {
        slab(g, box, SL0, S); const yH = box.h / (box.w / SL0), sx = box.w / SL0;
        // collision density blooms as histories accumulate
        silent(snap && gridMax < 50 ? 2500 : 25, yH); if (gridMax > 3000) { for (let i = 0; i < grid.length; i++) grid[i] *= 0.5; gridMax *= 0.5; }
        drawGrid(g, box, c.photon, grid, GX, GY, gridMax, 0.6, 1.6);
        if (snap && free.done.length < 4) { for (let i = 0; i < 26; i++) newFree(); free.live.forEach((L, i) => (L.u = L.h.pts.length * (0.2 + 0.75 * ((i * 0.37) % 1)))); }
        free.spawnT += dt; if (free.spawnT > 0.5 && free.live.length < 12) { free.spawnT = 0; newFree(); }
        free.done.forEach((L, i) => drawTrack(g, box, SL0, L.h, L.h.pts.length, 0.2 + 0.03 * i, yH));
        for (const L of free.live) { const was = Math.floor(L.u); L.u = Math.min(L.h.pts.length - 1, L.u + dt * 7); drawTrack(g, box, SL0, L.h, L.u, 1, yH);
          // the head glows; a finished fission starts the next neutrons of the chain
          const n = L.h.pts.length, i = Math.max(0, Math.min(n - 2, Math.floor(L.u) || 0)), a = L.h.pts[i], b = L.h.pts[i + 1], f = L.u - i;
          if (a && b && L.u < n - 1) { const hx = box.x + lerp(a[0], b[0], f) * sx, hy = box.y + ((((lerp(a[1], b[1], f)) % yH) + yH) % yH) * sx; g.glow(hx, hy, 12, c.neutron, 0.5); }
          if (Math.floor(L.u) > was) { const p = L.h.pts[Math.floor(L.u)]; if (p) { const px = box.x + p[0] * sx, py = box.y + (((p[1] % yH) + yH) % yH) * sx; if (p[2] === 3) flashes.push({ x: px, y: py, t: S.time, big: true }); else if (p[2] === 1) flashes.push({ x: px, y: py, t: S.time }); } }
          if (!L.kids && L.u >= n - 1 && L.h.end === "fis") { L.kids = true; const p = L.h.pts[n - 1]; if (free.live.length < 24) for (let k = 0; k < L.h.sites; k++) newFree(p[0], p[1]); } }
        for (let i = free.live.length - 1; i >= 0; i--) { const L = free.live[i]; if (L.u >= L.h.pts.length - 1 && (L.kids || L.h.end !== "fis")) { free.done.push(free.live.splice(i, 1)[0]); } } while (free.done.length > 14) free.done.shift();
        drawFlashes(g, S);
        g.label(phone ? "glow: collision density" : "amber glow: where collisions pile up", box.x + box.w - 6, box.y + box.h - 12, { color: c.photon, size: fs - 2, weight: 600, align: "right", bg: true });
        if (!LAY.used) g.label("tap the slab to start neutrons", box.x + box.w / 2, box.y + 14, { color: c.ink, size: fs - 1, weight: 600, bg: true, alpha: 0.9 });
        // legend
        const ly = box.y + box.h + 18, items = [["scatter", c.neutron], ["capture", c.soft], ["fission", c.fission], ["leak", c.proton]];
        items.forEach(([s, col], i) => { const x = W * (0.14 + 0.24 * i); g.dot(x - (phone ? 26 : 32), ly, 4, col); g.label(s, x - (phone ? 18 : 24), ly, { color: c.soft, size: fs - 1, align: "left" }); });
        // live sample: the free flight
        const xi = 0.05 + 0.9 * ((Math.sin(S.time * 0.9) + 1) / 2), s = -Math.log(xi);
        const fx0 = W * 0.12, fx1 = W * 0.88, fy = H * 0.82, sc = (fx1 - fx0) / 4;
        const pts = []; for (let i = 0; i <= 80; i++) { const ss = 4 * i / 80; pts.push([fx0 + ss * sc, fy - Math.exp(-ss) * H * 0.1]); }
        g.line(fx0, fy, fx1, fy, c.line, 1); g.ground(pts, c.neutron, 20, 0.3); g.poly(pts, c.neutron, 2);
        g.label("chance to fly at least s:  e^(−Σₜ s)", fx0, fy - H * 0.12, { color: c.soft, size: fs - 1, align: "left" });
        g.line(fx0 + s * sc, fy, fx0 + s * sc, fy - xi * H * 0.1, c.warm, 1.6); g.dot(fx0 + s * sc, fy - xi * H * 0.1, 4.5, c.warm); g.line(fx0, fy - xi * H * 0.1, fx0 + s * sc, fy - xi * H * 0.1, c.warm, 1, 0.6, [3, 3]);
        [0, 1, 2, 3, 4].forEach((v) => g.label(v === 4 ? "4 free paths" : String(v), fx0 + v * sc, fy + 12, { color: c.faint, size: fs - 2 }));
        g.label(`ξ = ${xi.toFixed(2)}  →  s = −ln ξ / Σₜ = ${s.toFixed(2)} free paths`, W / 2, yRd, rd);
      } else if (mode === "diff") {
        const T = DT, pa = S.pa; if (Math.abs(pa - dif.pa) > 1e-6) difReset(pa);
        const sx = box.w / T, yH = box.h / sx; slab(g, box, T, S, true);
        // run histories: tally all, keep a few tracks to show
        const nRun = snap ? (dif.n < 60000 ? 60000 : 0) : 1500; for (let i = 0; i < nRun; i++) historyT(r() * T, T, pa, dif.tally, NB); dif.n += nRun;
        // the slab is symmetric, so the two halves of the tally are averaged (halves the noise, changes nothing else)
        const V = new Float64Array(NB); for (let i = 0; i < NB; i++) V[i] = (dif.tally.v[i] + dif.tally.v[NB - 1 - i]) / 2;
        if (!snap) S.u += dt; if (dif.show.length < 24 || S.u > 0.045) { S.u = 0; dif.show.push({ h: history(r() * T, T, pa, 0, true, null, 0), u: 0, age: 0 }); while (dif.show.length > 40) dif.show.shift(); }
        { const mx = Math.max(...V, 1e-9), band = new Float32Array(NB * 2); for (let i = 0; i < NB; i++) band[i] = band[NB + i] = V[i]; drawGrid(g, box, c.accent, band, NB, 2, mx, 0.45, 1); }
        // neutrons born everywhere, random-walking until absorbed (grey dot) or escaping through a surface (red dot); each fades after it ends
        dif.show.forEach((L) => { const n = L.h.pts.length - 1; L.u = snap ? n : Math.min(n, L.u + dt * 6); if (L.u >= n) L.age += dt; const a = snap ? 0.7 : clamp(1 - L.age / 1.6, 0, 1); if (a <= 0) return;
          drawTrack(g, box, T, L.h, L.u, a, yH);
          if (L.u < n) { const i = Math.floor(L.u), f = L.u - i, A = L.h.pts[i], B = L.h.pts[i + 1], x = lerp(A[0], B[0], f), y = lerp(A[1], B[1], f), px = box.x + x * sx, py = box.y + (((y % yH) + yH) % yH) * sx; g.glow(px, py, 9, c.neutron, 0.5); g.ball(px, py, 3.2, c.neutron, 1); }
          else if (L.h.end === "leak" && L.age < 0.6) { const P = L.h.pts[n], px = box.x + P[0] * sx, py = box.y + (((P[1] % yH) + yH) % yH) * sx; g.glow(px, py, 16, c.proton, 0.6 * (1 - L.age / 0.6)); } });
        g.label(`${T} free paths`, box.x + box.w / 2, box.y + box.h + 12, { color: c.warm, size: fs - 1 });
        // flux landscape: MC vs diffusion
        const py0 = H * (phone ? 0.42 : 0.44), py1 = H * 0.84, bw = T / NB, S0 = 1 / T, Dd = 1 / 3, L = Math.sqrt(Dd / pa), ah = T / 2, ae = ah + 0.7104;
        const phiD = (x) => S0 / pa * (1 - Math.cosh((x - ah) / L) / Math.cosh(ae / L)), top = S0 / pa;
        const X = (x) => box.x + x * sx, Y = (v) => lerp(py1, py0, v / (top * 1.08));
        const mc = [], df = []; for (let i = 0; i < NB; i++) { const v = V[i] / (dif.n * bw); mc.push([X((i + 0.5) * bw), Y(v)]); }
        for (let i = 0; i <= 120; i++) { const x = T * i / 120; df.push([X(x), Y(phiD(x))]); }
        g.line(box.x, py1, box.x + box.w, py1, c.line, 1); g.line(box.x, Y(top), box.x + box.w, Y(top), c.soft, 1, 0.4, [2, 4]);
        g.label("infinite medium S/Σₐ", box.x + box.w, Y(top) - 10, { color: c.soft, size: fs - 2, align: "right" });
        const mcS = [[X(0), mc[0][1]], ...mc, [X(T), mc[NB - 1][1]]];
        g.clip(0, py0 - 4, W, py1 - py0 + 4); g.ground(mcS, c.accent, py1 - Y(top), 0.3); g.ctx.restore(); g.area([...df, ...mcS.slice().reverse()], c.warm, 0.28); g.poly(mcS, c.accent, 2.6); g.poly(df, c.warm, 2, 0.95, [6, 4]); // the gap: where diffusion is wrong
        g.label("Monte Carlo", X(T * 0.5), Y(V[NB / 2] / (dif.n * bw)) + 16, { color: c.accent, size: fs - 1, weight: 600, bg: true });
        g.label("diffusion", X(T * 0.13), Y(phiD(T * 0.13)) - 14, { color: c.warm, size: fs - 1, weight: 600, bg: true });
        g.label("flux", box.x, py0 - 12, { color: c.soft, size: fs - 1, align: "left" });
        const edge = V[0] / (dif.n * bw), mid = (V[NB / 2 - 1] + V[NB / 2]) / 2 / (dif.n * bw);
        const eE = phiD(bw / 2) / edge - 1, eM = phiD(ah) / mid - 1, p = (v) => `${v >= 0 ? "+" : "−"}${Math.abs(100 * v).toFixed(0)} %`;
        g.label(`diffusion vs Monte Carlo: ${p(eE)} at the surface, ${p(eM)} in the middle`, W / 2, yRd, rd);
      } else {
        // ---------- power iteration ----------
        if (!pw.src.length) S.pwStart(S);
        if (mode === "conv" && pw.N !== Math.round(S.nh)) S.pwStart(S);
        if (snap && pw.gen < (mode === "conv" ? 80 : 12)) { while (pw.gen < (mode === "conv" ? 80 : 12)) generation(); pw.u = 0.7; }
        if (!snap) { pw.u += dt; if (pw.u > (mode === "conv" ? 0.35 : 0.8) && pw.gen < 400) { pw.u = 0; generation(); } }
        const sx = box.w / SL0, yH = box.h / sx; slab(g, box, SL0, S);
        { const band = new Float32Array(80); for (let i = 0; i < 40; i++) band[i] = band[40 + i] = pw.hist[i]; drawGrid(g, box, c.fission, band, 40, 2, Math.max(...pw.hist, 1), 0.45); }
        if (pw.gen !== LAY.gen) { LAY.gen = pw.gen; for (let k = 0; k < 18 && k < pw.src.length; k++) flashes.push({ x: box.x + pw.src[k] * sx, y: box.y + 4 + (box.h - 8) * ((k * 0.6180339) % 1), t: S.time - (snap ? 0.25 : 0.5 * r()) }); }
        drawFlashes(g, S);
        if (!LAY.used) g.label(phone ? "tap: drop the source there" : "tap the slab to drop the whole source there", box.x + box.w - 8, box.y + 12, { color: c.ink, size: fs - 2, weight: 600, align: "right", bg: true });
        // source sites: glowing points (deterministic y per index)
        const ns = Math.min(pw.src.length, 500);
        for (let i = 0; i < ns; i++) { const x = box.x + pw.src[i] * sx, y = box.y + 4 + (box.h - 8) * ((i * 0.6180339) % 1); g.dot(x, y, phone ? 1.6 : 2, c.fission, 0.75); }
        const ut = clamp(pw.u / 0.6, 0, 1); pw.show.forEach((h) => drawTrack(g, box, SL0, h, ut * (h.pts.length - 1), 0.9, yH));
        g.label(`generation ${pw.gen}`, box.x + 8, box.y + 12, { color: c.ink, size: fs - 1, weight: 600, align: "left", bg: true });
        const py0 = box.y + box.h + H * 0.06, py1 = box.y + box.h + H * (phone ? 0.2 : 0.2), ky0 = H * (phone ? 0.6 : 0.6), ky1 = H * 0.84;
        if (mode === "power") {
          // source shape vs fundamental mode
          const hp = [], Te = SL0 + 2 * 0.7104, MEAN = 2 * Te / (Math.PI * SL0) * Math.cos(Math.PI * 0.7104 / Te), X = (x) => box.x + x * sx, Y = (v) => lerp(py1, py0, v);
          for (let i = 0; i < 20; i++) hp.push([X((i + 0.5) * SL0 / 20), Y((pw.hist[2 * i] + pw.hist[2 * i + 1]) / (pw.N / 20) / 2)]);
          const cs = []; for (let i = 0; i <= 80; i++) { const x = SL0 * i / 80; cs.push([X(x), Y(Math.sin(Math.PI * (x + 0.7104) / Te) / MEAN / 2)]); }
          g.line(box.x, py1, box.x + box.w, py1, c.line, 1); g.clip(box.x - 2, py0 - 2, box.w + 4, py1 - py0 + 4); g.ground(hp, c.fission, py1 - py0, 0.35); g.poly(hp, c.fission, 2.2); g.ctx.restore(); g.poly(cs, c.soft, 1.4, 0.9, [5, 4]);
          g.label(phone ? "source · dashed: fundamental mode" : "fission source · dashed: fundamental mode", box.x, py0 - 8, { color: c.soft, size: fs - 1, align: "left" });
        } else {
          // entropy per generation
          const GC = Math.max(80, pw.k.length), Hm = log2(20), X = (gn) => box.x + box.w * gn / GC, Y = (h) => lerp(py1, py0, (h - 2.5) / (Hm - 2.5));
          const ep = pw.Hs.map((h, i) => [X(i), Y(clamp(h, 2.5, Hm))]);
          g.line(box.x, py1, box.x + box.w, py1, c.line, 1); g.line(X(pw.inact), py0, X(pw.inact), ky1, c.soft, 1, 0.5, [3, 4]);
          g.clip(0, py0 - 4, W, py1 - py0 + 4); g.ground(ep, c.alpha, py1 - py0, 0.3); g.ctx.restore(); g.poly(ep, c.alpha, 2.2);
          g.label("source entropy H (bits)", box.x, py0 - 8, { color: c.soft, size: fs - 1, align: "left" });
          g.label(phone ? "inactive | active" : "inactive  |  active generations", X(pw.inact), py1 + 11, { color: c.soft, size: fs - 2 });
        }
        // k per generation
        const KL = 1.0, KH = 1.24, G = mode === "conv" ? Math.max(80, pw.k.length) : 40, X = (gn) => box.x + box.w * gn / G, Y = (k) => lerp(ky1, ky0, (clamp(k, KL, KH) - KL) / (KH - KL));
        g.line(box.x, ky1, box.x + box.w, ky1, c.line, 1);
        [1.0, 1.1, 1.2].forEach((k) => { g.line(box.x, Y(k), box.x + box.w, Y(k), c.line, 1, 0.4, [2, 5]); g.label(k.toFixed(1), box.x - 6, Y(k), { color: c.faint, size: fs - 2, align: "right" }); });
        const st = stats(), gs = Math.max(0, pw.k.length - G);
        if (st && mode === "conv") { g.area([[X(pw.inact), Y(st.m + st.se)], [box.x + box.w, Y(st.m + st.se)], [box.x + box.w, Y(st.m - st.se)], [X(pw.inact), Y(st.m - st.se)]], c.accent, 0.3); g.line(X(pw.inact), Y(st.m), box.x + box.w, Y(st.m), c.accent, 1.6); }
        pw.k.forEach((k, i) => { if (i < gs) return; g.dot(X(i - gs + 1), Y(k), phone ? 2 : 2.6, i < pw.inact ? c.soft : c.ink, 0.85); });
        g.label("k per generation", box.x, ky0 - 12, { color: c.soft, size: fs - 1, align: "left" });
        if (mode === "power") {
          const last = pw.k[pw.k.length - 1]; g.label(last ? `generation ${pw.gen}: k = ${last.toFixed(3)} · H = ${pw.Hs[pw.Hs.length - 1].toFixed(2)} bits` : "starting…", W / 2, yRd, rd);
        } else g.label(st ? `k_eff = ${st.m.toFixed(4)} ± ${st.se.toFixed(4)} (${st.n} × ${pw.N} histories) · diffusion 1.120` : `${pw.gen} generations, averaging starts after ${pw.inact}`, W / 2, yRd, rd);
      }
      g.label("illustrative one-group data", W - 6, H - 10, { color: c.faint, size: 10, align: "right" });
    },
  });
})();
