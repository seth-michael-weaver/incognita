/* Nuclear weapons (4): verification. How test bans and non-proliferation are checked. Scenes (S.mode):
 *   "seis"  = seismic monitoring. The CTBTO International Monitoring System (IMS, ctbto.org): 337 facilities when complete,
 *             170 seismic stations (50 primary, 120 auxiliary), 60 infrasound, 11 hydroacoustic, 80 radionuclide stations
 *             (40 of them also measure radioactive xenon), 16 radionuclide laboratories. The two seismograms are qualitative
 *             shapes (explosion: sharp compressional onset, strong P, weak S and surface waves; earthquake: emergent, strong S),
 *             as in introductory seismology texts. Wave speeds illustrative.
 *   "air"   = infrasound (low-frequency sound in air) and hydroacoustic (sound in the ocean's SOFAR channel) stations.
 *   "xe"    = radioactive xenon as a clock. Half-lives (ENSDF / NUBASE2020): Xe-135 9.14 h, Xe-133m 2.20 d, Xe-133 5.25 d,
 *             Xe-131m 11.8 d. Starting activities are illustrative (equal), so only the way the ratios change with time is meant;
 *             real fission ratios come from fission yields and decay chains. After the announced 2013 test in North Korea,
 *             xenon was measured in Japan and Russia about 55 days later (CTBTO press release, April 2013).
 *   "sg"    = IAEA safeguards (iaea.org): material accountancy, seals, cameras, environmental sampling, non-destructive assay:
 *             the 185.7 keV gamma line of U-235 for enrichment, neutron coincidence counting for plutonium. Spectrum shape
 *             illustrative (one line on a falling background). */
