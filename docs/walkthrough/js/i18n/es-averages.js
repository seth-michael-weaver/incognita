/* Spanish: averages (Capítulo 21, experto: de las resonancias a los promedios) */
WT.L.ch.averages = {
  num: "Capítulo 21", title: "De las resonancias a los promedios", short: "De resonancias a promedios",
  lead: "El capítulo 10 dibujó escaleras de resonancias. Aquí aparecen como secciones eficaces: la fórmula de la matriz R, la estadística que hay detrás de los parámetros, el efecto de la temperatura y cómo un promedio sobre muchas resonancias se convierte en Hauser–Feshbach.",
  html: `
<div class="step">
  <h3>Matriz R, nivel a nivel</h3>
  <p>Por debajo de unos pocos keV, en un núcleo pesado, cada nivel compuesto aparece por separado y la sección eficaz se escribe de forma exacta en función de los parámetros de los niveles: energías <i>E</i><sub>λ</sub>, anchuras neutrónicas reducidas y anchuras de captura. Las evaluaciones usan la teoría de la <b>matriz R</b>, casi siempre en la forma de <b>Reich–Moore</b>, que conserva la interferencia entre niveles en el canal neutrónico y trata los muchos canales de captura como una única anchura absorbente.</p>
  <div class="formula">R(E) = Σ<sub>λ</sub> γ<sub>λ</sub>² / (E<sub>λ</sub> − E − iΓ<sub>λγ</sub>/2) ,  U = e<sup>−2iφ</sup> (1 + iPR) / (1 − iPR)</div>
  <div class="formula">σ<sub>tot</sub> = (2π/k²) g (1 − Re U) ,  σ<sub>γ</sub> = (π/k²) g (1 − |U|²)</div>
  <div class="btns"><button class="btn ghost" data-act="rm" aria-pressed="true">Reich–Moore</button><button class="btn ghost" data-act="bw" aria-pressed="false">Breit–Wigner de un nivel</button></div>
  <p>La línea de arriba es la sección eficaz total; la de abajo, la de captura, para una escalera de niveles de onda s sobre un blanco de espín 0, parecido al uranio-238. Entre niveles la total cae por debajo de la dispersión de potencial, donde se cancelan las amplitudes de resonancia y de potencial. La forma de un nivel suma las secciones eficaces de los niveles en lugar de sus amplitudes; se acerca en los picos y falla en los valles, donde se suman las colas de muchos niveles y la total puede incluso volverse negativa.</p>
</div>
<div class="step">
  <h3>La estadística detrás de los parámetros</h3>
  <p>Un núcleo no medido no tiene escalera, solo sus promedios: <i>D</i>₀, la función de fuerza <i>S</i>₀ = ⟨Γ<sub>n</sub>⁰⟩/<i>D</i>₀ y ⟨Γ<sub>γ</sub>⟩. La teoría de matrices aleatorias da el resto: los espaciados entre niveles de un mismo espín y paridad siguen la distribución de Wigner, y las anchuras neutrónicas reducidas siguen Porter–Thomas, una χ² con un grado de libertad.</p>
  <div class="formula">P(s) = (πs/2) e<sup>−πs²/4</sup> ,  P(y) = e<sup>−y/2</sup> / √(2πy) ,  s = espaciado/D₀, y = Γ<sub>n</sub>⁰/⟨Γ<sub>n</sub>⁰⟩</div>
  <div class="btns"><button class="btn" data-act="more">Sortear diez escaleras más</button></div>
  <p>Los histogramas recogen los espaciados y las anchuras de todas las escaleras sorteadas hasta ahora; las curvas son las dos leyes. La anchura de captura, una suma sobre cientos de canales de fotones, apenas fluctúa, así que se toma como fija.</p>
</div>
<div class="step">
  <h3>El calor difumina los picos</h3>
  <p>Los núcleos del blanco se mueven. Un neutrón de energía <i>E</i> los encuentra con una dispersión de energías relativas de anchura Δ = √(4<i>E</i> <i>kT</i>/<i>A</i>), y cada resonancia se ve a través de esa dispersión: el <b>ensanchamiento Doppler</b>. Para un solo nivel el resultado es la función ψ, una lorentziana convolucionada con una gaussiana.</p>
  <div class="formula">σ<sub>γ</sub>(E,T) = σ₀ (Γ<sub>γ</sub>/Γ) ψ(x, ξ) ,  x = 2(E − E<sub>λ</sub>)/Γ ,  ξ = Γ/Δ</div>
  <div class="ctl"><label for="av-t">Temperatura (K)</label><input id="av-t" type="range" data-bind="TK" min="0" max="3000" step="10" value="300"><output data-show="TK" data-fmt="0"></output></div>
  <p>La resonancia ampliada es la más intensa de las primeras de la escalera; la línea discontinua es su forma a 0 K. El calor baja el pico y ensancha las alas, y el área bajo el pico de captura no cambia. En una muestra gruesa eso no es neutro: el pico está autoapantallado y las alas no, así que un combustible más caliente captura más. Es la realimentación Doppler de un reactor.</p>
</div>
<div class="step">
  <h3>El promedio es Hauser–Feshbach</h3>
  <p>Promediada sobre muchas resonancias, la captura se convierte en una función suave de la energía. La ventana se desliza por la escalera y su promedio se va representando a su paso; las líneas suaves son el valor de Hauser–Feshbach con las transmisiones <i>T<sub>n</sub></i> = 2π⟨Γ<sub>n</sub>⟩/<i>D</i> y <i>T<sub>γ</sub></i> = 2π⟨Γ<sub>γ</sub>⟩/<i>D</i>.</p>
  <div class="ctl"><label for="av-w">Anchura de la ventana (niveles)</label><input id="av-w" type="range" data-bind="win" min="2" max="40" step="1" value="12" data-instant><output data-show="win" data-fmt="0"></output></div>
  <div class="btns"><button class="btn ghost" data-act="ladder">Otra escalera</button></div>
  <p>Una ventana estrecha da mucha dispersión: pocas resonancias, anchuras de Porter–Thomas. Una ancha se asienta sobre la línea de abajo, la que incluye la corrección por fluctuaciones de anchura. La línea de arriba, el producto de los promedios, es aquí entre un 25 y un 47 % demasiado alta, sobre todo donde ⟨Γ<sub>n</sub>⟩ es de una a tres veces ⟨Γ<sub>γ</sub>⟩, desde unos 100 eV hasta 1 keV. (Con ondas p y más canales abiertos la corrección es menor.) Para un solo canal neutrónico con anchuras de Porter–Thomas y una anchura de captura fija, el valor corregido es exacto: (2π²/k²<i>D</i>) <i>g</i> ⟨Γ<sub>n</sub>Γ<sub>γ</sub>/Γ⟩.</p>
</div>
<div class="step">
  <h3>Resuelta, no resuelta, suave</h3>
  <p>Lo que resuelve una medida depende de su resolución en energía, que empeora al subir la energía. La línea es la sección eficaz tal como la ve un instrumento, ensanchada por una resolución que crece como <i>E</i><sup>3/2</sup>, como en tiempo de vuelo. A baja energía cada nivel aparece aislado y sus parámetros pueden ajustarse: la región de resonancias resueltas. Más arriba los niveles se funden en una banda fluctuante cuya estadística se conoce pero cuyos picos individuales no: la región no resuelta, descrita por parámetros medios y, para el autoapantallamiento, por tablas de probabilidad construidas a partir de escaleras sorteadas. Por encima, toman el relevo Hauser–Feshbach y el modelo óptico.</p>
  <div class="ctl"><label for="av-r">Resolución del instrumento (relativa)</label><input id="av-r" type="range" data-bind="res" min="0.2" max="3" step="0.05" value="1"><output data-show="res" data-fmt="2"></output></div>
  <p>La biblioteca de INCOGNITA todavía no tiene región de resonancias resueltas. Sus curvas son promedios de Hauser–Feshbach hasta las energías más bajas; donde hay resonancias medidas resueltas, la página <a href="data.html" data-keep-lang>Todos los núclidos</a> marca la curva como un promedio. Los parámetros de resonancia, y las secciones eficaces puntuales con ensanchamiento Doppler construidas a partir de ellos, están en desarrollo.</p>
  <div class="aside">En el código: <code>physics/resonance/ladder.py</code> (espaciados de matrices aleatorias, anchuras de Porter–Thomas, secciones eficaces de un nivel, conjuntos de escaleras), <code>ladder_statistics.py</code> (las leyes puestas a prueba con escaleras medidas), <code>compound/wfc.py</code> (la corrección por fluctuaciones de anchura hacia la que convergen los promedios). Las fórmulas de Reich–Moore, ψ–χ y resolución de la imagen se evalúan aquí, con parámetros ilustrativos parecidos a los del uranio-238; el motor de Hauser–Feshbach, y por tanto la biblioteca, todavía no calcula secciones eficaces en la región de resonancias.</div>
</div>`,
};
(function () {
  const L = {
    "{#} eV": "{#} eV", "{#} keV": "{#} keV", "{#} b": "{#} b", "{#}k b": "{#}k b",
    // scene 1: R-matrix
    "potential scattering {#}πR′² ≈ {#} b": "dispersión de potencial {#}πR′² ≈ {#} b",
    "Reich–Moore (dashed: single-level)": "Reich–Moore (discontinua: un nivel)",
    "single-level Breit–Wigner (dashed: Reich–Moore)": "Breit–Wigner de un nivel (discontinua: Reich–Moore)",
    "total": "total", "capture": "captura",
    // scene 2: statistics
    "spacings: Wigner": "espaciados: Wigner",
    "s = spacing / D₀": "s = espaciado / D₀",
    "reduced neutron widths: Porter–Thomas": "anchuras neutrónicas reducidas: Porter–Thomas",
    "y = Γn⁰ / ⟨Γn⁰⟩": "y = Γn⁰ / ⟨Γn⁰⟩",
    "{#} ladders · {#} spacings": "{#} escaleras · {#} espaciados",
    "s = {#}": "s = {#}",
    // scene 3: Doppler
    "capture near the {#} eV resonance": "captura cerca de la resonancia de {#} eV",
    "area {#} b·eV ({#} K: {#})": "área {#} b·eV ({#} K: {#})",
    "target nuclei at {#} K": "núcleos del blanco a {#} K",
    "target nuclei at rest": "núcleos del blanco en reposo",
    // scene 4: the average
    "Hauser–Feshbach, no correction": "Hauser–Feshbach, sin corrección",
    "with width fluctuations": "con fluctuaciones de anchura",
    "average capture cross section": "sección eficaz de captura media",
    "{#} levels around {#} eV: {#} b · HF {#} b without, {#} b with the correction": "{#} niveles en torno a {#} eV: {#} b · HF {#} b sin corrección, {#} b con ella",
    // scene 5: resolved, unresolved
    "resolved": "resuelta", "unresolved": "no resuelta", "averaged": "promediada",
    "capture as measured with finite resolution · dashed: Hauser–Feshbach with fluctuations": "captura medida con resolución finita · discontinua: Hauser–Feshbach con fluctuaciones",
    "resolution reaches D₀/{#} at {#} eV": "la resolución llega a D₀/{#} a {#} eV",
    "resolution reaches D₀/{#} at {#} keV": "la resolución llega a D₀/{#} a {#} keV",
    "time of flight: the arrival time measures the energy": "tiempo de vuelo: el instante de llegada mide la energía",
  };
  // axis ticks "10² b": the 10 is the number, the exponent stays
  for (const s of ["⁻³", "⁻²", "⁻¹", "⁰", "¹", "²", "³", "⁴", "⁵", "⁶"]) L[`{#}${s} b`] = `{#}${s} b`;
  // cross sections printed as "12 b" or "3.4k b"
  const B = ["{#} b", "{#}k b"];
  for (const a of B) for (const b of B) {
    L[`{#} eV · total ${a} · capture ${b}`] = `{#} eV · total ${a} · captura ${b}`;
    L[`Γ = {#} meV · Δ = {#} meV · peak ${a} ({#} K: ${b})`] = `Γ = {#} meV · Δ = {#} meV · pico ${a} ({#} K: ${b})`;
  }
  Object.assign(WT.L.labels, L);
})();
Object.assign(WT.L.glossary, {
  rMatrix: {
    term: "Teoría de la matriz R", aliases: ["matriz R"],
    short: "La descripción exacta de las reacciones resonantes mediante energías de nivel y anchuras reducidas dentro de un radio de canal, empalmadas con ondas libres fuera de él.",
    more: "Las evaluaciones ajustan sus parámetros a las resonancias medidas. Las formas de Breit–Wigner de un nivel y de varios niveles y la de Reich–Moore son aproximaciones a la teoría completa.",
    chapter: "averages",
  },
  reichMoore: {
    term: "Reich–Moore", aliases: ["Reich–Moore", "Reich-Moore"],
    short: "La aproximación de la matriz R usada en la mayoría de las evaluaciones de núcleos pesados: los canales neutrónicos se tratan de forma exacta y los muchos canales de fotones, como una única anchura absorbente por nivel.",
    chapter: "averages",
  },
  doppler: {
    term: "Ensanchamiento Doppler", aliases: ["ensanchamiento Doppler"],
    short: "El difuminado de las resonancias por el movimiento térmico de los núcleos del blanco: el pico baja y las alas se ensanchan, mientras que el área de un pico aislado se mantiene.",
    formula: "Δ = √(4 E kT / A)",
    chapter: "averages",
  },
  resolvedRegion: {
    term: "Regiones de resonancias resueltas y no resueltas", aliases: ["región de resonancias resueltas", "región no resuelta"],
    short: "Por debajo de cierta energía cada resonancia se mide por separado (resueltas); por encima solo se conocen sus parámetros medios (no resueltas), hasta que los promedios se vuelven suaves.",
    more: "En la región no resuelta el autoapantallamiento se trata con tablas de probabilidad, distribuciones de la sección eficaz construidas a partir de escaleras de resonancias sorteadas.",
    chapter: "averages",
  },
});
