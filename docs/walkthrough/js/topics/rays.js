/* Alpha, beta, gamma and neutrons. Scenes (S.mode):
 *   "lanes" = four beams (alpha ~5 MeV, e.g. Am-241; beta from Sr-90/Y-90, up to 2.28 MeV; gamma 662 keV from Cs-137; fast
 *             neutrons ~2 MeV) against a stack of shields. Lane thicknesses: paper 0.1 mm, aluminium 5 mm, lead 5 cm, water 50 cm.
 *             Chance to get through each layer (TR below): alpha stops in any of them (range ~40 um in tissue/water); beta:
 *             ~85 % through paper, none through 5 mm Al (1.35 g/cm2 > max range ~1.1 g/cm2), none through lead or water;
 *             gamma: narrow-beam exp(-mu x) with NIST XCOM mu/rho at 662 keV: Al 0.0750, Pb 0.1136, water 0.0862 cm2/g
 *             (Al 5 mm 0.90, Pb 5 cm 0.0016, water 50 cm 0.013); neutrons: exp(-Sigma_R x) with fast-neutron removal cross sections
 *             (Al 0.079, Pb 0.116, water 0.103 /cm; Glasstone & Sesonske): Al 5 mm 0.96, Pb 5 cm 0.56, water 50 cm 0.006. Distances in the drawing are not to scale.
 *   "gamma" = 662 keV photons into lead, mu = 1.29 /cm (half-value layer 5.4 mm): each photon's depth of first interaction is
 *             drawn from exp(-mu x); about half of the interacting ones are shown scattering off (Compton), the rest absorbed.
 *   "neut"  = 2D Monte Carlo of fast neutrons (2 MeV) in a slab, mirrored top and bottom (an infinite slab). Lead: mean free
 *             path 5.8 cm (sigma_tot ~5.3 b), energy loss per collision at most 1.9 % (A = 207). Water: mean free path from
 *             ~2.5 cm (2 MeV) to ~0.7 cm (eV-keV) to 0.3 cm (thermal); hydrogen (half the collisions when fast, 90 % when slow)
 *             takes a uniform share of the energy and sends it forward (cos theta = sqrt(E'/E)); oxygen at most 22 %.
 *             Thermal neutrons are absorbed with chance 0.65 % per collision (Sigma_a/Sigma_s of water, 0.022/3.45). Mean free paths and
 *             angles are simplified, so the percentages shown are those of this simplified model.
 * Sources: NIST XCOM photon cross sections; ICRU 49 (alpha ranges); Katz-Penfold beta range; ENDF/B-VIII total cross sections. */
