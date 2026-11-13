/* French (Français): stars (D'où viennent les éléments) */
WT.L.ch.stars = {
  num: "Leçon 1", title: "D'où viennent les éléments", short: "Étoiles",
  html: `
<div class="step">
  <h3>La fusion s'arrête au fer</h3>
  <p>Les étoiles fusionnent les noyaux légers jusqu'au fer ; presque tout ce qui est plus lourd se construit en ajoutant des neutrons.</p>
</div>
<div class="step">
  <h3>La voie lente</h3>
  <p>Dans les étoiles géantes, les neutrons arrivent rarement, si bien qu'un noyau instable subit d'abord une désintégration bêta : le chemin zigzague le long des noyaux stables.</p>
  <div class="ctl"><label for="st-k">Captures de neutrons</label><input id="st-k" type="range" data-bind="k" min="0" max="213" step="1" value="112"></div>
</div>
<div class="step">
  <h3>La voie rapide</h3>
  <p>Lors de la fusion de deux étoiles à neutrons, les neutrons affluent plus vite que les noyaux ne peuvent se désintégrer ; ensuite, les noyaux riches en neutrons redescendent vers la stabilité.</p>
  <div class="ctl"><label for="st-rt">Retour par désintégration</label><input id="st-rt" type="range" data-bind="rt" min="0" max="1" step="0.01" value="0"></div>
</div>
<div class="step">
  <h3>Les nombres magiques font des pics</h3>
  <p>Les noyaux à 50, 82 ou 126 neutrons ne capturent presque pas, donc la matière s'y accumule : pics s au strontium, au baryum et au plomb, pics r un peu plus légers.</p>
  <div class="btns"><button class="btn ghost" data-act="stS" aria-pressed="true">Pics du processus s</button> <button class="btn ghost" data-act="stR" aria-pressed="true">Pics du processus r</button></div>
</div>
<div class="step">
  <h3>Rare là où la capture est facile</h3>
  <p>Pour les isotopes produits uniquement par le processus s, l'abondance Nₛ multipliée par la section efficace de capture σ reste presque constante entre deux nombres magiques. σ est ici la valeur calculée par INCOGNITA à 30 keV.</p>
  <div class="btns"><button class="btn ghost" data-act="stvs" aria-pressed="false">σ</button> <button class="btn ghost" data-act="stvn" aria-pressed="false">Nₛ</button> <button class="btn ghost" data-act="stvsn" aria-pressed="true">σ × Nₛ</button></div>
</div>
<div class="step">
  <h3>Confronté aux mesures</h3>
  <p>Les valeurs à 30 keV d'INCOGNITA divisées par les valeurs mesurées, pour 94 nucléides stables (<a href="scoreboard.html">comparaisons</a>).</p>
</div>`,
};

