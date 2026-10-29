/* Dutch (Nederlands): binding (Hoofdstuk 3, waarom kernen bij elkaar blijven) */
WT.L.ch.binding = {
  num: "Hoofdstuk 3", title: "Waarom kernen bij elkaar blijven", short: "Bindingsenergie",
  html: `
<div class="step">
  <p>Hoger op de curve betekent steviger gebonden. Elk punt is één massagetal A (het aantal protonen plus neutronen), en zijn hoogte is de energie die het, per nucleon, zou kosten om die kern helemaal uit elkaar te trekken. Sleep A en lees de markering af: het midden van de curve, rond ijzer en nikkel, is de top.</p>
  <div class="ctl"><label for="bi-a">Massagetal A</label><input id="bi-a" type="range" data-bind="pick" data-instant min="2" max="260" step="1" value="56"><output data-show="pick" data-fmt="0"></output></div>
</div>
<div class="step">
  <p>Splijt uranium: beide stukken zitten hoger op de curve dan het uranium waaruit ze kwamen, dus dezelfde nucleonen zijn uiteindelijk steviger gebonden en het verschil komt vrij als energie. Kies het lichtere brokstuk; het zwaardere is de rest van de 236 nucleonen.</p>
  <div class="ctl"><label for="bi-f">Lichter brokstuk A</label><input id="bi-f" type="range" data-bind="frag" data-instant min="70" max="118" step="1" value="95"><output data-show="frag" data-fmt="0"></output></div>
  <p class="ctl-result" id="bi-split-out" aria-live="polite"></p>
  <p>Hoe het ook splijt, het is ongeveer 200 MeV: tientallen miljoenen keren de paar elektronvolt die het verbranden van één molecuul brandstof oplevert.</p>
</div>
<div class="step">
  <p>Voeg twee lichte kernen samen tot één. Als de nieuwe kern hoger op de curve zit, komt er energie vrij. Voorbij de top kost samenvoegen juist energie.</p>
  <div class="ctl"><label for="bi-u">Elke lichte kern A</label><input id="bi-u" type="range" data-bind="fuse" data-instant min="2" max="60" step="1" value="2"><output data-show="fuse" data-fmt="0"></output></div>
  <p class="ctl-result" id="bi-fuse-out" aria-live="polite"></p>
</div>`,
};
Object.assign(WT.L.labels, {
  "mass number A →": "massagetal A →",
  "binding energy per nucleon (MeV)": "bindingsenergie per nucleon (MeV)",
  "Ni{#}: most tightly bound": "Ni{#}: het sterkst gebonden",
  "measured masses (AME{#})": "gemeten massa's (AME{#})",
  "Fe{#}: {#} MeV per nucleon · {#} MeV in all": "Fe{#}: {#} MeV per nucleon · {#} MeV totaal",
});
