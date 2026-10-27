/* Spanish: exciton (Capítulo 20, experto: el modelo de excitones, en números) */
WT.L.ch.exciton = {
  num: "Capítulo 20", title: "El modelo de excitones, en números", short: "Modelo de excitones",
  lead: "El capítulo 4 siguió a un neutrón rápido a través de unas pocas colisiones. Aquí están las tasas que deciden, en cada etapa, si lo siguiente es otra colisión o una fuga, y el espectro que resulta de sumarlas.",
  html: `
<div class="step">
  <h3>Contar estados partícula–hueco</h3>
  <p>El modelo de excitones clasifica el núcleo en su camino hacia el equilibrio por su número de partículas excitadas <i>p</i> y de huecos <i>h</i>, <i>n</i> = <i>p</i> + <i>h</i>. Un neutrón que entra en un blanco empieza con <i>p</i> = 1, <i>h</i> = 0; cada colisión añade un par. Lo que importa en cada etapa es de cuántas formas puede repartirse la energía entre los <i>n</i> excitones: la densidad de estados partícula–hueco.</p>
  <div class="formula">ω(p,h,E) = g<sup>n</sup> (E − A<sub>p,h</sub>)<sup>n−1</sup> / (p! h! (n−1)!) ,  A<sub>p,h</sub> = max(p,h)²/g − (p² + h² + p + h)/4g</div>
  <div class="ctl"><label for="ex-n">Partículas p (huecos p − 1)</label><input id="ex-n" type="range" data-bind="pp" min="2" max="6" step="1" value="3" data-instant><output data-show="pp" data-fmt="0"></output></div>
  <div class="btns"><button class="btn ghost" data-act="pauli" aria-pressed="true">Corrección de Pauli</button></div>
  <p><i>g</i> ≈ <i>A</i>/15 MeV⁻¹ es la densidad de niveles de una partícula cerca de la energía de Fermi. <i>A<sub>p,h</sub></i> es la corrección de <b>Pauli</b>: dos partículas no pueden compartir un nivel, así que las configuraciones más bajas cuestan energía y la densidad cerca del umbral cae. El esquema muestra una configuración cada vez con la <i>p</i> elegida, sorteada al azar.</p>
</div>
<div class="step">
  <h3>Ir más hondo o salir</h3>
  <p>Desde cada etapa pueden pasar dos cosas. Una colisión crea otro par, con la tasa λ<sup>+</sup>, que por la regla de oro de Fermi es el elemento de matriz al cuadrado por la densidad de estados que puede alcanzar. O una partícula sale, con la tasa <i>W</i>, que da el balance detallado a partir de la sección eficaz inversa y del cociente de densidades de estados con y sin la partícula que escapa.</p>
  <div class="formula">λ<sup>+</sup>(n) = (2π/ħ) M² ω<sub>acc</sub> ,  W(p,h,ε) = (2s+1)/(π²ħ³) με σ<sub>inv</sub>(ε) ω(p−1,h,U) / ω(p,h,E)</div>
  <div class="ctl"><label for="ex-e">Energía del neutrón (MeV)</label><input id="ex-e" type="range" data-bind="Ein" min="5" max="60" step="0.5" value="20"><output data-show="Ein" data-fmt="1"></output></div>
  <p>Las barras son las dos tasas en cada etapa, en escala logarítmica: λ<sup>+</sup> del orden de 10²² s⁻¹, <i>W</i> alrededor de una décima parte en la primera etapa y menor en cada etapa siguiente, porque cada par nuevo reduce la energía que puede llevarse la partícula más energética. El motor toma M² de la forma de Koning–Duijvestijn, que disminuye con la energía por excitón:</p>
  <div class="formula">M² = (C₁ A<sub>p</sub> / A³) · [7.48 + 4.62×10⁵ / (E/(n A<sub>p</sub>) + 10.7)³]  MeV²</div>
</div>
<div class="step">
  <h3>La cadena en el tiempo</h3>
  <p>Si se desprecian las colisiones poco frecuentes que eliminan un par (la aproximación de no retorno, never-come-back), las poblaciones obedecen una cadena sencilla: cada etapa se llena desde la anterior y se vacía hacia la siguiente y hacia el continuo. Las barras resuelven esa ecuación maestra; el tiempo está en unidades de 10⁻²² s.</p>
  <div class="formula">dP(n)/dt = λ<sup>+</sup>(n−2) P(n−2) − [λ<sup>+</sup>(n) + W(n)] P(n)</div>
  <div class="ctl"><label for="ex-e2">Energía del neutrón (MeV)</label><input id="ex-e2" type="range" data-bind="Ein" min="5" max="60" step="0.5" value="20"><output data-show="Ein" data-fmt="1"></output></div>
  <p>Toda la cadena termina en unos pocos 10⁻²² s. La parte que escapa por el camino es la emisión de preequilibrio; el resto, tras un máximo de seis partículas en el motor, como en TALYS, pasa al núcleo compuesto. La integración en el tiempo da a cada etapa un peso τ(<i>n</i>)·<i>P</i>(<i>n</i>), y ese producto es lo que calcula el motor.</p>
</div>
<div class="step">
  <h3>De dónde sale la cola dura</h3>
  <p>El espectro de emisión es la suma sobre etapas de la población por la vida media por la tasa de emisión, más la evaporación de lo que queda. La etapa <i>n</i> = 3 por sí sola, dos partículas y un hueco, llega a las energías de salida más altas: su espectro solo cae linealmente hacia el punto final. Cada etapa posterior es más blanda.</p>
  <div class="formula">dσ/dε = σ<sub>CN</sub> Σ<sub>n</sub> P(n) τ(n) W(n,ε) + evaporación</div>
  <div class="ctl"><label for="ex-e3">Energía del neutrón (MeV)</label><input id="ex-e3" type="range" data-bind="Ein" min="5" max="60" step="0.5" value="20"><output data-show="Ein" data-fmt="1"></output></div>
  <p>Sube la energía y el espectro se endurece: la cola de preequilibrio se estira hasta el punto final mientras la joroba de evaporación se queda en 1 a 2 MeV. Por encima de unos 10 MeV, los neutrones de alta energía medidos solo se reproducen con esta cola.</p>
</div>
<div class="step">
  <h3>Qué fracción</h3>
  <p>La fracción de la emisión que es de preequilibrio crece con la energía incidente, desde un pequeño tanto por ciento cerca de 5 MeV hasta cerca del 40 % a 40 MeV aquí. Depende de una sola constante ajustable, el tamaño global del elemento de matriz: una interacción más débil supone un equilibrado más lento y más emisión temprana.</p>
  <div class="ctl"><label for="ex-c">Constante del elemento de matriz C₁</label><input id="ex-c" type="range" data-bind="c1" min="0.3" max="3" step="0.05" value="1"><output data-show="c1" data-fmt="2"></output></div>
  <p>La curva discontinua es C₁ = 1, el valor por defecto del motor; la continua sigue al control. Reducir C₁ a la mitad multiplica la fracción por 1,5 a 1,9, no por 2: la probabilidad de escape de cada etapa es W/(λ<sup>+</sup> + W), no W/λ<sup>+</sup>, y menos núcleos sobreviven hasta las etapas posteriores.</p>
</div>
<div class="step">
  <h3>Dos componentes y una segunda fuga</h3>
  <p>El motor sigue protones y neutrones por separado (<i>p</i><sub>π</sub>, <i>h</i><sub>π</sub>, <i>p</i><sub>ν</sub>, <i>h</i><sub>ν</sub>), con elementos de matriz distintos para pares de nucleones iguales y distintos, una profundidad de pozo reducida para la primera colisión cerca de la superficie y las reglas de Kalbach para los agregados. Por encima de 20 MeV deja también que el núcleo residual, que todavía contiene excitones, emita una segunda partícula rápida antes de equilibrarse.</p>
  <div class="ctl"><label for="ex-e4">Energía del neutrón (MeV)</label><input id="ex-e4" type="range" data-bind="Ein" min="5" max="60" step="0.5" value="20"><output data-show="Ein" data-fmt="1"></output></div>
  <p>La curva es una versión de juguete de eso: tras una primera emisión desde la etapa de tres excitones, la probabilidad de que la partícula sobrante del residual escape antes de su siguiente colisión. Es pequeña por debajo de 20 MeV y crece por encima, que es donde el motor activa el preequilibrio múltiple.</p>
  <div class="aside">En el código: <code>density/particle_hole.py</code> (densidades de Williams, correcciones de Pauli y de pozo finito, una y dos componentes), <code>preeq/exciton.py</code> (elementos de matriz, tasas de emisión y de transición, vidas medias, la solución de no retorno), <code>preeq/complex.py</code> (pickup, stripping y knockout de Kalbach), <code>preeq/multi.py</code> (preequilibrio múltiple, desde 20 MeV por defecto). La imagen es de una componente, con una sección eficaz inversa esquemática, para un blanco parecido al hierro-56.</div>
</div>`,
};
(function () {
  const L = {
    "E (MeV)": "E (MeV)", "{#} MeV": "{#} MeV", "n = {#}": "n = {#}",
    // scene 1: state densities
    "ω(p, h, E) per MeV": "ω(p, h, E) por MeV",
    "{#}p{#}h": "{#}p{#}h",
    "dashed: no Pauli correction": "discontinua: sin corrección de Pauli",
    "Fermi level": "nivel de Fermi",
    "{#} particles, {#} holes": "{#} partículas, {#} huecos",
    // scene 2: rates
    "rate (s⁻¹)": "tasa (s⁻¹)",
    "W/λ⁺ = {#}": "W/λ⁺ = {#}",
    "blue: λ⁺, the next collision · yellow: W, neutron escape": "azul: λ⁺, la siguiente colisión · amarillo: W, fuga del neutrón",
    "E = {#} + Sₙ = {#} MeV · τ(n={#}) = {#} × {#}⁻²² s": "E = {#} + Sₙ = {#} MeV · τ(n={#}) = {#} × {#}⁻²² s",
    // scene 3: the chain in time
    "compound": "compuesto",
    "emitted before equilibrium: {#} % (of {#} % in the end)": "emitido antes del equilibrio: {#} % (de un {#} % al final)",
    "t = {#} × {#}⁻²² s": "t = {#} × {#}⁻²² s",
    // scene 4: spectrum
    "outgoing neutron energy ε (MeV)": "energía del neutrón saliente ε (MeV)",
    "dσ/dε (mb/MeV)": "dσ/dε (mb/MeV)",
    "evaporation": "evaporación",
    "ε = {#} MeV: {#} % from n = {#}": "ε = {#} MeV: {#} % de n = {#}",
    "pre-equilibrium {#} % of the emission · solid: total": "preequilibrio: {#} % de la emisión · continua: total",
    // scene 5: share
    "pre-equilibrium share of the emission": "fracción de preequilibrio en la emisión",
    "{#} MeV: {#} %": "{#} MeV: {#} %",
    "C₁ = {#} (dashed: {#})": "C₁ = {#} (discontinua: {#})",
    // scene 6: second escape
    "{#} MeV: multiple pre-equilibrium on": "{#} MeV: se activa el preequilibrio múltiple",
    "chance of a second fast emission (toy estimate)": "probabilidad de una segunda emisión rápida (estimación de juguete)",
    "residual: {#}p{#}h": "residual: {#}p{#}h",
  };
  Object.assign(WT.L.labels, L);
})();
Object.assign(WT.L.glossary, {
  neverComeBack: {
    term: "Aproximación de no retorno (never-come-back)", aliases: ["aproximación de no retorno", "never-come-back"],
    short: "La aproximación de que, al principio del equilibrado, las colisiones solo añaden pares partícula–hueco y nunca los eliminan.",
    more: "Convierte la ecuación maestra en una cadena sencilla que puede integrarse etapa a etapa. Es válida mientras el número de excitones esté muy por debajo de su valor de equilibrio, que es donde ocurre la emisión de preequilibrio.",
    chapter: "exciton",
  },
});
