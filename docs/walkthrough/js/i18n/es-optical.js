/* Spanish: optical (Capítulo 23, experto: el modelo óptico, resuelto) */
WT.L.ch.optical = {
  num: "Capítulo 23", title: "El modelo óptico, resuelto", short: "Modelo óptico, resuelto",
  lead: "El capítulo 5 dibujó el potencial óptico como una bola de vidrio turbio. Aquí aparece tal como lo usa el motor: una parametrización global, una ecuación de Schrödinger radial integrada paso a paso y una condición de empalme que convierte la onda en coeficientes de transmisión.",
  html: `
<div class="step">
  <h3>El potencial de Koning–Delaroche</h3>
  <p>Para neutrones y protones sobre blancos esféricos, la opción por defecto es el potencial de <b>Koning–Delaroche</b> (KD03): formas de Woods–Saxon cuyas profundidades varían suavemente con la energía y con la masa y el exceso de neutrones del blanco, a partir de una fórmula global o, para los núcleos que KD03 ajustó uno por uno, como el hierro-56, a partir de un ajuste local de la misma forma. La imagen usa la fórmula global para neutrones sobre hierro-56. El pozo real (azul) liga; las partes imaginarias (rojo) absorben, en el volumen y, sobre todo a baja energía, en una capa delgada en la superficie.</p>
  <div class="ctl"><label for="op-e">Energía del neutrón (MeV)</label><input id="op-e" type="range" data-bind="E" min="0.1" max="80" step="0.1" value="5"><output data-show="E" data-fmt="1"></output></div>
  <div class="formula">U(r) = −V<sub>V</sub> f(r) − iW<sub>V</sub> f(r) + 4i a<sub>D</sub>W<sub>D</sub> df<sub>D</sub>/dr + 2(V<sub>so</sub> + iW<sub>so</sub>) (1/r) df<sub>so</sub>/dr ⟨l·σ⟩</div>
  <p>Los neutrones de prueba cruzan a la energía que elijas y se desvanecen donde la absorción muerde: su recorrido libre medio es ħ<i>v</i>/2|<i>W</i>|. Cada profundidad es función de <i>E</i> − <i>E</i><sub>F</sub>, medida desde la energía de Fermi: la profundidad real baja despacio, la absorción superficial <i>W</i><sub>D</sub> tiene su máximo cerca de 10 MeV y la absorción de volumen <i>W</i><sub>V</sub> crece de forma continua hasta imponerse, aquí por encima de unos 45 MeV.</p>
</div>
<div class="step">
  <h3>Integrar la ecuación radial</h3>
  <p>Cada onda parcial obedece su propia ecuación radial. El motor la integra hacia fuera desde <i>r</i> = 0 con el <b>método de Numerov</b>, una regla de tres puntos con una precisión de sexto orden en el paso, a través del potencial complejo completo.</p>
  <div class="formula">u″<sub>lj</sub>(r) = [ l(l+1)/r² + (2μ/ħ²) U<sub>lj</sub>(r) − k² ] u<sub>lj</sub>(r)</div>
  <div class="ctl"><label for="op-l">Onda parcial l</label><input id="op-l" type="range" data-bind="L" min="0" max="10" step="1" value="1" data-instant><output data-show="L" data-fmt="0"></output></div>
  <div class="ctl"><label for="op-e2">Energía del neutrón (MeV)</label><input id="op-e2" type="range" data-bind="E" min="0.1" max="80" step="0.1" value="5"><output data-show="E" data-fmt="1"></output></div>
  <p>La línea continua es la onda en el tiempo, Re[<i>u</i> e<sup>−iωt</sup>]; la discontinua es la onda libre, como si el núcleo no estuviera. Dentro del pozo la onda es más corta (el neutrón va más rápido) y más pequeña (absorbida); fuera, vuelve desplazada en fase.</p>
</div>
<div class="step">
  <h3>De la onda a S y T</h3>
  <p>Más allá de unos 12 fm el potencial se ha anulado y la onda tiene que ser una mezcla de una onda libre entrante y otra saliente, <i>u</i> ∝ <i>H</i><sup>−</sup> − <i>S</i> <i>H</i><sup>+</sup>. Empalmar la <i>u</i> integrada en dos radios fija el elemento <i>S<sub>lj</sub></i> de la <b>matriz S</b>: la amplitud saliente, con su fase.</p>
  <div class="btns"><button class="btn ghost" data-act="abs" aria-pressed="false">Desactivar la absorción</button></div>
  <div class="formula">S<sub>lj</sub> = η<sub>lj</sub> e<sup>2iδ<sub>lj</sub></sup> ,  T<sub>lj</sub> = 1 − |S<sub>lj</sub>|²</div>
  <p>El punto es <i>S</i> en el plano complejo, dentro de la circunferencia unidad; su rastro es el camino que sigue cuando la energía barre de 0,1 a 40 MeV. Sin absorción |<i>S</i>| = 1: el punto corre sobre la circunferencia, la onda solo cambia de fase y <i>T</i> = 0. Lo que el punto se aleja hacia dentro de la circunferencia es lo que reciben el núcleo compuesto y todas las demás reacciones.</p>
</div>
<div class="step">
  <h3>El espín–órbita separa j</h3>
  <p>El término de <b>espín–órbita</b> es atractivo para <i>j</i> = <i>l</i> + ½ y repulsivo para <i>j</i> = <i>l</i> − ½. Es pequeño, unos pocos MeV en la superficie, pero separa las dos transmisiones de cada <i>l</i>, sobre todo cerca de la onda parcial que roza la superficie.</p>
  <div class="ctl"><label for="op-e3">Energía del neutrón (MeV)</label><input id="op-e3" type="range" data-bind="E" min="0.1" max="80" step="0.1" value="5"><output data-show="E" data-fmt="1"></output></div>
  <div class="btns"><button class="btn ghost" data-act="so" aria-pressed="false">Desactivar el espín–órbita</button></div>
  <p>Hauser–Feshbach (capítulo 22) usa las dos por separado; sumadas con sus pesos, (<i>l</i>+1)<i>T</i><sub>l,l+½</sub> + <i>l</i> <i>T</i><sub>l,l−½</sub>, dan una sección eficaz de reacción casi sin cambios. Por eso las secciones eficaces totales apenas restringen la intensidad del espín–órbita y hacen falta datos de polarización.</p>
</div>
<div class="step">
  <h3>Las secciones eficaces</h3>
  <p>Sumando las ondas parciales se obtienen los observables a los que se ajusta el potencial. La sección eficaz de reacción cuenta el flujo eliminado, la sección eficaz total se deduce de la amplitud hacia delante y su diferencia es la dispersión elástica de forma.</p>
  <div class="formula">σ<sub>R</sub> = (π/k²) Σ<sub>l</sub> [(l+1)T<sub>l,l+½</sub> + l T<sub>l,l−½</sub>] ,  σ<sub>tot</sub> = (2π/k²) Σ<sub>lj</sub> (j+½)(1 − Re S<sub>lj</sub>)</div>
  <div class="ctl"><label for="op-e4">Energía del neutrón (MeV)</label><input id="op-e4" type="range" data-bind="E" min="0.2" max="50" step="0.1" value="5"><output data-show="E" data-fmt="1"></output></div>
  <p>KD03 se ajustó a datos de este tipo para muchos núcleos, de 1 keV a 200 MeV; la sección eficaz total del hierro, entre 3,5 y 4 b a unos pocos MeV y 2,5 b a 14 MeV, sale con un margen de alrededor del 5 por ciento sin ningún ajuste a este núcleo, máximos anchos incluidos: son el tamaño nuclear visto frente a la longitud de onda del neutrón.</p>
</div>
<div class="step">
  <h3>El extremo de baja energía</h3>
  <p>Por debajo de unos pocos keV solo importa la onda s, y <i>T</i><sub>0</sub> crece como √<i>E</i>: una pendiente de un medio en esta gráfica log–log. La constante es la <b>función de fuerza</b> <i>S</i><sub>0</sub> = <i>T</i><sub>0</sub>/(2π√<i>E</i>), con <i>E</i> en eV, la misma magnitud que los análisis de resonancias miden como Σ Γ<sub>n</sub><sup>0</sup>/Δ<i>E</i>.</p>
  <p>Un potencial global se ajusta sobre todo a energías de MeV, y su extremo de baja energía es su punto más débil. Para el hierro-56 este da <i>S</i><sub>0</sub> ≈ 5,5 × 10⁻⁴, y el ajuste local de KD03 casi lo mismo, mientras que el valor medido (RIPL) es 2,3 ± 0,6 × 10⁻⁴: el hierro está cerca del máximo de la resonancia de tamaño 3s en torno a <i>A</i> ≈ 55, donde <i>S</i><sub>0</sub> es más sensible al potencial. Por eso los valores medidos de <i>S</i><sub>0</sub> y <i>S</i><sub>1</sub> son una entrada aparte y opcional del motor.</p>
  <div class="aside">En el código: <code>omp/parameters.py</code> (KD03 y los demás potenciales globales), <code>omp/potential.py</code> (los factores de forma radiales), <code>omp/schrodinger.py</code> (integración de Numerov y empalme, con funciones de Coulomb por el método de Steed para partículas cargadas; sustituye a ECIS para blancos esféricos y se comprueba frente a los T<sub>lj</sub> de ECIS), <code>ecis/</code> (el port de canales acoplados para blancos deformados), <code>omp/sfunc.py</code> (opcional: S₀, S₁ medidos). La imagen resuelve la propia ecuación, de forma no relativista, para neutrones sobre hierro-56.</div>
</div>`,
};
(function () {
  const L = {
    // scene 1: the potential
    "{#} fm": "{#} fm", "{#} MeV": "{#} MeV", "E = {#} MeV": "E = {#} MeV",
    "real well, depth {#} MeV": "pozo real, profundidad {#} MeV",
    "surface absorption, peak {#} MeV": "absorción superficial, máximo {#} MeV",
    "volume absorption {#} MeV": "absorción de volumen {#} MeV",
    "spin–orbit for l = {#}, j = {#}/{#}: {#} MeV": "espín–órbita para l = {#}, j = {#}/{#}: {#} MeV",
    "real": "real", "volume": "volumen", "surface": "superficie",
    "depths (MeV) against energy (MeV)": "profundidades (MeV) frente a la energía (MeV)",
    // scene 2: the radial wave
    "potential: real (blue), imaginary (red)": "potencial: real (azul), imaginario (rojo)",
    "nuclear surface": "superficie nuclear",
    "l = {#}, j = {#}+½ · E = {#} MeV · |S| = {#} · δ = {#}° · T = {#}": "l = {#}, j = {#}+½ · E = {#} MeV · |S| = {#} · δ = {#}° · T = {#}",
    "solid: the wave now · shaded: its size |u| · dashed: free wave": "continua: la onda ahora · sombreado: su tamaño |u| · discontinua: onda libre",
    // scene 3: S in the complex plane
    "Re S": "Re S", "Im S": "Im S",
    "|S| = {#}: nothing absorbed": "|S| = {#}: no se absorbe nada",
    "l = {#}, j = {#}+½ · E = {#} MeV": "l = {#}, j = {#}+½ · E = {#} MeV",
    "|S| = {#} · T = {#} − |S|² = {#}": "|S| = {#} · T = {#} − |S|² = {#}",
    "l = {#}, j = {#}+½": "l = {#}, j = {#}+½",
    "|S| = {#}": "|S| = {#}",
    "T = {#} − |S|² = {#}": "T = {#} − |S|² = {#}",
    "trail: S as E runs {#} → {#} MeV": "rastro: S mientras E va de {#} a {#} MeV",
    "no absorption: S stays on the circle": "sin absorción: S se queda en la circunferencia",
    // scene 4: spin-orbit
    "T = {#}": "T = {#}", "l": "l",
    "hollow: j = l − ½ · solid: j = l + ½": "huecas: j = l − ½ · rellenas: j = l + ½",
    "hollow (purple): j = l − ½ · solid (blue): j = l + ½": "huecas (morado): j = l − ½ · rellenas (azul): j = l + ½",
    "reaction cross section {#} b (without spin–orbit {#} b)": "sección eficaz de reacción {#} b (sin espín–órbita: {#} b)",
    "reaction cross section {#} b (spin–orbit off)": "sección eficaz de reacción {#} b (espín–órbita desactivado)",
    "grazing l ≈ kR = {#}": "l rasante ≈ kR = {#}",
    // scene 5: cross sections
    "{#} b": "{#} b", "{#} keV": "{#} keV", "{#} eV": "{#} eV",
    "total {#} b": "total {#} b",
    "reaction {#} b": "reacción {#} b",
    "shape elastic {#} b": "elástica de forma {#} b",
    "n + ⁵⁶Fe, KD{#}, computed here": "n + ⁵⁶Fe, KD{#}, calculado aquí",
    // scene 6: low-energy end
    "T₀ (s-wave)": "T₀ (onda s)",
    "T₁ (p-wave, j = {#}/{#}): slope {#}/{#}": "T₁ (onda p, j = {#}/{#}): pendiente {#}/{#}",
    "dashed: {#}πS₀√E, slope ½": "discontinua: {#}πS₀√E, pendiente ½",
    "S₀ = {#} × {#}⁻⁴ from this potential": "S₀ = {#} × {#}⁻⁴ con este potencial",
  };
  // mean free path: each value is "{#}" or "> {#}"
  for (const a of ["{#}", "> {#}"]) for (const b of ["{#}", "> {#}"])
    L[`mean free path: ${a} fm at the surface, ${b} fm in the centre`] = `recorrido libre medio: ${a} fm en la superficie, ${b} fm en el centro`;
  Object.assign(WT.L.labels, L);
})();
Object.assign(WT.L.glossary, {
  koningDelaroche: {
    term: "Potencial de Koning–Delaroche", aliases: ["Koning–Delaroche", "Koning-Delaroche", "KD03"],
    short: "El potencial óptico global para neutrones y protones de A. J. Koning y J.-P. Delaroche (2003), de 1 keV a 200 MeV y de masa 24 a 209.",
    more: "Sus profundidades, radios y difusividades son funciones suaves de la energía, la masa y el exceso de neutrones, ajustadas de una vez a un gran conjunto de secciones eficaces y distribuciones angulares medidas. Es la opción por defecto para nucleones en TALYS y en el motor.",
    chapter: "optical",
  },
  numerov: {
    term: "Método de Numerov", aliases: ["método de Numerov", "Numerov"],
    short: "Una regla de tres puntos para integrar ecuaciones de segundo orden sin término en la primera derivada, como la ecuación de Schrödinger radial, con un error de orden h⁶ por paso.",
    formula: "(1 − h²Q_n+1/12) u_n+1 = 2(1 + 5h²Q_n/12) u_n − (1 − h²Q_n−1/12) u_n−1",
    chapter: "optical",
  },
  sMatrix: {
    term: "Matriz S", aliases: ["matriz S"],
    short: "Las amplitudes que conectan las ondas entrantes con las salientes; para la dispersión elástica en una onda parcial, un único número complejo S = η e^(2iδ).",
    more: "|S| = 1 significa que no se absorbe nada y solo cambia la fase δ; lo que falta, 1 − |S|², es el coeficiente de transmisión, el flujo que pasa a las reacciones.",
    chapter: "optical",
  },
  spinOrbit: {
    term: "Término de espín–órbita", aliases: ["espín–órbita", "espín-órbita"],
    short: "La parte del potencial nuclear que depende de si el espín del nucleón es paralelo o antiparalelo a su momento angular orbital.",
    more: "Es atractivo para j = l + ½ y repulsivo para j = l − ½, con su máximo en la superficie nuclear. La misma interacción produce los números mágicos del modelo de capas.",
    chapter: "optical",
  },
});
