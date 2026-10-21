/* Data explorer (data.html): a chart of nuclides coloured by how each is known, and for any nuclide the library's
 * predicted curves (with 68 / 95 % bands) beside every curated measurement. Data: data/index.json and data/z/<Z>.json,
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
    ["surface", "ink", "soft", "faint", "line", "grid", "curve", "meas", "alt", "none", "t0", "t1", "t2", "t3", "sel"].forEach((k) => (C[k] = cs.getPropertyValue("--dx-" + k).trim()));
    C.ramp = [1, 2, 3, 4, 5, 6, 7].map((i) => cs.getPropertyValue("--dx-r" + i).trim());
  }
  const rgba = (hex, a) => { const n = parseInt(hex.replace("#", ""), 16); return `rgba(${(n >> 16) & 255},${(n >> 8) & 255},${n & 255},${a})`; };
  const SANS = '"IBM Plex Sans", "Segoe UI", system-ui, sans-serif';

  function setupCanvas(cv, h) {
    const dpr = Math.min(2, window.devicePixelRatio || 1), w = cv.parentElement.clientWidth;
    cv.style.width = w + "px"; cv.style.height = h + "px"; cv.width = Math.round(w * dpr); cv.height = Math.round(h * dpr);
    const ctx = cv.getContext("2d"); ctx.setTransform(dpr, 0, 0, dpr, 0, 0); return { ctx, W: w, H: h };
  }

  // ---------- data ----------
  let IDX = null, rows = [], byKey = new Map(), sel = null, mode = "tier";
  const zcache = new Map();
  const loadZ = (Z) => zcache.get(Z) || zcache.set(Z, fetch(`data/z/${Z}.json`).then((r) => r.json())).get(Z);
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
    view = { s, x0: bounds.n0 - 2 - (W / s - (bounds.n1 - bounds.n0 + 4)) / 2, y0: bounds.z0 - 2 - (H / s - (bounds.z1 - bounds.z0 + 4)) / 2 };
  }
  const toX = (N) => (N - view.x0) * view.s, toY = (Z) => G.H - (Z - view.y0 + 1) * view.s;
  const fromXY = (x, y) => ({ N: Math.floor(x / view.s + view.x0), Z: Math.floor((G.H - y) / view.s + view.y0) });
  function drawChart() {
    const { ctx, W, H } = G, s = view.s, gap = s > 5 ? 1 : 0;
    ctx.fillStyle = C.surface; ctx.fillRect(0, 0, W, H);
    // magic numbers: faint lines where shells close
    ctx.strokeStyle = C.grid; ctx.lineWidth = 1;
    for (const m of MAGIC) { const x = toX(m) - 0.5 * gap, y = toY(m) + s; ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, H); ctx.stroke(); ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(W, y); ctx.stroke(); }
    for (const r of rows) {
      if (!r.A) continue;
      const x = toX(r.A - r.Z), y = toY(r.Z); if (x < -s || x > W || y < -s || y > H) continue;
      ctx.fillStyle = colorOf(r); ctx.fillRect(x, y, s - gap, s - gap);
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
    let lastX = -99; for (const m of MAGIC) { const x = toX(m) + 3; if (x > 20 && x < W - 40 && x - lastX > 44) { ctx.fillText(`N=${m}`, x, H - 10); lastX = x; } const y = toY(m) + s / 2; if (y > 14 && y < H - 20) ctx.fillText(`Z=${m}`, 6, y); }
    // selection and hover
    for (const [r, col, w] of [[hover, C.ink, 1.5], [sel, C.sel, 2.5]]) if (r && r.A) { ctx.strokeStyle = col; ctx.lineWidth = w; ctx.strokeRect(toX(r.A - r.Z) - 1, toY(r.Z) - 1, s + 1 - gap, s + 1 - gap); }
  }
  function legend() {
    const L = $("#dx-legend");
    const sw = (c, t) => `<span class="dx-key"><i style="background:${c}"></i>${t}</span>`;
    if (mode === "tier") L.innerHTML = [0, 1, 2, 3].map((i) => sw(C["t" + i], TIERS[i])).join("");
    else if (mode === "meas") L.innerHTML = sw(C.meas, T("dx_l_cap", "capture measured")) + sw(C.alt, T("dx_l_thr", "only (n,2n), (n,p) or (n,α) measured")) + sw(C.none, T("dx_l_none", "no measurement in this set"));
    else L.innerHTML = `<span class="dx-ramp"><span>0.1 mb</span><i style="background:linear-gradient(to right,${C.ramp.join(",")})"></i><span>10 b</span></span><span class="dx-key">${T("dx_l_macs", "predicted Maxwellian-averaged capture at kT = 30 keV (log scale)")}</span>` + sw(C.none, T("dx_l_nomacs", "no value"));
  }

  // pointer: pan, zoom, pinch, hover, click
  const pts = new Map(); let drag = null, moved = 0, pinch = null;
  cv.addEventListener("pointerdown", (e) => { cv.setPointerCapture(e.pointerId); pts.set(e.pointerId, { x: e.offsetX, y: e.offsetY }); moved = 0; drag = { x: e.offsetX, y: e.offsetY, v: { ...view } };
    if (pts.size === 2) { const [a, b] = [...pts.values()]; pinch = { d: Math.hypot(a.x - b.x, a.y - b.y), v: { ...view }, mx: (a.x + b.x) / 2, my: (a.y + b.y) / 2 }; } });
  cv.addEventListener("pointermove", (e) => {
    if (pts.has(e.pointerId)) pts.set(e.pointerId, { x: e.offsetX, y: e.offsetY });
    if (pinch && pts.size === 2) { const [a, b] = [...pts.values()], d = Math.hypot(a.x - b.x, a.y - b.y); zoomAt(pinch.mx, pinch.my, pinch.v.s * d / pinch.d, pinch.v); moved = 99; return; }
    if (drag && pts.size === 1) { const dx = e.offsetX - drag.x, dy = e.offsetY - drag.y; moved = Math.max(moved, Math.abs(dx) + Math.abs(dy)); view.x0 = drag.v.x0 - dx / view.s; view.y0 = drag.v.y0 + dy / view.s; drawChart(); return; }
    const { N, Z } = fromXY(e.offsetX, e.offsetY), r = byKey.get(Z + "-" + (N + Z)) || null;
    if (r !== hover) { hover = r; drawChart(); }
    if (r) { tip.hidden = false; tip.innerHTML = chartTip(r); place(tip, e.offsetX, e.offsetY, cv); } else tip.hidden = true;
  });
  const endPtr = (e) => { pts.delete(e.pointerId); if (pts.size < 2) pinch = null;
    if (pts.size === 0 && drag) { if (moved < 5 && e.type === "pointerup") { const { N, Z } = fromXY(e.offsetX, e.offsetY), r = byKey.get(Z + "-" + (N + Z)); if (r) select(r); } drag = null; } };
  cv.addEventListener("pointerup", endPtr); cv.addEventListener("pointercancel", endPtr);
  cv.addEventListener("pointerleave", () => { hover = null; tip.hidden = true; drawChart(); });
  cv.addEventListener("wheel", (e) => { e.preventDefault(); zoomAt(e.offsetX, e.offsetY, view.s * Math.exp(-e.deltaY * 0.0015)); }, { passive: false });
  function zoomAt(x, y, s, base = view) { s = clamp(s, 1.2, 60); const N = x / base.s + base.x0, Z = (G.H - y) / base.s + base.y0; view = { s, x0: N - x / s, y0: Z - (G.H - y) / s }; drawChart(); }
  document.querySelectorAll(".dx-zoom button").forEach((b) => b.addEventListener("click", () => { const z = +b.dataset.z; if (!z) { fit(); drawChart(); } else zoomAt(G.W / 2, G.H / 2, view.s * (z > 0 ? 1.6 : 1 / 1.6)); }));
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
        const sy = IDX.sym[r.Z].toLowerCase(), a = r.A ? String(r.A) : "nat";
        const keys = [sy + a, a + sy, sy];
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

  // ---------- one nuclide ----------
  let tab = "cap", cur = null, hl = null, P = null, showExcl = false, tableOpen = false;
  async function select(r, center) {
    sel = r; drawChart();
    if (center && r.A) { view.x0 = r.A - r.Z - G.W / view.s / 2; view.y0 = r.Z - G.H / view.s / 2; if (view.s < 14) zoomAt(G.W / 2, G.H / 2, 18); drawChart(); }
    history.replaceState(null, "", location.pathname + location.search + "#" + (r.A ? `${IDX.sym[r.Z]}-${r.A}` : `${IDX.sym[r.Z]}-nat`));
    const z = await loadZ(r.Z); if (sel !== r) return;
    cur = { r, d: z.nuc[r.A ? String(r.A) : "nat"] || {} };
    const tabs = ["cap"];
    for (const k of ["n2n", "np", "na"]) if ((cur.d.ch && cur.d.ch[k]) || (cur.d.thr && cur.d.thr[k])) tabs.push(k);
    if (cur.d.macs || (cur.d.meas && cur.d.meas.mxw.some((p) => p[0] >= 1000))) tabs.push("macs");
    if (!tabs.includes(tab)) tab = "cap";
    $("#dx-tabs").innerHTML = tabs.map((k) => `<button type="button" role="tab" data-tab="${k}" aria-selected="${k === tab}">${CH[k]}</button>`).join("");
    $("#dx-tabs").querySelectorAll("button").forEach((b) => b.addEventListener("click", () => { tab = b.dataset.tab; hl = null; $("#dx-tabs").querySelectorAll("button").forEach((x) => x.setAttribute("aria-selected", String(x === b))); renderNuc(); }));
    $("#dx-nuc").hidden = false; hl = null;
    $("#dx-name").textContent = nameOf(r.Z, r.A);
    const d = cur.d, f = [];
    if (d.tier != null) f.push(`<span class="dx-chip t${d.tier}">${TIERS[d.tier]}</span>`);
    f.push(`<span>Z ${r.Z} · N ${r.A ? r.A - r.Z : "–"}</span>`);
    if (d.macs30) f.push(`<span>MACS 30 keV ≈ <b>${num(d.macs30)} mb</b>${d.macsU ? ` (×/÷ ${num(d.macsU[6], 2)}, 68 %)` : ""}</span>`);
    if (d.meas) f.push(`<span>${d.meas.ds.length} ${T("dx_capsets", "capture datasets")}</span>`);
    if (d.tier != null && !d.valid) f.push(`<span class="dx-warn">${T("dx_outside", "outside the validated range (Z 26–83)")}</span>`);
    if (d.flag) f.push(`<span class="dx-warn">${T("dx_flag", "resolved resonances reach the MACS window: prefer a measured MACS")}</span>`);
    $("#dx-facts").innerHTML = f.join("");
    const nm = r.A ? `${IDX.sym[r.Z]}-${r.A}` : "";
    $("#dx-cmd").textContent = nm && d.cap ? `uv run python -m incognita.library show ${nm}\n\n# or from Python\nfrom incognita.library import capture_curve\ndf = capture_curve("${nm}")   # energy_ev, sigma_b, lo68_b, hi68_b, lo95_b, hi95_b, tier`
      : `# ${T("dx_nocurve", "no library curve for this entry; the measurements come from")} data/curation/inputs/exfor_cells.parquet`;
    renderNuc();
    if (center) $("#dx-nuc").scrollIntoView({ behavior: "smooth", block: "start" });
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
      if (d.res) out.note = { upto: d.res, text: T("dx_res", "resolved resonances: the curve is an average here") };
    } else if (tab === "macs") {
      out.xlab = "kT"; out.unit = "mb";
      if (d.macs) out.curves.push({ name: T("dx_pred", "prediction (library v0.1)"), col: C.curve, pts: IDX.kT_keV.map((k, i) => [k * 1e3, d.macs[i]]), b68: IDX.kT_keV.map((k, i) => (d.macsU && d.macsU[i] ? [k * 1e3, d.macs[i] / d.macsU[i], d.macs[i] * d.macsU[i]] : null)).filter(Boolean) });
      if (d.meas) { out.ds = d.meas.ds; for (const p of d.meas.mxw) if (p[0] >= 1000) out.points.push({ x: p[0], xlo: p[0], xhi: p[1], y: p[2] * 1000, e: p[3], ds: p[4], dec: p[5], st: p[6], kind: "mxw" }); }
    } else {
      out.unit = "mb";
      if (d.ch && d.ch[tab]) out.curves.push({ name: T("dx_recipe", "engine, no-data recipe"), col: C.curve, pts: grid.map((x, i) => [x, d.ch[tab][i]]) });
      if (tab === "np" && d.npL) out.curves.push({ name: T("dx_learned", "learned correction, 68 % band"), col: C.alt, pts: d.npL.map((p) => [p[0], p[1]]), b68: d.npL.filter((p) => p[2] != null).map((p) => [p[0], p[2], p[3]]) });
      const t = (d.thr && d.thr[tab]) || [], keys = [...new Set(t.map((p) => p[2]))];
      out.ds = keys.map((k) => [k, "", (t.find((p) => p[2] === k) || [])[3], ""]);
      for (const p of t) out.points.push({ x: p[0], y: p[1], e: null, ds: keys.indexOf(p[2]), dec: "k", kind: "thr" });
    }
    return out;
  }

  const pcv = $("#dx-plot"), ptip = $("#dx-ptip");
  function renderNuc() {
    if (!cur) return;
    const S = series(), shown = S.points.filter((p) => showExcl || p.dec !== "x");
    const W = pcv.parentElement.clientWidth, H = Math.round(clamp(W * 0.55, 300, 460));
    P = { ...setupCanvas(pcv, H), S, shown };
    const { ctx } = P, m = { l: 62, r: 16, t: 16, b: 44 };
    // ranges (log-log)
    const xs = [], ys = [];
    S.curves.forEach((c) => { c.pts.forEach(([x, y]) => { if (y > 0) { xs.push(x); ys.push(y); } }); (c.b68 || []).forEach(([x, lo, hi]) => { if (lo > 0) ys.push(lo); ys.push(hi); }); });
    shown.forEach((p) => { if (p.y > 0) { xs.push(p.xlo || p.x, p.xhi || p.x); ys.push(p.y); } });
    if (!xs.length) { P.ctx.fillStyle = C.surface; P.ctx.fillRect(0, 0, W, H); P.ctx.fillStyle = C.soft; P.ctx.font = `500 14px ${SANS}`; P.ctx.textAlign = "center"; P.ctx.fillText(T("dx_empty", "Nothing to show for this reaction."), W / 2, H / 2); finishNuc(S); return; }
    let x0 = log10(Math.min(...xs)), x1 = log10(Math.max(...xs)), y0 = log10(Math.min(...ys)), y1 = log10(Math.max(...ys));
    if (x1 - x0 < 1) { x0 -= 0.5; x1 += 0.5; } if (y1 - y0 < 1) { y0 -= 0.5; y1 += 0.5; }
    x0 -= 0.05 * (x1 - x0); x1 += 0.05 * (x1 - x0); y0 -= 0.08 * (y1 - y0); y1 += 0.08 * (y1 - y0);
    const X = (x) => m.l + (log10(x) - x0) / (x1 - x0) * (W - m.l - m.r), Y = (y) => H - m.b - (log10(y) - y0) / (y1 - y0) * (H - m.t - m.b);
    Object.assign(P, { X, Y, m, x0, x1, y0, y1, W, H });
    ctx.fillStyle = C.surface; ctx.fillRect(0, 0, W, H);
    // grid and axes (decades)
    ctx.font = `500 12px ${SANS}`; ctx.fillStyle = C.soft; ctx.strokeStyle = C.grid; ctx.lineWidth = 1;
    ctx.textAlign = "center"; ctx.textBaseline = "top";
    for (let k = Math.ceil(x0); k <= Math.floor(x1); k++) { const x = X(10 ** k); ctx.beginPath(); ctx.moveTo(x, m.t); ctx.lineTo(x, H - m.b); ctx.stroke(); ctx.fillText(decE(k), x, H - m.b + 6); }
    ctx.textAlign = "right"; ctx.textBaseline = "middle";
    for (let k = Math.ceil(y0); k <= Math.floor(y1); k++) { const y = Y(10 ** k); ctx.beginPath(); ctx.moveTo(m.l, y); ctx.lineTo(W - m.r, y); ctx.stroke(); ctx.fillText(decY(k, S.unit), m.l - 8, y); }
    ctx.textAlign = "left"; ctx.textBaseline = "alphabetic"; ctx.fillText(S.xlab + " →", m.l, H - 6);
    ctx.save(); ctx.beginPath(); ctx.rect(m.l, m.t, W - m.l - m.r, H - m.t - m.b); ctx.clip();
    if (S.note && S.note.upto > 10 ** x0) { const xe = Math.min(X(S.note.upto), W - m.r); ctx.fillStyle = rgba(C.soft, 0.07); ctx.fillRect(m.l, m.t, xe - m.l, H - m.t - m.b);
      ctx.fillStyle = C.soft; ctx.font = `500 12px ${SANS}`; ctx.textAlign = "left"; if (xe - m.l > 120) ctx.fillText(S.note.text, m.l + 8, m.t + 14); }
    // bands, then measured points, then the curves on top
    for (const c of S.curves) {
      for (const [b, a] of [[c.b95, 0.1], [c.b68, 0.2]]) if (b && b.length > 1) { ctx.fillStyle = rgba(c.col, a); ctx.beginPath(); b.forEach(([x, , hi], i) => (i ? ctx.lineTo(X(x), Y(hi)) : ctx.moveTo(X(x), Y(hi)))); for (let i = b.length - 1; i >= 0; i--) ctx.lineTo(X(b[i][0]), Y(Math.max(b[i][1], 10 ** (y0 - 1)))); ctx.closePath(); ctx.fill(); }
    }
    // measured points: error bars, energy-bin bars, dots (hollow = excluded, faint = down-weighted); 2px surface ring
    for (const p of shown) {
      if (!(p.y > 0)) continue;
      const dim = hl != null && p.ds !== hl, a = dim ? 0.15 : p.dec === "d" ? 0.55 : 1, x = X(p.x), y = Y(p.y);
      ctx.globalAlpha = a; ctx.strokeStyle = C.meas; ctx.lineWidth = 1.2;
      if (p.e > 0) { ctx.beginPath(); ctx.moveTo(x, Y(p.y * (1 + p.e))); ctx.lineTo(x, Y(Math.max(p.y * (1 - p.e), p.y * 0.05))); ctx.stroke(); }
      if (p.xhi > p.xlo * 1.02) { ctx.beginPath(); ctx.moveTo(X(p.xlo), y); ctx.lineTo(X(p.xhi), y); ctx.stroke(); }
      ctx.beginPath(); ctx.arc(x, y, p.kind === "mxw" ? 5 : 4, 0, Math.PI * 2);
      if (p.dec === "x") { ctx.strokeStyle = C.meas; ctx.lineWidth = 1.5; ctx.stroke(); } else { ctx.fillStyle = C.meas; ctx.fill(); ctx.strokeStyle = C.surface; ctx.lineWidth = 1.5; ctx.stroke(); }
    }
    ctx.globalAlpha = 1;
    for (const c of S.curves) for (const [w, col] of [[5, C.surface], [2.2, c.col]]) {
      ctx.strokeStyle = col; ctx.lineWidth = w; ctx.lineJoin = "round"; ctx.beginPath(); let on = false;
      for (const [x, y] of c.pts) { if (!(y > 0)) { on = false; continue; } on ? ctx.lineTo(X(x), Y(y)) : ctx.moveTo(X(x), Y(y)); on = true; }
      ctx.stroke();
    }
    ctx.restore();
    finishNuc(S);
  }
  function finishNuc(S) {
    const nPts = S.points.length, nEx = S.points.filter((p) => p.dec === "x").length;
    $("#dx-excl").parentElement.hidden = nEx === 0;
    const leg = S.curves.map((c) => `<span class="dx-key"><i class="ln" style="background:${c.col}"></i>${c.name}${c.b95 ? ` · ${T("dx_bands", "bands: 68 % and 95 %")}` : c.b68 && !c.name.includes("68") ? ` · ${T("dx_band68", "band: 68 %")}` : ""}</span>`);
    if (nPts) leg.push(`<span class="dx-key"><i class="dot" style="background:${C.meas}"></i>${T("dx_meas_pts", "measured")} (${nPts}${nEx ? `, ${nEx} ${T("dx_excl", "excluded")}` : ""})</span>`);
    $("#dx-plegend").innerHTML = leg.join("");
    pcv.setAttribute("aria-label", `${nameOf(cur.r.Z, cur.r.A)}, ${CH[tab]}: ${S.curves.length ? S.curves.map((c) => c.name).join(", ") : ""}${nPts ? `; ${nPts} ${T("dx_meas_pts", "measured")}` : ""}. ${T("dx_table_hint", "Use “Show as a table” for the values.")}`);
    // datasets
    const cnt = new Map(); S.points.forEach((p) => cnt.set(p.ds, (cnt.get(p.ds) || 0) + 1));
    const list = S.ds.map((d, i) => ({ d, i, n: cnt.get(i) || 0 })).filter((x) => x.n).sort((a, b) => (a.d[2] || 0) - (b.d[2] || 0));
    $("#dx-ds").innerHTML = list.length ? `<h3>${T("dx_ds_h", "Measurements")} <span class="dx-faint">(${list.length})</span></h3><ul>${list.map(({ d, i, n }) => {
      const sub = String(d[0]).split("/").filter(Boolean).pop() || d[0];
      return `<li data-ds="${i}"><span class="dx-who">${esc(d[1] || "EXFOR " + sub)}${d[2] ? ` <span class="dx-faint">${d[2]}</span>` : ""}</span><span class="dx-faint">${esc(d[3] || "")}</span><span class="dx-faint">${n} ${T("dx_pts", "pts")}</span>${/^[0-9A-Z]\d{7}$/.test(sub) ? `<a href="https://www-nds.iaea.org/exfor/servlet/X4sGetSubent?subID=${sub}" target="_blank" rel="noopener">EXFOR ${sub}</a>` : `<span class="dx-faint">${esc(d[0])}</span>`}</li>`; }).join("")}</ul>` : "";
    $("#dx-ds").querySelectorAll("li").forEach((li) => { li.addEventListener("mouseenter", () => { hl = +li.dataset.ds; renderNuc(); }); li.addEventListener("mouseleave", () => { hl = null; renderNuc(); }); li.addEventListener("focusin", () => { hl = +li.dataset.ds; renderNuc(); }); });
    if (tableOpen) table(S);
  }
  function table(S) {
    const rowsC = S.curves.flatMap((c) => c.pts.filter(([, y]) => y > 0).map(([x, y], i) => { const b = c.b68 && c.b68.find((q) => q[0] === x); return `<tr><td>${esc(c.name)}</td><td>${fmtE(x)}</td><td>${num(y)} ${S.unit}</td><td>${b ? `${num(b[1])}–${num(b[2])}` : ""}</td><td></td></tr>`; }));
    const rowsP = S.points.filter((p) => showExcl || p.dec !== "x").map((p) => { const d = S.ds[p.ds] || []; return `<tr><td>${esc(d[1] || d[0] || "")} ${d[2] || ""}</td><td>${p.xhi > p.xlo * 1.02 ? `${fmtE(p.xlo)}–${fmtE(p.xhi)}` : fmtE(p.x)}</td><td>${num(p.y)} ${S.unit}</td><td>${p.e ? "± " + num(p.e * 100, 2) + " %" : ""}</td><td>${DEC[p.dec] || ""}</td></tr>`; });
    $("#dx-table").innerHTML = `<table><thead><tr><th>${T("dx_th_src", "Source")}</th><th>${S.xlab}</th><th>${T("dx_th_val", "Value")}</th><th>${T("dx_th_unc", "Range / uncertainty")}</th><th>${T("dx_th_cur", "Curation")}</th></tr></thead><tbody>${rowsC.join("")}${rowsP.join("")}</tbody></table>`;
  }
  $("#dx-tbtn").addEventListener("click", (e) => { tableOpen = !tableOpen; e.currentTarget.setAttribute("aria-expanded", String(tableOpen)); $("#dx-table").hidden = !tableOpen; if (tableOpen) table(series()); });
  $("#dx-excl").addEventListener("change", (e) => { showExcl = e.target.checked; renderNuc(); });
  $("#dx-copy").addEventListener("click", (e) => { try { navigator.clipboard.writeText($("#dx-cmd").textContent); e.currentTarget.textContent = T("dx_copied", "Copied"); } catch (err) {} });
  pcv.addEventListener("pointermove", (e) => {
    if (!P || !P.X) return; const x = e.offsetX, y = e.offsetY;
    let best = null, bd = 14 * 14;
    for (const p of P.shown) { if (!(p.y > 0)) continue; const d = (P.X(p.x) - x) ** 2 + (P.Y(p.y) - y) ** 2; if (d < bd) { bd = d; best = p; } }
    if (best) { const d = P.S.ds[best.ds] || [];
      ptip.innerHTML = `<b>${esc(d[1] || "EXFOR " + (String(d[0]).split("/").filter(Boolean).pop() || ""))}</b> ${d[2] || ""}<br>${best.xhi > best.xlo * 1.02 ? `${fmtE(best.xlo)}–${fmtE(best.xhi)}` : fmtE(best.x)}: <b>${num(best.y)} ${P.S.unit}</b>${best.e ? ` ± ${num(best.e * 100, 2)} %` : ""}${best.kind === "mxw" ? ` · ${T("dx_mxw", "Maxwellian average")}` : ""}${best.st ? ` · ${T("dx_state", "state")} ${esc(best.st)}` : ""}<br><span class="dx-faint">${T("dx_cur", "curation")}: ${DEC[best.dec]}</span>`;
      ptip.hidden = false; place(ptip, x, y, pcv); return; }
    const c = P.S.curves[0];
    if (c && x > P.m.l && x < P.W - P.m.r) {
      const xv = 10 ** (P.x0 + (x - P.m.l) / (P.W - P.m.l - P.m.r) * (P.x1 - P.x0)); let j = -1, jd = Infinity; c.pts.forEach(([px], i) => { const dd = Math.abs(log10(px) - log10(xv)); if (dd < jd) { jd = dd; j = i; } });
      if (j >= 0 && jd < 0.2 && c.pts[j][1] > 0) { const b = c.b68 && c.b68.find((q) => q[0] === c.pts[j][0]);
        ptip.innerHTML = `${fmtE(c.pts[j][0])}: <b>${num(c.pts[j][1])} ${P.S.unit}</b>${b ? `<br><span class="dx-faint">68 %: ${num(b[1])}–${num(b[2])}</span>` : ""}`; ptip.hidden = false; place(ptip, x, y, pcv); return; } }
    ptip.hidden = true;
  });
  pcv.addEventListener("pointerleave", () => (ptip.hidden = true));

  // ---------- start ----------
  function layout() { G = setupCanvas(cv, Math.round(clamp(cv.parentElement.clientWidth * 0.62, 320, window.innerHeight * 0.72))); }
  fetch("data/index.json").then((r) => r.json()).then((idx) => {
    IDX = idx; readColors();
    const k = Object.fromEntries(idx.cols.map((c, i) => [c, i]));
    rows = idx.rows.map((a) => ({ Z: a[k.Z], A: a[k.A], tier: a[k.tier], macs: a[k.macs30_mb], u30: a[k.unc68_30], ncap: a[k.n_cap], nmxw: a[k.n_mxw], nds: a[k.n_ds], nn2n: a[k.n_n2n], nnp: a[k.n_np], nna: a[k.n_na] }));
    for (const Z of idx.natural) rows.push({ Z, A: 0, tier: -1, ncap: 1, nmxw: 0, nds: 0, nn2n: 0, nnp: 0, nna: 0 });
    rows.forEach((r) => byKey.set(r.Z + "-" + r.A, r));
    const real = rows.filter((r) => r.A); bounds = { n0: 0, n1: Math.max(...real.map((r) => r.A - r.Z)), z0: 0, z1: Math.max(...real.map((r) => r.Z)) };
    layout(); fit(); legend(); drawChart();
    const h = decodeURIComponent(location.hash.slice(1)); const r0 = (h && parseQ(h.replace(/-nat$/i, " nat"))) || byKey.get("79-197");
    if (r0) select(r0, !!h);
  }).catch((e) => { $("#dx-legend").textContent = T("dx_fail", "Could not load the data.") + " " + e; });
  let rt; window.addEventListener("resize", () => { clearTimeout(rt); rt = setTimeout(() => { if (!IDX) return; const c = { N: view.x0 + G.W / view.s / 2, Z: view.y0 + G.H / view.s / 2 }; layout(); view.x0 = c.N - G.W / view.s / 2; view.y0 = c.Z - G.H / view.s / 2; drawChart(); renderNuc(); }, 120); });
  window.matchMedia("(prefers-color-scheme: dark)").addEventListener("change", () => { readColors(); legend(); drawChart(); renderNuc(); });
})();
