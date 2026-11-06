/* Portuguese (pt-PT): halflife (Radioatividade e meia-vida) */
WT.L.ch.halflife = {
  num: "Lição 1", title: "Radioatividade e meia-vida", short: "Meia-vida",
  lead: "Alguns átomos são instáveis: mais cedo ou mais tarde o seu núcleo rebenta, emite radiação e transforma-se noutra coisa. Ninguém sabe dizer quando é que um deles vai, mas uma amostra inteira segue um relógio pelo qual se pode acertar o teu.",
  html: `
<div class="step">
  <h3>Uma amostra que rebenta ao acaso</h3>
  <p>Cada bola brilhante é um núcleo instável. Qualquer uma pode rebentar a qualquer momento, lançando um clarão de radiação e ficando um átomo calmo e estável. Toca numa para a fazer rebentar.</p>
  <div class="btns"><button class="btn" data-act="refill">Amostra nova</button></div>
</div>
<div class="step">
  <h3>Metade, e depois metade outra vez</h3>
  <p>Ninguém sabe dizer qual será a próxima, mas o conjunto é previsível: ao fim de uma <b>meia-vida</b> resta cerca de metade, ao fim de duas um quarto, depois um oitavo. Torna a meia-vida mais longa ou mais curta.</p>
  <div class="ctl"><label for="hl-th">Meia-vida (segundos)</label><input id="hl-th" type="range" data-bind="Th" data-instant min="1" max="8" step="0.5" value="3"><output data-show="Th" data-fmt="1"></output></div>
  <div class="btns"><button class="btn ghost" data-act="refill">Amostra nova</button></div>
</div>
<div class="step">
  <h3>Os núcleos não têm memória</h3>
  <p>Segue um sobrevivente. Por muito que já tenha durado, a sua probabilidade de durar mais uma meia-vida continua a ser de uma em duas: um núcleo não envelhece.</p>
  <div class="btns"><button class="btn ghost" data-act="tag">Seguir outro</button><button class="btn ghost" data-act="refill">Amostra nova</button></div>
</div>
<div class="step">
  <h3>Meias-vidas reais</h3>
  <p>Os isótopos reais vão de dias a milhares de milhões de anos. Nesta linha de tempo esticada, cada um cai por uma falésia na sua própria meia-vida. Escolhe um e arrasta o tempo para a frente.</p>
  <div class="btns"><button class="btn ghost" data-act="iso0" aria-pressed="false">Iodo-131</button><button class="btn ghost" data-act="iso1" aria-pressed="true">Césio-137</button><button class="btn ghost" data-act="iso2" aria-pressed="false">Carbono-14</button><button class="btn ghost" data-act="iso3" aria-pressed="false">Urânio-238</button></div>
  <div class="ctl"><label for="hl-t1">Tempo decorrido</label><input id="hl-t1" type="range" data-bind="lt" data-instant min="3" max="17.8" step="0.02" value="8.98"><output class="hl-tout"></output></div>
</div>
<div class="step">
  <h3>Atividade: desintegrações por segundo</h3>
  <p>Um grama de cada, lado a lado. Uma meia-vida curta significa muitas desintegrações por segundo, mas não por muito tempo; uma meia-vida longa brilha fracamente durante eras. Arrasta o tempo e vê as lâmpadas apagarem-se uma a uma.</p>
  <div class="ctl"><label for="hl-t2">Tempo decorrido</label><input id="hl-t2" type="range" data-bind="lt" data-instant min="3" max="17.8" step="0.02" value="4.94"><output class="hl-tout"></output></div>
</div>`,
};

