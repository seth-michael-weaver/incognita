/* Italian (Italiano): sandbox (Costruisci un reattore) */
WT.L.ch.sandbox = {
  num: "Lezione 1", title: "Costruisci un reattore", short: "Costruisci un reattore",
  lead: "Scegli un combustibile, un moderatore, un refrigerante e una dimensione, e vedi se una reazione a catena riesce ad autosostenersi. Un modello da manuale semplificato.",
  html: `
<div class="step">
  <h3>Quattro fattori</h3>
  <p>Se nessun neutrone sfuggisse, ogni neutrone assorbito ne produrrebbe <i>k</i><sub>∞</sub> = <i>η f p ε</i> nuovi; questa pila di grafite e uranio naturale ce la fa per un soffio.</p>
</div>
<div class="step">
  <h3>Scegli un moderatore</h3>
  <p>Con l'uranio naturale, solo l'acqua pesante o la grafite portano <i>k</i><sub>∞</sub> sopra 1: l'acqua leggera rallenta bene i neutroni ma ne assorbe troppi.</p>
  <div class="btns" role="group" aria-label="Moderatore"><button class="btn ghost" data-act="mo_h2o">Acqua leggera</button> <button class="btn ghost" data-act="mo_d2o">Acqua pesante</button> <button class="btn ghost" data-act="mo_c">Grafite</button></div>
  <div class="ctl"><label for="sb-m1">Moderatore per combustibile</label><input id="sb-m1" type="range" data-bind="lm" min="-0.5" max="2.3" step="0.01" value="0.3"><output class="sb-m"></output></div>
</div>
<div class="step">
  <h3>Arricchisci il combustibile</h3>
  <p>Qualche per cento di uranio-235 rende utilizzabile l'acqua comune, ed è per questo che oggi la usa la maggior parte dei reattori.</p>
  <div class="btns" role="group" aria-label="Combustibile"><button class="btn ghost" data-act="fu_nat">U naturale</button> <button class="btn ghost" data-act="fu_leu">U arricchito</button> <button class="btn ghost" data-act="fu_mox">MOX (Pu)</button> <button class="btn ghost" data-act="fu_th">Torio + U-233</button></div>
  <div class="ctl"><label for="sb-e1">Frazione fissile (%)</label><input id="sb-e1" type="range" data-bind="enr" min="0.7" max="30" step="0.1" value="3"><output data-show="enr" data-fmt="1"></output></div>
</div>
<div class="step">
  <h3>Dimensione e fughe</h3>
  <p>I neutroni sfuggono dalla superficie, quindi <i>k</i> = <i>k</i><sub>∞</sub> / (1 + <i>M</i>²<i>B</i>²). Trascina il bordo di questa pila di grafite e uranio naturale fino all'anello tratteggiato.</p>
  <div class="ctl"><label for="sb-r1">Raggio del nocciolo (m)</label><input id="sb-r1" type="range" data-bind="R" min="0.2" max="6" step="0.05" value="2"><output data-show="R" data-fmt="2"></output></div>
</div>
<div class="step">
  <h3>Quando il refrigerante bolle</h3>
  <p>In un nocciolo di grafite raffreddato ad acqua, l'ebollizione fa salire <i>k</i>, perché l'acqua assorbiva più di quanto rallentasse: il difetto dell'RBMK a Chernobyl. Prova altri refrigeranti.</p>
  <div class="btns" role="group" aria-label="Refrigerante"><button class="btn ghost" data-act="co_h2o">Acqua</button> <button class="btn ghost" data-act="co_gas">CO₂ / elio</button> <button class="btn ghost" data-act="co_na">Sodio</button></div>
</div>
<div class="step">
  <h3>Costruisci il tuo</h3>
  <p>Tutto è permesso. Un reattore veloce non ha moderatore e richiede molto più combustibile fissile.</p>
  <div class="btns" role="group" aria-label="Combustibile"><button class="btn ghost" data-act="fu_nat">U naturale</button> <button class="btn ghost" data-act="fu_leu">U arricchito</button> <button class="btn ghost" data-act="fu_mox">MOX (Pu)</button> <button class="btn ghost" data-act="fu_th">Torio + U-233</button></div>
  <div class="ctl"><label for="sb-e2">Frazione fissile (%)</label><input id="sb-e2" type="range" data-bind="enr" min="0.7" max="30" step="0.1" value="3"><output data-show="enr" data-fmt="1"></output></div>
  <div class="btns" role="group" aria-label="Moderatore"><button class="btn ghost" data-act="mo_none">Nessun moderatore</button> <button class="btn ghost" data-act="mo_h2o">Acqua leggera</button> <button class="btn ghost" data-act="mo_d2o">Acqua pesante</button> <button class="btn ghost" data-act="mo_c">Grafite</button></div>
  <div class="ctl"><label for="sb-m2">Moderatore per combustibile</label><input id="sb-m2" type="range" data-bind="lm" min="-0.5" max="2.3" step="0.01" value="0.3"><output class="sb-m"></output></div>
  <div class="btns" role="group" aria-label="Refrigerante"><button class="btn ghost" data-act="co_h2o">Acqua</button> <button class="btn ghost" data-act="co_d2o">Acqua pesante</button> <button class="btn ghost" data-act="co_gas">CO₂ / elio</button> <button class="btn ghost" data-act="co_na">Sodio</button> <button class="btn ghost" data-act="co_pb">Piombo</button> <button class="btn ghost" data-act="co_salt">Sale fuso</button></div>
  <div class="ctl"><label for="sb-r2">Raggio del nocciolo (m)</label><input id="sb-r2" type="range" data-bind="R" min="0.2" max="6" step="0.05" value="2"><output data-show="R" data-fmt="2"></output></div>
</div>`,
};

