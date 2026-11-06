/* Danish (Dansk): stars (Hvor grundstofferne kommer fra) */
WT.L.ch.stars = {
  num: "Lektion 1", title: "Hvor grundstofferne kommer fra", short: "Stjerner",
  html: `
<div class="step">
  <h3>Fusion stopper ved jern</h3>
  <p>Stjerner smelter lette kerner sammen op til jern; næsten alt tungere bygges op ved at tilføje neutroner.</p>
</div>
<div class="step">
  <h3>Den langsomme vej</h3>
  <p>I kæmpestjerner kommer neutroner sjældent, så en ustabil kerne betahenfalder først: vejen går i zigzag langs de stabile kerner.</p>
  <div class="ctl"><label for="st-k">Neutronindfangninger</label><input id="st-k" type="range" data-bind="k" min="0" max="213" step="1" value="112"></div>
</div>
<div class="step">
  <h3>Den hurtige vej</h3>
  <p>Når to neutronstjerner smelter sammen, strømmer neutroner ind hurtigere, end kernerne kan henfalde; bagefter henfalder de neutronrige kerner tilbage til stabilitet.</p>
  <div class="ctl"><label for="st-rt">Henfald tilbage</label><input id="st-rt" type="range" data-bind="rt" min="0" max="1" step="0.01" value="0"></div>
</div>
<div class="step">
  <h3>Magiske tal giver toppe</h3>
  <p>Kerner med 50, 82 eller 126 neutroner indfanger knap nok, så stoffet hober sig op der: s-toppe ved strontium, barium og bly, r-toppe lidt lettere.</p>
  <div class="btns"><button class="btn ghost" data-act="stS" aria-pressed="true">s-procestoppe</button> <button class="btn ghost" data-act="stR" aria-pressed="true">r-procestoppe</button></div>
</div>
<div class="step">
  <h3>Sjælden, hvor indfangning er let</h3>
  <p>For isotoper, der kun dannes i s-processen, er hyppigheden Nₛ gange indfangningstværsnittet σ næsten konstant mellem magiske tal. σ er her INCOGNITAs beregnede værdi ved 30 keV.</p>
  <div class="btns"><button class="btn ghost" data-act="stvs" aria-pressed="false">σ</button> <button class="btn ghost" data-act="stvn" aria-pressed="false">Nₛ</button> <button class="btn ghost" data-act="stvsn" aria-pressed="true">σ × Nₛ</button></div>
</div>
<div class="step">
  <h3>Sammenholdt med målinger</h3>
  <p>INCOGNITAs 30 keV-værdier divideret med målte, for 94 stabile nuklider (<a href="scoreboard.html">resultattavle</a>).</p>
</div>`,
};