Object.assign(WT.L.labels, {
  /* live sample */
  "survived {#} half-lives": "sobreviveu {#} meias-vidas",
  "chance to last one more: {#} in {#}": "hipótese de durar mais uma: {#} em {#}",
  "survived {#} half-lives · still {#} in {#}": "sobreviveu {#} meias-vidas · ainda {#} em {#}",
  "it popped: follow another": "desintegrou-se: segue outro",
  "{#} of {#} still unstable": "{#} de {#} ainda instáveis",
  "1 half-life": "1 meia-vida",
  "{#} half-life": "{#} meia-vida",
  "half-lives →": "meias-vidas →",
  "nuclei left": "núcleos restantes",
  "{#} of {#} left · half-life {#} s": "restam {#} de {#} · meia-vida {#} s",
  "every survivor has the same 1-in-2 chance per half-life": "cada sobrevivente tem a mesma hipótese, 1 em 2, por meia-vida",
  "every survivor has the same {#}-in{#} chance per half-life": "cada sobrevivente tem a mesma hipótese, {#} em {#}, por meia-vida",
  "illustrative half-life": "meia-vida ilustrativa",
  /* time axis ticks */
  "{#} hour": "{#} hora",
  "{#} h": "{#} h",
  "{#} day": "{#} dia",
  "{#} d": "{#} d",
  "{#} year": "{#} ano",
  "{#} yr": "{#} anos",
  "1000 years": "1000 anos",
  "10³ yr": "10³ anos",
  "10⁶ yr": "10⁶ anos",
  "10⁹ yr": "10⁹ anos",
  "{#}³ yr": "{#}³ anos",
  "{#}⁶ yr": "{#}⁶ anos",
  "{#}⁹ yr": "{#}⁹ anos",
  "1 million years": "1 milhão de anos",
  "1 billion years": "mil milhões de anos",
  "drag": "arrastar",
  /* time strings (fmtT) */
  "{#} minutes": "{#} minutos",
  "{#} hours": "{#} horas",
  "{#} days": "{#} dias",
  "{#} months": "{#} meses",
  "{#} years": "{#} anos",
  "{#} thousand years": "{#} mil anos",
  "{#} million years": "{#} milhões de anos",
  "{#} billion years": "{#} mil milhões de anos",
  /* real isotopes */
  "iodine{#} · half-life {#} days": "iodo{#} · meia-vida {#} dias",
  "caesium{#} · half-life {#} years": "césio{#} · meia-vida {#} anos",
  "carbon{#} · half-life {#} years": "carbono{#} · meia-vida {#} anos",
  "carbon-14 · half-life 5,700 years": "carbono-14 · meia-vida 5700 anos",
  "uranium{#} · half-life {#} billion years": "urânio{#} · meia-vida {#} mil milhões de anos",
  "medicine, fission product": "medicina, produto de fissão",
  "fission product": "produto de fissão",
  "radiocarbon dating": "datação por radiocarbono",
  "natural uranium": "urânio natural",
  "all": "tudo",
  "{#} % left after {#} minutes": "resta {#} % ao fim de {#} minutos",
  "{#} % left after {#} hours": "resta {#} % ao fim de {#} horas",
  "{#} % left after {#} days": "resta {#} % ao fim de {#} dias",
  "{#} % left after {#} months": "resta {#} % ao fim de {#} meses",
  "{#} % left after {#} years": "resta {#} % ao fim de {#} anos",
  "{#} % left after {#} thousand years": "resta {#} % ao fim de {#} mil anos",
  "{#} % left after {#} million years": "resta {#} % ao fim de {#} milhões de anos",
  "{#} % left after {#} billion years": "resta {#} % ao fim de {#} mil milhões de anos",
  "under {#} % left after {#} minutes": "resta menos de {#} % ao fim de {#} minutos",
  "under {#} % left after {#} hours": "resta menos de {#} % ao fim de {#} horas",
  "under {#} % left after {#} days": "resta menos de {#} % ao fim de {#} dias",
  "under {#} % left after {#} months": "resta menos de {#} % ao fim de {#} meses",
  "under {#} % left after {#} years": "resta menos de {#} % ao fim de {#} anos",
  "under {#} % left after {#} thousand years": "resta menos de {#} % ao fim de {#} mil anos",
  "under {#} % left after {#} million years": "resta menos de {#} % ao fim de {#} milhões de anos",
  "under {#} % left after {#} billion years": "resta menos de {#} % ao fim de {#} mil milhões de anos",
  /* activity of one gram */
  "iodine{#}": "iodo{#}",
  "caesium{#}": "césio{#}",
  "carbon{#}": "carbono{#}",
  "uranium{#}": "urânio{#}",
  "½ {#} days": "½ {#} dias",
  "½ {#} years": "½ {#} anos",
  "½ 5,700 years": "½ 5700 anos",
  "½ {#} billion years": "½ {#} mil milhões de anos",
  "½ {#} bn years": "½ {#} mil M anos",
  "almost none": "quase nenhuma",
  "{#} /s": "{#} /s",
  "~{#} /s": "~{#} /s",
  "{#}×{#}¹ /s": "{#}×{#}¹ /s",
  "{#}×{#}² /s": "{#}×{#}² /s",
  "{#}×{#}³ /s": "{#}×{#}³ /s",
  "{#}×{#}⁴ /s": "{#}×{#}⁴ /s",
  "{#}×{#}⁵ /s": "{#}×{#}⁵ /s",
  "{#}×{#}⁶ /s": "{#}×{#}⁶ /s",
  "{#}×{#}⁷ /s": "{#}×{#}⁷ /s",
  "{#}×{#}⁸ /s": "{#}×{#}⁸ /s",
  "{#}×{#}⁹ /s": "{#}×{#}⁹ /s",
  "{#}×{#}¹⁰ /s": "{#}×{#}¹⁰ /s",
  "{#}×{#}¹¹ /s": "{#}×{#}¹¹ /s",
  "{#}×{#}¹² /s": "{#}×{#}¹² /s",
  "{#}×{#}¹³ /s": "{#}×{#}¹³ /s",
  "{#}×{#}¹⁴ /s": "{#}×{#}¹⁴ /s",
  "{#}×{#}¹⁵ /s": "{#}×{#}¹⁵ /s",
  "{#}×{#}¹⁶ /s": "{#}×{#}¹⁶ /s",
  "pops per second (log)": "desintegrações/s (log)",
  "pops per second, {#} gram (each line ×{#})": "desintegrações por segundo, {#} grama (cada linha ×{#})",
  "one gram of each, after {#} minutes": "um grama de cada, ao fim de {#} minutos",
  "one gram of each, after {#} hours": "um grama de cada, ao fim de {#} horas",
  "one gram of each, after {#} days": "um grama de cada, ao fim de {#} dias",
  "one gram of each, after {#} months": "um grama de cada, ao fim de {#} meses",
  "one gram of each, after {#} years": "um grama de cada, ao fim de {#} anos",
  "one gram of each, after {#} thousand years": "um grama de cada, ao fim de {#} mil anos",
  "one gram of each, after {#} million years": "um grama de cada, ao fim de {#} milhões de anos",
  "one gram of each, after {#} billion years": "um grama de cada, ao fim de {#} mil milhões de anos",
});
