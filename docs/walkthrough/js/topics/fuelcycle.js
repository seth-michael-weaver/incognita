/* The fuel cycle: from mine to waste, followed for ONE TONNE of enriched uranium fuel (civilian power reactors, light water).
 * A strip across the top is the whole chain (mine, mill, conversion, enrichment, fabrication, reactor, storage, end);
 * its band is a Sankey of uranium mass (linear: natural uranium in, fuel and tails out), with the tonnes under each station.
 * Tap a station to go to its step. Scenes (S.mode):
 *   "mine"   = ore needed for one tonne of fuel at a chosen ore grade (% U by mass), drawn in 100-tonne blocks, and 1000
 *              uranium atoms of which 7 are U-235. Natural uranium: 0.711 % U-235 by mass (0.720 % of atoms). Ore grades: most
 *              mines average more than 0.10 % U; some work ore down to about 0.02 % U; some Canadian mines up to 20 % U average
 *              (World Nuclear Association, "Uranium Mining Overview"; OECD-NEA/IAEA "Uranium: Resources, Production and Demand"
 *              (the Red Book)). Ore tonnes = natural U needed / grade (losses in mining and milling left out, so a minimum).
 *              U3O8 (yellowcake) holds 0.848 kg U per kg (1.179 kg U3O8 per kg U); UF6 holds 0.676 kg U per kg (1.479 kg UF6
 *              per kg U): molar masses.
 *   "enrich" = the enrichment mass balance. Feed F, product P, tails T with assays xf, xp, xt (mass fractions of U-235):
 *              F = P + T and F xf = P xp + T xt, so F / P = (xp - xt) / (xf - xt). Separative work per kg of product:
 *              SWU = V(xp) + (T/P) V(xt) - (F/P) V(xf), V(x) = (2x - 1) ln(x / (1 - x)). Check against WNA "Uranium
 *              Enrichment": 5 % product, 0.25 % tails: 7.9 SWU and 10.3 kg feed (WNA quotes 7.9 SWU, 10.4 kg); 0.20 % tails:
 *              8.9 SWU and 9.4 kg (WNA: 8.9 SWU, 9.4 kg). Power-reactor fuel 3-5 % U-235 (5 % the usual maximum); tails
 *              0.18-0.22 % in Western plants, 0.25-0.30 % in older practice (WNA). Each dot in the bands is one uranium atom;
 *              the share of U-235 dots is the true assay.
 *   "fab"    = fabrication: 1 t U = 1.134 t UO2 (molar masses). A pellet ~5.5 g UO2 (4.85 g U), ~350 pellets per ~4 m rod,
 *              264 fuel rods per 17x17 assembly (Westinghouse layout; as in the "reactor" lesson): about 206 000 pellets,
 *              590 rods, 2.2 assemblies per tonne of uranium. Slider up to 27 t: "some 27 tonnes of fresh enriched fuel
 *              is required each year by a 1000 MWe reactor" (WNA "Nuclear Fuel Cycle Overview").
 *   "core"   = one tonne in the core against burnup (GWd/t). Composition per tonne (kg), ILLUSTRATIVE fit matching the
 *              "burnup" lesson's depletion model and the usual figures (4.5 % fuel at ~50 GWd/t ends with ~0.7-1 % U-235,
 *              ~1 % Pu, ~5 % fission products, ~0.1 % minor actinides: WNA "Nuclear Fuel Cycle Overview"; OECD-NEA 2011
 *              No. 6894): U-235 = U0 exp(-B / tau), tau = 27.7 GWd/t x (xp / 4.5 %); Pu = 13 (1 - exp(-B / 25));
 *              fission products = 1.05 kg per GWd/t (200 MeV per fission: 1 GWd = 8.64e13 J = 2.7e24 fissions = 1.05 kg
 *              of heavy atoms); minor actinides 0.02 kg per GWd/t; U-238 (with U-236) the rest. Each square is 1 kg.
 *              Electricity = B GWd x 24 h x 0.33 (a third of the heat, as in the "reactor" lesson). Typical discharge
 *              45-55 GWd/t (WNA). Fuel stays in the core three to six years (WNA).
 *   "after"  = storage and the two routes. Pools: at least five years, then often dry casks (designs for up to 100 years)
 *              (WNA "Storage and Disposal of Radioactive Waste"); mined repositories 250-1000 m deep (Finland's at ~400 m,
 *              Sweden's KBS-3 ~500 m). Once-through: the whole tonne is disposed of. Reprocessing (WNA "Processing of Used
 *              Nuclear Fuel", "Mixed Oxide Fuel"): uranium (~94-96 %) and plutonium (~1 %) separated; MOX averages ~9.5 % Pu,
 *              so MOX mass = Pu / 0.095 (WNA: seven used assemblies give about one MOX assembly); fission products and minor
 *              actinides vitrified: about 5 t of glass per ~27 t of fuel a year from a 1000 MWe reactor, i.e. ~0.2 t of glass
 *              per tonne, about half a 400 kg canister. Recycling plutonium as MOX gives ~12 % more energy from the original
 *              uranium, ~22 % with the uranium recycled too (WNA). */
