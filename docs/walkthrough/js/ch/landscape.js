/* The landscape of nuclei: every measured nucleus as a 3D chart (neutrons N across, protons Z deep), drawn with WebGL (kit3d.js).
 * Data: js/data/chart3d.js (AME2020 B/A, NUBASE2020 half-lives, INCOGNITA scope tier). Steps:
 *   "chart"  = flat chart coloured by half-life (stable dark);
 *   "valley" = columns rise to binding energy per nucleon: a ridge along the stable nuclei, falling away on both sides;
 *   "roll"   = one mass chain (fixed A): a nucleus hops by beta decay toward the most tightly bound member of the chain;
 *   "tiers"  = coloured by what INCOGNITA ships for each nucleus.
 * Without WebGL (or when too slow) the same steps draw as a 2D chart from above. */
(function () {
  const { clamp, lerp, smooth } = WT.util;
  const D = () => WT.CHART3D || [];
  const MAGIC = [2, 8, 20, 28, 50, 82, 126];
  const EL = ["n","H","He","Li","Be","B","C","N","O","F","Ne","Na","Mg","Al","Si","P","S","Cl","Ar","K","Ca","Sc","Ti","V","Cr","Mn","Fe","Co","Ni","Cu","Zn","Ga","Ge","As","Se","Br","Kr","Rb","Sr","Y","Zr","Nb","Mo","Tc","Ru","Rh","Pd","Ag","Cd","In","Sn","Sb","Te","I","Xe","Cs","Ba","La","Ce","Pr","Nd","Pm","Sm","Eu","Gd","Tb","Dy","Ho","Er","Tm","Yb","Lu","Hf","Ta","W","Re","Os","Ir","Pt","Au","Hg","Tl","Pb","Bi","Po","At","Rn","Fr","Ra","Ac","Th","Pa","U","Np","Pu","Am","Cm","Bk","Cf","Es","Fm","Md","No","Lr","Rf","Db","Sg","Bh","Hs","Mt","Ds","Rg","Cn","Nh","Fl","Mc","Lv","Ts","Og"];
  const name = (z, a) => `${EL[z] || "Z" + z}-${a}`;
  const fmtT = (lt) => lt == null ? "half-life unknown" : lt >= 99 ? "stable" : lt > 7.5 ? `half-life ${(Math.pow(10, lt) / 3.156e7).toPrecision(2)} years`
    : lt > 4.94 ? `half-life ${(Math.pow(10, lt) / 86400).toPrecision(2)} days` : lt > 1.78 ? `half-life ${(Math.pow(10, lt) / 60).toPrecision(2)} minutes`
    : lt > -0.5 ? `half-life ${Math.pow(10, lt).toPrecision(2)} s` : `half-life ${(Math.pow(10, lt) * 1000).toPrecision(2)} ms`;
  const TIERN = ["not in the library", "model file, tier A (stable or > 1 year)", "model file, tier B (> 1 day)", "model file, tier C (shorter-lived)", "evaluated from measured resonances"];

  // world layout: N along x, Z along -z, B/A up; one unit = one nucleon number step * S
  const SC = 0.06, N0 = 80, Z0 = 55, HB = 1.25, B0 = 6.8;   // world units per nucleon-number step (not S: frame()'s state is S)
  const X = (n) => (n - N0) * SC, Zw = (z) => -(z - Z0) * SC;
  // height: binding per nucleon above B0 MeV (nearly every nucleus holds 7-8.8 MeV per nucleon; the differences are what matter)
  const hOf = (ba, rise) => Math.max(0.02, rise * Math.max(0, ba - B0) * HB);

  // per-chain data for the "roll" step: most-bound isobar of each A
  function chainOf(A) { return D().filter((d) => d[0] + d[1] === A).sort((a, b) => a[0] - b[0]); }

  let col3 = null; // per-instance colour helpers set in build()
  WT.chapter("landscape", {
    title: "The landscape of nuclei", short: "Landscape",
    lead: "Every nucleus anyone has ever made and weighed, in one picture you can turn: about 3,600 of them, and only 252 last forever.",
    html: `
<div class="step">
  <h3>Every nucleus ever measured</h3>
  <p>Each little block is one nucleus: neutrons count across, protons count back. The <b>dark</b> blocks are the 252 that never decay. The others fall apart, orange ones in a blink, blue ones only after years. Drag sideways on the picture to turn it.</p>
  <div class="ctl"><label for="ls-z">Look at element (protons Z)</label><input id="ls-z" type="range" data-bind="zSel" data-instant min="1" max="110" step="1" value="26"><output data-show="zSel" data-fmt="0"></output></div>
  <p class="ctl-result" id="ls-z-out" aria-live="polite"></p>
</div>
<div class="step">
  <h3>Binding as height: the valley</h3>
  <p>Now each block rises to its <b>binding energy per nucleon</b>, how tightly each neutron or proton is held (Chapter 3). The stable nuclei sit along the top of a long ridge; step away from it, with too many neutrons or too many protons, and the blocks drop. The highest point is nickel-62. The thin lines mark the <b>magic numbers</b> (2, 8, 20, 28, 50, 82, 126), where nuclei are extra tightly bound.</p>
</div>
<div class="step">
  <h3>Rolling down to stability</h3>
  <p>Nuclei with the same total number of nucleons (the same <b>mass number</b> A) form a chain across the chart. Start with too many neutrons, as the fragments of a split uranium nucleus do. In <b>beta decay</b> a neutron turns into a proton, so the nucleus steps one place along its chain toward the more tightly bound middle, again and again, until it reaches the top of the ridge and stops. (Nuclei with too many protons do the reverse, from the other side.) Try A = 137: the chain passes caesium-137, the long-lived product of reactor accidents.</p>
  <div class="ctl"><label for="ls-a">Mass number A</label><input id="ls-a" type="range" data-bind="aSel" data-instant min="8" max="250" step="1" value="137"><output data-show="aSel" data-fmt="0"></output></div>
  <p class="ctl-result" id="ls-a-out" aria-live="polite"></p>
</div>
<div class="step">
  <h3>What INCOGNITA ships</h3>
  <p>The same map, coloured by what our library holds for each nucleus. <em style="font-style:normal;color:var(--fission);font-weight:600">Green</em>: evaluated from its measured resonances. The rest have a model file built by the engine alone: <b>dark</b> for stable or long-lived (tier A), <em style="font-style:normal;color:var(--accent);font-weight:600">blue</em> for more than a day (tier B), <em style="font-style:normal;color:var(--warm);font-weight:600">orange</em> for shorter-lived (tier C). Grey ones are not in the library (mostly the lightest nuclei, and a few the engine cannot run).</p>
</div>`,
    setup(S) { S.set("mode", "chart"); S.set("zSel", 26); S.set("aSel", 137); S.to("rise", 0, true); S.to("tierMix", 0, true); S.rollT = 0; },
    steps: [
      (S) => { S.set("mode", "chart"); S.to("rise", 0); S.to("tierMix", 0); },
      (S) => { S.set("mode", "valley"); S.to("rise", 1); S.to("tierMix", 0); },
      (S) => { S.set("mode", "roll"); S.to("rise", 1); S.to("tierMix", 0); S.rollT = S.time; },
      (S) => { S.set("mode", "tiers"); S.to("rise", 0.55); S.to("tierMix", 1); },
    ],
    frame(g, S, dt) {
      const { W, H, c } = g, phone = W < 600, fs = phone ? 11 : 13;
      const data = D(); if (!data.length) { g.label("loading the chart…", W / 2, H / 2, { color: c.soft, size: fs }); return; }
      const v = WT.view3d ? WT.view3d("landscape", g, build) : { ok: false };
      if (/[?&]v3ddebug\b/.test(location.search)) g.label(`rise ${(S.rise ?? 0).toFixed(2)} inst ${v.ok ? v.user.mesh.count : "-"} ` + "3D: " + (document.documentElement.dataset.v3d || "none") + (v.ok ? ` cam ${v.camera.position.x.toFixed(1)},${v.camera.position.y.toFixed(1)},${v.camera.position.z.toFixed(1)} canvas ${v.canvas.style.display} ${v.canvas.width}x${v.canvas.height}` : ""), W / 2, 24, { color: c.ink, size: 12, bg: true });
      if (S.aSel !== S.aShown) { S.aShown = S.aSel; S.rollT = S.time; }
      if (!v.ok) { draw2D(g, S, v.loading); captions(g, S, null); return; }
      // colours / heights for this frame (eased between steps)
      const rise = S.rise ?? 0, tm = S.tierMix ?? 0, mesh = v.user.mesh, m = v.user.m, cc = v.user.cc;
      if (v.user.rise !== rise || v.user.tm !== tm || v.user.gen !== v.gen || v.user.z !== S.zSel || v.user.a !== S.aSel || S.mode !== v.user.mode) {
        v.user.rise = rise; v.user.tm = tm; v.user.gen = v.gen; v.user.z = S.zSel; v.user.a = S.aSel; v.user.mode = S.mode;
        const ink = v.col("ink"), faint = v.col("line"), warm = v.col("warm"), acc = v.col("accent"), fis = v.col("fission"), sel = v.col("proton");
        data.forEach((d, i) => {
          const onChain = S.mode === "roll" && d[0] + d[1] === Math.round(S.aSel), h = hOf(d[2], rise) + (onChain ? 0.03 : 0);
          m.makeScale(SC * 0.86, h, SC * 0.86); m.setPosition(X(d[1]), h / 2, Zw(d[0])); mesh.setMatrixAt(i, m);
          // half-life colour: stable ink; long-lived accent; short warm
          if (d[4] === 99) cc.copy(ink); else if (d[4] == null) cc.copy(faint); else cc.copy(warm).lerp(acc, clamp((d[4] + 3) / 13, 0, 1));
          if (d[3]) cc.lerp(faint, 0.45);                               // estimated masses paler
          if (tm > 0) { const t = d[5], tc = t === 4 ? fis : t === 1 ? ink : t === 2 ? acc : t === 3 ? warm : faint; cc.lerp(tc, tm); }
          if (S.mode === "chart" && d[0] === Math.round(S.zSel)) cc.lerp(sel, 0.85);
          if (onChain) cc.copy(sel);
          mesh.setColorAt(i, cc);
        });
        mesh.instanceMatrix.needsUpdate = true; mesh.instanceColor.needsUpdate = true;
        v.user.magic.forEach((ln) => (ln.material.color.copy(v.col("soft"))));
      }
      v.user.magic.forEach((ln) => (ln.visible = S.mode === "valley" || S.mode === "roll"));
      // the rolling ball on the chosen chain
      const ball = v.user.ball; ball.visible = S.mode === "roll";
      let rollInfo = null;
      if (S.mode === "roll") {
        const ch = chainOf(Math.round(S.aSel));
        if (ch.length) {
          let top = 0; ch.forEach((d, i) => { if (d[2] > ch[top][2]) top = i; });
          // start at the neutron-rich end (lowest Z, the near side of the ridge): beta-minus decay, as fission products do
          const start = top > 0 ? 0 : ch.length - 1, dir = start < top ? 1 : -1, hops = Math.abs(top - start);
          const tt = Math.max(0, S.time - (S.rollT || 0)) * 1.4, k = Math.min(hops, Math.floor(tt)), f = smooth(0, 1, tt - k);
          const a = ch[start + dir * k], b = ch[start + dir * Math.min(hops, k + 1)];
          const px = lerp(X(a[1]), X(b[1]), k < hops ? f : 0), pz = lerp(Zw(a[0]), Zw(b[0]), k < hops ? f : 0);
          const py = lerp(hOf(a[2], 1), hOf(b[2], 1), k < hops ? f : 0) + 0.03 + 0.11 + (k < hops ? Math.sin(Math.PI * f) * 0.16 : 0);
          ball.position.set(px, py, pz); ball.material.color.copy(v.col("warm"));
          rollInfo = { now: k < hops ? a : ch[top], top: ch[top], hops, k, p: v.project(px, py + 0.12, pz), dir };
          if (tt > hops + 2.5) S.rollT = S.time;              // replay
        }
      }
      // camera: a wide orbit; closer on phones (narrow view)
      v.target.set(-0.7, (S.rise ?? 0) * 0.6, 0.1); v.orbit(phone ? 18 : 14.5, dt);
      v.render();
      // labels over the 3D picture
      const lab = (x, y, z, s, o) => { const [sx, sy, ok] = v.project(x, y, z); if (ok && sx > 10 && sx < W - 10 && sy > 10 && sy < H - 10) g.label(s, sx, sy, o); };
      lab(X(170), 0.05, Zw(Z0 - 12), "neutrons N →", { color: c.soft, size: fs - 1 });
      lab(X(-6), 0.05, Zw(118), "protons Z ↑", { color: c.soft, size: fs - 1 });
      if (S.mode === "valley" || S.mode === "roll") lab(X(34), hOf(8.7946, rise) + 0.25, Zw(28), "nickel-62: most tightly bound", { color: c.fission, size: fs, weight: 600, bg: true });
      if (S.mode === "valley" && !phone) MAGIC.slice(2).forEach((mg) => lab(X(mg), 0.05, Zw(-6), `N = ${mg}`, { color: c.faint, size: 11 }));
      if (rollInfo && rollInfo.p[2]) g.label(name(rollInfo.now[0], rollInfo.now[0] + rollInfo.now[1]), rollInfo.p[0], rollInfo.p[1] - 14, { color: c.warm, size: fs, weight: 600, bg: true });
      captions(g, S, rollInfo);
      g.label(phone ? "drag sideways to turn" : "drag on the picture to turn it", W - 8, H - 10, { color: c.faint, size: 11, align: "right" });
    },
  });

  function build(T, v) {
    const data = D(), geo = new T.BoxGeometry(1, 1, 1), mat = new T.MeshStandardMaterial({ roughness: 0.6, metalness: 0.0 });
    const mesh = new T.InstancedMesh(geo, mat, data.length); mesh.instanceMatrix.setUsage(T.DynamicDrawUsage); mesh.frustumCulled = false;   // instances move every step; never cull on a stale bound
    mesh.setColorAt(0, new T.Color(1, 1, 1));
    v.scene.add(mesh); v.user.mesh = mesh; v.user.m = new T.Matrix4(); v.user.cc = new T.Color();
    // magic-number lines on the ground: N = magic (across) and Z = magic (deep)
    v.user.magic = [];
    const lm = () => new T.LineBasicMaterial({ color: 0x888888, transparent: true, opacity: 0.55 });
    MAGIC.forEach((mg) => {
      const a = new T.BufferGeometry().setFromPoints([new T.Vector3(X(mg), 0.004, Zw(-2)), new T.Vector3(X(mg), 0.004, Zw(125))]);
      const b = new T.BufferGeometry().setFromPoints([new T.Vector3(X(-2), 0.004, Zw(mg)), new T.Vector3(X(180), 0.004, Zw(mg))]);
      [a, b].forEach((gm) => { const ln = new T.Line(gm, lm()); v.scene.add(ln); v.user.magic.push(ln); });
    });
    const ball = new T.Mesh(new T.SphereGeometry(0.11, 24, 16), new T.MeshStandardMaterial({ roughness: 0.3, emissive: 0x331100 }));
    v.scene.add(ball); v.user.ball = ball;
    v.yaw = -0.35; v.pitch = 0.62; v.spin = 0.05;
  }

  // HTML readouts under the sliders, and the canvas caption
  function captions(g, S, rollInfo) {
    const data = D();
    if (S.mode === "chart") {
      const z = Math.round(S.zSel);
      if (z !== S.zShown) { S.zShown = z; const row = data.filter((d) => d[0] === z), st = row.filter((d) => d[4] === 99).length, o = document.getElementById("ls-z-out");
        if (o) o.textContent = row.length ? `${EL[z] || "Z = " + z}: ${row.length} isotopes measured, ${st ? st + " stable" : "none stable"} (from ${name(z, z + row[0][1])} to ${name(z, z + row[row.length - 1][1])})` : `Z = ${z}: none measured`; }
    }
    if (S.mode === "roll" && rollInfo) {
      const key = `${Math.round(S.aSel)}|${rollInfo.k}`;
      if (key !== S.aKey) { S.aKey = key; const o = document.getElementById("ls-a-out"), t = rollInfo.top;
        if (o) o.textContent = rollInfo.hops ? `A = ${Math.round(S.aSel)}: from ${name(rollInfo.now[0], Math.round(S.aSel))} (${fmtT(rollInfo.now[4])}), ${rollInfo.hops} beta decay${rollInfo.hops > 1 ? "s" : ""} to ${name(t[0], Math.round(S.aSel))}, the most tightly bound of the chain`
          : `A = ${Math.round(S.aSel)}: only one nucleus measured in this chain`; }
    }
    void g;
  }

  // 2D fallback: the chart seen from above, same colours and steps
  function draw2D(g, S, loading) {
    const { W, H, c } = g, phone = W < 600, fs = phone ? 11 : 13, data = D();
    const x0 = W * 0.08, x1 = W * 0.96, y0 = H * 0.08, y1 = H * 0.86, sx = (x1 - x0) / 180, sy = (y1 - y0) / 120, cell = Math.max(1.4, Math.min(sx, sy) * 0.92);
    const tm = S.tierMix ?? 0;
    data.forEach((d) => {
      let col;
      if (tm > 0.5) col = d[5] === 4 ? c.fission : d[5] === 1 ? c.ink : d[5] === 2 ? c.accent : d[5] === 3 ? c.warm : c.line;
      else if (S.mode === "valley" || S.mode === "roll") { const u = clamp((d[2] - 6) / 2.8, 0, 1); col = u > 0.85 ? c.fission : u > 0.5 ? c.accent : c.warm; }
      else col = d[4] === 99 ? c.ink : d[4] == null ? c.line : d[4] > 4 ? c.accent : c.warm;
      const hl = (S.mode === "chart" && d[0] === Math.round(S.zSel)) || (S.mode === "roll" && d[0] + d[1] === Math.round(S.aSel));
      g.ctx.fillStyle = hl ? c.proton : col; g.ctx.globalAlpha = d[3] ? 0.5 : 1; g.ctx.fillRect(x0 + d[1] * sx, y1 - d[0] * sy, cell, cell);
    });
    g.ctx.globalAlpha = 1;
    g.label("neutrons N →", x1, y1 + 14, { color: c.soft, size: fs - 1, align: "right" });
    g.label("protons Z ↑", x0, y0 - 8, { color: c.soft, size: fs - 1, align: "left" });
    if (S.mode === "valley" || S.mode === "roll") g.label("green = most tightly bound, orange = least", W / 2, H * 0.95, { color: c.soft, size: fs - 1 });
    g.label(loading ? "loading the 3D view…" : "flat view (3D needs WebGL)", W - 8, 12, { color: c.faint, size: 10, align: "right" });
  }
})();
