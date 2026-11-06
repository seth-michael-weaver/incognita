/* Spanish: feedback (Estabilidad del reactor y realimentación) */
WT.L.ch.feedback = {
  num: "Lección 1", title: "Estabilidad del reactor y realimentación", short: "Realimentación",
  html: `
<div class="step">
  <h3>Un lazo: potencia, calor, reactividad</h3>
  <p>Más potencia calienta el combustible y el agua, y sus temperaturas cambian la reactividad <i>ρ</i>, que fija la potencia. Añade un escalón de reactividad y mira cómo la señal recorre el lazo. Con coeficientes negativos, el lazo se opone al cambio.</p>
  <div class="ctl"><label for="fb-r">Escalón de reactividad (pcm)</label><input id="fb-r" type="range" data-bind="rs" data-instant min="50" max="300" step="10" value="200"><output data-show="rs" data-fmt="0"></output></div>
  <div class="btns"><button class="btn" data-act="fbIns">Insertar</button> <button class="btn ghost" data-act="fbRes">Reiniciar</button></div>
</div>
<div class="step">
  <h3>Doppler: el freno rápido</h3>
  <p>Un combustible más caliente captura más neutrones en el uranio-238 sin fisión (<a href="#doppler">ensanchamiento Doppler</a>). El combustible se calienta en segundos, así que este freno actúa primero, y en los reactores de agua siempre es negativo. Aquí es la única realimentación.</p>
  <div class="ctl"><label for="fb-d">Coeficiente Doppler (pcm/K)</label><input id="fb-d" type="range" data-bind="aD" data-instant min="-5" max="-1" step="0.1" value="-2.5"><output data-show="aD" data-fmt="1"></output></div>
  <div class="btns"><button class="btn" data-act="fbIns">Insertar</button> <button class="btn ghost" data-act="fbRes">Reiniciar</button></div>
</div>
<div class="step">
  <h3>Entra el moderador</h3>
  <p>El agua más caliente es menos densa, así que frena peor los neutrones. En un reactor de agua a presión con niveles normales de boro, esto hace que el coeficiente del moderador también sea negativo: un segundo freno, más lento, y la potencia se estabiliza más abajo.</p>
  <div class="ctl"><label for="fb-m">Coeficiente del moderador (pcm/K)</label><input id="fb-m" type="range" data-bind="aM" data-instant min="-60" max="0" step="1" value="-30"><output data-show="aM" data-fmt="0"></output></div>
  <div class="btns"><button class="btn" data-act="fbIns">Insertar</button> <button class="btn ghost" data-act="fbRes">Reiniciar</button></div>
</div>
<div class="step">
  <h3>Cuando la realimentación es positiva</h3>
  <p>Si el término del refrigerante es positivo y pesa más que el Doppler, más potencia significa más reactividad y la potencia se dispara. Los reactores de agua se diseñan con coeficientes negativos; algunos diseños, como el RBMK a baja potencia, podían tener un coeficiente de huecos positivo.</p>
  <div class="ctl"><label for="fb-c">Coeficiente del refrigerante (pcm/K)</label><input id="fb-c" type="range" data-bind="aM" data-instant min="-60" max="150" step="5" value="150"><output data-show="aM" data-fmt="0"></output></div>
  <div class="btns"><button class="btn" data-act="fbIns">Insertar</button> <button class="btn ghost" data-act="fbRes">Reiniciar</button></div>
</div>`,
};

Object.assign(WT.L.labels, {
  // the loop
  "heat": "calor",
  "heats water": "calienta el agua",
  "chain": "cadena",
  "chain reaction": "reacción en cadena",
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
  "water +{#} K": "agua +{#} K",
  "water {#} K": "agua {#} K",
  "water ΔT +{#} K": "agua ΔT +{#} K",
  "water ΔT {#} K": "agua ΔT {#} K",
  "ρ +{#} pcm": "ρ +{#} pcm",
  "ρ {#} pcm": "ρ {#} pcm",
  // formulas and coefficients
  "ρ = ρext + αD ΔTf + αM ΔTm": "ρ = ρext + αD ΔTf + αM ΔTm",
  "C dT/dt = P − h (T − Tc)": "C dT/dt = P − h (T − Tc)",
  "Doppler α_D = {a} pcm/K": "Doppler α_D = {a} pcm/K",
  "moderator α_M = {a} pcm/K": "moderador α_M = {a} pcm/K",
  "coolant α_C = {a} pcm/K": "refrigerante α_C = {a} pcm/K",
  "inserted ρ_ext = {a}": "insertada ρ_ext = {a}",
  // power trace
  "+{a} pcm": "+{a} pcm",
  "power": "potencia",
  "last {#} s →": "últimos {#} s →",
  "last {#} seconds →": "últimos {#} segundos →",
  // verdict
  "power ran away · protection would shut it down": "la potencia se disparó · la protección pararía el reactor",
  "power ran away · in a real plant the protection system would shut it down": "la potencia se disparó · en una central real el sistema de protección pararía el reactor",
  "steady at {#} % · press Insert": "estable al {#} % · pulsa Insertar",
  "steady at {#} % power · press Insert to add reactivity": "estable al {#} % de potencia · pulsa Insertar para añadir reactividad",
  "power coefficient {a} pcm per {#} %: settles": "coeficiente de potencia {a} pcm por {#} %: se estabiliza",
  "power coefficient {a} pcm per {#} % power: self-stabilising": "coeficiente de potencia {a} pcm por {#} % de potencia: autoestabilizante",
  "power coefficient +{a} pcm per {#} %: runs away": "coeficiente de potencia +{a} pcm por {#} %: se dispara",
  "power coefficient +{a} pcm per {#} % power: runs away": "coeficiente de potencia +{a} pcm por {#} % de potencia: se dispara",
  "illustrative model": "modelo ilustrativo",
});
