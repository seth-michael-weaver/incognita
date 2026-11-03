/* Chapter 30 (part three, Intermediate): burning plasma. Physics explanation (no INCOGNITA computation). Scenes:
 *   "window" = a WebGL heat field over energy E (x, 0-250 keV) and temperature T (y, 1-100 keV, log): brightness is
 *              exp(-E/kT - sqrt(E_G/E)) relative to its maximum at the Gamow peak E0 = (E_G (kT)^2 / 4)^(1/3), times a row
 *              weight from the saddle-point integral ~ T^(-2/3) exp(-3 E0/kT). The reader drags the T line; below, the
 *              slice: the Maxwell tail exp(-E/kT), the tunnelling factor exp(-sqrt(E_G/E)) and their product, with
 *              E0 and the width 4 sqrt(E0 kT / 3). D-T: E_G = 1182 keV.
 *   "fuels"  = <sigma v>(T) for D-T, D-D (both branches) and D-3He on log axes, Bosch & Hale (1992), 1-100 keV.
 *   "lawson" = the Lawson plane (T, n tau_E), n = 1e20 m^-3, 50:50 D-T. Steady state with heating P_h:
 *              P_alpha + P_h = 3 n T / tau_E + C_B n^2 sqrt(T), P_alpha = n^2/4 <sigma v> E_alpha, Q = 5 P_alpha / P_h.
 *              Curves n tau_E = 3 T / ((1 + 5/Q) <sigma v> E_alpha / 4 - C_B sqrt T) for Q = 1, 10 and infinity
 *              (ignition); C_B = 5.35e-37 W m^3 keV^-1/2 (bremsstrahlung, Z_eff = 1). Released, the point follows a 0-D
 *              power balance with the heating off and tau_E degrading with power as P^-0.69 (IPB98(y,2) exponent;
 *              never improving above its value at release): below the ignition curve it cools and is lost, above it
 *              heats itself and settles where alpha heating equals the losses, on the ignition curve. */
