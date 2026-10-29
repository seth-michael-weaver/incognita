/* Dutch (Nederlands): direct (Hoofdstuk 6, directe reacties) */
WT.L.ch.direct = {
  num: "Hoofdstuk 6", title: "Directe reacties", short: "Directe reacties",
  lead: "Niet elk neutron dat de kern bereikt, wordt opgeslokt. Sommige strijken langs het oppervlak, geven de kern één duw en vliegen verder.",
  html: `
<div class="step">
  <p>Een neutron dat de kern alleen schampt, kan hem één keer in een aangeslagen niveau duwen en verder vliegen, meestal naar voren en maar een beetje langzamer. Dat is een <b>directe reactie</b>: één stap, voorbij in ongeveer 10⁻²² seconde. Hier vliegt een neutron voorbij op afstand <i>b</i>, de <b>impactparameter</b>, in kernstralen <i>R</i>; de gestippelde ring is de huid van de kern.</p>
  <div class="ctl"><label for="di-b">Richtpunt b (in stralen)</label><input id="di-b" type="range" data-bind="b" min="0" max="1.5" step="0.01" value="1.0"><output data-show="b" data-fmt="2"></output></div>
  <p>Sleep <i>b</i>. Onder ongeveer 0,8 wordt het neutron opgeslokt. Rond 1 schampt het en laat het de kern achter op zijn eerste aangeslagen niveau, 2⁺. Boven ongeveer 1,2 mist het en buigt het alleen af: <b>elastische verstrooiing</b>, de kern blijft onveranderd.</p>
</div>
<div class="step">
  <h3>Rotatie-excitatie van vervormde kernen</h3>
  <p>Een duw zet een uitgerekte kern (hoofdstuk 1) aan het roteren, de ladder van zijn <b>rotatieband</b> op: 0⁺, 2⁺, 4⁺, 6⁺, 8⁺. Het neutron kan de kern omhoog duwen en de kern kan terugduwen, dus geen enkel niveau kan op zichzelf worden uitgerekend. De motor lost ze allemaal tegelijk op: <b>gekoppelde kanalen</b>, waarbij elk kanaal één uitkomst is, hier één niveau van de band.</p>
  <div class="btns"><button class="btn" data-act="kick">Duw hem een niveau omhoog</button><button class="btn ghost" data-act="rpause">Pauze / verder</button></div>
  <div class="ctl"><label for="di-beta">Vervorming β₂</label><input id="di-beta" type="range" data-bind="beta2" min="0.05" max="0.4" step="0.01" value="0.25"><output data-show="beta2" data-fmt="2"></output></div>
  <p>De bogen laten zien welke niveaus verbonden zijn: <i>λ</i> = 2, de algehele uitrekking, verbindt buren; <i>λ</i> = 4, een fijnere bult, springt er twee. Sleep <i>β₂</i>: een sterker uitgerekte kern verbindt zijn niveaus sterker, en de bogen worden dikker. Omdat de band samen met het binnenkomende neutron wordt uitgewerkt, weet de motor precies hoeveel neutronen hij opeist, en geeft hij alleen de rest door aan de langzamere routes van de volgende hoofdstukken.</p>
</div>
<div class="step">
  <h3>Oppervlaktetrillingen</h3>
  <p>Een ronde kern kan rimpelen, en rimpelenergie komt in gelijke pakketjes die <b>fononen</b> heten. Eén fonon van de rimpeling van rugbybal naar schijf (<i>λ</i> = 2) geeft het 2⁺-niveau; twee geven drie niveaus, 0⁺, 2⁺ en 4⁺, bij de dubbele energie. Om die te bereiken zijn twee duwen achter elkaar nodig. De motor lost deze niveaus samen met de grondtoestand op.</p>
  <div class="ctl"><label for="di-lam">Vorm van de rimpeling λ</label><input id="di-lam" type="range" data-bind="lam" min="2" max="3" step="1" value="2" data-instant><output data-show="lam" data-fmt="0"></output></div>
  <div class="btns"><button class="btn ghost" data-act="ph1">Eén fonon</button><button class="btn ghost" data-act="ph2">Twee fononen</button></div>
  <p>Zet <i>λ</i> = 3 voor een peervormige rimpeling, waarvan het eerste niveau 3⁻ is. Druk op de knoppen om een of twee fononen toe te voegen.</p>
</div>
<div class="step">
  <h3>Directe reacties in één stap</h3>
  <p>Voor de meeste niveaus is de koppeling zwak en is één duw genoeg: <b>DWBA</b> (de Born-benadering met vervormde golven). De binnenkomende golf uit hoofdstuk 5 duwt de kern één keer, aan de rand, waar de potentiaal van diep naar nul zakt; de rand gloeit waar de golftoppen inslaan. De cirkelvormige golf die zich uitbreidt, zijn de neutronen die de kern aangeslagen achterlieten.</p>
  <div class="ctl"><label for="di-bd">Vervorming β van het niveau</label><input id="di-bd" type="range" data-bind="bd" min="0.02" max="0.4" step="0.01" value="0.2"><output data-show="bd" data-fmt="2"></output></div>
  <p>Sleep <i>β</i>: de rand wiebelt harder en de cirkels worden helderder, als <i>β</i>²: twee keer zoveel vervorming, vier keer zoveel neutronen. De motor haalt de <i>β</i> van elk niveau uit gemeten waarden, of uit systematiek waar er geen bekend is. Hoe de verstrooide neutronen zich over de hoeken verdelen, is een optionele extra uitvoer.</p>
</div>
<div class="step">
  <h3>Gigantische resonanties</h3>
  <p>Alle nucleonen kunnen samen bewegen: ademen, platdrukken en uitrekken, of in een peervorm zwaaien. Dit zijn <b>gigantische resonanties</b>. In deze kern van middelzware massa liggen ze ongeveer 7 tot 25 MeV hoger, elk enkele MeV breed, te breed om als één niveau te tellen; de bulten markeren de <b>excitatie-energie</b> van elk ervan.</p>
  <p>De motor legt de totale sterkte van elk vast met een <b>somregel</b>, een grens uit de basisnatuurkunde voor hoe sterk een kern kan reageren, en spreidt die als een bult boven het laatst bekende niveau. Deze bulten, plus duwen naar hoge niveaus, vormen het <b>collectieve continuüm</b>.</p>
  <div class="btns"><button class="btn ghost" data-act="mono">Ademen</button><button class="btn ghost" data-act="quad">Platdrukken</button><button class="btn ghost" data-act="oct">Peer</button></div>
  <p>De bekendste, protonen die tegen neutronen in heen en weer klotsen (de gigantische dipoolresonantie), absorbeert en zendt vooral licht uit, dus die hoort bij hoofdstuk 10.</p>
</div>
<div class="step">
  <h3>Directe vangst</h3>
  <p>Een vrij neutron kan rechtstreeks in een <b>lege baan</b> van de put vallen (een toegestane energie voor één neutron binnenin) en de overtollige energie uitzenden als een <em class="g">foton</em>. De kern wordt nooit warm. Dit is <b>directe vangst</b>. De motor kan haar berekenen uit dezelfde put als in hoofdstuk 5: de vrije golf buiten, de gebonden baan binnen, en het foton dat ze verbindt. Ze is optioneel en staat standaard uit.</p>
  <div class="btns"><button class="btn" data-act="drop">Laat een neutron erin vallen</button></div>
  <p>Directe vangst telt het zwaarst waar de gewone route, het verdelen van de energie van het neutron, zwak is: lichte kernen en kernen ver van de stabiliteit, met weinig niveaus die ver uit elkaar liggen.</p>
</div>
<div class="step">
  <h3>Directe versus compoundflux</h3>
  <p>De motor verdeelt de werkzame doorsnede voor reactie uit hoofdstuk 5 op volgorde: eerst directe reacties, dan snelle botsingen, en alleen de rest vormt een compoundkern. In de afbeelding ondergaat elk neutron een van drie lotgevallen: <b>direct</b> (schampt en vliegt verder), snel (stoot een nucleon eruit voordat de energie zich verspreidt: <b>pre-evenwicht</b>, hoofdstuk 7) of opgeslokt (een <b>compoundkern</b>, hoofdstuk 8). De stapels tellen ze.</p>
  <div class="ctl"><label for="di-e">Neutronenergie (MeV)</label><input id="di-e" type="range" data-bind="E" min="1" max="60" step="0.5" value="14"><output data-show="E" data-fmt="1"></output></div>
  <p>Sleep de energie en kijk hoe de stapels zich opnieuw vullen. Bij een paar MeV wordt bijna elk neutron opgeslokt. Bij tientallen MeV nemen directe reacties en snelle botsingen samen een groot deel voor hun rekening.</p>
  <div class="aside">In de code: <code>ecis/formfactor.py</code>, <code>ecis/coupling.py</code>, <code>ecis/solver.py</code> (vervormde potentiaal, gekoppelde kanalen voor rotoren en vibratoren), <code>ecis/dwba.py</code> en <code>direct/dwba.py</code> (enkele duw, gigantische resonanties, collectief continuüm), <code>direct/racapcalc.py</code> (directe vangst, optioneel, standaard uit), <code>compound/normalization.py</code> (de boekhouding).</div>
</div>`,
};
Object.assign(WT.L.labels, {
  // scene: aim
  "skin (surface)": "huid (oppervlak)",
  "b = {#} R": "b = {#} R",
  "absorbed: its energy is shared by all nucleons": "geabsorbeerd: zijn energie wordt over alle nucleonen verdeeld",
  "{#}⁺ level": "{#}⁺-niveau",
  "one push leaves the nucleus on {#}⁺; neutron flies on": "één duw laat de kern op {#}⁺; het neutron vliegt door",
  "a miss: deflected, nucleus unchanged (elastic)": "gemist: afgebogen, kern onveranderd (elastisch)",
  // scene: rotor
  "at rest: {#}⁺": "in rust: {#}⁺",
  "rotating: {#}⁺": "roterend: {#}⁺",
  "rotating: {#}⁺ (paused)": "roterend: {#}⁺ (gepauzeerd)",
  "λ = {#}": "λ = {#}",
  "levels solved together": "niveaus samen opgelost",
  // scene: vibrator
  "quadrupole ripple: football ↔ disc": "quadrupoolrimpeling: rugbybal ↔ schijf",
  "octupole ripple: pear ↔ pear": "octupoolrimpeling: peer ↔ peer",
  "{#}⁺  no phonon": "{#}⁺  geen fonon",
  "{#}⁺  one phonon": "{#}⁺  één fonon",
  "{#}⁻  one phonon": "{#}⁻  één fonon",
  "{#}⁺ {#}⁺ {#}⁺  two phonons": "{#}⁺ {#}⁺ {#}⁺  twee fononen",
  "{#}⁺ {#}⁺ {#}⁺ {#}⁺  two phonons": "{#}⁺ {#}⁺ {#}⁺ {#}⁺  twee fononen",
  "one push": "één duw",
  "two pushes": "twee duwen",
  "two phonons": "twee fononen",
  "equal energy steps": "gelijke energiestappen",
  // scene: DWBA
  "rim: the push happens here": "rand: hier gebeurt de duw",
  "incoming wave": "binnenkomende golf",
  "outgoing: nucleus left excited": "uitgaand: kern aangeslagen achtergelaten",
  "outgoing circles: the nucleus left on an excited level": "uitgaande cirkels: de kern achtergelaten op een aangeslagen niveau",
  "push strength ∝ β²: {#}× that at β = {#}": "duwsterkte ∝ β²: {#}× die bij β = {#}",
  // scene: giant resonances
  "breathing": "ademen",
  "squash and stretch": "platdrukken en uitrekken",
  "pear": "peer",
  "breathing (monopole)": "ademen (monopool)",
  "squash and stretch (quadrupole)": "platdrukken en uitrekken (quadrupool)",
  "pear-shaped (octupole), low and high": "peervormig (octupool), laag en hoog",
  "about {#} MeV up": "ongeveer {#} MeV hoger",
  "last known level": "laatst bekende niveau",
  "excitation energy (MeV) →": "excitatie-energie (MeV) →",
  // scene: direct capture
  "free: outside the nucleus": "vrij: buiten de kern",
  "empty orbit": "lege baan",
  "drops straight in; a photon carries off the spare energy": "valt er rechtstreeks in; een foton neemt de overtollige energie mee",
  // scene: ledger
  "direct": "direct",
  "fast (pre-eq.)": "snel (pre-ev.)",
  "compound": "compound",
  "direct: grazed, flew on": "direct: geschampt, doorgevlogen",
  "fast collision: one out at once": "snelle botsing: er gaat er meteen één uit",
  "compound: swallowed": "compound: opgeslokt",
  "{#}% (model {#}%)": "{#}% (model {#}%)",
  "{#}% seen · model {#}%": "{#}% gezien · model {#}%",
  "{#} MeV neutrons on a medium-mass nucleus (illustrative shares)": "neutronen van {#} MeV op een middelzware kern (illustratieve aandelen)",
});
Object.assign(WT.L.labels, {
  "{#}⁺ at about {#} keV": "{#}⁺ bij ongeveer {#} keV",
  "bound in the orbit; press the button to drop another": "gebonden in de baan; druk op de knop voor nog een",
});
