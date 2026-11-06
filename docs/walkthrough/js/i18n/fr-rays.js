/* French: rays (Alpha, bêta, gamma et neutrons) */
WT.L.ch.rays = {
  num: "Leçon 2", title: "Alpha, bêta, gamma et neutrons", short: "Rayonnements",
  html: `
<div class="step">
  <h3>Quatre sortes de rayonnement</h3>
  <p>L'<em class="a">alpha</em> est un amas lourd de deux protons et deux neutrons. Le <b>bêta</b> est un électron rapide. Le <em class="g">gamma</em> est de la lumière, bien trop énergétique pour être vue. Les <em class="n">neutrons</em> ne portent aucune charge. Chacun est arrêté par des choses différentes.</p>
</div>
<div class="step">
  <h3>Papier et aluminium</h3>
  <p>Les particules alpha sont grosses et chargées : elles heurtent les atomes aussitôt, et une feuille de papier les arrête. Les électrons bêta vont plus loin, mais quelques millimètres d'aluminium les arrêtent aussi.</p>
  <div class="btns"><button class="btn ghost" data-act="sh_paper" aria-pressed="true">Papier</button><button class="btn ghost" data-act="sh_al" aria-pressed="false">Aluminium</button></div>
</div>
<div class="step">
  <h3>Les rayons gamma : divisés par deux, jamais nuls</h3>
  <p>Les rayons gamma n'ont pas de charge et passent le plus souvent à côté des atomes. Chaque centimètre de plomb donne à chacun la même chance d'être capté, si bien que chaque tranche divise par deux ce qui reste. Le faisceau s'affaiblit sans jamais tout à fait atteindre zéro.</p>
  <div class="ctl"><label for="ry-pb">Plomb (cm)</label><input id="ry-pb" type="range" data-bind="pb" data-instant min="0" max="5" step="0.1" value="1"><output data-show="pb" data-fmt="1"></output></div>
</div>
<div class="step">
  <h3>Les neutrons : le plomb ne suffit pas</h3>
  <p>Un neutron qui rebondit sur un lourd noyau de plomb, c'est une balle de ping-pong qui heurte une boule de bowling : il garde sa vitesse. L'hydrogène de l'eau pèse autant qu'un neutron, donc chaque choc le ralentit, jusqu'à ce qu'il soit assez lent pour être absorbé.</p>
  <div class="btns"><button class="btn ghost" data-act="nm_pb" aria-pressed="true">Plomb</button><button class="btn ghost" data-act="nm_water" aria-pressed="false">Eau</button></div>
  <div class="ctl"><label for="ry-nx">Épaisseur (cm)</label><input id="ry-nx" type="range" data-bind="nx" data-instant min="0" max="60" step="1" value="30"><output data-show="nx" data-fmt="0"></output></div>
</div>
<div class="step">
  <h3>Construisez un écran</h3>
  <p>Empilez des couches jusqu'à ce que les quatre faisceaux soient arrêtés. Les rayons gamma ne tombent jamais exactement à zéro, seulement à une part infime.</p>
  <div class="btns"><button class="btn ghost" data-act="add_paper">+ Papier</button><button class="btn ghost" data-act="add_al">+ Aluminium</button><button class="btn ghost" data-act="add_pb">+ Plomb</button><button class="btn ghost" data-act="add_water">+ Eau</button><button class="btn" data-act="clear">Effacer</button></div>
</div>`,
};

Object.assign(WT.L.labels, {
  "alpha": "alpha",
  "beta": "bêta",
  "gamma": "gamma",
  "neutron": "neutron",
  "paper": "papier",
  "aluminium {#} mm": "aluminium {#} mm",
  "Al {#} mm": "Al {#} mm",
  "lead {#} cm": "plomb {#} cm",
  "water {#} cm": "eau {#} cm",
  "no shield": "sans écran",
  "stopped": "arrêté",
  "all through": "tout passe",
  "{#} % through": "{#} % passent",
  "{#} in {#}": "{#} sur {#}",
  "{#} in {#} million": "{#} sur {#} millions",
  "{#} in a billion": "{#} sur un milliard",
  "drag ↔": "glisser ↔",
  "all four stopped": "les quatre arrêtés",
  "all four beams stopped": "les quatre faisceaux sont arrêtés",
  "flash = stopped inside the shield": "éclair = arrêté dans l'écran",
  "each source fires a steady beam": "chaque source émet un faisceau continu",
  "flash = stopped": "éclair = arrêté",
  "four beams": "quatre faisceaux",
  "not to scale": "pas à l'échelle",
  "gamma rays (caesium{#})": "rayons gamma (césium{#})",
  "cm of lead": "cm de plomb",
  "share still going": "part qui passe encore",
  "through: all · halved every {#} mm": "passe : tout · moitié tous les {#} mm",
  "through: {#} % · halved every {#} mm": "passe : {#} % · moitié tous les {#} mm",
  "through: {#} in {#} · halved every {#} mm": "passe : {#} sur {#} · moitié tous les {#} mm",
  "gets through: {#} % · halved every {#} mm of lead": "passe : {#} % · divisé par deux tous les {#} mm de plomb",
  "gets through: {#} in {#} · halved every {#} mm of lead": "passe : {#} sur {#} · divisé par deux tous les {#} mm de plomb",
  "counted: {#} of {#}": "comptés : {#} sur {#}",
  "through {#} % · back {#} % · caught {#} %": "passent {#} % · renvoyés {#} % · capturés {#} %",
  "got through {#} % · bounced back {#} % · slowed and caught {#} %": "traversent {#} % · rebondissent en arrière {#} % · ralentis et capturés {#} %",
  "bright = fast · dim = slowed": "vif = rapide · pâle = ralenti",
  "bright = fast neutron · red = hydrogen nucleus knocked away · green flash = swallowed": "vif = neutron rapide · rouge = noyau d'hydrogène éjecté · éclair vert = absorbé",
  "simplified model": "modèle simplifié",
});
