/* Spanish: hauser (Capítulo 22, experto: Hauser–Feshbach canal a canal, con fluctuaciones de anchura) */
WT.L.ch.hauser = {
  num: "Capítulo 22", title: "Hauser–Feshbach, canal a canal", short: "Hauser–Feshbach",
  lead: "El capítulo 9 contó la competición entre salidas como puertas. Aquí está la fórmula que hay detrás de las puertas, canal a canal, y la corrección que necesita cuando solo hay unos pocos canales abiertos.",
  html: `
<div class="step">
  <h3>Una transmisión para cada canal</h3>
  <p>Un <b>canal</b> es una dirección de salida completa: qué partícula sale, en qué estado queda el núcleo residual, el momento angular orbital <i>l</i> y el momento angular total <i>j</i> = <i>l</i> ± ½ de la partícula. El modelo óptico del capítulo 5 asigna a cada uno un <b>coeficiente de transmisión</b> <i>T<sub>lj</sub></i>. Las columnas son las del neutrón incidente, para un blanco de espín 0.</p>
  <div class="ctl"><label for="hf-e">Energía del neutrón (MeV)</label><input id="hf-e" type="range" data-bind="lgE" min="-3" max="0.7" step="0.01" value="-0.3"><output data-show="Eshow" data-fmt="3"></output></div>
  <p>A 1 keV solo está abierta <i>l</i> = 0, con <i>T</i> ≈ 2π<i>S</i><sub>0</sub>√<i>E</i>, unos pocos por ciento. Cada unidad adicional de <i>l</i> cuesta a baja energía un factor de aproximadamente (<i>kR</i>)², así que las columnas se abren una a una a medida que sube la energía. Cada columna alimenta el núcleo compuesto con el peso g<sub>J</sub><i>T</i>:</p>
  <div class="formula">σ<sub>CN</sub> = (π/k²) Σ<sub>J,π</sub> g<sub>J</sub> Σ<sub>lj</sub> T<sub>lj</sub> ,  g<sub>J</sub> = (2J+1) / [(2s+1)(2I+1)]</div>
</div>
<div class="step">
  <h3>Un espín y una paridad cada vez</h3>
  <p>El momento angular y la paridad se conservan, así que el núcleo compuesto se desexcita de forma independiente en cada <i>J</i><sup>π</sup>. Dentro de un bloque, cada canal de salida abierto compite con su propia <i>T</i>: el elástico, de vuelta al estado fundamental; el inelástico, a cada nivel excitado (una columna suma los (<i>l</i>, <i>j</i>) que se acoplan al mismo <i>J</i>); el continuo por encima de 3,6 MeV, cuyos intervalos cuentan como muchos canales, ponderados por la densidad de niveles; y la captura, agrupada en una única <i>T</i><sub>γ</sub> = 2π⟨Γ<sub>γ</sub>⟩/<i>D</i> diminuta. Las alturas están en escala logarítmica.</p>
  <div class="ctl"><label for="hf-j">Bloque de espín y paridad</label><input id="hf-j" type="range" data-bind="jb" min="0" max="9" step="1" value="2" data-instant><output data-show="jbShow" data-fmt="0"></output></div>
  <div class="ctl"><label for="hf-e2">Energía del neutrón (MeV)</label><input id="hf-e2" type="range" data-bind="lgE" min="-3" max="0.7" step="0.01" value="-0.3"><output data-show="Eshow" data-fmt="3"></output></div>
  <p>La barra de abajo es el reparto de <b>Hauser–Feshbach</b>: cada salida se lleva la fracción <i>T<sub>b</sub></i>/Σ<i>T<sub>c</sub></i> de lo que entró por el canal <i>a</i>. Por debajo de 0,85 MeV solo están abiertos el elástico y la captura, y el elástico se lo lleva casi todo.</p>
  <div class="formula">σ<sub>ab</sub> = (π/k²) Σ<sub>J,π</sub> g<sub>J</sub> T<sub>a</sub> T<sub>b</sub> / Σ<sub>c</sub> T<sub>c</sub> · W<sub>ab</sub></div>
</div>
<div class="step">
  <h3>Fluctuaciones de anchura</h3>
  <p>La fórmula simple subestima un poco la dispersión elástica, y la corrección devuelve un poco de flujo hacia ella desde las otras salidas. He aquí por qué.</p>
  <p>Con <i>W<sub>ab</sub></i> = 1 la fórmula multiplica promedios. Las resonancias que hay detrás de esos promedios tienen anchuras que fluctúan (Porter–Thomas, capítulo 15), y en la dispersión elástica la anchura que deja entrar al neutrón es la misma que lo deja salir, así que ambas están correlacionadas. Para el elástico, el promedio de los productos supera entonces al producto de los promedios, y las demás salidas pierden lo que gana el elástico.</p>
  <div class="btns"><button class="btn ghost" data-act="w0" aria-pressed="false">Sin corrección</button><button class="btn ghost" data-act="w1" aria-pressed="true">Moldauer</button></div>
  <div class="ctl"><label for="hf-e3">Energía del neutrón (MeV)</label><input id="hf-e3" type="range" data-bind="lgE" min="-3" max="0.7" step="0.01" value="-0.3"><output data-show="Eshow" data-fmt="3"></output></div>
  <p>Las etiquetas dan σ con la corrección dividida por σ sin ella. Por debajo del primer umbral inelástico, el elástico ya se lleva casi todo el flujo y apenas cambia, mientras que la captura pierde entre un 10 y un 25 %. Entre 1 y 1,5 MeV, el elástico compuesto gana entre un 15 y un 35 %, y el primer nivel 2⁺ pierde alrededor de un tercio. A medida que se abren más niveles y el continuo, el elástico compuesto pasa a ser una parte pequeña del flujo: su propio factor sube hacia 2, pero lo que quita a los demás se reduce, y sus factores vuelven hacia 1. En la receta de Moldauer cada canal recibe un número de grados de libertad ν<sub>c</sub>, y <i>W</i> es una integral unidimensional, que se evalúa con la regla de Gauss–Laguerre de 32 puntos de TALYS.</p>
  <div class="formula">W<sub>ab</sub> = (1 + 2δ<sub>ab</sub>/ν<sub>a</sub>) ∫₀^∞ dx Π<sub>c</sub> (1 + 2T<sub>c</sub>x / ν<sub>c</sub>ΣT)<sup>−(δ<sub>ac</sub>+δ<sub>bc</sub>+ν<sub>c</sub>/2)</sup></div>
  <div class="formula">ν<sub>c</sub> = 1.78 + (T<sub>c</sub><sup>1.212</sup> − 0.78) e<sup>−0.228 ΣT</sup></div>
</div>
<div class="step">
  <h3>Moldauer y HRTW</h3>
  <p>Las curvas repiten el mismo cálculo en todo el intervalo de energías: el cociente para el elástico compuesto, para el primer nivel 2⁺ y para la captura, con Moldauer en trazo continuo y la receta <b>HRTW</b> en discontinuo. HRTW sustituye la integral por un factor elástico <i>W<sub>a</sub></i> y unas transmisiones efectivas <i>V<sub>a</sub></i> que se obtienen por iteración.</p>
  <div class="ctl"><label for="hf-e4">Energía del neutrón (MeV)</label><input id="hf-e4" type="range" data-bind="lgE" min="-3" max="0.7" step="0.01" value="-0.3"><output data-show="Eshow" data-fmt="3"></output></div>
  <div class="formula">σ<sub>ab</sub> ∝ V<sub>a</sub>V<sub>b</sub> / ΣV<sub>c</sub> · [1 + δ<sub>ab</sub>(W<sub>a</sub> − 1)] ,  V<sub>a</sub> = T<sub>a</sub> / [1 + (W<sub>a</sub> − 1) V<sub>a</sub>/ΣV]</div>
  <p>Ambas coinciden de cerca para el elástico y el inelástico; para la captura en la región de keV, HRTW quita hasta un 10 % más. Entre 0,85 y 2 MeV la captura incluso gana: ahí la anchura total está dominada por unas pocas anchuras neutrónicas que fluctúan, y el promedio de 1/Γ supera a 1/⟨Γ⟩. Las dos recetas son ajustes al resultado exacto de matrices aleatorias (GOE), que TALYS ofrece también como integral triple. INCOGNITA porta las tres (<code>widthmode</code> 1, 2, 3); Moldauer es la opción por defecto, aplicada a neutrones incidentes hasta la energía de separación del neutrón del blanco.</p>
</div>
<div class="step">
  <h3>Límites del realce elástico</h3>
  <p>¿Cuánto puede crecer el realce elástico? Entre dos y tres veces, según las resonancias estén separadas o se solapen.</p>
  <p>Los límites explican el tamaño del efecto. Toma <i>N</i> canales iguales, sin captura, y varía su suma ΣT, que es 2π veces el cociente entre la anchura total media y el espaciado de niveles, Γ/<i>D</i>. Con resonancias aisladas (ΣT ≪ 1) y muchos canales, cada anchura sigue Porter–Thomas con un grado de libertad y el realce elástico es ⟨Γ<sub>a</sub>²⟩/⟨Γ<sub>a</sub>⟩² = 3. Cuando las resonancias se solapan mucho (ΣT ≫ 2π), la sección eficaz fluctúa como una onda aleatoria (fluctuaciones de Ericson) y el realce baja a 2.</p>
  <div class="ctl"><label for="hf-n">Canales abiertos N</label><input id="hf-n" type="range" data-bind="nch" min="2" max="60" step="1" value="30" data-instant><output data-show="nch" data-fmt="0"></output></div>
  <p>Para <i>N</i> canales aislados el valor exacto es 3<i>N</i>/(<i>N</i>+2) (el rombo): con solo dos canales el realce no puede pasar de 1,5, porque entonces la anchura total fluctúa tanto como la elástica. La receta de Moldauer reproduce este límite; HRTW se queda por debajo cuando hay muchos canales débiles abiertos. El recuadro dibuja resonancias con la anchura que corresponde al punto móvil. En la fórmula de Moldauer el límite de muchos canales es 1 + 2/ν: ν → 1 para resonancias aisladas y ν → 1,78 cuando se solapan. Eso da 2,12 en solapamiento total en lugar de 2: un pequeño error del ajuste.</p>
  <div class="aside">En el código: <code>compound/prepare.py</code> (canales de salida y sus transmisiones por <i>J</i><sup>π</sup>), <code>compound/target.py</code> (las sumas de Hauser–Feshbach), <code>compound/wfc.py</code> (Moldauer, HRTW y GOE, portados de TALYS). La imagen evalúa las mismas fórmulas con ingredientes ilustrativos: transmisiones de esfera dura para un blanco parecido al hierro, siete niveles, un continuo de temperatura constante y un único canal de captura agrupado.</div>
</div>`,
};
(function () {
  const L = {
    // scene 1: incident T_lj
    "T = {#}": "T = {#}",
    "l={#}": "l={#}",
    "hollow: j = l − ½ · solid: j = l + ½": "huecas: j = l − ½ · rellenas: j = l + ½",
    "compound nucleus · σ(CN) ≈ {#} b": "núcleo compuesto · σ(CN) ≈ {#} b",
    "compound nucleus": "núcleo compuesto",
    "σ(CN) ≈ {#} b": "σ(CN) ≈ {#} b",
    "E = {#} MeV · kR = {#}": "E = {#} MeV · kR = {#}",
    "E = {#} keV · kR = {#}": "E = {#} keV · kR = {#}",
    "transmission Tₗⱼ of the incident neutron": "transmisión Tₗⱼ del neutrón incidente",
    // scene 2: one J^pi block
    "elastic": "elástico",
    "cont.": "cont.",
    "level energy (MeV) under each column": "energía del nivel (MeV) bajo cada columna",
    "residual level (energy in MeV) · n×: number of (l, j) channels summed": "nivel residual (energía en MeV) · n×: número de canales (l, j) sumados",
    "{#}/{#}⁺ block · in through l = {#}, Tₐ = {#}": "bloque {#}/{#}⁺ · entrada por l = {#}, Tₐ = {#}",
    "{#}/{#}⁻ block · in through l = {#}, Tₐ = {#}": "bloque {#}/{#}⁻ · entrada por l = {#}, Tₐ = {#}",
    "elastic {#} %": "elástico {#} %",
    "higher {#} %": "superiores {#} %",
    "Hauser–Feshbach split: T / ΣT for each exit": "reparto de Hauser–Feshbach: T / ΣT para cada salida",
    // scene 3: HF against WFC
    "closed": "cerrado",
    "compound elastic": "elástico compuesto",
    "first {#}⁺ level": "primer nivel {#}⁺",
    "higher levels": "niveles superiores",
    "capture": "captura",
    "{#} mb": "{#} mb",
    "with Moldauer's correction": "con la corrección de Moldauer",
    "Hauser–Feshbach without correction": "Hauser–Feshbach sin corrección",
    "compound formation {#} mb at {#} MeV": "formación del núcleo compuesto: {#} mb a {#} MeV",
    "compound formation {#} mb at {#} keV": "formación del núcleo compuesto: {#} mb a {#} keV",
    // scene 4: ratio curves
    "{#} keV": "{#} keV", "{#} MeV": "{#} MeV",
    "{#}⁺ opens": "se abre el {#}⁺",
    "continuum": "continuo",
    "continuum opens": "se abre el continuo",
    "elastic ×{#} (Moldauer) · ×{#} (HRTW)": "elástico ×{#} (Moldauer) · ×{#} (HRTW)",
    "capture ×{#} (Moldauer) · ×{#} (HRTW)": "captura ×{#} (Moldauer) · ×{#} (HRTW)",
    "first {#}⁺ ×{#} (Moldauer) · ×{#} (HRTW)": "primer {#}⁺ ×{#} (Moldauer) · ×{#} (HRTW)",
    "solid: Moldauer · dashed: HRTW": "continua: Moldauer · discontinua: HRTW",
    "σ with correction / σ without": "σ con corrección / σ sin ella",
    // scene 5: the limits
    "ΣT = {#}πΓ/D →": "ΣT = {#}πΓ/D →",
    "elastic enhancement Wₐₐ": "realce elástico Wₐₐ",
    "T → {#} per channel": "T → {#} por canal",
    "exact, isolated: {#}N/(N+{#}) = {#}": "exacto, aisladas: {#}N/(N+{#}) = {#}",
    "Porter–Thomas: {#}": "Porter–Thomas: {#}",
    "Ericson: {#}": "Ericson: {#}",
    "{#} channels · ΣT = {#} · Wₐₐ = {#}": "{#} canales · ΣT = {#} · Wₐₐ = {#}",
    "isolated resonances: Γ ≪ D": "resonancias aisladas: Γ ≪ D",
    "resonances begin to overlap": "las resonancias empiezan a solaparse",
    "strongly overlapping: Γ ≫ D": "muy solapadas: Γ ≫ D",
  };
  Object.assign(WT.L.labels, L);
})();
Object.assign(WT.L.glossary, {
  hrtw: {
    term: "HRTW", aliases: ["HRTW"],
    short: "Una receta de fluctuaciones de anchura de Hofmann, Richert, Tepel y Weidenmüller: un factor elástico por canal y unas transmisiones efectivas que se obtienen por iteración.",
    more: "Se ajustó, como la de Moldauer, a cálculos numéricos de matrices aleatorias. TALYS la ofrece como widthmode 2; Moldauer (1) es la opción por defecto, y la integral triple exacta del GOE (3), la referencia.",
    chapter: "hauser",
  },
  ericson: {
    term: "Fluctuaciones de Ericson", aliases: ["fluctuaciones de Ericson"],
    short: "Fluctuaciones aleatorias de una sección eficaz con la energía cuando se solapan muchas resonancias, en una escala de energía fijada por su anchura total media.",
    more: "Son el límite de solapamiento fuerte de la misma estadística que da anchuras de Porter–Thomas para resonancias aisladas. En ese límite el factor de realce elástico tiende a 2.",
    chapter: "hauser",
  },
});
/* attributes referenced in the English chapter script (for the structure check): data-show="jbShow" data-act="w0" data-act="w1" */
