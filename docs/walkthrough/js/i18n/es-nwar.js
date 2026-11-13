/* Spanish: part seven, nuclear weapons: history and control (nwhist, nwcities, nwrace, nwverify, nwdata) */
Object.assign(WT.L.ui, { tp_p7_k: "Séptima parte", tp_p7_h: "Armas nucleares: historia y control" });

WT.L.ch.nwhist = {
  num: "Lección 1", title: "Del descubrimiento a Trinity", short: "Del descubrimiento a Trinity",
  html: `
<div class="step">
  <h3>La división del átomo, 1938</h3>
  <p>En diciembre de 1938, en Berlín, Otto Hahn y Fritz Strassmann encontraron bario, un elemento mucho más ligero, en uranio bombardeado con neutrones. Lise Meitner, que había huido de la Alemania nazi ese verano, y su sobrino Otto Frisch lo explicaron en pocas semanas: el núcleo de uranio se había partido en dos. Frisch lo llamó <b>fisión</b>.</p>
</div>
<div class="step">
  <h3>La idea de una reacción en cadena</h3>
  <p>Cada división libera además unos pocos neutrones, que pueden partir otros núcleos. Leo Szilard había imaginado esa <b>reacción en cadena</b> en 1933. En agosto de 1939 redactó una carta, firmada por Albert Einstein, que advertía al presidente Roosevelt de que Alemania podría usarla para construir una bomba. En diciembre de 1942 el equipo de Enrico Fermi logró la primera reacción en cadena controlada, una pila de uranio y grafito en Chicago.</p>
</div>
<div class="step">
  <h3>El Proyecto Manhattan</h3>
  <p>Desde 1942 Estados Unidos, con el Reino Unido y Canadá, levantó una industria secreta que llegó a emplear a unas 130 000 personas. Oak Ridge, en Tennessee, separaba el escaso uranio-235 del uranio natural; Hanford, en Washington, tenía reactores que producían plutonio; y el laboratorio de Los Álamos, en Nuevo México, dirigido por J. Robert Oppenheimer, trabajaba en las armas.</p>
</div>
<div class="step">
  <h3>Trinity, 16 de julio de 1945</h3>
  <p>La primera explosión nuclear iluminó el desierto de Nuevo México antes del amanecer. Tres semanas después Estados Unidos lanzó dos bombas atómicas sobre Japón, sobre Hiroshima y Nagasaki. Alemania se había rendido en mayo; su propio proyecto de guerra nunca estuvo cerca de un arma.</p>
</div>`,
};

WT.L.ch.nwcities = {
  num: "Lección 1", title: "Hiroshima y Nagasaki", short: "Hiroshima, Nagasaki",
  html: `
<div class="step">
  <h3>6 y 9 de agosto de 1945</h3>
  <p>Una bomba atómica destruyó el centro de Hiroshima el 6 de agosto de 1945, y una segunda cayó sobre Nagasaki tres días después. A finales de ese año habían muerto entre 90 000 y 166 000 personas en Hiroshima y entre 60 000 y 80 000 en Nagasaki, la mayoría civiles. Japón anunció su rendición el 15 de agosto.</p>
</div>
<div class="step">
  <h3>Cómo daña una explosión nuclear</h3>
  <p>Las guías públicas de protección civil describen cuatro efectos: la <b>onda expansiva</b>, una ola de presión que derriba edificios; el <b>calor</b>, un destello que quema la piel y provoca incendios; la <b>radiación inmediata</b>, rayos gamma y neutrones emitidos en el primer instante; y la <b>lluvia radiactiva</b>, polvo radiactivo que el viento arrastra. En 1945 la mayoría de las muertes se debieron a la onda expansiva, las quemaduras y los incendios posteriores.</p>
  <div class="btns" role="group" aria-label="Efecto"><button class="btn ghost" data-act="e0" aria-pressed="false">Onda expansiva</button> <button class="btn ghost" data-act="e1" aria-pressed="false">Calor</button> <button class="btn ghost" data-act="e2" aria-pressed="false">Radiación inmediata</button> <button class="btn ghost" data-act="e3" aria-pressed="false">Lluvia radiactiva</button></div>
</div>
<div class="step">
  <h3>Los supervivientes</h3>
  <p>Los supervivientes, los <b>hibakusha</b>, llevan décadas contando su historia, y muchos se convirtieron en voces por la abolición de las armas nucleares. Desde 1950 una fundación conjunta japonesa y estadounidense ha seguido a unos 120 000 de ellos y a sus familias. Sus historiales médicos son la principal fuente de lo que se sabe sobre los efectos de la radiación a largo plazo, incluido un mayor riesgo de cáncer, y sustentan las normas de protección radiológica de todo el mundo.</p>
</div>`,
};

