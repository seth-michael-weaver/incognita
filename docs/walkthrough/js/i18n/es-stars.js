/* Spanish (Español): stars (De dónde vienen los elementos) */
WT.L.ch.stars = {
  num: "Lección 1", title: "De dónde vienen los elementos", short: "Estrellas",
  html: `
<div class="step">
  <h3>La fusión se detiene en el hierro</h3>
  <p>Las estrellas fusionan núcleos ligeros hasta el hierro; casi todo lo más pesado se construye añadiendo neutrones.</p>
</div>
<div class="step">
  <h3>El camino lento</h3>
  <p>En las estrellas gigantes los neutrones llegan rara vez, así que un núcleo inestable sufre antes una desintegración beta: el camino zigzaguea a lo largo de los núcleos estables.</p>
  <div class="ctl"><label for="st-k">Capturas de neutrones</label><input id="st-k" type="range" data-bind="k" min="0" max="213" step="1" value="112"></div>
</div>
<div class="step">
  <h3>El camino rápido</h3>
  <p>En una fusión de estrellas de neutrones, los neutrones llegan más deprisa de lo que los núcleos pueden desintegrarse; después, los núcleos ricos en neutrones vuelven a la estabilidad desintegrándose.</p>
  <div class="ctl"><label for="st-rt">Vuelta por desintegración</label><input id="st-rt" type="range" data-bind="rt" min="0" max="1" step="0.01" value="0"></div>
</div>
<div class="step">
  <h3>Los números mágicos crean picos</h3>
  <p>Los núcleos con 50, 82 o 126 neutrones apenas capturan, así que la materia se acumula ahí: picos s en el estroncio, el bario y el plomo, picos r algo más ligeros.</p>
  <div class="btns"><button class="btn ghost" data-act="stS" aria-pressed="true">Picos del proceso s</button> <button class="btn ghost" data-act="stR" aria-pressed="true">Picos del proceso r</button></div>
</div>
<div class="step">
  <h3>Escaso donde capturar es fácil</h3>
  <p>Para los isótopos formados solo por el proceso s, la abundancia Nₛ por la sección eficaz de captura σ se mantiene casi constante entre números mágicos. Aquí σ es el valor calculado por INCOGNITA a 30 keV.</p>
  <div class="btns"><button class="btn ghost" data-act="stvs" aria-pressed="false">σ</button> <button class="btn ghost" data-act="stvn" aria-pressed="false">Nₛ</button> <button class="btn ghost" data-act="stvsn" aria-pressed="true">σ × Nₛ</button></div>
</div>
<div class="step">
  <h3>Contrastado con medidas</h3>
  <p>Los valores a 30 keV de INCOGNITA divididos por los medidos, para 94 nucleidos estables (<a href="scoreboard.html">comparaciones</a>).</p>
</div>`,
};

