/* Fast and thermal reactors: neutron energy spectra and what they do. Scenes by step; "moderation" m runs from 0 (no
 * moderator: a sodium-cooled fast reactor) to 1 (a light-water reactor).
 * Spectrum, drawn per unit lethargy (E phi(E)) on a log energy axis, illustrative shapes:
 *   fission source: Watt spectrum for U-235, chi(E) ~ exp(-E/0.988 MeV) sinh(sqrt(2.249 E/MeV)), mean ~2 MeV;
 *   slowing-down plateau (phi ~ 1/E, flat per lethargy) from ~1 MeV down to a cutoff that moves from ~3 keV (m = 0) to
 *   ~0.3 eV (m = 1); fast-reactor case is mostly 10 keV - 2 MeV, peaking near 100-200 keV;
 *   thermal Maxwellian E^2 exp(-E/kT) per lethargy with kT = 0.048 eV (moderator near 290 C; at room temperature kT = 0.0253 eV,
 *   the 2200 m/s point), weight growing with m.
 * eta(E) for U-235 and Pu-239: piecewise in log E, read from the standard textbook curves (e.g. Lamarsh & Baratta,
 * Introduction to Nuclear Engineering, fig. "eta vs energy"; ENDF/B evaluations): thermal 2.07 (U-235), 2.1 (Pu-239), the
 * Pu-239 0.3 eV resonance and an epithermal trough near 1.6-1.8, rising to ~2.3-2.4 (U-235) and ~2.9-3.0 (Pu-239) at 1-2 MeV.
 * Fission cross sections: sigma_f = sigma_0 sqrt(0.0253 eV / E) + sigma_fast (U-235: 585 b + 1.25 b; Pu-239: 748 b + 1.75 b),
 * resonances smoothed. Absorption sigma_a = nu sigma_f / eta with nu = 2.43 (U-235), 2.88 (Pu-239) + 0.13 per MeV.
 * Spectrum averages: eta_bar = int nu sigma_f phi / int sigma_a phi (not the average of eta).
 * Fission share of absorptions for minor actinides, PWR vs sodium fast reactor (OECD-NEA, Accelerator-driven Systems and
 * Fast Reactors in Advanced Nuclear Fuel Cycles, 2002; Salvatores): Pu-240 1 % / 55 %, Np-237 3 % / 27 %, Am-241 1 % / 21 %,
 * Cm-244 4 % / 45 %. In between: interpolated (log) by the fast share of the flux, illustrative.
 * Fast-reactor fuel: some 15-25 % plutonium (or highly enriched uranium), against 3-5 % U-235 in water reactors. */
