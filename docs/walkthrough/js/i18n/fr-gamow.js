/* French: the Gamow peak and ignition (chapter 30) */
WT.L.ch.gamow = {
  num: "Chapitre 30", title: "Le pic de Gamow et l'ignition", short: "Pic de Gamow",
  lead: "Un plasma chaud brûle à travers une étroite fenêtre d'énergies : assez rapides pour passer par effet tunnel, assez nombreuses pour compter.",
  html: `
<div class="step">
  <h3>Le pic de Gamow</h3>
  <p>Peu de noyaux sont rapides ; les rapides passent plus facilement par effet tunnel. Le produit s'illumine : c'est le pic de Gamow. Faites glisser la ligne de température.</p>
  <div class="ctl"><label for="gw-t">Température kT (keV)</label><input id="gw-t" type="range" data-bind="lT" min="0" max="2" step="0.01" value="1"><output data-show="T" data-fmt="1"></output></div>
  <div class="formula">E₀ = (E<sub>G</sub> (kT)² / 4)<sup>1/3</sup> · largeur 4√(E₀kT/3)</div>
</div>
<div class="step">
  <h3>Réactivités des combustibles</h3>
  <p>Additionnez toute la fenêtre et vous obtenez la réactivité ⟨σv⟩. D–T l'emporte de loin à toute température qu'une machine peut atteindre.</p>
  <div class="ctl"><label for="gw-t2">Température kT (keV)</label><input id="gw-t2" type="range" data-bind="lT" min="0" max="2" step="0.01" value="1"><output data-show="T" data-fmt="1"></output></div>
  <div class="formula">⟨σv⟩ = ∫ σ(E) v f(E) dE</div>
</div>
<div class="step">
  <h3>Le critère de Lawson et l'ignition</h3>
  <p>Faites glisser le plasma vers une température et un confinement, puis lâchez-le. Au-dessus de la courbe du haut, il reste chaud tout seul.</p>
  <div class="btns"><button class="btn" data-act="lowgo">Essayer une machine faible</button> <button class="btn ghost" data-act="higo">Essayer une machine puissante</button></div>
  <div class="formula">ignition : n τ<sub>E</sub> T ≳ 3·10²¹ keV s m⁻³</div>
</div>`,
};
