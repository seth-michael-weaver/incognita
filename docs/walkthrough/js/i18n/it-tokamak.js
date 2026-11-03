/* Italian: tokamak (Capitolo 31, confinamento magnetico) */
WT.L.ch.tokamak = {
  num: "Capitolo 31", title: "Confinamento magnetico", short: "Confinamento",
  lead: "Nessuna parete può toccare un gas a 100 milioni di gradi. Un campo magnetico può trattenerlo, perché le particelle cariche non possono attraversare le linee di campo.",
  html: `
<div class="step">
  <h3>Girazione in un campo magnetico</h3>
  <p>Di traverso al campo una carica può solo girare in cerchio; lungo il campo, scivola. Trascina l'immagine per ruotarla.</p>
  <div class="ctl"><label for="tk-b">Campo B (tesla)</label><input id="tk-b" type="range" data-bind="B" min="1" max="12" step="0.1" value="5"><output data-show="B" data-fmt="1"></output></div>
  <div class="btns tk-sp"><button class="btn ghost" data-act="spd" aria-pressed="true">Deutone</button> <button class="btn ghost" data-act="spa" aria-pressed="false">Alfa</button> <button class="btn ghost" data-act="spe" aria-pressed="false">Elettrone</button></div>
  <div class="formula">ρ = √(2mE) / (|q| B)</div>
</div>
<div class="step">
  <h3>Linee di campo toroidali e fattore di sicurezza</h3>
  <p>Un campo rettilineo ha le estremità aperte, quindi piegalo ad anello e torcilo: ecco un tokamak. A ogni giro la linea lascia un punto dove attraversa la sezione.</p>
  <div class="ctl"><label for="tk-q">Fattore di sicurezza q</label><input id="tk-q" type="range" data-bind="q" min="1" max="4" step="0.01" value="2.62" data-instant><output data-show="q" data-fmt="2"></output></div>
  <div class="btns"><button class="btn ghost" data-act="q32">q = 3/2</button> <button class="btn ghost" data-act="q2">q = 2</button> <button class="btn ghost" data-act="qg">q = aureo</button></div>
</div>
<div class="step">
  <h3>Isole magnetiche e caos delle linee di campo</h3>
  <p>Le increspature del campo strappano le superfici in isole dove q è una frazione semplice, poi nel caos. Clicca per far partire una linea di campo.</p>
  <div class="ctl"><label for="tk-k">Perturbazione K</label><input id="tk-k" type="range" data-bind="K" min="0" max="6" step="0.05" value="1.5" data-instant><output data-show="K" data-fmt="2"></output></div>
  <div class="formula">ψ′ = ψ − (K/2π) ψ′/(1+ψ′) sin θ<br>θ′ = θ + 2π/q(ψ′) − (K/2π) cos θ/(1+ψ′)²</div>
</div>`,
};