(function () {
  const { TAU, clamp, lerp, smooth, rng } = WT.util;
  const X0 = -3, X1 = 7.3, NG = 260, KT = 0.048;
  const XS = []; for (let i = 0; i < NG; i++) XS.push(X0 + (X1 - X0) * i / (NG - 1));
  const sig = (z) => 1 / (1 + Math.exp(-z));
  const ETA_U = [[-3, 2.07], [-1.3, 2.06], [-0.5, 1.98], [0, 1.82], [1, 1.76], [2, 1.72], [3, 1.76], [4, 1.86], [5, 2.0], [5.5, 2.12], [6, 2.32], [6.5, 2.55], [7.3, 2.95]];
  const ETA_P = [[-3, 2.1], [-1.6, 2.04], [-0.9, 1.88], [-0.5, 1.8], [-0.2, 1.9], [0.3, 1.86], [1, 1.74], [2, 1.64], [3, 1.68], [4, 1.86], [5, 2.35], [5.5, 2.6], [6, 2.9], [6.5, 3.08], [7.3, 3.35]];
  const tab = (T, x) => { if (x <= T[0][0]) return T[0][1]; for (let i = 1; i < T.length; i++) if (x <= T[i][0]) { const [a, b] = T[i - 1], [c2, d] = T[i]; return lerp(b, d, (x - a) / (c2 - a)); } return T[T.length - 1][1]; };
  const NUC = { U: { eta: ETA_U, s0: 585, sf: 1.25, nu: 2.43 }, P: { eta: ETA_P, s0: 748, sf: 1.75, nu: 2.88 } };
  const sigF = (n, x) => { const E = 10 ** x; let s = n.s0 * Math.sqrt(0.0253 / E) + n.sf; if (n === NUC.P) s *= 1 + 3.5 / (1 + ((x + 0.52) / 0.1) ** 2); return s; };
  const nuOf = (n, x) => n.nu + 0.13 * (10 ** x) / 1e6;
  const MA = [["Pu-240", 0.01, 0.55], ["Np-237", 0.03, 0.27], ["Am-241", 0.01, 0.21], ["Cm-244", 0.04, 0.45]];
  const cache = new Map();
  function spec(m) {
    const key = Math.round(m * 200); if (cache.has(key)) return cache.get(key); m = key / 200;
    const xc = lerp(3.5, -0.5, smooth(0, 1, m)), Tw = 2.1 * smooth(0.45, 1, m), y = new Float64Array(NG);
    for (let i = 0; i < NG; i++) {
      const x = XS[i], E = 10 ** x, Em = E / 1e6;
      const fis = 0.9 * Em * Math.exp(-Em / 0.988) * Math.sinh(Math.sqrt(2.249 * Em)) / 0.55;
      const plat = (1 - 0.35 * (1 - m)) * sig((x - xc) / 0.32) * sig((6.0 - x) / 0.22) * (1 + 0.6 * (1 - m) * Math.exp(-(((x - 5.1) / 0.6) ** 2)));
      const th = Tw * ((E / KT) ** 2) * Math.exp(-E / KT) / 0.541;
      y[i] = fis + plat + th;
    }
    let A = 0, mx = 0; for (let i = 0; i < NG; i++) { A += y[i]; mx = Math.max(mx, y[i]); }
    const cdf = new Float64Array(NG); let c0 = 0; for (let i = 0; i < NG; i++) { c0 += y[i] / A; cdf[i] = c0; }
    const avg = {}; for (const k of ["U", "P"]) { const n = NUC[k]; let pr = 0, ab = 0, sf = 0; for (let i = 0; i < NG; i++) { const x = XS[i], s = sigF(n, x), e = tab(n.eta, x), w = y[i] / A; pr += nuOf(n, x) * s * w; ab += nuOf(n, x) * s / e * w; sf += s * w; } avg[k] = { eta: pr / ab, sf }; }
    let fast = 0; for (let i = 0; i < NG; i++) if (XS[i] > 5) fast += y[i] / A;
    const res = { y, mx, cdf, avg, fast }; cache.set(key, res); return res;
  }
  const F0 = spec(0).fast, F1 = spec(1).fast;
  const r = rng(77), gas = [], flashes = []; for (let i = 0; i < 90; i++) gas.push({});
  const ev = []; for (let i = 0; i < MA.length; i++) ev.push({ t: -r() * 2, fis: false });
  const sampleX = (S0) => { const u = r(); let i = 0; while (i < NG - 1 && S0.cdf[i] < u) i++; return XS[i]; };
  const eName = (x) => { const E = 10 ** x; return E >= 1e6 ? `${(E / 1e6).toFixed(0)} MeV` : E >= 1e3 ? `${(E / 1e3).toFixed(0)} keV` : E >= 1 ? `${E.toFixed(0)} eV` : `${E} eV`; };

  WT.chapter("spectrum", {
    level: 1, num: "Lesson 1", title: "Fast and thermal reactors", short: "Fast vs thermal",
    html: `
<div class="step">
  <h3>How fast the neutrons are</h3>
  <p>Neutrons are born fast, near 2 MeV. In a water reactor they bounce off hydrogen until they are as slow as the water's own atoms: <b>thermal</b>. A fast reactor has no moderator, so they stay fast. Slide between the two.</p>
  <div class="ctl"><label for="spc-m1">Moderation</label><input id="spc-m1" type="range" data-bind="mod" data-instant min="0" max="1" step="0.01" value="1"><output data-show="mod" data-fmt="2"></output></div>
</div>
<div class="step">
  <h3>Spare neutrons</h3>
  <p><i>η</i> is how many neutrons a fuel nucleus gives back per neutron it absorbs. One keeps the chain going; to breed new fuel you need a second to spare, so <i>η</i> well above 2. Plutonium-239 manages that only with fast neutrons.</p>
  <div class="ctl"><label for="spc-m2">Moderation</label><input id="spc-m2" type="range" data-bind="mod" data-instant min="0" max="1" step="0.01" value="0"><output data-show="mod" data-fmt="2"></output></div>
</div>
<div class="step">
  <h3>Burning the leftovers</h3>
  <p>Heavy leftovers like americium mostly just swallow slow neutrons and grow heavier. Fast neutrons split a much larger share of them, so a fast reactor can burn them.</p>
  <div class="ctl"><label for="spc-m3">Moderation</label><input id="spc-m3" type="range" data-bind="mod" data-instant min="0" max="1" step="0.01" value="0"><output data-show="mod" data-fmt="2"></output></div>
</div>
<div class="step">
  <h3>The price</h3>
  <p>A slow neutron is far more likely to cause fission: at 1 MeV the target is hundreds of times smaller. So a fast core needs much richer fuel, some 15–25 % plutonium instead of 3–5 % uranium-235.</p>
  <div class="ctl"><label for="spc-m4">Moderation</label><input id="spc-m4" type="range" data-bind="mod" data-instant min="0" max="1" step="0.01" value="1"><output data-show="mod" data-fmt="2"></output></div>
</div>`,
    setup(S) { S.set("mod", 1); },
    steps: [(S) => S.set("mod", 1), (S) => S.set("mod", 0), (S) => S.set("mod", 0), (S) => S.set("mod", document.body.classList.contains("shot") ? 0.3 : 1)],
    frame(g, S, dt) {
      const { W, H, c, ctx } = g, phone = W < 600, fs = phone ? 11 : 13, snap = document.body.classList.contains("shot"), st = Math.max(0, S.step);
      const m = clamp(S.mod, 0, 1), SP = spec(m), wFast = clamp((SP.fast - F1) / (F0 - F1), 0, 1);
      // ---------- landscape geometry ----------
      const x0 = W * (phone ? 0.08 : 0.07), x1 = W * 0.95, yTop = H * (phone ? 0.34 : 0.4), yBot = H * (phone ? 0.8 : 0.82);
      const X = (x) => lerp(x0, x1, (x - X0) / (X1 - X0));
      // ---------- top: a slice of the core (fuel pins in water or sodium), neutrons slowing collision by collision ----------
      const sy0 = H * 0.03, sy1 = H * (phone ? 0.24 : 0.29), ty = H * (phone ? 0.285 : 0.335), tx0 = x0 + (phone ? 52 : 90), tx1 = x1 - (phone ? 40 : 60);
      if (st !== 2) {
        const pw = x1 - x0, ph = sy1 - sy0;
        // coolant: water (blue) or liquid sodium (silvery), with a slow shimmer
        ctx.save(); const cg = ctx.createLinearGradient(0, sy0, 0, sy1);
        cg.addColorStop(0, g.rgba(m > 0.5 ? c.cool : c.soft, 0.1 + 0.12 * Math.abs(m - 0.5))); cg.addColorStop(0.5 + 0.1 * Math.sin(S.time * 0.7), g.rgba(m > 0.5 ? c.cool : c.photon, 0.16 + 0.1 * Math.abs(m - 0.5))); cg.addColorStop(1, g.rgba(m > 0.5 ? c.cool : c.soft, 0.08));
        ctx.fillStyle = cg; if (ctx.roundRect) { ctx.beginPath(); ctx.roundRect(x0, sy0, pw, ph, 14); ctx.fill(); } else ctx.fillRect(x0, sy0, pw, ph); ctx.restore();
        // fuel pins: a hexagonal lattice, tighter in a fast core
        const rp = Math.min(ph * 0.12, phone ? 11 : 15), pitch = rp * lerp(2.3, 3.3, m), rows = Math.max(2, Math.floor(ph / (pitch * 0.87))), cols = Math.floor(pw / pitch);
        const oxp = x0 + (pw - (cols - 0.5) * pitch) / 2 + pitch * 0.25, oyp = sy0 + (ph - (rows - 1) * pitch * 0.87) / 2;
        const pins = []; for (let j = 0; j < rows; j++) for (let i = 0; i < cols - (j % 2); i++) pins.push([oxp + (i + (j % 2) * 0.5) * pitch, oyp + j * pitch * 0.87]);
        g.clip(x0, sy0, pw, ph);
        // moderator atoms: hydrogen (water) or a few big sodium atoms
        const q = rng(9), nH = Math.round(70 * m), nNa = Math.round(26 * (1 - m));
        for (let i = 0; i < nH; i++) { const hx = x0 + q() * pw + Math.sin(S.time * 2 + i) * 2, hy = sy0 + q() * ph + Math.cos(S.time * 1.7 + i) * 2; g.ball(hx, hy, phone ? 1.8 : 2.3, c.soft, 0.4); }
        for (let i = 0; i < nNa; i++) { const hx = x0 + q() * pw + Math.sin(S.time + i) * 1.5, hy = sy0 + q() * ph; g.ball(hx, hy, phone ? 3.6 : 4.6, c.soft, 0.45); }
        for (const [px, py] of pins) { g.glow(px, py, rp * 2.2, c.warm, 0.22 + 0.06 * Math.sin(S.time * 3 + px)); g.ball(px, py, rp, c.warm, 0.95); }
        // neutrons: born fast in a pin; each collision with the coolant takes away a share of the energy (lethargy step ~xi)
        const xi = lerp(0.09, 0.92, m), lam = (phone ? 0.7 : 1) * lerp(70, 26, m), pAbs = lerp(1 / 50, 1 / 28, m), xth = Math.log10(KT);
        const spd = (E) => (phone ? 0.7 : 1) * (14 + 420 * clamp((E + 1.6) / 7.9, 0, 1) ** 1.6);
        const born = (n) => { const p = pins[Math.floor(r() * pins.length)] || [x0 + pw / 2, sy0 + ph / 2], a = r() * TAU; n.x = p[0]; n.y = p[1]; n.dx = Math.cos(a); n.dy = Math.sin(a); n.E = 6.2 + 0.3 * r(); n.s = lam * -Math.log(1 - r() + 1e-9); };
        if (snap && !gas.warm) { gas.forEach((n) => { born(n); const k = Math.floor(r() * 60); for (let i = 0; i < k; i++) n.E = Math.max(xth + 0.3 * (r() - 0.5), n.E - xi * -Math.log(1 - r() + 1e-9) / Math.LN10); n.x = x0 + r() * pw; n.y = sy0 + r() * ph; }); gas.warm = 1; }
        for (const n of gas) {
          if (n.E == null) born(n);
          let mv = spd(n.E) * (snap ? 0 : dt);
          while (mv > 0) {
            const stp2 = Math.min(mv, n.s); n.x += n.dx * stp2; n.y += n.dy * stp2; n.s -= stp2; mv -= stp2;
            if (n.s <= 0) { // a collision
              if (r() < pAbs) { born(n); break; }
              if (n.E > xth + 0.2) { const loss = xi * -Math.log(1 - r() + 1e-9) / Math.LN10; n.E = Math.max(xth + 0.25 * (r() - 0.5), n.E - loss); if (m > 0.3 && r() < 0.25 && flashes.length < 40) flashes.push([n.x, n.y, S.time]); }
              const a = r() * TAU; n.dx = Math.cos(a); n.dy = Math.sin(a); n.s = lam * -Math.log(1 - r() + 1e-9); mv = Math.min(mv, spd(n.E) * dt);
            }
          }
          if (n.x < x0) n.x += pw; if (n.x > x1) n.x -= pw; if (n.y < sy0) n.y += ph; if (n.y > sy1) n.y -= ph;
          const col = n.E > 4.5 ? c.warm : n.E > 0 ? c.photon : c.neutron, tl = Math.min(34, spd(n.E) * 0.06);
          g.line(n.x - n.dx * tl, n.y - n.dy * tl, n.x, n.y, col, 2, 0.4);
          g.ball(n.x, n.y, phone ? 2.6 : 3.2, col, 0.95);
        }
        for (let i = flashes.length - 1; i >= 0; i--) { const [fx, fy, t0] = flashes[i], a = (S.time - t0) / 0.3; if (a > 1 || a < 0) { flashes.splice(i, 1); continue; } g.glow(fx, fy, 4 + 10 * a, "#ffffff", 0.45 * (1 - a)); }
        g.ctx.restore();
        g.label(m > 0.8 ? (phone ? "water: neutrons slow down" : "water reactor: hydrogen slows the neutrons") : m < 0.15 ? (phone ? "sodium: they stay fast" : "fast reactor: sodium barely slows them") : "partly moderated", (x0 + x1) / 2, sy0 + 12, { color: c.ink, size: fs - 1, weight: 600, bg: true });
      } else {
        // ---------- minor actinides: fission or capture ----------
        const n = MA.length, cw = (x1 - x0) / n;
        MA.forEach(([name, a0, a1], i) => {
          const share = Math.exp(lerp(Math.log(a0), Math.log(a1), wFast)), cx = x0 + cw * (i + 0.5), cy = sy0 + (sy1 - sy0) * (phone ? 0.36 : 0.42), R = Math.min(cw * (phone ? 0.2 : 0.26), (sy1 - sy0) * (phone ? 0.22 : 0.3));
          const e = ev[i]; e.t += snap ? 0 : dt; if (e.t > 1.6) { e.t = 0; e.fis = r() < share; }
          const a = snap ? 1.2 : e.t, done = a > 0.6;
          if (!done) { const nx = cx - cw * 0.45 + (cw * 0.45 - R) * a / 0.6; g.ball(nx, cy, 3.2, wFast > 0.5 ? c.warm : c.neutron); g.line(nx - 14, cy, nx, cy, wFast > 0.5 ? c.warm : c.neutron, 2, 0.4); }
          if (done && e.fis && !snap) { const b = (a - 0.6) / 1; g.glow(cx, cy, R * (1 + 2.5 * b), c.fission, 0.6 * (1 - b)); g.ring(cx, cy, R * (1 + 3 * b), c.fission, 2, 1 - b); g.nucleus(cx - R * 0.7 * b - R * 0.3, cy, R * 0.68, { N: 24, Z: 10, seed: 5 + i, t: S.time, alpha: 1 - b * 0.3 }); g.nucleus(cx + R * 0.7 * b + R * 0.3, cy, R * 0.6, { N: 20, Z: 8, seed: 9 + i, t: S.time, alpha: 1 - b * 0.3 }); }
          else { g.nucleus(cx, cy, R * (done && !snap ? 1.08 : 1), { N: 40, Z: 16, seed: 11 + i, t: S.time, halo: done && !snap ? c.proton : null, haloAlpha: 0.3 }); }
          g.label(name, cx, cy - R - 12, { color: c.ink, size: fs, weight: 600 });
          const bw = cw * 0.7, by = cy + R + 10; ctx.save(); ctx.fillStyle = g.rgba(c.soft, 0.15); ctx.fillRect(cx - bw / 2, by, bw, 7); ctx.fillStyle = c.fission; ctx.fillRect(cx - bw / 2, by, bw * share, 7); ctx.restore();
          g.label(`${(100 * share).toFixed(0)} % split`, cx, by + (phone ? 17 : 20), { color: c.fission, size: fs, weight: 700 });
        });
      }
      // ---------- the moderation handle, in the picture (drag it, or anywhere on the core slice) ----------
      { const kx = lerp(tx0, tx1, m);
        g.line(tx0, ty, tx1, ty, c.soft, 3, 0.35);
        ctx.save(); const lg = ctx.createLinearGradient(tx0, 0, tx1, 0); lg.addColorStop(0, g.rgba(c.warm, 0.9)); lg.addColorStop(1, g.rgba(c.cool, 0.9)); ctx.strokeStyle = lg; ctx.lineWidth = 3; ctx.lineCap = "round"; ctx.beginPath(); ctx.moveTo(tx0, ty); ctx.lineTo(kx, ty); ctx.stroke(); ctx.restore();
        g.glow(kx, ty, 18, m > 0.5 ? c.cool : c.warm, 0.45 + 0.15 * Math.sin(S.time * 3)); g.ball(kx, ty, phone ? 7 : 8, m > 0.5 ? c.cool : c.warm);
        g.label(phone ? "sodium" : "no moderator (sodium)", tx0 - 10, ty, { color: c.warm, size: fs - 1, weight: 600, align: "right" });
        g.label("water", tx1 + 10, ty, { color: c.cool, size: fs - 1, weight: 600, align: "left" }); }
      const onCtl = (x, y) => Math.abs(y - ty) < 18 && x > tx0 - 20 && x < tx1 + 20 || (st !== 2 && x > x0 && x < x1 && y > sy0 && y < sy1);
      WT.grab(ctx.canvas, {
        down(x, y) { if (!onCtl(x, y)) return false; this.move(x, y); return true; },
        move(x, y) { const v = clamp((x - tx0) / (tx1 - tx0), 0, 1); S.set("mod", v); document.querySelectorAll('#spectrum [data-bind="mod"]').forEach((i) => (i.value = v)); },
        hover(x, y) { ctx.canvas.style.cursor = onCtl(x, y) ? "ew-resize" : "default"; },
      });
      // ---------- the spectrum landscape ----------
      const ytop = yTop, hgt = yBot - ytop;
      const pts = [], Ys = (v) => yBot - hgt * 0.85 * v / SP.mx;
      for (let i = 0; i < NG; i++) pts.push([X(XS[i]), Ys(SP.y[i])]);
      // region bands
      [[X0, -0.4, phone ? "thermal" : "thermal", c.neutron], [-0.4, 5, phone ? "resonances" : "slowing down (resonances)", c.photon], [5, X1, "fast", c.warm]].forEach(([a, b, s, col]) => {
        ctx.save(); ctx.fillStyle = g.rgba(col, 0.05); ctx.fillRect(X(a), ytop - 4, X(b) - X(a), yBot - ytop + 4); ctx.restore();
        g.label(s, (X(a) + X(b)) / 2, ytop + 6, { color: col, size: fs - 1, weight: 600 }); });
      const spCol = m > 0.5 ? c.cool : c.warm;
      g.clip(x0, ytop - 30, x1 - x0, yBot - ytop + 30); g.ground(pts, spCol, hgt * 0.6, 0.34); g.ctx.restore(); g.poly(pts, spCol, 2.4, st === 1 || st === 3 ? 0.55 : 1);
      g.line(x0, yBot, x1, yBot, c.line, 1);
      for (let e = -2; e <= 6; e += 2) g.label(e === -2 ? "0.01 eV" : eName(e), X(e), yBot + 12, { color: c.faint, size: fs - 2 });
      if (!phone) g.label("neutron energy →", x1, yBot + 28, { color: c.soft, size: fs - 1, align: "right" });
      if (st !== 1) g.arrow(X(6.6), ytop + 26, X(6.35), ytop + 46, c.warm, 1.5, 0.8, 7);
      if (st !== 1) g.label(phone ? "born ~2 MeV" : "born near 2 MeV", X(6.6), ytop + 18, { color: c.warm, size: fs - 1, align: "right" });
      // ---------- step 2: eta(E) ----------
      if (st === 1) {
        const ylo = 1.4, yhi = 3.4, Ye = (v) => lerp(yBot - 4, ytop + 22, (v - ylo) / (yhi - ylo));
        g.line(x0, Ye(2), x1, Ye(2), c.ink, 1.2, 0.55, [5, 4]); g.label(phone ? "η = 2" : "η = 2: one to continue, one to breed", X(1.6), Ye(2) - 12, { color: c.ink, size: fs - 1, bg: true });
        [["U", "U-235", c.accent], ["P", "Pu-239", c.proton]].forEach(([k, name, col]) => {
          const q = []; for (let i = 0; i < NG; i += 2) q.push([X(XS[i]), Ye(tab(NUC[k].eta, XS[i]))]); g.poly(q, col, 2.4, 0.95);
          g.label(name, X(7.1), Ye(tab(NUC[k].eta, 7.1)) + (k === "P" ? -14 : 14), { color: col, size: fs - 1, weight: 700, align: "right" });
        });
        const eU = SP.avg.U.eta, eP = SP.avg.P.eta, ry = H * 0.93;
        g.label(phone ? `average η: U-235 ${eU.toFixed(1)} · Pu-239 ${eP.toFixed(1)}` : `averaged over this spectrum:  η(U-235) ≈ ${eU.toFixed(1)}   η(Pu-239) ≈ ${eP.toFixed(1)}`, W / 2, ry, { color: c.ink, size: fs + 1, weight: 600, serif: true });
        if (eP > 2.3) g.glow(W / 2, ry, 90, c.fission, 0.12);
      }
      // ---------- step 4: fission cross section ----------
      if (st === 3) {
        const lo = 0, hi = 3.3, Yc = (s) => lerp(yBot - 4, ytop + 22, (Math.log10(s) - lo) / (hi - lo));
        const q = []; for (let i = 0; i < NG; i += 2) q.push([X(XS[i]), Yc(sigF(NUC.P, XS[i]))]);
        g.poly(q, c.proton, 2.6, 0.95);
        [1, 10, 100, 1000].forEach((s) => { g.line(x0, Yc(s), x0 + 8, Yc(s), c.soft, 1, 0.7); g.label(`${s} b`, x0 + 10, Yc(s), { color: c.soft, size: fs - 2, align: "left", bg: true }); });
        g.label(phone ? "Pu-239 fission target" : "Pu-239 fission cross section (target size)", X(2.4), Yc(sigF(NUC.P, 2.4)) - 16, { color: c.proton, size: fs - 1, weight: 600, align: "left" });
        g.dot(X(-1.6), Yc(sigF(NUC.P, -1.6)), 4, c.proton); g.dot(X(6), Yc(sigF(NUC.P, 6)), 4, c.proton);
        g.label("≈ 750 b", X(-1.6) + 10, Yc(sigF(NUC.P, -1.6)) - 14, { color: c.proton, size: fs - 1, weight: 700, align: "left" });
        g.label(`${sigF(NUC.P, 6).toFixed(1)} b`, X(6), Yc(sigF(NUC.P, 6)) - 14, { color: c.proton, size: fs - 1, weight: 700 });
        g.label(phone ? "1 MeV: a target ~400 times smaller" : "at 1 MeV the target is about 400 times smaller than at 0.025 eV", W / 2, H * 0.93, { color: c.ink, size: fs + 1, weight: 600, serif: true });
      }
      if (st === 0) {
        g.label(m > 0.6 ? (phone ? "most neutrons end up thermal" : "most neutrons are slowed all the way to thermal") : m < 0.25 ? (phone ? "most stay between 10 keV and 2 MeV" : "most neutrons stay between 10 keV and 2 MeV") : (phone ? "many linger at in-between energies" : "many neutrons linger at in-between energies"), W / 2, H * 0.93, { color: c.ink, size: fs + 1, weight: 600, serif: true });
        if (m > 0.5) g.label(phone ? "hot water: kT ≈ 0.05 eV" : "thermal: kT ≈ 0.05 eV in hot water, about 3 km/s", X(-1.1), Ys(SP.mx) - 4 < ytop + 24 ? ytop + 24 : Ys(SP.mx) - 14, { color: c.neutron, size: fs - 1, weight: 600, align: "left", bg: true });
      }
      if (st === 2) g.label(phone ? "the rest are captured and grow heavier" : "the rest are captured: the nucleus just grows heavier", W / 2, H * 0.93, { color: c.proton, size: fs + 1, weight: 600, serif: true });
      g.label("illustrative shapes", W - 6, H - 10, { color: c.faint, size: 10, align: "right" });
    },
  });
})();
