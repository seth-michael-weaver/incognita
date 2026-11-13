/* Danish (Dansk): part seven, nuclear weapons: history and control (nwhist, nwcities, nwrace, nwverify, nwdata) */
Object.assign(WT.L.ui, { tp_p7_k: "Del syv", tp_p7_h: "Atomvåben: historie og kontrol" });

WT.L.ch.nwhist = {
  num: "Lektion 1", title: "Fra opdagelsen til Trinity", short: "Opdagelse til Trinity",
  html: `
<div class="step">
  <h3>Atomet spaltes, 1938</h3>
  <p>I december 1938 fandt Otto Hahn og Fritz Strassmann i Berlin barium, et langt lettere grundstof, i uran, der var blevet beskudt med neutroner. Lise Meitner, som var flygtet fra Nazityskland den sommer, og hendes nevø Otto Frisch forklarede det inden for få uger: Urankernen var delt i to. Frisch kaldte det <b>fission</b>.</p>
</div>
<div class="step">
  <h3>Idéen om en kædereaktion</h3>
  <p>Hver spaltning frigør også nogle få neutroner, som kan spalte flere kerner. Leo Szilard havde forestillet sig en sådan <b>kædereaktion</b> allerede i 1933. I august 1939 skrev han udkastet til et brev, underskrevet af Albert Einstein, der advarede præsident Roosevelt om, at Tyskland kunne bruge den til at bygge en bombe. I december 1942 kørte Enrico Fermis hold den første kontrollerede kædereaktion i Chicago, i en stabel af uran og grafit.</p>
</div>
<div class="step">
  <h3>Manhattanprojektet</h3>
  <p>Fra 1942 byggede USA, sammen med Storbritannien og Canada, en hemmelig industri op, der på sit højeste beskæftigede omkring 130.000 mennesker. Oak Ridge i Tennessee udskilte det sjældne uran-235 fra naturligt uran, Hanford i Washington drev reaktorer, der producerede plutonium, og laboratoriet i Los Alamos i New Mexico, ledet af J. Robert Oppenheimer, arbejdede på våbnene.</p>
</div>
<div class="step">
  <h3>Trinity, 16. juli 1945</h3>
  <p>Den første kernesprængning lyste New Mexicos ørken op før daggry. Tre uger senere brugte USA to atombomber mod Japan, mod Hiroshima og Nagasaki. Tyskland havde overgivet sig i maj; landets eget krigsprojekt var aldrig kommet i nærheden af et våben.</p>
</div>`,
};

WT.L.ch.nwcities = {
  num: "Lektion 1", title: "Hiroshima og Nagasaki", short: "Hiroshima, Nagasaki",
  html: `
<div class="step">
  <h3>6. og 9. august 1945</h3>
  <p>En atombombe ødelagde centrum af Hiroshima den 6. august 1945, og en anden ramte Nagasaki tre dage senere. Ved udgangen af det år var mellem 90.000 og 166.000 mennesker døde i Hiroshima og mellem 60.000 og 80.000 i Nagasaki, de fleste civile. Japan meddelte sin overgivelse den 15. august.</p>
</div>
<div class="step">
  <h3>Hvordan en kernesprængning skader</h3>
  <p>Offentlige vejledninger fra beredskabet beskriver fire virkninger: <b>trykbølgen</b>, der vælter bygninger; <b>varmen</b>, et glimt, der forbrænder huden og starter brande; den <b>umiddelbare stråling</b>, gammastråler og neutroner i det første øjeblik; og <b>nedfaldet</b>, radioaktivt støv, som vinden fører bort. I 1945 skyldtes de fleste dødsfald trykbølgen, forbrændingerne og de brande, der fulgte.</p>
  <div class="btns" role="group" aria-label="Virkning"><button class="btn ghost" data-act="e0" aria-pressed="false">Trykbølge</button> <button class="btn ghost" data-act="e1" aria-pressed="false">Varme</button> <button class="btn ghost" data-act="e2" aria-pressed="false">Umiddelbar stråling</button> <button class="btn ghost" data-act="e3" aria-pressed="false">Nedfald</button></div>
</div>
<div class="step">
  <h3>De overlevende</h3>
  <p>De overlevende, <b>hibakusha</b>, har fortalt deres historie i årtier, og mange blev stemmer for afskaffelsen af atomvåben. Siden 1950 har en fælles japansk-amerikansk fond fulgt omkring 120.000 af dem og deres familier. Deres helbredsdata er den vigtigste kilde til det, vi ved om strålings langtidsvirkninger, herunder en øget kræftrisiko, og de ligger til grund for strålebeskyttelsesregler i hele verden.</p>
</div>`,
};

