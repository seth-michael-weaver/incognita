/* Portuguese (pt-PT): preeq (Chapter 4, pre-equilibrium) */
WT.L.ch.preeq = {
  num: "Capítulo 7", title: "Colisões antes da calma", short: "Pré-equilíbrio",
  lead: "Um neutrão que entra num núcleo não partilha a sua energia com todos ao mesmo tempo. Durante as primeiras colisões uma só partícula guarda quase toda a energia, e essa partícula pode sair disparada de volta. Isto é o pré-equilíbrio: emissão “antes de a energia se repartir por igual”.",
  html: `
<div class="step">
  <p>Dois poços, um para <em class="p">protões</em> e outro para <em class="n">neutrões</em>. Cada bola é um nucleão num nível de energia, desenhado como um degrau; os degraus enchem-se de baixo para cima até à <b>superfície de Fermi</b>. Um nucleão acima da linha tracejada “livre” tem energia suficiente para escapar. O motor segue protões e neutrões separadamente.</p>
  <p>O neutrão que chega flutua por cima com toda a energia: a sua mais vários MeV (milhões de eletrão-volts) libertados ao ser capturado.</p>
</div>
<div class="step">
  <h3>Levantar pares</h3>
  <p>Cada colisão sobe um nucleão para um degrau vazio e deixa para trás um <b>buraco</b> (um anel aberto). As partículas acima da superfície e os buracos abaixo dela chamam-se todos <b>excitões</b>. A primeira colisão dá 2 partículas e 1 buraco (n = 3); cada colisão seguinte acrescenta outro par.</p>
  <div class="btns"><button class="btn" data-act="collide">Colidir</button><button class="btn ghost" data-act="reset">Recomeçar</button></div>
  <p>Carrega em Colidir algumas vezes. O nucleão levantado pode ser um protão ou um neutrão, e o motor conta cada tipo. Com cada par a energia reparte-se por mais, por isso a partícula de cima fica mais abaixo.</p>
</div>
<div class="step">
  <h3>A bifurcação em cada etapa</h3>
  <p>Em cada etapa o neutrão de cima ou escapa (seta para cima, só se estiver acima da linha livre) ou volta a colidir (seta para baixo); a espessura indica a probabilidade. A taxa de escape vem do <b>balanço detalhado</b>: da probabilidade do processo inverso, essa mesma partícula ser absorvida, que o Capítulo 5 calcula. A taxa de colisão é a intensidade de uma colisão nucleão-nucleão vezes o número de novas configurações a que pode levar.</p>
  <div class="ctl"><label for="pe-n">Etapa (excitões n)</label><input id="pe-n" type="range" data-bind="n" min="3" max="11" step="2" value="3" data-instant><output data-show="n" data-fmt="0"></output></div>
  <p>Sobe a etapa. No início uma partícula tem quase toda a energia, por isso o que escapa é rápido. Mais tarde a energia está muito repartida e sai pouco.</p>
</div>
<div class="step">
  <h3>De onde vem a cauda rápida</h3>
  <p>O monte da direita é o <b>espectro</b>: quantos neutrões saem com cada energia, os lentos à esquerda, os rápidos à direita. Cada reação percorre a cadeia até o neutrão de cima escapar, e a sua cor diz quando: <em style="font-style:normal;color:var(--warm);font-weight:600">laranja intenso</em> na etapa 3, mais pálido depois, <em class="n">azul</em> se só saiu quando o núcleo já estava calmo (Capítulo 8).</p>
  <div class="btns"><button class="btn" data-act="run">Lançar 300 reações</button></div>
  <p>A etapa 3 forma um planalto largo, quase plano, que chega até à energia máxima. As etapas seguintes amontoam-se mais abaixo. A bossa azul é a <b>evaporação</b>: quando todos partilham a energia, só escapam neutrões lentos, como o vapor de um líquido quente.</p>
  <div class="ctl"><label for="pe-e">Energia do neutrão</label><input id="pe-e" type="range" data-bind="E" min="5" max="60" step="0.5" value="20"><output data-show="E" data-fmt="1"></output></div>
  <p>Muda a energia do neutrão que chega: lança-se uma nova série e o planalto alonga-se. A evaporação sozinha nunca produz neutrões rápidos.</p>
</div>
<div class="step">
  <h3>Contar configurações</h3>
  <p>O contador percorre todas as maneiras de pôr partículas em degraus vazios e buracos em degraus cheios de modo que as suas energias somem a energia a repartir (aqui os degraus estão a 1 MeV). Os nucleões são fermiões: dois não podem partilhar um degrau, por isso uma partícula tem de cair num degrau vazio e um buraco só se abre onde havia um nucleão. É o <b>bloqueio de Pauli</b>.</p>
  <div class="ctl"><label for="pe-u">Energia a repartir (MeV)</label><input id="pe-u" type="range" data-bind="U" min="2" max="16" step="1" value="8" data-instant><output data-show="U" data-fmt="0"></output></div>
  <div class="btns"><button class="btn" data-act="addpair">Juntar um par</button><button class="btn ghost" data-act="droppair">Tirar um par</button></div>
  <p>Junta um par e a contagem dispara; sobe a energia e cresce aproximadamente como <i>E</i><sup>n−1</sup>. Esta contagem, a <b>densidade de estados partícula-buraco</b>, fixa a taxa de colisão: mais configurações, mais destinos para uma colisão. O motor conta sobre a escada real, com degraus a uma fração de MeV, e acrescenta um limite que se vê a energia alta: um buraco não pode estar abaixo do fundo do poço.</p>
</div>
<div class="step">
  <h3>Também saem agregados</h3>
  <p>Também podem sair cedo pequenos agregados. Numa <b>captação</b> (pickup), um protão a caminho da saída agarra um neutrão à superfície e sai com ele como um <em class="n">deuterão</em>; se agarrar dois, dá um tritão ou um hélio-3. Num <b>arrancamento</b> (knockout), o neutrão que chega choca com uma <em class="a">partícula alfa</em> (dois protões e dois neutrões) já formada perto da superfície e expulsa-a. O motor usa as fórmulas de Kalbach para ambos.</p>
  <div class="btns"><button class="btn ghost" data-act="pickup">Captar um neutrão → d</button><button class="btn ghost" data-act="knock">Arrancar uma α</button></div>
  <p>Carrega num botão para ver um. Ambos dão aos deuterões e às partículas alfa as suas próprias caudas rápidas, que começam logo acima da energia que custa arrancar cada um.</p>
</div>
<div class="step">
  <h3>Um segundo rápido</h3>
  <p>A energia alta, um segundo nucleão levantado pode continuar acima da linha livre quando o primeiro neutrão sai, e escapar também, como neutrão ou protão rápido. Os poços repetem uma reação de cada vez, com a escala de energia comprimida.</p>
  <div class="ctl"><label for="pe-e2">Energia do neutrão</label><input id="pe-e2" type="range" data-bind="E" min="5" max="80" step="0.5" value="40"><output data-show="E" data-fmt="1"></output></div>
  <p>Muda a energia. Abaixo de cerca de 20 MeV o segundo nucleão raramente passa a linha; acima, cada vez mais reações largam duas partículas rápidas. É o <b>pré-equilíbrio múltiplo</b>, que o motor inclui a partir de 20 MeV. O que não saiu torna-se o núcleo composto do próximo capítulo. Abaixo de alguns MeV (o nível discreto mais alto do alvo que é usado) o motor salta a cadeia por completo.</p>
  <div class="aside">No código: <code>preeq/exciton.py</code> (cadeia de excitões de duas componentes, taxas de colisão e de escape), <code>density/particle_hole.py</code> (densidades de estados partícula-buraco com correções de Pauli e de poço finito), <code>preeq/complex.py</code> (captação, stripping e arrancamento α de Kalbach), <code>preeq/multi.py</code> (pré-equilíbrio múltiplo), <code>compound/normalization.py</code> (passagem ao núcleo composto).</div>
</div>`,
};
Object.assign(WT.L.labels, {
  // wells
  "protons": "protões",
  "neutrons": "neutrões",
  "Fermi": "Fermi",
  "Fermi surface": "superfície de Fermi",
  "free": "livre",
  "free: can escape": "livre: pode escapar",
  "all the energy in one nucleon": "toda a energia num nucleão",
  "{#} particle, {#} holes": "{#} partícula, {#} buracos",
  // pairs
  "{#} particle, {#} holes: n = {#}": "{#} partícula, {#} buracos: n = {#}",
  "{#} particle, {#} hole: n = {#}": "{#} partícula, {#} buraco: n = {#}",
  "{#} particles, {#} hole: n = {#}": "{#} partículas, {#} buraco: n = {#}",
  "{#} particles, {#} holes: n = {#}": "{#} partículas, {#} buracos: n = {#}",
  "protons: {#} lifted, {#} hole": "protões: {#} levantado(s), {#} buraco",
  "protons: {#} lifted, {#} holes": "protões: {#} levantado(s), {#} buracos",
  "neutrons: {#} lifted, {#} hole": "neutrões: {#} levantado(s), {#} buraco",
  "neutrons: {#} lifted, {#} holes": "neutrões: {#} levantado(s), {#} buracos",
  "chain ends: the rest becomes a compound nucleus": "fim da cadeia: o resto forma um núcleo composto",
  // fork
  "about {#} MeV above surface": "cerca de {#} MeV acima da superfície",
  "escapes  {#}%": "escapa  {#} %",
  "collides again  {#}%": "volta a colidir  {#} %",
  "below the free line: it cannot leave": "abaixo da linha livre: não pode sair",
  "n = {#}: {#} particles, {#} hole, {#} MeV": "n = {#}: {#} partículas, {#} buraco, {#} MeV",
  "n = {#}: {#} particles, {#} holes, {#} MeV": "n = {#}: {#} partículas, {#} buracos, {#} MeV",
  "stage n = {#}: {#} particles and {#} hole share {#} MeV": "etapa n = {#}: {#} partículas e {#} buraco partilham {#} MeV",
  "stage n = {#}: {#} particles and {#} holes share {#} MeV": "etapa n = {#}: {#} partículas e {#} buracos partilham {#} MeV",
  // tail
  "max {#} MeV": "máx. {#} MeV",
  "slow": "lento",
  "fast →": "rápido →",
  "stage {#}": "etapa {#}",
  "chain over: compound": "fim da cadeia: composto",
  "left at:": "saiu:",
  "neutron left at:": "neutrão saiu em:",
  "evaporation": "evaporação",
  "{#} of {#} landed · {#} left during the chain": "{#} de {#} caíram · {#} saíram durante a cadeia",
  // pauli
  "well bottom: no deeper hole": "fundo do poço: nenhum buraco mais fundo",
  "bottom of the well": "fundo do poço",
  "{#} MeV to share": "{#} MeV a repartir",
  "{#} particles · {#} hole": "{#} partículas · {#} buraco",
  "{#} particles · {#} holes": "{#} partículas · {#} buracos",
  "ways, all counted": "maneiras, todas contadas",
  "arrangements so far": "configurações até agora",
  "one more pair: {#} ways": "mais um par: {#} maneiras",
  "never two on one rung · holes only where a nucleon was": "nunca dois num degrau · buracos só onde havia um nucleão",
  "(first {#} shown as ticks)": "(as primeiras {#}, como marcas)",
  // cluster
  "a deuteron leaves": "sai um deuterão",
  "grabs a neutron at the edge": "agarra um neutrão na orla",
  "a fast proton heads out": "um protão rápido a sair",
  "an α ({#} protons + {#} neutrons) waits at the edge": "uma α ({#} protões + {#} neutrões) espera na orla",
  "knocked straight out": "expulsa de imediato",
  // second
  "first fast neutron": "primeiro neutrão rápido",
  "second fast proton": "segundo protão rápido",
  "second fast neutron": "segundo neutrão rápido",
  "below the free line: stays": "abaixo da linha livre: fica",
  "below the free line: it stays": "abaixo da linha livre: fica",
  "the rest settles: compound nucleus": "o resto acalma: núcleo composto",
  "{#} MeV carried in": "{#} MeV trazidos",
  "second fast particle in {#} of the last {#} reactions": "segunda partícula rápida em {#} das últimas {#} reações",
});
