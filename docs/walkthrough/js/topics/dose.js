/* Radiation dose. Scenes (S.mode):
 *   "cells" = a patch of tissue (cell nuclei). Absorbed dose in gray = joules per kilogram. For gamma/X-rays 1 mGy means on
 *             average about one electron track through each cell nucleus (UNSCEAR 2000, Annex G; ~1 track per nucleus per
 *             mGy of low-LET radiation). The same energy as alpha particles comes as rare, dense tracks. The sievert weights the
 *             gray by harm: radiation weighting factor w_R = 1 for photons and electrons, 20 for alpha (ICRP 103, 2007);
 *             effective dose also weights organs (tissue factors), not shown. Track counts are drawn to that rule; positions
 *             random. Alpha drawing: illustrative (few nuclei crossed, heavily).
 *   "ladder" = everyday doses on a log line (typical values): banana ~0.1 uSv; dental X-ray ~5 uSv; chest X-ray ~20 uSv;
 *             transatlantic flight one way ~40-80 uSv (shown 60); chest CT ~7 mSv (Mettler et al. 2008, Radiology 248:254);
 *             world average natural background 2.4 mSv/yr (UNSCEAR 2008); Kerala coast up to ~70 mGy/yr in spots (Nair et al.
 *             2009); Ramsar homes up to ~260 mGy/yr (Ghiassi-nejad et al. 2002); ICRP occupational limit 20 mSv/yr averaged over
 *             5 years (ICRP 103); ~1 Sv at once: radiation sickness begins; ~4-5 Sv at once: about half die without treatment.
 *   "year"  = your own year: UNSCEAR 2008 world averages radon 1.26, ground 0.48, food 0.29, cosmic 0.39 mSv/yr (sum 2.4);
 *             flights 60 uSv each; chest CT 7 mSv; cosmic dose doubles roughly every 1.5 km of altitude (approximation).
 *   "acute" = dose received at once, 1 mSv to 10 Sv: tracks per cell nucleus = dose / 1 mGy (gamma); thresholds as above.
 * Below about 100 mSv extra cancer risk is too small to measure directly; ICRP protection rules assume risk in proportion to
 * dose (the linear no-threshold model) as a prudent working assumption. Nothing here takes a side beyond that. */