WT.L.ch.nwrace = {
  num: "Lektion 1", title: "Våbenkapløbet og traktaterne", short: "Kapløb, traktater",
  html: `
<div class="step">
  <h3>Et kapløb begynder</h3>
  <p>Sovjetunionen prøvesprængte sin første atombombe i 1949, Storbritannien i 1952, Frankrig i 1960 og Kina i 1964. I 1952 prøvesprængte USA den første <b>termonukleare</b> bombe eller brintbombe, hvor en fissionseksplosion sætter fusion af brintisotoper i gang; Sovjetunionen fulgte efter inden for få år. Disse våben kunne være langt kraftigere end bomberne fra 1945.</p>
</div>
<div class="step">
  <h3>Castle Bravo, 1954: nedfaldet</h3>
  <p>En amerikansk prøvesprængning ved Bikiniatollen i marts 1954 blev langt større end ventet. Dens nedfald, en hvid radioaktiv aske, faldt over de beboede atoller Rongelap og Utrik og over den japanske fiskerbåd Daigo Fukuryū Maru („Lykkedragen nr. 5“). Besætningen blev syg, og telegrafisten døde samme efterår. Forargelsen var med til at starte den verdensomspændende kampagne mod prøvesprængninger.</p>
  <div class="btns"><button class="btn ghost" data-act="wind">Afspil vinden igen</button></div>
</div>
<div class="step">
  <h3>Halvfjerds tusind sprænghoveder</h3>
  <p>Mellem 1945 og 2017 blev der foretaget omkring 2000 kernevåbenprøver, mere end 500 af dem i fri luft. Antallet af sprænghoveder i verden steg i fire årtier, til omkring 70.000 i midten af 1980'erne, og faldt derefter med mere end fire femtedele efter den kolde krigs afslutning.</p>
  <div class="ctl"><label for="nwr-y">År</label><input id="nwr-y" type="range" data-bind="yr" data-instant min="1945" max="2025" step="1" value="1986"><output data-show="yr" data-fmt="0"></output></div>
</div>
<div class="step">
  <h3>Traktaterne</h3>
  <p>Den delvise prøvestopaftale fra 1963 flyttede prøverne under jorden. <b>Ikke-spredningstraktaten</b> fra 1968, som næsten alle lande i dag har tilsluttet sig, forbyder spredning af våbnene og forpligter atommagterne til nedrustning. Traktater mellem USA og Sovjetunionen, senere Rusland, skar arsenalerne ned, og den omfattende prøvestopaftale fra 1996, underskrevet af det meste af verden men endnu ikke trådt i kraft, forbyder alle prøvesprængninger. Peg på en traktat.</p>
</div>`,
};

