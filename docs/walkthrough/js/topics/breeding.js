/* Breeding new fuel. Scenes (S.mode):
 *   "chain"  = fertile to fissile: U-238 + n -> U-239 (beta-, T1/2 = 23.45 min) -> Np-239 (beta-, 2.356 d) -> Pu-239, and
 *              Th-232 + n -> Th-233 (beta-, 21.83 min) -> Pa-233 (beta-, 26.98 d) -> U-233 (half-lives: NNDC NuDat 3 /
 *              ENSDF). The share converted after a wait t is 1 - 2^(-t / T1/2) of the slow step (14 d: 98 % of Np-239;
 *              90 d: 90 % of Pa-233). The nuclei are drawn with ~46 balls (not to scale).
 *   "budget" = the neutron budget per neutron absorbed in fissile fuel: eta = nu sigma_f / sigma_a neutrons come out; one
 *              must be absorbed in fissile fuel to keep the chain going, the losses L (moderator, structure, coolant,
 *              control, fission products, leakage) are gone, and the rest is captured in fertile nuclei, so the conversion
 *              ratio CR = eta - 1 - L (bookkeeping per fissile absorption; fast fission of the fertile nuclei, which adds a
 *              little, is left out). Breeding (CR > 1) needs eta > 2 + L.
 *              eta at thermal energy (0.0253 eV; Lamarsh & Baratta, Introduction to Nuclear Engineering, 3rd ed.):
 *              U-233 2.29, U-235 2.07, Pu-239 2.11 (Maxwellian-averaged values are a little lower for Pu-239).
 *              Fast: spectrum-averaged estimates for a sodium-cooled fast-reactor spectrum (APPROXIMATE, labelled "≈"):
 *              Pu-239 ~2.4 (the "spectrum" lesson's own average is 2.37), U-233 ~2.3, U-235 ~2.0. (Near 1 MeV the values
 *              are higher, Pu-239 ~2.9, but a real fast core's neutrons are mostly far slower than that.)
 *              The losses L and the preset values are illustrative (an LWR has CR ~ 0.6, which L = 0.45 gives with U-235).
 *   "cr"     = conversion ratio as bookkeeping in a small lattice: each fission burns one fissile nucleus and, on average,
 *              CR fertile nuclei become fissile (beta glow). Illustrative counts.
 * The Shippingport light-water breeder core (thorium/U-233, 1977-1982) ended with about 1.4 % more fissile fuel than it
 * started with (Bettis LWBR proof-of-breeding results, 1987). */
