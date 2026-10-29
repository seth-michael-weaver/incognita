/* Chapter 1: structure (structure/). What the engine knows about a nucleus before any reaction is computed.
 * Scenes (S.mode): "build" = protons and neutrons packed, binding glue;
 *                   "well"  = the cost to pull one particle out (separation energies as the height of a climb);
 *                   "levels" = discrete levels as shelves with spin/parity, continuum above;
 *                   "gamma" = a ball dropped onto a shelf hops down by measured branchings, emitting photons;
 *                   "isomer" = a shelf the nucleus cannot leave quickly (large spin jump);
 *                   "shape" = spherical, vibrating or rotating nucleus and the level pattern each makes;
 *                   "finger" = the resonance forest just above S_n and the three averages read from it.
 * Shapes follow structure/masses.py (separation energies as mass differences), structure/levels.py (levels,
 * branchings, isomers; opt-in levjpar.py), structure/deformation.py (beta2, rotational/vibrational; opt-in collrule.py),
 * structure/resonances.py (D0, S0, Gg).
 * Numbers are illustrative: masses from a liquid-drop formula, levels loosely after 56Fe. */
(function () {
  const { TAU, clamp, lerp, smooth, rng } = WT.util;
  const Z0 = 26;
  // liquid-drop binding energy (MeV); only used so the slider gives believable separation energies
  function bind(Z, N) {
    const A = Z + N; if (A <= 0 || Z <= 0 || N <= 0) return 0;
    const pair = (Z % 2 === 0 && N % 2 === 0) ? 1 : (Z % 2 === 1 && N % 2 === 1) ? -1 : 0;
    return 15.75 * A - 17.8 * Math.pow(A, 2 / 3) - 0.711 * Z * Z / Math.cbrt(A) - 23.7 * (N - Z) * (N - Z) / A + pair * 11.18 / Math.sqrt(A);
  }
  const Sn = (Z, N) => bind(Z, N) - bind(Z, N - 1);
  const Sp = (Z, N) => bind(Z, N) - bind(Z - 1, N);
  const Sa = (Z, N) => bind(Z, N) - bind(Z - 2, N - 2) - 28.3;
  // discrete levels (MeV, J, parity) loosely after 56Fe; branchings are illustrative measured-style tables
  const LV = [
    [0, "0+"], [0.847, "2+"], [2.085, "4+"], [2.658, "2+"], [2.942, "0+"], [3.123, "2+"], [3.370, "3+"], [3.449, "1+"],
    [3.832, "2+"], [4.120, "4+"], [4.510, "3−"], [4.730, "2+"], [5.120, "1−"],
  ];
  const BR = { 12: [[9, 0.4], [6, 0.35], [1, 0.25]], 11: [[8, 0.5], [3, 0.3], [1, 0.2]], 10: [[1, 0.5], [2, 0.3], [5, 0.2]], 9: [[2, 0.7], [1, 0.3]], 8: [[1, 0.6], [0, 0.4]], 7: [[0, 0.5], [1, 0.5]], 6: [[1, 0.4], [2, 0.4], [3, 0.2]], 5: [[1, 0.6], [0, 0.4]], 4: [[1, 1]], 3: [[1, 0.9], [0, 0.1]], 2: [[1, 1]], 1: [[0, 1]] };
  const ECONT = 4.9, SN_SHOW = 11.2;
  // Weisskopf single-particle estimates (per second) for A ~ 56, electric multipole L, photon energy E (MeV)
  function weisskopf(L, E, A) {
    const c = [0, 1.0e14 * Math.pow(A, 2 / 3), 7.3e7 * Math.pow(A, 4 / 3), 34 * A * A, 1.1e-5 * Math.pow(A, 8 / 3), 2.4e-12 * Math.pow(A, 10 / 3)];
    return c[L] * Math.pow(E, 2 * L + 1);
  }
  function fmtTime(s) {
    if (s < 1e-12) return (s * 1e15).toFixed(0) + " femtoseconds";
    if (s < 1e-9) return (s * 1e12).toFixed(0) + " picoseconds";
    if (s < 1e-6) return (s * 1e9).toFixed(0) + " nanoseconds";
    if (s < 1e-3) return (s * 1e6).toFixed(0) + " microseconds";
    if (s < 1) return (s * 1e3).toFixed(0) + " milliseconds";
    if (s < 120) return s.toFixed(1) + " seconds";
    if (s < 7200) return (s / 60).toFixed(0) + " minutes";
    if (s < 2 * 86400) return (s / 3600).toFixed(1) + " hours";
    if (s < 2 * 3.156e7) return (s / 86400).toFixed(0) + " days";
    if (s < 1e6 * 3.156e7) return (s / 3.156e7).toFixed(0) + " years";
    return (s / 3.156e7).toExponential(1).replace("e+", "×10^") + " years";
  }

  /** Ground fill under a profile with its two x-ends faded into the page (no hard box edges). Draw it first in a scene:
   *  the fade erases (destination-out) whatever lies under the ends. */
  function fground(g, pts, color, depth = 140, alpha = 0.3, fade = 60) {
    if (pts.length < 2) return; const ctx = g.ctx; let top = Infinity, bot = -Infinity;
    for (const p of pts) { top = Math.min(top, p[1]); bot = Math.max(bot, p[1]); }
    const maxY = bot + depth, xa = pts[0][0], xb = pts[pts.length - 1][0], f = Math.min(fade, (xb - xa) * 0.3);
    ctx.save(); ctx.beginPath(); ctx.moveTo(xa, maxY); for (const p of pts) ctx.lineTo(p[0], p[1]); ctx.lineTo(xb, maxY); ctx.closePath(); ctx.clip();
    const gr = ctx.createLinearGradient(0, top, 0, maxY); gr.addColorStop(0, g.rgba(color, alpha)); gr.addColorStop(1, g.rgba(color, 0)); ctx.fillStyle = gr;
    ctx.fillRect(xa, top, xb - xa, maxY - top);
    ctx.globalCompositeOperation = "destination-out";
    const gl = ctx.createLinearGradient(xa, 0, xa + f, 0); gl.addColorStop(0, "rgba(0,0,0,1)"); gl.addColorStop(1, "rgba(0,0,0,0)"); ctx.fillStyle = gl; ctx.fillRect(xa, top, f, maxY - top);
    const gq = ctx.createLinearGradient(xb, 0, xb - f, 0); gq.addColorStop(0, "rgba(0,0,0,1)"); gq.addColorStop(1, "rgba(0,0,0,0)"); ctx.fillStyle = gq; ctx.fillRect(xb - f, top, f, maxY - top);
    ctx.restore();
  }

  let seedCounter = 3;

  WT.chapter("structure", {
    num: "Chapter 1", title: "What a nucleus is made of", short: "Structure",
    lead: "Before the engine (our reaction software) fires a single neutron, it needs a description of the target nucleus: how tightly it holds together, which energy states it can be in, and what shape it is.",
    html: `
<div class="step">
  <p>The picture shows an iron nucleus: a packed ball of <em class="p">protons</em> and <em class="n">neutrons</em> (<b>nucleons</b>), held together by the short-range <b>strong force</b>. Each nucleon feels only its nearest neighbours, so every nucleus has about the same density.</p>
  <div class="ctl"><label for="st-n">Neutrons (iron has 26 protons)</label><input id="st-n" type="range" data-bind="N" min="24" max="38" step="1" value="30" data-instant><output data-show="N" data-fmt="0"></output></div>
  <p>Drag to add or remove neutrons; each choice is a different <b>isotope</b>. The bars show the <b>binding energy</b> per nucleon in MeV (million electron-volts): the energy needed to pull the nucleus apart. It peaks near the stable isotopes.</p>
</div>
<div class="step">
  <h3>Separation energies</h3>
  <p>The energy to pull one particle out is its <b>separation energy</b>: <i>S<sub>n</sub></i> for a neutron, <i>S<sub>p</sub></i> for a proton, <i>S<sub>α</sub></i> for an <b>alpha particle</b> (two protons and two neutrons bound together). The picture shows the nucleus as a well, energy going up; each pull lifts the top particle out past the dashed "free" line, and the meter records the cost.</p>
  <div class="btns"><button class="btn ghost" data-act="pn">Pull a neutron</button><button class="btn ghost" data-act="pp">Pull a proton</button><button class="btn ghost" data-act="pa">Pull an alpha</button></div>
  <p>The engine gets each one as the difference of two nuclear masses: measured where possible, from a mass model where not.</p>
  <div class="ctl"><label for="st-n2">Neutrons</label><input id="st-n2" type="range" data-bind="N" min="24" max="38" step="1" value="30" data-instant><output data-show="N" data-fmt="0"></output></div>
  <p>Drag the neutron count and pull a neutron again: <i>S<sub>n</sub></i> zigzags, because nucleons pair up and an even count holds the last one tighter. A reaction can throw out a particle only if it brings enough energy to pay this cost. These costs are the <b>thresholds</b> of the whole calculation.</p>
</div>
<div class="step">
  <h3>Excited states and gamma decay</h3>
  <p>A nucleus can hold only certain exact amounts of extra energy: the lines, here for iron-56, with the <b>ground state</b> at the bottom. Each level has a <b>spin</b> <i>J</i> (angular momentum) and a <b>parity</b>, + or − (whether its wave looks the same in a mirror); 2<sup>+</sup> means spin 2, parity +.</p>
  <p>The orange ball is a nucleus on a high level. It falls one level at a time, each hop throwing off a <em class="g">photon</em> (a gamma ray) that carries the energy difference. The paths' width and percentage are the measured odds of each hop, the <b>branching ratios</b>.</p>
  <div class="btns"><button class="btn" data-act="drop">Excite the nucleus</button></div>
  <p>Press it a few times: the same level reaches the ground state by different routes. The engine keeps about thirty measured levels per nucleus, with their odds; higher up it treats the crowded levels as a smooth <b>continuum</b>. Above the dashed line, <i>S<sub>n</sub></i>, the nucleus can emit a neutron.</p>
</div>
<div class="step">
  <h3>Isomers: long-lived excited states</h3>
  <p>A level whose only way down needs a big spin change, Δ<i>J</i>, decays very slowly. On the right, 64 nuclei sit on such a level; each waits a random time, then drops and a <em class="g">photon</em> pops out. Half have dropped after one <b>half-life</b>.</p>
  <div class="ctl"><label for="st-dj">Spin change ΔJ</label><input id="st-dj" type="range" data-bind="dJ" min="1" max="5" step="1" value="2" data-instant><output data-show="dJ" data-fmt="0"></output></div>
  <div class="ctl"><label for="st-eg">Photon energy (MeV)</label><input id="st-eg" type="range" data-bind="Eg" min="0.05" max="1.5" step="0.05" value="0.3"><output data-show="Eg" data-fmt="2"></output></div>
  <div class="btns"><button class="btn ghost" data-act="excite">Excite them all</button></div>
  <p>Raise Δ<i>J</i> and the popping slows: each extra unit of spin makes the wait a hundred thousand times longer or more, and lower photon energy lengthens it too (shown on a log scale). A level that lives longer than about a second is an <b>isomer</b>, and the engine treats it as an end point, like the ground state.</p>
</div>
<div class="step">
  <h3>Nuclear deformation</h3>
  <p>Many nuclei are not round. <i>β₂</i> ("beta-two") measures the stretch: 0 is a sphere, positive is stretched like an American football, negative is squashed into a disc. The ladder on the right shows the levels each kind makes.</p>
  <p>A stretched nucleus can rotate, giving levels 0<sup>+</sup>, 2<sup>+</sup>, 4<sup>+</sup>, 6<sup>+</sup> with gaps growing like <i>J</i>(<i>J</i>+1): a <b>rotor</b>. A round one can ripple; each unit of ripple, a <b>phonon</b>, adds the same energy, so its levels are evenly spaced: a <b>vibrator</b>.</p>
  <div class="ctl"><label for="st-beta">Deformation β₂</label><input id="st-beta" type="range" data-bind="beta" min="-0.3" max="0.45" step="0.01" value="0.28"><output data-show="beta" data-fmt="2"></output></div>
  <div class="btns"><button class="btn ghost" data-act="still">Still</button><button class="btn ghost" data-act="vib">Vibrating</button><button class="btn ghost" data-act="rot">Rotating</button></div>
  <p>Drag <i>β₂</i> and press the buttons: a bigger stretch pulls the rotor's levels closer. A vibrator is round on average, so the slider rests while it ripples; and a sphere cannot rotate in this sense (turning it changes nothing), so near <i>β₂</i> = 0 the rotor band disappears. The engine stores deformations per nucleus and a tag: spherical, vibrator or rotor. Chapter 6 shows how a passing neutron uses them.</p>
</div>
<div class="step">
  <h3>Resonance parameters above the neutron threshold</h3>
  <p>A slow neutron joining the target lands just above <i>S<sub>n</sub></i>, in the small box on the left. The right panel magnifies that box thousands of times, neutron energy running left to right.</p>
  <div class="ctl"><label for="st-fe">Beam energy</label><input id="st-fe" type="range" data-bind="fe" min="0" max="1" step="0.001" value="0.3" data-instant><output id="st-fe-out"></output></div>
  <div class="btns"><button class="btn ghost" data-act="fplay" id="st-fplay">Pause the sweep</button></div>
  <p>At most energies the beam passes straight through. At certain exact energies the neutron plus the nucleus match a hidden level and much of the beam is taken in: a <b>resonance</b>. On a peak the drawn nucleus swells: not a real change of size, but the bigger target the neutron effectively sees when its wave overlaps the nucleus's. The nucleus then gives the energy back as a <em class="g">photon</em> or a neutron. The curve shows the share taken in; the bars mark each resonance found.</p>
  <div class="btns"><button class="btn ghost" data-act="fFe">Iron-56</button><button class="btn ghost" data-act="fAu">Gold-197</button><button class="btn ghost" data-act="fU">Uranium-238</button></div>
  <p>Each nucleus has its own barcode at its own scale: thousands of electron-volts between iron's resonances, tens for gold and uranium. Three averages sum it up: <i>D₀</i>, the average gap; ⟨Γ<sub>γ</sub>⟩, the <b>photon width</b>, nearly the same for every peak; and <i>S₀</i>, the <b>strength function</b>, how easily a slow neutron gets in.</p>
  <p>Each one checks a later step. The engine's level-density parameters were fitted to <i>D₀</i>, nucleus by nucleus; ⟨Γ<sub>γ</sub>⟩ tests photon emission, <i>S₀</i> the optical model of the next chapter. For unmeasured nuclei the engine uses trends fitted across many nuclei.</p>
  <div class="aside">In the code: <code>structure/masses.py</code> (measured masses, model masses beyond them, separation energies), <code>structure/levels.py</code> (discrete levels, branchings, isomers, guessed spins) and <code>levjpar.py</code> (optional, off by default: re-guesses a listed spin that is impossible for the nucleus), <code>structure/deformation.py</code> (β₂ and the spherical/vibrator/rotor tag) and <code>collrule.py</code> (optional, off by default: picks the target's tag from its measured levels), <code>structure/resonances.py</code> (D₀, S₀, S₁, ⟨Γγ⟩).</div>
</div>`,
    setup(S) {
      S.set("mode", "build"); S.to("N", 30, true); S.to("dJ", 2, true); S.to("Eg", 0.3, true); S.to("beta", 0.28, true);
      S.drops = []; S.to("vibA", 0, true); S.to("rotW", 0, true); S.set("shapeKind", "still"); S.rotAng = 0; S.rotT = null; S.pullK = 0; S.pullT0 = -100; S.marks = [null, null, null]; S.popReq = false; fingerSetup(S); S.betaInp = document.getElementById("st-beta");
      S.on("pn", () => { S.pullK = 0; S.pullT0 = S.time; }); S.on("pp", () => { S.pullK = 1; S.pullT0 = S.time; }); S.on("pa", () => { S.pullK = 2; S.pullT0 = S.time; });
      S.on("excite", () => { S.popReq = true; });
      S.on("drop", () => {
        const r = rng(++seedCounter * 977); const path = [LV.length - 1];
        while (path[path.length - 1] !== 0 && path.length < 12) { const from = path[path.length - 1]; const br = BR[from] || [[0, 1]]; let u = r(), to = br[br.length - 1][0]; for (const [k, p] of br) { if (u < p) { to = k; break; } u -= p; } path.push(to); }
        S.drops.push({ t0: S.time, r, path, photons: [], emitted: 0 }); if (S.drops.length > 3) S.drops.shift();
      });
      S.on("still", () => { S.set("shapeKind", "still"); S.to("vibA", 0); S.to("rotW", 0); });
      S.on("vib", () => { S.set("shapeKind", "vib"); S.to("vibA", 1); S.to("rotW", 0); });
      S.on("rot", () => { S.set("shapeKind", "rot"); S.to("vibA", 0); S.to("rotW", 1); });
    },
    steps: [
      (S) => { S.set("mode", "build"); },
      (S) => { S.set("mode", "well"); if (/[?&]shot=/.test(location.search)) { S.marks = [Sn(Z0, Math.round(S.N)), Sp(Z0, Math.round(S.N)), null]; S.pullK = 2; S.pullT0 = S.time - 1.4; } else { S.pullK = 0; S.pullT0 = S.time; } },
      (S) => { S.set("mode", "gamma"); S.drops = S.drops.filter((d) => d.t0 <= S.time); if (!S.drops.length) S.handlers.drop(); },
      (S) => { S.set("mode", "isomer"); S.popReq = true; },
      (S) => { S.set("mode", "shape"); if (S.shapeKind === "rot") S.to("rotW", 1); else if (S.shapeKind === "vib") S.to("vibA", 1); },
      (S) => { S.set("mode", "finger"); fingerEnter(S); },
    ],
    frame(g, S, dt) {
      switch (S.mode) {
        case "build": return drawBuild(g, S);
        case "well": return drawWell(g, S);
        case "levels": return drawLevels(g, S, false);
        case "gamma": return drawLevels(g, S, true);
        case "isomer": return drawIsomer(g, S);
        case "shape": return drawShape(g, S);
        default: return drawFinger(g, S, dt);
      }
    },
  });

  // ---------- scene 1: packed drop ----------
  function drawBuild(g, S) {
    const { W, H, c } = g; const N = Math.round(S.N), A = Z0 + N;
    const cx = W * 0.5, cy = H * 0.46, R = Math.min(W, H) * 0.2 * Math.cbrt(A / 56);
    g.glow(cx, cy, R * 1.5, c.warm, 0.1);
    g.nucleus(cx, cy, R, { N: A, Z: Z0, seed: 11, t: S.time, jiggle: 0.5 });
    g.label(`${A}Fe`, cx, cy - R - 30, { color: c.ink, size: 22, weight: 600, serif: true });
    g.label(`${Z0} protons · ${N} neutrons`, cx, cy - R - 8, { color: c.soft, size: 13 });
    const B = bind(Z0, N), per = B / A;
    g.label(`binding energy per nucleon: about ${per.toFixed(2)} MeV`, cx, cy + R + 34, { color: c.ink, size: 16, weight: 600, serif: true });
    // a row of small drops: binding per nucleon across the slider range, as a skyline of glue
    const n0 = 24, n1 = 38, x0 = W * 0.14, x1 = W * 0.86, yb = H * 0.9, hmax = H * 0.11;
    const pmax = 8.85, pmin = 8.25;
    for (let n = n0; n <= n1; n++) {
      const x = lerp(x0, x1, (n - n0) / (n1 - n0)), p = bind(Z0, n) / (Z0 + n), h = hmax * clamp((p - pmin) / (pmax - pmin), 0.05, 1);
      const on = n === N;
      g.ctx.save(); g.ctx.globalAlpha = on ? 0.9 : 0.35; g.ctx.fillStyle = on ? c.warm : c.faint; g.ctx.fillRect(x - 5, yb - h, 10, h); g.ctx.restore();
      if (on) { const capY = cy + R + 34, ly = yb - h - 10; if (ly > capY + 14) g.label(`${Z0 + n}`, x, ly, { color: c.warm, size: 11 }); else g.label(`${Z0 + n}`, x + 9, yb - h / 2, { color: c.warm, size: 11, align: "left" }); }   // beside the bar when the caption is close
    }
    g.label("binding per nucleon, one bar per isotope →", x1, yb + 14, { color: c.faint, size: 11, align: "right" });
  }

  // ---------- scene 2: separation energies, pulled out by hand ----------
  const PULL_DUR = 3.0, PULL_GAP = 3.8;
  function drawWell(g, S) {
    const { W, H, c } = g; const N = Math.round(S.N), A = Z0 + N, phone = W < 600;
    const sn = Sn(Z0, N), sp = Sp(Z0, N), sa = Sa(Z0, N), costs = [sn, sp, Math.max(0.3, sa)];
    const yFree = H * 0.22, yFloor = H * 0.82, DMAX = 19.5, ppm = (yFloor - yFree) / DMAX, Y = (d) => yFree + d * ppm;
    const x0 = W * 0.05, x1 = W * (phone ? 0.56 : 0.64), xm = (x0 + x1) / 2, hw = (x1 - x0) / 2;
    // auto-cycle n -> p -> alpha unless the reader picked one
    let u = (S.time - S.pullT0) / PULL_DUR;
    if (S.time - S.pullT0 > PULL_GAP) { S.pullK = (S.pullK + 1) % 3; S.pullT0 = S.time; u = 0; }
    const k = S.pullK, prog = smooth(0.12, 0.7, u);
    // well
    const pts = []; for (let i = 0; i <= 80; i++) { const v = -1 + 2 * i / 80; const depth = 1 / (1 + Math.exp((Math.abs(v) - 0.8) / 0.06)); pts.push([xm + v * hw * 1.18, Y(depth * DMAX)]); }
    { const ctx = g.ctx, gr = ctx.createLinearGradient(0, yFree, 0, yFloor + 40); gr.addColorStop(0, g.rgba(c.soft, 0.02)); gr.addColorStop(1, g.rgba(c.soft, 0.16)); ctx.save(); ctx.fillStyle = gr; ctx.beginPath(); pts.forEach((p, i) => (i ? ctx.lineTo(p[0], p[1]) : ctx.moveTo(p[0], p[1]))); ctx.closePath(); ctx.fill(); ctx.restore(); }
    g.poly(pts, c.ink, 2);
    g.line(x0 - 10, yFree, x1 + 10, yFree, c.faint, 1.2, 0.9, [5, 5]);
    g.label(phone ? "free" : "free: outside the nucleus", x0, yFree - 16, { color: c.faint, size: 12, align: "left" });
    // shelves: neutrons on the left, protons on the right, top shelf at the separation energy
    const cols = [[xm - hw * 0.34, sn, c.neutron, "neutrons"], [xm + hw * 0.34, sp, c.proton, "protons"]];
    const br = Math.max(4.5, Math.min(7, ppm * 0.42));
    cols.forEach(([cx, top, col, nm], j) => {
      for (let s = 0; s < 6; s++) {
        const d = top + s * 2.6; if (d > DMAX - 0.5) break; const y = Y(d), al = 1 - smooth(DMAX - 4, DMAX, d);
        g.line(cx - hw * 0.22, y, cx + hw * 0.22, y, c.soft, 1.2, 0.8 * al);
        const pulled = s === 0 && ((k === j && u < 1.05) || (k === 2));
        const two = !(j === 0 && s === 0 && N % 2 === 1);
        if (!(pulled && k === j)) g.ball(cx - br * 1.3, y - br - 1, br, col, al);
        if (two && !(pulled && k === 2)) g.ball(cx + br * 1.3, y - br - 1, br, col, al);
        else if (two && k === 2 && u > 1.05) g.ball(cx + br * 1.3, y - br - 1, br, col, al);
      }
      g.label(nm, cx, Math.min(Y(top + 2.6 * 5), yFloor) + 18, { color: col, size: 11 });
    });
    // the pulled object
    const startY = k === 2 ? Y(costs[2]) : Y(costs[k]), startX = k === 0 ? cols[0][0] - br * 1.3 : k === 1 ? cols[1][0] - br * 1.3 : xm;
    const lift = lerp(startY - br - 1, yFree - 34, prog), drift = smooth(0.75, 1, u);
    const px = lerp(startX, startX + (k === 1 ? 1 : -1) * W * 0.06, drift) , py = lift - drift * 20;
    if (u < 1.05) {
      { const hy = H * 0.12; g.line(px, hy, px, py - br * 2, c.ink, 1.3, 0.5 * (1 - drift), [3, 3]); g.dot(px, hy, 3.5, c.ink, 0.55 * (1 - drift)); }
      if (k === 2) { [[-1, -1, c.neutron], [1, -1, c.proton], [-1, 1, c.proton], [1, 1, c.neutron]].forEach(([dx, dy, col]) => g.ball(px + dx * br * 0.85, py + dy * br * 0.85, br, col, 1 - smooth(0.9, 1.05, u))); }
      else g.ball(px, py, br * 1.1, k === 0 ? c.neutron : c.proton, 1 - smooth(0.9, 1.05, u));
      if (prog > 0 && prog < 1) g.glow(px, py, 22, c.warm, 0.35);
      if (k === 2 && u < 0.2) g.label("an alpha forms from the top pairs", xm, startY + 22, { color: c.alpha, size: 11, bg: true });
    }
    // energy meter: same scale as the well, so each mark is exactly the climb
    const mx = W * (phone ? 0.7 : 0.82), mw = Math.max(16, W * 0.025), mb = yFloor, mtop = mb - DMAX * ppm, ctx = g.ctx;
    ctx.save(); ctx.strokeStyle = g.rgba(c.soft, 0.7); ctx.lineWidth = 1.5; ctx.beginPath(); if (ctx.roundRect) ctx.roundRect(mx - mw / 2, mtop, mw, mb - mtop, mw / 2); else ctx.rect(mx - mw / 2, mtop, mw, mb - mtop); ctx.stroke(); ctx.restore();
    const fillE = costs[k] * prog * (1 - smooth(1.0, 1.15, u) * 0), colK = [c.neutron, c.proton, c.alpha][k];
    ctx.save(); const gr = ctx.createLinearGradient(0, mb, 0, mb - DMAX * ppm); gr.addColorStop(0, g.rgba(c.warm, 0.85)); gr.addColorStop(1, g.rgba(c.warm, 0.5)); ctx.fillStyle = gr;
    ctx.fillRect(mx - mw / 2 + 3, mb - fillE * ppm, mw - 6, fillE * ppm); ctx.restore();
    if (u >= 0.7) S.marks[k] = costs[k];
    // recorded marks, labels spread so they never collide
    const names = ["neutron", "proton", "alpha"], marks = [0, 1, 2].filter((i) => S.marks[i] !== null).map((i) => ({ i, y: mb - S.marks[i] * ppm, ly: mb - S.marks[i] * ppm }));
    marks.sort((a, b) => a.y - b.y); for (let i = 1; i < marks.length; i++) if (marks[i].ly - marks[i - 1].ly < 17) marks[i].ly = marks[i - 1].ly + 17;
    marks.forEach((m) => { const col = [c.neutron, c.proton, c.alpha][m.i]; g.line(mx - mw / 2 - 6, m.y, mx + mw / 2 + 6, m.y, col, 2.4); g.line(mx + mw / 2 + 6, m.y, mx + mw / 2 + 12, m.ly, col, 1, 0.6); g.label(`${phone ? ["n", "p", "α"][m.i] : names[m.i]} ${S.marks[m.i].toFixed(1)}`, mx + mw / 2 + 14, m.ly, { color: col, size: phone ? 11 : 12, weight: 600, align: "left" }); });
    g.label(phone ? "energy paid" : "energy to pull", mx, mtop - 32, { color: c.soft, size: 12 }); g.label(phone ? "(MeV)" : "each one out (MeV)", mx, mtop - 17, { color: c.soft, size: 12 });
    g.label("higher mark =", mx, mb + 16, { color: c.faint, size: 11 }); g.label("harder to remove", mx, mb + 30, { color: c.faint, size: 11 });
    if (u < 1) g.label(`pulling out ${names[k] === "alpha" ? "an alpha" : "a " + names[k]}: ${(costs[k] * prog).toFixed(1)} MeV paid`, xm, H * 0.06, { color: colK, size: phone ? 13 : 15, weight: 600, serif: true, bg: true });
    else g.label(`${A}Fe`, xm, H * 0.06, { color: c.ink, size: 20, weight: 600, serif: true });
  }

  // ---------- scene 3/4: shelves, with optional gamma cascade ----------
  function levelLayout(g) {
    const { W, H } = g; const phone = W < 600;
    const yBot = phone ? H * 0.84 : H * 0.9, yTop = H * 0.1, Emax = SN_SHOW;
    return { x0: phone ? W * 0.16 : W * 0.24, x1: phone ? W * 0.6 : W * 0.64, Y: (E) => yBot - (yBot - yTop) * E / Emax, yBot, yTop, phone };
  }
  function drawLadder(g, S, L, withCont) {
    const { c } = g; const { x0, x1, Y, phone } = L;
    // walls of the well
    g.line(x0 - 14, Y(0) + 18, x0 - 14, Y(SN_SHOW) - 10, c.line, 2);
    g.line(x1 + 14, Y(0) + 18, x1 + 14, Y(SN_SHOW) - 10, c.line, 2);
    g.line(x0 - 14, Y(0) + 18, x1 + 14, Y(0) + 18, c.line, 2);
    // continuum: a smooth grey wash whose density rises with energy
    if (withCont) {
      const ctx = g.ctx; const yc = Y(ECONT), yt = Y(SN_SHOW);
      const gr = ctx.createLinearGradient(0, yc, 0, yt); gr.addColorStop(0, g.rgba(c.faint, 0.12)); gr.addColorStop(1, g.rgba(c.faint, 0.5));
      ctx.save(); ctx.fillStyle = gr; ctx.fillRect(x0 - 12, yt, x1 - x0 + 24, yc - yt); ctx.restore();
      for (let i = 0; i < 46; i++) { const E = ECONT + (SN_SHOW - ECONT) * Math.pow(i / 46, 0.6); g.line(x0, Y(E), x1, Y(E), c.faint, 0.8, 0.25 + 0.5 * i / 46); }
      g.label("continuum: too many levels to list", (x0 + x1) / 2, Y(ECONT + (SN_SHOW - ECONT) * 0.5), { color: c.soft, size: phone ? 11 : 13, bg: true });
    }
    // spin/parity labels in one column, nudged apart (with a short leader) so close levels never collide
    const gap = phone ? 12 : 13.5, ly = LV.map(([E]) => Y(E));
    for (let it = 0; it < 40; it++) for (let i = 1; i < ly.length; i++) { const d = ly[i - 1] - ly[i]; if (d < gap) { const m = (gap - d) / 2; ly[i - 1] += m; ly[i] -= m; } }
    LV.forEach(([E, jp], i) => {
      const y = Y(E); g.line(x0, y, x1, y, i === 0 ? c.ink : c.soft, i === 0 ? 2.5 : 1.6, 0.95);
      if (Math.abs(ly[i] - y) > 1) g.line(x1 + 2, y, x1 + 16, ly[i], c.faint, 1, 0.7);
      g.label(jp, x1 + 20, ly[i], { color: c.soft, size: phone ? 11 : 12, align: "left" });
      if (!phone && [0, 1, 2, 3, 10].includes(i)) g.label(`${E.toFixed(2)}`, x0 - 22, y, { color: c.faint, size: 11, align: "right" });
    });
    g.line(x0 - 14, Y(SN_SHOW), x1 + 14, Y(SN_SHOW), c.neutron, 1.5, 0.9, [5, 4]);
    g.label(`neutron threshold Sₙ ≈ ${SN_SHOW} MeV`, (x0 + x1) / 2, Y(SN_SHOW) - 12, { color: c.neutron, size: phone ? 11 : 12, bg: true });
    if (phone) g.label("ground state", (x0 + x1) / 2, Y(0) + 10, { color: c.ink, size: 11, bg: true });
    else { g.label("ground state", x0 - 22, Y(0) + 14, { color: c.ink, size: 11, align: "right" }); g.label("MeV", x0 - 22, Y(0) + 30, { color: c.faint, size: 10, align: "right" }); }
  }
  function drawLevels(g, S, withGamma) {
    const { W, H, c } = g; const L = levelLayout(g);
    drawLadder(g, S, L, true);
    if (!withGamma) { g.label("each line: an energy, a spin J and a parity (±)", (L.x0 + L.x1) / 2, L.Y(0) + 40, { color: c.soft, size: 13, serif: true, italic: true }); return; }
    const { x0, x1, Y } = L; const xm = (x0 + x1) / 2;
    // branches of the top level drawn faintly as a reference (width = branching)
    const now = S.time;
    const drops = S.drops || (S.drops = []), last = drops.length - 1;
    drops.forEach((d, di) => {
      const r = d.r; const age = Math.max(0, now - d.t0); const hop = 0.75;
      const k = clamp(Math.floor(age / hop), 0, d.path.length - 1), f = clamp((age - k * hop) / (hop * 0.45), 0, 1);
      // each hop that has begun emits one photon
      while (d.emitted < k && d.emitted < d.path.length - 1) { const to = d.path[d.emitted + 1]; d.photons.push({ y1: Y(LV[to][0]), t: now, a: (r() - 0.5) * 1.2 + (di % 2 ? Math.PI : 0) }); d.emitted++; }
      const from = d.path[k], to = d.path[Math.min(k + 1, d.path.length - 1)];
      if (!LV[from] || !LV[to]) return;
      const y = lerp(Y(LV[from][0]), Y(LV[to][0]), smooth(0, 1, f)), xoff = (di - last) * 26, newest = di === last;
      // the branches open from the current shelf, width = odds; only the newest ball gets percentages (no stacked labels)
      if (k < d.path.length - 1) {
        const labs = [];
        (BR[from] || []).forEach(([t, p], bi) => {
          const yf = Y(LV[from][0]), yt = Y(LV[t][0]), bul = 34 + bi * 30, ctx = g.ctx;
          ctx.save(); ctx.globalAlpha = newest ? 0.45 : 0.18; ctx.strokeStyle = c.photon; ctx.lineWidth = 1 + 7 * p; ctx.lineCap = "round"; ctx.beginPath(); ctx.moveTo(xm + xoff + 6, yf); ctx.quadraticCurveTo(xm + xoff + 6 + bul, (yf + yt) / 2, xm + xoff + 6, yt); ctx.stroke(); ctx.restore();
          if (newest) labs.push({ x: xm + xoff + 6 + bul * 0.5, y: (yf + yt) / 2, s: `${Math.round(p * 100)}%` });
        });
        labs.sort((a, b) => a.y - b.y); for (let i = 1; i < labs.length; i++) if (labs[i].y - labs[i - 1].y < 16) labs[i].y = labs[i - 1].y + 16;
        labs.forEach((l) => g.label(l.s, l.x, l.y, { color: c.photon, size: 10, bg: true }));
      }
      g.glow(xm + xoff, y - 8, 22, c.warm, newest ? 0.4 : 0.2); g.ball(xm + xoff, y - 8, 9, c.warm, newest ? 1 : 0.55);
    });
    drops.forEach((d, di) => d.photons.forEach((p) => {
      const age = now - p.t; if (age > 1.2 || age < 0) return; const u = smooth(0, 1.2, age);
      const x = xm + (di - last) * 26 + Math.cos(p.a) * (30 + u * W * 0.3), y = p.y1 - 8 + Math.sin(p.a) * u * 80;
      g.photon(x, y, p.a, 24, 1 - u * 0.9);
    }));
    g.label("path width and % = measured odds of each hop", xm, Y(0) + 40, { color: c.soft, size: 13, serif: true, italic: true });
  }

  // ---------- scene 5: isomer, a population of excited nuclei ----------
  const POP = 64, pop = []; let popHalf = -1, popRand = rng(91), popRefillAt = 0;
  function visHalf(half) { return clamp(0.35 * Math.pow(1.9, Math.log10(Math.max(half, 1e-16)) + 13), 0.25, 1e5); }
  function exciteAll(S) { pop.length = 0; const vh = visHalf(popHalf); for (let i = 0; i < POP; i++) pop.push({ at: S.time + 0.3 - Math.log(1 - popRand()) * vh / Math.LN2, t: null }); }
  function drawIsomer(g, S) {
    const { W, H, c } = g; const phone = W < 600;
    const dJ = Math.round(S.dJ), Eg = S.Eg, rate = weisskopf(dJ, Eg, 56), half = Math.LN2 / rate;
    if (popHalf < 0 || Math.abs(Math.log10(half) - Math.log10(popHalf)) > 0.2 || S.popReq) {
      const vh = visHalf(half); popHalf = half; if (!pop.length || S.popReq) exciteAll(S); else pop.forEach((p) => { if (p.t === null) p.at = S.time + 0.1 - Math.log(1 - popRand()) * vh / Math.LN2; }); S.popReq = false;
    }
    // small level pair on the left
    const lx0 = W * 0.06, lx1 = W * (phone ? 0.3 : 0.3), yG = H * 0.72, yI = yG - H * 0.4 * clamp(Eg / 1.5, 0.12, 1);
    g.line(lx0, yG, lx1, yG, c.ink, 2.5); g.label("ground", (lx0 + lx1) / 2, yG + 16, { color: c.ink, size: 12 }); g.label("J = 1/2", (lx0 + lx1) / 2, yG + 31, { color: c.soft, size: 11 });
    g.line(lx0, yI, lx1, yI, c.warm, 2); g.label(`J = ${2 * dJ + 1}/2`, (lx0 + lx1) / 2, yI - 14, { color: c.warm, size: 12 });
    g.arrow((lx0 + lx1) / 2, yI + 6, (lx0 + lx1) / 2, yG - 6, c.photon, clamp(6 - dJ, 1, 5), 0.9);
    g.label(`ΔJ = ${dJ}`, (lx0 + lx1) / 2 + 10, (yI + yG) / 2, { color: c.photon, size: 12, align: "left", bg: true });
    // the population
    const gx0 = W * (phone ? 0.38 : 0.4), gx1 = W * 0.96, gy0 = H * 0.16, gy1 = H * 0.76, cols = 8, rows = POP / cols;
    const sx = (gx1 - gx0) / cols, sy = (gy1 - gy0) / rows, r = Math.min(sx, sy) * 0.28;
    let alive = 0; const now = S.time;
    pop.forEach((p, i) => {
      const x = gx0 + (i % cols + 0.5) * sx, y = gy0 + (Math.floor(i / cols) + 0.5) * sy;
      if (p.t === null && now >= p.at) p.t = now;
      if (p.t === null) { alive++; g.glow(x, y, r * 2.4, c.warm, 0.4 + 0.1 * Math.sin(now * 3 + i)); g.ball(x, y, r, c.warm); }
      else { g.ball(x, y, r * 0.8, c.faint, 0.45); const a = now - p.t; if (a < 0.9) { const ang = (i * 2.4) % TAU; g.photon(x + Math.cos(ang) * (r + a * 60), y + Math.sin(ang) * (r + a * 60), ang, 20, 1 - a / 0.9); g.glow(x, y, r * 2, c.photon, 0.5 * (1 - a / 0.9)); } }
    });
    if (alive <= POP * 0.05 && !popRefillAt) popRefillAt = now + 1.5;
    if (popRefillAt && now > popRefillAt) { popRefillAt = 0; exciteAll(S); }
    g.label(`still excited: ${alive} of ${POP}`, (gx0 + gx1) / 2, gy0 - 22, { color: c.ink, size: phone ? 12 : 14, weight: 600, bg: true });
    g.label(`half-life about ${fmtTime(half)}`, W * 0.5, H * 0.86, { color: c.ink, size: phone ? 15 : 18, weight: 600, serif: true, bg: true });
    g.label(half > 1 ? "longer than a second: an isomer, a stop in its own right" : phone ? "shown slowed down (log scale)" : "shown slowed down: the slower they pop, the longer the real wait (log scale)", W * 0.5, H * 0.92, { color: half > 1 ? c.warm : c.soft, size: phone ? 11 : 13, serif: true, italic: true });
  }

  // ---------- scene 6: shape ----------
  function drawShape(g, S) {
    const { W, H, c } = g; const phone = W < 600;
    const beta = S.beta, vibA = S.vibA, rotW = S.rotW;
    const cx = phone ? W * 0.34 : W * 0.36, cy = H * 0.46, R = Math.min(W, H) * (phone ? 0.2 : 0.2);
    const vib = vibA * 0.22 * Math.sin(S.time * 4.2);
    // integrate the angle so easing rotW in/out never makes the spin jump
    // a vibrator is round on average, so the stretch slider has nothing to set while it vibrates
    if (S.betaInp) { const off = S.shapeKind === "vib"; if (S.betaInp.disabled !== off) { S.betaInp.disabled = off; const row = S.betaInp.closest && S.betaInp.closest(".ctl"); if (row) row.style.opacity = off ? "0.45" : ""; } }
    // a sphere has no orientation to turn: collective rotation needs a stretch, so the spin fades out as beta goes to 0
    const canRot = smooth(0.03, 0.07, Math.abs(beta)), sphereRot = S.shapeKind === "rot" && canRot < 0.5;
    const dtr = S.rotT === null ? 0 : Math.min(0.1, Math.max(0, S.time - S.rotT)); S.rotT = S.time; S.rotAng += rotW * canRot * dtr * 1.1;
    const rot = S.rotAng;
    const b = beta * (1 - vibA) + vib;
    g.glow(cx, cy, R * 1.6, c.warm, 0.08);
    g.nucleus(cx, cy, R, { N: 150, Z: 62, seed: 5, t: S.time, beta: b, rot, jiggle: 0.35 });
    const kind = S.shapeKind;
    const what = vibA > 0.5 ? "ripples at the surface: a vibrator" : sphereRot ? "a sphere cannot rotate: no turn to see" : rotW > 0.5 ? "stretched and rotating: a rotor" : Math.abs(beta) < 0.05 ? "round: a sphere" : beta > 0 ? "stretched (prolate): a football" : "squashed: an oblate disc";
    g.label(what, cx, cy + R * 1.5 + 30, { color: c.ink, size: phone ? 13 : 16, weight: 600, serif: true });
    // level pattern on the right
    const x0 = phone ? W * 0.62 : W * 0.62, x1 = phone ? W * 0.8 : W * 0.8, yb = H * 0.84, yt = H * 0.14;
    const dom = rotW > 0.5 && !sphereRot ? "rot" : vibA > 0.5 ? "vib" : "sph"; const rotMix = dom === "rot" ? rotW * canRot : 0, vibMix = dom === "vib" ? vibA : 0, sphMix = dom === "sph" ? (sphereRot ? 1 : clamp(1 - rotW - vibA, 0, 1)) : 0;
    g.line(x0, yb, x1, yb, c.ink, 2.5); g.label("0⁺", x1 + 6, yb, { color: c.ink, size: 12, align: "left" });
    // rotor: E_J = k J(J+1), k set so that 6+ reaches ~80% height when beta is big; k shrinks with beta (larger moment of inertia)
    const kRot = (yb - yt) / 42 * clamp(0.3 / Math.max(Math.abs(beta), 0.08), 0.5, 2.2) * 0.9;
    if (rotMix > 0.02) for (let J = 2; J <= 6; J += 2) { const y = yb - kRot * J * (J + 1); if (y < yt) continue; g.line(x0, y, x1, y, c.soft, 1.6, rotMix); g.label(`${J}⁺`, x1 + 6, y, { color: c.soft, size: 12, align: "left", alpha: rotMix }); }
    if (vibMix > 0.02) { const dyv = (yb - yt) / 3.4; [[1, "2⁺"], [2, "0⁺ 2⁺ 4⁺"], [3, "3 phonons"]].forEach(([n, s]) => { const y = yb - dyv * n; for (let k = 0; k < (n === 2 ? 3 : 1); k++) g.line(x0, y + (k - 1) * 5, x1, y + (k - 1) * 5, c.soft, 1.6, vibMix); g.label(s, x1 + 6, y, { color: c.soft, size: 12, align: "left", alpha: vibMix }); }); }
    if (sphMix > 0.02) { g.label("no regular", (x0 + x1) / 2, (yb + yt) / 2 - 8, { color: c.faint, size: 12, alpha: sphMix }); g.label("level pattern", (x0 + x1) / 2, (yb + yt) / 2 + 10, { color: c.faint, size: 12, alpha: sphMix }); }
    g.label(rotMix > 0.5 ? "spacing grows like J(J+1)" : vibMix > 0.5 ? "equal steps, one phonon each" : "its lowest levels", (x0 + x1) / 2, yt - 16, { color: c.soft, size: phone ? 11 : 12, bg: true });
    g.label(vibA > 0.5 ? "β₂ set aside: round on average while it ripples" : `β₂ = ${beta.toFixed(2)}`, cx, cy - R * 1.4 - 18, { color: c.soft, size: 13 });
  }

  // ---------- scene 7: the resonance fingerprint, measured by sweeping a beam's energy ----------
  // Left: the level ladder of the compound nucleus (target + n) up past Sn, with a box at Sn magnified into the right panel.
  // Right: a beam at one energy hits the nucleus; the share taken in is recorded against energy (a time-of-flight scan).
  // Resonance ladders follow structure/resonances.py's statistics: Wigner spacings around D0, Porter-Thomas reduced
  // neutron widths (S0*D0*x^2, times sqrt(E) for s-waves), nearly constant photon widths. Averages are about right.
  const FT = {
    Fe: { tgt: "iron-56", cn: "iron-57", Z: 26, A: 56, Sn: 7.646, D0: 25000, Gg: 1.0, S0: 2.2e-4, span: 150000, keV: true, Ec: 2.4, seed: 5602, thick: 1.0 },
    Au: { tgt: "gold-197", cn: "gold-198", Z: 79, A: 197, Sn: 6.512, D0: 15.8, Gg: 0.125, S0: 1.7e-4, span: 200, keV: false, Ec: 0.55, seed: 19707 },
    U: { tgt: "uranium-238", cn: "uranium-239", Z: 92, A: 238, Sn: 4.806, D0: 20.9, Gg: 0.023, S0: 1.0e-4, span: 250, keV: false, Ec: 0.32, seed: 23811 },
  };
  const FNB = 360, FSWEEP = 64, FSHOT = /[?&]shot=/.test(location.search), FSHOT_T = "U";
  function gauss(r) { return Math.sqrt(-2 * Math.log(1 - r() * 0.999999)) * Math.cos(TAU * r()); }
  function buildFT(T) {
    const r = rng(T.seed), res = [];
    let E = T.D0 * (0.25 + 0.5 * r());
    while (E < T.span * 0.985) {
      const x = gauss(r), Gn = T.S0 * T.D0 * x * x * Math.sqrt(E), Gg = T.Gg * (0.9 + 0.2 * r());
      res.push({ E, Gn, Gg, G: Gn + Gg, h: Gn / (Gn + Gg), fa: 0, found: false });
      E += T.D0 * Math.sqrt(-4 / Math.PI * Math.log(1 - r() * 0.999)); // Wigner spacing: neighbours repel
    }
    const Gs = res.map((q) => q.G).sort((a, b) => a - b), hs = res.map((q) => q.h).sort((a, b) => a - b);
    T.X = Math.max(1, 0.08 * T.D0 / Gs[Gs.length >> 1]); // drawn wider than life so a peak spans a few pixels
    T.tau = (T.thick || 0.55) / Math.max(hs[hs.length >> 1], 1e-3); // sample thickness: a median peak takes in about 40% of the beam
    res.forEach((q) => { q.Gd = q.G * T.X; q.P = 1 - Math.exp(-T.tau * q.h); q.bin = Math.min(FNB - 1, Math.floor(q.E / T.span * FNB)); });
    T.res = res; T.lv = []; const rl = rng(T.seed + 7); // counted low levels, crowding upward
    for (let k = 1; k <= 16; k++) T.lv.push(T.Ec * Math.log(1 + k + 0.6 * (rl() - 0.5)) / Math.log(17.3));
    return T;
  }
  Object.values(FT).forEach(buildFT);
  /** Chance that one beam neutron at energy E (eV) is taken in by the sample (thin-sample Breit-Wigner sum, saturating). */
  function fCatch(T, E) {
    let s = 0; for (const q of T.res) { const d = (E - q.E) / (q.Gd / 2); if (d > -40 && d < 40) s += q.h / (1 + d * d); }
    return 1 - Math.exp(-T.tau * s);
  }
  function fNear(T, E) { let b = null, bd = Infinity; for (const q of T.res) { const d = Math.abs(E - q.E) / q.Gd; if (d < bd) { bd = d; b = q; } } return b; }
  function fmtE(T, e, dec) { return T.keV ? (e / 1000).toFixed(dec ?? (e < 9950 ? 1 : 0)) + " keV" : e.toFixed(dec ?? (e < 9.95 ? 2 : 1)) + " eV"; }
  function fmtMag(m) { return m >= 1e6 ? (m / 1e6).toFixed(1) + " million" : m >= 1e4 ? Math.round(m / 1000) + " thousand" : m >= 1000 ? Math.round(m / 100) * 100 + "" : Math.round(m) + ""; }

  function fingerSetup(S) {
    S.ft = "U"; S.fplay = true; S.fpass = 0; S.fbins = []; S.fprev = -1; S.fbeam = []; S.flast = []; S.fnext = 0; S.fT0 = -100; S.fhalo = 0; S.fr = rng(77);
    const inp = document.getElementById("st-fe"), btn = document.getElementById("st-fplay");
    S.fInp = inp; S.fOut = document.getElementById("st-fe-out"); S.fBtn = btn;
    const setPlay = (v) => { S.fplay = v; if (btn) btn.textContent = v ? WT.ui("pause_sweep", "Pause the sweep") : WT.ui("play_sweep", "Play the sweep"); };
    S.fSetPlay = setPlay;
    if (inp) inp.addEventListener("input", () => setPlay(false));
    S.on("fplay", () => setPlay(!S.fplay));
    const pick = (k) => () => { fingerLoad(S, k, 0.3); S.fT0 = S.time; setPlay(true); };
    S.on("fFe", pick("Fe")); S.on("fAu", pick("Au")); S.on("fU", pick("U"));
  }
  /** Switch target and pre-measure the trace up to fraction `upto` (seeded, so the picture is never empty). */
  function fingerLoad(S, k, upto) {
    const T = FT[k], r = rng(T.seed + 3); S.ft = k; S.fpass = 0; S.fbeam.length = 0; S.flast.length = 0;
    S.fbins = []; for (let i = 0; i < FNB; i++) S.fbins.push({ n: 0, h: 0, pass: 0 });
    T.res.forEach((q) => { q.found = false; q.fa = 0; });
    const nb = Math.floor(upto * FNB);
    for (let i = 0; i < nb; i++) { const P = fCatch(T, (i + 0.5) / FNB * T.span), n = 120; S.fbins[i].n = n; S.fbins[i].h = clamp(Math.round(P * n + gauss(r) * Math.sqrt(n * P * (1 - P))), 0, n); }
    T.res.forEach((q) => { if (q.bin < nb) { q.found = true; q.fa = 1; } });
    S.set("fe", upto); S.fprev = nb - 1; S.fanA = 0;
    // a beam already in flight, and a recent tally, so the scene is alive on arrival
    const rb = rng(T.seed + 9), P0 = fCatch(T, upto * T.span), q0 = fNear(T, upto * T.span);
    for (let k = 14; k >= 1; k--) S.fbeam.push({ t0: S.time - k * 0.15, y: (rb() - 0.5) * 30, hit: (k === 9 && P0 > 0.3) || rb() < P0, gam: q0 ? (k === 9 && q0.Gg / q0.G > 0.25) || rb() < q0.Gg / q0.G : true, ang: rb() * TAU, counted: k * 0.15 > 0.9 });
    for (let k = 0; k < 20; k++) S.flast.push(rb() < P0);
  }
  function fingerEnter(S) {
    S.fT0 = FSHOT ? S.time - 10 : S.time;
    if (FSHOT) { // mid-sweep: paused on a strong peak in the middle of the strip
      const T = FT[FSHOT_T]; let best = T.res[0]; T.res.forEach((q) => { const f = q.E / T.span; if (f > 0.4 && f < 0.7 && q.P * (0.3 + q.Gg / q.G) > (best.E / T.span > 0.4 && best.E / T.span < 0.7 ? best.P * (0.3 + best.Gg / best.G) : -1)) best = q; });
      fingerLoad(S, FSHOT_T, best.E / T.span + 0.004); S.set("fe", best.E / T.span); S.fSetPlay(false); S.fanA = 1;
    } else if (!S.fbins.length || S.fbins.every((b) => !b.n)) { fingerLoad(S, S.ft, 0.3); S.fSetPlay(true); }
  }

  function drawFinger(g, S, dt) {
    const { W, H, c } = g, ctx = g.ctx, phone = W < 600, T = FT[S.ft], fs = phone ? 10.5 : 12;
    if (!S.fbins.length) fingerLoad(S, S.ft, 0.3);
    dt = dt || 0;
    // ---- sweep and measurement (many virtual neutrons per bin, a few drawn) ----
    if (S.fplay) { let f = S.fe + dt / FSWEEP; if (f > 1.06) { f = 0; S.fpass++; S.fprev = -1; } S.set("fe", f); }
    const fe = clamp(S.fe, 0, 1), Eb = fe * T.span, cur = Math.min(FNB - 1, Math.floor(fe * FNB)), r = S.fr;
    if (fe <= 1) {
      const a = S.fprev < 0 ? cur : S.fprev, lo = Math.min(a, cur), hi = Math.max(a, cur), many = hi - lo > 0;
      for (let i = lo; i <= hi; i++) {
        const b = S.fbins[i]; if (b.pass !== S.fpass) { b.pass = S.fpass; b.n = 0; b.h = 0; }
        const E = (i + (i === cur && !many ? fe * FNB - i : r())) / FNB * T.span, P = fCatch(T, E), m = many ? 10 : 24;
        for (let k = 0; k < m; k++) if (r() < P) b.h++; b.n += m;
        for (const q of T.res) if (q.bin === i) q.found = true;
      }
      S.fprev = cur;
    }
    let cov = 0; for (const b of S.fbins) if (b.n) cov++; cov /= FNB;
    T.res.forEach((q) => { if (q.found) q.fa = Math.min(1, q.fa + dt * 2.5); });
    // DOM: slider follows the sweep, readout shows the energy with its unit
    if (S.fInp && S.fplay) S.fInp.value = fe.toFixed(3);
    if (S.fOut) { const s = fmtE(T, Eb); if (S.fOut.textContent !== s) S.fOut.textContent = s; }

    // ---- layout ----
    const open = smooth(0, 1, (S.time - S.fT0) / 1.1);
    const lx0 = W * 0.045, lx1 = W * (phone ? 0.15 : 0.15), yBot = H * (phone ? 0.86 : 0.9), yTop = H * 0.13, Emax = T.Sn * 1.16;
    const LY = (E) => yBot - (yBot - yTop) * E / Emax, ySn = LY(T.Sn);
    const ix0 = W * (phone ? 0.3 : 0.27), ix1 = W * 0.965, iw = ix1 - ix0;
    const tTop = H * 0.43, tBase = H * 0.7, th = (tBase - tTop) * 0.92, bTop = tBase + 5, bBot = tBase + H * 0.055;
    const X = (E) => ix0 + E / T.span * iw;
    // ---- left: level ladder of the compound nucleus ----
    g.label(`${T.cn} levels`, lx0 - 4, H * 0.055, { color: c.ink, size: fs + 1, weight: 600, align: "left" });
    {
      const yc = LY(T.Ec), yt = LY(Emax), gr = ctx.createLinearGradient(0, yc, 0, yt);
      gr.addColorStop(0, g.rgba(c.faint, 0.08)); gr.addColorStop(0.85, g.rgba(c.faint, 0.42)); gr.addColorStop(1, g.rgba(c.faint, 0));
      ctx.save(); ctx.fillStyle = gr; ctx.fillRect(lx0, yt, lx1 - lx0, yc - yt); ctx.restore();
      for (let i = 0; i < 30; i++) { const E = T.Ec + (Emax - T.Ec) * Math.pow(i / 30, 0.55); g.line(lx0, LY(E), lx1, LY(E), c.faint, 0.7, (0.2 + 0.45 * i / 30) * (1 - smooth(0.9, 1, E / Emax))); }
    }
    g.line(lx0, yBot, lx1, yBot, c.ink, 2.4);
    T.lv.forEach((E) => g.line(lx0, LY(E), lx1, LY(E), c.soft, 1.1, 0.85));
    g.label("ground state", lx0 - 4, yBot + 15, { color: c.soft, size: fs - 0.5, align: "left" });
    if (!phone) g.label("continuum", (lx0 + lx1) / 2, LY((T.Ec + T.Sn) / 2), { color: c.soft, size: 11, bg: true });
    g.line(lx0 - 6, ySn, lx1 + 6, ySn, c.ink, 1.3, 0.8, [5, 4]);
    g.label(`Sₙ ≈ ${T.Sn.toFixed(1)} MeV`, lx0 - 4, ySn + 15, { color: c.ink, size: fs - 0.5, weight: 600, align: "left", bg: true });
    g.label(phone ? "slow neutron" : "a slow neutron lands here:", lx0 - 4, ySn - 31, { color: c.accent, size: fs - 0.5, weight: 600, align: "left" });
    g.label(phone ? "lands here" : "Sₙ + its kinetic energy", lx0 - 4, ySn - 17, { color: c.accent, size: fs - 0.5, weight: 600, align: "left" });
    // the box (its true height is far below a pixel) and the magnifier wedge to the panel
    const bh = 7, bx0 = lx0 - 3, bx1 = lx1 + 3, pT = tTop - 8, pB = bBot + 6;
    const wx = lerp(bx1, ix0 - 8, open), wT = lerp(ySn - bh, pT, open), wB = lerp(ySn, pB, open);
    { const gr = ctx.createLinearGradient(bx1, 0, ix0, 0); gr.addColorStop(0, g.rgba(c.accent, 0.2)); gr.addColorStop(1, g.rgba(c.accent, 0.05));
      ctx.save(); ctx.fillStyle = gr; ctx.beginPath(); ctx.moveTo(bx1, ySn - bh); ctx.lineTo(wx, wT); ctx.lineTo(wx, wB); ctx.lineTo(bx1, ySn); ctx.closePath(); ctx.fill(); ctx.restore(); }
    g.line(bx1, ySn - bh, wx, wT, c.accent, 1, 0.55); g.line(bx1, ySn, wx, wB, c.accent, 1, 0.55);
    ctx.save(); ctx.strokeStyle = c.accent; ctx.lineWidth = 1.6; ctx.fillStyle = g.rgba(c.accent, 0.25); ctx.beginPath(); if (ctx.roundRect) ctx.roundRect(bx0, ySn - bh, bx1 - bx0, bh, 2); else ctx.rect(bx0, ySn - bh, bx1 - bx0, bh); ctx.fill(); ctx.stroke(); ctx.restore();
    const mag = (iw / T.span) / ((yBot - yTop) / (Emax * 1e6));
    if (open > 0.5) {
      const mx = lerp(bx1, ix0, 0.5), my = lerp((ySn - bh / 2), (pT + pB) / 2, 0.5);
      if (phone) g.label(`×${fmtMag(mag)}`, lx0 - 4, ySn + 33, { color: c.accent, size: fs, weight: 700, align: "left", bg: true, alpha: smooth(0.5, 1, open) });
      else g.label(`×${fmtMag(mag)}`, mx, my, { color: c.accent, size: fs + 1, weight: 700, bg: true, alpha: smooth(0.5, 1, open) });
      if (!phone) g.label("magnified", mx, my + 17, { color: c.accent, size: 11, bg: true, alpha: smooth(0.5, 1, open) });
    }
    if (open < 1) ctx.globalAlpha = open;
    // soft panel behind the magnified strip (no hard edge)
    { const gr = ctx.createLinearGradient(0, pT, 0, pB); gr.addColorStop(0, g.rgba(c.accent, 0)); gr.addColorStop(0.15, g.rgba(c.accent, 0.05)); gr.addColorStop(0.85, g.rgba(c.accent, 0.05)); gr.addColorStop(1, g.rgba(c.accent, 0)); ctx.save(); ctx.fillStyle = gr; ctx.fillRect(ix0 - 8, pT, iw + 16, pB - pT); ctx.restore(); }

    // ---- right top: the beam and the nucleus ----
    const yB = H * 0.175, nx = ix0 + iw * 0.6, R = Math.max(14, Math.min(28, H * 0.038)), sx = ix0 + 4;
    g.label(`beam of neutrons at ${fmtE(T, Eb)}`, phone ? ix1 : sx, H * 0.055, { color: c.ink, size: fs + 1, weight: 600, align: phone ? "right" : "left" });
    // launch: one drawn neutron every ~0.15 s, its fate drawn from the same catch chance
    if (S.time > S.fnext) {
      S.fnext = S.time + 0.15; const P = fCatch(T, Eb), q = fNear(T, Eb);
      S.fbeam.push({ t0: S.time, y: (r() - 0.5) * R * 1.1, hit: r() < P, gam: q ? r() < q.Gg / q.G : true, ang: r() * TAU, counted: false });
      if (S.fbeam.length > 40) S.fbeam.shift();
    }
    const fly = 0.9;
    // effective size: the drawn radius swells with the cross section at the marker's energy (wave overlap at a
    // resonance, not a real size change). Peak sum sampled across this frame's sweep step so no peak is skipped;
    // slow attack, slower release, 1x to 1.6x.
    {
      const e0 = S.fEprev != null && Math.abs(Eb - S.fEprev) < 0.05 * T.span ? S.fEprev : Eb, n = Math.min(24, 2 + Math.ceil(Math.abs(Eb - e0) / (T.X * T.Gg * 0.25 + 1e-9)));
      let s = 0; for (let k = 0; k <= n; k++) { const E = lerp(e0, Eb, k / n); let v = 0; for (const q of T.res) { const d = (E - q.E) / (q.Gd / 2); if (d > -40 && d < 40) v += q.h / (1 + d * d); } s = Math.max(s, v); }
      if (!T.hRef) { const hs = T.res.map((q) => q.h).sort((a, b) => a - b); T.hRef = hs[hs.length >> 1] || 1; }
      const goal = 1 + 0.6 * clamp(Math.pow(s / T.hRef, 0.5), 0, 1), cur0 = S.fswell || 1;
      S.fswell = cur0 + (goal - cur0) * Math.min(1, dt / (goal > cur0 ? 0.3 : 1.0)); S.fEprev = Eb;
    }
    const Rv = R * S.fswell;
    g.glow(nx, yB, Rv * 2.6, c.warm, 0.12 + 0.4 * S.fhalo);
    S.fhalo = Math.max(0, S.fhalo - dt * 1.6);
    g.nucleus(nx, yB, Rv, { N: 34, Z: 14, seed: 9, t: S.time, jiggle: 0.4 + 1.2 * S.fhalo });
    for (const n of S.fbeam) {
      const age = S.time - n.t0, u = age / fly, x = lerp(sx + 10, nx - Rv * 0.6, u), y = yB + n.y * (1 - smooth(0.6, 1, u) * (n.hit ? 1 : 0));
      if (u >= 1 && !n.counted) { n.counted = true; S.flast.push(n.hit); if (S.flast.length > 20) S.flast.shift(); if (n.hit) S.fhalo = Math.min(1, S.fhalo + 0.5); }
      if (!n.hit) { const xx = lerp(sx + 10, nx - R * 0.6, u); if (xx < ix1) g.ball(xx, y, 4, c.neutron, 0.9 * (1 - smooth(0.85, 1, (xx - ix0) / iw))); continue; }
      if (u < 1) { g.ball(x, y, 4, c.neutron, 0.95); continue; }
      const e = age - fly - 0.25; // after a short stay, the energy leaves as a photon or the neutron is thrown back out
      if (e < 0 || e > 1.2) continue;
      const d = Rv + e * iw * 0.26, px = nx + Math.cos(n.ang) * d, py = yB + Math.sin(n.ang) * d * 0.5, fa = 1 - smooth(0.6, 1.2, e);
      if (e < 0.25) g.glow(nx, yB, R * 1.8, n.gam ? c.photon : c.neutron, 0.45 * (1 - e / 0.25));
      if (n.gam) g.photon(px, py, n.ang, 26, fa); else g.ball(px, py, 4, c.neutron, fa);
    }
    const nIn = S.flast.filter(Boolean).length;
    const yTk = yB + R * 1.6 + 14, yL1 = Math.max(H * 0.335, yTk + fs * 1.6 + 2), yL2 = Math.max(H * 0.385, yL1 + fs * 1.6 + 2);
    g.label(`${T.tgt}: took in ${nIn} of the last ${S.flast.length}`, nx, yTk, { color: c.soft, size: fs, bg: true });
    // phones: no room under the nucleus; the step text says the same
    if (!phone && yTk + 2 * fs + 5 < yL1 - fs) g.label("swells on a peak: the size the neutron effectively “sees” (waves overlap), not a real size change", (ix0 + ix1) / 2, yTk + fs + 5, { color: c.soft, size: fs - 1, italic: true });

    // ---- right middle: the measured trace (share taken in vs energy) ----
    const tx = (i) => ix0 + (i + 0.5) / FNB * iw, ty = (v) => tBase - v * th;
    let seg = [];
    const flush = () => {
      if (seg.length > 1) {
        ctx.save(); const gr = ctx.createLinearGradient(0, tTop, 0, tBase); gr.addColorStop(0, g.rgba(c.accent, 0.32)); gr.addColorStop(1, g.rgba(c.accent, 0.06)); ctx.fillStyle = gr;
        ctx.beginPath(); ctx.moveTo(seg[0][0], tBase); seg.forEach((p) => ctx.lineTo(p[0], p[1])); ctx.lineTo(seg[seg.length - 1][0], tBase); ctx.closePath(); ctx.fill(); ctx.restore();
        g.poly(seg, c.accent, 1.6, 0.95);
      }
      seg = [];
    };
    for (let i = 0; i < FNB; i++) { const b = S.fbins[i]; if (b.n) seg.push([tx(i), ty(b.h / b.n)]); else flush(); }
    flush();
    g.line(ix0, tBase, ix1, tBase, c.soft, 1.3, 0.8);
    g.label(phone ? "share taken in" : "share of the beam taken in", ix0 + 2, tTop - 2, { color: c.soft, size: fs - 1, align: "left", base: "bottom", alpha: 1 - (S.fanA || 0) });
    // the barcode: one bar per resonance found so far
    for (const q of T.res) if (q.fa > 0) {
      const x = X(q.E), w = Math.max(1.6, Math.min(6, q.Gd / T.span * iw));
      ctx.save(); ctx.globalAlpha = (0.3 + 0.7 * q.P) * q.fa * (open < 1 ? open : 1); ctx.fillStyle = c.ink; ctx.fillRect(x - w / 2, bTop, w, bBot - bTop); ctx.restore();
    }
    // axis words under the barcode
    const yAx = bBot + 13;
    g.label(phone ? "0 (Sₙ)" : "0 = exactly Sₙ", ix0, yAx, { color: c.soft, size: fs - 1, align: "left" });
    g.label(fmtE(T, T.span, 0), ix1, yAx, { color: c.soft, size: fs - 1, align: "right" });
    g.label(phone ? "neutron energy →" : "neutron's kinetic energy →", (ix0 + ix1) / 2, yAx, { color: c.soft, size: fs - 1 });
    // the beam marker riding the axis
    { const x = X(Eb), P = fCatch(T, Eb);
      g.line(x, tTop - 4, x, bBot + 2, c.ink, 1.2, 0.45, [3, 3]);
      ctx.save(); ctx.fillStyle = c.ink; ctx.beginPath(); ctx.moveTo(x, tBase + 1); ctx.lineTo(x - 6, tBase + 10); ctx.lineTo(x + 6, tBase + 10); ctx.closePath(); ctx.fill(); ctx.restore();
      g.glow(x, ty(P), 16 + 18 * P, c.warm, 0.25 + 0.4 * P); g.dot(x, ty(P), 3.5, c.ink, 0.9); }

    // ---- the three averages, once enough of the fingerprint exists ----
    const found = T.res.filter((q) => q.found && q.E < T.span);
    S.fanA = (S.fanA || 0) + ((cov > 0.45 && found.length >= 4 ? 1 : 0) - (S.fanA || 0)) * Math.min(1, dt * 3);
    const A = S.fanA * (open < 1 ? open : 1);
    if (A > 0.02) {
      const ink = c.ink;
      // D0: bracket under the barcode between the neighbouring pair whose gap is closest to D0
      let pr = null, pd = Infinity; for (let i = 1; i < found.length; i++) { const gp = found[i].E - found[i - 1].E, d = Math.abs(gp - T.D0) + 0.15 * T.D0 * Math.abs(found[i].E / T.span - 0.35); if (d < pd) { pd = d; pr = [found[i - 1], found[i]]; } }
      const yD = bBot + 30;
      if (pr) {
        const xa = X(pr[0].E), xb = X(pr[1].E);
        g.line(xa, yD - 6, xa, yD + 1, ink, 1.4, A); g.line(xb, yD - 6, xb, yD + 1, ink, 1.4, A); g.line(xa, yD + 1, xb, yD + 1, ink, 1.4, A);
        const lab = `D₀ ≈ ${fmtE(T, T.D0, T.keV ? 0 : 0)}: the average gap`;
        g.label(lab, clamp((xa + xb) / 2, ix0 + 90, ix1 - 90), yD + 15, { color: ink, size: fs, weight: 600, bg: true, alpha: A });
      }
      // S0: average strength of the peaks, a dashed level across the measured part
      const avgP = found.reduce((s, q) => s + q.P, 0) / found.length, yS = ty(avgP);
      g.line(ix0, yS, ix1, yS, ink, 1.3, 0.75 * A, [6, 4]);
      g.label(phone ? "S₀: average peak strength" : "S₀: how strong the peaks are on average (how easily a neutron gets in)", ix1, yL1, { color: ink, size: fs, weight: 600, align: "right", bg: true, alpha: A });
      g.line(ix1 - 24, yL1 + 9, ix1 - 24, yS - 2, ink, 1, 0.5 * A);
      // <Gg>: width of one clean, isolated peak (photon-dominated where that is true)
      let best = null, bs = -Infinity;
      for (const q of found) {
        const iso = Math.min(...T.res.filter((o) => o !== q).map((o) => Math.abs(o.E - q.E))) / q.Gd;
        const sc = (q.P > 0.25 && q.P < 0.85 ? 1 : 0) + Math.min(iso, 8) / 8 + (q.Gg / q.G) - 1.2 * Math.abs(q.E / T.span - 0.3);
        if (sc > bs) { bs = sc; best = q; }
      }
      if (best) {
        const xc = X(best.E), hw = Math.max(3, best.Gd / 2 / T.span * iw), yh = ty(best.P / 2 + 0.0);
        const photonWide = best.Gg / best.G > 0.5, gg = T.Gg < 0.1 ? T.Gg.toFixed(3) : T.Gg.toFixed(2);
        if (photonWide) { g.arrow(xc, yh, xc - hw - 1, yh, ink, 1.2, A, 5); g.arrow(xc, yh, xc + hw + 1, yh, ink, 1.2, A, 5); }
        const txt = photonWide ? (phone ? `⟨Γγ⟩ ≈ ${gg} eV: photon width` : `⟨Γγ⟩ ≈ ${gg} eV: photon width, about the same for every peak`)
          : (phone ? `⟨Γγ⟩ ≈ ${T.Gg.toFixed(0)} eV: a hairline here` : `⟨Γγ⟩ ≈ ${T.Gg.toFixed(0)} eV: a hairline here; neutrons widen these peaks`);
        ctx.save(); ctx.font = `600 ${fs}px system-ui, sans-serif`; const tw = ctx.measureText(txt).width * 1.06 + 12; ctx.restore();
        const lx = clamp(xc - 20, ix0, ix1 - tw);
        g.label(txt, lx, yL2, { color: ink, size: fs, weight: 600, align: "left", bg: true, alpha: A });
        g.line(clamp(xc, lx + 6, lx + tw - 6), yL2 + 9, xc, ty(best.P) - 3, ink, 1, 0.5 * A);
      }
    }
    if (T.X > 1.5) g.label(`peaks drawn about ${Math.round(T.X)}× wider than life so they show`, (ix0 + ix1) / 2, H * 0.94, { color: c.faint, size: fs - 1.5, italic: true, serif: true });
    ctx.globalAlpha = 1;
  }
})();
