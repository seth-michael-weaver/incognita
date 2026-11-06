/* French (Français): sandbox (Construire un réacteur) */
WT.L.ch.sandbox = {
  num: "Leçon 1", title: "Construire un réacteur", short: "Construire un réacteur",
  lead: "Choisissez un combustible, un modérateur, un caloporteur et une taille, et voyez si une réaction en chaîne peut s'entretenir d'elle-même. Un modèle de manuel simplifié.",
  html: `
<div class="step">
  <h3>Quatre facteurs</h3>
  <p>Si aucun neutron ne s'échappait, chaque neutron absorbé en donnerait <i>k</i><sub>∞</sub> = <i>η f p ε</i> nouveaux ; cet empilement de graphite et d'uranium naturel y parvient tout juste.</p>
</div>
<div class="step">
  <h3>Choisir un modérateur</h3>
  <p>Avec de l'uranium naturel, seuls l'eau lourde ou le graphite font passer <i>k</i><sub>∞</sub> au-dessus de 1 : l'eau légère ralentit bien les neutrons mais en absorbe trop.</p>
  <div class="btns" role="group" aria-label="Modérateur"><button class="btn ghost" data-act="mo_h2o">Eau légère</button> <button class="btn ghost" data-act="mo_d2o">Eau lourde</button> <button class="btn ghost" data-act="mo_c">Graphite</button></div>
  <div class="ctl"><label for="sb-m1">Modérateur par combustible</label><input id="sb-m1" type="range" data-bind="lm" min="-0.5" max="2.3" step="0.01" value="0.3"><output class="sb-m"></output></div>
</div>
<div class="step">
  <h3>Enrichir le combustible</h3>
  <p>Quelques pour cent d'uranium 235 rendent l'eau ordinaire utilisable, c'est pourquoi la plupart des réacteurs actuels l'emploient.</p>
  <div class="btns" role="group" aria-label="Combustible"><button class="btn ghost" data-act="fu_nat">U naturel</button> <button class="btn ghost" data-act="fu_leu">U enrichi</button> <button class="btn ghost" data-act="fu_mox">MOX (Pu)</button> <button class="btn ghost" data-act="fu_th">Thorium + U-233</button></div>
  <div class="ctl"><label for="sb-e1">Part fissile (%)</label><input id="sb-e1" type="range" data-bind="enr" min="0.7" max="30" step="0.1" value="3"><output data-show="enr" data-fmt="1"></output></div>
</div>
<div class="step">
  <h3>Taille et fuites</h3>
  <p>Les neutrons s'échappent par la surface, donc <i>k</i> = <i>k</i><sub>∞</sub> / (1 + <i>M</i>²<i>B</i>²). Faites glisser le bord de cet empilement de graphite et d'uranium naturel jusqu'à l'anneau pointillé.</p>
  <div class="ctl"><label for="sb-r1">Rayon du cœur (m)</label><input id="sb-r1" type="range" data-bind="R" min="0.2" max="6" step="0.05" value="2"><output data-show="R" data-fmt="2"></output></div>
</div>
<div class="step">
  <h3>Quand le caloporteur bout</h3>
  <p>Dans un cœur en graphite refroidi à l'eau, l'ébullition fait monter <i>k</i>, car l'eau absorbait plus qu'elle ne ralentissait : le défaut du RBMK à Tchernobyl. Essayez d'autres caloporteurs.</p>
  <div class="btns" role="group" aria-label="Caloporteur"><button class="btn ghost" data-act="co_h2o">Eau</button> <button class="btn ghost" data-act="co_gas">CO₂ / hélium</button> <button class="btn ghost" data-act="co_na">Sodium</button></div>
</div>
<div class="step">
  <h3>Construisez le vôtre</h3>
  <p>Tout est permis. Un réacteur à neutrons rapides n'a pas de modérateur et exige bien plus de combustible fissile.</p>
  <div class="btns" role="group" aria-label="Combustible"><button class="btn ghost" data-act="fu_nat">U naturel</button> <button class="btn ghost" data-act="fu_leu">U enrichi</button> <button class="btn ghost" data-act="fu_mox">MOX (Pu)</button> <button class="btn ghost" data-act="fu_th">Thorium + U-233</button></div>
  <div class="ctl"><label for="sb-e2">Part fissile (%)</label><input id="sb-e2" type="range" data-bind="enr" min="0.7" max="30" step="0.1" value="3"><output data-show="enr" data-fmt="1"></output></div>
  <div class="btns" role="group" aria-label="Modérateur"><button class="btn ghost" data-act="mo_none">Pas de modérateur</button> <button class="btn ghost" data-act="mo_h2o">Eau légère</button> <button class="btn ghost" data-act="mo_d2o">Eau lourde</button> <button class="btn ghost" data-act="mo_c">Graphite</button></div>
  <div class="ctl"><label for="sb-m2">Modérateur par combustible</label><input id="sb-m2" type="range" data-bind="lm" min="-0.5" max="2.3" step="0.01" value="0.3"><output class="sb-m"></output></div>
  <div class="btns" role="group" aria-label="Caloporteur"><button class="btn ghost" data-act="co_h2o">Eau</button> <button class="btn ghost" data-act="co_d2o">Eau lourde</button> <button class="btn ghost" data-act="co_gas">CO₂ / hélium</button> <button class="btn ghost" data-act="co_na">Sodium</button> <button class="btn ghost" data-act="co_pb">Plomb</button> <button class="btn ghost" data-act="co_salt">Sel fondu</button></div>
  <div class="ctl"><label for="sb-r2">Rayon du cœur (m)</label><input id="sb-r2" type="range" data-bind="R" min="0.2" max="6" step="0.05" value="2"><output data-show="R" data-fmt="2"></output></div>
</div>`,
};

