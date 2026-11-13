/* Dutch (Nederlands): part seven, nuclear weapons: history and control (nwhist, nwcities, nwrace, nwverify, nwdata) */
Object.assign(WT.L.ui, { tp_p7_k: "Deel zeven", tp_p7_h: "Kernwapens: geschiedenis en beheersing" });

WT.L.ch.nwhist = {
  num: "Les 1", title: "Van de ontdekking tot Trinity", short: "Ontdekking tot Trinity",
  html: `
<div class="step">
  <h3>Het splijten van het atoom, 1938</h3>
  <p>In december 1938 vonden Otto Hahn en Fritz Strassmann in Berlijn barium, een veel lichter element, in uranium dat met neutronen was beschoten. Lise Meitner, die die zomer uit nazi-Duitsland was gevlucht, en haar neef Otto Frisch verklaarden het binnen enkele weken: de uraniumkern was in tweeën gespleten. Frisch noemde het <b>splijting</b> (fissie).</p>
</div>
<div class="step">
  <h3>Het idee van een kettingreactie</h3>
  <p>Elke splijting maakt ook een paar neutronen vrij, die verdere kernen kunnen splijten. Leo Szilard had zich zo'n <b>kettingreactie</b> al in 1933 voorgesteld. In augustus 1939 stelde hij een brief op, ondertekend door Albert Einstein, die president Roosevelt waarschuwde dat Duitsland er een bom mee zou kunnen bouwen. In december 1942 bracht het team van Enrico Fermi in Chicago de eerste gecontroleerde kettingreactie op gang, in een stapel van uranium en grafiet.</p>
</div>
<div class="step">
  <h3>Het Manhattanproject</h3>
  <p>Vanaf 1942 bouwden de Verenigde Staten, samen met het Verenigd Koninkrijk en Canada, een geheime industrie op die op haar hoogtepunt zo'n 130.000 mensen werk gaf. Oak Ridge in Tennessee scheidde het zeldzame uranium-235 van natuurlijk uranium, Hanford in Washington had reactoren die plutonium maakten, en het laboratorium in Los Alamos in New Mexico, geleid door J. Robert Oppenheimer, werkte aan de wapens.</p>
</div>
<div class="step">
  <h3>Trinity, 16 juli 1945</h3>
  <p>De eerste kernexplosie verlichtte voor zonsopgang de woestijn van New Mexico. Drie weken later zetten de Verenigde Staten twee atoombommen in tegen Japan, op Hiroshima en Nagasaki. Duitsland had zich in mei overgegeven; zijn eigen oorlogsproject was nooit in de buurt van een wapen gekomen.</p>
</div>`,
};

WT.L.ch.nwcities = {
  num: "Les 1", title: "Hiroshima en Nagasaki", short: "Hiroshima, Nagasaki",
  html: `
<div class="step">
  <h3>6 en 9 augustus 1945</h3>
  <p>Een atoombom verwoestte op 6 augustus 1945 het centrum van Hiroshima, en een tweede trof drie dagen later Nagasaki. Tegen het einde van dat jaar waren in Hiroshima tussen 90.000 en 166.000 mensen omgekomen en in Nagasaki tussen 60.000 en 80.000, de meesten burgers. Japan kondigde op 15 augustus zijn capitulatie aan.</p>
</div>
<div class="step">
  <h3>Hoe een kernexplosie schade doet</h3>
  <p>Openbare handleidingen voor de bescherming van de bevolking beschrijven vier effecten: de <b>drukgolf</b>, die gebouwen platlegt; de <b>hitte</b>, een flits die de huid verbrandt en branden veroorzaakt; de <b>directe straling</b>, gammastraling en neutronen in het eerste ogenblik; en de <b>neerslag</b> (fall-out), radioactief stof dat de wind meevoert. In 1945 kwamen de meeste doden door de drukgolf, de brandwonden en de branden die volgden.</p>
  <div class="btns" role="group" aria-label="Effect"><button class="btn ghost" data-act="e0" aria-pressed="false">Drukgolf</button> <button class="btn ghost" data-act="e1" aria-pressed="false">Hitte</button> <button class="btn ghost" data-act="e2" aria-pressed="false">Directe straling</button> <button class="btn ghost" data-act="e3" aria-pressed="false">Neerslag</button></div>
</div>
<div class="step">
  <h3>De overlevenden</h3>
  <p>De overlevenden, de <b>hibakusha</b>, vertellen al tientallen jaren hun verhaal, en velen werden stemmen voor de afschaffing van kernwapens. Sinds 1950 volgt een gezamenlijke Japans-Amerikaanse stichting zo'n 120.000 van hen en hun families. Hun medische gegevens zijn de belangrijkste bron van wat bekend is over de langetermijngevolgen van straling, waaronder een verhoogd risico op kanker, en vormen de basis van de stralingsbeschermingsregels wereldwijd.</p>
</div>`,
};

