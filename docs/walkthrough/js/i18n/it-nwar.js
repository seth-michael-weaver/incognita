/* Italian (Italiano): part seven, nuclear weapons: history and control (nwhist, nwcities, nwrace, nwverify, nwdata) */
Object.assign(WT.L.ui, { tp_p7_k: "Parte settima", tp_p7_h: "Armi nucleari: storia e controllo" });

WT.L.ch.nwhist = {
  num: "Lezione 1", title: "Dalla scoperta a Trinity", short: "Dalla scoperta a Trinity",
  html: `
<div class="step">
  <h3>La scissione dell'atomo, 1938</h3>
  <p>Nel dicembre 1938, a Berlino, Otto Hahn e Fritz Strassmann trovarono bario, un elemento molto più leggero, nell'uranio bombardato con neutroni. Lise Meitner, fuggita dalla Germania nazista quell'estate, e suo nipote Otto Frisch lo spiegarono in poche settimane: il nucleo di uranio si era spaccato in due. Frisch lo chiamò <b>fissione</b>.</p>
</div>
<div class="step">
  <h3>L'idea di una reazione a catena</h3>
  <p>Ogni scissione libera anche alcuni neutroni, che possono spaccare altri nuclei. Leo Szilard aveva immaginato una tale <b>reazione a catena</b> già nel 1933. Nell'agosto 1939 scrisse una lettera, firmata da Albert Einstein, che avvertiva il presidente Roosevelt che la Germania avrebbe potuto usarla per costruire una bomba. Nel dicembre 1942 la squadra di Enrico Fermi realizzò a Chicago la prima reazione a catena controllata, in una pila di uranio e grafite.</p>
</div>
<div class="step">
  <h3>Il Progetto Manhattan</h3>
  <p>Dal 1942 gli Stati Uniti, con il Regno Unito e il Canada, costruirono un'industria segreta che arrivò a impiegare circa 130.000 persone. Oak Ridge, nel Tennessee, separava il raro uranio-235 dall'uranio naturale; Hanford, nello Stato di Washington, faceva funzionare reattori che producevano plutonio; e il laboratorio di Los Alamos, nel Nuovo Messico, diretto da J. Robert Oppenheimer, lavorava alle armi.</p>
</div>
<div class="step">
  <h3>Trinity, 16 luglio 1945</h3>
  <p>La prima esplosione nucleare illuminò il deserto del Nuovo Messico prima dell'alba. Tre settimane dopo gli Stati Uniti usarono due bombe atomiche contro il Giappone, su Hiroshima e Nagasaki. La Germania si era arresa a maggio; il suo progetto bellico non si era mai avvicinato a un'arma.</p>
</div>`,
};

WT.L.ch.nwcities = {
  num: "Lezione 1", title: "Hiroshima e Nagasaki", short: "Hiroshima, Nagasaki",
  html: `
<div class="step">
  <h3>6 e 9 agosto 1945</h3>
  <p>Una bomba atomica distrusse il centro di Hiroshima il 6 agosto 1945, e una seconda colpì Nagasaki tre giorni dopo. Entro la fine di quell'anno erano morte tra 90.000 e 166.000 persone a Hiroshima e tra 60.000 e 80.000 a Nagasaki, per lo più civili. Il Giappone annunciò la resa il 15 agosto.</p>
</div>
<div class="step">
  <h3>Come colpisce un'esplosione nucleare</h3>
  <p>Le guide pubbliche di protezione civile descrivono quattro effetti: l'<b>onda d'urto</b>, un'ondata di pressione che abbatte gli edifici; il <b>calore</b>, un lampo che ustiona la pelle e appicca incendi; la <b>radiazione immediata</b>, raggi gamma e neutroni emessi nel primo istante; e la <b>ricaduta</b> radioattiva, polvere radioattiva portata via dal vento. Nel 1945 la maggior parte dei morti fu causata dall'onda d'urto, dalle ustioni e dagli incendi successivi.</p>
  <div class="btns" role="group" aria-label="Effetto"><button class="btn ghost" data-act="e0" aria-pressed="false">Onda d'urto</button> <button class="btn ghost" data-act="e1" aria-pressed="false">Calore</button> <button class="btn ghost" data-act="e2" aria-pressed="false">Radiazione immediata</button> <button class="btn ghost" data-act="e3" aria-pressed="false">Ricaduta</button></div>
</div>
<div class="step">
  <h3>I sopravvissuti</h3>
  <p>I sopravvissuti, gli <b>hibakusha</b>, raccontano la loro storia da decenni, e molti sono diventati voci per l'abolizione delle armi nucleari. Dal 1950 una fondazione congiunta giapponese e statunitense segue circa 120.000 di loro e le loro famiglie. Le loro cartelle cliniche sono la principale fonte di ciò che si sa sugli effetti a lungo termine delle radiazioni, compreso un maggior rischio di cancro, e sono alla base delle norme di radioprotezione di tutto il mondo.</p>
</div>`,
};

