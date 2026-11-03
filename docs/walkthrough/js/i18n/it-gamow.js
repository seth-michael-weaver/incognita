/* Italian: gamow (Capitolo 30, picco di Gamow e ignizione) */
WT.L.ch.gamow = {
  num: "Capitolo 30", title: "Il picco di Gamow e l'ignizione", short: "Picco di Gamow",
  lead: "Un plasma caldo brucia attraverso una stretta finestra di energie: abbastanza veloci per l'effetto tunnel, abbastanza comuni da contare.",
  html: `
<div class="step">
  <h3>Il picco di Gamow</h3>
  <p>Pochi nuclei sono veloci; quelli veloci passano più facilmente per effetto tunnel. Il prodotto si illumina: è il picco di Gamow. Trascina la linea della temperatura.</p>
  <div class="ctl"><label for="gw-t">Temperatura kT (keV)</label><input id="gw-t" type="range" data-bind="lT" min="0" max="2" step="0.01" value="1"><output data-show="T" data-fmt="1"></output></div>
  <div class="formula">E₀ = (E<sub>G</sub> (kT)² / 4)<sup>1/3</sup> · larghezza 4√(E₀kT/3)</div>
</div>
<div class="step">
  <h3>Reattività dei combustibili</h3>
  <p>Somma tutta la finestra e ottieni la reattività ⟨σv⟩. Il D–T vince nettamente a qualsiasi temperatura che una macchina possa raggiungere.</p>
  <div class="ctl"><label for="gw-t2">Temperatura kT (keV)</label><input id="gw-t2" type="range" data-bind="lT" min="0" max="2" step="0.01" value="1"><output data-show="T" data-fmt="1"></output></div>
  <div class="formula">⟨σv⟩ = ∫ σ(E) v f(E) dE</div>
</div>
<div class="step">
  <h3>Il criterio di Lawson e l'ignizione</h3>
  <p>Trascina il plasma su una temperatura e un confinamento, poi lascialo. Sopra la curva più alta si mantiene caldo da solo.</p>
  <div class="btns"><button class="btn" data-act="lowgo">Prova una macchina debole</button> <button class="btn ghost" data-act="higo">Prova una macchina potente</button></div>
  <div class="formula">ignizione: n τ<sub>E</sub> T ≳ 3·10²¹ keV s m⁻³</div>
</div>`,
};
