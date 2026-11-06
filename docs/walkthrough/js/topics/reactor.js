/* How a reactor makes electricity: a pressurized water reactor (PWR). Scenes (S.mode):
 *   "fuel"  = the fuel hierarchy: a UO2 pellet (about 8 mm across, 1 cm tall) -> a rod (about 4 m, some 350 pellets in a
 *             zirconium-alloy tube) -> a 17x17 assembly (264 fuel rods + 24 guide tubes for control rods + 1 instrument tube,
 *             Westinghouse layout) -> a core of 193 assemblies (about 51 000 rods), as in a 4-loop PWR of ~3400 MW heat.
 *             Pellet energy: 5.5 g UO2 (4.8 g U) at 45-60 GWd/t gives 1.9-2.5e10 J; a tonne of coal is 2.4-2.9e10 J, so
 *             "about a tonne of coal" (the usual industry comparison, e.g. NEI: 1 pellet ~ 1 t coal ~ 17 000 ft3 = 480 m3 of gas).
 *   "plant" = the cutaway: primary loop (about 155 bar, 290 C in / 325 C out, does not boil; saturation at 155 bar is 345 C),
 *             steam generator, secondary loop (about 70 bar, steam near 285 C), turbine + generator, condenser cooled by
 *             river or sea water. Electricity about one third of the heat (3400 MW heat -> ~1150 MW electric).
 *             The turbine turns at a fixed speed locked to the grid (3000 rpm at 50 Hz for a 2-pole set; large nuclear sets
 *             often 1500 rpm); more steam means more torque and more electricity, not a faster spin.
 *   Control rods: power vs rod insertion is illustrative (in a real PWR power is mostly set by turbine demand and boron, and
 *   the core follows through temperature feedback). When the chain reaction stops the fuel still makes afterheat (~6 % at
 *   first, falling), shown as a small floor. */
