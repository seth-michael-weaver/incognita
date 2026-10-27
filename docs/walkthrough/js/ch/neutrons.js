/* Why reactors run on neutrons. Three scenes: (A) a proton rolling at a lead-208 nucleus, (B) a neutron at any energy
 * down to thermal, (C) a slow neutron starting fission in U-235 (a sketch). The textbook picture of the potential energy of a proton and of a neutron against distance r from a lead-208
 * nucleus (Z = 82): a square nuclear well 50 MeV deep, with the Coulomb repulsion 1.44 Z / r MeV fm outside for the proton
 * (a uniformly charged sphere inside). The proton's well ends at the touching radius R_c = r0 (A^(1/3) + 1^(1/3)), r0 = 1.3 fm
 * (9.0 fm), so the barrier top is the standard Coulomb barrier V_B = 1.44 Z / R_c = 13 MeV; the neutron's well ends at
 * r0 A^(1/3) (7.7 fm). A ball at the chosen energy rolls in: below the barrier top the proton turns back classically; quantum
 * tunnelling (WKB, s-wave, P = exp(-2 int sqrt(2 mu (V - E)) / hbar dr)) lets about 1 in 10^N through. The neutron (s-wave)
 * has no barrier. */
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
  <p>A proton is pushed back by the nucleus's charge.</p>
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
      if (ball.k !== S.mode) { ball.k = S.mode; ball.r = RMAX; ball.dir = -1; ball.inT = -9; }
      const x0 = W * (phone ? 0.12 : 0.1), x1 = W * 0.95, y0 = H * 0.1, y1 = H * 0.78, X = (r) => x0 + (x1 - x0) * r / RMAX;
      const VL = -55, VH = 20, Y = (v) => lerp(y1, y0, (v - VL) / (VH - VL));
      const pts = []; for (let i = 0; i <= 300; i++) { const r = RMAX * i / 300; pts.push([X(r), Y(V(r))]); }
      g.ground(pts, col, (y1 - y0) * 0.3, 0.2); g.poly(pts, col, 2.6, 1);
      g.line(x0, Y(0), x1, Y(0), c.line, 1, 0.8, [3, 4]);
      g.label("0", x0 - 6, Y(0), { color: c.faint, size: fs - 2, align: "right" }); g.label("−50", x0 - 6, Y(-50), { color: c.faint, size: fs - 2, align: "right" });
      g.label("energy (MeV)", x0, y0 - 16, { color: c.soft, size: fs - 1, align: "left" });
      g.label(isP ? "proton" : "neutron", x0 + 6, y0 + 6, { color: col, size: fs + 2, weight: 600, align: "left" });
      g.nucleus(X(0) + 14, Y(-V0) - 20, phone ? 12 : 17, { N: 46, Z: 18, t: S.time, jiggle: 0.4 });
      if (isP) g.label(`Coulomb barrier ≈ ${BTOP.toFixed(0)} MeV`, X(RTOP) + 8, Y(BTOP) - 12, { color: c.proton, size: fs, weight: 600, align: "left", bg: true });
      else g.label("no charge, no barrier", X(RN) + 12, Y(0) - 18, { color: c.neutron, size: fs, weight: 600, align: "left", bg: true });
      // energy line and the rolling ball (its speed grows as the square root of its kinetic energy)
      g.line(x0, Y(E), x1, Y(E), c.ink, 1, 0.45, [6, 5]); g.label(fmtE(E), x1, Y(E) - 12, { color: c.ink, size: fs, weight: 600, align: "right" });
      let rTurn = 0; if (isP && E < BTOP) { let r = RMAX; while (r > RTOP && V(r) < E) r -= 0.02; rTurn = r; }
      if (snap) { ball.r = isP ? Math.min(RMAX - 0.5, Math.max(rTurn + 2, 16)) : 18; ball.inT = -9; }
      else if (S.time - ball.inT > 1.3) {
        const v = isP ? 5 + 5 * Math.sqrt(Math.max(0.1, E - V(ball.r))) : clamp(3 + 9 * Math.sqrt(Math.max(E, 1e-9)), 2.2, 30);
        ball.r += ball.dir * v * dt;
        if (ball.dir < 0 && rTurn > 0 && ball.r <= rTurn) { ball.r = rTurn; ball.dir = 1; }
        const rIn = (isP ? R : RN) * 0.6; if (ball.dir < 0 && ball.r <= rIn) { ball.inT = S.time; ball.r = rIn; }
        if (ball.r > RMAX + 1) { ball.r = RMAX; ball.dir = -1; }
      } else if (S.time - ball.inT > 1.25) { ball.r = RMAX; ball.dir = -1; }
      if (S.time - ball.inT < 1.3) { const a = S.time - ball.inT; g.glow(X(0) + 14, Y(-V0) - 20, 30 + 50 * a, c.warm, 0.6 * (1 - a / 1.3)); }
      else { const bx = X(Math.min(ball.r, RMAX - 0.4)), by = Y(E) - 9; g.glow(bx, by, 16, col, 0.4); g.ball(bx, by, 8, col); }
      // verdict
      let msg;
      if (isP) { const P = tunnel(E); msg = E >= BTOP ? "over the barrier: it gets in" : P > 0.01 ? `mostly turned back · ${(100 * P).toFixed(0)} % tunnel through` : `turned back · about 1 in 10${sup(Math.round(-Math.log10(Math.max(P, 1e-300))))} tunnels through`; }
      else msg = E < 1e-6 ? "even this crawling neutron gets in" : "it gets in";
      g.label(msg, W * 0.55, y1 + (phone ? 22 : 30), { color: c.ink, size: fs + 2, weight: 600, serif: true, bg: true });
      [0, 10, 20, 30].forEach((r) => g.label(String(r), X(r), H * 0.9, { color: c.faint, size: fs - 2 }));
      g.label(phone ? "distance from lead-208 (fm) →" : "distance from the centre of lead-208 (fm) →", x1, H * 0.95, { color: c.soft, size: fs - 1, align: "right" });
      g.label("illustration", W - 6, 12, { color: c.faint, size: 10, align: "right" });
    },
  });

  // ---------- scene C: a slow neutron starts fission (a sketch, not to scale) ----------
  const fis = { t0: 0 };
  function sceneFission(g, S, dt) {
    const { W, H, c } = g, phone = W < 600, fs = phone ? 11 : 13, snap = document.body.classList.contains("shot");
    const cx = W * 0.55, cy = H * 0.42, Rn = Math.min(W, H) * (phone ? 0.1 : 0.09), CYC = 5.2;
    let a = (S.time - fis.t0) % CYC; if (snap) a = 3.4;
    const sx = W * 0.06;
    if (a < 2.2) {                                   // the slow neutron drifts in
      const f = smooth(0, 2.2, a), x = lerp(sx, cx - Rn - 6, f), y = cy + Math.sin(a * 3) * 4;
      g.nucleus(cx, cy, Rn, { N: 70, Z: 28, t: S.time, jiggle: 0.4, seed: 4 });
      g.glow(x, y, 14, c.neutron, 0.45); g.ball(x, y, 6, c.neutron);
      g.label("0.025 eV neutron", x, y - 20, { color: c.neutron, size: fs, weight: 600, bg: true });
    } else if (a < 3.0) {                            // absorbed: the new nucleus wobbles and stretches
      const f = (a - 2.2) / 0.8; g.glow(cx, cy, Rn * 2.2, c.warm, 0.35 * f);
      g.nucleus(cx, cy, Rn, { N: 70, Z: 28, t: S.time, jiggle: 0.9, heat: 2, beta: 0.15 + 0.35 * f + 0.08 * Math.sin(a * 18), seed: 4 });
    } else {                                         // it splits: two fragments and 2-3 neutrons fly apart
      const f = smooth(3.0, 4.6, a), d = Rn * (0.6 + 2.4 * f), al = 1 - smooth(4.6, 5.2, a);
      g.glow(cx, cy, Rn * (1.5 + 2.5 * f), "#ffffff", 0.5 * (1 - f));
      g.nucleus(cx - d, cy - d * 0.12, Rn * 0.78, { N: 34, Z: 13, t: S.time, jiggle: 0.6, heat: 1.5, seed: 7, alpha: al });
      g.nucleus(cx + d, cy + d * 0.12, Rn * 0.85, { N: 40, Z: 15, t: S.time, jiggle: 0.6, heat: 1.5, seed: 9, alpha: al });
      [-1.9, 0.4, 2.3].forEach((ang, k) => { const dd = Rn * (0.8 + 4.2 * f), x = cx + Math.cos(ang + k) * dd, y = cy + Math.sin(ang + k) * dd * 0.8; g.line(x - Math.cos(ang + k) * 14, y - Math.sin(ang + k) * 11, x, y, c.neutron, 2, 0.3 * al); g.ball(x, y, 5, c.neutron, al); });
    }
    g.label(a < 3.0 ? (a < 2.2 ? "U-235" : "U-236, wobbling") : "two fragments", cx, cy + Rn * 1.7, { color: c.soft, size: fs, weight: 600 });
    g.label(phone ? "slow neutron + U-235 → fission" : "a slow neutron + U-235 → two fragments, 2–3 new neutrons, about 200 MeV", W * 0.5, H * 0.84, { color: c.ink, size: fs + 1, weight: 600, serif: true });
    g.label("a proton this slow could never get in", W * 0.5, H * 0.84 + fs + 12, { color: c.soft, size: fs, serif: true, italic: true });
    g.label("illustration", W - 6, 12, { color: c.faint, size: 10, align: "right" });
  }
})();
