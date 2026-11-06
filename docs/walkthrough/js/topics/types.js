/* Kinds of reactor: one plant drawing for every reactor type, driven by the table TY. Five lessons:
 *   rwater (water-cooled), rgas (gas-cooled), rfast (fast), rother (molten salt and special), rcompare (all types side by side).
 * Each step of a type lesson shows one type: its core (by TY.core), the loops that carry the heat out (TY.loops, core side
 * first) and how the heat becomes electricity (TY.conv). Readouts: coolant outlet temperature, pressure, net efficiency.
 * Typical design values (rounded; they vary by plant):
 *   PWR 155 bar, 290 -> 325 C, ~34 % (Westinghouse 4-loop, EPR). BWR ~70 bar, boils in the core, steam ~286 C, ~34 %.
 *   PHWR/CANDU-6: heavy-water coolant ~100 bar in 380 horizontal pressure tubes, 266 -> 310 C; cool low-pressure heavy-water
 *   moderator in the calandria; natural uranium; refuelled at power; ~31 %.
 *   RBMK: graphite moderator, ~1660 vertical pressure tubes of boiling water, ~70 bar, 270 -> 284 C, steam drums, ~31 %.
 *   SCWR (Gen IV): 250 bar, 280 -> ~510 C, once-through to the turbine, ~44 %; not built.
 *   Magnox: CO2 7-27 bar (Calder Hall .. Wylfa), outlet ~350-400 C, natural-uranium metal in magnesium-alloy cans, ~22-31 %.
 *   AGR: CO2 ~40 bar, 290 -> 640 C, 2.5-3.5 % UO2 in stainless steel, ~41 %.
 *   HTGR pebble bed (HTR-PM, Shidao Bay, commercial operation Dec 2023): helium 70 bar, 250 -> 750 C, TRISO particles in
 *   6 cm graphite pebbles, steam 567 C, 2 x 250 MWth -> 210 MWe (~42 %).
 *   VHTR (Gen IV), prismatic blocks: helium outlet ~950 C (Japan's HTTR reached 950 C in 2004), Brayton cycle or hydrogen, ~48 %.
 *   SFR: sodium near atmospheric pressure, 355 -> 545 C (BN-800), pool with intermediate sodium loop then steam, ~40 %.
 *   LFR: lead near atmospheric pressure, 420 -> 535 C (BREST-OD-300, 700 MWth / 300 MWe, ~43 %), steam generators in the pool.
 *   GFR (Gen IV): helium ~70 bar, 400 -> 850 C, no moderator, ~45 %; ALLEGRO demonstrator planned.
 *   MSR: fuel dissolved in fluoride salt (UF4 is green), graphite moderator, ~1 bar; MSBR design 565 -> 705 C, ~44 %;
 *   MSRE at Oak Ridge ran 1965-69 (8 MWth); TMSR-LF1 (2 MWth, thorium, Wuwei, China) first critical 2023.
 *   TRIGA: U-ZrH fuel (hydride moderates; it gets less effective as it heats, a prompt negative feedback), open pool, pulsing.
 *   Integral SMR (NuScale-like): steam generators inside the vessel, natural circulation, ~138 bar, 250 -> 320 C, ~31 %.
 *   Heat-pipe microreactor: KRUSTY (Nevada, 2018): HEU-Mo core ~800 C, sodium heat pipes, Stirling engines (~25 %).
 *   ADS: subcritical core driven by a proton beam on a spallation target; MYRRHA (Belgium) lead-bismuth 270 -> 325 C, planned.
 *   Oklo (Gabon): natural reactors ~2 billion years ago, when uranium held ~3 % U-235; groundwater moderated; ran in pulses
 *   (about 30 min on, 2.5 h off; Meshik et al. 2004).
 *   World fleet (IAEA PRIS, rounded): about 7 in 10 PWRs, ~15 % BWRs, ~10 % PHWRs, a few % everything else. */
