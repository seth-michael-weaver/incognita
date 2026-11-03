/* Chapter 29 (part three, Intro): fusion, two light nuclei over one hill. Physics explanation (INCOGNITA does not
 * compute fusion; see FUSION_PLAN.md). Scenes (S.mode):
 *   "hill" = the d-t potential seen from above as a lit relief (WebGL fragment shader, CPU fallback): a Coulomb hill
 *            V = 1.44 MeV fm / r rising to ~0.36 MeV at contact (R = 4 fm) and the nuclear crater inside. The reader
 *            pulls the deuteron back and lets go (slingshot: the pull sets E, the aim sets the impact parameter b). The
 *            orbit is integrated in the Coulomb field (Rutherford), the turning point is r_c = 1.44 MeV fm / E, and at
 *            closest approach it fuses with P = P_WKB(E) exp(-(b/lambda-bar)^2), where P_WKB is the exact WKB
 *            transmission of a Coulomb barrier cut off at R: exp(-(2/pi) sqrt(E_G/E) [acos sqrt x - sqrt(x(1-x))]),
 *            x = R/r_c (-> exp(-sqrt(E_G/E)) far below the top); E_G = 2 mu c^2 (pi alpha)^2 = 1182 keV for d-t.
 *            The screen radius is logarithmic in r (rings are labelled), so 4 fm and 400 fm fit on one picture.
 *   "out"  = the products of four fuels, flying apart with momentum balanced (speed ~ sqrt(E/A)): D-T, D-D (two
 *            branches), D-3He, p-11B (three alphas); a hill bar ~ Z1 Z2 beside the energy released.
 *   "gas"  = a box of deuterons and tritons with Maxwellian speeds (2D) at temperature T; fusion flashes at a rate
 *            proportional to <sigma v>(T) (Bosch & Hale 1992 fit, valid 0.2-100 keV), normalised to 10 keV.
 * WT.fus (Bosch-Hale reactivities, constants) is shared with chapters 20-22. */
