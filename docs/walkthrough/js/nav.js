/* Site header shared by every page (index, data, scoreboard): translated header text, links that keep the language,
 * the language picker, and the phone menu. Load after i18n.js and the page's language files, before kit.js. */
(function () {
  "use strict";
  const head = document.querySelector(".site"); if (!head) return;
  // "Instructors" link (every page): the teaching guide, placed before GitHub
  const sl = head.querySelector(".site-links");
  // "Pipeline" link hidden for now (Seth, 2026-10-27); pipeline.html stays reachable by URL. Uncomment to restore.
  // if (sl && !sl.querySelector('a[href^="pipeline.html"]')) {
  //   const a = document.createElement("a"); a.href = "pipeline.html"; a.dataset.keepLang = ""; a.dataset.i18n = "nav_pipe"; a.textContent = WT.ui("nav_pipe", "Pipeline");
  //   if (/\/pipeline(\.html)?$/.test(location.pathname)) { a.className = "here"; a.setAttribute("aria-current", "page"); }
  //   const b = sl.querySelector('a[href^="scoreboard.html"]');
  //   sl.insertBefore(a, b ? b.nextSibling : sl.querySelector(".gh"));
  // }
  // "More topics" link (every page): lessons beside the engine story (reactors, radiation, fusion), placed after Scoreboard
  if (sl && !head.querySelector('[data-i18n="nav_topics"]')) { // topics.html has it as its chapter menu instead
    const a = document.createElement("a"); a.href = "topics.html"; a.dataset.keepLang = ""; a.dataset.i18n = "nav_topics"; a.textContent = WT.ui("nav_topics", "The Playground");
    const b = sl.querySelector('a[href^="scoreboard.html"]');
    sl.insertBefore(a, b ? b.nextSibling : sl.querySelector(".gh"));
  }
  if (sl && !sl.querySelector('a[href^="instructors.html"]')) {
    const a = document.createElement("a"); a.href = "instructors.html"; a.dataset.keepLang = ""; a.dataset.i18n = "nav_teach"; a.textContent = WT.ui("nav_teach", "Instructors");
    if (/\/instructors(\.html)?$/.test(location.pathname)) { a.className = "here"; a.setAttribute("aria-current", "page"); }
    sl.insertBefore(a, sl.querySelector(".gh"));
  }
  // cross-page menus (Seth 2026-11-06): "The Physics" and "More topics" open a chapter list on every page, like the
  // current page's own menu (filled by kit.js). Wide screens: a button and a list; phones keep the plain link in the ☰ menu.
  const MENUS = { "./": [["structure",0,"Structure"],["xsec",0,"Cross section"],["binding",0,"Binding"],["landscape",0,"Landscape"],["neutrons",0,"Why neutrons"],["omp",0,"Optical model"],["direct",0,"Direct reactions"],["preeq",1,"Pre-equilibrium"],["compound",1,"Compound nucleus"],["decay",1,"Decay"],["gamma",2,"Photons"],["cascade",1,"Cascade"],["fission",1,"Fission"],["fisout",1,"Fission neutrons"],["products",1,"Fission products"],["resonance",2,"Resonances"],["tof",1,"Measuring peaks"],["measure",1,"Observables"],["slowing",1,"Slowing down"],["layers",2,"Layers"],["#expert","xp_kicker","Part two · Expert","xp_h","Into the weeds"],["hauser",3,"A width-fluctuation recipe of Hofmann, Richert, Tepel and Weidenmüller: an elastic factor per channel and effective transmissions found by iteration."],["optical",3,"The global optical potential for neutrons and protons of A. J. Koning and J.-P. Delaroche (2003), from 1 keV to 200 MeV and mass 24 to 209."],["densities",3,"A composite level density: a constant-temperature law at low energy joined to the Fermi gas above a matching energy, with equal value and slope at the joint."],["strength",3,"The simplified modified Lorentzian: an E1 strength function whose width grows with photon energy and with the temperature of the final states."],["exciton",3,"The approximation that, early in the equilibration, collisions only add particle–hole pairs and never remove them."],["averages",3,"The exact description of resonance reactions by level energies and reduced widths inside a channel radius, matched to free waves outside it."]],
    "topics.html": [["#part-radiation","tp_p1_k","Part one","tp_p1_h","Radiation"],["halflife",0,"Half-life"],["rays",0,"Radiation"],["dose",0,"Dose"],["chains",1,"Decay chains"],["waste",1,"Spent fuel"],["#part-reactor","tp_p2_k","Part two","tp_p2_h","Inside a reactor"],["reactor",0,"Reactor"],["economy",1,"Neutron economy"],["spectrum",1,"Fast vs thermal"],["breeding",1,"Breeding"],["burnup",1,"Burnup"],["afterheat",0,"Afterheat"],["#part-control","tp_p3_k","Part three","tp_p3_h","Stability and control"],["critical",1,"Criticality"],["doppler",1,"Doppler"],["feedback",2,"Feedback"],["xenon",2,"Xenon"],["diffusion",2,"Critical size"],["kinetics",3,"Kinetics"],["transport",3,"Monte Carlo"],["#part-fusion","tp_p4_k","Part four","fu_h","Joining light nuclei"],["fusion",0,"Fusion"],["gamow",1,"Gamow peak"],["tokamak",2,"Confinement"],["blanket",3,"Blanket"]] };
  const LVN = ["Intro", "Intermediate", "Advanced", "Expert"];
  if (sl) sl.querySelectorAll('a[href="./"], a[href="topics.html"]').forEach((a) => {
    const page = a.getAttribute("href"), items = MENUS[page]; if (!items) return;
    let n = 0;
    const lis = items.map((it) => {
      if (it[0][0] === "#") return `<li class="toc-part"><span>${WT.ui(it[1], it[2])}</span>${WT.ui(it[3], it[4])}</li>`;
      const [id, lv, en] = it, t = (WT.L && WT.L.ch && WT.L.ch[id] && WT.L.ch[id].short) || WT.ui("in_s_" + id, en); n++;
      return `<li><a href="${page}#${id}" data-keep-lang><i class="l${lv}"></i><span class="n">${n}</span><span class="t">${t}</span><span class="lvl l${lv}">${WT.ui("lvl" + lv, LVN[lv])}</span></a></li>`;
    }).join("");
    const w = document.createElement("div"); w.className = "chap chap-x";
    a.replaceWith(w); w.appendChild(a);
    w.insertAdjacentHTML("beforeend", `<button type="button" class="toc-menu" aria-expanded="false"><span data-i18n="${a.dataset.i18n}">${a.innerHTML}</span> ▾</button><ol>${lis}</ol>`);
    const b = w.querySelector("button");
    b.addEventListener("click", (e) => { e.stopPropagation(); head.classList.remove("menu-open"); const o = w.classList.toggle("open"); b.setAttribute("aria-expanded", String(o)); });
  });
  // opening one menu closes the others (capture phase, before each button's own handler)
  head.addEventListener("click", (e) => { const b = e.target.closest(".toc-menu"); if (b) head.querySelectorAll(".chap.open").forEach((c) => { if (!c.contains(b)) { c.classList.remove("open"); const m = c.querySelector(".toc-menu"); m && m.setAttribute("aria-expanded", "false"); } }); }, true);
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
  const close = () => { head.classList.remove("menu-open"); burger && burger.setAttribute("aria-expanded", "false"); head.querySelectorAll(".chap").forEach((c) => { c.classList.remove("open"); const m = c.querySelector(".toc-menu"); m && m.setAttribute("aria-expanded", "false"); }); };
  if (burger) burger.addEventListener("click", (e) => { e.stopPropagation(); head.querySelectorAll(".chap").forEach((c) => c.classList.remove("open")); const o = head.classList.toggle("menu-open"); burger.setAttribute("aria-expanded", String(o)); });
  document.addEventListener("click", (e) => { if (!head.contains(e.target)) close(); });
  document.addEventListener("keydown", (e) => { if (e.key === "Escape") close(); });
  links.addEventListener("click", (e) => { if (e.target.closest("a")) close(); });
})();
