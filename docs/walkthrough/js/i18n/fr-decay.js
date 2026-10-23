/* French: decay (Chapitre 6) */
WT.L.ch.decay = {
  num: "Chapitre 6", title: "Choisir une sortie", short: "Désexcitation",
  lead: "Le noyau composé doit se débarrasser de son énergie en émettant une particule ou un photon. Ce chapitre représente chaque issue par une porte. Le rôle du moteur est de dire quelle part du flux (le courant de réactions qui arrivent ici) sort par chaque porte.",
  html: `
<div class="step">
  <p>Une porte par sortie : un <em class="g">photon</em> (γ), un <em class="n">neutron</em> (n), un <em class="p">proton</em> (p), une <em class="a">particule alpha</em> (α : deux protons et deux neutrons) et, pour les noyaux lourds seulement, la <em class="f">fission</em> (la cassure en deux). L'ouverture éclairée de chaque porte est la part de cette sortie, et les boules s'en échappent au même rythme ; les portes grises sont fermées. Ayant oublié comment il s'est formé, le noyau emprunte chaque porte b en proportion d'un poids :</p>
  <div class="formula">part<sub>b</sub> = T<sub>b</sub> · ρ<sub>b</sub> / Σ<sub>c</sub> T<sub>c</sub> · ρ<sub>c</sub></div>
  <p>Le <b>coefficient de transmission</b> <i>T</i> est la probabilité qu'une particule arrivée au bord passe ; pour les particules, il provient du modèle optique du chapitre 2, utilisé à l'envers. La <b>densité de niveaux</b> ρ, écrite à côté de chaque porte, compte les états dans lesquels le noyau restant peut se retrouver. Répartir selon <i>T</i> fois ρ, c'est la règle de <b>Hauser–Feshbach</b>. À 10 MeV, la porte du neutron prend presque tout.</p>
</div>
<div class="step">
  <h3>Pourquoi la plupart des particules sortent lentes</h3>
  <p>La porte du neutron, découpée selon l'énergie de sortie ε (lents à gauche, rapides à droite). L'ouverture <i>T</i>(ε) de chaque porte s'élargit pour les neutrons plus rapides. En dessous se trouve la foule d'états où le noyau restant peut se trouver : un neutron lent laisse derrière lui l'essentiel de l'énergie, là où les états abondent, donc les foules diminuent vers la droite.</p>
  <div class="ctl"><label for="dc-sp">Énergie disponible</label><input id="dc-sp" type="range" data-bind="spare" min="1" max="12" step="0.5" value="5"><output data-show="spare" data-fmt="1"></output></div>
  <p>Porte × foule donne à la pile la forme d'une bosse, le <b>spectre d'évaporation</b>, comme la vapeur qui s'échappe d'un liquide chaud. Faites varier l'énergie disponible (en MeV, millions d'électronvolts) : la pile recommence, et son maximum reste vers 1 MeV, fixé par la température nucléaire. L'énergie en plus sert surtout à chauffer davantage le noyau restant.</p>
</div>
<div class="step">
  <h3>Les particules chargées doivent grimper</h3>
  <p>L'énergie d'un proton à chaque distance r du centre : un puits à l'intérieur et, à l'extérieur, une colline due à la répulsion électrique (coulombienne), qui décroît comme 1/r. Sous le sommet de la colline, le proton, qui s'agite dans le puits, ne peut que traverser par <b>effet tunnel</b> la zone ombrée, un effet quantique qui réussit une fois sur de nombreux chocs contre la paroi.</p>
  <div class="ctl"><label for="dc-ce">Énergie de la particule</label><input id="dc-ce" type="range" data-bind="eps" min="0.5" max="12" step="0.1" value="3"><output data-show="eps" data-fmt="1"></output></div>
  <div class="btns"><button class="btn ghost" data-act="toggleAlpha">Basculer proton / alpha</button></div>
  <p>Diminuez l'énergie et regardez le tunnel s'élargir ; passez ensuite à l'alpha, dont les deux charges font face à une colline environ deux fois plus haute. C'est pourquoi les neutrons, sans charge, l'emportent en général dès qu'ils peuvent sortir, et pourquoi les sorties proton et alpha comptent surtout pour les noyaux légers et à haute énergie.</p>
</div>
<div class="step">
  <h3>Les portes s'ouvrent une à une</h3>
  <p>Chaque porte de particule ne s'ouvre qu'au-dessus de son <b>énergie de séparation</b>, le coût d'extraction de cette particule : ici 8 MeV pour un neutron, 9 pour un proton, 7 pour une alpha. En dessous des 8 MeV du neutron, presque toutes les désexcitations émettent de la lumière.</p>
  <div class="ctl"><label for="dc-e">Énergie d'excitation</label><input id="dc-e" type="range" data-bind="E" min="5" max="24" step="0.1" value="7"><output data-show="E" data-fmt="1"></output></div>
  <p>Faites passer l'énergie d'excitation au-delà de 8 MeV. En environ 1 MeV, la porte du neutron s'ouvre en grand et la part des photons chute d'un facteur cent. Les portes du proton et de l'alpha s'allument plus tard et restent étroites, freinées par leurs collines coulombiennes.</p>
</div>
<div class="step">
  <h3>Spin et parité doivent s'équilibrer</h3>
  <p>Le noyau composé (en haut) a un spin <i>J</i> ; les états du noyau restant sont rangés en dessous dans des tiroirs selon leur spin <i>J</i>′. Le neutron emporte la différence de spin et de parité : en partant avec un moment angulaire orbital <i>l</i>, il change le spin d'au plus <i>l</i> + ½ et inverse la parité quand <i>l</i> est impair. Un <i>l</i> plus grand signifie une porte plus étroite ; la porte de chaque tiroir correspond au plus petit <i>l</i> qui l'atteint. Les arrivées pleines conservent la parité ; les creuses l'inversent.</p>
  <div class="ctl"><label for="dc-j">Spin du noyau composé J</label><input id="dc-j" type="range" data-bind="J" min="0" max="10" step="1" value="2" data-instant><output id="dc-jout">5/2</output></div>
  <p>Augmentez <i>J</i>. Les portes ouvertes glissent vers les tiroirs de haut spin, qui contiennent peu d'états, tandis que les tiroirs pleins sont derrière des portes fermées. Un noyau composé de haut spin émet lentement des particules, ce qui laisse leur chance aux photons et aux isomères (états de longue durée de vie, chapitre 7).</p>
</div>
<div class="step">
  <h3>Par où vous êtes entré</h3>
  <p>À basse énergie, le noyau composé est un ensemble de <b>résonances</b> étroites, des énergies où le neutron est facilement absorbé ; huit sont dessinées, une par ligne. Chacune a des largeurs de porte aléatoires : l'entrée (la voie neutron) à gauche, de largeur <i>x</i>, et les autres portes, surtout des photons ici, à droite, de largeurs <i>y</i>.</p>
  <div class="btns"><button class="btn" data-act="fire">Tirer 40 neutrons</button><button class="btn ghost" data-act="reroll">Nouvelles résonances</button></div>
  <p>Un neutron entre dans la résonance <i>i</i> avec une probabilité proportionnelle à <i>x<sub>i</sub></i> et ressort par l'entrée avec une probabilité <i>x<sub>i</sub></i> / (<i>x<sub>i</sub></i> + Σ<i>y</i>). Les lignes à large entrée font entrer plus de neutrons et en renvoient davantage, donc la vraie part qui ressort (une <b>moyenne de produits</b>) dépasse l'estimation tirée des largeurs moyennes (un <b>produit de moyennes</b>). Le rapport est l'<b>amplification élastique</b>, et la <b>correction de fluctuation des largeurs</b> transfère ce flux des autres portes vers l'entrée.</p>
  <div class="ctl"><label for="dc-n">Autres portes</label><input id="dc-n" type="range" data-bind="Nch" min="1" max="12" step="1" value="2" data-instant><output data-show="Nch" data-fmt="0"></output></div>
  <p>Ajoutez des portes. Avec de nombreuses sorties, leur largeur totale cesse de fluctuer, donc la correction compte surtout quand peu de portes sont ouvertes. Le moteur l'applique, avec la formule de Moldauer, pour des neutrons incidents jusqu'à l'énergie de séparation neutronique de la cible, et l'omet au-delà.</p>
</div>
<div class="step">
  <h3>Ce qui reste à partager</h3>
  <p>Tous les neutrons absorbés ne forment pas un noyau composé. Certains font un seul coup rasant et repartent (réactions directes, chapitre 3) ; d'autres s'entrechoquent une ou deux fois et ressortent vite (prééquilibre, chapitre 4). Seul le reste demeure et chauffe le noyau. Les compteurs totalisent chaque sort.</p>
  <div class="ctl"><label for="dc-einc">Énergie du neutron</label><input id="dc-einc" type="range" data-bind="Einc" min="1" max="30" step="0.5" value="8"><output data-show="Einc" data-fmt="1"></output></div>
  <p>Seuls ceux qui restent entrent dans la compétition des portes. Faites varier l'énergie du neutron : à quelques MeV, presque tous restent ; à 30 MeV, environ la moitié est partie avant d'atteindre l'équilibre.</p>
  <div class="aside">Dans le code : <code>compound/prepare.py</code> (poids de sortie T·ρ par spin et parité, règles de sélection), <code>compound/target.py</code> (première désexcitation avec fluctuations des largeurs), <code>compound/continuum.py</code> (désexcitation de chaque intervalle suivant), <code>compound/wfc.py</code> (corrections Moldauer, HRTW, GOE), <code>compound/normalization.py</code> (flux restant pour le noyau composé), <code>omp/inverse.py</code> (les portes utilisées à l'envers).</div>
</div>`,
};
(function () {
  const L = {
    "{#} MeV": "{#} MeV",
    "n": "n", "p": "p", "fission": "fission",
    "heavy only": "lourds seuls",
    "heavy nuclei only": "noyaux lourds seulement",
    "shut below {#} MeV": "fermée sous {#} MeV",
    "the neutron door takes nearly everything": "la porte du neutron prend presque tout",
    "below the neutron threshold, nearly all decays emit light": "sous le seuil neutron, presque tout émet de la lumière",
    "the doors share the decays": "les portes se partagent les désexcitations",
    // hump
    "{#} MeV to spare": "{#} MeV disponibles",
    "door gap = T(ε)": "ouverture = T(ε)",
    "doors: one per neutron energy ε, gap = T(ε)": "portes : une par énergie ε du neutron, ouverture = T(ε)",
    "× states left behind": "× états restants",
    "× states the leftover nucleus can be in: many after a slow neutron": "× états possibles du noyau restant : nombreux après un neutron lent",
    "most ≈ {#} MeV": "maximum ≈ {#} MeV",
    "= the pile": "= la pile",
    "= where the neutrons land: the evaporation spectrum": "= où arrivent les neutrons : le spectre d'évaporation",
    "slow": "lents",
    "slow neutrons": "neutrons lents",
    "fast: {#} MeV →": "rapides : {#} MeV →",
    "fast: {#} MeV (beyond, up to {#}, almost none)": "rapides : {#} MeV (au-delà, jusqu'à {#}, presque aucun)",
    "fast: {#}": "rapides : {#}",
    "fast: {#} MeV, the neutron takes it all": "rapides : {#} MeV, le neutron prend tout",
    // coulomb
    "well ↓": "puits ↓",
    "well (much deeper) ↓": "puits (bien plus profond) ↓",
    "hilltop ≈ {#} MeV": "sommet ≈ {#} MeV",
    "falls as {#}/r": "décroît en {#}/r",
    "Coulomb hill, falling as {#}/r": "colline coulombienne, décroît en {#}/r",
    "tunnel: wider than the picture": "tunnel : plus large que l'image",
    "tunnel {#} fm": "tunnel {#} fm",
    "proton energy {#} MeV": "énergie du proton {#} MeV",
    "alpha energy {#} MeV": "énergie de l'alpha {#} MeV",
    "proton energy {#} MeV ↑": "énergie du proton {#} MeV ↑",
    "alpha energy {#} MeV ↑": "énergie de l'alpha {#} MeV ↑",
    "above the hilltop: it rolls straight out": "au-dessus du sommet : elle sort directement",
    "below the top, must tunnel: nearly every knock gets through": "sous le sommet, effet tunnel : passe presque à chaque choc",
    "below the top, must tunnel: about {#} knock in {#} gets through": "sous le sommet, effet tunnel : environ {#} choc sur {#} passe",
    "below the top, must tunnel: about {#} knock in {#} × {#}^{#} gets through": "sous le sommet, effet tunnel : environ {#} choc sur {#} × {#}^{#} passe",
    "out": "sortie",
    "through after {#} knock": "passée après {#} choc",
    "through after {#} knocks": "passée après {#} chocs",
    "knocks so far: {#}": "chocs jusqu'ici : {#}",
    "distance r from the centre (fm) →": "distance r au centre (fm) →",
    // spin
    "J = {#}/{#}, parity +": "J = {#}/{#}, parité +",
    "l={#}": "l={#}",
    "leftover states by spin J′ →": "états restants par spin J′ →",
    "drawers: states of the leftover nucleus by spin J′ (faint: states it holds) →": "tiroirs : états du noyau restant par spin J′ (pâle : états qu'il contient) →",
    "open doors reach {#} %": "les portes ouvertes atteignent {#} %",
    "open doors reach about {#} % of the states": "les portes ouvertes atteignent environ {#} % des états",
    "● parity kept (even l)   ○ flipped (odd l)": "● parité conservée (l pair)   ○ inversée (l impair)",
    // wfc
    "entrance x": "entrée x",
    "entrance, width x": "entrée, largeur x",
    "{#} other doors, y": "{#} autres portes, y",
    "{#} other door, widths y": "{#} autre porte, largeurs y",
    "{#} other doors, widths y": "{#} autres portes, largeurs y",
    "back out the entrance: {#} of {#}": "ressortis par l'entrée : {#} sur {#}",
    "out another door: {#}": "par une autre porte : {#}",
    // norm
    "absorbed neutrons, {#} MeV →": "neutrons absorbés, {#} MeV →",
    "direct: {#} %": "direct : {#} %",
    "pre-equilibrium: {#} %": "prééquilibre : {#} %",
    "compound nucleus: {#} %": "noyau composé : {#} %",
    "one glancing hit on the surface": "un coup rasant sur la surface",
    "a knock or two, then out fast": "un choc ou deux, puis sortie rapide",
    "stayed: on to the door competition": "resté : place à la compétition des portes",
  };
  // door hint with level-count wording (fmt: "1", "N", "N thousand", "N million") and T possibly in e-notation
  const cnt = [["{#} state", "{#} état"], ["{#} states", "{#} états"], ["{#} thousand states", "{#} mille états"], ["{#} million states", "{#} millions d'états"]];
  for (const [e, s] of cnt) {
    L[`weak door × ≈ ${e}`] = `porte étroite × ≈ ${s}`;
    L[`T ≈ {#} × ≈ ${e}`] = `T ≈ {#} × ≈ ${s}`;
    L[`T ≈ {#}e{#} × ≈ ${e}`] = `T ≈ {#}e{#} × ≈ ${s}`;
  }
  // share comparisons: each pct is "{#} %" or "≈ {#} %" (keys keep the English spacing; values use the French narrow space)
  const P = ["{#} %", "≈ {#} %"];
  const fr = (x) => x.replace(" %", " %");
  for (const a of P) for (const b of P) {
    L[`back out ${a}, not ${b}: × {#}`] = `ressortis ${fr(a)}, et non ${fr(b)} : × {#}`;
    L[`share back out: average of products ${a} · product of averages ${b} · × {#}`] = `part ressortie : moyenne des produits ${fr(a)} · produit des moyennes ${fr(b)} · × {#}`;
    L[`other doors ${a}, not ${b}`] = `autres portes ${fr(a)}, et non ${fr(b)}`;
    L[`other doors together: ${a} instead of ${b}`] = `autres portes ensemble : ${fr(a)} au lieu de ${fr(b)}`;
  }
  Object.assign(WT.L.labels, L);
})();
