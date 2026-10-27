/* Chapter 24 (Expert): level densities, matched (density/parameters.py, density/models.py, density/matching.py).
 * Scenes (S.mode): "fg"    = Ignatyuk's a(U) for several shell corrections, and the Fermi-gas ln rho(E) it gives;
 *                   "ct"    = ln rho against E: the Fermi gas, the constant-temperature line tangent at Ex (slider), its T and E0;
 *                   "root"  = the cumulative count N(E): counted levels as a staircase, the CT count for the trial Ex, and the
 *                             matching function F(Ex) whose zero the engine brackets and bisects (the bisection is animated);
 *                   "fail"  = a closed-shell (lead-like) case: F(Ex) has no zero, the empirical fallback, and the slope jump
 *                             at Exmatch when T stays at the empirical value (toggle: tangent T from the Fermi gas);
 *                   "d0"    = D0 = 1 / rho(Sn, J = 1/2, +) for an iron-57-like compound nucleus against the measured value.
 * Formulas as in the engine for ldmodel 1 (Gilbert-Cameron): a~ = alpha A + beta A^(2/3) with TALYS's global (alphald,
 * betald, gammashell1) = (0.0692559, 0.282769, 0.433090) (no collective enhancement), a(U) = a~ [1 + dW (1 - e^(-gamma U))/U],
 * Delta = chi 12/sqrt(A), sigma^2 = 0.01389 A^(5/3)/a~ sqrt(aU), Exmemp = 2.33 + 253/A + Delta, Tmemp = -0.25 + 10.2/sqrt(A(1 + gamma dW)).
 * Level schemes and shell corrections are illustrative (the lead-like case also has a~ x 1.3, so that it has neither a root nor
 * a temperature match below 3 Exmemp); D0 measured: RIPL value for 57Fe (TALYS structure/resonances/Fe.res). */
