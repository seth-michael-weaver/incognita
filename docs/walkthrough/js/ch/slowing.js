/* Slowing down: a fission neutron (2 MeV) thermalised in water. Scenes (S.mode):
 *   "walk"  = one neutron entering water, bouncing off hydrogen (or oxygen): elastic scattering, isotropic in the centre of
 *             mass, with the target's own thermal motion (free gas at kT = 0.0253 eV, target velocity sampled from a Maxwellian
 *             and weighted by the relative speed). Beside it, energy against collision number on a log scale; the dashed line
 *             is ln E_n = ln E_0 - n xi with the average lethargy gain xi = 1 + alpha ln(alpha)/(1 - alpha),
 *             alpha = ((A-1)/(A+1))^2: xi = 1 for H, 0.120 for O. xi is also measured from the runs (collisions above 1 eV).
 *   "bound" = the same with chemical binding switchable. Below 1 eV a bound hydrogen recoils with its molecule (mass 18) or
 *             trades a quantum of the molecule's motion (libration ~0.06 eV, bend 0.205 eV, stretch 0.45 eV; gains weighted by
 *             the Boltzmann factor). The weights are illustrative; above 1 eV hydrogen scatters as a free atom either way.
 *   "map"   = a scattering law S(alpha, beta) (alpha = momentum transfer, beta = energy change, both in kT units).
 *             Free gas: S = exp(-(alpha + beta)^2 / 4 alpha) / sqrt(4 pi alpha), exact. Bound: an illustrative molecule
 *             (translation with mass 18 plus bands at the quanta above, detailed balance e^{-beta/2}) that turns into the
 *             free-atom ridge at large alpha. The outline is what a neutron of energy E can reach:
 *             beta >= -E/kT, (sqrt(E) - sqrt(E'))^2 <= alpha kT <= (sqrt(E) + sqrt(E'))^2 (A = 1).
 * INCOGNITA's own laws for H in H2O and Be metal: library/tsl-v0.1. */
