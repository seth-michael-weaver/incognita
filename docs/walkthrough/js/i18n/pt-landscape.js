/* Portuguese (pt-PT): landscape (a paisagem dos núcleos) */
WT.L.ch.landscape = {
  title: "A paisagem dos núcleos", short: "Paisagem",
  lead: "Todos os núcleos que alguém já produziu, num só mapa: 3338 até agora, e só 252 duram para sempre.",
  html: `
<div class="step">
  <h3>A carta de nuclídeos</h3>
  <p>Cada quadradinho é um núcleo que foi de facto observado numa experiência: os neutrões contam-se na horizontal, os protões na vertical. Os quadrados pálidos foram observados, mas a sua massa ainda não foi pesada, apenas estimada. Os quadrados <b>escuros</b> são os 252 que nunca decaem. Os restantes desfazem-se, os laranja num instante, os azuis só ao fim de anos. A linha <em style="font-style:normal;color:var(--proton);font-weight:600">vermelha</em> é o elemento que escolheres com o cursor: todos os seus isótopos conhecidos.</p>
  <div class="ctl"><label for="ls-z">Ver o elemento (protões Z)</label><input id="ls-z" type="range" data-bind="zSel" data-instant min="1" max="110" step="1" value="26"><output data-show="zSel" data-fmt="0"></output></div>
  <p class="ctl-result" id="ls-z-out" aria-live="polite"></p>
</div>
<div class="step">
  <h3>Energia de ligação ao longo da carta</h3>
  <p>Agora cada quadrado é colorido pela sua <b>energia de ligação por nucleão</b>, isto é, pela força com que cada neutrão ou protão é retido (Capítulo 3). Os núcleos estáveis estão ao longo de uma crista de ligação forte; afastando-se dela, com neutrões a mais ou protões a mais, a ligação diminui. A mais forte de todas é a do níquel-62. As linhas finas marcam os <b>números mágicos</b> (8, 20, 28, 50, 82, 126), onde os núcleos são especialmente bem ligados.</p>
</div>
<div class="step">
  <h3>Decaimento beta rumo à estabilidade</h3>
  <p>Os núcleos com o mesmo número total de nucleões (o mesmo <b>número de massa</b> A) ficam numa linha diagonal do mapa, mostrada a <em style="font-style:normal;color:var(--proton);font-weight:600">vermelho</em>. Começa com neutrões a mais, como os fragmentos de um núcleo de urânio dividido. No <b>decaimento beta</b>, um neutrão transforma-se num protão, e assim o núcleo avança uma casa ao longo da sua linha, em direção ao meio, mais fortemente ligado, vez após vez, até chegar à crista e parar. O pequeno gráfico mostra a mesma cadeia como um vale por onde o núcleo rola. Experimenta A = 137: a cadeia passa pelo césio-137, o produto de longa vida dos acidentes em reatores.</p>
  <div class="ctl"><label for="ls-a">Número de massa A</label><input id="ls-a" type="range" data-bind="aSel" data-instant min="8" max="250" step="1" value="137"><output data-show="aSel" data-fmt="0"></output></div>
  <p class="ctl-result" id="ls-a-out" aria-live="polite"></p>
</div>
<div class="step">
  <h3>Cobertura da INCOGNITA</h3>
  <p>O mesmo mapa, colorido pelo que a nossa biblioteca contém para cada núcleo. <em style="font-style:normal;color:var(--fission);font-weight:600">Verde</em>: avaliado a partir das suas ressonâncias medidas. Os restantes têm um ficheiro de modelo construído apenas pelo motor: <b>escuro</b> para estáveis ou de longa vida (nível A), <em style="font-style:normal;color:var(--accent);font-weight:600">azul</em> para mais de um dia (nível B), <em style="font-style:normal;color:var(--warm);font-weight:600">laranja</em> para os de vida mais curta (nível C). Os cinzentos não estão na biblioteca (sobretudo os núcleos mais leves, e alguns que o motor não consegue calcular).</p>
</div>`,
};

Object.assign(WT.L.labels, {
  "neutrons N →": "neutrões N →",
  "protons Z ↑": "protões Z ↑",
  "Fe: all its isotopes": "Fe: todos os seus isótopos",
  "stable": "estável",
  "lives years": "vive anos",
  "gone in a blink": "some num instante",
  "red: Fe (your pick)": "vermelho: Fe (a tua escolha)",
  "nickel{#}: most tightly bound": "níquel{#}: o mais ligado",
  "held most tightly": "o mais ligado",
  "middle": "intermédio",
  "held least": "o menos ligado",
  "red: the A = {#} chain": "vermelho: a cadeia A = {#}",
  "A = {#}: deeper = more tightly bound": "A = {#}: mais fundo = mais ligado",
  "protons Z →": "protões Z →",
  "measured resonances": "ressonâncias medidas",
  "tier A": "nível A",
  "tier B": "nível B",
  "tier C": "nível C",
  "not in library": "fora da biblioteca",
});
