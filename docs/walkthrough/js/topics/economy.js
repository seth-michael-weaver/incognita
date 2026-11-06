/* The neutron economy: the life of one generation of neutrons in a thermal (light-water) reactor, drawn as a loop.
 * Six-factor formula k = eta f p eps P_FNL P_TNL. Reference set (typical thermal reactor, Duderstadt & Hamilton, Nuclear
 * Reactor Analysis, 1976, pp. 82-85, adjusted there so the product is 1): eta = 1.65, f = 0.71, p = 0.87, eps = 1.02,
 * P_FNL = 0.97, P_TNL = 0.99 (product 0.998). The sliders move the factors with simple illustrative models, calibrated to
 * reproduce that set at 3 % enrichment, typical water-to-fuel ratio m = 1 and typical size s = 1:
 *   fuel absorption per heavy atom a(e) = 681 e + 2.68 (1 - e) b (2200 m/s: U-235 sigma_a = 681 b, sigma_f = 585 b, nu = 2.43;
 *   U-238 sigma_a = 2.68 b); eta(e) = 1.65 * [nu 585 e / a(e)] / [same at 3 %] (spectrum-averaging scale kept from the set);
 *   f = 1 / (1 + (0.358 + 0.05 m) sqrt(a(3 %) / a(e)))  (water, structure, boron and poisons absorb the rest; the square root
 *   softens the dependence because part of that parasitic share, the boron, is itself set by the enrichment);
 *   p = exp(-0.1436 (1 - e) / m) (resonance capture in U-238 falls with more moderator: p ~ exp(-N_F I / xi Sigma_s));
 *   eps = 1 + 0.02 / sqrt(m); P_FNL = 1 / (1 + 0.0309 / (s^2 sqrt m)); P_TNL = 1 / (1 + 0.0101 sqrt(m) / s^2) (leakage ~ B^2 ~ 1/size^2).
 * These give the textbook behaviour: natural uranium in light water stays far below 1; k has a maximum in the water-to-fuel
 * ratio (here near m = 2), so the typical lattice is under-moderated, as real LWRs are; small cores leak too much. */
