/* French: magnetic confinement (chapter 31) */
WT.L.ch.tokamak = {
  num: "Chapitre 31", title: "Le confinement magnétique", short: "Confinement",
  lead: "Aucune paroi ne peut toucher un gaz à 100 millions de degrés. Un champ magnétique peut le retenir, car les particules chargées ne peuvent pas traverser les lignes de champ.",
  html: `
<div class="step">
  <h3>La giration dans un champ magnétique</h3>
  <p>En travers du champ, une charge ne peut que tourner en rond ; le long du champ, elle glisse. Faites glisser l'image pour la faire pivoter.</p>
  <div class="ctl"><label for="tk-b">Champ B (tesla)</label><input id="tk-b" type="range" data-bind="B" min="1" max="12" step="0.1" value="5"><output data-show="B" data-fmt="1"></output></div>
  <div class="btns tk-sp"><button class="btn ghost" data-act="spd" aria-pressed="true">Deutéron</button> <button class="btn ghost" data-act="spa" aria-pressed="false">Alpha</button> <button class="btn ghost" data-act="spe" aria-pressed="false">Électron</button></div>
  <div class="formula">ρ = √(2mE) / (|q| B)</div>
</div>
<div class="step">
  <h3>Lignes de champ toroïdales et facteur de sécurité</h3>
  <p>Un champ droit a des extrémités ouvertes : on le courbe donc en anneau et on le tord. C'est un tokamak. Chaque tour laisse un point là où la ligne traverse la coupe.</p>
  <div class="ctl"><label for="tk-q">Facteur de sécurité q</label><input id="tk-q" type="range" data-bind="q" min="1" max="4" step="0.01" value="2.62" data-instant><output data-show="q" data-fmt="2"></output></div>
  <div class="btns"><button class="btn ghost" data-act="q32">q = 3/2</button> <button class="btn ghost" data-act="q2">q = 2</button> <button class="btn ghost" data-act="qg">q = nombre d'or</button></div>
</div>
<div class="step">
  <h3>Îlots magnétiques et chaos des lignes de champ</h3>
  <p>Des ondulations du champ déchirent les surfaces en îlots là où q est une fraction simple, puis en chaos. Cliquez pour lancer une ligne de champ.</p>
  <div class="ctl"><label for="tk-k">Perturbation K</label><input id="tk-k" type="range" data-bind="K" min="0" max="6" step="0.05" value="1.5" data-instant><output data-show="K" data-fmt="2"></output></div>
  <div class="formula">ψ′ = ψ − (K/2π) ψ′/(1+ψ′) sin θ<br>θ′ = θ + 2π/q(ψ′) − (K/2π) cos θ/(1+ψ′)²</div>
</div>`,
};
