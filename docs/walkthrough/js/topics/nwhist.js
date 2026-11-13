/* Nuclear weapons, a history (1): from the discovery of fission to Trinity, 1938-1945. Historical and explanatory only:
 * no design information, no quantities that describe a device. Scenes (S.mode):
 *   "split" = one neutron splits a heavy nucleus into two fragments and a few neutrons (generic cartoon, as in the
 *             fission chapter). Hahn & Strassmann, Naturwissenschaften 27 (1939) 11 (barium found, December 1938);
 *             Meitner & Frisch, Nature 143 (1939) 239 (the interpretation, "fission"; about 200 MeV per split).
 *   "chain" = a branching cartoon of generations with generic nuclei (the idea, not a calculation): Szilard's 1933 idea
 *             (patent GB 630726, filed 1934); the Einstein-Szilard letter of 2 August 1939; Chicago Pile-1,
 *             2 December 1942 (first controlled chain reaction, Fermi).
 *   "sites" = the three Manhattan Project sites (US DOE, "The Manhattan Project: an interactive history", OSTI):
 *             Oak Ridge (uranium-235 separation), Hanford (plutonium production reactors), Los Alamos (the laboratory);
 *             project led by Gen. Leslie Groves, the laboratory by J. Robert Oppenheimer; ~130,000 people at its peak.
 *   "time"  = a timeline 1938-1945 ending with Trinity, 16 July 1945, 05:29, Jornada del Muerto, New Mexico (DOE).
 * Sources shown on the drawing: R. Rhodes, The Making of the Atomic Bomb (1986); US DOE / OSTI Manhattan Project history. */
