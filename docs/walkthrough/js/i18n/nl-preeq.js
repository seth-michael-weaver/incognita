/* Dutch (Nederlands): preeq (Hoofdstuk 7, pre-evenwicht) */
WT.L.ch.preeq = {
  num: "Hoofdstuk 7", title: "Botsingen voor de rust", short: "Pre-evenwicht",
  lead: "Een neutron dat een kern binnenkomt, verdeelt zijn energie niet in één keer over iedereen. Tijdens de eerste paar botsingen houdt één deeltje het meeste ervan vast, en dat deeltje kan rechtstreeks weer naar buiten vliegen. Dit is pre-evenwicht: emissie “voordat de energie gelijk verdeeld is”.",
  html: `
<div class="step">
  <p>Twee putten, één voor <em class="p">protonen</em> en één voor <em class="n">neutronen</em>. Elk bolletje is een nucleon op een energieniveau, getekend als een sport; de sporten zijn van onderen gevuld tot aan het <b>fermi-oppervlak</b>. Een nucleon boven de gestippelde lijn ‘vrij’ heeft genoeg energie om te ontsnappen. De motor houdt protonen en neutronen apart bij.</p>
  <p>Het binnenkomende neutron zweeft erboven en houdt alle energie vast: die van zichzelf plus enkele MeV (miljoen elektronvolt) die bij zijn vangst vrijkomen.</p>
</div>
<div class="step">
  <h3>Paren optillen</h3>
  <p>Elke botsing tilt een nucleon naar een lege sport en laat een <b>gat</b> (een open ring) achter. Deeltjes boven het oppervlak en gaten eronder heten allebei <b>excitonen</b>. De eerste botsing maakt 2 deeltjes en 1 gat (n = 3); elke latere voegt er weer een paar aan toe.</p>
  <div class="btns"><button class="btn" data-act="collide">Botsen</button><button class="btn ghost" data-act="reset">Opnieuw beginnen</button></div>
  <p>Druk een paar keer op Botsen. Het opgetilde nucleon kan een proton of een neutron zijn, en de motor telt beide soorten. Met elk paar wordt de energie over meer delen verdeeld, dus het bovenste deeltje komt lager te zitten.</p>
</div>
<div class="step">
  <h3>De splitsing in elke fase</h3>
  <p>In elke fase ontsnapt het bovenste neutron (pijl omhoog, alleen als het boven de vrije lijn zit) of botst het opnieuw (pijl omlaag); de dikte toont de kansen. De ontsnappingssnelheid volgt uit <b>gedetailleerd evenwicht</b>: uit de kans op het omgekeerde proces, dat hetzelfde deeltje wordt geabsorbeerd, die hoofdstuk 5 berekent. De botsingssnelheid is de sterkte van één nucleon-nucleonbotsing maal het aantal nieuwe configuraties dat ze kan bereiken.</p>
  <div class="ctl"><label for="pe-n">Fase (excitonen n)</label><input id="pe-n" type="range" data-bind="n" min="3" max="11" step="2" value="3" data-instant><output data-show="n" data-fmt="0"></output></div>
  <p>Sleep de fase omhoog. In het begin houdt één deeltje het meeste van de energie vast, dus wat ontsnapt is snel. Later is de energie dun uitgesmeerd en komt er weinig uit.</p>
</div>
<div class="step">
  <h3>Waar de snelle staart vandaan komt</h3>
  <p>De stapel rechts is het <b>spectrum</b>: hoeveel neutronen er bij elke energie uitkomen, langzaam links, snel rechts. Elke reactie doorloopt de keten tot het bovenste neutron ontsnapt, en de kleur zegt wanneer: <em style="font-style:normal;color:var(--warm);font-weight:600">diep oranje</em> in fase 3, bleker later, <em class="n">blauw</em> als het pas naar buiten kwam nadat de kern tot rust was gekomen (hoofdstuk 8).</p>
  <div class="btns"><button class="btn" data-act="run">Draai 300 reacties</button></div>
  <p>Fase 3 bouwt een brede, bijna vlakke plank op die tot de maximale energie reikt. Latere fasen stapelen lager op. De blauwe bult is <b>verdamping</b>: zodra iedereen de energie deelt, sijpelen alleen langzame neutronen naar buiten, zoals stoom uit een hete vloeistof.</p>
  <div class="ctl"><label for="pe-e">Neutronenergie</label><input id="pe-e" type="range" data-bind="E" min="5" max="60" step="0.5" value="20"><output data-show="E" data-fmt="1"></output></div>
  <p>Sleep de energie van het binnenkomende neutron: er draait een nieuwe reeks en de plank rekt verder uit. Verdamping alleen maakt nooit snelle neutronen.</p>
</div>
<div class="step">
  <h3>Configuraties tellen</h3>
  <p>De teller loopt elke manier af om deeltjes op lege sporten en gaten in gevulde sporten te zetten, zodanig dat hun energieën optellen tot de te verdelen energie (de sporten liggen hier 1 MeV uit elkaar). Nucleonen zijn fermionen: geen twee delen een sport, dus een deeltje moet op een lege sport terechtkomen en een gat ontstaat alleen waar een nucleon zat. Dit is <b>Pauli-blokkering</b>.</p>
  <div class="ctl"><label for="pe-u">Te verdelen energie (MeV)</label><input id="pe-u" type="range" data-bind="U" min="2" max="16" step="1" value="8" data-instant><output data-show="U" data-fmt="0"></output></div>
  <div class="btns"><button class="btn" data-act="addpair">Voeg een paar toe</button><button class="btn ghost" data-act="droppair">Haal een paar weg</button></div>
  <p>Voeg een paar toe en de telling springt omhoog; verhoog de energie en ze stijgt ruwweg als <i>E</i><sup>n−1</sup>. Deze telling, de <b>deeltje-gattoestandsdichtheid</b>, bepaalt de botsingssnelheid: meer configuraties, meer plekken waar een botsing naartoe kan leiden. De motor telt op de echte ladder, met sporten een fractie van een MeV uit elkaar, en voegt één grens toe die je bij hoge energie ziet: een gat kan niet onder de bodem van de put zitten.</p>
</div>
<div class="step">
  <h3>Ook clusters vertrekken</h3>
  <p>Kleine clusters kunnen ook vroeg vertrekken. Bij een <b>pick-up</b> grijpt een proton op weg naar buiten een neutron aan het oppervlak en vertrekt ermee als een <em class="n">deuteron</em>; grijpt het er twee, dan levert dat een triton of helium-3 op. Bij een <b>knock-out</b> raakt het binnenkomende neutron een <em class="a">alfadeeltje</em> (twee protonen en twee neutronen) dat al bij het oppervlak gevormd is, en stoot het eruit. De motor gebruikt voor beide de formules van Kalbach.</p>
  <div class="btns"><button class="btn ghost" data-act="pickup">Pik een neutron op → d</button><button class="btn ghost" data-act="knock">Stoot een α eruit</button></div>
  <p>Druk op een knop om er een te bekijken. Beide geven deuteronen en alfa's een eigen snelle staart, die net begint boven de energie die het kost om elk ervan eruit te halen.</p>
</div>
<div class="step">
  <h3>Een tweede snelle</h3>
  <p>Bij hoge energie kan een tweede opgetild nucleon nog boven de vrije lijn zitten wanneer het eerste neutron vertrekt, en ook ontsnappen, als snel neutron of proton. De putten spelen telkens één reactie af, met de energieschaal ingedrukt.</p>
  <div class="ctl"><label for="pe-e2">Neutronenergie</label><input id="pe-e2" type="range" data-bind="E" min="5" max="80" step="0.5" value="40"><output data-show="E" data-fmt="1"></output></div>
  <p>Sleep de energie. Onder ongeveer 20 MeV komt het tweede nucleon zelden over de lijn; daarboven stoten steeds meer reacties twee snelle deeltjes af. Dit is <b>meervoudig pre-evenwicht</b>, dat de motor vanaf 20 MeV meeneemt. Wat niet vertrokken is, wordt de compoundkern van het volgende hoofdstuk. Onder een paar MeV (het hoogste gebruikte discrete niveau van de trefkern) slaat de motor de keten helemaal over.</p>
  <div class="aside">In de code: <code>preeq/exciton.py</code> (excitonketen met twee componenten, botsings- en ontsnappingssnelheden), <code>density/particle_hole.py</code> (deeltje-gattoestandsdichtheden met correcties voor Pauli en de eindige put), <code>preeq/complex.py</code> (pick-up, stripping en α-knock-out volgens Kalbach), <code>preeq/multi.py</code> (meervoudig pre-evenwicht), <code>compound/normalization.py</code> (overdracht aan de compoundkern).</div>
</div>`,
};
Object.assign(WT.L.labels, {
  // wells
  "protons": "protonen",
  "neutrons": "neutronen",
  "Fermi": "Fermi",
  "Fermi surface": "fermi-oppervlak",
  "free": "vrij",
  "free: can escape": "vrij: kan ontsnappen",
  "all the energy in one nucleon": "alle energie in één nucleon",
  "{#} particle, {#} holes": "{#} deeltje, {#} gaten",
  // pairs
  "{#} particle, {#} holes: n = {#}": "{#} deeltje, {#} gaten: n = {#}",
  "{#} particle, {#} hole: n = {#}": "{#} deeltje, {#} gat: n = {#}",
  "{#} particles, {#} hole: n = {#}": "{#} deeltjes, {#} gat: n = {#}",
  "{#} particles, {#} holes: n = {#}": "{#} deeltjes, {#} gaten: n = {#}",
  "protons: {#} lifted, {#} hole": "protonen: {#} opgetild, {#} gat",
  "protons: {#} lifted, {#} holes": "protonen: {#} opgetild, {#} gaten",
  "neutrons: {#} lifted, {#} hole": "neutronen: {#} opgetild, {#} gat",
  "neutrons: {#} lifted, {#} holes": "neutronen: {#} opgetild, {#} gaten",
  "chain ends: the rest becomes a compound nucleus": "einde keten: de rest wordt een compoundkern",
  // fork
  "about {#} MeV above surface": "ongeveer {#} MeV boven het oppervlak",
  "escapes  {#}%": "ontsnapt  {#}%",
  "collides again  {#}%": "botst opnieuw  {#}%",
  "below the free line: it cannot leave": "onder de vrije lijn: kan niet weg",
  "n = {#}: {#} particles, {#} hole, {#} MeV": "n = {#}: {#} deeltjes, {#} gat, {#} MeV",
  "n = {#}: {#} particles, {#} holes, {#} MeV": "n = {#}: {#} deeltjes, {#} gaten, {#} MeV",
  "stage n = {#}: {#} particles and {#} hole share {#} MeV": "fase n = {#}: {#} deeltjes en {#} gat delen {#} MeV",
  "stage n = {#}: {#} particles and {#} holes share {#} MeV": "fase n = {#}: {#} deeltjes en {#} gaten delen {#} MeV",
  // tail
  "max {#} MeV": "max. {#} MeV",
  "slow": "langzaam",
  "fast →": "snel →",
  "stage {#}": "fase {#}",
  "chain over: compound": "keten voorbij: compound",
  "left at:": "vertrok bij:",
  "neutron left at:": "neutron vertrok bij:",
  "evaporation": "verdamping",
  "{#} of {#} landed · {#} left during the chain": "{#} van {#} geland · {#} vertrokken tijdens de keten",
  // pauli
  "well bottom: no deeper hole": "bodem van de put: geen dieper gat",
  "bottom of the well": "bodem van de put",
  "{#} MeV to share": "{#} MeV te verdelen",
  "{#} particles · {#} hole": "{#} deeltjes · {#} gat",
  "{#} particles · {#} holes": "{#} deeltjes · {#} gaten",
  "ways, all counted": "manieren, alle geteld",
  "arrangements so far": "configuraties tot nu toe",
  "one more pair: {#} ways": "één paar meer: {#} manieren",
  "never two on one rung · holes only where a nucleon was": "nooit twee op één sport · gaten alleen waar een nucleon zat",
  "(first {#} shown as ticks)": "(eerste {#} als streepjes)",
  // cluster
  "a deuteron leaves": "een deuteron vertrekt",
  "grabs a neutron at the edge": "grijpt een neutron aan de rand",
  "a fast proton heads out": "een snel proton gaat naar buiten",
  "an α ({#} protons + {#} neutrons) waits at the edge": "een α ({#} protonen + {#} neutronen) wacht aan de rand",
  "knocked straight out": "er meteen uitgestoten",
  // second
  "first fast neutron": "eerste snelle neutron",
  "second fast proton": "tweede snelle proton",
  "second fast neutron": "tweede snelle neutron",
  "below the free line: stays": "onder de vrije lijn: blijft",
  "below the free line: it stays": "onder de vrije lijn: het blijft",
  "the rest settles: compound nucleus": "de rest komt tot rust: compoundkern",
  "{#} MeV carried in": "{#} MeV meegebracht",
  "second fast particle in {#} of the last {#} reactions": "tweede snelle deeltje in {#} van de laatste {#} reacties",
});