WT.L.ch.nwrace = {
  num: "Les 1", title: "De wapenwedloop en de verdragen", short: "Wedloop, verdragen",
  html: `
<div class="step">
  <h3>Een wedloop begint</h3>
  <p>De Sovjet-Unie testte haar eerste atoombom in 1949, het Verenigd Koninkrijk in 1952, Frankrijk in 1960 en China in 1964. In 1952 testten de Verenigde Staten de eerste <b>thermonucleaire</b> bom of waterstofbom, waarin een splijtingsexplosie de fusie van waterstofisotopen in gang zet; de Sovjet-Unie volgde binnen enkele jaren. Deze wapens konden veel krachtiger zijn dan de bommen van 1945.</p>
</div>
<div class="step">
  <h3>Castle Bravo, 1954: de neerslag</h3>
  <p>Een Amerikaanse test op het atol Bikini in maart 1954 viel veel groter uit dan verwacht. De neerslag, een witte radioactieve as, kwam terecht op de bewoonde atollen Rongelap en Utrik en op de Japanse vissersboot Daigo Fukuryū Maru („Gelukkige Draak nr. 5”). De bemanning werd ziek en de marconist stierf die herfst. De verontwaardiging hielp de wereldwijde campagne tegen kernproeven op gang te brengen.</p>
  <div class="btns"><button class="btn ghost" data-act="wind">Wind opnieuw afspelen</button></div>
</div>
<div class="step">
  <h3>Zeventigduizend kernkoppen</h3>
  <p>Tussen 1945 en 2017 werden zo'n 2000 kernproeven gedaan, meer dan 500 daarvan in de open lucht. Het aantal kernkoppen in de wereld groeide vier decennia lang, tot zo'n 70.000 halverwege de jaren tachtig, en daalde na het einde van de Koude Oorlog met meer dan vier vijfde.</p>
  <div class="ctl"><label for="nwr-y">Jaar</label><input id="nwr-y" type="range" data-bind="yr" data-instant min="1945" max="2025" step="1" value="1986"><output data-show="yr" data-fmt="0"></output></div>
</div>
<div class="step">
  <h3>De verdragen</h3>
  <p>Het Gedeeltelijk Kernstopverdrag van 1963 dreef de proeven onder de grond. Het <b>Non-proliferatieverdrag</b> van 1968, waarbij nu bijna elk land is aangesloten, verbiedt de verspreiding van kernwapens en verplicht de kernwapenstaten tot ontwapening. Verdragen tussen de VS en de Sovjet-Unie, later Rusland, verkleinden de arsenalen, en het Alomvattend Kernstopverdrag van 1996, door het grootste deel van de wereld ondertekend maar nog niet in werking, verbiedt elke proefexplosie. Wijs een verdrag aan.</p>
</div>`,
};

