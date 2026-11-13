/* Portuguese (Português): part seven, nuclear weapons: history and control (nwhist, nwcities, nwrace, nwverify, nwdata) */
Object.assign(WT.L.ui, { tp_p7_k: "Sétima parte", tp_p7_h: "Armas nucleares: história e controle" });

WT.L.ch.nwhist = {
  num: "Lição 1", title: "Da descoberta a Trinity", short: "Da descoberta a Trinity",
  html: `
<div class="step">
  <h3>A divisão do átomo, 1938</h3>
  <p>Em dezembro de 1938, em Berlim, Otto Hahn e Fritz Strassmann encontraram bário, um elemento muito mais leve, em urânio bombardeado com nêutrons. Lise Meitner, que havia fugido da Alemanha nazista naquele verão, e seu sobrinho Otto Frisch explicaram o resultado em poucas semanas: o núcleo de urânio tinha se partido em dois. Frisch chamou isso de <b>fissão</b>.</p>
</div>
<div class="step">
  <h3>A ideia de uma reação em cadeia</h3>
  <p>Cada divisão libera também alguns nêutrons, que podem partir outros núcleos. Leo Szilard havia imaginado essa <b>reação em cadeia</b> em 1933. Em agosto de 1939 ele redigiu uma carta, assinada por Albert Einstein, que alertava o presidente Roosevelt de que a Alemanha poderia usá-la para construir uma bomba. Em dezembro de 1942 a equipe de Enrico Fermi realizou em Chicago a primeira reação em cadeia controlada, numa pilha de urânio e grafite.</p>
</div>
<div class="step">
  <h3>O Projeto Manhattan</h3>
  <p>A partir de 1942 os Estados Unidos, com o Reino Unido e o Canadá, ergueram uma indústria secreta que chegou a empregar cerca de 130 mil pessoas. Oak Ridge, no Tennessee, separava o raro urânio-235 do urânio natural; Hanford, no estado de Washington, operava reatores que produziam plutônio; e o laboratório de Los Alamos, no Novo México, dirigido por J. Robert Oppenheimer, trabalhava nas armas.</p>
</div>
<div class="step">
  <h3>Trinity, 16 de julho de 1945</h3>
  <p>A primeira explosão nuclear iluminou o deserto do Novo México antes do amanhecer. Três semanas depois os Estados Unidos lançaram duas bombas atômicas sobre o Japão, sobre Hiroshima e Nagasaki. A Alemanha havia se rendido em maio; seu próprio projeto de guerra nunca chegou perto de uma arma.</p>
</div>`,
};

WT.L.ch.nwcities = {
  num: "Lição 1", title: "Hiroshima e Nagasaki", short: "Hiroshima, Nagasaki",
  html: `
<div class="step">
  <h3>6 e 9 de agosto de 1945</h3>
  <p>Uma bomba atômica destruiu o centro de Hiroshima em 6 de agosto de 1945, e uma segunda atingiu Nagasaki três dias depois. Até o fim daquele ano haviam morrido entre 90 mil e 166 mil pessoas em Hiroshima e entre 60 mil e 80 mil em Nagasaki, a maioria civis. O Japão anunciou sua rendição em 15 de agosto.</p>
</div>
<div class="step">
  <h3>Como uma explosão nuclear causa dano</h3>
  <p>Os guias públicos de defesa civil descrevem quatro efeitos: a <b>onda de choque</b>, uma onda de pressão que derruba prédios; o <b>calor</b>, um clarão que queima a pele e provoca incêndios; a <b>radiação imediata</b>, raios gama e nêutrons emitidos no primeiro instante; e a <b>precipitação radioativa</b>, poeira radioativa levada pelo vento. Em 1945 a maioria das mortes veio da onda de choque, das queimaduras e dos incêndios que se seguiram.</p>
  <div class="btns" role="group" aria-label="Efeito"><button class="btn ghost" data-act="e0" aria-pressed="false">Onda de choque</button> <button class="btn ghost" data-act="e1" aria-pressed="false">Calor</button> <button class="btn ghost" data-act="e2" aria-pressed="false">Radiação imediata</button> <button class="btn ghost" data-act="e3" aria-pressed="false">Precipitação radioativa</button></div>
</div>
<div class="step">
  <h3>Os sobreviventes</h3>
  <p>Os sobreviventes, os <b>hibakusha</b>, contam sua história há décadas, e muitos se tornaram vozes pela abolição das armas nucleares. Desde 1950 uma fundação conjunta japonesa e americana acompanha cerca de 120 mil deles e suas famílias. Seus registros de saúde são a principal fonte do que se sabe sobre os efeitos de longo prazo da radiação, incluindo um risco maior de câncer, e fundamentam as normas de proteção radiológica no mundo todo.</p>
</div>`,
};

