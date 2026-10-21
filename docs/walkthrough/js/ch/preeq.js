/* Chapter 4: pre-equilibrium (preeq/, density/particle_hole.py). Fast collisions before the nucleus calms down.
 * Scenes (S.mode): "sea"   = two filled wells (protons, neutrons), Fermi surface, the incoming neutron above;
 *                   "pairs" = each collision lifts a nucleon and leaves a hole: excitons n = 1, 3, 5, ...;
 *                   "fork"  = at stage n the top particle escapes or collides again;
 *                   "tail"  = 300 reactions run as exciton chains; each escaping neutron flies to a pile sorted by energy,
 *                             coloured by the stage it left at: the pile is the spectrum (shelf from stage 3 + evaporation hump);
 *                   "pauli" = arrangements of p particles and h holes on an evenly spaced ladder, enumerated one by one;
 *                   "cluster" = pickup (p grabs n -> d) and alpha knockout;
 *                   "second"  = at high energy a second exciton still sits above the free line and escapes too; then calm.
 * Shapes follow preeq/exciton.py (two-component chain, never-come-back, emission by detailed balance),
 * density/particle_hole.py (Williams densities with Pauli and finite-well corrections), preeq/complex.py
 * (Kalbach pickup/stripping, alpha knockout), preeq/multi.py (multiple pre-equilibrium). Numbers illustrative. */