Object.assign(WT.L.labels, {
  " (scaled to a measured value)": " (escalado a un valor medido)",
  " (σ scaled to a measured value)": " (σ escalada a un valor medido)",
  "{a} % above measured": "{a} % por encima de lo medido",
  "{a} % below measured": "{a} % por debajo de lo medido",
  "{a} nuclides · typical difference {b} %": "{a} nucleidos · diferencia típica {b} %",
  "{a} stable nuclides · typical difference {b} % (median), rms {c} %": "{a} nucleidos estables · diferencia típica {b} % (mediana), rms {c} %",
  "{a}: INCOGNITA's engine {b} (the library then scales to it)": "{a}: motor de INCOGNITA {b} (luego la biblioteca se escala a él)",
  "↑ protons Z": "↑ protones Z",
  "A = {a}: mostly {b}, {c} atoms per million silicon": "A = {a}: sobre todo {b}, {c} átomos por millón de silicio",
  "A ≈ {#}": "A ≈ {#}",
  "abundances: Lodders, Palme & Gail {#}": "abundancias: Lodders, Palme & Gail {#}",
  "abundances: Lodders, Palme & Gail {#} · point at the curve": "abundancias: Lodders, Palme & Gail {#} · señala la curva",
  "atoms per {#}⁶ silicon": "átomos por {#}⁶ de silicio",
  "atoms per million silicon atoms (Solar System)": "átomos por millón de átomos de silicio (Sistema Solar)",
  "Ba": "Ba",
  "Ba{#}": "Ba{#}",
  "beta decay (n → p)": "desintegración beta (n → p)",
  "beta decays carry them back, mass number A fixed": "las desintegraciones beta los devuelven, con el número másico A fijo",
  "beta decays, A fixed": "desintegraciones beta, A fijo",
  "Big Bang": "Big Bang",
  "decayed back: each lands on the most neutron-rich stable isobar": "de vuelta: cada uno acaba en el isóbaro estable más rico en neutrones",
  "decayed back: r-made stable isotopes": "de vuelta: isótopos estables formados por el proceso r",
  "drag along the path": "arrastra a lo largo del camino",
  "drag along the path, or use the slider": "arrastra a lo largo del camino o usa el deslizador",
  "end of the road: Bi{#} → Po{#} → alpha decay back to Pb{#}": "fin del camino: Bi{#} → Po{#} → desintegración alfa de vuelta a Pb{#}",
  "end: the lead–bismuth cycle": "fin: el ciclo plomo-bismuto",
  "Fe": "Fe",
  "flat between magic numbers, steps down at each": "plano entre números mágicos, un escalón hacia abajo en cada uno",
  "fusion": "fusión",
  "fusion in stars": "fusión en las estrellas",
  "H": "H",
  "He": "He",
  "INCOGNITA ÷ measured, {#} keV": "INCOGNITA ÷ medido, {#} keV",
  "INCOGNITA: capture at {#} keV (MACS)": "INCOGNITA: captura a {#} keV (MACS)",
  "INCOGNITA's {#} keV capture rate (MACS) ÷ measured": "tasa de captura de INCOGNITA a {#} keV (MACS) ÷ medida",
  "Lodders et al. {#}": "Lodders et al. {#}",
  "Lu{#}": "Lu{#}",
  "made by neutron capture": "formados por captura de neutrones",
  "magic N: captures poorly, matter piles up": "N mágico: captura poco, la materia se acumula",
  "magic neutron number: it captures poorly, so matter piles up here": "número mágico de neutrones: captura poco, así que la materia se acumula aquí",
  "mass number A": "número másico A",
  "mass number A (protons + neutrons)": "número másico A (protones + neutrones)",
  "mb": "mb",
  "N = {#}": "N = {#}",
  "nearly flat between magic numbers, a step down at each": "casi plano entre números mágicos, un escalón hacia abajo en cada uno",
  "neutron capture": "captura de neutrones",
  "neutrons N →": "neutrones N →",
  "Nₛ alone jumps around the other way": "Nₛ solo salta en sentido contrario",
  "Nₛ alone: scattered": "Nₛ solo: disperso",
  "O": "O",
  "Pb": "Pb",
  "Pb{#}": "Pb{#}",
  "peaks: sources Lodders et al. {#}": "picos: fuentes Lodders et al. {#}",
  "plus a weaker s-process (massive stars)": "más un proceso s más débil (estrellas masivas)",
  "r {#}": "r {#}",
  "r-path: illustration": "camino r: ilustración",
  "r-peak Pt": "pico r Pt",
  "r-peak Se, Kr": "pico r Se, Kr",
  "r-peak Te, Xe": "pico r Te, Xe",
  "r-process: a flood of neutrons makes very neutron-rich nuclei": "proceso r: una avalancha de neutrones crea núcleos muy ricos en neutrones",
  "r-process: very neutron-rich nuclei": "proceso r: núcleos muy ricos en neutrones",
  "ringed: s-only · measured: KADoNiS": "con anillo: solo s · medidos: KADoNiS",
  "ringed: s-only isotopes · measured: compiled values (KADoNiS) · a development comparison, not an independent test": "con anillo: isótopos solo s · medidos: valores recopilados (KADoNiS) · una comparación de desarrollo, no una prueba independiente",
  "s Ba": "s Ba",
  "s Pb": "s Pb",
  "s Sr": "s Sr",
  "s-only isotopes · bars: INCOGNITA {#} %": "isótopos solo s · barras: INCOGNITA {#} %",
  "s-only isotopes · σ: INCOGNITA (bars: its {#} % range; open circle: scaled to a measurement) · Nₛ: Lodders et al. {#}": "isótopos solo s · σ: INCOGNITA (barras: su intervalo del {#} %; círculo abierto: escalado a una medida) · Nₛ: Lodders et al. {#}",
  "s-peak Ba": "pico s Ba",
  "s-peak Pb": "pico s Pb",
  "s-peak Sr": "pico s Sr",
  "seen in {#}: merger GW{#}": "observada en {#}: fusión GW{#}",
  "seen in {#}: the neutron-star merger GW{#} and its kilonova": "observada en {#}: la fusión de estrellas de neutrones GW{#} y su kilonova",
  "Sm{#}": "Sm{#}",
  "Sn": "Sn",
  "Sr": "Sr",
  "Sr{#}": "Sr{#}",
  "wait": "espera",
  "waiting point": "punto de espera",
  "weak s-process too": "también proceso s débil",
  "σ × Nₛ (mb × atoms per {#}⁶ Si)": "σ × Nₛ (mb × átomos por {#}⁶ Si)",
  "σ × Nₛ (mb × atoms per million Si)": "σ × Nₛ (mb × átomos por millón de Si)",
  "σ alone jumps around from isotope to isotope": "σ sola salta de un isótopo a otro",
});
