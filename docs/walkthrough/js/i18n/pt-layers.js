/* Portuguese (pt-PT): layers (chapter 12). The scoreboard counts come from WT.board (js/scoreboard-data.js, loaded first), as in
 * js/ch/layers.js; a missing block or field drops the number, not the sentence. */
(function () {
  const B = WT.board || {};
  const nOf = (v) => (typeof v === "number" && isFinite(v) ? v : null);
  const tally = (o) => {
    if (!o) return null;
    const w = nOf(o.WIN), t = nOf(o.TIE), l = nOf(o.LOSS);
    if (w === null || t === null || l === null) return null;
    return { w, t, l, d: nOf(o.decided) ?? w + t + l };
  };
  const TE = tally(B.incognita), TT = tally(B.terra);
  const LIBS = B.terra && Array.isArray(B.terra.by_rival) ? B.terra.by_rival.map((r) => r && r.rival).filter((s) => typeof s === "string") : [];
  const ASOF = (() => {
    const m = /^(\d{4})-(\d{2})-(\d{2})$/.exec(B.asof || ""); if (!m) return null;
    const mes = ["janeiro", "fevereiro", "março", "abril", "maio", "junho", "julho", "agosto", "setembro", "outubro", "novembro", "dezembro"][+m[2] - 1];
    return mes ? `${+m[3]} de ${mes} de ${m[1]}` : null;
  })();
  const figs = (T) => (T ? `<div class="figs" aria-label="${T.w} vitórias, ${T.t} empates, ${T.l} derrotas"><div class="w"><b>${T.w}</b><span>vitória</span></div><div><b>${T.t}</b><span>empate</span></div><div class="l"><b>${T.l}</b><span>derrota</span></div></div>` : "");
  const libs = LIBS.length ? `as principais bibliotecas de dados avaliados (${LIBS.join(", ")})` : "as principais bibliotecas de dados avaliados";
  const engineScore = TE ? ` De ${TE.d} dessas comparações, fica claramente à frente em ${TE.w}, empata em ${TE.t} e fica atrás em ${TE.l}.` : "";
  const terraScore = TT ? `Face a ${libs}, fica à frente em ${TT.w} de ${TT.d} comparações, empata em ${TT.t} e fica atrás em ${TT.l}.` : `É comparado com ${libs}.`;

  WT.L.ch.layers = {
    num: "Capítulo 15", title: "Como o modelo se organiza em camadas", short: "Camadas",
    lead: "O que entregamos é construído em camadas por cima do motor, e cada camada tem de merecer o seu lugar face às medições.",
    html: `
<div class="step">
  <div class="layer-chip on">Em uso</div>
  <h3>Camada 1 · Uma regra para todos os núcleos</h3>
  <p>A linha azul é a previsão do motor para uma reação. O motor é a camada de baixo: a mesma física e as mesmas definições globais para todos os nuclídeos, sem nada ajustado às secções eficazes de um núcleo concreto.</p>
  <div class="btns"><button class="btn ghost" data-act="reveal" aria-pressed="false">Mostrar as medições</button></div>
  <p>É isso que o torna verificável, face às medições e face a outros códigos de modelos aplicados aos mesmos núcleos. Não é um teste às cegas: as definições globais foram escolhidas a observar estas mesmas comparações.${engineScore}</p>
  ${figs(TE)}
</div>
<div class="step">
  <div class="layer-chip null">Testada: ainda sem ganho</div>
  <h3>Camada 2 · As medições de cada núcleo</h3>
  <p>Esta camada troca a regra global pelos valores medidos de cada núcleo: o seu espaçamento de níveis D0, as suas funções de intensidade S0 e S1 (a facilidade com que absorve neutrões lentos), a sua largura gama média ⟨Γγ⟩ e os seus níveis de energia conhecidos.</p>
  <div class="btns"><button class="btn ghost" data-act="ms0" aria-pressed="true">Regra global</button><button class="btn ghost" data-act="ms1" aria-pressed="false">Medições próprias</button></div>
  <p>Liga-a e a linha quase não se mexe. Os testes até agora não encontraram um ganho global: a única variante que ajuda uma reação perto do seu limiar piora a captura de neutrões. Por isso esta camada fica desligada, por agora.</p>
</div>
<div class="step">
  <div class="layer-chip cand">Candidata</div>
  <h3>Camada 3 · Seguir os bons dados (TERRA)</h3>
  <p>Onde uma reação foi bem medida, a linha deve seguir as medições. A terceira camada, TERRA, faz passar a linha do motor pelos bons dados onde eles existem e volta ao motor onde não existem.</p>
  <div class="ctl"><label for="lay-cov">Parte da gama de energia medida (%)</label><input id="lay-cov" type="range" data-bind="cov" min="0" max="1" step="0.01" value="0.45"><output data-show="covPct" data-fmt="0"></output></div>
  <p>${terraScore} A maioria é dentro da amostra: o TERRA já viu essas medições, tal como as bibliotecas.</p>
  ${figs(TT)}
</div>
<div class="step">
  <div class="layer-chip wip">Em desenvolvimento</div>
  <h3>Camada 4 · Barras de erro honestas</h3>
  <p>A camada de cima põe à volta da linha uma banda que deveria conter o valor verdadeiro cerca de duas vezes em cada três (uma banda de 68 %): estreita onde os bons dados a fixam, mais larga onde não.</p>
  <div class="ctl"><label for="lay-band">Largura da banda · medições dentro (%)</label><input id="lay-band" type="range" data-bind="band" min="0.2" max="2.5" step="0.05" value="1"><output data-show="inside" data-fmt="0"></output></div>
  <p>Arrasta-a e conta as medições que ficam dentro. Demasiado estreita, e a banda promete uma precisão que não tem; demasiado larga, e não diz nada. A banda do próprio motor ainda não foi adotada: acerta quando se juntam todas as reações, mas ainda não em cada família de reações. O TERRA tem as suas próprias bandas, e estas fazem parte das comparações acima.</p>
</div>
<div class="step">
  <h3>Ponto da situação</h3>
  <p>Uma camada só é adotada depois de testada face às medições, e fica desligada se não ajudar. Hoje o motor está em uso e o TERRA é candidato; a camada de estrutura medida e a banda de incerteza do motor continuam em testes.</p>
  <p><a href="scoreboard.html" data-keep-lang>Ver o quadro de resultados completo →</a> Todas as comparações que não ganhamos, cada rival e como as ler.</p>
  <div class="aside">${ASOF ? `Resultados a ${ASOF}, do` : "Resultados do"} registo de investigação do projeto. As curvas da imagem são ilustrativas.</div>
</div>`,
  };
})();
Object.assign(WT.L.labels, {
  "{#} · engine": "{#} · motor",
  "{#} · measured structure": "{#} · estrutura medida",
  "{#} · TERRA: anchored to data": "{#} · TERRA: ancorado nos dados",
  "{#} · uncertainty band": "{#} · banda de incerteza",
  "measured here": "medido aqui",
  "neutron energy →": "energia do neutrão →",
  "how often the reaction happens": "com que frequência ocorre a reação",
  "hollow dots: measurements the engine is compared with": "pontos ocos: medições com que o motor é comparado",
  "own measured values: the line barely moves": "valores medidos próprios: a linha quase não se mexe",
  "global rule": "regra global",
  "no measurements: TERRA falls back to the engine": "sem medições: o TERRA volta ao motor",
  "solid: follows the data · dashed: the engine alone": "contínua: segue os dados · tracejada: só o motor",
  "{#} of {#} measurements inside the band (aim: about {#} %)": "{#} de {#} medições dentro da banda (objetivo: cerca de {#} %)",
  "no measurements to check the band against": "não há medições com que verificar a banda",
});
Object.assign(WT.L.ui, { nav_board: "Quadro de resultados" });
