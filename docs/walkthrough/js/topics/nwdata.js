/* Nuclear weapons (5): reactors, weapons and nuclear data. Concepts only; no device quantities. Scenes (S.mode):
 *   "two"    = fission and fusion side by side (generic cartoons; energies only in words).
 *   "safe"   = why a power reactor cannot explode like a bomb, as stated by the IAEA, the US NRC and the World Nuclear
 *              Association: low-enriched fuel diluted in uranium-238, a chain reaction held at balance and paced by delayed
 *              neutrons (as in the criticality and kinetics lessons), negative temperature feedback. Labels only.
 *   "enr"    = enrichment levels: natural uranium 0.7 % U-235; power-reactor fuel about 3-5 %; low-enriched uranium (LEU) is
 *              below 20 % by definition (IAEA Safeguards Glossary); 20 % and above is highly enriched uranium (HEU). The axis
 *              stops at 25 % on purpose. Research-reactor conversion from HEU to LEU: the RERTR programme, since 1978 (US DOE/NNSA).
 *   "uses"   = where nuclear data serve safety and verification: criticality safety in fuel plants, transport and storage;
 *              the 1999 Tokaimura criticality accident (IAEA, "Report on the preliminary fact finding mission following the
 *              accident at the nuclear fuel processing facility in Tokaimura", 1999); safeguards; test monitoring. */
