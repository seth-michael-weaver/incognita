/* Hero of topics.html: a word cloud of hopeful things nuclear science does, each word with its own small picture
 * (Seth 2026-11-06: "a word-cloud with pictures on topics of optimistic things for nuclear").
 * The words float around the title without covering it (and away from the caption row), drift gently and follow the
 * pointer a little. Hover (or tap, on phones) shows one short, sourced fact; where a lesson on this page covers the topic,
 * a click scrolls to it. "Start a chain" sends a ripple through the cloud.
 * Facts (rounded, sourced):
 *   ~9 % of world electricity from nuclear in 2023 (IEA, World Energy Outlook 2024; IAEA PRIS); no CO2 from the plant itself.
 *   Voyager 1 and 2 (launched 1977) run on plutonium-238 radioisotope generators (NASA JPL).
 *   Curiosity (2012) and Perseverance (2021) Mars rovers: MMRTG plutonium-238 power (NASA).
 *   Tc-99m: about 40 million procedures a year (OECD-NEA 2019, "The Supply of Medical Radioisotopes").
 *   Sterile insect technique: radiation-sterilised screwworm flies eradicated the pest from the USA, Mexico and Central America
 *   (IAEA/FAO Joint Division; USDA).
 *   BN-350 (Aktau, Kazakhstan) desalinated Caspian water 1973-1999 (IAEA TECDOC-1235; WNA).
 *   Food irradiation kills bacteria and insects without making food radioactive (WHO, FAO/IAEA).
 *   Russian nuclear icebreakers keep the Northern Sea Route open (Rosatomflot; WNA "Nuclear-powered ships").
 * Dev aid: ?herot=<seconds> runs to that moment and freezes (for screenshots); ?herohover=<i> shows item i's fact. */
