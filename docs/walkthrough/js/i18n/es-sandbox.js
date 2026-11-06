/* Spanish (Español): sandbox (Construye un reactor) */
WT.L.ch.sandbox = {
  num: "Lección 1", title: "Construye un reactor", short: "Construye un reactor",
  lead: "Elige un combustible, un moderador, un refrigerante y un tamaño, y comprueba si una reacción en cadena puede sostenerse por sí sola. Un modelo de libro de texto simplificado.",
  html: `
<div class="step">
  <h3>Cuatro factores</h3>
  <p>Si no escapara ningún neutrón, cada neutrón absorbido daría lugar a <i>k</i><sub>∞</sub> = <i>η f p ε</i> nuevos; esta pila de grafito con uranio natural lo consigue por poco.</p>
</div>
<div class="step">
  <h3>Elige un moderador</h3>
  <p>Con uranio natural, solo el agua pesada o el grafito llevan <i>k</i><sub>∞</sub> por encima de 1: el agua ligera frena bien los neutrones pero absorbe demasiados.</p>
  <div class="btns" role="group" aria-label="Moderador"><button class="btn ghost" data-act="mo_h2o">Agua ligera</button> <button class="btn ghost" data-act="mo_d2o">Agua pesada</button> <button class="btn ghost" data-act="mo_c">Grafito</button></div>
  <div class="ctl"><label for="sb-m1">Moderador por combustible</label><input id="sb-m1" type="range" data-bind="lm" min="-0.5" max="2.3" step="0.01" value="0.3"><output class="sb-m"></output></div>
</div>
<div class="step">
  <h3>Enriquece el combustible</h3>
  <p>Unos pocos por ciento de uranio-235 hacen que funcione el agua corriente, y por eso la usan hoy la mayoría de los reactores.</p>
  <div class="btns" role="group" aria-label="Combustible"><button class="btn ghost" data-act="fu_nat">U natural</button> <button class="btn ghost" data-act="fu_leu">U enriquecido</button> <button class="btn ghost" data-act="fu_mox">MOX (Pu)</button> <button class="btn ghost" data-act="fu_th">Torio + U-233</button></div>
  <div class="ctl"><label for="sb-e1">Fracción fisible (%)</label><input id="sb-e1" type="range" data-bind="enr" min="0.7" max="30" step="0.1" value="3"><output data-show="enr" data-fmt="1"></output></div>
</div>
<div class="step">
  <h3>Tamaño y fugas</h3>
  <p>Los neutrones escapan por la superficie, así que <i>k</i> = <i>k</i><sub>∞</sub> / (1 + <i>M</i>²<i>B</i>²). Arrastra el borde de esta pila de grafito con uranio natural hasta el anillo discontinuo.</p>
  <div class="ctl"><label for="sb-r1">Radio del núcleo (m)</label><input id="sb-r1" type="range" data-bind="R" min="0.2" max="6" step="0.05" value="2"><output data-show="R" data-fmt="2"></output></div>
</div>
<div class="step">
  <h3>Cuando hierve el refrigerante</h3>
  <p>En un núcleo de grafito refrigerado por agua, la ebullición sube <i>k</i>, porque el agua absorbía más de lo que frenaba: el fallo del RBMK en Chernóbil. Prueba otros refrigerantes.</p>
  <div class="btns" role="group" aria-label="Refrigerante"><button class="btn ghost" data-act="co_h2o">Agua</button> <button class="btn ghost" data-act="co_gas">CO₂ / helio</button> <button class="btn ghost" data-act="co_na">Sodio</button></div>
</div>
<div class="step">
  <h3>Construye el tuyo</h3>
  <p>Todo vale. Un reactor rápido no tiene moderador y necesita mucho más combustible fisible.</p>
  <div class="btns" role="group" aria-label="Combustible"><button class="btn ghost" data-act="fu_nat">U natural</button> <button class="btn ghost" data-act="fu_leu">U enriquecido</button> <button class="btn ghost" data-act="fu_mox">MOX (Pu)</button> <button class="btn ghost" data-act="fu_th">Torio + U-233</button></div>
  <div class="ctl"><label for="sb-e2">Fracción fisible (%)</label><input id="sb-e2" type="range" data-bind="enr" min="0.7" max="30" step="0.1" value="3"><output data-show="enr" data-fmt="1"></output></div>
  <div class="btns" role="group" aria-label="Moderador"><button class="btn ghost" data-act="mo_none">Sin moderador</button> <button class="btn ghost" data-act="mo_h2o">Agua ligera</button> <button class="btn ghost" data-act="mo_d2o">Agua pesada</button> <button class="btn ghost" data-act="mo_c">Grafito</button></div>
  <div class="ctl"><label for="sb-m2">Moderador por combustible</label><input id="sb-m2" type="range" data-bind="lm" min="-0.5" max="2.3" step="0.01" value="0.3"><output class="sb-m"></output></div>
  <div class="btns" role="group" aria-label="Refrigerante"><button class="btn ghost" data-act="co_h2o">Agua</button> <button class="btn ghost" data-act="co_d2o">Agua pesada</button> <button class="btn ghost" data-act="co_gas">CO₂ / helio</button> <button class="btn ghost" data-act="co_na">Sodio</button> <button class="btn ghost" data-act="co_pb">Plomo</button> <button class="btn ghost" data-act="co_salt">Sal fundida</button></div>
  <div class="ctl"><label for="sb-r2">Radio del núcleo (m)</label><input id="sb-r2" type="range" data-bind="R" min="0.2" max="6" step="0.05" value="2"><output data-show="R" data-fmt="2"></output></div>
</div>`,
};

