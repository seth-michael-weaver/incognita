/* Site header shared by every page (index, data, scoreboard): Spanish text for the header, links that keep the language,
 * the EN | ES switch, and the phone menu. Load after i18n.js and the page's Spanish files, before kit.js. */
(function () {
  "use strict";
  const head = document.querySelector(".site"); if (!head) return;
  const es = WT.lang === "es";
  if (es) {
    head.querySelectorAll("[data-i18n]").forEach((el) => { const t = WT.es.ui[el.dataset.i18n]; if (t != null) el.innerHTML = t; });
    document.querySelectorAll("[data-i18n-aria]").forEach((el) => { const t = WT.es.ui[el.dataset.i18nAria]; if (t != null) el.setAttribute("aria-label", t); });
    document.querySelectorAll("a[data-keep-lang]").forEach((a) => {
      const h = a.getAttribute("href"); if (/[?&]lang=/.test(h)) return;
      const [path, hash] = h.split("#"); a.setAttribute("href", path + (path.includes("?") ? "&" : "?") + "lang=es" + (hash != null ? "#" + hash : ""));
    });
  }
  // EN | ES
  const links = head.querySelector(".site-links"), box = document.createElement("div");
  box.className = "lang"; box.setAttribute("role", "group"); box.setAttribute("aria-label", es ? "Idioma" : "Language");
  [["en", "EN", "English"], ["es", "ES", "Español"]].forEach(([l, t, full]) => {
    const b = document.createElement("button"); b.type = "button"; b.textContent = t; b.title = full; b.lang = l; b.setAttribute("aria-pressed", String(WT.lang === l));
    if (WT.lang === l) b.className = "on"; else b.addEventListener("click", () => WT.setLang && WT.setLang(l));
    box.appendChild(b);
  });
  links.appendChild(box);
  // phones: the page links open from a menu button; any open menu closes on Escape or a click elsewhere
  const burger = head.querySelector(".site-burger");
  const close = () => { head.classList.remove("menu-open"); burger && burger.setAttribute("aria-expanded", "false"); const c = head.querySelector(".chap"); if (c) { c.classList.remove("open"); const m = c.querySelector(".toc-menu"); m && m.setAttribute("aria-expanded", "false"); } };
  if (burger) burger.addEventListener("click", (e) => { e.stopPropagation(); const c = head.querySelector(".chap"); if (c) c.classList.remove("open"); const o = head.classList.toggle("menu-open"); burger.setAttribute("aria-expanded", String(o)); });
  document.addEventListener("click", (e) => { if (!head.contains(e.target)) close(); });
  document.addEventListener("keydown", (e) => { if (e.key === "Escape") close(); });
  links.addEventListener("click", (e) => { if (e.target.closest("a")) close(); });
})();
