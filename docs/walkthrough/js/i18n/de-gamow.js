/* German (Deutsch): gamow (Kapitel 30, Der Gamow-Peak und die Zündung) */
WT.L.ch.gamow = {
  num: "Kapitel 30", title: "Der Gamow-Peak und die Zündung", short: "Gamow-Peak",
  lead: "Ein heißes Plasma brennt durch ein schmales Energiefenster: schnell genug zum Tunneln, häufig genug, um ins Gewicht zu fallen.",
  html: `
<div class="step">
  <h3>Der Gamow-Peak</h3>
  <p>Wenige Kerne sind schnell; schnelle tunneln leichter. Das Produkt leuchtet: der Gamow-Peak. Zieh die Temperaturlinie.</p>
  <div class="ctl"><label for="gw-t">Temperatur kT (keV)</label><input id="gw-t" type="range" data-bind="lT" min="0" max="2" step="0.01" value="1"><output data-show="T" data-fmt="1"></output></div>
  <div class="formula">E₀ = (E<sub>G</sub> (kT)² / 4)<sup>1/3</sup> · Breite 4√(E₀kT/3)</div>
</div>
<div class="step">
  <h3>Reaktivitäten der Brennstoffe</h3>
  <p>Summiere über das Fenster, und du erhältst die Reaktivität ⟨σv⟩. D–T gewinnt mit Abstand, bei jeder Temperatur, die eine Maschine erreichen kann.</p>
  <div class="ctl"><label for="gw-t2">Temperatur kT (keV)</label><input id="gw-t2" type="range" data-bind="lT" min="0" max="2" step="0.01" value="1"><output data-show="T" data-fmt="1"></output></div>
  <div class="formula">⟨σv⟩ = ∫ σ(E) v f(E) dE</div>
</div>
<div class="step">
  <h3>Das Lawson-Kriterium und die Zündung</h3>
  <p>Zieh das Plasma auf eine Temperatur und einen Einschluss, dann lass los. Oberhalb der oberen Kurve hält es sich selbst heiß.</p>
  <div class="btns"><button class="btn" data-act="lowgo">Schwache Maschine testen</button> <button class="btn ghost" data-act="higo">Starke Maschine testen</button></div>
  <div class="formula">Zündung: n τ<sub>E</sub> T ≳ 3·10²¹ keV s m⁻³</div>
</div>`,
};
