/* Dutch (Nederlands): decay (Hoofdstuk 9, een uitgang kiezen) */
WT.L.ch.decay = {
  num: "Hoofdstuk 9", title: "Een uitgang kiezen", short: "Verval",
  lead: "De compoundkern moet haar energie kwijt door een deeltje of een foton uit te zenden. Dit hoofdstuk tekent elke uitweg als een deur. De taak van de motor is te zeggen welk deel van de flux (de stroom reacties die hier aankomt) door elke deur vertrekt.",
  html: `
<div class="step">
  <p>Eén deur per uitgang: een <em class="g">foton</em> (γ), een <em class="n">neutron</em> (n), een <em class="p">proton</em> (p), een <em class="a">alfadeeltje</em> (α: twee protonen en twee neutronen) en, alleen voor zware kernen, <em class="f">splijting</em> (in tweeën splitsen). De verlichte opening in elke deur is het aandeel van die uitgang, en de bolletjes stromen in hetzelfde tempo naar buiten; grijze deuren zijn dicht. Omdat de kern vergeten is hoe ze ontstond, gebruikt ze elke deur b naar verhouding van een gewicht:</p>
  <div class="formula">aandeel<sub>b</sub> = T<sub>b</sub> · ρ<sub>b</sub> / Σ<sub>c</sub> T<sub>c</sub> · ρ<sub>c</sub></div>
  <p>De <b>transmissiecoëfficiënt</b> <i>T</i> is de kans dat een deeltje dat de rand bereikt erdoor komt; voor deeltjes komt hij uit het optisch model van hoofdstuk 5, achterstevoren gedraaid. De <b>niveaudichtheid</b> ρ, naast elke deur geschreven, telt de toestanden waarin de overgebleven kern terecht kan komen. Verdelen volgens <i>T</i> maal ρ is de regel van <b>Hauser–Feshbach</b>. Bij 10 MeV neemt de neutrondeur bijna alles.</p>
</div>
<div class="step">
  <h3>Waarom de meeste deeltjes langzaam naar buiten komen</h3>
  <p>De neutrondeur, opgesplitst naar uitgaande energie ε (langzaam links, snel rechts). De opening <i>T</i>(ε) van elke deur wordt breder voor snellere neutronen. Eronder staat de menigte toestanden waarin de overgebleven kern kan zijn: een langzaam neutron laat het meeste van de energie achter, waar toestanden volop zijn, dus de menigten krimpen naar rechts.</p>
  <div class="ctl"><label for="dc-sp">Beschikbare energie</label><input id="dc-sp" type="range" data-bind="spare" min="1" max="12" step="0.5" value="5"><output data-show="spare" data-fmt="1"></output></div>
  <p>Deur × menigte maakt van de stapel een bult, het <b>verdampingsspectrum</b>, zoals stoom die uit een hete vloeistof ontsnapt. Sleep de beschikbare energie (in MeV, miljoen elektronvolt): de stapel begint opnieuw, en zijn piek blijft rond 1 MeV, bepaald door de kerntemperatuur. Extra energie maakt vooral de overgebleven kern heter.</p>
</div>
<div class="step">
  <h3>Geladen deeltjes moeten klimmen</h3>
  <p>De energie van een proton op elke afstand r van het middelpunt: binnen een put, en buiten een heuvel door de elektrische (coulomb)afstoting, die afneemt als 1/r. Onder de top van de heuvel kan het proton, dat in de put heen en weer rammelt, alleen door het gearceerde stuk <b>tunnelen</b>, een quantumeffect dat eens in de vele botsingen tegen de wand lukt.</p>
  <div class="ctl"><label for="dc-ce">Deeltjesenergie</label><input id="dc-ce" type="range" data-bind="eps" min="0.5" max="12" step="0.1" value="3"><output data-show="eps" data-fmt="1"></output></div>
  <div class="btns"><button class="btn ghost" data-act="toggleAlpha">Wissel proton / alfa</button></div>
  <p>Sleep de energie omlaag en kijk hoe de tunnel breder wordt; wissel dan naar de alfa, wiens twee ladingen tegenover een ongeveer twee keer zo hoge heuvel staan. Daarom winnen ongeladen neutronen meestal zodra ze weg kunnen, en daarom tellen proton- en alfa-uitgangen vooral voor lichte kernen en hoge energieën.</p>
</div>
<div class="step">
  <h3>Deuren gaan één voor één open</h3>
  <p>Elke deeltjesdeur gaat pas open boven haar <b>separatie-energie</b>, de kosten om dat deeltje eruit te halen: hier 8 MeV voor een neutron, 9 voor een proton, 7 voor een alfa. Onder de 8 MeV van het neutron geeft bijna elk verval licht af.</p>
  <div class="ctl"><label for="dc-e">Excitatie-energie</label><input id="dc-e" type="range" data-bind="E" min="5" max="24" step="0.1" value="7"><output data-show="E" data-fmt="1"></output></div>
  <p>Sleep de excitatie-energie voorbij 8 MeV. Binnen ongeveer 1 MeV zwaait de neutrondeur wijd open en zakt het fotonaandeel met een factor honderd. De proton- en alfadeuren lichten later op en blijven smal, tegengehouden door hun coulombheuvels.</p>
</div>
<div class="step">
  <h3>Spin en pariteit moeten kloppen</h3>
  <p>De compoundkern (boven) heeft spin <i>J</i>; de toestanden van de overgebleven kern zitten eronder in laden naar spin <i>J</i>′. Het neutron neemt het verschil in spin en pariteit mee: als het vertrekt met baanimpulsmoment <i>l</i>, verandert het de spin met hoogstens <i>l</i> + ½ en keert het de pariteit om als <i>l</i> oneven is. Een grotere <i>l</i> betekent een smallere deur; de deur van elke la is de kleinste <i>l</i> die haar bereikt. Dichte landingen behouden de pariteit; holle keren haar om.</p>
  <div class="ctl"><label for="dc-j">Compoundspin J</label><input id="dc-j" type="range" data-bind="J" min="0" max="10" step="1" value="2" data-instant><output id="dc-jout">5/2</output></div>
  <p>Sleep <i>J</i> omhoog. De open deuren schuiven naar laden met hoge spin, die weinig toestanden bevatten, terwijl de volle laden achter dichte deuren zitten. Een compoundkern met hoge spin zendt traag deeltjes uit, en dat geeft fotonen, en isomeren (langlevende toestanden, hoofdstuk 10), hun kans.</p>
</div>
<div class="step">
  <h3>De weg waarlangs je binnenkwam</h3>
  <p>Bij lage energie is de compoundkern een verzameling scherpe <b>resonanties</b>, energieën waarbij het neutron makkelijk wordt geabsorbeerd; er zijn er acht getekend, één per rij. Elk heeft willekeurige deurbreedten: de ingang (het neutronkanaal) links, breedte <i>x</i>, en de andere deuren, hier vooral fotonen, rechts, breedten <i>y</i>.</p>
  <div class="btns"><button class="btn" data-act="fire">Schiet 40 neutronen af</button><button class="btn ghost" data-act="reroll">Nieuwe resonanties</button></div>
  <p>Een neutron gaat resonantie <i>i</i> binnen met een kans evenredig met <i>x<sub>i</sub></i> en vertrekt via de ingang met kans <i>x<sub>i</sub></i> / (<i>x<sub>i</sub></i> + Σ<i>y</i>). Rijen met een brede ingang krijgen meer neutronen binnen en sturen er meer terug naar buiten, dus het echte aandeel dat terugkeert (een <b>gemiddelde van producten</b>) is groter dan de schatting uit gemiddelde breedten (een <b>product van gemiddelden</b>). De verhouding is de <b>elastische versterking</b>, en de <b>breedtefluctuatiecorrectie</b> verschuift die flux van de andere deuren naar de ingang.</p>
  <div class="ctl"><label for="dc-n">Andere deuren</label><input id="dc-n" type="range" data-bind="Nch" min="1" max="12" step="1" value="2" data-instant><output data-show="Nch" data-fmt="0"></output></div>
  <p>Voeg deuren toe. Met veel uitgangen fluctueert hun totale breedte niet meer, dus de correctie telt het zwaarst waar weinig deuren open zijn. De motor past haar toe, met de formule van Moldauer, voor invallende neutronen tot aan de neutronseparatie-energie van de trefkern, en laat haar daarboven weg.</p>
</div>
<div class="step">
  <h3>Wat er overblijft om te verdelen</h3>
  <p>Niet elk geabsorbeerd neutron vormt een compoundkern. Sommige maken één schampende treffer en vliegen weg (directe reacties, hoofdstuk 6); sommige botsen een of twee keer rond en schieten er snel uit (pre-evenwicht, hoofdstuk 7). Alleen de rest blijft en verhit de kern. De tellers houden elk lot bij.</p>
  <div class="ctl"><label for="dc-einc">Neutronenergie</label><input id="dc-einc" type="range" data-bind="Einc" min="1" max="30" step="0.5" value="8"><output data-show="Einc" data-fmt="1"></output></div>
  <p>Alleen de neutronen die blijven, doen mee aan de deurencompetitie. Sleep de neutronenergie: bij een paar MeV blijven ze bijna allemaal; bij 30 MeV is ongeveer de helft vertrokken voordat het evenwicht bereikt is.</p>
  <div class="aside">In de code: <code>compound/prepare.py</code> (uitganggewichten T·ρ per spin en pariteit, selectieregels), <code>compound/target.py</code> (eerste verval met breedtefluctuaties), <code>compound/continuum.py</code> (verval van elke latere bin), <code>compound/wfc.py</code> (correcties van Moldauer, HRTW, GOE), <code>compound/normalization.py</code> (flux die overblijft voor de compoundkern), <code>omp/inverse.py</code> (deuren achterstevoren gedraaid).</div>
</div>`,
};
(function () {
  const L = {
    "{#} MeV": "{#} MeV",
    "n": "n", "p": "p", "fission": "splijting",
    "heavy only": "alleen zware",
    "heavy nuclei only": "alleen zware kernen",
    "shut below {#} MeV": "dicht onder {#} MeV",
    "the neutron door takes nearly everything": "de neutrondeur neemt bijna alles",
    "below the neutron threshold, nearly all decays emit light": "onder de neutrondrempel zendt bijna elk verval licht uit",
    "the doors share the decays": "de deuren verdelen de vervallen",
    // hump
    "{#} MeV to spare": "{#} MeV beschikbaar",
    "door gap = T(ε)": "opening = T(ε)",
    "doors: one per neutron energy ε, gap = T(ε)": "deuren: één per neutronenergie ε, opening = T(ε)",
    "× states left behind": "× achtergelaten toestanden",
    "× states the leftover nucleus can be in: many after a slow neutron": "× toestanden van de overgebleven kern: veel na een langzaam neutron",
    "most ≈ {#} MeV": "meeste ≈ {#} MeV",
    "= the pile": "= de stapel",
    "= where the neutrons land: the evaporation spectrum": "= waar de neutronen landen: het verdampingsspectrum",
    "slow": "langzaam",
    "slow neutrons": "langzame neutronen",
    "fast: {#} MeV →": "snel: {#} MeV →",
    "fast: {#} MeV (beyond, up to {#}, almost none)": "snel: {#} MeV (daarboven, tot {#}, bijna geen)",
    "fast: {#}": "snel: {#}",
    "fast: {#} MeV, the neutron takes it all": "snel: {#} MeV, het neutron neemt alles",
    // coulomb
    "well ↓": "put ↓",
    "well (much deeper) ↓": "put (veel dieper) ↓",
    "hilltop ≈ {#} MeV": "top ≈ {#} MeV",
    "falls as {#}/r": "neemt af als {#}/r",
    "Coulomb hill, falling as {#}/r": "coulombheuvel, neemt af als {#}/r",
    "tunnel: wider than the picture": "tunnel: breder dan de afbeelding",
    "tunnel {#} fm": "tunnel {#} fm",
    "proton energy {#} MeV": "protonenergie {#} MeV",
    "alpha energy {#} MeV": "alfa-energie {#} MeV",
    "proton energy {#} MeV ↑": "protonenergie {#} MeV ↑",
    "alpha energy {#} MeV ↑": "alfa-energie {#} MeV ↑",
    "above the hilltop: it rolls straight out": "boven de top: rolt er recht uit",
    "below the top, must tunnel: nearly every knock gets through": "onder de top, moet tunnelen: bijna elke botsing komt erdoor",
    "below the top, must tunnel: about {#} knock in {#} gets through": "onder de top, moet tunnelen: ongeveer {#} op de {#} botsingen komt erdoor",
    "below the top, must tunnel: about {#} knock in {#} × {#}^{#} gets through": "onder de top, moet tunnelen: ongeveer {#} op de {#} × {#}^{#} botsingen komt erdoor",
    "out": "eruit",
    "through after {#} knock": "erdoor na {#} botsing",
    "through after {#} knocks": "erdoor na {#} botsingen",
    "knocks so far: {#}": "botsingen tot nu toe: {#}",
    "distance r from the centre (fm) →": "afstand r tot het middelpunt (fm) →",
    // spin
    "J = {#}/{#}, parity +": "J = {#}/{#}, pariteit +",
    "l={#}": "l={#}",
    "leftover states by spin J′ →": "overgebleven toestanden naar spin J′ →",
    "drawers: states of the leftover nucleus by spin J′ (faint: states it holds) →": "laden: toestanden van de overgebleven kern naar spin J′ (vaag: toestanden die ze heeft) →",
    "open doors reach {#} %": "open deuren bereiken {#} %",
    "open doors reach about {#} % of the states": "open deuren bereiken ongeveer {#} % van de toestanden",
    "● parity kept (even l)   ○ flipped (odd l)": "● pariteit behouden (even l)   ○ omgekeerd (oneven l)",
    // wfc
    "entrance x": "ingang x",
    "entrance, width x": "ingang, breedte x",
    "{#} other doors, y": "{#} andere deuren, y",
    "{#} other door, widths y": "{#} andere deur, breedten y",
    "{#} other doors, widths y": "{#} andere deuren, breedten y",
    "back out the entrance: {#} of {#}": "terug via de ingang: {#} van {#}",
    "out another door: {#}": "via een andere deur: {#}",
    // norm
    "absorbed neutrons, {#} MeV →": "geabsorbeerde neutronen, {#} MeV →",
    "direct: {#} %": "direct: {#} %",
    "pre-equilibrium: {#} %": "pre-evenwicht: {#} %",
    "compound nucleus: {#} %": "compoundkern: {#} %",
    "one glancing hit on the surface": "één schampende treffer op het oppervlak",
    "a knock or two, then out fast": "een botsing of twee, dan snel eruit",
    "stayed: on to the door competition": "gebleven: door naar de deurencompetitie",
  };
  // door hint with level-count wording (fmt: "1", "N", "N thousand", "N million") and T possibly in e-notation
  const cnt = [["{#} state", "{#} toestand"], ["{#} states", "{#} toestanden"], ["{#} thousand states", "{#} duizend toestanden"], ["{#} million states", "{#} miljoen toestanden"]];
  for (const [e, s] of cnt) {
    L[`weak door × ≈ ${e}`] = `zwakke deur × ≈ ${s}`;
    L[`T ≈ {#} × ≈ ${e}`] = `T ≈ {#} × ≈ ${s}`;
    L[`T ≈ {#}e{#} × ≈ ${e}`] = `T ≈ {#}e{#} × ≈ ${s}`;
  }
  // share comparisons: each pct is "{#} %" or "≈ {#} %"
  const P = ["{#} %", "≈ {#} %"];
  for (const a of P) for (const b of P) {
    L[`back out ${a}, not ${b}: × {#}`] = `terug ${a}, niet ${b}: × {#}`;
    L[`share back out: average of products ${a} · product of averages ${b} · × {#}`] = `terug: gemiddelde van producten ${a} · product van gemiddelden ${b} · × {#}`;
    L[`other doors ${a}, not ${b}`] = `andere deuren ${a}, niet ${b}`;
    L[`other doors together: ${a} instead of ${b}`] = `andere deuren samen: ${a} in plaats van ${b}`;
  }
  Object.assign(WT.L.labels, L);
})();
