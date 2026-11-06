/* Spanish: xenon (Lección 1, envenenamiento por xenón) */
WT.L.ch.xenon = {
  num: "Lección 1", title: "Envenenamiento por xenón", short: "Xenón",
  html: `
<div class="step">
  <h3>Un veneno creado por la fisión</h3>
  <p>Cerca del 6,6 % de las fisiones conducen, a través del yodo-135, al xenón-135: el absorbente de neutrones más fuerte que se conoce. Se acumula durante unos dos días, hasta que los neutrones lo queman y la desintegración lo elimina tan deprisa como se forma. A mayor potencia también se quema más rápido, así que el nivel se satura.</p>
  <div class="ctl"><label for="xe-p1">Potencia (%)</label><input id="xe-p1" type="range" data-bind="P" data-instant min="10" max="100" step="5" value="100"><output data-show="P" data-fmt="0"></output></div>
</div>
<div class="step">
  <h3>El pozo de xenón</h3>
  <p>Al parar el reactor el quemado se detiene, pero el yodo ya formado sigue convirtiéndose en xenón. El veneno alcanza su máximo unas nueve horas después, más de lo que las barras pueden devolver, así que el reactor no puede volver a arrancar; se desvanece en dos o tres días.</p>
  <div class="ctl"><label for="xe-th">Horas tras la parada</label><input id="xe-th" type="range" data-bind="th" data-instant min="0" max="72" step="0.5" value="9"><output data-show="th" data-fmt="1"></output></div>
</div>
<div class="step">
  <h3>Parar y volver a arrancar</h3>
  <p>Ahora corre en directo, tres horas por segundo. Para el reactor e intenta arrancarlo de nuevo: dentro del pozo se rechaza; más tarde, los neutrones queman el xenón. Un simple cambio de potencia también hace oscilar el xenón durante horas.</p>
  <div class="ctl"><label for="xe-p3">Potencia (%)</label><input id="xe-p3" type="range" data-bind="P" data-instant min="10" max="100" step="5" value="100"><output data-show="P" data-fmt="0"></output></div>
  <div class="btns"><button class="btn" data-act="xeshut">Parar</button><button class="btn ghost" data-act="xerestart">Arrancar de nuevo</button></div>
</div>
<div class="step">
  <h3>Oscilaciones de xenón</h3>
  <p>En un núcleo grande las dos mitades están solo débilmente acopladas. Introduce barras en un lado: allí hay menos flujo, que quema menos xenón, así que la potencia se desplaza al otro lado y luego vuelve, más o menos una vez al día. En núcleos más grandes la oscilación crece si los operadores no la amortiguan.</p>
  <div class="ctl"><label for="xe-wd">Tamaño del núcleo (m)</label><input id="xe-wd" type="range" data-bind="wd" data-instant min="1.5" max="3.5" step="0.1" value="3"><output data-show="wd" data-fmt="1"></output></div>
  <div class="btns"><button class="btn" data-act="xepush">Introducir barras en el lado izquierdo</button></div>
</div>`,
};
/* attributes referenced in the English chapter script (for the structure check): data-act="${act}" */

Object.assign(WT.L.labels, {
  "fission → iodine{#} ({#} h) → xenon{#} ({#} h) → Cs{#}": "fisión → yodo{#} ({#} h) → xenón{#} ({#} h) → Cs{#}",
  "xenon{#} + n → Xe{#}: {#} million barns": "xenón{#} + n → Xe{#}: {#} millones de barns",
  "fission → iodine{#} ({#} h) → xenon{#} ({#} h) → Cs{#}  ·  Xe{#} swallows neutrons: {#} million barns": "fisión → yodo{#} ({#} h) → xenón{#} ({#} h) → Cs{#}  ·  el Xe{#} traga neutrones: {#} millones de barns",
  "spare reactivity": "reserva de reactividad",
  "spare reactivity the rods can give": "reserva de reactividad de las barras",
  "{#} h": "{#} h",
  "equilibrium {#} %": "equilibrio {#} %",
  "xenon worth (% of k)": "antirreactividad del xenón (% de k)",
  "{#} % power · {#} h after start-up · xenon {#} %": "potencia {#} % · {#} h tras el arranque · xenón {#} %",
  "no restart": "sin rearranque",
  "too poisoned to restart": "demasiado envenenado para arrancar",
  "shutdown": "parada",
  "drag": "arrastra",
  "peak {#} % at {#} h": "máximo {#} % a las {#} h",
  "{#} h after shutdown · xenon {#} % · restart possible": "{#} h tras la parada · xenón {#} % · se puede arrancar",
  "{#} h after shutdown · xenon {#} % · cannot restart": "{#} h tras la parada · xenón {#} % · no puede arrancar",
  "shut down": "parado",
  "refused: more xenon than spare reactivity": "rechazado: más xenón que reserva de reactividad",
  "restarted": "arrancado de nuevo",
  "tap the core to shut down": "toca el núcleo para pararlo",
  "tap the core to restart": "toca el núcleo para arrancarlo",
  "power": "potencia",
  "running at {#} % · xenon {#} %": "en marcha al {#} % · xenón {#} %",
  "shut down · in the pit · xenon {#} %": "parado · en el pozo · xenón {#} %",
  "shut down · restart possible · xenon {#} %": "parado · se puede arrancar · xenón {#} %",
  "left {#} %": "izquierda {#} %",
  "right {#} %": "derecha {#} %",
  "tap a side to push rods in": "toca un lado para introducir barras",
  "more power left": "más potencia a la izquierda",
  "more power right": "más potencia a la derecha",
  "swing period {#} h · {#} m core: the swing dies away": "periodo {#} h · núcleo de {#} m: la oscilación se amortigua",
  "swing period {#} h · {#} m core: the swing dies away slowly": "periodo {#} h · núcleo de {#} m: la oscilación se amortigua despacio",
  "swing period {#} h · {#} m core: the swing grows": "periodo {#} h · núcleo de {#} m: la oscilación crece",
  "{#} m core: push the rods to start a swing": "núcleo de {#} m: introduce las barras para iniciar una oscilación",
  "illustration": "ilustración",
});
