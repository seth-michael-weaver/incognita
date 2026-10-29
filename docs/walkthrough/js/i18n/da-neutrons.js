/* Danish: neutrons (Kapitel 4, hvorfor neutroner) */
WT.L.ch.neutrons = {
  num: "Kapitel 4", title: "Hvorfor reaktorer kører på neutroner", short: "Hvorfor neutroner",
  html: `
<div class="step">
  <p>En proton er positiv, og det er kernens 82 protoner også. Ens ladninger frastøder hinanden, så protonen bliver skubbet væk, og skubbet vokser hurtigt, når den kommer tættere på (pilen). En langsom proton standser i god afstand og vender om uden at røre kernen. Først over omkring 13 MeV kommer den over skubbet; lige under slipper den nogle gange alligevel igennem (<b>tunnelering</b>). Den lille graf viser det samme skub som en energibakke.</p>
  <div class="ctl"><label for="wn-e1">Protonenergi (MeV)</label><input id="wn-e1" type="range" data-bind="Ep" data-instant min="0.5" max="20" step="0.1" value="6"><output data-show="Ep" data-fmt="1"></output></div>
</div>
<div class="step">
  <p>En neutron har ingen ladning: den kommer ind ved enhver hastighed. Intet skubber den væk, så der er ingen bakke at komme over; den skal bare nå frem til kernen, og så trækker den stærke kraft den ind.</p>
  <div class="ctl"><label for="wn-e2">Neutronenergi (langsom → hurtig)</label><input id="wn-e2" type="range" data-bind="lgEn" data-instant min="-1.6" max="7.3" step="0.01" value="-1.6"><output id="wn-en-out"></output></div>
  <p>Skyderen løber fra 0,025 eV, hastigheden af en neutron ved stuetemperatur, op til 20 MeV, næsten en milliard gange mere. Hele vejen ned kommer neutronen stadig ind.</p>
</div>
<div class="step">
  <p>Så selv langsomme neutroner kan spalte uran i en reaktor. En uran-235-kerne, der sluger en, bliver til uran-236 med lidt ekstra energi, nok til at svinge, strække sig til en hals og briste i to. De to stykker flyver fra hinanden med omkring 200 MeV, og de to eller tre nye neutroner, de kaster af sig, kan spalte de næste kerner: en kædereaktion.</p>
</div>
`,
};
