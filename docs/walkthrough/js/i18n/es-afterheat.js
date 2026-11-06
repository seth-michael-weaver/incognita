/* Spanish: afterheat (El calor tras la parada) */
WT.L.ch.afterheat = {
  num: "Lección 1", title: "El calor tras la parada", short: "Calor residual",
  html: `
<div class="step">
  <h3>La cadena se detiene</h3>
  <p>Dejar caer las barras de control detiene la fisión de los átomos en cerca de un minuto. Pero el combustible sigue al rojo: los fragmentos que dejaron las fisiones anteriores son radiactivos, y sus desintegraciones siguen desprendiendo calor.</p>
  <div class="btns"><button class="btn" data-act="ahDrop">Dejar caer las barras</button> <button class="btn ghost" data-act="ahUp">Reiniciar</button></div>
</div>
<div class="step">
  <h3>Se apaga, despacio</h3>
  <p>Justo después de la parada este calor es de un 6–7 % de la plena potencia. Al cabo de una hora es de un 1 %, al cabo de un día de medio por ciento, al cabo de una semana de un cuarto. Porcentajes pequeños, pero de una cifra enorme.</p>
  <div class="ctl"><label for="ah-t">Tiempo desde la parada</label><input id="ah-t" type="range" data-bind="lt" data-instant min="0" max="7.5" step="0.01" value="3.56"></div>
</div>
<div class="step">
  <h3>Que el agua siga circulando</h3>
  <p>Por eso el núcleo se sigue refrigerando también tras la parada. Las bombas hacen circular el agua junto al combustible y se llevan el calor. Apágalas y la temperatura sube, porque el calor no tiene adónde ir.</p>
  <div class="btns"><button class="btn ghost" data-act="ahPump" aria-pressed="true">Bombas</button></div>
</div>
<div class="step">
  <h3>Refrigerar sin bombas</h3>
  <p>El agua caliente sube y el agua fría baja. Un circuito que llega hasta una piscina situada más alta que el núcleo mantiene el agua en movimiento sin ninguna bomba. Varios diseños recientes confían en esto durante días.</p>
  <div class="btns"><button class="btn ghost" data-act="ahPump" aria-pressed="false">Bombas</button> <button class="btn ghost" data-act="ahPass" aria-pressed="true">Circuito pasivo</button></div>
</div>`,
};

Object.assign(WT.L.labels, {
  "illustration": "ilustración",
  // scene 1: the rods drop
  "splitting atoms": "fisiones",
  "heat from splitting atoms": "calor de las fisiones",
  "decaying fragments": "desintegraciones",
  "heat from decaying fragments": "calor de los fragmentos que se desintegran",
  "full power": "plena potencia",
  "running at full power": "funcionando a plena potencia",
  "{a} after the rods dropped": "{a} tras la caída de las barras",
  "{a} s": "{a} s",
  "{a} min": "{a} min",
  "{a} hours": "{a} horas",
  "{a} days": "{a} días",
  "{a} months": "{a} meses",
  "total heat: {a} % of full power": "calor total: {a} % de la plena potencia",
  "the splitting dies away in about a minute": "las fisiones se extinguen en un minuto",
  "the splitting dies away within about a minute": "las fisiones se extinguen en cerca de un minuto",
  "the decay heat stays and fades slowly": "el calor residual queda y baja despacio",
  "the decay heat stays, and fades only slowly": "el calor residual permanece y solo baja despacio",
  // scene 2: the fading curve
  "{#} min": "{#} min",
  "{#} hour": "{#} hora",
  "{#} day": "{#} día",
  "{#} week": "{#} semana",
  "{#} year": "{#} año",
  "heat, share of full power": "calor, fracción de la plena potencia",
  "heat, as a share of full power": "calor, como fracción de la plena potencia",
  "{a} after shutdown: {b} % of full power": "{a} tras la parada: {b} % de la plena potencia",
  "{#} MW core: {a} MW, like {b} kettles": "núcleo de {#} MW: {a} MW, como {b} hervidores",
  "for a {#} MW core: {a} MW, as much as {b} electric kettles": "en un núcleo de {#} MW: {a} MW, tanto como {b} hervidores eléctricos",
  // scenes 3-4: cooling
  "pool, up high": "piscina en alto",
  "water pool, placed higher": "piscina de agua, situada más alta",
  "cooler": "enfriador",
  "heat exchanger": "intercambiador de calor",
  "pump on": "bomba en marcha",
  "pump running": "bomba en marcha",
  "pump off": "bomba parada",
  "pump stopped": "bomba parada",
  "boiling": "ebullición",
  "the water starts to boil": "el agua empieza a hervir",
  "normal": "normal",
  "too hot": "demasiado caliente",
  "temperature": "temperatura",
  "core temperature": "temperatura del núcleo",
  "{a} after shutdown · heat {b} % of full power": "{a} tras la parada · calor {b} % de la plena potencia",
  "too hot: cooling must be restored": "demasiado caliente: hay que restablecer la refrigeración",
  "too hot: the water would start to boil away; cooling must be restored": "demasiado caliente: el agua empezaría a evaporarse; hay que restablecer la refrigeración",
  "temperature climbing": "la temperatura sube",
  "temperature climbing: the heat has nowhere to go": "la temperatura sube: el calor no tiene adónde ir",
  "pumps carry the heat away": "las bombas se llevan el calor",
  "steady: the pumps carry the heat away": "estable: las bombas se llevan el calor",
  "steady, with no pumps": "estable, sin bombas",
  "steady: natural circulation carries the heat away": "estable: la circulación natural se lleva el calor",
  "steady": "estable",
});
