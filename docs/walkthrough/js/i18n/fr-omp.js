/* French: omp (Chapitre 2, le modèle optique) */
WT.L.ch.omp = {
  num: "Chapitre 2", title: "Une boule de cristal trouble", short: "Modèle optique",
  lead: "Avant toute chose, le moteur se pose une question plus simple : à quoi ressemble le noyau pour un neutron qui arrive ?",
  html: `
<div class="step">
  <p>En mécanique quantique, un neutron est aussi une onde. L'image en montre une qui arrive de la gauche, ses crêtes formant des bandes claires, vers un noyau (le cercle en pointillés). Rien n'agit encore sur elle, donc les crêtes le traversent sans changer.</p>
  <div class="ctl"><label for="omp-e">Énergie du neutron (MeV)</label><input id="omp-e" type="range" data-bind="E" min="0.2" max="40" step="0.1" value="8"><output data-show="E" data-fmt="1"></output></div>
  <p>Faites varier l'énergie et regardez la longueur d'onde en bas, en femtomètres (fm, 10⁻¹⁵ m). Les neutrons lents ont de grandes longueurs d'onde : en dessous d'environ 9 MeV, une longueur d'onde est plus large que tout ce noyau.</p>
</div>
<div class="step">
  <h3>La partie réelle attire</h3>
  <p>Le <b>potentiel optique</b> est la force moyenne exercée par tout le noyau sur le neutron. Sa <em>partie réelle</em> est un puits d'environ 50 MeV de profondeur : à l'intérieur, le neutron accélère, donc les crêtes se resserrent. Le moteur lui donne une forme de Woods–Saxon, plate et profonde au centre, qui s'annule doucement à la surface.</p>
</div>
<div class="step">
  <h3>La partie imaginaire absorbe</h3>
  <p>L'ombre derrière le noyau, ce sont les neutrons perdus dans des réactions. La <em>partie imaginaire</em> du potentiel en rend compte : elle atténue l'onde au lieu de la dévier, surtout près de la surface (l'anneau coloré).</p>
  <div class="ctl"><label for="omp-w">Absorption W (MeV)</label><input id="omp-w" type="range" data-bind="W" min="0" max="14" step="0.5" value="7"><output data-show="W" data-fmt="1"></output></div>
  <p>Ramenez <i>W</i> à 0 et l'ombre se remplit : sans absorption, pas de réactions. D'où le nom de modèle optique : le noyau est une boule de verre trouble qui dévie en partie et absorbe en partie.</p>
</div>
<div class="step">
  <h3>La visée compte</h3>
  <p>Vue de face, la cible se divise en anneaux, un par <b>onde partielle</b> <i>l</i> = 0, 1, 2, … Un neutron qui passe à une distance <i>b</i> du centre porte un <b>moment angulaire</b> <i>l</i> ≈ <i>k b</i>, où <i>k</i> croît avec l'énergie. Plus un anneau est sombre, plus son <b>coefficient de transmission</b> <i>T<sub>l</sub></i> est grand : c'est la probabilité qu'un neutron de cet anneau soit absorbé.</p>
  <div class="ctl"><label for="omp-e3">Énergie du neutron (MeV)</label><input id="omp-e3" type="range" data-bind="E" min="0.2" max="40" step="0.1" value="8"><output data-show="E" data-fmt="1"></output></div>
  <div class="btns"><button class="btn" data-act="fire">Tirer 200 neutrons</button></div>
  <p>Les éclairs orange sont des neutrons absorbés ; les barres comparent la part absorbée dans chaque anneau au <i>T<sub>l</sub></i> du modèle (le repère). Les anneaux intérieurs absorbent presque tout, les anneaux extérieurs laissent passer les neutrons. À basse énergie, les anneaux sont énormes et seul <i>l</i> = 0 compte.</p>
</div>
<div class="step">
  <h3>Frôler le noyau</h3>
  <p>Un neutron qui porte beaucoup de moment angulaire passe trop loin pour toucher le noyau : c'est la <b>barrière centrifuge</b>. Vu de dessus, chaque neutron appartient ici à une même onde partielle <i>l</i>, donc il passe à la même <b>distance de passage</b> <i>b</i> ≈ (<i>l</i>+½)/<i>k</i> (le cercle en pointillés).</p>
  <p>Mais chaque neutron est une onde, floue sur environ une longueur d'onde réduite λ̄ (le halo). Même quand sa trajectoire passe à côté, le bord flou peut effleurer la surface et entrer : c'est l'<b>effet tunnel</b>.</p>
  <div class="ctl"><label for="omp-l">Onde partielle l</label><input id="omp-l" type="range" data-bind="L" min="0" max="8" step="1" value="3" data-instant><output data-show="L" data-fmt="0"></output></div>
  <div class="ctl"><label for="omp-e2">Énergie (MeV)</label><input id="omp-e2" type="range" data-bind="E" min="0.2" max="40" step="0.1" value="8"><output data-show="E" data-fmt="1"></output></div>
  <p>Augmentez <i>l</i> et la trajectoire s'éloigne : moins de neutrons entrent. Augmentez l'énergie et le même <i>l</i> passe plus près, avec moins de flou. Le moteur calcule chaque <i>T<sub>l</sub></i> exactement en résolvant l'équation de Schrödinger dans le potentiel complet ; <i>S</i> mesure la part de l'onde qui ressort.</p>
  <div class="formula">T<sub>lj</sub> = 1 − |S<sub>lj</sub>|²</div>
</div>
<div class="step">
  <h3>Additionner la cible</h3>
  <p>Le disque de droite montre la taille apparente du noyau pour le neutron : la <b>section efficace de réaction</b>, en barns (10⁻²⁴ cm²). Chaque anneau y ajoute son aire multipliée par <i>T<sub>l</sub></i>. Le cercle en pointillés est la taille géométrique.</p>
  <div class="ctl"><label for="omp-e4">Énergie du neutron (MeV)</label><input id="omp-e4" type="range" data-bind="E" min="0.2" max="40" step="0.1" value="8"><output data-show="E" data-fmt="1"></output></div>
  <div class="btns"><button class="btn ghost" data-act="sum">Additionner à nouveau</button></div>
  <p>Changez l'énergie et la somme recommence : à basse énergie, un ou deux grands anneaux forment presque tout le disque ; à haute énergie, de nombreux anneaux fins ajoutent de minces tranches et le disque approche la taille géométrique.</p>
  <div class="formula">σ<sub>R</sub> = (π/k²) Σ (2l+1) T<sub>l</sub></div>
  <p>Les <i>T<sub>l</sub></i> alimentent tout le reste du moteur : ils décident à quelle fréquence se forme chaque spin du noyau excité et, à l'inverse, avec quelle facilité chaque particule ressort.</p>
  <div class="aside">Dans le code : <code>omp/parameters.py</code> (potentiel global de Koning–Delaroche ; potentiels dispersifs pour les actinides), <code>omp/schrodinger.py</code> (intégration de Numerov et raccordement coulombien), <code>omp/inverse.py</code> (particules sortantes par bilan détaillé), <code>omp/regional.py</code> (facultatif, désactivé par défaut : un ajustement régional du puits pour les cibles déformées de terres rares, ajusté sur les S₀ et S₁ mesurés).</div>
</div>`,
};
Object.assign(WT.L.labels, {
  "absorbing surface": "surface absorbante",
  "shadow: neutrons lost to reactions": "ombre : neutrons perdus en réactions",
  "wavelength {#} fm   ·   nucleus {#} fm across": "longueur d'onde {#} fm   ·   noyau de {#} fm",
  "crests crowd inside the well": "les crêtes se resserrent dans le puits",
  "l={#}": "l={#}",
  "nuclear radius": "rayon nucléaire",
  "reaction cross section ≈ {#} b": "section efficace de réaction ≈ {#} b",
  "geometric size π(R+λ̄)² ≈ {#} b · darker ring = more absorbed · orange flash = absorbed": "taille géom. π(R+λ̄)² ≈ {#} b · plus sombre = plus absorbé · orange = absorbé",
  "absorbed, ring by ring": "absorbés, anneau par anneau",
  "bar: your neutrons · tick: model Tₗ": "barre : vos neutrons · repère : Tₗ",
  "rings: shade = Tₗ": "anneaux : teinte = Tₗ",
  "geometric size π(R+λ̄)²": "taille géométrique π(R+λ̄)²",
  "reaction cross section": "section efficace de réaction",
  "ring l={#}: ({#}l+{#})·Tₗ·π/k² = +{#} b": "anneau l={#} : ({#}l+{#})·Tₗ·π/k² = +{#} b",
  "all {#} rings added": "les {#} anneaux additionnés",
  "σ_R = {#} b": "σ_R = {#} b",
  "geometric {#} b": "géométrique {#} b",
  "geometric {#} b · darker = more absorbed · orange = absorbed": "géométrique {#} b · plus sombre = plus absorbé · orange = absorbé",
  "swing distance b ≈ (l+½)/k = {#} fm": "distance de passage b ≈ (l+½)/k = {#} fm",
  "nuclear radius R = {#} fm · wave fuzz λ̄ = {#} fm": "rayon nucléaire R = {#} fm · flou λ̄ = {#} fm",
  "path crosses the nucleus: most get in": "trajectoire dans le noyau : presque tous entrent",
  "path misses the nucleus: only the fuzzy edge can tunnel in": "trajectoire hors du noyau : seul le bord flou passe par effet tunnel",
  "absorbed {#} of {#} · model Tₗ = {#}": "absorbés {#} sur {#} · Tₗ du modèle = {#}",
});
