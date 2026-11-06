/* Critical size and leakage. Scenes (S.mode):
 *   "walk"  = neutrons random-walking in a tall cylindrical core seen end-on (width = diameter). 3D isotropic flights with
 *             exponential lengths (mean free path lambda = 1.64 cm), absorption chance 1.5 % per collision, so the diffusion
 *             area L^2 = lambda^2 / (3 p_a) = 60 cm^2 (the walk is a stand-in tuned to M^2 = 60 cm^2). Births sampled from the
 *             fundamental mode J0(2.405 r/R). Measured leakage is compared with one-group diffusion,
 *             P_leak = M^2 B^2 / (1 + M^2 B^2), B = 2.405 / (R + 0.71 lambda) (extrapolated edge).
 *   "shape" = fundamental flux shapes of bare cores from -D lap(phi) + Sigma_a phi = (nu Sigma_f / k) phi:
 *             slab cos(pi x / a), B^2 = (pi/a)^2; sphere sin(pi r/R)/(pi r/R), B^2 = (pi/R)^2;
 *             cylinder (height = diameter) J0(2.405 r/R) cos(pi z/H), B^2 = (2.405/R)^2 + (pi/H)^2.
 *   "crit"  = k_eff = k_inf / (1 + M^2 B^2) against core width; critical when B^2 = B_m^2 = (k_inf - 1)/M^2.
 *             Extrapolation distances (~0.7 lambda_tr, about 1 cm in water-moderated cores) neglected in these two scenes.
 *   "refl"  = slab core with an infinitely thick water reflector, one-group: core cos(B x), reflector exp(-|x - a/2|/L_r);
 *             equal D in core and reflector gives B tan(B a/2) = 1/L_r; reflector savings delta = atan(B L_r)/B.
 * Numbers: M^2 = 60 cm^2 (migration area of a light-water-reactor lattice, typical: L^2 ~ 2-3 cm^2 plus Fermi age ~ 50 cm^2);
 * L_r = 5.9 cm (water: L^2 = 8.1 cm^2, Fermi age 27 cm^2, M = 5.9 cm). k_inf = 1.20 is illustrative (fresh-fuel order);
 * with it B_m^2 = 3.33e-3 cm^-2 and critical widths of 54 cm (slab), 109 cm (sphere), 99 cm (cylinder). Real power reactors
 * are far bigger than critical because of poisons, burnup reserve and power density. */
