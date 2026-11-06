/* Portuguese (pt-PT): dose (Dose de radiação) */
WT.L.ch.dose = {
  num: "Lição 3", title: "Dose de radiação", short: "Dose",
  html: `
<div class="step">
  <h3>O que mede um sievert</h3>
  <p>A dose começa por ser energia absorvida por quilograma de corpo. O <b>sievert</b> pondera depois essa energia pelo dano que causa: a mesma energia entregue por partículas alfa conta vinte vezes mais do que por raios gama, porque fica concentrada em poucos rastos densos.</p>
  <div class="btns"><button class="btn ghost" data-act="rg" aria-pressed="true">Raios gama</button><button class="btn ghost" data-act="ra" aria-pressed="false">Partículas alfa</button></div>
</div>
<div class="step">
  <h3>Doses do dia a dia</h3>
  <p>Cada marca desta torre vale dez vezes a de baixo. Arrasta a conta luminosa para comparar: uma TAC ao tórax é a dose de muitos milhares de bananas, um ano de radiação natural a de algumas dezenas de voos.</p>
  <div class="ctl"><label for="ds-l">Dose</label><input id="ds-l" type="range" data-bind="ld" data-instant min="-7" max="1" step="0.02" value="-2.15"><output class="ds-out"></output></div>
</div>
<div class="step">
  <h3>Soma o teu ano</h3>
  <p>Toda a gente recebe da natureza cerca de 2,4 milisieverts por ano, sobretudo do radão, um gás que sai do solo. Junta os teus voos, exames e altitude.</p>
  <div class="ctl"><label for="ds-f">Voos transatlânticos</label><input id="ds-f" type="range" data-bind="fl" data-instant min="0" max="40" step="1" value="4"><output data-show="fl" data-fmt="0"></output></div>
  <div class="ctl"><label for="ds-ct">TAC ao tórax</label><input id="ds-ct" type="range" data-bind="ct" data-instant min="0" max="3" step="1" value="0"><output data-show="ct" data-fmt="0"></output></div>
  <div class="ctl"><label for="ds-h">Altitude da tua casa (m)</label><input id="ds-h" type="range" data-bind="alt" data-instant min="0" max="3500" step="50" value="300"><output data-show="alt" data-fmt="0"></output></div>
</div>
<div class="step">
  <h3>Uma dose grande de uma só vez</h3>
  <p>Abaixo de cerca de 100 milisieverts, qualquer risco adicional de cancro é pequeno demais para se medir; as regras de segurança assumem que cresce em proporção da dose. Por volta de um sievert de uma só vez, as células são atingidas tantas vezes que começa a doença da radiação.</p>
  <div class="ctl"><label for="ds-a">Dose de uma só vez</label><input id="ds-a" type="range" data-bind="la" data-instant min="-3" max="1" step="0.02" value="-1"><output class="ds-out2"></output></div>
</div>`,
};

