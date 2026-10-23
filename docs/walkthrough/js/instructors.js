/* Instructors' guide (instructors.html): chapter list with levels and times, level filter, suggested courses drawn as
 * time bars, and a link builder for any chapter or step. Levels match LEVEL in kit.js; step counts match js/ch/*.js. */
(function () {
  "use strict";
  const es = WT.tl, T = (k, en) => WT.ui(k, en);
  const $ = (s) => document.querySelector(s);
  if (es) {
    if (WT.L.ui.in_title) document.title = WT.L.ui.in_title;
    document.querySelectorAll("[data-i18n]").forEach((el) => { const t = WT.L.ui[el.dataset.i18n]; if (t != null) el.innerHTML = t; });
    document.querySelectorAll("[data-i18n-aria]").forEach((el) => { const t = WT.L.ui[el.dataset.i18nAria]; if (t != null) el.setAttribute("aria-label", t); });
    WT.keepLang();
  }
  const LV = [T("lvl0", "Intro"), T("lvl1", "Intermediate"), T("lvl2", "Advanced")];
  // id, number, level, minutes, steps, English title / topic / what it teaches (Spanish in js/i18n/es-instructors.js)
  const CH = [
    ["structure", 1, 0, 12, 6, "What a nucleus is made of", "Structure", "Masses and separation energies, discrete levels and their γ branchings, isomers, nuclear shapes, and the resonance averages D₀, S₀, ⟨Γγ⟩."],
    ["omp", 2, 0, 12, 6, "A cloudy crystal ball", "Optical model", "The optical model: a complex potential that bends and absorbs; aim and partial waves; transmission coefficients and the total cross section."],
    ["direct", 3, 0, 12, 7, "A glancing blow", "Direct reactions", "Inelastic scattering to collective levels (rotors, vibrators), coupled channels and DWBA, giant resonances, direct capture, and the flux direct reactions take first."],
    ["preeq", 4, 1, 15, 7, "Collisions before calm", "Pre-equilibrium", "The exciton model: particle–hole states, emission before equilibrium, the fast tail of spectra, cluster emission, multiple pre-equilibrium."],
    ["compound", 5, 1, 15, 6, "Sharing the energy", "Compound nucleus", "Level densities: from discrete levels to a continuum, constant-temperature and Fermi-gas pieces, shell damping, spin and parity, energy bins."],
    ["decay", 6, 1, 15, 7, "Choosing an exit", "Decay", "Hauser–Feshbach competition: why emitted particles are slow, the Coulomb barrier, spin and parity conservation, width fluctuations."],
    ["gamma", 7, 2, 15, 6, "Shedding light", "Photons", "Photon strength functions (giant dipole resonance, scissors mode, upbend), discrete γ cascades, isomers, radiative capture."],
    ["cascade", 8, 1, 10, 5, "Down the chart", "Cascade", "Multiple emission across the chart of nuclides, bin-by-bin bookkeeping, exclusive channels and residual production."],
    ["fission", 9, 1, 12, 6, "Splitting", "Fission", "The barrier as a landscape of shapes, tunnelling, transition states, double-humped barriers, multiple-chance channels."],
    ["resonance", 10, 2, 15, 6, "Sharp peaks", "Resonances", "Resonances as statistics: level repulsion, Porter–Thomas widths, ladders built from four averages, thermal values."],
    ["measure", 11, 1, 15, 7, "What comes out", "Observables", "From the nucleus to measured numbers: excitation functions, spectra, angular distributions, stellar capture (MACS), Total Monte Carlo uncertainty."],
    ["layers", 12, 2, 12, 5, "How the model is layered", "Layers", "How the data product is built on the engine: one global rule, each nucleus's own data, anchoring to good data (TERRA), calibrated error bars."],
  ].map(([id, n, lv, min, steps, title, topic, what]) => ({ id, n, lv, min, steps, title: T("in_t_" + id, title), topic: T("in_s_" + id, topic), what: T("in_w_" + id, what) }));
  const byId = Object.fromEntries(CH.map((c) => [c.id, c]));
  const lang = WT.langQ();
  const href = (id) => "./" + lang + "#" + id;
  const pill = (lv) => `<span class="lvl l${lv}">${LV[lv]}</span>`;
  const mins = (m) => `${m} ${T("in_min", "min")}`;

  // ---------- chapter list with a level filter ----------
  const list = $("#in-list"), chips = $("#in-filter");
  list.innerHTML = CH.map((c) => `<li class="in-ch" data-lv="${c.lv}"><a class="in-ch-a" href="${href(c.id)}"><span class="in-n">${c.n}</span><span class="in-body"><span class="in-top"><b>${c.title}</b><span class="in-topic">${c.topic}</span></span><span class="in-what">${c.what}</span><span class="in-meta">${pill(c.lv)}<span>${mins(c.min)}</span><span>${c.steps} ${T("in_steps", "steps")}</span><code>#${c.id}</code></span></span></a></li>`).join("");
  const opts = [["all", T("in_all", "All")], ["0", LV[0]], ["1", LV[1]], ["2", LV[2]]];
  chips.innerHTML = opts.map(([v, t]) => `<button type="button" data-v="${v}" aria-pressed="${v === "all"}">${t}</button>`).join("");
  const total = $("#in-total");
  const filt = (v) => {
    chips.querySelectorAll("button").forEach((b) => b.setAttribute("aria-pressed", String(b.dataset.v === v)));
    let n = 0, m = 0; list.querySelectorAll(".in-ch").forEach((li, i) => { const on = v === "all" || li.dataset.lv === v; li.hidden = !on; if (on) { n++; m += CH[i].min; } });
    total.textContent = `${n} ${T("in_chapters", "chapters")} · ≈ ${mins(m)}`;
  };
  chips.addEventListener("click", (e) => { const b = e.target.closest("button"); if (b) filt(b.dataset.v); });
  filt("all");

  // ---------- suggested courses: one bar per lecture, segment width = time ----------
  const COURSES = [
    { key: "one", lectures: [{ k: "in_l1_1", en: "From a nucleus to a cross section", ids: ["structure", "omp", "decay", "measure"] }] },
    { key: "three", lectures: [
      { k: "in_l3_1", en: "The nucleus and the first contact", ids: ["structure", "omp", "direct", "preeq"] },
      { k: "in_l3_2", en: "The compound nucleus", ids: ["compound", "decay", "gamma", "cascade"] },
      { k: "in_l3_3", en: "Beyond the averages, and the data", ids: ["fission", "resonance", "measure", "layers"] } ] },
  ];
  const maxMin = Math.max(...COURSES.flatMap((c) => c.lectures.map((l) => l.ids.reduce((s, id) => s + byId[id].min, 0))));
  COURSES.forEach((c) => {
    const box = $("#in-course-" + c.key); if (!box) return;
    box.innerHTML = c.lectures.map((l, i) => {
      const sum = l.ids.reduce((s, id) => s + byId[id].min, 0);
      const bar = l.ids.map((id) => { const ch = byId[id]; return `<a class="in-seg l${ch.lv}" href="${href(id)}" style="flex:${ch.min}" title="${ch.n} · ${ch.title} · ${mins(ch.min)}"><span>${ch.n}</span></a>`; }).join("");
      const items = l.ids.map((id) => { const ch = byId[id]; return `<li><a href="${href(id)}"><span class="in-n">${ch.n}</span>${ch.title}</a> ${pill(ch.lv)} <span class="in-faint">${mins(ch.min)}</span></li>`; }).join("");
      return `<div class="in-lec"><div class="in-lec-h">${c.lectures.length > 1 ? `<span class="in-lec-k">${T("in_lecture", "Lecture")} ${i + 1}</span>` : ""}<b>${T(l.k, l.en)}</b><span class="in-faint">≈ ${mins(sum)}</span></div>
        <div class="in-bar" style="width:${(100 * sum / maxMin).toFixed(1)}%">${bar}</div><ol class="in-lec-list">${items}</ol></div>`;
    }).join("");
  });

  // ---------- link builder ----------
  const selC = $("#in-b-ch"), selS = $("#in-b-step"), selL = $("#in-b-lang"), out = $("#in-b-url"), open = $("#in-b-open"), copy = $("#in-b-copy");
  const base = location.origin + location.pathname.replace(/instructors(\.html)?$/, "");
  selC.innerHTML = CH.map((c) => `<option value="${c.id}">${c.n} · ${c.title}</option>`).join("");
  const fillSteps = () => { const c = byId[selC.value], v = selS.value; selS.innerHTML = `<option value="">${T("in_b_whole", "whole chapter")}</option>` + Array.from({ length: c.steps }, (_, i) => `<option value="${i + 1}">${T("in_b_step", "step")} ${i + 1}</option>`).join(""); if (v && +v <= c.steps) selS.value = v; };
  const build = () => { const url = base + (selL.value !== "en" ? "?lang=" + selL.value : "") + "#" + selC.value + (selS.value ? "-" + selS.value : ""); out.textContent = url; open.href = url; };
  selL.innerHTML = Object.entries(WT.LANGS).map(([l, [, name]]) => `<option value="${l}" lang="${l}">${name}</option>`).join(""); selL.value = WT.lang; fillSteps(); build();
  selC.addEventListener("change", () => { fillSteps(); build(); }); selS.addEventListener("change", build); selL.addEventListener("change", build);
  copy.addEventListener("click", () => { const done = () => { copy.textContent = T("link_copied", "Link copied"); setTimeout(() => (copy.textContent = T("in_b_copy", "Copy")), 1600); };
    try { navigator.clipboard.writeText(out.textContent).then(done, done); } catch (e) { done(); } });
})();
