/* Chapter 32 (part three, Expert): the blanket. Scenes:
 *   "breed" / "lead" = Monte Carlo transport of 14.1 MeV D-T neutrons through a slab: steel first wall (2 cm), breeder
 *            (Pb-17Li eutectic or liquid lithium, depth D), then the shield (anything that gets there counts as leaked).
 *            Neutrons that leave toward the plasma cross it and come back (reflecting boundary). Collisions sample, per
 *            nuclide, elastic scattering (isotropic in the centre of mass, exact two-body kinematics), inelastic
 *            scattering with an evaporation spectrum, (n,2n) on Pb (threshold 7.4 MeV) and Fe, radiative capture (1/v),
 *            6Li(n,t)alpha (1/v, 940 b at 0.0253 eV, plus the 240 keV resonance) and 7Li(n,n't)alpha (threshold 2.8 MeV).
 *            The cross sections are simple fits to the evaluated shapes, so the numbers are illustrative; the trends
 *            (enrichment, depth, lead multiplication, 7Li at high energy) are the real ones. Number densities:
 *            Pb-17Li 9.5 g/cm3 (Pb 0.0274, Li 0.0056 per b cm), liquid Li 0.0443, steel (Fe) 0.0849.
 *            Tritium sites stay on a long-exposure layer (off-screen canvas, slow fade).
 *   "wall" = 14.1 MeV neutrons in a first-wall lattice. Helium (n,alpha), hydrogen (n,p) and (n,2n) happen at the rates
 *            of INCOGNITA's own cross sections at 14.1 MeV, read live from the v0.2 library files of the Every nuclide
 *            page (data/n/<Z>/<A>.json, 64-point grid 1 keV - 20 MeV, log-spaced, mb). appm per year =
 *            sigma * phi * t * 1e6, phi = 4.43e13 n/cm2/s per MW/m2 of 14.1 MeV wall load (uncollided neutrons only). */
