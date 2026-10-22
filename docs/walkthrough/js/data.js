/* Data explorer (data.html): a chart of nuclides coloured by how each is known, and for any nuclide the library's
 * predicted curves (with 68 / 95 % bands) beside every curated measurement. Data: data/index.json and data/n/<Z>/<A>.json,
 * built by scripts/build_site_data.py from library/v0.1, data/curation and incognita/bench. Plain script, no build. */
(function () {
  "use strict";
  const es = WT.lang === "es", T = (k, en) => WT.ui(k, en);
  const $ = (s) => document.querySelector(s);
  const th = /[?&]theme=(dark|light)/.exec(location.search); if (th) document.documentElement.dataset.theme = th[1];
  const esc = (s) => String(s ?? "").replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
  const clamp = (v, a, b) => Math.max(a, Math.min(b, v)), log10 = Math.log10;

  // ---------- static text, language switch ----------
  if (es) {
    if (WT.es.ui.dx_title) document.title = WT.es.ui.dx_title;
    document.querySelectorAll("[data-i18n]").forEach((el) => { const t = WT.es.ui[el.dataset.i18n]; if (t != null) el.innerHTML = t; });
    document.querySelectorAll("[data-i18n-aria]").forEach((el) => { const t = WT.es.ui[el.dataset.i18nAria]; if (t != null) el.setAttribute("aria-label", t); });
    document.querySelectorAll("[data-i18n-ph]").forEach((el) => { const t = WT.es.ui[el.dataset.i18nPh]; if (t != null) el.setAttribute("placeholder", t); });
  }
  // links that keep the language and the EN | ES switch: js/nav.js

  // ---------- formatting ----------
  const num = (v, p = 3) => (v == null || !isFinite(v) ? "–" : WT.dec(Math.abs(v) >= 1e5 || (Math.abs(v) < 1e-3 && v !== 0) ? v.toExponential(p - 1) : (+v.toPrecision(p)).toString()));
  const fmtE = (ev) => (ev >= 1e6 ? num(ev / 1e6) + " MeV" : ev >= 1e3 ? num(ev / 1e3) + " keV" : num(ev) + " eV");
  const SUP = { "-": "⁻", 0: "⁰", 1: "¹", 2: "²", 3: "³", 4: "⁴", 5: "⁵", 6: "⁶", 7: "⁷", 8: "⁸", 9: "⁹" };
  const pow10 = (k) => "10" + String(k).split("").map((c) => SUP[c]).join("");
  const decE = (k) => (k >= -2 ? fmtE(10 ** k) : pow10(k) + " eV"), decY = (k, u) => (k >= -2 && k <= 4 ? num(10 ** k) : pow10(k)) + " " + u;
  const TIERS = [T("dx_t0", "Measured"), T("dx_t1", "Anchored to a measured MACS"), T("dx_t2", "Interpolated from neighbours"), T("dx_t3", "Extrapolated (engine only)")];
  const TIER_SHORT = [T("dx_ts0", "measured"), T("dx_ts1", "anchored"), T("dx_ts2", "interpolated"), T("dx_ts3", "extrapolated")];
  const DEC = { k: T("dx_keep", "kept"), d: T("dx_down", "down-weighted"), x: T("dx_excl", "excluded"), f: T("dx_fix", "unit fixed") };
  const CH = { cap: T("dx_cap", "Capture (n,γ)"), n2n: "(n,2n)", np: "(n,p)", na: "(n,α)", macs: T("dx_macs", "Stellar average (MACS)") };

  // ---------- colours (CSS tokens on .dx, light and dark) ----------
  let C = {};
  function readColors() {
    const cs = getComputedStyle($(".dx"));
    ["surface", "ink", "soft", "faint", "line", "grid", "curve", "meas", "alt", "none", "t0", "t1", "t2", "t3", "sel", "l1", "l2", "l3"].forEach((k) => (C[k] = cs.getPropertyValue("--dx-" + k).trim()));
    C.ramp = [1, 2, 3, 4, 5, 6, 7].map((i) => cs.getPropertyValue("--dx-r" + i).trim());
  }
  const rgba = (hex, a) => { const n = parseInt(hex.replace("#", ""), 16); return `rgba(${(n >> 16) & 255},${(n >> 8) & 255},${n & 255},${a})`; };
  const SANS = '"IBM Plex Sans", "Segoe UI", system-ui, sans-serif';

  function setupCanvas(cv, h) {
    const dpr = Math.min(2, window.devicePixelRatio || 1), w = cv.parentElement.clientWidth;
    cv.style.width = w + "px"; cv.style.height = h + "px"; cv.width = Math.round(w * dpr); cv.height = Math.round(h * dpr);
    const ctx = cv.getContext("2d"); ctx.setTransform(dpr, 0, 0, dpr, 0, 0); return { ctx, W: w, H: h, dpr };
  }

  // ---------- data ----------
  let IDX = null, rows = [], byKey = new Map(), sel = null, mode = "tier";
  // one small file per nuclide (data/n/<Z>/<A|nat>.json), fetched the first time that nuclide is opened and kept in memory;
  // a failed fetch is forgotten so the next try fetches again
  const nkey = (Z, A) => `${Z}/${A || "nat"}`, ncache = new Map(), ndata = new Map();
  const loadNuc = (Z, A) => { const k = nkey(Z, A);
    if (!ncache.has(k)) ncache.set(k, fetch(`data/n/${k}.json`).then((r) => { if (!r.ok) throw new Error("HTTP " + r.status); return r.json(); })
      .then((d) => { ndata.set(k, d); return d; }, (e) => { ncache.delete(k); throw e; }));
    return ncache.get(k); };
  // evaluated libraries (comparators only, never used by INCOGNITA): data/lib/<Z>.json, fetched only when the overlay box is ticked.
  // Built offline by scripts/build_site_overlay.py (display-only); a missing file just means no library covers that element.
  const lcache = new Map(), LIBS = ["endfb8.1", "jeff4.0", "tendl2025"];
  const loadLib = (Z) => lcache.get(Z) || lcache.set(Z, fetch(`data/lib/${Z}.json`).then((r) => (r.ok ? r.json() : null)).catch(() => null)).get(Z);
  let libOn = false;
  const nameOf = (Z, A) => (A ? `${IDX.sym[Z]}-${A}` : `${IDX.sym[Z]} (${T("dx_nat", "natural")})`);

  // ---------- chart of nuclides ----------
  const cv = $("#dx-chart"), tip = $("#dx-tip");
  let G = null, view = { x0: 0, y0: 0, s: 4 }, bounds = { n0: 0, n1: 180, z0: 0, z1: 110 }, hover = null;
  const MAGIC = [8, 20, 28, 50, 82, 126];
  function colorOf(r) {
    if (mode === "tier") return r.tier >= 0 ? C["t" + r.tier] : C.none;
    if (mode === "macs") { if (!(r.macs > 0)) return C.none; const u = clamp((log10(r.macs) + 1) / 5, 0, 0.999); return C.ramp[Math.floor(u * C.ramp.length)]; } // 0.1 mb .. 10 b
    return r.ncap + r.nmxw > 0 ? C.meas : r.nn2n + r.nnp + r.nna > 0 ? C.alt : C.none;
  }
  function fit() {
    const H = G.H, W = G.W, s = Math.min(W / (bounds.n1 - bounds.n0 + 4), H / (bounds.z1 - bounds.z0 + 4));
    if (H > W * 1.15) { const s2 = H / (bounds.z1 - bounds.z0 + 6); view = { s: s2, x0: 62 - W / s2 / 2, y0: bounds.z0 - 3 }; return; } // tall phone screens: fill the height, centred on the valley; pan sideways
    view = { s, x0: bounds.n0 - 2 - (W / s - (bounds.n1 - bounds.n0 + 4)) / 2, y0: bounds.z0 - 2 - (H / s - (bounds.z1 - bounds.z0 + 4)) / 2 };
  }
  const toX = (N) => (N - view.x0) * view.s, toY = (Z) => G.H - (Z - view.y0 + 1) * view.s;
  const fromXY = (x, y) => ({ N: Math.floor(x / view.s + view.x0), Z: Math.floor((G.H - y) / view.s + view.y0) });
  // drawn in two steps: a cached picture of every square with its glow (redrawn only when the view, colouring or size changes),
  // then the hover and selection outlines on top, so moving the mouse costs one image copy; redraws are batched to one per frame
  const baseCv = document.createElement("canvas"), glowCv = document.createElement("canvas");
  let baseKey = "", chartRaf = 0, zooming = false, zt = 0;
  function drawChart() { if (!chartRaf) chartRaf = requestAnimationFrame(() => { chartRaf = 0; paintChart(); }); }
  const fresh = (c, w, h, dpr) => { const g = c.getContext("2d"); if (c.width !== w || c.height !== h) { c.width = w; c.height = h; } g.setTransform(1, 0, 0, 1, 0, 0); g.clearRect(0, 0, w, h); g.setTransform(dpr, 0, 0, dpr, 0, 0); return g; };
  function paintChart() {
    if (!G) return;
    const { ctx, dpr } = G, s = view.s, gap = s > 5 ? 1 : 0, glow = !(drag && moved > 4) && !pinch && !zooming; // the glow is skipped while dragging, pinching or wheel-zooming and restored after
    const key = [view.x0, view.y0, s, mode, cv.width, cv.height, glow, C.surface, C.t0].join();
    if (key !== baseKey) { baseKey = key; drawBase(glow); }
    ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.clearRect(0, 0, cv.width, cv.height); ctx.drawImage(baseCv, 0, 0); ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    // selection and hover
    for (const [r, col, w] of [[hover, C.ink, 1.5], [sel, C.sel, 2.5]]) if (r && r.A) { ctx.strokeStyle = col; ctx.lineWidth = w; ctx.strokeRect(toX(r.A - r.Z) - 1, toY(r.Z) - 1, s + 1 - gap, s + 1 - gap); }
  }
  function drawBase(glow) {
    const { W, H, dpr } = G, s = view.s, gap = s > 5 ? 1 : 0, ctx = fresh(baseCv, cv.width, cv.height, dpr);
    ctx.fillStyle = C.surface; ctx.fillRect(0, 0, W, H);
    // magic numbers: faint lines where shells close
    ctx.strokeStyle = C.grid; ctx.lineWidth = 1;
    for (const m of MAGIC) { const x = toX(m) - 0.5 * gap, y = toY(m) + s; ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, H); ctx.stroke(); ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(W, y); ctx.stroke(); }
    for (const r of rows) {
      if (!r.A) continue;
      const x = toX(r.A - r.Z), y = toY(r.Z); if (x < -s || x > W || y < -s || y > H) continue;
      ctx.fillStyle = colorOf(r); ctx.fillRect(x, y, s - gap, s - gap);
    }
    // glow on the nuclides that stand out in this view (measured, or with measured data), so the valley of stability shines
    if (glow) {
      const lit = rows.filter((r) => { if (!r.A || !(mode === "tier" ? r.tier === 0 || r.tier === 1 : mode === "meas" ? r.ncap + r.nmxw > 0 : r.macs > 300)) return false;
        const x = toX(r.A - r.Z), y = toY(r.Z); return !(x < -s || x > W || y < -s || y > H); });
      const blur = Math.max(6, s * 1.4);
      if (typeof ctx.filter === "string") { // one blur of all lit squares at once: the same picture as a shadow per square, far cheaper
        const g = fresh(glowCv, cv.width, cv.height, dpr);
        for (const r of lit) { g.fillStyle = colorOf(r); g.fillRect(toX(r.A - r.Z), toY(r.Z), s - gap, s - gap); }
        ctx.save(); ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.globalCompositeOperation = "lighter"; ctx.globalAlpha = 0.55;
        ctx.filter = `blur(${blur / 2}px)`; ctx.drawImage(glowCv, 0, 0); ctx.filter = "none"; ctx.drawImage(glowCv, 0, 0); ctx.restore();
      } else {
        ctx.save(); ctx.globalCompositeOperation = "lighter";
        for (const r of lit) { const col = colorOf(r); ctx.shadowColor = col; ctx.shadowBlur = blur; ctx.fillStyle = col; ctx.globalAlpha = 0.55; ctx.fillRect(toX(r.A - r.Z), toY(r.Z), s - gap, s - gap); }
        ctx.restore();
      }
    }
    // labels: element symbols along the left edge of each row, mass numbers inside cells when large
    ctx.textBaseline = "middle";
    if (s >= 9) {
      ctx.font = `600 ${Math.min(13, s * 0.62)}px ${SANS}`; ctx.textAlign = "right"; ctx.fillStyle = C.soft;
      const first = new Map(); for (const r of rows) if (r.A && (!first.has(r.Z) || r.A - r.Z < first.get(r.Z))) first.set(r.Z, r.A - r.Z);
      for (const [Z, N] of first) { const x = toX(N) - 4, y = toY(Z) + s / 2; if (y > 0 && y < H && x > 10) ctx.fillText(IDX.sym[Z], x, y); }
    }
    if (s >= 26) {
      ctx.textAlign = "center";
      for (const r of rows) { if (!r.A) continue; const x = toX(r.A - r.Z), y = toY(r.Z); if (x < -s || x > W || y < -s || y > H) continue;
        const dark = mode === "tier" ? r.tier <= 1 : mode === "macs" ? r.macs > 30 : false;
        ctx.fillStyle = dark ? "#ffffff" : C.ink; ctx.font = `600 ${Math.min(13, s * 0.3)}px ${SANS}`; ctx.fillText(IDX.sym[r.Z], x + (s - gap) / 2, y + s * 0.38);
        ctx.font = `500 ${Math.min(11, s * 0.24)}px ${SANS}`; ctx.fillText(String(r.A), x + (s - gap) / 2, y + s * 0.68); }
    }
    // axis hints
    ctx.font = `500 12px ${SANS}`; ctx.fillStyle = C.soft; ctx.textAlign = "left";
    let lastX = -99, lastY = 1e9; for (const m of MAGIC) { const x = toX(m) + 3; if (x > 20 && x < W - 40 && x - lastX > 44) { ctx.fillText(`N=${m}`, x, H - 10); lastX = x; } const y = toY(m) + s / 2; if (y > 14 && y < H - 20 && lastY - y > 18) { ctx.fillText(`Z=${m}`, 6, y); lastY = y; } }
  }
  function legend() {
    const L = $("#dx-legend");
    const sw = (c, t) => `<span class="dx-key"><i style="background:${c}"></i>${t}</span>`;
    if (mode === "tier") L.innerHTML = [0, 1, 2, 3].map((i) => sw(C["t" + i], TIERS[i])).join("");
    else if (mode === "meas") L.innerHTML = sw(C.meas, T("dx_l_cap", "capture measured")) + sw(C.alt, T("dx_l_thr", "only (n,2n), (n,p) or (n,α) measured")) + sw(C.none, T("dx_l_none", "no measurement in this set"));
    else L.innerHTML = `<span class="dx-ramp"><span>0.1 mb</span><i style="background:linear-gradient(to right,${C.ramp.join(",")})"></i><span>10 b</span></span><span class="dx-key">${T("dx_l_macs", "predicted Maxwellian-averaged capture at kT = 30 keV (log scale)")}</span>` + sw(C.none, T("dx_l_nomacs", "no value"));
  }

  // pointer: pan, zoom, pinch, hover, click
  const pts = new Map(); let drag = null, moved = 0, pinch = null, tipR = null, tipW = 0, tipH = 0, pf = 0;
  // a nuclide's file is fetched as soon as the pointer rests on it (or presses it), so it is usually here by the time of the click
  const prefetch = (r) => { if (r && IDX) loadNuc(r.Z, r.A).catch(() => {}); };
  const at = (e) => { const { N, Z } = fromXY(e.offsetX, e.offsetY); return byKey.get(Z + "-" + (N + Z)) || null; };
  cv.addEventListener("pointerdown", (e) => { prefetch(at(e)); cv.setPointerCapture(e.pointerId); pts.set(e.pointerId, { x: e.offsetX, y: e.offsetY }); moved = 0; drag = { x: e.offsetX, y: e.offsetY, v: { ...view } };
    if (pts.size === 2) { const [a, b] = [...pts.values()]; pinch = { d: Math.hypot(a.x - b.x, a.y - b.y), v: { ...view }, mx: (a.x + b.x) / 2, my: (a.y + b.y) / 2 }; } });
  cv.addEventListener("pointermove", (e) => {
    if (pts.has(e.pointerId)) pts.set(e.pointerId, { x: e.offsetX, y: e.offsetY });
    if (pinch && pts.size === 2) { const [a, b] = [...pts.values()], d = Math.hypot(a.x - b.x, a.y - b.y); zoomAt(pinch.mx, pinch.my, pinch.v.s * d / pinch.d, pinch.v); moved = 99; return; }
    if (drag && pts.size === 1) { const dx = e.offsetX - drag.x, dy = e.offsetY - drag.y; moved = Math.max(moved, Math.abs(dx) + Math.abs(dy)); view.x0 = drag.v.x0 - dx / view.s; view.y0 = drag.v.y0 + dy / view.s; drawChart(); return; }
    const r = at(e);
    if (r !== hover) { hover = r; drawChart(); clearTimeout(pf); if (r) pf = setTimeout(() => prefetch(r), 150); }
    if (r) { // the tooltip is rebuilt and measured only when it changes nuclide; between those, moving it forces no layout
      if (r !== tipR) { tipR = r; tip.innerHTML = chartTip(r); tip.hidden = false; tip.style.left = tip.style.top = "0px"; tipW = tip.offsetWidth; tipH = tip.offsetHeight; }
      const x = e.offsetX, y = e.offsetY; tip.style.transform = `translate(${clamp(x + 14, 4, G.W - tipW - 4)}px,${y - tipH - 12 < 0 ? y + 16 : y - tipH - 12}px)`; // a transform: no layout
    } else { tip.hidden = true; tipR = null; }
  });
  const endPtr = (e) => { pts.delete(e.pointerId); if (pts.size < 2) pinch = null;
    if (pts.size === 0 && drag) { if (moved < 5 && e.type === "pointerup") { const { N, Z } = fromXY(e.offsetX, e.offsetY), r = byKey.get(Z + "-" + (N + Z)); if (r) select(r); } drag = null; drawChart(); } };
  cv.addEventListener("pointerup", endPtr); cv.addEventListener("pointercancel", endPtr);
  cv.addEventListener("pointerleave", () => { hover = null; tip.hidden = true; tipR = null; clearTimeout(pf); drawChart(); });
  cv.addEventListener("wheel", (e) => { e.preventDefault(); zooming = true; clearTimeout(zt); zt = setTimeout(() => { zooming = false; drawChart(); }, 160); zoomAt(e.offsetX, e.offsetY, view.s * Math.exp(-e.deltaY * 0.0015)); }, { passive: false });
  function zoomAt(x, y, s, base = view) { s = clamp(s, 1.2, 60); const N = x / base.s + base.x0, Z = (G.H - y) / base.s + base.y0; view = { s, x0: N - x / s, y0: Z - (G.H - y) / s }; drawChart(); }
  document.querySelectorAll(".dx-zoom button").forEach((b) => b.addEventListener("click", () => { const z = +b.dataset.z; if (!z) { fit(); drawChart(); } else zoomAt(G.W / 2, G.H / 2, view.s * (z > 0 ? 1.6 : 1 / 1.6)); }));
  /** EXFOR link for a dataset id like "32234/32234009/1" (entry/subentry/pointer): the 8-character subentry, or null.
   *  Entry-only ids stay unlinked: no entry-level IAEA URL could be verified (the site sits behind a bot check). */
  function exforOf(id) {
    const s = String(id || "").split("/").find((p) => /^[0-9A-Z]\d{7}$/.test(p));
    return s ? { id: s, url: `https://www-nds.iaea.org/exfor/servlet/X4sGetSubent?subID=${s}` } : null;
  }
  function place(el, x, y, host) { const w = el.offsetWidth, h = el.offsetHeight, W = host.clientWidth; el.style.left = clamp(x + 14, 4, W - w - 4) + "px"; el.style.top = (y - h - 12 < 0 ? y + 16 : y - h - 12) + "px"; }
  function chartTip(r) {
    const bits = [`<b>${esc(nameOf(r.Z, r.A))}</b> <span class="dx-faint">Z ${r.Z} · N ${r.A - r.Z}</span>`];
    if (r.tier >= 0) bits.push(TIERS[r.tier]);
    if (r.macs > 0) bits.push(`MACS 30 keV ≈ ${num(r.macs)} mb${r.u30 ? ` (×/÷ ${num(r.u30, 2)})` : ""}`);
    const m = []; if (r.ncap + r.nmxw) m.push(`${r.nds} ${T("dx_capsets", "capture datasets")}`); for (const [k, n] of [["n2n", r.nn2n], ["np", r.nnp], ["na", r.nna]]) if (n) m.push(`${CH[k]} ${n}`);
    if (m.length) bits.push(T("dx_measured", "Measured") + ": " + m.join(", "));
    return bits.join("<br>");
  }
  document.querySelectorAll(".dx-seg button").forEach((b) => b.addEventListener("click", () => {
    mode = b.dataset.mode; document.querySelectorAll(".dx-seg button").forEach((x) => x.setAttribute("aria-pressed", String(x === b))); legend(); drawChart(); }));

  // ---------- search ----------
  const q = $("#dx-q");
  function parseQ(s) {
    s = s.trim(); if (!s) return null;
    let m = /^([A-Za-z]{1,2})\s*-?\s*(\d{1,3})$/.exec(s) || /^(\d{1,3})\s*-?\s*([A-Za-z]{1,2})$/.exec(s);
    if (m) { const [sy, A] = /^\d/.test(m[1]) ? [m[2], +m[1]] : [m[1], +m[2]]; const Z = IDX.sym.findIndex((x) => x.toLowerCase() === sy.toLowerCase()); return Z > 0 ? byKey.get(Z + "-" + A) || null : null; }
    m = /^([A-Za-z]{1,2})\s*(\(.*\)|nat.*)?$/i.exec(s);
    if (m) { const Z = IDX.sym.findIndex((x) => x.toLowerCase() === m[1].toLowerCase()); if (Z > 0) { if (m[2] && IDX.natural.includes(Z)) return byKey.get(Z + "-0"); const c = rows.filter((r) => r.Z === Z && r.A).sort((a, b) => (a.tier - b.tier) || (b.nds - a.nds)); return c[0] || null; } }
    return null;
  }
  // suggestions: filter as you type (symbol, mass number, or element name), arrow keys + Enter
  const sug = $("#dx-sugg"); let hits = [], hi = -1;
  const norm = (s) => s.toLowerCase().replace(/[\s\-()]/g, "");
  function suggest() {
    const t = norm(q.value); hits = []; hi = -1;
    if (t) {
      for (const r of rows) {
        const keys = r.keys || (r.keys = ((sy, a) => [sy + a, a + sy, sy])(IDX.sym[r.Z].toLowerCase(), r.A ? String(r.A) : "nat")); // built once per nuclide
        let s = -1; keys.forEach((k, i) => { if (k === t) s = Math.max(s, 100 - i); else if (k.startsWith(t)) s = Math.max(s, 50 - i); });
        if (s >= 0) hits.push([s + (r.tier === 0 ? 3 : 0) + Math.min(2, (r.nds || 0) / 50), r]);
      }
      hits.sort((x, y) => y[0] - x[0] || x[1].Z - y[1].Z || x[1].A - y[1].A); hits = hits.slice(0, 12).map((h) => h[1]);
    }
    sug.innerHTML = hits.map((r, i) => `<li role="option" id="dx-o${i}" data-i="${i}"><b>${esc(nameOf(r.Z, r.A))}</b> <span class="dx-faint">${r.tier >= 0 ? TIER_SHORT[r.tier] : ""}${r.nds ? ` · ${r.nds} ${T("dx_sets", "datasets")}` : ""}</span></li>`).join("");
    sug.hidden = !hits.length; q.setAttribute("aria-expanded", String(!!hits.length)); q.classList.toggle("bad", !!t && !hits.length);
  }
  const mark = () => { sug.querySelectorAll("li").forEach((li, i) => li.classList.toggle("on", i === hi)); if (hi >= 0) q.setAttribute("aria-activedescendant", "dx-o" + hi); else q.removeAttribute("aria-activedescendant"); };
  const pick = (r) => { if (!r) return; q.value = nameOf(r.Z, r.A); sug.hidden = true; q.setAttribute("aria-expanded", "false"); q.classList.remove("bad"); select(r, true); };
  q.addEventListener("input", suggest); q.addEventListener("focus", () => q.value && suggest());
  q.addEventListener("keydown", (e) => {
    if (e.key === "ArrowDown" && hits.length) { e.preventDefault(); hi = (hi + 1) % hits.length; mark(); }
    else if (e.key === "ArrowUp" && hits.length) { e.preventDefault(); hi = (hi - 1 + hits.length) % hits.length; mark(); }
    else if (e.key === "Enter") { e.preventDefault(); pick(hits[hi >= 0 ? hi : 0] || parseQ(q.value)); }
    else if (e.key === "Escape") { sug.hidden = true; q.setAttribute("aria-expanded", "false"); }
  });
  sug.addEventListener("pointerdown", (e) => { const li = e.target.closest("li"); if (li) { e.preventDefault(); pick(hits[+li.dataset.i]); } });
  q.addEventListener("blur", () => setTimeout(() => { sug.hidden = true; q.setAttribute("aria-expanded", "false"); }, 120));

  // ---------- the nucleus itself: Z protons and N neutrons packed in a sphere, slowly turning (as in the hero) ----------
  const atom = { cv: $("#dx-atom"), pts: [], t: 0, tx: 0, ty: 0, run: false, key: "" };
  function ball(col) {
    const c = document.createElement("canvas"); c.width = c.height = 64; const g = c.getContext("2d"), gr = g.createRadialGradient(20, 18, 2, 32, 32, 32);
    gr.addColorStop(0, "#ffffff"); gr.addColorStop(0.22, col); gr.addColorStop(0.75, col); gr.addColorStop(1, "#0b1020");
    g.fillStyle = gr; g.beginPath(); g.arc(32, 32, 31, 0, Math.PI * 2); g.fill(); return c;
  }
  const BALL = { p: ball("#ff6a5c"), n: ball("#6f8cff") };
  function atomSet(Z, A) {
    const key = Z + "-" + A; if (atom.key === key) return; atom.key = key;
    const n = Math.max(1, A || Z * 2), rnd = (() => { let s = (Z * 977 + n * 131) % 2147483647 || 1; return () => (s = (s * 16807) % 2147483647) / 2147483647; })();
    const P = []; for (let i = 0; i < n; i++) { let x, y, z; do { x = rnd() * 2 - 1; y = rnd() * 2 - 1; z = rnd() * 2 - 1; } while (x * x + y * y + z * z > 1); P.push({ x, y, z, p: false }); }
    const rb = Math.cbrt(0.62 / n), d0 = 2 * rb * 0.97, lim = 1 - rb;
    for (let it = 0; it < (n > 150 ? 30 : 50); it++) {
      for (let i = 0; i < n; i++) for (let j = i + 1; j < n; j++) { const a = P[i], b = P[j], dx = b.x - a.x, dy = b.y - a.y, dz = b.z - a.z, d = Math.sqrt(dx * dx + dy * dy + dz * dz) || 1e-6; if (d < d0) { const k = (d0 - d) / d * 0.5; a.x -= dx * k; a.y -= dy * k; a.z -= dz * k; b.x += dx * k; b.y += dy * k; b.z += dz * k; } }
      for (const a of P) { const d = Math.hypot(a.x, a.y, a.z); if (d > lim) { a.x *= lim / d; a.y *= lim / d; a.z *= lim / d; } }
    }
    const idx = P.map((_, i) => i); for (let i = n - 1; i > 0; i--) { const j = Math.floor(rnd() * (i + 1)); [idx[i], idx[j]] = [idx[j], idx[i]]; }
    for (let k = 0; k < Math.min(Z, n); k++) P[idx[k]].p = true;
    atom.pts = P; atom.rb = rb; atom.born = performance.now();
    atomGo();
  }
  // it turns only while it is on screen, at about 30 frames a second (the turn is slow, so this looks the same and halves the cost)
  atom.vis = true;
  const atomGo = () => { if (!atom.run && atom.vis && !document.hidden && atom.pts.length) { atom.run = true; atom.last = 0; requestAnimationFrame(atomFrame); } };
  if (atom.cv && "IntersectionObserver" in window) new IntersectionObserver((es) => { atom.vis = es[es.length - 1].isIntersecting; atomGo(); }).observe(atom.cv);
  document.addEventListener("visibilitychange", atomGo);
  // the packing is worked out after the plot's first frame is on screen, so opening a nuclide never waits for it
  const atomSoon = (Z, A) => requestAnimationFrame(() => setTimeout(() => atomSet(Z, A), 0));
  function atomFrame(now) {
    const cv2 = atom.cv; if (!cv2 || !atom.pts.length || !atom.vis || document.hidden) { atom.run = false; return; }
    if (now - atom.last < 30) { requestAnimationFrame(atomFrame); return; } atom.last = now;
    const S = cv2.clientWidth, dpr = Math.min(2, window.devicePixelRatio || 1);
    const px = Math.round(S * dpr); if (cv2.width !== px || cv2.height !== px) { cv2.width = cv2.height = px; } // check both: a new canvas starts at 300x150, which matches the width at 125 % scaling
    const g = cv2.getContext("2d"); g.setTransform(dpr, 0, 0, dpr, 0, 0); g.clearRect(0, 0, S, S);
    const grow = Math.min(1, (now - atom.born) / 600), e = 1 - Math.pow(1 - grow, 3), R = S * 0.36 * e, cx = S / 2, cy = S / 2;
    const glow = g.createRadialGradient(cx, cy, 0, cx, cy, S * 0.5); glow.addColorStop(0, "rgba(255,170,100,.22)"); glow.addColorStop(0.5, "rgba(80,120,255,.10)"); glow.addColorStop(1, "rgba(0,0,0,0)");
    g.fillStyle = glow; g.fillRect(0, 0, S, S);
    const ya = now / 4000 + atom.tx * 0.6, pa = 0.3 + atom.ty * 0.4, cY = Math.cos(ya), sY = Math.sin(ya), cP = Math.cos(pa), sP = Math.sin(pa), D = 5;
    const L = atom.pts.map((a) => { let x = a.x * cY + a.z * sY, z = -a.x * sY + a.z * cY; const y = a.y * cP - z * sP; z = a.y * sP + z * cP; const k = D / (D - z); return { X: cx + x * k * R, Y: cy + y * k * R, z, k, p: a.p }; }).sort((a, b) => a.z - b.z);
    const br = atom.rb * R * 1.08;
    for (const q of L) { g.globalAlpha = 0.55 + 0.45 * (q.z + 1) / 2; g.drawImage(q.p ? BALL.p : BALL.n, q.X - br * q.k, q.Y - br * q.k, 2 * br * q.k, 2 * br * q.k); }
    g.globalAlpha = 1;
    requestAnimationFrame(atomFrame);
  }
  if (atom.cv) atom.cv.parentElement.addEventListener("pointermove", (e) => { const r = atom.cv.getBoundingClientRect(); atom.tx = (e.clientX - r.left) / r.width - 0.5; atom.ty = (e.clientY - r.top) / r.height - 0.5; });

  // ---------- one nuclide ----------
  let tab = "cap", cur = null, hl = null, P = null, showExcl = false, tableOpen = false;
  /** Loading state while nuclide r's file is on its way (r null: done); with err, say it failed and offer a retry. */
  function busy(r, err) {
    const box = $("#dx-nuc"), s = $("#dx-status"), on = !!r && !err;
    box.classList.toggle("dx-loading", !!r); box.setAttribute("aria-busy", String(on)); box.classList.toggle("dx-empty", !cur);
    if (!r) { s.hidden = true; return; }
    box.hidden = false; $("#dx-name").textContent = nameOf(r.Z, r.A); atomSoon(r.Z, r.A);
    $("#dx-tile").innerHTML = `<span>${IDX.sym[r.Z]}</span>`; $("#dx-facts").innerHTML = ""; $("#dx-stats").innerHTML = "";
    s.hidden = false;
    s.innerHTML = err ? `${T("dx_nload", "Could not load this nuclide.")} <button type="button" class="dx-link" id="dx-retry">${T("dx_retry", "Try again")}</button>`
      : `${T("dx_loading", "Loading")} ${esc(nameOf(r.Z, r.A))}…`;
    if (err) $("#dx-retry").addEventListener("click", () => select(r, false, true));
  }
  async function select(r, center, stay) {
    sel = r; drawChart();
    if (center && r.A) { view.x0 = r.A - r.Z - G.W / view.s / 2; view.y0 = r.Z - G.H / view.s / 2; if (view.s < 14) zoomAt(G.W / 2, G.H / 2, 18); drawChart(); }
    history.replaceState(null, "", location.pathname + location.search + "#" + (r.A ? `${IDX.sym[r.Z]}-${r.A}` : `${IDX.sym[r.Z]}-nat`));
    if (!ndata.has(nkey(r.Z, r.A)) || (libOn && !lcache.has(r.Z))) busy(r);
    let d0, lz; // the nuclide's file and, if the overlay is ticked, its element's library file
    try { [d0, lz] = await Promise.all([loadNuc(r.Z, r.A), libOn ? loadLib(r.Z) : null]); } catch (e) { if (sel === r) busy(r, e); return; }
    if (sel !== r) return;
    cur = { r, d: d0, lib: libOf(lz, r) }; busy(null);
    buildTabs();
    $("#dx-nuc").hidden = false; hl = null;
    $("#dx-name").textContent = nameOf(r.Z, r.A);
    atomSoon(r.Z, r.A);
    $("#dx-tile").innerHTML = `<span>${IDX.sym[r.Z]}</span>`; $("#dx-tile").title = "Z = " + r.Z;
    const d = cur.d, f = [];
    if (d.tier != null) f.push(`<span class="dx-chip t${d.tier}">${TIERS[d.tier]}</span>`);
    f.push(`<span>Z ${r.Z} · N ${r.A ? r.A - r.Z : "–"}</span>`);
    if (d.macs30) f.push(`<span>MACS 30 keV ≈ <b>${num(d.macs30)} mb</b>${d.macsU ? ` (×/÷ ${num(d.macsU[6], 2)}, 68 %)` : ""}</span>`);
    if (d.meas) f.push(`<span>${d.meas.ds.length} ${T("dx_capsets", "capture datasets")}</span>`);
    if (d.tier != null && !d.valid) f.push(`<span class="dx-warn">${T("dx_outside", "outside the validated range (Z 26–83)")}</span>`);
    if (d.flag) f.push(`<span class="dx-warn">${T("dx_flag", "resolved resonances reach the MACS window: prefer a measured MACS")}</span>`);
    $("#dx-facts").innerHTML = f.join("");
    const st = [[r.Z, T("dx_s_p", "protons")], [r.A ? r.A - r.Z : "–", T("dx_s_n", "neutrons")]];
    if (d.macs30) st.push([num(d.macs30) + " mb", T("dx_s_macs", "capture in a star at 30 keV")]);
    if (d.meas) st.push([d.meas.cap.length + d.meas.mxw.length, T("dx_s_pts", "measured capture points")]);
    const nThr = d.thr ? Object.values(d.thr).reduce((s, v) => s + v.length, 0) : 0; if (nThr) st.push([nThr, T("dx_s_thr", "(n,2n), (n,p), (n,α) points")]);
    $("#dx-stats").innerHTML = st.map(([v, l]) => `<div class="dx-stat"><b>${v}</b><span>${l}</span></div>`).join("");
    const nm = r.A ? `${IDX.sym[r.Z]}-${r.A}` : "";
    $("#dx-cmd").textContent = nm && d.cap ? `uv run python -m incognita.library show ${nm}\n\n# or from Python\nfrom incognita.library import capture_curve\ndf = capture_curve("${nm}")   # energy_ev, sigma_b, lo68_b, hi68_b, lo95_b, hi95_b, tier`
      : `# ${T("dx_nocurve", "no library curve for this entry; the measurements come from")} data/curation/inputs/exfor_cells.parquet`;
    sweep();
    if (center && !stay) $("#dx-nuc").scrollIntoView({ behavior: "smooth", block: "start" });
  }

  function libOf(lz, r) { const n = lz && lz.nuc[r.A ? String(r.A) : "nat"]; return { libs: (lz && lz.libs) || {}, n: n || {} }; }
  const libHas = (k) => !!(libOn && cur.lib && Object.values(cur.lib.n).some((v) => v[k]));
  function buildTabs() {
    const tabs = ["cap"], d = cur.d;
    for (const k of ["n2n", "np", "na"]) if ((d.ch && d.ch[k]) || (d.thr && d.thr[k]) || libHas(k)) tabs.push(k);
    if (d.macs || (d.meas && d.meas.mxw.some((p) => p[0] >= 1000)) || libHas("macs")) tabs.push("macs");
    if (!tabs.includes(tab)) tab = "cap";
    $("#dx-tabs").innerHTML = tabs.map((k) => `<button type="button" role="tab" data-tab="${k}" aria-selected="${k === tab}">${CH[k]}</button>`).join("");
    $("#dx-tabs").querySelectorAll("button").forEach((b) => b.addEventListener("click", () => { tab = b.dataset.tab; hl = null; $("#dx-tabs").querySelectorAll("button").forEach((x) => x.setAttribute("aria-selected", String(x === b))); sweep(); }));
  }
  // evaluated-library curves for the current tab: dashed, thin, one muted colour per library
  function libCurves(out) {
    if (!libOn || !cur.lib) return;
    const xs = tab === "macs" ? IDX.kT_keV.map((k) => k * 1e3) : IDX.grid_ev;
    LIBS.forEach((key, i) => { const v = cur.lib.n[key] && cur.lib.n[key][tab], L = cur.lib.libs[key];
      if (!v || !L) return; const floor = tab === "cap" || tab === "macs" ? 0 : Math.max(...v.filter((y) => y > 0)) * 1e-6; // drop sub-threshold tails so they do not stretch the axis
      out.curves.push({ name: `${L.label} (${T("dx_eval", "evaluation")})`, short: L.label, col: C["l" + (i + 1)], pts: xs.map((x, j) => [x, v[j] > floor ? v[j] : null]), dash: true }); });
  }
  function libNote() {
    const box = $("#dx-libnote"); box.hidden = !libOn; if (!libOn || !cur) return;
    const L = cur.lib || { libs: {}, n: {} }, have = LIBS.filter((k) => L.n[k] && L.libs[k]), miss = LIBS.filter((k) => !L.n[k]);
    const LAB = { "endfb8.1": "ENDF/B-VIII.1", "jeff4.0": "JEFF-4.0", "tendl2025": "TENDL-2025" };
    const lic = (s) => (s === "US public domain" ? T("dx_lib_pd", "US public domain") : s);
    box.innerHTML = `<p>${T("dx_lib_note", "Dashed lines are evaluated nuclear-data libraries, shown only for comparison: INCOGNITA does not use them and they are not in the downloads. Each is reconstructed at 0 K from the library’s ENDF-6 file (NJOY) and averaged over the same energy bins as the curve (log-energy bin averages, so resonances are smoothed out); the MACS uses the full pointwise curve.")}</p>`
      + (have.length ? `<ul>${have.map((k) => `<li><i style="color:${C["l" + (LIBS.indexOf(k) + 1)]}"></i><span><b>${esc(L.libs[k].label)}</b> · ${esc(lic(L.libs[k].lic))} · ${esc(L.libs[k].cite)}</span></li>`).join("")}</ul>` : "")
      + `<p>${miss.length ? `${T("dx_lib_none", "No file for this nuclide in")} ${miss.map((k) => LAB[k]).join(", ")}. ` : ""}${(() => { const no = have.filter((k) => !L.n[k][tab]); return no.length ? `${T("dx_lib_notab", "No separate value for this reaction in")} ${no.map((k) => LAB[k]).join(", ")}. ` : ""; })()}${T("dx_lib_held", "JENDL-5 will be added once its terms for redistributing derived tables are confirmed.")}</p>`;
  }

  // series for the current tab: { unit, curves:[{name,col,pts:[[x,y]],band68:[[x,lo,hi]],band95}], points:[{x,y,lo,hi,xlo,xhi,ds,dec,kind}], ds:[...] }
  function series() {
    const d = cur.d, grid = IDX.grid_ev, out = { curves: [], points: [], ds: [], xlab: T("dx_xE", "neutron energy"), unit: "b", note: null };
    const band = (ys, us) => grid.map((x, i) => (ys[i] > 0 && us && us[i] != null ? [x, ys[i] / 10 ** us[i], ys[i] * 10 ** us[i]] : null)).filter(Boolean);
    if (tab === "cap") {
      if (d.cap) out.curves.push({ name: T("dx_pred", "prediction (library v0.1)"), col: C.curve, pts: grid.map((x, i) => [x, d.cap[i]]), b68: band(d.cap, d.u68), b95: band(d.cap, d.u95) });
      if (d.meas) { out.ds = d.meas.ds;
        for (const p of d.meas.cap) out.points.push({ x: Math.sqrt(p[0] * p[1]), xlo: p[0], xhi: p[1], y: p[2], e: p[3], ds: p[4], dec: p[5], st: p[6], kind: "sig" });
        for (const p of d.meas.mxw) if (p[0] < 1000) out.points.push({ x: p[0], xlo: p[0], xhi: p[1], y: p[2], e: p[3], ds: p[4], dec: p[5], st: p[6], kind: "mxw" }); }
      libCurves(out);
      if (d.res) out.note = { upto: d.res, text: T("dx_res", "resolved resonances: the curve is an average here") };
    } else if (tab === "macs") {
      out.xlab = "kT"; out.unit = "mb";
      if (d.macs) out.curves.push({ name: T("dx_pred", "prediction (library v0.1)"), col: C.curve, pts: IDX.kT_keV.map((k, i) => [k * 1e3, d.macs[i]]), b68: IDX.kT_keV.map((k, i) => (d.macsU && d.macsU[i] ? [k * 1e3, d.macs[i] / d.macsU[i], d.macs[i] * d.macsU[i]] : null)).filter(Boolean) });
      libCurves(out);
      if (d.meas) { out.ds = d.meas.ds; for (const p of d.meas.mxw) if (p[0] >= 1000) out.points.push({ x: p[0], xlo: p[0], xhi: p[1], y: p[2] * 1000, e: p[3], ds: p[4], dec: p[5], st: p[6], kind: "mxw" }); }
    } else {
      out.unit = "mb";
      if (d.ch && d.ch[tab]) out.curves.push({ name: T("dx_recipe", "engine, no-data recipe"), col: C.curve, pts: grid.map((x, i) => [x, d.ch[tab][i]]) });
      libCurves(out);
      if (tab === "np" && d.npL) out.curves.push({ name: T("dx_learned", "learned correction, 68 % band"), col: C.alt, pts: d.npL.map((p) => [p[0], p[1]]), b68: d.npL.filter((p) => p[2] != null).map((p) => [p[0], p[2], p[3]]) });
      const t = (d.thr && d.thr[tab]) || [], keys = [...new Set(t.map((p) => p[2]))];
      out.ds = keys.map((k) => [k, "", (t.find((p) => p[2] === k) || [])[3], ""]);
      for (const p of t) out.points.push({ x: p[0], y: p[1], e: null, ds: keys.indexOf(p[2]), dec: "k", kind: "thr" });
    }
    return out;
  }

  const pcv = $("#dx-plot"), ptip = $("#dx-ptip");
  // the plot is drawn once per nuclide, reaction or size into three layers (base: grid, axes, bands; measured points; curves);
  // the opening sweep and the dataset highlight only recompose them, so an animation frame is a few image copies
  const LAY = { a: document.createElement("canvas"), p: document.createElement("canvas"), c: document.createElement("canvas") };
  const layer = (c) => fresh(c, pcv.width, pcv.height, P.dpr);
  // a sweep from left to right draws the curve and reveals the measured points when a nuclide or reaction opens
  let anim = 1, animT0 = 0, animRaf = 0;
  function sweep() {
    buildNuc(); cancelAnimationFrame(animRaf);
    if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) { anim = 1; compose(); return; }
    animT0 = performance.now(); anim = 0; compose();
    const step = (now) => { const u = clamp((now - animT0) / 1100, 0, 1); anim = 1 - Math.pow(1 - u, 3); compose(); if (u < 1) animRaf = requestAnimationFrame(step); }; animRaf = requestAnimationFrame(step);
  }
  function renderNuc() { buildNuc(); compose(); }
  function buildNuc() {
    if (!cur) return;
    const S = series(), shown = S.points.filter((p) => showExcl || p.dec !== "x");
    const W = pcv.parentElement.clientWidth, H = Math.round(clamp(W * 0.55, 300, 460));
    P = { ...setupCanvas(pcv, H), S, shown };
    const ctx = layer(LAY.a), m = { l: 62, r: 16, t: 16, b: 44 };
    // ranges (log-log)
    let x0 = Infinity, x1 = -Infinity, y0 = Infinity, y1 = -Infinity;
    const ax = (x) => { if (x < x0) x0 = x; if (x > x1) x1 = x; }, ay = (y) => { if (y < y0) y0 = y; if (y > y1) y1 = y; };
    S.curves.forEach((c) => { c.pts.forEach(([x, y]) => { if (y > 0) { ax(x); ay(y); } }); (c.b68 || []).forEach(([x, lo, hi]) => { if (lo > 0) ay(lo); ay(hi); }); });
    shown.forEach((p) => { if (p.y > 0) { ax(p.xlo || p.x); ax(p.xhi || p.x); ay(p.y); } });
    for (const c of [LAY.p, LAY.c]) layer(c);
    if (!(x1 > 0)) { ctx.fillStyle = C.surface; ctx.fillRect(0, 0, W, H); ctx.fillStyle = C.soft; ctx.font = `500 14px ${SANS}`; ctx.textAlign = "center"; ctx.fillText(T("dx_empty", "Nothing to show for this reaction."), W / 2, H / 2); finishNuc(S); return; }
    x0 = log10(x0); x1 = log10(x1); y0 = log10(y0); y1 = log10(y1);
    if (x1 - x0 < 1) { x0 -= 0.5; x1 += 0.5; } if (y1 - y0 < 1) { y0 -= 0.5; y1 += 0.5; }
    x0 -= 0.05 * (x1 - x0); x1 += 0.05 * (x1 - x0); y0 -= 0.08 * (y1 - y0); y1 += 0.08 * (y1 - y0);
    const X = (x) => m.l + (log10(x) - x0) / (x1 - x0) * (W - m.l - m.r), Y = (y) => H - m.b - (log10(y) - y0) / (y1 - y0) * (H - m.t - m.b);
    Object.assign(P, { X, Y, m, x0, x1, y0, y1, W, H });
    ctx.fillStyle = C.surface; ctx.fillRect(0, 0, W, H);
    // grid and axes (decades)
    ctx.font = `500 12px ${SANS}`; ctx.fillStyle = C.soft; ctx.strokeStyle = C.grid; ctx.lineWidth = 1;
    ctx.textAlign = "center"; ctx.textBaseline = "top";
    { let lastX = -1e9; const step = W < 600 ? 62 : 48; for (let k = Math.ceil(x0); k <= Math.floor(x1); k++) { const x = X(10 ** k); ctx.beginPath(); ctx.moveTo(x, m.t); ctx.lineTo(x, H - m.b); ctx.stroke(); if (x - lastX >= step) { ctx.fillText(decE(k), x, H - m.b + 6); lastX = x; } } }
    ctx.textAlign = "right"; ctx.textBaseline = "middle";
    for (let k = Math.ceil(y0); k <= Math.floor(y1); k++) { const y = Y(10 ** k); ctx.beginPath(); ctx.moveTo(m.l, y); ctx.lineTo(W - m.r, y); ctx.stroke(); ctx.fillText(decY(k, S.unit), m.l - 8, y); }
    ctx.textAlign = "left"; ctx.textBaseline = "alphabetic"; ctx.fillText(S.xlab + " →", m.l, H - 6);
    let note = null; // drawn last, over the points, with a dark halo so it stays readable
    ctx.save(); ctx.beginPath(); ctx.rect(m.l, m.t, W - m.l - m.r, H - m.t - m.b); ctx.clip();
    if (S.note && S.note.upto > 10 ** x0) { const xe = Math.min(X(S.note.upto), W - m.r); ctx.fillStyle = rgba(C.soft, 0.07); ctx.fillRect(m.l, m.t, xe - m.l, H - m.t - m.b);
      ctx.font = `500 12px ${SANS}`;
      if (xe - m.l > 120) { // wrapped to the plot's width, so a narrow (phone) plot shows the whole note instead of cutting it off
        const maxW = W - m.r - m.l - 16; let ln = ""; note = [];
        for (const w of S.note.text.split(" ")) { const t = ln ? ln + " " + w : w; if (ln && ctx.measureText(t).width > maxW) { note.push(ln); ln = w; } else ln = t; }
        note.push(ln); } }
    // bands, then measured points, then the curves on top
    for (const c of S.curves) {
      for (const [b, a] of [[c.b95, 0.1], [c.b68, 0.2]]) if (b && b.length > 1) { ctx.fillStyle = rgba(c.col, a); ctx.beginPath(); b.forEach(([x, , hi], i) => (i ? ctx.lineTo(X(x), Y(hi)) : ctx.moveTo(X(x), Y(hi)))); for (let i = b.length - 1; i >= 0; i--) ctx.lineTo(X(b[i][0]), Y(Math.max(b[i][1], 10 ** (y0 - 1)))); ctx.closePath(); ctx.fill(); }
    }
    ctx.restore();
    drawPoints(false);
    const cc = LAY.c.getContext("2d"); cc.save(); cc.beginPath(); cc.rect(m.l, m.t, W - m.l - m.r, H - m.t - m.b); cc.clip();
    for (const c of [...S.curves].sort((a, b) => !!a.dash - !!b.dash)) for (const [w, col] of c.dash ? [[1.7, c.col]] : [[5, C.surface], [2.2, c.col]]) { // dashed library lines go on top, thin and without a halo, so they never hide the prediction
      cc.strokeStyle = col; cc.lineWidth = w; cc.shadowColor = w > 3 || c.dash ? "transparent" : col; cc.shadowBlur = w > 3 || c.dash ? 0 : 12; cc.lineJoin = "round"; cc.setLineDash(c.dash ? [7, 5] : []); cc.beginPath(); let on = false;
      for (const [x, y] of c.pts) { if (!(y > 0)) { on = false; continue; } on ? cc.lineTo(X(x), Y(y)) : cc.moveTo(X(x), Y(y)); on = true; }
      cc.stroke();
    }
    if (note) { cc.shadowBlur = 0; cc.setLineDash([]); cc.font = `500 12px ${SANS}`; cc.textAlign = "left"; cc.textBaseline = "alphabetic"; cc.lineJoin = "round"; cc.lineWidth = 3; cc.strokeStyle = document.documentElement.dataset.theme === "light" ? C.surface : "rgba(8,13,28,.85)"; cc.fillStyle = C.soft;
      note.forEach((l, i) => { cc.strokeText(l, m.l + 8, m.t + 14 + i * 15); cc.fillText(l, m.l + 8, m.t + 14 + i * 15); }); }
    cc.restore();
    finishNuc(S);
  }
  // measured points: error bars, energy-bin bars, dots (hollow = excluded, faint = down-weighted); 2px surface ring
  function drawPoints(clear) {
    const ctx = clear === false ? LAY.p.getContext("2d") : layer(LAY.p), { X, Y, m, W, H } = P;
    ctx.save(); ctx.beginPath(); ctx.rect(m.l, m.t, W - m.l - m.r, H - m.t - m.b); ctx.clip();
    for (const p of P.shown) {
      if (!(p.y > 0)) continue;
      const dim = hl != null && p.ds !== hl, x = X(p.x), y = Y(p.y);
      ctx.globalAlpha = dim ? 0.15 : p.dec === "d" ? 0.55 : 1; ctx.strokeStyle = C.meas; ctx.lineWidth = 1.2;
      if (p.e > 0) { ctx.beginPath(); ctx.moveTo(x, Y(p.y * (1 + p.e))); ctx.lineTo(x, Y(Math.max(p.y * (1 - p.e), p.y * 0.05))); ctx.stroke(); }
      if (p.xhi > p.xlo * 1.02) { ctx.beginPath(); ctx.moveTo(X(p.xlo), y); ctx.lineTo(X(p.xhi), y); ctx.stroke(); }
      ctx.beginPath(); ctx.arc(x, y, p.kind === "mxw" ? 5 : 4, 0, Math.PI * 2);
      if (p.dec === "x") { ctx.strokeStyle = C.meas; ctx.lineWidth = 1.5; ctx.stroke(); } else { ctx.fillStyle = C.meas; ctx.fill(); ctx.strokeStyle = C.surface; ctx.lineWidth = 1.5; ctx.stroke(); }
    }
    ctx.restore();
  }
  const setHl = (v) => { if (hl === v) return; hl = v; if (P && P.X) { drawPoints(); compose(); } };
  // one frame: the base, the points fading in over the 30 px behind the sweep, the curves up to it
  function compose() {
    if (!P) return;
    const g = P.ctx, d = P.dpr, pw = pcv.width, ph = pcv.height;
    g.setTransform(1, 0, 0, 1, 0, 0); g.clearRect(0, 0, pw, ph); g.drawImage(LAY.a, 0, 0);
    if (P.X) {
      if (anim >= 1) { g.drawImage(LAY.p, 0, 0); g.drawImage(LAY.c, 0, 0); }
      else {
        const rv = (P.m.l + anim * (P.W - P.m.l - P.m.r)) * d, f = 30 * d;
        const part = (c, a, b, al) => { a = clamp(Math.round(a), 0, pw); b = clamp(Math.round(b), 0, pw); if (b > a) { g.globalAlpha = al; g.drawImage(c, a, 0, b - a, ph, a, 0, b - a, ph); } };
        part(LAY.p, 0, rv - f, 1); for (let i = 0; i < 3; i++) part(LAY.p, rv - f + i * f / 3, rv - f + (i + 1) * f / 3, (5 - 2 * i) / 6);
        g.globalAlpha = 1; part(LAY.c, 0, rv, 1);
      }
    }
    g.globalAlpha = 1; g.setTransform(d, 0, 0, d, 0, 0);
  }
  function finishNuc(S) {
    const nPts = S.points.length, nEx = S.points.filter((p) => p.dec === "x").length;
    $("#dx-excl").parentElement.hidden = nEx === 0;
    libNote();
    const leg = S.curves.map((c) => c.dash ? `<span class="dx-key"><i class="dash" style="color:${c.col}"></i>${esc(c.name)}</span>` : `<span class="dx-key"><i class="ln" style="background:${c.col}"></i>${c.name}${c.b95 ? ` · ${T("dx_bands", "bands: 68 % and 95 %")}` : c.b68 && !c.name.includes("68") ? ` · ${T("dx_band68", "band: 68 %")}` : ""}</span>`);
    if (nPts) leg.push(`<span class="dx-key"><i class="dot" style="background:${C.meas}"></i>${T("dx_meas_pts", "measured")} (${nPts}${nEx ? `, ${nEx} ${T("dx_excl", "excluded")}` : ""})</span>`);
    $("#dx-plegend").innerHTML = leg.join("");
    pcv.setAttribute("aria-label", `${nameOf(cur.r.Z, cur.r.A)}, ${CH[tab]}: ${S.curves.length ? S.curves.map((c) => c.name).join(", ") : ""}${nPts ? `; ${nPts} ${T("dx_meas_pts", "measured")}` : ""}. ${T("dx_table_hint", "Use “Show as a table” for the values.")}`);
    // datasets
    const cnt = new Map(); S.points.forEach((p) => cnt.set(p.ds, (cnt.get(p.ds) || 0) + 1));
    const list = S.ds.map((d, i) => ({ d, i, n: cnt.get(i) || 0 })).filter((x) => x.n).sort((a, b) => (a.d[2] || 0) - (b.d[2] || 0));
    $("#dx-ds").innerHTML = list.length ? `<h3>${T("dx_ds_h", "Measurements")} <span class="dx-faint">(${list.length})</span></h3><ul>${list.map(({ d, i, n }) => {
      const ex = exforOf(d[0]), sub = ex ? ex.id : String(d[0]).split("/").filter(Boolean).pop() || d[0];
      return `<li data-ds="${i}"><span class="dx-who">${esc(d[1] || "EXFOR " + sub)}${d[2] ? ` <span class="dx-faint">${d[2]}</span>` : ""}</span><span class="dx-faint">${esc(d[3] || "")}</span><span class="dx-faint">${n} ${T("dx_pts", "pts")}</span>${ex ? `<a href="${ex.url}" target="_blank" rel="noopener">EXFOR ${sub}</a>` : `<span class="dx-faint">${esc(d[0])}</span>`}</li>`; }).join("")}</ul>` : "";
    $("#dx-ds").querySelectorAll("li").forEach((li) => { li.addEventListener("mouseenter", () => setHl(+li.dataset.ds)); li.addEventListener("mouseleave", () => setHl(null)); li.addEventListener("focusin", () => setHl(+li.dataset.ds)); });
    if (tableOpen) table(S);
  }
  function table(S) {
    const rowsC = S.curves.flatMap((c) => c.pts.filter(([, y]) => y > 0).map(([x, y], i) => { const b = c.b68 && c.b68.find((q) => q[0] === x); return `<tr><td>${esc(c.name)}</td><td>${fmtE(x)}</td><td>${num(y)} ${S.unit}</td><td>${b ? `${num(b[1])}–${num(b[2])}` : ""}</td><td></td></tr>`; }));
    const rowsP = S.points.filter((p) => showExcl || p.dec !== "x").map((p) => { const d = S.ds[p.ds] || []; return `<tr><td>${esc(d[1] || d[0] || "")} ${d[2] || ""}</td><td>${p.xhi > p.xlo * 1.02 ? `${fmtE(p.xlo)}–${fmtE(p.xhi)}` : fmtE(p.x)}</td><td>${num(p.y)} ${S.unit}</td><td>${p.e ? "± " + num(p.e * 100, 2) + " %" : ""}</td><td>${DEC[p.dec] || ""}</td></tr>`; });
    $("#dx-table").innerHTML = `<table><thead><tr><th>${T("dx_th_src", "Source")}</th><th>${S.xlab}</th><th>${T("dx_th_val", "Value")}</th><th>${T("dx_th_unc", "Range / uncertainty")}</th><th>${T("dx_th_cur", "Curation")}</th></tr></thead><tbody>${rowsC.join("")}${rowsP.join("")}</tbody></table>`;
  }
  $("#dx-tbtn").addEventListener("click", (e) => { tableOpen = !tableOpen; e.currentTarget.setAttribute("aria-expanded", String(tableOpen)); $("#dx-table").hidden = !tableOpen; if (tableOpen) table(series()); });
  $("#dx-lib").addEventListener("change", async (e) => { libOn = e.target.checked; if (!cur) return; const c0 = cur;
    if (libOn) { $("#dx-libnote").hidden = false; $("#dx-libnote").textContent = T("dx_lib_loading", "Loading the libraries…"); const lz = await loadLib(c0.r.Z); if (cur !== c0) return; cur.lib = libOf(lz, c0.r); }
    buildTabs(); renderNuc(); });
  $("#dx-excl").addEventListener("change", (e) => { showExcl = e.target.checked; renderNuc(); });
  $("#dx-copy").addEventListener("click", (e) => { try { navigator.clipboard.writeText($("#dx-cmd").textContent); e.currentTarget.textContent = T("dx_copied", "Copied"); } catch (err) {} });
  // hover (mouse) or tap (touch) shows the tooltip; clicking a measured point, or tapping it a second time, opens its EXFOR subentry
  let tipPin = null, lastPT = "mouse";
  function tipAt(x, y) {
    if (!P || !P.X) return null;
    let best = null, bd = (lastPT === "mouse" ? 14 : 22) ** 2;
    for (const p of P.shown) { if (!(p.y > 0)) continue; const d = (P.X(p.x) - x) ** 2 + (P.Y(p.y) - y) ** 2; if (d < bd) { bd = d; best = p; } }
    if (best) { const d = P.S.ds[best.ds] || [], ex = exforOf(d[0]);
      let html = `<b>${esc(d[1] || "EXFOR " + (ex ? ex.id : String(d[0]).split("/").filter(Boolean).pop() || ""))}</b> ${d[2] || ""}<br>${best.xhi > best.xlo * 1.02 ? `${fmtE(best.xlo)}–${fmtE(best.xhi)}` : fmtE(best.x)}: <b>${num(best.y)} ${P.S.unit}</b>${best.e ? ` ± ${num(best.e * 100, 2)} %` : ""}${best.kind === "mxw" ? ` · ${T("dx_mxw", "Maxwellian average")}` : ""}${best.st ? ` · ${T("dx_state", "state")} ${esc(best.st)}` : ""}<br><span class="dx-faint">${T("dx_cur", "curation")}: ${DEC[best.dec]}</span>`;
      if (ex) html += lastPT === "mouse" ? `<br><span class="dx-exhint">${T("dx_exfor_click", "click the point to open")} EXFOR ${ex.id} ↗</span>`
        : `<br><a class="dx-exhint" href="${ex.url}" target="_blank" rel="noopener">${T("dx_exfor_tap", "tap again, or here, to open")} EXFOR ${ex.id} ↗</a>`;
      return { html, url: ex && ex.url, p: best }; }
    const c = P.S.curves[0];
    if (c && x > P.m.l && x < P.W - P.m.r) {
      const xv = 10 ** (P.x0 + (x - P.m.l) / (P.W - P.m.l - P.m.r) * (P.x1 - P.x0)); let j = -1, jd = Infinity; c.pts.forEach(([px], i) => { const dd = Math.abs(log10(px) - log10(xv)); if (dd < jd) { jd = dd; j = i; } });
      if (j >= 0 && jd < 0.2) { const xe = c.pts[j][0], lines = [], anyLib = P.S.curves.some((cc) => cc.dash);
        for (const cc of P.S.curves) { const q = cc.pts.find((p) => p[0] === xe); if (!q || !(q[1] > 0)) continue; const b = cc.b68 && cc.b68.find((r) => r[0] === xe);
          lines.push(cc.dash ? `<span class="dx-faint">${esc(cc.short)}: ${num(q[1])} ${P.S.unit}</span>` : `<b>${num(q[1])} ${P.S.unit}</b>${b ? ` <span class="dx-faint">(68 %: ${num(b[1])}–${num(b[2])})</span>` : ""}${anyLib ? ` <span class="dx-faint">· ${esc(cc.name)}</span>` : ""}`); }
        if (lines.length) return { html: `${fmtE(xe)}${anyLib && tab !== "macs" ? ` <span class="dx-faint">· ${T("dx_lib_bin", "libraries: bin averages")}</span>` : ""}<br>${lines.join("<br>")}`, url: null, p: null }; } }
    return null;
  }
  function showTip(h, x, y) {
    pcv.style.cursor = h && h.url ? "pointer" : "";
    ptip.style.pointerEvents = h && h.url && lastPT !== "mouse" ? "auto" : "";
    if (!h) { ptip.hidden = true; return; }
    ptip.innerHTML = h.html; ptip.hidden = false; place(ptip, x, y, pcv);
  }
  const openEx = (url) => { try { window.open(url, "_blank", "noopener"); } catch (err) {} };
  pcv.addEventListener("pointerdown", (e) => { lastPT = e.pointerType || "mouse"; });
  pcv.addEventListener("pointermove", (e) => { if ((e.pointerType || "mouse") !== "mouse") return; lastPT = "mouse"; tipPin = null; showTip(tipAt(e.offsetX, e.offsetY), e.offsetX, e.offsetY); });
  pcv.addEventListener("click", (e) => {
    const h = tipAt(e.offsetX, e.offsetY);
    if (lastPT === "mouse") { if (h && h.url) openEx(h.url); return; }
    if (h && h.url && h.p === tipPin) { openEx(h.url); return; } // second tap on the same point
    tipPin = h ? h.p : null; showTip(h, e.offsetX, e.offsetY);
  });
  pcv.addEventListener("pointerleave", (e) => { if ((e.pointerType || "mouse") === "mouse") { tipPin = null; showTip(null); } });
  document.addEventListener("pointerdown", (e) => { if (!ptip.hidden && e.target !== pcv && !ptip.contains(e.target)) { tipPin = null; showTip(null); } });

  // ---------- downloads: everything loaded for one nuclide, as CSV or JSON, built here from data/n/<Z>/<A>.json ----------
  const DECW = { k: "kept", d: "down-weighted", x: "excluded", f: "unit fixed" };
  /** { name, csv, json } for nuclide (Z, A) with record d; English labels so files read the same in either language. */
  function exportNuc(Z, A, d) {
    const sym = IDX.sym[Z], id = A ? `${sym}-${A}` : `${sym}-nat`, grid = IDX.grid_ev, kT = IDX.kT_keV;
    const page = `${location.origin}${location.pathname.replace(/data(\.html)?$/, "")}data.html#${id}`;
    const meta = {
      nuclide: id, Z, A: A || null,
      source: "INCOGNITA library v0.1 (preview): library/v0.1 in https://github.com/seth-michael-weaver/incognita, as shown on the Every nuclide page",
      page, generated: new Date().toISOString().slice(0, 10),
      engine: "The INCOGNITA engine is a port of TALYS-2 (A. J. Koning, S. Hilaire, S. Goriely, Eur. Phys. J. A 59 (2023) 131) and uses the TALYS nuclear-structure database.",
      license: "Predictions and data: CC-BY-4.0. Cite the project (CITATION.cff in the repository), TALYS (Eur. Phys. J. A 59 (2023) 131) and EXFOR (N. Otuka et al., Nucl. Data Sheets 120 (2014) 272).",
      measurements: "Measured points are from EXFOR (IAEA Nuclear Data Section) as curated in data/curation; each row carries its EXFOR dataset id (entry/subentry/pointer). (n,2n), (n,p) and (n,alpha) points are the benchmark rows in incognita/bench, with their EXFOR subentry.",
      units: "energy in eV (Maxwellian rows: kT in eV); capture cross sections in barns (b); (n,2n), (n,p), (n,alpha) and MACS in millibarns (mb)",
    };
    const J = { ...meta };
    if (d.tier != null) Object.assign(J, { tier: IDX.tiers[d.tier], in_validated_range: !!d.valid, value_source: d.src || null, uncertainty_kind: d.unc || null, resolved_resonances_up_to_ev: d.res ?? null, macs30_mb: d.macs30 ?? null, macs30_flag: d.flag || null });
    if (d.cap) J.capture = { unit: "b", energy_ev: grid, sigma_b: d.cap, unc68_log10: d.u68 || null, unc95_log10: d.u95 || null, note: "68 % and 95 % bands: sigma divided and multiplied by 10^unc" };
    if (d.ch) J.channels_recipe = { unit: "mb", energy_ev: grid, ...Object.fromEntries(Object.entries(d.ch).map(([k, v]) => [k === "na" ? "n_alpha" : k, v])), note: "engine, no-data recipe" };
    if (d.npL) J.np_learned = { unit: "mb", columns: ["energy_ev", "sigma_mb", "lo68_mb", "hi68_mb"], rows: d.npL, note: "(n,p) with a learned correction, 68 % interval" };
    if (d.macs) J.macs = { unit: "mb", kT_keV: kT, macs_mb: d.macs, unc68_factor: d.macsU || null, note: "68 % band: MACS divided and multiplied by the factor" };
    const ds = d.meas ? d.meas.ds.map((x, i) => { const ex = exforOf(x[0]); return { index: i, exfor_id: x[0], exfor_subentry: ex ? ex.id : null, url: ex ? ex.url : null, author: x[1] || null, year: x[2] ?? null, facility: x[3] || null }; }) : [];
    const mrow = (p) => [p[0], p[1], p[2], p[3], p[4], DECW[p[5]] || p[5], p[6] || ""];
    if (d.meas || d.thr) J.measured = {
      datasets: ds,
      capture: d.meas ? { unit: "b", columns: ["e_lo_ev", "e_hi_ev", "sigma_b", "rel_unc", "dataset", "curation", "state"], rows: d.meas.cap.map(mrow) } : null,
      maxwellian: d.meas ? { unit: "b", columns: ["kT_lo_ev", "kT_hi_ev", "value_b", "rel_unc", "dataset", "curation", "state"], rows: d.meas.mxw.map(mrow) } : null,
      threshold: d.thr ? Object.fromEntries(Object.entries(d.thr).map(([k, v]) => [k === "na" ? "n_alpha" : k, { unit: "mb", columns: ["energy_ev", "sigma_mb", "exfor_subentry", "year"], rows: v }])) : null,
    };
    // CSV: one long table, '#' header lines first
    const q = (v) => { if (v == null) return ""; const s = String(v); return /[",\n]/.test(s) ? `"${s.replace(/"/g, '""')}"` : s; };
    const rows = [["kind", "reaction", "energy_ev", "energy_hi_ev", "value", "unit", "lo68", "hi68", "lo95", "hi95", "rel_unc", "exfor_id", "author", "year", "curation", "state"]];
    const r4 = (v) => (v == null ? null : +v.toPrecision(4));
    if (d.cap) grid.forEach((x, i) => { const y = d.cap[i], u = d.u68 && d.u68[i], w = d.u95 && d.u95[i];
      rows.push(["prediction", "capture (n,g)", x, "", y, "b", u != null ? r4(y / 10 ** u) : "", u != null ? r4(y * 10 ** u) : "", w != null ? r4(y / 10 ** w) : "", w != null ? r4(y * 10 ** w) : ""]); });
    if (d.ch) for (const [k, v] of Object.entries(d.ch)) grid.forEach((x, i) => rows.push(["prediction (no-data recipe)", k === "na" ? "(n,alpha)" : `(${k[0]},${k.slice(1)})`, x, "", v[i], "mb"]));
    if (d.npL) d.npL.forEach((p) => rows.push(["prediction (learned correction)", "(n,p)", p[0], "", p[1], "mb", p[2] ?? "", p[3] ?? ""]));
    if (d.macs) kT.forEach((k, i) => { const f = d.macsU && d.macsU[i]; rows.push(["prediction", "MACS (kT)", k * 1e3, "", d.macs[i], "mb", f ? r4(d.macs[i] / f) : "", f ? r4(d.macs[i] * f) : ""]); });
    const mline = (kind, reac, p) => { const s = ds[p[4]] || {}; rows.push([kind, reac, p[0], p[1], p[2], "b", "", "", "", "", p[3] ?? "", s.exfor_id || "", s.author || "", s.year ?? "", DECW[p[5]] || p[5], p[6] || ""]); };
    if (d.meas) { d.meas.cap.forEach((p) => mline("measured (EXFOR)", "capture (n,g)", p)); d.meas.mxw.forEach((p) => mline("measured (EXFOR)", "Maxwellian average (kT)", p)); }
    if (d.thr) for (const [k, v] of Object.entries(d.thr)) v.forEach((p) => rows.push(["measured (EXFOR, benchmark)", k === "na" ? "(n,alpha)" : `(${k[0]},${k.slice(1)})`, p[0], "", p[1], "mb", "", "", "", "", "", p[2] || "", "", p[3] ?? "", "", ""]));
    const head = [`INCOGNITA · ${id} (Z=${Z}${A ? `, A=${A}` : ""})`, `Source: ${meta.source}`, `Page: ${page} (generated ${meta.generated})`, `Engine: ${meta.engine}`, `License: ${meta.license}`,
      `Measurements: ${meta.measurements}`, `Units: ${meta.units}. Bands: lo/hi columns are the 68 % and 95 % intervals where the library gives them.`]
      .concat(d.tier != null ? [`Tier: ${IDX.tiers[d.tier]}${d.valid ? "" : " (outside the validated range Z 26-83)"}${d.res ? `; resolved resonances up to ${d.res} eV (the curve is an average there)` : ""}`] : []);
    const csv = head.map((l) => "# " + l).join("\n") + "\n" + rows.map((r) => r.map(q).join(",")).join("\n") + "\n";
    return { name: `incognita_${id}_v0.1`, csv, json: JSON.stringify(J, null, 1) + "\n" };
  }
  WT.dxExport = (Z, A) => loadNuc(Z, A).then((d) => exportNuc(Z, A, d));
  function save(text, name, type) {
    const url = URL.createObjectURL(new Blob([text], { type })), a = document.createElement("a");
    a.href = url; a.download = name; document.body.appendChild(a); a.click(); a.remove(); setTimeout(() => URL.revokeObjectURL(url), 4000);
  }
  [["#dx-dl-csv", "csv", "text/csv;charset=utf-8"], ["#dx-dl-json", "json", "application/json"]].forEach(([s, ext, type]) => { const b = $(s); if (b) b.addEventListener("click", () => {
    const r = sel; if (!r) return; // the selected nuclide, fetched first if it has not arrived yet
    WT.dxExport(r.Z, r.A).then((e) => save(e[ext], `${e.name}.${ext}`, type), (err) => { if (sel === r) busy(r, err); }); }); });

  // ---------- start ----------
  // the chart fills the rest of the first screen (title, controls and legend stay visible), so it is never cut off at the fold
  function layout() { const top = cv.parentElement.getBoundingClientRect().top + window.scrollY; G = setupCanvas(cv, Math.round(clamp(window.innerHeight - top - 64, 300, 1100))); }
  fetch("data/index.json").then((r) => r.json()).then((idx) => {
    IDX = idx; readColors();
    const k = Object.fromEntries(idx.cols.map((c, i) => [c, i]));
    rows = idx.rows.map((a) => ({ Z: a[k.Z], A: a[k.A], tier: a[k.tier], macs: a[k.macs30_mb], u30: a[k.unc68_30], ncap: a[k.n_cap], nmxw: a[k.n_mxw], nds: a[k.n_ds], nn2n: a[k.n_n2n], nnp: a[k.n_np], nna: a[k.n_na] }));
    for (const Z of idx.natural) rows.push({ Z, A: 0, tier: -1, ncap: 1, nmxw: 0, nds: 0, nn2n: 0, nnp: 0, nna: 0 });
    rows.forEach((r) => byKey.set(r.Z + "-" + r.A, r));
    const real = rows.filter((r) => r.A); bounds = { n0: 0, n1: Math.max(...real.map((r) => r.A - r.Z)), z0: 0, z1: Math.max(...real.map((r) => r.Z)) };
    layout(); fit(); legend(); paintChart();
    // nothing is fetched for a nuclide until it is opened; a link like data.html#Fe-56 opens that one
    const fromHash = () => { const h = decodeURIComponent(location.hash.slice(1)), r0 = h && parseQ(h.replace(/-nat$/i, " nat")); if (r0 && r0 !== sel) select(r0, true, true); };
    fromHash(); window.addEventListener("hashchange", fromHash);
  }).catch((e) => { $("#dx-legend").textContent = T("dx_fail", "Could not load the data.") + " " + e; });
  let rt; window.addEventListener("resize", () => { clearTimeout(rt); rt = setTimeout(() => { if (!IDX) return; const c = { N: view.x0 + G.W / view.s / 2, Z: view.y0 + G.H / view.s / 2 }; layout(); view.x0 = c.N - G.W / view.s / 2; view.y0 = c.Z - G.H / view.s / 2; drawChart(); renderNuc(); }, 120); });
  window.matchMedia("(prefers-color-scheme: dark)").addEventListener("change", () => { readColors(); legend(); drawChart(); renderNuc(); });
})();