WT.L.ch.nwrace = {
  num: "Lezione 1", title: "La corsa agli armamenti e i trattati", short: "Corsa e trattati",
  html: `
<div class="step">
  <h3>Comincia una corsa</h3>
  <p>L'Unione Sovietica provò la sua prima bomba atomica nel 1949, il Regno Unito nel 1952, la Francia nel 1960 e la Cina nel 1964. Nel 1952 gli Stati Uniti provarono la prima bomba <b>termonucleare</b>, o all'idrogeno, in cui un'esplosione a fissione innesca la fusione di isotopi dell'idrogeno; l'Unione Sovietica seguì in pochi anni. Queste armi potevano essere molto più potenti delle bombe del 1945.</p>
</div>
<div class="step">
  <h3>Castle Bravo, 1954: la ricaduta</h3>
  <p>Un test statunitense all'atollo di Bikini nel marzo 1954 risultò molto più grande del previsto. La sua ricaduta, una cenere radioattiva bianca, cadde sugli atolli abitati di Rongelap e Utrik e sul peschereccio giapponese Daigo Fukuryū Maru («Drago fortunato n. 5»). L'equipaggio si ammalò e il suo radiotelegrafista morì quell'autunno. L'indignazione contribuì ad avviare la campagna mondiale per fermare i test.</p>
  <div class="btns"><button class="btn ghost" data-act="wind">Riproduci il vento</button></div>
</div>
<div class="step">
  <h3>Settantamila testate</h3>
  <p>Tra il 1945 e il 2017 furono eseguiti circa 2000 test nucleari, più di 500 dei quali all'aperto. Il numero di testate nel mondo crebbe per quattro decenni, fino a circa 70.000 a metà degli anni Ottanta, poi calò di oltre quattro quinti dopo la fine della guerra fredda.</p>
  <div class="ctl"><label for="nwr-y">Anno</label><input id="nwr-y" type="range" data-bind="yr" data-instant min="1945" max="2025" step="1" value="1986"><output data-show="yr" data-fmt="0"></output></div>
</div>
<div class="step">
  <h3>I trattati</h3>
  <p>Il Trattato sulla messa al bando parziale degli esperimenti nucleari del 1963 spostò i test sottoterra. Il <b>Trattato di non proliferazione nucleare</b> (TNP) del 1968, a cui oggi aderiscono quasi tutti i paesi, vieta la diffusione delle armi e impegna gli stati nucleari al disarmo. Trattati tra Stati Uniti e Unione Sovietica, poi Russia, ridussero gli arsenali, e il Trattato sulla messa al bando totale degli esperimenti nucleari (CTBT) del 1996, firmato dalla maggior parte del mondo ma non ancora in vigore, vieta ogni esplosione di prova. Indica un trattato.</p>
</div>`,
};

