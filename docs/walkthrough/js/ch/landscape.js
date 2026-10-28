/* The landscape of nuclei: every measured nucleus on the chart (neutrons N across, protons Z up), 2D.
 * Data: js/data/chart3d.js (AME2020 B/A, NUBASE2020 half-lives, INCOGNITA scope tier). Steps:
 *   "chart"  = coloured by half-life (stable dark), one element row picked by a slider;
 *   "valley" = coloured by binding energy per nucleon: a ridge along the stable nuclei, magic numbers marked;
 *   "roll"   = one mass chain (fixed A) highlighted; a ball hops by beta decay from the neutron-rich end to the most tightly bound
 *              member, and an inset draws the chain's binding as a valley profile with the ball rolling down it;
 *   "tiers"  = coloured by what INCOGNITA ships for each nucleus. */
(function () {
  const { clamp, lerp, smooth } = WT.util;
  const D = () => WT.CHART3D || [];
  const MAGIC = [8, 20, 28, 50, 82, 126];
  const EL = ["n","H","He","Li","Be","B","C","N","O","F","Ne","Na","Mg","Al","Si","P","S","Cl","Ar","K","Ca","Sc","Ti","V","Cr","Mn","Fe","Co","Ni","Cu","Zn","Ga","Ge","As","Se","Br","Kr","Rb","Sr","Y","Zr","Nb","Mo","Tc","Ru","Rh","Pd","Ag","Cd","In","Sn","Sb","Te","I","Xe","Cs","Ba","La","Ce","Pr","Nd","Pm","Sm","Eu","Gd","Tb","Dy","Ho","Er","Tm","Yb","Lu","Hf","Ta","W","Re","Os","Ir","Pt","Au","Hg","Tl","Pb","Bi","Po","At","Rn","Fr","Ra","Ac","Th","Pa","U","Np","Pu","Am","Cm","Bk","Cf","Es","Fm","Md","No","Lr","Rf","Db","Sg","Bh","Hs","Mt","Ds","Rg","Cn","Nh","Fl","Mc","Lv","Ts","Og"];
  const name = (z, a) => `${EL[z] || "Z" + z}-${a}`;
  const fmtT = (lt) => lt == null ? "half-life unknown" : lt >= 99 ? "stable" : lt > 7.5 ? `half-life ${(Math.pow(10, lt) / 3.156e7).toPrecision(2)} years`
    : lt > 4.94 ? `half-life ${(Math.pow(10, lt) / 86400).toPrecision(2)} days` : lt > 1.78 ? `half-life ${(Math.pow(10, lt) / 60).toPrecision(2)} minutes`
    : lt > -0.5 ? `half-life ${Math.pow(10, lt).toPrecision(2)} s` : `half-life ${(Math.pow(10, lt) * 1000).toPrecision(2)} ms`;
  function chainOf(A) { return D().filter((d) => d[0] + d[1] === A).sort((a, b) => a[0] - b[0]); }
  // mix two #rrggbb colours (t = 0..1)
  const mix = (a, b, t) => { const p = (s) => [1, 3, 5].map((i) => parseInt(s.slice(i, i + 2), 16)); if (!/^#[0-9a-f]{6}$/i.test(a) || !/^#[0-9a-f]{6}$/i.test(b)) return t < 0.5 ? a : b;
    const x = p(a), y = p(b); return "#" + x.map((v, i) => Math.round(v + (y[i] - v) * t).toString(16).padStart(2, "0")).join(""); };

  WT.chapter("landscape", {
    title: "The landscape of nuclei", short: "Landscape",
    lead: "Every nucleus anyone has ever made and weighed, on one map: about 3,600 of them, and only 252 last forever.",
    html: `
<div class="step">
  <h3>Every nucleus ever measured</h3>
  <p>Each little square is one nucleus: neutrons count across, protons count up. The <b>dark</b> squares are the 252 that never decay. The others fall apart, orange ones in a blink, blue ones only after years. The <em style="font-style:normal;color:var(--proton);font-weight:600">red</em> row is the element you pick with the slider: all its known isotopes.</p>
  <div class="ctl"><label for="ls-z">Look at element (protons Z)</label><input id="ls-z" type="range" data-bind="zSel" data-instant min="1" max="110" step="1" value="26"><output data-show="zSel" data-fmt="0"></output></div>
  <p class="ctl-result" id="ls-z-out" aria-live="polite"></p>
</div>
<div class="step">
  <h3>Binding: the ridge</h3>
  <p>Now each square is coloured by its <b>binding energy per nucleon</b>, how tightly each neutron or proton is held (Chapter 3). The stable nuclei sit along a ridge of strong binding; step away from it, with too many neutrons or too many protons, and the binding drops. The strongest of all is nickel-62. The thin lines mark the <b>magic numbers</b> (8, 20, 28, 50, 82, 126), where nuclei are extra tightly bound.</p>
</div>
<div class="step">
  <h3>Rolling down to stability</h3>
  <p>Nuclei with the same total number of nucleons (the same <b>mass number</b> A) lie on a diagonal line across the map, shown in <em style="font-style:normal;color:var(--proton);font-weight:600">red</em>. Start with too many neutrons, as the fragments of a split uranium nucleus do. In <b>beta decay</b> a neutron turns into a proton, so the nucleus steps one place along its line toward the more tightly bound middle, again and again, until it reaches the ridge and stops. The small graph shows the same chain as a valley the nucleus rolls down. Try A = 137: the chain passes caesium-137, the long-lived product of reactor accidents.</p>
  <div class="ctl"><label for="ls-a">Mass number A</label><input id="ls-a" type="range" data-bind="aSel" data-instant min="8" max="250" step="1" value="137"><output data-show="aSel" data-fmt="0"></output></div>
  <p class="ctl-result" id="ls-a-out" aria-live="polite"></p>
</div>
<div class="step">
  <h3>What INCOGNITA ships</h3>
  <p>The same map, coloured by what our library holds for each nucleus. <em style="font-style:normal;color:var(--fission);font-weight:600">Green</em>: evaluated from its measured resonances. The rest have a model file built by the engine alone: <b>dark</b> for stable or long-lived (tier A), <em style="font-style:normal;color:var(--accent);font-weight:600">blue</em> for more than a day (tier B), <em style="font-style:normal;color:var(--warm);font-weight:600">orange</em> for shorter-lived (tier C). Grey ones are not in the library (mostly the lightest nuclei, and a few the engine cannot run).</p>
</div>`,
    setup(S) { S.set("mode", "chart"); S.set("zSel", 26); S.set("aSel", 137); S.rollT = 0; },
    steps: [
      (S) => { S.set("mode", "chart"); },
      (S) => { S.set("mode", "valley"); },
      (S) => { S.set("mode", "roll"); S.rollT = S.time; },
      (S) => { S.set("mode", "tiers"); },
    ],
    frame(g, S) {
      const { W, H, c, ctx } = g, phone = W < 600, fs = phone ? 11 : 13, data = D();
      if (!data.length) { g.label("loading the chart…", W / 2, H / 2, { color: c.soft, size: fs }); return; }
      if (S.aSel !== S.aShown) { S.aShown = S.aSel; S.rollT = S.time; }
      // map area: N 0..180 across, Z 0..118 up, square cells
      const x0 = W * (phone ? 0.09 : 0.07), x1 = W * 0.97, y0 = H * (phone ? 0.1 : 0.08), y1 = H * (phone ? 0.86 : 0.88);
      const cell = Math.max(1.5, Math.min((x1 - x0) / 180, (y1 - y0) / 120)), X = (n) => x0 + n * cell, Y = (z) => y1 - (z + 1) * cell;
      const zSel = Math.round(S.zSel), aSel = Math.round(S.aSel);
      // colour of each square for this step
      const colOf = (d) => {
        if (S.mode === "tiers") return d[5] === 4 ? c.fission : d[5] === 1 ? c.ink : d[5] === 2 ? c.accent : d[5] === 3 ? c.warm : c.line;
        if (S.mode === "valley" || S.mode === "roll") { const u = clamp((d[2] - 7.0) / 1.8, 0, 1); return u > 0.5 ? mix(c.accent, c.fission, (u - 0.5) * 2) : mix(c.warm, c.accent, u * 2); }
        return d[4] === 99 ? c.ink : d[4] == null ? c.line : mix(c.warm, c.accent, clamp((d[4] + 3) / 13, 0, 1));
      };
      data.forEach((d) => {
        let col = colOf(d);
        if (S.mode === "chart" && d[0] === zSel) col = c.proton;
        if (S.mode === "roll" && d[0] + d[1] === aSel) col = c.proton;
        ctx.globalAlpha = d[3] && S.mode !== "tiers" ? 0.55 : 1; ctx.fillStyle = col; ctx.fillRect(X(d[1]), Y(d[0]), cell * 0.9, cell * 0.9);
      });
      ctx.globalAlpha = 1;
      // axes and magic numbers
      g.label("neutrons N →", x1, y1 + (phone ? 12 : 16), { color: c.soft, size: fs - 1, align: "right" });
      g.label("protons Z ↑", x0, y0 - 8, { color: c.soft, size: fs - 1, align: "left" });
      if (S.mode === "valley" || S.mode === "roll") {
        MAGIC.forEach((m) => {
          g.line(X(m) + cell * 0.45, y1, X(m) + cell * 0.45, Y(Math.min(118, m * 0.9 + 10)), c.faint, 1, 0.5, [3, 4]);
          if (m < 118) g.line(x0, Y(m) + cell * 0.45, X(Math.min(180, m * 1.6 + 10)), Y(m) + cell * 0.45, c.faint, 1, 0.5, [3, 4]);
          if (!phone || m >= 50) g.label(String(m), X(m) + cell * 0.45, y1 + 6, { color: c.faint, size: 10 });
        });
        g.ring(X(34) + cell * 0.45, Y(28) + cell * 0.45, 7, c.fission, 2);
        g.label("nickel-62: most tightly bound", X(34) + 12, Y(28) - 10, { color: c.fission, size: fs, weight: 600, align: "left", bg: true });
      }
      // legend
      const leg = S.mode === "tiers" ? [[c.fission, "measured resonances"], [c.ink, "tier A"], [c.accent, "tier B"], [c.warm, "tier C"], [c.line, "not in library"]]
        : S.mode === "chart" ? [[c.ink, "stable"], [c.accent, "lives years"], [c.warm, "gone in a blink"], [c.proton, `red: ${EL[zSel] || "Z " + zSel} (your pick)`]]
        : S.mode === "roll" ? [[c.fission, "held most tightly"], [c.accent, "middle"], [c.warm, "held least"], [c.proton, `red: the A = ${aSel} chain`]]
        : [[c.fission, "held most tightly"], [c.accent, "middle"], [c.warm, "held least"]];
      // name the red highlight on the map itself
      if (S.mode === "chart") { const row = data.filter((d) => d[0] === zSel); if (row.length) { const last = row[row.length - 1]; g.label(`${EL[zSel] || "Z " + zSel}: all its isotopes`, X(last[1]) + 10, Y(zSel) + cell * 0.45, { color: c.proton, size: fs, weight: 600, align: "left", bg: true }); } }
      if (!phone) leg.forEach(([col, t], i) => { const lx = X(100), ly = Y(28) + i * 18; ctx.fillStyle = col; ctx.fillRect(lx, ly - 5, 10, 10); g.label(t, lx + 16, ly, { color: c.soft, size: 12, align: "left" }); });
      else g.label(leg.map((l) => l[1]).join(" · "), W / 2, H - 8, { color: c.soft, size: 10 });
      // roll step: the ball hops along the chain; an inset draws the chain as a valley
      if (S.mode === "roll") roll(g, S, X, Y, cell, aSel, phone, fs);
      captions(S, aSel);
    },
  });

  function roll(g, S, X, Y, cell, A, phone, fs) {
    const { W, H, c } = g, ch = chainOf(A); if (!ch.length) return;
    let top = 0; ch.forEach((d, i) => { if (d[2] > ch[top][2]) top = i; });
    const start = top > 0 ? 0 : ch.length - 1, dir = start < top ? 1 : -1, hops = Math.abs(top - start);
    const tt = Math.max(0, S.time - (S.rollT || 0)) * 1.4, k = Math.min(hops, Math.floor(tt)), f = smooth(0, 1, tt - k);
    const a = ch[start + dir * k], b = ch[start + dir * Math.min(hops, k + 1)], mv = k < hops ? f : 0;
    const bx = lerp(X(a[1]), X(b[1]), mv) + cell * 0.45, by = lerp(Y(a[0]), Y(b[0]), mv) + cell * 0.45 - Math.sin(Math.PI * mv) * 8;
    g.glow(bx, by, 12, c.warm, 0.5); g.ball(bx, by, phone ? 5 : 6, c.warm);
    g.label(name(a[0], A), bx, by - 14, { color: c.warm, size: fs, weight: 600, bg: true });
    if (tt > hops + 2.5) S.rollT = S.time;
    // inset: binding per nucleon along the chain (Z across), drawn upside down (most bound lowest) so it reads as a valley
    const iw = phone ? W * 0.42 : W * 0.3, ih = phone ? H * 0.2 : H * 0.24, ix = phone ? W * 0.05 : W * 0.06, iy = phone ? H * 0.05 : H * 0.08;
    const zs = ch.map((d) => d[0]), bmin = Math.min(...ch.map((d) => d[2])), bmax = Math.max(...ch.map((d) => d[2]));
    const IX = (z) => ix + iw * (z - zs[0]) / Math.max(1, zs[zs.length - 1] - zs[0]), VY = (bv) => iy + ih * (bv - bmin) / Math.max(1e-6, bmax - bmin);
    g.ctx.save(); g.ctx.fillStyle = g.rgba(c.card, 0.92); g.ctx.strokeStyle = g.rgba(c.line, 0.9); g.ctx.beginPath(); g.ctx.rect(ix - 8, iy - 22, iw + 16, ih + 40); g.ctx.fill(); g.ctx.stroke(); g.ctx.restore();
    g.poly(ch.map((d) => [IX(d[0]), VY(d[2])]), c.proton, 2, 0.9);
    ch.forEach((d) => g.dot(IX(d[0]), VY(d[2]), 2.5, d[4] === 99 ? c.ink : c.proton, 1));
    g.label(phone ? "the chain as a valley" : `A = ${A}: deeper = more tightly bound`, ix, iy - 11, { color: c.soft, size: phone ? 10 : 12, align: "left" });
    g.label("protons Z →", ix + iw, iy + ih + 12, { color: c.faint, size: 10, align: "right" });
    g.ball(IX(lerp(a[0], b[0], mv)), VY(lerp(a[2], b[2], mv)) - 6, 5, c.warm);
  }

  // HTML readouts under the sliders
  function captions(S, A) {
    const data = D();
    if (S.mode === "chart") {
      const z = Math.round(S.zSel);
      if (z !== S.zShown) { S.zShown = z; const row = data.filter((d) => d[0] === z), st = row.filter((d) => d[4] === 99).length, o = document.getElementById("ls-z-out");
        if (o) o.textContent = row.length ? `${EL[z] || "Z = " + z}: ${row.length} isotopes measured, ${st ? st + " stable" : "none stable"} (from ${name(z, z + row[0][1])} to ${name(z, z + row[row.length - 1][1])})` : `Z = ${z}: none measured`; }
    }
    if (S.mode === "roll") {
      const ch = chainOf(A); if (!ch.length) return;
      let top = 0; ch.forEach((d, i) => { if (d[2] > ch[top][2]) top = i; });
      const start = top > 0 ? 0 : ch.length - 1, hops = Math.abs(top - start), key = `${A}`;
      if (key !== S.aKey) { S.aKey = key; const o = document.getElementById("ls-a-out"), s0 = ch[start], t = ch[top];
        if (o) o.textContent = hops ? `A = ${A}: from ${name(s0[0], A)} (${fmtT(s0[4])}), ${hops} beta decay${hops > 1 ? "s" : ""} to ${name(t[0], A)}, the most tightly bound of the chain`
          : `A = ${A}: only one nucleus measured in this chain`; }
    }
  }
})();
