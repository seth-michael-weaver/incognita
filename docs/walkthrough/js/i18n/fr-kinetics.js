/* French: kinetics (Leçon 1, cinétique du réacteur : six groupes et équation de Nordheim) */
WT.L.ch.kinetics = {
  num: "Leçon 1", title: "Cinétique du réacteur : six groupes et équation de Nordheim", short: "Cinétique",
  html: `
<div class="step">
  <h3>Six groupes de neutrons tardifs</h3>
  <p>Les neutrons retardés proviennent d'environ six groupes de produits de fission, de demi-vies comprises entre 0,23 s et 56 s (Keepin, U-235). Les groupes de 2 s et de 22 s en émettent la plupart, tandis que les groupes à vie longue détiennent l'essentiel du stock en attente : retard moyen Σ <i>a</i><sub>i</sub>/<i>λ</i><sub>i</sub> ≈ 13 s. Arrêtez les fissions et regardez chaque groupe s'épuiser à son propre rythme.</p>
  <div class="btns"><button class="btn" data-act="kistop" aria-pressed="false">Arrêter les fissions</button></div>
</div>
<div class="step">
  <h3>L'équation de Nordheim (« inhour »)</h3>
  <p>Essayez <i>n</i> ∝ e<sup><i>ωt</i></sup> dans la cinétique ponctuelle à six groupes et vous obtenez <i>ρ</i> = <i>ω</i>Λ + Σ <i>β</i><sub>i</sub><i>ω</i>/(<i>ω</i> + <i>λ</i><sub>i</sub>) : sept branches séparées par les pôles en −<i>λ</i><sub>i</sub>. Un échelon de <i>ρ</i> coupe chaque branche une fois ; la racine la plus à droite donne la période stable <i>T</i> = 1/<i>ω</i><sub>1</sub>, les six autres s'éteignent.</p>
  <div class="ctl"><label for="ki-r1">Réactivité ρ ($)</label><input id="ki-r1" type="range" data-bind="rd" data-instant min="-2" max="1.3" step="0.01" value="0.3"><output data-show="rd" data-fmt="2"></output></div>
</div>
<div class="step">
  <h3>Saut prompt et criticité prompte</h3>
  <p>Un échelon de réactivité élève d'abord la puissance en quelques millisecondes d'un facteur <i>P</i><sub>1</sub>/<i>P</i><sub>0</sub> ≈ <i>β</i>/(<i>β</i> − <i>ρ</i>), puis elle croît selon la période stable. À <i>ρ</i> = 1 $, les neutrons prompts seuls sont critiques et la période s'effondre vers Λ/(<i>ρ</i> − <i>β</i>).</p>
  <div class="ctl"><label for="ki-r2">Réactivité ρ ($)</label><input id="ki-r2" type="range" data-bind="rj" data-instant min="0.05" max="1.3" step="0.01" value="0.5"><output data-show="rj" data-fmt="2"></output></div>
</div>
<div class="step">
  <h3>Après un arrêt d'urgence</h3>
  <p>Insérez une forte réactivité négative : la puissance chute promptement à environ <i>β</i>/(<i>β</i> − <i>ρ</i>), puis ne peut pas baisser plus vite que ne décroît le groupe de plus longue demi-vie. Quelle que soit la profondeur de l'arrêt d'urgence, la période tend vers −1/<i>λ</i><sub>1</sub> ≈ −80 s.</p>
  <div class="ctl"><label for="ki-r3">Réactivité ρ ($)</label><input id="ki-r3" type="range" data-bind="rs" data-instant min="-30" max="-0.5" step="0.5" value="-10"><output data-show="rs" data-fmt="1"></output></div>
</div>`,
};
/* attributes referenced in the English chapter script (for the structure check): data-act="kistop" data-act="kistop" */

Object.assign(WT.L.labels, {
  "Stop fissions": "Arrêter les fissions",
  "Restart fissions": "Relancer les fissions",
  "half-life · share emitted": "demi-vie · part émise",
  "waiting stock": "stock en attente",
  "delayed neutrons out": "neutrons retardés émis",
  "{#} s": "{#} s",
  "{#} s after stopping · delayed emission {#} % of the start": "{#} s après l'arrêt · émission retardée {#} % du départ",
  "mean delay Σ aᵢ/λᵢ = {#} s · β = {#} (U{#})": "retard moyen Σ aᵢ/λᵢ = {#} s · β = {#} (U{#})",
  "Keepin six-group data": "données de Keepin à six groupes",
  "prompt critical": "critique prompt",
  "drag ρ": "glissez ρ",
  "prompt root": "racine prompte",
  "prompt root ≈ −(β−ρ)/Λ": "racine prompte ≈ −(β−ρ)/Λ",
  "ω ({#}/s), stretched": "ω ({#}/s), étiré",
  "ω ({#}/s), axis stretched (asinh)": "ω ({#}/s), axe étiré (asinh)",
  "ρ = 0: power stays flat": "ρ = 0 : la puissance reste constante",
  "ρ = {#}: power stays flat": "ρ = {#} : la puissance reste constante",
  "stable period T = {#}/ω₁ = {#} ms": "période stable T = {#}/ω₁ = {#} ms",
  "stable period T = {#}/ω₁ = {#} s": "période stable T = {#}/ω₁ = {#} s",
  "stable period T = {#}/ω₁ = {#} min": "période stable T = {#}/ω₁ = {#} min",
  "stable period T = {#}/ω₁ = {#} h": "période stable T = {#}/ω₁ = {#} h",
  "drag the rods out": "glissez pour retirer les barres",
  "prompt jump β/(β−ρ) = {#}": "saut prompt β/(β−ρ) = {#}",
  "power": "puissance",
  "prompt critical · period {#} ms (Λ = {#} µs)": "critique prompt · période {#} ms (Λ = {#} µs)",
  "prompt critical · period {#} s (Λ = {#} µs)": "critique prompt · période {#} s (Λ = {#} µs)",
  "prompt critical · period {#} min (Λ = {#} µs)": "critique prompt · période {#} min (Λ = {#} µs)",
  "prompt critical · period {#} h (Λ = {#} µs)": "critique prompt · période {#} h (Λ = {#} µs)",
  "ρ = {#} $ · stable period {#} ms": "ρ = {#} $ · période stable {#} ms",
  "ρ = {#} $ · stable period {#} s": "ρ = {#} $ · période stable {#} s",
  "ρ = {#} $ · stable period {#} min": "ρ = {#} $ · période stable {#} min",
  "ρ = {#} $ · stable period {#} h": "ρ = {#} $ · période stable {#} h",
  "drag the rods in": "glissez pour enfoncer les barres",
  "prompt drop to {#}": "chute prompte à {#}",
  "slope e^(−t/{#} s)": "pente e^(−t/{#} s)",
  "slope e^(−t / {#} s): the {#} s group": "pente e^(−t / {#} s) : le groupe de {#} s",
  "power ×{#} speed": "puissance, vitesse ×{#}",
  "ρ = {#} $ · stable period {#} ms (limit {#} s)": "ρ = {#} $ · période stable {#} ms (limite {#} s)",
  "ρ = {#} $ · stable period {#} s (limit {#} s)": "ρ = {#} $ · période stable {#} s (limite {#} s)",
  "ρ = {#} $ · stable period {#} min (limit {#} s)": "ρ = {#} $ · période stable {#} min (limite {#} s)",
  "ρ = {#} $ · stable period {#} h (limit {#} s)": "ρ = {#} $ · période stable {#} h (limite {#} s)",
});