WT.L.ch.nwverify = {
  num: "Lektion 1", title: "Overvåge prøver, vogte materiale", short: "Verifikation",
  html: `
<div class="step">
  <h3>At lytte til Jorden</h3>
  <p>En traktat er kun så god som midlerne til at kontrollere den. Overvågningsnettet under den omfattende prøvestopaftale er bygget til at dække hele kloden: 170 seismiske stationer blandt mere end 300 anlæg. En underjordisk eksplosion er pludselig og lavtliggende og skubber klippen udad, så dens seismiske optegnelse ser anderledes ud end et jordskælvs forskydning langs en forkastning.</p>
  <div class="btns" role="group" aria-label="Kilde"><button class="btn ghost" data-act="vEx" aria-pressed="true">Eksplosion</button> <button class="btn ghost" data-act="vEq" aria-pressed="false">Jordskælv</button></div>
</div>
<div class="step">
  <h3>Lyd i luft og vand</h3>
  <p>Tres <b>infralyd</b>stationer lytter efter lyd, der er for dyb for øret, og som rejser tusindvis af kilometer gennem atmosfæren. Elleve <b>hydroakustiske</b> stationer lytter i havene, hvor et vandlag leder lyden på tværs af hele havbassiner.</p>
</div>
<div class="step">
  <h3>Xenon: et ur i luften</h3>
  <p>Selv en godt indesluttet underjordisk prøve kan lække radioaktivt xenon, en ædelgas, der ikke reagerer med noget. Dens isotoper henfalder med forskellig hast, så deres forhold fortæller, hvor længe siden fissionen skete, og hjælper med at skelne en prøve fra en reaktor eller et anlæg til medicinske isotoper. At aflæse det ur kræver kernedata: fissionsudbytter og halveringstider.</p>
  <div class="ctl"><label for="nwv-d">Dage siden fissionen</label><input id="nwv-d" type="range" data-bind="days" data-instant min="0" max="60" step="0.5" value="5"><output data-show="days" data-fmt="1"></output></div>
</div>
<div class="step">
  <h3>Sikkerhedskontrol: at tælle materialet</h3>
  <p>Under ikke-spredningstraktaten kontrollerer Det Internationale Atomenergiagentur (IAEA), at anmeldt nukleart materiale forbliver i fredelig brug. Inspektørerne fører regnskab, plomberer beholdere, overvåger med kameraer og tager aftørringsprøver. De måler også: Gammastrålingen fra uran-235 afslører, hvor beriget uranet er, og neutrontælling vejer plutonium. Begge målinger hviler på kernedata.</p>
</div>`,
};

WT.L.ch.nwdata = {
  num: "Lektion 1", title: "Reaktorer, våben og kernedata", short: "Reaktor eller våben",
  html: `
<div class="step">
  <h3>Spalte og sammensmelte</h3>
  <p>Kerneenergi kommer fra to modsatte reaktioner. <b>Fission</b> spalter en tung kerne som uran; <b>fusion</b> smelter lette kerner som brint sammen. Begge omdanner lidt masse til meget energi, som <a href="./#binding" data-keep-lang>bindingsenergikurven</a> viser. Kraftreaktorer bruger fission; Solen og de <a href="#fusion">fusion</a>smaskiner, der bygges i dag, bruger fusion.</p>
</div>
<div class="step">
  <h3>Hvorfor en reaktor ikke kan eksplodere som en bombe</h3>
  <p>En kraftreaktor og et våben bruger begge fission, men næsten intet andet ligner hinanden. Reaktorbrændsel er mest uran-238 med kun nogle få procent uran-235. Kædereaktionen holdes i balance, i takt med den lille andel neutroner, der kommer for sent, og når brændslet bliver varmere, bremser fysikken den selv. Reaktorulykker kan være meget alvorlige, gennem overophedning, damp eller brint (se <a href="#accidents">tre ulykker</a>), men en kraftreaktor kan ikke blive til en kernesprængning.</p>
</div>
<div class="step">
  <h3>Berigelsen betyder noget</h3>
  <p>Naturligt uran indeholder 0,7 % uran-235. Brændsel til kraftreaktorer beriges til omkring 3–5 %. Alt under 20 % kaldes <b>lavt beriget uran</b> og regnes ikke for brugbart til våben; fra 20 % og op er det højt beriget og bevogtes under de strengeste kontroller. Siden 1978 er mange forskningsreaktorer verden over blevet omstillet fra højt til lavt beriget brændsel.</p>
</div>
<div class="step">
  <h3>Kernedata for sikkerhed og verifikation</h3>
  <p>Overalt hvor fissilt materiale håndteres, på brændselsfabrikker, i transportbeholdere og lagerbassiner, beregner ingeniører, hvor tæt det er på en kædereaktion, og holder en bred margin; de beregninger hviler på evaluerede kernedata. Da den margin blev ignoreret, som på et brændselsanlæg i Tokaimura i Japan i 1999, døde arbejdere. De samme data, halveringstider, fissionsudbytter og tværsnit, lader inspektører måle materiale og overvågningsnettet aflæse en xenonprøve.</p>
</div>`,
};

