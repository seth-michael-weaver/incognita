/* Nuclear weapons, a history (3): the arms race and the treaties. Scenes (S.mode):
 *   "bravo" = Castle Bravo, 1 March 1954, Bikini Atoll: fallout on the inhabited atolls of Rongelap and Utrik and on the
 *             Japanese fishing boat Daigo Fukuryu Maru (Lucky Dragon No. 5); its radio operator Aikichi Kuboyama died that
 *             September (US DOE Marshall Islands program history; Hiroshima Peace Memorial Museum). Schematic, not to scale.
 *   "count" = the world's nuclear warhead inventory, 1945-2025, approximate, after the Federation of American Scientists
 *             (Kristensen, Korda et al., "Status of World Nuclear Forces", and Norris & Kristensen, Bull. At. Sci. 66 (2010) 77):
 *             about 70,000 at the 1986 peak, about 12,000 today (total inventory, including retired warheads awaiting
 *             dismantlement). Anchor points below; drawn as a smooth curve, rounded.
 *   Treaties marked (UN Office for Disarmament Affairs; CTBTO; US State Dept.): Partial Test Ban 1963; NPT signed 1968, in force
 *   1970; INF 1987; START I 1991; CTBT opened for signature 1996 (not in force); New START 2010 (in force 2011, expired
 *   February 2026). Test counts (Arms Control Association): about 2,000 tests 1945-2017, over 500 of them in the atmosphere. */
