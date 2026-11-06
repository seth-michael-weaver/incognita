/* Portuguese (pt-PT): feedback (Estabilidade do reator e realimentação) */
WT.L.ch.feedback = {
  num: "Lição 1", title: "Estabilidade do reator e realimentação", short: "Realimentação",
  html: `
<div class="step">
  <h3>Um ciclo: potência, calor, reatividade</h3>
  <p>Mais potência aquece o combustível e a água, e as suas temperaturas alteram a reatividade <i>ρ</i>, que define a potência. Acrescenta um degrau de reatividade e vê o sinal percorrer o ciclo. Com coeficientes negativos, o ciclo contraria-o.</p>
  <div class="ctl"><label for="fb-r">Degrau de reatividade (pcm)</label><input id="fb-r" type="range" data-bind="rs" data-instant min="50" max="300" step="10" value="200"><output data-show="rs" data-fmt="0"></output></div>
  <div class="btns"><button class="btn" data-act="fbIns">Inserir</button> <button class="btn ghost" data-act="fbRes">Repor</button></div>
</div>
<div class="step">
  <h3>Doppler: o travão rápido</h3>
  <p>Um combustível mais quente captura mais neutrões no urânio-238 sem fissão (<a href="#doppler">alargamento de Doppler</a>). O combustível aquece em segundos, por isso este travão atua primeiro, e nos reatores de água é sempre negativo. Aqui é a única realimentação.</p>
  <div class="ctl"><label for="fb-d">Coeficiente Doppler (pcm/K)</label><input id="fb-d" type="range" data-bind="aD" data-instant min="-5" max="-1" step="0.1" value="-2.5"><output data-show="aD" data-fmt="1"></output></div>
  <div class="btns"><button class="btn" data-act="fbIns">Inserir</button> <button class="btn ghost" data-act="fbRes">Repor</button></div>
</div>
<div class="step">
  <h3>O moderador entra em jogo</h3>
  <p>A água mais quente é menos densa, e por isso abranda pior os neutrões. Num reator de água pressurizada com concentrações normais de boro, isto torna também negativo o coeficiente do moderador: um segundo travão, mais lento, e a potência estabiliza mais abaixo.</p>
  <div class="ctl"><label for="fb-m">Coeficiente do moderador (pcm/K)</label><input id="fb-m" type="range" data-bind="aM" data-instant min="-60" max="0" step="1" value="-30"><output data-show="aM" data-fmt="0"></output></div>
  <div class="btns"><button class="btn" data-act="fbIns">Inserir</button> <button class="btn ghost" data-act="fbRes">Repor</button></div>
</div>
<div class="step">
  <h3>Quando a realimentação é positiva</h3>
  <p>Se o termo do refrigerante for positivo e pesar mais do que o Doppler, mais potência significa mais reatividade e a potência dispara. Os reatores de água são projetados com coeficientes negativos; alguns projetos, como o RBMK a baixa potência, podiam ter um coeficiente de vazio positivo.</p>
  <div class="ctl"><label for="fb-c">Coeficiente do refrigerante (pcm/K)</label><input id="fb-c" type="range" data-bind="aM" data-instant min="-60" max="150" step="5" value="150"><output data-show="aM" data-fmt="0"></output></div>
  <div class="btns"><button class="btn" data-act="fbIns">Inserir</button> <button class="btn ghost" data-act="fbRes">Repor</button></div>
</div>`,
};

Object.assign(WT.L.labels, {
  // the loop
  "heat": "calor",
  "heats water": "aquece a água",
  "chain": "cadeia",
  "chain reaction": "reação em cadeia",
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
  "fuel ΔT +{#} K": "combustível ΔT +{#} K",
  "fuel ΔT {#} K": "combustível ΔT {#} K",
  "water +{#} K": "água +{#} K",
  "water {#} K": "água {#} K",
  "water ΔT +{#} K": "água ΔT +{#} K",
  "water ΔT {#} K": "água ΔT {#} K",
  "ρ +{#} pcm": "ρ +{#} pcm",
  "ρ {#} pcm": "ρ {#} pcm",
  // formulas and coefficients
  "ρ = ρext + αD ΔTf + αM ΔTm": "ρ = ρext + αD ΔTf + αM ΔTm",
  "C dT/dt = P − h (T − Tc)": "C dT/dt = P − h (T − Tc)",
  "Doppler α_D = {a} pcm/K": "Doppler α_D = {a} pcm/K",
  "moderator α_M = {a} pcm/K": "moderador α_M = {a} pcm/K",
  "coolant α_C = {a} pcm/K": "refrigerante α_C = {a} pcm/K",
  "inserted ρ_ext = {a}": "inserida ρ_ext = {a}",
  // power trace
  "+{a} pcm": "+{a} pcm",
  "power": "potência",
  "last {#} s →": "últimos {#} s →",
  "last {#} seconds →": "últimos {#} segundos →",
  // verdict
  "power ran away · protection would shut it down": "a potência disparou · a proteção desligaria o reator",
  "power ran away · in a real plant the protection system would shut it down": "a potência disparou · numa central real, o sistema de proteção desligaria o reator",
  "steady at {#} % · press Insert": "estável a {#} % · carrega em Inserir",
  "steady at {#} % power · press Insert to add reactivity": "estável a {#} % da potência · carrega em Inserir para acrescentar reatividade",
  "power coefficient {a} pcm per {#} %: settles": "coeficiente de potência {a} pcm por {#} %: estabiliza",
  "power coefficient {a} pcm per {#} % power: self-stabilising": "coeficiente de potência {a} pcm por {#} % da potência: autoestabilizante",
  "power coefficient +{a} pcm per {#} %: runs away": "coeficiente de potência +{a} pcm por {#} %: dispara",
  "power coefficient +{a} pcm per {#} % power: runs away": "coeficiente de potência +{a} pcm por {#} % da potência: dispara",
  "illustrative model": "modelo ilustrativo",
});