WT.L.ch.nwverify = {
  num: "Les 1", title: "Proeven opsporen, materiaal bewaken", short: "Verificatie",
  html: `
<div class="step">
  <h3>Luisteren naar de aarde</h3>
  <p>Een verdrag is zo goed als de middelen om het te controleren. Het meetnet van het Alomvattend Kernstopverdrag is ontworpen om de hele aardbol te bestrijken: 170 seismische stations onder meer dan 300 installaties. Een ondergrondse explosie is plotseling en ondiep en duwt het gesteente naar buiten, zodat haar seismische registratie er anders uitziet dan het verschuiven langs een breuk bij een aardbeving.</p>
  <div class="btns" role="group" aria-label="Bron"><button class="btn ghost" data-act="vEx" aria-pressed="true">Explosie</button> <button class="btn ghost" data-act="vEq" aria-pressed="false">Aardbeving</button></div>
</div>
<div class="step">
  <h3>Geluid in lucht en water</h3>
  <p>Zestig <b>infrageluid</b>stations luisteren naar geluid dat te laag is voor het oor en duizenden kilometers door de atmosfeer reist. Elf <b>hydroakoestische</b> stations luisteren in de oceanen, waar een waterlaag het geluid over hele bekkens geleidt.</p>
</div>
<div class="step">
  <h3>Xenon: een klok in de lucht</h3>
  <p>Zelfs uit een goed afgesloten ondergrondse proef kan radioactief xenon ontsnappen, een edelgas dat met niets reageert. De isotopen vervallen met verschillende snelheden, dus hun verhoudingen vertellen hoe lang geleden de splijting plaatsvond en helpen een proef te onderscheiden van een reactor of een fabriek voor medische isotopen. Om die klok te lezen zijn kerngegevens nodig: splijtingsopbrengsten en halveringstijden.</p>
  <div class="ctl"><label for="nwv-d">Dagen sinds de splijting</label><input id="nwv-d" type="range" data-bind="days" data-instant min="0" max="60" step="0.5" value="5"><output data-show="days" data-fmt="1"></output></div>
</div>
<div class="step">
  <h3>Safeguards: het materiaal tellen</h3>
  <p>Onder het Non-proliferatieverdrag controleert het Internationaal Atoomenergieagentschap (IAEA) dat aangegeven nucleair materiaal voor vreedzaam gebruik blijft. Inspecteurs houden de boekhouding bij, verzegelen containers, kijken mee met camera's en nemen veegmonsters. Ze meten ook: de gammastraling van uranium-235 laat zien hoe sterk het uranium verrijkt is, en neutronentelling weegt plutonium. Beide metingen berusten op kerngegevens.</p>
</div>`,
};

WT.L.ch.nwdata = {
  num: "Les 1", title: "Reactoren, wapens en kerngegevens", short: "Reactor of wapen",
  html: `
<div class="step">
  <h3>Splijten en samensmelten</h3>
  <p>Kernenergie komt uit twee tegengestelde reacties. <b>Splijting</b> deelt een zware kern zoals uranium; <b>fusie</b> voegt lichte kernen zoals waterstof samen. Beide zetten een beetje massa om in veel energie, zoals de <a href="./#binding" data-keep-lang>bindingsenergiekromme</a> laat zien. Kernreactoren gebruiken splijting; de zon, en de <a href="#fusion">fusie</a>machines die nu worden gebouwd, gebruiken fusie.</p>
</div>
<div class="step">
  <h3>Waarom een reactor niet kan ontploffen als een bom</h3>
  <p>Een kerncentrale en een wapen gebruiken allebei splijting, maar verder lijkt bijna niets op elkaar. Reactorbrandstof is vooral uranium-238 met slechts een paar procent uranium-235. De kettingreactie wordt in evenwicht gehouden, in het tempo van het kleine deel neutronen dat later aankomt, en als de brandstof heter wordt, remt de natuurkunde zelf haar af. Reactorongevallen kunnen zeer ernstig zijn, door oververhitting, stoom of waterstof (zie <a href="#accidents">drie ongevallen</a>), maar een vermogensreactor kan geen kernexplosie worden.</p>
</div>
<div class="step">
  <h3>Verrijking doet ertoe</h3>
  <p>Natuurlijk uranium bevat 0,7 % uranium-235. Brandstof voor vermogensreactoren is verrijkt tot zo'n 3–5 %. Alles onder 20 % heet <b>laagverrijkt uranium</b> en geldt niet als bruikbaar voor wapens; vanaf 20 % is het hoogverrijkt en wordt het onder de strengste controles bewaakt. Sinds 1978 zijn veel onderzoeksreactoren wereldwijd omgebouwd van hoog- naar laagverrijkte brandstof.</p>
</div>
<div class="step">
  <h3>Kerngegevens voor veiligheid en verificatie</h3>
  <p>Overal waar splijtbaar materiaal wordt behandeld, in brandstoffabrieken, transportcontainers en opslagbassins, berekenen ingenieurs hoe dicht het bij een kettingreactie is en houden ze een ruime marge aan; die berekeningen berusten op geëvalueerde kerngegevens. Toen die marge werd genegeerd, zoals in 1999 in een brandstoffabriek in Tokaimura, Japan, kwamen werknemers om. Dezelfde gegevens, halveringstijden, splijtingsopbrengsten en werkzame doorsneden, laten inspecteurs materiaal meten en het meetnet een xenonmonster lezen.</p>
</div>`,
};

