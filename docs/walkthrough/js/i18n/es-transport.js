/* Spanish: transport (Lección 1, transporte de neutrones y Monte Carlo) */
WT.L.ch.transport = {
  num: "Lección 1", title: "Transporte de neutrones y Monte Carlo", short: "Monte Carlo",
  html: `
<div class="step">
  <h3>La ecuación de transporte</h3>
  <p>En rigor, los neutrones obedecen la ecuación de Boltzmann para el flujo angular <i>ψ</i>(<b>r</b>, <b>Ω</b>, <i>E</i>): <b>Ω</b>·∇<i>ψ</i> + Σ<sub>t</sub><i>ψ</i> = ∫∫Σ<sub>s</sub><i>ψ</i>′ d<b>Ω</b>′d<i>E</i>′ + (<i>χ</i>/4π<i>k</i>)∫<i>ν</i>Σ<sub>f</sub><i>φ</i>′ d<i>E</i>′. Monte Carlo la resuelve jugando los neutrones de uno en uno: un vuelo de <i>s</i> = −ln <i>ξ</i> / Σ<sub>t</sub>, y después dispersión, captura o fisión.</p>
  <div class="btns"><button class="btn" data-act="trnew">Nuevo neutrón</button></div>
</div>
<div class="step">
  <h3>Donde falla la difusión</h3>
  <p>La difusión supone un flujo casi igual en todas las direcciones. Eso falla a uno o dos recorridos libres de una superficie y en absorbentes fuertes. Compárala con el flujo Monte Carlo en una placa con fuente uniforme mientras subes la absorción.</p>
  <div class="ctl"><label for="tr-pa">Absorción Σ<sub>a</sub>/Σ<sub>t</sub></label><input id="tr-pa" type="range" data-bind="pa" data-instant min="0.05" max="0.8" step="0.05" value="0.5"><output data-show="pa" data-fmt="2"></output></div>
</div>
<div class="step">
  <h3>Iteración de potencia</h3>
  <p>Para <i>k</i><sub>eff</sub>, los puntos de fisión de cada generación se convierten en la fuente de la siguiente; <i>k</i> es el número de puntos guardados por neutrón lanzado. Parte de una mala estimación, todos los neutrones en un borde, y mira cómo la fuente se extiende hasta el modo fundamental.</p>
  <div class="btns"><button class="btn" data-act="trbad">Reiniciar desde una mala estimación</button></div>
</div>
<div class="step">
  <h3>¿Ha convergido la fuente?</h3>
  <p>La entropía de Shannon <i>H</i> = −Σ <i>p</i><sub>b</sub> log<sub>2</sub> <i>p</i><sub>b</sub> de la fuente repartida en intervalos se estabiliza cuando la fuente se ha asentado; solo entonces se promedian las generaciones. La barra de error de <i>k</i> se reduce como 1/√<i>N</i> con las historias contadas.</p>
  <div class="ctl"><label for="tr-n">Historias por generación</label><input id="tr-n" type="range" data-bind="nh" data-instant min="100" max="2000" step="100" value="400"><output data-show="nh" data-fmt="0"></output></div>
</div>`,
};

Object.assign(WT.L.labels, {
  "vacuum": "vacío",
  "glow: collision density": "brillo: densidad de colisiones",
  "amber glow: where collisions pile up": "brillo ámbar: donde se acumulan las colisiones",
  "tap the slab to start neutrons": "toca la placa para lanzar neutrones",
  "scatter": "dispersión",
  "capture": "captura",
  "fission": "fisión",
  "leak": "fuga",
  "chance to fly at least s:  e^(−Σₜ s)": "probabilidad de volar al menos s:  e^(−Σₜ s)",
  "{#} free paths": "{#} recorridos libres",
  "ξ = {#}  →  s = −ln ξ / Σₜ = {#} free paths": "ξ = {#}  →  s = −ln ξ / Σₜ = {#} recorridos libres",
  "infinite medium S/Σₐ": "medio infinito S/Σₐ",
  "Monte Carlo": "Monte Carlo",
  "diffusion": "difusión",
  "flux": "flujo",
  "diffusion vs Monte Carlo: +{#} % at the surface, +{#} % in the middle": "difusión frente a Monte Carlo: +{#} % en la superficie, +{#} % en el centro",
  "diffusion vs Monte Carlo: +{#} % at the surface, {#} % in the middle": "difusión frente a Monte Carlo: +{#} % en la superficie, {#} % en el centro",
  "diffusion vs Monte Carlo: {#} % at the surface, +{#} % in the middle": "difusión frente a Monte Carlo: {#} % en la superficie, +{#} % en el centro",
  "diffusion vs Monte Carlo: {#} % at the surface, {#} % in the middle": "difusión frente a Monte Carlo: {#} % en la superficie, {#} % en el centro",
  "tap: drop the source there": "toca: la fuente va allí",
  "tap the slab to drop the whole source there": "toca la placa para poner allí toda la fuente",
  "generation {#}": "generación {#}",
  "source · dashed: fundamental mode": "fuente · discontinua: modo fundamental",
  "fission source · dashed: fundamental mode": "fuente de fisión · discontinua: modo fundamental",
  "source entropy H (bits)": "entropía de la fuente H (bits)",
  "inactive | active": "inactivas | activas",
  "inactive  |  active generations": "generaciones inactivas  |  activas",
  "k per generation": "k por generación",
  "generation {#}: k = {#} · H = {#} bits": "generación {#}: k = {#} · H = {#} bits",
  "starting…": "empezando…",
  "k_eff = {#} ± {#} ({#} × {#} histories) · diffusion {#}": "k_eff = {#} ± {#} ({#} × {#} historias) · difusión {#}",
  "{#} generations, averaging starts after {#}": "{#} generaciones, el promedio empieza tras {#}",
  "illustrative one-group data": "datos ilustrativos de un grupo",
});