WT.L.ch.nwrace = {
  num: "Lição 1", title: "A corrida armamentista e os tratados", short: "Corrida e tratados",
  html: `
<div class="step">
  <h3>Começa uma corrida</h3>
  <p>A União Soviética testou sua primeira bomba atômica em 1949, o Reino Unido em 1952, a França em 1960 e a China em 1964. Em 1952 os Estados Unidos testaram a primeira bomba <b>termonuclear</b>, ou de hidrogênio, em que uma explosão de fissão desencadeia a fusão de isótopos de hidrogênio; a União Soviética veio em poucos anos. Essas armas podiam ser muito mais potentes que as bombas de 1945.</p>
</div>
<div class="step">
  <h3>Castle Bravo, 1954: a precipitação radioativa</h3>
  <p>Um teste americano no atol de Bikini em março de 1954 foi muito maior do que o previsto. Sua precipitação, uma cinza radioativa branca, caiu sobre os atóis habitados de Rongelap e Utrik e sobre o barco pesqueiro japonês Daigo Fukuryū Maru («Dragão da Sorte nº 5»). A tripulação adoeceu e seu radiotelegrafista morreu naquele outono. A indignação ajudou a iniciar a campanha mundial para acabar com os testes.</p>
  <div class="btns"><button class="btn ghost" data-act="wind">Repetir o vento</button></div>
</div>
<div class="step">
  <h3>Setenta mil ogivas</h3>
  <p>Entre 1945 e 2017 foram feitos cerca de 2000 testes nucleares, mais de 500 deles a céu aberto. O número de ogivas no mundo cresceu por quatro décadas, até cerca de 70 mil em meados dos anos 1980, e depois caiu mais de quatro quintos após o fim da Guerra Fria.</p>
  <div class="ctl"><label for="nwr-y">Ano</label><input id="nwr-y" type="range" data-bind="yr" data-instant min="1945" max="2025" step="1" value="1986"><output data-show="yr" data-fmt="0"></output></div>
</div>
<div class="step">
  <h3>Os tratados</h3>
  <p>O Tratado de Proibição Parcial de Testes Nucleares, de 1963, levou os testes para debaixo da terra. O <b>Tratado de Não Proliferação de Armas Nucleares</b> (TNP), de 1968, ao qual hoje pertencem quase todos os países, proíbe a disseminação das armas e compromete os Estados nucleares com o desarmamento. Tratados entre os Estados Unidos e a União Soviética, depois a Rússia, reduziram os arsenais, e o Tratado de Proibição Completa de Testes Nucleares (CTBT), de 1996, assinado pela maior parte do mundo mas ainda não em vigor, proíbe toda explosão de teste. Aponte para um tratado.</p>
</div>`,
};

