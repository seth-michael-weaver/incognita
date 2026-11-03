/* Spanish: fusion (chapter 29, part three: two light nuclei over the Coulomb hill) */
WT.L.ch.fusion = {
  num: "Capítulo 29", title: "La energía de fusión y la barrera de Coulomb", short: "Fusión",
  lead: "La fusión va en sentido contrario a la fisión: dos núcleos ligeros se unen, y el par pesa menos que sus partes.",
  html: `
<div class="step">
  <h3>La energía de fusión a partir de la curva de ligadura</h3>
  <p>Une dos núcleos ligeros: si el nuevo queda más arriba en la curva de ligadura, se libera energía. Pasado el pico del hierro, unirlos cuesta energía.</p>
  <div class="ctl"><label for="fu-a">A de cada núcleo ligero</label><input id="fu-a" type="range" data-bind="fuse" data-instant min="2" max="60" step="1" value="2"><output data-show="fuse" data-fmt="0"></output></div>
  <p class="ctl-result" id="fu-fuse-out" aria-live="polite"></p>
</div>
<div class="step">
  <h3>La barrera de Coulomb y el efecto túnel</h3>
  <p>Tira del deuterón hacia atrás y suéltalo. Los dos núcleos tienen carga, así que la mayoría de los disparos rebotan en la colina; unos pocos la atraviesan por efecto túnel.</p>
  <div class="ctl"><label for="fu-e">Empuje (keV)</label><input id="fu-e" type="range" data-bind="lE" min="0.5" max="2.6" step="0.01" value="1.7"><output data-show="E" data-fmt="0"></output></div>
  <div class="btns"><button class="btn" data-act="fire">Disparar</button></div>
</div>
<div class="step">
  <h3>Productos de la reacción y valor Q</h3>
  <p>El par unido es más ligero que las dos partes. La masa que falta sale despedida en forma de partículas rápidas.</p>
  <div class="btns fu-fuels"><button class="btn ghost" data-act="DT" aria-pressed="true">D–T</button> <button class="btn ghost" data-act="DD" aria-pressed="false">D–D</button> <button class="btn ghost" data-act="DHe" aria-pressed="false">D–³He</button> <button class="btn ghost" data-act="pB" aria-pressed="false">p–¹¹B</button></div>
</div>
<div class="step">
  <h3>Tasa de reacción termonuclear</h3>
  <p>En un gas caliente pasan los núcleos más rápidos. Cada destello es una fusión.</p>
  <div class="ctl"><label for="fu-t">Temperatura (keV)</label><input id="fu-t" type="range" data-bind="lT" min="0" max="2" step="0.01" value="1"><output data-show="T" data-fmt="1"></output></div>
</div>`,
};
Object.assign(WT.L.labels, {
  "B": "B",
  "Copper{#}": "Cobre{#}",
  "Coulomb hill": "Colina de Coulomb",
  "D–D": "D–D",
  "D–T": "D–T",
  "D–³He": "D–³He",
  "E = kT": "E = kT",
  "Gamow peak E₀": "pico de Gamow E₀",
  "K {#} · field lines lost to the wall: {#}": "K {#} · líneas de campo perdidas en la pared: {#}",
  "Q = {#}": "Q = {#}",
  "Q = ∞: no heating needed": "Q = ∞: no hace falta calentar",
  "Silicon{#} (SiC)": "Silicio{#} (SiC)",
  "Steel (iron{#})": "Acero (hierro{#})",
  "Sun's core": "centro del Sol",
  "TBR {#}": "TBR {#}",
  "Tungsten{#}": "Wolframio{#}",
  "Vanadium{#}": "Vanadio{#}",
  "after {#} years at {#} MW/m² · {#} MeV neutrons only · σ from INCOGNITA library v{#}": "tras {#} años a {#} MW/m² · solo neutrones de {#} MeV · σ de la biblioteca de INCOGNITA v{#}",
  "almost never": "casi nunca",
  "alpha {#} MeV": "alfa {#} MeV",
  "axis, q = {#}": "eje, q = {#}",
  "binding per nucleon (MeV)": "ligadura por nucleón (MeV)",
  "bubble-chamber view, magnetic field into the page: charged products curl, the neutron leaves no track": "vista de cámara de burbujas, campo magnético hacia dentro de la página: los productos cargados se curvan, el neutrón no deja traza",
  "burning on its own": "arde por sí solo",
  "cooled down: plasma lost": "enfriado: plasma perdido",
  "cooling": "enfriándose",
  "could not load the library file": "no se pudo cargar la biblioteca",
  "deuteron": "deuterón",
  "deuteron {#} keV": "deuterón {#} keV",
  "deuteron: pull back, let go": "deuterón: tira hacia atrás y suelta",
  "drag or tap a point; it runs on its own": "arrastra o toca un punto; evoluciona solo",
  "easiest: {a} keV, nτT {b}": "más fácil: {a} keV, nτT {b}",
  "edge: q = {#} · lines that cross it are lost": "borde: q = {#} · las líneas que lo cruzan se pierden",
  "electron {#} keV": "electrón {#} keV",
  "energy of the colliding pair (keV)": "energía del par que choca (keV)",
  "few are this fast": "pocos van tan rápido",
  "fusion rate: {a} the rate at {b} keV": "tasa de fusión: {a} la de {b} keV",
  "grain boundary": "límite de grano",
  "heating itself": "se calienta solo",
  "helium stays and gathers into bubbles; hydrogen mostly diffuses out": "el helio se queda y forma burbujas; el hidrógeno se difunde casi todo hacia fuera",
  "helium {#} appm": "helio {#} appm",
  "hill to climb: charge product Z₁Z₂ = {#}": "colina que subir: producto de cargas Z₁Z₂ = {#}",
  "hold: heaters on (Q = fusion power / heating) · let go: heaters off, the plasma is on its own": "mantén: calefacción encendida (Q = potencia de fusión / calefacción) · suelta: calefacción apagada, el plasma queda solo",
  "hydrogen {#} appm": "hidrógeno {#} appm",
  "ignition (Q = ∞)": "ignición (Q = ∞)",
  "kT (keV)": "kT (keV)",
  "kT {#} keV · E₀ {#} keV · width {#} keV": "kT {#} keV · E₀ {#} keV · anchura {#} keV",
  "kT {a} keV · D–T {b} m³/s · {c}× D–D": "kT {a} keV · D–T {b} m³/s · {c}× D–D",
  "keeps itself hot": "autosostenido",
  "laps {#}": "vueltas {#}",
  "lead–lithium": "plomo–litio",
  "liquid lithium": "litio líquido",
  "loading INCOGNITA's cross sections…": "cargando las secciones eficaces de INCOGNITA…",
  "missing {#} u  =  {#} MeV out": "faltan {#} u  =  salen {#} MeV",
  "n τE (s/m³)": "n τE (s/m³)",
  "negative: turns the other way": "negativa: gira al revés",
  "neutron escapes": "el neutrón escapa",
  "peak near {#} keV": "pico cerca de {#} keV",
  "per fusion neutron · {#} neutrons · cross sections are simple fits": "por neutrón de fusión · {#} neutrones · secciones eficaces: ajustes simples",
  "plasma": "plasma",
  "product ×{a}": "producto ×{a}",
  "push {a} keV · chance to tunnel head-on {b}": "empuje {a} keV · probabilidad de túnel de frente {b}",
  "q = {#}": "q = {#}",
  "q = {#}/{#}: closes after {#} lap": "q = {#}/{#}: se cierra tras {#} vuelta",
  "q = {#}/{#}: closes after {#} laps": "q = {#}/{#}: se cierra tras {#} vueltas",
  "q = {#}: no simple fraction, the dots fill the circle": "q = {#}: sin fracción sencilla, los puntos llenan el círculo",
  "screen radius is logarithmic: {#} fm to {#} fm": "radio en pantalla logarítmico: de {#} fm a {#} fm",
  "shield": "blindaje",
  "tap to fire": "toca para disparar",
  "the cut, flat": "el corte, plano",
  "time slowed {a}×": "tiempo {a}× más lento",
  "tries {#} · fused {#}": "intentos {#} · fusiones {#}",
  "tritium made, by depth": "tritio por profundidad",
  "triton": "tritón",
  "tunnels more easily": "túnel más fácil",
  "turns at {#} fm": "rebota a {#} fm",
  "wall": "pared",
  "{#} MeV": "{#} MeV",
  "{#} cm": "{#} cm",
  "{#} in {a}": "{#} entre {a}",
  "{#} keV": "{#} keV",
  "{#} keV = {#} million K": "{#} keV = {#} millones de K",
  "{a} %": "{a} %",
  "{a} + {a} → {b}: about {c} MeV released": "{a} + {a} → {b}: se liberan unos {c} MeV",
  "{a} + {a} → {b}: costs {c} MeV": "{a} + {a} → {b}: cuesta {c} MeV",
  "{a} keV · chance {b}": "{a} keV · probabilidad {b}",
  "{a} keV · nτ {b} · {c}": "{a} keV · nτ {b} · {c}",
  "{a} · two branches, equally likely": "{a} · dos ramas, igual de probables",
  "{a} · ρ up to {b} · {c} turns a second": "{a} · ρ hasta {b} · {c} vueltas por segundo",
  "σ at {#} MeV:  (n,α) {#} mb · (n,p) {#} mb · (n,{#}n) {#} mb": "σ a {#} MeV:  (n,α) {#} mb · (n,p) {#} mb · (n,{#}n) {#} mb",
  "⁶Li {#} · ⁷Li {#} · (n,{#}n) {#}": "⁶Li {#} · ⁷Li {#} · (n,{#}n) {#}",
  "⁶Li {#} · ⁷Li {#} · (n,{#}n) {#} · captured {#} · leaked {#}": "⁶Li {#} · ⁷Li {#} · (n,{#}n) {#} · capturados {#} · fugados {#}",
  "⟨σv⟩ (m³/s)": "⟨σv⟩ (m³/s)",
});
