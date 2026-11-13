/* Nuclear weapons, a history (2): Hiroshima and Nagasaki. Scenes (S.mode):
 *   "lanterns" = paper lanterns on a river at dusk (toro nagashi, held in Hiroshima every 6 August): one lantern for about
 *                1,000 people who had died by the end of 1945. Estimates from the Radiation Effects Research Foundation
 *                (RERF, "Frequently asked questions"): Hiroshima 90,000-166,000, Nagasaki 60,000-80,000 (populations about
 *                340,000-350,000 and 250,000-270,000). Solid lanterns = the low estimate, faint ones = the range up to the high one.
 *   "effects"  = the four effects of a nuclear explosion in general terms, as in public civil-defence literature (blast,
 *                heat, prompt radiation, fallout); rings are qualitative and NOT to scale; no distances are shown.
 *   "cohort"   = the RERF Life Span Study: about 120,000 people followed since 1950 (RERF). One dot = 500 people.
 * Sources shown on the drawing: RERF; Hiroshima Peace Memorial Museum; Nagasaki Atomic Bomb Museum. */
(function () {
  const { TAU, clamp, lerp, smooth, rng } = WT.util;
  const SHOT = () => document.body.classList.contains("shot");
  const mk = (n, seed) => { const r = rng(seed), a = []; for (let i = 0; i < n; i++) a.push({ x: r(), y: r(), ph: r() * TAU, s: 0.8 + 0.4 * r() }); return a; };
  const HIRO = mk(166, 21), NAGA = mk(80, 37), COH = mk(240, 5);
  const EFF = [["blast", "a pressure wave that flattens buildings"], ["heat", "a flash of light and heat that burns and starts fires"], ["prompt radiation", "gamma rays and neutrons in the first instant"], ["fallout", "radioactive dust carried downwind, for days to weeks"]];

  WT.chapter("nwcities", {
    level: 0, num: "Lesson 1", title: "Hiroshima and Nagasaki", short: "Hiroshima, Nagasaki",
    html: `
<div class="step">
  <h3>6 and 9 August 1945</h3>
  <p>An atomic bomb destroyed the centre of Hiroshima on 6 August 1945, and a second struck Nagasaki three days later. By the end of that year between 90,000 and 166,000 people had died in Hiroshima and between 60,000 and 80,000 in Nagasaki, most of them civilians. Japan announced its surrender on 15 August.</p>
</div>
<div class="step">
  <h3>How a nuclear explosion harms</h3>
  <p>Public civil-defence guides describe four effects: the <b>blast</b>, a wave of pressure that flattens buildings; the <b>heat</b>, a flash that burns skin and starts fires; <b>prompt radiation</b>, gamma rays and neutrons released in the first instant; and <b>fallout</b>, radioactive dust that the wind carries away. In 1945 most deaths came from the blast, the burns and the fires that followed.</p>
  <div class="btns" role="group" aria-label="Effect"><button class="btn ghost" data-act="e0" aria-pressed="false">Blast</button> <button class="btn ghost" data-act="e1" aria-pressed="false">Heat</button> <button class="btn ghost" data-act="e2" aria-pressed="false">Prompt radiation</button> <button class="btn ghost" data-act="e3" aria-pressed="false">Fallout</button></div>
</div>
<div class="step">
  <h3>The survivors</h3>
  <p>The survivors, the <b>hibakusha</b>, have told their stories for decades, and many became voices for abolishing nuclear weapons. Since 1950 a joint Japanese–US foundation has followed about 120,000 of them and their families. Their health records are the main source of what is known about the long-term effects of radiation, including a raised risk of cancer, and they underpin radiation-protection rules worldwide.</p>
</div>`,
    setup(S) {
      S.set("mode", "lanterns"); S.eff = -1;
      const press = () => document.querySelectorAll("#nwcities [data-act^=e]").forEach((b) => b.setAttribute("aria-pressed", String(b.dataset.act === "e" + S.eff)));
      [0, 1, 2, 3].forEach((k) => S.on("e" + k, () => { S.eff = S.eff === k ? -1 : k; S.effT = S.time; press(); }));
    },
    steps: [(S) => S.set("mode", "lanterns"), (S) => { S.set("mode", "effects"); if (SHOT()) S.eff = 1; }, (S) => S.set("mode", "cohort")],
    frame(g, S, dt) {
      const { W, H, c, ctx } = g, phone = W < 600, fs = phone ? 11 : 13, t = SHOT() ? 3 : S.time;
      const foot = (s) => g.label(s, W - 6, H - 8, { color: c.faint, size: 10, align: "right" });
      if (S.mode === "lanterns") {
        // dusk water: a band of dark blue with a few reflections; two groups of lanterns drifting slowly
        const wy = H * 0.3, gr = ctx.createLinearGradient(0, wy, 0, H); gr.addColorStop(0, g.rgba(c.cool, 0.05)); gr.addColorStop(1, g.rgba(c.cool, 0.22)); ctx.save(); ctx.fillStyle = gr; ctx.fillRect(0, wy, W, H - wy); ctx.restore();
        for (let i = 0; i < 6; i++) g.line(0, wy + (H - wy) * (i + 1) / 7, W, wy + (H - wy) * (i + 1) / 7 + Math.sin(t * 0.3 + i) * 3, c.cool, 1, 0.12);
        const groups = phone ? [[HIRO, 90, "Hiroshima", W * 0.05, H * 0.36, W * 0.9, H * 0.28], [NAGA, 60, "Nagasaki", W * 0.05, H * 0.7, W * 0.9, H * 0.15]]
          : [[HIRO, 90, "Hiroshima", W * 0.05, H * 0.38, W * 0.54, H * 0.42], [NAGA, 60, "Nagasaki", W * 0.64, H * 0.38, W * 0.31, H * 0.42]];
        const ls = phone ? 4.2 : 5.2;
        groups.forEach(([arr, lo, name, gx, gy, gw, gh]) => {
          arr.forEach((p, i) => {
            const x = gx + gw * ((p.x + t * 0.004 * p.s) % 1), y = gy + gh * p.y + Math.sin(t * 0.8 + p.ph) * 1.5, solid = i < lo, a = solid ? 1 : 0.35;
            g.glow(x, y - ls * 0.2, ls * 3.2, c.photon, (solid ? 0.32 : 0.12) * (0.85 + 0.15 * Math.sin(t * 2 + p.ph)));
            ctx.save(); ctx.globalAlpha = a; ctx.fillStyle = "#ffd98a"; ctx.fillRect(x - ls * 0.6, y - ls, ls * 1.2, ls * 1.3); ctx.fillStyle = g.rgba(c.warm, 0.9); ctx.fillRect(x - ls * 0.75, y + ls * 0.3, ls * 1.5, ls * 0.35); ctx.restore();
            g.line(x, y + ls * 0.8, x, y + ls * 2.6, c.photon, 1, 0.12 * a);
          });
          g.label(name, gx + gw / 2, gy - (phone ? 14 : 20), { color: c.ink, size: fs + 2, weight: 600, serif: true });
        });
        g.label(phone ? "one lantern ≈ 1,000 people who died by the end of 1945" : "one lantern for about 1,000 people who had died by the end of 1945", W / 2, H * 0.1, { color: c.ink, size: fs + 1, weight: 600, serif: true });
        g.label(phone ? "faint lanterns: the range of estimates" : "faint lanterns: the range between the low and the high estimate", W / 2, H * 0.1 + fs + 10, { color: c.soft, size: fs - 1 });
        foot(phone ? "estimates: RERF" : "estimates: Radiation Effects Research Foundation (RERF)");
        return;
      }
      if (S.mode === "effects") {
        const cx = W / 2, cy = H * (phone ? 0.46 : 0.48), R = Math.min(W * 0.4, H * 0.36), e = S.eff, age = SHOT() ? 2 : S.time - (S.effT || 0);
        const RING = [[0.62, c.cool], [0.86, c.warm], [0.38, c.alpha]]; // qualitative only, not to scale
        RING.forEach(([f, col], k) => { const on = e === -1 || e === k; ctx.save(); ctx.globalAlpha = on ? 0.16 : 0.04; ctx.fillStyle = col; ctx.beginPath(); ctx.arc(cx, cy, R * f, 0, TAU); ctx.fill(); ctx.restore(); g.ring(cx, cy, R * f, col, on ? 2 : 1, on ? 0.9 : 0.25, [5, 5]);
          if (e === k) { const p = (age * 0.6) % 1; g.ring(cx, cy, R * f * p, col, 2, 1 - p); } });
        // fallout: a plume drifting downwind
        { const on = e === -1 || e === 3; ctx.save(); ctx.globalAlpha = on ? 0.22 : 0.05; ctx.fillStyle = c.soft; ctx.beginPath(); ctx.moveTo(cx, cy - R * 0.05); ctx.quadraticCurveTo(cx + R * 0.9, cy - R * 0.35, cx + R * 1.5, cy - R * 0.2); ctx.quadraticCurveTo(cx + R * 0.9, cy + R * 0.05, cx, cy + R * 0.05); ctx.fill(); ctx.restore();
          if (e === 3) for (let i = 0; i < 18; i++) { const u = ((t * 0.15 + i / 18) % 1), x = cx + R * 1.4 * u, y = cy - R * 0.12 * Math.sin(u * 2.4) + Math.sin(i * 7.1) * R * 0.08 * u; g.dot(x, y, 2.2, c.soft, 0.8 * (1 - u)); } }
        g.glow(cx, cy, R * 0.18, c.photon, 0.6); g.dot(cx, cy, 4, c.ink);
        const L = [[0, -0.62, c.cool], [1, -0.86, c.warm], [2, -0.38, c.alpha]];
        L.forEach(([k, f, col]) => g.label(EFF[k][0], cx - R * 0.2, cy + R * f + 12, { color: col, size: fs, weight: 600, bg: true, alpha: e === -1 || e === k ? 1 : 0.35 }));
        g.label(EFF[3][0], Math.min(W - 40, cx + R * 1.2), cy - R * 0.36, { color: c.soft, size: fs, weight: 600, bg: true, alpha: e === -1 || e === 3 ? 1 : 0.35 });
        g.label(e >= 0 ? EFF[e][1] : (phone ? "pick an effect" : "pick an effect to see what it does"), W / 2, H * 0.9, { color: c.ink, size: fs + 1, weight: 600, serif: true });
        g.label("rings are qualitative, not to scale", W / 2, H * 0.08, { color: c.soft, size: fs - 1 });
        foot("after public civil-defence literature");
        return;
      }
      // ---------- the Life Span Study cohort ----------
      const cols = phone ? 16 : 24, rows = Math.ceil(COH.length / cols), gx = W * (phone ? 0.1 : 0.15), gw = W * (phone ? 0.8 : 0.7), gy = H * 0.24, gh = H * (phone ? 0.42 : 0.48);
      const d = Math.min(gw / cols, gh / rows), x0 = W / 2 - d * cols / 2;
      COH.forEach((p, i) => { const x = x0 + (i % cols + 0.5) * d, y = gy + (Math.floor(i / cols) + 0.5) * d;
        g.glow(x, y, d * 0.8, c.photon, 0.12); g.ball(x, y, d * 0.3, c.photon, 0.9); });
      g.label(phone ? "about 120,000 survivors, followed since 1950" : "about 120,000 survivors and their families, followed since 1950", W / 2, H * 0.12, { color: c.ink, size: fs + 1, weight: 600, serif: true });
      g.label("one dot = 500 people", W / 2, gy + rows * d + 18, { color: c.soft, size: fs - 1 });
      foot(phone ? "RERF Life Span Study" : "Radiation Effects Research Foundation, Life Span Study · Hiroshima Peace Memorial Museum");
    },
  });
})();
