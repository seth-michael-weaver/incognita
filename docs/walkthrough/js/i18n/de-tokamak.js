/* German (Deutsch): tokamak (Kapitel 31, Magnetischer Einschluss) */
WT.L.ch.tokamak = {
  num: "Kapitel 31", title: "Magnetischer Einschluss", short: "Einschluss",
  lead: "Keine Wand verträgt die Berührung mit einem 100 Millionen Grad heißen Gas. Ein Magnetfeld kann es halten, weil geladene Teilchen Feldlinien nicht überqueren können.",
  html: `
<div class="step">
  <h3>Gyration im Magnetfeld</h3>
  <p>Quer zum Feld kann eine Ladung nur kreisen; entlang des Feldes gleitet sie. Zieh am Bild, um es zu drehen.</p>
  <div class="ctl"><label for="tk-b">Feld B (Tesla)</label><input id="tk-b" type="range" data-bind="B" min="1" max="12" step="0.1" value="5"><output data-show="B" data-fmt="1"></output></div>
  <div class="btns tk-sp"><button class="btn ghost" data-act="spd" aria-pressed="true">Deuteron</button> <button class="btn ghost" data-act="spa" aria-pressed="false">Alpha</button> <button class="btn ghost" data-act="spe" aria-pressed="false">Elektron</button></div>
  <div class="formula">ρ = √(2mE) / (|q| B)</div>
</div>
<div class="step">
  <h3>Toroidale Feldlinien und der Sicherheitsfaktor</h3>
  <p>Ein gerades Feld hat offene Enden, also biege es zu einem Ring und verdrille es: ein Tokamak. Jeder Umlauf hinterlässt einen Punkt, wo die Linie den Schnitt kreuzt.</p>
  <div class="ctl"><label for="tk-q">Sicherheitsfaktor q</label><input id="tk-q" type="range" data-bind="q" min="1" max="4" step="0.01" value="2.62" data-instant><output data-show="q" data-fmt="2"></output></div>
  <div class="btns"><button class="btn ghost" data-act="q32">q = 3/2</button> <button class="btn ghost" data-act="q2">q = 2</button> <button class="btn ghost" data-act="qg">q = Goldener Schnitt</button></div>
</div>
<div class="step">
  <h3>Magnetische Inseln und Feldlinienchaos</h3>
  <p>Kleine Wellen im Feld reißen die Flächen dort, wo q ein einfacher Bruch ist, zu Inseln auf und dann ins Chaos. Klicke, um eine Feldlinie zu starten.</p>
  <div class="ctl"><label for="tk-k">Störung K</label><input id="tk-k" type="range" data-bind="K" min="0" max="6" step="0.05" value="1.5" data-instant><output data-show="K" data-fmt="2"></output></div>
  <div class="formula">ψ′ = ψ − (K/2π) ψ′/(1+ψ′) sin θ<br>θ′ = θ + 2π/q(ψ′) − (K/2π) cos θ/(1+ψ′)²</div>
</div>`,
};
