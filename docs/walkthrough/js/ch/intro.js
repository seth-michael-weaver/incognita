/* Hero: a neutron drifts in, is absorbed, the nucleus glows, and one of the possible outcomes flies out. Loops. */
(function () {
  const { TAU, clamp, smooth, rng } = WT.util;
  const OUT = [
    { k: "neutron", label: "a neutron comes back out", col: "neutron" },
    { k: "photon", label: "a gamma ray: a burst of light", col: "photon" },
    { k: "proton", label: "a proton escapes", col: "proton" },
    { k: "neutron2", label: "two neutrons come out", col: "neutron" },
    { k: "alpha", label: "an alpha particle: 2 protons + 2 neutrons", col: "alpha" },
  ];
  WT.chapter("intro", {
    setup(S) { S.set("cycle", 0); },
    frame(g, S) {
      const { W, H, c } = g;
      const cx = W * 0.55, cy = H * 0.5, R = Math.min(W, H) * 0.2;
      const P = 5.2, t = S.time % P, n = Math.floor(S.time / P), out = OUT[n % OUT.length];
      const r = rng(n * 31 + 7), ang = -0.9 + r() * 1.8 + (r() < 0.5 ? Math.PI : 0);
      // phase 1: approach (0–1.6 s), phase 2: glow (1.6–2.6), phase 3: emission (2.6–4.6)
      const absorb = smooth(1.45, 1.75, t), heat = smooth(1.5, 2.2, t) * (1 - smooth(3.6, 4.8, t));
      g.nucleus(cx, cy, R, { N: 56, Z: 26, t: S.time, heat: 1 + heat * 3, jiggle: 0.7, halo: c.warm, haloAlpha: 0.05 + heat * 0.45 });
      if (t < 1.75) {
        const x = cx - R - 40 - (1 - smooth(0, 1.6, t)) * W * 0.5, a = 1 - absorb;
        for (let i = 1; i < 10; i++) g.dot(x - i * 9, cy, 6 - i * 0.5, c.neutron, a * (0.25 - i * 0.02));
        g.ball(x, cy, 7, c.neutron, a);
      }
      if (t > 2.6 && t < 4.8) {
        const show = smooth(2.6, 2.85, t);
        const u = smooth(2.6, 4.6, t), d = R + 20 + u * Math.max(W, H) * 0.45, fade = 1 - smooth(4.2, 4.8, t);
        const px = cx + Math.cos(ang) * d, py = cy + Math.sin(ang) * d;
        if (out.k === "photon") g.photon(px, py, ang, 34, fade);
        else if (out.k === "alpha") { for (let i = 0; i < 4; i++) g.ball(px + (i % 2) * 8 - 4, py + (i > 1 ? 8 : 0) - 4, 6, i < 2 ? c.proton : c.neutron, fade); }
        else if (out.k === "neutron2") { g.ball(px, py, 7, c.neutron, fade); const a2 = ang + 2.2; g.ball(cx + Math.cos(a2) * d * 0.9, cy + Math.sin(a2) * d * 0.9, 7, c.neutron, fade); }
        else g.ball(px, py, 7, c[out.col], fade);
        g.label(out.label, cx, cy + R + 44, { color: c[out.col], size: 16, serif: true, italic: true, alpha: fade * show });
      }
      if (t > 1.6 && t < 2.55) g.label("absorbed: its energy spreads through the whole nucleus", cx, cy + R + 44, { color: c.warm, size: 15, serif: true, italic: true, alpha: smooth(1.6, 1.9, t) * (1 - smooth(2.3, 2.55, t)) });
    },
  });
})();