WT.L.ch.nwverify = {
  num: "Lição 1", title: "Vigiar os testes, guardar o material", short: "Verificação",
  html: `
<div class="step">
  <h3>Escutar a Terra</h3>
  <p>Um tratado vale o que valem os meios de verificá-lo. A rede de monitoramento do CTBT foi pensada para cobrir o planeta: 170 estações sísmicas entre mais de 300 instalações. Uma explosão subterrânea é súbita e rasa e empurra a rocha para fora, por isso seu registro sísmico é diferente do deslizamento de uma falha num terremoto.</p>
  <div class="btns" role="group" aria-label="Fonte"><button class="btn ghost" data-act="vEx" aria-pressed="true">Explosão</button> <button class="btn ghost" data-act="vEq" aria-pressed="false">Terremoto</button></div>
</div>
<div class="step">
  <h3>Som no ar e na água</h3>
  <p>Sessenta estações de <b>infrassom</b> escutam sons graves demais para o ouvido, que viajam milhares de quilômetros pela atmosfera. Onze estações <b>hidroacústicas</b> escutam nos oceanos, onde uma camada de água canaliza o som através de bacias inteiras.</p>
</div>
<div class="step">
  <h3>O xenônio: um relógio no ar</h3>
  <p>Mesmo um teste subterrâneo bem contido pode deixar escapar xenônio radioativo, um gás nobre que não reage com nada. Seus isótopos decaem em ritmos diferentes, então suas proporções indicam há quanto tempo ocorreu a fissão e ajudam a distinguir um teste de um reator ou de uma usina de isótopos médicos. Ler esse relógio exige dados nucleares: rendimentos de fissão e meias-vidas.</p>
  <div class="ctl"><label for="nwv-d">Dias desde a fissão</label><input id="nwv-d" type="range" data-bind="days" data-instant min="0" max="60" step="0.5" value="5"><output data-show="days" data-fmt="1"></output></div>
</div>
<div class="step">
  <h3>Salvaguardas: contar o material</h3>
  <p>Pelo Tratado de Não Proliferação, a Agência Internacional de Energia Atômica (AIEA) verifica se o material nuclear declarado continua em uso pacífico. Os inspetores mantêm a contabilidade, lacram contêineres, vigiam com câmeras e coletam amostras por esfregaço. Também medem: os raios gama do urânio-235 revelam quão enriquecido está o urânio, e a contagem de nêutrons pesa o plutônio. As duas medidas se baseiam em dados nucleares.</p>
</div>`,
};

WT.L.ch.nwdata = {
  num: "Lição 1", title: "Reatores, armas e dados nucleares", short: "Reatores e armas",
  html: `
<div class="step">
  <h3>Partir e unir</h3>
  <p>A energia nuclear vem de duas reações opostas. A <b>fissão</b> parte um núcleo pesado como o urânio; a <b>fusão</b> une núcleos leves como o hidrogênio. Ambas transformam um pouco de massa em muita energia, como mostra a <a href="./#binding" data-keep-lang>curva da energia de ligação</a>. Os reatores de potência usam a fissão; o Sol, e as máquinas de <a href="#fusion">fusão</a> em construção hoje, usam a fusão.</p>
</div>
<div class="step">
  <h3>Por que um reator não pode explodir como uma bomba</h3>
  <p>Um reator de potência e uma arma usam a fissão, mas quase nada mais se parece. O combustível do reator é sobretudo urânio-238, com apenas alguns por cento de urânio-235. A reação em cadeia é mantida em equilíbrio, no ritmo da pequena fração de nêutrons que chegam atrasados, e quando o combustível esquenta a própria física a freia. Acidentes de reator podem ser muito graves, por superaquecimento, vapor ou hidrogênio (veja <a href="#accidents">três acidentes</a>), mas um reator de potência não pode se tornar uma explosão nuclear.</p>
</div>
<div class="step">
  <h3>O enriquecimento importa</h3>
  <p>O urânio natural tem 0,7 % de urânio-235. O combustível dos reatores de potência é enriquecido a cerca de 3–5 %. Tudo abaixo de 20 % se chama <b>urânio pouco enriquecido</b> e não é considerado utilizável em armas; de 20 % para cima é altamente enriquecido e fica sob os controles mais rigorosos. Desde 1978 muitos reatores de pesquisa no mundo foram convertidos de combustível altamente enriquecido para pouco enriquecido.</p>
</div>
<div class="step">
  <h3>Dados nucleares para a segurança e a verificação</h3>
  <p>Onde quer que se manuseie material físsil, em fábricas de combustível, contêineres de transporte e piscinas de armazenamento, os engenheiros calculam quão perto ele está de uma reação em cadeia e mantêm uma margem ampla; esses cálculos se baseiam em dados nucleares avaliados. Quando essa margem foi ignorada, como numa usina de combustível em Tokaimura, no Japão, em 1999, trabalhadores morreram. Os mesmos dados, meias-vidas, rendimentos de fissão e seções de choque, permitem aos inspetores medir o material e à rede de monitoramento ler uma amostra de xenônio.</p>
</div>`,
};