(function () {
  const { TAU, clamp, lerp, smooth, rng } = WT.util;
  // ---------- shared fusion physics ----------
  // Bosch & Hale, Nucl. Fusion 32 (1992) 611, Table VII: B_G (keV^1/2), m_r c^2 (keV), C1..C7; <sigma v> in cm^3/s, T in keV
  const BH = {
    DT: [34.3827, 1124656, 1.17302e-9, 1.51361e-2, 7.51886e-2, 4.60643e-3, 1.35e-2, -1.0675e-4, 1.366e-5],
    DDn: [31.397, 937814, 5.4336e-12, 5.85778e-3, 7.68222e-3, 0, -2.964e-6, 0, 0],
    DDp: [31.397, 937814, 5.65718e-12, 3.41267e-3, 1.99167e-3, 0, 1.0506e-5, 0, 0],
    DHe: [68.7508, 1124572, 5.51036e-10, 6.41918e-3, -2.02896e-3, -1.9108e-5, 1.35776e-4, 0, 0],
  };
  function bh(k, T) {
    const [BG, m, C1, C2, C3, C4, C5, C6, C7] = BH[k]; T = clamp(T, 0.2, 100);
    const th = T / (1 - (T * (C2 + T * (C4 + T * C6))) / (1 + T * (C3 + T * (C5 + T * C7))));
    const xi = Math.cbrt((BG * BG) / (4 * th));
    return C1 * th * Math.sqrt(xi / (m * T * T * T)) * Math.exp(-3 * xi) * 1e-6; // m^3/s
  }
  const sv = (fuel, T) => (fuel === "DD" ? bh("DDn", T) + bh("DDp", T) : bh(fuel, T));
  const EG = { DT: 34.3827 ** 2, DD: 31.397 ** 2, DHe: 68.7508 ** 2 }; // Gamow energies, keV
  WT.fus = { sv, EG, KEV: 1.602176634e-16, EALPHA: 3.5e3, CB: 5.35e-37, KC: 1440, MUDT: 1124.7 };

  // ---------- scene 1: the hill ----------
  const KC = 1440, RN = 4.0, RMAX = 400, R0 = 6, LMAP = Math.log(1 + RMAX / R0), EGDT = EG.DT;
  const rhoOf = (r, RP) => (RP * Math.log(1 + r / R0)) / LMAP;
  const lamBar = (E) => 197.327 / Math.sqrt(2 * WT.fus.MUDT * (E / 1000));
  function pTun(E) {
    const x = (RN * E) / KC; if (x >= 1) return 1;
    return Math.exp(-(2 / Math.PI) * Math.sqrt(EGDT / E) * (Math.acos(Math.sqrt(x)) - Math.sqrt(x * (1 - x))));
  }
  const pFuse = (E, b) => pTun(E) * Math.exp(-((b / lamBar(E)) ** 2));
  const oneIn = (p) => (p > 0.5 ? (100 * p).toFixed(0) + " %" : p > 1e-9 ? "1 in " + (1 / p < 1e4 ? Math.round(1 / p).toLocaleString("en-US") : (1 / p).toExponential(0).replace("e+", "·10^")) : "almost never");
  const HILL_GLSL = `
uniform vec2 u_c; uniform float u_rp, u_rc, u_t;
uniform vec3 u_paper, u_warm, u_hot, u_deep, u_ring;
const float R0 = ${R0.toFixed(1)}, RN = ${RN.toFixed(1)}, RMAX = ${RMAX.toFixed(1)}, LM = ${LMAP.toFixed(6)};
float rOf(float rho) { return R0 * (exp(rho / u_rp * LM) - 1.0); }
float hOf(float rho) { float r = rOf(rho); if (r > RN) return clamp(log(RMAX / r) / log(RMAX / RN), 0.0, 1.0); float q = r / RN; return 1.0 - 1.6 * (1.0 - q * q); }
vec4 shade(vec2 p) {
  vec2 d = p - u_c; float rho = length(d); vec2 dir = rho > 0.0 ? d / rho : vec2(0.0);
  float h = hOf(rho), dh = (hOf(rho + 1.0) - hOf(max(rho - 1.0, 0.0))) * 0.5;
  vec3 n = normalize(vec3(-dir * dh * u_rp * 1.1, 1.0)); vec3 L = normalize(vec3(-0.5, -0.62, 0.62));
  float lam = clamp(dot(n, L), 0.0, 1.0), spec = pow(max(dot(reflect(-L, n), vec3(0.0, 0.0, 1.0)), 0.0), 18.0);
  vec3 col = mix(u_paper, u_warm, smoothstep(0.0, 0.75, h));
  col = mix(col, u_hot, smoothstep(0.7, 1.0, h));
  float r = rOf(rho);
  if (r < RN) { float q = r / RN; col = mix(u_deep, u_hot, q * q); col += u_hot * 0.25 * (0.5 + 0.5 * sin(u_t * 2.2)) * (1.0 - q); }
  col *= 0.6 + 0.7 * lam; col += vec3(0.35) * spec * smoothstep(0.1, 0.6, h);
  float cl = abs(fract(h * 9.0 + 0.5) - 0.5) / max(9.0 * abs(dh), 1e-4);
  col = mix(col, u_deep, 0.10 * (1.0 - smoothstep(0.0, 1.1, cl)) * step(0.02, h));
  float rhoc = u_rp * log(1.0 + u_rc / R0) / LM;
  float ring = exp(-pow((rho - rhoc) / 1.8, 2.0)) + 0.35 * exp(-pow((rho - rhoc) / 7.0, 2.0));
  col = mix(col, u_ring, clamp(ring, 0.0, 1.0) * 0.85);
  float a = (1.0 - smoothstep(u_rp * 0.88, u_rp * 1.02, rho)) * (0.35 + 0.65 * smoothstep(0.0, 0.25, h) + ring);
  return vec4(col, clamp(a, 0.0, 1.0));
}`;
  let hillGL, hillTried = false, cpuField = null;
  function hillField(g, S, cx, cy, RP, rc) {
    const c = g.c;
    if (!hillTried) { hillTried = true; hillGL = WT.shader(HILL_GLSL); }
    const U = { u_c: [cx, cy], u_rp: RP, u_rc: rc, u_t: S.time, u_paper: WT.rgb01(c.paper), u_warm: WT.rgb01(c.warm), u_hot: WT.rgb01(c.photon), u_deep: WT.rgb01(c.ink), u_ring: WT.rgb01(c.neutron) };
    if (hillGL) { hillGL.draw(g, U, Math.min(1.5, window.devicePixelRatio || 1)); return; }
    // CPU fallback: the same relief, coarser
    const NX = Math.max(60, Math.round(g.W / 4)), NY = Math.max(60, Math.round(g.H / 4));
    if (!cpuField || cpuField.width !== NX || cpuField.height !== NY) { cpuField = document.createElement("canvas"); cpuField.width = NX; cpuField.height = NY; }
    const fc = cpuField.getContext("2d"), img = fc.createImageData(NX, NY), D = img.data;
    const rOf = (rho) => R0 * (Math.exp((rho / RP) * LMAP) - 1);
    const hOf = (rho) => { const r = rOf(rho); if (r > RN) return clamp(Math.log(RMAX / r) / Math.log(RMAX / RN), 0, 1); const q = r / RN; return 1 - 1.6 * (1 - q * q); };
    const P = U.u_paper, Wm = U.u_warm, Ho = U.u_hot, De = U.u_deep, Ri = U.u_ring, rhoc = rhoOf(rc, RP);
    for (let j = 0; j < NY; j++) for (let i = 0; i < NX; i++) {
      const x = ((i + 0.5) / NX) * g.W - cx, y = ((j + 0.5) / NY) * g.H - cy, rho = Math.hypot(x, y), h = hOf(rho), dh = (hOf(rho + 1) - hOf(Math.max(rho - 1, 0))) / 2;
      const nx = rho ? (-x / rho) * dh * RP * 0.55 : 0, ny = rho ? (-y / rho) * dh * RP * 0.55 : 0, nl = Math.hypot(nx, ny, 1);
      const lam = clamp((nx * -0.5 + ny * -0.62 + 0.62) / nl / 0.9876, 0, 1);
      const a1 = smooth(0, 0.75, h), a2 = smooth(0.7, 1, h), ring = Math.min(1, Math.exp(-(((rho - rhoc) / 1.8) ** 2)) + 0.35 * Math.exp(-(((rho - rhoc) / 7) ** 2)));
      const r = rOf(rho), q = r / RN, k = (0.72 + 0.55 * lam);
      const al = (1 - smooth(RP * 0.88, RP * 1.02, rho)) * (0.35 + 0.65 * smooth(0, 0.25, h) + ring), p4 = (j * NX + i) * 4;
      for (let ch = 0; ch < 3; ch++) {
        let v = lerp(lerp(P[ch], Wm[ch], a1), Ho[ch], a2);
        if (r < RN) v = lerp(De[ch], Ho[ch], q * q);
        v = lerp(v * k, Ri[ch], ring * 0.85); D[p4 + ch] = clamp(v, 0, 1) * 255;
      }
      D[p4 + 3] = clamp(al, 0, 1) * 255;
    }
    fc.putImageData(img, 0, 0); g.ctx.save(); g.ctx.imageSmoothingEnabled = true; g.ctx.drawImage(cpuField, 0, 0, g.W, g.H); g.ctx.restore();
  }
  /** Integrate a Coulomb orbit (mu = 1, E in keV, lengths in fm) from (-RS, 0) along angle psi. */
  const RS = RMAX * 0.97;
  function newShot(E, psi) {
    const v = Math.sqrt(2 * E);
    return { E, psi, b: RS * Math.sin(psi), x: -RS, y: 0, vx: v * Math.cos(psi), vy: v * Math.sin(psi), t: 0, rmin: 1e9, rdotPrev: -1, state: "fly", trail: [], age: 0 };
  }
  function stepOrbit(s, simT) {
    let left = simT, n = 0;
    while (left > 0 && n++ < 6000) {
      const r = Math.hypot(s.x, s.y), v = Math.hypot(s.vx, s.vy) + 1e-6;
      const dt = Math.min(left, (0.01 * r) / v, 0.02 * Math.sqrt((r * r * r) / KC));
      const a = KC / (r * r * r);
      s.vx += 0.5 * dt * a * s.x; s.vy += 0.5 * dt * a * s.y; s.x += dt * s.vx; s.y += dt * s.vy;
      const r2 = Math.hypot(s.x, s.y), a2 = KC / (r2 * r2 * r2); s.vx += 0.5 * dt * a2 * s.x; s.vy += 0.5 * dt * a2 * s.y;
      left -= dt; const rdot = s.x * s.vx + s.y * s.vy;
      if (r2 < s.rmin) s.rmin = r2;
      if (s.rdotPrev < 0 && rdot >= 0) { s.rdotPrev = rdot; return "turn"; }
      s.rdotPrev = rdot;
    }
    return null;
  }
  function preview(E, psi) {
    const s = newShot(E, psi), pts = [[s.x, s.y]], v0 = Math.sqrt(2 * E);
    for (let i = 0; i < 160; i++) { stepOrbit(s, 6 / v0); pts.push([s.x, s.y]); if (Math.hypot(s.x, s.y) > RMAX) break; }
    return pts;
  }

  // ---------- scene 2: the products of four fuels ----------
  // [label, reactants [[A, Z, label]], products [[A, Z, E MeV, label]], Z1 Z2, Q MeV]
  const FUELS = {
    DT: ["D–T", [[2, 1, "d"], [3, 1, "t"]], [[[4, 2, 3.52, "α"], [1, 0, 14.07, "n"]]], 1, 17.59],
    DD: ["D–D", [[2, 1, "d"], [2, 1, "d"]], [[[3, 1, 1.01, "t"], [1, 1, 3.02, "p"]], [[3, 2, 0.82, "³He"], [1, 0, 2.45, "n"]]], 1, 3.65],
    DHe: ["D–³He", [[2, 1, "d"], [3, 2, "³He"]], [[[4, 2, 3.67, "α"], [1, 1, 14.68, "p"]]], 2, 18.35],
    pB: ["p–¹¹B", [[1, 1, "p"], [11, 5, "¹¹B"]], [[[4, 2, 2.89, "α"], [4, 2, 2.89, "α"], [4, 2, 2.89, "α"]]], 5, 8.68],
  };
  const colOf = (g, A, Z) => (A === 1 ? (Z ? g.c.proton : g.c.neutron) : A === 4 ? g.c.alpha : A === 2 ? g.c.warm : A === 3 && Z === 1 ? g.c.fission : g.c.proton);
  function particle(g, x, y, A, Z, R, t, seed) {
    if (A === 1) { g.ball(x, y, R * 0.55, Z ? g.c.proton : g.c.neutron); return; }
    g.glow(x, y, R * 2.2, colOf(g, A, Z), 0.22);
    g.nucleus(x, y, R, { N: A, Z, seed, t, jiggle: 0.5 });
  }

  // ---------- scene 3: the hot gas ----------
  const GAS = []; let gasInit = false;
  const flashes = [];
  function initGas() {
    const r = rng(19); GAS.length = 0;
    const gauss = () => Math.sqrt(-2 * Math.log(r() + 1e-12)) * Math.cos(TAU * r());
    for (let i = 0; i < 150; i++) { const m = i % 2 ? 3 : 2; GAS.push({ x: r(), y: r(), ux: gauss() / Math.sqrt(m), uy: gauss() / Math.sqrt(m), m }); }
    gasInit = true;
  }

  WT.chapter("fusion", {
    num: "Chapter 29", title: "Fusion and the Coulomb barrier", short: "Fusion",
    lead: "Fusion runs the other way from fission: two light nuclei join, and the pair weighs less than its parts.",
    html: `
<div class="step">
  <h3>Coulomb barrier and tunnelling</h3>
  <p>Pull the deuteron back and let go. Both nuclei are charged, so most shots bounce off the hill; a few tunnel through.</p>
  <div class="ctl"><label for="fu-e">Push (keV)</label><input id="fu-e" type="range" data-bind="lE" min="0.5" max="2.6" step="0.01" value="1.7"><output data-show="E" data-fmt="0"></output></div>
  <div class="btns"><button class="btn" data-act="fire">Fire</button></div>
</div>
<div class="step">
  <h3>Reaction products and Q-value</h3>
  <p>The joined pair is lighter than the two parts. The missing mass flies off as fast particles.</p>
  <div class="btns fu-fuels"><button class="btn ghost" data-act="DT" aria-pressed="true">D–T</button> <button class="btn ghost" data-act="DD" aria-pressed="false">D–D</button> <button class="btn ghost" data-act="DHe" aria-pressed="false">D–³He</button> <button class="btn ghost" data-act="pB" aria-pressed="false">p–¹¹B</button></div>
</div>
<div class="step">
  <h3>Thermonuclear reaction rate</h3>
  <p>In a hot gas the fastest nuclei get through. Each flash is one fusion.</p>
  <div class="ctl"><label for="fu-t">Temperature (keV)</label><input id="fu-t" type="range" data-bind="lT" min="0" max="2" step="0.01" value="1"><output data-show="T" data-fmt="1"></output></div>
</div>`,
    setup(S) {
      S.set("mode", "hill"); S.set("lE", 1.7); S.set("lT", 1); S.set("fuel", "DT"); S.speed = 8;
      S.E = Math.pow(10, 1.7); S.T = 10;
      S.sling = { pull: null, shot: null, tries: 0, fused: 0, last: -10, products: [], auto: 0, touched: false };
      S.on("fire", () => fire(S, S.E, (Math.random() - 0.5) * 0.06));
      const pick = (k) => () => { S.set("fuel", k); S.outT0 = S.time; document.querySelectorAll(".fu-fuels .btn").forEach((b) => b.setAttribute("aria-pressed", String(b.dataset.act === k))); };
      ["DT", "DD", "DHe", "pB"].forEach((k) => S.on(k, pick(k)));
    },
    steps: [
      (S) => { S.set("mode", "hill"); },
      (S) => { S.set("mode", "out"); S.outT0 = S.time; },
      (S) => { S.set("mode", "gas"); },
    ],
    frame(g, S, dt) {
      S.E = Math.pow(10, S.lE); S.T = Math.pow(10, S.lT);
      if (S.mode === "hill") drawHill(g, S, dt);
      else if (S.mode === "out") drawOut(g, S);
      else drawGas(g, S, dt);
    },
  });

  function fire(S, E, psi) {
    const sl = S.sling; sl.shot = newShot(E, psi); sl.tries++; sl.last = S.time;
  }

  function drawHill(g, S, dt) {
    const { W, H, c } = g, phone = W < 600, sl = S.sling;
    const RP = Math.min(W * (phone ? 0.5 : 0.47), H * 0.43), cx = clamp(W * 0.6, RP + 44, W - RP * 0.55), cy = H * (phone ? 0.53 : 0.52);
    const P0 = [cx - rhoOf(RS, RP), cy];
    const toS = (x, y) => { const r = Math.hypot(x, y), a = Math.atan2(y, x), rho = rhoOf(r, RP); return [cx + rho * Math.cos(a), cy + rho * Math.sin(a)]; };
    // the pull: drag vector from the rest point -> energy (log) and aim
    const LMAX = RP * 0.42;
    const pullState = () => { if (!sl.pull) return null; const dx = sl.pull[0] - P0[0], dy = sl.pull[1] - P0[1], l = Math.min(Math.hypot(dx, dy), LMAX);
      const E = 2 * Math.pow(400 / 2, l / LMAX), psi = clamp(Math.atan2(-dy, -dx), -0.35, 0.35); return { l, E, psi, dx, dy }; };
    WT.grab(g.ctx.canvas, {
      down(x, y) { if (S.mode !== "hill") return false; sl.touched = true;
        if (W < 600) { sl.tap = true; return true; }      // phones: a tap (not a scroll) fires at the slider's push
        if (Math.hypot(x - P0[0], y - P0[1]) < 70 || x < cx - RP * 0.5) { sl.pull = [x, y]; return true; } return false; },
      move(x, y) { if (!sl.tap) sl.pull = [x, y]; },
      up() { if (sl.tap) { sl.tap = false; fire(S, S.E, (Math.random() - 0.5) * 0.06); return; } const p = pullState(); sl.pull = null; if (!p) return;
        if (p.l < 10) { fire(S, S.E, (Math.random() - 0.5) * 0.06); return; }
        S.set("lE", Math.log10(p.E)); const inp = document.getElementById("fu-e"); if (inp) inp.value = S.lE; fire(S, p.E, p.psi); },
      cancel() { sl.pull = null; sl.tap = false; },
      hover(x, y) { g.ctx.canvas.style.cursor = S.mode === "hill" && (Math.hypot(x - P0[0], y - P0[1]) < 70 || x < cx - RP * 0.5) ? "grab" : "default"; },
    });
    const ps = pullState(), Eshow = ps ? ps.E : sl.shot ? sl.shot.E : S.E, rc = KC / Eshow;
    hillField(g, S, cx, cy, RP, rc);
    // energy contours of the hill, labelled
    [[10, "10 keV"], [50, "50 keV"], [200, "200 keV"]].forEach(([V, t]) => { const rho = rhoOf(KC / V, RP); g.ring(cx, cy, rho, c.ink, 1, 0.22, [2, 5]); g.label(t, cx + rho * 0.71, cy - rho * 0.71, { color: c.soft, size: 11, alpha: 0.9 }); });
    // the target
    g.nucleus(cx, cy, Math.max(7, RP * 0.05), { N: 3, Z: 1, seed: 4, t: S.time, jiggle: 0.3 });
    g.label("triton", cx, cy + Math.max(7, RP * 0.05) + 13, { color: c.ink, size: 12, weight: 600, bg: true });
    g.label("Coulomb hill", cx, cy - rhoOf(KC / 10, RP) - 14, { color: c.warm, size: phone ? 12 : 14, weight: 600, bg: true });
    // the turning ring (where the push runs out)
    { const rho = rhoOf(rc, RP); if (rc > RN * 1.05) g.label(`turns at ${rc < 20 ? rc.toFixed(1) : rc.toFixed(0)} fm`, cx + rho * 0.72 + 8, cy + rho * 0.72 + 12, { color: c.neutron, size: 12, weight: 600, bg: true, align: "left" }); }
    // the slingshot posts and band
    const post = 22;
    g.line(P0[0] - 4, P0[1] - post, P0[0] - 4, P0[1] + post, c.soft, 3, 0.5);
    let dpos = P0;
    if (ps) {
      dpos = [P0[0] + (ps.dx / Math.max(1, Math.hypot(ps.dx, ps.dy))) * ps.l, P0[1] + (ps.dy / Math.max(1, Math.hypot(ps.dx, ps.dy))) * ps.l];
      g.line(P0[0] - 4, P0[1] - post, dpos[0], dpos[1], c.soft, 1.6, 0.8); g.line(P0[0] - 4, P0[1] + post, dpos[0], dpos[1], c.soft, 1.6, 0.8);
      const pts = preview(ps.E, ps.psi).map((p) => toS(p[0], p[1])); g.poly(pts, c.warm, 1.6, 0.7, [3, 5]);
      const p = pFuse(ps.E, RS * Math.sin(ps.psi));
      g.label(`${ps.E.toFixed(0)} keV · chance ${oneIn(p)}`, dpos[0], dpos[1] - 22, { color: c.ink, size: 13, weight: 600, bg: true });
    }
    // the shot in flight
    const sh = sl.shot;
    if (sh) {
      const v0 = Math.sqrt(2 * sh.E), simRate = (RMAX * 0.75) / v0;   // the first stretch takes ~1.3 s at every energy
      if (sh.state === "fly") {
        const ev = stepOrbit(sh, simRate * Math.min(dt, 0.05));
        sh.trail.push(toS(sh.x, sh.y)); if (sh.trail.length > 90) sh.trail.shift();
        if (ev === "turn") {
          const p = pFuse(sh.E, Math.abs(sh.b));
          if (Math.random() < p) { sh.state = "fused"; sh.t = S.time; sl.fused++; const a = Math.random() * TAU; sl.products.push({ t0: S.time, a, x: cx, y: cy }); }
        }
        if (Math.hypot(sh.x, sh.y) > RMAX * 1.02 && sh.rdotPrev > 0) sl.shot = null;
      } else if (S.time - sh.t > 0.5) sl.shot = null;
      if (sl.shot) {
        const [x, y] = toS(sh.x, sh.y); g.poly(sh.trail, c.warm, 2, 0.5);
        if (sh.state === "fly") { g.glow(x, y, 16, c.warm, 0.35); g.nucleus(x, y, 7, { N: 2, Z: 1, seed: 9, t: S.time, jiggle: 0.2 }); }
      }
    } else if (!ps) {
      g.nucleus(P0[0] + 10, P0[1], 7, { N: 2, Z: 1, seed: 9, t: S.time, jiggle: 0.2 });
      g.label(phone ? "tap to fire" : "deuteron: pull back, let go", P0[0] + 10, P0[1] + 28, { color: c.ink, size: 12, weight: 600, bg: true, align: phone ? "center" : "left" });
    }
    // fusion products: alpha and neutron back to back, the neutron 4x faster (momentum balance)
    for (let i = sl.products.length - 1; i >= 0; i--) {
      const pr = sl.products[i], age = S.time - pr.t0; if (age > 2.6) { sl.products.splice(i, 1); continue; }
      const sp = Math.min(W, H) * 0.42, xn = pr.x + Math.cos(pr.a) * sp * age, yn = pr.y + Math.sin(pr.a) * sp * age;
      const xa = pr.x - Math.cos(pr.a) * sp * 0.25 * age, ya = pr.y - Math.sin(pr.a) * sp * 0.25 * age, fade = 1 - smooth(1.8, 2.6, age);
      if (age < 0.5) g.glow(pr.x, pr.y, 30 + 160 * age, c.photon, 0.9 * (1 - age / 0.5));
      g.line(xn - Math.cos(pr.a) * 30, yn - Math.sin(pr.a) * 30, xn, yn, c.neutron, 2.5, 0.6 * fade);
      g.ball(xn, yn, 5, c.neutron, fade); g.label("n 14.1 MeV", xn, yn - 14, { color: c.neutron, size: 12, weight: 600, alpha: fade, bg: true });
      g.glow(xa, ya, 14, c.alpha, 0.3 * fade); g.nucleus(xa, ya, 7, { N: 4, Z: 2, seed: 2, t: S.time, alpha: fade });
      g.label("α 3.5 MeV", xa, ya + 16, { color: c.alpha, size: 12, weight: 600, alpha: fade, bg: true });
    }
    // auto-fire while nobody plays (so the picture is never still)
    if (!sl.touched && !sl.shot && !ps && S.time - sl.last > 2.2) fire(S, Math.pow(10, 1.6 + 0.6 * Math.random()), (Math.random() - 0.5) * 0.05);
    // readouts
    const E = ps ? ps.E : S.E;
    g.label(`push ${E.toFixed(0)} keV · chance to tunnel head-on ${oneIn(pTun(E))}`, W / 2, phone ? 16 : 26, { color: c.ink, size: phone ? 12 : 14, weight: 600, bg: true });
    g.label(`tries ${sl.tries} · fused ${sl.fused}`, W / 2, H - (phone ? 14 : 24), { color: c.soft, size: phone ? 12 : 13, bg: true });
    if (!phone) g.label("screen radius is logarithmic: 4 fm to 400 fm", W / 2, H - 46, { color: c.faint, size: 11 });
  }

  // atomic masses (u) for the mass balance
  const MASS = { d: 2.014102, t: 3.016049, "³He": 3.016029, α: 4.002602, n: 1.008665, p: 1.007825, "¹¹B": 11.009305 };
  const events = [];
  function drawOut(g, S) {
    const { W, H, c } = g, phone = W < 600, f = FUELS[S.fuel] || FUELS.DT;
    const cx = W * 0.5, cy = H * (phone ? 0.44 : 0.43), PER = 1.5;
    if (S.outFuel !== S.fuel) { S.outFuel = S.fuel; events.length = 0; S.outN = 0; S.outT0 = S.time - PER; }
    // a new fusion every PER seconds, in a random direction; branches alternate
    while (S.time - S.outT0 >= PER) {
      S.outT0 += PER; const n = S.outN++, r = rng(n * 7919 + 104729), br = f[2].length > 1 ? n % 2 : 0;
      r(); r(); events.push({ t0: S.outT0, dir: r() * TAU, br, sgn: 1 }); if (events.length > 9) events.shift();
    }
    // a bubble chamber in a magnetic field (into the page): charged products curl with radius p/(qB), p = sqrt(2 m E);
    // the neutron has no charge, leaves no bubbles and flies straight (dashed)
    const k = Math.min(W, H) * (phone ? 0.16 : 0.13), vk = Math.min(W, H) * 0.32, ctx = g.ctx;
    g.glow(cx, cy, 70, c.photon, 0.12);
    let newest = null;
    for (const ev of events) {
      const age = S.time - ev.t0, prods = f[2][ev.br], fade = 1 - smooth(6, 13, age);
      if (fade <= 0) continue; newest = ev;
      if (age < 0.5) { g.glow(cx, cy, 30 + 180 * age, c.photon, 0.9 * (1 - age / 0.5)); g.glow(cx, cy, 22, "#ffffff", 0.7 * (1 - age / 0.5)); }
      prods.forEach(([A, Z, E, lab], i) => {
        const a = ev.dir + (prods.length === 3 ? (i * TAU) / 3 : i * Math.PI), col = colOf(g, A, Z);
        const p = Math.sqrt(2 * A * E), sLen = vk * Math.min(age * Math.sqrt(E / A) * 0.6, 3.2);   // path length so far (speed ~ sqrt(E/A))
        let x = cx, y = cy, last = [cx, cy];
        if (!Z) {   // neutron: straight, dashed, no bubbles
          const L = Math.min(sLen, Math.hypot(W, H)); x = cx + Math.cos(a) * L; y = cy + Math.sin(a) * L;
          g.line(cx, cy, x, y, col, 1.6, 0.55 * fade, [5, 6]); last = [x, y];
        } else {
          const R = (k * p) / (Z * 2.8);    // radius of curvature, px
          const nb = Math.floor(sLen / 4), sR = rng(Math.round(ev.t0 * 100) + i);
          ctx.save(); ctx.fillStyle = col;
          for (let b = 0; b < nb; b++) {
            const s = b * 4, th = s / R, px = cx + R * (Math.sin(a + th) - Math.sin(a)), py = cy - R * (Math.cos(a + th) - Math.cos(a));
            if (th > TAU * 0.92) break;
            ctx.globalAlpha = (0.25 + 0.55 * sR()) * fade; ctx.beginPath(); ctx.arc(px + (sR() - 0.5) * 1.2, py + (sR() - 0.5) * 1.2, 1.1 + 0.9 * sR() * Math.min(1, 2.5 / p), 0, TAU); ctx.fill();
            last = [px, py];
          }
          ctx.restore();
        }
        if (ev === events[events.length - 1] || age < 2.4) {
          const lf = 1 - smooth(1.6, 2.4, age);
          if (lf > 0) {
            if (A === 1) g.ball(last[0], last[1], 5, col, lf); else { g.glow(last[0], last[1], 14, col, 0.3 * lf); g.nucleus(last[0], last[1], 6.5 * Math.cbrt(A) * 0.8, { N: A, Z, seed: 2 + i, t: S.time, alpha: lf }); }
            g.label(`${lab} ${E.toFixed(E < 10 ? 2 : 1)} MeV`, last[0], last[1] - 15, { color: col, size: phone ? 12 : 13, weight: 600, alpha: lf, bg: true });
          }
        }
      });
    }
    // the reactants arriving at the centre, just before each new event
    const tin = (S.time - S.outT0) / PER;
    if (tin > 0.55) { const s = 1 - smooth(0.55, 1, tin), d = s * Math.min(W, H) * 0.3 + 8;
      const [a1, a2] = f[1]; particle(g, cx - d, cy, a1[0], a1[1], 6.5 * Math.cbrt(a1[0]), S.time, 3); particle(g, cx + d, cy, a2[0], a2[1], 6.5 * Math.cbrt(a2[0]), S.time, 5); }
    // the mass balance: before and after, the difference is the energy released (E = mc^2)
    const br = newest ? newest.br : 0, prods = f[2][br];
    const mIn = f[1].reduce((s, r) => s + MASS[r[2]], 0), mOut = prods.reduce((s, r) => s + MASS[r[3]], 0), dm = mIn - mOut;
    const by = H * (phone ? 0.8 : 0.82), lab = (s, x, y, o) => g.label(s, x, y, Object.assign({ size: phone ? 11 : 13 }, o));
    lab(`${f[1].map((r) => r[2]).join(" + ")}  ${mIn.toFixed(4)} u   →   ${prods.map((r) => r[3]).join(" + ")}  ${mOut.toFixed(4)} u`, W / 2, by, { color: c.ink, weight: 600, bg: true });
    lab(`missing ${dm.toFixed(4)} u  =  ${(dm * 931.494).toFixed(2)} MeV out`, W / 2, by + (phone ? 20 : 24), { color: c.photon, weight: 600, bg: true });
    lab(`hill to climb: charge product Z₁Z₂ = ${f[3]}`, W / 2, by + (phone ? 40 : 48), { color: c.warm, size: phone ? 11 : 12 });
    g.label(f[0] + (f[2].length > 1 ? " · two branches, equally likely" : ""), W / 2, phone ? 16 : 30, { color: c.ink, size: phone ? 14 : 18, weight: 600, serif: true });
    if (!phone) g.label("bubble-chamber view, magnetic field into the page: charged products curl, the neutron leaves no track", W / 2, phone ? 34 : 54, { color: c.faint, size: 12 });
  }

  function drawGas(g, S, dt) {
    const { W, H, c } = g, phone = W < 600, ctx = g.ctx;
    if (!gasInit) initGas();
    const T = S.T, bx = phone ? 14 : W * 0.1, by = phone ? 30 : H * 0.1, bw = W - 2 * bx, bh = H * (phone ? 0.58 : 0.6);
    // the box: a faint glow that warms with T
    const heat = clamp(Math.log10(T) / 2, 0, 1);
    { const gr = ctx.createRadialGradient(bx + bw / 2, by + bh / 2, 0, bx + bw / 2, by + bh / 2, Math.max(bw, bh) * 0.7);
      gr.addColorStop(0, g.rgba(c.warm, 0.05 + 0.18 * heat)); gr.addColorStop(1, g.rgba(c.warm, 0.02)); ctx.fillStyle = gr; ctx.beginPath(); ctx.roundRect ? ctx.roundRect(bx, by, bw, bh, 14) : ctx.rect(bx, by, bw, bh); ctx.fill();
      ctx.strokeStyle = g.rgba(c.soft, 0.35); ctx.lineWidth = 1.2; ctx.stroke(); }
    // speeds ~ sqrt(T/m): the same Maxwellian, scaled
    const vs = 0.11 * Math.sqrt(T / 10), sub = 3;
    for (let s = 0; s < sub; s++) for (const p of GAS) {
      p.x += (p.ux * vs * dt) / sub; p.y += ((p.uy * vs * dt) / sub) * (bw / bh);
      if (p.x < 0) { p.x = -p.x; p.ux = Math.abs(p.ux); } if (p.x > 1) { p.x = 2 - p.x; p.ux = -Math.abs(p.ux); }
      if (p.y < 0) { p.y = -p.y; p.uy = Math.abs(p.uy); } if (p.y > 1) { p.y = 2 - p.y; p.uy = -Math.abs(p.uy); }
    }
    const rr = phone ? 2.6 : 3.4;
    for (const p of GAS) {
      const x = bx + p.x * bw, y = by + p.y * bh, sp = Math.hypot(p.ux, p.uy) * Math.sqrt(p.m / 2);
      const col = p.m === 2 ? c.warm : c.fission;
      g.line(x - p.ux * 6 * Math.sqrt(T / 10), y - p.uy * 6 * Math.sqrt(T / 10), x, y, col, 1.2, 0.25);
      g.ball(x, y, rr * (0.9 + 0.1 * p.m), col, 0.55 + 0.45 * clamp(sp / 2.5, 0, 1));
    }
    // fusions: Poisson, rate ~ <sigma v>(T), 1.2 per second at 10 keV
    const rel = sv("DT", T) / sv("DT", 10), lam = Math.min(1.2 * rel, 40);
    if (Math.random() < 1 - Math.exp(-lam * dt)) { const p = GAS[(Math.random() * GAS.length) | 0]; flashes.push({ x: p.x, y: p.y, t0: S.time, a: Math.random() * TAU }); }
    for (let i = flashes.length - 1; i >= 0; i--) {
      const f = flashes[i], age = S.time - f.t0; if (age > 1.6) { flashes.splice(i, 1); continue; }
      const x = bx + f.x * bw, y = by + f.y * bh;
      g.glow(x, y, 10 + 70 * age, c.photon, 0.8 * Math.max(0, 1 - age / 0.6));
      const d = age * Math.max(W, H) * 0.9; g.line(x + Math.cos(f.a) * Math.max(0, d - 26), y + Math.sin(f.a) * Math.max(0, d - 26), x + Math.cos(f.a) * d, y + Math.sin(f.a) * d, c.neutron, 2.4, 0.7);
      g.glow(x, y, 9, c.alpha, 0.6 * (1 - age / 1.6));
    }
    // legend, thermometer (log 1-100 keV) and the rate
    const ly = by + bh + (phone ? 16 : 22);
    g.ball(bx + 6, ly, 4, c.warm); g.label("deuteron", bx + 16, ly, { color: c.soft, size: 12, align: "left" });
    g.ball(bx + 96, ly, 4, c.fission); g.label("triton", bx + 106, ly, { color: c.soft, size: 12, align: "left" });
    g.line(bx + 170, ly, bx + 190, ly, c.neutron, 2.4); g.label("neutron escapes", bx + 196, ly, { color: c.soft, size: 12, align: "left" });
    const ty = ly + (phone ? 40 : 44), tx0 = bx, tw = bw, X = (Tk) => tx0 + (tw * Math.log10(Tk)) / 2;
    { const gr = ctx.createLinearGradient(tx0, 0, tx0 + tw, 0); gr.addColorStop(0, g.rgba(c.cool, 0.6)); gr.addColorStop(0.5, g.rgba(c.warm, 0.7)); gr.addColorStop(1, g.rgba(c.photon, 0.9)); ctx.fillStyle = gr; ctx.fillRect(tx0, ty - 3, tw, 6); }
    [1, 10, 100].forEach((v) => { g.line(X(v), ty - 7, X(v), ty + 7, c.soft, 1); g.label(`${v} keV`, X(v), ty + 17, { color: c.soft, size: 11, align: v === 1 ? "left" : v === 100 ? "right" : "center" }); });
    g.line(X(1.3), ty - 10, X(1.3), ty + 3, c.photon, 2); g.label("Sun's core", X(1.3) + 4, ty - 16, { color: c.soft, size: 11, align: "left" });
    g.dot(X(T), ty, 7, c.ink); g.ring(X(T), ty, 11, c.ink, 1.5, 0.5);
    g.label(`${T.toFixed(T < 10 ? 1 : 0)} keV = ${(T * 11.6).toFixed(0)} million K`, W / 2, phone ? 14 : by - 22, { color: c.ink, size: phone ? 13 : 15, weight: 600, bg: true });
    const relS = rel >= 1 ? `×${rel < 10 ? rel.toFixed(1) : rel.toFixed(0)}` : `1/${(1 / rel) < 1e4 ? Math.round(1 / rel).toLocaleString("en-US") : (1 / rel).toExponential(0).replace("e+", "·10^")}`;
    g.label(`fusion rate: ${relS} the rate at 10 keV`, W / 2, ty + (phone ? 34 : 42), { color: c.photon, size: phone ? 12 : 14, weight: 600, bg: true });
  }
})();