(function () {
  const { TAU, clamp, lerp, smooth, rng } = WT.util;
  const ETH = 2.53e-8; // MeV
  const v1 = (E, s0) => s0 * Math.sqrt(ETH / Math.max(E, ETH));
  const thr = (E, t, s, w) => (E > t ? s * (1 - Math.exp(-(E - t) / w)) : 0);
  // microscopic cross sections (barns), E in MeV
  const XS = {
    Fe: (E) => ({ el: 3.0 + 8 / (1 + E / 1e-4), inl: thr(E, 0.85, 1.4, 1.0), n2n: thr(E, 11.2, 0.45, 1.5), cap: v1(E, 2.56) }),
    Pb: (E) => ({ el: 3 + 2.5 * Math.exp(-E / 5) + 5.5 / (1 + E / 0.1), inl: thr(E, 0.57, 2.2, 0.8) * (E > 7 ? Math.exp(-(E - 7) / 4) : 1), n2n: thr(E, 7.4, 2.15, 1.6), cap: v1(E, 0.171) }),
    Li6: (E) => ({ el: 0.75 + 7 / (1 + ((E - 0.24) / 0.06) ** 2), nt: v1(E, 940) + 2.9 / (1 + ((E - 0.24) / 0.06) ** 2) }),
    Li7: (E) => ({ el: 1.2, nnt: thr(E, 2.82, 0.38, 1.8), cap: v1(E, 0.045) }),
  };
  const MASS = { Fe: 55.85, Pb: 207.2, Li6: 6.015, Li7: 7.016 };
  function mats(S) {
    const enr = S.enr / 100, li = S.mat === "Li" ? 0.0443 : 0.0056;
    const br = S.mat === "Li" ? [["Li6", li * enr], ["Li7", li * (1 - enr)]] : [["Pb", 0.0274], ["Li6", li * enr], ["Li7", li * (1 - enr)]];
    return { wall: [["Fe", 0.0849]], br };
  }
  const WALL = 2;
  const evap = (r, U, A) => { const T = Math.max(0.05, Math.sqrt(Math.max(U, 0.01) / (A / 10))); return Math.min(U, -T * Math.log(Math.max(1e-12, r() * r()))); };
  const isoDir = (r) => { const mu = 2 * r() - 1, ph = TAU * r(), s = Math.sqrt(1 - mu * mu); return [mu, s * Math.cos(ph), s * Math.sin(ph)]; };
  function rotate(d, mu, r) { // new direction at angle acos(mu) from d, random azimuth
    const ph = TAU * r(), s = Math.sqrt(Math.max(0, 1 - mu * mu)), [u, v, w] = d;
    if (Math.abs(w) > 0.9999) return [s * Math.cos(ph), s * Math.sin(ph), mu * Math.sign(w)];
    const t = Math.sqrt(1 - w * w);
    return [mu * u + (s * (u * w * Math.cos(ph) - v * Math.sin(ph))) / t, mu * v + (s * (v * w * Math.cos(ph) + u * Math.sin(ph))) / t, mu * w - s * Math.cos(ph) * t];
  }
  /** One source neutron's history (with all its (n,2n) daughters). rec: optional array of track segments for drawing. */
  function history(S, M, r, tally, rec) {
    const stack = [{ x: 0.001, y: 0, d: isoDir(r).map((v, i) => (i === 0 ? Math.abs(v) : v)), E: 14.1, id: 0 }];
    let guard = 0;
    while (stack.length && guard++ < 50) {
      const n = stack.pop(); const path = rec ? [[n.x, n.y, n.E, null]] : null; let steps = 0;
      for (;;) {
        if (steps++ > 3000) break;
        const inWall = n.x < WALL, mix = inWall ? M.wall : M.br;
        const xs = mix.map(([k, N]) => { const s = XS[k](n.E); let t = 0; for (const q in s) t += s[q]; return [k, N, s, N * t]; });
        const Sig = xs.reduce((a, b) => a + b[3], 0);
        let L = -Math.log(Math.max(1e-12, r())) / Sig;
        // boundaries: wall/breeder interface (re-sample there), plasma side (reflect), back (leak)
        const bx = n.d[0] > 0 ? (inWall ? WALL : WALL + S.depth) : inWall ? 0 : WALL;
        const toB = (bx - n.x) / n.d[0];
        if (toB >= 0 && toB < L) {
          n.x = bx; n.y += n.d[1] * toB;
          if (bx >= WALL + S.depth - 1e-9 && n.d[0] > 0) { tally.leak++; path && path.push([n.x, n.y, n.E, "leak"]); break; }
          if (bx <= 0 && n.d[0] < 0) { n.d = [-n.d[0], n.d[1], n.d[2]]; tally.cross++; path && path.push([n.x, n.y, n.E, "cross"]); }
          n.x += n.d[0] * 1e-6; continue;
        }
        n.x += n.d[0] * L; n.y += n.d[1] * L;
        // which nuclide, which reaction
        let u = r() * Sig, pick = xs[0]; for (const e of xs) { if (u < e[3]) { pick = e; break; } u -= e[3]; }
        const [k, N, s] = pick; let tot = 0; for (const q in s) tot += s[q]; let v = r() * tot, rx = "el"; for (const q in s) { if (v < s[q]) { rx = q; break; } v -= s[q]; }
        const A = MASS[k];
        if (rx === "el") {
          const mc = 2 * r() - 1, E2 = (n.E * (A * A + 2 * A * mc + 1)) / ((A + 1) * (A + 1)), mul = (1 + A * mc) / Math.sqrt(A * A + 2 * A * mc + 1);
          n.E = Math.max(ETH, E2); n.d = rotate(n.d, mul, r);
        } else if (rx === "inl") { n.E = Math.max(ETH, evap(r, n.E - (k === "Pb" ? 0.57 : 0.85), A)); n.d = isoDir(r); }
        else if (rx === "n2n") { const U = n.E - (k === "Pb" ? 7.4 : 11.2), e1 = evap(r, U, A), e2 = evap(r, Math.max(0.01, U - e1), A); tally.n2n++; path && path.push([n.x, n.y, n.E, "n2n"]);
          stack.push({ x: n.x, y: n.y, d: isoDir(r), E: Math.max(ETH, e2), id: 1 }); n.E = Math.max(ETH, e1); n.d = isoDir(r); continue; }
        else if (rx === "nnt") { tally.t7++; tally.sites.push([n.x, n.y, 7]); path && path.push([n.x, n.y, n.E, "t7"]); n.E = Math.max(ETH, r() * (n.E - 2.47) * 0.6); n.d = isoDir(r); continue; }
        else if (rx === "nt") { tally.t6++; tally.sites.push([n.x, n.y, 6]); path && path.push([n.x, n.y, n.E, "t6"]); break; }
        else { tally[inWall ? "capFe" : "capPb"]++; path && path.push([n.x, n.y, n.E, "cap"]); break; }
        path && path.push([n.x, n.y, n.E, null]);
      }
      if (rec && path) rec.push(path);
    }
    tally.N++;
  }

  // ---------- 14 MeV data from the library ----------
  const GRID = (i) => 1000 * Math.pow(20000, i / 63); // eV, the library's 64-point grid
  const MATS = { Fe: [26, 56, "Steel (iron-56)"], W: [74, 184, "Tungsten-184"], V: [23, 51, "Vanadium-51"], Cu: [29, 63, "Copper-63"], Si: [14, 28, "Silicon-28 (SiC)"] };
  const lib = {};
  function libAt(v, E) { for (let i = 0; i < 63; i++) { const a = GRID(i), b = GRID(i + 1); if (E >= a && E <= b) { const t = Math.log(E / a) / Math.log(b / a); return v[i] + (v[i + 1] - v[i]) * t; } } return NaN; }
  function load(key) {
    if (lib[key]) return lib[key]; const [Z, A] = MATS[key]; lib[key] = { state: "loading" };
    fetch(`data/n/${Z}/${A}.json`).then((r) => r.json()).then((d) => { const ch = d.ch || {}; lib[key] = { state: "ok", na: libAt(ch.na, 14.1e6), np: libAt(ch.np, 14.1e6), n2n: libAt(ch.n2n, 14.1e6) }; })
      .catch(() => (lib[key] = { state: "fail" }));
    return lib[key];
  }

  const T = { N: 0, t6: 0, t7: 0, leak: 0, cross: 0, n2n: 0, capFe: 0, capPb: 0, sites: [] };
  const resetT = () => { for (const k in T) T[k] = k === "sites" ? [] : 0; };
  let expo = null, prof = [], key0 = "", vis = [];
  const R = rng(2207);

  WT.chapter("blanket", {
    num: "Chapter 32", title: "Breeding blanket and first wall", short: "Blanket",
    lead: "Tritium barely exists in nature. A D–T plant must breed its own from lithium, using the neutrons its plasma makes.",
    html: `
<div class="step">
  <h3>Tritium breeding ratio</h3>
  <p>Each neutron wanders until lithium catches it and makes a triton. Every glowing dot is one triton.</p>
  <div class="ctl"><label for="bk-e">Lithium-6 share (%)</label><input id="bk-e" type="range" data-bind="enr" min="7.5" max="90" step="0.5" value="90" data-instant><output data-show="enr" data-fmt="1"></output></div>
  <div class="ctl"><label for="bk-d">Breeder depth (cm)</label><input id="bk-d" type="range" data-bind="depth" min="10" max="100" step="1" value="60" data-instant><output data-show="depth" data-fmt="0"></output></div>
  <div class="formula">TBR = (⁶Li(n,t) + ⁷Li(n,n′t)) / n<sub>fusion</sub> &gt; 1</div>
</div>
<div class="step">
  <h3>Neutron multiplication by (n,2n)</h3>
  <p>A 14 MeV neutron that hits lead can knock out a second neutron: (n,2n). Compare with lithium alone.</p>
  <div class="btns bk-m"><button class="btn ghost" data-act="pbli" aria-pressed="true">Lead–lithium</button> <button class="btn ghost" data-act="li" aria-pressed="false">Lithium only</button></div>
  <div class="ctl"><label for="bk-e2">Lithium-6 share (%)</label><input id="bk-e2" type="range" data-bind="enr" min="7.5" max="90" step="0.5" value="90" data-instant><output data-show="enr" data-fmt="1"></output></div>
</div>
<div class="step">
  <h3>Helium and hydrogen in the first wall</h3>
  <p>The first wall takes the full 14 MeV beam. Helium and hydrogen build up inside it, at the rates INCOGNITA computes.</p>
  <div class="btns bk-w"><button class="btn ghost" data-act="wFe" aria-pressed="true">Steel</button> <button class="btn ghost" data-act="wW" aria-pressed="false">Tungsten</button> <button class="btn ghost" data-act="wV" aria-pressed="false">Vanadium</button> <button class="btn ghost" data-act="wCu" aria-pressed="false">Copper</button> <button class="btn ghost" data-act="wSi" aria-pressed="false">SiC</button></div>
  <div class="ctl"><label for="bk-l">Wall load (MW/m²)</label><input id="bk-l" type="range" data-bind="load" min="0.5" max="3" step="0.1" value="1" data-instant><output data-show="load" data-fmt="1"></output></div>
  <div class="ctl"><label for="bk-y">Years</label><input id="bk-y" type="range" data-bind="yrs" min="0" max="10" step="0.1" value="2" data-instant><output data-show="yrs" data-fmt="1"></output></div>
  <div class="formula">appm = σ(14.1 MeV) · φ · t · 10⁶</div>
  <div class="aside">Cross sections: INCOGNITA's library v0.2 (<code>library/v0.2/channels_v02.parquet</code>), the same curves as <a href="data.html#Fe-56" data-keep-lang>Every nuclide</a>.</div>
</div>`,
    setup(S) {
      S.set("mode", "breed"); S.set("enr", 90); S.set("depth", 60); S.set("load", 1); S.set("yrs", 2); S.mat = "PbLi"; S.wmat = "Fe";
      const press = (sel, act) => document.querySelectorAll(sel + " .btn").forEach((b) => b.setAttribute("aria-pressed", String(b.dataset.act === act)));
      S.on("pbli", () => { S.mat = "PbLi"; press(".bk-m", "pbli"); }); S.on("li", () => { S.mat = "Li"; press(".bk-m", "li"); });
      Object.keys(MATS).forEach((k) => S.on("w" + k, () => { S.wmat = k; press(".bk-w", "w" + k); S.wallT0 = S.time; }));
    },
    steps: [
      (S) => { S.set("mode", "breed"); },
      (S) => { S.set("mode", "lead"); },
      (S) => { S.set("mode", "wall"); S.wallT0 = S.time; load(S.wmat); },
    ],
    frame(g, S, dt) { if (S.mode === "wall") drawWall(g, S, dt); else drawBreed(g, S, dt); },
  });

  function drawBreed(g, S, dt) {
    const { W, H, c } = g, phone = W < 600, ctx = g.ctx, M = mats(S);
    const key = `${S.mat}|${S.enr}|${S.depth}`;
    if (key !== key0) { key0 = key; resetT(); prof = new Array(Math.ceil(S.depth)).fill(0); vis = []; if (expo) expo.getContext("2d").clearRect(0, 0, expo.width, expo.height); }
    // geometry on screen: depth x to the right, the slab periodic in y
    const x0 = phone ? 34 : W * 0.1, x1 = W - (phone ? 10 : W * 0.04), top = phone ? 76 : H * 0.12, bot = H * (phone ? 0.66 : 0.7);
    const span = WALL + S.depth + 6, px = (x1 - x0) / span, X = (x) => x0 + x * px, hcm = (bot - top) / px, Y = (y) => top + ((((y / hcm) % 1) + 1) % 1) * (bot - top);
    // layers
    { const gr = ctx.createLinearGradient(x0 - 40, 0, x0, 0); gr.addColorStop(0, g.rgba(c.alpha, 0)); gr.addColorStop(1, g.rgba(c.alpha, 0.35)); ctx.fillStyle = gr; ctx.fillRect(x0 - 40, top, 40, bot - top); }
    ctx.fillStyle = g.rgba(c.soft, 0.35); ctx.fillRect(X(0), top, WALL * px, bot - top);
    ctx.fillStyle = g.rgba(S.mat === "Li" ? c.fission : c.cool, 0.1); ctx.fillRect(X(WALL), top, S.depth * px, bot - top);
    ctx.fillStyle = g.rgba(c.soft, 0.18); ctx.fillRect(X(WALL + S.depth), top, 6 * px, bot - top);
    g.label("plasma", x0 - 6, top - 12, { color: c.alpha, size: 11, weight: 600, align: "right" });
    if (!phone) g.label("wall", X(WALL / 2), top - 12, { color: c.soft, size: 11 });
    g.label(S.mat === "Li" ? "liquid lithium" : "lead–lithium", X(WALL + S.depth / 2), top - 12, { color: c.ink, size: 12, weight: 600 });
    g.label("shield", X(WALL + S.depth + 3), top - 12, { color: c.soft, size: 11 });
    // background histories for the counters (not drawn), then the long-exposure layer
    if (dt > 0) for (let i = 0; i < (phone ? 25 : 45); i++) history(S, M, R, T, null);
    const ew = Math.max(2, Math.round(W)), eh = Math.max(2, Math.round(H));
    if (!expo || expo.width !== ew || expo.height !== eh) { expo = document.createElement("canvas"); expo.width = ew; expo.height = eh; }
    const ex = expo.getContext("2d");
    if (dt > 0) { ex.globalCompositeOperation = "destination-out"; ex.fillStyle = "rgba(0,0,0,0.012)"; ex.fillRect(0, 0, ew, eh); ex.globalCompositeOperation = "source-over"; }
    for (const [x, y, kind] of T.sites) {
      ex.fillStyle = kind === 6 ? c.fission : c.photon; ex.globalAlpha = 0.18; ex.beginPath(); ex.arc(X(x), Y(y), phone ? 3 : 4.5, 0, TAU); ex.fill(); ex.globalAlpha = 0.8; ex.beginPath(); ex.arc(X(x), Y(y), phone ? 1.3 : 1.8, 0, TAU); ex.fill();
      const b = Math.floor(x - WALL); if (b >= 0 && b < prof.length) prof[b]++;
    }
    ex.globalAlpha = 1; T.sites.length = 0;
    ctx.drawImage(expo, 0, 0, W, H);
    // a few drawn neutrons: the recorded track animated, collisions as ticks
    if (dt > 0 && (!vis.length || S.time - vis[vis.length - 1].t0 > 0.6)) { const rec = []; history(S, M, R, T, rec); vis.push({ t0: S.time, rec }); if (vis.length > 5) vis.shift(); }
    for (const v of vis) {
      const age = S.time - v.t0, fade = 1 - smooth(2.6, 3.4, age);
      v.rec.forEach((path, pi) => {
        const n = Math.min(path.length, Math.floor(age * 150) + 2);
        for (let i = Math.max(1, n - 50); i < n; i++) {
          const a = path[i - 1], b = path[i], ya = Y(a[1]), yb = Y(b[1]);
          if (Math.abs(ya - yb) < (bot - top) * 0.5) g.line(X(a[0]), ya, X(b[0]), yb, pi ? c.photon : c.neutron, 1 + 1.2 * clamp(Math.log10(b[2] / 1e-6) / 7, 0, 1), 0.7 * fade * (0.15 + 0.85 * (1 - (n - i) / 50)));
          if (b[3] === "t6" || b[3] === "t7") g.glow(X(b[0]), yb, 14, b[3] === "t6" ? c.fission : c.photon, 0.9 * fade);
          if (b[3] === "n2n") { g.glow(X(b[0]), yb, 16, c.photon, 0.9 * fade); }
          if (b[3] === "cap") g.dot(X(b[0]), yb, 3, c.proton, fade);
        }
        if (n < path.length) { const h = path[n - 1]; g.ball(X(h[0]), Y(h[1]), 4, c.neutron, fade); }
      });
    }
    // depth profile of tritium production
    const py0 = bot + (phone ? 26 : 34), ph = H * (phone ? 0.12 : 0.11), pm = Math.max(1, ...prof);
    const pts = prof.map((v, i) => [X(WALL + i + 0.5), py0 + ph - (ph * v) / pm]);
    if (pts.length > 1) { g.area([[X(WALL), py0 + ph], ...pts, [X(WALL + S.depth), py0 + ph]], c.fission, 0.3); g.poly(pts, c.fission, 2); }
    g.line(X(WALL), py0 + ph, X(WALL + S.depth), py0 + ph, c.faint, 1);
    g.label("tritium made, by depth", X(WALL) + 4, py0 - 4, { color: c.soft, size: 11, align: "left" });
    g.label(`${S.depth} cm`, X(WALL + S.depth), py0 + ph + 12, { color: c.soft, size: 11 });
    // counters
    const N = Math.max(1, T.N), tbr = (T.t6 + T.t7) / N, ok = tbr > 1.05;
    g.label(`TBR ${tbr.toFixed(2)}`, phone ? W / 2 : W * 0.3, phone ? 16 : 30, { color: ok ? c.fission : c.proton, size: phone ? 18 : 24, weight: 700, serif: true });
    const line = `⁶Li ${(T.t6 / N).toFixed(2)} · ⁷Li ${(T.t7 / N).toFixed(2)} · (n,2n) ${(T.n2n / N).toFixed(2)} · captured ${((T.capFe + T.capPb) / N).toFixed(2)} · leaked ${(T.leak / N).toFixed(2)}`;
    g.label(phone ? `⁶Li ${(T.t6 / N).toFixed(2)} · ⁷Li ${(T.t7 / N).toFixed(2)} · (n,2n) ${(T.n2n / N).toFixed(2)}` : line, phone ? W / 2 : W * 0.66, phone ? 40 : 30, { color: c.soft, size: phone ? 11 : 12 });
    g.label(`per fusion neutron · ${T.N} neutrons · cross sections are simple fits`, W / 2, H - (phone ? 8 : 14), { color: c.faint, size: 11 });
  }

  // ---------- the first wall ----------
  const atoms = []; let wallK = "";
  function drawWall(g, S, dt) {
    const { W, H, c } = g, phone = W < 600, m = MATS[S.wmat], L = load(S.wmat);
    const x0 = phone ? 14 : W * 0.12, x1 = W - (phone ? 14 : W * 0.08), y0 = phone ? 64 : H * 0.16, y1 = H * (phone ? 0.66 : 0.66);
    const gb = lerp(x0, x1, 0.62); // a grain boundary
    // the lattice
    const sp = phone ? 15 : 20;
    for (let y = y0; y <= y1; y += sp) for (let x = x0 + ((((y - y0) / sp) % 2) * sp) / 2; x <= x1; x += sp) if (Math.abs(x - gb) > sp * 0.4) g.ball(x + Math.sin(S.time * 3 + x * 0.3 + y) * 0.4, y, sp * 0.3, S.wmat === "Cu" ? c.warm : S.wmat === "W" ? c.soft : S.wmat === "Si" ? c.cool : c.faint, 0.75);
    g.line(gb, y0 - 8, gb, y1 + 8, c.soft, 1.2, 0.5, [3, 4]); g.label("grain boundary", gb, y1 + 20, { color: c.soft, size: 11 });
    // incoming 14.1 MeV neutrons
    for (let i = 0; i < 6; i++) { const u = (S.time * 0.9 + i / 6) % 1, y = lerp(y0, y1, ((i * 0.37 + Math.floor(S.time * 0.9 + i / 6) * 0.61) % 1)); g.line(x0 - 60 + u * 80 - 26, y, x0 - 60 + u * 80, y, c.neutron, 2, 0.6 * (1 - u)); }
    g.label("14.1 MeV", x0 - 4, y0 - 14, { color: c.neutron, size: 11, weight: 600, align: "left" });
    // reaction products at the library's relative rates: He sticks and drifts to the boundary, H wanders off
    if (wallK !== S.wmat) { wallK = S.wmat; atoms.length = 0; }
    if (L.state === "ok" && dt > 0) {
      const tot = L.na + L.np + L.n2n, rate = 9; // events per second on screen, split by cross section
      if (Math.random() < rate * dt) { const u = Math.random() * tot, kind = u < L.na ? "He" : u < L.na + L.np ? "H" : "2n";
        atoms.push({ kind, x: lerp(x0, x1, Math.random()), y: lerp(y0, y1, Math.random()), t0: S.time, vx: 0, vy: 0 }); }
    }
    for (let i = atoms.length - 1; i >= 0; i--) {
      const a = atoms[i], age = S.time - a.t0;
      if (a.kind === "He") { a.x += (gb - a.x) * Math.min(1, dt * 0.25) + (Math.random() - 0.5) * 0.8; a.y += (Math.random() - 0.5) * 0.8; g.glow(a.x, a.y, 10, c.alpha, 0.45); g.ball(a.x, a.y, 4.2, c.alpha); }
      else if (a.kind === "H") { a.x += (Math.random() - 0.5) * 6 + dt * 30; a.y += (Math.random() - 0.5) * 6; g.ball(a.x, a.y, 3.2, c.proton, Math.max(0, 1 - age / 3)); if (age > 3 || a.x > x1 + 30) atoms.splice(i, 1); }
      else { const d = age * 140; g.line(a.x, a.y, a.x + d, a.y - d * 0.3, c.neutron, 1.6, Math.max(0, 1 - age)); g.line(a.x, a.y, a.x + d * 0.8, a.y + d * 0.5, c.neutron, 1.6, Math.max(0, 1 - age)); if (age < 0.3) g.glow(a.x, a.y, 14, c.photon, 0.8); if (age > 1) atoms.splice(i, 1); }
    }
    // helium bubbles on the grain boundary, sized by the helium dose (radius ~ cube root of the gas content)
    if (L.state === "ok") { const he = L.na * 1e-27 * 4.43e13 * S.load * S.yrs * 3.156e7 * 1e6, rb = Math.min(sp * 0.9, 1.6 * Math.cbrt(he));
      for (let i = 0; i < 7; i++) { const by = lerp(y0, y1, (i + 0.5) / 7) + Math.sin(i * 2.1) * 6; if (rb > 0.5) { g.glow(gb, by, rb * 2.2, c.alpha, 0.25); g.dot(gb, by, rb, c.alpha, 0.25); g.ring(gb, by, rb, c.alpha, 1.4, 0.8); } } }
    if (atoms.length > 260) atoms.splice(atoms.findIndex((a) => a.kind === "He"), 1);
    // readouts
    const ly = y1 + (phone ? 44 : 54), fs = phone ? 12 : 14;
    g.label(m[2], W / 2, phone ? 16 : 28, { color: c.ink, size: phone ? 15 : 18, weight: 600, serif: true });
    if (L.state === "ok") {
      const phi = 4.43e13 * S.load, sec = S.yrs * 3.156e7, appm = (mb) => mb * 1e-27 * phi * sec * 1e6;
      g.label(`σ at 14.1 MeV:  (n,α) ${L.na.toFixed(1)} mb · (n,p) ${L.np.toFixed(1)} mb · (n,2n) ${L.n2n.toFixed(0)} mb`, W / 2, phone ? 36 : 52, { color: c.soft, size: phone ? 11 : 12 });
      g.ball(W * 0.22, ly, 5, c.alpha); g.label(`helium ${appm(L.na).toFixed(0)} appm`, W * 0.22 + 10, ly, { color: c.alpha, size: fs, weight: 700, align: "left" });
      g.ball(W * 0.6, ly, 4, c.proton); g.label(`hydrogen ${appm(L.np).toFixed(0)} appm`, W * 0.6 + 10, ly, { color: c.proton, size: fs, weight: 700, align: "left" });
      { const t = WT.tr(`after ${S.yrs.toFixed(1)} years at ${S.load.toFixed(1)} MW/m² · 14.1 MeV neutrons only · σ from INCOGNITA library v0.2`), k = t.lastIndexOf(" · ");
        if (phone && k > 0) { g.label(t.slice(0, k), W / 2, ly + 20, { color: c.faint, size: 11, raw: true }); g.label(t.slice(k + 3), W / 2, ly + 34, { color: c.faint, size: 11, raw: true }); }
        else g.label(t, W / 2, ly + (phone ? 22 : 28), { color: c.faint, size: 11, raw: true }); }
      g.label("helium stays and gathers into bubbles; hydrogen mostly diffuses out", W / 2, ly + (phone ? 52 : 48), { color: c.soft, size: 11 });
    } else g.label(L.state === "fail" ? "could not load the library file" : "loading INCOGNITA's cross sections…", W / 2, ly, { color: c.soft, size: 12 });
  }
})();