(function () {
  const { TAU, clamp, lerp, smooth, rng } = WT.util;
  const KT = 0.0253, E0 = 2e6, ETH = 0.1, LG0 = -3, LG1 = 6.5;
  const log10 = (x) => Math.log(x) / Math.LN10;
  const xiOf = (A) => { if (A === 1) return 1; const a = ((A - 1) / (A + 1)) ** 2; return 1 + a * Math.log(a) / (1 - a); };
  const r = rng(29);
  const nrm = () => Math.sqrt(-2 * Math.log(1 - r())) * Math.cos(TAU * r());
  const unit = () => { const z = 2 * r() - 1, p = TAU * r(), s = Math.sqrt(1 - z * z); return [s * Math.cos(p), s * Math.sin(p), z]; };
  /** one elastic collision with a free nucleus of mass A (neutron masses) in a gas at kT. Units: E = v^2. */
  function freeGas(E, A) {
    const v = Math.sqrt(E), sV = Math.sqrt(KT / (2 * A)); let V = [0, 0, 0];
    for (let k = 0; k < 200; k++) { V = [nrm() * sV, nrm() * sV, nrm() * sV]; const rel = Math.hypot(v - V[0], V[1], V[2]), vv = Math.hypot(V[0], V[1], V[2]); if (r() * (v + vv) <= rel) break; }
    const ur = Math.hypot(v - V[0], V[1], V[2]), c = 1 / (1 + A), m = A * c * ur, o = unit();
    const vc = [(v + A * V[0]) * c, A * V[1] * c, A * V[2] * c];
    return (vc[0] + m * o[0]) ** 2 + (vc[1] + m * o[1]) ** 2 + (vc[2] + m * o[2]) ** 2;
  }
  const QUANTA = [[0.06, 1.0], [0.205, 0.35], [0.45, 0.5]];   // illustrative (eV, weight)
  function boundH(E) {
    const ch = [[0, 1.2]];
    for (const [q, w] of QUANTA) { if (E > q) ch.push([-q, w]); ch.push([q, w * Math.exp(-q / KT)]); }
    let s = 0; ch.forEach((x) => (s += x[1])); let u = r() * s, k = 0; while (k < ch.length - 1 && u > ch[k][1]) { u -= ch[k][1]; k++; }
    return { E: freeGas(Math.max(2e-4, E + ch[k][0]), 18), q: ch[k][0] };
  }

  // ---------- colours ----------
  const hexRGB = (h) => { const n = parseInt(h.replace("#", ""), 16); return [(n >> 16) & 255, (n >> 8) & 255, n & 255]; };
  const mix = (a, b, t) => { const p = hexRGB(a), q = hexRGB(b); return "#" + p.map((v, i) => Math.round(lerp(v, q[i], clamp(t, 0, 1))).toString(16).padStart(2, "0")).join(""); };
  const eCol = (c, E) => mix(c.neutron, c.warm, smooth(-1.6, 6.3, log10(E)));

  // ---------- water: molecules in the unit square ----------
  const MOL = []; { const q = rng(5); for (let i = 0; i < 46; i++) MOL.push({ x: 0.04 + 0.92 * q(), y: 0.08 + 0.84 * q(), a: q() * TAU, ph: q() * TAU, w: 0.6 + 0.8 * q(), hx: [q() - 0.5, q() - 0.5], hy: [q() - 0.5, q() - 0.5], k: [[0, 0], [0, 0], [0, 0]] }); }
  // relax so molecules do not overlap
  for (let it = 0; it < 30; it++) for (const m of MOL) for (const n of MOL) { if (m === n) continue; const dx = m.x - n.x, dy = m.y - n.y, d = Math.hypot(dx, dy); if (d < 0.11 && d > 1e-6) { const f = (0.11 - d) * 0.25; m.x = clamp(m.x + dx / d * f, 0.04, 0.96); m.y = clamp(m.y + dy / d * f, 0.08, 0.92); } }
  function atoms(S, bx, t) {
    const out = [], b = 1 - S.looseV, R = Math.min(bx.w, bx.h * 2.2) * 0.022;
    for (const m of MOL) {
      const ox = bx.x + (m.x + 0.006 * Math.sin(t * 0.7 * m.w + m.ph)) * bx.w, oy = bx.y + (m.y + 0.008 * Math.cos(t * 0.6 * m.w + m.ph)) * bx.h;
      const a = m.a + 0.25 * Math.sin(t * 1.3 * m.w + m.ph);
      out.push({ m, i: 0, el: "O", x: ox + m.k[0][0], y: oy + m.k[0][1] });
      for (let j = 0; j < 2; j++) {
        const ang = a + (j ? 0.91 : -0.91), d = R * 2.0, bxp = ox + Math.cos(ang) * d, byp = oy + Math.sin(ang) * d;
        const fxp = ox + (m.hx[j] * 2.6 + 0.7 * Math.sin(t * 0.9 * m.w + j * 2 + m.ph)) * R * 2.2, fyp = oy + (m.hy[j] * 2.6 + 0.7 * Math.cos(t * 0.8 * m.w + j * 3 + m.ph)) * R * 2.2;
        out.push({ m, i: j + 1, el: "H", ox, oy, x: lerp(fxp, bxp, b) + m.k[j + 1][0], y: lerp(fyp, byp, b) + m.k[j + 1][1] });
      }
    }
    return { list: out, R };
  }

  // ---------- one neutron's run ----------
  const run = { pts: [], E: E0, n: 0, nTh: -1, extra: 0, done: false, doneT: 0, path: [], u: 0, from: null, to: null, flash: [], A: 1, bind: 0 };
  const ghosts = [], xiAcc = { 1: [0, 0], 16: [0, 0] }, thAcc = { 1: [], 16: [] };
  /** one collision: the new energy (and the quantum traded, if any) */
  function collide(E, A, bind) { if (A === 1 && bind && E < 1) return boundH(E); return { E: freeGas(E, A), q: 0 }; }
  const nMaxOf = (A) => (A === 1 ? 40 : 230), extraOf = (A) => (A === 1 ? 10 : 24);
  /** a whole run computed at once (earlier neutrons, shown faint) */
  function simRun(A, bind) {
    let E = E0, n = 0, nTh = -1, extra = 0; const pts = [E0];
    while (n < nMaxOf(A) && extra < extraOf(A)) { const Eb = E; E = collide(E, A, bind).E; n++; pts.push(E); if (Eb > 1) { xiAcc[A][0] += Math.log(Eb / E); xiAcc[A][1]++; } if (nTh < 0 && E < ETH) { nTh = n; thAcc[A].push(n); } if (nTh >= 0) extra++; }
    return { A, bind, pts };
  }
  const snap = () => document.body.classList.contains("shot");
  function restart(S) {
    if (run.pts.length > 3 && run.done) { ghosts.push({ A: run.A, bind: run.bind, pts: run.pts.slice() }); }
    for (let i = ghosts.length - 1; i >= 0; i--) if (ghosts[i].A !== S.A || ghosts[i].bind !== S.bind) ghosts.splice(i, 1);
    while (ghosts.length < 3) ghosts.unshift(simRun(S.A, S.bind));
    while (ghosts.length > 6) ghosts.shift();
    Object.assign(run, { pts: [E0], E: E0, n: 0, nTh: -1, extra: 0, done: false, path: [[0, 0.5, E0]], u: 0, from: [0, 0.5], to: null, flash: [], A: S.A, bind: S.bind });
    if (snap()) { const s = simRun(S.A, S.bind); run.pts = s.pts; run.n = s.pts.length - 1; run.E = s.pts[run.n]; run.done = true; run.doneT = 1e9; run.path = [[0, 0.5, E0], [0.3, 0.3, 1e4], [0.55, 0.7, 10], [0.7, 0.45, 0.03]]; run.from = [0.7, 0.45]; }
  }
  function nextTarget(S, at) {
    const [x, y] = run.from; let best = null, bd = Infinity;
    const ang = run.n === 0 ? (r() - 0.5) * 0.5 : r() * TAU, len = (0.1 + 0.16 * -Math.log(1 - r() * 0.9)) * (run.n === 0 ? 1.6 : 1);
    let tx = x + Math.cos(ang) * len * 0.62, ty = y + Math.sin(ang) * len;
    tx = tx < 0.03 ? 0.06 - tx : tx > 0.97 ? 1.94 - tx : tx; ty = ty < 0.08 ? 0.16 - ty : ty > 0.92 ? 1.84 - ty : ty;
    for (const a of at.list) { if (a.el !== (run.A === 1 ? "H" : "O")) continue; const d = Math.hypot(a.m.x - tx, a.m.y - ty); if (d < bd && !(run.to && run.to.m === a.m && run.to.i === a.i)) { bd = d; best = a; } }
    run.to = { m: best.m, i: best.i };
  }

  WT.chapter("slowing", {
    num: "Chapter 13", title: "Slowing down", short: "Slowing down",
    html: `
<div class="step">
  <p>Each bounce off hydrogen costs about half the energy.</p>
  <div class="btns"><button class="btn ghost" data-act="tgtH" aria-pressed="true">Hydrogen</button><button class="btn ghost" data-act="tgtO" aria-pressed="false">Oxygen</button><button class="btn" data-act="again">Fire again</button></div>
</div>
<div class="step">
  <p>Below about 1 eV, the molecule's bonds shape each bounce.</p>
  <div class="btns"><button class="btn ghost" data-act="bind" aria-pressed="true">Chemical binding</button><button class="btn" data-act="again">Fire again</button></div>
</div>
<div class="step">
  <p>INCOGNITA's own laws for water and beryllium: <a href="https://github.com/seth-michael-weaver/incognita/tree/main/library/tsl-v0.1" style="white-space:nowrap">tsl-v0.1</a>.</p>
  <div class="ctl"><label for="slo-e">Neutron energy (eV)</label><input id="slo-e" type="range" data-bind="lgE" data-instant min="-2.3" max="0" step="0.01" value="-1"><output data-show="Eshow" data-fmt="3"></output></div>
  <div class="btns"><button class="btn ghost" data-act="bind" aria-pressed="true">Chemical binding</button></div>
</div>`,
    setup(S) {
      S.set("mode", "walk"); S.set("A", 1); S.set("bind", 0); S.to("bindV", 0, true); S.to("looseV", 0, true); S.set("lgE", -1); S.Eshow = 0.1;
      const press = (act, on) => document.querySelectorAll(`#slowing [data-act="${act}"]`).forEach((b) => b.setAttribute("aria-pressed", String(on)));
      S.press = press;
      S.on("tgtH", () => { S.set("A", 1); press("tgtH", true); press("tgtO", false); restart(S); });
      S.on("tgtO", () => { S.set("A", 16); S.set("bind", 0); S.to("bindV", 0); press("tgtH", false); press("tgtO", true); restart(S); });
      S.on("again", () => restart(S));
      S.on("bind", () => { const on = !S.bind; S.set("bind", on ? 1 : 0); S.to("bindV", on ? 1 : 0); S.to("looseV", on || S.mode !== "bound" ? 0 : 1); press("bind", on); if (S.mode !== "map") { if (S.A !== 1) { S.set("A", 1); press("tgtH", true); press("tgtO", false); } restart(S); } });
      restart(S);
    },
    steps: [
      (S) => { S.set("mode", "walk"); S.set("bind", 0); S.to("bindV", 0); S.to("looseV", 0); S.press("bind", false); if (run.bind || snap()) restart(S); },
      (S) => { S.set("mode", "bound"); S.to("looseV", 0); if (S.A !== 1 || !S.bind) { S.set("A", 1); S.set("bind", 1); S.to("bindV", 1); S.press("tgtH", true); S.press("tgtO", false); S.press("bind", true); restart(S); } else if (snap()) restart(S); },
      (S) => { S.set("mode", "map"); S.press("bind", !!S.bind); },
    ],
    frame(g, S, dt) {
      if (S.mode === "map") sceneMap(g, S);
      else sceneWalk(g, S, dt);
      tag(g);
    },
  });

  const tag = (g) => g.label("illustration", g.W - 6, g.H - 10, { color: g.c.faint, size: 10, align: "right" });

  // ---------- scene: the walk and its energy trace ----------
  function sceneWalk(g, S, dt) {
    const { W, H, c, ctx } = g, phone = W < 600, fs = phone ? 11 : 13;
    const bx = { x: W * 0.04, y: H * 0.07, w: W * 0.92, h: H * (phone ? 0.36 : 0.38) };
    const at = atoms(S, bx, S.time), Rr = clamp(at.R, 2.6, 7.5);
    // the water: a lit pool whose edges fade into the page
    ctx.save(); const gr = ctx.createLinearGradient(0, bx.y, 0, bx.y + bx.h); gr.addColorStop(0, g.rgba(c.cool, 0.03)); gr.addColorStop(0.5, g.rgba(c.cool, 0.11)); gr.addColorStop(1, g.rgba(c.cool, 0.03));
    ctx.fillStyle = gr; if (ctx.roundRect) { ctx.beginPath(); ctx.roundRect(bx.x, bx.y, bx.w, bx.h, 18); ctx.fill(); } else ctx.fillRect(bx.x, bx.y, bx.w, bx.h); ctx.restore();
    g.label(S.A === 1 ? "water · neutron hits hydrogen" : "water · neutron hits oxygen", bx.x + 10, bx.y + 12, { color: c.cool, size: fs - 1, align: "left", weight: 600 });
    // bonds, then atoms
    const bOn = 1 - S.looseV, hCol = mix(c.faint, c.card, 0.3);
    if (bOn > 0.02) for (const a of at.list) if (a.el === "H") g.line(a.ox, a.oy, a.x, a.y, S.bindV > 0.5 ? c.photon : c.soft, 1.6, (0.35 + 0.35 * S.bindV) * bOn);
    for (const a of at.list) {
      const hot = run.to && run.to.m === a.m && run.to.i === a.i;
      if (a.el === "O") g.ball(a.x, a.y, Rr * 1.25, c.proton, S.A === 16 ? 1 : 0.75);
      else g.ball(a.x, a.y, Rr * 0.8, hCol, S.A === 1 ? 1 : 0.7);
      if (hot && !run.done) g.ring(a.x, a.y, Rr * (a.el === "O" ? 1.9 : 1.5), c.ink, 1, 0.35);
    }
    // decay recoil kicks
    for (const m of MOL) for (const k of m.k) { k[0] *= Math.exp(-3 * dt); k[1] *= Math.exp(-3 * dt); }
    // advance the neutron
    const xi = xiOf(S.A), nExp = Math.log(E0 / ETH) / xi, stepT = clamp(6.5 / nExp, 0.045, 0.34);
    const P = (p) => [bx.x + p[0] * bx.w, bx.y + p[1] * bx.h];
    if (!run.done) {
      if (!run.to) nextTarget(S, at);
      run.u += dt / stepT;
      if (run.u >= 1) {
        run.u = 0; const tgt = at.list.find((a) => a.m === run.to.m && a.i === run.to.i);
        const Eb = run.E, o = collide(Eb, S.A, run.bind), Ea = o.E, q = o.q;
        if (Eb > 1) { const acc = xiAcc[S.A]; acc[0] += Math.log(Eb / Ea); acc[1]++; }
        run.E = Ea; run.n++; run.pts.push(Ea);
        const p = [(tgt.x - bx.x) / bx.w, (tgt.y - bx.y) / bx.h]; run.from = p; run.path.push([p[0], p[1], Ea]); if (run.path.length > 16) run.path.shift();
        run.flash.push({ x: tgt.x, y: tgt.y, t: S.time, q });
        // the struck atom recoils: harder when the neutron was fast and the atom light
        const kick = Math.min(Rr * 2.4, Rr * 0.5 * Math.sqrt(Math.max(0, Eb - Ea) / Math.max(Eb, 1e-6)) * (S.A === 1 ? 4 : 2) + 0.6), ang = r() * TAU;
        tgt.m.k[tgt.i][0] += Math.cos(ang) * kick; tgt.m.k[tgt.i][1] += Math.sin(ang) * kick;
        if (run.nTh < 0 && Ea < ETH) { run.nTh = run.n; thAcc[S.A].push(run.n); if (thAcc[S.A].length > 60) thAcc[S.A].shift(); }
        if (run.nTh >= 0) run.extra++;
        if (run.extra >= extraOf(S.A) || run.n >= nMaxOf(S.A)) { run.done = true; run.doneT = S.time; }
        else nextTarget(S, at);
      }
    } else if (S.time - run.doneT > 2.2) restart(S);
    // trail and neutron
    const pts = run.path.map((p) => [...P(p), p[2]]);
    let head = null;
    if (!run.done && run.to) { const tgt = at.list.find((a) => a.m === run.to.m && a.i === run.to.i), a0 = P(run.from); head = [lerp(a0[0], tgt.x, run.u), lerp(a0[1], tgt.y, run.u)]; }
    const tr = head ? pts.concat([[head[0], head[1], run.E]]) : pts;
    for (let i = 1; i < tr.length; i++) g.line(tr[i - 1][0], tr[i - 1][1], tr[i][0], tr[i][1], eCol(c, tr[i - 1][2] > 0 ? tr[i][2] : tr[i][2]), 2, 0.12 + 0.6 * (i / tr.length));
    for (let i = run.flash.length - 1; i >= 0; i--) { const f = run.flash[i], a = S.time - f.t; if (a > 0.7) { run.flash.splice(i, 1); continue; } g.glow(f.x, f.y, 10 + 30 * a, f.q < 0 ? c.photon : c.warm, 0.55 * (1 - a / 0.7)); }
    const hp = head || (pts.length ? pts[pts.length - 1] : null);
    if (hp) { const col = eCol(c, run.E), al = run.done ? 1 - smooth(0, 1.6, S.time - run.doneT) : 1; g.glow(hp[0], hp[1], 16, col, 0.45 * al); g.ball(hp[0], hp[1], Math.max(4, Rr * 0.95), col, al); }
    if (run.n === 0 && head) g.label("2 MeV neutron →", Math.max(bx.x + 70, head[0]), head[1] - 16, { color: c.warm, size: fs - 1, weight: 600, bg: true });

    // ---------- the energy trace ----------
    const tx0 = W * (phone ? 0.14 : 0.11), tx1 = W * 0.96, ty0 = H * (phone ? 0.5 : 0.52), ty1 = H * (phone ? 0.84 : 0.85);
    const nMax = S.A === 1 ? 40 : 230, X = (n) => tx0 + (tx1 - tx0) * n / nMax, Y = (E) => lerp(ty1, ty0, (log10(clamp(E, 10 ** LG0, 10 ** LG1)) - LG0) / (LG1 - LG0));
    // binding region and thermal band
    if (S.bindV > 0.02 && S.A === 1) { ctx.save(); ctx.fillStyle = g.rgba(c.photon, 0.08 * S.bindV); ctx.fillRect(tx0, Y(1), tx1 - tx0, ty1 - Y(1)); ctx.restore(); g.label("bonds matter", tx1 - 4, Y(1) + 11, { color: c.photon, size: fs - 2, align: "right", alpha: S.bindV }); }
    ctx.save(); const tb = ctx.createLinearGradient(0, Y(0.1), 0, Y(0.006)); tb.addColorStop(0, g.rgba(c.neutron, 0)); tb.addColorStop(0.5, g.rgba(c.neutron, 0.16)); tb.addColorStop(1, g.rgba(c.neutron, 0)); ctx.fillStyle = tb; ctx.fillRect(tx0, Y(0.1), tx1 - tx0, Y(0.006) - Y(0.1)); ctx.restore();
    g.line(tx0, Y(KT), tx1, Y(KT), c.neutron, 1.2, 0.7, [4, 4]);
    g.label("thermal · kT ≈ 0.025 eV", tx1 - 4, Y(KT) - 10, { color: c.neutron, size: fs - 1, align: "right", weight: 600, bg: true });
    g.line(tx0, ty0, tx0, ty1, c.line, 1); g.line(tx0, ty1, tx1, ty1, c.line, 1);
    [[1e6, "1 MeV"], [1e3, "1 keV"], [1, "1 eV"], [1e-3, "1 meV"]].forEach(([e, s]) => { g.line(tx0 - 4, Y(e), tx0, Y(e), c.faint, 1); g.label(s, tx0 - 7, Y(e), { color: c.faint, size: fs - 2, align: "right" }); });
    const nt = S.A === 1 ? [0, 10, 20, 30, 40] : [0, 50, 100, 150, 200];
    nt.forEach((n) => g.label(String(n), X(n), ty1 + 12, { color: c.faint, size: fs - 2 }));
    g.label("collisions →", tx1, ty1 + 27, { color: c.soft, size: fs - 1, align: "right" });
    g.label("energy", tx0, ty0 - 12, { color: c.soft, size: fs - 1, align: phone ? "left" : "center" });
    // expected: ln E drops by xi per collision
    const ex = []; for (let n = 0; n <= nExp + 0.01; n += nExp / 40) ex.push([X(n), Y(E0 * Math.exp(-n * xi))]);
    g.poly(ex, c.soft, 1.4, 0.7, [5, 5]);
    // ghosts of earlier runs, then this run
    for (const gh of ghosts) g.poly(gh.pts.map((e, i) => [X(i), Y(e)]), c.soft, 1.2, 0.22);
    const cur = run.pts.map((e, i) => [X(i), Y(e)]);
    if (cur.length > 1) { for (let i = 1; i < cur.length; i++) g.line(cur[i - 1][0], cur[i - 1][1], cur[i][0], cur[i][1], eCol(c, run.pts[i]), 2.2, 1); }
    cur.forEach((p, i) => g.dot(p[0], p[1], S.A === 1 ? 3 : 1.8, eCol(c, run.pts[i])));
    // readouts
    const acc = xiAcc[S.A], xiM = acc[1] ? acc[0] / acc[1] : null, th = thAcc[S.A], thM = th.length ? th.reduce((a, b) => a + b, 0) / th.length : null;
    const ry = H * (phone ? 0.95 : 0.94);
    g.label(`ξ per collision: ${xiM === null ? "…" : xiM.toFixed(2)}  (theory ${xi.toFixed(xi === 1 ? 2 : 3)})${thM ? ` · ${thM.toFixed(0)} collisions to thermal` : ""}`, W * 0.5, ry, { color: c.ink, size: fs + 1, weight: 600, serif: true });
    if (!phone) g.label("ξ: average loss in ln E", W * 0.5, ry - fs - 9, { color: c.soft, size: fs - 1 });
  }

  // ---------- scene: the scattering law S(alpha, beta) ----------
  const AM = 30, B0 = -30, B1 = 8;
  const sFree = (a, b, M) => { const am = a / M; return Math.exp(-((am + b) ** 2) / (4 * am)) / Math.sqrt(4 * Math.PI * am); };
  const gauss = (d, w) => Math.exp(-(d * d) / (2 * w * w)) / (w * 2.5066);
  const BANDS = [[0.06, 1.0, 0.8], [0.205, 0.35, 0.45], [0.45, 0.5, 0.6]];   // illustrative: quantum (eV), weight, width (kT)
  function sBound(a, b) {
    // illustrative molecule: translation with mass 18, plus one-quantum loss (beta = -e) and gain (beta = +e, Boltzmann e^-e)
    const dw = Math.exp(-a * 0.045); let s = 0.6 * dw * sFree(a, b, 18);
    for (const [eV, w, wd] of BANDS) { const e = eV / KT, amp = dw * w * a / e / (1 - Math.exp(-e)); s += amp * gauss(b + e, wd) + amp * Math.exp(-e) * gauss(b - e, wd); }
    return lerp(s, sFree(a, b, 1), smooth(6, 28, a));
  }
  let mapCache = null;
  function mapImage(g, bind, w, h) {
    const cv = document.createElement("canvas"); cv.width = w; cv.height = h; const cx = cv.getContext("2d"), im = cx.createImageData(w, h), c = g.c;
    const lo = hexRGB(c.paper), mid = hexRGB(c.neutron), hi = hexRGB(c.photon);
    for (let j = 0; j < h; j++) for (let i = 0; i < w; i++) {
      const a = Math.max(0.05, (i + 0.5) / w * AM), b = B1 - (j + 0.5) / h * (B1 - B0), s = bind ? sBound(a, b) : sFree(a, b, 1);
      const v = clamp((log10(Math.max(s, 1e-12)) + 3.2) / 3, 0, 1) ** 1.2, k = 4 * (j * w + i);
      const col = v < 0.6 ? lo.map((x, q) => lerp(x, mid[q], v / 0.6)) : mid.map((x, q) => lerp(x, hi[q], (v - 0.6) / 0.4));
      im.data[k] = col[0]; im.data[k + 1] = col[1]; im.data[k + 2] = col[2]; im.data[k + 3] = 255;
    }
    cx.putImageData(im, 0, 0); return cv;
  }
  function sceneMap(g, S) {
    const { W, H, c, ctx } = g, phone = W < 600, fs = phone ? 11 : 13;
    const x0 = W * (phone ? 0.14 : 0.12), x1 = W * 0.95, y0 = H * 0.1, y1 = H * (phone ? 0.78 : 0.8);
    const key = c.paper + c.neutron;
    if (!mapCache || mapCache.key !== key) mapCache = { key, free: mapImage(g, false, 150, 110), bound: mapImage(g, true, 150, 110) };
    const XA = (a) => x0 + (x1 - x0) * a / AM, YB = (b) => y0 + (y1 - y0) * (B1 - b) / (B1 - B0);
    ctx.save(); ctx.imageSmoothingEnabled = true;
    ctx.globalAlpha = 1; ctx.drawImage(mapCache.free, x0, y0, x1 - x0, y1 - y0);
    if (S.bindV > 0.01) { ctx.globalAlpha = S.bindV; ctx.drawImage(mapCache.bound, x0, y0, x1 - x0, y1 - y0); }
    ctx.restore();
    // reachable region for a neutron of energy E (A = 1)
    const E = Math.pow(10, S.lgE), eps = E / KT; S.Eshow = E;
    const up = [], dn = [];
    for (let i = 0; i <= 120; i++) { const b = -eps + (Math.min(B1, 60) + eps) * i / 120; if (b > B1) break; const e2 = eps + b; const am = (Math.sqrt(eps) - Math.sqrt(e2)) ** 2, ap = (Math.sqrt(eps) + Math.sqrt(e2)) ** 2; dn.push([XA(Math.min(am, AM)), YB(Math.max(b, B0))]); up.push([XA(Math.min(ap, AM)), YB(Math.max(b, B0))]); }
    g.clip(x0, y0, x1 - x0, y1 - y0);
    g.area(dn.concat(up.reverse()), c.ink, 0.06); g.poly(dn, c.ink, 2, 0.9); g.poly(up, c.ink, 2, 0.9);
    if (eps < -B0) g.line(x0, YB(-eps), x1, YB(-eps), c.ink, 1, 0.45, [3, 4]);
    g.ctx.restore();
    // free-atom recoil line beta = -alpha
    g.line(XA(0), YB(0), XA(Math.min(AM, -B0)), YB(-Math.min(AM, -B0)), c.ink, 1, 0.35, [2, 5]);
    g.label("free-atom recoil", XA(Math.min(AM, -B0) * 0.72), YB(-Math.min(AM, -B0) * 0.72) + 14, { color: c.soft, size: fs - 2, align: "left", bg: true });
    g.line(x0, YB(0), x1, YB(0), c.soft, 1, 0.35);
    // axes
    g.line(x0, y1, x1, y1, c.line, 1); g.line(x0, y0, x0, y1, c.line, 1);
    [0, 10, 20, 30].forEach((a) => g.label(String(a), XA(a), y1 + 12, { color: c.faint, size: fs - 2 }));
    [-30, -20, -10, 0].forEach((b) => g.label(String(b).replace("-", "−"), x0 - 6, YB(b), { color: c.faint, size: fs - 2, align: "right" }));
    g.label("momentum transfer α →", x1, y1 + 28, { color: c.soft, size: fs - 1, align: "right" });
    g.label(phone ? "energy change β (kT)" : "energy change β (units of kT)", x0, y0 - 12, { color: c.soft, size: fs - 1, align: "left" });
    g.label("gain ↑", x1 - 4, YB(0) - 10, { color: c.faint, size: fs - 2, align: "right" }); g.label("loss ↓", x1 - 4, YB(0) + 12, { color: c.faint, size: fs - 2, align: "right" });
    g.label(`outline: reachable from ${E < 0.1 ? (1000 * E).toFixed(0) + " meV" : E.toFixed(2) + " eV"}`, x1 - 6, YB(B1) + 16, { color: c.ink, size: fs, weight: 600, bg: true, align: "right" });
    g.label(S.bind ? "scattering law S(α,β) · hydrogen bound in water" : "scattering law S(α,β) · free hydrogen gas", W * 0.5, H * (phone ? 0.9 : 0.9), { color: c.ink, size: fs + 1, weight: 600, serif: true });
  }
})();