(function () {
  const { TAU, clamp, lerp, smooth } = WT.util;
  const SHOT = () => document.body.classList.contains("shot");

  WT.chapter("nwdata", {
    level: 0, num: "Lesson 1", title: "Reactors, weapons and nuclear data", short: "Reactors vs weapons",
    html: `
<div class="step">
  <h3>Splitting and joining</h3>
  <p>Nuclear energy comes from two opposite reactions. <b>Fission</b> splits a heavy nucleus such as uranium; <b>fusion</b> joins light ones such as hydrogen. Both turn a little mass into a lot of energy, as the <a href="./#binding" data-keep-lang>binding-energy curve</a> shows. Power reactors use fission; the Sun, and the <a href="#fusion">fusion</a> machines being built today, use fusion.</p>
</div>
<div class="step">
  <h3>Why a reactor cannot explode like a bomb</h3>
  <p>A power reactor and a weapon both use fission, but almost nothing else is alike. Reactor fuel is mostly uranium-238 with only a few percent uranium-235. The chain reaction is held in balance, paced by the small share of neutrons that arrive late, and when the fuel heats up physics itself slows it down. Reactor accidents can be very serious, through overheating, steam or hydrogen (see <a href="#accidents">three accidents</a>), but a power reactor cannot become a nuclear explosion.</p>
</div>
<div class="step">
  <h3>Enrichment matters</h3>
  <p>Natural uranium is 0.7 % uranium-235. Power-reactor fuel is enriched to about 3–5 %. Anything below 20 % is called <b>low-enriched uranium</b> and is not considered usable for weapons; 20 % and above is highly enriched and is guarded under the strictest controls. Since 1978 many research reactors around the world have been converted from highly to low-enriched fuel.</p>
</div>
<div class="step">
  <h3>Nuclear data for safety and verification</h3>
  <p>Wherever fissile material is handled, in fuel plants, transport casks and storage pools, engineers compute how close it is to a chain reaction and keep a wide margin; those calculations rest on evaluated nuclear data. When that margin was ignored, as at a fuel plant in Tokaimura, Japan, in 1999, workers died. The same data, half-lives, fission yields and cross sections, let inspectors measure material and let the monitoring network read a xenon sample.</p>
</div>`,
    setup(S) { S.set("mode", "two"); },
    steps: [(S) => S.set("mode", "two"), (S) => S.set("mode", "safe"), (S) => S.set("mode", "enr"), (S) => S.set("mode", "uses")],
    frame(g, S, dt) {
      const { W, H, c, ctx } = g, phone = W < 600, fs = phone ? 11 : 13, t = SHOT() ? 1.7 : S.time;
      const foot = (s) => g.label(s, W - 6, H - 8, { color: c.faint, size: 10, align: "right" });
      if (S.mode === "two") {
        const ax = phone ? W / 2 : W * 0.28, ay = phone ? H * 0.3 : H * 0.48, bx = phone ? W / 2 : W * 0.72, by = phone ? H * 0.72 : H * 0.48, R = Math.min(W, H) * (phone ? 0.09 : 0.1);
        // fission: one big nucleus breaks in two, repeatedly
        { const u = (t % 3) / 3, s = smooth(0.35, 0.7, u);
          if (s < 0.02) g.nucleus(ax, ay, R, { N: 80, Z: 32, seed: 4, t, beta: 0.1 + 0.3 * smooth(0.2, 0.35, u), halo: c.warm, haloAlpha: 0.25 });
          else { const d = R * (0.6 + 1.6 * s); g.glow(ax, ay, R * 2.4, c.photon, 0.4 * (1 - s)); g.nucleus(ax - d, ay, R * 0.75, { N: 44, Z: 18, seed: 2, t }); g.nucleus(ax + d, ay, R * 0.68, { N: 36, Z: 14, seed: 9, t }); }
          g.label("fission: heavy splits", ax, ay + R * 2.1, { color: c.warm, size: fs + 1, weight: 600 }); }
        // fusion: two light nuclei join
        { const u = (t % 3) / 3, s = smooth(0.1, 0.5, u), d = R * 1.6 * (1 - s), r = R * 0.38;
          if (s < 0.98) { g.nucleus(bx - d, by, r, { N: 2, Z: 1, seed: 3, t }); g.nucleus(bx + d, by, r * 1.1, { N: 3, Z: 1, seed: 5, t }); }
          else { g.glow(bx, by, R * 2.2, c.photon, 0.5 * (1 - smooth(0.5, 1, u))); g.nucleus(bx, by, r * 1.25, { N: 4, Z: 2, seed: 6, t }); }
          g.label("fusion: light nuclei join", bx, by + R * 2.1, { color: c.cool, size: fs + 1, weight: 600 }); }
        g.label(phone ? "both release nuclear energy" : "both turn a little mass into energy", W / 2, H * 0.08, { color: c.ink, size: fs + 2, weight: 600, serif: true });
        foot("illustration");
        return;
      }
      if (S.mode === "safe") {
        // a reactor vessel cartoon with labelled reasons, lit one after another
        const cx = W * (phone ? 0.5 : 0.36), cy = H * (phone ? 0.38 : 0.5), vw = Math.min(W * (phone ? 0.3 : 0.24), 220), vh = vw * 1.35;
        ctx.save(); ctx.fillStyle = g.rgba(c.cool, 0.18); ctx.strokeStyle = g.rgba(c.soft, 0.7); ctx.lineWidth = 2; ctx.beginPath(); if (ctx.roundRect) ctx.roundRect(cx - vw / 2, cy - vh / 2, vw, vh, vw * 0.3); else ctx.rect(cx - vw / 2, cy - vh / 2, vw, vh); ctx.fill(); ctx.stroke(); ctx.restore();
        for (let i = 0; i < 6; i++) { const x = cx - vw * 0.32 + i * vw * 0.128; ctx.save(); ctx.fillStyle = g.rgba(c.warm, 0.55); ctx.fillRect(x - 3, cy - vh * 0.25, 6, vh * 0.55); ctx.restore(); }
        for (let i = 0; i < 3; i++) { const x = cx - vw * 0.26 + i * vw * 0.26; ctx.save(); ctx.fillStyle = g.rgba(c.ink, 0.6); ctx.fillRect(x - 2.5, cy - vh * 0.5, 5, vh * 0.32); ctx.restore(); }
        g.glow(cx, cy + vh * 0.05, vw * 0.5, c.fission, 0.15 + 0.03 * Math.sin(t * 2));
        const R4 = [["low-enriched fuel, mostly uranium-238", c.warm], ["chain held in balance, not growing", c.fission], ["late neutrons set a slow pace", c.neutron], ["hotter fuel → fewer fissions", c.proton]];
        const lx = phone ? W * 0.06 : W * 0.6, ly = phone ? H * 0.66 : H * 0.3;
        R4.forEach(([s, col], k) => { const on = SHOT() ? 1 : smooth(k * 0.8, k * 0.8 + 0.5, t % 6), y = ly + k * (phone ? 24 : 40);
          g.dot(lx, y, 5, col, 0.3 + 0.7 * on); if (on > 0.5) g.glow(lx, y, 14, col, 0.4); g.label(s, lx + 14, y, { color: c.ink, size: fs, weight: 600, align: "left", alpha: 0.35 + 0.65 * on }); });
        g.label(phone ? "a power reactor" : "a power reactor: four reasons it cannot explode like a bomb", W / 2, H * 0.07, { color: c.ink, size: fs + 1, weight: 600, serif: true });
        foot("after IAEA, US NRC, World Nuclear Association");
        return;
      }
      if (S.mode === "enr") {
        const x0 = W * 0.08, x1 = W * 0.92, y = H * 0.5, MAX = 25, X = (p) => lerp(x0, x1, p / MAX);
        ctx.save(); ctx.fillStyle = g.rgba(c.fission, 0.12); ctx.fillRect(x0, y - 26, X(20) - x0, 52); ctx.fillStyle = g.rgba(c.proton, 0.1); ctx.fillRect(X(20), y - 26, x1 - X(20), 52); ctx.restore();
        g.line(x0, y + 26, x1, y + 26, c.soft, 1.2, 0.6);
        [0, 5, 10, 15, 20, 25].forEach((p) => { g.line(X(p), y + 26, X(p), y + 32, c.soft, 1, 0.6); g.label(`${p} %`, X(p), y + 44, { color: c.faint, size: fs - 2 }); });
        g.line(X(20), y - 46, X(20), y + 26, c.proton, 2, 0.9);
        g.label(phone ? "LEU: below 20 %" : "low-enriched uranium (LEU): below 20 %", X(phone ? 12.5 : 12), y - 40, { color: c.fission, size: fs, weight: 600 });
        g.label(phone ? "HEU" : "highly enriched (HEU)", (X(20) + x1) / 2, y - 40, { color: c.proton, size: fs, weight: 600 });
        const mark = (p0, p1, col, s1, s2, up) => { const xm = (X(p0) + X(p1)) / 2; ctx.save(); ctx.fillStyle = g.rgba(col, 0.55); ctx.fillRect(X(p0) - (p1 === p0 ? 2 : 0), y - 10, Math.max(4, X(p1) - X(p0)), 20); ctx.restore(); g.glow(xm, y, 18, col, 0.4);
          g.label(s1, xm, y + (up ? -96 : 70), { color: col, size: fs, weight: 600, bg: true }); g.label(s2, xm, y + (up ? -96 : 70) + fs + 6, { color: c.soft, size: fs - 2 }); g.line(xm, y + (up ? -12 : 12), xm, y + (up ? -58 : 58), col, 1, 0.5); };
        mark(0.7, 0.7, c.soft, "natural uranium", "0.7 %", false); mark(3, 5, c.warm, phone ? "reactor fuel" : "power-reactor fuel", "about 3–5 %", true);
        g.label("share of uranium-235", W / 2, H * 0.12, { color: c.ink, size: fs + 2, weight: 600, serif: true });
        foot("definitions: IAEA Safeguards Glossary");
        return;
      }
      // ---------- uses ----------
      const U = [["fuel plants", c.warm], ["transport casks", c.cool], ["storage pools", c.fission], ["safeguards", c.photon], ["test monitoring", c.alpha]];
      const n = U.length, cy = H * 0.5, R = Math.min(W / (n * 2.6), H * 0.09);
      const hub = [W / 2, H * (phone ? 0.2 : 0.18)];
      g.glow(hub[0], hub[1], R * 2.4, c.accent, 0.35); g.ball(hub[0], hub[1], R * 0.6, c.accent);
      g.label("evaluated nuclear data", hub[0], hub[1] - R * 1.2, { color: c.accent, size: fs + 1, weight: 600 });
      U.forEach(([s, col], k) => { const x = phone ? W * (0.12 + 0.19 * k) : W * (0.12 + 0.19 * k), y = cy + (phone && k % 2 ? H * 0.12 : 0), u = ((t * 0.4 + k * 0.2) % 1);
        g.line(hub[0], hub[1], x, y, col, 1.2, 0.35); g.dot(lerp(hub[0], x, u), lerp(hub[1], y, u), 3, col, 1 - u * 0.5);
        g.glow(x, y, R * 1.6, col, 0.3); g.ring(x, y, R, col, 2, 0.9); g.label(s, x, y + R + 14, { color: col, size: fs - 1, weight: 600 }); });
      g.label(phone ? "safety margins and measurements rest on the data" : "the same data keep handling safe and let inspectors measure", W / 2, H * 0.86, { color: c.ink, size: fs + 1, weight: 600, serif: true });
      foot("Tokaimura 1999: IAEA fact-finding report");
    },
  });
})();
