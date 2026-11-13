/* Portuguese (Português): stars (De onde vêm os elementos) */
WT.L.ch.stars = {
  num: "Lição 1", title: "De onde vêm os elementos", short: "Estrelas",
  html: `
<div class="step">
  <h3>A fusão para no ferro</h3>
  <p>As estrelas fundem núcleos leves até ao ferro; quase tudo o que é mais pesado é construído juntando neutrões.</p>
</div>
<div class="step">
  <h3>O caminho lento</h3>
  <p>Nas estrelas gigantes os neutrões chegam raramente, por isso um núcleo instável sofre primeiro decaimento beta: o caminho ziguezagueia ao longo dos núcleos estáveis.</p>
  <div class="ctl"><label for="st-k">Capturas de neutrões</label><input id="st-k" type="range" data-bind="k" min="0" max="213" step="1" value="112"></div>
</div>
<div class="step">
  <h3>O caminho rápido</h3>
  <p>Numa fusão de estrelas de neutrões, os neutrões chegam mais depressa do que os núcleos conseguem decair; depois, os núcleos ricos em neutrões decaem de volta à estabilidade.</p>
  <div class="ctl"><label for="st-rt">Decair de volta</label><input id="st-rt" type="range" data-bind="rt" min="0" max="1" step="0.01" value="0"></div>
</div>
<div class="step">
  <h3>Os números mágicos fazem picos</h3>
  <p>Núcleos com 50, 82 ou 126 neutrões quase não capturam, por isso a matéria acumula-se aí: picos s no estrôncio, no bário e no chumbo, picos r um pouco mais leves.</p>
  <div class="btns"><button class="btn ghost" data-act="stS" aria-pressed="true">Picos do processo s</button> <button class="btn ghost" data-act="stR" aria-pressed="true">Picos do processo r</button></div>
</div>
<div class="step">
  <h3>Raro onde a captura é fácil</h3>
  <p>Para isótopos formados apenas pelo processo s, a abundância Nₛ vezes a secção eficaz de captura σ fica quase constante entre números mágicos. Aqui σ é o valor calculado pelo INCOGNITA a 30 keV.</p>
  <div class="btns"><button class="btn ghost" data-act="stvs" aria-pressed="false">σ</button> <button class="btn ghost" data-act="stvn" aria-pressed="false">Nₛ</button> <button class="btn ghost" data-act="stvsn" aria-pressed="true">σ × Nₛ</button></div>
</div>
<div class="step">
  <h3>Comparado com medições</h3>
  <p>Os valores a 30 keV do INCOGNITA divididos pelos medidos, para 94 nuclídeos estáveis (<a href="scoreboard.html">comparações</a>).</p>
</div>`,
};

