/* Hero: a full-screen, live picture of one nuclear reaction, on a loop.
 * A neutron streaks in, the impact rings through the nucleus as a heat wave, the nucleus glows, and something bursts out:
 * a neutron, a proton, an alpha particle, a gamma ray, two neutrons, or (every few cycles) fission, where the nucleus
 * stretches, necks and tears in two. The nucleus tilts toward the pointer, a click or tap fires your own neutron, and
 * scrolling zooms into the nucleus. Standalone (own canvas and frame loop), not a kit chapter. Illustrative, not computed. */
(function () {
  "use strict";
  const hero = document.querySelector(".hero"), cv = hero && hero.querySelector(".hero-cv");
  if (!cv) return;
  const ctx = cv.getContext("2d"), copy = hero.querySelector(".hero-copy");
  const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  const TAU = Math.PI * 2, clamp = (v, a, b) => Math.max(a, Math.min(b, v)), lerp = (a, b, s) => a + (b - a) * s;
  const smooth = (e0, e1, x) => { const t = clamp((x - e0) / (e1 - e0), 0, 1); return t * t * (3 - 2 * t); };
  const easeOut = (t) => 1 - Math.pow(1 - clamp(t, 0, 1), 3);
  const tr = (s) => (window.WT && WT.tr ? WT.tr(s) : s);
  function rng(seed) { let s = seed >>> 0 || 1; return () => ((s = (s * 16807) % 2147483647) / 2147483647); }
  const C = { n: "#6f8cff", p: "#ff6a5c", gam: "#ffd166", hot: "#ffb067", white: "#fff6ea", a: "#b48cff" };

  // ---------- sprites (drawn once, stamped with drawImage) ----------
  function hex(h) { const n = parseInt(h.slice(1), 16); return [(n >> 16) & 255, (n >> 8) & 255, n & 255]; }
  const rgba = (h, a) => { const [r, g, b] = hex(h); return `rgba(${r},${g},${b},${a})`; };
  const shade = (h, f) => { const [r, g, b] = hex(h), c = (v) => Math.min(255, (v * f) | 0).toString(16).padStart(2, "0"); return "#" + c(r) + c(g) + c(b); };
  function ballSprite(col, S = 96) {
    const c = document.createElement("canvas"); c.width = c.height = S; const g = c.getContext("2d"), r = S / 2;
    const gr = g.createRadialGradient(r * 0.62, r * 0.55, r * 0.04, r, r, r);
    gr.addColorStop(0, "#ffffff"); gr.addColorStop(0.22, col); gr.addColorStop(0.75, shade(col, 0.55)); gr.addColorStop(1, shade(col, 0.22));
    g.fillStyle = gr; g.beginPath(); g.arc(r, r, r - 1, 0, TAU); g.fill(); return c;
  }
  function glowSprite(col, S = 128) {
    const c = document.createElement("canvas"); c.width = c.height = S; const g = c.getContext("2d"), r = S / 2;
    const gr = g.createRadialGradient(r, r, 0, r, r, r); gr.addColorStop(0, rgba(col, 1)); gr.addColorStop(0.25, rgba(col, 0.45)); gr.addColorStop(1, rgba(col, 0));
    g.fillStyle = gr; g.fillRect(0, 0, S, S); return c;
  }
  const DEPTH = [0.5, 0.72, 0.9, 1.08];                 // nucleons further back are drawn darker
  const SPD = { n: DEPTH.map((f) => ballSprite(shade(C.n, f))), p: DEPTH.map((f) => ballSprite(shade(C.p, f))) }, SP = { n: SPD.n[2], p: SPD.p[2] }, GL = { n: glowSprite(C.n), p: glowSprite(C.p), hot: glowSprite(C.hot), white: glowSprite(C.white), gam: glowSprite(C.gam), a: glowSprite(C.a) };
  const stamp = (img, x, y, r, a = 1) => { if (a <= 0.003 || r <= 0.2) return; ctx.globalAlpha = Math.min(1, a); ctx.drawImage(img, x - r, y - r, 2 * r, 2 * r); };

  // ---------- the nucleus: uranium-235 (92 protons, 143 neutrons) packed in a unit sphere (relaxed once) ----------
  const N = 235, Z = 92, rb = Math.cbrt(0.62 / N);
  const nuc = [];
  (function pack() {
    const r = rng(11);
    for (let i = 0; i < N; i++) { let x, y, z; do { x = r() * 2 - 1; y = r() * 2 - 1; z = r() * 2 - 1; } while (x * x + y * y + z * z > 1); nuc.push({ x, y, z, p: false, ph: r() * 100, h: 0, side: 0 }); }
    const d0 = 2 * rb * 0.97, lim = 1 - rb;
    for (let it = 0; it < 60; it++) {
      for (let i = 0; i < N; i++) for (let j = i + 1; j < N; j++) {
        const a = nuc[i], b = nuc[j], dx = b.x - a.x, dy = b.y - a.y, dz = b.z - a.z, d = Math.sqrt(dx * dx + dy * dy + dz * dz) || 1e-6;
        if (d < d0) { const k = (d0 - d) / d * 0.5; a.x -= dx * k; a.y -= dy * k; a.z -= dz * k; b.x += dx * k; b.y += dy * k; b.z += dz * k; }
      }
      for (const a of nuc) { const d = Math.sqrt(a.x * a.x + a.y * a.y + a.z * a.z); if (d > lim) { a.x *= lim / d; a.y *= lim / d; a.z *= lim / d; } }
    }
    const idx = nuc.map((_, i) => i); for (let i = N - 1; i > 0; i--) { const j = Math.floor(r() * (i + 1)); [idx[i], idx[j]] = [idx[j], idx[i]]; }
    for (let k = 0; k < Z; k++) nuc[idx[k]].p = true;
  })();

  // ---------- background: stars and a drifting stream of faint flux ----------
  const R0 = rng(5), stars = [], flux = [];
  for (let i = 0; i < 260; i++) stars.push({ x: R0(), y: R0(), d: 0.2 + R0() * 0.8, s: 0.4 + R0() * 1.3, tw: R0() * TAU });
  for (let i = 0; i < 70; i++) flux.push({ x: R0(), y: R0(), v: 0.04 + R0() * 0.12, l: 10 + R0() * 40, a: 0.08 + R0() * 0.22 });

  // ---------- the reaction cycle ----------
  const SEQ = ["fission", "gamma", "neutron", "fission", "alpha", "two", "fission", "proton", "gamma", "fission"]; // U-235: fission comes up often
  const CAP = {
    neutron: "a neutron comes back out", gamma: "a gamma ray: a burst of light", proton: "a proton escapes",
    two: "two neutrons come out", alpha: "an alpha particle: 2 protons + 2 neutrons", fission: "fission: the nucleus splits in two",
    absorbed: "absorbed: its energy spreads through the whole nucleus",
  };
  const FA = 1.15, FC = Math.cos(FA), FS = Math.sin(FA);                         // fission axis: steep, so both halves stay right of the title
  const T_IMP = 1.9, T_EMIT = 3.5, T_END = 6.6;                                    // ordinary cycle
  const F_STRETCH = 3.0, F_SCISSION = 4.6, F_GONE = 7.4, F_REFORM = 9.0, F_END = 9.6; // fission cycle
  let W = 0, H = 0, dpr = 1, time = 0, ct = 0, cyc = 0, kind = SEQ[0], ang = 0, yaw = 0.4;
  let tiltX = 0, tiltY = 0, tgtX = 0, tgtY = 0, scrollP = 0, shake = 0, flash = 0, flashCol = C.white, impacted = false, emitted = false;
  let spin = 1, fis = { e: 0, sep: 0, done: false, rot: 0, alpha: 1, away: 0 }, reform = 1, kick = 0;
  const parts = [], rings = [], shots = [];
  let imp = { x: 0, y: 0, t: -99 };
  const geo = () => {
    const phone = W < 720;
    // the nucleus stays put while the page scrolls (no zoom or drift): the hero is what visitors see on arrival
    // phones: the nucleus fills the band above the text, never behind the title
    const room = phone ? Math.max(120, copy.offsetTop + (copy.firstElementChild ? copy.firstElementChild.offsetTop : 0)) : 0; // the copy box is bottom-aligned: its first line is where the text starts
    const R = phone ? Math.min(W * 0.13, room * 0.3) : Math.min(W, H) * 0.24, cx = W * (phone ? 0.5 : 0.64), cy = phone ? room * 0.56 : H * 0.47;
    return { R, cx, cy, phone };
  };

  function startCycle() {
    ct = 0; kind = SEQ[cyc % SEQ.length]; cyc++; impacted = false; emitted = false; ang = (rng(cyc * 31 + 7))() * TAU;
    fis = { e: 0, sep: 0, done: false, rot: 0, alpha: 1, away: 0 }; for (const a of nuc) a.side = 0;
    const { R, cx, cy } = geo(), r = rng(cyc * 13 + 3), off = (r() - 0.5) * R * 0.9;
    // the projectile: from far off-screen left, aimed at the nucleus's left side
    parts.push({ k: "in", x: -W * 0.15, y: cy + off - H * 0.12, tx: cx - Math.sqrt(Math.max(0, R * R - off * off)) * 0.92, ty: cy + off, t0: 0, dur: T_IMP, trail: [] });
  }

  // your neutron reaches the nucleus and starts the next reaction (same outcome sequence, captions and timing from the
  // impact on), replacing whatever the cycle was doing; only a fission split in progress is let finish, and the hit
  // then waits for the nucleus to re-form (pending)
  let pending = null;
  const idle = () => kind !== "fission" || ct < F_STRETCH || ct >= F_REFORM;
  function userHit(x, y) {
    if (!idle()) { pending = { x, y }; return false; }
    pending = null;
    for (let i = parts.length - 1; i >= 0; i--) if (parts[i].k === "in") parts.splice(i, 1);
    kind = SEQ[cyc % SEQ.length]; cyc++; emitted = false; ang = (rng(cyc * 31 + 7))() * TAU;
    fis = { e: 0, sep: 0, done: false, rot: 0, alpha: 1, away: 0 }; for (const a of nuc) a.side = 0;
    reform = 1; ct = T_IMP; impact(x, y, 1); impacted = true;
    return true;
  }

  function impact(x, y, strength) {
    imp = { x, y, t: time, s: strength }; flash = Math.max(flash, 0.55 * strength); flashCol = C.white; shake = Math.max(shake, 10 * strength);
    rings.push({ x, y, t: time, s: strength, col: C.white }, { x, y, t: time + 0.08, s: strength * 0.7, col: C.hot });
  }

  function emit(k, cx, cy, R) {
    const a = ang, sp = Math.max(W, H) * 0.55, out = (dir, extra) => ({ x: cx + Math.cos(dir) * R * 1.02, y: cy + Math.sin(dir) * R * 1.02, vx: Math.cos(dir) * sp, vy: Math.sin(dir) * sp, t0: time, trail: [], ...extra });
    if (k === "gamma") { parts.push(out(a, { k: "gam" }), out(a + 2.5, { k: "gam" })); flash = 0.7; flashCol = C.gam; }
    else if (k === "proton") parts.push(out(a, { k: "p" }));
    else if (k === "neutron") parts.push(out(a, { k: "n" }));
    else if (k === "two") parts.push(out(a, { k: "n" }), out(a + 2.4, { k: "n" }));
    else if (k === "alpha") parts.push(out(a, { k: "a", vx: Math.cos(a) * sp * 0.7, vy: Math.sin(a) * sp * 0.7 }));
    shake = Math.max(shake, 6); rings.push({ x: cx + Math.cos(a) * R, y: cy + Math.sin(a) * R, t: time, s: 0.6, col: k === "gamma" ? C.gam : C.hot });
  }

  // ---------- pointer: tilt and fire ----------
  hero.addEventListener("pointermove", (e) => { const r = cv.getBoundingClientRect(); tgtX = ((e.clientX - r.left) / r.width - 0.5) * 2; tgtY = ((e.clientY - r.top) / r.height - 0.5) * 2; });
  hero.addEventListener("pointerleave", () => { tgtX = 0; tgtY = 0; });
  // after the first neutron the scroll cue lights up: readers who keep firing should see that the page goes on below
  const cue = document.querySelector(".scrollcue");
  const nudge = () => { if (cue) cue.classList.add("hot"); };
  hero.addEventListener("pointerdown", (e) => {
    if (e.target.closest("a, button")) return;
    const r = cv.getBoundingClientRect(), x = e.clientX - r.left, y = e.clientY - r.top, { cx, cy } = geo();
    shots.push({ x, y, sx: x, sy: y, t0: time, trail: [], dx: cx, dy: cy });
    nudge();
    if (reduce) frame(0);
  });
  // the same for keyboard and screen-reader users: a real button fires a neutron in from the left
  const fire = hero.querySelector(".fire-btn");
  if (fire) fire.addEventListener("click", () => { const { cy } = geo(), y = cy + (Math.random() - 0.5) * H * 0.3; shots.push({ x: 0, y, sx: -20, sy: y, t0: time, trail: [] }); nudge(); if (reduce) frame(0); });

  // ---------- drawing ----------
  // performance: the backdrop gradient is painted once per size into its own canvas, and the drifting streaks are one
  // pre-drawn image, instead of a full-screen gradient and 70 new gradient objects every frame
  let bgC = null, bgKey = "";
  const STREAK = (() => { const c = document.createElement("canvas"); c.width = 64; c.height = 2; const g = c.getContext("2d"), gr = g.createLinearGradient(0, 0, 64, 0); gr.addColorStop(0, rgba(C.n, 0)); gr.addColorStop(1, rgba(C.n, 1)); g.fillStyle = gr; g.fillRect(0, 0, 64, 2); return c; })();
  function background(cx, cy, R) {
    const key = W + "x" + H + "@" + dpr + ":" + Math.round(cx) + "," + Math.round(cy);
    if (key !== bgKey) {
      bgKey = key; bgC = bgC || document.createElement("canvas"); bgC.width = Math.round(W * dpr); bgC.height = Math.round(H * dpr);
      const b = bgC.getContext("2d"); b.setTransform(dpr, 0, 0, dpr, 0, 0);
      const g = b.createRadialGradient(cx, cy, R * 0.2, cx, cy, Math.max(W, H) * 0.95);
      g.addColorStop(0, "#101a33"); g.addColorStop(0.45, "#070b17"); g.addColorStop(1, "#020308"); b.fillStyle = g; b.fillRect(0, 0, W, H);
    }
    ctx.globalAlpha = 1; ctx.drawImage(bgC, 0, 0, W, H);
    ctx.globalCompositeOperation = "lighter";
    for (const s of stars) { const x = ((s.x * W - tiltX * 18 * s.d) % W + W) % W, y = ((s.y * H - tiltY * 12 * s.d) % H + H) % H; ctx.globalAlpha = (0.25 + 0.35 * Math.sin(time * 1.3 + s.tw) ** 2) * s.d; ctx.fillStyle = "#cfd8ff"; ctx.fillRect(x, y, s.s, s.s); }
    ctx.lineCap = "round";
    for (const f of flux) {
      f.x += f.v * (reduce ? 0 : 1 / 60); if (f.x > 1.1) f.x = -0.1;
      const x = f.x * W, y = f.y * H - tiltY * 8; ctx.globalAlpha = f.a; ctx.drawImage(STREAK, x - f.l, y - 0.6, f.l, 1.2);
    }
    ctx.globalCompositeOperation = "source-over";
  }

  function trail(pts, col, w) {
    if (pts.length < 2) return; ctx.globalCompositeOperation = "lighter"; ctx.lineCap = "butt"; ctx.lineJoin = "round";
    for (let i = 1; i < pts.length; i++) { const f = i / pts.length; ctx.globalAlpha = f * f * 0.9; ctx.strokeStyle = col; ctx.lineWidth = w * (0.3 + 0.7 * f); ctx.beginPath(); ctx.moveTo(pts[i - 1][0], pts[i - 1][1]); ctx.lineTo(pts[i][0], pts[i][1]); ctx.stroke(); }
    ctx.globalCompositeOperation = "source-over";
  }

  function nucleus(cx, cy, R, heatAll) {
    // rotation: slow spin plus the pointer's tilt
    const ya = yaw + tiltX * 0.55, pa = 0.28 + tiltY * 0.35, cyw = Math.cos(ya), syw = Math.sin(ya), cp = Math.cos(pa), spt = Math.sin(pa), D = 5;
    const sc = R * reform, list = [];
    const e = fis.e, sx = 1 + e * 0.9, syz = 1 / Math.sqrt(1 + e * 0.9);
    for (const a of nuc) {
      let x, y, z;
      if (a.side) { x = a.fx; y = a.fy; z = a.fz; }   // fission: orientation frozen when the stretch began, so each half stays on its side
      else { x = a.x * cyw + a.z * syw; z = -a.x * syw + a.z * cyw; y = a.y * cp - z * spt; z = a.y * spt + z * cp; }
      const j = rb * 0.42 * (a.h + kick * 0.6) + rb * 0.06; // thermal jiggle grows with local heat
      x += Math.sin(time * 9.1 + a.ph) * j; y += Math.cos(time * 8.3 + a.ph * 1.7) * j; z += Math.sin(time * 7.7 + a.ph * 2.3) * j;
      let ox = 0, oy = 0;
      if (e > 0 || fis.sep > 0) {
        // stretch along screen x, then neck: each side pulled toward its own centre; after scission the halves fly apart and spin
        x *= sx; y *= syz; z *= syz;
        const s = a.side || (x < 0 ? -1 : 1), neck = smooth(0.35, 1, e), c = s * 0.62 * sx;
        x = lerp(x, c + (x - c) * 0.82, neck); y *= lerp(1, 0.9, neck);
        if (fis.sep > 0) { const rx = x - c, ry = y, ca = Math.cos(s * fis.rot), sa = Math.sin(s * fis.rot); x = c + rx * ca - ry * sa; y = rx * sa + ry * ca; ox = s * fis.sep; }
      }
      const k = D / (D - z); let dx = (x * k) * sc + ox, dy = (y * k) * sc + oy;
      if (a.side) { const f = 1 / (1 + fis.away), u = dx * FC - dy * FS; dy = (dx * FS + dy * FC) * f; dx = u * f; } // fission runs along a steep axis, clear of the title; halves recede as they part
      const X = cx + dx, Y = cy + dy;
      list.push({ X, Y, z, k, a });
    }
    list.sort((p, q) => p.z - q.z);
    // halo: the whole nucleus glows as it heats
    ctx.globalCompositeOperation = "lighter";
    if (fis.sep < R * 0.3) { stamp(GL.n, cx, cy, sc * 2.6, 0.14 * fis.alpha); stamp(GL.hot, cx, cy, sc * (2.2 + heatAll), (0.06 + heatAll * 0.55) * fis.alpha); }
    ctx.globalCompositeOperation = "source-over";
    const br = rb * sc * 1.08;
    for (const q of list) { const d = clamp(Math.floor((q.z + 1) * 0.5 * DEPTH.length), 0, DEPTH.length - 1); stamp((q.a.p ? SPD.p : SPD.n)[d], q.X, q.Y, br * q.k, fis.alpha * clamp(reform * 1.4, 0, 1)); }
    ctx.globalCompositeOperation = "lighter";
    for (const q of list) if (q.a.h > 0.05) stamp(GL.hot, q.X, q.Y, br * q.k * 1.8, q.a.h * 0.22 * fis.alpha);
    ctx.globalCompositeOperation = "source-over";
    return list;
  }

  function frame(dt) {
    time += dt; ct += dt;
    tiltX += (tgtX - tiltX) * (1 - Math.exp(-3 * dt)); tiltY += (tgtY - tiltY) * (1 - Math.exp(-3 * dt));
    if (pending && idle()) { const { cx, cy, R } = geo(); userHit(cx - R * 0.9, cy); }
    const isF = kind === "fission", end = isF ? F_END : T_END;
    if (ct >= end) startCycle();
    // during fission the spin stops so the split stays in the picture plane
    spin += ((isF && ct > T_IMP ? 0 : 1) - spin) * (1 - Math.exp(-2.5 * dt)); yaw += dt * 0.22 * spin;
    const { R, cx, cy, phone } = geo();
    const shx = (Math.random() - 0.5) * shake, shy = (Math.random() - 0.5) * shake; shake *= Math.exp(-6 * dt); flash *= Math.exp(-3.2 * dt); kick *= Math.exp(-4 * dt);
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    background(cx, cy, R);
    ctx.setTransform(dpr, 0, 0, dpr, shx * dpr, shy * dpr);

    // heat: a wave spreads from the impact point through the nucleus, then cools after the emission
    const since = time - imp.t, cool = isF ? 0 : smooth(T_EMIT, T_END - 0.4, ct);
    let heatAll = 0;
    for (const a of nuc) {
      if (since < 3) { const px = cx + a.x * R, py = cy + a.y * R, d = Math.hypot(px - imp.x, py - imp.y) / R, front = since * 2.6; if (front > d) a.h = Math.max(a.h, (imp.s || 1) * (1 - 0.35 * smooth(0, 1.6, front - d))); }
      if (cool > 0) a.h *= Math.exp(-dt * 2.2 * cool);
      if (isF && fis.done) a.h *= Math.exp(-dt * 1.4);              // fragments cool as they fly apart
      heatAll += a.h;
    }
    heatAll /= N;

    // fission timeline
    if (isF) {
      fis.e = smooth(F_STRETCH, F_SCISSION, ct) * (1 - smooth(F_GONE, F_GONE + 0.01, ct));
      if (ct >= F_STRETCH && ct < F_GONE && !nuc[0].side) {
        const ya = yaw + tiltX * 0.55, pa = 0.28 + tiltY * 0.35, c = Math.cos(ya), s = Math.sin(ya), cp = Math.cos(pa), sp = Math.sin(pa);
        for (const a of nuc) { const x = a.x * c + a.z * s, z0 = -a.x * s + a.z * c; a.fx = x; a.fy = a.y * cp - z0 * sp; a.fz = a.y * sp + z0 * cp; a.side = x < 0 ? -1 : 1; }
      }
      if (ct >= F_SCISSION && ct < F_GONE && !fis.done) {   // once per cycle (fis.done is cleared again at F_GONE)
        fis.done = true; flash = 0.75; flashCol = C.white; shake = 9; impact(cx, cy, 1);
        // the neck snaps: two or three neutrons and a couple of gammas leave from the middle, across the fission axis
        const r = rng(cyc * 7 + 1), sp = Math.max(W, H) * 0.32;
        for (let i = 0; i < 3; i++) { const d = FA + (i % 2 ? 1 : -1) * Math.PI / 2 + (r() - 0.5) * 1.1; parts.push({ k: "n", x: cx, y: cy, vx: Math.cos(d) * sp, vy: Math.sin(d) * sp, t0: time, trail: [] }); }
        for (let i = 0; i < 2; i++) { const d = FA + (i ? 1 : -1) * Math.PI / 2 + (r() - 0.5) * 1.6; parts.push({ k: "gam", x: cx, y: cy, vx: Math.cos(d) * sp * 2, vy: Math.sin(d) * sp * 2, t0: time, trail: [] }); }
      }
      if (fis.done) { const u = (ct - F_SCISSION) / (F_GONE - F_SCISSION); fis.sep = R * (0.1 + 0.75 * easeOut(u)); fis.rot = u * 0.45; fis.away = 0.7 * easeOut(u); }
      if (ct >= F_GONE) { fis.sep = 0; fis.e = 0; fis.away = 0; fis.done = false; for (const a of nuc) { a.side = 0; a.h = 0; } reform = 0; }
      if (ct >= F_GONE) reform = easeOut((ct - F_GONE) / (F_REFORM - F_GONE));
      fis.alpha = fis.done ? 1 - smooth(0.6, 1, (ct - F_SCISSION) / (F_GONE - F_SCISSION)) : 1;
    } else reform += (1 - reform) * (1 - Math.exp(-4 * dt));
    if (reform < 0.999 && ct >= F_GONE && isF) stamp(GL.white, cx, cy, R * 1.6 * (1 - reform), 0.5 * (1 - reform));

    // ambient rings, then the nucleus
    ctx.globalCompositeOperation = "lighter";
    for (let i = rings.length - 1; i >= 0; i--) {
      const g = rings[i], u = (time - g.t) / 1.1; if (u < 0) continue; if (u > 1) { rings.splice(i, 1); continue; }
      ctx.globalAlpha = (1 - u) * 0.7 * g.s; ctx.strokeStyle = g.col; ctx.lineWidth = 2 + 6 * (1 - u); ctx.beginPath(); ctx.arc(g.x, g.y, R * (0.1 + 2.4 * easeOut(u)) * g.s, 0, TAU); ctx.stroke();
    }
    ctx.globalCompositeOperation = "source-over";
    nucleus(cx, cy, R, heatAll + (isF ? smooth(T_IMP, F_SCISSION, ct) * 0.5 : 0));

    // the projectile and every particle in flight
    for (let i = parts.length - 1; i >= 0; i--) {
      const q = parts[i];
      if (q.k === "in") {
        const u = clamp((ct - q.t0) / q.dur, 0, 1), f = u * u * (1.6 - 0.6 * u);
        const x = lerp(q.x, q.tx, f), y = lerp(q.y, q.ty, f) + Math.sin(u * Math.PI) * -H * 0.05;
        q.trail.push([x, y]); if (q.trail.length > 26) q.trail.shift();
        trail(q.trail, C.n, R * 0.09);
        ctx.globalCompositeOperation = "lighter"; stamp(GL.n, x, y, R * 0.42, 0.9); ctx.globalCompositeOperation = "source-over";
        stamp(SP.n, x, y, rb * R * 1.25, 1);
        if (u >= 1) { parts.splice(i, 1); impact(q.tx, q.ty, 1); impacted = true; }
        continue;
      }
      const age = time - q.t0; q.x += q.vx * dt; q.y += q.vy * dt;
      if (q.k === "a") { q.vx *= 1 + dt * 0.5; q.vy *= 1 + dt * 0.5; }
      q.trail.push([q.x, q.y]); if (q.trail.length > 22) q.trail.shift();
      const off = q.x < -W * 0.3 || q.x > W * 1.3 || q.y < -H * 0.3 || q.y > H * 1.3;
      if (off && age > 0.3) { parts.splice(i, 1); continue; }
      if (q.k === "gam") {
        const d = Math.atan2(q.vy, q.vx), L = R * 0.55; ctx.globalCompositeOperation = "lighter"; ctx.globalAlpha = 1; ctx.strokeStyle = C.gam; ctx.lineWidth = 2.4; ctx.beginPath();
        for (let s = 0; s <= 30; s++) { const t = s / 30 - 1, w = Math.sin(s * 1.25 - time * 40) * R * 0.035 * (s / 30); const px = q.x + Math.cos(d) * t * L - Math.sin(d) * w, py = q.y + Math.sin(d) * t * L + Math.cos(d) * w; s ? ctx.lineTo(px, py) : ctx.moveTo(px, py); }
        ctx.stroke(); stamp(GL.gam, q.x, q.y, R * 0.45, 0.8); ctx.globalCompositeOperation = "source-over";
      } else if (q.k === "a") {
        trail(q.trail, C.a, R * 0.12); ctx.globalCompositeOperation = "lighter"; stamp(GL.a, q.x, q.y, R * 0.5, 0.7); ctx.globalCompositeOperation = "source-over";
        const s = rb * R * 1.15, o = s * 0.8, rot = age * 6;
        [[-1, -1, "p"], [1, 1, "p"], [1, -1, "n"], [-1, 1, "n"]].forEach(([u, v, k]) => { const rx = (u * Math.cos(rot) - v * Math.sin(rot)) * o * 0.7, ry = (u * Math.sin(rot) + v * Math.cos(rot)) * o * 0.7; stamp(SP[k], q.x + rx, q.y + ry, s, 1); });
      } else {
        const col = q.k === "p" ? C.p : C.n; trail(q.trail, col, R * 0.08);
        ctx.globalCompositeOperation = "lighter"; stamp(GL[q.k], q.x, q.y, R * 0.38, 0.85); ctx.globalCompositeOperation = "source-over";
        stamp(SP[q.k], q.x, q.y, rb * R * 1.2, 1);
      }
    }

    // your own neutrons
    for (let i = shots.length - 1; i >= 0; i--) {
      const s = shots[i], u = clamp((time - s.t0) / 0.55, 0, 1), f = u * u, x = lerp(s.sx, cx, f), y = lerp(s.sy, cy, f);
      s.trail.push([x, y]); if (s.trail.length > 16) s.trail.shift(); trail(s.trail, C.n, R * 0.07);
      ctx.globalCompositeOperation = "lighter"; stamp(GL.n, x, y, R * 0.32, 0.9); ctx.globalCompositeOperation = "source-over"; stamp(SP.n, x, y, rb * R * 1.1, 1);
      if (Math.hypot(x - cx, y - cy) < R * 0.95 * reform || u >= 1) { shots.splice(i, 1); if (reform > 0.5 && !userHit(x, y)) { impact(x, y, 0.75); kick = 1; } }
    }

    // flash over everything
    if (flash > 0.01) { ctx.globalCompositeOperation = "lighter"; stamp(GL[flashCol === C.gam ? "gam" : "white"], cx, cy, Math.max(W, H) * 0.6, flash * 0.55); ctx.globalCompositeOperation = "source-over"; }

    // caption under the nucleus: what just happened
    let cap = null, ca = 0;
    if (impacted && !emitted && time - imp.t > 0.15) { cap = CAP.absorbed; ca = smooth(0.15, 0.5, time - imp.t); }
    if (!isF && !emitted && ct >= T_EMIT) { emitted = true; emit(kind, cx, cy, R); }
    if (emitted || (isF && ct > F_SCISSION - 0.2)) { cap = CAP[kind]; ca = smooth(isF ? F_SCISSION - 0.2 : T_EMIT, (isF ? F_SCISSION : T_EMIT) + 0.3, ct) * (1 - smooth(end - 0.7, end - 0.1, ct)); }
    if (cap && ca > 0.01 && scrollP < 0.5 && !document.body.classList.contains("og")) {
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0); ctx.globalAlpha = ca * (1 - scrollP * 2);
      let fs = phone ? 15 : 18; ctx.font = `italic 500 ${fs}px "Source Serif 4", Georgia, serif`;
      while (ctx.measureText(tr(cap)).width > W - 28 && fs > 10) { fs -= 0.5; ctx.font = `italic 500 ${fs}px "Source Serif 4", Georgia, serif`; } // fit narrow screens
      ctx.textAlign = "center"; ctx.textBaseline = "middle";
      ctx.fillStyle = "rgba(230,236,250,0.92)"; ctx.shadowColor = "rgba(0,0,0,0.8)"; ctx.shadowBlur = 12;
      ctx.fillText(tr(cap), cx, phone ? Math.max(18, cy - R * 1.5) : Math.min(H - 30, cy + R * 1.5)); // phones: above the nucleus, clear of the title ctx.shadowBlur = 0;
    }
    // left-side shade so the title stays readable over the picture
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0); ctx.globalAlpha = 1;
    if (!phone) { const g = ctx.createLinearGradient(0, 0, W * 0.55, 0); g.addColorStop(0, "rgba(2,3,8,0.72)"); g.addColorStop(1, "rgba(2,3,8,0)"); ctx.fillStyle = g; ctx.fillRect(0, 0, W * 0.55, H); }
    else { const g = ctx.createLinearGradient(0, H * 0.45, 0, H); g.addColorStop(0, "rgba(2,3,8,0)"); g.addColorStop(1, "rgba(2,3,8,0.85)"); ctx.fillStyle = g; ctx.fillRect(0, H * 0.45, W, H * 0.55); }
  }

  // ---------- sizing, scrolling, the loop ----------
  function resize() {
    const r = cv.getBoundingClientRect(); dpr = Math.min(maxDpr, r.width < 720 ? 1.5 : 2, window.devicePixelRatio || 1); // phones: 1.5x is sharp enough and draws ~45 % fewer pixels
    W = Math.max(1, r.width); H = Math.max(1, r.height); cv.width = Math.round(W * dpr); cv.height = Math.round(H * dpr);
  }
  function onScroll() {
    const r = hero.getBoundingClientRect(); scrollP = clamp(-r.top / Math.max(1, r.height), 0, 1);
    if (copy) { copy.style.opacity = String(clamp(1 - scrollP * 2.2, 0, 1)); copy.style.transform = `translateY(${-scrollP * 60}px)`; }
  }
  let visible = true, last = 0; let maxDpr = 2, slowAcc = 0, slowN = 0;
  new IntersectionObserver((ents) => ents.forEach((en) => (visible = en.isIntersecting))).observe(hero);
  window.addEventListener("resize", () => { resize(); if (reduce) frame(0); });
  window.addEventListener("scroll", onScroll, { passive: true });
  resize(); onScroll(); startCycle();
  if (/[?&]og=1/.test(location.search)) document.body.classList.add("og"); // dev aid: render the share image (1200x630)
  const ff = /[?&]herot=([\d.]+)/.exec(location.search); // dev aid for screenshots: fast-forward the hero by N seconds
  if (ff) { cv.width = cv.height = 1; for (let s = +ff[1]; s > 0; s -= 1 / 60) frame(1 / 60); resize(); frame(0); }
  if (reduce) {
    // one still frame: the nucleus just after a neutron struck it
    ct = T_IMP + 0.6; impact(geo().cx - geo().R * 0.9, geo().cy, 1); time += 0.6; parts.length = 0; impacted = true; frame(0);
    return;
  }
  function loop(now) {
    const dt = Math.min(0.05, (now - (last || now)) / 1000); last = now;
    if (visible && dt > 0) { slowAcc += dt; slowN++; if (slowN >= 90) { if (slowAcc / slowN > 0.019 && maxDpr > 1) { maxDpr = Math.max(1, dpr - 0.5); resize(); } slowAcc = 0; slowN = 0; } } // slow device: step the resolution down
    if (visible && !document.hidden) frame(ff ? 0 : dt); // a fast-forwarded screenshot holds still
    requestAnimationFrame(loop);
  }
  requestAnimationFrame(loop);
})();