Object.assign(WT.L.labels, {
  // nwhist
  "fission: a heavy nucleus splits into two lighter ones": "fissão: um núcleo pesado se parte em dois mais leves",
  "fission: one nucleus splits in two": "fissão: um núcleo se parte em dois",
  "two lighter nuclei": "dois núcleos mais leves", "and a few free neutrons": "e alguns nêutrons livres",
  "after Meitner & Frisch {#} · illustration": "segundo Meitner e Frisch, {#} · ilustração",
  "first split": "primeira divisão", "generation {#}": "geração {#}",
  "each split frees neutrons that can split more nuclei: a chain reaction": "cada divisão libera nêutrons que podem partir mais núcleos: uma reação em cadeia",
  "each split frees neutrons that split more nuclei": "cada divisão libera nêutrons que partem mais núcleos",
  "the idea only · illustration": "só a ideia · ilustração",
  "Oak Ridge, Tennessee": "Oak Ridge, Tennessee", "Hanford, Washington": "Hanford, Washington", "Los Alamos, New Mexico": "Los Alamos, Novo México",
  "separating uranium{#}": "separar o urânio{#}", "reactors making plutonium": "reatores que produzem plutônio", "the laboratory": "o laboratório",
  "three secret sites, {#}–{#}": "três locais secretos, {#}–{#}", "after US DOE / OSTI, The Manhattan Project": "segundo US DOE / OSTI, The Manhattan Project",
  "fission found": "descoberta da fissão", "Einstein–Szilard letter": "carta de Einstein e Szilard", "Manhattan Project": "Projeto Manhattan",
  "first chain reaction": "primeira reação em cadeia", "Trinity": "Trinity", "Hiroshima, Nagasaki": "Hiroshima, Nagasaki",
  "Dec {#} · fission discovered in Berlin": "dez. {#} · fissão descoberta em Berlim",
  "Aug {#} · the Einstein–Szilard letter": "ago. {#} · a carta de Einstein e Szilard",
  "{#} · the Manhattan Project begins": "{#} · começa o Projeto Manhattan",
  "Dec {#} · first controlled chain reaction, Chicago": "dez. {#} · primeira reação em cadeia controlada, Chicago",
  "{#} July {#} · Trinity, New Mexico": "{#} de julho de {#} · Trinity, Novo México",
  "{#} and {#} August {#} · Hiroshima and Nagasaki": "{#} e {#} de agosto de {#} · Hiroshima e Nagasaki",
  "seven years from a laboratory discovery to a weapon": "sete anos de uma descoberta de laboratório a uma arma", "{#} to {#}": "de {#} a {#}",
  "sources: R. Rhodes, The Making of the Atomic Bomb ({#}); US DOE / OSTI history": "fontes: R. Rhodes, The Making of the Atomic Bomb ({#}); história do US DOE / OSTI",
  "sources: Rhodes {#}; US DOE": "fontes: Rhodes {#}; US DOE",
  // nwcities
  "Hiroshima": "Hiroshima", "Nagasaki": "Nagasaki",
  "one lantern for about {#} people who had died by the end of {#}": "uma lanterna para cada {#} pessoas, aproximadamente, mortas até o fim de {#}",
  "one lantern ≈ {#} people who died by the end of {#}": "uma lanterna ≈ {#} mortos até o fim de {#}",
  "faint lanterns: the range between the low and the high estimate": "lanternas fracas: a faixa entre a estimativa baixa e a alta",
  "faint lanterns: the range of estimates": "lanternas fracas: faixa das estimativas",
  "estimates: Radiation Effects Research Foundation (RERF)": "estimativas: Radiation Effects Research Foundation (RERF)", "estimates: RERF": "estimativas: RERF",
  "blast": "onda de choque", "heat": "calor", "prompt radiation": "radiação imediata", "fallout": "precipitação radioativa",
  "a pressure wave that flattens buildings": "uma onda de pressão que derruba prédios",
  "a flash of light and heat that burns and starts fires": "um clarão de luz e calor que queima e provoca incêndios",
  "gamma rays and neutrons in the first instant": "raios gama e nêutrons no primeiro instante",
  "radioactive dust carried downwind, for days to weeks": "poeira radioativa levada pelo vento, por dias ou semanas",
  "pick an effect": "escolha um efeito", "pick an effect to see what it does": "escolha um efeito para ver o que ele faz",
  "rings are qualitative, not to scale": "anéis qualitativos, fora de escala", "after public civil-defence literature": "segundo a literatura pública de defesa civil",
  "about {#} survivors, followed since {#}": "cerca de {#} sobreviventes, acompanhados desde {#}",
  "about {#} survivors and their families, followed since {#}": "cerca de {#} sobreviventes e suas famílias, acompanhados desde {#}",
  "one dot = {#} people": "um ponto = {#} pessoas", "RERF Life Span Study": "Life Span Study da RERF",
  "Radiation Effects Research Foundation, Life Span Study · Hiroshima Peace Memorial Museum": "Radiation Effects Research Foundation, Life Span Study · Museu Memorial da Paz de Hiroshima",
  // nwrace
  "Bikini Atoll (test site)": "atol de Bikini (local de testes)", "Rongelap": "Rongelap", "Utrik": "Utrik",
  "fishing boat Lucky Dragon No. {#}": "pesqueiro Dragão da Sorte nº {#}", "Lucky Dragon No. {#}": "Dragão da Sorte nº {#}", "wind": "vento",
  "schematic of the fallout, not to scale": "esquema da precipitação, fora de escala", "schematic, not to scale": "esquema, fora de escala",
  "after US DOE Marshall Islands history; Hiroshima Peace Memorial Museum": "segundo a história das Ilhas Marshall do US DOE; Museu Memorial da Paz de Hiroshima",
  "after US DOE history": "segundo a história do US DOE",
  "{#}: about {#} warheads": "{#}: cerca de {#} ogivas",
  "nuclear warheads in the world": "ogivas nucleares no mundo", "nuclear warheads in the world (approximate)": "ogivas nucleares no mundo (aproximado)",
  "peak, {#}": "pico, {#}", "peak, {#}: about {#}": "pico, {#}: cerca de {#}",
  "approximate, after the Federation of American Scientists": "aproximado, segundo a Federation of American Scientists", "approx., after FAS": "aprox., segundo a FAS",
  "point at a green dot to read a treaty": "aponte para um ponto verde para ler um tratado", "tap a green dot: a treaty": "toque num ponto verde: um tratado",
  "{#} · Partial Test Ban": "{#} · Proibição Parcial de Testes", "{#} · Non-Proliferation Treaty": "{#} · Tratado de Não Proliferação",
  "{#} · INF Treaty": "{#} · Tratado INF", "{#} · START I": "{#} · START I", "{#} · Comprehensive Test Ban": "{#} · Proibição Completa de Testes", "{#} · New START": "{#} · Novo START",
  "no tests in the air, in space or under water": "sem testes no ar, no espaço ou debaixo d'água",
  "no spread of weapons; disarmament; peaceful use": "não disseminar armas; desarmamento; uso pacífico",
  "a whole class of missiles removed": "eliminada toda uma classe de mísseis", "the first deep cuts": "os primeiros grandes cortes",
  "no test explosions at all (not yet in force)": "nenhuma explosão de teste (ainda não em vigor)", "limits on deployed warheads (expired {#})": "limites a ogivas implantadas (expirou em {#})",
  // nwverify
  "explosion: shallow, pushes outward": "explosão: rasa, empurra para fora", "earthquake: deeper, slip on a fault": "terremoto: mais profundo, deslizamento de falha",
  "explosion: sharp start, strong P waves": "explosão: início brusco, ondas P fortes", "earthquake: weak start, strong S waves": "terremoto: início fraco, ondas S fortes",
  "seismometer": "sismômetro", "P": "P", "S": "S",
  "qualitative shapes · CTBTO International Monitoring System": "formas qualitativas · Sistema Internacional de Monitoramento da CTBTO",
  "CTBTO International Monitoring System": "Sistema Internacional de Monitoramento da CTBTO",
  "infrasound": "infrassom", "hydroacoustic": "hidroacústica", "sound channelled in the ocean": "som canalizado no oceano", "sound in the sea": "som no mar",
  "{#} infrasound and {#} hydroacoustic stations in the network": "{#} estações de infrassom e {#} hidroacústicas na rede",
  "{#} infrasound · {#} hydroacoustic stations": "{#} de infrassom · {#} hidroacústicas",
  "xenon{#}": "xenônio{#}", "xenon{#}m": "xenônio{#}m", "Xe{#}": "Xe{#}", "Xe{#}m": "Xe{#}m",
  "half-life {#} h": "meia-vida {#} h", "half-life {#} d": "meia-vida {#} d", "start": "início",
  "{#} days after the fission": "{#} dias após a fissão",
  "short-lived isotopes fade first, so the ratios read like a clock": "os isótopos de vida curta somem primeiro, então as proporções se leem como um relógio",
  "the ratios change with time: a clock": "as proporções mudam com o tempo: um relógio",
  "equal starting amounts, for illustration; real ratios come from fission yields": "quantidades iniciais iguais, para ilustrar; as proporções reais vêm dos rendimentos de fissão",
  "illustrative starting amounts": "quantidades iniciais ilustrativas", "half-lives: ENSDF / NUBASE{#}": "meias-vidas: ENSDF / NUBASE{#}",
  "seal": "lacre", "camera": "câmera", "detector": "detector",
  "uranium{#} line, {#} keV": "linha do urânio{#}, {#} keV", "U{#} line, {#} keV": "linha do U{#}, {#} keV", "gamma-ray energy →": "energia gama →",
  "the height of the peak tells how enriched the uranium is": "a altura do pico indica quão enriquecido está o urânio",
  "a bigger peak: more uranium{#}": "pico maior: mais urânio{#}", "after IAEA safeguards; spectrum illustrative": "segundo as salvaguardas da AIEA; espectro ilustrativo",
  // nwdata
  "fission: heavy splits": "fissão: o pesado se parte", "fusion: light nuclei join": "fusão: núcleos leves se unem",
  "both turn a little mass into energy": "ambas transformam um pouco de massa em energia", "both release nuclear energy": "ambas liberam energia nuclear",
  "a power reactor: four reasons it cannot explode like a bomb": "um reator de potência: quatro razões pelas quais não pode explodir como uma bomba", "a power reactor": "um reator de potência",
  "low-enriched fuel, mostly uranium{#}": "combustível pouco enriquecido, sobretudo urânio{#}", "chain held in balance, not growing": "cadeia em equilíbrio, sem crescer",
  "late neutrons set a slow pace": "nêutrons atrasados ditam um ritmo lento", "hotter fuel → fewer fissions": "combustível mais quente → menos fissões",
  "after IAEA, US NRC, World Nuclear Association": "segundo AIEA, US NRC, World Nuclear Association",
  "share of uranium{#}": "fração de urânio{#}", "low-enriched uranium (LEU): below {#} %": "urânio pouco enriquecido (LEU): abaixo de {#} %", "LEU: below {#} %": "LEU: abaixo de {#} %",
  "highly enriched (HEU)": "altamente enriquecido (HEU)", "HEU": "HEU", "natural uranium": "urânio natural", "power-reactor fuel": "combustível de reator de potência", "reactor fuel": "combustível de reator",
  "about {#}–{#} %": "cerca de {#}–{#} %", "definitions: IAEA Safeguards Glossary": "definições: Glossário de Salvaguardas da AIEA",
  "evaluated nuclear data": "dados nucleares avaliados", "fuel plants": "fábricas de combustível", "transport casks": "contêineres de transporte", "storage pools": "piscinas de armazenamento",
  "safeguards": "salvaguardas", "test monitoring": "monitoramento de testes",
  "the same data keep handling safe and let inspectors measure": "os mesmos dados tornam o manuseio seguro e permitem aos inspetores medir",
  "safety margins and measurements rest on the data": "margens de segurança e medidas se baseiam nos dados", "Tokaimura {#}: IAEA fact-finding report": "Tokaimura {#}: relatório de investigação da AIEA",
});
