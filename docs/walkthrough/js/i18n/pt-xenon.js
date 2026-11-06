/* Portuguese (pt-PT): xenon (Lição 1, envenenamento por xénon) */
WT.L.ch.xenon = {
  num: "Lição 1", title: "Envenenamento por xénon", short: "Xénon",
  html: `
<div class="step">
  <h3>Um veneno feito pela fissão</h3>
  <p>Cerca de 6,6 % das fissões conduzem, através do iodo-135, ao xénon-135: o absorvente de neutrões mais forte que se conhece. Acumula-se durante uns dois dias, até que os neutrões o queimam e o decaimento o remove tão depressa quanto se forma. Uma potência mais alta também o queima mais depressa, por isso o nível satura.</p>
  <div class="ctl"><label for="xe-p1">Potência (%)</label><input id="xe-p1" type="range" data-bind="P" data-instant min="10" max="100" step="5" value="100"><output data-show="P" data-fmt="0"></output></div>
</div>
<div class="step">
  <h3>O poço de xénon</h3>
  <p>Ao parar o reator a queima acaba, mas o iodo já produzido continua a transformar-se em xénon. O veneno atinge o máximo cerca de nove horas depois, mais do que as barras conseguem compensar, e o reator não pode voltar a arrancar; desaparece ao fim de dois a três dias.</p>
  <div class="ctl"><label for="xe-th">Horas após a paragem</label><input id="xe-th" type="range" data-bind="th" data-instant min="0" max="72" step="0.5" value="9"><output data-show="th" data-fmt="1"></output></div>
</div>
<div class="step">
  <h3>Parar e rearrancar</h3>
  <p>Agora corre em tempo real, três horas por segundo. Para o reator e depois tenta rearrancá-lo: dentro do poço é recusado; mais tarde os neutrões queimam o xénon. Uma simples mudança de potência também faz oscilar o xénon durante horas.</p>
  <div class="ctl"><label for="xe-p3">Potência (%)</label><input id="xe-p3" type="range" data-bind="P" data-instant min="10" max="100" step="5" value="100"><output data-show="P" data-fmt="0"></output></div>
  <div class="btns"><button class="btn" data-act="xeshut">Parar</button><button class="btn ghost" data-act="xerestart">Rearrancar</button></div>
</div>
<div class="step">
  <h3>Oscilações de xénon</h3>
  <p>Num núcleo grande os dois lados estão apenas fracamente acoplados. Introduz barras num dos lados: com menos fluxo queima-se lá menos xénon, e a potência desloca-se para o outro lado e depois regressa, cerca de uma vez por dia. Em núcleos maiores a oscilação cresce, a menos que os operadores a amorteçam.</p>
  <div class="ctl"><label for="xe-wd">Tamanho do núcleo (m)</label><input id="xe-wd" type="range" data-bind="wd" data-instant min="1.5" max="3.5" step="0.1" value="3"><output data-show="wd" data-fmt="1"></output></div>
  <div class="btns"><button class="btn" data-act="xepush">Introduzir barras do lado esquerdo</button></div>
</div>`,
};
/* attributes referenced in the English chapter script (for the structure check): data-act="${act}" */

Object.assign(WT.L.labels, {
  "fission → iodine{#} ({#} h) → xenon{#} ({#} h) → Cs{#}": "fissão → iodo{#} ({#} h) → xénon{#} ({#} h) → Cs{#}",
  "xenon{#} + n → Xe{#}: {#} million barns": "xénon{#} + n → Xe{#}: {#} milhões de barns",
  "fission → iodine{#} ({#} h) → xenon{#} ({#} h) → Cs{#}  ·  Xe{#} swallows neutrons: {#} million barns": "fissão → iodo{#} ({#} h) → xénon{#} ({#} h) → Cs{#}  ·  o Xe{#} engole neutrões: {#} milhões de barns",
  "spare reactivity": "reserva de reatividade",
  "spare reactivity the rods can give": "reserva de reatividade das barras",
  "{#} h": "{#} h",
  "equilibrium {#} %": "equilíbrio {#} %",
  "xenon worth (% of k)": "efeito do xénon (% de k)",
  "{#} % power · {#} h after start-up · xenon {#} %": "potência {#} % · {#} h após o arranque · xénon {#} %",
  "no restart": "sem rearranque",
  "too poisoned to restart": "demasiado envenenado para rearrancar",
  "shutdown": "paragem",
  "drag": "arrastar",
  "peak {#} % at {#} h": "pico {#} % ao fim de {#} h",
  "{#} h after shutdown · xenon {#} % · restart possible": "{#} h após a paragem · xénon {#} % · rearranque possível",
  "{#} h after shutdown · xenon {#} % · cannot restart": "{#} h após a paragem · xénon {#} % · rearranque impossível",
  "shut down": "parado",
  "refused: more xenon than spare reactivity": "recusado: mais xénon do que reserva de reatividade",
  "restarted": "rearrancado",
  "tap the core to shut down": "toca no núcleo para o parar",
  "tap the core to restart": "toca no núcleo para rearrancar",
  "power": "potência",
  "running at {#} % · xenon {#} %": "a funcionar a {#} % · xénon {#} %",
  "shut down · in the pit · xenon {#} %": "parado · no poço · xénon {#} %",
  "shut down · restart possible · xenon {#} %": "parado · rearranque possível · xénon {#} %",
  "left {#} %": "esquerda {#} %",
  "right {#} %": "direita {#} %",
  "tap a side to push rods in": "toca num lado para introduzir barras",
  "more power left": "mais potência à esquerda",
  "more power right": "mais potência à direita",
  "swing period {#} h · {#} m core: the swing dies away": "período {#} h · núcleo de {#} m: a oscilação extingue-se",
  "swing period {#} h · {#} m core: the swing dies away slowly": "período {#} h · núcleo de {#} m: a oscilação extingue-se devagar",
  "swing period {#} h · {#} m core: the swing grows": "período {#} h · núcleo de {#} m: a oscilação cresce",
  "{#} m core: push the rods to start a swing": "núcleo de {#} m: introduz as barras para iniciar uma oscilação",
  "illustration": "ilustração",
});
