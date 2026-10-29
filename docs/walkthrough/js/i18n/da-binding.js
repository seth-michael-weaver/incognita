/* Danish: binding (Kapitel 3, bindingsenergi) */
WT.L.ch.binding = {
  num: "Kapitel 3", title: "Hvorfor kerner holder sammen", short: "Binding",
  html: `
<div class="step">
  <p>Højere på kurven betyder stærkere bundet. Hvert punkt er ét massetal A (antallet af protoner plus neutroner), og dets højde er den energi, det ville koste, pr. nukleon, at trække kernen helt fra hinanden. Træk i A og aflæs markøren: midten af kurven, omkring jern og nikkel, er toppen.</p>
  <div class="ctl"><label for="bi-a">Massetal A</label><input id="bi-a" type="range" data-bind="pick" data-instant min="2" max="260" step="1" value="56"><output data-show="pick" data-fmt="0"></output></div>
</div>
<div class="step">
  <p>Spalt uran: begge stykker ligger højere på kurven end det uran, de kom fra, så de samme nukleoner ender med at være stærkere bundet, og forskellen kommer ud som energi. Vælg det lettere fragment; det tungere er resten af de 236 nukleoner.</p>
  <div class="ctl"><label for="bi-f">Lettere fragment A</label><input id="bi-f" type="range" data-bind="frag" data-instant min="70" max="118" step="1" value="95"><output data-show="frag" data-fmt="0"></output></div>
  <p class="ctl-result" id="bi-split-out" aria-live="polite"></p>
  <p>Uanset opdelingen er det omkring 200 MeV: snesevis af millioner gange de få elektronvolt, som afbrænding af ét brændstofmolekyle giver.</p>
</div>
<div class="step">
  <p>Slå to lette kerner sammen til én. Hvis den nye kerne ligger højere på kurven, frigives der energi. Forbi toppen koster sammenslutning i stedet energi.</p>
  <div class="ctl"><label for="bi-u">Hver let kerne A</label><input id="bi-u" type="range" data-bind="fuse" data-instant min="2" max="60" step="1" value="2"><output data-show="fuse" data-fmt="0"></output></div>
  <p class="ctl-result" id="bi-fuse-out" aria-live="polite"></p>
</div>`,
};
