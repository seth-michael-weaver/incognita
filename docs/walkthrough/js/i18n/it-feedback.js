/* Italian: feedback (Stabilità del reattore e retroazioni) */
WT.L.ch.feedback = {
  num: "Lezione 1", title: "Stabilità del reattore e retroazioni", short: "Retroazioni",
  html: `
<div class="step">
  <h3>Un anello: potenza, calore, reattività</h3>
  <p>Più potenza scalda il combustibile e l'acqua, e le loro temperature cambiano la reattività <i>ρ</i>, che determina la potenza. Aggiungi un gradino di reattività e guarda il segnale percorrere l'anello. Con coefficienti negativi, l'anello si oppone.</p>
  <div class="ctl"><label for="fb-r">Gradino di reattività (pcm)</label><input id="fb-r" type="range" data-bind="rs" data-instant min="50" max="300" step="10" value="200"><output data-show="rs" data-fmt="0"></output></div>
  <div class="btns"><button class="btn" data-act="fbIns">Inserisci</button> <button class="btn ghost" data-act="fbRes">Azzera</button></div>
</div>
<div class="step">
  <h3>Doppler: il freno rapido</h3>
  <p>Un combustibile più caldo cattura più neutroni nell'uranio-238 senza fissione (<a href="#doppler">allargamento Doppler</a>). Il combustibile si scalda in pochi secondi, quindi questo freno agisce per primo, e nei reattori ad acqua è sempre negativo. Qui è l'unica retroazione.</p>
  <div class="ctl"><label for="fb-d">Coefficiente Doppler (pcm/K)</label><input id="fb-d" type="range" data-bind="aD" data-instant min="-5" max="-1" step="0.1" value="-2.5"><output data-show="aD" data-fmt="1"></output></div>
  <div class="btns"><button class="btn" data-act="fbIns">Inserisci</button> <button class="btn ghost" data-act="fbRes">Azzera</button></div>
</div>
<div class="step">
  <h3>Entra in gioco il moderatore</h3>
  <p>L'acqua più calda è meno densa, quindi rallenta peggio i neutroni. In un reattore ad acqua pressurizzata, con le normali concentrazioni di boro, questo rende negativo anche il coefficiente del moderatore: un secondo freno, più lento, e la potenza si assesta più in basso.</p>
  <div class="ctl"><label for="fb-m">Coefficiente del moderatore (pcm/K)</label><input id="fb-m" type="range" data-bind="aM" data-instant min="-60" max="0" step="1" value="-30"><output data-show="aM" data-fmt="0"></output></div>
  <div class="btns"><button class="btn" data-act="fbIns">Inserisci</button> <button class="btn ghost" data-act="fbRes">Azzera</button></div>
</div>
<div class="step">
  <h3>Quando la retroazione è positiva</h3>
  <p>Se il termine del refrigerante è positivo e supera il Doppler, più potenza significa più reattività e la potenza va fuori controllo. I reattori ad acqua sono progettati con coefficienti negativi; alcuni progetti, come l'RBMK a bassa potenza, potevano avere un coefficiente di vuoto positivo.</p>
  <div class="ctl"><label for="fb-c">Coefficiente del refrigerante (pcm/K)</label><input id="fb-c" type="range" data-bind="aM" data-instant min="-60" max="150" step="5" value="150"><output data-show="aM" data-fmt="0"></output></div>
  <div class="btns"><button class="btn" data-act="fbIns">Inserisci</button> <button class="btn ghost" data-act="fbRes">Azzera</button></div>
</div>`,
};

Object.assign(WT.L.labels, {
  // the loop
  "heat": "calore",
  "heats water": "scalda l'acqua",
  "chain": "catena",
  "chain reaction": "reazione a catena",
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
  "fuel ΔT +{#} K": "combustibile ΔT +{#} K",
  "fuel ΔT {#} K": "combustibile ΔT {#} K",
  "water +{#} K": "acqua +{#} K",
  "water {#} K": "acqua {#} K",
  "water ΔT +{#} K": "acqua ΔT +{#} K",
  "water ΔT {#} K": "acqua ΔT {#} K",
  "ρ +{#} pcm": "ρ +{#} pcm",
  "ρ {#} pcm": "ρ {#} pcm",
  // formulas and coefficients
  "ρ = ρext + αD ΔTf + αM ΔTm": "ρ = ρext + αD ΔTf + αM ΔTm",
  "C dT/dt = P − h (T − Tc)": "C dT/dt = P − h (T − Tc)",
  "Doppler α_D = {a} pcm/K": "Doppler α_D = {a} pcm/K",
  "moderator α_M = {a} pcm/K": "moderatore α_M = {a} pcm/K",
  "coolant α_C = {a} pcm/K": "refrigerante α_C = {a} pcm/K",
  "inserted ρ_ext = {a}": "inserita ρ_ext = {a}",
  // power trace
  "+{a} pcm": "+{a} pcm",
  "power": "potenza",
  "last {#} s →": "ultimi {#} s →",
  "last {#} seconds →": "ultimi {#} secondi →",
  // verdict
  "power ran away · protection would shut it down": "potenza fuori controllo · la protezione spegnerebbe il reattore",
  "power ran away · in a real plant the protection system would shut it down": "potenza fuori controllo · in un impianto reale il sistema di protezione spegnerebbe il reattore",
  "steady at {#} % · press Insert": "stabile al {#} % · premi Inserisci",
  "steady at {#} % power · press Insert to add reactivity": "stabile al {#} % di potenza · premi Inserisci per aggiungere reattività",
  "power coefficient {a} pcm per {#} %: settles": "coefficiente di potenza {a} pcm per {#} %: si assesta",
  "power coefficient {a} pcm per {#} % power: self-stabilising": "coefficiente di potenza {a} pcm per {#} % di potenza: autostabilizzante",
  "power coefficient +{a} pcm per {#} %: runs away": "coefficiente di potenza +{a} pcm per {#} %: fuori controllo",
  "power coefficient +{a} pcm per {#} % power: runs away": "coefficiente di potenza +{a} pcm per {#} % di potenza: va fuori controllo",
  "illustrative model": "modello illustrativo",
});
