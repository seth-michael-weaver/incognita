/* Language layer. Loaded before everything else.
 * WT.lang: "en" (default) or "es", from ?lang= or the saved choice. Spanish files (js/i18n/es-*.js) register:
 *   WT.es.ch[id]   = { num, title, short, lead, html }   chapter text (replaces the English fields)
 *   WT.es.labels   = { "english label": "etiqueta" }    canvas labels; numbers are templated as {#}
 *   WT.es.ui       = { key: "texto" }                   static page text (data-i18n="key") and kit UI strings
 *   WT.es.glossary = { key: { term, aliases, short, more, formula?, chapter? } }   same keys as WT.glossary
 */
(function () {
  const WT = (window.WT = window.WT || {});
  WT.es = WT.es || { ch: {}, labels: {}, ui: {}, glossary: {} };
  let lang = "en";
  const q = /[?&]lang=(en|es)\b/.exec(location.search);
  if (q) lang = q[1];
  else { try { const s = localStorage.getItem("wt_lang"); if (s === "es" || s === "en") lang = s; } catch (e) {} }
  WT.lang = lang;
  document.documentElement.lang = lang;
  WT.missing = new Set();
  const NUM = /[−-]?\d+(?:[.,]\d+)?/g;
  const cache = new Map();
  // translate one canvas label; untranslated strings fall back to English (and are recorded in WT.missing)
  WT.tr = function (s) {
    if (WT.lang !== "es" || s == null) return s;
    s = String(s); if (!/[A-Za-z]/.test(s)) return WT.dec(s);   // pure numbers/symbols: decimal comma only
    if (cache.has(s)) return cache.get(s);
    const L = WT.es.labels; let out = L[s];
    if (out === undefined) {
      const nums = s.match(NUM) || [], key = s.replace(NUM, "{#}"), t = L[key];
      if (t !== undefined) { let i = 0; out = t.replace(/\{#\}/g, () => WT.dec(nums[i++] ?? "")); }
    }
    if (out === undefined) { WT.missing.add(s.replace(NUM, "{#}")); out = s; }
    cache.set(s, out); return out;
  };
  // decimal comma in Spanish (3.6 → 3,6); leaves English untouched
  WT.dec = (v) => (WT.lang === "es" ? String(v).replace(/(\d)\.(\d)/g, "$1,$2") : String(v));
  WT.loc = () => (WT.lang === "es" ? "es-ES" : "en-US");
  WT.ui = (key, en) => (WT.lang === "es" && WT.es.ui[key] != null ? WT.es.ui[key] : en);
  // switch language: remember the choice and where the reader is, then reload
  WT.setLang = function (l) {
    try { localStorage.setItem("wt_lang", l); } catch (e) {}
    try { sessionStorage.setItem("wt_scroll", String(window.scrollY / Math.max(1, document.documentElement.scrollHeight))); } catch (e) {}
    const u = new URL(location.href); u.searchParams.set("lang", l); location.replace(u.toString());
  };
})();
