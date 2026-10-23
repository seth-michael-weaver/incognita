/* Language layer. Loaded before everything else.
 * WT.lang: "en" (default) or a code in WT.LANGS, from ?lang= or the saved choice. Each language's files (js/i18n/<code>-*.js)
 * register into WT.L, the active language's pack (WT.es is the same object, so the Spanish files keep working):
 *   WT.L.ch[id]   = { num, title, short, lead, html }   chapter text (replaces the English fields)
 *   WT.L.labels   = { "english label": "etiqueta" }    canvas labels; numbers are templated as {#}
 *   WT.L.ui       = { key: "texto" }                   static page text (data-i18n="key") and kit UI strings
 *   WT.L.glossary = { key: { term, aliases, short, more, formula?, chapter? } }   same keys as WT.glossary
 * Adding a language: one row in LANGS, then js/i18n/<code>-*.js with the same keys as the es-*.js files.
 */
(function () {
  const WT = (window.WT = window.WT || {});
  // code: [button text, own name, locale, decimal comma]
  const LANGS = {
    en: ["EN", "English", "en-US", false],
    es: ["ES", "Español", "es-ES", true],
    de: ["DE", "Deutsch", "de-DE", true],
    pt: ["PT", "Português", "pt-PT", true],
    nl: ["NL", "Nederlands", "nl-NL", true],
    da: ["DA", "Dansk", "da-DK", true],
    ko: ["KO", "한국어", "ko-KR", false],
  };
  WT.LANGS = LANGS;
  WT.L = WT.es = WT.L || WT.es || { ch: {}, labels: {}, ui: {}, glossary: {} };
  let lang = "en";
  const q = /[?&]lang=([a-z]{2})\b/.exec(location.search);
  if (q && LANGS[q[1]]) lang = q[1];
  else { try { const s = localStorage.getItem("wt_lang"); if (s && LANGS[s]) lang = s; } catch (e) {} }
  WT.lang = lang;
  WT.tl = lang !== "en";   // a translation is active
  document.documentElement.lang = lang;
  WT.missing = new Set();
  const NUM = /[−-]?\d+(?:[.,]\d+)?/g;
  const cache = new Map();
  // translate one canvas label; untranslated strings fall back to English (and are recorded in WT.missing)
  WT.tr = function (s) {
    if (!WT.tl || s == null) return s;
    s = String(s); if (!/[A-Za-z]/.test(s)) return WT.dec(s);   // pure numbers/symbols: decimal comma only
    if (cache.has(s)) return cache.get(s);
    const L = WT.L.labels; let out = L[s];
    if (out === undefined) {
      const nums = s.match(NUM) || [], key = s.replace(NUM, "{#}"), t = L[key];
      if (t !== undefined) { let i = 0; out = t.replace(/\{#\}/g, () => WT.dec(nums[i++] ?? "")); }
    }
    if (out === undefined) { WT.missing.add(s.replace(NUM, "{#}")); out = s; }
    cache.set(s, out); return out;
  };
  // decimal comma where the language uses one (3.6 → 3,6); leaves English untouched
  WT.dec = (v) => (LANGS[WT.lang][3] ? String(v).replace(/(\d)\.(\d)/g, "$1,$2") : String(v));
  WT.loc = () => LANGS[WT.lang][2];
  WT.ui = (key, en) => (WT.tl && WT.L.ui[key] != null ? WT.L.ui[key] : en);
  // the ?lang= suffix that keeps the current language on a link ("" in English)
  WT.langQ = (sep) => (WT.tl ? (sep || "?") + "lang=" + WT.lang : "");
  // load this language's files for a page: WT.load(["ui", "data"]) writes <script src="js/i18n/<code>-ui.js?v=..">
  WT.load = function (files, v) {
    if (!WT.tl) return;
    files.forEach((f) => document.write('<script src="js/i18n/' + WT.lang + "-" + f + ".js?v=" + v + '"><\/script>'));
  };
  // apply the static page text (data-i18n, data-i18n-aria, data-i18n-ph) and the page title key
  WT.applyStatic = function (root, titleKey) {
    if (!WT.tl) return;
    if (titleKey && WT.L.ui[titleKey]) document.title = WT.L.ui[titleKey];
    const r = root || document;
    r.querySelectorAll("[data-i18n]").forEach((el) => { const t = WT.L.ui[el.dataset.i18n]; if (t != null) el.innerHTML = t; });
    document.querySelectorAll("[data-i18n-aria]").forEach((el) => { const t = WT.L.ui[el.dataset.i18nAria]; if (t != null) el.setAttribute("aria-label", t); });
    document.querySelectorAll("[data-i18n-ph]").forEach((el) => { const t = WT.L.ui[el.dataset.i18nPh]; if (t != null) el.setAttribute("placeholder", t); });
  };
  // links marked data-keep-lang carry ?lang= (before any #hash)
  WT.keepLang = function () {
    if (!WT.tl) return;
    document.querySelectorAll("a[data-keep-lang]").forEach((a) => {
      const h = a.getAttribute("href"); if (/[?&]lang=/.test(h)) return;
      const [path, hash] = h.split("#"); a.setAttribute("href", path + (path.includes("?") ? "&" : "?") + "lang=" + WT.lang + (hash != null ? "#" + hash : ""));
    });
  };
  // the language picker: a compact menu showing the current code (EN ▾); each language is named in itself
  WT.langSwitch = function () {
    const box = document.createElement("label"); box.className = "lang";
    const sel = document.createElement("select"); sel.setAttribute("aria-label", WT.ui("lang_label", "Language"));
    Object.entries(LANGS).forEach(([l, [code, name]]) => {
      const o = document.createElement("option"); o.value = l; o.lang = l; o.textContent = code + " · " + name; if (l === WT.lang) o.selected = true; sel.appendChild(o);
    });
    const face = document.createElement("span"); face.className = "lang-face"; face.setAttribute("aria-hidden", "true"); face.textContent = LANGS[WT.lang][0];
    sel.addEventListener("change", () => WT.setLang(sel.value));
    box.append(face, sel); return box;
  };
  // switch language: remember the choice and where the reader is, then reload
  WT.setLang = function (l) {
    try { localStorage.setItem("wt_lang", l); } catch (e) {}
    try { sessionStorage.setItem("wt_scroll", String(window.scrollY / Math.max(1, document.documentElement.scrollHeight))); } catch (e) {}
    const u = new URL(location.href); if (l === "en") u.searchParams.delete("lang"); else u.searchParams.set("lang", l); location.replace(u.toString());
  };
})();
