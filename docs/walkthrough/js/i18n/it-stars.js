/* Italian (Italiano): stars (Da dove vengono gli elementi) */
WT.L.ch.stars = {
  num: "Lezione 1", title: "Da dove vengono gli elementi", short: "Stelle",
  html: `
<div class="step">
  <h3>La fusione si ferma al ferro</h3>
  <p>Le stelle fondono nuclei leggeri fino al ferro; quasi tutto ciò che è più pesante si costruisce aggiungendo neutroni.</p>
</div>
<div class="step">
  <h3>La via lenta</h3>
  <p>Nelle stelle giganti i neutroni arrivano di rado, così un nucleo instabile fa prima un decadimento beta: il percorso procede a zigzag lungo i nuclei stabili.</p>
  <div class="ctl"><label for="st-k">Catture neutroniche</label><input id="st-k" type="range" data-bind="k" min="0" max="213" step="1" value="112"></div>
</div>
<div class="step">
  <h3>La via rapida</h3>
  <p>In una fusione di stelle di neutroni i neutroni arrivano più in fretta di quanto i nuclei possano decadere; poi i nuclei ricchi di neutroni decadono di nuovo verso la stabilità.</p>
  <div class="ctl"><label for="st-rt">Ritorno per decadimento</label><input id="st-rt" type="range" data-bind="rt" min="0" max="1" step="0.01" value="0"></div>
</div>
<div class="step">
  <h3>I numeri magici creano picchi</h3>
  <p>I nuclei con 50, 82 o 126 neutroni catturano a malapena, così la materia si accumula lì: picchi s a stronzio, bario e piombo, picchi r un po' più leggeri.</p>
  <div class="btns"><button class="btn ghost" data-act="stS" aria-pressed="true">Picchi del processo s</button> <button class="btn ghost" data-act="stR" aria-pressed="true">Picchi del processo r</button></div>
</div>
<div class="step">
  <h3>Raro dove catturare è facile</h3>
  <p>Per gli isotopi prodotti solo dal processo s, l'abbondanza Nₛ per la sezione d'urto di cattura σ resta quasi costante tra due numeri magici. Qui σ è il valore calcolato da INCOGNITA a 30 keV.</p>
  <div class="btns"><button class="btn ghost" data-act="stvs" aria-pressed="false">σ</button> <button class="btn ghost" data-act="stvn" aria-pressed="false">Nₛ</button> <button class="btn ghost" data-act="stvsn" aria-pressed="true">σ × Nₛ</button></div>
</div>
<div class="step">
  <h3>Confrontato con le misure</h3>
  <p>I valori a 30 keV di INCOGNITA divisi per quelli misurati, per 94 nuclidi stabili (<a href="scoreboard.html">classifica</a>).</p>
</div>`,
};