Object.assign(WT.L.labels, {
  // nwhist
  "fission: a heavy nucleus splits into two lighter ones": "fission: en tung kerne spaltes i to lettere",
  "fission: one nucleus splits in two": "fission: én kerne deles i to",
  "two lighter nuclei": "to lettere kerner", "and a few free neutrons": "og nogle få frie neutroner",
  "after Meitner & Frisch {#} · illustration": "efter Meitner & Frisch {#} · illustration",
  "first split": "første spaltning", "generation {#}": "generation {#}",
  "each split frees neutrons that can split more nuclei: a chain reaction": "hver spaltning frigør neutroner, der kan spalte flere kerner: en kædereaktion",
  "each split frees neutrons that split more nuclei": "hver spaltning frigør neutroner til flere spaltninger",
  "the idea only · illustration": "kun idéen · illustration",
  "Oak Ridge, Tennessee": "Oak Ridge, Tennessee", "Hanford, Washington": "Hanford, Washington", "Los Alamos, New Mexico": "Los Alamos, New Mexico",
  "separating uranium{#}": "udskille uran{#}", "reactors making plutonium": "reaktorer til plutonium", "the laboratory": "laboratoriet",
  "three secret sites, {#}–{#}": "tre hemmelige steder, {#}–{#}", "after US DOE / OSTI, The Manhattan Project": "efter US DOE / OSTI, The Manhattan Project",
  "fission found": "fission opdaget", "Einstein–Szilard letter": "Einstein-Szilard-brevet", "Manhattan Project": "Manhattanprojektet",
  "first chain reaction": "første kædereaktion", "Trinity": "Trinity", "Hiroshima, Nagasaki": "Hiroshima, Nagasaki",
  "Dec {#} · fission discovered in Berlin": "dec. {#} · fission opdaget i Berlin",
  "Aug {#} · the Einstein–Szilard letter": "aug. {#} · Einstein-Szilard-brevet",
  "{#} · the Manhattan Project begins": "{#} · Manhattanprojektet begynder",
  "Dec {#} · first controlled chain reaction, Chicago": "dec. {#} · første kontrollerede kædereaktion, Chicago",
  "{#} July {#} · Trinity, New Mexico": "{#}. juli {#} · Trinity, New Mexico",
  "{#} and {#} August {#} · Hiroshima and Nagasaki": "{#}. og {#}. august {#} · Hiroshima og Nagasaki",
  "seven years from a laboratory discovery to a weapon": "syv år fra en laboratorieopdagelse til et våben", "{#} to {#}": "{#} til {#}",
  "sources: R. Rhodes, The Making of the Atomic Bomb ({#}); US DOE / OSTI history": "kilder: R. Rhodes, The Making of the Atomic Bomb ({#}); historie fra US DOE / OSTI",
  "sources: Rhodes {#}; US DOE": "kilder: Rhodes {#}; US DOE",
  // nwcities
  "Hiroshima": "Hiroshima", "Nagasaki": "Nagasaki",
  "one lantern for about {#} people who had died by the end of {#}": "én lanterne for omkring {#} mennesker, der var døde ved udgangen af {#}",
  "one lantern ≈ {#} people who died by the end of {#}": "én lanterne ≈ {#} døde ved udgangen af {#}",
  "faint lanterns: the range between the low and the high estimate": "svage lanterner: spændet mellem det lave og det høje skøn",
  "faint lanterns: the range of estimates": "svage lanterner: spændet i skønnene",
  "estimates: Radiation Effects Research Foundation (RERF)": "skøn: Radiation Effects Research Foundation (RERF)", "estimates: RERF": "skøn: RERF",
  "blast": "trykbølge", "heat": "varme", "prompt radiation": "umiddelbar stråling", "fallout": "nedfald",
  "a pressure wave that flattens buildings": "en trykbølge, der vælter bygninger",
  "a flash of light and heat that burns and starts fires": "et glimt af lys og varme, der brænder og starter brande",
  "gamma rays and neutrons in the first instant": "gammastråler og neutroner i det første øjeblik",
  "radioactive dust carried downwind, for days to weeks": "radioaktivt støv ført med vinden, i dage til uger",
  "pick an effect": "vælg en virkning", "pick an effect to see what it does": "vælg en virkning for at se, hvad den gør",
  "rings are qualitative, not to scale": "ringene er kvalitative, ikke målfaste", "after public civil-defence literature": "efter offentlig beredskabslitteratur",
  "about {#} survivors, followed since {#}": "omkring {#} overlevende, fulgt siden {#}",
  "about {#} survivors and their families, followed since {#}": "omkring {#} overlevende og deres familier, fulgt siden {#}",
  "one dot = {#} people": "én prik = {#} mennesker", "RERF Life Span Study": "RERF Life Span Study",
  "Radiation Effects Research Foundation, Life Span Study · Hiroshima Peace Memorial Museum": "Radiation Effects Research Foundation, Life Span Study · Hiroshimas Fredsmindemuseum",
  // nwrace
  "Bikini Atoll (test site)": "Bikiniatollen (prøveområde)", "Rongelap": "Rongelap", "Utrik": "Utrik",
  "fishing boat Lucky Dragon No. {#}": "fiskerbåden Lykkedragen nr. {#}", "Lucky Dragon No. {#}": "Lykkedragen nr. {#}", "wind": "vind",
  "schematic of the fallout, not to scale": "skitse af nedfaldet, ikke målfast", "schematic, not to scale": "skitse, ikke målfast",
  "after US DOE Marshall Islands history; Hiroshima Peace Memorial Museum": "efter US DOE's Marshalløerne-historie; Hiroshimas Fredsmindemuseum",
  "after US DOE history": "efter US DOE-historie",
  "{#}: about {#} warheads": "{#}: omkring {#} sprænghoveder",
  "nuclear warheads in the world": "atomsprænghoveder i verden", "nuclear warheads in the world (approximate)": "atomsprænghoveder i verden (omtrentligt)",
  "peak, {#}": "toppunkt, {#}", "peak, {#}: about {#}": "toppunkt, {#}: omkring {#}",
  "approximate, after the Federation of American Scientists": "omtrentligt, efter Federation of American Scientists", "approx., after FAS": "ca., efter FAS",
  "point at a green dot to read a treaty": "peg på en grøn prik for at læse en traktat", "tap a green dot: a treaty": "tryk på en grøn prik: en traktat",
  "{#} · Partial Test Ban": "{#} · Delvis prøvestopaftale", "{#} · Non-Proliferation Treaty": "{#} · Ikke-spredningstraktaten",
  "{#} · INF Treaty": "{#} · INF-traktaten", "{#} · START I": "{#} · START I", "{#} · Comprehensive Test Ban": "{#} · Omfattende prøvestopaftale", "{#} · New START": "{#} · New START",
  "no tests in the air, in space or under water": "ingen prøver i luften, i rummet eller under vand",
  "no spread of weapons; disarmament; peaceful use": "ingen spredning; nedrustning; fredelig brug",
  "a whole class of missiles removed": "en hel klasse missiler fjernet", "the first deep cuts": "de første dybe nedskæringer",
  "no test explosions at all (not yet in force)": "slet ingen prøvesprængninger (endnu ikke i kraft)", "limits on deployed warheads (expired {#})": "lofter over udsendte sprænghoveder (udløb {#})",
  // nwverify
  "explosion: shallow, pushes outward": "eksplosion: lavt, skubber udad", "earthquake: deeper, slip on a fault": "jordskælv: dybere, forskydning langs en forkastning",
  "explosion: sharp start, strong P waves": "eksplosion: skarp start, stærke P-bølger", "earthquake: weak start, strong S waves": "jordskælv: svag start, stærke S-bølger",
  "seismometer": "seismometer", "P": "P", "S": "S",
  "qualitative shapes · CTBTO International Monitoring System": "kvalitative former · CTBTO's internationale overvågningssystem",
  "CTBTO International Monitoring System": "CTBTO's internationale overvågningssystem",
  "infrasound": "infralyd", "hydroacoustic": "hydroakustik", "sound channelled in the ocean": "lyd ledt i havet", "sound in the sea": "lyd i havet",
  "{#} infrasound and {#} hydroacoustic stations in the network": "{#} infralyd- og {#} hydroakustiske stationer i nettet",
  "{#} infrasound · {#} hydroacoustic stations": "{#} infralyd · {#} hydroakustik",
  "xenon{#}": "xenon{#}", "xenon{#}m": "xenon{#}m", "Xe{#}": "Xe{#}", "Xe{#}m": "Xe{#}m",
  "half-life {#} h": "halveringstid {#} t", "half-life {#} d": "halveringstid {#} d", "start": "start",
  "{#} days after the fission": "{#} dage efter fissionen",
  "short-lived isotopes fade first, so the ratios read like a clock": "kortlivede isotoper forsvinder først, så forholdene kan aflæses som et ur",
  "the ratios change with time: a clock": "forholdene ændrer sig med tiden: et ur",
  "equal starting amounts, for illustration; real ratios come from fission yields": "lige store startmængder, til illustration; virkelige forhold kommer fra fissionsudbytter",
  "illustrative starting amounts": "illustrative startmængder", "half-lives: ENSDF / NUBASE{#}": "halveringstider: ENSDF / NUBASE{#}",
  "seal": "plombe", "camera": "kamera", "detector": "detektor",
  "uranium{#} line, {#} keV": "linje fra uran{#}, {#} keV", "U{#} line, {#} keV": "U{#}-linje, {#} keV", "gamma-ray energy →": "gammaenergi →",
  "the height of the peak tells how enriched the uranium is": "toppens højde viser, hvor beriget uranet er",
  "a bigger peak: more uranium{#}": "større top: mere uran{#}", "after IAEA safeguards; spectrum illustrative": "efter IAEA's sikkerhedskontrol; spektrum til illustration",
  // nwdata
  "fission: heavy splits": "fission: tungt spaltes", "fusion: light nuclei join": "fusion: lette kerner smelter sammen",
  "both turn a little mass into energy": "begge omdanner lidt masse til energi", "both release nuclear energy": "begge frigør kerneenergi",
  "a power reactor: four reasons it cannot explode like a bomb": "en kraftreaktor: fire grunde til, at den ikke kan eksplodere som en bombe", "a power reactor": "en kraftreaktor",
  "low-enriched fuel, mostly uranium{#}": "lavt beriget brændsel, mest uran{#}", "chain held in balance, not growing": "kæden i balance, vokser ikke",
  "late neutrons set a slow pace": "forsinkede neutroner sætter et langsomt tempo", "hotter fuel → fewer fissions": "varmere brændsel → færre fissioner",
  "after IAEA, US NRC, World Nuclear Association": "efter IAEA, US NRC, World Nuclear Association",
  "share of uranium{#}": "andel uran{#}", "low-enriched uranium (LEU): below {#} %": "lavt beriget uran (LEU): under {#} %", "LEU: below {#} %": "LEU: under {#} %",
  "highly enriched (HEU)": "højt beriget (HEU)", "HEU": "HEU", "natural uranium": "naturligt uran", "power-reactor fuel": "brændsel til kraftreaktorer", "reactor fuel": "reaktorbrændsel",
  "about {#}–{#} %": "omkring {#}–{#} %", "definitions: IAEA Safeguards Glossary": "definitioner: IAEA Safeguards Glossary",
  "evaluated nuclear data": "evaluerede kernedata", "fuel plants": "brændselsfabrikker", "transport casks": "transportbeholdere", "storage pools": "lagerbassiner",
  "safeguards": "sikkerhedskontrol", "test monitoring": "prøveovervågning",
  "the same data keep handling safe and let inspectors measure": "de samme data holder håndteringen sikker og lader inspektører måle",
  "safety margins and measurements rest on the data": "sikkerhedsmarginer og målinger hviler på dataene", "Tokaimura {#}: IAEA fact-finding report": "Tokaimura {#}: IAEA's undersøgelsesrapport",
});
