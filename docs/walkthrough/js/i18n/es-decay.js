/* Spanish: decay (Capítulo 6) */
WT.es.ch.decay = {
  num: "Capítulo 6", title: "Elegir una salida", short: "Desintegración",
  lead: "El núcleo compuesto tiene que deshacerse de su energía emitiendo una partícula o un fotón. Este capítulo dibuja cada salida como una puerta. La tarea del motor es decir qué parte del flujo (la corriente de reacciones que llega aquí) sale por cada puerta.",
  html: `
<div class="step">
  <p>La imagen muestra el núcleo compuesto a la izquierda y una puerta para cada tipo de salida: un <em class="g">fotón</em> (γ, una partícula de luz), un <em class="n">neutrón</em> (n), un <em class="p">protón</em> (p), una <em class="a">partícula alfa</em> (α: dos protones y dos neutrones ligados) y, solo en núcleos pesados, la <em class="f">fisión</em> (partirse en dos). El hueco iluminado de cada puerta es la parte de las desintegraciones que toma esa salida, y las bolas salen por los huecos al mismo ritmo. Las puertas grises están cerradas. Como el núcleo ha olvidado cómo se formó, no tiene favorita; usa cada puerta b en proporción a un peso:</p>
  <div class="formula">fracción<sub>b</sub> = T<sub>b</sub> · ρ<sub>b</sub> / Σ<sub>c</sub> T<sub>c</sub> · ρ<sub>c</sub></div>
  <p>El peso tiene dos partes. El <b>coeficiente de transmisión</b> <i>T</i> es la probabilidad de que una partícula que llega al borde lo atraviese. Sale del modelo óptico del Capítulo 2, aplicado al revés. La <b>densidad de niveles</b> ρ cuenta los estados en los que puede acabar el núcleo que queda atrás, escrita junto a cada puerta. Repartir según <i>T</i> por ρ es la regla de <b>Hauser–Feshbach</b>. A 10 MeV la puerta del neutrón se lleva casi todo; la del fotón es una rendija.</p>
</div>
<div class="step">
  <h3>Por qué casi todas las partículas salen lentas</h3>
  <p>La imagen desmonta la puerta del neutrón, energía por energía. Cada puerta de la fila superior es la salida de los neutrones con una energía de salida ε, lentos a la izquierda y rápidos a la derecha; su hueco es <i>T</i>(ε), más ancho para neutrones más rápidos. Bajo cada puerta está la multitud de estados en los que puede quedar el núcleo restante cuando sale ese neutrón: un neutrón lento deja atrás casi toda la energía, donde los estados abundan, así que las multitudes menguan hacia la derecha. Cada neutrón que sale cae por su puerta y su multitud y aterriza en el montón de abajo.</p>
  <div class="ctl"><label for="dc-sp">Energía disponible</label><input id="dc-sp" type="range" data-bind="spare" min="1" max="12" step="0.5" value="5"><output data-show="spare" data-fmt="1"></output></div>
  <p>Puertas anchas a la derecha, multitudes grandes a la izquierda: el montón, puerta × multitud, es una joroba, el <b>espectro de evaporación</b>, llamado así porque recuerda al vapor que escapa de un líquido caliente. Arrastra la energía disponible (en MeV, millones de electronvoltios): el montón vuelve a empezar, y su pico se queda por debajo de 1 MeV aproximadamente por mucha energía que haya, fijado por la temperatura nuclear. La energía extra sobre todo calienta más al núcleo restante.</p>
</div>
<div class="step">
  <h3>Las partículas cargadas tienen que escalar</h3>
  <p>La imagen muestra la energía que tiene un protón a cada distancia r del centro del núcleo: un pozo dentro y, fuera, una colina creada por la repulsión eléctrica (de Coulomb) de los protones que quedan, que decae como 1/r. El protón rebota dentro del pozo, golpeando la pared. Por debajo de la cima solo puede atravesar por <b>efecto túnel</b> el tramo sombreado de la colina, un efecto cuántico que funciona una vez de cada muchos golpes. Cuanto más ancho es ese tramo, más golpes hacen falta.</p>
  <div class="ctl"><label for="dc-ce">Energía de la partícula</label><input id="dc-ce" type="range" data-bind="eps" min="0.5" max="12" step="0.1" value="3"><output data-show="eps" data-fmt="1"></output></div>
  <div class="btns"><button class="btn ghost" data-act="toggleAlpha">Cambiar protón / alfa</button></div>
  <p>Baja la energía y mira cómo se ensancha el túnel y se acumulan los golpes; luego cambia a la alfa. Con dos cargas se enfrenta a una colina unas dos veces más alta. Por eso los neutrones, que no tienen carga, suelen ganar en cuanto pueden salir, y por eso las salidas de protón y alfa importan sobre todo en núcleos ligeros y a energías altas.</p>
</div>
<div class="step">
  <h3>Las puertas se abren una a una</h3>
  <p>La imagen vuelve a las puertas, ahora a 7 MeV. Cada puerta de partícula se abre solo por encima de su <b>energía de separación</b>, lo que cuesta arrancar esa partícula: aquí 8 MeV para un neutrón, 9 para un protón, 7 para una alfa. Por debajo de los 8 MeV del neutrón, casi todas las desintegraciones emiten luz.</p>
  <div class="ctl"><label for="dc-e">Energía de excitación</label><input id="dc-e" type="range" data-bind="E" min="5" max="24" step="0.1" value="7"><output data-show="E" data-fmt="1"></output></div>
  <p>Arrastra la energía de excitación (la energía que guarda el núcleo) más allá de 8 MeV. En cerca de 1 MeV la puerta del neutrón se abre de par en par y se lleva casi todas las desintegraciones, y la del fotón se estrecha hasta una rendija: su fracción cae cien veces. Las puertas de protón y alfa se iluminan más tarde y siguen estrechas, frenadas por sus colinas de Coulomb.</p>
</div>
<div class="step">
  <h3>Espín y paridad deben cuadrar</h3>
  <p>La imagen muestra el núcleo compuesto (arriba) con espín <i>J</i>, su momento angular, y debajo los estados del núcleo restante ordenados en cajones según su espín <i>J</i>′; los puntos tenues son los estados que guarda cada cajón. El espín y la paridad (una etiqueta + o − de simetría especular) se conservan, así que el neutrón debe llevarse la diferencia. Un neutrón que sale con momento angular orbital <i>l</i> (cuánto gira alrededor del núcleo al salir) cambia el espín hasta <i>l</i> + ½, e invierte la paridad cuando <i>l</i> es impar. Cuanto mayor es <i>l</i>, más estrecha es la puerta: la puerta sobre cada cajón es la de menor <i>l</i> que lo alcanza. Las desintegraciones que aterrizan son macizas donde la paridad se conserva y huecas donde se invierte.</p>
  <div class="ctl"><label for="dc-j">Espín compuesto J</label><input id="dc-j" type="range" data-bind="J" min="0" max="10" step="1" value="2" data-instant><output id="dc-jout">5/2</output></div>
  <p>Sube <i>J</i>. Las puertas abiertas se desplazan hacia los cajones de espín alto, que guardan pocos estados, y los cajones que más guardan quedan tras puertas cerradas. Así, un núcleo compuesto de espín alto tarda en emitir partículas, lo que da su oportunidad a los fotones y a los isómeros (estados de vida larga, Capítulo 7).</p>
</div>
<div class="step">
  <h3>El camino por el que entraste</h3>
  <p>A baja energía el núcleo compuesto es en realidad un conjunto de <b>resonancias</b> separadas y estrechas: energías concretas en las que el neutrón se absorbe con facilidad. La imagen muestra ocho, una por fila. Cada una tiene sus propias anchuras de puerta al azar: la puerta de entrada a la izquierda (el canal del neutrón), de anchura <i>x</i>, y las demás puertas a la derecha, de anchuras <i>y</i> (a estas energías bajas las otras salidas son sobre todo fotones). Anchuras así varían muchísimo de una resonancia a otra; algunas puertas están casi cerradas, unas pocas son anchas.</p>
  <div class="btns"><button class="btn" data-act="fire">Lanzar 40 neutrones</button><button class="btn ghost" data-act="reroll">Nuevas resonancias</button></div>
  <p>Un neutrón entra en la resonancia <i>i</i> con probabilidad proporcional a <i>x<sub>i</sub></i>, y sale por la entrada con probabilidad <i>x<sub>i</sub></i> / (<i>x<sub>i</sub></i> + Σ<i>y</i>). Las filas con entrada ancha reciben más neutrones y además devuelven más. Así, la fracción real que vuelve a salir, un <b>promedio de productos</b>, supera a la estimación simple hecha con anchuras promedio, un <b>producto de promedios</b>. El cociente es el <b>realce elástico</b> («elástico»: el neutrón vuelve a salir y el blanco queda igual), y la <b>corrección por fluctuaciones de anchura</b> traslada ese flujo de las otras puertas a la entrada.</p>
  <div class="ctl"><label for="dc-n">Otras puertas</label><input id="dc-n" type="range" data-bind="Nch" min="1" max="12" step="1" value="2" data-instant><output data-show="Nch" data-fmt="0"></output></div>
  <p>Añade puertas. Con muchas salidas su anchura total deja de fluctuar, las otras puertas vuelven a acercarse a la estimación simple, y la fracción de la entrada, aunque sigue multiplicada por dos o tres, es pequeña. La corrección importa más donde hay pocas puertas abiertas: cerca y por debajo de la energía de separación del neutrón. El motor la calcula con la fórmula de Moldauer, que promedia sobre estas estadísticas de anchuras.</p>
</div>
<div class="step">
  <h3>Lo que queda por repartir</h3>
  <p>La imagen muestra neutrones absorbidos que llegan por la izquierda. No todos forman un núcleo compuesto. Algunos dan un solo golpe rasante en la superficie y salen despedidos: las reacciones directas del Capítulo 3. Otros chocan una o dos veces y salen disparados: las emisiones de preequilibrio del Capítulo 4. Solo el resto se queda, reparte su energía y calienta el núcleo. Los contadores registran cada destino.</p>
  <div class="ctl"><label for="dc-einc">Energía del neutrón</label><input id="dc-einc" type="range" data-bind="Einc" min="1" max="30" step="0.5" value="8"><output data-show="Einc" data-fmt="1"></output></div>
  <p>Solo los que se quedan entran en la competición de puertas de arriba. Arrastra la energía del neutrón: a pocos MeV casi todos los neutrones se quedan; a 30 MeV cerca de la mitad ya se ha ido sin llegar nunca al equilibrio.</p>
  <div class="aside">En el código: <code>compound/prepare.py</code> (pesos de salida T·ρ por espín y paridad, reglas de selección), <code>compound/target.py</code> (primera desintegración con fluctuaciones de anchura), <code>compound/continuum.py</code> (desintegración de cada intervalo posterior), <code>compound/wfc.py</code> (correcciones de Moldauer, HRTW, GOE), <code>compound/normalization.py</code> (flujo que queda para el núcleo compuesto), <code>omp/inverse.py</code> (puertas al revés).</div>
</div>`,
};
(function () {
  const L = {
    "{#} MeV": "{#} MeV",
    "n": "n", "p": "p", "fission": "fisión",
    "heavy only": "solo pesados",
    "heavy nuclei only": "solo núcleos pesados",
    "shut below {#} MeV": "cerrada bajo {#} MeV",
    "the neutron door takes nearly everything": "la puerta del neutrón se lleva casi todo",
    "below the neutron threshold, nearly all decays emit light": "bajo el umbral del neutrón, casi todo emite luz",
    "the doors share the decays": "las puertas se reparten las desintegraciones",
    // hump
    "{#} MeV to spare": "{#} MeV disponibles",
    "door gap = T(ε)": "hueco = T(ε)",
    "doors: one per neutron energy ε, gap = T(ε)": "puertas: una por energía ε del neutrón, hueco = T(ε)",
    "× states left behind": "× estados restantes",
    "× states the leftover nucleus can be in: many after a slow neutron": "× estados posibles del núcleo restante: muchos tras un neutrón lento",
    "most ≈ {#} MeV": "máximo ≈ {#} MeV",
    "= the pile": "= el montón",
    "= where the neutrons land: the evaporation spectrum": "= donde caen los neutrones: el espectro de evaporación",
    "slow": "lentos",
    "slow neutrons": "neutrones lentos",
    "fast: {#} MeV →": "rápidos: {#} MeV →",
    "fast: {#} MeV (beyond, up to {#}, almost none)": "rápidos: {#} MeV (más allá, hasta {#}, casi ninguno)",
    "fast: {#}": "rápidos: {#}",
    "fast: {#} MeV, the neutron takes it all": "rápidos: {#} MeV, el neutrón se lo lleva todo",
    // coulomb
    "well ↓": "pozo ↓",
    "well (much deeper) ↓": "pozo (mucho más hondo) ↓",
    "hilltop ≈ {#} MeV": "cima ≈ {#} MeV",
    "falls as {#}/r": "cae como {#}/r",
    "Coulomb hill, falling as {#}/r": "colina de Coulomb, cae como {#}/r",
    "tunnel: wider than the picture": "túnel: más ancho que la imagen",
    "tunnel {#} fm": "túnel {#} fm",
    "proton energy {#} MeV": "energía del protón {#} MeV",
    "alpha energy {#} MeV": "energía de la alfa {#} MeV",
    "proton energy {#} MeV ↑": "energía del protón {#} MeV ↑",
    "alpha energy {#} MeV ↑": "energía de la alfa {#} MeV ↑",
    "above the hilltop: it rolls straight out": "sobre la cima: sale rodando directamente",
    "below the top, must tunnel: nearly every knock gets through": "bajo la cima, efecto túnel: pasa casi en cada golpe",
    "below the top, must tunnel: about {#} knock in {#} gets through": "bajo la cima, efecto túnel: pasa {#} golpe de cada {#}",
    "below the top, must tunnel: about {#} knock in {#} × {#}^{#} gets through": "bajo la cima, efecto túnel: pasa {#} golpe de cada {#} × {#}^{#}",
    "out": "fuera",
    "through after {#} knock": "atraviesa tras {#} golpe",
    "through after {#} knocks": "atraviesa tras {#} golpes",
    "knocks so far: {#}": "golpes hasta ahora: {#}",
    "distance r from the centre (fm) →": "distancia r al centro (fm) →",
    // spin
    "J = {#}/{#}, parity +": "J = {#}/{#}, paridad +",
    "l={#}": "l={#}",
    "leftover states by spin J′ →": "estados restantes por espín J′ →",
    "drawers: states of the leftover nucleus by spin J′ (faint: states it holds) →": "cajones: estados del núcleo restante por espín J′ (tenue: estados que guarda) →",
    "open doors reach {#} %": "las puertas abiertas alcanzan el {#} %",
    "open doors reach about {#} % of the states": "las puertas abiertas alcanzan cerca del {#} % de los estados",
    "● parity kept (even l)   ○ flipped (odd l)": "● l par: paridad igual   ○ l impar: invertida",
    // wfc
    "entrance x": "entrada x",
    "entrance, width x": "entrada, anchura x",
    "{#} other doors, y": "{#} otras puertas, y",
    "{#} other door, widths y": "{#} otra puerta, anchuras y",
    "{#} other doors, widths y": "{#} otras puertas, anchuras y",
    "back out the entrance: {#} of {#}": "de vuelta por la entrada: {#} de {#}",
    "out another door: {#}": "por otra puerta: {#}",
    // norm
    "absorbed neutrons, {#} MeV →": "neutrones absorbidos, {#} MeV →",
    "direct: {#} %": "directas: {#} %",
    "pre-equilibrium: {#} %": "preequilibrio: {#} %",
    "compound nucleus: {#} %": "núcleo compuesto: {#} %",
    "one glancing hit on the surface": "un golpe rasante en la superficie",
    "a knock or two, then out fast": "un choque o dos y sale rápido",
    "stayed: on to the door competition": "se queda: a la competición de puertas",
  };
  // door hint with level-count wording (fmt: "1", "N", "N thousand", "N million") and T possibly in e-notation
  const cnt = [["{#} state", "{#} estado"], ["{#} states", "{#} estados"], ["{#} thousand states", "{#} mil estados"], ["{#} million states", "{#} millones de estados"]];
  for (const [e, s] of cnt) {
    L[`weak door × ≈ ${e}`] = `puerta débil × ≈ ${s}`;
    L[`T ≈ {#} × ≈ ${e}`] = `T ≈ {#} × ≈ ${s}`;
    L[`T ≈ {#}e{#} × ≈ ${e}`] = `T ≈ {#}e{#} × ≈ ${s}`;
  }
  // share comparisons: each pct is "{#} %" or "≈ {#} %"
  const P = ["{#} %", "≈ {#} %"];
  for (const a of P) for (const b of P) {
    L[`back out ${a}, not ${b}: × {#}`] = `vuelven ${a}, no ${b}: × {#}`;
    L[`share back out: average of products ${a} · product of averages ${b} · × {#}`] = `de vuelta: promedio de productos ${a} · producto de promedios ${b} · × {#}`;
    L[`other doors ${a}, not ${b}`] = `otras puertas ${a}, no ${b}`;
    L[`other doors together: ${a} instead of ${b}`] = `otras puertas juntas: ${a} en vez de ${b}`;
  }
  Object.assign(WT.es.labels, L);
})();
