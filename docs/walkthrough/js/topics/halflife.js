/* Radioactivity and half-life. Scenes (S.mode):
 *   "live" = a sample of unstable nuclei; every frame each one pops with chance 1 - 2^(-dt/T) (no memory: the chance does not
 *            depend on how long it has already lived). T is an illustrative half-life in seconds of animation. The landscape
 *            under it is the count left (dots) and the expected N0 2^(-t/T) (ground). A tagged survivor shows that its chance to
 *            last one more half-life is still 1/2 however old it is.
 *   "real" = real half-lives on a log time axis (each cliff sits at its half-life); nucleus i survives while u_i < 2^(-t/T).
 *   "act"  = activity of one gram, A = (ln 2 / T) N_A / M, against log time: I-131 4.6e15 Bq/g, Cs-137 3.2e12, C-14 1.65e11,
 *            U-238 1.24e4 (computed below). Short half-life: high plateau, early cliff.
 * Half-lives (NNDC NuDat 3 / ENSDF): I-131 8.0252 d, Cs-137 30.08 y, C-14 5700 y, U-238 4.468e9 y. N_A = 6.02214e23 /mol;
 * molar masses taken as the mass numbers. The lamps' flicker rate is a log-scaled picture of the activity, not a count. */
(function () {
  const { TAU, clamp, lerp, smooth, rng } = WT.util;
  const DAY = 86400, YR = 365.25 * DAY, LN2 = Math.LN2, NA = 6.02214e23;
  const ISO = [
    { id: "I-131", name: "iodine-131", T: 8.0252 * DAY, M: 131, ht: "8 days", use: "medicine, fission product" },
    { id: "Cs-137", name: "caesium-137", T: 30.08 * YR, M: 137, ht: "30 years", use: "fission product" },
    { id: "C-14", name: "carbon-14", T: 5700 * YR, M: 14, ht: "5,700 years", use: "radiocarbon dating" },
    { id: "U-238", name: "uranium-238", T: 4.468e9 * YR, M: 238, ht: "4.5 billion years", use: "natural uranium" },
  ];
  ISO.forEach((s) => (s.A0 = (LN2 / s.T) * NA / s.M)); // becquerel per gram
  const LT0 = 3, LT1 = 17.8, log10 = (x) => Math.log(x) / Math.LN10;
  const SUP = "⁰¹²³⁴⁵⁶⁷⁸⁹", sup = (n) => (n < 0 ? "⁻" : "") + String(Math.abs(n)).split("").map((d) => SUP[+d]).join("");
  function fmtA(a) {
    if (a < 1) return "under 1";
    if (a < 1000) return a.toFixed(0);
    const e = Math.floor(log10(a)), m = a / 10 ** e; return `${m.toFixed(1)}×10${sup(e)}`;
  }
  function fmtT(s) {
    const y = s / YR;
    if (s < 3600) return `${Math.round(s / 60)} minutes`;
    if (s < 2 * DAY) return `${Math.round(s / 3600)} hours`;
    if (s < 60 * DAY) return `${Math.round(s / DAY)} days`;
    if (y < 2) return `${Math.round(s / (30.44 * DAY))} months`;
    if (y < 1e4) return `${y < 100 ? Math.round(y) : Math.round(y / 10) * 10} years`.replace(/(\d)(\d{3}) /, "$1,$2 ");
    if (y < 1e6) return `${Math.round(y / 1000)} thousand years`;
    if (y < 1e9) return `${(y / 1e6).toFixed(y < 1e7 ? 1 : 0)} million years`;
    return `${(y / 1e9).toFixed(1)} billion years`;
  }
  const TICKS = [[log10(3600), "1 hour", "1 h"], [log10(DAY), "1 day", "1 d"], [log10(YR), "1 year", "1 yr"], [log10(1000 * YR), "1000 years", "10³ yr"], [log10(1e6 * YR), "1 million years", "10⁶ yr"], [log10(1e9 * YR), "1 billion years", "10⁹ yr"]];

  // ---------- the sample ----------
  const N0 = 220, R = rng(31), P = [], alive = new Uint8Array(N0), was = new Uint8Array(N0), U = new Float32Array(N0);
  for (let i = 0; i < N0; i++) { const a = i * 2.39996 + R() * 0.25, rr = Math.sqrt((i + 0.5) / N0) * (0.94 + 0.06 * R()); P.push([rr * Math.cos(a), rr * Math.sin(a), R() * TAU]); U[i] = R(); }
  const sim = { t: 0, n: N0, hist: [], acc: 0, pause: 0 }, flashes = [], shots = [], rings = [];
  function refill() { alive.fill(1); sim.t = 0; sim.n = N0; sim.hist = [[0, N0]]; sim.acc = 0; sim.pause = 0; }
  refill();
  function pop(i, S, x, y) {
    flashes.push({ x, y, t: S.time }); if (flashes.length > 80) flashes.shift();
    const a = R() * TAU; shots.push({ x, y, vx: Math.cos(a), vy: Math.sin(a), t: S.time }); if (shots.length > 90) shots.shift();
  }
  function advance(S, dt, geo) {
    const p = 1 - Math.pow(2, -dt / S.Th);
    for (let i = 0; i < N0; i++) if (alive[i] && R() < p) { alive[i] = 0; sim.n--; if (geo) pop(i, S, geo.x + P[i][0] * geo.r, geo.y + P[i][1] * geo.r * geo.sq); }
    sim.t += dt; sim.acc += dt; if (sim.acc >= 0.05) { sim.acc = 0; sim.hist.push([sim.t, sim.n]); }
  }
  function pickTag(S) { const a = []; for (let i = 0; i < N0; i++) if (alive[i]) a.push(i); S.tag = a.length ? a[Math.floor(R() * a.length)] : -1; S.tagT = sim.t; S.tagGone = 0; }
  const press = (sel, on) => document.querySelectorAll(`#halflife [data-act^="${sel}"]`).forEach((b) => b.setAttribute("aria-pressed", String(b.dataset.act === on)));

  WT.chapter("halflife", {
    level: 0, num: "Lesson 1", title: "Radioactivity and half-life", short: "Half-life",
    lead: "Some atoms are unstable: sooner or later their nucleus pops, throws out radiation and becomes something else. Nobody can say when one will go, yet a whole sample follows a clock you can set your watch by.",
    html: `
<div class="step">
  <h3>A sample that pops at random</h3>
  <p>Each glowing ball is an unstable nucleus. Any one may pop at any moment, sending out a flash of radiation and settling into a calm, stable atom. Tap one to make it pop.</p>
  <div class="btns"><button class="btn" data-act="refill">Fresh sample</button></div>
</div>
<div class="step">
  <h3>Half, then half again</h3>
  <p>Nobody can say which one goes next, but the crowd is predictable: after one <b>half-life</b> about half are left, after two a quarter, then an eighth. Make the half-life longer or shorter.</p>
  <div class="ctl"><label for="hl-th">Half-life (seconds)</label><input id="hl-th" type="range" data-bind="Th" data-instant min="1" max="8" step="0.5" value="3"><output data-show="Th" data-fmt="1"></output></div>
  <div class="btns"><button class="btn ghost" data-act="refill">Fresh sample</button></div>
</div>
<div class="step">
  <h3>Nuclei have no memory</h3>
  <p>Follow one survivor. However long it has already lasted, its chance of lasting one more half-life is still one in two: a nucleus does not age.</p>
  <div class="btns"><button class="btn ghost" data-act="tag">Follow another</button><button class="btn ghost" data-act="refill">Fresh sample</button></div>
</div>
<div class="step">
  <h3>Real half-lives</h3>
  <p>Real isotopes span from days to billions of years. On this stretched time line each one falls off a cliff at its own half-life. Pick one and drag time forward.</p>
  <div class="btns"><button class="btn ghost" data-act="iso0" aria-pressed="false">Iodine-131</button><button class="btn ghost" data-act="iso1" aria-pressed="true">Caesium-137</button><button class="btn ghost" data-act="iso2" aria-pressed="false">Carbon-14</button><button class="btn ghost" data-act="iso3" aria-pressed="false">Uranium-238</button></div>
  <div class="ctl"><label for="hl-t1">Time passed</label><input id="hl-t1" type="range" data-bind="lt" data-instant min="${LT0}" max="${LT1}" step="0.02" value="8.98"><output class="hl-tout"></output></div>
</div>
<div class="step">
  <h3>Activity: pops per second</h3>
  <p>One gram of each, side by side. A short half-life means many pops every second, but not for long; a long half-life glows faintly for ages. Drag time and watch the lamps go out one by one.</p>
  <div class="ctl"><label for="hl-t2">Time passed</label><input id="hl-t2" type="range" data-bind="lt" data-instant min="${LT0}" max="${LT1}" step="0.02" value="4.94"><output class="hl-tout"></output></div>
</div>`,
    setup(S) {
      S.set("mode", "live"); S.set("Th", 3); S.set("lt", 8.98); S.set("iso", 1); S.set("curveV", 0); S.tag = -1; S.tagT = 0; S.tagGone = 0; S._tout = "";
      S.on("refill", () => { refill(); if (S.step === 2) pickTag(S); });
      S.on("tag", () => pickTag(S));
      ISO.forEach((s, k) => S.on("iso" + k, () => {
        S.set("iso", k); press("iso", "iso" + k);
        const v = Math.min(LT1, log10(s.T)); S.to("lt", v); document.querySelectorAll("#halflife [data-bind=lt]").forEach((x) => (x.value = v));
      }));
    },
    steps: [
      (S) => { S.set("mode", "live"); S.to("curveV", 0); S.tag = -1; },
      (S) => { S.set("mode", "live"); S.to("curveV", 1); S.tag = -1; },
      (S) => { S.set("mode", "live"); S.to("curveV", 1); if (sim.n < N0 * 0.3) refill(); pickTag(S); },
      (S) => { S.set("mode", "real"); S.tag = -1; press("iso", "iso" + S.iso); S.to("lt", log10(ISO[S.iso].T)); },
      (S) => { S.set("mode", "act"); S.tag = -1; S.to("lt", log10(DAY)); },
    ],
    frame(g, S, dt) {
      const { W, H, c, ctx } = g, phone = W < 600, fs = phone ? 11 : 13, snap = document.body.classList.contains("shot"), mode = S.mode;
      const tl = 10 ** S.lt;
      { const s = fmtT(tl); if (s !== S._tout) { S._tout = s; document.querySelectorAll("#halflife .hl-tout").forEach((o) => (o.textContent = s)); } }
      // ---------- geometry ----------
      const big = mode === "live" ? 1 - S.curveV : 0, sr = Math.min(W * (phone ? 0.3 : 0.27), H * 0.21) * (1 + 0.45 * big), sx = W * 0.5, sy = lerp(H * 0.07 + sr, H * 0.45, big), sq = 0.92;
      const geo = { x: sx, y: sy, r: sr, sq }, br = Math.max(2.4, sr / Math.sqrt(N0) * 0.86);
      const x0 = W * (phone ? 0.1 : 0.12), x1 = W * (phone ? 0.95 : 0.92), yT = H * (phone ? 0.58 : 0.56), yB = H * (phone ? 0.84 : 0.83);
      S._g = { sx, sy, sr, sq, br, x0, x1, yT, yB };
      if (!S._cv) { S._cv = ctx.canvas; const cv = S._cv;
        const hitN = (x, y) => { const G = S._g; let best = -1, bd = (G.br * 2.6) ** 2; for (let i = 0; i < N0; i++) { if (!alive[i]) continue; const dx = G.sx + P[i][0] * G.sr - x, dy = G.sy + P[i][1] * G.sr * G.sq - y, d = dx * dx + dy * dy; if (d < bd) { bd = d; best = i; } } return best; };
        const onPlot = (x, y) => { const G = S._g; return S.mode !== "live" && x > G.x0 - 10 && x < G.x1 + 10 && y > G.yT - 24 && y < G.yB + 24; };
        const setT = (x) => { const G = S._g; S.set("lt", clamp(LT0 + (LT1 - LT0) * (x - G.x0) / (G.x1 - G.x0), LT0, LT1)); };
        const sync = () => document.querySelectorAll("#halflife [data-bind=lt]").forEach((el) => (el.value = S.lt));
        WT.grab(cv, {
          down: (x, y) => {
            if (S.mode === "live") { const i = hitN(x, y); if (i >= 0) { const G = S._g, px = G.sx + P[i][0] * G.sr, py = G.sy + P[i][1] * G.sr * G.sq; alive[i] = 0; sim.n--; pop(i, S, px, py); rings.push({ x: px, y: py, t: S.time }); if (rings.length > 12) rings.shift(); } return false; }
            if (onPlot(x, y)) { setT(x); return true; } return false;
          },
          move: (x) => { setT(x); }, up: sync,
          hover: (x, y) => { cv.style.cursor = (S.mode === "live" ? hitN(x, y) >= 0 : onPlot(x, y)) ? (S.mode === "live" ? "pointer" : "ew-resize") : ""; },
        });
      }

      if (mode === "live") {
        // ---------- live sample ----------
        if (snap && sim.t === 0) { const target = S.step >= 2 ? 1.7 * S.Th : S.step === 1 ? 1.4 * S.Th : 0.6 * S.Th; while (sim.t < target) advance(S, 0.05, null); if (S.step === 2) { pickTag(S); S.tagT = 0; } }
        if (!snap) {
          if (sim.n === 0 || sim.t > 6.5 * S.Th) { sim.pause += dt; if (sim.pause > 1.4) { refill(); if (S.step === 2) pickTag(S); } }
          else { let left = dt; while (left > 1e-6) { const h = Math.min(left, 0.02); advance(S, h, geo); left -= h; } }
        }
        g.glow(sx, sy, sr * 1.5, c.warm, 0.08 + 0.22 * sim.n / N0);
        for (let i = 0; i < N0; i++) {
          const x = sx + P[i][0] * sr, y = sy + P[i][1] * sr * sq;
          if (alive[i]) { const j = Math.sin(S.time * 7 + P[i][2] * 9) * 0.6, tw = (S.time * 0.9 + P[i][2]) % 2.2; if (tw < 0.25) g.glow(x, y, br * 2.6, c.photon, 0.5 * (1 - tw / 0.25)); g.ball(x + j, y - j * 0.5, br, c.warm, 0.96); }
          else g.dot(x, y, br * 0.6, c.soft, 0.3);
        }
        // pops: flashes and little streaks of radiation
        for (const f of flashes) { const a = S.time - f.t; if (a < 0.5) g.glow(f.x, f.y, br * 2 + a * 40, c.photon, 0.75 * (1 - a / 0.5)); }
        if (snap) { let m = 0; for (let i = 0; i < N0 && m < 7; i += 29) if (!alive[i]) { m++; const x = sx + P[i][0] * sr, y = sy + P[i][1] * sr * sq, an = i * 1.7; g.glow(x, y, br * 3, c.photon, 0.6); g.ring(x, y, br * 1.6 + m, c.photon, 1.6, 0.55); g.line(x + Math.cos(an) * 14, y + Math.sin(an) * 14, x + Math.cos(an) * 46, y + Math.sin(an) * 46, c.photon, 2, 0.8); } }
        for (const q of rings) { const a = S.time - q.t; if (a > 0.9) continue; g.ring(q.x, q.y, br * 2 + a * 120, c.photon, 3 * (1 - a / 0.9), 0.9 * (1 - a / 0.9)); g.glow(q.x, q.y, br * 4 + a * 60, "#ffffff", 0.5 * (1 - a / 0.9)); }
        for (const s of shots) { const a = S.time - s.t; if (a > 0.7) continue; const d = 8 + a * 260; g.line(s.x + s.vx * (d - 14), s.y + s.vy * (d - 14), s.x + s.vx * d, s.y + s.vy * d, c.photon, 2, 1 - a / 0.7); }
        // tagged survivor (no memory)
        if (S.tag >= 0) {
          const i = S.tag, x = sx + P[i][0] * sr, y = sy + P[i][1] * sr * sq, age = (sim.t - S.tagT) / S.Th;
          if (alive[i]) {
            g.ring(x, y, br * 2.6 + Math.sin(S.time * 4) * 1.5, c.accent, 2.2); g.glow(x, y, br * 5, c.accent, 0.3);
            const lx = sx + sr + 16 < W - 150 ? sx + sr + 16 : null;
            const s1 = `survived ${age.toFixed(1)} half-lives`, s2 = "chance to last one more: 1 in 2";
            if (!phone && lx) { g.label(s1, lx, sy - 12, { color: c.accent, size: fs, weight: 600, align: "left" }); g.label(s2, lx, sy + 10, { color: c.soft, size: fs - 1, align: "left" }); g.line(x + br * 3, y, lx - 6, sy - 2, c.accent, 1, 0.4, [3, 4]); }
            else { g.label(`survived ${age.toFixed(1)} half-lives · still 1 in 2`, sx, sy + sr * sq + 14, { color: c.accent, size: fs, weight: 600, bg: true }); }
          } else {
            if (!S.tagGone) S.tagGone = S.time;
            g.label("it popped: follow another", sx, sy + sr * sq + 14, { color: c.accent, size: fs, weight: 600, bg: true });
            if (S.time - S.tagGone > 1.6 && sim.n > 0) pickTag(S);
          }
        }
        if (S.curveV < 0.5) g.label(`${sim.n} of ${N0} still unstable`, sx, sy + sr * sq + (phone ? 16 : 22), { color: c.soft, size: fs, alpha: S.tag >= 0 ? 0 : 1 });
        // ---------- landscape: what is left ----------
        const cv = S.curveV;
        if (cv > 0.02) {
          ctx.save(); ctx.globalAlpha = cv;
          const TM = 6, X = (t) => x0 + (x1 - x0) * t / (TM * S.Th), Y = (n) => lerp(yB, yT, n / N0);
          const exp = []; for (let i = 0; i <= 120; i++) { const t = TM * S.Th * i / 120; exp.push([X(t), Y(N0 * 2 ** (-t / S.Th))]); }
          g.clip(0, 0, W, yB); g.ground(exp, c.warm, (yB - yT) * 0.9, 0.3); ctx.restore(); g.poly(exp, c.warm, 1.6, 0.55, [5, 4]);
          g.line(x0, yB, x1, yB, c.line, 1);
          for (let k = 1; k <= 4; k++) {
            const xx = X(k * S.Th), yy = Y(N0 / 2 ** k);
            g.line(xx, yy, xx, yB, c.soft, 1, 0.35, [2, 4]); g.line(x0, yy, xx, yy, c.soft, 1, 0.25, [2, 4]);
            g.label(["½", "¼", "⅛", "1/16"][k - 1], xx + 4, yy - 10, { color: c.ink, size: fs, weight: 600, align: "left" });
            g.label(phone ? `${k}` : k === 1 ? "1 half-life" : `${k}`, xx, yB + 12, { color: c.soft, size: fs - 1 });
          }
          if (phone) g.label("half-lives →", x1, yB + 12, { color: c.soft, size: fs - 1, align: "right" });
          const pts = sim.hist.map(([t, n]) => [X(t), Y(n)]).filter((p) => p[0] <= x1);
          g.poly(pts, c.ink, 2.2, 0.9);
          const last = pts[pts.length - 1]; if (last) { g.dot(last[0], last[1], 4.5, c.photon); g.glow(last[0], last[1], 14, c.photon, 0.5); }
          g.label("nuclei left", x0, yT - 12, { color: c.soft, size: fs - 1, align: "left" });
          ctx.restore();
          if (S.tag < 0) g.label(`${sim.n} of ${N0} left · half-life ${S.Th.toFixed(1)} s`, W * 0.5, H * 0.935, { color: c.ink, size: fs + 1, weight: 600, serif: true });
          else g.label("every survivor has the same 1-in-2 chance per half-life", W * 0.5, H * 0.935, { color: c.ink, size: fs + 1, weight: 600, serif: true });
        }
        g.label("illustrative half-life", W - 6, H - 10, { color: c.faint, size: 10, align: "right" });
        return;
      }

      // ---------- real isotopes: log time ----------
      const XL = (lt) => x0 + (x1 - x0) * (lt - LT0) / (LT1 - LT0);
      const tick = () => {
        g.line(x0, yB, x1, yB, c.line, 1);
        TICKS.forEach(([lt, w, s]) => { const xx = XL(lt); g.line(xx, yB, xx, yB + 4, c.soft, 1, 0.6); g.label(phone ? s : w, xx, yB + 13, { color: c.soft, size: fs - 2 }); });
        const xc = XL(S.lt); g.line(xc, yT - 6, xc, yB, c.accent, 1.5, 0.7); g.glow(xc, yB, 10, c.accent, 0.5); g.glow(xc, yT - 8, 16 + 3 * Math.sin(S.time * 3), c.accent, 0.45); g.ball(xc, yT - 8, 6, c.accent); g.label("drag", xc + 10, yT - 8, { color: c.accent, size: fs - 2, align: "left", alpha: 0.8 });
      };
      if (mode === "real") {
        const iso = ISO[S.iso], f = 2 ** (-tl / iso.T);
        let n = 0;
        for (let i = 0; i < N0; i++) { const a = U[i] < f ? 1 : 0; if (was[i] && !a && !snap) pop(i, S, sx + P[i][0] * sr, sy + P[i][1] * sr * sq); was[i] = a; alive[i] = a; n += a; }
        g.glow(sx, sy, sr * 1.5, c.warm, 0.06 + 0.22 * n / N0);
        for (let i = 0; i < N0; i++) {
          const x = sx + P[i][0] * sr, y = sy + P[i][1] * sr * sq;
          if (alive[i]) { const j = Math.sin(S.time * 7 + P[i][2] * 9) * 0.6; g.ball(x + j, y - j * 0.5, br, c.warm, 0.96); } else g.dot(x, y, br * 0.6, c.soft, 0.3);
        }
        for (const fl of flashes) { const a = S.time - fl.t; if (a < 0.5) g.glow(fl.x, fl.y, br * 2 + a * 40, c.photon, 0.75 * (1 - a / 0.5)); }
        g.label(`${iso.name} · half-life ${iso.ht}`, sx, sy + sr * sq + (phone ? 14 : 20), { color: c.ink, size: fs, weight: 600 });
        if (!phone) g.label(iso.use, sx, sy + sr * sq + 38, { color: c.soft, size: fs - 1 });
        // cliffs
        ISO.forEach((s, k) => {
          const pts = []; for (let i = 0; i <= 220; i++) { const lt = LT0 + (LT1 - LT0) * i / 220; pts.push([XL(lt), lerp(yB, yT, 2 ** (-(10 ** lt) / s.T))]); }
          const on = k === S.iso;
          if (on) { g.clip(0, 0, W, yB); g.ground(pts, c.warm, (yB - yT) * 0.9, 0.34); ctx.restore(); }
          g.poly(pts, on ? c.warm : c.soft, on ? 2.6 : 1.3, on ? 1 : 0.45);
          const hx = XL(log10(s.T)); g.dot(hx, lerp(yB, yT, 0.5), on ? 4 : 2.5, on ? c.warm : c.soft, on ? 1 : 0.6);
          g.label(s.id, hx + 4, lerp(yB, yT, 0.5) + (k % 2 ? 14 : -14), { color: on ? c.warm : c.soft, size: fs - 1, weight: on ? 700 : 500, align: "left", bg: on });
        });
        g.label("½", x0 - 8, lerp(yB, yT, 0.5), { color: c.soft, size: fs - 1, align: "right" }); g.label("all", x0 - 8, yT, { color: c.soft, size: fs - 1, align: "right" });
        tick();
        g.label(f >= 0.001 ? `${(100 * f).toFixed(f > 0.1 ? 0 : 1)} % left after ${fmtT(tl)}` : `under 0.1 % left after ${fmtT(tl)}`, W * 0.5, H * 0.935, { color: c.ink, size: fs + 1, weight: 600, serif: true });
        return;
      }

      // ---------- activity of one gram ----------
      const AL0 = -1, AL1 = 17, YA = (la) => lerp(yB, yT, (la - AL0) / (AL1 - AL0));
      const lampY = H * (phone ? 0.13 : 0.24), cols = [c.photon, c.warm, c.fission, c.alpha];
      ISO.forEach((s, k) => {
        const lx = W * (0.14 + 0.24 * k), A = s.A0 * 2 ** (-tl / s.T), la = A > 0 ? log10(A) : -50, lv = clamp((la - 1) / 15, 0, 1);
        const rL = Math.min(W * 0.07, H * 0.08) * (phone ? 0.85 : 1);
        g.glow(lx, lampY, rL * (1.1 + 1.0 * lv), cols[k], 0.08 + 0.45 * lv);
        g.ball(lx, lampY, rL * 0.55, lv > 0.01 ? cols[k] : c.faint, 0.35 + 0.65 * lv);
        // sparkle: more pops for more activity (log scale picture)
        const nsp = Math.round(14 * lv), rr = rng(k * 97 + Math.floor(S.time * (3 + 14 * lv)));
        for (let i = 0; i < nsp; i++) { const a = rr() * TAU, d = rL * (0.65 + 0.6 * rr()); g.dot(lx + Math.cos(a) * d, lampY + Math.sin(a) * d, 1.6 + rr() * 1.6, cols[k], 0.5 + 0.5 * rr()); }
        g.label(phone ? s.id : s.name, lx, lampY + rL * 1.25 + 10, { color: c.ink, size: fs, weight: 600 });
        g.label(`½ ${s.ht}`.replace("billion", phone ? "bn" : "billion"), lx, lampY + rL * 1.25 + 10 + fs + 4, { color: c.soft, size: fs - 2 });
        g.label(A < 1 ? (phone ? "~0 /s" : "almost none") : `${fmtA(A)} /s`, lx, lampY + rL * 1.25 + 10 + 2 * fs + 10, { color: lv > 0.01 ? cols[k] : c.soft, size: fs, weight: 600 });
        // landscape: log activity against log time (plateau, then the cliff)
        const pts = []; for (let i = 0; i <= 200; i++) { const lt = LT0 + (LT1 - LT0) * i / 200, a = s.A0 * 2 ** (-(10 ** lt) / s.T); const l = a > 0 ? log10(a) : -50; if (l < AL0 - 0.5) { pts.push([XL(lt), YA(AL0 - 0.5)]); break; } pts.push([XL(lt), YA(l)]); }
        g.clip(x0, yT - 8, x1 - x0 + 2, yB - yT + 8); g.ground(pts, cols[k], yB - yT, 0.14); g.poly(pts, cols[k], 2.2, 0.9); g.ctx.restore();
        if (la > AL0) { g.dot(XL(S.lt), YA(la), 4, cols[k]); g.glow(XL(S.lt), YA(la), 12, cols[k], 0.5); }
      });
      g.label(phone ? "pops per second (log)" : "pops per second, 1 gram (each line ×10)", x0, yT - 30, { color: c.soft, size: fs - 1, align: "left" });
      for (let e = 0; e <= 15; e += 5) { g.line(x0, YA(e), x1, YA(e), c.line, 1, 0.5, [2, 5]); g.label(`10${sup(e)}`, x0 - 5, YA(e), { color: c.soft, size: fs - 2, align: "right" }); }
      tick();
      g.label(`one gram of each, after ${fmtT(tl)}`, W * 0.5, H * 0.935, { color: c.ink, size: fs + 1, weight: 600, serif: true });
    },
  });
})();
