/* French: burnup (Le taux de combustion) */
WT.L.ch.burnup = {
  num: "Leçon 1", title: "Le taux de combustion", short: "Taux de combustion",
  html: `
<div class="step">
  <h3>Une pastille au fil de sa vie</h3>
  <p>Voici mille atomes d'une pastille de combustible neuve : 45 sont de l'uranium-235, les autres de l'uranium-238. Faites fonctionner le réacteur et regardez l'uranium-235 se fissionner tandis que de nouveaux atomes apparaissent. Le <b>taux de combustion</b> compte l'énergie extraite, en gigawatts-jours par tonne d'uranium ; les réacteurs à eau s'arrêtent vers 45–55.</p>
  <div class="ctl"><label for="bu-d1">Jours à pleine puissance</label><input id="bu-d1" type="range" data-bind="d" data-instant min="0" max="1400" step="10" value="400"><output data-show="d" data-fmt="0"></output></div>
</div>
<div class="step">
  <h3>Le plutonium s'en mêle</h3>
  <p>L'uranium-238 capture des neutrons et devient du plutonium-239, qui se fissionne lui aussi. En fin de vie, plus de la moitié des fissions ont lieu dans le plutonium ; sur toute la vie du combustible, environ un tiers de l'énergie en provient.</p>
  <div class="ctl"><label for="bu-d2">Jours à pleine puissance</label><input id="bu-d2" type="range" data-bind="d" data-instant min="0" max="1400" step="10" value="1000"><output data-show="d" data-fmt="0"></output></div>
</div>
<div class="step">
  <h3>Les poisons s'accumulent</h3>
  <p>Chaque fission laisse deux produits de fission, et certains absorbent des neutrons. Avec moins d'uranium-235 et plus de poisons, <i>k</i><sub>∞</sub> (nouvelles fissions par fission dans un réseau infini de ce combustible) baisse peu à peu, jusqu'à ce que le combustible ne puisse plus entretenir seul une réaction en chaîne.</p>
  <div class="ctl"><label for="bu-d3">Jours à pleine puissance</label><input id="bu-d3" type="range" data-bind="d" data-instant min="0" max="1400" step="10" value="700"><output data-show="d" data-fmt="0"></output></div>
</div>
<div class="step">
  <h3>Le bore et les rechargements</h3>
  <p>Un cœur mélange du combustible neuf, d'âge moyen et ancien. Le combustible neuf a trop de réactivité : du bore dissous dans l'eau de refroidissement absorbe l'excédent et est peu à peu dilué. Quand il atteint zéro, le tiers le plus ancien sort et du combustible neuf entre.</p>
  <div class="ctl"><label for="bu-m">Mois à pleine puissance</label><input id="bu-m" type="range" data-bind="m" data-instant min="0" max="54" step="0.5" value="8"><output data-show="m" data-fmt="1"></output></div>
</div>`,
};

Object.assign(WT.L.labels, {
  "illustrative model": "modèle illustratif",
  // scenes 1-3: the pellet
  "{a} days · burnup {b} GWd/t": "{a} jours · taux de combustion {b} GWj/t",
  "uranium{#}": "uranium{#}",
  "plutonium{#}": "plutonium{#}",
  "other Pu": "autre Pu",
  "other plutonium": "autre plutonium",
  "fission products": "produits de fission",
  "fission products (pairs)": "produits de fission (paires)",
  "{a} in {#}": "{a} sur {#}",
  "uranium{#}: the remaining ~{#}–{#} %": "uranium{#} : le reste, ~{#}–{#} %",
  "plutonium's share": "part du plutonium",
  "fissions": "fissions",
  "fissions now": "fissions actuelles",
  "energy so far": "énergie cumulée",
  "Pu": "Pu",
  "plutonium": "plutonium",
  "split": "fissionnés",
  "each dot: {#} atom in {#}": "chaque point : {#} atome sur {#}",
  "each dot: one atom in a thousand": "chaque point : un atome sur mille",
  // scene 3: k-infinity
  "k = {#}": "k = {#}",
  "GWd/t →": "GWj/t →",
  "burnup (GWd/t) →": "taux de combustion (GWj/t) →",
  "typical discharge": "déchargement typique",
  "typical discharge {#}–{#}": "déchargement typique {#}–{#}",
  "can't keep a chain going alone": "ne peut plus entretenir seul la chaîne",
  "this fuel alone can no longer keep a chain going": "seul, ce combustible ne peut plus entretenir de réaction en chaîne",
  "k∞ reaches {#}": "k∞ atteint {#}",
  "k∞ = {a}": "k∞ = {a}",
  "fission products catch {a} % of neutrons": "les produits de fission capturent {a} % des neutrons",
  // scene 4: the core and boron
  "fresh": "neuf",
  "{#} cycle": "{#} cycle",
  "one cycle old": "un cycle d'usage",
  "{#} cycles": "{#} cycles",
  "two cycles old": "deux cycles d'usage",
  "reload": "rechargement",
  "boron (ppm)": "bore (ppm)",
  "boron in the water (ppm)": "bore dans l'eau (ppm)",
  "months →": "mois →",
  "months at full power →": "mois à pleine puissance →",
  "{a} ppm": "{a} ppm",
  "cycle {a} months · fuel leaves at {b} GWd/t": "cycle de {a} mois · le combustible sort à {b} GWj/t",
});
