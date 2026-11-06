/* Three accidents, explained: Three Mile Island 2 (1979), Chernobyl 4 (1986), Fukushima Daiichi (2011). Scenes (S.mode):
 *   "tmi"  = TMI-2, 28 March 1979 (NRC Backgrounder "Backgrounder on the Three Mile Island Accident"; Rogovin report 1980).
 *            Facts used: rated 2772 MWt (906 MWe) pressurised water reactor; the pilot-operated relief valve (PORV) on the
 *            pressurizer opened and stuck open, with the control-room light showing only that the valve had been told to
 *            close; the pressurizer level read high, so operators throttled high-pressure injection; reactor coolant pumps
 *            were stopped at about 1 h 13 min and 1 h 40 min; the block valve behind the PORV was closed at about 2 h 22 min;
 *            full injection was restored at about 3 h 20 min; "about half of the core melted"; the containment held most
 *            of the radioactivity; average dose to the ~2 million people nearby about 1 millirem (0.01 mSv) (NRC).
 *            The coolant model is illustrative: inventory i (1 = full) falls by a leak 0.0042/min through the open valve and
 *            gains 0.0012/min (throttled injection) or 0.008/min (full); collapsed vessel level = 1.6 i - 0.6; the pumps keep
 *            a two-phase mixture over the core until 1 h 40 min; melting begins after 12 "uncovered-core minutes" and grows
 *            with the uncovered fraction, tuned so that the historical sequence gives about one half. Clock 6 min per second.
 *   "void" = Chernobyl 4, 26 April 1986 (IAEA INSAG-7, 1992; WNA "RBMK reactors" appendix). Facts: RBMK-1000, 3200 MWt;
 *            at the test the power was about 200 MWt, the core xenon-poisoned after a long run at low power, the operating
 *            reactivity margin below the 15 rod equivalents required; at low power the void coefficient was strongly
 *            positive and dominated the (negative) fuel Doppler coefficient. Model (illustrative, as in feedback.js):
 *            one-group point kinetics, beta = 0.005, Lambda = 1 ms (graphite), lambda = 0.08/s; fuel time constant 4 s,
 *            600 K per full power; void fraction relaxes in 1.5 s to 0.12 (n / n0) / flow; Doppler -2 pcm/K; the reader sets
 *            the void coefficient (-10 .. +30 pcm per % steam). "Run the pumps down" lowers flow to 75 % with an 8 s time
 *            constant. Power axis is logarithmic; the run stops above 300 %.
 *   "rod"  = the positive scram effect (INSAG-7; WNA): each rod had a 4.5 m graphite displacer; with the rod fully withdrawn
 *            it sat in the middle of the 7 m core with 1.25 m of water above and below; full insertion took about 18 s
 *            (0.39 m/s). AZ-5 was pressed at 01:23:40; the power surge followed within seconds (INSAG-7).
 *            Worth model (illustrative): local weight phi^2 with an axial flux bottom-weighted, phi = sin(pi z/H) e^(-2.5 z/H);
 *            relative absorption water -1, graphite 0, absorber -10. Curves: whole core and lower half.
 *   "blackout" = Fukushima Daiichi, 11 March 2011 (IAEA "The Fukushima Daiichi Accident", Director General report, 2015).
 *            Facts: units 1-3 operating, scrammed automatically on the earthquake at 14:46; off-site power lost; diesels
 *            started; tsunami waves from about 15:27, the largest about 15:35, some 14-15 m high at a site 10 m above sea
 *            level (design basis 5.7 m); station blackout in units 1-5 from about 15:37-15:42. Unit 1: 1380 MWt; units 2-3:
 *            2381 MWt. Decay heat: Way-Wigner 0.066 [t^-0.2 - (t+T)^-0.2], T = 1 year (as in afterheat.js). Boil-off: decay
 *            power / 2.0 MJ/kg (latent heat 1.5 MJ/kg at 7 MPa .. 2.26 MJ/kg at 1 atm, plus heating). Water level drawn for unit 1
 *            "if no water is added" from 0.85 h, with 80 t above the top of the fuel and 25 t in the core region (illustrative).
 *   "h2"   = Zr + 2 H2O -> ZrO2 + 2 H2, about 586 kJ per mol Zr (6.4 MJ/kg Zr) released; 1 kg Zr gives 44 g H2 (stoichiometry).
 *            Parabolic rate constant (Cathcart-Pawel, ORNL/NUREG-17, 1977): K = 0.3622 exp(-20100/T) (g/cm^2)^2/s, shown
 *            relative to 1000 C. Explosions in reactor buildings: unit 1 12 March 15:36, unit 3 14 March 11:01, unit 4
 *            15 March about 06:14 (hydrogen from unit 3 through the shared vent line); unit 2's building did not explode (IAEA 2015).
 *   "after" = what changed. TMI: direct valve-position indication, subcooling monitors, training and simulators (NRC Action Plan,
 *            NUREG-0660); passive decay-heat removal in newer designs, e.g. AP1000 72 h without operator action or AC power (vendor).
 *            RBMK (WNA): enrichment 2.0 -> 2.4 %, 80-90 extra fixed absorbers, void coefficient reduced to about +1 beta,
 *            minimum ORM 26-30 -> 43-48 rods, scram time 18 -> 12 s, fast scram of 24 rods in under 2.5 s, rods no longer
 *            leave water below the displacer. Fukushima: FLEX portable pumps and generators (NRC order EA-12-049), hardened
 *            containment vents (EA-12-050, EA-13-109), hydrogen recombiners and filtered vents (EU stress tests), higher
 *            tsunami walls and new regulatory requirements in Japan (NRA, 2013).
 * Casualty figures are deliberately left out. */
