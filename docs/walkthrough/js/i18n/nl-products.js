/* Dutch (Nederlands): products (Hoofdstuk 14, splijtingsproducten en nawarmte) */
WT.L.ch.products = {
  num: "Hoofdstuk 14", title: "Splijtingsproducten en nawarmte", short: "Splijtingsproducten",
  html: `
<div class="step">
  <p>De stukken zijn ongelijk: één licht, één zwaar. De grafiek toont voor elke brokstukmassa A (protonen plus neutronen) het aandeel splijtingen dat die maakt. Twee bulten: lichte stukken rond A = 95, zware rond 139. Een gelijke splitsing, rond A = 117, is ongeveer honderd keer zeldzamer.</p>
  <p>Elke stippellijn ligt tien keer hoger dan de lijn eronder, zodat ook de zeldzame massa's te zien zijn. Tik op een balk of sleep de schuif: eronder staan de twee stukken van die splitsing. Hun massa's tellen op tot 234, niet 236 (uranium-235 plus het neutron), omdat er ook ongeveer 2,4 neutronen wegvliegen.</p>
  <div class="ctl"><label for="pr-a">Licht brokstuk A</label><input id="pr-a" type="range" data-bind="pick" data-instant min="70" max="117" step="1" value="95"><output data-show="pick" data-fmt="0"></output></div>
</div>
<div class="step">
  <p>Hun verval blijft de brandstof verwarmen na het afschakelen. De brokstukken zijn radioactief: ze vervallen een voor een, en elk verval geeft warmte af, of de kettingreactie nu loopt of niet.</p>
  <div class="ctl"><label for="pr-t">Tijd na het afschakelen</label><input id="pr-t" type="range" data-bind="lgt" data-instant min="0" max="8.5" step="0.01" value="0"><output id="pr-tout">1 s</output></div>
  <p>Sleep de tijd. Een seconde nadat de reactor stopt, geven de vervallen nog ongeveer 6 % van het volle vermogen; na een dag ongeveer een half procent; na een jaar een paar honderdsten van een procent, in een grote reactor nog steeds het grootste deel van een megawatt. Daarom wordt gebruikte brandstof jarenlang in koelbassins bewaard. De curve is de vuistregel van Way–Wigner: één eenvoudige formule voor het verval van alle brokstukken samen, na een jaar draaien. Beide schalen springen bij elk streepje met een factor tien.</p>
</div>`,
};