(function () {
  const { TAU, clamp, lerp, smooth, rng } = WT.util;
  const XF = 0.711, U3O8 = 1.179, UF6 = 1.479, UO2 = 1.134, GLASS = 0.19, MOXPU = 0.095;
  const SNAP = () => document.body.classList.contains("shot");
  const V = (p) => { const x = p / 100; return (2 * x - 1) * Math.log(x / (1 - x)); };
  const feed = (S) => (S.xp - S.xt) / (XF - S.xt);
  const swu = (S) => { const F = feed(S); return V(S.xp) + (F - 1) * V(S.xt) - F * V(XF); };
  const gradeOf = (S) => Math.pow(10, S.lg);                               // ore grade, % U
  function comp(S) {
    const B = S.bu, u0 = 10 * S.xp, u5 = u0 * Math.exp(-B / (27.7 * S.xp / 4.5)), pu = 13 * (1 - Math.exp(-B / 25)), fp = 1.05 * B, ma = 0.02 * B;
    return { u5, pu, fp, ma, u8: 1000 - u5 - pu - fp - ma, u0, e: B * 24 * 0.33 };
  }
  // number formatting with thin thousands spaces
  const nf = (v, d = 0) => { const s = v.toFixed(d), [a, b] = s.split("."); return a.replace(/\B(?=(\d{3})+(?!\d))/g, " ") + (b ? "." + b : ""); };
  const t3 = (kg) => kg >= 9995 ? nf(kg / 1000, 0) : kg >= 995 ? nf(kg / 1000, 1) : nf(kg / 1000, 2);
  const sig2 = (t) => { const p = Math.pow(10, Math.floor(Math.log10(t)) - 1); const v = Math.round(t / p) * p; return v >= 100 ? nf(v) : v >= 10 ? nf(v, 0) : v.toFixed(1); }; // tonnes, two significant figures

  const STN = [
    { lab: "Mine", s: 0 }, { lab: "Mill", s: 0 }, { lab: "Convert", s: 1 }, { lab: "Enrich", s: 1 },
    { lab: "Fabricate", s: 2 }, { lab: "Reactor", s: 3 }, { lab: "Pool · cask", ph: "Store", s: 4 }, { lab: "Disposal", ph: "End", s: 4 },
  ];
  const r = rng(17);
  // particles: strip band, enrichment bands, after-reactor bands
  const SP = []; for (let i = 0; i < 70; i++) SP.push({ u: r(), v: r() - 0.5, q: r() });
  const EP = []; for (let i = 0; i < 1500; i++) EP.push({ u: r(), v: r() - 0.5, q: r(), b: 0 });
  const AP = []; for (let i = 0; i < 260; i++) AP.push({ u: r(), v: r() - 0.5, q: r() });
  const PERM = []; { const q = rng(9); for (let i = 0; i < 1000; i++) PERM.push(i); for (let i = 999; i > 0; i--) { const j = Math.floor(q() * (i + 1)); [PERM[i], PERM[j]] = [PERM[j], PERM[i]]; } }
  // guide tube positions in a 17x17 Westinghouse assembly (row, col), as in reactor.js; (8,8) is the instrument tube
  const GTS = new Set([[2, 5], [2, 8], [2, 11], [3, 3], [3, 13], [5, 2], [5, 5], [5, 8], [5, 11], [5, 14], [8, 2], [8, 5], [8, 8], [8, 11], [8, 14], [11, 2], [11, 5], [11, 8], [11, 11], [11, 14], [13, 3], [13, 13], [14, 5], [14, 8], [14, 11]].map(([a, b]) => a * 17 + b));
  const cellT = new Float32Array(1000).fill(-9), cellK = new Int8Array(1000).fill(-1);
  const ROCK = []; { const q = rng(3); for (let i = 0; i < 520; i++) ROCK.push([q(), q(), q(), q()]); }

  const geo = { stn: [], bar: null };
  function syncInputs(k, v) { document.querySelectorAll(`#fuelcycle [data-bind="${k}"]`).forEach((i) => (i.value = v)); }
  function grabSetup(cv, S) {
    let drag = null;
    const setG = (x) => { const b = geo.bar; if (!b) return; const v = clamp(lerp(-1.7, 1.3, (x - b.x0) / (b.x1 - b.x0)), -1.7, 1.3); S.set("lg", v); syncInputs("lg", v); };
    const setB = (x) => { const b = geo.bbar; if (!b) return; const v = Math.round(clamp((x - b.x0) / (b.x1 - b.x0) * 60, 0, 60)); S.set("bu", v); syncInputs("bu", v); };
    const onStn = (x, y) => geo.stn.find((s) => Math.abs(x - s.x) < s.hw && Math.abs(y - s.y) < 26);
    WT.grab(cv, {
      down(x, y) {
        const s = onStn(x, y);
        if (s) { const t = document.getElementById("fuelcycle-" + (STN[s.i].s + 1)); if (t) { const PH = window.matchMedia("(max-width: 860px)").matches; window.scrollTo({ top: t.getBoundingClientRect().top + scrollY - innerHeight * (PH ? 0.5 : 0.38), behavior: "smooth" }); } return false; }
        if (S.mode === "mine" && geo.bar && Math.abs(y - geo.bar.y) < 24 && x > geo.bar.x0 - 12 && x < geo.bar.x1 + 12) { drag = "g"; setG(x); return true; }
        if (S.mode === "core" && geo.bbar && Math.abs(y - geo.bbar.y) < 24 && x > geo.bbar.x0 - 12 && x < geo.bbar.x1 + 12) { drag = "b"; setB(x); return true; }
        return false;
      },
      move(x) { if (drag === "g") setG(x); else if (drag === "b") setB(x); },
      up() { drag = null; }, cancel() { drag = null; },
      hover(x, y) {
        cv.style.cursor = onStn(x, y) ? "pointer"
          : S.mode === "mine" && geo.bar && Math.abs(y - geo.bar.y) < 24 && x > geo.bar.x0 - 12 && x < geo.bar.x1 + 12 ? "ew-resize"
          : S.mode === "core" && geo.bbar && Math.abs(y - geo.bbar.y) < 24 && x > geo.bbar.x0 - 12 && x < geo.bbar.x1 + 12 ? "ew-resize" : "";
      },
    });
  }
  function setRoute(S, k) { S.set("route", k); S.to("rt", k === "R" ? 1 : 0); document.querySelectorAll('#fuelcycle [data-act^="fr"]').forEach((b) => b.setAttribute("aria-pressed", String(b.dataset.act === "fr" + k))); }

  WT.chapter("fuelcycle", {
    level: 0, num: "Lesson 1", title: "The fuel cycle", short: "Fuel cycle",
    html: `
<div class="step">
  <h3>Digging up uranium</h3>
  <p>Ore is mostly rock, and only 0.7 % of the uranium in it is uranium-235, the kind that splits easily.</p>
  <div class="ctl"><label for="fc-g">Ore grade (% uranium)</label><input id="fc-g" type="range" data-bind="lg" data-instant min="-1.7" max="1.3" step="0.01" value="-1"></div>
</div>
<div class="step">
  <h3>Enrichment is a mass balance</h3>
  <p>As a gas, the uranium is split into a small stream richer in uranium-235, the fuel, and a large depleted one, the tails.</p>
  <div class="ctl"><label for="fc-p">Fuel enrichment (% U-235)</label><input id="fc-p" type="range" data-bind="xp" data-instant min="3" max="5" step="0.05" value="4.5"><output data-show="xp" data-fmt="2"></output></div>
  <div class="ctl"><label for="fc-t">Tails (% U-235)</label><input id="fc-t" type="range" data-bind="xt" data-instant min="0.15" max="0.35" step="0.01" value="0.25"><output data-show="xt" data-fmt="2"></output></div>
</div>
<div class="step">
  <h3>Pellets, rods, assemblies</h3>
  <p>The enriched uranium is baked into ceramic pellets, sealed in rods and bundled into assemblies; <a href="#reactor">the next lesson</a> follows them into the core.</p>
  <div class="ctl"><label for="fc-f">Fuel (tonnes of uranium)</label><input id="fc-f" type="range" data-bind="ft" data-instant min="1" max="27" step="1" value="1"><output data-show="ft" data-fmt="0"></output></div>
</div>
<div class="step">
  <h3>Years in the core</h3>
  <p>Over three to six years a few percent of the heavy atoms split, leaving fission products and some new plutonium (<a href="#burnup">burnup</a>).</p>
  <div class="ctl"><label for="fc-b">Burnup (GWd per tonne)</label><input id="fc-b" type="range" data-bind="bu" data-instant min="0" max="60" step="1" value="50"><output data-show="bu" data-fmt="0"></output></div>
</div>
<div class="step">
  <h3>Cooling, then two routes</h3>
  <p>Used fuel cools in a pool and then in dry casks; afterwards it is either buried deep as it is, or reprocessed so its uranium and plutonium are used again (<a href="#waste">spent fuel</a>, <a href="#breeding">breeding</a>).</p>
  <div class="btns"><button class="btn ghost" data-act="frO" aria-pressed="true">Once-through</button> <button class="btn ghost" data-act="frR" aria-pressed="false">Reprocess</button></div>
</div>`,
    setup(S) {
      S.set("mode", "mine"); S.set("lg", -1); S.set("xp", 4.5); S.set("xt", 0.25); S.set("bu", 50); S.set("ft", 1); S.set("route", "O"); S.set("rt", 0); S.set("hi", 0);
      S.on("frO", () => setRoute(S, "O")); S.on("frR", () => setRoute(S, "R"));
    },
    steps: [
      (S) => { S.set("mode", "mine"); S.set("hi", 0); },
      (S) => { S.set("mode", "enrich"); S.set("hi", 1); },
      (S) => { S.set("mode", "fab"); S.set("hi", 2); S.fab0 = S.time; if (SNAP()) S.set("ft", 27); },
      (S) => { S.set("mode", "core"); S.set("hi", 3); },
      (S) => { S.set("mode", "after"); S.set("hi", 4); setRoute(S, SNAP() && !/[?&]route=O/.test(location.search) ? "R" : S.route); }, // shots show reprocessing (dev aid: &route=O)
    ],
    frame(g, S, dt) {
      const { W, H, c } = g, phone = W < 600, fs = phone ? 11 : 13, snap = SNAP();
      if (!S.grabbed) { S.grabbed = true; grabSetup(g.ctx.canvas, S); }
      const top = drawStrip(g, S, dt, phone, fs, snap);
      const box = { x: W * 0.03, y: top, w: W * 0.94, h: H - top - (phone ? 6 : 14) };
      if (S.mode === "mine") drawMine(g, S, box, phone, fs);
      else if (S.mode === "enrich") drawEnrich(g, S, dt, box, phone, fs, snap);
      else if (S.mode === "fab") drawFab(g, S, box, phone, fs, snap);
      else if (S.mode === "core") drawCore(g, S, box, phone, fs, snap);
      else drawAfter(g, S, dt, box, phone, fs, snap);
      g.label("illustration", W - 6, H - 8, { color: c.faint, size: 10, align: "right" });
    },
  });

  // ---------- helpers: a Sankey band between two points with horizontal tangents ----------
  function bandPt(b, t) { const s = t * t * (3 - 2 * t); return [lerp(b.x0, b.x1, t), lerp(b.y0, b.y1, s), lerp(b.w0, b.w1, t)]; }
  function band(g, b, color, a0 = 0.32, a1) {
    const ctx = g.ctx, N = 40, up = [], dn = [];
    for (let i = 0; i <= N; i++) { const [x, y, w] = bandPt(b, i / N); up.push([x, y - w / 2]); dn.push([x, y + w / 2]); }
    ctx.save(); const gr = ctx.createLinearGradient(b.x0, 0, b.x1, 0); gr.addColorStop(0, g.rgba(color, a0)); gr.addColorStop(1, g.rgba(color, a1 ?? a0));
    ctx.fillStyle = gr; ctx.beginPath(); ctx.moveTo(up[0][0], up[0][1]); up.forEach((p) => ctx.lineTo(p[0], p[1])); for (let i = N; i >= 0; i--) ctx.lineTo(dn[i][0], dn[i][1]); ctx.closePath(); ctx.fill(); ctx.restore();
  }

  // ---------- the chain strip ----------
  function drawStrip(g, S, dt, phone, fs, snap) {
    const { W, c } = g, F = feed(S), co = comp(S);
    const x0 = W * (phone ? 0.06 : 0.05), x1 = W * (phone ? 0.94 : 0.95), n = STN.length, xs = STN.map((_, i) => lerp(x0, x1, i / (n - 1)));
    const ly = phone ? 11 : 15, yc = phone ? 32 : 44, bw = phone ? 14 : 22, wP = bw / F, wT = bw - wP;
    const hi = S.hi, act = (i) => clamp(1 - Math.abs(STN[i].s - hi) * 1.6, 0, 1);
    // uranium band: natural uranium to the enrichment plant, then the fuel; tails peel off below
    const xe = xs[3];
    band(g, { x0: xs[0], x1: xe, y0: yc, y1: yc, w0: bw, w1: bw }, c.soft, 0.22);
    band(g, { x0: xe, x1: xs[n - 1], y0: yc - bw / 2 + wP / 2, y1: yc - bw / 2 + wP / 2, w0: wP, w1: wP }, c.fission, 0.55);
    const tb = { x0: xe, x1: xe + (xs[4] - xe) * 0.85, y0: yc + bw / 2 - wT / 2, y1: yc + bw * (phone ? 0.9 : 1.1), w0: wT, w1: wT * 0.7 };
    band(g, tb, c.cool, 0.28, 0.02);
    // atoms drifting along it
    for (const p of SP) {
      p.u = (p.u + dt * 0.045) % 1; const x = lerp(x0, x1, p.u);
      let y, col = c.soft;
      if (x < xe) y = yc + p.v * bw * 0.85;
      else if (p.q < 1 / F) { y = yc - bw / 2 + wP / 2 + p.v * wP * 0.6; col = c.fission; }
      else { const t = (x - xe) / (tb.x1 - xe); if (t > 1) continue; const [bx, by, w] = bandPt(tb, t); y = by + p.v * w * 0.8; col = c.cool; g.dot(bx, y, phone ? 1.2 : 1.6, col, 0.7 * (1 - t)); continue; }
      g.dot(x, y, phone ? 1.2 : 1.6, col, 0.75);
    }
    // stations
    const ore = 1000 * F / (gradeOf(S) / 100);
    const sub = [
      phone ? `${sig2(ore / 1000)} t` : WT.trf("{a} t ore", sig2(ore / 1000)),
      phone ? `${t3(F * 1000 * U3O8)} t` : WT.trf("{a} t U₃O₈", t3(F * 1000 * U3O8)),
      phone ? `${t3(F * 1000 * UF6)} t` : WT.trf("{a} t UF₆", t3(F * 1000 * UF6)),
      phone ? "1 t" : WT.trf("1 t fuel + {a} t tails", t3((F - 1) * 1000)),
      phone ? "1 t" : WT.trf("{a} t UO₂", t3(UO2 * 1000)),
      phone ? `${nf(co.e)} GWh` : WT.trf("{a} GWh", nf(co.e)),
      phone ? "≥ 5 y" : "pool ≥ 5 years",
      S.route === "R" && hi >= 3.5 ? "recycle" : "repository",
    ];
    geo.stn = [];
    xs.forEach((x, i) => {
      const a = act(i), on = a > 0.5, stY = i < 3 ? yc : i === 3 ? yc : yc - bw / 2 + wP / 2;
      if (a > 0.05) g.glow(x, stY, (phone ? 14 : 22) * (0.6 + a), c.accent, 0.35 * a);
      g.dot(x, stY, phone ? 4 : 5, on ? c.accent : c.card, 1); g.ring(x, stY, phone ? 4 : 5, on ? c.accent : c.soft, 1.4, on ? 1 : 0.6);
      const show = !phone || on;
      if (show || phone) g.label(phone && !on ? String(i + 1) : phone && STN[i].ph ? STN[i].ph : STN[i].lab, x, ly, { color: on ? c.ink : c.soft, size: fs - (on ? 0 : 1), weight: on ? 700 : 500, raw: phone && !on, alpha: on ? 1 : 0.8 });
      if (show && !(phone && i === 3)) g.label(sub[i], x + (i === 3 && !phone ? 0 : 0), yc + bw / 2 + (phone ? 12 : 16) + (i === 3 && !phone ? 6 : 0), { color: i === 3 ? c.fission : c.soft, size: fs - 2, raw: /\d/.test(sub[i]) || phone, bg: true, alpha: on ? 1 : 0.75 });
      geo.stn.push({ i, x, y: (ly + yc) / 2, hw: Math.max(14, (x1 - x0) / (n - 1) / 2) });
    });
    if (phone && hi > 0.5 && hi < 1.5) g.label(WT.trf("1 t fuel + {a} t tails", t3((F - 1) * 1000)), xs[3], yc + bw / 2 + 12, { color: c.fission, size: fs - 2, raw: true, bg: true });
    const bot = yc + bw / 2 + (phone ? 22 : 34);
    g.line(W * 0.03, bot, W * 0.97, bot, c.line || c.faint, 1, 0.6);
    return bot + (phone ? 4 : 10);
  }

  // ---------- step 1: ore and the 0.7 % ----------
  function drawMine(g, S, b, phone, fs) {
    const { c, ctx } = g, F = feed(S), gr = gradeOf(S), ore = F / (gr / 100), blocks = ore / 100;   // ore in tonnes per tonne of fuel
    // rock blocks: one block = 100 t of ore
    const barH = phone ? 14 : 58, titleH = phone ? 18 : 26;
    const rx = b.x, rw = b.w * (phone ? 0.64 : 0.6), ry = b.y + titleH, rh = b.h - titleH - barH - (phone ? 4 : 8);
    const cols = phone ? 20 : 24, rows = Math.ceil(470 / cols), sz = Math.min(rw / cols, rh / rows), gap = Math.max(1, sz * 0.14);
    g.label(WT.trf(phone ? "ore ≈ {a} t · block = 100 t" : "ore for one tonne of fuel: ≈ {a} t  (each block 100 t)", sig2(ore)), rx, b.y + titleH * 0.4, { color: c.ink, size: fs, weight: 600, align: "left", raw: true });
    const full = Math.floor(blocks), frac = blocks - full, nb = Math.min(cols * rows, Math.ceil(blocks));
    const spk = clamp(Math.log10(gr / 0.02) / 3, 0, 1);
    for (let i = 0; i < nb; i++) {
      const x = rx + (i % cols) * sz, y = ry + Math.floor(i / cols) * sz, w = sz - gap, f = i < full ? 1 : frac, R = ROCK[i % ROCK.length];
      ctx.save(); ctx.beginPath(); ctx.rect(x, y, Math.max(0.6, w * f), w); ctx.clip();
      const gg = ctx.createLinearGradient(x, y, x + w, y + w); gg.addColorStop(0, g.rgba(c.soft, 0.42 + 0.12 * R[0])); gg.addColorStop(1, g.rgba(c.soft, 0.2 + 0.1 * R[1]));
      ctx.fillStyle = gg; ctx.fillRect(x, y, w, w);
      const ns = 1 + Math.round(spk * 4);
      for (let k = 0; k < ns; k++) g.dot(x + w * ((R[2] + k * 0.37) % 1), y + w * ((R[3] + k * 0.61) % 1), Math.max(0.8, w * 0.07), c.photon, 0.95);
      ctx.restore();
    }
    for (let i = nb; i < cols * rows; i++) g.dot(rx + (i % cols + 0.45) * sz, ry + (Math.floor(i / cols) + 0.45) * sz, 1, c.soft, 0.3); // empty slots: the scale of the grid
    if (nb === 0 || blocks < 1) g.label(WT.trf("{a} of one block", (blocks * 100).toFixed(0) + " %"), rx + sz * 1.3, ry + sz * 0.5, { color: c.soft, size: fs - 1, align: "left", raw: true });
    // grade readout
    const gtxt = gr >= 1 ? gr.toFixed(gr >= 10 ? 0 : 1) : gr >= 0.1 ? gr.toFixed(2) : gr.toFixed(3);
    // grade bar (log), desktop only: drag to change
    if (!phone) {
      const x0 = rx + 6, x1 = rx + rw - 6, y = b.y + b.h - 22, X = (lg) => lerp(x0, x1, (lg + 1.7) / 3);
      geo.bar = { x0, x1, y };
      g.ctx.save(); g.ctx.fillStyle = g.rgba(c.soft, 0.12); g.ctx.fillRect(x0, y - 4, x1 - x0, 8); g.ctx.restore();
      g.ctx.save(); g.ctx.fillStyle = g.rgba(c.photon, 0.35); g.ctx.fillRect(X(-1), y - 4, x1 - X(-1), 8); g.ctx.restore();
      [[0.02, "0.02 %"], [0.1, "0.1 %"], [1, "1 %"], [10, "10 %"]].forEach(([v, s]) => { const x = X(Math.log10(v)); g.line(x, y - 7, x, y + 7, c.soft, 1, 0.7); g.label(s, x, y + 16, { color: c.soft, size: fs - 2, raw: true }); });
      g.label("most mines: above 0.1 %", (X(-1) + X(0.6)) / 2, y - 16, { color: c.photon, size: fs - 2, weight: 600 });
      g.label("richest, Canada: up to 20 %", x1, y - 16, { color: c.soft, size: fs - 2, align: "right" });
      const hx = X(S.lg); g.glow(hx, y, 18, c.photon, 0.5); g.ball(hx, y, 8, c.photon); g.label(WT.trf("{a} % U", gtxt), hx, y - 34, { color: c.ink, size: fs + 1, weight: 700, raw: true, bg: true });
    } else { geo.bar = null; g.label(WT.trf("grade {a} % U", gtxt), rx, b.y + b.h - 6, { color: c.photon, size: fs, weight: 700, align: "left", raw: true }); }
    // 1000 uranium atoms, 7 of them U-235 (0.72 % of atoms)
    const ax = b.x + b.w * (phone ? 0.69 : 0.66), aw = b.w * (phone ? 0.31 : 0.34), ac = phone ? 20 : 25, ar = 1000 / ac;
    const ay = b.y + titleH, ah = b.h - titleH - (phone ? 22 : 40), as = Math.min(aw / ac, ah / ar);
    g.label(phone ? "1000 U atoms" : "1000 uranium atoms", ax, b.y + titleH * 0.4, { color: c.ink, size: fs, weight: 600, align: "left" });
    const LIT = new Set([37, 171, 288, 455, 596, 702, 913]);
    for (let i = 0; i < 1000; i++) {
      const x = ax + (i % ac + 0.5) * as, y = ay + (Math.floor(i / ac) + 0.5) * as;
      if (LIT.has(i)) { g.glow(x, y, as * 1.8, c.fission, 0.45 + 0.15 * Math.sin(S.time * 3 + i)); g.dot(x, y, as * 0.48, c.fission); }
      else g.dot(x, y, as * 0.3, c.soft, 0.55);
    }
    g.label(phone ? "7 are U-235" : "7 are uranium-235", ax, ay + ar * as + (phone ? 12 : 18), { color: c.fission, size: fs, weight: 700, align: "left" });
    if (!phone) g.label("the rest: uranium-238", ax, ay + ar * as + 36, { color: c.soft, size: fs - 1, align: "left" });
  }

  // ---------- step 2: enrichment mass balance ----------
  function drawEnrich(g, S, dt, b, phone, fs, snap) {
    const { c } = g, F = feed(S), T = F - 1, sw = swu(S);
    const labH = phone ? 40 : 58, top = b.y + (phone ? 4 : 10), bot = b.y + b.h - labH;
    const k = (bot - top) * 0.62 / 13.2;                 // px per kg (fixed: the bands change as the sliders move)
    const wF = F * k, wP = k, wT = T * k, xs = b.x + b.w * 0.02, xm = b.x + b.w * (phone ? 0.4 : 0.44), xe = b.x + b.w * (phone ? 0.74 : 0.8);
    const ym = (top + bot) / 2, yP = top + Math.max(wP, 14) / 2 + (phone ? 16 : 22), yT = bot - wT / 2 - 4;
    const bf = { x0: xs, x1: xm, y0: ym, y1: ym, w0: wF, w1: wF };
    const bp = { x0: xm, x1: xe, y0: ym - wF / 2 + wP / 2, y1: yP, w0: wP, w1: wP };
    const bt = { x0: xm, x1: xe, y0: ym + wF / 2 - wT / 2, y1: yT, w0: wT, w1: wT };
    band(g, bf, c.soft, 0.16); band(g, bt, c.cool, 0.2); band(g, bp, c.fission, 0.35);
    // the plant: a soft glowing gate where the stream divides
    g.glow(xm, ym, wF * 0.9 + 20, c.accent, 0.18);
    g.line(xm, ym - wF / 2 - 10, xm, ym + wF / 2 + 10, c.accent, 2, 0.6, [4, 4]);
    g.label(phone ? "enrich" : "enrichment plant (UF₆ gas)", xm, ym - wF / 2 - (phone ? 16 : 20), { color: c.accent, size: fs - 1, weight: 600, bg: true });
    // atoms: the share of green (U-235) dots in each band is the true assay
    const dens = phone ? 0.9 : 1.15, nF = Math.min(600, Math.round(wF * (xm - xs) * 0.06 * dens)), nP = Math.round(wP * (xe - xm) * 0.06 * dens), nT = Math.min(800, Math.round(wT * (xe - xm) * 0.06 * dens));
    const draw = (bb, i0, n, x, col) => { for (let i = 0; i < n; i++) { const p = EP[i0 + i]; if (!snap) p.u = (p.u + dt * 0.07) % 1; const [px, py, w] = bandPt(bb, p.u); const is5 = p.q < x / 100;
      if (is5) { g.glow(px, py + p.v * w * 0.85, 7, c.fission, 0.55); g.dot(px, py + p.v * w * 0.85, phone ? 2 : 2.6, c.fission); } else g.dot(px, py + p.v * w * 0.85, phone ? 1 : 1.3, col, 0.55); } };
    draw(bf, 0, nF, XF, c.soft); draw(bt, 600, Math.min(nT, 800), S.xt, c.cool); draw(bp, 1400, Math.min(nP, 100), S.xp, c.fission);
    // end labels
    const L = (s, x, y, o) => g.label(s, x, y, Object.assign({ size: fs - 1, raw: true }, o));
    L(WT.trf(phone ? "natural U {a} kg" : "natural uranium {a} kg", F.toFixed(1)), xs + 2, ym - wF / 2 - (phone ? 10 : 14), { color: c.ink, weight: 700, align: "left", size: fs });
    L(WT.trf("{a} % U-235", XF.toFixed(3)), xs + 2, ym + wF / 2 + (phone ? 10 : 14), { color: c.soft, align: "left" });
    const ex = xe + (phone ? 6 : 10);
    L(WT.trf("fuel 1 kg", ""), ex, yP - (phone ? 7 : 9), { color: c.fission, weight: 700, align: "left", size: fs });
    L(WT.trf("{a} % U-235", S.xp.toFixed(2)), ex, yP + (phone ? 7 : 9), { color: c.fission, align: "left" });
    L(WT.trf("tails {a} kg", T.toFixed(1)), ex, yT - (phone ? 7 : 9), { color: c.cool, weight: 700, align: "left", size: fs });
    L(WT.trf("{a} % U-235", S.xt.toFixed(2)), ex, yT + (phone ? 7 : 9), { color: c.cool, align: "left" });
    // formula and separative work
    const fy = b.y + b.h - labH + (phone ? 14 : 20);
    L(phone ? WT.trf("feed/fuel = (xp − xt)/(xf − xt) = {a}", F.toFixed(2)) : WT.trf("natural / fuel = (xp − xt) / (xf − xt) = ({a} − {b}) / ({c} − {b}) = {d}", S.xp.toFixed(2), S.xt.toFixed(2), XF.toFixed(3), F.toFixed(2)), b.x + b.w / 2, fy, { color: c.ink, size: fs, serif: true, weight: 600 });
    L(WT.trf(phone ? "≈ {a} SWU of separative work per kg of fuel" : "separative work ≈ {a} SWU per kg of fuel · lower tails: less uranium, more work", sw.toFixed(1)), b.x + b.w / 2, fy + (phone ? 16 : 24), { color: c.soft, size: fs - 1 });
  }

  // ---------- step 3: fabrication ----------
  function drawFab(g, S, b, phone, fs, snap) {
    const { c, ctx } = g, t = snap ? 4.6 : ((S.time - (S.fab0 || 0)) % 8), ft = Math.round(S.ft);
    const nP = 1e6 / 4.85 * ft, nR = nP / 350, nA = nR / 264;
    const big = { color: c.ink, size: fs + (phone ? 1 : 5), weight: 700, raw: true }, sm = { color: c.soft, size: fs - 2 };
    g.label(phone ? WT.trf("{a} t uranium = {b} t UO₂", ft, (ft * UO2).toFixed(ft > 9 ? 0 : 2)) : WT.trf("{a} t of enriched uranium, as {b} t of uranium dioxide (UO₂) ceramic", ft, (ft * UO2).toFixed(ft > 9 ? 0 : 2)), b.x + b.w / 2, b.y + (phone ? 8 : 14), { color: c.ink, size: fs, weight: 600, raw: true });
    // ---- top row: pellet -> rod -> assembly ----
    const colW = b.w / 3, cy = b.y + b.h * (phone ? 0.3 : 0.28), yl = cy + b.h * (phone ? 0.17 : 0.15);
    const px = b.x + colW * 0.42, pr = Math.min(colW * 0.16, b.h * 0.07), ph = pr * 1.25;
    g.glow(px, cy, pr * 2.6, c.warm, 0.14);
    ctx.save();
    const pg = ctx.createLinearGradient(px - pr, 0, px + pr, 0); pg.addColorStop(0, g.rgba(c.soft, 0.6)); pg.addColorStop(0.4, g.rgba(c.soft, 0.25)); pg.addColorStop(1, g.rgba(c.soft, 0.7));
    ctx.fillStyle = pg; ctx.beginPath(); ctx.ellipse(px, cy + ph / 2, pr, pr * 0.3, 0, 0, Math.PI); ctx.lineTo(px - pr, cy - ph / 2); ctx.ellipse(px, cy - ph / 2, pr, pr * 0.3, 0, Math.PI, TAU); ctx.closePath(); ctx.fill();
    ctx.fillStyle = g.rgba(c.soft, 0.45); ctx.beginPath(); ctx.ellipse(px, cy - ph / 2, pr, pr * 0.3, 0, 0, TAU); ctx.fill(); ctx.strokeStyle = g.rgba(c.ink, 0.3); ctx.lineWidth = 1; ctx.stroke(); ctx.restore();
    g.label(WT.trf("≈ {a}", nf(nP >= 1e6 ? Math.round(nP / 1e4) * 1e4 : Math.round(nP / 1000) * 1000)), px, yl, big);
    g.label(phone ? "pellets" : "pellets, 1 cm tall", px, yl + (phone ? 15 : 22), sm);
    // rod filling with pellets
    const rx0 = b.x + colW * 0.82, rx1 = b.x + colW * 1.9, rh = phone ? 7 : 11, n = phone ? 14 : 24, fill = smooth(0, 3.2, t);
    ctx.save(); ctx.strokeStyle = g.rgba(c.soft, 0.8); ctx.lineWidth = 1.4; ctx.beginPath(); if (ctx.roundRect) ctx.roundRect(rx0, cy - rh / 2, rx1 - rx0, rh, rh / 2); else ctx.rect(rx0, cy - rh / 2, rx1 - rx0, rh); ctx.stroke(); ctx.restore();
    const pw = (rx1 - rx0 - 6) / n, k = Math.floor(fill * n);
    ctx.save(); ctx.fillStyle = g.rgba(c.ink, 0.45);
    for (let i = 0; i < k; i++) ctx.fillRect(rx0 + 3 + i * pw + 0.5, cy - rh / 2 + 2, pw - 1, rh - 4);
    if (k < n) ctx.fillRect(lerp(rx0 - 24, rx0 + 3 + k * pw, (fill * n) % 1), cy - rh / 2 + 2, pw - 1, rh - 4);
    ctx.restore();
    g.label(WT.trf("≈ {a}", nf(Math.round(nR / 10) * 10)), (rx0 + rx1) / 2, yl, big);
    g.label(phone ? "rods, 4 m" : "rods, about 4 m long", (rx0 + rx1) / 2, yl + (phone ? 15 : 22), sm);
    // one 17x17 assembly seen from above: 264 fuel rods + 25 tubes for control rods and instruments
    const as = Math.min(colW * 0.62, b.h * (phone ? 0.24 : 0.22)), cell = as / 17, ax = b.x + colW * 2.5 - as / 2, ay = cy - as / 2;
    const done = snap ? 289 : Math.floor(smooth(1.5, 6.5, t) * 289);
    ctx.save(); ctx.strokeStyle = g.rgba(c.soft, 0.7); ctx.lineWidth = 1.2; ctx.strokeRect(ax - 2, ay - 2, as + 4, as + 4); ctx.restore();
    for (let i = 0; i < 289; i++) { const rr = Math.floor(i / 17), cc = i % 17, x = ax + (cc + 0.5) * cell, y = ay + (rr + 0.5) * cell;
      if (GTS.has(rr * 17 + cc)) { g.ring(x, y, cell * 0.38, c.soft, 1, 0.7); continue; }
      if (i < done) g.dot(x, y, cell * 0.36, c.warm, 0.9); else g.dot(x, y, cell * 0.15, c.soft, 0.4); }
    g.arrow(px + pr + 10, cy, rx0 - 10, cy, c.soft, 1.5, 0.6, 7); g.arrow(rx1 + 8, cy, ax - 10, cy, c.soft, 1.5, 0.6, 7);
    g.label(WT.trf("≈ {a}", nA >= 10 ? nA.toFixed(0) : nA.toFixed(1)), ax + as / 2, yl, big);
    g.label(phone ? "assemblies" : "assemblies of 264 rods", ax + as / 2, yl + (phone ? 15 : 22), sm);
    // ---- bottom: all the assemblies for this much fuel, as small squares ----
    const fy0 = yl + (phone ? 30 : 44), fh = b.y + b.h - fy0 - (phone ? 4 : 10), N = Math.ceil(nA), full = Math.floor(nA);
    const per = phone ? 20 : 20, s = Math.min(b.w / per, fh / 3.2), q = s * 0.8, fx = b.x + (b.w - per * s) / 2 + (s - q) / 2;
    for (let i = 0; i < N; i++) { const x = fx + (i % per) * s, y = fy0 + Math.floor(i / per) * s, f = i < full ? 1 : nA - full;
      g.glow(x + q / 2, y + q / 2, q * 0.8, c.warm, 0.12);
      ctx.save(); ctx.fillStyle = g.rgba(c.warm, 0.18); ctx.fillRect(x, y, q, q); ctx.fillStyle = g.rgba(c.warm, 0.75); ctx.fillRect(x, y, q * f, q); ctx.restore(); }
    if (ft >= 20) g.label(phone ? "≈ a big reactor's yearly reload" : "about what a 1000 MWe reactor loads in a year", b.x + b.w / 2, fy0 + Math.ceil(N / per) * s + (phone ? 8 : 14), { color: c.warm, size: fs - 1, weight: 600 });
  }

  // ---------- step 4: one tonne in the core ----------
  function drawCore(g, S, b, phone, fs, snap) {
    const { c } = g, co = comp(S);
    const cols = 40, rows = 25, gw = b.w * (phone ? 1 : 0.6), barH = phone ? 0 : 54;
    const gh = phone ? b.h * 0.5 : b.h - 26 - barH, cs = Math.min(gw / cols, gh / rows), gx = b.x, gy = b.y + (phone ? 18 : 26);
    g.label(phone ? "one tonne: each square 1 kg" : "one tonne of fuel: each square is 1 kg", gx, b.y + (phone ? 8 : 12), { color: c.ink, size: fs, weight: 600, align: "left" });
    // categories: 0 U-238, 1 U-235, 2 Pu, 3 fission products, 4 minor actinides
    const n0 = Math.round(co.u0), n5 = Math.round(co.u5), nPu = Math.round(co.pu), nFP = Math.round(co.fp), nMA = Math.round(co.ma);
    const burned5 = Math.min(n0 - n5, nFP), extraFP = nFP - burned5;
    const kind = new Int8Array(1000);
    for (let j = 0; j < 1000; j++) {
      const i = PERM[j]; let k = 0;
      if (j < n0) k = j < n0 - n5 ? (j < burned5 ? 3 : 0) : 1;
      else if (j < n0 + nPu) k = 2;
      else if (j < n0 + nPu + nMA) k = 4;
      else if (j >= 1000 - extraFP) k = 3;
      kind[i] = k;
    }
    const COL = [c.soft, c.fission, c.warm, c.faint, c.alpha];
    for (let i = 0; i < 1000; i++) {
      const k = kind[i]; if (cellK[i] !== k) { if (cellK[i] >= 0 && !snap) cellT[i] = S.time; cellK[i] = k; }
      const x = gx + (i % cols) * cs, y = gy + Math.floor(i / cols) * cs, age = S.time - cellT[i];
      if (age < 0.8) g.glow(x + cs / 2, y + cs / 2, cs * 2.5, k === 3 ? c.photon : COL[k], 0.7 * (1 - age / 0.8));
      if (k === 1 || k === 2) g.glow(x + cs / 2, y + cs / 2, cs * 1.4, COL[k], 0.25);
      g.ctx.save(); g.ctx.fillStyle = g.rgba(COL[k], k === 0 ? 0.32 : k === 3 ? 0.75 : 0.95); g.ctx.fillRect(x + 0.5, y + 0.5, cs - 1, cs - 1); g.ctx.restore();
    }
    // legend with kg
    const items = [[c.soft, phone ? "U-238" : "uranium-238 (and -236)", co.u8], [c.fission, phone ? "U-235" : "uranium-235", co.u5], [c.warm, phone ? "Pu" : "plutonium", co.pu], [c.faint, phone ? "fission prod." : "fission products", co.fp], [c.alpha, phone ? "minor act." : "minor actinides", co.ma]];
    if (!phone) {
      const lx = b.x + b.w * 0.66, ly0 = gy + 6, dy = Math.min(34, (gh - 80) / 5);
      items.forEach(([col, s, v], i) => { const y = ly0 + i * dy; g.ctx.save(); g.ctx.fillStyle = g.rgba(col, i === 0 ? 0.4 : 0.95); g.ctx.fillRect(lx, y - 6, 12, 12); g.ctx.restore();
        g.label(s, lx + 20, y, { color: c.ink, size: fs, align: "left" }); g.label(WT.trf("{a} kg", v >= 100 ? nf(v) : v.toFixed(1)), b.x + b.w, y, { color: i === 0 ? c.soft : col === c.faint ? c.ink : col, size: fs, weight: 700, align: "right", raw: true }); });
      const ey = ly0 + 5 * dy + 26;
      g.label(WT.trf("≈ {a} GWh", nf(co.e)), lx, ey, { color: c.photon, size: fs + 8, weight: 700, align: "left", raw: true });
      g.label("of electricity from this tonne", lx, ey + 24, { color: c.soft, size: fs - 1, align: "left" });
      g.label(WT.trf("{a} % of the heavy atoms split", (co.fp / 10).toFixed(1)), lx, ey + 48, { color: c.soft, size: fs - 1, align: "left", raw: true });
      // burnup bar (drag)
      const x0 = gx + 6, x1 = gx + cols * cs - 6, y = Math.min(b.y + b.h - 20, gy + rows * cs + 62), X = (v) => lerp(x0, x1, v / 60);
      geo.bbar = { x0, x1, y };
      g.ctx.save(); g.ctx.fillStyle = g.rgba(c.soft, 0.12); g.ctx.fillRect(x0, y - 4, x1 - x0, 8); g.ctx.fillStyle = g.rgba(c.warm, 0.3); g.ctx.fillRect(X(45), y - 4, X(55) - X(45), 8); g.ctx.restore();
      g.label("typical discharge 45–55", (X(45) + X(55)) / 2 - 20, y + 16, { color: c.warm, size: fs - 2 });
      [0, 20, 60].forEach((v) => g.label(String(v), X(v), y + 16, { color: c.soft, size: fs - 2, raw: true }));
      const hx = X(S.bu); g.glow(hx, y, 16, c.warm, 0.5); g.ball(hx, y, 8, c.warm);
      g.label(WT.trf("{a} GWd/t", S.bu.toFixed(0)), hx, y - 22, { color: c.ink, size: fs, weight: 700, raw: true, bg: true });
    } else {
      geo.bbar = null;
      const ly0 = gy + rows * cs + 14, colw = b.w / 2;
      items.forEach(([col, s, v], i) => { const x = b.x + (i % 2) * colw, y = ly0 + Math.floor(i / 2) * 17; g.ctx.save(); g.ctx.fillStyle = g.rgba(col, i === 0 ? 0.4 : 0.95); g.ctx.fillRect(x, y - 5, 10, 10); g.ctx.restore();
        g.label(WT.trf("{a} {b} kg", WT.tr ? WT.tr(s) : s, v >= 100 ? nf(v) : v.toFixed(1)), x + 15, y, { color: c.ink, size: fs - 1, align: "left", raw: true }); });
      g.label(WT.trf("≈ {a} GWh of electricity", nf(co.e)), b.x + b.w * 0.75, ly0 + 2 * 17, { color: c.photon, size: fs, weight: 700, raw: true });
    }
  }

  // ---------- step 5: storage and the two routes ----------
  function drawAfter(g, S, dt, b, phone, fs, snap) {
    const { c, ctx } = g, co = comp(S), rt = S.rt, ru = S.route === "R";
    const k = (phone ? 0.032 : 0.05) * Math.min(1, b.h / 520);       // px per kg: 1 t = 32-50 px
    const W1 = 1000 * k, gy = b.y + b.h * (phone ? 0.5 : 0.52);       // ground line
    const xP = b.x + b.w * 0.1, xC = b.x + b.w * 0.33, xS = b.x + b.w * 0.55, xE = b.x + b.w * 0.9, yB = b.y + b.h * 0.26;
    // ground and deep rock
    ctx.save(); const rg = ctx.createLinearGradient(0, gy, 0, b.y + b.h); rg.addColorStop(0, g.rgba(c.soft, 0.16)); rg.addColorStop(1, g.rgba(c.soft, 0.04)); ctx.fillStyle = rg; ctx.fillRect(b.x, gy, b.w, b.y + b.h - gy); ctx.restore();
    g.line(b.x, gy, b.x + b.w, gy, c.soft, 1.2, 0.6);
    // the repository far below
    const repY = b.y + b.h - (phone ? 20 : 30), repX = xE - b.w * 0.08;
    ctx.save(); ctx.fillStyle = g.rgba(c.ink, 0.12); ctx.strokeStyle = g.rgba(c.soft, 0.6); ctx.lineWidth = 1.2; ctx.beginPath(); if (ctx.roundRect) ctx.roundRect(repX - b.w * 0.13, repY - 10, b.w * 0.26, 20, 10); else ctx.rect(repX - b.w * 0.13, repY - 10, b.w * 0.26, 20); ctx.fill(); ctx.stroke(); ctx.restore();
    g.line(repX + b.w * 0.12, gy, repX + b.w * 0.12, repY - 10, c.soft, 1.2, 0.5, [3, 3]);
    g.label(phone ? "repository 250–1000 m deep" : "deep repository, 250–1000 m down", b.x + b.w, repY + (phone ? -20 : -24), { color: c.ink, size: fs - 1, weight: 600, bg: true, align: "right" });
    // pool and cask (both routes)
    const pw = b.w * 0.14, ph = b.h * 0.16;
    ctx.save(); const pg = ctx.createLinearGradient(0, yB - ph / 2, 0, yB + ph / 2); pg.addColorStop(0, g.rgba(c.cool, 0.25)); pg.addColorStop(1, g.rgba(c.cool, 0.5)); ctx.fillStyle = pg; ctx.fillRect(xP - pw / 2, yB - ph / 2, pw, ph); ctx.restore();
    g.glow(xP, yB + ph * 0.15, pw * 0.5, "#5fb0ff", 0.35 + 0.1 * Math.sin(S.time * 2));
    g.label("pool", xP, yB - ph / 2 - (phone ? 10 : 14), { color: c.cool, size: fs, weight: 700 });
    g.label(phone ? "≥ 5 years" : "at least 5 years", xP, yB + ph / 2 + (phone ? 10 : 14), { color: c.soft, size: fs - 2 });
    const cw = b.w * 0.05, chh = ph * 1.15;
    ctx.save(); const cg = ctx.createLinearGradient(xC - cw / 2, 0, xC + cw / 2, 0); cg.addColorStop(0, g.rgba(c.soft, 0.35)); cg.addColorStop(0.4, g.rgba(c.soft, 0.7)); cg.addColorStop(1, g.rgba(c.soft, 0.3)); ctx.fillStyle = cg;
    ctx.beginPath(); if (ctx.roundRect) ctx.roundRect(xC - cw / 2, yB - chh / 2, cw, chh, 4); else ctx.rect(xC - cw / 2, yB - chh / 2, cw, chh); ctx.fill(); ctx.restore();
    g.label(phone ? "cask" : "dry cask", xC, yB - chh / 2 - (phone ? 10 : 14), { color: c.ink, size: fs, weight: 700 });
    g.label(phone ? "decades" : "decades in air", xC, yB + chh / 2 + (phone ? 10 : 14), { color: c.soft, size: fs - 2 });
    band(g, { x0: xP + pw / 2, x1: xC - cw / 2, y0: yB, y1: yB, w0: W1, w1: W1 }, c.soft, 0.3);
    g.label(phone ? "1 t used" : "1 t used fuel", (xP + pw / 2 + xC - cw / 2) / 2, yB - W1 / 2 - (phone ? 9 : 13), { color: c.ink, size: fs - 1, weight: 700 });
    // once-through: the whole tonne goes down
    const bo = { x0: xC + cw / 2, x1: repX - b.w * 0.13, y0: yB, y1: repY, w0: W1, w1: W1 };
    // reprocessing plant
    const rpw = b.w * 0.1, rph = b.h * 0.18;
    const aO = 1 - rt, aR = rt;
    if (aO > 0.02) band(g, bo, c.soft, 0.3 * aO, 0.18 * aO);
    if (aR > 0.02) {
      ctx.save(); ctx.globalAlpha = aR; ctx.fillStyle = g.rgba(c.accent, 0.14); ctx.strokeStyle = g.rgba(c.accent, 0.8); ctx.lineWidth = 1.5; ctx.fillRect(xS - rpw / 2, yB - rph / 2, rpw, rph); ctx.strokeRect(xS - rpw / 2, yB - rph / 2, rpw, rph); ctx.restore();
      g.label(phone ? "reprocess" : "reprocessing", xS, yB - rph / 2 - (phone ? 10 : 14), { color: c.accent, size: fs, weight: 700, alpha: aR });
      band(g, { x0: xC + cw / 2, x1: xS - rpw / 2, y0: yB, y1: yB, w0: W1, w1: W1 }, c.soft, 0.3 * aR);
      const wU = co.u8 * k + co.u5 * k, wPu = Math.max(2, co.pu * k), wW = Math.max(2.5, (co.fp + co.ma) * k);
      const yU = b.y + (phone ? 30 : 18), yPu = yB, yW = yB + rph / 2 + 4;
      const bU = { x0: xS + rpw / 2, x1: xE, y0: yB - rph / 2 + wU / 2 + 2, y1: yU + wU / 2, w0: wU, w1: wU };
      const bPu = { x0: xS + rpw / 2, x1: xE, y0: yPu, y1: yPu, w0: wPu, w1: wPu };
      const bW = { x0: xS, x1: repX + b.w * 0.05, y0: yW, y1: repY, w0: wW, w1: wW };
      band(g, bU, c.soft, 0.3 * aR); band(g, bPu, c.warm, 0.8 * aR); band(g, bW, c.photon, 0.6 * aR, 0.4 * aR);
      const lx = xE + (phone ? -2 : 6), al = phone ? "right" : "left", L = (s, x, y, o) => g.label(s, x, y, Object.assign({ size: fs - 1, raw: true, alpha: aR, bg: true }, o));
      if (!phone) {
        L(WT.trf("uranium {a} t", ((co.u8 + co.u5) / 1000).toFixed(2)), lx, bU.y1 - 8, { color: c.ink, weight: 700, align: al });
        L("→ re-enriched", lx, bU.y1 + 10, { color: c.soft, align: al });
        L(WT.trf("plutonium {a} kg", co.pu.toFixed(0)), lx, yPu - 9, { color: c.warm, weight: 700, align: al });
        L(WT.trf("→ ≈ {a} t MOX fuel", (co.pu / MOXPU / 1000).toFixed(2)), lx, yPu + 9, { color: c.warm, align: al });
        L(WT.trf("fission products + minor actinides {a} kg → ≈ 0.2 t glass", (co.fp + co.ma).toFixed(0)), (xS + repX) / 2 + b.w * 0.04, (yW + repY) / 2 + 6, { color: c.photon, align: "center", weight: 600 });
      } else {
        L(WT.trf("U {a} t → re-enrich", ((co.u8 + co.u5) / 1000).toFixed(2)), b.x + b.w, bU.y1 - wU / 2 - 9, { color: c.ink, weight: 600, align: "right" });
        L(WT.trf("Pu {a} kg → MOX", co.pu.toFixed(0)), b.x + b.w, yPu + 12, { color: c.warm, weight: 600, align: "right" });
        L(WT.trf("{a} kg waste → glass", (co.fp + co.ma).toFixed(0)), (xS + repX) / 2, (yW + repY) / 2 + 4, { color: c.photon, weight: 600 });
      }
      for (const p of AP) { if (!snap) p.u = (p.u + dt * 0.12) % 1; const bb = p.q < 0.55 ? bU : p.q < 0.7 ? bPu : bW, col = bb === bU ? c.soft : bb === bPu ? c.warm : c.photon; const [x, y, w] = bandPt(bb, p.u); g.dot(x, y + p.v * w * 0.7, phone ? 1.3 : 1.8, col, 0.8 * aR); }
    }
    if (aO > 0.02) {
      for (const p of AP) { if (p.q > 0.5) continue; if (!snap && aR < 0.02) p.u = (p.u + dt * 0.12) % 1; const [x, y, w] = bandPt(bo, p.u); g.dot(x, y + p.v * w * 0.7, phone ? 1.3 : 1.8, c.soft, 0.8 * aO); }
      g.label(phone ? "the whole tonne" : "once-through: the whole tonne is disposed of", xS - b.w * 0.02, (gy + yB) / 2 + (phone ? 6 : 0), { color: c.ink, size: fs - 1, weight: 600, alpha: aO, bg: true, align: "left" });
    }
    // particles from pool to cask
    for (let i = 0; i < 24; i++) { const p = AP[i]; const u = (p.u * 3) % 1, x = lerp(xP + pw / 2, xC - cw / 2, u); g.dot(x, yB + p.v * W1 * 0.7, phone ? 1.3 : 1.8, c.soft, 0.8); }
  }
})();