WT.L.ch.nwrace = {
  num: "Lección 1", title: "La carrera de armamentos y los tratados", short: "Carrera y tratados",
  html: `
<div class="step">
  <h3>Empieza una carrera</h3>
  <p>La Unión Soviética probó su primera bomba atómica en 1949, el Reino Unido en 1952, Francia en 1960 y China en 1964. En 1952 Estados Unidos probó la primera bomba <b>termonuclear</b> o de hidrógeno, en la que una explosión de fisión desencadena la fusión de isótopos de hidrógeno; la Unión Soviética la siguió en pocos años. Estas armas podían ser mucho más potentes que las bombas de 1945.</p>
</div>
<div class="step">
  <h3>Castle Bravo, 1954: la lluvia radiactiva</h3>
  <p>Una prueba estadounidense en el atolón de Bikini en marzo de 1954 resultó mucho mayor de lo previsto. Su lluvia radiactiva, una ceniza blanca, cayó sobre los atolones habitados de Rongelap y Utrik y sobre el pesquero japonés Dragón Afortunado n.º 5. La tripulación enfermó y su radiotelegrafista murió ese otoño. La indignación ayudó a iniciar la campaña mundial para detener las pruebas.</p>
  <div class="btns"><button class="btn ghost" data-act="wind">Repetir el viento</button></div>
</div>
<div class="step">
  <h3>Setenta mil cabezas nucleares</h3>
  <p>Entre 1945 y 2017 se hicieron unas 2000 pruebas nucleares, más de 500 de ellas al aire libre. El número de cabezas nucleares en el mundo creció durante cuatro décadas, hasta unas 70 000 a mediados de los años ochenta, y luego cayó en más de cuatro quintas partes tras el fin de la Guerra Fría.</p>
  <div class="ctl"><label for="nwr-y">Año</label><input id="nwr-y" type="range" data-bind="yr" data-instant min="1945" max="2025" step="1" value="1986"><output data-show="yr" data-fmt="0"></output></div>
</div>
<div class="step">
  <h3>Los tratados</h3>
  <p>El Tratado de Prohibición Parcial de 1963 llevó las pruebas bajo tierra. El <b>Tratado de No Proliferación</b> de 1968, al que hoy pertenecen casi todos los países, prohíbe la difusión de las armas y obliga a los estados nucleares a desarmarse. Los tratados entre Estados Unidos y la Unión Soviética, y luego Rusia, redujeron los arsenales, y el Tratado de Prohibición Completa de 1996, firmado por la mayor parte del mundo pero aún no en vigor, prohíbe toda explosión de prueba. Señala un tratado.</p>
</div>`,
};

