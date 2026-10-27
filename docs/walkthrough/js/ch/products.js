/* After the split. Scene "yield": the fission-product mass yield of thermal U-235 drawn as two Gaussian humps (peaks at
 * A = 95 and 139, peak yield 6.5 %, width 6; illustrative shape, the measured curve has fine structure) on a log scale;
 * tap a bar to see the fragment pair (A and 234 - A: about 2.4 neutrons leave; charge split Z ~ 92 A / 236).
 * Scene "heat": decay heat after shutdown, Way-Wigner approximation P/P0 = 0.0622 [t^-0.2 - (t + T)^-0.2], t and T in
 * seconds, T = one year at full power; shown for a 3000 MW (thermal) reactor. */
(function () {
  const { TAU, clamp, lerp, smooth } = WT.util;
  const EL = ["", "H", "He", "Li", "Be", "B", "C", "N", "O", "F", "Ne", "Na", "Mg", "Al", "Si", "P", "S", "Cl", "Ar", "K", "Ca", "Sc", "Ti", "V", "Cr", "Mn", "Fe", "Co", "Ni", "Cu", "Zn", "Ga", "Ge", "As", "Se", "Br", "Kr", "Rb", "Sr", "Y", "Zr", "Nb", "Mo", "Tc", "Ru", "Rh", "Pd", "Ag", "Cd", "In", "Sn", "Sb", "Te", "I", "Xe", "Cs", "Ba", "La", "Ce", "Pr", "Nd", "Pm", "Sm", "Eu", "Gd"];
  const yld = (a) => 6.5 * (Math.exp(-((a - 95) ** 2) / 72) + Math.exp(-((a - 139) ** 2) / 72));   // % per fission
  const ALO = 70, AHI = 164, TOP = 3.156e7, P0 = 3000;
  const ww = (t) => 0.0622 * (Math.pow(t, -0.2) - Math.pow(t + TOP, -0.2));
  const nm = (a) => { const z = Math.round(92 * a / 236); return `${EL[z] || "?"}-${a}`; };
  const fmtT = (t) => (t < 60 ? `${t.toFixed(0)} s` : t < 3600 ? `${(t / 60).toFixed(0)} min` : t < 86400 ? `${(t / 3600).toFixed(t < 36000 ? 1 : 0)} h` : t < 3.156e7 ? `${(t / 86400).toFixed(0)} days` : `${(t / 3.156e7).toFixed(1)} years`);
  let lay = null, bound = false;

  WT.chapter("products", {
    num: "Fission", title: "After the split", short: "Fission products",
    html: `
<div class="step">
  <p>The pieces are unequal: one light, one heavy. Tap a bar.</p>
  <div class="ctl"><label for="pr-a">Light fragment A</label><input id="pr-a" type="range" data-bind="pick" data-instant min="${ALO}" max="117" step="1" value="95"><output data-show="pick" data-fmt="0"></output></div>
</div>
<div class="step">
  <p>Their decays keep heating the fuel after shutdown.</p>
  <div class="ctl"><label for="pr-t">Time after shutdown</label><input id="pr-t" type="range" data-bind="lgt" data-instant min="0" max="8.5" step="0.01" value="0"></div>
</div>`,
    setup(S) { S.set("mode", "yield"); S.set("pick", 95); S.set("lgt", 0); S.tShow = 1; },
    steps: [(S) => S.set("mode", "yield"), (S) => S.set("mode", "heat")],
    frame(g, S) {
      const { W, H, c, ctx } = g, phone = W < 600, fs = phone ? 11 : 13;
      if (!bound) { bound = true; const cv = ctx.canvas; cv.addEventListener("pointerdown", (e) => { if (S.mode !== "yield" || !lay) return; const rc = cv.getBoundingClientRect(), x = e.clientX - rc.left, y = e.clientY - rc.top; if (y < lay.y0 - 20 || y > lay.y1 + 20) return; let a = Math.round(ALO + (x - lay.x0) / lay.bw - 0.5); a = clamp(a, ALO, AHI); if (a > 117) a = 234 - a; S.set("pick", clamp(a, ALO, 117)); const inp = document.getElementById("pr-a"); if (inp) inp.value = S.pick; }); }
      if (S.mode === "yield") {
        const x0 = W * (phone ? 0.12 : 0.09), x1 = W * 0.96, y0 = H * 0.08, y1 = H * 0.62, n = AHI - ALO + 1, bw = (x1 - x0) / n, L0 = -3, L1 = 1.1;
        const Y = (v) => lerp(y1, y0, (Math.log10(Math.max(v, 10 ** L0)) - L0) / (L1 - L0)); lay = { x0, x1, y0, y1, bw };
        const aL = Math.round(S.pick), aH = 234 - aL;
        for (let e = L0; e <= 1; e++) { g.line(x0, Y(10 ** e), x1, Y(10 ** e), c.line, 1, 0.6, [2, 5]); g.label(e >= 0 ? `${10 ** e} %` : `${10 ** e} %`, x0 - 6, Y(10 ** e), { color: c.faint, size: fs - 2, align: "right" }); }
        for (let a = ALO; a <= AHI; a++) {
          const x = x0 + (a - ALO) * bw, v = yld(a), sel = a === aL || a === aH, col = a < 117 ? c.cool : c.warm;
          ctx.save(); const gr = ctx.createLinearGradient(0, Y(v), 0, y1); gr.addColorStop(0, g.rgba(col, sel ? 1 : 0.75)); gr.addColorStop(1, g.rgba(col, 0.12)); ctx.fillStyle = gr; ctx.fillRect(x + bw * 0.12, Y(v), bw * 0.76, y1 - Y(v)); ctx.restore();
          if (sel) g.glow(x + bw / 2, Y(v), 16, col, 0.6);
        }
        [80, 100, 120, 140, 160].forEach((a) => g.label(String(a), x0 + (a - ALO + 0.5) * bw, y1 + 12, { color: c.faint, size: fs - 2 }));
        g.label("fragment mass number A →", x1, y1 + 28, { color: c.soft, size: fs - 1, align: "right" });
        g.label(phone ? "yield per fission" : "yield per fission (log scale)", x0, y0 - 12 < 8 ? 10 : y0 - 12, { color: c.soft, size: fs - 1, align: "left" });
        // the pair
        const py = H * 0.8, rL = 10 + Math.cbrt(aL) * (phone ? 3 : 4), rH = 10 + Math.cbrt(aH) * (phone ? 3 : 4);
        g.nucleus(W * 0.3, py, rL, { N: Math.round(aL / 3), Z: Math.round(aL / 7.5), t: S.time, jiggle: 0.4, seed: aL, halo: c.cool, haloAlpha: 0.25 });
        g.nucleus(W * 0.7, py, rH, { N: Math.round(aH / 3), Z: Math.round(aH / 7.5), t: S.time, jiggle: 0.4, seed: aH, halo: c.warm, haloAlpha: 0.25 });
        g.label(`${nm(aL)} · ${yld(aL).toFixed(yld(aL) < 0.1 ? 3 : 1)} %`, W * 0.3, py + rL + 16, { color: c.cool, size: fs + 1, weight: 600 });
        g.label(`${nm(aH)} · ${yld(aH).toFixed(yld(aH) < 0.1 ? 3 : 1)} %`, W * 0.7, py + rH + 16, { color: c.warm, size: fs + 1, weight: 600 });
        g.label("+ about 2.4 neutrons", W * 0.5, py, { color: c.neutron, size: fs - 1 });
      } else {
        const t = Math.pow(10, S.lgt), f = ww(t); S.tShow = t < 60 ? t : t < 3600 ? t / 60 : t < 86400 ? t / 3600 : t / 86400;
        const x0 = W * (phone ? 0.14 : 0.1), x1 = W * 0.95, y0 = H * 0.34, y1 = H * 0.8, L0 = -4, L1 = -1, X = (tt) => x0 + (x1 - x0) * Math.log10(tt) / 8.5, Y = (v) => lerp(y1, y0, (Math.log10(v) - L0) / (L1 - L0));
        // the glow: heat still coming out
        const hx = W * 0.5, hy = H * 0.15, lv = clamp((Math.log10(f) + 4) / 3, 0, 1);
        g.glow(hx, hy, 40 + 90 * lv, c.warm, 0.25 + 0.55 * lv); g.glow(hx, hy, 20 + 30 * lv, c.photon, 0.4 * lv);
        g.label(`${(100 * f).toFixed(f < 0.01 ? 2 : 1)} % of full power`, hx, hy - 10, { color: c.ink, size: fs + 8, weight: 600, serif: true });
        g.label(`≈ ${(P0 * f).toFixed(P0 * f < 10 ? 1 : 0)} MW in a ${P0} MW reactor · ${fmtT(t)} after shutdown`, hx, hy + 18, { color: c.soft, size: fs });
        for (let e = L0; e <= L1; e++) { g.line(x0, Y(10 ** e), x1, Y(10 ** e), c.line, 1, 0.6, [2, 5]); g.label(["0.01 %", "0.1 %", "1 %", "10 %"][e - L0], x0 - 6, Y(10 ** e), { color: c.faint, size: fs - 2, align: "right" }); }
        const pts = []; for (let i = 0; i <= 200; i++) { const tt = Math.pow(10, 8.5 * i / 200); pts.push([X(tt), Y(ww(tt))]); }
        g.clip(x0, y0 - 4, x1 - x0 + 4, y1 - y0 + 8); g.ground(pts, c.warm, H * 0.1, 0.18); g.poly(pts, c.warm, 2.6, 1); g.ctx.restore();
        g.line(X(t), y0, X(t), y1, c.ink, 1, 0.3); g.glow(X(t), Y(f), 16, c.warm, 0.6); g.ball(X(t), Y(f), 6, c.warm);
        [[1, "1 s"], [60, "1 min"], [3600, "1 h"], [86400, "1 day"], [3.156e7, "1 yr"]].forEach(([tt, s]) => g.label(s, X(tt), y1 + 12, { color: c.faint, size: fs - 2 }));
        g.label("time after shutdown (log) →", x1, y1 + 28, { color: c.soft, size: fs - 1, align: "right" });
        g.label("Way–Wigner approximation, after a year at full power", W * 0.5, H * 0.94, { color: c.soft, size: fs - 1 });
      }
      g.label("illustration", W - 6, H - 10, { color: c.faint, size: 10, align: "right" });
    },
  });
})();
