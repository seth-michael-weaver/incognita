/* French: exciton (Chapitre 26, Expert : le modèle d'excitons en chiffres) */
WT.L.ch.exciton = {
  num: "Chapitre 26", title: "Le modèle d'excitons, en chiffres", short: "Modèle d'excitons",
  lead: "Le chapitre 7 a suivi un neutron rapide au fil de quelques collisions. Voici les taux qui décident, à chaque étape, si la suite sera une nouvelle collision ou une émission, et le spectre qu'ils produisent ensemble.",
  html: `
<div class="step">
  <h3>Compter les états particule–trou</h3>
  <p>Le modèle d'excitons classe le noyau, sur le chemin de l'équilibre, d'après son nombre de particules excitées <i>p</i> et de trous <i>h</i>, avec <i>n</i> = <i>p</i> + <i>h</i>. Un neutron qui entre dans une cible part de <i>p</i> = 1, <i>h</i> = 0 ; chaque collision ajoute une paire. Ce qui compte à chaque étape, c'est le nombre de façons de répartir l'énergie entre les <i>n</i> excitons : la densité d'états particule–trou.</p>
  <div class="formula">ω(p,h,E) = g<sup>n</sup> (E − A<sub>p,h</sub>)<sup>n−1</sup> / (p! h! (n−1)!) ,  A<sub>p,h</sub> = max(p,h)²/g − (p² + h² + p + h)/4g</div>
  <div class="ctl"><label for="ex-n">Particules p (trous p − 1)</label><input id="ex-n" type="range" data-bind="pp" min="2" max="6" step="1" value="3" data-instant><output data-show="pp" data-fmt="0"></output></div>
  <div class="btns"><button class="btn ghost" data-act="pauli" aria-pressed="true">Correction de Pauli</button></div>
  <p><i>g</i> ≈ <i>A</i>/15 MeV⁻¹ est la densité de niveaux à une particule près de l'énergie de Fermi. <i>A<sub>p,h</sub></i> est la correction de <b>Pauli</b> : deux particules ne peuvent pas occuper le même niveau, si bien que les configurations les plus basses coûtent de l'énergie et que la densité chute près du seuil. Le croquis montre une configuration à la fois pour le <i>p</i> choisi, tirée au hasard.</p>
</div>
<div class="step">
  <h3>S'enfoncer ou sortir</h3>
  <p>À chaque étape, deux choses peuvent arriver. Une collision crée une nouvelle paire, au taux λ<sup>+</sup>, qui vaut d'après la règle d'or de Fermi le carré de l'élément de matrice fois la densité des états accessibles. Ou bien une particule s'échappe, au taux <i>W</i>, que le bilan détaillé tire de la section efficace inverse et du rapport des densités d'états avec et sans la particule qui part.</p>
  <div class="formula">λ<sup>+</sup>(n) = (2π/ħ) M² ω<sub>acc</sub> ,  W(p,h,ε) = (2s+1)/(π²ħ³) με σ<sub>inv</sub>(ε) ω(p−1,h,U) / ω(p,h,E)</div>
  <div class="ctl"><label for="ex-e">Énergie du neutron (MeV)</label><input id="ex-e" type="range" data-bind="Ein" min="5" max="60" step="0.5" value="20"><output data-show="Ein" data-fmt="1"></output></div>
  <p>Les barres sont les deux taux à chaque étape, en échelle logarithmique : λ<sup>+</sup> de l'ordre de 10²² s⁻¹, <i>W</i> environ dix fois plus faible à la première étape, et de plus en plus faible ensuite, car chaque nouvelle paire réduit l'énergie que peut emporter la particule de tête. Le moteur prend M² sous la forme de Koning–Duijvestijn, qui décroît avec l'énergie par exciton :</p>
  <div class="formula">M² = (C₁ A<sub>p</sub> / A³) · [7,48 + 4,62×10⁵ / (E/(n A<sub>p</sub>) + 10,7)³]  MeV²</div>
</div>
<div class="step">
  <h3>La chaîne au fil du temps</h3>
  <p>Si l'on néglige les rares collisions qui détruisent une paire (l'approximation de non-retour, dite « never-come-back »), les populations obéissent à une chaîne simple : chaque étape se remplit à partir de la précédente et se vide dans la suivante et dans le continuum. Les barres résolvent cette équation maîtresse ; le temps est en unités de 10⁻²² s.</p>
  <div class="formula">dP(n)/dt = λ<sup>+</sup>(n−2) P(n−2) − [λ<sup>+</sup>(n) + W(n)] P(n)</div>
  <div class="ctl"><label for="ex-e2">Énergie du neutron (MeV)</label><input id="ex-e2" type="range" data-bind="Ein" min="5" max="60" step="0.5" value="20"><output data-show="Ein" data-fmt="1"></output></div>
  <p>Toute la chaîne est terminée en quelques 10⁻²² s. La part qui s'échappe en chemin est l'émission de prééquilibre ; le reste, au plus après six particules dans le moteur comme dans TALYS, est confié au noyau composé. L'intégration en temps donne à chaque étape un poids τ(<i>n</i>)·<i>P</i>(<i>n</i>), et c'est ce produit que calcule le moteur.</p>
</div>
<div class="step">
  <h3>D'où vient la queue de haute énergie</h3>
  <p>Le spectre d'émission est la somme, sur les étapes, de la population fois la durée de vie fois le taux d'émission, à laquelle s'ajoute l'évaporation de ce qui reste. L'étape <i>n</i> = 3 à elle seule, deux particules et un trou, atteint les énergies de sortie les plus élevées : son spectre ne décroît que linéairement jusqu'au point final. Chaque étape suivante est plus molle.</p>
  <div class="formula">dσ/dε = σ<sub>CN</sub> Σ<sub>n</sub> P(n) τ(n) W(n,ε) + évaporation</div>
  <div class="ctl"><label for="ex-e3">Énergie du neutron (MeV)</label><input id="ex-e3" type="range" data-bind="Ein" min="5" max="60" step="0.5" value="20"><output data-show="Ein" data-fmt="1"></output></div>
  <p>Augmentez l'énergie et le spectre se durcit : la queue de prééquilibre s'étire jusqu'au point final tandis que la bosse d'évaporation reste vers 1 à 2 MeV. Au-dessus de 10 MeV environ, les neutrons de haute énergie mesurés ne peuvent être reproduits qu'avec cette queue.</p>
</div>
<div class="step">
  <h3>Quelle part au total</h3>
  <p>La part de prééquilibre dans l'émission croît avec l'énergie incidente, de quelques pour cent vers 5 MeV à environ 40 % à 40 MeV ici. Elle dépend d'une seule constante ajustable, la taille globale de l'élément de matrice : une interaction plus faible signifie une équilibration plus lente et davantage d'émission précoce.</p>
  <div class="ctl"><label for="ex-c">Constante de l'élément de matrice C₁</label><input id="ex-c" type="range" data-bind="c1" min="0.3" max="3" step="0.05" value="1"><output data-show="c1" data-fmt="2"></output></div>
  <p>La courbe en tirets correspond à C₁ = 1, la valeur par défaut du moteur ; la courbe pleine suit le curseur. Diviser C₁ par deux multiplie la part par 1,5 à 1,9, et non par 2 : la probabilité d'émission de chaque étape est W/(λ<sup>+</sup> + W), et non W/λ<sup>+</sup>, et moins de noyaux survivent jusqu'aux étapes suivantes.</p>
</div>
<div class="step">
  <h3>Deux composantes, et une seconde émission</h3>
  <p>Le moteur suit séparément protons et neutrons (<i>p</i><sub>π</sub>, <i>h</i><sub>π</sub>, <i>p</i><sub>ν</sub>, <i>h</i><sub>ν</sub>), avec des éléments de matrice différents pour les paires semblables et dissemblables, une profondeur de puits réduite pour la première collision près de la surface, et les règles de Kalbach pour les agrégats. Au-dessus de 20 MeV, il permet aussi au noyau résiduel, qui contient encore des excitons, d'émettre une seconde particule rapide avant de s'équilibrer.</p>
  <div class="ctl"><label for="ex-e4">Énergie du neutron (MeV)</label><input id="ex-e4" type="range" data-bind="Ein" min="5" max="60" step="0.5" value="20"><output data-show="Ein" data-fmt="1"></output></div>
  <p>La courbe en est une version simplifiée : après une première émission depuis l'étape à trois excitons, la probabilité que la particule restante du noyau résiduel s'échappe avant sa collision suivante. Elle reste faible sous 20 MeV et croît au-dessus, là où le moteur active le prééquilibre multiple.</p>
  <div class="aside">Dans le code : <code>density/particle_hole.py</code> (densités de Williams, corrections de Pauli et de puits fini, à une et deux composantes), <code>preeq/exciton.py</code> (éléments de matrice, taux d'émission et de transition, durées de vie, solution « never-come-back »), <code>preeq/complex.py</code> (pick-up, stripping et knock-out de Kalbach), <code>preeq/multi.py</code> (prééquilibre multiple, à partir de 20 MeV par défaut). L'image est à une composante, avec une section efficace inverse schématique, pour une cible semblable au fer 56.</div>
</div>`,
};
Object.assign(WT.L.labels, {
  // state densities
  "E (MeV)": "E (MeV)",
  "ω(p, h, E) per MeV": "ω(p, h, E) par MeV",
  "{#}p{#}h": "{#}p{#}h",
  "dashed: no Pauli correction": "tirets : sans correction de Pauli",
  "Fermi level": "niveau de Fermi",
  "{#} particles, {#} holes": "{#} particules, {#} trous",
  // rates
  "rate (s⁻¹)": "taux (s⁻¹)",
  "n = {#}": "n = {#}",
  "W/λ⁺ = {#}": "W/λ⁺ = {#}",
  "blue: λ⁺, the next collision · yellow: W, neutron escape": "bleu : λ⁺, la collision suivante · jaune : W, l'émission d'un neutron",
  "E = {#} + Sₙ = {#} MeV · τ(n={#}) = {#} × {#}⁻²² s": "E = {#} + Sₙ = {#} MeV · τ(n={#}) = {#} × {#}⁻²² s",
  // master equation
  "compound": "composé",
  "emitted before equilibrium: {#} % (of {#} % in the end)": "émis avant l'équilibre : {#} % (sur {#} % au final)",
  "t = {#} × {#}⁻²² s": "t = {#} × {#}⁻²² s",
  // spectrum
  "outgoing neutron energy ε (MeV)": "énergie du neutron sortant ε (MeV)",
  "dσ/dε (mb/MeV)": "dσ/dε (mb/MeV)",
  "evaporation": "évaporation",
  "ε = {#} MeV: {#} % from n = {#}": "ε = {#} MeV : {#} % venant de n = {#}",
  "pre-equilibrium {#} % of the emission · solid: total": "prééquilibre : {#} % de l'émission · trait plein : total",
  // share
  "{#} MeV": "{#} MeV",
  "pre-equilibrium share of the emission": "part de prééquilibre dans l'émission",
  "{#} MeV: {#} %": "{#} MeV : {#} %",
  "C₁ = {#} (dashed: {#})": "C₁ = {#} (tirets : {#})",
  // second escape
  "{#} MeV: multiple pre-equilibrium on": "{#} MeV : prééquilibre multiple activé",
  "chance of a second fast emission (toy estimate)": "probabilité d'une seconde émission rapide (estimation simplifiée)",
  "residual: {#}p{#}h": "résiduel : {#}p{#}h",
});
Object.assign(WT.L.glossary, {
  neverComeBack: {
    term: "Approximation de non-retour (never-come-back)", aliases: ["approximation de non-retour", "never-come-back"],
    short: "L'approximation selon laquelle, au début de l'équilibration, les collisions ne font qu'ajouter des paires particule–trou sans jamais en retirer.",
    more: "Elle transforme l'équation maîtresse en une chaîne simple que l'on intègre étape par étape. Elle est valable tant que le nombre d'excitons reste très inférieur à sa valeur d'équilibre, c'est-à-dire là où se produit l'émission de prééquilibre.",
    chapter: "exciton",
  },
});
