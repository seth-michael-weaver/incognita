/* Hotter means less reactive: Doppler broadening and the fuel-temperature feedback. A fuel pellet's atoms jiggle with
 * thermal speeds ~ sqrt(T); one capture resonance (illustrative, U-238-like: E0 = 6.67 eV, Gn = 1.5 meV, Gg = 23 meV) is
 * Doppler-broadened by a Gaussian of width Delta = sqrt(4 E0 kT / A): the peak drops, the wings widen, the area stays.
 * In a thick lump (n = 0.011 atoms/b, about half a centimetre of UO2) the centre of the resonance is black whatever T is, so
 * absorption follows the width: W(T) = int (1 - exp(-n sigma_T(E))) dE grows with T (self-shielding relaxes). The k gauge
 * converts the extra absorption with an illustrative constant chosen so the fuel-temperature coefficient is -2.5 pcm/K
 * between 300 and 1200 K, a typical size for light-water-reactor fuel. */
(function () {
  const { TAU, clamp, lerp, smooth, rng } = WT.util;
  const E0 = 6.67, GN = 0.0015, GG = 0.023, GT = GN + GG, A = 238, KB = 8.617e-5, NT = 0.011;
  const s0 = 2.608e6 / E0 * ((A + 1) / A) ** 2 * GN / GT;
  const ELO = E0 - 0.6, EHI = E0 + 0.6, NG = 481, dE = (EHI - ELO) / (NG - 1), EXT = 200;
  const cold = []; for (let i = -EXT; i < NG + EXT; i++) { const e = ELO + i * dE, x = 2 * (e - E0) / GT; cold.push(s0 / (1 + x * x)); }
  const cache = new Map();
  function sigT(T) {
    const key = Math.round(T / 5) * 5; if (cache.has(key)) return cache.get(key);
    const D = Math.sqrt(4 * E0 * KB * key / A), k = Math.min(EXT, Math.ceil(3 * D / dE)), w = []; let ws = 0;
    for (let j = -k; j <= k; j++) { const v = Math.exp(-((j * dE) ** 2) / (D * D)); w.push(v); ws += v; }
    const out = new Float64Array(NG); for (let i = 0; i < NG; i++) { let s = 0; for (let j = -k; j <= k; j++) s += w[j + k] * cold[i + EXT + j]; out[i] = s / ws; }
    let W = 0; for (let i = 0; i < NG; i++) W += (1 - Math.exp(-NT * out[i])) * dE;
    const res = { s: out, W, peak: Math.max(...out), D }; cache.set(key, res); if (cache.size > 300) cache.delete(cache.keys().next().value); return res;
  }
  const W300 = sigT(300).W, CK = 900 * 2.5e-5 / (sigT(1200).W / W300 - 1);
  const ATOMS = []; { const q = rng(4); for (let j = -6; j <= 6; j++) for (let i = -6; i <= 6; i++) { const x = (i + (j % 2 ? 0.5 : 0)) / 6.4, y = j * 0.866 / 6.4; if (x * x + y * y < 0.92) ATOMS.push([x, y, q() * TAU, q() * TAU, 0.7 + 0.6 * q()]); } }

  function dial(g, x, y, R, f, col, title, val, fs) {
    const c = g.c, a0 = Math.PI * 0.85, a1 = Math.PI * 2.15, ctx = g.ctx;
    ctx.save(); ctx.lineCap = "round"; ctx.lineWidth = Math.max(5, R * 0.14); ctx.strokeStyle = g.rgba(c.soft, 0.18); ctx.beginPath(); ctx.arc(x, y, R, a0, a1); ctx.stroke();
    ctx.strokeStyle = col; ctx.beginPath(); ctx.arc(x, y, R, a0, lerp(a0, a1, clamp(f, 0, 1))); ctx.stroke(); ctx.restore();
    const an = lerp(a0, a1, clamp(f, 0, 1)); g.glow(x + Math.cos(an) * R, y + Math.sin(an) * R, R * 0.4, col, 0.45);
    g.label(val, x, y + 2, { color: c.ink, size: fs + 3, weight: 600 });
    g.label(title, x, y + R * 0.9 + 4, { color: c.soft, size: fs - 1 });
  }

  WT.chapter("doppler", {
    num: "Chapter 19", title: "Doppler broadening", short: "Doppler",
    html: `
<div class="step">
  <h3>Thermal motion of the target</h3>
  <p>Hotter fuel: its atoms jiggle faster. Each uranium atom is no longer sitting still when a neutron arrives.</p>
  <div class="ctl"><label for="dop-t1">Fuel temperature (K)</label><input id="dop-t1" type="range" data-bind="T" data-instant min="300" max="1500" step="10" value="600"><output data-show="T" data-fmt="0"></output></div>
</div>
<div class="step">
  <h3>Doppler broadening</h3>
  <p>The curve is the chance that uranium-238 catches a neutron, plotted against the neutron's energy. Its height is a target area in <b>barns</b> (one barn is 10<sup>−24</sup> cm², roughly the size a nucleus shows a neutron). Because the atoms move, some meet the neutron head-on and some run away from it, so the narrow peak gets smeared: lower and wider. Its area stays the same.</p>
  <div class="ctl"><label for="dop-t2">Fuel temperature (K)</label><input id="dop-t2" type="range" data-bind="T" data-instant min="300" max="1500" step="10" value="1200"><output data-show="T" data-fmt="0"></output></div>
</div>
<div class="step">
  <h3>Resonance self-shielding</h3>
  <p>A fuel pellet is thick. The shaded band is the share of neutrons it stops at each energy. The peak's centre already stops everything, hot or cold, so a lower peak loses nothing there; the wider wings catch more. More neutrons are lost to capture instead of causing fission, so <i>k</i> drops by itself. (<i>k</i> is how many new fissions each fission leads to; Chapter 20 explains it.)</p>
  <div class="ctl"><label for="dop-t3">Fuel temperature (K)</label><input id="dop-t3" type="range" data-bind="T" data-instant min="300" max="1500" step="10" value="900"><output data-show="T" data-fmt="0"></output></div>
</div>`,
    setup(S) { S.set("T", 600); },
    steps: [(S) => S.set("T", 600), (S) => S.set("T", 1200), (S) => S.set("T", 900)],
    frame(g, S) {
      const { W, H, c, ctx } = g, phone = W < 600, fs = phone ? 11 : 13, T = S.T, st = Math.max(0, S.step);
      const R = sigT(T), R0 = sigT(300), hot = (T - 300) / 1200;
      // ---------- the pellet ----------
      const py = H * 0.2, pr = Math.min(W * (phone ? 0.16 : 0.15), H * 0.15), px = W * (phone ? 0.2 : 0.17);
      g.glow(px, py, pr * 1.6, c.warm, 0.12 + 0.35 * hot);
      ctx.save(); const pg = ctx.createRadialGradient(px - pr * 0.3, py - pr * 0.3, pr * 0.1, px, py, pr); pg.addColorStop(0, g.rgba(c.warm, 0.18 + 0.2 * hot)); pg.addColorStop(1, g.rgba(c.soft, 0.12)); ctx.fillStyle = pg; ctx.beginPath(); ctx.arc(px, py, pr, 0, TAU); ctx.fill(); ctx.restore();
      g.ring(px, py, pr, c.soft, 1.2, 0.5);
      const amp = pr * 0.032 * Math.sqrt(T / 300), sp = 9 * Math.sqrt(T / 300);
      for (const [x, y, p1, p2, w] of ATOMS) g.ball(px + x * pr + amp * Math.sin(S.time * sp * w + p1), py + y * pr + amp * Math.cos(S.time * sp * 1.13 * w + p2), Math.max(2.5, pr * 0.06), c.proton, 0.95);
      g.label(phone ? "fuel atoms" : "uranium atoms in the fuel", px, py + pr + 14, { color: c.soft, size: fs - 1 });
      // thermometer
      const tx = px + pr + (phone ? 22 : 34), tt = py - pr, tb = py + pr * 0.8, tf = lerp(tb, tt, clamp((T - 200) / 1400, 0, 1));
      ctx.save(); ctx.strokeStyle = g.rgba(c.soft, 0.6); ctx.lineWidth = 9; ctx.lineCap = "round"; ctx.beginPath(); ctx.moveTo(tx, tt); ctx.lineTo(tx, tb); ctx.stroke(); ctx.strokeStyle = c.warm; ctx.lineWidth = 5; ctx.beginPath(); ctx.moveTo(tx, tb); ctx.lineTo(tx, tf); ctx.stroke(); ctx.restore();
      g.dot(tx, tb + 5, 8, c.warm); g.glow(tx, tf, 12, c.warm, 0.5);
      g.label(`${T.toFixed(0)} K`, tx, tt - 14, { color: c.warm, size: fs, weight: 600 });
      // ---------- gauges ----------
      const gR = Math.min(W * (phone ? 0.1 : 0.085), H * 0.085), gy = py - 4, g1 = W * (phone ? 0.62 : 0.6), g2 = W * (phone ? 0.86 : 0.83);
      const rel = R.W / W300 - 1, k = 1 - CK * rel, on3 = st >= 2 ? 1 : 0.35;
      g.ctx.save(); g.ctx.globalAlpha = on3;
      dial(g, g1, gy, gR, rel / 0.5, c.photon, phone ? "caught" : "caught in the peak", `${rel >= 0 ? "+" : ""}${(100 * rel).toFixed(0)} %`, fs);
      dial(g, g2, gy, gR, (1 - k) / 0.04, c.accent, "k", k.toFixed(4), fs);
      g.ctx.restore();
      // ---------- the resonance ----------
      const x0 = W * (phone ? 0.1 : 0.08), x1 = W * 0.96, y0 = H * (phone ? 0.52 : 0.46), y1 = H * 0.84, X = (e) => x0 + (x1 - x0) * (e - ELO) / (EHI - ELO), Y = (s) => lerp(y1, y0, s / (R0.peak * 1.05));
      const cur = [], ref = []; for (let i = 0; i < NG; i += 2) { cur.push([X(ELO + i * dE), Y(R.s[i])]); ref.push([X(ELO + i * dE), Y(R0.s[i])]); }
      g.line(x0, y1, x1, y1, c.line, 1);
      const shield = st >= 2; // step 3: shade the share stopped by a thick pellet, 1 - exp(-n sigma)
      g.area([[x0, y1], ...cur, [x1, y1]], c.photon, shield ? 0.08 : 0.22); g.poly(cur, c.photon, shield ? 1.6 : 2.6, shield ? 0.45 : 1);
      if (shield) {
        const Ya = (f) => lerp(y1, y0, f), ab = [], ab0 = [];
        for (let i = 0; i < NG; i += 2) { const x = X(ELO + i * dE); ab.push([x, Ya(1 - Math.exp(-NT * R.s[i]))]); ab0.push([x, Ya(1 - Math.exp(-NT * R0.s[i]))]); }
        g.area([[x0, y1], ...ab, [x1, y1]], c.warm, 0.32); g.poly(ab, c.warm, 2.2, 0.95);
        if (T > 320) g.poly(ab0, c.soft, 1.3, 0.8, [4, 4]);
        g.line(x0, y0, x1, y0, c.warm, 1, 0.4, [2, 4]);
        g.label("all stopped", x1, y0 - 10, { color: c.warm, size: fs - 1, align: "right" });
        const wx = X(E0 + (phone ? 0.36 : 0.33)); g.label(phone ? "wings" : "wider wings catch more", wx, Ya(0.55), { color: c.warm, size: fs - 1, weight: 600, align: "left", bg: true });
      }
      if (T > 320 && !shield) { g.poly(ref, c.soft, 1.4, 0.7, [4, 4]); g.label("300 K", X(E0) + 10, Y(R0.peak) + 2, { color: c.soft, size: fs - 1, align: "left" }); }
      if (!shield) g.label(`${T.toFixed(0)} K`, X(E0) + (T > 320 ? -10 : 10), Y(R.peak) - 12, { color: c.photon, size: fs, weight: 600, align: T > 320 ? "right" : "left" });
      [6.2, 6.4, 6.6, 6.8, 7.0, 7.2].forEach((e) => g.label(phone && e === 7.2 ? "7.2 eV" : e.toFixed(1), X(e), y1 + 12, { color: c.faint, size: fs - 2 }));
      if (!phone) g.label("neutron energy (eV) →", x1, y1 + 28, { color: c.soft, size: fs - 1, align: "right" });
      g.label(shield ? (phone ? "share stopped in the fuel" : "share of neutrons stopped in the fuel") : "capture cross section", x0, y0 - 10, { color: shield ? c.warm : c.soft, size: fs - 1, align: "left" });
      const rd = { color: c.ink, size: fs + 1, weight: 600, serif: true };
      if (shield) {
        if (phone) { g.label("the centre already stops everything;", W * 0.5, H * 0.91, rd); g.label("the wider wings catch more", W * 0.5, H * 0.91 + fs + 6, rd); }
        else g.label("the peak's centre already stops everything; the wider wings catch more", W * 0.5, H * 0.93, rd);
      } else if (phone) {
        g.label(`peak ${(R.peak / 1000).toFixed(1)}k barns · width ${(1000 * R.D).toFixed(0)} meV`, W * 0.5, H * 0.91, rd);
        g.label("area unchanged", W * 0.5, H * 0.91 + fs + 6, rd);
      } else g.label(`peak ${(R.peak / 1000).toFixed(1)}k barns · Doppler width ${(1000 * R.D).toFixed(0)} meV · area unchanged`, W * 0.5, H * 0.93, rd);
      g.label("illustration", W - 6, H - 10, { color: c.faint, size: 10, align: "right" });
    },
  });
})();
