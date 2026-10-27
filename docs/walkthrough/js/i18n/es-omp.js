/* Spanish: omp (Capítulo 5, el modelo óptico) */
WT.es.ch.omp = {
  num: "Capítulo 5", title: "Una bola de cristal nublada", short: "Modelo óptico",
  lead: "Antes que nada, el motor se hace una pregunta más sencilla: ¿cómo ve el núcleo un neutrón que llega?",
  html: `
<div class="step">
  <p>En mecánica cuántica un neutrón es también una onda. La imagen muestra una que llega rodando desde la izquierda, con sus crestas como bandas brillantes, hacia un núcleo (el círculo discontinuo). Todavía nada actúa sobre ella, así que las crestas lo atraviesan sin cambiar.</p>
  <div class="ctl"><label for="omp-e">Energía del neutrón (MeV)</label><input id="omp-e" type="range" data-bind="E" min="0.2" max="40" step="0.1" value="8"><output data-show="E" data-fmt="1"></output></div>
  <p>Arrastra la energía y mira abajo la longitud de onda, en femtómetros (fm, 10⁻¹⁵ m). Los neutrones lentos tienen ondas largas: por debajo de unos 9 MeV, una longitud de onda es más ancha que todo este núcleo.</p>
</div>
<div class="step">
  <h3>La parte real atrae</h3>
  <p>El <b>potencial óptico</b> es la fuerza promedio de todo el núcleo sobre el neutrón. Su <em>parte real</em> es un pozo de unos 50 MeV de profundidad: dentro, el neutrón se acelera, así que las crestas se apiñan. El motor le da una forma de Woods–Saxon, plana y profunda en el centro, que se desvanece suavemente hasta cero en la superficie.</p>
</div>
<div class="step">
  <h3>La parte imaginaria absorbe</h3>
  <p>La sombra detrás del núcleo son los neutrones perdidos en reacciones. La <em>parte imaginaria</em> del potencial los representa: encoge la onda en lugar de desviarla, sobre todo cerca de la superficie (el anillo de color).</p>
  <div class="ctl"><label for="omp-w">Absorción W (MeV)</label><input id="omp-w" type="range" data-bind="W" min="0" max="14" step="0.5" value="7"><output data-show="W" data-fmt="1"></output></div>
  <p>Lleva <i>W</i> a 0 y la sombra se rellena: sin absorción no hay reacciones. De ahí el nombre de modelo óptico: el núcleo es una bola de cristal nublada que en parte desvía y en parte absorbe.</p>
</div>
<div class="step">
  <h3>La puntería importa</h3>
  <p>Visto de frente, el blanco se divide en anillos, uno por cada <b>onda parcial</b> <i>l</i> = 0, 1, 2, … Un neutrón que pasa a una distancia <i>b</i> del centro lleva un <b>momento angular</b> <i>l</i> ≈ <i>k b</i>, donde <i>k</i> crece con la energía. Cuanto más oscuro es un anillo, mayor es su <b>coeficiente de transmisión</b> <i>T<sub>l</sub></i>: la probabilidad de que un neutrón de ese anillo sea absorbido.</p>
  <div class="ctl"><label for="omp-e3">Energía del neutrón (MeV)</label><input id="omp-e3" type="range" data-bind="E" min="0.2" max="40" step="0.1" value="8"><output data-show="E" data-fmt="1"></output></div>
  <div class="btns"><button class="btn" data-act="fire">Disparar 200 neutrones</button></div>
  <p>Los destellos naranjas son neutrones absorbidos; las barras comparan la fracción absorbida en cada anillo con el <i>T<sub>l</sub></i> del modelo (la marca). Los anillos interiores lo absorben casi todo; los exteriores dejan pasar los neutrones. A baja energía los anillos son enormes y solo importa <i>l</i> = 0.</p>
</div>
<div class="step">
  <h3>Pasar de largo junto al núcleo</h3>
  <p>Un neutrón con mucho momento angular pasa demasiado lejos para tocar el núcleo: esa es la <b>barrera centrífuga</b>. Visto desde arriba, cada neutrón de aquí pertenece a una misma onda parcial <i>l</i>, así que pasa a la misma <b>distancia de paso</b> <i>b</i> ≈ (<i>l</i>+½)/<i>k</i> (el círculo discontinuo).</p>
  <p>Pero cada neutrón es una onda, difuminada sobre aproximadamente una longitud de onda reducida λ̄ (el halo). Aunque su trayectoria no acierte, el borde difuso puede rozar la superficie y entrar: el <b>efecto túnel</b>.</p>
  <div class="ctl"><label for="omp-l">Onda parcial l</label><input id="omp-l" type="range" data-bind="L" min="0" max="8" step="1" value="3" data-instant><output data-show="L" data-fmt="0"></output></div>
  <div class="ctl"><label for="omp-e2">Energía (MeV)</label><input id="omp-e2" type="range" data-bind="E" min="0.2" max="40" step="0.1" value="8"><output data-show="E" data-fmt="1"></output></div>
  <p>Sube <i>l</i> y la trayectoria se aleja: entran menos. Sube la energía y la misma <i>l</i> pasa más cerca, con menos difuminado. El motor calcula cada <i>T<sub>l</sub></i> de forma exacta resolviendo la ecuación de Schrödinger a través del potencial completo; <i>S</i> mide cuánta onda vuelve a salir.</p>
  <div class="formula">T<sub>lj</sub> = 1 − |S<sub>lj</sub>|²</div>
</div>
<div class="step">
  <h3>Sumar el blanco</h3>
  <p>El disco de la derecha es lo grande que el núcleo le parece al neutrón: la <b>sección eficaz de reacción</b>, en barns (10⁻²⁴ cm²). Cada anillo le añade su área por <i>T<sub>l</sub></i>. El círculo discontinuo es el tamaño geométrico.</p>
  <div class="ctl"><label for="omp-e4">Energía del neutrón (MeV)</label><input id="omp-e4" type="range" data-bind="E" min="0.2" max="40" step="0.1" value="8"><output data-show="E" data-fmt="1"></output></div>
  <div class="btns"><button class="btn ghost" data-act="sum">Volver a sumar</button></div>
  <p>Cambia la energía y la suma vuelve a empezar: a baja energía, uno o dos anillos grandes forman casi todo el disco; a alta energía, muchos anillos finos añaden tajadas y el disco se acerca al tamaño geométrico.</p>
  <div class="formula">σ<sub>R</sub> = (π/k²) Σ (2l+1) T<sub>l</sub></div>
  <p>Los <i>T<sub>l</sub></i> alimentan el resto del motor: deciden con qué frecuencia se forma cada espín del núcleo excitado y, al revés, con qué facilidad cada partícula vuelve a salir.</p>
  <div class="aside">En el código: <code>omp/parameters.py</code> (potencial global de Koning–Delaroche; potenciales dispersivos para actínidos), <code>omp/schrodinger.py</code> (integración de Numerov y empalme coulombiano), <code>omp/inverse.py</code> (partículas salientes por balance detallado), <code>omp/regional.py</code> (opcional, desactivado por defecto: un ajuste regional del pozo para blancos deformados de tierras raras, ajustado a S₀ y S₁ medidos).</div>
</div>`,
};
Object.assign(WT.es.labels, {
  "absorbing surface": "superficie absorbente",
  "shadow: neutrons lost to reactions": "sombra: neutrones perdidos en reacciones",
  "wavelength {#} fm   ·   nucleus {#} fm across": "longitud de onda {#} fm   ·   núcleo de {#} fm",
  "crests crowd inside the well": "las crestas se apiñan en el pozo",
  "l={#}": "l={#}",
  "nuclear radius": "radio nuclear",
  "reaction cross section ≈ {#} b": "sección eficaz de reacción ≈ {#} b",
  "geometric size π(R+λ̄)² ≈ {#} b · darker ring = more absorbed · orange flash = absorbed": "tamaño geom. π(R+λ̄)² ≈ {#} b · más oscuro = más absorción · naranja = absorbido",
  "absorbed, ring by ring": "absorbidos, anillo a anillo",
  "bar: your neutrons · tick: model Tₗ": "barra: los tuyos · marca: Tₗ",
  "rings: shade = Tₗ": "anillos: tono = Tₗ",
  "geometric size π(R+λ̄)²": "tamaño geométrico π(R+λ̄)²",
  "reaction cross section": "sección eficaz de reacción",
  "ring l={#}: ({#}l+{#})·Tₗ·π/k² = +{#} b": "anillo l={#}: ({#}l+{#})·Tₗ·π/k² = +{#} b",
  "all {#} rings added": "los {#} anillos sumados",
  "σ_R = {#} b": "σ_R = {#} b",
  "geometric {#} b": "geométrico {#} b",
  "geometric {#} b · darker = more absorbed · orange = absorbed": "geométrico {#} b · más oscuro = más absorción · naranja = absorbido",
  "swing distance b ≈ (l+½)/k = {#} fm": "distancia de paso b ≈ (l+½)/k = {#} fm",
  "nuclear radius R = {#} fm · wave fuzz λ̄ = {#} fm": "radio nuclear R = {#} fm · difuminado λ̄ = {#} fm",
  "path crosses the nucleus: most get in": "la trayectoria cruza el núcleo: casi todos entran",
  "path misses the nucleus: only the fuzzy edge can tunnel in": "la trayectoria pasa fuera: solo el borde difuso entra por túnel",
  "absorbed {#} of {#} · model Tₗ = {#}": "absorbidos {#} de {#} · Tₗ del modelo = {#}",
});
