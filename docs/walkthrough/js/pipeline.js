/* Pipeline page (pipeline.html): the reactor-data pipeline as a lit diagram (7 stages and the judges' loop back to the fit);
 * picking a stage shows its text and a live drawing below. Plain script, no build step, own canvas code (kit.js is not loaded).
 * Drawings redraw on input only; requestAnimationFrame runs only for short transitions and while a fit is running.
 * Numbers on the page: the drawings marked "illustration" are simulated; every other number is from library/res-v0.1/README.md
 * or the research reports RESINTEG, PU239DIAG, JUDGEFIX and DOPPLER (27 October 2026). */
(function () {
  "use strict";
  const WT = (window.WT = window.WT || {});
  const T = (k, en) => (WT.ui ? WT.ui(k, en) : en);

  // ===================================================================================================================
  // physics (pure functions; also loaded by a node check, so nothing here touches the DOM)
  // ===================================================================================================================
  const P = {};
  P.rng = (seed) => { let s = seed >>> 0 || 1; return () => ((s = (s * 16807) % 2147483647) / 2147483647); };
  P.gauss = (r) => { const u = Math.max(1e-12, r()), v = r(); return Math.sqrt(-2 * Math.log(u)) * Math.cos(2 * Math.PI * v); };
  // Gaussian kernel with standard deviation sd on a grid of step dE
  P.kernel = (sd, dE) => { const m = Math.max(1, Math.ceil((4 * sd) / dE)), k = new Float64Array(2 * m + 1); for (let i = -m; i <= m; i++) k[i + m] = Math.exp(-0.5 * ((i * dE) / sd) ** 2); return k; };
  // convolution, renormalised at the edges
  P.conv = (a, k) => {
    const n = a.length, m = (k.length - 1) / 2, out = new Float64Array(n);
    for (let i = 0; i < n; i++) { let s = 0, w = 0; const j0 = Math.max(-m, -i), j1 = Math.min(m, n - 1 - i); for (let j = j0; j <= j1; j++) { const kk = k[j + m]; s += kk * a[i + j]; w += kk; } out[i] = s / w; }
    return out;
  };

  // --- stage 1-2 illustration: one resonance seen by two simulated transmission experiments (thin and thick sample) ---
  const TRUE = { E0: 10.0, G: 0.06, S0: 4000, SP: 10 };       // eV, eV, b, b
  const EXPS = [{ key: "thin", n: 2e-4 }, { key: "thick", n: 2e-3 }]; // areal density, atoms per barn
  const RES_SD = 0.08 / 2.3548, BKG = 0.03, NORM = 0.97, NOISE = 0.012;
  const FLO = 9.3, FDE = 0.002, NF = 701, ELO = 9.6, EHI = 10.4, ND = 81;
  const ED = Array.from({ length: ND }, (_, i) => ELO + ((EHI - ELO) * i) / (ND - 1));
  const KER = P.kernel(RES_SD, FDE);
  P.TRUE = TRUE; P.EXPS = EXPS; P.ED = ED; P.ELO = ELO; P.EHI = EHI;
  P.sig = (E, p) => p.SP + p.S0 / (1 + ((E - p.E0) / (p.G / 2)) ** 2);
  // what one experiment records at the data energies (fx: which experiment effects are on)
  P.recorded = (p, n, fx, Es) => {
    const T0 = new Float64Array(NF); for (let i = 0; i < NF; i++) T0[i] = Math.exp(-n * P.sig(FLO + i * FDE, p));
    const Tc = fx.res ? P.conv(T0, KER) : T0;
    return (Es || ED).map((E) => { const x = (E - FLO) / FDE, i = Math.min(NF - 2, Math.max(0, Math.floor(x))), f = x - i; return (fx.norm ? NORM : 1) * (Tc[i] * (1 - f) + Tc[i + 1] * f) + (fx.bkg ? BKG : 0); });
  };
  const NOISES = EXPS.map((_, k) => { const r = P.rng(4242 + 97 * k); return ED.map(() => NOISE * P.gauss(r)); });
  P.data = (fx) => EXPS.map((x, k) => P.recorded(TRUE, x.n, fx, ED).map((v, i) => v + NOISES[k][i]));
  P.ALL = { res: true, bkg: true, norm: true }; P.NONE = { res: false, bkg: false, norm: false };
  P.chi2 = (p, data, modelOn) => { let s = 0, n = 0; EXPS.forEach((x, k) => { const m = P.recorded(p, x.n, modelOn ? P.ALL : P.NONE, ED); m.forEach((v, i) => { s += ((data[k][i] - v) / NOISE) ** 2; n++; }); }); return s / n; };
  P.toP = (x) => ({ E0: x[0], G: Math.exp(x[1]), S0: Math.exp(x[2]), SP: TRUE.SP });
  P.toX = (p) => [p.E0, Math.log(p.G), Math.log(p.S0)];
  // Nelder-Mead, one iteration per call (so a fit can run a few iterations per frame)
  P.nmInit = (f, x0, d) => { const S = [x0.slice()]; x0.forEach((_, i) => { const x = x0.slice(); x[i] += d[i]; S.push(x); }); const st = { f, S, F: S.map(f), it: 0 }; P.nmBest(st); return st; };
  P.nmBest = (st) => { let b = 0; st.F.forEach((v, i) => { if (v < st.F[b]) b = i; }); st.best = st.S[b]; st.fbest = st.F[b]; st.spread = Math.max(...st.F) - Math.min(...st.F); };
  P.nmStep = (st) => {
    const f = st.f, idx = st.S.map((_, i) => i).sort((a, b) => st.F[a] - st.F[b]);
    const s = idx.map((i) => st.S[i]), v = idx.map((i) => st.F[i]), n = s[0].length;
    const c = new Array(n).fill(0); for (let i = 0; i < n; i++) for (let j = 0; j < n; j++) c[j] += s[i][j] / n;
    const pt = (t) => c.map((cj, j) => cj + t * (s[n][j] - cj));
    const xr = pt(-1), fr = f(xr);
    if (fr < v[0]) { const xe = pt(-2), fe = f(xe); if (fe < fr) { s[n] = xe; v[n] = fe; } else { s[n] = xr; v[n] = fr; } }
    else if (fr < v[n - 1]) { s[n] = xr; v[n] = fr; }
    else {
      const xc = fr < v[n] ? pt(-0.5) : pt(0.5), fc = f(xc);
      if (fc < Math.min(fr, v[n])) { s[n] = xc; v[n] = fc; }
      else for (let i = 1; i <= n; i++) { s[i] = s[i].map((x, j) => s[0][j] + 0.5 * (x - s[0][j])); v[i] = f(s[i]); }
    }
    st.S = s; st.F = v; st.it++; P.nmBest(st);
  };

  // --- stage 4 illustration: Doppler broadening of one narrow resonance (Gaussian / psi-function approximation) ---
  const DOP = { E0: 6.67, G: 0.025, A: 238, k: 8.617333e-5, half: 0.6, dE: 0.0008 };
  DOP.n = Math.round((2 * DOP.half) / DOP.dE) + 1;
  DOP.E = Array.from({ length: DOP.n }, (_, i) => DOP.E0 - DOP.half + i * DOP.dE);
  DOP.s0 = Float64Array.from(DOP.E, (E) => 1 / (1 + ((E - DOP.E0) / (DOP.G / 2)) ** 2));
  P.DOP = DOP;
  P.dopWidth = (TK) => Math.sqrt((4 * DOP.k * TK * DOP.E0) / DOP.A); // Doppler width Δ (eV)
  P.doppler = (TK) => (TK < 0.5 ? DOP.s0 : P.conv(DOP.s0, P.kernel(P.dopWidth(TK) / Math.SQRT2, DOP.dE)));
  P.fwhm = (s) => { let m = 0; for (let i = 0; i < s.length; i++) if (s[i] > s[m]) m = i; const h = s[m] / 2; let a = m, b = m; while (a > 0 && s[a] > h) a--; while (b < s.length - 1 && s[b] > h) b++; return (b - a) * DOP.dE; };

  WT.pipePhys = P;
  if (typeof document === "undefined" || !document.getElementById("pl-flow")) return;

  // ===================================================================================================================
  // drawing helpers
  // ===================================================================================================================
  const C = { ink: "#e8ecf3", soft: "#b3bccc", faint: "#8e98ab", grid: "rgba(150,170,220,.11)", axis: "rgba(150,170,220,.34)", panel: "rgba(150,170,230,.22)",
    meas: "#ff9b55", fit: "#7c9cff", file: "#b392ff", proc: "#f5c04d", lib: "#5fb0ff", bench: "#3fd3a8", judge: "#ff7e72", thin: "#5fb0ff", thick: "#ff9b55",
    win: "#3fd3a8", loss: "#ff8b80", nc: "#9aa7c7", accent: "#7c9cff" };
  const SANS = '"IBM Plex Sans", "Segoe UI", system-ui, sans-serif', MONO = '"IBM Plex Mono", ui-monospace, Menlo, monospace';
  const RM = window.matchMedia && matchMedia("(prefers-reduced-motion: reduce)").matches;
  const clamp = (v, a, b) => Math.max(a, Math.min(b, v));
  const rgba = (hex, a) => { const n = parseInt(hex.slice(1), 16); return `rgba(${(n >> 16) & 255},${(n >> 8) & 255},${n & 255},${a})`; };
  const esc = (s) => String(s).replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" })[c]);
  const fmt = (v, d) => (WT.dec ? WT.dec(v.toFixed(d)) : v.toFixed(d));
  const sgn = (v) => (v > 0 ? "+" : v < 0 ? "−" : "") + Math.abs(v).toLocaleString("en-US").replace(/,/g, " ");

  function surf(cv) {
    const ctx = cv.getContext("2d");
    const s = { cv, ctx, W: 0, H: 0, size(w, h) { const d = Math.min(2, window.devicePixelRatio || 1); cv.width = Math.round(w * d); cv.height = Math.round(h * d); cv.style.height = h + "px"; ctx.setTransform(d, 0, 0, d, 0, 0); s.W = w; s.H = h; } };
    return s;
  }
  function font(size, weight, mono) { return `${weight || 500} ${size}px ${mono ? MONO : SANS}`; }
  function text(ctx, s, x, y, o = {}) {
    if (WT.tr) s = WT.tr(s);
    let size = o.size || 13; ctx.font = font(size, o.weight, o.mono);
    if (o.max) while (ctx.measureText(s).width > o.max && size > 9) { size -= 0.5; ctx.font = font(size, o.weight, o.mono); }
    ctx.textAlign = o.align || "left"; ctx.textBaseline = o.base || "middle"; ctx.fillStyle = o.color || C.ink; ctx.globalAlpha = o.alpha ?? 1;
    ctx.fillText(s, x, y); ctx.globalAlpha = 1; return ctx.measureText(s).width;
  }
  function wrap(ctx, s, maxW, size, weight) {
    ctx.font = font(size, weight); const words = String(s).split(" "), lines = []; let cur = "";
    words.forEach((w) => { const t = cur ? cur + " " + w : w; if (ctx.measureText(t).width > maxW && cur) { lines.push(cur); cur = w; } else cur = t; });
    if (cur) lines.push(cur); return lines;
  }
  function rrect(ctx, x, y, w, h, r) { ctx.beginPath(); if (ctx.roundRect) ctx.roundRect(x, y, w, h, r); else ctx.rect(x, y, w, h); }
  function pill(ctx, s, x, y, col, o = {}) {
    const size = o.size || 12; ctx.font = font(size, 600); const w = ctx.measureText(s).width + 16, h = size + 9;
    const x0 = o.align === "right" ? x - w : o.align === "center" ? x - w / 2 : x;
    rrect(ctx, x0, y - h / 2, w, h, h / 2); ctx.fillStyle = rgba(col, o.fill ?? 0.14); ctx.fill(); ctx.strokeStyle = rgba(col, 0.75); ctx.lineWidth = 1.2; ctx.stroke();
    text(ctx, s, x0 + w / 2, y + 0.5, { size, weight: 600, color: col, align: "center" }); return w;
  }
  function arrowHead(ctx, x, y, ang, col, size = 8) {
    ctx.save(); ctx.fillStyle = col; ctx.beginPath(); ctx.moveTo(x, y);
    ctx.lineTo(x - size * Math.cos(ang - 0.45), y - size * Math.sin(ang - 0.45)); ctx.lineTo(x - size * Math.cos(ang + 0.45), y - size * Math.sin(ang + 0.45)); ctx.closePath(); ctx.fill(); ctx.restore();
  }
  function glowDot(ctx, x, y, r, col) {
    const g = ctx.createRadialGradient(x, y, 0, x, y, r * 4); g.addColorStop(0, rgba(col, 0.9)); g.addColorStop(0.25, rgba(col, 0.35)); g.addColorStop(1, rgba(col, 0));
    ctx.fillStyle = g; ctx.beginPath(); ctx.arc(x, y, r * 4, 0, Math.PI * 2); ctx.fill();
    ctx.fillStyle = "#fff"; ctx.beginPath(); ctx.arc(x, y, r * 0.8, 0, Math.PI * 2); ctx.fill();
  }

  // ===================================================================================================================
  // the stages
  // ===================================================================================================================
  const STAGES = [
    { id: "meas", col: C.meas, t: T("pl_s1_t", "Measurements"), sub: T("pl_s1_s", "EXFOR experiments + IAEA standards"), viz: "meas",
      lead: T("pl_s1_lead", "Raw EXFOR experiments and IAEA standards"), tag: T("pl_s1_tag", "illustration · simulated data"), },
    { id: "fit", col: C.fit, t: T("pl_s2_t", "Data model + fit"), sub: T("pl_s2_s", "R-matrix, through our model of each experiment"), viz: "fit",
      lead: T("pl_s2_lead", "Fit raw data through our experiment model"), tag: T("pl_s2_tag", "illustration · simulated data"), },
    { id: "file", col: C.file, t: T("pl_s3_t", "Evaluated file"), sub: T("pl_s3_s", "ENDF-6 tape"), viz: "endf",
      lead: T("pl_s3_lead", "Parameters written to an ENDF-6 file"), tag: T("pl_s3_tag", "schematic"), },
    { id: "proc", col: C.proc, t: T("pl_s4_t", "Processing"), sub: T("pl_s4_s", "NJOY: reconstruct, broaden, tabulate"), viz: "dop",
      lead: T("pl_s4_lead", "NJOY reconstructs and broadens to reactor temperatures"), tag: T("pl_s4_tag", "illustration"), },
    { id: "lib", col: C.lib, t: T("pl_s5_t", "Library"), sub: T("pl_s5_s", "OpenMC HDF5 + cross_sections.xml"), viz: "lib",
      lead: T("pl_s5_lead", "res-v0.1: seven own resonance-region files"), tag: T("pl_s5_tag", ""), },
    { id: "bench", col: C.bench, t: T("pl_s6_t", "Benchmarks"), sub: T("pl_s6_s", "ICSBEP critical experiments, k-eff"), viz: "bench",
      lead: T("pl_s6_lead", "Real experiments: does simulation hit the measured answer?"), tag: T("pl_s6_tag", ""), },
    { id: "judge", col: C.judge, t: T("pl_s7_t", "Judges"), sub: T("pl_s7_s", "fixed checks; failures go back"), viz: "judge",
      lead: T("pl_s7_lead", "Every file checked against EXFOR alone"), tag: T("pl_s7_tag", ""), },
  ];

  // ===================================================================================================================
  // the diagram
  // ===================================================================================================================
  const fcv = document.getElementById("pl-flow"), flow = surf(fcv);
  let cur = 0, hover = -1, boxes = [], horiz = true, loopPath = [], anim = null;

  function icon(ctx, id, x, y, col) { // a small glyph per stage, 22 x 16 px, top-left at x, y
    ctx.save(); ctx.strokeStyle = col; ctx.fillStyle = col; ctx.lineWidth = 1.5; ctx.lineCap = "round";
    if (id === "meas") { [[2, 10], [6, 7], [10, 12], [14, 4], [18, 9]].forEach(([a, b]) => { ctx.beginPath(); ctx.arc(x + a, y + b, 1.7, 0, 7); ctx.fill(); }); }
    else if (id === "fit") { ctx.beginPath(); for (let i = 0; i <= 22; i++) { const u = (i - 11) / 2.4; const v = y + 3 + 11 * (1 - 1 / (1 + u * u)); i ? ctx.lineTo(x + i, v) : ctx.moveTo(x + i, v); } ctx.stroke(); }
    else if (id === "file") { [3, 7, 11, 15].forEach((b, i) => { ctx.beginPath(); ctx.moveTo(x + 2, y + b); ctx.lineTo(x + (i % 2 ? 14 : 20), y + b); ctx.stroke(); }); }
    else if (id === "proc") { ctx.beginPath(); for (let i = 0; i <= 22; i++) { const u = (i - 11) / 4; const v = y + 15 - 11 * Math.exp(-u * u); i ? ctx.lineTo(x + i, v) : ctx.moveTo(x + i, v); } ctx.stroke(); }
    else if (id === "lib") { [0, 5, 10].forEach((d) => { ctx.beginPath(); ctx.ellipse(x + 11, y + 3 + d, 8, 2.6, 0, 0, 7); ctx.stroke(); }); }
    else if (id === "bench") { ctx.beginPath(); ctx.arc(x + 11, y + 14, 9, Math.PI, 2 * Math.PI); ctx.stroke(); ctx.beginPath(); ctx.moveTo(x + 11, y + 14); ctx.lineTo(x + 15, y + 7); ctx.stroke(); }
    else if (id === "judge") { ctx.beginPath(); ctx.moveTo(x + 3, y + 8); ctx.lineTo(x + 8, y + 13); ctx.lineTo(x + 19, y + 2); ctx.stroke(); }
    ctx.restore();
  }

  function layoutFlow() {
    const W = Math.max(280, fcv.parentElement.clientWidth); horiz = W >= 860; boxes = [];
    if (horiz) {
      const m = 14, gx = 22, top = 14, ph = 112, bw = (W - 2 * m - 6 * gx) / 7;
      STAGES.forEach((_, i) => boxes.push({ x: m + i * (bw + gx), y: top, w: bw, h: ph }));
      const ly = top + ph + 30, a = boxes[6], b = boxes[1];
      loopPath = [[a.x + a.w / 2, a.y + a.h], [a.x + a.w / 2, ly], [b.x + b.w / 2, ly], [b.x + b.w / 2, b.y + b.h]];
      flow.size(W, ly + 22);
    } else {
      const m = 12, top = 12, rh = 52, gy = 12, gut = 40;
      STAGES.forEach((_, i) => boxes.push({ x: m, y: top + i * (rh + gy), w: W - m - gut, h: rh }));
      const lx = W - 18, a = boxes[6], b = boxes[1];
      loopPath = [[a.x + a.w, a.y + a.h / 2], [lx, a.y + a.h / 2], [lx, b.y + b.h / 2], [b.x + b.w, b.y + b.h / 2]];
      flow.size(W, boxes[6].y + rh + top);
    }
    drawFlow();
  }

  function connector(ctx, i) { // from stage i to i+1: [x1, y1, x2, y2]
    const a = boxes[i], b = boxes[i + 1];
    return horiz ? [a.x + a.w + 3, a.y + a.h / 2, b.x - 3, b.y + b.h / 2] : [a.x + 26, a.y + a.h + 2, b.x + 26, b.y - 2];
  }

  function drawFlow(pulseT) {
    const { ctx, W, H } = flow; ctx.clearRect(0, 0, W, H);
    // connectors
    for (let i = 0; i < 6; i++) {
      const [x1, y1, x2, y2] = connector(ctx, i), lit = i < cur;
      const g = ctx.createLinearGradient(x1, y1, x2, y2); g.addColorStop(0, rgba(STAGES[i].col, lit ? 0.9 : 0.4)); g.addColorStop(1, rgba(STAGES[i + 1].col, lit ? 0.9 : 0.4));
      ctx.strokeStyle = g; ctx.lineWidth = lit ? 2 : 1.5; ctx.beginPath(); ctx.moveTo(x1, y1); ctx.lineTo(x2 - (horiz ? 4 : 0), y2 - (horiz ? 0 : 4)); ctx.stroke();
      arrowHead(ctx, x2, y2, Math.atan2(y2 - y1, x2 - x1), rgba(STAGES[i + 1].col, lit ? 0.95 : 0.55), 7);
    }
    // the judges' loop back to the fit
    const loopOn = cur === 6 || cur === 1 || hover === 6;
    ctx.save(); ctx.strokeStyle = rgba(C.judge, loopOn ? 0.9 : 0.5); ctx.lineWidth = loopOn ? 2 : 1.5; ctx.setLineDash([6, 5]); ctx.lineJoin = "round";
    ctx.beginPath(); loopPath.forEach(([x, y], i) => (i ? ctx.lineTo(x, y) : ctx.moveTo(x, y))); ctx.stroke(); ctx.restore();
    { const [x2, y2] = loopPath[3], [x1, y1] = loopPath[2]; arrowHead(ctx, x2, y2, Math.atan2(y2 - y1, x2 - x1), rgba(C.judge, loopOn ? 0.95 : 0.6), 8); }
    const loopLab = T("pl_loop", "fails a judge → back to the fit");
    if (horiz) { const mx = (loopPath[1][0] + loopPath[2][0]) / 2; ctx.font = font(12, 600); const w = ctx.measureText(loopLab).width + 18; rrect(ctx, mx - w / 2, loopPath[1][1] - 11, w, 22, 11); ctx.fillStyle = "#0b1226"; ctx.fill(); text(ctx, loopLab, mx, loopPath[1][1], { size: 12, weight: 600, color: rgba(C.judge, loopOn ? 1 : 0.8), align: "center" }); }
    else { ctx.save(); const lx = loopPath[1][0], my = (loopPath[1][1] + loopPath[2][1]) / 2; ctx.translate(lx, my); ctx.rotate(-Math.PI / 2); ctx.font = font(11.5, 600); const w = ctx.measureText(loopLab).width + 14; rrect(ctx, -w / 2, -9, w, 18, 9); ctx.fillStyle = "#0b1226"; ctx.fill(); text(ctx, loopLab, 0, 0.5, { size: 11.5, weight: 600, color: rgba(C.judge, loopOn ? 1 : 0.8), align: "center" }); ctx.restore(); }
    // panels
    STAGES.forEach((s, i) => {
      const b = boxes[i], sel = i === cur, hov = i === hover;
      ctx.save();
      if (sel) { ctx.shadowColor = rgba(s.col, 0.55); ctx.shadowBlur = 22; }
      rrect(ctx, b.x, b.y, b.w, b.h, 12);
      const g = ctx.createLinearGradient(0, b.y, 0, b.y + b.h); g.addColorStop(0, sel ? rgba(s.col, 0.2) : "rgba(28,38,66,.9)"); g.addColorStop(1, sel ? "rgba(14,20,40,.95)" : "rgba(12,18,36,.92)");
      ctx.fillStyle = g; ctx.fill(); ctx.restore();
      rrect(ctx, b.x, b.y, b.w, b.h, 12); ctx.strokeStyle = sel ? s.col : hov ? rgba(s.col, 0.7) : C.panel; ctx.lineWidth = sel ? 2 : 1.2; ctx.stroke();
      // lit edge
      const lg = horiz ? ctx.createLinearGradient(b.x, 0, b.x + b.w, 0) : ctx.createLinearGradient(0, b.y, 0, b.y + b.h);
      lg.addColorStop(0, rgba(s.col, 0)); lg.addColorStop(0.5, rgba(s.col, sel ? 1 : 0.55)); lg.addColorStop(1, rgba(s.col, 0));
      ctx.fillStyle = lg; if (horiz) ctx.fillRect(b.x + 10, b.y + 1, b.w - 20, 2); else ctx.fillRect(b.x + 1, b.y + 8, 2, b.h - 16);
      if (horiz) {
        text(ctx, String(i + 1).padStart(2, "0"), b.x + 12, b.y + 18, { size: 11, mono: true, color: s.col, weight: 500 });
        icon(ctx, s.id, b.x + b.w - 32, b.y + 10, rgba(s.col, sel || hov ? 1 : 0.7));
        const tl = wrap(ctx, s.t, b.w - 22, 15, 600);
        tl.slice(0, 2).forEach((l, k) => text(ctx, l, b.x + 12, b.y + 40 + k * 18, { size: 15, weight: 600, color: sel ? "#fff" : C.ink, max: b.w - 20 }));
        const sl = wrap(ctx, s.sub, b.w - 22, 12, 500), y0 = b.y + 40 + Math.min(2, tl.length) * 18 + 2;
        sl.slice(0, Math.max(1, Math.floor((b.y + b.h - 8 - y0) / 15))).forEach((l, k) => text(ctx, l, b.x + 12, y0 + k * 15, { size: 12, color: C.soft, max: b.w - 20 }));
      } else {
        text(ctx, String(i + 1).padStart(2, "0"), b.x + 26, b.y + b.h / 2, { size: 12, mono: true, color: s.col, align: "center" });
        text(ctx, s.t, b.x + 48, b.y + 18, { size: 15, weight: 600, color: sel ? "#fff" : C.ink, max: b.w - 86 });
        ctx.font = font(12); let sub = s.sub; const mw = b.w - 60; while (ctx.measureText(sub).width > mw && sub.length > 4) sub = sub.slice(0, -2).trimEnd() + "…";
        text(ctx, sub.replace(/……$/, "…"), b.x + 48, b.y + 36, { size: 12, color: C.soft });
        icon(ctx, s.id, b.x + b.w - 32, b.y + 10, rgba(s.col, sel || hov ? 1 : 0.7));
      }
    });
    // a pulse travelling along the pipe to the newly picked stage
    if (pulseT != null && anim) {
      const pts = anim.path; let L = 0; const seg = []; for (let i = 1; i < pts.length; i++) { const d = Math.hypot(pts[i][0] - pts[i - 1][0], pts[i][1] - pts[i - 1][1]); seg.push(d); L += d; }
      let d = pulseT * L, k = 0; while (k < seg.length - 1 && d > seg[k]) { d -= seg[k]; k++; }
      const f = seg[k] ? d / seg[k] : 0, x = pts[k][0] + (pts[k + 1][0] - pts[k][0]) * f, y = pts[k][1] + (pts[k + 1][1] - pts[k][1]) * f;
      glowDot(ctx, x, y, 3.2, anim.col);
    }
  }

  function pulseTo(from, to) {
    if (RM || from === to) return drawFlow();
    let path = [];
    if (from === 6 && to === 1) path = loopPath.slice();
    else { const lo = Math.min(from, to), hi = Math.max(from, to); for (let i = lo; i < hi; i++) { const [x1, y1, x2, y2] = connector(null, i); path.push([x1, y1], [x2, y2]); } if (to < from) path.reverse(); }
    if (path.length < 2) return drawFlow();
    const t0 = performance.now(), dur = Math.min(900, 260 + 160 * Math.abs(to - from));
    anim = { path, col: STAGES[to].col };
    const step = (now) => { const t = clamp((now - t0) / dur, 0, 1); drawFlow(t < 1 ? t * t * (3 - 2 * t) : null); if (t < 1) anim.raf = requestAnimationFrame(step); else anim = null; };
    if (anim.raf) cancelAnimationFrame(anim.raf); anim.raf = requestAnimationFrame(step);
  }

  const hitBox = (x, y) => boxes.findIndex((b) => x >= b.x && x <= b.x + b.w && y >= b.y && y <= b.y + b.h);
  fcv.addEventListener("pointermove", (e) => { const h = hitBox(e.offsetX, e.offsetY); if (h !== hover) { hover = h; fcv.style.cursor = h >= 0 ? "pointer" : "default"; if (!anim) drawFlow(); } });
  fcv.addEventListener("pointerleave", () => { if (hover !== -1) { hover = -1; if (!anim) drawFlow(); } });
  fcv.addEventListener("click", (e) => { const h = hitBox(e.offsetX, e.offsetY); if (h >= 0) select(h, true); });
  fcv.addEventListener("keydown", (e) => {
    const k = e.key, n = k === "ArrowRight" || k === "ArrowDown" ? cur + 1 : k === "ArrowLeft" || k === "ArrowUp" ? cur - 1 : k === "Home" ? 0 : k === "End" ? 6 : null;
    if (n != null) { e.preventDefault(); select(clamp(n, 0, 6)); }
  });
  // screen-reader / keyboard tabs that mirror the diagram
  const tabs = document.getElementById("pl-tabs");
  STAGES.forEach((s, i) => { const b = document.createElement("button"); b.type = "button"; b.setAttribute("role", "tab"); b.textContent = `${i + 1}. ${s.t}`; b.addEventListener("click", () => select(i)); tabs.appendChild(b); });

  // ===================================================================================================================
  // the stage panel and its live drawing
  // ===================================================================================================================
  const stEl = document.getElementById("pl-stage"), vcv = document.getElementById("pl-viz"), viz = surf(vcv), ctl = document.getElementById("pl-ctl"), tagEl = document.getElementById("pl-tag"), tip = document.getElementById("pl-tip");
  const VIZ = {};
  let V = null;
  const vW = () => Math.max(260, vcv.parentElement.clientWidth);
  function sizeViz() { const W = vW(); viz.size(W, V.height(W)); V.draw(); }
  function showTip(html, x, y) { if (!html) { tip.hidden = true; return; } tip.innerHTML = html; tip.hidden = false; const W = viz.W, tw = tip.offsetWidth, th = tip.offsetHeight; tip.style.left = clamp(x + 12, 4, W - tw - 4) + "px"; tip.style.top = (y - th - 10 < 4 ? y + 14 : y - th - 10) + "px"; }

  function select(i, fromClick) {
    const prev = cur; cur = i; const s = STAGES[i];
    stEl.style.setProperty("--c", s.col); stEl.style.setProperty("--glow", rgba(s.col, 0.32));
    document.getElementById("pl-num").textContent = T("pl_stage_n", "Stage {i} of 7").replace("{i}", i + 1);
    document.getElementById("pl-title").textContent = s.t;
    document.getElementById("pl-lead").textContent = s.lead;
    tagEl.textContent = s.tag; tagEl.hidden = !s.tag;
    const pv = document.getElementById("pl-prev"), nx = document.getElementById("pl-next");
    pv.hidden = i === 0; nx.hidden = i === 6; if (i > 0) pv.querySelector("span").textContent = STAGES[i - 1].t; if (i < 6) nx.querySelector("span").textContent = i === 6 ? "" : STAGES[i + 1].t;
    [...tabs.children].forEach((b, k) => b.setAttribute("aria-selected", String(k === i)));
    if (V && V.stop) V.stop();
    tip.hidden = true; ctl.innerHTML = ""; V = VIZ[s.viz]; vcv.setAttribute("aria-label", s.t + ": " + s.lead); V.init(ctl); sizeViz();
    pulseTo(prev, i);
    try { history.replaceState(null, "", "#" + s.id); } catch (e) {}
    if (fromClick && !horiz) { const r = stEl.getBoundingClientRect(); if (r.top > innerHeight * 0.8) stEl.scrollIntoView({ behavior: RM ? "auto" : "smooth", block: "start" }); }
  }
  document.getElementById("pl-prev").addEventListener("click", () => select(Math.max(0, cur - 1)));
  document.getElementById("pl-next").addEventListener("click", () => select(Math.min(6, cur + 1)));
  vcv.addEventListener("pointermove", (e) => V && V.move && V.move(e.offsetX, e.offsetY));
  vcv.addEventListener("pointerdown", (e) => V && V.down && V.down(e.offsetX, e.offsetY));
  vcv.addEventListener("pointerleave", () => { tip.hidden = true; V && V.leave && V.leave(); });

  // small control builders
  function seg(items, val, on, col) {
    const box = document.createElement("div"); box.className = "pl-seg"; box.setAttribute("role", "group"); if (col) box.style.setProperty("--c", col);
    items.forEach(([v, label, title, dot]) => { const b = document.createElement("button"); b.type = "button"; b.textContent = label; if (title) b.title = title; if (dot) { const i = document.createElement("i"); i.className = "pl-dot"; i.style.background = dot; b.prepend(i); } b.setAttribute("aria-pressed", String(v === val)); b.addEventListener("click", () => { [...box.children].forEach((c) => c.setAttribute("aria-pressed", String(c === b))); on(v); }); box.appendChild(b); });
    return box;
  }
  function chk(label, val, on) { const l = document.createElement("label"); l.className = "pl-chk"; const i = document.createElement("input"); i.type = "checkbox"; i.checked = val; i.addEventListener("change", () => on(i.checked)); l.append(i, document.createTextNode(label)); return l; }
  function rng(label, min, max, step, val, show, on) {
    const l = document.createElement("label"); l.className = "pl-rng"; const sp = document.createElement("span"); sp.innerHTML = label;
    const i = document.createElement("input"); i.type = "range"; i.min = min; i.max = max; i.step = step; i.value = val; const o = document.createElement("output"); o.textContent = show(+val);
    i.addEventListener("input", () => { o.textContent = show(+i.value); on(+i.value); }); l.append(sp, i, o); l.set = (v) => { i.value = v; o.textContent = show(+v); }; return l;
  }
  function el(tag, cls, html) { const e = document.createElement(tag); if (cls) e.className = cls; if (html != null) e.innerHTML = html; return e; }

  // axes helper: frame, gridlines and labels for a plot area
  function frame(ctx, a, xt, yt, o = {}) {
    ctx.save(); ctx.strokeStyle = C.grid; ctx.lineWidth = 1;
    yt.forEach(([v, lab]) => { const y = a.y(v); ctx.beginPath(); ctx.moveTo(a.x0, y); ctx.lineTo(a.x1, y); ctx.stroke(); text(ctx, lab, a.x0 - 6, y, { size: 11, color: C.faint, align: "right", mono: true }); });
    xt.forEach(([v, lab]) => { const x = a.x(v); ctx.beginPath(); ctx.moveTo(x, a.y0); ctx.lineTo(x, a.y1); ctx.stroke(); if (lab) text(ctx, lab, x, a.y1 + 12, { size: 11, color: C.faint, align: "center", mono: true }); });
    ctx.strokeStyle = C.axis; ctx.beginPath(); ctx.moveTo(a.x0, a.y0); ctx.lineTo(a.x0, a.y1); ctx.lineTo(a.x1, a.y1); ctx.stroke(); ctx.restore();
    if (o.ylab) text(ctx, o.ylab, a.x0 - (o.ylx ?? 0), a.y0 - 12, { size: 11.5, color: C.soft, weight: 600 });
  }
  function line(ctx, pts, col, w, dash, alpha) { ctx.save(); ctx.strokeStyle = col; ctx.lineWidth = w || 2; ctx.globalAlpha = alpha ?? 1; ctx.lineJoin = "round"; if (dash) ctx.setLineDash(dash); ctx.beginPath(); pts.forEach(([x, y], i) => (i ? ctx.lineTo(x, y) : ctx.moveTo(x, y))); ctx.stroke(); ctx.restore(); }

  // ---------- stages 1 and 2: simulated transmission data, and the fit ----------
  const MEAS = { show: "both", fx: { res: true, bkg: true, norm: true } };
  const FIT = { p: { E0: 9.93, G: 0.16, S0: 1500, SP: TRUE.SP }, model: true, nm: null, raf: 0, data: P.data(P.ALL), fitted: null };
  const EFINE = Array.from({ length: 241 }, (_, i) => ELO + ((EHI - ELO) * i) / 240);
  function transPlot(W, H) {
    const narrow = W < 520, L = narrow ? 40 : 48, R = 12, top = 50, gap = 40, bottom = 30, h = H - top - gap - bottom, h1 = Math.round(h * 0.62), h2 = h - h1;
    const xs = (E) => L + ((E - ELO) / (EHI - ELO)) * (W - L - R);
    const A1 = { x0: L, x1: W - R, y0: top, y1: top + h1, x: xs, y: (t) => top + h1 - (clamp(t, -0.05, 1.12) / 1.1) * h1 };
    const lg = (s) => Math.log10(clamp(s, 3, 3e4)), y20 = top + h1 + gap;
    const A2 = { x0: L, x1: W - R, y0: y20, y1: y20 + h2, x: xs, y: (s) => y20 + h2 - ((lg(s) - lg(3)) / (lg(3e4) - lg(3))) * h2 };
    return { A1, A2, narrow };
  }
  const xTicks = [9.6, 9.8, 10, 10.2, 10.4].map((E) => [E, E.toFixed(1)]);
  function drawTrans(mode) {
    const { ctx, W, H } = viz; ctx.clearRect(0, 0, W, H);
    const { A1, A2, narrow } = transPlot(W, H);
    frame(ctx, A1, xTicks.map(([v]) => [v, ""]), [[0, "0"], [0.5, "0.5"], [1, "1"]], { ylab: T("pl_tr_y", "transmission (fraction of neutrons through)") });
    frame(ctx, A2, xTicks, [[10, "10"], [100, "100"], [1000, "1000"], [10000, "10⁴"]], { ylab: T("pl_sig_y", "cross section (barns)") });
    text(ctx, T("pl_E_x", "neutron energy (eV)"), A2.x1, A2.y1 + 24, { size: 11, color: C.faint, align: "right" });
    const sigTrue = EFINE.map((E) => [A2.x(E), A2.y(P.sig(E, TRUE))]);
    const show = mode === "fit" ? ["thin", "thick"] : MEAS.show === "both" ? ["thin", "thick"] : [MEAS.show];
    const data = mode === "fit" ? FIT.data : P.data(MEAS.fx);
    EXPS.forEach((x, k) => {
      if (!show.includes(x.key)) return; const col = C[x.key];
      if (mode === "meas") line(ctx, EFINE.map((E, i) => [A1.x(E), A1.y(Math.exp(-x.n * P.sig(E, TRUE)))]), col, 1.4, [5, 4], 0.7);
      else { const m = P.recorded(FIT.p, x.n, FIT.model ? P.ALL : P.NONE, EFINE); ctx.save(); ctx.shadowColor = rgba(C.fit, 0.6); ctx.shadowBlur = 8; line(ctx, EFINE.map((E, i) => [A1.x(E), A1.y(m[i])]), col, 2.2); ctx.restore(); }
      ctx.fillStyle = col; data[k].forEach((v, i) => { ctx.globalAlpha = 0.9; ctx.beginPath(); ctx.arc(A1.x(ED[i]), A1.y(v), narrow ? 2 : 2.4, 0, 7); ctx.fill(); }); ctx.globalAlpha = 1;
    });
    // legend
    let lx = narrow ? 8 : A1.x0 + 8; const ly = 14;
    show.forEach((key) => { ctx.fillStyle = C[key]; ctx.beginPath(); ctx.arc(lx + 4, ly, 3, 0, 7); ctx.fill(); lx += 12 + text(ctx, key === "thin" ? (narrow ? T("pl_thin_b", "Thin") : T("pl_thin", "thin sample")) : (narrow ? T("pl_thick_b", "Thick") : T("pl_thick", "thick sample")), lx + 12, ly, { size: 12, color: C.soft }) + 14; });
    if (mode === "meas") { line(ctx, [[lx, ly], [lx + 18, ly]], C.soft, 1.4, [5, 4]); text(ctx, narrow ? T("pl_perfect_s", "perfect experiment") : T("pl_perfect", "what a perfect experiment would record"), lx + 24, ly, { size: 12, color: C.soft }); }
    else { line(ctx, [[lx, ly], [lx + 18, ly]], C.ink, 2.2); text(ctx, narrow ? (FIT.model ? T("pl_model_on_s", "fit, with our model") : T("pl_model_off_s", "fit, no experiment")) : FIT.model ? T("pl_model_on", "fit, through our experiment model") : T("pl_model_off", "fit, experiment ignored"), lx + 24, ly, { size: 12, color: C.soft, max: W - lx - 30 }); }
    // lower panel: the cross section
    if (mode === "meas") { ctx.save(); ctx.shadowColor = rgba("#ffffff", 0.5); ctx.shadowBlur = 10; line(ctx, sigTrue, "#f2f5ff", 2); ctx.restore(); text(ctx, T("pl_sig_true", "the cross section we want"), A2.x(10.06) + 4, A2.y(2500), { size: 12, color: C.ink }); }
    else {
      line(ctx, sigTrue, C.soft, 1.4, [4, 4], 0.8);
      ctx.save(); ctx.shadowColor = rgba(C.fit, 0.7); ctx.shadowBlur = 10; line(ctx, EFINE.map((E) => [A2.x(E), A2.y(P.sig(E, FIT.p))]), C.fit, 2.2); ctx.restore();
      const yy = A2.y0 + 10; line(ctx, [[A2.x1 - (narrow ? 150 : 300), yy], [A2.x1 - (narrow ? 132 : 282), yy]], C.soft, 1.4, [4, 4]);
      text(ctx, T("pl_true_s", "true (simulated)"), A2.x1 - (narrow ? 126 : 276), yy, { size: 11.5, color: C.soft });
    }
  }
  VIZ.meas = {
    height: (W) => (W < 520 ? 350 : 370),
    init(box) {
      box.append(seg([["both", T("pl_both", "Both samples")], ["thin", T("pl_thin_b", "Thin")], ["thick", T("pl_thick_b", "Thick")]], MEAS.show, (v) => { MEAS.show = v; this.draw(); }, C.meas));
      [["res", T("pl_fx_res", "Detector resolution")], ["bkg", T("pl_fx_bkg", "Background")], ["norm", T("pl_fx_norm", "Normalisation (−3 %)")]].forEach(([k, lab]) => box.append(chk(lab, MEAS.fx[k], (v) => { MEAS.fx[k] = v; this.draw(); })));
    },
    draw: () => drawTrans("meas"),
  };
  VIZ.fit = {
    height: (W) => (W < 520 ? 350 : 370),
    init(box) {
      box.style.setProperty("--c", C.fit);
      const show = { E0: (v) => fmt(v, 3) + " eV", G: (v) => fmt(v * 1000, 0) + " meV", S0: (v) => Math.round(Math.pow(10, v)).toLocaleString("en-US").replace(/,/g, " ") + " b" };
      this.rE = rng(T("pl_p_E", "energy"), 9.8, 10.2, 0.001, FIT.p.E0, show.E0, (v) => { FIT.p.E0 = v; this.upd(); });
      this.rG = rng(T("pl_p_G", "width Γ"), 0.01, 0.3, 0.001, FIT.p.G, show.G, (v) => { FIT.p.G = v; this.upd(); });
      this.rS = rng(T("pl_p_S", "peak σ₀"), 2.5, 4.5, 0.005, Math.log10(FIT.p.S0), show.S0, (v) => { FIT.p.S0 = Math.pow(10, v); this.upd(); });
      this.bFit = el("button", "pl-btn", T("pl_fitbtn", "Fit")); this.bFit.type = "button"; this.bFit.addEventListener("click", () => this.run());
      const bReset = el("button", "pl-btn ghost", T("pl_reset", "Reset")); bReset.type = "button"; bReset.addEventListener("click", () => { this.stop(); FIT.p = { E0: 9.93, G: 0.16, S0: 1500, SP: TRUE.SP }; this.sync(); this.upd(); });
      this.read = el("div", "pl-read");
      box.append(this.bFit, bReset, chk(T("pl_model_chk", "Our experiment model (here: resolution, background, normalisation)"), FIT.model, (v) => { FIT.model = v; this.upd(); }), this.rE, this.rG, this.rS, this.read);
      this.upd(true);
    },
    sync() { this.rE.set(FIT.p.E0); this.rG.set(FIT.p.G); this.rS.set(Math.log10(FIT.p.S0)); },
    upd(noDraw) {
      const c2 = P.chi2(FIT.p, FIT.data, FIT.model);
      this.read.innerHTML = `<span>χ²/point <b>${fmt(c2, c2 < 10 ? 2 : 0)}</b></span><span>${T("pl_vs_true", "true values")}: <b>10.000 eV</b>, <b>60 meV</b>, <b>4 000 b</b></span>`;
      if (!noDraw) this.draw();
    },
    run() {
      this.stop(); const f = (x) => (x[1] < Math.log(0.004) || x[1] > Math.log(1) ? 1e9 : P.chi2(P.toP(x), FIT.data, FIT.model));
      FIT.nm = P.nmInit(f, P.toX(FIT.p), [0.03, 0.4, 0.4]); this.bFit.disabled = true;
      const step = () => {
        for (let k = 0; k < (RM ? 400 : 1); k++) { P.nmStep(FIT.nm); if (FIT.nm.it > 400 || FIT.nm.spread < 1e-6) break; }
        FIT.p = P.toP(FIT.nm.best); this.sync(); this.upd();
        if (FIT.nm.it > 400 || FIT.nm.spread < 1e-6) { this.stop(); return; }
        FIT.raf = requestAnimationFrame(step);
      };
      FIT.raf = requestAnimationFrame(step);
    },
    stop() { if (FIT.raf) cancelAnimationFrame(FIT.raf); FIT.raf = 0; if (this.bFit) this.bFit.disabled = false; },
    draw: () => drawTrans("fit"),
  };

  // ---------- stage 3: anatomy of an ENDF-6 file (hybrid) ----------
  const ENDF = [
    { k: "MF2", t: T("pl_e_rrr", "Resolved resonances"), span: [0, 0.42], own: true, d: T("pl_e_rrr_d", "<b>MF2 · resolved resonances</b> · ours") },
    { k: "MF2", t: T("pl_e_urr", "Unresolved resonances"), span: [0.42, 0.62], d: T("pl_e_urr_d", "<b>MF2 · unresolved resonances</b> · ENDF/B-VIII.1") },
    { k: "MF3", t: T("pl_e_mf3", "Cross sections"), span: [0, 1], soft: [0, 0.62], d: T("pl_e_mf3_d", "<b>MF3 · cross sections</b> · ENDF/B-VIII.1") },
    { k: "MF4", t: T("pl_e_mf4", "Angular distributions"), span: [0, 1], d: T("pl_e_mf4_d", "<b>MF4 · angular distributions</b> · ENDF/B-VIII.1") },
    { k: "MF5/6", t: T("pl_e_mf5", "Energy distributions"), span: [0, 1], d: T("pl_e_mf5_d", "<b>MF5/6 · energy distributions</b> · ENDF/B-VIII.1") },
    { k: "MF1", t: T("pl_e_mf1", "General information, ν̄"), span: [0, 1], d: T("pl_e_mf1_d", "<b>MF1 · ν̄ and header</b> · ENDF/B-VIII.1") },
  ];
  const EN = { sel: 0, hov: -1 };
  function endfGeom(W) { const narrow = W < 560, lab = narrow ? 118 : 196, top = 40, rh = narrow ? 34 : 38, x0 = lab + 8, x1 = W - 14; return { narrow, lab, top, rh, x0, x1 }; }
  VIZ.endf = {
    height: (W) => { const g = endfGeom(W); return g.top + ENDF.length * g.rh + 40; },
    init(box) { this.note = el("p", "pl-note"); box.append(this.note); this.setNote(); },
    setNote() { this.note.innerHTML = ENDF[EN.sel].d; },
    draw() {
      const { ctx, W, H } = viz; ctx.clearRect(0, 0, W, H); const g = endfGeom(W);
      // legend
      ctx.fillStyle = rgba(C.file, 0.85); rrect(ctx, 14, 14, 14, 10, 3); ctx.fill(); let x = 34 + text(ctx, T("pl_own", "INCOGNITA's own"), 34, 19, { size: 12, color: C.soft });
      ctx.fillStyle = "rgba(150,165,200,.28)"; rrect(ctx, x + 16, 14, 14, 10, 3); ctx.fill(); text(ctx, T("pl_carrier", "ENDF/B-VIII.1 carrier"), x + 36, 19, { size: 12, color: C.soft });
      ENDF.forEach((r, i) => {
        const y = g.top + i * g.rh, h = g.rh - 10, on = i === EN.sel || i === EN.hov;
        if (on) { ctx.fillStyle = "rgba(150,170,230,.07)"; rrect(ctx, 6, y - 3, W - 12, g.rh - 4, 8); ctx.fill(); }
        text(ctx, r.k, 14, y + h / 2, { size: 11, mono: true, color: r.own ? C.file : C.faint });
        text(ctx, r.t, g.narrow ? 14 : 66, g.narrow ? y + h / 2 + 12 : y + h / 2, { size: g.narrow ? 11.5 : 13, color: on ? "#fff" : C.ink, weight: on ? 600 : 500, max: g.lab - (g.narrow ? 14 : 66) });
        const a = g.x0 + r.span[0] * (g.x1 - g.x0), b = g.x0 + r.span[1] * (g.x1 - g.x0);
        ctx.save(); rrect(ctx, a, y, b - a, h, 6);
        if (r.own) { ctx.shadowColor = rgba(C.file, 0.7); ctx.shadowBlur = 14; const gr = ctx.createLinearGradient(a, 0, b, 0); gr.addColorStop(0, rgba(C.file, 0.95)); gr.addColorStop(1, rgba(C.file, 0.6)); ctx.fillStyle = gr; }
        else ctx.fillStyle = "rgba(150,165,200,.26)";
        ctx.fill(); ctx.restore();
        if (r.soft) { ctx.fillStyle = "rgba(150,165,200,.10)"; const s0 = g.x0 + r.soft[0] * (g.x1 - g.x0), s1 = g.x0 + r.soft[1] * (g.x1 - g.x0); rrect(ctx, s0, y, s1 - s0, h, 6); ctx.fill(); }
        if (on) { rrect(ctx, a, y, b - a, h, 6); ctx.strokeStyle = r.own ? "#fff" : "rgba(200,210,240,.7)"; ctx.lineWidth = 1.4; ctx.stroke(); }
      });
      // energy axis (region boundaries schematic)
      const ya = g.top + ENDF.length * g.rh + 2; ctx.strokeStyle = C.axis; ctx.beginPath(); ctx.moveTo(g.x0, ya); ctx.lineTo(g.x1, ya); ctx.stroke();
      text(ctx, "10 µeV", g.x0, ya + 13, { size: 11, mono: true, color: C.faint }); text(ctx, "20 MeV", g.x1, ya + 13, { size: 11, mono: true, color: C.faint, align: "right" });
      text(ctx, T("pl_E_log", "neutron energy (log scale)"), (g.x0 + g.x1) / 2, g.narrow ? ya + 30 : ya + 13, { size: 11, color: C.faint, align: "center" });
      [0.42, 0.62].forEach((f) => { const xx = g.x0 + f * (g.x1 - g.x0); ctx.save(); ctx.setLineDash([3, 4]); ctx.strokeStyle = "rgba(200,210,240,.25)"; ctx.beginPath(); ctx.moveTo(xx, g.top - 8); ctx.lineTo(xx, ya); ctx.stroke(); ctx.restore(); });
    },
    rowAt(x, y) { const g = endfGeom(viz.W), i = Math.floor((y - g.top + 3) / g.rh); return i >= 0 && i < ENDF.length ? i : -1; },
    move(x, y) { const i = this.rowAt(x, y); if (i !== EN.hov) { EN.hov = i; vcv.style.cursor = i >= 0 ? "pointer" : "default"; this.draw(); } },
    leave() { EN.hov = -1; this.draw(); },
    down(x, y) { const i = this.rowAt(x, y); if (i >= 0) { EN.sel = i; this.setNote(); this.draw(); } },
  };

  // ---------- stage 4: Doppler broadening ----------
  const DS = { T: 293.6 };
  VIZ.dop = {
    height: (W) => (W < 520 ? 300 : 330),
    init(box) {
      box.style.setProperty("--c", C.proc);
      const fmtT = (v) => (v < 0.5 ? "0 K" : (Math.abs(v - 293.6) < 0.05 ? "293.6" : String(Math.round(v))) + " K");
      this.r = rng(T("pl_temp", "temperature"), 0, 1500, 0.1, DS.T, fmtT, (v) => { DS.T = v; this.cache = null; this.upd(); });
      this.r.querySelector("input").setAttribute("list", "pl-tlist");
      const dl = el("datalist"); dl.id = "pl-tlist"; [0, 293.6, 600, 900].forEach((v) => { const o = document.createElement("option"); o.value = v; dl.appendChild(o); });
      this.sg = seg([[0, "0 K"], [293.6, "293.6 K"], [600, "600 K"], [900, "900 K"]], DS.T, (v) => { DS.T = v; this.r.set(v); this.cache = null; this.upd(); }, C.proc);
      this.read = el("div", "pl-read"); box.append(this.sg, this.r, dl, this.read); this.cache = null; this.upd(true);
    },
    curve() { if (!this.cache || this.cache.T !== DS.T) this.cache = { T: DS.T, s: P.doppler(DS.T) }; return this.cache.s; },
    upd(noDraw) {
      const s = this.curve(); let pk = 0, a0 = 0, a1 = 0; for (let i = 0; i < s.length; i++) { pk = Math.max(pk, s[i]); a0 += DOP.s0[i]; a1 += s[i]; }
      this.read.innerHTML = `<span>${T("pl_peak", "peak")} <b>×${fmt(pk, 2)}</b></span><span>${T("pl_width", "width")} <b>${fmt(P.fwhm(s) * 1000, 0)} meV</b></span><span>${T("pl_area", "area")} <b>×${fmt(a1 / a0, 2)}</b></span><span>${T("pl_dw", "Doppler width")} <b>${fmt(P.dopWidth(DS.T) * 1000, 0)} meV</b></span>`;
      if (!noDraw) this.draw();
    },
    draw() {
      const { ctx, W, H } = viz; ctx.clearRect(0, 0, W, H); const narrow = W < 520;
      const L = narrow ? 40 : 48, R = 14, top = 40, bot = 40, x0 = DOP.E0 - 0.3, x1 = DOP.E0 + 0.3;
      const a = { x0: L, x1: W - R, y0: top, y1: H - bot, x: (E) => L + ((E - x0) / (x1 - x0)) * (W - L - R), y: (v) => H - bot - (v / 1.08) * (H - bot - top) };
      frame(ctx, a, [6.4, 6.5, 6.6, 6.7, 6.8, 6.9].map((E) => [E, E.toFixed(1)]), [[0, "0"], [0.25, "0.25"], [0.5, "0.5"], [0.75, "0.75"], [1, "1"]], { ylab: T("pl_dop_y", "cross section, relative to the 0 K peak") });
      text(ctx, T("pl_E_x", "neutron energy (eV)"), a.x1, H - 12, { size: 11, color: C.faint, align: "right" });
      const pts = (s) => { const out = []; for (let i = 0; i < DOP.n; i += 2) { const E = DOP.E[i]; if (E >= x0 && E <= x1) out.push([a.x(E), a.y(s[i])]); } return out; };
      const p0 = pts(DOP.s0), s = this.curve(), p1 = pts(s);
      line(ctx, p0, C.soft, 1.3, [4, 4], 0.75);
      if (DS.T >= 0.5) {
        const gr = ctx.createLinearGradient(0, a.y0, 0, a.y1); gr.addColorStop(0, rgba(C.proc, 0.45)); gr.addColorStop(1, rgba(C.proc, 0.02));
        ctx.fillStyle = gr; ctx.beginPath(); ctx.moveTo(p1[0][0], a.y1); p1.forEach(([x, y]) => ctx.lineTo(x, y)); ctx.lineTo(p1[p1.length - 1][0], a.y1); ctx.closePath(); ctx.fill();
        ctx.save(); ctx.shadowColor = rgba(C.proc, 0.8); ctx.shadowBlur = 12; line(ctx, p1, C.proc, 2.4); ctx.restore();
      }
      let pk = 0; for (let i = 0; i < s.length; i++) pk = Math.max(pk, s[i]);
      text(ctx, DS.T < 0.5 ? T("pl_dop_0", "0 K: nuclei at rest") : (Math.abs(DS.T - 293.6) < 0.05 ? "293.6" : Math.round(DS.T)) + " K", a.x(DOP.E0) + 10, a.y(Math.min(1, pk)) - 2, { size: 12.5, weight: 600, color: DS.T < 0.5 ? C.ink : C.proc });
      text(ctx, T("pl_dop_ref", "0 K"), a.x(DOP.E0) - 8, a.y(1) - 10, { size: 11.5, color: C.soft, align: "right" });
    },
  };

  // ---------- stage 5: the res-v0.1 files ----------
  const LIB = [
    { s: "Fe", a: 56, m: "Fe56", tier: "STRICT", own: T("pl_l_fe", "own Reich–Moore fit to raw EXFOR") },
    { s: "Ni", a: 58, m: "Ni58", tier: "STRICT", own: T("pl_l_ni", "own Reich–Moore fit to raw EXFOR") },
    { s: "Zr", a: 90, m: "Zr90", tier: "STRICT", own: T("pl_l_zr90", "own Reich–Moore fit to raw EXFOR") },
    { s: "Cu", a: 65, m: "Cu65", tier: "PROVISIONAL", own: T("pl_l_cu", "own Reich–Moore fit to raw EXFOR") },
    { s: "Gd", a: 155, m: "Gd155", tier: "STRICT", own: T("pl_l_gd", "own Reich–Moore fit to raw GELINA + J-PARC data") },
    { s: "F", a: 19, m: "F19", tier: "STRICT", own: T("pl_l_f", "own statistical resonances, thermal refit") },
    { s: "Na", a: 23, m: "Na23", tier: "STRICT", own: T("pl_l_na", "own statistical resonances, thermal refit") },
  ];
  const LS = { sel: 0, hov: -1 };
  function libGeom(W) { const cols = W < 640 ? 4 : 7, m = 14, gap = W < 520 ? 10 : 14, tw = (W - 2 * m - (cols - 1) * gap) / cols, th = W < 520 ? 82 : 96; return { cols, m, gap, tw, th, top: 14 }; }
  VIZ.lib = {
    height: (W) => { const g = libGeom(W); return g.top * 2 + Math.ceil(LIB.length / g.cols) * (g.th + g.gap) - g.gap; },
    init(box) { this.note = el("p", "pl-note"); this.pre = el("pre", "pl-pre"); box.append(this.note, this.pre); this.setNote(); },
    setNote() {
      const f = LIB[LS.sel];
      this.note.innerHTML = `<b>${f.s}-${f.a}</b> · ${f.tier} · ${esc(f.own)}`;
      this.pre.textContent = `<library materials="${f.m}" path="${f.m}.h5" type="neutron" />`;
    },
    rect(i, W) { const g = libGeom(W), c = i % g.cols, r = Math.floor(i / g.cols); return { x: g.m + c * (g.tw + g.gap), y: g.top + r * (g.th + g.gap), w: g.tw, h: g.th }; },
    draw() {
      const { ctx, W, H } = viz; ctx.clearRect(0, 0, W, H); const small = W < 520;
      LIB.forEach((f, i) => {
        const b = this.rect(i, W), wd = false, sel = i === LS.sel, hov = i === LS.hov, col = wd ? C.judge : f.tier === "STRICT" ? C.lib : C.proc;
        ctx.save(); if (sel) { ctx.shadowColor = rgba(col, 0.6); ctx.shadowBlur = 18; }
        rrect(ctx, b.x, b.y, b.w, b.h, 12); const gr = ctx.createLinearGradient(b.x, b.y, b.x + b.w, b.y + b.h);
        gr.addColorStop(0, wd ? "rgba(60,40,52,.55)" : rgba(col, sel ? 0.42 : 0.24)); gr.addColorStop(1, "rgba(10,16,34,.9)"); ctx.fillStyle = gr; ctx.fill(); ctx.restore();
        rrect(ctx, b.x, b.y, b.w, b.h, 12); ctx.strokeStyle = sel ? col : hov ? rgba(col, 0.75) : C.panel; ctx.lineWidth = sel ? 2 : 1.2; ctx.stroke();
        const cx = b.x + b.w / 2, sz = small ? 22 : 28;
        ctx.font = font(sz, 600); const sw = ctx.measureText(f.s).width; ctx.font = font(small ? 11 : 12, 500, true); const aw = ctx.measureText(String(f.a)).width;
        const x0 = cx - (sw + aw + 2) / 2, yb = b.y + b.h * 0.46;
        text(ctx, String(f.a), x0, yb - sz * 0.38, { size: small ? 11 : 12, mono: true, color: wd ? C.faint : C.soft });
        text(ctx, f.s, x0 + aw + 2, yb, { size: sz, weight: 600, color: wd ? "rgba(232,236,243,.45)" : "#fff" });
        text(ctx, f.tier, cx, b.y + b.h - (small ? 14 : 17), { size: small ? 9.5 : 10.5, weight: 600, color: col, align: "center", max: b.w - 8 });
        if (wd) { ctx.save(); ctx.strokeStyle = rgba(C.judge, 0.7); ctx.lineWidth = 2; ctx.beginPath(); ctx.moveTo(b.x + 12, b.y + b.h - 28); ctx.lineTo(b.x + b.w - 12, b.y + 14); ctx.stroke(); ctx.restore(); }
      });
    },
    at(x, y) { return LIB.findIndex((_, i) => { const b = this.rect(i, viz.W); return x >= b.x && x <= b.x + b.w && y >= b.y && y <= b.y + b.h; }); },
    move(x, y) { const i = this.at(x, y); if (i !== LS.hov) { LS.hov = i; vcv.style.cursor = i >= 0 ? "pointer" : "default"; this.draw(); } },
    leave() { LS.hov = -1; this.draw(); },
    down(x, y) { const i = this.at(x, y); if (i >= 0) { LS.sel = i; this.setNote(); this.draw(); } },
  };

  // ---------- stage 6: one real critical experiment, measured vs simulated ----------
  // Per case, from research/rl/resinteg/out/arms/<arm>.json (the source of the res-v0.1 README's DEV column):
  // [plain name, kind (u uranium / m plutonium-uranium oxide), E (measured k), sE (pcm), standard library k − E (pcm, same-machine
  //  control), with our file k − E (pcm), change in |k − E| (pcm; ±35 pcm is the simulation's own noise), ICSBEP case, moderator]
  const BENCH = {
    "Fe-56": [["Uranium rods #1", "u", 1.0007, 120, 38.6, -26.4, -12, "LEU-COMP-THERM-008 case 1", "water with 1511 ppm boron"], ["Uranium rods #2", "u", 1.0007, 120, 3.0, -0.9, -2, "LEU-COMP-THERM-008 case 5", "water with 1182 ppm boron"], ["Uranium rods #3", "u", 1.0007, 120, 99.7, 122.0, 22, "LEU-COMP-THERM-008 case 11", "water with 1384 ppm boron"],
      ["Plutonium-uranium rods #1", "m", 1.0024, 600, -377.8, -334.8, -43, "MIX-COMP-THERM-002 PNL-30", "water, almost no boron"], ["Plutonium-uranium rods #2", "m", 1.0024, 240, 116.5, 94.0, -22, "MIX-COMP-THERM-002 PNL-33", "borated water"], ["Plutonium-uranium rods #3", "m", 1.0029, 270, 99.2, 54.7, -45, "MIX-COMP-THERM-002 PNL-35", "borated water"]],
    "Ni-58": [["Plutonium-uranium rods #1", "m", 1.0024, 600, -373.1, -361.2, -12, "MIX-COMP-THERM-002 PNL-30", "water, almost no boron"], ["Plutonium-uranium rods #2", "m", 1.0024, 240, 125.6, 119.3, -6, "MIX-COMP-THERM-002 PNL-33", "borated water"], ["Plutonium-uranium rods #3", "m", 1.0029, 270, 99.2, 6.2, -93, "MIX-COMP-THERM-002 PNL-35", "borated water"]],
    "Zr-90": [["Plutonium-uranium rods #1", "m", 1.0024, 600, -373.1, -441.3, 68, "MIX-COMP-THERM-002 PNL-30", "water, almost no boron"], ["Plutonium-uranium rods #2", "m", 1.0024, 240, 125.6, 129.6, 4, "MIX-COMP-THERM-002 PNL-33", "borated water"], ["Plutonium-uranium rods #3", "m", 1.0029, 270, 99.2, -4.2, -95, "MIX-COMP-THERM-002 PNL-35", "borated water"]],
    "Na-23": [["Uranium rods #2", "u", 1.0007, 120, 0.4, 33.2, 33, "LEU-COMP-THERM-008 case 5", "water with 1182 ppm boron"]],
  };
  const BS = { nuc: "Fe-56", ci: 0, std: 38.6, own: -26.4, span: 200, raf: 0 };
  const verdict = (w) => (Math.abs(w) <= 35 ? ["same", C.nc] : w < 0 ? ["closer", C.win] : ["farther", C.loss]);
  const spanFor = (r) => { const need = Math.max(r[3] * 1.35, Math.abs(r[4]) * 1.3, Math.abs(r[5]) * 1.3, 60); return [100, 150, 200, 300, 400, 500, 600, 800].find((s) => s >= need) || 1000; };
  function rods(ctx, cx, cy, R, kind) { // a top view of a lattice of fuel rods in a water tank
    ctx.save(); ctx.beginPath(); ctx.arc(cx, cy, R, 0, 7);
    const w = ctx.createRadialGradient(cx, cy - R * 0.3, R * 0.1, cx, cy, R); w.addColorStop(0, "rgba(95,176,255,.30)"); w.addColorStop(1, "rgba(30,70,140,.18)");
    ctx.fillStyle = w; ctx.fill(); ctx.strokeStyle = "rgba(95,176,255,.55)"; ctx.lineWidth = 1.5; ctx.stroke(); ctx.clip();
    const p = R / 4.2, col = kind === "m" ? "#f5c04d" : "#ff9b55";
    for (let i = -4; i <= 4; i++) for (let j = -4; j <= 4; j++) {
      const x = cx + i * p, y = cy + j * p; if (Math.hypot(x - cx, y - cy) > R * 0.72) continue;
      const g = ctx.createRadialGradient(x - p * 0.12, y - p * 0.12, 0, x, y, p * 0.36); g.addColorStop(0, "#fff"); g.addColorStop(0.35, col); g.addColorStop(1, rgba(col, 0.55));
      ctx.fillStyle = g; ctx.beginPath(); ctx.arc(x, y, p * 0.34, 0, 7); ctx.fill();
    }
    ctx.restore();
  }
  VIZ.bench = {
    height: (W) => (W < 600 ? 336 : 260),
    init(box) {
      const cases = el("div", "pl-ctlrow");
      const fill = () => { cases.innerHTML = ""; cases.append(seg(BENCH[BS.nuc].map((r, i) => [i, r[0], r[7], r[1] === "m" ? "#f5c04d" : "#ff9b55"]), BS.ci, (i) => this.go(i), C.bench)); };
      box.append(seg(Object.keys(BENCH).map((n) => [n, n]), BS.nuc, (n) => { BS.nuc = n; fill(); this.go(0); }, C.lib), cases);
      fill(); this.go(BS.ci, true);
    },
    go(i, now) {
      BS.ci = i; const r = BENCH[BS.nuc][i], to = { std: r[4], own: r[5], span: spanFor(r) }, from = { std: BS.std, own: BS.own, span: BS.span };
      if (BS.raf) cancelAnimationFrame(BS.raf);
      if (now || RM) { Object.assign(BS, to); return now ? null : this.draw(); }
      const t0 = performance.now();
      const step = (tn) => { const t = clamp((tn - t0) / 450, 0, 1), e = t * t * (3 - 2 * t); ["std", "own", "span"].forEach((k) => (BS[k] = from[k] + (to[k] - from[k]) * e)); this.draw(); BS.raf = t < 1 ? requestAnimationFrame(step) : 0; };
      BS.raf = requestAnimationFrame(step);
    },
    stop() { if (BS.raf) cancelAnimationFrame(BS.raf); BS.raf = 0; const r = BENCH[BS.nuc][BS.ci]; BS.std = r[4]; BS.own = r[5]; BS.span = spanFor(r); },
    draw() {
      const { ctx, W, H } = viz; ctx.clearRect(0, 0, W, H); const narrow = W < 600, r = BENCH[BS.nuc][BS.ci];
      // the experiment
      const R = narrow ? 50 : 66, icx = narrow ? W / 2 : 34 + R, icy = narrow ? 16 + R : H / 2 - 22;
      rods(ctx, icx, icy, R, r[1]);
      text(ctx, r[0], icx, icy + R + 16, { size: 12.5, weight: 600, color: C.ink, align: "center" });
      text(ctx, r[1] === "m" ? T("pl_b_mox", "plutonium-uranium oxide fuel rods") : T("pl_b_leu", "uranium fuel rods, 2.46 % U-235"), icx, icy + R + 33, { size: 11.5, color: C.soft, align: "center" });
      text(ctx, T("pl_b_mod_" + r[7].replace(/\W+/g, ""), "in " + r[8]), icx, icy + R + 49, { size: 11.5, color: C.soft, align: "center" });
      // the gauge: simulated k − measured k, in % of k
      const gx0 = narrow ? 24 : icx + R + 90, gx1 = W - 24, gy = narrow ? icy + R + 124 : H / 2 - 4, mid = (gx0 + gx1) / 2;
      const gx = (pcm) => mid + (pcm / BS.span) * ((gx1 - gx0) / 2);
      const [vt, vc] = verdict(r[6]);
      pill(ctx, vt, gx1, narrow ? 18 : 26, vc, { align: "right", size: 13 });
      // experiment's own uncertainty
      const b0 = gx(-r[3]), b1 = gx(r[3]); const bg = ctx.createLinearGradient(b0, 0, b1, 0);
      bg.addColorStop(0, "rgba(235,240,255,0)"); bg.addColorStop(0.5, "rgba(235,240,255,.16)"); bg.addColorStop(1, "rgba(235,240,255,0)");
      ctx.fillStyle = bg; rrect(ctx, Math.max(gx0, b0), gy - 16, Math.min(gx1, b1) - Math.max(gx0, b0), 32, 8); ctx.fill();
      ctx.strokeStyle = "rgba(235,240,255,.28)"; ctx.lineWidth = 1; [b0, b1].forEach((x) => { if (x > gx0 && x < gx1) { ctx.beginPath(); ctx.moveTo(x, gy - 14); ctx.lineTo(x, gy + 14); ctx.stroke(); } });
      text(ctx, T("pl_b_unc", "shaded: measurement uncertainty"), mid, gy + (narrow ? 72 : 54), { size: 10.5, color: C.faint, align: "center" });
      ctx.strokeStyle = C.axis; ctx.lineWidth = 1.5; ctx.beginPath(); ctx.moveTo(gx0, gy); ctx.lineTo(gx1, gy); ctx.stroke();
      const st = BS.span / 2; [-BS.span, -st, 0, st, BS.span].forEach((v) => { const x = gx(v); ctx.strokeStyle = v === 0 ? "rgba(235,240,255,.9)" : "rgba(150,170,220,.35)"; ctx.lineWidth = v === 0 ? 2 : 1; ctx.beginPath(); ctx.moveTo(x, gy - (v === 0 ? 10 : 5)); ctx.lineTo(x, gy + (v === 0 ? 10 : 5)); ctx.stroke();
        if (v !== 0) text(ctx, (v > 0 ? "+" : "−") + fmt(Math.abs(v) / 1000, Math.abs(v) / 1000 < 0.1 ? 3 : 2) + " %", x, gy + 36, { size: 10.5, mono: true, color: C.faint, align: "center" }); });
      text(ctx, T("pl_b_meas", "measured"), mid, gy - 38, { size: 12.5, weight: 600, color: "#fff", align: "center" });
      text(ctx, T("pl_b_low", "simulation too low"), gx0, gy + 54, { size: 11, color: C.faint });
      text(ctx, T("pl_b_high", "too high"), gx1, gy + 54, { size: 11, color: C.faint, align: "right" });
      // the two markers
      const xs = gx(clamp(BS.std, -BS.span, BS.span)), xo = gx(clamp(BS.own, -BS.span, BS.span));
      ctx.save(); ctx.strokeStyle = rgba(C.lib, 0.6); ctx.setLineDash([3, 3]); ctx.beginPath(); ctx.moveTo(xs, gy); ctx.lineTo(xo, gy); ctx.stroke(); ctx.restore();
      ctx.save(); ctx.translate(xs, gy); ctx.rotate(Math.PI / 4); ctx.fillStyle = "#c9d2e6"; ctx.fillRect(-5, -5, 10, 10); ctx.restore();
      glowDot(ctx, xo, gy, 5, C.lib);
      const lo = narrow ? 11 : 12, labS = T("pl_b_std", "standard library"), labO = T("pl_b_own", "with our file");
      // our file's label above the line, the standard library's below it (different rows, so they never collide)
      const cl = (x) => clamp(x, gx0 + 56, gx1 - 56);
      text(ctx, labO, cl(xo), gy - 19, { size: lo, weight: 600, color: C.lib, align: "center" });
      text(ctx, labS, cl(xs), gy + 20, { size: lo, color: "#c9d2e6", align: "center" });
    },
  };

  // ---------- stage 7: the EXFOR-only judge, worked example Na-23 (res-v0.1 README: PASS; value = file ÷ EXFOR) ----------
  const NA23 = [[T("pl_j_cap", "thermal capture"), "0.975"], [T("pl_j_el", "thermal elastic"), "1.04"], [T("pl_j_ri", "capture resonance integral"), "0.996"]];
  VIZ.judge = {
    height: (W) => (W < 560 ? 344 : 284),
    init() {},
    draw() {
      const { ctx, W, H } = viz; ctx.clearRect(0, 0, W, H); const narrow = W < 560;
      text(ctx, T("pl_j_head", "Na-23 in res-v0.1"), 16, 24, { size: 15, weight: 600, color: "#fff" });
      pill(ctx, T("pl_pass", "PASS"), W - 16, 24, C.win, { align: "right", size: 11.5 });
      text(ctx, T("pl_j_sub", "file ÷ EXFOR reference"), 16, 46, { size: 12, color: C.soft });
      const rh = narrow ? 90 : 68, top = 64, lab = narrow ? 0 : 210, gx0 = narrow ? 30 : 16 + lab, gx1 = W - (narrow ? 30 : 150);
      const gx = (r) => gx0 + ((r - 0.9) / 0.2) * (gx1 - gx0);
      NA23.forEach(([name, vs], i) => {
        const y = top + i * rh, v = parseFloat(vs), gy = narrow ? y + 46 : y + rh / 2 - 4;
        ctx.fillStyle = "rgba(150,170,230,.05)"; rrect(ctx, 8, y + 4, W - 16, rh - 8, 10); ctx.fill();
        text(ctx, name, 18, narrow ? y + 22 : gy, { size: 13, weight: 600, color: C.ink, max: narrow ? W - 110 : lab - 10 });
        // the ratio axis 0.90 … 1.10, exact agreement marked
        const g = ctx.createLinearGradient(gx0, 0, gx1, 0); g.addColorStop(0, "rgba(63,211,168,0)"); g.addColorStop(0.5, "rgba(63,211,168,.3)"); g.addColorStop(1, "rgba(63,211,168,0)");
        ctx.fillStyle = g; rrect(ctx, gx0, gy - 3, gx1 - gx0, 6, 3); ctx.fill();
        [0.9, 0.95, 1, 1.05, 1.1].forEach((t) => { const x = gx(t); ctx.strokeStyle = t === 1 ? "rgba(235,240,255,.75)" : "rgba(150,170,220,.3)"; ctx.lineWidth = t === 1 ? 1.5 : 1; ctx.beginPath(); ctx.moveTo(x, gy - (t === 1 ? 9 : 5)); ctx.lineTo(x, gy + (t === 1 ? 9 : 5)); ctx.stroke(); text(ctx, t.toFixed(2), x, gy + 17, { size: 10, mono: true, color: C.faint, align: "center" }); });
        glowDot(ctx, gx(v), gy, 4, C.win);
        if (narrow) text(ctx, vs + "  ✓", W - 18, y + 22, { size: 14, mono: true, weight: 600, color: "#fff", align: "right" });
        else { text(ctx, vs, W - 64, gy, { size: 15, mono: true, weight: 600, color: "#fff", align: "right" }); text(ctx, "✓", W - 32, gy, { size: 16, weight: 600, color: C.win, align: "center" }); }
      });
    },
  };

  // ===================================================================================================================
  // start
  // ===================================================================================================================
  const start = Math.max(0, STAGES.findIndex((s) => "#" + s.id === location.hash));
  layoutFlow(); cur = start; select(start);
  let rt = 0, lastW = 0;
  const onResize = () => { cancelAnimationFrame(rt); rt = requestAnimationFrame(() => { layoutFlow(); if (vW() !== lastW) { lastW = vW(); sizeViz(); } }); };
  if (window.ResizeObserver) new ResizeObserver(onResize).observe(document.querySelector(".pl")); else addEventListener("resize", onResize);
  if (document.fonts && document.fonts.ready) document.fonts.ready.then(() => { layoutFlow(); sizeViz(); });
})();
