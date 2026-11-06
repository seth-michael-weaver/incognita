/* French: breeding (La surgénération du combustible) */
WT.L.ch.breeding = {
  num: "Leçon 1", title: "La surgénération du combustible", short: "Surgénération",
  html: `
<div class="step">
  <h3>Le fertile devient fissile</h3>
  <p>L'uranium-238 ne se fissionne presque pas, mais il peut capturer un neutron. Deux désintégrations bêta plus tard (à chaque fois, un neutron du noyau se change en proton), il est devenu du plutonium-239, qui se fissionne facilement. Le thorium-232 fait de même et devient de l'uranium-233.</p>
  <div class="btns"><button class="btn ghost" data-act="bcU" aria-pressed="true">Uranium-238</button> <button class="btn ghost" data-act="bcT" aria-pressed="false">Thorium-232</button></div>
</div>
<div class="step">
  <h3>Le bilan neutronique</h3>
  <p>Chaque neutron absorbé dans le combustible fissile en rend <i>η</i> nouveaux. L'un doit provoquer la fission suivante et certains sont perdus ; ce qui reste peut servir à surgénérer. Avec l'uranium-235 et des neutrons lents, il ne se forme qu'environ 0,6 nouveau noyau fissile par noyau brûlé.</p>
  <div class="btns"><button class="btn ghost" data-act="bfU5" aria-pressed="true">U-235</button> <button class="btn ghost" data-act="bfP9" aria-pressed="false">Pu-239</button> <button class="btn ghost" data-act="bfU3" aria-pressed="false">U-233</button></div>
  <div class="btns"><button class="btn ghost" data-act="bsT" aria-pressed="true">Neutrons lents</button> <button class="btn ghost" data-act="bsF" aria-pressed="false">Neutrons rapides</button></div>
</div>
<div class="step">
  <h3>Les neutrons rapides surgénèrent</h3>
  <p>Pour surgénérer, un neutron doit poursuivre la chaîne et au moins un autre doit produire du combustible neuf : <i>η</i> doit donc dépasser 2 d'une marge supérieure aux pertes. Le plutonium-239 dans un réacteur à neutrons rapides donne environ 2,4 : de quoi en revendre.</p>
  <div class="ctl"><label for="br-l1">Neutrons perdus</label><input id="br-l1" type="range" data-bind="L" data-instant min="0.05" max="0.8" step="0.01" value="0.2"><output data-show="L" data-fmt="2"></output></div>
</div>
<div class="step">
  <h3>Le thorium en neutrons lents</h3>
  <p>En neutrons lents, le plutonium-239 ne donne qu'environ 2,1, mais l'uranium-233 donne 2,29. Cette marge permet à un réacteur au thorium de surgénérer avec des neutrons lents, s'il en gaspille très peu. Réduisez les pertes jusqu'à ce qu'il surgénère.</p>
  <div class="ctl"><label for="br-l2">Neutrons perdus</label><input id="br-l2" type="range" data-bind="L" data-instant min="0.05" max="0.8" step="0.01" value="0.35"><output data-show="L" data-fmt="2"></output></div>
</div>
<div class="step">
  <h3>Le taux de conversion</h3>
  <p>Le taux de conversion est le nombre de noyaux fissiles produits par noyau fissile brûlé. En dessous de 1, le combustible s'épuise lentement (un convertisseur, comme les réacteurs à eau actuels) ; au-dessus de 1, le réacteur finit avec plus de combustible qu'au départ (un surgénérateur).</p>
  <div class="btns"><button class="btn ghost" data-act="bfU5" aria-pressed="true">U-235</button> <button class="btn ghost" data-act="bfP9" aria-pressed="false">Pu-239</button> <button class="btn ghost" data-act="bfU3" aria-pressed="false">U-233</button></div>
  <div class="btns"><button class="btn ghost" data-act="bsT" aria-pressed="true">Neutrons lents</button> <button class="btn ghost" data-act="bsF" aria-pressed="false">Neutrons rapides</button></div>
</div>`,
};