Object.assign(WT.L.labels, {
  " (scaled to a measured value)": " (skaleret til en målt værdi)",
  " (σ scaled to a measured value)": " (σ skaleret til en målt værdi)",
  "{a} % above measured": "{a} % over målt",
  "{a} % below measured": "{a} % under målt",
  "{a} nuclides · typical difference {b} %": "{a} nuklider · typisk afvigelse {b} %",
  "{a} stable nuclides · typical difference {b} % (median), rms {c} %": "{a} stabile nuklider · typisk afvigelse {b} % (median), rms {c} %",
  "{a}: INCOGNITA's engine {b} (the library then scales to it)": "{a}: INCOGNITAs beregning {b} (biblioteket skaleres derefter til den)",
  "↑ protons Z": "↑ protoner Z",
  "A = {a}: mostly {b}, {c} atoms per million silicon": "A = {a}: mest {b}, {c} atomer pr. million silicium",
  "A ≈ {#}": "A ≈ {#}",
  "abundances: Lodders, Palme & Gail {#}": "hyppigheder: Lodders, Palme & Gail {#}",
  "abundances: Lodders, Palme & Gail {#} · point at the curve": "hyppigheder: Lodders, Palme & Gail {#} · peg på kurven",
  "atoms per {#}⁶ silicon": "atomer pr. {#}⁶ silicium",
  "atoms per million silicon atoms (Solar System)": "atomer pr. million siliciumatomer (solsystemet)",
  "Ba": "Ba",
  "Ba{#}": "Ba{#}",
  "beta decay (n → p)": "betahenfald (n → p)",
  "beta decays carry them back, mass number A fixed": "betahenfald fører dem tilbage, massetallet A uændret",
  "beta decays, A fixed": "betahenfald, A fast",
  "Big Bang": "Big Bang",
  "decayed back: each lands on the most neutron-rich stable isobar": "henfaldet tilbage: hver lander på den mest neutronrige stabile isobar",
  "decayed back: r-made stable isotopes": "henfaldet tilbage: stabile isotoper fra r-processen",
  "drag along the path": "træk langs vejen",
  "drag along the path, or use the slider": "træk langs vejen, eller brug skyderen",
  "end of the road: Bi{#} → Po{#} → alpha decay back to Pb{#}": "vejs ende: Bi{#} → Po{#} → alfahenfald tilbage til Pb{#}",
  "end: the lead–bismuth cycle": "slut: bly-bismut-cyklussen",
  "Fe": "Fe",
  "flat between magic numbers, steps down at each": "flad mellem magiske tal, et trin ned ved hvert",
  "fusion": "fusion",
  "fusion in stars": "fusion i stjerner",
  "H": "H",
  "He": "He",
  "INCOGNITA ÷ measured, {#} keV": "INCOGNITA ÷ målt, {#} keV",
  "INCOGNITA: capture at {#} keV (MACS)": "INCOGNITA: indfangning ved {#} keV (MACS)",
  "INCOGNITA's {#} keV capture rate (MACS) ÷ measured": "INCOGNITAs indfangningsrate ved {#} keV (MACS) ÷ målt",
  "Lodders et al. {#}": "Lodders et al. {#}",
  "Lu{#}": "Lu{#}",
  "made by neutron capture": "dannet ved neutronindfangning",
  "magic N: captures poorly, matter piles up": "magisk N: indfanger dårligt, stof hober sig op",
  "magic neutron number: it captures poorly, so matter piles up here": "magisk neutrontal: indfanger dårligt, så stoffet hober sig op her",
  "mass number A": "massetal A",
  "mass number A (protons + neutrons)": "massetal A (protoner + neutroner)",
  "mb": "mb",
  "N = {#}": "N = {#}",
  "nearly flat between magic numbers, a step down at each": "næsten flad mellem magiske tal, et trin ned ved hvert",
  "neutron capture": "neutronindfangning",
  "neutrons N →": "neutroner N →",
  "Nₛ alone jumps around the other way": "Nₛ alene springer den anden vej",
  "Nₛ alone: scattered": "Nₛ alene: spredt",
  "O": "O",
  "Pb": "Pb",
  "Pb{#}": "Pb{#}",
  "peaks: sources Lodders et al. {#}": "toppe: kilder Lodders et al. {#}",
  "plus a weaker s-process (massive stars)": "plus en svagere s-proces (massive stjerner)",
  "r {#}": "r {#}",
  "r-path: illustration": "r-vej: illustration",
  "r-peak Pt": "r-top Pt",
  "r-peak Se, Kr": "r-top Se, Kr",
  "r-peak Te, Xe": "r-top Te, Xe",
  "r-process: a flood of neutrons makes very neutron-rich nuclei": "r-proces: en flod af neutroner danner meget neutronrige kerner",
  "r-process: very neutron-rich nuclei": "r-proces: meget neutronrige kerner",
  "ringed: s-only · measured: KADoNiS": "med ring: kun s · målt: KADoNiS",
  "ringed: s-only isotopes · measured: compiled values (KADoNiS) · a development comparison, not a blind test": "med ring: rene s-isotoper · målt: kompilerede værdier (KADoNiS) · en udviklingssammenligning, ikke en blindtest",
  "s Ba": "s Ba",
  "s Pb": "s Pb",
  "s Sr": "s Sr",
  "s-only isotopes · bars: INCOGNITA {#} %": "rene s-isotoper · søjler: INCOGNITA {#} %",
  "s-only isotopes · σ: INCOGNITA (bars: its {#} % range; open circle: scaled to a measurement) · Nₛ: Lodders et al. {#}": "rene s-isotoper · σ: INCOGNITA (søjler: dens {#} %-interval; åben cirkel: skaleret til en måling) · Nₛ: Lodders et al. {#}",
  "s-peak Ba": "s-top Ba",
  "s-peak Pb": "s-top Pb",
  "s-peak Sr": "s-top Sr",
  "seen in {#}: merger GW{#}": "set i {#}: sammensmeltningen GW{#}",
  "seen in {#}: the neutron-star merger GW{#} and its kilonova": "set i {#}: neutronstjernesammensmeltningen GW{#} og dens kilonova",
  "Sm{#}": "Sm{#}",
  "Sn": "Sn",
  "Sr": "Sr",
  "Sr{#}": "Sr{#}",
  "wait": "vent",
  "waiting point": "ventepunkt",
  "weak s-process too": "også svag s-proces",
  "σ × Nₛ (mb × atoms per {#}⁶ Si)": "σ × Nₛ (mb × atomer pr. {#}⁶ Si)",
  "σ × Nₛ (mb × atoms per million Si)": "σ × Nₛ (mb × atomer pr. million Si)",
  "σ alone jumps around from isotope to isotope": "σ alene springer fra isotop til isotop",
});
