/* Spanish: fission (chapter 9) */
WT.es.ch.fission = {
  num: "Capítulo 9", title: "Partirse en dos", short: "Fisión",
  lead: "Los núcleos más pesados tienen una salida que a los ligeros les falta: en lugar de lanzar una partícula, el núcleo entero se rompe en dos. Esto es la fisión.",
  html: `
<div class="step">
  <p>La imagen muestra el núcleo como una gota de líquido cargado. La tensión superficial (flechas grises) la mantiene redonda; los protones, todos con carga positiva, se repelen entre sí y la empujan a separarse (flechas rojas). En un núcleo tan pesado como el uranio, las dos fuerzas están casi equilibradas.</p>
  <div class="ctl"><label for="fis-d">Estira la gota</label><input id="fis-d" type="range" data-bind="def" min="0" max="1" step="0.01" value="0"><output data-show="def" data-fmt="2"></output></div>
  <p>Arrastra para estirarla y observa el punto en la pequeña curva de abajo, la energía de la gota. Estirarla añade superficie, lo que cuesta energía, pero reparte la carga, lo que libera energía. Pasada la cima de la curva gana la carga: se forma un cuello y las dos mitades salen despedidas llevándose unos 200 MeV.</p>
</div>
<div class="step">
  <h3>El paisaje de las formas</h3>
  <p>La altura de la curva es la energía del núcleo para cada forma, desde redonda a la izquierda hasta partida a la derecha; la gotita que rueda por ella muestra cada forma. Una gota líquida lisa daría una sola colina. Pero los nucleones llenan los niveles de energía por grupos, llamados <b>capas</b>, y en los elementos más pesados esto excava un segundo valle en la colina. El resultado es una <b>barrera de doble joroba</b>: dos colinas con un pozo entre ellas, donde el núcleo puede quedarse un tiempo con forma estirada.</p>
  <p>El motor no da esta curva por supuesta. La lee punto a punto de un cálculo microscópico de la energía en cada deformación, es decir, en cada grado de estiramiento.</p>
</div>
<div class="step">
  <h3>Atravesar la colina por efecto túnel</h3>
  <p>La bola es el núcleo excitado en el primer valle, y la línea discontinua naranja es su energía de excitación. Por debajo de la cima, aquí unos 6 MeV, la física clásica dice que nunca puede llegar al otro lado. La mecánica cuántica le permite atravesar por <b>efecto túnel</b> la parte más oscura y prohibida de la colina, con una probabilidad <i>T</i> que cae exponencialmente a medida que esa parte se hace más gruesa.</p>
  <div class="ctl"><label for="fis-e">Energía de excitación</label><input id="fis-e" type="range" data-bind="E" min="3" max="8" step="0.05" value="5"><output data-show="E" data-fmt="2"></output></div>
  <p>Sube la energía y mira cómo <i>T</i> crece al adelgazarse la parte prohibida. El atajo de los libros de texto (Hill–Wheeler) trata la cima como una parábola, la curva azul discontinua. El motor sigue la forma real, que es más ancha más abajo, así que muy por debajo de la cima la probabilidad es menor de lo que dice la parábola. <i>K</i>, abajo, mide cuánta colina hay en medio.</p>
  <div class="formula">T = 1 / (1 + e<sup>2K</sup>),  K = ∫ √(2μ(V−E)) dβ / ħ</div>
</div>
<div class="step">
  <h3>Puertas en la cima</h3>
  <p>Las puertas que se alzan en la cima son los <b>estados de transición</b>: los estados cuánticos en los que puede estar el núcleo mientras está estirado sobre la barrera. Cada uno tiene un espín y una paridad (0⁺, 2⁻, …: cómo gira el estado y si se ve igual en un espejo), y cada uno actúa como una puerta: el ancho de su rendija iluminada indica cuánto está abierta. Un núcleo solo puede pasar por puertas con su mismo espín y paridad, y cada puerta se abre poco a poco a medida que la energía supera su altura.</p>
  <div class="ctl"><label for="fis-e2">Energía de excitación</label><input id="fis-e2" type="range" data-bind="E" min="3" max="8" step="0.05" value="5"><output data-show="E" data-fmt="2"></output></div>
  <div class="btns"><button class="btn ghost" data-act="jpAll">Cualquier espín</button><button class="btn ghost" data-act="jp0">Compuesto 0⁺</button><button class="btn ghost" data-act="jp1">Compuesto 1⁻</button></div>
  <p>Elige un espín y una paridad: solo cuentan las puertas que coinciden, y la apertura total baja. Más arriba, las puertas se apiñan en un <b>continuo</b> demasiado denso para enumerarlo, así que el motor usa su densidad, como hace con los niveles ordinarios.</p>
</div>
<div class="step">
  <h3>Dos colinas en serie</h3>
  <p>Ahora las dos colinas, cada una con su puerta (el círculo; su parte rellena indica cuánto está abierta). Los puntos son núcleos que llegan desde la izquierda. Los que cruzan la primera colina quedan atrapados en el pozo y rebotan entre las dos puertas hasta salir por un lado u otro. Las probabilidades se combinan como resistencias eléctricas en serie, así que la colina más difícil es la que más decide.</p>
  <div class="ctl"><label for="fis-b">Altura de la colina exterior</label><input id="fis-b" type="range" data-bind="Bb" min="3.5" max="7.5" step="0.05" value="5.6"><output data-show="Bb" data-fmt="2"></output></div>
  <div class="formula">1/T = 1/T<sub>A</sub> + 1/T<sub>B</sub></div>
  <p>Sube la colina exterior y mira cómo se estrangula el flujo hacia la fisión, por muy abierta que esté la puerta interior.</p>
</div>
<div class="step">
  <h3>Más de una oportunidad</h3>
  <p>La imagen sigue un núcleo cada vez. El uranio-238 absorbe el neutrón y se convierte en uranio-239 con energía de excitación <i>E</i>* (la línea discontinua). Intenta pasar la barrera. Si no se parte, puede lanzar un neutrón: eso cuesta energía, así que la línea baja, y el núcleo más ligero que queda, uranio-238, sigue caliente e intenta su propia barrera. Eso es la fisión de <b>segunda oportunidad</b>, escrita (n,n′f). Los montones de abajo recogen cómo terminó cada núcleo.</p>
  <div class="ctl"><label for="fis-en">Energía del neutrón</label><input id="fis-en" type="range" data-bind="En" min="0" max="25" step="0.1" value="7"><output data-show="En" data-fmt="1"></output></div>
  <p>Sube la energía y los intentos posteriores empiezan a tener éxito: una tercera oportunidad se abre cerca de 12 MeV. En la <b>sección eficaz de fisión</b> medida, la probabilidad de que el núcleo se parta, cada nueva oportunidad aparece como un escalón. El motor calcula con qué frecuencia se parte el núcleo, no en qué fragmentos.</p>
  <div class="aside">En el código: <code>fission/wkb.py</code> (el camino de energía de deformación y las integrales WKB), <code>fission/barriers.py</code> (Hill–Wheeler, estados de transición, la densidad de niveles en la barrera), <code>fission/transmission.py</code> (jorobas en serie, T<sub>fis</sub> por espín y paridad), <code>fission/chain.py</code> (barreras para cada núcleo de la cascada).</div>
</div>`,
};
Object.assign(WT.es.labels, {
  // drop
  "surface tension pulls it round": "la tensión superficial la redondea",
  "the protons push it apart": "los protones la separan",
  "a charged drop, nearly round": "una gota cargada, casi redonda",
  "stretched: more surface, charge further apart": "estirada: más superficie, carga más repartida",
  "a neck forms": "se forma un cuello",
  "two fragments, carrying about {#} MeV": "dos fragmentos, con unos {#} MeV",
  "energy of the drop": "energía de la gota",
  // landscape
  "ground state": "estado fundamental", "inner barrier": "barrera interior", "second well": "segundo pozo",
  "outer barrier": "barrera exterior", "split (scission)": "partida (escisión)", "one smooth hill": "una sola colina lisa",
  "shell effects carving the second well": "los efectos de capa excavan el segundo pozo",
  "round → stretched → necked → split": "redonda → estirada → con cuello → partida",
  "stretch (deformation) →": "estiramiento (deformación) →",
  // tunnel
  "forbidden zone": "zona prohibida",
  "excitation {#} MeV": "excitación {#} MeV",
  "hilltop {#} MeV": "cima {#} MeV",
  "parabola fit": "ajuste parabólico",
  "passes over the top": "pasa por encima de la cima",
  // gates
  "continuum: a density": "continuo: una densidad",
  "continuum of gates: counted as a density": "continuo de puertas: contado como densidad",
  "gates: transition states": "estados de transición",
  "E = {#} MeV": "E = {#} MeV",
  "all gates: total opening {#}": "todas las puertas: apertura total {#}",
  "all gates: total opening {#} + {#} from the continuum": "todas las puertas: apertura total {#} + {#} del continuo",
  "{#}⁺ gates only: total opening {#}": "solo puertas {#}⁺: apertura total {#}",
  "{#}⁺ gates only: total opening {#} + {#} from the continuum": "solo puertas {#}⁺: apertura total {#} + {#} del continuo",
  "{#}⁻ gates only: total opening {#}": "solo puertas {#}⁻: apertura total {#}",
  "{#}⁻ gates only: total opening {#} + {#} from the continuum": "solo puertas {#}⁻: apertura total {#} + {#} del continuo",
  // series
  "nuclei arriving →": "núcleos que llegan →",
  "trapped in the well": "atrapados en el pozo",
  "fission": "fisión",
  "so far: {#} through, {#} turned back": "hasta ahora: {#} pasan, {#} vuelven atrás",
  // chance
  "²³⁹U*  E* = {#} MeV": "²³⁹U*  E* = {#} MeV", "²³⁸U*  E* = {#} MeV": "²³⁸U*  E* = {#} MeV", "²³⁷U*  E* = {#} MeV": "²³⁷U*  E* = {#} MeV",
  "↑ E* above the picture": "↑ E* por encima del dibujo",
  "fission!": "¡fisión!",
  "emits a neutron, cools, tries again": "emite un neutrón, se enfría, lo intenta otra vez",
  "too cool to split: a photon, no fission": "demasiado frío para partirse: un fotón, sin fisión",
  "attempt {#}: barrier {#} % open": "intento {#}: barrera abierta al {#} %",
  "{#}st chance (n,f)": "{#}.ª oportunidad (n,f)", "{#}nd chance (n,n′f)": "{#}.ª oportunidad (n,n′f)", "{#}rd chance (n,{#}nf)": "{#}.ª oportunidad (n,{#}nf)",
  "{#}st (n,f)": "{#}.ª (n,f)", "{#}nd (n,n′f)": "{#}.ª (n,n′f)", "{#}rd (n,{#}nf)": "{#}.ª (n,{#}nf)",
  "no fission": "sin fisión",
});
// labels carrying a transmission T, printed either as 0.12 or as 3.4·10⁻5 (two number shapes)
(function () {
  const L = WT.es.labels, F = ["{#}", "{#}·{#}⁻{#}"];
  for (const a of F) {
    L[`inner gate T ≈ ${a}`] = `puerta interior T ≈ ${a}`;
    L[`outer gate T ≈ ${a}`] = `puerta exterior T ≈ ${a}`;
    L[`both hills: T ≈ ${a}, {#} % of what arrives gets through`] = `ambas colinas: T ≈ ${a}, pasa el {#} % de lo que llega`;
    for (const b of F) {
      L[`T ≈ ${a} real shape · ${b} parabola`] = `T ≈ ${a} forma real · ${b} parábola`;
      L[`chance to tunnel T ≈ ${a} on the real shape, ${b} on the parabola`] = `probabilidad de túnel T ≈ ${a} con la forma real, ${b} con la parábola`;
    }
  }
})();
