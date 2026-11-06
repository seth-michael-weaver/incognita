/* Dutch (Nederlands): sandbox (Bouw een reactor) */
WT.L.ch.sandbox = {
  num: "Les 1", title: "Bouw een reactor", short: "Bouw een reactor",
  lead: "Kies een brandstof, een moderator, een koelmiddel en een grootte, en kijk of een kettingreactie zichzelf in stand kan houden. Een vereenvoudigd leerboekmodel.",
  html: `
<div class="step">
  <h3>Vier factoren</h3>
  <p>Als er geen neutronen weglekten, zou elk geabsorbeerd neutron tot <i>k</i><sub>∞</sub> = <i>η f p ε</i> nieuwe leiden; deze grafietstapel met natuurlijk uranium haalt het net.</p>
</div>
<div class="step">
  <h3>Kies een moderator</h3>
  <p>Met natuurlijk uranium brengt alleen zwaar water of grafiet <i>k</i><sub>∞</sub> boven 1: licht water remt neutronen goed af maar absorbeert er te veel.</p>
  <div class="btns" role="group" aria-label="Moderator"><button class="btn ghost" data-act="mo_h2o">Licht water</button> <button class="btn ghost" data-act="mo_d2o">Zwaar water</button> <button class="btn ghost" data-act="mo_c">Grafiet</button></div>
  <div class="ctl"><label for="sb-m1">Moderator per brandstof</label><input id="sb-m1" type="range" data-bind="lm" min="-0.5" max="2.3" step="0.01" value="0.3"><output class="sb-m"></output></div>
</div>
<div class="step">
  <h3>Verrijk de brandstof</h3>
  <p>Een paar procent uranium-235 maakt gewoon water bruikbaar, daarom gebruiken de meeste reactoren het vandaag.</p>
  <div class="btns" role="group" aria-label="Brandstof"><button class="btn ghost" data-act="fu_nat">Natuurlijk U</button> <button class="btn ghost" data-act="fu_leu">Verrijkt U</button> <button class="btn ghost" data-act="fu_mox">MOX (Pu)</button> <button class="btn ghost" data-act="fu_th">Thorium + U-233</button></div>
  <div class="ctl"><label for="sb-e1">Splijtbaar aandeel (%)</label><input id="sb-e1" type="range" data-bind="enr" min="0.7" max="30" step="0.1" value="3"><output data-show="enr" data-fmt="1"></output></div>
</div>
<div class="step">
  <h3>Grootte en lekkage</h3>
  <p>Neutronen ontsnappen door het oppervlak, dus <i>k</i> = <i>k</i><sub>∞</sub> / (1 + <i>M</i>²<i>B</i>²). Sleep de rand van deze grafietstapel met natuurlijk uranium naar de gestippelde ring.</p>
  <div class="ctl"><label for="sb-r1">Kernstraal (m)</label><input id="sb-r1" type="range" data-bind="R" min="0.2" max="6" step="0.05" value="2"><output data-show="R" data-fmt="2"></output></div>
</div>
<div class="step">
  <h3>Als het koelmiddel kookt</h3>
  <p>In een grafietkern die met water wordt gekoeld, verhoogt koken <i>k</i>, omdat het water meer absorbeerde dan het afremde: de fout van de RBMK in Tsjernobyl. Probeer andere koelmiddelen.</p>
  <div class="btns" role="group" aria-label="Koelmiddel"><button class="btn ghost" data-act="co_h2o">Water</button> <button class="btn ghost" data-act="co_gas">CO₂ / helium</button> <button class="btn ghost" data-act="co_na">Natrium</button></div>
</div>
<div class="step">
  <h3>Bouw je eigen reactor</h3>
  <p>Alles mag. Een snelle reactor heeft geen moderator en heeft veel meer splijtbare brandstof nodig.</p>
  <div class="btns" role="group" aria-label="Brandstof"><button class="btn ghost" data-act="fu_nat">Natuurlijk U</button> <button class="btn ghost" data-act="fu_leu">Verrijkt U</button> <button class="btn ghost" data-act="fu_mox">MOX (Pu)</button> <button class="btn ghost" data-act="fu_th">Thorium + U-233</button></div>
  <div class="ctl"><label for="sb-e2">Splijtbaar aandeel (%)</label><input id="sb-e2" type="range" data-bind="enr" min="0.7" max="30" step="0.1" value="3"><output data-show="enr" data-fmt="1"></output></div>
  <div class="btns" role="group" aria-label="Moderator"><button class="btn ghost" data-act="mo_none">Geen moderator</button> <button class="btn ghost" data-act="mo_h2o">Licht water</button> <button class="btn ghost" data-act="mo_d2o">Zwaar water</button> <button class="btn ghost" data-act="mo_c">Grafiet</button></div>
  <div class="ctl"><label for="sb-m2">Moderator per brandstof</label><input id="sb-m2" type="range" data-bind="lm" min="-0.5" max="2.3" step="0.01" value="0.3"><output class="sb-m"></output></div>
  <div class="btns" role="group" aria-label="Koelmiddel"><button class="btn ghost" data-act="co_h2o">Water</button> <button class="btn ghost" data-act="co_d2o">Zwaar water</button> <button class="btn ghost" data-act="co_gas">CO₂ / helium</button> <button class="btn ghost" data-act="co_na">Natrium</button> <button class="btn ghost" data-act="co_pb">Lood</button> <button class="btn ghost" data-act="co_salt">Gesmolten zout</button></div>
  <div class="ctl"><label for="sb-r2">Kernstraal (m)</label><input id="sb-r2" type="range" data-bind="R" min="0.2" max="6" step="0.05" value="2"><output data-show="R" data-fmt="2"></output></div>
</div>`,
};

