/* Why reactors run on neutrons. Three scenes: (A) a proton rolling at a lead-208 nucleus, (B) a neutron at any energy
 * down to thermal, (C) a slow neutron starting fission in U-235 (a sketch). The textbook picture of the potential energy of a proton and of a neutron against distance r from a lead-208
 * nucleus (Z = 82): a square nuclear well 50 MeV deep, with the Coulomb repulsion 1.44 Z / r MeV fm outside for the proton
 * (a uniformly charged sphere inside). The proton's well ends at the touching radius R_c = r0 (A^(1/3) + 1^(1/3)), r0 = 1.3 fm
 * (9.0 fm), so the barrier top is the standard Coulomb barrier V_B = 1.44 Z / R_c = 13 MeV; the neutron's well ends at
 * r0 A^(1/3) (7.7 fm). A ball at the chosen energy rolls in: below the barrier top the proton turns back classically; quantum
 * tunnelling (WKB, s-wave, P = exp(-2 int sqrt(2 mu (V - E)) / hbar dr)) lets about 1 in 10^N through. The neutron (s-wave)
 * has no barrier. Scenes A and B draw the nucleus itself with the particle flying at it (the potential is an inset graph);
 * scene C shows a slow neutron absorbed by U-235, the compound U-236 stretching to a neck and splitting (Ba-141 + Kr-92 + 3 n). */
