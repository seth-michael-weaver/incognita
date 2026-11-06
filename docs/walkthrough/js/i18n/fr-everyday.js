/* French (Français): everyday (Le nucléaire au quotidien) */
WT.L.ch.everyday = {
  num: "Leçon 4", title: "Le nucléaire au quotidien", short: "Quotidien",
  html: `
<div class="step">
  <h3>La TEP</h3>
  <p>Un traceur au fluor 18 (période de 110 minutes) émet des positons, et chacun se transforme en deux rayons gamma de 511 keV qui partent dos à dos. Faites glisser le point chaud : l'anneau trace une ligne pour chaque paire, et les lignes se croisent là où se trouve le traceur.</p>
</div>
<div class="step">
  <h3>Radiothérapie</h3>
  <p>Des faisceaux venus de plusieurs directions se superposent sur la tumeur, qui reçoit ainsi la dose complète tandis que chaque trajet dans les tissus sains n'en reçoit qu'une part. Faites glisser pour tourner les faisceaux et les tenir à l'écart de la moelle épinière.</p>
  <div class="ctl"><label for="ev-n">Faisceaux</label><input id="ev-n" type="range" data-bind="nb" data-instant min="1" max="7" step="1" value="5"><output data-show="nb" data-fmt="0"></output></div>
  <div class="ctl"><label for="ev-r">Rotation</label><input id="ev-r" type="range" data-bind="rotd" data-instant min="0" max="360" step="1" value="20"><output class="ev-rot"></output></div>
</div>
<div class="step">
  <h3>Technétium 99m</h3>
  <p>L'isotope de la plupart des examens de médecine nucléaire émet un rayon gamma de 140 keV qu'une caméra placée hors du corps peut voir, et avec une période de 6 heures il en reste peu au bout d'une journée. Les hôpitaux <a href="#chains-3">le traient à partir du molybdène 99</a>.</p>
  <div class="ctl"><label for="ev-t">Heures après l'injection</label><input id="ev-t" type="range" data-bind="th" data-instant min="0" max="48" step="0.5" value="0"><output data-show="th" data-fmt="1"></output></div>
</div>
<div class="step">
  <h3>Datation au carbone 14</h3>
  <p>Les êtres vivants absorbent sans cesse du carbone 14 ; après la mort, il décroît avec une période de 5730 ans. Réglez l'âge, ou mesurez ce qu'il reste pour lire l'âge.</p>
  <div class="ctl"><label for="ev-a">Âge (années)</label><input id="ev-a" type="range" data-bind="age" data-instant min="0" max="50000" step="10" value="5300"><output class="ev-age"></output></div>
  <div class="ctl"><label for="ev-f">Carbone 14 restant (%)</label><input id="ev-f" type="range" data-bind="fr" data-instant min="0.3" max="100" step="0.1" value="52.7"><output class="ev-fr"></output></div>
</div>
<div class="step">
  <h3>Détecteurs de fumée</h3>
  <p>Une poussière scellée d'américium 241 envoie des particules alpha à travers une petite lame d'air, créant des ions qui portent un courant minuscule. La fumée capte les ions, le courant chute et l'alarme sonne.</p>
  <div class="ctl"><label for="ev-s">Fumée</label><input id="ev-s" type="range" data-bind="sm" data-instant min="0" max="1" step="0.01" value="0"><output class="ev-sm"></output></div>
</div>`,
};

Object.assign(WT.L.labels, {
  "{#} beams cross: the tumour gets their sum": "{#} faisceaux se croisent : la tumeur reçoit leur somme",
  "{#} h": "{#} h",
  "{#} h: {#} % left": "{#} h : il reste {#} %",
  "{#} half-lives": "{#} périodes",
  "{#} keV gamma rays": "rayons gamma de {#} keV",
  "{#} of {#} left": "{#} sur {#} restants",
  "{#} years · {#} % left": "{#} ans · il reste {#} %",
  "~{#} y: too little to measure": "~{#} ans : trop peu pour mesurer",
  "a beam crosses the spinal cord: turn the beams": "un faisceau traverse la moelle : tournez les faisceaux",
  "a strong gamma signal, easy to image": "un signal gamma intense, facile à imager",
  "after a day, about {#} % is left": "au bout d'une journée, il en reste environ {#} %",
  "alarm": "alarme",
  "alpha particles make ions in the air": "les particules alpha créent des ions dans l'air",
  "Am{#}": "Am{#}",
  "americium{#} · half-life {#} years · alphas reach about {#} cm in air": "américium{#} · période {#} ans · les alphas parcourent environ {#} cm dans l'air",
  "americium{#} (sealed)": "américium{#} (scellé)",
  "beyond ~{#} years too little is left to measure": "au-delà de ~{#} ans, il en reste trop peu pour mesurer",
  "carbon{#}": "carbone{#}",
  "clean air: steady current": "air pur : courant stable",
  "current": "courant",
  "detector ring": "anneau de détecteurs",
  "dose": "dose",
  "each decay: two {#} keV gamma rays, back to back": "chaque désintégration : deux rayons gamma de {#} keV, dos à dos",
  "fading: half is gone every {#} hours": "décroissance : la moitié disparaît toutes les {#} heures",
  "fluorine{#} · half-life {#} min · {#} pairs recorded": "fluor{#} · période {#} min · {#} paires enregistrées",
  "gamma camera": "gamma-caméra",
  "half-life {#} y": "période {#} ans",
  "illustration": "illustration",
  "Mo{#} ({#} h)": "Mo{#} ({#} h)",
  "molybdenum{#}, half-life {#} h": "molybdène{#}, période {#} h",
  "nitrogen{#}": "azote{#}",
  "nitrogen{#} (after a beta decay)": "azote{#} (après une désintégration bêta)",
  "one beam: more dose near the skin than in the tumour": "un seul faisceau : plus de dose près de la peau que dans la tumeur",
  "Ötzi the Iceman, ~{#} y": "Ötzi, l'homme des glaces, ~{#} ans",
  "pairs of {#} keV gamma rays, back to back": "paires de rayons gamma de {#} keV, dos à dos",
  "physical decay only": "décroissance physique seule",
  "smoke: current down, alarm!": "fumée : le courant chute, alarme !",
  "some ions caught: current dipping": "quelques ions captés : le courant baisse",
  "spinal cord": "moelle épinière",
  "Tc{#}m ({#} h)": "Tc{#}m ({#} h)",
  "technetium{#}m, half-life {#} h": "technétium{#}m, période {#} h",
  "tracer": "traceur",
  "tracer (drag me)": "traceur (déplacez-moi)",
  "tumour": "tumeur",
  "tumour {#} % · spinal cord {#} % · healthy tissue at most {#} %": "tumeur {#} % · moelle {#} % · tissus sains au plus {#} %",
  "tumour {#} % · spinal cord {#} % · other tissue at most {#} %": "tumeur {#} % · moelle {#} % · autres tissus au plus {#} %",
  "years": "ans",
});
