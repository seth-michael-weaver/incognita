/* Spanish: omp (Capítulo 2, el modelo óptico) */
WT.es.ch.omp = {
  num: "Capítulo 2", title: "Una bola de cristal nublada", short: "Modelo óptico",
  lead: "Antes que nada, el motor se hace una pregunta más sencilla: ¿cómo ve el núcleo un neutrón que llega?",
  html: `
<div class="step">
  <p>La imagen muestra un neutrón como una onda que llega rodando desde la izquierda; las bandas brillantes son sus crestas. En mecánica cuántica toda partícula se comporta también como una onda. El círculo discontinuo es el núcleo. Todavía nada actúa sobre la onda, así que las crestas lo atraviesan sin cambiar.</p>
  <div class="ctl"><label for="omp-e">Energía del neutrón (MeV)</label><input id="omp-e" type="range" data-bind="E" min="0.2" max="40" step="0.1" value="8"><output data-show="E" data-fmt="1"></output></div>
  <p>Arrastra la energía y mira abajo la longitud de onda (la distancia entre crestas), en femtómetros (fm, 10⁻¹⁵ m). Los neutrones lentos tienen ondas largas: por debajo de 1 MeV, más o menos, una longitud de onda es más ancha que el núcleo entero.</p>
</div>
<div class="step">
  <h3>La parte real atrae</h3>
  <p>Ahora las crestas se apiñan dentro del círculo. Los 56 nucleones atraen al neutrón hacia dentro, como un pozo de unos 50 MeV de profundidad. Dentro, el neutrón se acelera, así que su longitud de onda se acorta. Este pozo es la primera mitad del <b>potencial óptico</b>: la fuerza promedio que todo el núcleo ejerce sobre el neutrón. Los físicos la llaman la <em>parte real</em>. El motor le da una forma suave de Woods–Saxon: plana y profunda en el centro, y se desvanece hasta cero en aproximadamente medio femtómetro en la superficie.</p>
</div>
<div class="step">
  <h3>La parte imaginaria absorbe</h3>
  <p>Ahora la onda detrás del núcleo es más tenue, y un anillo de color marca la superficie. A veces el neutrón choca con un nucleón e inicia una reacción, así que sale de la onda. El modelo lo incorpora como la segunda mitad del potencial, la <em>parte imaginaria</em>: un término que encoge la onda en lugar de desviarla. Actúa sobre todo cerca de la superficie. La sombra detrás del núcleo son los neutrones perdidos en reacciones.</p>
  <div class="ctl"><label for="omp-w">Absorción W (MeV)</label><input id="omp-w" type="range" data-bind="W" min="0" max="14" step="0.5" value="7"><output data-show="W" data-fmt="1"></output></div>
  <p>Lleva <i>W</i> a 0 y la sombra se rellena: sin absorción no hay reacciones. Por eso se llama modelo óptico: el núcleo se comporta como una bola de cristal nublada, que en parte desvía la luz y en parte la absorbe.</p>
</div>
<div class="step">
  <h3>La puntería importa</h3>
  <p>Ahora miras el núcleo de frente, como lo ve el neutrón. Un neutrón que pasa a una distancia <i>b</i> del centro lleva un <b>momento angular</b> (cuánto gira alrededor del centro) <i>l</i> ≈ <i>k b</i>, donde <i>k</i> crece con la energía. Así que el blanco se divide en anillos, uno por cada número entero <i>l</i> = 0, 1, 2, … Cada anillo es una <b>onda parcial</b>. Cuanto más oscuro es un anillo, mayor es su <b>coeficiente de transmisión</b> <i>T<sub>l</sub></i>: la probabilidad de que un neutrón de ese anillo sea absorbido. </p>
  <div class="ctl"><label for="omp-e3">Energía del neutrón (MeV)</label><input id="omp-e3" type="range" data-bind="E" min="0.2" max="40" step="0.1" value="8"><output data-show="E" data-fmt="1"></output></div>
  <div class="btns"><button class="btn" data-act="fire">Disparar 200 neutrones</button></div>
  <p>Los destellos naranjas son neutrones absorbidos. Las barras sobre el blanco cuentan tu ráfaga anillo por anillo: el relleno naranja es la fracción de neutrones de ese anillo que fueron absorbidos, y la marca oscura es el <i>T<sub>l</sub></i> del modelo. Cada pulsación empieza una cuenta nueva; con 200 neutrones las barras quedan cerca de las marcas. Los anillos interiores lo absorben casi todo; los exteriores dejan pasar los neutrones de largo. A baja energía los anillos son enormes y solo importa <i>l</i> = 0.</p>
</div>
<div class="step">
  <h3>Pasar de largo junto al núcleo</h3>
  <p>La imagen mira el núcleo desde arriba. Cada neutrón que ves pertenece a una misma onda parcial <i>l</i>, así que pasa de largo a la misma <b>distancia de paso</b> <i>b</i> ≈ (<i>l</i>+½)/<i>k</i> (el círculo discontinuo; la banda tenue es su anillo del paso anterior). Esa es la barrera: un neutrón con mucho momento angular simplemente pasa demasiado lejos para tocar el núcleo. Los físicos lo dibujan como una colina, la <b>barrera centrífuga</b>, pero es lo mismo.</p>
  <p>Pero un neutrón es una onda, y el halo alrededor de cada uno es su difuminado, de aproximadamente una longitud de onda reducida λ̄ de ancho. Incluso cuando la trayectoria no acierta, el borde difuso puede rozar la superficie y el neutrón todavía puede entrar. Eso es el <b>efecto túnel</b>.</p>
  <div class="ctl"><label for="omp-l">Onda parcial l</label><input id="omp-l" type="range" data-bind="L" min="0" max="8" step="1" value="3" data-instant><output data-show="L" data-fmt="0"></output></div>
  <div class="ctl"><label for="omp-e2">Energía (MeV)</label><input id="omp-e2" type="range" data-bind="E" min="0.2" max="40" step="0.1" value="8"><output data-show="E" data-fmt="1"></output></div>
  <p>Sube <i>l</i> y la trayectoria se aleja: entran menos. Sube la energía: <i>k</i> crece, así que la misma <i>l</i> pasa más cerca, y además el difuminado se encoge. El contador compara lo que ves con el <i>T<sub>l</sub></i> del modelo. El motor calcula cada <i>T<sub>l</sub></i> de forma exacta. Resuelve la ecuación de Schrödinger (la ecuación de ondas básica de la mecánica cuántica) hacia fuera a través del potencial completo y la empalma con una onda libre en el exterior. <i>S</i> mide cuánta onda vuelve a salir; el resto fue absorbido.</p>
  <div class="formula">T<sub>lj</sub> = 1 − |S<sub>lj</sub>|²</div>
</div>
<div class="step">
  <h3>Sumar el blanco</h3>
  <p>A la izquierda vuelven a estar los anillos. Uno a uno, cada anillo se eleva, conserva solo la parte de su área que absorbe (su área por <i>T<sub>l</sub></i>) y vuela hacia el disco de la derecha. El disco crece anillo a anillo. Cuando todos los anillos están dentro, su área es lo grande que el núcleo le parece al neutrón: la <b>sección eficaz de reacción</b>, medida en barns (1 barn = 10⁻²⁴ cm²). El círculo discontinuo es el tamaño geométrico del núcleo, para comparar.</p>
  <div class="ctl"><label for="omp-e4">Energía del neutrón (MeV)</label><input id="omp-e4" type="range" data-bind="E" min="0.2" max="40" step="0.1" value="8"><output data-show="E" data-fmt="1"></output></div>
  <div class="btns"><button class="btn ghost" data-act="sum">Volver a sumar</button></div>
  <p>Cambia la energía y la suma vuelve a empezar. A baja energía, uno o dos anillos grandes forman casi todo el disco; a alta energía, muchos anillos finos añaden cada uno una tajada, y el disco se acerca al tamaño geométrico.</p>
  <div class="formula">σ<sub>R</sub> = (π/k²) Σ (2l+1) T<sub>l</sub></div>
  <p>Los valores de <i>T<sub>l</sub></i> alimentan el resto del motor. Deciden con qué frecuencia se forma cada espín del núcleo excitado y, al revés, con qué facilidad cada tipo de partícula vuelve a salir.</p>
  <div class="aside">En el código: <code>omp/parameters.py</code> (potencial global de Koning–Delaroche; potenciales dispersivos para actínidos), <code>omp/schrodinger.py</code> (integración de Numerov y empalme coulombiano), <code>omp/inverse.py</code> (partículas salientes por balance detallado).</div>
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
  "swing distance b ≈ (l+½)/k = {#} fm": "distancia de paso b ≈ (l+½)/k = {#} fm",
  "nuclear radius R = {#} fm · wave fuzz λ̄ = {#} fm": "radio nuclear R = {#} fm · difuminado λ̄ = {#} fm",
  "path crosses the nucleus: most get in": "la trayectoria cruza el núcleo: casi todos entran",
  "path misses the nucleus: only the fuzzy edge can tunnel in": "la trayectoria pasa fuera: solo el borde difuso entra por túnel",
  "absorbed {#} of {#} · model Tₗ = {#}": "absorbidos {#} de {#} · Tₗ del modelo = {#}",
});