(function () {
  const { TAU, clamp, lerp, smooth, rng } = WT.util;
  const RAD = ["alpha", "beta", "gamma", "neutron"];
  const MAT = {
    paper: { lab: "paper", labP: "paper", w: 8, col: "warm" },
    al: { lab: "aluminium 5 mm", labP: "Al 5 mm", w: 20, col: "soft" },
    pb: { lab: "lead 5 cm", labP: "lead 5 cm", w: 40, col: "ink" },
    water: { lab: "water 50 cm", labP: "water 50 cm", w: 66, col: "cool" },
  };
  const TR = { // chance to get through one layer, per radiation [alpha, beta, gamma, neutron]
    paper: [0, 0.85, 0.999, 1], al: [0, 0, 0.904, 0.96], pb: [0, 0, 0.00158, 0.56], water: [0, 0, 0.0134, 0.006],
  };
  const MU_PB = 0.1136 * 11.35, HVL = Math.LN2 / MU_PB; // per cm, cm
  const r = rng(77);
  const press = (sel, on) => document.querySelectorAll(`#rays [data-act^="${sel}"]`).forEach((b) => b.setAttribute("aria-pressed", String(on.includes(b.dataset.act))));
  function fmtP(p) {
    if (p <= 0) return "stopped";
    if (p > 0.985) return "all through";
    if (p >= 0.1) return `${Math.round(p * 100)} % through`;
    const n = 1 / p; const s = n < 1000 ? String(Math.round(n / (n < 100 ? 1 : 10)) * (n < 100 ? 1 : 10)) : n < 1e6 ? `${Math.round(n / 1000)},000` : n < 1e9 ? `${(n / 1e6).toFixed(n < 1e7 ? 1 : 0)} million` : "a billion";
    return `1 in ${s}`;
  }


  // ---------- a lit, solid-looking slab of material ----------
  const NOISE = []; { const q = rng(9); for (let i = 0; i < 90; i++) NOISE.push([q(), q(), q()]); }
  function slab(g, x0, x1, y0, y1, m, t) {
    const { ctx, c } = g, w = Math.max(1.5, x1 - x0), h = y1 - y0;
    const base = m === "water" ? c.cool : m === "paper" ? c.warm : c.faint;
    ctx.save();
    let gr = ctx.createLinearGradient(x0, 0, x1, 0);
    if (m === "water") { gr.addColorStop(0, g.rgba(base, 0.42)); gr.addColorStop(1, g.rgba(base, 0.22)); }
    else if (m === "paper") { gr.addColorStop(0, g.rgba("#ffffff", 0.85)); gr.addColorStop(1, g.rgba(base, 0.55)); }
    else { gr.addColorStop(0, g.rgba(base, m === "pb" ? 0.95 : 0.7)); gr.addColorStop(0.18, g.rgba("#ffffff", m === "pb" ? 0.25 : 0.45)); gr.addColorStop(0.35, g.rgba(base, m === "pb" ? 0.9 : 0.65)); gr.addColorStop(1, g.rgba("#000000", m === "pb" ? 0.45 : 0.25)); }
    ctx.fillStyle = gr; ctx.fillRect(x0, y0, w, h);
    if (m === "pb") { ctx.fillStyle = g.rgba(base, 0.9); ctx.globalAlpha = 0.6; ctx.fillRect(x0, y0, w, h); ctx.globalAlpha = 1; ctx.fillStyle = gr; ctx.fillRect(x0, y0, w, h); }
    ctx.beginPath(); ctx.rect(x0, y0, w, h); ctx.clip();
    if (m === "water") { // drifting caustic ripples
      ctx.strokeStyle = g.rgba("#ffffff", 0.22); ctx.lineWidth = 1;
      for (let i = 0; i < 9; i++) { ctx.beginPath(); for (let k = 0; k <= 12; k++) { const yy = y0 + h * (i + 0.5) / 9 + Math.sin(k * 0.9 + t * 1.3 + i) * 4, xx = x0 + w * k / 12; k ? ctx.lineTo(xx, yy) : ctx.moveTo(xx, yy); } ctx.stroke(); }
    } else if (m === "al") { ctx.strokeStyle = g.rgba("#ffffff", 0.18); ctx.lineWidth = 1; for (let i = 0; i < h; i += 5) { ctx.beginPath(); ctx.moveTo(x0, y0 + i); ctx.lineTo(x1, y0 + i + 1); ctx.stroke(); } }
    else if (m === "pb") { for (const [a, b, q] of NOISE) { ctx.fillStyle = g.rgba(q > 0.5 ? "#ffffff" : "#000000", 0.12); ctx.fillRect(x0 + a * w, y0 + b * h, 2, 2); } }
    ctx.restore();
    g.line(x0, y0, x0, y1, "#ffffff", 1.2, m === "water" ? 0.35 : 0.55); g.line(x0, y0, x1, y0, "#ffffff", 1, 0.4); g.line(x1, y0, x1, y1, "#000000", 1, 0.25);
  }
  const sparks = [];
  function spark(x, y, col, n, t) { for (let i = 0; i < n; i++) { const a = Math.PI + (r() - 0.5) * 2.4, v = 60 + 120 * r(); sparks.push({ x, y, vx: Math.cos(a) * v, vy: Math.sin(a) * v, col, t }); } while (sparks.length > 160) sparks.shift(); }
  function drawSparks(g, t, dt) { for (let i = sparks.length - 1; i >= 0; i--) { const p = sparks[i], a = t - p.t; if (a > 0.55) { sparks.splice(i, 1); continue; } p.x += p.vx * dt; p.y += p.vy * dt; p.vy += 260 * dt; g.dot(p.x, p.y, 1.8, p.col, 1 - a / 0.55); g.glow(p.x, p.y, 5, p.col, 0.5 * (1 - a / 0.55)); } }

  function handle(g, x, cy, bh, S, fs) {
    const c = g.c, pulse = 0.5 + 0.5 * Math.sin(S.time * 3);
    g.glow(x, cy, 22 + 4 * pulse, c.accent, 0.35 + 0.15 * pulse); g.line(x, cy - 16, x, cy + 16, c.accent, 4, 0.9);
    g.label("drag ↔", x + 10, cy + bh / 2 + 14, { color: c.accent, size: fs - 1, weight: 600, align: "left" });
  }
  function attachGrab(S, cv) {
    const near = (x, y) => S._h && S.mode !== "lanes" && Math.abs(x - S._h.x) < 22 && y > S._h.y0 - 10 && y < S._h.y1 + 24;
    const set = (x) => { const h = S._h; let v = clamp((x - h.L) / h.k, 0, h.max); v = h.key === "pb" ? Math.round(v * 10) / 10 : Math.round(v); S.set(h.key, v); };
    WT.grab(cv, {
      down: (x, y) => { if (!near(x, y)) return false; set(x); return true; },
      move: (x) => set(x),
      up: () => { const h = S._h; document.querySelectorAll(`#rays [data-bind=${h.key}]`).forEach((el) => (el.value = S[h.key])); },
      hover: (x, y) => { cv.style.cursor = near(x, y) ? "ew-resize" : ""; },
    });
  }
  // ---------- lanes ----------
  const lp = []; let lastEmit = [0, 0, 0, 0];
  // ---------- gamma into lead ----------
  const gp = [], gHist = [];
  // ---------- neutrons in a slab ----------
  const np = [], nHist = [], nh = []; // neutrons, outcomes, collision flashes
  const mfpW = (E) => (E < 0.1 ? 0.3 : E < 1 ? lerp(0.3, 0.68, Math.log10(E / 0.1)) : E < 1e4 ? 0.68 : lerp(0.68, 2.5, clamp((Math.log10(E) - 4) / 2.3, 0, 1)));
  const nSpeed = (E) => 45 + 230 * clamp((Math.log10(Math.max(E, 0.025)) + 1.6) / 7.9, 0, 1);
  function nNew(S) { np.push({ x: -1, y: (r() - 0.5) * 0.6, dx: 1, dy: 0, E: 2e6, st: "in", seg: 0, tr: [], hits: 0, t: S.time }); }
  function nCollide(p, S) {
    const mat = S.nmat;
    if (mat === "pb") { p.E *= 1 - 0.019 * r(); const a = r() * TAU; p.dx = Math.cos(a); p.dy = Math.sin(a); return Math.max(0.05, -Math.log(1 - r()) * 5.8); }
    if (p.E < 0.1) { if (r() < 0.0065) { p.st = "abs"; p.t = S.time; return 0; } const a = r() * TAU; p.dx = Math.cos(a); p.dy = Math.sin(a); return Math.max(0.02, -Math.log(1 - r()) * mfpW(p.E)); }
    const pH = p.E > 1e4 ? 0.55 : 0.9;
    p.H = r() < pH; if (p.H) { const u = r(), E2 = Math.max(0.025, p.E * u), ct = Math.sqrt(Math.min(1, E2 / p.E)), th = Math.acos(ct) * (r() < 0.5 ? -1 : 1), a = Math.atan2(p.dy, p.dx) + th; p.dx = Math.cos(a); p.dy = Math.sin(a); p.E = E2; }
    else { p.E = Math.max(0.025, p.E * (0.7785 + 0.2215 * r())); const a = r() * TAU; p.dx = Math.cos(a); p.dy = Math.sin(a); }
    return Math.max(0.02, -Math.log(1 - r()) * mfpW(p.E));
  }
  // advance one neutron by a screen distance d (pixels), k = px per cm, Th = slab thickness (cm), YB = half-height (cm)
  function nMove(p, S, dpx, k, Th, YB) {
    let guard = 0;
    while (dpx > 0 && guard++ < 40) {
      if (p.st === "abs") return;
      if (p.st === "in") { // flying towards the slab face at x = 0
        const need = (0 - p.x) * k; if (need > dpx) { p.x += dpx / k; return; } p.x = 0; dpx -= need;
        if (Th <= 0.01) { p.st = "out"; continue; }
        p.st = "slab"; p.seg = Math.max(0.05, -Math.log(1 - r()) * (S.nmat === "pb" ? 5.8 : mfpW(p.E)));
        continue;
      }
      if (p.st === "out" || p.st === "back") { p.x += p.dx * dpx / k; p.y += p.dy * dpx / k; return; }
      // inside the slab: travel along the current free path, stop at faces
      const len = Math.min(p.seg, dpx / k);
      let nx = p.x + p.dx * len, ny = p.y + p.dy * len;
      if (nx > Th || nx < 0) {
        const xf = nx > Th ? Th : 0, s = (xf - p.x) / p.dx; p.x = xf; p.y += p.dy * s; p.st = nx > Th ? "out" : "back"; p.t = S.time;
        nHist.push(p.st); if (nHist.length > 120) nHist.shift(); dpx -= s * k; continue;
      }
      if (ny > YB) { ny = 2 * YB - ny; p.dy = -p.dy; } else if (ny < -YB) { ny = -2 * YB - ny; p.dy = -p.dy; }
      p.x = nx; p.y = ny; p.seg -= len; dpx -= len * k;
      if (p.seg <= 1e-6) {
        p.tr.push([p.x, p.y]); if (p.tr.length > 14) p.tr.shift(); p.hits++;
        p.H = false; p.seg = nCollide(p, S); nh.push([p.x, p.y, S.time, p.H ? p.dx : 0, p.H ? p.dy : 0]); if (nh.length > 120) nh.shift(); if (p.st === "abs") { nHist.push("abs"); if (nHist.length > 120) nHist.shift(); return; }
      }
    }
  }

  WT.chapter("rays", {
    level: 0, num: "Lesson 2", title: "Alpha, beta, gamma and neutrons", short: "Radiation",
    html: `
<div class="step">
  <h3>Four kinds of radiation</h3>
  <p><em class="a">Alpha</em> is a heavy clump of two protons and two neutrons. <b>Beta</b> is a fast electron. <em class="g">Gamma</em> is light, far too energetic to see. <em class="n">Neutrons</em> carry no charge at all. Each one gets stopped by different things.</p>
</div>
<div class="step">
  <h3>Paper and aluminium</h3>
  <p>Alpha particles are big and charged, so they crash into atoms at once: a sheet of paper stops them. Beta electrons go further, but a few millimetres of aluminium stop them too.</p>
  <div class="btns"><button class="btn ghost" data-act="sh_paper" aria-pressed="true">Paper</button><button class="btn ghost" data-act="sh_al" aria-pressed="false">Aluminium</button></div>
</div>
<div class="step">
  <h3>Gamma rays: halved, never zero</h3>
  <p>Gamma rays have no charge and usually pass atoms by. Each centimetre of lead gives every one the same chance to be caught, so each slice halves what is left. The beam fades but never quite reaches zero.</p>
  <div class="ctl"><label for="ry-pb">Lead (cm)</label><input id="ry-pb" type="range" data-bind="pb" data-instant min="0" max="5" step="0.1" value="1"><output data-show="pb" data-fmt="1"></output></div>
</div>
<div class="step">
  <h3>Neutrons: lead is not enough</h3>
  <p>A neutron bouncing off a heavy lead nucleus is a ping-pong ball hitting a bowling ball: it keeps its speed. Hydrogen in water weighs the same as a neutron, so every hit slows it, until it is slow enough to be swallowed.</p>
  <div class="btns"><button class="btn ghost" data-act="nm_pb" aria-pressed="true">Lead</button><button class="btn ghost" data-act="nm_water" aria-pressed="false">Water</button></div>
  <div class="ctl"><label for="ry-nx">Thickness (cm)</label><input id="ry-nx" type="range" data-bind="nx" data-instant min="0" max="60" step="1" value="30"><output data-show="nx" data-fmt="0"></output></div>
</div>
<div class="step">
  <h3>Build a shield</h3>
  <p>Stack up layers until all four beams are stopped. Gamma rays never drop to exactly zero, only to a tiny share.</p>
  <div class="btns"><button class="btn ghost" data-act="add_paper">+ Paper</button><button class="btn ghost" data-act="add_al">+ Aluminium</button><button class="btn ghost" data-act="add_pb">+ Lead</button><button class="btn ghost" data-act="add_water">+ Water</button><button class="btn" data-act="clear">Clear</button></div>
</div>`,
    setup(S) {
      S.set("mode", "lanes"); S.layers = []; S.set("pb", 1); S.set("nx", 30); S.nmat = "pb";
      ["paper", "al"].forEach((m) => S.on("sh_" + m, () => { S.layers = [m]; press("sh_", ["sh_" + m]); lp.length = 0; }));
      ["pb", "water"].forEach((m) => S.on("nm_" + m, () => { S.nmat = m; press("nm_", ["nm_" + m]); np.length = 0; nHist.length = 0; }));
      Object.keys(MAT).forEach((m) => S.on("add_" + m, () => { if (S.layers.length >= 6) S.layers.shift(); S.layers.push(m); }));
      S.on("clear", () => { S.layers = []; });
    },
    steps: [
      (S) => { S.set("mode", "lanes"); S.layers = []; },
      (S) => { S.set("mode", "lanes"); S.layers = ["paper"]; press("sh_", ["sh_paper"]); },
      (S) => { S.set("mode", "gamma"); gHist.length = 0; },
      (S) => { S.set("mode", "neut"); np.length = 0; nHist.length = 0; },
      (S) => { S.set("mode", "lanes"); S.layers = ["paper", "al"]; },
    ],
    frame(g, S, dt) {
      const { W, H, c, ctx } = g, phone = W < 600, fs = phone ? 11 : 13, snap = document.body.classList.contains("shot"), mode = S.mode;
      const RC = [c.alpha, c.accent, c.photon, c.neutron];
      if (!S._cv) { S._cv = ctx.canvas; attachGrab(S, S._cv); }
      const drawP = (k, x, y, a, al) => {
        if (k === 0) { g.glow(x, y, 14, c.alpha, 0.35 * al); g.nucleus(x, y, phone ? 6 : 8, { N: 4, Z: 2, seed: 3, jiggle: 0, alpha: al }); }
        else if (k === 1) { g.line(x - 12, y, x, y, c.accent, 2, 0.35 * al); g.dot(x, y, 3.2, c.accent, al); g.glow(x, y, 10, c.accent, 0.5 * al); }
        else if (k === 2) g.photon(x, y, a, phone ? 20 : 28, al);
        else { g.glow(x, y, 12, c.neutron, 0.35 * al); g.ball(x, y, phone ? 4.2 : 5.2, c.neutron, al); }
      };
      const SPD = [150, 380, 470, 260];

      if (mode === "lanes") {
        // ---------- four beams against a stack of layers ----------
        const top = H * (phone ? 0.17 : 0.12), bot = H * 0.86, lh = (bot - top) / 4, sx = W * (phone ? 0.1 : 0.1), ex = W * 0.97, mv = snap ? 0 : dt;
        const sc = phone ? 0.62 : 1, gap = 3; let wsum = 0; S.layers.forEach((m) => (wsum += MAT[m].w * sc + gap));
        const shL = W * 0.52 - wsum / 2, edges = []; { let x = shL; S.layers.forEach((m) => { const w = MAT[m].w * sc; edges.push([x, x + w, m]); x += w + gap; }); }
        const shR = edges.length ? edges[edges.length - 1][1] : W * 0.52;
        // layers
        edges.forEach(([a, b, m], j) => {
          slab(g, a, b, top - 6, bot - 2, m, S.time);
        });
        // layer labels (staggered so they do not collide)
        edges.forEach(([a, b, m], j) => g.label(phone ? MAT[m].labP : MAT[m].lab, (a + b) / 2, top - 16 - (j % 2) * (fs + 4), { color: c.ink, size: fs - 1, weight: 600, bg: true }));
        if (!edges.length) g.label("no shield", W * 0.52, top - 16, { color: c.soft, size: fs - 1 });
        const Ps = [0, 1, 2, 3].map((k) => S.layers.reduce((p, m) => p * TR[m][k], 1)), sealed = edges.length > 0 && Ps.every((p) => p < 0.01);
        if (sealed && !S._sealed) S._sealT = S.time; S._sealed = sealed;
        if (sealed) { const a = S.time - (S._sealT || -9), mx = (shL + shR) / 2, my = (top + bot) / 2;
          g.glow(mx, my, (bot - top) * 0.55, c.fission, 0.12 + 0.05 * Math.sin(S.time * 2));
          if (a < 1.4) { g.ring(mx, my, 30 + a * W * 0.5, c.fission, 4 * (1 - a / 1.4), 1 - a / 1.4); g.glow(mx, my, 60 + a * 200, "#ffffff", 0.4 * (1 - a / 1.4)); } }
        const rate = phone ? 6 : 9;
        for (let k = 0; k < 4; k++) {
          const cy = top + lh * (k + 0.5);
          let P = 1; S.layers.forEach((m) => (P *= TR[m][k]));
          // the beam: a soft ribbon that dims at each layer, with a hot spot where it is stopped
          { let I = 1, x = sx; const bh2 = lh * 0.22;
            const band = (xa, xb, v) => { if (xb <= xa || v < 0.004) return; ctx.save(); const gb = ctx.createLinearGradient(0, cy - bh2, 0, cy + bh2); gb.addColorStop(0, g.rgba(RC[k], 0)); gb.addColorStop(0.5, g.rgba(RC[k], 0.2 * Math.sqrt(v))); gb.addColorStop(1, g.rgba(RC[k], 0)); ctx.fillStyle = gb; ctx.fillRect(xa, cy - bh2, xb - xa, 2 * bh2); ctx.restore(); };
            for (const [a, b, m] of edges) { band(x, a, I); const I2 = I * TR[m][k]; if (I - I2 > 0.05) g.glow(a + 2, cy, lh * 0.32, RC[k], 0.45 * (I - I2) * (0.85 + 0.15 * Math.sin(S.time * 9 + k))); I = I2; x = b; }
            band(x, ex, I); }
          // source
          g.glow(sx, cy, Math.min(lh * 0.4, sx - 2), RC[k], 0.4); g.ball(sx, cy, phone ? 6 : 8, RC[k]);
          g.label(RAD[k], sx + (phone ? 12 : 16), cy - lh * 0.32, { color: RC[k], size: fs, weight: 700, align: "left" });
          // detector
          g.line(ex, cy - lh * 0.32, ex, cy + lh * 0.32, c.soft, 3, 0.5);
          g.label(fmtP(P), ex - 6, cy - lh * 0.32, { color: P <= 0 ? c.soft : RC[k], size: fs - 1, weight: 600, align: "right", bg: true });
          // emit
          if (!snap && S.time - lastEmit[k] > 1 / rate * (0.6 + 0.8 * r())) {
            lastEmit[k] = S.time; let stop = Infinity;
            for (const [a, b, m] of edges) { if (r() > TR[m][k]) { stop = k < 2 ? a + (b - a) * (0.08 + 0.25 * r()) : a + (b - a) * r(); break; } }
            lp.push({ k, x: sx, y: cy + (r() - 0.5) * lh * 0.42, stop, t: -1, ph: r() * TAU });
          }
        }
        if (snap && !lp.length) { // a representative still: particles spread along each lane
          for (let k = 0; k < 4; k++) for (let i = 0; i < 9; i++) { const cy = top + lh * (k + 0.5); let stop = Infinity; for (const [a, b, m] of edges) if (r() > TR[m][k]) { stop = k < 2 ? a + (b - a) * 0.15 : a + (b - a) * r(); break; }
            const x = lerp(sx, ex, i / 9 + 0.05 * r()); if (x > stop && i % 3) continue; lp.push({ k, x: Math.min(x, stop), y: cy + (r() - 0.5) * lh * 0.42, stop, t: x > stop ? S.time - 0.2 : -1, ph: r() * TAU }); }
        }
        for (let i = lp.length - 1; i >= 0; i--) {
          const p = lp[i];
          if (p.t < 0) { p.x += SPD[p.k] * mv * (phone ? 0.7 : 1); if (p.x >= p.stop) { p.x = p.stop; p.t = S.time; spark(p.x, p.y, RC[p.k], p.k < 2 ? 7 : 4, S.time); } }
          let y = p.y; if (p.k === 3 && p.x > shL && p.stop < Infinity) y += Math.sin(p.x * 0.5 + p.ph) * 4;
          if (p.t >= 0) { const a = S.time - p.t; if (a > 0.9) { lp.splice(i, 1); continue; } g.glow(p.x, y, 10 + 18 * a, RC[p.k], 0.55 * (1 - a / 0.9)); if (a < 0.25) drawP(p.k, p.x, y, 0, 1 - a / 0.25); continue; }
          if (p.x > ex) { lp.splice(i, 1); g.glow(ex, y, 14, RC[p.k], 0.6); continue; }
          drawP(p.k, p.x, y, 0, 1);
        }
        if (sealed) g.label(phone ? "all four stopped" : "all four beams stopped", W * 0.5, H * (phone ? 0.95 : 0.935), { color: c.fission, size: fs + 2, weight: 700, serif: true });
        else if (!phone) g.label(edges.length ? "flash = stopped inside the shield" : "each source fires a steady beam", W * 0.5, H * 0.935, { color: c.ink, size: fs + 1, weight: 600, serif: true });
        else if (phone) g.label(edges.length ? "flash = stopped" : "four beams", W * 0.5, H * 0.95, { color: c.ink, size: fs, weight: 600, serif: true });
        drawSparks(g, S.time, snap ? 0 : dt);
        g.label("not to scale", W - 6, H - 10, { color: c.faint, size: 10, align: "right" });
        return;
      }

      if (mode === "gamma") {
        // ---------- gamma rays into lead ----------
        const cy = H * 0.36, bh = H * (phone ? 0.36 : 0.4), sx = W * 0.1, k = W * (phone ? 0.5 : 0.46) / 5, L = W * 0.3, Th = S.pb, Rr = L + Th * k, ex = W * 0.96;
        slab(g, L, Rr, cy - bh / 2, cy + bh / 2, "pb", S.time);
        for (let cm = 1; cm < Th; cm++) g.line(L + cm * k, cy - bh / 2, L + cm * k, cy + bh / 2, c.paper, 1, 0.3, [2, 5]);
        S._h = { x: Rr, y0: cy - bh / 2, y1: cy + bh / 2, L, k, key: "pb", max: 5 }; handle(g, Rr, cy, bh, S, fs);
        if (Th > 0.05) g.label(`lead ${Th.toFixed(1)} cm`, (L + Rr) / 2, cy - bh / 2 - 12, { color: c.ink, size: fs, weight: 600, bg: true });
        g.glow(sx, cy, Math.min(bh * 0.4, sx - 2), c.photon, 0.45); g.ball(sx, cy, 9, c.photon);
        if (!phone) g.label("gamma rays (caesium-137)", sx, cy + bh / 2 + 14, { color: c.photon, size: fs - 1, weight: 600, align: "left" });
        const emit = (x0) => { const d = -Math.log(1 - r()) / MU_PB; gp.push({ x: x0, y: cy + (r() - 0.5) * bh * 0.8, a: 0, d, stopX: d < Th ? L + d * k : Infinity, t: -1, sc: r() < 0.5 }); };
        if (snap && !gp.length) for (let i = 0; i < 70; i++) { emit(lerp(sx, ex, r())); const p = gp[gp.length - 1]; if (p.x > p.stopX) gp.pop(); }
        if (!snap) { S._ge = (S._ge || 0) + dt * (phone ? 14 : 22); while (S._ge > 1) { S._ge--; emit(sx); } }
        for (let i = gp.length - 1; i >= 0; i--) {
          const p = gp[i];
          if (p.t < 0) {
            const v = 420 * (snap ? 0 : dt); p.x += Math.cos(p.a) * v; p.y += Math.sin(p.a) * v;
            if (p.a === 0 && p.x >= p.stopX) { p.x = p.stopX; gHist.push(0); if (gHist.length > 300) gHist.shift(); if (p.sc) { p.a = (r() - 0.5) * 2.6 + (r() < 0.4 ? Math.PI : 0); p.fade = S.time; } else { p.t = S.time; spark(p.x, p.y, c.photon, 4, S.time); } }
            if (p.a === 0 && p.x > Rr && !p.cnt) { p.cnt = 1; gHist.push(1); if (gHist.length > 300) gHist.shift(); }
          }
          if (p.t >= 0) { const a = S.time - p.t; if (a > 0.5) { gp.splice(i, 1); continue; } g.glow(p.x, p.y, 6 + 16 * a, c.photon, 0.7 * (1 - a / 0.5)); continue; }
          const fa = p.fade ? 1 - (S.time - p.fade) / 0.45 : 1;
          if (fa <= 0 || p.x > W + 20 || p.x < -20 || p.y < 0 || p.y > H) { gp.splice(i, 1); continue; }
          g.photon(p.x, p.y, p.a, phone ? 16 : 22, fa * (p.fade ? 0.6 : 1));
        }
        // landscape: the share still going, along the beam (exp(-mu x), never zero)
        const yB = H * 0.86, yT = H * 0.62, pts = [], X1 = L + 5 * k;
        for (let i = 0; i <= 120; i++) { const x = 5 * i / 120; pts.push([L + x * k, lerp(yB, yT, Math.exp(-MU_PB * x))]); }
        g.line(sx, yT, L, yT, c.photon, 2, 0.8); g.clip(0, 0, W, yB); g.ground([[sx, yT], ...pts], c.photon, (yB - yT) * 0.9, 0.3); ctx.restore(); g.poly(pts, c.photon, 2.4, 0.9);
        g.line(sx, yB, X1, yB, c.line, 1);
        for (let h = 1; h <= 4; h++) { const x = L + h * HVL * k; g.line(x, yB, x, lerp(yB, yT, 0.5 ** h), c.soft, 1, 0.4, [2, 4]); g.label(["½", "¼", "⅛", "1/16"][h - 1], x + 3, lerp(yB, yT, 0.5 ** h) - 10, { color: c.ink, size: fs - 1, weight: 600, align: "left" }); }
        const xc = L + Th * k, fc = Math.exp(-MU_PB * Th); g.line(xc, yT - 4, xc, yB, c.accent, 1.5, 0.7); g.dot(xc, lerp(yB, yT, fc), 4.5, c.accent);
        [0, 1, 2, 3, 4, 5].forEach((cm) => g.label(`${cm}`, L + cm * k, yB + 12, { color: c.soft, size: fs - 2 }));
        g.label("cm of lead", X1 + 6, yB + 12, { color: c.soft, size: fs - 2, align: "left" });
        g.label("share still going", sx, yT - 12, { color: c.soft, size: fs - 1, align: "left" });
        const n = gHist.length, thr = gHist.reduce((s, v) => s + v, 0);
        g.label(phone ? `through: ${fmtP(fc).replace(" through", "")} · halved every 5.4 mm` : `gets through: ${fc >= 0.1 ? Math.round(fc * 100) + " %" : fmtP(fc)} · halved every 5.4 mm of lead`, W * 0.5, H * 0.94, { color: c.ink, size: fs + 1, weight: 600, serif: true });
        drawSparks(g, S.time, snap ? 0 : dt);
        if (n > 40 && !phone) g.label(`counted: ${thr} of ${n}`, ex, cy - bh / 2 - 12, { color: c.photon, size: fs - 1, align: "right", bg: true });
        return;
      }

      // ---------- neutrons in a slab of lead or water ----------
      const cy = H * 0.42, bh = H * (phone ? 0.62 : 0.6), L = W * (phone ? 0.2 : 0.22), k = W * (phone ? 0.56 : 0.52) / 60, Th = S.nx, Rr = L + Th * k, YB = bh / 2 / k, sx = W * 0.07;
      const water = S.nmat === "water", mc = water ? c.cool : c.ink;
      if (Th > 0) slab(g, L, Rr, cy - bh / 2, cy + bh / 2, water ? "water" : "pb", S.time);
      S._h = { x: Rr, y0: cy - bh / 2, y1: cy + bh / 2, L, k, key: "nx", max: 60 }; handle(g, Rr, cy, bh, S, fs);
      if (Th > 0) g.label(water ? `water ${Th.toFixed(0)} cm` : `lead ${Th.toFixed(0)} cm`, (L + Rr) / 2, cy - bh / 2 - 12, { color: c.ink, size: fs, weight: 600, bg: true });
      g.glow(sx, cy, Math.min(30, sx - 2), c.neutron, 0.4); g.ball(sx, cy, 7, c.neutron);
      const wkPx = (sx - L) / k; // source position in cm (negative)
      const step = (h) => {
        S._ne = (S._ne || 0) + h * 8; while (S._ne > 1 && np.length < 70) { S._ne--; nNew(S); const p = np[np.length - 1]; p.x = wkPx; }
        for (let i = np.length - 1; i >= 0; i--) {
          const p = np[i]; nMove(p, S, nSpeed(p.E) * h * (phone ? 0.75 : 1), k, Th, YB);
          if (p.st === "abs" && S.time - p.t > 0.8) np.splice(i, 1);
          else if ((p.st === "out" || p.st === "back") && (L + p.x * k > W + 10 || L + p.x * k < -10 || Math.abs(p.y) > YB * 1.6)) np.splice(i, 1);
        }
      };
      if (snap && !S._nwarm) { S._nwarm = 1; for (let i = 0; i < 450; i++) { S.time += 1 / 30; step(1 / 30); } }
      if (!snap) step(dt);
      for (const [hx, hy, ht, ux, uy] of nh) { const a = S.time - ht; if (a > 0.5) continue; const X = L + hx * k, Y = cy + hy * k; g.glow(X, Y, 7 + a * 14, "#ffffff", 0.45 * (1 - a / 0.5)); if (ux || uy) g.ball(X + uy * a * 40, Y - ux * a * 40, 2.6, c.proton, 1 - a / 0.5); }
      for (const p of np) {
        const X = L + p.x * k, Y = cy + p.y * k, slow = clamp((Math.log10(p.E) + 1.6) / 7.9, 0, 1);
        if (p.tr.length > 1) g.poly(p.tr.map(([x, y]) => [L + x * k, cy + y * k]).concat([[X, Y]]), c.neutron, 1.2, 0.4);
        if (p.st === "abs") { const a = S.time - p.t; g.glow(X, Y, 6 + 20 * a, c.fission, 0.8 * (1 - a / 0.8)); continue; }
        g.glow(X, Y, 6 + 8 * slow, c.neutron, 0.25 + 0.3 * slow); g.ball(X, Y, 2.4 + 1.8 * slow, slow > 0.15 ? c.neutron : c.cool, 0.95);
      }
      const n = nHist.length, cnt = (s) => nHist.filter((v) => v === s).length;
      const pc = (s) => (n ? Math.round(100 * cnt(s) / n) : 0);
      if (n >= 15) {
        const s = phone ? `through ${pc("out")} % · back ${pc("back")} % · caught ${pc("abs")} %` : `got through ${pc("out")} % · bounced back ${pc("back")} % · slowed and caught ${pc("abs")} %`;
        g.label(s, W * 0.5, H * 0.86, { color: c.ink, size: fs + 1, weight: 600, serif: true });
      }
      g.label(phone ? "bright = fast · dim = slowed" : "bright = fast neutron · red = hydrogen nucleus knocked away · green flash = swallowed", W * 0.5, H * 0.93, { color: c.soft, size: fs - 1 });
      drawSparks(g, S.time, snap ? 0 : dt);
      g.label("simplified model", W - 6, H - 10, { color: c.faint, size: 10, align: "right" });
    },
  });
})();