(function () {
  const { TAU, clamp, lerp, smooth } = WT.util;
  const SHOT = () => document.body.classList.contains("shot");
  const INV = [[1945, 2], [1950, 300], [1955, 2600], [1960, 22000], [1965, 38000], [1970, 39000], [1975, 47000], [1980, 55000], [1986, 70300], [1990, 60000], [1995, 40000], [2000, 31500], [2005, 26000], [2010, 22000], [2015, 15800], [2020, 13400], [2025, 12200]];
  const inv = (y) => { if (y <= INV[0][0]) return INV[0][1]; for (let i = 1; i < INV.length; i++) if (y <= INV[i][0]) { const [a, va] = INV[i - 1], [b, vb] = INV[i], s = (y - a) / (b - a), u = s * s * (3 - 2 * s); return lerp(va, vb, u); } return INV[INV.length - 1][1]; };
  const TREATY = [[1963.6, "Partial Test Ban", "no tests in the air, in space or under water"], [1968.5, "Non-Proliferation Treaty", "no spread of weapons; disarmament; peaceful use"], [1987.9, "INF Treaty", "a whole class of missiles removed"], [1991.6, "START I", "the first deep cuts"], [1996.7, "Comprehensive Test Ban", "no test explosions at all (not yet in force)"], [2010.3, "New START", "limits on deployed warheads (expired 2026)"]];

  WT.chapter("nwrace", {
    level: 1, num: "Lesson 1", title: "The arms race and the treaties", short: "Arms race, treaties",
    html: `
<div class="step">
  <h3>A race begins</h3>
  <p>The Soviet Union tested its first atomic bomb in 1949, Britain in 1952, France in 1960 and China in 1964. In 1952 the United States tested the first <b>thermonuclear</b> or hydrogen bomb, in which a fission explosion sets off the fusion of hydrogen isotopes; the Soviet Union followed within a few years. These weapons could be far more powerful than the bombs of 1945.</p>
</div>
<div class="step">
  <h3>Castle Bravo, 1954: fallout</h3>
  <p>A US test at Bikini Atoll in March 1954 turned out far bigger than expected. Its fallout, white radioactive ash, fell on the inhabited atolls of Rongelap and Utrik and on the Japanese fishing boat Lucky Dragon No. 5. The crew fell ill and its radio operator died that autumn. The outcry helped start the worldwide campaign to stop testing.</p>
  <div class="btns"><button class="btn ghost" data-act="wind">Replay the wind</button></div>
</div>
<div class="step">
  <h3>Seventy thousand warheads</h3>
  <p>About 2,000 nuclear tests were carried out between 1945 and 2017, more than 500 of them in the open air. The number of warheads in the world climbed for four decades, to about 70,000 in the mid-1980s, then fell by more than four fifths after the Cold War ended.</p>
  <div class="ctl"><label for="nwr-y">Year</label><input id="nwr-y" type="range" data-bind="yr" data-instant min="1945" max="2025" step="1" value="1986"><output data-show="yr" data-fmt="0"></output></div>
</div>
<div class="step">
  <h3>The treaties</h3>
  <p>The 1963 Partial Test Ban moved tests underground. The 1968 <b>Non-Proliferation Treaty</b>, now joined by almost every country, bars the spread of weapons and commits the nuclear states to disarm. US–Soviet and US–Russian treaties then cut the arsenals, and the 1996 Comprehensive Test Ban, signed by most of the world but not yet in force, bans all test explosions. Point at a treaty.</p>
</div>`,
    setup(S) { S.set("mode", "bravo"); S.set("yr", 1986); S.set("wind", 0); S.windT = 0; S.on("wind", () => (S.windT = S.time)); S.pick = -1; },
    steps: [
      (S) => { S.set("mode", "count"); S.to("yr", 1964, SHOT()); S.span = 0; },
      (S) => { S.set("mode", "bravo"); S.windT = S.time; },
      (S) => { S.set("mode", "count"); S.to("yr", 1986, SHOT()); S.span = 1; },
      (S) => { S.set("mode", "count"); S.to("yr", 2025, SHOT()); S.span = 2; if (SHOT()) S.pick = 1; },
    ],
    frame(g, S, dt) {
      const { W, H, c, ctx } = g, phone = W < 600, fs = phone ? 11 : 13;
      const foot = (s) => g.label(s, W - 6, H - 8, { color: c.faint, size: 10, align: "right" });
      if (S.mode === "bravo") {
        // schematic ocean with three atolls and a boat; the plume drifts east with the wind (not to scale)
        const u = SHOT() ? 1 : clamp((S.time - (S.windT || 0)) / 6, 0, 1), y0 = H * 0.5;
        const P = { bik: [W * 0.14, y0 + H * 0.04], ron: [W * 0.58, y0 - H * 0.02], utr: [W * 0.84, y0 - H * 0.16], boat: [W * 0.42, y0 + H * 0.06] };
        for (let i = 0; i < 9; i++) g.line(0, H * (0.2 + i * 0.08), W, H * (0.2 + i * 0.08) + Math.sin(S.time * 0.4 + i) * 2, c.cool, 1, 0.12);
        // the plume: a soft band widening downwind, cut at u
        ctx.save(); const gx = lerp(P.bik[0], W * 0.98, u); ctx.beginPath(); ctx.rect(0, 0, gx, H); ctx.clip();
        const gr = ctx.createLinearGradient(P.bik[0], 0, W, 0); gr.addColorStop(0, g.rgba(c.soft, 0.42)); gr.addColorStop(1, g.rgba(c.soft, 0.1)); ctx.fillStyle = gr;
        ctx.beginPath(); ctx.moveTo(P.bik[0], P.bik[1] - 6); ctx.bezierCurveTo(W * 0.4, y0 - H * 0.16, W * 0.7, y0 - H * 0.3, W, y0 - H * 0.32); ctx.lineTo(W, y0 + H * 0.02); ctx.bezierCurveTo(W * 0.7, y0 + H * 0.08, W * 0.4, y0 + H * 0.16, P.bik[0], P.bik[1] + 6); ctx.closePath(); ctx.fill(); ctx.restore();
        for (let i = 0; i < 40; i++) { const f = ((S.time * 0.05 + i / 40) % 1) * u; const x = lerp(P.bik[0], W, f), y = lerp(P.bik[1], y0 - H * 0.12, f) + Math.sin(i * 5.3) * H * 0.1 * f; g.dot(x, y, 1.8, c.ink, 0.5 * (1 - f)); }
        const isl = (p, name, hit) => { const on = hit && u > (p[0] - P.bik[0]) / (W - P.bik[0]); g.ring(p[0], p[1], phone ? 9 : 12, on ? c.proton : c.fission, 3, 0.85); g.glow(p[0], p[1], 22, on ? c.proton : c.fission, on ? 0.4 : 0.15); g.label(name, p[0], p[1] + (phone ? 22 : 26), { color: on ? c.proton : c.soft, size: fs, weight: 600, bg: true }); };
        isl(P.bik, "Bikini Atoll (test site)", false); isl(P.ron, "Rongelap", true); isl(P.utr, "Utrik", true);
        { const [bx, by] = P.boat, on = u > (bx - P.bik[0]) / (W - P.bik[0]); ctx.save(); ctx.fillStyle = on ? c.proton : c.soft; ctx.beginPath(); ctx.moveTo(bx - 14, by); ctx.lineTo(bx + 14, by); ctx.lineTo(bx + 9, by + 6); ctx.lineTo(bx - 9, by + 6); ctx.closePath(); ctx.fill(); ctx.fillRect(bx - 1, by - 14, 2, 14); ctx.restore();
          g.label(phone ? "Lucky Dragon No. 5" : "fishing boat Lucky Dragon No. 5", bx, by + (phone ? 40 : 26), { color: on ? c.proton : c.soft, size: fs, weight: 600, bg: true }); }
        g.arrow(W * 0.1, H * 0.16, W * 0.26, H * 0.16, c.soft, 2, 0.7); g.label("wind", W * 0.18, H * 0.16 - 14, { color: c.soft, size: fs - 1 });
        g.label(phone ? "schematic, not to scale" : "schematic of the fallout, not to scale", W / 2, H * 0.9, { color: c.soft, size: fs });
        foot(phone ? "after US DOE history" : "after US DOE Marshall Islands history; Hiroshima Peace Memorial Museum");
        return;
      }
      // ---------- the count ----------
      const x0 = W * (phone ? 0.13 : 0.1), x1 = W * 0.95, yT = H * 0.2, yB = H * (phone ? 0.7 : 0.78), Y0 = 1945, Y1 = 2025, VM = 75000;
      const X = (y) => lerp(x0, x1, (y - Y0) / (Y1 - Y0)), Yv = (v) => lerp(yB, yT, v / VM), yr = clamp(S.yr, Y0, Y1), span = S.span || 0;
      const pts = [], cur = [];
      for (let y = Y0; y <= Y1; y += 0.5) { pts.push([X(y), Yv(inv(y))]); if (y <= yr) cur.push([X(y), Yv(inv(y))]); }
      g.clip(x0, yT - 30, x1 - x0, yB - yT + 30); g.ground(cur.length > 1 ? cur : pts.slice(0, 2), c.proton, (yB - yT) * 0.9, 0.3); g.ctx.restore();
      g.poly(pts, c.soft, 1.5, 0.3, [4, 4]); if (cur.length > 1) g.poly(cur, c.proton, 2.6, 0.95);
      [0, 20000, 40000, 60000].forEach((v) => { g.line(x0, Yv(v), x1, Yv(v), c.soft, 1, 0.1); g.label(v ? `${(v / 1000).toFixed(0)},000` : "0", x0 - 6, Yv(v), { color: c.faint, size: fs - 2, align: "right" }); });
      for (let y = 1950; y <= 2020; y += phone ? 20 : 10) g.label(String(y), X(y), yB + 14, { color: c.faint, size: fs - 2, raw: true });
      const v = inv(yr); g.line(X(yr), yT, X(yr), yB, c.ink, 1, 0.3); g.dot(X(yr), Yv(v), 5, c.ink); g.glow(X(yr), Yv(v), 16, c.proton, 0.5);
      g.label(`${Math.round(yr)}: about ${(Math.round(v / (v > 2000 ? 1000 : 100)) * (v > 2000 ? 1000 : 100)).toLocaleString("en")} warheads`, W / 2, H * 0.08, { color: c.ink, size: fs + 2, weight: 600, serif: true });
      g.label(phone ? "nuclear warheads in the world" : "nuclear warheads in the world (approximate)", x0, yT - 14, { color: c.soft, size: fs - 1, align: "left" });
      if (span >= 1) { g.label(phone ? "peak, 1986" : "peak, 1986: about 70,000", X(1986), Yv(70300) - 14, { color: c.proton, size: fs - 1, weight: 600, bg: true }); }
      if (span >= 2) {
        // treaty markers along the bottom, with hover / tap to read
        const ty = yB + (phone ? 30 : 40);
        WT.grab(ctx.canvas, { down(x, y) { if (S.mode !== "count" || S.step !== 3) return false; let b = -1, bd = 24; TREATY.forEach(([ty2], k) => { const d = Math.abs(x - X(ty2)); if (d < bd && Math.abs(y - (yB + 40)) < 40) { bd = d; b = k; } }); if (b < 0) return false; S.pick = b; return true; },
          hover(x, y) { if (S.mode !== "count" || S.step !== 3) return; let b = -1, bd = 24; TREATY.forEach(([ty2], k) => { const d = Math.abs(x - X(ty2)); if (d < bd && Math.abs(y - (yB + 40)) < 40) { bd = d; b = k; } }); ctx.canvas.style.cursor = b >= 0 ? "pointer" : "default"; if (b >= 0) S.pick = b; } });
        TREATY.forEach(([ty2, name], k) => { const on = S.pick === k; g.line(X(ty2), Yv(inv(ty2)), X(ty2), ty - 8, c.fission, 1, on ? 0.8 : 0.3, [2, 3]); g.dot(X(ty2), ty, on ? 7 : 5, c.fission, on ? 1 : 0.7); if (on) g.glow(X(ty2), ty, 18, c.fission, 0.5); });
        const p = S.pick >= 0 ? TREATY[S.pick] : null;
        g.label(p ? `${Math.floor(p[0])} · ${p[1]}` : (phone ? "tap a green dot: a treaty" : "point at a green dot to read a treaty"), W / 2, H * (phone ? 0.85 : 0.9), { color: p ? c.fission : c.soft, size: fs + 1, weight: 600 });
        if (p) g.label(p[2], W / 2, H * (phone ? 0.86 : 0.9) + fs + 8, { color: c.soft, size: fs });
      }
      foot(phone ? "approx., after FAS" : "approximate, after the Federation of American Scientists");
    },
  });
})();
