/* Spanish (Español): everyday (Lo nuclear en la vida cotidiana) */
WT.L.ch.everyday = {
  num: "Lección 4", title: "Lo nuclear en la vida cotidiana", short: "Vida cotidiana",
  html: `
<div class="step">
  <h3>Tomografía PET</h3>
  <p>Un trazador de flúor-18 (semivida de 110 minutos) emite positrones, y cada uno se convierte en dos rayos gamma de 511 keV que salen en sentidos opuestos. Arrastra el punto caliente: el anillo traza una línea por cada par, y las líneas se cruzan donde está el trazador.</p>
</div>
<div class="step">
  <h3>Radioterapia</h3>
  <p>Haces desde varias direcciones se superponen en el tumor, que así recibe la dosis completa mientras cada trayecto por tejido sano solo recibe una parte. Arrastra para girar los haces y mantenerlos lejos de la médula espinal.</p>
  <div class="ctl"><label for="ev-n">Haces</label><input id="ev-n" type="range" data-bind="nb" data-instant min="1" max="7" step="1" value="5"><output data-show="nb" data-fmt="0"></output></div>
  <div class="ctl"><label for="ev-r">Giro</label><input id="ev-r" type="range" data-bind="rotd" data-instant min="0" max="360" step="1" value="20"><output class="ev-rot"></output></div>
</div>
<div class="step">
  <h3>Tecnecio-99m</h3>
  <p>El isótopo de la mayoría de las exploraciones de medicina nuclear emite un rayo gamma de 140 keV que una cámara fuera del cuerpo puede ver, y con una semivida de 6 horas queda poco al cabo de un día. Los hospitales <a href="#chains-3">lo ordeñan del molibdeno-99</a>.</p>
  <div class="ctl"><label for="ev-t">Horas tras la dosis</label><input id="ev-t" type="range" data-bind="th" data-instant min="0" max="48" step="0.5" value="0"><output data-show="th" data-fmt="1"></output></div>
</div>
<div class="step">
  <h3>Datación por carbono</h3>
  <p>Los seres vivos incorporan carbono-14 sin cesar; tras la muerte, decae con una semivida de 5730 años. Fija la edad, o mide lo que queda para leer la edad.</p>
  <div class="ctl"><label for="ev-a">Edad (años)</label><input id="ev-a" type="range" data-bind="age" data-instant min="0" max="50000" step="10" value="5300"><output class="ev-age"></output></div>
  <div class="ctl"><label for="ev-f">Carbono-14 restante (%)</label><input id="ev-f" type="range" data-bind="fr" data-instant min="0.3" max="100" step="0.1" value="52.7"><output class="ev-fr"></output></div>
</div>
<div class="step">
  <h3>Detectores de humo</h3>
  <p>Una mota sellada de americio-241 envía partículas alfa a través de un pequeño hueco de aire y crea iones que transportan una corriente diminuta. El humo atrapa los iones, la corriente cae y suena la alarma.</p>
  <div class="ctl"><label for="ev-s">Humo</label><input id="ev-s" type="range" data-bind="sm" data-instant min="0" max="1" step="0.01" value="0"><output class="ev-sm"></output></div>
</div>`,
};

Object.assign(WT.L.labels, {
  "{#} beams cross: the tumour gets their sum": "{#} haces se cruzan: el tumor recibe su suma",
  "{#} h": "{#} h",
  "{#} h: {#} % left": "{#} h: queda un {#} %",
  "{#} half-lives": "{#} semividas",
  "{#} keV gamma rays": "rayos gamma de {#} keV",
  "{#} of {#} left": "quedan {#} de {#}",
  "{#} years · {#} % left": "{#} años · queda un {#} %",
  "~{#} y: too little to measure": "~{#} años: demasiado poco para medir",
  "a beam crosses the spinal cord: turn the beams": "un haz cruza la médula: gira los haces",
  "a strong gamma signal, easy to image": "una señal gamma intensa, fácil de captar en imagen",
  "after a day, about {#} % is left": "al cabo de un día queda alrededor del {#} %",
  "alarm": "alarma",
  "alpha particles make ions in the air": "las partículas alfa crean iones en el aire",
  "Am{#}": "Am{#}",
  "americium{#} · half-life {#} years · alphas reach about {#} cm in air": "americio{#} · semivida {#} años · las alfas recorren unos {#} cm en aire",
  "americium{#} (sealed)": "americio{#} (sellado)",
  "beyond ~{#} years too little is left to measure": "más allá de ~{#} años queda demasiado poco para medir",
  "carbon{#}": "carbono{#}",
  "clean air: steady current": "aire limpio: corriente estable",
  "current": "corriente",
  "detector ring": "anillo de detectores",
  "dose": "dosis",
  "each decay: two {#} keV gamma rays, back to back": "cada desintegración: dos rayos gamma de {#} keV, en sentidos opuestos",
  "fading: half is gone every {#} hours": "se desvanece: la mitad desaparece cada {#} horas",
  "fluorine{#} · half-life {#} min · {#} pairs recorded": "flúor{#} · semivida {#} min · {#} pares registrados",
  "gamma camera": "gammacámara",
  "half-life {#} y": "semivida {#} años",
  "illustration": "ilustración",
  "Mo{#} ({#} h)": "Mo{#} ({#} h)",
  "molybdenum{#}, half-life {#} h": "molibdeno{#}, semivida {#} h",
  "nitrogen{#}": "nitrógeno{#}",
  "nitrogen{#} (after a beta decay)": "nitrógeno{#} (tras una desintegración beta)",
  "one beam: more dose near the skin than in the tumour": "un solo haz: más dosis cerca de la piel que en el tumor",
  "Ötzi the Iceman, ~{#} y": "Ötzi, el hombre de hielo, ~{#} años",
  "pairs of {#} keV gamma rays, back to back": "pares de rayos gamma de {#} keV, en sentidos opuestos",
  "physical decay only": "solo decaimiento físico",
  "smoke: current down, alarm!": "humo: la corriente cae, ¡alarma!",
  "some ions caught: current dipping": "algunos iones atrapados: la corriente baja",
  "spinal cord": "médula espinal",
  "Tc{#}m ({#} h)": "Tc{#}m ({#} h)",
  "technetium{#}m, half-life {#} h": "tecnecio{#}m, semivida {#} h",
  "tracer": "trazador",
  "tracer (drag me)": "trazador (arrástrame)",
  "tumour": "tumor",
  "tumour {#} % · spinal cord {#} % · healthy tissue at most {#} %": "tumor {#} % · médula {#} % · tejido sano como máximo {#} %",
  "tumour {#} % · spinal cord {#} % · other tissue at most {#} %": "tumor {#} % · médula {#} % · otros tejidos como máximo {#} %",
  "years": "años",
});
