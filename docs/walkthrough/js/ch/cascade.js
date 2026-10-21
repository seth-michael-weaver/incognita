/* Chapter 8: the multi-chance cascade down the chart of nuclides (emission/).
 * Scenes (S.mode): "second"  = one neutron leaves the compound; the residual's excitation is a ball that drops by the
 *                              neutron's kinetic energy and lands on the residual's levels; landings stack up;
 *                   "chart"   = a corner of the chart of nuclides with the flux flowing square to square as streams;
 *                   "topdown" = two nuclei as shelves of balls, emptied top down: photons drop balls to lower shelves,
 *                              neutrons move them into the daughter, p and alpha take them off the picture;
 *                   "channels"= one history at a time, emitted particles collected in a tray that spells the channel;
 *                   "ends"    = fired reactions land on ground-state and isomer shelves; pile height = production.
 * The numbers come from a small flux-propagation model inside this file, built the way emission/multiple.py and
 * compound/continuum.py do it: nuclei in order of decreasing Z and N, bins top down, each bin's flux shared between
 * exits by T x rho, particle flux landing on the daughter's bins, photon flux on the bins below. Separation energies
 * are illustrative for an iron-like target. */
(function () {
  const { TAU, clamp, lerp, smooth, rng } = WT.util;
  // window of the chart: dz = Z - Zcompound (0, -1, -2), dn = N - Ncompound (0..-3). S = [S_n, S_p, S_alpha] MeV.
  const NUC = {
    "0,0": { S: [7.6, 10.6, 7.3], ch: "(n,γ)", name: "compound" },
    "0,-1": { S: [11.2, 10.2, 7.6], ch: "(n,n′)", name: "target" },
    "0,-2": { S: [9.3, 9.2, 8.4], ch: "(n,2n)" },
    "0,-3": { S: [13.4, 8.9, 8.4], ch: "(n,3n)" },
    "-1,0": { S: [7.3, 6.5, 7.0], ch: "(n,p)" },
    "-1,-1": { S: [10.2, 8.1, 7.9], ch: "(n,np)", iso: 0.35 },
    "-1,-2": { S: [9.0, 7.6, 7.6], ch: "(n,2np)" },
    "-1,-3": { S: [12.0, 7.0, 8.0], ch: "(n,3np)" },
    "-2,0": { S: [8.5, 9.0, 7.8], ch: "(n,2p)" },
    "-2,-1": { S: [9.9, 9.8, 8.0], ch: "(n,n2p)" },
    "-2,-2": { S: [9.7, 11.0, 8.1], ch: "(n,α)", iso: 0.6 },
    "-2,-3": { S: [12.0, 10.5, 8.5], ch: "(n,nα)" },
  };
  const KEYS = Object.keys(NUC);
  const EXITS = [{ k: "n", dz: 0, dn: -1, col: "neutron" }, { k: "p", dz: -1, dn: 0, col: "proton" }, { k: "a", dz: -2, dn: -2, col: "alpha" }];
  const BAR = { p: 4.0, a: 7.5 }, BW = { p: 0.6, a: 0.4 };          // logistic steepness ~ Coulomb tunnelling
  const ATILDE = 8.0, DELTA = 1.6, EMATCH = 6.5;
  function rho(U) { if (U <= 0.05) return 1; const s = Math.sqrt(Math.max(2.5, 11.4 * Math.sqrt(U / ATILDE))); return Math.exp(2 * Math.sqrt(ATILDE * U)) / (12 * Math.SQRT2 * s * Math.pow(ATILDE, 0.25) * Math.pow(U, 1.25)); }
  const rhoFG = (Ex) => rho(Ex - DELTA);
  const CT = (() => { const h = 0.02, sl = (Math.log(rhoFG(EMATCH + h)) - Math.log(rhoFG(EMATCH - h))) / (2 * h); const T = 1 / sl; return { T, E0: EMATCH - T * Math.log(T * rhoFG(EMATCH)) }; })();
  const rhoRes = (Ex) => (Ex < 0 ? 0 : Ex < EMATCH ? Math.exp((Ex - CT.E0) / CT.T) / CT.T : rhoFG(Ex));
  const Tn = (e) => (e <= 0 ? 0 : 1 - Math.exp(-2.2 * Math.sqrt(e)));
  const Tc = (e, k) => (e <= 0 ? 0 : 1 / (1 + Math.exp((BAR[k] - e) / BW[k])));
  const Tx = (k, e) => (k === "n" ? 2 * Tn(e) : k === "p" ? 2 * Tc(e, "p") : Tc(e, "a"));
  const DE = 0.5;                                                   // bin width, MeV
  const SC = NUC["0,0"].S[0];
  // photon exit scale, fixed so that the photon share is ~1 % half an MeV above the compound's neutron threshold
  const GAMK = (() => { const Ex = SC + 0.5, b = Math.round(Ex / DE); let wg = 0, wn = 0; for (let k = 0; k < b; k++) { const Eg = (b - k) * DE; wg += Eg * Eg * Eg * rhoRes(k * DE) * DE; } for (let k = 0; k < 40; k++) { const eps = Ex - SC - k * DE; if (eps <= 0) break; wn += Tx("n", eps) * rhoRes(k * DE) * DE; } return 0.01 * wn / wg; })();

  /** Decay widths of bin b of nucleus key: photon (to bins below) and the three particles (to the daughters' bins). */
  function binWidths(key, b) {
    const [dz, dn] = key.split(",").map(Number), nuc = NUC[key], Ex = b * DE;
    const w = { g: 0, n: 0, p: 0, a: 0 }, dest = { g: [], n: [], p: [], a: [] };
    for (let k = 0; k < b; k++) { const Eg = (b - k) * DE; const v = GAMK * Eg * Eg * Eg * rhoRes(k * DE) * DE; w.g += v; dest.g.push([k, v]); }
    EXITS.forEach((ex, i) => {
      const S = nuc.S[i];
      for (let k = 0; k < 200; k++) { const eps = Ex - S - k * DE; if (eps <= 0) break; const v = Tx(ex.k, eps) * rhoRes(k * DE) * DE; if (v > 0) { w[ex.k] += v; dest[ex.k].push([k, v]); } }
      dest[ex.k].dkey = `${dz + ex.dz},${dn + ex.dn}`;
    });
    return { w, dest };
  }

  /** Propagate unit flux from the compound nucleus at excitation S_n + Einc through the window. */
  function cascade(Einc) {
    const Etop = SC + Einc;
    const nb = Math.ceil(Etop / DE) + 1;
    const pop = {}, ends = {}, flow = {};
    for (const key of KEYS) { pop[key] = new Float64Array(nb); ends[key] = 0; flow[key] = { g: 0, n: 0, p: 0, a: 0 }; }
    pop["0,0"][Math.min(nb - 1, Math.round(Etop / DE))] = 1;
    const order = KEYS.slice().sort((a, b) => { const [za, na] = a.split(",").map(Number), [zb, nbb] = b.split(",").map(Number); return zb - za || nbb - na; });
    for (const key of order) {
      const nuc = NUC[key], P = pop[key], Smin = Math.min(...nuc.S);
      for (let b = nb - 1; b >= 0; b--) {
        const f = P[b]; if (f <= 0) continue;
        if (b * DE < Smin) { ends[key] += f; continue; }
        const { w, dest } = binWidths(key, b);
        const tot = w.g + w.n + w.p + w.a; if (tot <= 0) { ends[key] += f; continue; }
        for (const x of ["g", "n", "p", "a"]) {
          const share = f * w[x] / tot; if (share <= 0) continue; flow[key][x] += share;
          const target = x === "g" ? P : pop[dest[x].dkey];
          if (!target) continue;                                   // outside the window: counted as leaving the picture
          for (const [k, v] of dest[x]) if (k < nb) target[k] += share * v / w[x];
        }
      }
    }
    return { Etop, nb, pop, ends, flow };
  }
  const cache = {};
  function model(E) { const k = (Math.round(E * 2) / 2).toFixed(1); return cache[k] || (cache[k] = cascade(parseFloat(k))); }
  /** Residual excitation after the first neutron leaves the compound at incoming energy E: weights T_n(eps) rho(Er). */
  function firstEmission(E) { const out = []; for (let Er = 0; Er < E; Er += 0.1) out.push([Er, Tx("n", E - Er) * rhoRes(Er)]); return out; }
  function pick(arr, r) { let t = 0; for (const a of arr) t += a[1]; let u = r * t; for (const a of arr) { if (u < a[1]) return a[0]; u -= a[1]; } return arr.length ? arr[arr.length - 1][0] : 0; }

  const hops = [];                                     // step 1: reactions hopping across the chart
  const drops = [], batches = [];                      // step 4: reactions landing on shelves
  const landed = [];                                   // step 0: where each residual's excitation landed
  let td = null;                                       // step 2: shelf simulation
  const CHANNELS = ["(n,2n)", "(n,n′)", "(n,p)", "(n,np)", "(n,α)", "(n,3n)", "(n,γ)"];

  WT.chapter("cascade", {
    num: "Chapter 8", title: "Down the chart", short: "Cascade",
    lead: "One emission is rarely the end: the nucleus left behind is often hot enough to emit again.",
    html: `
<div class="step">
  <p>A neutron has left the compound nucleus (left), and the <b>residual</b> it leaves behind (right) is still hot. The orange ball is the energy. The residual's ground state sits higher by the neutron's <b>separation energy</b> S<sub>n</sub>, the cost of pulling it out.</p>
  <p>Each time a neutron leaves, the ball drops by the neutron's kinetic energy. Where it stops is the residual's <b>excitation</b>, its spare energy; the dots on the right count the landings.</p>
  <div class="ctl"><label for="cs-e">Neutron energy</label><input id="cs-e" type="range" data-bind="E" min="1" max="30" step="0.5" value="15"><output data-show="E" data-fmt="1"></output></div>
  <p>Emitted neutrons are usually slow, so most drops are short. Blue dots sit above the dashed neutron threshold: they can afford a second neutron, the (n,2n) reaction. Below about 11 MeV none get there.</p>
</div>
<div class="step">
  <h3>A walk across the chart</h3>
  <p>The streams are reactions walking across a corner of the <b>chart of nuclides</b>, nuclei mapped by neutron number N (across) and proton number Z (up). Each starts in the outlined compound square; each square is named for the reaction that ends there.</p>
  <p>A <em class="n">neutron</em> out moves one square left, a <em class="p">proton</em> one down, an <em class="a">alpha particle</em> (two protons, two neutrons) two diagonally. Stream width is how much takes that step; shade and percentage are where reactions end.</p>
  <div class="btns"><button class="btn" data-act="fire">Fire 200 reactions</button></div>
  <p>Each step costs 7 to 11 MeV of separation energy, so even at 30 MeV the walk is three or four steps at most.</p>
</div>
<div class="step">
  <h3>Top down, bin by bin</h3>
  <p>The engine empties each nucleus from the top down, one energy slice, or <b>bin</b>, at a time. Right: the residual from the first emission; left: its daughter, one neutron fewer. Orange balls are reactions waiting in each bin. Bins are 1 MeV here; the engine uses about 40 per nucleus, sized to the energy available.</p>
  <p>As the marker sweeps a bin, each ball takes an exit by the competition of Chapter 6: a photon (<em class="g">γ</em>) drops it to a lower bin, a <em class="n">neutron</em> moves it into the daughter, a proton or alpha takes it off the picture. Below every threshold, photons carry the rest to the ground state (grey). Then the daughter is swept.</p>
  <div class="ctl"><label for="cs-e3">Neutron energy</label><input id="cs-e3" type="range" data-bind="E" min="8" max="30" step="0.5" value="18"><output data-show="E" data-fmt="1"></output></div>
  <div class="btns"><button class="btn ghost" data-act="restart">Start again</button></div>
  <p>Photons only fall, and each nucleus is finished before its daughters, so nothing lands on a bin already emptied.</p>
</div>
<div class="step">
  <h3>Naming the history</h3>
  <p>One reaction plays at a time: the marker hops across the chart and each particle emitted falls into the tray. The full tray names the <b>exclusive channel</b>, such as (n,2n); photons do not count. The engine gives each channel its own cross section (its likelihood, as an effective target area).</p>
  <div class="btns"><button class="btn ghost" data-act="next">Next channel</button></div>
  <p>Step through them. (n,np) plays twice, neutron first and proton first: same square, same tray, one channel. Then a ghost deuteron (a bound proton and neutron) reaches that square in one hop: its tray reads d, a different channel, (n,d).</p>
</div>
<div class="step">
  <h3>Where everything ends</h3>
  <p>Each square now holds shelves: ink for the <b>ground state</b>, green (on two squares) for an <b>isomer</b>, an excited state long-lived enough to count as a separate product. Pile height is the <b>residual production</b>: how much of each nucleus the reactions made.</p>
  <div class="ctl"><label for="cs-e2">Neutron energy</label><input id="cs-e2" type="range" data-bind="E" min="1" max="30" step="0.5" value="14"><output data-show="E" data-fmt="1"></output></div>
  <div class="btns"><button class="btn" data-act="fire">Fire 200 reactions</button></div>
  <p>Drag the energy: the next batch uses it and old piles fade. Production moves away from the start as more particles can leave. Every history ends on a shelf, and an activation measurement sees exactly these piles: irradiate a sample, then count each product's decays.</p>
  <div class="aside">In the code: <code>emission/multiple.py</code> (the loop over nuclei and bins, the γ cascade), <code>emission/feeding.py</code> (grids and inputs for every nucleus of the chain), <code>compound/continuum.py</code> (the decay of one bin), <code>emission/channels.py</code> (exclusive channels, residual production, isomer branches), <code>emission/binary.py</code> (the first emission's bookkeeping).</div>
</div>`,
    setup(S) {
      S.set("mode", "second"); S.to("E", 15, true); S.chan = 0; S.fireN = 0; S.chanT = 0;
      S.on("fire", () => {
        S.fireN++; const E = S.target.E, m = model(E), r = rng(S.fireN * 53 + 1);
        if (S.mode === "ends") fireBatch(S, E, 200);
        else for (let i = 0; i < 200; i++) hops.push(samplePath(m, r, S.time + i * 0.02));
      });
      S.on("next", () => { S.chan = (S.chan + 1) % CHANNELS.length; S.chanT = S.time; });
      S.on("restart", () => { td = null; });
    },
    steps: [
      (S) => { S.set("mode", "second"); S.to("E", 15); landed.length = 0; S.lastE0 = -1; },
      (S) => { S.set("mode", "chart"); S.to("E", 14); hops.length = 0; const m = model(14), r = rng(7); for (let i = 0; i < 60; i++) hops.push(samplePath(m, r, S.time + 0.3 + i * 0.05)); },
      (S) => { S.set("mode", "topdown"); S.to("E", 18); td = null; },
      (S) => { S.set("mode", "channels"); S.to("E", 16); S.chanT = S.time; },
      (S) => { S.set("mode", "ends"); S.to("E", 14); drops.length = 0; batches.length = 0; fireBatch(S, 14, 200, true); S.lastBatchE = 14; S.lastTE = 14; S.lastTEt = S.time; },
    ],
    frame(g, S, dt) {
      if (S.mode === "second") drawSecond(g, S, dt);
      else if (S.mode === "chart") drawChart(g, S);
      else if (S.mode === "topdown") drawTopDown(g, S, dt);
      else if (S.mode === "channels") drawChannels(g, S);
      else drawEnds(g, S);
    },
  });

  /** A random path over the squares, following the per-nucleus flow fractions (a Markov walk consistent with the totals). */
  function samplePath(m, r, t0) {
    const path = [[0, 0]]; let dz = 0, dn = 0, guard = 0;
    while (guard++ < 6) {
      const key = `${dz},${dn}`, fl = m.flow[key]; if (!fl) break;
      const tot = fl.n + fl.p + fl.a + m.ends[key]; if (tot <= 0) break;
      let u = r() * tot; let moved = false;
      for (const ex of EXITS) { if (u < fl[ex.k]) { dz += ex.dz; dn += ex.dn; path.push([dz, dn]); moved = true; break; } u -= fl[ex.k]; }
      if (!moved) break;
      if (!NUC[`${dz},${dn}`]) break;
    }
    return { path, t0, u: r() };
  }

  // ---------- geometry of the chart window: touching tiles like a real chart, ghost tiles beyond ----------
  function grid(g, tray) {
    const { W, H } = g; const phone = W < 600;
    const cols = 4, rows = 3;
    const cell = Math.min(W * (phone ? 0.74 : 0.62) / cols, H * (tray ? 0.5 : 0.62) / rows);
    const cx = W * 0.5 + cell * 0.12, top = tray ? Math.max(H * 0.08, (H - cell * (rows + 1.15)) / 2) : H * 0.5 - cell * rows / 2 - 10;
    const x0 = cx - cell * cols / 2 + cell / 2, y0 = top + cell / 2;
    return { cell, sq: cell - 4, X: (dn) => x0 + (dn + 3) * cell, Y: (dz) => y0 - dz * cell, phone, left: x0 - cell / 2, right: x0 + cell * (cols - 0.5), top, bottom: top + cell * rows };
  }
  function rr(ctx, x, y, w, h, r) { ctx.beginPath(); if (ctx.roundRect) ctx.roundRect(x, y, w, h, r); else ctx.rect(x, y, w, h); }
  /** Chart base: ghost neighbours fading out, the window's tiles, axis numbers. fill(key) -> [color, alpha] or null. */
  function drawChartBase(g, G, fill, labelAlpha = 1) {
    const { c } = g, ctx = g.ctx, { cell, sq } = G;
    for (let dz = 2; dz >= -4; dz--) for (let dn = -6; dn <= 2; dn++) {
      if (NUC[`${dz},${dn}`]) continue;
      const ddz = dz > 0 ? dz : dz < -2 ? -2 - dz : 0, ddn = dn > 0 ? dn : dn < -3 ? -3 - dn : 0, d = Math.hypot(ddz, ddn);
      const a = 0.55 * Math.max(0, 1 - d / 2.2); if (a < 0.03) continue;
      const x = G.X(dn), y = G.Y(dz); ctx.save(); ctx.globalAlpha = a; ctx.strokeStyle = c.line; ctx.lineWidth = 1; rr(ctx, x - sq / 2, y - sq / 2, sq, sq, 4); ctx.stroke(); ctx.restore();
    }
    for (const key of KEYS) {
      const [dz, dn] = key.split(",").map(Number), x = G.X(dn), y = G.Y(dz);
      ctx.fillStyle = c.card; rr(ctx, x - sq / 2, y - sq / 2, sq, sq, 4); ctx.fill();
      const f = fill && fill(key); if (f) { ctx.save(); ctx.globalAlpha = f[1]; ctx.fillStyle = f[0]; rr(ctx, x - sq / 2, y - sq / 2, sq, sq, 4); ctx.fill(); ctx.restore(); }
      ctx.strokeStyle = g.rgba(c.ink, key === "0,0" ? 0.85 : 0.18); ctx.lineWidth = key === "0,0" ? 2.2 : 1; rr(ctx, x - sq / 2, y - sq / 2, sq, sq, 4); ctx.stroke();
      g.label(NUC[key].ch, x - sq / 2 + 5, y - sq / 2 + 11, { color: c.ink, size: G.phone ? 10 : 12, weight: 600, alpha: labelAlpha, align: "left" });
    }
    g.label("compound", G.X(0), G.top - 10, { color: c.ink, size: G.phone ? 10 : 11, weight: 600 });
    g.label("target", G.X(-1), G.top - 10, { color: c.soft, size: G.phone ? 10 : 11 });
    const fs = G.phone ? 10 : 11;
    ["N−2", "N−1", "N", "N+1"].forEach((s, i) => g.label(s, G.X(i - 3), G.bottom + 10, { color: c.faint, size: fs }));
    ["Z", "Z−1", "Z−2"].forEach((s, i) => g.label(s, G.left - 8, G.Y(-i), { color: c.faint, size: fs, align: "right" }));
    g.label("neutron number →", (G.left + G.right) / 2, G.bottom + 24, { color: c.faint, size: fs });
  }
  /** Point on the hop curve between two squares (alpha hops bow out so they do not cross the square between). */
  function hopPt(G, a, b, u) {
    const vert = a[1] === b[1] ? G.cell * (G.vshift || 0) : 0;
    const x1 = G.X(a[1]) + vert, y1 = G.Y(a[0]), x2 = G.X(b[1]) + vert, y2 = G.Y(b[0]);
    const diag = a[0] - b[0] === 2, bow = diag ? G.cell * 0.42 : G.cell * 0.08;
    const mx = (x1 + x2) / 2, my = (y1 + y2) / 2, L = Math.hypot(x2 - x1, y2 - y1) || 1;
    const qx = mx + (-(y2 - y1) / L) * bow, qy = my + ((x2 - x1) / L) * bow;
    const v = 1 - u; return [v * v * x1 + 2 * v * u * qx + u * u * x2, v * v * y1 + 2 * v * u * qy + u * u * y2];
  }
  function strokeHop(g, G, a, b, color, w, alpha, u0 = 0, u1 = 1, dash) {
    const pts = []; for (let i = 0; i <= 20; i++) pts.push(hopPt(G, a, b, lerp(u0, u1, i / 20)));
    g.poly(pts, color, w, alpha, dash);
  }
  const exitOf = (a, b) => EXITS.find((e) => e.dz === b[0] - a[0] && e.dn === b[1] - a[1]);
  const keyOf = (p) => `${p[0]},${p[1]}`;

  // ---------- scene 1: the residual is still hot ----------
  function levelLines(xc, hw, e0, eTop, Y, g) {
    // rungs at the energies where the counted number of levels passes 1, 2, 3, ...: sparse low, crowding higher up;
    // once they are closer than ~4 px the continuum is drawn as fine lines that darken with energy. Ends fade out.
    const { c } = g, ctx = g.ctx;
    const gr = ctx.createLinearGradient(xc - hw, 0, xc + hw, 0);
    gr.addColorStop(0, g.rgba(c.ink, 0)); gr.addColorStop(0.18, g.rgba(c.ink, 1)); gr.addColorStop(0.82, g.rgba(c.ink, 1)); gr.addColorStop(1, g.rgba(c.ink, 0));
    ctx.save(); ctx.strokeStyle = gr; ctx.lineWidth = 1;
    let last = Infinity, eC = null;
    for (let k = 1; k < 400; k++) {
      const e = CT.E0 + CT.T * Math.log(k + Math.exp(-CT.E0 / CT.T)); if (e <= 0.05) continue; if (e > eTop) break;
      const y = Y(e0 + e); if (last - y < 4) { eC = e; break; }
      ctx.globalAlpha = 0.45; ctx.beginPath(); ctx.moveTo(xc - hw, y); ctx.lineTo(xc + hw, y); ctx.stroke(); last = y;
    }
    if (eC != null) for (let y = last - 3; y > Y(e0 + eTop); y -= 3) { const f = (last - y) / (last - Y(e0 + eTop)); ctx.globalAlpha = 0.1 + 0.22 * f * (1 - smooth(0.85, 1, f)); ctx.beginPath(); ctx.moveTo(xc - hw, y); ctx.lineTo(xc + hw, y); ctx.stroke(); }
    ctx.restore();
    g.line(xc - hw, Y(e0), xc + hw, Y(e0), c.ink, 3);
    return eC;
  }
  function drawSecond(g, S, dt) {
    const { W, H, c } = g, phone = W < 600;
    const E = clamp(S.target.E, 1, 30), Emax = 40;
    const yBot = H * 0.88, yTop = H * 0.07, Y = (e) => yBot - (yBot - yTop) * e / Emax;
    const hw = Math.min(W * (phone ? 0.11 : 0.085), 62), xa = W * (phone ? 0.2 : 0.2), xb = W * (phone ? 0.56 : 0.52);
    const S1 = NUC["0,-1"].S[0], Ec = SC + E;
    if (Math.abs(E - (S.lastE0 ?? -1)) > 0.01) {        // new energy: start a fresh stack, seeded so it is never empty
      S.lastE0 = E; landed.length = 0; S.evT = S.time; S.flying = [];
      const fe = firstEmission(E), r = rng(Math.round(E * 10) + 3); for (let i = 0; i < 40; i++) landed.push({ Er: pick(fe, r()), t: -9 });
    }
    // columns: compound ground at 0, residual ground one separation energy higher
    levelLines(xa, hw, 0, Ec + 2, Y, g);
    const eC = levelLines(xb, hw, SC, Emax - SC, Y, g);
    if (!phone && eC != null) { g.label("levels", xb + hw + 6, Y(SC + 1.2), { color: c.faint, size: 10, align: "left" }); }
    g.line(xa + hw + 6, Y(0), xb - hw - 6, Y(0), c.faint, 1, 0.8, [3, 4]);
    g.arrow(xb - hw - 12, Y(0) - 2, xb - hw - 12, Y(SC) + 4, c.soft, 1.3, 0.9, 6);
    g.label(phone ? `Sₙ ${SC} MeV` : `Sₙ = ${SC} MeV`, xb - hw - 18, (Y(0) + Y(SC)) / 2, { color: c.soft, size: 11, align: "right", bg: true });
    g.label("compound", xa, yBot + 16, { color: c.ink, size: phone ? 11 : 13, weight: 600 });
    g.label("ground", xa, Y(0) - 9, { color: c.faint, size: 10 });
    g.label(phone ? "residual" : "residual (one neutron fewer)", xb, Y(SC) + 14, { color: c.ink, size: phone ? 11 : 13, weight: 600, bg: true });
    // the residual's own neutron threshold
    const yT = Y(SC + S1);
    g.line(xb - hw - 4, yT, xb + hw + 4, yT, c.neutron, 1.5, 0.9, [5, 4]);
    g.label(phone ? "n threshold" : "its neutron threshold", xb, yT - 10, { color: c.neutron, size: 11, bg: true });
    // compound state
    const yc = Y(Ec) + Math.sin(S.time * 2.4) * 1.5;
    g.glow(xa, yc, 24, c.warm, 0.55); g.ball(xa, yc, 7, c.warm);
    g.label(`${Ec.toFixed(1)} MeV`, phone ? xa + hw + 6 : xa - hw - 8, Y(Ec), { color: c.warm, size: 12, align: phone ? "left" : "right", weight: 600, bg: true });
    // events: cross over at the same energy, then drop by the neutron's kinetic energy
    const fe = firstEmission(E);
    if (S.time - S.evT > 0.6) { S.evT = S.time; if (S.flying.length < 6) S.flying.push({ Er: pick(fe, Math.random()), t0: S.time, x: (Math.random() - 0.5) * 1.4 * hw }); }
    for (let i = S.flying.length - 1; i >= 0; i--) {
      const f = S.flying[i], age = S.time - f.t0, eps = E - f.Er;
      const cross = smooth(0, 0.6, age), drop = smooth(0.6, 0.6 + 0.25 + 0.04 * eps, age);
      const x = lerp(xa, xb + f.x, cross), e = lerp(Ec, SC + f.Er, drop), y = Y(e);
      // the neutron: leaves from the crossing point, speed ~ sqrt(kinetic energy)
      const na = age - 0.55; if (na > 0 && na < 1.6) { const sp = 120 + 90 * Math.sqrt(Math.max(eps, 0.05)); g.ball(xb + hw + 10 + na * sp, Y(Ec) - na * 30, 5, c.neutron, 1 - smooth(1.1, 1.6, na)); }
      if (age > 0.6 && drop < 1) { g.line(xb + f.x, Y(Ec), xb + f.x, y, c.warm, 1.5, 0.45, [2, 3]); if (!phone && eps > 2) g.label("drop = neutron's kinetic energy", xb + f.x - hw * 0.2 - 8, (Y(Ec) + y) / 2, { color: c.warm, size: 10, align: "right", bg: true, alpha: 0.9 * (1 - drop) }); }
      g.glow(x, y, 14, c.warm, 0.4); g.ball(x, y, 5.5, c.warm);
      if (drop >= 1) { landed.push({ Er: f.Er, t: S.time }); if (landed.length > 220) landed.shift(); S.flying.splice(i, 1); }
    }
    // the stack: one dot per landing, rows of 1 MeV, to the right of the residual
    const rowE = 1, xs = xb + hw + 8, maxW = W - xs - 14, dot = phone ? 2.4 : 3;
    const counts = {}; let above = 0;
    for (const L of landed) { const row = Math.floor(L.Er / rowE); counts[row] = (counts[row] || 0) + 1; if (L.Er >= S1) above++; }
    let mxc = 0; for (const k in counts) mxc = Math.max(mxc, counts[k]);
    const step = Math.min(dot * 2.4, maxW / Math.max(mxc, 1));
    const seen = {};
    for (const L of landed) {
      const row = Math.floor(L.Er / rowE), k = (seen[row] = (seen[row] || 0) + 1) - 1;
      const x = xs + k * step + dot, y = Y(SC + (row + 0.5) * rowE), fresh = 1 - smooth(0, 0.5, S.time - L.t);
      g.dot(x, y, dot + fresh * 2, L.Er >= S1 ? c.neutron : c.warm, 0.85);
    }
    const frac = landed.length ? above / landed.length : 0;
    const msg = frac > 0.004 ? `${Math.round(frac * 100) || "<1"} % land above the threshold: a second neutron can leave` : "all land below the threshold: only photons remain";
    g.label(phone ? (frac > 0.004 ? `${Math.round(frac * 100) || "<1"} % above threshold: (n,2n) possible` : "all below threshold: photons only") : msg, W * 0.5, H - 14, { color: frac > 0.004 ? c.neutron : c.ink, size: phone ? 12 : 14, weight: 600, serif: true, bg: true });
  }

  // ---------- scene 2: the chart with the flux flowing ----------
  function drawChart(g, S) {
    const { W, H, c } = g;
    const E = 14, m = model(E), G = grid(g, false);
    let mxEnd = 0; for (const k in m.ends) mxEnd = Math.max(mxEnd, m.ends[k]);
    drawChartBase(g, G, (key) => [c.accent, mxEnd > 0 ? 0.04 + 0.42 * Math.sqrt(m.ends[key] / mxEnd) : 0]);
    for (const key of KEYS) {
      const [dz, dn] = key.split(",").map(Number), end = m.ends[key];
      g.label(end >= 0.0005 ? `${(end * 100).toFixed(end < 0.01 ? 1 : 0)} %` : "", G.X(dn), G.Y(dz) + G.sq * 0.3, { color: c.ink, size: G.phone ? 11 : 14, serif: true, weight: 600 });
    }
    // streams: width ~ sqrt(flow), particles drifting along them all the time (proton streams run right of centre, clear of the labels)
    G.vshift = 0.22;
    let mxFlow = 0; for (const k in m.flow) for (const x of ["n", "p", "a"]) mxFlow = Math.max(mxFlow, m.flow[k][x]);
    for (const key of KEYS) {
      const a = key.split(",").map(Number);
      for (const ex of EXITS) {
        const f = m.flow[key][ex.k]; if (f < 0.002 * mxFlow) continue;
        const b = [a[0] + ex.dz, a[1] + ex.dn]; if (!NUC[keyOf(b)]) continue;
        const wgt = Math.sqrt(f / mxFlow), col = c[ex.col];
        strokeHop(g, G, a, b, col, 3 + 16 * wgt, 0.16, 0.12, 0.88);
        strokeHop(g, G, a, b, col, 1.2, 0.5, 0.12, 0.88);
        const [hx, hy] = hopPt(G, a, b, 0.88), [px, py] = hopPt(G, a, b, 0.8);
        g.arrow(px, py, hx, hy, col, 1.2, 0.7, 6 + 5 * wgt);
        const nd = Math.max(1, Math.round(7 * wgt));
        for (let i = 0; i < nd; i++) { const u = 0.12 + 0.76 * ((S.time * 0.35 + i / nd) % 1); const [x, y] = hopPt(G, a, b, u); g.dot(x, y, 2 + 2 * wgt, col, 0.85 * Math.sin(Math.PI * (u - 0.12) / 0.76)); }
      }
    }
    G.vshift = 0;
    drawHops(g, S, G);
    g.label(`incoming neutron: ${E.toFixed(0)} MeV`, W * 0.5, H * 0.05, { color: c.ink, size: G.phone ? 13 : 15, weight: 600, serif: true, bg: true });
    g.label(G.phone ? "shade and % = where reactions end" : "stream width = flow · shade and % = share of reactions that end in that nucleus", W * 0.5, H - 18, { color: c.soft, size: 12, bg: true });
  }
  function drawHops(g, S, G) {
    const { c } = g;
    for (let i = hops.length - 1; i >= 0; i--) {
      const h = hops[i], age = S.time - h.t0; if (age < 0) continue;
      const seg = Math.floor(age / 0.55), u = (age / 0.55) % 1, n = h.path.length - 1;
      if (seg > n) { hops.splice(i, 1); continue; }
      if (seg === n) { const p = h.path[n]; g.ring(G.X(p[1]) + (h.u - 0.5) * G.sq * 0.5, G.Y(p[0]) + G.sq * 0.08, 3 + 10 * u, c.accent, 1.5, 0.8 * (1 - u)); continue; }
      const a = h.path[seg], b = h.path[seg + 1], ex = exitOf(a, b);
      const [x, y] = hopPt(G, a, b, smooth(0, 1, u));
      g.ball(x, y - 5 * Math.sin(u * Math.PI), 4.5, c[ex ? ex.col : "neutron"]);
    }
  }

  // ---------- scene 3: top down, shelves of balls ----------
  const TD_KEYS = ["0,-1", "0,-2"];
  function newTD(E) {
    const s = { E, shelves: [[], []], fly: [], gone: 0, phase: 0, cur: -1, wait: 0.8, done: [[], []] };
    const nShelf = Math.ceil(E) + 1; s.n = nShelf;
    for (let j = 0; j < 2; j++) for (let k = 0; k < nShelf; k++) { s.shelves[j].push([]); s.done[j].push(false); }
    const fe = firstEmission(E), r = rng(Math.round(E * 7) + 11);
    for (let i = 0; i < 44; i++) { const Er = pick(fe, r()); s.shelves[0][Math.min(nShelf - 1, Math.floor(Er))].push({ id: i, cold: false }); }
    s.cur = nShelf - 1; return s;
  }
  function tdProcess(s, j, k, now) {
    const key = TD_KEYS[j], nuc = NUC[key], Ex = k + 0.5, list = s.shelves[j][k];
    s.done[j][k] = true; if (!list.length) return 0;
    s.shelves[j][k] = [];
    const Smin = Math.min(...nuc.S);
    if (Ex < Smin) {                                       // below every threshold: photons carry it to the ground state
      list.forEach((b, i) => s.fly.push({ b, j0: j, k0: k, j1: j, k1: 0, kind: "gs", t0: now + i * 0.04, dur: 0.7 }));
      return list.length;
    }
    const { w, dest } = binWidths(key, 2 * k + 1);
    const gLow = dest.g.filter(([kk]) => kk * DE < k);       // photon destinations strictly on lower shelves
    let wg = 0; gLow.forEach((d) => (wg += d[1]));
    const tot = wg + w.n + w.p + w.a;
    list.forEach((b, i) => {
      let u = Math.random() * tot, x;
      if ((u -= wg) < 0) x = "g"; else if ((u -= w.n) < 0) x = "n"; else if ((u -= w.p) < 0) x = "p"; else x = "a";
      const f = { b, j0: j, k0: k, kind: x, t0: now + i * 0.05, dur: 0.75 };
      if (x === "g") { f.j1 = j; f.k1 = Math.floor(pick(gLow, Math.random()) * DE); }
      else if (x === "n" && j === 0) { f.j1 = 1; f.k1 = Math.min(s.n - 1, Math.floor(pick(dest.n, Math.random()) * DE)); }
      else { f.j1 = -1; }
      s.fly.push(f);
    });
    return list.length;
  }
  function drawTopDown(g, S, dt) {
    const { W, H, c } = g, phone = W < 600;
    const E = clamp(S.target.E, 8, 30);
    if (E !== S.tdLastE) { S.tdLastE = E; S.tdLastT = S.time; }
    if (!td || (td.E !== E && S.time - S.tdLastT > 0.4)) td = newTD(E);
    const s = td, now = S.time;
    const nS = s.n, yBot = H * 0.86, yTop = H * 0.1, shH = (yBot - yTop) / nS, Yk = (k) => yBot - k * shH;
    const hw = Math.min(W * (phone ? 0.16 : 0.13), 92), xs = [W * (phone ? 0.7 : 0.66), W * (phone ? 0.27 : 0.3)];
    // sweep logic: one shelf at a time, never while balls are still in the air
    const inAir = s.fly.some((f) => f.j1 >= 0);
    s.wait -= dt;
    if (s.wait <= 0 && !inAir) {
      if (s.phase < 2) {
        const j = s.phase; const nMoved = tdProcess(s, j, s.cur, now);
        s.wait = nMoved ? 0.55 : 0.12; s.cur--;
        if (s.cur < 0) { s.phase++; s.cur = nS - 1; s.wait = 1.0; }
      } else if (s.phase === 2) { s.phase = 3; s.wait = 3.0; }
      else td = newTD(E);
    }
    // columns
    const ctx = g.ctx, r = Math.min(shH * 0.32, 5.5);
    [0, 1].forEach((j) => {
      const xc = xs[j], key = TD_KEYS[j];
      g.line(xc - hw, yBot, xc + hw, yBot, c.ink, 3);
      for (let k = 1; k < nS; k++) g.line(xc - hw * 0.94, Yk(k), xc + hw * 0.94, Yk(k), c.line, 1, 0.9);
      for (let k = 0; k < nS; k++) if (s.done[j][k] && k > 0) { ctx.save(); ctx.globalAlpha = 0.5; ctx.fillStyle = c.paper; ctx.fillRect(xc - hw, Yk(k + 1), 2 * hw, shH); ctx.restore(); }
      const Sn = NUC[key].S[0]; if (Sn < nS) { g.line(xc - hw - 4, Yk(Sn), xc + hw + 4, Yk(Sn), c.neutron, 1.4, 0.9, [5, 4]); g.label(`n threshold`, xc + hw - 2, Yk(Sn) - 8, { color: c.neutron, size: 10, align: "right", bg: true }); }
      g.label(j === 0 ? (phone ? "residual" : "residual (first step)") : (phone ? "daughter: n fewer" : "daughter (one neutron fewer)"), xc, yBot + 16, { color: c.ink, size: phone ? 11 : 13, weight: 600 });
      // balls on shelves
      for (let k = 0; k < nS; k++) {
        const list = s.shelves[j][k]; if (!list.length) continue;
        const per = Math.max(1, Math.floor((2 * hw - 8) / (2 * r + 2))), sp = Math.min(2 * r + 2, (2 * hw - 8) / Math.max(1, Math.min(list.length, per * 2)));
        list.forEach((b, i) => {
          const col = i % per, row = Math.floor(i / per);
          const x = xc - hw + 4 + r + (row ? (col + 0.5) : col) * sp, y = Yk(k) - r - 2 - row * (r * 1.4) + Math.sin(now * 3 + b.id) * (b.cold ? 0 : 0.6);
          if (b.cold) g.dot(x, y, r, c.soft, 0.9); else g.ball(x, y, r, c.warm);
        });
      }
    });
    // flights
    for (let i = s.fly.length - 1; i >= 0; i--) {
      const f = s.fly[i], age = now - f.t0; if (age < 0) continue;
      const u = clamp(age / f.dur, 0, 1), x0 = xs[f.j0] + (f.b.id % 7 - 3) * hw * 0.2, y0 = Yk(f.k0) - r - 2;
      if (f.j1 >= 0) {
        const x1 = xs[f.j1] + (f.b.id % 5 - 2) * hw * 0.25, y1 = Yk(f.k1) - r - 2;
        const x = lerp(x0, x1, smooth(0, 1, u)), y = lerp(y0, y1, u * u) - Math.sin(u * Math.PI) * (f.j1 !== f.j0 ? 40 : 6);
        if (f.kind === "gs") g.dot(x, y, r, c.soft, 0.9); else g.ball(x, y, r, c.warm);
        if (f.kind === "g" || f.kind === "gs") { if (u < 0.8) g.photon(x0 + hw * 0.6 + u * hw * 1.4, y0 - u * 20, -0.3, 18, 1 - u); }
        if (f.kind === "n") { g.ball(x0 - u * W * 0.5, y0 - 30 - u * 60, 4, c.neutron, 1 - smooth(0.6, 1, u)); }
        if (u >= 1) { if (f.kind === "gs") f.b.cold = true; s.shelves[f.j1][f.k1].push(f.b); s.fly.splice(i, 1); }
      } else {
        const off = f.kind === "n" ? -1 : 1, col = f.kind === "n" ? c.neutron : f.kind === "p" ? c.proton : c.alpha;
        const x = x0 + off * u * W * 0.6, y = y0 - u * H * 0.4;
        g.ball(x, y, r, c.warm, 1 - u); g.ball(x + off * 10, y - 8, 4, col, 1 - u);
        if (u >= 1) { s.gone++; s.fly.splice(i, 1); }
      }
    }
    // the sweep marker
    if (s.phase < 2) {
      const xc = xs[s.phase], k = clamp(s.cur, 0, nS - 1), y = Yk(k) - shH / 2;
      const xm = s.phase === 0 ? xc + hw + 10 : xc - hw - 10, dir = s.phase === 0 ? 1 : -1;
      g.arrow(xm + dir * 22, y, xm + dir * 2, y, c.accent, 2, 1, 8);
      if (phone) g.label(`now: ${k}–${k + 1} MeV`, xc, yTop - 14, { color: c.accent, size: 11, bg: true });
      else g.label(`${k}–${k + 1} MeV`, xm + dir * 26, y, { color: c.accent, size: 11, align: dir > 0 ? "left" : "right", bg: true });
    } else g.label(s.gone ? `done: ${s.gone} left by proton or alpha, the rest sit on ground states` : "done: everything sits on a ground state", W / 2, yTop - 14, { color: c.ink, size: 12, bg: true });
    if (!phone) g.label("orange ball = reactions waiting in a bin · grey = settled on the ground state · pale bins = already emptied", W * 0.5, H - 14, { color: c.soft, size: 11, bg: true });
  }

  // ---------- scene 4: exclusive channels, one history at a time ----------
  const HIST = {
    "(n,2n)": [{ p: [[0, 0], [0, -1], [0, -2]], e: "nn" }],
    "(n,n′)": [{ p: [[0, 0], [0, -1]], e: "n" }],
    "(n,p)": [{ p: [[0, 0], [-1, 0]], e: "p" }],
    "(n,np)": [{ p: [[0, 0], [0, -1], [-1, -1]], e: "np" }, { p: [[0, 0], [-1, 0], [-1, -1]], e: "pn" }, { ghost: true }],
    "(n,α)": [{ p: [[0, 0], [-2, -2]], e: "a" }],
    "(n,3n)": [{ p: [[0, 0], [0, -1], [0, -2], [0, -3]], e: "nnn" }],
    "(n,γ)": [{ p: [[0, 0]], e: "" }],
  };
  const HOP = 0.95, PRE = 0.5, POST = 0.9, HOLD = 1.4;
  const playDur = (pl) => (pl.ghost ? 3.2 : PRE + HOP * (pl.p.length - 1) + POST + HOLD);
  function drawParticle(g, k, x, y, r, alpha = 1) {
    const { c } = g;
    if (k === "n") g.ball(x, y, r, c.neutron, alpha);
    else if (k === "p") g.ball(x, y, r, c.proton, alpha);
    else if (k === "a") { const q = r * 0.62; [[-1, -1, "p"], [1, -1, "n"], [-1, 1, "n"], [1, 1, "p"]].forEach(([dx, dy, t]) => g.ball(x + dx * q, y + dy * q, r * 0.72, t === "p" ? c.proton : c.neutron, alpha)); }
    else if (k === "d") { g.ball(x - r * 0.55, y, r * 0.8, c.proton, alpha); g.ball(x + r * 0.55, y, r * 0.8, c.neutron, alpha); }
  }
  function drawChannels(g, S) {
    const { W, H, c } = g; const G = grid(g, true), m = model(16), chan = CHANNELS[S.chan], plays = HIST[chan];
    const dest = KEYS.find((k) => NUC[k].ch === chan);
    const total = plays.reduce((a, p) => a + playDur(p), 0), t = (S.time - S.chanT) % total;
    let pi = 0, tp = t; while (pi < plays.length - 1 && tp >= playDur(plays[pi])) { tp -= playDur(plays[pi]); pi++; }
    const play = plays[pi];
    drawChartBase(g, G, (key) => (key === dest ? [c.accent, 0.16] : null));
    // tray
    const r = G.phone ? 7 : 9, slot = r * 2.8, ty = Math.min(G.bottom + G.cell * 0.62 + (G.phone ? 10 : 0), H - 54), tx = W * 0.5;
    const ctx = g.ctx; ctx.save(); ctx.strokeStyle = c.soft; ctx.lineWidth = 2; ctx.beginPath(); ctx.moveTo(tx - slot * 2.2, ty - r - 2); ctx.quadraticCurveTo(tx, ty + r * 2.6, tx + slot * 2.2, ty - r - 2); ctx.stroke(); ctx.restore();
    g.label("collected", tx - slot * 2.2 - 8, ty - 2, { color: c.faint, size: 11, align: "right" });
    const slotX = (i, n) => tx + (i - (n - 1) / 2) * slot;
    const canon = (e) => e.split("").sort((a, b) => "npa".indexOf(a) - "npa".indexOf(b));
    let caption = "";
    if (play.ghost) {
      // the (n,np) square reached in one hop by a deuteron: ghosted, with its own tray
      const a = [0, 0], b = [-1, -1], u = smooth(0.2, 1.4, tp);
      strokeHop(g, G, a, b, c.soft, 1.5, 0.6, 0.1, lerp(0.1, 0.9, u), [5, 5]);
      const [x, y] = hopPt(G, a, b, lerp(0.1, 0.9, u)); drawParticle(g, "d", x, y, 8, 0.5);
      canon("np").forEach((k, i) => drawParticle(g, k, slotX(i, 2), ty, r, 0.35));
      const gx = tx + slot * 3.6; drawParticle(g, "d", gx, ty, r * 1.1, 0.75 * smooth(1.2, 1.8, tp));
      g.label("tray: d", gx, ty + r + 12, { color: c.soft, size: 11, alpha: smooth(1.2, 1.8, tp) });
      caption = "a deuteron lands on the same square, but its tray reads d: channel (n,d)";
    } else {
      const nh = play.p.length - 1, th = tp - PRE, hop = Math.floor(th / HOP), u = th / HOP - hop;
      const em = play.e.split(""), order = canon(play.e);
      // the paths already travelled, and the token (the hot nucleus)
      for (let i = 0; i < nh; i++) { const ex = exitOf(play.p[i], play.p[i + 1]); if (i < hop) strokeHop(g, G, play.p[i], play.p[i + 1], c[ex.col], 2.5, 0.6, 0.1, 0.9); }
      if (pi === 1) { const p0 = plays[0].p; for (let i = 0; i < p0.length - 1; i++) strokeHop(g, G, p0[i], p0[i + 1], c.soft, 1.5, 0.4, 0.1, 0.9, [4, 4]); }
      let tokX, tokY, heat;
      if (th < 0) { tokX = G.X(0); tokY = G.Y(0); heat = 1; }
      else if (hop < nh) { [tokX, tokY] = hopPt(G, play.p[hop], play.p[hop + 1], smooth(0, 1, u)); heat = 1 - (hop + u) / (nh + 1); }
      else { const p = play.p[nh]; tokX = G.X(p[1]); tokY = G.Y(p[0]); heat = Math.max(0, 1 / (nh + 1) * (1 - smooth(0, POST, th - nh * HOP))); }
      g.glow(tokX, tokY, 14 + 20 * heat, c.warm, 0.25 + 0.5 * heat); g.ring(tokX, tokY, 7, c.ink, 1.5, 0.8); g.dot(tokX, tokY, 4.5, c.warm, 0.4 + 0.6 * heat);
      // emitted particles fall into the tray, each to its slot in channel order
      const used = order.map(() => false);
      em.forEach((k, i) => {
        let si = order.findIndex((o, j) => o === k && !used[j]); used[si] = true;
        const tE = th - i * HOP; if (tE < 0) return;
        const [sx, sy] = hopPt(G, play.p[i], play.p[i + 1], 0.35), q = smooth(0, HOP * 0.9, tE);
        const x = lerp(sx, slotX(si, order.length), q), y = lerp(sy, ty, q * q) - Math.sin(q * Math.PI) * 30;
        drawParticle(g, k, x, y, r);
      });
      // last photons off the final square
      const tg = th - nh * HOP; if (tg > 0 && tg < 1.2) { const p = play.p[nh]; for (let k = 0; k < 2; k++) g.photon(G.X(p[1]) + (k ? 1 : -1) * tg * 60, G.Y(p[0]) - tg * 70, k ? -0.9 : -2.2, 20, 1 - tg / 1.2); }
      const done = tg > 0.3, end = m.ends[dest];
      if (done) g.label(`${(end * 100).toFixed(end < 0.01 ? 1 : 0)} %`, G.X(play.p[nh][1]), G.Y(play.p[nh][0]) + G.sq * 0.28, { color: c.accent, size: G.phone ? 12 : 15, serif: true, weight: 600 });
      caption = done ? (em.length ? `tray: ${order.join(" ")}  →  ${chan}` : `tray empty, only photons: ${chan}, capture`) + (pi === 1 ? " · same square, same tray" : "") : em.length ? "each emitted particle falls into the tray" : "no particle gets out: only photons";
    }
    g.label(caption, W * 0.5, Math.min(ty + r + 30, H - 12), { color: c.accent, size: G.phone ? 12 : 14, weight: 600, bg: true });
    g.label(`incoming neutron: 16 MeV · channel ${S.chan + 1} of ${CHANNELS.length}`, W * 0.5, H * 0.03 + 4, { color: c.soft, size: 12 });
  }

  // ---------- scene 5: where everything ends ----------
  function fireBatch(S, E, n, prefill) {
    const m = model(E), r = rng(Math.round(E * 13) + batches.length * 7 + 5);
    batches.forEach((b) => { if (b.fade == null) b.fade = S.time; });
    const B = { E, fade: null, slots: {} }; batches.push(B);
    for (let i = 0; i < n; i++) {
      const h = samplePath(m, r, S.time + (prefill ? -10 : 0.1 + i * 0.025));
      const end = h.path[h.path.length - 1], nuc = NUC[keyOf(end)];
      h.iso = !!(nuc && nuc.iso && r() < nuc.iso); h.B = B; drops.push(h);
    }
  }
  function drawEnds(g, S) {
    const { W, H, c } = g; const G = grid(g, false), { sq } = G;
    // a new batch when the slider settles at a new energy
    const tE = S.target.E;
    if (tE !== S.lastTE) { S.lastTE = tE; S.lastTEt = S.time; }
    if (Math.abs(tE - S.lastBatchE) > 0.01 && S.time - S.lastTEt > 0.45) { fireBatch(S, tE, 200); S.lastBatchE = tE; }
    drawChartBase(g, G, null);
    const ctx = g.ctx, r = Math.max(1.8, G.cell * 0.026), per = Math.floor((sq * 0.84) / (2 * r + 0.8));
    const shelfY = (key, iso) => G.Y(+key.split(",")[0]) + (iso ? -sq * 0.02 : sq * 0.42);
    for (const key of KEYS) {
      const [dz, dn] = key.split(",").map(Number), x = G.X(dn);
      g.line(x - sq * 0.44, shelfY(key, false), x + sq * 0.44, shelfY(key, false), c.ink, 2.2, 0.8);
      if (NUC[key].iso) { g.line(x - sq * 0.44, shelfY(key, true), x + sq * 0.44, shelfY(key, true), c.fission, 2.2, 0.9); g.label("isomer", x - sq * 0.44, shelfY(key, true) - 7, { color: c.fission, size: G.phone ? 9 : 10, align: "left" }); }
    }
    // piles and drops
    for (let bi = batches.length - 1; bi >= 0; bi--) { const B = batches[bi]; B.alpha = B.fade == null ? 1 : 1 - smooth(B.fade, B.fade + 1.6, S.time); if (B.alpha <= 0) batches.splice(bi, 1); }
    for (let i = drops.length - 1; i >= 0; i--) {
      const h = drops[i], B = h.B; if (!batches.includes(B)) { drops.splice(i, 1); continue; }
      const age = S.time - h.t0; if (age < 0) continue;
      const n = h.path.length - 1, end = h.path[n], key = keyOf(end), HOPT = 0.42, tLand = n * HOPT + 0.35;
      if (h.slot == null && age >= tLand) { const sk = key + (h.iso ? "m" : "g"); h.slot = B.slots[sk] = (B.slots[sk] || 0) + 1; h.slot--; h.landT = h.t0 + tLand; }
      if (h.slot != null) {
        const row = Math.floor(h.slot / per), col = h.slot % per, base = shelfY(key, h.iso), room = h.iso ? sq * 0.3 : sq * 0.38;
        const rowH = Math.min(2 * r * 0.9, room / Math.max(1, Math.ceil(((B.slots[key + (h.iso ? "m" : "g")]) || 1) / per)));
        const off = (col + (row % 2) * 0.5) * (2 * r + 0.8), x = h.iso ? G.X(end[1]) + sq * 0.42 - r - off : G.X(end[1]) - sq * 0.42 + r + off, y = base - r - 1.5 - row * rowH;
        g.dot(x, y, r, h.iso ? c.fission : c.soft, 0.9 * B.alpha);
        const pa = S.time - h.landT; if (pa < 0.7 && B.alpha > 0.5) g.photon(x + pa * 50, y - pa * 70, -1.1, 14, 1 - pa / 0.7);
        continue;
      }
      if (age < n * HOPT) { const seg = Math.floor(age / HOPT), u = age / HOPT - seg, a = h.path[seg], b = h.path[seg + 1], ex = exitOf(a, b); const [x, y] = hopPt(G, a, b, smooth(0, 1, u)); g.dot(x, y, 3.5, c.warm, 0.9); g.dot(x + 5, y - 4, 2, c[ex ? ex.col : "neutron"], 0.9); }
      else { const u = (age - n * HOPT) / 0.35, x = G.X(end[1]) + (h.u - 0.5) * sq * 0.6, y = lerp(G.Y(end[0]), shelfY(key, h.iso) - 4, u * u); g.dot(x, y, 3.5, c.warm, 0.9); }
    }
    const cur = batches[batches.length - 1];
    g.label(`batch of 200 at ${cur ? cur.E.toFixed(1) : tE.toFixed(1)} MeV`, W * 0.5, H * 0.05, { color: c.ink, size: G.phone ? 13 : 15, weight: 600, serif: true, bg: true });
    g.label(G.phone ? "ink shelf: ground state · green: isomer" : "ink shelf: ground state · green shelf: isomer · pile height = how much of that nucleus was made", W * 0.5, H - 16, { color: c.soft, size: 12, bg: true });
  }
})();
