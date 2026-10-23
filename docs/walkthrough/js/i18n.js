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
  // code: [button text, own name, locale, decimal comma, flag (flags/<cc>.svg)]
  const LANGS = {
    en: ["EN", "English", "en-US", false, "us"],
    es: ["ES", "Español", "es-ES", true, "es"],
    de: ["DE", "Deutsch", "de-DE", true, "de"],
    pt: ["PT", "Português", "pt-PT", true, "pt"],
    nl: ["NL", "Nederlands", "nl-NL", true, "nl"],
    da: ["DA", "Dansk", "da-DK", true, "dk"],
    ko: ["KO", "한국어", "ko-KR", false, "kr"],
    zh: ["ZH", "简体中文", "zh-CN", false, "cn"],
    ja: ["JA", "日本語", "ja-JP", false, "jp"],
    fr: ["FR", "Français", "fr-FR", true, "fr"],
    ru: ["RU", "Русский", "ru-RU", true, "ru"],
    it: ["IT", "Italiano", "it-IT", true, "it"],
    hi: ["HI", "हिन्दी", "hi-IN", false, "in"],
    ar: ["AR", "العربية", "ar", false, "sa"],   // right to left: html dir="rtl" (diagrams stay left to right)
  };
  // languages shipped so far (a language is listed once all its js/i18n/<code>-*.js files are in)
  const LIVE = ["en", "es", "pt", "da", "ko", "de"];
  Object.keys(LANGS).forEach((l) => { if (!LIVE.includes(l)) delete LANGS[l]; });
  WT.LANGS = LANGS;
  WT.L = WT.es = WT.L || WT.es || { ch: {}, labels: {}, ui: {}, glossary: {} };
  let lang = "en";
  const q = /[?&]lang=([a-z]{2})\b/.exec(location.search);
  if (q && LANGS[q[1]]) lang = q[1];
  else { try { const s = localStorage.getItem("wt_lang"); if (s && LANGS[s]) lang = s; } catch (e) {} }
  WT.lang = lang;
  WT.tl = lang !== "en";   // a translation is active
  document.documentElement.lang = lang;
  WT.rtl = lang === "ar";
  document.documentElement.dir = WT.rtl ? "rtl" : "ltr";
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
  // the language picker: a pill with the current flag and code (🇬🇧 EN ▾) that opens a list of every language, each with its
  // flag and its own name. A listbox (not a native <select>) so the flags show; arrows / Home / End move, Enter picks, Esc closes.
  const flag = (l) => `<img class="lang-flag" src="flags/${LANGS[l][4]}.svg" alt="" width="20" height="15" decoding="async">`;
  WT.langSwitch = function () {
    const box = document.createElement("div"); box.className = "lang";
    const btn = document.createElement("button"); btn.type = "button"; btn.className = "lang-btn";
    btn.setAttribute("aria-haspopup", "listbox"); btn.setAttribute("aria-expanded", "false");
    btn.setAttribute("aria-label", WT.ui("lang_label", "Language") + ": " + LANGS[WT.lang][1]);
    btn.innerHTML = `${flag(WT.lang)}<span class="lang-code">${LANGS[WT.lang][0]}</span><svg class="lang-chev" viewBox="0 0 10 6" width="10" height="6" aria-hidden="true"><path d="M1 1l4 4 4-4" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/></svg>`;
    const list = document.createElement("ul"); list.className = "lang-list"; list.setAttribute("role", "listbox"); list.tabIndex = -1;
    list.setAttribute("aria-label", WT.ui("lang_label", "Language"));
    const items = Object.keys(LANGS).map((l) => {
      const li = document.createElement("li"); li.setAttribute("role", "option"); li.dataset.lang = l; li.lang = l; li.tabIndex = -1;
      li.setAttribute("aria-selected", String(l === WT.lang));
      li.innerHTML = `${flag(l)}<span class="lang-name">${LANGS[l][1]}</span><span class="lang-iso">${LANGS[l][0]}</span>`;
      li.addEventListener("click", () => pick(l)); list.appendChild(li); return li;
    });
    const isOpen = () => box.classList.contains("open");
    const open = () => { box.classList.add("open"); btn.setAttribute("aria-expanded", "true"); (items.find((i) => i.dataset.lang === WT.lang) || items[0]).focus(); };
    const close = (refocus) => { if (!isOpen()) return; box.classList.remove("open"); btn.setAttribute("aria-expanded", "false"); if (refocus) btn.focus(); };
    const pick = (l) => { close(true); if (l !== WT.lang) WT.setLang(l); };
    btn.addEventListener("click", (e) => { e.stopPropagation(); isOpen() ? close(true) : open(); });
    btn.addEventListener("keydown", (e) => { if (e.key === "ArrowDown" || e.key === "ArrowUp") { e.preventDefault(); open(); } });
    list.addEventListener("keydown", (e) => {
      const i = items.indexOf(document.activeElement), n = items.length;
      const go = (j) => { e.preventDefault(); items[(j + n) % n].focus(); };
      if (e.key === "ArrowDown") go(i + 1); else if (e.key === "ArrowUp") go(i - 1);
      else if (e.key === "Home") go(0); else if (e.key === "End") go(n - 1);
      else if (e.key === "Enter" || e.key === " ") { e.preventDefault(); if (i >= 0) pick(items[i].dataset.lang); }
      else if (e.key === "Escape") { e.preventDefault(); e.stopPropagation(); close(true); }
      else if (e.key === "Tab") close(false);
    });
    list.addEventListener("click", (e) => e.stopPropagation());
    document.addEventListener("click", () => close(false));
    box.append(btn, list); return box;
  };
  // switch language: remember the choice and where the reader is, then reload
  WT.setLang = function (l) {
    try { localStorage.setItem("wt_lang", l); } catch (e) {}
    try { sessionStorage.setItem("wt_scroll", String(window.scrollY / Math.max(1, document.documentElement.scrollHeight))); } catch (e) {}
    const u = new URL(location.href); if (l === "en") u.searchParams.delete("lang"); else u.searchParams.set("lang", l); location.replace(u.toString());
  };
})();
