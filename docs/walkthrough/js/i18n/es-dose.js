/* Spanish: dose (Dosis de radiación) */
WT.L.ch.dose = {
  num: "Lección 3", title: "Dosis de radiación", short: "Dosis",
  html: `
<div class="step">
  <h3>Qué mide un sievert</h3>
  <p>La dosis empieza siendo energía absorbida por kilogramo de cuerpo. El <b>sievert</b> pondera después esa energía según el daño que causa: la misma energía aportada por partículas alfa cuenta veinte veces más que si llega con rayos gamma, porque se concentra en unas pocas trazas densas.</p>
  <div class="btns"><button class="btn ghost" data-act="rg" aria-pressed="true">Rayos gamma</button><button class="btn ghost" data-act="ra" aria-pressed="false">Partículas alfa</button></div>
</div>
<div class="step">
  <h3>Dosis cotidianas</h3>
  <p>Cada marca de esta torre vale diez veces la de abajo. Arrastra la perla brillante para comparar: un TAC de tórax equivale a la dosis de muchos miles de plátanos, y un año de radiación natural, a unas cuantas docenas de vuelos.</p>
  <div class="ctl"><label for="ds-l">Dosis</label><input id="ds-l" type="range" data-bind="ld" data-instant min="-7" max="1" step="0.02" value="-2.15"><output class="ds-out"></output></div>
</div>
<div class="step">
  <h3>Suma tu año</h3>
  <p>Todo el mundo recibe unos 2,4 milisieverts al año de la naturaleza, sobre todo del radón, un gas que sale del suelo. Añade tus vuelos, tus pruebas médicas y tu altitud.</p>
  <div class="ctl"><label for="ds-f">Vuelos transatlánticos</label><input id="ds-f" type="range" data-bind="fl" data-instant min="0" max="40" step="1" value="4"><output data-show="fl" data-fmt="0"></output></div>
  <div class="ctl"><label for="ds-ct">TAC de tórax</label><input id="ds-ct" type="range" data-bind="ct" data-instant min="0" max="3" step="1" value="0"><output data-show="ct" data-fmt="0"></output></div>
  <div class="ctl"><label for="ds-h">Altitud de tu casa (m)</label><input id="ds-h" type="range" data-bind="alt" data-instant min="0" max="3500" step="50" value="300"><output data-show="alt" data-fmt="0"></output></div>
</div>
<div class="step">
  <h3>Una dosis alta de golpe</h3>
  <p>Por debajo de unos 100 milisieverts, cualquier riesgo añadido de cáncer es demasiado pequeño para medirlo; las normas de protección suponen que crece en proporción a la dosis. Hacia un sievert de golpe, las células reciben tantos impactos que empieza la enfermedad por radiación.</p>
  <div class="ctl"><label for="ds-a">Dosis de golpe</label><input id="ds-a" type="range" data-bind="la" data-instant min="-3" max="1" step="0.02" value="-1"><output class="ds-out2"></output></div>
</div>`,
};

