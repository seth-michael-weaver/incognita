/* French: resonance (chapter 10) */
WT.L.ch.resonance = {
  num: "Chapitre 10", title: "Des pics étroits", short: "Résonances",
  lead: "À énergie suffisamment basse, un neutron ne voit plus un noyau lisse et moyenné. Il voit les niveaux d'énergie individuels du noyau composé, un par un.",
  html: `
<div class="step">
  <p>Chaque pic est une <b>résonance</b> : un niveau d'énergie du noyau composé dans lequel un neutron ayant exactement cette énergie peut tomber. Sa hauteur est la section efficace de <b>capture</b> à cet endroit (neutron absorbé, photons émis), en échelle logarithmique ; sa largeur est la largeur de résonance Γ, dessinée environ cent fois plus large qu'elle ne l'est.</p>
  <div class="ctl"><label for="res-e">Énergie du neutron (eV)</label><input id="res-e" type="range" data-bind="En" min="0.5" max="300" step="0.1" value="30"><output data-show="En" data-fmt="1"></output></div>
  <p>Le neutron avance par sauts en énergie ; là où il atterrit, il peut être capturé, dans un éclair de photons. Sur un pic, la section efficace atteint des milliers de barns et la capture est presque certaine ; entre les pics, elle n'est que de quelques barns. Faites glisser l'énergie pour le placer sur un pic, puis entre deux.</p>
</div>
<div class="step">
  <h3>Les pics gardent leurs distances</h3>
  <p>La rangée du milieu montre comment se placent les vrais niveaux : deux niveaux de même spin et de même parité se repoussent, si bien que les quasi-coïncidences sont rares. La <b>théorie des matrices aléatoires</b> décrit ce motif. Des positions vraiment aléatoires (rangée du haut) forment des amas et laissent des trous.</p>
  <div class="btns"><button class="btn" data-act="again">Tirer à nouveau</button></div>
  <p>Tirez à nouveau pour obtenir un autre échantillon. ⟨r̃⟩ compare chaque espacement au suivant : environ 0,39 pour des positions aléatoires, 0,53 pour des niveaux qui se repoussent ; le code utilise le motif avec répulsion. Mélanger deux séquences, par exemple deux spins (rangée du bas), masque en partie la répulsion.</p>
</div>
<div class="step">
  <h3>Les hauteurs varient énormément</h3>
  <p>La hauteur de chaque pic est maintenant sa <b>largeur neutronique</b> Γ<sub>n</sub>, en échelle linéaire : la force avec laquelle le niveau se couple à un neutron. Le chapeau jaune est sa largeur γ Γ<sub>γ</sub>, la rapidité avec laquelle il émet des photons ; elle somme des centaines de chemins de photons, elle est donc presque la même pour tous les niveaux.</p>
  <div class="btns"><button class="btn" data-act="roll">Tirer une largeur</button><button class="btn ghost" data-act="equal">Largeurs égales</button><button class="btn ghost" data-act="pt">Porter–Thomas</button></div>
  <p>Un niveau n'a qu'une seule façon de se briser en neutron plus cible : sa largeur se comporte donc comme le carré d'un unique nombre tiré d'une courbe en cloche. Tirez-en un : la bille tombe en <i>x</i>, <i>x</i>² devient la hauteur du pic suivant, et un point tombe dans la pile. La pile se concentre près de zéro avec une longue queue : c'est la loi de <b>Porter–Thomas</b>. La plupart des niveaux sont faibles, quelques-uns énormes. « Largeurs égales » montre à la place une rangée de pics moyens.</p>
</div>
<div class="step">
  <h3>Une série à partir de quatre nombres</h3>
  <p>Les pics proviennent maintenant de quatre moyennes que vous pouvez régler. Pour un noyau non mesuré, seules ces moyennes peuvent être prédites : l'espacement moyen <i>D</i><sub>0</sub> ; les <b>fonctions de force</b> <i>S</i><sub>0</sub> et <i>S</i><sub>1</sub>, la largeur neutronique moyenne par unité d'espacement pour les neutrons en onde s (de plein fouet) et en onde p (décentrés) ; et la largeur γ moyenne. À partir de celles-ci, le code construit une <b>série de résonances</b> : un ensemble aléatoire de niveaux ayant ces moyennes.</p>
  <div class="ctl"><label for="res-d0">Espacement D₀ (eV)</label><input id="res-d0" type="range" data-bind="D0" min="3" max="60" step="0.5" value="20"><output data-show="D0" data-fmt="1"></output></div>
  <div class="ctl"><label for="res-s0">Fonction de force S₀ (×10⁻⁴)</label><input id="res-s0" type="range" data-bind="S0" min="0.2" max="3" step="0.05" value="1"><output data-show="S0" data-fmt="2"></output></div>
  <div class="ctl"><label for="res-gg">Largeur γ ⟨Γγ⟩ (meV)</label><input id="res-gg" type="range" data-bind="Gg" min="10" max="80" step="1" value="23"><output data-show="Gg" data-fmt="0"></output></div>
  <p>Faites glisser <i>D</i><sub>0</sub> et les pics s'écartent ou se resserrent. Les pics pleins sont des niveaux en onde s (parité positive), les pics en contour des niveaux en onde p (parité négative). Les largeurs neutroniques croissent comme √<i>E</i> pour les ondes s et comme <i>E</i><sup>3/2</sup> pour les ondes p : les pics en contour commencent petits et grandissent vers la droite.</p>
</div>
<div class="step">
  <h3>En bas, dans le domaine thermique</h3>
  <p>Les mêmes pics sur une échelle d'énergie logarithmique, jusqu'aux millièmes d'eV. Les neutrons d'un réacteur ralentissent en rebondissant sur des noyaux légers et perdent à peu près la même fraction de leur énergie à chaque fois : ici, tous les sauts ont donc la même longueur. Certains sont capturés par les pics en chemin.</p>
  <div class="btns"><button class="btn" data-act="slow">Ralentir 10 neutrons</button></div>
  <p>Ceux qui passent se stabilisent à température ambiante, 0,025 eV, l'énergie <b>thermique</b>, bien au-dessous du premier pic. Là, la section efficace, l'aire du disque, est la somme des queues des résonances, y compris de niveaux liés situés juste sous zéro ; les queues croissent comme 1/<i>v</i> (<i>v</i> étant la vitesse du neutron), si bien que le plancher monte vers la gauche. Ce qui est capturé pendant la descente se mesure par l'<b>intégrale de résonance</b> : la section efficace au-dessus de 0,5 eV, chaque énergie étant pondérée par 1/<i>E</i>.</p>
</div>
<div class="step">
  <h3>Seule la statistique est prévisible</h3>
  <p>Chaque rangée est une série tirée des quatre mêmes nombres, avec un disque dont l'aire est sa section efficace de capture thermique. Le crochet s'étend jusqu'au pic qui fixe cette valeur, en général le plus proche ; sa distance change d'une série à l'autre, et le disque varie d'un facteur dix ou plus.</p>
  <div class="btns"><button class="btn" data-act="draw1">Tirer une série</button><button class="btn ghost" data-act="more">En tirer 20</button></div>
  <p>Chaque valeur tombe dans la pile de droite. Pour un noyau non mesuré, la réponse est une dispersion de valeurs, pas un nombre unique, et aucun modèle meilleur ne peut la réduire. L'intégrale de résonance, une somme sur de nombreux pics, se disperse moins. Là où les niveaux sont espacés de plus de 10 keV environ, comme dans les noyaux légers, aucun n'est proche du domaine thermique : la capture y est directe, et le code refuse de répondre.</p>
  <div class="aside">Dans le code : <code>physics/resonance/ladder.py</code> (espacements des matrices aléatoires, largeurs de Porter–Thomas, sections efficaces de Breit–Wigner, capture thermique et intégrale de résonance sur un ensemble de séries), <code>ladder_statistics.py</code> (les mêmes lois testées sur des séries mesurées), <code>ensemble_runner.py</code>. Ils tournent à côté du moteur de réactions, pas à l'intérieur.</div>
</div>`,
};
Object.assign(WT.L.labels, {
  // forest
  "{#} eV": "{#} eV", "+{#} eV": "+{#} eV",
  "height: peak capture (log) · width Γ ×{#}": "hauteur : capture au pic (log) · largeur Γ ×{#}",
  "peak height: capture cross section (log scale) · width: resonance width Γ, drawn {#}× wide": "hauteur : section efficace de capture au pic (échelle log) · largeur Γ, dessinée {#}× plus large",
  "D₀ {#} eV · S₀ {#}×{#}⁻⁴ · S₁ {#}×{#}⁻⁴ · ⟨Γγ⟩ {#} meV": "D₀ {#} eV · S₀ {#}×{#}⁻⁴ · S₁ {#}×{#}⁻⁴ · ⟨Γγ⟩ {#} meV",
  "s-wave (+ parity)": "onde s (parité +)", "p-wave (− parity)": "onde p (parité −)",
  "caught {#} times in {#} landings": "capturé {#} fois sur {#} arrivées",
  "each peak: one level of the compound nucleus": "chaque pic : un niveau du noyau composé",
  "each peak: one level of the compound nucleus · about {#} eV apart": "chaque pic : un niveau du noyau composé · espacés d'environ {#} eV",
  // spacing
  "random positions (Poisson)": "positions aléatoires (Poisson)",
  "repelling levels (random-matrix)": "niveaux qui se repoussent (matrices aléatoires)",
  "two repelling sequences mixed": "deux séquences qui se repoussent, mélangées",
  "clumps and gaps · ⟨r̃⟩ ≈ {#}": "amas et trous · ⟨r̃⟩ ≈ {#}",
  "evenly kept apart · ⟨r̃⟩ ≈ {#}": "régulièrement espacés · ⟨r̃⟩ ≈ {#}",
  "repulsion half hidden · ⟨r̃⟩ ≈ {#}": "répulsion à moitié masquée · ⟨r̃⟩ ≈ {#}",
  "clumps and gaps · spacing ratio ⟨r̃⟩ ≈ {#}": "amas et trous · rapport d'espacements ⟨r̃⟩ ≈ {#}",
  "evenly kept apart · spacing ratio ⟨r̃⟩ ≈ {#}": "régulièrement espacés · rapport d'espacements ⟨r̃⟩ ≈ {#}",
  "repulsion half hidden · spacing ratio ⟨r̃⟩ ≈ {#}": "répulsion à moitié masquée · rapport d'espacements ⟨r̃⟩ ≈ {#}",
  "⟨r̃⟩: {#} if random, {#} for random-matrix": "⟨r̃⟩ : {#} si aléatoire, {#} pour les matrices aléatoires",
  "same average spacing in every row · ⟨r̃⟩: {#} if random, {#} for random-matrix": "même espacement moyen dans chaque rangée · ⟨r̃⟩ : {#} si aléatoire, {#} pour les matrices aléatoires",
  // Porter-Thomas
  "height: neutron width Γn (linear)": "hauteur : largeur neutronique Γn (linéaire)",
  "peak height: neutron width Γn, linear scale": "hauteur : largeur neutronique Γn, échelle linéaire",
  "yellow: γ width": "jaune : largeur γ",
  "yellow cap: γ width, nearly the same on every peak": "chapeau jaune : largeur γ, presque la même partout",
  "equal widths: every peak the average": "largeurs égales : tous les pics à la moyenne",
  "rolled widths": "largeurs tirées", "pile of rolled widths": "pile des largeurs tirées",
  "× average": "× moyenne", "(in units of the average)": "(en unités de la moyenne)",
  "dashed: Porter–Thomas": "tirets : Porter–Thomas", "dashed: the Porter–Thomas law": "tirets : la loi de Porter–Thomas",
  "bell-curve number x": "nombre en cloche x",
  "x = {#}  →  x² = {#}": "x = {#}  →  x² = {#}",
  "press Roll a width": "appuyez sur Tirer une largeur",
  // thermal
  "bound level {#} eV": "niveau lié {#} eV",
  "a bound level at {#} eV: its tail lifts this end": "un niveau lié à {#} eV : sa queue relève cette extrémité",
  "resonance integral ≈ {#} b": "intégrale de résonance ≈ {#} b",
  "resonance integral above {#} eV ≈ {#} b": "intégrale de résonance au-dessus de {#} eV ≈ {#} b",
  "{#}/v": "{#}/v",
  "caught by a peak on the way down: {#} · reached thermal: {#}": "capturés par un pic en descendant : {#} · arrivés au thermique : {#}",
  "each hop: one bounce, the same fraction of energy lost": "chaque saut : un rebond, la même fraction d'énergie perdue",
  // ensemble
  "thermal neutron": "neutron thermique",
  "σ disc": "disque σ", "disc area = σ at {#} eV": "aire du disque = σ à {#} eV",
  "{#}k": "{#}k",
  "thermal σ (b)": "σ thermique (b)", "thermal σ, barns": "σ thermique, barns",
  "{#} ladders · thermal ×{#} · res. integral ×{#}": "{#} séries · thermique ×{#} · int. de rés. ×{#}",
});
// labels that carry a cross section printed as "12 b" or "3.4k b"
(function () {
  const L = WT.L.labels;
  for (const b of ["{#} b", "{#}k b"]) {
    L[b] = b;
    L[`σ ≈ ${b} · caught on {#} % of landings`] = `σ ≈ ${b} · capturé dans {#} % des arrivées`;
    L[`σ ≈ ${b} · caught on <{#} % of landings`] = `σ ≈ ${b} · capturé dans <{#} % des arrivées`;
    L[`thermal, {#} eV: σ ≈ ${b}`] = `thermique, {#} eV : σ ≈ ${b}`;
    L[`{#} ladders · thermal σ median ${b}, middle two thirds ×{#} · resonance integral only ×{#}`] =
      `{#} séries · σ thermique médiane ${b}, deux tiers centraux ×{#} · intégrale de résonance seulement ×{#}`;
  }
})();
