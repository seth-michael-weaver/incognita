/* Spanish: decay (Capítulo 9) */
WT.es.ch.decay = {
  num: "Capítulo 9", title: "Desintegración del núcleo compuesto", short: "Desintegración",
  lead: "El núcleo compuesto tiene que soltar su energía emitiendo una partícula o un fotón. Este capítulo dibuja cada salida como una puerta. El trabajo del motor es decir qué parte del flujo (la corriente de reacciones que llega aquí) sale por cada puerta.",
  html: `
<div class="step">
  <p>Una puerta por salida: un <em class="g">fotón</em> (γ), un <em class="n">neutrón</em> (n), un <em class="p">protón</em> (p), una <em class="a">partícula alfa</em> (α: dos protones y dos neutrones) y, solo en núcleos pesados, la <em class="f">fisión</em> (partirse en dos). El hueco iluminado de cada puerta es la fracción de esa salida, y las bolas salen al mismo ritmo; las puertas grises están cerradas. Como ha olvidado cómo se formó, el núcleo usa cada puerta b en proporción a un peso:</p>
  <div class="formula">fracción<sub>b</sub> = T<sub>b</sub> · ρ<sub>b</sub> / Σ<sub>c</sub> T<sub>c</sub> · ρ<sub>c</sub></div>
  <p>El <b>coeficiente de transmisión</b> <i>T</i> es la probabilidad de que una partícula que llega al borde lo atraviese; para las partículas sale del modelo óptico del Capítulo 5, aplicado al revés. La <b>densidad de niveles</b> ρ, escrita junto a cada puerta, cuenta los estados en los que puede acabar el núcleo restante. Repartir según <i>T</i> por ρ es la regla de <b>Hauser–Feshbach</b>. A 10 MeV la puerta del neutrón se lleva casi todo.</p>
</div>
<div class="step">
  <h3>Espectros de evaporación</h3>
  <p>La puerta del neutrón, dividida según la energía de salida ε (lentos a la izquierda, rápidos a la derecha). El hueco <i>T</i>(ε) de cada puerta se ensancha para los más rápidos. Debajo está la multitud de estados en los que puede quedar el núcleo restante: un neutrón lento deja atrás casi toda la energía, donde los estados abundan, así que las multitudes menguan hacia la derecha.</p>
  <div class="ctl"><label for="dc-sp">Energía disponible</label><input id="dc-sp" type="range" data-bind="spare" min="1" max="12" step="0.5" value="5"><output data-show="spare" data-fmt="1"></output></div>
  <p>Puerta × multitud convierte el montón en una joroba, el <b>espectro de evaporación</b>, como el vapor que escapa de un líquido caliente. Arrastra la energía disponible (en MeV, millones de electronvoltios): el montón vuelve a empezar y su pico se queda cerca de 1 MeV, fijado por la temperatura nuclear. La energía extra sobre todo calienta más al núcleo restante.</p>
</div>
<div class="step">
  <h3>La barrera de Coulomb en la emisión</h3>
  <p>La energía de un protón a cada distancia r del centro: un pozo dentro y, fuera, una colina debida a la repulsión eléctrica (de Coulomb), que decae como 1/r. Por debajo de la cima el protón, que rebota en el pozo, solo puede atravesar por <b>efecto túnel</b> el tramo sombreado, un efecto cuántico que funciona una vez de cada muchos golpes contra la pared. Las probabilidades se calculan como en el capítulo 4: cuanto más ancho y alto es el tramo, más ceros hay en «1 golpe de cada 10<sup>N</sup>».</p>
  <div class="ctl"><label for="dc-ce">Energía de la partícula</label><input id="dc-ce" type="range" data-bind="eps" min="0.5" max="12" step="0.1" value="3"><output data-show="eps" data-fmt="1"></output></div>
  <div class="btns"><button class="btn ghost" data-act="toggleAlpha">Cambiar protón / alfa</button></div>
  <p>Baja la energía y mira cómo se ensancha el túnel; luego cambia a la alfa, cuyas dos cargas se enfrentan a una colina unas dos veces más alta. Por eso los neutrones, sin carga, suelen ganar en cuanto pueden salir, y las salidas de protón y alfa importan sobre todo en núcleos ligeros y a energías altas.</p>
</div>
<div class="step">
  <h3>Umbrales de los canales</h3>
  <p>Cada puerta de partícula se abre solo por encima de su <b>energía de separación</b>, lo que cuesta arrancar esa partícula: aquí 8 MeV para un neutrón, 9 para un protón, 7 para una alfa. Por debajo de los 8 MeV del neutrón, casi todas las desintegraciones emiten luz.</p>
  <div class="ctl"><label for="dc-e">Energía de excitación</label><input id="dc-e" type="range" data-bind="E" min="5" max="24" step="0.1" value="7"><output data-show="E" data-fmt="1"></output></div>
  <p>Arrastra la energía de excitación más allá de 8 MeV. En cerca de 1 MeV la puerta del neutrón se abre de par en par y la fracción del fotón cae cien veces. La puerta de la alfa se desbloquea primero, a 7 MeV, pero apenas se abre: su colina de Coulomb (capítulo 4) la mantiene casi cerrada hasta bastante más arriba. La puerta del protón se desbloquea a 9 MeV y también sigue estrecha, frenada por su propia colina.</p>
</div>
<div class="step">
  <h3>Conservación del momento angular y de la paridad</h3>
  <p>El núcleo compuesto (arriba) tiene espín <i>J</i>; debajo, los estados del núcleo restante están en cajones según su espín <i>J</i>′. El neutrón se lleva la diferencia de espín y paridad: si sale con momento angular orbital <i>l</i>, cambia el espín hasta <i>l</i> + ½ e invierte la paridad cuando <i>l</i> es impar. Mayor <i>l</i> significa puerta más estrecha; la puerta de cada cajón es la de menor <i>l</i> que lo alcanza. Las caídas macizas conservan la paridad; las huecas la invierten.</p>
  <div class="ctl"><label for="dc-j">Espín compuesto J</label><input id="dc-j" type="range" data-bind="J" min="0" max="10" step="1" value="2" data-instant><output id="dc-jout">5/2</output></div>
  <p>Sube <i>J</i>. Las puertas abiertas se desplazan hacia los cajones de espín alto, que guardan pocos estados, mientras los cajones llenos quedan tras puertas cerradas. Un núcleo compuesto de espín alto tarda en emitir partículas, lo que da su oportunidad a los fotones y a los isómeros (estados de vida larga, Capítulo 10).</p>
</div>
<div class="step">
  <h3>Realce elástico</h3>
  <p>A baja energía el núcleo compuesto es un conjunto de <b>resonancias</b> estrechas, energías en las que el neutrón se absorbe con facilidad; se dibujan ocho, una por fila. Cada una tiene anchuras de puerta al azar: la entrada (el canal del neutrón) a la izquierda, de anchura <i>x</i>, y las demás puertas, aquí sobre todo fotones, a la derecha, de anchuras <i>y</i>.</p>
  <div class="btns"><button class="btn" data-act="fire">Lanzar 40 neutrones</button><button class="btn ghost" data-act="reroll">Nuevas resonancias</button></div>
  <p>Pulsa Lanzar y sigue a los neutrones. Un neutrón entra en una fila en proporción a la anchura de entrada <i>x</i> de esa fila. Una vez dentro, elige una salida en proporción a las anchuras: de vuelta por la entrada con probabilidad <i>x</i> / (<i>x</i> + Σ<i>y</i>), y si no, por una de las otras puertas. Las bandejas cuentan adónde fueron.</p>
  <p>El truco: una fila con entrada ancha recibe más neutrones y también devuelve más. Así que vuelven más de los que se adivinaría solo con las anchuras promedio. La fracción real que vuelve a salir (un <b>promedio de productos</b>) supera a la estimación simple (un <b>producto de promedios</b>); ambas están escritas arriba.</p>
  <p>Su cociente es el <b>realce elástico</b>. La <b>corrección por fluctuaciones de anchura</b> del motor lo aplica: traslada ese flujo extra de las otras puertas de vuelta a la entrada.</p>
  <div class="ctl"><label for="dc-n">Otras puertas</label><input id="dc-n" type="range" data-bind="Nch" min="1" max="12" step="1" value="2" data-instant><output data-show="Nch" data-fmt="0"></output></div>
  <p>Añade puertas. Con muchas salidas su anchura total deja de fluctuar, así que la corrección importa sobre todo donde hay pocas puertas abiertas. El motor la aplica, con la fórmula de Moldauer, a neutrones incidentes hasta la energía de separación del neutrón del blanco, y la omite por encima.</p>
</div>
<div class="step">
  <h3>Flujo tras las reacciones directas</h3>
  <p>Las puertas de este capítulo solo reparten los neutrones que de verdad se quedaron. Los capítulos 6 y 7 ya se llevaron su parte: algunos neutrones dan un golpe rasante y salen despedidos (directas), otros chocan una o dos veces y salen disparados (preequilibrio). Solo el resto se queda dentro y calienta el núcleo. Los contadores de la derecha registran cada destino; los que se quedan nunca salen del núcleo, solo se cuentan.</p>
  <div class="ctl"><label for="dc-einc">Energía del neutrón</label><input id="dc-einc" type="range" data-bind="Einc" min="1" max="30" step="0.5" value="8"><output data-show="Einc" data-fmt="1"></output></div>
  <p>Solo los que se quedan entran en la competición de puertas. Arrastra la energía del neutrón: a pocos MeV casi todos se quedan; a 30 MeV cerca de la mitad se ha ido antes de llegar al equilibrio.</p>
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

Object.assign(WT.L.labels, {
  "press Fire to send neutrons in": "pulsa Disparar para enviar neutrones",
  "stayed inside: counted here, not moved": "se quedó dentro: contado aquí, no movido",
});