Object.assign(WT.L.labels, {
  " (scaled to a measured value)": " (scalato su un valore misurato)",
  " (σ scaled to a measured value)": " (σ scalata su un valore misurato)",
  "{a} % above measured": "{a} % sopra il misurato",
  "{a} % below measured": "{a} % sotto il misurato",
  "{a} nuclides · typical difference {b} %": "{a} nuclidi · scarto tipico {b} %",
  "{a} stable nuclides · typical difference {b} % (median), rms {c} %": "{a} nuclidi stabili · scarto tipico {b} % (mediana), rms {c} %",
  "{a}: INCOGNITA's engine {b} (the library then scales to it)": "{a}: motore di INCOGNITA {b} (poi la libreria viene scalata su di esso)",
  "↑ protons Z": "↑ protoni Z",
  "A = {a}: mostly {b}, {c} atoms per million silicon": "A = {a}: soprattutto {b}, {c} atomi per milione di silicio",
  "A ≈ {#}": "A ≈ {#}",
  "abundances: Lodders, Palme & Gail {#}": "abbondanze: Lodders, Palme & Gail {#}",
  "abundances: Lodders, Palme & Gail {#} · point at the curve": "abbondanze: Lodders, Palme & Gail {#} · punta la curva",
  "atoms per {#}⁶ silicon": "atomi per {#}⁶ di silicio",
  "atoms per million silicon atoms (Solar System)": "atomi per milione di atomi di silicio (Sistema solare)",
  "Ba": "Ba",
  "Ba{#}": "Ba{#}",
  "beta decay (n → p)": "decadimento beta (n → p)",
  "beta decays carry them back, mass number A fixed": "i decadimenti beta li riportano indietro, con il numero di massa A fisso",
  "beta decays, A fixed": "decadimenti beta, A fisso",
  "Big Bang": "Big Bang",
  "decayed back: each lands on the most neutron-rich stable isobar": "tornati per decadimento: ciascuno finisce sull'isobaro stabile più ricco di neutroni",
  "decayed back: r-made stable isotopes": "tornati per decadimento: isotopi stabili del processo r",
  "drag along the path": "trascina lungo il percorso",
  "drag along the path, or use the slider": "trascina lungo il percorso, o usa il cursore",
  "end of the road: Bi{#} → Po{#} → alpha decay back to Pb{#}": "fine della strada: Bi{#} → Po{#} → decadimento alfa di nuovo a Pb{#}",
  "end: the lead–bismuth cycle": "fine: il ciclo piombo-bismuto",
  "Fe": "Fe",
  "flat between magic numbers, steps down at each": "piatto tra numeri magici, un gradino in giù a ciascuno",
  "fusion": "fusione",
  "fusion in stars": "fusione nelle stelle",
  "H": "H",
  "He": "He",
  "INCOGNITA ÷ measured, {#} keV": "INCOGNITA ÷ misurato, {#} keV",
  "INCOGNITA: capture at {#} keV (MACS)": "INCOGNITA: cattura a {#} keV (MACS)",
  "INCOGNITA's {#} keV capture rate (MACS) ÷ measured": "tasso di cattura di INCOGNITA a {#} keV (MACS) ÷ misurato",
  "Lodders et al. {#}": "Lodders et al. {#}",
  "Lu{#}": "Lu{#}",
  "made by neutron capture": "prodotti per cattura neutronica",
  "magic N: captures poorly, matter piles up": "N magico: cattura poco, la materia si accumula",
  "magic neutron number: it captures poorly, so matter piles up here": "numero magico di neutroni: cattura poco, quindi la materia si accumula qui",
  "mass number A": "numero di massa A",
  "mass number A (protons + neutrons)": "numero di massa A (protoni + neutroni)",
  "mb": "mb",
  "N = {#}": "N = {#}",
  "nearly flat between magic numbers, a step down at each": "quasi piatto tra numeri magici, un gradino in giù a ciascuno",
  "neutron capture": "cattura neutronica",
  "neutrons N →": "neutroni N →",
  "Nₛ alone jumps around the other way": "Nₛ da solo salta nel verso opposto",
  "Nₛ alone: scattered": "Nₛ da solo: sparso",
  "O": "O",
  "Pb": "Pb",
  "Pb{#}": "Pb{#}",
  "peaks: sources Lodders et al. {#}": "picchi: fonti Lodders et al. {#}",
  "plus a weaker s-process (massive stars)": "più un processo s più debole (stelle massicce)",
  "r {#}": "r {#}",
  "r-path: illustration": "percorso r: illustrazione",
  "r-peak Pt": "picco r Pt",
  "r-peak Se, Kr": "picco r Se, Kr",
  "r-peak Te, Xe": "picco r Te, Xe",
  "r-process: a flood of neutrons makes very neutron-rich nuclei": "processo r: un'ondata di neutroni crea nuclei molto ricchi di neutroni",
  "r-process: very neutron-rich nuclei": "processo r: nuclei molto ricchi di neutroni",
  "ringed: s-only · measured: KADoNiS": "cerchiati: solo s · misurati: KADoNiS",
  "ringed: s-only isotopes · measured: compiled values (KADoNiS) · a development comparison, not a blind test": "cerchiati: isotopi solo s · misurati: valori compilati (KADoNiS) · un confronto di sviluppo, non un test alla cieca",
  "s Ba": "s Ba",
  "s Pb": "s Pb",
  "s Sr": "s Sr",
  "s-only isotopes · bars: INCOGNITA {#} %": "isotopi solo s · barre: INCOGNITA {#} %",
  "s-only isotopes · σ: INCOGNITA (bars: its {#} % range; open circle: scaled to a measurement) · Nₛ: Lodders et al. {#}": "isotopi solo s · σ: INCOGNITA (barre: il suo intervallo al {#} %; cerchio vuoto: scalato su una misura) · Nₛ: Lodders et al. {#}",
  "s-peak Ba": "picco s Ba",
  "s-peak Pb": "picco s Pb",
  "s-peak Sr": "picco s Sr",
  "seen in {#}: merger GW{#}": "osservata nel {#}: fusione GW{#}",
  "seen in {#}: the neutron-star merger GW{#} and its kilonova": "osservata nel {#}: la fusione di stelle di neutroni GW{#} e la sua kilonova",
  "Sm{#}": "Sm{#}",
  "Sn": "Sn",
  "Sr": "Sr",
  "Sr{#}": "Sr{#}",
  "wait": "attesa",
  "waiting point": "punto di attesa",
  "weak s-process too": "anche processo s debole",
  "σ × Nₛ (mb × atoms per {#}⁶ Si)": "σ × Nₛ (mb × atomi per {#}⁶ Si)",
  "σ × Nₛ (mb × atoms per million Si)": "σ × Nₛ (mb × atomi per milione di Si)",
  "σ alone jumps around from isotope to isotope": "σ da sola salta da un isotopo all'altro",
});
