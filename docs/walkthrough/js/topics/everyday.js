/* Nuclear in everyday life. Scenes (S.mode):
 *   "pet"   = a PET scanner ring around a body cross-section. Fluorine-18: half-life 109.77 min (NNDC NuDat 3 / ENSDF;
 *             NUBASE2020 agrees to 0.1 %), decays by positron emission (96.9 %) or electron capture. The positron travels
 *             ~0.6 mm in tissue (mean; Cherry, Sorenson & Phelps, Physics in Nuclear Medicine, 4th ed. 2012, ch. 18), then
 *             annihilates with an electron into two 511 keV photons (m_e c^2 = 510.999 keV, CODATA 2018) going almost exactly
 *             opposite ways (spread ~0.25 deg FWHM, ibid.). The ring records a pair seen within a few ns as one coincidence;
 *             the line between the two detectors (line of response) passes through the decay. Lines are summed here by plain
 *             back-projection, so the hot spot shows as the place where lines cross. Some tracer also spreads through the
 *             whole body (drawn as 12 % of decays, illustrative); photon speed slowed down by many orders of magnitude.
 *   "rt"    = external-beam radiotherapy, a cross-section with a tumour and the spinal cord. Each beam's dose falls with
 *             depth as exp(-mu d), mu = 0.05 /cm, roughly a 6 MV X-ray beam past its build-up depth (depth dose about 67 %
 *             at 10 cm; Khan & Gibbons, The Physics of Radiation Therapy, 5th ed. 2014, ch. 9-10). Body 34 cm wide; build-up,
 *             scatter and beam divergence left out. Dose is relative to the tumour centre (100 %). Illustration of the
 *             principle (crossfire from several angles), not a treatment plan.
 *   "tc"    = technetium-99m: half-life 6.007 h, a 140.5 keV gamma ray in 89 % of decays (NNDC NuDat 3 / ENSDF). Made in
 *             a generator from molybdenum-99, half-life 65.98 h (ibid.; see the `chains` lesson, step 3). Tc-99m is used
 *             in about 80 % of diagnostic nuclear-medicine scans, tens of millions a year (OECD-NEA, The Supply of Medical
 *             Radioisotopes, 2019). Curve = physical decay only (the body also clears some of the tracer). A gamma camera's
 *             collimator passes only photons travelling straight at it. Figure and uptake pattern (a bone scan) illustrative.
 *   "c14"   = radiocarbon: carbon-14 half-life 5730 +/- 40 y (the "Cambridge" value, Godwin 1962, Nature 195:984); the
 *             current evaluation is 5700 +/- 30 y (NNDC NuDat 3 / ENSDF, NUBASE2020), 0.5 % shorter. Laboratories quote
 *             "radiocarbon years" with the conventional Libby half-life 5568 y and then calibrate against tree rings
 *             (IntCal20), because atmospheric C-14 was not constant. About 1.2 C-14 atoms per 10^12 carbon atoms in living
 *             things. Practical limit about 50,000 years. Otzi the Iceman: about 5,300 years old (radiocarbon, Bonani et
 *             al. 1994, Radiocarbon 36:247). Atom grid: each atom gets a decay time from evenly spaced quantiles, so the
 *             drawn count follows the curve.
 *   "smoke" = ionisation smoke detector: americium-241, half-life 432.6 y (NUBASE2020), alpha energy 5.486 MeV (ENSDF);
 *             typical source about 37 kBq (1 microcurie), about 0.3 micrograms, sealed in foil (World Nuclear Association,
 *             "Smoke Detectors and Americium", 2023; US NRC). A 5.5 MeV alpha travels about 4 cm in air (NIST ASTAR). The
 *             alphas ionise the air between two charged plates; the ions carry a small current. Smoke particles catch the
 *             ions, the current drops and the alarm sounds. Ion and particle counts and the alarm threshold illustrative.
 * Nothing here is a health claim beyond these standard facts. */
