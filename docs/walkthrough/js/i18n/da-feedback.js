/* Danish: feedback (Reaktorstabilitet og tilbagekobling) */
WT.L.ch.feedback = {
  num: "Lektion 12", title: "Reaktorstabilitet og tilbagekobling", short: "Tilbagekobling",
  html: `
<div class="step">
  <h3>En sløjfe: effekt, varme, reaktivitet</h3>
  <p>Mere effekt opvarmer brændslet og vandet, og deres temperaturer ændrer reaktiviteten <i>ρ</i>, som bestemmer effekten. Tilfør et spring i reaktivitet, og se signalet løbe rundt i sløjfen. Med negative koefficienter skubber det tilbage.</p>
  <div class="ctl"><label for="fb-r">Reaktivitetsspring (pcm)</label><input id="fb-r" type="range" data-bind="rs" data-instant min="50" max="300" step="10" value="200"><output data-show="rs" data-fmt="0"></output></div>
  <div class="btns"><button class="btn" data-act="fbIns">Tilfør</button> <button class="btn ghost" data-act="fbRes">Nulstil</button></div>
</div>
<div class="step">
  <h3>Doppler: den hurtige bremse</h3>
  <p>Varmere brændsel fanger flere neutroner i uran-238 uden fission (<a href="#doppler">dopplerudvidelse</a>). Brændslet opvarmes på sekunder, så denne bremse virker først, og i vandreaktorer er den altid negativ. Her er den den eneste tilbagekobling.</p>
  <div class="ctl"><label for="fb-d">Dopplerkoefficient (pcm/K)</label><input id="fb-d" type="range" data-bind="aD" data-instant min="-5" max="-1" step="0.1" value="-2.5"><output data-show="aD" data-fmt="1"></output></div>
  <div class="btns"><button class="btn" data-act="fbIns">Tilfør</button> <button class="btn ghost" data-act="fbRes">Nulstil</button></div>
</div>
<div class="step">
  <h3>Moderatoren kommer med</h3>
  <p>Varmere vand er mindre tæt, så det bremser neutroner dårligere. I en trykvandsreaktor ved normale borkoncentrationer gør det også moderatorkoefficienten negativ: en anden, langsommere bremse, og effekten falder til ro på et lavere niveau.</p>
  <div class="ctl"><label for="fb-m">Moderatorkoefficient (pcm/K)</label><input id="fb-m" type="range" data-bind="aM" data-instant min="-60" max="0" step="1" value="-30"><output data-show="aM" data-fmt="0"></output></div>
  <div class="btns"><button class="btn" data-act="fbIns">Tilfør</button> <button class="btn ghost" data-act="fbRes">Nulstil</button></div>
</div>
<div class="step">
  <h3>Når tilbagekoblingen er positiv</h3>
  <p>Hvis kølemiddelleddet er positivt og vejer tungere end Doppler, betyder mere effekt mere reaktivitet, og effekten løber løbsk. Vandreaktorer konstrueres med negative koefficienter; nogle design, såsom RBMK ved lav effekt, kunne have en positiv dampblærekoefficient.</p>
  <div class="ctl"><label for="fb-c">Kølemiddelkoefficient (pcm/K)</label><input id="fb-c" type="range" data-bind="aM" data-instant min="-60" max="150" step="5" value="150"><output data-show="aM" data-fmt="0"></output></div>
  <div class="btns"><button class="btn" data-act="fbIns">Tilfør</button> <button class="btn ghost" data-act="fbRes">Nulstil</button></div>
</div>`,
};

Object.assign(WT.L.labels, {
  "+{a} pcm": "+{a} pcm",
  "C dT/dt = P − h (T − Tc)": "C dT/dt = P − h (T − Tc)",
  "Doppler α_D = {a} pcm/K": "Doppler α_D = {a} pcm/K",
  "P {#} %": "P {#} %",
  "chain": "kæde",
  "chain reaction": "kædereaktion",
  "coolant α_C = {a} pcm/K": "kølemiddel α_C = {a} pcm/K",
  "fuel +{#} K": "brændsel +{#} K",
  "fuel {#} K": "brændsel {#} K",
  "fuel ΔT +{#} K": "brændsel ΔT +{#} K",
  "fuel ΔT {#} K": "brændsel ΔT {#} K",
  "heat": "varme",
  "heats water": "opvarmer vand",
  "illustrative model": "illustrativ model",
  "inserted ρ_ext = {a}": "tilført ρ_ext = {a}",
  "last {#} s →": "seneste {#} s →",
  "last {#} seconds →": "seneste {#} sekunder →",
  "moderator α_M = {a} pcm/K": "moderator α_M = {a} pcm/K",
  "power": "effekt",
  "power coefficient +{a} pcm per 100 % power: runs away": "effektkoefficient +{a} pcm pr. 100 % effekt: løber løbsk",
  "power coefficient +{a} pcm per 100 %: runs away": "effektkoefficient +{a} pcm pr. 100 %: løber løbsk",
  "power coefficient {a} pcm per 100 % power: self-stabilising": "effektkoefficient {a} pcm pr. 100 % effekt: selvstabiliserende",
  "power coefficient {a} pcm per 100 %: settles": "effektkoefficient {a} pcm pr. 100 %: falder til ro",
  "power ran away · protection would shut it down": "effekten løb løbsk · sikringen ville lukke ned",
  "power ran away · in a real plant the protection system would shut it down": "effekten løb løbsk · på et rigtigt værk ville sikkerhedssystemet lukke ned",
  "steady at {#} % · press Insert": "stabil ved {#} % · tryk på Tilfør",
  "steady at {#} % power · press Insert to add reactivity": "stabil ved {#} % effekt · tryk på Tilfør for at tilføre reaktivitet",
  "water +{#} K": "vand +{#} K",
  "water {#} K": "vand {#} K",
  "water ΔT +{#} K": "vand ΔT +{#} K",
  "water ΔT {#} K": "vand ΔT {#} K",
  "αC +": "αC +",
  "αC −": "αC −",
  "αD −": "αD −",
  "αM {#}": "αM {#}",
  "αM −": "αM −",
  "ρ +{#} pcm": "ρ +{#} pcm",
  "ρ = ρext + αD ΔTf + αM ΔTm": "ρ = ρext + αD ΔTf + αM ΔTm",
  "ρ {#} pcm": "ρ {#} pcm",
});
