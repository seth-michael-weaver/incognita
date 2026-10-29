/* Portuguese (pt-PT): decay (Capítulo 9) */
WT.L.ch.decay = {
  num: "Capítulo 9", title: "Decaimento do núcleo composto", short: "Decaimento",
  lead: "O núcleo composto tem de libertar a sua energia emitindo uma partícula ou um fotão. Este capítulo desenha cada saída como uma porta. O trabalho do motor é dizer que parte do fluxo (a corrente de reações que aqui chega) sai por cada porta.",
  html: `
<div class="step">
  <p>Uma porta por saída: um <em class="g">fotão</em> (γ), um <em class="n">neutrão</em> (n), um <em class="p">protão</em> (p), uma <em class="a">partícula alfa</em> (α: dois protões e dois neutrões) e, só em núcleos pesados, a <em class="f">fissão</em> (partir-se em dois). A abertura iluminada de cada porta é a fração dessa saída, e as bolas saem ao mesmo ritmo; as portas cinzentas estão fechadas. Como esqueceu a forma como se formou, o núcleo usa cada porta b em proporção a um peso:</p>
  <div class="formula">fração<sub>b</sub> = T<sub>b</sub> · ρ<sub>b</sub> / Σ<sub>c</sub> T<sub>c</sub> · ρ<sub>c</sub></div>
  <p>O <b>coeficiente de transmissão</b> <i>T</i> é a probabilidade de uma partícula que chega à borda a atravessar; para as partículas, vem do modelo ótico do Capítulo 5, aplicado ao contrário. A <b>densidade de níveis</b> ρ, escrita junto a cada porta, conta os estados em que o núcleo restante pode acabar. Repartir segundo <i>T</i> vezes ρ é a regra de <b>Hauser–Feshbach</b>. A 10 MeV, a porta do neutrão leva quase tudo.</p>
</div>
<div class="step">
  <h3>Espetros de evaporação</h3>
  <p>A porta do neutrão, dividida segundo a energia de saída ε (lentos à esquerda, rápidos à direita). A abertura <i>T</i>(ε) de cada porta alarga-se para os neutrões mais rápidos. Por baixo está a multidão de estados em que o núcleo restante pode ficar: um neutrão lento deixa para trás quase toda a energia, onde os estados abundam, por isso as multidões diminuem para a direita.</p>
  <div class="ctl"><label for="dc-sp">Energia disponível</label><input id="dc-sp" type="range" data-bind="spare" min="1" max="12" step="0.5" value="5"><output data-show="spare" data-fmt="1"></output></div>
  <p>Porta × multidão transforma o monte numa bossa, o <b>espectro de evaporação</b>, como o vapor que escapa de um líquido quente. Arrasta a energia disponível (em MeV, milhões de eletrão-volts): o monte recomeça e o seu pico fica perto de 1 MeV, fixado pela temperatura nuclear. A energia extra sobretudo aquece mais o núcleo restante.</p>
</div>
<div class="step">
  <h3>A barreira de Coulomb na emissão</h3>
  <p>A energia de um protão a cada distância r do centro: um poço por dentro e, por fora, uma colina devida à repulsão elétrica (de Coulomb), que decresce como 1/r. Abaixo do topo, o protão, que ressalta dentro do poço, só pode atravessar por <b>efeito túnel</b> o troço sombreado, um efeito quântico que resulta uma vez em cada muitos embates contra a parede. As probabilidades calculam-se como no Capítulo 4: quanto mais larga e alta a barreira, mais zeros em “1 embate em 10<sup>N</sup>”.</p>
  <div class="ctl"><label for="dc-ce">Energia da partícula</label><input id="dc-ce" type="range" data-bind="eps" min="0.5" max="12" step="0.1" value="3"><output data-show="eps" data-fmt="1"></output></div>
  <div class="btns"><button class="btn ghost" data-act="toggleAlpha">Alternar protão / alfa</button></div>
  <p>Baixa a energia e repara como o túnel se alarga; depois muda para a alfa, cujas duas cargas enfrentam uma colina cerca de duas vezes mais alta. É por isso que os neutrões, sem carga, costumam ganhar assim que podem sair, e que as saídas de protão e alfa importam sobretudo em núcleos leves e a energias altas.</p>
</div>
<div class="step">
  <h3>Limiares dos canais</h3>
  <p>Cada porta de partícula só se abre acima da sua <b>energia de separação</b>, o custo de arrancar essa partícula: aqui 8 MeV para um neutrão, 9 para um protão, 7 para uma alfa. Abaixo dos 8 MeV do neutrão, quase todos os decaimentos emitem luz.</p>
  <div class="ctl"><label for="dc-e">Energia de excitação</label><input id="dc-e" type="range" data-bind="E" min="5" max="24" step="0.1" value="7"><output data-show="E" data-fmt="1"></output></div>
  <p>Arrasta a energia de excitação para lá dos 8 MeV. Em cerca de 1 MeV, a porta do neutrão escancara-se e a fração do fotão cai cem vezes. A porta alfa é a primeira a destrancar-se, aos 7 MeV, mas mal se abre: a sua colina de Coulomb (Capítulo 4) mantém-na quase fechada até muito acima. A porta do protão destranca-se aos 9 MeV e também continua estreita, travada pela sua própria colina.</p>
</div>
<div class="step">
  <h3>Conservação do momento angular e da paridade</h3>
  <p>O núcleo composto (em cima) tem spin <i>J</i>; em baixo, os estados do núcleo restante estão em gavetas segundo o seu spin <i>J</i>′. O neutrão leva a diferença de spin e paridade: se sai com momento angular orbital <i>l</i>, muda o spin até <i>l</i> + ½ e inverte a paridade quando <i>l</i> é ímpar. Maior <i>l</i> significa porta mais estreita; a porta de cada gaveta é a de menor <i>l</i> que lá chega. As descidas cheias conservam a paridade; as ocas invertem-na.</p>
  <div class="ctl"><label for="dc-j">Spin composto J</label><input id="dc-j" type="range" data-bind="J" min="0" max="10" step="1" value="2" data-instant><output id="dc-jout">5/2</output></div>
  <p>Aumenta <i>J</i>. As portas abertas deslocam-se para as gavetas de spin alto, que guardam poucos estados, enquanto as gavetas cheias ficam atrás de portas fechadas. Um núcleo composto de spin alto demora a emitir partículas, o que dá uma oportunidade aos fotões e aos isómeros (estados de vida longa, Capítulo 10).</p>
</div>
<div class="step">
  <h3>Reforço elástico</h3>
  <p>A baixa energia, o núcleo composto é um conjunto de <b>ressonâncias</b> estreitas, energias em que o neutrão é absorvido com facilidade; desenham-se oito, uma por linha. Cada uma tem larguras de porta aleatórias: a entrada (o canal do neutrão) à esquerda, de largura <i>x</i>, e as outras portas, aqui sobretudo fotões, à direita, de larguras <i>y</i>.</p>
  <div class="btns"><button class="btn" data-act="fire">Lançar 40 neutrões</button><button class="btn ghost" data-act="reroll">Novas ressonâncias</button></div>
  <p>Carrega em Lançar e segue os neutrões. Um neutrão entra numa linha na proporção da largura de entrada <i>x</i> dessa linha. Lá dentro, escolhe uma saída na proporção das larguras: de volta pela entrada com probabilidade <i>x</i> / (<i>x</i> + Σ<i>y</i>), caso contrário por uma das outras portas. Os tabuleiros contam para onde foram.</p>
  <p>O senão: uma linha com entrada larga recebe mais neutrões e também devolve mais. Assim voltam mais do que se adivinharia só pelas larguras médias. A fração real que volta a sair (uma <b>média de produtos</b>) supera a estimativa simples (um <b>produto de médias</b>); ambas estão escritas no topo.</p>
  <p>A sua razão é o <b>reforço elástico</b>. A <b>correção de flutuação de larguras</b> do motor aplica-o: transfere esse fluxo extra das outras portas de volta para a entrada.</p>
  <div class="ctl"><label for="dc-n">Outras portas</label><input id="dc-n" type="range" data-bind="Nch" min="1" max="12" step="1" value="2" data-instant><output data-show="Nch" data-fmt="0"></output></div>
  <p>Acrescenta portas. Com muitas saídas, a sua largura total deixa de flutuar, por isso a correção importa sobretudo onde há poucas portas abertas. O motor aplica-a, com a fórmula de Moldauer, a neutrões incidentes até à energia de separação do neutrão do alvo, e omite-a acima disso.</p>
</div>
<div class="step">
  <h3>Fluxo após as reações diretas</h3>
  <p>As portas deste capítulo só repartem os neutrões que de facto ficaram. Os Capítulos 6 e 7 já levaram a sua parte: alguns neutrões dão um toque rasante e saem disparados (diretos), outros chocam uma ou duas vezes e saem a grande velocidade (pré-equilíbrio). Só os restantes ficam lá dentro e aquecem o núcleo. Os contadores à direita registam cada destino; os que ficam nunca saem do núcleo, são apenas contados.</p>
  <div class="ctl"><label for="dc-einc">Energia do neutrão</label><input id="dc-einc" type="range" data-bind="Einc" min="1" max="30" step="0.5" value="8"><output data-show="Einc" data-fmt="1"></output></div>
  <p>Só os que ficam entram na competição das portas. Arrasta a energia do neutrão: a poucos MeV quase todos ficam; a 30 MeV cerca de metade já saiu antes de chegar ao equilíbrio.</p>
  <div class="aside">No código: <code>compound/prepare.py</code> (pesos de saída T·ρ por spin e paridade, regras de seleção), <code>compound/target.py</code> (primeiro decaimento com flutuações de larguras), <code>compound/continuum.py</code> (decaimento de cada intervalo posterior), <code>compound/wfc.py</code> (correções de Moldauer, HRTW, GOE), <code>compound/normalization.py</code> (fluxo que resta para o núcleo composto), <code>omp/inverse.py</code> (portas ao contrário).</div>
</div>`,
};
(function () {
  const L = {
    "{#} MeV": "{#} MeV",
    "n": "n", "p": "p", "fission": "fissão",
    "heavy only": "só pesados",
    "heavy nuclei only": "só núcleos pesados",
    "shut below {#} MeV": "fechada abaixo de {#} MeV",
    "the neutron door takes nearly everything": "a porta do neutrão leva quase tudo",
    "below the neutron threshold, nearly all decays emit light": "abaixo do limiar do neutrão, quase tudo emite luz",
    "the doors share the decays": "as portas repartem os decaimentos",
    // hump
    "{#} MeV to spare": "{#} MeV disponíveis",
    "door gap = T(ε)": "abertura = T(ε)",
    "doors: one per neutron energy ε, gap = T(ε)": "portas: uma por energia ε do neutrão, abertura = T(ε)",
    "× states left behind": "× estados restantes",
    "× states the leftover nucleus can be in: many after a slow neutron": "× estados possíveis do núcleo restante: muitos após um neutrão lento",
    "most ≈ {#} MeV": "máximo ≈ {#} MeV",
    "= the pile": "= o monte",
    "= where the neutrons land: the evaporation spectrum": "= onde caem os neutrões: o espectro de evaporação",
    "slow": "lentos",
    "slow neutrons": "neutrões lentos",
    "fast: {#} MeV →": "rápidos: {#} MeV →",
    "fast: {#} MeV (beyond, up to {#}, almost none)": "rápidos: {#} MeV (além disso, até {#}, quase nenhum)",
    "fast: {#}": "rápidos: {#}",
    "fast: {#} MeV, the neutron takes it all": "rápidos: {#} MeV, o neutrão leva tudo",
    // coulomb
    "well ↓": "poço ↓",
    "well (much deeper) ↓": "poço (muito mais fundo) ↓",
    "hilltop ≈ {#} MeV": "topo ≈ {#} MeV",
    "falls as {#}/r": "decresce como {#}/r",
    "Coulomb hill, falling as {#}/r": "colina de Coulomb, decresce como {#}/r",
    "tunnel: wider than the picture": "túnel: mais largo do que a imagem",
    "tunnel {#} fm": "túnel {#} fm",
    "proton energy {#} MeV": "energia do protão {#} MeV",
    "alpha energy {#} MeV": "energia da alfa {#} MeV",
    "proton energy {#} MeV ↑": "energia do protão {#} MeV ↑",
    "alpha energy {#} MeV ↑": "energia da alfa {#} MeV ↑",
    "above the hilltop: it rolls straight out": "acima do topo: sai diretamente a rolar",
    "below the top, must tunnel: nearly every knock gets through": "abaixo do topo, efeito túnel: passa quase em cada embate",
    "below the top, must tunnel: about {#} knock in {#} gets through": "abaixo do topo, efeito túnel: passa cerca de {#} embate em cada {#}",
    "below the top, must tunnel: about {#} knock in {#} × {#}^{#} gets through": "abaixo do topo, efeito túnel: passa cerca de {#} embate em cada {#} × {#}^{#}",
    "out": "fora",
    "through after {#} knock": "atravessa após {#} embate",
    "through after {#} knocks": "atravessa após {#} embates",
    "knocks so far: {#}": "embates até agora: {#}",
    "distance r from the centre (fm) →": "distância r ao centro (fm) →",
    // spin
    "J = {#}/{#}, parity +": "J = {#}/{#}, paridade +",
    "l={#}": "l={#}",
    "leftover states by spin J′ →": "estados restantes por spin J′ →",
    "drawers: states of the leftover nucleus by spin J′ (faint: states it holds) →": "gavetas: estados do núcleo restante por spin J′ (ténue: estados que guarda) →",
    "open doors reach {#} %": "as portas abertas chegam a {#} %",
    "open doors reach about {#} % of the states": "as portas abertas chegam a cerca de {#} % dos estados",
    "● parity kept (even l)   ○ flipped (odd l)": "● l par: paridade igual   ○ l ímpar: invertida",
    // wfc
    "entrance x": "entrada x",
    "entrance, width x": "entrada, largura x",
    "{#} other doors, y": "{#} outras portas, y",
    "{#} other door, widths y": "{#} outra porta, larguras y",
    "{#} other doors, widths y": "{#} outras portas, larguras y",
    "back out the entrance: {#} of {#}": "de volta pela entrada: {#} de {#}",
    "out another door: {#}": "por outra porta: {#}",
    // norm
    "absorbed neutrons, {#} MeV →": "neutrões absorvidos, {#} MeV →",
    "direct: {#} %": "diretas: {#} %",
    "pre-equilibrium: {#} %": "pré-equilíbrio: {#} %",
    "compound nucleus: {#} %": "núcleo composto: {#} %",
    "one glancing hit on the surface": "um toque rasante na superfície",
    "a knock or two, then out fast": "um choque ou dois e sai rápido",
    "stayed: on to the door competition": "fica: segue para a competição das portas",
  };
  // door hint with level-count wording (fmt: "1", "N", "N thousand", "N million") and T possibly in e-notation
  const cnt = [["{#} state", "{#} estado"], ["{#} states", "{#} estados"], ["{#} thousand states", "{#} mil estados"], ["{#} million states", "{#} milhões de estados"]];
  for (const [e, s] of cnt) {
    L[`weak door × ≈ ${e}`] = `porta fraca × ≈ ${s}`;
    L[`T ≈ {#} × ≈ ${e}`] = `T ≈ {#} × ≈ ${s}`;
    L[`T ≈ {#}e{#} × ≈ ${e}`] = `T ≈ {#}e{#} × ≈ ${s}`;
  }
  // share comparisons: each pct is "{#} %" or "≈ {#} %"
  const P = ["{#} %", "≈ {#} %"];
  for (const a of P) for (const b of P) {
    L[`back out ${a}, not ${b}: × {#}`] = `voltam ${a}, não ${b}: × {#}`;
    L[`share back out: average of products ${a} · product of averages ${b} · × {#}`] = `de volta: média de produtos ${a} · produto de médias ${b} · × {#}`;
    L[`other doors ${a}, not ${b}`] = `outras portas ${a}, não ${b}`;
    L[`other doors together: ${a} instead of ${b}`] = `outras portas juntas: ${a} em vez de ${b}`;
  }
  Object.assign(WT.L.labels, L);
})();

Object.assign(WT.L.labels, {
  "press Fire to send neutrons in": "carrega em Lançar para enviar neutrões",
  "stayed inside: counted here, not moved": "ficou dentro: contado aqui, não movido",
});