(function () {
  const { TAU, clamp, lerp, smooth, rng } = WT.util;
  const PTH = 3400, ETA = 0.335;
  const r = rng(29);
  // guide tube positions in a 17x17 Westinghouse assembly (row, col); (8,8) is the instrument tube
  const GT = [[2, 5], [2, 8], [2, 11], [3, 3], [3, 13], [5, 2], [5, 5], [5, 8], [5, 11], [5, 14], [8, 2], [8, 5], [8, 8], [8, 11], [8, 14], [11, 2], [11, 5], [11, 8], [11, 11], [11, 14], [13, 3], [13, 13], [14, 5], [14, 8], [14, 11]];
  const GTS = new Set(GT.map(([a, b]) => a * 17 + b));
  const CORE_ROWS = [7, 11, 13, 13, 15, 15, 15, 15, 15, 15, 15, 13, 13, 11, 7]; // 193 assemblies
  const COAL = []; { const q = rng(5); for (let i = 0; i < 70; i++) { const a = q(), b = q(); COAL.push([(a - 0.5) * 2 * (1 - b * 0.9), b, 0.6 + 0.5 * q()]); } COAL.sort((p, s) => s[1] - p[1]); }

  // polyline helpers (normalized coordinates, mapped to the plant box each frame)
  function mkPath(pts) { const L = [0]; for (let i = 1; i < pts.length; i++) L.push(L[i - 1] + Math.hypot(pts[i][0] - pts[i - 1][0], pts[i][1] - pts[i - 1][1])); return { pts, L, len: L[L.length - 1] }; }
  function at(p, s) { const d = ((s % 1) + 1) % 1 * p.len; let i = 1; while (i < p.L.length - 1 && p.L[i] < d) i++; const u = (d - p.L[i - 1]) / (p.L[i] - p.L[i - 1] || 1), a = p.pts[i - 1], b = p.pts[i]; return [lerp(a[0], b[0], u), lerp(a[1], b[1], u), d / p.len]; }
  // vessel 0.04-0.25 x, 0.16-0.86 y; core 0.44-0.78; steam generator 0.34-0.50; turbine 0.56-0.80; generator 0.83-0.96; condenser 0.57-0.82
  const PRI = mkPath([[0.145, 0.86], [0.145, 0.30], [0.25, 0.36], [0.31, 0.36], [0.31, 0.80], [0.38, 0.80], [0.38, 0.32], [0.415, 0.24], [0.45, 0.32], [0.45, 1.0], [0.18, 1.0], [0.145, 0.86]]);
  const SEC = mkPath([[0.485, 0.62], [0.485, 0.2], [0.44, 0.11], [0.44, 0.06], [0.58, 0.06], [0.58, 0.26], [0.78, 0.29], [0.78, 0.7], [0.64, 0.7], [0.64, 0.8], [0.53, 0.8], [0.53, 0.62], [0.485, 0.62]]);
  const CW = mkPath([[1.02, 0.66], [0.6, 0.66], [0.6, 0.6], [1.02, 0.6]]);
  const NP = 150, NS = 120, NC = 50;
  const pp = [], sp = [], cp = [];
  for (let i = 0; i < NP; i++) pp.push({ s: i / NP + r() * 0.004, o: r() * 2 - 1 });
  for (let i = 0; i < NS; i++) sp.push({ s: i / NS + r() * 0.004, o: r() * 2 - 1 });
  for (let i = 0; i < NC; i++) cp.push({ s: i / NC, o: r() * 2 - 1 });
  const neut = []; for (let i = 0; i < 60; i++) neut.push({ x: r(), y: r(), a: r() * TAU, t: r() });

  WT.chapter("reactor", {
    level: 0, num: "Lesson 1", title: "How a reactor makes electricity", short: "Reactor",
    html: `
<div class="step">
  <h3>The fuel</h3>
  <p>Uranium is baked into ceramic pellets the size of a fingertip, stacked in long metal rods, and the rods are bundled into assemblies. One pellet gives roughly as much heat as burning a tonne of coal.</p>
  <div class="ctl"><label for="rea-z">Zoom out</label><input id="rea-z" type="range" data-bind="z" min="0" max="3" step="0.01" value="0"><output data-show="z" data-fmt="1"></output></div>
</div>
<div class="step">
  <h3>Splitting atoms makes heat</h3>
  <p>In the core, splitting uranium atoms heat the water flowing up past the rods. The same water slows the neutrons so they can split more atoms. High pressure keeps it from boiling, even at 325 °C.</p>
</div>
<div class="step">
  <h3>Steam turns the turbine</h3>
  <p>The hot water passes its heat through thin tubes to a second loop, which boils. The steam spins a turbine and a generator, then cold river or sea water turns it back into water. About a third of the heat becomes electricity.</p>
</div>
<div class="step">
  <h3>Control rods</h3>
  <p>Control rods soak up neutrons. Push them in and fewer atoms split: less heat, less steam, less electricity. Pull them out and the power climbs.</p>
  <div class="ctl"><label for="rea-rod">Control rods in (%)</label><input id="rea-rod" type="range" data-bind="ins" data-instant min="0" max="100" step="1" value="15"><output data-show="ins" data-fmt="0"></output></div>
</div>`,
    setup(S) { S.set("mode", "fuel"); S.set("z", 0); S.set("ins", 15); S.Pw = 1; S.rot = 0; S.hl = 0; },
    steps: [
      (S) => { S.set("mode", "fuel"); },
      (S) => { S.set("mode", "plant"); S.to("hl", 1); S.set("ins", 15); },
      (S) => { S.set("mode", "plant"); S.to("hl", 2); S.set("ins", 15); },
      (S) => { S.set("mode", "plant"); S.to("hl", 3); S.set("ins", document.body.classList.contains("shot") ? 55 : 15); },
    ],
    frame(g, S, dt) {
      const { W, H, c } = g, phone = W < 600, fs = phone ? 11 : 13, snap = document.body.classList.contains("shot");
      if (S.mode === "fuel") return drawFuel(g, S, phone, fs, snap);
      // ---------- power ----------
      const ins = S.step >= 3 ? S.ins / 100 : 0.15, Pt = clamp((0.82 - ins) / 0.67, 0, 1);
      S.Pw += (Pt - S.Pw) * (snap ? 1 : 1 - Math.exp(-dt / 2.2));
      const P = S.Pw, heat = Math.max(P, 0.05 * smooth(0.25, 0, P) + P), flow = 0.35 + 0.65 * smooth(0, 0.3, heat), steam = clamp(P, 0, 1);
      // ---------- plant box ----------
      const bx = W * 0.03, bw = W * 0.94, by = H * (phone ? 0.07 : 0.1), bh = H * (phone ? 0.68 : 0.6);
      const X = (u) => bx + bw * u, Y = (v) => by + bh * v, hl = S.step;
      const hot = c.warm, cold = c.cool;
      // cooling water (sea/river), right edge
      g.area([[X(0.84), Y(0.57)], [W, Y(0.57)], [W, Y(0.76)], [X(0.84), Y(0.76)]], cold, 0.08);
      // ---------- vessel ----------
      const vx0 = X(0.045), vx1 = X(0.245), vy0 = Y(0.18), vy1 = Y(0.88), cy0 = Y(0.46), cy1 = Y(0.8);
      const ctx = g.ctx;
      const dark = /^#[0-3]/.test(c.paper), vr = (vx1 - vx0) / 2;
      const vpath = () => { ctx.beginPath(); ctx.moveTo(vx0, vy0 + vr * 0.6); ctx.quadraticCurveTo(vx0, vy0, vx0 + vr, vy0); ctx.quadraticCurveTo(vx1, vy0, vx1, vy0 + vr * 0.6); ctx.lineTo(vx1, vy1 - vr * 0.6); ctx.quadraticCurveTo(vx1, vy1, vx0 + vr, vy1); ctx.quadraticCurveTo(vx0, vy1, vx0, vy1 - vr * 0.6); ctx.closePath(); };
      g.glow((vx0 + vx1) / 2, (cy0 + cy1) / 2, (vx1 - vx0) * 1.3, c.warm, 0.1 + 0.25 * heat);
      ctx.save(); vpath(); const wgr = ctx.createLinearGradient(0, vy0, 0, vy1); wgr.addColorStop(0, g.rgba(c.warm, 0.12 + 0.22 * heat)); wgr.addColorStop(0.55, g.rgba(c.cool, 0.16)); wgr.addColorStop(1, g.rgba(c.cool, 0.26)); ctx.fillStyle = wgr; ctx.fill(); ctx.clip();
      // water rising through the vessel: soft bands drifting upward
      const vh = vy1 - vy0;
      for (let i = 0; i < 6; i++) { const yb = vy1 - ((S.time * 26 * flow + i * vh / 6) % vh), bg2 = ctx.createLinearGradient(0, yb - 14, 0, yb + 14); bg2.addColorStop(0, g.rgba(c.ink, 0)); bg2.addColorStop(0.5, g.rgba(dark ? c.ink : c.cool, 0.07)); bg2.addColorStop(1, g.rgba(c.ink, 0)); ctx.fillStyle = bg2; ctx.fillRect(vx0, yb - 14, vx1 - vx0, 28); }
      ctx.restore();
      ctx.save(); vpath(); ctx.strokeStyle = g.rgba(c.soft, 0.75); ctx.lineWidth = 3; ctx.stroke(); ctx.restore();
      // core: lit fuel assemblies, with the blue Cherenkov glow of the water around them
      const na = phone ? 6 : 8, aw = (vx1 - vx0 - 16) / na;
      ctx.save(); if (dark) ctx.globalCompositeOperation = "lighter";
      const chx = (vx0 + vx1) / 2, chy = (cy0 + cy1) / 2, flick = 0.9 + 0.1 * Math.sin(S.time * 7) * Math.sin(S.time * 3.1);
      g.glow(chx, chy, (vx1 - vx0) * 0.85, dark ? "#5fb0ff" : c.cool, (0.08 + 0.5 * heat) * flick); g.glow(chx, chy, (vx1 - vx0) * 0.45, "#a9d6ff", 0.3 * heat * flick);
      ctx.restore();
      for (let i = 0; i < na; i++) { const x = vx0 + 8 + aw * (i + 0.5), w2 = aw * 0.3;
        ctx.save(); const fg = ctx.createLinearGradient(x - w2, 0, x + w2, 0); fg.addColorStop(0, g.rgba(c.warm, 0.35 + 0.3 * heat)); fg.addColorStop(0.4, g.rgba(heat > 0.3 ? "#ffd2a0" : c.warm, 0.55 + 0.4 * heat)); fg.addColorStop(1, g.rgba(c.warm, 0.25 + 0.25 * heat));
        ctx.fillStyle = fg; ctx.fillRect(x - w2, cy0, 2 * w2, cy1 - cy0); ctx.restore(); }
      // control rods from the top (drag them in the last step)
      const rodY = lerp(cy0 - 2, cy1, ins);
      for (let i = 0; i < na - 1; i++) { const x = vx0 + 8 + aw * (i + 1); ctx.save(); const rg2 = ctx.createLinearGradient(x - 3, 0, x + 3, 0); rg2.addColorStop(0, g.rgba(c.ink, 0.55)); rg2.addColorStop(0.5, g.rgba(c.ink, 0.95)); rg2.addColorStop(1, g.rgba(c.ink, 0.5)); ctx.fillStyle = rg2; ctx.fillRect(x - 3, vy0 - 14, 6, rodY - vy0 + 14); ctx.restore(); }
      ctx.save(); ctx.fillStyle = g.rgba(c.ink, 0.7); ctx.fillRect(vx0 + 10, vy0 - 19, vx1 - vx0 - 20, 6); ctx.restore();
      if (S.step >= 3) { const pulse = 0.35 + 0.2 * Math.sin(S.time * 4); g.glow((vx0 + vx1) / 2, vy0 - 16, (vx1 - vx0) * 0.45, c.accent, pulse); for (let i = 0; i < na - 1; i++) g.dot(vx0 + 8 + aw * (i + 1), rodY, 3, c.accent, 0.9); }
      WT.grab(ctx.canvas, {
        down(x, y) { if (S.mode !== "plant" || S.step < 3 || x < vx0 - 16 || x > vx1 + 16 || y < vy0 - 40 || y > cy1 + 20) return false; this.move(x, y); return true; },
        move(x, y) { const v = Math.round(clamp((y - cy0) / (cy1 - cy0), 0, 1) * 100); S.set("ins", v); const i = document.getElementById("rea-rod"); if (i) i.value = v; },
        hover(x, y) { ctx.canvas.style.cursor = S.mode === "plant" && S.step >= 3 && x > vx0 - 16 && x < vx1 + 16 && y > vy0 - 40 && y < cy1 + 20 ? "ns-resize" : "default"; },
      });
      // neutrons flickering in the core
      const nn = Math.round(60 * heat);
      for (let i = 0; i < nn; i++) { const n = neut[i]; n.t += dt * 2.2; if (n.t > 1) { n.t = 0; n.x = r(); n.y = r(); n.a = r() * TAU; }
        const x = lerp(vx0 + 10, vx1 - 10, n.x) + Math.cos(n.a) * n.t * 14, y = lerp(cy0 + 4, cy1 - 4, n.y) + Math.sin(n.a) * n.t * 14;
        if (y > rodY && y < cy1) g.dot(x, y, 2, c.neutron, 0.9 * (1 - n.t)); }
      for (let i = 0; i < Math.round(4 * P); i++) { const x = lerp(vx0 + 12, vx1 - 12, r()), y = lerp(Math.max(cy0, rodY), cy1, r()); g.glow(x, y, 10, "#ffffff", 0.35); }
      // ---------- steam generator ----------
      const sx0 = X(0.355), sx1 = X(0.51), sy0 = Y(0.08), sy1 = Y(0.86);
      ctx.save(); { const sg = ctx.createLinearGradient(sx0, 0, sx1, 0); sg.addColorStop(0, g.rgba(c.soft, 0.05)); sg.addColorStop(0.35, g.rgba(c.soft, 0.2)); sg.addColorStop(1, g.rgba(c.soft, 0.04)); ctx.fillStyle = sg; } ctx.strokeStyle = g.rgba(c.soft, 0.75); ctx.lineWidth = 2.5; ctx.beginPath();
      if (ctx.roundRect) ctx.roundRect(sx0, sy0, sx1 - sx0, sy1 - sy0, (sx1 - sx0) / 2); else ctx.rect(sx0, sy0, sx1 - sx0, sy1 - sy0); ctx.fill(); ctx.stroke(); ctx.restore();
      g.poly([[X(0.38), Y(0.84)], [X(0.38), Y(0.32)], [X(0.415), Y(0.24)], [X(0.45), Y(0.32)], [X(0.45), Y(0.84)]], hot, 5, 0.25);
      // ---------- turbine + generator ----------
      const tx0 = X(0.57), tx1 = X(0.8), ty = Y(0.28);
      S.rot += dt * (snap ? 0 : 9) * smooth(0, 0.08, P);
      ctx.save(); { const tg = ctx.createLinearGradient(0, ty - bh * 0.13, 0, ty + bh * 0.13); tg.addColorStop(0, g.rgba(c.soft, 0.06)); tg.addColorStop(0.3, g.rgba(c.soft, 0.24)); tg.addColorStop(1, g.rgba(c.soft, 0.05)); ctx.fillStyle = tg; } ctx.strokeStyle = g.rgba(c.soft, 0.75); ctx.lineWidth = 2;
      ctx.beginPath(); ctx.moveTo(tx0, ty - bh * 0.06); ctx.lineTo(tx1, ty - bh * 0.13); ctx.lineTo(tx1, ty + bh * 0.13); ctx.lineTo(tx0, ty + bh * 0.06); ctx.closePath(); ctx.fill(); ctx.stroke(); ctx.restore();
      g.line(tx0 - 6, ty, X(0.95), ty, c.soft, 3, 0.8);
      const nd = phone ? 4 : 6, blur = snap ? 0.18 : 0.11 * smooth(0, 0.08, P);
      for (let i = 0; i < 7; i++) { const u = ((S.time * 0.35 * (0.3 + steam) + i / 7) % 1), x = lerp(tx0 + 6, tx1 - 6, u), R = lerp(bh * 0.04, bh * 0.11, u); g.glow(x, ty + Math.sin(i * 3 + S.time) * R * 0.3, R * 1.4, c.ink, 0.1 * steam * (1 - u * 0.5)); }
      for (let d = 0; d < nd; d++) { const x = lerp(tx0 + 10, tx1 - 10, (d + 0.5) / nd), R = lerp(bh * 0.055, bh * 0.12, (d + 0.5) / nd);
        ctx.save(); ctx.strokeStyle = g.rgba(c.soft, 0.35); ctx.lineWidth = 1; ctx.beginPath(); ctx.ellipse(x, ty, 4, R, 0, 0, TAU); ctx.stroke(); ctx.restore();
        for (let k = 3; k >= 0; k--) for (let b = 0; b < 6; b++) { const a = S.rot - k * blur + b * TAU / 6 + d * 0.4, yb = Math.sin(a) * R, front = Math.cos(a), al = (front > 0 ? 0.85 : 0.3) * (k ? 0.22 * (4 - k) / 3 : 1);
          g.line(x - 3 * front, ty, x + 3 * front, ty + yb, front > 0 ? c.ink : c.soft, k ? 3.2 : 2.2, al); } }
      const gx0 = X(0.83), gx1 = X(0.96);
      ctx.save(); ctx.fillStyle = g.rgba(c.photon, 0.12 + 0.25 * P); ctx.strokeStyle = g.rgba(c.soft, 0.7); ctx.lineWidth = 2; ctx.beginPath();
      if (ctx.roundRect) ctx.roundRect(gx0, ty - bh * 0.08, gx1 - gx0, bh * 0.16, 8); else ctx.rect(gx0, ty - bh * 0.08, gx1 - gx0, bh * 0.16); ctx.fill(); ctx.stroke(); ctx.restore();
      g.glow((gx0 + gx1) / 2, ty, bh * 0.16, c.photon, 0.5 * P);
      for (let i = 0; i < 5; i++) { const yy = ty + Math.sin(S.rot * 0.5 + i * TAU / 5) * bh * 0.065, al = 0.25 + 0.5 * Math.max(0, Math.cos(S.rot * 0.5 + i * TAU / 5)); g.line(gx0 + 4, yy, gx1 - 4, yy, c.photon, 2, al * (0.4 + 0.6 * P)); }
      // power line up to the grid
      const lx = (gx0 + gx1) / 2; g.line(lx, ty - bh * 0.08, lx, by - (phone ? 2 : 10), c.photon, 2, 0.4 + 0.6 * P);
      for (let i = 0; i < 3; i++) { const u = (S.time * 1.5 + i / 3) % 1; if (P > 0.03) g.glow(lx, lerp(ty - bh * 0.08, by - 6, u), 8, c.photon, 0.8 * P); }
      // ---------- condenser ----------
      const kx0 = X(0.57), kx1 = X(0.84), ky0 = Y(0.54), ky1 = Y(0.72);
      ctx.save(); { const kg = ctx.createLinearGradient(0, ky0, 0, ky1); kg.addColorStop(0, g.rgba(c.soft, 0.16)); kg.addColorStop(1, g.rgba(c.cool, 0.22)); ctx.fillStyle = kg; } ctx.strokeStyle = g.rgba(c.soft, 0.75); ctx.lineWidth = 2; ctx.beginPath();
      if (ctx.roundRect) ctx.roundRect(kx0, ky0, kx1 - kx0, ky1 - ky0, 8); else ctx.rect(kx0, ky0, kx1 - kx0, ky1 - ky0); ctx.fill(); ctx.stroke(); ctx.restore();
      // ---------- pipes ----------
      const pipe = (p, col, w, a) => g.poly(p.pts.map(([u, v]) => [X(u), Y(v)]), col, w, a);
      const pseg = (p, i0, i1, col, w, a) => g.poly(p.pts.slice(i0, i1 + 1).map(([u, v]) => [X(u), Y(v)]), col, w, a);
      pipe(PRI, c.soft, phone ? 9 : 12, 0.2); pipe(SEC, c.soft, phone ? 9 : 12, 0.2); pipe(CW, c.cool, phone ? 9 : 12, 0.16);
      pseg(PRI, 1, 7, c.warm, phone ? 5 : 7, 0.18 + 0.25 * heat); pseg(PRI, 7, 12, c.cool, phone ? 5 : 7, 0.25);
      pseg(SEC, 0, 7, c.ink, phone ? 5 : 7, 0.06 + 0.1 * steam); pseg(SEC, 7, 12, c.cool, phone ? 5 : 7, 0.25);
      // ---------- moving water ----------
      const sh = smooth;
      const spd = dt * (snap ? 0 : 0.055) * flow;
      for (const q of pp) { q.s += spd; const [u, v, f] = at(PRI, q.s); let x = X(u), y = Y(v);
        // in the vessel the water spreads across the core
        if (u < 0.2 && v > 0.3 && v < 0.86) x = lerp(vx0 + 12, vx1 - 12, (q.o + 1) / 2);
        const tC = f < 0.08 ? 0 : f < 0.13 ? (f - 0.08) / 0.05 : f < 0.6 ? 1 : f < 0.72 ? 1 - (f - 0.6) / 0.12 : 0; // heats in the core, cools in the tubes
        const inCore = v > 0.46 && v < 0.8 && u < 0.2, tt = inCore ? lerp(0, 1, (0.8 - v) / 0.34) * heat : tC * (0.3 + 0.7 * heat);
        g.dot(x, y, phone ? 2.1 : 2.6, tt > 0.5 ? hot : cold, 0.55 + 0.4 * tt); }
      for (const q of sp) { q.s += spd * 1.15; const [u, v, f] = at(SEC, q.s), x = X(u) + q.o * 2, y = Y(v);
        const isSteam = (u > 0.43 && v < 0.6 && u < 0.8) || (u > 0.47 && u < 0.5 && v < 0.3); if (isSteam) { if (q.o > lerp(-1, 1, steam)) continue; g.glow(x, y, phone ? 7 : 10, c.ink, 0.2); g.dot(x, y, 1.8, c.ink, 0.75); } else g.dot(x, y, phone ? 2.1 : 2.6, c.cool, 0.8); }
      for (const q of cp) { q.s += spd * 0.8; const [u, v, f] = at(CW, q.s); g.dot(X(u), Y(v) + q.o * 2, phone ? 2 : 2.4, f < 0.5 ? c.cool : g.rgba(c.warm, 1), 0.7); }
      // boiling bubbles on the secondary side of the steam generator
      for (let i = 0; i < Math.round(14 * steam); i++) { const u = (S.time * 0.4 + i * 0.137) % 1; g.ring(X(0.485) + Math.sin(i * 7 + S.time * 3) * 4, lerp(Y(0.6), Y(0.2), u), 2.4, c.ink, 1, 0.45 * (1 - u)); }
      // ---------- highlights per step ----------
      const H1 = hl === 1, H2 = hl === 2, H3 = hl === 3;
      if (H1) { g.ring((vx0 + vx1) / 2, (cy0 + cy1) / 2, (vx1 - vx0) * 0.7, c.warm, 1.5, 0.5 + 0.3 * Math.sin(S.time * 3), [4, 5]); }
      if (H2) { g.glow(X(0.68), ty, bh * 0.2, c.ink, 0.08); }
      // ---------- labels ----------
      const L = (s, x, y, o = {}) => g.label(s, x, y, Object.assign({ color: c.soft, size: fs - 1, bg: true }, o));
      L(phone ? "reactor" : "reactor vessel", (vx0 + vx1) / 2, vy1 + (phone ? 10 : 14), { color: H1 ? c.ink : c.soft, weight: H1 ? 600 : 500 });
      if (!phone || H1 || H3) L(H3 ? "control rods" : "core", H3 ? (vx0 + vx1) / 2 : vx1 + (phone ? 4 : 8), H3 ? vy0 - 28 : (cy0 + cy1) / 2, { align: H3 ? "center" : "left", color: H3 ? c.ink : c.warm, weight: 600 });
      L(phone ? "steam gen." : "steam generator", (sx0 + sx1) / 2, sy1 + (phone ? 12 : 16), { color: H2 ? c.ink : c.soft });
      L("turbine", (tx0 + tx1) / 2, ty + bh * 0.13 + (phone ? 10 : 14), { color: H2 ? c.ink : c.soft, weight: H2 ? 600 : 500 });
      L(phone ? "gen." : "generator", (gx0 + gx1) / 2, ty + bh * 0.08 + (phone ? 10 : 14), { color: c.photon, weight: 600 });
      L("condenser", (kx0 + kx1) / 2, ky1 + (phone ? 10 : 14), { color: H2 ? c.ink : c.soft });
      if (!phone) L("sea or river water", X(0.92), Y(0.8), { color: c.cool });
      if (H1 && !phone) { L("325 °C out", X(0.3), Y(0.3), { color: c.warm, weight: 600 }); L("290 °C in", X(0.3), Y(1.06), { color: c.cool, weight: 600 }); }
      if (H2 && !phone) L("steam ~285 °C", X(0.51), Y(0.03), { color: c.ink, align: "left" });
      // ---------- readouts ----------
      const ry = H * (phone ? 0.85 : 0.82), rd = { color: c.ink, size: fs + 1, weight: 600, serif: true };
      const MWt = Math.round(PTH * heat), MWe = Math.round(PTH * ETA * P);
      if (H1) {
        g.label(phone ? "155 bar: hot, but no boiling" : "155 bar keeps the water liquid at 325 °C", W / 2, ry, rd);
        g.label(phone ? "the water also slows the neutrons" : "the water carries the heat and slows the neutrons", W / 2, ry + fs + 10, { color: c.soft, size: fs, serif: true });
      } else {
        const bw2 = Math.min(W * 0.36, 220), bx1 = W / 2 - bw2 - 8, bx2 = W / 2 + 8, bb = ry - 6;
        const bar = (x, f, col, t) => { ctx.save(); ctx.fillStyle = g.rgba(c.soft, 0.15); ctx.fillRect(x, bb, bw2, 10); ctx.fillStyle = col; ctx.fillRect(x, bb, bw2 * clamp(f, 0, 1), 10); ctx.restore(); g.glow(x + bw2 * clamp(f, 0, 1), bb + 5, 14, col, 0.5); g.label(t, x, bb - 12, { color: col, size: fs, weight: 600, align: "left" }); };
        bar(bx1, heat, c.warm, `heat ${MWt} MW`); bar(bx2, P * ETA / 1, c.photon, phone ? `electric ${MWe} MW` : `electricity ${MWe} MW`);
        const msg = P < 0.03 ? (phone ? "chain stopped; fuel still warm (afterheat)" : "chain reaction stopped; the fuel still gives off afterheat")
          : H3 ? (phone ? "turbine speed fixed by the grid; more steam, more push" : "the turbine's speed is fixed by the grid; more steam pushes harder")
          : (phone ? "2/3 of the heat goes to the water" : "about two thirds of the heat leaves through the condenser");
        g.label(msg, W / 2, ry + fs + 16, { color: c.soft, size: fs, serif: true });
      }
      g.label("illustration", W - 6, H - 10, { color: c.faint, size: 10, align: "right" });
    },
  });

  function drawFuel(g, S, phone, fs, snap) {
    const { W, H, c, ctx } = g, z = clamp(S.z, 0, 3), cx = W * 0.5, cy = H * (phone ? 0.47 : 0.45), R = Math.min(W, H);
    const vis = (k) => clamp(1 - Math.abs(z - k) * 1.6, 0, 1);
    WT.grab(ctx.canvas, {
      down(x) { if (S.mode !== "fuel") return false; this.x0 = x; this.z0 = S.z; return true; },
      move(x) { const v = clamp(this.z0 + (x - this.x0) / (W * 0.25), 0, 3); S.set("z", v); const i = document.getElementById("rea-z"); if (i) i.value = v; },
      hover() { ctx.canvas.style.cursor = S.mode === "fuel" ? "ew-resize" : "default"; },
    });
    g.label(phone ? "drag sideways to zoom" : "drag sideways to zoom out", W / 2, H * (phone ? 0.06 : 0.08), { color: c.faint, size: fs - 1 });
    // 0: pellet next to a pile of coal
    const a0 = vis(0);
    if (a0 > 0.01) {
      ctx.save(); ctx.globalAlpha = a0;
      const pw = R * 0.12, ph = pw * 1.25, px = W * (phone ? 0.27 : 0.3), py = cy;
      g.glow(px, py, pw * 1.6, c.warm, 0.25);
      const gr = ctx.createLinearGradient(px - pw / 2, 0, px + pw / 2, 0); gr.addColorStop(0, g.rgba(c.soft, 0.5)); gr.addColorStop(0.35, g.rgba(c.ink, 0.55)); gr.addColorStop(1, g.rgba(c.soft, 0.25));
      ctx.fillStyle = gr; ctx.fillRect(px - pw / 2, py - ph / 2, pw, ph);
      ctx.beginPath(); ctx.ellipse(px, py - ph / 2, pw / 2, pw * 0.18, 0, 0, TAU); ctx.fillStyle = g.rgba(c.ink, 0.35); ctx.fill(); ctx.strokeStyle = g.rgba(c.soft, 0.7); ctx.stroke();
      ctx.beginPath(); ctx.ellipse(px, py + ph / 2, pw / 2, pw * 0.18, 0, 0, Math.PI); ctx.strokeStyle = g.rgba(c.soft, 0.7); ctx.stroke();
      ctx.restore();
      g.label(phone ? "UO₂ pellet, 1 cm" : "uranium oxide pellet, about 1 cm", px, py + ph / 2 + 24, { color: c.ink, size: fs, weight: 600, alpha: a0 });
      g.label("≈", W * 0.5, py, { color: c.ink, size: fs + 14, weight: 600, alpha: a0 });
      const hx = W * (phone ? 0.74 : 0.71), hy = py + ph / 2, hw = R * (phone ? 0.22 : 0.24), hh = hw * 0.85;
      for (const [u, v, s] of COAL) g.ball(hx + u * hw, hy - v * hh, R * 0.018 * s, "#3a3a40", a0);
      g.label(phone ? "1 tonne of coal" : "about 1 tonne of coal (or 480 m³ of gas)", hx, hy + 24, { color: c.ink, size: fs, weight: 600, alpha: a0 });
      g.label("same heat, roughly", W * 0.5, H * (phone ? 0.86 : 0.8), { color: c.soft, size: fs + 1, serif: true, alpha: a0 });
    }
    // 1: a rod, pellets stacked inside
    const a1 = vis(1);
    if (a1 > 0.01) {
      const rh = H * 0.62, rw = Math.max(10, R * 0.035), x = cx, y0 = cy - rh / 2, n = 40;
      g.glow(x, cy, rh * 0.45, c.warm, 0.12 * a1);
      ctx.save(); ctx.globalAlpha = a1; ctx.fillStyle = g.rgba(c.soft, 0.18); ctx.strokeStyle = g.rgba(c.soft, 0.8); ctx.lineWidth = 1.5; ctx.fillRect(x - rw / 2, y0, rw, rh); ctx.strokeRect(x - rw / 2, y0, rw, rh);
      for (let i = 0; i < n; i++) { ctx.fillStyle = g.rgba(c.ink, i % 2 ? 0.45 : 0.35); ctx.fillRect(x - rw / 2 + 2, y0 + 4 + (rh - 8) * i / n, rw - 4, (rh - 8) / n - 1); }
      ctx.restore();
      g.label(phone ? "fuel rod, ~4 m" : "fuel rod, about 4 m long", x + rw + 10, y0 + 10, { color: c.ink, size: fs, weight: 600, align: "left", alpha: a1 });
      g.label(phone ? "~350 pellets inside" : "about 350 pellets in a metal tube", x + rw + 10, y0 + 30, { color: c.soft, size: fs - 1, align: "left", alpha: a1 });
      g.label("(not to scale)", x + rw + 10, y0 + rh - 8, { color: c.faint, size: fs - 2, align: "left", alpha: a1 });
    }
    // 2: an assembly seen from the top, 17 x 17
    const a2 = vis(2);
    if (a2 > 0.01) {
      const s = R * 0.62, x0 = cx - s / 2, y0 = cy - s / 2, d = s / 17;
      g.glow(cx, cy, s * 0.7, c.warm, 0.18 * a2);
      ctx.save(); ctx.globalAlpha = a2; ctx.strokeStyle = g.rgba(c.soft, 0.6); ctx.strokeRect(x0 - 3, y0 - 3, s + 6, s + 6); ctx.restore();
      for (let i = 0; i < 17; i++) for (let j = 0; j < 17; j++) { const gt = GTS.has(i * 17 + j), x = x0 + d * (j + 0.5), y = y0 + d * (i + 0.5);
        if (gt) g.ring(x, y, d * 0.42, c.ink, 1.4, 0.8 * a2); else g.ball(x, y, d * 0.4, c.warm, a2); }
      g.label(phone ? "assembly: 264 rods" : "fuel assembly from above: 264 rods", cx, y0 - 16, { color: c.ink, size: fs, weight: 600, alpha: a2 });
      g.label(phone ? "rings: control-rod guide tubes" : "rings: tubes the control rods slide into", cx, y0 + s + 18, { color: c.soft, size: fs - 1, alpha: a2 });
    }
    // 3: the core, 193 assemblies
    const a3 = vis(3);
    if (a3 > 0.01) {
      const s = R * 0.66, d = s / 15;
      g.glow(cx, cy, s * 0.75, c.warm, 0.25 * a3);
      CORE_ROWS.forEach((n, i) => { for (let j = 0; j < n; j++) { const x = cx + (j - (n - 1) / 2) * d, y = cy + (i - 7) * d, e = Math.hypot(x - cx, y - cy) / (s / 2);
        ctx.save(); ctx.globalAlpha = a3; ctx.fillStyle = g.rgba(c.warm, 0.85 - 0.45 * e); ctx.fillRect(x - d * 0.45, y - d * 0.45, d * 0.9, d * 0.9); ctx.restore(); } });
      g.ring(cx, cy, s * 0.56, c.soft, 2, 0.6 * a3);
      g.label(phone ? "core: 193 assemblies" : "the core from above: 193 assemblies", cx, cy - s * 0.56 - 16, { color: c.ink, size: fs, weight: 600, alpha: a3 });
      g.label(phone ? "~51,000 rods, ~3.4 m across" : "about 51,000 rods in a cylinder about 3.4 m across", cx, cy + s * 0.56 + 18, { color: c.soft, size: fs - 1, alpha: a3 });
    }
    const names = ["pellet", "rod", "assembly", "core"];
    names.forEach((n, i) => { const x = W * (0.2 + 0.2 * i), y = H * (phone ? 0.95 : 0.92), on = vis(i); g.dot(x, y - 12, 3.5, on > 0.5 ? c.warm : c.faint, 0.9); g.label(n, x, y + 2, { color: on > 0.5 ? c.ink : c.soft, size: fs - 1, weight: on > 0.5 ? 600 : 500 }); });
  }
})();
