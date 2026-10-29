/* Chapter 9: Hauser-Feshbach decay as a competition between exits (compound/).
 * Scenes (S.mode): "doors" = the hot nucleus and one door per exit (g.door: lit gap = share = T x rooms beyond); balls stream out at the shares;
 *                   "hump"  = a door per emission energy (gap = T) over a crowd of residual states (rho); neutrons fall through both onto a pile;
 *                   "coul"  = a charged particle rattling in the well, tunnelling the Coulomb hill (1/r tail, tunnel width shown);
 *                   "spin"  = spin and parity: decays land in residual spin drawers through l-doors; parity by fill;
 *                   "wfc"   = width fluctuations: eight resonances with Porter-Thomas door widths; fired neutrons tally the elastic enhancement;
 *                   "norm"  = absorbed neutrons meet three fates: direct, pre-equilibrium, compound (counted).
 * Shapes follow compound/prepare.py (exit_channel_sums: weight = rho0 x T, selection rules), compound/target.py (comptarget),
 * compound/wfc.py (Moldauer nu, W_aa = 1 + 2/nu; applied for Einc <= ewfc, default S_n of the target), compound/normalization.py (xsflux = sigma_R - direct - preeq).
 * Numbers are illustrative for a medium-weight compound nucleus (A ~ 57): S_n 8, S_p 9, S_alpha 7 MeV, barriers 4 / 7.5 MeV. */
