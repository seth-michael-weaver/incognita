/* Spanish: kcalc (Computing criticality) */
WT.L.ch.kcalc = {
  num: "Lección 1", title: "Cálculo de la criticidad", short: "Cálculo de k",
  html: `
<div class="step">
  <h3>Los benchmarks</h3>
  <p>Cuatro conjuntos críticos rápidos metálicos del ICSBEP, a escala. Godiva y Jezebel son esferas desnudas; Flattop-25 y Flattop-Pu tienen un reflector de uranio natural.</p>
</div>
<div class="step">
  <h3><i>k</i><sub>eff</sub> calculado</h3>
  <p>OpenMC, energía continua, geometría 3-D. Los cuatro están dentro de ±1σ del benchmark. <i>k</i><sub>eff</sub> no se usa en el ajuste.</p>
</div>
<div class="step">
  <h3>Perfiles de sensibilidad</h3>
  <p>Sensibilidad adjunta de <i>k</i><sub>eff</sub> a cada reacción, por unidad de letargia.</p>
  <div class="btns"><button class="btn ghost" data-act="se0" aria-pressed="true">Godiva</button><button class="btn ghost" data-act="se1" aria-pressed="false">Jezebel</button><button class="btn ghost" data-act="se2" aria-pressed="false">Flattop-Pu</button></div>
</div>
<div class="step">
  <h3>Verificación por perturbación directa</h3>
  <p>Cambios de <i>k</i><sub>eff</sub> predichos frente a recalculados, 63 conjuntos de datos perturbados.</p>
</div>
<div class="step">
  <h3>Núcleo del reactor C5G7</h3>
  <p>Cuarto de núcleo OECD/NEA C5G7, 1056 varillas de UO<sub>2</sub> y MOX: en 2-D y en la extensión 3-D con barras de control insertadas. <i>k</i><sub>eff</sub> a menos de 19&nbsp;pcm de la referencia en 2-D y a menos de 9&nbsp;pcm en cada configuración 3-D.</p>
  <div class="btns"><button class="btn ghost" data-act="c50" aria-pressed="true">2-D</button><button class="btn ghost" data-act="c51" aria-pressed="false">3-D</button><button class="btn ghost" data-act="c52" aria-pressed="false">Barras A</button><button class="btn ghost" data-act="c53" aria-pressed="false">Barras B</button></div>
</div>`,
};

Object.assign(WT.L.labels, {
  "{#} pcm  (±{#} benchmark)": "{#} pcm  (±{#} benchmark)",
  "+{#} pcm  (±{#} benchmark)": "+{#} pcm  (±{#} benchmark)",
  "Calculated − experimental k, with the benchmark ±{#}σ band": "k calculado − experimental, con la banda ±{#}σ del benchmark",
  "Drag to rotate": "Arrastra para girar",
  "Godiva, integral sensitivity: ν {#}, fission {#} (% k per % change)": "Godiva, sensibilidad integral: ν {#}, fisión {#} (% de k por % de cambio)",
  "Jezebel, integral sensitivity: ν {#}, fission {#} (% k per % change)": "Jezebel, sensibilidad integral: ν {#}, fisión {#} (% de k por % de cambio)",
  "Flattop-Pu, integral sensitivity: ν {#}, fission {#} (% k per % change)": "Flattop-Pu, sensibilidad integral: ν {#}, fisión {#} (% de k por % de cambio)",
  "Godiva: ν {#}, fission {#}": "Godiva: ν {#}, fisión {#}",
  "Jezebel: ν {#}, fission {#}": "Jezebel: ν {#}, fisión {#}",
  "Flattop-Pu: ν {#}, fission {#}": "Flattop-Pu: ν {#}, fisión {#}",
  "UO₂: {#} × mean": "UO₂: {#} × media",
  "MOX {#} %: {#} × mean": "MOX {#} %: {#} × media",
  "OpenMC re-solve, Δk (pcm)": "Recálculo OpenMC, Δk (pcm)",
  "Predicted from sensitivities, Δk (pcm)": "Predicho con sensibilidades, Δk (pcm)",
  "predicted Δk, pcm": "Δk predicho, pcm",
  "U{#} capture": "captura de U{#}",
  "Pu{#} capture": "captura de Pu{#}",
  "U{#} elastic": "elástica de U{#}",
  "Pu{#} elastic": "elástica de Pu{#}",
  "U{#} fission": "fisión de U{#}",
  "Pu{#} fission": "fisión de Pu{#}",
  "U{#} inelastic": "inelástica de U{#}",
  "Pu{#} inelastic": "inelástica de Pu{#}",
  "U{#} neutrons per fission (ν)": "neutrones por fisión de U{#} (ν)",
  "Pu{#} neutrons per fission (ν)": "neutrones por fisión de Pu{#} (ν)",
  "Relative pin power (hover a pin)": "Potencia relativa por varilla (pasa sobre una varilla)",
  "Relative pin power (tap a pin)": "Potencia relativa por varilla (toca una varilla)",
  "To scale.": "A escala.",
  "To scale. Drag to rotate.": "A escala. Arrastra para girar.",
  "core {#} cm, reflector {#} cm": "núcleo {#} cm, reflector {#} cm",
  "radius {#} cm": "radio {#} cm",
  "{#} cm in {#} cm": "{#} cm en {#} cm",
  "k = {#}; reference {#} ({#} pcm)": "k = {#}; referencia {#} ({#} pcm)",
  "k = {#}; reference {#} (+{#} pcm)": "k = {#}; referencia {#} (+{#} pcm)",
  "k {#}, reference {#}": "k {#}, referencia {#}",
  "plutonium in natural uranium": "plutonio en uranio natural",
  "plutonium metal": "plutonio metálico",
  "uranium{#} in natural uranium": "uranio{#} en uranio natural",
  "uranium{#} metal": "uranio{#} metálico",
  "water": "agua",
  "×{#} of mean": "×{#} de la media",
  "U{#} ν": "U{#} ν",
  "Pu{#} ν": "Pu{#} ν",
  "Godiva   k = {#}": "Godiva   k = {#}",
  "Godiva {#}": "Godiva {#}",
  "Godiva: rms {#} pcm": "Godiva: rms {#} pcm",
  "Jezebel   k = {#}": "Jezebel   k = {#}",
  "Jezebel {#}": "Jezebel {#}",
  "Jezebel: rms {#} pcm": "Jezebel: rms {#} pcm",
  "Flattop-Pu   k = {#}": "Flattop-Pu   k = {#}",
  "Flattop-Pu {#}": "Flattop-Pu {#}",
  "Flattop-Pu: rms {#} pcm": "Flattop-Pu: rms {#} pcm",
  "Flattop{#}   k = {#}": "Flattop{#}   k = {#}",
  "Flattop{#} {#}": "Flattop{#} {#}",
  "{#} pcm (±{#})": "{#} pcm (±{#})",
  "+{#} pcm (±{#})": "+{#} pcm (±{#})",
  "{#} cm": "{#} cm",
  "{#} keV": "{#} keV",
  "{#} MeV": "{#} MeV",
  "OpenMC Δk": "OpenMC Δk"
});