WT.L.ch.nwverify = {
  num: "Lezione 1", title: "Sorvegliare i test, custodire il materiale", short: "Verifica",
  html: `
<div class="step">
  <h3>Ascoltare la Terra</h3>
  <p>Un trattato vale quanto i mezzi per verificarlo. La rete di monitoraggio del CTBT è pensata per coprire il pianeta: 170 stazioni sismiche tra oltre 300 impianti. Un'esplosione sotterranea è improvvisa e poco profonda e spinge la roccia verso l'esterno, quindi la sua registrazione sismica appare diversa dallo scorrimento lungo una faglia in un terremoto.</p>
  <div class="btns" role="group" aria-label="Sorgente"><button class="btn ghost" data-act="vEx" aria-pressed="true">Esplosione</button> <button class="btn ghost" data-act="vEq" aria-pressed="false">Terremoto</button></div>
</div>
<div class="step">
  <h3>Suono nell'aria e nell'acqua</h3>
  <p>Sessanta stazioni a <b>infrasuoni</b> ascoltano suoni troppo gravi per l'orecchio, che viaggiano per migliaia di chilometri nell'atmosfera. Undici stazioni <b>idroacustiche</b> ascoltano negli oceani, dove uno strato d'acqua incanala il suono attraverso interi bacini.</p>
</div>
<div class="step">
  <h3>Lo xeno: un orologio nell'aria</h3>
  <p>Anche un test sotterraneo ben confinato può lasciar sfuggire xeno radioattivo, un gas nobile che non reagisce con nulla. I suoi isotopi decadono con ritmi diversi, perciò i loro rapporti dicono quanto tempo fa è avvenuta la fissione e aiutano a distinguere un test da un reattore o da un impianto di isotopi medici. Leggere quell'orologio richiede dati nucleari: rese di fissione ed emivite.</p>
  <div class="ctl"><label for="nwv-d">Giorni dalla fissione</label><input id="nwv-d" type="range" data-bind="days" data-instant min="0" max="60" step="0.5" value="5"><output data-show="days" data-fmt="1"></output></div>
</div>
<div class="step">
  <h3>Salvaguardie: contare il materiale</h3>
  <p>In base al Trattato di non proliferazione, l'Agenzia internazionale per l'energia atomica (AIEA) verifica che il materiale nucleare dichiarato resti a uso pacifico. Gli ispettori tengono la contabilità, sigillano i contenitori, sorvegliano con telecamere e prelevano campioni per strofinamento. Misurano anche: i raggi gamma dell'uranio-235 rivelano quanto è arricchito l'uranio, e il conteggio dei neutroni pesa il plutonio. Entrambe le misure si basano su dati nucleari.</p>
</div>`,
};

WT.L.ch.nwdata = {
  num: "Lezione 1", title: "Reattori, armi e dati nucleari", short: "Reattori e armi",
  html: `
<div class="step">
  <h3>Spaccare e unire</h3>
  <p>L'energia nucleare viene da due reazioni opposte. La <b>fissione</b> spacca un nucleo pesante come l'uranio; la <b>fusione</b> unisce nuclei leggeri come l'idrogeno. Entrambe trasformano un po' di massa in molta energia, come mostra la <a href="./#binding" data-keep-lang>curva dell'energia di legame</a>. I reattori di potenza usano la fissione; il Sole, e le macchine a <a href="#fusion">fusione</a> costruite oggi, usano la fusione.</p>
</div>
<div class="step">
  <h3>Perché un reattore non può esplodere come una bomba</h3>
  <p>Un reattore di potenza e un'arma usano entrambi la fissione, ma quasi nient'altro si somiglia. Il combustibile del reattore è soprattutto uranio-238 con solo una piccola percentuale di uranio-235. La reazione a catena è mantenuta in equilibrio, scandita dalla piccola quota di neutroni che arrivano in ritardo, e quando il combustibile si scalda è la fisica stessa a rallentarla. Gli incidenti ai reattori possono essere molto gravi, per surriscaldamento, vapore o idrogeno (vedi <a href="#accidents">tre incidenti</a>), ma un reattore di potenza non può diventare un'esplosione nucleare.</p>
</div>
<div class="step">
  <h3>L'arricchimento conta</h3>
  <p>L'uranio naturale contiene lo 0,7 % di uranio-235. Il combustibile dei reattori di potenza è arricchito al 3–5 % circa. Tutto ciò che sta sotto il 20 % si chiama <b>uranio a basso arricchimento</b> e non è considerato utilizzabile per armi; dal 20 % in su è altamente arricchito ed è custodito sotto i controlli più severi. Dal 1978 molti reattori di ricerca nel mondo sono passati da combustibile ad alto a basso arricchimento.</p>
</div>
<div class="step">
  <h3>Dati nucleari per la sicurezza e la verifica</h3>
  <p>Ovunque si maneggi materiale fissile, negli impianti di combustibile, nei contenitori di trasporto e nelle piscine di stoccaggio, gli ingegneri calcolano quanto sia vicino a una reazione a catena e mantengono un ampio margine; quei calcoli si basano su dati nucleari valutati. Quando quel margine fu ignorato, come in un impianto di combustibile a Tokaimura, in Giappone, nel 1999, morirono dei lavoratori. Gli stessi dati, emivite, rese di fissione e sezioni d'urto, permettono agli ispettori di misurare il materiale e alla rete di monitoraggio di leggere un campione di xeno.</p>
</div>`,
};

