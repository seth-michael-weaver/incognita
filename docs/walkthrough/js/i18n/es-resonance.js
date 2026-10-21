/* Spanish: resonance (chapter 10) */
WT.es.ch.resonance = {
  num: "Capítulo 10", title: "El bosque de resonancias", short: "Resonancias",
  lead: "A energía suficientemente baja, un neutrón ya no ve un núcleo liso y promediado. Ve los niveles de energía individuales del núcleo compuesto, uno a uno.",
  html: `
<div class="step">
  <p>Cada árbol es una <b>resonancia</b>: un nivel de energía del núcleo compuesto en el que puede caer un neutrón que tenga exactamente esa energía. El tronco está en la energía del nivel, de unos pocos eV a unos cientos de eV (un MeV es un millón de eV). La altura del árbol indica cuánto crece la sección eficaz de <b>captura</b> encima de él, en una escala comprimida (logarítmica); captura significa que el neutrón es absorbido y el núcleo emite fotones. El ancho de la copa es el ancho de la resonancia Γ, dibujado unas cien veces más ancho de lo que es para que se vea.</p>
  <div class="ctl"><label for="res-e">Energía del neutrón (eV)</label><input id="res-e" type="range" data-bind="En" min="0.5" max="300" step="0.1" value="30"><output data-show="En" data-fmt="1"></output></div>
  <p>El neutrón avanza a saltos en energía. Cada vez que aterriza puede ser capturado: un destello y una ráfaga de fotones. Sobre un árbol la sección eficaz es de miles de barns y la captura es casi segura; entre árboles es de unos pocos barns y el neutrón casi siempre sigue saltando. Arrastra la energía para dejarlo bajo un árbol, y luego entre dos.</p>
</div>
<div class="step">
  <h3>Los árboles guardan las distancias</h3>
  <p>Cada fila muestra una serie de posiciones de niveles con el mismo espaciado medio. Los niveles reales no están colocados al azar: dos niveles con el mismo espín y paridad se repelen, y cuanto más se acercan, más se empujan. La <b>teoría de matrices aleatorias</b>, las matemáticas de los niveles de un sistema cuántico complicado, da el patrón (fila central): las casi coincidencias son raras. Las posiciones realmente aleatorias (fila de arriba) se agrupan y dejan huecos.</p>
  <div class="btns"><button class="btn" data-act="again">Sortear de nuevo</button></div>
  <p>Sortea de nuevo para obtener otra muestra. El número ⟨r̃⟩ compara cada espaciado con el siguiente: unos 0,39 para posiciones aleatorias, 0,53 para niveles que se repelen. El motor saca sus espaciados del patrón de matrices aleatorias. Mezclar dos secuencias, por ejemplo dos espines (fila de abajo), oculta en parte la repulsión, y así es como un conjunto de niveles medidos revela cuántas secuencias contiene.</p>
</div>
<div class="step">
  <h3>Las alturas se dispersan muchísimo</h3>
  <p>Ahora la altura de cada árbol es su <b>anchura neutrónica</b> Γ<sub>n</sub> en una escala lineal ordinaria: cuán fuertemente se conecta ese nivel con un neutrón más el blanco. La tapa amarilla de cada árbol es su anchura γ Γ<sub>γ</sub>, la rapidez con que emite fotones. La anchura γ suma cientos de caminos de fotones, así que es casi igual para todos los niveles.</p>
  <div class="btns"><button class="btn" data-act="roll">Sortear una anchura</button><button class="btn ghost" data-act="equal">Anchuras iguales</button><button class="btn ghost" data-act="pt">Porter–Thomas</button></div>
  <p>Un nivel tiene una sola manera de romperse en neutrón más blanco, así que su anchura se comporta como el cuadrado de un único número aleatorio de campana. Sortea uno: una bola cae sobre la campana en <i>x</i>, el cuadrado <i>x</i>² pasa a ser la altura del siguiente árbol, y un punto cae al montón de la derecha. El montón se acumula cerca de cero con una cola larga, la ley de <b>Porter–Thomas</b>: la mayoría de los niveles son débiles, unos pocos enormes. Anchuras iguales muestra cómo sería en cambio un bosque de árboles promedio.</p>
</div>
<div class="step">
  <h3>Una escalera a partir de cuatro números</h3>
  <p>El bosque crece ahora a partir de números promedio que puedes ajustar. Para un núcleo que nadie ha medido, nadie puede decir dónde está cada árbol, pero los promedios sí se pueden predecir: el espaciado medio <i>D</i><sub>0</sub>; las <b>funciones de fuerza</b> <i>S</i><sub>0</sub> y <i>S</i><sub>1</sub>, la anchura neutrónica media por unidad de espaciado, para neutrones de onda s (que llegan de frente) y de onda p (que llegan descentrados, con una unidad de momento angular); y la anchura γ media. A partir de estos cuatro el motor construye una <b>escalera</b>: un conjunto aleatorio de niveles con esos promedios.</p>
  <div class="ctl"><label for="res-d0">Espaciado D₀ (eV)</label><input id="res-d0" type="range" data-bind="D0" min="3" max="60" step="0.5" value="20"><output data-show="D0" data-fmt="1"></output></div>
  <div class="ctl"><label for="res-s0">Fuerza S₀ (×10⁻⁴)</label><input id="res-s0" type="range" data-bind="S0" min="0.2" max="3" step="0.05" value="1"><output data-show="S0" data-fmt="2"></output></div>
  <div class="ctl"><label for="res-gg">Anchura γ ⟨Γγ⟩ (meV)</label><input id="res-gg" type="range" data-bind="Gg" min="10" max="80" step="1" value="23"><output data-show="Gg" data-fmt="0"></output></div>
  <p>Arrastra <i>D</i><sub>0</sub> y los árboles se separan o se apiñan. Las copas macizas son niveles de onda s (paridad positiva); las huecas, niveles de onda p (paridad negativa). Las anchuras neutrónicas crecen como √<i>E</i> para las ondas s y como <i>E</i><sup>3/2</sup> para las ondas p, así que los árboles huecos son bajos a baja energía y crecen hacia la derecha.</p>
</div>
<div class="step">
  <h3>Abajo, en la zona térmica</h3>
  <p>El mismo bosque en una escala de energía logarítmica que baja hasta unas milésimas de eV. Los neutrones de un reactor nacen rápidos y se frenan rebotando en núcleos ligeros; cada rebote les quita más o menos la misma fracción de su energía, así que cada salto aquí cubre el mismo tramo de la escala logarítmica. En su descenso cruzan el bosque, y algunos quedan atrapados.</p>
  <div class="btns"><button class="btn" data-act="slow">Frenar 10 neutrones</button></div>
  <p>Los que lo atraviesan se asientan a temperatura ambiente, 0,025 eV, la energía <b>térmica</b>, muy por debajo del primer árbol. Allí la sección eficaz es la suma de las colas de todas las resonancias, incluidos niveles ligados justo por debajo de energía cero; el suelo sube hacia la izquierda porque las colas crecen como 1/<i>v</i>, siendo <i>v</i> la velocidad del neutrón (un neutrón más lento pasa más tiempo cerca del núcleo). El área del disco es la sección eficaz térmica. Como el neutrón aterriza igual de a menudo en cada factor de energía, lo que el bosque atrapa durante el descenso se mide con la <b>integral de resonancia</b>: la sección eficaz por encima de 0,5 eV con cada energía ponderada por 1/<i>E</i>.</p>
</div>
<div class="step">
  <h3>Solo la estadística es predecible</h3>
  <p>Cada fila es una escalera sacada de los mismos cuatro números: sus árboles cerca de energía cero, el neutrón térmico a 0,025 eV y un disco cuya área es la sección eficaz de captura térmica de esa escalera. El corchete llega hasta el árbol que fija el valor, normalmente el más cercano, y el número da su distancia. Esa distancia cambia de una escalera a otra, y el disco varía en un factor de diez o más.</p>
  <div class="btns"><button class="btn" data-act="draw1">Sortear una escalera</button><button class="btn ghost" data-act="more">Sortear 20</button></div>
  <p>Cada valor cae al montón de la derecha. Así que para un núcleo no medido el motor da una dispersión de valores, no un único número, y ningún modelo mejor puede estrecharla. La integral de resonancia, que suma sobre todo el bosque, se dispersa menos. En los núcleos ligeros los niveles están separados decenas de keV y ninguno queda cerca de la zona térmica; allí la captura ocurre por otro proceso, directo, y el método de escaleras no da respuesta.</p>
  <div class="aside">En el código: <code>physics/resonance/ladder.py</code> (espaciados de matrices aleatorias, anchuras de Porter–Thomas, secciones eficaces de Breit–Wigner, captura térmica e integral de resonancia sobre un conjunto de escaleras), <code>ladder_statistics.py</code> (las mismas leyes puestas a prueba con escaleras medidas), <code>ensemble_runner.py</code>.</div>
</div>`,
};
Object.assign(WT.es.labels, {
  // forest
  "{#} eV": "{#} eV", "+{#} eV": "+{#} eV",
  "height: peak capture (log) · canopy: width Γ ×{#}": "altura: captura máx. (log) · copa: ancho Γ ×{#}",
  "tree height: peak capture cross section (log scale) · canopy: resonance width Γ, drawn {#}× wide": "altura: sección eficaz de captura máxima (escala log) · copa: ancho Γ, dibujado {#}× más ancho",
  "D₀ {#} eV · S₀ {#}×{#}⁻⁴ · S₁ {#}×{#}⁻⁴ · ⟨Γγ⟩ {#} meV": "D₀ {#} eV · S₀ {#}×{#}⁻⁴ · S₁ {#}×{#}⁻⁴ · ⟨Γγ⟩ {#} meV",
  "s-wave (+ parity)": "onda s (paridad +)", "p-wave (− parity)": "onda p (paridad −)",
  "caught {#} times in {#} landings": "capturado {#} veces en {#} aterrizajes",
  "each tree: one level of the compound nucleus": "cada árbol: un nivel del núcleo compuesto",
  "each tree: one level of the compound nucleus · about {#} eV apart": "cada árbol: un nivel del núcleo compuesto · separados unos {#} eV",
  // spacing
  "random positions (Poisson)": "posiciones aleatorias (Poisson)",
  "repelling levels (random-matrix)": "niveles que se repelen (matrices aleatorias)",
  "two repelling sequences mixed": "dos secuencias que se repelen, mezcladas",
  "clumps and gaps · ⟨r̃⟩ ≈ {#}": "grupos y huecos · ⟨r̃⟩ ≈ {#}",
  "evenly kept apart · ⟨r̃⟩ ≈ {#}": "separados con regularidad · ⟨r̃⟩ ≈ {#}",
  "repulsion half hidden · ⟨r̃⟩ ≈ {#}": "repulsión medio oculta · ⟨r̃⟩ ≈ {#}",
  "clumps and gaps · spacing ratio ⟨r̃⟩ ≈ {#}": "grupos y huecos · razón de espaciados ⟨r̃⟩ ≈ {#}",
  "evenly kept apart · spacing ratio ⟨r̃⟩ ≈ {#}": "separados con regularidad · razón de espaciados ⟨r̃⟩ ≈ {#}",
  "repulsion half hidden · spacing ratio ⟨r̃⟩ ≈ {#}": "repulsión medio oculta · razón de espaciados ⟨r̃⟩ ≈ {#}",
  "⟨r̃⟩: {#} if random, {#} for random-matrix": "⟨r̃⟩: {#} si es aleatorio, {#} con matrices aleatorias",
  "same average spacing in every row · ⟨r̃⟩: {#} if random, {#} for random-matrix": "mismo espaciado medio en cada fila · ⟨r̃⟩: {#} si es aleatorio, {#} con matrices aleatorias",
  // Porter-Thomas
  "height: neutron width Γn (linear)": "altura: anchura neutrónica Γn (lineal)",
  "tree height: neutron width Γn, linear scale": "altura: anchura neutrónica Γn, escala lineal",
  "yellow: γ width": "amarillo: anchura γ",
  "yellow cap: γ width, nearly the same on every tree": "tapa amarilla: anchura γ, casi igual en todos",
  "equal widths: every tree the average": "anchuras iguales: todos los árboles en el promedio",
  "rolled widths": "anchuras sorteadas", "pile of rolled widths": "montón de anchuras sorteadas",
  "× average": "× promedio", "(in units of the average)": "(en unidades del promedio)",
  "dashed: Porter–Thomas": "discontinua: Porter–Thomas", "dashed: the Porter–Thomas law": "discontinua: la ley de Porter–Thomas",
  "bell-curve number x": "número de campana x",
  "x = {#}  →  x² = {#}": "x = {#}  →  x² = {#}",
  "press Roll a width": "pulsa Sortear una anchura",
  // thermal
  "bound level {#} eV": "nivel ligado {#} eV",
  "a bound level at {#} eV: its tail lifts this end": "un nivel ligado a {#} eV: su cola levanta este extremo",
  "resonance integral ≈ {#} b": "integral de resonancia ≈ {#} b",
  "resonance integral above {#} eV ≈ {#} b": "integral de resonancia sobre {#} eV ≈ {#} b",
  "{#}/v": "{#}/v",
  "caught by a tree on the way down: {#} · reached thermal: {#}": "atrapados por un árbol al bajar: {#} · llegan a térmico: {#}",
  "each hop: one bounce, the same fraction of energy lost": "cada salto: un rebote, se pierde la misma fracción de energía",
  // ensemble
  "thermal neutron": "neutrón térmico",
  "σ disc": "disco σ", "disc area = σ at {#} eV": "disco: área = σ a {#} eV",
  "{#}k": "{#}k",
  "thermal σ (b)": "σ térmica (b)", "thermal σ, barns": "σ térmica, barns",
  "{#} ladders · thermal ×{#} · res. integral ×{#}": "{#} escaleras · térmica ×{#} · int. de res. ×{#}",
});
// labels that carry a cross section printed as "12 b" or "3.4k b"
(function () {
  const L = WT.es.labels;
  for (const b of ["{#} b", "{#}k b"]) {
    L[b] = b;
    L[`σ ≈ ${b} · caught on {#} % of landings`] = `σ ≈ ${b} · capturado en el {#} % de los aterrizajes`;
    L[`σ ≈ ${b} · caught on <{#} % of landings`] = `σ ≈ ${b} · capturado en el <{#} % de los aterrizajes`;
    L[`thermal, {#} eV: σ ≈ ${b}`] = `térmico, {#} eV: σ ≈ ${b}`;
    L[`{#} ladders · thermal σ median ${b}, middle two thirds ×{#} · resonance integral only ×{#}`] =
      `{#} escaleras · σ térmica mediana ${b}, dos tercios centrales ×{#} · integral de resonancia solo ×{#}`;
  }
})();
