/* French: optical (Chapitre 14, Expert) */
WT.L.ch.optical = {
  num: "Chapitre 14", title: "Le modèle optique, résolu", short: "Modèle optique résolu",
  lead: "Le chapitre 2 a dessiné le potentiel optique comme une boule de verre trouble. Le voici tel que le moteur l'utilise : une paramétrisation globale, une équation de Schrödinger radiale intégrée pas à pas, et une condition de raccordement qui transforme l'onde en coefficients de transmission.",
  html: `
<div class="step">
  <h3>Le potentiel de Koning–Delaroche</h3>
  <p>Pour les neutrons et les protons sur des cibles sphériques, le choix par défaut est le potentiel de <b>Koning–Delaroche</b> (KD03) : des formes de Woods–Saxon dont les profondeurs varient régulièrement avec l'énergie, la masse de la cible et son excès de neutrons, d'après une formule globale ou, pour les noyaux que KD03 a ajustés un par un, comme le fer 56, d'après un ajustement local de même forme. L'image utilise la formule globale pour des neutrons sur le fer 56. Le puits réel (en bleu) lie ; les parties imaginaires (en rouge) absorbent, dans le volume et, surtout à basse énergie, dans une mince couche à la surface.</p>
  <div class="ctl"><label for="op-e">Énergie du neutron (MeV)</label><input id="op-e" type="range" data-bind="E" min="0.1" max="80" step="0.1" value="5"><output data-show="E" data-fmt="1"></output></div>
  <div class="formula">U(r) = −V<sub>V</sub> f(r) − iW<sub>V</sub> f(r) + 4i a<sub>D</sub>W<sub>D</sub> df<sub>D</sub>/dr + 2(V<sub>so</sub> + iW<sub>so</sub>) (1/r) df<sub>so</sub>/dr ⟨l·σ⟩</div>
  <p>Les neutrons sondes traversent à l'énergie choisie et s'estompent là où l'absorption mord : leur libre parcours moyen est ħ<i>v</i>/2|<i>W</i>|. Chaque profondeur est une fonction de <i>E</i> − <i>E</i><sub>F</sub>, mesurée à partir de l'énergie de Fermi : la profondeur réelle décroît lentement, l'absorption de surface <i>W</i><sub>D</sub> culmine vers 10 MeV, et l'absorption de volume <i>W</i><sub>V</sub> croît régulièrement jusqu'à prendre le dessus, au-delà d'environ 45 MeV ici.</p>
</div>
<div class="step">
  <h3>Intégrer l'équation radiale</h3>
  <p>Chaque onde partielle obéit à sa propre équation radiale. Le moteur l'intègre vers l'extérieur à partir de <i>r</i> = 0 par la <b>méthode de Numerov</b>, une règle à trois points précise à la puissance six du pas, à travers le potentiel complexe complet.</p>
  <div class="formula">u″<sub>lj</sub>(r) = [ l(l+1)/r² + (2μ/ħ²) U<sub>lj</sub>(r) − k² ] u<sub>lj</sub>(r)</div>
  <div class="ctl"><label for="op-l">Onde partielle l</label><input id="op-l" type="range" data-bind="L" min="0" max="10" step="1" value="1" data-instant><output data-show="L" data-fmt="0"></output></div>
  <div class="ctl"><label for="op-e2">Énergie du neutron (MeV)</label><input id="op-e2" type="range" data-bind="E" min="0.1" max="80" step="0.1" value="5"><output data-show="E" data-fmt="1"></output></div>
  <p>Le trait plein est l'onde dans le temps, Re[<i>u</i> e<sup>−iωt</sup>] ; les tirets montrent l'onde libre, comme si le noyau n'était pas là. Dans le puits, l'onde est plus courte (le neutron va plus vite) et plus petite (absorbée) ; à l'extérieur, elle ressort déphasée.</p>
</div>
<div class="step">
  <h3>De l'onde à S et T</h3>
  <p>Au-delà d'environ 12 fm, le potentiel s'est annulé et l'onde doit être un mélange d'une onde libre entrante et d'une onde libre sortante, <i>u</i> ∝ <i>H</i><sup>−</sup> − <i>S</i> <i>H</i><sup>+</sup>. Raccorder le <i>u</i> intégré en deux rayons fixe l'élément <i>S<sub>lj</sub></i> de la <b>matrice S</b> : l'amplitude sortante, avec sa phase.</p>
  <div class="btns"><button class="btn ghost" data-act="abs" aria-pressed="false">Couper l'absorption</button></div>
  <div class="formula">S<sub>lj</sub> = η<sub>lj</sub> e<sup>2iδ<sub>lj</sub></sup> ,  T<sub>lj</sub> = 1 − |S<sub>lj</sub>|²</div>
  <p>Le point est <i>S</i> dans le plan complexe, à l'intérieur du cercle unité ; sa traînée est le chemin parcouru quand l'énergie balaie de 0,1 à 40 MeV. Sans absorption, |<i>S</i>| = 1 : le point court sur le cercle, l'onde ne fait que changer de phase, et <i>T</i> = 0. La distance à l'intérieur du cercle est ce que reçoivent le noyau composé et toutes les autres réactions.</p>
</div>
<div class="step">
  <h3>Le spin-orbite sépare j</h3>
  <p>Le terme de <b>spin-orbite</b> est attractif pour <i>j</i> = <i>l</i> + ½ et répulsif pour <i>j</i> = <i>l</i> − ½. Il est faible, quelques MeV à la surface, mais il écarte les deux transmissions de chaque <i>l</i>, surtout près de l'onde partielle qui rase la surface.</p>
  <div class="ctl"><label for="op-e3">Énergie du neutron (MeV)</label><input id="op-e3" type="range" data-bind="E" min="0.1" max="80" step="0.1" value="5"><output data-show="E" data-fmt="1"></output></div>
  <div class="btns"><button class="btn ghost" data-act="so" aria-pressed="false">Couper le spin-orbite</button></div>
  <p>Hauser–Feshbach (chapitre 13) les utilise séparément ; additionnées avec leurs poids, (<i>l</i>+1)<i>T</i><sub>l,l+½</sub> + <i>l</i> <i>T</i><sub>l,l−½</sub>, elles donnent une section efficace de réaction presque inchangée. C'est pourquoi les sections efficaces totales contraignent à peine l'intensité du spin-orbite et qu'il faut des données de polarisation.</p>
</div>
<div class="step">
  <h3>Les sections efficaces</h3>
  <p>La somme des ondes partielles donne les observables sur lesquelles le potentiel est ajusté. La section efficace de réaction compte le flux retiré, la section efficace totale découle de l'amplitude vers l'avant, et leur différence est la diffusion élastique de forme.</p>
  <div class="formula">σ<sub>R</sub> = (π/k²) Σ<sub>l</sub> [(l+1)T<sub>l,l+½</sub> + l T<sub>l,l−½</sub>] ,  σ<sub>tot</sub> = (2π/k²) Σ<sub>lj</sub> (j+½)(1 − Re S<sub>lj</sub>)</div>
  <div class="ctl"><label for="op-e4">Énergie du neutron (MeV)</label><input id="op-e4" type="range" data-bind="E" min="0.2" max="50" step="0.1" value="5"><output data-show="E" data-fmt="1"></output></div>
  <p>KD03 a été ajusté sur de telles données pour de nombreux noyaux, de 1 keV à 200 MeV ; la section efficace totale du fer, entre 3,5 et 4 b à quelques MeV et 2,5 b à 14 MeV, en sort à environ 5 pour cent près sans ajustement propre à ce noyau, maxima larges compris : ils traduisent la taille du noyau rapportée à la longueur d'onde du neutron.</p>
</div>
<div class="step">
  <h3>L'extrémité de basse énergie</h3>
  <p>En dessous de quelques keV, seule l'onde s compte, et <i>T</i><sub>0</sub> croît comme √<i>E</i> : une pente d'un demi sur ce graphique log–log. La constante est la <b>fonction de force</b> <i>S</i><sub>0</sub> = <i>T</i><sub>0</sub>/(2π√<i>E</i>), avec <i>E</i> en eV, la même grandeur que les analyses de résonances mesurent sous la forme Σ Γ<sub>n</sub><sup>0</sup>/Δ<i>E</i>.</p>
  <p>Un potentiel global est surtout ajusté aux énergies du MeV, et son extrémité de basse énergie est son point faible. Pour le fer 56, celui-ci donne <i>S</i><sub>0</sub> ≈ 5,5 × 10⁻⁴, et l'ajustement local de KD03 presque autant, alors que la valeur mesurée (RIPL) est de 2,3 ± 0,6 × 10⁻⁴ : le fer se trouve près du sommet de la résonance de taille 3s, vers <i>A</i> ≈ 55, là où <i>S</i><sub>0</sub> est le plus sensible au potentiel. C'est pourquoi les <i>S</i><sub>0</sub> et <i>S</i><sub>1</sub> mesurés constituent une entrée séparée et facultative du moteur.</p>
  <div class="aside">Dans le code : <code>omp/parameters.py</code> (KD03 et les autres potentiels globaux), <code>omp/potential.py</code> (les facteurs de forme radiaux), <code>omp/schrodinger.py</code> (intégration de Numerov et raccordement, avec les fonctions coulombiennes par la méthode de Steed pour les particules chargées ; il remplace ECIS pour les cibles sphériques et est vérifié par rapport aux T<sub>lj</sub> d'ECIS), <code>ecis/</code> (le portage des voies couplées pour les cibles déformées), <code>omp/sfunc.py</code> (facultatif : S₀, S₁ mesurés). L'image résout elle-même l'équation, de façon non relativiste, pour des neutrons sur le fer 56.</div>
</div>`,
};
Object.assign(WT.L.labels, {
  // potential
  "{#} fm": "{#} fm", "{#} MeV": "{#} MeV", "{#} keV": "{#} keV", "{#} eV": "{#} eV", "{#} b": "{#} b",
  "real well, depth {#} MeV": "puits réel, profondeur {#} MeV",
  "surface absorption, peak {#} MeV": "absorption de surface, maximum {#} MeV",
  "volume absorption {#} MeV": "absorption de volume {#} MeV",
  "spin–orbit for l = {#}, j = {#}/{#}: {#} MeV": "spin-orbite pour l = {#}, j = {#}/{#} : {#} MeV",
  "E = {#} MeV": "E = {#} MeV",
  "mean free path: {#} fm at the surface, {#} fm in the centre": "libre parcours moyen : {#} fm à la surface, {#} fm au centre",
  "mean free path: {#} fm at the surface, > {#} fm in the centre": "libre parcours moyen : {#} fm à la surface, > {#} fm au centre",
  "mean free path: > {#} fm at the surface, {#} fm in the centre": "libre parcours moyen : > {#} fm à la surface, {#} fm au centre",
  "mean free path: > {#} fm at the surface, > {#} fm in the centre": "libre parcours moyen : > {#} fm à la surface, > {#} fm au centre",
  "real": "réel", "volume": "volume", "surface": "surface",
  "depths (MeV) against energy (MeV)": "profondeurs (MeV) en fonction de l'énergie (MeV)",
  // wave
  "potential: real (blue), imaginary (red)": "potentiel : réel (bleu), imaginaire (rouge)",
  "nuclear surface": "surface nucléaire",
  "l = {#}, j = {#}+½ · E = {#} MeV · |S| = {#} · δ = {#}° · T = {#}": "l = {#}, j = {#}+½ · E = {#} MeV · |S| = {#} · δ = {#}° · T = {#}",
  "solid: the wave now · shaded: its size |u| · dashed: free wave": "trait plein : l'onde à cet instant · ombré : son amplitude |u| · tirets : onde libre",
  // S-matrix
  "Re S": "Re S", "Im S": "Im S",
  "|S| = {#}: nothing absorbed": "|S| = {#} : rien n'est absorbé",
  "l = {#}, j = {#}+½ · E = {#} MeV": "l = {#}, j = {#}+½ · E = {#} MeV",
  "|S| = {#} · T = {#} − |S|² = {#}": "|S| = {#} · T = {#} − |S|² = {#}",
  "l = {#}, j = {#}+½": "l = {#}, j = {#}+½",
  "|S| = {#}": "|S| = {#}", "T = {#} − |S|² = {#}": "T = {#} − |S|² = {#}",
  "trail: S as E runs {#} → {#} MeV": "traînée : S quand E va de {#} à {#} MeV",
  "no absorption: S stays on the circle": "sans absorption : S reste sur le cercle",
  // spin-orbit
  "T = {#}": "T = {#}", "l": "l",
  "hollow: j = l − ½ · solid: j = l + ½": "creux : j = l − ½ · plein : j = l + ½",
  "hollow (purple): j = l − ½ · solid (blue): j = l + ½": "creux (violet) : j = l − ½ · plein (bleu) : j = l + ½",
  "reaction cross section {#} b (without spin–orbit {#} b)": "section efficace de réaction {#} b (sans spin-orbite {#} b)",
  "reaction cross section {#} b (spin–orbit off)": "section efficace de réaction {#} b (spin-orbite coupé)",
  "grazing l ≈ kR = {#}": "l rasant ≈ kR = {#}",
  // cross sections
  "total {#} b": "totale {#} b", "reaction {#} b": "réaction {#} b", "shape elastic {#} b": "élastique de forme {#} b",
  "n + ⁵⁶Fe, KD{#}, computed here": "n + ⁵⁶Fe, KD{#}, calculé ici",
  // low energy
  "T₀ (s-wave)": "T₀ (onde s)",
  "T₁ (p-wave, j = {#}/{#}): slope {#}/{#}": "T₁ (onde p, j = {#}/{#}) : pente {#}/{#}",
  "dashed: {#}πS₀√E, slope ½": "tirets : {#}πS₀√E, pente ½",
  "S₀ = {#} × {#}⁻⁴ from this potential": "S₀ = {#} × {#}⁻⁴ d'après ce potentiel",
});
Object.assign(WT.L.glossary, {
  koningDelaroche: {
    term: "Potentiel de Koning–Delaroche", aliases: ["Koning–Delaroche", "KD03"],
    short: "Le potentiel optique global pour les neutrons et les protons d'A. J. Koning et J.-P. Delaroche (2003), de 1 keV à 200 MeV et pour des masses de 24 à 209.",
    more: "Ses profondeurs, rayons et diffusivités sont des fonctions régulières de l'énergie, de la masse et de l'excès de neutrons, ajustées une fois pour toutes sur un vaste ensemble de sections efficaces et de distributions angulaires mesurées. C'est le potentiel par défaut pour les nucléons dans TALYS et dans le moteur.",
    chapter: "optical",
  },
  numerov: {
    term: "Méthode de Numerov", aliases: ["méthode de Numerov", "Numerov"],
    short: "Une règle à trois points pour intégrer les équations du second ordre sans terme de dérivée première, comme l'équation de Schrödinger radiale, avec une erreur d'ordre h⁶ par pas.",
    formula: "(1 − h²Q_n+1/12) u_n+1 = 2(1 + 5h²Q_n/12) u_n − (1 − h²Q_n−1/12) u_n−1",
    chapter: "optical",
  },
  sMatrix: {
    term: "Matrice S", aliases: ["matrice S"],
    short: "Les amplitudes qui relient ondes entrantes et ondes sortantes ; pour la diffusion élastique dans une onde partielle, un seul nombre complexe S = η e^(2iδ).",
    more: "|S| = 1 signifie que rien n'est absorbé et que seule la phase δ change ; le déficit 1 − |S|² est le coefficient de transmission, le flux emporté vers les réactions.",
    chapter: "optical",
  },
  spinOrbit: {
    term: "Terme de spin-orbite", aliases: ["spin-orbite", "spin–orbite"],
    short: "La partie du potentiel nucléaire qui dépend de l'orientation, parallèle ou antiparallèle, du spin du nucléon par rapport à son moment angulaire orbital.",
    more: "Il est attractif pour j = l + ½ et répulsif pour j = l − ½, et culmine à la surface nucléaire. La même interaction produit les nombres magiques du modèle en couches.",
    chapter: "optical",
  },
});
