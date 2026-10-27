/* What is a cross section? A slab of nuclei seen face-on; each nucleus carries a disc whose area is its cross section sigma.
 * Particles rain onto the slab at random spots: those landing on a disc react (counted), the rest pass through, so the
 * reacting share is the area the discs cover, and the transmission is the rest. A square of 1 barn (1e-24 cm^2) sets the
 * scale. sigma(E) is illustrative: 5 b of scattering, 50 b of capture at 0.0253 eV falling as 1/v (1/sqrt(E)), and one
 * single-level resonance at 7 eV (peak 400 b, width 0.4 eV drawn wide). */
(function () {
  const { TAU, clamp, lerp, smooth, rng } = WT.util;
  const log10 = (x) => Math.log(x) / Math.LN10;
  const sig = (E) => { const x = 2 * (E - 7) / 0.4; return 5 + 50 * Math.sqrt(0.0253 / E) + 400 / (1 + x * x); };
  const r = rng(3);
  const drops = [], hist = []; let acc = 0;

  WT.chapter("xsec", {
    num: "Basics", title: "What is a cross section?", short: "Cross section",
    html: `
<div class="step">
  <p>Each disc is a nucleus's target area: its cross section.</p>
  <div class="ctl"><label for="xs-e1">Neutron energy (eV)</label><input id="xs-e1" type="range" data-bind="lgE" data-instant min="-2.3" max="2" step="0.01" value="2"><output data-show="Eshow" data-fmt="2"></output></div>
</div>
<div class="step">
  <p>Slower neutrons see bigger targets.</p>
  <div class="ctl"><label for="xs-e2">Neutron energy (eV)</label><input id="xs-e2" type="range" data-bind="lgE" data-instant min="-2.3" max="2" step="0.01" value="-1.6"><output data-show="Eshow" data-fmt="2"></output></div>
</div>
<div class="step">
  <p>At a resonance the target swells.</p>
  <div class="ctl"><label for="xs-e3">Neutron energy (eV)</label><input id="xs-e3" type="range" data-bind="lgE" data-instant min="-2.3" max="2" step="0.005" value="0.845"><output data-show="Eshow" data-fmt="2"></output></div>
</div>`,
    setup(S) { S.set("lgE", 2); S.Eshow = 100; },
    steps: [(S) => { S.set("lgE", 2); hist.length = 0; }, (S) => { S.set("lgE", -1.6); hist.length = 0; }, (S) => { S.set("lgE", log10(7)); hist.length = 0; }],
    frame(g, S, dt) {
      const { W, H, c, ctx } = g, phone = W < 600, fs = phone ? 11 : 13, snap = document.body.classList.contains("shot");
      const E = Math.pow(10, S.lgE), s = sig(E); S.Eshow = E;
      // the slab, face-on
      const sx = W * 0.05, sy = H * 0.05, sw = W * 0.9, sh = H * (phone ? 0.6 : 0.62);
      const nx = phone ? 5 : 7, ny = phone ? 4 : 5, cw = sw / nx, chh = sh / ny, K = Math.min(cw, chh) * 0.085;   // px per sqrt(barn)
      ctx.save(); const sg = ctx.createRadialGradient(sx + sw / 2, sy + sh / 2, 10, sx + sw / 2, sy + sh / 2, sw * 0.6); sg.addColorStop(0, g.rgba(c.soft, 0.1)); sg.addColorStop(1, g.rgba(c.soft, 0.02)); ctx.fillStyle = sg;
      if (ctx.roundRect) { ctx.beginPath(); ctx.roundRect(sx, sy, sw, sh, 18); ctx.fill(); } else ctx.fillRect(sx, sy, sw, sh); ctx.restore();
      const rD = K * Math.sqrt(s / Math.PI), nuc = [], q = rng(9);
      for (let j = 0; j < ny; j++) for (let i = 0; i < nx; i++) nuc.push([sx + cw * (i + 0.5 + (j % 2 ? 0.25 : -0.25) + (q() - 0.5) * 0.2), sy + chh * (j + 0.5 + (q() - 0.5) * 0.2)]);
      for (const [x, y] of nuc) { g.dot(x, y, rD, c.neutron, 0.16); g.ring(x, y, rD, c.neutron, 1.4, 0.75); g.nucleus(x, y, Math.max(3, Math.min(7, K * 0.9)), { N: 14, Z: 6, t: S.time, jiggle: 0.25, seed: Math.round(x + y) }); }
      // rain
      const inside = (x, y) => nuc.some(([a, b]) => (x - a) ** 2 + (y - b) ** 2 < rD * rD);
      const N = snap ? 0 : dt * 26; acc += N;
      while (acc >= 1) { acc--; const x = sx + 8 + (sw - 16) * r(), y = sy + 8 + (sh - 16) * r(); const hit = inside(x, y); drops.push({ x, y, t0: S.time, hit }); hist.push(hit ? 1 : 0); }
      if (snap && !hist.length) for (let i = 0; i < 500; i++) { const x = sx + sw * r(), y = sy + sh * r(); hist.push(inside(x, y) ? 1 : 0); if (i < 30) drops.push({ x, y, t0: S.time - r() * 0.9, hit: inside(x, y) }); }
      while (hist.length > 600) hist.shift();
      for (let i = drops.length - 1; i >= 0; i--) {
        const d = drops[i], a = S.time - d.t0; if (a > 1.1) { drops.splice(i, 1); continue; }
        if (a < 0.35) { const f = a / 0.35; g.ring(d.x, d.y, 14 * (1 - f) + 2, c.ink, 1, 0.4 * f); g.ball(d.x, d.y - 26 * (1 - f), 3.2, c.neutron, f); }
        else if (d.hit) { const f = (a - 0.35) / 0.75; g.glow(d.x, d.y, 8 + 22 * f, c.warm, 0.8 * (1 - f)); }
        else { const f = (a - 0.35) / 0.75; g.dot(d.x, d.y, 2.6 * (1 - f), c.neutron, 0.6 * (1 - f)); }
      }
      // one-barn square (scale)
      const bx = sx + sw - K - 14, by = sy + sh + (phone ? 18 : 22);
      ctx.save(); ctx.fillStyle = g.rgba(c.ink, 0.75); ctx.fillRect(bx, by - K / 2, K, K); ctx.restore();
      g.label(phone ? "1 barn = 10⁻²⁴ cm²" : "this square: 1 barn = 10⁻²⁴ cm²", bx - 8, by, { color: c.soft, size: fs - 1, align: "right" });
      // sigma(E) strip: where we are on the energy axis
      const ex0 = sx + 4, ex1 = phone ? sx + sw * 0.52 : sx + sw * 0.55, eY = sy + sh + (phone ? 52 : 62), eH = H * 0.08, L0 = -2.3, L1 = 2;
      const EX = (e) => ex0 + (ex1 - ex0) * (log10(e) - L0) / (L1 - L0), SY = (v) => eY - eH * clamp(log10(v / 4) / log10(120), 0, 1);
      const pts = []; for (let i = 0; i <= 200; i++) { const e = Math.pow(10, L0 + (L1 - L0) * i / 200); pts.push([EX(e), SY(sig(e))]); }
      g.ground(pts, c.neutron, eH * 0.5, 0.18); g.poly(pts, c.neutron, 1.8, 0.9);
      g.dot(EX(E), SY(s), 5, c.warm); g.line(EX(E), SY(s), EX(E), eY + 4, c.warm, 1, 0.6, [2, 3]);
      [[0.01, "0.01"], [1, "1"], [100, "100 eV"]].forEach(([e, t]) => g.label(t, EX(e), eY + 12, { color: c.faint, size: fs - 2 }));
      g.label("σ", ex0 - 2, eY - eH - 6, { color: c.neutron, size: fs, weight: 600, align: "left" });
      // readouts
      const n = hist.length, h = hist.reduce((a, b) => a + b, 0);
      const ry = H * 0.94;
      g.label(`σ ≈ ${s.toFixed(s < 10 ? 1 : 0)} b · reacted ${n ? Math.round(100 * h / n) : 0} % · transmitted ${n ? 100 - Math.round(100 * h / n) : 100} %`, W * 0.5, ry, { color: c.ink, size: fs + 2, weight: 600, serif: true });
      g.label("illustration", W - 6, H - 10, { color: c.faint, size: 10, align: "right" });
    },
  });
})();