Object.assign(WT.L.labels, {
  "{#} % U{#}": "{#} % U{#}",
  "= η f p ε, if nothing leaked": "= η f p ε, sin fugas",
  "= η f, if nothing leaked": "= η f, sin fugas",
  "absorbed in fuel": "absorbidos en el combustible",
  "bonus from fast fission": "extra por fisión rápida",
  "can never sustain a chain, at any size": "nunca puede sostener una cadena, sea cual sea el tamaño",
  "caught by fuel": "capturados por el combustible",
  "CO₂ / helium gas coolant": "refrigerante: gas CO₂ / helio",
  "coolant boils away: k ↑": "el refrigerante se evapora: k ↑",
  "coolant boils away: k ↑ (big sodium cores: spectrum hardens)": "el refrigerante se evapora: k ↑ (núcleos grandes de sodio: el espectro se endurece)",
  "coolant boils away: k ↑ (small; positive in CANDU)": "el refrigerante se evapora: k ↑ (pequeño; positivo en CANDU)",
  "coolant boils away: k ↑ (smaller than with sodium)": "el refrigerante se evapora: k ↑ (menor que con sodio)",
  "coolant boils away: k ↓": "el refrigerante se evapora: k ↓",
  "coolant boils away: k ≈": "el refrigerante se evapora: k ≈",
  "coolant boils away: k barely changes": "el refrigerante se evapora: k apenas cambia",
  "coolant boils: k ↑": "el refrigerante hierve: k ↑",
  "coolant boils: k ↓": "el refrigerante hierve: k ↓",
  "coolant boils: k ≈": "el refrigerante hierve: k ≈",
  "coolant heats: k ↑": "el refrigerante se calienta: k ↑",
  "coolant heats: k ↑ (big sodium cores: spectrum hardens)": "el refrigerante se calienta: k ↑ (núcleos grandes de sodio: el espectro se endurece)",
  "coolant heats: k ↑ (small; positive in CANDU)": "el refrigerante se calienta: k ↑ (pequeño; positivo en CANDU)",
  "coolant heats: k ↑ (smaller than with sodium)": "el refrigerante se calienta: k ↑ (menor que con sodio)",
  "coolant heats: k ↓": "el refrigerante se calienta: k ↓",
  "coolant heats: k ≈": "el refrigerante se calienta: k ≈",
  "coolant heats: k barely changes": "el refrigerante se calienta: k apenas cambia",
  "coolant lost: k ↑": "refrigerante perdido: k ↑",
  "coolant lost: k ↑ (big sodium cores: spectrum hardens)": "refrigerante perdido: k ↑ (núcleos grandes de sodio: el espectro se endurece)",
  "coolant lost: k ↑ (small; positive in CANDU)": "refrigerante perdido: k ↑ (pequeño; positivo en CANDU)",
  "coolant lost: k ↑ (smaller than with sodium)": "refrigerante perdido: k ↑ (menor que con sodio)",
  "coolant lost: k ↓": "refrigerante perdido: k ↓",
  "coolant lost: k ≈": "refrigerante perdido: k ≈",
  "coolant lost: k barely changes": "refrigerante perdido: k apenas cambia",
  "critical at {#} m": "crítico a {#} m",
  "critical size": "tamaño crítico",
  "enriched U": "U enriquecido",
  "escape capture": "escapan a la captura",
  "escape capture while slowing": "escapan a la captura al frenarse",
  "f": "f",
  "fast fission": "fisión rápida",
  "fast fission counted in η": "fisión rápida incluida en η",
  "fission": "fisión",
  "fuel": "combustible",
  "fuel heats up: k ↓ (Doppler)": "el combustible se calienta: k ↓ (Doppler)",
  "fuel hotter: k ↓": "combustible más caliente: k ↓",
  "graphite moderator": "moderador: grafito",
  "graphite moderator · CO₂ / helium gas coolant": "moderador: grafito · refrigerante: gas CO₂ / helio",
  "graphite moderator · heavy water coolant": "moderador: grafito · refrigerante: agua pesada",
  "graphite moderator · lead coolant": "moderador: grafito · refrigerante: plomo",
  "graphite moderator · molten salt coolant": "moderador: grafito · refrigerante: sal fundida",
  "graphite moderator · sodium coolant": "moderador: grafito · refrigerante: sodio",
  "graphite moderator · water coolant": "moderador: grafito · refrigerante: agua",
  "heavy water coolant": "refrigerante: agua pesada",
  "heavy water moderates": "el agua pesada modera",
  "heavy water moderator": "moderador: agua pesada",
  "heavy water moderator · CO₂ / helium gas coolant": "moderador: agua pesada · refrigerante: gas CO₂ / helio",
  "heavy water moderator · heavy water coolant": "moderador: agua pesada · refrigerante: agua pesada",
  "heavy water moderator · lead coolant": "moderador: agua pesada · refrigerante: plomo",
  "heavy water moderator · molten salt coolant": "moderador: agua pesada · refrigerante: sal fundida",
  "heavy water moderator · sodium coolant": "moderador: agua pesada · refrigerante: sodio",
  "heavy water moderator · water coolant": "moderador: agua pesada · refrigerante: agua",
  "k": "k",
  "k∞": "k∞",
  "lead coolant": "refrigerante: plomo",
  "leak": "fuga",
  "leak out": "se fugan",
  "light water moderator": "moderador: agua ligera",
  "light water moderator · CO₂ / helium gas coolant": "moderador: agua ligera · refrigerante: gas CO₂ / helio",
  "light water moderator · heavy water coolant": "moderador: agua ligera · refrigerante: agua pesada",
  "light water moderator · lead coolant": "moderador: agua ligera · refrigerante: plomo",
  "light water moderator · molten salt coolant": "moderador: agua ligera · refrigerante: sal fundida",
  "light water moderator · sodium coolant": "moderador: agua ligera · refrigerante: sodio",
  "light water moderator · water coolant": "moderador: agua ligera · refrigerante: agua",
  "mod./cool.": "mod./refr.",
  "moderator, coolant": "moderador, refrigerante",
  "molten salt coolant": "refrigerante: sal fundida",
  "MOX {#} % Pu": "MOX {#} % Pu",
  "MOX, {#} % plutonium{#}": "MOX, {#} % de plutonio{#}",
  "natural U": "U natural",
  "natural uranium ({#} % U{#})": "uranio natural ({#} % U{#})",
  "neutrons per absorption in fuel": "neutrones por absorción en el combustible",
  "never critical": "nunca crítico",
  "no chain, any size": "sin cadena, a cualquier tamaño",
  "no leakage": "sin fugas",
  "no moderator, but the heavy water moderates": "sin moderador, pero el agua pesada modera",
  "no moderator, but the heavy water moderates · heavy water coolant": "sin moderador, pero el agua pesada modera · refrigerante: agua pesada",
  "no moderator, but the water moderates": "sin moderador, pero el agua modera",
  "no moderator, but the water moderates · water coolant": "sin moderador, pero el agua modera · refrigerante: agua",
  "no moderator: a fast reactor": "sin moderador: un reactor rápido",
  "no moderator: a fast reactor · CO₂ / helium gas coolant": "sin moderador: un reactor rápido · refrigerante: gas CO₂ / helio",
  "no moderator: a fast reactor · heavy water coolant": "sin moderador: un reactor rápido · refrigerante: agua pesada",
  "no moderator: a fast reactor · lead coolant": "sin moderador: un reactor rápido · refrigerante: plomo",
  "no moderator: a fast reactor · molten salt coolant": "sin moderador: un reactor rápido · refrigerante: sal fundida",
  "no moderator: a fast reactor · sodium coolant": "sin moderador: un reactor rápido · refrigerante: sodio",
  "no moderator: a fast reactor · water coolant": "sin moderador: un reactor rápido · refrigerante: agua",
  "no moderator: fast": "sin moderador: rápido",
  "no size is big enough": "ningún tamaño basta",
  "no slowing down, no resonance loss": "sin moderación, sin pérdidas por resonancia",
  "p": "p",
  "per fuel absorption": "por absorción en el combustible",
  "R {#} m": "R {#} m",
  "radius {#} m": "radio {#} m",
  "radius {#} m · drag the edge": "radio {#} m · arrastra el borde",
  "share absorbed in fuel": "fracción absorbida en el combustible",
  "simplified model": "modelo simplificado",
  "simplified one-group model · illustration": "modelo simplificado a un grupo · ilustración",
  "sodium coolant": "refrigerante: sodio",
  "stays in": "se quedan",
  "stays in (M² {#} cm²)": "se quedan (M² {#} cm²)",
  "stays in: {#} / ({#} + M²B²), M² = {#} cm²": "se quedan: {#} / ({#} + M²B²), M² = {#} cm²",
  "sustains a chain, {#} % to spare (ρ)": "sostiene una cadena, {#} % de margen (ρ)",
  "sustains: +{#} % spare": "sostiene: +{#} % de margen",
  "thorium + U{#}": "torio + U{#}",
  "thorium, {#} % U{#}": "torio, {#} % U{#}",
  "too small: critical at radius {#} m": "demasiado pequeño: crítico con radio {#} m",
  "too small: needs {#} m": "demasiado pequeño: necesita {#} m",
  "uranium, {#} % U{#}": "uranio, {#} % U{#}",
  "uranium, {#} % U{#} (highly enriched)": "uranio, {#} % U{#} (altamente enriquecido)",
  "water boils: k ↑": "el agua hierve: k ↑",
  "water boils: k ↓": "el agua hierve: k ↓",
  "water boils: k ≈": "el agua hierve: k ≈",
  "water coolant": "refrigerante: agua",
  "water heats or boils: k ↑": "el agua se calienta o hierve: k ↑",
  "water heats or boils: k ↑ (big sodium cores: spectrum hardens)": "el agua se calienta o hierve: k ↑ (núcleos grandes de sodio: el espectro se endurece)",
  "water heats or boils: k ↑ (small; positive in CANDU)": "el agua se calienta o hierve: k ↑ (pequeño; positivo en CANDU)",
  "water heats or boils: k ↑ (smaller than with sodium)": "el agua se calienta o hierve: k ↑ (menor que con sodio)",
  "water heats or boils: k ↓": "el agua se calienta o hierve: k ↓",
  "water heats or boils: k ≈": "el agua se calienta o hierve: k ≈",
  "water heats or boils: k barely changes": "el agua se calienta o hierve: k apenas cambia",
  "water moderates": "el agua modera",
  "where the neutrons go": "adónde van los neutrones",
});
