/* Reactor stability and feedback. One model in every step (S.mode only changes what is shown and which coefficients the
 * reader sets): point kinetics with one delayed-neutron group plus a lumped fuel and a lumped coolant/moderator node,
 *   dn/dt  = (rho - beta)/Lambda n + lambda C,   dC/dt = beta/Lambda n - lambda C          (n = power / nominal)
 *   Cf dTf/dt = n - hf (Tf - Tm),   Cm dTm/dt = hf (Tf - Tm) - hm (Tm - Tin)
 *   rho = rho_ext + aD (Tf - Tf0) + aM (Tm - Tm0)
 * beta = 0.0065, lambda = 0.0767 /s, Lambda = 1e-4 s (as in the "critical" lesson); hf = 1/600 (fuel 600 K above the
 * coolant at full power), hm = 1/15 (coolant 15 K above inlet on average at full power), fuel time constant Cf/hf = 4 s,
 * coolant 8 s (illustrative lumped values with LWR-like sizes). Starts in equilibrium at 60 % power; explicit Euler,
 * 2 ms steps, real time. Coefficients: Doppler aD -1..-5 pcm/K (LWR fuel ~ -2 to -4 pcm/K), moderator/coolant aM
 * -60..+150 pcm/K (PWR moderator temperature coefficient roughly -10 to -60 pcm/K at normal boron; the positive end
 * stands in for a positive void/coolant effect, illustrative). Power coefficient shown = aD x 600 K + aM x 15 K per
 * 100 % power. Above 300 % the run stops ("protection would shut it down"). */