(function () {
  const { TAU, clamp, lerp, smooth, rng } = WT.util;
  const log10 = (x) => Math.log(x) / Math.LN10;
  const LO = -7.3, HI = 1.1; // log10 sievert range of the ladder
  const ITEMS = [ // [sievert, label, short label, colour key]
    [1e-7, "eating a banana", "banana", "photon", "banana"],
    [5e-6, "dental X-ray", "dental X-ray", "cool", "tooth"],
    [2e-5, "chest X-ray", "chest X-ray", "cool", "ribs"],
    [6e-5, "flight across the Atlantic", "Atlantic flight", "accent", "plane"],
    [2.4e-3, "a year of natural background", "1 yr background", "fission", "hill"],
    [7e-3, "chest CT scan", "chest CT", "cool", "ring"],
    [2e-2, "yearly limit for radiation workers", "worker limit/yr", "warm", "hat"],
    [7e-2, "a year on the Kerala coast (high spots)", "Kerala, 1 yr", "fission", "wave"],
    [2.6e-1, "a year in the highest Ramsar homes", "Ramsar, 1 yr", "fission", "house"],
    [1, "at once: radiation sickness begins", "1 Sv at once", "proton", "tre"],
    [4.5, "at once: about half die untreated", "4–5 Sv at once", "proton", "tre"],
  ];
  /** Small lit pictograms for the dose tower. */
  function icon(g, kind, x, y, sz, col, al) {
    const ctx = g.ctx; ctx.save(); ctx.globalAlpha = al; ctx.strokeStyle = col; ctx.fillStyle = col; ctx.lineWidth = Math.max(1.6, sz * 0.16); ctx.lineCap = "round"; ctx.lineJoin = "round";
    const s = sz / 2; ctx.beginPath();
    if (kind === "banana") { ctx.lineWidth = sz * 0.28; ctx.arc(x, y - s * 0.9, s * 1.2, Math.PI * 0.2, Math.PI * 0.8); ctx.stroke(); }
    else if (kind === "tooth") { ctx.moveTo(x - s * 0.8, y - s * 0.6); ctx.quadraticCurveTo(x, y - s * 1.1, x + s * 0.8, y - s * 0.6); ctx.lineTo(x + s * 0.5, y + s * 0.9); ctx.lineTo(x + s * 0.15, y + s * 0.1); ctx.lineTo(x - s * 0.15, y + s * 0.1); ctx.lineTo(x - s * 0.5, y + s * 0.9); ctx.closePath(); ctx.fill(); }
    else if (kind === "ribs") { ctx.moveTo(x, y - s); ctx.lineTo(x, y + s); for (let i = -1; i <= 1; i++) { const yy = y + i * s * 0.55; ctx.moveTo(x, yy); ctx.quadraticCurveTo(x - s, yy - s * 0.2, x - s * 0.9, yy + s * 0.3); ctx.moveTo(x, yy); ctx.quadraticCurveTo(x + s, yy - s * 0.2, x + s * 0.9, yy + s * 0.3); } ctx.stroke(); }
    else if (kind === "plane") { ctx.moveTo(x - s, y + s * 0.1); ctx.lineTo(x + s, y - s * 0.1); ctx.moveTo(x - s * 0.1, y - s * 0.9); ctx.lineTo(x + s * 0.25, y + s * 0.9); ctx.moveTo(x - s * 0.9, y - s * 0.4); ctx.lineTo(x - s * 0.8, y + s * 0.5); ctx.stroke(); }
    else if (kind === "hill") { ctx.moveTo(x - s, y + s * 0.7); ctx.lineTo(x - s * 0.2, y - s * 0.4); ctx.lineTo(x + s * 0.2, y + s * 0.1); ctx.lineTo(x + s * 0.5, y - s * 0.2); ctx.lineTo(x + s, y + s * 0.7); ctx.closePath(); ctx.fill(); ctx.beginPath(); ctx.arc(x + s * 0.6, y - s * 0.75, s * 0.25, 0, TAU); ctx.fill(); }
    else if (kind === "ring") { ctx.lineWidth = sz * 0.26; ctx.arc(x, y, s * 0.7, 0, TAU); ctx.stroke(); }
    else if (kind === "hat") { ctx.arc(x, y + s * 0.3, s * 0.75, Math.PI, 0); ctx.closePath(); ctx.fill(); ctx.beginPath(); ctx.moveTo(x - s, y + s * 0.35); ctx.lineTo(x + s, y + s * 0.35); ctx.stroke(); }
    else if (kind === "wave") { for (let k = 0; k < 2; k++) { const yy = y + k * s * 0.6 - s * 0.2; ctx.moveTo(x - s, yy); ctx.bezierCurveTo(x - s * 0.5, yy - s * 0.6, x, yy + s * 0.6, x + s, yy); } ctx.stroke(); }
    else if (kind === "house") { ctx.moveTo(x - s, y); ctx.lineTo(x, y - s); ctx.lineTo(x + s, y); ctx.lineTo(x + s * 0.7, y); ctx.lineTo(x + s * 0.7, y + s * 0.85); ctx.lineTo(x - s * 0.7, y + s * 0.85); ctx.lineTo(x - s * 0.7, y); ctx.closePath(); ctx.fill(); }
    else { for (let k = 0; k < 3; k++) { const a = -Math.PI / 2 + k * TAU / 3; ctx.moveTo(x, y); ctx.arc(x, y, s, a - 0.5, a + 0.5); ctx.closePath(); } ctx.fill(); }
    ctx.restore();
  }
  const BUB = []; { const q = rng(23); for (let i = 0; i < 40; i++) BUB.push([q(), q(), 0.5 + q()]); }
  function fmtD(sv) {
    if (sv < 1e-3) { const u = sv * 1e6; return `${u < 1 ? u.toFixed(1) : u < 10 ? u.toFixed(1).replace(/\.0$/, "") : Math.round(u)} µSv`; }
    if (sv < 1) { const m = sv * 1e3; return `${m < 10 ? m.toFixed(1).replace(/\.0$/, "") : Math.round(m)} mSv`; }
    return `${sv.toFixed(sv < 10 ? 1 : 0).replace(/\.0$/, "")} Sv`;
  }
  const big = (n) => (n < 1000 ? String(Math.round(n)) : n < 1e6 ? `${Math.round(n / 1000).toLocaleString("en")} thousand` : `${(n / 1e6).toFixed(n < 1e7 ? 1 : 0)} million`);
  // ---------- tissue ----------
  const CELLS = []; { const q = rng(5); for (let j = 0; j < 7; j++) for (let i = 0; i < 11; i++) CELLS.push([(i + (j % 2) * 0.5 + 0.2 * (q() - 0.5)) / 11, (j + 0.5 + 0.2 * (q() - 0.5)) / 7, 0.8 + 0.3 * q(), q() * TAU]); }
  const press = (sel, on) => document.querySelectorAll(`#dose [data-act^="${sel}"]`).forEach((b) => b.setAttribute("aria-pressed", String(b.dataset.act === on)));

  WT.chapter("dose", {
    level: 0, num: "Lesson 3", title: "Radiation dose", short: "Dose",
    html: `
<div class="step">
  <h3>What a sievert measures</h3>
  <p>Dose starts as energy soaked up per kilogram of body. A <b>sievert</b> then weights that energy by the harm it does: the same energy delivered by alpha particles counts twenty times more than by gamma rays, because it is packed into a few dense tracks.</p>
  <div class="btns"><button class="btn ghost" data-act="rg" aria-pressed="true">Gamma rays</button><button class="btn ghost" data-act="ra" aria-pressed="false">Alpha particles</button></div>
</div>
<div class="step">
  <h3>Everyday doses</h3>
  <p>Each mark up this tower is ten times the one below. Drag the glowing bead to compare: a chest CT scan is the dose of many thousand bananas, a year of natural background a few dozen flights.</p>
  <div class="ctl"><label for="ds-l">Dose</label><input id="ds-l" type="range" data-bind="ld" data-instant min="-7" max="1" step="0.02" value="-2.15"><output class="ds-out"></output></div>
</div>
<div class="step">
  <h3>Stack up your year</h3>
  <p>Everyone gets about 2.4 millisieverts a year from nature, mostly radon gas from the ground. Add your own flights, scans and altitude.</p>
  <div class="ctl"><label for="ds-f">Flights across the Atlantic</label><input id="ds-f" type="range" data-bind="fl" data-instant min="0" max="40" step="1" value="4"><output data-show="fl" data-fmt="0"></output></div>
  <div class="ctl"><label for="ds-ct">Chest CT scans</label><input id="ds-ct" type="range" data-bind="ct" data-instant min="0" max="3" step="1" value="0"><output data-show="ct" data-fmt="0"></output></div>
  <div class="ctl"><label for="ds-h">Home altitude (m)</label><input id="ds-h" type="range" data-bind="alt" data-instant min="0" max="3500" step="50" value="300"><output data-show="alt" data-fmt="0"></output></div>
</div>
<div class="step">
  <h3>A big dose all at once</h3>
  <p>Below about 100 millisieverts, any extra cancer risk is too small to measure; safety rules assume it grows in proportion to dose. Around one sievert at once, cells are hit so often that radiation sickness begins.</p>
  <div class="ctl"><label for="ds-a">Dose at once</label><input id="ds-a" type="range" data-bind="la" data-instant min="-3" max="1" step="0.02" value="-1"><output class="ds-out2"></output></div>
</div>`,
    setup(S) {
      S.set("mode", "cells"); S.set("rad", 0); S.to("radV", 0, true); S.set("ld", -2.15); S.set("fl", 4); S.set("ct", 0); S.set("alt", 300); S.set("la", -1); S._o1 = S._o2 = "";
      S.on("rg", () => { S.set("rad", 0); S.to("radV", 0); press("r", "rg"); });
      S.on("ra", () => { S.set("rad", 1); S.to("radV", 1); press("r", "ra"); });
      S._cv = null;
    },
    steps: [
      (S) => { S.set("mode", "cells"); },
      (S) => { S.set("mode", "ladder"); },
      (S) => { S.set("mode", "year"); },
      (S) => { S.set("mode", "acute"); },
    ],
    frame(g, S, dt) {
      const { W, H, c, ctx } = g, phone = W < 600, fs = phone ? 11 : 13, snap = document.body.classList.contains("shot"), mode = S.mode;
      { const a = fmtD(10 ** S.ld), b = fmtD(10 ** S.la); if (a !== S._o1) { S._o1 = a; document.querySelectorAll("#dose .ds-out").forEach((o) => (o.textContent = a)); } if (b !== S._o2) { S._o2 = b; document.querySelectorAll("#dose .ds-out2").forEach((o) => (o.textContent = b)); } }
      if (!S._cv && g.ctx.canvas) { S._cv = g.ctx.canvas; WT.grab(S._cv, {
        down: (x, y) => { if (S.mode !== "ladder" || !S._lad) return false; const L = S._lad; if (Math.abs(x - L.x) > 50) return false; S.set("ld", clamp(L.inv(y), -7, 1)); return true; },
        move: (x, y) => { if (S.mode === "ladder" && S._lad) S.set("ld", clamp(S._lad.inv(y), -7, 1)); },
        up: () => { document.querySelectorAll("#dose [data-bind=ld]").forEach((i) => (i.value = S.ld)); },
        hover: (x, y) => { S._cv.style.cursor = S.mode === "ladder" && S._lad && Math.abs(x - S._lad.x) < 50 ? "ns-resize" : ""; },
      }); }

      // ---------- tissue patch (cells and acute) ----------
      const tissue = (x0, y0, w, h, tracksPer, alphaMix, harm = 0) => {
        const ncell = CELLS.length, cr = Math.min(w / 11, h / 7) * 0.36;
        ctx.save(); ctx.beginPath(); if (ctx.roundRect) ctx.roundRect(x0, y0, w, h, 14); else ctx.rect(x0, y0, w, h); ctx.fillStyle = g.rgba(c.proton, 0.06); ctx.fill(); ctx.clip();
        const hit = new Float32Array(ncell), hard = new Float32Array(ncell), CX = (k) => x0 + w * (0.06 + 0.88 * CELLS[k][0] / 0.96), CY = (k) => y0 + h * CELLS[k][1];
        // gamma-like tracks: thin wandering electron paths; count from the dose (about one per nucleus per mGy)
        const nT = Math.min(700, Math.round(tracksPer * ncell * (1 - alphaMix))), q = rng(11 + Math.floor(S.time * 1.2) * 0), tt = S.time;
        for (let i = 0; i < nT; i++) {
          const sx = x0 + q() * w, sy = y0 + q() * h, a = q() * TAU, L = (0.25 + 0.5 * q()) * Math.min(w, h) * 0.5;
          const ex = sx + Math.cos(a) * L, ey = sy + Math.sin(a) * L, ph = (tt * 0.35 + q()) % 1;
          g.line(sx, sy, ex, ey, c.accent, 1.3, nT > 200 ? 0.25 : 0.75);
          if (nT < 200) { g.dot(lerp(sx, ex, ph), lerp(sy, ey, ph), 2.2, c.accent, 1); g.glow(lerp(sx, ex, ph), lerp(sy, ey, ph), 6, c.accent, 0.4); }
          for (let k = 0; k < ncell; k++) { const cx = CX(k), cy = CY(k), dx = ex - sx, dy = ey - sy, t = clamp(((cx - sx) * dx + (cy - sy) * dy) / (dx * dx + dy * dy), 0, 1), px = sx + dx * t - cx, py = sy + dy * t - cy; if (px * px + py * py < cr * cr) hit[k] += 1; }
        }
        // alpha tracks: the same energy as a few dense straight tracks
        const nA = alphaMix > 0.01 ? Math.max(1, Math.round(3 * alphaMix)) : 0;
        for (let i = 0; i < nA; i++) {
          const sx = x0 + w * (0.15 + 0.3 * i), sy = y0 - 4, a = Math.PI * (0.35 + 0.12 * i), L = h * 0.75, ex = sx + Math.cos(a) * L, ey = sy + Math.sin(a) * L;
          g.line(sx, sy, ex, ey, c.alpha, 5, 0.75 * alphaMix); g.line(sx, sy, ex, ey, "#ffffff", 1.2, 0.5 * alphaMix);
          for (let s = 0; s < 22; s++) g.dot(lerp(sx, ex, s / 22) + Math.sin(s * 7) * 2, lerp(sy, ey, s / 22) + Math.cos(s * 5) * 2, 1.6, c.alpha, alphaMix);
          for (let k = 0; k < ncell; k++) { const cx = CX(k), cy = CY(k), dx = ex - sx, dy = ey - sy, t = clamp(((cx - sx) * dx + (cy - sy) * dy) / (dx * dx + dy * dy), 0, 1), px = sx + dx * t - cx, py = sy + dy * t - cy; if (px * px + py * py < cr * cr) { hit[k] += 1; hard[k] = alphaMix; } }
        }
        ctx.restore();
        for (let k = 0; k < ncell; k++) {
          const cx = CX(k), cy = CY(k), hk = hit[k], dmg = clamp(hard[k] + harm, 0, 1);
          g.ring(cx, cy, cr * 1.45, c.soft, 1, 0.3);
          g.ball(cx, cy, cr * CELLS[k][2] * 0.6, dmg > 0.5 ? c.proton : c.warm, 0.6 + 0.35 * (1 - dmg));
          if (hk > 0) g.glow(cx, cy, cr * 1.6, dmg > 0.3 ? c.proton : c.photon, 0.12 + 0.35 * dmg);
        }
        let n0 = 0; for (let k = 0; k < ncell; k++) if (hit[k] === 0) n0++;
        return n0 / ncell;
      };

      if (mode === "cells") {
        const a = S.radV, x0 = W * 0.08, y0 = H * 0.1, w = W * 0.84, h = H * (phone ? 0.58 : 0.6);
        tissue(x0, y0, w, h, 1, a);
        g.label(phone ? "cell nuclei in a patch of body" : "cell nuclei in a patch of body tissue", x0 + 6, y0 - 12, { color: c.soft, size: fs - 1, align: "left" });
        const al = S.rad === 1;
        g.label(al ? "1 milligray of alpha: a few cells hit hard" : "1 milligray of gamma: about one track per cell", W * 0.5, y0 + h + (phone ? 16 : 22), { color: al ? c.alpha : c.accent, size: fs, weight: 600 });
        g.label(al ? "same energy · counts as 20 millisieverts" : "counts as 1 millisievert", W * 0.5, H * 0.92, { color: c.ink, size: fs + 2, weight: 600, serif: true });
        g.label("illustration", W - 6, H - 10, { color: c.faint, size: 10, align: "right" });
        return;
      }

      if (mode === "ladder") {
        // ---------- a lit tower of everyday doses; the light fills up to the dose you drag ----------
        const tw = phone ? 22 : 34, lx = W * (phone ? 0.28 : 0.3), yT = H * 0.06, yB = H * 0.86, Y = (l) => lerp(yB, yT, (l - LO) / (HI - LO));
        S._lad = { x: lx, inv: (y) => LO + (HI - LO) * (yB - y) / (yB - yT) };
        const my = Y(S.ld), d = 10 ** S.ld;
        // the glass tube
        ctx.save(); ctx.beginPath(); if (ctx.roundRect) ctx.roundRect(lx - tw / 2, yT - 8, tw, yB - yT + 16, tw / 2); else ctx.rect(lx - tw / 2, yT - 8, tw, yB - yT + 16);
        ctx.fillStyle = g.rgba(c.soft, 0.08); ctx.fill(); ctx.strokeStyle = g.rgba(c.soft, 0.45); ctx.lineWidth = 1.5; ctx.stroke(); ctx.clip();
        // the light inside, up to the marker, with rising bubbles
        const grd = ctx.createLinearGradient(0, yB, 0, yT); grd.addColorStop(0, g.rgba(c.fission, 0.85)); grd.addColorStop(0.6, g.rgba(c.photon, 0.85)); grd.addColorStop(1, g.rgba(c.proton, 0.9));
        ctx.fillStyle = grd; ctx.fillRect(lx - tw / 2, my, tw, yB + 10 - my);
        for (const [bx, by, sp] of BUB) { const yy = yB + 6 - ((by + S.time * 0.08 * sp) % 1) * (yB - yT); if (yy < my) continue; g.dot(lx - tw / 2 + 4 + bx * (tw - 8), yy, 1 + sp, "#ffffff", 0.4); }
        ctx.fillStyle = g.rgba("#ffffff", 0.18); ctx.fillRect(lx - tw / 2 + 3, yT - 8, tw * 0.18, yB - yT + 16);
        ctx.restore();
        for (let l = -7; l <= 1; l++) g.line(lx - tw / 2, Y(l), lx + tw / 2, Y(l), c.paper, 1.4, 0.75);
        g.glow(lx, my, tw * 2.2, c.photon, 0.35 + 0.1 * Math.sin(S.time * 3));
        [[-6, "1 µSv"], [-3, "1 mSv"], [0, "1 Sv"]].forEach(([l, s]) => g.label(s, lx - tw / 2 - 10, Y(l), { color: c.soft, size: fs - 1, weight: 600, align: "right" }));
        // items: an icon on its level, labels pushed apart so nothing overlaps; reached items light up
        const gap = fs + 6, ix = lx + tw / 2 + (phone ? 14 : 22), tx = ix + (phone ? 12 : 18); let prev = Infinity;
        const ys = ITEMS.map(([sv]) => Y(log10(sv))), put = [];
        ys.forEach((y) => { const v = Math.min(y, prev - gap); put.push(v); prev = v; });
        if (put[put.length - 1] < yT) { put[put.length - 1] = yT; for (let i = put.length - 2; i >= 0; i--) put[i] = Math.max(put[i], put[i + 1] + gap); }
        ITEMS.forEach(([sv, lab, sh, ck, ic], i) => {
          const y = ys[i], col = c[ck], lit = log10(sv) <= S.ld + 1e-6, al = lit ? 1 : 0.45;
          g.line(lx + tw / 2, y, ix - 9, put[i], col, 1, 0.4 * al);
          if (lit) g.glow(ix, put[i], 14, col, 0.45);
          icon(g, ic, ix, put[i], phone ? 11 : 15, col, al);
          g.label(`${phone ? sh : lab}  ·  ${fmtD(sv)}`, tx, put[i], { color: col, size: fs - 1, weight: lit ? 700 : 500, align: "left", alpha: lit ? 1 : 0.7 });
        });
        // the handle you drag
        g.glow(lx, my, 26, "#ffffff", 0.35); g.ball(lx, my, tw * 0.42, c.photon); g.ring(lx, my, tw * 0.42 + 4 + 2 * Math.sin(S.time * 3), c.ink, 1.6, 0.7);
        const nearTick = [-6, -3, 0].some((l) => Math.abs(my - Y(l)) < 16);
        g.label(fmtD(d), lx - tw / 2 - 14, my + (nearTick ? 18 : 0), { color: c.ink, size: fs + 2, weight: 700, align: "right", bg: true });
        const nb = d / 1e-7, nf = d / 6e-5, bg = d / 2.4e-3, fl = nf < 10 ? nf.toFixed(1).replace(/\.0$/, "") : big(nf), yrs = bg < 10 ? bg.toFixed(1).replace(/\.0$/, "") : Math.round(bg);
        const line = nf < 0.5 ? `${fmtD(d)}: the dose of ${big(nb)} bananas` : bg < 0.3 || phone ? `${fmtD(d)}: ${big(nb)} bananas, or ${fl} flights` : `${fmtD(d)}: ${big(nb)} bananas, ${fl} flights or ${yrs} years of background`;
        g.label(line, W * 0.5, H * 0.94, { color: c.ink, size: fs + 1, weight: 600, serif: true });
        g.label("typical values", W - 6, H - 10, { color: c.faint, size: 10, align: "right" });
        return;
      }

      if (mode === "year") {
        // ---------- your year, stacked like rock strata ----------
        const cos = 0.39 * 2 ** (S.alt / 1500);
        const L = [["radon in the air", "radon", 1.26, c.fission], ["rocks and soil", "ground", 0.48, c.warm], ["food and water", "food", 0.29, c.photon], [S.alt > 800 ? `cosmic rays at ${Math.round(S.alt)} m` : "cosmic rays", "cosmic", cos, c.accent],
          [`${Math.round(S.fl)} flights`, "flights", S.fl * 0.06, c.cool], [`${Math.round(S.ct)} chest CT`, "CT", S.ct * 7, c.proton]];
        const tot = L.reduce((s, l) => s + l[2], 0);
        S.to("ymax", Math.max(3.2, tot * 1.18));
        const ymax = S.ymax || 3.2, bx = W * (phone ? 0.24 : 0.25), bw = W * (phone ? 0.3 : 0.28), yb = H * 0.86, yt = H * 0.1, Y = (v) => yb - (yb - yt) * v / ymax;
        // reference lines
        [[2.4, phone ? "average 2.4" : "world average 2.4 mSv"], [20, phone ? "worker limit 20" : "worker limit 20 mSv"]].forEach(([v, s]) => { if (v > ymax) return; g.line(W * 0.03, Y(v), bx + bw + 8, Y(v), c.soft, 1, 0.55, [3, 5]); g.label(s, bx - 8, Y(v) - 9, { color: c.soft, size: fs - 2, align: "right" }); });
        let acc = 0; const rows = [];
        L.forEach(([lab, sh, v, col], i) => {
          if (v <= 0.0005) return;
          const ya = Y(acc), yz = Y(acc + v); acc += v;
          ctx.save(); const gr = ctx.createLinearGradient(bx, 0, bx + bw, 0); gr.addColorStop(0, g.rgba(col, 0.9)); gr.addColorStop(1, g.rgba(col, 0.55)); ctx.fillStyle = gr; ctx.fillRect(bx, yz, bw, Math.max(0.6, ya - yz)); ctx.restore();
          g.line(bx, yz, bx + bw, yz, c.paper, 1, 0.6);
          { const q = rng(40 + i), nd = Math.min(14, Math.round((ya - yz) / 7)); for (let k = 0; k < nd; k++) { const px = bx + 4 + q() * (bw - 8), py = yz + 3 + ((q() + S.time * 0.05 * (0.5 + q())) % 1) * Math.max(1, ya - yz - 6); g.dot(px, py, 1.6, "#ffffff", 0.35 + 0.3 * Math.sin(S.time * 3 + k)); } }
          rows.push([lab, sh, v, col, (ya + yz) / 2]);
        });
        g.glow(bx + bw / 2, Y(acc), bw * 0.7, c.photon, 0.25);
        // labels to the right, pushed apart so they never overlap
        const gap = fs + 6, lxx = bx + bw + 18; let prev = Infinity;
        rows.forEach((rw) => { let y = Math.min(rw[4], prev - gap); prev = y; rw[5] = y; });
        rows.forEach(([lab, sh, v, col, ym, y]) => { g.line(bx + bw + 2, ym, lxx - 4, y, col, 1, 0.5); g.label(`${phone ? sh : lab}  ${v < 1 ? v.toFixed(2) : v.toFixed(1)}`, lxx, y, { color: col, size: fs - 1, weight: 600, align: "left" }); });
        g.label("mSv", bx + bw / 2, yb + 12, { color: c.soft, size: fs - 2 });
        g.label(`your year: ${tot.toFixed(1)} mSv`, bx + bw / 2, Y(acc) - 16, { color: c.ink, size: fs + 2, weight: 700, bg: true });
        g.label(tot > 20 ? "more than the yearly worker limit" : tot > 5 ? `${(tot / 2.4).toFixed(1)} times the world average` : "close to the world average", W * 0.5, H * 0.94, { color: c.ink, size: fs + 1, weight: 600, serif: true });
        return;
      }

      // ---------- acute: dose at once ----------
      const d = 10 ** S.la, x0 = W * 0.08, y0 = H * 0.1, w = W * 0.84, h = H * (phone ? 0.5 : 0.54);
      const per = d / 1e-3; // tracks per nucleus (gamma)
      tissue(x0, y0, w, h, Math.min(per, 9), 0, 0.8 * smooth(-0.4, 0.7, S.la));
      g.label(per < 20 ? `tracks through each cell nucleus: about ${per < 2 ? per.toFixed(1).replace(/\.0$/, "") : Math.round(per)}` : `tracks through each cell nucleus: about ${big(per)} (a few drawn)`, W * 0.5, y0 - 4 < 14 ? y0 + 12 : y0 - 12, { color: c.accent, size: fs - 1, weight: 600, bg: true });
      // a strip with the zones
      const sx0 = W * 0.08, sx1 = W * 0.92, sy = y0 + h + (phone ? 24 : 34), XX = (l) => lerp(sx0, sx1, (l + 3) / 4);
      const zones = [[-3, -1, c.fission, "no effect seen"], [-1, 0, c.photon, phone ? "risk assumed" : "small added risk assumed"], [0, log10(4.5), c.warm, "sickness"], [log10(4.5), 1, c.proton, phone ? "lethal" : "often lethal"]];
      zones.forEach(([a, b, col, s]) => { ctx.save(); ctx.fillStyle = g.rgba(col, 0.35); ctx.fillRect(XX(a), sy - 5, XX(b) - XX(a), 10); ctx.restore(); g.label(s, (XX(a) + XX(b)) / 2, sy + 16, { color: col, size: fs - 2, weight: 600 }); });
      [[-3, "1 mSv"], [-2, "10 mSv"], [-1, "100 mSv"], [0, "1 Sv"], [1, "10 Sv"]].forEach(([l, s]) => g.label(s, XX(l), sy - 14, { color: c.soft, size: fs - 2 }));
      const mx = XX(S.la); g.glow(mx, sy, 18, c.ink, 0.3); g.ring(mx, sy, 8, c.ink, 2); g.dot(mx, sy, 3, c.ink);
      const msg = d < 0.1 ? "any extra risk too small to measure" : d < 1 ? "no sickness; risk assumed to rise with dose" : d < 4 ? "radiation sickness: nausea, low blood counts" : "about half die without treatment";
      g.label(`${fmtD(d)} at once: ${msg}`, W * 0.5, H * 0.94, { color: c.ink, size: fs + 1, weight: 600, serif: true });
    },
  });
})();
