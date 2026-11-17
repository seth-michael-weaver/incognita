/* Computing criticality: real benchmark numbers, drawn in 3-D (js/kit3d.js). Data: js/data/kcalc.js (WT.kcalcData).
 * Scenes (S.mode):
 *   "geo"   = the four ICSBEP fast assemblies to scale (cm), cut open: Godiva (bare HEU, r 8.74), Jezebel (bare Pu, r 6.39),
 *             Flattop-25 (HEU core r 6.12 in natural U to r 24.12), Flattop-Pu (Pu core r 4.53 in natural U to r 24.14).
 *             Columns: uranium left, plutonium right. Drag turns the spheres.
 *   "k"     = the same spheres with k_eff from INCOGNITA data in OpenMC (continuous energy, 3-D) and a gauge of C - E (pcm)
 *             inside the benchmark's 1-sigma band.
 *   "sn"    = OpenSn (discrete ordinates) against OpenMC on the same 33-group data: one dial, two needles, in pcm.
 *   "sens"  = adjoint sensitivity profiles dk/k per dsigma/sigma per unit lethargy, ECCO-33 groups above 100 eV, one ribbon
 *             per reaction (3-D, orbitable).
 *   "check" = predicted (adjoint) against re-solved k changes for 63 candidate data sets.
 *   "core"  = C5G7 2-D (quarter core, 2 UO2 + 2 MOX assemblies, water reflector): pin power relative to the core mean as
 *             extruded bars (3-D, orbitable); hover or tap a pin for its value.
 * Without WebGL (or when it is slow) every scene has a flat 2-D drawing. */
