/* What fission throws out (thermal-neutron fission of U-235). Each event: two fragments and nu prompt neutrons, nu drawn from
 * the measured multiplicity distribution P(nu) = 0.032, 0.172, 0.336, 0.304, 0.127, 0.027, 0.003, 0.0002 (nu = 0..7, mean
 * 2.41); energies from the Watt spectrum f(E) ~ exp(-E/a) sinh(sqrt(b E)), a = 0.988 MeV, b = 2.249 /MeV (mean 2.03 MeV),
 * sampled as in OpenMC (a Maxwellian, then shifted); delayed neutrons 0.0158 per fission (0.65 % of all), their delays drawn from the
 * six Keepin groups (half-lives 55.7, 22.7, 6.22, 2.30, 0.610, 0.230 s; abundances 0.033, 0.219, 0.196, 0.395, 0.115, 0.042). */
(function () {
  const { TAU, clamp, lerp, smooth, rng } = WT.util;
  const PNU = [0.0317, 0.172, 0.3363, 0.3038, 0.1268, 0.0266, 0.0026, 0.0002], NUD = 0.0158, WA = 0.988, WB = 2.249;
  const GRP = [[55.72, 0.033], [22.72, 0.219], [6.22, 0.196], [2.3, 0.395], [0.61, 0.115], [0.23, 0.042]];
  const r = rng(71);
  const nuMean = PNU.reduce((s, p, i) => s + p * i, 0);
  const watt = (E) => Math.exp(-E / WA) * Math.sinh(Math.sqrt(WB * E));
  let wNorm = 0; for (let i = 0; i < 4000; i++) { const e = (i + 0.5) * 0.005; wNorm += watt(e) * 0.005; }
  // OpenMC watt_spectrum: a Maxwellian w (temperature a), then E = w + a^2 b / 4 + (2u - 1) sqrt(a^2 b w)
  function sampleWatt() { const c = Math.cos(Math.PI * r() / 2), w = -WA * (Math.log(1 - r()) + Math.log(1 - r()) * c * c); return w + WA * WA * WB / 4 + (2 * r() - 1) * Math.sqrt(WA * WA * WB * w); }
  function sampleNu() { let u = r(), k = 0; while (k < 7 && u > PNU[k]) { u -= PNU[k]; k++; } return k; }
  function sampleDelay() { let u = r(), k = 0; while (k < 5 && u > GRP[k][1]) { u -= GRP[k][1]; k++; } return -Math.log(1 - r()) * GRP[k][0] / Math.LN2; }
  const ST = { n: 0, nuH: new Array(8).fill(0), eH: new Array(30).fill(0), nP: 0, sumE: 0, del: [], ev: [] };
  function fission(S, show) {
    const nu = sampleNu(), es = []; for (let i = 0; i < nu; i++) { const e = sampleWatt(); es.push(e); ST.sumE += e; if (e < 10) ST.eH[Math.floor(e / (10 / 30))]++; }
    ST.n++; ST.nuH[nu]++; ST.nP += nu;
    if (r() < NUD) ST.del.push({ t: sampleDelay(), born: S.time });
    if (show) ST.ev.push({ t0: S.time, es, ang: es.map(() => r() * TAU), fa: r() * TAU });
  }
  function batch(S, n) { for (let i = 0; i < n; i++) fission(S, false); }

  WT.chapter("fisout", {
    num: "Chapter 13", title: "What fission throws out", short: "Fission neutrons",
    html: `
<div class="step">
  <p>Each fission frees two or three neutrons: 2.4 on average. At the top, one fission at a time: the uranium nucleus tears into two fragments and the blue balls fly off. These are the <b>prompt</b> neutrons, out in far less than a millionth of a second.</p>
  <p>The left chart counts how many fissions freed 0, 1, 2, 3 … neutrons. The bars are the fissions you fired; the thin line on each bar is the measured share. Fire more and the bars settle onto the lines.</p>
  <div class="btns"><button class="btn" data-act="f100">100 fissions</button><button class="btn ghost" data-act="f1000">1000 fissions</button></div>
</div>
<div class="step">
  <p>They are born fast: about 2 MeV on average, some 80 million times the energy of a slow neutron in a reactor at room temperature. The right chart sorts the prompt neutrons by energy. The line is the measured shape (the Watt spectrum): a hump near 1 MeV and a long tail out to 10 MeV.</p>
  <p>Such fast neutrons rarely cause the next fission in uranium-235, so a reactor first slows them down, as a later chapter shows.</p>
  <div class="btns"><button class="btn" data-act="f100">100 fissions</button><button class="btn ghost" data-act="f1000">1000 fissions</button></div>
</div>
<div class="step">
  <p>A few come seconds later: 0.65 % of all the neutrons. Some fragments are so neutron-rich that, when they later decay, the new nucleus cannot hold one of its neutrons and lets it go. That waits for the decay, often seconds.</p>
  <p>The bottom line is a clock after the fission, from 0.01 s to 100 s; each tick is ten times later than the one before. The ball on the left is all the prompt neutrons, out at once. Each small dot is one delayed neutron: it rides along the line while its wait runs, on a clock sped up 20 times, and settles where it finally came out. These few late neutrons are what makes a reactor controllable: they slow the chain's response from thousandths of a second to seconds.</p>
  <div class="btns"><button class="btn" data-act="f1000">1000 fissions</button><button class="btn ghost" data-act="clear">Clear</button></div>
</div>`,
    setup(S) {
      S.on("f100", () => batch(S, 100)); S.on("f1000", () => batch(S, 1000));
      S.on("clear", () => { ST.n = 0; ST.nuH.fill(0); ST.eH.fill(0); ST.nP = 0; ST.sumE = 0; ST.del.length = 0; });
      S.ft = 0;
    },
    steps: [() => {}, () => {}, () => {}],
    frame(g, S, dt) {
      const { W, H, c, ctx } = g, phone = W < 600, fs = phone ? 11 : 13, st = Math.max(0, S.step), snap = document.body.classList.contains("shot");
      if (snap && ST.n < 3000) { batch(S, 3000); ST.del.forEach((d) => (d.born = S.time - 400)); fission(S, true); ST.ev[ST.ev.length - 1].t0 = S.time - 0.45; }
      S.ft += dt; if (S.ft > 1.3) { S.ft = 0; fission(S, true); }
      // ---------- the event ----------
      const cx = W * 0.5, cy = H * 0.17, Rn = phone ? 13 : 17;
      for (let i = ST.ev.length - 1; i >= 0; i--) {
        const e = ST.ev[i], a = S.time - e.t0; if (a > 1.3) { ST.ev.splice(i, 1); continue; }
        if (a < 0.18) { g.nucleus(cx, cy, Rn, { N: 60, Z: 24, t: S.time, beta: a * 3, heat: 2, jiggle: 0.6, halo: c.warm, haloAlpha: 0.3 }); continue; }
        const f = a - 0.18, d = 30 + f * 120, al = 1 - smooth(0.8, 1.12, f);
        g.glow(cx, cy, 40 + 60 * f, "#ffffff", 0.5 * Math.max(0, 1 - f / 0.4));
        g.nucleus(cx + Math.cos(e.fa) * d * 0.7, cy + Math.sin(e.fa) * d * 0.35, Rn * 0.75, { N: 28, Z: 11, t: S.time, jiggle: 0.5, alpha: al, seed: 3 });
        g.nucleus(cx - Math.cos(e.fa) * d * 0.55, cy - Math.sin(e.fa) * d * 0.3, Rn * 0.85, { N: 34, Z: 13, t: S.time, jiggle: 0.5, alpha: al, seed: 5 });
        e.es.forEach((en, k) => { const dd = 20 + f * (90 + 70 * Math.sqrt(en)), x = cx + Math.cos(e.ang[k]) * dd * 1.4, y = cy + Math.sin(e.ang[k]) * dd * 0.6; g.line(x - Math.cos(e.ang[k]) * 12, y - Math.sin(e.ang[k]) * 5, x, y, c.neutron, 2, 0.3 * al); g.ball(x, y, 4, c.neutron, al); });
      }
      if (!ST.ev.length) g.nucleus(cx, cy, Rn, { N: 60, Z: 24, t: S.time, jiggle: 0.4 });
      if (!phone) g.label("n + U-235 → two fragments + neutrons", cx, cy + Rn + 62, { color: c.soft, size: fs - 1 });
      // ---------- multiplicity histogram ----------
      const hy1 = H * (phone ? 0.6 : 0.62), hy0 = H * (phone ? 0.38 : 0.38), focus = (i) => (st === i ? 1 : 0.4);
      { const x0 = W * 0.05, x1 = W * (phone ? 0.46 : 0.45), bw = (x1 - x0) / 8, mx = Math.max(1, ...ST.nuH), al = focus(0);
        for (let v = 0; v < 8; v++) { const h = (hy1 - hy0) * ST.nuH[v] / mx, x = x0 + v * bw; ctx.save(); ctx.globalAlpha = al; const gr = ctx.createLinearGradient(0, hy1 - h, 0, hy1); gr.addColorStop(0, c.neutron); gr.addColorStop(1, g.rgba(c.neutron, 0.25)); ctx.fillStyle = gr; ctx.fillRect(x + bw * 0.15, hy1 - h, bw * 0.7, h); ctx.restore();
          if (ST.n) g.line(x + bw * 0.08, hy1 - (hy1 - hy0) * PNU[v] * ST.n / mx, x + bw * 0.92, hy1 - (hy1 - hy0) * PNU[v] * ST.n / mx, c.ink, 1.5, 0.6 * al);
          g.label(String(v), x + bw / 2, hy1 + 12, { color: c.faint, size: fs - 2, alpha: Math.max(al, 0.7) }); }
        g.label(phone ? "neutrons per fission" : "prompt neutrons per fission", (x0 + x1) / 2, hy1 + 28, { color: c.soft, size: fs - 1 });
        g.label(phone ? "line: measured" : "lines: measured shares", x0, hy0 - 6, { color: c.soft, size: fs - 2, align: "left", alpha: al });
        g.label(`mean ${ST.n ? (ST.nP / ST.n).toFixed(2) : "–"}`, x1, hy0 - 6, { color: c.ink, size: fs, weight: 600, align: "right", alpha: Math.max(al, 0.6) }); }
      // ---------- energy histogram ----------
      { const x0 = W * (phone ? 0.54 : 0.55), x1 = W * 0.95, bw = (x1 - x0) / 30, tot = ST.eH.reduce((a, b) => a + b, 0), mx = Math.max(1, ...ST.eH), al = focus(1);
        for (let b = 0; b < 30; b++) { const h = (hy1 - hy0) * ST.eH[b] / mx; ctx.save(); ctx.globalAlpha = al; ctx.fillStyle = g.rgba(c.warm, 0.75); ctx.fillRect(x0 + b * bw + 0.5, hy1 - h, bw - 1, h); ctx.restore(); }
        if (tot) { const pts = []; for (let i = 0; i <= 100; i++) { const e = 10 * i / 100; pts.push([x0 + (x1 - x0) * e / 10, hy1 - (hy1 - hy0) * tot * (10 / 30) * watt(e) / wNorm / mx]); } g.poly(pts, c.ink, 1.6, 0.75 * al); }
        [0, 5, 10].forEach((e) => g.label(String(e), x0 + (x1 - x0) * e / 10, hy1 + 12, { color: c.faint, size: fs - 2 }));
        g.label(phone ? "energy (MeV)" : "prompt-neutron energy (MeV)", (x0 + x1) / 2, hy1 + 28, { color: c.soft, size: fs - 1 });
        g.label(`mean ${ST.nP ? (ST.sumE / ST.nP).toFixed(2) : "–"} MeV`, x1, hy0 - 6, { color: c.ink, size: fs, weight: 600, align: "right", alpha: Math.max(al, 0.6) });
        g.label(phone ? "line: measured" : "line: measured shape", x1, hy0 + 12, { color: c.soft, size: fs - 2, align: "right", alpha: al }); }
      // ---------- timeline: when the neutrons come ----------
      const ty = H * (phone ? 0.8 : 0.82), tx0 = W * 0.16, tx1 = W * 0.95, L0 = -2, L1 = 2.5, TX = (t) => tx0 + (tx1 - tx0) * (Math.log10(clamp(t, 10 ** L0, 10 ** L1)) - L0) / (L1 - L0), al = focus(2);
      g.line(tx0, ty, tx1, ty, c.line, 2);
      [[0.01, "0.01 s"], [0.1, "0.1"], [1, "1"], [10, "10"], [100, "100 s"]].forEach(([t, s]) => { g.line(TX(t), ty - 4, TX(t), ty + 4, c.faint, 1); g.label(s, TX(t), ty + 14, { color: c.faint, size: fs - 2 }); });
      const pxp = W * 0.07; g.glow(pxp, ty, 18 + Math.min(14, Math.log10(1 + ST.nP) * 4), c.neutron, 0.5); g.ball(pxp, ty, 6, c.neutron);
      g.label("prompt", pxp, ty - 16, { color: c.neutron, size: fs - 1, weight: 600 }); g.label(String(ST.nP), pxp, ty + 16, { color: c.ink, size: fs - 1, weight: 600 });
      // delayed neutrons: each rides the clock (sped up SPD times) until its wait is over, then settles at its delay
      const SPD = 20, cnt = {};
      for (const d of ST.del) {
        const el = (S.time - d.born) * SPD;
        if (el < d.t) { const x = TX(Math.max(el, 0.01)); g.ring(x, ty, 4, c.photon, 1.5, al * 0.6 + 0.3); continue; }
        const x = TX(d.t), k = Math.round(x / 7); cnt[k] = (cnt[k] || 0) + 1; const yy = ty - 8 - (cnt[k] - 1) * 7, f = smooth(0, 0.25, (el - d.t) / SPD);
        if (yy > ty - H * 0.1) { g.dot(x, lerp(ty, yy, f), 3, c.photon, al * 0.6 + 0.4); if (f < 1) g.glow(x, ty, 12, c.photon, 0.5 * (1 - f)); }
      }
      g.label(`time after fission · clock sped up ${SPD}×`, tx0, ty + 32, { color: c.soft, size: fs - 2, align: "left", alpha: Math.max(al, 0.7) });
      g.label(`delayed ${ST.del.length} of ${ST.nP + ST.del.length} (${ST.nP ? (100 * ST.del.length / (ST.nP + ST.del.length)).toFixed(2) : "–"} %)`, tx1, phone ? ty + 48 : ty - H * 0.1 - 8, { color: c.photon, size: fs, weight: 600, align: "right", alpha: Math.max(al, 0.7) });
      g.label(`${ST.n} fissions`, phone ? W * 0.05 : W * 0.5, H * 0.95, { color: c.ink, size: fs + 1, weight: 600, serif: true, align: phone ? "left" : "center" });
    },
  });
})();