(function () {
  const { TAU, clamp, lerp, smooth } = WT.util;
  const SHOT = () => document.body.classList.contains("shot");
  const XE = [["xenon-135", 9.14 / 24], ["xenon-133m", 2.2], ["xenon-133", 5.25], ["xenon-131m", 11.8]];

  WT.chapter("nwverify", {
    level: 1, num: "Lesson 1", title: "Watching for tests, guarding material", short: "Verification",
    html: `
<div class="step">
  <h3>Listening to the Earth</h3>
  <p>A treaty is only as good as the means to check it. The Comprehensive Test Ban's monitoring network is built to span the globe: 170 seismic stations among more than 300 facilities. An underground explosion is sudden and shallow and pushes the rock outward, so its seismic record looks different from an earthquake's slip along a fault.</p>
  <div class="btns" role="group" aria-label="Source"><button class="btn ghost" data-act="vEx" aria-pressed="true">Explosion</button> <button class="btn ghost" data-act="vEq" aria-pressed="false">Earthquake</button></div>
</div>
<div class="step">
  <h3>Sound in air and water</h3>
  <p>Sixty <b>infrasound</b> stations listen for sound too low for the ear, which travels thousands of kilometres through the atmosphere. Eleven <b>hydroacoustic</b> stations listen in the oceans, where a layer of water channels sound across whole basins.</p>
</div>
<div class="step">
  <h3>Xenon: a clock in the air</h3>
  <p>Even a well-contained underground test can leak radioactive xenon, a noble gas that reacts with nothing. Its isotopes decay at different rates, so their ratios tell how long ago the fission happened and help separate a test from a reactor or a medical-isotope plant. Reading that clock needs nuclear data: fission yields and half-lives.</p>
  <div class="ctl"><label for="nwv-d">Days since the fission</label><input id="nwv-d" type="range" data-bind="days" data-instant min="0" max="60" step="0.5" value="5"><output data-show="days" data-fmt="1"></output></div>
</div>
<div class="step">
  <h3>Safeguards: counting the material</h3>
  <p>Under the Non-Proliferation Treaty, the International Atomic Energy Agency checks that declared nuclear material stays in peaceful use. Inspectors keep the books, seal containers, watch with cameras and take swipe samples. They also measure: the gamma rays of uranium-235 reveal how enriched uranium is, and neutron counting weighs plutonium. Both measurements rest on nuclear data.</p>
</div>`,
    setup(S) {
      S.set("mode", "seis"); S.set("days", 5); S.eq = 0; S.seisT = 0;
      const press = () => document.querySelectorAll("#nwverify [data-act^=vE]").forEach((b) => b.setAttribute("aria-pressed", String((b.dataset.act === "vEq") === !!S.eq)));
      S.on("vEx", () => { S.eq = 0; S.seisT = S.time; press(); }); S.on("vEq", () => { S.eq = 1; S.seisT = S.time; press(); });
    },
    steps: [(S) => { S.set("mode", "seis"); S.seisT = S.time; }, (S) => S.set("mode", "air"), (S) => { S.set("mode", "xe"); S.to("days", SHOT() ? 10 : 5, SHOT()); }, (S) => S.set("mode", "sg")],
    frame(g, S, dt) {
      const { W, H, c, ctx } = g, phone = W < 600, fs = phone ? 11 : 13;
      const foot = (s) => g.label(s, W - 6, H - 8, { color: c.faint, size: 10, align: "right" });
      const sta = (x, y, col, name) => { ctx.save(); ctx.fillStyle = col; ctx.beginPath(); ctx.moveTo(x, y - 12); ctx.lineTo(x + 8, y); ctx.lineTo(x - 8, y); ctx.closePath(); ctx.fill(); ctx.restore(); g.glow(x, y - 4, 16, col, 0.3); if (name) g.label(name, x, y + 14, { color: col, size: fs - 1, weight: 600 }); };
      if (S.mode === "seis" || S.mode === "air") {
        // a slice of the Earth: curved surface, an event, waves spreading; stations on the surface
        const R = Math.max(W, H) * 1.4, cx = W / 2, cy = H * 0.34 + R, age = SHOT() ? 2.2 : (S.time - (S.seisT || 0)) % 6;
        ctx.save(); const gr = ctx.createRadialGradient(cx, cy, R * 0.8, cx, cy, R); gr.addColorStop(0, g.rgba(c.warm, 0.12)); gr.addColorStop(1, g.rgba(c.warm, 0.22)); ctx.fillStyle = gr; ctx.beginPath(); ctx.arc(cx, cy, R, 0, TAU); ctx.fill(); ctx.restore();
        g.ring(cx, cy, R, c.soft, 1.5, 0.6);
        const surf = (x) => cy - Math.sqrt(Math.max(0, R * R - (x - cx) ** 2));
        const ex = W * (phone ? 0.3 : 0.24), ey = surf(ex) + (S.mode === "seis" ? (S.eq ? H * 0.14 : H * 0.03) : -H * 0.005);
        if (S.mode === "air") {
          // sea on the right: hydroacoustic; air above: infrasound
          ctx.save(); ctx.fillStyle = g.rgba(c.cool, 0.25); ctx.beginPath(); ctx.moveTo(W * 0.55, surf(W * 0.55)); for (let x = W * 0.55; x <= W; x += 8) ctx.lineTo(x, surf(x) - 2); ctx.lineTo(W, surf(W) + H * 0.1); ctx.lineTo(W * 0.55, surf(W * 0.55) + H * 0.1); ctx.closePath(); ctx.fill(); ctx.restore();
          for (let k = 0; k < 3; k++) { const r = ((age * 0.5 + k / 3) % 1) * W * 0.8; ctx.save(); ctx.strokeStyle = g.rgba(c.alpha, 0.6 * (1 - r / (W * 0.8))); ctx.lineWidth = 2; ctx.beginPath(); ctx.arc(ex, ey, r, Math.PI * 1.05, Math.PI * 1.95); ctx.stroke(); ctx.restore(); }
          const hx = W * 0.62, hy = surf(hx) + H * 0.05; for (let k = 0; k < 3; k++) { const r = ((age * 0.5 + k / 3) % 1) * W * 0.4; g.line(hx, hy, Math.min(W, hx + r), hy, c.cool, 2, 0.7 * (1 - r / (W * 0.4))); }
          g.glow(hx, hy, 14, c.cool, 0.5); g.label(phone ? "sound in the sea" : "sound channelled in the ocean", W * 0.8, hy + 22, { color: c.cool, size: fs - 1, weight: 600, bg: true });
          sta(W * 0.08, surf(W * 0.08), c.alpha, "infrasound"); sta(W * 0.46, surf(W * 0.46), c.alpha, phone ? "" : "infrasound"); sta(W * 0.95, surf(W * 0.95) + H * 0.04, c.cool, "hydroacoustic");
          g.glow(ex, ey, 18, c.photon, 0.6); g.dot(ex, ey, 4, c.ink);
          g.label(phone ? "60 infrasound · 11 hydroacoustic stations" : "60 infrasound and 11 hydroacoustic stations in the network", W / 2, H * 0.1, { color: c.ink, size: fs + 1, weight: 600, serif: true });
          foot("CTBTO International Monitoring System");
          return;
        }
        // seismic waves: P (fast) and S (slower) fronts
        const vP = W * 0.33, vS = vP * 0.58;
        [[vP, c.neutron, "P"], [vS, c.proton, "S"]].forEach(([v, col], k) => { const r = age * v; if (r > 4) { ctx.save(); ctx.beginPath(); ctx.arc(cx, cy, R, 0, TAU); ctx.clip(); g.ring(ex, ey, r, col, 2, k === 0 ? (S.eq ? 0.5 : 0.95) : (S.eq ? 0.95 : 0.35)); ctx.restore(); } });
        const sx = W * (phone ? 0.82 : 0.72), sy = surf(sx); sta(sx, sy, c.fission, "seismometer");
        g.glow(ex, ey, 20, S.eq ? c.warm : c.photon, 0.6); g.dot(ex, ey, 4, c.ink);
        g.label(S.eq ? "earthquake: deeper, slip on a fault" : "explosion: shallow, pushes outward", ex, ey + (phone ? 22 : 26), { color: c.ink, size: fs - 1, weight: 600, bg: true });
        // the recorded trace (qualitative)
        const ty = H * 0.16, tx0 = W * 0.08, tx1 = W * 0.92, dist = Math.hypot(sx - ex, sy - ey), tP = dist / vP, tS = dist / vS, span = 5.5;
        g.line(tx0, ty, tx1, ty, c.soft, 1, 0.3);
        const tr = []; for (let i = 0; i <= 400; i++) { const tt = (i / 400) * span; if (tt > age) break; let a = 0;
          const env = (t0, A, sharp, dec) => (tt < t0 ? 0 : A * (sharp ? 1 : smooth(0, 0.5, tt - t0)) * Math.exp(-(tt - t0) / dec));
          a = env(tP, S.eq ? 0.35 : 1, !S.eq, 0.5) * Math.sin(tt * 55) + env(tS, S.eq ? 1 : 0.25, false, 0.9) * Math.sin(tt * 30 + 1);
          tr.push([lerp(tx0, tx1, tt / span), ty - a * H * 0.07]); }
        if (tr.length > 1) g.poly(tr, c.fission, 1.6, 0.95);
        g.label("P", lerp(tx0, tx1, tP / span), ty + H * 0.09, { color: c.neutron, size: fs - 1, weight: 600, alpha: age > tP ? 1 : 0.2 });
        g.label("S", lerp(tx0, tx1, tS / span), ty + H * 0.09, { color: c.proton, size: fs - 1, weight: 600, alpha: age > tS ? 1 : 0.2 });
        g.label(S.eq ? "earthquake: weak start, strong S waves" : "explosion: sharp start, strong P waves", W / 2, H * 0.06, { color: c.ink, size: fs + 1, weight: 600, serif: true });
        foot("qualitative shapes · CTBTO International Monitoring System");
        return;
      }
      if (S.mode === "xe") {
        const d = clamp(S.days, 0, 60), x0 = W * (phone ? 0.14 : 0.18), x1 = W * 0.9, yT = H * 0.24, yB = H * 0.72, bw = (x1 - x0) / XE.length;
        const LO = -4, Y = (v) => lerp(yB, yT, (Math.log10(Math.max(v, 1e-4)) - LO) / -LO);
        [1, 0.1, 0.01, 0.001].forEach((v) => { g.line(x0 - 4, Y(v), x1, Y(v), c.soft, 1, 0.12); g.label(v === 1 ? "start" : `×${v}`, x0 - 8, Y(v), { color: c.faint, size: fs - 2, align: "right", raw: v !== 1 }); });
        XE.forEach(([name, T12], k) => { const a = Math.pow(0.5, d / T12), x = x0 + (k + 0.5) * bw, top = Y(a), col = [c.proton, c.warm, c.photon, c.fission][k];
          ctx.save(); ctx.fillStyle = g.rgba(col, 0.35); ctx.fillRect(x - bw * 0.3, top, bw * 0.6, yB - top); ctx.restore(); g.line(x - bw * 0.3, top, x + bw * 0.3, top, col, 2.5, 0.95); if (a > 1e-4) g.glow(x, top, bw * 0.3, col, 0.3);
          g.label(phone ? name.replace("xenon-", "Xe-") : name, x, yB + 16, { color: col, size: fs - 1, weight: 600 });
          g.label(phone ? (T12 < 1 ? `${Math.round(T12 * 24)} h` : `${T12} d`) : T12 < 1 ? `half-life ${Math.round(T12 * 24)} h` : `half-life ${T12} d`, x, yB + 32, { color: c.soft, size: fs - 2 }); });
        g.label(`${d.toFixed(d < 10 ? 1 : 0)} days after the fission`, W / 2, H * 0.08, { color: c.ink, size: fs + 2, weight: 600, serif: true });
        g.label(phone ? "the ratios change with time: a clock" : "short-lived isotopes fade first, so the ratios read like a clock", W / 2, H * 0.08 + fs + 10, { color: c.soft, size: fs });
        g.label(phone ? "illustrative starting amounts" : "equal starting amounts, for illustration; real ratios come from fission yields", W / 2, H * 0.88, { color: c.soft, size: fs - 1 });
        foot("half-lives: ENSDF / NUBASE2020");
        return;
      }
      // ---------- safeguards: a sealed container, a camera, a detector and its spectrum ----------
      const cx = W * (phone ? 0.3 : 0.26), cy = H * (phone ? 0.36 : 0.46), cw = Math.min(W * 0.18, 110), ch = cw * 1.25;
      ctx.save(); ctx.fillStyle = g.rgba(c.soft, 0.22); ctx.strokeStyle = g.rgba(c.soft, 0.6); ctx.lineWidth = 1.5; ctx.beginPath(); if (ctx.roundRect) ctx.roundRect(cx - cw / 2, cy - ch / 2, cw, ch, 8); else ctx.rect(cx - cw / 2, cy - ch / 2, cw, ch); ctx.fill(); ctx.stroke(); ctx.restore();
      g.line(cx - cw / 2, cy - ch * 0.3, cx + cw / 2, cy - ch * 0.3, c.soft, 1, 0.5);
      g.dot(cx + cw / 2, cy - ch * 0.3, 6, c.proton); g.glow(cx + cw / 2, cy - ch * 0.3, 14, c.proton, 0.4); g.label("seal", cx + cw / 2 + 12, cy - ch * 0.3, { color: c.proton, size: fs - 1, weight: 600, align: "left" });
      { const kx = cx - cw * 0.9, ky = cy - ch * 0.85; ctx.save(); ctx.fillStyle = g.rgba(c.ink, 0.7); ctx.fillRect(kx - 12, ky - 7, 24, 14); ctx.restore(); g.dot(kx + 12, ky, 4, c.accent); g.label("camera", kx, ky - 16, { color: c.soft, size: fs - 1 });
        ctx.save(); ctx.fillStyle = g.rgba(c.accent, 0.07); ctx.beginPath(); ctx.moveTo(kx + 12, ky); ctx.lineTo(cx + cw * 0.7, cy - ch * 0.2); ctx.lineTo(cx - cw * 0.2, cy + ch * 0.7); ctx.closePath(); ctx.fill(); ctx.restore(); }
      for (let i = 0; i < 5; i++) { const u = ((S.time * 0.8 + i / 5) % 1), x = lerp(cx + cw / 2, W * (phone ? 0.72 : 0.56), u), y = cy + ch * 0.15 + Math.sin(i * 3) * 6; g.photon(x, y, 0, 18, 1 - u * 0.6); }
      const dx = W * (phone ? 0.78 : 0.6), dy = cy + ch * 0.15; ctx.save(); ctx.fillStyle = g.rgba(c.photon, 0.25); ctx.fillRect(dx - 8, dy - 18, 30, 36); ctx.restore(); g.label("detector", dx + 7, dy + 32, { color: c.photon, size: fs - 1, weight: 600 });
      // spectrum
      const sx0 = phone ? W * 0.1 : W * 0.68, sx1 = W * 0.95, sy1 = phone ? H * 0.88 : H * 0.62, sy0 = phone ? H * 0.64 : H * 0.3;
      const sp = []; for (let i = 0; i <= 120; i++) { const e = i / 120, b = 0.55 * Math.exp(-e * 2.6) + 0.05, pk = 0.75 * Math.exp(-0.5 * ((e - 0.45) / 0.018) ** 2); sp.push([lerp(sx0, sx1, e), lerp(sy1, sy0, b + pk)]); }
      g.clip(sx0, sy0 - 20, sx1 - sx0, sy1 - sy0 + 20); g.ground(sp, c.photon, (sy1 - sy0) * 0.9, 0.3); g.ctx.restore(); g.poly(sp, c.photon, 2, 0.95); g.line(sx0, sy1, sx1, sy1, c.soft, 1, 0.5);
      g.label(phone ? "U-235 line, 186 keV" : "uranium-235 line, 186 keV", lerp(sx0, sx1, 0.45), sy0 - 10, { color: c.photon, size: fs - 1, weight: 600, bg: true });
      g.label("gamma-ray energy →", sx1, sy1 + 14, { color: c.soft, size: fs - 2, align: "right" });
      g.label(phone ? "a bigger peak: more uranium-235" : "the height of the peak tells how enriched the uranium is", W / 2, H * 0.08, { color: c.ink, size: fs + 1, weight: 600, serif: true });
      foot("after IAEA safeguards; spectrum illustrative");
    },
  });
})();