(function () {
  const { TAU, clamp, lerp, smooth } = WT.util;
  const log10 = (x) => Math.log(x) / Math.LN10;
  function nucleus(A, chi, dW, levels, Nlow, Ntop) {
    const at = 0.0692559 * A + 0.282769 * Math.pow(A, 2 / 3), gam = 0.43309 / Math.cbrt(A), D = chi * 12 / Math.sqrt(A);
    return { A, at, gam, D, dW, levels, Nlow, Ntop, Exmemp: 2.33 + 253 / A + D };
  }
  const MID = nucleus(56, 2, 1.0, [0, 0.85, 2.09, 2.66, 2.94, 3.12, 3.37, 3.45, 3.60, 3.76, 3.83, 3.86, 4.05, 4.12, 4.30, 4.40, 4.46, 4.51, 4.61, 4.68, 4.73, 4.80], 2, 20);
  const PB = nucleus(208, 2, -8.0, [0, 2.614, 3.198, 3.475, 3.708, 3.920, 3.946, 3.961, 4.037, 4.086, 4.106, 4.125, 4.180, 4.206, 4.230, 4.254, 4.262, 4.297, 4.324, 4.359, 4.383], 2, 20);
  PB.at *= 1.3;   // illustrative: a~ raised so the Fermi-gas T stays below the empirical T (0.85 MeV) up to ~24 MeV, beyond the root search (20.4 MeV) and 3 Exmemp (15.6 MeV)
  const aU = (n, U, dW) => { const d = dW ?? n.dW; if (U <= 1e-6) return n.at * (1 + d * n.gam); return Math.max(0.5, n.at * (1 + d * (1 - Math.exp(-n.gam * U)) / U)); };
  const sig2 = (n, U, a) => Math.max(1, 0.01389 * Math.pow(n.A, 5 / 3) / n.at * Math.sqrt(a * Math.max(U, 0.05)));
  function lnRhoF(n, E, dW, as) { const U = E - n.D; if (U <= 0.05) return NaN; const a = aU(n, U, dW) * (as || 1), s2 = sig2(n, U, a); return 2 * Math.sqrt(a * U) - Math.log(12 * Math.SQRT2 * Math.sqrt(s2) * Math.pow(a, 0.25) * Math.pow(U, 1.25)); }
  const TF = (n, E, dW) => { const h = 0.01; return 1 / Math.max(1e-3, (lnRhoF(n, E + h, dW) - lnRhoF(n, E - h, dW)) / (2 * h)); };
  const ctAt = (n, Ex, dW) => { const T = TF(n, Ex, dW); return { T, E0: Ex - T * (Math.log(T) + lnRhoF(n, Ex, dW)) }; };
  const ctCount = (ct, E) => Math.exp((E - ct.E0) / ct.T);
  const want = (n) => n.Ntop - n.Nlow;
  const Fmatch = (n, Ex, dW) => { const ct = ctAt(n, Ex, dW); return ctCount(ct, n.levels[n.Ntop]) - ctCount(ct, n.levels[n.Nlow]) - want(n); };
  const lowLim = (n, dW) => 2.25 / aU(n, 2, dW) + n.D + 0.11;
  /** the engine's search: scan [x1, x2] in 100 steps for a sign change (zbrak), then bisect (rtbis); null if none */
  function findRoot(n, dW, x2) {
    const x1 = lowLim(n, dW), dx = (x2 - x1) / 100; let a = x1, fa = Fmatch(n, a, dW);
    for (let i = 1; i <= 100; i++) { const b = x1 + i * dx, fb = Fmatch(n, b, dW); if (isFinite(fa) && isFinite(fb) && fa * fb < 0) return bisect(n, dW, a, b); a = b; fa = fb; }
    return null;
  }
  function bisect(n, dW, a, b) { const hist = [[a, b]]; let fa = Fmatch(n, a, dW); for (let i = 0; i < 40; i++) { const m = 0.5 * (a + b), fm = Fmatch(n, m, dW); if (fa * fm <= 0) b = m; else { a = m; fa = fm; } hist.push([a, b]); } return { x: 0.5 * (a + b), hist }; }
  // D0 for an iron-57-like compound nucleus (odd A: chi = 1), s-wave on a 0+ target: J = 1/2, positive parity only
  const C57 = nucleus(57, 1, 0, [], 0, 0), SN57 = 7.646, D0MEAS = 25.4, D0ERR = 2.2;
  function D0of(as, dW) {
    const U = SN57 - C57.D, a = aU(C57, U, dW) * as, s2 = sig2(C57, U, a), rho = Math.exp(lnRhoF(C57, SN57, dW, as));
    const rJ = 0.5 * rho * (2 * 0.5 + 1) / (2 * s2) * Math.exp(-((0.5 + 0.5) ** 2) / (2 * s2));
    return { D0: 1000 / rJ, rho, s2, a };   // keV
  }
  const fmtN = (v) => (v < 10 ? v.toFixed(1) : v < 1e4 ? v.toFixed(0) : v.toExponential(1).replace("e+", "e"));
  const SHOT = /[?&]shot=/.test(location.search);

  Object.assign(WT.glossary || (WT.glossary = {}), {
    gilbertCameron: {
      term: "Gilbert–Cameron", aliases: ["Gilbert–Cameron"],
      short: "A composite level density: a constant-temperature law at low energy joined to the Fermi gas above a matching energy, with equal value and slope at the joint.",
      more: "Proposed by A. Gilbert and A. G. W. Cameron in 1965. It is TALYS's and the engine's default (ldmodel 1), with Ignatyuk's energy-dependent level-density parameter.",
      chapter: "densities",
    },
    ignatyuk: {
      term: "Ignatyuk", aliases: ["Ignatyuk"],
      short: "Ignatyuk's form of the level-density parameter: the shell correction acts fully at low excitation and fades with energy, so a(U) tends to its smooth value.",
      formula: "a(U) = ã [1 + δW (1 − e^(−γU)) / U]",
      chapter: "densities",
    },
  });

  WT.chapter("densities", {
    num: "Chapter 24", title: "Level densities, matched", short: "Level densities",
    lead: "Chapter 8 joined a straight plank to a hillside. This chapter writes down both, shows how the joint is found from the counted levels, and what happens when no joint exists.",
    html: `
<div class="step">
  <h3>The Fermi gas with damped shell effects</h3>
  <p>The engine's default level density, ldmodel 1, is the <b>Gilbert–Cameron</b> composite: a Fermi gas at high energy, a constant temperature below. The Fermi gas needs one number, the level-density parameter <i>a</i>, and at low energy that number feels the shells. <b>Ignatyuk</b>'s form lets the shell correction δW act fully at low excitation and fade with a damping rate γ, so that <i>a</i>(<i>U</i>) tends to the smooth <i>ã</i> once the nucleus is hot.</p>
  <div class="formula">a(U) = ã [1 + δW (1 − e<sup>−γU</sup>) / U] ,  ã = αA + βA<sup>2/3</sup> ,  γ = γ₁ / A<sup>1/3</sup></div>
  <div class="ctl"><label for="ld-dw">Shell correction δW (MeV)</label><input id="ld-dw" type="range" data-bind="dW" min="-6" max="4" step="0.1" value="1"><output data-show="dW" data-fmt="1"></output></div>
  <div class="formula">ρ<sub>F</sub>(E) = exp(2√(aU)) / (12√2 σ a<sup>1/4</sup> U<sup>5/4</sup>) ,  U = E − Δ ,  σ² = 0.01389 A<sup>5/3</sup> √(aU) / ã</div>
  <p>The upper curves are <i>a</i>(<i>U</i>)/<i>ã</i> for several δW; yours is bold. Below it is ln ρ<sub>F</sub>. A negative δW (a closed shell) suppresses the density by one to two orders of magnitude, and the suppression fades only slowly: <i>a</i>(<i>U</i>) returns to <i>ã</i> as δW/<i>U</i>, so even at 20 MeV a δW of −6 MeV still costs a factor of about 40. Δ is the pairing shift, 12/√A per paired kind of nucleon.</p>
</div>
<div class="step">
  <h3>A tangent line below</h3>
  <p>Below the matching energy <i>E<sub>x</sub></i> the Fermi gas is replaced by the <b>constant-temperature</b> law. Two conditions fix its two parameters: equal value and equal slope at <i>E<sub>x</sub></i>, so the line is the tangent to ln ρ<sub>F</sub> there.</p>
  <div class="formula">ρ<sub>T</sub>(E) = (1/T) e<sup>(E − E₀)/T</sup> ,  1/T = d ln ρ<sub>F</sub>/dE |<sub>E<sub>x</sub></sub> ,  E₀ = E<sub>x</sub> − T ln[T ρ<sub>F</sub>(E<sub>x</sub>)]</div>
  <div class="ctl"><label for="ld-ex">Matching energy Eₓ (MeV)</label><input id="ld-ex" type="range" data-bind="Ex" min="4.6" max="14" step="0.05" value="7"><output data-show="Ex" data-fmt="2"></output></div>
  <p>Slide <i>E<sub>x</sub></i> and the tangent swings: a higher joint gives a higher <i>T</i> (a flatter line) and a lower <i>E</i>₀. Any <i>E<sub>x</sub></i> gives a smooth curve. The counted levels decide which one is right.</p>
</div>
<div class="step">
  <h3>Finding the joint from the counted levels</h3>
  <p>The staircase is the number of known levels below <i>E</i>, on a log scale. The constant-temperature law integrates to a straight line, <i>N</i>(<i>E</i>) = e<sup>(E − E₀)/T</sup> + const, and it must reproduce the count between level <i>N<sub>L</sub></i> and level <i>N<sub>P</sub></i>, the stretch of the scheme believed complete. That is one equation for the one unknown <i>E<sub>x</sub></i>.</p>
  <div class="formula">F(E<sub>x</sub>) = e<sup>(E<sub>P</sub>−E₀)/T</sup> − e<sup>(E<sub>L</sub>−E₀)/T</sup> − (N<sub>P</sub> − N<sub>L</sub>) = 0</div>
  <div class="ctl"><label for="ld-ex2">Trial Eₓ (MeV)</label><input id="ld-ex2" type="range" data-bind="Ex" min="4.6" max="14" step="0.05" value="7"><output data-show="Ex" data-fmt="2"></output></div>
  <p>The lower panel is <i>F</i>. The engine, as TALYS, scans an interval in 100 steps for a change of sign, then bisects it; the shrinking bracket shows the bisection. Where <i>F</i> = 0 the trial line lies on the staircase.</p>
</div>
<div class="step">
  <h3>When there is no joint</h3>
  <p>For a doubly closed shell the low-energy Fermi gas is so suppressed that its temperature stays low everywhere, and <i>F</i> never changes sign: there is no matching energy. TALYS then takes the empirical temperature <i>T</i> = −0.25 + 10.2/√(<i>A</i>(1 + γδW)) and looks for the energy where the Fermi gas has that temperature. Near a doubly closed shell the Fermi gas reaches that temperature only far above any sensible joint, or never, so the joint also falls back on systematics, <i>E<sub>x</sub></i> = 2.33 + 253/<i>A</i> + Δ, and <i>E</i>₀ is fixed so that the value is continuous.</p>
  <div class="btns"><button class="btn ghost" data-act="tang" aria-pressed="false">Tangent at the fallback energy</button></div>
  <p>The value is continuous, but the empirical <i>T</i> is not the Fermi-gas temperature at that energy, so the slope jumps. With the default input this happens for ²⁰⁵,²⁰⁶Tl, ²⁰⁶⁻²⁰⁹Pb and ²¹⁰Bi, with slope jumps of 34 to 62 %; taking <i>T</i> from the Fermi gas there, as TALYS already does when <i>E<sub>x</sub></i> is given in the input, restores the tangent and moves capture in the lead region by up to 20 to 30 %. INCOGNITA reproduces TALYS here; the change has been reported to the TALYS developers. The picture is a lead-like illustration, with <i>ã</i> raised by 30 % so that its Fermi gas stays below the empirical temperature up to about 24 MeV, beyond the search; its slope jumps by 62 %.</p>
</div>
<div class="step">
  <h3>The spacing D₀ as a check</h3>
  <p>At the neutron separation energy the density is measured directly: the mean spacing <i>D</i>₀ of s-wave resonances counts the states of the one spin and parity a slow neutron can reach. For a spin-0 target that is <i>J</i><sup>π</sup> = ½⁺ alone.</p>
  <div class="formula">1/D₀ = ρ(S<sub>n</sub>, ½, +) = ½ ρ<sub>F</sub>(S<sub>n</sub>) · (2J+1)/(2σ²) · e<sup>−(J+½)²/2σ²</sup></div>
  <div class="ctl"><label for="ld-as">Scale on ã</label><input id="ld-as" type="range" data-bind="as" min="0.8" max="1.2" step="0.005" value="1"><output data-show="as" data-fmt="3"></output></div>
  <p>The picture is for an iron-57-like compound nucleus with the global <i>ã</i>, against the measured 25.4 ± 2.2 keV. A few per cent on <i>ã</i> moves <i>D</i>₀ by tens of per cent, so where <i>D</i>₀ is measured the density at <i>S<sub>n</sub></i> is pinned well, and where it is not, it is the largest single uncertainty in capture. Evaluations adjust <i>a</i> to <i>D</i>₀, and so does TALYS's default, which the engine follows: for a nucleus with a measured <i>D</i>₀ it reads a level-density parameter fitted to it, and uses the global formula only for the others.</p>
  <div class="aside">In the code: <code>density/parameters.py</code> (ã, Ignatyuk damping, pairing, spin cutoff), <code>density/models.py</code> (Fermi gas, constant temperature, tables), <code>density/matching.py</code> (the matching root, the empirical fallback, TALYS's own single-precision details reproduced). The picture uses TALYS's global parameters for ldmodel 1 with illustrative level schemes and shell corrections (and, for the lead-like case, <i>ã</i> × 1.3); the measured <i>D</i>₀ is the RIPL value for ⁵⁷Fe.</div>
</div>`,
    setup(S) {
      S.set("mode", "fg"); S.to("dW", 1, true); S.to("Ex", 7, true); S.to("as", 1, true); S.to("tang", 0, true);
      S.Ex = 7; S.bis = 0; S.dot = 0;
      const press = (on) => document.querySelectorAll('#densities [data-act="tang"]').forEach((b) => b.setAttribute("aria-pressed", String(on)));
      S.on("tang", () => { const on = S.target.tang < 0.5; S.to("tang", on ? 1 : 0); press(on); });
    },
    steps: [
      (S) => { S.set("mode", "fg"); },
      (S) => { S.set("mode", "ct"); },
      (S) => { S.set("mode", "root"); S.bis = 0; if (SHOT) S.bis = 2.2; },
      (S) => { S.set("mode", "fail"); },
      (S) => { S.set("mode", "d0"); },
    ],
    frame(g, S, dt) {
      if (S.mode === "fg") drawFG(g, S, dt);
      else if (S.mode === "ct") drawCT(g, S, dt);
      else if (S.mode === "root") drawRoot(g, S, dt);
      else if (S.mode === "fail") drawFail(g, S, dt);
      else drawD0(g, S, dt);
    },
  });
  WT.mods.densities.calc = { MID, PB, Fmatch, findRoot, ctAt, lnRhoF, TF, D0of, aU, lowLim };

  // a log-density landscape: E on x, ln rho (decades) on y
  function frameLR(g, x0, x1, yT, yB, Emax, dmin, dmax) {
    const X = (e) => lerp(x0, x1, e / Emax), Y = (ln) => lerp(yB, yT, (ln / Math.LN10 - dmin) / (dmax - dmin));
    return { X, Y, x0, x1, yT, yB, Emax };
  }
  function decades(g, F, d0, d1, step, unit) {
    const { c } = g; for (let d = d0; d <= d1; d += step) { const y = F.Y(d * Math.LN10); g.line(F.x0, y, F.x1, y, c.line, 1, 0.8); g.label(d === 0 ? "1" : `10${sup(d)}`, F.x0 - 6, y, { color: c.faint, size: 10, align: "right" }); }
    for (let e = 0; e <= F.Emax; e += F.Emax > 16 ? 5 : 2) g.label(`${e}`, F.X(e), F.yB + 12, { color: c.faint, size: 10 });
    g.label(unit, F.x1, F.yB + 26, { color: c.faint, size: 10, align: "right" });
  }
  const sup = (n) => String(n).replace(/[-0-9]/g, (ch) => "⁻⁰¹²³⁴⁵⁶⁷⁸⁹"["-0123456789".indexOf(ch)]);
  function curve(n, E0, E1, f, N = 160) { const p = []; for (let i = 0; i <= N; i++) { const e = lerp(E0, E1, i / N), v = f(e); if (isFinite(v)) p.push([e, v]); } return p; }

  // ---------- scene 1: Ignatyuk a(U) and the Fermi gas ----------
  function drawFG(g, S, dt) {
    const { W, H, c } = g, phone = W < 600, n = MID, dW = S.dW;
    // top: a(U)/a~ for a fan of shell corrections
    const x0 = W * 0.1, x1 = W * 0.95, yT = H * 0.08, yB = H * (phone ? 0.36 : 0.38), Umax = 30;
    const X = (u) => lerp(x0, x1, u / Umax), Y = (r) => lerp(yB, yT, (r - 0.4) / 1.2);
    [0.5, 1, 1.5].forEach((r) => { g.line(x0, Y(r), x1, Y(r), r === 1 ? c.soft : c.line, 1, 0.9); g.label(r.toFixed(1), x0 - 6, Y(r), { color: c.faint, size: 10, align: "right" }); });
    for (let d = -6; d <= 4; d += 2) { const p = []; for (let i = 1; i <= 120; i++) { const u = Umax * i / 120; p.push([X(u), Y(aU(n, u, d) / n.at)]); } g.poly(p, c.faint, 1.2, 0.7); }
    const pm = []; for (let i = 1; i <= 160; i++) { const u = Umax * i / 160; pm.push([X(u), Y(aU(n, u, dW) / n.at)]); } g.poly(pm, c.accent, 3);
    g.label("a(U) / ã", x0, yT - 10, { color: c.ink, size: 12, weight: 600, align: "left" });
    [0, 10, 20, 30].forEach((u) => g.label(`${u}`, X(u), yB + 12, { color: c.faint, size: 10 }));
    g.label("U (MeV)", x1, yB + 26, { color: c.faint, size: 10, align: "right" });
    // moving probe on the bold curve
    S.dot = (((S.dot + dt / 7) % 1) + 1) % 1; const up = 0.5 + 29 * (0.5 - 0.5 * Math.cos(TAU * S.dot)), ap = aU(n, up, dW);
    g.glow(X(up), Y(ap / n.at), 14, c.accent, 0.5); g.dot(X(up), Y(ap / n.at), 4.5, c.accent);
    g.label(`U = ${up.toFixed(1)} MeV · a = ${ap.toFixed(2)} MeV⁻¹ · T ≈ √(U/a) = ${Math.sqrt(up / ap).toFixed(2)} MeV`, W / 2, yB + (phone ? 44 : 46), { color: c.accent, size: phone ? 11 : 13, weight: 600, bg: true });
    // bottom: ln rho_F against E, for the chosen dW and dW = 0 (dashed)
    const F = frameLR(g, x0, x1, H * (phone ? 0.56 : 0.58), H * (phone ? 0.9 : 0.9), 25, 0, 10);
    decades(g, F, 0, 10, 2, "E (MeV)");
    const p0 = curve(n, n.D + 0.3, 25, (e) => lnRhoF(n, e, 0)).map(([e, v]) => [F.X(e), F.Y(v)]), p1 = curve(n, n.D + 0.3, 25, (e) => lnRhoF(n, e, dW)).map(([e, v]) => [F.X(e), F.Y(v)]);
    g.ground(p1, c.accent, H * 0.1, 0.18); g.poly(p0, c.faint, 1.4, 0.9, [5, 4]); g.poly(p1, c.accent, 2.6);
    g.label("ρ_F (states per MeV), A = 56", F.x0, F.yT - 10, { color: c.ink, size: 12, weight: 600, align: "left" });
    if (!phone) g.label("dashed: δW = 0", F.X(15), F.Y(lnRhoF(n, 15, 0)) - 14, { color: c.soft, size: 11, bg: true });
    const r8 = Math.exp(lnRhoF(n, 8, dW)) / Math.exp(lnRhoF(n, 8, 0));
    g.label(`at 8 MeV: ×${r8 >= 0.1 ? r8.toFixed(2) : r8.toExponential(1)} against δW = 0`, F.x1, F.yB - 14, { color: c.accent, size: 12, align: "right", bg: true });
  }

  // ---------- scene 2: the tangent ----------
  function drawCT(g, S, dt) {
    const { W, H, c } = g, phone = W < 600, n = MID, dW = n.dW, Ex = clamp(S.Ex, 4.6, 14), ct = ctAt(n, Ex, dW);
    const F = frameLR(g, W * 0.1, W * 0.95, H * 0.1, H * (phone ? 0.78 : 0.8), 16, -1, 6);
    decades(g, F, -1, 6, 1, "E (MeV)");
    const pf = curve(n, n.D + 0.4, 16, (e) => lnRhoF(n, e, dW)).map(([e, v]) => [F.X(e), F.Y(v)]);
    g.ground(pf, c.soft, H * 0.12, 0.2); g.poly(pf, c.ink, 2.4, 0.85);
    // the CT line from 0 to Ex, and its ghost continuation
    const lnct = (e) => (e - ct.E0) / ct.T - Math.log(ct.T);
    const pl = [[F.X(0), F.Y(lnct(0))], [F.X(Ex), F.Y(lnct(Ex))]], pg = [[F.X(Ex), F.Y(lnct(Ex))], [F.X(16), F.Y(lnct(16))]];
    g.line(pl[0][0], pl[0][1], pl[1][0], pl[1][1], c.accent, 5); g.line(pg[0][0], pg[0][1], pg[1][0], pg[1][1], c.accent, 1.4, 0.5, [5, 5]);
    // slope triangle at the joint: over T MeV the line rises by e
    const jx = F.X(Ex), jy = F.Y(lnRhoF(n, Ex, dW)), tx = F.X(Ex - ct.T), ty = F.Y(lnct(Ex - ct.T));
    g.line(tx, ty, jx, ty, c.warm, 1.6, 0.9); g.line(jx, ty, jx, jy, c.warm, 1.6, 0.9);
    g.label(`T = ${ct.T.toFixed(2)} MeV`, (tx + jx) / 2, ty + 14, { color: c.warm, size: 12, weight: 600, bg: true });
    g.label("× e", jx + 6, (ty + jy) / 2, { color: c.warm, size: 11, align: "left", bg: true });
    g.glow(jx, jy, 16, c.accent, 0.5 + 0.15 * Math.sin(S.time * 3)); g.dot(jx, jy, 6, c.accent);
    g.label(`joint Eₓ = ${Ex.toFixed(2)} MeV`, jx + 10, jy - 16, { color: c.accent, size: 12, weight: 600, align: "left", bg: true });
    g.label(`E₀ = ${ct.E0.toFixed(2)} MeV`, F.X(0.2), F.Y(lnct(0)) - 14, { color: c.accent, size: 12, align: "left", bg: true });
    g.label("Fermi gas", F.X(14), F.Y(lnRhoF(n, 14, dW)) - 16, { color: c.ink, size: 12, bg: true });
    g.label("constant temperature", F.X(Math.max(0.6, Ex * 0.25)), F.Y(lnct(Math.max(0.6, Ex * 0.25))) + (phone ? 18 : 20), { color: c.accent, size: 12, align: "left", bg: true });
    g.label("ln ρ (states per MeV), A = 56", F.x0, F.yT - 12, { color: c.ink, size: 12, weight: 600, align: "left" });
  }

  // ---------- scene 3: the staircase, F(Ex) and the bisection ----------
  function rootOf(n, dW) { const k = `${n.A}|${dW.toFixed(2)}`; if (!rootOf.c || rootOf.c.k !== k) rootOf.c = { k, r: findRoot(n, dW, 19 + 300 / n.A) }; return rootOf.c.r; }
  function staircase(g, F, n, ct, col, phone) {
    const { c } = g, Ls = n.levels, pts = [];
    for (let i = 0; i < Ls.length; i++) { const y = F.Y(Math.log(i + 1)); pts.push([F.X(Ls[i]), i ? F.Y(Math.log(i)) : F.yB]); pts.push([F.X(Ls[i]), y]); }
    pts.push([F.X(Ls[Ls.length - 1] + 0.4), F.Y(Math.log(Ls.length))]);
    g.poly(pts, c.ink, 2, 0.9);
    // the window Nlow..Ntop
    const xa = F.X(Ls[n.Nlow]), xb = F.X(Ls[n.Ntop]); g.ctx.save(); g.ctx.fillStyle = g.rgba(c.fission, 0.08); g.ctx.fillRect(xa, F.yT, xb - xa, F.yB - F.yT); g.ctx.restore();
    g.label(phone ? `levels ${n.Nlow}–${n.Ntop}` : `levels ${n.Nlow} to ${n.Ntop}: taken as complete`, (xa + xb) / 2, F.yT + 10, { color: c.fission, size: 11, bg: true });
    // CT count, anchored at level Nlow: N(E) = N_L + e^((E-E0)/T) - e^((E_L-E0)/T)
    if (ct) { const EL = Ls[n.Nlow], base = n.Nlow + 1 - ctCount(ct, EL), pl = []; for (let i = 0; i <= 100; i++) { const e = lerp(EL - 0.6, Math.min(F.Emax, Ls[n.Ntop] + 1.5), i / 100), N = base + ctCount(ct, e); if (N > 0.5) pl.push([F.X(e), F.Y(Math.log(N))]); } g.poly(pl, col, 2.6); }
  }
  function drawRoot(g, S, dt) {
    const { W, H, c } = g, phone = W < 600, n = MID, dW = n.dW, Ex = clamp(S.Ex, 4.6, 14), ct = ctAt(n, Ex, dW), fv = Fmatch(n, Ex, dW), ok = Math.abs(fv) < 0.6;
    const F = frameLR(g, W * 0.1, W * 0.95, H * 0.08, H * (phone ? 0.46 : 0.48), 6, 0, 2);
    decades(g, F, 0, 2, 1, "E (MeV)");
    staircase(g, F, n, ct, ok ? c.fission : c.accent, phone);
    g.label("number of levels below E", F.x0, F.yT - 10, { color: c.ink, size: 12, weight: 600, align: "left" });
    g.label(`trial Eₓ = ${Ex.toFixed(2)} MeV: the line gives ${(fv + want(n)).toFixed(1)} levels for ${want(n)} counted`, W / 2, F.yB + (phone ? 36 : 40), { color: ok ? c.fission : c.accent, size: phone ? 11 : 13, weight: 600, bg: true });
    // lower panel: F(Ex)
    const r = rootOf(n, dW), x1 = lowLim(n, dW), x2 = 14, gx0 = W * 0.1, gx1 = W * 0.95, gy0 = H * 0.62, gy1 = H * 0.92, X = (e) => lerp(gx0, gx1, (e - x1) / (x2 - x1));
    let fmin = 0, fmax = 0; const pts = []; for (let i = 0; i <= 120; i++) { const e = lerp(x1, x2, i / 120), f = Fmatch(n, e, dW); if (isFinite(f)) { pts.push([e, f]); fmin = Math.min(fmin, f); fmax = Math.max(fmax, f); } }
    const span = Math.max(Math.abs(fmin), Math.abs(fmax), 1), Y = (f) => lerp(gy1, gy0, 0.5 + 0.5 * clamp(Math.sign(f) * Math.log1p(Math.abs(f)) / Math.log1p(span), -1, 1));
    g.line(gx0, Y(0), gx1, Y(0), c.soft, 1.2, 0.8); g.label("F = 0", gx0 - 6, Y(0), { color: c.faint, size: 10, align: "right" });
    g.poly(pts.map(([e, f]) => [X(e), Y(f)]), c.accent, 2.4);
    [6, 8, 10, 12, 14].forEach((e) => g.label(`${e}`, X(e), gy1 + 12, { color: c.faint, size: 10 }));
    g.label("Eₓ (MeV)", gx1, gy1 + 26, { color: c.faint, size: 10, align: "right" });
    g.label("F(Eₓ): predicted minus counted (signed log scale)", gx0, gy0 - 12, { color: c.ink, size: 12, weight: 600, align: "left" });
    g.dot(X(Ex), Y(fv), 5, ok ? c.fission : c.accent);
    if (r) {
      // the bisection: brackets shrinking, one per 0.25 s, then a pause
      S.bis = (((S.bis + dt) % 7) + 7) % 7; const k = Math.min(r.hist.length - 1, Math.floor(S.bis / 0.25)), [a, b] = r.hist[k];
      g.ctx.save(); g.ctx.fillStyle = g.rgba(c.warm, 0.18); g.ctx.fillRect(X(a), gy0, Math.max(2, X(b) - X(a)), gy1 - gy0); g.ctx.restore();
      g.line(X(a), gy0, X(a), gy1, c.warm, 1.4, 0.8); g.line(X(b), gy0, X(b), gy1, c.warm, 1.4, 0.8);
      g.label(`bisection step ${k}: [${a.toFixed(3)}, ${b.toFixed(3)}]`, X(r.x), gy0 + 12, { color: c.warm, size: 11, weight: 600, bg: true });
      g.glow(X(r.x), Y(0), 12, c.fission, 0.6); g.dot(X(r.x), Y(0), 4, c.fission);
      if (!phone) g.label(`root Eₓ = ${r.x.toFixed(3)} MeV`, X(r.x) + 8, Y(0) + 16, { color: c.fission, size: 12, weight: 600, align: "left", bg: true });
    }
  }

  // ---------- scene 4: no root (lead-like) and the fallback ----------
  function drawFail(g, S, dt) {
    const { W, H, c } = g, phone = W < 600, n = PB, dW = n.dW, r = rootOf(n, dW);
    const Tm = -0.25 + 10.2 / Math.sqrt(n.A * (1 + n.gam * dW)), Exm = n.Exmemp, Tfg = TF(n, Exm, dW), Tuse = lerp(Tm, Tfg, S.tang);
    const lnF = (e) => lnRhoF(n, e, dW), E0 = Exm - Tuse * (Math.log(Tuse) + lnF(Exm)), lnct = (e) => (e - E0) / Tuse - Math.log(Tuse);
    const F = frameLR(g, W * 0.1, W * 0.95, H * 0.08, H * (phone ? 0.54 : 0.6), 10, -1, 5);
    decades(g, F, -1, 5, 1, "E (MeV)");
    const pf = curve(n, n.D + 0.4, 10, lnF).map(([e, v]) => [F.X(e), F.Y(v)]);
    g.clip(F.x0 - 2, F.yT - 6, F.x1 - F.x0 + 4, F.yB - F.yT + 12);
    g.poly(pf.filter((p) => p[0] >= F.X(Exm)), c.ink, 2.6, 0.9); g.poly(pf.filter((p) => p[0] <= F.X(Exm)), c.ink, 1.2, 0.45, [4, 4]);
    g.line(F.X(0.5), F.Y(lnct(0.5)), F.X(Exm), F.Y(lnct(Exm)), S.tang > 0.5 ? c.fission : c.proton, 4.5);
    // the joint, with a pulsing kink marker when the slopes differ
    const jx = F.X(Exm), jy = F.Y(lnF(Exm)), jump = Tuse / Tfg - 1;   // slope above / slope below - 1 (slopes are 1/T)
    g.glow(jx, jy, 18 + 4 * Math.sin(S.time * 4), Math.abs(jump) > 0.03 ? c.proton : c.fission, 0.55); g.dot(jx, jy, 6, Math.abs(jump) > 0.03 ? c.proton : c.fission);
    // the two slopes as short arrows at the joint
    const ang = (T) => Math.atan2(-(F.Y(lnF(Exm) + 1 / T) - jy), F.X(Exm + 1) - jx);
    const L = Math.min(W * 0.12, 90), a1 = ang(Tuse), a2 = ang(Tfg);
    g.arrow(jx - Math.cos(a1) * L, jy + Math.sin(a1) * L, jx, jy, S.tang > 0.5 ? c.fission : c.proton, 2, 0.9);
    g.arrow(jx, jy, jx + Math.cos(a2) * L, jy - Math.sin(a2) * L, c.ink, 2, 0.9);
    g.restore();
    g.label(`below: 1/T with T = ${Tuse.toFixed(2)} MeV (${S.tang > 0.5 ? "Fermi-gas T" : "empirical T"})`, F.X(0.4), F.Y(lnct(0.9)) - 18, { color: S.tang > 0.5 ? c.fission : c.proton, size: phone ? 10 : 12, weight: 600, align: "left", bg: true });
    g.label(`above: Fermi gas, T = ${Tfg.toFixed(2)} MeV`, jx + 12, jy + 18, { color: c.ink, size: phone ? 10 : 12, weight: 600, align: "left", bg: true });
    g.label(Math.abs(jump) > 0.005 ? `slope jumps by ${(100 * jump).toFixed(0)} % at Eₓ = ${Exm.toFixed(2)} MeV` : `tangent at Eₓ = ${Exm.toFixed(2)} MeV: no jump`, W / 2, F.yB + (phone ? 34 : 40), { color: Math.abs(jump) > 0.005 ? c.proton : c.fission, size: phone ? 12 : 14, weight: 600, serif: true, bg: true });
    g.label("ln ρ, lead-like nucleus (A = 208, δW = −8 MeV)", F.x0, F.yT - 10, { color: c.ink, size: 12, weight: 600, align: "left" });
    // small F(Ex) strip: no zero crossing
    const gx0 = W * 0.1, gx1 = W * 0.95, gy0 = H * (phone ? 0.8 : 0.76), gy1 = H * 0.95, x1 = lowLim(n, dW), x2 = 19 + 300 / n.A, X = (e) => lerp(gx0, gx1, (e - x1) / (x2 - x1));
    const pts = []; let mn = Infinity, mx = -Infinity; for (let i = 0; i <= 100; i++) { const e = lerp(x1, x2, i / 100), f = Fmatch(n, e, dW); if (isFinite(f)) { pts.push([e, f]); mn = Math.min(mn, f); mx = Math.max(mx, f); } }
    const span = Math.max(Math.abs(mn), Math.abs(mx), 1), Y = (f) => lerp(gy1, gy0, 0.5 + 0.5 * clamp(Math.sign(f) * Math.log1p(Math.abs(f)) / Math.log1p(span), -1, 1));
    g.line(gx0, Y(0), gx1, Y(0), c.soft, 1.2, 0.8); g.poly(pts.map(([e, f]) => [X(e), Y(f)]), c.proton, 2.2);
    g.label("F = 0", gx0 - 6, Y(0), { color: c.faint, size: 10, align: "right" });
    g.label(r ? "F changes sign: a root exists" : "F(Eₓ) never reaches zero: no matching energy", gx0, gy0 - 10, { color: c.proton, size: 12, weight: 600, align: "left" });
  }

  // ---------- scene 5: D0 ----------
  function drawD0(g, S, dt) {
    const { W, H, c } = g, phone = W < 600, as = clamp(S.as, 0.8, 1.2), d = D0of(as, 0);
    // a gauge: D0 on a log axis from 3 to 200 keV with the measured band
    const x0 = W * 0.08, x1 = W * 0.92, y = H * (phone ? 0.3 : 0.3), X = (v) => lerp(x0, x1, (log10(v) - log10(3)) / (log10(200) - log10(3)));
    g.line(x0, y, x1, y, c.soft, 2, 0.8);
    [3, 10, 30, 100, 200].forEach((v) => { g.line(X(v), y - 5, X(v), y + 5, c.soft, 1.2); g.label(`${v} keV`, X(v), y + 18, { color: c.faint, size: 10 }); });
    g.ctx.save(); g.ctx.fillStyle = g.rgba(c.fission, 0.25); g.ctx.fillRect(X(D0MEAS - D0ERR), y - 16, X(D0MEAS + D0ERR) - X(D0MEAS - D0ERR), 32); g.ctx.restore();
    g.label(`measured ${D0MEAS} ± ${D0ERR} keV`, X(D0MEAS), y - 26, { color: c.fission, size: 12, weight: 600, bg: true });
    const xd = X(clamp(d.D0, 3, 200)); g.glow(xd, y, 18, c.accent, 0.55); g.dot(xd, y, 7, c.accent);
    g.label(`computed D₀ = ${d.D0.toFixed(1)} keV`, xd, y + 38, { color: c.accent, size: phone ? 13 : 15, weight: 600, serif: true, bg: true });
    g.label(`ã × ${as.toFixed(3)} = ${(C57.at * as).toFixed(2)} MeV⁻¹ · σ² = ${d.s2.toFixed(1)} · ρ(Sₙ) = ${fmtN(d.rho)} per MeV`, W / 2, y + (phone ? 60 : 64), { color: c.soft, size: phone ? 10 : 12, bg: true });
    // below: a slice of the resonance ladder at Sn with that spacing, scrolling (Wigner spacings)
    const ly = H * 0.78, lh = H * 0.2, lx0 = W * 0.06, lx1 = W * 0.94, win = 400; // keV shown
    if (!S.lad) { const L = []; let e = 0, sd = 9; const rnd = () => ((sd = (sd * 16807) % 2147483647) / 2147483647); for (let i = 0; i < 400; i++) { e += Math.sqrt(-4 / Math.PI * Math.log(1 - rnd())); const z = Math.sqrt(-2 * Math.log(1 - rnd())) * Math.cos(TAU * rnd()); L.push({ u: e, h: z * z }); } S.lad = L; }
    const off = (S.time * 0.06) % 1, span = win / d.D0, XS = (u) => lerp(lx0, lx1, (u - off * 40) / span);
    g.line(lx0, ly, lx1, ly, c.soft, 1.2, 0.7);
    for (const q of S.lad) { const x = XS(q.u); if (x < lx0 || x > lx1) continue; const h = Math.min(1, 0.12 + 0.5 * q.h) * lh; const fade = smooth(lx0, lx0 + 30, x) * (1 - smooth(lx1 - 30, lx1, x)); g.line(x, ly, x, ly - h, c.neutron, 2, 0.85 * fade); }
    g.label(`s-wave resonances above Sₙ, ${win} keV shown: about ${(win / d.D0).toFixed(0)} levels`, W / 2, ly + 16, { color: c.soft, size: 12, bg: true });
    g.label("iron-57-like compound nucleus, Sₙ = 7.65 MeV, spin and parity ½⁺", x0, H * 0.08, { color: c.ink, size: 12, weight: 600, align: "left" });
  }
})();