Object.assign(WT.L.labels, {
  /* step 1: tissue */
  "cell nuclei in a patch of body": "núcleos celulares en un trozo de cuerpo",
  "cell nuclei in a patch of body tissue": "núcleos celulares en un trozo de tejido",
  "{#} milligray of alpha: a few cells hit hard": "{#} miligray de alfa: pocas células, muy dañadas",
  "{#} milligray of gamma: about one track per cell": "{#} miligray de gamma: cerca de una traza por célula",
  "same energy · counts as {#} millisieverts": "misma energía · cuenta como {#} milisieverts",
  "counts as {#} millisievert": "cuenta como {#} milisievert",
  "illustration": "ilustración",
  /* step 2: the ladder */
  "{#} µSv": "{#} µSv",
  "{#} mSv": "{#} mSv",
  "{#} Sv": "{#} Sv",
  "eating a banana  ·  {#} µSv": "comer un plátano  ·  {#} µSv",
  "dental X-ray  ·  {#} µSv": "radiografía dental  ·  {#} µSv",
  "chest X-ray  ·  {#} µSv": "radiografía de tórax  ·  {#} µSv",
  "flight across the Atlantic  ·  {#} µSv": "vuelo transatlántico  ·  {#} µSv",
  "a year of natural background  ·  {#} mSv": "un año de radiación natural  ·  {#} mSv",
  "chest CT scan  ·  {#} mSv": "TAC de tórax  ·  {#} mSv",
  "yearly limit for radiation workers  ·  {#} mSv": "límite anual de trabajadores expuestos  ·  {#} mSv",
  "a year on the Kerala coast (high spots)  ·  {#} mSv": "un año en la costa de Kerala (zonas altas)  ·  {#} mSv",
  "a year in the highest Ramsar homes  ·  {#} mSv": "un año en las casas más expuestas de Ramsar  ·  {#} mSv",
  "at once: radiation sickness begins  ·  {#} Sv": "de golpe: empieza la enfermedad por radiación  ·  {#} Sv",
  "at once: about half die untreated  ·  {#} Sv": "de golpe: muere la mitad sin tratamiento  ·  {#} Sv",
  "banana  ·  {#} µSv": "plátano  ·  {#} µSv",
  "Atlantic flight  ·  {#} µSv": "vuelo Atlántico  ·  {#} µSv",
  "{#} yr background  ·  {#} mSv": "{#} año natural  ·  {#} mSv",
  "chest CT  ·  {#} mSv": "TAC tórax  ·  {#} mSv",
  "worker limit/yr  ·  {#} mSv": "límite trabajador/año  ·  {#} mSv",
  "Kerala, {#} yr  ·  {#} mSv": "Kerala, {#} año  ·  {#} mSv",
  "Ramsar, {#} yr  ·  {#} mSv": "Ramsar, {#} año  ·  {#} mSv",
  "{#} Sv at once  ·  {#} Sv": "{#} Sv de golpe  ·  {#} Sv",
  "{#}–{#} Sv at once  ·  {#} Sv": "{#}–{#} Sv de golpe  ·  {#} Sv",
  "{#} µSv: the dose of {#} bananas": "{#} µSv: la dosis de {#} plátanos",
  "{#} µSv: the dose of {#} thousand bananas": "{#} µSv: la dosis de {#} mil plátanos",
  "{#} µSv: {#} bananas, or {#} flights": "{#} µSv: {#} plátanos, o {#} vuelos",
  "{#} µSv: {#} thousand bananas, or {#} flights": "{#} µSv: {#} mil plátanos, o {#} vuelos",
  "{#} µSv: {#} million bananas, or {#} flights": "{#} µSv: {#} millones de plátanos, o {#} vuelos",
  "{#} µSv: {#} bananas, or {#} thousand flights": "{#} µSv: {#} plátanos, o {#} mil vuelos",
  "{#} µSv: {#} thousand bananas, or {#} thousand flights": "{#} µSv: {#} mil plátanos, o {#} mil vuelos",
  "{#} µSv: {#} million bananas, or {#} thousand flights": "{#} µSv: {#} millones de plátanos, o {#} mil vuelos",
  "{#} mSv: {#} bananas, or {#} flights": "{#} mSv: {#} plátanos, o {#} vuelos",
  "{#} mSv: {#} thousand bananas, or {#} flights": "{#} mSv: {#} mil plátanos, o {#} vuelos",
  "{#} mSv: {#} million bananas, or {#} flights": "{#} mSv: {#} millones de plátanos, o {#} vuelos",
  "{#} mSv: {#} bananas, or {#} thousand flights": "{#} mSv: {#} plátanos, o {#} mil vuelos",
  "{#} mSv: {#} thousand bananas, or {#} thousand flights": "{#} mSv: {#} mil plátanos, o {#} mil vuelos",
  "{#} mSv: {#} million bananas, or {#} thousand flights": "{#} mSv: {#} millones de plátanos, o {#} mil vuelos",
  "{#} Sv: {#} bananas, or {#} flights": "{#} Sv: {#} plátanos, o {#} vuelos",
  "{#} Sv: {#} thousand bananas, or {#} flights": "{#} Sv: {#} mil plátanos, o {#} vuelos",
  "{#} Sv: {#} million bananas, or {#} flights": "{#} Sv: {#} millones de plátanos, o {#} vuelos",
  "{#} Sv: {#} bananas, or {#} thousand flights": "{#} Sv: {#} plátanos, o {#} mil vuelos",
  "{#} Sv: {#} thousand bananas, or {#} thousand flights": "{#} Sv: {#} mil plátanos, o {#} mil vuelos",
  "{#} Sv: {#} million bananas, or {#} thousand flights": "{#} Sv: {#} millones de plátanos, o {#} mil vuelos",
  "{#} µSv: {#} bananas, {#} flights or {#} years of background": "{#} µSv: {#} plátanos, {#} vuelos o {#} años de radiación natural",
  "{#} µSv: {#} thousand bananas, {#} flights or {#} years of background": "{#} µSv: {#} mil plátanos, {#} vuelos o {#} años de radiación natural",
  "{#} µSv: {#} million bananas, {#} flights or {#} years of background": "{#} µSv: {#} millones de plátanos, {#} vuelos o {#} años de radiación natural",
  "{#} µSv: {#} bananas, {#} thousand flights or {#} years of background": "{#} µSv: {#} plátanos, {#} mil vuelos o {#} años de radiación natural",
  "{#} µSv: {#} thousand bananas, {#} thousand flights or {#} years of background": "{#} µSv: {#} mil plátanos, {#} mil vuelos o {#} años de radiación natural",
  "{#} µSv: {#} million bananas, {#} thousand flights or {#} years of background": "{#} µSv: {#} millones de plátanos, {#} mil vuelos o {#} años de radiación natural",
  "{#} mSv: {#} bananas, {#} flights or {#} years of background": "{#} mSv: {#} plátanos, {#} vuelos o {#} años de radiación natural",
  "{#} mSv: {#} thousand bananas, {#} flights or {#} years of background": "{#} mSv: {#} mil plátanos, {#} vuelos o {#} años de radiación natural",
  "{#} mSv: {#} million bananas, {#} flights or {#} years of background": "{#} mSv: {#} millones de plátanos, {#} vuelos o {#} años de radiación natural",
  "{#} mSv: {#} bananas, {#} thousand flights or {#} years of background": "{#} mSv: {#} plátanos, {#} mil vuelos o {#} años de radiación natural",
  "{#} mSv: {#} thousand bananas, {#} thousand flights or {#} years of background": "{#} mSv: {#} mil plátanos, {#} mil vuelos o {#} años de radiación natural",
  "{#} mSv: {#} million bananas, {#} thousand flights or {#} years of background": "{#} mSv: {#} millones de plátanos, {#} mil vuelos o {#} años de radiación natural",
  "{#} Sv: {#} bananas, {#} flights or {#} years of background": "{#} Sv: {#} plátanos, {#} vuelos o {#} años de radiación natural",
  "{#} Sv: {#} thousand bananas, {#} flights or {#} years of background": "{#} Sv: {#} mil plátanos, {#} vuelos o {#} años de radiación natural",
  "{#} Sv: {#} million bananas, {#} flights or {#} years of background": "{#} Sv: {#} millones de plátanos, {#} vuelos o {#} años de radiación natural",
  "{#} Sv: {#} bananas, {#} thousand flights or {#} years of background": "{#} Sv: {#} plátanos, {#} mil vuelos o {#} años de radiación natural",
  "{#} Sv: {#} thousand bananas, {#} thousand flights or {#} years of background": "{#} Sv: {#} mil plátanos, {#} mil vuelos o {#} años de radiación natural",
  "{#} Sv: {#} million bananas, {#} thousand flights or {#} years of background": "{#} Sv: {#} millones de plátanos, {#} mil vuelos o {#} años de radiación natural",
  "typical values": "valores típicos",
  /* step 3: your year */
  "average {#}": "media {#}",
  "world average {#} mSv": "media mundial {#} mSv",
  "worker limit {#}": "límite trab. {#}",
  "worker limit {#} mSv": "límite de trabajadores {#} mSv",
  "radon in the air  {#}": "radón en el aire  {#}",
  "radon  {#}": "radón  {#}",
  "rocks and soil  {#}": "rocas y suelo  {#}",
  "ground  {#}": "suelo  {#}",
  "food and water  {#}": "comida y agua  {#}",
  "food  {#}": "comida  {#}",
  "cosmic rays at {#} m  {#}": "rayos cósmicos a {#} m  {#}",
  "cosmic rays  {#}": "rayos cósmicos  {#}",
  "cosmic  {#}": "cósmica  {#}",
  "{#} flights  {#}": "{#} vuelos  {#}",
  "flights  {#}": "vuelos  {#}",
  "{#} chest CT  {#}": "{#} TAC de tórax  {#}",
  "CT  {#}": "TAC  {#}",
  "mSv": "mSv",
  "your year: {#} mSv": "tu año: {#} mSv",
  "more than the yearly worker limit": "más que el límite anual de los trabajadores",
  "{#} times the world average": "{#} veces la media mundial",
  "close to the world average": "cerca de la media mundial",
  /* step 4: dose at once */
  "tracks through each cell nucleus: about {#}": "trazas por núcleo celular: unas {#}",
  "tracks through each cell nucleus: about {#} (a few drawn)": "trazas por núcleo celular: unas {#} (se dibujan pocas)",
  "tracks through each cell nucleus: about {#} thousand (a few drawn)": "trazas por núcleo celular: unas {#} mil (se dibujan pocas)",
  "no effect seen": "sin efecto observado",
  "risk assumed": "riesgo supuesto",
  "small added risk assumed": "se supone un pequeño riesgo añadido",
  "sickness": "enfermedad",
  "lethal": "letal",
  "often lethal": "a menudo letal",
  "{#} µSv at once: any extra risk too small to measure": "{#} µSv de golpe: riesgo añadido demasiado pequeño para medirlo",
  "{#} mSv at once: any extra risk too small to measure": "{#} mSv de golpe: riesgo añadido demasiado pequeño para medirlo",
  "{#} mSv at once: no sickness; risk assumed to rise with dose": "{#} mSv de golpe: sin enfermedad; se supone que el riesgo crece con la dosis",
  "{#} Sv at once: no sickness; risk assumed to rise with dose": "{#} Sv de golpe: sin enfermedad; se supone que el riesgo crece con la dosis",
  "{#} Sv at once: radiation sickness: nausea, low blood counts": "{#} Sv de golpe: enfermedad por radiación, náuseas, caída de glóbulos",
  "{#} Sv at once: about half die without treatment": "{#} Sv de golpe: muere cerca de la mitad sin tratamiento",
});
