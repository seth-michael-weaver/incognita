/* Hero worker: runs js/ch/intro.js unchanged on an OffscreenCanvas, behind a tiny stand-in for the few page objects the
 * hero reads (its canvas, the title box, sizes, scroll, visibility). Input arrives from the page (intro.js heroWorker). */
"use strict";
self.__heroWorker = true;
const S = { w: 1, h: 1, dpr: 1, copyTop: 0, firstTop: 0, heroTop: 0, heroH: 1, hidden: false, og: false, tr: {} };
const H = { hero: {}, fire: {}, win: {}, vis: null, io: null };
let canvas = null;
const fakeCv = {
  getContext: (k, o) => canvas.getContext(k, o),
  getBoundingClientRect: () => ({ left: 0, top: 0, width: S.w, height: S.h, right: S.w, bottom: S.h }),
  get width() { return canvas.width; }, set width(v) { canvas.width = v; },
  get height() { return canvas.height; }, set height(v) { canvas.height = v; },
  style: {}, setAttribute() {},
};
const copy = { get offsetTop() { return S.copyTop; }, get firstElementChild() { return { offsetTop: S.firstTop }; }, style: {} };
const fire = { addEventListener: (t, f) => { H.fire[t] = f; } };
const hero = {
  querySelector: (q) => (q === ".hero-cv" ? fakeCv : q === ".hero-copy" ? copy : q === ".fire-btn" ? fire : null),
  addEventListener: (t, f) => { H.hero[t] = f; },
  getBoundingClientRect: () => ({ top: S.heroTop, height: S.heroH }),
};
self.document = {
  querySelector: (q) => (q === ".hero" ? hero : null),
  createElement: () => new OffscreenCanvas(1, 1),
  get hidden() { return S.hidden; },
  body: { classList: { contains: (c) => c === "og" && S.og, add() {} } },
  addEventListener: (t, f) => { if (t === "visibilitychange") H.vis = f; },
};
self.window = self;
Object.defineProperty(self, "devicePixelRatio", { get: () => S.dpr, configurable: true });
self.matchMedia = () => ({ matches: false, addEventListener() {} });
const addEv = self.addEventListener.bind(self);
self.addEventListener = (t, f, o) => { if (t === "resize" || t === "scroll") H.win[t] = f; else addEv(t, f, o); };
self.IntersectionObserver = class { constructor(cb) { H.io = cb; } observe() {} disconnect() {} };
if (typeof self.requestAnimationFrame !== "function") self.requestAnimationFrame = (cb) => setTimeout(() => cb(performance.now()), 16);
self.WT = { tr: (s) => S.tr[s] || s };

async function loadFonts(hrefs) { // the caption's serif: the same Google Fonts files the page uses
  try {
    for (const href of hrefs) {
      const css = await (await fetch(href)).text();
      for (const m of css.matchAll(/@font-face\s*{([^}]*)}/g)) {
        const b = m[1], fam = /font-family:\s*'([^']+)'/.exec(b), src = /src:\s*url\(([^)]+)\)/.exec(b);
        if (!fam || !src || fam[1] !== "Source Serif 4") continue;
        const wt = (/font-weight:\s*([\d ]+);/.exec(b) || [])[1], st = (/font-style:\s*(\w+)/.exec(b) || [])[1], ur = (/unicode-range:\s*([^;]+);/.exec(b) || [])[1];
        const f = new FontFace(fam[1], `url(${src[1]})`, { weight: wt || "400", style: st || "normal", unicodeRange: ur || "U+0-10FFFF" });
        self.fonts.add(f); f.load().catch(() => {});
      }
    }
  } catch (e) { /* the caption falls back to Georgia */ }
}

self.onmessage = (ev) => {
  const m = ev.data;
  if (m.t === "init") {
    canvas = m.canvas; Object.assign(S, m.size, m.scroll); S.og = m.og; S.tr = m.tr || {};
    if (self.fonts && m.fonts) loadFonts(m.fonts);
    importScripts("intro.js?v=" + ((/[?&]v=(\d+)/.exec(location.search) || [])[1] || "0"));
    return;
  }
  if (!canvas) return;
  if (m.t === "move" && H.hero.pointermove) H.hero.pointermove({ clientX: m.x, clientY: m.y });
  else if (m.t === "leave" && H.hero.pointerleave) H.hero.pointerleave({});
  else if (m.t === "down" && H.hero.pointerdown) H.hero.pointerdown({ clientX: m.x, clientY: m.y, target: { closest: () => null } });
  else if (m.t === "fire" && H.fire.click) H.fire.click({});
  else if (m.t === "resize") { Object.assign(S, m.size); H.win.resize && H.win.resize(); }
  else if (m.t === "scroll") { Object.assign(S, m.scroll); H.win.scroll && H.win.scroll(); }
  else if (m.t === "vis" && H.io) H.io([{ isIntersecting: m.v }]);
  else if (m.t === "hidden") { S.hidden = m.v; H.vis && H.vis(); }
};
