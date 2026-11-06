/* Build a reactor: a sandbox. The reader picks fuel, moderator, coolant, moderator-to-fuel ratio and core size; the model
 * gives k-infinity from the four-factor formula and k-effective with one-group leakage. SIMPLIFIED MODEL (labelled on the
 * drawing): a homogenised, cold, clean, fresh lattice of oxide fuel rods, all 2200 m/s thermal data, no control rods,
 * no fission products, no reflector. It aims to be right at textbook level, not to design a reactor.
 *
 * Thermal data, 2200 m/s, barns (Lamarsh & Baratta, Introduction to Nuclear Engineering, 3rd ed., table II.3; the U-235
 * values as in the "economy" lesson):
 *   U-235  sigma_a 681, sigma_f 585, nu 2.43 (eta 2.09)      U-238  sigma_a 2.68
 *   Pu-239 sigma_a 1011, sigma_f 742.5, nu 2.87 (eta 2.11)   Th-232 sigma_a 7.40
 *   U-233  sigma_a 578.8, sigma_f 531.1, nu 2.49 (eta 2.29)  (eta values as in the "breeding" lesson)
 *   MOX = Pu-239 in depleted uranium (0.25 % U-235); Pu-240 and the other plutonium isotopes are left out.
 * Fuel: oxide, 0.0232 heavy-metal atoms per barn-cm (UO2 at 10.4 g/cm3); rods of radius 0.5 cm.
 * Moderators (per molecule; epithermal slowing-down power xi Sigma_s from sigma_s and xi; diffusion coefficient D; Fermi age
 * tau to thermal; Lamarsh & Baratta tables 5.2, 5.3 and 6.x; Duderstadt & Hamilton ch. 5, 8):
 *   light water  N 0.0334, sigma_a 0.664 b, xi Sigma_s 1.35 /cm,  D 0.16 cm, tau 27 cm2   (L = 2.7 cm)
 *   heavy water  N 0.0332, sigma_a 0.0026 b (99.8 % D2O), xi Sigma_s 0.179 /cm, D 0.87 cm, tau 131 cm2  (L = 100 cm)
 *   graphite     N 0.0803 (1.6 g/cm3), sigma_a 0.0035 b, xi Sigma_s 0.060 /cm, D 0.84 cm, tau 368 cm2  (L = 55 cm)
 * Four factors for a heterogeneous lattice, homogenised (per unit fuel volume; m = moderator volume / fuel volume):
 *   eta = sum nu sigma_f / sum sigma_a over the fuel nuclides;
 *   f = Sigma_aF / (Sigma_aF + zeta (m Sigma_aM + c Sigma_aC) + Sigma_aS), thermal disadvantage factor zeta = 1.15,
 *       cladding and structure Sigma_aS = 0.004 /cm, coolant channel volume c = 1 per fuel volume when coolant and
 *       moderator differ (hot coolant: light water at 0.75 g/cm3, heavy water at 0.8 of its cold density);
 *   p = exp(-N_fert I_eff / (m xi Sigma_sM + c xi Sigma_sC)) (lattice resonance escape; Lamarsh & Baratta eq. 6.x), with the
 *       lumped-rod resonance integrals I = A + B sqrt(S/M): UO2 4.45 + 26.6 sqrt(S/M) -> 21 b; ThO2 3.4 + 24.5 sqrt(S/M)
 *       -> 19 b (approximate);
 *   eps = 1 + 0.06 x_U238 / (1 + 0.1 m) (0.02 for Th-232, whose fast fission is weaker): illustrative, 1.01 to 1.06.
 * Leakage, one group, bare cylinder with height = diameter: B^2 = (2.405/R)^2 + (pi/2R)^2 = 8.25/R^2;
 *   M^2 = L^2 + tau with L^2 = (1 - f) L_M^2 (L_M^2 = D/Sigma_a of the moderator) and tau = tau_M (1 + m + c)/m;
 *   k_eff = k_inf / (1 + M^2 B^2). Critical radius where k_eff = 1: R_c = sqrt(8.25 M^2 / (k_inf - 1)).
 * Fast cores (no moderator, coolant not water): one-group data for a sodium-cooled oxide-core spectrum, rounded and
 *   APPROXIMATE (after Waltar & Reynolds, Fast Breeder Reactors, 1981), chosen so the spectrum-averaged eta matches the
 *   "spectrum" and "breeding" lessons (Pu-239 2.37, U-235 1.96, U-233 2.30):
 *   U-235 sigma_f 1.81 b, sigma_c 0.45 b, nu 2.45;  U-238 0.04, 0.30, 2.8;  Pu-239 1.76, 0.42, 2.94;  U-233 2.75, 0.28, 2.53;
 *   Th-232 0.01, 0.33, 2.4. Volume fractions fuel 0.4, coolant 0.4, steel 0.2 (Fe 0.085 /b-cm, sigma_c 6 mb);
 *   coolant capture: Na 1.8 mb, Pb 4 mb, salt 5 mb, gas 0; D = 1.68 cm (Na), 1.5 (Pb), 1.35 (salt), 2.0 (gas); k_inf = eta f.
 * Thermal capture in coolants (2200 m/s): sodium 0.53 b (0.0222 /b-cm), lead 0.171 b (0.0305), FLiBe salt with
 *   99.995 % Li-7 ~0.23 b per formula unit (0.0118); CO2 and helium negligible.
 * Results (this model): natural U + light water peaks near k_inf 0.90 (m ~ 1.5), so it can never be critical; natural U +
 * heavy water reaches ~1.12 (m ~ 15, CANDU-like), natural U + graphite ~1.05 (m ~ 60-80; critical radius ~3.6 m, like the
 * first piles); 3 % U + light water ~1.4 to 1.5 (cold, clean, no boron); fast MOX needs roughly 10 % plutonium for
 * k_inf = 1 and more against leakage.
 * Feedback signs shown: fuel temperature (Doppler) always negative here (all fuels are mostly U-238 or Th-232). Coolant
 * void from the model (coolant density -10 %) for light-water and liquid-metal coolant in thermal cores (RBMK: positive;
 * an under-moderated water lattice: negative); textbook statements for the rest: gas ~0, heavy-water coolant small and
 * positive in CANDU, sodium fast cores positive when large (the spectrum hardens), lead smaller. */
