/* Danish: magnetic confinement (chapter 31) */
WT.L.ch.tokamak = {
  num: "Kapitel 31", title: "Magnetisk indeslutning", short: "Indeslutning",
  lead: "Ingen væg kan røre en gas på 100 millioner grader. Et magnetfelt kan holde den, fordi ladede partikler ikke kan krydse feltlinjer.",
  html: `
<div class="step">
  <h3>Gyration i et magnetfelt</h3>
  <p>På tværs af feltet kan en ladning kun køre i ring; langs feltet glider den. Træk i billedet for at dreje det.</p>
  <div class="ctl"><label for="tk-b">Felt B (tesla)</label><input id="tk-b" type="range" data-bind="B" min="1" max="12" step="0.1" value="5"><output data-show="B" data-fmt="1"></output></div>
  <div class="btns tk-sp"><button class="btn ghost" data-act="spd" aria-pressed="true">Deuteron</button> <button class="btn ghost" data-act="spa" aria-pressed="false">Alfa</button> <button class="btn ghost" data-act="spe" aria-pressed="false">Elektron</button></div>
  <div class="formula">ρ = √(2mE) / (|q| B)</div>
</div>
<div class="step">
  <h3>Toroidale feltlinjer og sikkerhedsfaktoren</h3>
  <p>Et lige felt har åbne ender, så bøj det til en ring, og vrid det: en tokamak. Hver omgang efterlader en prik, hvor linjen krydser snittet.</p>
  <div class="ctl"><label for="tk-q">Sikkerhedsfaktor q</label><input id="tk-q" type="range" data-bind="q" min="1" max="4" step="0.01" value="2.62" data-instant><output data-show="q" data-fmt="2"></output></div>
  <div class="btns"><button class="btn ghost" data-act="q32">q = 3/2</button> <button class="btn ghost" data-act="q2">q = 2</button> <button class="btn ghost" data-act="qg">q = gyldne snit</button></div>
</div>
<div class="step">
  <h3>Magnetiske øer og feltlinjekaos</h3>
  <p>Krusninger i feltet river fladerne op i øer, hvor q er en simpel brøk, og derefter i kaos. Klik for at starte en feltlinje.</p>
  <div class="ctl"><label for="tk-k">Forstyrrelse K</label><input id="tk-k" type="range" data-bind="K" min="0" max="6" step="0.05" value="1.5" data-instant><output data-show="K" data-fmt="2"></output></div>
  <div class="formula">ψ′ = ψ − (K/2π) ψ′/(1+ψ′) sin θ<br>θ′ = θ + 2π/q(ψ′) − (K/2π) cos θ/(1+ψ′)²</div>
</div>`,
};