Object.assign(WT.L.labels, {
  // nwhist
  "fission: a heavy nucleus splits into two lighter ones": "fissione: un nucleo pesante si spacca in due più leggeri",
  "fission: one nucleus splits in two": "fissione: un nucleo si spacca in due",
  "two lighter nuclei": "due nuclei più leggeri", "and a few free neutrons": "e alcuni neutroni liberi",
  "after Meitner & Frisch {#} · illustration": "da Meitner e Frisch, {#} · illustrazione",
  "first split": "prima scissione", "generation {#}": "generazione {#}",
  "each split frees neutrons that can split more nuclei: a chain reaction": "ogni scissione libera neutroni che possono spaccare altri nuclei: una reazione a catena",
  "each split frees neutrons that split more nuclei": "ogni scissione libera neutroni che ne spaccano altri",
  "the idea only · illustration": "solo l'idea · illustrazione",
  "Oak Ridge, Tennessee": "Oak Ridge, Tennessee", "Hanford, Washington": "Hanford, Washington", "Los Alamos, New Mexico": "Los Alamos, Nuovo Messico",
  "separating uranium{#}": "separare l'uranio{#}", "reactors making plutonium": "reattori per il plutonio", "the laboratory": "il laboratorio",
  "three secret sites, {#}–{#}": "tre siti segreti, {#}–{#}", "after US DOE / OSTI, The Manhattan Project": "da US DOE / OSTI, The Manhattan Project",
  "fission found": "scoperta la fissione", "Einstein–Szilard letter": "lettera di Einstein e Szilard", "Manhattan Project": "Progetto Manhattan",
  "first chain reaction": "prima reazione a catena", "Trinity": "Trinity", "Hiroshima, Nagasaki": "Hiroshima, Nagasaki",
  "Dec {#} · fission discovered in Berlin": "dic. {#} · scoperta la fissione a Berlino",
  "Aug {#} · the Einstein–Szilard letter": "ago. {#} · la lettera di Einstein e Szilard",
  "{#} · the Manhattan Project begins": "{#} · inizia il Progetto Manhattan",
  "Dec {#} · first controlled chain reaction, Chicago": "dic. {#} · prima reazione a catena controllata, Chicago",
  "{#} July {#} · Trinity, New Mexico": "{#} luglio {#} · Trinity, Nuovo Messico",
  "{#} and {#} August {#} · Hiroshima and Nagasaki": "{#} e {#} agosto {#} · Hiroshima e Nagasaki",
  "seven years from a laboratory discovery to a weapon": "sette anni da una scoperta di laboratorio a un'arma", "{#} to {#}": "dal {#} al {#}",
  "sources: R. Rhodes, The Making of the Atomic Bomb ({#}); US DOE / OSTI history": "fonti: R. Rhodes, The Making of the Atomic Bomb ({#}); storia US DOE / OSTI",
  "sources: Rhodes {#}; US DOE": "fonti: Rhodes {#}; US DOE",
  // nwcities
  "Hiroshima": "Hiroshima", "Nagasaki": "Nagasaki",
  "one lantern for about {#} people who had died by the end of {#}": "una lanterna ogni {#} persone circa morte entro la fine del {#}",
  "one lantern ≈ {#} people who died by the end of {#}": "una lanterna ≈ {#} morti entro il {#}",
  "faint lanterns: the range between the low and the high estimate": "lanterne tenui: l'intervallo tra la stima bassa e quella alta",
  "faint lanterns: the range of estimates": "lanterne tenui: intervallo delle stime",
  "estimates: Radiation Effects Research Foundation (RERF)": "stime: Radiation Effects Research Foundation (RERF)", "estimates: RERF": "stime: RERF",
  "blast": "onda d'urto", "heat": "calore", "prompt radiation": "radiazione immediata", "fallout": "ricaduta",
  "a pressure wave that flattens buildings": "un'onda di pressione che abbatte gli edifici",
  "a flash of light and heat that burns and starts fires": "un lampo di luce e calore che ustiona e appicca incendi",
  "gamma rays and neutrons in the first instant": "raggi gamma e neutroni nel primo istante",
  "radioactive dust carried downwind, for days to weeks": "polvere radioattiva portata dal vento, per giorni o settimane",
  "pick an effect": "scegli un effetto", "pick an effect to see what it does": "scegli un effetto per vedere cosa fa",
  "rings are qualitative, not to scale": "anelli qualitativi, non in scala", "after public civil-defence literature": "dalla letteratura pubblica di protezione civile",
  "about {#} survivors, followed since {#}": "circa {#} sopravvissuti, seguiti dal {#}",
  "about {#} survivors and their families, followed since {#}": "circa {#} sopravvissuti e le loro famiglie, seguiti dal {#}",
  "one dot = {#} people": "un punto = {#} persone", "RERF Life Span Study": "Life Span Study della RERF",
  "Radiation Effects Research Foundation, Life Span Study · Hiroshima Peace Memorial Museum": "Radiation Effects Research Foundation, Life Span Study · Museo memoriale della pace di Hiroshima",
  // nwrace
  "Bikini Atoll (test site)": "atollo di Bikini (sito dei test)", "Rongelap": "Rongelap", "Utrik": "Utrik",
  "fishing boat Lucky Dragon No. {#}": "peschereccio Drago fortunato n. {#}", "Lucky Dragon No. {#}": "Drago fortunato n. {#}", "wind": "vento",
  "schematic of the fallout, not to scale": "schema della ricaduta, non in scala", "schematic, not to scale": "schema, non in scala",
  "after US DOE Marshall Islands history; Hiroshima Peace Memorial Museum": "dalla storia delle Isole Marshall del US DOE; Museo memoriale della pace di Hiroshima",
  "after US DOE history": "dalla storia del US DOE",
  "{#}: about {#} warheads": "{#}: circa {#} testate",
  "nuclear warheads in the world": "testate nucleari nel mondo", "nuclear warheads in the world (approximate)": "testate nucleari nel mondo (approssimato)",
  "peak, {#}": "massimo, {#}", "peak, {#}: about {#}": "massimo, {#}: circa {#}",
  "approximate, after the Federation of American Scientists": "approssimato, dalla Federation of American Scientists", "approx., after FAS": "approssim., dalla FAS",
  "point at a green dot to read a treaty": "punta un pallino verde per leggere un trattato", "tap a green dot: a treaty": "tocca un pallino verde: un trattato",
  "{#} · Partial Test Ban": "{#} · Bando parziale dei test", "{#} · Non-Proliferation Treaty": "{#} · Trattato di non proliferazione",
  "{#} · INF Treaty": "{#} · Trattato INF", "{#} · START I": "{#} · START I", "{#} · Comprehensive Test Ban": "{#} · Bando totale dei test (CTBT)", "{#} · New START": "{#} · New START",
  "no tests in the air, in space or under water": "niente test in atmosfera, nello spazio o sott'acqua",
  "no spread of weapons; disarmament; peaceful use": "non diffusione delle armi; disarmo; uso pacifico",
  "a whole class of missiles removed": "eliminata un'intera classe di missili", "the first deep cuts": "i primi tagli profondi",
  "no test explosions at all (not yet in force)": "nessuna esplosione di prova (non ancora in vigore)", "limits on deployed warheads (expired {#})": "limiti alle testate schierate (scaduto nel {#})",
  // nwverify
  "explosion: shallow, pushes outward": "esplosione: poco profonda, spinge verso l'esterno", "earthquake: deeper, slip on a fault": "terremoto: più profondo, scorrimento su una faglia",
  "explosion: sharp start, strong P waves": "esplosione: inizio netto, onde P forti", "earthquake: weak start, strong S waves": "terremoto: inizio debole, onde S forti",
  "seismometer": "sismometro", "P": "P", "S": "S",
  "qualitative shapes · CTBTO International Monitoring System": "forme qualitative · Sistema internazionale di monitoraggio della CTBTO",
  "CTBTO International Monitoring System": "Sistema internazionale di monitoraggio della CTBTO",
  "infrasound": "infrasuoni", "hydroacoustic": "idroacustica", "sound channelled in the ocean": "suono incanalato nell'oceano", "sound in the sea": "suono nel mare",
  "{#} infrasound and {#} hydroacoustic stations in the network": "{#} stazioni a infrasuoni e {#} idroacustiche nella rete",
  "{#} infrasound · {#} hydroacoustic stations": "{#} infrasuoni · {#} idroacustiche",
  "xenon{#}": "xeno{#}", "xenon{#}m": "xeno{#}m", "Xe{#}": "Xe{#}", "Xe{#}m": "Xe{#}m",
  "half-life {#} h": "emivita {#} h", "half-life {#} d": "emivita {#} d", "start": "inizio",
  "{#} days after the fission": "{#} giorni dopo la fissione",
  "short-lived isotopes fade first, so the ratios read like a clock": "gli isotopi a vita breve svaniscono prima, così i rapporti si leggono come un orologio",
  "the ratios change with time: a clock": "i rapporti cambiano nel tempo: un orologio",
  "equal starting amounts, for illustration; real ratios come from fission yields": "quantità iniziali uguali, per illustrazione; i rapporti reali vengono dalle rese di fissione",
  "illustrative starting amounts": "quantità iniziali illustrative", "half-lives: ENSDF / NUBASE{#}": "emivite: ENSDF / NUBASE{#}",
  "seal": "sigillo", "camera": "telecamera", "detector": "rivelatore",
  "uranium{#} line, {#} keV": "riga dell'uranio{#}, {#} keV", "U{#} line, {#} keV": "riga U{#}, {#} keV", "gamma-ray energy →": "energia gamma →",
  "the height of the peak tells how enriched the uranium is": "l'altezza del picco dice quanto è arricchito l'uranio",
  "a bigger peak: more uranium{#}": "picco più alto: più uranio{#}", "after IAEA safeguards; spectrum illustrative": "dalle salvaguardie AIEA; spettro illustrativo",
  // nwdata
  "fission: heavy splits": "fissione: il pesante si spacca", "fusion: light nuclei join": "fusione: nuclei leggeri si uniscono",
  "both turn a little mass into energy": "entrambe trasformano un po' di massa in energia", "both release nuclear energy": "entrambe liberano energia nucleare",
  "a power reactor: four reasons it cannot explode like a bomb": "un reattore di potenza: quattro motivi per cui non può esplodere come una bomba", "a power reactor": "un reattore di potenza",
  "low-enriched fuel, mostly uranium{#}": "combustibile a basso arricchimento, soprattutto uranio{#}", "chain held in balance, not growing": "catena in equilibrio, non cresce",
  "late neutrons set a slow pace": "i neutroni ritardati danno un ritmo lento", "hotter fuel → fewer fissions": "combustibile più caldo → meno fissioni",
  "after IAEA, US NRC, World Nuclear Association": "da AIEA, US NRC, World Nuclear Association",
  "share of uranium{#}": "quota di uranio{#}", "low-enriched uranium (LEU): below {#} %": "uranio a basso arricchimento (LEU): sotto il {#} %", "LEU: below {#} %": "LEU: sotto il {#} %",
  "highly enriched (HEU)": "altamente arricchito (HEU)", "HEU": "HEU", "natural uranium": "uranio naturale", "power-reactor fuel": "combustibile per reattori di potenza", "reactor fuel": "combustibile per reattori",
  "about {#}–{#} %": "circa {#}–{#} %", "definitions: IAEA Safeguards Glossary": "definizioni: IAEA Safeguards Glossary",
  "evaluated nuclear data": "dati nucleari valutati", "fuel plants": "impianti di combustibile", "transport casks": "contenitori di trasporto", "storage pools": "piscine di stoccaggio",
  "safeguards": "salvaguardie", "test monitoring": "monitoraggio dei test",
  "the same data keep handling safe and let inspectors measure": "gli stessi dati rendono sicura la manipolazione e permettono agli ispettori di misurare",
  "safety margins and measurements rest on the data": "margini di sicurezza e misure si basano sui dati", "Tokaimura {#}: IAEA fact-finding report": "Tokaimura {#}: rapporto d'indagine dell'AIEA",
});
