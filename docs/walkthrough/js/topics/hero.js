/* Hero of topics.html: looking straight down through the water of a research-reactor pool (Seth 2026-11-06: "it should look much
 * more real"). Modelled on pool-reactor photographs: the core sits on a grid plate at the bottom of a tiled pool; square fuel
 * assemblies (5 x 5 rod end caps and a lifting handle seen from above), control assemblies with their drive shafts rising to the
 * surface, an open-water flux trap in the middle and a ring of reflector blocks. Cherenkov light glows in the water between the
 * rods, brightest in the middle of the core; the metal stays dark against it. The pool walls converge to the floor in true
 * top-down perspective, caustics ripple on the floor, specks drift in the water. A fission is a blue-white Cherenkov flash that
 * sends 2-3 neutrons (faint streaks) to nearby rods, so chains flare and die away (multiplication just below 1). The first big
 * chain launches the title (.hero-live). Click or tap the core, or press "Start a chain"; the camera drifts with the pointer.
 * Standalone canvas loop, not a kit chapter. Illustrative. */
(function () {
  "use strict";
  const hero = document.querySelector(".tp-hero"), cv = hero && hero.querySelector(".hero-cv");
  if (!cv) return;
  const ctx = cv.getContext("2d"), copy = hero.querySelector(".hero-copy");
  const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  const shot = document.body.classList.contains("shot") || /[?&](herot=|shot=)/.test(location.search);
  const TAU = Math.PI * 2, clamp = (v, a, b) => Math.max(a, Math.min(b, v)), lerp = (a, b, s) => a + (b - a) * s;
  let seed = 11; const rnd = () => ((seed = (seed * 16807) % 2147483647) / 2147483647);
  const mk = (w, h) => { const c = document.createElement("canvas"); c.width = Math.max(1, Math.round(w)); c.height = Math.max(1, Math.round(h)); return c; };

  // ---------- world (units: assembly pitch = 1; floor at h = 0, camera at h = D looking straight down) ----------
  const D = 13, PX = 9.5, PY = 6.5;            // camera height; pool half-width / half-depth at the floor
  const AW = 0.9, RP = 0.165, RR = 0.06;         // assembly width, rod pitch, rod radius
  const asm = [], rods = [];
  for (let i = -4; i <= 4; i++) for (let j = -3; j <= 3; j++) {
    const r2 = i * i + j * j * 1.3;
    let kind = null;
    if (i === 0 && j === 0) kind = "trap";
    else if ((Math.abs(i) === 1 && Math.abs(j) === 1) || (Math.abs(i) === 2 && j === 0)) kind = "ctrl";
    else if (r2 <= 9.5) kind = "fuel";
    else if (r2 <= 17) kind = "refl";
    if (!kind) continue;
    const base = kind === "refl" ? 0.12 : Math.max(0.15, Math.cos(Math.min(1, Math.sqrt(r2) / 3.6) * Math.PI / 2));
    const a = { i, j, u: i, v: j, kind, base, flash: 0 }; asm.push(a);
    if (kind === "fuel") for (let p = 0; p < 5; p++) for (let q = 0; q < 5; q++) rods.push({ u: i + (p - 2) * RP, v: j + (q - 2) * RP, a, flash: 0, sx: 0, sy: 0 });
  }
  const shafts = asm.filter((a) => a.kind === "ctrl" && Math.abs(a.i) === 1).map((a) => ({ a, du: 0, dv: 0 })); // vertical tubes: from above they fan out from the centre
  const fuelA = asm.filter((a) => a.kind === "fuel");

  // ---------- camera ----------
  let W = 0, H = 0, dpr = 1, S0 = 40; const cam = { x: 0, y: 0 };
  /** world (u, v, h) -> screen [x, y, scale]; straight-down pinhole camera */
  const P = (u, v, h) => { const s = S0 * D / (D - h); return [W / 2 + (u - cam.x) * s, H * 0.48 + (v - cam.y) * s, s]; };

  // ---------- pre-rendered layers ----------
  let floorC = null, FS = 0;   // floor texture (world -PX..PX x -PY..PY) at FS px per unit
  const glowC = mk(PX * 2 * 8, PY * 2 * 8); // low-res Cherenkov map; upscaling blurs it
  const caus = mk(256, 256);
  function glowCol(b, a) { b = Math.min(1, b) * 0.85; return `rgba(${Math.round(lerp(20, 170, b))},${Math.round(lerp(80, 235, b))},${Math.round(lerp(190, 255, b))},${a})`; }
  function buildFloor() {
    FS = Math.min(2.2 * S0 * dpr, 140); floorC = mk(PX * 2 * FS, PY * 2 * FS); const x = floorC.getContext("2d");
    x.setTransform(FS, 0, 0, FS, PX * FS, PY * FS); const px = 1 / FS;
    // pool liner: pale steel tiles, darker joints, lit blue toward the core
    x.fillStyle = "#0c2234"; x.fillRect(-PX, -PY, 2 * PX, 2 * PY);
    seed = 5;
    for (let u = -PX; u < PX; u += 0.5) for (let v = -PY; v < PY; v += 0.5) { x.fillStyle = `rgba(${150 + 40 * rnd()},${200 + 30 * rnd()},235,${0.03 + 0.03 * rnd()})`; x.fillRect(u + 0.02, v + 0.02, 0.46, 0.46); }
    x.strokeStyle = "rgba(4,16,28,0.55)"; x.lineWidth = 1.2 * px;
    for (let u = -PX; u <= PX; u += 0.5) { x.beginPath(); x.moveTo(u, -PY); x.lineTo(u, PY); x.stroke(); }
    for (let v = -PY; v <= PY; v += 0.5) { x.beginPath(); x.moveTo(-PX, v); x.lineTo(PX, v); x.stroke(); }
    // grid plate under the core
    x.fillStyle = "#0b1d2c"; x.fillRect(-4.75, -3.75, 9.5, 7.5);
    x.strokeStyle = "rgba(120,170,210,0.08)"; x.lineWidth = 1.5 * px; x.strokeRect(-4.75, -3.75, 9.5, 7.5);
    for (const a of asm) {
      const h = AW / 2, b = a.base;
      if (a.kind === "refl") {
        x.fillStyle = glowCol(0.1, 0.5); x.fillRect(a.u - 0.5, a.v - 0.5, 1, 1);
        const g = x.createLinearGradient(a.u - h, a.v - h, a.u + h, a.v + h); g.addColorStop(0, "#2a3946"); g.addColorStop(1, "#141f29");
        x.fillStyle = g; x.fillRect(a.u - h, a.v - h, AW, AW);
        x.fillStyle = "#0c1a26"; x.beginPath(); x.arc(a.u, a.v, 0.13, 0, TAU); x.fill();
        x.strokeStyle = "rgba(150,190,215,0.12)"; x.lineWidth = 1 * px; x.strokeRect(a.u - h, a.v - h, AW, AW);
        continue;
      }
      // the water in the cell glows (Cherenkov), brightest in the middle of the core
      const wg = x.createRadialGradient(a.u, a.v, 0, a.u, a.v, 0.75); wg.addColorStop(0, glowCol(Math.min(1, b * 1.05), 1)); wg.addColorStop(1, glowCol(b * 0.75, 1));
      x.fillStyle = wg; x.fillRect(a.u - 0.5, a.v - 0.5, 1, 1);
      if (a.kind === "trap") { // open water flux trap: a thin tube ring, very bright
        x.fillStyle = glowCol(1, 0.9); x.fillRect(a.u - h, a.v - h, AW, AW);
        x.strokeStyle = "#0d1f2e"; x.lineWidth = 0.05; x.beginPath(); x.arc(a.u, a.v, 0.3, 0, TAU); x.stroke();
        x.strokeStyle = "rgba(230,250,255,0.6)"; x.lineWidth = 1.2 * px; x.beginPath(); x.arc(a.u, a.v, 0.27, 0, TAU); x.stroke();
        continue;
      }
      // assembly box walls
      x.strokeStyle = "#0a1824"; x.lineWidth = 0.05; x.strokeRect(a.u - h + 0.025, a.v - h + 0.025, AW - 0.05, AW - 0.05);
      x.strokeStyle = "rgba(150,195,225,0.14)"; x.lineWidth = 1 * px; x.strokeRect(a.u - h, a.v - h, AW, AW);
      if (a.kind === "ctrl") { // control element: a dark cap with the drive-shaft hub
        x.fillStyle = "#101e2a"; x.fillRect(a.u - 0.36, a.v - 0.36, 0.72, 0.72);
        x.strokeStyle = "rgba(160,200,225,0.3)"; x.lineWidth = 1.2 * px; x.strokeRect(a.u - 0.36, a.v - 0.36, 0.72, 0.72);
        const hg = x.createRadialGradient(a.u - 0.05, a.v - 0.05, 0, a.u, a.v, 0.2); hg.addColorStop(0, "#5c7384"); hg.addColorStop(1, "#1a2a37");
        x.fillStyle = hg; x.beginPath(); x.arc(a.u, a.v, 0.18, 0, TAU); x.fill();
        continue;
      }
      // fuel: 5 x 5 rod end caps (dark, a little highlight) with glowing water between them, and a lifting handle
      for (let p = 0; p < 5; p++) for (let q = 0; q < 5; q++) {
        const ru = a.u + (p - 2) * RP, rv = a.v + (q - 2) * RP;
        const rg = x.createRadialGradient(ru - RR * 0.35, rv - RR * 0.35, 0, ru, rv, RR); rg.addColorStop(0, "#4f6577"); rg.addColorStop(0.7, "#1a2b38"); rg.addColorStop(1, "#0b1620");
        x.fillStyle = rg; x.beginPath(); x.arc(ru, rv, RR, 0, TAU); x.fill();
      }
      x.save(); x.translate(a.u, a.v); x.rotate(Math.PI / 4);
      x.fillStyle = "rgba(6,14,22,0.55)"; x.fillRect(-0.5, -0.03 + 0.03, 1.0, 0.07);   // shadow
      const bg = x.createLinearGradient(0, -0.04, 0, 0.04); bg.addColorStop(0, "#7f95a5"); bg.addColorStop(1, "#33475a");
      x.fillStyle = bg; x.fillRect(-0.52, -0.035, 1.04, 0.07); x.fillRect(-0.06, -0.06, 0.12, 0.12);
      x.restore();
    }
    // the core lights the pool floor around it
    x.globalCompositeOperation = "lighter";
    const lg = x.createRadialGradient(0, 0, 2.5, 0, 0, 9); lg.addColorStop(0, "rgba(40,130,230,0.35)"); lg.addColorStop(1, "rgba(40,130,230,0)");
    x.fillStyle = lg; x.fillRect(-PX, -PY, 2 * PX, 2 * PY);
    x.globalCompositeOperation = "source-over";
    // Cherenkov map (low res): every glowing cell, plus a soft spill
    const gx = glowC.getContext("2d"), k = 8; gx.setTransform(k, 0, 0, k, PX * k, PY * k); gx.clearRect(-PX, -PY, 2 * PX, 2 * PY);
    for (const a of asm) { if (a.kind === "refl") continue; gx.fillStyle = glowCol(a.base, a.kind === "trap" ? 0.95 : 0.35 + 0.5 * a.base); gx.fillRect(a.u - 0.5, a.v - 0.5, 1, 1); }
    // caustic tile (seamless): bright filaments where two wave fields line up
    const cx = caus.getContext("2d"), im = cx.createImageData(256, 256), d = im.data;
    for (let yy = 0; yy < 256; yy++) for (let xx = 0; xx < 256; xx++) {
      const X = xx / 256 * TAU, Y = yy / 256 * TAU;
      const f = Math.sin(3 * X + 1.7 * Math.sin(2 * Y)) + Math.sin(4 * Y + 1.3 * Math.sin(3 * X + Y)) + 0.6 * Math.sin(5 * (X + Y));
      const c = Math.pow(Math.max(0, 1 - Math.abs(f) * 0.9), 5); const o = (yy * 256 + xx) * 4;
      d[o] = 150; d[o + 1] = 225; d[o + 2] = 255; d[o + 3] = Math.round(255 * c);
    }
    cx.putImageData(im, 0, 0);
  }

  function layout() {
    const r = cv.getBoundingClientRect(); W = r.width; H = r.height;
    dpr = Math.min(window.devicePixelRatio || 1, W < 700 ? 1.5 : 2);
    cv.width = Math.round(W * dpr); cv.height = Math.round(H * dpr); ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    S0 = Math.min(W / (W < 700 ? 13 : 23), H / (W < 700 ? 17 : 14.5));
    buildFloor();
  }

  // ---------- neutrons and fissions ----------
  const ns = [], flashes = [], specks = [];
  for (let i = 0; i < 70; i++) specks.push({ u: (rnd() * 2 - 1) * PX, v: (rnd() * 2 - 1) * PY, h: 1 + rnd() * (D - 3), ph: rnd() * TAU, s: 0.4 + rnd() });
  const K = 0.93; // neutrons per fission 2.43; each causes a fission with chance K/2.43, so chains end by themselves
  let live = false;
  function fission(r, strong) {
    r.flash = 1; r.a.flash = Math.min(1.4, r.a.flash + (strong ? 1 : 0.55)); flashes.push({ u: r.u, v: r.v, t: 0, big: strong ? 1.6 : 1 });
    const n = strong ? 5 : (rnd() < 0.43 ? 3 : 2);
    for (let i = 0; i < n && ns.length < 260; i++) {
      const a = rnd() * TAU, sp = 2.4 + 2.6 * rnd();
      ns.push({ u: r.u, v: r.v, h: 0.3 + 0.5 * rnd(), vu: Math.cos(a) * sp, vv: Math.sin(a) * sp, life: 0, max: 0.35 + 0.7 * rnd(), tr: [] });
    }
    if (strong && !live) { live = true; setTimeout(() => hero.classList.add("hero-live"), 250); setTimeout(() => document.body.classList.add("hero-done"), 2600); }
  }
  function nearestWorld(u, v) { let best = null, bd = 1e9; for (const r of rods) { const d = (r.u - u) ** 2 + (r.v - v) ** 2; if (d < bd) { bd = d; best = r; } } return [best, Math.sqrt(bd)]; }
  function startChain(x, y) {
    let r = null;
    if (x == null) { const c = rods.filter((q) => q.a.base > 0.75); r = c[Math.floor(rnd() * c.length)]; }
    else { let bd = 1e9; for (const q of rods) { const d = (q.sx - x) ** 2 + (q.sy - y) ** 2; if (d < bd) { bd = d; r = q; } } }
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
    const k = 1 - Math.exp(-dt * 1.2);
    cam.x = lerp(cam.x, (mx - 0.5) * 1.6 + 0.35 * Math.sin(T * 0.11), k);
    cam.y = lerp(cam.y, (my - 0.5) * 1.1 + 0.25 * Math.sin(T * 0.08 + 1), k);
    if (rnd() < dt * 2.2) { const r = rods[Math.floor(rnd() * rods.length)]; if (rnd() < r.a.base) { r.flash = Math.max(r.flash, 0.4); r.a.flash = Math.max(r.a.flash, 0.25); } }
    auto -= dt; if (live && auto < 0 && ns.length < 6) { startChain(); auto = 2.5 + 2.5 * rnd(); }
    for (let i = ns.length - 1; i >= 0; i--) {
      const n = ns[i]; n.life += dt; n.u += n.vu * dt; n.v += n.vv * dt; const damp = 1 - dt * 1.8; n.vu *= damp; n.vv *= damp; // slowing down in the water
      n.tr.push(n.u, n.v, n.h); if (n.tr.length > 24) n.tr.splice(0, 3);
      if (n.life > n.max) { ns.splice(i, 1); const [r, d] = nearestWorld(n.u, n.v); if (r && d < 0.3 && rnd() < K / 2.43) fission(r, false); }
    }
    for (const r of rods) r.flash = Math.max(0, r.flash - dt * 1.4);
    for (const a of asm) a.flash = Math.max(0, a.flash - dt * 0.9);
    for (let i = flashes.length - 1; i >= 0; i--) { flashes[i].t += dt; if (flashes[i].t > 1.1) flashes.splice(i, 1); }
    for (const s of specks) { s.h += dt * 0.12 * s.s; s.u += dt * 0.05 * Math.sin(T * 0.3 + s.ph); if (s.h > D - 1.5) { s.h = 0.8; s.u = (rnd() * 2 - 1) * PX; s.v = (rnd() * 2 - 1) * PY; } }
    const sy = window.scrollY / Math.max(1, H); if (copy) copy.style.opacity = String(clamp(1 - sy * 1.6, 0, 1));
  }

  // ---------- drawing ----------
  const halo = (() => { const c = mk(256, 256), x = c.getContext("2d"), g = x.createRadialGradient(128, 128, 0, 128, 128, 128);
    g.addColorStop(0, "rgba(150,225,255,1)"); g.addColorStop(0.25, "rgba(70,170,255,0.55)"); g.addColorStop(0.6, "rgba(40,120,240,0.15)"); g.addColorStop(1, "rgba(40,120,240,0)");
    x.fillStyle = g; x.fillRect(0, 0, 256, 256); return c; })();
  const spark = (() => { const c = mk(96, 96), x = c.getContext("2d"), g = x.createRadialGradient(48, 48, 0, 48, 48, 48);
    g.addColorStop(0, "rgba(255,255,255,1)"); g.addColorStop(0.18, "rgba(190,240,255,0.9)"); g.addColorStop(0.5, "rgba(90,190,255,0.3)"); g.addColorStop(1, "rgba(60,150,255,0)");
    x.fillStyle = g; x.fillRect(0, 0, 96, 96); return c; })();
  function wall(c0, c1) { // one pool wall: the floor edge c0-c1 rising to the camera, tiled, lit from the core below
    const top = 0.88 * D, a = P(c0[0], c0[1], 0), b = P(c1[0], c1[1], 0), A = P(c0[0], c0[1], top), B = P(c1[0], c1[1], top);
    const g = ctx.createLinearGradient((a[0] + b[0]) / 2, (a[1] + b[1]) / 2, (A[0] + B[0]) / 2, (A[1] + B[1]) / 2);
    g.addColorStop(0, "#1b4a6b"); g.addColorStop(0.18, "#0f2f48"); g.addColorStop(0.55, "#06182a"); g.addColorStop(1, "#020a14");
    ctx.fillStyle = g; ctx.beginPath(); ctx.moveTo(a[0], a[1]); ctx.lineTo(b[0], b[1]); ctx.lineTo(B[0], B[1]); ctx.lineTo(A[0], A[1]); ctx.closePath(); ctx.fill();
    ctx.strokeStyle = "rgba(3,12,22,0.6)"; ctx.lineWidth = 1;
    for (let h = 0.5; h < top; h += 0.5) { const p = P(c0[0], c0[1], h), q = P(c1[0], c1[1], h); ctx.globalAlpha = clamp(1 - h / 6, 0.15, 1); ctx.beginPath(); ctx.moveTo(p[0], p[1]); ctx.lineTo(q[0], q[1]); ctx.stroke(); }
    const L = Math.hypot(c1[0] - c0[0], c1[1] - c0[1]);
    for (let s = 0.5; s < L; s += 0.5) { const u = lerp(c0[0], c1[0], s / L), v = lerp(c0[1], c1[1], s / L), p = P(u, v, 0), q = P(u, v, top); ctx.globalAlpha = 0.5; ctx.beginPath(); ctx.moveTo(p[0], p[1]); ctx.lineTo(q[0], q[1]); ctx.stroke(); }
    ctx.globalAlpha = 1;
  }
  function draw() {
    const act = Math.min(1, ns.length / 60);
    ctx.globalCompositeOperation = "source-over"; ctx.globalAlpha = 1; ctx.fillStyle = "#020a14"; ctx.fillRect(0, 0, W, H);
    // pool walls (far ones first does not matter: they do not overlap in a straight-down view)
    const c = [[-PX, -PY], [PX, -PY], [PX, PY], [-PX, PY]];
    for (let i = 0; i < 4; i++) wall(c[i], c[(i + 1) % 4]);
    // floor: liner, grid plate, core
    const f0 = P(-PX, -PY, 0); ctx.imageSmoothingQuality = "high"; ctx.drawImage(floorC, f0[0], f0[1], 2 * PX * f0[2], 2 * PY * f0[2]);
    // caustics rippling on the floor (two drifting layers)
    ctx.globalCompositeOperation = "lighter";
    ctx.save(); ctx.beginPath(); ctx.rect(f0[0], f0[1], 2 * PX * f0[2], 2 * PY * f0[2]); ctx.clip();
    for (const [sc, vx, vy, al] of [[3.2, 0.05, 0.03, 0.06], [2.1, -0.04, 0.05, 0.05]]) {
      const tile = sc * f0[2], ox = ((T * vx * f0[2] * 4 - cam.x * f0[2]) % tile + tile) % tile, oy = ((T * vy * f0[2] * 4 - cam.y * f0[2]) % tile + tile) % tile;
      ctx.globalAlpha = al;
      for (let x = f0[0] - tile + ox; x < f0[0] + 2 * PX * f0[2]; x += tile) for (let y = f0[1] - tile + oy; y < f0[1] + 2 * PY * f0[2]; y += tile) ctx.drawImage(caus, x, y, tile, tile);
    }
    ctx.restore();
    // Cherenkov: the low-res map upscaled (soft), breathing a little, plus every assembly's flash
    ctx.globalAlpha = 0.3 + 0.25 * act + 0.04 * Math.sin(T * 1.3); ctx.drawImage(glowC, f0[0], f0[1], 2 * PX * f0[2], 2 * PY * f0[2]);
    for (const a of asm) { if (a.flash < 0.02 || a.kind === "refl") continue; const p = P(a.u, a.v, 0.3), s = p[2] * 1.1; ctx.globalAlpha = Math.min(1, a.flash) * 0.7; ctx.drawImage(halo, p[0] - s, p[1] - s, 2 * s, 2 * s); }
    // neutrons: faint streaks just above the core
    ctx.lineWidth = 1.2; ctx.strokeStyle = "rgba(170,235,255,0.35)"; ctx.globalAlpha = 1;
    for (const n of ns) { const tr = n.tr; ctx.beginPath(); for (let i = 0; i < tr.length; i += 3) { const p = P(tr[i], tr[i + 1], tr[i + 2]); i ? ctx.lineTo(p[0], p[1]) : ctx.moveTo(p[0], p[1]); } ctx.stroke(); }
    // fission flashes: blue-white Cherenkov bursts
    for (const fl of flashes) { const p = P(fl.u, fl.v, 0.5), a = 1 - fl.t / 1.1, s = p[2] * (0.25 + 1.4 * fl.t) * fl.big; ctx.globalAlpha = a * a * (fl.big > 1.2 ? 1 : 0.7); ctx.drawImage(spark, p[0] - s, p[1] - s, 2 * s, 2 * s); }
    for (const r of rods) { const p = P(r.u, r.v, 0.55); r.sx = p[0]; r.sy = p[1]; }
    ctx.globalCompositeOperation = "source-over";
    // water: light scattered over the core, drifting specks lit from below, depth haze
    ctx.globalCompositeOperation = "lighter";
    { const p = P(0, 0, D * 0.35), s = p[2] * 5.2; ctx.globalAlpha = 0.2 + 0.2 * act; ctx.drawImage(halo, p[0] - s, p[1] - s * 0.8, 2 * s, 1.6 * s); }
    for (const s of specks) { const p = P(s.u, s.v, s.h); if (p[0] < -10 || p[0] > W + 10 || p[1] < -10 || p[1] > H + 10) continue; const lit = clamp(1 - Math.hypot(s.u, s.v) / 9, 0.1, 1); ctx.globalAlpha = 0.35 * lit * (0.6 + 0.4 * Math.sin(T * 2 + s.ph)); ctx.fillStyle = "rgb(170,225,255)"; const r = Math.min(3, 0.025 * p[2]); ctx.fillRect(p[0], p[1], r, r); }
    ctx.globalCompositeOperation = "source-over"; ctx.globalAlpha = 1;
    // control-rod drive shafts rising from the core to the surface (they spread out toward the camera)
    for (const sh of shafts) {
      const a = sh.a, b = P(a.u, a.v, 0.6), t = P(a.u + sh.du * D, a.v + sh.dv * D, D * 0.8);
      const wb = b[2] * 0.07, wt = Math.min(t[2] * 0.07, 34), ang = Math.atan2(t[1] - b[1], t[0] - b[0]) + Math.PI / 2, cx = Math.cos(ang), sy = Math.sin(ang);
      const g = ctx.createLinearGradient(b[0], b[1], t[0], t[1]); g.addColorStop(0, "rgba(26,52,72,0.95)"); g.addColorStop(0.25, "rgba(8,24,42,0.9)"); g.addColorStop(0.7, "rgba(2,8,16,0.55)"); g.addColorStop(1, "rgba(2,8,16,0)");
      ctx.fillStyle = g; ctx.beginPath(); ctx.moveTo(b[0] - cx * wb, b[1] - sy * wb); ctx.lineTo(b[0] + cx * wb, b[1] + sy * wb); ctx.lineTo(t[0] + cx * wt, t[1] + sy * wt); ctx.lineTo(t[0] - cx * wt, t[1] - sy * wt); ctx.closePath(); ctx.fill();
      const hg = ctx.createLinearGradient(b[0], b[1], t[0], t[1]); hg.addColorStop(0, "rgba(140,210,255,0.55)"); hg.addColorStop(0.35, "rgba(80,160,230,0.12)"); hg.addColorStop(1, "rgba(80,160,230,0)");
      ctx.strokeStyle = hg; ctx.lineWidth = 1.5; ctx.beginPath(); ctx.moveTo(b[0] + cx * wb * 0.5, b[1] + sy * wb * 0.5); ctx.lineTo(t[0] + cx * wt * 0.5, t[1] + sy * wt * 0.5); ctx.stroke();
    }
    ctx.globalCompositeOperation = "source-over"; ctx.globalAlpha = 1;
    ctx.fillStyle = "rgba(4,40,80,0.12)"; ctx.fillRect(0, 0, W, H);
    // vignette + a dim band at the bottom so the caption reads
    const vg = ctx.createRadialGradient(W / 2, H * 0.48, Math.min(W, H) * 0.32, W / 2, H * 0.48, Math.hypot(W, H) * 0.62);
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
