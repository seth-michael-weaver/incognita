/* 3D layer for the walkthrough (WebGL through three.js r160, self-hosted in js/vendor/three, MIT licence).
 * A chapter asks for a 3D view inside its frame():
 *     const v = WT.view3d("structure-nucleus", g, (T, v) => { ...build meshes into v.scene once... });
 *     if (!v.ok) { ...draw the 2D version...; return; }        // no WebGL, still loading, too slow, or ?no3d
 *     v.orbit(radius); ...update meshes...; v.render();
 *     then draw labels with g.label as usual: the 2D canvas is transparent and sits ON TOP of the 3D canvas.
 * Rules learned from the hero (Edge freeze 2026-10-26): render only while the chapter calls (it stops when the chapter is off screen
 * or on a 2D step), pause in hidden tabs, cap the pixel ratio, time every frame and fall back to 2D for good if the median of the
 * last 40 frames exceeds 45 ms. three.js loads only on the first view3d() call.
 * v.orbit(): drag on the drawing (mouse or one finger) turns the camera; it eases back to a slow spin when left alone.
 * v.col(name): a THREE.Color from the site's CSS colour tokens (ink, proton, neutron, ...), refreshed when the theme changes.
 * mesh.sync() (nucleus3d meshes): re-colour after a light/dark theme switch; call once per frame.
 * v.project(x, y, z): screen coordinates (CSS px in the 2D canvas) of a world point, for placing g.label over 3D objects. */
