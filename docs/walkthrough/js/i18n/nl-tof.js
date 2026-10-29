/* Dutch (Nederlands): tof (Hoofdstuk 16, vluchttijdmetingen) */
WT.L.ch.tof = {
  num: "Hoofdstuk 16", title: "Vluchttijdmetingen", short: "Pieken meten",
  html: `
<div class="step">
  <p>De vliegtijd van een neutron vertelt zijn energie. Een korte puls neutronen met allerlei energieën verlaat de bron en snelt door een lege buis naar de detector; de snelle komen het eerst aan. De lengte <i>L</i> van de buis is bekend, dus elke aankomsttijd <i>t</i> geeft de snelheid van het neutron, en de snelheid geeft zijn energie:</p>
  <div class="formula">E = (72,3 · L / t)²   (E in eV, L in meter, t in microseconden)</div>
  <p>De klok boven de buis telt echte tijd sinds de puls; de vlucht is ongeveer 1400 keer langzamer getekend. Onder de buis wordt de laatste aankomst omgezet in een energie. Sleep de vluchtbaan: een langere buis spreidt dezelfde energieën over een langere tijd, zodat elk ervan fijner te onderscheiden is.</p>
  <div class="ctl"><label for="tof-l1">Vluchtbaan (m)</label><input id="tof-l1" type="range" data-bind="Lv" data-instant min="5" max="200" step="1" value="50"><output data-show="Lv" data-fmt="0"></output></div>
</div>
<div class="step">
  <p>Dun monster: de dip volgt de werkzame doorsnede. Er staat nu een monster in de bundel. Bij 6,7 eV hebben zijn kernen een resonantie en grijpen ze neutronen (de flitsen), dus komen er op het bijpassende moment minder aan. De grafiek vergelijkt de tellingen met en zonder het monster: de <b>transmissie</b>, 1 wanneer elk neutron erdoorheen komt.</p>
  <p>De stippen zijn gesimuleerde tellingen, met hun spreiding; de ononderbroken lijn is wat de detector gemiddeld registreert; de stippellijn is de vorm van de werkzame doorsnede zelf. Bij een dun monster kopieert de dip die vorm.</p>
  <div class="ctl"><label for="tof-d1">Dikte van het monster (µm)</label><input id="tof-d1" type="range" data-bind="lgT" data-instant min="0" max="3.5" step="0.01" value="0.5"><output data-show="thk" data-fmt="0"></output></div>
</div>
<div class="step">
  <p>Dik monster: de dip verzadigt. Bij de piekenergie vangt de voorkant van het monster elk neutron, dus het midden wordt zwart en blijft zwart hoe dik je het ook maakt; de dip kan alleen groeien door in de flanken te verbreden. Dit is <b>zelfafscherming</b>: de voorste lagen schermen de achterste af. Een dik monster vertelt dan meer over de flanken van de resonantie dan over zijn piek.</p>
  <div class="ctl"><label for="tof-d2">Dikte van het monster (µm)</label><input id="tof-d2" type="range" data-bind="lgT" data-instant min="0" max="3.5" step="0.01" value="3"><output data-show="thk" data-fmt="0"></output></div>
</div>
<div class="step">
  <p>Langere pulsen, kortere vluchten: de dip vervaagt. Drie dingen bepalen de breedte van een dip, alle drie onder de grafiek geschreven: de eigen breedte van de resonantie; de atomen van het monster die van warmte trillen, wat de energie van elke botsing een beetje uitsmeert (<b>Doppler</b>verbreding); en de tijdsonscherpte, omdat een langere puls of een kortere buis elke aankomsttijd, en dus elke energie, onzekerder maakt.</p>
  <p>Maak de puls langer of de buis korter: de dip wordt breder en ondieper, hoewel het aandeel neutronen dat hij wegneemt ongeveer gelijk blijft.</p>
  <div class="ctl"><label for="tof-p1">Pulsbreedte (µs)</label><input id="tof-p1" type="range" data-bind="lgDt" data-instant min="-2" max="1" step="0.01" value="0.3"><output data-show="dt" data-fmt="2"></output></div>
  <div class="ctl"><label for="tof-l2">Vluchtbaan (m)</label><input id="tof-l2" type="range" data-bind="Lv" data-instant min="5" max="200" step="1" value="20"><output data-show="Lv" data-fmt="0"></output></div>
</div>
<div class="step">
  <p>INCOGNITA werkt terug: het neemt gemeten tellingen als deze en vraagt welke resonantie, door ditzelfde experiment gehaald (dikte, warmte, tijdsonscherpte), ze reproduceert. Hier begint de fit bij een gok waarvan de neutronbreedte Γ<sub>n</sub> (hoe sterk het niveau neutronen vasthoudt) bijna vier keer te groot is (de blauwe curve), en verandert die stap voor stap tot de curve door de stippen loopt.</p>
  <p>De uitlezing toont de huidige gok en de <b>afwijking</b>: ongeveer 1 betekent dat de curve zo dicht bij de stippen ligt als hun telspreiding toelaat. Verander het experiment en de fit begint opnieuw, met nieuwe tellingen, en komt uit bij bijna dezelfde breedte; waar hij de stippen niet goed kan volgen, laat de afwijking dat zien.</p>
  <div class="ctl"><label for="tof-l3">Vluchtbaan (m)</label><input id="tof-l3" type="range" data-bind="Lv" data-instant min="5" max="200" step="1" value="50"><output data-show="Lv" data-fmt="0"></output></div>
  <div class="ctl"><label for="tof-d3">Dikte van het monster (µm)</label><input id="tof-d3" type="range" data-bind="lgT" data-instant min="0" max="3.5" step="0.01" value="1.5"><output data-show="thk" data-fmt="0"></output></div>
  <div class="ctl"><label for="tof-p2">Pulsbreedte (µs)</label><input id="tof-p2" type="range" data-bind="lgDt" data-instant min="-2" max="1" step="0.01" value="-1"><output data-show="dt" data-fmt="2"></output></div>
</div>`,
};
Object.assign(WT.L.labels, {
  "pulsed source": "gepulste bron",
  "detector": "detector",
  "L = {#} m · clock: {#} ms since the pulse": "L = {#} m · klok: {#} ms sinds de puls",
  "transmission": "transmissie",
  "cross-section shape (scaled)": "vorm werkzame doorsnede (geschaald)",
  "what the detector records": "wat de detector registreert",
  "simulated counts": "gesimuleerde tellingen",
  "fast neutrons arrive first, slow ones later: the clock sorts them by energy": "snelle neutronen komen eerst, langzame later: de klok sorteert ze op energie",
  "L = {#} m · clock: {#} µs since the pulse": "L = {#} m · klok: {#} µs sinds de puls",
  "last arrival: t = {#} µs → E = ({#} × {#} / {#})² = {#} eV": "laatste aankomst: t = {#} µs → E = ({#} × {#} / {#})² = {#} eV",
  "last arrival: t = {#} ms → E = ({#} × {#} / {#})² = {#} eV": "laatste aankomst: t = {#} ms → E = ({#} × {#} / {#})² = {#} eV",
  "sample": "monster",
  "L = {#} m · {#} eV arrives after {#} ms": "L = {#} m · {#} eV komt aan na {#} ms",
  "sample {#} µm · dip {#} % deep": "monster {#} µm · dip {#} % diep",
  "sample {#} µm · dip {#} % deep: black in the centre": "monster {#} µm · dip {#} % diep: zwart in het midden",
  "L = {#} m · {#} eV arrives after {#} µs": "L = {#} m · {#} eV komt aan na {#} µs",
  "width from timing {#} meV · from heat (Doppler) {#} meV · the resonance's own {#} meV": "breedte door timing {#} meV · door warmte (Doppler) {#} meV · eigen breedte {#} meV",
  "the fit's current guess": "huidige gok van de fit",
  "fit: Γn = {#} meV (put into the simulation: {#}) · misfit {#}": "fit: Γn = {#} meV (in de simulatie: {#}) · afwijking {#}",
});
