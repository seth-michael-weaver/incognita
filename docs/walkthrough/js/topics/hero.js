/* Hero of topics.html: looking down through the water of a TRIGA-type research-reactor pool into the core (Seth 2026-11-06:
 * the flat top-down pool "does not look good"). A live 3D scene drawn with Canvas 2D: concentric rings of cylindrical fuel
 * elements (B to F ring), four control-rod guide tubes, the central thimble and a ring of graphite dummies stand in a
 * graphite reflector; the camera looks down at an angle, drifts slowly and follows the pointer; scrolling dives toward the core.
 * Blue Cherenkov light glows in the water between the elements; its brightness follows the reactor power.
 * Physics, kept honest: neutrons are a Monte Carlo sample (Russian roulette and splitting keep their number drawable, each
 * carries a weight). Each absorbed neutron causes a fission with chance k / nu (nu = 2.43), so k > 1 grows, k < 1 dies away.
 * At rest the core is critical at low power, held there by temperature feedback. "Start a chain" is a TRIGA pulse: the
 * transient rod is pulled, k jumps above 1, the power climbs exponentially, the fuel heats and the prompt negative
 * temperature coefficient of the U-ZrH fuel turns the pulse over by itself, before the rod drops back. Clicking an element
 * puts a fission there; its neutrons are drawn brighter so you can follow your own chain. Illustrative: time is slowed
 * enormously (real neutron generations last microseconds) and individual neutrons cannot actually be seen.
 * Dev aid: ?herot=<seconds> fast-forwards to that moment of the opening pulse and freezes (for screenshots). */