Object.assign(WT.L.labels, {
  // nwhist
  "fission: a heavy nucleus splits into two lighter ones": "splijting: een zware kern splitst in twee lichtere",
  "fission: one nucleus splits in two": "splijting: een kern splitst in tweeën",
  "two lighter nuclei": "twee lichtere kernen", "and a few free neutrons": "en een paar vrije neutronen",
  "after Meitner & Frisch {#} · illustration": "naar Meitner & Frisch {#} · illustratie",
  "first split": "eerste splijting", "generation {#}": "generatie {#}",
  "each split frees neutrons that can split more nuclei: a chain reaction": "elke splijting maakt neutronen vrij die meer kernen kunnen splijten: een kettingreactie",
  "each split frees neutrons that split more nuclei": "elke splijting maakt neutronen vrij voor nieuwe splijtingen",
  "the idea only · illustration": "alleen het idee · illustratie",
  "Oak Ridge, Tennessee": "Oak Ridge, Tennessee", "Hanford, Washington": "Hanford, Washington", "Los Alamos, New Mexico": "Los Alamos, New Mexico",
  "separating uranium{#}": "uranium{#} scheiden", "reactors making plutonium": "reactoren voor plutonium", "the laboratory": "het laboratorium",
  "three secret sites, {#}–{#}": "drie geheime locaties, {#}–{#}", "after US DOE / OSTI, The Manhattan Project": "naar US DOE / OSTI, The Manhattan Project",
  "fission found": "splijting ontdekt", "Einstein–Szilard letter": "brief van Einstein en Szilard", "Manhattan Project": "Manhattanproject",
  "first chain reaction": "eerste kettingreactie", "Trinity": "Trinity", "Hiroshima, Nagasaki": "Hiroshima, Nagasaki",
  "Dec {#} · fission discovered in Berlin": "dec. {#} · splijting ontdekt in Berlijn",
  "Aug {#} · the Einstein–Szilard letter": "aug. {#} · de brief van Einstein en Szilard",
  "{#} · the Manhattan Project begins": "{#} · het Manhattanproject begint",
  "Dec {#} · first controlled chain reaction, Chicago": "dec. {#} · eerste gecontroleerde kettingreactie, Chicago",
  "{#} July {#} · Trinity, New Mexico": "{#} juli {#} · Trinity, New Mexico",
  "{#} and {#} August {#} · Hiroshima and Nagasaki": "{#} en {#} augustus {#} · Hiroshima en Nagasaki",
  "seven years from a laboratory discovery to a weapon": "zeven jaar van een laboratoriumontdekking tot een wapen", "{#} to {#}": "{#} tot {#}",
  "sources: R. Rhodes, The Making of the Atomic Bomb ({#}); US DOE / OSTI history": "bronnen: R. Rhodes, The Making of the Atomic Bomb ({#}); geschiedenis US DOE / OSTI",
  "sources: Rhodes {#}; US DOE": "bronnen: Rhodes {#}; US DOE",
  // nwcities
  "Hiroshima": "Hiroshima", "Nagasaki": "Nagasaki",
  "one lantern for about {#} people who had died by the end of {#}": "één lantaarn voor ongeveer {#} mensen die eind {#} waren omgekomen",
  "one lantern ≈ {#} people who died by the end of {#}": "één lantaarn ≈ {#} doden tot eind {#}",
  "faint lanterns: the range between the low and the high estimate": "vage lantaarns: de marge tussen de lage en de hoge schatting",
  "faint lanterns: the range of estimates": "vage lantaarns: marge van schattingen",
  "estimates: Radiation Effects Research Foundation (RERF)": "schattingen: Radiation Effects Research Foundation (RERF)", "estimates: RERF": "schattingen: RERF",
  "blast": "drukgolf", "heat": "hitte", "prompt radiation": "directe straling", "fallout": "neerslag",
  "a pressure wave that flattens buildings": "een drukgolf die gebouwen platlegt",
  "a flash of light and heat that burns and starts fires": "een flits van licht en hitte die verbrandt en branden sticht",
  "gamma rays and neutrons in the first instant": "gammastraling en neutronen in het eerste ogenblik",
  "radioactive dust carried downwind, for days to weeks": "radioactief stof met de wind mee, dagen tot weken lang",
  "pick an effect": "kies een effect", "pick an effect to see what it does": "kies een effect om te zien wat het doet",
  "rings are qualitative, not to scale": "ringen kwalitatief, niet op schaal", "after public civil-defence literature": "naar openbare literatuur over bevolkingsbescherming",
  "about {#} survivors, followed since {#}": "ongeveer {#} overlevenden, gevolgd sinds {#}",
  "about {#} survivors and their families, followed since {#}": "ongeveer {#} overlevenden en hun families, gevolgd sinds {#}",
  "one dot = {#} people": "één stip = {#} mensen", "RERF Life Span Study": "RERF Life Span Study",
  "Radiation Effects Research Foundation, Life Span Study · Hiroshima Peace Memorial Museum": "Radiation Effects Research Foundation, Life Span Study · Vredesmuseum Hiroshima",
  // nwrace
  "Bikini Atoll (test site)": "atol Bikini (testgebied)", "Rongelap": "Rongelap", "Utrik": "Utrik",
  "fishing boat Lucky Dragon No. {#}": "vissersboot Gelukkige Draak nr. {#}", "Lucky Dragon No. {#}": "Gelukkige Draak nr. {#}", "wind": "wind",
  "schematic of the fallout, not to scale": "schema van de neerslag, niet op schaal", "schematic, not to scale": "schema, niet op schaal",
  "after US DOE Marshall Islands history; Hiroshima Peace Memorial Museum": "naar de Marshalleilanden-geschiedenis van het US DOE; Vredesmuseum Hiroshima",
  "after US DOE history": "naar US DOE-geschiedenis",
  "{#}: about {#} warheads": "{#}: ongeveer {#} kernkoppen",
  "nuclear warheads in the world": "kernkoppen in de wereld", "nuclear warheads in the world (approximate)": "kernkoppen in de wereld (bij benadering)",
  "peak, {#}": "piek, {#}", "peak, {#}: about {#}": "piek, {#}: ongeveer {#}",
  "approximate, after the Federation of American Scientists": "bij benadering, naar de Federation of American Scientists", "approx., after FAS": "ca., naar FAS",
  "point at a green dot to read a treaty": "wijs een groene stip aan om een verdrag te lezen", "tap a green dot: a treaty": "tik op een groene stip: een verdrag",
  "{#} · Partial Test Ban": "{#} · Gedeeltelijk Kernstopverdrag", "{#} · Non-Proliferation Treaty": "{#} · Non-proliferatieverdrag",
  "{#} · INF Treaty": "{#} · INF-verdrag", "{#} · START I": "{#} · START I", "{#} · Comprehensive Test Ban": "{#} · Alomvattend Kernstopverdrag", "{#} · New START": "{#} · New START",
  "no tests in the air, in space or under water": "geen proeven in de lucht, in de ruimte of onder water",
  "no spread of weapons; disarmament; peaceful use": "geen verspreiding; ontwapening; vreedzaam gebruik",
  "a whole class of missiles removed": "een hele klasse raketten afgeschaft", "the first deep cuts": "de eerste diepe reducties",
  "no test explosions at all (not yet in force)": "helemaal geen proefexplosies (nog niet in werking)", "limits on deployed warheads (expired {#})": "plafonds voor ingezette kernkoppen (verlopen {#})",
  // nwverify
  "explosion: shallow, pushes outward": "explosie: ondiep, duwt naar buiten", "earthquake: deeper, slip on a fault": "aardbeving: dieper, verschuiving langs een breuk",
  "explosion: sharp start, strong P waves": "explosie: scherp begin, sterke P-golven", "earthquake: weak start, strong S waves": "aardbeving: zwak begin, sterke S-golven",
  "seismometer": "seismometer", "P": "P", "S": "S",
  "qualitative shapes · CTBTO International Monitoring System": "kwalitatieve vormen · Internationaal Monitoringsysteem van de CTBTO",
  "CTBTO International Monitoring System": "Internationaal Monitoringsysteem van de CTBTO",
  "infrasound": "infrageluid", "hydroacoustic": "hydroakoestiek", "sound channelled in the ocean": "geluid geleid in de oceaan", "sound in the sea": "geluid in zee",
  "{#} infrasound and {#} hydroacoustic stations in the network": "{#} infrageluid- en {#} hydroakoestische stations in het net",
  "{#} infrasound · {#} hydroacoustic stations": "{#} infrageluid · {#} hydroakoestiek",
  "xenon{#}": "xenon{#}", "xenon{#}m": "xenon{#}m", "Xe{#}": "Xe{#}", "Xe{#}m": "Xe{#}m",
  "half-life {#} h": "halveringstijd {#} u", "half-life {#} d": "halveringstijd {#} d", "start": "begin",
  "{#} days after the fission": "{#} dagen na de splijting",
  "short-lived isotopes fade first, so the ratios read like a clock": "kortlevende isotopen verdwijnen eerst, dus de verhoudingen lezen als een klok",
  "the ratios change with time: a clock": "de verhoudingen veranderen met de tijd: een klok",
  "equal starting amounts, for illustration; real ratios come from fission yields": "gelijke beginhoeveelheden, ter illustratie; echte verhoudingen volgen uit splijtingsopbrengsten",
  "illustrative starting amounts": "illustratieve beginhoeveelheden", "half-lives: ENSDF / NUBASE{#}": "halveringstijden: ENSDF / NUBASE{#}",
  "seal": "zegel", "camera": "camera", "detector": "detector",
  "uranium{#} line, {#} keV": "lijn van uranium{#}, {#} keV", "U{#} line, {#} keV": "U{#}-lijn, {#} keV", "gamma-ray energy →": "gamma-energie →",
  "the height of the peak tells how enriched the uranium is": "de hoogte van de piek toont hoe sterk het uranium verrijkt is",
  "a bigger peak: more uranium{#}": "hogere piek: meer uranium{#}", "after IAEA safeguards; spectrum illustrative": "naar IAEA-safeguards; spectrum ter illustratie",
  // nwdata
  "fission: heavy splits": "splijting: zwaar splitst", "fusion: light nuclei join": "fusie: lichte kernen smelten samen",
  "both turn a little mass into energy": "beide zetten een beetje massa om in energie", "both release nuclear energy": "beide maken kernenergie vrij",
  "a power reactor: four reasons it cannot explode like a bomb": "een vermogensreactor: vier redenen waarom hij niet als een bom kan ontploffen", "a power reactor": "een vermogensreactor",
  "low-enriched fuel, mostly uranium{#}": "laagverrijkte brandstof, vooral uranium{#}", "chain held in balance, not growing": "keten in evenwicht, groeit niet",
  "late neutrons set a slow pace": "vertraagde neutronen bepalen een traag tempo", "hotter fuel → fewer fissions": "hetere brandstof → minder splijtingen",
  "after IAEA, US NRC, World Nuclear Association": "naar IAEA, US NRC, World Nuclear Association",
  "share of uranium{#}": "aandeel uranium{#}", "low-enriched uranium (LEU): below {#} %": "laagverrijkt uranium (LEU): onder {#} %", "LEU: below {#} %": "LEU: onder {#} %",
  "highly enriched (HEU)": "hoogverrijkt (HEU)", "HEU": "HEU", "natural uranium": "natuurlijk uranium", "power-reactor fuel": "brandstof voor vermogensreactoren", "reactor fuel": "reactorbrandstof",
  "about {#}–{#} %": "ongeveer {#}–{#} %", "definitions: IAEA Safeguards Glossary": "definities: IAEA Safeguards Glossary",
  "evaluated nuclear data": "geëvalueerde kerngegevens", "fuel plants": "brandstoffabrieken", "transport casks": "transportcontainers", "storage pools": "opslagbassins",
  "safeguards": "safeguards", "test monitoring": "proefbewaking",
  "the same data keep handling safe and let inspectors measure": "dezelfde gegevens houden de behandeling veilig en laten inspecteurs meten",
  "safety margins and measurements rest on the data": "veiligheidsmarges en metingen berusten op de gegevens", "Tokaimura {#}: IAEA fact-finding report": "Tokaimura {#}: onderzoeksrapport van de IAEA",
});
