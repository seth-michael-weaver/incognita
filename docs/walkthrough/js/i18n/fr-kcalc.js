/* French: kcalc (Computing criticality) */
WT.L.ch.kcalc = {
  num: "Leçon 1", title: "Calcul de la criticité", short: "Calcul de k",
  html: `
<div class="step">
  <h3>Les benchmarks</h3>
  <p>Quatre assemblages critiques rapides métalliques de l’ICSBEP, à l’échelle. Godiva et Jezebel sont des sphères nues ; Flattop-25 et Flattop-Pu ont un réflecteur en uranium naturel.</p>
</div>
<div class="step">
  <h3><i>k</i><sub>eff</sub> calculé</h3>
  <p>OpenMC, énergie continue, géométrie 3-D. Les quatre sont dans le ±1σ du benchmark. <i>k</i><sub>eff</sub> n’est pas utilisé dans l’ajustement.</p>
</div>
<div class="step">
  <h3>Profils de sensibilité</h3>
  <p>Sensibilité adjointe de <i>k</i><sub>eff</sub> à chaque réaction, par unité de léthargie.</p>
  <div class="btns"><button class="btn ghost" data-act="se0" aria-pressed="true">Godiva</button><button class="btn ghost" data-act="se1" aria-pressed="false">Jezebel</button><button class="btn ghost" data-act="se2" aria-pressed="false">Flattop-Pu</button></div>
</div>
<div class="step">
  <h3>Vérifié par perturbation directe</h3>
  <p>Variations de <i>k</i><sub>eff</sub> prédites contre recalculées, 63 jeux de données perturbés.</p>
</div>
<div class="step">
  <h3>Cœur de réacteur C5G7</h3>
  <p>OCDE/AEN C5G7, quart de cœur 2-D, 1 056 crayons UO<sub>2</sub> et MOX. <i>k</i><sub>eff</sub> à −19&nbsp;pcm de la référence ; erreur maximale de puissance par crayon 0,13&nbsp;%.</p>
</div>`,
};

Object.assign(WT.L.labels, {
  "{#} pcm  (±{#} benchmark)": "{#} pcm  (benchmark ±{#})",
  "+{#} pcm  (±{#} benchmark)": "+{#} pcm  (benchmark ±{#})",
  "Calculated − experimental k, with the benchmark ±{#}σ band": "k calculé − expérimental, avec la bande ±{#}σ du benchmark",
  "Drag to rotate": "Faire glisser pour tourner",
  "Godiva, integral sensitivity: ν {#}, fission {#} (% k per % change)": "Godiva, sensibilité intégrale : ν {#}, fission {#} (% de k par % de variation)",
  "Jezebel, integral sensitivity: ν {#}, fission {#} (% k per % change)": "Jezebel, sensibilité intégrale : ν {#}, fission {#} (% de k par % de variation)",
  "Flattop-Pu, integral sensitivity: ν {#}, fission {#} (% k per % change)": "Flattop-Pu, sensibilité intégrale : ν {#}, fission {#} (% de k par % de variation)",
  "Godiva: ν {#}, fission {#}": "Godiva: ν {#}, fission {#}",
  "Jezebel: ν {#}, fission {#}": "Jezebel: ν {#}, fission {#}",
  "Flattop-Pu: ν {#}, fission {#}": "Flattop-Pu: ν {#}, fission {#}",
  "UO₂: {#} × mean": "UO₂: {#} × moyenne",
  "MOX {#} %: {#} × mean": "MOX {#} %: {#} × moyenne",
  "OpenMC re-solve, Δk (pcm)": "Recalcul OpenMC, Δk (pcm)",
  "Predicted from sensitivities, Δk (pcm)": "Prédit par les sensibilités, Δk (pcm)",
  "predicted Δk, pcm": "Δk prédit, pcm",
  "U{#} capture": "capture U{#}",
  "Pu{#} capture": "capture Pu{#}",
  "U{#} elastic": "élastique U{#}",
  "Pu{#} elastic": "élastique Pu{#}",
  "U{#} fission": "fission U{#}",
  "Pu{#} fission": "fission Pu{#}",
  "U{#} inelastic": "inélastique U{#}",
  "Pu{#} inelastic": "inélastique Pu{#}",
  "U{#} neutrons per fission (ν)": "neutrons par fission U{#} (ν)",
  "Pu{#} neutrons per fission (ν)": "neutrons par fission Pu{#} (ν)",
  "Relative pin power (hover a pin)": "Puissance relative par crayon (survoler un crayon)",
  "Relative pin power (tap a pin)": "Puissance relative par crayon (toucher un crayon)",
  "To scale.": "À l’échelle.",
  "To scale. Drag to rotate.": "À l’échelle. Faire glisser pour tourner.",
  "core {#} cm, reflector {#} cm": "cœur {#} cm, réflecteur {#} cm",
  "radius {#} cm": "rayon {#} cm",
  "{#} cm in {#} cm": "{#} cm dans {#} cm",
  "k = {#}; reference {#} ({#} pcm)": "k = {#} ; référence {#} ({#} pcm)",
  "k {#}, reference {#}": "k {#}, référence {#}",
  "plutonium in natural uranium": "plutonium dans l’uranium naturel",
  "plutonium metal": "plutonium métal",
  "uranium{#} in natural uranium": "uranium{#} dans l’uranium naturel",
  "uranium{#} metal": "uranium{#} métal",
  "water": "eau",
  "×{#} of mean": "×{#} de la moyenne",
  "U{#} ν": "U{#} ν",
  "Pu{#} ν": "Pu{#} ν",
  "Godiva   k = {#}": "Godiva   k = {#}",
  "Godiva {#}": "Godiva {#}",
  "Godiva: rms {#} pcm": "Godiva: rms {#} pcm",
  "Jezebel   k = {#}": "Jezebel   k = {#}",
  "Jezebel {#}": "Jezebel {#}",
  "Jezebel: rms {#} pcm": "Jezebel: rms {#} pcm",
  "Flattop-Pu   k = {#}": "Flattop-Pu   k = {#}",
  "Flattop-Pu {#}": "Flattop-Pu {#}",
  "Flattop-Pu: rms {#} pcm": "Flattop-Pu: rms {#} pcm",
  "Flattop{#}   k = {#}": "Flattop{#}   k = {#}",
  "Flattop{#} {#}": "Flattop{#} {#}",
  "{#} pcm (±{#})": "{#} pcm (±{#})",
  "+{#} pcm (±{#})": "+{#} pcm (±{#})",
  "{#} cm": "{#} cm",
  "{#} keV": "{#} keV",
  "{#} MeV": "{#} MeV",
  "OpenMC Δk": "OpenMC Δk"
});
