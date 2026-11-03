/* Dutch (Nederlands): gamow (Hoofdstuk 30, de gamowpiek en ontsteking) */
WT.L.ch.gamow = {
  num: "Hoofdstuk 30", title: "De gamowpiek en ontsteking", short: "Gamowpiek",
  lead: "Een heet plasma brandt door een smal venster van energieën: snel genoeg om te tunnelen, talrijk genoeg om mee te tellen.",
  html: `
<div class="step">
  <h3>De gamowpiek</h3>
  <p>Weinig kernen zijn snel; snelle tunnelen makkelijker. Het product gloeit op: de gamowpiek. Sleep de temperatuurlijn.</p>
  <div class="ctl"><label for="gw-t">Temperatuur kT (keV)</label><input id="gw-t" type="range" data-bind="lT" min="0" max="2" step="0.01" value="1"><output data-show="T" data-fmt="1"></output></div>
  <div class="formula">E₀ = (E<sub>G</sub> (kT)² / 4)<sup>1/3</sup> · breedte 4√(E₀kT/3)</div>
</div>
<div class="step">
  <h3>Reactiviteit van brandstoffen</h3>
  <p>Tel het venster op en je krijgt de reactiviteit ⟨σv⟩. D–T wint ruim bij elke temperatuur die een machine kan halen.</p>
  <div class="ctl"><label for="gw-t2">Temperatuur kT (keV)</label><input id="gw-t2" type="range" data-bind="lT" min="0" max="2" step="0.01" value="1"><output data-show="T" data-fmt="1"></output></div>
  <div class="formula">⟨σv⟩ = ∫ σ(E) v f(E) dE</div>
</div>
<div class="step">
  <h3>Het lawsoncriterium en ontsteking</h3>
  <p>Sleep het plasma naar een temperatuur en opsluiting, en laat dan los. Boven de bovenste curve houdt het zichzelf heet.</p>
  <div class="btns"><button class="btn" data-act="lowgo">Probeer een zwakke machine</button> <button class="btn ghost" data-act="higo">Probeer een sterke</button></div>
  <div class="formula">ontsteking: n τ<sub>E</sub> T ≳ 3·10²¹ keV s m⁻³</div>
</div>`,
};
