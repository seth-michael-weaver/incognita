/* Spanish: preeq (Chapter 4, pre-equilibrium) */
WT.es.ch.preeq = {
  num: "Capítulo 7", title: "Emisión de preequilibrio", short: "Preequilibrio",
  lead: "Un neutrón que entra en un núcleo no comparte su energía con todos a la vez. Durante los primeros choques una sola partícula conserva casi toda la energía, y esa partícula puede salir disparada de vuelta. Esto es el preequilibrio: emisión “antes de que la energía se reparta por igual”.",
  html: `
<div class="step">
  <p>Dos pozos, uno para <em class="p">protones</em> y otro para <em class="n">neutrones</em>. Cada bola es un nucleón en un nivel de energía, dibujado como un peldaño; los peldaños se llenan de abajo arriba hasta la <b>superficie de Fermi</b>. Un nucleón por encima de la línea discontinua “libre” tiene energía suficiente para escapar. El motor sigue a protones y neutrones por separado.</p>
  <p>El neutrón entrante flota encima con toda la energía: la suya más varios MeV (millones de electronvoltios) liberados al ser capturado.</p>
</div>
<div class="step">
  <h3>Excitaciones partícula–hueco</h3>
  <p>El neutrón rápido choca con un nucleón del mar y le cede parte de su energía. Ese nucleón salta a un peldaño vacío, y el lugar que dejó queda vacío: un <b>hueco</b> (el anillo abierto). Así, cada choque crea un <b>par</b>: un nucleón más levantado y un hueco. Los físicos cuentan juntos los nucleones levantados y los huecos y los llaman <b>excitones</b>: tras el primer choque hay 3 (2 levantados, 1 hueco).</p>
  <div class="btns"><button class="btn" data-act="collide">Chocar</button><button class="btn ghost" data-act="reset">Empezar de nuevo</button></div>
  <p>Pulsa Chocar y mira un choque: la zambullida, el salto, el hueco. Hazlo unas cuantas veces. El nucleón golpeado puede ser un protón o un neutrón. Con cada choque la energía se reparte entre más nucleones, así que cada uno de los levantados queda más abajo, y el rápido tiene menos probabilidad de escapar.</p>
</div>
<div class="step">
  <h3>Emisión frente a nuevos choques</h3>
  <p>En cada etapa el neutrón de arriba o bien escapa (flecha hacia arriba, solo si está por encima de la línea libre) o vuelve a chocar (flecha hacia abajo); el grosor indica la probabilidad. La rapidez con que escapa se lee del suceso inverso: un núcleo que traga con facilidad un neutrón de cierta energía también deja salir con facilidad uno de esa energía. El Capítulo 5 ya calculó con qué facilidad lo traga (esta regla de doble sentido se llama <b>balance detallado</b>). La rapidez con que choca es la fuerza con que se golpean dos nucleones, por cuántas formas nuevas hay de repartir la energía tras el golpe.</p>
  <div class="ctl"><label for="pe-n">Etapa (excitones n)</label><input id="pe-n" type="range" data-bind="n" min="3" max="11" step="2" value="3" data-instant><output data-show="n" data-fmt="0"></output></div>
  <p>Sube la etapa. Al principio una partícula tiene casi toda la energía, así que lo que escapa es rápido. Más tarde la energía está muy repartida y sale poco.</p>
</div>
<div class="step">
  <h3>El espectro de preequilibrio</h3>
  <p>El montón de la derecha es el <b>espectro</b>: cuántos neutrones salen con cada energía, los lentos a la izquierda, los rápidos a la derecha. Cada reacción recorre la cadena hasta que el neutrón de arriba escapa, y su color dice cuándo: <em style="font-style:normal;color:var(--warm);font-weight:600">naranja intenso</em> en la etapa 3, más pálido después, <em class="n">azul</em> si salió solo cuando el núcleo ya estaba en calma (Capítulo 8).</p>
  <div class="btns"><button class="btn" data-act="run">Lanzar 300 reacciones</button></div>
  <p>La etapa 3 forma una cúpula ancha y baja que se extiende casi hasta la energía máxima, la única etapa que llega tan lejos. Las etapas posteriores se amontonan más abajo. La joroba azul es la <b>evaporación</b>: cuando todos comparten la energía, solo se escapan neutrones lentos, como el vapor de un líquido caliente.</p>
  <div class="ctl"><label for="pe-e">Energía del neutrón</label><input id="pe-e" type="range" data-bind="E" min="5" max="60" step="0.5" value="20"><output data-show="E" data-fmt="1"></output></div>
  <p>Cambia la energía del neutrón entrante: se lanza una nueva tanda y la cúpula se alarga. La evaporación sola nunca produce neutrones rápidos.</p>
</div>
<div class="step">
  <h3>Densidades de estados partícula–hueco</h3>
  <p>El contador recorre todas las maneras de poner partículas en peldaños vacíos y huecos en peldaños llenos de modo que sus energías sumen la energía a repartir (aquí los peldaños están a 1 MeV). Los nucleones son fermiones: dos no pueden compartir peldaño, así que una partícula tiene que caer en un peldaño vacío y un hueco solo se abre donde había un nucleón. Es el <b>bloqueo de Pauli</b>.</p>
  <div class="ctl"><label for="pe-u">Energía a repartir (MeV)</label><input id="pe-u" type="range" data-bind="U" min="2" max="16" step="1" value="8" data-instant><output data-show="U" data-fmt="0"></output></div>
  <div class="btns"><button class="btn" data-act="addpair">Añadir un par</button><button class="btn ghost" data-act="droppair">Quitar un par</button></div>
  <p>Añade un par y la cuenta se dispara; sube la energía y crece aproximadamente como <i>E</i><sup>n−1</sup>. Esta cuenta, la <b>densidad de estados partícula-hueco</b>, fija la tasa de choque: más configuraciones, más destinos para un choque. El motor cuenta sobre la escalera real, con peldaños a una fracción de MeV, y añade un límite que se ve a energía alta: un hueco no puede estar por debajo del fondo del pozo.</p>
</div>
<div class="step">
  <h3>Emisión de agregados</h3>
  <p>También pueden salir pronto pequeños agregados. En una <b>captura de nucleón</b> (pickup), un protón que va saliendo agarra un neutrón en la superficie y sale con él como un <em class="n">deuterón</em>; si agarra dos, da un tritón o un helio-3. En un <b>arranque</b> (knockout), el neutrón entrante choca con una <em class="a">partícula alfa</em> (dos protones y dos neutrones) ya formada cerca de la superficie y la expulsa. El motor usa las fórmulas de Kalbach para ambos.</p>
  <div class="btns"><button class="btn ghost" data-act="pickup">Captura un neutrón → d</button><button class="btn ghost" data-act="knock">Arranca una α</button></div>
  <p>Pulsa un botón para ver uno. Ambos dan a deuterones y alfas sus propias colas rápidas, que empiezan justo por encima de la energía que cuesta sacar a cada uno.</p>
</div>
<div class="step">
  <h3>Emisión múltiple de preequilibrio</h3>
  <p>A alta energía el primer choque también puede ceder mucha energía al nucleón golpeado. Cuando el neutrón rápido se va, ese segundo nucleón puede tener aún más de los 8 MeV que necesita para salir (la línea libre), y entonces también sale volando: dos partículas rápidas de una sola reacción. La imagen repite una reacción cada vez y dice qué ocurre en cada momento; el número junto a cada bola es su energía.</p>
  <div class="ctl"><label for="pe-e2">Energía del neutrón</label><input id="pe-e2" type="range" data-bind="E" min="5" max="80" step="0.5" value="40"><output data-show="E" data-fmt="1"></output></div>
  <p>Cambia la energía. Por debajo de unos 20 MeV el segundo nucleón rara vez supera la línea; por encima, cada vez más reacciones sueltan dos partículas rápidas. Es el <b>preequilibrio múltiple</b>, que el motor incluye a partir de 20 MeV. Lo que no ha salido se convierte en el núcleo compuesto del próximo capítulo. Por debajo de unos pocos MeV (el nivel discreto más alto del blanco que se usa) el motor se salta la cadena por completo.</p>
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

Object.assign(WT.L.labels, {
  "bump {#}: a proton in the sea was hit, jumped up, and left a hole": "choque {#}: un protón del mar fue golpeado, subió y dejó un hueco",
  "bump!": "¡choque!",
  "hole": "hueco",
  "lifted": "elevado",
  "free line: more than {#} MeV needed to get out": "línea libre: hacen falta más de {#} MeV para salir",
  "a fast neutron comes in with {#} MeV": "entra un neutrón rápido con {#} MeV",
  "bump: it hits a neutron in the sea, which jumps up and leaves a hole": "choque: golpea un neutrón del mar, que sube y deja un hueco",
  "neutron: {#} MeV": "neutrón: {#} MeV",
});
