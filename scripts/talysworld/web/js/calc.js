/* Engine calculator (calculator.html). Four dropdowns in one row: Target, Model, Energy points, Bins.
 * Public site (static): Target and Model change the plot. Default = the library curve (data/n/<Z>/<A>.json); Level density,
 * Gamma strength and Pre-equilibrium overlay precomputed engine runs (data/calc/, scripts/build_site_calc.py: one engine
 * run per curve on the library's 64-point grid, 40 bins) for the nuclides in the first dropdown group. Points and Bins are
 * greyed out ("live only"): they are never faked.
 * Local live mode: when the engine service runs on this machine (scripts/talysworld/server.py, http://localhost:8765,
 * never exposed publicly; looked for only on localhost, with ?live=1, or after it was once found) all four work. Any curve
 * not precomputed runs as ONE engine job per curve (whole grid + bins in one call, GRIDTOP pad, a warm worker), with a
 * spinner; "More" holds every other engine setting. Plain script, no build; colours from calc.css tokens. */
(function () {
  "use strict";
  const T = (k, en) => WT.ui(k, en), $ = (s) => document.querySelector(s);
  const esc = (s) => String(s ?? "").replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
  const clamp = (v, a, b) => Math.max(a, Math.min(b, v)), L10 = Math.log10;
  const LIVE = /^(localhost|127\.0\.0\.1)$/.test(location.hostname) && location.port === "8765" ? "" : "http://localhost:8765";
  if (WT.tl) { WT.applyStatic(document, "cx_title"); WT.keepLang(); }

  // ---------- formatting ----------
  const num = (v, p = 3) => (v == null || !isFinite(v) ? "–" : WT.dec(Math.abs(v) >= 1e5 || (Math.abs(v) < 1e-3 && v !== 0) ? v.toExponential(p - 1) : (+v.toPrecision(p)).toString()));
  const fmtE = (ev) => (ev >= 1e6 ? num(ev / 1e6) + " MeV" : ev >= 1e3 ? num(ev / 1e3) + " keV" : num(ev) + " eV");
  const SUP = { "-": "⁻", 0: "⁰", 1: "¹", 2: "²", 3: "³", 4: "⁴", 5: "⁵", 6: "⁶", 7: "⁷", 8: "⁸", 9: "⁹" };
  const pow10 = (k) => (k >= -2 && k <= 3 ? WT.dec(String(+(10 ** k).toPrecision(1))) : "10" + String(k).split("").map((c) => SUP[c]).join(""));

  // ---------- reactions, models, grids ----------
  const CHS = [["capture", T("cx_c_cap", "Capture"), "b"], ["elastic", T("cx_c_el", "Elastic"), "b"], ["inelastic", T("cx_c_inl", "Inelastic"), "b"],
    ["np", "(n,p)", "mb"], ["na", "(n,α)", "mb"], ["n2n", "(n,2n)", "mb"], ["fission", T("cx_c_fis", "Fission"), "b"], ["total", T("cx_c_tot", "Total"), "b"]];
  const CH = Object.fromEntries(CHS.map((c) => [c[0], c]));
  const MODELS = [
    { id: "", name: T("cx_m_def", "Default"), vars: [] },
    { id: "ld", name: T("cx_p_ld", "Level density"), vars: ["ld1", "ld2", "ld3", "ld4", "ld5", "ld6"], kw: "ldmodel 1–6" },
    { id: "gs", name: T("cx_p_gs", "Gamma strength"), vars: ["gs1", "gs2", "gs8", "gs9"], kw: "strength 1, 2, 8, 9" },
    { id: "pe", name: T("cx_p_pe", "Pre-equilibrium"), vars: ["pe0"], kw: "preequilibrium y / n" },
  ];
  const VKW = { ld1: ["ldmodel", "1"], ld2: ["ldmodel", "2"], ld3: ["ldmodel", "3"], ld4: ["ldmodel", "4"], ld5: ["ldmodel", "5"], ld6: ["ldmodel", "6"],
    gs1: ["strength", "1"], gs2: ["strength", "2"], gs8: ["strength", "8"], gs9: ["strength", "9"], pe0: ["preequilibrium", "n"] };
  const VL = {
    base: T("cx_v_base", "Library settings"),
    ld1: T("cx_v_ld1", "Constant temperature + Fermi gas"), ld2: T("cx_v_ld2", "Back-shifted Fermi gas"), ld3: T("cx_v_ld3", "Generalised superfluid"),
    ld4: T("cx_v_ld4", "Microscopic tables (Goriely)"), ld5: T("cx_v_ld5", "Microscopic tables (Hilaire–Goriely)"), ld6: T("cx_v_ld6", "Microscopic, temperature-dependent"),
    gs1: T("cx_v_gs1", "Kopecky–Uhl"), gs2: T("cx_v_gs2", "Brink–Axel"), gs8: T("cx_v_gs8", "Gogny HFB + QRPA"), gs9: T("cx_v_gs9", "SMLO"),
    pe0: T("cx_v_pe0", "Pre-equilibrium off"),
  };
  const PTS = [["16", "16"], ["32", "32"], ["64", "64 · " + T("cx_pt_lib", "library")], ["134", "134 · " + T("cx_pt_prod", "production")],
    ["64L", "64 " + T("cx_low", "+ below 1 keV")], ["134L", "134 " + T("cx_low", "+ below 1 keV")]];
  const BINS = ["20", "40", "60", "100"];

  // ---------- colours ----------
  const C = {};
  function readColors() {
    const cs = getComputedStyle($(".cx"));
    ["base", "meas", "grid", "axis"].forEach((k) => (C[k] = cs.getPropertyValue("--cx-" + k).trim()));
    C.s = [1, 2, 3, 4, 5, 6, 7].map((i) => cs.getPropertyValue("--cx-s" + i).trim());
    C.ink = cs.getPropertyValue("--ink").trim(); C.faint = cs.getPropertyValue("--faint").trim();
  }
  readColors();
  const SANS = '"IBM Plex Sans", "Segoe UI", system-ui, sans-serif';

  // ---------- state ----------
  let IDX = null, CI = null, byKey = new Map(), calcSet = new Set(), site = null, calc = null, loadTok = 0;
  const st = { key: null, model: "", pts: "64", bins: "40", ch: "capture", off: new Set() };
  const live = { meta: null, res: new Map(), busy: 0, t0: 0 };
  const cache = new Map();
  const getJ = (url) => { if (!cache.has(url)) cache.set(url, fetch(url).then((r) => (r.ok ? r.json() : null)).catch(() => { cache.delete(url); return null; })); return cache.get(url); };
  const nameOf = (k) => { const [Z, A] = k.split("-").map(Number); return `${IDX.sym[Z]}-${A}`; };
  const model = () => MODELS.find((m) => m.id === st.model) || MODELS[0];

  // ---------- dropdowns ----------
  const sel = $("#cx-sel"), msel = $("#cx-model"), psel = $("#cx-pts"), bsel = $("#cx-bins");
  msel.innerHTML = MODELS.map((m) => `<option value="${m.id}">${esc(m.name)}</option>`).join("");
  psel.innerHTML = PTS.map(([v, l]) => `<option value="${v}">${esc(l)}</option>`).join("");
  bsel.innerHTML = BINS.map((v) => `<option value="${v}">${v}${v === "40" ? " · TALYS" : ""}</option>`).join("");
  function fillTargets(rows) {
    const g = [`<optgroup label="${esc(T("cx_g_var", "With model variations"))}">${CI.nuclides.map((n) => `<option value="${n[0]}-${n[1]}">${esc(IDX.sym[n[0]])}-${n[1]}</option>`).join("")}</optgroup>`];
    let z = -1, buf = [];
    const flush = () => { if (buf.length) g.push(`<optgroup label="${esc(IDX.sym[z])} · Z ${z}">${buf.join("")}</optgroup>`); buf = []; };
    rows.forEach((r) => { if (r.Z !== z) { flush(); z = r.Z; } buf.push(`<option value="${r.k}">${esc(IDX.sym[r.Z])}-${r.A}</option>`); });
    flush(); sel.innerHTML = g.join("");
  }
  sel.addEventListener("change", () => select(sel.value));
  msel.addEventListener("change", () => { st.model = msel.value; st.off.clear(); update(); });
  psel.addEventListener("change", () => { st.pts = psel.value; update(); });
  bsel.addEventListener("change", () => { st.bins = bsel.value; update(); });
  const cbox = $("#cx-chips");
  cbox.innerHTML = CHS.map((c) => `<button type="button" data-c="${c[0]}" aria-pressed="false">${esc(c[1])}</button>`).join("");
  cbox.addEventListener("click", (e) => { const b = e.target.closest("button"); if (!b || b.disabled) return; st.ch = b.dataset.c; render(); });
  $("#cx-legend").addEventListener("click", (e) => { const b = e.target.closest("button"); if (!b) return; st.off.has(b.dataset.id) ? st.off.delete(b.dataset.id) : st.off.add(b.dataset.id); render(); });

  // ---------- which curves, and where they come from ----------
  const moreKw = () => { const o = {}; document.querySelectorAll("#cx-live-f select").forEach((s) => { if (s.value) o[s.dataset.k] = s.value; }); return o; };
  const isDefault = () => st.pts === "64" && st.bins === "40" && !Object.keys(moreKw()).length;
  // the static (precomputed or library) answer fits only the default grid, bins and settings
  const needLive = () => !!live.meta && (!isDefault() || (st.model && !calc));
  function jobs() {   // live jobs for the current view: [{id, kw}]
    const m = model(), more = moreKw(), out = [{ id: "base", kw: { ...more } }];
    m.vars.forEach((v) => out.push({ id: v, kw: { ...more, [VKW[v][0]]: VKW[v][1] } }));
    return out;
  }
  const jobKey = (j) => JSON.stringify([st.key, st.pts, st.bins, j.kw]);
  function series() {
    const out = [], m = model();
    if (needLive()) {
      jobs().forEach((j, i) => { const r = live.res.get(jobKey(j)); if (r && r.channels) out.push({ id: j.id, name: j.id === "base" ? VL.base : VL[j.id], col: j.id === "base" ? C.base : C.s[i - 1], w: j.id === "base" ? 2.4 : 1.9, mb: r.channels, grid: r.e_ev, base: j.id === "base", t: r.wall_s }); });
    } else if (!m.id || !calc) {
      if (site) {
        const mb = {}; if (site.cap) mb.capture = site.cap.map((v) => v * 1000);
        if (site.ch) for (const k of ["np", "na", "n2n"]) if (site.ch[k]) mb[k] = site.ch[k];
        out.push({ id: "lib", name: T("cx_v_lib", "INCOGNITA library v0.2.2"), col: C.s[0], w: 2.4, mb, grid: IDX.grid_ev });
      }
    } else {
      out.push({ id: "base", name: VL.base + (m.id === "pe" ? " · " + T("cx_v_pe1", "pre-equilibrium on") : ""), col: C.base, w: 2.4, mb: calc.v.base, grid: CI.grid_ev, base: true, t: calc.t && calc.t.base });
      m.vars.forEach((v, i) => { if (calc.v[v]) out.push({ id: v, name: VL[v], col: C.s[i], w: 1.9, mb: calc.v[v], grid: CI.grid_ev, same: calc.same.includes(v), t: calc.t && calc.t[v] }); });
    }
    return out;
  }
  function measured(ch) {
    if (!site) return [];
    if (ch === "capture" && site.meas) return site.meas.cap.filter((p) => p[5] !== "x" && p[2] > 0).map((p) => ({ x: Math.sqrt(p[0] * p[1]), y: p[2] * 1000, e: p[3] }));
    if (site.thr && site.thr[ch]) return site.thr[ch].filter((p) => p[1] > 0).map((p) => ({ x: p[0], y: p[1] }));
    return [];
  }

  // ---------- live runs: one engine job per curve ----------
  async function runLive() {
    if (!needLive() || !st.key) return;
    const todo = jobs().filter((j) => !live.res.has(jobKey(j)));
    if (!todo.length) return;
    const [Z, A] = st.key.split("-").map(Number), pts = parseInt(st.pts, 10), low = st.pts.endsWith("L");
    todo.forEach((j) => live.res.set(jobKey(j), { pending: true }));
    live.busy += todo.length; if (!live.t0) live.t0 = Date.now(); spin();
    await Promise.all(todo.map(async (j) => {
      const k = jobKey(j);
      try {
        const r = await fetch(LIVE + "/api/gridrun", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ z: Z, a: A, comp: "library", kw: j.kw, points: pts, low, bins: +st.bins }) }).then((x) => x.json());
        if (r.error) throw new Error(r.error);
        let s; for (;;) { await new Promise((ok) => setTimeout(ok, 700)); s = await fetch(`${LIVE}/api/run?run=${r.run}`).then((x) => x.json()); if (s.done) break; }
        const p = s.points[0]; if (p.err) throw new Error(p.err);
        live.res.set(k, p);
      } catch (e) { live.res.set(k, { err: String(e.message || e).slice(0, 160) }); }
      live.busy--; spin(); render();
    }));
    if (!live.busy) live.t0 = 0; spin();
  }
  let tick = null;
  function spin() {
    const on = live.busy > 0; $("#cx-spin").hidden = !on;
    if (on && !tick) tick = setInterval(spin, 1000); if (!on && tick) { clearInterval(tick); tick = null; }
    if (on) $("#cx-spin-t").textContent = `${live.busy} · ${Math.round((Date.now() - live.t0) / 1000)} s`;
  }

  // ---------- the plot ----------
  const pcv = $("#cx-plot"), ptip = $("#cx-ptip"); let P = null, hov = null;
  function draw() {
    if (!IDX) return;
    const dpr = Math.min(2, window.devicePixelRatio || 1), wrap = pcv.parentElement, W = wrap.clientWidth, H = wrap.clientHeight;
    pcv.width = Math.round(W * dpr); pcv.height = Math.round(H * dpr); pcv.style.width = W + "px"; pcv.style.height = H + "px";
    const ctx = pcv.getContext("2d"); ctx.setTransform(dpr, 0, 0, dpr, 0, 0); ctx.clearRect(0, 0, W, H);
    const ch = st.ch, unit = CH[ch][2], f = unit === "b" ? 1e-3 : 1, S = series().filter((s) => !st.off.has(s.id) && s.mb[ch]), M = measured(ch);
    const narrow = W < 500, m = { l: narrow ? 50 : 66, r: 16, t: 16, b: 30 }, X0 = m.l, X1 = W - m.r, Y0 = m.t, Y1 = H - m.b;
    const val = (s, j) => { const v = s.mb[ch][j]; return v > 0 ? v * f : null; };
    // energy range: from the lowest grid point, or where the reaction opens (above 1e-6 of its peak), to 20 MeV
    let peak = 0, first = Infinity, gmin = Infinity;
    S.forEach((s) => { gmin = Math.min(gmin, s.grid[0]); s.mb[ch].forEach((v) => (peak = Math.max(peak, v))); });
    S.forEach((s) => { const j = s.mb[ch].findIndex((v) => v > peak * 1e-6); if (j >= 0) first = Math.min(first, s.grid[Math.max(0, j - 1)]); });
    const floor = isFinite(gmin) ? Math.min(1e3, gmin) : 1e3;
    let xlo = Math.max(floor, isFinite(first) ? first : floor); const xhi = 2e7;
    M.forEach((p) => { if (p.x >= floor && p.x <= xhi) xlo = Math.min(xlo, p.x); });
    let ylo = Infinity, yhi = -Infinity;
    S.forEach((s) => s.grid.forEach((x, j) => { const v = val(s, j); if (v != null && x >= xlo * .999) { ylo = Math.min(ylo, v); yhi = Math.max(yhi, v); } }));
    M.forEach((p) => { if (p.x >= xlo && p.x <= xhi) { ylo = Math.min(ylo, p.y * f); yhi = Math.max(yhi, p.y * f); } });
    P = null;
    if (!isFinite(ylo)) { ctx.font = `500 14px ${SANS}`; ctx.fillStyle = C.faint; ctx.textAlign = "center"; ctx.fillText(live.busy ? "…" : site || calc ? T("cx_none", "No curve for this reaction here") : "…", W / 2, H / 2); return; }
    ylo = Math.max(ylo, yhi * 1e-5); ylo = 10 ** Math.floor(L10(ylo)); yhi = 10 ** Math.ceil(L10(yhi) + 1e-9); if (yhi / ylo < 100) { ylo /= 3; yhi *= 3; }
    const X = (x) => X0 + (L10(x) - L10(xlo)) / (L10(xhi) - L10(xlo)) * (X1 - X0), Y = (y) => Y1 - (L10(y) - L10(ylo)) / (L10(yhi) - L10(ylo)) * (Y1 - Y0);
    P = { X0, X1, Y0, Y1, xlo, xhi, S, val, unit, ch };
    ctx.font = `500 12px ${SANS}`; ctx.lineWidth = 1;
    const kx0 = Math.ceil(L10(xlo) - 1e-9), kx1 = Math.floor(L10(xhi) + 1e-9), xev = kx1 - kx0 > 6 ? 2 : 1;
    for (let k = kx0; k <= kx1; k++) {
      const x = X(10 ** k); ctx.strokeStyle = C.grid; ctx.beginPath(); ctx.moveTo(x, Y0); ctx.lineTo(x, Y1); ctx.stroke();
      if ((k - kx1) % xev === 0) { ctx.fillStyle = C.axis; ctx.textAlign = "center"; ctx.textBaseline = "top"; ctx.fillText(fmtE(10 ** k), x, Y1 + 8); }
    }
    const k0 = Math.round(L10(ylo)), k1 = Math.round(L10(yhi)), every = k1 - k0 > 7 ? 2 : 1;
    ctx.textAlign = "right"; ctx.textBaseline = "middle";
    for (let k = k0; k <= k1; k++) { const y = Y(10 ** k); ctx.strokeStyle = C.grid; ctx.beginPath(); ctx.moveTo(X0, y); ctx.lineTo(X1, y); ctx.stroke(); if ((k - k0) % every === 0) { ctx.fillStyle = C.axis; ctx.fillText(pow10(k) + " " + unit, X0 - 8, y); } }
    ctx.save(); ctx.beginPath(); ctx.rect(X0, Y0 - 2, X1 - X0, Y1 - Y0 + 4); ctx.clip();
    ctx.strokeStyle = C.meas; ctx.lineWidth = 1.4; ctx.globalAlpha = .8;
    for (const p of M) {
      if (p.x < xlo || p.x > xhi) continue; const x = X(p.x), y = Y(p.y * f);
      if (p.e > 0 && p.e < 1) { ctx.beginPath(); ctx.moveTo(x, Y(p.y * f * (1 + p.e))); ctx.lineTo(x, Y(Math.max(p.y * f * (1 - p.e), ylo))); ctx.stroke(); }
      ctx.beginPath(); ctx.arc(x, y, 3, 0, 7); ctx.stroke();
    }
    ctx.globalAlpha = 1;
    [...S].sort((a, b) => (a.base ? 1 : 0) - (b.base ? 1 : 0)).forEach((s) => {   // library settings on top
      ctx.strokeStyle = s.col; ctx.lineWidth = s.w; ctx.lineJoin = "round";
      ctx.beginPath(); let on = false;
      s.grid.forEach((x, j) => { const v = val(s, j); if (v == null || x < xlo * .999) { on = false; return; } const px = X(x), py = Y(clamp(v, ylo * .5, yhi * 2)); on ? ctx.lineTo(px, py) : ctx.moveTo(px, py); on = true; });
      ctx.stroke();
      if (s.grid.length <= 40) { ctx.fillStyle = s.col; s.grid.forEach((x, j) => { const v = val(s, j); if (v != null && x >= xlo * .999) { ctx.beginPath(); ctx.arc(X(x), Y(v), 2.2, 0, 7); ctx.fill(); } }); }
    });
    if (hov) {
      const x = X(hov); ctx.strokeStyle = C.axis; ctx.lineWidth = 1; ctx.setLineDash([3, 3]); ctx.beginPath(); ctx.moveTo(x, Y0); ctx.lineTo(x, Y1); ctx.stroke(); ctx.setLineDash([]);
      S.forEach((s) => { const j = s.grid.findIndex((g) => Math.abs(g / hov - 1) < 1e-6), v = j >= 0 ? val(s, j) : null; if (v == null) return; ctx.fillStyle = s.col; ctx.beginPath(); ctx.arc(x, Y(v), 4, 0, 7); ctx.fill(); });
    }
    ctx.restore();
  }
  pcv.addEventListener("pointermove", (e) => {
    if (!P) return; const b = pcv.getBoundingClientRect(), x = e.clientX - b.left, y = e.clientY - b.top;
    if (x < P.X0 - 10 || x > P.X1 + 10) { if (hov) { hov = null; ptip.hidden = true; draw(); } return; }
    const xs = [...new Set(P.S.flatMap((s) => s.grid))].filter((g) => g >= P.xlo * .999 && g <= P.xhi); if (!xs.length) return;
    const lx = L10(P.xlo) + (x - P.X0) / (P.X1 - P.X0) * (L10(P.xhi) - L10(P.xlo));
    hov = xs.reduce((a, g) => (Math.abs(L10(g) - lx) < Math.abs(L10(a) - lx) ? g : a), xs[0]); draw();
    const tr = P.S.map((s) => { const j = s.grid.findIndex((g) => Math.abs(g / hov - 1) < 1e-6), v = j >= 0 ? P.val(s, j) : null;
      return v == null ? "" : `<tr><td><i style="background:${s.col}"></i></td><td>${esc(s.name)}</td><td class="v">${num(v, 4)} ${P.unit}</td></tr>`; }).join("");
    ptip.innerHTML = `<b>${esc(CH[P.ch][1])} · ${fmtE(hov)}</b><table>${tr}</table>`; ptip.hidden = false;
    const w = ptip.offsetWidth, h = ptip.offsetHeight; ptip.style.left = (x + 18 + w > b.width ? Math.max(4, x - w - 18) : x + 18) + "px"; ptip.style.top = clamp(y - h / 2, 4, b.height - h - 4) + "px";
  });
  pcv.addEventListener("pointerleave", () => { hov = null; ptip.hidden = true; draw(); });

  // ---------- everything around the plot ----------
  function update() { render(); runLive(); }
  function render() {
    if (!IDX) return;
    msel.value = st.model; psel.value = st.pts; bsel.value = st.bins;
    // public page: a model needs the precomputed runs; live: any target
    [...msel.options].forEach((o) => (o.disabled = !!o.value && !calc && !live.meta));
    if (st.model && !calc && !live.meta) { st.model = ""; msel.value = ""; }
    const S = series(), avail = new Set(S.flatMap((s) => Object.keys(s.mb).filter((k) => s.mb[k] && s.mb[k].some((v) => v > 0))));
    if (site && site.thr) Object.keys(site.thr).forEach((k) => avail.add(k));
    if (S.length) avail.add("capture");   // while live curves are still running, keep the chosen reaction
    if (avail.size && !avail.has(st.ch) && !live.busy) st.ch = avail.has("capture") ? "capture" : CHS.find((c) => avail.has(c[0]))[0];
    cbox.querySelectorAll("button").forEach((b) => { b.disabled = avail.size > 0 && !avail.has(b.dataset.c) && !(live.busy && b.dataset.c === st.ch); b.setAttribute("aria-pressed", String(b.dataset.c === st.ch)); });
    const nM = measured(st.ch).length, errs = needLive() ? jobs().map((j) => live.res.get(jobKey(j))).filter((r) => r && r.err) : [];
    $("#cx-legend").innerHTML = S.filter((s) => s.mb[st.ch]).map((s) => `<button type="button" data-id="${s.id}" aria-pressed="${!st.off.has(s.id)}"><i style="background:${s.col}"></i>${esc(s.name)}${s.same ? ` <small>= ${esc(VL.base)}</small>` : ""}</button>`).join("")
      + (nM ? `<span><i class="dot" style="border-color:${C.meas}"></i>${T("cx_meas_n", "Measured (EXFOR)")} · ${nM}</span>` : "")
      + (errs.length ? `<span style="color:var(--proton)">${esc(errs[0].err)}</span>` : "");
    // N points · bins B · ~T s (T: the engine's own time per curve; ~ an estimate where none was measured)
    const n = S.length ? S[0].grid.length : parseInt(st.pts, 10) + (st.pts.endsWith("L") ? 15 : 0), ts = S.map((s) => s.t).filter((t) => t > 0);
    const tt = ts.length ? `${num(ts.reduce((a, b) => a + b, 0) / ts.length, 2)} s` : `~${Math.round(6 + 0.07 * n * (+st.bins / 40))} s`;
    $("#cx-info").textContent = `${n} ${T("cx_pts_u", "points")} · bins ${needLive() || S.some((s) => s.base) ? st.bins : 40} · ${tt}${S.length > 1 ? " / " + T("cx_curve", "curve") : ""}`;
    const m = model();
    $("#cx-note").innerHTML = (m.kw ? `<code>${esc(m.kw)}</code> · ` : "") + esc(T("cx_note", "Precomputed variants for {n} nuclides; library curves for all; live runs need the local engine.").replace("{n}", CI.nuclides.length));
    const url = new URL(location.href); url.searchParams.set("n", nameOf(st.key)); st.model ? url.searchParams.set("p", st.model) : url.searchParams.delete("p"); url.searchParams.set("ch", st.ch);
    for (const [k, v, d] of [["pts", st.pts, "64"], ["bins", st.bins, "40"]]) v !== d ? url.searchParams.set(k, v) : url.searchParams.delete(k);
    history.replaceState(null, "", url);
    draw();
  }
  $("#cx-csv").addEventListener("click", () => {
    if (!st.key) return; const S = series().filter((s) => !st.off.has(s.id) && s.mb[st.ch]), nm = nameOf(st.key), m = model();
    const es = [...new Set(S.flatMap((s) => s.grid))].sort((a, b) => a - b);
    const lines = [`# INCOGNITA engine calculator: ${nm}, ${st.ch}, cross sections in mb${m.kw ? "; " + m.kw : ""}; ${location.origin}${location.pathname}`,
      ["energy_eV", ...S.map((s) => `"${s.name.replace(/"/g, "'")}"`)].join(",")];
    es.forEach((e) => lines.push([e, ...S.map((s) => { const j = s.grid.findIndex((g) => Math.abs(g / e - 1) < 1e-6); return j >= 0 ? s.mb[st.ch][j] ?? "" : ""; })].join(",")));
    const a = document.createElement("a"); a.href = URL.createObjectURL(new Blob([lines.join("\n") + "\n"], { type: "text/csv" }));
    a.download = `incognita_${nm}_${st.ch}${m.id ? "_" + m.id : ""}.csv`; a.click(); setTimeout(() => URL.revokeObjectURL(a.href), 2000);
  });

  async function select(k) {
    if (!byKey.has(k)) return; st.key = k; sel.value = k; const tok = ++loadTok, [Z, A] = k.split("-");
    const [s, c] = await Promise.all([getJ(`data/n/${Z}/${A}.json`), calcSet.has(k) ? getJ(`data/calc/${Z}/${A}.json`) : null]);
    if (tok !== loadTok) return; site = s; calc = c; update();
  }

  // ---------- local live engine ----------
  async function probe() {
    let on = /^(localhost|127\.0\.0\.1)$/.test(location.hostname) || /[?&]live=1/.test(location.search);
    try { on = on || localStorage.getItem("cx_live") === "1"; } catch (e) {}
    if (!on) return;
    try {
      const ac = new AbortController(), t = setTimeout(() => ac.abort(), 2500);
      const m = await fetch(LIVE + "/api/meta", { signal: ac.signal }).then((r) => r.json()); clearTimeout(t);
      if (!m.gridrun) return;
      live.meta = m; try { localStorage.setItem("cx_live", "1"); } catch (e) {}
      document.querySelector(".cx").classList.add("cx-live-on"); psel.disabled = false; bsel.disabled = false;
      const u = new URLSearchParams(location.search);   // ?pts=32&bins=60 (live only)
      if (PTS.some((p) => p[0] === u.get("pts"))) st.pts = u.get("pts"); if (BINS.includes(u.get("bins"))) st.bins = u.get("bins");
      $("#cx-live-f").innerHTML = Object.entries(m.keywords).map(([k, d]) => `<label>${esc(d.label)}<select data-k="${k}">${d.options.map((o) => `<option value="${esc(o[0])}">${esc(o[1])}</option>`).join("")}</select></label>`).join("");
      $("#cx-live-f").addEventListener("change", update);
      $("#cx-live").hidden = false; update();
    } catch (e) { /* no local engine: the page stays static */ }
  }

  // ---------- start ----------
  new ResizeObserver(() => draw()).observe($("#cx-plotwrap"));
  window.matchMedia("(prefers-color-scheme: dark)").addEventListener("change", () => { readColors(); render(); });
  Promise.all([fetch("data/index.json").then((r) => r.json()), fetch("data/calc/index.json").then((r) => (r.ok ? r.json() : null)).catch(() => null)]).then(([idx, ci]) => {
    IDX = idx; CI = ci || { nuclides: [], grid_ev: [] };
    const ix = Object.fromEntries(idx.cols.map((c, i) => [c, i]));
    const rows = idx.rows.map((r) => ({ Z: r[ix.Z], A: r[ix.A] })).filter((r) => r.A > 0).sort((a, b) => a.Z - b.Z || a.A - b.A);
    rows.forEach((r) => { r.k = r.Z + "-" + r.A; byKey.set(r.k, r); });
    CI.nuclides.forEach((n) => calcSet.add(n[0] + "-" + n[1]));
    fillTargets(rows);
    const u = new URLSearchParams(location.search), mm = /^([A-Za-z]{1,2})-?(\d{1,3})$/.exec((u.get("n") || "").trim());
    const z = mm ? IDX.sym.findIndex((s) => s.toLowerCase() === mm[1].toLowerCase()) : -1, want = z > 0 ? z + "-" + mm[2] : "";
    if (MODELS.some((m) => m.id && m.id === u.get("p"))) st.model = u.get("p");
    if (CH[u.get("ch")]) st.ch = u.get("ch");
    select(byKey.has(want) ? want : "26-56");
    probe();
  });
})();
