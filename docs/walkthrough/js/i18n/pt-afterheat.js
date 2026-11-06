/* Portuguese (pt-PT): afterheat (Calor depois da paragem) */
WT.L.ch.afterheat = {
  num: "Lição 1", title: "Calor depois da paragem", short: "Calor residual",
  html: `
<div class="step">
  <h3>A cadeia para</h3>
  <p>Quando as barras de controlo caem, a cisão dos átomos cessa em cerca de um minuto. Mas o combustível continua a brilhar: os fragmentos deixados pelas cisões anteriores são radioativos, e os seus decaimentos continuam a libertar calor.</p>
  <div class="btns"><button class="btn" data-act="ahDrop">Deixar cair as barras</button> <button class="btn ghost" data-act="ahUp">Reiniciar</button></div>
</div>
<div class="step">
  <h3>Diminui, devagar</h3>
  <p>Logo após a paragem, este calor é cerca de 6–7 % da plena potência. Ao fim de uma hora é cerca de 1 %, ao fim de um dia cerca de meio por cento, ao fim de uma semana um quarto. Frações pequenas, mas de um número muito grande.</p>
  <div class="ctl"><label for="ah-t">Tempo desde a paragem</label><input id="ah-t" type="range" data-bind="lt" data-instant min="0" max="7.5" step="0.01" value="3.56"></div>
</div>
<div class="step">
  <h3>Manter a água em movimento</h3>
  <p>Por isso o núcleo continua a ser arrefecido depois da paragem. As bombas fazem a água correr junto ao combustível e levam o calor. Desliga-as e a temperatura sobe, porque o calor não tem para onde ir.</p>
  <div class="btns"><button class="btn ghost" data-act="ahPump" aria-pressed="true">Bombas</button></div>
</div>
<div class="step">
  <h3>Arrefecer sem bombas</h3>
  <p>A água quente sobe e a água fria desce. Um circuito até uma piscina colocada acima do núcleo mantém a água em movimento sem bomba nenhuma. Vários projetos recentes contam com isto durante dias.</p>
  <div class="btns"><button class="btn ghost" data-act="ahPump" aria-pressed="false">Bombas</button> <button class="btn ghost" data-act="ahPass" aria-pressed="true">Circuito passivo</button></div>
</div>`,
};

Object.assign(WT.L.labels, {
  "illustration": "ilustração",
  // scene 1: the rods drop
  "splitting atoms": "cisões",
  "heat from splitting atoms": "calor das cisões",
  "decaying fragments": "decaimentos",
  "heat from decaying fragments": "calor dos fragmentos que decaem",
  "full power": "plena potência",
  "running at full power": "a funcionar a plena potência",
  "{a} after the rods dropped": "{a} depois da queda das barras",
  "{a} s": "{a} s",
  "{a} min": "{a} min",
  "{a} hours": "{a} horas",
  "{a} days": "{a} dias",
  "{a} months": "{a} meses",
  "total heat: {a} % of full power": "calor total: {a} % da plena potência",
  "the splitting dies away in about a minute": "as cisões extinguem-se em cerca de um minuto",
  "the splitting dies away within about a minute": "as cisões extinguem-se em cerca de um minuto",
  "the decay heat stays and fades slowly": "o calor residual fica e diminui devagar",
  "the decay heat stays, and fades only slowly": "o calor residual permanece, e só diminui devagar",
  // scene 2: the fading curve
  "{#} min": "{#} min",
  "{#} hour": "{#} hora",
  "{#} day": "{#} dia",
  "{#} week": "{#} semana",
  "{#} year": "{#} ano",
  "heat, share of full power": "calor, fração da plena potência",
  "heat, as a share of full power": "calor, como fração da plena potência",
  "{a} after shutdown: {b} % of full power": "{a} após a paragem: {b} % da plena potência",
  "{#} MW core: {a} MW, like {b} kettles": "núcleo de {#} MW: {a} MW, {b} chaleiras",
  "for a {#} MW core: {a} MW, as much as {b} electric kettles": "num núcleo de {#} MW: {a} MW, tanto como {b} chaleiras elétricas",
  // scenes 3-4: cooling
  "pool, up high": "piscina, em cima",
  "water pool, placed higher": "piscina de água, colocada mais acima",
  "cooler": "arrefecedor",
  "heat exchanger": "permutador de calor",
  "pump on": "bomba ligada",
  "pump running": "bomba a funcionar",
  "pump off": "bomba desligada",
  "pump stopped": "bomba parada",
  "boiling": "ebulição",
  "the water starts to boil": "a água começa a ferver",
  "normal": "normal",
  "too hot": "quente demais",
  "temperature": "temperatura",
  "core temperature": "temperatura do núcleo",
  "{a} after shutdown · heat {b} % of full power": "{a} após a paragem · calor {b} % da plena potência",
  "too hot: cooling must be restored": "quente demais: é preciso repor o arrefecimento",
  "too hot: the water would start to boil away; cooling must be restored": "quente demais: a água começaria a evaporar-se; é preciso repor o arrefecimento",
  "temperature climbing": "a temperatura sobe",
  "temperature climbing: the heat has nowhere to go": "a temperatura sobe: o calor não tem para onde ir",
  "pumps carry the heat away": "as bombas levam o calor",
  "steady: the pumps carry the heat away": "estável: as bombas levam o calor",
  "steady, with no pumps": "estável, sem bombas",
  "steady: natural circulation carries the heat away": "estável: a circulação natural leva o calor",
  "steady": "estável",
});
