/* Dutch (Nederlands): doppler (Hoofdstuk 19, dopplerverbreding) */
WT.L.ch.doppler = {
  num: "Hoofdstuk 19", title: "Dopplerverbreding", short: "Doppler",
  html: `
<div class="step">
  <h3>Thermische beweging van het doel</h3>
  <p>Hetere brandstof: haar atomen trillen sneller. Elk uraniumatoom zit niet meer stil wanneer een neutron aankomt.</p>
  <div class="ctl"><label for="dop-t1">Brandstoftemperatuur (K)</label><input id="dop-t1" type="range" data-bind="T" data-instant min="300" max="1500" step="10" value="600"><output data-show="T" data-fmt="0"></output></div>
</div>
<div class="step">
  <h3>Dopplerverbreding</h3>
  <p>De curve is de kans dat uranium-238 een neutron vangt, uitgezet tegen de energie van het neutron. Haar hoogte is een trefoppervlak in <b>barn</b> (één barn is 10<sup>−24</sup> cm², ruwweg de grootte die een kern aan een neutron toont). Doordat de atomen bewegen, ontmoeten sommige het neutron frontaal en lopen andere ervan weg, dus de smalle piek wordt uitgesmeerd: lager en breder. Haar oppervlak blijft gelijk.</p>
  <div class="ctl"><label for="dop-t2">Brandstoftemperatuur (K)</label><input id="dop-t2" type="range" data-bind="T" data-instant min="300" max="1500" step="10" value="1200"><output data-show="T" data-fmt="0"></output></div>
</div>
<div class="step">
  <h3>Zelfafscherming van resonanties</h3>
  <p>Een brandstoftablet is dik. De gearceerde band is het aandeel neutronen dat ze bij elke energie tegenhoudt. Het midden van de piek houdt al alles tegen, heet of koud, dus een lagere piek verliest daar niets; de bredere flanken vangen meer. Er gaan meer neutronen verloren aan vangst in plaats van splijting te veroorzaken, dus <i>k</i> daalt vanzelf. (<i>k</i> is tot hoeveel nieuwe splijtingen elke splijting leidt; hoofdstuk 20 legt het uit.)</p>
  <div class="ctl"><label for="dop-t3">Brandstoftemperatuur (K)</label><input id="dop-t3" type="range" data-bind="T" data-instant min="300" max="1500" step="10" value="900"><output data-show="T" data-fmt="0"></output></div>
</div>`,
};