Object.assign(WT.L.labels, {
  "{#} % U{#}": "{#} % U{#}",
  "= η f p ε, if nothing leaked": "= η f p ε, sans fuites",
  "= η f, if nothing leaked": "= η f, sans fuites",
  "absorbed in fuel": "absorbés dans le combustible",
  "bonus from fast fission": "bonus de la fission rapide",
  "can never sustain a chain, at any size": "ne peut jamais entretenir une chaîne, quelle que soit la taille",
  "caught by fuel": "capturés par le combustible",
  "CO₂ / helium gas coolant": "caloporteur : gaz CO₂ / hélium",
  "coolant boils away: k ↑": "le caloporteur s'évapore : k ↑",
  "coolant boils away: k ↑ (big sodium cores: spectrum hardens)": "le caloporteur s'évapore : k ↑ (grands cœurs sodium : le spectre durcit)",
  "coolant boils away: k ↑ (small; positive in CANDU)": "le caloporteur s'évapore : k ↑ (faible ; positif dans les CANDU)",
  "coolant boils away: k ↑ (smaller than with sodium)": "le caloporteur s'évapore : k ↑ (plus faible qu'avec le sodium)",
  "coolant boils away: k ↓": "le caloporteur s'évapore : k ↓",
  "coolant boils away: k ≈": "le caloporteur s'évapore : k ≈",
  "coolant boils away: k barely changes": "le caloporteur s'évapore : k change à peine",
  "coolant boils: k ↑": "le caloporteur bout : k ↑",
  "coolant boils: k ↓": "le caloporteur bout : k ↓",
  "coolant boils: k ≈": "le caloporteur bout : k ≈",
  "coolant heats: k ↑": "le caloporteur chauffe : k ↑",
  "coolant heats: k ↑ (big sodium cores: spectrum hardens)": "le caloporteur chauffe : k ↑ (grands cœurs sodium : le spectre durcit)",
  "coolant heats: k ↑ (small; positive in CANDU)": "le caloporteur chauffe : k ↑ (faible ; positif dans les CANDU)",
  "coolant heats: k ↑ (smaller than with sodium)": "le caloporteur chauffe : k ↑ (plus faible qu'avec le sodium)",
  "coolant heats: k ↓": "le caloporteur chauffe : k ↓",
  "coolant heats: k ≈": "le caloporteur chauffe : k ≈",
  "coolant heats: k barely changes": "le caloporteur chauffe : k change à peine",
  "coolant lost: k ↑": "caloporteur perdu : k ↑",
  "coolant lost: k ↑ (big sodium cores: spectrum hardens)": "caloporteur perdu : k ↑ (grands cœurs sodium : le spectre durcit)",
  "coolant lost: k ↑ (small; positive in CANDU)": "caloporteur perdu : k ↑ (faible ; positif dans les CANDU)",
  "coolant lost: k ↑ (smaller than with sodium)": "caloporteur perdu : k ↑ (plus faible qu'avec le sodium)",
  "coolant lost: k ↓": "caloporteur perdu : k ↓",
  "coolant lost: k ≈": "caloporteur perdu : k ≈",
  "coolant lost: k barely changes": "caloporteur perdu : k change à peine",
  "critical at {#} m": "critique à {#} m",
  "critical size": "taille critique",
  "enriched U": "U enrichi",
  "escape capture": "échappent à la capture",
  "escape capture while slowing": "échappent à la capture pendant le ralentissement",
  "f": "f",
  "fast fission": "fission rapide",
  "fast fission counted in η": "fission rapide comptée dans η",
  "fission": "fission",
  "fuel": "combustible",
  "fuel heats up: k ↓ (Doppler)": "le combustible chauffe : k ↓ (Doppler)",
  "fuel hotter: k ↓": "combustible plus chaud : k ↓",
  "graphite moderator": "modérateur : graphite",
  "graphite moderator · CO₂ / helium gas coolant": "modérateur : graphite · caloporteur : gaz CO₂ / hélium",
  "graphite moderator · heavy water coolant": "modérateur : graphite · caloporteur : eau lourde",
  "graphite moderator · lead coolant": "modérateur : graphite · caloporteur : plomb",
  "graphite moderator · molten salt coolant": "modérateur : graphite · caloporteur : sel fondu",
  "graphite moderator · sodium coolant": "modérateur : graphite · caloporteur : sodium",
  "graphite moderator · water coolant": "modérateur : graphite · caloporteur : eau",
  "heavy water coolant": "caloporteur : eau lourde",
  "heavy water moderates": "l'eau lourde modère",
  "heavy water moderator": "modérateur : eau lourde",
  "heavy water moderator · CO₂ / helium gas coolant": "modérateur : eau lourde · caloporteur : gaz CO₂ / hélium",
  "heavy water moderator · heavy water coolant": "modérateur : eau lourde · caloporteur : eau lourde",
  "heavy water moderator · lead coolant": "modérateur : eau lourde · caloporteur : plomb",
  "heavy water moderator · molten salt coolant": "modérateur : eau lourde · caloporteur : sel fondu",
  "heavy water moderator · sodium coolant": "modérateur : eau lourde · caloporteur : sodium",
  "heavy water moderator · water coolant": "modérateur : eau lourde · caloporteur : eau",
  "k": "k",
  "k∞": "k∞",
  "lead coolant": "caloporteur : plomb",
  "leak": "fuite",
  "leak out": "s'échappent",
  "light water moderator": "modérateur : eau légère",
  "light water moderator · CO₂ / helium gas coolant": "modérateur : eau légère · caloporteur : gaz CO₂ / hélium",
  "light water moderator · heavy water coolant": "modérateur : eau légère · caloporteur : eau lourde",
  "light water moderator · lead coolant": "modérateur : eau légère · caloporteur : plomb",
  "light water moderator · molten salt coolant": "modérateur : eau légère · caloporteur : sel fondu",
  "light water moderator · sodium coolant": "modérateur : eau légère · caloporteur : sodium",
  "light water moderator · water coolant": "modérateur : eau légère · caloporteur : eau",
  "mod./cool.": "mod./calo.",
  "moderator, coolant": "modérateur, caloporteur",
  "molten salt coolant": "caloporteur : sel fondu",
  "MOX {#} % Pu": "MOX {#} % Pu",
  "MOX, {#} % plutonium{#}": "MOX, {#} % de plutonium{#}",
  "natural U": "U naturel",
  "natural uranium ({#} % U{#})": "uranium naturel ({#} % U{#})",
  "neutrons per absorption in fuel": "neutrons par absorption dans le combustible",
  "never critical": "jamais critique",
  "no chain, any size": "pas de chaîne, quelle que soit la taille",
  "no leakage": "sans fuites",
  "no moderator, but the heavy water moderates": "pas de modérateur, mais l'eau lourde modère",
  "no moderator, but the heavy water moderates · heavy water coolant": "pas de modérateur, mais l'eau lourde modère · caloporteur : eau lourde",
  "no moderator, but the water moderates": "pas de modérateur, mais l'eau modère",
  "no moderator, but the water moderates · water coolant": "pas de modérateur, mais l'eau modère · caloporteur : eau",
  "no moderator: a fast reactor": "pas de modérateur : un réacteur rapide",
  "no moderator: a fast reactor · CO₂ / helium gas coolant": "pas de modérateur : un réacteur rapide · caloporteur : gaz CO₂ / hélium",
  "no moderator: a fast reactor · heavy water coolant": "pas de modérateur : un réacteur rapide · caloporteur : eau lourde",
  "no moderator: a fast reactor · lead coolant": "pas de modérateur : un réacteur rapide · caloporteur : plomb",
  "no moderator: a fast reactor · molten salt coolant": "pas de modérateur : un réacteur rapide · caloporteur : sel fondu",
  "no moderator: a fast reactor · sodium coolant": "pas de modérateur : un réacteur rapide · caloporteur : sodium",
  "no moderator: a fast reactor · water coolant": "pas de modérateur : un réacteur rapide · caloporteur : eau",
  "no moderator: fast": "pas de modérateur : rapide",
  "no size is big enough": "aucune taille ne suffit",
  "no slowing down, no resonance loss": "pas de ralentissement, pas de pertes par résonance",
  "p": "p",
  "per fuel absorption": "par absorption dans le combustible",
  "R {#} m": "R {#} m",
  "radius {#} m": "rayon {#} m",
  "radius {#} m · drag the edge": "rayon {#} m · faites glisser le bord",
  "share absorbed in fuel": "part absorbée dans le combustible",
  "simplified model": "modèle simplifié",
  "simplified one-group model · illustration": "modèle simplifié à un groupe · illustration",
  "sodium coolant": "caloporteur : sodium",
  "stays in": "restent",
  "stays in (M² {#} cm²)": "restent (M² {#} cm²)",
  "stays in: {#} / ({#} + M²B²), M² = {#} cm²": "restent : {#} / ({#} + M²B²), M² = {#} cm²",
  "sustains a chain, {#} % to spare (ρ)": "entretient une chaîne, {#} % de marge (ρ)",
  "sustains: +{#} % spare": "entretient : +{#} % de marge",
  "thorium + U{#}": "thorium + U{#}",
  "thorium, {#} % U{#}": "thorium, {#} % U{#}",
  "too small: critical at radius {#} m": "trop petit : critique à un rayon de {#} m",
  "too small: needs {#} m": "trop petit : il faut {#} m",
  "uranium, {#} % U{#}": "uranium, {#} % U{#}",
  "uranium, {#} % U{#} (highly enriched)": "uranium, {#} % U{#} (hautement enrichi)",
  "water boils: k ↑": "l'eau bout : k ↑",
  "water boils: k ↓": "l'eau bout : k ↓",
  "water boils: k ≈": "l'eau bout : k ≈",
  "water coolant": "caloporteur : eau",
  "water heats or boils: k ↑": "l'eau chauffe ou bout : k ↑",
  "water heats or boils: k ↑ (big sodium cores: spectrum hardens)": "l'eau chauffe ou bout : k ↑ (grands cœurs sodium : le spectre durcit)",
  "water heats or boils: k ↑ (small; positive in CANDU)": "l'eau chauffe ou bout : k ↑ (faible ; positif dans les CANDU)",
  "water heats or boils: k ↑ (smaller than with sodium)": "l'eau chauffe ou bout : k ↑ (plus faible qu'avec le sodium)",
  "water heats or boils: k ↓": "l'eau chauffe ou bout : k ↓",
  "water heats or boils: k ≈": "l'eau chauffe ou bout : k ≈",
  "water heats or boils: k barely changes": "l'eau chauffe ou bout : k change à peine",
  "water moderates": "l'eau modère",
  "where the neutrons go": "où vont les neutrons",
});