(function () {
  const WT = (window.WT = window.WT || {});
  let T = null, loading = null, failed = false;
  const supported = (() => { try { const c = document.createElement("canvas"); return !!(c.getContext("webgl2") || c.getContext("webgl")); } catch (e) { return false; } })();
  const off = /[?&]no3d\b/.test(location.search);
  function load() {
    if (T || failed || loading) return;
    loading = import(new URL("js/vendor/three/three.module.min.js?v=160", document.baseURI).href)
      .then((m) => { T = m; }).catch((e) => { failed = true; console.warn("3D unavailable, using 2D", e); });
  }
  const views = new Map();
  let themeGen = 0;
  if (window.matchMedia) { const mq = matchMedia("(prefers-color-scheme: dark)"); mq.addEventListener && mq.addEventListener("change", () => themeGen++); }
  new MutationObserver(() => themeGen++).observe(document.documentElement, { attributes: true, attributeFilter: ["data-theme", "class"] });

  function create(key, cv2, build) {
    const stage = cv2.parentElement, canvas = document.createElement("canvas");
    canvas.className = "stage3d"; canvas.setAttribute("aria-hidden", "true");
    Object.assign(canvas.style, { position: "absolute", left: "0", top: "0", zIndex: "0", pointerEvents: "none", display: "none" });
    if (getComputedStyle(stage).position === "static") stage.style.position = "relative";
    cv2.style.position = "relative"; cv2.style.zIndex = "1";
    stage.insertBefore(canvas, cv2);
    let renderer;
    try { renderer = new T.WebGLRenderer({ canvas, antialias: true, alpha: true, powerPreference: "default" }); }
    catch (e) { canvas.remove(); return { ok: false, dead: true }; }
    renderer.setClearColor(0x000000, 0);
    const scene = new T.Scene(), camera = new T.PerspectiveCamera(40, 1, 0.1, 2000);
    scene.add(new T.HemisphereLight(0xffffff, 0x445566, 1.1));
    const sun = new T.DirectionalLight(0xffffff, 1.6); sun.position.set(3, 5, 4); scene.add(sun);
    const v = { ok: true, key, T, scene, camera, renderer, canvas, stage, W: 0, H: 0, last: 0, times: [], dead: false,
      yaw: 0.6, pitch: 0.35, vyaw: 0, vpitch: 0, drag: null, idle: 0, spin: 0.12, target: new T.Vector3(0, 0, 0), cols: {}, gen: -1, user: {} };
    // drag to orbit: listen on the stage (the 2D canvas above passes events up)
    const down = (e) => { if (!v.visible) return; v.drag = { x: e.clientX, y: e.clientY }; v.idle = 0; };
    const move = (e) => { if (!v.drag) return; const dx = e.clientX - v.drag.x, dy = e.clientY - v.drag.y; v.drag = { x: e.clientX, y: e.clientY };
      v.vyaw = -dx * 0.008; v.vpitch = dy * 0.006; v.yaw += v.vyaw; v.pitch = Math.max(-1.35, Math.min(1.35, v.pitch + v.vpitch)); };
    const up = () => { v.drag = null; };
    // phones: vertical swipes keep scrolling the page (touch-action pan-y), horizontal drags turn the view
    stage.style.touchAction = "pan-y";
    stage.addEventListener("pointerdown", down); window.addEventListener("pointermove", move); window.addEventListener("pointerup", up); window.addEventListener("pointercancel", up);
    v.col = (name) => {
      if (v.gen !== themeGen) { v.gen = themeGen; v.cols = {}; }
      if (!v.cols[name]) { const s = getComputedStyle(document.documentElement).getPropertyValue("--" + name).trim() || "#888"; v.cols[name] = new T.Color(s); }
      return v.cols[name];
    };
    v.orbit = (radius, dt = 1 / 60) => {
      if (!v.drag) { v.idle += dt; v.yaw += v.vyaw; v.vyaw *= 0.92; v.vpitch *= 0.9; if (v.idle > 2.5) v.yaw += v.spin * dt; }
      const cp = Math.cos(v.pitch);
      camera.position.set(v.target.x + radius * cp * Math.sin(v.yaw), v.target.y + radius * Math.sin(v.pitch), v.target.z + radius * cp * Math.cos(v.yaw));
      camera.lookAt(v.target);
    };
    v.project = (x, y, z) => { const p = new T.Vector3(x, y, z).project(camera); return [(p.x + 1) / 2 * v.W, (1 - p.y) / 2 * v.H, p.z < 1]; };
    v.render = () => {
      if (v.dead) return; const t0 = performance.now(); renderer.render(scene, camera); const dtm = performance.now() - t0;
      v.times.push(dtm); if (v.times.length > 40) v.times.shift();
      if (v.times.length === 40) { const s = [...v.times].sort((a, b) => a - b); if (s[20] > 45) kill(v, "slow (" + s[20].toFixed(0) + " ms per frame)"); }
    };
    try { build(T, v); } catch (e) { console.error("3D build", key, e); kill(v, "build error"); }
    return v;
  }
  function kill(v, why) { v.dead = true; v.ok = false; if (v.canvas) v.canvas.style.display = "none"; console.info("3D view", v.key, "off:", why); mark(v.key, "off: " + why); }
  // a small status note on <html data-v3d="key=state; ..."> for checking a page without devtools
  const states = {}; function mark(key, st) { states[key] = st; document.documentElement.dataset.v3d = Object.entries(states).map(([k, s]) => k + "=" + s).join("; "); }

  WT.view3d = function (key, g, build) {
    if (!supported || failed || off) { if (!states[key]) mark(key, !supported ? "no WebGL" : failed ? "load failed" : "off by ?no3d"); return { ok: false }; }
    load(); if (!T) return { ok: false, loading: true };
    let v = views.get(key); const cv2 = g.ctx.canvas;
    if (!v) { v = create(key, cv2, build); views.set(key, v); mark(key, v.ok ? "ok" : "failed"); }
    if (!v.ok || v.dead) return { ok: false };
    if (v.W !== g.W || v.H !== g.H) {
      v.W = g.W; v.H = g.H; v.renderer.setPixelRatio(Math.min(1.5, window.devicePixelRatio || 1)); v.renderer.setSize(g.W, g.H, false);
      v.canvas.style.width = g.W + "px"; v.canvas.style.height = g.H + "px"; v.camera.aspect = g.W / Math.max(1, g.H); v.camera.updateProjectionMatrix();
    }
    v.last = performance.now(); v.visible = true; v.canvas.style.display = "block"; v.frames = (v.frames || 0) + 1;
    if (v.frames % 30 === 1) mark(key, `ok ${v.W}x${v.H} frames ${v.frames} draw ${(v.times[v.times.length - 1] || 0).toFixed(1)} ms`);
    return v;
  };
  // hide views that their chapter stopped asking for (other step, off screen) so they cost nothing
  (function sweep() {
    const now = performance.now();
    views.forEach((v) => { if (v.canvas && v.visible && now - v.last > 250) { v.visible = false; v.canvas.style.display = "none"; } });
    setTimeout(sweep, 200);
  })();
  // shared builder: a nucleus of N + Z nucleon spheres (instanced), radius R, quadrupole deformation beta (prolate along y)
  WT.nucleus3d = function (T, v, { N = 40, Z = 30, R = 1, beta = 0, seed = 7 } = {}) {
    const n = N + Z, geo = new T.SphereGeometry(1, 18, 14), mat = new T.MeshStandardMaterial({ roughness: 0.45, metalness: 0.05 });
    const mesh = new T.InstancedMesh(geo, mat, n), r = WT.util.rng(seed), pts = [], m = new T.Matrix4(), col = new T.Color();
    for (let i = 0; i < n; i++) {
      // even spread inside a sphere (golden-spiral shells), then squash/stretch for beta
      const u = (i + 0.5) / n, rr = Math.cbrt(u) * 0.9, th = Math.acos(1 - 2 * ((i * 0.618034) % 1)), ph = i * 2.39996 + r() * 0.2;
      pts.push([rr * Math.sin(th) * Math.cos(ph), rr * Math.cos(th), rr * Math.sin(th) * Math.sin(ph), r()]);
    }
    const isP = pts.map((_, i) => i < Z); for (let i = n - 1; i > 0; i--) { const j = Math.floor(r() * (i + 1)); [isP[i], isP[j]] = [isP[j], isP[i]]; }
    const rb = R / Math.cbrt(n) * 0.98;
    mesh.userData = { pts, isP, rb, R, beta, n };
    mesh.setPose = (beta = 0, t = 0, jig = 0) => {
      const sx = 1 - beta * 0.5, sy = 1 + beta;
      for (let i = 0; i < n; i++) { const [x, y, z, ph] = pts[i];
        m.makeScale(rb, rb, rb); m.setPosition(R * (x * sx + Math.sin(t * 3.1 + ph * 20) * jig), R * (y * sy + Math.cos(t * 2.7 + ph * 17) * jig), R * (z * sx + Math.sin(t * 2.3 + ph * 11) * jig));
        mesh.setMatrixAt(i, m); }
      mesh.instanceMatrix.needsUpdate = true;
    };
    mesh.setColors = () => { for (let i = 0; i < n; i++) mesh.setColorAt(i, col.copy(v.col(isP[i] ? "proton" : "neutron"))); mesh.instanceColor.needsUpdate = true; mesh.gen = v.gen; };
    mesh.sync = () => { v.col("ink"); if (mesh.gen !== v.gen) mesh.setColors(); };   // re-colour after a light/dark switch
    mesh.setPose(beta); mesh.setColors();
    return mesh;
  };
})();