(function () {
  const { TAU, clamp, lerp, smooth, rng } = WT.util;
  const BETA = 0.0065, LAM = 0.0767, LAMBDA = 1e-4, HF = 1 / 600, HM = 1 / 15, CF = 4 * HF, CM = 8 * HM, N0 = 0.6, WIN = 60, DT = 0.002;
  const sim = { n: N0, C: 0, dTf: 0, dTm: 0, t: 0, rx: 0, hist: [], halt: false, ins: -1 };
  function reset() { sim.n = N0; sim.C = BETA * N0 / (LAM * LAMBDA); sim.dTf = 0; sim.dTm = 0; sim.t = 0; sim.rx = 0; sim.hist.length = 0; sim.halt = false; sim.ins = -1; }
  function rhoOf(S) { return sim.rx + S.aD * 1e-5 * sim.dTf + S.aM * 1e-5 * sim.dTm; }
  function advance(S, sec) {
    if (sim.halt) return;
    const n = Math.ceil(sec / DT);
    for (let i = 0; i < n; i++) {
      const rho = rhoOf(S), q = sim.n;
      const dn = ((rho - BETA) / LAMBDA) * q + LAM * sim.C, dC = (BETA / LAMBDA) * q - LAM * sim.C;
      // temperatures as deviations from the starting equilibrium (Tf0 - Tm0 = 600 N0, Tm0 - Tin = 15 N0)
      const qf = HF * (sim.dTf - sim.dTm), dTf = ((q - N0) - qf) / CF, dTm = (qf - HM * sim.dTm) / CM;
      sim.n = Math.max(0, q + dn * DT); sim.C += dC * DT; sim.dTf += dTf * DT; sim.dTm += dTm * DT; sim.t += DT;
      if (!sim.hist.length || sim.t - sim.hist[sim.hist.length - 1][0] >= 0.1) { sim.hist.push([sim.t, sim.n, rho]); if (sim.hist.length > WIN * 10 + 20) sim.hist.shift(); }
      if (sim.n > 3) { sim.halt = true; break; }
    }
  }
  const geo = {}, flash = [];
  /** The reactor core at the top of the loop: fuel rods glow with power, their colour follows the fuel temperature. */
  function drawCore(g, S, x, y, w, h, phone) {
    const { c, ctx } = g, n = sim.n, hot = clamp(sim.dTf / 600, 0, 1.4), gl = clamp(n / 1.2, 0.1, 1.6), nR = phone ? 6 : 8;
    g.glow(x, y, w * 0.9, c.warm, 0.18 + 0.3 * clamp(gl, 0, 1));
    ctx.save(); const wg = ctx.createLinearGradient(0, y - h / 2, 0, y + h / 2); wg.addColorStop(0, g.rgba(c.cool, 0.08)); wg.addColorStop(1, g.rgba(c.cool, 0.22));
    ctx.fillStyle = wg; ctx.strokeStyle = g.rgba(c.soft, 0.55); ctx.lineWidth = 1.4; ctx.beginPath(); if (ctx.roundRect) ctx.roundRect(x - w / 2, y - h / 2, w, h, h * 0.22); else ctx.rect(x - w / 2, y - h / 2, w, h); ctx.fill(); ctx.stroke(); ctx.restore();
    const col = hot > 0.6 ? c.proton : c.warm;
    for (let i = 0; i < nR; i++) {
      const rx = lerp(x - w * 0.38, x + w * 0.38, (i + 0.5) / nR), fw = w * 0.045, fv = clamp(gl * (0.85 + 0.15 * Math.sin(S.time * 7 + i * 1.9)), 0, 1.3);
      ctx.save(); ctx.fillStyle = g.rgba(col, 0.35 + 0.5 * clamp(fv, 0, 1)); ctx.fillRect(rx - fw / 2, y - h * 0.34, fw, h * 0.68); ctx.restore();
      g.glow(rx, y, fw * 4, hot > 1 ? "#ffffff" : c.photon, 0.15 * fv);
    }
    // neutrons and fission flashes, both proportional to power
    const q = rng(5), nn = Math.round(clamp(18 * Math.sqrt(n), 0, 50));
    for (let i = 0; i < nn; i++) { const ux = (q() + S.time * (0.05 + 0.1 * q())) % 1, uy = 0.5 + 0.38 * Math.sin(S.time * (0.8 + q()) + i * 2.3); g.dot(lerp(x - w * 0.44, x + w * 0.44, ux), lerp(y - h / 2, y + h / 2, uy), 1.8, c.neutron, 0.85); }
    if (Math.random() < 0.25 * n) flash.push({ x: lerp(x - w * 0.36, x + w * 0.36, Math.random()), y: lerp(y - h * 0.3, y + h * 0.3, Math.random()), t: S.time });
    for (let i = flash.length - 1; i >= 0; i--) { const f = flash[i], a = S.time - f.t; if (a > 0.4) { flash.splice(i, 1); continue; } g.glow(f.x, f.y, 6 + 26 * a, c.fission, 0.7 * (1 - a / 0.4)); }
    while (flash.length > 30) flash.shift();
    // a burst when reactivity was just added
    const since = sim.t - sim.ins; if (sim.ins >= 0 && since < 0.8) { g.ring(x, y, w * (0.5 + since), c.photon, 2.5 * (1 - since / 0.8), 0.9 * (1 - since / 0.8)); g.glow(x, y, w * 0.8, "#ffffff", 0.4 * (1 - since / 0.8)); }
  }
  const fl = []; const r = rng(3); for (let i = 0; i < 60; i++) fl.push(r());

  WT.chapter("feedback", {
    level: 2, num: "Lesson 1", title: "Reactor stability and feedback", short: "Feedback",
    html: `
<div class="step">
  <h3>A loop: power, heat, reactivity</h3>
  <p>More power heats the fuel and the water, and their temperatures change the reactivity <i>ρ</i>, which sets the power. Add a step of reactivity and watch the signal travel round the loop. With negative coefficients it pushes back.</p>
  <div class="ctl"><label for="fb-r">Reactivity step (pcm)</label><input id="fb-r" type="range" data-bind="rs" data-instant min="50" max="300" step="10" value="200"><output data-show="rs" data-fmt="0"></output></div>
  <div class="btns"><button class="btn" data-act="fbIns">Insert</button> <button class="btn ghost" data-act="fbRes">Reset</button></div>
</div>
<div class="step">
  <h3>Doppler: the fast brake</h3>
  <p>Hotter fuel catches more neutrons in uranium-238 without fission (<a href="#doppler">Doppler broadening</a>). Fuel heats within seconds, so this brake acts first, and in water reactors it is always negative. Here it is the only feedback.</p>
  <div class="ctl"><label for="fb-d">Doppler coefficient (pcm/K)</label><input id="fb-d" type="range" data-bind="aD" data-instant min="-5" max="-1" step="0.1" value="-2.5"><output data-show="aD" data-fmt="1"></output></div>
  <div class="btns"><button class="btn" data-act="fbIns">Insert</button> <button class="btn ghost" data-act="fbRes">Reset</button></div>
</div>
<div class="step">
  <h3>The moderator joins</h3>
  <p>Warmer water is less dense, so it slows neutrons less well. In a pressurised water reactor at normal boron levels this makes the moderator coefficient negative too: a second, slower brake, and the power settles lower.</p>
  <div class="ctl"><label for="fb-m">Moderator coefficient (pcm/K)</label><input id="fb-m" type="range" data-bind="aM" data-instant min="-60" max="0" step="1" value="-30"><output data-show="aM" data-fmt="0"></output></div>
  <div class="btns"><button class="btn" data-act="fbIns">Insert</button> <button class="btn ghost" data-act="fbRes">Reset</button></div>
</div>
<div class="step">
  <h3>When feedback is positive</h3>
  <p>If the coolant term is positive and outweighs Doppler, more power means more reactivity and the power runs away. Water reactors are designed with negative coefficients; some designs, such as the RBMK at low power, could have a positive void coefficient.</p>
  <div class="ctl"><label for="fb-c">Coolant coefficient (pcm/K)</label><input id="fb-c" type="range" data-bind="aM" data-instant min="-60" max="150" step="5" value="150"><output data-show="aM" data-fmt="0"></output></div>
  <div class="btns"><button class="btn" data-act="fbIns">Insert</button> <button class="btn ghost" data-act="fbRes">Reset</button></div>
</div>`,
    setup(S) {
      S.set("mode", "loop"); S.set("rs", 200); S.set("aD", -2.5); S.set("aM", -30); reset();
      S.on("fbIns", () => { if (sim.halt) reset(); sim.rx += S.rs * 1e-5; sim.ins = sim.t; });
      S.on("fbRes", () => reset());
    },
    steps: [
      (S) => { S.set("mode", "loop"); S.set("aD", -2.5); S.set("aM", -30); reset(); },
      (S) => { S.set("mode", "dop"); S.set("aD", -2.5); S.set("aM", 0); S.set("rs", 200); reset(); },
      (S) => { S.set("mode", "mod"); S.set("aD", -2.5); S.set("aM", -30); S.set("rs", 200); reset(); },
      (S) => { S.set("mode", "pos"); S.set("aD", -2.5); S.set("aM", 150); S.set("rs", 150); reset(); },
    ],
    frame(g, S, dt) {
      const { W, H, c, ctx } = g, phone = W < 600, fs = phone ? 11 : 13, snap = document.body.classList.contains("shot");
      if (!S.grabbed) { S.grabbed = true; const cv = g.ctx.canvas; const inC = (x, y) => geo.core && x > geo.core.x - 10 && x < geo.core.x + geo.core.w + 10 && y > geo.core.y - 10 && y < geo.core.y + geo.core.h + 10;
        WT.grab(cv, { down(x, y) { if (inC(x, y)) S.handlers.fbIns(); return false; }, hover(x, y) { cv.style.cursor = inC(x, y) ? "pointer" : ""; } }); }
      if (snap && sim.t === 0) { advance(S, 4); sim.rx += S.rs * 1e-5; sim.ins = sim.t; advance(S, S.mode === "pos" ? 45 : 36); }
      else if (!snap && dt > 0) { advance(S, dt); if (sim.ins < 0 && sim.t > 3 && !S.auto) { /* idle */ } }
      if (!snap && sim.t > 2.5 && sim.ins < 0 && S.step === 0 && !S.fired) { S.fired = true; sim.rx += S.rs * 1e-5; sim.ins = sim.t; }
      const rho = rhoOf(S), fD = S.aD * 1e-5 * sim.dTf, fM = S.aM * 1e-5 * sim.dTm;
      // ---------- the loop diagram ----------
      const cx = phone ? W * 0.5 : W * 0.25, cy = phone ? H * 0.33 : H * 0.34, rx = phone ? W * 0.33 : W * 0.17, ry = phone ? H * 0.13 : H * 0.2;
      const NP = [cx, cy - ry], NF = [cx + rx, cy], NM = [cx, cy + ry], NR = [cx - rx, cy];
      const nr = phone ? 17 : 22, coreW = phone ? W * 0.26 : W * 0.3, coreH = coreW * 0.62, rP = coreH * 0.62;
      geo.core = { x: NP[0] - coreW / 2, y: NP[1] - coreH / 2, w: coreW, h: coreH };
      const pcm = (v) => `${v >= 0 ? "+" : "−"}${Math.abs(v * 1e5).toFixed(0)} pcm`;
      const arrows = [
        [NP, NF, sim.n - N0, phone ? "heat" : "heat", c.warm, 1],
        [NF, NM, sim.dTf / 600, phone ? "heat" : "heats water", c.warm, S.mode !== "dop" ? 1 : 0.35],
        [NM, NR, fM * 30, S.mode === "pos" ? "α_C" : "α_M", S.aM > 0 ? c.proton : c.cool, S.mode === "dop" ? 0.25 : 1],
        [NF, NR, fD * 30, "α_D", c.cool, 1],
        [NR, NP, rho * 30, phone ? "chain" : "chain reaction", rho >= 0 ? c.warm : c.cool, 1],
      ];
      arrows.forEach(([a, b, sig, lab, col, al], k) => {
        const dx = b[0] - a[0], dy = b[1] - a[1], L = Math.hypot(dx, dy), ux = dx / L, uy = dy / L;
        const ra = a === NP ? rP : nr, rb = b === NP ? rP : nr;
        const x0 = a[0] + ux * (ra + 6), y0 = a[1] + uy * (ra + 6), x1 = b[0] - ux * (rb + 8), y1 = b[1] - uy * (rb + 8);
        g.arrow(x0, y0, x1, y1, col, 1.6, 0.3 * al, 8);
        // the signal as flowing light: comets whose speed and brightness follow the size of the change
        const sp = clamp(Math.abs(sig) * 3, 0, 1.6), br = al * clamp(0.15 + sp * 1.5, 0.15, 1);
        for (let i = 0; i < 4; i++) {
          const f = (fl[k * 6 + i] + S.time * 0.22 * (0.25 + sp)) % 1, fx = lerp(x0, x1, f), fy = lerp(y0, y1, f);
          g.glow(fx, fy, 12 + 10 * sp, col, 0.55 * br);
          for (let t = 1; t <= 4; t++) { const ft = Math.max(0, f - t * 0.025); g.dot(lerp(x0, x1, ft), lerp(y0, y1, ft), 2.8 - t * 0.5, col, br * (1 - t * 0.22)); }
          g.dot(fx, fy, 3, "#ffffff", br * 0.8);
        }
        const mx = (x0 + x1) / 2 - uy * (phone ? 13 : 16), my = (y0 + y1) / 2 + ux * (phone ? 13 : 16) + (phone && k === 3 ? 26 : 0);
        const sign = k === 2 ? (S.aM > 0 ? " +" : S.aM < 0 ? " −" : " 0") : k === 3 ? " −" : "";
        if (!phone || k === 2 || k === 3) g.label(lab.replace("_", "") + sign, mx, my, { color: col, size: fs - 1, weight: 600, alpha: Math.max(0.5, al), bg: true });
      });
      // nodes
      drawCore(g, S, NP[0], NP[1], coreW, coreH, phone);
      g.ball(NF[0], NF[1], nr * 0.85, c.proton, 0.9); g.glow(NF[0], NF[1], nr * 2, c.proton, clamp(sim.dTf / 300, 0, 0.6));
      g.ball(NM[0], NM[1], nr * 0.85, c.cool, S.mode === "dop" ? 0.4 : 0.9); g.glow(NM[0], NM[1], nr * 2, c.cool, clamp(sim.dTm / 8, 0, 0.5));
      g.ball(NR[0], NR[1], nr * 0.85, rho >= 0 ? c.photon : c.neutron, 0.95);
      const lb = { size: fs, weight: 700, bg: true };
      g.label(`P ${(100 * sim.n).toFixed(0)} %`, NP[0], NP[1] - coreH / 2 - 12, Object.assign({ color: c.warm }, lb));
      g.label(phone ? `fuel ${sim.dTf >= 0 ? "+" : "−"}${Math.abs(sim.dTf).toFixed(0)} K` : `fuel ΔT ${sim.dTf >= 0 ? "+" : "−"}${Math.abs(sim.dTf).toFixed(0)} K`, NF[0] + (phone ? 0 : nr + 8), NF[1] + (phone ? nr + 14 : 0), Object.assign({ color: c.proton, align: phone ? "center" : "left" }, lb));
      g.label(phone ? `water ${sim.dTm >= 0 ? "+" : "−"}${Math.abs(sim.dTm).toFixed(1)} K` : `water ΔT ${sim.dTm >= 0 ? "+" : "−"}${Math.abs(sim.dTm).toFixed(1)} K`, NM[0], NM[1] + nr + 13, Object.assign({ color: c.cool, alpha: S.mode === "dop" ? 0.5 : 1 }, lb));
      g.label(`ρ ${pcm(rho)}`, NR[0] - (phone ? 0 : nr + 8), NR[1] + (phone ? nr + 14 : 0), Object.assign({ color: rho >= 0 ? c.photon : c.neutron, align: phone ? "center" : "right" }, lb));
      // formulas (desktop beside the loop, phone one line)
      if (!phone) {
        const fx = W * 0.56, fy = H * 0.12, fsty = { color: c.ink, size: fs + 1, serif: true, italic: true, align: "left" };
        g.label("ρ = ρext + αD ΔTf + αM ΔTm", fx, fy, fsty);
        g.label("C dT/dt = P − h (T − Tc)", fx, fy + 26, fsty);
        const coefs = [[c.cool, WT.trf("Doppler α_D = {a} pcm/K", S.aD.toFixed(1)).replace("_", "")], [S.aM > 0 ? c.proton : c.cool, WT.trf(S.mode === "pos" ? "coolant α_C = {a} pcm/K" : "moderator α_M = {a} pcm/K", S.aM.toFixed(0)).replace("_", "")]];
        coefs.forEach(([col, s], i) => g.label(s, fx, fy + 62 + i * 22, { color: col, size: fs, weight: 600, align: "left", raw: true, alpha: i === 1 && S.mode === "dop" ? 0.5 : 1 }));
        g.label(WT.trf("inserted ρ_ext = {a}", pcm(sim.rx)).replace("_", ""), fx, fy + 112, { color: c.soft, size: fs, align: "left", raw: true });
      }
      // ---------- power trace (landscape) ----------
      const x0 = W * (phone ? 0.12 : 0.08), x1 = W * 0.95, y0 = H * (phone ? 0.62 : 0.64), y1 = H * (phone ? 0.8 : 0.85), PMAX = 2;
      const tEnd = Math.max(WIN, sim.t), tS = tEnd - WIN, Xt = (t) => lerp(x0, x1, (t - tS) / WIN), Yp = (p) => lerp(y1, y0, clamp(p / PMAX, 0, 1.04));
      g.line(x0, y1, x1, y1, c.line, 1);
      [0.5, 1, 1.5, 2].forEach((p) => { g.line(x0, Yp(p), x1, Yp(p), c.line, 1, p === 1 ? 0.8 : 0.35, p === 1 ? null : [2, 5]); g.label(`${(100 * p).toFixed(0)} %`, x0 - 6, Yp(p), { color: c.faint, size: fs - 2, align: "right" }); });
      const pts = [], rp = [];
      for (const [t, n, rh] of sim.hist) if (t >= tS) { pts.push([Xt(t), Yp(n)]); rp.push([Xt(t), Yp(1 + rh / BETA)]); }
      if (pts.length > 1) { g.clip(x0, y0 - 20, x1 - x0 + 10, y1 - y0 + 20); g.ground(pts, c.warm, (y1 - y0) * 0.8, 0.3); ctx.restore(); g.poly(pts, c.warm, 2.4); const l = pts[pts.length - 1]; g.glow(l[0], l[1], 16, c.warm, 0.6); g.dot(l[0], l[1], 4.5, c.warm); }
      if (sim.ins >= tS && sim.ins >= 0) { const xi = Xt(sim.ins); g.line(xi, y0, xi, y1, c.photon, 1.2, 0.7, [3, 3]); g.label(WT.trf("+{a} pcm", Math.round(sim.rx * 1e5)), xi + 4, y0 + 8, { color: c.photon, size: fs - 1, align: "left", raw: true }); }
      g.label("power", x0, y0 - 12, { color: c.soft, size: fs - 1, align: "left" });
      g.label(phone ? "last 60 s →" : "last 60 seconds →", x1, y1 + 14, { color: c.soft, size: fs - 2, align: "right" });
      // ---------- verdict ----------
      const pc = S.aD * 600 + (S.mode === "dop" ? 0 : S.aM * 15);
      const rd = { color: c.ink, size: fs + 1, weight: 600, serif: true, raw: true };
      const vy = H * (phone ? 0.88 : 0.93);
      if (sim.halt) { g.label(WT.tr(phone ? "power ran away · protection would shut it down" : "power ran away · in a real plant the protection system would shut it down"), W * 0.5, vy, Object.assign({}, rd, { color: c.proton })); g.glow(W * 0.5, vy, 90, c.proton, 0.15); }
      else if (sim.ins < 0) g.label(WT.tr(phone ? "steady at 60 % · press Insert" : "steady at 60 % power · press Insert to add reactivity"), W * 0.5, vy, rd);
      else {
        const s = pc < 0 ? WT.trf(phone ? "power coefficient {a} pcm per 100 %: settles" : "power coefficient {a} pcm per 100 % power: self-stabilising", Math.round(pc)) : WT.trf(phone ? "power coefficient +{a} pcm per 100 %: runs away" : "power coefficient +{a} pcm per 100 % power: runs away", Math.round(pc));
        g.label(s, W * 0.5, vy, Object.assign({}, rd, { color: pc < 0 ? c.fission : c.proton }));
      }
      g.label("illustrative model", W - 6, H - 10, { color: c.faint, size: 10, align: "right" });
    },
  });
})();