Object.assign(WT.L.labels, {
  /* step 1: tissue */
  "cell nuclei in a patch of body": "núcleos celulares num pedaço do corpo",
  "cell nuclei in a patch of body tissue": "núcleos celulares num pedaço de tecido",
  "{#} milligray of alpha: a few cells hit hard": "{#} miligray de alfa: poucas células, muito atingidas",
  "{#} milligray of gamma: about one track per cell": "{#} miligray de gama: cerca de um rasto por célula",
  "same energy · counts as {#} millisieverts": "mesma energia · conta como {#} milisieverts",
  "counts as {#} millisievert": "conta como {#} milisievert",
  "illustration": "ilustração",
  /* step 2: the ladder */
  "{#} µSv": "{#} µSv",
  "{#} mSv": "{#} mSv",
  "{#} Sv": "{#} Sv",
  "eating a banana  ·  {#} µSv": "comer uma banana  ·  {#} µSv",
  "dental X-ray  ·  {#} µSv": "radiografia dentária  ·  {#} µSv",
  "chest X-ray  ·  {#} µSv": "radiografia ao tórax  ·  {#} µSv",
  "flight across the Atlantic  ·  {#} µSv": "voo transatlântico  ·  {#} µSv",
  "a year of natural background  ·  {#} mSv": "um ano de radiação natural  ·  {#} mSv",
  "chest CT scan  ·  {#} mSv": "TAC ao tórax  ·  {#} mSv",
  "yearly limit for radiation workers  ·  {#} mSv": "limite anual dos trabalhadores expostos  ·  {#} mSv",
  "a year on the Kerala coast (high spots)  ·  {#} mSv": "um ano na costa de Kerala (pontos altos)  ·  {#} mSv",
  "a year in the highest Ramsar homes  ·  {#} mSv": "um ano nas casas mais expostas de Ramsar  ·  {#} mSv",
  "at once: radiation sickness begins  ·  {#} Sv": "de uma vez: começa a doença da radiação  ·  {#} Sv",
  "at once: about half die untreated  ·  {#} Sv": "de uma vez: metade morre sem tratamento  ·  {#} Sv",
  "banana  ·  {#} µSv": "banana  ·  {#} µSv",
  "Atlantic flight  ·  {#} µSv": "voo Atlântico  ·  {#} µSv",
  "{#} yr background  ·  {#} mSv": "{#} ano natural  ·  {#} mSv",
  "chest CT  ·  {#} mSv": "TAC tórax  ·  {#} mSv",
  "worker limit/yr  ·  {#} mSv": "limite trab./ano  ·  {#} mSv",
  "Kerala, {#} yr  ·  {#} mSv": "Kerala, {#} ano  ·  {#} mSv",
  "Ramsar, {#} yr  ·  {#} mSv": "Ramsar, {#} ano  ·  {#} mSv",
  "{#} Sv at once  ·  {#} Sv": "{#} Sv de uma vez  ·  {#} Sv",
  "{#}–{#} Sv at once  ·  {#} Sv": "{#}–{#} Sv de uma vez  ·  {#} Sv",
  "{#} µSv: the dose of {#} bananas": "{#} µSv: a dose de {#} bananas",
  "{#} µSv: the dose of {#} thousand bananas": "{#} µSv: a dose de {#} mil bananas",
  "{#} µSv: {#} bananas, or {#} flights": "{#} µSv: {#} bananas, ou {#} voos",
  "{#} µSv: {#} thousand bananas, or {#} flights": "{#} µSv: {#} mil bananas, ou {#} voos",
  "{#} µSv: {#} million bananas, or {#} flights": "{#} µSv: {#} milhões de bananas, ou {#} voos",
  "{#} µSv: {#} bananas, or {#} thousand flights": "{#} µSv: {#} bananas, ou {#} mil voos",
  "{#} µSv: {#} thousand bananas, or {#} thousand flights": "{#} µSv: {#} mil bananas, ou {#} mil voos",
  "{#} µSv: {#} million bananas, or {#} thousand flights": "{#} µSv: {#} milhões de bananas, ou {#} mil voos",
  "{#} mSv: {#} bananas, or {#} flights": "{#} mSv: {#} bananas, ou {#} voos",
  "{#} mSv: {#} thousand bananas, or {#} flights": "{#} mSv: {#} mil bananas, ou {#} voos",
  "{#} mSv: {#} million bananas, or {#} flights": "{#} mSv: {#} milhões de bananas, ou {#} voos",
  "{#} mSv: {#} bananas, or {#} thousand flights": "{#} mSv: {#} bananas, ou {#} mil voos",
  "{#} mSv: {#} thousand bananas, or {#} thousand flights": "{#} mSv: {#} mil bananas, ou {#} mil voos",
  "{#} mSv: {#} million bananas, or {#} thousand flights": "{#} mSv: {#} milhões de bananas, ou {#} mil voos",
  "{#} Sv: {#} bananas, or {#} flights": "{#} Sv: {#} bananas, ou {#} voos",
  "{#} Sv: {#} thousand bananas, or {#} flights": "{#} Sv: {#} mil bananas, ou {#} voos",
  "{#} Sv: {#} million bananas, or {#} flights": "{#} Sv: {#} milhões de bananas, ou {#} voos",
  "{#} Sv: {#} bananas, or {#} thousand flights": "{#} Sv: {#} bananas, ou {#} mil voos",
  "{#} Sv: {#} thousand bananas, or {#} thousand flights": "{#} Sv: {#} mil bananas, ou {#} mil voos",
  "{#} Sv: {#} million bananas, or {#} thousand flights": "{#} Sv: {#} milhões de bananas, ou {#} mil voos",
  "{#} µSv: {#} bananas, {#} flights or {#} years of background": "{#} µSv: {#} bananas, {#} voos ou {#} anos de radiação natural",
  "{#} µSv: {#} thousand bananas, {#} flights or {#} years of background": "{#} µSv: {#} mil bananas, {#} voos ou {#} anos de radiação natural",
  "{#} µSv: {#} million bananas, {#} flights or {#} years of background": "{#} µSv: {#} milhões de bananas, {#} voos ou {#} anos de radiação natural",
  "{#} µSv: {#} bananas, {#} thousand flights or {#} years of background": "{#} µSv: {#} bananas, {#} mil voos ou {#} anos de radiação natural",
  "{#} µSv: {#} thousand bananas, {#} thousand flights or {#} years of background": "{#} µSv: {#} mil bananas, {#} mil voos ou {#} anos de radiação natural",
  "{#} µSv: {#} million bananas, {#} thousand flights or {#} years of background": "{#} µSv: {#} milhões de bananas, {#} mil voos ou {#} anos de radiação natural",
  "{#} mSv: {#} bananas, {#} flights or {#} years of background": "{#} mSv: {#} bananas, {#} voos ou {#} anos de radiação natural",
  "{#} mSv: {#} thousand bananas, {#} flights or {#} years of background": "{#} mSv: {#} mil bananas, {#} voos ou {#} anos de radiação natural",
  "{#} mSv: {#} million bananas, {#} flights or {#} years of background": "{#} mSv: {#} milhões de bananas, {#} voos ou {#} anos de radiação natural",
  "{#} mSv: {#} bananas, {#} thousand flights or {#} years of background": "{#} mSv: {#} bananas, {#} mil voos ou {#} anos de radiação natural",
  "{#} mSv: {#} thousand bananas, {#} thousand flights or {#} years of background": "{#} mSv: {#} mil bananas, {#} mil voos ou {#} anos de radiação natural",
  "{#} mSv: {#} million bananas, {#} thousand flights or {#} years of background": "{#} mSv: {#} milhões de bananas, {#} mil voos ou {#} anos de radiação natural",
  "{#} Sv: {#} bananas, {#} flights or {#} years of background": "{#} Sv: {#} bananas, {#} voos ou {#} anos de radiação natural",
  "{#} Sv: {#} thousand bananas, {#} flights or {#} years of background": "{#} Sv: {#} mil bananas, {#} voos ou {#} anos de radiação natural",
  "{#} Sv: {#} million bananas, {#} flights or {#} years of background": "{#} Sv: {#} milhões de bananas, {#} voos ou {#} anos de radiação natural",
  "{#} Sv: {#} bananas, {#} thousand flights or {#} years of background": "{#} Sv: {#} bananas, {#} mil voos ou {#} anos de radiação natural",
  "{#} Sv: {#} thousand bananas, {#} thousand flights or {#} years of background": "{#} Sv: {#} mil bananas, {#} mil voos ou {#} anos de radiação natural",
  "{#} Sv: {#} million bananas, {#} thousand flights or {#} years of background": "{#} Sv: {#} milhões de bananas, {#} mil voos ou {#} anos de radiação natural",
  "typical values": "valores típicos",
  /* step 3: your year */
  "average {#}": "média {#}",
  "world average {#} mSv": "média mundial {#} mSv",
  "worker limit {#}": "limite trab. {#}",
  "worker limit {#} mSv": "limite dos trabalhadores {#} mSv",
  "radon in the air  {#}": "radão no ar  {#}",
  "radon  {#}": "radão  {#}",
  "rocks and soil  {#}": "rochas e solo  {#}",
  "ground  {#}": "solo  {#}",
  "food and water  {#}": "comida e água  {#}",
  "food  {#}": "comida  {#}",
  "cosmic rays at {#} m  {#}": "raios cósmicos a {#} m  {#}",
  "cosmic rays  {#}": "raios cósmicos  {#}",
  "cosmic  {#}": "cósmica  {#}",
  "{#} flights  {#}": "{#} voos  {#}",
  "flights  {#}": "voos  {#}",
  "{#} chest CT  {#}": "{#} TAC ao tórax  {#}",
  "CT  {#}": "TAC  {#}",
  "mSv": "mSv",
  "your year: {#} mSv": "o teu ano: {#} mSv",
  "more than the yearly worker limit": "mais do que o limite anual dos trabalhadores",
  "{#} times the world average": "{#} vezes a média mundial",
  "close to the world average": "perto da média mundial",
  /* step 4: dose at once */
  "tracks through each cell nucleus: about {#}": "rastos por núcleo celular: cerca de {#}",
  "tracks through each cell nucleus: about {#} (a few drawn)": "rastos por núcleo celular: cerca de {#} (alguns desenhados)",
  "tracks through each cell nucleus: about {#} thousand (a few drawn)": "rastos por núcleo celular: cerca de {#} mil (alguns desenhados)",
  "no effect seen": "sem efeito observado",
  "risk assumed": "risco assumido",
  "small added risk assumed": "assume-se um pequeno risco adicional",
  "sickness": "doença",
  "lethal": "letal",
  "often lethal": "muitas vezes letal",
  "{#} µSv at once: any extra risk too small to measure": "{#} µSv de uma vez: risco adicional pequeno demais para se medir",
  "{#} mSv at once: any extra risk too small to measure": "{#} mSv de uma vez: risco adicional pequeno demais para se medir",
  "{#} mSv at once: no sickness; risk assumed to rise with dose": "{#} mSv de uma vez: sem doença; assume-se que o risco cresce com a dose",
  "{#} Sv at once: no sickness; risk assumed to rise with dose": "{#} Sv de uma vez: sem doença; assume-se que o risco cresce com a dose",
  "{#} Sv at once: radiation sickness: nausea, low blood counts": "{#} Sv de uma vez: doença da radiação, náuseas, queda das células sanguíneas",
  "{#} Sv at once: about half die without treatment": "{#} Sv de uma vez: cerca de metade morre sem tratamento",
});
