/* Lesson index on topics.html (runs after WT.start): a plain list like a glossary (no boxes), grouped by
 * part as the page orders them. Each row: number, title, the first sentence of the lesson (from the page, so it is already
 * in the reader's language) and the level; chips filter by level. Built from the page, so adding a lesson needs no edit here. */
(function () {
  "use strict";
  const box = document.querySelector(".tp-parts"), chips = document.querySelector(".tp-filter"); if (!box) return;
  const T = (k, en) => (WT.ui ? WT.ui(k, en) : en);
  const LV = [T("lvl0", "Intro"), T("lvl1", "Intermediate"), T("lvl2", "Advanced"), T("lvl3", "Expert")];
  const LEVEL = { critical: 1, doppler: 1, fusion: 0, gamow: 1, tokamak: 2, blanket: 3 }; // moved chapters (as in kit.js)
  const esc = (s) => s.replace(/&/g, "&amp;").replace(/</g, "&lt;");
  const first = (el) => { // the lesson's first sentence: its lead, else its first paragraph
    const p = el.querySelector(".lead, .step p"); if (!p) return "";
    const t = p.textContent.replace(/\s+/g, " ").trim(), m = t.match(/^.+?[.!?。！？](?=\s|$)/);
    const s = m ? m[0] : t; return s.length > 170 ? s.slice(0, 165).replace(/\s+\S*$/, "") + "…" : s;
  };
  const parts = []; let cur = null;
  document.querySelectorAll("main > .part-head, main > .chapter").forEach((el) => {
    if (el.classList.contains("part-head")) { cur = { k: el.querySelector(".part-kicker").textContent, h: el.querySelector("h2").textContent, id: el.id, items: [] }; parts.push(cur); return; }
    const id = el.dataset.ch, m = WT.mods[id]; if (!m || !m.title || !cur) return;
    const lv = m.level != null ? m.level : LEVEL[id];
    cur.items.push({ id, lv, n: (m.num || "").replace(/[^0-9]/g, ""), title: m.title, d: first(el) });
  });
  box.innerHTML = parts.filter((p) => p.items.length).map((p) => `<div class="tp-part"><h3 class="tp-part-h"><span class="part-kicker">${esc(p.k)}</span><a href="#${p.id}">${esc(p.h)}</a></h3><ol class="tp-list">${p.items.map((c) =>
    `<li data-lv="${c.lv}"><a href="#${c.id}"><span class="tp-n">${c.n}</span><span class="tp-t"><b>${esc(c.title)}</b>${c.d ? `<span class="tp-d">${esc(c.d)}</span>` : ""}</span><span class="lvl l${c.lv}">${LV[c.lv]}</span></a></li>`).join("")}</ol></div>`).join("");
  const opts = [["all", T("in_all", "All")], ["0", LV[0]], ["1", LV[1]], ["2", LV[2]], ["3", LV[3]]];
  chips.innerHTML = opts.map(([v, t]) => `<button type="button" data-v="${v}" aria-pressed="${v === "all"}">${t}</button>`).join("");
  chips.addEventListener("click", (e) => {
    const b = e.target.closest("button"); if (!b) return; const v = b.dataset.v;
    chips.querySelectorAll("button").forEach((x) => x.setAttribute("aria-pressed", String(x === b)));
    box.querySelectorAll(".tp-list li").forEach((li) => (li.hidden = v !== "all" && li.dataset.lv !== v));
    box.querySelectorAll(".tp-part").forEach((p) => (p.hidden = !p.querySelector("li:not([hidden])")));
  });
})();
// the page title (kit.js sets the main page's; this page has its own)
if (window.WT && WT.tl && WT.L.ui.tp_title) document.title = WT.L.ui.tp_title;
