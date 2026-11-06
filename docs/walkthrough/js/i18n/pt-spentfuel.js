/* Portuguese (Português): spentfuel (O combustível irradiado, nuclídeo a nuclídeo) */
WT.L.ch.spentfuel = {
  num: "Lição 1", title: "O combustível irradiado, nuclídeo a nuclídeo", short: "Nuclídeo a nuclídeo",
  html: `
<div class="step">
  <h3>O que tem dentro</h3>
  <p>Uma tonelada de combustível de PWR um ano após a descarga (enriquecido a 4,2 %, 50 GWd/t): quase toda a massa é urânio, quase toda a atividade está em poucos quilogramas.</p>
</div>
<div class="step">
  <h3>Atividade ou radiotoxicidade</h3>
  <p>Os becquerels contam decaimentos; os sieverts pesam cada decaimento pelo dano se for ingerido, o que realça os emissores alfa.</p>
  <div class="btns"><button class="btn ghost" data-act="mA" aria-pressed="false">Atividade (Bq)</button> <button class="btn ghost" data-act="mT" aria-pressed="true">Radiotoxicidade (Sv)</button></div>
</div>
<div class="step">
  <h3>Quem domina e quando</h3>
  <p>Passe o cursor ou toque numa banda para a identificar; arraste ao longo do eixo do tempo para as ordenar.</p>
</div>
<div class="step">
  <h3>Reciclar o plutónio</h3>
  <p>O reprocessamento aos quatro anos retira o plutónio (e o urânio com ele). Quanto fica para trás?</p>
  <div class="btns"><span class="sf-k" style="font:600 13px var(--sans);color:var(--soft);margin-right:4px;align-self:center">Pu removido</span> <button class="btn ghost" data-act="pu0" aria-pressed="true">0 %</button> <button class="btn ghost" data-act="pu99" aria-pressed="false">99 %</button> <button class="btn ghost" data-act="pu999" aria-pressed="false">99,9 %</button></div>
</div>
<div class="step">
  <h3>Remover também os actinídeos menores</h3>
  <p>Retire também o amerício, o cúrio e o neptúnio: então é o 1 % ou o 0,1 % que fica que decide o tempo.</p>
  <div class="btns"><span class="sf-k" style="font:600 13px var(--sans);color:var(--soft);margin-right:4px;align-self:center">Pu removido</span> <button class="btn ghost" data-act="pu0" aria-pressed="true">0 %</button> <button class="btn ghost" data-act="pu99" aria-pressed="false">99 %</button> <button class="btn ghost" data-act="pu999" aria-pressed="false">99,9 %</button></div>
  <div class="btns"><span class="sf-k" style="font:600 13px var(--sans);color:var(--soft);margin-right:4px;align-self:center">Am, Cm, Np removidos</span> <button class="btn ghost" data-act="ma0" aria-pressed="true">0 %</button> <button class="btn ghost" data-act="ma99" aria-pressed="false">99 %</button> <button class="btn ghost" data-act="ma999" aria-pressed="false">99,9 %</button></div>
</div>`,
};

Object.assign(WT.L.labels, {
  "{#} g": "{#} g",
  "{#} kg": "{#} kg",
  "{#} million": "{#} milhão",
  "{#} years:": "{#} anos:",
  "{#} yr": "{#} anos",
  "{#}¹⁰ Bq": "{#}¹⁰ Bq",
  "{#}¹³ Bq": "{#}¹³ Bq",
  "{#}¹⁶ Bq": "{#}¹⁶ Bq",
  "activity": "atividade",
  "activity after {#} year (log scale)": "atividade após {#} ano (escala log.)",
  "Am{#}": "Am{#}",
  "Am{#} {#} %": "Am{#} {#} %",
  "below the ore after ≈ {#} years": "abaixo do minério após ≈ {#} anos",
  "Cm{#}": "Cm{#}",
  "computed · band height = share": "calculado · altura da banda = fração",
  "computed (Bateman decay, ICRP{#}) · band height = share of the total": "calculado (decaimento de Bateman, ICRP{#}) · altura da banda = fração do total",
  "Cs{#}": "Cs{#}",
  "drag along the time axis · hover a band": "arraste ao longo do eixo do tempo · passe sobre uma banda",
  "drag the time · tap a band": "arraste o tempo · toque numa banda",
  "I{#}": "I{#}",
  "inventory: OECD-NEA {#} ({#} %, {#} GWd/t) + computed fission products": "inventário: OCDE-NEA {#} ({#} %, {#} GWd/t) + produtos de fissão calculados",
  "mass": "massa",
  "mass (log scale)": "massa (escala log.)",
  "most of the {#} kg of fission products is stable; activity includes short-lived daughters": "a maior parte dos {#} kg de produtos de fissão é estável; a atividade inclui descendentes de vida curta",
  "NEA {#} + computed": "NEA {#} + calculado",
  "Np{#}": "Np{#}",
  "once-through": "ciclo aberto",
  "once-through (no recycling)": "ciclo aberto (sem reciclagem)",
  "ore: {#}×{#}⁵ Sv": "minério: {#}×{#}⁵ Sv",
  "other fission products": "outros produtos de fissão",
  "other FP": "outros PF",
  "other FP: mostly stable": "outros PF: quase todos estáveis",
  "Pu{#}": "Pu{#}",
  "Pu{#} {#} %": "Pu{#} {#} %",
  "radiotoxicity ÷ ore": "radiotoxicidade ÷ minério",
  "radiotoxicity if swallowed (Sv), relative to the ore": "radiotoxicidade por ingestão (Sv), relativa ao minério",
  "reprocessing at {#} yr": "reprocessamento aos {#} anos",
  "Sr{#}": "Sr{#}",
  "Sr{#} + Y{#}": "Sr{#} + Y{#}",
  "still above the ore after a million years": "ainda acima do minério após um milhão de anos",
  "Tc{#}": "Tc{#}",
  "the ore it came from: {#} t natural uranium + daughters = {#}×{#}⁵ Sv": "o minério de origem: {#} t de urânio natural + descendentes = {#}×{#}⁵ Sv",
  "then mostly Am{#} ({#} %)": "depois sobretudo Am{#} ({#} %)",
  "then mostly Np{#} ({#} %)": "depois sobretudo Np{#} ({#} %)",
  "then mostly Pb{#} + Po{#} ({#} %)": "depois sobretudo Pb{#} + Po{#} ({#} %)",
  "then mostly Pu{#} ({#} %)": "depois sobretudo Pu{#} ({#} %)",
  "then mostly Sr{#} + Y{#} ({#} %)": "depois sobretudo Sr{#} + Y{#} ({#} %)",
  "uranium": "urânio",
  "years after unloading (log scale) →": "anos após a descarga (escala log.) →",
});