WT.L.ch.nwverify = {
  num: "Lección 1", title: "Vigilar las pruebas, custodiar el material", short: "Verificación",
  html: `
<div class="step">
  <h3>Escuchar a la Tierra</h3>
  <p>Un tratado vale lo que valgan los medios para verificarlo. La red de vigilancia de la Prohibición Completa está pensada para cubrir el planeta: 170 estaciones sísmicas entre más de 300 instalaciones. Una explosión subterránea es repentina y poco profunda y empuja la roca hacia fuera, así que su registro sísmico es distinto del deslizamiento de una falla en un terremoto.</p>
  <div class="btns" role="group" aria-label="Fuente"><button class="btn ghost" data-act="vEx" aria-pressed="true">Explosión</button> <button class="btn ghost" data-act="vEq" aria-pressed="false">Terremoto</button></div>
</div>
<div class="step">
  <h3>Sonido en el aire y en el agua</h3>
  <p>Sesenta estaciones de <b>infrasonido</b> escuchan sonidos demasiado graves para el oído, que viajan miles de kilómetros por la atmósfera. Once estaciones <b>hidroacústicas</b> escuchan en los océanos, donde una capa de agua canaliza el sonido a través de cuencas enteras.</p>
</div>
<div class="step">
  <h3>El xenón: un reloj en el aire</h3>
  <p>Incluso una prueba subterránea bien contenida puede dejar escapar xenón radiactivo, un gas noble que no reacciona con nada. Sus isótopos se desintegran a ritmos distintos, así que sus proporciones indican cuánto hace que ocurrió la fisión y ayudan a distinguir una prueba de un reactor o de una planta de isótopos médicos. Leer ese reloj requiere datos nucleares: rendimientos de fisión y periodos de semidesintegración.</p>
  <div class="ctl"><label for="nwv-d">Días desde la fisión</label><input id="nwv-d" type="range" data-bind="days" data-instant min="0" max="60" step="0.5" value="5"><output data-show="days" data-fmt="1"></output></div>
</div>
<div class="step">
  <h3>Salvaguardias: contar el material</h3>
  <p>En virtud del Tratado de No Proliferación, el Organismo Internacional de Energía Atómica comprueba que el material nuclear declarado sigue en uso pacífico. Los inspectores llevan la contabilidad, precintan contenedores, vigilan con cámaras y toman muestras por frotis. También miden: los rayos gamma del uranio-235 revelan lo enriquecido que está el uranio, y el conteo de neutrones pesa el plutonio. Ambas medidas se basan en datos nucleares.</p>
</div>`,
};

WT.L.ch.nwdata = {
  num: "Lección 1", title: "Reactores, armas y datos nucleares", short: "Reactores frente a armas",
  html: `
<div class="step">
  <h3>Partir y unir</h3>
  <p>La energía nuclear procede de dos reacciones opuestas. La <b>fisión</b> parte un núcleo pesado como el uranio; la <b>fusión</b> une núcleos ligeros como el hidrógeno. Ambas convierten un poco de masa en mucha energía, como muestra la <a href="./#binding" data-keep-lang>curva de energía de enlace</a>. Los reactores de potencia usan la fisión; el Sol, y las máquinas de <a href="#fusion">fusión</a> que se construyen hoy, usan la fusión.</p>
</div>
<div class="step">
  <h3>Por qué un reactor no puede estallar como una bomba</h3>
  <p>Un reactor de potencia y un arma usan la fisión, pero casi nada más se parece. El combustible del reactor es sobre todo uranio-238 con solo un pequeño porcentaje de uranio-235. La reacción en cadena se mantiene en equilibrio, marcada por la pequeña fracción de neutrones que llegan con retraso, y cuando el combustible se calienta la propia física la frena. Los accidentes de reactor pueden ser muy graves, por sobrecalentamiento, vapor o hidrógeno (ver <a href="#accidents">tres accidentes</a>), pero un reactor de potencia no puede convertirse en una explosión nuclear.</p>
</div>
<div class="step">
  <h3>El enriquecimiento importa</h3>
  <p>El uranio natural tiene un 0,7 % de uranio-235. El combustible de los reactores de potencia se enriquece hasta un 3–5 %. Todo lo que está por debajo del 20 % se llama <b>uranio poco enriquecido</b> y no se considera utilizable para armas; a partir del 20 % es muy enriquecido y se custodia bajo los controles más estrictos. Desde 1978 muchos reactores de investigación de todo el mundo han pasado de combustible muy enriquecido a poco enriquecido.</p>
</div>
<div class="step">
  <h3>Datos nucleares para la seguridad y la verificación</h3>
  <p>Allí donde se maneja material fisible, en plantas de combustible, contenedores de transporte y piscinas de almacenamiento, los ingenieros calculan lo cerca que está de una reacción en cadena y mantienen un amplio margen; esos cálculos se basan en datos nucleares evaluados. Cuando se ignoró ese margen, como en una planta de combustible de Tokaimura, Japón, en 1999, murieron trabajadores. Los mismos datos, periodos de semidesintegración, rendimientos de fisión y secciones eficaces, permiten a los inspectores medir el material y a la red de vigilancia leer una muestra de xenón.</p>
</div>`,
};