(function () {
  "use strict";
  const hero = document.querySelector(".tp-hero"), cv = hero && hero.querySelector(".hero-cv");
  if (!cv) return;
  const ctx = cv.getContext("2d"), copy = hero.querySelector(".hero-copy");
  const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  const qT = /[?&]herot=([\d.]+)/.exec(location.search), freezeAt = qT ? +qT[1] : null;
  const qH = /[?&]herohover=(\d+)/.exec(location.search);
  const TAU = Math.PI * 2, clamp = (v, a, b) => Math.max(a, Math.min(b, v)), lerp = (a, b, s) => a + (b - a) * s;
  const ease = (u) => 1 - Math.pow(1 - clamp(u, 0, 1), 3);
  const T = (k, en) => (window.WT && WT.ui ? WT.ui(k, en) : en);
  const SERIF = getComputedStyle(document.documentElement).getPropertyValue("--display").trim() || "Georgia, serif";
  const SANS = getComputedStyle(document.documentElement).getPropertyValue("--sans").trim() || "system-ui, sans-serif";

  // ---------- the topics: [key, words, tier (0 big .. 2 small), colour, picture, link (#id or null), fact] ----------
  const C = { gold: "#f5c04d", blue: "#5fb0ff", green: "#3fd3a8", red: "#ff7e72", violet: "#b392ff", orange: "#ff9b55", cyan: "#62e0f0" };
  const ITEMS = [
    ["power", "Clean electricity", 0, C.gold, "bolt", "reactor", "About 9 % of the world's electricity, with no CO₂ from the plant"],
    ["cancer", "Cancer treatment", 0, C.red, "beams", "everyday-2", "Beams from many sides meet on the tumour"],
    ["fusion", "Fusion energy", 0, C.orange, "sun", "fusion", "Joining light nuclei, the way the Sun shines"],
    ["space", "Voyager's power", 1, C.violet, "probe", null, "Plutonium-238 has powered Voyager 1 and 2 since 1977"],
    ["pet", "PET scans", 1, C.cyan, "ring", "everyday-1", "Two gamma rays, back to back, show where the tracer went"],
    ["stars", "Stardust", 1, C.gold, "star", "stars", "Most heavy elements were built in stars by neutron capture"],
    ["water", "Clean water", 1, C.blue, "drop", null, "Kazakhstan's BN-350 reactor desalinated sea water for 26 years"],
    ["crops", "Saving crops", 1, C.green, "fly", null, "Sterilised flies wiped out the screwworm pest across North America"],
    ["mars", "Mars rovers", 1, C.red, "rover", null, "Curiosity and Perseverance run on plutonium-238 heat"],
    ["isotopes", "Medical isotopes", 2, C.cyan, "vial", "everyday-3", "Technetium-99m: about 40 million scans a year"],
    ["dating", "Carbon dating", 2, C.green, "leaf", "everyday-4", "Carbon-14 tells the age of anything that once lived"],
    ["smr", "Small modular reactors", 2, C.blue, "module", "rwater-5", "Factory-built reactors, small enough to ship"],
    ["recycle", "Recycling fuel", 2, C.green, "cycle", "fuelcycle-5", "Used fuel still holds uranium and plutonium to burn again"],
    ["food", "Safer food", 2, C.orange, "apple", null, "Irradiation kills bacteria without making food radioactive"],
    ["ice", "Arctic icebreakers", 2, C.cyan, "ship", null, "Nuclear icebreakers keep the Northern Sea Route open"],
    ["build", "Build a reactor", 2, C.violet, "atom", "sandbox", "Pick fuel, moderator and size: will it run?"],
    ["breed", "Breeding fuel", 2, C.orange, "spark", "breeding", "Turning uranium-238 into new fuel"],
    ["smoke", "Smoke alarms", 2, C.red, "alarm", "everyday-5", "A speck of americium guards millions of homes"],
  ].map(([key, words, tier, col, pic, link, fact]) => ({ key, words: T("tp_w_" + key, words), tier, col, pic, link, fact: T("tp_f_" + key, fact) }));

  // ---------- pictures: drawn in a unit circle (radius 1), white strokes on a coloured disc ----------
  function picture(x, kind) {
    x.lineCap = "round"; x.lineJoin = "round"; x.strokeStyle = "#fff"; x.fillStyle = "#fff"; x.lineWidth = 0.11;
    const P = (pts, close, fill) => { x.beginPath(); pts.forEach(([a, b], i) => (i ? x.lineTo(a, b) : x.moveTo(a, b))); if (close) x.closePath(); fill ? x.fill() : x.stroke(); };
    const O = (cx, cy, r, fill) => { x.beginPath(); x.arc(cx, cy, r, 0, TAU); fill ? x.fill() : x.stroke(); };
    switch (kind) {
      case "bolt": P([[0.12, -0.62], [-0.3, 0.08], [0.02, 0.08], [-0.12, 0.62], [0.32, -0.12], [0, -0.12]], true, true); break;
      case "beams": for (let k = 0; k < 5; k++) { const a = k * TAU / 5 - Math.PI / 2; x.globalAlpha = 0.75; P([[Math.cos(a) * 0.62, Math.sin(a) * 0.62], [Math.cos(a) * 0.18, Math.sin(a) * 0.18]]); } x.globalAlpha = 1; O(0, 0, 0.16, true); break;
      case "sun": O(0, 0, 0.26, true); for (let k = 0; k < 8; k++) { const a = k * TAU / 8; P([[Math.cos(a) * 0.38, Math.sin(a) * 0.38], [Math.cos(a) * 0.58, Math.sin(a) * 0.58]]); } break;
      case "probe": O(-0.12, 0.08, 0.28); P([[-0.3, -0.14], [0.06, 0.3]]); P([[0.12, -0.08], [0.6, -0.5]]); P([[0.2, -0.02], [0.46, 0.24]]); O(0.6, -0.5, 0.07, true); break;
      case "ring": for (let k = 0; k < 12; k++) { const a = k * TAU / 12; x.fillRect(Math.cos(a) * 0.52 - 0.06, Math.sin(a) * 0.52 - 0.06, 0.12, 0.12); } P([[-0.42, 0.24], [0.42, -0.24]]); O(0.08, -0.05, 0.08, true); break;
      case "star": { const pts = []; for (let k = 0; k < 10; k++) { const a = k * TAU / 10 - Math.PI / 2, r = k % 2 ? 0.25 : 0.6; pts.push([Math.cos(a) * r, Math.sin(a) * r]); } P(pts, true, true); break; }
      case "drop": x.beginPath(); x.moveTo(0, -0.6); x.bezierCurveTo(0.12, -0.3, 0.42, -0.02, 0.42, 0.18); x.arc(0, 0.18, 0.42, 0, Math.PI); x.bezierCurveTo(-0.42, -0.02, -0.12, -0.3, 0, -0.6); x.fill(); break;
      case "fly": x.save(); x.scale(1, 0.75); O(0, 0.1, 0.18, true); x.restore(); x.globalAlpha = 0.8; x.beginPath(); x.ellipse(-0.24, -0.16, 0.26, 0.13, -0.5, 0, TAU); x.fill(); x.beginPath(); x.ellipse(0.24, -0.16, 0.26, 0.13, 0.5, 0, TAU); x.fill(); x.globalAlpha = 1; P([[-0.08, -0.06], [-0.2, -0.46]]); P([[0.08, -0.06], [0.2, -0.46]]); break;
      case "rover": x.fillRect(-0.44, -0.1, 0.88, 0.24); O(-0.32, 0.32, 0.13, true); O(0, 0.32, 0.13, true); O(0.32, 0.32, 0.13, true); P([[0.24, -0.1], [0.24, -0.44], [0.42, -0.44]]); break;
      case "vial": P([[-0.16, -0.56], [-0.16, 0.4], [0, 0.56], [0.16, 0.4], [0.16, -0.56]]); x.fillRect(-0.24, -0.62, 0.48, 0.1); x.globalAlpha = 0.85; x.fillRect(-0.12, 0.02, 0.24, 0.38); x.globalAlpha = 1; break;
      case "leaf": x.beginPath(); x.moveTo(-0.5, 0.5); x.quadraticCurveTo(-0.5, -0.5, 0.5, -0.5); x.quadraticCurveTo(0.5, 0.5, -0.5, 0.5); x.fill(); x.strokeStyle = "rgba(0,0,0,.35)"; P([[-0.42, 0.42], [0.3, -0.3]]); break;
      case "module": x.strokeRect(-0.4, -0.5, 0.8, 1.0); x.strokeRect(-0.22, -0.3, 0.44, 0.44); P([[-0.4, 0.3], [0.4, 0.3]]); break;
      case "cycle": for (let k = 0; k < 3; k++) { const a0 = k * TAU / 3 - 0.2; x.beginPath(); x.arc(0, 0, 0.46, a0, a0 + 1.6); x.stroke(); const a1 = a0 + 1.6, hx = Math.cos(a1) * 0.46, hy = Math.sin(a1) * 0.46, tx = -Math.sin(a1), ty = Math.cos(a1);
          P([[hx + tx * 0.16 - Math.cos(a1) * 0.12, hy + ty * 0.16 - Math.sin(a1) * 0.12], [hx + tx * 0.02, hy + ty * 0.02], [hx + tx * 0.16 + Math.cos(a1) * 0.12, hy + ty * 0.16 + Math.sin(a1) * 0.12]]); } break;
      case "apple": O(-0.14, 0.12, 0.34, true); O(0.14, 0.12, 0.34, true); P([[0, -0.2], [0.06, -0.5]]); x.beginPath(); x.ellipse(0.2, -0.46, 0.16, 0.08, -0.4, 0, TAU); x.fill(); break;
      case "ship": P([[-0.58, 0.06], [0.58, 0.06], [0.36, 0.4], [-0.44, 0.4]], true, true); x.fillRect(-0.24, -0.24, 0.42, 0.28); x.fillRect(0.0, -0.46, 0.1, 0.24); P([[-0.66, 0.54], [0.66, 0.54]]); break;
      case "atom": for (let k = 0; k < 3; k++) { x.save(); x.rotate(k * Math.PI / 3); x.beginPath(); x.ellipse(0, 0, 0.6, 0.22, 0, 0, TAU); x.stroke(); x.restore(); } O(0, 0, 0.12, true); break;
      case "spark": O(-0.2, 0.08, 0.2, true); O(0.28, -0.22, 0.12, true); P([[-0.02, -0.02], [0.18, -0.14]]); for (let k = 0; k < 6; k++) { const a = k * TAU / 6; P([[0.28 + Math.cos(a) * 0.2, -0.22 + Math.sin(a) * 0.2], [0.28 + Math.cos(a) * 0.32, -0.22 + Math.sin(a) * 0.32]]); } break;
      case "alarm": O(0, 0.08, 0.44); O(0, 0.08, 0.16, true); P([[-0.56, -0.5], [-0.36, -0.36]]); P([[0.56, -0.5], [0.36, -0.36]]); P([[0, -0.6], [0, -0.44]]); break;
    }
  }
  function shade(hex, f) { const n = parseInt(hex.slice(1), 16); return `rgb(${Math.round(((n >> 16) & 255) * f)},${Math.round(((n >> 8) & 255) * f)},${Math.round((n & 255) * f)})`; }
  function hexA(hex, a) { const n = parseInt(hex.slice(1), 16); return `rgba(${(n >> 16) & 255},${(n >> 8) & 255},${n & 255},${a})`; }
  // each item's badge is drawn once into its own small canvas (crisp at the device pixel ratio)
  function badge(it, R) {
    const s = Math.ceil(R * 2.6 * dpr), c = document.createElement("canvas"); c.width = c.height = s; const x = c.getContext("2d");
    x.translate(s / 2, s / 2); x.scale(s / 2.6, s / 2.6);
    const g = x.createRadialGradient(-0.35, -0.4, 0.1, 0, 0, 1); g.addColorStop(0, "#ffffff"); g.addColorStop(0.18, it.col); g.addColorStop(1, shade(it.col, 0.42));
    x.fillStyle = g; x.beginPath(); x.arc(0, 0, 1, 0, TAU); x.fill();
    x.strokeStyle = "rgba(255,255,255,.35)"; x.lineWidth = 0.05; x.stroke();
    x.save(); x.scale(0.78, 0.78); picture(x, it.pic); x.restore();
    return c;
  }

  // the hub: a nucleus (protons red, neutrons blue), drawn once
  function nucleusSprite(size) {
    const c = document.createElement("canvas"); c.width = c.height = size; const x = c.getContext("2d"), R = size * 0.36, r = R * 0.24, pts = [];
    let q = 7; const rn = () => ((q = (q * 16807) % 2147483647) / 2147483647);
    for (let i = 0; i < 60; i++) { const u = rn(), v = rn(), w = rn(), rr = R * Math.cbrt(u) * 0.86, th = TAU * v, ph = Math.acos(2 * w - 1); pts.push({ x: rr * Math.sin(ph) * Math.cos(th), y: rr * Math.sin(ph) * Math.sin(th), z: rr * Math.cos(ph), p: rn() < 0.42 }); }
    pts.sort((a, b) => a.z - b.z);
    for (const p of pts) { const cx = size / 2 + p.x, cy = size / 2 + p.y, lit = 0.55 + 0.45 * (p.z / R + 1) / 2, base = p.p ? [236, 92, 78] : [86, 120, 230];
      const g = x.createRadialGradient(cx - r * 0.35, cy - r * 0.4, r * 0.08, cx, cy, r);
      g.addColorStop(0, `rgba(255,255,255,${(0.95 * lit).toFixed(2)})`); g.addColorStop(0.25, `rgb(${base.map((v) => Math.round(v * (0.75 + 0.35 * lit))).join(",")})`); g.addColorStop(1, `rgb(${base.map((v) => Math.round(v * 0.28)).join(",")})`);
      x.fillStyle = g; x.beginPath(); x.arc(cx, cy, r, 0, TAU); x.fill(); }
    return c;
  }
  const NUC = nucleusSprite(256);
  let hubX = 0, hubY = 0, hubR = 60;

  // ---------- layout: a spiral packing around the title, avoiding the text ----------
  let W = 0, H = 0, dpr = 1, phone = false, placed = [], blocks = [], mx = 0.5, my = 0.5, pmx = 0.5, pmy = 0.5, hover = -1, t = 0, ripple = -9, motes = [];
  const SIZES = [[34, 34], [25, 26], [19, 20]]; // [font px, badge radius] by tier
  const hit = (a, b) => a.x0 < b.x1 && a.x1 > b.x0 && a.y0 < b.y1 && a.y1 > b.y0;
  function rectOf(el, pad) { if (!el) return null; const b = hero.getBoundingClientRect(), r = el.getBoundingClientRect(); if (!r.width || !r.height) return null;
    return { x0: r.left - b.left - pad, y0: r.top - b.top - pad, x1: r.right - b.left + pad, y1: r.bottom - b.top + pad }; }
  // the title's final box: its text width at full size (the fly-in transform scales it, so measure layout boxes, not the rendered rect)
  function titleRect(h1, pad) {
    const b = hero.getBoundingClientRect(), left = h1.offsetLeft, top = h1.offsetTop, w = h1.offsetWidth, h = h1.offsetHeight;
    const rg = document.createRange(); rg.selectNodeContents(h1); const rs = [...rg.getClientRects()], sc = scaleOf(h1);
    const tw = rs.length ? Math.max(...rs.map((q) => q.width)) / sc : w; void b;
    const cx = left + w / 2, cyTop = top; // the CSS centres it vertically with translate(-50%)
    return { x0: cx - tw / 2 - pad, x1: cx + tw / 2 + pad, y0: cyTop - h / 2 - pad, y1: cyTop + h / 2 + pad };
  }
  function scaleOf(el) { const m = getComputedStyle(el).transform; if (!m || m === "none") return 1; const v = m.match(/matrix\(([^,]+),([^,]+)/); return v ? Math.hypot(+v[1], +v[2]) || 1 : 1; }
  function layout() {
    const b = hero.getBoundingClientRect(); W = Math.max(320, b.width); H = Math.max(400, b.height); phone = W < 720;
    dpr = Math.min(window.devicePixelRatio || 1, 2); cv.width = Math.round(W * dpr); cv.height = Math.round(H * dpr);
    blocks = [];
    const h1 = hero.querySelector("h1");
    if (h1) blocks.push(phone ? rectOf(h1, 10) : titleRect(h1, 26));
    [".kicker", ".hero-tag", ".hero-hint", ".scrollcue"].forEach((s) => { const r = rectOf(hero.querySelector(s), phone ? 8 : 14); if (r) blocks.push(r); });
    blocks = blocks.filter(Boolean);
    if (phone) { const top = Math.min(...blocks.map((r) => r.y0).concat([H * 0.62])); blocks.push({ x0: -9, x1: W + 9, y0: top - 6, y1: H + 9 }); }
    const sc = phone ? 0.7 : clamp(Math.min(W / 1500, H / 760), 0.72, 1.35);
    placed = [];
    const cx = W / 2, cy = phone ? H * 0.3 : H * 0.45, list = phone ? ITEMS.slice(0, 13) : ITEMS;
    hubX = cx; hubY = phone ? cy : (blocks[0] ? (blocks[0].y0 + blocks[0].y1) / 2 : cy); hubR = Math.min(W, H) * (phone ? 0.13 : 0.15);
    if (phone) { hubR = Math.min(W, H) * 0.11; blocks.push({ x0: hubX - hubR * 1.15, x1: hubX + hubR * 1.15, y0: hubY - hubR * 1.15, y1: hubY + hubR * 1.15 }); } // phones: the topics go around the nucleus
    list.forEach((it, i) => {
      const [fs0, R0] = SIZES[it.tier], fs = Math.round(fs0 * sc), R = R0 * sc;
      ctx.font = `600 ${fs}px ${it.tier === 0 ? SERIF : SANS}`; const tw = ctx.measureText(it.words).width;
      const w = R * 2 + 10 + tw, h = Math.max(R * 2, fs * 1.2), pad = phone ? 6 : 14;
      let found = null; // spiral outward from the centre (stretched to the screen's shape); the first free spot wins
      for (let s = 0; s < 2200 && !found; s++) {
        const a = s * 0.37 + i * 1.7, rr = 6 + s * (phone ? 0.9 : 1.4), x = cx + Math.cos(a) * rr * (W / H) * 0.62 - w / 2, y = cy + Math.sin(a) * rr * 0.62 - h / 2;
        const box = { x0: x - pad, y0: y - pad, x1: x + w + pad, y1: y + h + pad };
        if (box.x0 < (phone ? 8 : 60) || box.x1 > W - 8 || box.y0 < 10 || box.y1 > H - 8) continue; // desktop: clear of the lesson dots on the left
        if (blocks.some((r) => hit(box, r)) || placed.some((p) => hit(box, p.box))) continue;
        found = { x, y, box };
      }
      if (!found) return;
      placed.push(Object.assign({}, it, { x: found.x, y: found.y, w, h, fs, R, tw, box: found.box, img: badge(it, R), ph: (i * 2.399) % TAU, order: placed.length, z: 0.6 + 0.4 * ((i * 0.618) % 1) }));
    });
    motes = []; for (let i = 0; i < (phone ? 40 : 90); i++) motes.push({ x: Math.random() * W, y: Math.random() * H, r: 0.6 + Math.random() * 1.6, v: 4 + Math.random() * 10, ph: Math.random() * TAU });
  }

  // ---------- drawing ----------
  function itemPos(p) {
    const appear = ease((t - 0.35 - p.order * 0.07) / 0.9), bob = reduce ? 0 : Math.sin(t * 0.8 + p.ph) * 4 * p.z;
    const rp = t - ripple, d = Math.hypot(p.x + p.w / 2 - W / 2, p.y + p.h / 2 - H / 2), rip = rp > 0 && rp < 2.5 ? Math.max(0, Math.sin(clamp(rp * 4 - d / 200, 0, Math.PI))) * 12 : 0;
    const px = (pmx - 0.5) * 26 * p.z, py = (pmy - 0.5) * 16 * p.z, cx = W / 2, cy = H * 0.45, ox = p.x + p.w / 2, oy = p.y + p.h / 2;
    return { x: lerp(cx, ox, appear) - p.w / 2 + px, y: lerp(cy, oy, appear) - p.h / 2 + py + bob - rip, a: appear, s: lerp(0.4, 1, appear) * (1 + 0.08 * rip / 12), rip };
  }
  function draw() {
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0); ctx.globalAlpha = 1; ctx.globalCompositeOperation = "source-over";
    const bg = ctx.createRadialGradient(W * 0.5, H * 0.42, 0, W * 0.5, H * 0.5, Math.hypot(W, H) * 0.65);
    bg.addColorStop(0, "#0b1d3d"); bg.addColorStop(0.5, "#050d22"); bg.addColorStop(1, "#01040b"); ctx.fillStyle = bg; ctx.fillRect(0, 0, W, H);
    ctx.globalCompositeOperation = "lighter"; // slow drifting motes
    for (const m of motes) { const y = (((m.y - t * m.v) % H) + H) % H; ctx.globalAlpha = 0.22 + 0.18 * Math.sin(t + m.ph); ctx.fillStyle = "#9fc4ff"; ctx.beginPath(); ctx.arc(m.x + Math.sin(t * 0.3 + m.ph) * 6, y, m.r, 0, TAU); ctx.fill(); }
    ctx.globalAlpha = 1;
    // the hub: one nucleus behind the title, glowing and slowly turning; everything below grows out of it
    const pulse = 1 + 0.04 * Math.sin(t * 1.6), rp0 = t - ripple, kick = rp0 > 0 && rp0 < 1.2 ? (1 - rp0 / 1.2) : 0;
    ctx.globalCompositeOperation = "lighter";
    const hg = ctx.createRadialGradient(hubX, hubY, 0, hubX, hubY, hubR * 3.2 * pulse); hg.addColorStop(0, `rgba(150,200,255,${0.32 + 0.4 * kick})`); hg.addColorStop(0.35, "rgba(70,130,255,0.13)"); hg.addColorStop(1, "rgba(40,80,220,0)");
    ctx.fillStyle = hg; ctx.fillRect(hubX - hubR * 3.4, hubY - hubR * 3.4, hubR * 6.8, hubR * 6.8);
    ctx.globalCompositeOperation = "source-over";
    ctx.save(); ctx.translate(hubX, hubY); ctx.rotate(t * 0.08); ctx.globalAlpha = phone ? 0.95 : 0.55; const ns = hubR * 2.2 * pulse; ctx.drawImage(NUC, -ns / 2, -ns / 2, ns, ns); ctx.restore();
    // rays from the nucleus to each topic, with sparks running outward
    ctx.globalCompositeOperation = "lighter";
    placed.forEach((p, i) => {
      const q = itemPos(p); if (q.a <= 0.01) return; const on = i === hover, bx = q.x + p.R, by = q.y + p.h / 2, dx = bx - hubX, dy = by - hubY, L = Math.hypot(dx, dy) || 1;
      const sx = hubX + dx / L * hubR * 0.7, sy = hubY + dy / L * hubR * 0.7, bend = (i % 2 ? 1 : -1) * 0.12 * L, cxp = (sx + bx) / 2 - dy / L * bend, cyp = (sy + by) / 2 + dx / L * bend;
      const lg = ctx.createLinearGradient(sx, sy, bx, by); lg.addColorStop(0, hexA(p.col, 0)); lg.addColorStop(1, hexA(p.col, (on ? 0.75 : 0.26) * q.a));
      ctx.globalAlpha = 1; ctx.strokeStyle = lg; ctx.lineWidth = on ? 2.4 : 1.3; ctx.beginPath(); ctx.moveTo(sx, sy); ctx.quadraticCurveTo(cxp, cyp, bx, by); ctx.stroke();
      for (let k = 0; k < (on ? 4 : 2); k++) { const u = (t * 0.22 + p.ph / TAU + k / (on ? 4 : 2)) % 1, a2 = (1 - u) * (1 - u), ax = a2 * sx + 2 * (1 - u) * u * cxp + u * u * bx, ay = a2 * sy + 2 * (1 - u) * u * cyp + u * u * by;
        const sg = ctx.createRadialGradient(ax, ay, 0, ax, ay, 7); sg.addColorStop(0, hexA(p.col, 0.9 * Math.sin(Math.PI * u) * q.a)); sg.addColorStop(1, hexA(p.col, 0)); ctx.fillStyle = sg; ctx.fillRect(ax - 7, ay - 7, 14, 14); }
    });
    ctx.globalCompositeOperation = "source-over"; ctx.globalAlpha = 1;
    placed.forEach((p, i) => {
      const q = itemPos(p); if (q.a <= 0.01) return; const on = i === hover, k = q.s * (on ? 1.08 : 1);
      ctx.save(); ctx.translate(q.x + p.w / 2, q.y + p.h / 2); ctx.scale(k, k); ctx.translate(-p.w / 2, -p.h / 2); ctx.globalAlpha = q.a;
      ctx.globalCompositeOperation = "lighter"; // soft coloured glow behind the picture
      const gr = ctx.createRadialGradient(p.R, p.h / 2, 0, p.R, p.h / 2, p.R * (on ? 3.4 : 2.4) + q.rip);
      gr.addColorStop(0, hexA(p.col, on ? 0.5 : 0.24 * p.z + q.rip / 40)); gr.addColorStop(1, hexA(p.col, 0)); ctx.fillStyle = gr; ctx.fillRect(-p.R * 2.5, p.h / 2 - p.R * 3.5, p.R * 7, p.R * 7);
      ctx.globalCompositeOperation = "source-over";
      { const bp = 1 + 0.035 * Math.sin(t * 2 + p.ph), bs = p.R * 2.6 * bp; ctx.drawImage(p.img, p.R - bs / 2, p.h / 2 - bs / 2, bs, bs);
        const oa = t * (0.9 + 0.3 * p.z) + p.ph, ox = p.R + Math.cos(oa) * p.R * 1.32, oy = p.h / 2 + Math.sin(oa) * p.R * 1.32 * 0.55;
        ctx.globalCompositeOperation = "lighter"; const og = ctx.createRadialGradient(ox, oy, 0, ox, oy, 6); og.addColorStop(0, "rgba(255,255,255,.95)"); og.addColorStop(0.4, hexA(p.col, 0.8)); og.addColorStop(1, hexA(p.col, 0));
        ctx.fillStyle = og; ctx.fillRect(ox - 6, oy - 6, 12, 12); ctx.globalCompositeOperation = "source-over"; }
      ctx.font = `600 ${p.fs}px ${p.tier === 0 ? SERIF : SANS}`; ctx.textBaseline = "middle"; ctx.textAlign = "left";
      ctx.fillStyle = on ? "#ffffff" : `rgba(232,240,255,${(0.66 + 0.34 * p.z).toFixed(2)})`; ctx.shadowColor = "rgba(1,4,12,.9)"; ctx.shadowBlur = 8;
      ctx.fillText(p.words, p.R * 2 + 10, p.h / 2 + 1); ctx.shadowBlur = 0;
      if (on && p.link) { ctx.strokeStyle = hexA(p.col, 0.9); ctx.lineWidth = 2; ctx.beginPath(); ctx.moveTo(p.R * 2 + 10, p.h / 2 + p.fs * 0.62); ctx.lineTo(p.R * 2 + 10 + p.tw, p.h / 2 + p.fs * 0.62); ctx.stroke(); }
      ctx.restore();
    });
    if (hover >= 0 && placed[hover]) { // the fact, in a small dark card next to the item (kept on screen and off the text)
      const p = placed[hover], q = itemPos(p), fs = phone ? 13 : 14;
      ctx.font = `500 ${fs}px ${SANS}`; const txt = p.fact + (p.link ? "  →" : ""), w = Math.min(ctx.measureText(txt).width + 26, W - 16), h = fs * 2.2;
      let x = clamp(q.x + p.w / 2 - w / 2, 8, W - 8 - w), y = q.y + p.h + 10;
      if (blocks.some((r) => hit({ x0: x, y0: y, x1: x + w, y1: y + h }, r)) || y + h > H - 6) y = q.y - h - 10;
      ctx.globalAlpha = 0.95; ctx.fillStyle = "rgba(6,14,32,.94)"; ctx.strokeStyle = hexA(p.col, 0.75); ctx.lineWidth = 1.2; ctx.beginPath(); if (ctx.roundRect) ctx.roundRect(x, y, w, h, 10); else ctx.rect(x, y, w, h); ctx.fill(); ctx.stroke();
      ctx.globalAlpha = 1; ctx.fillStyle = "#eef3ff"; ctx.textAlign = "center"; ctx.textBaseline = "middle"; ctx.fillText(txt, x + w / 2, y + h / 2, w - 16);
    }
    const vg = ctx.createRadialGradient(W / 2, H / 2, Math.min(W, H) * 0.4, W / 2, H / 2, Math.hypot(W, H) * 0.62); vg.addColorStop(0, "rgba(1,3,9,0)"); vg.addColorStop(1, "rgba(1,3,9,0.55)");
    ctx.fillStyle = vg; ctx.fillRect(0, 0, W, H);
  }

  // ---------- interaction ----------
  function pick(x, y) { for (let i = placed.length - 1; i >= 0; i--) { const p = placed[i], q = itemPos(p); if (x >= q.x - 6 && x <= q.x + p.w + 6 && y >= q.y - 6 && y <= q.y + p.h + 6) return i; } return -1; }
  hero.addEventListener("pointermove", (e) => { if (e.pointerType === "touch") return; const b = cv.getBoundingClientRect(), x = e.clientX - b.left, y = e.clientY - b.top;
    mx = x / b.width; my = y / b.height; hover = pick(x, y); cv.style.cursor = hover >= 0 && placed[hover].link ? "pointer" : "default"; if (reduce) draw(); });
  hero.addEventListener("pointerleave", () => { hover = -1; if (reduce) draw(); });
  let lastType = "mouse"; cv.addEventListener("pointerdown", (e) => (lastType = e.pointerType));
  cv.addEventListener("click", (e) => { const b = cv.getBoundingClientRect(), i = pick(e.clientX - b.left, e.clientY - b.top);
    if (i < 0) { hover = -1; if (reduce) draw(); return; }
    if (lastType === "touch" && hover !== i) { hover = i; if (reduce) draw(); return; } // phones: the first tap shows the fact
    const p = placed[i]; hover = i; if (!p.link) { if (reduce) draw(); return; }
    const el = document.getElementById(p.link) || document.getElementById(p.link.replace(/-\d+$/, ""));
    if (el) { history.replaceState(null, "", location.pathname + location.search + "#" + p.link); el.scrollIntoView({ behavior: reduce ? "auto" : "smooth", block: "center" }); } });
  const btn = hero.querySelector(".fire-btn");
  if (btn) btn.addEventListener("click", (e) => { e.stopPropagation(); ripple = t; if (reduce) draw(); });

  // ---------- loop ----------
  let last = 0, vis = true;
  new IntersectionObserver((es) => es.forEach((en) => (vis = en.isIntersecting))).observe(hero);
  function frame(now) {
    const dt = Math.min(0.05, last ? (now - last) / 1000 : 0.016); last = now;
    if (vis && !document.hidden) { t += dt; pmx += (mx - pmx) * Math.min(1, dt * 3); pmy += (my - pmy) * Math.min(1, dt * 3); draw();
      const sc = clamp(window.scrollY / (H * 0.8), 0, 1); if (copy) copy.style.opacity = String(clamp(1 - sc * 1.6, 0, 1)); }
    requestAnimationFrame(frame);
  }
  let relayT = 0; window.addEventListener("resize", () => { clearTimeout(relayT); relayT = setTimeout(() => { layout(); draw(); }, 120); });
  hero.classList.add("hero-live"); setTimeout(() => document.body.classList.add("hero-done"), 2600);
  // lay out once fonts are in (the title's size depends on them)
  (document.fonts && document.fonts.ready ? document.fonts.ready : Promise.resolve()).then(() => {
    layout(); if (qH) hover = Math.min(+qH[1], placed.length - 1);
    if (freezeAt != null || reduce) { t = freezeAt != null ? freezeAt : 5; draw(); } else requestAnimationFrame(frame);
  });
})();