(function () {
  const { TAU, clamp, lerp, smooth, rng } = WT.util;
  const r = rng(29);
  const ETA = { U5: { T: 2.07, F: 2.0 }, P9: { T: 2.11, F: 2.4 }, U3: { T: 2.29, F: 2.3 } };
  const FUEL = { U5: "U-235", P9: "Pu-239", U3: "U-233" };
  const CHAIN = {
    U: { nuc: ["U-238", "U-239", "Np-239", "Pu-239"], Z: [92, 92, 93, 94], hl: ["23.45 min", "2.356 d"], hlS: ["23 min", "2.4 d"], wait: "after 2 weeks, 98 % has become Pu-239" },
    T: { nuc: ["Th-232", "Th-233", "Pa-233", "U-233"], Z: [90, 90, 91, 92], hl: ["21.83 min", "26.98 d"], hlS: ["22 min", "27 d"], wait: "after 3 months, 90 % has become U-233" },
  };
  const CYC = 9;
  const parts = []; // budget stream: {x0,y0,x1,y1,t0,d,cx,cy}
  let lastSpawn = 0;
  const lat = { atoms: [], n: 0, burned: 0, made: 0, acc: 0, t: 0, fx: [] };

  const geo = { bar: null };
  function grabSetup(cv, S) {
    let dragBar = false;
    const setL = (x) => { const b = geo.bar; if (!b) return; const v = (x - b.x0) / (b.x1 - b.x0) * 3.2, L = clamp(+(b.eta - v).toFixed(2), 0.05, 0.8); S.set("L", L); document.querySelectorAll('#breeding [data-bind="L"]').forEach((i) => (i.value = L)); };
    WT.grab(cv, {
      down(x, y) {
        if (S.mode === "budget" && geo.bar && Math.abs(y - geo.bar.by) < 30 && x > geo.bar.x0 - 10 && x < geo.bar.x1 + 10) { dragBar = true; setL(x); return true; }
        if (S.mode === "chain") S.t0 = S.time;
        if (S.mode === "cr") lat.reset = true;
        return false;
      },
      move(x) { if (dragBar) setL(x); },
      up() { dragBar = false; }, cancel() { dragBar = false; },
      hover(x, y) { cv.style.cursor = S.mode === "budget" ? (geo.bar && Math.abs(y - geo.bar.by) < 30 ? "ew-resize" : "") : "pointer"; },
    });
  }
  function setFuel(S, f, sp) {
    if (f) S.set("fuel", f); if (sp) S.set("sp", sp);
    document.querySelectorAll('#breeding [data-act^="bf"]').forEach((b) => b.setAttribute("aria-pressed", String(b.dataset.act === "bf" + S.fuel)));
    document.querySelectorAll('#breeding [data-act^="bs"]').forEach((b) => b.setAttribute("aria-pressed", String(b.dataset.act === "bs" + S.sp)));
  }
  function setCyc(S, k) { S.set("cyc", k); S.t0 = S.time; document.querySelectorAll('#breeding [data-act^="bc"]').forEach((b) => b.setAttribute("aria-pressed", String(b.dataset.act === "bc" + k))); }
  const etaOf = (S) => ETA[S.fuel][S.sp];
  const crOf = (S) => Math.max(0, etaOf(S) - 1 - S.L);

  function resetLat(nx, ny) {
    lat.atoms.length = 0; lat.n = nx * ny; lat.burned = 0; lat.made = 0; lat.acc = 0; lat.t = 0; lat.fx.length = 0;
    const q = rng(5);
    for (let i = 0; i < nx * ny; i++) lat.atoms.push({ k: 0, t: -9, ph: q() * TAU });
    let f = 0; while (f < Math.round(nx * ny * 0.17)) { const i = Math.floor(q() * lat.n); if (lat.atoms[i].k === 0) { lat.atoms[i].k = 1; f++; } }
    lat.nx = nx; lat.ny = ny;
  }

  WT.chapter("breeding", {
    level: 1, num: "Lesson 1", title: "Breeding new fuel", short: "Breeding",
    html: `
<div class="step">
  <h3>Fertile becomes fissile</h3>
  <p>Uranium-238 hardly splits, but it can catch a neutron. Two beta decays later (a neutron inside turns into a proton each time) it has become plutonium-239, which splits easily. Thorium-232 does the same and becomes uranium-233.</p>
  <div class="btns"><button class="btn ghost" data-act="bcU" aria-pressed="true">Uranium-238</button> <button class="btn ghost" data-act="bcT" aria-pressed="false">Thorium-232</button></div>
</div>
<div class="step">
  <h3>The neutron budget</h3>
  <p>Each neutron absorbed in fissile fuel gives back <i>η</i> new neutrons. One must cause the next fission and some are lost; whatever is left can breed. With uranium-235 and slow neutrons only about 0.6 new fissile nuclei are made per one burned.</p>
  <div class="btns"><button class="btn ghost" data-act="bfU5" aria-pressed="true">U-235</button> <button class="btn ghost" data-act="bfP9" aria-pressed="false">Pu-239</button> <button class="btn ghost" data-act="bfU3" aria-pressed="false">U-233</button></div>
  <div class="btns"><button class="btn ghost" data-act="bsT" aria-pressed="true">Slow neutrons</button> <button class="btn ghost" data-act="bsF" aria-pressed="false">Fast neutrons</button></div>
</div>
<div class="step">
  <h3>Fast neutrons breed</h3>
  <p>To breed, one neutron must continue the chain and at least one must make new fuel, so <i>η</i> has to beat 2 by more than the losses. Plutonium-239 in a fast reactor gives about 2.4: enough to spare.</p>
  <div class="ctl"><label for="br-l1">Neutrons lost</label><input id="br-l1" type="range" data-bind="L" data-instant min="0.05" max="0.8" step="0.01" value="0.2"><output data-show="L" data-fmt="2"></output></div>
</div>
<div class="step">
  <h3>Thorium with slow neutrons</h3>
  <p>With slow neutrons plutonium-239 gives only about 2.1, but uranium-233 gives 2.29. That margin lets a thorium reactor breed with slow neutrons, if it wastes very few. Lower the losses until it breeds.</p>
  <div class="ctl"><label for="br-l2">Neutrons lost</label><input id="br-l2" type="range" data-bind="L" data-instant min="0.05" max="0.8" step="0.01" value="0.35"><output data-show="L" data-fmt="2"></output></div>
</div>
<div class="step">
  <h3>Conversion ratio</h3>
  <p>The conversion ratio is fissile nuclei made per fissile nucleus burned. Below 1 the fuel slowly runs down (a converter, like today's water reactors); above 1 the reactor ends with more fuel than it started with (a breeder).</p>
  <div class="btns"><button class="btn ghost" data-act="bfU5" aria-pressed="true">U-235</button> <button class="btn ghost" data-act="bfP9" aria-pressed="false">Pu-239</button> <button class="btn ghost" data-act="bfU3" aria-pressed="false">U-233</button></div>
  <div class="btns"><button class="btn ghost" data-act="bsT" aria-pressed="true">Slow neutrons</button> <button class="btn ghost" data-act="bsF" aria-pressed="false">Fast neutrons</button></div>
</div>`,
    setup(S) {
      S.set("mode", "chain"); S.set("cyc", "U"); S.set("fuel", "U5"); S.set("sp", "T"); S.set("L", 0.45); S.t0 = 0;
      ["U", "T"].forEach((k) => S.on("bc" + k, () => setCyc(S, k)));
      ["U5", "P9", "U3"].forEach((k) => S.on("bf" + k, () => { setFuel(S, k); lat.reset = true; }));
      ["T", "F"].forEach((k) => S.on("bs" + k, () => { setFuel(S, null, k); lat.reset = true; }));
    },
    steps: [
      (S) => { S.set("mode", "chain"); setCyc(S, S.cyc || "U"); },
      (S) => { S.set("mode", "budget"); setFuel(S, "U5", "T"); S.set("L", 0.45); },
      (S) => { S.set("mode", "budget"); setFuel(S, "P9", "F"); S.set("L", 0.2); },
      (S) => { S.set("mode", "budget"); setFuel(S, "U3", "T"); S.set("L", 0.35); },
      (S) => { S.set("mode", "cr"); setFuel(S, "U5", "T"); S.set("L", 0.45); lat.reset = true; },
    ],
    frame(g, S, dt) {
      const { W, H, c, ctx } = g, phone = W < 600, fs = phone ? 11 : 13, snap = document.body.classList.contains("shot");
      if (!S.grabbed) { S.grabbed = true; grabSetup(g.ctx.canvas, S); }
      if (S.mode === "chain") drawChain(g, S, phone, fs, snap);
      else if (S.mode === "budget") drawBudget(g, S, dt, phone, fs, snap);
      else drawCR(g, S, dt, phone, fs, snap);
      g.label("illustration", W - 6, H - 10, { color: c.faint, size: 10, align: "right" });
    },
  });

  // ---------- scene 1: the transmutation chain ----------
  function drawChain(g, S, phone, fs, snap) {
    const { W, H, c } = g, C = CHAIN[S.cyc];
    const xs = phone ? [0.13, 0.38, 0.63, 0.87].map((f) => W * f) : [0.14, 0.38, 0.62, 0.86].map((f) => W * f);
    const y = H * (phone ? 0.26 : 0.28), R = Math.min(phone ? W * 0.075 : W * 0.055, H * 0.085);
    let tc = snap ? 5.5 : (S.time - S.t0) % CYC; if (tc < 0) tc = 0;
    // stage of the travelling nucleus
    const mv = (a, b) => smooth(a, b, tc);
    const pos = mv(1.5, 2.4) + mv(3.6, 4.5) + mv(5.8, 6.7);
    const node = Math.floor(pos + 1e-6), z = node >= 2 ? (node >= 3 ? 2 : 1) : 0;
    // faint placeholders and arrows
    for (let i = 0; i < 4; i++) {
      const done = pos >= i - 0.02, here = Math.abs(pos - i) < 0.05;
      g.ring(xs[i], y, R * 1.12, i === 3 ? c.fission : c.soft, 1.2, done ? 0.5 : 0.25, [3, 4]);
      g.label(C.nuc[i], xs[i], y + R + (phone ? 16 : 20), { color: here ? c.ink : c.soft, size: fs + (phone ? 0 : 2), weight: here ? 700 : 500, alpha: done ? 1 : 0.55 });
      g.label(phone ? `${C.Z[i]} p` : `${C.Z[i]} protons`, xs[i], y + R + (phone ? 31 : 39), { color: c.proton, size: fs - 2, alpha: done ? 0.95 : 0.5 });
    }
    const tags = [phone ? "fertile" : "fertile: barely splits", "", "", phone ? "fissile" : "fissile: splits easily"];
    g.label(tags[0], xs[0], y - R - (phone ? 30 : 34), { color: c.soft, size: fs - 1 });
    g.label(tags[3], xs[3], y - R - (phone ? 30 : 34), { color: c.fission, size: fs - 1, weight: 600 });
    for (let i = 0; i < 3; i++) {
      const xa = xs[i] + R * 1.25, xb = xs[i + 1] - R * 1.25, act = pos > i + 0.02 && pos < i + 1.02 ? 1 : 0.45;
      g.arrow(xa, y, xb, y, i === 0 ? c.neutron : c.cool, 2, act);
      const lab = i === 0 ? "+ n" : "β⁻", sub = i === 0 ? "catch" : xb - xa > 70 ? C.hl[i - 1] : C.hlS[i - 1];
      g.label(lab, (xa + xb) / 2, y - 14, { color: i === 0 ? c.neutron : c.cool, size: fs + 1, weight: 700, alpha: act });
      g.label(sub, (xa + xb) / 2, y + 14, { color: c.soft, size: fs - 2, alpha: act });
    }
    // incoming neutron
    if (tc < 1.5) { const f = smooth(0, 1.4, tc), nx = lerp(-10, xs[0] - R * 0.6, f); g.glow(nx, y, 16, c.neutron, 0.5); g.ball(nx, y, phone ? 5 : 6, c.neutron); }
    if (tc > 1.35 && tc < 2.1) g.glow(xs[0], y, R * 2.2, c.neutron, 0.5 * (1 - (tc - 1.35) / 0.75));
    // beta decays: electron + antineutrino fly out, the nucleus flashes
    [[3.0, 1], [5.2, 2]].forEach(([tb, i]) => {
      const a = tc - tb; if (a < 0 || a > 1.6) return;
      const x0 = xs[i], f = a / 1.6, ang = -1.15, ang2 = -2.3;
      // the moment: a white-hot flash, a shock ring, and the nucleus glows proton-red (one neutron became a proton)
      if (a < 0.25) g.glow(x0, y, R * (1.2 + 6 * a), "#ffffff", 0.9 * (1 - a / 0.25));
      g.ring(x0, y, R * (1.1 + 2.6 * f), c.cool, 2.2 * (1 - f) + 0.3, 0.85 * (1 - f));
      g.glow(x0, y, R * 2.2, c.proton, 0.6 * (1 - f));
      // the electron: a fast blue streak with a fading trail
      const dE = Math.min(1, a / 0.55) * Math.min(W, H) * 0.32, ex = x0 + Math.cos(ang) * (R + dE), ey = y + Math.sin(ang) * (R + dE);
      for (let k = 0; k < 10; k++) { const q = k / 10, d = R + dE * (1 - q * 0.6); g.dot(x0 + Math.cos(ang) * d, y + Math.sin(ang) * d, (phone ? 2.6 : 3.2) * (1 - q), c.cool, (1 - q) * (1 - f)); }
      g.glow(ex, ey, 18, c.cool, 0.75 * (1 - f)); g.ball(ex, ey, phone ? 3.5 : 4.5, c.cool, 1 - f);
      if (f < 0.6) g.label(phone ? "e⁻" : "electron", ex + 10, ey, { color: c.cool, size: fs - 2, align: "left", alpha: 1 - f / 0.6 });
      // the antineutrino: a pale flash that leaves at once and never interacts
      const dn = Math.min(1, a / 0.35) * Math.min(W, H) * 0.4, nx = x0 + Math.cos(ang2) * (R + dn), ny = y + Math.sin(ang2) * (R + dn);
      g.glow(nx, ny, 12, c.photon, 0.7 * (1 - f)); g.ring(nx, ny, 4 + 10 * f, c.photon, 1.2, 0.8 * (1 - f));
      if (f < 0.6 && !phone) g.label("antineutrino", nx - 10, ny, { color: c.photon, size: fs - 2, align: "right", alpha: 1 - f / 0.6 });
    });
    // the travelling nucleus
    const i0 = Math.min(3, Math.floor(pos)), fr = pos - i0, x = i0 < 3 ? lerp(xs[i0], xs[i0 + 1], fr) : xs[3];
    const fiss = smooth(6.6, 7.2, tc);
    if (fiss > 0) g.glow(x, y, R * (2.2 + 0.25 * Math.sin(S.time * 3)), c.fission, 0.45 * fiss);
    g.nucleus(x, y, R, { N: 46, Z: 18 + z, seed: 11, t: S.time, jiggle: 0.5, halo: [c.neutron, c.alpha, c.fission][z], haloAlpha: 0.22 });
    // the wait: a batch of 40 nuclei at the slow step, each decaying at a random moment (exponential, the real half-life)
    const hl = S.cyc === "U" ? 2.356 : 26.98, span = S.cyc === "U" ? 14 : 90, n = 40, cols = phone ? 20 : 20, rows = n / cols;
    const ct = snap ? 0.5 : ((S.time - S.t0) % 9) / 7, day = clamp(ct, 0, 1) * span;
    const bw = Math.min(W * 0.84, cols * (phone ? 17 : 24)), bx = W / 2 - bw / 2, by = H * (phone ? 0.62 : 0.52), sp = bw / cols, br = Math.min(sp * 0.34, 7);
    const q = rng(S.cyc === "U" ? 21 : 23), mean = hl / Math.LN2; let left = 0;
    for (let i = 0; i < n; i++) {
      const td = -Math.log(1 - q() * 0.99999) * mean, done = day >= td, x = bx + sp * (i % cols + 0.5), yy = by + sp * Math.floor(i / cols);
      if (done && day - td < span * 0.04) g.glow(x, yy, br * 3.5, c.cool, 0.6);
      if (done) { g.glow(x, yy, br * 2.2, c.fission, 0.25); g.ball(x, yy, br, c.fission); } else { g.ball(x, yy, br, c.neutron, 0.85); left++; }
    }
    const nm = C.nuc[2], fin = C.nuc[3];
    g.label(WT.trf(phone ? "{a} waiting: day {b}" : "a batch of {a} waiting · day {b}", nm, day.toFixed(0)), bx, by - sp * 0.5 - 14, { color: c.soft, size: fs - 1, align: "left", raw: true });
    g.label(WT.trf("{a} % now {b}", (100 * (1 - Math.pow(2, -day / hl))).toFixed(0), fin), bx + bw, by - sp * 0.5 - 14, { color: c.fission, size: fs - 1, weight: 600, align: "right", raw: true });
    const rd = { color: c.ink, size: fs + 1, weight: 600, serif: true };
    const ly = by + sp * (rows - 0.5) + (phone ? 22 : 30);
    g.label(C.wait, W * 0.5, ly, rd);
    g.label(S.cyc === "U" ? (phone ? "slow step: Np-239, half-life 2.356 d" : "the slow step is Np-239 (half-life 2.356 days)") : (phone ? "slow step: Pa-233, half-life 26.98 d" : "the slow step is Pa-233 (half-life 26.98 days)"), W * 0.5, ly + fs + 10, { color: c.soft, size: fs - 1 });
  }

  // ---------- scenes 2-4: the neutron budget ----------
  function drawBudget(g, S, dt, phone, fs, snap) {
    const { W, H, c } = g, eta = etaOf(S), L = S.L, cr = crOf(S), fert = S.fuel === "U3" ? "Th-232" : "U-238", made = S.fuel === "U3" ? "U-233" : "Pu-239";
    const sx = W * (phone ? 0.17 : 0.2), sy = H * (phone ? 0.28 : 0.3), R = Math.min(W * 0.085, H * 0.1);
    const dx = W * (phone ? 0.6 : 0.64), dys = [H * 0.1, H * 0.28, H * 0.46].map((v) => v + (phone ? 0.02 * H : 0));
    const dcol = [c.fission, c.warm, c.faint], probs = [1 / eta, Math.max(0, eta - 1 - L) / eta, Math.min(L, eta - 1) / eta];
    // stream of neutrons, on average the budget's proportions
    const rate = 16, now = S.time;
    if (snap && !parts.length) for (let i = 0; i < 26; i++) spawnN(now - i / rate, sx, sy, dx, dys, probs);
    while (!snap && lastSpawn < now) { lastSpawn = Math.max(lastSpawn + 1 / rate, now - 0.5); spawnN(lastSpawn, sx, sy, dx, dys, probs); }
    // incoming neutron + source nucleus
    const pin = (now * 1.2) % 1;
    g.glow(sx, sy, R * 2.4, c.fission, 0.25 + 0.15 * Math.sin(now * 6));
    g.nucleus(sx, sy, R, { N: 40, Z: 16, seed: 3, t: now, jiggle: 0.7 });
    { const nx = lerp(4, sx - R, pin); g.ball(nx, sy, 4, c.neutron, 0.9 * (1 - pin * 0.3)); }
    g.label(FUEL[S.fuel], sx, sy + R + 16, { color: c.ink, size: fs + 1, weight: 700 });
    g.label(S.sp === "T" ? "slow neutrons" : "fast neutrons", sx, sy + R + 32, { color: c.soft, size: fs - 1 });
    // destinations
    const names = phone ? ["next fission", `${fert} → ${made}`, "lost"] : ["next fission: keeps the chain going", `breeds: ${fert} → ${made}`, "lost: water, steel, poisons, leakage"];
    const vals = [1, Math.max(0, eta - 1 - L), Math.min(L, eta - 1)];
    for (let i = 0; i < 3; i++) {
      const y = dys[i];
      if (i < 2) { g.glow(dx, y, 24, dcol[i], 0.3); g.ball(dx, y, phone ? 9 : 11, i === 0 ? c.fission : c.soft); }
      else g.ring(dx, y, phone ? 9 : 11, c.faint, 1.4, 0.8, [3, 3]);
      g.label(names[i], dx + (phone ? 16 : 22), y - (phone ? 7 : 8), { color: i === 2 ? c.soft : dcol[i], size: fs, weight: 600, align: "left" });
      g.label(WT.trf("{a} per absorption", vals[i].toFixed(2)), dx + (phone ? 16 : 22), y + (phone ? 8 : 10), { color: c.soft, size: fs - 2, align: "left", raw: true });
    }
    // particles
    for (let i = parts.length - 1; i >= 0; i--) {
      const p = parts[i], a = (now - p.t0) / 1.3; if (a > 1) { if (p.d < 2) g.glow(p.x1, p.y1, 22, dcol[p.d], 0.5); parts.splice(i, 1); continue; } if (a < 0) continue;
      const u = 1 - a, x = u * u * p.x0 + 2 * u * a * p.cx + a * a * p.x1, y = u * u * p.y0 + 2 * u * a * p.cy + a * a * p.y1;
      g.ball(x, y, phone ? 3 : 3.6, c.neutron, p.d === 2 ? 0.9 * (1 - a * 0.7) : 0.92);
    }
    while (parts.length > 120) parts.shift();
    // the budget bar: 0..3.2 neutrons
    const x0 = W * 0.08, x1 = W * 0.92, by = H * (phone ? 0.66 : 0.68), bh = phone ? 16 : 20, X = (v) => lerp(x0, x1, v / 3.2);
    g.ctx.save(); g.ctx.fillStyle = g.rgba(c.soft, 0.08); g.ctx.fillRect(x0, by - bh / 2, x1 - x0, bh); g.ctx.restore();
    const segs = [[0, 1, c.fission, "chain"], [1, 1 + vals[1], c.warm, "breed"], [1 + vals[1], eta, c.faint, "lost"]];
    segs.forEach(([a, b, col, nm]) => {
      if (b - a < 0.005) return; const xa = X(a) + 1, xb = X(b) - 1;
      g.ctx.save(); const gr = g.ctx.createLinearGradient(0, by - bh / 2, 0, by + bh / 2); gr.addColorStop(0, g.rgba(col, 0.95)); gr.addColorStop(1, g.rgba(col, 0.6));
      g.ctx.fillStyle = gr; g.ctx.beginPath(); if (g.ctx.roundRect) g.ctx.roundRect(xa, by - bh / 2, Math.max(1, xb - xa), bh, 5); else g.ctx.rect(xa, by - bh / 2, xb - xa, bh); g.ctx.fill(); g.ctx.restore();
      if (xb - xa > (phone ? 30 : 40)) g.label(nm, (xa + xb) / 2, by - bh / 2 - 10, { color: col === c.faint ? c.soft : col, size: fs - 1, weight: 600 });
    });
    geo.bar = { x0, x1, by, bh, eta };
    { const hx = X(1 + vals[1]), pulse = 0.5 + 0.5 * Math.sin(S.time * 3); g.glow(hx, by, 18 + 4 * pulse, c.warm, 0.35 + 0.2 * pulse); g.ring(hx, by, bh * 0.75, c.ink, 1.6, 0.7); }
    g.glow(X(eta), by, 26, c.neutron, 0.35);
    g.label(WT.trf(S.sp === "F" ? "η ≈ {a}" : "η = {a}", eta.toFixed(2)), X(eta), by + bh / 2 + 14, { color: c.neutron, size: fs, weight: 700, raw: true });
    // the breeding line at 2
    g.line(X(2), by - bh - 18, X(2), by + bh + 4, c.ink, 1.3, 0.75, [4, 4]);
    g.label(phone ? "2" : "2: breeding line", X(2), by - bh - 26, { color: c.ink, size: fs - 1 });
    [0, 1, 3].filter((v) => Math.abs(v - eta) > 0.35).forEach((v) => g.label(String(v), X(v), by + bh / 2 + 14, { color: c.faint, size: fs - 2 }));
    g.label(phone ? "neutrons per absorption" : "neutrons out per neutron absorbed in the fuel", x0, by + bh / 2 + 32, { color: c.soft, size: fs - 1, align: "left" });
    // verdict
    const breeds = cr >= 1;
    const rd = { color: breeds ? c.fission : c.ink, size: fs + 2, weight: 600, serif: true };
        g.label(WT.trf(breeds ? (phone ? "conversion ratio ≈ η − 1 − lost = {a}: breeds" : "conversion ratio ≈ η − 1 − lost = {a}: breeds, makes more fuel than it burns") : (phone ? "conversion ratio ≈ η − 1 − lost = {a}: converts" : "conversion ratio ≈ η − 1 − lost = {a}: converts, makes less fuel than it burns"), cr.toFixed(2)), W * 0.5, H * 0.9, Object.assign({ raw: true }, rd));
    if (breeds) g.glow(W * 0.5, H * 0.9, 100, c.fission, 0.15);
  }
  function spawnN(t0, sx, sy, dx, dys, probs) {
    const u = r(); const d = u < probs[0] ? 0 : u < probs[0] + probs[1] ? 1 : 2;
    let x1 = dx, y1 = dys[d]; if (d === 2) { x1 = dx + (r() - 0.3) * 60; y1 = dys[2] + 40 + r() * 30; }
    parts.push({ t0, d, x0: sx, y0: sy, x1, y1, cx: lerp(sx, x1, 0.5) + (r() - 0.5) * 40, cy: lerp(sy, y1, 0.5) + (r() - 0.5) * 80 });
  }

  // ---------- scene 5: conversion ratio as bookkeeping ----------
  function drawCR(g, S, dt, phone, fs, snap) {
    const { W, H, c } = g, nx = phone ? 9 : 12, ny = phone ? 7 : 8, cr = crOf(S), fert = S.fuel === "U3" ? "Th-232" : "U-238", made = S.fuel === "U3" ? "U-233" : "Pu-239";
    if (lat.reset || lat.nx !== nx || lat.ny !== ny) { lat.reset = false; resetLat(nx, ny); }
    const ax = W * 0.08, aw = W * 0.84, ay = H * (phone ? 0.1 : 0.06), ah = H * (phone ? 0.46 : 0.56), sp = Math.min(aw / nx, ah / ny), R = sp * 0.26;
    const ox = ax + (aw - sp * nx) / 2 + sp / 2, oy = ay + (ah - sp * ny) / 2 + sp / 2;
    const P = (i) => [ox + (i % nx) * sp, oy + Math.floor(i / nx) * sp];
    const step = () => {
      const fis = []; lat.atoms.forEach((a, i) => a.k === 1 && fis.push(i));
      const fer = []; lat.atoms.forEach((a, i) => a.k === 0 && fer.push(i));
      if (!fis.length || lat.burned >= 80 || fer.length < 2) { resetLat(nx, ny); return; }
      const i = fis[Math.floor(r() * fis.length)]; lat.atoms[i].k = 2; lat.atoms[i].t = S.time; lat.burned++;
      lat.acc += cr;
      while (lat.acc >= 1 && fer.length) { lat.acc -= 1; const j = fer.splice(Math.floor(r() * fer.length), 1)[0]; lat.atoms[j].k = 1; lat.atoms[j].t = S.time; lat.atoms[j].born = true; lat.made++; }
    };
    if (snap && lat.burned === 0) { for (let i = 0; i < 9; i++) step(); }
    lat.t += dt; if (!snap && lat.t > 0.45) { lat.t = 0; step(); }
    let nf = 0;
    lat.atoms.forEach((a, i) => {
      const [x, y] = P(i), age = S.time - a.t;
      if (a.k === 0) g.ball(x, y, R, c.soft, 0.75);
      else if (a.k === 1) { if (a.born && age < 1.2) g.glow(x, y, R * 4 * (1 - age / 1.2) + R, c.cool, 0.6 * (1 - age / 1.2)); g.glow(x, y, R * 2.6, c.fission, 0.3 + 0.08 * Math.sin(S.time * 3 + a.ph)); g.ball(x, y, R * 1.08, c.fission); nf++; }
      else { if (age < 0.7) g.glow(x, y, R * (2 + 6 * age), c.fission, 0.7 * (1 - age / 0.7)); g.dot(x - R * 0.35, y, R * 0.42, c.faint, 0.8); g.dot(x + R * 0.4, y + R * 0.1, R * 0.36, c.faint, 0.8); }
    });
    // legend
    const ly = ay + ah + (phone ? 16 : 20), lx = W * 0.5, gap = phone ? W * 0.31 : W * 0.24;
    [[c.soft, phone ? fert : `${fert} (fertile)`], [c.fission, "fissile"], [c.faint, phone ? "split" : "split (fission products)"]].forEach(([col, s], i) => {
      const x = lx + (i - 1) * gap; g.ball(x - (phone ? 30 : 46), ly, phone ? 4 : 5, col); g.label(s, x - (phone ? 22 : 36), ly, { color: c.soft, size: fs - 1, align: "left" });
    });
    // tallies
    const ty = H * (phone ? 0.72 : 0.75);
    g.label(WT.trf("burned {a}", lat.burned), W * 0.3, ty, { color: c.fission, size: fs + 2, weight: 700, raw: true });
    g.label(WT.trf("made {a}", lat.made), W * 0.7, ty, { color: c.cool, size: fs + 2, weight: 700, raw: true });
    g.label(WT.trf(S.sp === "T" ? "{a} · slow neutrons" : "{a} · fast neutrons", FUEL[S.fuel]), W * 0.5, phone ? ty + 22 : ty, { color: c.soft, size: fs - 1, raw: true });
    const breeds = cr >= 1;
    g.label(WT.trf(breeds ? "conversion ratio {a}: a breeder" : "conversion ratio {a}: a converter", cr.toFixed(2)), W * 0.5, H * 0.88, { color: breeds ? c.fission : c.ink, size: fs + 2, weight: 600, serif: true, raw: true });
    if (breeds) g.glow(W * 0.5, H * 0.88, 100, c.fission, 0.15);
  }
})();