(function () {
  const { TAU, clamp, lerp, smooth, rng } = WT.util;
  const r = rng(41);
  // fluids: colour (theme token or hex), dots per loop, speed, gas (sparse fast dots)
  const FL = {
    h2o: { col: "cool", n: 80, v: 1 }, d2o: { col: "#2bb3a3", n: 80, v: 1 }, boil: { col: "cool", n: 90, v: 1.1, steam: 1 },
    scw: { col: "#7fb8ff", n: 80, v: 1.2 }, steam: { col: "cool", n: 90, v: 1.15, steam: 1 },
    co2: { col: "#9fb0c4", n: 45, v: 1.8, gas: 1 }, he: { col: "#c48ef0", n: 40, v: 2, gas: 1 }, gas: { col: "#c48ef0", n: 40, v: 2, gas: 1, brayton: 1 },
    na: { col: "#f0a92b", n: 80, v: 0.9 }, pb: { col: "#8d98a8", n: 80, v: 0.6 }, pbbi: { col: "#8d98a8", n: 80, v: 0.6 },
    fsalt: { col: "#47d27a", n: 80, v: 0.8 }, salt: { col: "#d6c58f", n: 80, v: 0.8 }, pipe: { col: "#f0a92b", n: 40, v: 1.4 },
  };
  let GRAPHITE = "#5b6068"; // lighter on the dark theme (set each frame)
  const TY = {
    pwr: { n: "Pressurized water reactor", ab: "PWR", mod: "light water", cool: "water", spec: "thermal", p: 155, tin: 290, tout: 325, eff: 34, core: "rods", loops: ["h2o", "steam"], conv: "steam", ex: "about 7 in 10 of the world's reactors" },
    bwr: { n: "Boiling water reactor", ab: "BWR", mod: "light water", cool: "boiling water", spec: "thermal", p: 70, tin: 278, tout: 286, eff: 34, core: "rods", boil: 1, below: 1, loops: ["boil"], conv: "steam", ex: "about 15 % of reactors; US, Japan, Sweden" },
    phwr: { n: "Pressurized heavy water reactor", ab: "PHWR", mod: "heavy water", cool: "heavy water", spec: "thermal", p: 100, tin: 266, tout: 310, eff: 31, core: "calandria", loops: ["d2o", "steam"], conv: "steam", ex: "CANDU; Canada, India, Romania, Argentina" },
    rbmk: { n: "Graphite-moderated boiling water reactor", ab: "RBMK", mod: "graphite", cool: "boiling water", spec: "thermal", p: 70, tin: 270, tout: 284, eff: 31, core: "graphite", boil: 1, loops: ["boil"], conv: "steam", ex: "the Chernobyl type; a few still run in Russia" },
    scwr: { n: "Supercritical water reactor", ab: "SCWR", mod: "light water", cool: "supercritical water", spec: "thermal", p: 250, tin: 280, tout: 510, eff: 44, core: "rods", loops: ["scw"], conv: "steam", ex: "Generation IV design, not yet built" },
    magnox: { n: "Magnox", ab: "Magnox", mod: "graphite", cool: "CO₂ gas", spec: "thermal", p: 20, tin: 250, tout: 380, eff: 28, core: "graphite", loops: ["co2", "steam"], conv: "steam", ex: "UK, 1956 (Calder Hall) to 2015 (Wylfa)" },
    agr: { n: "Advanced gas-cooled reactor", ab: "AGR", mod: "graphite", cool: "CO₂ gas", spec: "thermal", p: 40, tin: 290, tout: 640, eff: 41, core: "graphite", loops: ["co2", "steam"], conv: "steam", ex: "UK only: Heysham, Hartlepool, Torness" },
    htgr: { n: "High-temperature gas reactor", ab: "HTGR", mod: "graphite", cool: "helium", spec: "thermal", p: 70, tin: 250, tout: 750, eff: 42, core: "pebbles", loops: ["he", "steam"], conv: "steam", ex: "HTR-PM, Shidao Bay, China (2023)" },
    vhtr: { n: "Very-high-temperature reactor", ab: "VHTR", mod: "graphite", cool: "helium", spec: "thermal", p: 70, tin: 400, tout: 950, eff: 48, core: "prism", loops: ["he", "gas"], conv: "gas", ex: "Japan's HTTR reached 950 °C; Generation IV" },
    sfr: { n: "Sodium-cooled fast reactor", ab: "SFR", mod: "none", cool: "liquid sodium", spec: "fast", p: 1, tin: 355, tout: 545, eff: 40, core: "pool", prim: "na", loops: ["na", "steam"], conv: "steam", ex: "BN-600 and BN-800 (Russia); EBR-II, Phénix" },
    lfr: { n: "Lead-cooled fast reactor", ab: "LFR", mod: "none", cool: "liquid lead", spec: "fast", p: 1, tin: 420, tout: 535, eff: 43, core: "pool", prim: "pb", loops: ["steam"], conv: "steam", ex: "BREST-OD-300 (Russia), being built" },
    gfr: { n: "Gas-cooled fast reactor", ab: "GFR", mod: "none", cool: "helium", spec: "fast", p: 70, tin: 400, tout: 850, eff: 45, core: "prism", loops: ["he", "gas"], conv: "gas", ex: "Generation IV; ALLEGRO demonstrator planned" },
    msr: { n: "Molten salt reactor", ab: "MSR", mod: "graphite", cool: "molten salt, fuel dissolved in it", spec: "thermal", p: 1, tin: 565, tout: 705, eff: 44, core: "salt", loops: ["fsalt", "salt", "steam"], conv: "steam", ex: "MSRE, Oak Ridge (1965–69); TMSR-LF1, China" },
    smr: { n: "Small modular reactor", ab: "SMR", mod: "light water", cool: "water", spec: "thermal", p: 138, tin: 250, tout: 320, eff: 31, core: "integral", loops: ["steam"], conv: "steam", ex: "NuScale (US), Linglong One (China)" },
    micro: { n: "Heat-pipe microreactor", ab: "Micro", mod: "none", cool: "sodium heat pipes", spec: "fast", p: 1, tin: 0, tout: 800, eff: 25, core: "heatpipe", loops: ["pipe"], conv: "stirling", ex: "KRUSTY test, Nevada (2018)" },
    triga: { n: "Pool research reactor", ab: "TRIGA", mod: "water and zirconium hydride", cool: "open pool", spec: "thermal", p: 1, tin: 30, tout: 45, eff: 0, core: "rpool", loops: [], conv: "none", ex: "universities, isotopes, neutron beams" },
    ads: { n: "Accelerator-driven system", ab: "ADS", mod: "none", cool: "lead-bismuth", spec: "fast", p: 1, tin: 270, tout: 325, eff: 0, core: "ads", loops: [], conv: "none", ex: "MYRRHA, Belgium (planned)" },
    oklo: { n: "Natural reactor", ab: "Oklo", mod: "groundwater", cool: "groundwater", spec: "thermal", p: 0, tin: 0, tout: 0, eff: 0, core: "oklo", loops: [], conv: "nature", ex: "Oklo, Gabon, two billion years ago" },
  };
  WT.reactorTypes = TY;
  // where each type is taught: lesson id and step (1-based), for links from the comparison lesson
  const HOME = {};

  // ---------- path helpers ----------
  function mkPath(pts) { const L = [0]; for (let i = 1; i < pts.length; i++) L.push(L[i - 1] + Math.hypot(pts[i][0] - pts[i - 1][0], pts[i][1] - pts[i - 1][1])); return { pts, L, len: L[L.length - 1] }; }
  function at(p, s) { const d = (((s % 1) + 1) % 1) * p.len; let i = 1; while (i < p.L.length - 1 && p.L[i] < d) i++; const u = (d - p.L[i - 1]) / (p.L[i] - p.L[i - 1] || 1), a = p.pts[i - 1], b = p.pts[i]; return [lerp(a[0], b[0], u), lerp(a[1], b[1], u), d / p.len]; }
  const col = (c, k) => (k[0] === "#" ? k : c[k]);
  const snapOn = () => document.body.classList.contains("shot");
  function rr(ctx, x, y, w, h, R) { ctx.beginPath(); if (ctx.roundRect) ctx.roundRect(x, y, w, h, R); else ctx.rect(x, y, w, h); }
  function box(g, x0, y0, x1, y1, R, fill, stroke, a = 0.75) {
    const { ctx, c } = g; ctx.save(); rr(ctx, x0, y0, x1 - x0, y1 - y0, R); ctx.fillStyle = g.rgba(c.paper, 0.92); ctx.fill();
    if (fill) { ctx.fillStyle = fill; ctx.fill(); } ctx.strokeStyle = g.rgba(stroke || c.soft, a); ctx.lineWidth = 2; ctx.stroke(); ctx.restore();
  }

  // ---------- the plant layout for a type ----------
  function layout(t, W, H, phone) {
    const bx = W * 0.03, bw = W * 0.94, by = H * (phone ? 0.08 : 0.1), bh = H * (phone ? 0.6 : 0.58);
    const X = (u) => bx + bw * u, Y = (v) => by + bh * v;
    const L = { X, Y, bx, bw, by, bh };
    const pool = t.core === "pool", wide = pool;
    L.core = { x0: X(0.02), x1: X(wide ? 0.3 : 0.24), y0: Y(0.08), y1: Y(0.95) };
    if (t.core === "integral") L.core = { x0: X(0.08), x1: X(0.2), y0: Y(0.0), y1: Y(1.0) };
    if (t.core === "calandria") L.core = { x0: X(0.0), x1: X(0.32), y0: Y(0.36), y1: Y(0.82) };
    const nHX = Math.max(0, t.loops.length - 1);
    L.hx = []; const a = (L.core.x1 - L.bx) / L.bw + 0.06, b = 0.56;
    for (let i = 0; i < nHX; i++) { const hw = nHX === 1 ? 0.1 : 0.08, u0 = nHX === 1 ? (a + b) / 2 - 0.05 : lerp(a, b - hw, i / (nHX - 1)); L.hx.push({ x0: X(u0), x1: X(u0 + hw), y0: Y(0.08), y1: Y(0.9) }); }
    L.tb = { x0: X(0.63), x1: X(0.82), y: Y(0.26), h: bh * 0.13 };
    L.gen = { x0: X(0.85), x1: X(0.97) };
    L.cond = { x0: X(0.63), x1: X(0.84), y0: Y(0.66), y1: Y(0.84) };
    // loops: rectangles between consecutive boxes (core, heat exchangers, turbine); hot leg on top
    const nodes = [L.core, ...L.hx];
    L.paths = t.loops.map((f, i) => {
      const A = nodes[i], last = i === t.loops.length - 1, ax = (A.x0 + A.x1) / 2;
      if (last && (t.conv === "steam" || t.conv === "gas" || t.conv === "stirling")) {
        const tx = (L.tb.x0 + L.tb.x1) / 2, yc = (L.cond.y0 + L.cond.y1) / 2;
        if (f === "pipe") return [0.31, 0.41, 0.61, 0.71].map((v) => mkPath([[ax, Y(v)], [L.tb.x0 + 8, Y(v)]]));
        return mkPath([[ax, Y(0.2 + 0.03 * i)], [L.tb.x0, Y(0.2 + 0.03 * i)], [L.tb.x0, L.tb.y], [tx, L.tb.y], [tx, yc], [ax, yc], [ax, Y(0.2 + 0.03 * i)]]);
      }
      const B = nodes[i + 1], bxm = (B.x0 + B.x1) / 2, yh = Y(0.2 + 0.04 * i), yc = Y(0.82 - 0.04 * i);
      return mkPath([[ax, yh], [bxm, yh], [bxm, yc], [ax, yc], [ax, yh]]);
    });
    return L;
  }
  function seed(S, t) {
    S.dots = t.loops.map((f) => { const n = FL[f].n, a = []; for (let i = 0; i < n; i++) a.push({ s: i / n + r() * 0.004, o: r() * 2 - 1 }); return a; });
    S.inner = []; for (let i = 0; i < 90; i++) S.inner.push({ s: r(), o: r() * 2 - 1, x: r(), y: r(), a: r() * TAU, t: r() });
    S.nn = []; for (let i = 0; i < 60; i++) S.nn.push({ x: r(), y: r(), a: r() * TAU, t: r() });
  }
  function setType(S, k) { if (S.ty === k) return; S.ty = k; seed(S, TY[k]); }

  // ---------- drawing one plant ----------
  function drawPlant(g, S, dt) {
    const { W, H, c, ctx } = g, phone = W < 600, fs = phone ? 11 : 13, t = TY[S.ty], snap = snapOn();
    GRAPHITE = darkTheme(c) ? "#7d848e" : "#5b6068";
    if (t.core === "oklo") { drawOklo(g, S, phone, fs, snap, dt); return readouts(g, S, t, phone, fs); }
    const L = layout(t, W, H, phone), lab = (s, x, y, o = {}) => g.label(s, x, y, Object.assign({ color: c.soft, size: fs - 1, bg: true }, o));
    const spd = snap ? 0 : dt * 0.05;
    // cooling water at the right edge (steam plants)
    if (t.conv === "steam") g.area([[L.cond.x1, L.cond.y0 + 6], [W, L.cond.y0 + 6], [W, L.cond.y1 - 6], [L.cond.x1, L.cond.y1 - 6]], c.cool, 0.1);
    // pipes and moving fluid
    L.paths.forEach((P, i) => {
      const f = FL[t.loops[i]], fc = col(c, f.col), list = Array.isArray(P) ? P : [P];
      list.forEach((p) => {
        g.poly(p.pts, c.soft, phone ? 9 : 12, 0.16);
        const half = Math.floor(p.pts.length / 2);
        g.poly(p.pts.slice(0, half + 1), c.warm, phone ? 4 : 6, 0.22); g.poly(p.pts.slice(half), fc, phone ? 4 : 6, 0.2);
      });
      S.dots[i].forEach((q, j) => {
        q.s += spd * f.v * (f.gas ? 1.6 : 1);
        const p = list[j % list.length], [x, y, u] = at(p, q.s), hot = u < 0.5;
        const ox = q.o * (phone ? 2 : 3);
        if (f.steam && hot) { if (q.o > 0.3) return; g.glow(x + ox, y + ox, phone ? 6 : 9, c.ink, 0.16); g.dot(x + ox, y + ox, 1.7, c.ink, 0.7); }
        else if (f.gas) g.dot(x + ox, y + ox, 1.8, hot ? c.warm : fc, 0.85);
        else if (t.loops[i] === "fsalt") { g.glow(x + ox, y + ox, 7, fc, 0.25); g.dot(x + ox, y + ox, 2.3, fc, 0.9); }
        else g.dot(x + ox, y + ox, phone ? 2 : 2.5, hot && !f.steam ? (t.loops[i] === "h2o" || t.loops[i] === "d2o" || t.loops[i] === "scw" ? c.warm : fc) : fc, 0.8);
      });
    });
    // heat exchangers
    L.hx.forEach((h, i) => {
      box(g, h.x0, h.y0, h.x1, h.y1, (h.x1 - h.x0) / 2, g.rgba(c.soft, 0.08));
      for (let k = 0; k < 6; k++) { const y = lerp(h.y0 + 18, h.y1 - 18, k / 5); g.poly([[h.x0 + 6, y], [h.x1 - 6, y + 6]], c.soft, 1.2, 0.5); }
      const next = t.loops[i + 1], sh = phone || L.hx.length > 1, nm = next === "steam" ? (sh ? "steam gen." : "steam generator") : (sh ? "heat exch." : "heat exchanger");
      lab(nm, (h.x0 + h.x1) / 2, h.y1 + (phone ? 12 : 16));
    });
    // turning heat into electricity
    if (t.conv === "steam" || t.conv === "gas" || t.conv === "stirling") drawConv(g, S, L, t, phone, fs, dt, snap, lab);
    if (t.conv === "none") {
      const x = (L.X(0.62) + L.X(0.96)) / 2;
      if (t.core !== "ads") { g.label(t.core === "rpool" ? "no turbine" : "", x, L.Y(0.35), { color: c.ink, size: fs + 3, weight: 600, serif: true }); lab(phone ? "neutrons for research" : "neutrons for research, isotopes for medicine", x, L.Y(0.48), { color: c.soft, size: fs }); }
    }
    // the core on top
    CORE[t.core](g, S, L, t, phone, fs, dt, snap, lab);
    readouts(g, S, t, phone, fs);
  }

  function drawConv(g, S, L, t, phone, fs, dt, snap, lab) {
    const { c, ctx } = g, tb = L.tb, gen = L.gen, cd = L.cond, P = 1;
    S.rot = (S.rot || 0) + dt * (snap ? 0 : 8);
    if (t.conv === "stirling") {
      for (let k = 0; k < 2; k++) { const y0 = L.Y(0.25 + 0.3 * k), y1 = y0 + L.bh * 0.22; box(g, tb.x0, y0, tb.x1, y1, 8, g.rgba(c.warm, 0.08));
        const px = lerp(tb.x0 + 14, tb.x1 - 14, 0.5 + 0.35 * Math.sin(S.rot * 1.2 + k * 2)); g.line(px, y0 + 6, px, y1 - 6, c.ink, 5, 0.75); }
      lab(phone ? "Stirling engines" : "Stirling engines", (tb.x0 + tb.x1) / 2, L.Y(0.82), { color: c.ink, weight: 600 });
    } else {
      ctx.save(); { const tg = ctx.createLinearGradient(0, tb.y - tb.h, 0, tb.y + tb.h); tg.addColorStop(0, g.rgba(c.soft, 0.06)); tg.addColorStop(0.3, g.rgba(c.soft, 0.24)); tg.addColorStop(1, g.rgba(c.soft, 0.05)); ctx.fillStyle = tg; }
      ctx.strokeStyle = g.rgba(c.soft, 0.75); ctx.lineWidth = 2; ctx.beginPath(); ctx.moveTo(tb.x0, tb.y - tb.h * 0.45); ctx.lineTo(tb.x1, tb.y - tb.h); ctx.lineTo(tb.x1, tb.y + tb.h); ctx.lineTo(tb.x0, tb.y + tb.h * 0.45); ctx.closePath(); ctx.fill(); ctx.stroke(); ctx.restore();
      const nd = phone ? 4 : 6;
      for (let d = 0; d < nd; d++) { const x = lerp(tb.x0 + 10, tb.x1 - 10, (d + 0.5) / nd), R = lerp(tb.h * 0.42, tb.h * 0.92, (d + 0.5) / nd);
        for (let b = 0; b < 6; b++) { const a = S.rot + b * TAU / 6 + d * 0.4, front = Math.cos(a); g.line(x - 3 * front, tb.y, x + 3 * front, tb.y + Math.sin(a) * R, front > 0 ? c.ink : c.soft, 2, front > 0 ? 0.8 : 0.3); } }
      lab(t.conv === "gas" ? (phone ? "gas turbine" : "helium gas turbine") : "turbine", (tb.x0 + tb.x1) / 2, tb.y + tb.h + (phone ? 10 : 14));
      box(g, cd.x0, cd.y0, cd.x1, cd.y1, 8, g.rgba(c.cool, 0.12));
      lab(t.conv === "gas" ? "precooler" : "condenser", (cd.x0 + cd.x1) / 2, cd.y1 + (phone ? 10 : 14));
    }
    g.line(tb.x1, tb.y, gen.x0, tb.y, c.soft, 3, 0.8);
    box(g, gen.x0, tb.y - tb.h * 0.6, gen.x1, tb.y + tb.h * 0.6, 8, g.rgba(c.photon, 0.25), c.soft, 0.7);
    g.glow((gen.x0 + gen.x1) / 2, tb.y, tb.h * 1.2, c.photon, 0.4 * P);
    lab(phone ? "gen." : "generator", (gen.x0 + gen.x1) / 2, tb.y + tb.h * 0.6 + (phone ? 10 : 14), { color: c.photon, weight: 600 });
    const lx = (gen.x0 + gen.x1) / 2; g.line(lx, tb.y - tb.h * 0.6, lx, L.by - 6, c.photon, 2, 0.8);
    for (let i = 0; i < 3; i++) { const u = (S.time * 1.5 + i / 3) % 1; g.glow(lx, lerp(tb.y - tb.h * 0.6, L.by - 6, u), 8, c.photon, 0.8); }
  }

  // ---------- cores ----------
  function vesselPath(ctx, x0, y0, x1, y1) { const vr = (x1 - x0) / 2; ctx.beginPath(); ctx.moveTo(x0, y0 + vr * 0.6); ctx.quadraticCurveTo(x0, y0, x0 + vr, y0); ctx.quadraticCurveTo(x1, y0, x1, y0 + vr * 0.6); ctx.lineTo(x1, y1 - vr * 0.6); ctx.quadraticCurveTo(x1, y1, x0 + vr, y1); ctx.quadraticCurveTo(x0, y1, x0, y1 - vr * 0.6); ctx.closePath(); }
  function fuelCol(g, x0, x1, y0, y1, n, heat, w = 0.3) {
    const { c, ctx } = g, aw = (x1 - x0) / n;
    for (let i = 0; i < n; i++) { const x = x0 + aw * (i + 0.5), w2 = aw * w; ctx.save(); const fg = ctx.createLinearGradient(x - w2, 0, x + w2, 0);
      fg.addColorStop(0, g.rgba(c.warm, 0.5)); fg.addColorStop(0.4, g.rgba("#ffd2a0", 0.6 + 0.3 * heat)); fg.addColorStop(1, g.rgba(c.warm, 0.4)); ctx.fillStyle = fg; ctx.fillRect(x - w2, y0, 2 * w2, y1 - y0); ctx.restore(); }
  }
  const darkTheme = (c) => /^#[0-3]/.test(c.paper);
  function cherenkov(g, x, y, R, a) { const { c, ctx } = g; ctx.save(); if (darkTheme(c)) ctx.globalCompositeOperation = "lighter"; g.glow(x, y, R, darkTheme(c) ? "#5fb0ff" : c.cool, a); g.glow(x, y, R * 0.5, "#a9d6ff", a * 0.6); ctx.restore(); }
  function rise(g, S, x0, x1, y0, y1, n, color, size, alpha, spd) { // dots drifting upward through a region
    for (let i = 0; i < n; i++) { const q = S.inner[i % S.inner.length], u = (q.s + S.time * spd) % 1; g.dot(lerp(x0, x1, q.x), lerp(y1, y0, u), size, color, alpha * Math.min(1, u * 6, (1 - u) * 6)); }
  }
  function bubbles(g, S, x0, x1, y0, y1, n) { const { c } = g; for (let i = 0; i < n; i++) { const q = S.inner[i % S.inner.length], u = (q.s + S.time * 0.35) % 1; g.ring(lerp(x0, x1, q.x) + Math.sin(i * 7 + S.time * 3) * 2, lerp(y1, y0, u), 1.6 + 2.2 * u, c.ink, 1, 0.55 * (1 - u * 0.6)); } }
  function neutrons(g, S, x0, x1, y0, y1, n, dt, fast) {
    const { c } = g; for (let i = 0; i < n; i++) { const q = S.nn[i % S.nn.length]; q.t += dt * (fast ? 3.2 : 2.2); if (q.t > 1) { q.t = 0; q.x = r(); q.y = r(); q.a = r() * TAU; }
      g.dot(lerp(x0, x1, q.x) + Math.cos(q.a) * q.t * 14, lerp(y0, y1, q.y) + Math.sin(q.a) * q.t * 14, 1.8, c.neutron, 0.85 * (1 - q.t)); }
  }
  const CORE = {
    rods(g, S, L, t, phone, fs, dt, snap, lab) {
      const { c, ctx } = g, { x0, x1, y0, y1 } = L.core, cy0 = lerp(y0, y1, 0.45), cy1 = lerp(y0, y1, 0.85);
      ctx.save(); vesselPath(ctx, x0, y0, x1, y1); const wg = ctx.createLinearGradient(0, y0, 0, y1); wg.addColorStop(0, g.rgba(t.ab === "SCWR" ? "#7fb8ff" : c.warm, 0.2)); wg.addColorStop(1, g.rgba(c.cool, 0.28));
      ctx.fillStyle = g.rgba(c.paper, 0.95); ctx.fill(); ctx.fillStyle = wg; ctx.fill(); ctx.strokeStyle = g.rgba(c.soft, 0.8); ctx.lineWidth = 3; ctx.stroke(); ctx.clip();
      cherenkov(g, (x0 + x1) / 2, (cy0 + cy1) / 2, (x1 - x0) * 0.8, 0.45);
      fuelCol(g, x0 + 8, x1 - 8, cy0, cy1, phone ? 5 : 7, 1);
      if (t.boil) bubbles(g, S, x0 + 8, x1 - 8, y0 + 20, cy1, 40);
      else if (t.ab === "SCWR") rise(g, S, x0 + 8, x1 - 8, y0 + 10, cy1, 50, "#bfe0ff", 1.6, 0.6, 0.5); // supercritical: no bubbles, one phase
      neutrons(g, S, x0 + 10, x1 - 10, cy0, cy1, 30, dt);
      // control rods: from the top (PWR) or from below (BWR)
      const na = phone ? 5 : 7, aw = (x1 - x0 - 16) / na;
      for (let i = 0; i < na - 1; i++) { const x = x0 + 8 + aw * (i + 1); if (t.below) g.line(x, y1, x, lerp(cy1, cy0, 0.2), c.ink, 4, 0.8); else g.line(x, y0 + 4, x, lerp(cy0, cy1, 0.2), c.ink, 4, 0.8); }
      if (t.boil) { ctx.fillStyle = g.rgba(c.soft, 0.25); ctx.fillRect(x0, y0 + 8, x1 - x0, (cy0 - y0) * 0.45); }
      ctx.restore();
      lab(phone ? "vessel" : "reactor vessel", (x0 + x1) / 2, y1 + (phone ? 12 : 16));
      if (t.boil) lab(phone ? "boils in the core" : "water boils in the core", (x0 + x1) / 2, y0 - 12, { color: c.ink, weight: 600 });
      else if (t.ab === "SCWR") lab(phone ? "250 bar: never boils" : "250 bar: hotter than boiling, still one fluid", (x0 + x1) / 2 + (phone ? 0 : 40), y0 - 12, { color: c.ink, weight: 600 });
      if (t.below) lab(phone ? "rods from below" : "control rods from below", (x0 + x1) / 2, y1 + (phone ? 28 : 36), { color: c.soft });
    },
    integral(g, S, L, t, phone, fs, dt, snap, lab) {
      const { c, ctx } = g, { x0, x1, y0, y1 } = L.core, cy0 = lerp(y0, y1, 0.66), cy1 = lerp(y0, y1, 0.92), xm = (x0 + x1) / 2;
      ctx.save(); vesselPath(ctx, x0, y0, x1, y1); ctx.fillStyle = g.rgba(c.paper, 0.95); ctx.fill(); ctx.fillStyle = g.rgba(c.cool, 0.2); ctx.fill(); ctx.strokeStyle = g.rgba(c.soft, 0.8); ctx.lineWidth = 3; ctx.stroke(); ctx.clip();
      cherenkov(g, xm, (cy0 + cy1) / 2, (x1 - x0) * 0.8, 0.45); fuelCol(g, xm - (x1 - x0) * 0.25, xm + (x1 - x0) * 0.25, cy0, cy1, 3, 1);
      // riser in the middle, steam generator coils around it, water falling back down the sides: natural circulation
      g.line(xm - (x1 - x0) * 0.12, cy0, xm - (x1 - x0) * 0.12, y0 + 30, c.soft, 1.5, 0.5); g.line(xm + (x1 - x0) * 0.12, cy0, xm + (x1 - x0) * 0.12, y0 + 30, c.soft, 1.5, 0.5);
      rise(g, S, xm - (x1 - x0) * 0.1, xm + (x1 - x0) * 0.1, y0 + 30, cy0, 30, c.warm, 2, 0.8, 0.4);
      for (let k = 0; k < 8; k++) { const y = lerp(y0 + 40, cy0 - 30, k / 7); g.line(x0 + 4, y, xm - (x1 - x0) * 0.14, y + 5, c.ink, 1.5, 0.5); g.line(xm + (x1 - x0) * 0.14, y, x1 - 4, y + 5, c.ink, 1.5, 0.5); }
      for (let i = 0; i < 24; i++) { const q = S.inner[i], u = (q.s + S.time * 0.3) % 1, side = i % 2 ? 1 : -1; g.dot(xm + side * (x1 - x0) * 0.33, lerp(y0 + 30, cy0, u), 2, c.cool, 0.8); }
      ctx.restore();
      lab(phone ? "all in one vessel" : "core, pump-free loop and steam generator in one vessel", xm + (phone ? 30 : 90), y1 + (phone ? 12 : 16), { color: c.ink, weight: 600 });
      lab(phone ? "steam gen." : "steam generator", x1 + 6, lerp(y0, cy0, 0.4), { align: "left" });
      lab("core", x1 + 6, (cy0 + cy1) / 2, { align: "left", color: c.warm, weight: 600 });
    },
    calandria(g, S, L, t, phone, fs, dt, snap, lab) {
      const { c, ctx } = g, { x0, x1, y0, y1 } = L.core, ym = (y0 + y1) / 2, h = y1 - y0;
      ctx.save(); rr(ctx, x0, y0, x1 - x0, h, h / 2); ctx.fillStyle = g.rgba(c.paper, 0.95); ctx.fill(); ctx.fillStyle = g.rgba("#2bb3a3", 0.22); ctx.fill(); ctx.strokeStyle = g.rgba(c.soft, 0.8); ctx.lineWidth = 3; ctx.stroke(); ctx.clip();
      cherenkov(g, (x0 + x1) / 2, ym, (x1 - x0) * 0.6, 0.35);
      const n = phone ? 5 : 7;
      for (let k = 0; k < n; k++) { const y = lerp(y0 + h * 0.18, y1 - h * 0.18, k / (n - 1)); ctx.fillStyle = g.rgba(c.soft, 0.3); ctx.fillRect(x0 - 10, y - 5, x1 - x0 + 20, 10); ctx.fillStyle = g.rgba(c.warm, 0.85); ctx.fillRect(x0 + h * 0.2, y - 2.5, x1 - x0 - h * 0.4, 5);
        for (let j = 0; j < 4; j++) { const u = ((S.time * 0.25 + j / 4 + k * 0.13) % 1); g.dot(lerp(x0, x1, k % 2 ? u : 1 - u), y, 2, "#2bb3a3", 0.9); } }
      neutrons(g, S, x0 + 10, x1 - 10, y0 + 10, y1 - 10, 24, dt);
      ctx.restore();
      lab(phone ? "calandria: cool heavy water" : "calandria: cool heavy water slows the neutrons", (x0 + x1) / 2 + (phone ? 10 : 30), y1 + (phone ? 12 : 16), { color: "#2bb3a3", weight: 600 });
      lab(phone ? "pressure tubes" : "horizontal pressure tubes, refuelled while running", (x0 + x1) / 2 + (phone ? 10 : 40), y0 - 14, { color: c.ink });
    },
    graphite(g, S, L, t, phone, fs, dt, snap, lab) {
      const { c, ctx } = g, { x0, x1, y0, y1 } = L.core, gx0 = x0 + 10, gx1 = x1 - 10, gy0 = lerp(y0, y1, 0.3), gy1 = lerp(y0, y1, 0.86), gas = t.loops[0] === "co2";
      box(g, x0, y0, x1, y1, gas ? 14 : 4, gas ? g.rgba(c.soft, 0.1) : null, c.soft, 0.85);
      if (gas) { ctx.save(); ctx.strokeStyle = g.rgba(c.soft, 0.35); ctx.lineWidth = 7; rr(ctx, x0 + 4, y0 + 4, x1 - x0 - 8, y1 - y0 - 8, 12); ctx.stroke(); ctx.restore(); }
      ctx.save(); ctx.fillStyle = g.rgba(GRAPHITE, 0.85); ctx.fillRect(gx0, gy0, gx1 - gx0, gy1 - gy0); ctx.restore();
      const n = phone ? 6 : 9, aw = (gx1 - gx0) / n;
      for (let i = 0; i < n; i++) { const x = gx0 + aw * (i + 0.5); g.line(x, t.boil ? y0 + 12 : gy0, x, gy1, c.paper, aw * 0.42, 0.9);
        if (i % 3 !== 1 || !t.boil) g.line(x, gy0 + 4, x, gy1 - 4, c.warm, aw * 0.18, 0.85); else g.line(x, gy0, x, lerp(gy0, gy1, 0.4), c.ink, aw * 0.2, 0.85); }
      g.glow((gx0 + gx1) / 2, (gy0 + gy1) / 2, (gx1 - gx0) * 0.7, c.warm, 0.18);
      if (t.boil) { for (let i = 0; i < 46; i++) { const q = S.inner[i], k = i % n; if (k % 3 === 1) continue; const x = gx0 + aw * (k + 0.5), u = (q.s + S.time * 0.35) % 1; g.ring(x, lerp(gy1, y0 + 12, u), 1.4 + 1.6 * u, c.ink, 1, 0.6 * (1 - u * 0.5)); }
        ctx.save(); ctx.fillStyle = g.rgba(c.soft, 0.3); ctx.fillRect(gx0, y0 + 6, gx1 - gx0, 10); ctx.restore(); }
      else rise(g, S, gx0, gx1, gy0 - 30, gy1, 50, "#9fb0c4", 1.8, 0.8, 0.9);
      neutrons(g, S, gx0, gx1, gy0, gy1, 24, dt);
      lab(phone ? "graphite" : "graphite blocks slow the neutrons", (x0 + x1) / 2 + (phone ? 0 : 40), y1 + (phone ? 12 : 16), { color: c.ink, weight: 600 });
      lab(t.boil ? (phone ? "boiling water in tubes" : "water boils in ~1,700 pressure tubes") : (phone ? "CO₂ gas" : "CO₂ gas blown through the channels"), (x0 + x1) / 2 + (phone ? 0 : 40), y0 - 14, { color: c.soft });
    },
    pebbles(g, S, L, t, phone, fs, dt, snap, lab) {
      const { c, ctx } = g, { x0, x1, y0, y1 } = L.core, py0 = lerp(y0, y1, 0.15), py1 = lerp(y0, y1, 0.88);
      ctx.save(); vesselPath(ctx, x0, y0, x1, y1); ctx.fillStyle = g.rgba(c.paper, 0.95); ctx.fill(); ctx.fillStyle = g.rgba("#c48ef0", 0.08); ctx.fill(); ctx.strokeStyle = g.rgba(c.soft, 0.8); ctx.lineWidth = 3; ctx.stroke(); ctx.clip();
      g.glow((x0 + x1) / 2, (py0 + py1) / 2, (x1 - x0) * 0.8, c.warm, 0.3);
      const R = Math.max(3, (x1 - x0) / (phone ? 14 : 18)), cols = Math.floor((x1 - x0 - 10) / (2 * R)), rows = Math.floor((py1 - py0) / (1.75 * R)), fall = snap ? 0 : (S.time * 4) % (1.75 * R);
      for (let j = -1; j < rows; j++) for (let i = 0; i < cols; i++) { const x = x0 + 5 + R + i * 2 * R + (j % 2 ? R : 0), y = py0 + j * 1.75 * R + fall + R; if (y > py1 || y < py0 || x > x1 - R) continue;
        const hot = smooth(py0, py1, y) * 0.6 + 0.3; g.ball(x, y, R * 0.92, hot > 0.6 ? "#c08060" : "#7a7f88", 0.95); }
      rise(g, S, x0 + 8, x1 - 8, py0, py1, 40, "#c48ef0", 1.8, 0.85, -0.6);
      neutrons(g, S, x0 + 10, x1 - 10, py0, py1, 20, dt);
      ctx.restore();
      lab(phone ? "pebbles of fuel" : "tennis-ball pebbles of fuel and graphite, slowly sinking", (x0 + x1) / 2 + (phone ? 10 : 90), y1 + (phone ? 12 : 16), { color: c.ink, weight: 600 });
      lab(phone ? "helium flows down" : "helium flows down through the bed", (x0 + x1) / 2 + (phone ? 0 : 40), y0 - 12, { color: "#c48ef0" });
    },
    prism(g, S, L, t, phone, fs, dt, snap, lab) {
      const { c, ctx } = g, { x0, x1, y0, y1 } = L.core, py0 = lerp(y0, y1, 0.2), py1 = lerp(y0, y1, 0.85), fast = t.spec === "fast";
      ctx.save(); vesselPath(ctx, x0, y0, x1, y1); ctx.fillStyle = g.rgba(c.paper, 0.95); ctx.fill(); ctx.fillStyle = g.rgba("#c48ef0", 0.08); ctx.fill(); ctx.strokeStyle = g.rgba(c.soft, 0.8); ctx.lineWidth = 3; ctx.stroke(); ctx.clip();
      const n = phone ? 4 : 5, bw = (x1 - x0 - 16) / n, rows = 4;
      for (let i = 0; i < n; i++) for (let j = 0; j < rows; j++) { const bx = x0 + 8 + i * bw, by = lerp(py0, py1, j / rows), bh = (py1 - py0) / rows;
        ctx.save(); ctx.fillStyle = fast ? g.rgba(c.warm, 0.45) : g.rgba(GRAPHITE, 0.8); ctx.fillRect(bx + 1.5, by + 1.5, bw - 3, bh - 3); ctx.restore();
        for (let k = 0; k < 3; k++) g.dot(bx + bw * (0.25 + 0.25 * k), by + bh / 2, Math.max(1.5, bw * 0.07), k === 1 ? c.paper : c.warm, 0.9); }
      g.glow((x0 + x1) / 2, (py0 + py1) / 2, (x1 - x0) * 0.8, c.warm, fast ? 0.4 : 0.28);
      rise(g, S, x0 + 8, x1 - 8, py0, py1, 40, "#c48ef0", 1.8, 0.85, -0.7);
      neutrons(g, S, x0 + 10, x1 - 10, py0, py1, 22, dt, fast);
      ctx.restore();
      lab(fast ? (phone ? "no moderator" : "no moderator: dense fuel, fast neutrons") : (phone ? "graphite blocks" : "hexagonal graphite blocks with fuel"), (x0 + x1) / 2 + (phone ? 0 : 50), y1 + (phone ? 12 : 16), { color: c.ink, weight: 600 });
      lab(phone ? "helium" : "helium, 70 bar", (x0 + x1) / 2, y0 - 12, { color: "#c48ef0" });
    },
    pool(g, S, L, t, phone, fs, dt, snap, lab) {
      const { c, ctx } = g, { x0, x1, y0, y1 } = L.core, f = FL[t.prim], mc = col(c, f.col), xm = (x0 + x1) / 2, lead = t.prim === "pb";
      box(g, x0, y0, x1, y1, 10, null, c.soft, 0.85);
      ctx.save(); rr(ctx, x0 + 3, y0 + 18, x1 - x0 - 6, y1 - y0 - 21, 8); ctx.clip(); ctx.fillStyle = g.rgba(mc, 0.22); ctx.fillRect(x0, y0, x1 - x0, y1 - y0);
      g.area([[x0, y0 + 18], [x1, y0 + 18], [x1, y0 + 22], [x0, y0 + 22]], mc, 0.5);
      // the core: a tight hexagonal bundle near the bottom
      const cw = (x1 - x0) * 0.32, cy0 = lerp(y0, y1, 0.58), cy1 = lerp(y0, y1, 0.86);
      g.glow(xm, (cy0 + cy1) / 2, cw * 1.4, c.warm, 0.45); fuelCol(g, xm - cw / 2, xm + cw / 2, cy0, cy1, 6, 1, 0.42);
      // in-pool heat exchangers (SFR) or steam generators (LFR)
      const hx = [x0 + (x1 - x0) * 0.1, x1 - (x1 - x0) * 0.1 - 14];
      hx.forEach((x) => { ctx.save(); ctx.fillStyle = g.rgba(c.soft, 0.35); ctx.fillRect(x, y0 + 6, 14, (y1 - y0) * 0.55); ctx.restore(); for (let k = 0; k < 6; k++) g.line(x + 2, y0 + 30 + k * 12, x + 12, y0 + 36 + k * 12, c.ink, 1, 0.5); });
      // the pool circulation: up through the core, over into the exchangers, down and back
      const loop = mkPath([[xm, cy1], [xm, y0 + 30], [hx[1] + 7, y0 + 30], [hx[1] + 7, lerp(y0, y1, 0.75)], [xm + cw / 2, cy1 + 8], [xm, cy1]]);
      const loopL = mkPath([[xm, cy1], [xm, y0 + 30], [hx[0] + 7, y0 + 30], [hx[0] + 7, lerp(y0, y1, 0.75)], [xm - cw / 2, cy1 + 8], [xm, cy1]]);
      for (let i = 0; i < 70; i++) { const q = S.inner[i % S.inner.length], p = i % 2 ? loop : loopL, [x, y, u] = at(p, q.s + S.time * 0.04 * f.v + i / 70); g.dot(x + q.o * 4, y + q.o * 3, 2.2, u < 0.45 ? c.warm : mc, 0.8); }
      neutrons(g, S, xm - cw / 2, xm + cw / 2, cy0, cy1, 26, dt, true);
      ctx.restore();
      lab(lead ? (phone ? "pool of molten lead" : "a pool of molten lead, near atmospheric pressure") : (phone ? "pool of liquid sodium" : "a pool of liquid sodium, near atmospheric pressure"), xm, y1 + (phone ? 12 : 16), { color: mc, weight: 600 });
      lab(phone ? "fast core, no moderator" : "small dense core, no moderator", xm, cy0 - 14, { color: c.ink });
      if (!phone) lab(lead ? "steam generators in the pool" : "heat exchangers in the pool", x1 + 6, y0 + 20, { align: "left" });
    },
    salt(g, S, L, t, phone, fs, dt, snap, lab) {
      const { c, ctx } = g, { x0, x1, y0, y1 } = L.core, xm = (x0 + x1) / 2, gx0 = x0 + 14, gx1 = x1 - 14, gy0 = lerp(y0, y1, 0.2), gy1 = lerp(y0, y1, 0.85), fc = FL.fsalt.col;
      ctx.save(); vesselPath(ctx, x0, y0, x1, y1); ctx.fillStyle = g.rgba(c.paper, 0.95); ctx.fill(); ctx.fillStyle = g.rgba(fc, 0.18); ctx.fill(); ctx.strokeStyle = g.rgba(c.soft, 0.8); ctx.lineWidth = 3; ctx.stroke(); ctx.clip();
      ctx.fillStyle = g.rgba(GRAPHITE, 0.85); ctx.fillRect(gx0, gy0, gx1 - gx0, gy1 - gy0);
      const n = phone ? 6 : 9, aw = (gx1 - gx0) / n;
      for (let i = 0; i < n; i++) { const x = gx0 + aw * (i + 0.5); g.line(x, gy0, x, gy1, fc, aw * 0.35, 0.55); }
      g.glow(xm, (gy0 + gy1) / 2, (gx1 - gx0) * 0.75, fc, 0.35);
      for (let i = 0; i < 60; i++) { const q = S.inner[i], k = Math.floor(q.x * n), u = (q.s + S.time * 0.3) % 1; g.dot(gx0 + aw * (k + 0.5), lerp(gy1 + 10, gy0 - 10, u), 2.2, fc, 0.9); }
      neutrons(g, S, gx0, gx1, gy0, gy1, 22, dt);
      ctx.restore();
      lab(phone ? "fuel is dissolved in the salt" : "the fuel is dissolved in the salt: no fuel rods", xm + (phone ? 10 : 60), y1 + (phone ? 12 : 16), { color: fc, weight: 600 });
      lab(phone ? "graphite" : "graphite moderator, salt in channels", xm + (phone ? 0 : 30), y0 - 12, { color: c.soft });
      if (!phone) lab("freeze plug: melts to drain the salt into tanks", xm, y1 + 36, { color: c.soft, size: fs - 2 });
    },
    heatpipe(g, S, L, t, phone, fs, dt, snap, lab) {
      const { c, ctx } = g, { x0, x1, y0, y1 } = L.core, cy0 = L.Y(0.25), cy1 = L.Y(0.75), xm = (x0 + x1) / 2;
      box(g, x0 + 10, cy0, x1 - 10, cy1, 10, g.rgba(c.warm, 0.35), c.soft, 0.85);
      g.glow(xm, (cy0 + cy1) / 2, (x1 - x0) * 0.7, c.warm, 0.4);
      for (let k = 0; k < 5; k++) g.dot(xm, L.Y(0.3 + 0.1 * k), 4, "#f0a92b", 0.9);
      neutrons(g, S, x0 + 14, x1 - 14, cy0 + 6, cy1 - 6, 20, dt, true);
      lab(phone ? "solid metal core" : "solid core, no pumps, no water", xm, cy1 + (phone ? 14 : 18), { color: c.ink, weight: 600 });
      lab(phone ? "heat pipes" : "sodium heat pipes carry the heat", (x1 + L.tb.x0) / 2, L.Y(0.82), { color: "#f0a92b" });
    },
    rpool(g, S, L, t, phone, fs, dt, snap, lab) {
      const { c, ctx } = g, x0 = L.X(0.06), x1 = L.X(0.5), y0 = L.Y(0.0), y1 = L.Y(1.0), xm = (x0 + x1) / 2, cy0 = lerp(y0, y1, 0.72), cy1 = lerp(y0, y1, 0.92);
      box(g, x0, y0, x1, y1, 6, null, c.soft, 0.85);
      ctx.save(); rr(ctx, x0 + 3, y0 + 10, x1 - x0 - 6, y1 - y0 - 13, 4); ctx.clip();
      const wg = ctx.createLinearGradient(0, y0, 0, y1); wg.addColorStop(0, g.rgba(c.cool, 0.12)); wg.addColorStop(1, g.rgba(c.cool, 0.32)); ctx.fillStyle = wg; ctx.fillRect(x0, y0, x1 - x0, y1 - y0);
      const pulse = snap ? 0.6 : Math.exp(-(((S.time % 7) - 1) ** 2) * 6);
      cherenkov(g, xm, (cy0 + cy1) / 2, (x1 - x0) * (0.3 + 0.35 * pulse), 0.5 + 0.5 * pulse);
      fuelCol(g, xm - (x1 - x0) * 0.12, xm + (x1 - x0) * 0.12, cy0, cy1, 6, 1, 0.3);
      neutrons(g, S, xm - (x1 - x0) * 0.13, xm + (x1 - x0) * 0.13, cy0, cy1, 20, dt);
      for (let i = 0; i < 3; i++) g.line(xm - (x1 - x0) * 0.08 + i * (x1 - x0) * 0.08, y0 + 12, xm - (x1 - x0) * 0.08 + i * (x1 - x0) * 0.08, cy0 - 4, c.ink, 2, 0.4);
      ctx.restore();
      lab(phone ? "open pool, ~7 m deep" : "open pool of water, about 7 m deep", xm, y0 - 10, { color: c.cool, weight: 600 });
      lab(phone ? "the blue glow: Cherenkov light" : "the blue glow is Cherenkov light", xm, cy0 - 26, { color: c.ink });
      if (pulse > 0.4) lab(phone ? "pulse!" : "pulse: a burst, then the hot fuel stops it", xm, cy1 + 22, { color: c.accent, weight: 600 });
    },
    ads(g, S, L, t, phone, fs, dt, snap, lab) {
      const { c, ctx } = g, x0 = L.X(0.03), x1 = L.X(0.33), y0 = L.Y(0.15), y1 = L.Y(1.0), xm = (x0 + x1) / 2, cy0 = lerp(y0, y1, 0.5), cy1 = lerp(y0, y1, 0.85);
      box(g, x0, y0, x1, y1, 10, g.rgba("#8d98a8", 0.25), c.soft, 0.85);
      ctx.save(); rr(ctx, x0, y0, x1 - x0, y1 - y0, 10); ctx.clip();
      fuelCol(g, xm - (x1 - x0) * 0.25, xm + (x1 - x0) * 0.25, cy0, cy1, 6, 0.6, 0.38);
      g.glow(xm, (cy0 + cy1) / 2, (x1 - x0) * 0.5, c.warm, 0.3);
      neutrons(g, S, xm - (x1 - x0) * 0.25, xm + (x1 - x0) * 0.25, cy0, cy1, 40, dt, true);
      ctx.restore();
      // the accelerator: a long beam line from the right, bending down into the target in the core
      const ay = L.Y(0.05), ax1 = L.X(0.96);
      box(g, L.X(0.45), ay - 12, ax1, ay + 12, 10, g.rgba(c.accent, 0.12), c.soft, 0.7);
      g.poly([[L.X(0.45), ay], [xm + 20, ay], [xm, ay + 20], [xm, (cy0 + cy1) / 2]], c.accent, 3, 0.7);
      for (let i = 0; i < 8; i++) { const u = (S.time * 0.8 + i / 8) % 1, p = mkPath([[ax1, ay], [xm + 20, ay], [xm, ay + 20], [xm, (cy0 + cy1) / 2]]), [x, y] = at(p, u * 0.999); g.glow(x, y, 7, c.proton, 0.6); g.dot(x, y, 2.2, c.proton, 1); }
      g.glow(xm, (cy0 + cy1) / 2, 22, "#ffffff", 0.5 + 0.3 * Math.sin(S.time * 9));
      lab(phone ? "proton accelerator" : "proton accelerator (linac)", (L.X(0.45) + ax1) / 2, ay + 26, { color: c.accent, weight: 600 });
      lab(phone ? "beam off: chain stops" : "subcritical core: switch the beam off and the chain stops", L.X(0.66), L.Y(0.55), { color: c.ink, weight: 600 });
      lab(phone ? "spallation target" : "spallation target: each proton chips out many neutrons", L.X(0.62), (cy0 + cy1) / 2 + 30, { color: c.soft });
      lab(phone ? "lead-bismuth" : "lead-bismuth coolant", xm, y1 + (phone ? 12 : 16), { color: "#8d98a8" });
    },
  };

  function drawOklo(g, S, phone, fs, snap, dt) {
    const { W, H, c, ctx } = g, y0 = H * 0.12, y1 = H * 0.66, seamY = lerp(y0, y1, 0.62);
    const strata = ["#8a6b4a", "#a2805a", "#6e5a46", "#937352"];
    strata.forEach((k, i) => { const a = lerp(y0, y1, i / 4), b = lerp(y0, y1, (i + 1) / 4); g.area([[0, a + Math.sin(i) * 6], [W, a - 6], [W, b - 6], [0, b + Math.sin(i + 1) * 6]], k, 0.35); });
    // the ore seam
    g.area([[W * 0.05, seamY - 10], [W * 0.95, seamY - 18], [W * 0.95, seamY + 12], [W * 0.05, seamY + 16]], "#3b3a33", 0.6);
    const cyc = snap ? 0.3 : (S.time % 9) / 9, on = cyc < 0.35, heat = on ? smooth(0, 0.08, cyc) : 1 - smooth(0.35, 0.55, cyc);
    const wx = W * 0.5;
    g.glow(wx, seamY, W * 0.18, c.warm, 0.45 * heat);
    // groundwater seeping down into the seam; boiled off when the zone gets hot
    for (let i = 0; i < 40; i++) { const q = S.inner[i], u = (q.s + S.time * 0.12) % 1, x = lerp(W * 0.2, W * 0.8, q.x), y = lerp(y0, seamY, u); if (heat > 0.5 && u > 0.6) continue; g.dot(x, y, 2, c.cool, 0.7); }
    if (heat > 0.3) for (let i = 0; i < 16; i++) { const q = S.inner[40 + i], u = (q.s + S.time * 0.5) % 1; g.ring(lerp(W * 0.38, W * 0.62, q.x), lerp(seamY, y0, u), 2 + 3 * u, c.ink, 1, 0.5 * (1 - u) * heat); }
    if (heat > 0.05) neutrons(g, S, W * 0.38, W * 0.62, seamY - 12, seamY + 12, Math.round(30 * heat), dt);
    g.label(phone ? "uranium ore, 3 % U-235" : "uranium ore when it still held 3 % U-235", W * 0.5, seamY + 34, { color: c.ink, size: fs, weight: 600, bg: true });
    g.label(on ? (phone ? "water in: chain runs ~30 min" : "water fills the cracks: the chain runs for about 30 minutes") : (phone ? "water boiled off: off ~2.5 h" : "the heat boils the water away: it stops for about 2.5 hours"), W * 0.5, y0 - 2, { color: on ? c.warm : c.cool, size: fs, weight: 600, bg: true });
  }

  function readouts(g, S, t, phone, fs) {
    const { W, H, c } = g, y = H * (phone ? 0.79 : 0.78), big = { color: c.ink, size: fs + (phone ? 3 : 6), weight: 600, serif: true };
    const cells = [];
    if (t.core === "oklo") { cells.push(["neutrons", "thermal"], ["moderator", "water"], ["power", "~100 kW"]); }
    else {
      cells.push([phone ? "outlet" : "coolant out", `${t.tout} °C`]);
      cells.push(["pressure", t.p <= 1 ? (phone ? "~1 bar" : "~1 bar (unpressurized)") : `${t.p} bar`]);
      cells.push(["electricity", t.eff ? `${t.eff} %` : (phone ? "none" : "none made")]);
    }
    cells.forEach(([k, v], i) => { const x = W * (0.2 + 0.3 * i); g.label(v, x, y, big); g.label(k, x, y + fs + 10, { color: c.soft, size: fs - 1 }); });
    const line = `${t.spec === "fast" ? (phone ? "fast" : "fast neutrons") : (phone ? "thermal" : "thermal neutrons")} · ${phone ? "mod." : "moderator"}: ${t.mod} · ${phone ? "cool." : "coolant"}: ${t.cool}`;
    if (t.core !== "oklo") g.label(line, W / 2, y + fs * 2 + 22, { color: c.soft, size: fs - 1 });
    g.label(t.ex, W / 2, y + fs * 3 + 30, { color: c.faint, size: fs - 1, serif: true, italic: true });
    if (!phone) g.label(t.ab, W * 0.03, H * 0.04, { color: c.accent, size: fs + 2, weight: 700, align: "left" });
    g.label("illustration", W - 6, H - 10, { color: c.faint, size: 10, align: "right" });
  }

  // ---------- the four type lessons ----------
  function typeLesson(id, level, title, short, lead, list) {
    list.forEach(([k], i) => (HOME[k] = `${id}-${i + 1}`));
    WT.chapter(id, {
      level, num: "Lesson 1", title, short, lead,
      html: list.map(([k, h, p]) => `
<div class="step">
  <h3>${h}</h3>
  <p>${p}</p>
</div>`).join(""),
      setup(S) { S.ty = null; setType(S, list[0][0]); },
      steps: list.map(([k]) => (S) => setType(S, k)),
      frame(g, S, dt) { drawPlant(g, S, dt); },
    });
  }

  typeLesson("rwater", 0, "Water-cooled reactors", "Water reactors", "Almost every power reactor today is cooled by water. They differ in how the water carries the heat out.", [
    ["pwr", "Pressurized water (PWR)", "Water under high pressure carries the heat to a steam generator; a second loop makes the steam."],
    ["bwr", "Boiling water (BWR)", "The water boils in the core itself and the steam goes straight to the turbine: one loop."],
    ["phwr", "Heavy water (CANDU)", "Heavy water slows neutrons without soaking many up, so natural uranium is enough."],
    ["rbmk", "Graphite and boiling water (RBMK)", "Graphite slows the neutrons; water boils in hundreds of separate tubes."],
    ["smr", "Small modular (SMR)", "A small PWR with everything in one vessel, built in a factory."],
    ["scwr", "Supercritical water (SCWR)", "Above 221 bar water never boils, so it can run hotter and turn more heat into electricity."],
  ]);
  typeLesson("rgas", 1, "Gas-cooled reactors", "Gas reactors", "Gas cannot boil, so these reactors run hot. Graphite slows the neutrons.", [
    ["magnox", "Magnox", "The first power reactors: natural uranium metal, graphite, and CO₂ gas."],
    ["agr", "Advanced gas-cooled (AGR)", "Enriched fuel in steel cans lets the gas leave at 640 °C."],
    ["htgr", "Pebble bed (HTGR)", "Fuel in graphite pebbles, cooled by helium. The fuel survives over 1,600 °C."],
    ["vhtr", "Very high temperature (VHTR)", "Helium at 950 °C: hot enough for a gas turbine, or to make hydrogen."],
  ]);
  typeLesson("rfast", 2, "Fast reactors", "Fast reactors", "No moderator: the neutrons stay fast, so the reactor can breed new fuel and burn long-lived waste.", [
    ["sfr", "Sodium-cooled (SFR)", "Liquid sodium carries heat well without pressure. A middle sodium loop keeps it away from water."],
    ["lfr", "Lead-cooled (LFR)", "Lead boils only at 1,750 °C and does not burn in air or water."],
    ["gfr", "Gas-cooled fast (GFR)", "Helium with dense fuel and no graphite: hot and fast."],
  ]);
  typeLesson("rother", 2, "Molten salt and other reactors", "Salt and others", "Liquid fuel, tiny reactors, reactors with no electricity, and one nature built.", [
    ["msr", "Molten salt (MSR)", "The fuel is dissolved in hot salt that flows through the core."],
    ["micro", "Microreactor", "A few kilowatts to a few megawatts, with no pumps: heat pipes carry the heat."],
    ["triga", "Research pool (TRIGA)", "A small core in an open pool, built for neutrons, not electricity."],
    ["ads", "Accelerator-driven (ADS)", "The core cannot sustain a chain on its own; a proton beam supplies the missing neutrons."],
    ["oklo", "Natural reactor (Oklo)", "Two billion years ago, a uranium deposit in Gabon went critical by itself."],
  ]);

  // ---------- comparing them all ----------
  const ROWS = [["water", ["pwr", "smr", "triga", "oklo"], ["phwr"], [], []], ["boiling water", ["bwr"], [], ["rbmk"], []], ["supercritical water", ["scwr"], [], [], []],
    ["gas", [], [], ["magnox", "agr", "htgr", "vhtr"], ["gfr"]], ["liquid metal", [], [], [], ["sfr", "lfr", "ads", "micro"]], ["molten salt", [], [], ["msr"], []]];
  const COLS = ["light water", "heavy water", "graphite", "none (fast)"];
  const ROWS_PH = ["water", "boiling", "supercrit.", "gas", "liquid metal", "salt"];
  // label offsets in the temperature chart, where the water reactors crowd together
  const LOFF = { bwr: [-9, -10, "right"], pwr: [9, -10, "left"], smr: [9, 11, "left"], phwr: [0, 17, "center"], rbmk: [-9, 11, "right"], lfr: [-9, 11, "right"], sfr: [9, 11, "left"] };
  const FLEET = [["PWR", 0.7, "pwr"], ["BWR", 0.15, "bwr"], ["PHWR", 0.1, "phwr"], ["others", 0.05, null]];
  WT.chapter("rcompare", {
    level: 1, num: "Lesson 1", title: "Reactor types compared", short: "Compared", lead: "Every reactor is a choice of moderator and coolant.",
    html: `
<div class="step">
  <h3>Moderator and coolant</h3>
  <p>Pick what slows the neutrons and what carries the heat. Tap a type to visit it.</p>
</div>
<div class="step">
  <h3>Hotter is better</h3>
  <p>The hotter the coolant leaves the core, the more of the heat can become electricity.</p>
</div>
<div class="step">
  <h3>What runs today</h3>
  <p>Most of the world's reactors are the first three water-cooled types.</p>
</div>`,
    setup(S) { S.set("mode", "grid"); S.hot = null; S.k = 1; },
    steps: [(S) => S.set("mode", "grid"), (S) => S.set("mode", "temp"), (S) => S.set("mode", "fleet")],
    frame(g, S, dt) {
      const { W, H, c, ctx } = g, phone = W < 600, fs = phone ? 11 : 13, hits = [];
      const go = (k) => { const h = HOME[k]; if (!h) return; const el = document.getElementById(h); if (el) { history.replaceState(null, "", location.pathname + location.search + "#" + h); el.scrollIntoView({ behavior: "smooth", block: "center" }); } };
      if (S.mode === "grid") {
        const x0 = W * (phone ? 0.24 : 0.2), x1 = W * 0.97, y0 = H * 0.14, y1 = H * 0.86, cw = (x1 - x0) / COLS.length, rh = (y1 - y0) / ROWS.length;
        g.label(phone ? "slows the neutrons →" : "what slows the neutrons (moderator) →", (x0 + x1) / 2, H * 0.05, { color: c.soft, size: fs });
        g.label(phone ? "carries the heat ↓" : "what carries the heat ↓", W * 0.02, H * 0.05, { color: c.soft, size: fs, align: "left" });
        COLS.forEach((k, j) => g.label(phone && j === 3 ? "none" : k,x0 + cw * (j + 0.5), y0 - (phone ? 10 : 14), { color: c.ink, size: fs - 1, weight: 600 }));
        ROWS.forEach(([name, ...cells], i) => {
          const y = y0 + rh * (i + 0.5); g.line(W * 0.02, y0 + rh * i, x1, y0 + rh * i, c.soft, 1, 0.2);
          g.label(phone ? ROWS_PH[i] : name, W * 0.02, y, { color: c.ink, size: fs - 1, weight: 600, align: "left" });
          // chips sized to their (translated) text, two per row, centred in the cell and kept inside the drawing
          const fsz = phone ? 9 : fs - 1; ctx.save(); ctx.font = `600 ${fsz}px ${getComputedStyle(document.documentElement).getPropertyValue("--sans") || "sans-serif"}`;
          const cw2 = cells.map((list) => list.map((k) => Math.max(cw * (phone ? 0.4 : 0.36), ctx.measureText(WT.tr ? WT.tr(TY[k].ab) : TY[k].ab).width + (phone ? 10 : 16)))); ctx.restore();
          cells.forEach((list, j) => list.forEach((k, m) => {
            const per = 2, col2 = m % per, row2 = Math.floor(m / per), nrow = Math.ceil(list.length / per), r0 = row2 * per, rowK = list.slice(r0, r0 + per), ws = cw2[j].slice(r0, r0 + per);
            const tot = ws.reduce((a2, b2) => a2 + b2, 0) + 4 * (ws.length - 1); let left = x0 + cw * (j + 0.5) - tot / 2; left = Math.min(left, W - 4 - tot);
            const w = ws[col2], x = left + ws.slice(0, col2).reduce((a2, b2) => a2 + b2 + 4, 0) + w / 2, yy = y + (row2 - (nrow - 1) / 2) * rh * 0.42, t = TY[k], hov = S.hot === k;
            const fast = t.spec === "fast", h = Math.min(rh * 0.36, 30);
            ctx.save(); rr(ctx, x - w / 2, yy - h / 2, w, h, 8); ctx.fillStyle = g.rgba(fast ? c.warm : c.cool, hov ? 0.4 : 0.18); ctx.fill(); ctx.strokeStyle = g.rgba(fast ? c.warm : c.cool, 0.8); ctx.lineWidth = hov ? 2.2 : 1.2; ctx.stroke(); ctx.restore();
            g.label(t.ab, x, yy, { color: c.ink, size: fsz, weight: 600 });
            hits.push([x - w / 2, yy - h / 2, w, h, k]);
          }));
        });
        g.line(W * 0.02, y1, x1, y1, c.soft, 1, 0.2);
        g.dot(W * 0.3, H * 0.94, 5, c.cool, 0.8); g.label("thermal", W * 0.3 + 10, H * 0.94, { color: c.soft, size: fs - 1, align: "left" });
        g.dot(W * 0.55, H * 0.94, 5, c.warm, 0.8); g.label("fast", W * 0.55 + 10, H * 0.94, { color: c.soft, size: fs - 1, align: "left" });
      } else if (S.mode === "temp") {
        const x0 = W * 0.12, x1 = W * 0.95, y0 = H * 0.1, y1 = H * 0.8, T0 = 200, T1 = 1000, E0 = 20, E1 = 80;
        const X = (T) => lerp(x0, x1, (T - T0) / (T1 - T0)), Y = (e) => lerp(y1, y0, (e - E0) / (E1 - E0));
        g.line(x0, y1, x1, y1, c.soft, 1.2, 0.6); g.line(x0, y1, x0, y0, c.soft, 1.2, 0.6);
        for (let T = 200; T <= 1000; T += 200) g.label(`${T} °C`, X(T), y1 + 16, { color: c.soft, size: fs - 2 });
        for (let e = 20; e <= 80; e += 10) g.label(`${e} %`, x0 - 8, Y(e), { color: c.soft, size: fs - 2, align: "right" });
        g.label(phone ? "coolant out →" : "coolant temperature leaving the core →", (x0 + x1) / 2, y1 + 36, { color: c.soft, size: fs - 1 });
        g.label(phone ? "↑ electricity" : "↑ share of heat turned into electricity", x0 + 4, y0 - 8, { color: c.soft, size: fs - 1, align: "left" });
        // Carnot limit with 30 C cooling water: 1 - Tc/Th
        const pts = []; for (let T = T0; T <= T1; T += 10) { const e = 100 * (1 - 303 / (T + 273)); if (e <= E1) pts.push([X(T), Y(e)]); }
        g.poly(pts, c.accent, 2, 0.6, [6, 5]); if (pts.length) g.label(phone ? "ideal limit" : "ideal (Carnot) limit", pts[pts.length - 1][0] - 8, pts[pts.length - 1][1] - 14, { color: c.accent, size: fs - 1, align: "right" });
        Object.keys(TY).forEach((k) => { const t = TY[k]; if (!t.eff) return; const x = X(t.tout), y = Y(t.eff), hov = S.hot === k, fast = t.spec === "fast";
          g.glow(x, y, hov ? 26 : 16, fast ? c.warm : c.cool, 0.4); g.dot(x, y, hov ? 7 : 5, fast ? c.warm : c.cool, 0.95);
          const [dx, dy, al] = LOFF[k] || [9, -9, "left"];
          g.label(t.ab, x + dx, y + dy, { color: hov ? c.ink : c.soft, size: fs - 1, weight: hov ? 700 : 500, align: al }); hits.push([x - 14, y - 14, 28, 28, k]); });
        if (S.hot && TY[S.hot].eff) { const t = TY[S.hot]; g.label(`${t.n}: ${t.tout} °C, ${t.eff} %`, W / 2, H * 0.92, { color: c.ink, size: fs, weight: 600, bg: true }); }
      } else {
        const x0 = W * 0.06, x1 = W * 0.94, y = H * 0.4, h = H * 0.12; let x = x0;
        g.label(phone ? "the world's power reactors" : "the world's power reactors, by type (rounded)", W / 2, y - h - 16, { color: c.soft, size: fs });
        FLEET.forEach(([name, f, k], i) => { const w = (x1 - x0) * f, hov = S.hot === k && k, colr = [c.cool, "#7fb8ff", "#2bb3a3", c.warm][i];
          ctx.save(); ctx.fillStyle = g.rgba(colr, hov ? 0.75 : 0.5); ctx.fillRect(x + 1, y - h / 2, w - 2, h); ctx.restore();
          if (w > 40) { g.label(name, x + w / 2, y - 8, { color: c.ink, size: fs, weight: 700 }); g.label(`~${Math.round(f * 100)} %`, x + w / 2, y + 12, { color: c.ink, size: fs - 1 }); }
          else { g.label(`${name} ~${Math.round(f * 100)} %`, x + w / 2, y + h / 2 + 18 + (i % 2) * 16, { color: c.soft, size: fs - 1 }); }
          if (k) hits.push([x, y - h / 2, w, h, k]); x += w; });
        g.label(phone ? "others: gas, graphite, fast, HTGR" : "others: AGR, RBMK, fast reactors, HTR-PM", W / 2, y + h / 2 + 60, { color: c.soft, size: fs - 1 });
        g.label(phone ? "about 420 reactors in all" : "about 420 power reactors in operation", W / 2, H * 0.78, { color: c.ink, size: fs + 3, weight: 600, serif: true });
      }
      const hit = (x, y) => { for (const [a, b, w, h, k] of hits) if (x >= a && x <= a + w && y >= b && y <= b + h) return k; return null; };
      WT.grab(ctx.canvas, {
        down(x, y) { const k = hit(x, y); if (k) { go(k); } return false; },
        hover(x, y) { const k = hit(x, y); S.hot = k; ctx.canvas.style.cursor = k ? "pointer" : "default"; },
      });
      g.label("illustration", W - 6, H - 10, { color: c.faint, size: 10, align: "right" });
    },
  });
})();
