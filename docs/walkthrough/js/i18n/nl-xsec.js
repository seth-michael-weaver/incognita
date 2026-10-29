/* Dutch (Nederlands): xsec (Hoofdstuk 2, wat is een werkzame doorsnede?) */
WT.L.ch.xsec = {
  num: "Hoofdstuk 2", title: "Wat is een werkzame doorsnede?", short: "Werkzame doorsnede",
  html: `
<div class="step">
  <p>Elke schijf is het trefoppervlak van een kern: zijn <b>werkzame doorsnede</b>, geschreven als σ (sigma). De afbeelding kijkt recht neer op een dun vel kernen terwijl neutronen op willekeurige plekken op het vel regenen. Een neutron dat binnen een schijf landt, reageert met die kern (een oranje flits); een neutron dat tussen de schijven landt, gaat er recht doorheen (het vervaagt gewoon).</p>
  <p>Het aandeel dat reageert is dus gewoon het deel van het vel dat de schijven bedekken. Het kleine zwarte vierkant is de eenheid van oppervlak, één <b>barn</b>, 10⁻²⁴ cm²: het echte oppervlak van een kern is ongeveer één barn.</p>
  <div class="ctl"><label for="xs-e1">Neutronenergie (eV)</label><input id="xs-e1" type="range" data-bind="lgE" data-instant min="-2.3" max="2" step="0.01" value="2"><output data-show="Eshow" data-fmt="2"></output></div>
</div>
<div class="step">
  <p>Langzamere neutronen zien grotere doelen. De schijf is niet de echte grootte van de kern: het is hoe groot de kern zich gedraagt voor een neutron bij deze energie, en een langzaam neutron blijft langer bij de kern, dus de kans dat het wordt gevangen is groter. Bij vangst laat dit σ groeien als 1/snelheid.</p>
  <p>De curve onder het vel is σ over alle energieën (beide schalen zijn logaritmisch); de oranje stip markeert de energie die je koos. Sleep naar de langzaamste neutronen en kijk hoe de schijven groeien en het gereageerde aandeel stijgt.</p>
  <div class="ctl"><label for="xs-e2">Neutronenergie (eV)</label><input id="xs-e2" type="range" data-bind="lgE" data-instant min="-2.3" max="2" step="0.01" value="-1.6"><output data-show="Eshow" data-fmt="2"></output></div>
</div>
<div class="step">
  <p>Bij een resonantie zwelt het doel op. Bij 7 eV hebben het neutron en de kern samen precies de energie van een van de eigen niveaus van de kern, dus wordt het veel makkelijker opgenomen: de schijf groeit ongeveer vijftig keer in oppervlak, hier tot ongeveer 400 barn.</p>
  <p>Ga een beetje weg van 7 eV en de schijf krimpt meteen terug: de piek in de curve is smal. Echte kernen hebben veel van zulke pieken; hoofdstuk 1 liet hun streepjescode zien.</p>
  <div class="ctl"><label for="xs-e3">Neutronenergie (eV)</label><input id="xs-e3" type="range" data-bind="lgE" data-instant min="-2.3" max="2" step="0.005" value="0.845"><output data-show="Eshow" data-fmt="2"></output></div>
</div>`,
};
