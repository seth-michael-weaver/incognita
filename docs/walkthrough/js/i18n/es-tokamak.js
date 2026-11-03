/* Spanish: tokamak (chapter 31, magnetic confinement) */
WT.L.ch.tokamak = {
  num: "Capítulo 31", title: "Confinamiento magnético", short: "Confinamiento",
  lead: "Ninguna pared puede tocar un gas a 100 millones de grados. Un campo magnético sí puede sujetarlo, porque las partículas cargadas no pueden cruzar las líneas de campo.",
  html: `
<div class="step">
  <h3>Giro en un campo magnético</h3>
  <p>A través del campo, una carga solo puede girar en círculo; a lo largo de él, se desliza. Arrastra la imagen para girarla.</p>
  <div class="ctl"><label for="tk-b">Campo B (tesla)</label><input id="tk-b" type="range" data-bind="B" min="1" max="12" step="0.1" value="5"><output data-show="B" data-fmt="1"></output></div>
  <div class="btns tk-sp"><button class="btn ghost" data-act="spd" aria-pressed="true">Deuterón</button> <button class="btn ghost" data-act="spa" aria-pressed="false">Alfa</button> <button class="btn ghost" data-act="spe" aria-pressed="false">Electrón</button></div>
  <div class="formula">ρ = √(2mE) / (|q| B)</div>
</div>
<div class="step">
  <h3>Líneas de campo toroidales y el factor de seguridad</h3>
  <p>Un campo recto tiene los extremos abiertos, así que se curva en un anillo y se retuerce: un tokamak. Cada vuelta deja un punto donde la línea cruza el corte.</p>
  <div class="ctl"><label for="tk-q">Factor de seguridad q</label><input id="tk-q" type="range" data-bind="q" min="1" max="4" step="0.01" value="2.62" data-instant><output data-show="q" data-fmt="2"></output></div>
  <div class="btns"><button class="btn ghost" data-act="q32">q = 3/2</button> <button class="btn ghost" data-act="q2">q = 2</button> <button class="btn ghost" data-act="qg">q = áureo</button></div>
</div>
<div class="step">
  <h3>Islas magnéticas y caos de las líneas de campo</h3>
  <p>Las ondulaciones del campo rasgan las superficies en islas donde q es una fracción sencilla, y después en caos. Haz clic para iniciar una línea de campo.</p>
  <div class="ctl"><label for="tk-k">Perturbación K</label><input id="tk-k" type="range" data-bind="K" min="0" max="6" step="0.05" value="1.5" data-instant><output data-show="K" data-fmt="2"></output></div>
  <div class="formula">ψ′ = ψ − (K/2π) ψ′/(1+ψ′) sin θ<br>θ′ = θ + 2π/q(ψ′) − (K/2π) cos θ/(1+ψ′)²</div>
</div>`,
};
