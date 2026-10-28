/* Chapter: the optical model (omp/). Exemplar chapter: other chapters follow this structure.
 * Scenes (S.mode): "wave" = plane wave through a complex potential, eikonal field;
 *                   "rings" = partial waves as rings of impact parameter, neutrons fired at the target;
 *                   "hill"  = effective potential for one l, tunnelling through the centrifugal barrier.
 * Shapes follow omp/potential.py (Woods-Saxon real well, surface absorption) and omp/schrodinger.py (T = 1 - |S|^2);
 * numbers are illustrative (A = 56, R = 4.8 fm, V = 50 MeV). */
(function () {
  const { TAU, clamp, lerp, smooth, rng } = WT.util;
  const R_FM = 4.8, V0 = 50, HB2M = 20.7;               // fm, MeV, hbar^2/2m (MeV fm^2)
  const kOf = (E) => 0.2197 * Math.sqrt(Math.max(E, 1e-4)); // fm^-1, nucleon on A=56
  // schematic transmission coefficient: full absorption for impact parameters inside the nucleus,
  // a soft edge of ~1 partial wave, and the s-wave low-energy fall-off (T0 ~ sqrt(E))
  function Tl(l, E, W) {
    const k = kOf(E), kr = k * (R_FM + 1.0);
    const edge = 1 / (1 + Math.exp((l + 0.5 - kr) / 0.55));
    const lowE = 1 - Math.exp(-2.2 * Math.sqrt(E));       // reflection at the sharp surface when lambda >> R
    const abs = 1 - Math.exp(-W / 2.5);                     // no absorption, no reaction
    return clamp(edge * lowE * abs, 0, 1);
  }
  function sigmaR(E, W) { const k = kOf(E); let s = 0; for (let l = 0; l < 40; l++) s += (2 * l + 1) * Tl(l, E, W); return (Math.PI / (k * k)) * s / 100; } // barns

  let field = null, fctx = null;
  const shots = [];
  const tally = { hit: new Array(9).fill(0), tot: new Array(9).fill(0) }; // per-ring count of the last volley
  const resetTally = () => { tally.hit.fill(0); tally.tot.fill(0); };

  WT.chapter("omp", {
    num: "Chapter 5", title: "A cloudy crystal ball", short: "Optical model",
    lead: "Before anything else, the engine asks a simpler question: what does the nucleus look like to an incoming neutron?",
    html: `
<div class="step">
  <p>In quantum mechanics a neutron is also a wave. The picture shows one rolling in from the left, its crests as bright bands, toward a nucleus (the dashed circle). Nothing acts on it yet, so the crests pass straight through.</p>
  <div class="ctl"><label for="omp-e">Neutron energy (MeV)</label><input id="omp-e" type="range" data-bind="E" min="0.2" max="40" step="0.1" value="8"><output data-show="E" data-fmt="1"></output></div>
  <p>Drag the energy and watch the wavelength at the bottom, in femtometres (fm, 10⁻¹⁵ m). Slow neutrons have long waves: below about 9 MeV one wavelength is wider than this whole nucleus.</p>
</div>
<div class="step">
  <h3>The real part pulls</h3>
  <p>The <b>optical potential</b> is the averaged force of the whole nucleus on the neutron. Its <em>real part</em> is a well about 50 MeV deep: the neutron speeds up inside, so the crests crowd together. The engine gives it a Woods–Saxon shape, flat and deep in the middle, fading smoothly to zero at the surface.</p>
</div>
<div class="step">
  <h3>The imaginary part absorbs</h3>
  <p>The shadow behind the nucleus is the neutrons lost to reactions. The <em>imaginary part</em> of the potential models them: it shrinks the wave instead of bending it, mostly near the surface (the coloured ring).</p>
  <div class="ctl"><label for="omp-w">Absorption W (MeV)</label><input id="omp-w" type="range" data-bind="W" min="0" max="14" step="0.5" value="7"><output data-show="W" data-fmt="1"></output></div>
  <p>Drag <i>W</i> to 0 and the shadow fills in: no absorption, no reactions. Hence the name optical model: the nucleus is a cloudy glass ball that partly bends and partly absorbs.</p>
</div>
<div class="step">
  <h3>Aim matters</h3>
  <p>Seen head-on, the target splits into rings, one per <b>partial wave</b> <i>l</i> = 0, 1, 2, … A neutron passing at distance <i>b</i> from the centre carries <b>angular momentum</b> <i>l</i> ≈ <i>k b</i>, where <i>k</i> grows with energy. The darker a ring, the larger its <b>transmission coefficient</b> <i>T<sub>l</sub></i>: the chance that a neutron in that ring is absorbed.</p>
  <div class="ctl"><label for="omp-e3">Neutron energy (MeV)</label><input id="omp-e3" type="range" data-bind="E" min="0.2" max="40" step="0.1" value="8"><output data-show="E" data-fmt="1"></output></div>
  <div class="btns"><button class="btn" data-act="fire">Fire 200 neutrons</button></div>
  <p>Orange flashes are absorbed neutrons; the bars count each ring's absorbed share against the model's <i>T<sub>l</sub></i> (the tick). Inner rings absorb nearly everything, outer rings let neutrons pass. At low energy the rings are huge and only <i>l</i> = 0 matters.</p>
</div>
<div class="step">
  <h3>Swinging past the nucleus</h3>
  <p>A neutron with a lot of angular momentum passes too far out to touch the nucleus: that is the <b>centrifugal barrier</b>. Seen from above, every neutron here belongs to one partial wave <i>l</i>, so it passes at the same <b>swing distance</b> <i>b</i> ≈ (<i>l</i>+½)/<i>k</i> (the dashed circle).</p>
  <p>But each neutron is a wave, fuzzy over about one reduced wavelength λ̄ (the glow). Even when its path misses, the fuzzy edge can brush the surface and get in: <b>tunnelling</b>.</p>
  <div class="ctl"><label for="omp-l">Partial wave l</label><input id="omp-l" type="range" data-bind="L" min="0" max="8" step="1" value="3" data-instant><output data-show="L" data-fmt="0"></output></div>
  <div class="ctl"><label for="omp-e2">Energy (MeV)</label><input id="omp-e2" type="range" data-bind="E" min="0.2" max="40" step="0.1" value="8"><output data-show="E" data-fmt="1"></output></div>
  <p>Raise <i>l</i> and the path moves out: fewer get in. Raise the energy and the same <i>l</i> passes closer, with less fuzz. The engine finds each <i>T<sub>l</sub></i> exactly by solving the Schrödinger equation through the full potential; <i>S</i> measures how much wave comes back out.</p>
  <div class="formula">T<sub>lj</sub> = 1 − |S<sub>lj</sub>|²</div>
</div>
<div class="step">
  <h3>Adding up the target</h3>
  <p>The disc on the right is how big the nucleus looks to the neutron: the <b>reaction cross section</b>, in barns (10⁻²⁴ cm²). Each ring adds its area times <i>T<sub>l</sub></i> to it. The dashed circle is the geometric size.</p>
  <div class="ctl"><label for="omp-e4">Neutron energy (MeV)</label><input id="omp-e4" type="range" data-bind="E" min="0.2" max="40" step="0.1" value="8"><output data-show="E" data-fmt="1"></output></div>
  <div class="btns"><button class="btn ghost" data-act="sum">Add up again</button></div>
  <p>Change the energy and the sum runs again: at low energy one or two big rings make almost the whole disc; at high energy many thin rings add slivers and the disc nears the geometric size.</p>
  <div class="formula">σ<sub>R</sub> = (π/k²) Σ (2l+1) T<sub>l</sub></div>
  <p>The <i>T<sub>l</sub></i> feed the rest of the engine: they decide how often each spin of the excited nucleus forms and, run in reverse, how easily each particle gets back out.</p>
  <div class="aside">In the code: <code>omp/parameters.py</code> (Koning–Delaroche global potential; dispersive potentials for actinides), <code>omp/schrodinger.py</code> (Numerov integration and Coulomb matching), <code>omp/inverse.py</code> (outgoing particles by detailed balance), <code>omp/regional.py</code> (optional, off by default: a regional adjustment of the well for deformed rare-earth targets, fitted to measured S₀ and S₁).</div>
</div>`,
    setup(S) {
      S.set("mode", "wave"); S.to("Wshow", 0, true); S.to("V", 0, true); S.to("W", 7, true); S.to("E", 8, true); S.to("L", 3, true);
      S.to("nucAlpha", 0.35, true); S.to("ringMix", 0, true); S.to("hillMix", 0, true);
      S.on("sum", () => { S.sumT0 = S.time; });
      S.on("fire", () => { resetTally(); shots.length = 0; const r = rng((performance.now() | 0) + 1); for (let i = 0; i < 200; i++) shots.push({ b: Math.sqrt(r()) * 1.0, a: r() * TAU, u: r(), t0: S.time + i * 0.012 }); });
    },
    steps: [
      (S) => { S.set("mode", "wave"); S.to("V", 0); S.to("Wshow", 0); S.to("ringMix", 0); S.to("hillMix", 0); S.to("nucAlpha", 0.25); },
      (S) => { S.set("mode", "wave"); S.to("V", V0); S.to("Wshow", 0); S.to("ringMix", 0); S.to("hillMix", 0); S.to("nucAlpha", 0.45); },
      (S) => { S.set("mode", "wave"); S.to("V", V0); S.to("Wshow", 1); S.to("ringMix", 0); S.to("hillMix", 0); S.to("nucAlpha", 0.45); },
      // the later scenes have no W slider: restore the standard absorption, or a reader who followed "drag W to 0" sees nothing absorbed
      (S) => { const w0 = S.target.W; S.to("W", 7, true); S.set("mode", "rings"); S.to("ringMix", 1); S.to("hillMix", 0); if (w0 !== 7 || !tally.tot.some((x) => x)) S.handlers.fire(); },
      (S) => { S.to("W", 7, true); S.set("mode", "hill"); S.to("ringMix", 0); S.to("hillMix", 1); },
      (S) => { S.to("W", 7, true); S.set("mode", "sum"); S.to("ringMix", 1); S.to("hillMix", 0); S.sumT0 = /[?&]shot=/.test(location.search) ? S.time - 2.2 : S.time; S.sumE = S.target.E; },
    ],
    frame(g, S) {
      const { W: Wd, H: Hd, c } = g;
      if (S.mode === "wave") drawWave(g, S);
      else if (S.mode === "rings") drawRings(g, S);
      else if (S.mode === "sum") drawSum(g, S);
      else drawHill(g, S);
    },
  });

  // ---------- scene 1: wave through a complex potential ----------
  function drawWave(g, S) {
    const { W, H, c } = g, ctx = g.ctx;
    const cx = W * 0.56, cy = H * 0.5, Rpx = Math.min(W, H) * 0.17, s = R_FM / Rpx; // fm per px
    const NX = 200, NY = Math.round(200 * H / W);
    if (!field || field.width !== NX || field.height !== NY) { field = document.createElement("canvas"); field.width = NX; field.height = NY; fctx = field.getContext("2d"); }
    const img = fctx.createImageData(NX, NY), d = img.data;
    const k = kOf(S.E), kin = kOf(S.E + S.V), kap = 0.055 * S.W * (S.Wshow ?? 0), om = 2.2;
    const col = hexRgb(c.neutron), bg = hexRgb(c.paper);
    for (let j = 0; j < NY; j++) {
      const y = ((j + 0.5) / NY * H - cy) * s;
      const half = Math.abs(y) < R_FM ? Math.sqrt(R_FM * R_FM - y * y) : 0;
      for (let i = 0; i < NX; i++) {
        const x = ((i + 0.5) / NX * W - cx) * s;
        const Lin = half ? clamp(x + half, 0, 2 * half) : 0;
        // surface-weighted absorption: more where the chord runs near the rim
        const rim = half ? 1 + 1.4 * (1 - half / R_FM) : 1;
        const ph = k * x + (kin - k) * Lin - om * S.time;
        const amp = Math.exp(-kap * rim * Lin);
        const v = 0.5 + 0.5 * Math.cos(ph);
        const a = v * v * amp * 0.85;
        const p = (j * NX + i) * 4;
        d[p] = lerp(bg[0], col[0], a); d[p + 1] = lerp(bg[1], col[1], a); d[p + 2] = lerp(bg[2], col[2], a); d[p + 3] = 255;
      }
    }
    fctx.putImageData(img, 0, 0);
    ctx.save(); ctx.imageSmoothingEnabled = true; ctx.drawImage(field, 0, 0, W, H); ctx.restore();
    g.vignette(0.16);
    // nucleus outline (the well) and nucleons, faint
    g.nucleus(cx, cy, Rpx * 0.92, { N: 56, Z: 26, t: S.time, alpha: S.nucAlpha, jiggle: 0.4 });
    g.ring(cx, cy, Rpx, c.ink, 1.2, 0.55, [4, 5]);
    if ((S.Wshow ?? 0) > 0.5) {
      g.ring(cx, cy, Rpx * 1.02, c.proton, 6, 0.18 * S.Wshow);
      g.label("absorbing surface", cx, cy - Rpx - 18, { color: c.proton, size: 13, bg: true });
      if (W < 600) g.label("shadow: neutrons lost to reactions", W - 12, cy + Rpx + 50, { color: c.soft, size: 12, align: "right", bg: true });
      else g.label("shadow: neutrons lost to reactions", Math.min(cx + Rpx * 1.9, W - 120), cy + Rpx * 1.3, { color: c.soft, size: 13, bg: true });
    }
    const lam = 2 * Math.PI / kOf(S.E);
    g.label(`wavelength ${lam.toFixed(1)} fm   ·   nucleus ${(2 * R_FM).toFixed(1)} fm across`, W / 2, H - 22, { color: c.soft, size: 13, bg: true });
    if (S.V > 5) g.label("crests crowd inside the well", cx, cy + Rpx + 22, { color: c.neutron, size: 13, bg: true });
  }

  // ---------- scene 2: partial-wave rings ----------
  function drawRings(g, S) {
    const { W, H, c } = g;
    const phoneR = W < 600, cx = W * (phoneR ? 0.62 : 0.5), cy = phoneR ? H * 0.53 : H * 0.55, maxR = phoneR ? W * 0.28 : Math.min(W, H) * 0.34;
    const k = kOf(S.E);
    // show the target out to b = max(1.6 R, (l+1)/k for the last visible ring), scaled to maxR
    const bMax = Math.max(R_FM * 1.7, Math.min(5.5 / k, 30));
    const px = maxR / bMax;
    const L = Math.ceil(k * bMax);
    for (let l = Math.min(L, 40); l >= 0; l--) {
      const r1 = Math.min((l + 1) / k, bMax) * px;
      const T = Tl(l, S.E, S.W);
      g.dot(cx, cy, r1, c.neutron, 0.08 + 0.72 * T);
      g.ring(cx, cy, r1, c.paper, 1.2, 0.9);
      if (r1 - (l / k) * px > 16 && l < 6) g.label(`l=${l}`, cx + ((l + 0.5) / k) * px, cy + (phoneR ? (l % 2 ? 8 : -8) : 0), { color: T > 0.5 ? c.card : c.soft, size: 12 });
    }
    g.ring(cx, cy, R_FM * px, c.ink, 1.5, 0.8, [5, 5]);
    g.label("nuclear radius", cx, cy - R_FM * px - 12, { color: c.ink, size: 12 });
    // shots
    const now = S.time;
    for (let i = shots.length - 1; i >= 0; i--) {
      const sh = shots[i], age = now - sh.t0; if (age < 0) continue;
      const bfm = sh.b * bMax, l = Math.floor(k * bfm), hit = sh.u < Tl(l, S.E, S.W);
      const x = cx + Math.cos(sh.a) * bfm * px, y = cy + Math.sin(sh.a) * bfm * px;
      if (age >= 0.25 && !sh.counted) { sh.counted = true; if (l < 9) { tally.tot[l]++; if (hit) tally.hit[l]++; } }
      if (age < 0.25) g.dot(x, y, 3, c.ink, age / 0.25);
      else if (hit) g.glow(x, y, 12, c.warm, 0.7 * Math.max(0, 1 - (age - 0.25) / 1.4));
      else g.dot(x, y, 2.2, c.faint, Math.max(0, 1 - (age - 0.25) / 1.4));
      if (age > 1.8) shots.splice(i, 1);
    }
    const sR = sigmaR(S.E, S.W), geo = Math.PI * Math.pow(R_FM + 1 / k, 2) / 100;
    g.label(`reaction cross section ≈ ${sR.toFixed(2)} b`, phoneR ? W / 2 : cx, H - 44, { color: c.ink, size: 16, weight: 600, serif: true });
    if (phoneR) g.label(`geometric ${geo.toFixed(2)} b · darker = more absorbed · orange = absorbed`, W / 2, H - 20, { color: c.faint, size: 11 });
    else g.label(`geometric size π(R+λ̄)² ≈ ${geo.toFixed(2)} b · darker ring = more absorbed · orange flash = absorbed`, cx, H - 20, { color: c.faint, size: 12 });
    // a new energy invalidates the old count: clear it and fire a fresh volley once the slider settles
    if (tally.E === undefined) tally.E = S.target.E;
    if (S.target.E !== tally.E) { tally.E = S.target.E; resetTally(); shots.length = 0; tally.refireAt = S.time + 0.5; }
    if (tally.refireAt && S.time > tally.refireAt) { tally.refireAt = 0; S.handlers.fire(); }
    // per-ring tally of the last volley: filled bar = share of that ring's neutrons absorbed; dark tick = the model's T_l
    const n = 7, phone = W < 600, bw = phone ? 15 : 20, bh = phone ? 54 : 84;
    // fixed column pitch wide enough for the text under the bars at the size g.label really draws (min 10 px phone, 12 px desktop):
    // counts alternate between two rows (a big count like "150/200" at low energy still never touches its neighbour)
    g.ctx.save(); g.ctx.font = `500 ${phone ? 10 : 12}px "IBM Plex Sans", "Segoe UI", system-ui, sans-serif`;
    const tw = g.ctx.measureText(phone ? "l=6" : "88/88").width; g.ctx.restore();
    const gap = Math.max(phone ? 9 : 10, Math.ceil(tw + (phone ? 6 : 10) - bw));
    const x0 = phone ? 14 : cx - (n * (bw + gap) - gap) / 2, y0 = phone ? 34 : 44;
    g.label("absorbed, ring by ring", x0 + (n * (bw + gap) - gap) / 2, y0 - 26, { color: c.ink, size: 12, weight: 600 });
    g.label("bar: your neutrons · tick: model Tₗ", x0 + (n * (bw + gap) - gap) / 2, y0 - 11, { color: c.faint, size: 11 });
    for (let l = 0; l < n; l++) {
      const T = Tl(l, S.E, S.W), xb = x0 + l * (bw + gap), tot = tally.tot[l], f = tot ? tally.hit[l] / tot : 0;
      g.ctx.fillStyle = g.rgba(c.line, 0.7); g.ctx.fillRect(xb, y0, bw, bh);
      if (tot) { g.ctx.fillStyle = g.rgba(c.warm, 0.85); g.ctx.fillRect(xb, y0 + bh * (1 - f), bw, bh * f); }
      g.line(xb - 3, y0 + bh * (1 - T), xb + bw + 3, y0 + bh * (1 - T), c.ink, 2);
      g.label(`l=${l}`, xb + bw / 2, y0 + bh + 12, { color: c.soft, size: 11 });
      g.label(tot ? `${tally.hit[l]}/${tot}` : "–", xb + bw / 2, y0 + bh + 26 + (l % 2 ? 12 : 0), { color: c.faint, size: 10 });
    }
  }

  // ---------- scene 2b: adding up the rings into the reaction cross section ----------
  function drawSum(g, S) {
    const { W, H, c } = g, ctx = g.ctx, phone = W < 600;
    if (S.target.E !== S.sumE) { S.sumE = S.target.E; S.sumT0 = S.time + 0.4; }
    const k = kOf(S.E), lam = 1 / k;
    let L = 0; while (L < 30 && (Tl(L, S.E, S.W) > 0.01 || L < 1)) L++;
    const rings = []; let acc = 0;
    for (let l = 0; l < L; l++) { const T = Tl(l, S.E, S.W), add = Math.PI * lam * lam * (2 * l + 1) * T; rings.push({ l, T, r0: l * lam, r1: (l + 1) * lam, add, before: acc }); acc += add; }
    const total = acc, geoR = R_FM + lam;
    // one shared fm scale for both pictures, so the disc's area is directly comparable to the rings
    const bMax = Math.max(L * lam, geoR) * 1.05, side = phone ? W * 0.46 : W * 0.4, px = Math.min(side / 2, H * 0.3) / bMax;
    const cxL = W * 0.27, cxR = W * 0.73, cy = H * 0.46;
    const per = Math.max(0.35, Math.min(0.9, 4.5 / L)), t = Math.max(0, S.time - S.sumT0);
    const done = Math.min(L, Math.floor(t / per)), frac = smooth(0, 1, (t - done * per) / per);
    // left: the rings, dimmed once they have been added
    for (let i = L - 1; i >= 0; i--) {
      const R = rings[i], gone = i < done || (i === done && frac > 0.05);
      g.dot(cxL, cy, R.r1 * px, c.neutron, (0.08 + 0.72 * R.T) * (gone ? 0.25 : 1));
      g.ring(cxL, cy, R.r1 * px, c.paper, 1.2, 0.9);
    }
    g.ring(cxL, cy, R_FM * px, c.ink, 1.2, 0.6, [4, 4]);
    g.label("rings: shade = Tₗ", cxL, cy + bMax * px + 22, { color: c.soft, size: 12 });
    // right: the growing disc of equal area, with the geometric size dashed
    const grown = done >= L ? total : rings[done].before + rings[done].add * frac;
    g.glow(cxR, cy, Math.sqrt(grown / Math.PI) * px * 1.4, c.neutron, 0.12);
    g.dot(cxR, cy, Math.sqrt(grown / Math.PI) * px, c.neutron, 0.75);
    g.ring(cxR, cy, geoR * px, c.ink, 1.4, 0.7, [5, 5]);
    g.label("geometric size π(R+λ̄)²", cxR, cy - geoR * px - 12, { color: c.ink, size: 12, bg: true });
    g.label("reaction cross section", cxR, cy + bMax * px + 22, { color: c.soft, size: 12 });
    // the ring in flight: an annulus that keeps T_l of its area, shrinking to a band that wraps onto the disc
    if (done < L) {
      const R = rings[done], x = lerp(cxL, cxR, frac), lift = Math.sin(frac * Math.PI) * H * 0.08;
      const rOutTarget = Math.sqrt((R.before + R.add) / Math.PI), rInTarget = Math.sqrt(R.before / Math.PI);
      const rOut = lerp(R.r1, rOutTarget, frac) * px, rIn = lerp(R.r1 - (R.r1 - R.r0) * R.T, rInTarget, frac) * px;
      ctx.save(); ctx.globalAlpha = 0.85; ctx.fillStyle = c.warm; ctx.beginPath(); ctx.arc(x, cy - lift, Math.max(rOut, 0.5), 0, TAU); ctx.arc(x, cy - lift, Math.max(0, rIn), 0, TAU, true); ctx.fill(); ctx.restore();
      g.label(`ring l=${R.l}: (2l+1)·Tₗ·π/k² = +${(R.add / 100).toFixed(3)} b`, W / 2, H * 0.1, { color: c.warm, size: phone ? 12 : 14, weight: 600, bg: true });
    } else g.label(`all ${L} rings added`, W / 2, H * 0.1, { color: c.soft, size: phone ? 12 : 14, bg: true });
    g.label(`σ_R = ${(grown / 100).toFixed(2)} b`, cxR, cy + bMax * px + 50, { color: c.ink, size: 18, weight: 600, serif: true });
    g.label(`geometric ${(Math.PI * geoR * geoR / 100).toFixed(2)} b`, cxR, cy + bMax * px + 72, { color: c.faint, size: 12 });
  }

  // ---------- scene 3: centrifugal hill ----------
  function drawHill(g, S) {
    // top-down view: neutrons of one partial wave l fly past the nucleus at their swing distance b = (l+1/2)/k.
    // Each neutron is a fuzzy wave packet of width ~λ̄; where its fuzz overlaps the surface it can tunnel in.
    const { W, H, c } = g, phone = W < 600;
    const L = Math.round(S.L), E = S.E, k = kOf(E), lam = 1 / k, b = (L + 0.5) / k, T = Tl(L, E, S.W);
    const cx = W * (phone ? 0.42 : 0.4), cy = H * 0.5;
    const span = Math.max(b + 2.2 * lam, R_FM * 1.6) * 1.08, px = Math.min(H * 0.36, W * 0.34) / span;
    // the nucleus and its absorbing surface
    g.glow(cx, cy, R_FM * px * 1.5, c.warm, 0.08);
    g.nucleus(cx, cy, R_FM * px, { N: 56, Z: 26, seed: 3, t: S.time, jiggle: 0.25 });
    g.ring(cx, cy, R_FM * px, c.warm, 1.6, 0.6, [4, 4]);
    // this partial wave's ring of aim (as in the previous step), and the swing distance
    { const ctx = g.ctx; ctx.save(); ctx.globalAlpha = 0.12; ctx.fillStyle = c.neutron; ctx.beginPath(); ctx.arc(cx, cy, (L + 1) / k * px, 0, TAU); ctx.arc(cx, cy, L / k * px, 0, TAU, true); ctx.fill(); ctx.restore(); }
    g.ring(cx, cy, b * px, c.neutron, 1.2, 0.55, [3, 4]);
    // the stream: one neutron every 0.7 s along y = cy - b (alternating above/below)
    if (!S.swing || S.swing.key !== `${L}|${E.toFixed(1)}`) { S.swing = { key: `${L}|${E.toFixed(1)}`, list: [], next: S.time + 0.7, n: 0, hit: 0 }; for (let i = 6; i >= 1; i--) S.swing.list.push({ t0: S.time - i * 0.7, side: i % 2 ? 1 : -1, absorb: Math.random() < T, done: false }); }
    const sw = S.swing, speed = W * 0.28;
    if (S.time > sw.next) { sw.next = S.time + 0.7; const side = sw.list.length % 2 ? 1 : -1; sw.list.push({ t0: S.time, side, absorb: Math.random() < T, done: false }); if (sw.list.length > 14) sw.list.shift(); }
    const xStart = 0.02 * W, xEnd = W * 1.05, fuzz = Math.max(4, lam * px);
    sw.list.forEach((nn) => {
      const x = xStart + (S.time - nn.t0) * speed, y = cy + nn.side * b * px;
      if (nn.absorb && x >= cx) {           // reached closest approach: it tunnels / falls in
        const a = Math.max(0, 1 - (x - cx) / (W * 0.25));
        if (!nn.done) { nn.done = true; sw.n++; sw.hit++; }
        const mx = cx, my = cy + nn.side * Math.min(b, R_FM) * px;
        g.glow(mx, my, 22, c.warm, 0.6 * a); return;
      }
      if (!nn.absorb && x >= cx && !nn.done) { nn.done = true; sw.n++; }
      if (x > xEnd) return;
      const fin = Math.min(1, (x - xStart) / (W * 0.08)), fout = Math.min(1, (xEnd - x) / (W * 0.1));
      g.glow(x, y, fuzz * 1.6, c.neutron, 0.22 * fin * fout); g.ball(x, y, 5, c.neutron, 0.95 * fin * fout);
    });
    // straight-line guides for the two paths
    g.line(0, cy - b * px, W, cy - b * px, c.neutron, 1, 0.18, [2, 6]); g.line(0, cy + b * px, W, cy + b * px, c.neutron, 1, 0.18, [2, 6]);
    // readouts
    const inside = b < R_FM, rx = phone ? W * 0.5 : W * 0.8;
    g.label(`swing distance b ≈ (l+½)/k = ${b.toFixed(1)} fm`, rx, H * 0.1, { color: c.neutron, size: phone ? 12 : 13, weight: 600, bg: true });
    g.label(`nuclear radius R = ${R_FM.toFixed(1)} fm · wave fuzz λ̄ = ${lam.toFixed(1)} fm`, rx, H * 0.1 + 20, { color: c.soft, size: phone ? 11 : 12, bg: true });
    g.label(inside ? "path crosses the nucleus: most get in" : "path misses the nucleus: only the fuzzy edge can tunnel in", W * 0.5, H * 0.9 - 24, { color: c.ink, size: phone ? 13 : 15, weight: 600, serif: true });
    g.label(`absorbed ${sw.hit} of ${sw.n} · model Tₗ = ${T.toFixed(2)}`, W * 0.5, H * 0.9, { color: c.soft, size: 12 });
  }


  function hexRgb(h) { h = (h || "#888888").replace("#", ""); if (h.length === 3) h = h.split("").map((x) => x + x).join(""); const n = parseInt(h, 16); return [(n >> 16) & 255, (n >> 8) & 255, n & 255]; }
})();