(function () {
  const { TAU, clamp, lerp, smooth, rng } = WT.util;
  const SHOT = () => document.body.classList.contains("shot");
  const EVENTS = [ // year (fractional), short label, long label, scene emphasis
    [1938.95, "fission found", "Dec 1938 · fission discovered in Berlin"],
    [1939.6, "Einstein–Szilard letter", "Aug 1939 · the Einstein–Szilard letter"],
    [1942.7, "Manhattan Project", "1942 · the Manhattan Project begins"],
    [1942.92, "first chain reaction", "Dec 1942 · first controlled chain reaction, Chicago"],
    [1945.54, "Trinity", "16 July 1945 · Trinity, New Mexico"],
    [1945.6, "Hiroshima, Nagasaki", "6 and 9 August 1945 · Hiroshima and Nagasaki"],
  ];

  WT.chapter("nwhist", {
    level: 0, num: "Lesson 1", title: "From discovery to Trinity", short: "Discovery to Trinity",
    html: `
<div class="step">
  <h3>Splitting the atom, 1938</h3>
  <p>In December 1938 in Berlin, Otto Hahn and Fritz Strassmann found barium, a much lighter element, in uranium that had been hit by neutrons. Lise Meitner, who had fled Nazi Germany that summer, and her nephew Otto Frisch explained it within weeks: the uranium nucleus had split in two. Frisch called it <b>fission</b>.</p>
</div>
<div class="step">
  <h3>The idea of a chain reaction</h3>
  <p>Each split also frees a few neutrons, which can split further nuclei. Leo Szilard had imagined such a <b>chain reaction</b> in 1933. In August 1939 he drafted a letter, signed by Albert Einstein, warning President Roosevelt that Germany might use it to build a bomb. In December 1942 Enrico Fermi's team ran the first controlled chain reaction, a pile of uranium and graphite in Chicago.</p>
</div>
<div class="step">
  <h3>The Manhattan Project</h3>
  <p>From 1942 the United States, with Britain and Canada, built a secret industry employing some 130,000 people at its peak. Oak Ridge in Tennessee separated the rare uranium-235 from natural uranium, Hanford in Washington ran reactors that made plutonium, and the laboratory at Los Alamos in New Mexico, led by J. Robert Oppenheimer, worked on the weapons.</p>
</div>
<div class="step">
  <h3>Trinity, 16 July 1945</h3>
  <p>The first nuclear explosion lit the New Mexico desert before dawn. Three weeks later the United States used two atomic bombs on Japan, on Hiroshima and Nagasaki. Germany had surrendered in May; its own wartime project had never come close to a weapon.</p>
</div>`,
    setup(S) { S.set("mode", "split"); S.set("tl", 1938.5); },
    steps: [
      (S) => S.set("mode", "split"),
      (S) => S.set("mode", "chain"),
      (S) => S.set("mode", "sites"),
      (S) => { S.set("mode", "time"); S.to("tl", 1945.65, SHOT()); },
    ],
    frame(g, S, dt) {
      const { W, H, c } = g, phone = W < 600, fs = phone ? 11 : 13, t = S.time, sh = SHOT();
      const foot = (s) => g.label(s, W - 6, H - 8, { color: c.faint, size: 10, align: "right" });
      if (S.mode === "split") {
        // a neutron comes in, the nucleus wobbles, stretches and splits; fragments and neutrons fly apart (loop 4 s)
        const u = sh ? 0.6 : (t % 4) / 4, cx = W / 2, cy = H * 0.46, R = Math.min(W, H) * (phone ? 0.13 : 0.12);
        const inT = smooth(0, 0.3, u), split = smooth(0.42, 0.7, u), wob = u > 0.3 && u < 0.45 ? Math.sin((u - 0.3) * 80) * 0.08 : 0;
        if (u < 0.3) { const nx = lerp(W * 0.06, cx - R * 1.05, inT); g.glow(nx, cy, 16, c.neutron, 0.5); g.ball(nx, cy, phone ? 6 : 7, c.neutron); }
        if (split < 0.02) g.nucleus(cx, cy, R, { N: 90, Z: 36, seed: 11, t, beta: 0.12 + wob + smooth(0.36, 0.42, u) * 0.35, halo: c.warm, haloAlpha: 0.2 + 0.25 * smooth(0.3, 0.42, u) });
        else {
          const d = R * (0.6 + 2.4 * split), a = -0.25;
          g.glow(cx, cy, R * (1.4 + 2.5 * split), c.photon, 0.45 * (1 - split * 0.7));
          g.nucleus(cx - Math.cos(a) * d, cy - Math.sin(a) * d, R * 0.78, { N: 52, Z: 21, seed: 3, t, halo: c.warm, haloAlpha: 0.25 });
          g.nucleus(cx + Math.cos(a) * d, cy + Math.sin(a) * d, R * 0.7, { N: 38, Z: 15, seed: 5, t, halo: c.warm, haloAlpha: 0.25 });
          [1.9, -1.2, 0.5].forEach((b) => { const r = R * (0.4 + 3.2 * split); g.glow(cx + Math.cos(b) * r, cy + Math.sin(b) * r, 14, c.neutron, 0.5); g.ball(cx + Math.cos(b) * r, cy + Math.sin(b) * r, phone ? 5.5 : 6.5, c.neutron); });
          if (split > 0.6) { g.label("two lighter nuclei", cx, cy + R * 2.6, { color: c.warm, size: fs, weight: 600, alpha: smooth(0.6, 0.7, u) }); g.label("and a few free neutrons", cx, cy + R * 2.6 + fs + 6, { color: c.neutron, size: fs, alpha: smooth(0.6, 0.7, u) }); }
        }
        if (split < 0.02) g.label("uranium", cx, cy + R * 1.5, { color: c.soft, size: fs });
        if (u < 0.3) g.label("neutron", lerp(W * 0.06, cx - R * 1.05, inT), cy - 20, { color: c.neutron, size: fs - 1 });
        g.label(phone ? "fission: one nucleus splits in two" : "fission: a heavy nucleus splits into two lighter ones", W / 2, H * 0.1, { color: c.ink, size: fs + 2, weight: 600, serif: true });
        foot("after Meitner & Frisch 1939 · illustration");
        return;
      }
      if (S.mode === "chain") {
        // a branching tree, two new splits per split, drawn as an idea (each generation fades in over time)
        const G = phone ? 4 : 5, x0 = W * 0.08, x1 = W * 0.92, top = H * 0.2, bot = H * 0.8, per = 1.1, age = sh ? 99 : (t % (G * per + 2.5));
        const nodes = [];
        for (let k = 0; k < G; k++) { const n = 2 ** k; for (let i = 0; i < n; i++) nodes.push({ k, i, x: lerp(x0, x1, G === 1 ? 0.5 : k / (G - 1)), y: lerp(top, bot, (i + 0.5) / n) }); }
        const at = (k, i) => nodes.find((q) => q.k === k && q.i === i);
        for (const q of nodes) { if (q.k === 0) continue; const p = at(q.k - 1, q.i >> 1), f = clamp((age - (q.k - 0.4) * per) / (per * 0.6), 0, 1); if (f <= 0) continue;
          g.line(p.x, p.y, lerp(p.x, q.x, f), lerp(p.y, q.y, f), c.neutron, 1.4, 0.55); if (f < 1) { g.glow(lerp(p.x, q.x, f), lerp(p.y, q.y, f), 10, c.neutron, 0.6); } }
        const r0 = Math.min(18, (bot - top) / 2 ** (G - 1) * 0.36 + 2);
        for (const q of nodes) { const f = clamp((age - q.k * per) / 0.3, 0, 1); if (f <= 0) continue; const r = Math.max(4, Math.min(r0 * 1.6, (bot - top) / 2 ** q.k * 0.3));
          g.glow(q.x, q.y, r * 2.2, c.photon, 0.35 * f); g.ball(q.x, q.y, r, c.warm, f); }
        for (let k = 0; k < G; k++) g.label(k === 0 ? (phone ? "first split" : "first split") : `generation ${k + 1}`, lerp(x0, x1, G === 1 ? 0.5 : k / (G - 1)), H * 0.12, { color: c.soft, size: fs - 1 });
        g.label(phone ? "each split frees neutrons that split more nuclei" : "each split frees neutrons that can split more nuclei: a chain reaction", W / 2, H * 0.9, { color: c.ink, size: fs + 1, weight: 600, serif: true });
        foot("the idea only · illustration");
        return;
      }
      if (S.mode === "sites") {
        const SITES = [["Oak Ridge, Tennessee", "separating uranium-235", c.cool], ["Hanford, Washington", "reactors making plutonium", c.proton], ["Los Alamos, New Mexico", "the laboratory", c.alpha]];
        const n = 3, gap = phone ? 10 : 24, wv = phone ? W * 0.84 : (W * 0.9 - gap * 2) / 3, hv = phone ? (H * 0.8 - gap * 2) / 3 : H * 0.42;
        SITES.forEach(([name, what, col], k) => {
          const x = phone ? W * 0.08 : W * 0.05 + k * (wv + gap), y = phone ? H * 0.08 + k * (hv + gap) : H * 0.24, cx = x + wv / 2, by = y + hv * (phone ? 0.62 : 0.66);
          const ctx = g.ctx; ctx.save(); ctx.fillStyle = g.rgba(col, 0.08); ctx.strokeStyle = g.rgba(col, 0.5); ctx.lineWidth = 1.2; ctx.beginPath(); if (ctx.roundRect) ctx.roundRect(x, y, wv, hv, 12); else ctx.rect(x, y, wv, hv); ctx.fill(); ctx.stroke(); ctx.restore();
          g.line(x + 10, by, x + wv - 10, by, c.soft, 1, 0.35);
          if (k === 0) { // a very long low building; light and heavy atoms sorted at the end
            const bw = wv * 0.62, bh = hv * 0.16; ctx.save(); ctx.fillStyle = g.rgba(c.soft, 0.25); ctx.fillRect(cx - bw / 2, by - bh, bw, bh); ctx.restore();
            for (let i = 0; i < 9; i++) { const xx = cx - bw / 2 + (i + 0.5) * bw / 9, f = ((t * 0.5 + i * 0.37) % 1); g.ball(xx, by - bh - 6 - f * hv * 0.12, 3, i % 4 ? c.soft : c.cool, 1 - f); }
            g.ball(cx + bw / 2 + 12, by - 6, 5, c.cool); g.glow(cx + bw / 2 + 12, by - 6, 14, c.cool, 0.4);
          } else if (k === 1) { // a reactor block by a river, with its glow
            const bw = wv * 0.3, bh = hv * 0.32; ctx.save(); ctx.fillStyle = g.rgba(c.soft, 0.25); ctx.fillRect(cx - bw / 2, by - bh, bw, bh); ctx.restore();
            g.glow(cx, by - bh * 0.5, bw * 0.6, c.fission, 0.25 + 0.08 * Math.sin(t * 2)); g.line(cx + bw / 2 + 6, by - bh * 0.6, cx + bw / 2 + 6, by - bh - 14, c.soft, 3, 0.4);
            ctx.save(); ctx.strokeStyle = g.rgba(c.cool, 0.6); ctx.lineWidth = 3; ctx.beginPath(); for (let i = 0; i <= 30; i++) { const xx = x + 12 + (wv - 24) * i / 30, yy = by + 10 + Math.sin(i * 0.6 + t) * 2; i ? ctx.lineTo(xx, yy) : ctx.moveTo(xx, yy); } ctx.stroke(); ctx.restore();
          } else { // a mesa with small buildings
            ctx.save(); ctx.fillStyle = g.rgba(c.warm, 0.22); ctx.beginPath(); ctx.moveTo(x + 12, by); ctx.lineTo(cx - wv * 0.3, by - hv * 0.22); ctx.lineTo(cx + wv * 0.28, by - hv * 0.22); ctx.lineTo(x + wv - 12, by); ctx.closePath(); ctx.fill(); ctx.restore();
            for (let i = 0; i < 4; i++) { ctx.save(); ctx.fillStyle = g.rgba(c.soft, 0.4); ctx.fillRect(cx - wv * 0.22 + i * wv * 0.12, by - hv * 0.22 - 9, wv * 0.08, 9); ctx.restore(); }
          }
          g.label(name, cx, y + (phone ? 14 : 20), { color: col, size: fs, weight: 600 });
          g.label(what, cx, by + (phone ? 18 : 30), { color: c.soft, size: fs - 1 });
        });
        if (!phone) g.label("three secret sites, 1942–1945", W / 2, H * 0.84, { color: c.ink, size: fs + 2, weight: 600, serif: true });
        foot("after US DOE / OSTI, The Manhattan Project");
        return;
      }
      // ---------- timeline ----------
      const x0 = W * 0.08, x1 = W * 0.92, y = H * 0.56, Y0 = 1938.5, Y1 = 1946, X = (v) => lerp(x0, x1, (v - Y0) / (Y1 - Y0));
      const tl = S.tl, dawn = smooth(1945.3, 1945.56, tl);
      g.glow(X(1945.54), y, W * 0.22, c.photon, 0.08 + 0.25 * dawn);
      g.line(x0, y, x1, y, c.soft, 2, 0.5);
      for (let yr = 1939; yr <= 1945; yr++) { g.line(X(yr), y - 5, X(yr), y + 5, c.soft, 1, 0.6); g.label(String(yr), X(yr), y + 18, { color: c.faint, size: fs - 1, raw: true }); }
      g.line(x0, y, X(Math.min(tl, Y1)), y, c.accent, 3, 0.9);
      EVENTS.forEach(([v, sh2, lng], i) => {
        const on = tl >= v - 0.02, up = i % 2 === 0, ly = up ? y - (phone ? 46 : 60) - (i % 3) * (phone ? 16 : 18) : y + (phone ? 50 : 62) + (i % 3) * (phone ? 16 : 18);
        const col = i >= 4 ? c.photon : c.accent;
        g.line(X(v), y, X(v), ly + (up ? 8 : -8), col, 1, on ? 0.6 : 0.15);
        g.dot(X(v), y, on ? 5 : 3, col, on ? 1 : 0.3); if (on) g.glow(X(v), y, 14, col, 0.4);
        g.label(phone ? sh2 : lng, X(v), ly, { color: on ? (i >= 4 ? c.ink : c.soft) : c.faint, size: phone ? fs - 1 : fs, weight: i === 4 ? 700 : 500, alpha: on ? 1 : 0.4, bg: true });
      });
      g.label(phone ? "1938 to 1945" : "seven years from a laboratory discovery to a weapon", W / 2, H * 0.12, { color: c.ink, size: fs + 2, weight: 600, serif: true });
      foot(phone ? "sources: Rhodes 1986; US DOE" : "sources: R. Rhodes, The Making of the Atomic Bomb (1986); US DOE / OSTI history");
    },
  });
})();