(function () {
  const { TAU, clamp, lerp, smooth, rng } = WT.util;
  const SEP = 8; // MeV, separation energy drawn above the Fermi surface
  let chain = []; // particle/hole bookkeeping for the pairs scene
  let clusterT = -10, clusterKind = "d";

  function resetChain(S) { chain = [{ kind: "n", y: 1, hole: false }]; S.n = 1; S.set("n", 1); }

  WT.chapter("preeq", {
    num: "Chapter 4", title: "Collisions before calm", short: "Pre-equilibrium",
    lead: "Pre-equilibrium means “before the energy evens out”. A neutron that enters a nucleus does not share its energy with everyone at once. For the first few collisions one particle still holds most of it, and that particle can fly straight back out.",
    html: `
<div class="step">
  <p>The picture shows two wells, one for <em class="p">protons</em> and one for <em class="n">neutrons</em>. Each ball is a nucleon (a proton or a neutron) sitting on an energy level, drawn as a rung. The rungs are filled from the bottom up to the <b>Fermi surface</b>, the top of the filled levels. A nucleon above the dashed line marked “free” has enough energy to escape. The engine tracks protons and neutrons separately throughout this chapter.</p>
  <p>The incoming neutron hovers above both wells. It carries its own energy plus the energy released when it was captured, several MeV (million electron-volts, the energy unit used here). Right now one particle holds all of that energy, and the filled levels have no gaps.</p>
</div>
<div class="step">
  <h3>Lifting pairs</h3>
  <p>Now the neutron has hit a nucleon below the surface and knocked it up onto an empty rung. The empty slot it left behind is a <b>hole</b>, drawn as an open ring. The engine counts particles above the surface plus holes below it, and calls each one an <b>exciton</b>. The first collision turns 1 particle into 2 particles and 1 hole (n = 3 excitons); each further collision adds one more particle–hole pair.</p>
  <div class="btns"><button class="btn" data-act="collide">Collide</button><button class="btn ghost" data-act="reset">Start again</button></div>
  <p>Press Collide a few times. The lifted nucleon may be a proton or a neutron, and the engine keeps a separate count for each. With every pair the energy is split more ways, so the highest particle sits lower.</p>
</div>
<div class="step">
  <h3>The fork at every stage</h3>
  <p>The picture shows one stage of the chain. The top neutron can escape (the arrow up and out), if it still sits above the free line, or it can collide again (the arrow down). The thickness of each arrow shows its chance. The escape rate comes from <b>detailed balance</b>: the chance of leaving follows from the chance of the reverse process, the same particle being absorbed, which Chapter 2 computes. The collision rate is the average strength of one nucleon–nucleon collision times the number of new arrangements it can reach.</p>
  <div class="ctl"><label for="pe-n">Stage (excitons n)</label><input id="pe-n" type="range" data-bind="n" min="3" max="11" step="2" value="3" data-instant><output data-show="n" data-fmt="0"></output></div>
  <p>Drag the stage up. Early in the chain one particle holds most of the energy, so whatever escapes is fast. Later the energy is spread thin, and only slow particles get out, if any.</p>
</div>
<div class="step">
  <h3>Where the fast tail comes from</h3>
  <p>The same two wells, now running whole reactions. In each one the chain steps through stages 3, 5, 7, … until the top neutron escapes. It flies to the right and lands in a pile sorted by its energy: slow on the left, fast on the right. Its colour says when it left: <em style="font-style:normal;color:var(--warm);font-weight:600">deep orange</em> at stage 3, paler at later stages, and <em class="n">blue</em> if nothing escaped during the chain and the neutron came out later, from the calm compound nucleus (Chapter 5). The pile is the <b>spectrum</b>: how many neutrons come out at each energy.</p>
  <div class="btns"><button class="btn" data-act="run">Run 300 reactions</button></div>
  <p>Stage 3 builds a broad, nearly flat shelf that reaches all the way to the maximum energy, because one particle still holds most of it. Later stages pile up lower. The blue hump on the left is <b>evaporation</b>: once the energy is shared by everyone, only slow neutrons trickle out, like steam from a hot liquid.</p>
  <div class="ctl"><label for="pe-e">Neutron energy</label><input id="pe-e" type="range" data-bind="E" min="5" max="60" step="0.5" value="20"><output data-show="E" data-fmt="1"></output></div>
  <p>Drag the incoming neutron's energy and a new batch runs. Evaporation alone cannot make fast neutrons; the shelf can, and it stretches further as the incoming neutron gets faster.</p>
</div>
<div class="step">
  <h3>Counting arrangements</h3>
  <p>One well, drawn with evenly spaced rungs 1 MeV apart. The picture runs through every way to place the particles on empty rungs above the Fermi surface and the holes in filled rungs below it, so that their energies add up to the energy to share; the counter ticks once per arrangement. Nucleons are fermions: no two can sit on the same rung, so a lifted nucleon must land on an empty rung and a hole can only open where a nucleon was. This rule is <b>Pauli blocking</b>.</p>
  <div class="ctl"><label for="pe-u">Energy to share (MeV)</label><input id="pe-u" type="range" data-bind="U" min="2" max="16" step="1" value="8" data-instant><output data-show="U" data-fmt="0"></output></div>
  <div class="btns"><button class="btn" data-act="addpair">Add a pair</button><button class="btn ghost" data-act="droppair">Remove a pair</button></div>
  <p>Add a pair and the count jumps; raise the energy and it climbs roughly like <i>E</i><sup>n−1</sup>, where n is the number of excitons. That count, the <b>particle–hole state density</b>, is what sets the collision rate of the last step: more ways to arrange means more places a collision can lead. The engine counts with the Pauli rule built in, on the real ladder (rungs about a quarter MeV apart in a medium nucleus, so far more arrangements), plus one more limit you can see at high energy: a hole cannot be deeper than the bottom of the well.</p>
</div>
<div class="step">
  <h3>Clusters leave too</h3>
  <p>Press a button to watch a small cluster of nucleons leave early. In a <b>pickup</b>, a proton on its way out grabs a neutron at the surface and leaves with it as a <em class="n">deuteron</em> (one proton plus one neutron). Grabbing two gives a triton (one proton, two neutrons) or helium-3 (two protons, one neutron). The engine uses Kalbach's formulas for how often each pickup happens. In a <b>knockout</b>, the incoming neutron hits an <em class="a">alpha particle</em> (two protons and two neutrons bound tightly together) that already exists near the surface, and knocks it straight out.</p>
  <div class="btns"><button class="btn ghost" data-act="pickup">Pick up a neutron → d</button><button class="btn ghost" data-act="knock">Knock out an α</button></div>
  <p>Both give deuterons and alphas fast tails of their own, starting just above their separation energies (the energy it costs to pull each one out).</p>
</div>
<div class="step">
  <h3>A second fast one</h3>
  <p>The wells replay one reaction at a time, with the energy scale squeezed to fit. The neutron enters and collides; the top neutron escapes fast. Look at what is left: one more lifted nucleon and a hole. At low energy that nucleon sits below the free line and stays. At high energy it can still sit above the line, and it escapes too, a second fast neutron or proton, before the rest settles.</p>
  <div class="ctl"><label for="pe-e2">Neutron energy</label><input id="pe-e2" type="range" data-bind="E" min="5" max="80" step="0.5" value="40"><output data-show="E" data-fmt="1"></output></div>
  <p>Drag the energy. Below about 20 MeV the second nucleon almost never clears the line; above it, more and more reactions shed two fast particles. This is <b>multiple pre-equilibrium</b> emission, and the engine follows the residual's excitons for it. Whatever has not left by the end of the chain becomes the compound nucleus of the next chapter. The engine runs this chain at every incoming energy with a smooth onset, because a sudden switch would put a false step into the capture cross section (how often the neutron is captured and a photon comes out).</p>
  <div class="aside">In the code: <code>preeq/exciton.py</code> (two-component exciton chain, collision and escape rates), <code>density/particle_hole.py</code> (particle–hole state densities with Pauli and finite-well corrections), <code>preeq/complex.py</code> (Kalbach pickup, stripping and α knockout), <code>preeq/multi.py</code> (multiple pre-equilibrium), <code>compound/normalization.py</code> (hand-off to the compound nucleus).</div>
</div>`,
    setup(S) {
      S.set("mode", "sea"); S.to("E", 20, true); S.to("U", 12, true); S.set("n", 1);
      resetChain(S);
      S.on("collide", () => {
        if (chain.filter((x) => !x.hole).length >= 6) return;
        const r = rng((performance.now() | 0) + 3); const kind = r() < 0.5 ? "p" : "n";
        const n = chain.length + 2;
        // energy shares: the top particle sinks as the pair count rises
        chain.forEach((x) => { if (!x.hole) x.y *= 0.72; else x.y *= 0.9; });
        chain.push({ kind, y: 0.4 * Math.pow(0.8, (n - 3) / 2), hole: false }, { kind, y: -0.12 - 0.1 * r() - 0.03 * n, hole: true });
        S.set("n", n); S.collideT = S.time;
      });
      S.on("reset", () => resetChain(S));
      S.on("pickup", () => { clusterT = S.time; clusterKind = "d"; });
      S.on("knock", () => { clusterT = S.time; clusterKind = "a"; });
      S.on("run", () => startRun(S, S.target.E, 0));
      S.on("addpair", () => { S.ph = Math.min(3, (S.ph || 1) + 1); S.cntT = S.time; });
      S.on("droppair", () => { S.ph = Math.max(1, (S.ph || 1) - 1); S.cntT = S.time; });
      S.ph = 1; S.cntT = 0;
    },
    steps: [
      (S) => { S.set("mode", "sea"); },
      (S) => { S.set("mode", "pairs"); if (chain.length === 1) S.handlers.collide(); },
      (S) => { S.set("mode", "fork"); if (S.n < 3) S.set("n", 3); },
      (S) => { S.set("mode", "tail"); S.to("E", 20); startRun(S, 20, 150); S.runE = 20; },
      (S) => { S.set("mode", "pauli"); S.to("U", 8); S.cntT = S.time; },
      (S) => { S.set("mode", "cluster"); if (clusterT < 0) clusterT = S.time; },
      (S) => { S.set("mode", "second"); S.to("E", 40); S.secT = S.time; S.tally = null; },
    ],
    frame(g, S, dt) {
      switch (S.mode) {
        case "sea": return drawWells(g, S, "sea");
        case "pairs": return drawWells(g, S, "pairs");
        case "fork": return drawFork(g, S);
        case "tail": return drawTail(g, S, dt);
        case "pauli": return drawPauli(g, S);
        case "cluster": return drawCluster(g, S);
        default: return drawSecond(g, S);
      }
    },
  });

  // ---------- the two wells ----------
  function wells(g) {
    const { W, H } = g; const phone = W < 600;
    const yFermi = H * 0.56, yFloor = H * 0.9, yFree = yFermi - (yFloor - yFermi) * 0.35, yTop = H * 0.08;
    const gapx = phone ? W * 0.05 : W * 0.07, ww = (W * (phone ? 0.6 : 0.7) - gapx) / 2;
    const px0 = W * 0.07, nx0 = px0 + ww + gapx;
    // energy in MeV above the Fermi surface mapped to y: SEP MeV = yFermi - yFree
    const Y = (E) => yFermi - (yFermi - yFree) * E / SEP;
    return { yFermi, yFloor, yFree, yTop, ww, px0, nx0, Y, phone };
  }
  // the sea's rung rows and ball slots (shared so holes can replace a ball exactly)
  const NR = 6;
  function seaRow(L, i) { return L.yFloor - 10 - i * (L.yFloor - L.yFermi - 14) / (NR - 1); }
  function drawWellBase(g, L, labels = true, t = 0, holes) {
    const { c } = g; const { yFermi, yFloor, yFree, yTop, ww, px0, nx0, phone } = L;
    [[px0, c.proton, "protons", "p"], [nx0, c.neutron, "neutrons", "n"]].forEach(([x, col, nm, kind]) => {
      if (L.only && L.only !== kind) return;
      // walls and floor
      g.line(x, yTop, x, yFloor, c.line, 2); g.line(x + ww, yTop, x + ww, yFloor, c.line, 2); g.line(x, yFloor, x + ww, yFloor, c.line, 2);
      // filled sea: rungs with balls up to the Fermi surface; the balls shimmer, most at the surface
      const ctx = g.ctx; ctx.save(); ctx.globalAlpha = 0.12; ctx.fillStyle = col; ctx.fillRect(x + 2, yFermi, ww - 4, yFloor - yFermi); ctx.restore();
      for (let i = 0; i < NR; i++) {
        const y = seaRow(L, i), amp = 0.25 + 1.6 * Math.pow(i / (NR - 1), 3);
        g.line(x + ww * 0.12, y, x + ww * 0.88, y, c.line, 1);
        for (let k = 0; k < 3; k++) {
          if (holes && holes[kind + i + "," + k]) continue;
          const ph = i * 1.7 + k * 2.3 + (kind === "p" ? 0.9 : 0);
          g.ball(x + ww * (0.3 + 0.2 * k) + Math.sin(t * 1.3 + ph) * amp * 0.6, y - 6 + Math.sin(t * 2.1 + ph * 1.4) * amp, Math.min(6.5, ww * 0.04), col, 0.9);
        }
      }
      // a faint glint drifting along the surface
      const gx = x + ww * (0.5 + 0.38 * Math.sin(t * 0.45 + (kind === "p" ? 0 : 2)));
      g.glow(gx, yFermi - 4, ww * 0.18, col, 0.12);
      // empty rungs above the surface
      for (let i = 1; i <= 5; i++) { const y = yFermi - i * (yFermi - yTop) / 5.5; g.line(x + ww * 0.12, y, x + ww * 0.88, y, c.line, 1, 0.7, [3, 5]); }
      if (labels) g.label(nm, x + ww / 2, yFloor + 14, { color: col, size: phone ? 11 : 13 });
    });
    const xl = L.only === "n" ? nx0 : px0, xr = L.only === "p" ? px0 + ww : nx0 + ww;
    g.line(xl - 10, yFermi, xr + 10, yFermi, c.ink, 1.5, 0.8);
    g.line(xl - 10, yFree, xr + 10, yFree, c.faint, 1.2, 0.9, [5, 5]);
    if (L.sideLabels !== false) {
      g.label(phone ? "Fermi" : "Fermi surface", xr + 12, yFermi, { color: c.ink, size: phone ? 10 : 12, align: "left" });
      g.label(phone ? "free" : "free: can escape", xr + 12, yFree, { color: c.faint, size: phone ? 10 : 12, align: "left" });
    }
  }
  function wellLabelsInside(g, L) {
    const { c } = g, xl = L.px0;
    g.label(L.phone ? "Fermi" : "Fermi surface", xl + 4, L.yFermi + 9, { color: g.c.ink, size: 10, align: "left", bg: true });
    g.label("free", xl + 4, L.yFree - 9, { color: c.faint, size: 10, align: "left", bg: true });
  }
  // place a particle or hole: kind p/n, y in units of (free - Fermi) above Fermi (holes negative, in units of sea depth).
  // Holes snap onto a sea ball's slot (that ball is then not drawn).
  function placeAt(L, item, slot) {
    const { yFermi, yFree, yFloor, ww, px0, nx0 } = L; const x0 = item.kind === "p" ? px0 : nx0;
    if (item.hole) {
      const yh = yFermi + (yFloor - yFermi) * (-item.y); let best = 0, bd = 1e9;
      for (let i = 0; i < NR; i++) { const d = Math.abs(seaRow(L, i) - yh); if (d < bd) { bd = d; best = i; } }
      const k = slot % 3; item.cell = item.kind + best + "," + k;
      return [x0 + ww * (0.3 + 0.2 * k), seaRow(L, best)];
    }
    const x = x0 + ww * (0.22 + 0.56 * ((slot * 0.37) % 1));
    const y = yFermi - (yFermi - yFree) * item.y * 2.2;
    return [x, y];
  }
  function drawWells(g, S, mode) {
    const { W, H, c } = g; const L = wells(g); const { yFermi, yFree, yTop, ww, px0, nx0, phone } = L;
    const holes = {}; chain.forEach((it, i) => { if (it.hole) { placeAt(L, it, i); holes[it.cell] = 1; } });
    drawWellBase(g, L, true, S.time, mode === "pairs" ? holes : null);
    if (mode === "sea") {
      // the incoming neutron hovering above the neutron well, with its energy marked
      const x = nx0 + ww * 0.5, y = yTop + 24 + Math.sin(S.time * 2) * 3;
      g.glow(x, y, 26, c.warm, 0.45); g.ball(x, y, 9, c.neutron);
      g.arrow(x + ww * 0.3, yFermi - 4, x + ww * 0.3, y + 14, c.warm, 1.5, 0.8, 7);
      g.label("all the energy in one nucleon", x + ww * 0.3 - 8, (yFermi + y) / 2, { color: c.warm, size: phone ? 11 : 12, align: "right", bg: true });
      g.label("1 particle, 0 holes", W / 2, H * 0.97, { color: c.ink, size: phone ? 13 : 16, weight: 600, serif: true });
      return;
    }
    // pairs: draw the chain
    const flash = Math.max(0, 1 - (S.time - (S.collideT || -10)) / 0.7);
    let slot = 0; const counts = { p: [0, 0], n: [0, 0] };
    chain.forEach((it, i) => {
      const [x, y] = placeAt(L, it, slot++); const col = it.kind === "p" ? c.proton : c.neutron;
      counts[it.kind][it.hole ? 1 : 0]++;
      if (it.hole) g.ring(x, y - 6, 6, col, 2, 0.9);
      else { if (i >= chain.length - 2 && flash > 0) g.glow(x, y, 28, c.warm, flash * 0.6); g.ball(x, y, 8, col); }
    });
    if (flash > 0 && chain.length > 1) { const a = chain[chain.length - 2], h = chain[chain.length - 1]; const [xa, ya] = placeAt(L, a, chain.length - 2), [xh, yh] = placeAt(L, h, chain.length - 1); g.arrow(xh, yh - 6, xa, ya + 10, c.warm, 2, flash * 0.8); }
    const n = chain.length;
    const P = counts.p[0] + counts.n[0], Hh = counts.p[1] + counts.n[1];
    g.label(`${P} particle${P > 1 ? "s" : ""}, ${Hh} hole${Hh !== 1 ? "s" : ""}: n = ${n}`, W / 2, H * 0.97, { color: c.ink, size: phone ? 13 : 16, weight: 600, serif: true });
    g.label(`protons: ${counts.p[0]} lifted, ${counts.p[1]} hole${counts.p[1] !== 1 ? "s" : ""}`, px0 + ww / 2, yTop - 2 + 10, { color: c.proton, size: 12, bg: true });
    g.label(`neutrons: ${counts.n[0]} lifted, ${counts.n[1]} hole${counts.n[1] !== 1 ? "s" : ""}`, nx0 + ww / 2, yTop - 2 + 10, { color: c.neutron, size: 12, bg: true });
    if (P >= 6) g.label("chain ends: the rest becomes a compound nucleus", W / 2, yTop + 30, { color: c.soft, size: 12, bg: true });
  }

  // ---------- scene 3: the fork ----------
  function drawFork(g, S) {
    const { W, H, c } = g; const L = wells(g); const { yFermi, yFree, yTop, yFloor, ww, px0, nx0, phone, Y } = L;
    drawWellBase(g, L, true, S.time);
    const n = Math.round(S.n), E0 = 20 + SEP; // MeV available above the Fermi surface
    // typical energy of the top particle when E0 is shared among n excitons (illustrative): about 2E/(n+1)
    const Etop = 2 * E0 / (n + 1);
    const emit = clamp(0.55 * Math.pow(3 / n, 1.6) * (Etop > SEP ? 1 : 0.15), 0.02, 0.6);
    const p = (n + 1) / 2, h = (n - 1) / 2;
    // particles at shared heights (neutron well gets the top one), holes in both seas
    const ytop = clamp(Y(Etop), yTop + 14, yFermi - 10);
    const x = nx0 + ww * 0.5;
    for (let i = 1; i < p; i++) { const kind = i % 2 ? "p" : "n"; const xx = (kind === "p" ? px0 : nx0) + ww * (0.25 + 0.5 * ((i * 0.37) % 1)); const yy = yFermi - (yFermi - yTop) * (0.08 + 0.25 * Math.pow(0.8, i)); g.ball(xx, yy, 7, kind === "p" ? c.proton : c.neutron); }
    for (let i = 0; i < h; i++) { const kind = i % 2 ? "n" : "p"; const xx = (kind === "p" ? px0 : nx0) + ww * (0.25 + 0.5 * ((i * 0.61 + 0.2) % 1)); const yy = yFermi + (yFloor - yFermi) * (0.15 + 0.12 * i); g.ring(xx, yy - 6, 7, kind === "p" ? c.proton : c.neutron, 2, 0.9); g.ctx.save(); g.ctx.fillStyle = c.paper; g.ctx.beginPath(); g.ctx.arc(xx, yy - 6, 6, 0, TAU); g.ctx.fill(); g.ctx.restore(); }
    g.glow(x, ytop, 26, c.warm, 0.4); g.ball(x, ytop, 9, c.neutron);
    g.label(`about ${Etop.toFixed(0)} MeV above surface`, x - 16, ytop - 14, { color: c.soft, size: 11, align: "right", bg: true });
    // the two arrows: escape (up and out) and collide (down into the sea)
    const wE = 1 + 12 * emit, wC = 1 + 12 * (1 - emit);
    if (Etop > SEP) { g.arrow(x + 14, ytop - 6, x + ww * 0.42, yTop + 6, c.warm, wE, 0.9, 10 + wE); g.label(`escapes  ${(emit * 100).toFixed(0)}%`, x + ww * 0.42 + 6, yTop + 10, { color: c.warm, size: phone ? 11 : 13, weight: 600, align: "left", bg: true }); }
    else { g.label("below the free line: it cannot leave", x, yFree - 14, { color: c.soft, size: phone ? 11 : 12, bg: true }); }
    g.arrow(x - 14, ytop + 8, x - ww * 0.3, yFermi + (yFloor - yFermi) * 0.4, c.neutron, wC, 0.9, 10 + wC);
    g.label(`collides again  ${((1 - emit) * 100).toFixed(0)}%`, x - ww * 0.3 - 6, yFermi + (yFloor - yFermi) * 0.4 + 16, { color: c.neutron, size: phone ? 11 : 13, weight: 600, align: "right", bg: true });
    g.label(phone ? `n = ${n}: ${p} particles, ${h} hole${h > 1 ? "s" : ""}, ${E0} MeV` : `stage n = ${n}: ${p} particles and ${h} hole${h > 1 ? "s" : ""} share ${E0} MeV`, W / 2, H * 0.97, { color: c.ink, size: phone ? 13 : 16, weight: 600, serif: true });
  }

  // ---------- scene 4: the spectrum built from events ----------
  // Each reaction: the chain picks the stage at which the top neutron escapes (or none: evaporation later), then an
  // energy from that stage's shape, e (Emax - e)^(n-2) (the exciton-model emission spectrum with a flat inverse cross
  // section), or e exp(-e/T) for evaporation. Stage shares fall with n; the pre-equilibrium total grows with energy.
  const STAGES = [3, 5, 7, 9], STAGE_W = [0.55, 0.27, 0.12, 0.06], TEVAP = 1.2, ESPAN = 62, NCOL = 41;
  let run = null;
  function sampleEmission(E, r) {
    const F = 0.6 * clamp((E - 1) / 18, 0, 1);         // share that escapes during the chain (illustrative)
    let u = r(), stage = 0;
    for (let i = 0; i < 4; i++) { if (u < F * STAGE_W[i]) { stage = STAGES[i]; break; } u -= F * STAGE_W[i]; }
    let e;
    if (stage) { const m = stage - 2, emode = E / (m + 1), fmax = emode * Math.pow(E - emode, m); for (let k = 0; k < 200; k++) { e = r() * E; if (r() * fmax <= e * Math.pow(E - e, m)) break; } }
    else { do { e = -TEVAP * Math.log(Math.max(1e-9, r() * r())); } while (e > E); }
    return { stage, e };
  }
  function startRun(S, E, prefill) {
    if (run) run.fadeFrom = { counts: run.counts, cols: run.cols, t: S.time };
    const r = rng(Math.round(E * 31) + (S.runN = (S.runN || 0) + 1) * 977);
    const evs = []; for (let i = 0; i < 300; i++) evs.push(sampleEmission(E, r));
    run = { E, evs, next: 0, t0: S.time, fly: [], counts: new Array(NCOL).fill(0), cols: [], fadeFrom: run && run.fadeFrom };
    for (let k = 0; k < NCOL; k++) run.cols.push([]);
    for (let i = 0; i < prefill; i++) land(run, evs[i]); run.next = prefill; run.tNext = S.time + 0.3;
  }
  function colOf(e) { return clamp(Math.floor(e / ESPAN * NCOL), 0, NCOL - 1); }
  function land(R, ev) { const k = colOf(ev.e); R.counts[k]++; R.cols[k].push(ev.stage); }
  function stageStyle(c, st) { return st === 0 ? [c.neutron, 0.9] : [c.warm, [1, 0.62, 0.4, 0.26][STAGES.indexOf(st)]]; }
  function drawTail(g, S, dt) {
    const { W, H, c } = g; const phone = W < 600;
    if (!run) startRun(S, 20, 150);
    const tE = S.target.E; if (tE !== S.runLastE) { S.runLastE = tE; S.runLastT = S.time; }
    if (Math.abs(tE - run.E) > 0.01 && S.time - S.runLastT > 0.45) startRun(S, tE, 0);
    // small wells on the left
    const L0 = wells(g), sc = phone ? 0.5 : 0.52, ww = L0.ww * sc * 0.95, gap = W * 0.03;
    const px0 = W * 0.04, nx0 = px0 + ww + gap;
    const yFermi = H * 0.6, yFloor = H * 0.86, yFree = yFermi - (yFloor - yFermi) * 0.45, yTop = H * 0.16;
    const L = { yFermi, yFloor, yFree, yTop, ww, px0, nx0, phone, sideLabels: false };
    const Ymev = (e) => yFermi - (yFermi - yFree) * e / SEP;
    drawWellBase(g, L, true, S.time);
    // the pile on the right
    const x0 = nx0 + ww + W * (phone ? 0.06 : 0.07), x1 = W * 0.96, yB = H * 0.86, yT = H * 0.14;
    const colW = (x1 - x0) / NCOL, X = (e) => x0 + (x1 - x0) * e / ESPAN, r = Math.min(colW * 0.42, 4);
    let mx = 1; run.counts.forEach((v) => (mx = Math.max(mx, v)));
    const unit = Math.min(2 * r * 0.95, (yB - yT) / mx);
    const ctx = g.ctx;
    // fading previous batch
    if (run.fadeFrom) {
      const fa = 1 - smooth(run.fadeFrom.t, run.fadeFrom.t + 1.5, S.time);
      if (fa <= 0) run.fadeFrom = null;
      else run.fadeFrom.cols.forEach((col, k) => col.forEach((st, i) => { const [cl, a] = stageStyle(c, st); g.dot(x0 + (k + 0.5) * colW, yB - r - i * unit, r, cl, a * fa * 0.6); }));
    }
    run.cols.forEach((col, k) => col.forEach((st, i) => { const [cl, a] = stageStyle(c, st); g.dot(x0 + (k + 0.5) * colW, yB - r - i * unit, r, cl, a); }));
    g.line(x0 - 4, yB + 1, x1 + 2, yB + 1, c.line, 1.5);
    g.line(X(run.E), yB + 1, X(run.E), yB + 12, c.ink, 1.2, 0.8); g.label(`max ${run.E.toFixed(0)} MeV`, X(run.E), yB + 22, { color: c.ink, size: 11, bg: true });
    g.label("slow", x0, yB + 22, { color: c.faint, size: 11, align: "left" }); if (X(run.E) < x1 - 70) g.label("fast →", x1, yB + 22, { color: c.faint, size: 11, align: "right" });
    // launches: one reaction every 35 ms; the well shows the latest chain's stage
    while (run.next < run.evs.length && S.time >= run.tNext) {
      const ev = run.evs[run.next++]; run.tNext += 0.035; run.last = ev; run.lastT = S.time;
      run.fly.push({ ev, t0: S.time, sx: nx0 + ww * (0.3 + 0.4 * Math.random()), sy: clamp(Ymev(SEP + ev.e), yTop + 8, yFree - 6) });
    }
    if (run.last) {
      const n = run.last.stage || 9, p = (n + 1) / 2, h = (n - 1) / 2;
      for (let i = 1; i < p; i++) { const kind = i % 2 ? "p" : "n"; g.ball((kind === "p" ? px0 : nx0) + ww * (0.25 + 0.5 * ((i * 0.37) % 1)), yFermi - (yFermi - yFree) * (0.15 + 0.5 * Math.pow(0.75, i)), 4.5, kind === "p" ? c.proton : c.neutron, 0.85); }
      for (let i = 0; i < h; i++) { const kind = i % 2 ? "n" : "p"; const hx = (kind === "p" ? px0 : nx0) + ww * (0.3 + 0.2 * ((i * 2 + 1) % 3)), hy = seaRow(L, NR - 1 - Math.floor(i / 2)) - 6; g.dot(hx, hy, 6.5, c.paper); g.ring(hx, hy, 4.5, kind === "p" ? c.proton : c.neutron, 1.8, 0.9); }
      g.label(run.last.stage ? `stage ${run.last.stage}` : "chain over: compound", (px0 + nx0 + ww) / 2, yTop - 18, { color: run.last.stage ? c.warm : c.neutron, size: phone ? 11 : 12, weight: 600, bg: true });
    }
    for (let i = run.fly.length - 1; i >= 0; i--) {
      const f = run.fly[i], u = clamp((S.time - f.t0) / 0.9, 0, 1), k = colOf(f.ev.e);
      const tx = x0 + (k + 0.5) * colW, ty = yB - r - run.counts[k] * unit;
      const x = lerp(f.sx, tx, u), y = lerp(f.sy, ty, u) - Math.sin(u * Math.PI) * H * 0.12;
      const [cl, a] = stageStyle(c, f.ev.stage); g.dot(x, y, r + 1.5, cl, Math.min(1, a + 0.2)); g.ball(x, y, r + 0.5, f.ev.stage ? c.warm : c.neutron, a);
      if (u >= 1) { land(run, f.ev); run.fly.splice(i, 1); }
    }
    wellLabelsInside(g, L);
    // legend chips in exactly the pile's colours
    const items = [[3, "stage 3"], [5, "5"], [7, "7"], [9, "9"], [0, "evaporation"]];
    let lx = x0, ly = yT - 2;
    g.label(phone ? "left at:" : "neutron left at:", lx, ly, { color: c.soft, size: 11, align: "left" }); lx += phone ? 44 : 88;
    items.forEach(([st, nm]) => { const [cl, a] = stageStyle(c, st); g.dot(lx + 4, ly, 4.5, cl, a); g.label(nm, lx + 12, ly, { color: c.soft, size: 11, align: "left" }); ctx.save(); ctx.font = "500 11px sans-serif"; lx += 22 + ctx.measureText(nm).width; ctx.restore(); });
    const fast = run.cols.reduce((a, col) => a + col.filter((st) => st > 0).length, 0), tot = run.counts.reduce((a, b) => a + b, 0);
    g.label(`${tot} of 300 landed · ${fast} left during the chain`, (x0 + x1) / 2, H * 0.955, { color: c.ink, size: phone ? 12 : 14, weight: 600, serif: true });
  }

  // ---------- scene 5: counting arrangements on an evenly spaced ladder ----------
  const DEPTH = 8, UP = 17;   // filled rungs below the surface (the well bottom), empty rungs drawn above
  const cfgCache = {};
  function distinctSets(n, sum, lo, hi) {      // all sets of n distinct integers in [lo, hi] adding up to sum (ascending)
    const out = [], cur = [];
    (function rec(start, left, need) {
      if (need === 0) { if (left === 0) out.push(cur.slice()); return; }
      for (let v = start; v <= hi; v++) { if (v * need > left + 1e-9 && v > 0) break; cur.push(v); rec(v + 1, left - v, need - 1); cur.pop(); }
    })(lo, sum, n);
    return out;
  }
  function configs(p, h, U) {
    const key = p + "," + h + "," + U; if (cfgCache[key]) return cfgCache[key];
    const segs = []; let total = 0;
    for (let a = 0; a <= U; a++) {
      const P = distinctSets(p, a, 1, UP), Hs = distinctSets(h, U - a, 0, DEPTH - 1);
      if (P.length && Hs.length) { segs.push({ P, Hs, start: total }); total += P.length * Hs.length; }
    }
    return (cfgCache[key] = { segs, total });
  }
  function configAt(C, i) { let s = C.segs[0]; for (const q of C.segs) { if (q.start <= i) s = q; else break; } const j = i - s.start; return [s.P[Math.floor(j / s.Hs.length)], s.Hs[j % s.Hs.length]]; }
  function drawPauli(g, S) {
    const { W, H, c } = g; const phone = W < 600;
    const U = Math.round(S.target.U), pairs = S.ph || 1, p = pairs + 1, h = pairs;
    const key = p + "," + h + "," + U; if (S.cntKey !== key) { S.cntKey = key; S.cntT = S.time; }
    const C = configs(p, h, U);
    const x0 = W * (phone ? 0.06 : 0.08), ww = W * (phone ? 0.34 : 0.28), yFermi = H * 0.62, rung = Math.min((yFermi - H * 0.08) / UP, (H * 0.9 - yFermi) / DEPTH);
    const yUp = (k) => yFermi - k * rung, yDn = (j) => yFermi + (j + 0.5) * rung, yFloor = yDn(DEPTH - 1) + rung * 0.5;
    const ctx = g.ctx;
    // the well
    g.line(x0, yUp(UP) - 4, x0, yFloor, c.line, 2); g.line(x0 + ww, yUp(UP) - 4, x0 + ww, yFloor, c.line, 2); g.line(x0, yFloor, x0 + ww, yFloor, c.ink, 2.5, 0.7);
    ctx.save(); ctx.globalAlpha = 0.1; ctx.fillStyle = c.neutron; ctx.fillRect(x0 + 2, yFermi, ww - 4, yFloor - yFermi); ctx.restore();
    // the energy band in play: up to U above, down to min(U, depth) below
    const bandUp = yUp(Math.min(U, UP)), bandDn = Math.min(yFloor, yFermi + U * rung);
    [bandUp, bandDn].forEach((y) => { g.line(x0 + 2, y, x0 + ww - 2, y, c.warm, 1.5, 0.8); });
    g.line(x0 + ww * 0.08, bandUp, x0 + ww * 0.08, bandDn, c.warm, 3, 0.35);
    // which arrangement is showing: all of them, one after another, in about five seconds
    const rate = Math.max(5, C.total / 5), el = S.time - S.cntT, idx = Math.min(C.total - 1, Math.floor(el * rate));
    const finished = el * rate >= C.total, cycle = C.total / rate + 2;
    if (el > cycle) S.cntT = S.time;
    const [P, Hs] = C.total ? configAt(C, Math.max(0, idx)) : [[], []];
    const occ = {}; P.forEach((k) => (occ[k] = 1)); const hol = {}; Hs.forEach((j) => (hol[j] = 1));
    const r = Math.min(rung * 0.36, 7), bx = x0 + ww * 0.5;
    for (let k = 1; k <= UP; k++) { g.line(x0 + ww * 0.15, yUp(k), x0 + ww * 0.85, yUp(k), c.line, 1, 0.8, [3, 4]); if (occ[k]) g.ball(bx, yUp(k) - r, r, c.neutron); }
    for (let j = 0; j < DEPTH; j++) {
      g.line(x0 + ww * 0.15, yDn(j) + r, x0 + ww * 0.85, yDn(j) + r, c.line, 1);
      if (hol[j]) g.ring(bx, yDn(j), r * 0.9, c.neutron, 1.8, 0.95);
      else g.ball(bx + Math.sin(S.time * 1.7 + j) * 0.4, yDn(j), r, c.neutron, 0.75);
    }
    // links from each hole to a particle: who was lifted where (pairs only; the first particle is the incoming one)
    for (let q = 0; q < Hs.length; q++) { const k = P[P.length - 1 - q]; if (k) g.line(bx + r + 3, yDn(Hs[q]), bx + r + 3, yUp(k) - r, c.warm, 1, 0.35, [2, 3]); }
    g.line(x0 - 8, yFermi, x0 + ww + 8, yFermi, c.ink, 1.5, 0.8);
    g.label("Fermi surface", x0 + ww + 10, yFermi, { color: c.ink, size: phone ? 10 : 12, align: "left" });
    g.label(U >= DEPTH ? "well bottom: no deeper hole" : "bottom of the well", x0 + ww + 10, yFloor, { color: U >= DEPTH ? c.ink : c.faint, size: phone ? 10 : 11, align: "left" });
    if (!phone) g.label(`${U} MeV to share`, x0 + ww + 10, bandUp, { color: c.warm, size: 11, align: "left", bg: true });
    // the counter
    const tx = W * (phone ? 0.74 : 0.73), ty = H * 0.3;
    g.label(`${p} particles · ${h} hole${h > 1 ? "s" : ""}`, tx, ty - 46, { color: c.soft, size: phone ? 12 : 14 });
    g.label(`${(finished ? C.total : idx + 1).toLocaleString(WT.loc ? WT.loc() : "en-US")}`, tx, ty, { color: c.ink, size: phone ? 30 : 44, weight: 600, serif: true });
    g.label(finished ? "ways, all counted" : "arrangements so far", tx, ty + (phone ? 26 : 34), { color: c.soft, size: phone ? 11 : 13 });
    if (pairs < 3) { const C2 = configs(p + 1, h + 1, U); g.label(`one more pair: ${C2.total.toLocaleString(WT.loc ? WT.loc() : "en-US")} ways`, tx, ty + (phone ? 56 : 76), { color: c.faint, size: phone ? 11 : 12 }); }
    if (!phone) g.label("never two on one rung · holes only where a nucleon was", tx, ty + 104, { color: c.faint, size: 11 });
    // tally ticks: one per arrangement shown, up to 120, so the growth is visible
    const nt = Math.min(120, finished ? C.total : idx + 1), per = 20, tw = phone ? 4 : 6;
    for (let i = 0; i < nt; i++) { const col = i % per, row = Math.floor(i / per); g.line(tx - per * tw / 2 + col * tw, ty + 130 + row * 14, tx - per * tw / 2 + col * tw, ty + 140 + row * 14, c.warm, 1.5, 0.75); }
    if (C.total > 120) g.label(`(first 120 shown as ticks)`, tx, ty + 130 + 6 * 14 + 8, { color: c.faint, size: 10, alpha: nt >= 120 ? 1 : 0 });
  }

  // ---------- scene 6: clusters ----------
  function drawCluster(g, S) {
    const { W, H, c } = g; const phone = W < 600;
    const cx = W * 0.5, cy = H * 0.5, R = Math.min(W, H) * 0.2;
    const age = S.time - clusterT, P = 4.2, t = age < 0 ? -1 : age % P;
    g.nucleus(cx, cy, R, { N: 56, Z: 26, seed: 13, t: S.time, jiggle: 0.5, halo: c.warm, haloAlpha: 0.12 });
    g.ring(cx, cy, R * 1.12, c.faint, 1, 0.5, [3, 5]);
    if (t < 0) return;
    if (clusterKind === "d") {
      // a proton rises from inside toward the rim, grabs a surface neutron, and the pair leaves together
      const a = -0.5; const rise = smooth(0, 1.4, t), grab = smooth(1.4, 1.9, t), out = smooth(1.9, 3.6, t), fade = 1 - smooth(3.6, 4.2, t);
      const d = lerp(R * 0.2, R * 1.05, rise) + out * Math.max(W, H) * 0.4;
      const px = cx + Math.cos(a) * d, py = cy + Math.sin(a) * d;
      const sn = [cx + Math.cos(a + 0.25) * R * 1.0, cy + Math.sin(a + 0.25) * R * 1.0]; // the surface neutron waiting
      const nx = lerp(sn[0], px + 9, grab), ny = lerp(sn[1], py + 6, grab);
      g.glow(px, py, 20, c.warm, 0.4 * fade); g.ball(px, py, 7, c.proton, fade); g.ball(nx, ny, 7, c.neutron, fade);
      g.label(grab > 0.9 ? "a deuteron leaves" : rise > 0.95 ? "grabs a neutron at the edge" : "a fast proton heads out", cx, cy + R + 46, { color: c.ink, size: phone ? 13 : 16, serif: true, italic: true, alpha: fade });
    } else {
      // the incoming neutron hits a preformed alpha at the rim, which flies off; the neutron is absorbed
      const a = 0.6; const come = smooth(0, 1.3, t), hit = smooth(1.3, 1.5, t), out = smooth(1.5, 3.4, t), fade = 1 - smooth(3.4, 4.2, t);
      const ax = cx + Math.cos(a) * R * 0.95 + out * Math.cos(a - 0.4) * Math.max(W, H) * 0.42, ay = cy + Math.sin(a) * R * 0.95 + out * Math.sin(a - 0.4) * Math.max(W, H) * 0.42;
      g.glow(ax, ay, 22, c.alpha, 0.35 * fade); for (let i = 0; i < 4; i++) g.ball(ax + (i % 2) * 10 - 5, ay + (i > 1 ? 10 : 0) - 5, 6.5, i < 2 ? c.proton : c.neutron, fade);
      if (hit < 1) { const nx = lerp(cx - R * 3, cx + Math.cos(a) * R * 0.8, come), ny = lerp(cy - R * 0.9, cy + Math.sin(a) * R * 0.8, come); g.ball(nx, ny, 7, c.neutron, 1 - hit); }
      if (out < 0.02) g.label("an α (2 protons + 2 neutrons) waits at the edge", cx, cy + R + 46, { color: c.alpha, size: phone ? 12 : 14, serif: true, italic: true });
      else g.label("knocked straight out", cx, cy + R + 46, { color: c.ink, size: phone ? 13 : 16, serif: true, italic: true, alpha: fade });
    }
  }

  // ---------- scene 7: a second fast particle from the residual's excitons ----------
  function drawSecond(g, S) {
    const { W, H, c } = g; const phone = W < 600;
    const E = S.target.E, E0 = E + SEP;                    // energy above the Fermi surface carried in
    const L = wells(g); const { yFermi, yFloor, yTop, ww, px0, nx0 } = L;
    const k = (yFermi - yTop - 26) / Math.max(E0, 30), Ym = (e) => yFermi - e * k;
    L.yFree = Ym(SEP);
    drawWellBase(g, L, true, S.time);
    const P = 4.6, cyc = Math.floor((S.time - (S.secT || 0)) / P), t = (S.time - (S.secT || 0)) % P;
    // one reaction per cycle: the top neutron takes ~55 %, the other lifted nucleon a random part of the rest
    const r = rng(cyc * 7919 + 13); r();
    const eA = 0.55 * E0, uB = r(), eB = 0.45 * E0 * (0.1 + 0.55 * uB), eH = 0.45 * E0 - eB, kindB = r() < 0.5 ? "p" : "n";
    const second = eB > SEP;
    // tally over the last 12 reactions (seeded with the previous ones so it is never empty)
    let n2 = 0; for (let q = cyc - 11; q <= cyc; q++) { const rq = rng(q * 7919 + 13); rq(); const e = 0.45 * E0 * (0.1 + 0.55 * rq()); if (e > SEP) n2++; }
    const xA = nx0 + ww * 0.55, xB = (kindB === "p" ? px0 : nx0) + ww * (kindB === "p" ? 0.5 : 0.3), xH = (kindB === "p" ? px0 : nx0) + ww * 0.62;
    const yA = Ym(eA), yB = Ym(eB), yH = yFermi + Math.min(yFloor - yFermi - 8, eH * k * 0.6);
    const colB = kindB === "p" ? c.proton : c.neutron;
    const enter = smooth(0, 0.7, t), hit = smooth(0.7, 1.1, t), outA = smooth(1.3, 2.3, t), outB = second ? smooth(2.3, 3.3, t) : 0, calm = smooth(3.4, 4.2, t), fade = 1 - smooth(4.2, 4.6, t);
    const far = W * 0.6;
    if (hit < 1) { const y = lerp(yTop - 30, yA, enter); g.glow(xA, y, 22, c.warm, 0.45); g.ball(xA, y, 8, c.neutron); }
    else {
      // the hole left by the lifted nucleon
      g.dot(xH, yH, 7, c.paper, fade); g.ring(xH, yH, 6.5, colB, 2, fade);
      // top neutron: escapes first
      const ax = xA + outA * far, ay = yA - outA * H * 0.25;
      if (outA < 1) { g.glow(ax, ay, 20, c.warm, 0.4 * (1 - outA)); g.ball(ax, ay, 8, c.neutron, 1 - smooth(0.85, 1, outA)); }
      if (outA > 0.1 && outA < 0.95) g.label("first fast neutron", Math.min(ax, W - 70), ay - 18, { color: c.ink, size: 12, bg: true });
      // the second lifted nucleon: escapes only if it still sits above the free line
      const bx = xB + outB * far, by = yB - outB * H * 0.25 + (second ? 0 : Math.sin(S.time * 3) * 1.5);
      if (outB < 1) { g.glow(bx, by, 16 + 8 * (1 - calm), c.warm, (second ? 0.4 : 0.25) * (1 - calm * (second ? 0 : 0.6))); g.ball(bx, by, 7, colB, (1 - smooth(0.85, 1, outB)) * (second ? 1 : fade)); }
      if (second && outB > 0.1 && outB < 0.95) g.label(`second fast ${kindB === "p" ? "proton" : "neutron"}`, Math.min(bx, W - 80), by + 20, { color: c.warm, size: 12, bg: true });
      if (!second && t > 2.3 && t < 4.2) g.label(phone ? "below the free line: stays" : "below the free line: it stays", xB, yB - 16, { color: c.soft, size: 11, bg: true });
      if (calm > 0) { g.glow((px0 + nx0 + ww) / 2, yFermi, ww * 1.1, c.warm, 0.18 * calm * fade); g.label("the rest settles: compound nucleus", (px0 + nx0 + ww) / 2, yTop + 6, { color: c.soft, size: phone ? 11 : 13, italic: true, serif: true, alpha: calm * fade, bg: true }); }
    }
    g.label(`${E0.toFixed(0)} MeV carried in`, xA - 14, Ym(E0) - 4, { color: c.warm, size: 11, align: "right", bg: true, alpha: 1 - hit });
    g.label(`second fast particle in ${n2} of the last 12 reactions`, W / 2, H * 0.965, { color: n2 ? c.warm : c.ink, size: phone ? 13 : 15, weight: 600, serif: true });
  }
})();
