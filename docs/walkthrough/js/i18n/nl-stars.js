/* Dutch (Nederlands): stars (Waar de elementen vandaan komen) */
WT.L.ch.stars = {
  num: "Les 1", title: "Waar de elementen vandaan komen", short: "Sterren",
  html: `
<div class="step">
  <h3>Fusie stopt bij ijzer</h3>
  <p>Sterren smelten lichte kernen samen tot ijzer; bijna alles wat zwaarder is, wordt opgebouwd door neutronen toe te voegen.</p>
</div>
<div class="step">
  <h3>De langzame weg</h3>
  <p>In reuzensterren komen neutronen zelden, dus een instabiele kern ondergaat eerst bètaverval: het pad zigzagt langs de stabiele kernen.</p>
  <div class="ctl"><label for="st-k">Neutronenvangsten</label><input id="st-k" type="range" data-bind="k" min="0" max="213" step="1" value="112"></div>
</div>
<div class="step">
  <h3>De snelle weg</h3>
  <p>Bij het samensmelten van neutronensterren stromen neutronen sneller binnen dan kernen kunnen vervallen; daarna vervallen de neutronrijke kernen terug naar stabiliteit.</p>
  <div class="ctl"><label for="st-rt">Terugvervallen</label><input id="st-rt" type="range" data-bind="rt" min="0" max="1" step="0.01" value="0"></div>
</div>
<div class="step">
  <h3>Magische getallen maken pieken</h3>
  <p>Kernen met 50, 82 of 126 neutronen vangen nauwelijks, dus daar hoopt materie zich op: s-pieken bij strontium, barium en lood, r-pieken iets lichter.</p>
  <div class="btns"><button class="btn ghost" data-act="stS" aria-pressed="true">s-procespieken</button> <button class="btn ghost" data-act="stR" aria-pressed="true">r-procespieken</button></div>
</div>
<div class="step">
  <h3>Zeldzaam waar vangst makkelijk is</h3>
  <p>Voor isotopen die alleen door het s-proces ontstaan, blijft de abundantie Nₛ maal de vangstdoorsnede σ bijna vlak tussen magische getallen. σ is hier de door INCOGNITA berekende waarde bij 30 keV.</p>
  <div class="btns"><button class="btn ghost" data-act="stvs" aria-pressed="false">σ</button> <button class="btn ghost" data-act="stvn" aria-pressed="false">Nₛ</button> <button class="btn ghost" data-act="stvsn" aria-pressed="true">σ × Nₛ</button></div>
</div>
<div class="step">
  <h3>Getoetst aan metingen</h3>
  <p>De 30 keV-waarden van INCOGNITA gedeeld door gemeten waarden, voor 94 stabiele nucliden (<a href="scoreboard.html">vergelijkingen</a>).</p>
</div>`,
};