(function () {
  const { TAU, clamp, lerp, smooth } = WT.util;
  const F = () => WT.fus;
  const EGDT = 34.3827 ** 2;
  const lg = Math.log10;
  const sup = (n) => String(n).replace(/-/g, "⁻").replace(/\d/g, (d) => "⁰¹²³⁴⁵⁶⁷⁸⁹"[d]);
  const sci = (v, d = 1) => { const e = Math.floor(lg(v)), m = v / 10 ** e; return `${m.toFixed(d)}·10${sup(e)}`; };

  // ---------- scene 1: the Gamow window as a heat field ----------
  const GLSL = `
uniform vec4 u_rect; uniform float u_EG, u_T, u_t;
uniform vec3 u_paper, u_cool, u_warm, u_hot, u_peak;
float lnI(float T) { return -(2.0 / 3.0) * log(T) - 3.0 * pow(u_EG / (4.0 * T), 1.0 / 3.0); }
vec4 shade(vec2 p) {
  vec2 q = (p - u_rect.xy) / (u_rect.zw - u_rect.xy);
  if (q.x < 0.0 || q.x > 1.0 || q.y < 0.0 || q.y > 1.0) return vec4(0.0);
  float E = max(q.x * 250.0, 0.05), T = pow(10.0, 2.0 * (1.0 - q.y));
  float tau = 3.0 * pow(u_EG / (4.0 * T), 1.0 / 3.0);
  float b = exp(-E / T - sqrt(u_EG / E) + tau);
  float row = clamp((lnI(T) - lnI(1.0)) / (lnI(100.0) - lnI(1.0)), 0.0, 1.0);
  float tail = exp(-E / T), tun = exp(-sqrt(u_EG / E));
  vec3 col = u_paper;
  col = mix(col, u_cool, 0.35 * tail);
  col = mix(col, u_warm, 0.30 * tun);
  float glow = b * (0.25 + 0.75 * row);
  col = mix(col, u_hot, smoothstep(0.0, 0.6, glow));
  col = mix(col, u_peak, smoothstep(0.55, 1.0, glow) * (0.6 + 0.4 * row));
  float sel = exp(-pow((q.y - (1.0 - log(u_T) / log(10.0) / 2.0)) * (u_rect.w - u_rect.y) / 2.0, 2.0));
  col = mix(col, vec3(1.0), 0.35 * sel * (0.6 + 0.4 * sin(u_t * 3.0 + q.x * 20.0)));
  float edge = smoothstep(0.0, 0.02, q.x) * smoothstep(0.0, 0.02, 1.0 - q.x) * smoothstep(0.0, 0.03, q.y) * smoothstep(0.0, 0.03, 1.0 - q.y);
  return vec4(col, 0.15 + 0.85 * edge);
}`;
  let gl = null, glTried = false, cpu = null;
  function field(g, S, R) {
    const c = g.c; if (!glTried) { glTried = true; gl = WT.shader(GLSL); }
    const U = { u_rect: R, u_EG: EGDT, u_T: S.T, u_t: S.time, u_paper: WT.rgb01(c.paper), u_cool: WT.rgb01(c.cool), u_warm: WT.rgb01(c.warm), u_hot: WT.rgb01(c.alpha), u_peak: WT.rgb01(c.photon) };
    if (gl) { gl.draw(g, U, Math.min(1.5, window.devicePixelRatio || 1)); return; }
    // CPU fallback: the same field at 1/4 resolution over the rectangle
    const [x0, y0, x1, y1] = R, NX = Math.max(40, Math.round((x1 - x0) / 4)), NY = Math.max(30, Math.round((y1 - y0) / 4));
    if (!cpu || cpu.width !== NX || cpu.height !== NY) { cpu = document.createElement("canvas"); cpu.width = NX; cpu.height = NY; }
    const fc = cpu.getContext("2d"), img = fc.createImageData(NX, NY), D = img.data;
    const lnI = (T) => -(2 / 3) * Math.log(T) - 3 * Math.cbrt(EGDT / (4 * T)), l1 = lnI(1), l100 = lnI(100);
    for (let j = 0; j < NY; j++) { const T = 10 ** (2 * (1 - (j + 0.5) / NY)), tau = 3 * Math.cbrt(EGDT / (4 * T)), row = clamp((lnI(T) - l1) / (l100 - l1), 0, 1);
      for (let i = 0; i < NX; i++) { const E = Math.max(((i + 0.5) / NX) * 250, 0.05), b = Math.exp(-E / T - Math.sqrt(EGDT / E) + tau), tail = Math.exp(-E / T), tun = Math.exp(-Math.sqrt(EGDT / E)), glow = b * (0.25 + 0.75 * row), p = (j * NX + i) * 4;
        for (let k = 0; k < 3; k++) { let v = U.u_paper[k]; v = lerp(v, U.u_cool[k], 0.35 * tail); v = lerp(v, U.u_warm[k], 0.3 * tun); v = lerp(v, U.u_hot[k], smooth(0, 0.6, glow)); v = lerp(v, U.u_peak[k], smooth(0.55, 1, glow) * (0.6 + 0.4 * row)); D[p + k] = v * 255; }
        D[p + 3] = 255; } }
    fc.putImageData(img, 0, 0); g.ctx.save(); g.ctx.imageSmoothingEnabled = true; g.ctx.drawImage(cpu, x0, y0, x1 - x0, y1 - y0); g.ctx.restore();
  }

  // ---------- Lawson plane ----------
  const NDEN = 1e20;
  const pAlpha = (T) => (NDEN * NDEN / 4) * F().sv("DT", T) * F().EALPHA * F().KEV;      // W/m^3
  const pBrem = (T) => F().CB * NDEN * NDEN * Math.sqrt(T);
  function ntCurve(T, Q) { const d = (1 + 5 / Q) * (F().sv("DT", T) * F().EALPHA * F().KEV) / 4 - F().CB * Math.sqrt(T); return d > 0 ? (3 * T * F().KEV) / d : Infinity; }

  WT.chapter("gamow", {
    num: "Chapter 30", title: "The Gamow peak and ignition", short: "Gamow peak",
    lead: "A hot plasma burns through a narrow window of energies: fast enough to tunnel, common enough to matter.",
    html: `
<div class="step">
  <h3>The Gamow peak</h3>
  <p>Few nuclei are fast; fast ones tunnel more easily. The product glows: the Gamow peak. Drag the temperature line.</p>
  <div class="ctl"><label for="gw-t">Temperature kT (keV)</label><input id="gw-t" type="range" data-bind="lT" min="0" max="2" step="0.01" value="1"><output data-show="T" data-fmt="1"></output></div>
  <div class="formula">E₀ = (E<sub>G</sub> (kT)² / 4)<sup>1/3</sup> · width 4√(E₀kT/3)</div>
</div>
<div class="step">
  <h3>Fuel reactivities</h3>
  <p>Add up the window and you get the reactivity ⟨σv⟩. D–T wins by far at any temperature a machine can reach.</p>
  <div class="ctl"><label for="gw-t2">Temperature kT (keV)</label><input id="gw-t2" type="range" data-bind="lT" min="0" max="2" step="0.01" value="1"><output data-show="T" data-fmt="1"></output></div>
  <div class="formula">⟨σv⟩ = ∫ σ(E) v f(E) dE</div>
</div>
<div class="step">
  <h3>The Lawson criterion and ignition</h3>
  <p>Drag the plasma to a temperature and confinement, then let go. Above the top curve it keeps itself hot.</p>
  <div class="btns"><button class="btn" data-act="lowgo">Try a weak machine</button> <button class="btn ghost" data-act="higo">Try a strong one</button></div>
  <div class="formula">ignition: n τ<sub>E</sub> T ≳ 3·10²¹ keV s m⁻³</div>
</div>`,
    setup(S) {
      S.set("mode", "window"); S.set("lT", 1); S.T = 10; S.speed = 8;
      S.law = { T: 10, nt: 1.5e21, held: false, run: false, trail: [], msg: "", touched: false, t0: 0 };
      S.on("lowgo", () => launch(S, 6, 2e19)); S.on("higo", () => launch(S, 9, 1.4e21));
    },
    steps: [
      (S) => { S.set("mode", "window"); },
      (S) => { S.set("mode", "fuels"); },
      (S) => { S.set("mode", "lawson"); if (!S.law.run && !S.law.held) launch(S, 9, 1.4e21); },
    ],
    frame(g, S, dt) {
      S.T = 10 ** S.lT;
      if (S.mode === "window") drawWindow(g, S);
      else if (S.mode === "fuels") drawFuels(g, S);
      else drawLawson(g, S, dt);
    },
  });

  function setT(S, T) { S.set("lT", clamp(lg(T), 0, 2)); document.querySelectorAll('#gamow input[data-bind="lT"]').forEach((i) => (i.value = S.lT)); }

  function axisLabels(g, xs, y, color) { xs.forEach(([x, t, al]) => g.label(t, x, y, { color, size: 11, align: al || "center" })); }

  function drawWindow(g, S) {
    const { W, H, c } = g, phone = W < 600;
    const x0 = phone ? 40 : W * 0.1, x1 = W - (phone ? 12 : W * 0.06), y0 = phone ? 34 : H * 0.09, y1 = H * (phone ? 0.52 : 0.56);
    const X = (E) => x0 + ((x1 - x0) * E) / 250, Y = (T) => y0 + (y1 - y0) * (1 - lg(T) / 2);
    WT.grab(g.ctx.canvas, {
      down(x, y) { if (S.mode !== "window" || x < x0 || x > x1 || y < y0 - 8 || y > y1 + 8) return false; setT(S, 10 ** (2 * (1 - (y - y0) / (y1 - y0)))); S.T = 10 ** S.target.lT; return true; },
      move(x, y) { setT(S, 10 ** (2 * (1 - clamp((y - y0) / (y1 - y0), 0, 1)))); },
      hover(x, y) { g.ctx.canvas.style.cursor = S.mode === "window" && x > x0 && x < x1 && y > y0 && y < y1 ? "ns-resize" : "default"; },
    });
    field(g, S, [x0, y0, x1, y1]);
    // E0(T) ridge and E = kT, dashed
    const ridge = [], kt = [];
    for (let i = 0; i <= 60; i++) { const T = 10 ** (i / 30), E0 = Math.cbrt((EGDT * T * T) / 4); ridge.push([X(E0), Y(T)]); if (T <= 250) kt.push([X(T), Y(T)]); }
    g.poly(ridge, c.ink, 1.4, 0.55, [4, 5]); g.poly(kt, c.cool, 1.2, 0.6, [2, 4]);
    g.label("Gamow peak E₀", X(Math.cbrt(EGDT * 1600 / 4)) + 10, Y(40), { color: c.ink, size: 12, weight: 600, align: "left", bg: true });
    g.label("E = kT", X(80) - 6, Y(80), { color: c.cool, size: 11, align: "right", bg: true });
    // the selected temperature
    const T = S.T, yT = Y(T), E0 = Math.cbrt((EGDT * T * T) / 4), wid = 4 * Math.sqrt((E0 * T) / 3);
    g.line(x0, yT, x1, yT, c.ink, 2, 0.85); g.dot(X(E0), yT, 5, c.ink); g.ring(X(E0), yT, 9 + 2 * Math.sin(S.time * 4), c.photon, 2, 0.9);
    // axes
    axisLabels(g, [0, 50, 100, 150, 200, 250].map((E) => [X(E), String(E), E === 0 ? "left" : E === 250 ? "right" : "center"]), y1 + 12, c.soft);
    [1, 10, 100].forEach((t) => g.label(`${t}`, x0 - 6, Y(t), { color: c.soft, size: 11, align: "right" }));
    g.label("kT (keV)", x0 - 6, y0 - 14, { color: c.soft, size: 11, align: phone ? "left" : "right" });
    g.label("energy of the colliding pair (keV)", (x0 + x1) / 2, y1 + 26, { color: c.soft, size: 11 });
    // the slice: tail, tunnelling, product
    const sy0 = y1 + (phone ? 42 : 52), sy1 = H - (phone ? 30 : 44), sh = sy1 - sy0;
    const tail = [], tun = [], prod = []; let pmax = 0; const tunMax = Math.exp(-Math.sqrt(EGDT / 250));
    for (let i = 1; i <= 200; i++) { const E = (i / 200) * 250; pmax = Math.max(pmax, Math.exp(-E / T - Math.sqrt(EGDT / E))); }
    for (let i = 0; i <= 200; i++) { const E = Math.max((i / 200) * 250, 1e-3), a = Math.exp(-E / T), b = Math.exp(-Math.sqrt(EGDT / E));
      tail.push([X(E), sy1 - sh * a]); tun.push([X(E), sy1 - (sh * b) / tunMax]); prod.push([X(E), sy1 - sh * 0.92 * ((a * b) / pmax)]); }
    g.area([[X(0), sy1], ...prod, [X(250), sy1]], c.photon, 0.35); g.poly(prod, c.photon, 9, 0.15);
    g.poly(tail, c.cool, 2.2, 0.9); g.poly(tun, c.warm, 2.2, 0.9); g.poly(prod, c.photon, 2.6, 1);
    g.line(x0, sy1, x1, sy1, c.faint, 1);
    g.line(X(E0 - wid / 2), sy1 + 6, X(E0 + wid / 2), sy1 + 6, c.ink, 2); g.line(X(E0), sy1 + 2, X(E0), sy0 + sh * 0.05, c.ink, 1, 0.5, [3, 3]);
    g.label("few are this fast", X(Math.min(240, T * 2.2)) + 4, sy1 - sh * Math.exp(-Math.min(240, T * 2.2) / T) - 10, { color: c.cool, size: 11, align: "left", bg: true });
    g.label("tunnels more easily", X(235), sy0 + 2, { color: c.warm, size: 11, align: "right", bg: true });
    g.label(WT.trf("product ×{a}", sci(1 / pmax, 0)), X(E0) + 8, sy1 - sh * 0.92 - 4, { color: c.photon, size: 12, weight: 600, align: "left", bg: true, raw: true });
    g.label(`kT ${T.toFixed(T < 10 ? 1 : 0)} keV · E₀ ${E0.toFixed(0)} keV · width ${wid.toFixed(0)} keV`, W / 2, H - (phone ? 10 : 16), { color: c.ink, size: phone ? 12 : 14, weight: 600, bg: true });
  }

  function drawFuels(g, S) {
    const { W, H, c } = g, phone = W < 600, ctx = g.ctx;
    const x0 = phone ? 46 : W * 0.12, x1 = W - (phone ? 14 : W * 0.06), y0 = phone ? 60 : H * 0.1, y1 = H - (phone ? 46 : H * 0.14);
    const YMIN = -32, YMAX = -21, X = (T) => x0 + ((x1 - x0) * lg(T)) / 2, Y = (v) => y1 - ((y1 - y0) * (lg(v) - YMIN)) / (YMAX - YMIN);
    WT.grab(ctx.canvas, {
      down(x, y) { if (S.mode !== "fuels" || x < x0 - 10 || x > x1 + 10 || y < y0 || y > y1) return false; setT(S, 10 ** (2 * clamp((x - x0) / (x1 - x0), 0, 1))); return true; },
      move(x) { setT(S, 10 ** (2 * clamp((x - x0) / (x1 - x0), 0, 1))); },
      hover(x, y) { ctx.canvas.style.cursor = S.mode === "fuels" && x > x0 && x < x1 && y > y0 && y < y1 ? "ew-resize" : "default"; },
    });
    // grid
    for (let e = YMIN; e <= YMAX; e++) { g.line(x0, Y(10 ** e), x1, Y(10 ** e), c.line, 1, e % 2 ? 0.4 : 0.9); if (!(e % 2) || !phone) g.label(`10${sup(e)}`, x0 - 6, Y(10 ** e), { color: c.soft, size: 11, align: "right" }); }
    [1, 2, 5, 10, 20, 50, 100].forEach((t) => { g.line(X(t), y0, X(t), y1, c.line, 1, 0.6); g.label(`${t}`, X(t), y1 + 12, { color: c.soft, size: 11 }); });
    g.label("kT (keV)", (x0 + x1) / 2, y1 + 28, { color: c.soft, size: 11 });
    g.label("⟨σv⟩ (m³/s)", x0 - 6, y0 - 16, { color: c.soft, size: 11, align: phone ? "left" : "right" });
    // luminous ribbons with travelling glints
    const FU = [["DT", "D–T", c.photon], ["DHe", "D–³He", c.alpha], ["DD", "D–D", c.cool]];
    FU.forEach(([k, lab, col], fi) => {
      const pts = []; for (let i = 0; i <= 120; i++) { const T = 10 ** (i / 60), v = F().sv(k, T); if (lg(v) > YMIN) pts.push([X(T), Y(v)]); }
      g.poly(pts, col, 12, 0.12); g.poly(pts, col, 5, 0.3); g.poly(pts, col, 2.4, 1);
      for (let j = 0; j < 3; j++) { const u = ((S.time * 0.18 + j / 3 + fi * 0.11) % 1), i = Math.floor(u * (pts.length - 1)); if (pts[i]) g.glow(pts[i][0], pts[i][1], 12, col, 0.6); }
      const end = pts[pts.length - 1]; g.label(lab, end[0] - 4, end[1] - 14, { color: col, size: 13, weight: 700, align: "right", bg: true });
    });
    // D-T maximum
    let best = [0, 0]; for (let i = 0; i <= 400; i++) { const T = 10 ** (i / 200), v = F().sv("DT", T); if (v > best[1]) best = [T, v]; }
    g.ring(X(best[0]), Y(best[1]), 7, c.photon, 1.5, 0.8); g.label(`peak near ${best[0].toFixed(0)} keV`, X(best[0]), Y(best[1]) - 30, { color: c.soft, size: 11, bg: true });
    // the reader's temperature
    const T = S.T, xT = X(T);
    g.line(xT, y0, xT, y1, c.ink, 1.6, 0.7);
    FU.forEach(([k, , col]) => { const v = F().sv(k, T); if (lg(v) > YMIN) { g.dot(xT, Y(v), 6, col); g.ring(xT, Y(v), 10, col, 1.5, 0.6); } });
    const r = F().sv("DT", T) / F().sv("DD", T);
    g.label(WT.trf("kT {a} keV · D–T {b} m³/s · {c}× D–D", T.toFixed(T < 10 ? 1 : 0), sci(F().sv("DT", T)), r.toFixed(0)), W / 2, phone ? 14 : 24, { color: c.ink, size: phone ? 12 : 14, weight: 600, bg: true, raw: true });
  }

  function launch(S, T, nt) { const L = S.law; L.T = T; L.nt = nt; L.held = false; release(S); }
  function release(S) {
    const L = S.law, tau = L.nt / NDEN, pa = pAlpha(L.T), loss = (3 * NDEN * L.T * F().KEV) / tau + pBrem(L.T);
    L.tauRef = tau; L.pRef = pa + Math.max(0, loss - pa); L.run = true; L.trail = []; L.msg = ""; L.clock = 0;
  }
  function drawLawson(g, S, dt) {
    const { W, H, c } = g, phone = W < 600, ctx = g.ctx, L = S.law;
    const x0 = phone ? 46 : W * 0.12, x1 = W - (phone ? 14 : W * 0.06), y0 = phone ? 60 : H * 0.11, y1 = H - (phone ? 62 : H * 0.17);
    const YMIN = 18, YMAX = 22.5, X = (T) => x0 + ((x1 - x0) * lg(T)) / 2, Y = (v) => y1 - ((y1 - y0) * (lg(v) - YMIN)) / (YMAX - YMIN);
    const fromXY = (x, y) => [10 ** (2 * clamp((x - x0) / (x1 - x0), 0, 1)), 10 ** (YMIN + (YMAX - YMIN) * clamp((y1 - y) / (y1 - y0), 0, 1))];
    WT.grab(ctx.canvas, {
      down(x, y) { if (S.mode !== "lawson" || x < x0 - 10 || x > x1 + 10 || y < y0 - 10 || y > y1 + 10) return false; L.touched = true; [L.T, L.nt] = fromXY(x, y); L.held = true; L.run = false; L.trail = []; return true; },
      move(x, y) { if (L.held) [L.T, L.nt] = fromXY(x, y); },
      up() { if (L.held) { L.held = false; release(S); } },
      cancel() { if (L.held) { L.held = false; release(S); } },
      hover(x, y) { ctx.canvas.style.cursor = S.mode === "lawson" && x > x0 && x < x1 && y > y0 && y < y1 ? "crosshair" : "default"; },
    });
    // curves Q = 1, 10, ignition; the self-burning region above ignition glows
    const curve = (Q) => { const p = []; for (let i = 0; i <= 160; i++) { const T = 10 ** (i / 80), v = ntCurve(T, Q); if (isFinite(v) && lg(v) < YMAX + 0.3) p.push([X(T), Y(v)]); } return p; };
    const ign = curve(Infinity);
    if (ign.length > 2) { ctx.save(); const gr = ctx.createLinearGradient(0, y0, 0, y1); gr.addColorStop(0, g.rgba(c.photon, 0.32)); gr.addColorStop(1, g.rgba(c.photon, 0.05));
      ctx.fillStyle = gr; ctx.beginPath(); ctx.moveTo(ign[0][0], y0); ign.forEach((p) => ctx.lineTo(p[0], Math.max(y0, p[1]))); ctx.lineTo(ign[ign.length - 1][0], y0); ctx.closePath(); ctx.fill(); ctx.restore(); }
    for (let e = Math.ceil(YMIN); e <= YMAX; e++) { g.line(x0, Y(10 ** e), x1, Y(10 ** e), c.line, 1, 0.8); g.label(`10${sup(e)}`, x0 - 6, Y(10 ** e), { color: c.soft, size: 11, align: "right" }); }
    [1, 2, 5, 10, 20, 50, 100].forEach((t) => { g.line(X(t), y0, X(t), y1, c.line, 1, 0.5); g.label(`${t}`, X(t), y1 + 12, { color: c.soft, size: 11 }); });
    g.label("kT (keV)", (x0 + x1) / 2, y1 + 28, { color: c.soft, size: 11 });
    g.label("n τE (s/m³)", x0 - 6, y0 - 18, { color: c.soft, size: 11, align: phone ? "left" : "right" });
    [[1, c.cool, "Q = 1", 20.3], [10, c.warm, "Q = 10", 21.0], [Infinity, c.photon, "ignition (Q = ∞)", 21.8]].forEach(([Q, col, lab, yl]) => {
      const p = curve(Q); g.poly(p, col, Q === Infinity ? 3 : 2, 0.95); const m = p.find((q) => q[1] >= Y(10 ** yl));
      if (m) g.label(lab, m[0] - 8, m[1], { color: col, size: 12, weight: 600, align: "right", bg: true });
    });
    if (ign.length > 2) g.label("keeps itself hot", X(30), Y(10 ** 22), { color: c.ink, size: phone ? 12 : 14, weight: 600, serif: true });
    // triple-product minimum
    let best = [1e99, 0]; for (let i = 0; i <= 200; i++) { const T = 10 ** (0.5 + i / 200), v = ntCurve(T, Infinity) * T; if (v < best[0]) best = [v, T]; }
    g.dot(X(best[1]), Y(best[0] / best[1]), 4, c.ink); g.label(WT.trf("easiest: {a} keV, nτT {b}", best[1].toFixed(0), sci(best[0] * 1, 0)), X(best[1]) + 8, Y(best[0] / best[1]) + 16, { color: c.soft, size: 11, align: "left", bg: true, raw: true });
    // dynamics: heating off, tau_E degrading with power
    if (L.run && dt > 0) {
      const warp = 0.9 * L.tauRef, n = 40, h = (dt * warp) / n;
      for (let i = 0; i < n; i++) {
        const pa = pAlpha(L.T), tau = L.tauRef * Math.min(1, (pa / L.pRef) ** -0.69 || 1);
        const dT = (pa - (3 * NDEN * L.T * F().KEV) / tau - pBrem(L.T)) / (3 * NDEN * F().KEV);
        L.T = clamp(L.T + dT * h, 0.9, 100); L.nt = NDEN * tau; L.clock += h; L.rate = dT;
      }
      if (L.T <= 0.95) { L.run = false; L.msg = "cooled down: plasma lost"; }
      else if (Math.abs(L.rate) * L.tauRef < 0.02 * L.T && pAlpha(L.T) > 0.5 * L.pRef) L.msg = "burning on its own";
      else L.msg = L.rate > 0 ? "heating itself" : "cooling";
      const last = L.trail[L.trail.length - 1], p = [X(L.T), Y(L.nt)]; if (!last || Math.hypot(p[0] - last[0], p[1] - last[1]) > 1.5) L.trail.push(p); if (L.trail.length > 300) L.trail.shift();
    }
    // demo: until someone plays, alternate a strong and a weak machine
    if (!L.touched && !L.held && L.clock > 0 && (!L.run || S.time - (L.t0 || 0) > 9)) { L.t0 = S.time; L.alt = !L.alt; L.alt ? launch(S, 6, 2e19) : launch(S, 9, 1.4e21); }
    if (!L.t0) L.t0 = S.time;
    // comet trail and the machine
    L.trail.forEach((p, i) => g.dot(p[0], p[1], 1 + 2.5 * (i / L.trail.length), c.ink, 0.12 + 0.5 * (i / L.trail.length)));
    const px = X(L.T), py = Y(L.nt), burning = L.msg === "burning on its own" || L.msg === "heating itself";
    g.glow(px, py, burning ? 46 + 6 * Math.sin(S.time * 5) : 22, burning ? c.photon : c.cool, burning ? 0.7 : 0.4);
    g.ball(px, py, 8, burning ? c.warm : c.cool); g.ring(px, py, 13, c.ink, 1.2, L.held ? 0.9 : 0.4);
    // readout: Q while held (heating needed), state when released
    const pa = pAlpha(L.T), need = (3 * NDEN * L.T * F().KEV) / (L.nt / NDEN) + pBrem(L.T) - pa;
    const Qs = need <= 0 ? WT.trf("Q = ∞: no heating needed") : "Q = " + WT.dec(((5 * pa) / need).toFixed((5 * pa) / need < 10 ? 2 : 0));
    g.label(WT.trf("{a} keV · nτ {b} · {c}", L.T.toFixed(1), sci(L.nt), L.held ? Qs : L.msg ? WT.trf(L.msg) : ""), W / 2, phone ? 14 : 24, { color: c.ink, size: phone ? 12 : 14, weight: 600, bg: true, raw: true });
    g.label(phone ? "drag or tap a point; it runs on its own" : "hold: heaters on (Q = fusion power / heating) · let go: heaters off, the plasma is on its own", W / 2, H - (phone ? 14 : 22), { color: c.faint, size: 11 });
  }
})();