Object.assign(WT.L.labels, {
  "{#} % U{#}": "{#} % U{#}",
  "= η f p ε, if nothing leaked": "= η f p ε, zonder lekkage",
  "= η f, if nothing leaked": "= η f, zonder lekkage",
  "absorbed in fuel": "in brandstof geabsorbeerd",
  "bonus from fast fission": "bonus door snelle splijting",
  "can never sustain a chain, at any size": "kan nooit een keten in stand houden, bij geen enkele grootte",
  "caught by fuel": "door brandstof gevangen",
  "CO₂ / helium gas coolant": "koelmiddel: CO₂-/heliumgas",
  "coolant boils away: k ↑": "koelmiddel kookt weg: k ↑",
  "coolant boils away: k ↑ (big sodium cores: spectrum hardens)": "koelmiddel kookt weg: k ↑ (grote natriumkernen: spectrum wordt harder)",
  "coolant boils away: k ↑ (small; positive in CANDU)": "koelmiddel kookt weg: k ↑ (klein; positief in CANDU)",
  "coolant boils away: k ↑ (smaller than with sodium)": "koelmiddel kookt weg: k ↑ (kleiner dan met natrium)",
  "coolant boils away: k ↓": "koelmiddel kookt weg: k ↓",
  "coolant boils away: k ≈": "koelmiddel kookt weg: k ≈",
  "coolant boils away: k barely changes": "koelmiddel kookt weg: k verandert nauwelijks",
  "coolant boils: k ↑": "koelmiddel kookt: k ↑",
  "coolant boils: k ↓": "koelmiddel kookt: k ↓",
  "coolant boils: k ≈": "koelmiddel kookt: k ≈",
  "coolant heats: k ↑": "koelmiddel warmt op: k ↑",
  "coolant heats: k ↑ (big sodium cores: spectrum hardens)": "koelmiddel warmt op: k ↑ (grote natriumkernen: spectrum wordt harder)",
  "coolant heats: k ↑ (small; positive in CANDU)": "koelmiddel warmt op: k ↑ (klein; positief in CANDU)",
  "coolant heats: k ↑ (smaller than with sodium)": "koelmiddel warmt op: k ↑ (kleiner dan met natrium)",
  "coolant heats: k ↓": "koelmiddel warmt op: k ↓",
  "coolant heats: k ≈": "koelmiddel warmt op: k ≈",
  "coolant heats: k barely changes": "koelmiddel warmt op: k verandert nauwelijks",
  "coolant lost: k ↑": "koelmiddel verloren: k ↑",
  "coolant lost: k ↑ (big sodium cores: spectrum hardens)": "koelmiddel verloren: k ↑ (grote natriumkernen: spectrum wordt harder)",
  "coolant lost: k ↑ (small; positive in CANDU)": "koelmiddel verloren: k ↑ (klein; positief in CANDU)",
  "coolant lost: k ↑ (smaller than with sodium)": "koelmiddel verloren: k ↑ (kleiner dan met natrium)",
  "coolant lost: k ↓": "koelmiddel verloren: k ↓",
  "coolant lost: k ≈": "koelmiddel verloren: k ≈",
  "coolant lost: k barely changes": "koelmiddel verloren: k verandert nauwelijks",
  "critical at {#} m": "kritisch bij {#} m",
  "critical size": "kritische grootte",
  "enriched U": "verrijkt U",
  "escape capture": "ontsnappen aan vangst",
  "escape capture while slowing": "ontsnappen aan vangst tijdens afremmen",
  "f": "f",
  "fast fission": "snelle splijting",
  "fast fission counted in η": "snelle splijting zit in η",
  "fission": "splijting",
  "fuel": "brandstof",
  "fuel heats up: k ↓ (Doppler)": "brandstof warmt op: k ↓ (Doppler)",
  "fuel hotter: k ↓": "brandstof heter: k ↓",
  "graphite moderator": "moderator: grafiet",
  "graphite moderator · CO₂ / helium gas coolant": "moderator: grafiet · koelmiddel: CO₂-/heliumgas",
  "graphite moderator · heavy water coolant": "moderator: grafiet · koelmiddel: zwaar water",
  "graphite moderator · lead coolant": "moderator: grafiet · koelmiddel: lood",
  "graphite moderator · molten salt coolant": "moderator: grafiet · koelmiddel: gesmolten zout",
  "graphite moderator · sodium coolant": "moderator: grafiet · koelmiddel: natrium",
  "graphite moderator · water coolant": "moderator: grafiet · koelmiddel: water",
  "heavy water coolant": "koelmiddel: zwaar water",
  "heavy water moderates": "zwaar water modereert",
  "heavy water moderator": "moderator: zwaar water",
  "heavy water moderator · CO₂ / helium gas coolant": "moderator: zwaar water · koelmiddel: CO₂-/heliumgas",
  "heavy water moderator · heavy water coolant": "moderator: zwaar water · koelmiddel: zwaar water",
  "heavy water moderator · lead coolant": "moderator: zwaar water · koelmiddel: lood",
  "heavy water moderator · molten salt coolant": "moderator: zwaar water · koelmiddel: gesmolten zout",
  "heavy water moderator · sodium coolant": "moderator: zwaar water · koelmiddel: natrium",
  "heavy water moderator · water coolant": "moderator: zwaar water · koelmiddel: water",
  "k": "k",
  "k∞": "k∞",
  "lead coolant": "koelmiddel: lood",
  "leak": "lek",
  "leak out": "weglekken",
  "light water moderator": "moderator: licht water",
  "light water moderator · CO₂ / helium gas coolant": "moderator: licht water · koelmiddel: CO₂-/heliumgas",
  "light water moderator · heavy water coolant": "moderator: licht water · koelmiddel: zwaar water",
  "light water moderator · lead coolant": "moderator: licht water · koelmiddel: lood",
  "light water moderator · molten salt coolant": "moderator: licht water · koelmiddel: gesmolten zout",
  "light water moderator · sodium coolant": "moderator: licht water · koelmiddel: natrium",
  "light water moderator · water coolant": "moderator: licht water · koelmiddel: water",
  "mod./cool.": "mod./koelm.",
  "moderator, coolant": "moderator, koelmiddel",
  "molten salt coolant": "koelmiddel: gesmolten zout",
  "MOX {#} % Pu": "MOX {#} % Pu",
  "MOX, {#} % plutonium{#}": "MOX, {#} % plutonium{#}",
  "natural U": "natuurlijk U",
  "natural uranium ({#} % U{#})": "natuurlijk uranium ({#} % U{#})",
  "neutrons per absorption in fuel": "neutronen per absorptie in brandstof",
  "never critical": "nooit kritisch",
  "no chain, any size": "geen keten, bij elke grootte",
  "no leakage": "geen lekkage",
  "no moderator, but the heavy water moderates": "geen moderator, maar het zwaar water modereert",
  "no moderator, but the heavy water moderates · heavy water coolant": "geen moderator, maar het zwaar water modereert · koelmiddel: zwaar water",
  "no moderator, but the water moderates": "geen moderator, maar het water modereert",
  "no moderator, but the water moderates · water coolant": "geen moderator, maar het water modereert · koelmiddel: water",
  "no moderator: a fast reactor": "geen moderator: een snelle reactor",
  "no moderator: a fast reactor · CO₂ / helium gas coolant": "geen moderator: een snelle reactor · koelmiddel: CO₂-/heliumgas",
  "no moderator: a fast reactor · heavy water coolant": "geen moderator: een snelle reactor · koelmiddel: zwaar water",
  "no moderator: a fast reactor · lead coolant": "geen moderator: een snelle reactor · koelmiddel: lood",
  "no moderator: a fast reactor · molten salt coolant": "geen moderator: een snelle reactor · koelmiddel: gesmolten zout",
  "no moderator: a fast reactor · sodium coolant": "geen moderator: een snelle reactor · koelmiddel: natrium",
  "no moderator: a fast reactor · water coolant": "geen moderator: een snelle reactor · koelmiddel: water",
  "no moderator: fast": "geen moderator: snel",
  "no size is big enough": "geen grootte is groot genoeg",
  "no slowing down, no resonance loss": "geen afremming, geen resonantieverlies",
  "p": "p",
  "per fuel absorption": "per absorptie in brandstof",
  "R {#} m": "R {#} m",
  "radius {#} m": "straal {#} m",
  "radius {#} m · drag the edge": "straal {#} m · sleep de rand",
  "share absorbed in fuel": "aandeel geabsorbeerd in brandstof",
  "simplified model": "vereenvoudigd model",
  "simplified one-group model · illustration": "vereenvoudigd één-groepsmodel · illustratie",
  "sodium coolant": "koelmiddel: natrium",
  "stays in": "blijft binnen",
  "stays in (M² {#} cm²)": "blijft binnen (M² {#} cm²)",
  "stays in: {#} / ({#} + M²B²), M² = {#} cm²": "blijft binnen: {#} / ({#} + M²B²), M² = {#} cm²",
  "sustains a chain, {#} % to spare (ρ)": "houdt een keten in stand, {#} % over (ρ)",
  "sustains: +{#} % spare": "houdt stand: +{#} % over",
  "thorium + U{#}": "thorium + U{#}",
  "thorium, {#} % U{#}": "thorium, {#} % U{#}",
  "too small: critical at radius {#} m": "te klein: kritisch bij straal {#} m",
  "too small: needs {#} m": "te klein: heeft {#} m nodig",
  "uranium, {#} % U{#}": "uranium, {#} % U{#}",
  "uranium, {#} % U{#} (highly enriched)": "uranium, {#} % U{#} (hoogverrijkt)",
  "water boils: k ↑": "water kookt: k ↑",
  "water boils: k ↓": "water kookt: k ↓",
  "water boils: k ≈": "water kookt: k ≈",
  "water coolant": "koelmiddel: water",
  "water heats or boils: k ↑": "water warmt op of kookt: k ↑",
  "water heats or boils: k ↑ (big sodium cores: spectrum hardens)": "water warmt op of kookt: k ↑ (grote natriumkernen: spectrum wordt harder)",
  "water heats or boils: k ↑ (small; positive in CANDU)": "water warmt op of kookt: k ↑ (klein; positief in CANDU)",
  "water heats or boils: k ↑ (smaller than with sodium)": "water warmt op of kookt: k ↑ (kleiner dan met natrium)",
  "water heats or boils: k ↓": "water warmt op of kookt: k ↓",
  "water heats or boils: k ≈": "water warmt op of kookt: k ≈",
  "water heats or boils: k barely changes": "water warmt op of kookt: k verandert nauwelijks",
  "water moderates": "water modereert",
  "where the neutrons go": "waar de neutronen heen gaan",
});
