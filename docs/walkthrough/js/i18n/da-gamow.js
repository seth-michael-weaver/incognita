/* Danish: the Gamow peak and ignition (chapter 30) */
WT.L.ch.gamow = {
  num: "Kapitel 30", title: "Gamow-toppen og antændelse", short: "Gamow-top",
  lead: "Et varmt plasma brænder gennem et smalt vindue af energier: hurtige nok til at tunnelere, almindelige nok til at betyde noget.",
  html: `
<div class="step">
  <h3>Gamow-toppen</h3>
  <p>Få kerner er hurtige; de hurtige tunnelerer lettere. Produktet lyser op: Gamow-toppen. Træk i temperaturlinjen.</p>
  <div class="ctl"><label for="gw-t">Temperatur kT (keV)</label><input id="gw-t" type="range" data-bind="lT" min="0" max="2" step="0.01" value="1"><output data-show="T" data-fmt="1"></output></div>
  <div class="formula">E₀ = (E<sub>G</sub> (kT)² / 4)<sup>1/3</sup> · bredde 4√(E₀kT/3)</div>
</div>
<div class="step">
  <h3>Brændstoffernes reaktivitet</h3>
  <p>Læg hele vinduet sammen, og du får reaktiviteten ⟨σv⟩. D–T vinder klart ved enhver temperatur, en maskine kan nå.</p>
  <div class="ctl"><label for="gw-t2">Temperatur kT (keV)</label><input id="gw-t2" type="range" data-bind="lT" min="0" max="2" step="0.01" value="1"><output data-show="T" data-fmt="1"></output></div>
  <div class="formula">⟨σv⟩ = ∫ σ(E) v f(E) dE</div>
</div>
<div class="step">
  <h3>Lawson-kriteriet og antændelse</h3>
  <p>Træk plasmaet til en temperatur og en indeslutning, og giv slip. Over den øverste kurve holder det sig selv varmt.</p>
  <div class="btns"><button class="btn" data-act="lowgo">Prøv en svag maskine</button> <button class="btn ghost" data-act="higo">Prøv en stærk</button></div>
  <div class="formula">antændelse: n τ<sub>E</sub> T ≳ 3·10²¹ keV s m⁻³</div>
</div>`,
};