(function () {
  const { TAU, clamp, lerp, smooth, rng } = WT.util;
  const r = rng(53), fl = []; for (let i = 0; i < 80; i++) fl.push(r());
  const ill = (g) => g.label("illustration", g.W - 6, g.H - 10, { color: g.c.faint, size: 10, align: "right" });
  const ww = (h) => { const t = Math.max(h * 3600, 1); return 0.066 * (Math.pow(t, -0.2) - Math.pow(t + 3.156e7, -0.2)); };
  const hm = (min) => { const m = Math.max(0, Math.round(min)); return m < 60 ? WT.trf("{a} min", m) : WT.trf("{a} h {b} min", Math.floor(m / 60), m % 60); };
  function box(g, x, y, w, h, rad, fill, stroke, lw = 1.4) { const { ctx } = g; ctx.save(); ctx.beginPath(); if (ctx.roundRect) ctx.roundRect(x, y, w, h, rad); else ctx.rect(x, y, w, h); if (fill) { ctx.fillStyle = fill; ctx.fill(); } if (stroke) { ctx.strokeStyle = stroke; ctx.lineWidth = lw; ctx.stroke(); } ctx.restore(); }
  function setPressed(sel, on) { document.querySelectorAll(`#accidents [data-act="${sel}"]`).forEach((b) => b.setAttribute("aria-pressed", String(!!on))); }
  /** fuel rods inside (x0..x1, y0..y1); `melt` turns the lower part into a molten mass; `hot` 0..1 colours exposed rods */
  function fuel(g, S, x0, x1, y0, y1, n, glow, hot, melt) {
    const { c, ctx } = g, fw = Math.max(2.5, (x1 - x0) / n * 0.42), my = lerp(y1, y0, clamp(melt * 1.1, 0, 1));
    for (let i = 0; i < n; i++) {
      const x = lerp(x0, x1, (i + 0.5) / n), col = hot > 0.5 ? c.proton : c.warm;
      ctx.save(); ctx.fillStyle = g.rgba(col, 0.45 + 0.4 * glow); ctx.fillRect(x - fw / 2, y0, fw, Math.max(0, my - y0)); ctx.restore();
      if (glow > 0.05) g.glow(x, (y0 + y1) / 2, fw * 3, c.photon, 0.12 * glow * (0.8 + 0.2 * Math.sin(S.time * 6 + i)));
    }
    if (melt > 0.01) { // a rubble/molten mass where the lower rods were
      const pts = []; for (let i = 0; i <= 24; i++) { const u = i / 24, x = lerp(x0 - 4, x1 + 4, u); pts.push([x, my - 6 * Math.sin(Math.PI * u) - 2 * Math.sin(u * 17 + S.time * 1.5)]); }
      pts.push([x1 + 4, y1], [x0 - 4, y1]); g.area(pts, c.proton, 0.75); g.glow((x0 + x1) / 2, (my + y1) / 2, (x1 - x0) * 0.7, c.photon, 0.35);
    }
  }
  /** water up to level y (with rising bubbles), inside a clipped region */
  function water(g, S, x, y, w, h, lvlY, boil, seed = 0) {
    const { c, ctx } = g; if (lvlY >= y + h) return;
    ctx.save(); const wg = ctx.createLinearGradient(0, lvlY, 0, y + h); wg.addColorStop(0, g.rgba(c.cool, 0.3)); wg.addColorStop(1, g.rgba(c.cool, 0.5)); ctx.fillStyle = wg; ctx.fillRect(x, lvlY, w, y + h - lvlY); ctx.restore();
    g.line(x, lvlY, x + w, lvlY, c.cool, 1.6, 0.9);
    const nb = Math.round(36 * clamp(boil, 0, 1.5));
    for (let i = 0; i < nb; i++) { const k = (i * 7 + seed) % 80, u = fl[k], v = (fl[(k + 13) % 80] + S.time * (0.25 + 0.3 * fl[(k + 29) % 80])) % 1, by = lerp(y + h, lvlY, v); if (by < lvlY + 2) continue; g.ring(x + w * (0.06 + 0.88 * u) + 2 * Math.sin(S.time * 4 + i), by, 1.6 + 2 * v, "#ffffff", 1, 0.7); }
  }

  // ================= TMI =================
  const CT = 0.55, CB = 0.12, TMI_END = 300;
  const tmi = { t: 0, inv: 1, melt: 0, unc: 0, sw: 0, block: -1, hpi: -1, ub: false, uh: false };
  function tmiReset() { Object.assign(tmi, { t: 0, inv: 1, melt: 0, unc: 0, sw: 0, block: -1, hpi: -1, ub: false, uh: false }); setPressed("acHpi", false); setPressed("acBlk", false); }
  function tmiLvl() { const lvl = clamp(1.6 * tmi.inv - 0.6, 0, 1); return { lvl, eff: tmi.t < 100 ? Math.max(lvl, 0.62) : lvl }; }
  function tmiAdv(min) {
    const n = Math.ceil(min / 0.05), d = min / n;
    for (let i = 0; i < n && tmi.t < TMI_END; i++) {
      if (tmi.block < 0 && tmi.t >= 142) { tmi.block = 142; setPressed("acBlk", true); }
      if (tmi.hpi < 0 && tmi.t >= 200) { tmi.hpi = 200; setPressed("acHpi", true); }
      const open = tmi.block < 0, L = open ? 0.0042 : 0, J = tmi.hpi >= 0 ? 0.008 : 0.0012;
      tmi.inv = clamp(tmi.inv + (J - L) * d, 0.3, 1);
      tmi.sw = clamp(tmi.sw + (open && tmi.t > 1.5 ? 0.25 : -0.012) * d, 0, 1);
      const { eff } = tmiLvl(), e = clamp((CT - eff) / (CT - CB), 0, 1);
      tmi.unc += e * d; if (tmi.unc > 12) tmi.melt = Math.min(0.9, tmi.melt + 0.022 * e * d * (1 - tmi.melt * 0.5));
      tmi.t += d;
    }
  }
  const geo = {};
  function drawTMI(g, S, dt, phone, fs, snap) {
    const { W, H, c, ctx } = g;
    if (snap) { if (tmi.t === 0) tmiAdv(125); } else if (dt > 0) tmiAdv(dt * 6);
    const { lvl, eff } = tmiLvl(), open = tmi.block < 0, ind = clamp(0.5 - 0.22 * smooth(0, 1.5, tmi.t) + 0.72 * tmi.sw * (tmi.inv > 0.4 ? 1 : 0.6), 0.05, 1);
    // layout: containment dome holding vessel and pressurizer; meters and clock below (desktop: at the right)
    const top = phone ? 18 : 30, bot = phone ? H * 0.66 : H * 0.8, vh = (bot - top) * 0.72, vw = Math.min(vh * 0.42, W * (phone ? 0.2 : 0.16));
    const vx = W * (phone ? 0.24 : 0.2) - vw / 2, vy = bot - vh - (bot - top) * 0.05;
    const pw = vw * 0.42, ph = vh * 0.62, px = vx + vw + W * (phone ? 0.13 : 0.1), py = vy - vh * 0.08;
    const dome = { x: vx - vw * 0.35, y: top + 4, w: px + pw + vw * 1.15 - (vx - vw * 0.35), h: bot - top };
    // containment
    ctx.save(); ctx.beginPath(); const dr = dome.w / 2; ctx.moveTo(dome.x, dome.y + dome.h); ctx.lineTo(dome.x, dome.y + Math.min(dr, dome.h * 0.45)); ctx.ellipse(dome.x + dr, dome.y + Math.min(dr, dome.h * 0.45), dr, Math.min(dr, dome.h * 0.45), 0, Math.PI, 0); ctx.lineTo(dome.x + dome.w, dome.y + dome.h); ctx.closePath();
    ctx.fillStyle = g.rgba(c.soft, 0.05); ctx.strokeStyle = g.rgba(c.soft, 0.45); ctx.lineWidth = 3; ctx.fill(); ctx.stroke(); ctx.restore();
    g.label("containment", dome.x + dome.w / 2, dome.y + dome.h - 10, { color: c.soft, size: fs - 1 });
    // vessel
    const coreT = vy + vh * (1 - CT), coreB = vy + vh * (1 - CB);
    ctx.save(); ctx.beginPath(); if (ctx.roundRect) ctx.roundRect(vx, vy, vw, vh, vw * 0.45); else ctx.rect(vx, vy, vw, vh); ctx.clip();
    ctx.fillStyle = g.rgba(c.soft, 0.08); ctx.fillRect(vx, vy, vw, vh);
    water(g, S, vx, vy, vw, vh, vy + vh * (1 - (tmi.t < 100 ? eff : lvl)), tmi.t < 100 ? 1 : 0.5, 0);
    const exposed = clamp((CT - eff) / (CT - CB), 0, 1);
    fuel(g, S, vx + vw * 0.16, vx + vw * 0.84, coreT, coreB, phone ? 5 : 7, 0.4, exposed, tmi.melt);
    ctx.restore();
    box(g, vx, vy, vw, vh, vw * 0.45, null, g.rgba(c.ink, 0.55), 2);
    if (exposed > 0 && tmi.melt < 0.02) g.glow(vx + vw / 2, coreT, vw * 0.8, c.proton, 0.25 * exposed);
    // surge line, pressurizer, valve, drain tank
    const hl = vy + vh * 0.22;
    g.line(vx + vw, hl, px + pw / 2, hl, c.soft, 5, 0.5); g.line(px + pw / 2, hl, px + pw / 2, py + ph, c.soft, 5, 0.5);
    ctx.save(); ctx.beginPath(); if (ctx.roundRect) ctx.roundRect(px, py, pw, ph, pw / 2); else ctx.rect(px, py, pw, ph); ctx.clip();
    ctx.fillStyle = g.rgba(c.soft, 0.08); ctx.fillRect(px, py, pw, ph);
    water(g, S, px, py, pw, ph, py + ph * (1 - ind), open ? 0.6 : 0.1, 17); ctx.restore();
    box(g, px, py, pw, ph, pw / 2, null, g.rgba(c.ink, 0.55), 2);
    const vX = px + pw / 2, vY = py - (phone ? 16 : 22), vs = phone ? 8 : 11;
    g.line(vX, py, vX, vY, c.soft, 4, 0.6);
    const tx = px + pw + vw * 0.6;
    g.line(vX, vY, tx, vY, c.soft, 4, 0.6); g.line(tx, vY, tx, vY + vh * 0.5, c.soft, 4, 0.6);
    box(g, tx - vw * 0.25, vY + vh * 0.5, vw * 0.5, vh * 0.2, 8, g.rgba(c.soft, 0.1), g.rgba(c.ink, 0.4));
    // the valve (bow tie), open = steam jets along the line
    const vcol = open ? c.proton : c.fission;
    g.area([[vX - vs, vY - vs * 0.7], [vX + vs, vY + vs * 0.7], [vX + vs, vY - vs * 0.7], [vX - vs, vY + vs * 0.7]], vcol, 0.85);
    g.glow(vX, vY, vs * 3.2, vcol, open ? 0.35 + 0.15 * Math.sin(S.time * 6) : 0.15);
    geo.valve = { x: vX, y: vY, r: vs * 3 };
    if (open) for (let i = 0; i < 12; i++) { const f = (fl[i] + S.time * 0.6) % 1, L = (tx - vX) + vh * 0.5, d = f * L, x = d < tx - vX ? vX + d : tx, y = d < tx - vX ? vY : vY + (d - (tx - vX)); g.dot(x + (fl[i + 20] - 0.5) * 4, y + (fl[i + 40] - 0.5) * 4, 3 - 2 * f, "#ffffff", 0.6 * (1 - f)); g.glow(x, y, 8, c.cool, 0.3 * (1 - f)); }
    g.label(open ? (phone ? "valve stuck open" : "relief valve stuck open") : (phone ? "block valve shut" : "block valve closed"), vX + (phone ? 0 : 4), vY - vs - 12, { color: vcol, size: fs - 1, weight: 700, bg: true, align: phone ? "center" : "left" });
    // injection pump into the vessel
    const pX = vx - (phone ? vw * 0.35 : vw * 0.2), pY = vy + vh * 0.82 + (phone ? 0 : 0), pr = phone ? 10 : 13, full = tmi.hpi >= 0;
    g.line(pX + pr, pY, vx, pY, c.cool, 3, 0.7);
    g.ball(pX, pY, pr, c.cool, full ? 1 : 0.5); geo.pump = { x: pX, y: pY, r: pr * 2.2 };
    ctx.save(); ctx.translate(pX, pY); ctx.rotate(S.time * (full ? 6 : 1.2)); g.line(-pr * 0.6, 0, pr * 0.6, 0, "#ffffff", 2, 0.9); g.line(0, -pr * 0.6, 0, pr * 0.6, "#ffffff", 2, 0.9); ctx.restore();
    g.label(full ? (phone ? "full" : "injection full") : (phone ? "throttled" : "injection throttled"), pX, pY + pr + 12, { color: c.cool, size: fs - 1, weight: 600, bg: true });
    // ---- the two readings: what the operators saw vs what the core had ----
    const mx = phone ? W * 0.06 : W * 0.66, my = phone ? H * 0.73 : H * 0.14, mw = phone ? W * 0.88 : W * 0.3, gap = phone ? 26 : 58;
    const rows = [[phone ? "pressurizer level (seen)" : "pressurizer level: what they saw", ind, c.photon, ind > 0.9 ? "full" : ""], [phone ? "water over the core (real)" : "water over the core: what was real", clamp((eff - CB) / (1 - CB), 0, 1), c.cool, eff < CT ? (phone ? "uncovered" : "core uncovered") : ""]];
    rows.forEach(([nm, v, col, tag], i) => {
      const y = my + i * gap;
      g.label(nm, mx, y - 11, { color: c.soft, size: fs - 1, align: "left" });
      box(g, mx, y - 4, mw, 9, 4, g.rgba(c.soft, 0.12)); box(g, mx, y - 4, Math.max(4, mw * v), 9, 4, col);
      if (tag) g.label(tag, mx + mw, phone ? y - 11 : y + 16, { color: i ? c.proton : col, size: fs - 1, weight: 700, align: "right" });
    });
    // core state + clock
    const cyy = phone ? 12 : my + 2 * gap + 4;
    if (!phone) {
      g.label(WT.trf("time {a}", hm(tmi.t)), mx, cyy, { color: c.ink, size: fs + 4, weight: 700, align: "left", serif: true, raw: true });
      const st = tmi.melt > 0.02 ? WT.trf("core melted: about {a} %", Math.round(tmi.melt * 20) * 5) : exposed > 0 ? WT.tr("fuel heating up") : WT.tr("core covered");
      g.label(st, mx, cyy + 28, { color: tmi.melt > 0.02 ? c.proton : exposed > 0 ? c.warm : c.fission, size: fs + 1, weight: 700, align: "left", raw: true });
      if (tmi.melt > 0.02) g.label("most radioactivity stayed in containment", mx, cyy + 52, { color: c.soft, size: fs - 1, align: "left" });
    } else {
      const st = tmi.melt > 0.02 ? WT.trf("melted ≈ {a} %", Math.round(tmi.melt * 20) * 5) : exposed > 0 ? WT.tr("fuel heating") : WT.tr("core covered");
      g.label(`${hm(tmi.t)} · ${st}`, W - 8, 12, { color: tmi.melt > 0.02 ? c.proton : c.ink, size: fs, weight: 700, align: "right", raw: true });
    }
    // timeline with the day's actions
    const tx0 = phone ? W * 0.06 : W * 0.06, tx1 = W * 0.94, ty = phone ? H * 0.89 : H * 0.9, X = (m) => lerp(tx0, tx1, m / TMI_END);
    g.line(tx0, ty, tx1, ty, c.line, 2); g.line(tx0, ty, X(tmi.t), ty, c.accent, 3);
    g.dot(X(tmi.t), ty, 5, c.accent); g.glow(X(tmi.t), ty, 14, c.accent, 0.4);
    const ev = [[100, phone ? "pumps off" : "pumps off 1:40", c.soft], [tmi.block >= 0 ? tmi.block : 142, tmi.block >= 0 && tmi.block !== 142 ? (phone ? "you shut it" : "you closed the valve") : phone ? "valve 2:22" : "block valve 2:22", c.fission], [tmi.hpi >= 0 ? tmi.hpi : 200, tmi.hpi >= 0 && tmi.hpi !== 200 ? (phone ? "you" : "you: full injection") : phone ? "inject 3:20" : "injection 3:20", c.cool]];
    ev.forEach(([m, s, col], i) => { const x = X(m); g.line(x, ty - 6, x, ty + 6, col, 2); g.label(s, x, ty + (i % 2 ? -16 : 16), { color: col, size: fs - 2, weight: 600 }); });
    if (!phone) g.label("illustrative model, timings as on 28 March 1979", W - 6, H - 10, { color: c.faint, size: 10, align: "right" });
  }

  // ================= Chernobyl: void feedback =================
  const VB = 0.005, VL = 0.08, VLG = 1e-3, VN0 = 0.0625, VXS = 0.12, VAD = -2;
  const cv = { n: VN0, C: 0, Tf: 0, x: VXS, flow: 1, t: 0, rd: -1, hist: [], halt: false };
  function cvReset() { Object.assign(cv, { n: VN0, C: VB * VN0 / (VL * VLG), Tf: 0, x: VXS, flow: 1, t: 0, rd: -1, hist: [], halt: false }); }
  cvReset();
  const cvRho = (S) => S.av * 1e-5 * 100 * (cv.x - VXS) + VAD * 1e-5 * cv.Tf;
  function cvAdv(S, sec) {
    if (cv.halt) return; const n = Math.ceil(sec / 0.0005), d = sec / n;
    for (let i = 0; i < n; i++) {
      cv.flow = cv.rd < 0 ? 1 : 0.75 + 0.25 * Math.exp(-(cv.t - cv.rd) / 8);
      const rho = cvRho(S), dn = (rho - VB) / VLG * cv.n + VL * cv.C, dC = VB / VLG * cv.n - VL * cv.C;
      cv.n = Math.max(1e-4, cv.n + dn * d); cv.C += dC * d; cv.Tf += ((cv.n - VN0) * 150 - cv.Tf / 4) * d;
      cv.x += (clamp(VXS * (cv.n / VN0) / cv.flow, 0, 0.9) - cv.x) / 1.5 * d; cv.t += d;
      const lh = cv.hist[cv.hist.length - 1]; if (!lh || cv.t - lh[0] >= 0.05) { cv.hist.push([cv.t, cv.n]); if (cv.hist.length > 900) cv.hist.shift(); }
      if (cv.n > 3) { cv.halt = true; break; }
    }
  }
  function drawVoid(g, S, dt, phone, fs, snap) {
    const { W, H, c, ctx } = g;
    if (snap) { if (cv.t === 0) { cvAdv(S, 3); cv.rd = cv.t; cvAdv(S, 16); } } else if (dt > 0) cvAdv(S, dt);
    if (!snap && S.step === 1 && cv.rd < 0 && cv.t > 3 && !S.vFired) { S.vFired = true; cv.rd = cv.t; }
    const lp = clamp((Math.log10(cv.n) + 2) / 2.5, 0, 1); // brightness: 1 % .. 300 %
    // core: graphite block with channels
    const cw = phone ? W * 0.42 : Math.min(W * 0.36, H * 0.52), ch = phone ? H * 0.42 : Math.min(H * 0.4, cw * 0.8), cx = phone ? W * 0.27 : W * 0.24, cy = phone ? H * 0.27 : H * 0.3;
    const x0 = cx - cw / 2, y0 = cy - ch / 2;
    g.glow(cx, cy, cw * 0.9, c.warm, 0.1 + 0.4 * lp);
    box(g, x0, y0, cw, ch, 10, g.rgba(c.soft, 0.16), g.rgba(c.ink, 0.45), 1.5);
    const nC = phone ? 5 : 7;
    for (let i = 0; i < nC; i++) {
      const x = lerp(x0, x0 + cw, (i + 0.5) / nC), w = cw / nC * 0.42;
      ctx.save(); ctx.beginPath(); ctx.rect(x - w / 2, y0 + 6, w, ch - 12); ctx.clip();
      ctx.fillStyle = g.rgba(c.cool, 0.45); ctx.fillRect(x - w / 2, y0, w, ch);
      ctx.fillStyle = g.rgba(c.photon, 0.15 + 0.6 * lp); ctx.fillRect(x - w * 0.15, y0 + 6, w * 0.3, ch - 12);
      const nb = Math.round(40 * cv.x / 0.5);
      for (let k = 0; k < nb; k++) { const u = fl[(k * 3 + i * 11) % 80], v = (fl[(k * 7 + i) % 80] + S.time * (0.3 + cv.x * 1.5)) % 1; const by = lerp(y0 + ch, y0 + ch * 0.1, v * (0.3 + 0.7 * v)); g.dot(x + (u - 0.5) * w * 0.8, by, 1.2 + 2.2 * v * cv.x * 2, "#ffffff", 0.8); }
      ctx.restore();
    }
    g.label(phone ? "steam in channels" : "steam in the channels", cx, y0 + ch + 14, { color: c.soft, size: fs - 1 });
    g.label(WT.trf("{a} % steam", (100 * cv.x).toFixed(0)), cx, y0 - 13, { color: c.cool, size: fs, weight: 700, bg: true, raw: true });
    // the loop: power -> steam -> reactivity -> power
    const lx = phone ? W * 0.75 : W * 0.62, ly = cy, lr = phone ? Math.min(W * 0.17, H * 0.17) : Math.min(W * 0.13, H * 0.18), pos = S.av > 0;
    const nodes = [[lx, ly - lr, "power", c.warm], [lx + lr * 0.95, ly + lr * 0.6, "steam", c.cool], [lx - lr * 0.95, ly + lr * 0.6, "reactivity", pos ? c.proton : c.fission]];
    const sig = clamp(Math.abs(Math.log(cv.n / VN0)) * 0.8 + 0.1, 0.1, 1.5);
    nodes.forEach((a, k) => {
      const b = nodes[(k + 1) % 3], dx = b[0] - a[0], dy = b[1] - a[1], L = Math.hypot(dx, dy), ux = dx / L, uy = dy / L, rr = phone ? 15 : 20;
      const ax = a[0] + ux * rr, ay = a[1] + uy * rr, bx = b[0] - ux * (rr + 4), by = b[1] - uy * (rr + 4), col = k === 1 ? (pos ? c.proton : c.fission) : a[3];
      g.arrow(ax, ay, bx, by, col, 1.6, 0.35, 8);
      for (let i = 0; i < 3; i++) { const f = (fl[k * 5 + i] + S.time * 0.25 * (0.3 + sig)) % 1; g.glow(lerp(ax, bx, f), lerp(ay, by, f), 10 + 8 * sig, col, 0.5 * Math.min(1, sig)); g.dot(lerp(ax, bx, f), lerp(ay, by, f), 2.6, "#ffffff", 0.8); }
      if (k === 1) g.label(pos ? (phone ? "more" : "more steam → more") : (phone ? "less" : "more steam → less"), (ax + bx) / 2, (ay + by) / 2 + (phone ? 14 : 18), { color: col, size: fs - 1, weight: 700, bg: true });
    });
    nodes.forEach(([x, y, s, col]) => { g.ball(x, y, phone ? 9 : 12, col, 0.95); g.label(s, x, y + (y < ly ? -(phone ? 20 : 26) : phone ? 20 : 26), { color: col, size: fs, weight: 700, bg: true }); });
    // power trace, log scale
    const px0 = W * (phone ? 0.13 : 0.1), px1 = W * 0.95, py0 = H * (phone ? 0.6 : 0.6), py1 = H * (phone ? 0.86 : 0.86), WIN = 40;
    const tE = Math.max(WIN, cv.t), tS = tE - WIN, Xt = (t) => lerp(px0, px1, (t - tS) / WIN), Yp = (p) => lerp(py1, py0, clamp((Math.log10(p) + 2) / 2.5, 0, 1.03));
    [0.01, 0.1, 1, 3].forEach((p) => { g.line(px0, Yp(p), px1, Yp(p), c.line, 1, p === 1 ? 0.9 : 0.4, p === 1 ? null : [2, 5]); g.label(`${(100 * p).toFixed(0)} %`, px0 - 6, Yp(p), { color: c.faint, size: fs - 2, align: "right" }); });
    const pts = cv.hist.filter((h) => h[0] >= tS).map(([t, n]) => [Xt(t), Yp(n)]);
    if (pts.length > 1) { g.poly(pts, c.warm, 2.4); const l = pts[pts.length - 1]; g.glow(l[0], l[1], 16, c.warm, 0.6); g.dot(l[0], l[1], 4.5, c.warm); }
    if (cv.rd >= tS && cv.rd >= 0) { const xr = Xt(cv.rd); g.line(xr, py0, xr, py1, c.cool, 1.2, 0.7, [3, 3]); g.label(phone ? "pumps down" : "pumps run down", xr + 4, py0 + 8, { color: c.cool, size: fs - 1, align: "left" }); }
    g.label(phone ? "power (log)" : "power, % of full (log scale)", px0, py0 - 14, { color: c.soft, size: fs - 1, align: "left" });
    g.label(phone ? "full power" : "full power 3200 MW", px1, Yp(1) - 10, { color: c.soft, size: fs - 2, align: "right" });
    const vy = H * (phone ? 0.95 : 0.94), pc = VAD * 600 + S.av * 100 * VXS / VN0;
    const s = cv.halt ? (phone ? "power ran away" : "power ran away: past full power in seconds") : cv.rd < 0 ? (phone ? "about 6 % power, steady" : "about 200 MW, 6 % of full power: steady") : pc > 0 ? (phone ? "steam feeds the power" : "positive feedback: steam feeds the power") : (phone ? "steam damps the power" : "negative feedback: steam damps the power");
    g.label(s, W / 2, vy, { color: cv.halt || (cv.rd >= 0 && pc > 0) ? c.proton : c.ink, size: fs + 1, weight: 600, serif: true });
    if (!phone) g.label("illustrative model", W - 6, H - 10, { color: c.faint, size: 10, align: "right" });
  }

  // ================= Chernobyl: the rods =================
  const HC = 7, NZ = 140, VR = 7 / 18;
  const phi = (z) => Math.sin(Math.PI * z / HC) * Math.exp(-2.5 * z / HC);
  function mat(z, d, fixed) { if (z >= HC - d) return -10; const dt = (fixed ? HC - 1.25 : 5.75) - d, db = fixed ? -9 : 1.25 - d; if (z >= dt) return -1; if (z >= db) return 0; return -1; }
  let PHN = 0; for (let i = 0; i < NZ; i++) PHN += phi((i + 0.5) * HC / NZ) ** 2;
  function worth(d, fixed, lo) { let s = 0; for (let i = 0; i < NZ; i++) { const z = (i + 0.5) * HC / NZ; if (lo && z >= 3.5) continue; s += phi(z) ** 2 * (mat(z, d, fixed) - mat(z, 0, fixed)); } return s / PHN; }
  const rod = { d: 0, go: -1, drag: false };
  function drawRod(g, S, dt, phone, fs, snap) {
    const { W, H, c, ctx } = g, fixed = !!S.fixed;
    if (snap && rod.go < 0 && rod.d === 0) { rod.d = 1.0; rod.go = S.time; rod.snap = true; }
    if (rod.go >= 0 && !rod.drag && !rod.snap) rod.d = Math.min(HC, rod.d + VR * dt);
    // core column
    const ch = phone ? H * 0.72 : H * 0.7, ct = phone ? H * 0.12 : H * 0.15, cb = ct + ch, M = ch / HC, Z = (z) => cb - z * M;
    const rx = phone ? W * 0.3 : W * 0.3, rw = phone ? 22 : 30, cw = phone ? W * 0.36 : Math.min(W * 0.3, 260);
    // graphite block either side of the channel, with the flux profile
    box(g, rx - cw / 2, ct, cw, ch, 6, g.rgba(c.soft, 0.12), g.rgba(c.ink, 0.35));
    const loPos = worth(rod.d, fixed, true) > 0.001;
    const pr = []; for (let i = 0; i <= 40; i++) { const z = i / 40 * HC; pr.push([rx - cw / 2 + 6 + phi(z) / 0.62 * (cw / 2 - rw - 14), Z(z)]); }
    g.area([[rx - cw / 2 + 6, cb], ...pr, [rx - cw / 2 + 6, ct]], c.warm, 0.18); g.poly(pr, c.warm, 1.8, 0.8);
    if (loPos) g.glow(rx, Z(1.2), cw * 0.6, c.proton, 0.25 + 0.1 * Math.sin(S.time * 8));
    g.label(phone ? "flux" : "neutron flux", rx - cw / 2 + 8, ct - 12, { color: c.warm, size: fs - 1, align: "left" });
    // the channel and the rod's segments (absorber / water / graphite / water)
    ctx.save(); ctx.beginPath(); ctx.rect(rx - rw / 2, ct - H * 0.12, rw, ch + H * 0.12); ctx.clip();
    const seg = (z0, z1, col, a) => { ctx.fillStyle = g.rgba(col, a); ctx.fillRect(rx - rw / 2, Z(z1), rw, Z(z0) - Z(z1)); };
    seg(-2, 12, c.cool, 0.4);
    const dTop = (fixed ? HC - 1.25 : 5.75) - rod.d, dBot = fixed ? -9 : 1.25 - rod.d;
    seg(Math.max(dBot, -2), dTop, c.faint, 0.95); seg(HC - rod.d, HC + 6, c.neutron, 0.95);
    ctx.restore();
    box(g, rx - rw / 2, ct, rw, ch, 3, null, g.rgba(c.ink, 0.6), 1.5);
    // handle on top: drag the rod
    const hy = Z(HC - rod.d) - 4; g.line(rx, hy, rx, ct - H * 0.08, c.neutron, 3, 0.6); g.ball(rx, ct - H * 0.08 + 2, phone ? 8 : 10, c.neutron); geo.rod = { x: rx, y0: ct - H * 0.1, y1: cb, M, ct };
    // segment labels at the right of the channel
    const lab = (z, s, col) => { if (z > -0.3 && z < HC + 0.3) g.label(s, rx + rw / 2 + 8, Z(z), { color: col, size: fs - 1, weight: 600, align: "left", bg: true }); };
    lab(clamp((HC - rod.d + HC) / 2, HC - rod.d, HC), "absorber", c.neutron);
    if (!fixed || dTop < HC) lab((dTop + Math.min(HC, HC - rod.d)) / 2, "water", c.cool);
    lab(clamp((Math.max(dBot, 0) + Math.min(dTop, HC)) / 2, 0.2, HC - 0.2), phone ? "graphite" : "graphite tip", c.soft);
    if (!fixed && dBot > 0.15) lab(dBot / 2, "water", c.cool);
    g.label("7 m", rx - cw / 2 - 8, (ct + cb) / 2, { color: c.soft, size: fs - 2, align: "right" });
    // worth chart vs time since AZ-5
    const gx0 = phone ? W * 0.62 : W * 0.56, gx1 = W * 0.95, gy0 = phone ? H * 0.2 : H * 0.24, gy1 = phone ? H * 0.78 : H * 0.72, TT = 18;
    const Xt = (t) => lerp(gx0, gx1, t / TT), Yr = (v) => lerp(gy1, gy0, clamp((v + 0.6) / 0.9, -0.02, 1.02)), y0 = Yr(0);
    g.line(gx0, y0, gx1, y0, c.ink, 1, 0.5);
    [0, 6, 12, 18].forEach((t) => g.label(WT.trf("{a} s", t), Xt(t), gy1 + 50, { color: c.soft, size: fs - 2, raw: true }));
    g.label(phone ? "rod reactivity" : "reactivity from the rod", gx0, gy0 - 34, { color: c.soft, size: fs - 1, align: "left" });
    g.area([[gx0, gy0], [gx1, gy0], [gx1, y0], [gx0, y0]], c.proton, 0.05);
    g.label(phone ? "+ adds" : "+ adds reactivity", gx0 + 4, gy0 + 10, { color: c.proton, size: fs - 2, align: "left" });
    g.label(phone ? "− removes" : "− removes reactivity", gx0 + 4, gy1 - 10, { color: c.fission, size: fs - 2, align: "left" });
    [[false, c.ink, phone ? "whole core" : "whole core"], [true, c.proton, phone ? "lower half" : "lower half of core"]].forEach(([lo, col, nm], k) => {
      const pts = []; for (let i = 0; i <= 90; i++) { const t = i / 90 * TT; pts.push([Xt(t), Yr(worth(Math.min(HC, t * VR), fixed, lo) * (lo ? 1 : 1))]); }
      g.clip(gx0, gy0 - 4, gx1 - gx0, gy1 - gy0 + 8); g.poly(pts, col, 2.2, lo ? 0.9 : 0.75, lo ? [5, 4] : null); ctx.restore();
      g.label(nm, gx1, (lo ? gy1 + 14 : gy1 + 30), { color: col, size: fs - 2, weight: 600, align: "right" });
    });
    const tn = rod.d / VR, wn = worth(rod.d, fixed, false), wl = worth(rod.d, fixed, true);
    g.line(Xt(tn), gy0, Xt(tn), gy1, c.accent, 1, 0.6, [3, 3]); g.dot(Xt(tn), Yr(wn), 4.5, c.ink); g.dot(Xt(tn), Yr(wl), 4.5, c.proton); g.glow(Xt(tn), Yr(wl), 14, c.proton, 0.5);
    g.label(WT.trf("{a} s after AZ-5", tn.toFixed(1)), Xt(tn), gy0 - 12, { color: c.accent, size: fs - 1, weight: 700, bg: true, raw: true });
    const msg = fixed ? (phone ? "rod after 1986: no positive start" : "rod as modified after 1986: no positive start") : loPos ? (phone ? "lower core gains reactivity" : "first seconds: the lower core gains reactivity") : rod.d > 2 ? (phone ? "now the rod removes it" : "then the absorber takes over") : (phone ? "press AZ-5" : "press AZ-5 or drag the rod down");
    g.label(msg, W / 2, H * (phone ? 0.95 : 0.93), { color: loPos ? c.proton : c.ink, size: fs + 1, weight: 600, serif: true });
    g.label(phone ? "illustrative model" : "illustrative model · full insertion took about 18 s", W - 6, H - 10, { color: c.faint, size: 10, align: "right" });
  }

  // ================= Fukushima: blackout and boil-off =================
  const T_SBO = 0.85, U1 = 1380;
  const lvlCache = [];
  (function () { let m = 105, t = T_SBO; const dtt = 0.01; for (let i = 0; i <= 9600; i++) { const h = i * 0.01; if (h > t) { m = Math.max(0, m - ww(h) * U1 * 1.8 * dtt); t = h; } lvlCache.push(m); } })(); // t/h = MW * 3600/2000
  const mAt = (h) => h <= T_SBO ? 105 : lvlCache[Math.min(lvlCache.length - 1, Math.round(h / 0.01))];
  const hOf = (u) => Math.pow(10, lerp(Math.log10(1 / 60), Math.log10(96), u));
  const EVF = [[0, "earthquake: scram", "scram"], [0.82, "tsunami 15:35", "tsunami"], [24.83, "unit 1 explosion", "U1"], [68.25, "unit 3", "U3"], [87.47, "unit 4", "U4"]];
  function fmtH(h) { return h < 1.5 ? WT.trf("{a} min", Math.round(h * 60)) : h < 48 ? WT.trf("{a} h", h.toFixed(h < 10 ? 1 : 0)) : WT.trf("{a} days", (h / 24).toFixed(1)); }
  function drawBlackout(g, S, dt, phone, fs) {
    const { W, H, c, ctx } = g, h = hOf(S.fu), P = ww(h), MW = P * U1, boil = MW * 1.8, m = mAt(h), lost = h > T_SBO;
    // sea + seawall + building strip on the left; vessel cutaway inside
    const bx = phone ? W * 0.04 : W * 0.06, bw = phone ? W * 0.36 : Math.min(W * 0.34, H * 0.5), sea = phone ? H * 0.78 : H * 0.8;
    const vw = bw * 0.42, vh = Math.min(sea - H * 0.12, bw * 1.5), vx = bx + bw / 2 - vw / 2, vy = sea - vh - 8;
    // tsunami: water rises against the building around 0.7-1.1 h
    const wave = smooth(0.62, 0.82, h) * (1 - smooth(0.95, 1.4, h)), wy = sea - wave * vh * 0.35;
    // vessel
    ctx.save(); ctx.beginPath(); if (ctx.roundRect) ctx.roundRect(vx, vy, vw, vh, vw * 0.45); else ctx.rect(vx, vy, vw, vh); ctx.clip();
    ctx.fillStyle = g.rgba(c.soft, 0.08); ctx.fillRect(vx, vy, vw, vh);
    const cT = vy + vh * 0.42, cB = vy + vh * 0.85, above = clamp(m - 25, 0, 80) / 80, inCore = clamp(m, 0, 25) / 25;
    const ly = m > 25 ? lerp(cT, vy + vh * 0.1, above) : lerp(cB, cT, inCore);
    water(g, S, vx, vy, vw, vh, ly, clamp(P / 0.01, 0.2, 1.3), 5);
    const exp = m < 25 ? 1 - inCore : 0;
    fuel(g, S, vx + vw * 0.18, vx + vw * 0.82, cT, cB, phone ? 4 : 6, clamp(P / 0.015, 0.1, 1), exp, 0);
    ctx.restore();
    box(g, vx, vy, vw, vh, vw * 0.45, null, g.rgba(c.ink, 0.55), 2);
    if (exp > 0) g.glow(vx + vw / 2, (cT + cB) / 2, vw, c.proton, 0.35 * exp);
    // building outline and the diesel room at the bottom
    box(g, bx, vy - vh * 0.12, bw, sea - (vy - vh * 0.12), 4, null, g.rgba(c.soft, 0.5), 1.5);
    const dx = bx + 6, dy = sea - 26, dgen = !lost;
    box(g, dx, dy, bw * 0.3, 20, 3, g.rgba(dgen ? c.fission : c.soft, dgen ? 0.6 : 0.2), g.rgba(c.ink, 0.4));
    g.label(dgen ? (h < 0.02 ? "grid" : "diesels") : "no power", dx + bw * 0.15, dy - 10, { color: dgen ? c.fission : c.proton, size: fs - 2, weight: 700, bg: true });
    // sea at the right of the building; water floods in during the wave
    const sx = bx + bw;
    ctx.save(); ctx.fillStyle = g.rgba(c.cool, 0.35); ctx.beginPath(); ctx.moveTo(bx - 4, sea + 26); ctx.lineTo(bx - 4, wy);
    for (let i = 0; i <= 30; i++) { const x = lerp(bx - 4, phone ? W * 0.46 : W * 0.5, i / 30); ctx.lineTo(x, wy + 2 * Math.sin(i * 0.9 + S.time * 2)); }
    ctx.lineTo(phone ? W * 0.46 : W * 0.5, sea + 26); ctx.closePath(); ctx.fill(); ctx.restore(); if (wave > 0.05) g.label("tsunami", bx + bw + 8, wy - 12, { color: c.cool, size: fs - 1, weight: 700, align: "left", bg: true });
    g.label(WT.trf("water above fuel: {a} t", Math.max(0, m - 25).toFixed(0)), bx + bw / 2, vy - vh * 0.12 - 14, { color: c.cool, size: fs - 1, weight: 700, bg: true, raw: true });
    // decay-heat curve on the right with the time slider marker
    const gx0 = phone ? W * 0.55 : W * 0.56, gx1 = W * 0.95, gy0 = phone ? H * 0.12 : H * 0.14, gy1 = phone ? H * 0.6 : H * 0.6;
    const Xh = (hh) => lerp(gx0, gx1, (Math.log10(hh) - Math.log10(1 / 60)) / (Math.log10(96) - Math.log10(1 / 60))), Yp = (p) => lerp(gy1, gy0, clamp((Math.log10(p) + 2.8) / 1.5, 0, 1));
    [0.002, 0.005, 0.01, 0.02, 0.05].forEach((p) => { g.line(gx0, Yp(p), gx1, Yp(p), c.line, 1, 0.4, [2, 5]); g.label(`${(100 * p).toFixed(1)} %`, gx0 - 6, Yp(p), { color: c.faint, size: fs - 2, align: "right" }); });
    const pts = []; for (let i = 0; i <= 120; i++) { const hh = hOf(i / 120); pts.push([Xh(hh), Yp(ww(hh))]); }
    g.clip(gx0, gy0, gx1 - gx0, gy1 - gy0); g.ground(pts, c.photon, gy1 - gy0, 0.25); ctx.restore(); g.poly(pts, c.photon, 2.4);
    [[1 / 60, "1 min"], [1, "1 h"], [24, "1 day"], [96, "4 days"]].forEach(([hh, s]) => g.label(s, Xh(hh), gy1 + 14, { color: c.soft, size: fs - 2 }));
    EVF.slice(1).forEach(([hh, s, sp], i) => { const x = Xh(hh); g.line(x, gy0, x, gy1, i ? c.proton : c.cool, 1, 0.45, [3, 4]); }); g.label(phone ? "tsunami" : "tsunami 15:35", Xh(0.82), gy0 - 10, { color: c.cool, size: fs - 2, weight: 600 }); g.label(phone ? "explosions" : "explosions: units 1, 3, 4", Xh(87.47), gy0 - 10, { color: c.proton, size: fs - 2, weight: 600, align: "right" });
    const mx = Xh(h), my = Yp(P); g.line(mx, gy0, mx, gy1, c.accent, 1.2, 0.6); g.glow(mx, my, 18, c.photon, 0.7); g.dot(mx, my, 5, c.photon); geo.curve = { x0: gx0, x1: gx1, y0: gy0, y1: gy1 };
    g.label(phone ? "decay heat" : "decay heat, % of full power", gx0, gy0 - (phone ? 26 : 38), { color: c.photon, size: fs - 1, weight: 600, align: "left" });
    // readouts
    const ry = phone ? H * 0.74 : H * 0.72, rx = gx0, big = { size: fs + 4, weight: 700, serif: true, align: "left", raw: true };
    g.label(WT.trf("{a} after scram", fmtH(h)), rx, ry, Object.assign({ color: c.ink }, big));
    g.label(WT.trf("{a} MW of heat", MW.toFixed(MW < 10 ? 1 : 0)), rx, ry + (phone ? 22 : 30), Object.assign({ color: c.photon }, big, { size: fs + 1 }));
    g.label(WT.trf(phone ? "boils {a} t of water/h" : "boils off {a} tonnes of water an hour", boil.toFixed(0)), rx, ry + (phone ? 42 : 56), { color: c.cool, size: fs + (phone ? 0 : 1), weight: 700, align: "left", raw: true });
    g.label(phone ? "unit 1, 1380 MW" : "unit 1 (1380 MW thermal), if no water is added", rx, ry + (phone ? 60 : 80), { color: c.soft, size: fs - 2, align: "left" });
    ill(g);
  }

  // ================= Fukushima: hydrogen =================
  const kRel = (TC) => Math.exp(-20100 / (TC + 273.15)) / Math.exp(-20100 / 1273.15);
  const bubbles = [];
  const BLD = [["1", "12 Mar 15:36", 1], ["2", "no explosion", 0], ["3", "14 Mar 11:01", 1], ["4", "15 Mar ≈06:14", 1]];
  function drawH2(g, S, dt, phone, fs) {
    const { W, H, c, ctx } = g, T = S.zt, k = kRel(T);
    // four reactor buildings along the top
    const by1 = phone ? H * 0.44 : H * 0.42, bh = phone ? H * 0.26 : H * 0.26, bx0 = W * 0.06, bx1 = W * 0.94, bw = (bx1 - bx0) / 4 * 0.72;
    BLD.forEach(([u, when, ex], i) => {
      const x = lerp(bx0, bx1, (i + 0.5) / 4) - bw / 2, y = by1 - bh, sel = S.bsel === i;
      box(g, x, y, bw, bh, 3, g.rgba(c.soft, sel ? 0.16 : 0.08), g.rgba(c.ink, 0.45), sel ? 2 : 1.2);
      // upper floor with hydrogen (units 1, 3, 4)
      if (ex) { ctx.save(); ctx.beginPath(); ctx.rect(x, y, bw, bh * 0.3); ctx.clip(); for (let j = 0; j < 22; j++) { const u2 = fl[(j * 3 + i * 7) % 80], v = fl[(j * 5 + i) % 80]; g.dot(x + bw * u2 + 3 * Math.sin(S.time * 1.5 + j), y + bh * 0.3 * v + 2 * Math.cos(S.time * 1.2 + j), phone ? 2 : 2.6, c.alpha, 0.75); } ctx.restore(); g.line(x, y + bh * 0.3, x + bw, y + bh * 0.3, c.alpha, 1, 0.5, [3, 3]); }
      if (i < 3) { const vw2 = bw * 0.3; box(g, x + bw / 2 - vw2 / 2, y + bh * 0.4, vw2, bh * 0.55, vw2 * 0.4, g.rgba(c.warm, 0.2), g.rgba(c.ink, 0.4)); }
      else box(g, x + bw * 0.25, y + bh * 0.45, bw * 0.5, bh * 0.4, 3, g.rgba(c.cool, 0.3), g.rgba(c.ink, 0.4)); // unit 4: fuel pool, reactor empty (outage)
      g.label(WT.trf("unit {a}", u), x + bw / 2, by1 + 12, { color: c.ink, size: fs - 1, weight: 700, raw: true });
      if (!phone || sel) g.label(when, x + bw / 2, by1 + 28, { color: ex ? c.alpha : c.soft, size: fs - 2, weight: 600 });
      if (sel && ex) g.glow(x + bw / 2, y + bh * 0.15, bw * 0.7, c.alpha, 0.25 + 0.1 * Math.sin(S.time * 4));
      geo["b" + i] = { x, y, w: bw, h: bh + 34 };
    });
    // unit 3 -> unit 4 shared vent line
    const xa = lerp(bx0, bx1, 2.5 / 4) + bw / 2, xb = lerp(bx0, bx1, 3.5 / 4) - bw / 2, yv = by1 - bh * 0.85;
    g.line(xa, yv, xb, yv, c.alpha, 2, 0.7, [5, 4]);
    for (let i = 0; i < 3; i++) { const f = (fl[i + 60] + S.time * 0.3) % 1; g.dot(lerp(xa, xb, f), yv, 3, c.alpha, 0.9); }
    if (!phone) g.label("shared vent", (xa + xb) / 2, yv - 12, { color: c.alpha, size: fs - 2 });
    g.label(phone ? "hydrogen" : "hydrogen collects under the roof", W * 0.06, by1 - bh - 14, { color: c.alpha, size: fs - 1, weight: 600, align: "left" });
    if (phone && S.bsel != null) { /* label already shown under the selected building */ }
    // the cladding close-up: tube in steam, oxide layer, hydrogen leaving
    const cy0 = phone ? H * 0.58 : H * 0.56, cyy1 = H * 0.9, tx = phone ? W * 0.08 : W * 0.08, tw = phone ? W * 0.28 : W * 0.28, tcy = (cy0 + cyy1) / 2, tr = (cyy1 - cy0) * 0.22;
    const heat = clamp((T - 700) / 800, 0, 1);
    box(g, tx, tcy - tr, tw, tr * 2, tr, g.rgba(heat > 0.6 ? c.proton : c.warm, 0.35 + 0.5 * heat), g.rgba(c.ink, 0.5));
    const ox = clamp(Math.log10(k * 10) / 3, 0.05, 1) * tr * 0.2;
    box(g, tx - ox, tcy - tr - ox, tw + 2 * ox, (tr + ox) * 2, tr + ox, null, g.rgba(c.soft, 0.45), Math.max(1.5, ox)); if (!phone) g.label(phone ? "oxide" : "oxide layer", tx + tw + ox + 6, tcy - tr, { color: c.soft, size: fs - 2, align: "left" });
    g.glow(tx + tw / 2, tcy, tw * 0.7, c.photon, 0.15 + 0.4 * heat);
    // steam in, hydrogen out at a rate following the reaction rate
    const rate = clamp(k * 3, 0.2, 60);
    S.hAcc = (S.hAcc || 0) + (dt || 0) * rate; while (S.hAcc > 1 && bubbles.length < 120) { S.hAcc -= 1; bubbles.push({ x: tx + tw * Math.random(), y: tcy - tr - ox, t: S.time, vx: (Math.random() - 0.5) * 30 }); }
    for (let i = bubbles.length - 1; i >= 0; i--) { const b = bubbles[i], a = S.time - b.t; if (a > 2) { bubbles.splice(i, 1); continue; } const y = b.y - a * 40 * (phone ? 0.6 : 1); g.dot(b.x + b.vx * a, y, phone ? 2.2 : 3, c.alpha, 0.9 * (1 - a / 2)); }
    for (let i = 0; i < 10; i++) { const f = (fl[i + 30] + S.time * 0.35) % 1; g.ring(tx + tw * fl[i + 45], lerp(cyy1, tcy + tr + ox + 4, f), 2.5, c.cool, 1.2, 0.6 * (1 - f)); }
    g.label(WT.trf("{a} °C", Math.round(T)), tx + tw / 2, tcy, { color: "#ffffff", size: fs + 1, weight: 700, raw: true });
    g.label("Zr + 2 H₂O → ZrO₂ + 2 H₂ + heat", phone ? W * 0.04 : tx, cy0 - (phone ? 6 : 10), { color: c.ink, size: fs, serif: true, italic: true, align: "left" });
    if (!phone) g.label("1 kg of zirconium → 44 g of hydrogen", tx, cyy1 + 4, { color: c.soft, size: fs - 1, align: "left" });
    // rate chart (log) vs temperature
    const gx0 = phone ? W * 0.5 : W * 0.5, gx1 = W * 0.95, gy0 = cy0 + (phone ? 8 : 10), gy1 = cyy1 - (phone ? 2 : 6);
    const Xt = (t) => lerp(gx0, gx1, (t - 700) / 800), Yk = (v) => lerp(gy1, gy0, clamp((Math.log10(v) + 2) / 4, 0, 1));
    const pts = []; for (let t = 700; t <= 1500; t += 10) pts.push([Xt(t), Yk(kRel(t))]);
    g.clip(gx0, gy0, gx1 - gx0, gy1 - gy0); g.ground(pts, c.alpha, gy1 - gy0, 0.2); ctx.restore(); g.poly(pts, c.alpha, 2.2);
    g.label(phone ? "rate (log)" : "reaction rate (log scale)", gx0, gy0 - 2, { color: c.alpha, size: fs - 2, align: "left" });
    g.line(Xt(1200), gy0, Xt(1200), gy1, c.proton, 1, 0.6, [3, 4]); g.label("1200 °C", Xt(1200), gy0 - 2, { color: c.proton, size: fs - 2, bg: true });
    [800, 1000, 1400].forEach((t) => g.label(`${t}`, Xt(t), gy1 + 12, { color: c.soft, size: fs - 2 }));
    g.dot(Xt(T), Yk(k), 5, c.alpha); g.glow(Xt(T), Yk(k), 16, c.alpha, 0.6);
    g.label(WT.trf(phone ? "×{a} vs 1000 °C" : "reaction rate ×{a} vs 1000 °C", k < 1 ? k.toFixed(2) : k < 10 ? k.toFixed(1) : k.toFixed(0)), Xt(T) < (gx0 + gx1) / 2 ? Xt(T) + 10 : Xt(T) - 10, Yk(k) - 16, { color: c.alpha, size: fs - 1, weight: 700, align: Xt(T) < (gx0 + gx1) / 2 ? "left" : "right", bg: true, raw: true });
    ill(g);
  }

  // ================= what changed =================
  function drawAfter(g, S, dt, phone, fs) {
    const { W, H, c, ctx } = g, k = S.ak || 0;
    const items = [
      [["valve position shown directly", "valve shown"], ["subcooling monitors", "subcooling"], ["simulators and training", "training"], ["passive cooling: 72 h, no power (AP1000)", "passive cooling 72 h"]],
      [["enrichment 2.0 → 2.4 %", "2.0 → 2.4 %"], ["80–90 extra absorbers", "+80–90 absorbers"], ["void coefficient cut to about +1 β", "void ≈ +1 β"], ["scram 18 → 12 s, fast scram < 2.5 s", "scram 18 → 12 s"], ["reserve 26–30 → 43–48 rods", "43–48 rods"]],
      [["FLEX: portable pumps and generators", "FLEX pumps"], ["hardened, filtered vents", "hardened vents"], ["hydrogen recombiners", "recombiners"], ["higher tsunami walls", "higher walls"]],
    ][k];
    const head = ["After Three Mile Island", "After Chernobyl", "After Fukushima"][k];
    g.label(head, phone ? W * 0.05 : W * 0.06, phone ? 14 : 40, { color: c.ink, size: fs + 4, weight: 700, serif: true, align: "left" });
    // drawing area left/top, the list right/bottom
    const dx = phone ? W * 0.05 : W * 0.06, dy = phone ? 34 : 56, dw = phone ? W * 0.5 : W * 0.48, dh = phone ? H * 0.6 : H * 0.8;
    if (k === 0) { // valve with a position light; passive pool above the core with a natural-circulation loop
      const vx = dx + dw * 0.22, vy = dy + dh * 0.22, vs = phone ? 9 : 13, shut = Math.sin(S.time * 0.8) > 0;
      g.line(vx - dw * 0.18, vy, vx + dw * 0.18, vy, c.soft, 4, 0.6);
      g.area([[vx - vs, vy - vs * 0.7], [vx + vs, vy + vs * 0.7], [vx + vs, vy - vs * 0.7], [vx - vs, vy + vs * 0.7]], shut ? c.fission : c.proton, 0.85);
      g.ball(vx, vy - vs * 2.4, phone ? 6 : 8, shut ? c.fission : c.proton); g.glow(vx, vy - vs * 2.4, 20, shut ? c.fission : c.proton, 0.5);
      g.label(shut ? "shut" : "open", vx + 16, vy - vs * 2.4, { color: shut ? c.fission : c.proton, size: fs - 1, weight: 700, align: "left" });
      const cx = dx + dw * 0.32, cy = dy + dh * 0.78, cw = dw * 0.22, chh = dh * 0.26, px = dx + dw * 0.62, py = dy + dh * 0.38, pw = dw * 0.32, ph = dh * 0.2;
      box(g, cx - cw / 2, cy - chh / 2, cw, chh, 10, g.rgba(c.cool, 0.25), g.rgba(c.ink, 0.5)); fuel(g, S, cx - cw * 0.35, cx + cw * 0.35, cy - chh * 0.3, cy + chh * 0.35, 4, 0.3, 0, 0);
      box(g, px, py, pw, ph, 6, g.rgba(c.cool, 0.4), g.rgba(c.ink, 0.5));
      const loop = [[cx + cw / 2, cy - chh * 0.3], [px + pw * 0.2, cy - chh * 0.3], [px + pw * 0.2, py + ph], [px + pw * 0.8, py + ph], [px + pw * 0.8, cy + chh * 0.3], [cx + cw / 2, cy + chh * 0.3]];
      g.poly(loop, c.soft, 3, 0.5);
      const segs = []; let L = 0; for (let i = 1; i < loop.length; i++) { const l = Math.hypot(loop[i][0] - loop[i - 1][0], loop[i][1] - loop[i - 1][1]); segs.push(l); L += l; }
      for (let j = 0; j < 10; j++) { let d = ((j / 10 + S.time * 0.08) % 1) * L, i = 0; while (i < segs.length - 1 && d > segs[i]) { d -= segs[i]; i++; } const f = d / segs[i], x = lerp(loop[i][0], loop[i + 1][0], f), y = lerp(loop[i][1], loop[i + 1][1], f); g.dot(x, y, 3.2, i < 2 ? c.warm : c.cool, 0.9); }
      g.label(phone ? "pool" : "pool above the core", px + pw / 2, py - 12, { color: c.cool, size: fs - 1 });
      g.label(phone ? "no pumps" : "warm rises, cool sinks: no pumps", (cx + px + pw) / 2, cy + chh / 2 + 16, { color: c.soft, size: fs - 1 });
    } else if (k === 1) { // the rod before and after
      const ch = dh * 0.82, ct = dy + dh * 0.1, rw = phone ? 18 : 26, M = ch / HC, Z = (z) => ct + ch - z * M;
      [[0, "before"], [1, "after"]].forEach(([fx, nm], i) => {
        const x = dx + dw * (0.28 + 0.4 * i), dTop = fx ? HC - 1.25 : 5.75, dBot = fx ? -9 : 1.25;
        box(g, x - rw * 1.6, ct, rw * 3.2, ch, 5, g.rgba(c.soft, 0.12), g.rgba(c.ink, 0.3));
        ctx.save(); ctx.beginPath(); ctx.rect(x - rw / 2, ct, rw, ch); ctx.clip();
        ctx.fillStyle = g.rgba(c.cool, 0.45); ctx.fillRect(x - rw / 2, ct, rw, ch);
        ctx.fillStyle = g.rgba(c.faint, 0.95); ctx.fillRect(x - rw / 2, Z(dTop), rw, Z(Math.max(dBot, -1)) - Z(dTop)); ctx.restore();
        box(g, x - rw / 2, ct, rw, ch, 3, null, g.rgba(c.ink, 0.6), 1.4);
        if (!fx) { g.glow(x, Z(0.6), rw * 2.2, c.proton, 0.3 + 0.1 * Math.sin(S.time * 4)); g.label("water", x + rw * 1.7, Z(0.6), { color: c.cool, size: fs - 2, align: "left", bg: true }); }
        g.label(nm, x, ct - 12, { color: fx ? c.fission : c.proton, size: fs, weight: 700 });
      });
    } else { // building with vent + filter, recombiner, portable pump, wall
      const bx = dx + dw * 0.18, bw = dw * 0.42, by = dy + dh * 0.2, bh = dh * 0.62, sea = by + bh;
      box(g, bx, by, bw, bh, 4, g.rgba(c.soft, 0.1), g.rgba(c.ink, 0.5));
      const vw = bw * 0.35; box(g, bx + bw / 2 - vw / 2, by + bh * 0.3, vw, bh * 0.6, vw * 0.4, g.rgba(c.warm, 0.2), g.rgba(c.ink, 0.4));
      // recombiner boxes under the roof
      [0.2, 0.75].forEach((u) => { box(g, bx + bw * u - 8, by + 8, 16, 12, 2, g.rgba(c.fission, 0.6), g.rgba(c.ink, 0.4)); g.glow(bx + bw * u, by + 14, 14, c.fission, 0.3 + 0.15 * Math.sin(S.time * 3 + u * 5)); });
      // vent to a filter and a stack
      const sx = bx + bw + dw * 0.14; g.poly([[bx + bw / 2, by + bh * 0.3], [bx + bw / 2, by - dh * 0.04], [sx, by - dh * 0.04], [sx, by + bh * 0.4]], c.soft, 3, 0.6);
      box(g, sx - 12, by + bh * 0.4, 24, bh * 0.25, 4, g.rgba(c.accent, 0.35), g.rgba(c.ink, 0.5)); g.line(sx + 18, by + bh * 0.5, sx + 18, by - dh * 0.15, c.soft, 5, 0.6);
      for (let i = 0; i < 6; i++) { const f = (fl[i] + S.time * 0.25) % 1; g.dot(lerp(sx + 18, sx + 18 + 6 * Math.sin(i), f), lerp(by + bh * 0.5, by - dh * 0.15, f), 2.5, c.soft, 0.6 * (1 - f)); }
      if (!phone) g.label("filter", sx, by + bh * 0.75, { color: c.accent, size: fs - 2 });
      // portable pump truck feeding water
      const tx = bx - dw * 0.12, ty = sea - 18; box(g, tx - 22, ty - 8, 36, 16, 4, g.rgba(c.photon, 0.8), g.rgba(c.ink, 0.5)); g.dot(tx - 14, ty + 10, 4, c.ink); g.dot(tx + 8, ty + 10, 4, c.ink);
      g.line(tx + 14, ty, bx + bw / 2 - vw / 2, by + bh * 0.7, c.cool, 2.5, 0.8);
      for (let i = 0; i < 5; i++) { const f = (fl[i + 10] + S.time * 0.5) % 1; g.dot(lerp(tx + 14, bx + bw / 2 - vw / 2, f), lerp(ty, by + bh * 0.7, f), 2.6, c.cool, 0.9); }
      // seawall
      const wx = dx + dw * 0.95; box(g, wx - 5, sea - bh * 0.55, 10, bh * 0.55, 2, g.rgba(c.soft, 0.6)); ctx.save(); ctx.fillStyle = g.rgba(c.cool, 0.35); ctx.fillRect(wx + 5, sea - bh * 0.3 + 3 * Math.sin(S.time * 1.5), W - wx, bh * 0.3); ctx.restore();
      g.line(dx, sea, wx, sea, c.soft, 1.5, 0.6);
      if (!phone) { g.label("FLEX pump", tx - 4, ty + 26, { color: c.photon, size: fs - 2, weight: 600 }); g.label("recombiners", bx + bw / 2, by - 10, { color: c.fission, size: fs - 2, weight: 600, bg: true }); g.label("vent", sx + 18, by - dh * 0.15 - 12, { color: c.soft, size: fs - 2 }); g.label("sea wall", wx, sea - bh * 0.55 - 12, { color: c.soft, size: fs - 2 }); }
    }
    // the list
    const lx = phone ? W * 0.58 : W * 0.6, ly0 = phone ? 44 : H * 0.2, lgap = phone ? Math.min(30, (H * 0.62 - 44) / items.length) : Math.min(54, H * 0.6 / items.length);
    items.forEach(([long, short], i) => {
      const y = ly0 + i * lgap, a = smooth(0, 0.35, S.time - (S.akT || 0) - i * 0.12);
      g.ball(lx, y, phone ? 4 : 6, [c.photon, c.fission, c.accent][k], a);
      g.label(phone ? short : long, lx + (phone ? 10 : 16), y, { color: c.ink, size: fs - (phone ? 1 : 0), weight: 600, align: "left", alpha: a });
    });
    if (phone) { /* phone: compact list already */ }
    ill(g);
  }

  // ================= chapter =================
  const PICK = ["acT", "acC", "acF"];
  function setAk(S, k) { S.ak = k; S.akT = S.time; PICK.forEach((p, i) => setPressed(p, i === k)); }
  WT.chapter("accidents", {
    level: 2, num: "Lesson 1", title: "Three accidents, explained", short: "Accidents",
    lead: "Three Mile Island, Chernobyl and Fukushima, each told by the physics that drove it.",
    html: `
<div class="step">
  <h3>Three Mile Island 2, 1979</h3>
  <p>A relief valve stuck open and the pressurizer read full, so operators cut the emergency water while the core lost its own to <a href="#afterheat">decay heat</a>. Close the valve or restore injection sooner.</p>
  <div class="btns"><button class="btn ghost" data-act="acBlk" aria-pressed="false">Close block valve</button> <button class="btn ghost" data-act="acHpi" aria-pressed="false">Full injection</button> <button class="btn ghost" data-act="acTr">Restart</button></div>
</div>
<div class="step">
  <h3>Chernobyl 4, 1986: steam feeds power</h3>
  <p>At low power, <a href="#xenon">xenon</a>-poisoned and with most rods out, the RBMK's <a href="#feedback">void feedback</a> was positive: more steam, more reactivity. Run the pumps down and set its sign.</p>
  <div class="ctl"><label for="ac-v">Void coefficient (pcm per % steam)</label><input id="ac-v" type="range" data-bind="av" data-instant min="-10" max="30" step="1" value="20"><output data-show="av" data-fmt="0"></output></div>
  <div class="btns"><button class="btn" data-act="acRd">Run the pumps down</button> <button class="btn ghost" data-act="acVr">Reset</button></div>
</div>
<div class="step">
  <h3>Chernobyl: the scram</h3>
  <p>Each rod led with a graphite tip that pushed water out of the bottom of the core, so for the first seconds the scram added reactivity there.</p>
  <div class="btns"><button class="btn" data-act="acAz">AZ-5</button> <button class="btn ghost" data-act="acRr">Withdraw</button> <button class="btn ghost" data-act="acFx" aria-pressed="false">Rod after 1986</button></div>
</div>
<div class="step">
  <h3>Fukushima Daiichi, 2011: no power</h3>
  <p>The earthquake scram worked; the tsunami then flooded the emergency diesels, and <a href="#afterheat">decay heat</a>, a few percent of full power and falling slowly, boiled the water away.</p>
  <div class="ctl"><label for="ac-t">Time since the earthquake</label><input id="ac-t" type="range" data-bind="fu" data-instant min="0" max="1" step="0.002" value="0.55"></div>
</div>
<div class="step">
  <h3>Fukushima: hydrogen</h3>
  <p>Uncovered zirconium cladding reacts with steam ever faster as it heats, making hydrogen; it reached the reactor buildings and exploded in units 1, 3 and 4.</p>
  <div class="ctl"><label for="ac-z">Cladding temperature (°C)</label><input id="ac-z" type="range" data-bind="zt" data-instant min="700" max="1500" step="10" value="1200"><output data-show="zt" data-fmt="0"></output></div>
</div>
<div class="step">
  <h3>What changed</h3>
  <p>Each accident changed designs and rules worldwide. Pick one.</p>
  <div class="btns"><button class="btn ghost" data-act="acT" aria-pressed="true">Three Mile Island</button> <button class="btn ghost" data-act="acC" aria-pressed="false">Chernobyl</button> <button class="btn ghost" data-act="acF" aria-pressed="false">Fukushima</button></div>
</div>`,
    setup(S) {
      S.set("mode", "tmi"); S.set("av", 20); S.set("fu", 0.55); S.set("zt", 1200); S.fixed = 0; S.ak = +((/[?&]ak=(\d)/.exec(location.search) || [])[1] || 0); S.bsel = 0; // ?ak=1 opens one "what changed" panel (screenshot aid)
      S.on("acBlk", () => { if (tmi.block < 0 && tmi.t < TMI_END) { tmi.block = tmi.t; setPressed("acBlk", true); } });
      S.on("acHpi", () => { if (tmi.hpi < 0 && tmi.t < TMI_END) { tmi.hpi = tmi.t; setPressed("acHpi", true); } });
      S.on("acTr", () => tmiReset());
      S.on("acRd", () => { if (cv.halt) cvReset(); if (cv.rd < 0) cv.rd = cv.t; S.vFired = true; });
      S.on("acVr", () => { cvReset(); S.vFired = true; });
      S.on("acAz", () => { rod.snap = false; if (rod.d >= HC - 0.01) rod.d = 0; rod.go = S.time; });
      S.on("acRr", () => { rod.d = 0; rod.go = -1; rod.snap = false; });
      S.on("acFx", () => { S.fixed = S.fixed ? 0 : 1; setPressed("acFx", S.fixed); });
      PICK.forEach((p, i) => S.on(p, () => setAk(S, i)));
    },
    steps: [
      (S) => { S.set("mode", "tmi"); if (tmi.t >= TMI_END) tmiReset(); },
      (S) => { S.set("mode", "void"); },
      (S) => { S.set("mode", "rod"); },
      (S) => { S.set("mode", "blackout"); },
      (S) => { S.set("mode", "h2"); },
      (S) => { S.set("mode", "after"); setAk(S, S.ak || 0); },
    ],
    frame(g, S, dt) {
      const { W } = g, phone = W < 600, fs = phone ? 11 : 13, snap = document.body.classList.contains("shot");
      if (!S.grabbed) {
        S.grabbed = true; const cvs = g.ctx.canvas;
        const near = (o, x, y) => o && Math.hypot(x - o.x, y - o.y) < o.r;
        const inB = (b, x, y) => b && x >= b.x && x <= b.x + b.w && y >= b.y && y <= b.y + b.h;
        const setU = (x) => { const cc = geo.curve; if (!cc) return; const v = clamp((x - cc.x0) / (cc.x1 - cc.x0), 0, 1); S.set("fu", v); const el = document.getElementById("ac-t"); if (el) el.value = v; };
        const setD = (y) => { const o = geo.rod; if (!o) return; rod.d = clamp((y - o.ct) / o.M, 0, HC); rod.go = -1; rod.snap = false; };
        WT.grab(cvs, {
          down(x, y) {
            if (S.mode === "tmi") { if (near(geo.valve, x, y)) S.handlers.acBlk(); else if (near(geo.pump, x, y)) S.handlers.acHpi(); return false; }
            if (S.mode === "rod") { const o = geo.rod; if (o && Math.abs(x - o.x) < 40 && y > o.y0 - 20 && y < o.y1) { rod.drag = true; setD(y); return true; } return false; }
            if (S.mode === "blackout") { const cc = geo.curve; if (cc && x > cc.x0 - 10 && x < cc.x1 + 10 && y > cc.y0 - 20 && y < cc.y1 + 20) { setU(x); S.dragU = true; return true; } return false; }
            if (S.mode === "h2") { for (let i = 0; i < 4; i++) if (inB(geo["b" + i], x, y)) S.bsel = i; return false; }
            return false;
          },
          move(x, y) { if (rod.drag) setD(y); if (S.dragU) setU(x); },
          up() { rod.drag = false; S.dragU = false; }, cancel() { rod.drag = false; S.dragU = false; },
          hover(x, y) {
            const o = geo.rod, cc = geo.curve;
            cvs.style.cursor = S.mode === "tmi" && (near(geo.valve, x, y) || near(geo.pump, x, y)) ? "pointer" : S.mode === "rod" && o && Math.abs(x - o.x) < 40 && y > o.y0 - 20 && y < o.y1 ? "ns-resize" : S.mode === "blackout" && cc && x > cc.x0 - 10 && x < cc.x1 + 10 && y > cc.y0 - 20 && y < cc.y1 + 20 ? "ew-resize" : S.mode === "h2" && [0, 1, 2, 3].some((i) => inB(geo["b" + i], x, y)) ? "pointer" : "";
          },
        });
      }
      const f = { tmi: drawTMI, void: drawVoid, rod: drawRod, blackout: drawBlackout, h2: drawH2, after: drawAfter }[S.mode];
      if (f) f(g, S, dt, phone, fs, snap);
    },
  });
})();