(function () {
  const { TAU, clamp, lerp } = WT.util;
  const D = WT.kcalcData;
  if (!D) return;
  const C = D.cases, byId = {}; C.forEach((c) => (byId[c.id] = c));
  const pcm = (p) => (p > 0 ? "+" : p < 0 ? "−" : "") + Math.abs(p).toFixed(Number.isInteger(p) ? 0 : 1) + " pcm";
  // 2x2 layout (world cm): uranium column left, plutonium column right; bare spheres on top
  const POS = { Godiva: [-27, 33], Jezebel: [27, 33], "Flattop-25": [-27, -14], "Flattop-Pu": [27, -14] };
  const outerR = (c) => c.refl || c.core;
  const fuelCol = (c) => (c.fuel === "U" ? "warm" : "alpha");
  const SENS = ["Godiva", "Jezebel", "Flattop-Pu"];
  const RX = { nu: "neutrons per fission (ν)", fis: "fission", el: "elastic", nonel: "inelastic", cap: "capture" };
  const RXC = { nu: "photon", fis: "warm", el: "cool", nonel: "alpha", cap: "proton" };
  const nucName = (n) => ({ U235: "U-235", U238: "U-238", Pu239: "Pu-239", Pu240: "Pu-240" }[n] || n);
  // energy groups above 100 eV, ascending energy: [log10 Emid, lethargy width, group index]
  const GR = []; for (let gi = 32; gi >= 0; gi--) { const lo = D.ecco[32 - gi], hi = D.ecco[33 - gi]; if (lo >= 99) GR.push([Math.log10(Math.sqrt(lo * hi)), Math.log(hi / lo), gi]); }
  const LX0 = 2.2, LX1 = 7.2, ex = (l) => (l - 4.7) * 14;          // log10 E -> world x
  const SY = 95;                                                      // sensitivity per lethargy -> world y
  const pins = D.c5g7.pins, NP = pins.length;
  let pinMax = 0; pins.forEach((r) => r.forEach((p) => (pinMax = Math.max(pinMax, p))));
  const PH = 5.5;                                                     // world height per unit relative power

  const setBtns = (act, i) => document.querySelectorAll(`#kcalc [data-act^="${act}"]`).forEach((b) => b.setAttribute("aria-pressed", String(b.dataset.act === act + i)));

  // ---------- 3-D builders ----------
  function glowTex(T) {
    const cv = document.createElement("canvas"); cv.width = cv.height = 128; const x = cv.getContext("2d");
    const gr = x.createRadialGradient(64, 64, 0, 64, 64, 64); gr.addColorStop(0, "rgba(255,255,255,1)"); gr.addColorStop(0.35, "rgba(255,255,255,.35)"); gr.addColorStop(1, "rgba(255,255,255,0)");
    x.fillStyle = gr; x.fillRect(0, 0, 128, 128); const t = new T.CanvasTexture(cv); return t;
  }
  function buildSpheres(T, v) {
    v.spin = 0; v.yaw = 0; v.pitch = 0;
    const U = (v.user = { items: [], mats: [] }), PHI = 1.5 * Math.PI, tex = glowTex(T);
    const steel = new T.MeshStandardMaterial({ color: 0x8e96a2, metalness: 0.55, roughness: 0.42 });
    const steelCut = new T.MeshStandardMaterial({ color: 0xa9b0bb, metalness: 0.2, roughness: 0.75, side: T.DoubleSide });
    const cutFaces = (grp, geoF) => [0, PHI].forEach((phi) => { const m = new T.Mesh(geoF(), grp.cutMat); m.rotation.y = phi - Math.PI; grp.add(m); });
    C.forEach((c) => {
      const g = new T.Group(), inner = new T.Group(); g.add(inner);
      const coreMat = new T.MeshStandardMaterial({ metalness: 0.35, roughness: 0.35 });
      const coreCut = new T.MeshStandardMaterial({ roughness: 0.6, side: T.DoubleSide });
      U.mats.push([coreMat, coreCut, fuelCol(c)]);
      inner.add(new T.Mesh(new T.SphereGeometry(c.core, 48, 32, 0, PHI), coreMat));
      [0, PHI].forEach((phi) => { const m = new T.Mesh(new T.CircleGeometry(c.core, 40, -Math.PI / 2, Math.PI), coreCut); m.rotation.y = phi - Math.PI; inner.add(m); });
      if (c.refl) {
        inner.add(new T.Mesh(new T.SphereGeometry(c.refl, 64, 40, 0, PHI), steel));
        [0, PHI].forEach((phi) => { const m = new T.Mesh(new T.RingGeometry(c.core, c.refl, 64, 1, -Math.PI / 2, Math.PI), steelCut); m.rotation.y = phi - Math.PI; inner.add(m); });
      }
      const glow = new T.Sprite(new T.SpriteMaterial({ map: tex, transparent: true, depthWrite: false, opacity: 0.5 }));
      glow.scale.set(c.core * 4.2, c.core * 4.2, 1); g.add(glow); glow.renderOrder = -1;
      const [x, y] = POS[c.id]; g.position.set(x, y, 0);
      v.scene.add(g); U.items.push({ c, g, inner, glow, coreMat, coreCut });
    });
    // a 10 cm scale bar on the floor line between the rows
    const bar = new T.Mesh(new T.BoxGeometry(10, 0.5, 0.5), new T.MeshBasicMaterial({ color: 0x8b93a5 }));
    bar.position.set(0, 17, 0); v.scene.add(bar); U.bar = bar;
  }
  function colorSpheres(v) {
    const U = v.user; if (U.gen === v.gen) return; U.gen = v.gen;
    U.items.forEach((it) => {
      const col = v.col(fuelCol(it.c));
      it.coreMat.color.copy(col); it.coreMat.emissive.copy(col); it.coreMat.emissiveIntensity = 0.35;
      it.coreCut.color.copy(col); it.coreCut.emissive.copy(col); it.coreCut.emissiveIntensity = 0.85;
      it.glow.material.color.copy(col);
    });
  }
  function buildSens(T, v) {
    v.yaw = 0.55; v.pitch = 0.42; v.spin = 0.08; v.target.set(6, 10, 0);
    const U = (v.user = { sets: {} });
    SENS.forEach((id) => {
      const grp = new T.Group(), list = D.prof[id], n = list.length, items = [];
      list.forEach(([key, s], i) => {
        const [nuc, rx] = key.split("|"), z = (i - (n - 1) / 2) * 9;
        const pts = GR.map(([l, w, gi]) => [ex(l), s[gi] / w * SY]);
        const pos = [], idx = [];
        pts.forEach(([x, y], j) => { pos.push(x, 0, z, x, y, z); if (j) { const a = 2 * (j - 1); idx.push(a, a + 1, a + 2, a + 1, a + 3, a + 2); } });
        const geo = new T.BufferGeometry(); geo.setAttribute("position", new T.Float32BufferAttribute(pos, 3)); geo.setIndex(idx); geo.computeVertexNormals();
        const mat = new T.MeshBasicMaterial({ transparent: true, opacity: 0.42, side: T.DoubleSide, depthWrite: false });
        const lgeo = new T.BufferGeometry().setFromPoints(pts.map(([x, y]) => new T.Vector3(x, y, z)));
        const lmat = new T.LineBasicMaterial({});
        const base = new T.BufferGeometry().setFromPoints([new T.Vector3(ex(LX0), 0, z), new T.Vector3(ex(LX1), 0, z)]);
        const bmat = new T.LineBasicMaterial({ transparent: true, opacity: 0.35 });
        grp.add(new T.Mesh(geo, mat), new T.Line(lgeo, lmat), new T.Line(base, bmat));
        let tot = 0, pk = 0, pkx = 0, pky = 0; s.forEach((x) => (tot += x)); pts.forEach(([x, y]) => { if (Math.abs(y) > Math.abs(pk)) { pk = y; pkx = x; pky = y; } });
        items.push({ nuc, rx, z, mat, lmat, bmat, tot, pkx, pky, col: nuc === list[0][0].split("|")[0] || rx !== "fis" ? RXC[rx] : "fission" });
      });
      // decade lines on the floor
      const fl = []; for (let e = 3; e <= 7; e++) fl.push(new T.Vector3(ex(e), 0, -(n - 1) / 2 * 9 - 6), new T.Vector3(ex(e), 0, (n - 1) / 2 * 9 + 6));
      const fmat = new T.LineBasicMaterial({ transparent: true, opacity: 0.3 });
      grp.add(new T.LineSegments(new T.BufferGeometry().setFromPoints(fl), fmat));
      grp.visible = false; v.scene.add(grp); U.sets[id] = { grp, items, n, fmat };
    });
  }
  function colorSens(v) {
    const U = v.user; if (U.gen === v.gen) return; U.gen = v.gen;
    Object.values(U.sets).forEach((st) => { st.fmat.color.copy(v.col("faint")); st.items.forEach((it) => { const c = v.col(it.col); it.mat.color.copy(c); it.lmat.color.copy(c); it.bmat.color.copy(v.col("faint")); }); });
  }
  function buildCore(T, v) {
    v.yaw = 0.75; v.pitch = 0.72; v.spin = 0.06; v.target.set(22, 2, 22);
    const U = (v.user = { tmp: new T.Vector3(), col: new T.Color(), hit: -1 });
    const list = []; for (let i = 0; i < NP; i++) for (let j = 0; j < NP; j++) if (pins[i][j] > 0) list.push([i, j, pins[i][j], D.c5g7.map[i][j]]);
    const m = new T.Matrix4(), box = new T.BoxGeometry(0.82, 1, 0.82); box.translate(0, 0.5, 0);
    const mesh = new T.InstancedMesh(box, new T.MeshStandardMaterial({ roughness: 0.5, metalness: 0.05 }), list.length);
    list.forEach(([i, j, p], k) => { m.makeScale(1, p * PH, 1); m.setPosition(j + 0.5, 0, i + 0.5); mesh.setMatrixAt(k, m); });
    v.scene.add(mesh);
    // guide tubes and the fission chamber: short dark stubs
    const gl = []; for (let i = 0; i < NP; i++) for (let j = 0; j < NP; j++) if (!(pins[i][j] > 0)) gl.push([i, j]);
    const cyl = new T.CylinderGeometry(0.32, 0.32, 0.5, 12); cyl.translate(0, 0.25, 0);
    const tubes = new T.InstancedMesh(cyl, new T.MeshStandardMaterial({ roughness: 0.7 }), gl.length);
    gl.forEach(([i, j], k) => { m.makeTranslation(j + 0.5, 0, i + 0.5); tubes.setMatrixAt(k, m); }); v.scene.add(tubes);
    // assembly plates and the water reflector (the quarter core's outer 17-pin band)
    const plate = (x, z, w, d, mat) => { const b = new T.Mesh(new T.BoxGeometry(w, 0.3, d), mat); b.position.set(x + w / 2, -0.16, z + d / 2); v.scene.add(b); return b; };
    const uo2 = new T.MeshStandardMaterial({ roughness: 0.9 }), mox = new T.MeshStandardMaterial({ roughness: 0.9 });
    const water = new T.MeshStandardMaterial({ transparent: true, opacity: 0.16, roughness: 0.3, depthWrite: false });
    plate(0, 0, 17, 17, uo2); plate(17, 17, 17, 17, uo2); plate(17, 0, 17, 17, mox); plate(0, 17, 17, 17, mox);
    plate(0, 34, 51, 17, water); plate(34, 0, 17, 34, water);
    Object.assign(U, { list, mesh, tubes, uo2, mox, water });
  }
  // sequential ramp for pin power: cool (low) -> photon -> proton (high)
  function ramp(v, t, out) {
    const a = v.col("cool"), b = v.col("photon"), c = v.col("proton");
    return t < 0.5 ? out.copy(a).lerp(b, t * 2) : out.copy(b).lerp(c, (t - 0.5) * 2);
  }
  const P_LO = 0.3, P_HI = 2.5;
  function colorCore(v, hit) {
    const U = v.user; if (U.gen === v.gen && U.lastHit === hit) return;
    const full = U.gen !== v.gen; U.gen = v.gen;
    const paint = (k) => { if (k < 0) return; if (k === hit) U.mesh.setColorAt(k, U.col.copy(v.col("ink"))); else U.mesh.setColorAt(k, ramp(v, clamp((U.list[k][2] - P_LO) / (P_HI - P_LO), 0, 1), U.col)); };
    if (full) { U.list.forEach((_, k) => paint(k)); U.tubes.material.color.copy(v.col("faint")); U.uo2.color.copy(v.col("line")); U.mox.color.copy(v.col("line")).lerp(v.col("alpha"), 0.25); U.water.color.copy(v.col("cool")); }
    else { paint(U.lastHit); paint(hit); }
    U.lastHit = hit; U.mesh.instanceColor.needsUpdate = true;
  }
  const fit = (v, w, h) => { const t = Math.tan((v.camera.fov / 2) * Math.PI / 180); return Math.max(h / 2 / t, w / 2 / (t * v.camera.aspect)); };

  // ---------- 2-D helpers ----------
  function gauge(g, x, y, w, c, a, fs) {
    const R = 300, X = (p) => x + (w / 2) * clamp(p / R, -1, 1);
    g.ctx.save(); g.ctx.fillStyle = g.rgba(g.c.fission, 0.18 * a); g.ctx.fillRect(X(-c.unc), y - 6, X(c.unc) - X(-c.unc), 12); g.ctx.restore();
    g.line(x - w / 2, y, x + w / 2, y, g.c.faint, 1, a);
    g.line(X(0), y - 9, X(0), y + 9, g.c.soft, 1.2, a);
    g.line(X(-c.unc), y - 6, X(-c.unc), y + 6, g.c.fission, 1, 0.8 * a); g.line(X(c.unc), y - 6, X(c.unc), y + 6, g.c.fission, 1, 0.8 * a);
    const px = X(c.pcm * a); g.ctx.save(); g.ctx.globalAlpha = a; g.ctx.fillStyle = g.c.ink; g.ctx.beginPath(); g.ctx.moveTo(px, y - 2); g.ctx.lineTo(px - 6, y - 12); g.ctx.lineTo(px + 6, y - 12); g.ctx.closePath(); g.ctx.fill(); g.ctx.restore();
    g.dot(px, y, 3.5, g.c.ink, a);
  }

  WT.chapter("kcalc", {
    level: 2, num: "Lesson 1", title: "Computing criticality", short: "Computing k",
    html: `
<div class="step">
  <h3>Four spheres of metal</h3>
  <p>Four real critical assemblies, to scale: two bare spheres, and two small cores inside thick shells of natural uranium.</p>
</div>
<div class="step">
  <h3>k, computed</h3>
  <p>Our data in a full 3-D Monte Carlo model: all four within 200 pcm of critical (1&nbsp;pcm = 0.001&nbsp;%), and <i>k</i> was never part of the fit.</p>
</div>
<div class="step">
  <h3>Two solvers, one answer</h3>
  <p>A deterministic solver (OpenSn) against Monte Carlo (OpenMC), on the same 33-group data.</p>
  <div class="btns"><button class="btn ghost" data-act="sn0" aria-pressed="true">Godiva</button><button class="btn ghost" data-act="sn1" aria-pressed="false">Jezebel</button></div>
</div>
<div class="step">
  <h3>What each sphere listens to</h3>
  <p>How much <i>k</i> moves when one reaction changes at one energy, from a single adjoint solve.</p>
  <div class="btns"><button class="btn ghost" data-act="se0" aria-pressed="true">Godiva</button><button class="btn ghost" data-act="se1" aria-pressed="false">Jezebel</button><button class="btn ghost" data-act="se2" aria-pressed="false">Flattop-Pu</button></div>
</div>
<div class="step">
  <h3>Checked by brute force</h3>
  <p>15 of 15 sensitivities match direct re-solves, and they predict the <i>k</i> of 63 new data sets before any re-run.</p>
</div>
<div class="step">
  <h3>A whole core, pin by pin</h3>
  <p>The C5G7 reactor benchmark: 1,056 fuel pins, <i>k</i> within 19 pcm of the reference, every pin power within 0.13&nbsp;%. Next: 3-D, with control rods.</p>
</div>`,
    setup(S) {
      S.set("mode", "geo"); S.set("snc", 0); S.set("sec", 0); S.to("kA", 0, true); S.to("ndl", 0, true); S.hx = S.hy = null;
      [0, 1].forEach((i) => S.on("sn" + i, () => { S.set("snc", i); S.ndl = 0; S.to("ndl", D.sn[i].d); setBtns("sn", i); }));
      [0, 1, 2].forEach((i) => S.on("se" + i, () => { S.set("sec", i); setBtns("se", i); }));
    },
    steps: [
      (S) => { S.set("mode", "geo"); S.to("kA", 0); },
      (S) => { S.set("mode", "k"); S.kA = 0; S.to("kA", 1); },
      (S) => { S.set("mode", "sn"); S.ndl = 0; S.to("ndl", D.sn[S.snc].d); },
      (S) => { S.set("mode", "sens"); },
      (S) => { S.set("mode", "check"); },
      (S) => { S.set("mode", "core"); },
    ],
    frame(g, S, dt) {
      if (g.W < 40 || g.H < 40) return;
      const { W, H, c } = g, phone = W < 600, fs = phone ? 11 : 13, mode = S.mode, snap = document.body.classList.contains("shot");
      if (snap) { S.kA = S.target.kA; S.ndl = S.target.ndl; }
      if (!g.ctx.canvas._kc) {
        g.ctx.canvas._kc = 1;
        const at = (x, y) => { S.hx = x; S.hy = y; };
        WT.grab(g.ctx.canvas, { hover: at, down: (x, y) => { at(x, y); return false; } });
        g.ctx.canvas.addEventListener("pointerleave", (e) => { if (e.pointerType === "mouse") S.hx = S.hy = null; });
      }
      const foot = (s, col) => g.label(s, W / 2, H - (phone ? 16 : 22), { color: col || c.ink, size: fs + 1, weight: 600, serif: true });

      if (mode === "geo" || mode === "k") {
        // world window: x -56..56, y -62..60 (phones -62..76): room for labels above the top row and below the bottom row
        const v = WT.view3d("kcalc-spheres", g, buildSpheres);
        let P, scale;
        const wy0 = -62, wy1 = phone ? 76 : 60, wx = 112;
        if (v.ok) {
          v.orbit(100, dt); colorSpheres(v);
          const d = fit(v, wx, wy1 - wy0), cy = (wy0 + wy1) / 2;
          v.camera.position.set(0, cy + d * 0.12, d); v.camera.lookAt(0, cy, 0);
          const sway = 0.22 * Math.sin(S.time * 0.35);
          v.user.items.forEach((it) => {
            it.inner.rotation.y = Math.PI / 2 + 0.2 + v.yaw + sway; it.inner.rotation.x = 0.32 + clamp(v.pitch, -0.6, 0.6);
            const pulse = mode === "k" ? 0.55 + 0.25 * S.kA * (0.5 + 0.5 * Math.sin(S.time * 2.2 + it.c.core)) : 0.4;
            it.glow.material.opacity = pulse * (it.c.refl ? 0.35 : 0.75); it.coreCut.emissiveIntensity = 0.6 + 0.5 * pulse;
          });
          v.render();
          P = (x, y) => v.project(x, y, 0); scale = Math.abs(P(10, 0)[0] - P(0, 0)[0]) / 10;
        } else {
          scale = Math.min(W / wx, H / (wy1 - wy0)); const cx = W / 2, cy = H / 2 + ((wy0 + wy1) / 2) * scale;
          P = (x, y) => [cx + x * scale, cy - y * scale];
          C.forEach((k) => { const [x, y] = POS[k.id], [px, py] = P(x, y), col = c[fuelCol(k)];
            if (k.refl) { g.dot(px, py, k.refl * scale, c.faint, 0.55); g.ring(px, py, k.refl * scale, c.soft, 1, 0.6); }
            g.glow(px, py, k.core * scale * 2, col, 0.35); g.ball(px, py, k.core * scale, col, 1); });
        }
        // scale bar label
        { const [bx, by] = P(0, 17); g.label("10 cm", bx, by + 14, { color: c.soft, size: fs - 1 }); if (!v.ok) g.line(bx - 5 * scale, by, bx + 5 * scale, by, c.soft, 3); }
        C.forEach((k) => {
          const [x, y] = POS[k.id], R = outerR(k), top = y > 0, gap = phone ? 15 : 18;
          const [lx, ly] = top ? P(x, y + R) : P(x, y - R), y0 = ly + (top ? -1 : 1) * (phone ? 18 : 26);
          const a = clamp(S.kA, 0, 1), L = [];   // lines, top to bottom; the gauge is a line of its own
          if (mode === "geo") {
            L.push([k.id, { color: c.ink, size: fs + 2, weight: 600 }]);
            L.push([k.refl ? (phone ? `${k.core} cm in ${k.refl} cm` : `core ${k.core} cm · shell ${k.refl} cm`) : `radius ${k.core} cm`, { color: c.soft, size: fs - 1 }]);
            if (!phone) L.push([k.fuel === "U" ? (k.refl ? "uranium-235 in natural uranium" : "uranium-235 metal") : (k.refl ? "plutonium in natural uranium" : "plutonium metal"), { color: c[fuelCol(k)], size: fs - 1 }]);
          } else {
            L.push([phone ? `${k.id} ${(1 + (k.k - 1) * a).toFixed(5)}` : `${k.id}  ·  k = ${(1 + (k.k - 1) * a).toFixed(5)}`, { color: c.ink, size: fs + 1, weight: 600 }]);
            L.push([phone ? `${pcm(Math.round(k.pcm * a))} (±${k.unc})` : `${pcm(Math.round(k.pcm * a))}  (benchmark ±${k.unc})`, { color: Math.abs(k.pcm) <= k.unc ? c.fission : c.proton, size: fs - 1, weight: 600 }]);
            L.push(["gauge"]);
          }
          L.forEach(([s, o], i) => {
            const yy = top ? y0 - (L.length - 1 - i) * gap : y0 + i * gap;
            if (s === "gauge") gauge(g, lx, yy + (top ? 0 : 4), phone ? Math.min(112, W * 0.3) : 170, k, a, fs); else g.label(s, lx, yy, o);
          });
        });
        if (phone) return;
        if (mode === "geo") foot(v.ok ? "Drawn to scale. Drag to turn them." : "Drawn to scale.", c.soft);
        else foot(phone ? "4 of 4 within 200 pcm" : "4 of 4 within 200 pcm of k = 1, each inside the benchmark's own ± band", c.fission);
        return;
      }

      if (mode === "sn") {
        const s = D.sn[S.snc], cx = W / 2, cy = H * (phone ? 0.62 : 0.6), R = Math.min(W * 0.42, H * 0.48), A0 = Math.PI * 1.1, A1 = Math.PI * 1.9, RANGE = 60;
        const ang = (p) => lerp(A0, A1, (clamp(p, -RANGE, RANGE) + RANGE) / (2 * RANGE));
        const ctx = g.ctx;
        // target band (±50 pcm) and the dial
        ctx.save(); ctx.lineWidth = R * 0.11; ctx.strokeStyle = g.rgba(c.fission, 0.2); ctx.beginPath(); ctx.arc(cx, cy, R * 0.9, ang(-50), ang(50)); ctx.stroke();
        ctx.lineWidth = 2; ctx.strokeStyle = c.line; ctx.beginPath(); ctx.arc(cx, cy, R, A0, A1); ctx.stroke(); ctx.restore();
        for (let p = -RANGE; p <= RANGE; p += 5) {
          const a = ang(p), big = p % 25 === 0, r0 = R * (big ? 0.93 : 0.96);
          g.line(cx + Math.cos(a) * r0, cy + Math.sin(a) * r0, cx + Math.cos(a) * R, cy + Math.sin(a) * R, big ? c.soft : c.faint, big ? 1.6 : 1);
          if (big) g.label(p === 0 ? "0" : (p > 0 ? "+" : "−") + Math.abs(p), cx + Math.cos(a) * R * 1.09, cy + Math.sin(a) * R * 1.09, { color: c.soft, size: fs - 1 });
        }
        g.label("target ±50 pcm", cx + Math.cos(ang(38)) * R * 0.74, cy + Math.sin(ang(38)) * R * 0.74, { color: c.fission, size: fs - 1, weight: 600 });
        const needle = (p, col, len, w) => { const a = ang(p); g.line(cx, cy, cx + Math.cos(a) * R * len, cy + Math.sin(a) * R * len, col, w); };
        needle(0, c.cool, 0.97, 3); needle(S.ndl, c.warm, 0.88, 4); g.dot(cx, cy, 7, c.ink);
        g.label("OpenMC", cx + Math.cos(ang(0)) * R * 0.5 + (phone ? 34 : 44), cy - R * 0.72, { color: c.cool, size: fs, weight: 600, align: "left" });
        g.label("OpenSn", cx + Math.cos(ang(S.ndl)) * R * 0.5 - (phone ? 30 : 40), cy - R * 0.62, { color: c.warm, size: fs, weight: 600, align: "right" });
        g.label((S.ndl < -0.05 ? "−" : S.ndl > 0.05 ? "+" : "") + Math.abs(S.ndl).toFixed(1) + " pcm", cx, cy + R * 0.22, { color: c.ink, size: phone ? 30 : 40, weight: 600, serif: true });
        g.label(`${s.id}: OpenSn − OpenMC`, cx, cy + R * 0.22 + (phone ? 28 : 36), { color: c.soft, size: fs });
        g.label("pcm", cx, cy - R * 1.2 < 10 ? 14 : cy - R * 1.2, { color: c.faint, size: fs - 1 });
        foot(phone ? "Godiva −11.0 · Jezebel −12.5 pcm" : "Godiva −11.0 pcm · Jezebel −12.5 pcm · Flattop-Pu in progress", c.ink);
        return;
      }

      if (mode === "sens") {
        const id = SENS[S.sec], v = WT.view3d("kcalc-sens", g, buildSens), set = D.prof[id];
        let P;
        if (v.ok) {
          colorSens(v); Object.entries(v.user.sets).forEach(([k, st]) => (st.grp.visible = k === id));
          v.target.y = phone ? 4 : 10; v.target.x = phone ? 13 : 6; v.orbit(fit(v, 92, 70), dt); v.render(); P = (x, y, z) => v.project(x, y, z);
          const st = v.user.sets[id];
          st.items.forEach((it) => {
            const [px, py, vis] = P(it.pkx, it.pky, it.z); if (!vis) return;
            const name = `${nucName(it.nuc)} ${RX[it.rx]}`;
            g.label(phone ? `${nucName(it.nuc)} ${it.rx === "nu" ? "ν" : RX[it.rx]}` : name, px, py + (it.pky >= 0 ? -14 : 14), { color: c[it.col], size: fs - 1, weight: 600, bg: true });
          });
          const zf = (st.n - 1) / 2 * 9 + 6;
          [[3, "1 keV"], [4, "10 keV"], [5, "100 keV"], [6, "1 MeV"], [7, "10 MeV"]].forEach(([e, s]) => { const [px, py, vis] = P(ex(e), 0, zf + 3); if (vis) g.label(s, px, py + 10, { color: c.soft, size: fs - 2 }); });
        } else {
          // flat fallback: one line per reaction
          const x0 = W * 0.1, x1 = W * 0.92, y0 = H * 0.15, y1 = H * 0.78, X = (l) => lerp(x0, x1, (l - LX0) / (LX1 - LX0)), Y = (s) => lerp(y1, y0, (s + 0.05) / 0.45);
          g.line(x0, Y(0), x1, Y(0), c.line, 1);
          set.forEach(([key, s]) => { const [nuc, rx] = key.split("|"), col = c[RXC[rx]], pts = GR.map(([l, w, gi]) => [X(l), Y(s[gi] / w)]); g.poly(pts, col, 2); g.label(`${nucName(nuc)} ${RX[rx]}`, pts[pts.length - 6][0], pts[pts.length - 6][1] - 10, { color: col, size: fs - 1, bg: true }); });
          [[3, "1 keV"], [5, "100 keV"], [7, "10 MeV"]].forEach(([e, s]) => g.label(s, X(e), y1 + 14, { color: c.soft, size: fs - 2 }));
        }
        g.label(phone ? `${id}: change in k per change in data` : `${id}: change in k per change in each reaction, by neutron energy`, W / 2, phone ? 14 : 20, { color: c.ink, size: fs, weight: 600 });
        const nu = set[0][1].reduce((a, b) => a + b, 0), fi = set[1][1].reduce((a, b) => a + b, 0);
        foot(phone ? `+1 % in ν → k +${nu.toFixed(2)} %` : `+1 % in ν → k +${nu.toFixed(2)} % · +1 % in fission → k +${fi.toFixed(2)} %`, c.ink);
        if (v.ok && !phone) g.label("drag to turn", W - 8, 40, { color: c.faint, size: fs - 2, align: "right" });
        return;
      }

      if (mode === "check") {
        const m = phone ? 40 : 64, side = Math.min(W - m - 20, H - (phone ? 150 : 190)), x0 = phone ? m : (W - side) / 2 + 10, y0 = phone ? 58 : 76, L = 1700;
        const X = (p) => x0 + side * (p + L) / (2 * L), Y = (p) => y0 + side * (L - p) / (2 * L);
        g.ctx.save(); g.ctx.strokeStyle = c.line; g.ctx.lineWidth = 1; g.ctx.strokeRect(x0, y0, side, side); g.ctx.restore();
        [-1000, 0, 1000].forEach((p) => { g.line(X(p), y0, X(p), y0 + side, c.line, 1, 0.6, [2, 4]); g.line(x0, Y(p), x0 + side, Y(p), c.line, 1, 0.6, [2, 4]);
          g.label(String(p === 0 ? 0 : (p > 0 ? "+" : "−") + Math.abs(p)), X(p), y0 + side + 12, { color: c.soft, size: fs - 2 }); g.label(String(p === 0 ? 0 : (p > 0 ? "+" : "−") + Math.abs(p)), x0 - 6, Y(p), { color: c.soft, size: fs - 2, align: "right" }); });
        g.line(X(-L), Y(-L), X(L), Y(L), c.soft, 1.2, 0.8);
        const CC = { Godiva: c.warm, Jezebel: c.alpha, "Flattop-Pu": c.cool };
        D.ks.forEach(([cs, p, t], i) => g.dot(X(p), Y(t), phone ? 3.2 : 4.2, CC[cs], 0.9));
        g.label(phone ? "predicted Δk (pcm) →" : "predicted from sensitivities, Δk (pcm) →", x0 + side, y0 + side + 30, { color: c.soft, size: fs - 1, align: "right" });
        g.label(phone ? "re-solved ↑" : "re-solved in OpenMC ↑", x0, y0 - 14, { color: c.soft, size: fs - 1, align: "left" });
        const rms = {}; D.ks.forEach(([cs, p, t]) => { (rms[cs] = rms[cs] || []).push((p - t) ** 2); });
        Object.keys(rms).forEach((cs, i) => { const r = Math.sqrt(rms[cs].reduce((a, b) => a + b, 0) / rms[cs].length);
          const ly = y0 + 16 + i * (phone ? 16 : 20); g.dot(x0 + 14, ly, 4, CC[cs]); g.label(`${cs}: ${Math.round(r)} pcm rms`, x0 + 24, ly, { color: c.ink, size: fs - 1, align: "left", bg: true }); });
        g.label("15 of 15", x0 + side - 10, y0 + side - (phone ? 20 : 28), { color: c.fission, size: phone ? 20 : 28, weight: 600, serif: true, align: "right" });
        foot(phone ? "adjoint = direct to 1 part in 10,000" : "adjoint sensitivities match direct re-solves to 1 part in 10,000", c.ink);
        return;
      }

      if (mode === "core") {
        const v = WT.view3d("kcalc-core", g, buildCore);
        let hit = -1, info = null;
        if (v.ok) {
          v.orbit(fit(v, 66, 60), dt);
          // nearest pin top to the pointer (screen space)
          v.camera.updateMatrixWorld();
          if (S.hx != null) {
            const U = v.user, tmp = U.tmp; let best = phone ? 18 : 14;
            for (let k = 0; k < U.list.length; k++) { const [i, j, p] = U.list[k]; tmp.set(j + 0.5, p * PH, i + 0.5).project(v.camera);
              const sx = (tmp.x + 1) / 2 * W, sy = (1 - tmp.y) / 2 * H, dd = Math.hypot(sx - S.hx, sy - S.hy); if (dd < best) { best = dd; hit = k; } }
          }
          colorCore(v, hit); v.render();
          if (hit >= 0) { const [i, j, p, t] = v.user.list[hit], [px, py] = v.project(j + 0.5, p * PH, i + 0.5); info = { p, t, px, py }; }
          const lab = (x, y, z, s, col) => { const [px, py, vis] = v.project(x, y, z); if (vis) g.label(s, px, py, { color: col, size: fs - 1, weight: 600, bg: true }); };
          lab(8.5, 0, 8.5, "UO₂", c.soft); lab(25.5, 0, 25.5, "UO₂", c.soft); lab(25.5, 0, 8.5, "MOX", c.alpha); lab(8.5, 0, 25.5, "MOX", c.alpha); lab(42.5, 0, 17, "water", c.cool);
        } else {
          const n = NP + 17, s = Math.min((W - 40) / n, (H - 120) / n), x0 = (W - n * s) / 2, y0 = 50;
          g.ctx.save(); g.ctx.fillStyle = g.rgba(c.cool, 0.15); g.ctx.fillRect(x0, y0, n * s, n * s); g.ctx.restore();
          for (let i = 0; i < NP; i++) for (let j = 0; j < NP; j++) { const p = pins[i][j]; g.ctx.fillStyle = p > 0 ? "rgb(" + rgbRamp(c, clamp((p - P_LO) / (P_HI - P_LO), 0, 1)) + ")" : c.faint; g.ctx.fillRect(x0 + j * s, y0 + i * s, s * 0.9, s * 0.9);
            if (S.hx != null && p > 0 && S.hx >= x0 + j * s && S.hx < x0 + (j + 1) * s && S.hy >= y0 + i * s && S.hy < y0 + (i + 1) * s) info = { p, t: D.c5g7.map[i][j], px: x0 + (j + 0.5) * s, py: y0 + i * s }; }
        }
        // colour key
        { const kw = phone ? 120 : 170, kx = W - kw - 12, ky = phone ? 16 : 22;
          for (let i = 0; i < 24; i++) { g.ctx.fillStyle = "rgb(" + rgbRamp(c, i / 23) + ")"; g.ctx.fillRect(kx + (kw * i) / 24, ky, kw / 24 + 0.5, 7); }
          g.label(`×${P_LO}`, kx, ky + 18, { color: c.soft, size: fs - 2, align: "left" }); g.label(`×${P_HI} of mean`, kx + kw, ky + 18, { color: c.soft, size: fs - 2, align: "right" });
          g.label(phone ? "tap a pin" : "pin power · hover a pin", 12, ky + 4, { color: c.soft, size: fs - 1, align: "left" }); }
        if (info) {
          const fuel = info.t === 1 ? "UO₂" : info.t === 4 ? "MOX 4.3 %" : info.t === 2 ? "MOX 7.0 %" : "MOX 8.7 %";
          g.label(`${fuel} · ${info.p.toFixed(3)} × mean`, info.px, info.py - 20, { color: c.ink, size: fs, weight: 600, bg: true });
        }
        foot(phone ? "k 1.18636 vs 1.18655 · −19 pcm" : "k = 1.18636 against the reference 1.18655 (−19 pcm) · pin powers within 0.13 %", c.ink);
      }
    },
  });
  // the same ramp as the 3-D bars, for 2-D fills: cool -> photon -> proton
  function rgbRamp(c, t) {
    const a = WT.rgb01(c.cool), b = WT.rgb01(c.photon), d = WT.rgb01(c.proton), u = t < 0.5 ? t * 2 : (t - 0.5) * 2, p = t < 0.5 ? a : b, q = t < 0.5 ? b : d;
    return [0, 1, 2].map((i) => Math.round(255 * lerp(p[i], q[i], u))).join(",");
  }
})();