Object.assign(WT.L.labels, {
  " (scaled to a measured value)": " (geschaald naar een meetwaarde)",
  " (σ scaled to a measured value)": " (σ geschaald naar een meetwaarde)",
  "{a} % above measured": "{a} % boven gemeten",
  "{a} % below measured": "{a} % onder gemeten",
  "{a} nuclides · typical difference {b} %": "{a} nucliden · typisch verschil {b} %",
  "{a} stable nuclides · typical difference {b} % (median), rms {c} %": "{a} stabiele nucliden · typisch verschil {b} % (mediaan), rms {c} %",
  "{a}: INCOGNITA's engine {b} (the library then scales to it)": "{a}: rekenkern van INCOGNITA {b} (de bibliotheek schaalt daarna erop)",
  "↑ protons Z": "↑ protonen Z",
  "A = {a}: mostly {b}, {c} atoms per million silicon": "A = {a}: vooral {b}, {c} atomen per miljoen silicium",
  "A ≈ {#}": "A ≈ {#}",
  "abundances: Lodders, Palme & Gail {#}": "abundanties: Lodders, Palme & Gail {#}",
  "abundances: Lodders, Palme & Gail {#} · point at the curve": "abundanties: Lodders, Palme & Gail {#} · wijs de curve aan",
  "atoms per {#}⁶ silicon": "atomen per {#}⁶ silicium",
  "atoms per million silicon atoms (Solar System)": "atomen per miljoen siliciumatomen (zonnestelsel)",
  "Ba": "Ba",
  "Ba{#}": "Ba{#}",
  "beta decay (n → p)": "bètaverval (n → p)",
  "beta decays carry them back, mass number A fixed": "bètaverval brengt ze terug, massagetal A blijft gelijk",
  "beta decays, A fixed": "bètaverval, A vast",
  "Big Bang": "oerknal",
  "decayed back: each lands on the most neutron-rich stable isobar": "teruggevallen: elk belandt op de meest neutronrijke stabiele isobaar",
  "decayed back: r-made stable isotopes": "teruggevallen: stabiele isotopen uit het r-proces",
  "drag along the path": "sleep langs het pad",
  "drag along the path, or use the slider": "sleep langs het pad of gebruik de schuif",
  "end of the road: Bi{#} → Po{#} → alpha decay back to Pb{#}": "eindpunt: Bi{#} → Po{#} → alfaverval terug naar Pb{#}",
  "end: the lead–bismuth cycle": "einde: de lood-bismutcyclus",
  "Fe": "Fe",
  "flat between magic numbers, steps down at each": "vlak tussen magische getallen, bij elk een trede omlaag",
  "fusion": "fusie",
  "fusion in stars": "fusie in sterren",
  "H": "H",
  "He": "He",
  "INCOGNITA ÷ measured, {#} keV": "INCOGNITA ÷ gemeten, {#} keV",
  "INCOGNITA: capture at {#} keV (MACS)": "INCOGNITA: vangst bij {#} keV (MACS)",
  "INCOGNITA's {#} keV capture rate (MACS) ÷ measured": "vangstsnelheid van INCOGNITA bij {#} keV (MACS) ÷ gemeten",
  "Lodders et al. {#}": "Lodders et al. {#}",
  "Lu{#}": "Lu{#}",
  "made by neutron capture": "gemaakt door neutronenvangst",
  "magic N: captures poorly, matter piles up": "magisch N: vangt slecht, materie hoopt op",
  "magic neutron number: it captures poorly, so matter piles up here": "magisch neutronengetal: vangt slecht, dus hier hoopt materie zich op",
  "mass number A": "massagetal A",
  "mass number A (protons + neutrons)": "massagetal A (protonen + neutronen)",
  "mb": "mb",
  "N = {#}": "N = {#}",
  "nearly flat between magic numbers, a step down at each": "bijna vlak tussen magische getallen, bij elk een trede omlaag",
  "neutron capture": "neutronenvangst",
  "neutrons N →": "neutronen N →",
  "Nₛ alone jumps around the other way": "Nₛ alleen springt de andere kant op",
  "Nₛ alone: scattered": "Nₛ alleen: verspreid",
  "O": "O",
  "Pb": "Pb",
  "Pb{#}": "Pb{#}",
  "peaks: sources Lodders et al. {#}": "pieken: bronnen Lodders et al. {#}",
  "plus a weaker s-process (massive stars)": "plus een zwakker s-proces (zware sterren)",
  "r {#}": "r {#}",
  "r-path: illustration": "r-pad: illustratie",
  "r-peak Pt": "r-piek Pt",
  "r-peak Se, Kr": "r-piek Se, Kr",
  "r-peak Te, Xe": "r-piek Te, Xe",
  "r-process: a flood of neutrons makes very neutron-rich nuclei": "r-proces: een vloed van neutronen maakt zeer neutronrijke kernen",
  "r-process: very neutron-rich nuclei": "r-proces: zeer neutronrijke kernen",
  "ringed: s-only · measured: KADoNiS": "omcirkeld: alleen s · gemeten: KADoNiS",
  "ringed: s-only isotopes · measured: compiled values (KADoNiS) · a development comparison, not an independent test": "omcirkeld: zuivere s-isotopen · gemeten: verzamelde waarden (KADoNiS) · een ontwikkelvergelijking, geen onafhankelijke test",
  "s Ba": "s Ba",
  "s Pb": "s Pb",
  "s Sr": "s Sr",
  "s-only isotopes · bars: INCOGNITA {#} %": "zuivere s-isotopen · balken: INCOGNITA {#} %",
  "s-only isotopes · σ: INCOGNITA (bars: its {#} % range; open circle: scaled to a measurement) · Nₛ: Lodders et al. {#}": "zuivere s-isotopen · σ: INCOGNITA (balken: het {#} %-bereik; open cirkel: geschaald naar een meting) · Nₛ: Lodders et al. {#}",
  "s-peak Ba": "s-piek Ba",
  "s-peak Pb": "s-piek Pb",
  "s-peak Sr": "s-piek Sr",
  "seen in {#}: merger GW{#}": "gezien in {#}: samensmelting GW{#}",
  "seen in {#}: the neutron-star merger GW{#} and its kilonova": "gezien in {#}: de samensmelting van neutronensterren GW{#} en haar kilonova",
  "Sm{#}": "Sm{#}",
  "Sn": "Sn",
  "Sr": "Sr",
  "Sr{#}": "Sr{#}",
  "wait": "wacht",
  "waiting point": "wachtpunt",
  "weak s-process too": "ook zwak s-proces",
  "σ × Nₛ (mb × atoms per {#}⁶ Si)": "σ × Nₛ (mb × atomen per {#}⁶ Si)",
  "σ × Nₛ (mb × atoms per million Si)": "σ × Nₛ (mb × atomen per miljoen Si)",
  "σ alone jumps around from isotope to isotope": "σ alleen springt van isotoop tot isotoop",
});
