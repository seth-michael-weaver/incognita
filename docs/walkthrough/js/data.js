/* Data explorer (data.html): a chart of nuclides coloured by how each is known, and for any nuclide the library's
 * predicted curves (with 68 / 95 % bands) beside every curated measurement. Data: data/index.json and data/n/<Z>/<A>.json,
 * built by scripts/build_site_data.py from library/v0.2, data/curation and incognita/bench. Plain script, no build. */
(function () {
  "use strict";
  const es = WT.tl, T = (k, en) => WT.ui(k, en);
  const $ = (s) => document.querySelector(s);
  const th = /[?&]theme=(dark|light)/.exec(location.search); if (th) document.documentElement.dataset.theme = th[1];
  const esc = (s) => String(s ?? "").replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
  const clamp = (v, a, b) => Math.max(a, Math.min(b, v)), log10 = Math.log10;

  // ---------- static text, language switch ----------
  if (es) {
    if (WT.L.ui.dx_title) document.title = WT.L.ui.dx_title;
    document.querySelectorAll("[data-i18n]").forEach((el) => { const t = WT.L.ui[el.dataset.i18n]; if (t != null) el.innerHTML = t; });
    document.querySelectorAll("[data-i18n-aria]").forEach((el) => { const t = WT.L.ui[el.dataset.i18nAria]; if (t != null) el.setAttribute("aria-label", t); });
    document.querySelectorAll("[data-i18n-ph]").forEach((el) => { const t = WT.L.ui[el.dataset.i18nPh]; if (t != null) el.setAttribute("placeholder", t); });
    WT.keepLang();   // after the text above: links inside translated text keep the language too
  }
  // links that keep the language and the EN | ES switch: js/nav.js

  // ---------- formatting ----------
  const num = (v, p = 3) => (v == null || !isFinite(v) ? "–" : WT.dec(Math.abs(v) >= 1e5 || (Math.abs(v) < 1e-3 && v !== 0) ? v.toExponential(p - 1) : (+v.toPrecision(p)).toString()));
  const fmtE = (ev) => (ev >= 1e6 ? num(ev / 1e6) + " MeV" : ev >= 1e3 ? num(ev / 1e3) + " keV" : num(ev) + " eV");
  const SUP = { "-": "⁻", 0: "⁰", 1: "¹", 2: "²", 3: "³", 4: "⁴", 5: "⁵", 6: "⁶", 7: "⁷", 8: "⁸", 9: "⁹" };
  const pow10 = (k) => "10" + String(k).split("").map((c) => SUP[c]).join("");
  const decE = (k) => (k >= -2 ? fmtE(10 ** k) : pow10(k) + " eV"), decY = (k, u) => (k >= -2 && k <= 4 ? num(10 ** k) : pow10(k)) + " " + u;
  const TIERS = [T("dx_t0", "Measured"), T("dx_t1", "Anchored to a measured MACS"), T("dx_t2", "Interpolated (near measured nuclides)"), T("dx_t3", "Extrapolated")];
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
  let libOn = true; // the comparison libraries show by default; untick the box to hide them
  // the same libraries POINTWISE below 1 keV (0 K NJOY RECONR, thinned; DISPLAY-ONLY, scripts/build_site_pointwise.py):
  // data/lib/pw/<Z>/<A|nat>.json, one file per nuclide, listed in data/lib/pw/index.json so absent files are never requested
  let PWI = null, pwiLoad = null; const pwcache = new Map(), PW_E = 1000;
  const loadPwIdx = () => pwiLoad || (pwiLoad = fetch("data/lib/pw/index.json").then((r) => (r.ok ? r.json() : null)).then((j) => { PWI = j ? { ...j, set: new Set(j.keys) } : null; }, () => {}));
  const loadPw = (Z, A) => loadPwIdx().then(() => { const k = nkey(Z, A); if (!PWI || !PWI.set.has(k)) return null;
    if (!pwcache.has(k)) pwcache.set(k, fetch(`data/lib/pw/${k}.json`).then((r) => (r.ok ? r.json() : null)).catch(() => null)); return pwcache.get(k); });
  // measured thermal capture σγ(0.0253 eV) from EXFOR (scripts/build_site_thermal.py): data/thermal.json, fetched once.
  // A measurement, not a library value: it is drawn as a diamond whether or not the overlay is ticked
  // INCOGNITA's own capture below the 1 keV join (RESFILL, scripts/build_site_rr.py): data/rr/<Z>/<A>.json, one per isotope
  // row (none for natural elements); kind own-fit, statistical or smooth, each drawn and labelled differently
  const rrcache = new Map();
  const loadRr = (Z, A) => { if (!A) return Promise.resolve(null); const k = nkey(Z, A);
    if (!rrcache.has(k)) rrcache.set(k, fetch(`data/rr/${k}.json`).then((r) => (r.ok ? r.json() : null)).catch(() => null)); return rrcache.get(k); };
  let TH = null, thLoad = null;
  const loadTh = () => thLoad || (thLoad = fetch("data/thermal.json").then((r) => (r.ok ? r.json() : null)).then((j) => { TH = j && j.th; }, () => {}));
  // Q-values of (n,p), (n,α) and (n,2n) per nuclide, from the engine's mass tables (scripts/build_site_q.py); they place the
  // window of the threshold plots. Fetched once, with the first nuclide; without them the plots fall back to the curves alone
  let QV = null, qLoad = null;
  const loadQ = () => qLoad || (qLoad = fetch("data/q.json").then((r) => (r.ok ? r.json() : null)).then((j) => { QV = j && j.q; }, () => {}));
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
    if (pts.size === 0 && drag) { if (moved < 5 && e.type === "pointerup") { const { N, Z } = fromXY(e.offsetX, e.offsetY), r = byKey.get(Z + "-" + (N + Z)); if (r) select(r, false, false, true); } drag = null; drawChart(); } };
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
  let tab = "cap", cur = null, hl = null, P = null, showExcl = false, tableOpen = false, full = false;
  /** Loading state while nuclide r's file is on its way (r null: done); with err, say it failed and offer a retry. */
  function busy(r, err) {
    const box = $("#dx-nuc"), s = $("#dx-status"), on = !!r && !err;
    box.classList.toggle("dx-loading", !!r); box.setAttribute("aria-busy", String(on)); box.classList.toggle("dx-empty", !cur);
    if (!r) { s.hidden = true; return; }
    box.hidden = false; $("#dx-name").textContent = nameOf(r.Z, r.A); atomSoon(r.Z, r.A);
    $("#dx-tile").innerHTML = `<span>${IDX.sym[r.Z]}</span>`; $("#dx-facts").innerHTML = ""; $("#dx-stats").innerHTML = ""; if ($("#dx-mf")) $("#dx-mf").hidden = true;
    s.hidden = false;
    s.innerHTML = err ? `${T("dx_nload", "Could not load this nuclide.")} <button type="button" class="dx-link" id="dx-retry">${T("dx_retry", "Try again")}</button>`
      : `${T("dx_loading", "Loading")} ${esc(nameOf(r.Z, r.A))}…`;
    if (err) $("#dx-retry").addEventListener("click", () => select(r, false, true));
  }
  // the address names the nuclide and, past capture, the reaction: data.html#Ho-165/np
  const setHash = (r) => history.replaceState(null, "", location.pathname + location.search + "#" + (r.A ? `${IDX.sym[r.Z]}-${r.A}` : `${IDX.sym[r.Z]}-nat`) + (tab !== "cap" ? "/" + tab : ""));
  async function select(r, center, stay, scroll) { // scroll: a click on the chart, which opens the details below it
    sel = r; drawChart();
    if (center && r.A) { view.x0 = r.A - r.Z - G.W / view.s / 2; view.y0 = r.Z - G.H / view.s / 2; if (view.s < 14) zoomAt(G.W / 2, G.H / 2, 18); drawChart(); }
    setHash(r);
    if (!ndata.has(nkey(r.Z, r.A)) || (libOn && !lcache.has(r.Z))) busy(r);
    let d0, lz; // the nuclide's file and, if the overlay is ticked, its element's library file
    let pw, rr;
    try { [d0, lz, , , pw, rr] = await Promise.all([loadNuc(r.Z, r.A), libOn ? loadLib(r.Z) : null, loadQ(), loadTh(), libOn ? loadPw(r.Z, r.A) : null, loadRr(r.Z, r.A)]); } catch (e) { if (sel === r) busy(r, e); return; }
    if (sel !== r) return;
    cur = { r, d: d0, lib: libOf(lz, r, pw), rr }; busy(null);
    buildTabs(); setHash(r);
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
    const mf = mformNote(d.mform), mfb = $("#dx-mf"); if (mfb) { mfb.hidden = !mf; mfb.innerHTML = mf || ""; }
    trustPanel();
    const st =[[r.Z, T("dx_s_p", "protons")], [r.A ? r.A - r.Z : "–", T("dx_s_n", "neutrons")]];
    if (d.macs30) st.push([num(d.macs30) + " mb", T("dx_s_macs", "capture in a star at 30 keV")]);
    if (d.meas) st.push([d.meas.cap.length + d.meas.mxw.length, T("dx_s_pts", "measured capture points")]);
    const nThr = d.thr ? Object.values(d.thr).reduce((s, v) => s + v.length, 0) : 0; if (nThr) st.push([nThr, T("dx_s_thr", "(n,2n), (n,p), (n,α) points")]);
    $("#dx-stats").innerHTML = st.map(([v, l]) => `<div class="dx-stat"><b>${v}</b><span>${l}</span></div>`).join("");
    const nm = r.A ? `${IDX.sym[r.Z]}-${r.A}` : "";
    $("#dx-cmd").textContent = nm && d.cap ? `uv run python -m incognita.library show ${nm} --version v0.2\n\n# or from Python\nfrom incognita.library import capture_curve\ndf = capture_curve("${nm}", version="v0.2")   # energy_ev, sigma_b, lo68_b, hi68_b, lo95_b, hi95_b, tier`
      : `# ${T("dx_nocurve", "no library curve for this entry; the measurements come from")} data/curation/inputs/exfor_cells.parquet`;
    sweep();
    if ((center || scroll) && !stay) $("#dx-nuc").scrollIntoView({ behavior: "smooth", block: "start" });
  }

  /** One plain sentence for a nuclide whose capture below 1 MeV hinges on one engine setting (library v0.2 model_form_flag):
   *  m = { kind: "pe_kev" | "fists2" | "gg_deadend", ratio: other choice / this curve, at 30 keV }. {n} is the factor. */
  function mformNote(m) {
    if (!m || !m.kind) return "";
    const r = m.ratio, side = !(r > 0) ? "" : r < 0.5 ? "lo" : r > 2 ? "hi" : "near", n = num(r > 0 && r < 1 ? 1 / r : r, 2);
    const EN = {
      pe_kev: { lo: "Uncertain model choice: this engine lets a particle escape before the nucleus settles (pre-equilibrium emission) at all energies, while TALYS does so only above about 1 MeV; the TALYS choice gives about {n}× less capture at 30 keV, and the 95 % band below 1 MeV covers both.",
        hi: "Uncertain model choice: this engine lets a particle escape before the nucleus settles (pre-equilibrium emission) at all energies, while TALYS does so only above about 1 MeV; the TALYS choice gives about {n}× more capture at 30 keV, and the 95 % band below 1 MeV covers both.",
        near: "Uncertain model choice: this engine lets a particle escape before the nucleus settles (pre-equilibrium emission) at all energies, while TALYS does so only above about 1 MeV; the TALYS choice agrees with this curve at 30 keV but differs by more than 2× elsewhere below 1 MeV, and the 95 % band there covers both." },
      fists2: { lo: "Uncertain model choice: below 1 MeV this curve depends on one engine setting for how the nucleus passes its fission barriers; the other choice gives about {n}× less capture at 30 keV, and the 95 % band below 1 MeV covers both.",
        hi: "Uncertain model choice: below 1 MeV this curve depends on one engine setting for how the nucleus passes its fission barriers; the other choice gives about {n}× more capture at 30 keV, and the 95 % band below 1 MeV covers both.",
        near: "Uncertain model choice: below 1 MeV this curve depends on one engine setting for how the nucleus passes its fission barriers; the other choice agrees with this curve at 30 keV but differs by more than 2× elsewhere below 1 MeV, and the 95 % band there covers both." },
      gg_deadend: { lo: "This curve uses a correction to the gamma-ray decay of the nucleus that TALYS and TENDL do not apply; without it, capture at 30 keV would be about {n}× less.",
        hi: "This curve uses a correction to the gamma-ray decay of the nucleus that TALYS and TENDL do not apply; without it, capture at 30 keV would be about {n}× more.",
        near: "This curve uses a correction to the gamma-ray decay of the nucleus that TALYS and TENDL do not apply; without it, capture at 30 keV would be about the same." },
    };
    const k = { pe_kev: "pe", fists2: "fi", gg_deadend: "gg" }[m.kind]; if (!k || !side) return "";
    return T(`dx_mf_${k}_${side}`, EN[m.kind][side]).replace("{n}", n);
  }
  function libOf(lz, r, pw) { const n = lz && lz.nuc[r.A ? String(r.A) : "nat"]; return { libs: (lz && lz.libs) || {}, n: n || {}, pw: (pw && pw.libs) || {} }; }
  const libHas = (k) => !!(libOn && cur.lib && Object.values(cur.lib.n).some((v) => v[k]));
  function buildTabs() {
    const tabs = ["cap"], d = cur.d;
    for (const k of ["n2n", "np", "na"]) if ((d.ch && d.ch[k]) || (d.thr && d.thr[k]) || libHas(k)) tabs.push(k);
    if (d.macs || (d.meas && d.meas.mxw.some((p) => p[0] >= 1000)) || libHas("macs")) tabs.push("macs");
    if (!tabs.includes(tab)) tab = "cap";
    cur.tabs = tabs;
    $("#dx-tabs").innerHTML = tabs.map((k) => `<button type="button" role="tab" data-tab="${k}" aria-selected="${k === tab}">${CH[k]}</button>`).join("");
    $("#dx-tabs").querySelectorAll("button").forEach((b) => b.addEventListener("click", () => { tab = b.dataset.tab; hl = null; setHash(cur.r); $("#dx-tabs").querySelectorAll("button").forEach((x) => x.setAttribute("aria-selected", String(x === b))); sweep(); }));
  }
  // evaluated-library curves for the current tab: dashed, thin, one muted colour per library
  function libCurves(out) {
    if (!libOn || !cur.lib) return;
    const xs = tab === "macs" ? IDX.kT_keV.map((k) => k * 1e3) : IDX.grid_ev;
    LIBS.forEach((key, i) => { const v = cur.lib.n[key] && cur.lib.n[key][tab], L = cur.lib.libs[key];
      if (!v || !L) return; const floor = tab === "cap" || tab === "macs" ? 0 : Math.max(...v.filter((y) => y > 0)) * 1e-6; // drop sub-threshold tails so they do not stretch the axis
      const name = `${L.label} (${T("dx_eval_cmp", "evaluated library · comparator, not INCOGNITA")})`;
      out.curves.push({ name, short: L.label, col: C["l" + (i + 1)], pts: xs.map((x, j) => [x, v[j] > floor ? v[j] : null]), dash: true });
      // below 1 keV: the same library pointwise (0 K, thinned), drawn thin and solid so the resonances stay readable
      const p = cur.lib.pw[key] && cur.lib.pw[key][tab];
      if (p && p.e && p.e.length > 1) out.curves.push({ name: `${name} · ${T("dx_pw_short", "pointwise 0 K, below 1 keV")}`, short: L.label, col: C["l" + (i + 1)], pw: true, nmax: p.nmax || 500,
        pts: p.e.map((x, j) => [x, p.s[j]]).filter(([x]) => x <= PW_E * 1.0001) }); });
  }
  const pwOf = (S) => S.curves.filter((c) => c.pw);
  /** σ of a pointwise curve at energy x (lin-lin between the kept points), or null outside it */
  function pwAt(c, x) { const p = c.pts; if (!p.length || x < p[0][0] || x > p[p.length - 1][0]) return null; let a = 0, b = p.length - 1;
    while (b - a > 1) { const h = (a + b) >> 1; if (p[h][0] <= x) a = h; else b = h; } const [x0, y0] = p[a], [x1, y1] = p[b]; // straight in log-log, as drawn
    return x1 > x0 && y0 > 0 && y1 > 0 ? y0 * (y1 / y0) ** (Math.log(x / x0) / Math.log(x1 / x0)) : y0; }
  function libNote() {
    const box = $("#dx-libnote"); box.hidden = !libOn; if (!libOn || !cur) return;
    const L = cur.lib || { libs: {}, n: {} }, have = LIBS.filter((k) => L.n[k] && L.libs[k]), miss = LIBS.filter((k) => !L.n[k]);
    const LAB = { "endfb8.1": "ENDF/B-VIII.1", "jeff4.0": "JEFF-4.0", "tendl2025": "TENDL-2025" };
    const lic = (s) => (s === "US public domain" ? T("dx_lib_pd", "US public domain") : s);
    box.innerHTML = `<p>${T("dx_lib_note", "Dashed lines are evaluated nuclear-data libraries, shown only for comparison: INCOGNITA does not use them and they are not in the downloads. Each is reconstructed at 0 K from the library’s ENDF-6 file (NJOY) and averaged over the same energy bins as the curve (log-energy bin averages, so resonances are smoothed out); the MACS uses the full pointwise curve.")}</p>`
      + (have.some((k) => L.pw && L.pw[k] && L.pw[k][tab]) ? `<p>${(tab === "cap" && cur.rr ? T("dx_lib_pw_rr", "Below 1 keV the same libraries are drawn pointwise, as thin solid lines: reconstructed at 0 K (NJOY RECONR, 0.01 % tolerance) and thinned to at most {n} points per curve, choosing the points that keep the resonance peaks and dips. They are comparators too, not INCOGNITA.")
        : T("dx_lib_pw", "Below 1 keV the same libraries are drawn pointwise, as thin solid lines: reconstructed at 0 K (NJOY RECONR, 0.01 % tolerance) and thinned to at most {n} points per curve, choosing the points that keep the resonance peaks and dips. They are comparators too: INCOGNITA has no curve below 1 keV.")).replace("{n}", Math.max(500, ...have.map((k) => (L.pw[k] && L.pw[k][tab] && L.pw[k][tab].nmax) || 500)))}${have.some((k) => L.pw[k] && L.pw[k][tab] && L.pw[k][tab].nmax > 500) ? " " + T("dx_lib_pw_dense", "This nuclide has many resonances below 1 keV, so it keeps more points: five per resonance peak, up to 5000 (with 500, a fixed budget, many peaks of U-235 or Pu-239 would be cut).") : ""}</p>` : "")
      + (have.length ? `<ul>${have.map((k) => `<li><i style="color:${C["l" + (LIBS.indexOf(k) + 1)]}"></i><span><b>${esc(L.libs[k].label)}</b> · ${esc(lic(L.libs[k].lic))} · ${esc(L.libs[k].cite)}</span></li>`).join("")}</ul>` : "")
      + `<p>${miss.length ? `${T("dx_lib_none", "No file for this nuclide in")} ${miss.map((k) => LAB[k]).join(", ")}. ` : ""}${(() => { const no = have.filter((k) => !L.n[k][tab]); return no.length ? `${T("dx_lib_notab", "No separate value for this reaction in")} ${no.map((k) => LAB[k]).join(", ")}. ` : ""; })()}${T("dx_lib_held", "JENDL-5 will be added once its terms for redistributing derived tables are confirmed.")}</p>`;
  }

  // INCOGNITA's own curve below 1 keV (RESFILL): what it is, in plain words, by kind; and how it is drawn
  const RR_STYLE = { "own-fit": { w: 2.2, halo: 0, dash: [] }, statistical: { w: 1.8, halo: 0, dash: [6, 3, 1.5, 3] }, smooth: { w: 1.4, halo: 0, dash: [1.5, 3] } };
  const rrSty = (k) => RR_STYLE[k] || RR_STYLE.smooth;
  const rrAnch = (rr) => !!(rr.thermal && rr.thermal.anchored);
  function rrLabel(rr) {
    if (rr.kind === "own-fit") return T("dx_rr_own", "INCOGNITA’s own resonance fit to measured data (up to 300 eV; statistical resonances from 300 eV to 1 keV)");
    if (rr.kind === "statistical") return T("dx_rr_stat", "statistical resonances from INCOGNITA’s own average parameters, not the measured resonances: the peak positions are one random sample; over many nuclides the resonance integral is typically within a factor of 2 of measurement") + (rrAnch(rr) ? T("dx_rr_anch", "; passes through the measured thermal capture") : "");
    return rrAnch(rr) ? T("dx_rr_sm_a", "INCOGNITA’s smooth estimate through the measured thermal capture; no resonances drawn") : T("dx_rr_sm", "INCOGNITA’s smooth estimate; real thermal values can differ by orders of magnitude");
  }
  const rrShort = (rr) => rr.kind === "own-fit" ? T("dx_rr_k_own", "own resonance fit") : rr.kind === "statistical" ? T("dx_rr_k_stat", "statistical resonances (not the real peaks)") : T("dx_rr_k_sm", "smooth estimate (no resonances)");
  function rrSentence(rr, th) {
    let s = rr.kind === "own-fit" ? T("dx_below_own", "Below 1 keV the solid line is INCOGNITA’s own resonance fit to measured capture data up to 300 eV; from 300 eV to 1 keV it uses statistical resonances. It joins the prediction at 1 keV.")
      : rr.kind === "statistical" ? T("dx_below_stat", "Below 1 keV the dash-dot line is INCOGNITA’s statistical estimate: resonances with INCOGNITA’s own average spacing and widths, placed at random, so single peaks do not match the real ones. Tested on nuclides whose resonance integral was held out, it was typically within a factor of 2 of measurement, and no better: median off by ×1.9, 54 % within ×2.") 
      : rrAnch(rr) ? T("dx_below_sm_a", "Below 1 keV the dotted line is INCOGNITA’s smooth estimate: a 1/v curve through the measured thermal capture, bridged to the 1 keV value. No resonances are drawn, so between about 1 eV and 1 keV the real cross section can be far higher at its peaks.")
      : T("dx_below_sm", "Below 1 keV the dotted line is INCOGNITA’s smooth estimate: the 1 keV value continued as 1/v, with no resonances and no measurement to pin it. Real thermal values can differ from it by orders of magnitude.");
    const te = rr.thermal && rr.thermal.exp;
    if (rrAnch(rr) && te && te.value > 0) { s += " " + T("dx_below_anch", "It is forced through a measured thermal capture value, {v} b.").replace("{v}", num(te.value, 3));
      if (th && th.y > 0 && Math.abs(th.y / te.value - 1) > 0.05) s += " " + T("dx_rr_anch_diff", "The diamond is a separate average of EXFOR entries and differs from it."); }
    const ri = riText(rr); if (ri) s += " " + ri;
    return s;
  }
  // the resonance-integral comparison for one nuclide (RESFILL rr/<Z>/<A>.json "ri"), or "" when there is no measured RI
  function riText(rr) {
    const ri = rr && rr.ri; if (!(ri && ri.exp && ri.exp.value > 0 && ri.model_b > 0)) return "";
    let s = T("dx_rr_ri", "Resonance integral of capture above 0.5 eV for this nuclide: INCOGNITA {m} b, measured {e} b.").replace("{m}", num(ri.model_b, 3)).replace("{e}", num(ri.exp.value, 3));
    if (/^used/.test(ri.role || "")) s += " " + T("dx_rr_ri_used", "That measured value was used to pick this random sample, so the agreement is not a test.");
    else if (/^HOLD/.test(ri.role || "")) s += " " + T("dx_rr_ri_hold", "That measured value was held out: it was not used to make this curve.");
    return s;
  }

  /** "How far to trust this": only checked results, no new claims.
   *  Tier meanings, the validated range (Z 26–83), model_form_flag: library/v0.2/README.md and CHANGELOG.md.
   *  Bands: the pre-registered coverage check of 2026-10-24 (research reports/COVAR.md, 5 test nuclides; caveat in
   *  library/v0.2/README.md): capture, fission, elastic covered as stated; (n,p), (n,α), (n,2n) and total under-covered.
   *  Capture "if anything, wide": library/v0.2/README.md ("the bands are on the wide side").
   *  Engine errors: data/board/cells.csv, engine section (scoring "in-sample (development)", not blind), score_ours of the
   *  row with the most nuclei: [view, nuclei, Z from, Z to (nuclei in d_pernuc.csv / band name), rms dex]. */
  const BOARD = {
    cap: [["capture_all", 41, 26, 82, 0.1299289503]],
    macs: [["K185 Z20-39", 20, 20, 39, 0.1608116676], ["K185 Z40-59", 15, 40, 59, 0.1538501219], ["K185 Z60-83", 69, 60, 83, 0.1141666319]],
    n2n: [["thrA1_n2n", 35, 28, 92, 0.08696570963]], np: [["thrA1_np", 41, 26, 92, 0.1691835923]], na: [["thrA1_na", 25, 26, 82, 0.1860277146]],
  };
  function trustPanel() {
    const box = $("#dx-trust"); if (!box) return;
    const d = cur.d, r = cur.r, rr = cur.rr;
    if (d.tier == null || !r.A) { box.hidden = true; box.innerHTML = ""; return; }
    const TT = [
      T("dx_tr_t0", "Measured nucleus. The curve is still the engine’s own prediction, not fitted to these measurements; but the engine’s global settings were chosen using many nuclei, this one among them, so a match here is a check, not an independent test."),
      T("dx_tr_t1", "Anchored. No measured cross sections, but a measured stellar average at 30 keV: the engine’s curve is scaled by one factor to match it, so its shape is still the model’s."),
      T("dx_tr_t2", "Interpolated. Not measured, but within two neutrons or protons of measured nuclei; the curve is the model’s prediction."),
      T("dx_tr_t3", "Extrapolated. Not measured and not close to measured nuclei (or without structure data): the curve is the model alone, with no measurement to check it.")];
    const h = [`<h3>${T("dx_tr_h", "How far to trust this")}</h3>`, `<p><span class="dx-chip t${d.tier}">${TIER_SHORT[d.tier]}</span> ${TT[d.tier]}</p>`];
    if (!d.valid) h.push(`<p>${T("dx_tr_out", "Outside Z 26–83, the range the library’s validation covers.")}</p>`);
    const mk = d.mform && d.mform.kind;
    if (mk === "pe_kev" || mk === "fists2") h.push(`<p>${T("dx_tr_mf", "Model-form flag: one engine setting changes capture here by more than a factor of 2 (see the note above). No measurement can decide between the two choices; the bands below 1 MeV are widened to contain both.")}</p>`);
    else if (mk === "gg_deadend") h.push(`<p>${T("dx_tr_mf_gg", "Model-form flag: the value relies on the engine’s fix of a missing gamma-decay width (see the note above); the band is not widened for it.")}</p>`);
    const tabs = cur.tabs || ["cap"], li = [];
    for (const k of tabs) {
      // the coverage check scored measured nuclei only, so for an unmeasured nucleus (tier 2, 3) it says nothing
      const band = k === "cap" ? (!d.u68 ? "" : d.tier >= 2 ? T("dx_tr_b_unm", "bands checked only on measured nuclei, not on nuclei like this one") : T("dx_tr_b_ok", "bands cover as stated (if anything, wide)"))
        : k === "macs" ? (d.macsU ? T("dx_tr_b_macs", "band not checked on its own") : "")
        : k === "np" && d.npL && d.npL.some((p) => p[2] != null) ? T("dx_tr_b_narrow", "band likely too narrow: it under-covered")
        : T("dx_tr_b_none", "no band shown");
      const tested = k === "cap" ? d.tier === 0 : k === "macs" ? d.tier <= 1 : !!(d.thr && d.thr[k] && d.thr[k].length);
      const b = tested && (BOARD[k] || []).find((x) => r.Z >= x[2] && r.Z <= x[3]);
      const err = b ? T("dx_tr_e", "Scoreboard error typically ×{f} ({n} measured nuclei, Z {z}; not blind)").replace("{f}", num(10 ** b[4], 3)).replace("{n}", b[1]).replace("{z}", `${b[2]}–${b[3]}`)
        : T("dx_tr_e_none", "no held-out test for this region");
      li.push(`<li><b>${CH[k]}</b> <span>${[band, err].filter(Boolean).join(" · ")}</span></li>`);
    }
    if (d.cap && rr && rr.kind) { const ri = riText(rr); li.push(`<li><b>${T("dx_rr_b1k", "Below 1 keV")}</b> <span>${rrShort(rr)}${ri ? " · " + ri : ""}</span></li>`); }
    h.push(`<ul>${li.join("")}</ul>`);
    h.push(`<p class="dx-tr-src">${T("dx_tr_src", "Tier and flags: library/v0.2 README. Bands: a pre-registered coverage check against measurements (5 test nuclides, October 2026), in which capture, fission and elastic bands covered as stated and the threshold channels and total under-covered. Errors: the <a href=\"scoreboard.html\" data-keep-lang>Scoreboard</a>, root-mean-square of log10(engine / measured); it is not a blind test, because the engine’s rules were chosen while watching it.")}</p>`);
    box.innerHTML = h.join(""); box.hidden = false; WT.keepLang();
  }
  const rrSwatch = (c) => { const s = rrSty(c.rr); return `<svg class="dx-rrsw" width="22" height="8" aria-hidden="true"><line x1="1" y1="4" x2="21" y2="4" stroke="${c.col}" stroke-width="${s.w}" stroke-dasharray="${s.dash.join(" ")}" stroke-linecap="round"/></svg>`; };

  // series for the current tab: { unit, curves:[{name,col,pts:[[x,y]],band68:[[x,lo,hi]],band95}], points:[{x,y,lo,hi,xlo,xhi,ds,dec,kind}], ds:[...] }
  function series() {
    const d = cur.d, grid = IDX.grid_ev, out = { curves: [], points: [], ds: [], xlab: T("dx_xE", "neutron energy"), unit: "b", note: null };
    const band = (ys, us) => grid.map((x, i) => (ys[i] > 0 && us && us[i] != null ? [x, ys[i] / 10 ** us[i], ys[i] * 10 ** us[i]] : null)).filter(Boolean);
    if (tab === "cap") {
      if (d.cap) out.curves.push({ name: "INCOGNITA · " + T("dx_pred", "prediction (library v0.2)"), col: C.curve, pts: grid.map((x, i) => [x, d.cap[i]]), b68: band(d.cap, d.u68), b95: band(d.cap, d.u95) });
      // below 1 keV, INCOGNITA's own curve (RESFILL, 0 K), joined to the prediction's first point (1 keV, cap[0])
      const rr = cur.rr;
      if (d.cap && d.cap[0] > 0 && rr && rr.E && rr.cap && rr.E.length > 1) out.curves.push({ name: `${T("dx_rr_b1k", "Below 1 keV")}: ${rrLabel(rr)}`, short: rrShort(rr), col: C.curve, rr: rr.kind, rrd: rr,
        pts: [...rr.E.map((x, j) => [x, rr.cap[j]]).filter(([x]) => x < grid[0] * 0.9999), [grid[0], d.cap[0]]] });
      const th = TH && cur.r.A && TH[`${cur.r.Z}-${cur.r.A}`]; // [value b, 1σ b, n entries, tier, [EXFOR subentries], note]
      if (th) out.th = { x: 0.0253, y: th[0], u: th[1], n: th[2], tier: th[3], subs: th[4] || [], abs: th[5] === "abs" };
      if (d.meas) { out.ds = d.meas.ds;
        for (const p of d.meas.cap) out.points.push({ x: Math.sqrt(p[0] * p[1]), xlo: p[0], xhi: p[1], y: p[2], e: p[3], ds: p[4], dec: p[5], st: p[6], kind: "sig" });
        for (const p of d.meas.mxw) if (p[0] < 1000) out.points.push({ x: p[0], xlo: p[0], xhi: p[1], y: p[2], e: p[3], ds: p[4], dec: p[5], st: p[6], kind: "mxw" }); }
      libCurves(out);
      if (d.res) out.note = { upto: d.res, text: T("dx_res", "resolved resonances: the curve is an average here") };
    } else if (tab === "macs") {
      out.xlab = "kT"; out.unit = "mb";
      if (d.macs) out.curves.push({ name: "INCOGNITA · " + T("dx_pred", "prediction (library v0.2)"), col: C.curve, pts: IDX.kT_keV.map((k, i) => [k * 1e3, d.macs[i]]), b68: IDX.kT_keV.map((k, i) => (d.macsU && d.macsU[i] ? [k * 1e3, d.macs[i] / d.macsU[i], d.macs[i] * d.macsU[i]] : null)).filter(Boolean) });
      libCurves(out);
      if (d.meas) { out.ds = d.meas.ds; for (const p of d.meas.mxw) if (p[0] >= 1000) out.points.push({ x: p[0], xlo: p[0], xhi: p[1], y: p[2] * 1000, e: p[3], ds: p[4], dec: p[5], st: p[6], kind: "mxw" }); }
    } else {
      out.unit = "mb";
      // v0.2: (n,2n), (n,p), (n,α) come from the same engine runs as capture; (n,p) also has a 68 % band (npL: the engine's
      // (n,p) at the benchmark energies, from the same runs), drawn around the one curve
      const npB = tab === "np" && d.npL ? d.npL.filter((p) => p[2] != null).map((p) => [p[0], p[2], p[3]]) : null;
      if (d.ch && d.ch[tab]) out.curves.push({ name: "INCOGNITA · " + T("dx_pred", "prediction (library v0.2)"), col: C.curve, pts: grid.map((x, i) => [x, d.ch[tab][i]]), b68: npB && npB.length > 1 ? npB : undefined });
      else if (npB) out.curves.push({ name: "INCOGNITA · " + T("dx_pred", "prediction (library v0.2)"), col: C.curve, pts: d.npL.map((p) => [p[0], p[1]]), b68: npB });
      libCurves(out);
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
  // The window of a threshold plot opens where the reaction can contribute, not at the 1e-30 mb tail of the curves.
  // Physics edge: the kinematic threshold, and for a proton or alpha out, the neutron energy at which it leaves with half
  // the Coulomb barrier of the residual nucleus (below that, tunnelling leaves a negligible cross section); the window starts
  // at half that energy so the rise is in view, but never far below the threshold, under which there is nothing. It opens further down for any measured point, and for any curve that reaches
  // 1 % of the reaction's size at 14 MeV (thermal and resonance (n,α), for example). The size at 14 MeV is the median over
  // the curves, so one curve far off does not move the axes; the y-axis reaches four decades below it.
  // Without a Q-value, the edge is where the curves come within four decades of their peak.
  function thrWindow(S, shown) {
    const { Z, A } = cur.r, q = QV && A && QV[`${Z}-${A}`], Q = q ? q[{ np: 0, na: 1, n2n: 2 }[tab]] : null;
    const at14 = (c) => { let b = null, bd = 0.1; for (const [x, y] of c.pts) { const dd = Math.abs(log10(x / 14e6)); if (y > 0 && dd < bd) { bd = dd; b = y; } } return b; };
    const refs = S.curves.map(at14).filter((v) => v > 0).sort((a, b) => a - b);
    const top = Math.max(0, ...S.curves.flatMap((c) => c.pts.map(([, y]) => y || 0))), ref = refs.length ? refs[(refs.length - 1) >> 1] : top;
    if (!(ref > 0)) return null;
    const marks = []; let edge, thrE = 0;
    if (Q != null) {
      const kin = (A + 1) / A; thrE = Q < 0 ? -Q * kin * 1e6 : 0;
      if (thrE > 0) marks.push([thrE, T("dx_mk_thr", "threshold")]);
      if (tab === "n2n") edge = thrE;
      else {
        const [z, a] = tab === "np" ? [1, 1] : [2, 4], Ar = A + 1 - a, Vc = 1.44 * z * (Z - z) / (1.4 * (Ar ** (1 / 3) + a ** (1 / 3))); // MeV
        const cb = Math.max(thrE, (Vc - Q) * kin * 1e6); if (cb > thrE) marks.push([cb, T("dx_mk_cb", "Coulomb barrier")]);
        edge = Math.max(thrE, (Vc / 2 - Q) * kin * 1e6);
      }
    } else edge = Math.min(...S.curves.flatMap((c) => c.pts.filter(([, y]) => y > top * 1e-4).map(([x]) => x)));
    let x0 = isFinite(edge) && edge > 0 ? Math.max(edge / 2, thrE * 0.9) : 0; // nothing at all below the threshold
    for (const c of S.curves) for (const [x, y] of c.pts) if (y >= ref * 0.01 && x < x0) x0 = x;
    for (const p of shown) if (p.y > 0 && (p.xlo || p.x) < x0) x0 = p.xlo || p.x;
    return { x0, yf: ref * 1e-4, marks };
  }
  function buildNuc() {
    if (!cur) return;
    const S = series(), shown = S.points.filter((p) => showExcl || p.dec !== "x");
    const W = pcv.parentElement.clientWidth, H = Math.round(clamp(W * 0.55, 300, 460));
    P = { ...setupCanvas(pcv, H), S, shown };
    const ctx = layer(LAY.a), m = { l: 62, r: 16, t: 16, b: 44 };
    // ranges (log-log)
    let x0 = Infinity, x1 = -Infinity, y0 = Infinity, y1 = -Infinity;
    const ax = (x) => { if (x < x0) x0 = x; if (x > x1) x1 = x; }, ay = (y) => { if (y < y0) y0 = y; if (y > y1) y1 = y; };
    // (n,2n), (n,p), (n,α): the window from thrWindow unless "full energy range" is ticked; measured points always stay in range
    const tw = tab !== "cap" && tab !== "macs" ? thrWindow(S, shown) : null, win = full ? null : tw, xf = win ? win.x0 : 0, yf = win ? win.yf : 0;
    if (xf > 0) ax(xf);
    // a pointwise library curve's deepest interference dips do not stretch the y-axis: it reaches at most 9 decades below the top
    const ytop = Math.max(0, ...S.curves.flatMap((c) => c.pts.map(([, y]) => y || 0))), ypw = Math.max(yf, ytop * 1e-9);
    S.curves.forEach((c) => { c.pts.forEach(([x, y]) => { if (y > (c.pw || c.rr ? ypw : yf) && x >= xf) { ax(x); ay(y); } }); (c.b68 || []).forEach(([x, lo, hi]) => { if (x < xf) return; if (lo > yf) ay(lo); if (hi > yf) ay(hi); }); });
    shown.forEach((p) => { if (p.y > 0) { ax(p.xlo || p.x); ax(p.xhi || p.x); ay(p.y); } });
    if (S.th && S.th.y > 0) { ax(S.th.x); ay(S.th.y); }
    for (const c of [LAY.p, LAY.c]) layer(c);
    if (!(x1 > 0)) { ctx.fillStyle = C.surface; ctx.fillRect(0, 0, W, H); ctx.fillStyle = C.soft; ctx.font = `500 14px ${SANS}`; ctx.textAlign = "center"; ctx.fillText(T("dx_empty", "Nothing to show for this reaction."), W / 2, H / 2); finishNuc(S); return; }
    x0 = log10(x0); x1 = log10(x1); y0 = log10(y0); y1 = log10(y1);
    if (x1 - x0 < 1 && !win) { x0 -= 0.5; x1 += 0.5; } // a threshold window keeps its edge: it may span under a decade if (y1 - y0 < 1) { y0 -= 0.5; y1 += 0.5; }
    x0 -= 0.05 * (x1 - x0); x1 += 0.05 * (x1 - x0); y0 -= 0.08 * (y1 - y0); y1 += 0.08 * (y1 - y0);
    const X = (x) => m.l + (log10(x) - x0) / (x1 - x0) * (W - m.l - m.r), Y = (y) => H - m.b - (log10(y) - y0) / (y1 - y0) * (H - m.t - m.b);
    Object.assign(P, { X, Y, m, x0, x1, y0, y1, W, H });
    ctx.fillStyle = C.surface; ctx.fillRect(0, 0, W, H);
    // grid and axes (decades)
    ctx.font = `500 12px ${SANS}`; ctx.fillStyle = C.soft; ctx.strokeStyle = C.grid; ctx.lineWidth = 1;
    ctx.textAlign = "center"; ctx.textBaseline = "top";
    { let lastX = -1e9; const step = W < 600 ? 62 : 48, minor = x1 - x0 < 1.6 ? [1, 2, 5] : [1]; // a narrow (threshold) window also marks 2 and 5
      for (let k = Math.floor(x0); k <= Math.floor(x1); k++) for (const f of minor) { const v = f * 10 ** k; if (log10(v) < x0 || log10(v) > x1) continue;
        const x = X(v); ctx.strokeStyle = f === 1 ? C.grid : rgba(C.soft, 0.08); ctx.beginPath(); ctx.moveTo(x, m.t); ctx.lineTo(x, H - m.b); ctx.stroke(); if (x - lastX >= step) { ctx.fillText(f === 1 ? decE(k) : fmtE(v), x, H - m.b + 6); lastX = x; } }
      ctx.strokeStyle = C.grid; }
    ctx.textAlign = "right"; ctx.textBaseline = "middle";
    for (let k = Math.ceil(y0); k <= Math.floor(y1); k++) { const y = Y(10 ** k); ctx.beginPath(); ctx.moveTo(m.l, y); ctx.lineTo(W - m.r, y); ctx.stroke(); ctx.fillText(decY(k, S.unit), m.l - 8, y); }
    ctx.textAlign = "left"; ctx.textBaseline = "alphabetic"; ctx.fillText(S.xlab + " →", m.l, H - 6);
    let note = null; // drawn last, over the points, with a dark halo so it stays readable
    ctx.save(); ctx.beginPath(); ctx.rect(m.l, m.t, W - m.l - m.r, H - m.t - m.b); ctx.clip();
    const wrap = (text, maxW) => { if (maxW < 60) return null; const out = []; let ln = ""; // wrapped to the room it has, so a narrow (phone) plot shows the whole note
      for (const w of text.split(" ")) { const t = ln ? ln + " " + w : w; if (ln && ctx.measureText(t).width > maxW) { out.push(ln); ln = w; } else ln = t; }
      out.push(ln); return out; };
    ctx.font = `500 12px ${SANS}`;
    // capture below 1 keV: INCOGNITA's own RESFILL curve where there is one (its kind named on the left), else only the
    // evaluated libraries (comparators) and measurements; a dotted line marks 1 keV
    const own = tab === "cap" && S.curves.some((c) => !c.dash && !c.pw), split = own && 10 ** x0 < PW_E && 10 ** x1 > PW_E ? X(PW_E) : null;
    const rrC = S.curves.find((c) => c.rr);
    let below = null;
    if (split != null) {
      ctx.strokeStyle = rgba(C.soft, 0.7); ctx.setLineDash([2, 4]); ctx.beginPath(); ctx.moveTo(split, m.t); ctx.lineTo(split, H - m.b); ctx.stroke(); ctx.setLineDash([]); ctx.strokeStyle = C.grid;
      if (split - m.l >= 220) below = wrap(rrC ? T("dx_below_rr", "below 1 keV: INCOGNITA’s {k}").replace("{k}", rrC.short) : T("dx_below_cv", "below 1 keV: no INCOGNITA curve, only evaluated libraries and measurements"), split - m.l - 16); // a narrow (phone) plot leaves it to the sentence under the plot
    }
    const nx = split != null ? split : m.l; // the resolved-resonance note covers INCOGNITA's own range only
    if (S.note && S.note.upto > Math.max(10 ** x0, split != null ? PW_E : 0)) { const xe = Math.min(X(S.note.upto), W - m.r); ctx.fillStyle = rgba(C.soft, 0.07); ctx.fillRect(nx, m.t, xe - nx, H - m.t - m.b);
      if (xe - nx > 120) note = wrap(S.note.text, W - m.r - nx - 16); }
    // bands, then measured points, then the curves on top
    for (const c of S.curves) {
      for (const [b, a] of [[c.b95, 0.1], [c.b68, 0.2]]) if (b && b.length > 1) { ctx.fillStyle = rgba(c.col, a); ctx.beginPath(); b.forEach(([x, , hi], i) => (i ? ctx.lineTo(X(x), Y(hi)) : ctx.moveTo(X(x), Y(hi)))); for (let i = b.length - 1; i >= 0; i--) ctx.lineTo(X(b[i][0]), Y(Math.max(b[i][1], 10 ** (y0 - 1)))); ctx.closePath(); ctx.fill(); }
    }
    // threshold and Coulomb-barrier markers of a threshold reaction: a dotted line, labelled at the top
    ctx.font = `500 12px ${SANS}`; ctx.textBaseline = "alphabetic";
    (tw ? tw.marks : []).forEach(([e, label], i) => { const x = X(e); if (x < m.l || x > W - m.r) return;
      ctx.strokeStyle = rgba(C.soft, 0.55); ctx.setLineDash([2, 4]); ctx.beginPath(); ctx.moveTo(x, m.t); ctx.lineTo(x, H - m.b); ctx.stroke(); ctx.setLineDash([]);
      const right = x > W - m.r - 130; ctx.fillStyle = C.soft; ctx.textAlign = right ? "right" : "left"; ctx.fillText(label, x + (right ? -5 : 5), m.t + 12 + i * 16); });
    ctx.restore();
    drawPoints(false);
    const cc = LAY.c.getContext("2d"); cc.save(); cc.beginPath(); cc.rect(m.l, m.t, W - m.l - m.r, H - m.t - m.b); cc.clip();
    const lib = (c) => !!(c.dash || c.pw), zOf = (c) => (c.rr ? 2 : lib(c) ? 1 : 0); // INCOGNITA's own below-1-keV curve last, over the comparators
    // INCOGNITA's own curve below 1 keV: solid for its own resonance fit, dash-dot for statistical resonances, thin dotted for the smooth estimate
    const sty = (c) => { if (c.pw) return [[1.15, c.col]]; if (c.dash) return [[1.7, c.col]]; if (c.rr) { const s = rrSty(c.rr); return s.halo ? [[s.halo, C.surface], [s.w, c.col]] : [[s.w, c.col]]; } return [[5, C.surface], [2.2, c.col]]; };
    for (const c of [...S.curves].sort((a, b) => zOf(a) - zOf(b))) for (const [w, col] of sty(c)) { // library lines go on top, thin and without a halo, so they never hide the prediction; pointwise ones solid, so the resonances stay readable
      const glow = !(w > 3 || lib(c) || (c.rr && c.rr !== "own-fit"));
      cc.strokeStyle = col; cc.lineWidth = w; cc.shadowColor = glow ? col : "transparent"; cc.shadowBlur = glow ? 12 : 0; cc.lineJoin = "round"; cc.setLineDash(c.dash ? [7, 5] : c.rr ? rrSty(c.rr).dash : []); cc.globalAlpha = c.pw ? 0.9 : 1; cc.beginPath(); let on = false;
      for (const [x, y] of c.pts) { if (!(y > 0)) { on = false; continue; } on ? cc.lineTo(X(x), Y(y)) : cc.moveTo(X(x), Y(y)); on = true; }
      cc.stroke(); cc.globalAlpha = 1;
    }
    cc.shadowBlur = 0; cc.setLineDash([]); cc.font = `500 12px ${SANS}`; cc.textAlign = "left"; cc.textBaseline = "alphabetic"; cc.lineJoin = "round"; cc.lineWidth = 3; cc.strokeStyle = document.documentElement.dataset.theme === "light" ? C.surface : "rgba(8,13,28,.85)"; cc.fillStyle = C.soft;
    for (const [lines, x0n] of [[note, nx], [below, m.l]]) if (lines) lines.forEach((l, i) => { cc.strokeText(l, x0n + 8, m.t + 14 + i * 15); cc.fillText(l, x0n + 8, m.t + 14 + i * 15); });
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
    // the measured thermal capture value (EXFOR): a diamond with its 1σ error bar and short caps, outlined in ink
    const th = P.S.th;
    if (th && th.y > 0) { const x = X(th.x), y = Y(th.y), r = 7; ctx.globalAlpha = 1;
      if (th.u > 0) { const ya = Y(th.y + th.u), yb = Y(Math.max(th.y - th.u, th.y * 0.05)); ctx.strokeStyle = C.ink; ctx.lineWidth = 1.5; ctx.beginPath(); ctx.moveTo(x, ya); ctx.lineTo(x, yb); ctx.moveTo(x - 4, ya); ctx.lineTo(x + 4, ya); ctx.moveTo(x - 4, yb); ctx.lineTo(x + 4, yb); ctx.stroke(); }
      ctx.beginPath(); ctx.moveTo(x, y - r); ctx.lineTo(x + r, y); ctx.lineTo(x, y + r); ctx.lineTo(x - r, y); ctx.closePath();
      ctx.fillStyle = C.meas; ctx.fill(); ctx.strokeStyle = C.ink; ctx.lineWidth = 1.6; ctx.stroke(); }
    ctx.globalAlpha = 1;
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
    $("#dx-full").parentElement.hidden = tab === "cap" || tab === "macs";
    libNote();
    const pws = pwOf(S);
    const leg = S.curves.filter((c) => !c.pw).map((c) => c.dash ? `<span class="dx-key">${pws.some((q) => q.short === c.short) ? `<i class="ln thin" style="background:${c.col}"></i>` : ""}<i class="dash" style="color:${c.col}"></i>${esc(c.name)}${pws.some((q) => q.short === c.short) ? ` · ${T("dx_pw_leg2", "solid below 1 keV: pointwise, 0 K")}` : ""}</span>` : c.rr ? `<span class="dx-key dx-rrkey">${rrSwatch(c)}<span>${esc(c.name)}</span></span>` : `<span class="dx-key"><i class="ln" style="background:${c.col}"></i>${c.name}${c.b95 ? ` · ${T("dx_bands", "bands: 68 % and 95 %")}` : c.b68 && !c.name.includes("68") ? ` · ${T("dx_band68", "band: 68 %")}` : ""}</span>`);
    if (nPts) leg.push(`<span class="dx-key"><i class="dot" style="background:${C.meas}"></i>${T("dx_meas_pts", "measured")} (${nPts}${nEx ? `, ${nEx} ${T("dx_excl", "excluded")}` : ""})</span>`);
    if (S.th) leg.push(`<span class="dx-key"><i class="dia" style="background:${C.meas};border-color:${C.ink}"></i>${T("dx_th", "measured thermal value (EXFOR)")}</span>`);
    $("#dx-plegend").innerHTML = leg.join("");
    // under the plot, in plain words: where INCOGNITA's own curve starts, and what the diamond is (with its EXFOR entries)
    const bl = $("#dx-below"), xl = P && P.X ? 10 ** P.x0 : Infinity, ownC = S.curves.some((c) => !c.dash && !c.pw);
    if (bl) { const parts = [];
      const rrC = S.curves.find((c) => c.rr);
      if (tab === "cap" && ownC && xl < PW_E) parts.push(rrC ? rrSentence(rrC.rrd, S.th) : T("dx_below", "INCOGNITA’s own curve starts at 1 keV; below that only comparators and measurements are shown."));
      if (S.th) { const t = S.th, links = t.subs.map((s) => { const ex = exforOf(s); return ex ? `<a href="${ex.url}" target="_blank" rel="noopener">${ex.id}</a>` : esc(s); }).join(", ");
        parts.push(`${T("dx_th_sent", "Diamond: measured thermal capture cross section σγ(0.0253 eV)")} = <b>${num(t.y, 4)} ± ${num(t.u, 2)} b</b>, ${T("dx_th_mean", "weighted mean of {n} EXFOR entries").replace("{n}", t.n)}${t.abs ? ` (${T("dx_th_abs", "absorption minus fission")})` : ""}: ${links}.`); }
      bl.innerHTML = parts.join(" "); bl.hidden = !parts.length; }
    pcv.setAttribute("aria-label", `${nameOf(cur.r.Z, cur.r.A)}, ${CH[tab]}: ${S.curves.length ? S.curves.filter((c) => !c.pw).map((c) => c.name).join(", ") : ""}${nPts ? `; ${nPts} ${T("dx_meas_pts", "measured")}` : ""}${S.th ? `; ${T("dx_th", "measured thermal value (EXFOR)")} ${num(S.th.y, 4)} b` : ""}. ${T("dx_table_hint", "Use “Show as a table” for the values.")}`);
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
    if (S.th) rowsP.push(`<tr><td>${T("dx_th", "measured thermal value (EXFOR)")} · ${S.th.subs.map(esc).join(", ")}</td><td>${fmtE(S.th.x)}</td><td>${num(S.th.y, 4)} b</td><td>± ${num(S.th.u, 2)} b</td><td></td></tr>`);
    $("#dx-table").innerHTML = `<table><thead><tr><th>${T("dx_th_src", "Source")}</th><th>${S.xlab}</th><th>${T("dx_th_val", "Value")}</th><th>${T("dx_th_unc", "Range / uncertainty")}</th><th>${T("dx_th_cur", "Curation")}</th></tr></thead><tbody>${rowsC.join("")}${rowsP.join("")}</tbody></table>`;
  }
  $("#dx-tbtn").addEventListener("click", (e) => { tableOpen = !tableOpen; e.currentTarget.setAttribute("aria-expanded", String(tableOpen)); $("#dx-table").hidden = !tableOpen; if (tableOpen) table(series()); });
  $("#dx-lib").addEventListener("change", async (e) => { libOn = e.target.checked; if (!cur) return; const c0 = cur;
    if (libOn) { $("#dx-libnote").hidden = false; $("#dx-libnote").textContent = T("dx_lib_loading", "Loading the libraries…"); const [lz, pw] = await Promise.all([loadLib(c0.r.Z), loadPw(c0.r.Z, c0.r.A)]); if (cur !== c0) return; cur.lib = libOf(lz, c0.r, pw); }
    buildTabs(); renderNuc(); });
  $("#dx-excl").addEventListener("change", (e) => { showExcl = e.target.checked; renderNuc(); });
  $("#dx-full").addEventListener("change", (e) => { full = e.target.checked; renderNuc(); });
  $("#dx-copy").addEventListener("click", (e) => { try { navigator.clipboard.writeText($("#dx-cmd").textContent); e.currentTarget.textContent = T("dx_copied", "Copied"); } catch (err) {} });
  // hover (mouse) or tap (touch) shows the tooltip; clicking a measured point, or tapping it a second time, opens its EXFOR subentry
  let tipPin = null, lastPT = "mouse";
  function tipAt(x, y) {
    if (!P || !P.X) return null;
    let best = null, bd = (lastPT === "mouse" ? 14 : 22) ** 2;
    const th = P.S.th;
    if (th && th.y > 0 && (P.X(th.x) - x) ** 2 + (P.Y(th.y) - y) ** 2 < bd) { // the thermal diamond wins over the points under it
      const ex = th.subs.map(exforOf).filter(Boolean);
      let html = `<b>${T("dx_th", "measured thermal value (EXFOR)")}</b><br>σγ(0.0253 eV) = <b>${num(th.y, 4)} ± ${num(th.u, 2)} b</b><br>${T("dx_th_mean", "weighted mean of {n} EXFOR entries").replace("{n}", th.n)}${th.abs ? ` (${T("dx_th_abs", "absorption minus fission")})` : ""}<br><span class="dx-faint">EXFOR ${th.subs.map(esc).join(", ")}</span>`;
      if (ex.length) html += lastPT === "mouse" ? `<br><span class="dx-exhint">${T("dx_exfor_click", "click the point to open")} EXFOR ${ex[0].id} ↗</span>`
        : `<br><a class="dx-exhint" href="${ex[0].url}" target="_blank" rel="noopener">${T("dx_exfor_tap", "tap again, or here, to open")} EXFOR ${ex[0].id} ↗</a>`;
      return { html, url: ex.length ? ex[0].url : null, p: th }; }
    for (const p of P.shown) { if (!(p.y > 0)) continue; const d = (P.X(p.x) - x) ** 2 + (P.Y(p.y) - y) ** 2; if (d < bd) { bd = d; best = p; } }
    if (best) { const d = P.S.ds[best.ds] || [], ex = exforOf(d[0]);
      let html = `<b>${esc(d[1] || "EXFOR " + (ex ? ex.id : String(d[0]).split("/").filter(Boolean).pop() || ""))}</b> ${d[2] || ""}<br>${best.xhi > best.xlo * 1.02 ? `${fmtE(best.xlo)}–${fmtE(best.xhi)}` : fmtE(best.x)}: <b>${num(best.y)} ${P.S.unit}</b>${best.e ? ` ± ${num(best.e * 100, 2)} %` : ""}${best.kind === "mxw" ? ` · ${T("dx_mxw", "Maxwellian average")}` : ""}${best.st ? ` · ${T("dx_state", "state")} ${esc(best.st)}` : ""}<br><span class="dx-faint">${T("dx_cur", "curation")}: ${DEC[best.dec]}</span>`;
      if (ex) html += lastPT === "mouse" ? `<br><span class="dx-exhint">${T("dx_exfor_click", "click the point to open")} EXFOR ${ex.id} ↗</span>`
        : `<br><a class="dx-exhint" href="${ex.url}" target="_blank" rel="noopener">${T("dx_exfor_tap", "tap again, or here, to open")} EXFOR ${ex.id} ↗</a>`;
      return { html, url: ex && ex.url, p: best }; }
    const pws = pwOf(P.S), rrC = P.S.curves.find((c) => c.rr);
    if ((pws.length || rrC) && x > P.m.l && x < P.W - P.m.r) { // below 1 keV: INCOGNITA's own curve (if any), then the pointwise library values at this energy
      const xv = 10 ** (P.x0 + (x - P.m.l) / (P.W - P.m.l - P.m.r) * (P.x1 - P.x0));
      if (xv < PW_E) { const lines = pws.map((c) => [c, pwAt(c, xv)]).filter(([, v]) => v > 0).map(([c, v]) => `<span class="dx-faint"><i class="dx-sw" style="background:${c.col}"></i>${esc(c.short)}: ${num(v)} ${P.S.unit}</span>`);
        const ov = rrC ? pwAt(rrC, xv) : null;
        if (ov > 0) return { html: `${fmtE(xv)}<br>${rrSwatch(rrC)} <b>${num(ov)} ${P.S.unit}</b> <span class="dx-faint">· INCOGNITA, ${esc(rrC.short)}</span>${lines.length ? `<br><span class="dx-faint">${T("dx_pw_tip_rr", "evaluated libraries (comparators), pointwise 0 K")}:</span><br>${lines.join("<br>")}` : ""}`, url: null, p: null };
        if (lines.length) return { html: `${fmtE(xv)} <span class="dx-faint">· ${T("dx_pw_tip", "evaluated libraries (comparators), pointwise 0 K; no INCOGNITA curve below 1 keV")}</span><br>${lines.join("<br>")}`, url: null, p: null }; }
    }
    const c = P.S.curves[0];
    if (c && x > P.m.l && x < P.W - P.m.r) {
      const xv = 10 ** (P.x0 + (x - P.m.l) / (P.W - P.m.l - P.m.r) * (P.x1 - P.x0)); let j = -1, jd = Infinity; c.pts.forEach(([px], i) => { const dd = Math.abs(log10(px) - log10(xv)); if (dd < jd) { jd = dd; j = i; } });
      if (j >= 0 && jd < 0.2 && (!(pws.length || rrC) || xv >= PW_E * 0.98)) { const xe = c.pts[j][0], lines = [], anyLib = P.S.curves.some((cc) => cc.dash);
        for (const cc of P.S.curves) { if (cc.pw || cc.rr) continue; const q =cc.pts.find((p) => p[0] === xe); if (!q || !(q[1] > 0)) continue; const b = cc.b68 && cc.b68.find((r) => r[0] === xe);
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
      source: "INCOGNITA library v0.2 (October 2026): library/v0.2 in https://github.com/seth-michael-weaver/incognita, as shown on the Every nuclide page. Every curve is the prediction of the production engine scored on the Scoreboard (engine-20261022-3); none is fitted to this nuclide's measurements, except that an ANCHORED curve is scaled by one factor to a measured 30 keV MACS. The earlier v0.1 stays in library/v0.1.",
      page, generated: new Date().toISOString().slice(0, 10),
      engine: "The INCOGNITA engine is a port of TALYS-2 (A. J. Koning, S. Hilaire, S. Goriely, Eur. Phys. J. A 59 (2023) 131) and uses the TALYS nuclear-structure database.",
      license: "Predictions and data: CC-BY-4.0. Cite the project (CITATION.cff in the repository), TALYS (Eur. Phys. J. A 59 (2023) 131) and EXFOR (N. Otuka et al., Nucl. Data Sheets 120 (2014) 272).",
      measurements: "Measured points are from EXFOR (IAEA Nuclear Data Section) as curated in data/curation; each row carries its EXFOR dataset id (entry/subentry/pointer). (n,2n), (n,p) and (n,alpha) points are the benchmark rows in incognita/bench, with their EXFOR subentry.",
      units: "energy in eV (Maxwellian rows: kT in eV); capture cross sections in barns (b); (n,2n), (n,p), (n,alpha) and MACS in millibarns (mb)",
    };
    const J = { ...meta };
    if (d.tier != null) Object.assign(J, { tier: IDX.tiers[d.tier], in_validated_range: !!d.valid, value_source: d.src || null, uncertainty_kind: d.unc || null, resolved_resonances_up_to_ev: d.res ?? null, macs30_mb: d.macs30 ?? null, macs30_flag: d.flag || null });
    if (d.cap) J.capture = { unit: "b", energy_ev: grid, sigma_b: d.cap, unc68_log10: d.u68 || null, unc95_log10: d.u95 || null, note: "68 % and 95 % bands: sigma divided and multiplied by 10^unc" };
    if (d.mform) J.model_form = { flag: d.mform.kind, alt_value_30keV_b: d.mform.alt30 ?? null, alt_over_value_30keV: d.mform.ratio ?? null,
      note: { pe_kev: "keV capture depends on pre-equilibrium emission at low energies (on in this engine; TALYS starts it near 1 MeV); the 68 % and 95 % bands below 1 MeV are widened to contain the other choice",
        fists2: "keV capture depends on the engine's fission-transmission setting; the bands below 1 MeV are widened to contain the other choice",
        gg_deadend: "the value relies on the engine's fix of a missing gamma-decay width (the 'radiative dead end') that TALYS-based TENDL keeps; alt_value_30keV_b is without the fix; bands not widened" }[d.mform.kind] || null };
    if (d.ch) J.channels = { unit: "mb", energy_ev: grid, ...Object.fromEntries(Object.entries(d.ch).map(([k, v]) => [k === "na" ? "n_alpha" : k, v])), note: "production engine, the same runs as the capture curve" };
    if (d.npL) J.np_band = { unit: "mb", columns: ["energy_ev", "sigma_mb", "lo68_mb", "hi68_mb"], rows: d.npL, note: "(n,p) from the same engine runs at the benchmark energies (log-log interpolated from the engine grid), with the engine's 68 % band" };
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
    if (d.ch) for (const [k, v] of Object.entries(d.ch)) grid.forEach((x, i) => rows.push(["prediction", k === "na" ? "(n,alpha)" : `(${k[0]},${k.slice(1)})`, x, "", v[i], "mb"]));
    if (d.npL) d.npL.forEach((p) => rows.push(["prediction (benchmark energies, 68 % band)", "(n,p)", p[0], "", p[1], "mb", p[2] ?? "", p[3] ?? ""]));
    if (d.macs) kT.forEach((k, i) => { const f = d.macsU && d.macsU[i]; rows.push(["prediction", "MACS (kT)", k * 1e3, "", d.macs[i], "mb", f ? r4(d.macs[i] / f) : "", f ? r4(d.macs[i] * f) : ""]); });
    const mline = (kind, reac, p) => { const s = ds[p[4]] || {}; rows.push([kind, reac, p[0], p[1], p[2], "b", "", "", "", "", p[3] ?? "", s.exfor_id || "", s.author || "", s.year ?? "", DECW[p[5]] || p[5], p[6] || ""]); };
    if (d.meas) { d.meas.cap.forEach((p) => mline("measured (EXFOR)", "capture (n,g)", p)); d.meas.mxw.forEach((p) => mline("measured (EXFOR)", "Maxwellian average (kT)", p)); }
    if (d.thr) for (const [k, v] of Object.entries(d.thr)) v.forEach((p) => rows.push(["measured (EXFOR, benchmark)", k === "na" ? "(n,alpha)" : `(${k[0]},${k.slice(1)})`, p[0], "", p[1], "mb", "", "", "", "", "", p[2] || "", "", p[3] ?? "", "", ""]));
    const head = [`INCOGNITA · ${id} (Z=${Z}${A ? `, A=${A}` : ""})`, `Source: ${meta.source}`, `Page: ${page} (generated ${meta.generated})`, `Engine: ${meta.engine}`, `License: ${meta.license}`,
      `Measurements: ${meta.measurements}`, `Units: ${meta.units}. Bands: lo/hi columns are the 68 % and 95 % intervals where the library gives them.`]
      .concat(d.tier != null ? [`Tier: ${IDX.tiers[d.tier]}${d.valid ? "" : " (outside the validated range Z 26-83)"}${d.res ? `; resolved resonances up to ${d.res} eV (the curve is an average there)` : ""}`] : [])
      .concat(J.model_form ? [`Model-form flag: ${J.model_form.flag}: ${J.model_form.note}. Other choice at 30 keV: ${J.model_form.alt_value_30keV_b ?? "n/a"} b.`] : []);
    const csv = head.map((l) => "# " + l).join("\n") + "\n" + rows.map((r) => r.map(q).join(",")).join("\n") + "\n";
    return { name: `incognita_${id}_v0.2`, csv, json: JSON.stringify(J, null, 1) + "\n" };
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
    // other nuclides are fetched only when opened; a link like data.html#Fe-56 opens that one, otherwise U-238 opens by default
    const fromHash = () => { const [h, t] = decodeURIComponent(location.hash.slice(1)).split("/"), r0 = h && parseQ(h.replace(/-nat$/i, " nat")), t0 = tab;
      if (t in CH) tab = t;
      if (r0 && r0 !== sel) select(r0, true, true); else if (cur && tab !== t0) { buildTabs(); sweep(); } };
    fromHash(); window.addEventListener("hashchange", fromHash);
    if (!sel) { const u = byKey.get("92-238"); if (u) select(u, false, true); }
  }).catch((e) => { $("#dx-legend").textContent = T("dx_fail", "Could not load the data.") + " " + e; });
  let rt; window.addEventListener("resize", () => { clearTimeout(rt); rt = setTimeout(() => { if (!IDX) return; const c = { N: view.x0 + G.W / view.s / 2, Z: view.y0 + G.H / view.s / 2 }; layout(); view.x0 = c.N - G.W / view.s / 2; view.y0 = c.Z - G.H / view.s / 2; drawChart(); renderNuc(); }, 120); });
  window.matchMedia("(prefers-color-scheme: dark)").addEventListener("change", () => { readColors(); legend(); drawChart(); renderNuc(); });
})();
