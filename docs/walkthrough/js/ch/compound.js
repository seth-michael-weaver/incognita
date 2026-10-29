/* Chapter 8: the compound nucleus and its level density (density/).
 * Scenes (S.mode): "bohr"   = a neutron hits, the heat spreads until the nucleus forgets where it was hit;
 *                   "ladder" = the ladder of levels, with a 1-MeV magnifier whose rungs multiply as energy rises;
 *                   "join"   = terrain: counted rungs, a constant-temperature plank, a Fermi-gas hillside, one joint;
 *                   "shell"  = two single-particle level schemes heated until nucleons hop; a(U) needles converge on a~;
 *                   "spin"   = states sorted into drawers by spin J (solid + parity, hollow -), collective enhancement;
 *                   "bins"   = the continuum chopped into drawers; dots collapse into counted blocks, a cascade drops.
 * Shapes follow density/models.py (gilcam, fermi), density/parameters.py (ignatyuk, spincut, spindis, colenhance),
 * density/matching.py and core/grids.py (exgrid). Numbers are illustrative for A = 56 (a~ = 8 MeV^-1). */
(function () {
  const { TAU, clamp, lerp, smooth, rng } = WT.util;
  const A = 56, ATILDE = 8.0, DELTA = 3.2, GAM = 0.433 / Math.cbrt(A);
  // a mock even-even level scheme (MeV), roughly iron-like: the "counted" levels
  const LEVELS = [0, 0.85, 2.09, 2.66, 2.94, 3.12, 3.37, 3.45, 3.60, 3.76, 3.83, 3.86, 4.05, 4.12, 4.30, 4.40, 4.46, 4.51, 4.61, 4.68, 4.73, 4.80];
  const NLOW = 2, NTOP = 20, ELAST = LEVELS[LEVELS.length - 1];

  function aOfU(U, dW) { if (U <= 0) return Math.max(1, ATILDE * (1 + dW * GAM)); return Math.max(1, ATILDE * (1 + dW * (1 - Math.exp(-GAM * U)) / U)); }
  function sig2(U, a) { return Math.max(2.5, 0.01389 * Math.pow(A, 5 / 3) * Math.sqrt(Math.max(U, 0.05) / a)); }
  /** Fermi-gas total level density per MeV (fermi.f90 shape). */
  function rhoFG(E, dW = 0) { const U = E - DELTA; if (U <= 0.05) return 1; const a = aOfU(U, dW); const s = Math.sqrt(sig2(U, a)); return Math.exp(2 * Math.sqrt(a * U)) / (12 * Math.SQRT2 * s * Math.pow(a, 0.25) * Math.pow(U, 1.25)); }
  function lnRhoFG(E, dW = 0) { return Math.log(rhoFG(E, dW)); }
  /** Constant-temperature law tangent to the Fermi gas at Ex: T = 1 / slope, E0 from equal value. */
  function ctAt(Ex) { const h = 0.02, slope = (lnRhoFG(Ex + h) - lnRhoFG(Ex - h)) / (2 * h); const T = 1 / Math.max(slope, 0.05); const E0 = Ex - T * Math.log(T * rhoFG(Ex)); return { T, E0 }; }
  function rhoCT(E, ct) { return Math.exp((E - ct.E0) / ct.T) / ct.T; }
  function ctCount(ct, E1, E2) { return Math.exp((E2 - ct.E0) / ct.T) - Math.exp((E1 - ct.E0) / ct.T); }
  // the matching energy the engine would pick: the CT law tangent there reproduces counted levels NLOW..NTOP
  const WANT = NTOP - NLOW;
  const EXSTAR = (() => { let a = 4.5, b = 12; for (let i = 0; i < 50; i++) { const m = 0.5 * (a + b); if (ctCount(ctAt(m), LEVELS[NLOW], LEVELS[NTOP]) < WANT) a = m; else b = m; } return 0.5 * (a + b); })();
  const CTSTAR = ctAt(EXSTAR);
  function rhoGC(E) { return E > EXSTAR ? rhoFG(E) : rhoCT(E, CTSTAR); }
  function fmtRho(r) { if (r < 10) return r.toFixed(1); if (r < 1000) return Math.round(r).toString(); if (r < 1e6) return (r / 1000).toFixed(r < 1e4 ? 1 : 0) + " thousand"; if (r < 1e9) return (r / 1e6).toFixed(1) + " million"; return (r / 1e9).toFixed(1) + " billion"; }
  function fmtShort(r) { if (r < 10) return r.toFixed(1); if (r < 1000) return Math.round(r).toString(); if (r < 1e6) return (r / 1000).toFixed(r < 1e4 ? 1 : 0) + "k"; if (r < 1e9) return (r / 1e6).toFixed(r < 1e7 ? 1 : 0) + "M"; return (r / 1e9).toFixed(1) + "B"; }
  const SHOT = /[?&]shot=/.test(location.search);
  const hash = (k) => { const s = Math.sin(k * 127.1 + 311.7) * 43758.5453; return s - Math.floor(s); };

  // cumulative number of levels N(E): counted levels below ELAST, the integral of rho above (fine table, interpolated)
  const CUM_DE = 0.002, CUM_E1 = 21.5, CUM = (() => { const n = Math.ceil((CUM_E1 - ELAST) / CUM_DE) + 1, t = new Float64Array(n); t[0] = LEVELS.length; for (let i = 1; i < n; i++) { const e = ELAST + (i - 0.5) * CUM_DE; t[i] = t[i - 1] + rhoGC(e) * CUM_DE; } return t; })();
  function cumN(E) { if (E <= ELAST) { let n = 0; for (const l of LEVELS) if (l <= E) n++; return n; } const x = (E - ELAST) / CUM_DE, i = Math.min(CUM.length - 2, Math.floor(x)); return lerp(CUM[i], CUM[i + 1], x - i); }
  function energyOfN(k) { let lo = 0, hi = CUM.length - 1; while (hi - lo > 1) { const m = (lo + hi) >> 1; if (CUM[m] < k) lo = m; else hi = m; } return ELAST + (lo + (k - CUM[lo]) / Math.max(1e-12, CUM[hi] - CUM[lo])) * CUM_DE; }

  // packed nucleons (same spiral as the kit, kept here so each ball can carry its own heat)
  function pack(N, seed) { const r = rng(seed); const p = []; for (let i = 0; i < N; i++) { const a = i * 2.39996 + r() * 0.3, rr = Math.sqrt((i + 0.5) / N) * 0.86; p.push({ x: rr * Math.cos(a), y: rr * Math.sin(a), ph: r(), p: false }); } const idx = p.map((_, i) => i); for (let i = N - 1; i > 0; i--) { const j = Math.floor(r() * (i + 1)); [idx[i], idx[j]] = [idx[j], idx[i]]; } idx.slice(0, Math.round(N * 0.46)).forEach((i) => (p[i].p = true)); return p; }
  const NUC = pack(56, 11), NUC_ORDER = NUC.map((p, i) => i).sort((a, b) => NUC[a].ph - NUC[b].ph);

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

  // ---------- shell scene: two single-particle schemes (energies in MeV, two nucleons per level) ----------
  const SCHEMES = [
    { name: "closed shell", dW: -3, levels: [...Array(8).keys(), ...Array.from({ length: 30 }, (_, k) => 11 + k)], np: 16, vis: [4, 5, 6, 7, 8, 9, 10] },
    { name: "mid-shell", dW: 2.5, levels: Array.from({ length: 38 }, (_, k) => k), np: 17, vis: [4, 5, 6, 7, 8, 9, 10, 11, 12, 13] },
  ];
  /** Number of ways to place np nucleons (2 per level) with each integer excitation 0..UMAX (exact count). */
  function configCounts(levels, np, UMAX) {
    let eg = 0, left = np; for (const e of levels) { const k = Math.min(2, left); eg += k * e; left -= k; }
    const NB = eg + UMAX + 1; let dp = []; for (let n = 0; n <= np; n++) dp.push(new Float64Array(NB)); dp[0][0] = 1;
    const C = [1, 2, 1];
    for (const e of levels) {
      const nd = []; for (let n = 0; n <= np; n++) nd.push(new Float64Array(NB));
      for (let n = 0; n <= np; n++) for (let b = 0; b < NB; b++) { const v = dp[n][b]; if (!v) continue; for (let k = 0; k <= 2 && n + k <= np; k++) { const bb = b + k * e; if (bb < NB) nd[n + k][bb] += v * C[k]; } }
      dp = nd;
    }
    const out = new Float64Array(UMAX + 1); for (let u = 0; u <= UMAX; u++) out[u] = dp[np][eg + u]; return out;
  }
  SCHEMES.forEach((s) => {
    s.ways = configCounts(s.levels, s.np, 42);
    // the visible window: which slots start filled (ground configuration)
    const occ = []; let left = s.np; s.levels.forEach((e, i) => { const k = Math.min(2, left); left -= k; if (s.vis.includes(i)) { occ.push(k >= 1, k >= 2); } });
    s.slots = []; s.vis.forEach((li, j) => { s.slots.push({ li, e: s.levels[li], side: -1 }, { li, e: s.levels[li], side: 1 }); });
    s.balls = []; occ.forEach((o, si) => { if (o) s.balls.push({ slot: si, from: si, t0: -10 }); });
    s.acc = 0; s.rand = rng(s.dW + 50);
  });
  function waysAt(s, U) { const u = clamp(U, 0, 41.99), i = Math.floor(u), f = u - i; const a = Math.log(1 + s.ways[i]), b = Math.log(1 + s.ways[i + 1]); return Math.exp(lerp(a, b, f)) - 1; }

  // ---------- spin drawers ----------
  const NJ = 11; const drawers = Array.from({ length: NJ }, () => []); let spinRand = rng(77), spinSpawnAcc = 0, churnAcc = 0;

  // ---------- bins scene state ----------
  const NBD = 10; let casc = { t0: 0, path: [] };

  WT.chapter("compound", {
    num: "Chapter 8", title: "The compound nucleus", short: "Compound nucleus",
    lead: "Once the first fast collisions are over, all the nucleons share the energy. This settled state is the compound nucleus. To predict what it does next, the engine needs to know how many ways it can hold its energy.",
    html: `
<div class="step">
  <p>A neutron strikes one side of a nucleus. Its energy, plus the energy released by its capture, starts as a hot spot (the orange glow); collisions pass it on, and within about 10⁻²¹ seconds every nucleon carries a share.</p>
  <div class="btns"><button class="btn" data-act="hit">Hit from another side</button></div>
  <p>Press the button to send the neutron in from another side. The glow always ends the same: the nucleus has <b>forgotten how it was formed</b>. This is Bohr's compound nucleus. From here on only three facts matter: its energy, its spin (how much it rotates) and its parity (a + or − label for its mirror symmetry).</p>
</div>
<div class="step">
  <h3>From discrete levels to the continuum</h3>
  <p>The ladder on the left holds the states of the nucleus, energy rising upward; the window on the right magnifies a 1-MeV slice around the orange ball. Near the bottom the rungs are far apart, and each one has been measured. Higher up, the ways to share the energy among 56 nucleons multiply until the rungs blur into a solid band, the continuum.</p>
  <div class="ctl"><label for="cn-e">Excitation energy</label><input id="cn-e" type="range" data-bind="E" min="0" max="20" step="0.1" value="6.5"><output data-show="E" data-fmt="1"></output></div>
  <p>Drag the excitation energy (the energy held above the lowest state, in MeV) and watch the window. The <b>level density</b> ρ, states per MeV, grows roughly as e<sup>2√(aE)</sup>, where <i>a</i> sets each nucleus's pace: a few per MeV at 3 MeV, hundreds near 8 MeV (where a neutron could escape), millions by 20 MeV. Up there the engine works with ρ itself.</p>
</div>
<div class="step">
  <h3>The composite level density</h3>
  <p>The terrain's height is the level density on a log scale, with energy to the right. Bottom left stand the counted levels. The straight plank is the <b>constant-temperature</b> law: ρ multiplies by e (about 2.7) every <i>T</i> MeV, where <i>T</i> is the nuclear temperature. The hillside is the <b>Fermi gas</b>, which treats the nucleons as independent particles. Except for the heaviest targets, where it reads tabulated densities, the engine uses this pair by default.</p>
  <div class="ctl"><label for="cn-ex">Matching energy</label><input id="cn-ex" type="range" data-bind="Ex" min="4.5" max="12" step="0.05" value="6"><output data-show="Ex" data-fmt="1"></output></div>
  <p>Drag the matching energy: the joint slides along the hill, and the plank pivots to meet it with the same height and slope. The two stacks below compare the levels the plank predicts with those actually counted. Only one joint makes them equal; there the plank turns green. That is the energy the engine picks.</p>
</div>
<div class="step">
  <h3>Shell effects and their damping</h3>
  <p>Single-nucleon levels, two nucleons each, for two nuclei. Left, a closed shell: everything below a big gap is full, so any move pays for the whole gap. Right, a mid-shell nucleus with a half-full top level, so cheap moves exist at once. Each counter shows how many arrangements hold the given heat.</p>
  <div class="ctl"><label for="cn-u">Heat (excitation)</label><input id="cn-u" type="range" data-bind="U" min="0" max="40" step="0.5" value="3"><output data-show="U" data-fmt="1"></output></div>
  <p>Drag the heat up and watch nucleons hop. At low heat the closed shell is starved of arrangements; with enough heat the gap stops mattering and both counts grow alike. The engine sums this up in one number per nucleus, the <b>level-density parameter</b> <i>a</i>: the bigger <i>a</i>, the faster the count of arrangements grows with heat. The needles show it for each nucleus: they start apart and, over about 10 MeV, both settle on the same smooth value (written <i>ã</i>, "a-tilde"), the one a nucleus with no shell gaps would have.</p>
  <p>So the engine starts each nucleus with its shell effect, the extra energy its gaps are worth (written δW), and lets that effect fade as the heat rises.</p>
  <div class="aside">The formula: <i>a</i>(<i>U</i>) = <i>ã</i> · [1 + δW · (1 − e<sup>−γ<i>U</i></sup>) / <i>U</i>], with <i>U</i> the heat and γ (gamma, about 0.1 per MeV here, less in heavier nuclei) how quickly the shell effect fades.</div>
</div>
<div class="step">
  <h3>Spin and parity distributions</h3>
  <p>The states at one energy fall into drawers by spin <i>J</i>, the nucleus's angular momentum: solid tokens for + parity, hollow for −. The middle drawers fill most, following (2<i>J</i>+1) e<sup>−(J+½)²/2σ²</sup>, where the spin cutoff σ sets the spread. The two parities come out about equal.</p>
  <div class="ctl"><label for="cn-u2">Excitation</label><input id="cn-u2" type="range" data-bind="U2" min="1" max="30" step="0.5" value="8"><output data-show="U2" data-fmt="1"></output></div>
  <div class="btns"><button class="btn ghost" data-act="deform">Deform the nucleus</button></div>
  <p>Drag the excitation up: σ grows, since a hotter nucleus can carry more spin. Then press Deform. A football-shaped nucleus can also rotate as a whole, so every drawer gains states (the blue tokens): the <b>collective enhancement</b>. By default the engine adds it only for targets heavier than about 215 nucleons.</p>
</div>
<div class="step">
  <h3>Energy bins in the continuum</h3>
  <p>Above the last counted level the engine cuts the continuum into slices of equal energy width, called bins. In each bin the dots collapse into one block of ρ·ΔE states (ΔE is the bin width), sorted by spin and parity as above.</p>
  <div class="ctl"><label for="cn-emax">Top of the ladder</label><input id="cn-emax" type="range" data-bind="Emax" min="8" max="30" step="0.5" value="14"><output data-show="Emax" data-fmt="1"></output></div>
  <div class="btns"><button class="btn ghost" data-act="rebin">Sort again</button></div>
  <p>Drag the top of the ladder, the most energy the neutron can bring. The same number of bins must cover more energy, so each gets taller. The orange ball drops from bin to bin: every later step (choosing an exit, the photon cascade, the walk down the chart) works on these bins. Ten are drawn here; the engine uses up to 40.</p>
  <div class="aside">In the code: <code>density/parameters.py</code> (Ignatyuk <i>a</i>(U), spin cutoff, Wigner distribution, collective enhancement), <code>density/models.py</code> (constant temperature, Fermi gas, tables), <code>density/matching.py</code> (the matching energy from the counted levels), <code>core/grids.py</code> (excitation bins).</div>
</div>`,
    setup(S) {
      S.set("mode", "bohr"); S.to("E", 6.5, true); S.to("Ex", 6, true); S.to("U", 3, true); S.to("U2", 8, true); S.to("Emax", 14, true);
      S.to("beta", 0, true); S.hitT = 0; S.hitA = Math.PI; S.hitN = 0; S.sweep0 = -100; S.binT0 = -100; S.snap = 0;
      S.on("hit", () => { S.hitN++; const r = rng(S.hitN * 97 + 3); S.hitA = r() * TAU; S.hitT = S.time; });
      S.on("deform", () => S.to("beta", S.target.beta > 0.1 ? 0 : 0.3));
      S.on("rebin", () => { S.binT0 = S.time; newCascade(S); });
    },
    steps: [
      (S) => { S.set("mode", "bohr"); S.hitT = S.time - (/shot=compound:0/.test(location.search) ? 4.8 : 0); },
      (S) => { S.set("mode", "ladder"); S.sweep0 = SHOT ? -100 : S.time; S.to("E", 6.5); },
      (S) => { S.set("mode", "join"); },
      (S) => { S.set("mode", "shell"); },
      (S) => { S.set("mode", "spin"); seedDrawers(S); },
      (S) => { S.set("mode", "bins"); S.binT0 = S.time - (SHOT ? 6 : 0); newCascade(S); if (SHOT) casc.t0 = S.time - 1.7; },
    ],
    frame(g, S, dt) {
      if (S.mode === "bohr") drawBohr(g, S);
      else if (S.mode === "ladder") drawLadder(g, S);
      else if (S.mode === "join") drawJoin(g, S, dt);
      else if (S.mode === "shell") drawShell(g, S, dt);
      else if (S.mode === "spin") drawSpin(g, S, dt);
      else drawBins(g, S);
    },
  });

  // ---------- scene 1: Bohr's uniform glow ----------
  function drawBohr(g, S) {
    const { W, H, c } = g;
    const cx = W * 0.5, cy = H * 0.47, R = Math.min(W, H) * 0.24;
    const P = 7.0; let t = S.time - S.hitT; if (t > P) { S.hitT = S.time - (t % P); S.hitA += 2.4; t = t % P; }
    const ang = S.hitA;
    const approach = smooth(0, 1.4, t), hit = smooth(1.35, 1.5, t);
    const spread = smooth(1.5, 4.2, t), uniform = smooth(3.2, 4.6, t);
    const hx = Math.cos(ang) * 0.86, hy = Math.sin(ang) * 0.86;
    const sigma = 0.12 + spread * 1.3, rb = R / Math.sqrt(56) * 0.98;
    g.glow(cx, cy, R * 1.9, c.warm, 0.05 + uniform * 0.32);
    const heats = new Array(NUC.length);
    for (let i = 0; i < NUC.length; i++) { const p = NUC[i]; const d2 = (p.x - hx) ** 2 + (p.y - hy) ** 2; const local = hit * Math.exp(-d2 / (2 * sigma * sigma)) / (0.25 + spread * 1.6) * 1.1; heats[i] = clamp(lerp(local, 0.45, uniform), 0, 1); }
    // heat is drawn as an orange halo behind each nucleon; the nucleons keep their own colours
    const pos = (i) => { const p = NUC[i], jig = 0.4 + heats[i] * 2.6; return [cx + p.x * R + Math.sin(S.time * 3.1 + p.ph * 20) * jig, cy + p.y * R + Math.cos(S.time * 2.7 + p.ph * 17) * jig]; };
    for (const i of NUC_ORDER) if (heats[i] > 0.06) { const [x, y] = pos(i); g.glow(x, y, rb * (2 + heats[i] * 1.6), c.warm, 0.25 + heats[i] * 0.55); }
    for (const i of NUC_ORDER) { const [x, y] = pos(i); g.ball(x, y, rb, NUC[i].p ? c.proton : c.neutron); }
    if (t < 1.5) {
      const d = R + 12 + (1 - approach) * Math.max(W, H) * 0.45;
      const x = cx + Math.cos(ang) * d, y = cy + Math.sin(ang) * d, a = 1 - hit;
      for (let i = 1; i < 8; i++) g.dot(x + Math.cos(ang) * i * 8, y + Math.sin(ang) * i * 8, 5 - i * 0.5, c.neutron, a * (0.25 - i * 0.03));
      g.ball(x, y, 7, c.neutron, a);
    }
    const msg = t < 1.4 ? "a neutron comes in" : t < 3.4 ? "a hot spot: the energy is still local" : "equilibrium: every nucleon holds a share";
    g.label(msg, cx, cy + R + 44, { color: t < 1.4 ? c.neutron : c.warm, size: 16, serif: true, italic: true, bg: true });
    if (t > 4.4) g.label("no trace left of where it was hit", cx, cy + R + 70, { color: c.soft, size: 13, bg: true, alpha: smooth(4.4, 5, t) });
  }

  // ---------- scene 2: the ladder and its magnifier ----------
  function drawLadder(g, S) {
    const { W, H, c } = g, ctx = g.ctx, phone = W < 600;
    // on entry the energy climbs slowly so the rungs visibly multiply
    const sw = (S.time - S.sweep0) / 4.5; if (sw < 1 && S.target.E === 6.5) { S.E = lerp(0.6, 6.5, smooth(0, 1, sw)); }
    const Emax = 20, E = clamp(S.E, 0, Emax);
    const yBot = H * 0.9, yTop = H * 0.08, Y = (e) => yBot - (yBot - yTop) * e / Emax, pxPerMeV = (yBot - yTop) / Emax;
    const lx = W * (phone ? 0.2 : 0.22), hw = Math.min(W * 0.09, 64);
    // overview ladder: band darkness follows log rho; rungs drawn while they are resolvable
    for (let i = 0; i < 120; i++) {
      const E1 = ELAST + (Emax - ELAST) * i / 120, E2 = ELAST + (Emax - ELAST) * (i + 1) / 120, rho = rhoGC(0.5 * (E1 + E2));
      const dark = clamp(Math.log10(rho) / 7, 0, 1); ctx.fillStyle = g.rgba(c.ink, 0.04 + dark * 0.45); ctx.fillRect(lx - hw, Y(E2), 2 * hw, Y(E1) - Y(E2) + 0.5);
    }
    const gr = ctx.createLinearGradient(0, yTop - 4, 0, yTop + 50); gr.addColorStop(0, g.rgba(c.paper, 1)); gr.addColorStop(1, g.rgba(c.paper, 0)); ctx.fillStyle = gr; ctx.fillRect(lx - hw - 4, yTop - 4, 2 * hw + 8, 54);
    LEVELS.forEach((e, i) => g.line(lx - hw, Y(e), lx + hw, Y(e), c.ink, i === 0 ? 3 : 1.4, 0.9));
    g.line(lx - hw, Y(0) + 6, lx - hw, yTop + 20, c.soft, 2.2, 0.8); g.line(lx + hw, Y(0) + 6, lx + hw, yTop + 20, c.soft, 2.2, 0.8);
    g.label("ground state", lx, Y(0) + 16, { color: c.ink, size: 12 });
    // the magnified window
    const lo = E - 0.5, hi = E + 0.5;
    const mx0 = W * (phone ? 0.44 : 0.5), mx1 = W * (phone ? 0.9 : 0.9), my0 = H * 0.14, my1 = H * 0.76;
    const MY = (e) => my1 - (my1 - my0) * (e - lo);
    // bracket on the overview and the magnifier rays
    const by0 = Y(Math.max(lo, 0)), by1 = Y(Math.min(hi, Emax));
    ctx.save(); ctx.strokeStyle = g.rgba(c.accent, 0.8); ctx.lineWidth = 1.5; ctx.strokeRect(lx - hw - 5, by1, 2 * hw + 10, by0 - by1); ctx.restore();
    g.line(lx + hw + 5, by1, mx0, my0, c.accent, 1, 0.35, [3, 4]); g.line(lx + hw + 5, by0, mx0, my1, c.accent, 1, 0.35, [3, 4]);
    // window frame: soft rails, no box
    g.line(mx0, my0 - 6, mx0, my1 + 6, c.soft, 2.2, 0.8); g.line(mx1, my0 - 6, mx1, my1 + 6, c.soft, 2.2, 0.8);
    g.clip(mx0, my0, mx1 - mx0, my1 - my0);
    let nWin = 0, nearest = null;
    // counted levels in the window
    LEVELS.forEach((e) => { if (e >= lo && e <= hi) { nWin++; g.line(mx0, MY(e), mx1, MY(e), c.ink, 2, 0.95); if (!nearest || Math.abs(e - E) < Math.abs(nearest - E)) nearest = e; } });
    // continuum rungs: rung k sits where N(E) crosses k, nudged by a fraction of the local spacing
    const loC = Math.max(lo, ELAST);
    if (hi > ELAST) {
      const k0 = Math.ceil(cumN(loC)), k1 = Math.floor(cumN(hi)), n = k1 - k0 + 1; nWin += Math.max(0, n);
      const step = Math.max(1, Math.ceil(n / 260));
      const a = n < 40 ? 0.9 : n < 120 ? 0.6 : 0.35, lw = n < 40 ? 1.8 : n < 120 ? 1.1 : 0.8;
      if (n > 260) { ctx.fillStyle = g.rgba(c.ink, clamp(0.12 + 0.05 * Math.log10(n / 260), 0.12, 0.5)); ctx.fillRect(mx0, MY(hi), mx1 - mx0, MY(loC) - MY(hi)); }
      for (let k = k0; k <= k1; k += step) {
        let e = energyOfN(k + (step > 1 ? hash(k) * step : 0)); const sp = 1 / Math.max(rhoGC(e), 1e-3); e += (hash(k + 7) - 0.5) * 0.5 * sp * step;
        const tw = 0.75 + 0.25 * Math.sin(S.time * 2.3 + k * 1.7);
        g.line(mx0, MY(e), mx1, MY(e), c.ink, lw, a * tw);
        if (!nearest || Math.abs(e - E) < Math.abs(nearest - E)) nearest = e;
      }
    }
    g.restore();
    // the nucleus sitting on its rung, in both views
    const yb = nearest !== null && nWin < 200 ? MY(nearest) : MY(E);
    const xb = (mx0 + mx1) / 2;
    g.glow(xb, yb - 8, 22, c.warm, 0.45); g.ball(xb, yb - 8, 8, c.warm);
    g.glow(lx, Y(E) - 5, 14, c.warm, 0.4); g.ball(lx, Y(E) - 5, 5, c.warm);
    // window captions
    g.label(`${lo.toFixed(1)}–${hi.toFixed(1)} MeV, magnified`, (mx0 + mx1) / 2, my0 - 18, { color: c.accent, size: 12, bg: true });
    const rho = E < ELAST ? nWin : rhoGC(E);
    const big = nWin > 260;
    g.label(nWin === 0 ? "no level in this slice" : big ? (phone ? `about ${fmtShort(rho)} rungs: too close to draw` : `about ${fmtRho(rho)} rungs in this slice: too close to draw`) : phone ? `${nWin} rung${nWin === 1 ? "" : "s"} in 1 MeV` : `${nWin} rung${nWin === 1 ? "" : "s"} in this 1-MeV slice`, (mx0 + mx1) / 2, my1 + 24, { color: c.ink, size: phone ? 13 : 15, weight: 600, serif: true, bg: true });
    g.label(E < ELAST ? "each one measured: energy, spin and parity" : E < 7 ? "the rungs are multiplying" : "a continuum: the engine uses ρ itself", (mx0 + mx1) / 2, my1 + 46, { color: c.soft, size: 12, bg: true });
    if (E > 7.3 && E < 8.6) g.label("≈ energy to free a neutron", lx + hw + 8, Y(E) - 14, { color: c.neutron, size: 11, align: "left", bg: true });
    g.label("energy ↑", lx, yTop - 6, { color: c.faint, size: 12 });
  }

  // ---------- scene 3: the terrain of the three laws ----------
  function drawJoin(g, S, dt) {
    const { W, H, c } = g, ctx = g.ctx, phone = W < 600;
    const Emax = 16, x0 = W * 0.07, x1 = W * 0.95, yTop = H * 0.06, yBot = H * (phone ? 0.62 : 0.66);
    const lnMin = -1.3, lnMax = lnRhoFG(Emax) + 0.4;
    const X = (E) => x0 + (x1 - x0) * E / Emax, Y = (v) => yBot - (yBot - yTop) * (v - lnMin) / (lnMax - lnMin);
    const Ex = clamp(S.Ex, 4.5, 12), ct = ctAt(Ex);
    const got = ctCount(ct, LEVELS[NLOW], LEVELS[NTOP]), ratio = got / WANT, ok = Math.abs(ratio - 1) < 0.08;
    S.snap += ((ok ? 1 : 0) - S.snap) * (1 - Math.exp(-8 * dt));
    // Fermi-gas hillside
    const pts = []; for (let i = 0; i <= 160; i++) { const E = DELTA + 0.6 + (Emax - DELTA - 0.6) * i / 160; pts.push([X(E), Y(lnRhoFG(E))]); }
    fground(g, pts, c.soft, H * 0.12, 0.3, 70);
    g.poly(pts, c.ink, 2.4, 0.85);
    // the counted rungs: a stack standing where levels 2..20 lie, its top at the height the matched plank has there
    const Ep = 0.5 * (LEVELS[NLOW] + LEVELS[NTOP]), topV = Math.log(rhoCT(Ep, CTSTAR));
    const px = X(Ep), pw = Math.max(16, W * 0.03), pyTop = Y(topV), pyBase = Y(lnMin) + 6;
    for (let k = 0; k < WANT; k++) { const y = lerp(pyBase, pyTop, (k + 1) / WANT); g.line(px - pw, y, px + pw, y, c.ink, 1.6, 0.85); }
    g.line(px - pw, pyBase, px - pw, pyTop, c.soft, 2, 0.8); g.line(px + pw, pyBase, px + pw, pyTop, c.soft, 2, 0.8);
    // the plank: tangent to the hill at the joint, so its left end lands where the CT law says
    const plankV = (E) => Math.log(rhoCT(E, ct));
    const eL = 0.2, wob = ok ? 0 : Math.sin(S.time * 7) * 1.2;
    let yL = Y(plankV(eL)), yAtP = Y(plankV(Ep));
    const snapDy = (pyTop - yAtP) * S.snap; yL += snapDy * (Ex - eL) / (Ex - Ep); yAtP += snapDy;
    const jx = X(Ex), jy = Y(lnRhoFG(Ex));
    const col = S.snap > 0.5 ? c.fission : c.accent;
    if (S.snap > 0.3) g.glow((X(eL) + jx) / 2, (yL + jy) / 2, (jx - X(eL)) * 0.4, c.fission, 0.07 * S.snap * (0.8 + 0.2 * Math.sin(S.time * 3)));
    g.line(X(eL), yL + wob - 1, jx, jy, g.rgba(c.ink, 0.25), 9);
    g.line(X(eL), yL + wob, jx, jy, col, 6);
    g.dot(jx, jy, 7, col); g.ring(jx, jy, 12 + Math.sin(S.time * 3) * 1.5, col, 1.5, 0.6);
    // the contact at the stack: gap with a spark, or a clean seat
    const gap = yAtP - pyTop;   // >0: plank below the top (too few); <0: plank floats above (too many)
    if (!ok) {
      const ys = Math.min(yAtP, pyTop), ye = Math.max(yAtP, pyTop);
      g.line(px, ys, px, ye, c.accent, 1, 0.6, [2, 3]);
      const fl = 0.5 + 0.5 * Math.sin(S.time * 23) * Math.sin(S.time * 7.3);
      for (let i = 0; i < 9; i++) { const a = i / 9 * TAU + S.time * 4, r1 = 5, r2 = 12 + 9 * fl * hash(i + Math.floor(S.time * 12)); g.line(px + Math.cos(a) * r1, pyTop + Math.sin(a) * r1, px + Math.cos(a) * r2, pyTop + Math.sin(a) * r2, c.accent, 1.8, 0.5 + 0.5 * fl); }
      g.glow(px, pyTop, 24, c.accent, 0.35 + 0.3 * fl);
 if (!phone) g.label(gap > 0 ? "gap: plank below the rungs" : "gap: plank above the rungs", px - pw - 8, pyTop - 4, { color: c.accent, size: 11, align: "right", bg: true });
    } else g.glow(px, pyTop, 18, c.fission, 0.35);
    // labels, kept off the lines
    g.label("counted levels", px + pw + 8, pyBase - 12, { color: c.ink, size: 12, align: "left", bg: true });
    g.label(phone ? "CT plank" : "constant-temperature plank", X(0.25), Y(plankV(phone ? 0.6 : 1.6)) - (phone ? 22 : 30), { color: col, size: 12, align: "left", bg: true });
    g.label("Fermi-gas hillside", X(phone ? 11 : 13.2), Y(lnRhoFG(phone ? 11 : 13.2)) - 22, { color: c.ink, size: 12, bg: true });
    g.label(`joint ${Ex.toFixed(1)} MeV`, jx + 10, jy + 20, { color: col, size: 12, weight: 600, align: "left", bg: true });
    if (!phone) g.label("energy →", x1, Y(lnMin) + 16, { color: c.faint, size: 11, align: "right" });
    // two rung stacks: counted vs predicted
    const sy1 = H * 0.91, sh = H * 0.19, cap = phone ? 30 : 40, spc = Math.min(sh / cap, 6);
    const stack = (x, n, color, title) => {
      const m = Math.min(cap, Math.round(n));
      for (let k = 0; k < m; k++) g.line(x - 22, sy1 - (k + 0.5) * spc, x + 22, sy1 - (k + 0.5) * spc, color, Math.min(2, spc * 0.5), 0.9);
      if (n > cap) g.label(`+${Math.round(n - cap)} more`, x, sy1 - cap * spc - 10, { color, size: 11, bg: true });
      g.label(title, x + 32, sy1 - Math.min(m, cap) * spc * 0.5, { color, size: 12, align: "left", bg: true });
    };
    const cxS = W * (phone ? 0.24 : 0.32);
    stack(cxS, WANT, c.ink, `${WANT} counted`);
    stack(cxS + W * (phone ? 0.36 : 0.3), got, ok ? c.fission : c.accent, `${got < 999 ? Math.round(got) : "999+"} predicted`);
    g.label(ok ? "equal: the plank rests on the counted rungs" : got < WANT ? "too few: the plank is too steep and sinks" : "too many: the plank is too shallow and floats", W * 0.5, sy1 + (phone ? 16 : 20), { color: ok ? c.fission : c.soft, size: phone ? 12 : 14, weight: 600, serif: true, bg: true });   // under the stacks, clear of "+N more"
  }

  // ---------- scene 4: shells that melt ----------
  function drawShell(g, S, dt) {
    const { W, H, c } = g, phone = W < 600;
    const U = clamp(S.U, 0, 40);
    const cols = [W * 0.27, W * 0.73];
    const yA = H * 0.06, yB = H * (phone ? 0.5 : 0.52), eLo = 3.5, eHi = 13.6;
    const Ye = (e) => yB - (yB - yA) * (e - eLo) / (eHi - eLo);
    const br = Math.max(4, Math.min(7, H * 0.009)), half = Math.min(W * 0.13, 70);
    SCHEMES.forEach((s, k) => {
      const cx = cols[k];
      const a = aOfU(U, s.dW), T = Math.sqrt(U / a);
      // Metropolis hops at temperature T: up with probability e^(-dE/T), down always
      s.acc += dt; while (s.acc > 0.11) {
        s.acc -= 0.11; const r = s.rand;
        const b = s.balls[Math.floor(r() * s.balls.length)]; if (S.time - b.t0 < 0.4) continue;
        const occ = new Set(s.balls.map((x) => x.slot)), empty = s.slots.map((_, i) => i).filter((i) => !occ.has(i));
        const j = empty[Math.floor(r() * empty.length)]; const dE = s.slots[j].e - s.slots[b.slot].e;
        if (dE === 0) continue;
        if (dE < 0 || (T > 0.01 && r() < Math.exp(-dE / T))) { b.from = b.slot; b.slot = j; b.t0 = S.time; }
      }
      // levels
      s.vis.forEach((li) => { const y = Ye(s.levels[li]); g.line(cx - half, y, cx + half, y, c.soft, 1.6, 0.85); });
      s.slots.forEach((sl) => g.ring(cx + sl.side * half * 0.32, Ye(sl.e) - br - 1, br, c.faint, 1, 0.6));
      if (k === 0) { const y1 = Ye(7), y2 = Ye(11); g.arrow(cx + half + 12, (y1 + y2) / 2, cx + half + 12, y2 + 4, c.soft, 1.2, 0.7, 6); g.arrow(cx + half + 12, (y1 + y2) / 2, cx + half + 12, y1 - 4, c.soft, 1.2, 0.7, 6); g.label("gap", cx + half + 18, (y1 + y2) / 2, { color: c.soft, size: 11, align: "left", bg: true }); }
      // nucleons, with their hops animated along an arc
      s.balls.forEach((b) => {
        const u = smooth(0, 1, (S.time - b.t0) / 0.38), A0 = s.slots[b.from], A1 = s.slots[b.slot];
        const x = lerp(cx + A0.side * half * 0.32, cx + A1.side * half * 0.32, u), y = lerp(Ye(A0.e), Ye(A1.e), u) - br - 1 - Math.sin(u * Math.PI) * 14;
        const up = A1.e > 7.5 && (k === 1 ? A1.e > 8 : true);
        if (u < 1 || up) g.glow(x, y, br * 3, c.warm, u < 1 ? 0.5 : 0.25);
        g.ball(x, y, br, c.neutron);
      });
      g.label(s.name, cx, yB + 22, { color: c.ink, size: phone ? 13 : 15, weight: 600, bg: true });
      const ways = waysAt(s, U);
      const flick = ways > 2 ? 1 + 0.015 * Math.sin(S.time * 17 + k * 3) : 1;
      g.label(ways < 0.5 ? "no arrangement holds this heat" : `≈ ${fmtRho(ways * flick)} arrangement${ways < 1.5 ? "" : "s"}`, cx, yB + (phone ? 40 : 46), { color: ways < 0.5 ? c.ink : c.soft, size: phone ? 11 : 13, weight: ways < 0.5 ? 600 : 500, bg: true });
      // needle gauge for a(U)
      const gy = H * (phone ? 0.9 : 0.86), gr = Math.min(W * 0.14, H * (phone ? 0.16 : 0.12));
      const ang = (v) => Math.PI + clamp((v - 4) / 8, 0, 1) * Math.PI;
      const ctx = g.ctx; ctx.save(); ctx.strokeStyle = g.rgba(c.soft, 0.6); ctx.lineWidth = 2; ctx.beginPath(); ctx.arc(cx, gy, gr, Math.PI, TAU); ctx.stroke(); ctx.restore();
      for (let v = 4; v <= 12; v++) { const t = ang(v), l = v === 8 ? 10 : 5; g.line(cx + Math.cos(t) * gr, gy + Math.sin(t) * gr, cx + Math.cos(t) * (gr - l), gy + Math.sin(t) * (gr - l), v === 8 ? c.ink : c.faint, v === 8 ? 2 : 1); }
      g.label("ã", cx, gy - gr - 10, { color: c.ink, size: 13, serif: true, italic: true });
      const tn = ang(a) + Math.sin(S.time * 9 + k) * 0.01;
      g.line(cx, gy, cx + Math.cos(tn) * gr * 0.86, gy + Math.sin(tn) * gr * 0.86, c.accent, 2.4); g.dot(cx, gy, 4, c.accent);
      g.label(`a ≈ ${a.toFixed(1)}`, cx, gy + 14, { color: c.accent, size: 12, weight: 600 });
    });
    const T0 = Math.sqrt(U / ATILDE);
    g.label(U < 0.3 ? "cold: nobody can move" : `temperature ≈ ${T0.toFixed(1)} MeV`, W * 0.5, H * (phone ? 0.74 : 0.69), { color: c.warm, size: phone ? 12 : 13, bg: true });
  }

  // ---------- scene 5: spin drawers ----------
  function spinTargets(S) {
    const U = clamp(S.U2, 1, 30), a = aOfU(U, 0), s2 = sig2(U, a), T = Math.sqrt(U / a), beta = S.beta;
    const Krot = beta > 0.02 ? clamp(1 + (0.0139 * Math.pow(A, 5 / 3) * (1 + beta / 3) * T - 1) * (beta / 0.3), 1, 40) : 1;
    const dist = []; let sum = 0; for (let J = 0; J < NJ; J++) { const v = (2 * J + 1) * Math.exp(-((J + 0.5) ** 2) / (2 * s2)); dist.push(v); sum += v; }
    return { s2, Krot, frac: dist.map((v) => v / sum) };
  }
  function seedDrawers(S) {
    if (drawers.some((d) => d.length)) return;
    const { frac } = spinTargets(S); const r = spinRand;
    for (let J = 0; J < NJ; J++) for (let k = 0; k < Math.round(frac[J] * 150); k++) drawers[J].push({ par: r() < 0.5, rot: false, born: S.time - 2, die: 0, y: null });
  }
  function drawSpin(g, S, dt) {
    const { W, H, c } = g, ctx = g.ctx, phone = W < 600;
    const { s2, Krot, frac } = spinTargets(S), sigma = Math.sqrt(s2);
    const x0 = W * 0.04, x1 = W * (phone ? 0.96 : 0.75), yB = H * 0.9, yT = H * (phone ? 0.36 : 0.3);
    const colW = (x1 - x0) / NJ, dw = colW * 0.82, tr = Math.max(2.2, Math.min(dw / 5.2, 6.5));
    const perRow = Math.max(2, Math.floor((dw - 4) / (2.3 * tr))), rowH = tr * 2.3, rows = Math.floor((yB - yT - 6) / rowH), cap = perRow * rows;
    const hop = [W * (phone ? 0.5 : 0.42), phone ? H * 0.2 : Math.max(H * 0.12, H * 0.04 + 50)];   // its label stays under the title on short canvases
    const TOTAL = Math.min(200, cap * 0.85 / 0.285);
    const now = S.time, r = spinRand;
    // keep each drawer at its target: spawn into short drawers, retire tokens from full ones, churn a little at rest
    spinSpawnAcc += dt; churnAcc += dt;
    for (let J = 0; J < NJ; J++) {
      const d = drawers[J], tI = Math.round(frac[J] * TOTAL), tR = Math.min(cap - tI, Math.round(frac[J] * TOTAL * (Krot - 1)));
      const liveI = d.filter((t) => !t.die && !t.rot), liveR = d.filter((t) => !t.die && t.rot);
      if (liveI.length > tI) liveI[liveI.length - 1].die = now; if (liveR.length > Math.max(0, tR)) liveR[liveR.length - 1].die = now;
      if (spinSpawnAcc > 0.02) { if (liveI.length < tI) { d.push({ par: r() < 0.5, rot: false, born: now, die: 0, y: null }); spinSpawnAcc -= 0.02; } else if (liveR.length < tR) { d.push({ par: r() < 0.5, rot: true, born: now, die: 0, y: null }); spinSpawnAcc -= 0.02; } }
      for (let i = d.length - 1; i >= 0; i--) if (d[i].die && now - d[i].die > 0.45) d.splice(i, 1);
    }
    spinSpawnAcc = Math.min(spinSpawnAcc, 0.1);
    if (churnAcc > 0.35) { churnAcc = 0; const J = Math.floor(r() * NJ), d = drawers[J], live = d.filter((t) => !t.die); if (live.length > 2) live[Math.floor(r() * live.length)].die = now; }
    // hopper: where the states at this energy come from
    g.glow(hop[0], hop[1], 30, c.warm, 0.25 + 0.05 * Math.sin(now * 3));
    g.line(hop[0] - 26, hop[1] - 8, hop[0] - 6, hop[1] + 12, c.soft, 1.6, 0.7); g.line(hop[0] + 26, hop[1] - 8, hop[0] + 6, hop[1] + 12, c.soft, 1.6, 0.7);
    g.label(`states at ${S.U2.toFixed(1)} MeV`, hop[0], hop[1] - 22, { color: c.warm, size: 12, bg: true });
    for (let J = 0; J < NJ; J++) {
      const xc = x0 + (J + 0.5) * colW, d = drawers[J];
      // drawer: two walls, a floor and a front plate
      g.line(xc - dw / 2, yT, xc - dw / 2, yB, c.soft, 1.2, 0.55); g.line(xc + dw / 2, yT, xc + dw / 2, yB, c.soft, 1.2, 0.55); g.line(xc - dw / 2 - 1, yB, xc + dw / 2 + 1, yB, c.soft, 2.4, 0.8);
      g.label(String(J), xc, yB + 13, { color: c.ink, size: phone ? 11 : 12, weight: 600 });
      let idx = 0;
      d.forEach((t) => {
        const slot = idx; if (!t.die) idx++;
        const row = Math.floor(slot / perRow), colI = slot % perRow;
        const tx = xc - (perRow - 1) * rowH / 2 + colI * rowH, ty = yB - tr - 2 - row * rowH;
        if (t.y === null) t.y = ty; if (!t.die) { t.y += (ty - t.y) * (1 - Math.exp(-10 * dt)); t.x = tx; }
        const fly = smooth(0, 1, (now - t.born) / 0.6);
        const x = lerp(hop[0], t.x, fly), y = lerp(hop[1], t.y, fly) - Math.sin(fly * Math.PI) * 40;
        const al = t.die ? Math.max(0, 1 - (now - t.die) / 0.45) : 1;
        const col = t.rot ? c.accent : c.ink;
        if (row >= rows) return;
        if (t.par) g.dot(x, y, tr, col, 0.85 * al); else g.ring(x, y, tr - 0.6, col, 1.4, 0.9 * al);
      });
    }
    g.label("spin J →", x1, yB + 30, { color: c.faint, size: 11, align: "right" });
    const lx = x0 + 4, ly = yT - 16;
    g.dot(lx + 4, ly, 5, c.ink, 0.85); g.label("+ parity", lx + 14, ly, { color: c.soft, size: 12, align: "left" });
    g.ring(lx + 84, ly, 4.4, c.ink, 1.4); g.label("− parity", lx + 94, ly, { color: c.soft, size: 12, align: "left" });
    if (Krot > 1.05) { g.dot(lx + 170, ly, 5, c.accent, 0.85); g.label(phone ? `rotation ×${Krot.toFixed(0)}` : `added by rotation: ×${Krot.toFixed(0)} (a few drawn)`, lx + 180, ly, { color: c.accent, size: 12, align: "left" }); }
    g.label(`spread σ ≈ ${sigma.toFixed(1)}: most states near J ≈ ${Math.max(0, sigma - 0.5).toFixed(0)}`, phone ? W * 0.5 : (x0 + x1) / 2, H * (phone ? 0.05 : 0.04), { color: c.ink, size: phone ? 13 : 15, weight: 600, serif: true, bg: true });
    if (!phone) {
      const cx = W * 0.88, cy = H * 0.5, R = Math.min(W * 0.1, H * 0.12), U = S.U2;
      g.nucleus(cx, cy, R, { N: 40, Z: 18, t: now, beta: S.beta, rot: now * (0.3 + 0.1 * sigma), heat: 1 + U / 12, jiggle: 0.5, halo: c.warm, haloAlpha: 0.1 + U / 60 });
      g.label(S.beta > 0.05 ? "deformed: it can rotate" : "spherical", cx, cy + R * 1.5 + 18, { color: c.soft, size: 12, bg: true });
    }
  }

  // ---------- scene 6: bins ----------
  function newCascade(S) { const r = rng((S.time * 1000) | 0 + 5); const p = [NBD - 1]; while (p[p.length - 1] >= 0) p.push(p[p.length - 1] - 1 - Math.floor(r() * 3)); casc = { t0: S.time + 3.4, path: p, r }; }
  function drawBins(g, S) {
    const { W, H, c } = g, ctx = g.ctx, phone = W < 600;
    const Emax = S.Emax, topE = Math.max(Emax, 12) * 1.05;
    const yBot = H * 0.92, yTop = H * 0.07, Y = (e) => yBot - (yBot - yTop) * e / topE;
    const cx = W * (phone ? 0.36 : 0.4), hw = Math.min(W * (phone ? 0.2 : 0.17), 150);
    const t = S.time - S.binT0, dE = (Emax - ELAST) / NBD;
    const walls = smooth(0.2, 1.0, t), collapse = smooth(1.3, 2.3, t), sortJ = smooth(2.5, 3.3, t);
    // counted levels
    LEVELS.forEach((e, i) => g.line(cx - hw, Y(e), cx + hw, Y(e), c.ink, i === 0 ? 3 : 1.4, 0.9));
    g.line(cx - hw, Y(0) + 6, cx - hw, Y(Emax) - 4, c.soft, 2.2, 0.8); g.line(cx + hw, Y(0) + 6, cx + hw, Y(Emax) - 4, c.soft, 2.2, 0.8);
    const r = rng(19), nTop = rhoGC(Emax - dE / 2) * dE;
    for (let b = 0; b < NBD; b++) {
      const E1 = ELAST + b * dE, E2 = E1 + dE, Em = 0.5 * (E1 + E2), n = rhoGC(Em) * dE;
      const ya = Y(E2), yb = Y(E1), hpx = yb - ya;
      // dots crowding with energy (count follows log rho), drifting gently
      const nd = Math.round(clamp(1.6 * Math.pow(n, 0.36), 2, 70));
      const bw = (hw * 2 - 10) * clamp(0.18 + 0.12 * Math.log10(1 + n), 0.2, 0.9), bh = Math.max(3, hpx * 0.56);
      const bx = cx - hw + 6, by = (ya + yb) / 2;
      for (let k = 0; k < nd; k++) {
        const fx = r(), fy = r(), ph = r() * TAU;
        const dx = cx - hw + 6 + fx * (hw * 2 - 12) + Math.sin(S.time * 1.3 + ph) * 2, dy = ya + 3 + fy * Math.max(1, hpx - 6) + Math.cos(S.time * 1.1 + ph) * 1;
        const tx = bx + bw / 2, ty = by;
        const x = lerp(dx, tx, collapse), y = lerp(dy, ty, collapse);
        g.dot(x, y, 1.8, c.ink, 0.55 * (1 - collapse));
      }
      // the drawer walls
      if (walls > 0) { g.line(cx - hw, yb, lerp(cx - hw, cx + hw, walls), yb, c.accent, 1.6, 0.85); if (b === NBD - 1) g.line(cx - hw, ya, lerp(cx - hw, cx + hw, walls), ya, c.accent, 1.6, 0.85); }
      // the counted block, then its spin columns
      if (collapse > 0.02) {
        const al = collapse * (1 - sortJ);
        ctx.save(); ctx.globalAlpha = al; ctx.fillStyle = g.rgba(c.accent, 0.3); ctx.strokeStyle = c.accent; ctx.lineWidth = 1.2; ctx.beginPath();
        const w = bw * collapse; if (ctx.roundRect) ctx.roundRect(bx, by - bh / 2, w, bh, 3); else ctx.rect(bx, by - bh / 2, w, bh); ctx.fill(); ctx.stroke(); ctx.restore();
        if (sortJ > 0.02 && hpx > 10) {
          const U = Math.max(Em - DELTA, 0.5), s2 = sig2(U, aOfU(U, 0)); const NJm = 8; const cw = (hw * 2 - 16) / NJm * 0.5;
          let mx = 0; const v = []; for (let J = 0; J < NJm; J++) { const q = (2 * J + 1) * Math.exp(-((J + 0.5) ** 2) / (2 * s2)); v.push(q); mx = Math.max(mx, q); }
          for (let J = 0; J < NJm; J++) {
            const h = (hpx - 5) * v[J] / mx * sortJ * clamp(0.3 + 0.7 * Math.log10(1 + n) / Math.log10(1 + nTop), 0.3, 1), xl = cx - hw + 7 + J * cw * 2;
            ctx.save(); ctx.globalAlpha = sortJ; ctx.fillStyle = g.rgba(c.ink, 0.75); ctx.fillRect(xl, yb - 2 - h, cw * 0.8, h);
            ctx.strokeStyle = g.rgba(c.ink, 0.75); ctx.lineWidth = 1; ctx.strokeRect(xl + cw * 0.85 + 0.5, yb - 2 - h + 0.5, cw * 0.8 - 1, Math.max(0, h - 1)); ctx.restore();
          }
        }
        if (hpx > 13 || b % 2 === 1) g.label(`≈ ${phone ? fmtShort(n) : fmtRho(n)}`, cx + hw + 10, by, { color: c.accent, size: phone ? 11 : 12, align: "left", alpha: collapse, bg: true });
      }
    }
    // the cascade ball: drops from bin to bin, a photon each time, then down the counted levels
    const ct = S.time - casc.t0, hopT = 0.7;
    if (ct > 0) {
      const p = casc.path, k = Math.min(Math.floor(ct / hopT), p.length - 1), f = smooth(0.55, 1, (ct - k * hopT) / hopT);
      const yOf = (i) => i >= 0 ? Y(ELAST + (i + 0.5) * dE) : i === -1 ? Y(LEVELS[1]) : Y(0);
      const i0 = p[k], i1 = p[Math.min(k + 1, p.length - 1)], done = k >= p.length - 1;
      const yb = done ? Y(0) : lerp(yOf(i0), yOf(Math.max(i1, -2)), f), xb = cx + hw - 22;
      g.glow(xb, yb - 7, 20, c.warm, 0.45); g.ball(xb, yb - 7, 7, c.warm);
      if (f > 0 && f < 1 && !done) g.photon(xb + 18 + f * 50, yb - 14 - f * 22, -0.5, 22, 1 - f);
      if (done && ct > (p.length - 1) * hopT + 1.4) { casc.t0 = S.time + 0.3; const r2 = rng((S.time * 977) | 0); const q = [NBD - 1]; while (q[q.length - 1] >= 0) q.push(q[q.length - 1] - 1 - Math.floor(r2() * 3)); casc.path = q; }
    }
    g.label(`${NBD} bins, each ${dE.toFixed(2)} MeV wide`, cx, Y(Emax) - 18, { color: c.accent, size: phone ? 12 : 14, weight: 600, bg: true });
    g.label(phone ? "counted" : "counted levels", cx - hw - 10, Y(2.4), { color: c.soft, size: 12, align: "right" });
    if (!phone) g.label("states in each bin", cx + hw + 10, Y(Emax) - 18, { color: c.faint, size: 11, align: "left" });
    g.label("energy ↑", cx - hw - 10, Y(Emax), { color: c.faint, size: 11, align: "right" });
  }
})();