(function () {
  const { TAU, clamp, lerp, smooth, rng } = WT.util;
  const NHM = 0.0232, ZETA = 1.15, SS = 0.004, CC = 1;
  const TH = { U5: { a: 681, f: 585, nu: 2.43 }, U8: { a: 2.68, f: 0, nu: 0 }, P9: { a: 1011, f: 742.5, nu: 2.87 }, U3: { a: 578.8, f: 531.1, nu: 2.49 }, T2: { a: 7.4, f: 0, nu: 0 } };
  const FA = { U5: { f: 1.81, c: 0.45, nu: 2.45 }, U8: { f: 0.04, c: 0.3, nu: 2.8 }, P9: { f: 1.76, c: 0.42, nu: 2.94 }, U3: { f: 2.75, c: 0.28, nu: 2.53 }, T2: { f: 0.01, c: 0.33, nu: 2.4 } };
  const RI = { U8: 21.0, T2: 18.9 }, EPS = { U8: 0.06, T2: 0.02 };
  const FUEL = {
    nat: { ab: "natural U", col: "#9a927c", mix: () => [["U5", 0.00711], ["U8", 0.99289]] },
    leu: { ab: "enriched U", col: "#b8925a", mix: (x) => [["U5", x], ["U8", 1 - x]] },
    mox: { ab: "MOX", col: "#d0675a", mix: (x) => [["P9", x], ["U5", (1 - x) * 0.0025], ["U8", (1 - x) * 0.9975]] },
    th: { ab: "thorium + U-233", col: "#5fbf8f", mix: (x) => [["U3", x], ["T2", 1 - x]] },
  };
  const MOD = {
    h2o: { ab: "light water", N: 0.0334, sa: 0.664, xs: 1.35, D: 0.16, tau: 27, m0: 2 },
    d2o: { ab: "heavy water", N: 0.0332, sa: 0.0026, xs: 0.179, D: 0.87, tau: 131, m0: 15 },
    c: { ab: "graphite", N: 0.0803, sa: 0.0035, xs: 0.06, D: 0.84, tau: 368, m0: 60 },
  };
  const COOL = {
    h2o: { ab: "water", mod: "h2o", rho: 0.75, col: "cool" },
    d2o: { ab: "heavy water", mod: "d2o", rho: 0.8, col: "#2bb3a3" },
    gas: { ab: "CO₂ / helium gas", N: 0, sa: 0, fc: 0, D: 2.0, col: "#b49be0", gas: 1 },
    na: { ab: "sodium", N: 0.0222, sa: 0.53, fc: 0.0018, D: 1.68, col: "#f0a92b" },
    pb: { ab: "lead", N: 0.0305, sa: 0.171, fc: 0.004, D: 1.5, col: "#8d98a8" },
    salt: { ab: "molten salt", N: 0.0118, sa: 0.23, fc: 0.005, D: 1.35, col: "#d6c58f" },
  };
  const B2C = 2.405 * 2.405 + Math.PI * Math.PI / 4; // B^2 R^2 for a bare cylinder with H = 2R

  /** The whole model. x = fissile share (0..1, ignored for natural U), m = moderator/fuel volume, R = core radius (m),
   *  vf = coolant density factor (1 = normal; < 1 for the void check). */
  function model(fuel, x, mod, cool, m, R, vf = 1) {
    const mix = FUEL[fuel].mix(x), C = COOL[cool];
    let mk = mod === "none" ? C.mod || null : mod;
    const merged = !!mk && C.mod === mk; // the coolant is the moderator (light water in a PWR)
    const B2 = B2C / (R * 100) ** 2, o = { fuel, mod, cool, mk, merged, fast: !mk, waterMod: mod === "none" && !!mk };
    if (mk) {
      const M = MOD[mk], mm = m * (merged ? vf : 1);
      let aT = 0, nf = 0, fis = 0, fert = 0, ri = 0, ep = 0;
      mix.forEach(([k, s]) => { const d = TH[k]; aT += s * d.a; nf += s * d.nu * d.f; fis += s * d.f; if (RI[k]) { fert += s; ri += s * RI[k]; ep += s * EPS[k]; } });
      let SC = 0, XC = 0, cc = 0;
      if (!merged) { cc = CC; if (C.mod) { const Cm = MOD[C.mod], N = Cm.N * C.rho * vf; SC = ZETA * cc * N * Cm.sa; XC = cc * N / Cm.N * Cm.xs; } else SC = ZETA * cc * C.N * vf * C.sa; }
      const SF = NHM * aT, SM = ZETA * mm * M.N * M.sa;
      const eta = nf / aT, f = SF / (SF + SM + SC + SS), p = Math.exp(-NHM * ri / (mm * M.xs + XC)), eps = 1 + ep / (1 + 0.1 * mm);
      const kinf = eta * f * p * eps, L2 = (1 - f) * M.D / (M.N * M.sa), tau = M.tau * (1 + mm + cc) / mm, M2 = L2 + tau;
      const PNL = 1 / (1 + M2 * B2), th = PNL * p, fa = th * f;
      Object.assign(o, { eta, f, p, eps, kinf, M2, L2, tau, PNL, keff: kinf * PNL, nu: nf / fis,
        bud: { fis: fa * fis / aT, cap: PNL * (1 - p) + fa * (1 - fis / aT), par: th * (1 - f), leak: 1 - PNL } });
    } else {
      let prod = 0, ab = 0, fv = 0;
      mix.forEach(([k, s]) => { const d = FA[k]; prod += s * d.nu * d.f; ab += s * (d.f + d.c); fv += s * d.f; });
      const SFa = 0.4 * NHM * ab, Sp = 0.2 * 0.085 * 0.006 + 0.4 * C.N * vf * C.fc, Sa = SFa + Sp;
      const eta = prod / ab, f = SFa / Sa, kinf = eta * f, L2 = C.D / Sa, PNL = 1 / (1 + L2 * B2);
      Object.assign(o, { eta, f, p: 1, eps: 1, kinf, M2: L2, L2, tau: 0, PNL, keff: kinf * PNL, nu: prod / fv,
        bud: { fis: PNL * 0.4 * NHM * fv / Sa, cap: PNL * 0.4 * NHM * (ab - fv) / Sa, par: PNL * Sp / Sa, leak: 1 - PNL } });
    }
    o.Rc = o.kinf > 1 ? Math.sqrt(B2C * o.M2 / (o.kinf - 1)) / 100 : Infinity;
    return o;
  }
  /** Coolant-void sign: -1 (k falls), +1 (rises), 0 (about none), or a textbook note. */
  function voidOf(o, x, m, R) {
    const C = COOL[o.cool];
    if (C.gas) return { s: 0 };
    if (o.cool === "d2o") return { s: 1, note: "small; positive in CANDU" };
    if (o.fast) return o.cool === "na" ? { s: 1, note: "big sodium cores: spectrum hardens" } : o.cool === "pb" ? { s: 1, note: "smaller than with sodium" } : null;
    if (o.cool === "salt") return null;
    const v = model(o.fuel, x, o.mod, o.cool, m, R, 0.9), dk = v.keff - o.keff;
    return { s: Math.abs(dk) < 3e-4 ? 0 : Math.sign(dk), dk };
  }
  WT.sandboxModel = { model, voidOf };
  if (typeof document === "undefined") return; // node test harness

  // ---------- state helpers: buttons and sliders ----------
  const $$ = (q) => document.querySelectorAll("#sandbox " + q);
  const SHOT = () => document.body.classList.contains("shot");
  function press(S) {
    $$("[data-act]").forEach((b) => { const [k, v] = b.dataset.act.split("_"); b.setAttribute("aria-pressed", String((k === "fu" && S.fuel === v) || (k === "mo" && S.mod === v) || (k === "co" && S.cool === v))); });
  }
  function slide(S, k, v, now) { S.to(k, v, now); $$(`[data-bind="${k}"]`).forEach((i) => (i.value = v)); }
  /** One recipe: fuel, fissile %, moderator, coolant, moderator/fuel ratio, radius (m). */
  function recipe(S, fu, enr, mo, co, m, R) {
    const now = SHOT();
    S.fuel = fu; S.mod = mo; S.cool = co; press(S);
    slide(S, "enr", enr, now); slide(S, "lm", Math.log10(m), now); slide(S, "R", R, now);
  }
  const mOf = (S) => 10 ** S.lm;

  // ---------- neutrons: born at fissions, they live out the fates the model gives them ----------
  const r = rng(23), parts = [], fx = [], sites = [];
  const sim = { init: false };
  function pick(b) { let u = r() * (b.fis + b.cap + b.par + b.leak); for (const k of ["fis", "cap", "par", "leak"]) { u -= b[k]; if (u <= 0) return k; } return "leak"; }
  function spawn(q, o, Rp, at) {
    let x, y;
    if (at) { x = at[0]; y = at[1]; }
    else if (sites.length && r() < 0.8) { const s = sites[Math.floor(r() * sites.length)]; x = s[0]; y = s[1]; }
    else { for (let i = 0; i < 20; i++) { const rr = Math.sqrt(r()) * Rp * 0.92, a = r() * TAU; x = Math.cos(a) * rr; y = Math.sin(a) * rr; if (r() < Math.cos(1.2 * rr / Rp)) break; } }
    const a = r() * TAU;
    q.x = x; q.y = y; q.a = a; q.t = 0; q.ph = "f"; q.turn = 0; q.fate = pick(o.bud); q.al = 1;
    q.Tf = 0.3 + 0.35 * r(); q.Tt = o.fast ? 0 : 0.7 + 1.1 * r();
    if (q.fate === "cap" && !o.fast) q.res = r() < (o.PNL * (1 - o.p)) / Math.max(1e-9, o.bud.cap); else q.res = false;
    q.leakFast = o.fast || r() < o.tau / Math.max(1, o.M2);
  }
  function step(o, Rp, Rmax, dt) {
    const vF = Rmax * 1.1, vT = Rmax * 0.16;
    parts.forEach((q) => {
      q.t += dt; q.turn -= dt;
      const d = Math.hypot(q.x, q.y);
      if (q.ph === "l") { q.x += Math.cos(q.a) * q.v * dt; q.y += Math.sin(q.a) * q.v * dt; if (d > Rp + 40) spawn(q, o, Rp); return; }
      // the end of a phase decides the fate
      if (q.ph === "f" && q.t >= q.Tf) {
        if (q.fate === "leak" && q.leakFast) return toLeak(q, vF);
        if (o.fast || q.res) return die(q, o, Rp);
        q.ph = "t"; q.t = 0;
      }
      if (q.ph === "t" && q.fate === "leak" && q.t > q.Tt * 0.4) return toLeak(q, vT * 3);
      if (q.ph === "t" && q.t >= q.Tt) return die(q, o, Rp);
      if (q.turn <= 0) { q.a += (r() - 0.5) * (q.ph === "f" ? 2.2 : 5); q.turn = q.ph === "f" ? 0.12 + 0.2 * r() : 0.04 + 0.08 * r(); }
      const v = q.ph === "f" ? vF : vT; q.x += Math.cos(q.a) * v * dt; q.y += Math.sin(q.a) * v * dt;
      const d2 = Math.hypot(q.x, q.y); if (d2 > Rp * 0.97) { q.a = Math.atan2(-q.y, -q.x) + (r() - 0.5); q.x *= (Rp * 0.97) / d2; q.y *= (Rp * 0.97) / d2; }
    });
    function toLeak(q, v) { q.ph = "l"; q.v = v; q.a = Math.atan2(q.y, q.x) + (r() - 0.5) * 0.8; }
    function die(q, o, Rp) {
      const k = q.fate === "fis" ? "fis" : q.fate === "cap" ? "cap" : "par";
      fx.push({ x: q.x, y: q.y, t: 0, k });
      if (k === "fis") { sites.push([q.x, q.y]); if (sites.length > 24) sites.shift(); spawn(q, o, Rp, [q.x, q.y]); }
      else spawn(q, o, Rp);
    }
    for (let i = fx.length - 1; i >= 0; i--) { fx[i].t += dt; if (fx[i].t > 0.7) fx.splice(i, 1); }
    // a core that shrank: forget birthplaces outside it
    for (let i = sites.length - 1; i >= 0; i--) if (Math.hypot(sites[i][0], sites[i][1]) > Rp) sites.splice(i, 1);
  }

  // ---------- drawing ----------
  const dark = (c) => /^#[0-3]/.test(c.paper);
  const fmtR = (v) => (v < 10 ? v.toFixed(v < 1 ? 2 : 1) : v.toFixed(0));
  function core(g, S, o, L, dt) {
    const { c, ctx } = g, { cx, cy, Rmax } = L, Rp = L.Rp, fu = FUEL[S.fuel], C = COOL[S.cool], snap = SHOT();
    const graphite = dark(c) ? "#7d848e" : "#5b6068", ccol = C.col[0] === "#" ? C.col : c[C.col];
    const mcol = o.mk === "h2o" ? c.cool : o.mk === "d2o" ? "#2bb3a3" : o.mk === "c" ? graphite : ccol;
    // lattice: rod pitch from the volume ratio (fuel area : cell area = 1 : 1 + m [+ coolant]), capped for drawing
    const mv = o.fast ? 1.5 : mOf(S) + (o.merged ? 0 : CC);
    let rr = clamp(Rmax * 0.024, 2.2, 5.5), pitch = 2 * rr * Math.sqrt((Math.PI / 4) * (1 + mv));
    const minP = Rp * Math.sqrt(Math.PI / 800); if (pitch < minP) { rr *= minP / pitch; pitch = minP; }
    ctx.save(); ctx.beginPath(); ctx.arc(cx, cy, Rp, 0, TAU); ctx.clip();
    ctx.fillStyle = g.rgba(mcol, o.mk === "c" ? 0.24 : 0.2); ctx.fillRect(cx - Rp, cy - Rp, 2 * Rp, 2 * Rp);
    const n = Math.ceil(Rp / pitch) + 1;
    if (o.mk === "c" && pitch > 9) { ctx.strokeStyle = g.rgba(graphite, 0.55); ctx.lineWidth = 1; ctx.beginPath(); for (let i = -n; i <= n; i++) { const u = (i + 0.5) * pitch; ctx.moveTo(cx + u, cy - Rp); ctx.lineTo(cx + u, cy + Rp); ctx.moveTo(cx - Rp, cy + u); ctx.lineTo(cx + Rp, cy + u); } ctx.stroke(); }
    // fuel glows with the fission rate (a cosine-like shape across the core)
    const glow = clamp(o.bud.fis * 1.6, 0.15, 1);
    for (let i = -n; i <= n; i++) for (let j = -n; j <= n; j++) {
      const x = i * pitch, y = j * pitch, d = Math.hypot(x, y); if (d > Rp - rr) continue;
      if (!o.merged && !o.fast && !C.gas) g.ring(cx + x, cy + y, rr + 2.2, ccol, 2.4, 0.75); // coolant channel
      else if (!o.merged && !o.fast) g.ring(cx + x, cy + y, rr + 2, ccol, 1.2, 0.6);
      g.dot(cx + x, cy + y, rr, fu.col, 0.8);
      const sh = Math.cos(1.3 * d / Rp); if (sh > 0.3 && pitch > 7) g.glow(cx + x, cy + y, rr * 2.4, c.warm, 0.18 * glow * sh);
    }
    ctx.restore();
    g.ring(cx, cy, Rp, c.soft, 2, 0.75);
    // neutrons
    if (!sim.init) { for (let i = 0; i < L.N; i++) { const q = {}; parts.push(q); spawn(q, o, Rp); } for (let k = 0; k < 90; k++) step(o, Rp, Rmax, 1 / 30); sim.init = true; }
    L.N = Math.round(L.N * clamp(0.2 + Rp / Rmax, 0.4, 1)); // fewer neutrons in a small core
    while (parts.length < L.N) { const q = {}; parts.push(q); spawn(q, o, Rp); } if (parts.length > L.N) parts.length = L.N;
    step(o, Rp, Rmax, clamp(dt || 0, 0, 0.05));
    fx.forEach((e) => { const u = e.t / 0.7, x = cx + e.x, y = cy + e.y;
      if (e.k === "fis") { g.glow(x, y, 8 + 22 * u, c.fission, 0.55 * (1 - u)); g.dot(x, y, 2.5, c.fission, 1 - u); }
      else g.ring(x, y, 3 + 7 * u, e.k === "cap" ? c.warm : c.cool, 1.6, 0.9 * (1 - u)); });
    parts.forEach((q) => { const x = cx + q.x, y = cy + q.y, d = Math.hypot(q.x, q.y), al = d > Rp ? clamp(1 - (d - Rp) / 40, 0, 1) : 1;
      if (q.ph === "t") g.dot(x, y, 2.3, c.neutron, 0.95 * al);
      else { g.glow(x, y, 7, c.photon, 0.35 * al); g.dot(x, y, 2, c.photon, al); } });
    // critical size and the radius
    const fs = L.fs;
    if (isFinite(o.Rc)) {
      const Rc = L.map(Math.min(o.Rc, 7.5)), out = o.Rc > 6.02;
      g.ring(cx, cy, Rc, c.fission, 1.8, 0.85, [6, 5]);
      const a = -0.8, lx = cx + Math.cos(a) * Rc, ly = cy + Math.sin(a) * Rc;
      g.label(out ? `critical at ${fmtR(o.Rc)} m` : "critical size", lx + 6, ly - 10, { color: c.fission, size: fs - 1, weight: 600, align: "left", bg: true });
    }
    const yR = cy + Math.max(Rp, isFinite(o.Rc) ? L.map(Math.min(o.Rc, 7.5)) : 0) + (L.phone ? 14 : 20);
    g.label(L.phone ? `R ${fmtR(S.R)} m` : `radius ${fmtR(S.R)} m${S.step === 3 ? " · drag the edge" : ""}`, cx, Math.min(yR, L.H - 26), { color: c.ink, size: fs, weight: 600, bg: true });
    if (!isFinite(o.Rc)) g.label(L.phone ? "never critical" : "no size is big enough", cx, Math.min(yR, L.H - 26) + (L.phone ? 16 : 20), { color: c.proton, size: fs - 1, weight: 600, bg: true });
  }

  function bar(g, x0, x1, y, v, col, h = 6) {
    const { c, ctx } = g, X = (u) => x0 + (x1 - x0) * clamp(u / 2.4, 0, 1);
    ctx.save(); ctx.fillStyle = g.rgba(c.soft, 0.14); ctx.fillRect(x0, y - h / 2, x1 - x0, h);
    ctx.fillStyle = g.rgba(col, 0.85); ctx.fillRect(x0, y - h / 2, X(v) - x0, h); ctx.restore();
    g.line(X(1), y - h / 2 - 3, X(1), y + h / 2 + 3, c.ink, 1.4, 0.7);
  }
  function panel(g, S, o, L) {
    const { c } = g, { x0, x1, y0, y1 } = L.P, ph = L.phone, fs = L.fs, w = x1 - x0, narrow = w < 300;
    const need = ph ? 300 : 470, u = clamp((y1 - y0) / need, 0.62, 1.2);
    let y = y0 + 8 * u;
    const lab = (s, x, yy, o2 = {}) => g.label(s, x, yy, Object.assign({ color: c.soft, size: fs - 1, align: "left" }, o2));
    // the recipe
    const fu = S.fuel === "nat" ? "natural uranium (0.7 % U-235)" : S.fuel === "leu" ? `uranium, ${S.enr.toFixed(1)} % U-235${S.enr > 20.05 ? " (highly enriched)" : ""}` : S.fuel === "mox" ? `MOX, ${S.enr.toFixed(1)} % plutonium-239` : `thorium, ${S.enr.toFixed(1)} % U-233`;
    const fuS = S.fuel === "nat" ? "natural U" : S.fuel === "leu" ? `${S.enr.toFixed(1)} % U-235` : S.fuel === "mox" ? `MOX ${S.enr.toFixed(1)} % Pu` : `Th + ${S.enr.toFixed(1)} % U-233`;
    lab(ph ? fuS : fu, x0, y, { color: c.ink, weight: 600, size: fs });
    const modT = o.fast ? (ph ? "no moderator: fast" : "no moderator: a fast reactor") : o.waterMod ? (ph ? `${COOL[S.cool].ab} moderates` : `no moderator, but the ${COOL[S.cool].ab} moderates`) : `${MOD[S.mod].ab} moderator`;
    y += (ph ? 15 : 20) * u;
    lab(ph ? modT : `${modT} · ${COOL[S.cool].ab} coolant`, x0, y);
    if (ph && !o.fast) { y += 14 * u; lab(`${COOL[S.cool].ab} coolant`, x0, y); }
    y += (ph ? 20 : 30) * u;
    // the four factors
    const F = [["η", o.fast ? "neutrons per absorption in fuel" : "neutrons per absorption in fuel", o.eta, 1],
      ["f", "share absorbed in fuel", o.f, 1],
      ["p", o.fast ? "no slowing down, no resonance loss" : "escape capture while slowing", o.p, !o.fast],
      ["ε", o.fast ? "fast fission counted in η" : "bonus from fast fission", o.eps, !o.fast]];
    const shortN = { η: "per fuel absorption", f: "absorbed in fuel", p: o.fast ? "—" : "escape capture", ε: o.fast ? "—" : "fast fission" };
    const xs = x0 + (ph ? 0 : 22);
    if (ph) {
      F.forEach(([s, , v, on], i) => { const xx = x0 + (i % 2) * w * 0.5, yy = y + Math.floor(i / 2) * 16 * u;
        g.label(s, xx, yy, { color: on ? c.ink : c.faint, size: fs + 1, serif: true, italic: true, align: "left" });
        g.label(on ? v.toFixed(3) : "1", xx + 14, yy, { color: on ? c.ink : c.faint, size: fs, align: "left" }); });
      y += 34 * u;
    } else {
      F.forEach(([s, nm, v, on]) => {
        g.label(s, x0 + 6, y + 1, { color: on ? c.ink : c.faint, size: fs + 4, serif: true, italic: true });
        lab(narrow ? shortN[s] : nm, xs, y, { color: on ? c.soft : c.faint });
        g.label(on ? v.toFixed(3) : "1", x1, y, { color: on ? c.ink : c.faint, size: fs, weight: 600, align: "right" });
        if (on) bar(g, xs, x1, y + 13 * u, v, c.accent, 5);
        y += 36 * u;
      });
    }
    // k-infinity, leakage, k-effective
    const kc = (k) => (k >= 1 ? c.fission : c.proton);
    g.label("k∞", x0 + (ph ? 0 : 6), y, { color: c.ink, size: fs + 2, serif: true, italic: true, weight: 700, align: ph ? "left" : "center" });
    lab(ph ? "" : narrow ? "no leakage" : o.fast ? "= η f, if nothing leaked" : "= η f p ε, if nothing leaked", xs + 10, y);
    g.label(o.kinf.toFixed(3), x1, y, { color: kc(o.kinf), size: fs + 1, weight: 700, align: "right" });
    if (!ph) bar(g, xs, x1, y + 13 * u, o.kinf, kc(o.kinf), 7);
    y += (ph ? 17 : 38) * u;
    lab(ph ? "stays in" : narrow ? `stays in (M² ${o.M2.toFixed(0)} cm²)` : `stays in: 1 / (1 + M²B²), M² = ${o.M2.toFixed(0)} cm²`, ph ? x0 : xs, y);
    g.label(`× ${o.PNL.toFixed(3)}`, x1, y, { color: c.ink, size: fs, weight: 600, align: "right" });
    y += (ph ? 22 : 34) * u;
    g.label("k", x0 + (ph ? 0 : 6), y, { color: c.ink, size: fs + 8, serif: true, italic: true, weight: 700, align: ph ? "left" : "center" });
    g.label(`= ${o.keff.toFixed(3)}`, x0 + (ph ? 14 : 22), y, { color: kc(o.keff), size: fs + 8, serif: true, weight: 700, align: "left" });
    if (!ph) bar(g, xs + w * 0.36, x1, y, o.keff, kc(o.keff), 9);
    y += (ph ? 20 : 30) * u;
    // the verdict
    const rho = (o.keff - 1) / o.keff * 100;
    let vt, vc;
    if (o.kinf < 1) { vt = ph ? "no chain, any size" : "can never sustain a chain, at any size"; vc = c.proton; }
    else if (o.keff < 1) { vt = ph ? `too small: needs ${fmtR(o.Rc)} m` : `too small: critical at radius ${fmtR(o.Rc)} m`; vc = c.warm; }
    else { vt = ph ? `sustains: +${rho.toFixed(1)} % spare` : `sustains a chain, ${rho.toFixed(1)} % to spare (ρ)`; vc = c.fission; }
    lab(vt, x0, y, { color: vc, size: fs, weight: 700 });
    y += (ph ? 22 : 34) * u;
    // where the neutrons go
    if (!ph) { lab("where the neutrons go", x0, y); y += 18 * u; }
    const B = o.bud, segs = [["fis", c.fission, "fission"], ["cap", c.warm, ph ? "fuel" : "caught by fuel"], ["par", c.cool, ph ? "mod./cool." : "moderator, coolant"], ["leak", c.faint, ph ? "leak" : "leak out"]];
    const bh = ph ? 12 : 18; let x = x0;
    segs.forEach(([k, col]) => { const ww = w * B[k]; if (ww > 0.5) { g.ctx.save(); g.ctx.fillStyle = g.rgba(col, 0.8); g.ctx.fillRect(x, y - bh / 2, Math.max(0, ww - 1.5), bh); g.ctx.restore();
      if (ww > (ph ? 30 : 38)) g.label(`${Math.round(B[k] * 100)} %`, x + ww / 2, y, { color: "#ffffff", size: ph ? 9 : fs - 2, weight: 700 }); } x += ww; });
    y += (ph ? 15 : 22) * u;
    segs.forEach(([k, col, nm], i) => { const xx = x0 + (i % 2) * w * 0.5, yy = y + Math.floor(i / 2) * (ph ? 14 : 18) * u;
      g.dot(xx + 5, yy, ph ? 3.5 : 4.5, col, 0.9); lab(nm, xx + 14, yy, { size: ph ? 9 : fs - 2 }); });
    y += (ph ? 30 : 40) * u;
    // feedback signs
    if (y < y1 - 4) {
      const vd = voidOf(o, S.enr / 100, mOf(S), S.R), arrow = (s) => (s < 0 ? "↓" : s > 0 ? "↑" : "≈");
      const sgnCol = (s) => (s < 0 ? c.fission : s > 0 ? c.proton : c.soft);
      if (ph) {
        lab("fuel hotter: k ↓", x0, y, { color: c.fission, size: 10, weight: 600 });
        if (vd && y + 14 * u < y1) lab(`${o.merged ? "water" : "coolant"} boils: k ${arrow(vd.s)}`, x0, y + 14 * u, { color: sgnCol(vd.s), size: 10, weight: 600 });
      } else {
        lab("fuel heats up: k ↓ (Doppler)", x0, y, { color: c.fission, weight: 600 });
        if (vd) { const what = o.merged ? (o.mk === "h2o" ? "water heats or boils" : "coolant heats") : C2(o.cool) ? "coolant boils away" : "coolant lost";
          lab(`${what}: k ${vd.s === 0 ? "barely changes" : arrow(vd.s)}${vd.note && !narrow ? ` (${vd.note})` : ""}`, x0, y + 20 * u, { color: sgnCol(vd.s), weight: 600 }); }
      }
    }
  }
  const C2 = (k) => k === "h2o" || k === "d2o";
  function layout(W, H) {
    const phone = W < 600, fs = phone ? 11 : 13;
    const Rmax = phone ? Math.min(W * 0.22, H * 0.36) : Math.min(W * 0.27, H * 0.38);
    const cx = phone ? W * 0.245 : Math.max(Rmax + 18, W * 0.29), cy = phone ? H * 0.46 : H * 0.47;
    const px0 = phone ? W * 0.51 : Math.max(cx + Rmax + 34, W * 0.58);
    const L = { phone, fs, W, H, Rmax, cx, cy, N: phone ? 36 : 70, P: { x0: px0, x1: W - (phone ? 6 : 14), y0: H * (phone ? 0.03 : 0.05), y1: H * 0.95 } };
    L.map = (R) => Rmax * Math.sqrt(R / 6);
    L.unmap = (p) => 6 * (p / Rmax) ** 2;
    return L;
  }

  WT.chapter("sandbox", {
    level: 2, num: "Lesson 1", title: "Build a reactor", short: "Build a reactor",
    lead: "Choose a fuel, a moderator, a coolant and a size, and see whether a chain reaction can keep itself going. A simplified textbook model.",
    html: `
<div class="step">
  <h3>Four factors</h3>
  <p>If no neutrons leaked, each one absorbed would lead to <i>k</i><sub>∞</sub> = <i>η f p ε</i> new ones; this graphite pile of natural uranium just makes it.</p>
</div>
<div class="step">
  <h3>Choose a moderator</h3>
  <p>With natural uranium, only heavy water or graphite lets <i>k</i><sub>∞</sub> pass 1: light water slows neutrons well but absorbs too many.</p>
  <div class="btns" role="group" aria-label="Moderator"><button class="btn ghost" data-act="mo_h2o">Light water</button> <button class="btn ghost" data-act="mo_d2o">Heavy water</button> <button class="btn ghost" data-act="mo_c">Graphite</button></div>
  <div class="ctl"><label for="sb-m1">Moderator per fuel</label><input id="sb-m1" type="range" data-bind="lm" min="-0.5" max="2.3" step="0.01" value="0.3"><output class="sb-m"></output></div>
</div>
<div class="step">
  <h3>Enrich the fuel</h3>
  <p>A few per cent of uranium-235 makes ordinary water work, which is why most reactors today use it.</p>
  <div class="btns" role="group" aria-label="Fuel"><button class="btn ghost" data-act="fu_nat">Natural U</button> <button class="btn ghost" data-act="fu_leu">Enriched U</button> <button class="btn ghost" data-act="fu_mox">MOX (Pu)</button> <button class="btn ghost" data-act="fu_th">Thorium + U-233</button></div>
  <div class="ctl"><label for="sb-e1">Fissile share (%)</label><input id="sb-e1" type="range" data-bind="enr" min="0.7" max="30" step="0.1" value="3"><output data-show="enr" data-fmt="1"></output></div>
</div>
<div class="step">
  <h3>Size and leakage</h3>
  <p>Neutrons escape through the surface, so <i>k</i> = <i>k</i><sub>∞</sub> / (1 + <i>M</i>²<i>B</i>²). Drag the edge of this natural-uranium graphite pile out to the dashed ring.</p>
  <div class="ctl"><label for="sb-r1">Core radius (m)</label><input id="sb-r1" type="range" data-bind="R" min="0.2" max="6" step="0.05" value="2"><output data-show="R" data-fmt="2"></output></div>
</div>
<div class="step">
  <h3>When the coolant boils</h3>
  <p>In a graphite core cooled by water, boiling raises <i>k</i>, because the water absorbed more than it slowed: the RBMK's flaw at Chernobyl. Try other coolants.</p>
  <div class="btns" role="group" aria-label="Coolant"><button class="btn ghost" data-act="co_h2o">Water</button> <button class="btn ghost" data-act="co_gas">CO₂ / helium</button> <button class="btn ghost" data-act="co_na">Sodium</button></div>
</div>
<div class="step">
  <h3>Build your own</h3>
  <p>Anything goes. A fast reactor has no moderator and needs far more fissile fuel.</p>
  <div class="btns" role="group" aria-label="Fuel"><button class="btn ghost" data-act="fu_nat">Natural U</button> <button class="btn ghost" data-act="fu_leu">Enriched U</button> <button class="btn ghost" data-act="fu_mox">MOX (Pu)</button> <button class="btn ghost" data-act="fu_th">Thorium + U-233</button></div>
  <div class="ctl"><label for="sb-e2">Fissile share (%)</label><input id="sb-e2" type="range" data-bind="enr" min="0.7" max="30" step="0.1" value="3"><output data-show="enr" data-fmt="1"></output></div>
  <div class="btns" role="group" aria-label="Moderator"><button class="btn ghost" data-act="mo_none">No moderator</button> <button class="btn ghost" data-act="mo_h2o">Light water</button> <button class="btn ghost" data-act="mo_d2o">Heavy water</button> <button class="btn ghost" data-act="mo_c">Graphite</button></div>
  <div class="ctl"><label for="sb-m2">Moderator per fuel</label><input id="sb-m2" type="range" data-bind="lm" min="-0.5" max="2.3" step="0.01" value="0.3"><output class="sb-m"></output></div>
  <div class="btns" role="group" aria-label="Coolant"><button class="btn ghost" data-act="co_h2o">Water</button> <button class="btn ghost" data-act="co_d2o">Heavy water</button> <button class="btn ghost" data-act="co_gas">CO₂ / helium</button> <button class="btn ghost" data-act="co_na">Sodium</button> <button class="btn ghost" data-act="co_pb">Lead</button> <button class="btn ghost" data-act="co_salt">Molten salt</button></div>
  <div class="ctl"><label for="sb-r2">Core radius (m)</label><input id="sb-r2" type="range" data-bind="R" min="0.2" max="6" step="0.05" value="2"><output data-show="R" data-fmt="2"></output></div>
</div>`,
    setup(S) {
      S.fuel = "nat"; S.mod = "c"; S.cool = "gas"; S.set("enr", 0.7); S.set("lm", Math.log10(60)); S.set("R", 6); S.pair = false;
      ["nat", "leu", "mox", "th"].forEach((k) => S.on("fu_" + k, () => {
        S.fuel = k; const e = k === "nat" ? 0.7 : k === "leu" ? (S.enr < 1 ? 3 : S.enr) : S.enr < 1 ? 5 : S.enr; slide(S, "enr", e); press(S); }));
      ["none", "h2o", "d2o", "c"].forEach((k) => S.on("mo_" + k, () => {
        S.mod = k; if (S.pair) S.cool = k === "h2o" ? "h2o" : k === "d2o" ? "d2o" : "gas";
        if (k !== "none") slide(S, "lm", Math.log10(MOD[k].m0)); else if (C2(S.cool)) slide(S, "lm", Math.log10(2)); press(S); }));
      ["h2o", "d2o", "gas", "na", "pb", "salt"].forEach((k) => S.on("co_" + k, () => { S.cool = k; if (S.mod === "none" && C2(k)) slide(S, "lm", Math.log10(2)); press(S); }));
      // moving the fissile-share slider with natural uranium chosen switches to enriched uranium
      $$('[data-bind="enr"]').forEach((i) => i.addEventListener("input", () => { if (S.fuel === "nat") { S.fuel = "leu"; press(S); } }));
      press(S);
    },
    steps: [
      (S) => { S.pair = false; recipe(S, "nat", 0.7, "c", "gas", 60, 6); },
      (S) => { S.pair = true; recipe(S, "nat", 0.7, "h2o", "h2o", 2, 6); },
      (S) => { S.pair = false; recipe(S, "leu", 3, "h2o", "h2o", 2, 6); },
      (S) => { S.pair = false; recipe(S, "nat", 0.7, "c", "gas", 60, 2); },
      (S) => { S.pair = false; recipe(S, "leu", 2, "c", "h2o", 60, 6); },
      (S) => { S.pair = false; if (SHOT()) recipe(S, "mox", 20, "none", "na", 1, 1); },
    ],
    frame(g, S, dt) {
      const { W, H, c, ctx } = g, L = layout(W, H);
      if (S.fuel === "nat" && Math.abs(S.enr - 0.7) > 0.05) S.set("enr", 0.7);
      const o = model(S.fuel, S.enr / 100, S.mod, S.cool, mOf(S), S.R);
      L.Rp = L.map(S.R);
      core(g, S, o, L, dt);
      panel(g, S, o, L);
      // moderator-per-fuel readout (the slider is logarithmic)
      const mt = o.fast ? "no moderator" : (mOf(S) < 10 ? mOf(S).toFixed(1) : mOf(S).toFixed(0)) + " ×";
      if (S._mt !== mt) { S._mt = mt; $$(".sb-m").forEach((e) => (e.textContent = mt)); }
      g.label(L.phone ? "simplified model" : "simplified one-group model · illustration", W - 6, H - 10, { color: c.faint, size: 10, align: "right" });
      // drag the core's edge to resize it
      const setR = (x, y) => { const R = clamp(Math.round(L.unmap(Math.hypot(x - L.cx, y - L.cy)) / 0.05) * 0.05, 0.2, 6); slide(S, "R", R, true); };
      WT.grab(ctx.canvas, {
        down(x, y) { const d = Math.hypot(x - L.cx, y - L.cy); if (Math.abs(d - L.Rp) < 16) { S.drag = true; setR(x, y); return true; } return false; },
        move(x, y) { if (S.drag) setR(x, y); }, up() { S.drag = false; }, cancel() { S.drag = false; },
        hover(x, y) { const d = Math.hypot(x - L.cx, y - L.cy); ctx.canvas.style.cursor = Math.abs(d - L.Rp) < 16 ? "ew-resize" : "default"; },
      });
    },
  });
})();