(function () {
  const { TAU, clamp, lerp, smooth, rng } = WT.util;
  const SEP = { n: 8.0, p: 9.0, a: 7.0 }, BAR = { p: 4.0, a: 7.5 }, BW = { p: 0.6, a: 0.4 };
  const ATILDE = 8.0, DELTA = 1.6, EMATCH = 6.5;                    // residual level densities: constant temperature below EMATCH, Fermi gas above
  function rho(U) { if (U <= 0.05) return 1; const s = Math.sqrt(Math.max(2.5, 11.4 * Math.sqrt(U / ATILDE))); return Math.exp(2 * Math.sqrt(ATILDE * U)) / (12 * Math.SQRT2 * s * Math.pow(ATILDE, 0.25) * Math.pow(U, 1.25)); }
  const rhoFG = (Ex) => rho(Ex - DELTA);
  const CT = (() => { const h = 0.02, sl = (Math.log(rhoFG(EMATCH + h)) - Math.log(rhoFG(EMATCH - h))) / (2 * h); const T = 1 / sl; return { T, E0: EMATCH - T * Math.log(T * rhoFG(EMATCH)) }; })();
  const rhoRes = (Ex) => (Ex <= 0 ? 0 : Ex < EMATCH ? Math.exp((Ex - CT.E0) / CT.T) / CT.T : rhoFG(Ex));
  const Tn = (e) => (e <= 0 ? 0 : 1 - Math.exp(-2.2 * Math.sqrt(e)));                       // s-wave-like neutron door
  const Tsum = (e) => (e <= 0 ? 0 : 1 - Math.exp(-e / 1.5));                                // every partial wave together: more l open as the neutron speeds up
  const Tc = (e, k) => (e <= 0 ? 0 : 1 / (1 + Math.exp((BAR[k] - e) / BW[k])));                 // Coulomb barrier (proton, alpha)
  const fE1 = (e) => { const Er = 18, G = 6; return e * G * G / ((e * e - Er * Er) ** 2 + e * e * G * G); };
  let CGAM = 1;                                                      // gamma scale: fixed so that at E = S_n + 0.5 the photon share is ~1 %
  function width(k, E) {
    const n = 48; let s = 0;
    if (k === "g") { for (let i = 0; i < n; i++) { const e = (i + 0.5) / n * E; s += e * e * e * fE1(e) * rhoRes(E - e) * E / n; } return CGAM * s; }
    const top = E - SEP[k]; if (top <= 0) return 0;
    for (let i = 0; i < n; i++) { const e = (i + 0.5) / n * top; const T = k === "n" ? Tn(e) : Tc(e, k); s += T * rhoRes(top - e) * top / n; }
    return (k === "n" ? 2 : k === "p" ? 2 : 1) * s;
  }
  function shares(E) { const w = { g: width("g", E), n: width("n", E), p: width("p", E), a: width("a", E) }; const tot = w.g + w.n + w.p + w.a; const sh = {}; for (const k in w) sh[k] = w[k] / tot; return { w, sh, tot }; }
  (function calibrate() { const E = SEP.n + 0.5; const wn = width("n", E); CGAM = 1; const wg = width("g", E); CGAM = 0.01 * wn / wg; })();
  function rooms(k, E) { const top = k === "g" ? E : E - SEP[k]; if (top <= 0) return 0; const n = 30; let s = 0; for (let i = 0; i < n; i++) s += rhoRes(top - (i + 0.5) / n * top) * top / n; return s; }
  function fmt(n) { if (n < 1.5) return "1"; if (n < 100) return n.toFixed(0); if (n < 1e4) return Math.round(n / 10) * 10 + ""; if (n < 1e6) return (n / 1e3).toFixed(0) + " thousand"; return (n / 1e6).toFixed(1) + " million"; }


  const DOORS = [
    { k: "g", name: "γ", col: "photon" },
    { k: "n", name: "n", col: "neutron" },
    { k: "p", name: "p", col: "proton" },
    { k: "a", name: "α", col: "alpha" },
    { k: "f", name: "fission", col: "fission" },
  ];
  const pct = (v) => (v >= 0.995 ? "≈ 100 %" : v >= 0.01 ? `${(v * 100).toFixed(0)} %` : v >= 0.001 ? `${(v * 100).toFixed(1)} %` : v > 0 ? `${(v * 100).toFixed(2)} %` : "0 %");
  // piecewise-linear path through waypoints: pts [[x,y],...], durations ts (one per segment); returns [x, y, segment index]
  function follow(pts, ts, t) {
    for (let i = 0; i < ts.length; i++) { if (t < ts[i]) { const u = t / ts[i]; return [lerp(pts[i][0], pts[i + 1][0], u), lerp(pts[i][1], pts[i + 1][1], u), i, u]; } t -= ts[i]; }
    const p = pts[pts.length - 1]; return [p[0], p[1], ts.length, 1];
  }
  const sum = (a) => a.reduce((s, v) => s + v, 0);
  function pick(ws, r) { let u = r * sum(ws); for (let i = 0; i < ws.length; i++) { if (u < ws[i]) return i; u -= ws[i]; } return ws.length - 1; }
  // a pile of dots stacked in columns of `wide`, scaled down when the tallest exceeds `rows`
  function pile(g, xc, yBase, count, scaleMax, rows, wide, rd, color, hollow) {
    const n = scaleMax > rows * wide ? Math.round(count * rows * wide / scaleMax) : count;
    for (let k = 0; k < n; k++) {
      const row = Math.floor(k / wide), col = k % wide, x = xc + (col - (wide - 1) / 2) * rd * 2.1, y = yBase - rd - row * rd * 2.05;
      if (hollow) g.ring(x, y, rd * 0.78, color, 1.3, 0.9); else g.dot(x, y, rd * 0.9, color, 0.9);
    }
    return yBase - Math.ceil(n / wide) * rd * 2.05;
  }

  const flying = [], fall = [], spinFall = [], wfBalls = [], normBalls = [];
  const HUMP = { key: null, cnt: [], w: [] }, SPIN = { key: null, cnt: [], lit: [] }, NORM = { key: null, cnt: [0, 0, 0] };
  const WF = { seed: 1, x: [], y: [], el: 0, tot: 0, queue: 0, idle: 0, key: null };
  function wfNew(seed) {
    const r = rng(seed * 7919 + 3);
    const gauss = () => Math.sqrt(-2 * Math.log(Math.max(1e-9, r()))) * Math.cos(TAU * r());
    WF.x = []; WF.y = [];
    for (let i = 0; i < 8; i++) { WF.x.push(gauss() ** 2); const ys = []; for (let j = 0; j < 12; j++) ys.push(gauss() ** 2); WF.y.push(ys); }
  }
  function wfStats(N) {
    let sx = 0, sxx = 0; const ybar = new Array(N).fill(0);
    for (let i = 0; i < 8; i++) { const x = WF.x[i]; let sy = 0; for (let j = 0; j < N; j++) { sy += WF.y[i][j]; ybar[j] += WF.y[i][j] / 8; } sx += x; sxx += x * x / (x + sy); }
    const xbar = sx / 8, avgProd = sxx / sx, prodAvg = xbar / (xbar + sum(ybar));
    return { avgProd, prodAvg };
  }

  WT.chapter("decay", {
    num: "Chapter 9", title: "Choosing an exit", short: "Decay",
    lead: "The compound nucleus must shed its energy by emitting a particle or a photon. This chapter draws each way out as a door. The engine's job is to say what share of the flux (the stream of reactions arriving here) leaves through each door.",
    html: `
<div class="step">
  <p>One door per exit: a <em class="g">photon</em> (γ), a <em class="n">neutron</em> (n), a <em class="p">proton</em> (p), an <em class="a">alpha particle</em> (α: two protons and two neutrons) and, for heavy nuclei only, <em class="f">fission</em> (splitting in two). The lit gap in each door is that exit's share, and the balls stream out at the same rates; grey doors are shut. Having forgotten how it formed, the nucleus uses each door b in proportion to a weight:</p>
  <div class="formula">share<sub>b</sub> = T<sub>b</sub> · ρ<sub>b</sub> / Σ<sub>c</sub> T<sub>c</sub> · ρ<sub>c</sub></div>
  <p>The <b>transmission coefficient</b> <i>T</i> is the chance that a particle reaching the edge gets through; for particles it comes from the optical model of Chapter 5, run backwards. The <b>level density</b> ρ, written beside each door, counts the states the leftover nucleus can end up in. Sharing by <i>T</i> times ρ is the <b>Hauser–Feshbach</b> rule. At 10 MeV the neutron door takes nearly everything.</p>
</div>
<div class="step">
  <h3>Evaporation spectra</h3>
  <p>The neutron door, split by outgoing energy ε (slow left, fast right). Each door's gap <i>T</i>(ε) widens for faster neutrons. Under it is the crowd of states the leftover nucleus can be in: a slow neutron leaves most of the energy behind, where states are plentiful, so the crowds shrink to the right.</p>
  <div class="ctl"><label for="dc-sp">Energy to spare</label><input id="dc-sp" type="range" data-bind="spare" min="1" max="12" step="0.5" value="5"><output data-show="spare" data-fmt="1"></output></div>
  <p>Door × crowd makes the pile a hump, the <b>evaporation spectrum</b>, like steam leaving a hot liquid. Drag the energy to spare (in MeV, million electron-volts): the pile restarts, and its peak stays near 1 MeV, set by the nuclear temperature. Extra energy mostly makes the leftover nucleus hotter.</p>
</div>
<div class="step">
  <h3>The Coulomb barrier in emission</h3>
  <p>A proton's energy at each distance r from the centre: a well inside, and outside a hill from the electric (Coulomb) repulsion, falling off as 1/r. Below the hilltop the proton, rattling in the well, can only <b>tunnel</b> through the shaded stretch, a quantum effect that succeeds once in many knocks on the wall. The odds are worked out as in Chapter 4: the wider and higher the stretch, the more zeros in "1 knock in 10<sup>N</sup>".</p>
  <div class="ctl"><label for="dc-ce">Particle energy</label><input id="dc-ce" type="range" data-bind="eps" min="0.5" max="12" step="0.1" value="3"><output data-show="eps" data-fmt="1"></output></div>
  <div class="btns"><button class="btn ghost" data-act="toggleAlpha">Switch proton / alpha</button></div>
  <p>Drag the energy down and watch the tunnel widen; then switch to the alpha, whose two charges face a hill about twice as high. That is why uncharged neutrons usually win once they can leave, and why proton and alpha exits matter mostly for light nuclei and high energies.</p>
</div>
<div class="step">
  <h3>Channel thresholds</h3>
  <p>Each particle door opens only above its <b>separation energy</b>, the cost of pulling that particle out: here 8 MeV for a neutron, 9 for a proton, 7 for an alpha. Below the neutron's 8 MeV, nearly every decay gives off light.</p>
  <div class="ctl"><label for="dc-e">Excitation energy</label><input id="dc-e" type="range" data-bind="E" min="5" max="24" step="0.1" value="7"><output data-show="E" data-fmt="1"></output></div>
  <p>Drag the excitation energy past 8 MeV. Within about 1 MeV the neutron door swings wide and the photon share drops a hundredfold. The alpha door is unlocked first, at 7 MeV, yet barely opens: its Coulomb hill (Chapter 4) keeps it nearly shut until well above. The proton door unlocks at 9 MeV and also stays narrow, held back by its own hill.</p>
</div>
<div class="step">
  <h3>Angular-momentum and parity conservation</h3>
  <p>The compound nucleus (top) has spin <i>J</i>; the leftover nucleus's states sit below in drawers by spin <i>J</i>′. The neutron carries off the difference in spin and parity: leaving with orbital angular momentum <i>l</i>, it changes the spin by up to <i>l</i> + ½ and flips the parity when <i>l</i> is odd. Larger <i>l</i> means a narrower door; each drawer's door is the smallest <i>l</i> that reaches it. Solid landings keep parity; hollow ones flip it.</p>
  <div class="ctl"><label for="dc-j">Compound spin J</label><input id="dc-j" type="range" data-bind="J" min="0" max="10" step="1" value="2" data-instant><output id="dc-jout">5/2</output></div>
  <p>Drag <i>J</i> up. The open doors slide toward high-spin drawers, which hold few states, while the full drawers sit behind shut doors. A high-spin compound nucleus is slow to emit particles, which gives photons, and isomers (long-lived states, Chapter 10), their chance.</p>
</div>
<div class="step">
  <h3>Elastic enhancement</h3>
  <p>At low energy the compound nucleus is a set of sharp <b>resonances</b>, energies where the neutron is easily absorbed; eight are drawn, one per row. Each has random door widths: the entrance (the neutron channel) on the left, width <i>x</i>, and the other doors, mostly photons here, on the right, widths <i>y</i>.</p>
  <div class="btns"><button class="btn" data-act="fire">Fire 40 neutrons</button><button class="btn ghost" data-act="reroll">New resonances</button></div>
  <p>Press Fire and follow the neutrons. A neutron gets into a row in proportion to that row's entrance width <i>x</i>. Once inside, it picks a way out in proportion to the widths: back through the entrance with chance <i>x</i> / (<i>x</i> + Σ<i>y</i>), otherwise through one of the other doors. The trays count where they went.</p>
  <p>The catch: a row with a wide entrance gets more neutrons in and also sends more of them back out. So more come back than you would guess from the average widths alone. The true share back out (an <b>average of products</b>) beats the simple estimate (a <b>product of averages</b>); both are written at the top.</p>
  <p>Their ratio is the <b>elastic enhancement</b>. The engine's <b>width-fluctuation correction</b> applies it: it moves that extra flux from the other doors back to the entrance.</p>
  <div class="ctl"><label for="dc-n">Other doors</label><input id="dc-n" type="range" data-bind="Nch" min="1" max="12" step="1" value="2" data-instant><output data-show="Nch" data-fmt="0"></output></div>
  <p>Add doors. With many exits their total width stops fluctuating, so the correction matters most where few doors are open. The engine applies it, with Moldauer's formula, for incident neutrons up to the target's neutron separation energy, and leaves it out above.</p>
</div>
<div class="step">
  <h3>Flux after direct reactions</h3>
  <p>The doors of this chapter only share out the neutrons that actually stayed. Chapters 6 and 7 already took their cut: some neutrons make one glancing hit and fly off (direct), some knock about once or twice and shoot out fast (pre-equilibrium). Only the rest stay inside and heat the nucleus. The counters on the right tally each fate; the ones that stay never leave the nucleus, they are only counted.</p>
  <div class="ctl"><label for="dc-einc">Neutron energy</label><input id="dc-einc" type="range" data-bind="Einc" min="1" max="30" step="0.5" value="8"><output data-show="Einc" data-fmt="1"></output></div>
  <p>Only those that stay enter the door competition. Drag the neutron energy: at a few MeV nearly all stay; by 30 MeV about half have left before reaching equilibrium.</p>
  <div class="aside">In the code: <code>compound/prepare.py</code> (exit weights T·ρ per spin and parity, selection rules), <code>compound/target.py</code> (first decay with width fluctuations), <code>compound/continuum.py</code> (decay of every later bin), <code>compound/wfc.py</code> (Moldauer, HRTW, GOE corrections), <code>compound/normalization.py</code> (flux left for the compound nucleus), <code>omp/inverse.py</code> (doors run backwards).</div>
</div>`,
    setup(S) {
      S.set("mode", "doors"); S.to("E", 10, true); S.to("spare", 5, true); S.to("eps", 3, true); S.to("J", 2, true); S.to("Nch", 2, true); S.to("Einc", 8, true);
      S.to("alpha", 0, true); S.lastSpawn = 0; S.cb = null; S.jShown = -1;
      S.on("toggleAlpha", () => { S.to("alpha", S.target.alpha > 0.5 ? 0 : 1); S.cb = null; });
      S.on("fire", () => { WF.queue += 40; });
      S.on("reroll", () => { WF.seed++; WF.key = null; });
      wfNew(WF.seed);
    },
    steps: [
      (S) => { S.set("mode", "doors"); S.to("E", 10); },
      (S) => { S.set("mode", "hump"); },
      (S) => { S.set("mode", "coul"); S.cb = null; },
      (S) => { S.set("mode", "doors"); S.to("E", 7); },
      (S) => { S.set("mode", "spin"); },
      (S) => { S.set("mode", "wfc"); },
      (S) => { S.set("mode", "norm"); },
    ],
    frame(g, S, dt) {
      const J = Math.round(S.target.J ?? 2);
      if (J !== S.jShown) { S.jShown = J; const o = document.getElementById("dc-jout"); if (o) o.textContent = `${2 * J + 1}/2`; }
      if (S.mode === "doors") drawDoors(g, S, dt);
      else if (S.mode === "hump") drawHump(g, S, dt);
      else if (S.mode === "coul") drawCoulomb(g, S, dt);
      else if (S.mode === "spin") drawSpin(g, S, dt);
      else if (S.mode === "wfc") drawWfc(g, S, dt);
      else drawNorm(g, S, dt);
    },
  });

  // ---------- scene 1 / 4: the room with doors ----------
  function drawDoors(g, S, dt) {
    const { W, H, c } = g;
    const E = clamp(S.E, 5, 24);
    const phone = W < 600;
    const cx = W * (phone ? 0.24 : 0.28), cy = H * 0.5, Rn = Math.min(W, H) * (phone ? 0.075 : 0.085);
    const Rd = Math.min(W * (phone ? 0.36 : 0.4), H * 0.37), dh = Math.min(80, H * 0.1), dw = dh * 0.62;
    const { sh, w } = shares(E);
    g.glow(cx, cy, Rn * 3.2, c.warm, 0.1 + E / 70);
    g.nucleus(cx, cy, Rn, { N: 48, Z: 22, t: S.time, heat: 1 + E / 6, jiggle: 0.6 });
    g.label(`${E.toFixed(1)} MeV`, cx, cy + Rn + 20, { color: c.warm, size: 13, bg: true, weight: 600 });
    const ANG = [-1.12, -0.56, 0, 0.56, 1.12];
    const geo = {};
    DOORS.forEach((d, i) => {
      const x = cx + Math.cos(ANG[i]) * Rd, yc = cy + Math.sin(ANG[i]) * Rd, col = c[d.col];
      const closed = d.k === "f" || (d.k !== "g" && E <= SEP[d.k]);
      const share = closed ? 0 : sh[d.k];
      const r = g.door(x, yc + dh / 2, dh, share, col, d.name, { size: phone ? 12 : 14 });
      geo[d.k] = r;
      const tx = x + dw / 2 + 10;
      g.label(closed ? (d.k === "f" ? (phone ? "heavy only" : "heavy nuclei only") : `shut below ${SEP[d.k]} MeV`) : pct(share), tx, yc - (phone ? 0 : 9), { color: closed ? c.faint : c.ink, size: phone ? 12 : 14, weight: closed ? 500 : 600, align: "left", bg: true });
      if (!closed && !phone) {
        const rm = rooms(d.k, E);
        const T = d.k === "g" ? null : w[d.k] / Math.max(rm, 1e-9) / (d.k === "a" ? 1 : 2);
        g.label(T === null ? `weak door × ≈ ${fmt(rm)} states` : `T ≈ ${T < 0.01 ? T.toExponential(0) : T.toFixed(2)} × ≈ ${fmt(rm)} state${fmt(rm) === "1" ? "" : "s"}`, tx, yc + 10, { color: c.faint, size: 11, align: "left", bg: true });
      }
    });
    // particles streaming out through the gaps, in proportion to the shares
    S.lastSpawn += dt * 16;
    while (S.lastSpawn > 1) {
      S.lastSpawn -= 1; if (flying.length > 70) continue;
      const r = Math.random(); let acc = 0;
      for (const d of DOORS) { if (d.k === "f") continue; acc += sh[d.k]; if (r < acc) { flying.push({ k: d.k, t0: S.time, j: Math.random() - 0.5 }); break; } }
    }
    for (let i = flying.length - 1; i >= 0; i--) {
      const f = flying[i], u = (S.time - f.t0) / 1.5, d = geo[f.k];
      if (u > 1 || !d) { flying.splice(i, 1); continue; }
      const gx = d.mx + f.j * Math.max(0, d.gap - 6), gy = d.my + f.j * dh * 0.3;
      let x, y; const dx = gx - cx, dy = gy - cy, L = Math.hypot(dx, dy);
      if (u < 0.55) { const v = u / 0.55; x = lerp(cx, gx, v); y = lerp(cy, gy, v); } else { const v = (u - 0.55) / 0.45; x = gx + dx / L * v * Rd * 0.45; y = gy + dy / L * v * Rd * 0.45; }
      const fade = 1 - smooth(0.8, 1, u), a = Math.atan2(dy, dx);
      if (f.k === "g") g.photon(x, y, a, 18, fade);
      else if (f.k === "a") { for (let k = 0; k < 4; k++) g.dot(x + (k % 2) * 6 - 3, y + (k > 1 ? 6 : 0) - 3, 3.6, k < 2 ? c.proton : c.neutron, fade); }
      else g.ball(x, y, 5.5, c[f.k === "n" ? "neutron" : "proton"], fade);
    }
    const lead = sh.n > 0.5 ? "the neutron door takes nearly everything" : sh.g > 0.5 ? "below the neutron threshold, nearly all decays emit light" : "the doors share the decays";
    g.label(lead, W * 0.5, phone ? 16 : H - 24, { color: c.ink, size: phone ? 13 : 15, weight: 600, serif: true, bg: true });
  }

  // ---------- scene 2: door x crowd -> the evaporation pile ----------
  function drawHump(g, S, dt) {
    const { W, H, c } = g;
    const phone = W < 600;
    const spare = clamp(S.target.spare, 1, 12), range = Math.min(spare, 5), NC = 14;
    const x0 = W * 0.05, x1 = W * 0.97, colW = (x1 - x0) / NC, X = (i) => x0 + (i + 0.5) * colW;
    const eps = (i) => (i + 0.5) / NC * range;
    const nx = W * 0.5, ny = H * 0.075, nR = Math.min(W, H) * 0.04;
    const dh = Math.min(60, H * 0.08), dw = Math.min(dh * 0.62, colW * 0.72), sill = H * 0.24;
    const sq = Math.min(4.2, colW / 6.5), roomTop = sill + (phone ? 22 : 30), roomBot = roomTop + 12 * sq * 1.7 + 6;
    const base = H * 0.9, pileH = base - roomBot - (phone ? 34 : 46);
    const rd = Math.min(3.6, colW / 7.5), rows = Math.max(4, Math.floor(pileH / (rd * 2.05)));
    if (HUMP.key !== spare) {
      HUMP.key = spare; HUMP.w = []; for (let i = 0; i < NC; i++) HUMP.w.push(Tsum(eps(i)) * rhoRes(spare - eps(i)));
      const wm = Math.max(...HUMP.w); HUMP.cnt = HUMP.w.map((v) => Math.round(0.55 * rows * 3 * v / wm)); fall.length = 0;
    }
    // the hot nucleus that emits
    g.glow(nx, ny, nR * 2.6, c.warm, 0.35); g.nucleus(nx, ny, nR, { N: 30, Z: 13, t: S.time, heat: 2, jiggle: 0.5 });
    if (!phone) g.label(`${spare.toFixed(1)} MeV to spare`, nx + nR + 12, ny, { color: c.warm, size: 13, weight: 600, align: "left", bg: true });
    // row 1: one door per neutron energy
    const rho0 = rhoRes(spare - eps(0)), doors = [];
    for (let i = 0; i < NC; i++) doors.push(g.door(X(i), sill, dh, Tsum(eps(i)), c.neutron, null, { w: dw }));
    g.label(phone ? "door gap = T(ε)" : "doors: one per neutron energy ε, gap = T(ε)", x0, sill - dh - 14, { color: c.neutron, size: phone ? 12 : 13, weight: 600, align: "left", bg: true });
    // row 2: the crowd of states left behind
    for (let i = 0; i < NC; i++) {
      const n = Math.max(1, Math.round(36 * rhoRes(spare - eps(i)) / rho0));
      for (let k = 0; k < n; k++) { const row = Math.floor(k / 3), col = k % 3; g.dot(X(i) + (col - 1) * sq * 1.8, roomTop + sq + row * sq * 1.7, sq * 0.62, c.soft, 0.7); }
    }
    g.label(phone ? "× states left behind" : "× states the leftover nucleus can be in: many after a slow neutron", x0, roomTop - 9, { color: c.soft, size: phone ? 12 : 13, align: "left", bg: true });
    // row 3: the pile
    const maxC = Math.max(...HUMP.cnt);
    let iPk = 0; HUMP.w.forEach((v, i) => { if (v > HUMP.w[iPk]) iPk = i; });
    const tops = HUMP.cnt.map((n, i) => pile(g, X(i), base, n, maxC, rows, 3, rd, c.neutron));
    g.line(x0, base + 1, x1, base + 1, c.faint, 1, 0.5);
    g.label(`most ≈ ${eps(iPk).toFixed(1)} MeV`, X(iPk) + colW * 0.7, tops[iPk] - 12, { color: c.neutron, size: 13, weight: 600, bg: true, align: "left" });
    g.label(phone ? "= the pile" : "= where the neutrons land: the evaporation spectrum", x1, base - pileH * 0.75, { color: c.ink, size: phone ? 12 : 13, weight: 600, align: "right", bg: true });
    g.label(phone ? "slow" : "slow neutrons", x0, base + 16, { color: c.faint, size: 12, align: "left" });
    g.label(spare > 5 ? (phone ? "fast: 5 MeV →" : `fast: 5 MeV (beyond, up to ${spare.toFixed(1)}, almost none)`) : (phone ? `fast: ${spare.toFixed(1)}` : `fast: ${spare.toFixed(1)} MeV, the neutron takes it all`), x1, base + 16, { color: c.faint, size: 12, align: "right" });
    // falling neutrons: nucleus -> door gap -> through the crowd -> the pile
    S.lastSpawn += dt * 14;
    while (S.lastSpawn > 1) { S.lastSpawn -= 1; if (fall.length < 40) fall.push({ i: pick(HUMP.w, Math.random()), t: 0, j: Math.random() - 0.5 }); }
    for (let k = fall.length - 1; k >= 0; k--) {
      const f = fall[k]; f.t += dt; const d = doors[f.i], gx = X(f.i) + f.j * Math.max(0, d.gap - 5);
      const [x, y, seg] = follow([[nx, ny], [gx, sill - dh], [gx, sill], [gx + f.j * rd * 3, tops[f.i] - rd]], [0.55, 0.18, 0.6], f.t);
      if (seg >= 3) { HUMP.cnt[f.i]++; fall.splice(k, 1); continue; }
      g.ball(x, y, 4.5, c.neutron);
    }
  }

  // ---------- scene 3: the Coulomb hill, knocking and tunnelling ----------
  function drawCoulomb(g, S, dt) {
    const { W, H, c } = g, ctx = g.ctx;
    const phone = W < 600;
    const isA = S.target.alpha > 0.5, k = isA ? "a" : "p", col = isA ? c.alpha : c.proton;
    const eps = clamp(S.eps, 0.5, 12);
    const Rn = 5.0, rMax = 30, vMin = -4, vMax = 9;
    const x0 = W * 0.06, x1 = W * 0.96, yTop = H * 0.14, yBot = H * 0.72;
    const X = (r) => x0 + (x1 - x0) * r / rMax, Y = (v) => yBot - (yBot - yTop) * (v - vMin) / (vMax - vMin);
    const B = BAR[k], Rc = Rn + 1.6;
    const fws = (r) => 1 / (1 + Math.exp((r - Rn) / 0.45));
    const V = (r) => -40 * fws(r) + (1 - fws(r)) * B * Rc / Math.max(r, Rc);
    const pts = []; let rTop = Rn, vTop = -1e9;
    for (let i = 0; i <= 300; i++) { const r = 0.3 + (rMax - 0.3) * i / 300; const v = V(r); if (v > vTop) { vTop = v; rTop = r; } pts.push([X(r), Y(Math.max(v, vMin - 3))]); }
    // terrain: a soft band hugging the inside of the profile, fading at both ends and into the well
    ctx.save(); ctx.beginPath(); ctx.moveTo(pts[0][0], yBot); pts.forEach((p) => ctx.lineTo(p[0], p[1])); ctx.lineTo(pts[pts.length - 1][0], yBot); ctx.closePath(); ctx.clip(); ctx.beginPath(); ctx.rect(0, 0, W, yBot - 2); ctx.clip();
    for (const [lw, a] of [[70, 0.07], [40, 0.08], [18, 0.1]]) g.poly(pts, c.soft, lw, a);
    ctx.restore();
    g.clip(0, 0, W, yBot); g.poly(pts, c.ink, 2.4); g.restore();
    [[x0 - 10, x0 + 40], [x1 + 10, x1 - 60]].forEach(([a, b]) => { const gr = ctx.createLinearGradient(a, 0, b, 0); gr.addColorStop(0, g.rgba(c.paper, 1)); gr.addColorStop(1, g.rgba(c.paper, 0)); ctx.fillStyle = gr; ctx.fillRect(Math.min(a, b) - 20, yTop - 30, Math.abs(b - a) + 20, yBot - yTop + 40); });
    { const gr = ctx.createLinearGradient(0, yBot - 50, 0, yBot + 2); gr.addColorStop(0, g.rgba(c.paper, 0)); gr.addColorStop(1, g.rgba(c.paper, 1)); ctx.fillStyle = gr; ctx.fillRect(0, yBot - 50, W, 54); }
    g.label(phone ? "well ↓" : "well (much deeper) ↓", X(Rn * 0.5), Y(-2.6), { color: c.soft, size: 12 });
    g.label(`hilltop ≈ ${vTop.toFixed(1)} MeV`, X(rTop) + 12, Y(vTop) - 16, { color: col, size: 13, weight: 600, align: "left", bg: true });
    g.label(phone ? "falls as 1/r" : "Coulomb hill, falling as 1/r", X(rMax * 0.72), Y(V(rMax * 0.72)) + 18, { color: c.soft, size: 12, bg: true });
    // the particle's energy line and the tunnel stretch
    const over = eps >= vTop, ey = Y(Math.min(eps, vMax));
    let rIn = Rn, rOut = rMax;
    const rOutT = (e) => B * Rc / e;   // where the 1/r hill falls back to the particle's energy (may lie beyond the picture)
    if (!over) { for (let r = 3; r < rTop; r += 0.02) if (V(r) >= eps) { rIn = r; break; } rOut = Math.min(rMax, rOutT(eps)); }
    g.line(X(0.6), ey, x1, ey, col, 1.5, 0.75, [6, 4]);
    if (!over) {
      g.line(X(rIn), ey, X(rOut), ey, col, 8, 0.25);
      g.label(rOut >= rMax ? "tunnel: wider than the picture" : `tunnel ${(rOut - rIn).toFixed(1)} fm`, Math.max(X(rIn) + 44, (X(rIn) + X(rOut)) / 2), ey + 28, { color: col, size: 12, weight: 600, bg: true });
    }
    const rightBelow = V(rMax) < eps;
    g.label(`${isA ? "alpha" : "proton"} energy ${eps.toFixed(1)} MeV${eps > vMax ? " ↑" : ""}`, x1, rightBelow && !phone ? ey - 14 : ey + 16, { color: col, size: phone ? 12 : 13, align: "right", bg: true });
    // the particle: rattles in the well, knocks on the wall, sometimes gets through
    // tunnelling odds by WKB through the drawn hill, as in Chapter 4: P = exp(-2/hbar-c * integral sqrt(2 mu (V - E)) dr)
    let T = 1;
    if (!over) { const MU = isA ? 3727.4 * 53 / 57 : 938.3 * 56 / 57, n = 400, h = (rOutT(eps) - rIn) / n; let sI = 0; for (let i = 0; i < n; i++) { const r = rIn + (i + 0.5) * h; sI += Math.sqrt(Math.max(0, 2 * MU * (V(r) - eps))) * h; } T = Math.exp(-2 * sI / 197.327); }
    if (!S.cb || S.cb.k !== k) S.cb = { k, ph: "in", r: 1, dir: 1, knocks: 0, t: 0, last: 0 };
    const cb = S.cb, wall = over ? Rn : rIn, sp = (wall - 0.8) / 0.32;
    if (cb.ph === "in") {
      cb.r += cb.dir * sp * dt;
      if (cb.r <= 0.8) { cb.r = 0.8; cb.dir = 1; }
      if (cb.r >= wall) {
        cb.r = wall; cb.dir = -1; cb.knocks++; cb.flash = S.time;
        if (over || Math.random() < T) { cb.ph = "out"; cb.r = over ? wall : rOut; cb.v = 4; cb.t = S.time; cb.last = cb.knocks; cb.tun = !over; }
      }
    } else {
      cb.v += dt * 30; cb.r += cb.v * dt;
      if (cb.r > rMax + 1) { cb.ph = "in"; cb.r = 1; cb.dir = 1; cb.knocks = 0; }
    }
    const bx = X(cb.r), by = ey - 9, a = cb.ph === "out" ? 1 - smooth(rMax - 4, rMax + 1, cb.r) : 1;
    if (cb.ph === "out" && cb.tun && S.time - cb.t < 0.5) g.line(X(rIn), by, X(rOut), by, col, 3, 0.6 * (1 - (S.time - cb.t) / 0.5), [3, 4]);
    if (cb.flash && S.time - cb.flash < 0.25 && cb.ph === "in") g.glow(X(wall), by, 18, col, 0.5 * (1 - (S.time - cb.flash) / 0.25));
    if (isA) { for (let i = 0; i < 4; i++) g.ball(bx + (i % 2) * 8 - 4, by + (i > 1 ? 8 : 0) - 4, 5.5, i < 2 ? c.proton : c.neutron, a); }
    else g.ball(bx, by, 8, c.proton, a);
    const odds = 1 / Math.max(T, 1e-12);
    const oddsTxt = odds < 1.5 ? "nearly every knock" : odds < 1e5 ? `about 1 knock in ${Math.round(odds).toLocaleString(WT.loc ? WT.loc() : "en")}` : `about 1 knock in ${odds.toExponential(0).replace("e+", " × 10^")}`;
    g.label(over ? "above the hilltop: it rolls straight out" : `below the top, must tunnel: ${oddsTxt} gets through`, W * 0.5, yBot + 30, { color: c.ink, size: phone ? 13 : 15, weight: 600, serif: true, bg: true });
    g.label(cb.ph === "out" ? (over ? "out" : `through after ${cb.last} knock${cb.last === 1 ? "" : "s"}`) : `knocks so far: ${cb.knocks}`, W * 0.5, yBot + 54, { color: c.soft, size: 13, bg: true });
    if (!phone) g.label("distance r from the centre (fm) →", x1, yBot + 80, { color: c.faint, size: 12, align: "right" });
  }

  // ---------- scene 5: spin and parity: which drawers fill ----------
  function drawSpin(g, S, dt) {
    const { W, H, c } = g;
    const phone = W < 600;
    const J = Math.round(clamp(S.target.J, 0, 10));
    const kR = 2.3, Tl = (l) => 1 / (1 + Math.exp((l + 0.5 - kR) / 0.55)), s2 = 12, NJ = 13;
    const x0 = W * 0.04, x1 = W * 0.97, colW = (x1 - x0) / NJ, X = (i) => x0 + (i + 0.5) * colW;
    const cx = W * 0.12, cy = H * 0.1, R = Math.min(W, H) * 0.055;
    const dh = Math.min(46, colW * 1.25), dw = Math.min(dh * 0.62, colW * 0.8), sill = H * 0.34, base = H * 0.86, maxH = base - sill - 34;
    const rd = Math.min(3.2, colW / 7.5), rows = Math.max(4, Math.floor(maxH / (rd * 2.05)));
    if (SPIN.key !== J) {
      SPIN.key = J; SPIN.lit = [];
      for (let Jr = 0; Jr < NJ; Jr++) { const need = Math.max(0, Math.round(Math.abs(J + 0.5 - Jr) - 0.5)); const T = Tl(need), nRooms = (2 * Jr + 1) / (2 * s2) * Math.exp(-((Jr + 0.5) ** 2) / (2 * s2)); SPIN.lit.push({ need, T, nRooms, w: T * nRooms }); }
      const wm = Math.max(...SPIN.lit.map((v) => v.w)); SPIN.cnt = SPIN.lit.map((v) => Math.round(0.5 * rows * 3 * v.w / wm)); spinFall.length = 0;
    }
    const lit = SPIN.lit;
    g.glow(cx, cy, R * 2.6, c.warm, 0.3);
    g.nucleus(cx, cy, R, { N: 36, Z: 16, t: S.time, rot: S.time * (0.4 + J * 0.35), heat: 1.6, jiggle: 0.5 });
    if (phone) g.label(`J = ${2 * J + 1}/2, parity +`, cx - R, cy + R + 14, { color: c.ink, size: 12, weight: 600, align: "left", bg: true });
    else g.label(`J = ${2 * J + 1}/2, parity +`, cx + R + 12, cy, { color: c.ink, size: 13, weight: 600, align: "left", bg: true });
    const doors = lit.map((v, i) => g.door(X(i), sill, dh, v.T < 0.02 ? 0 : v.T, c.neutron, !phone && v.T >= 0.02 ? `l=${v.need}` : null, { w: dw, size: 10 }));
    // each drawer: its states as faint slots (how many it holds), and the decays that landed there
    const peak = Math.max(...lit.map((v) => v.nRooms)), maxC = Math.max(...SPIN.cnt), tops = [];
    lit.forEach((v, i) => {
      const nSlots = Math.round(v.nRooms / peak * rows * 3);
      for (let k = 0; k < nSlots; k++) { const row = Math.floor(k / 3), cl = k % 3; g.dot(X(i) + (cl - 1) * rd * 2.1, base - rd - row * rd * 2.05, rd * 0.55, c.faint, 0.45); }
      tops.push(pile(g, X(i), base, SPIN.cnt[i], Math.max(maxC, rows * 3), rows, 3, rd, c.ink, v.need % 2 === 1));
      g.label(String(i), X(i), base + 14, { color: c.soft, size: phone ? 10 : 12 });
    });
    g.label(phone ? "leftover states by spin J′ →" : "drawers: states of the leftover nucleus by spin J′ (faint: states it holds) →", x1, base + 32, { color: c.faint, size: 12, align: "right" });
    const reach = lit.reduce((s, v) => s + (v.T > 0.3 ? v.nRooms : 0), 0) / lit.reduce((s, v) => s + v.nRooms, 0);
    g.label(phone ? `open doors reach ${(reach * 100).toFixed(0)} %` : `open doors reach about ${(reach * 100).toFixed(0)} % of the states`, x1, H * 0.05, { color: c.ink, size: phone ? 13 : 15, weight: 600, serif: true, bg: true, align: "right" });
    g.label("● parity kept (even l)   ○ flipped (odd l)", x1, H * 0.05 + 22, { color: c.soft, size: 12, bg: true, align: "right" });
    S.lastSpawn += dt * 12;
    while (S.lastSpawn > 1) { S.lastSpawn -= 1; if (spinFall.length < 30) spinFall.push({ i: pick(lit.map((v) => v.w), Math.random()), t: 0, j: Math.random() - 0.5 }); }
    for (let k = spinFall.length - 1; k >= 0; k--) {
      const f = spinFall[k]; f.t += dt; const d = doors[f.i], gx = X(f.i) + f.j * Math.max(0, d.gap - 4);
      const [x, y, seg] = follow([[cx, cy], [gx, sill - dh], [gx, sill], [gx, tops[f.i] - rd]], [0.6, 0.18, 0.5], f.t);
      if (seg >= 3) { SPIN.cnt[f.i]++; spinFall.splice(k, 1); continue; }
      if (seg < 2) g.ball(x, y, 4.2, c.neutron); else if (lit[f.i].need % 2) g.ring(x, y, rd * 0.8, c.ink, 1.3); else g.dot(x, y, rd * 0.9, c.ink);
    }
    if (maxC > rows * 3 * 1.6) SPIN.cnt = SPIN.cnt.map((v) => Math.round(v * 0.7));
  }

  // ---------- scene 6: width fluctuations: eight resonances with random doors ----------
  function drawWfc(g, S, dt) {
    const { W, H, c } = g;
    const phone = W < 600;
    const N = Math.round(clamp(S.target.Nch, 1, 12));
    const key = WF.seed + ":" + N;
    if (WF.key !== key) {
      if (WF.key === null || WF.key.split(":")[0] !== String(WF.seed)) wfNew(WF.seed);
      WF.key = key; wfBalls.length = 0;
      WF.tot = 0; WF.el = 0; WF.queue = 0;   // a new set of doors is a new experiment: the trays start empty, counts come only from fired neutrons
    }
    const st = wfStats(N);
    const yS0 = H * (phone ? 0.13 : 0.12), yS1 = H * (phone ? 0.66 : 0.66), sh = (yS1 - yS0) / 8, Yc = (i) => yS0 + (i + 0.5) * sh;
    const dh = sh * 0.8, dwFull = dh * 0.62;
    const xSrc = W * 0.02, xE = W * 0.17, xR = W * 0.29, xX0 = W * 0.38, xX1 = W * 0.97;
    const step = Math.min(dwFull * 1.5, (xX1 - xX0) / N), dwX = Math.min(dwFull, step * 0.8);
    const open = (v) => Math.min(1, v / 3.5);
    const ent = [], ex = [];
    for (let i = 0; i < 8; i++) {
      const y = Yc(i);
      ent.push(g.door(xE, y + dh / 2, dh, open(WF.x[i]), c.neutron, null, { w: dwFull }));
      g.glow(xR, y, sh * 0.55, c.warm, 0.2); g.ring(xR, y, Math.min(sh * 0.28, 13), c.warm, 2, 0.85);
      const row = [];
      for (let j = 0; j < N; j++) row.push(g.door(xX0 + (j + 0.5) * step, y + dh / 2, dh, open(WF.y[i][j]), c.photon, null, { w: dwX }));
      ex.push(row);
    }
    g.label(phone ? "entrance x" : "entrance, width x", xE, yS0 - 13, { color: c.neutron, size: 12, weight: 600, bg: true });
    g.label(phone ? `${N} other doors, y` : `${N} other door${N > 1 ? "s" : ""}, widths y`, xX0 + Math.max(N * step, 120) / 2, yS0 - 13, { color: c.photon, size: 12, weight: 600, bg: true });
    // trays
    const tY = Math.min(H * 0.92, yS1 + 160), tL = W * (phone ? 0.26 : 0.22), tR = W * (phone ? 0.76 : 0.68);
    const back = WF.el, on = WF.tot - WF.el, rd = phone ? 2.4 : 3, wide = phone ? 8 : 11, rows = Math.max(3, Math.floor((tY - yS1 - 50) / (rd * 2.05)));
    const mx = Math.max(back, on, rows * wide * 0.6);
    pile(g, tL, tY, back, mx, rows, wide, rd, c.neutron);
    pile(g, tR, tY, on, mx, rows, wide, rd, c.photon);
    if (!WF.tot && !wfBalls.length && WF.queue <= 0) g.label("press Fire to send neutrons in", W * 0.5, (yS1 + tY) / 2 + 6, { color: c.soft, size: phone ? 12 : 13, italic: true });
    g.label(`back out the entrance: ${back} of ${WF.tot}`, tL, tY + 14, { color: c.neutron, size: phone ? 11 : 12, weight: 600, bg: true });
    g.label(`out another door: ${on}`, tR, tY + 14, { color: c.photon, size: phone ? 11 : 12, weight: 600, bg: true });
    // the comparison
    g.label(phone ? `back out ${pct(st.avgProd)}, not ${pct(st.prodAvg)}: × ${(st.avgProd / st.prodAvg).toFixed(1)}` : `share back out: average of products ${pct(st.avgProd)} · product of averages ${pct(st.prodAvg)} · × ${(st.avgProd / st.prodAvg).toFixed(1)}`, W * 0.5, H * 0.035, { color: c.ink, size: phone ? 12 : 14, weight: 600, serif: true, bg: true });
    g.label(phone ? `other doors ${pct(1 - st.avgProd)}, not ${pct(1 - st.prodAvg)}` : `other doors together: ${pct(1 - st.avgProd)} instead of ${pct(1 - st.prodAvg)}`, W * 0.5, yS1 + 20, { color: c.soft, size: 12, bg: true });
    // neutrons
    S.lastSpawn += dt * 16;
    while (S.lastSpawn > 1) {
      S.lastSpawn -= 1; if (WF.queue <= 0 || wfBalls.length > 50) continue; WF.queue--;
      const i = pick(WF.x, Math.random()), ys = WF.y[i].slice(0, N), x = WF.x[i], el = Math.random() < x / (x + sum(ys));
      wfBalls.push({ i, j: el ? -1 : pick(ys, Math.random()), el, t: 0, jit: Math.random() - 0.5 });
    }
    const ySrc = (yS0 + yS1) / 2;
    for (let k = wfBalls.length - 1; k >= 0; k--) {
      const b = wfBalls[k]; b.t += dt; const y = Yc(b.i), e = ent[b.i], eg = e.mx + b.jit * Math.max(0, e.gap - 4);
      let pts, ts;
      if (b.el) { pts = [[xSrc, ySrc], [eg, e.my], [xR, y], [xR, y], [eg, e.my], [tL + b.jit * 40, tY - 24]]; ts = [0.45, 0.16, 0.2, 0.16, 0.55]; }
      else { const d = ex[b.i][b.j], dg = d.mx + b.jit * Math.max(0, d.gap - 3); pts = [[xSrc, ySrc], [eg, e.my], [xR, y], [xR, y], [dg, d.my], [tR + b.jit * 40, tY - 24]]; ts = [0.45, 0.16, 0.2, 0.3, 0.55]; }
      const [px, py, seg] = follow(pts, ts, b.t);
      if (seg >= 5) { WF.tot++; if (b.el) WF.el++; wfBalls.splice(k, 1); continue; }
      if (seg === 2 || seg === 3) g.glow(xR, y, 16, c.warm, 0.55);
      if (seg >= 4 && !b.el) g.photon(px, py, Math.atan2(pts[seg + 1][1] - pts[seg][1], pts[seg + 1][0] - pts[seg][0]), 16); else g.ball(px, py, phone ? 3.6 : 4.5, c.neutron);
    }
    if (WF.tot > 400) { WF.el = Math.round(WF.el / 2); WF.tot = Math.round(WF.tot / 2); }
  }

  // ---------- scene 7: compound normalisation: three fates, counted ----------
  function drawNorm(g, S, dt) {
    const { W, H, c } = g;
    const phone = W < 600;
    const E = clamp(S.target.Einc, 1, 30);
    const fDir = 0.05 + 0.08 * smooth(0, 30, E), fPre = 0.5 * E * E / (E * E + 14 * 14), fCn = 1 - fDir - fPre;
    const tx = W * 0.8, tys = [H * 0.24, H * 0.54, H * 0.86], rd = phone ? 2.6 : 3.2, wide = phone ? 10 : 14, rows = Math.max(3, Math.floor(H * 0.15 / (rd * 2.05)));
    if (NORM.key !== E) { NORM.key = E; const n = rows * wide * 0.7; NORM.cnt = [Math.round(n * fDir), Math.round(n * fPre), Math.round(n * fCn)]; normBalls.length = 0; }
    const cx = W * 0.4, cy = H * 0.5, R = Math.min(W, H) * (phone ? 0.12 : 0.14);
    g.glow(cx, cy, R * 2.3, c.warm, 0.12 + 0.3 * fCn);
    g.nucleus(cx, cy, R, { N: 48, Z: 22, t: S.time, heat: 1 + 2 * fCn, jiggle: 0.6, alpha: 0.85 });
    g.label(`absorbed neutrons, ${E.toFixed(1)} MeV →`, W * 0.02, cy - R - 16, { color: c.neutron, size: 13, align: "left", bg: true });
    const mx = Math.max(...NORM.cnt, rows * wide * 0.5);
    const names = [["direct", "one glancing hit on the surface"], ["pre-equilibrium", "a knock or two, then out fast"], ["compound nucleus", "stayed inside: counted here, not moved"]];
    const tot = Math.max(1, sum(NORM.cnt));
    tys.forEach((ty, f) => {
      const top = pile(g, tx, ty, NORM.cnt[f], mx, rows, wide, rd, f === 2 ? c.warm : c.neutron);
      g.label(`${names[f][0]}: ${Math.round(100 * NORM.cnt[f] / tot)} %`, tx, top - 24, { color: c.ink, size: phone ? 12 : 14, weight: 600, bg: true, serif: f === 2 });
      if (!phone) g.label(names[f][1], tx, ty + 14, { color: c.faint, size: 11, bg: true });
    });
    S.lastSpawn += dt * 10;
    while (S.lastSpawn > 1) {
      S.lastSpawn -= 1; if (normBalls.length > 40) continue;
      const r = Math.random(), fate = r < fDir ? 0 : r < fDir + fPre ? 1 : 2, b = { fate, t: 0, jit: Math.random() - 0.5 };
      const y0 = cy + b.jit * R * 0.8, dest = [tx + b.jit * wide * rd * 1.6, tys[fate] - rd * 4];
      if (fate === 0) { const yh = cy - R * 0.98; b.pts = [[-20, yh], [cx - R * 0.2, yh], dest]; b.ts = [1.0, 0.7]; }
      else if (fate === 1) { b.pts = [[-20, y0], [cx - R * 0.85, y0], [cx - R * 0.1, cy - R * 0.4 * Math.sign(b.jit || 1)], [cx + R * 0.4, cy + R * 0.2], dest]; b.ts = [1.0, 0.12, 0.12, 0.45]; }
      else { const r2 = rng(((Math.random() * 1e9) | 0) + 1); b.pts = [[-20, y0], [cx - R * 0.85, y0]]; for (let k = 0; k < 6; k++) { const a = r2() * TAU, rr = Math.sqrt(r2()) * R * 0.7; b.pts.push([cx + Math.cos(a) * rr, cy + Math.sin(a) * rr]); } b.ts = [1.0, 0.3, 0.35, 0.4, 0.4, 0.4, 0.5]; }   // stays inside: wanders, then melts into the heat
      normBalls.push(b);
    }
    for (let k = normBalls.length - 1; k >= 0; k--) {
      const b = normBalls[k]; b.t += dt; const [x, y, seg, u] = follow(b.pts, b.ts, b.t);
      if (seg >= b.ts.length) { NORM.cnt[b.fate]++; normBalls.splice(k, 1); continue; }
      if (b.fate === 0 && seg === 1 && u < 0.25) g.glow(x, y, 16, c.neutron, 0.5);
      if (b.fate === 1 && seg === 3) g.line(x - 14, y, x, y, c.neutron, 2, 0.4);
      if (b.fate === 2 && seg >= 1) { const fa = seg === b.ts.length - 1 ? 1 - u : 1; g.glow(x, y, 14, c.warm, 0.55 * fa); g.dot(x, y, 4.5, c.warm, fa); }
      else g.ball(x, y, 5, c.neutron);
    }
    if (tot > 900) NORM.cnt = NORM.cnt.map((v) => Math.round(v / 2));
  }
})();
