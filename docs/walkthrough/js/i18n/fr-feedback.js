/* French: feedback (Stabilité du réacteur et contre-réactions) */
WT.L.ch.feedback = {
  num: "Leçon 1", title: "Stabilité du réacteur et contre-réactions", short: "Contre-réactions",
  html: `
<div class="step">
  <h3>Une boucle : puissance, chaleur, réactivité</h3>
  <p>Plus de puissance chauffe le combustible et l'eau, et leurs températures modifient la réactivité <i>ρ</i>, qui fixe la puissance. Ajoutez un échelon de réactivité et regardez le signal faire le tour de la boucle. Avec des coefficients négatifs, elle s'y oppose.</p>
  <div class="ctl"><label for="fb-r">Échelon de réactivité (pcm)</label><input id="fb-r" type="range" data-bind="rs" data-instant min="50" max="300" step="10" value="200"><output data-show="rs" data-fmt="0"></output></div>
  <div class="btns"><button class="btn" data-act="fbIns">Insérer</button> <button class="btn ghost" data-act="fbRes">Réinitialiser</button></div>
</div>
<div class="step">
  <h3>Doppler : le frein rapide</h3>
  <p>Un combustible plus chaud capture davantage de neutrons dans l'uranium-238, sans fission (<a href="#doppler">élargissement Doppler</a>). Le combustible chauffe en quelques secondes : ce frein agit donc en premier, et dans les réacteurs à eau il est toujours négatif. Ici, c'est la seule contre-réaction.</p>
  <div class="ctl"><label for="fb-d">Coefficient Doppler (pcm/K)</label><input id="fb-d" type="range" data-bind="aD" data-instant min="-5" max="-1" step="0.1" value="-2.5"><output data-show="aD" data-fmt="1"></output></div>
  <div class="btns"><button class="btn" data-act="fbIns">Insérer</button> <button class="btn ghost" data-act="fbRes">Réinitialiser</button></div>
</div>
<div class="step">
  <h3>Le modérateur entre en jeu</h3>
  <p>Une eau plus chaude est moins dense : elle ralentit moins bien les neutrons. Dans un réacteur à eau sous pression, avec une concentration de bore normale, le coefficient de modérateur devient lui aussi négatif : un second frein, plus lent, et la puissance se stabilise plus bas.</p>
  <div class="ctl"><label for="fb-m">Coefficient de modérateur (pcm/K)</label><input id="fb-m" type="range" data-bind="aM" data-instant min="-60" max="0" step="1" value="-30"><output data-show="aM" data-fmt="0"></output></div>
  <div class="btns"><button class="btn" data-act="fbIns">Insérer</button> <button class="btn ghost" data-act="fbRes">Réinitialiser</button></div>
</div>
<div class="step">
  <h3>Quand la contre-réaction est positive</h3>
  <p>Si le terme du caloporteur est positif et l'emporte sur l'effet Doppler, plus de puissance signifie plus de réactivité, et la puissance s'emballe. Les réacteurs à eau sont conçus avec des coefficients négatifs ; certaines conceptions, comme le RBMK à faible puissance, pouvaient avoir un coefficient de vide positif.</p>
  <div class="ctl"><label for="fb-c">Coefficient du caloporteur (pcm/K)</label><input id="fb-c" type="range" data-bind="aM" data-instant min="-60" max="150" step="5" value="150"><output data-show="aM" data-fmt="0"></output></div>
  <div class="btns"><button class="btn" data-act="fbIns">Insérer</button> <button class="btn ghost" data-act="fbRes">Réinitialiser</button></div>
</div>`,
};

Object.assign(WT.L.labels, {
  // the loop
  "heat": "chaleur",
  "heats water": "chauffe l'eau",
  "chain": "chaîne",
  "chain reaction": "réaction en chaîne",
  "αM +": "αM +",
  "αM −": "αM −",
  "αM {#}": "αM {#}",
  "αC +": "αC +",
  "αC −": "αC −",
  "αC {#}": "αC {#}",
  "αD −": "αD −",
  "P {#} %": "P {#} %",
  "fuel +{#} K": "comb. +{#} K",
  "fuel {#} K": "comb. {#} K",
  "fuel ΔT +{#} K": "combustible ΔT +{#} K",
  "fuel ΔT {#} K": "combustible ΔT {#} K",
  "water +{#} K": "eau +{#} K",
  "water {#} K": "eau {#} K",
  "water ΔT +{#} K": "eau ΔT +{#} K",
  "water ΔT {#} K": "eau ΔT {#} K",
  "ρ +{#} pcm": "ρ +{#} pcm",
  "ρ {#} pcm": "ρ {#} pcm",
  // formulas and coefficients
  "ρ = ρext + αD ΔTf + αM ΔTm": "ρ = ρext + αD ΔTf + αM ΔTm",
  "C dT/dt = P − h (T − Tc)": "C dT/dt = P − h (T − Tc)",
  "Doppler α_D = {a} pcm/K": "Doppler α_D = {a} pcm/K",
  "moderator α_M = {a} pcm/K": "modérateur α_M = {a} pcm/K",
  "coolant α_C = {a} pcm/K": "caloporteur α_C = {a} pcm/K",
  "inserted ρ_ext = {a}": "inséré ρ_ext = {a}",
  // power trace
  "+{a} pcm": "+{a} pcm",
  "power": "puissance",
  "last {#} s →": "dernières {#} s →",
  "last {#} seconds →": "{#} dernières secondes →",
  // verdict
  "power ran away · protection would shut it down": "la puissance s'est emballée · la protection arrêterait le réacteur",
  "power ran away · in a real plant the protection system would shut it down": "la puissance s'est emballée · dans une vraie centrale, le système de protection arrêterait le réacteur",
  "steady at {#} % · press Insert": "stable à {#} % · appuyez sur Insérer",
  "steady at {#} % power · press Insert to add reactivity": "stable à {#} % de puissance · appuyez sur Insérer pour ajouter de la réactivité",
  "power coefficient {a} pcm per {#} %: settles": "coefficient de puissance {a} pcm par {#} % : se stabilise",
  "power coefficient {a} pcm per {#} % power: self-stabilising": "coefficient de puissance {a} pcm par {#} % de puissance : autostabilisant",
  "power coefficient +{a} pcm per {#} %: runs away": "coefficient de puissance +{a} pcm par {#} % : s'emballe",
  "power coefficient +{a} pcm per {#} % power: runs away": "coefficient de puissance +{a} pcm par {#} % de puissance : s'emballe",
  "illustrative model": "modèle illustratif",
});
