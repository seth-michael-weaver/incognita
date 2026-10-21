/* Chapter 12: how the model is layered. One reaction's cross section drawn as a landscape over neutron energy; four layers
 * stack up on it (a small stack of slabs shows which are on):
 *   1 the blind engine (one global rule; judged on measurements it never saw: hollow dots revealed on demand),
 *   2 the measured-structure tier (own D0, S0/S1, <Gg>, levels): the line barely moves (today's tests found no gain),
 *   3 TERRA anchoring: where measurements exist the line follows them, elsewhere it falls back to the engine,
 *   4 the uncertainty band: drag its width and count the measurements inside (68 % is the honest target).
 * Curves and points are illustrative (one made-up nucleus); the counts quoted in the text are the real scoreboard. */
(function () {
  const { clamp, lerp, smooth, rng } = WT.util;
  const truth = (x) => 0.78 - 0.46 * x + 0.05 * Math.sin(7 * x) + 0.09 * Math.exp(-Math.pow((x - 0.62) / 0.06, 2));
  const engine = (x) => truth(x) + 0.06 * Math.sin(3.1 * x + 0.6) - 0.045 * Math.exp(-Math.pow((x - 0.62) / 0.09, 2));
  const msDelta = (x) => 0.008 * Math.sin(9 * x + 1);
  // measurements: fixed points across the range; a point "exists" when it lies inside the measured window
  const PTS = (() => { const r = rng(11), a = []; for (let i = 0; i < 26; i++) { const x = 0.04 + 0.92 * (i + r() * 0.8) / 26; a.push({ x, y: truth(x) + (r() - 0.5) * 0.05, e: 0.02 + r() * 0.012 }); } return a; })();
  const winOf = (S) => { const c = 0.56, h = 0.5 * S.cov; return [c - h, c + h]; };
  const wIn = (x, w) => smooth(w[0] - 0.05, w[0] + 0.02, x) * (1 - smooth(w[1] - 0.02, w[1] + 0.05, x));   // 1 inside the window
  const terra = (x, S, w) => { const e = engine(x) + S.ms * msDelta(x); return e + S.anchor * wIn(x, w) * (truth(x) - e) * 0.94; };
  const half = (x, S, w) => S.band * lerp(0.06, 0.017, S.anchor * wIn(x, w));

  const LAYERS = [
    { n: 1, name: "blind engine", col: "neutron" },
    { n: 2, name: "measured structure", col: "alpha" },
    { n: 3, name: "TERRA: anchored to data", col: "accent" },
    { n: 4, name: "uncertainty band", col: "warm" },
  ];

  WT.chapter("layers", {
    num: "Chapter 12", title: "How the model is layered", short: "Layers",
    lead: "Everything so far was one engine. What we actually deliver is built in layers on top of it, and each layer has to earn its place against measurements.",
    html: `
<div class="step">
  <div class="layer-chip on">In use</div>
  <h3>Layer 1 · One rule for every nucleus</h3>
  <p>The engine you have just read about is the bottom layer. It runs the same physics, with the same global settings, for every nuclide, and it is never fitted to the cross sections it is judged on. The blue line is its prediction for one reaction.</p>
  <div class="btns"><button class="btn ghost" data-act="reveal" aria-pressed="false">Show the measurements</button></div>
  <p>That is what makes it testable: it is scored on measurements it never saw, against other model codes run on the same nuclei. As of 21 October 2026 it is ahead, with the whole 95 % interval below zero, in 53 of 71 such comparisons, level in 17 and behind in 1.</p>
  <div class="figs" aria-label="53 wins, 17 ties, 1 loss"><div class="w"><b>53</b><span>win</span></div><div><b>17</b><span>tie</span></div><div class="l"><b>1</b><span>loss</span></div></div>
</div>
<div class="step">
  <div class="layer-chip null">Tested: no gain yet</div>
  <h3>Layer 2 · Each nucleus's own measurements</h3>
  <p>Some properties of a nucleus are measured directly: how far apart its resonances sit (the level spacing D0), how readily it absorbs slow neutrons (the strength functions S0 and S1), how fast it gives off gamma rays (⟨Γγ⟩), and its known energy levels. The second layer gives each nucleus its own measured values in place of the global rule.</p>
  <div class="btns"><button class="btn ghost" data-act="ms0" aria-pressed="true">Global rule</button><button class="btn ghost" data-act="ms1" aria-pressed="false">Own measurements</button></div>
  <p>Switch it on and the line barely moves. That is today's honest result. The latest tests went after the comparisons we do not win and found no gain: matching the measured ⟨Γγ⟩ moved capture the wrong way, the measured S0 did not follow the misses, and a nucleus-by-nucleus level-density fit pushed the rare earths away from the data. Part of the reason is that the engine already uses the measured S1 and D0 for those nuclei. One result points the other way: fitting each nucleus's level density to its own measured levels and D0 turns the single remaining loss, (n,p) near its threshold, into a tie, but it makes neutron capture worse, so the layer stays off for now.</p>
</div>
<div class="step">
  <div class="layer-chip cand">Candidate</div>
  <h3>Layer 3 · Following good data (TERRA)</h3>
  <p>Where a reaction has been measured well, the best estimate should follow the measurements. The third layer, TERRA, takes the engine's line and, where good data exist, draws the result through them. Where there are none, it falls back to the engine.</p>
  <div class="ctl"><label for="lay-cov">Share of the energy range measured (%)</label><input id="lay-cov" type="range" data-bind="cov" min="0" max="1" step="0.01" value="0.45"><output data-show="covPct" data-fmt="0"></output></div>
  <p>Against the four main evaluated data libraries (ENDF/B-VIII.1, JEFF-4.0, JENDL-5 and TENDL-2025), the current candidate, R072w of 11 October 2026, is ahead in 217 of 326 comparisons, level in 108 and behind in 1. Most of these are in-sample: TERRA has seen those measurements, as the libraries have. A rebuild on the current engine, R073, is in progress.</p>
  <div class="figs" aria-label="217 wins, 108 ties, 1 loss"><div class="w"><b>217</b><span>win</span></div><div><b>108</b><span>tie</span></div><div class="l"><b>1</b><span>loss</span></div></div>
</div>
<div class="step">
  <div class="layer-chip wip">Work in progress</div>
  <h3>Layer 4 · Honest error bars</h3>
  <p>A number without an uncertainty is half an answer. The top layer puts a band around the line that should hold the truth about two times in three (a 68 % band): narrow where good data pin it down, wider where they do not.</p>
  <div class="ctl"><label for="lay-band">Band width · measurements inside (%)</label><input id="lay-band" type="range" data-bind="band" min="0.2" max="2.5" step="0.05" value="1"><output data-show="inside" data-fmt="0"></output></div>
  <p>Drag it and count the measurements inside. Too narrow, and the band claims a precision it does not have; too wide, and it says nothing. The band for the engine itself is not adopted yet. The latest version is on target when all reactions are pooled (73 % inside its 68 % band, 95 % inside its 95 % band), but no variant yet hits both targets in each of the six reaction families. TERRA carries its own bands, and they are part of its comparisons above.</p>
</div>
<div class="step">
  <h3>Where it stands</h3>
  <p>A layer is adopted only after it has been tested against measurements, and it stays off when it does not help. Today the engine is in use and TERRA is a candidate; the measured-structure layer and the engine's uncertainty band are still being tested.</p>
  <p><a href="scoreboard.html" data-keep-lang>See the full scoreboard →</a> Every comparison we do not win, each rival, and how to read it.</p>
  <div class="aside">Figures as of 21 October 2026, from the project's research ledger. The curves in the picture are illustrative.</div>
</div>`,
    setup(S) {
      S.to("layer", 1, true); S.to("reveal", 0, true); S.to("ms", 0, true); S.to("anchor", 0, true); S.to("bandOn", 0, true);
      S.set("cov", 0.45); S.set("band", 1); S.covPct = 45; S.inside = 0;
      const press = (act, on) => document.querySelectorAll(`#layers [data-act="${act}"]`).forEach((b) => b.setAttribute("aria-pressed", String(on)));
      S.on("reveal", () => { const on = S.target.reveal < 0.5; S.to("reveal", on ? 1 : 0); press("reveal", on); });
      S.on("ms0", () => { S.to("ms", 0); press("ms0", true); press("ms1", false); });
      S.on("ms1", () => { S.to("ms", 1); press("ms0", false); press("ms1", true); });
    },
    steps: [
      (S) => { S.set("layer", 1); S.to("anchor", 0); S.to("bandOn", 0); },
      (S) => { S.set("layer", 2); S.to("reveal", 1); S.to("anchor", 0); S.to("bandOn", 0); },
      (S) => { S.set("layer", 3); S.to("reveal", 1); S.to("anchor", 1); S.to("bandOn", 0); },
      (S) => { S.set("layer", 4); S.to("reveal", 1); S.to("anchor", 1); S.to("bandOn", 1); },
      (S) => { S.set("layer", 4); S.to("reveal", 1); S.to("anchor", 1); S.to("bandOn", 1); },
    ],
    frame(g, S) {
      const { W, H, c } = g, phone = W < 600;
      const x0 = W * (phone ? 0.06 : 0.08), x1 = W * (phone ? 0.94 : 0.92), top = H * (phone ? 0.34 : 0.3), bot = H * (phone ? 0.72 : 0.8);
      const X = (x) => lerp(x0, x1, x), Y = (v) => lerp(bot, top, (v - 0.15) / 0.8);
      const w = winOf(S), N = 120;
      S.covPct = Math.round(S.cov * 100);
      // layer 4 band (under everything)
      if (S.bandOn > 0.01) {
        const up = [], dn = [];
        for (let i = 0; i <= N; i++) { const x = i / N, m = terra(x, S, w), h = half(x, S, w); up.push([X(x), Y(m + h)]); dn.push([X(x), Y(m - h)]); }
        g.area(up.concat(dn.reverse()), c.warm, 0.22 * S.bandOn);
      }
      // layer 1: the engine's line as a landscape
      const eng = []; for (let i = 0; i <= N; i++) { const x = i / N; eng.push([X(x), Y(engine(x) + S.ms * msDelta(x))]); }
      g.ground(eng, c.neutron, H * 0.18, 0.14);
      g.poly(eng, c.neutron, 2.5, S.anchor > 0.5 ? 0.45 : 1, S.anchor > 0.5 ? [6, 5] : null);
      // layer 2 ghost: the global rule, when the own-measurement switch is on
      if (S.ms > 0.02 && S.layer === 2) { const gl = []; for (let i = 0; i <= N; i++) { const x = i / N; gl.push([X(x), Y(engine(x))]); } g.poly(gl, c.faint, 1.5, 0.8 * S.ms, [3, 4]); }
      // layer 3: the anchored line
      if (S.anchor > 0.01) { const tl = []; for (let i = 0; i <= N; i++) { const x = i / N; tl.push([X(x), Y(terra(x, S, w))]); } g.poly(tl, c.accent, 3, S.anchor); }
      // the measured window
      if (S.anchor > 0.01 && w[1] > w[0]) {
        g.line(X(Math.max(0, w[0])), bot + (phone ? 10 : 18), X(Math.min(1, w[1])), bot + (phone ? 10 : 18), c.accent, 3, 0.6 * S.anchor);
        g.label("measured here", X(clamp((w[0] + w[1]) / 2, 0.1, 0.9)), bot + (phone ? 24 : 36), { color: c.accent, size: 12, bg: true, alpha: S.anchor });
      }
      // measurements: hollow dots with error bars; in layers 3-4 only those inside the measured window exist
      let shown = 0, inside = 0;
      for (const p of PTS) {
        const exists = S.layer < 3 || (p.x >= w[0] && p.x <= w[1]); if (!exists) continue;
        const a = S.reveal; if (a < 0.02) continue;
        shown++; const m = terra(p.x, S, w); if (Math.abs(p.y - m) <= half(p.x, S, w)) inside++;
        g.line(X(p.x), Y(p.y - p.e), X(p.x), Y(p.y + p.e), c.ink, 1.2, 0.55 * a);
        g.dot(X(p.x), Y(p.y), 4.2, c.paper, a); g.ring(X(p.x), Y(p.y), 4.2, c.ink, 1.6, 0.9 * a);
      }
      S.inside = shown ? Math.round((100 * inside) / shown) : 0;
      // axis words (a landscape, not a chart)
      g.label("neutron energy →", x1, bot + (S.anchor > 0.01 ? (phone ? 44 : 58) : 22), { color: c.faint, size: 12, align: "right" });
      g.label("how often the reaction happens", x0, top - 18, { color: c.faint, size: 12, align: "left" });
      // readouts per layer
      const ry = phone ? H - 14 : H * 0.9, sz = phone ? 12 : 14;
      if (S.layer === 1 && S.reveal > 0.5) g.label("hollow dots: measurements the engine never saw", W / 2, ry, { color: c.ink, size: sz, bg: true });
      if (S.layer === 2) g.label(S.ms > 0.5 ? "own measured values: the line barely moves" : "global rule", W / 2, ry, { color: c.ink, size: sz, bg: true });
      if (S.layer === 3) g.label(S.cov < 0.03 ? "no measurements: TERRA falls back to the engine" : "solid: follows the data · dashed: the engine alone", W / 2, ry, { color: c.ink, size: sz, bg: true });
      if (S.layer === 4 && S.bandOn > 0.5) g.label(shown ? `${inside} of ${shown} measurements inside the band (aim: about 68 %)` : "no measurements to check the band against", W / 2, ry, { color: inside / Math.max(1, shown) > 0.85 ? c.warm : c.ink, size: sz, bg: true });
      drawStack(g, S, phone);
    },
  });

  // the four layers as a small stack of slabs: lit = on in this step
  function drawStack(g, S, phone) {
    const { W, H, c } = g, sw = phone ? Math.min(W * 0.86, 300) : Math.min(260, W * 0.3), sh = phone ? 13 : 18, gap = 3;
    const x = phone ? (W - sw) / 2 : W - sw - W * 0.05, y0 = phone ? 10 : H * 0.06;
    for (let i = 3; i >= 0; i--) {
      const L = LAYERS[i], on = L.n <= S.layer, here = L.n === S.layer, y = y0 + (3 - i) * (sh + gap);
      g.ctx.save(); g.ctx.globalAlpha = on ? (here ? 0.9 : 0.45) : 0.12; g.ctx.fillStyle = c[L.col];
      g.ctx.beginPath(); if (g.ctx.roundRect) g.ctx.roundRect(x, y, sw, sh, 4); else g.ctx.rect(x, y, sw, sh); g.ctx.fill(); g.ctx.restore();
      g.label(`${L.n} · ${L.name}`, x + 8, y + sh / 2 + 0.5, { color: on && here ? c.card : on ? c.ink : c.faint, size: phone ? 10.5 : 12, weight: here ? 600 : 500, align: "left" });
    }
  }
})();
