/* Why neutrons? The potential energy of a proton and of a neutron against distance r from a lead-208 nucleus (Z = 82):
 * nuclear attraction as a Woods-Saxon well (depth 50 MeV, R = 1.25 A^(1/3) fm, diffuseness 0.65 fm) for both; the proton
 * also feels the Coulomb repulsion 1.44 Z / r MeV fm (a uniformly charged sphere inside R). A ball at the chosen energy rolls
 * in: below the barrier top the proton turns back classically; quantum tunnelling (WKB, s-wave,
 * P = exp(-2 int sqrt(2 mu (V - E)) / hbar dr)) lets about 1 in 10^N through. The neutron (s-wave) has no barrier. */
(function () {
  const { TAU, clamp, lerp, smooth } = WT.util;
  const Z = 82, A = 208, R = 1.25 * Math.cbrt(A), AD = 0.65, V0 = 50, MU = 938.27 * A / (A + 1), HC = 197.327, RMAX = 30;
  const vN = (r) => -V0 / (1 + Math.exp((r - R) / AD));
  const vC = (r) => (r >= R ? 1.44 * Z / r : 1.44 * Z / (2 * R) * (3 - (r * r) / (R * R)));
  const vP = (r) => vN(r) + vC(r);
  let BTOP = 0, RTOP = R; for (let r = R; r < 20; r += 0.01) { const v = vP(r); if (v > BTOP) { BTOP = v; RTOP = r; } }
  function tunnel(E) {
    if (E >= BTOP) return 1; let ri = RTOP, ro = RTOP; while (ri > 0.1 && vP(ri) > E) ri -= 0.01; while (ro < 400 && vP(ro) > E) ro += 0.01;
    let s = 0; const n = 400, h = (ro - ri) / n; for (let i = 0; i < n; i++) { const r = ri + (i + 0.5) * h; s += Math.sqrt(Math.max(0, 2 * MU * (vP(r) - E))) * h; }
    return Math.exp(-2 * s / HC);
  }
  const balls = { p: { r: RMAX, dir: -1, t: 0, inT: -9 }, n: { r: RMAX, dir: -1, t: 0, inT: -9 } };

  WT.chapter("neutrons", {
    num: "Basics", title: "Why neutrons?", short: "Why neutrons",
    html: `
<div class="step">
  <p>A proton is pushed back by the nucleus's charge.</p>
  <div class="ctl"><label for="wn-e1">Energy (MeV)</label><input id="wn-e1" type="range" data-bind="E" data-instant min="0.2" max="20" step="0.1" value="6"><output data-show="E" data-fmt="1"></output></div>
</div>
<div class="step">
  <p>A neutron has no charge: any energy gets in.</p>
  <div class="ctl"><label for="wn-e2">Energy (MeV)</label><input id="wn-e2" type="range" data-bind="E" data-instant min="0.2" max="20" step="0.1" value="0.5"><output data-show="E" data-fmt="1"></output></div>
</div>`,
    setup(S) { S.set("E", 6); S.set("focus", 0); },
    steps: [(S) => { S.set("focus", 0); S.set("E", 6); }, (S) => { S.set("focus", 1); S.set("E", 0.5); }],
    frame(g, S, dt) {
      const { W, H, c, ctx } = g, phone = W < 600, fs = phone ? 11 : 13, E = S.E, snap = document.body.classList.contains("shot");
      const lanes = [{ k: "p", name: "proton", col: c.proton, V: vP, y0: H * 0.04, y1: H * 0.44 }, { k: "n", name: "neutron", col: c.neutron, V: vN, y0: H * 0.5, y1: H * 0.88 }];
      const x0 = W * (phone ? 0.12 : 0.1), x1 = W * 0.95, X = (r) => x0 + (x1 - x0) * r / RMAX;
      lanes.forEach((L, li) => {
        const VL = -55, VH = 22, Y = (v) => lerp(L.y1, L.y0, (v - VL) / (VH - VL)), on = S.focus === li ? 1 : 0.55;
        // landscape
        const pts = []; for (let i = 0; i <= 300; i++) { const r = RMAX * i / 300; pts.push([X(r), Y(L.V(r))]); }
        g.ground(pts, L.col, (L.y1 - L.y0) * 0.35, 0.2 * on); g.poly(pts, L.col, 2.4, on);
        g.line(x0, Y(0), x1, Y(0), c.line, 1, 0.8, [3, 4]);
        g.label(L.name, x0 + 4, L.y0 + 10, { color: L.col, size: fs + 1, weight: 600, align: "left", alpha: Math.max(on, 0.8) });
        // nucleus at r = 0
        g.nucleus(X(0) + 12, Y(-V0) - 18, phone ? 10 : 14, { N: 40, Z: 16, t: S.time, jiggle: 0.4, alpha: 0.9 });
        if (li === 0) { g.label(`barrier ≈ ${BTOP.toFixed(0)} MeV`, X(RTOP) + 8, Y(BTOP) - 12, { color: c.proton, size: fs - 1, weight: 600, align: "left", bg: true }); }
        // energy line
        g.line(x0, Y(E), x1, Y(E), c.ink, 1, 0.35 * on + 0.1, [6, 5]);
        g.label(`${E.toFixed(1)} MeV`, x1, Y(E) - 10, { color: c.ink, size: fs - 1, align: "right" });
        // the rolling ball
        const b = balls[L.k], Vh = L.V, rTurn = (() => { if (E >= (L.k === "p" ? BTOP : 0) || L.k === "n") return 0; let r = RMAX; while (r > RTOP && Vh(r) < E) r -= 0.02; return r; })();
        if (snap) { b.r = L.k === "p" ? Math.max(rTurn + 2, 16) : R * 0.6; b.inT = L.k === "n" ? S.time : -9; }
        else if (S.time - b.inT > 1.2) {
          const v = 5 + 5 * Math.sqrt(Math.max(0.1, E - Vh(b.r)));
          b.r += b.dir * v * dt;
          if (b.dir < 0 && rTurn > 0 && b.r <= rTurn) { b.r = rTurn; b.dir = 1; }
          if (b.dir < 0 && b.r <= R * 0.6) { b.inT = S.time; b.r = R * 0.6; }
          if (b.r > RMAX + 1) { b.r = RMAX; b.dir = -1; }
        } else if (S.time - b.inT > 1.15) { b.r = RMAX; b.dir = -1; }
        const inside = S.time - b.inT < 1.2;
        if (inside) { const a = S.time - b.inT; g.glow(X(0) + 12, Y(-V0) - 18, 30 + 40 * a, c.warm, 0.6 * (1 - a / 1.2)); }
        else { g.glow(X(b.r), Y(E) - 8, 14, L.col, 0.4); g.ball(X(b.r), Y(E) - 8, 7, L.col); }
        // verdict
        const vy = L.y1 - 6;
        if (L.k === "p") {
          const P = tunnel(E), lg = Math.log10(Math.max(P, 1e-300));
          g.label(E >= BTOP ? "over the barrier: it gets in" : P > 0.01 ? `mostly turned back · tunnels through ${(100 * P).toFixed(0)} %` : `turned back · tunnels through about 1 in 10^${Math.round(-lg)}`.replace(/10\^(\d+)/, (m, d) => "10" + [...d].map((x) => "⁰¹²³⁴⁵⁶⁷⁸⁹"[x]).join("")), W * 0.5 + (phone ? 0 : 60), vy, { color: c.ink, size: fs + 1, weight: 600, serif: true, bg: true });
        } else g.label("no barrier: it gets in", W * 0.5 + (phone ? 0 : 60), vy, { color: c.ink, size: fs + 1, weight: 600, serif: true, bg: true });
      });
      g.label("distance from the centre of lead-208 (fm) →", x1, H * 0.95, { color: c.soft, size: fs - 1, align: "right" });
      [0, 10, 20, 30].forEach((r) => g.label(String(r), X(r), H * 0.905, { color: c.faint, size: fs - 2 }));
    },
  });
})();
