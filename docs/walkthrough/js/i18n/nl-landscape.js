/* Dutch (Nederlands): landscape (Hoofdstuk 4, het landschap van kernen) */
WT.L.ch.landscape = {
  num: "Hoofdstuk 4", title: "Het landschap van kernen", short: "Landschap",
  lead: "Elke kern die ooit iemand heeft gemaakt, op één kaart: tot nu toe 3.338, en maar 252 blijven eeuwig bestaan.",
  html: `
<div class="step">
  <h3>De nuclidenkaart</h3>
  <p>Elk vierkantje is één kern die echt in een experiment is waargenomen: neutronen tellen naar rechts, protonen naar boven. Bleke vierkantjes zijn gezien, maar hun massa is nog niet gewogen, alleen geschat. De <b>donkere</b> vierkantjes zijn de 252 die nooit vervallen. De andere vallen uit elkaar, de oranje in een oogwenk, de blauwe pas na jaren. De <em style="font-style:normal;color:var(--proton);font-weight:600">rode</em> rij is het element dat je met de schuif kiest: al zijn bekende isotopen.</p>
  <div class="ctl"><label for="ls-z">Bekijk element (protonen Z)</label><input id="ls-z" type="range" data-bind="zSel" data-instant min="1" max="110" step="1" value="26"><output data-show="zSel" data-fmt="0"></output></div>
  <p class="ctl-result" id="ls-z-out" aria-live="polite"></p>
</div>
<div class="step">
  <h3>Bindingsenergie over de kaart</h3>
  <p>Nu is elk vierkantje gekleurd naar zijn <b>bindingsenergie per nucleon</b>, hoe stevig elk neutron of proton wordt vastgehouden (hoofdstuk 3). De stabiele kernen liggen langs een rug van sterke binding; stap ervan af, met te veel neutronen of te veel protonen, en de binding neemt af. De sterkste van allemaal is nikkel-62. De dunne lijnen markeren de <b>magische getallen</b> (8, 20, 28, 50, 82, 126), waar kernen extra stevig gebonden zijn.</p>
</div>
<div class="step">
  <h3>Bètaverval richting stabiliteit</h3>
  <p>Kernen met hetzelfde totale aantal nucleonen (hetzelfde <b>massagetal</b> A) liggen op een diagonale lijn over de kaart, in <em style="font-style:normal;color:var(--proton);font-weight:600">rood</em> getekend. Begin met te veel neutronen, zoals de brokstukken van een gesplitste uraniumkern. Bij <b>bètaverval</b> verandert een neutron in een proton, dus de kern zet steeds één stap langs zijn lijn richting het steviger gebonden midden, tot hij de rug bereikt en stopt. De kleine grafiek toont dezelfde keten als een dal waar de kern in afrolt. Probeer A = 137: de keten passeert cesium-137, het langlevende product van reactorongevallen.</p>
  <div class="ctl"><label for="ls-a">Massagetal A</label><input id="ls-a" type="range" data-bind="aSel" data-instant min="8" max="250" step="1" value="137"><output data-show="aSel" data-fmt="0"></output></div>
  <p class="ctl-result" id="ls-a-out" aria-live="polite"></p>
</div>
<div class="step">
  <h3>Dekking door INCOGNITA</h3>
  <p>Dezelfde kaart, gekleurd naar wat onze bibliotheek voor elke kern bevat. <em style="font-style:normal;color:var(--fission);font-weight:600">Groen</em>: geëvalueerd uit zijn gemeten resonanties. De rest heeft een modelbestand dat alleen door de motor is gebouwd: <b>donker</b> voor stabiel of langlevend (klasse A), <em style="font-style:normal;color:var(--accent);font-weight:600">blauw</em> voor meer dan een dag (klasse B), <em style="font-style:normal;color:var(--warm);font-weight:600">oranje</em> voor kortlevender (klasse C). Grijze staan niet in de bibliotheek (vooral de lichtste kernen, en enkele die de motor niet kan draaien).</p>
</div>`,
};
Object.assign(WT.L.labels, {
  "neutrons N →": "neutronen N →",
  "protons Z ↑": "protonen Z ↑",
  "Fe: all its isotopes": "Fe: al zijn isotopen",
  "stable": "stabiel",
  "lives years": "leeft jaren",
  "gone in a blink": "weg in een oogwenk",
  "red: Fe (your pick)": "rood: Fe (jouw keuze)",
  "nickel{#}: most tightly bound": "nikkel-{#}: het sterkst gebonden",
  "held most tightly": "het sterkst vastgehouden",
  "middle": "midden",
  "held least": "het zwakst vastgehouden",
  "red: the A = {#} chain": "rood: de keten A = {#}",
  "A = {#}: deeper = more tightly bound": "A = {#}: dieper = sterker gebonden",
  "protons Z →": "protonen Z →",
  "measured resonances": "gemeten resonanties",
  "tier A": "klasse A",
  "tier B": "klasse B",
  "tier C": "klasse C",
  "not in library": "niet in bibliotheek",
});
