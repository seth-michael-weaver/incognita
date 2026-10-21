/* Spanish: preeq (Chapter 4, pre-equilibrium) */
WT.es.ch.preeq = {
  num: "Capítulo 4", title: "Choques antes de la calma", short: "Preequilibrio",
  lead: "Preequilibrio significa “antes de que la energía se reparta por igual”. Un neutrón que entra en un núcleo no comparte su energía con todos a la vez. Durante los primeros choques una sola partícula conserva casi toda la energía, y esa partícula puede salir disparada de vuelta.",
  html: `
<div class="step">
  <p>La imagen muestra dos pozos, uno para <em class="p">protones</em> y otro para <em class="n">neutrones</em>. Cada bola es un nucleón (un protón o un neutrón) situado en un nivel de energía, dibujado como un peldaño. Los peldaños se llenan de abajo arriba hasta la <b>superficie de Fermi</b>, el tope de los niveles ocupados. Un nucleón por encima de la línea discontinua marcada “libre” tiene energía suficiente para escapar. El motor sigue a protones y neutrones por separado a lo largo de todo este capítulo.</p>
  <p>El neutrón entrante flota sobre ambos pozos. Lleva su propia energía más la energía liberada al ser capturado, varios MeV (millones de electronvoltios, la unidad de energía que usamos aquí). Ahora mismo una sola partícula tiene toda esa energía, y los niveles ocupados no tienen huecos.</p>
</div>
<div class="step">
  <h3>Levantar pares</h3>
  <p>Ahora el neutrón ha chocado con un nucleón bajo la superficie y lo ha subido a un peldaño vacío. El sitio vacío que deja atrás es un <b>hueco</b>, dibujado como un anillo abierto. El motor cuenta las partículas por encima de la superficie más los huecos por debajo, y llama a cada uno <b>excitón</b>. El primer choque convierte 1 partícula en 2 partículas y 1 hueco (n = 3 excitones); cada choque posterior añade otro par partícula-hueco.</p>
  <div class="btns"><button class="btn" data-act="collide">Chocar</button><button class="btn ghost" data-act="reset">Empezar de nuevo</button></div>
  <p>Pulsa Chocar unas cuantas veces. El nucleón levantado puede ser un protón o un neutrón, y el motor lleva una cuenta aparte para cada uno. Con cada par la energía se reparte entre más, así que la partícula más alta queda más abajo.</p>
</div>
<div class="step">
  <h3>La bifurcación en cada etapa</h3>
  <p>La imagen muestra una etapa de la cadena. El neutrón de arriba puede escapar (la flecha hacia arriba y afuera), si todavía está por encima de la línea libre, o puede volver a chocar (la flecha hacia abajo). El grosor de cada flecha indica su probabilidad. La tasa de escape sale del <b>balance detallado</b>: la probabilidad de salir se deduce de la del proceso inverso, que esa misma partícula sea absorbida, y eso lo calcula el Capítulo 2. La tasa de choque es la intensidad media de un choque nucleón-nucleón multiplicada por el número de nuevas configuraciones a las que puede llevar.</p>
  <div class="ctl"><label for="pe-n">Etapa (excitones n)</label><input id="pe-n" type="range" data-bind="n" min="3" max="11" step="2" value="3" data-instant><output data-show="n" data-fmt="0"></output></div>
  <p>Sube la etapa. Al principio de la cadena una partícula tiene casi toda la energía, así que lo que escapa es rápido. Más tarde la energía está muy repartida y solo salen partículas lentas, si es que sale alguna.</p>
</div>
<div class="step">
  <h3>De dónde sale la cola rápida</h3>
  <p>Los mismos dos pozos, ahora con reacciones completas. En cada una la cadena recorre las etapas 3, 5, 7, … hasta que el neutrón de arriba escapa. Vuela hacia la derecha y cae en un montón ordenado por energía: los lentos a la izquierda, los rápidos a la derecha. Su color dice cuándo salió: <em style="font-style:normal;color:var(--warm);font-weight:600">naranja intenso</em> en la etapa 3, más pálido en etapas posteriores, y <em class="n">azul</em> si nada escapó durante la cadena y el neutrón salió después, del núcleo compuesto ya en calma (Capítulo 5). El montón es el <b>espectro</b>: cuántos neutrones salen con cada energía.</p>
  <div class="btns"><button class="btn" data-act="run">Lanzar 300 reacciones</button></div>
  <p>La etapa 3 forma una meseta ancha, casi plana, que llega hasta la energía máxima, porque una partícula todavía tiene casi toda la energía. Las etapas posteriores se amontonan más abajo. La joroba azul de la izquierda es la <b>evaporación</b>: cuando la energía ya está repartida entre todos, solo se escapan neutrones lentos, como el vapor de un líquido caliente.</p>
  <div class="ctl"><label for="pe-e">Energía del neutrón</label><input id="pe-e" type="range" data-bind="E" min="5" max="60" step="0.5" value="20"><output data-show="E" data-fmt="1"></output></div>
  <p>Cambia la energía del neutrón entrante y se lanza una nueva tanda. La evaporación sola no puede producir neutrones rápidos; la meseta sí, y se extiende más cuanto más rápido llega el neutrón.</p>
</div>
<div class="step">
  <h3>Contar configuraciones</h3>
  <p>Un solo pozo, dibujado con peldaños equidistantes separados 1 MeV. La imagen recorre todas las maneras de colocar las partículas en peldaños vacíos por encima de la superficie de Fermi y los huecos en peldaños llenos por debajo, de modo que sus energías sumen la energía a repartir; el contador avanza una vez por configuración. Los nucleones son fermiones: dos no pueden ocupar el mismo peldaño, así que un nucleón levantado tiene que caer en un peldaño vacío y un hueco solo puede abrirse donde había un nucleón. Esta regla es el <b>bloqueo de Pauli</b>.</p>
  <div class="ctl"><label for="pe-u">Energía a repartir (MeV)</label><input id="pe-u" type="range" data-bind="U" min="2" max="16" step="1" value="8" data-instant><output data-show="U" data-fmt="0"></output></div>
  <div class="btns"><button class="btn" data-act="addpair">Añadir un par</button><button class="btn ghost" data-act="droppair">Quitar un par</button></div>
  <p>Añade un par y la cuenta se dispara; sube la energía y crece aproximadamente como <i>E</i><sup>n−1</sup>, donde n es el número de excitones. Esa cuenta, la <b>densidad de estados partícula-hueco</b>, es la que fija la tasa de choque del paso anterior: más maneras de colocarse significan más destinos posibles para un choque. El motor cuenta con la regla de Pauli incorporada, sobre la escalera real (en un núcleo mediano los peldaños están a un cuarto de MeV, así que hay muchísimas más configuraciones), y con un límite más que se ve a energía alta: un hueco no puede estar más hondo que el fondo del pozo.</p>
</div>
<div class="step">
  <h3>También salen agregados</h3>
  <p>Pulsa un botón para ver cómo un pequeño agregado de nucleones sale pronto. En una <b>captura de nucleón</b> (pickup), un protón que va saliendo agarra un neutrón en la superficie y sale con él como un <em class="n">deuterón</em> (un protón más un neutrón). Si agarra dos, da un tritón (un protón y dos neutrones) o un helio-3 (dos protones y un neutrón). El motor usa las fórmulas de Kalbach para la frecuencia de cada captura. En un <b>arranque</b> (knockout), el neutrón entrante choca con una <em class="a">partícula alfa</em> (dos protones y dos neutrones fuertemente ligados) que ya existe cerca de la superficie, y la expulsa directamente.</p>
  <div class="btns"><button class="btn ghost" data-act="pickup">Captura un neutrón → d</button><button class="btn ghost" data-act="knock">Arranca una α</button></div>
  <p>Ambos procesos dan a deuterones y alfas sus propias colas rápidas, que empiezan justo por encima de sus energías de separación (la energía que cuesta sacar a cada uno).</p>
</div>
<div class="step">
  <h3>Un segundo rápido</h3>
  <p>Los pozos repiten una reacción cada vez, con la escala de energía comprimida para que quepa. El neutrón entra y choca; el neutrón de arriba escapa rápido. Mira lo que queda: otro nucleón levantado y un hueco. A baja energía ese nucleón queda por debajo de la línea libre y se queda. A alta energía todavía puede estar por encima de la línea, y también escapa: un segundo neutrón o protón rápido, antes de que el resto se calme.</p>
  <div class="ctl"><label for="pe-e2">Energía del neutrón</label><input id="pe-e2" type="range" data-bind="E" min="5" max="80" step="0.5" value="40"><output data-show="E" data-fmt="1"></output></div>
  <p>Cambia la energía. Por debajo de unos 20 MeV el segundo nucleón casi nunca supera la línea; por encima, cada vez más reacciones sueltan dos partículas rápidas. Es la emisión de <b>preequilibrio múltiple</b>, y para ella el motor sigue los excitones del núcleo residual. Lo que no ha salido al final de la cadena se convierte en el núcleo compuesto del próximo capítulo. El motor ejecuta esta cadena a todas las energías incidentes con una entrada suave, porque un cambio brusco metería un escalón falso en la sección eficaz de captura (con qué frecuencia el neutrón es capturado y sale un fotón).</p>
  <div class="aside">En el código: <code>preeq/exciton.py</code> (cadena de excitones de dos componentes, tasas de choque y de escape), <code>density/particle_hole.py</code> (densidades de estados partícula-hueco con correcciones de Pauli y de pozo finito), <code>preeq/complex.py</code> (captura, desprendimiento y arranque α de Kalbach), <code>preeq/multi.py</code> (preequilibrio múltiple), <code>compound/normalization.py</code> (paso al núcleo compuesto).</div>
</div>`,
};
Object.assign(WT.es.labels, {
  // wells
  "protons": "protones",
  "neutrons": "neutrones",
  "Fermi": "Fermi",
  "Fermi surface": "superficie de Fermi",
  "free": "libre",
  "free: can escape": "libre: puede escapar",
  "all the energy in one nucleon": "toda la energía en un nucleón",
  "{#} particle, {#} holes": "{#} partícula, {#} huecos",
  // pairs
  "{#} particle, {#} holes: n = {#}": "{#} partícula, {#} huecos: n = {#}",
  "{#} particle, {#} hole: n = {#}": "{#} partícula, {#} hueco: n = {#}",
  "{#} particles, {#} hole: n = {#}": "{#} partículas, {#} hueco: n = {#}",
  "{#} particles, {#} holes: n = {#}": "{#} partículas, {#} huecos: n = {#}",
  "protons: {#} lifted, {#} hole": "protones: {#} arriba, {#} hueco",
  "protons: {#} lifted, {#} holes": "protones: {#} arriba, {#} huecos",
  "neutrons: {#} lifted, {#} hole": "neutrones: {#} arriba, {#} hueco",
  "neutrons: {#} lifted, {#} holes": "neutrones: {#} arriba, {#} huecos",
  "chain ends: the rest becomes a compound nucleus": "fin de la cadena: el resto forma un núcleo compuesto",
  // fork
  "about {#} MeV above surface": "unos {#} MeV sobre la superficie",
  "escapes  {#}%": "escapa  {#} %",
  "collides again  {#}%": "vuelve a chocar  {#} %",
  "below the free line: it cannot leave": "bajo la línea libre: no puede salir",
  "n = {#}: {#} particles, {#} hole, {#} MeV": "n = {#}: {#} partículas, {#} hueco, {#} MeV",
  "n = {#}: {#} particles, {#} holes, {#} MeV": "n = {#}: {#} partículas, {#} huecos, {#} MeV",
  "stage n = {#}: {#} particles and {#} hole share {#} MeV": "etapa n = {#}: {#} partículas y {#} hueco se reparten {#} MeV",
  "stage n = {#}: {#} particles and {#} holes share {#} MeV": "etapa n = {#}: {#} partículas y {#} huecos se reparten {#} MeV",
  // tail
  "max {#} MeV": "máx. {#} MeV",
  "slow": "lento",
  "fast →": "rápido →",
  "stage {#}": "etapa {#}",
  "chain over: compound": "fin de cadena: compuesto",
  "left at:": "salió:",
  "neutron left at:": "salió en:",
  "evaporation": "evaporación",
  "{#} of {#} landed · {#} left during the chain": "{#} de {#} caídos · {#} salieron durante la cadena",
  // pauli
  "well bottom: no deeper hole": "fondo del pozo: ningún hueco más hondo",
  "bottom of the well": "fondo del pozo",
  "{#} MeV to share": "{#} MeV a repartir",
  "{#} particles · {#} hole": "{#} partículas · {#} hueco",
  "{#} particles · {#} holes": "{#} partículas · {#} huecos",
  "ways, all counted": "maneras, todas contadas",
  "arrangements so far": "configuraciones hasta ahora",
  "one more pair: {#} ways": "un par más: {#} maneras",
  "never two on one rung · holes only where a nucleon was": "nunca dos en un peldaño · huecos solo donde había un nucleón",
  "(first {#} shown as ticks)": "(las primeras {#}, como marcas)",
  // cluster
  "a deuteron leaves": "sale un deuterón",
  "grabs a neutron at the edge": "agarra un neutrón en el borde",
  "a fast proton heads out": "un protón rápido va saliendo",
  "an α ({#} protons + {#} neutrons) waits at the edge": "una α ({#} protones + {#} neutrones) espera en el borde",
  "knocked straight out": "expulsada de golpe",
  // second
  "first fast neutron": "primer neutrón rápido",
  "second fast proton": "segundo protón rápido",
  "second fast neutron": "segundo neutrón rápido",
  "below the free line: stays": "bajo la línea libre: se queda",
  "below the free line: it stays": "bajo la línea libre: se queda",
  "the rest settles: compound nucleus": "el resto se calma: núcleo compuesto",
  "{#} MeV carried in": "{#} MeV aportados",
  "second fast particle in {#} of the last {#} reactions": "segunda partícula rápida en {#} de las últimas {#} reacciones",
});
