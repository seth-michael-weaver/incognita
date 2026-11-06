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
  const LV = [T("lvl0", "Intro"), T("lvl1", "Intermediate"), T("lvl2", "Advanced"), T("lvl3", "Expert")];
  // id, number, level, minutes, steps, English title / topic / what it teaches (Spanish in js/i18n/es-instructors.js)
  const CH = [
    ["structure", 1, 0, 12, 6, "What a nucleus is made of", "Structure", "Masses and separation energies, discrete levels and their γ branchings, isomers, nuclear shapes, and the resonance averages D₀, S₀, ⟨Γγ⟩."],
    ["xsec", 2, 0, 6, 3, "What is a cross section?", "Cross section", "The cross section as a target area in barns: a beam on a slab of nuclei, transmission, 1/v at low energy and a resonance."],
    ["binding", 3, 0, 7, 2, "Why nuclei hold together", "Binding", "Binding energy per nucleon from measured masses (AME2020): the iron peak and the energy from splitting uranium."],
    ["landscape", 4, 0, 6, 4, "The landscape of nuclei", "Landscape", "The chart of nuclides from measured masses and half-lives (AME2020, NUBASE2020): the 252 stable nuclei, the ridge of binding energy per nucleon with the magic numbers, beta decay down a mass chain to stability, and what INCOGNITA holds for each nucleus."],
    ["neutrons", 5, 0, 6, 3, "Why reactors run on neutrons", "Why neutrons", "The Coulomb barrier: a proton turned back or tunnelling; a neutron entering at any energy, down to thermal; so slow neutrons can start fission."],
    ["omp", 6, 0, 12, 6, "The optical model", "Optical model", "The optical model: a complex potential that bends and absorbs; aim and partial waves; transmission coefficients and the total cross section."],
    ["direct", 7, 0, 12, 7, "Direct reactions", "Direct reactions", "Inelastic scattering to collective levels (rotors, vibrators), coupled channels and DWBA, giant resonances, direct capture, and the flux direct reactions take first."],
    ["preeq", 8, 1, 15, 7, "Pre-equilibrium emission", "Pre-equilibrium", "The exciton model: particle–hole states, emission before equilibrium, the fast tail of spectra, cluster emission, multiple pre-equilibrium."],
    ["compound", 9, 1, 15, 6, "The compound nucleus", "Compound nucleus", "Level densities: from discrete levels to a continuum, constant-temperature and Fermi-gas pieces, shell damping, spin and parity, energy bins."],
    ["decay", 10, 1, 15, 7, "Compound-nucleus decay", "Decay", "Hauser–Feshbach competition: why emitted particles are slow, the Coulomb barrier, spin and parity conservation, width fluctuations."],
    ["gamma", 11, 2, 15, 6, "Gamma-ray emission", "Photons", "Photon strength functions (giant dipole resonance, scissors mode, upbend), discrete γ cascades, isomers, radiative capture."],
    ["cascade", 12, 1, 10, 5, "The emission cascade", "Cascade", "Multiple emission across the chart of nuclides, bin-by-bin bookkeeping, exclusive channels and residual production."],
    ["fission", 13, 1, 12, 6, "Fission", "Fission", "The barrier as a landscape of shapes, tunnelling, transition states, double-humped barriers, multiple-chance channels."],
    ["fisout", 14, 1, 8, 3, "Fission neutrons", "Fission neutrons", "Prompt-neutron multiplicity (about 2.4), the Watt energy spectrum (about 2 MeV), delayed neutrons (0.65 %) and their delay groups."],
    ["products", 15, 1, 8, 2, "Fission products and decay heat", "Fission products", "The double-humped fission-product mass yield, and decay heat after shutdown (Way–Wigner approximation)."],
    ["resonance", 16, 2, 15, 6, "Resonances", "Resonances", "Resonances as statistics: level repulsion, Porter–Thomas widths, ladders built from four averages, thermal values."],
    ["tof", 17, 1, 10, 5, "Time-of-flight measurements", "Measuring peaks", "Time of flight: a pulsed source, a flight path and a sample; transmission dips, self-shielding in thick samples, and resolution broadening."],
    ["measure", 18, 1, 15, 7, "Observables", "Observables", "From the nucleus to measured numbers: excitation functions, spectra, angular distributions, stellar capture (MACS), Total Monte Carlo uncertainty."],
    ["slowing", 19, 1, 10, 3, "Neutron moderation", "Slowing down", "Moderation: energy lost per collision with hydrogen and oxygen, thermal neutrons, chemical binding and the scattering law S(α,β)."],
    ["layers", 22, 2, 12, 5, "How the model is layered", "Layers", "How the data product is built on the engine: one global rule, each nucleus's own data, anchoring to good data (TERRA), calibrated error bars."],
    ["hauser", 23, 3, 18, 5, "Hauser–Feshbach, channel by channel", "Hauser–Feshbach", "The Hauser–Feshbach formula one spin and parity at a time, transmission per channel, width fluctuations (Moldauer, HRTW) and their effect when few channels are open."],
    ["optical", 24, 3, 20, 6, "The optical model, solved", "Optical model, solved", "The Koning–Delaroche potential, Numerov integration of the radial equation, matching to S and T, spin–orbit splitting, cross sections and the s-wave strength function."],
    ["densities", 25, 3, 18, 5, "Level densities, matched", "Level densities", "Gilbert–Cameron with Ignatyuk's damping, the tangent constant-temperature law, finding the matching energy from counted levels, the empirical fallback, and D₀ as a check."],
    ["strength", 26, 3, 18, 5, "Photon strength, in detail", "Photon strength", "E1 (SLO and SMLO) and M1 (spin-flip, scissors, upbend), the Brink–Axel hypothesis, the average radiative width ⟨Γγ⟩ and the γ cascade."],
    ["exciton", 27, 3, 20, 6, "The exciton model, in numbers", "Exciton model", "Particle–hole state densities, transition and emission rates, the exciton chain in time, the hard tail of spectra, the pre-equilibrium share and the two-component model."],
    ["averages", 28, 3, 18, 5, "From resonances to averages", "Resonances to averages", "The R-matrix formula, the statistics of resonance parameters, Doppler broadening, the energy average that becomes Hauser–Feshbach, and resolved, unresolved and smooth ranges."],
    ["halflife", 0, 0, 10, 5, "Radioactivity and half-life", "Half-life", "Random decay of single nuclei, the half-life as a statistical law, exponential decay curves and activity.", 1],
    ["rays", 0, 0, 10, 5, "Alpha, beta, gamma and neutrons", "Radiation", "The four kinds of radiation, what stops each (paper, aluminium, lead, water), and shielding by thickness.", 1],
    ["dose", 0, 0, 8, 4, "Radiation dose", "Dose", "Gray and sievert, everyday doses from a banana to a CT scan, and the doses at which tissue damage begins.", 1],
    ["everyday", 0, 0, 10, 5, "Nuclear in everyday life", "Everyday", "PET scans (fluorine-18, back-to-back 511 keV photons), radiotherapy beams crossing on a tumour, technetium-99m, carbon dating and smoke detectors.", 1],
    ["chains", 0, 1, 8, 4, "Decay chains and equilibrium", "Decay chains", "The uranium series to lead, secular equilibrium, and a medical isotope generator milked for its daughter.", 1],
    ["waste", 0, 1, 8, 4, "Spent fuel over time", "Spent fuel", "What is in used fuel, how its radioactivity falls over centuries, and when it drops to the level of uranium ore.", 1],
    ["reactor", 0, 0, 8, 4, "How a reactor makes electricity", "Reactor", "Core, control rods, coolant, steam and turbine: how fission heat becomes electricity in a water-cooled reactor.", 1],
    ["economy", 0, 1, 8, 4, "The neutron economy", "Neutron economy", "Where each generation of neutrons goes: fission, capture in uranium-238 and water, leakage, and the six-factor formula.", 1],
    ["spectrum", 0, 1, 8, 4, "Fast and thermal reactors", "Fast vs thermal", "Slowing neutrons down with a moderator, why thermal reactors need less enrichment, and what fast reactors gain.", 1],
    ["breeding", 0, 1, 10, 5, "Breeding new fuel", "Breeding", "Turning uranium-238 and thorium-232 into fissile fuel, neutrons per absorption (η), and the conversion and breeding ratio.", 1],
    ["burnup", 0, 1, 8, 4, "Fuel burnup", "Burnup", "How fuel changes in the core: uranium-235 burns, plutonium builds up, fission products absorb, and burnup in MWd/kg.", 1],
    ["afterheat", 0, 0, 8, 4, "Heat after shutdown", "Afterheat", "Decay heat after a reactor stops, how quickly it falls, and why cooling must continue after shutdown.", 1],
    ["rwater", 0, 0, 8, 6, "Water-cooled reactors", "Water reactors", "PWR, BWR, CANDU heavy water, RBMK, small modular and supercritical water reactors: one plant drawing each, with loops, pressures and temperatures.", 1],
    ["rgas", 0, 1, 6, 4, "Gas-cooled reactors", "Gas reactors", "Magnox, AGR, pebble-bed HTGR and VHTR: graphite moderation, CO₂ and helium coolant, high outlet temperatures.", 1],
    ["rfast", 0, 2, 6, 3, "Fast reactors", "Fast reactors", "Sodium, lead and gas-cooled fast reactors: pool designs, intermediate loops, no moderator.", 1],
    ["rother", 0, 2, 8, 5, "Molten salt and other reactors", "Salt and others", "Molten salt reactors, heat-pipe microreactors, TRIGA pool research reactors, accelerator-driven systems and the Oklo natural reactor.", 1],
    ["rcompare", 0, 1, 6, 3, "Reactor types compared", "Compared", "The moderator × coolant grid of every type, outlet temperature against efficiency with the Carnot limit, and the world fleet by type.", 1],
    ["sandbox", 0, 2, 10, 6, "Build a reactor", "Build a reactor", "A sandbox: pick fuel, enrichment, moderator, coolant, lattice and size; the four-factor formula, one-group leakage and the critical size, the neutron budget, and the sign of the void and Doppler feedback.", 1],
    ["critical", 21, 1, 10, 3, "Criticality and reactor control", "Criticality", "The chain reaction: the multiplication factor k, delayed neutrons and why a reactor can be controlled, critical experiments.", 1],
    ["doppler", 20, 1, 8, 3, "Doppler broadening", "Doppler", "Doppler broadening of a resonance with fuel temperature, self-shielding in thick fuel, and the negative fuel-temperature feedback on k.", 1],
    ["feedback", 0, 2, 8, 4, "Reactor stability and feedback", "Feedback", "Fuel- and moderator-temperature feedback, void coefficients, and why negative feedback makes a reactor stable.", 1],
    ["xenon", 0, 2, 8, 4, "Xenon poisoning", "Xenon", "Xenon-135 build-up and burn-out, the iodine pit after shutdown, and xenon oscillations in large cores.", 1],
    ["diffusion", 0, 2, 8, 4, "Critical size and leakage", "Critical size", "Neutron diffusion, leakage through the surface, buckling, and the critical size of a bare core.", 1],
    ["kinetics", 0, 3, 10, 4, "Reactor kinetics: six groups and the inhour equation", "Kinetics", "Point kinetics with six delayed-neutron groups, the inhour equation, the reactor period and the prompt jump.", 1],
    ["transport", 0, 3, 10, 4, "Neutron transport and Monte Carlo", "Monte Carlo", "Following neutrons one at a time through a slab: collisions, the random walk, and how Monte Carlo transport estimates k and flux.", 1],
    ["fusion", 29, 0, 12, 4, "Fusion energy and the Coulomb barrier", "Fusion", "Fusion energy from the binding curve; two light nuclei over the Coulomb hill: tunnelling, the energy released as missing mass, fuels compared, and why the gas must be hot.", 1],
    ["gamow", 30, 1, 12, 3, "The Gamow peak and ignition", "Gamow peak", "The Gamow peak from the Maxwell tail and tunnelling, reactivities of D–T, D–D and D–³He, and the Lawson plane with a 0-D power balance to ignition.", 1],
    ["tokamak", 31, 2, 12, 3, "Magnetic confinement", "Confinement", "Gyration in a magnetic field, the twisted field of a tokamak and its safety factor, Poincaré sections, magnetic islands and chaos (the tokamap).", 1],
    ["blanket", 32, 3, 15, 3, "Breeding blanket and first wall", "Blanket", "Monte Carlo neutron transport in a breeding blanket: tritium breeding ratio, ⁶Li enrichment, (n,2n) multiplication; helium and hydrogen in the first wall from INCOGNITA's 14.1 MeV cross sections.", 1],
  ].map(([id, n, lv, min, steps, title, topic, what, tp], i) => ({ id, lv, min, steps, tp: !!tp, title: T("in_t_" + id, title), topic: T("in_s_" + id, topic), what: T("in_w_" + id, what) }));
  // numbers per page: main story 1..26, then the More topics lessons 1..28 (topics.html)
  { let a = 0, b = 0; CH.forEach((c) => (c.n = c.tp ? ++b : ++a)); }
  const byId = Object.fromEntries(CH.map((c) => [c.id, c]));
  const lang = WT.langQ();
  const href = (id) => (byId[id] && byId[id].tp ? "./topics.html" : "./") + lang + "#" + id;
  const pill = (lv) => `<span class="lvl l${lv}">${LV[lv]}</span>`;
  const mins = (m) => `${m} ${T("in_min", "min")}`;

  // ---------- chapter list with a level filter ----------
  const list = $("#in-list"), chips = $("#in-filter");
  const tpHead = `<li class="in-part"><h3>${T("way4_t", "More Nuclear Topics")}</h3><p class="in-faint">${T("in_tp_p", "Lessons on topics.html, beside the main story: radiation, how reactors work, every kind of reactor, stability and control, fusion.")}</p></li>`;
  list.innerHTML = CH.map((c, i) => (c.tp && !(CH[i - 1] || {}).tp ? tpHead : "") + `<li class="in-ch" data-lv="${c.lv}" data-min="${c.min}"><a class="in-ch-a" href="${href(c.id)}"><span class="in-n">${c.n}</span><span class="in-body"><span class="in-top"><b>${c.title}</b><span class="in-topic">${c.topic}</span></span><span class="in-what">${c.what}</span><span class="in-meta">${pill(c.lv)}<span>${mins(c.min)}</span><span>${c.steps} ${T("in_steps", "steps")}</span><code>#${c.id}</code></span></span></a></li>`).join("");
  const opts = [["all", T("in_all", "All")], ["0", LV[0]], ["1", LV[1]], ["2", LV[2]], ["3", LV[3]]];
  chips.innerHTML = opts.map(([v, t]) => `<button type="button" data-v="${v}" aria-pressed="${v === "all"}">${t}</button>`).join("");
  const total = $("#in-total");
  const filt = (v) => {
    chips.querySelectorAll("button").forEach((b) => b.setAttribute("aria-pressed", String(b.dataset.v === v)));
    let n = 0, m = 0; list.querySelectorAll(".in-ch").forEach((li) => { const on = v === "all" || li.dataset.lv === v; li.hidden = !on; if (on) { n++; m += +li.dataset.min; } });
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
  const opt = (c) => `<option value="${c.id}">${c.n} · ${c.title}</option>`;
  selC.innerHTML = CH.filter((c) => !c.tp).map(opt).join("") + `<optgroup label="${T("way4_t", "More Nuclear Topics")}">` + CH.filter((c) => c.tp).map(opt).join("") + "</optgroup>";
  const fillSteps = () => { const c = byId[selC.value], v = selS.value; selS.innerHTML = `<option value="">${T("in_b_whole", "whole chapter")}</option>` + Array.from({ length: c.steps }, (_, i) => `<option value="${i + 1}">${T("in_b_step", "step")} ${i + 1}</option>`).join(""); if (v && +v <= c.steps) selS.value = v; };
  const build = () => { const url = base + (byId[selC.value].tp ? "topics.html" : "") + (selL.value !== "en" ? "?lang=" + selL.value : "") + "#" + selC.value + (selS.value ? "-" + selS.value : ""); out.textContent = url; open.href = url; };
  selL.innerHTML = Object.entries(WT.LANGS).map(([l, [, name]]) => `<option value="${l}" lang="${l}">${name}</option>`).join(""); selL.value = WT.lang; fillSteps(); build();
  selC.addEventListener("change", () => { fillSteps(); build(); }); selS.addEventListener("change", build); selL.addEventListener("change", build);
  copy.addEventListener("click", () => { const done = () => { copy.textContent = T("link_copied", "Link copied"); setTimeout(() => (copy.textContent = T("in_b_copy", "Copy")), 1600); };
    try { navigator.clipboard.writeText(out.textContent).then(done, done); } catch (e) { done(); } });
})();
