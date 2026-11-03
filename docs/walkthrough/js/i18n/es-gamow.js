/* Spanish: gamow (chapter 30, the Gamow peak, reactivities and ignition) */
WT.L.ch.gamow = {
  num: "Capítulo 30", title: "El pico de Gamow y la ignición", short: "Pico de Gamow",
  lead: "Un plasma caliente arde a través de una estrecha ventana de energías: núcleos lo bastante rápidos para el efecto túnel y lo bastante numerosos para importar.",
  html: `
<div class="step">
  <h3>El pico de Gamow</h3>
  <p>Pocos núcleos son rápidos; los rápidos atraviesan la barrera por efecto túnel con más facilidad. El producto brilla: el pico de Gamow. Arrastra la línea de temperatura.</p>
  <div class="ctl"><label for="gw-t">Temperatura kT (keV)</label><input id="gw-t" type="range" data-bind="lT" min="0" max="2" step="0.01" value="1"><output data-show="T" data-fmt="1"></output></div>
  <div class="formula">E₀ = (E<sub>G</sub> (kT)² / 4)<sup>1/3</sup> · anchura 4√(E₀kT/3)</div>
</div>
<div class="step">
  <h3>Reactividades de los combustibles</h3>
  <p>Suma toda la ventana y obtienes la reactividad ⟨σv⟩. El D–T gana con mucho a cualquier temperatura que pueda alcanzar una máquina.</p>
  <div class="ctl"><label for="gw-t2">Temperatura kT (keV)</label><input id="gw-t2" type="range" data-bind="lT" min="0" max="2" step="0.01" value="1"><output data-show="T" data-fmt="1"></output></div>
  <div class="formula">⟨σv⟩ = ∫ σ(E) v f(E) dE</div>
</div>
<div class="step">
  <h3>El criterio de Lawson y la ignición</h3>
  <p>Arrastra el plasma hasta una temperatura y un confinamiento, y suéltalo. Por encima de la curva superior se mantiene caliente por sí solo.</p>
  <div class="btns"><button class="btn" data-act="lowgo">Prueba una máquina débil</button> <button class="btn ghost" data-act="higo">Prueba una potente</button></div>
  <div class="formula">ignición: n τ<sub>E</sub> T ≳ 3·10²¹ keV s m⁻³</div>
</div>`,
};