Object.assign(WT.L.labels, {
  " (scaled to a measured value)": " (escalado a um valor medido)",
  " (σ scaled to a measured value)": " (σ escalada a um valor medido)",
  "{a} % above measured": "{a} % acima do medido",
  "{a} % below measured": "{a} % abaixo do medido",
  "{a} nuclides · typical difference {b} %": "{a} nuclídeos · diferença típica {b} %",
  "{a} stable nuclides · typical difference {b} % (median), rms {c} %": "{a} nuclídeos estáveis · diferença típica {b} % (mediana), rms {c} %",
  "{a}: INCOGNITA's engine {b} (the library then scales to it)": "{a}: motor do INCOGNITA {b} (a biblioteca é depois escalada a ele)",
  "↑ protons Z": "↑ protões Z",
  "A = {a}: mostly {b}, {c} atoms per million silicon": "A = {a}: sobretudo {b}, {c} átomos por milhão de silício",
  "A ≈ {#}": "A ≈ {#}",
  "abundances: Lodders, Palme & Gail {#}": "abundâncias: Lodders, Palme & Gail {#}",
  "abundances: Lodders, Palme & Gail {#} · point at the curve": "abundâncias: Lodders, Palme & Gail {#} · aponte para a curva",
  "atoms per {#}⁶ silicon": "átomos por {#}⁶ de silício",
  "atoms per million silicon atoms (Solar System)": "átomos por milhão de átomos de silício (Sistema Solar)",
  "Ba": "Ba",
  "Ba{#}": "Ba{#}",
  "beta decay (n → p)": "decaimento beta (n → p)",
  "beta decays carry them back, mass number A fixed": "os decaimentos beta trazem-nos de volta, com o número de massa A fixo",
  "beta decays, A fixed": "decaimentos beta, A fixo",
  "Big Bang": "Big Bang",
  "decayed back: each lands on the most neutron-rich stable isobar": "de volta: cada um acaba no isóbaro estável mais rico em neutrões",
  "decayed back: r-made stable isotopes": "de volta: isótopos estáveis formados pelo processo r",
  "drag along the path": "arraste ao longo do caminho",
  "drag along the path, or use the slider": "arraste ao longo do caminho, ou use o cursor",
  "end of the road: Bi{#} → Po{#} → alpha decay back to Pb{#}": "fim do caminho: Bi{#} → Po{#} → decaimento alfa de volta a Pb{#}",
  "end: the lead–bismuth cycle": "fim: o ciclo chumbo-bismuto",
  "Fe": "Fe",
  "flat between magic numbers, steps down at each": "plano entre números mágicos, um degrau para baixo em cada um",
  "fusion": "fusão",
  "fusion in stars": "fusão nas estrelas",
  "H": "H",
  "He": "He",
  "INCOGNITA ÷ measured, {#} keV": "INCOGNITA ÷ medido, {#} keV",
  "INCOGNITA: capture at {#} keV (MACS)": "INCOGNITA: captura a {#} keV (MACS)",
  "INCOGNITA's {#} keV capture rate (MACS) ÷ measured": "taxa de captura do INCOGNITA a {#} keV (MACS) ÷ medida",
  "Lodders et al. {#}": "Lodders et al. {#}",
  "Lu{#}": "Lu{#}",
  "made by neutron capture": "formados por captura de neutrões",
  "magic N: captures poorly, matter piles up": "N mágico: captura pouco, a matéria acumula-se",
  "magic neutron number: it captures poorly, so matter piles up here": "número mágico de neutrões: captura pouco, por isso a matéria acumula-se aqui",
  "mass number A": "número de massa A",
  "mass number A (protons + neutrons)": "número de massa A (protões + neutrões)",
  "mb": "mb",
  "N = {#}": "N = {#}",
  "nearly flat between magic numbers, a step down at each": "quase plano entre números mágicos, um degrau para baixo em cada um",
  "neutron capture": "captura de neutrões",
  "neutrons N →": "neutrões N →",
  "Nₛ alone jumps around the other way": "Nₛ sozinho salta no sentido contrário",
  "Nₛ alone: scattered": "Nₛ sozinho: disperso",
  "O": "O",
  "Pb": "Pb",
  "Pb{#}": "Pb{#}",
  "peaks: sources Lodders et al. {#}": "picos: fontes Lodders et al. {#}",
  "plus a weaker s-process (massive stars)": "mais um processo s mais fraco (estrelas massivas)",
  "r {#}": "r {#}",
  "r-path: illustration": "caminho r: ilustração",
  "r-peak Pt": "pico r Pt",
  "r-peak Se, Kr": "pico r Se, Kr",
  "r-peak Te, Xe": "pico r Te, Xe",
  "r-process: a flood of neutrons makes very neutron-rich nuclei": "processo r: uma enxurrada de neutrões cria núcleos muito ricos em neutrões",
  "r-process: very neutron-rich nuclei": "processo r: núcleos muito ricos em neutrões",
  "ringed: s-only · measured: KADoNiS": "com anel: só s · medidos: KADoNiS",
  "ringed: s-only isotopes · measured: compiled values (KADoNiS) · a development comparison, not an independent test": "com anel: isótopos só s · medidos: valores compilados (KADoNiS) · uma comparação de desenvolvimento, não um teste independente",
  "s Ba": "s Ba",
  "s Pb": "s Pb",
  "s Sr": "s Sr",
  "s-only isotopes · bars: INCOGNITA {#} %": "isótopos só s · barras: INCOGNITA {#} %",
  "s-only isotopes · σ: INCOGNITA (bars: its {#} % range; open circle: scaled to a measurement) · Nₛ: Lodders et al. {#}": "isótopos só s · σ: INCOGNITA (barras: o seu intervalo de {#} %; círculo aberto: escalado a uma medição) · Nₛ: Lodders et al. {#}",
  "s-peak Ba": "pico s Ba",
  "s-peak Pb": "pico s Pb",
  "s-peak Sr": "pico s Sr",
  "seen in {#}: merger GW{#}": "observada em {#}: fusão GW{#}",
  "seen in {#}: the neutron-star merger GW{#} and its kilonova": "observada em {#}: a fusão de estrelas de neutrões GW{#} e a sua kilonova",
  "Sm{#}": "Sm{#}",
  "Sn": "Sn",
  "Sr": "Sr",
  "Sr{#}": "Sr{#}",
  "wait": "espera",
  "waiting point": "ponto de espera",
  "weak s-process too": "também processo s fraco",
  "σ × Nₛ (mb × atoms per {#}⁶ Si)": "σ × Nₛ (mb × átomos por {#}⁶ Si)",
  "σ × Nₛ (mb × atoms per million Si)": "σ × Nₛ (mb × átomos por milhão de Si)",
  "σ alone jumps around from isotope to isotope": "σ sozinha salta de isótopo para isótopo",
});