Object.assign(WT.L.labels, {
  "{#} % U{#}": "{#} % U{#}",
  "= η f p ε, if nothing leaked": "= η f p ε, senza fughe",
  "= η f, if nothing leaked": "= η f, senza fughe",
  "absorbed in fuel": "assorbiti nel combustibile",
  "bonus from fast fission": "bonus dalla fissione veloce",
  "can never sustain a chain, at any size": "non può mai sostenere una catena, a nessuna dimensione",
  "caught by fuel": "catturati dal combustibile",
  "CO₂ / helium gas coolant": "refrigerante: gas CO₂ / elio",
  "coolant boils away: k ↑": "il refrigerante evapora: k ↑",
  "coolant boils away: k ↑ (big sodium cores: spectrum hardens)": "il refrigerante evapora: k ↑ (grandi noccioli al sodio: lo spettro si indurisce)",
  "coolant boils away: k ↑ (small; positive in CANDU)": "il refrigerante evapora: k ↑ (piccolo; positivo nei CANDU)",
  "coolant boils away: k ↑ (smaller than with sodium)": "il refrigerante evapora: k ↑ (minore che col sodio)",
  "coolant boils away: k ↓": "il refrigerante evapora: k ↓",
  "coolant boils away: k ≈": "il refrigerante evapora: k ≈",
  "coolant boils away: k barely changes": "il refrigerante evapora: k cambia appena",
  "coolant boils: k ↑": "il refrigerante bolle: k ↑",
  "coolant boils: k ↓": "il refrigerante bolle: k ↓",
  "coolant boils: k ≈": "il refrigerante bolle: k ≈",
  "coolant heats: k ↑": "il refrigerante si scalda: k ↑",
  "coolant heats: k ↑ (big sodium cores: spectrum hardens)": "il refrigerante si scalda: k ↑ (grandi noccioli al sodio: lo spettro si indurisce)",
  "coolant heats: k ↑ (small; positive in CANDU)": "il refrigerante si scalda: k ↑ (piccolo; positivo nei CANDU)",
  "coolant heats: k ↑ (smaller than with sodium)": "il refrigerante si scalda: k ↑ (minore che col sodio)",
  "coolant heats: k ↓": "il refrigerante si scalda: k ↓",
  "coolant heats: k ≈": "il refrigerante si scalda: k ≈",
  "coolant heats: k barely changes": "il refrigerante si scalda: k cambia appena",
  "coolant lost: k ↑": "refrigerante perso: k ↑",
  "coolant lost: k ↑ (big sodium cores: spectrum hardens)": "refrigerante perso: k ↑ (grandi noccioli al sodio: lo spettro si indurisce)",
  "coolant lost: k ↑ (small; positive in CANDU)": "refrigerante perso: k ↑ (piccolo; positivo nei CANDU)",
  "coolant lost: k ↑ (smaller than with sodium)": "refrigerante perso: k ↑ (minore che col sodio)",
  "coolant lost: k ↓": "refrigerante perso: k ↓",
  "coolant lost: k ≈": "refrigerante perso: k ≈",
  "coolant lost: k barely changes": "refrigerante perso: k cambia appena",
  "critical at {#} m": "critico a {#} m",
  "critical size": "dimensione critica",
  "enriched U": "U arricchito",
  "escape capture": "sfuggono alla cattura",
  "escape capture while slowing": "sfuggono alla cattura durante il rallentamento",
  "f": "f",
  "fast fission": "fissione veloce",
  "fast fission counted in η": "fissione veloce inclusa in η",
  "fission": "fissione",
  "fuel": "combustibile",
  "fuel heats up: k ↓ (Doppler)": "il combustibile si scalda: k ↓ (Doppler)",
  "fuel hotter: k ↓": "combustibile più caldo: k ↓",
  "graphite moderator": "moderatore: grafite",
  "graphite moderator · CO₂ / helium gas coolant": "moderatore: grafite · refrigerante: gas CO₂ / elio",
  "graphite moderator · heavy water coolant": "moderatore: grafite · refrigerante: acqua pesante",
  "graphite moderator · lead coolant": "moderatore: grafite · refrigerante: piombo",
  "graphite moderator · molten salt coolant": "moderatore: grafite · refrigerante: sale fuso",
  "graphite moderator · sodium coolant": "moderatore: grafite · refrigerante: sodio",
  "graphite moderator · water coolant": "moderatore: grafite · refrigerante: acqua",
  "heavy water coolant": "refrigerante: acqua pesante",
  "heavy water moderates": "l'acqua pesante modera",
  "heavy water moderator": "moderatore: acqua pesante",
  "heavy water moderator · CO₂ / helium gas coolant": "moderatore: acqua pesante · refrigerante: gas CO₂ / elio",
  "heavy water moderator · heavy water coolant": "moderatore: acqua pesante · refrigerante: acqua pesante",
  "heavy water moderator · lead coolant": "moderatore: acqua pesante · refrigerante: piombo",
  "heavy water moderator · molten salt coolant": "moderatore: acqua pesante · refrigerante: sale fuso",
  "heavy water moderator · sodium coolant": "moderatore: acqua pesante · refrigerante: sodio",
  "heavy water moderator · water coolant": "moderatore: acqua pesante · refrigerante: acqua",
  "k": "k",
  "k∞": "k∞",
  "lead coolant": "refrigerante: piombo",
  "leak": "fuga",
  "leak out": "sfuggono",
  "light water moderator": "moderatore: acqua leggera",
  "light water moderator · CO₂ / helium gas coolant": "moderatore: acqua leggera · refrigerante: gas CO₂ / elio",
  "light water moderator · heavy water coolant": "moderatore: acqua leggera · refrigerante: acqua pesante",
  "light water moderator · lead coolant": "moderatore: acqua leggera · refrigerante: piombo",
  "light water moderator · molten salt coolant": "moderatore: acqua leggera · refrigerante: sale fuso",
  "light water moderator · sodium coolant": "moderatore: acqua leggera · refrigerante: sodio",
  "light water moderator · water coolant": "moderatore: acqua leggera · refrigerante: acqua",
  "mod./cool.": "mod./refr.",
  "moderator, coolant": "moderatore, refrigerante",
  "molten salt coolant": "refrigerante: sale fuso",
  "MOX {#} % Pu": "MOX {#} % Pu",
  "MOX, {#} % plutonium{#}": "MOX, {#} % di plutonio{#}",
  "natural U": "U naturale",
  "natural uranium ({#} % U{#})": "uranio naturale ({#} % U{#})",
  "neutrons per absorption in fuel": "neutroni per assorbimento nel combustibile",
  "never critical": "mai critico",
  "no chain, any size": "nessuna catena, a qualsiasi dimensione",
  "no leakage": "senza fughe",
  "no moderator, but the heavy water moderates": "nessun moderatore, ma l'acqua pesante modera",
  "no moderator, but the heavy water moderates · heavy water coolant": "nessun moderatore, ma l'acqua pesante modera · refrigerante: acqua pesante",
  "no moderator, but the water moderates": "nessun moderatore, ma l'acqua modera",
  "no moderator, but the water moderates · water coolant": "nessun moderatore, ma l'acqua modera · refrigerante: acqua",
  "no moderator: a fast reactor": "nessun moderatore: un reattore veloce",
  "no moderator: a fast reactor · CO₂ / helium gas coolant": "nessun moderatore: un reattore veloce · refrigerante: gas CO₂ / elio",
  "no moderator: a fast reactor · heavy water coolant": "nessun moderatore: un reattore veloce · refrigerante: acqua pesante",
  "no moderator: a fast reactor · lead coolant": "nessun moderatore: un reattore veloce · refrigerante: piombo",
  "no moderator: a fast reactor · molten salt coolant": "nessun moderatore: un reattore veloce · refrigerante: sale fuso",
  "no moderator: a fast reactor · sodium coolant": "nessun moderatore: un reattore veloce · refrigerante: sodio",
  "no moderator: a fast reactor · water coolant": "nessun moderatore: un reattore veloce · refrigerante: acqua",
  "no moderator: fast": "nessun moderatore: veloce",
  "no size is big enough": "nessuna dimensione basta",
  "no slowing down, no resonance loss": "nessun rallentamento, nessuna perdita per risonanza",
  "p": "p",
  "per fuel absorption": "per assorbimento nel combustibile",
  "R {#} m": "R {#} m",
  "radius {#} m": "raggio {#} m",
  "radius {#} m · drag the edge": "raggio {#} m · trascina il bordo",
  "share absorbed in fuel": "frazione assorbita nel combustibile",
  "simplified model": "modello semplificato",
  "simplified one-group model · illustration": "modello semplificato a un gruppo · illustrazione",
  "sodium coolant": "refrigerante: sodio",
  "stays in": "restano",
  "stays in (M² {#} cm²)": "restano (M² {#} cm²)",
  "stays in: {#} / ({#} + M²B²), M² = {#} cm²": "restano: {#} / ({#} + M²B²), M² = {#} cm²",
  "sustains a chain, {#} % to spare (ρ)": "sostiene una catena, {#} % di margine (ρ)",
  "sustains: +{#} % spare": "sostiene: +{#} % di margine",
  "thorium + U{#}": "torio + U{#}",
  "thorium, {#} % U{#}": "torio, {#} % U{#}",
  "too small: critical at radius {#} m": "troppo piccolo: critico a un raggio di {#} m",
  "too small: needs {#} m": "troppo piccolo: servono {#} m",
  "uranium, {#} % U{#}": "uranio, {#} % U{#}",
  "uranium, {#} % U{#} (highly enriched)": "uranio, {#} % U{#} (altamente arricchito)",
  "water boils: k ↑": "l'acqua bolle: k ↑",
  "water boils: k ↓": "l'acqua bolle: k ↓",
  "water boils: k ≈": "l'acqua bolle: k ≈",
  "water coolant": "refrigerante: acqua",
  "water heats or boils: k ↑": "l'acqua si scalda o bolle: k ↑",
  "water heats or boils: k ↑ (big sodium cores: spectrum hardens)": "l'acqua si scalda o bolle: k ↑ (grandi noccioli al sodio: lo spettro si indurisce)",
  "water heats or boils: k ↑ (small; positive in CANDU)": "l'acqua si scalda o bolle: k ↑ (piccolo; positivo nei CANDU)",
  "water heats or boils: k ↑ (smaller than with sodium)": "l'acqua si scalda o bolle: k ↑ (minore che col sodio)",
  "water heats or boils: k ↓": "l'acqua si scalda o bolle: k ↓",
  "water heats or boils: k ≈": "l'acqua si scalda o bolle: k ≈",
  "water heats or boils: k barely changes": "l'acqua si scalda o bolle: k cambia appena",
  "water moderates": "l'acqua modera",
  "where the neutrons go": "dove vanno i neutroni",
});
