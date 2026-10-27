/* Chapter 25 (Expert): photon strength, transmission, <Gamma_gamma> and the cascade (gamma/strength.py, gamma/transmission.py).
 * Scenes (S.mode): "e1"     = f_E1(E_gamma): the standard Lorentzian (SLO) against SMLO at a final-state temperature T;
 *                              a small proton/neutron dipole oscillation for the giant resonance;
 *                   "m1"     = f_M1: spin-flip Lorentzian, scissors (strength ~ beta^2), low-energy upbend; E1 faint behind;
 *                   "ba"     = Brink-Axel: the same f from every start energy; primary spectra E^3 f(E) rho(Ex - E) as humps;
 *                   "gg"     = <Gamma_gamma> at S_n: the integrand by multipolarity, the computed width against the measured one;
 *                   "casc"   = Monte Carlo cascades from S_n down a level density: a ladder with the falling state, the summed
 *                              spectrum and the multiplicity.
 * Formulas: SLO f = K s0 G0^2 E / ((E^2 - E0^2)^2 + E^2 G0^2); SMLO (Plujko et al. 2018) f = K s0 G0 E G(E,T) / ((E^2 - E0^2)^2
 * + E^2 G(E,T)^2) / (1 - e^(-E/T)), G(E,T) = (G0/E0)(E + 4 pi^2 T^2/E0), K = 8.674e-8 mb^-1 MeV^-2; GDR from RIPL systematics;
 * M1 spin-flip at 41 A^(-1/3) MeV, normalised to f_M1(7 MeV) = 1.6e-9 MeV^-3 (about 0.15 x the RIPL-2 systematics 1.58e-9 A^0.47,
 * so that M1 is a realistic ~15 % of <Gamma_gamma>); scissors 1.0e-9 at 3 MeV for beta = 0.25; upbend 3.6e-9 e^(-0.9 E);
 * T_XL = 2 pi E^(2L+1) f_XL.
 * The engine's default E1 is the tabulated SMLO-2019 strength (strength 9) and the IAEA-CRP M1 with upbend (strengthM1 3);
 * the closed forms here stand in for those tables. Illustrative compound nucleus: A = 57 (iron-57-like), S_n = 7.65 MeV,
 * level density as in Chapter 24 with a~ scaled by 0.918 (D0 ~ 28 keV); measured <Gamma_gamma> = 0.92 eV (RIPL, 57Fe). */
