/* Explorable-explanation kit for "Inside a Nuclear Reaction".
 *
 * A chapter is a <section class="chapter" data-ch="ID"> containing
 *   .stage  (sticky drawing area; a <canvas> is created inside it)
 *   .story  (a column of .step blocks; the step nearest the middle of the screen is "active")
 * and a JS module registered with WT.chapter(ID, { setup, frame, steps }).
 *
 *   setup(S)            once; S is the chapter state object (put your own fields on it)
 *   steps[i](S)         called when step i becomes active: set targets, e.g. S.to("E", 5)
 *   frame(g, S, dt)     every animation frame while the chapter is on screen; draw with g
 *
 * Inline controls in the text bind to state:  <input type="range" data-bind="E" min max step value>
 * and <output data-show="E" data-fmt="1"> shows a value. Buttons: <button data-act="fire">.
 * S.on("fire", fn) receives button presses. Everything animates by easing S[key] toward S.target[key].
 * Plain script (no modules) so the page also works from disk. */
(function () {
  "use strict";
  const WT = (window.WT = Object.assign(window.WT || {}, { mods: {} })); // glossary.js may have defined WT.glossary already
  WT.chapter = (id, mod) => (WT.mods[id] = mod);

  const TAU = Math.PI * 2;
  const clamp = (v, a, b) => Math.max(a, Math.min(b, v));
  const lerp = (a, b, s) => a + (b - a) * s;
  const smooth = (e0, e1, x) => { const t = clamp((x - e0) / (e1 - e0), 0, 1); return t * t * (3 - 2 * t); };
  function rng(seed) { let s = seed >>> 0 || 1; return () => ((s = (s * 16807) % 2147483647) / 2147483647); }
  WT.util = { TAU, clamp, lerp, smooth, rng };

  // ---------- palette from CSS tokens ----------
  const COL = {};
  const KEYS = ["ink", "soft", "faint", "paper", "card", "line", "accent", "neutron", "proton", "alpha", "photon", "fission", "warm", "cool"];
  function readColors() { const cs = getComputedStyle(document.documentElement); KEYS.forEach((k) => (COL[k] = cs.getPropertyValue("--" + k).trim())); }
  WT.col = COL;
  function shade(hex, f) { const n = parseInt(hex.slice(1), 16), c = (v) => Math.min(255, Math.round(v * f)); return `rgb(${c((n >> 16) & 255)},${c((n >> 8) & 255)},${c(n & 255)})`; }
  function rgba(hex, a) {
    const h = hex.replace("#", ""); const n = parseInt(h.length === 3 ? h.split("").map((c) => c + c).join("") : h, 16);
    return `rgba(${(n >> 16) & 255},${(n >> 8) & 255},${n & 255},${a})`;
  }

  // ---------- drawing context ----------
  function makeG(ctx, W, H) {
    const g = { ctx, W, H, c: COL, rgba, TAU };
    const SANS = getComputedStyle(document.documentElement).getPropertyValue("--sans").trim() || "system-ui, sans-serif";
    const SERIF = getComputedStyle(document.documentElement).getPropertyValue("--serif").trim() || "Georgia, serif";
    g.clear = () => ctx.clearRect(0, 0, W, H);
    g.save = () => ctx.save(); g.restore = () => ctx.restore();
    /** Text label. o: color size weight serif italic align base alpha, bg (true = paper backing so it never collides). */
    g.label = (s, x, y, o = {}) => {
      if (WT.tr) s = WT.tr(s);
      ctx.save(); ctx.globalAlpha = o.alpha ?? 1;
      let size = Math.max(o.size || 14, W < 600 ? 10 : 12); // legible minimum; phones keep their tighter sizes so labels fit
      const font = () => `${o.italic ? "italic " : ""}${o.weight || 500} ${size}px ${o.serif ? SERIF : SANS}`;
      ctx.font = font(); ctx.textAlign = o.align || "center"; ctx.textBaseline = o.base || "middle";
      // never run off the drawing: shrink a too-long label (down to 9 px), then slide it inside the edges
      const room = W - 8 - (o.bg ? 12 : 0);
      while (ctx.measureText(s).width > room && size > 9) { size -= 0.5; ctx.font = font(); }
      { const w = ctx.measureText(s).width, a = ctx.textAlign, left = a === "left" ? x : a === "right" ? x - w : x - w / 2, pad = 4 + (o.bg ? 6 : 0);
        if (left < pad) x += pad - left; else if (left + w > W - pad) x -= left + w - (W - pad); }
      if (o.bg) {
        const w = ctx.measureText(s).width, h = size * 1.5, pad = 6;
        const x0 = (o.align === "left" ? x : o.align === "right" ? x - w : x - w / 2) - pad;
        ctx.fillStyle = rgba(COL.paper, 0.88); ctx.beginPath(); if (ctx.roundRect) ctx.roundRect(x0, y - h / 2, w + 2 * pad, h, 6); else ctx.rect(x0, y - h / 2, w + 2 * pad, h); ctx.fill();
      }
      ctx.fillStyle = !o.color || o.color === COL.faint ? COL.soft : o.color; ctx.fillText(s, x, y); ctx.restore(); // faint grey is too pale for text
    };
    /** Fade the stage edges into the page so drawings never look boxed. */
    g.vignette = (edge = 0.12) => {
      const e = Math.min(W, H) * edge;
      [[0, 0, e, 0, 0, 0, e, H], [W, 0, W - e, 0, W - e, 0, e, H], [0, 0, 0, e, 0, 0, W, e], [0, H, 0, H - e, 0, H - e, W, e]].forEach(([x1, y1, x2, y2, rx, ry, rw, rh]) => {
        const gr = ctx.createLinearGradient(x1, y1, x2, y2); gr.addColorStop(0, rgba(COL.paper, 1)); gr.addColorStop(1, rgba(COL.paper, 0));
        ctx.fillStyle = gr; ctx.fillRect(rx, ry, rw, rh);
      });
    };
    /** Ground under a profile line (a landscape, not a chart): gradient fading downward over `depth` px. */
    g.ground = (pts, color, depth = 140, alpha = 0.32) => {
      if (pts.length < 2) return; let top = Infinity; pts.forEach((p) => (top = Math.min(top, p[1])));
      const maxY = Math.max(...pts.map((p) => p[1])) + depth;
      ctx.save(); const gr = ctx.createLinearGradient(0, top, 0, maxY); gr.addColorStop(0, rgba(color, alpha)); gr.addColorStop(1, rgba(color, 0));
      ctx.fillStyle = gr; ctx.beginPath(); ctx.moveTo(pts[0][0], maxY); pts.forEach((p) => ctx.lineTo(p[0], p[1])); ctx.lineTo(pts[pts.length - 1][0], maxY); ctx.closePath(); ctx.fill(); ctx.restore();
    };
    g.clip = (x, y, w, h) => { ctx.save(); ctx.beginPath(); ctx.rect(x, y, w, h); ctx.clip(); };
    g.line = (x1, y1, x2, y2, color, w = 1.5, alpha = 1, dash) => {
      ctx.save(); ctx.globalAlpha = alpha; ctx.strokeStyle = color; ctx.lineWidth = w; ctx.lineCap = "round";
      if (dash) ctx.setLineDash(dash); ctx.beginPath(); ctx.moveTo(x1, y1); ctx.lineTo(x2, y2); ctx.stroke(); ctx.restore();
    };
    g.poly = (pts, color, w = 2, alpha = 1, dash, close) => {
      if (pts.length < 2) return; ctx.save(); ctx.globalAlpha = alpha; ctx.strokeStyle = color; ctx.lineWidth = w;
      ctx.lineJoin = "round"; ctx.lineCap = "round"; if (dash) ctx.setLineDash(dash);
      ctx.beginPath(); ctx.moveTo(pts[0][0], pts[0][1]); for (let i = 1; i < pts.length; i++) ctx.lineTo(pts[i][0], pts[i][1]);
      if (close) ctx.closePath(); ctx.stroke(); ctx.restore();
    };
    g.area = (pts, color, alpha = 0.25) => {
      if (pts.length < 3) return; ctx.save(); ctx.globalAlpha = alpha; ctx.fillStyle = color; ctx.beginPath();
      ctx.moveTo(pts[0][0], pts[0][1]); for (let i = 1; i < pts.length; i++) ctx.lineTo(pts[i][0], pts[i][1]);
      ctx.closePath(); ctx.fill(); ctx.restore();
    };
    g.dot = (x, y, r, color, alpha = 1) => { ctx.save(); ctx.globalAlpha = alpha; ctx.fillStyle = color; ctx.beginPath(); ctx.arc(x, y, Math.max(0.1, r), 0, TAU); ctx.fill(); ctx.restore(); };
    g.ring = (x, y, r, color, w = 1.5, alpha = 1, dash) => { ctx.save(); ctx.globalAlpha = alpha; ctx.strokeStyle = color; ctx.lineWidth = w; if (dash) ctx.setLineDash(dash); ctx.beginPath(); ctx.arc(x, y, Math.max(0.1, r), 0, TAU); ctx.stroke(); ctx.restore(); };
    /** A nucleon drawn as a small lit sphere. */
    g.ball = (x, y, r, color, alpha = 1) => {
      ctx.save(); ctx.globalAlpha = alpha;
      const gr = ctx.createRadialGradient(x - r * 0.35, y - r * 0.4, r * 0.1, x, y, r);
      const hx = color.length === 7 ? color : "#888888";
      gr.addColorStop(0, "#ffffff"); gr.addColorStop(0.22, color); gr.addColorStop(0.75, shade(hx, 0.62)); gr.addColorStop(1, shade(hx, 0.34));
      ctx.fillStyle = gr; ctx.beginPath(); ctx.arc(x, y, Math.max(0.1, r), 0, TAU); ctx.fill();
      ctx.strokeStyle = rgba("#000000", 0.18); ctx.lineWidth = 0.8; ctx.stroke(); ctx.restore();
    };
    /** Soft glow (energy, absorption). */
    g.glow = (x, y, r, color, alpha = 0.5) => {
      ctx.save(); const gr = ctx.createRadialGradient(x, y, 0, x, y, r);
      gr.addColorStop(0, rgba(color, alpha)); gr.addColorStop(1, rgba(color, 0)); ctx.fillStyle = gr;
      ctx.beginPath(); ctx.arc(x, y, r, 0, TAU); ctx.fill(); ctx.restore();
    };
    g.arrow = (x1, y1, x2, y2, color, w = 2, alpha = 1, head = 9) => {
      ctx.save(); ctx.globalAlpha = alpha; ctx.strokeStyle = color; ctx.fillStyle = color; ctx.lineWidth = w; ctx.lineCap = "round";
      ctx.beginPath(); ctx.moveTo(x1, y1); ctx.lineTo(x2, y2); ctx.stroke();
      const a = Math.atan2(y2 - y1, x2 - x1);
      ctx.beginPath(); ctx.moveTo(x2 + Math.cos(a) * 2, y2 + Math.sin(a) * 2);
      ctx.lineTo(x2 - head * Math.cos(a - 0.45), y2 - head * Math.sin(a - 0.45));
      ctx.lineTo(x2 - head * Math.cos(a + 0.45), y2 - head * Math.sin(a + 0.45)); ctx.closePath(); ctx.fill(); ctx.restore();
    };
    /** A photon: a short glowing wavy streak moving along direction a. */
    g.photon = (x, y, a, len = 26, alpha = 1) => {
      ctx.save(); ctx.globalAlpha = alpha; ctx.strokeStyle = COL.photon; ctx.lineWidth = 2.2; ctx.lineCap = "round"; ctx.beginPath();
      for (let i = 0; i <= 24; i++) { const s = (i / 24 - 0.5) * len, w = Math.sin(i * 1.3) * 3.2; const px = x + Math.cos(a) * s - Math.sin(a) * w, py = y + Math.sin(a) * s + Math.cos(a) * w; i ? ctx.lineTo(px, py) : ctx.moveTo(px, py); }
      ctx.stroke(); ctx.restore(); g.glow(x, y, len * 0.6, COL.photon, 0.25 * alpha);
    };
    /** A doorway whose lit gap shows how open it is. (x, y) = bottom-centre of the doorway, h = height (width = 0.62 h).
     *  openness 0..1 = width of the lit gap between two sliding panels; at 0 the panels meet and the door greys out.
     *  label (optional) is drawn under the sill. o: { ang (rotation about the sill, 0 = upright), w (width), alpha, size }.
     *  Returns { x, y, w, h, gap, mx, my }: (mx, my) = centre of the gap in stage coordinates (where things come out). */
    g.door = (x, y, h, openness, color, label, o = {}) => {
      const op = clamp(openness || 0, 0, 1), w = o.w || h * 0.62, ang = o.ang || 0, al = o.alpha ?? 1;
      const shut = op < 1e-6, iw = w - 6, gap = shut ? 0 : Math.max(1.6, iw * op);
      const col = shut ? COL.faint : color;
      ctx.save(); ctx.globalAlpha = al; ctx.translate(x, y); ctx.rotate(ang);
      // light spilling out in front of the gap (the floor), only when open
      if (!shut) {
        const gr = ctx.createLinearGradient(0, 0, 0, h * 0.42); gr.addColorStop(0, rgba(color, 0.28 * Math.sqrt(op) + 0.06)); gr.addColorStop(1, rgba(color, 0));
        ctx.fillStyle = gr; ctx.beginPath(); ctx.moveTo(-gap / 2, 0); ctx.lineTo(gap / 2, 0); ctx.lineTo(gap / 2 + h * 0.22, h * 0.42); ctx.lineTo(-gap / 2 - h * 0.22, h * 0.42); ctx.closePath(); ctx.fill();
      }
      // the lit gap
      if (!shut) {
        const gr = ctx.createLinearGradient(0, -h, 0, 0); gr.addColorStop(0, rgba(color, 0.55)); gr.addColorStop(1, rgba(color, 0.95));
        ctx.fillStyle = gr; ctx.fillRect(-gap / 2, -h + 3, gap, h - 3);
      }
      // two sliding panels, meeting in the middle when shut
      const pw = (iw - gap) / 2;
      ctx.fillStyle = rgba(COL.soft, shut ? 0.1 : 0.16); ctx.strokeStyle = rgba(COL.soft, shut ? 0.35 : 0.5); ctx.lineWidth = 1;
      if (pw > 0.3) { ctx.fillRect(-iw / 2, -h + 3, pw, h - 3); ctx.strokeRect(-iw / 2 + 0.5, -h + 3.5, pw - 1, h - 4); ctx.fillRect(iw / 2 - pw, -h + 3, pw, h - 3); ctx.strokeRect(iw / 2 - pw + 0.5, -h + 3.5, pw - 1, h - 4); }
      // the frame: two posts and a lintel, coloured when open, grey when shut
      ctx.strokeStyle = shut ? rgba(COL.faint, 0.7) : rgba(color, 0.95); ctx.lineWidth = Math.max(2, h * 0.045); ctx.lineJoin = "round"; ctx.lineCap = "round";
      ctx.beginPath(); ctx.moveTo(-w / 2, 0); ctx.lineTo(-w / 2, -h); ctx.lineTo(w / 2, -h); ctx.lineTo(w / 2, 0); ctx.stroke();
      ctx.strokeStyle = rgba(COL.faint, 0.6); ctx.lineWidth = 1.2; ctx.beginPath(); ctx.moveTo(-w / 2 - 4, 0); ctx.lineTo(w / 2 + 4, 0); ctx.stroke();
      ctx.restore();
      if (!shut && op > 0.15) g.glow(x + Math.sin(ang) * h * 0.5, y - Math.cos(ang) * h * 0.5, h * 0.55, color, 0.18 * op * al);
      if (label) g.label(label, x - Math.sin(ang) * 14, y + Math.cos(ang) * 14, { color: col, size: o.size || Math.max(11, Math.min(14, h * 0.24)), weight: 600, bg: true, alpha: al });
      return { x, y, w, h, gap, mx: x + Math.sin(ang) * h * 0.5, my: y - Math.cos(ang) * h * 0.5 };
    };
    /** Packed nucleus of N nucleons (Z protons), radius R, optional deformation (prolate) and rotation. Positions are stable per seed. */
    g.nucleus = (x, y, R, o = {}) => {
      const N = o.N || 40, Z = o.Z ?? Math.round(N * 0.45), seed = o.seed || 7, t = o.t || 0, beta = o.beta || 0, rot = o.rot || 0, jig = o.jiggle ?? 0.6;
      const r = rng(seed); const pts = [];
      for (let i = 0; i < N; i++) { const a = i * 2.39996 + r() * 0.3, rr = Math.sqrt((i + 0.5) / N) * 0.86; pts.push([rr * Math.cos(a), rr * Math.sin(a), r()]); }
      const isP = pts.map((_, i) => i < Z); for (let i = N - 1; i > 0; i--) { const j = Math.floor(r() * (i + 1)); [isP[i], isP[j]] = [isP[j], isP[i]]; }
      const rb = R / Math.sqrt(N) * 0.98;
      if (o.halo) g.glow(x, y, R * 1.9, o.halo, o.haloAlpha ?? 0.35);
      const order = pts.map((p, i) => i).sort((a, b) => pts[a][2] - pts[b][2]);
      for (const i of order) {
        const [px, py, ph] = pts[i];
        let X = px * R * (1 + beta), Y = py * R * (1 - beta * 0.55);
        const c = Math.cos(rot), s = Math.sin(rot); [X, Y] = [X * c - Y * s, X * s + Y * c];
        X += Math.sin(t * 3.1 + ph * 20) * jig * (o.heat || 1); Y += Math.cos(t * 2.7 + ph * 17) * jig * (o.heat || 1);
        g.ball(x + X, y + Y, rb, isP[i] ? COL.proton : COL.neutron, o.alpha ?? 1);
      }
    };
    g.text = g.label;
    return g;
  }

  // ---------- chapter runtime ----------
  function makeState(id) {
    const S = { id, target: {}, speed: 6, time: 0, step: -1, handlers: {} };
    S.to = (k, v, now) => { S.target[k] = v; if (now || S[k] === undefined) S[k] = v; };
    S.set = (k, v) => { S[k] = v; S.target[k] = v; };
    S.on = (name, fn) => (S.handlers[name] = fn);
    S.ease = (dt) => { const a = 1 - Math.exp(-S.speed * dt); for (const k in S.target) { const v = S.target[k]; if (typeof v === "number") S[k] += (v - S[k]) * a; else S[k] = v; } };
    return S;
  }

  // ---------- glossary: mark technical terms in the prose, explain them in a card ----------
  // Terms come from WT.glossary (js/glossary.js). Each step, lead, the hero and the coda mark the FIRST use of each
  // term (entries with scope "chapter"/"page": first use per chapter/page), so the page stays calm. Longest match wins.
  const GL_BLOCKS = ".intro-text p, .story .lead, .step p, .coda p, .coda td:nth-child(2)";
  const GL_SKIP = ".ctl, .btns, button, input, label, output, select, textarea, code, pre, .formula, .aside, .term, h1, h2, h3, a";
  const BOUND = "[\\p{L}\\p{M}\\p{N}_\\-]";   // \p{M}: Devanagari vowel signs are marks, not letters
  // Korean attaches particles to the noun (핵이, 핵을), so a term may be followed by Hangul; Chinese and Japanese write no spaces
  // at all, so there a term may sit between any characters. Latin letters and digits still bound a match in every language.
  const LATIN = "[A-Za-z0-9_\\-]";
  const BOUND_BEFORE = WT.lang === "zh" || WT.lang === "ja" ? LATIN : BOUND;
  const BOUND_AFTER = WT.lang === "ko" || WT.lang === "zh" || WT.lang === "ja" ? LATIN : BOUND;
  const escRe = (s) => s.replace(/[.*+?^${}()|[\]\\]/g, "\\$&").replace(/\s+/g, "\\s+");
  function plural(a) {
    if (WT.tl && WT.lang !== "es") return a;   // other languages list their plural forms as glossary aliases
    if (WT.lang === "es") { if (/[aeiouáéó]$/.test(a)) return a + "s"; if (/z$/.test(a)) return a.slice(0, -1) + "ces"; if (/s$/.test(a)) return a; return a + "es"; }
    if (/(s|x|ch|sh)$/.test(a)) return a + "es";
    if (/[^aeiou]y$/.test(a)) return a.slice(0, -1) + "ies";
    return a + "s";
  }
  function glMatchers() {
    const ci = new Map(), cs = new Map(); // alias -> key
    const G = WT.gl() || {};
    for (const key in G) for (const a of G[key].aliases || []) {
      // plain words (an optional capital first letter, then lower case) match case-insensitively, with plurals;
      // a single letter is a symbol and keeps its case (the width Γ must not mark every γ)
      if (/^\p{L}[\p{Ll}' \-–]+$/u.test(a)) { const l = a.toLowerCase(); if (!ci.has(l)) ci.set(l, key); const pl = plural(l); if (!ci.has(pl)) ci.set(pl, key); }
      else if (!cs.has(a)) cs.set(a, key);
    }
    const mk = (m, fl) => { if (!m.size) return null; const alts = [...m.keys()].sort((x, y) => y.length - x.length).map(escRe).join("|"); return new RegExp(`(?<!${BOUND_BEFORE})(?:${alts})(?!${BOUND_AFTER})`, "gu" + fl); };
    return { ci, cs, rci: mk(ci, "i"), rcs: mk(cs, "") };
  }
  function glMark() {
    const G = WT.gl(); if (!G) return 0;
    const M = glMatchers(); let count = 0;
    const scopes = new Map(), chapters = new Map(), pageUsed = new Set();
    const setOf = (map, k) => { let s = map.get(k); if (!s) map.set(k, (s = new Set())); return s; };
    document.querySelectorAll(GL_BLOCKS).forEach((block) => {
      if (block.closest(GL_SKIP)) return;
      const scopeEl = block.closest("[data-ch]") || block.closest(".coda") || block.closest(".intro-text") || block; // first use per chapter keeps the page calm
      const chEl = block.closest("[data-ch]"), chKey = chEl ? chEl : block.closest(".coda") || block;
      const used = setOf(scopes, scopeEl), chUsed = setOf(chapters, chKey);
      // the block's text, as segments of text nodes (segments inside controls/code are off limits)
      const segs = []; let text = "";
      const tw = document.createTreeWalker(block, NodeFilter.SHOW_TEXT);
      for (let n; (n = tw.nextNode()); ) { segs.push({ n, s: text.length, e: text.length + n.data.length, skip: !!(n.parentElement && n.parentElement !== block && n.parentElement.closest(GL_SKIP) && block.contains(n.parentElement.closest(GL_SKIP))) }); text += n.data; }
      if (!text.trim()) return;
      const found = [];
      [[M.rci, M.ci, true], [M.rcs, M.cs, false]].forEach(([re, map, low]) => {
        if (!re) return; re.lastIndex = 0;
        for (let m; (m = re.exec(text)); ) { const k = map.get(low ? m[0].toLowerCase().replace(/\s+/g, " ") : m[0].replace(/\s+/g, " ")); if (k) found.push({ s: m.index, e: m.index + m[0].length, k }); }
      });
      found.sort((a, b) => a.s - b.s || b.e - a.e);
      const picks = []; let end = -1;
      for (const f of found) {
        if (f.s < end) continue; end = f.e;                     // overlapping shorter match: the longer one owns this text
        if (segs.some((g) => g.skip && g.s < f.e && g.e > f.s)) continue;
        const sc = G[f.k].scope, once = sc === "page" ? pageUsed : sc === "chapter" ? chUsed : used;
        if (once.has(f.k)) continue;
        used.add(f.k); chUsed.add(f.k); pageUsed.add(f.k); picks.push(f);
      }
      for (let i = picks.length - 1; i >= 0; i--) {            // wrap from the end so earlier offsets stay valid
        const f = picks[i];
        const a = segs.find((g) => f.s >= g.s && f.s < g.e), b = segs.find((g) => f.e > g.s && f.e <= g.e);
        if (!a || !b) continue;
        const r = document.createRange();
        try {
          r.setStart(a.n, f.s - a.s); r.setEnd(b.n, f.e - b.s);
          const span = document.createElement("span");
          span.className = "term"; span.dataset.term = f.k; span.setAttribute("role", "button"); span.tabIndex = 0;
          span.setAttribute("aria-describedby", "gl-d-" + f.k); span.setAttribute("aria-controls", "gl-card"); span.setAttribute("aria-expanded", "false");
          // a match like S<sub>n</sub> or <i>T<sub>l</sub></i> crosses elements: grow it over the inline wrappers it fully covers
          try { r.surroundContents(span); } catch (e0) { glGrow(r, block); r.surroundContents(span); }
          count++;
        } catch (e) { /* range crosses an element boundary we cannot wrap; leave it plain */ }
      }
    });
    return count;
  }

  function glGrow(r, block) {
    for (;;) { // end boundary: step out of elements whose content it closes
      const c = r.endContainer, o = r.endOffset; let el;
      if (c.nodeType === 3) { if (o !== c.data.length || c !== c.parentNode.lastChild) break; el = c.parentNode; }
      else { if (o !== c.childNodes.length) break; el = c; }
      if (el === block || !block.contains(el)) break; r.setEndAfter(el);
    }
    for (;;) { // start boundary: likewise for elements whose content it opens
      const c = r.startContainer, o = r.startOffset; let el;
      if (o !== 0) break;
      if (c.nodeType === 3) { if (c !== c.parentNode.firstChild) break; el = c.parentNode; } else el = c;
      if (el === block || !block.contains(el)) break; r.setStartBefore(el);
    }
  }
  const Card = { el: null, term: null, pinned: false, openT: 0, closeT: 0, px: null, py: null, keyNav: false };
  const sheetMQ = window.matchMedia("(max-width: 639.98px)");
  const reduceMQ = window.matchMedia("(prefers-reduced-motion: reduce)");
  function glCard() {
    const G = WT.gl(); if (!G || Card.el) return;
    // hidden one-line descriptions that every marked term points to, so screen readers announce the meaning on focus
    const descs = document.createElement("div"); descs.hidden = true; descs.id = "gl-descs";
    for (const k in G) { const s = document.createElement("span"); s.id = "gl-d-" + k; s.textContent = G[k].short; descs.appendChild(s); }
    document.body.appendChild(descs);
    const el = (Card.el = document.createElement("div"));
    el.id = "gl-card"; el.className = "gl-card"; el.setAttribute("role", "tooltip"); el.setAttribute("aria-labelledby", "gl-title");
    el.innerHTML = `<span class="gl-arrow" aria-hidden="true"></span><button type="button" class="gl-close" aria-label="${WT.ui ? WT.ui("close", "Close") : "Close"}">×</button><div class="gl-title" id="gl-title"></div><p class="gl-short"></p><p class="gl-more"></p><div class="gl-formula"></div><a class="gl-link" href="#"></a>`;
    document.body.appendChild(el);
    const q = (s) => el.querySelector(s);
    q(".gl-close").addEventListener("click", () => glClose(true));
    q(".gl-link").addEventListener("click", (e) => {
      e.preventDefault(); const id = e.currentTarget.dataset.goto, t = document.getElementById(id); glClose(false);
      if (t) t.scrollIntoView({ behavior: reduceMQ.matches ? "auto" : "smooth", block: "start" });
    });
    q(".gl-link").addEventListener("keydown", (e) => {
      if (e.key !== "Tab" || sheetMQ.matches || !Card.term) return;
      const t = Card.term; if (e.shiftKey) e.preventDefault(); else glClose(false); // Shift+Tab: back to the word; Tab: close and move on
      Card.keyNav = true; t.focus({ preventScroll: true }); Card.keyNav = false;
    });
    el.addEventListener("pointerenter", () => clearTimeout(Card.closeT));
    el.addEventListener("pointerleave", (e) => { if (e.pointerType === "mouse" && !Card.pinned) glScheduleClose(); });

    const termOf = (t) => (t && t.closest ? t.closest(".term") : null);
    document.addEventListener("pointerover", (e) => {
      const t = termOf(e.target); if (!t || e.pointerType !== "mouse") return;
      clearTimeout(Card.closeT); if (Card.term === t) return;
      clearTimeout(Card.openT); Card.px = e.clientX; Card.py = e.clientY;
      Card.openT = setTimeout(() => { if (!Card.pinned || Card.term !== t) glOpen(t, false); }, Card.term ? 60 : 120);
    });
    document.addEventListener("pointerout", (e) => {
      const t = termOf(e.target); if (!t || e.pointerType !== "mouse" || t.contains(e.relatedTarget)) return;
      clearTimeout(Card.openT); if (Card.term === t && !Card.pinned) glScheduleClose();
    });
    document.addEventListener("click", (e) => {
      const t = termOf(e.target); if (!t) return;
      e.preventDefault(); clearTimeout(Card.openT); Card.px = e.clientX; Card.py = e.clientY;
      if (Card.term === t && Card.pinned) glClose(false); else glOpen(t, true, e.pointerType !== "mouse" && e.detail > 0);
    });
    document.addEventListener("keydown", (e) => {
      if (e.key === "Escape" && Card.term) { const back = el.contains(document.activeElement); const t = Card.term; glClose(false); if (back || document.activeElement === t) { Card.keyNav = true; t.focus({ preventScroll: true }); Card.keyNav = false; } return; }
      const t = termOf(e.target);
      // Tab from a term whose card was opened with Enter moves into the card (its chapter link)
      if (t && e.key === "Tab" && !e.shiftKey && t === Card.term && Card.pinned && !el.querySelector(".gl-link").hidden) { e.preventDefault(); el.querySelector(".gl-link").focus({ preventScroll: true }); return; }
      if (!t || (e.key !== "Enter" && e.key !== " ")) return;
      e.preventDefault(); Card.px = Card.py = null;
      if (Card.term === t && Card.pinned) glClose(false); else glOpen(t, true, true);
    });
    document.addEventListener("focusin", (e) => {
      const t = termOf(e.target);
      if (t && !Card.keyNav && t.matches(":focus-visible") && Card.term !== t) { Card.px = Card.py = null; glOpen(t, false); }
    });
    document.addEventListener("focusout", (e) => {
      if (!Card.term || Card.pinned) return; const to = e.relatedTarget;
      if (to && (el.contains(to) || to === Card.term)) return;
      if (e.target === Card.term) glClose(false);
    });
    document.addEventListener("pointerdown", (e) => { if (Card.term && !el.contains(e.target) && !termOf(e.target)) glClose(false); });
    const follow = () => { if (Card.term && !sheetMQ.matches) { const r = Card.term.getBoundingClientRect(); if (r.bottom < 0 || r.top > innerHeight) glClose(false); else glPlace(); } };
    window.addEventListener("scroll", follow, { passive: true });
    window.addEventListener("resize", () => Card.term && glPlace());
  }
  /** Formula text to HTML: x^(…) or x^2 → superscript, T_b or σ_inv → subscript; everything else escaped. */
  function glFormula(src) {
    const esc = (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;" }[c] || c);
    let out = "";
    for (let i = 0; i < src.length; i++) {
      const c = src[i];
      if ((c === "^" || c === "_") && i + 1 < src.length) {
        const tag = c === "^" ? "sup" : "sub"; let body = "";
        if (src[i + 1] === "(") { let d = 0, j = i + 1; for (; j < src.length; j++) { if (src[j] === "(") d++; else if (src[j] === ")" && --d === 0) break; } body = src.slice(i + 2, j); i = j; }
        else { const m = /^[\p{L}\p{N}+−\-]+/u.exec(src.slice(i + 1)); if (!m) { out += esc(c); continue; } body = m[0]; i += m[0].length; }
        out += `<${tag}>${glFormula(body)}</${tag}>`;
      } else out += esc(c);
    }
    return out;
  }
  function glScheduleClose() { clearTimeout(Card.closeT); Card.closeT = setTimeout(() => glClose(false), 180); }
  function glOpen(t, pin, focusSheet) {
    const G = WT.gl(), e = G && G[t.dataset.term]; if (!e || !Card.el) return;
    clearTimeout(Card.closeT); clearTimeout(Card.openT);
    const el = Card.el, q = (s) => el.querySelector(s);
    if (Card.term && Card.term !== t) Card.term.setAttribute("aria-expanded", "false"), Card.term.classList.remove("on");
    const same = Card.term === t && el.classList.contains("open");
    Card.term = t; Card.pinned = !!pin;
    t.setAttribute("aria-expanded", "true"); t.classList.add("on");
    if (!same) {
      q(".gl-title").textContent = e.term; q(".gl-short").textContent = e.short;
      const more = q(".gl-more"); more.textContent = e.more || ""; more.hidden = !e.more;
      const f = q(".gl-formula"); f.innerHTML = e.formula ? glFormula(e.formula) : ""; f.hidden = !e.formula;
      const here = (t.closest("[data-ch]") || {}).dataset?.ch, mod = e.chapter && WT.mods[e.chapter], a = q(".gl-link");
      if (mod && e.chapter !== here && document.getElementById(e.chapter)) { a.hidden = false; a.dataset.goto = e.chapter; a.href = "#" + e.chapter; a.textContent = `→ ${mod.num}: ${mod.title}`; }
      else a.hidden = true;
      if (el.classList.contains("open")) { el.classList.add("swap"); requestAnimationFrame(() => el.classList.remove("swap")); }
    }
    const sheet = sheetMQ.matches;
    el.setAttribute("role", sheet ? "dialog" : "tooltip");
    if (sheet) el.setAttribute("aria-modal", "false"); else el.removeAttribute("aria-modal");
    glPlace();
    if (!same) { el.classList.remove("open"); void el.offsetWidth; }
    el.classList.add("open");
    if (sheet && focusSheet) q(".gl-close").focus({ preventScroll: true });
  }
  function glClose(refocus) {
    clearTimeout(Card.openT); clearTimeout(Card.closeT);
    if (!Card.el || !Card.term) return;
    const t = Card.term; Card.term = null; Card.pinned = false;
    t.setAttribute("aria-expanded", "false"); t.classList.remove("on");
    Card.el.classList.remove("open");
    if (refocus) { Card.keyNav = true; t.focus({ preventScroll: true }); Card.keyNav = false; }
  }
  function glPlace() {
    const el = Card.el, t = Card.term; if (!el || !t) return;
    if (sheetMQ.matches) { el.style.left = el.style.top = el.style.maxHeight = ""; el.classList.remove("tight"); el.dataset.side = "sheet"; return; }
    // the line box of the word nearest the pointer (a term can wrap over two lines)
    const rects = [...t.getClientRects()]; let r = rects[0] || t.getBoundingClientRect();
    if (Card.py != null && rects.length > 1) r = rects.reduce((best, x) => (Math.abs((x.top + x.bottom) / 2 - Card.py) < Math.abs((best.top + best.bottom) / 2 - Card.py) ? x : best), r);
    const vw = document.documentElement.clientWidth, vh = innerHeight, M = 12, GAP = 11;
    const toc = document.querySelector(".toc"), tb = toc ? Math.max(0, toc.getBoundingClientRect().bottom) : 0;
    el.style.maxHeight = ""; const w = el.offsetWidth; let h = el.offsetHeight;
    const above = r.top - GAP - Math.max(M, tb + 6), below = vh - M - r.bottom - GAP;
    let side = above >= h || above >= below ? "above" : "below";
    if (side === "above" && above < h && below >= h) side = "below";
    const room = side === "above" ? above : below;
    el.classList.toggle("tight", h > room);
    if (h > room) { el.style.maxHeight = Math.max(120, room) + "px"; h = Math.max(120, room); }
    const cx = (r.left + r.right) / 2, left = clamp(cx - w / 2, M, vw - w - M);
    const top = side === "above" ? r.top - GAP - h : r.bottom + GAP;
    el.style.left = Math.round(left) + "px"; el.style.top = Math.round(top) + "px";
    el.dataset.side = side; el.style.setProperty("--ax", Math.round(clamp(cx - left, 18, w - 18)) + "px");
  }
  WT.term = { open: (t, pin) => glOpen(t, pin), close: () => glClose(false) };

  WT.gl = () => (WT.tl && Object.keys(WT.L.glossary).length ? WT.L.glossary : WT.glossary);
  // language picker in the contents bar
  function langToggle() {
    const nav = document.querySelector(".toc"); if (!nav || nav.querySelector(".lang")) return;
    const box = WT.langSwitch();
    const board = nav.querySelector(".board-link"); // keep the order: chapters, scoreboard link, language switch
    if (board) nav.appendChild(board);
    nav.appendChild(box);
  }
  WT.start = function () {
    const th = /[?&]theme=(dark|light)/.exec(location.search); if (th) document.documentElement.dataset.theme = th[1]; // dev aid
    readColors();
    const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    const PHONE = window.matchMedia("(max-width: 860px)").matches; // stacked layout: picture pinned on top, text below
    const navH = () => { const t = document.querySelector(".toc"); document.documentElement.style.setProperty("--navh", (t ? t.offsetHeight : 0) + "px"); };
    navH(); window.addEventListener("resize", navH);
    const chapters = [];
    const LEVELS = ["Intro", "Intermediate", "Advanced"]; // course level of each chapter (also listed on instructors.html)
    const LEVEL = { structure: 0, omp: 0, direct: 0, preeq: 1, compound: 1, decay: 1, gamma: 2, cascade: 1, fission: 1, resonance: 2, measure: 1, layers: 2 };
    document.querySelectorAll("[data-ch]").forEach((el) => {
      const id = el.dataset.ch, mod = WT.mods[id]; if (!mod) return;
      const esm = WT.tl && WT.L.ch[id]; if (esm) Object.assign(mod, esm);
      if (!el.querySelector(".stage") && mod.html) {
        el.id = id;
        const lv = LEVEL[id], lvt = lv == null ? "" : ` <span class="lvl l${lv}" title="${WT.ui ? WT.ui("lvl_title", "Level") : "Level"}">${WT.ui ? WT.ui("lvl" + lv, LEVELS[lv]) : LEVELS[lv]}</span>`;
        el.innerHTML = `<div class="stage"></div><div class="story"><header><div class="num">${mod.num || ""}${lvt}</div><h2>${mod.title || ""}</h2>${mod.lead ? `<p class="lead">${mod.lead}</p>` : ""}</header>${mod.html}</div>`;
      }
      const stage = el.querySelector(".stage"); const cv = document.createElement("canvas"); stage.appendChild(cv);
      const ctx = cv.getContext("2d"); const S = makeState(id); const ch = { id, el, stage, cv, ctx, S, mod, visible: false, g: null };
      try { mod.setup && mod.setup(S); } catch (e) { console.error(id, e); }
      // inline controls
      el.querySelectorAll("[data-bind]").forEach((inp) => {
        const k = inp.dataset.bind; S.set(k, parseFloat(inp.value));
        inp.addEventListener("input", () => { S.to(k, parseFloat(inp.value)); if (inp.dataset.instant !== undefined) S[k] = parseFloat(inp.value); });
      });
      el.querySelectorAll("[data-act]").forEach((b) => b.addEventListener("click", () => { const f = S.handlers[b.dataset.act]; f && f(); }));
      // step observer
      const steps = [...el.querySelectorAll(".step")];
      // stable deep links: #<chapter>-<n> (n from 1); the link mark beside each step copies the address
      steps.forEach((s, i) => { s.id = `${id}-${i + 1}`; const a = document.createElement("a"); a.className = "step-link"; a.href = "#" + s.id;
        a.setAttribute("aria-label", (WT.ui ? WT.ui("step_link", "Copy a link to this step") : "Copy a link to this step") + ` (${id}-${i + 1})`); a.title = a.getAttribute("aria-label");
        a.innerHTML = '<svg viewBox="0 0 16 16" width="15" height="15" aria-hidden="true"><path fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" d="M6.5 9.5l3-3M7 4.6l1.2-1.2a2.6 2.6 0 013.7 3.7L10.7 8.3M9 11.4l-1.2 1.2a2.6 2.6 0 01-3.7-3.7L5.3 7.7"/></svg>';
        a.addEventListener("click", (e) => { e.preventDefault(); const url = location.origin + location.pathname + WT.langQ() + "#" + s.id;
          history.replaceState(null, "", location.pathname + location.search + "#" + s.id);
          const done = () => { a.dataset.done = WT.ui ? WT.ui("link_copied", "Link copied") : "Link copied"; clearTimeout(a._t); a._t = setTimeout(() => delete a.dataset.done, 1600); };
          try { navigator.clipboard.writeText(url).then(done, done); } catch (err) { done(); } });
        s.prepend(a); });
      // screen readers: the drawing is an image whose description is the active step's heading and first sentence
      const describe = (i) => { const st = steps[i], h = st && st.querySelector("h3"), p = st && st.querySelector("p"); const first = p ? (p.textContent.trim().match(/^.*?[.!?](\s|$)/) || [p.textContent])[0].trim() : ""; cv.setAttribute("aria-label", `${WT.ui ? WT.ui("diagram", "Diagram") : "Diagram"}: ${(h ? h.textContent : mod.title || "").trim()}. ${first}`); };
      cv.setAttribute("role", "img"); describe(0);
      const io = new IntersectionObserver((ents) => {
        ents.forEach((en) => {
          if (!en.isIntersecting) return;
          const i = steps.indexOf(en.target); if (i === S.step) return;
          steps.forEach((s, j) => s.classList.toggle("active", j === i)); S.step = i; describe(i);
          const fn = mod.steps && mod.steps[i]; if (fn) { try { fn(S); } catch (e) { console.error(id, e); } }
          el.querySelectorAll("[data-bind]").forEach((inp) => { const k = inp.dataset.bind; if (typeof S.target[k] === "number" && Math.abs(parseFloat(inp.value) - S.target[k]) > 1e-9) inp.value = S.target[k]; });
        });
      }, { rootMargin: PHONE ? "-50% 0px -22% 0px" : "-45% 0px -45% 0px" }); // phones: the step being read sits just below the pinned picture
      steps.forEach((s) => io.observe(s));
      new IntersectionObserver((ents) => ents.forEach((en) => (ch.visible = en.isIntersecting)), { rootMargin: "100px 0px" }).observe(el);
      chapters.push(ch);
    });
    // contents bar
    const toc = document.querySelector(".toc ol");
    if (toc) {
      chapters.filter((c) => c.mod.title).forEach((c) => { const li = document.createElement("li"); li.innerHTML = `<a href="#${c.id}"><span>${(c.mod.num || "").replace(/[^0-9]/g, "")}</span>${c.mod.short || c.mod.title}</a>`; toc.appendChild(li); });
      const links = [...toc.querySelectorAll("a")];
      const nav = toc.parentElement, made = !nav.querySelector(".toc-menu"), menu = nav.querySelector(".toc-menu") || document.createElement("button"); // the chapter list opens from a button
      if (made) { menu.type = "button"; menu.className = "toc-menu"; menu.setAttribute("aria-expanded", "false"); menu.textContent = (WT.ui ? WT.ui("chapters", "Chapters") : "Chapters") + " ▾"; }
      menu.addEventListener("click", (e) => { e.stopPropagation(); const h = document.querySelector(".site"); h && h.classList.remove("menu-open"); const o = nav.classList.toggle("open"); menu.setAttribute("aria-expanded", String(o)); });
      links.forEach((a) => a.addEventListener("click", () => { nav.classList.remove("open"); menu.setAttribute("aria-expanded", "false"); }));
      if (made) nav.insertBefore(menu, toc);
      new IntersectionObserver((ents) => ents.forEach((en) => { if (en.isIntersecting) links.forEach((a) => a.classList.toggle("here", a.getAttribute("href") === "#" + en.target.id)); }), { rootMargin: "-50% 0px -50% 0px" })
        && chapters.forEach((c) => c.mod.title && links.length && new IntersectionObserver((ents) => ents.forEach((en) => { if (en.isIntersecting) { links.forEach((a) => a.classList.toggle("here", a.getAttribute("href") === "#" + c.id)); const h = toc.querySelector("a.here"); if (h && toc.offsetParent && toc.scrollWidth > toc.clientWidth) h.scrollIntoView({ block: "nearest", inline: "center" }); } }), { rootMargin: "-50% 0px -50% 0px" }).observe(c.el));
    }
    function resize() {
      chapters.forEach((ch) => {
        const r = ch.stage.getBoundingClientRect(), dpr = Math.min(PHONE ? 1.5 : 2, window.devicePixelRatio || 1); // phones: 1.5x keeps lines sharp with ~45 % fewer pixels
        ch.cv.width = Math.round(r.width * dpr); ch.cv.height = Math.round(r.height * dpr);
        ch.cv.style.width = r.width + "px"; ch.cv.style.height = r.height + "px";
        ch.ctx.setTransform(dpr, 0, 0, dpr, 0, 0); ch.g = makeG(ch.ctx, r.width, r.height);
      });
    }
    function outputs() {
      chapters.forEach((ch) => ch.el.querySelectorAll("[data-show]").forEach((o) => {
        const v = ch.S[o.dataset.show]; if (typeof v !== "number") return;
        const d = parseInt(o.dataset.fmt ?? "1", 10); o.textContent = WT.dec ? WT.dec(v.toFixed(d)) : v.toFixed(d);
      }));
    }
    let last = performance.now();
    function loop(now) {
      const dt = Math.min(0.05, (now - last) / 1000); last = now;
      chapters.forEach((ch) => {
        if (!ch.visible || !ch.g) return;
        ch.S.time += reduce ? 0 : dt; ch.S.ease(reduce ? 1 : dt);
        try { ch.g.clear(); ch.mod.frame(ch.g, ch.S, reduce ? 0 : dt); } catch (e) { console.error(ch.id, e); }
      });
      outputs(); requestAnimationFrame(loop);
    }
    window.addEventListener("resize", resize);
    const mq = window.matchMedia("(prefers-color-scheme: dark)");
    if (mq.addEventListener) mq.addEventListener("change", readColors);
    resize(); requestAnimationFrame(loop);
    WT.applyStatic(document, "title");
    langToggle();
    WT.keepLang();
    try { WT.termCount = glMark(); glCard(); } catch (e) { console.error("glossary", e); }
    try { const f = sessionStorage.getItem("wt_scroll"); if (f !== null) { sessionStorage.removeItem("wt_scroll"); requestAnimationFrame(() => window.scrollTo(0, +f * document.documentElement.scrollHeight)); } } catch (e) {}
    if (/[?&]i18ndump=1/.test(location.search)) setTimeout(() => { const pre = document.createElement("pre"); pre.id = "i18n-missing"; pre.textContent = [...WT.missing].join("\n"); document.body.appendChild(pre); }, 3000);
    // screenshot aid: ?shot=<chapter>:<step> shows only that chapter and step (headless Chrome does not paint script-scrolled pages)
    const m = /[?&]shot=([a-z]+):(\d+)/.exec(location.search);
    if (/[?&]shot=code\b/.test(location.search)) document.body.classList.add("shot-code"); // ?shot=code shows only "Where this lives in the code"
    if (m) {
      document.body.classList.add("shot");
      const el = document.querySelector(`[data-ch="${m[1]}"]`); if (el) el.classList.add("shot-target");
      const steps = el ? el.querySelectorAll(".step") : []; steps.forEach((x, i) => x.classList.toggle("shot-step", i === +m[2]));
      const ch = chapters.find((c) => c.id === m[1]);
      if (ch) { for (let i = 0; i <= +m[2]; i++) { const fn = ch.mod.steps && ch.mod.steps[i]; fn && fn(ch.S); } ch.S.step = +m[2]; ch.visible = true; }
      resize();
      // ?shot=<chapter>:<step>&term=<key> also opens that term's card (dev aid for screenshots)
      const tm = /[?&]term=([A-Za-z0-9]+)/.exec(location.search);
      if (tm) {
        const pick = () => { const t = [...document.querySelectorAll(`.term[data-term="${tm[1]}"]`)].find((x) => x.getClientRects().length);
          if (t) { Card.el && Card.el.classList.add("instant"); glOpen(t, true); } };
        setTimeout(pick, 200); if (document.fonts && document.fonts.ready) document.fonts.ready.then(() => setTimeout(pick, 50));
      }
    }
    if (document.fonts && document.fonts.ready) document.fonts.ready.then(resize);
    // deep links (#omp, #omp-3): scroll there once the page has its final layout; a step lands where it becomes active
    const goHash = (smooth) => {
      const t = document.getElementById(decodeURIComponent(location.hash.slice(1))); if (!t || m) return;
      const isStep = t.classList.contains("step"); if (!isStep && !t.matches("[data-ch]")) return;
      const nh = document.querySelector(".toc") ? document.querySelector(".toc").offsetHeight : 0;
      const y = t.getBoundingClientRect().top + window.scrollY - (isStep ? window.innerHeight * (PHONE ? 0.5 : 0.38) : nh);
      window.scrollTo({ top: Math.max(0, y), behavior: smooth ? "smooth" : "instant" });
    };
    if (location.hash) { goHash(false); if (document.fonts && document.fonts.ready) document.fonts.ready.then(() => requestAnimationFrame(() => goHash(false))); }
    window.addEventListener("hashchange", () => goHash(!reduce));
  };
})();
