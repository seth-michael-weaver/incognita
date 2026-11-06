/* Hero of topics.html: looking down into a reactor pool in perspective. Fuel assemblies (5 x 5 rods with guide tubes)
 * stand on the pool floor and glow Cherenkov blue, brightest in the middle of the core (a cosine-like flux shape).
 * Neutrons streak from rod to rod, slowing in the water; a fission flashes, rings out and sends 2 or 3 more, so chains
 * flare across the core and die away (multiplication just below 1). The first big chain launches the title (.hero-live,
 * same animation as the main page's hero). Click or tap near a rod, or press "Start a chain", to start one; the camera
 * drifts toward the pointer; water caustics ripple over the top. Standalone canvas loop, not a kit chapter. Illustrative. */
(function () {
  "use strict";
  const hero = document.querySelector(".tp-hero"), cv = hero && hero.querySelector(".hero-cv");
  if (!cv) return;
  const ctx = cv.getContext("2d"), copy = hero.querySelector(".hero-copy");
  const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  const shot = document.body.classList.contains("shot") || /[?&](herot=|shot=)/.test(location.search);
  const TAU = Math.PI * 2, clamp = (v, a, b) => Math.max(a, Math.min(b, v)), lerp = (a, b, s) => a + (b - a) * s;
  let seed = 11; const rnd = () => ((seed = (seed * 16807) % 2147483647) / 2147483647);
  const BLUE = "70,160,255", CYAN = "140,235,255", WHITE = "240,250,255", HOT = "255,214,150";

  // ---------- sprites ----------
  function glowSprite(rgb, size, core, mid = 0.3) {
    const c = document.createElement("canvas"); c.width = c.height = size; const x = c.getContext("2d"), r = size / 2;
    const g = x.createRadialGradient(r, r, 0, r, r, r);
    g.addColorStop(0, `rgba(${core > 0 ? WHITE : rgb},${core > 0 ? core : 0.55})`); g.addColorStop(0.15, `rgba(${rgb},0.75)`);
    g.addColorStop(0.45, `rgba(${rgb},${mid})`); g.addColorStop(1, `rgba(${rgb},0)`);
    x.fillStyle = g; x.fillRect(0, 0, size, size); return c;
  }
  const SP = { halo: glowSprite(BLUE, 96, 0, 0.18), n: glowSprite(CYAN, 48, 1, 0.35), flash: glowSprite(HOT, 160, 1, 0.35), pool: glowSprite(BLUE, 256, 0, 0.12) };

  // ---------- world: rods on the floor plane (u across, v away from the viewer), heights h up ----------
  const PER = 5, PITCH = 1, GAP = 0.6, AW = PER * PITCH + GAP, ROD_H = 2.6;
  const rods = [], frames = [];
  const RC = 3.2 * AW; // core radius (world units)
  for (let ai = -4; ai <= 4; ai++) for (let aj = -4; aj <= 4; aj++) {
    const ax = ai * AW, ay = aj * AW; if (Math.hypot(ax, ay) > RC + AW * 0.3) continue;
    frames.push([ax, ay]);
    for (let i = 0; i < PER; i++) for (let j = 0; j < PER; j++) {
      const u = ax + (i - 2) * PITCH, v = ay + (j - 2) * PITCH, guide = (i === 1 || i === 3) && (j === 1 || j === 3);
      const d = Math.hypot(u, v) / (RC + AW);
      rods.push({ u, v, guide, base: Math.max(0.05, Math.cos(Math.min(1, d) * Math.PI / 2)), flash: 0, sx: 0, sy: 0, sz: 1 });
    }
  }
  rods.sort((a, b) => b.v - a.v); // far first

  // ---------- camera ----------
  let W = 0, H = 0, dpr = 1, F = 1; const cam = { tilt: 0.95, yaw: 0, dist: 34 };
  function layout() {
    const r = cv.getBoundingClientRect(); W = r.width; H = r.height;
    dpr = Math.min(window.devicePixelRatio || 1, W < 700 ? 1.5 : 2);
    cv.width = Math.round(W * dpr); cv.height = Math.round(H * dpr); ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    F = Math.max(W, H * 1.25) * (W < 700 ? 0.72 : 0.78);
  }
  const cosT = () => Math.cos(cam.tilt), sinT = () => Math.sin(cam.tilt);
  /** world (u, v, h) -> screen [x, y, scale] */
  function P(u, v, h) {
    const cy = Math.cos(cam.yaw), sy = Math.sin(cam.yaw), uu = u * cy - v * sy, vv = u * sy + v * cy;
    const ct = cosT(), st = sinT(), y = vv * ct - h * st, z = vv * st + h * ct + cam.dist;
    const s = F / z; return [W / 2 + uu * s, H * 0.47 + y * s, s];
  }

  // ---------- neutrons and fissions ----------
  const ns = [], flashes = [];
  const K = 0.93; // neutrons per fission 2.43; each one causes a fission with chance K/2.43, so chains end by themselves
  let live = false;
  function fission(r, strong) {
    r.flash = 1; flashes.push({ u: r.u, v: r.v, t: 0, big: strong ? 1.6 : 1 });
    const n = strong ? 5 : (rnd() < 0.43 ? 3 : 2);
    for (let i = 0; i < n && ns.length < 320; i++) {
      const a = rnd() * TAU, sp = 7 + 7 * rnd();
      ns.push({ u: r.u, v: r.v, h: ROD_H * (0.3 + 0.6 * rnd()), vu: Math.cos(a) * sp, vv: Math.sin(a) * sp, life: 0, max: 0.35 + 0.8 * rnd(), tr: [] });
    }
    if (strong && !live) { live = true; setTimeout(() => hero.classList.add("hero-live"), 250); setTimeout(() => document.body.classList.add("hero-done"), 2600); }
  }
  function nearestWorld(u, v) { let best = null, bd = 1e9; for (const r of rods) { if (r.guide) continue; const d = (r.u - u) ** 2 + (r.v - v) ** 2; if (d < bd) { bd = d; best = r; } } return [best, Math.sqrt(bd)]; }
  function nearestScreen(x, y) { let best = null, bd = 1e9; for (const r of rods) { if (r.guide) continue; const d = (r.sx - x) ** 2 + (r.sy - y) ** 2; if (d < bd) { bd = d; best = r; } } return best; }
  function startChain(x, y) {
    let r = null;
    if (x == null) { const c = rods.filter((q) => !q.guide && q.base > 0.8); r = c[Math.floor(rnd() * c.length)]; }
    else r = nearestScreen(x, y);
    if (r) fission(r, true);
  }

  // ---------- input ----------
  let mx = 0.5, my = 0.5;
  hero.addEventListener("pointermove", (e) => { const b = cv.getBoundingClientRect(); mx = (e.clientX - b.left) / b.width; my = (e.clientY - b.top) / b.height; });
  cv.addEventListener("click", (e) => { const b = cv.getBoundingClientRect(); startChain(e.clientX - b.left, e.clientY - b.top); });
  const btn = hero.querySelector(".fire-btn"); if (btn) btn.addEventListener("click", (e) => { e.stopPropagation(); startChain(); });

  // ---------- simulation ----------
  let T = 0, auto = 2.2;
  function step(dt) {
    T += dt;
    const k = 1 - Math.exp(-dt * 1.5);
    cam.yaw = lerp(cam.yaw, (mx - 0.5) * 0.35 + 0.05 * Math.sin(T * 0.13), k);
    cam.tilt = lerp(cam.tilt, 0.78 + (my - 0.5) * 0.18 + 0.03 * Math.sin(T * 0.17), k);
    // background: a few spontaneous fissions; a fresh chain when the core goes quiet
    if (rnd() < dt * 2.5) { const r = rods[Math.floor(rnd() * rods.length)]; if (!r.guide && rnd() < r.base) { r.flash = Math.max(r.flash, 0.45); flashes.push({ u: r.u, v: r.v, t: 0, big: 0.45 }); } }
    auto -= dt; if (live && auto < 0 && ns.length < 6) { startChain(); auto = 2.5 + 2.5 * rnd(); }
    for (let i = ns.length - 1; i >= 0; i--) {
      const n = ns[i]; n.life += dt; n.u += n.vu * dt; n.v += n.vv * dt; const damp = 1 - dt * 1.7; n.vu *= damp; n.vv *= damp; // slowing down in the water
      n.tr.push(n.u, n.v, n.h); if (n.tr.length > 27) n.tr.splice(0, 3);
      if (n.life > n.max) {
        ns.splice(i, 1);
        const [r, d] = nearestWorld(n.u, n.v);
        if (r && d < 0.8 && rnd() < K / 2.43) fission(r, false);
      }
    }
    for (const r of rods) r.flash = Math.max(0, r.flash - dt * 1.3);
    for (let i = flashes.length - 1; i >= 0; i--) { flashes[i].t += dt; if (flashes[i].t > 1.3) flashes.splice(i, 1); }
    const sy = window.scrollY / Math.max(1, H); if (copy) copy.style.opacity = String(clamp(1 - sy * 1.6, 0, 1));
  }

  // ---------- drawing ----------
  function draw() {
    const act = Math.min(1, ns.length / 70);
    // pool: deep blue-black with the core's light pooled in the middle
    const g = ctx.createRadialGradient(W / 2, H * 0.5, 0, W / 2, H * 0.5, Math.hypot(W, H) * 0.7);
    g.addColorStop(0, "#0a2a52"); g.addColorStop(0.4, "#051a33"); g.addColorStop(1, "#010409");
    ctx.globalCompositeOperation = "source-over"; ctx.globalAlpha = 1; ctx.fillStyle = g; ctx.fillRect(0, 0, W, H);
    // assembly frames on the floor
    ctx.strokeStyle = "rgba(120,190,255,0.10)"; ctx.lineWidth = 1;
    for (const [ax, ay] of frames) { const h = AW / 2 - GAP * 0.2, q = [P(ax - h, ay - h, 0), P(ax + h, ay - h, 0), P(ax + h, ay + h, 0), P(ax - h, ay + h, 0)]; ctx.beginPath(); q.forEach((p, i) => (i ? ctx.lineTo(p[0], p[1]) : ctx.moveTo(p[0], p[1]))); ctx.closePath(); ctx.stroke(); }
    // Cherenkov light pooled over the core
    ctx.globalCompositeOperation = "lighter";
    { const c = P(0, 0, ROD_H * 0.5), R = c[2] * RC * 1.5; ctx.globalAlpha = 0.65 + 0.35 * act + 0.06 * Math.sin(T * 1.1); ctx.drawImage(SP.pool, c[0] - R, c[1] - R * 0.8, 2 * R, 1.6 * R); }
    ctx.globalCompositeOperation = "source-over"; ctx.globalAlpha = 1; ctx.lineCap = "round";
    // rods, far to near: a dark cladding column from the floor up, lit blue toward the top, flashing warm on fission
    for (const r of rods) {
      const b = P(r.u, r.v, 0), t = P(r.u, r.v, ROD_H); r.sx = t[0]; r.sy = t[1]; r.sz = t[2];
      const w = Math.max(1.2, t[2] * (r.guide ? 0.2 : 0.21));
      if (r.guide) { ctx.strokeStyle = `rgba(150,205,255,${0.18 + 0.2 * r.base})`; ctx.lineWidth = 1; ctx.beginPath(); ctx.ellipse(t[0], t[1], w, w * cosT() * 0.9 + 0.5, 0, 0, TAU); ctx.stroke(); continue; }
      const f = clamp(r.flash, 0, 1), gr = ctx.createLinearGradient(b[0], b[1], t[0], t[1]);
      gr.addColorStop(0, "rgba(8,24,48,0.95)"); gr.addColorStop(1, `rgb(${Math.round(lerp(40 + 60 * r.base, 255, f))},${Math.round(lerp(90 + 110 * r.base, 220, f))},${Math.round(lerp(150 + 100 * r.base, 170, f))})`);
      ctx.strokeStyle = gr; ctx.lineWidth = w * 2; ctx.beginPath(); ctx.moveTo(b[0], b[1]); ctx.lineTo(t[0], t[1]); ctx.stroke();
    }
    ctx.globalCompositeOperation = "lighter";
    for (const r of rods) { if (r.guide) continue; const lit = r.base * (0.7 + 0.12 * Math.sin(T * 1.7 + r.u * 0.9 + r.v * 0.5)) + r.flash; if (lit < 0.06) continue; const s = r.sz * (0.8 + 1.6 * r.flash); ctx.globalAlpha = clamp(lit * 0.8, 0, 1); ctx.drawImage(SP.halo, r.sx - s, r.sy - s, 2 * s, 2 * s); }
    // flashes: a hot core and an expanding ring along the floor
    for (const f of flashes) {
      const p = P(f.u, f.v, ROD_H * 0.6), a = 1 - f.t / 1.3, s = p[2] * (0.8 + 3 * f.t) * f.big;
      ctx.globalAlpha = a * a * (f.big > 0.6 ? 1 : 0.55); ctx.drawImage(SP.flash, p[0] - s, p[1] - s, 2 * s, 2 * s);
      if (f.big > 0.6) { const q = P(f.u, f.v, 0), R = q[2] * (0.5 + 5 * f.t); ctx.globalAlpha = 0.5 * a; ctx.strokeStyle = `rgba(${HOT},1)`; ctx.lineWidth = 1.5; ctx.beginPath(); ctx.ellipse(q[0], q[1], R, R * cosT(), 0, 0, TAU); ctx.stroke(); }
    }
    // neutrons with fading trails
    ctx.lineWidth = 1.8; ctx.strokeStyle = `rgba(${CYAN},0.5)`;
    for (const n of ns) {
      const tr = n.tr; ctx.globalAlpha = 0.8; ctx.beginPath();
      for (let i = 0; i < tr.length; i += 3) { const p = P(tr[i], tr[i + 1], tr[i + 2]); i ? ctx.lineTo(p[0], p[1]) : ctx.moveTo(p[0], p[1]); } ctx.stroke();
      const p = P(n.u, n.v, n.h), s = Math.max(5, p[2] * 0.45); ctx.globalAlpha = 1; ctx.drawImage(SP.n, p[0] - s, p[1] - s, 2 * s, 2 * s);
    }
    // water caustics over everything
    ctx.globalAlpha = 1; ctx.strokeStyle = "rgba(150,215,255,0.045)"; ctx.lineWidth = 2.5;
    for (let k = 0; k < 9; k++) { ctx.beginPath(); for (let x = -20; x <= W + 20; x += 22) { const y = H * (k + 0.5) / 9 + 18 * Math.sin(x * 0.011 + T * (0.5 + k * 0.06) + k * 1.7) + 9 * Math.sin(x * 0.029 - T * 0.8 + k); x > -20 ? ctx.lineTo(x, y) : ctx.moveTo(x, y); } ctx.stroke(); }
    ctx.globalCompositeOperation = "source-over";
    // vignette + a dim band at the bottom so the caption reads
    const vg = ctx.createRadialGradient(W / 2, H * 0.48, Math.min(W, H) * 0.35, W / 2, H * 0.48, Math.hypot(W, H) * 0.62);
    vg.addColorStop(0, "rgba(1,4,9,0)"); vg.addColorStop(1, "rgba(1,4,9,0.85)"); ctx.fillStyle = vg; ctx.fillRect(0, 0, W, H);
    const y0 = H * (W < 700 ? 0.3 : 0.55), lo = ctx.createLinearGradient(0, y0, 0, H); lo.addColorStop(0, "rgba(1,4,9,0)"); lo.addColorStop(W < 700 ? 0.55 : 1, "rgba(1,4,9,0.8)"); lo.addColorStop(1, "rgba(1,4,9,0.85)"); ctx.fillStyle = lo; ctx.fillRect(0, y0, W, H - y0);
  }

  // ---------- loop ----------
  let last = performance.now(), visible = true;
  new IntersectionObserver((e) => (visible = e[0].isIntersecting)).observe(hero);
  function frame(now) { const dt = Math.min(0.05, (now - last) / 1000); last = now; if (visible && !document.hidden) { step(dt); draw(); } requestAnimationFrame(frame); }
  layout(); window.addEventListener("resize", () => { layout(); if (reduce) draw(); });
  if (shot || reduce) { for (let i = 0; i < 30; i++) step(0.03); startChain(); for (let i = 0; i < 22; i++) step(0.03); hero.classList.add("hero-live"); document.body.classList.add("hero-done"); }
  if (reduce) draw(); else { if (!shot) setTimeout(() => startChain(), 1100); requestAnimationFrame(frame); }
})();
