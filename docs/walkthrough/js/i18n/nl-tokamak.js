/* Dutch (Nederlands): tokamak (Hoofdstuk 31, magnetische opsluiting) */
WT.L.ch.tokamak = {
  num: "Hoofdstuk 31", title: "Magnetische opsluiting", short: "Opsluiting",
  lead: "Geen wand kan een gas van 100 miljoen graden aanraken. Een magneetveld kan het vasthouden, omdat geladen deeltjes veldlijnen niet kunnen oversteken.",
  html: `
<div class="step">
  <h3>Gyratie in een magneetveld</h3>
  <p>Dwars op het veld kan een lading alleen rondcirkelen; erlangs glijdt ze. Sleep aan het plaatje om het te draaien.</p>
  <div class="ctl"><label for="tk-b">Veld B (tesla)</label><input id="tk-b" type="range" data-bind="B" min="1" max="12" step="0.1" value="5"><output data-show="B" data-fmt="1"></output></div>
  <div class="btns tk-sp"><button class="btn ghost" data-act="spd" aria-pressed="true">Deuteron</button> <button class="btn ghost" data-act="spa" aria-pressed="false">Alfa</button> <button class="btn ghost" data-act="spe" aria-pressed="false">Elektron</button></div>
  <div class="formula">ρ = √(2mE) / (|q| B)</div>
</div>
<div class="step">
  <h3>Toroïdale veldlijnen en de veiligheidsfactor</h3>
  <p>Een recht veld heeft open uiteinden, dus buig het tot een ring en draai het in elkaar: een tokamak. Elke ronde laat een punt achter waar de lijn de doorsnede kruist.</p>
  <div class="ctl"><label for="tk-q">Veiligheidsfactor q</label><input id="tk-q" type="range" data-bind="q" min="1" max="4" step="0.01" value="2.62" data-instant><output data-show="q" data-fmt="2"></output></div>
  <div class="btns"><button class="btn ghost" data-act="q32">q = 3/2</button> <button class="btn ghost" data-act="q2">q = 2</button> <button class="btn ghost" data-act="qg">q = gulden snede</button></div>
</div>
<div class="step">
  <h3>Magnetische eilanden en chaos in de veldlijnen</h3>
  <p>Rimpelingen in het veld scheuren de oppervlakken open tot eilanden waar q een eenvoudige breuk is, en daarna tot chaos. Klik om een veldlijn te starten.</p>
  <div class="ctl"><label for="tk-k">Verstoring K</label><input id="tk-k" type="range" data-bind="K" min="0" max="6" step="0.05" value="1.5" data-instant><output data-show="K" data-fmt="2"></output></div>
  <div class="formula">ψ′ = ψ − (K/2π) ψ′/(1+ψ′) sin θ<br>θ′ = θ + 2π/q(ψ′) − (K/2π) cos θ/(1+ψ′)²</div>
</div>`,
};