Object.assign(WT.L.labels, {
  "illustration": "illustration",
  // scene 1: the chain
  "{#} protons": "{#} protons",
  "{#} p": "{#} p",
  "fertile": "fertile",
  "fertile: barely splits": "fertile : se fissionne à peine",
  "fissile": "fissile",
  "fissile: splits easily": "fissile : se fissionne facilement",
  "+ n": "+ n",
  "catch": "capture",
  "{#} min": "{#} min",
  "{#} d": "{#} j",
  "e⁻": "e⁻",
  "electron": "électron",
  "antineutrino": "antineutrino",
  "{a} waiting: day {b}": "{a} en attente : jour {b}",
  "a batch of {a} waiting · day {b}": "un lot de {a} en attente · jour {b}",
  "{a} % now {b}": "{a} % devenus {b}",
  "after {#} weeks, {#} % has become Pu{#}": "après {#} semaines, {#} % est devenu du Pu{#}",
  "after {#} months, {#} % has become U{#}": "après {#} mois, {#} % est devenu de l'U{#}",
  "slow step: Np{#}, half-life {#} d": "étape lente : Np{#}, demi-vie {#} j",
  "slow step: Pa{#}, half-life {#} d": "étape lente : Pa{#}, demi-vie {#} j",
  "the slow step is Np{#} (half-life {#} days)": "l'étape lente est Np{#} (demi-vie {#} jours)",
  "the slow step is Pa{#} (half-life {#} days)": "l'étape lente est Pa{#} (demi-vie {#} jours)",
  // scenes 2-4: the neutron budget
  "slow neutrons": "neutrons lents",
  "fast neutrons": "neutrons rapides",
  "next fission": "fission suivante",
  "next fission: keeps the chain going": "fission suivante : entretient la chaîne",
  "U{#} → Pu{#}": "U{#} → Pu{#}",
  "Th{#} → U{#}": "Th{#} → U{#}",
  "breeds: U{#} → Pu{#}": "surgénère : U{#} → Pu{#}",
  "breeds: Th{#} → U{#}": "surgénère : Th{#} → U{#}",
  "lost": "perdus",
  "lost: water, steel, poisons, leakage": "perdus : eau, acier, poisons, fuites",
  "{a} per absorption": "{a} par absorption",
  "chain": "chaîne",
  "breed": "surgénère",
  "η = {a}": "η = {a}",
  "η ≈ {a}": "η ≈ {a}",
  "{#}: breeding line": "{#} : seuil de surgénération",
  "neutrons per absorption": "neutrons par absorption",
  "neutrons out per neutron absorbed in the fuel": "neutrons émis par neutron absorbé dans le combustible",
  "conversion ratio ≈ η − {#} − lost = {a}: breeds": "taux de conversion ≈ η − {#} − pertes = {a} : surgénère",
  "conversion ratio ≈ η − {#} − lost = {a}: breeds, makes more fuel than it burns": "taux de conversion ≈ η − {#} − pertes = {a} : surgénère, produit plus de combustible qu'il n'en brûle",
  "conversion ratio ≈ η − {#} − lost = {a}: converts": "taux de conversion ≈ η − {#} − pertes = {a} : convertit",
  "conversion ratio ≈ η − {#} − lost = {a}: converts, makes less fuel than it burns": "taux de conversion ≈ η − {#} − pertes = {a} : convertit, produit moins de combustible qu'il n'en brûle",
  // scene 5: conversion ratio
  "Th{#}": "Th{#}",
  "U{#} (fertile)": "U{#} (fertile)",
  "Th{#} (fertile)": "Th{#} (fertile)",
  "split": "fissionnés",
  "split (fission products)": "fissionnés (produits de fission)",
  "burned {a}": "brûlés {a}",
  "made {a}": "produits {a}",
  "{a} · slow neutrons": "{a} · neutrons lents",
  "{a} · fast neutrons": "{a} · neutrons rapides",
  "conversion ratio {a}: a breeder": "taux de conversion {a} : surgénérateur",
  "conversion ratio {a}: a converter": "taux de conversion {a} : convertisseur",
});
