/* Lesson index on topics.html (runs after WT.start): one card per lesson, grouped by part as the page orders them,
 * each with its number and level; chips filter by level. Built from the page, so adding a lesson needs no edit here. */
(function () {
  "use strict";
  const box = document.querySelector(".tp-parts"), chips = document.querySelector(".tp-filter"); if (!box) return;
  const T = (k, en) => (WT.ui ? WT.ui(k, en) : en);
  const LV = [T("lvl0", "Intro"), T("lvl1", "Intermediate"), T("lvl2", "Advanced"), T("lvl3", "Expert")];
  const LEVEL = { critical: 1, doppler: 1, fusion: 0, gamow: 1, tokamak: 2, blanket: 3 }; // moved chapters (as in kit.js)
  const parts = []; let cur = null;
  document.querySelectorAll("main > .part-head, main > .chapter").forEach((el) => {
    if (el.classList.contains("part-head")) { cur = { k: el.querySelector(".part-kicker").textContent, h: el.querySelector("h2").textContent, id: el.id, items: [] }; parts.push(cur); return; }
    const id = el.dataset.ch, m = WT.mods[id]; if (!m || !m.title || !cur) return;
    const lv = m.level != null ? m.level : LEVEL[id];
    cur.items.push({ id, lv, n: (m.num || "").replace(/[^0-9]/g, ""), title: m.title, short: m.short || "" });
  });
  box.innerHTML = parts.filter((p) => p.items.length).map((p) => `<div class="tp-part"><div class="tp-part-h"><span class="part-kicker">${p.k}</span><a href="#${p.id}">${p.h}</a></div><ol class="tp-cards">${p.items.map((c) =>
    `<li data-lv="${c.lv}"><a class="tp-card l${c.lv}" href="#${c.id}"><span class="tp-n">${c.n}</span><b>${c.title}</b><span class="lvl l${c.lv}">${LV[c.lv]}</span></a></li>`).join("")}</ol></div>`).join("");
  const opts = [["all", T("in_all", "All")], ["0", LV[0]], ["1", LV[1]], ["2", LV[2]], ["3", LV[3]]];
  chips.innerHTML = opts.map(([v, t]) => `<button type="button" data-v="${v}" aria-pressed="${v === "all"}">${t}</button>`).join("");
  chips.addEventListener("click", (e) => {
    const b = e.target.closest("button"); if (!b) return; const v = b.dataset.v;
    chips.querySelectorAll("button").forEach((x) => x.setAttribute("aria-pressed", String(x === b)));
    box.querySelectorAll(".tp-cards li").forEach((li) => (li.hidden = v !== "all" && li.dataset.lv !== v));
    box.querySelectorAll(".tp-part").forEach((p) => (p.hidden = !p.querySelector("li:not([hidden])")));
  });
})();
// the page title (kit.js sets the main page's; this page has its own)
if (window.WT && WT.tl && WT.L.ui.tp_title) document.title = WT.L.ui.tp_title;