(function () {
  "use strict";
  const hero = document.querySelector(".tp-hero"), cv = hero && hero.querySelector(".hero-cv");
  if (!cv) return;
  const ctx = cv.getContext("2d"), copy = hero.querySelector(".hero-copy");
  const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  const qT = /[?&]herot=([\d.]+)/.exec(location.search), freezeAt = qT ? +qT[1] : null;
  const TAU = Math.PI * 2, clamp = (v, a, b) => Math.max(a, Math.min(b, v)), lerp = (a, b, s) => a + (b - a) * s;
  let seed = 7; const rnd = () => ((seed = (seed * 16807) % 2147483647) / 2147483647);
  const mk = (w, h) => { const c = document.createElement("canvas"); c.width = w; c.height = h || w; return c; };

  // ---------- the core (units: ring spacing, about 4 cm; z up, top of the core at z = 0) ----------
  const ER = 0.46, ZTOP = 0.35, RIN = 6.65, ROUT = 12.6, RGROOVE = 8.7, ZFLOOR = -16;
  const els = [];   // {x, y, kind: fuel|ctrl|thim|dummy, b (flux shape), glow, fl}
  els.push({ x: 0, y: 0, kind: "thim", b: 1 });
  const CTRL = { "2,0": 1, "2,6": 1, "3,4": 1, "3,13": 1 };
  for (let n = 1; n <= 6; n++) for (let k = 0; k < 6 * n; k++) {
    const a = (k / (6 * n)) * TAU + (n % 2 ? 0 : Math.PI / (6 * n)) + 0.3;
    const kind = n === 6 ? "dummy" : CTRL[n + "," + k] ? "ctrl" : "fuel";
    const r = n * 1.0, b = Math.max(0.12, Math.cos((r / 6.9) * Math.PI / 2)); // fundamental-mode flux shape, cos-like
    els.push({ x: r * Math.cos(a), y: r * Math.sin(a), kind, b, fl: 0 });
  }
  const fuel = els.filter((e) => e.kind === "fuel");

  // ---------- sprites ----------
  function radial(size, stops) { const c = mk(size), x = c.getContext("2d"), g = x.createRadialGradient(size / 2, size / 2, 0, size / 2, size / 2, size / 2); for (const [o, col] of stops) g.addColorStop(o, col); x.fillStyle = g; x.fillRect(0, 0, size, size); return c; }
  const sGlow = radial(128, [[0, "rgba(150,215,255,1)"], [0.22, "rgba(70,150,255,0.62)"], [0.55, "rgba(30,90,235,0.2)"], [1, "rgba(20,60,200,0)"]]);
  const sSpark = radial(128, [[0, "rgba(255,255,255,1)"], [0.12, "rgba(215,240,255,0.95)"], [0.35, "rgba(110,190,255,0.4)"], [1, "rgba(60,130,255,0)"]]);
  const sDot = radial(32, [[0, "rgba(235,248,255,1)"], [0.35, "rgba(150,210,255,0.55)"], [1, "rgba(90,160,255,0)"]]);
  function capSprite(kind) {
    const S = 128, c = mk(S), x = c.getContext("2d"), R = S / 2 - 2; x.translate(S / 2, S / 2);
    if (kind === "thim") { // aluminium tube, open water inside
      x.lineWidth = R * 0.16; x.strokeStyle = "#2c4458"; x.beginPath(); x.arc(0, 0, R * 0.8, 0, TAU); x.stroke();
      x.lineWidth = 2; x.strokeStyle = "rgba(170,225,255,0.8)"; x.beginPath(); x.arc(0, 0, R * 0.72, 0, TAU); x.stroke(); return c;
    }
    const g = x.createRadialGradient(-R * 0.3, -R * 0.35, R * 0.05, 0, 0, R);
    if (kind === "dummy") { g.addColorStop(0, "#3a4954"); g.addColorStop(1, "#141d25"); }
    else { g.addColorStop(0, "#2f4152"); g.addColorStop(0.55, "#121f2b"); g.addColorStop(1, "#070e15"); }
    x.fillStyle = g; x.beginPath(); x.arc(0, 0, R, 0, TAU); x.fill();
    x.lineWidth = 3; x.strokeStyle = "rgba(110,190,255,0.55)"; x.beginPath(); x.arc(0, 0, R - 1.5, 0, TAU); x.stroke(); // rim catches the blue light
    if (kind === "ctrl") { // guide tube: the absorber rod's top inside it
      x.fillStyle = "#04090f"; x.beginPath(); x.arc(0, 0, R * 0.74, 0, TAU); x.fill();
      const h = x.createRadialGradient(-R * 0.15, -R * 0.15, 0, 0, 0, R * 0.42); h.addColorStop(0, "#8aa0b2"); h.addColorStop(1, "#1d2c39");
      x.fillStyle = h; x.beginPath(); x.arc(0, 0, R * 0.4, 0, TAU); x.fill(); return c;
    }
    if (kind === "dummy") { x.fillStyle = "#0c141b"; x.beginPath(); x.arc(0, 0, R * 0.16, 0, TAU); x.fill(); return c; }
    // fuel: triangular top end fitting (three arms and a knob), as on TRIGA elements
    x.lineCap = "round"; x.lineWidth = R * 0.2;
    for (let i = 0; i < 3; i++) { const a = -Math.PI / 2 + i * TAU / 3; const lg = x.createLinearGradient(0, 0, Math.cos(a) * R * 0.78, Math.sin(a) * R * 0.78); lg.addColorStop(0, "#64798c"); lg.addColorStop(1, "#22323f"); x.strokeStyle = lg; x.beginPath(); x.moveTo(0, 0); x.lineTo(Math.cos(a) * R * 0.74, Math.sin(a) * R * 0.74); x.stroke(); }
    const k = x.createRadialGradient(-R * 0.08, -R * 0.08, 0, 0, 0, R * 0.26); k.addColorStop(0, "#aebfcd"); k.addColorStop(0.6, "#4a5e70"); k.addColorStop(1, "#1c2a38");
    x.fillStyle = k; x.beginPath(); x.arc(0, 0, R * 0.25, 0, TAU); x.fill();
    return c;
  }
  const caps = { fuel: capSprite("fuel"), ctrl: capSprite("ctrl"), thim: capSprite("thim"), dummy: capSprite("dummy") };
  // cladding seen from the side: a cylinder, rims lit blue, sinking into the glowing water (bluer, then gone)
  const sBody = (() => { const w = 48, h = 256, c = mk(w, h), x = c.getContext("2d"), im = x.createImageData(w, h), d = im.data;
    for (let j = 0; j < h; j++) { const v = j / (h - 1), a = Math.pow(1 - v, 2.6), m = Math.pow(v, 0.45);
      for (let i = 0; i < w; i++) { const u = (i / (w - 1)) * 2 - 1, nz = Math.sqrt(Math.max(0, 1 - u * u)), rim = Math.pow(1 - nz, 3), spec = Math.pow(Math.max(0, nz * 0.9 + u * 0.4), 18);
        const o = (j * w + i) * 4;
        d[o] = clamp(10 + 25 * rim + 30 * spec, 0, 255); d[o + 1] = clamp(lerp(18, 45, m) + 80 * rim + 45 * spec, 0, 255); d[o + 2] = clamp(lerp(28, 130, m) + 150 * rim + 55 * spec, 0, 255);
        d[o + 3] = Math.round(255 * a * (u * u > 0.97 ? 0.6 : 1)); } }
    x.putImageData(im, 0, 0); return c; })();
  // light in the water just around an element's top: drawn flat around every cap, the rings add up in the gaps between them
  const sRing = radial(128, [[0, "rgba(0,0,0,0)"], [0.7, "rgba(0,0,0,0)"], [0.74, "rgba(120,200,255,0.9)"], [0.8, "rgba(60,140,255,0.55)"], [0.9, "rgba(30,100,255,0.18)"], [1, "rgba(20,80,255,0)"]]);

  // ---------- camera ----------
  let shade = null, dprCap = 2, W = 0, H = 0, dpr = 1, F = 1000, cx0 = 0, cy0 = 0, phone = false;
  const cam = { az: 0, el: 1.0, dist: 44, C: [0, 0, 0], r: [1, 0, 0], u: [0, 0, 1], f: [0, 1, 0] };
  function setCam(az, el, dist) {
    const ce = Math.cos(el); cam.az = az; cam.el = el; cam.dist = dist;
    const C = [dist * ce * Math.sin(az), -dist * ce * Math.cos(az), dist * Math.sin(el) - 1.5];
    const f = [-C[0], -C[1], -1.5 - C[2]], fl = Math.hypot(f[0], f[1], f[2]); f[0] /= fl; f[1] /= fl; f[2] /= fl;
    let r = [f[1], -f[0], 0]; const rl = Math.hypot(r[0], r[1]); r = [r[0] / rl, r[1] / rl, 0];
    const u = [r[1] * f[2] - r[2] * f[1], r[2] * f[0] - r[0] * f[2], r[0] * f[1] - r[1] * f[0]];
    cam.C = C; cam.r = r; cam.u = u; cam.f = f;
  }
  /** world -> [sx, sy, depth, px per unit] */
  function P(x, y, z) { const dx = x - cam.C[0], dy = y - cam.C[1], dz = z - cam.C[2], zc = dx * cam.f[0] + dy * cam.f[1] + dz * cam.f[2], s = F / zc;
    return [cx0 + (dx * cam.r[0] + dy * cam.r[1] + dz * cam.r[2]) * s, cy0 - (dx * cam.u[0] + dy * cam.u[1] + dz * cam.u[2]) * s, zc, s]; }
  function circ(r, z, n) { const bb = [1e9, 1e9, -1e9, -1e9]; ctx.beginPath(); for (let i = 0; i <= n; i++) { const a = i / n * TAU, p = P(r * Math.cos(a), r * Math.sin(a), z); i ? ctx.lineTo(p[0], p[1]) : ctx.moveTo(p[0], p[1]);
    bb[0] = Math.min(bb[0], p[0]); bb[1] = Math.min(bb[1], p[1]); bb[2] = Math.max(bb[2], p[0]); bb[3] = Math.max(bb[3], p[1]); } ctx.closePath(); return bb; }
  /** a sprite lying flat at (x, y, z), radius r: affine map from the local Jacobian of the projection */
  function flat(img, x, y, z, r) { const p = P(x, y, z), a = P(x + r, y, z), b = P(x, y + r, z);
    ctx.setTransform(dpr * (a[0] - p[0]), dpr * (a[1] - p[1]), dpr * (b[0] - p[0]), dpr * (b[1] - p[1]), dpr * p[0], dpr * p[1]); ctx.drawImage(img, -1, -1, 2, 2); }
  function bill(img, p, r) { ctx.drawImage(img, p[0] - r, p[1] - r, 2 * r, 2 * r); }

  function layout() {
    const b = cv.getBoundingClientRect(); W = b.width; H = b.height; phone = W < 721;
    dpr = Math.min(window.devicePixelRatio || 1, phone ? 1.5 : 2, dprCap);
    cv.width = Math.round(W * dpr); cv.height = Math.round(H * dpr);
    cx0 = W / 2; cy0 = phone ? H * 0.3 : H * 0.46;
    const Rpx = phone ? Math.min(W * 0.45, H * 0.27) : Math.min(W * 0.24, H * 0.36); // projected core radius
    F = Rpx * 44 / RIN;
    // vignette and a dark band under the caption: drawn once (half resolution is plenty for gradients)
    shade = mk(Math.max(1, Math.round(W / 2)), Math.max(1, Math.round(H / 2))); const x = shade.getContext("2d"); x.scale(0.5, 0.5);
    { const g = x.createRadialGradient(W / 2, cy0, Math.min(W, H) * 0.35, W / 2, cy0, Math.hypot(W, H) * 0.66); g.addColorStop(0, "rgba(1,4,10,0)"); g.addColorStop(1, "rgba(1,4,10,0.85)"); x.fillStyle = g; x.fillRect(0, 0, W, H); }
    { const y0 = H * (phone ? 0.5 : 0.62), g = x.createLinearGradient(0, y0, 0, H); g.addColorStop(0, "rgba(1,4,10,0)"); g.addColorStop(phone ? 0.35 : 1, "rgba(1,4,10,0.82)"); g.addColorStop(1, "rgba(1,4,10,0.9)"); x.fillStyle = g; x.fillRect(0, y0, W, H - y0); }
  }

  // ---------- neutrons, fissions, feedback ----------
  const NU = 2.43, GEN = 0.42;          // neutrons per fission; mean visible lifetime of a neutron, s (slowed down enormously)
  const ns = [], sparks = [], specks = [];
  let Pv = 1, rho = 0, rhoS = 0, Tf = 0, pulseT = -1, Pw = 1, live = false, T = 0;
  const kEff = () => Math.max(0, 1 + rho + rhoS - 1.15 * Tf);   // rods, servo, prompt negative temperature feedback (U-ZrH fuel)
  for (let i = 0; i < 90; i++) specks.push({ x: (rnd() * 2 - 1) * 15, y: (rnd() * 2 - 1) * 15, z: -2 + rnd() * 30, ph: rnd() * TAU, s: 0.5 + rnd() });
  function emit(e, n, w, mine) {
    for (let i = 0; i < n; i++) { const a = rnd() * TAU, sp = 3.2 + 2.5 * rnd();
      ns.push({ x: e.x + Math.cos(a) * ER, y: e.y + Math.sin(a) * ER, z: -1 - 4 * rnd(), vx: Math.cos(a) * sp, vy: Math.sin(a) * sp, vz: (rnd() - 0.5) * 1.5, life: 0, max: GEN * (0.6 + 0.8 * rnd()), w, mine, tr: [] }); }
  }
  function fission(e, w, mine, big) {
    e.fl = Math.min(1.6, e.fl + (mine ? 1 : 0.35));
    if (mine || sparks.length < 120) sparks.push({ x: e.x, y: e.y, t: 0, big: big ? 2 : mine ? 1.3 : 1 });
    emit(e, rnd() < 0.43 ? 3 : 2, w, mine);
  }
  /** the title flies out once the first pulse is under way (or after a few seconds on a slow device) */
  function goLive() { if (live) return; live = true; setTimeout(() => hero.classList.add("hero-live"), 150); setTimeout(() => document.body.classList.add("hero-done"), 2600); }
  function nearestFuel(x, y) { let best = null, bd = 1e9; for (const e of fuel) { const d = (e.x - x) ** 2 + (e.y - y) ** 2; if (d < bd) { bd = d; best = e; } } return best; }
  function pulse() { if (pulseT >= 0 && T - pulseT < 7) return false; rho = 0.75; pulseT = T; const e = fuel[Math.floor(rnd() * 18)]; fission(e, Pw, true, true); return true; }
  function clickAt(sx, sy) { let best = null, bd = 1e9; for (const e of fuel) { const p = P(e.x, e.y, ZTOP), d = (p[0] - sx) ** 2 + (p[1] - sy) ** 2; if (d < bd) { bd = d; best = e; } }
    if (!best) return; if (!live) { pulse(); return; } fission(best, Pw, true, true); emit(best, 2, Pw, true); }
  // start: critical at low power, a handful of neutrons in flight
  for (let i = 0; i < 26; i++) emit(fuel[Math.floor(rnd() * fuel.length)], 1, 1, false);

  function step(dt) {
    T += dt;
    // transient rod: out for 4.4 s, then driven back in
    if (pulseT >= 0 && T - pulseT > 4.4) rho *= Math.exp(-dt / 1.6);
    // outside a pulse the regulating rod (on its servo) steers the power back to the resting level
    if (pulseT < 0 || T - pulseT > 5) rhoS = lerp(rhoS, clamp(-0.14 * Math.log(Math.max(1e-6, Pw)), -0.1, 0.5), 1 - Math.exp(-dt * 2));
    const k = kEff();
    for (let i = ns.length - 1; i >= 0; i--) {
      const n = ns[i]; n.life += dt;
      const damp = Math.exp(-dt * 3.2); n.vx *= damp; n.vy *= damp; n.vz *= damp;  // slowing down in the water
      if (n.life > n.max * 0.4) { n.vx += (rnd() - 0.5) * 9 * dt; n.vy += (rnd() - 0.5) * 9 * dt; } // thermal diffusion
      n.x += n.vx * dt; n.y += n.vy * dt; n.z = clamp(n.z + n.vz * dt, -6, -0.5);
      const r = Math.hypot(n.x, n.y); if (r > RIN - 0.4) { const s = (RIN - 0.4) / r; n.x *= s; n.y *= s; const vr = (n.vx * n.x + n.vy * n.y) / (r * s); n.vx -= 2 * vr * n.x / (r * s); n.vy -= 2 * vr * n.y / (r * s); } // the reflector scatters them back
      n.tr.push(n.x, n.y, n.z); if (n.tr.length > 27) n.tr.splice(0, 3);
      if (n.life > n.max) { ns.splice(i, 1); if (rnd() < k / NU) fission(nearestFuel(n.x, n.y), n.w, n.mine && rnd() < 0.85, false); }
    }
    // keep the sample drawable: drop random neutrons above the target count, copy random ones below it, then share the total
    // weight equally (all neutrons are alike here), so the power the sample stands for is unchanged by the bookkeeping
    const totW = ns.reduce((s, n) => s + n.w, 0), target = clamp(26 * Math.pow(Pw, 0.38), 16, phone ? 150 : 230);
    if (ns.length > target * 1.2) { let mine = ns.filter((n) => n.mine).length; while (ns.length > target) { const i = Math.floor(rnd() * ns.length); if (ns[i].mine && mine < target * 0.5) continue; if (ns[i].mine) mine--; ns.splice(i, 1); } }
    else if (ns.length && ns.length < target * 0.8) { const m = ns.length; while (ns.length < target) { const n = ns[Math.floor(rnd() * m)]; ns.push({ ...n, vx: -n.vy, vy: n.vx, tr: n.tr.slice(), mine: false }); } }
    else if (!ns.length) emit(fuel[Math.floor(rnd() * fuel.length)], 3, Math.max(Pw, 0.05) * 26 / 3, false); // the start-up source never lets it go fully dark
    if (ns.length && totW) { const w = totW / ns.length; for (const n of ns) n.w = w; }
    // power: the neutron population the sample stands for, relative to the resting level
    Pw = ns.length ? totW / 26 : Pw * 0.97;
    // fuel temperature above its resting value: heated by power above rest, cooled by the pool water
    Tf += dt * (0.01 * (Pw - 1) - Tf / 1.6); Tf = Math.max(-0.08, Tf);
    Pv = Math.exp(lerp(Math.log(Pv), Math.log(Math.max(0.05, Pw)), 1 - Math.exp(-dt / 0.3))); // what the eye sees: smoothed
    if (!live && (Pw > 5 || (pulseT >= 0 && T - pulseT > 4.5))) goLive();
    for (const e of els) { e.fl = Math.max(0, e.fl - dt * 1.3); }
    for (let i = sparks.length - 1; i >= 0; i--) { sparks[i].t += dt; if (sparks[i].t > 0.9) sparks.splice(i, 1); }
    for (const s of specks) { s.z += dt * 0.25 * s.s; s.x += dt * 0.08 * Math.sin(T * 0.3 + s.ph); if (s.z > 28) { s.z = -2; s.x = (rnd() * 2 - 1) * 15; s.y = (rnd() * 2 - 1) * 15; } }
  }

  // ---------- input ----------
  let mx = 0.5, my = 0.5;
  hero.addEventListener("pointermove", (e) => { if (e.pointerType === "touch") return; const b = cv.getBoundingClientRect(); mx = (e.clientX - b.left) / b.width; my = (e.clientY - b.top) / b.height; });
  cv.addEventListener("click", (e) => { const b = cv.getBoundingClientRect(); clickAt(e.clientX - b.left, e.clientY - b.top); if (reduce) still(); });
  const btn = hero.querySelector(".fire-btn"); if (btn) btn.addEventListener("click", (e) => { e.stopPropagation(); if (!pulse()) { const f = fuel[Math.floor(rnd() * 30)]; fission(f, Pw, true, true); emit(f, 2, Pw, true); } if (reduce) still(); });

  // reduced motion: no animation; a click or the button advances the picture by a moment and shows the result
  function still() { for (let i = 0; i < 36; i++) step(1 / 60); draw(); }

  // ---------- drawing ----------
  let az = 0, el = 0.88, sc = 0;
  function draw() {
    const bright = clamp(0.66 + 0.24 * Math.log10(Math.max(0.2, Pv)), 0.45, 1.1), hot = clamp((Pv - 8) / 60, 0, 1);
    const dive = clamp(sc, 0, 1);
    setCam(az, el + dive * 0.25, 44 * (1 - 0.45 * dive));
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0); ctx.globalCompositeOperation = "source-over"; ctx.globalAlpha = 1;
    // deep water, lit from the core
    const c0 = P(0, 0, -2);
    { const g = ctx.createRadialGradient(c0[0], c0[1], 0, c0[0], c0[1], Math.max(W, H) * 0.8); g.addColorStop(0, "#0a3a70"); g.addColorStop(0.45, "#041d3c"); g.addColorStop(1, "#01060e"); ctx.fillStyle = g; ctx.fillRect(0, 0, W, H); }
    // pool floor around the reflector
    circ(30, ZFLOOR, 72); { const g = ctx.createRadialGradient(c0[0], c0[1], 0, c0[0], c0[1], 30 * c0[3]); g.addColorStop(0, "rgba(30,110,200,0.5)"); g.addColorStop(0.5, "rgba(8,40,80,0.4)"); g.addColorStop(1, "rgba(2,10,22,0)"); ctx.fillStyle = g; ctx.fill(); }
    // reflector: outer side (the part facing the camera)
    ctx.beginPath(); const N = 96; let started = false;
    const top = [], bot = [];
    for (let i = 0; i <= N; i++) { const a = i / N * TAU, x = Math.cos(a), y = Math.sin(a); top.push(P(ROUT * x, ROUT * y, ZTOP)); bot.push(P(ROUT * x, ROUT * y, -14)); }
    for (let i = 0; i < N; i++) { const a = (i + 0.5) / N * TAU, nx = Math.cos(a), ny = Math.sin(a), facing = nx * (cam.C[0] - ROUT * nx) + ny * (cam.C[1] - ROUT * ny) > 0; if (!facing) continue;
      ctx.moveTo(top[i][0], top[i][1]); ctx.lineTo(top[i + 1][0], top[i + 1][1]); ctx.lineTo(bot[i + 1][0], bot[i + 1][1]); ctx.lineTo(bot[i][0], bot[i][1]); ctx.closePath(); started = true; }
    if (started) { const yt = P(0, -ROUT, ZTOP)[1], yb = P(0, -ROUT, -14)[1], g = ctx.createLinearGradient(0, yt, 0, yb); g.addColorStop(0, `rgba(40,110,180,${0.55 * bright})`); g.addColorStop(0.08, "#0b2238"); g.addColorStop(1, "#020912"); ctx.fillStyle = g; ctx.fill(); }

    // ---- the well: everything below the top of the reflector, seen through its opening ----
    ctx.save(); const wb = circ(RIN, ZTOP, 72); ctx.clip();
    { const cw = P(0, 0, -4), R = RIN * cw[3] * 1.15, g = ctx.createRadialGradient(cw[0], cw[1], 0, cw[0], cw[1], R);
      g.addColorStop(0, `rgba(${lerp(70, 200, hot)},${lerp(165, 235, hot)},255,${0.95 * bright})`); g.addColorStop(0.5, `rgba(20,95,245,${0.9 * bright})`); g.addColorStop(1, `rgba(8,40,150,${0.95})`);
      ctx.fillStyle = "#03122a"; ctx.fillRect(wb[0], wb[1], wb[2] - wb[0], wb[3] - wb[1]); ctx.fillStyle = g; ctx.fillRect(wb[0], wb[1], wb[2] - wb[0], wb[3] - wb[1]); }
    // inner wall of the reflector, far side: lit
    const order = els.map((e) => [e, P(e.x, e.y, ZTOP)]).sort((a, b) => b[1][2] - a[1][2]);
    ctx.globalCompositeOperation = "lighter";
    for (const [e, p] of order) { if (e.kind === "dummy") continue; const q = P(e.x, e.y, -3.5); ctx.globalAlpha = clamp((0.35 + 0.75 * e.b) * bright + 0.5 * e.fl, 0, 1); bill(sGlow, q, q[3] * 2.3); }
    ctx.globalCompositeOperation = "source-over"; ctx.globalAlpha = 1;
    for (const [e, p] of order) {
      if (e.kind !== "thim") { // cladding hanging down into the glow
        const b = P(e.x, e.y, -6.5), dx = b[0] - p[0], dy = b[1] - p[1], L = Math.hypot(dx, dy) || 1, w = ER * p[3];
        ctx.setTransform(dpr * (dy / L) * -w, dpr * (dx / L) * w, dpr * dx, dpr * dy, dpr * p[0], dpr * p[1]); ctx.drawImage(sBody, -1, 0, 2, 1);
      }
      ctx.globalAlpha = 1; flat(caps[e.kind], e.x, e.y, ZTOP, ER);
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      if (e.fl > 0.03 || e.kind === "thim") { ctx.globalCompositeOperation = "lighter"; ctx.globalAlpha = e.kind === "thim" ? 0.55 * bright : Math.min(1, e.fl) * 0.55; bill(sGlow, p, p[3] * (e.kind === "thim" ? 0.9 : 1.3)); ctx.globalCompositeOperation = "source-over"; ctx.globalAlpha = 1; }
    }
    ctx.globalCompositeOperation = "lighter";
    for (const e of els) { ctx.globalAlpha = clamp((0.4 + 0.6 * e.b) * bright * 0.9 + 0.6 * e.fl, 0, 1); flat(sRing, e.x, e.y, ZTOP, ER / 0.72); }
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    // light in the water between the elements and the camera
    ctx.globalCompositeOperation = "lighter";
    { const p = P(0, 0, 0.5); ctx.globalAlpha = 0.14 * bright + 0.3 * hot; bill(sGlow, p, RIN * p[3] * 1.05); }
    // neutrons (a drawn sample) and fission flashes
    ctx.lineCap = "round";
    for (const n of ns) { const t = n.tr; if (t.length < 6) continue; ctx.beginPath(); for (let i = 0; i < t.length; i += 3) { const p = P(t[i], t[i + 1], t[i + 2]); i ? ctx.lineTo(p[0], p[1]) : ctx.moveTo(p[0], p[1]); }
      ctx.strokeStyle = n.mine ? "rgba(255,244,214,0.8)" : "rgba(185,232,255,0.5)"; ctx.lineWidth = n.mine ? 2 : 1.3; ctx.stroke();
      const p = P(n.x, n.y, n.z); ctx.globalAlpha = n.mine ? 1 : 0.75; bill(sDot, p, n.mine ? 5 : 3.2); ctx.globalAlpha = 1; }
    for (const s of sparks) { const p = P(s.x, s.y, -0.5), a = 1 - s.t / 0.9; ctx.globalAlpha = a * a * (s.big > 1 ? 1 : 0.6); bill(sSpark, p, p[3] * (0.35 + 1.6 * s.t) * s.big); }
    ctx.restore(); ctx.setTransform(dpr, 0, 0, dpr, 0, 0); ctx.globalCompositeOperation = "source-over"; ctx.globalAlpha = 1;

    // reflector top: aluminium annulus with the rotary specimen rack groove, lit from the well
    ctx.beginPath(); { for (let i = 0; i <= 96; i++) { const a = i / 96 * TAU, p = P(ROUT * Math.cos(a), ROUT * Math.sin(a), ZTOP); i ? ctx.lineTo(p[0], p[1]) : ctx.moveTo(p[0], p[1]); }
      for (let i = 0; i <= 96; i++) { const a = -i / 96 * TAU, p = P(RIN * Math.cos(a), RIN * Math.sin(a), ZTOP); i ? ctx.lineTo(p[0], p[1]) : ctx.moveTo(p[0], p[1]); } }
    { const p = P(0, 0, ZTOP), rx = RIN * p[3], g = ctx.createRadialGradient(p[0], p[1], rx * 0.9, p[0], p[1], ROUT * p[3] * 1.05);
      g.addColorStop(0, `rgb(${Math.round(lerp(40, 90, hot))},${Math.round(110 * bright + 40)},${Math.round(200 * bright + 40)})`); g.addColorStop(0.12, `rgb(16,${Math.round(50 + 30 * bright)},${Math.round(90 + 40 * bright)})`); g.addColorStop(0.5, "#0b2236"); g.addColorStop(1, "#06131f");
      ctx.fillStyle = g; ctx.fill("evenodd"); }
    ctx.lineWidth = 1.2; ctx.strokeStyle = `rgba(150,215,255,${0.35 + 0.4 * bright})`; circ(RIN, ZTOP, 96); ctx.stroke();
    ctx.strokeStyle = "rgba(2,8,14,0.7)"; ctx.lineWidth = 2.2; circ(RGROOVE, ZTOP, 96); ctx.stroke();
    ctx.strokeStyle = `rgba(120,190,240,${0.12 + 0.12 * bright})`; ctx.lineWidth = 1; circ(RGROOVE + 0.18, ZTOP, 96); ctx.stroke();
    for (let i = 0; i < 40; i++) { const a = i / 40 * TAU; flat(caps.dummy, RGROOVE * Math.cos(a), RGROOVE * Math.sin(a), ZTOP, 0.15); }
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    ctx.strokeStyle = "rgba(150,200,240,0.16)"; ctx.lineWidth = 1; circ(ROUT - 0.1, ZTOP, 96); ctx.stroke();

    // light scattered up through the water column
    ctx.globalCompositeOperation = "lighter";
    { const p = P(0, 0, 5); ctx.globalAlpha = 0.22 * bright + 0.25 * hot; bill(sGlow, p, RIN * p[3] * 2.2); }
    { const p = P(0, 0, 14); ctx.globalAlpha = 0.1 * bright + 0.18 * hot; bill(sGlow, p, RIN * p[3] * 3.6); }
    for (const s of specks) { const p = P(s.x, s.y, s.z); if (p[2] < 4 || p[0] < -5 || p[0] > W + 5 || p[1] < -5 || p[1] > H + 5) continue; const lit = clamp(1 - Math.hypot(s.x, s.y) / 16, 0.15, 1) * bright;
      ctx.globalAlpha = 0.5 * lit * (0.6 + 0.4 * Math.sin(T * 1.7 + s.ph)); const r = clamp(0.05 * p[3], 0.8, 3.5); ctx.fillStyle = "rgb(160,215,255)"; ctx.fillRect(p[0] - r / 2, p[1] - r / 2, r, r); }
    // the brief blue-white bloom at the top of a pulse
    if (hot > 0.02) { ctx.globalAlpha = 0.24 * hot; ctx.fillStyle = "rgb(40,110,255)"; ctx.fillRect(0, 0, W, H); }
    ctx.globalCompositeOperation = "source-over"; ctx.globalAlpha = 1;
    // vignette, and a dark band so the caption reads
    ctx.drawImage(shade, 0, 0, W, H);
  }

  function cameraStep(dt) {
    const k = 1 - Math.exp(-dt * 1.4);
    az = lerp(az, 0.16 * Math.sin(T * 0.06) + (mx - 0.5) * 0.5, k);
    el = lerp(el, 0.88 + 0.05 * Math.sin(T * 0.045 + 1) - (my - 0.5) * 0.14, k);
    sc = window.scrollY / Math.max(1, H);
    if (copy) copy.style.opacity = String(clamp(1 - sc * 1.6, 0, 1));
  }

  // ---------- loop ----------
  let last = performance.now(), visible = true;
  new IntersectionObserver((e) => (visible = e[0].isIntersecting)).observe(hero);
  let slow = 0; // a slow device: lower the canvas resolution rather than drop frames
  function frame(now) { const raw = (now - last) / 1000, dt = Math.min(0.05, raw); last = now;
    if (visible && !document.hidden && raw < 0.2) { slow = raw > 0.045 ? slow + raw : Math.max(0, slow - raw * 0.5); if (slow > 1.5 && dprCap > 0.5) { dprCap = Math.max(0.5, Math.min(dprCap, dpr) - 0.25); slow = 0; layout(); } }
    if (visible && !document.hidden) { if (freezeAt == null) { step(dt); cameraStep(dt); } draw(); } requestAnimationFrame(frame); }
  layout(); window.addEventListener("resize", () => { layout(); if (reduce) draw(); });
  if (freezeAt != null || reduce) { // fast-forward deterministically: settle, pulse at 1 s, stop at the requested moment
    const end = freezeAt != null ? freezeAt : 4.2; let t = 0, fired = false;
    while (t < end) { if (!fired && t >= 1) { pulse(); fired = true; } step(1 / 60); cameraStep(1 / 60); t += 1 / 60; }
    hero.classList.add("hero-live"); document.body.classList.add("hero-done");
  }
  if (reduce) draw(); else { if (freezeAt == null) { setTimeout(() => pulse(), 1000); setTimeout(goLive, 4500); } requestAnimationFrame(frame); }
})();