(function () {
  const { TAU, clamp, lerp, smooth, rng } = WT.util;
  const KINF = 1.2, M2 = 60, LR = 5.9, BM2 = (KINF - 1) / M2, BM = Math.sqrt(BM2);
  const PA = 0.015, LAM = Math.sqrt(3 * PA * M2), WMAX = 200;
  const r = rng(17);
  function J0(x) { // Abramowitz & Stegun 9.4.1 / 9.4.3
    const ax = Math.abs(x); if (ax < 3) { const y = (x / 3) ** 2; return 1 - 2.2499997 * y + 1.2656208 * y * y - 0.3163866 * y ** 3 + 0.0444479 * y ** 4 - 0.0039444 * y ** 5 + 0.00021 * y ** 6; }
    const y = 3 / ax, f = 0.79788456 - 0.00000077 * y - 0.0055274 * y * y - 0.00009512 * y ** 3 + 0.00137237 * y ** 4 - 0.00072805 * y ** 5 + 0.00014476 * y ** 6;
    const th = ax - 0.78539816 - 0.04166397 * y - 0.00003954 * y * y + 0.00262573 * y ** 3 - 0.00054125 * y ** 4 - 0.00029333 * y ** 5 + 0.00013558 * y ** 6; return f * Math.cos(th) / Math.sqrt(ax);
  }
  const GEO = ["slab", "sphere", "cylinder"];
  const B2of = (geo, w) => (geo === 0 ? (Math.PI / w) ** 2 : geo === 1 ? (Math.PI / (w / 2)) ** 2 : (2.405 / (w / 2)) ** 2 + (Math.PI / w) ** 2);
  const keff = (B2) => KINF / (1 + M2 * B2);
  const wCrit = (geo) => (geo === 0 ? Math.PI / BM : geo === 1 ? 2 * Math.PI / BM : Math.sqrt((4 * 2.405 ** 2 + Math.PI ** 2) / BM2));
  /** reflected slab of width a: fundamental B from B tan(B a/2) = 1/L_r */
  function reflB(a) { let lo = 1e-6, hi = Math.PI / a - 1e-9; for (let i = 0; i < 60; i++) { const m = (lo + hi) / 2; if (m * Math.tan(m * a / 2) < 1 / LR) lo = m; else hi = m; } return (lo + hi) / 2; }
  const wCritRefl = 2 * Math.atan(1 / (BM * LR)) / BM, DELTA = Math.atan(BM * LR) / BM;
  /** flux at (u, v) in cm from the centre (u across, v up) for the current geometry; 0 outside */
  function phiAt(geo, w, u, v, refl) {
    const h = w / 2;
    if (geo === 0) { if (refl) { const B = reflB(w), e = Math.cos(B * h); return Math.abs(u) <= h ? Math.cos(B * u) : e * Math.exp(-(Math.abs(u) - h) / LR); } return Math.abs(u) <= h ? Math.cos(Math.PI * u / w) : 0; }
    if (geo === 1) { const q = Math.hypot(u, v); if (q > h) return 0; const z = Math.PI * q / h; return z < 1e-6 ? 1 : Math.sin(z) / z; }
    if (Math.abs(u) > h || Math.abs(v) > h) return 0; return Math.max(0, J0(2.405 * u / h)) * Math.cos(Math.PI * v / w);
  }
  // ---------- flux picture, rendered small and scaled up ----------
  const OFF = document.createElement("canvas"), OX = OFF.getContext("2d"), NP = 120; OFF.width = NP; OFF.height = NP; let offKey = "";
  function heat(g, geo, w, refl, cx, cy, sc, span, clipBox) {
    const key = [geo, w.toFixed(1), refl, span.toFixed(1), g.c.warm].join();
    if (key !== offKey) {
      offKey = key; const img = OX.createImageData(NP, NP), [R, G, B] = WT.rgb01(g.c.warm).map((x) => Math.round(255 * x));
      for (let j = 0; j < NP; j++) for (let i = 0; i < NP; i++) {
        const u = (i + 0.5 - NP / 2) / NP * span, v = (NP / 2 - j - 0.5) / NP * span, p = phiAt(geo, w, u, v, refl), k = 4 * (j * NP + i);
        img.data[k] = R; img.data[k + 1] = G; img.data[k + 2] = B; img.data[k + 3] = Math.round(235 * clamp(p, 0, 1) ** 0.9);
      }
      OX.putImageData(img, 0, 0);
    }
    const s = span * sc; g.clip(clipBox.x, clipBox.y, clipBox.w, clipBox.h); g.ctx.imageSmoothingEnabled = true; g.ctx.drawImage(OFF, cx - s / 2, cy - s / 2, s, s); g.ctx.restore();
  }
  function outline(g, geo, w, cx, cy, sc, refl, hy) {
    const { c, ctx } = g, h = w / 2 * sc;
    if (geo === 0) {
      if (refl) { const rw = 26 * sc; [[-1], [1]].forEach(([s]) => { const x0 = s < 0 ? cx - h - rw : cx + h; ctx.save(); const gr = ctx.createLinearGradient(0, cy - hy, 0, cy + hy); gr.addColorStop(0, g.rgba(c.cool, 0)); gr.addColorStop(0.2, g.rgba(c.cool, 0.2)); gr.addColorStop(0.8, g.rgba(c.cool, 0.2)); gr.addColorStop(1, g.rgba(c.cool, 0)); ctx.fillStyle = gr; ctx.fillRect(x0, cy - hy, rw, 2 * hy); ctx.restore(); }); }
      [-h, h].forEach((d) => g.line(cx + d, cy - hy, cx + d, cy + hy, c.warm, 1.5, 0.8));
    } else if (geo === 1) { g.ring(cx, cy, h, c.warm, 1.6, 0.85); }
    else { ctx.save(); ctx.strokeStyle = g.rgba(c.warm, 0.85); ctx.lineWidth = 1.5; ctx.strokeRect(cx - h, cy - h, 2 * h, 2 * h); ctx.beginPath(); ctx.ellipse(cx, cy - h, h, h * 0.16, 0, 0, TAU); ctx.stroke(); ctx.restore(); }
  }
  // ---------- random walkers ----------
  const NW = 70, walkers = [], tally = { leak: 0, abs: 0, w: -1 };
  /** silent histories for the leak tally (same walk, no drawing) */
  function warm(w, n) { const R = w / 2; for (let k = 0; k < n; k++) { const b = born(w); let x = b.x, y = b.y; for (;;) { const mu = 2 * r() - 1, ph = TAU * r(), s = -LAM * Math.log(1 - r()), st = Math.sqrt(1 - mu * mu); x += s * st * Math.cos(ph); y += s * st * Math.sin(ph); if (x * x + y * y > R * R) { tally.leak++; break; } if (r() < PA) { tally.abs++; break; } } } }
  function born(w) { const R = w / 2; let q; do q = R * Math.sqrt(r()); while (r() > J0(2.405 * q / R)); const a = r() * TAU; return { x: q * Math.cos(a), y: q * Math.sin(a), tx: 0, ty: 0, f: 1, tr: [], out: false, dead: -1 }; }
  function nextFlight(n) { const mu = 2 * r() - 1, ph = TAU * r(), s = -LAM * Math.log(1 - r()), st = Math.sqrt(1 - mu * mu); n.sx = n.x; n.sy = n.y; n.tx = n.x + s * st * Math.cos(ph); n.ty = n.y + s * st * Math.sin(ph); n.f = 0; }
  // ---------- direct manipulation: drag the core edge (ratio drag, since the drawing rescales with the core) ----------
  const LAY = { used: false, drag: false };
  const rim = []; // where neutrons left the core: { a, t }
  const GRAB = {
    down(x, y) { const S = LAY.S; if (!S || !LAY.cx) return false; const d = LAY.geo === 0 || LAY.mode !== "walk" && LAY.geo !== 1 ? Math.abs(x - LAY.cx) : Math.hypot(x - LAY.cx, y - LAY.cy);
      if (Math.abs(d - LAY.edge) > 26 || (LAY.inY && (y < LAY.inY[0] || y > LAY.inY[1]))) return false;
      LAY.drag = true; LAY.used = true; LAY.d0 = Math.max(8, d); LAY.w0 = S.w; return true; },
    move(x, y) { const S = LAY.S; if (!LAY.drag || !S) return; const d = LAY.geo === 0 || LAY.mode !== "walk" && LAY.geo !== 1 ? Math.abs(x - LAY.cx) : Math.hypot(x - LAY.cx, y - LAY.cy);
      const v = Math.round(clamp(LAY.w0 * d / LAY.d0, 20, LAY.mode === "refl" ? 120 : 200)); S.set("w", v); ["df-w0", "df-w1", "df-w2", "df-w3"].forEach((id) => { const el = document.getElementById(id); if (el) el.value = v; }); },
    up() { LAY.drag = false; }, cancel() { LAY.drag = false; },
    hover(x, y, e) { if (!LAY.cx) return; const d = LAY.geo === 0 || LAY.mode !== "walk" && LAY.geo !== 1 ? Math.abs(x - LAY.cx) : Math.hypot(x - LAY.cx, y - LAY.cy); e.target.style.cursor = Math.abs(d - LAY.edge) < 26 && (!LAY.inY || (y >= LAY.inY[0] && y <= LAY.inY[1])) ? "ew-resize" : ""; },
  };
  function handle(g, x, y, S, fs, label) { const { c } = g; g.glow(x, y, 16 + 3 * Math.sin(S.time * 3), c.accent, LAY.drag ? 0.7 : 0.45); g.dot(x, y, 5.5, c.accent); g.line(x - 2, y - 3, x - 2, y + 3, c.paper, 1.2); g.line(x + 2, y - 3, x + 2, y + 3, c.paper, 1.2);
    if (!LAY.used && label) g.label("drag the edge", x + 12, y - 16, { color: c.accent, size: fs - 2, weight: 600, align: "left", bg: true }); }
  // a few dozen neutrons scattered with density ~ flux, re-sampled when the shape changes
  const AMB = []; let ambKey = "";
  function ambient(g, S, geo, w, refl, cx, cy, sc, span, hy) {
    const key = [geo, Math.round(w), refl].join(); if (key !== ambKey) { ambKey = key; AMB.length = 0; const q = rng(3);
      for (let k = 0; k < 4000 && AMB.length < 90; k++) { const u = (q() - 0.5) * span, v = geo === 0 ? (q() - 0.5) * 2 * hy / sc : (q() - 0.5) * span; if (q() < phiAt(geo, w, u, v, refl)) AMB.push([u, v, q() * TAU, 0.5 + q()]); } }
    for (const [u, v, ph, sp] of AMB) { const x = cx + u * sc + 4 * Math.sin(S.time * 1.7 * sp + ph), y = cy + v * sc + 4 * Math.cos(S.time * 1.3 * sp + ph * 2), tw = 0.55 + 0.45 * Math.sin(S.time * 3 * sp + ph);
      g.glow(x, y, 7, g.c.neutron, 0.25 * tw); g.ball(x, y, 2.6, g.c.neutron, 0.6 + 0.4 * tw); }
  }
  const btns = (geo) => ["dfslab", "dfsph", "dfcyl"].forEach((a, i) => document.querySelectorAll(`#diffusion [data-act="${a}"]`).forEach((b) => b.setAttribute("aria-pressed", String(i === geo))));

  WT.chapter("diffusion", {
    level: 2, num: "Lesson 1", title: "Critical size and leakage", short: "Critical size",
    html: `
<div class="step">
  <h3>Neutrons wander, some leak</h3>
  <p>A neutron zigzags from collision to collision until something absorbs it. Born near the edge, it may wander out and be lost. A bigger core has less surface for its volume, so a smaller share leaks.</p>
  <div class="ctl"><label for="df-w0">Core width (cm)</label><input id="df-w0" type="range" data-bind="w" data-instant min="20" max="200" step="2" value="60"><output data-show="w" data-fmt="0"></output></div>
</div>
<div class="step">
  <h3>The shape of the flux</h3>
  <p>The neutron population settles into one shape that falls to about zero at the edge: a cosine across a slab, sin(<i>r</i>)/<i>r</i> in a sphere, a Bessel function times a cosine in a cylinder. How sharply it must bend is the <b>geometric buckling</b> <i>B</i>².</p>
  <div class="btns"><button class="btn ghost" data-act="dfslab" aria-pressed="false">Slab</button><button class="btn ghost" data-act="dfsph" aria-pressed="true">Sphere</button><button class="btn ghost" data-act="dfcyl" aria-pressed="false">Cylinder</button></div>
  <div class="ctl"><label for="df-w1">Core width (cm)</label><input id="df-w1" type="range" data-bind="w" data-instant min="20" max="200" step="2" value="80"><output data-show="w" data-fmt="0"></output></div>
</div>
<div class="step">
  <h3>Critical size</h3>
  <p>One-group diffusion gives <i>k</i><sub>eff</sub> = <i>k</i><sub>∞</sub> / (1 + <i>M</i>²<i>B</i>²), with the migration area <i>M</i>² about 60 cm² in a water reactor. The core is critical when <i>B</i>² equals the material buckling (<i>k</i><sub>∞</sub> − 1)/<i>M</i>². Find that size.</p>
  <div class="btns"><button class="btn ghost" data-act="dfslab" aria-pressed="false">Slab</button><button class="btn ghost" data-act="dfsph" aria-pressed="true">Sphere</button><button class="btn ghost" data-act="dfcyl" aria-pressed="false">Cylinder</button></div>
  <div class="ctl"><label for="df-w2">Core width (cm)</label><input id="df-w2" type="range" data-bind="w" data-instant min="20" max="200" step="1" value="90"><output data-show="w" data-fmt="0"></output></div>
</div>
<div class="step">
  <h3>A reflector saves neutrons</h3>
  <p>Surround a slab core with water: some neutrons that leave are scattered back. The flux no longer drops to zero at the core edge, so a thinner core reaches the same <i>k</i>; the gain is the <b>reflector savings</b>, here about 6 cm per side.</p>
  <div class="btns"><button class="btn ghost" data-act="dfrefl" aria-pressed="true">Water reflector</button></div>
  <div class="ctl"><label for="df-w3">Core width (cm)</label><input id="df-w3" type="range" data-bind="w" data-instant min="20" max="120" step="1" value="44"><output data-show="w" data-fmt="0"></output></div>
</div>`,
    setup(S) {
      S.set("mode", "walk"); S.set("w", 60); S.set("geo", 1); S.set("refl", 1); S.to("rV", 1, true);
      [["dfslab", 0], ["dfsph", 1], ["dfcyl", 2]].forEach(([a, k]) => S.on(a, () => { if (S.mode === "refl") return; S.set("geo", k); btns(k); }));
      S.on("dfrefl", () => { S.set("refl", S.refl ? 0 : 1); document.querySelectorAll('#diffusion [data-act="dfrefl"]').forEach((b) => b.setAttribute("aria-pressed", String(!!S.refl))); });
    },
    steps: [
      (S) => { S.set("mode", "walk"); S.to("w", 60); },
      (S) => { S.set("mode", "shape"); S.to("w", 80); btns(S.geo); },
      (S) => { S.set("mode", "crit"); S.to("w", 90); btns(S.geo); },
      (S) => { S.set("mode", "refl"); S.to("w", 44); },
    ],
    frame(g, S, dt) {
      if (g.W < 40 || g.H < 40) return;
      if (!g.ctx.canvas._dfg) { g.ctx.canvas._dfg = 1; WT.grab(g.ctx.canvas, GRAB); }
      LAY.S = S; LAY.mode = S.mode;
      const { W, H, c } = g, phone = W < 600, fs = phone ? 11 : 13, snap = document.body.classList.contains("shot"), mode = S.mode, w = S.w;
      const rd = { color: c.ink, size: fs + 1, weight: 600, serif: true }, yRd = H * 0.93;
      if (mode === "walk") {
        const cx = W / 2, cy = H * 0.44, sc = Math.min(W * 0.86, H * 0.64) / (w + 36), R = w / 2, Rp = Math.max(2, R * sc);
        if (Math.abs(tally.w - w) > 1e-6) { tally.w = w; tally.leak = tally.abs = 0; warm(w, 3000); walkers.length = 0; }
        // the core: lit disc with fuel texture
        g.glow(cx, cy, Rp * 1.25, c.warm, 0.22);
        { const ctx = g.ctx; ctx.save(); const gr = ctx.createRadialGradient(cx, cy, 0, cx, cy, Rp); gr.addColorStop(0, g.rgba(c.warm, 0.28)); gr.addColorStop(1, g.rgba(c.warm, 0.06)); ctx.fillStyle = gr; ctx.beginPath(); ctx.arc(cx, cy, Rp, 0, TAU); ctx.fill(); ctx.restore(); }
        g.ring(cx, cy, Rp, c.warm, 1.6, 0.8);
        LAY.cx = cx; LAY.cy = cy; LAY.edge = Rp; LAY.geo = 1; LAY.inY = null;
        for (let i = rim.length - 1; i >= 0; i--) { const h = rim[i], a = S.time - h.t; if (a > 1.6) { rim.splice(i, 1); continue; } const x = cx + Math.cos(h.a) * Rp, y = cy + Math.sin(h.a) * Rp; g.glow(x, y, 10 + 26 * a, c.proton, 0.55 * (1 - a / 1.6)); }
        while (rim.length > 60) rim.shift();
        // walkers
        const steps = dt * 26; // flights per second of each walker
        while (walkers.length < NW) { const n = born(w); nextFlight(n); n.f = r(); walkers.push(n); }
        const reps = 1;
        for (let rep = 0; rep < reps; rep++) for (let i = 0; i < walkers.length; i++) {
          const n = walkers[i];
          if (n.dead >= 0) { n.dead += dt || 0.02; if (n.dead > (n.out ? 1.2 : 0.5)) walkers[i] = Object.assign(born(w), {}), nextFlight(walkers[i]); continue; }
          if (n.x * n.x + n.y * n.y > R * R * 1.02 && !n.out) { n.x = n.sx; n.y = n.sy; nextFlight(n); }
          n.f += steps; let guard = 0;
          while (n.f >= 1 && n.dead < 0 && guard++ < 20) {
            n.x = n.tx; n.y = n.ty; n.tr.push([n.x, n.y]); if (n.tr.length > 14) n.tr.shift();
            if (n.x * n.x + n.y * n.y > R * R) { n.out = true; n.dead = 0; tally.leak++; const a = Math.atan2(n.y, n.x); n.ex = Math.cos(a); n.ey = Math.sin(a); rim.push({ a, t: S.time }); break; }
            if (r() < PA) { n.dead = 0; tally.abs++; break; }
            const f = n.f - 1; nextFlight(n); n.f = f;
          }
          if (snap && rep < reps - 1) continue;
          // draw trail and head
          const hx = n.dead >= 0 ? n.x : lerp(n.sx, n.tx, clamp(n.f, 0, 1)), hy = n.dead >= 0 ? n.y : lerp(n.sy, n.ty, clamp(n.f, 0, 1));
          const pts = n.tr.map(([x, y]) => [cx + x * sc, cy + y * sc]); pts.push([cx + hx * sc, cy + hy * sc]);
          const fade = n.dead >= 0 ? clamp(1 - n.dead / (n.out ? 1.2 : 0.5), 0, 1) : 1;
          g.poly(pts, n.out ? c.proton : c.neutron, 1.4, 0.65 * fade);
          if (n.out) { const d = (Rp + 4 + 60 * n.dead); g.ball(cx + n.ex * d, cy + n.ey * d, 3, c.proton, fade); }
          else g.ball(cx + hx * sc, cy + hy * sc, n.dead >= 0 ? 2.5 : 3, c.neutron, fade);
        }
        handle(g, cx + Rp * Math.cos(-0.6), cy + Rp * Math.sin(-0.6), S, fs, true);
        // scale bar
        { const bx = W * 0.07, by = H * 0.8; g.line(bx, by, bx + 10 * sc, by, c.soft, 2); g.label("10 cm", bx + 5 * sc, by - 10, { color: c.soft, size: fs - 2 }); }
        // the theory and the walk
        const Rx = R + 0.71 * LAM, B2 = (2.405 / Rx) ** 2, pl = M2 * B2 / (1 + M2 * B2), tot = tally.leak + tally.abs, meas = tot > 20 ? tally.leak / tot : null;
        g.label(`${w.toFixed(0)} cm`, cx, cy + Rp + 14, { color: c.warm, size: fs, weight: 600, bg: true });
        g.label(phone ? "red: leaked" : "red: leaked out · blue: absorbed inside", W / 2, H * 0.06, { color: c.soft, size: fs - 1 });
        const ws = meas == null ? "…" : `${(100 * meas).toFixed(0)} %`;
        g.label(phone ? `leak: walk ${ws} · diffusion ${(100 * pl).toFixed(0)} %` : `share leaking: random walk ${ws} · diffusion theory ${(100 * pl).toFixed(0)} %`, W / 2, H * 0.86, { color: c.ink, size: fs, weight: 600 });
        g.label(`k_eff = k∞ × (1 − leak) = ${(KINF * (1 - pl)).toFixed(3)}`, W / 2, yRd, rd);
      } else {
        const refl = mode === "refl" ? S.refl : 0, geo = mode === "refl" ? 0 : S.geo;
        const top = H * 0.07, bot = H * (phone ? 0.42 : 0.44), cx = W / 2, cy = (top + bot) / 2, span = w + (mode === "refl" ? 60 : 30);
        const sc = Math.min(W * 0.9 / span, geo === 0 ? 1e9 : (bot - top - 6) / w), hy = (bot - top) / 2;
        heat(g, geo, w, refl, cx, cy, sc, Math.max(span, geo === 0 ? (bot - top) / sc : 0), { x: 0, y: top, w: W, h: bot - top }); outline(g, geo, w, cx, cy, sc, refl, hy);
        g.clip(0, top, W, bot - top); ambient(g, S, geo, w, refl, cx, cy, sc, span, hy); g.ctx.restore();
        LAY.cx = cx; LAY.cy = cy; LAY.edge = w / 2 * sc; LAY.geo = geo; LAY.inY = [top, bot];
        handle(g, cx + w / 2 * sc, geo === 0 ? cy + hy * 0.55 : cy, S, fs, true);
        if (refl) { g.label("water", cx - (w / 2 + 13) * sc, top + 10, { color: c.cool, size: fs - 1, weight: 600 }); g.label("water", cx + (w / 2 + 13) * sc, top + 10, { color: c.cool, size: fs - 1, weight: 600 }); }
        if (!phone || mode !== "crit") g.label(mode === "refl" ? "slab core" : GEO[geo], cx, top - 2 < 8 ? 10 : top - 2, { color: c.warm, size: fs - 1, weight: 600, bg: true });
        // the flux across the middle, as a landscape under the core
        const ly0 = H * 0.5, ly1 = H * 0.63, pts = [], half = span / 2;
        for (let i = 0; i <= 240; i++) { const u = -half + 2 * half * i / 240, p = phiAt(geo, w, u, 0, refl); pts.push([cx + u * sc, lerp(ly1, ly0, p)]); }
        g.line(cx - half * sc, ly1, cx + half * sc, ly1, c.line, 1);
        g.clip(0, ly0 - 4, W, ly1 - ly0 + 4); g.ground(pts, c.warm, ly1 - ly0, 0.35); g.ctx.restore(); g.poly(pts, c.warm, 2.4);
        if (refl) { const bare = []; for (let i = 0; i <= 120; i++) { const u = -w / 2 + w * i / 120; bare.push([cx + u * sc, lerp(ly1, ly0, Math.cos(Math.PI * u / w))]); } g.poly(bare, c.soft, 1.3, 0.8, [4, 4]); }
        g.label("flux across the middle", cx - half * sc, ly0 - 12, { color: c.soft, size: fs - 1, align: "left" });
        const B2 = refl ? reflB(w) ** 2 : B2of(geo, w), k = keff(B2);
        const bf = geo === 0 ? "B² = (π/a)²" : geo === 1 ? "B² = (π/R)²" : "B² = (2.405/R)² + (π/H)²";
        if (mode === "shape") {
          g.label("−D∇²φ + Σₐφ = (νΣ_f / k) φ", phone ? W / 2 : cx - half * sc, H * 0.8, { color: c.soft, size: fs, serif: true, italic: true, align: phone ? "center" : "left" });
          g.label(`${refl ? "" : bf + " = "}${(1e4 * B2).toFixed(1)} × 10⁻⁴ cm⁻²`, phone ? W / 2 : cx + half * sc, phone ? H * 0.8 + fs + 8 : H * 0.8, { color: c.accent, size: fs, weight: 600, align: phone ? "center" : "right" });
          g.label(`${GEO[geo]} ${w.toFixed(0)} cm wide · smaller core → sharper bend → larger B²`, W / 2, yRd, rd);
        } else {
          // k_eff against width: a landscape with the critical line
          const kx0 = W * (phone ? 0.12 : 0.1), kx1 = W * 0.95, ky0 = H * 0.72, ky1 = H * 0.85, wmax = mode === "refl" ? 120 : WMAX, X = (ww) => lerp(kx0, kx1, (ww - 20) / (wmax - 20)), Y = (kk) => lerp(ky1, ky0, (kk - 0.7) / (KINF - 0.7));
          const kc = (ww, rf) => keff(rf ? reflB(ww) ** 2 : B2of(geo, ww)), kp = [];
          for (let i = 0; i <= 120; i++) { const ww = 20 + (wmax - 20) * i / 120; kp.push([X(ww), Y(Math.max(0.7, kc(ww, refl)))]); }
          g.line(kx0, Y(1), kx1, Y(1), c.fission, 1, 0.8, [4, 4]); g.label("k = 1", kx0 - 4, Y(1), { color: c.fission, size: fs - 2, align: "right" });
          if (mode === "refl" && refl) { const bp = []; for (let i = 0; i <= 120; i++) { const ww = 20 + (wmax - 20) * i / 120; bp.push([X(ww), Y(Math.max(0.7, kc(ww, 0)))]); } g.poly(bp, c.soft, 1.2, 0.7, [3, 4]); }
          g.clip(0, ky0 - 10, W, ky1 - ky0 + 10); g.ground(kp, c.accent, ky1 - ky0, 0.25); g.ctx.restore(); g.poly(kp, c.accent, 2.2);
          g.dot(X(w), Y(Math.max(0.7, k)), 5, c.accent); g.glow(X(w), Y(Math.max(0.7, k)), 16, c.accent, 0.4);
          const wc = mode === "refl" ? (refl ? wCritRefl : wCrit(0)) : wCrit(geo);
          g.line(X(wc), ky0 - 4, X(wc), ky1, c.fission, 1, 0.6);
          g.label(`critical ${wc.toFixed(0)} cm`, X(wc) + 6, ky0 - 8, { color: c.fission, size: fs - 2, align: "left", bg: true });
          g.line(kx0, ky1, kx1, ky1, c.line, 1); g.label("core width →", kx1, ky1 + 12, { color: c.faint, size: fs - 2, align: "right" });
          const crit = Math.abs(k - 1) < 0.004;
          if (mode === "crit") g.label(crit ? `critical: B² = B²ₘ, k_eff = ${k.toFixed(3)}` : `k_eff = ${KINF.toFixed(2)} / (1 + 60 cm² × ${(1e4 * B2).toFixed(1)}e-4 cm⁻²) = ${k.toFixed(3)}`, W / 2, yRd, { ...rd, color: crit ? c.fission : c.ink });
          else g.label(refl ? `reflected: k_eff ${k.toFixed(3)} · bare: ${kc(w, 0).toFixed(3)} · savings ${DELTA.toFixed(1)} cm per side` : `bare: k_eff ${k.toFixed(3)} · critical at ${wCrit(0).toFixed(0)} cm`, W / 2, yRd, rd);
        }
      }
      g.label("illustration", W - 6, H - 10, { color: c.faint, size: 10, align: "right" });
    },
  });
})();