(function () {
  const { TAU, clamp, lerp, smooth, rng } = WT.util;
  const r = rng(41), SHOT = () => document.body.classList.contains("shot");
  const aF = (e) => 681 * e + 2.68 * (1 - e), eta0 = (e) => (2.43 * 585 * e) / aF(e), A3 = aF(0.03), ETA3 = eta0(0.03);
  function factors(enr, m, s) {
    const e = enr / 100;
    const eta = 1.65 * eta0(e) / ETA3, f = 1 / (1 + (0.358 + 0.05 * m) * Math.sqrt(A3 / aF(e))), p = Math.exp(-0.1436 * (1 - e) / m);
    const eps = 1 + 0.02 / Math.sqrt(m), fnl = 1 / (1 + 0.0309 / (s * s * Math.sqrt(m))), tnl = 1 / (1 + 0.0101 * Math.sqrt(m) / (s * s));
    return { eta, f, p, eps, fnl, tnl, k: eta * f * p * eps * fnl * tnl, kinf: eta * f * p * eps };
  }
  const hits = {}, gen = {};
  /** rounded-rectangle track as a sampled polyline from the middle of the left side, going up (clockwise on screen);
   *  mark = path lengths at the start/end of the top straight and of the bottom straight. Cached per size. */
  let trk = null;
  function track(W, H, x0, x1, y0, y1, rc) {
    const key = [W, H, x0, x1, y0, y1, rc].join(","); if (trk && trk.key === key) return trk;
    const pts = [], yM = (y0 + y1) / 2, arc = (cx, cy, a0, a1) => { for (let i = 1; i <= 16; i++) { const a = lerp(a0, a1, i / 16); pts.push([cx + Math.cos(a) * rc, cy + Math.sin(a) * rc]); } };
    pts.push([x0, yM]); pts.push([x0, y0 + rc]); arc(x0 + rc, y0 + rc, Math.PI, Math.PI * 1.5); const iTA = pts.length - 1;
    pts.push([x1 - rc, y0]); const iTB = pts.length - 1; arc(x1 - rc, y0 + rc, -Math.PI / 2, 0); pts.push([x1, y1 - rc]); arc(x1 - rc, y1 - rc, 0, Math.PI / 2); const iBA = pts.length - 1;
    pts.push([x0 + rc, y1]); const iBB = pts.length - 1; arc(x0 + rc, y1 - rc, Math.PI / 2, Math.PI); pts.push([x0, yM]);
    const L = [0]; for (let i = 1; i < pts.length; i++) L.push(L[i - 1] + Math.hypot(pts[i][0] - pts[i - 1][0], pts[i][1] - pts[i - 1][1]));
    trk = { key, pts, L, len: L[L.length - 1], mark: [L[iTA], L[iTB], L[iBA], L[iBB]] }; return trk;
  }
  /** point at path length d: [x, y, nx, ny] (n = unit normal) */
  function at(P, d) {
    d = clamp(d, 0, P.len - 1e-6); let lo = 0, hi = P.L.length - 1; while (hi - lo > 1) { const m = (lo + hi) >> 1; if (P.L[m] <= d) lo = m; else hi = m; }
    const a = P.pts[lo], b = P.pts[hi], sl = P.L[hi] - P.L[lo] || 1, u = (d - P.L[lo]) / sl, tx = (b[0] - a[0]) / sl, ty = (b[1] - a[1]) / sl;
    return [lerp(a[0], b[0], u), lerp(a[1], b[1], u), -ty, tx];
  }
  const parts = [], flashes = [];
  let spawnAcc = 0;
  const walk = []; for (let i = 0; i < 46; i++) walk.push({ x: 0, y: 0, n: 0, out: -1, life: 0 });

  WT.chapter("economy", {
    level: 1, num: "Lesson 1", title: "The neutron economy", short: "Neutron economy",
    html: `
<div class="step">
  <h3>A thousand neutrons</h3>
  <p>Follow 1000 fast neutrons through one generation. A few cause extra fissions, some leak out, some are caught on the way, and the rest split uranium-235 to make the next thousand. Six factors multiply to <i>k</i> = <i>η f p ε P</i><sub>FNL</sub> <i>P</i><sub>TNL</sub>.</p>
</div>
<div class="step">
  <h3>Enrichment</h3>
  <p>More uranium-235 in the fuel means more neutrons are absorbed where they cause fission. With natural uranium (0.7 %) and ordinary water, <i>k</i> never reaches 1.</p>
  <div class="ctl"><label for="eco-e">Uranium-235 (%)</label><input id="eco-e" type="range" data-bind="enr" min="0.7" max="5" step="0.1" value="3"><output data-show="enr" data-fmt="1"></output></div>
</div>
<div class="step">
  <h3>Water between the rods</h3>
  <p>Too little water and slowing neutrons are caught by uranium-238; too much and the water itself absorbs them. There is a best ratio, and water reactors are built a little below it.</p>
  <div class="ctl"><label for="eco-m">Water per fuel (× typical)</label><input id="eco-m" type="range" data-bind="m" min="0.3" max="4" step="0.05" value="1"><output data-show="m" data-fmt="2"></output></div>
</div>
<div class="step">
  <h3>Size</h3>
  <p>Neutrons born near the surface can escape. A small core leaks too many; a bigger one keeps them. Find the size where <i>k</i> crosses 1.</p>
  <div class="ctl"><label for="eco-s">Core size (× typical)</label><input id="eco-s" type="range" data-bind="s" min="0.3" max="2" step="0.05" value="0.6"><output data-show="s" data-fmt="2"></output></div>
</div>`,
    setup(S) { S.set("enr", 3); S.set("m", 1); S.set("s", 1); },
    steps: [
      (S) => { const n = SHOT(); S.to("enr", 3, n); S.to("m", 1, n); S.to("s", 1, n); },
      (S) => { const n = SHOT(); S.to("enr", n ? 1.5 : 3, n); S.to("m", 1, n); S.to("s", 1, n); },
      (S) => { const n = SHOT(); S.to("enr", 3, n); S.to("m", n ? 2 : 1, n); S.to("s", 1, n); },
      (S) => { const n = SHOT(); S.to("enr", 3, n); S.to("m", 1, n); S.to("s", 0.6, n); },
    ],
    frame(g, S, dt) {
      const { W, H, c, ctx } = g, phone = W < 600, fs = phone ? 11 : 13, snap = document.body.classList.contains("shot"), st = Math.max(0, S.step);
      const F = factors(S.enr, S.m, S.s);
      let drag = null;
      // ---------- the loop: a rounded track, the fuel (U-235) on its left side ----------
      const yT = H * (phone ? 0.25 : 0.15), yB = H * (phone ? 0.6 : 0.72), xL0 = W * (phone ? 0.09 : 0.1), xR0 = W * 0.95, yM = (yT + yB) / 2;
      const rc = Math.min((yB - yT) / 2 * 0.9, W * 0.12);
      const P = track(W, H, xL0, xR0, yT, yB, rc), TOT = P.len, pos = (d) => at(P, d);
      const topA = P.mark[0], topB = P.mark[1], botA = P.mark[2], botB = P.mark[3]; // top straight (left->right), bottom straight (right->left)
      const D = { eps: lerp(topA, topB, 0.1), fnl: lerp(topA, topB, 0.5), p: lerp(topA, topB, 0.88), tnl: lerp(botA, botB, 0.14), f: lerp(botA, botB, 0.6), fuel: TOT - 0.5 };
      // neutron numbers per 1000 starting
      const n1 = 1000 * F.eps, lf = n1 * (1 - F.fnl), n2 = n1 - lf, lr = n2 * (1 - F.p), n3 = n2 - lr, lt = n3 * (1 - F.tnl), n4 = n3 - lt, la = n4 * (1 - F.f), n5 = n4 - la, nxt = n5 * F.eta;
      const nAt = (d) => (d < D.eps ? 1000 : d < D.fnl ? n1 : d < D.p ? n2 : d < D.tnl ? n3 : d < D.f ? n4 : n5);
      const temp = (d) => smooth(topB, botA, d); // 0 fast .. 1 thermal (slowing down on the right side)
      // the band: width ~ neutrons left, warm (fast) to blue (slow)
      const NS = 140;
      for (let i = 0; i < NS; i++) { const d0 = TOT * i / NS, d1 = TOT * (i + 1) / NS, a = pos(d0), b = pos(d1), t = temp(d0);
        ctx.save(); ctx.globalAlpha = 0.16; ctx.strokeStyle = t > 0.5 ? c.cool : c.warm; ctx.lineWidth = Math.max(2, (phone ? 20 : 30) * nAt(d0) / 1050); ctx.lineCap = "butt"; ctx.beginPath(); ctx.moveTo(a[0], a[1]); ctx.lineTo(b[0], b[1]); ctx.stroke(); ctx.restore(); }
      // ---------- absorbers inside the loop: U-238 under the top row, water over the bottom row ----------
      const NR = Math.max(9, Math.min(phone ? 12 : 19, rc * 0.24)), inY = phone ? 26 : 40;
      const ABS = { eps: [pos(D.eps)[0], yT + inY], p: [pos(D.p)[0], yT + inY], f: [pos(D.f)[0], yB - inY] };
      for (const k of ["eps", "p", "f"]) { const [x, y] = ABS[k], hit = clamp(1 - (S.time - (hits[k] || -9)) / 0.5, 0, 1);
        if (hit > 0) g.glow(x, y, NR * (2 + 2 * hit), k === "eps" ? c.photon : c.proton, 0.5 * hit);
        if (k === "f") { g.ball(x, y, NR * 0.75, c.cool, 0.9); g.ball(x - NR * 0.75, y - NR * 0.45, NR * 0.42, c.soft, 0.9); g.ball(x + NR * 0.75, y - NR * 0.45, NR * 0.42, c.soft, 0.9); }
        else g.nucleus(x, y, NR * (1 + 0.12 * hit), { N: 30, Z: 12, seed: k === "p" ? 21 : 23, t: S.time, jiggle: 0.4 + hit }); }
      // ---------- particles ----------
      const fateOf = () => { const u = r(); let q = 1 - F.fnl; if (u < q) return "fnl"; q += F.fnl * (1 - F.p); if (u < q) return "p"; q += F.fnl * F.p * (1 - F.tnl); if (u < q) return "tnl"; q += F.fnl * F.p * F.tnl * (1 - F.f); if (u < q) return "f"; return "fuel"; };
      if (snap && !parts.length) { for (let i = 0; i < 260; i++) { const d = r() * TOT, fate = fateOf(); if (D[fate] > d) parts.push({ d, fate, out: -1, o: r() * 2 - 1 }); } }
      spawnAcc += snap ? 0 : dt * 26;
      while (spawnAcc > 1 && parts.length < 380) { spawnAcc -= 1; parts.push({ d: 0, fate: fateOf(), out: -1, o: r() * 2 - 1 }); if (r() < F.eps - 1) { parts.push({ d: D.eps, fate: fateOf(), out: -1, o: r() * 2 - 1, born: 1 }); hits.eps = S.time; } }
      const nr = phone ? 2.4 : 3;
      for (let i = parts.length - 1; i >= 0; i--) {
        const q = parts[i];
        if (q.out < 0) {
          const t = temp(q.d), v = lerp(phone ? 150 : 230, phone ? 55 : 80, t);
          q.d += v * (snap ? 0 : dt);
          if (q.d >= D[q.fate]) { if (q.fate === "fuel") { flashes.push({ t: S.time }); parts.splice(i, 1); continue; } q.out = 0; q.d = D[q.fate]; q.vx = (r() - 0.5) * 80; }
          const [x, y, nx, ny] = pos(q.d), w = (phone ? 8 : 12) * nAt(q.d) / 1050, px = x + nx * q.o * w, py = y + ny * q.o * w;
          if (t < 0.5 && !phone) g.line(px - 7, py, px, py, c.warm, 1.6, 0.3); // fast ones leave a short streak
          g.ball(px, py, nr, t > 0.5 ? c.neutron : c.warm, 0.95);
          if (q.born && q.d < D.eps + 40) g.glow(px, py, 9, c.photon, 0.5);
        } else {
          q.out += snap ? 0 : dt; const [x, y] = pos(q.d);
          if (q.fate === "fnl" || q.fate === "tnl") { // leaks: fly out of the picture
            const dir = q.fate === "fnl" ? -1 : 1, sp = q.fate === "fnl" ? 320 : 170, ex = x + q.vx * q.out, ey = y + dir * sp * q.out, col = q.fate === "fnl" ? c.warm : c.neutron;
            if (ey < -10 || ey > H + 10) { parts.splice(i, 1); continue; }
            g.line(ex, ey, ex - q.vx * 0.05, ey - dir * sp * 0.05, col, 1.6, 0.5); g.ball(ex, ey, nr, col, 0.9);
          } else { // captures: swallowed by the absorber with a flash
            const [ax, ay] = ABS[q.fate], u = q.out / 0.35;
            if (u >= 1) { hits[q.fate] = S.time; parts.splice(i, 1); continue; }
            const e = u * u; g.ball(lerp(x, ax, e), lerp(y, ay, e), nr * (1 - 0.4 * u), q.fate === "p" ? c.warm : c.neutron, 0.95);
          }
        }
      }
      // ---------- the fuel: U-235 on the left side, flashing as the slow neutrons split it ----------
      const fx = xL0, fR = Math.min(rc * 0.42, phone ? 22 : 34);
      let fl = snap ? 0.6 : 0; for (let i = flashes.length - 1; i >= 0; i--) { const a = S.time - flashes[i].t; if (a > 0.5 || a < 0) { flashes.splice(i, 1); continue; } fl = Math.max(fl, 1 - a / 0.5); }
      while (flashes.length > 30) flashes.shift();
      g.glow(fx, yM, fR * (2.2 + 1.2 * fl), c.fission, 0.25 + 0.35 * fl);
      g.nucleus(fx, yM, fR, { N: 44, Z: 18, seed: 3, t: S.time, jiggle: 0.5 + 1.5 * fl });
      // one generation every 1.6 s: a ring from the fuel, bright when the chain grows, faint when it dies away
      if (!snap && S.time - (gen.t || 0) > 1.6) gen.t = S.time;
      { const a = snap ? 0.35 : (S.time - (gen.t || 0)) / 1.2; if (a < 1) g.ring(fx, yM, fR * (1.2 + 5 * a), F.k > 1.004 ? c.warm : F.k < 0.996 ? c.cool : c.fission, 2.5 * (1 - a), clamp(0.3 + 3 * (F.k - 0.9), 0.1, 1) * (1 - a)); }
      // ---------- station labels (outside the loop) ----------
      const L = (s, x, y, o) => g.label(s, x, y, Object.assign({ size: fs - 1, bg: true }, o));
      const fmtN = (v) => Math.round(v).toString();
      const lab = [
        ["eps", "fast fission", `+${fmtN(n1 - 1000)}`, `ε ${F.eps.toFixed(3)}`, -1, c.photon, 0],
        ["fnl", phone ? "fast leak" : "leaks out, fast", `−${fmtN(lf)}`, `P fast ${F.fnl.toFixed(3)}`, -1, c.warm, 3],
        ["p", phone ? "U-238 catches" : "caught by U-238", `−${fmtN(lr)}`, `p ${F.p.toFixed(3)}`, -1, c.proton, 2],
        ["tnl", phone ? "slow leak" : "leaks out, slow", `−${fmtN(lt)}`, `P slow ${F.tnl.toFixed(3)}`, 1, c.neutron, 3],
        ["f", phone ? "water, steel…" : "water, steel, boron", `−${fmtN(la)}`, `f ${F.f.toFixed(3)}`, 1, c.proton, 2],
      ];
      for (const [key, name, num, fac, dir, col, hl] of lab) {
        const [x, y] = pos(D[key]), on = st === 0 || st === hl || (st === 1 && key === "f") || (st === 2 && key === "p") ? 1 : 0.55;
        const y1 = y + dir * (phone ? 26 : 34), y2 = y1 + dir * (fs + 5), y3 = y2 + dir * (fs + 3);
        L(num, x, y1, { color: col, size: fs + 1, weight: 700, alpha: on });
        L(name, x, y2, { color: c.ink, alpha: on });
        if (!(phone && st === 2 && dir > 0)) L(fac, x, y3, { color: c.soft, size: fs - 2, alpha: on, bg: false });
      }
      L(phone ? "slowing" : "slowing down", xR0 - rc * 0.55, yM, { color: c.soft, bg: false });
      if (!phone) L(`${fmtN(n5)} split U-235`, fx + fR + 8, yM + fR * 0.6 + 10, { color: c.fission, weight: 700, align: "left", bg: false });
      L(`× η ${F.eta.toFixed(2)}`, fx + fR + 8, yM - fR * 0.6 - 10, { color: c.fission, weight: 700, align: "left", bg: false });
      if (!phone) L("U-238", ABS.p[0], ABS.p[1] + NR + 12, { color: c.soft, size: fs - 2, bg: false });
      // ---------- k inside the loop ----------
      const k = F.k, crit = Math.abs(k - 1) < 0.004, kc = crit ? c.fission : k > 1 ? c.warm : c.cool;
      const kx = st === 3 && !phone ? W * 0.4 : W * 0.52 + (phone ? 10 : 0), ky = st === 2 && !phone ? yT + (yB - yT) * 0.32 : yM - (phone ? 12 : 2);
      g.glow(kx, ky, phone ? 50 : 90, kc, 0.18 + 0.06 * Math.sin(S.time * 2));
      g.label(phone ? `next: ${fmtN(nxt)}` : `next generation: ${fmtN(nxt)}`, kx, ky - (phone ? 20 : 28), { color: c.soft, size: fs });
      g.label(`k = ${k.toFixed(3)}`, kx, ky + 4, { color: kc, size: phone ? 20 : 30, weight: 700, serif: true });
      g.label(crit ? "critical: steady" : k > 1 ? "grows" : "dies away", kx, ky + (phone ? 24 : 34), { color: kc, size: fs, weight: 600 });
      // step 3: k against the water-to-fuel ratio (the shape is the idea); drag along it
      if (st === 2) {
        const cx0 = phone ? W * 0.12 : W * 0.24, cx1 = phone ? W * 0.88 : W * 0.8, cy1 = phone ? H * 0.9 : yB - inY - NR - 30, cy0 = cy1 - H * (phone ? 0.1 : 0.14), M0 = 0.3, M1 = 4;
        const X = (m) => lerp(cx0, cx1, (Math.log(m) - Math.log(M0)) / (Math.log(M1) - Math.log(M0))), Yk = (kk) => lerp(cy1, cy0, (kk - 0.7) / 0.4);
        const pts = []; let best = 0, bm = 1; for (let i = 0; i <= 80; i++) { const m = M0 * (M1 / M0) ** (i / 80), kk = factors(S.enr, m, S.s).k; pts.push([X(m), Yk(kk)]); if (kk > best) { best = kk; bm = m; } }
        g.clip(cx0, cy0 - 20, cx1 - cx0, cy1 - cy0 + 20); g.ground(pts, c.accent, cy1 - cy0, 0.22); g.ctx.restore(); g.poly(pts, c.accent, 2, 0.9);
        g.line(cx0, Yk(1), cx1, Yk(1), c.soft, 1, 0.6, [3, 4]); g.label("k = 1", cx1 + 4, Yk(1), { color: c.soft, size: fs - 2, align: "left" });
        g.glow(X(S.m), Yk(F.k), 18, c.accent, 0.35 + 0.15 * Math.sin(S.time * 4)); g.ball(X(S.m), Yk(F.k), 6, c.accent);
        if (!phone) g.label(`best ≈ ${bm.toFixed(1)}×`, X(bm), Yk(best) - 14, { color: c.accent, size: fs - 2, weight: 600 });
        g.label("less water", cx0, cy1 + 10, { color: c.soft, size: fs - 2, align: "left" }); g.label("more water", cx1, cy1 + 10, { color: c.soft, size: fs - 2, align: "right" });
        drag = { x0: cx0, x1: cx1, y0: cy0 - 24, y1: cy1 + 18, set: (x) => M0 * (M1 / M0) ** clamp((x - cx0) / (cx1 - cx0), 0, 1), key: "m", id: "eco-m" };
      }
      // step 4 (wide screens): a core of that size inside the loop, neutrons wandering until absorbed or out through the surface; drag its edge
      if (st === 3 && !phone) {
        const ccx = W * 0.68, ccy = yM, Rmax = (yB - yT) / 2 - inY - NR - 6, Rc = Rmax * S.s / 2, stp = Rmax * 0.09;
        g.glow(ccx, ccy, Rc * 1.4, c.warm, 0.2);
        ctx.save(); const cg = ctx.createRadialGradient(ccx - Rc * 0.3, ccy - Rc * 0.3, Rc * 0.1, ccx, ccy, Rc); cg.addColorStop(0, g.rgba(c.warm, 0.35)); cg.addColorStop(1, g.rgba(c.cool, 0.12)); ctx.fillStyle = cg; ctx.beginPath(); ctx.arc(ccx, ccy, Rc, 0, TAU); ctx.fill(); ctx.restore();
        g.ring(ccx, ccy, Rc, c.ink, 2, 0.5); g.glow(ccx + Rc, ccy, 12, c.accent, 0.45 + 0.2 * Math.sin(S.time * 4)); g.dot(ccx + Rc, ccy, 4, c.accent);
        for (const q of walk) {
          if (q.out >= 0) { q.out += dt; const a = q.out / 0.6; if (a >= 1) { q.out = -1; q.n = 0; } else { const d = Math.hypot(q.x, q.y) || 1; g.ball(ccx + q.x + q.x / d * a * 40, ccy + q.y + q.y / d * a * 40, 2.6, c.warm, 1 - a); } continue; }
          if (q.n <= 0) { const a = r() * TAU, rr = Rc * Math.sqrt(r()); q.x = Math.cos(a) * rr; q.y = Math.sin(a) * rr; q.n = 1; q.life = 10 + Math.floor(r() * 30); q.acc = r() * 0.12; }
          q.acc += snap ? 0.12 : dt; if (q.acc > 0.12) { q.acc = 0; const a = r() * TAU; q.x += Math.cos(a) * stp; q.y += Math.sin(a) * stp; q.n++; if (q.n > q.life) q.n = 0; if (Math.hypot(q.x, q.y) > Rc) q.out = 0; }
          g.ball(ccx + q.x, ccy + q.y, 2.6, c.neutron, 0.9);
        }
        g.label(`${(100 * (1 - F.fnl * F.tnl)).toFixed(0)} % leak out`, ccx, ccy + Rc + 16, { color: c.soft, size: fs, bg: true });
        drag = { cx: ccx, cy: ccy, R: Rc, set: (x, y) => clamp(Math.hypot(x - ccx, y - ccy) / Rmax * 2, 0.3, 2), key: "s", id: "eco-s" };
      }
      const over = (x, y) => drag && (drag.cx != null ? Math.abs(Math.hypot(x - drag.cx, y - drag.cy) - drag.R) < 26 : x > drag.x0 - 10 && x < drag.x1 + 10 && y > drag.y0 && y < drag.y1);
      WT.grab(ctx.canvas, {
        down(x, y) { if (!over(x, y)) return false; this.move(x, y); return true; },
        move(x, y) { if (!drag) return; const v = drag.set(x, y); S.set(drag.key, v); const i = document.getElementById(drag.id); if (i) i.value = v; },
        hover(x, y) { ctx.canvas.style.cursor = over(x, y) ? (drag.cx != null ? "nwse-resize" : "ew-resize") : "default"; },
      });
      // ---------- bottom line ----------
      const by = H * (phone ? 0.93 : 0.94);
      const txt = phone ? `${F.eta.toFixed(2)} × ${F.f.toFixed(2)} × ${F.p.toFixed(2)} × ${F.eps.toFixed(2)} × ${F.fnl.toFixed(2)} × ${F.tnl.toFixed(2)}` : `k = η ${F.eta.toFixed(2)} × f ${F.f.toFixed(2)} × p ${F.p.toFixed(2)} × ε ${F.eps.toFixed(2)} × P ${F.fnl.toFixed(2)} × P ${F.tnl.toFixed(2)}`;
      if (!(phone && st === 2)) g.label(txt, W / 2, by, { color: c.ink, size: fs, weight: 600, serif: true });
      g.label(phone ? "textbook set (D&H); trends illustrative" : "factors: textbook set (Duderstadt & Hamilton) at 3 %; slider trends illustrative", W - 6, H - 10, { color: c.faint, size: 10, align: "right" });
    },
  });
})();