Object.assign(WT.L.labels, {
  " (scaled to a measured value)": " (recalé sur une valeur mesurée)",
  " (σ scaled to a measured value)": " (σ recalé sur une valeur mesurée)",
  "{a} % above measured": "{a} % au-dessus de la mesure",
  "{a} % below measured": "{a} % en dessous de la mesure",
  "{a} nuclides · typical difference {b} %": "{a} nucléides · écart typique {b} %",
  "{a} stable nuclides · typical difference {b} % (median), rms {c} %": "{a} nucléides stables · écart typique {b} % (médiane), rms {c} %",
  "{a}: INCOGNITA σ = {b} mb": "{a} : INCOGNITA σ = {b} mb",
  "{a}: INCOGNITA σ = {b} mb, {c}": "{a} : INCOGNITA σ = {b} mb, {c}",
  "{a}: INCOGNITA's engine {b} (the library then scales to it)": "{a} : moteur d'INCOGNITA {b} (la bibliothèque est ensuite recalée dessus)",
  "{a}: σ = {b} mb × Nₛ = {c} → σNₛ = {d}": "{a} : σ = {b} mb × Nₛ = {c} → σNₛ = {d}",
  "↑ protons Z": "↑ protons Z",
  "A = {a}: mostly {b}, {c} atoms per million silicon": "A = {a} : surtout {b}, {c} atomes par million de silicium",
  "A ≈ {#}": "A ≈ {#}",
  "abundances: Lodders, Palme & Gail {#}": "abondances : Lodders, Palme & Gail {#}",
  "abundances: Lodders, Palme & Gail {#} · point at the curve": "abondances : Lodders, Palme & Gail {#} · pointez la courbe",
  "atoms per {#}⁶ silicon": "atomes pour {#}⁶ silicium",
  "atoms per million silicon atoms (Solar System)": "atomes par million d'atomes de silicium (Système solaire)",
  "Ba": "Ba",
  "Ba{#}": "Ba{#}",
  "beta decay (n → p)": "désintégration bêta (n → p)",
  "beta decays carry them back, mass number A fixed": "les désintégrations bêta les ramènent, nombre de masse A inchangé",
  "beta decays, A fixed": "désintégrations bêta, A fixe",
  "Big Bang": "Big Bang",
  "decayed back: each lands on the most neutron-rich stable isobar": "retour par désintégration : chacun aboutit à l'isobare stable le plus riche en neutrons",
  "decayed back: r-made stable isotopes": "retour par désintégration : isotopes stables issus du processus r",
  "drag along the path": "faites glisser le long du chemin",
  "drag along the path, or use the slider": "faites glisser le long du chemin, ou utilisez le curseur",
  "end of the road: Bi{#} → Po{#} → alpha decay back to Pb{#}": "fin du chemin : Bi{#} → Po{#} → désintégration alpha vers Pb{#}",
  "end: the lead–bismuth cycle": "fin : le cycle plomb-bismuth",
  "Fe": "Fe",
  "flat between magic numbers, steps down at each": "plat entre nombres magiques, une marche vers le bas à chacun",
  "fusion": "fusion",
  "fusion in stars": "fusion dans les étoiles",
  "H": "H",
  "He": "He",
  "INCOGNITA ÷ measured, {#} keV": "INCOGNITA ÷ mesure, {#} keV",
  "INCOGNITA: capture at {#} keV (MACS)": "INCOGNITA : capture à {#} keV (MACS)",
  "INCOGNITA's {#} keV capture rate (MACS) ÷ measured": "taux de capture d'INCOGNITA à {#} keV (MACS) ÷ mesure",
  "Lodders et al. {#}": "Lodders et al. {#}",
  "Lu{#}": "Lu{#}",
  "made by neutron capture": "formés par capture de neutrons",
  "magic N: captures poorly, matter piles up": "N magique : capture peu, la matière s'accumule",
  "magic neutron number: it captures poorly, so matter piles up here": "nombre magique de neutrons : il capture peu, donc la matière s'accumule ici",
  "mass number A": "nombre de masse A",
  "mass number A (protons + neutrons)": "nombre de masse A (protons + neutrons)",
  "mb": "mb",
  "N = {#}": "N = {#}",
  "nearly flat between magic numbers, a step down at each": "presque plat entre nombres magiques, une marche vers le bas à chacun",
  "neutron capture": "capture de neutrons",
  "neutrons N →": "neutrons N →",
  "Nₛ alone jumps around the other way": "Nₛ seul saute dans l'autre sens",
  "Nₛ alone: scattered": "Nₛ seul : dispersé",
  "O": "O",
  "Pb": "Pb",
  "Pb{#}": "Pb{#}",
  "peaks: sources Lodders et al. {#}": "pics : sources Lodders et al. {#}",
  "plus a weaker s-process (massive stars)": "plus un processus s plus faible (étoiles massives)",
  "r {#}": "r {#}",
  "r-path: illustration": "chemin r : illustration",
  "r-peak Pt": "pic r Pt",
  "r-peak Se, Kr": "pic r Se, Kr",
  "r-peak Te, Xe": "pic r Te, Xe",
  "r-process: a flood of neutrons makes very neutron-rich nuclei": "processus r : un flot de neutrons crée des noyaux très riches en neutrons",
  "r-process: very neutron-rich nuclei": "processus r : noyaux très riches en neutrons",
  "ringed: s-only · measured: KADoNiS": "cerclés : s purs · mesures : KADoNiS",
  "ringed: s-only isotopes · measured: compiled values (KADoNiS) · a development comparison, not an independent test": "cerclés : isotopes s purs · mesures : valeurs compilées (KADoNiS) · une comparaison de développement, pas un test indépendant",
  "s Ba": "s Ba",
  "s Pb": "s Pb",
  "s Sr": "s Sr",
  "s-only isotopes · bars: INCOGNITA {#} %": "isotopes s purs · barres : INCOGNITA {#} %",
  "s-only isotopes · σ: INCOGNITA (bars: its {#} % range; open circle: scaled to a measurement) · Nₛ: Lodders et al. {#}": "isotopes s purs · σ : INCOGNITA (barres : son intervalle à {#} % ; cercle vide : recalé sur une mesure) · Nₛ : Lodders et al. {#}",
  "s-peak Ba": "pic s Ba",
  "s-peak Pb": "pic s Pb",
  "s-peak Sr": "pic s Sr",
  "seen in {#}: merger GW{#}": "observée en {#} : fusion GW{#}",
  "seen in {#}: the neutron-star merger GW{#} and its kilonova": "observée en {#} : la fusion d'étoiles à neutrons GW{#} et sa kilonova",
  "Sm{#}": "Sm{#}",
  "Sn": "Sn",
  "Sr": "Sr",
  "Sr{#}": "Sr{#}",
  "wait": "attente",
  "waiting point": "point d'attente",
  "weak s-process too": "processus s faible aussi",
  "σ × Nₛ (mb × atoms per {#}⁶ Si)": "σ × Nₛ (mb × atomes pour {#}⁶ Si)",
  "σ × Nₛ (mb × atoms per million Si)": "σ × Nₛ (mb × atomes par million de Si)",
  "σ alone jumps around from isotope to isotope": "σ seul saute d'un isotope à l'autre",
});
