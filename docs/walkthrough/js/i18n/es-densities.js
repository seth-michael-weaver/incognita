/* Spanish: densities (Capítulo 24, experto: densidades de niveles, empalmadas) */
WT.L.ch.densities = {
  num: "Capítulo 24", title: "Densidades de niveles, empalmadas", short: "Densidades de niveles",
  lead: "El capítulo 8 unió un tablón recto a una ladera. Este capítulo escribe las dos, muestra cómo se encuentra el punto de unión a partir de los niveles contados y qué ocurre cuando no existe.",
  html: `
<div class="step">
  <h3>El gas de Fermi con efectos de capas amortiguados</h3>
  <p>La densidad de niveles por defecto del motor es la combinación de <b>Gilbert–Cameron</b>: un gas de Fermi a alta energía y una temperatura constante por debajo. El gas de Fermi necesita un solo número, el parámetro de densidad de niveles <i>a</i>, y a baja energía ese número nota las capas. La forma de <b>Ignatyuk</b> deja que la corrección de capas δW actúe por completo a baja excitación y se desvanezca con un ritmo de amortiguamiento γ, de modo que <i>a</i>(<i>U</i>) tiende al valor suave <i>ã</i> en cuanto el núcleo está caliente.</p>
  <div class="formula">a(U) = ã [1 + δW (1 − e<sup>−γU</sup>) / U] ,  ã = αA + βA<sup>2/3</sup> ,  γ = γ₁ / A<sup>1/3</sup></div>
  <div class="ctl"><label for="ld-dw">Corrección de capas δW (MeV)</label><input id="ld-dw" type="range" data-bind="dW" min="-6" max="4" step="0.1" value="1"><output data-show="dW" data-fmt="1"></output></div>
  <div class="formula">ρ<sub>F</sub>(E) = exp(2√(aU)) / (12√2 σ a<sup>1/4</sup> U<sup>5/4</sup>) ,  U = E − Δ ,  σ² = 0.01389 A<sup>5/3</sup> √(aU) / ã</div>
  <p>Las curvas de arriba son <i>a</i>(<i>U</i>)/<i>ã</i> para varios δW; la tuya, en negrita. Debajo está ln ρ<sub>F</sub>. Un δW negativo (una capa cerrada) reduce la densidad en uno o dos órdenes de magnitud, y esa reducción se desvanece solo despacio: <i>a</i>(<i>U</i>) vuelve a <i>ã</i> como δW/<i>U</i>, así que incluso a 20 MeV un δW de −6 MeV sigue costando un factor de unos 40. Δ es el desplazamiento por apareamiento, 12/√A por cada tipo de nucleón apareado.</p>
</div>
<div class="step">
  <h3>Una recta tangente por debajo</h3>
  <p>Por debajo de la energía de empalme <i>E<sub>x</sub></i>, el gas de Fermi se sustituye por la ley de <b>temperatura constante</b>. Dos condiciones fijan sus dos parámetros: igual valor e igual pendiente en <i>E<sub>x</sub></i>, así que la recta es la tangente a ln ρ<sub>F</sub> en ese punto.</p>
  <div class="formula">ρ<sub>T</sub>(E) = (1/T) e<sup>(E − E₀)/T</sup> ,  1/T = d ln ρ<sub>F</sub>/dE |<sub>E<sub>x</sub></sub> ,  E₀ = E<sub>x</sub> − T ln[T ρ<sub>F</sub>(E<sub>x</sub>)]</div>
  <div class="ctl"><label for="ld-ex">Energía de empalme Eₓ (MeV)</label><input id="ld-ex" type="range" data-bind="Ex" min="4.6" max="14" step="0.05" value="7"><output data-show="Ex" data-fmt="2"></output></div>
  <p>Desliza <i>E<sub>x</sub></i> y la tangente gira: un empalme más alto da una <i>T</i> mayor (una recta más plana) y un <i>E</i>₀ menor. Cualquier <i>E<sub>x</sub></i> da una curva suave. Los niveles contados deciden cuál es la correcta.</p>
</div>
<div class="step">
  <h3>Encontrar el empalme a partir de los niveles contados</h3>
  <p>La escalera es el número de niveles conocidos por debajo de <i>E</i>, en escala logarítmica. La ley de temperatura constante se integra en una recta, <i>N</i>(<i>E</i>) = e<sup>(E − E₀)/T</sup> + const, que debe reproducir el recuento entre el nivel <i>N<sub>L</sub></i> y el nivel <i>N<sub>P</sub></i>, el tramo del esquema que se considera completo. Es una ecuación para la única incógnita <i>E<sub>x</sub></i>.</p>
  <div class="formula">F(E<sub>x</sub>) = e<sup>(E<sub>P</sub>−E₀)/T</sup> − e<sup>(E<sub>L</sub>−E₀)/T</sup> − (N<sub>P</sub> − N<sub>L</sub>) = 0</div>
  <div class="ctl"><label for="ld-ex2">Eₓ de prueba (MeV)</label><input id="ld-ex2" type="range" data-bind="Ex" min="4.6" max="14" step="0.05" value="7"><output data-show="Ex" data-fmt="2"></output></div>
  <p>El panel inferior es <i>F</i>. El motor, como TALYS, recorre un intervalo en 100 pasos en busca de un cambio de signo y luego lo biseca; el corchete que se estrecha muestra la bisección. Donde <i>F</i> = 0, la recta de prueba se apoya sobre la escalera.</p>
</div>
<div class="step">
  <h3>Cuando no hay empalme</h3>
  <p>A veces las dos curvas no pueden unirse con suavidad. En un núcleo con capas cerradas tanto de protones como de neutrones, como el plomo-208, el gas de Fermi queda tan deprimido que ninguna recta tangente toca los niveles contados: no hay energía de empalme. El código recurre entonces a reglas prácticas para la temperatura y para el empalme. Las dos piezas siguen encontrándose, pero con un pliegue: los valores coinciden y las pendientes no.</p>
  <div class="btns"><button class="btn ghost" data-act="tang" aria-pressed="false">Tangente en la energía empírica</button></div>
  <p>Pulsa el botón para ver en su lugar la tangente suave. Con la entrada por defecto el pliegue aparece en siete núcleos en torno al plomo, y eliminarlo cambia su captura de neutrones hasta en un 20 a 30 %. INCOGNITA reproduce aquí a TALYS; el cambio se ha comunicado a los desarrolladores de TALYS.</p>
  <div class="aside">Los detalles: en un núcleo doblemente mágico el gas de Fermi a baja energía se mantiene frío en todas partes, y <i>F</i> nunca cambia de signo. TALYS toma entonces la temperatura empírica <i>T</i> = −0,25 + 10,2/√(<i>A</i>(1 + γδW)) y busca la energía en la que el gas de Fermi tiene esa temperatura. Cerca de un núcleo doblemente mágico solo la alcanza muy por encima de cualquier empalme razonable, o nunca, así que el empalme también recurre a sistemáticas, <i>E<sub>x</sub></i> = 2,33 + 253/<i>A</i> + Δ, y <i>E</i>₀ se fija para que el valor sea continuo. La <i>T</i> empírica no es la temperatura del gas de Fermi a esa energía, así que la pendiente da un salto: con la entrada por defecto, en ²⁰⁵,²⁰⁶Tl, ²⁰⁶⁻²⁰⁹Pb y ²¹⁰Bi, del 34 al 62 %. Tomar ahí <i>T</i> del gas de Fermi, como TALYS ya hace cuando <i>E<sub>x</sub></i> se da en la entrada, recupera la tangente. La imagen es una ilustración de un núcleo parecido al plomo, con <i>ã</i> aumentada un 30 % para que su gas de Fermi quede por debajo de la temperatura empírica hasta unos 24 MeV, más allá de la búsqueda; su pendiente salta un 62 %.</div>
</div>
<div class="step">
  <h3>El espaciado D₀ como comprobación</h3>
  <p>A la energía de separación del neutrón la densidad se mide directamente: el espaciado medio <i>D</i>₀ de las resonancias de onda s cuenta los estados del único espín y paridad que puede alcanzar un neutrón lento. Para un blanco de espín 0 es solo <i>J</i><sup>π</sup> = ½⁺.</p>
  <div class="formula">1/D₀ = ρ(S<sub>n</sub>, ½, +) = ½ ρ<sub>F</sub>(S<sub>n</sub>) · (2J+1)/(2σ²) · e<sup>−(J+½)²/2σ²</sup></div>
  <div class="ctl"><label for="ld-as">Escala sobre ã</label><input id="ld-as" type="range" data-bind="as" min="0.8" max="1.2" step="0.005" value="1"><output data-show="as" data-fmt="3"></output></div>
  <p>La imagen corresponde a un núcleo compuesto parecido al hierro-57 con la <i>ã</i> global, frente al valor medido de 25,4 ± 2,2 keV. Un pequeño tanto por ciento en <i>ã</i> mueve <i>D</i>₀ decenas de por ciento, así que donde <i>D</i>₀ está medido la densidad en <i>S<sub>n</sub></i> queda bien fijada, y donde no lo está es la mayor fuente individual de incertidumbre en la captura. Las evaluaciones ajustan <i>a</i> a <i>D</i>₀, y también lo hace el cálculo por defecto de TALYS, que el motor sigue: para un núcleo con <i>D</i>₀ medido lee un parámetro de densidad de niveles ajustado a él, y usa la fórmula global solo para los demás.</p>
  <div class="aside">En el código: <code>density/parameters.py</code> (ã, amortiguamiento de Ignatyuk, apareamiento, corte de espín), <code>density/models.py</code> (gas de Fermi, temperatura constante, tablas), <code>density/matching.py</code> (la raíz del empalme, el recurso empírico, los detalles de precisión simple del propio TALYS reproducidos). La imagen usa los parámetros globales de TALYS para ldmodel 1 con esquemas de niveles y correcciones de capas ilustrativos (y, para el caso parecido al plomo, <i>ã</i> × 1,3); el <i>D</i>₀ medido es el valor de RIPL para el ⁵⁷Fe.</div>
</div>`,
};
(function () {
  const L = {
    "E (MeV)": "E (MeV)", "U (MeV)": "U (MeV)", "Eₓ (MeV)": "Eₓ (MeV)", "{#} keV": "{#} keV",
    // scene 1: Ignatyuk and the Fermi gas
    "a(U) / ã": "a(U) / ã",
    "U = {#} MeV · a = {#} MeV⁻¹ · T ≈ √(U/a) = {#} MeV": "U = {#} MeV · a = {#} MeV⁻¹ · T ≈ √(U/a) = {#} MeV",
    "ρ_F (states per MeV), A = {#}": "ρ_F (estados por MeV), A = {#}",
    "dashed: δW = {#}": "discontinua: δW = {#}",
    "at {#} MeV: ×{#} against δW = {#}": "a {#} MeV: ×{#} frente a δW = {#}",
    "at {#} MeV: ×{#}e{#} against δW = {#}": "a {#} MeV: ×{#}e{#} frente a δW = {#}",
    // scene 2: the tangent
    "T = {#} MeV": "T = {#} MeV",
    "× e": "× e",
    "joint Eₓ = {#} MeV": "empalme Eₓ = {#} MeV",
    "E₀ = {#} MeV": "E₀ = {#} MeV",
    "Fermi gas": "gas de Fermi",
    "constant temperature": "temperatura constante",
    "ln ρ (states per MeV), A = {#}": "ln ρ (estados por MeV), A = {#}",
    // scene 3: the root
    "levels {#}–{#}": "niveles {#}–{#}",
    "levels {#} to {#}: taken as complete": "niveles {#} a {#}: se toman como completos",
    "number of levels below E": "número de niveles por debajo de E",
    "trial Eₓ = {#} MeV: the line gives {#} levels for {#} counted": "Eₓ de prueba = {#} MeV: la recta da {#} niveles frente a {#} contados",
    "F = {#}": "F = {#}",
    "F(Eₓ): predicted minus counted (signed log scale)": "F(Eₓ): predicho menos contado (escala log con signo)",
    "bisection step {#}: [{#}, {#}]": "paso de bisección {#}: [{#}; {#}]",
    "root Eₓ = {#} MeV": "raíz Eₓ = {#} MeV",
    // scene 4: no joint
    "below: {#}/T with T = {#} MeV (Fermi-gas T)": "por debajo: {#}/T con T = {#} MeV (T del gas de Fermi)",
    "below: {#}/T with T = {#} MeV (empirical T)": "por debajo: {#}/T con T = {#} MeV (T empírica)",
    "above: Fermi gas, T = {#} MeV": "por encima: gas de Fermi, T = {#} MeV",
    "slope jumps by {#} % at Eₓ = {#} MeV": "la pendiente salta un {#} % en Eₓ = {#} MeV",
    "tangent at Eₓ = {#} MeV: no jump": "tangente en Eₓ = {#} MeV: sin salto",
    "ln ρ, lead-like nucleus (A = {#}, δW = {#} MeV)": "ln ρ, núcleo parecido al plomo (A = {#}, δW = {#} MeV)",
    "F changes sign: a root exists": "F cambia de signo: existe una raíz",
    "F(Eₓ) never reaches zero: no matching energy": "F(Eₓ) nunca llega a cero: no hay energía de empalme",
    // scene 5: D0
    "measured {#} ± {#} keV": "medido {#} ± {#} keV",
    "computed D₀ = {#} keV": "D₀ calculado = {#} keV",
    "ã × {#} = {#} MeV⁻¹ · σ² = {#} · ρ(Sₙ) = {#} per MeV": "ã × {#} = {#} MeV⁻¹ · σ² = {#} · ρ(Sₙ) = {#} por MeV",
    "ã × {#} = {#} MeV⁻¹ · σ² = {#} · ρ(Sₙ) = {#}e{#} per MeV": "ã × {#} = {#} MeV⁻¹ · σ² = {#} · ρ(Sₙ) = {#}e{#} por MeV",
    "s-wave resonances above Sₙ, {#} keV shown: about {#} levels": "resonancias de onda s por encima de Sₙ, {#} keV representados: unos {#} niveles",
    // "iron-57-like": the number is read as −57 and put back with its hyphen
    "iron{#}-like compound nucleus, Sₙ = {#} MeV, spin and parity ½⁺": "núcleo compuesto parecido al hierro{#}, Sₙ = {#} MeV, espín y paridad ½⁺",
  };
  Object.assign(WT.L.labels, L);
})();
Object.assign(WT.L.glossary, {
  gilbertCameron: {
    term: "Gilbert–Cameron", aliases: ["Gilbert–Cameron", "Gilbert-Cameron"],
    short: "Una densidad de niveles compuesta: una ley de temperatura constante a baja energía unida al gas de Fermi por encima de una energía de empalme, con igual valor e igual pendiente en la unión.",
    more: "La propusieron A. Gilbert y A. G. W. Cameron en 1965. Es la opción por defecto de TALYS y del motor (ldmodel 1), con el parámetro de densidad de niveles dependiente de la energía de Ignatyuk.",
    chapter: "densities",
  },
  ignatyuk: {
    term: "Ignatyuk", aliases: ["Ignatyuk"],
    short: "La forma de Ignatyuk del parámetro de densidad de niveles: la corrección de capas actúa por completo a baja excitación y se desvanece con la energía, de modo que a(U) tiende a su valor suave.",
    formula: "a(U) = ã [1 + δW (1 − e^(−γU)) / U]",
    chapter: "densities",
  },
});
/* attributes referenced in the English chapter script (for the structure check): data-act="tang" */
