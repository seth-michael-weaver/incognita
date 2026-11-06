/* French: chains (Chaînes de désintégration et équilibre) */
WT.L.ch.chains = {
  num: "Leçon 4", title: "Chaînes de désintégration et équilibre", short: "Chaînes de désintégration",
  html: `
<div class="step">
  <h3>Père, fils, petit-fils</h3>
  <p>Souvent, le nouveau noyau est lui aussi instable. Le père se désintègre en un fils, qui se désintègre à son tour en un petit-fils stable. Les fils s'accumulent puis s'effacent ; la hauteur de leur pic dépend de la vitesse de leur désintégration comparée à celle du père.</p>
  <div class="ctl"><label for="ch-t2">Demi-vie du fils (s)</label><input id="ch-t2" type="range" data-bind="T2" data-instant min="0.5" max="9" step="0.5" value="1.5"><output data-show="T2" data-fmt="1"></output></div>
  <div class="btns"><button class="btn ghost" data-act="refill">Nouvel échantillon</button></div>
</div>
<div class="step">
  <h3>Équilibre séculaire : radium et radon</h3>
  <p>Le radium-226 dure 1600 ans ; son fils, le radon-222, un gaz, seulement 3,8 jours. Dans un bocal scellé, le radon s'accumule jusqu'à se désintégrer aussi vite qu'il est produit : <i>A</i><sub>Rn</sub> = <i>A</i><sub>Ra</sub>(1 − e<sup>−λt</sup>), où λ est la constante de désintégration du radon. Au bout de quelques semaines, les deux se désintègrent au même rythme.</p>
  <div class="btns"><button class="btn" data-act="vent">Ouvrir le bocal</button></div>
</div>
<div class="step">
  <h3>Équilibre transitoire : la vache à technétium</h3>
  <p>Les hôpitaux reçoivent une colonne de molybdène-99 (66 heures) qui produit sans cesse du technétium-99m (6 heures), le traceur médical le plus utilisé. On extrait le technétium chaque matin et il se reforme, en suivant le molybdène qui s'éteint lentement.</p>
  <div class="btns"><button class="btn" data-act="milk">Traire le générateur</button><button class="btn ghost" data-act="genre">Nouveau générateur</button></div>
</div>
<div class="step">
  <h3>Le long de la chaîne de l'uranium</h3>
  <p>L'uranium-238 franchit quatorze étapes avant de devenir du plomb stable. Sur cette carte, une désintégration alpha descend de deux cases et recule de deux vers la gauche, une désintégration bêta monte d'une case et recule d'une vers la gauche. Dans un vieux minerai d'uranium non perturbé, chaque membre se désintègre au même rythme.</p>
  <div class="btns"><button class="btn" data-act="next">Désintégration suivante</button><button class="btn ghost" data-act="restart">Recommencer</button></div>
</div>`,
};

Object.assign(WT.L.labels, {
  /* step 1 */
  "parent {#}": "père {#}",
  "daughter {#}": "fils {#}",
  "stable {#}": "stable {#}",
  "parent ({#} s): {#}": "père ({#} s) : {#}",
  "daughter ({#} s): {#}": "fils ({#} s) : {#}",
  "granddaughter (stable): {#}": "petit-fils (stable) : {#}",
  "daughter peaks: {#} %": "pic du fils : {#} %",
  "{#} s": "{#} s",
  "illustrative half-lives": "demi-vies illustratives",
  /* step 2 */
  "radium{#}": "radium{#}",
  "radon{#} gas": "radon{#} (gaz)",
  "radium": "radium",
  "radium activity": "activité du radium",
  "radon": "radon",
  "radon activity": "activité du radon",
  "{#} d": "{#} j",
  "days →": "jours →",
  "day {#}: radon at {#} % of radium": "jour {#} : radon à {#} % du radium",
  /* step 3 */
  "Tc{#}m out": "Tc{#}m extrait",
  "Tc{#}m to the patient": "Tc{#}m vers le patient",
  "molybdenum{#}": "molybdène{#}",
  "dashed: never milked": "tirets : sans traite",
  "activity": "activité",
  "{#} h since last milking · Tc{#}m at {#} % of Mo{#}": "{#} h depuis la dernière traite · Tc{#}m à {#} % du Mo{#}",
  "regrows to its peak in about {#} hours": "revient à son pic en environ {#} heures",
  /* step 4 */
  "neutrons →": "neutrons →",
  "grey: stable": "gris : stable",
  "protons ↑": "protons ↑",
  "alpha: {#} p, {#} n": "alpha : {#} p, {#} n",
  "alpha: loses {#} protons and {#} neutrons": "alpha : perd {#} protons et {#} neutrons",
  "beta: n → p": "bêta : n → p",
  "beta: a neutron becomes a proton": "bêta : un neutron devient un proton",
  "U{#} · half-life {#} billion yr · alpha next": "U{#} · demi-vie {#} milliards d'années · puis alpha",
  "Th{#} · half-life {#} days · beta next": "Th{#} · demi-vie {#} jours · puis bêta",
  "Pa{#}m · half-life {#} min · beta next": "Pa{#}m · demi-vie {#} min · puis bêta",
  "U{#} · half-life {#} yr · alpha next": "U{#} · demi-vie {#} ans · puis alpha",
  "Th{#} · half-life {#} yr · alpha next": "Th{#} · demi-vie {#} ans · puis alpha",
  "Ra{#} · half-life {#} yr · alpha next": "Ra{#} · demi-vie {#} ans · puis alpha",
  "Rn{#} · half-life {#} days · alpha next": "Rn{#} · demi-vie {#} jours · puis alpha",
  "Po{#} · half-life {#} min · alpha next": "Po{#} · demi-vie {#} min · puis alpha",
  "Pb{#} · half-life {#} min · beta next": "Pb{#} · demi-vie {#} min · puis bêta",
  "Bi{#} · half-life {#} min · beta next": "Bi{#} · demi-vie {#} min · puis bêta",
  "Po{#} · half-life {#} µs · alpha next": "Po{#} · demi-vie {#} µs · puis alpha",
  "Pb{#} · half-life {#} years · beta next": "Pb{#} · demi-vie {#} ans · puis bêta",
  "Bi{#} · half-life {#} days · beta next": "Bi{#} · demi-vie {#} jours · puis bêta",
  "Po{#} · half-life {#} days · alpha next": "Po{#} · demi-vie {#} jours · puis alpha",
  "Pb{#}: stable, the chain ends": "Pb{#} : stable, la chaîne s'arrête",
  "step {#} of {#} · tap the nucleus": "étape {#} sur {#} · touchez le noyau",
});
