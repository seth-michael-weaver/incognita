/* Hero of topics.html (rebuilt from scratch 2026-11-06; Seth: the 3D pool core was "insanely bad").
 * A full-screen field of heavy nuclei in three depth layers (parallax with the pointer), with a live chain reaction running
 * through it: neutrons fly as light streaks; a neutron that hits a nucleus may split it: a white flash, two hot fragments flying
 * apart, a gamma flicker, and two or three new neutrons. Blue light lingers where fissions were, like the glow of a running core.
 * At rest the chain is kept near critical (about one new chain-carrying neutron per neutron lost), so it neither dies nor runs
 * away; "Start a chain" briefly makes it supercritical, then it settles back. Clicking anywhere fires neutrons in.
 * Illustrative: time is slowed enormously and nuclei are drawn hugely magnified and far apart.
 * The title flies out of the first fission (same CSS as the main hero: .hero-live, --hx/--hy/--ho).
 * Dev aid: ?herot=<seconds> runs the opening deterministically to that moment and freezes (for screenshots). */
(function () {
  "use strict";
  const hero = document.querySelector(".tp-hero"), cv = hero && hero.querySelector(".hero-cv");
  if (!cv) return;
  const ctx = cv.getContext("2d"), copy = hero.querySelector(".hero-copy"), h1 = hero.querySelector("h1");
  const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  const qT = /[?&]herot=([\d.]+)/.exec(location.search), freezeAt = qT ? +qT[1] : null;
  const TAU = Math.PI * 2, clamp = (v, a, b) => Math.max(a, Math.min(b, v)), lerp = (a, b, s) => a + (b - a) * s;
  let seed = 11; const rnd = () => ((seed = (seed * 16807) % 2147483647) / 2147483647);
  const mk = (s) => { const c = document.createElement("canvas"); c.width = c.height = s; return c; };

  // ---------- sprites (drawn once) ----------
  function glowSprite(size, stops) { const c = mk(size), x = c.getContext("2d"), g = x.createRadialGradient(size / 2, size / 2, 0, size / 2, size / 2, size / 2);
    stops.forEach(([o, col]) => g.addColorStop(o, col)); x.fillStyle = g; x.fillRect(0, 0, size, size); return c; }
  const S_BLUE = glowSprite(128, [[0, "rgba(140,205,255,0.9)"], [0.25, "rgba(60,140,255,0.45)"], [0.6, "rgba(25,80,230,0.14)"], [1, "rgba(10,40,180,0)"]]);
  const S_WHITE = glowSprite(128, [[0, "rgba(255,255,255,1)"], [0.18, "rgba(255,244,220,0.85)"], [0.45, "rgba(255,190,110,0.3)"], [1, "rgba(255,140,60,0)"]]);
  const S_HOT = glowSprite(64, [[0, "rgba(255,236,200,1)"], [0.3, "rgba(255,150,70,0.75)"], [1, "rgba(255,80,30,0)"]]);
  const S_N = glowSprite(32, [[0, "rgba(235,245,255,1)"], [0.3, "rgba(150,195,255,0.7)"], [1, "rgba(90,140,255,0)"]]);
  const S_HALO = glowSprite(64, [[0, "rgba(255,170,90,0.28)"], [0.5, "rgba(255,120,60,0.08)"], [1, "rgba(255,100,40,0)"]]);
  // a nucleus: a packed cluster of protons (red) and neutrons (blue) lit from the upper left; two versions, sharp and soft
  function nucleusSprite(size, soft) {
    const c = mk(size), x = c.getContext("2d"), R = size * 0.36, n = 46, r = R * 0.27, pts = [];
    let s2 = 5; const q = () => ((s2 = (s2 * 16807) % 2147483647) / 2147483647);
    for (let i = 0; i < n; i++) { const u = q(), v = q(), w = q(), rr = R * Math.cbrt(u) * 0.86, th = TAU * v, ph = Math.acos(2 * w - 1);
      pts.push({ x: rr * Math.sin(ph) * Math.cos(th), y: rr * Math.sin(ph) * Math.sin(th), z: rr * Math.cos(ph), p: q() < 0.4 }); }
    pts.sort((a, b) => a.z - b.z);
    if (soft) x.filter = "blur(" + (size * 0.035).toFixed(1) + "px)";
    for (const p of pts) { const cx = size / 2 + p.x, cy = size / 2 + p.y, lit = 0.55 + 0.45 * (p.z / R + 1) / 2;
      const g = x.createRadialGradient(cx - r * 0.35, cy - r * 0.4, r * 0.08, cx, cy, r);
      const base = p.p ? [236, 92, 78] : [86, 120, 230];
      g.addColorStop(0, "rgba(255,255,255," + (0.95 * lit).toFixed(2) + ")");
      g.addColorStop(0.25, `rgb(${base.map((v) => Math.round(v * (0.75 + 0.35 * lit))).join(",")})`);
      g.addColorStop(1, `rgb(${base.map((v) => Math.round(v * 0.28)).join(",")})`);
      x.fillStyle = g; x.beginPath(); x.arc(cx, cy, r, 0, TAU); x.fill(); }
    return c;
  }
  const S_NUC = nucleusSprite(96, false), S_NUC_SOFT = nucleusSprite(96, true);
  const S_FRAG = nucleusSprite(64, false);

  // ---------- world ----------
  let W = 0, H = 0, dpr = 1, phone = false, mx = 0.5, my = 0.5, pmx = 0.5, pmy = 0.5, quality = 1;
  const LAYERS = [{ z: 0.42, a: 0.38, soft: true }, { z: 0.7, a: 0.7, soft: true }, { z: 1, a: 1, soft: false }];
  let nuc = [], neu = [], frags = [], flashes = [], gammas = [], blooms = [];
  let t = 0, kBoost = 0, firstHit = null, live = false, shake = 0;
  function layout() {
    const b = hero.getBoundingClientRect(); W = Math.max(320, b.width); H = Math.max(400, b.height); phone = W < 720;
    dpr = Math.min(window.devicePixelRatio || 1, 1.5) * quality; cv.width = Math.round(W * dpr); cv.height = Math.round(H * dpr);
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    const want = Math.round(clamp(W * H / (phone ? 9000 : 13000), 30, 110));
    if (nuc.length < want) while (nuc.length < want) nuc.push(newNucleus(true));
    else nuc.length = want;
  }
  function newNucleus(anywhere) {
    const L = rnd(), layer = L < 0.38 ? 0 : L < 0.72 ? 1 : 2;
    return { x: rnd() * W, y: rnd() * H, layer, r: (phone ? 18 : 27) * Math.pow(LAYERS[layer].z, 1.5) * (0.8 + 0.4 * rnd()), ph: rnd() * TAU,
      vx: (rnd() - 0.5) * 4, vy: (rnd() - 0.5) * 4, born: anywhere ? -9 : t, hot: 0 };
  }
  const par = (layer) => { const z = LAYERS[layer].z; return [(pmx - 0.5) * 60 * (z - 0.55), (pmy - 0.5) * 40 * (z - 0.55)]; };
  function addNeutron(x, y, a, layer, mine) {
    const sp = (phone ? 300 : 380) * (0.85 + 0.3 * rnd()) * LAYERS[layer].z;
    neu.push({ x, y, vx: Math.cos(a) * sp, vy: Math.sin(a) * sp, layer, life: 0, trail: [], mine: !!mine });
  }
  function edgeNeutron() { // a stray neutron entering from an edge (cosmic or spontaneous fission source)
    const side = Math.floor(rnd() * 4), layer = 1 + Math.floor(rnd() * 2);
    const x = side === 0 ? -10 : side === 1 ? W + 10 : rnd() * W, y = side === 2 ? -10 : side === 3 ? H + 10 : rnd() * H;
    const a = Math.atan2(H / 2 - y + (rnd() - 0.5) * H * 0.6, W / 2 - x + (rnd() - 0.5) * W * 0.6);
    addNeutron(x, y, a, layer, false);
  }
  function fission(n, by) {
    const [ox, oy] = par(n.layer), x = n.x + ox, y = n.y + oy, z = LAYERS[n.layer].z;
    if (!firstHit) { firstHit = { x, y }; goLive(); }
    flashes.push({ x, y, t: 0, r: n.r, z });
    blooms.push({ x, y, t: 0, r: Math.max(60, n.r * 9) * z, z });
    const a = rnd() * TAU, sp = 120 * z;
    for (const s of [1, -1]) frags.push({ x, y, vx: Math.cos(a) * sp * s, vy: Math.sin(a) * sp * s, r: n.r * (s > 0 ? 0.78 : 0.68), t: 0, z, layer: n.layer });
    gammas.push({ x, y, a: rnd() * TAU, t: 0, z });
    const kids = 2 + (rnd() < 0.43 ? 1 : 0); // about 2.4 neutrons per fission of U-235
    for (let i = 0; i < kids; i++) addNeutron(x, y, rnd() * TAU, n.layer, by && by.mine);
    shake = Math.min(1, shake + 0.12 * z);
    Object.assign(n, newNucleus(false), { x: rnd() * W, y: rnd() * H }); // a fresh nucleus fades in elsewhere
  }
  function goLive() {
    if (live) return; live = true;
    if (h1 && firstHit && !phone) { // the title grows out of the first fission
      const b = hero.getBoundingClientRect(), hb = h1.getBoundingClientRect(), cx = hb.left - b.left + hb.width / 2, cy = hb.top - b.top + hb.height / 2;
      h1.style.setProperty("--ho", `${(firstHit.x - (hb.left - b.left)).toFixed(1)}px ${(firstHit.y - (hb.top - b.top)).toFixed(1)}px`);
      h1.style.setProperty("--hx", "0px"); h1.style.setProperty("--hy", "0px"); h1.style.setProperty("--hk", "1");
      void cx; void cy;
    }
    hero.classList.add("hero-live"); setTimeout(() => document.body.classList.add("hero-done"), 2600);
  }

  // ---------- simulation step ----------
  function step(dt) {
    t += dt; kBoost = Math.max(0, kBoost - dt * 0.22);
    pmx += (mx - pmx) * Math.min(1, dt * 2.5); pmy += (my - pmy) * Math.min(1, dt * 2.5); shake *= Math.exp(-dt * 6);
    // keep the population near a target: below it, strays come in; above it, neutrons are more often absorbed without fission
    const target = (phone ? 10 : 18) * (1 + 5 * kBoost), cap = (phone ? 60 : 120);
    if (neu.length < target * 0.6 && rnd() < dt * 3) edgeNeutron();
    for (const n of nuc) { n.x += n.vx * dt; n.y += n.vy * dt; if (n.x < -40) n.x += W + 80; if (n.x > W + 40) n.x -= W + 80; if (n.y < -40) n.y += H + 80; if (n.y > H + 40) n.y -= H + 80; n.hot = Math.max(0, n.hot - dt * 2); }
    for (let i = neu.length - 1; i >= 0; i--) {
      const q = neu[i]; q.life += dt; q.x += q.vx * dt; q.y += q.vy * dt;
      q.trail.push(q.x, q.y); if (q.trail.length > 28) q.trail.splice(0, 2);
      // the screen edge acts like a reflector: most neutrons bounce back in, some leak out
      if (q.x < 0 || q.x > W) { if (q.refl === undefined && rnd() < 0.75) { q.vx = -q.vx; q.x = clamp(q.x, 0, W); q.refl = 1; } else if (q.x < -60 || q.x > W + 60) { neu.splice(i, 1); continue; } }
      if (q.y < 0 || q.y > H) { if (q.refl === undefined && rnd() < 0.75) { q.vy = -q.vy; q.y = clamp(q.y, 0, H); q.refl = 1; } else if (q.y < -60 || q.y > H + 60) { neu.splice(i, 1); continue; } }
      if (q.life > 7) { neu.splice(i, 1); continue; }
      if (q.refl === 1 && q.x > 0 && q.x < W && q.y > 0 && q.y < H) q.refl = undefined;
      for (const n of nuc) {
        if (n.layer !== q.layer || t - n.born < 0.6) continue;
        const [ox, oy] = par(n.layer), dx = n.x + ox - q.x, dy = n.y + oy - q.y;
        const hr = n.r * 1.4 + 5; if (dx * dx + dy * dy < hr * hr) {
          // chance this hit splits the nucleus; pushed down when the population is high (feedback), up when the chain is started
          const crowd = neu.length / target, pf = clamp(0.62 / Math.max(0.6, crowd) + 0.4 * kBoost, 0.12, 0.98);
          neu.splice(i, 1);
          if (rnd() < pf && neu.length < cap) fission(n, q); else { n.hot = 1; } // captured: the nucleus glows briefly
          break;
        }
      }
    }
    for (let i = frags.length - 1; i >= 0; i--) { const f = frags[i]; f.t += dt; f.x += f.vx * dt; f.y += f.vy * dt; f.vx *= Math.exp(-dt * 1.4); f.vy *= Math.exp(-dt * 1.4); if (f.t > 2.2) frags.splice(i, 1); }
    for (let i = flashes.length - 1; i >= 0; i--) if ((flashes[i].t += dt) > 0.9) flashes.splice(i, 1);
    for (let i = gammas.length - 1; i >= 0; i--) if ((gammas[i].t += dt) > 0.5) gammas.splice(i, 1);
    for (let i = blooms.length - 1; i >= 0; i--) if ((blooms[i].t += dt) > 3.5) blooms.splice(i, 1);
    if (blooms.length > 60) blooms.splice(0, blooms.length - 60);
  }

  // ---------- drawing ----------
  function spr(img, x, y, s, a) { if (a <= 0.003) return; ctx.globalAlpha = a; ctx.drawImage(img, x - s / 2, y - s / 2, s, s); }
  function draw() {
    const sx = (rnd() - 0.5) * 6 * shake, sy = (rnd() - 0.5) * 6 * shake;
    ctx.setTransform(dpr, 0, 0, dpr, dpr * sx, dpr * sy);
    // deep background: near-black with a cold blue haze toward the centre
    ctx.globalCompositeOperation = "source-over"; ctx.globalAlpha = 1;
    const bg = ctx.createRadialGradient(W * 0.5, H * 0.46, 0, W * 0.5, H * 0.5, Math.hypot(W, H) * 0.62);
    bg.addColorStop(0, "#071733"); bg.addColorStop(0.45, "#030a1c"); bg.addColorStop(1, "#010309"); ctx.fillStyle = bg; ctx.fillRect(-10, -10, W + 20, H + 20);
    // lingering blue light where fissions happened (additive)
    ctx.globalCompositeOperation = "lighter";
    for (const b of blooms) { const u = b.t / 3.5, a = (u < 0.08 ? u / 0.08 : 1 - (u - 0.08) / 0.92) * 0.85 * b.z; spr(S_BLUE, b.x, b.y, b.r * (1 + 0.6 * u) * 2.4, a); }
    // nuclei, far to near
    for (let L = 0; L < 3; L++) {
      const lay = LAYERS[L], [ox, oy] = par(L);
      ctx.globalCompositeOperation = "source-over";
      for (const n of nuc) { if (n.layer !== L) continue;
        const fade = clamp((t - n.born) / 0.6, 0, 1), x = n.x + ox, y = n.y + oy + Math.sin(t * 0.7 + n.ph) * 2 * lay.z, s = n.r * 2.7;
        spr(lay.soft ? S_NUC_SOFT : S_NUC, x, y, s, lay.a * fade);
        if (n.hot > 0) { ctx.globalCompositeOperation = "lighter"; spr(S_HOT, x, y, s * 1.4, 0.5 * n.hot); ctx.globalCompositeOperation = "source-over"; } }
      ctx.globalCompositeOperation = "lighter";
      for (const n of nuc) if (n.layer === L) spr(S_HALO, n.x + ox, n.y + oy, n.r * 4.2, 0.5 * lay.a);
      // neutrons of this layer: a fading streak and a bright head
      for (const q of neu) { if (q.layer !== L) continue;
        const tr = q.trail, k = tr.length / 2;
        for (let j = 1; j < k; j++) { ctx.globalAlpha = Math.min(1, (j / k) * 0.9 * lay.a * (q.mine ? 1.2 : 1)); ctx.strokeStyle = q.mine ? "#ffe9a8" : "#a8ceff"; ctx.lineWidth = (q.mine ? 3 : 2.4) * lay.z;
          ctx.beginPath(); ctx.moveTo(tr[2 * j - 2], tr[2 * j - 1]); ctx.lineTo(tr[2 * j], tr[2 * j + 1]); ctx.stroke(); }
        spr(S_N, q.x, q.y, 26 * lay.z * (q.mine ? 1.3 : 1), Math.min(1, lay.a * 1.2)); }
      // fission fragments of this layer: hot, slowing, cooling
      for (const f of frags) { if (f.layer !== L) continue; const u = f.t / 2.2, a = (1 - u) * lay.a;
        ctx.globalCompositeOperation = "source-over"; spr(S_FRAG, f.x, f.y, f.r * 2.6, a);
        ctx.globalCompositeOperation = "lighter"; spr(S_HOT, f.x, f.y, f.r * (3.2 - 1.6 * u), a * (1 - u) * 0.9); }
    }
    ctx.globalCompositeOperation = "lighter";
    // flashes: a white burst and an expanding ring
    for (const f of flashes) { const u = f.t / 0.9, s = f.r * (5 + 26 * Math.sqrt(u)) * f.z;
      spr(S_WHITE, f.x, f.y, s, (1 - u) * (1 - u) * 1.1);
      ctx.globalAlpha = (1 - u) * 0.5 * f.z; ctx.strokeStyle = "#ffd9a0"; ctx.lineWidth = 2.2 * (1 - u) + 0.4; ctx.beginPath(); ctx.arc(f.x, f.y, f.r * (1.2 + 7 * u) * f.z, 0, TAU); ctx.stroke(); }
    // gamma rays: short golden wiggles racing out
    for (const g of gammas) { const u = g.t / 0.5, d = 40 + 380 * u * g.z; ctx.globalAlpha = (1 - u) * 0.85; ctx.strokeStyle = "#ffd36b"; ctx.lineWidth = 1.6; ctx.beginPath();
      for (let i = 0; i <= 14; i++) { const s = d - 26 + i * 2.6, w = Math.sin(i * 1.4 + g.t * 40) * 3; ctx.lineTo(g.x + Math.cos(g.a) * s - Math.sin(g.a) * w, g.y + Math.sin(g.a) * s + Math.cos(g.a) * w); } ctx.stroke(); }
    // keep the title readable: a soft dark band behind it, and a vignette at the edges
    ctx.globalCompositeOperation = "source-over"; ctx.globalAlpha = 1;
    if (!phone) { const ty = H * 0.43, band = ctx.createRadialGradient(W / 2, ty, 0, W / 2, ty, Math.max(W * 0.42, 300)); band.addColorStop(0, "rgba(1,3,10,0.42)"); band.addColorStop(1, "rgba(1,3,10,0)");
      ctx.save(); ctx.translate(W / 2, ty); ctx.scale(1, 0.38); ctx.translate(-W / 2, -ty); ctx.fillStyle = band; ctx.fillRect(0, ty - W, W, 2 * W); ctx.restore(); }
    else { const g2 = ctx.createLinearGradient(0, H * 0.45, 0, H); g2.addColorStop(0, "rgba(1,3,10,0)"); g2.addColorStop(1, "rgba(1,3,10,0.85)"); ctx.fillStyle = g2; ctx.fillRect(0, H * 0.45, W, H * 0.56); }
    const vg = ctx.createRadialGradient(W / 2, H / 2, Math.min(W, H) * 0.35, W / 2, H / 2, Math.hypot(W, H) * 0.6); vg.addColorStop(0, "rgba(1,3,9,0)"); vg.addColorStop(1, "rgba(1,3,9,0.75)");
    ctx.fillStyle = vg; ctx.fillRect(-10, -10, W + 20, H + 20);
  }

  // ---------- interaction ----------
  function fireAt(x, y, n) { for (let i = 0; i < n; i++) { const L = 1 + Math.floor(rnd() * 2), [ox, oy] = par(L); addNeutron(x - ox, y - oy, rnd() * TAU, L, true); } }
  hero.addEventListener("pointermove", (e) => { if (e.pointerType === "touch") return; const b = cv.getBoundingClientRect(); mx = (e.clientX - b.left) / b.width; my = (e.clientY - b.top) / b.height; });
  cv.addEventListener("click", (e) => { const b = cv.getBoundingClientRect(); fireAt(e.clientX - b.left, e.clientY - b.top, 3); if (reduce) still(1.2); });
  const btn = hero.querySelector(".fire-btn");
  if (btn) btn.addEventListener("click", (e) => { e.stopPropagation(); kBoost = 1; for (let i = 0; i < 6; i++) fireAt(W * (0.3 + 0.4 * rnd()), H * (0.3 + 0.4 * rnd()), 2); if (reduce) still(1.6); });

  // ---------- loop ----------
  let last = 0, slow = 0, vis = true;
  new IntersectionObserver((es) => es.forEach((en) => (vis = en.isIntersecting))).observe(hero);
  function frame(now) {
    const dt = Math.min(0.05, last ? (now - last) / 1000 : 0.016); last = now;
    if (vis && !document.hidden) {
      step(dt); draw();
      // slow device: lower the canvas resolution once or twice
      slow = dt > 0.034 ? slow + 1 : Math.max(0, slow - 1);
      if (slow > 50 && quality > 0.6) { quality -= 0.2; slow = 0; layout(); }
      const sc = clamp(window.scrollY / (H * 0.8), 0, 1); if (copy) copy.style.opacity = String(clamp(1 - sc * 1.6, 0, 1));
    }
    requestAnimationFrame(frame);
  }
  function still(sec) { for (let i = 0; i < sec * 60; i++) step(1 / 60); draw(); }
  function opening() { // the first neutron comes in from the left toward a nucleus near the centre
    const target = nuc.reduce((b, n) => (n.layer === 2 && Math.abs(n.x - W * 0.5) + Math.abs(n.y - H * 0.42) < Math.abs(b.x - W * 0.5) + Math.abs(b.y - H * 0.42) ? n : b), nuc.find((n) => n.layer === 2) || nuc[0]);
    target.layer = 2; target.born = -9; const [ox, oy] = par(2), tx = target.x + ox, ty = target.y + oy;
    addNeutron(tx - W * 0.42, ty + H * 0.12, Math.atan2(-H * 0.12, W * 0.42), 2, true);
  }
  layout(); window.addEventListener("resize", () => { layout(); if (reduce) draw(); });
  opening();
  if (freezeAt != null || reduce) { still(freezeAt != null ? freezeAt : 2.5); if (!live) goLive(); hero.classList.add("hero-live"); document.body.classList.add("hero-done"); }
  if (!reduce && freezeAt == null) requestAnimationFrame(frame);
})();