(function () {
  const { TAU, clamp, lerp, smooth, rng } = WT.util;
  const log10 = (x) => Math.log(x) / Math.LN10;
  const A = 57, Z = 26, N = 31, K = 8.674e-8, SN = 7.646, GGMEAS = 0.92;
  const E0 = 31.2 * Math.pow(A, -1 / 3) + 20.6 * Math.pow(A, -1 / 6), G0 = 0.026 * Math.pow(E0, 1.91), S0 = 1.2 * 120 * N * Z / (A * Math.PI * G0);
  const EM = 41 * Math.pow(A, -1 / 3), GM = 4;
  const slo = (E, e0, g0, s0) => K * s0 * g0 * g0 * E / ((E * E - e0 * e0) ** 2 + E * E * g0 * g0);
  const SM1 = 1.6e-9 / slo(7, EM, GM, 1);                                          // spin-flip strength from f_M1(7 MeV) (illustrative)
  function fE1(E, T, model) {
    if (model === 0) return slo(E, E0, G0, S0);
    const G = (G0 / E0) * (E + 4 * Math.PI * Math.PI * T * T / E0), th = T > 1e-3 ? 1 / (1 - Math.exp(-E / T)) : 1;
    return K * S0 * G0 * E * G / ((E * E - E0 * E0) ** 2 + E * E * G * G) * th;
  }
  const fSF = (E) => slo(E, EM, GM, SM1);
  const fSC = (E, beta) => (beta > 0 ? slo(E, 3.0, 1.5, 1) * 1.0e-9 / slo(3, 3.0, 1.5, 1) * (beta / 0.25) ** 2 : 0);
  const fUP = (E, on) => (on ? 3.6e-9 * Math.exp(-0.9 * E) : 0);
  // level density of the compound nucleus (Chapter 24 formulas; a~ scaled so that D0 ~ 25 keV)
  const AT = (0.0692559 * A + 0.282769 * Math.pow(A, 2 / 3)) * 0.918, DEL = 12 / Math.sqrt(A), SIG2C = (U) => Math.hypot(2, 0.01389 * Math.pow(A, 5 / 3) / AT * Math.sqrt(AT * Math.max(U, 0.01)));   // smooth floor near 2 at low energy
  const lnFG = (E) => { const U = Math.max(E - DEL, 0.05); return 2 * Math.sqrt(AT * U) - Math.log(12 * Math.SQRT2 * Math.sqrt(SIG2C(U)) * Math.pow(AT, 0.25) * Math.pow(U, 1.25)); };
  const EXM = 5.0, TCT = (() => { const h = 0.01; return 1 / ((lnFG(EXM + h) - lnFG(EXM - h)) / (2 * h)); })(), E0CT = EXM - TCT * (Math.log(TCT) + lnFG(EXM));
  const rho = (E) => (E >= EXM ? Math.exp(lnFG(E)) : Math.exp((E - E0CT) / TCT) / TCT);
  const fJ = (J, E) => { const s2 = SIG2C(Math.max(E - DEL, 0.1)); return (2 * J + 1) / (2 * s2) * Math.exp(-((J + 0.5) ** 2) / (2 * s2)); };
  const temp = (Ef) => Math.sqrt(Math.max(Ef - DEL, 0.01) / AT);
  /** <Gamma_gamma> (eV) of the s-wave resonances (J = 1/2+) at S_n, and the integrand per multipolarity */
  function gammaWidth(o) {
    const scale = o.scale ?? 1, beta = o.beta ?? 0, up = o.up ?? 1, n = 300, dE = SN / n; let sE1 = 0, sM1 = 0; const curve = [];
    for (let i = 0; i < n; i++) {
      const Eg = (i + 0.5) * dE, Ef = SN - Eg, r = rho(Ef), wE1 = fJ(0.5, Ef) + fJ(1.5, Ef), wM1 = wE1;   // dipole: J' = 1/2, 3/2; parity halves
      const tE1 = TAU * Eg ** 3 * fE1(Eg, temp(Ef), 1) * scale, tM1 = TAU * Eg ** 3 * (fSF(Eg) + fSC(Eg, beta) + fUP(Eg, up)) * scale;
      const a = tE1 * 0.5 * r * wE1 * dE, b = tM1 * 0.5 * r * wM1 * dE; sE1 += a; sM1 += b; curve.push([Eg, a / dE, b / dE]);
    }
    const rJ = 0.5 * rho(SN) * fJ(0.5, SN), D0 = 1 / rJ;                                   // MeV
    return { gg: (sE1 + sM1) * D0 / TAU * 1e6, e1: sE1 * D0 / TAU * 1e6, m1: sM1 * D0 / TAU * 1e6, D0: D0 * 1e3, curve };
  }
  const SHOT = /[?&]shot=/.test(location.search);
  const sup = (n) => String(n).replace(/[-0-9]/g, (ch) => "⁻⁰¹²³⁴⁵⁶⁷⁸⁹"["-0123456789".indexOf(ch)]);

  Object.assign(WT.glossary || (WT.glossary = {}), {
    smlo: {
      term: "SMLO", aliases: ["SMLO"],
      short: "The simplified modified Lorentzian: an E1 strength function whose width grows with photon energy and with the temperature of the final states.",
      more: "Proposed by V. Plujko and co-workers, and tabulated for every nucleus in the IAEA photon strength function database (2019). The engine's default E1, like TALYS-2's, is that SMLO-2019 table.",
      chapter: "strength",
    },
    brinkAxel: {
      term: "Brink–Axel hypothesis", aliases: ["Brink–Axel hypothesis", "Brink–Axel"],
      short: "The assumption that the photon strength function depends only on the photon energy, not on the excitation energy of the state that emits it.",
      more: "It lets one strength, measured or calculated for the ground state, serve the whole cascade. It is tested by extracting strengths at different excitation energies; it holds approximately, with deviations debated for particular nuclei and energies.",
      chapter: "strength",
    },
  });

  WT.chapter("strength", {
    num: "Chapter 25", title: "Photon strength, in detail", short: "Photon strength",
    lead: "Chapter 10 showed which photons a hot nucleus prefers. This chapter writes the strength functions down, follows them into transmission coefficients and the average radiative width, and runs the cascade they drive.",
    html: `
<div class="step">
  <h3>E1: the tail of the giant dipole resonance</h3>
  <p>The <b>photon strength function</b> <i>f<sub>XL</sub></i>(<i>E</i><sub>γ</sub>) is the average reduced probability for a photon of type <i>XL</i>: electric dipole E1, magnetic dipole M1 and so on. For E1 it is dominated by the giant dipole resonance near 18 MeV, but decay at <i>S<sub>n</sub></i> uses photons of 1 to 7 MeV, far down its tail, and the tail's shape is the whole question.</p>
  <div class="formula">f<sub>E1</sub> = K σ₀Γ₀ · E<sub>γ</sub> Γ(E<sub>γ</sub>,T) / [(E<sub>γ</sub>² − E₀²)² + E<sub>γ</sub>² Γ(E<sub>γ</sub>,T)²] / (1 − e<sup>−E<sub>γ</sub>/T</sup>) ,  Γ(E<sub>γ</sub>,T) = (Γ₀/E₀)(E<sub>γ</sub> + 4π²T²/E₀)</div>
  <div class="ctl"><label for="ps-t">Final-state temperature T (MeV)</label><input id="ps-t" type="range" data-bind="T" min="0" max="1.5" step="0.01" value="0.7"><output data-show="T" data-fmt="2"></output></div>
  <p>The dashed line is the standard Lorentzian (SLO), the shape fitted to photoabsorption. With its constant width it overestimates the strength in the decay window by a factor of 2 to 5, a long-known failure for spherical nuclei. The solid line is the simplified modified Lorentzian (<b>SMLO</b>): its width grows with photon energy and with the temperature of the final states, which lowers the tail in the window but leaves a finite strength at zero photon energy, as decay data require. Drag <i>T</i> to 0 and that low-energy floor falls away.</p>
</div>
<div class="step">
  <h3>M1: spin-flip, scissors, upbend</h3>
  <p>M1 strength is weaker but not negligible: a spin-flip resonance near 41<i>A</i><sup>−1/3</sup> MeV, a scissors mode near 3 MeV in deformed nuclei (strength growing as β²), and an upbend, a rise toward zero photon energy seen in Oslo-method data and in shell-model calculations.</p>
  <div class="ctl"><label for="ps-b">Deformation β (scissors)</label><input id="ps-b" type="range" data-bind="beta" min="0" max="0.35" step="0.01" value="0.2"><output data-show="beta" data-fmt="2"></output></div>
  <div class="btns"><button class="btn ghost" data-act="up" aria-pressed="true">Upbend</button></div>
  <p>The faint line behind is E1. At the lowest photon energies, below about 2 MeV here, the upbend lets M1 rival or exceed it (the marker shows where), which is why it matters for the soft end of the cascade and for capture far from stability. The engine's default M1 is the IAEA recommendation with the upbend, tabulated per nucleus, and its default E1 is the tabulated SMLO-2019; the closed forms here stand in for those tables.</p>
</div>
<div class="step">
  <h3>Brink–Axel</h3>
  <p>The <b>Brink–Axel hypothesis</b> says that the strength depends on the photon energy and not on where the nucleus starts: the same <i>f</i> holds for a resonance at <i>S<sub>n</sub></i> and for a state at 4 MeV. (SMLO keeps a weak dependence through <i>T</i>.) Each starting energy then emits with the transmission coefficient times the density of final states.</p>
  <div class="formula">T<sub>XL</sub>(E<sub>γ</sub>) = 2π E<sub>γ</sub><sup>2L+1</sup> f<sub>XL</sub>(E<sub>γ</sub>) ,  dΓ/dE<sub>γ</sub> ∝ T<sub>XL</sub>(E<sub>γ</sub>) ρ(E<sub>x</sub> − E<sub>γ</sub>)</div>
  <div class="ctl"><label for="ps-x">Start energy Eₓ (MeV)</label><input id="ps-x" type="range" data-bind="Ex" min="2" max="7.6" step="0.05" value="7.6"><output data-show="Ex" data-fmt="2"></output></div>
  <p>The product of a rising <i>E</i><sub>γ</sub>³<i>f</i> and a falling ρ makes a hump. From <i>S<sub>n</sub></i> it peaks near 4 to 5 MeV here. From lower starts it is cut off at the start energy; below the matching energy, where ρ is a constant-temperature exponential, the shape is the same from every start, only truncated. Test the hypothesis by comparing strengths extracted at different excitation energies, which is what Oslo-type analyses do.</p>
</div>
<div class="step">
  <h3>The average radiative width</h3>
  <p>Summing over every final state reachable by E1 or M1 from the s-wave resonances (<i>J</i><sup>π</sup> = ½⁺ on a spin-0 target) gives their average total photon width. It is measured, from resonance shapes, for a few hundred nuclei, and it is the main check on the strength at <i>S<sub>n</sub></i>.</p>
  <div class="formula">⟨Γ<sub>γ</sub>⟩ = D₀/2π · Σ<sub>XL</sub> Σ<sub>J′π′</sub> ∫₀^{S<sub>n</sub>} T<sub>XL</sub>(E<sub>γ</sub>) ρ(S<sub>n</sub> − E<sub>γ</sub>, J′, π′) dE<sub>γ</sub></div>
  <div class="ctl"><label for="ps-s">Scale on the strength</label><input id="ps-s" type="range" data-bind="scale" min="0.3" max="5" step="0.01" value="1"><output data-show="scale" data-fmt="2"></output></div>
  <p>The curves show where the width comes from, photon by photon: mostly 3 to 7 MeV, and mostly E1, with M1 adding about 15 %. Here, with closed forms and a schematic level density standing in for the engine's tables, the width comes out at about a sixth of the measured 0.92 eV: it is that sensitive to the level density below <i>S<sub>n</sub></i> and to the tail of the strength. TALYS's defaults, which the engine follows, give about 1.3 eV for this nucleus. The slider applies the single overall factor an evaluation would fit. Capture in the keV range is nearly proportional to ⟨Γ<sub>γ</sub>⟩ when Γ<sub>γ</sub> ≪ Γ<sub>n</sub>, so a factor here is a factor in (n,γ). TALYS can rescale the strength to a measured ⟨Γ<sub>γ</sub>⟩ (<code>gnorm</code>); in INCOGNITA that rescaling, applied to every nucleus of the cascade, is an optional switch, off by default.</p>
</div>
<div class="step">
  <h3>The cascade</h3>
  <p>Below the first photon the same rule repeats: from each new energy the next photon is drawn from <i>T</i>(<i>E</i><sub>γ</sub>) ρ(<i>E<sub>x</sub></i> − <i>E</i><sub>γ</sub>), until the nucleus reaches its known levels. Each history is a few photons; their summed spectrum is what a calorimeter sees after capture.</p>
  <div class="btns"><button class="btn ghost" data-act="up2" aria-pressed="true">Upbend</button><button class="btn ghost" data-act="clear">Start again</button></div>
  <p>The upbend adds soft photons and a little to the multiplicity. The engine does not draw histories: it moves populations bin by bin, top down (Chapter 11), which gives the same averages without sampling noise.</p>
  <div class="aside">In the code: <code>gamma/strength.py</code> (every strength model TALYS supports; default SMLO-2019 tables and the IAEA M1 with upbend), <code>gamma/parameters.py</code> (giant-resonance systematics, tables), <code>gamma/transmission.py</code> (T = 2π E<sup>2L+1</sup> f), <code>gamma/ggnorm.py</code> (optional ⟨Γγ⟩ normalisation), <code>emission/</code> (the cascade). The picture uses closed forms and systematics for an iron-57-like nucleus; the measured ⟨Γγ⟩ is the RIPL value for ⁵⁷Fe.</div>
</div>`,
    setup(S) {
      S.set("mode", "e1"); S.to("T", 0.7, true); S.to("beta", 0.2, true); S.to("up", 1, true); S.to("Ex", 7.6, true); S.to("scale", 1, true);
      S.sweep = 0; S.casc = null; S.hist = new Float64Array(40); S.nC = 0; S.mult = 0;
      const press = (on) => document.querySelectorAll('#strength [data-act="up"], #strength [data-act="up2"]').forEach((b) => b.setAttribute("aria-pressed", String(on)));
      const tog = () => { const on = S.target.up < 0.5; S.to("up", on ? 1 : 0); press(on); S.hist.fill(0); S.nC = 0; S.mult = 0; };
      S.on("up", tog); S.on("up2", tog);
      S.on("clear", () => { S.hist.fill(0); S.nC = 0; S.mult = 0; });
    },
    steps: [
      (S) => { S.set("mode", "e1"); },
      (S) => { S.set("mode", "m1"); },
      (S) => { S.set("mode", "ba"); },
      (S) => { S.set("mode", "gg"); },
      (S) => { S.set("mode", "casc"); if (SHOT) for (let i = 0; i < 1500; i++) cascadeOnce(S); },
    ],
    frame(g, S, dt) {
      if (S.mode === "e1") drawE1(g, S, dt);
      else if (S.mode === "m1") drawM1(g, S, dt);
      else if (S.mode === "ba") drawBA(g, S, dt);
      else if (S.mode === "gg") drawGG(g, S, dt);
      else drawCasc(g, S, dt);
    },
  });
  WT.mods.strength.calc = { fE1, fSF, fSC, fUP, gammaWidth, rho, E0, G0, S0, TCT, E0CT };

  // log-strength frame: E from 0 to Emax, f from 10^d0 to 10^d1 MeV^-3
  function fFrame(g, phone, yT, yB, Emax, d0, d1) {
    const { W, c } = g, x0 = W * (phone ? 0.14 : 0.11), x1 = W * 0.95, X = (e) => lerp(x0, x1, e / Emax), Y = (f) => lerp(yB, yT, (log10(Math.max(f, 1e-30)) - d0) / (d1 - d0));
    for (let d = d0; d <= d1; d++) { const y = lerp(yB, yT, (d - d0) / (d1 - d0)); g.line(x0, y, x1, y, c.line, 1, 0.8); g.label(`10${sup(d)}`, x0 - 6, y, { color: c.faint, size: 10, align: "right" }); }
    for (let e = 0; e <= Emax; e += Emax > 12 ? 5 : 1) g.label(`${e}`, X(e), yB + 12, { color: c.faint, size: 10 });
    g.label("Eγ (MeV)", x1, yB + 26, { color: c.faint, size: 10, align: "right" });
    return { X, Y, x0, x1, yT, yB, Emax };
  }
  const path = (F, f, e0, e1, n = 200) => { const p = []; for (let i = 0; i <= n; i++) { const e = lerp(e0, e1, i / n); p.push([F.X(e), F.Y(f(e))]); } return p; };

  // ---------- scene 1: E1 ----------
  function drawE1(g, S, dt) {
    const { W, H, c } = g, phone = W < 600, T = S.T;
    const F = fFrame(g, phone, H * 0.1, H * (phone ? 0.8 : 0.82), 25, -10, -6);
    g.label("E1 strength f (MeV⁻³), A = 57", F.x0, F.yT - 14, { color: c.ink, size: 12, weight: 600, align: "left" });
    const ps = path(F, (e) => fE1(e, T, 1), 0.05, 25), pl = path(F, (e) => fE1(e, 0, 0), 0.05, 25);
    g.clip(F.x0, F.yT - 4, F.x1 - F.x0, F.yB - F.yT + 4);
    g.ground(ps, c.photon, H * 0.16, 0.2); g.poly(pl, c.soft, 1.8, 0.9, [6, 5]); g.poly(ps, c.photon, 2.8);
    g.restore();
    // the window that matters for decay at S_n
    g.ctx.save(); g.ctx.fillStyle = g.rgba(c.warm, 0.07); g.ctx.fillRect(F.X(1), F.yT, F.X(7.6) - F.X(1), F.yB - F.yT); g.ctx.restore();
    g.label("photons that decay uses", F.X(4.3), F.yT + 12, { color: c.warm, size: 11, bg: true });
    g.label(`GDR: E₀ = ${E0.toFixed(1)} MeV, Γ₀ = ${G0.toFixed(1)} MeV, σ₀ = ${S0.toFixed(0)} mb`, F.X(17), F.Y(fE1(E0, T, 1)) - 18, { color: c.photon, size: phone ? 10 : 12, weight: 600, bg: true });
    g.label("dashed: SLO", F.X(2.2), F.Y(fE1(2.2, 0, 0)) + 16, { color: c.soft, size: 11, bg: true });
    // a probe sweeping the decay window
    S.sweep = (((S.sweep + dt / 6) % 1) + 1) % 1; const e = 1 + 6.6 * (0.5 - 0.5 * Math.cos(TAU * S.sweep)), fs = fE1(e, T, 1), fl = fE1(e, 0, 0);
    g.line(F.X(e), F.Y(fl), F.X(e), F.Y(fs), c.warm, 1.4, 0.8, [2, 3]); g.glow(F.X(e), F.Y(fs), 12, c.photon, 0.6); g.dot(F.X(e), F.Y(fs), 4.5, c.photon);
    g.label(`at ${e.toFixed(1)} MeV: SMLO / SLO = ${(fs / fl).toFixed(2)}`, W / 2, H * (phone ? 0.93 : 0.93), { color: c.ink, size: phone ? 12 : 14, weight: 600, serif: true, bg: true });
    // the dipole: proton and neutron clouds sloshing against each other
    if (!phone) {
      const cx = W * 0.84, cy = H * 0.66, R = Math.min(W, H) * 0.045, s = Math.sin(S.time * 5) * R * 0.28;
      g.ctx.save(); g.ctx.globalAlpha = 0.5; g.dot(cx - s, cy, R, c.proton, 0.45); g.dot(cx + s, cy, R, c.neutron, 0.45); g.ctx.restore();
      g.label("protons against neutrons", cx, cy + R + 16, { color: c.soft, size: 11 });
    }
  }

  // ---------- scene 2: M1 ----------
  function drawM1(g, S, dt) {
    const { W, H, c } = g, phone = W < 600, beta = S.beta, up = S.up, T = 0.7;
    const F = fFrame(g, phone, H * 0.1, H * (phone ? 0.8 : 0.82), 12, -10, -6);
    g.label("M1 strength f (MeV⁻³), A = 57", F.x0, F.yT - 14, { color: c.ink, size: 12, weight: 600, align: "left" });
    g.clip(F.x0, F.yT - 4, F.x1 - F.x0, F.yB - F.yT + 4);
    g.poly(path(F, (e) => fE1(e, T, 1), 0.05, 12), c.photon, 1.6, 0.35);
    const tot = (e) => fSF(e) + fSC(e, beta) + fUP(e, up);
    const pt = path(F, tot, 0.05, 12);
    g.ground(pt, c.alpha, H * 0.14, 0.2);
    g.poly(path(F, fSF, 0.05, 12), c.alpha, 1.4, 0.8, [5, 4]);
    if (beta > 0.005) g.poly(path(F, (e) => fSC(e, beta), 0.3, 8), c.cool, 1.4, 0.9, [3, 3]);
    if (up > 0.01) g.poly(path(F, (e) => fUP(e, up), 0.05, 8), c.warm, 1.4, 0.9 * up, [2, 3]);
    g.poly(pt, c.alpha, 2.8);
    g.restore();
    g.label("spin-flip", F.X(10.6), F.Y(fSF(10.6)) - 14, { color: c.alpha, size: 11, bg: true });
    if (beta > 0.05) g.label(`scissors, β = ${beta.toFixed(2)}`, F.X(3), F.Y(fSC(3, beta)) - 14, { color: c.cool, size: 11, bg: true });
    if (up > 0.5) g.label("upbend", F.X(0.6), F.Y(fUP(0.6, 1)) - 14, { color: c.warm, size: 11, align: "left", bg: true });
    g.label("faint: E1 at T = 0.7 MeV", F.X(9.5), F.Y(fE1(9.5, T, 1)) - 14, { color: c.photon, size: 11, bg: true, alpha: 0.8 });
    // where M1 overtakes E1
    let cross = null; for (let e = 0.1; e < 6; e += 0.02) if (tot(e) < fE1(e, T, 1)) { cross = e; break; }
    if (cross && cross > 0.15) { g.line(F.X(cross), F.yT, F.X(cross), F.yB, c.warm, 1, 0.5 + 0.2 * Math.sin(S.time * 3), [2, 4]); g.label(`M1 > E1 below ${cross.toFixed(1)} MeV`, F.X(cross) + 6, F.yB - 14, { color: c.warm, size: 12, weight: 600, align: "left", bg: true }); }
    else g.label("E1 dominates at every energy here", W / 2, F.yB - 14, { color: c.soft, size: 12, bg: true });
    // scissors: two ellipses rocking, amplitude ~ beta
    if (!phone && beta > 0.01) {
      const cx = W * 0.4, cy = H * 0.24, R = Math.min(W, H) * 0.05, a = Math.sin(S.time * 3) * beta * 0.9, ctx = g.ctx;
      [[c.proton, a], [c.neutron, -a]].forEach(([col, ang]) => { ctx.save(); ctx.translate(cx, cy); ctx.rotate(ang); ctx.globalAlpha = 0.4; ctx.fillStyle = col; ctx.beginPath(); ctx.ellipse(0, 0, R * (1 + beta), R * (1 - beta * 0.6), 0, 0, TAU); ctx.fill(); ctx.restore(); });
      g.label("scissors: the two deformed clouds rock", cx, cy + R + 18, { color: c.soft, size: 11 });
    }
  }

  // ---------- scene 3: Brink-Axel primary spectra ----------
  function drawBA(g, S, dt) {
    const { W, H, c } = g, phone = W < 600, Ex = clamp(S.Ex, 2, 7.646);
    const x0 = W * (phone ? 0.1 : 0.08), x1 = W * 0.95, yT = H * 0.12, yB = H * (phone ? 0.8 : 0.8), X = (e) => lerp(x0, x1, e / 8);
    // three reference starts, faint, and the chosen one bold; each normalised to its own maximum
    const spec = (ex) => { const p = []; let mx = 0; for (let i = 1; i <= 160; i++) { const e = ex * i / 160, v = TAU * e ** 3 * (fE1(e, temp(ex - e), 1) + fSF(e) + fUP(e, S.up)) * rho(ex - e); p.push([e, v]); mx = Math.max(mx, v); } return { p, mx }; };
    const Y = (v) => lerp(yB, yT, v);
    [4, 6, 7.646].forEach((ex) => { const s = spec(ex); g.poly(s.p.map(([e, v]) => [X(e), Y(0.85 * v / s.mx)]), c.faint, 1.3, 0.8, [4, 4]); g.label(`from ${ex.toFixed(1)} MeV`, X(ex), yB + 26, { color: c.faint, size: 10 }); });
    const s = spec(Ex), pts = s.p.map(([e, v]) => [X(e), Y(0.85 * v / s.mx)]);
    g.ground(pts, c.photon, H * 0.12, 0.25); g.poly(pts, c.photon, 2.8);
    g.line(x0, yB, x1, yB, c.soft, 1.2, 0.8); for (let e = 0; e <= 8; e++) g.label(`${e}`, X(e), yB + 12, { color: c.faint, size: 10 });
    g.label("Eγ (MeV)", x1, yB + 40, { color: c.faint, size: 10, align: "right" });
    let pk = 0, mx = 0; s.p.forEach(([e, v]) => { if (v > mx) { mx = v; pk = e; } });
    g.line(X(pk), yT, X(pk), yB, c.warm, 1, 0.5, [2, 4]);
    g.label(`peak at Eγ ≈ ${pk.toFixed(1)} MeV`, X(pk) + 6, yT + 8, { color: c.warm, size: 12, weight: 600, align: "left", bg: true });
    g.label("primary spectrum T(Eγ) ρ(Eₓ − Eγ), each scaled to its peak", x0, yT - 14, { color: c.ink, size: 12, weight: 600, align: "left" });
    // photons leaving the start level, energies drawn from this spectrum
    if (!S.bp) S.bp = []; if (Math.random() < dt * 6) { let u = Math.random() * s.p.reduce((a, q) => a + q[1], 0), e = s.p[0][0]; for (const q of s.p) { u -= q[1]; if (u <= 0) { e = q[0]; break; } } S.bp.push({ e, t0: S.time }); }
    for (let i = S.bp.length - 1; i >= 0; i--) { const q = S.bp[i], u = (S.time - q.t0) / 1.2; if (u > 1) { S.bp.splice(i, 1); continue; } g.photon(X(q.e), lerp(yB - 6, yT + 30, u), -Math.PI / 2, 18, 1 - u); }
  }

  // ---------- scene 4: <Gamma_gamma> ----------
  function drawGG(g, S, dt) {
    const { W, H, c } = g, phone = W < 600, key = `${S.scale.toFixed(3)}|${S.up > 0.5}`;
    if (!S.gw || S.gw.key !== key) S.gw = { key, r: gammaWidth({ scale: S.scale, beta: 0, up: S.up > 0.5 ? 1 : 0 }) };
    const r = S.gw.r, x0 = W * (phone ? 0.1 : 0.08), x1 = W * 0.95, yT = H * 0.12, yB = H * (phone ? 0.6 : 0.62), X = (e) => lerp(x0, x1, e / SN);
    let mx = 0; r.curve.forEach(([, a, b]) => (mx = Math.max(mx, a + b)));
    const Y = (v) => lerp(yB, yT, v / (mx * 1.1)), pe = r.curve.map(([e, a]) => [X(e), Y(a)]), pt = r.curve.map(([e, a, b]) => [X(e), Y(a + b)]);
    g.area([[X(0), yB]].concat(pt, [[X(SN), yB]]), c.alpha, 0.25); g.area([[X(0), yB]].concat(pe, [[X(SN), yB]]), c.photon, 0.4);
    g.poly(pt, c.alpha, 2); g.poly(pe, c.photon, 2.4);
    g.line(x0, yB, x1, yB, c.soft, 1.2, 0.8); for (let e = 0; e <= 7; e++) g.label(`${e}`, X(e), yB + 12, { color: c.faint, size: 10 });
    g.label("Eγ (MeV)", x1, yB + 26, { color: c.faint, size: 10, align: "right" });
    g.label("contribution to ⟨Γγ⟩ per MeV of photon energy: E1 (yellow), M1 (purple, on top)", x0, yT - 14, { color: c.ink, size: phone ? 10 : 12, weight: 600, align: "left" });
    // the gauge
    const gy = H * 0.8, gx0 = W * 0.1, gx1 = W * 0.9, GX = (v) => lerp(gx0, gx1, (log10(v) - log10(0.1)) / (log10(5) - log10(0.1)));
    g.line(gx0, gy, gx1, gy, c.soft, 2, 0.8); [0.1, 0.2, 0.5, 1, 2, 5].forEach((v) => { g.line(GX(v), gy - 5, GX(v), gy + 5, c.soft, 1.2); g.label(`${v} eV`, GX(v), gy + 18, { color: c.faint, size: 10 }); });
    g.ctx.save(); g.ctx.fillStyle = g.rgba(c.fission, 0.25); g.ctx.fillRect(GX(GGMEAS * 0.9), gy - 14, GX(GGMEAS * 1.1) - GX(GGMEAS * 0.9), 28); g.ctx.restore();
    g.label(`measured ${GGMEAS} eV`, GX(GGMEAS), gy - 24, { color: c.fission, size: 12, weight: 600, bg: true });
    const xg = GX(clamp(r.gg, 0.1, 5)); g.glow(xg, gy, 16 + 3 * Math.sin(S.time * 3), c.photon, 0.6); g.dot(xg, gy, 6.5, c.photon);
    g.label(`computed ⟨Γγ⟩ = ${(r.gg * 1000).toFixed(0)} meV (E1 ${(100 * r.e1 / r.gg).toFixed(0)} %, M1 ${(100 * r.m1 / r.gg).toFixed(0)} %)`, W / 2, gy + (phone ? 40 : 44), { color: c.ink, size: phone ? 12 : 14, weight: 600, serif: true, bg: true });
  }

  // ---------- scene 5: Monte Carlo cascades ----------
  const EDISC = 1.2;
  function sampleEg(ex, up) {
    const n = 60; let tot = 0; const w = new Float64Array(n);
    for (let i = 0; i < n; i++) { const e = ex * (i + 0.5) / n, ef = ex - e; w[i] = e ** 3 * (fE1(e, temp(ef), 1) + fSF(e) + fUP(e, up)) * (ef < EDISC ? 2 : rho(ef)); tot += w[i]; }
    let u = Math.random() * tot; for (let i = 0; i < n; i++) { u -= w[i]; if (u <= 0) return ex * (i + Math.random()) / n; } return ex;
  }
  function cascadeOnce(S) {
    let ex = SN; const steps = []; let guard = 0;
    while (ex > EDISC && guard++ < 20) { const e = sampleEg(ex, S.up > 0.5 ? 1 : 0); steps.push(e); ex -= e; }
    if (ex > 0.02) steps.push(ex);                                 // the last step: into the ground state
    for (const e of steps) { const b = Math.min(39, Math.floor(e / SN * 40)); S.hist[b]++; }
    S.nC++; S.mult += steps.length; return steps;
  }
  function drawCasc(g, S, dt) {
    const { W, H, c } = g, phone = W < 600;
    // the ladder (left): continuum shading by log rho, discrete region at the bottom
    const lx = W * (phone ? 0.12 : 0.12), lw = W * (phone ? 0.1 : 0.08), yT = H * 0.1, yB = H * 0.88, Y = (e) => lerp(yB, yT, e / 8);
    for (let i = 0; i < 80; i++) { const e = 8 * i / 80; if (e < EDISC) continue; const d = clamp(log10(rho(e + 0.05)) / 5, 0, 1); g.ctx.fillStyle = g.rgba(c.ink, 0.05 + 0.4 * d); g.ctx.fillRect(lx - lw / 2, Y(e + 0.1), lw, Y(e) - Y(e + 0.1) + 0.5); }
    [0, 0.37, 0.71, 1.0].forEach((e) => g.line(lx - lw / 2, Y(e), lx + lw / 2, Y(e), c.ink, e ? 1.4 : 3, 0.9));
    g.line(lx - lw / 2 - 6, Y(SN), lx + lw / 2 + 6, Y(SN), c.neutron, 2, 0.9); g.label("Sₙ", lx + lw / 2 + 10, Y(SN), { color: c.neutron, size: 11, align: "left" });
    // play cascades: one shown slowly, many more counted in the background
    for (let k = 0; k < (S.nC < 4000 ? 6 : 0); k++) cascadeOnce(S);
    if (!S.casc || S.time - S.casc.t0 > S.casc.steps.length * 0.55 + 0.6) { const st = cascadeOnce(S); S.casc = { steps: st, t0: S.time }; }
    const cs = S.casc, tt = S.time - cs.t0, k = Math.min(cs.steps.length, Math.floor(tt / 0.55)); let ex = SN; for (let i = 0; i < k; i++) ex -= cs.steps[i];
    const f = k < cs.steps.length ? smooth(0.3, 0.55, tt - k * 0.55) : 0, exNow = ex - (k < cs.steps.length ? cs.steps[k] * f : 0);
    g.glow(lx, Y(exNow) - 6, 18, c.warm, 0.5); g.ball(lx, Y(exNow) - 6, 6, c.warm);
    if (k < cs.steps.length && f > 0 && f < 1) g.photon(lx + lw / 2 + 20 + f * 60, Y(ex) - 10 - f * 20, -0.3, 20, 1 - f * 0.6);
    // the summed spectrum (right)
    const hx0 = W * (phone ? 0.3 : 0.28), hx1 = W * 0.95, hy0 = H * 0.18, hy1 = H * 0.78, nb = 40, bw = (hx1 - hx0) / nb; let mx = 1; for (const v of S.hist) mx = Math.max(mx, v);
    for (let i = 0; i < nb; i++) { const h = (hy1 - hy0) * S.hist[i] / mx; g.ctx.fillStyle = g.rgba(c.photon, 0.8); g.ctx.fillRect(hx0 + i * bw + 0.5, hy1 - h, bw - 1, h); }
    g.line(hx0, hy1, hx1, hy1, c.soft, 1.2, 0.8); [0, 2, 4, 6].forEach((e) => g.label(`${e}`, lerp(hx0, hx1, e / SN), hy1 + 12, { color: c.faint, size: 10 }));
    g.label("Eγ (MeV)", hx1, hy1 + 26, { color: c.faint, size: 10, align: "right" });
    g.label("all photons from all cascades", hx0, hy0 - 14, { color: c.ink, size: 12, weight: 600, align: "left" });
    g.label(`${S.nC} cascades · mean multiplicity ${(S.mult / Math.max(1, S.nC)).toFixed(2)}`, (hx0 + hx1) / 2, H * 0.9, { color: c.ink, size: phone ? 12 : 14, weight: 600, serif: true, bg: true });
  }
})();
