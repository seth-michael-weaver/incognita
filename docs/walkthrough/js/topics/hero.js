/* Hero of topics.html: a cousin of the main page's hero (js/ch/intro.js), same look: a uranium-235 nucleus of 235 shaded
 * nucleons over a star field. On arrival a neutron streaks in, the impact flashes, the title flies out of it (same CSS as
 * the main hero: .hero-live), and the nucleus bursts: its nucleons fly out in groups that gather into small spinning
 * nuclei around the title, one for each part of this page, labelled with the part's own heading (read from the page,
 * so already translated). Hover a fragment to light it; click to go to that part. A click on empty space fires a neutron
 * at the nearest fragment. The nucleus tilts toward the pointer, as on the main page. Illustrative, not a fission model.
 * Dev aid: ?herot=<seconds> runs to that moment and freezes (for screenshots). */
(function () {
  "use strict";
  const hero = document.querySelector(".tp-hero"), cv = hero && hero.querySelector(".hero-cv");
  if (!cv) return;
  const ctx = cv.getContext("2d"), copy = hero.querySelector(".hero-copy");
  const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  const qT = /[?&]herot=([\d.]+)/.exec(location.search), freezeAt = qT ? +qT[1] : null;
  const TAU = Math.PI * 2, clamp = (v, a, b) => Math.max(a, Math.min(b, v)), lerp = (a, b, s) => a + (b - a) * s;
  const smooth = (e0, e1, x) => { const t = clamp((x - e0) / (e1 - e0), 0, 1); return t * t * (3 - 2 * t); };
  const easeOut = (t) => 1 - Math.pow(1 - clamp(t, 0, 1), 3);
  function rng(seed) { let s = seed >>> 0 || 1; return () => ((s = (s * 16807) % 2147483647) / 2147483647); }
  const C = { n: "#6f8cff", p: "#ff6a5c", hot: "#ffb067", white: "#fff6ea", gam: "#ffd166" };
  const SERIF = getComputedStyle(document.documentElement).getPropertyValue("--display").trim() || "Georgia, serif";

  // ---------- sprites (as in intro.js) ----------
  function hex(h) { const n = parseInt(h.slice(1), 16); return [(n >> 16) & 255, (n >> 8) & 255, n & 255]; }
  const rgba = (h, a) => { const [r, g, b] = hex(h); return `rgba(${r},${g},${b},${a})`; };
  const shade = (h, f) => { const [r, g, b] = hex(h), c = (v) => Math.min(255, (v * f) | 0).toString(16).padStart(2, "0"); return "#" + c(r) + c(g) + c(b); };
  function ballSprite(col, S = 96) { const c = document.createElement("canvas"); c.width = c.height = S; const g = c.getContext("2d"), r = S / 2;
    const gr = g.createRadialGradient(r * 0.62, r * 0.55, r * 0.04, r, r, r); gr.addColorStop(0, "#ffffff"); gr.addColorStop(0.22, col); gr.addColorStop(0.75, shade(col, 0.55)); gr.addColorStop(1, shade(col, 0.22));
    g.fillStyle = gr; g.beginPath(); g.arc(r, r, r - 1, 0, TAU); g.fill(); return c; }
  function glowSprite(col, S = 128) { const c = document.createElement("canvas"); c.width = c.height = S; const g = c.getContext("2d"), r = S / 2;
    const gr = g.createRadialGradient(r, r, 0, r, r, r); gr.addColorStop(0, rgba(col, 1)); gr.addColorStop(0.25, rgba(col, 0.45)); gr.addColorStop(1, rgba(col, 0)); g.fillStyle = gr; g.fillRect(0, 0, S, S); return c; }
  const DEPTH = [0.5, 0.72, 0.9, 1.08];
  const SPD = { n: DEPTH.map((f) => ballSprite(shade(C.n, f))), p: DEPTH.map((f) => ballSprite(shade(C.p, f))) };
  const GL = { n: glowSprite(C.n), hot: glowSprite(C.hot), white: glowSprite(C.white), gam: glowSprite(C.gam) };
  const stamp = (img, x, y, r, a = 1) => { if (a <= 0.003 || r <= 0.2) return; ctx.globalAlpha = Math.min(1, a); ctx.drawImage(img, x - r, y - r, 2 * r, 2 * r); };

  // ---------- the nucleus: U-235 packed in a unit sphere (relaxed once, as on the main page) ----------
  const N = 235, Z = 92, rb = Math.cbrt(0.62 / N), nuc = [];
  (function pack() { const r = rng(11);
    for (let i = 0; i < N; i++) { let x, y, z; do { x = r() * 2 - 1; y = r() * 2 - 1; z = r() * 2 - 1; } while (x * x + y * y + z * z > 1); nuc.push({ x, y, z, p: false, ph: r() * 100 }); }
    const d0 = 2 * rb * 0.97, lim = 1 - rb;
    for (let it = 0; it < 60; it++) { for (let i = 0; i < N; i++) for (let j = i + 1; j < N; j++) { const a = nuc[i], b = nuc[j], dx = b.x - a.x, dy = b.y - a.y, dz = b.z - a.z, d = Math.sqrt(dx * dx + dy * dy + dz * dz) || 1e-6;
        if (d < d0) { const k = (d0 - d) / d * 0.5; a.x -= dx * k; a.y -= dy * k; a.z -= dz * k; b.x += dx * k; b.y += dy * k; b.z += dz * k; } }
      for (const a of nuc) { const d = Math.sqrt(a.x * a.x + a.y * a.y + a.z * a.z); if (d > lim) { a.x *= lim / d; a.y *= lim / d; a.z *= lim / d; } } }
    const idx = nuc.map((_, i) => i); for (let i = N - 1; i > 0; i--) { const j = Math.floor(r() * (i + 1)); [idx[i], idx[j]] = [idx[j], idx[i]]; }
    for (let k = 0; k < Z; k++) nuc[idx[k]].p = true;
  })();

  // ---------- the parts of the page (headings read from the page) ----------
  // the hero runs before the page applies its translations, so each heading's text is looked up by its i18n key
  const PARTS = [...document.querySelectorAll("main > .part-head")].map((el) => { const h = el.querySelector("h2") || el, en = h.textContent.trim(), k = h.dataset && h.dataset.i18n;
    return { id: el.id, name: k && window.WT && WT.ui ? WT.ui(k, en) : en }; });
  const NP = Math.max(1, PARTS.length);

  // ---------- background (as in intro.js) ----------
  const R0 = rng(5), stars = [], flux = [];
  for (let i = 0; i < 260; i++) stars.push({ x: R0(), y: R0(), d: 0.2 + R0() * 0.8, s: 0.4 + R0() * 1.3, tw: R0() * TAU });
  for (let i = 0; i < 70; i++) flux.push({ x: R0(), y: R0(), v: 0.04 + R0() * 0.12, l: 10 + R0() * 40, a: 0.08 + R0() * 0.22 });
  const STREAK = (() => { const c = document.createElement("canvas"); c.width = 64; c.height = 2; const g = c.getContext("2d"), gr = g.createLinearGradient(0, 0, 64, 0); gr.addColorStop(0, rgba(C.n, 0)); gr.addColorStop(1, rgba(C.n, 1)); g.fillStyle = gr; g.fillRect(0, 0, 64, 2); return c; })();

  // ---------- timeline ----------
  const T_IMP = 1.6, T_BURST = 2.5, T_LAND = 4.6, FS = 0.62; // FS: a fragment's drawing scale against the parent nucleus   // neutron arrives, nucleus heats and bulges, fragments fly and settle
  let W = 0, H = 0, dpr = 1, phone = false, time = 0, tiltX = 0, tiltY = 0, tgtX = 0, tgtY = 0, flash = 0, shake = 0, live = false, hover = -1;
  const rings = [], shots = [];
  let frags = [], cx0 = 0, cy0 = 0, R = 100, inTrail = [];

  function layout() {
    const b = hero.getBoundingClientRect(); W = Math.max(320, b.width); H = Math.max(400, b.height); phone = W < 720;
    dpr = Math.min(window.devicePixelRatio || 1, 2); cv.width = Math.round(W * dpr); cv.height = Math.round(H * dpr);
    const h1 = hero.querySelector("h1"), top = phone && h1 ? Math.max(160, copy.offsetTop + h1.offsetTop - 20) : H;
    cx0 = W / 2; cy0 = phone ? top * 0.5 : H * 0.43; R = phone ? Math.min(W * 0.2, top * 0.24) : Math.min(W, H) * 0.24;
    // where the fragments settle: an ellipse around the title (desktop) or a grid above it (phones)
    frags = PARTS.map((p, i) => {
      let x, y;
      if (phone) { const col = i % 2, row = Math.floor(i / 2), rows = Math.ceil(NP / 2); x = W * (col ? 0.72 : 0.28); y = lerp(top * 0.14, top * 0.86, rows > 1 ? row / (rows - 1) : 0.5); }
      else { const nTop = Math.ceil(NP / 2), top1 = i < nTop, k = top1 ? i : i - nTop, n = top1 ? nTop : NP - nTop; // a row above the title and a row below it
        x = W * lerp(0.2, 0.8, n > 1 ? k / (n - 1) : 0.5); y = H * (top1 ? 0.17 : 0.64); }
      return Object.assign({}, p, { x, y, dir: Math.atan2(y - cy0, x - cx0), members: [], r: 0, flash: 0, ph: i * 1.7 });
    });
    // each nucleon joins the fragment whose direction is closest to its own side of the nucleus
    nuc.forEach((a) => { const da = Math.atan2(a.y, a.x); let best = 0, bd = 9; frags.forEach((f, i) => { const d = Math.abs(Math.atan2(Math.sin(da - f.dir), Math.cos(da - f.dir))); if (d < bd) { bd = d; best = i; } }); a.f = null; frags[best] && frags[best].members.push(a); });
    // balance: move nucleons from the biggest groups to the smallest so every fragment looks alike
    const angTo = (a, t) => Math.abs(Math.atan2(Math.sin(Math.atan2(a.y, a.x) - t), Math.cos(Math.atan2(a.y, a.x) - t)));
    for (let k = 0; k < 400 && frags.length; k++) { let mx = 0, mn = 0; frags.forEach((f, i) => { if (f.members.length > frags[mx].members.length) mx = i; if (f.members.length < frags[mn].members.length) mn = i; });
      if (frags[mx].members.length - frags[mn].members.length <= 1) break; const fm = frags[mx].members, tgt = frags[mn].dir; let bi = 0, bd = 9;
      fm.forEach((a, i) => { const d = angTo(a, tgt); if (d < bd) { bd = d; bi = i; } }); frags[mn].members.push(fm.splice(bi, 1)[0]); }
    // each fragment's own compact shape: its nucleons' offsets from their centre, squeezed into a small ball
    frags.forEach((f, fi) => { const n = f.members.length || 1, want = Math.cbrt(n / N), r2 = rng(97 + fi), d0 = 2 * rb * 0.97, lim = want - rb;
      f.members.forEach((a) => { let x, y, z; do { x = r2() * 2 - 1; y = r2() * 2 - 1; z = r2() * 2 - 1; } while (x * x + y * y + z * z > 1); a.ox = x * lim; a.oy = y * lim; a.oz = z * lim; a.f = f; });
      const m = f.members; for (let it = 0; it < 40; it++) { for (let i = 0; i < m.length; i++) for (let j = i + 1; j < m.length; j++) { const A = m[i], B = m[j], dx = B.ox - A.ox, dy = B.oy - A.oy, dz = B.oz - A.oz, d = Math.sqrt(dx * dx + dy * dy + dz * dz) || 1e-6;
          if (d < d0) { const k = (d0 - d) / d * 0.5; A.ox -= dx * k; A.oy -= dy * k; A.oz -= dz * k; B.ox += dx * k; B.oy += dy * k; B.oz += dz * k; } }
        for (const A of m) { const d = Math.hypot(A.ox, A.oy, A.oz); if (d > lim) { A.ox *= lim / d; A.oy *= lim / d; A.oz *= lim / d; } } }
      f.r = R * FS * want; });
  }

  // ---------- pointer ----------
  const labelSize = () => (phone ? 15 : clamp(Math.min(W / 60, H / 30), 17, 26));
  const labelY = (f) => f.y + f.r * (phone ? 1.3 : 1) + labelSize() * 1.1;
  function fragAt(x, y) { for (let i = 0; i < frags.length; i++) { const f = frags[i]; if (Math.hypot(x - f.x, y - f.y) < f.r * 1.4 + 10) return i;
      ctx.font = `600 ${labelSize()}px ${SERIF}`; const w = ctx.measureText(f.name).width, ly = labelY(f); if (x > f.x - w / 2 - 8 && x < f.x + w / 2 + 8 && y > ly - 16 && y < ly + 16) return i; } return -1; }
  hero.addEventListener("pointermove", (e) => { const r = cv.getBoundingClientRect(), x = e.clientX - r.left, y = e.clientY - r.top; tgtX = (x / r.width - 0.5) * 2; tgtY = (y / r.height - 0.5) * 2;
    if (e.pointerType !== "touch") { hover = time > T_LAND - 0.3 ? fragAt(x, y) : -1; cv.style.cursor = hover >= 0 ? "pointer" : "crosshair"; } });
  hero.addEventListener("pointerleave", () => { tgtX = 0; tgtY = 0; hover = -1; });
  cv.addEventListener("click", (e) => { const r = cv.getBoundingClientRect(), x = e.clientX - r.left, y = e.clientY - r.top, i = fragAt(x, y);
    if (i >= 0 && time > T_LAND - 0.3) { const el = document.getElementById(frags[i].id); frags[i].flash = 1; if (el) el.scrollIntoView({ behavior: reduce ? "auto" : "smooth", block: "start" }); return; }
    let best = 0, bd = 1e9; frags.forEach((f, k) => { const d = Math.hypot(f.x - x, f.y - y); if (d < bd) { bd = d; best = k; } }); // empty space: a neutron flies to the nearest fragment
    if (frags[best]) shots.push({ sx: x, sy: y, t0: time, to: best, trail: [] }); if (reduce) draw(0); });

  // ---------- drawing ----------
  let bgC = null, bgKey = "";
  function background() {
    const key = W + "x" + H + "@" + dpr;
    if (key !== bgKey) { bgKey = key; bgC = bgC || document.createElement("canvas"); bgC.width = Math.round(W * dpr); bgC.height = Math.round(H * dpr);
      const b = bgC.getContext("2d"); b.setTransform(dpr, 0, 0, dpr, 0, 0); const g = b.createRadialGradient(cx0, cy0, R * 0.2, cx0, cy0, Math.max(W, H) * 0.95);
      g.addColorStop(0, "#101a33"); g.addColorStop(0.45, "#070b17"); g.addColorStop(1, "#020308"); b.fillStyle = g; b.fillRect(0, 0, W, H); }
    ctx.globalAlpha = 1; ctx.drawImage(bgC, 0, 0, W, H);
    ctx.globalCompositeOperation = "lighter";
    for (const s of stars) { const x = ((s.x * W - tiltX * 18 * s.d) % W + W) % W, y = ((s.y * H - tiltY * 12 * s.d) % H + H) % H; ctx.globalAlpha = (0.25 + 0.35 * Math.sin(time * 1.3 + s.tw) ** 2) * s.d; ctx.fillStyle = "#cfd8ff"; ctx.fillRect(x, y, s.s, s.s); }
    for (const f of flux) { const x = ((f.x + f.v * time) % 1.2 - 0.1) * W, y = f.y * H - tiltY * 8; ctx.globalAlpha = f.a; ctx.drawImage(STREAK, x - f.l, y - 0.6, f.l, 1.2); }
    ctx.globalCompositeOperation = "source-over";
  }
  function trail(pts, col, w) { if (pts.length < 2) return; ctx.globalCompositeOperation = "lighter"; ctx.lineCap = "round";
    for (let i = 1; i < pts.length; i++) { const f = i / pts.length; ctx.globalAlpha = f * f * 0.9; ctx.strokeStyle = col; ctx.lineWidth = w * (0.3 + 0.7 * f); ctx.beginPath(); ctx.moveTo(pts[i - 1][0], pts[i - 1][1]); ctx.lineTo(pts[i][0], pts[i][1]); ctx.stroke(); }
    ctx.globalCompositeOperation = "source-over"; }

  function draw(dt) {
    tiltX += (tgtX - tiltX) * Math.min(1, dt * 3); tiltY += (tgtY - tiltY) * Math.min(1, dt * 3);
    flash *= Math.exp(-dt * 3.5); shake *= Math.exp(-dt * 6);
    const sx = (Math.random() - 0.5) * shake, sy = (Math.random() - 0.5) * shake;
    ctx.setTransform(dpr, 0, 0, dpr, dpr * sx, dpr * sy); ctx.globalCompositeOperation = "source-over";
    background();
    // the incoming neutron
    if (time < T_IMP) { const u = easeOut(time / T_IMP), x = lerp(-W * 0.1, cx0 - R * 0.9, u), y = lerp(cy0 - H * 0.16, cy0 + R * 0.08, u); inTrail.push([x, y]); if (inTrail.length > 22) inTrail.shift();
      trail(inTrail, C.n, 4); ctx.globalCompositeOperation = "lighter"; stamp(GL.n, x, y, 26, 0.9); ctx.globalCompositeOperation = "source-over"; stamp(SPD.n[3], x, y, rb * R * 1.1); }
    else if (!live) { flash = 1; shake = 12; rings.push({ x: cx0 - R * 0.9, y: cy0 + R * 0.08, t: time, col: C.white }, { x: cx0, y: cy0, t: time + 0.25, col: C.hot }); goLive(); }
    // the nucleus heats and bulges, then bursts; each nucleon flies to its fragment along a gentle arc
    const heat = smooth(T_IMP, T_BURST, time), go = easeOut((time - T_BURST) / (T_LAND - T_BURST)), ya = 0.4 + time * 0.25 + tiltX * 0.55, pa = 0.28 + tiltY * 0.35;
    const cyw = Math.cos(ya), syw = Math.sin(ya), cp = Math.cos(pa), spt = Math.sin(pa), D = 5, list = [], fsc = R * FS * (phone ? 1.3 : 1);
    for (const a of nuc) {
      const f = a.f; if (!f) continue;
      let x = a.x * cyw + a.z * syw, z = -a.x * syw + a.z * cyw, y = a.y * cp - z * spt; z = a.y * spt + z * cp;
      const j = rb * (0.06 + 0.5 * heat * (1 - go)), bulge = 1 + 0.12 * heat * (1 - go);
      x = (x + Math.sin(time * 9.1 + a.ph) * j) * bulge; y = (y + Math.cos(time * 8.3 + a.ph * 1.7) * j) * bulge;
      const k0 = D / (D - z), X0 = cx0 + x * k0 * R, Y0 = cy0 + y * k0 * R;
      const fy = 0.6 * time + f.ph + tiltX * 0.4, c2 = Math.cos(fy), s2 = Math.sin(fy); // each fragment spins on its own
      let ux = a.ox * c2 + a.oz * s2, uz = -a.ox * s2 + a.oz * c2; const uy = a.oy * cp - uz * spt; uz = a.oy * spt + uz * cp;
      const bob = Math.sin(time * 0.9 + f.ph) * 5, k1 = D / (D - uz), X1 = f.x + ux * k1 * fsc + tiltX * 10, Y1 = f.y + uy * k1 * fsc + bob + tiltY * 7;
      const mid = Math.sin(Math.PI * go) * R * 0.15, nx = -Math.sin(f.dir), ny = Math.cos(f.dir);
      list.push({ X: lerp(X0, X1, go) + nx * mid, Y: lerp(Y0, Y1, go) + ny * mid, z: lerp(z, uz, go), a, k: lerp(k0, k1, go), sc: lerp(R, fsc, go) });
    }
    list.sort((p, q) => p.z - q.z);
    ctx.globalCompositeOperation = "lighter"; // halos: the whole nucleus before the burst, each fragment after
    if (go < 1) stamp(GL.hot, cx0, cy0, R * (2.2 + heat), (0.06 + heat * 0.5) * (1 - go));
    if (go < 0.3) stamp(GL.n, cx0, cy0, R * 2.6, 0.14 * (1 - go / 0.3));
    frags.forEach((f, i) => { const on = i === hover, fx = f.x + tiltX * 10, fy = f.y + tiltY * 7; stamp(GL.n, fx, fy, f.r * (on ? 4 : 3), go * (on ? 0.6 : 0.22) + f.flash * 0.6); stamp(GL.hot, fx, fy, f.r * 2.4, f.flash * 0.7 + (1 - go) * go * 0.8); f.flash *= Math.exp(-dt * 2.5); });
    ctx.globalCompositeOperation = "source-over";
    for (const q of list) { const d = clamp(Math.floor((q.z + 1) * 0.5 * DEPTH.length), 0, DEPTH.length - 1); stamp((q.a.p ? SPD.p : SPD.n)[d], q.X, q.Y, rb * q.sc * 1.08 * q.k); }
    ctx.globalCompositeOperation = "lighter"; // flash and rings
    if (flash > 0.01) stamp(GL.white, cx0, cy0, Math.max(W, H) * 0.7, flash * 0.5);
    for (let i = rings.length - 1; i >= 0; i--) { const g = rings[i], u = (time - g.t) / 1.2; if (u > 1) { rings.splice(i, 1); continue; } if (u < 0) continue;
      ctx.globalAlpha = (1 - u) * 0.7; ctx.strokeStyle = g.col; ctx.lineWidth = 3 * (1 - u) + 0.5; ctx.beginPath(); ctx.arc(g.x, g.y, 10 + u * R * 2.4, 0, TAU); ctx.stroke(); }
    for (let i = shots.length - 1; i >= 0; i--) { const s = shots[i], f = frags[s.to], u = (time - s.t0) / 0.7; // neutrons fired by clicks
      if (!f || u > 1) { if (f) { f.flash = 1; rings.push({ x: f.x, y: f.y, t: time, col: C.hot }); } shots.splice(i, 1); continue; }
      const x = lerp(s.sx, f.x, easeOut(u)), y = lerp(s.sy, f.y, easeOut(u)); s.trail.push([x, y]); if (s.trail.length > 16) s.trail.shift(); trail(s.trail, C.n, 3); ctx.globalCompositeOperation = "lighter"; stamp(GL.n, x, y, 18, 0.9); }
    ctx.globalCompositeOperation = "source-over"; ctx.globalAlpha = 1;
    if (go > 0.6) { const fs = labelSize(); ctx.font = `600 ${fs}px ${SERIF}`; ctx.textAlign = "center"; ctx.textBaseline = "middle"; // the part names under the fragments
      frags.forEach((f, i) => { const on = i === hover, a = smooth(0.6, 1, go), lx = f.x + tiltX * 10, ly = labelY(f) + tiltY * 7;
        ctx.globalAlpha = a * (on ? 1 : 0.88); ctx.shadowColor = "rgba(2,3,8,.9)"; ctx.shadowBlur = 10; ctx.fillStyle = on ? "#ffffff" : "#e8ecff"; ctx.fillText(f.name, lx, ly); ctx.shadowBlur = 0;
        if (on) { const w = ctx.measureText(f.name).width; ctx.strokeStyle = "rgba(180,200,255,.85)"; ctx.lineWidth = 1.5; ctx.beginPath(); ctx.moveTo(lx - w / 2, ly + fs * 0.62); ctx.lineTo(lx + w / 2, ly + fs * 0.62); ctx.stroke(); } });
      ctx.globalAlpha = 1; }
  }

  // ---------- loop ----------
  function goLive() { if (live) return; live = true; hero.classList.add("hero-live"); setTimeout(() => document.body.classList.add("hero-done"), 2600); }
  let last = 0, vis = true;
  new IntersectionObserver((es) => es.forEach((en) => (vis = en.isIntersecting))).observe(hero);
  function loop(now) { const dt = Math.min(0.05, last ? (now - last) / 1000 : 0.016); last = now;
    if (vis && !document.hidden) { time += dt; draw(dt); const sc = clamp(window.scrollY / (H * 0.8), 0, 1); if (copy) copy.style.opacity = String(clamp(1 - sc * 1.6, 0, 1)); }
    requestAnimationFrame(loop); }
  let relayT = 0; window.addEventListener("resize", () => { clearTimeout(relayT); relayT = setTimeout(() => { layout(); bgKey = ""; if (reduce || freezeAt != null) draw(0); }, 120); });
  (document.fonts && document.fonts.ready ? document.fonts.ready : Promise.resolve()).then(() => {
    layout();
    if (freezeAt != null || reduce) { const end = freezeAt != null ? freezeAt : T_LAND + 1; for (time = 0; time < end; time += 1 / 30) draw(1 / 30); goLive(); }
    else requestAnimationFrame(loop);
  });
})();
