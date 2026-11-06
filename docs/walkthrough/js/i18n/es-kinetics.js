/* Spanish: kinetics (Lección 1, cinética del reactor: seis grupos y la ecuación inhour) */
WT.L.ch.kinetics = {
  num: "Lección 1", title: "Cinética del reactor: seis grupos y la ecuación inhour", short: "Cinética",
  html: `
<div class="step">
  <h3>Seis grupos de neutrones tardíos</h3>
  <p>Los neutrones retardados proceden de unos seis grupos de productos de fisión, con vidas medias de 0,23 s a 56 s (Keepin, U-235). Los grupos de 2 s y de 22 s emiten la mayoría, mientras que los grupos de vida larga guardan la mayor parte de la reserva en espera: retardo medio Σ <i>a</i><sub>i</sub>/<i>λ</i><sub>i</sub> ≈ 13 s. Detén las fisiones y mira cómo cada grupo se agota a su propio ritmo.</p>
  <div class="btns"><button class="btn" data-act="kistop" aria-pressed="false">Detener fisiones</button></div>
</div>
<div class="step">
  <h3>La ecuación inhour</h3>
  <p>Prueba <i>n</i> ∝ e<sup><i>ωt</i></sup> en la cinética puntual de seis grupos y obtienes <i>ρ</i> = <i>ω</i>Λ + Σ <i>β</i><sub>i</sub><i>ω</i>/(<i>ω</i> + <i>λ</i><sub>i</sub>): siete ramas separadas por los polos en −<i>λ</i><sub>i</sub>. Un escalón de <i>ρ</i> corta cada rama una vez; la raíz más a la derecha da el periodo estable <i>T</i> = 1/<i>ω</i><sub>1</sub>, las otras seis se extinguen.</p>
  <div class="ctl"><label for="ki-r1">Reactividad ρ ($)</label><input id="ki-r1" type="range" data-bind="rd" data-instant min="-2" max="1.3" step="0.01" value="0.3"><output data-show="rd" data-fmt="2"></output></div>
</div>
<div class="step">
  <h3>Salto instantáneo y criticidad instantánea</h3>
  <p>Un escalón de reactividad primero eleva la potencia en milisegundos en un factor <i>P</i><sub>1</sub>/<i>P</i><sub>0</sub> ≈ <i>β</i>/(<i>β</i> − <i>ρ</i>), y después crece con el periodo estable. Con <i>ρ</i> = 1 $ los neutrones instantáneos por sí solos son críticos y el periodo se desploma hacia Λ/(<i>ρ</i> − <i>β</i>).</p>
  <div class="ctl"><label for="ki-r2">Reactividad ρ ($)</label><input id="ki-r2" type="range" data-bind="rj" data-instant min="0.05" max="1.3" step="0.01" value="0.5"><output data-show="rj" data-fmt="2"></output></div>
</div>
<div class="step">
  <h3>Tras un disparo del reactor</h3>
  <p>Introduce una gran reactividad negativa: la potencia cae al instante hasta cerca de <i>β</i>/(<i>β</i> − <i>ρ</i>), y después no puede bajar más deprisa de lo que se desintegra el grupo de vida más larga. Por profundo que sea el disparo, el periodo tiende a −1/<i>λ</i><sub>1</sub> ≈ −80 s.</p>
  <div class="ctl"><label for="ki-r3">Reactividad ρ ($)</label><input id="ki-r3" type="range" data-bind="rs" data-instant min="-30" max="-0.5" step="0.5" value="-10"><output data-show="rs" data-fmt="1"></output></div>
</div>`,
};
/* attributes referenced in the English chapter script (for the structure check): data-act="kistop" data-act="kistop" */

Object.assign(WT.L.labels, {
  "Stop fissions": "Detener fisiones",
  "Restart fissions": "Reanudar fisiones",
  "half-life · share emitted": "vida media · fracción emitida",
  "waiting stock": "reserva en espera",
  "delayed neutrons out": "neutrones retardados emitidos",
  "{#} s": "{#} s",
  "{#} s after stopping · delayed emission {#} % of the start": "{#} s tras detener · emisión retardada {#} % de la inicial",
  "mean delay Σ aᵢ/λᵢ = {#} s · β = {#} (U{#})": "retardo medio Σ aᵢ/λᵢ = {#} s · β = {#} (U{#})",
  "Keepin six-group data": "datos de seis grupos de Keepin",
  "prompt critical": "crítico instantáneo",
  "drag ρ": "arrastra ρ",
  "prompt root": "raíz instantánea",
  "prompt root ≈ −(β−ρ)/Λ": "raíz instantánea ≈ −(β−ρ)/Λ",
  "ω ({#}/s), stretched": "ω ({#}/s), estirado",
  "ω ({#}/s), axis stretched (asinh)": "ω ({#}/s), eje estirado (asinh)",
  "ρ = 0: power stays flat": "ρ = 0: la potencia se mantiene constante",
  "ρ = {#}: power stays flat": "ρ = {#}: la potencia se mantiene constante",
  "stable period T = {#}/ω₁ = {#} ms": "periodo estable T = {#}/ω₁ = {#} ms",
  "stable period T = {#}/ω₁ = {#} s": "periodo estable T = {#}/ω₁ = {#} s",
  "stable period T = {#}/ω₁ = {#} min": "periodo estable T = {#}/ω₁ = {#} min",
  "stable period T = {#}/ω₁ = {#} h": "periodo estable T = {#}/ω₁ = {#} h",
  "drag the rods out": "arrastra para sacar las barras",
  "prompt jump β/(β−ρ) = {#}": "salto instantáneo β/(β−ρ) = {#}",
  "power": "potencia",
  "prompt critical · period {#} ms (Λ = {#} µs)": "crítico instantáneo · periodo {#} ms (Λ = {#} µs)",
  "prompt critical · period {#} s (Λ = {#} µs)": "crítico instantáneo · periodo {#} s (Λ = {#} µs)",
  "prompt critical · period {#} min (Λ = {#} µs)": "crítico instantáneo · periodo {#} min (Λ = {#} µs)",
  "prompt critical · period {#} h (Λ = {#} µs)": "crítico instantáneo · periodo {#} h (Λ = {#} µs)",
  "ρ = {#} $ · stable period {#} ms": "ρ = {#} $ · periodo estable {#} ms",
  "ρ = {#} $ · stable period {#} s": "ρ = {#} $ · periodo estable {#} s",
  "ρ = {#} $ · stable period {#} min": "ρ = {#} $ · periodo estable {#} min",
  "ρ = {#} $ · stable period {#} h": "ρ = {#} $ · periodo estable {#} h",
  "drag the rods in": "arrastra para introducir las barras",
  "prompt drop to {#}": "caída instantánea a {#}",
  "slope e^(−t/{#} s)": "pendiente e^(−t/{#} s)",
  "slope e^(−t / {#} s): the {#} s group": "pendiente e^(−t / {#} s): el grupo de {#} s",
  "power ×{#} speed": "potencia, velocidad ×{#}",
  "ρ = {#} $ · stable period {#} ms (limit {#} s)": "ρ = {#} $ · periodo estable {#} ms (límite {#} s)",
  "ρ = {#} $ · stable period {#} s (limit {#} s)": "ρ = {#} $ · periodo estable {#} s (límite {#} s)",
  "ρ = {#} $ · stable period {#} min (limit {#} s)": "ρ = {#} $ · periodo estable {#} min (límite {#} s)",
  "ρ = {#} $ · stable period {#} h (limit {#} s)": "ρ = {#} $ · periodo estable {#} h (límite {#} s)",
});
