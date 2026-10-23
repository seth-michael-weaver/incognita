/* Portuguese (pt-PT): cascade (chapter 8) */
WT.L.ch.cascade = {
  num: "Capítulo 8", title: "Descendo pela carta", short: "Cascata",
  lead: "Uma emissão raramente é o fim: o núcleo que fica está muitas vezes quente o suficiente para voltar a emitir.",
  html: `
<div class="step">
  <p>Um neutrão saiu do núcleo composto (esquerda), e o <b>núcleo residual</b> que deixa para trás (direita) continua quente. A bola laranja é a energia. O estado fundamental do residual está mais acima, pela <b>energia de separação</b> S<sub>n</sub> do neutrão, o custo de o arrancar.</p>
  <p>Cada vez que sai um neutrão, a bola desce o equivalente à energia cinética do neutrão. Onde para é a <b>excitação</b> do residual, a sua energia de sobra; os pontos à direita contam as aterragens.</p>
  <div class="ctl"><label for="cs-e">Energia do neutrão</label><input id="cs-e" type="range" data-bind="E" min="1" max="30" step="0.5" value="15"><output data-show="E" data-fmt="1"></output></div>
  <p>Os neutrões emitidos costumam ser lentos, por isso a maioria das descidas é curta. Os pontos azuis ficam acima do limiar de neutrões (linha tracejada): podem dar-se ao luxo de um segundo neutrão, a reação (n,2n). Abaixo de cerca de 11 MeV nenhum lá chega.</p>
</div>
<div class="step">
  <h3>Um passeio pela carta</h3>
  <p>As correntes são reações que percorrem um canto da <b>carta de nuclídeos</b>, os núcleos dispostos por número de neutrões N (na horizontal) e número de protões Z (na vertical). Todas começam na casa contornada do núcleo composto; cada casa tem o nome da reação que aí termina.</p>
  <p>Um <em class="n">neutrão</em> emitido move uma casa para a esquerda, um <em class="p">protão</em> uma para baixo, uma <em class="a">partícula alfa</em> (dois protões, dois neutrões) duas na diagonal. A largura da corrente é quanto dá esse passo; o tom e a percentagem, onde terminam as reações.</p>
  <div class="btns"><button class="btn" data-act="fire">Lançar 200 reações</button></div>
  <p>Cada passo custa de 7 a 11 MeV de energia de separação, por isso mesmo a 30 MeV o percurso tem no máximo três ou quatro passos.</p>
</div>
<div class="step">
  <h3>De cima para baixo, intervalo a intervalo</h3>
  <p>O motor esvazia cada núcleo de cima para baixo, uma fatia de energia, ou <b>intervalo</b>, de cada vez. À direita, o residual da primeira emissão; à esquerda, o seu filho, com um neutrão a menos. As bolas laranja são reações à espera em cada intervalo. Aqui os intervalos medem 1 MeV; o motor usa cerca de 40 por núcleo, ajustados à energia disponível.</p>
  <p>Quando o marcador varre um intervalo, cada bola toma uma saída segundo a competição do capítulo 6: um fotão (<em class="g">γ</em>) desce-a para um intervalo inferior, um <em class="n">neutrão</em> leva-a para o filho, um protão ou uma alfa tiram-na da figura. Abaixo de todos os limiares, os fotões levam o resto para o estado fundamental (cinzento). Depois varre-se o filho.</p>
  <div class="ctl"><label for="cs-e3">Energia do neutrão</label><input id="cs-e3" type="range" data-bind="E" min="8" max="30" step="0.5" value="18"><output data-show="E" data-fmt="1"></output></div>
  <div class="btns"><button class="btn ghost" data-act="restart">Recomeçar</button></div>
  <p>Os fotões só descem, e cada núcleo fica terminado antes dos seus filhos, por isso nada cai num intervalo já esvaziado.</p>
</div>
<div class="step">
  <h3>Dar nome à história</h3>
  <p>Reproduz-se uma reação de cada vez: o marcador salta pela carta e cada partícula emitida cai no tabuleiro. O tabuleiro cheio dá nome ao <b>canal exclusivo</b>, como (n,2n); os fotões não contam. O motor dá a cada canal a sua própria secção eficaz (a sua probabilidade, como uma área efetiva do alvo).</p>
  <div class="btns"><button class="btn ghost" data-act="next">Canal seguinte</button></div>
  <p>Percorre-os. (n,np) reproduz-se duas vezes, primeiro com o neutrão e depois com o protão: a mesma casa, o mesmo tabuleiro, um só canal. Depois, um deuterão fantasma (um protão e um neutrão ligados) chega a essa casa num só salto: o seu tabuleiro diz d, outro canal, (n,d).</p>
</div>
<div class="step">
  <h3>Onde tudo acaba</h3>
  <p>Cada casa tem agora prateleiras: de tinta para o <b>estado fundamental</b>, verde (em duas casas) para um <b>isómero</b>, um estado excitado que vive o suficiente para contar como produto à parte. A altura do monte é a <b>produção residual</b>: quanto de cada núcleo as reações fabricaram.</p>
  <div class="ctl"><label for="cs-e2">Energia do neutrão</label><input id="cs-e2" type="range" data-bind="E" min="1" max="30" step="0.5" value="14"><output data-show="E" data-fmt="1"></output></div>
  <div class="btns"><button class="btn" data-act="fire">Lançar 200 reações</button></div>
  <p>Arrasta a energia: o lote seguinte usa-a e os montes antigos desvanecem-se. A produção afasta-se do ponto de partida à medida que podem sair mais partículas. Toda a história acaba numa prateleira, e uma medição por ativação vê exatamente estes montes: irradia-se uma amostra e depois contam-se os decaimentos de cada produto.</p>
  <div class="aside">No código: <code>emission/multiple.py</code> (o ciclo sobre núcleos e intervalos, a cascata γ), <code>emission/feeding.py</code> (grelhas e dados de entrada para cada núcleo da cadeia), <code>compound/continuum.py</code> (o decaimento de um intervalo), <code>emission/channels.py</code> (canais exclusivos, produção residual, ramos isoméricos), <code>emission/binary.py</code> (a contabilidade da primeira emissão).</div>
</div>`,
};
Object.assign(WT.L.labels, {
  // reaction names on the squares (unchanged in Portuguese)
  "(n,γ)": "(n,γ)", "(n,n′)": "(n,n′)", "(n,{#}n)": "(n,{#}n)", "(n,p)": "(n,p)", "(n,np)": "(n,np)", "(n,{#}np)": "(n,{#}np)",
  "(n,{#}p)": "(n,{#}p)", "(n,n{#}p)": "(n,n{#}p)", "(n,α)": "(n,α)", "(n,nα)": "(n,nα)",
  "compound": "composto", "target": "alvo",
  "N{#}": "N{#}", "N": "N", "N+{#}": "N+{#}", "Z": "Z", "Z{#}": "Z{#}",
  "neutron number →": "número de neutrões →",
  // scene 1
  "levels": "níveis",
  "Sₙ {#} MeV": "Sₙ {#} MeV", "Sₙ = {#} MeV": "Sₙ = {#} MeV",
  "ground": "fundamental",
  "residual": "residual", "residual (one neutron fewer)": "residual (um neutrão a menos)",
  "n threshold": "limiar n", "its neutron threshold": "o seu limiar de neutrões",
  "{#} MeV": "{#} MeV",
  "drop = neutron's kinetic energy": "descida = energia cinética do neutrão",
  "{#} % land above the threshold: a second neutron can leave": "{#} % caem acima do limiar: pode sair um segundo neutrão",
  "<{#} % land above the threshold: a second neutron can leave": "<{#} % caem acima do limiar: pode sair um segundo neutrão",
  "all land below the threshold: only photons remain": "todos caem abaixo do limiar: só restam fotões",
  "{#} % above threshold: (n,{#}n) possible": "{#} % acima do limiar: (n,{#}n) possível",
  "<{#} % above threshold: (n,{#}n) possible": "<{#} % acima do limiar: (n,{#}n) possível",
  "all below threshold: photons only": "todos abaixo do limiar: só fotões",
  // scene 2
  "incoming neutron: {#} MeV": "neutrão incidente: {#} MeV",
  "shade and % = where reactions end": "tom e % = onde terminam",
  "stream width = flow · shade and % = share of reactions that end in that nucleus": "largura = fluxo · tom e % = fração de reações que terminam nesse núcleo",
  // scene 3
  "residual (first step)": "residual (primeiro passo)",
  "daughter: n fewer": "filho: um n a menos", "daughter (one neutron fewer)": "filho (um neutrão a menos)",
  "now: {#}–{#} MeV": "agora: {#}–{#} MeV", "{#}–{#} MeV": "{#}–{#} MeV",
  "done: {#} left by proton or alpha, the rest sit on ground states": "feito: {#} saíram por protão ou alfa, o resto está em estados fundamentais",
  "done: everything sits on a ground state": "feito: tudo está num estado fundamental",
  "orange ball = reactions waiting in a bin · grey = settled on the ground state · pale bins = already emptied": "bola laranja = reações à espera · cinzento = no estado fundamental · intervalos pálidos = já esvaziados",
  // scene 4
  "collected": "recolhido",
  "tray: d": "tabuleiro: d",
  "a deuteron lands on the same square, but its tray reads d: channel (n,d)": "um deuterão chega à mesma casa, mas o seu tabuleiro diz d: canal (n,d)",
  "tray: n n  →  (n,{#}n)": "tabuleiro: n n  →  (n,{#}n)",
  "tray: n  →  (n,n′)": "tabuleiro: n  →  (n,n′)",
  "tray: p  →  (n,p)": "tabuleiro: p  →  (n,p)",
  "tray: n p  →  (n,np)": "tabuleiro: n p  →  (n,np)",
  "tray: n p  →  (n,np) · same square, same tray": "tabuleiro: n p  →  (n,np) · mesma casa, mesmo tabuleiro",
  "tray: a  →  (n,α)": "tabuleiro: a  →  (n,α)",
  "tray: n n n  →  (n,{#}n)": "tabuleiro: n n n  →  (n,{#}n)",
  "tray empty, only photons: (n,γ), capture": "tabuleiro vazio, só fotões: (n,γ), captura",
  "each emitted particle falls into the tray": "cada partícula emitida cai no tabuleiro",
  "no particle gets out: only photons": "não sai nenhuma partícula: só fotões",
  "incoming neutron: {#} MeV · channel {#} of {#}": "neutrão incidente: {#} MeV · canal {#} de {#}",
  // scene 5
  "isomer": "isómero",
  "batch of {#} at {#} MeV": "lote de {#} a {#} MeV",
  "ink shelf: ground state · green: isomer": "tinta: estado fundamental · verde: isómero",
  "ink shelf: ground state · green shelf: isomer · pile height = how much of that nucleus was made": "prateleira de tinta: fundamental · verde: isómero · altura = quanto se produziu desse núcleo",
});