(function () {
  const { TAU, clamp, lerp, smooth, rng } = WT.util;
  const T_F18 = 109.77, T_TC = 6.007, T_MO = 65.98, T_C14 = 5730, T_AM = 432.6;
  const fmtN = (n) => Math.round(n).toLocaleString("en");
  const pct = (f) => (f >= 0.1 ? Math.round(f * 100) : f >= 0.01 ? (f * 100).toFixed(1) : (f * 100).toFixed(2)) + " %";
  const setIn = (k, v) => document.querySelectorAll(`#everyday [data-bind="${k}"]`).forEach((i) => (i.value = v));
  const setOut = (cls, s) => document.querySelectorAll(`#everyday .${cls}`).forEach((o) => { if (o.textContent !== s) o.textContent = s; });

  // ---------- PET ----------
  const ND = 72; // detector blocks around the ring
  const pet = { ev: [], acc: null, ax: null, aR: 0, fl: new Float32Array(ND), sp: 0, n: 0, q: rng(31), warm: false, mv: 0 };
  function petEvent(S, q) {
    let ox, oy;
    if (q() < 0.88) { const r = Math.sqrt(-2 * Math.log(q() + 1e-9)) * 0.03, a = q() * TAU; ox = S.hx + r * Math.cos(a); oy = S.hy + r * Math.sin(a); }
    else { do { ox = (q() * 2 - 1) * 0.66; oy = (q() * 2 - 1) * 0.48; } while ((ox / 0.66) ** 2 + (oy / 0.48) ** 2 > 1); }
    const a = q() * Math.PI, dx = Math.cos(a), dy = Math.sin(a), b = ox * dx + oy * dy, cc = ox * ox + oy * oy - 1, d = Math.sqrt(b * b - cc);
    return { ox, oy, dx, dy, tA: -b + d, tB: b + d, t: 0, hitA: false, hitB: false, done: false };
  }
  const detOf = (x, y) => Math.floor((((Math.atan2(y, x) % TAU) + TAU) % TAU) / TAU * ND) % ND;
  function petAccum(e, col) {
    const R = pet.aR, x = pet.ax, ax = e.ox + e.dx * e.tA, ay = e.oy + e.dy * e.tA, bx = e.ox - e.dx * e.tB, by = e.oy - e.dy * e.tB;
    x.strokeStyle = col; x.globalAlpha = 0.032; x.lineWidth = 1.4; x.beginPath(); x.moveTo(R + ax * R, R + ay * R); x.lineTo(R + bx * R, R + by * R); x.stroke();
  }

  // ---------- radiotherapy ----------
  const BRX = 0.8, BRY = 0.56, TUM = [0.22, -0.08], TR = 0.11, CORD = [0, 0.43], CR = 0.045, HW = 0.135, PEN = 0.025, MU = 0.05, CM = 17 / BRX;
  const rt = { key: "", cv: null, stats: null };
  function rtDose(px, py, beams) {
    let d = 0;
    for (const [ux, uy] of beams) {
      const rx = px - TUM[0], ry = py - TUM[1], perp = Math.abs(-uy * rx + ux * ry);
      if (perp > HW + PEN) continue;
      const f = 1 - smooth(HW - PEN, HW + PEN, perp);
      const A = ux * ux / (BRX * BRX) + uy * uy / (BRY * BRY), B = 2 * (px * ux / (BRX * BRX) + py * uy / (BRY * BRY)), C = px * px / (BRX * BRX) + py * py / (BRY * BRY) - 1;
      const s = (-B + Math.sqrt(Math.max(0, B * B - 4 * A * C))) / (2 * A); // distance to the skin, towards the beam's source
      d += f * Math.exp(-MU * s * CM);
    }
    return d;
  }
  function rtMap(c, n, rot) {
    const GW = 120, GH = Math.round(GW * BRY / BRX);
    if (!rt.cv) { rt.cv = document.createElement("canvas"); rt.cv.width = GW; rt.cv.height = GH; }
    const beams = []; for (let k = 0; k < n; k++) { const a = rot + k * TAU / n; beams.push([Math.cos(a), Math.sin(a)]); }
    const d0 = rtDose(TUM[0], TUM[1], beams), x = rt.cv.getContext("2d"), im = x.createImageData(GW, GH);
    const stops = [[0, WT.rgb01(c.cool)], [0.35, WT.rgb01(c.fission)], [0.65, WT.rgb01(c.photon)], [1, WT.rgb01(c.proton)]];
    let hmax = 0;
    for (let j = 0; j < GH; j++) for (let i = 0; i < GW; i++) {
      const px = ((i + 0.5) / GW * 2 - 1) * BRX, py = ((j + 0.5) / GH * 2 - 1) * BRY; if ((px / BRX) ** 2 + (py / BRY) ** 2 > 1) continue;
      const v = rtDose(px, py, beams) / d0, k = (j * GW + i) * 4;
      if (Math.hypot(px - TUM[0], py - TUM[1]) > TR + 0.06) hmax = Math.max(hmax, v);
      const t = clamp(v, 0, 1); let s = 0; while (s < stops.length - 2 && t > stops[s + 1][0]) s++;
      const [t0, c0] = stops[s], [t1, c1] = stops[s + 1], u = clamp((t - t0) / (t1 - t0), 0, 1);
      im.data[k] = 255 * lerp(c0[0], c1[0], u); im.data[k + 1] = 255 * lerp(c0[1], c1[1], u); im.data[k + 2] = 255 * lerp(c0[2], c1[2], u);
      im.data[k + 3] = 255 * 0.85 * smooth(0.03, 0.3, v);
    }
    x.putImageData(im, 0, 0);
    rt.stats = { cord: rtDose(CORD[0], CORD[1], beams) / d0, hmax, beams };
  }

  // ---------- technetium ----------
  const tc = { ph: [], sp: 0, q: rng(7), fl: [] };
  const SPOTS = [[0.06, 0, 1.2], [0.2, 0, 1], [0.3, 0, 1], [0.4, 0, 1], [0.5, 0, 1.4], [0.24, -0.5, 0.8], [0.24, 0.5, 0.8], [0.7, -0.22, 0.9], [0.7, 0.22, 0.9], [0.92, -0.2, 0.7], [0.92, 0.2, 0.7]]; // skull, spine, shoulders, pelvis, knees, ankles

  // ---------- carbon-14 ----------
  const C14 = { q: rng(3), times: null, n: 0, prev: null, fl: [] };
  function c14Atoms(n) {
    if (C14.n === n) return; C14.n = n; const u = []; for (let i = 0; i < n; i++) u.push((i + 0.5) / n);
    const q = rng(77); for (let i = n - 1; i > 0; i--) { const j = Math.floor(q() * (i + 1)); [u[i], u[j]] = [u[j], u[i]]; }
    C14.times = u.map((v) => -T_C14 * Math.log2(v)); C14.prev = null;
    C14.jit = u.map(() => [q() * TAU, 0.6 + q()]);
  }

  // ---------- smoke detector ----------
  const SM = { al: [], ion: [], blob: [], sp: 0, rate: 0, q: rng(12), fl: [], warm: false, ripple: 0 };
  const AL_RATE = 5, PAIRS = 9;

  WT.chapter("everyday", {
    level: 0, num: "Lesson 4", title: "Nuclear in everyday life", short: "Everyday",
    html: `
<div class="step">
  <h3>PET scans</h3>
  <p>A fluorine-18 tracer (half-life 110 minutes) emits positrons, and each one turns into two 511 keV gamma rays flying apart back to back. Drag the hot spot: the ring draws a line for every pair, and the lines cross where the tracer is.</p>
</div>
<div class="step">
  <h3>Radiotherapy</h3>
  <p>Beams from several directions overlap on the tumour, so it gets the full dose while each path through healthy tissue gets only a share. Drag to turn the beams and keep them off the spinal cord.</p>
  <div class="ctl"><label for="ev-n">Beams</label><input id="ev-n" type="range" data-bind="nb" data-instant min="1" max="7" step="1" value="5"><output data-show="nb" data-fmt="0"></output></div>
  <div class="ctl"><label for="ev-r">Turn</label><input id="ev-r" type="range" data-bind="rotd" data-instant min="0" max="360" step="1" value="20"><output class="ev-rot"></output></div>
</div>
<div class="step">
  <h3>Technetium-99m</h3>
  <p>The isotope behind most nuclear-medicine scans gives off a 140 keV gamma ray that a camera outside the body can see, and with a 6-hour half-life little is left after a day. Hospitals <a href="#chains-3">milk it from molybdenum-99</a>.</p>
  <div class="ctl"><label for="ev-t">Hours after the dose</label><input id="ev-t" type="range" data-bind="th" data-instant min="0" max="48" step="0.5" value="0"><output data-show="th" data-fmt="1"></output></div>
</div>
<div class="step">
  <h3>Carbon dating</h3>
  <p>Living things keep taking in carbon-14; after death it decays with a half-life of 5,730 years. Set the age, or measure what is left to read the age.</p>
  <div class="ctl"><label for="ev-a">Age (years)</label><input id="ev-a" type="range" data-bind="age" data-instant min="0" max="50000" step="10" value="5300"><output class="ev-age"></output></div>
  <div class="ctl"><label for="ev-f">Carbon-14 left (%)</label><input id="ev-f" type="range" data-bind="fr" data-instant min="0.3" max="100" step="0.1" value="52.7"><output class="ev-fr"></output></div>
</div>
<div class="step">
  <h3>Smoke detectors</h3>
  <p>A sealed speck of americium-241 sends alpha particles across a small air gap, making ions that carry a tiny current. Smoke catches the ions, the current drops, and the alarm sounds.</p>
  <div class="ctl"><label for="ev-s">Smoke</label><input id="ev-s" type="range" data-bind="sm" data-instant min="0" max="1" step="0.01" value="0"><output class="ev-sm"></output></div>
</div>`,
    setup(S) {
      S.set("mode", "pet"); S.set("hx", 0.28); S.set("hy", -0.14); S.set("nb", 5); S.set("rotd", 20); S.set("th", 0); S.set("age", 5300); S.set("fr", 52.7); S.set("sm", 0);
      S._pa = 5300; S._pf = 52.7; S._cv = null; S._drag = null;
    },
    steps: [
      (S) => { S.set("mode", "pet"); },
      (S) => { S.set("mode", "rt"); },
      (S) => { S.set("mode", "tc"); },
      (S) => { S.set("mode", "c14"); },
      (S) => { S.set("mode", "smoke"); const m = /[?&]evsm=([\d.]+)/.exec(location.search); if (m) S.set("sm", +m[1]); },
    ],
    frame(g, S, dt) {
      const { W, H, c, ctx } = g, phone = W < 600, fs = phone ? 11 : 13, snap = document.body.classList.contains("shot"), mode = S.mode;
      const cx = W / 2, cy = H * 0.47, R = Math.min(W * 0.38, H * 0.35);
      if (!S._cv && ctx.canvas) { S._cv = ctx.canvas; WT.grab(S._cv, {
        down: (x, y) => {
          const m = S.mode, G = S._geo; if (!G) return false;
          if (m === "pet") { const u = (x - G.cx) / G.R, v = (y - G.cy) / G.R; if (Math.hypot(u, v) > 1) return false; S._drag = "pet"; petMove(u, v); return true; }
          if (m === "rt") { if (Math.hypot(x - G.cx, y - G.cy) > G.R * 1.25) return false; S._drag = { a: Math.atan2(y - G.cy, x - G.cx), r: S.rotd }; return true; }
          if ((m === "tc" || m === "c14") && G.ch) { const P = G.ch; if (x < P.x0 - 20 || x > P.x1 + 20 || y < P.y0 - 20 || y > P.y1 + 20) return false; S._drag = m; chartSet(x); return true; }
          return false;
        },
        move: (x, y) => {
          const G = S._geo, d = S._drag; if (!G || !d) return;
          if (d === "pet") petMove((x - G.cx) / G.R, (y - G.cy) / G.R);
          else if (d === "tc" || d === "c14") chartSet(x);
          else if (d.a != null) { const a = Math.atan2(y - G.cy, x - G.cx); let r = (d.r + (a - d.a) * 180 / Math.PI) % 360; if (r < 0) r += 360; S.set("rotd", r); }
        },
        up: () => { const d = S._drag; S._drag = null; if (d && d.a != null) setIn("rotd", Math.round(S.rotd)); },
        cancel: () => { S._drag = null; },
        hover: (x, y) => { const G = S._geo, m = S.mode; let cur = ""; if (G) {
          if (m === "pet" && Math.hypot(x - G.cx - S.hx * G.R, y - G.cy - S.hy * G.R) < 30) cur = "grab";
          else if (m === "pet" && Math.hypot(x - G.cx, y - G.cy) < G.R) cur = "crosshair";
          else if (m === "rt" && Math.hypot(x - G.cx, y - G.cy) < G.R * 1.25) cur = "grab";
          else if ((m === "tc" || m === "c14") && G.ch && x > G.ch.x0 - 10 && x < G.ch.x1 + 10 && y > G.ch.y0 - 10 && y < G.ch.y1 + 10) cur = "ew-resize"; }
          S._cv.style.cursor = cur; },
      }); }
      function petMove(u, v) { const r = Math.hypot(u / 0.6, v / 0.42); if (r > 1) { u /= r; v /= r; } S.set("hx", u); S.set("hy", v); pet.mv = 1; }
      function chartSet(x) {
        const P = S._geo.ch, f = clamp((x - P.x0) / (P.x1 - P.x0), 0, 1);
        if (S._drag === "tc") { const v = Math.round(f * 96) / 2; S.set("th", v); setIn("th", v); }
        else { const v = Math.round(f * 5000) * 10; S.set("age", v); }
      }
      S._geo = { cx, cy, R };

      // ================= PET =================
      if (mode === "pet") {
        const th = R * 0.085, Ri = Math.round(R);
        if (!pet.acc || pet.aR !== Ri) { pet.acc = document.createElement("canvas"); pet.acc.width = pet.acc.height = 2 * Ri; pet.ax = pet.acc.getContext("2d"); pet.aR = Ri; pet.warm = false; }
        if (!pet.warm) { pet.warm = true; const q = rng(5); const nw = snap ? 700 : 360; for (let i = 0; i < nw; i++) petAccum(petEvent(S, q), c.warm); pet.n += nw; }
        // fade the image (faster while the tracer is being moved) and add new decays
        pet.mv = Math.max(0, pet.mv - dt * 1.5);
        { const k = 1 - Math.exp(-dt * (0.12 + 2.2 * pet.mv)); const x = pet.ax; x.save(); x.globalCompositeOperation = "destination-out"; x.globalAlpha = k; x.fillStyle = "#000"; x.fillRect(0, 0, 2 * Ri, 2 * Ri); x.restore(); }
        pet.sp += dt * 16; while (pet.sp >= 1) { pet.sp -= 1; pet.ev.push(petEvent(S, pet.q)); }
        if (snap && !pet.snapped && (pet.snapped = true)) for (let i = 0; i < 8; i++) { const e = petEvent(S, rng(90 + i)); e.t = 0.12 + i * 0.14; pet.ev.push(e); }
        const speed = 1.1;
        // body cross-section: outline, lungs, spine
        g.glow(cx, cy, R * 1.3, c.accent, 0.08);
        ctx.save(); ctx.beginPath(); ctx.ellipse(cx, cy, R * 0.66, R * 0.48, 0, 0, TAU); ctx.fillStyle = g.rgba(c.warm, 0.1); ctx.fill(); ctx.strokeStyle = g.rgba(c.soft, 0.55); ctx.lineWidth = 1.5; ctx.stroke(); ctx.restore();
        [[-0.27, -0.05], [0.27, -0.05]].forEach(([u, v]) => { ctx.save(); ctx.beginPath(); ctx.ellipse(cx + u * R, cy + v * R, R * 0.17, R * 0.25, 0, 0, TAU); ctx.fillStyle = g.rgba(c.soft, 0.07); ctx.fill(); ctx.strokeStyle = g.rgba(c.soft, 0.22); ctx.stroke(); ctx.restore(); });
        g.ring(cx, cy + R * 0.33, R * 0.06, c.soft, 1.2, 0.35);
        // the image built from lines of response
        ctx.save(); ctx.beginPath(); ctx.arc(cx, cy, R, 0, TAU); ctx.clip(); ctx.globalAlpha = 0.95; ctx.drawImage(pet.acc, cx - Ri, cy - Ri, 2 * Ri, 2 * Ri); ctx.restore();
        // detector ring
        for (let i = 0; i < ND; i++) pet.fl[i] = Math.max(0, pet.fl[i] - dt * 2.5);
        const bw = TAU * R / ND * 0.78;
        for (let i = 0; i < ND; i++) {
          const a = (i + 0.5) / ND * TAU, f = pet.fl[i];
          ctx.save(); ctx.translate(cx + Math.cos(a) * (R + th / 2), cy + Math.sin(a) * (R + th / 2)); ctx.rotate(a);
          ctx.fillStyle = g.rgba(c.soft, 0.22); ctx.fillRect(-th / 2, -bw / 2, th, bw);
          if (f > 0) { ctx.fillStyle = g.rgba(c.photon, Math.min(1, f)); ctx.fillRect(-th / 2, -bw / 2, th, bw); }
          ctx.restore();
          if (f > 0.3) g.glow(cx + Math.cos(a) * (R + th / 2), cy + Math.sin(a) * (R + th / 2), th * 1.6, c.photon, 0.35 * f);
        }
        // decays in flight: two photons back to back, then the line of response
        const P = (e, s) => [cx + (e.ox + e.dx * s) * R, cy + (e.oy + e.dy * s) * R];
        for (const e of pet.ev) {
          e.t += dt * speed;
          const tm = Math.max(e.tA, e.tB);
          if (e.t < 0.08) g.glow(cx + e.ox * R, cy + e.oy * R, 12, "#ffffff", 0.7 * (1 - e.t / 0.08));
          if (e.t < e.tA) { const [x, y] = P(e, e.t); g.photon(x, y, Math.atan2(e.dy, e.dx), phone ? 12 : 16, 0.9); }
          else if (!e.hitA) { e.hitA = true; pet.fl[detOf(e.ox + e.dx * e.tA, e.oy + e.dy * e.tA)] = 1; }
          if (e.t < e.tB) { const [x, y] = P(e, -e.t); g.photon(x, y, Math.atan2(-e.dy, -e.dx), phone ? 12 : 16, 0.9); }
          else if (!e.hitB) { e.hitB = true; pet.fl[detOf(e.ox - e.dx * e.tB, e.oy - e.dy * e.tB)] = 1; }
          if (e.t >= tm) {
            if (!e.done) { e.done = true; petAccum(e, c.warm); pet.n++; }
            const al = 1 - (e.t - tm) / 0.9; const [ax, ay] = P(e, e.tA), [bx, by] = P(e, -e.tB);
            if (al > 0) g.line(ax, ay, bx, by, c.photon, 1.6, 0.85 * al);
          }
        }
        pet.ev = pet.ev.filter((e) => e.t < Math.max(e.tA, e.tB) + 0.9);
        // the tracer you drag
        const hx = cx + S.hx * R, hy = cy + S.hy * R;
        g.ring(hx, hy, 14 + 2 * Math.sin(S.time * 3), c.ink, 1.5, 0.6, [3, 3]);
        g.label(phone ? "tracer" : "tracer (drag me)", hx, hy + 30, { color: c.ink, size: fs - 1, weight: 600, bg: true });
        g.label("detector ring", cx, cy - R - th - (phone ? 10 : 14), { color: c.soft, size: fs - 1, weight: 600 });
        g.label(phone ? "pairs of 511 keV gamma rays, back to back" : "each decay: two 511 keV gamma rays, back to back", W * 0.5, cy + R + th + (phone ? 16 : 22), { color: c.photon, size: fs, weight: 600 });
        g.label(`fluorine-18 · half-life 110 min · ${fmtN(pet.n)} pairs recorded`, W * 0.5, H * 0.94, { color: c.ink, size: fs + 1, weight: 600, serif: true });
        g.label("illustration", W - 6, H - 10, { color: c.faint, size: 10, align: "right" });
        return;
      }

      // ================= radiotherapy =================
      if (mode === "rt") {
        const n = Math.round(S.nb), rot = S.rotd * Math.PI / 180, key = `${n}|${S.rotd.toFixed(1)}|${c.proton}`;
        setOut("ev-rot", Math.round(S.rotd) + "°");
        if (key !== rt.key) { rt.key = key; rtMap(c, n, rot); }
        const X = (u) => cx + u * R, Y = (v) => cy + v * R, Rg = R * 1.08, tx = TUM[0], ty = TUM[1];
        g.ring(cx, cy, Rg, c.soft, 1.2, 0.3, [4, 6]);
        // beams: a band from the machine head through the tumour and out
        rt.stats.beams.forEach(([ux, uy], k) => {
          const b = tx * ux + ty * uy, L = -b + Math.sqrt(b * b - (tx * tx + ty * ty) + (Rg / R) ** 2);
          const hx = tx + ux * L, hy = ty + uy * L, ex = tx - ux * 1.2, ey = ty - uy * 1.2, nx = -uy * HW, ny = ux * HW;
          ctx.save(); ctx.beginPath(); ctx.moveTo(X(hx + nx), Y(hy + ny)); ctx.lineTo(X(ex + nx), Y(ey + ny)); ctx.lineTo(X(ex - nx), Y(ey - ny)); ctx.lineTo(X(hx - nx), Y(hy - ny)); ctx.closePath();
          const gr = ctx.createLinearGradient(X(hx), Y(hy), X(ex), Y(ey)); gr.addColorStop(0, g.rgba(c.accent, 0.22)); gr.addColorStop(1, g.rgba(c.accent, 0));
          ctx.fillStyle = gr; ctx.fill(); ctx.restore();
          // photons streaming along the beam
          for (let i = 0; i < 5; i++) { const s = ((S.time * 0.45 + i / 5 + k * 0.13) % 1), px = lerp(hx, ex, s), py = lerp(hy, ey, s), o = ((i * 37 + k * 11) % 7 - 3) / 3.5 * HW * 0.8;
            g.dot(X(px - uy * o), Y(py + ux * o), phone ? 1.6 : 2, c.accent, 0.7 * (1 - s)); }
          // machine head
          ctx.save(); ctx.translate(X(hx), Y(hy)); ctx.rotate(Math.atan2(uy, ux)); const hs = R * 0.07;
          ctx.fillStyle = g.rgba(c.accent, 0.9); ctx.beginPath(); ctx.moveTo(-hs * 0.4, -hs * 1.1); ctx.lineTo(hs * 1.2, -hs * 1.1); ctx.lineTo(hs * 1.2, hs * 1.1); ctx.lineTo(-hs * 0.4, hs * 1.1); ctx.closePath(); ctx.fill(); ctx.restore();
        });
        // body with the dose map
        ctx.save(); ctx.beginPath(); ctx.ellipse(cx, cy, BRX * R, BRY * R, 0, 0, TAU); ctx.fillStyle = g.rgba(c.warm, 0.08); ctx.fill(); ctx.clip();
        ctx.imageSmoothingEnabled = true; ctx.drawImage(rt.cv, cx - BRX * R, cy - BRY * R, 2 * BRX * R, 2 * BRY * R); ctx.restore();
        ctx.save(); ctx.beginPath(); ctx.ellipse(cx, cy, BRX * R, BRY * R, 0, 0, TAU); ctx.strokeStyle = g.rgba(c.soft, 0.6); ctx.lineWidth = 1.5; ctx.stroke(); ctx.restore();
        // tumour and spinal cord
        const st = rt.stats, cordHot = st.cord > 0.5;
        g.ring(X(tx), Y(ty), TR * R, c.ink, 1.6, 0.85, [4, 3]);
        g.label("tumour", X(tx), Y(ty) - TR * R - 12, { color: c.ink, size: fs - 1, weight: 600, bg: true });
        g.dot(X(CORD[0]), Y(CORD[1]), CR * R, cordHot ? c.proton : c.alpha, 0.9); g.ring(X(CORD[0]), Y(CORD[1]), CR * R + 3, c.ink, 1, 0.5);
        if (cordHot) g.glow(X(CORD[0]), Y(CORD[1]), CR * R * 4, c.proton, 0.4 + 0.15 * Math.sin(S.time * 5));
        g.label("spinal cord", X(CORD[0]), Y(CORD[1]) + CR * R + 13, { color: cordHot ? c.proton : c.soft, size: fs - 1, weight: 600, bg: true });
        // colour key
        { const kx = phone ? W * 0.06 : W * 0.06, ky = H * 0.06, kw = phone ? 90 : 130, gr = ctx.createLinearGradient(kx, 0, kx + kw, 0);
          [[0, c.cool], [0.35, c.fission], [0.65, c.photon], [1, c.proton]].forEach(([s, col]) => gr.addColorStop(s, col));
          ctx.save(); ctx.fillStyle = gr; ctx.globalAlpha = 0.85; ctx.fillRect(kx, ky, kw, 7); ctx.restore();
          g.label("dose", kx, ky - 10, { color: c.soft, size: fs - 2, align: "left" }); g.label("100 %", kx + kw, ky + 18, { color: c.soft, size: fs - 2, align: "right" }); g.label("0", kx, ky + 18, { color: c.soft, size: fs - 2, align: "left" }); }
        const line = `tumour 100 % · spinal cord ${Math.round(st.cord * 100)} % · ${phone ? "other tissue" : "healthy tissue"} at most ${Math.round(st.hmax * 100)} %`;
        g.label(line, W * 0.5, H * 0.94, { color: c.ink, size: fs + 1, weight: 600, serif: true });
        g.label(n === 1 ? "one beam: more dose near the skin than in the tumour" : cordHot ? "a beam crosses the spinal cord: turn the beams" : `${n} beams cross: the tumour gets their sum`, W * 0.5, cy + Rg + (phone ? 10 : 16), { color: n === 1 || cordHot ? c.proton : c.fission, size: fs, weight: 600, bg: true });
        g.label("illustration", W - 6, H - 10, { color: c.faint, size: 10, align: "right" });
        return;
      }

      // ================= technetium-99m =================
      if (mode === "tc") {
        const A = 2 ** (-S.th / T_TC), lx0 = W * (phone ? 0.12 : 0.2), lx1 = W * (phone ? 0.88 : 0.8), bodyY = H * (phone ? 0.36 : 0.34), sc = (lx1 - lx0), bh = Math.min(H * 0.05, sc * 0.06);
        const camY = H * (phone ? 0.1 : 0.12), camH = H * 0.045;
        // table
        g.line(lx0 - 20, bodyY + bh * 1.6, lx1 + 20, bodyY + bh * 1.6, c.soft, 3, 0.4);
        // the patient, lying down, seen from the side-ish (top view of an outline)
        ctx.save(); ctx.globalAlpha = 0.55; ctx.strokeStyle = c.soft; ctx.lineWidth = 1.5; ctx.fillStyle = g.rgba(c.warm, 0.1);
        ctx.beginPath(); ctx.arc(lx0 + sc * 0.05, bodyY, bh * 1.05, 0, TAU); ctx.fill(); ctx.stroke();
        ctx.beginPath(); if (ctx.roundRect) ctx.roundRect(lx0 + sc * 0.11, bodyY - bh * 1.15, sc * 0.46, bh * 2.3, bh); else ctx.rect(lx0 + sc * 0.11, bodyY - bh * 1.15, sc * 0.46, bh * 2.3); ctx.fill(); ctx.stroke();
        ctx.beginPath(); if (ctx.roundRect) ctx.roundRect(lx0 + sc * 0.55, bodyY - bh * 0.9, sc * 0.42, bh * 1.8, bh * 0.7); else ctx.rect(lx0 + sc * 0.55, bodyY - bh * 0.9, sc * 0.42, bh * 1.8); ctx.fill(); ctx.stroke();
        ctx.restore();
        const spot = SPOTS.map(([u, v, w]) => [lx0 + u * sc, bodyY + v * bh * 1.6, w]);
        spot.forEach(([x, y, w], i) => { g.glow(x, y, bh * 0.75 * w, c.fission, (0.15 + 0.6 * A) * (0.85 + 0.15 * Math.sin(S.time * 2 + i))); g.dot(x, y, 2.4 * w, c.fission, 0.3 + 0.7 * A); });
        // gamma camera head
        ctx.save(); ctx.fillStyle = g.rgba(c.soft, 0.18); ctx.strokeStyle = g.rgba(c.soft, 0.6); ctx.lineWidth = 1.2; ctx.fillRect(lx0, camY, lx1 - lx0, camH); ctx.strokeRect(lx0 + 0.5, camY + 0.5, lx1 - lx0 - 1, camH - 1);
        for (let x = lx0 + 6; x < lx1; x += phone ? 6 : 8) g.line(x, camY + camH * 0.55, x, camY + camH, c.soft, 1, 0.35); ctx.restore();
        g.label("gamma camera", lx1 + 8, camY + camH / 2, { color: c.soft, size: fs - 1, weight: 600, align: "left" });
        // photons: most of those drawn go straight up (the ones the collimator passes)
        tc.sp += dt * 26 * A; while (tc.sp >= 1) { tc.sp -= 1; const q = tc.q, s = spot[Math.floor(q() * spot.length)], up = q() < 0.7; tc.ph.push({ x: s[0], y: s[1], a: up ? -Math.PI / 2 : q() * TAU, t: 0, up }); }
        if (snap && !tc.ph.length) { const q = rng(4); for (let i = 0; i < 12 * A + 2; i++) { const s = spot[i % spot.length]; tc.ph.push({ x: s[0], y: s[1] - q() * (s[1] - camY - camH), a: -Math.PI / 2, t: 0, up: true }); } }
        const v = H * 0.55;
        tc.ph.forEach((p) => { p.t += dt; p.x += Math.cos(p.a) * v * dt; p.y += Math.sin(p.a) * v * dt;
          if (p.up && p.y <= camY + camH) { p.dead = true; tc.fl.push([p.x, 1]); } else g.photon(p.x, p.y, p.a, phone ? 10 : 14, p.up ? 0.95 : 0.45); });
        tc.ph = tc.ph.filter((p) => !p.dead && p.t < 1.5);
        tc.fl.forEach((f) => { f[1] -= dt * 2; if (f[1] > 0) g.glow(f[0], camY + camH, 12, c.photon, 0.7 * f[1]); }); tc.fl = tc.fl.filter((f) => f[1] > 0);
        g.label("140 keV gamma rays", lx0 - 6, (camY + camH + bodyY) / 2, { color: c.photon, size: fs - 1, weight: 600, align: "right" });
        // decay curve
        const x0 = W * (phone ? 0.1 : 0.12), x1 = W * (phone ? 0.94 : 0.9), y0 = H * (phone ? 0.53 : 0.52), y1 = H * (phone ? 0.84 : 0.85), TM = 48;
        S._geo.ch = { x0, x1, y0, y1 };
        const XT = (t) => lerp(x0, x1, t / TM), YA = (a) => lerp(y1, y0, a);
        g.line(x0, y1, x1, y1, c.soft, 1, 0.5); g.line(x0, y0, x0, y1, c.soft, 1, 0.5);
        for (let k = 1; k <= 8; k++) { const t = k * T_TC; g.line(XT(t), y0, XT(t), y1, c.soft, 1, 0.18, [2, 4]); }
        [0, 12, 24, 36, 48].forEach((t) => g.label(`${t} h`, XT(t), y1 + 12, { color: c.soft, size: fs - 2 }));
        g.label("100 %", x0 - 6, YA(1), { color: c.soft, size: fs - 2, align: "right" }); g.label("50 %", x0 - 6, YA(0.5), { color: c.soft, size: fs - 2, align: "right" });
        const mo = [], tcp = []; for (let i = 0; i <= 120; i++) { const t = TM * i / 120; mo.push([XT(t), YA(2 ** (-t / T_MO))]); tcp.push([XT(t), YA(2 ** (-t / T_TC))]); }
        g.poly(mo, c.warm, 1.5, 0.6, [5, 4]); g.label(phone ? "Mo-99 (66 h)" : "molybdenum-99, half-life 66 h", XT(30), YA(2 ** (-30 / T_MO)) - 12, { color: c.warm, size: fs - 1, weight: 600 });
        g.area([[x0, y1], ...tcp.filter((p, i) => i <= Math.round(S.th / TM * 120)), [XT(S.th), y1]], c.fission, 0.15);
        g.poly(tcp, c.fission, 2.5);
        g.label(phone ? "Tc-99m (6 h)" : "technetium-99m, half-life 6 h", XT(T_TC) + 8, YA(0.5) - 6, { color: c.fission, size: fs - 1, weight: 600, align: "left" });
        const mx = XT(S.th), my = YA(A);
        g.line(mx, my, mx, y1, c.ink, 1, 0.4); g.glow(mx, my, 16, c.fission, 0.5); g.ball(mx, my, 6, c.fission); g.ring(mx, my, 10 + 1.5 * Math.sin(S.time * 3), c.ink, 1.4, 0.6);
        g.label(`${S.th.toFixed(1).replace(/\.0$/, "")} h: ${pct(A)} left`, clamp(mx, x0 + 60, x1 - 60), Math.min(my, y1 - 30) - 22, { color: c.ink, size: fs + 1, weight: 700, bg: true });
        g.label("physical decay only", x1, y0 - 8, { color: c.faint, size: fs - 2, align: "right" });
        g.label(A > 0.5 ? "a strong gamma signal, easy to image" : A > 0.0625 ? "fading: half is gone every 6 hours" : "after a day, about 6 % is left", W * 0.5, H * 0.94, { color: c.ink, size: fs + 1, weight: 600, serif: true });
        g.label("illustration", W - 6, H - 10, { color: c.faint, size: 10, align: "right" });
        return;
      }

      // ================= carbon dating =================
      if (mode === "c14") {
        // keep the two sliders in step: whichever moved last sets the other
        if (Math.abs(S.target.age - S._pa) > 1e-6) { const f = 100 * 2 ** (-S.target.age / T_C14); S.set("fr", f); setIn("fr", f.toFixed(1)); setIn("age", S.target.age); }
        else if (Math.abs(S.target.fr - S._pf) > 1e-6) { const a = -T_C14 * Math.log2(S.target.fr / 100); S.set("age", a); setIn("age", Math.round(a / 10) * 10); }
        S._pa = S.target.age; S._pf = S.target.fr; S.age = S.target.age; S.fr = S.target.fr;
        const age = S.age, F = 2 ** (-age / T_C14);
        setOut("ev-age", fmtN(Math.round(age / 10) * 10)); setOut("ev-fr", pct(F));
        // atoms
        const cols = phone ? 18 : 30, rows = 6, N = cols * rows; c14Atoms(N);
        const ax0 = W * 0.08, ax1 = W * 0.92, ay0 = H * 0.1, ay1 = H * (phone ? 0.36 : 0.38), cw = (ax1 - ax0) / cols, chh = (ay1 - ay0) / rows, r = Math.min(cw, chh) * 0.3;
        let left = 0; const st = C14.times.map((t) => t > age);
        st.forEach((alive, i) => {
          const x = ax0 + (i % cols + 0.5) * cw, y = ay0 + (Math.floor(i / cols) + 0.5) * chh, [ph, sp] = C14.jit[i], jx = Math.sin(S.time * 2 * sp + ph) * 0.8, jy = Math.cos(S.time * 1.7 * sp + ph) * 0.8;
          if (C14.prev && C14.prev[i] !== alive) C14.fl.push([x, y, 1, alive]);
          if (alive) { left++; g.ball(x + jx, y + jy, r, c.fission); } else g.ball(x + jx, y + jy, r * 0.8, c.neutron, 0.45);
        });
        C14.prev = st;
        C14.fl.forEach((f) => { f[2] -= dt * 1.6; if (f[2] > 0 && !f[3]) { g.glow(f[0], f[1], r * 4, c.accent, 0.6 * f[2]); g.ring(f[0], f[1], r * (1 + 3 * (1 - f[2])), c.accent, 1.2, f[2]); } }); C14.fl = C14.fl.filter((f) => f[2] > 0);
        g.ball(ax0 + 6, ay0 - 14, 5, c.fission); g.label("carbon-14", ax0 + 16, ay0 - 14, { color: c.fission, size: fs - 1, weight: 600, align: "left" });
        g.ball(ax0 + (phone ? 100 : 120), ay0 - 14, 4, c.neutron, 0.6); g.label(phone ? "nitrogen-14" : "nitrogen-14 (after a beta decay)", ax0 + (phone ? 110 : 130), ay0 - 14, { color: c.neutron, size: fs - 1, weight: 600, align: "left" });
        g.label(`${left} of ${N} left`, ax1, ay0 - 14, { color: c.ink, size: fs - 1, weight: 700, align: "right" });
        // curve
        const x0 = W * (phone ? 0.12 : 0.1), x1 = W * 0.92, y0 = H * (phone ? 0.5 : 0.5), y1 = H * 0.84, AM = 50000;
        S._geo.ch = { x0, x1, y0, y1 };
        const XA = (a) => lerp(x0, x1, a / AM), YF = (f) => lerp(y1, y0, f);
        g.line(x0, y1, x1, y1, c.soft, 1, 0.5); g.line(x0, y0, x0, y1, c.soft, 1, 0.5);
        for (let k = 1; k * T_C14 <= AM; k++) g.line(XA(k * T_C14), y0, XA(k * T_C14), y1, c.soft, 1, 0.18, [2, 4]);
        (phone ? [0, 20000, 40000] : [0, 10000, 20000, 30000, 40000, 50000]).forEach((a) => g.label(a ? `${a / 1000},000` : "0", XA(a), y1 + 12, { color: c.soft, size: fs - 2 }));
        g.label("years", x1, y1 + 26, { color: c.soft, size: fs - 2, align: "right" });
        g.label("100 %", x0 - 6, YF(1), { color: c.soft, size: fs - 2, align: "right" }); g.label("50 %", x0 - 6, YF(0.5), { color: c.soft, size: fs - 2, align: "right" });
        const pts = []; for (let i = 0; i <= 160; i++) { const a = AM * i / 160; pts.push([XA(a), YF(2 ** (-a / T_C14))]); }
        g.area([[x0, y1], ...pts.filter((p, i) => i <= Math.round(age / AM * 160)), [XA(age), y1]], c.fission, 0.13); g.poly(pts, c.fission, 2.5);
        // landmarks
        g.dot(XA(T_C14), YF(0.5), 3.5, c.fission); g.label("half-life 5,730 y", XA(T_C14) + 10, YF(0.5) + 16, { color: c.fission, size: fs - 1, weight: 600, align: "left" });
        if (!phone) { g.line(XA(5300), YF(2 ** (-5300 / T_C14)), XA(5300), y1, c.warm, 1, 0.5, [3, 3]); g.label("Ötzi the Iceman, ~5,300 y", XA(5300) + 6, y1 - 12, { color: c.warm, size: fs - 2, weight: 600, align: "left" }); }
        g.label(phone ? "~50,000 y: too little to measure" : "beyond ~50,000 years too little is left to measure", x1, YF(0.12), { color: c.soft, size: fs - 2, align: "right" });
        const mx = XA(age), my = YF(F);
        g.line(x0, my, mx, my, c.ink, 1, 0.35, [3, 3]); g.line(mx, my, mx, y1, c.ink, 1, 0.35, [3, 3]);
        g.glow(mx, my, 16, c.fission, 0.5); g.ball(mx, my, 6, c.fission); g.ring(mx, my, 10 + 1.5 * Math.sin(S.time * 3), c.ink, 1.4, 0.6);
        g.label(`${fmtN(Math.round(age / 10) * 10)} years · ${pct(F)} left`, clamp(mx, x0 + 90, x1 - 90), Math.max(y0 + 6, my - 24), { color: c.ink, size: fs + 1, weight: 700, bg: true });
        g.label(`${(age / T_C14).toFixed(1).replace(/\.0$/, "")} half-lives`, W * 0.5, H * 0.94, { color: c.ink, size: fs + 1, weight: 600, serif: true });
        return;
      }

      // ================= smoke detector =================
      {
        setOut("ev-sm", Math.round(S.sm * 100) + " %");
        const cx0 = W * (phone ? 0.08 : 0.1), cx1 = W * (phone ? 0.7 : 0.68), py0 = H * 0.2, py1 = H * 0.7, mid = (py0 + py1) / 2, sx = cx0 + 10;
        const step = (h) => {
          // alphas from the source, each leaving ion pairs along its path
          SM.sp += h * AL_RATE; while (SM.sp >= 1) { SM.sp -= 1; const a = (SM.q() - 0.5) * 1.1; SM.al.push({ a, t: 0, L: (cx1 - cx0) * (0.72 + 0.25 * SM.q()), k: 0 }); }
          const vA = (cx1 - cx0) * 2.2;
          SM.al.forEach((p) => { p.t += h; const d = Math.min(p.L, p.t * vA), want = Math.floor(d / p.L * PAIRS);
            while (p.k < want) { p.k++; const s = p.k / PAIRS * p.L, x = sx + Math.cos(p.a) * s, y = mid + Math.sin(p.a) * s;
              if (y > py0 + 4 && y < py1 - 4 && x < cx1 - 4) { SM.ion.push({ x, y: y - 2, s: 1 }); SM.ion.push({ x, y: y + 2, s: -1 }); } } });
          SM.al = SM.al.filter((p) => p.t * vA < p.L + 30);
          // smoke particles drift in and out
          const want = Math.round(S.sm * 56); while (SM.blob.length < want) SM.blob.push({ x: lerp(cx0, cx1, SM.q()), y: lerp(py0, py1, SM.q()), r: 5 + 5 * SM.q(), ph: SM.q() * TAU, f: 0 });
          if (SM.blob.length > want) SM.blob.length = want;
          SM.blob.forEach((b) => { b.ph += h; b.x += Math.sin(b.ph * 0.7) * 6 * h + 4 * h; b.y += Math.cos(b.ph * 0.9) * 6 * h; if (b.x > cx1 - 4) b.x = cx0 + 4; b.y = clamp(b.y, py0 + 8, py1 - 8); b.f = Math.max(0, b.f - h * 3); });
          // ions drift to the plates (+ ions down to the - plate, - ions up to the + plate); smoke catches some
          const vI = (py1 - py0) * 0.55; let got = 0;
          SM.ion.forEach((o) => { o.y += o.s * vI * h; for (const b of SM.blob) if (Math.abs(o.x - b.x) < b.r + 6 && Math.abs(o.y - b.y) < b.r + 6) { o.dead = true; b.f = 1; break; }
            if (!o.dead && (o.y >= py1 || o.y <= py0)) { o.dead = true; got++; SM.fl.push([o.x, o.y >= py1 ? py1 : py0, 1]); } });
          SM.ion = SM.ion.filter((o) => !o.dead);
          SM.rate += (got / h - SM.rate) * (1 - Math.exp(-h / 1.2));
        };
        if (!SM.warm) { SM.warm = true; SM.rate = AL_RATE * PAIRS * 2 * 0.9; for (let i = 0; i < (snap ? 300 : 120); i++) step(1 / 60); SM.fl.length = 0; }
        if (dt > 0) step(dt);
        const ref = AL_RATE * PAIRS * 2 * 0.86, I = clamp(SM.rate / ref, 0, 1.2), alarm = I < 0.6;
        // plates and the chamber
        ctx.save(); ctx.fillStyle = g.rgba(c.accent, 0.04); ctx.fillRect(cx0, py0, cx1 - cx0, py1 - py0); ctx.restore();
        g.line(cx0, py0, cx1, py0, c.proton, 4, 0.8); g.line(cx0, py1, cx1, py1, c.cool, 4, 0.8);
        g.label("+", cx1 + 12, py0, { color: c.proton, size: fs + 4, weight: 700 }); g.label("−", cx1 + 12, py1, { color: c.cool, size: fs + 4, weight: 700 });
        // source
        g.glow(sx, mid, 22, c.alpha, 0.45); ctx.save(); ctx.fillStyle = c.alpha; ctx.fillRect(cx0 - 4, mid - 12, 9, 24); ctx.restore();
        g.label(phone ? "Am-241" : "americium-241 (sealed)", cx0 - 4, mid + 28, { color: c.alpha, size: fs - 1, weight: 600, align: "left", bg: true });
        // smoke
        SM.blob.forEach((b) => { g.glow(b.x, b.y, b.r * 1.8, c.soft, 0.35); g.dot(b.x, b.y, b.r * 0.75, c.soft, 0.45); if (b.f > 0) g.ring(b.x, b.y, b.r, c.ink, 1, b.f * 0.6); });
        // alphas and ions
        const vA = (cx1 - cx0) * 2.2;
        SM.al.forEach((p) => { const d = Math.min(p.L, p.t * vA), x = sx + Math.cos(p.a) * d, y = mid + Math.sin(p.a) * d, fade = d >= p.L ? 0.3 : 1;
          g.line(sx, mid, x, y, c.alpha, 1.4, 0.25 * fade); if (d < p.L) { g.glow(x, y, 9, c.alpha, 0.6); g.dot(x, y, 2.6, c.alpha); } });
        SM.ion.forEach((o) => g.dot(o.x, o.y, phone ? 1.8 : 2.2, o.s > 0 ? c.proton : c.cool, 0.9));
        SM.fl.forEach((f) => { f[2] -= dt * 3; if (f[2] > 0) g.glow(f[0], f[1], 7, c.photon, 0.5 * f[2]); }); SM.fl = SM.fl.filter((f) => f[2] > 0);
        if (!phone) g.label("alpha particles make ions in the air", (cx0 + cx1) / 2, py0 - 14, { color: c.alpha, size: fs - 1, weight: 600 });
        // current meter
        const mx0 = W * (phone ? 0.8 : 0.79), mw = phone ? 22 : 30, my0 = py0, my1 = py1, YI = (v) => lerp(my1, my0, v / 1.2);
        ctx.save(); ctx.fillStyle = g.rgba(c.soft, 0.1); ctx.fillRect(mx0, my0, mw, my1 - my0); ctx.strokeStyle = g.rgba(c.soft, 0.5); ctx.strokeRect(mx0 + 0.5, my0 + 0.5, mw - 1, my1 - my0 - 1);
        const gr = ctx.createLinearGradient(0, my1, 0, my0); gr.addColorStop(0, g.rgba(alarm ? c.proton : c.fission, 0.9)); gr.addColorStop(1, g.rgba(alarm ? c.proton : c.fission, 0.5));
        ctx.fillStyle = gr; ctx.fillRect(mx0 + 3, YI(I), mw - 6, my1 - YI(I)); ctx.restore();
        g.line(mx0 - 6, YI(0.6), mx0 + mw + 6, YI(0.6), c.proton, 1.5, 0.8, [4, 3]);
        g.label("alarm", mx0 + mw + 8, YI(0.6), { color: c.proton, size: fs - 2, weight: 600, align: "left" });
        g.label("current", mx0 + mw / 2, my1 + 14, { color: c.soft, size: fs - 1, weight: 600 });
        // alarm light
        const lx = mx0 + mw / 2, ly = py0 - (phone ? 26 : 34);
        SM.ripple = alarm ? (SM.ripple + dt) % 1 : 0;
        if (alarm) { g.glow(lx, ly, 34, c.proton, 0.5 + 0.3 * Math.sin(S.time * 12)); g.ring(lx, ly, 10 + 26 * SM.ripple, c.proton, 2, 1 - SM.ripple); }
        g.ball(lx, ly, 8, alarm ? c.proton : c.soft, alarm ? 1 : 0.5);
        g.label(alarm ? "smoke: current down, alarm!" : S.sm > 0.02 ? "some ions caught: current dipping" : "clean air: steady current", W * 0.5, H * 0.84, { color: alarm ? c.proton : c.ink, size: fs + 1, weight: 600, bg: true });
        g.label(`americium-241 · half-life ${Math.round(T_AM)} years · alphas reach about 4 cm in air`, W * 0.5, H * 0.94, { color: c.ink, size: fs, weight: 600, serif: true });
        g.label("illustration", W - 6, H - 10, { color: c.faint, size: 10, align: "right" });
      }
    },
  });
})();