Object.assign(WT.L.labels, {
  // nwhist
  "fission: a heavy nucleus splits into two lighter ones": "fisión: un núcleo pesado se parte en dos más ligeros",
  "fission: one nucleus splits in two": "fisión: un núcleo se parte en dos",
  "two lighter nuclei": "dos núcleos más ligeros", "and a few free neutrons": "y unos pocos neutrones libres",
  "after Meitner & Frisch {#} · illustration": "según Meitner y Frisch, {#} · ilustración",
  "first split": "primera división", "generation {#}": "generación {#}",
  "each split frees neutrons that can split more nuclei: a chain reaction": "cada división libera neutrones que pueden partir más núcleos: una reacción en cadena",
  "each split frees neutrons that split more nuclei": "cada división libera neutrones que parten más núcleos",
  "the idea only · illustration": "solo la idea · ilustración",
  "Oak Ridge, Tennessee": "Oak Ridge, Tennessee", "Hanford, Washington": "Hanford, Washington", "Los Alamos, New Mexico": "Los Álamos, Nuevo México",
  "separating uranium{#}": "separar el uranio{#}", "reactors making plutonium": "reactores que producen plutonio", "the laboratory": "el laboratorio",
  "three secret sites, {#}–{#}": "tres emplazamientos secretos, {#}–{#}", "after US DOE / OSTI, The Manhattan Project": "según US DOE / OSTI, The Manhattan Project",
  "fission found": "se descubre la fisión", "Einstein–Szilard letter": "carta de Einstein y Szilard", "Manhattan Project": "Proyecto Manhattan",
  "first chain reaction": "primera reacción en cadena", "Trinity": "Trinity", "Hiroshima, Nagasaki": "Hiroshima, Nagasaki",
  "Dec {#} · fission discovered in Berlin": "dic. {#} · se descubre la fisión en Berlín",
  "Aug {#} · the Einstein–Szilard letter": "ago. {#} · la carta de Einstein y Szilard",
  "{#} · the Manhattan Project begins": "{#} · empieza el Proyecto Manhattan",
  "Dec {#} · first controlled chain reaction, Chicago": "dic. {#} · primera reacción en cadena controlada, Chicago",
  "{#} July {#} · Trinity, New Mexico": "{#} de julio de {#} · Trinity, Nuevo México",
  "{#} and {#} August {#} · Hiroshima and Nagasaki": "{#} y {#} de agosto de {#} · Hiroshima y Nagasaki",
  "seven years from a laboratory discovery to a weapon": "siete años de un descubrimiento de laboratorio a un arma", "{#} to {#}": "de {#} a {#}",
  "sources: R. Rhodes, The Making of the Atomic Bomb ({#}); US DOE / OSTI history": "fuentes: R. Rhodes, The Making of the Atomic Bomb ({#}); historia de US DOE / OSTI",
  "sources: Rhodes {#}; US DOE": "fuentes: Rhodes {#}; US DOE",
  // nwcities
  "Hiroshima": "Hiroshima", "Nagasaki": "Nagasaki",
  "one lantern for about {#} people who had died by the end of {#}": "un farol por cada {#} personas aproximadamente muertas a finales de {#}",
  "one lantern ≈ {#} people who died by the end of {#}": "un farol ≈ {#} muertos a finales de {#}",
  "faint lanterns: the range between the low and the high estimate": "faroles tenues: el intervalo entre la estimación baja y la alta",
  "faint lanterns: the range of estimates": "faroles tenues: el intervalo de estimaciones",
  "estimates: Radiation Effects Research Foundation (RERF)": "estimaciones: Radiation Effects Research Foundation (RERF)", "estimates: RERF": "estimaciones: RERF",
  "blast": "onda expansiva", "heat": "calor", "prompt radiation": "radiación inmediata", "fallout": "lluvia radiactiva",
  "a pressure wave that flattens buildings": "una ola de presión que derriba edificios",
  "a flash of light and heat that burns and starts fires": "un destello de luz y calor que quema y provoca incendios",
  "gamma rays and neutrons in the first instant": "rayos gamma y neutrones en el primer instante",
  "radioactive dust carried downwind, for days to weeks": "polvo radiactivo arrastrado por el viento, durante días o semanas",
  "pick an effect": "elige un efecto", "pick an effect to see what it does": "elige un efecto para ver qué hace",
  "rings are qualitative, not to scale": "anillos cualitativos, no a escala", "after public civil-defence literature": "según la literatura pública de protección civil",
  "about {#} survivors, followed since {#}": "unos {#} supervivientes, seguidos desde {#}",
  "about {#} survivors and their families, followed since {#}": "unos {#} supervivientes y sus familias, seguidos desde {#}",
  "one dot = {#} people": "un punto = {#} personas", "RERF Life Span Study": "Life Span Study de la RERF",
  "Radiation Effects Research Foundation, Life Span Study · Hiroshima Peace Memorial Museum": "Radiation Effects Research Foundation, Life Span Study · Museo Memorial de la Paz de Hiroshima",
  // nwrace
  "Bikini Atoll (test site)": "atolón de Bikini (zona de pruebas)", "Rongelap": "Rongelap", "Utrik": "Utrik",
  "fishing boat Lucky Dragon No. {#}": "pesquero Dragón Afortunado n.º {#}", "Lucky Dragon No. {#}": "Dragón Afortunado n.º {#}", "wind": "viento",
  "schematic of the fallout, not to scale": "esquema de la lluvia radiactiva, no a escala", "schematic, not to scale": "esquema, no a escala",
  "after US DOE Marshall Islands history; Hiroshima Peace Memorial Museum": "según la historia de las Islas Marshall del US DOE; Museo Memorial de la Paz de Hiroshima",
  "after US DOE history": "según la historia del US DOE",
  "{#}: about {#} warheads": "{#}: unas {#} cabezas nucleares",
  "nuclear warheads in the world": "cabezas nucleares en el mundo", "nuclear warheads in the world (approximate)": "cabezas nucleares en el mundo (aproximado)",
  "peak, {#}": "máximo, {#}", "peak, {#}: about {#}": "máximo, {#}: unas {#}",
  "approximate, after the Federation of American Scientists": "aproximado, según la Federation of American Scientists", "approx., after FAS": "aprox., según la FAS",
  "point at a green dot to read a treaty": "señala un punto verde para leer un tratado", "tap a green dot: a treaty": "toca un punto verde: un tratado",
  "{#} · Partial Test Ban": "{#} · Prohibición Parcial de Pruebas", "{#} · Non-Proliferation Treaty": "{#} · Tratado de No Proliferación",
  "{#} · INF Treaty": "{#} · Tratado INF", "{#} · START I": "{#} · START I", "{#} · Comprehensive Test Ban": "{#} · Prohibición Completa de Pruebas", "{#} · New START": "{#} · Nuevo START",
  "no tests in the air, in space or under water": "sin pruebas en el aire, en el espacio ni bajo el agua",
  "no spread of weapons; disarmament; peaceful use": "no difundir armas; desarme; uso pacífico",
  "a whole class of missiles removed": "se elimina toda una clase de misiles", "the first deep cuts": "los primeros grandes recortes",
  "no test explosions at all (not yet in force)": "ninguna explosión de prueba (aún no en vigor)", "limits on deployed warheads (expired {#})": "límites a las cabezas desplegadas (expiró en {#})",
  // nwverify
  "explosion: shallow, pushes outward": "explosión: poco profunda, empuja hacia fuera", "earthquake: deeper, slip on a fault": "terremoto: más profundo, deslizamiento de una falla",
  "explosion: sharp start, strong P waves": "explosión: inicio brusco, ondas P fuertes", "earthquake: weak start, strong S waves": "terremoto: inicio débil, ondas S fuertes",
  "seismometer": "sismómetro", "P": "P", "S": "S",
  "qualitative shapes · CTBTO International Monitoring System": "formas cualitativas · Sistema Internacional de Vigilancia de la OTPCE",
  "CTBTO International Monitoring System": "Sistema Internacional de Vigilancia de la OTPCE",
  "infrasound": "infrasonido", "hydroacoustic": "hidroacústica", "sound channelled in the ocean": "sonido canalizado en el océano", "sound in the sea": "sonido en el mar",
  "{#} infrasound and {#} hydroacoustic stations in the network": "{#} estaciones de infrasonido y {#} hidroacústicas en la red",
  "{#} infrasound · {#} hydroacoustic stations": "{#} de infrasonido · {#} hidroacústicas",
  "xenon{#}": "xenón{#}", "xenon{#}m": "xenón{#}m", "Xe{#}": "Xe{#}", "Xe{#}m": "Xe{#}m",
  "half-life {#} h": "semivida {#} h", "half-life {#} d": "semivida {#} d", "start": "inicio",
  "{#} days after the fission": "{#} días después de la fisión",
  "short-lived isotopes fade first, so the ratios read like a clock": "los isótopos de vida corta se apagan antes, así que las proporciones se leen como un reloj",
  "the ratios change with time: a clock": "las proporciones cambian con el tiempo: un reloj",
  "equal starting amounts, for illustration; real ratios come from fission yields": "cantidades iniciales iguales, como ilustración; las proporciones reales salen de los rendimientos de fisión",
  "illustrative starting amounts": "cantidades iniciales ilustrativas", "half-lives: ENSDF / NUBASE{#}": "periodos: ENSDF / NUBASE{#}",
  "seal": "precinto", "camera": "cámara", "detector": "detector",
  "uranium{#} line, {#} keV": "línea del uranio{#}, {#} keV", "U{#} line, {#} keV": "línea del U{#}, {#} keV", "gamma-ray energy →": "energía gamma →",
  "the height of the peak tells how enriched the uranium is": "la altura del pico indica lo enriquecido que está el uranio",
  "a bigger peak: more uranium{#}": "un pico mayor: más uranio{#}", "after IAEA safeguards; spectrum illustrative": "según las salvaguardias del OIEA; espectro ilustrativo",
  // nwdata
  "fission: heavy splits": "fisión: lo pesado se parte", "fusion: light nuclei join": "fusión: los núcleos ligeros se unen",
  "both turn a little mass into energy": "ambas convierten un poco de masa en energía", "both release nuclear energy": "ambas liberan energía nuclear",
  "a power reactor: four reasons it cannot explode like a bomb": "un reactor de potencia: cuatro razones por las que no puede estallar como una bomba", "a power reactor": "un reactor de potencia",
  "low-enriched fuel, mostly uranium{#}": "combustible poco enriquecido, sobre todo uranio{#}", "chain held in balance, not growing": "cadena en equilibrio, sin crecer",
  "late neutrons set a slow pace": "los neutrones retardados marcan un ritmo lento", "hotter fuel → fewer fissions": "combustible más caliente → menos fisiones",
  "after IAEA, US NRC, World Nuclear Association": "según OIEA, US NRC, World Nuclear Association",
  "share of uranium{#}": "proporción de uranio{#}", "low-enriched uranium (LEU): below {#} %": "uranio poco enriquecido (LEU): menos del {#} %", "LEU: below {#} %": "LEU: menos del {#} %",
  "highly enriched (HEU)": "muy enriquecido (HEU)", "HEU": "HEU", "natural uranium": "uranio natural", "power-reactor fuel": "combustible de reactor de potencia", "reactor fuel": "combustible de reactor",
  "about {#}–{#} %": "aprox. {#}–{#} %", "definitions: IAEA Safeguards Glossary": "definiciones: Glosario de Salvaguardias del OIEA",
  "evaluated nuclear data": "datos nucleares evaluados", "fuel plants": "plantas de combustible", "transport casks": "contenedores de transporte", "storage pools": "piscinas de almacenamiento",
  "safeguards": "salvaguardias", "test monitoring": "vigilancia de pruebas",
  "the same data keep handling safe and let inspectors measure": "los mismos datos hacen segura la manipulación y permiten medir a los inspectores",
  "safety margins and measurements rest on the data": "márgenes de seguridad y medidas se basan en los datos", "Tokaimura {#}: IAEA fact-finding report": "Tokaimura {#}: informe de investigación del OIEA",
});
