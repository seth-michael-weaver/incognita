/* Spanish: strength (Capítulo 19, experto: la función de fuerza fotónica, en detalle) */
WT.L.ch.strength = {
  num: "Capítulo 19", title: "La fuerza fotónica, en detalle", short: "Fuerza fotónica",
  lead: "El capítulo 7 mostró qué fotones prefiere un núcleo caliente. Este capítulo escribe las funciones de fuerza, las sigue hasta los coeficientes de transmisión y la anchura radiativa media, y ejecuta la cascada que ponen en marcha.",
  html: `
<div class="step">
  <h3>E1: la cola de la resonancia gigante dipolar</h3>
  <p>La <b>función de fuerza fotónica</b> <i>f<sub>XL</sub></i>(<i>E</i><sub>γ</sub>) es la probabilidad reducida media para un fotón de tipo <i>XL</i>: dipolo eléctrico E1, dipolo magnético M1, etc. Para E1 la domina la resonancia gigante dipolar, cerca de 18 MeV, pero la desexcitación en <i>S<sub>n</sub></i> usa fotones de 1 a 7 MeV, muy abajo en su cola, y la forma de esa cola es toda la cuestión.</p>
  <div class="formula">f<sub>E1</sub> = K σ₀Γ₀ · E<sub>γ</sub> Γ(E<sub>γ</sub>,T) / [(E<sub>γ</sub>² − E₀²)² + E<sub>γ</sub>² Γ(E<sub>γ</sub>,T)²] / (1 − e<sup>−E<sub>γ</sub>/T</sup>) ,  Γ(E<sub>γ</sub>,T) = (Γ₀/E₀)(E<sub>γ</sub> + 4π²T²/E₀)</div>
  <div class="ctl"><label for="ps-t">Temperatura del estado final T (MeV)</label><input id="ps-t" type="range" data-bind="T" min="0" max="1.5" step="0.01" value="0.7"><output data-show="T" data-fmt="2"></output></div>
  <p>La línea discontinua es la lorentziana estándar (SLO), la forma ajustada a la fotoabsorción. Con su anchura constante sobrestima la fuerza en la ventana de desexcitación en un factor de 2 a 5, un fallo conocido desde hace tiempo para núcleos esféricos. La línea continua es la lorentziana modificada simplificada (<b>SMLO</b>): su anchura crece con la energía del fotón y con la temperatura de los estados finales, lo que baja la cola en la ventana pero deja una fuerza finita a energía de fotón cero, como exigen los datos de desexcitación. Lleva <i>T</i> a 0 y ese suelo de baja energía desaparece.</p>
</div>
<div class="step">
  <h3>M1: spin-flip, tijera, upbend</h3>
  <p>La fuerza M1 es más débil, pero no despreciable: una resonancia de spin-flip cerca de 41<i>A</i><sup>−1/3</sup> MeV, un modo tijera cerca de 3 MeV en núcleos deformados (con una fuerza que crece como β²) y un upbend, una subida hacia energía de fotón cero observada en datos del método de Oslo y en cálculos del modelo de capas.</p>
  <div class="ctl"><label for="ps-b">Deformación β (tijera)</label><input id="ps-b" type="range" data-bind="beta" min="0" max="0.35" step="0.01" value="0.2"><output data-show="beta" data-fmt="2"></output></div>
  <div class="btns"><button class="btn ghost" data-act="up" aria-pressed="true">Upbend</button></div>
  <p>La línea tenue del fondo es E1. A las energías de fotón más bajas, por debajo de unos 2 MeV aquí, el upbend permite que M1 rivalice con ella o la supere (el marcador indica dónde), y por eso importa en el extremo blando de la cascada y en la captura lejos de la estabilidad. La M1 por defecto del motor es la recomendación del OIEA con upbend, tabulada núcleo a núcleo, y su E1 por defecto es la SMLO-2019 tabulada; las formas cerradas de aquí sustituyen a esas tablas.</p>
</div>
<div class="step">
  <h3>Brink–Axel</h3>
  <p>La <b>hipótesis de Brink–Axel</b> dice que la fuerza depende de la energía del fotón y no del punto de partida del núcleo: la misma <i>f</i> vale para una resonancia en <i>S<sub>n</sub></i> y para un estado a 4 MeV. (SMLO conserva una dependencia débil a través de <i>T</i>.) Cada energía de partida emite entonces con el coeficiente de transmisión por la densidad de estados finales.</p>
  <div class="formula">T<sub>XL</sub>(E<sub>γ</sub>) = 2π E<sub>γ</sub><sup>2L+1</sup> f<sub>XL</sub>(E<sub>γ</sub>) ,  dΓ/dE<sub>γ</sub> ∝ T<sub>XL</sub>(E<sub>γ</sub>) ρ(E<sub>x</sub> − E<sub>γ</sub>)</div>
  <div class="ctl"><label for="ps-x">Energía de partida Eₓ (MeV)</label><input id="ps-x" type="range" data-bind="Ex" min="2" max="7.6" step="0.05" value="7.6"><output data-show="Ex" data-fmt="2"></output></div>
  <p>El producto de una <i>E</i><sub>γ</sub>³<i>f</i> creciente y una ρ decreciente forma una joroba. Desde <i>S<sub>n</sub></i> tiene aquí su máximo hacia 4 a 5 MeV. Desde puntos de partida más bajos queda cortada en la energía de partida; por debajo de la energía de empalme, donde ρ es una exponencial de temperatura constante, la forma es la misma desde cualquier punto de partida, solo truncada. La hipótesis se pone a prueba comparando fuerzas extraídas a distintas energías de excitación, que es lo que hacen los análisis de tipo Oslo.</p>
</div>
<div class="step">
  <h3>La anchura radiativa media</h3>
  <p>Sumar sobre todos los estados finales accesibles por E1 o M1 desde las resonancias de onda s (<i>J</i><sup>π</sup> = ½⁺ sobre un blanco de espín 0) da su anchura fotónica total media. Se mide, a partir de las formas de las resonancias, para unos cientos de núcleos, y es la principal comprobación de la fuerza en <i>S<sub>n</sub></i>.</p>
  <div class="formula">⟨Γ<sub>γ</sub>⟩ = D₀/2π · Σ<sub>XL</sub> Σ<sub>J′π′</sub> ∫₀^{S<sub>n</sub>} T<sub>XL</sub>(E<sub>γ</sub>) ρ(S<sub>n</sub> − E<sub>γ</sub>, J′, π′) dE<sub>γ</sub></div>
  <div class="ctl"><label for="ps-s">Escala sobre la fuerza</label><input id="ps-s" type="range" data-bind="scale" min="0.3" max="5" step="0.01" value="1"><output data-show="scale" data-fmt="2"></output></div>
  <p>Las curvas muestran de dónde sale la anchura, fotón a fotón: sobre todo de 3 a 7 MeV, y sobre todo E1, con M1 aportando alrededor de un 15 %. Aquí, con formas cerradas y una densidad de niveles esquemática en lugar de las tablas del motor, la anchura sale en torno a un sexto de los 0,92 eV medidos: así de sensible es a la densidad de niveles por debajo de <i>S<sub>n</sub></i> y a la cola de la fuerza. Los valores por defecto de TALYS, que el motor sigue, dan unos 1,3 eV para este núcleo. El control aplica el único factor global que ajustaría una evaluación. La captura en la región de keV es casi proporcional a ⟨Γ<sub>γ</sub>⟩ cuando Γ<sub>γ</sub> ≪ Γ<sub>n</sub>, así que un factor aquí es un factor en (n,γ). TALYS puede reescalar la fuerza a una ⟨Γ<sub>γ</sub>⟩ medida (<code>gnorm</code>); en INCOGNITA ese reescalado, aplicado a todos los núcleos de la cascada, es una opción, desactivada por defecto.</p>
</div>
<div class="step">
  <h3>La cascada</h3>
  <p>Por debajo del primer fotón se repite la misma regla: desde cada nueva energía el siguiente fotón se sortea a partir de <i>T</i>(<i>E</i><sub>γ</sub>) ρ(<i>E<sub>x</sub></i> − <i>E</i><sub>γ</sub>), hasta que el núcleo llega a sus niveles conocidos. Cada historia consta de unos pocos fotones; su espectro sumado es lo que ve un calorímetro tras una captura.</p>
  <div class="btns"><button class="btn ghost" data-act="up2" aria-pressed="true">Upbend</button><button class="btn ghost" data-act="clear">Empezar de nuevo</button></div>
  <p>El upbend añade fotones blandos y un poco de multiplicidad. El motor no sortea historias: traslada poblaciones intervalo a intervalo, de arriba abajo (capítulo 8), lo que da los mismos promedios sin ruido de muestreo.</p>
  <div class="aside">En el código: <code>gamma/strength.py</code> (todos los modelos de fuerza que admite TALYS; por defecto, las tablas SMLO-2019 y la M1 del OIEA con upbend), <code>gamma/parameters.py</code> (sistemáticas de resonancias gigantes, tablas), <code>gamma/transmission.py</code> (T = 2π E<sup>2L+1</sup> f), <code>gamma/ggnorm.py</code> (normalización opcional a ⟨Γγ⟩), <code>emission/</code> (la cascada). La imagen usa formas cerradas y sistemáticas para un núcleo parecido al hierro-57; la ⟨Γγ⟩ medida es el valor de RIPL para el ⁵⁷Fe.</div>
</div>`,
};
(function () {
  const L = {
    "Eγ (MeV)": "Eγ (MeV)", "{#} eV": "{#} eV", "Sₙ": "Sₙ",
    // scene 1: E1
    "E{#} strength f (MeV⁻³), A = {#}": "función de fuerza E{#} f (MeV⁻³), A = {#}",
    "photons that decay uses": "fotones que usa la desexcitación",
    "GDR: E₀ = {#} MeV, Γ₀ = {#} MeV, σ₀ = {#} mb": "GDR: E₀ = {#} MeV, Γ₀ = {#} MeV, σ₀ = {#} mb",
    "dashed: SLO": "discontinua: SLO",
    "at {#} MeV: SMLO / SLO = {#}": "a {#} MeV: SMLO / SLO = {#}",
    "protons against neutrons": "protones contra neutrones",
    // scene 2: M1
    "M{#} strength f (MeV⁻³), A = {#}": "función de fuerza M{#} f (MeV⁻³), A = {#}",
    "spin-flip": "spin-flip",
    "scissors, β = {#}": "tijera, β = {#}",
    "upbend": "upbend",
    "faint: E{#} at T = {#} MeV": "tenue: E{#} a T = {#} MeV",
    "M{#} > E{#} below {#} MeV": "M{#} > E{#} por debajo de {#} MeV",
    "E{#} dominates at every energy here": "aquí E{#} domina a todas las energías",
    "scissors: the two deformed clouds rock": "tijera: las dos nubes deformadas se balancean",
    // scene 3: Brink-Axel
    "from {#} MeV": "desde {#} MeV",
    "peak at Eγ ≈ {#} MeV": "máximo en Eγ ≈ {#} MeV",
    "primary spectrum T(Eγ) ρ(Eₓ − Eγ), each scaled to its peak": "espectro primario T(Eγ) ρ(Eₓ − Eγ), cada uno escalado a su máximo",
    // scene 4: the average radiative width
    "contribution to ⟨Γγ⟩ per MeV of photon energy: E{#} (yellow), M{#} (purple, on top)": "contribución a ⟨Γγ⟩ por MeV de energía del fotón: E{#} (amarillo), M{#} (morado, encima)",
    "measured {#} eV": "medida {#} eV",
    "computed ⟨Γγ⟩ = {#} meV (E{#} {#} %, M{#} {#} %)": "⟨Γγ⟩ calculada = {#} meV (E{#} {#} %, M{#} {#} %)",
    // scene 5: the cascade
    "all photons from all cascades": "todos los fotones de todas las cascadas",
    "{#} cascades · mean multiplicity {#}": "{#} cascadas · multiplicidad media {#}",
  };
  Object.assign(WT.L.labels, L);
})();
Object.assign(WT.L.glossary, {
  smlo: {
    term: "SMLO", aliases: ["SMLO"],
    short: "La lorentziana modificada simplificada: una función de fuerza E1 cuya anchura crece con la energía del fotón y con la temperatura de los estados finales.",
    more: "La propusieron V. Plujko y colaboradores, y está tabulada para todos los núcleos en la base de datos de funciones de fuerza fotónica del OIEA (2019). La E1 por defecto del motor, como la de TALYS-2, es esa tabla SMLO-2019.",
    chapter: "strength",
  },
  brinkAxel: {
    term: "Hipótesis de Brink–Axel", aliases: ["hipótesis de Brink–Axel", "Brink–Axel", "Brink-Axel"],
    short: "La suposición de que la función de fuerza fotónica depende solo de la energía del fotón, no de la energía de excitación del estado que lo emite.",
    more: "Permite que una sola fuerza, medida o calculada para el estado fundamental, sirva para toda la cascada. Se pone a prueba extrayendo fuerzas a distintas energías de excitación; se cumple de forma aproximada, con desviaciones que se discuten para núcleos y energías concretos.",
    chapter: "strength",
  },
});
