/* Site header shared by every page (index, data, scoreboard): translated header text, links that keep the language,
 * the language picker, and the phone menu. Load after i18n.js and the page's language files, before kit.js. */
(function () {
  "use strict";
  const head = document.querySelector(".site"); if (!head) return;
  // "Instructors" link (every page): the teaching guide, placed before GitHub
  const sl = head.querySelector(".site-links");
  if (sl && !sl.querySelector('a[href^="instructors.html"]')) {
    const a = document.createElement("a"); a.href = "instructors.html"; a.dataset.keepLang = ""; a.dataset.i18n = "nav_teach"; a.textContent = WT.ui("nav_teach", "Instructors");
    if (/\/instructors(\.html)?$/.test(location.pathname)) { a.className = "here"; a.setAttribute("aria-current", "page"); }
    sl.insertBefore(a, sl.querySelector(".gh"));
  }
  if (WT.tl) {
    head.querySelectorAll("[data-i18n]").forEach((el) => { const t = WT.L.ui[el.dataset.i18n]; if (t != null) el.innerHTML = t; });
    document.querySelectorAll("[data-i18n-aria]").forEach((el) => { const t = WT.L.ui[el.dataset.i18nAria]; if (t != null) el.setAttribute("aria-label", t); });
    WT.keepLang();
  }
  // language picker
  const links = head.querySelector(".site-links");
  links.appendChild(WT.langSwitch());
  // phones: the page links open from a menu button; any open menu closes on Escape or a click elsewhere
  const burger = head.querySelector(".site-burger");
  const close = () => { head.classList.remove("menu-open"); burger && burger.setAttribute("aria-expanded", "false"); const c = head.querySelector(".chap"); if (c) { c.classList.remove("open"); const m = c.querySelector(".toc-menu"); m && m.setAttribute("aria-expanded", "false"); } };
  if (burger) burger.addEventListener("click", (e) => { e.stopPropagation(); const c = head.querySelector(".chap"); if (c) c.classList.remove("open"); const o = head.classList.toggle("menu-open"); burger.setAttribute("aria-expanded", String(o)); });
  document.addEventListener("click", (e) => { if (!head.contains(e.target)) close(); });
  document.addEventListener("keydown", (e) => { if (e.key === "Escape") close(); });
  links.addEventListener("click", (e) => { if (e.target.closest("a")) close(); });
})();