(function () {
  const { TAU, clamp, lerp, smooth } = WT.util;
  const Z = 82, A = 208, R0 = 1.3, R = R0 * (Math.cbrt(A) + 1), RN = R0 * Math.cbrt(A), V0 = 50, MU = 938.27 * A / (A + 1), HC = 197.327, RMAX = 30;
  const vN = (r) => (r < RN ? -V0 : 0);                                     // neutron: square well, no barrier
  const vC = (r) => (r >= R ? 1.44 * Z / r : 1.44 * Z / (2 * R) * (3 - (r * r) / (R * R)));
  const vP = (r) => (r < R ? -V0 : 0) + vC(r);                              // proton: square well to the touching radius, Coulomb outside
  let BTOP = 0, RTOP = R; for (let r = R; r < 20; r += 0.01) { const v = vP(r); if (v > BTOP) { BTOP = v; RTOP = r; } }
  function tunnel(E) {
    if (E >= BTOP) return 1; let ri = RTOP, ro = RTOP; while (ri > 0.1 && vP(ri) > E) ri -= 0.01; while (ro < 400 && vP(ro) > E) ro += 0.01;
    let s = 0; const n = 400, h = (ro - ri) / n; for (let i = 0; i < n; i++) { const r = ri + (i + 0.5) * h; s += Math.sqrt(Math.max(0, 2 * MU * (vP(r) - E))) * h; }
    return Math.exp(-2 * s / HC);
  }
  const ball = { r: RMAX, dir: -1, inT: -9, k: "" };
  const fmtE = (mev) => (mev >= 1 ? `${mev.toFixed(1)} MeV` : mev >= 1e-3 ? `${(mev * 1000).toFixed(0)} keV` : mev >= 1e-6 ? `${(mev * 1e6).toFixed(mev < 1e-5 ? 1 : 0)} eV` : `${(mev * 1e6).toFixed(3)} eV`);
  const sup = (d) => [...String(d)].map((x) => "⁰¹²³⁴⁵⁶⁷⁸⁹"[x]).join("");

  WT.chapter("neutrons", {
    num: "Chapter 4", title: "Why reactors run on neutrons", short: "Why neutrons",
    html: `
<div class="step">
  <p>A proton is pushed back by the nucleus's charge. The small graph shows the same push as an energy hill.</p>
  <div class="ctl"><label for="wn-e1">Proton energy (MeV)</label><input id="wn-e1" type="range" data-bind="Ep" data-instant min="0.5" max="20" step="0.1" value="6"><output data-show="Ep" data-fmt="1"></output></div>
</div>
<div class="step">
  <p>A neutron has no charge: it gets in at any speed.</p>
  <div class="ctl"><label for="wn-e2">Neutron energy (slow → fast)</label><input id="wn-e2" type="range" data-bind="lgEn" data-instant min="-1.6" max="7.3" step="0.01" value="-1.6"></div>
</div>
<div class="step">
  <p>So even slow neutrons can split uranium in a reactor.</p>
</div>`,
    setup(S) { S.set("Ep", 6); S.set("lgEn", -1.6); S.set("mode", "p"); },
    steps: [(S) => S.set("mode", "p"), (S) => S.set("mode", "n"), (S) => S.set("mode", "f")],
    frame(g, S, dt) {
      if (S.mode === "f") return sceneFission(g, S, dt);
      const { W, H, c } = g, phone = W < 600, fs = phone ? 11 : 13, snap = document.body.classList.contains("shot");
      const isP = S.mode === "p", E = isP ? S.Ep : Math.pow(10, S.lgEn) * 1e-6, V = isP ? vP : vN, col = isP ? c.proton : c.neutron;
      // the nucleus itself, to scale with the distance the particle flies (px per fm from the drawn radius)
      const cxN = W * (phone ? 0.72 : 0.66), cyN = H * (phone ? 0.56 : 0.52), Rpx = Math.min(W, H) * (phone ? 0.085 : 0.08), PX = Rpx / RN;
      const xStart = W * 0.03, rStart = (cxN - xStart) / PX;
      if (ball.k !== S.mode) { ball.k = S.mode; ball.r = rStart; ball.dir = -1; ball.inT = -9; ball.tun = false; }
      let rTurn = 0; if (isP && E < BTOP) { let r = 400; while (r > RTOP && V(r) < E) r -= 0.05; rTurn = r; }
      if (isP) {                                       // the nucleus's +82 charge: a red haze that pushes protons away
        g.glow(cxN, cyN, Rpx * 3.4, c.proton, 0.16);
        g.label("+82 charge pushes protons away", cxN, cyN - Rpx * 2.2, { color: c.proton, size: fs, weight: 600, bg: true });
        if (rTurn > 0 && rTurn * PX < cxN - xStart - 10) {
          g.ring(cxN, cyN, rTurn * PX, c.proton, 1.3, 0.55, [4, 5]);
          g.label(phone ? "turns back" : "turns back here", cxN - rTurn * PX * 0.72, cyN + rTurn * PX * 0.72 + 12, { color: c.proton, size: fs - 1, bg: true });
        }
      } else g.label("no charge, no push", cxN, cyN - Rpx * 2.0, { color: c.neutron, size: fs, weight: 600, bg: true });
      g.nucleus(cxN, cyN, Rpx, { N: 60, Z: 24, t: S.time, jiggle: 0.4, seed: 3 });
      g.label("lead-208", cxN, cyN + Rpx + (phone ? 14 : 18), { color: c.soft, size: fs, weight: 600 });
      // motion: a few seconds per pass; the proton slows as it climbs the hill (speed ~ sqrt of its kinetic energy)
      const T = isP ? lerp(4.2, 2.0, clamp(E / 20, 0, 1)) : lerp(9, 1.6, clamp((S.lgEn + 1.6) / 8.9, 0, 1)), v0 = rStart / T;
      const rIn = RN * 0.55;
      if (snap) { ball.r = isP && rTurn ? Math.min(rStart, rTurn + 6) : rStart * 0.45; ball.inT = -9; ball.dir = -1; }
      else if (S.time - ball.inT > 1.3) {
        const ke = Math.max(0, E - V(ball.r)), v = isP ? v0 * Math.max(0.22, Math.sqrt(ke / Math.max(E, 1e-9))) : v0;
        ball.r += ball.dir * v * dt;
        if (ball.dir < 0 && rTurn > 0 && ball.r <= rTurn) {
          const P = tunnel(E);
          if (P > 0.002 && Math.random() < P) { ball.tun = true; ball.inT = S.time; ball.r = rIn; } else { ball.r = rTurn; ball.dir = 1; ball.tun = false; }
        }
        if (ball.dir < 0 && ball.r <= rIn) { ball.inT = S.time; ball.r = rIn; }
        if (ball.r > rStart + 2) { ball.r = rStart; ball.dir = -1; ball.tun = false; }
      } else if (S.time - ball.inT > 1.25) { ball.r = rStart; ball.dir = -1; }
      if (S.time - ball.inT < 1.3) {                   // absorbed: a flash in the nucleus
        const a = S.time - ball.inT; g.glow(cxN, cyN, Rpx * (1.2 + 2.2 * a), c.warm, 0.6 * (1 - a / 1.3));
        g.label(ball.tun ? "tunnelled through!" : "in!", cxN, cyN - Rpx - 16, { color: c.warm, size: fs + 1, weight: 700, bg: true });
      } else {                                         // in flight: head-on in, deflected upward on the way back out
        const bx = cxN - ball.r * PX, by = cyN - (ball.dir > 0 ? (ball.r - rTurn) * PX * 0.45 : 0);
        g.glow(bx, by, 14, col, 0.45); g.ball(bx, by, 7, col);
        g.label(`${isP ? "proton" : "neutron"} · ${fmtE(E)}`, bx, by - 18, { color: col, size: fs, weight: 600, bg: true });
      }
      // inset: the same physics as energy against distance, with a dot where the particle is now
      const ix = W * (phone ? 0.04 : 0.03), iy = H * 0.05, iw = W * (phone ? 0.42 : 0.27), ih = H * (phone ? 0.2 : 0.25), RI = 30;
      const IX = (r) => ix + iw * clamp(r, 0, RI) / RI, VL = -55, VH = 20, IY = (u) => lerp(iy + ih, iy, (clamp(u, VL, VH) - VL) / (VH - VL));
      g.ctx.save(); g.ctx.fillStyle = g.rgba(c.card, 0.85); g.ctx.strokeStyle = g.rgba(c.line, 0.9); g.ctx.lineWidth = 1;
      g.ctx.beginPath(); g.ctx.rect(ix - 6, iy - 18, iw + 12, ih + 30); g.ctx.fill(); g.ctx.stroke(); g.ctx.restore();
      const ipts = []; for (let k = 0; k <= 150; k++) { const r = RI * k / 150; ipts.push([IX(r), IY(V(r))]); }
      g.poly(ipts, col, 2, 1); g.line(ix, IY(0), ix + iw, IY(0), c.line, 1, 0.8, [3, 4]);
      g.line(ix, IY(E), ix + iw, IY(E), c.ink, 1, 0.5, [5, 4]);
      g.label("energy vs distance", ix, iy - 9, { color: c.soft, size: fs - 2, align: "left" });
      if (isP) g.label(`hill ≈ ${BTOP.toFixed(0)} MeV`, IX(RTOP) + 4, IY(BTOP) - 9, { color: c.proton, size: fs - 2, align: "left" });
      if (S.time - ball.inT >= 1.3 && ball.r <= RI) g.dot(IX(ball.r), IY(E), 4, col, 1);
      // verdict
      let msg;
      if (isP) { const P = tunnel(E); msg = E >= BTOP ? "over the hill: it gets in" : P > 0.01 ? `mostly pushed back · ${(100 * P).toFixed(0)} % tunnel through` : `pushed back · about 1 in 10${sup(Math.round(-Math.log10(Math.max(P, 1e-300))))} tunnels through`; }
      else msg = E < 1e-6 ? "even this crawling neutron gets in" : "it gets in";
      g.label(msg, W * 0.5, H * 0.9, { color: c.ink, size: fs + 3, weight: 600, serif: true, bg: true });
      g.label("illustration", W - 6, 12, { color: c.faint, size: 10, align: "right" });
    },
  });

  // ---------- scene C: a slow neutron is absorbed by U-235; U-236 stretches, necks and splits ----------
  const fis = { t0: 0 };
  function sceneFission(g, S, dt) {
    const { W, H, c, ctx } = g, phone = W < 600, fs = phone ? 11 : 13, snap = document.body.classList.contains("shot");
    const cx = W * 0.55, cy = H * 0.44, Rn = Math.min(W, H) * (phone ? 0.11 : 0.1), CYC = 6.6;
    let a = (S.time - fis.t0) % CYC; if (snap) a = 4.4;
    const sx = W * 0.05, rBa = Rn * 0.842, rKr = Rn * 0.731;   // fragment radii ~ A^(1/3): Ba-141 and Kr-92 against U-236
    let cap = "";
    if (a < 2.2) {                                   // the slow neutron drifts in
      const f = smooth(0, 2.2, a), x = lerp(sx, cx - Rn - 6, f), y = cy + Math.sin(a * 3) * 4;
      g.nucleus(cx, cy, Rn, { N: 70, Z: 28, t: S.time, jiggle: 0.4, seed: 4 });
      g.glow(x, y, 14, c.neutron, 0.45); g.ball(x, y, 6, c.neutron);
      g.label("slow neutron, 0.025 eV", x, y - 20, { color: c.neutron, size: fs, weight: 600, bg: true });
      cap = "U-235";
    } else if (a < 3.0) {                            // absorbed: U-236 is hot and wobbles
      const f = (a - 2.2) / 0.8; g.glow(cx, cy, Rn * 2.1, c.warm, 0.35 * f);
      g.nucleus(cx, cy, Rn, { N: 70, Z: 28, t: S.time, jiggle: 0.9, heat: 2, beta: 0.12 + 0.22 * f + 0.08 * Math.sin(a * 18), seed: 4 });
      cap = "U-236, hot and wobbling";
    } else if (a < 3.7) {                            // it stretches into two lobes joined by a thinning neck
      const f = smooth(3.0, 3.7, a), d = Rn * lerp(0.35, 0.95, f), neck = Rn * lerp(0.75, 0.12, f);
      ctx.save(); ctx.fillStyle = g.rgba(c.warm, 0.32); ctx.beginPath(); ctx.rect(cx - d, cy - neck, 2 * d, 2 * neck); ctx.fill(); ctx.restore();
      g.glow(cx, cy, Rn * 1.8, c.warm, 0.3);
      g.nucleus(cx - d, cy, lerp(Rn * 0.9, rBa, f), { N: 35, Z: 23, t: S.time, jiggle: 0.8, heat: 1.8, seed: 7 });
      g.nucleus(cx + d, cy, lerp(Rn * 0.85, rKr, f), { N: 23, Z: 15, t: S.time, jiggle: 0.8, heat: 1.8, seed: 9 });
      cap = "stretching: a neck forms";
    } else {                                         // split: two fragments and 3 neutrons fly apart, ~200 MeV
      const f = smooth(3.7, 5.4, a), d = Rn * (0.95 + 2.6 * f), al = 1 - smooth(6.0, 6.6, a);
      g.glow(cx, cy, Rn * (1.4 + 2.6 * f), "#ffffff", 0.55 * (1 - f));
      const xa = cx - d, xb = cx + d * 1.25;         // the lighter fragment moves faster (momentum balance)
      g.nucleus(xa, cy - d * 0.08, rBa, { N: 35, Z: 23, t: S.time, jiggle: 0.6, heat: 1.4, seed: 7, alpha: al });
      g.nucleus(xb, cy + d * 0.1, rKr, { N: 23, Z: 15, t: S.time, jiggle: 0.6, heat: 1.4, seed: 9, alpha: al });
      g.label("Ba-141", xa, cy - d * 0.08 + rBa + 14, { color: c.soft, size: fs, weight: 600, alpha: al });
      g.label("Kr-92", xb, cy + d * 0.1 + rKr + 14, { color: c.soft, size: fs, weight: 600, alpha: al });
      [-1.25, 1.6, 3.6].forEach((ang) => { const dd = Rn * (0.6 + 4.4 * f), x = cx + Math.cos(ang) * dd, y = cy + Math.sin(ang) * dd * 0.85; g.line(x - Math.cos(ang) * 16, y - Math.sin(ang) * 13, x, y, c.neutron, 2, 0.35 * al); g.ball(x, y, 5, c.neutron, al); });
      if (f > 0.15) g.label("≈ 200 MeV released", cx, cy - Rn * 1.9, { color: c.warm, size: fs + 2, weight: 700, bg: true, alpha: al });
      cap = "two fragments + 3 new neutrons";
    }
    g.label(cap, cx, H * 0.74, { color: c.soft, size: fs + 1, weight: 600 });
    g.label(phone ? "slow neutron + U-235 → fission" : "a slow neutron + U-235 → two fragments, 2–3 new neutrons, about 200 MeV", W * 0.5, H * 0.84, { color: c.ink, size: fs + 1, weight: 600, serif: true });
    g.label("a proton this slow could never get in", W * 0.5, H * 0.84 + fs + 12, { color: c.soft, size: fs, serif: true, italic: true });
    g.label("illustration", W - 6, 12, { color: c.faint, size: 10, align: "right" });
  }
})();
