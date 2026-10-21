/* Chapter 7: photon emission (gamma/), the cascade through discrete levels and isomers.
 * Scenes (S.mode): "emit"    = a hot state sheds photons (streak weight ~ E^3) that land in a crowd of states; a pile of landings builds;
 *                   "gdr"     = the giant dipole resonance: proton (hatched) and neutron (filled) clouds sloshing, and the strength landscape;
 *                   "m1"      = deformed nuclei: scissors (clouds rocking, vigour ~ beta), spin-flip arrows, upbend soft photons;
 *                   "cascade" = a random cascade from the bins down the measured branchings (stretched ladder, parity by fill);
 *                   "isomer"  = cascades as balls piling up on the isomer or the ground state; the isomer ratio depends on the entrance spin;
 *                   "capture" = the photon door against the neutron door (g.door, gap ~ width): (n, gamma).
 * Shapes follow gamma/parameters.py (GDR, M1 and scissors systematics, upbend), gamma/strength.py (Lorentzian forms),
 * gamma/transmission.py (T = 2 pi E^(2l+1) f), structure/levels.py (branchings; isomers = half-life >= 1 s) and
 * emission/multiple.py (cascade). Numbers are illustrative. */
(function () {
  const { TAU, clamp, lerp, smooth, rng } = WT.util;
  const KGR1 = 8.674e-8;                                             // kgr(1) = pi2h2c2 / 3, mb^-1 MeV^-2
  const slo = (E, Er, G, sig) => KGR1 * sig * G * G * E / ((E * E - Er * Er) ** 2 + E * E * G * G);
  function gdr(A, Z) { const N = A - Z; const Er = 31.2 * Math.pow(A, -1 / 3) + 20.6 * Math.pow(A, -1 / 6); const G = 0.026 * Math.pow(Er, 1.91); const sig = 1.2 * 120 * N * Z / (A * Math.PI * G); return { Er, G, sig }; }
  function fE1(E, A, Z) { const p = gdr(A, Z); return slo(E, p.Er, p.G, p.sig); }
  function fM1(E, A, beta) {                                           // spin-flip + scissors + upbend (strengthM1 3 systematics)
    const spin = slo(E, 18 / Math.pow(A, 1 / 6), 4.0, 0.03 * Math.pow(A, 5 / 6));
    const sc = slo(E, 5 / Math.pow(A, 0.1), 1.5, 1e-2 * Math.abs(beta) * Math.pow(A, 0.9));
    const up = 3.5e-8 * Math.exp(-0.8 * E) * Math.exp(-6.0 * Math.abs(beta));
    return { spin, sc, up, tot: spin + sc + up };
  }
  // a generic residual level density (constant temperature) for the photon weights
  const rhoCT = (Ex, T = 0.75) => (Ex < 0 ? 0 : Math.exp(Ex / T) / T);
  const A0 = 112, Z0 = 48;                                             // the cascade / capture nucleus: a cadmium-like odd-A nucleus with an 11/2- isomer

  // mock level scheme (MeV, 2J, parity) with an 11/2- isomer at 0.40 MeV
  const LV = [
    { E: 0, j2: 1, p: 1, name: "1/2+", gs: true },
    { E: 0.25, j2: 5, p: 1, name: "5/2+" },
    { E: 0.34, j2: 3, p: 1, name: "3/2+" },
    { E: 0.40, j2: 11, p: -1, name: "11/2−", iso: true },
    { E: 0.62, j2: 7, p: 1, name: "7/2+" },
    { E: 0.75, j2: 3, p: 1, name: "3/2+" },
    { E: 0.86, j2: 9, p: -1, name: "9/2−" },
    { E: 1.05, j2: 5, p: 1, name: "5/2+" },
    { E: 1.19, j2: 7, p: -1, name: "7/2−" },
    { E: 1.33, j2: 1, p: 1, name: "1/2+" },
    { E: 1.46, j2: 9, p: 1, name: "9/2+" },
    { E: 1.58, j2: 13, p: -1, name: "13/2−" },
  ];
  const ECONT = 1.7, ETOP = 7.0;                                        // continuum from 1.7 MeV up to the capture state
  // branchings between discrete levels: dipole-like weights E^3 exp(-|dJ|), |dJ| <= 2, never into an isomer unless spins allow
  function branches(i) { const L = LV[i]; const out = []; let s = 0; for (let k = 0; k < i; k++) { const d = Math.abs(L.j2 - LV[k].j2) / 2; if (d > 2) continue; const Eg = L.E - LV[k].E; const w = Eg ** 3 * Math.exp(-1.2 * d) * (L.p === LV[k].p ? 1 : 0.6); out.push([k, w]); s += w; } return out.map(([k, w]) => [k, w / s]); }
  const BR = LV.map((_, i) => (i ? branches(i) : []));
  /** One random cascade from (E, 2J) in the continuum down to the ground state or the isomer. */
  function walk(E, j2, r) {
    const path = [{ E, j2 }];
    let guard = 0;
    while (E > ECONT && guard++ < 40) {
      // sample a dipole photon energy with weight Eg^3 f_E1 rho(E - Eg)
      const n = 48; const w = []; let s = 0;
      for (let i = 0; i < n; i++) { const Eg = (i + 0.5) / n * E; const v = Eg ** 3 * fE1(Eg, A0, Z0) * rhoCT(E - Eg); w.push(v); s += v; }
      let u = r() * s, i = 0; while (i < n - 1 && u > w[i]) { u -= w[i]; i++; }
      E = E - (i + 0.5) / n * E;
      const dj = r() < 0.34 ? -2 : r() < 0.5 ? 2 : 0; j2 = Math.max(1, j2 + dj);
      if (E <= ECONT) {                                              // land on the nearest discrete level of a compatible spin
        let best = -1, bd = 1e9; LV.forEach((L, k) => { const d = Math.abs(L.E - E) + 0.25 * Math.abs(L.j2 - j2) / 2; if (Math.abs(L.j2 - j2) <= 4 && d < bd) { bd = d; best = k; } });
        if (best < 0) best = LV.length - 1;
        E = LV[best].E; j2 = LV[best].j2; path.push({ E, j2, lv: best }); break;
      }
      path.push({ E, j2 });
    }
    let lv = path[path.length - 1].lv ?? 0;
    guard = 0;
    while (!LV[lv].gs && !LV[lv].iso && guard++ < 20) {
      let u = r(), k = 0; for (const [kk, p] of BR[lv]) { if (u < p) { k = kk; break; } u -= p; k = kk; }
      lv = k; path.push({ E: LV[lv].E, j2: LV[lv].j2, lv });
    }
    return path;
  }
  const isoCache = {};
  function isomerShare(j2) { if (isoCache[j2] !== undefined) return isoCache[j2]; const r = rng(1000 + j2); let n = 0; for (let i = 0; i < 300; i++) { const p = walk(ETOP, j2, r); if (LV[p[p.length - 1].lv].iso) n++; } return (isoCache[j2] = n / 300); }
  const paths = [];
  const sum = (a) => a.reduce((s, v) => s + v, 0);
  function pick(ws, r) { let u = r * sum(ws); for (let i = 0; i < ws.length; i++) { if (u < ws[i]) return i; u -= ws[i]; } return ws.length - 1; }
  function follow(pts, ts, t) {
    for (let i = 0; i < ts.length; i++) { if (t < ts[i]) { const u = t / ts[i]; return [lerp(pts[i][0], pts[i + 1][0], u), lerp(pts[i][1], pts[i + 1][1], u), i, u]; } t -= ts[i]; }
    const p = pts[pts.length - 1]; return [p[0], p[1], ts.length, 1];
  }
  /** A photon streak whose thickness and brightness carry its weight (0..1). */
  function streak(g, x, y, a, len, wgt, alpha = 1) {
    const ctx = g.ctx; ctx.save(); ctx.globalAlpha = alpha * (0.3 + 0.7 * wgt); ctx.strokeStyle = g.c.photon; ctx.lineWidth = 1 + 3.2 * wgt; ctx.lineCap = "round"; ctx.beginPath();
    for (let i = 0; i <= 20; i++) { const s = (i / 20 - 0.5) * len, w = Math.sin(i * 1.4) * (2 + 2 * wgt); const px = x + Math.cos(a) * s - Math.sin(a) * w, py = y + Math.sin(a) * s + Math.cos(a) * w; i ? ctx.lineTo(px, py) : ctx.moveTo(px, py); }
    ctx.stroke(); ctx.restore(); if (wgt > 0.2) g.glow(x, y, len * 0.7, g.c.photon, 0.3 * wgt * alpha);
  }
  /** A cloud of protons or neutrons: protons hatched with an outline, neutrons a soft fill. Never two fills on top of each other. */
  function cloud(g, x, y, rx, ry, rot, color, hatch, alpha = 1) {
    const ctx = g.ctx; ctx.save(); ctx.globalAlpha = alpha; ctx.translate(x, y); ctx.rotate(rot);
    ctx.beginPath(); ctx.ellipse(0, 0, rx, ry, 0, 0, TAU);
    if (hatch) {
      ctx.save(); ctx.clip(); ctx.strokeStyle = g.rgba(color, 0.75); ctx.lineWidth = 1.6;
      const m = Math.max(rx, ry) * 1.5; ctx.beginPath(); for (let s = -m * 2; s < m * 2; s += 7) { ctx.moveTo(s - m, -m); ctx.lineTo(s + m, m); } ctx.stroke(); ctx.restore();
      ctx.beginPath(); ctx.ellipse(0, 0, rx, ry, 0, 0, TAU); ctx.strokeStyle = color; ctx.lineWidth = 2.6; ctx.stroke();
    } else {
      const gr = ctx.createRadialGradient(0, 0, 0, 0, 0, Math.max(rx, ry)); gr.addColorStop(0, g.rgba(color, 0.42)); gr.addColorStop(1, g.rgba(color, 0.16));
      ctx.fillStyle = gr; ctx.fill(); ctx.strokeStyle = g.rgba(color, 0.9); ctx.lineWidth = 2; ctx.setLineDash([5, 4]); ctx.stroke();
    }
    ctx.restore();
  }
  function fmtE(keV) { return keV < 1 ? `${(keV * 1000).toFixed(0)} eV` : keV < 1000 ? `${keV.toFixed(keV < 10 ? 1 : 0)} keV` : `${(keV / 1000).toFixed(1)} MeV`; }

  // photon weights from a state at E: Eg^3 f_E1(Eg) rho(E - Eg) on NB bins
  function dropWeights(E, NB) { const w = []; for (let i = 0; i < NB; i++) { const Eg = (i + 0.5) / NB * E; w.push(Eg ** 3 * fE1(Eg, A0, Z0) * rhoCT(E - Eg)); } return w; }

  const EM = { key: null, cnt: [], w: [], fly: [], queue: 0, acc: 0 };
  const M1 = { fly: [], acc: [0, 0, 0] };
  const ISO = { key: null, iso: 0, gs: 0, balls: [], acc: 0 };
  const CAP = { key: null, g: 0, n: 0, balls: [], acc: 0 };

  WT.chapter("gamma", {
    num: "Chapter 7", title: "Shedding light", short: "Photons",
    lead: "When no particle can leave, or none happens to, the nucleus cools by emitting photons: gamma rays, particles of very high-energy light. This exit is open at every energy.",
    html: `
<div class="step">
  <p>The picture shows the energy ladder again, with a hot state glowing at 8 MeV (million electron-volts). It sheds photons (γ); each one carries away the energy of the drop, <i>E<sub>γ</sub></i>, and lands the nucleus on a lower state. Below 2 MeV the states are a few named rungs; above, they are a crowd that thickens steeply with energy (the grey dots). Each photon is drawn thicker and brighter in proportion to <i>E<sub>γ</sub></i>³, which grows steeply with photon energy (for dipole photons, the most common kind).</p>
  <div class="formula">T<sub>γ</sub>(E<sub>γ</sub>) = 2π · E<sub>γ</sub><sup>2l+1</sup> · f(E<sub>γ</sub>)</div>
  <p>Here <i>T<sub>γ</sub></i> is the photon's transmission coefficient (the “how open is the door” factor of Chapter 6), <i>l</i> = 1 for dipole photons, and <i>f</i>(<i>E<sub>γ</sub></i>) is the <b>photon strength</b>, how readily the nucleus radiates at that energy. The chance of a drop is <i>T<sub>γ</sub></i> times the crowd of states where it lands. Small drops land in a big crowd but are faint; big drops are bright but find few states. The pile beside the ladder collects where they land.</p>
  <div class="ctl"><label for="gm-e0">Start energy</label><input id="gm-e0" type="range" data-bind="E0" min="3" max="9" step="0.5" value="8"><output data-show="E0" data-fmt="1"></output></div>
  <div class="btns"><button class="btn" data-act="emit">Emit 100</button></div>
  <p>The pile peaks a few MeV below the start: the likeliest photons carry about 2 to 4 MeV. Move the start energy and the peak moves with it.</p>
</div>
<div class="step">
  <h3>The whole nucleus rings</h3>
  <p>On the left, the nucleus's protons (hatched) and neutrons (filled) swing back and forth against each other. On the right is the photon strength <i>f</i> at each photon energy, with height on a log scale (each step up is ten times more). Its big peak is the <b>giant dipole resonance</b>: all the protons sloshing against all the neutrons. The frequency of that motion sets the photon energy the nucleus absorbs and emits most readily.</p>
  <div class="ctl"><label for="gm-a">Mass number A</label><input id="gm-a" type="range" data-bind="A" min="40" max="240" step="1" value="112"><output data-show="A" data-fmt="0"></output></div>
  <p>Drag the mass number A, the count of protons plus neutrons: the sloshing slows for heavy nuclei. They ring around 12 to 14 MeV; light ones near 20. Photons from a decaying nucleus carry only a few MeV, far below the peak, so what matters most is the shaded low-energy tail.</p>
</div>
<div class="step">
  <h3>Scissors and the upbend</h3>
  <p>The picture shows a deformed nucleus as two footballs, protons (hatched) and neutrons (filled). They can rock against each other like the blades of scissors. This <b>scissors mode</b> is a magnetic vibration near 3 MeV, and each swing can send off a photon. A second magnetic source, near 8 MeV, is <b>spin-flip</b>: single nucleons flipping their spin (the small arrows), which happens in any shape.</p>
  <div class="ctl"><label for="gm-b">Deformation β₂</label><input id="gm-b" type="range" data-bind="beta" min="0" max="0.35" step="0.01" value="0.25"><output data-show="beta" data-fmt="2"></output></div>
  <p>Drag the deformation β₂, a measure of how stretched the nucleus is (0 is a sphere). The more stretched, the harder the blades rock and the more scissors photons fly; a sphere has no blades. At the lowest photon energies the strength rises again: the <b>upbend</b>, seen in many measured nuclei as a trickle of soft photons. The engine makes it weaker as the nucleus deforms. An added option swaps the default scissors strength for newer systematics fitted to Oslo measurements, about four to five times stronger in the heaviest nuclei.</p>
</div>
<div class="step">
  <h3>Down the ladder</h3>
  <p>The picture shows the ladder with bins at the top, where states are too dense to list (Chapter 5), and named measured levels below (stretched, so they can be read), each with its spin and parity: a solid rung is parity +, a hollow rung parity −. From a bin, the nucleus emits photons one after another, each landing in a lower bin, until it reaches the measured levels. From there the engine stops estimating: each measured level decays with measured probabilities, called <b>branching ratios</b>, and it follows those.</p>
  <div class="btns"><button class="btn" data-act="drop">Drop a cascade</button></div>
  <p>Press the button a few times. Each press follows one possible history. The upper part changes every time, but the ending always follows one of a few measured paths.</p>
</div>
<div class="step">
  <h3>Shelves that hold</h3>
  <p>The picture marks one level as special: the 11/2− level at 0.40 MeV. Its spin is so different from the levels below it that a photon can hardly connect them, so it lives for seconds, hours or even years. A long-lived level like this is an <b>isomer</b>, and whatever lands there stays. The engine treats any level that lives longer than one second as an end point of its own. Each ball is one cascade, dropping rung to rung and shedding a photon at each drop; it ends in the isomer's pile or the ground state's.</p>
  <div class="ctl"><label for="gm-j">Entrance spin</label><input id="gm-j" type="range" data-bind="J0" min="0" max="8" step="1" value="2" data-instant><output id="gm-jout">5/2</output></div>
  <p>Drag the entrance spin, the spin of the state where the cascades start, and watch the piles start again. The share that ends on the isomer, the <b>isomer ratio</b>, depends on that starting spin. A high-spin start feeds the high-spin isomer; a low-spin start slides past it to the ground state, the lowest level.</p>
</div>
<div class="step">
  <h3>Capture</h3>
  <p>The picture shows a nucleus that has just absorbed a slow neutron, with two exit doors, as in Chapter 6: photons (top) and neutrons (right). Below the neutron threshold, the energy needed to free a neutron, the photon door is the only one. Just above it it has one rival: the neutron going back out. Each door's gap is its <b>width</b>, in eV, which measures how fast the nucleus decays through it. The photon width hardly changes with energy; the neutron width grows as the neutron gets faster.</p>
  <div class="ctl"><label for="gm-e">Neutron energy</label><input id="gm-e" type="range" data-bind="lgE" min="-2" max="3.3" step="0.02" value="0"><output id="gm-eout">1.0 keV</output></div>
  <p>Drag the neutron energy, from 10 eV to 2 MeV. <b>Capture</b>, written (n,γ), means the neutron stays and a photon leaves: at 10 eV it wins most of the time; above a few keV the neutron door has swung wide and capture becomes a small share. The total photon width at threshold has been measured for hundreds of nuclei from their resonances, so it is a check on the photon strength. By default the engine only compares against it; an added option scales each nucleus's photon strength until the two agree, for every nucleus in the cascade.</p>
  <div class="aside">In the code: <code>gamma/parameters.py</code> (giant resonance, spin-flip, scissors and upbend systematics; tabulated strengths), <code>gamma/strength.py</code> (<i>f</i>(E<sub>γ</sub>) for every multipole), <code>gamma/transmission.py</code> (T<sub>γ</sub> and the average radiative width), <code>structure/levels.py</code> (branching ratios, isomers), <code>emission/multiple.py</code> (the cascade). Added options, off by default: <code>gamma/scissors.py</code> (stronger scissors), <code>gamma/ggnorm.py</code> (match the measured ⟨Γγ⟩), <code>gamma/actphys.py</code> (both, for actinides).</div>
</div>`,
    setup(S) {
      S.set("mode", "emit"); S.to("E0", 8, true); S.to("A", 112, true); S.to("beta", 0.25, true); S.to("J0", 2, true); S.to("lgE", 0, true);
      S.dropN = 0; S.jShown = -1; S.eShown = -99; S.autoDrop = 0;
      S.on("emit", () => { EM.queue += 100; });
      S.on("drop", () => { S.dropN++; S.autoDrop = 0; const r = rng(S.dropN * 131 + 7); const j2 = 2 * Math.round(1 + r() * 3) + 1; paths.push({ p: walk(ETOP - r() * 1.5, j2, r), t0: S.time }); if (paths.length > 4) paths.shift(); });
    },
    steps: [
      (S) => { S.set("mode", "emit"); },
      (S) => { S.set("mode", "gdr"); },
      (S) => { S.set("mode", "m1"); },
      (S) => { S.set("mode", "cascade"); if (!paths.length) { const r = rng(3); paths.push({ p: walk(6.5, 5, r), t0: S.time }); } },
      (S) => { S.set("mode", "isomer"); },
      (S) => { S.set("mode", "capture"); },
    ],
    frame(g, S, dt) {
      const J = Math.round(S.target.J0 ?? 2);
      if (J !== S.jShown) { S.jShown = J; const o = document.getElementById("gm-jout"); if (o) o.textContent = `${2 * J + 1}/2`; }
      if (Math.abs(S.lgE - S.eShown) > 0.004) { S.eShown = S.lgE; const o = document.getElementById("gm-eout"); if (o) o.textContent = WT.dec ? WT.dec(fmtE(Math.pow(10, S.lgE))) : fmtE(Math.pow(10, S.lgE)); }
      if (S.mode === "emit") drawEmit(g, S, dt);
      else if (S.mode === "gdr") drawGdr(g, S);
      else if (S.mode === "m1") drawM1(g, S, dt);
      else if (S.mode === "cascade") drawCascade(g, S, dt);
      else if (S.mode === "isomer") drawIsomer(g, S, dt);
      else drawCapture(g, S, dt);
    },
  });

  // ---------- scene 1: photons landing in the crowd ----------
  function drawEmit(g, S, dt) {
    const { W, H, c } = g;
    const phone = W < 600;
    const E0 = clamp(S.target.E0, 3, 9), Emax = 9.5, NB = 38;
    const xc = W * (phone ? 0.27 : 0.36), hw = Math.min(W * (phone ? 0.2 : 0.17), 130);
    const yBot = H * 0.9, yTop = H * 0.07, Y = (E) => yBot - (yBot - yTop) * E / Emax;
    const px0 = xc + hw + 14, pxMax = W * 0.97, rd = phone ? 2.2 : 2.6, cap = Math.floor((pxMax - px0) / (rd * 2.1));
    if (EM.key !== E0) { EM.key = E0; EM.w = dropWeights(E0, NB); const wm = Math.max(...EM.w); EM.cnt = EM.w.map((v) => Math.round(0.45 * cap * v / wm)); EM.fly.length = 0; }
    // rungs: discrete at the bottom, then a crowd of states thickening upward
    [0, 0.5, 0.9, 1.25, 1.5, 1.75, 1.95].forEach((e, i) => g.line(xc - hw, Y(e), xc + hw, Y(e), c.ink, i ? 1.4 : 3, 0.8));
    const r = rng(11);
    for (let e = 2.1; e < Emax; e += 0.12) {
      const n = Math.max(1, Math.min(26, Math.round(26 * Math.exp((e - E0) / 0.75))));
      for (let k = 0; k < n; k++) g.dot(xc - hw + r() * 2 * hw, Y(e + r() * 0.12), 1.5, c.soft, e > E0 ? 0.18 : 0.55);
      for (let k = n; k < 26; k++) { r(); r(); }
    }
    g.label("energy ↑", xc - hw, yTop - 12, { color: c.faint, size: 12, align: "left" });
    if (!phone) { g.label("named levels", xc - hw - 10, Y(1), { color: c.soft, size: 12, align: "right" }); g.label("a crowd of states", xc - hw - 10, Y(E0 - 0.6), { color: c.soft, size: 12, align: "right" }); }
    // the hot state
    const hx = xc - hw * 0.65, hy = Y(E0);
    g.glow(hx, hy, 26, c.warm, 0.6); g.dot(hx, hy, 7, c.warm);
    g.label(phone ? `${E0} MeV` : `hot state, ${E0.toFixed(1)} MeV`, hx, hy - 20, { color: c.warm, size: 13, weight: 600, bg: true });
    // the pile of landings, beside the ladder at the landing height
    const maxC = Math.max(...EM.cnt), sc = maxC > cap ? cap / maxC : 1;
    let iPk = 0; EM.w.forEach((v, i) => { if (v > EM.w[iPk]) iPk = i; });
    for (let i = 0; i < NB; i++) {
      const Eg = (i + 0.5) / NB * E0, y = Y(E0 - Eg), n = Math.round(EM.cnt[i] * sc);
      for (let k = 0; k < n; k++) g.dot(px0 + k * rd * 2.1, y, rd, c.photon, 0.85);
    }
    const EgPk = (iPk + 0.5) / NB * E0, yPk = Y(E0 - EgPk), nPk = Math.round(EM.cnt[iPk] * sc);
    g.label(`most photons ≈ ${EgPk.toFixed(1)} MeV`, Math.min(px0 + nPk * rd * 2.1 + 10, pxMax - 150), yPk - 14, { color: c.photon, size: 13, weight: 600, align: "left", bg: true });
    if (!phone) {
      g.label("small drops: faint (E³ tiny)", px0, Y(E0 - 0.25) - 16, { color: c.faint, size: 12, align: "left", bg: true });
      g.label("big drops: bright, but few states to land on", px0, Y(Math.min(1.2, E0 * 0.2)) - 14, { color: c.faint, size: 12, align: "left", bg: true });
    }
    // photons in flight
    EM.acc += dt * (EM.queue > 0 ? 45 : 3);
    while (EM.acc > 1) {
      EM.acc -= 1; if (EM.queue > 0) EM.queue--; if (EM.fly.length > 60) continue;
      const i = pick(EM.w, Math.random()), Eg = (i + 0.5) / NB * E0 + (Math.random() - 0.5) * E0 / NB;
      EM.fly.push({ i, Eg, t: 0, x1: xc - hw * 0.3 + Math.random() * hw * 1.2 });
    }
    for (let k = EM.fly.length - 1; k >= 0; k--) {
      const f = EM.fly[k]; f.t += dt; const u = f.t / 0.7, y1 = Y(E0 - f.Eg);
      if (u >= 1) { EM.cnt[f.i]++; EM.fly.splice(k, 1); continue; }
      const x = lerp(hx, f.x1, u), y = lerp(hy, y1, u), wgt = Math.min(1, (f.Eg / 5) ** 3);
      streak(g, x, y, Math.atan2(y1 - hy, f.x1 - hx), 22, wgt);
      if (u > 0.85) g.glow(f.x1, y1, 10, c.photon, 0.6);
    }
  }

  // ---------- the strength landscape (log height), for gdr ----------
  function landscape(g, x0, x1, yB, yT, Emax, f) {
    const { c } = g;
    const lmin = -9.6, lmax = -5.2;
    const X = (E) => x0 + (x1 - x0) * E / Emax, Yv = (v) => yB - (yB - yT) * (clamp(Math.log10(Math.max(v, 1e-12)), lmin, lmax) - lmin) / (lmax - lmin);
    const tot = []; for (let i = 0; i <= 160; i++) { const E = 0.1 + (Emax - 0.1) * i / 160; tot.push([X(E), Yv(f(E))]); }
    g.ground(tot, c.photon, 120, 0.18);
    g.clip(x0 - 5, yT - 40, X(7) - x0 + 5, yB - yT + 200); g.ground(tot, c.photon, 120, 0.35); g.restore();
    g.poly(tot, c.ink, 2.2, 0.9);
    return { X, Yv };
  }

  // ---------- scene 2: the giant dipole resonance ----------
  function drawGdr(g, S) {
    const { W, H, c } = g;
    const A = Math.round(clamp(S.A, 40, 240)), Z = Math.round(A / (1.98 + 0.0155 * Math.pow(A, 2 / 3)));
    const p = gdr(A, Z);
    const phone = W < 600;
    const cx = W * (phone ? 0.3 : 0.24), cy = H * (phone ? 0.2 : 0.42), R = Math.min(W, H) * (phone ? 0.1 : 0.14) * Math.cbrt(A / 112);
    const om = p.Er * 0.5, s = Math.sin(S.time * om), d = R * 0.2 * s;
    cloud(g, cx - d, cy, R, R, 0, c.neutron, false);
    cloud(g, cx + d, cy, R, R, 0, c.proton, true);
    if (!phone) {
      g.label("protons", cx + R + 16, cy - R * 0.5, { color: c.proton, size: 13, weight: 600, align: "left", bg: true });
      g.label("neutrons", cx - R - 16, cy + R * 0.5, { color: c.neutron, size: 13, weight: 600, align: "right", bg: true });
    }
    g.label(`A = ${A}: rings at ${p.Er.toFixed(1)} MeV`, cx, cy + R + 26, { color: c.ink, size: 13, weight: 600, bg: true });
    const x0 = W * (phone ? 0.08 : 0.52), x1 = W * 0.95, yB = H * (phone ? 0.9 : 0.8), yT = H * (phone ? 0.5 : 0.14);
    const { X, Yv } = landscape(g, x0, x1, yB, yT, 25, (E) => fE1(E, A, Z));
    const fpk = fE1(p.Er, A, Z);
    g.label(phone ? `peak ${p.Er.toFixed(1)} MeV` : `giant resonance at ${p.Er.toFixed(1)} MeV`, X(p.Er), Yv(fpk) - 18, { color: c.ink, size: 13, weight: 600, bg: true });
    g.label(`width ≈ ${p.G.toFixed(1)} MeV`, X(p.Er), Yv(fpk) + 22, { color: c.soft, size: 12, bg: true });
    g.label(phone ? "decays use this" : "shaded: the tail decays use", X(3.5), yB - 14, { color: c.photon, size: 12, weight: 600, bg: true });
    g.label("photon energy (MeV) →", x1, yB + 16, { color: c.faint, size: 12, align: "right" });
    if (!phone) g.label("photon strength f (log scale) ↑", x0, yT - 14, { color: c.faint, size: 12, align: "left" });
  }

  // ---------- scene 3: scissors, spin-flip, upbend as three photon sources ----------
  function drawM1(g, S, dt) {
    const { W, H, c } = g;
    const A = 160, beta = clamp(S.beta, 0, 0.35);
    const phone = W < 600;
    const cx = W * 0.45, cy = H * 0.47, R = Math.min(W, H) * (phone ? 0.15 : 0.17);
    const m = fM1(5 / Math.pow(A, 0.1), A, beta), m0 = fM1(5 / Math.pow(A, 0.1), A, 0.35);
    const vig = beta / 0.35, amp = 0.42 * vig, ph = S.time * 4.2, th = amp * Math.sin(ph);
    const rx = R * (1 + beta * 1.5), ry = R * (1 - beta * 0.9);
    cloud(g, cx, cy, rx, ry, -th, c.neutron, false);
    cloud(g, cx, cy, rx, ry, th, c.proton, true);
    // spin-flip: a few nucleons flipping their spin arrows, in any shape
    for (let k = 0; k < 6; k++) {
      const a = k * 1.05 + 0.4, rr = R * 0.5, x = cx + Math.cos(a) * rr * (1 + beta), y = cy + Math.sin(a) * rr * (1 - beta * 0.8);
      const up = Math.sin(S.time * 1.3 + k * 2.1) > 0 ? -1 : 1;
      g.dot(x, y, 4.5, c.ink, 0.9); g.arrow(x, y - up * 11, x, y + up * 13, c.ink, 2, 0.9, 7);
    }
    // photons: scissors ~3 MeV (rate grows with beta), spin-flip ~8 MeV (steady), upbend: soft, fewer as it deforms
    const rates = [5 * vig * vig + 0.0, 1.2, 4 * Math.exp(-6 * beta)];
    for (let kind = 0; kind < 3; kind++) {
      M1.acc[kind] += dt * rates[kind];
      while (M1.acc[kind] > 1) { M1.acc[kind] -= 1; if (M1.fly.length < 40) M1.fly.push({ kind, a: Math.random() * TAU, t: 0 }); }
    }
    for (let k = M1.fly.length - 1; k >= 0; k--) {
      const f = M1.fly[k]; f.t += dt; const u = f.t / 1.4; if (u > 1) { M1.fly.splice(k, 1); continue; }
      const dist = R * 1.1 + u * Math.min(W, H) * 0.32, x = cx + Math.cos(f.a) * dist * (1 + beta * 0.5), y = cy + Math.sin(f.a) * dist;
      const wgt = f.kind === 1 ? 1 : f.kind === 0 ? 0.45 : 0.08, len = f.kind === 1 ? 30 : f.kind === 0 ? 22 : 12;
      streak(g, x, y, f.a, len, wgt, 1 - smooth(0.7, 1, u));
    }
    const ls = phone ? 12 : 13;
    const Esc = 5 / Math.pow(A, 0.1), Esf = 18 / Math.pow(A, 1 / 6);
    g.label(beta < 0.03 ? "a sphere has no blades: no scissors" : `scissors ≈ ${Esc.toFixed(1)} MeV: strength ${(m.sc / m0.sc * 100).toFixed(0)} % of the most stretched`, W * 0.5, H * 0.06, { color: c.ink, size: phone ? 13 : 15, weight: 600, serif: true, bg: true });
    g.label(`spin-flip ≈ ${Esf.toFixed(1)} MeV: steady, any shape (thick photons)`, W * 0.5, H * 0.06 + 24, { color: c.soft, size: ls, bg: true });
    g.label(`upbend below 2 MeV: soft photons, ${beta < 0.08 ? "plenty" : beta < 0.2 ? "fewer" : "few"} at this shape`, W * 0.5, H * 0.94, { color: c.soft, size: ls, bg: true });
    if (!phone) { g.label("protons", cx + rx + 14, cy - ry * 0.8, { color: c.proton, size: 13, weight: 600, align: "left", bg: true }); g.label("neutrons", cx - rx - 14, cy + ry * 0.8, { color: c.neutron, size: 13, weight: 600, align: "right", bg: true }); }
  }

  // ---------- ladder with a stretched bottom (named levels readable), parity by fill ----------
  function ladder2(g, xc, hw) {
    const { H, c } = g, ctx = g.ctx;
    const Emax = ETOP + 0.5, yBot = H * 0.9, yMid = H * 0.5, yTop = H * 0.07;
    const Y = (E) => (E <= ECONT ? yBot - (yBot - yMid) * E / ECONT : yMid - (yMid - yTop) * (E - ECONT) / (Emax - ECONT));
    g.line(xc - hw, yBot + 4, xc - hw, yTop, c.soft, 2, 0.7); g.line(xc + hw, yBot + 4, xc + hw, yTop, c.soft, 2, 0.7);
    // bins: faint stripes that fade at both ends
    for (let b = 0; b < 16; b++) {
      const e1 = ECONT + (ETOP - ECONT) * b / 16, e2 = e1 + (ETOP - ECONT) / 16;
      const gr = ctx.createLinearGradient(xc - hw, 0, xc + hw, 0); gr.addColorStop(0, g.rgba(c.ink, 0)); gr.addColorStop(0.5, g.rgba(c.ink, b % 2 ? 0.07 : 0.13)); gr.addColorStop(1, g.rgba(c.ink, 0));
      ctx.fillStyle = gr; ctx.fillRect(xc - hw, Y(e2), 2 * hw, Y(e1) - Y(e2));
    }
    // levels: + solid, - hollow; isomer in the accent colour; labels spread so they never stack
    const rows = LV.map((L, i) => ({ i, y: Y(L.E), ly: Y(L.E) })).sort((a, b) => b.y - a.y);
    for (let k = 1; k < rows.length; k++) rows[k].ly = Math.min(rows[k].ly, rows[k - 1].ly - 13);
    rows.forEach((rw) => {
      const L = LV[rw.i], col = L.iso ? c.accent : c.ink, th = L.iso || L.gs ? 6 : 4.5;
      ctx.save(); ctx.fillStyle = L.p > 0 ? col : c.paper; ctx.strokeStyle = col; ctx.lineWidth = 1.4;
      ctx.beginPath(); ctx.rect(xc - hw, rw.y - th / 2, 2 * hw, th); ctx.fill(); ctx.stroke(); ctx.restore();
      g.line(xc + hw + 2, rw.y, xc + hw + 14, rw.ly, c.faint, 1, 0.6);
      g.label(L.name, xc + hw + 17, rw.ly, { color: L.iso ? c.accent : c.soft, size: 11, align: "left", weight: L.iso ? 700 : 500 });
    });
    return Y;
  }

  // ---------- scene 4: random cascades ----------
  function drawCascade(g, S, dt) {
    const { W, H, c } = g;
    const phone = W < 600;
    const xc = W * (phone ? 0.42 : 0.4), hw = Math.min(W * (phone ? 0.2 : 0.16), 120);
    const Y = ladder2(g, xc, hw);
    S.autoDrop += dt; if (S.autoDrop > 4.5) S.handlers.drop();
    paths.forEach((P, k) => drawPath(g, P.p, Y, xc, hw, k === paths.length - 1 ? 1 : 0.25, S.time - P.t0));
    g.label("ground state", xc - hw - 10, Y(0), { color: c.ink, size: 12, align: "right" });
    g.label(phone ? "isomer" : "isomer: long-lived", xc - hw - 10, Y(0.4), { color: c.accent, size: 12, align: "right", weight: 600 });
    if (!phone) {
      g.label("bins: too dense to list", xc - hw - 10, Y(5.5), { color: c.soft, size: 12, align: "right" });
      g.label("one photon at a time", xc - hw - 10, Y(3.6), { color: c.soft, size: 12, align: "right" });
      g.label("measured branching ratios", xc - hw - 10, Y(1.2), { color: c.soft, size: 12, align: "right" });
      g.label("▬ parity +   ▭ parity −", xc + hw + 17, Y(ETOP), { color: c.soft, size: 12, align: "left" });
    }
  }
  function pathX(xc, hw, i) { return xc + Math.sin(i * 1.7 + 0.6) * hw * 0.55; }
  function drawPath(g, p, Y, xc, hw, alpha, age) {
    const { c } = g;
    const steps = p.length - 1, shown = Math.min(steps, Math.floor(age * 2.5) + 1);
    for (let i = 0; i < shown; i++) {
      const a = p[i], b = p[i + 1];
      g.arrow(pathX(xc, hw, i), Y(a.E), pathX(xc, hw, i + 1), Y(b.E), c.photon, 1.6, alpha, 7);
      if (i === shown - 1 && shown < steps + 1 && alpha > 0.5) { const u = (age * 2.5) % 1; streak(g, lerp(pathX(xc, hw, i), pathX(xc, hw, i + 1), u) + 20, lerp(Y(a.E), Y(b.E), u), 0.3, 18, Math.min(1, ((a.E - b.E) / 4) ** 3)); }
    }
    const last = p[p.length - 1];
    if (shown >= steps && last.lv !== undefined) g.glow(pathX(xc, hw, steps), Y(last.E), 16, LV[last.lv].iso ? c.accent : c.warm, 0.6 * alpha);
  }

  // ---------- scene 5: cascades as balls, piling up on the isomer or the ground state ----------
  function drawIsomer(g, S, dt) {
    const { W, H, c } = g;
    const phone = W < 600;
    const xc = W * (phone ? 0.55 : 0.5), hw = Math.min(W * (phone ? 0.17 : 0.14), 110);
    const Y = ladder2(g, xc, hw);
    const j2 = 2 * Math.round(clamp(S.target.J0, 0, 8)) + 1;
    if (ISO.key !== j2) { ISO.key = j2; const r = rng(400 + j2); ISO.iso = 0; ISO.gs = 0; for (let k = 0; k < 30; k++) { const p = walk(ETOP, j2, r); if (LV[p[p.length - 1].lv].iso) ISO.iso++; else ISO.gs++; } ISO.balls.length = 0; }
    const share = isomerShare(j2);
    // entrance
    const ex = pathX(xc, hw, 0), ey = Y(ETOP);
    g.glow(ex, ey, 24, c.warm, 0.6); g.dot(ex, ey, 6, c.warm);
    g.label(`entrance: J = ${j2}/2`, xc - hw - 10, ey, { color: c.warm, size: 13, align: "right", weight: 600, bg: true });
    // piles to the left of the isomer and ground rungs
    const rd = phone ? 2.4 : 3, perRow = Math.floor((xc - hw - 16 - W * 0.03) / (rd * 2.1)), cap = perRow * 3;
    const mx = Math.max(ISO.iso, ISO.gs, cap * 0.6), sc = mx > cap ? cap / mx : 1;
    const heap = (n, y, col) => { const m = Math.round(n * sc); for (let k = 0; k < m; k++) { const row = Math.floor(k / perRow), cl = k % perRow; g.dot(xc - hw - 10 - cl * rd * 2.1, y - rd - row * rd * 2.1, rd, col, 0.9); } };
    heap(ISO.iso, Y(0.4) - 3, c.accent); heap(ISO.gs, Y(0) - 4, c.ink);
    const tot = Math.max(1, ISO.iso + ISO.gs);
    g.label(`isomer: ${ISO.iso} (${Math.round(100 * ISO.iso / tot)} %)`, W * 0.03, Y(0.4) - rd * 7 - 12, { color: c.accent, size: 13, weight: 700, align: "left", bg: true });
    g.label(`ground state: ${ISO.gs} (${Math.round(100 * ISO.gs / tot)} %)`, W * 0.03, Y(0) + 18, { color: c.ink, size: 13, weight: 600, align: "left", bg: true });
    g.label(phone ? `many cascades: ≈ ${Math.round(share * 100)} % isomer` : `over many cascades from J = ${j2}/2: ≈ ${Math.round(share * 100)} % end on the isomer`, W * 0.5, H * 0.035, { color: c.ink, size: phone ? 13 : 15, weight: 600, serif: true, bg: true });
    // the balls
    ISO.acc += dt * 2.2;
    while (ISO.acc > 1) { ISO.acc -= 1; if (ISO.balls.length < 14) ISO.balls.push({ p: walk(ETOP, j2, Math.random), t: 0, off: (Math.random() - 0.5) * hw * 0.5 }); }
    const hop = 0.32;
    for (let k = ISO.balls.length - 1; k >= 0; k--) {
      const b = ISO.balls[k]; b.t += dt; const n = b.p.length - 1, i = Math.floor(b.t / hop), u = (b.t % hop) / hop;
      if (i >= n) { if (LV[b.p[n].lv].iso) ISO.iso++; else ISO.gs++; ISO.balls.splice(k, 1); continue; }
      const a = b.p[i], z = b.p[i + 1], uu = smooth(0, 1, u);
      const x = lerp(pathX(xc, hw, i), pathX(xc, hw, i + 1), uu) + b.off * 0.3, y = lerp(Y(a.E), Y(z.E), uu);
      g.ball(x, y, 5, i + 1 === n && LV[z.lv]?.iso ? c.accent : c.warm);
      if (u < 0.6) { const Eg = a.E - z.E; streak(g, x + 14 + u * 60, y - u * 10, -0.15, 16, Math.min(1, (Eg / 4) ** 3), 1 - u / 0.6); }
    }
    if (tot > 600) { ISO.iso = Math.round(ISO.iso / 2); ISO.gs = Math.round(ISO.gs / 2); }
  }

  // ---------- scene 6: capture against re-emission, through two doors ----------
  function drawCapture(g, S, dt) {
    const { W, H, c } = g;
    const lg = clamp(S.lgE, -2, 3.3), EkeV = Math.pow(10, lg), EeV = EkeV * 1000;
    const D0 = 200, Gg = 0.12;
    const Ts = 1 - Math.exp(-2 * Math.PI * 1.2e-4 * Math.sqrt(EeV));
    const Tp = 1 - Math.exp(-2 * Math.PI * 1.0e-4 * Math.pow(EeV, 1.5) / 1.6e5 / (1 + EeV / 4e5));
    const inel = EkeV > 250 ? 0.8 * (1 - Math.exp(-(EkeV - 250) / 300)) : 0;
    const Gn = (Ts + Tp + inel) * D0 / (2 * Math.PI), shareG = Gg / (Gg + Gn);
    const key = Math.round(S.target.lgE * 20);
    if (CAP.key !== key) { CAP.key = key; CAP.g = Math.round(40 * shareG); CAP.n = 40 - CAP.g; CAP.balls.length = 0; }
    const phone = W < 600;
    const cx = W * 0.42, cy = H * 0.56, R = Math.min(W, H) * 0.1;
    g.glow(cx, cy, R * 2.3, c.warm, 0.25);
    g.nucleus(cx, cy, R, { N: 56, Z: 24, t: S.time, heat: 1.3, jiggle: 0.5 });
    const dh = Math.min(84, H * 0.12), open = (G) => G / (G + 0.4);
    const dG = g.door(cx, cy - R * 2.1, dh, open(Gg), c.photon, null);
    const dN = g.door(cx + R * 2.6 + dh * 0.31, cy + dh / 2, dh, open(Gn), c.neutron, null);
    const tot = Math.max(1, CAP.g + CAP.n);
    g.label(`photon door: ${Gg} eV, barely changes`, cx, cy - R * 2.1 - dh - 40, { color: c.photon, size: phone ? 12 : 13, weight: 600, bg: true });
    g.label(`captured (n,γ): ${CAP.g} (${Math.round(100 * CAP.g / tot)} %)`, cx, cy - R * 2.1 - dh - 18, { color: c.ink, size: phone ? 12 : 13, weight: 600, bg: true });
    const nx = dN.x, ny = cy + dh / 2 + 22;
    g.label(phone ? `neutron: ${Gn < 1 ? Gn.toFixed(2) : Gn.toFixed(0)} eV` : `neutron door: ${Gn < 1 ? Gn.toFixed(2) : Gn < 100 ? Gn.toFixed(1) : Gn.toFixed(0)} eV, wider when faster`, Math.min(nx, W - 120), ny, { color: c.neutron, size: phone ? 12 : 13, weight: 600, bg: true });
    g.label(`back out: ${CAP.n} (${Math.round(100 * CAP.n / tot)} %)`, Math.min(nx, W - 120), ny + 20, { color: c.ink, size: phone ? 12 : 13, weight: 600, bg: true });
    if (inel > 0) g.label("more doors open (target left excited)", Math.min(nx, W - 130), ny + 40, { color: c.faint, size: 11, bg: true });
    // the stream: a neutron arrives, the nucleus holds it a moment, then one door wins
    const sp = 0.7 + 0.5 * clamp((lg + 2) / 5.3, 0, 1);
    CAP.acc += dt * 2.6;
    while (CAP.acc > 1) { CAP.acc -= 1; if (CAP.balls.length < 12) CAP.balls.push({ t: 0, g: Math.random() < shareG, j: Math.random() - 0.5 }); }
    for (let k = CAP.balls.length - 1; k >= 0; k--) {
      const b = CAP.balls[k]; b.t += dt;
      const tin = 1.1 / sp, dwell = 0.35, tout = 0.8;
      if (b.t < tin) { const u = b.t / tin; g.ball(lerp(-10, cx - R * 0.9, u), cy + b.j * R * 0.6, 5.5, c.neutron); continue; }
      if (b.t < tin + dwell) { g.glow(cx + b.j * R * 0.5, cy, 18, c.warm, 0.6); continue; }
      const u = (b.t - tin - dwell) / tout;
      if (u >= 1) { if (b.g) CAP.g++; else CAP.n++; CAP.balls.splice(k, 1); continue; }
      if (b.g) { const gx = dG.mx + b.j * Math.max(0, dG.gap - 4); const [x, y] = follow([[cx, cy - R], [gx, dG.my], [gx, dG.my - dh * 1.3]], [0.5, 0.5], u); streak(g, x, y, -Math.PI / 2, 22, 0.8, 1 - smooth(0.8, 1, u)); }
      else { const gy = dN.my + b.j * dh * 0.4, gx = dN.mx + b.j * Math.max(0, dN.gap - 4); const [x, y] = follow([[cx + R, cy], [gx, gy], [W + 20, gy]], [0.45, 0.55], u); g.ball(x, y, 5.5, c.neutron); }
    }
    g.label(fmtE(EkeV) + " neutrons →", W * 0.03, cy - R - 16, { color: c.neutron, size: 13, align: "left", bg: true });
    g.label(shareG > 0.5 ? "slow neutrons: the photon door wins" : shareG > 0.03 ? `the neutron door wins; capture takes about ${Math.round(100 * shareG)} %` : "fast: capture is a rare event", W * 0.5, H - 22, { color: c.ink, size: phone ? 13 : 15, weight: 600, serif: true, bg: true });
  }
})();
