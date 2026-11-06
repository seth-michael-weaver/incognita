/* Portuguese (pt-PT): breeding (Regeneração de combustível) */
WT.L.ch.breeding = {
  num: "Lição 1", title: "Regeneração de combustível", short: "Regeneração",
  html: `
<div class="step">
  <h3>O fértil torna-se físsil</h3>
  <p>O urânio-238 quase não se cinde, mas pode capturar um neutrão. Dois decaimentos beta depois (de cada vez, um neutrão do núcleo transforma-se num protão), tornou-se plutónio-239, que se cinde facilmente. O tório-232 faz o mesmo e torna-se urânio-233.</p>
  <div class="btns"><button class="btn ghost" data-act="bcU" aria-pressed="true">Urânio-238</button> <button class="btn ghost" data-act="bcT" aria-pressed="false">Tório-232</button></div>
</div>
<div class="step">
  <h3>O balanço de neutrões</h3>
  <p>Cada neutrão absorvido no combustível físsil devolve <i>η</i> neutrões novos. Um tem de causar a fissão seguinte e alguns perdem-se; o que sobra pode regenerar combustível. Com urânio-235 e neutrões lentos formam-se apenas cerca de 0,6 núcleos físseis novos por cada um queimado.</p>
  <div class="btns"><button class="btn ghost" data-act="bfU5" aria-pressed="true">U-235</button> <button class="btn ghost" data-act="bfP9" aria-pressed="false">Pu-239</button> <button class="btn ghost" data-act="bfU3" aria-pressed="false">U-233</button></div>
  <div class="btns"><button class="btn ghost" data-act="bsT" aria-pressed="true">Neutrões lentos</button> <button class="btn ghost" data-act="bsF" aria-pressed="false">Neutrões rápidos</button></div>
</div>
<div class="step">
  <h3>Os neutrões rápidos regeneram</h3>
  <p>Para regenerar, um neutrão tem de continuar a cadeia e pelo menos outro tem de criar combustível novo, por isso <i>η</i> tem de ultrapassar 2 por mais do que as perdas. O plutónio-239 num reator rápido dá cerca de 2,4: margem de sobra.</p>
  <div class="ctl"><label for="br-l1">Neutrões perdidos</label><input id="br-l1" type="range" data-bind="L" data-instant min="0.05" max="0.8" step="0.01" value="0.2"><output data-show="L" data-fmt="2"></output></div>
</div>
<div class="step">
  <h3>Tório com neutrões lentos</h3>
  <p>Com neutrões lentos o plutónio-239 dá só cerca de 2,1, mas o urânio-233 dá 2,29. Essa margem permite a um reator de tório regenerar com neutrões lentos, se desperdiçar muito poucos. Baixa as perdas até ele regenerar.</p>
  <div class="ctl"><label for="br-l2">Neutrões perdidos</label><input id="br-l2" type="range" data-bind="L" data-instant min="0.05" max="0.8" step="0.01" value="0.35"><output data-show="L" data-fmt="2"></output></div>
</div>
<div class="step">
  <h3>Razão de conversão</h3>
  <p>A razão de conversão é o número de núcleos físseis criados por cada núcleo físsil queimado. Abaixo de 1 o combustível vai-se esgotando (um conversor, como os reatores de água atuais); acima de 1 o reator termina com mais combustível do que tinha no início (um regenerador).</p>
  <div class="btns"><button class="btn ghost" data-act="bfU5" aria-pressed="true">U-235</button> <button class="btn ghost" data-act="bfP9" aria-pressed="false">Pu-239</button> <button class="btn ghost" data-act="bfU3" aria-pressed="false">U-233</button></div>
  <div class="btns"><button class="btn ghost" data-act="bsT" aria-pressed="true">Neutrões lentos</button> <button class="btn ghost" data-act="bsF" aria-pressed="false">Neutrões rápidos</button></div>
</div>`,
};

Object.assign(WT.L.labels, {
  "illustration": "ilustração",
  // scene 1: the chain
  "{#} protons": "{#} protões",
  "{#} p": "{#} p",
  "fertile": "fértil",
  "fertile: barely splits": "fértil: quase não se cinde",
  "fissile": "físsil",
  "fissile: splits easily": "físsil: cinde-se facilmente",
  "+ n": "+ n",
  "catch": "captura",
  "{#} min": "{#} min",
  "{#} d": "{#} d",
  "e⁻": "e⁻",
  "electron": "eletrão",
  "antineutrino": "antineutrino",
  "{a} waiting: day {b}": "{a} à espera: dia {b}",
  "a batch of {a} waiting · day {b}": "um lote de {a} à espera · dia {b}",
  "{a} % now {b}": "{a} % já é {b}",
  "after {#} weeks, {#} % has become Pu{#}": "ao fim de {#} semanas, {#} % já é Pu{#}",
  "after {#} months, {#} % has become U{#}": "ao fim de {#} meses, {#} % já é U{#}",
  "slow step: Np{#}, half-life {#} d": "passo lento: Np{#}, meia-vida {#} d",
  "slow step: Pa{#}, half-life {#} d": "passo lento: Pa{#}, meia-vida {#} d",
  "the slow step is Np{#} (half-life {#} days)": "o passo lento é o Np{#} (meia-vida {#} dias)",
  "the slow step is Pa{#} (half-life {#} days)": "o passo lento é o Pa{#} (meia-vida {#} dias)",
  // scenes 2-4: the neutron budget
  "slow neutrons": "neutrões lentos",
  "fast neutrons": "neutrões rápidos",
  "next fission": "fissão seguinte",
  "next fission: keeps the chain going": "fissão seguinte: mantém a cadeia",
  "U{#} → Pu{#}": "U{#} → Pu{#}",
  "Th{#} → U{#}": "Th{#} → U{#}",
  "breeds: U{#} → Pu{#}": "regenera: U{#} → Pu{#}",
  "breeds: Th{#} → U{#}": "regenera: Th{#} → U{#}",
  "lost": "perdidos",
  "lost: water, steel, poisons, leakage": "perdidos: água, aço, venenos, fugas",
  "{a} per absorption": "{a} por absorção",
  "chain": "cadeia",
  "breed": "regenera",
  "η = {a}": "η = {a}",
  "η ≈ {a}": "η ≈ {a}",
  "{#}: breeding line": "{#}: limiar de regeneração",
  "neutrons per absorption": "neutrões por absorção",
  "neutrons out per neutron absorbed in the fuel": "neutrões emitidos por neutrão absorvido no combustível",
  "conversion ratio ≈ η − {#} − lost = {a}: breeds": "razão de conversão ≈ η − {#} − perdas = {a}: regenera",
  "conversion ratio ≈ η − {#} − lost = {a}: breeds, makes more fuel than it burns": "razão de conversão ≈ η − {#} − perdas = {a}: regenera, cria mais combustível do que queima",
  "conversion ratio ≈ η − {#} − lost = {a}: converts": "razão de conversão ≈ η − {#} − perdas = {a}: converte",
  "conversion ratio ≈ η − {#} − lost = {a}: converts, makes less fuel than it burns": "razão de conversão ≈ η − {#} − perdas = {a}: converte, cria menos combustível do que queima",
  // scene 5: conversion ratio
  "Th{#}": "Th{#}",
  "U{#} (fertile)": "U{#} (fértil)",
  "Th{#} (fertile)": "Th{#} (fértil)",
  "split": "cindidos",
  "split (fission products)": "cindidos (produtos de fissão)",
  "burned {a}": "queimados {a}",
  "made {a}": "criados {a}",
  "{a} · slow neutrons": "{a} · neutrões lentos",
  "{a} · fast neutrons": "{a} · neutrões rápidos",
  "conversion ratio {a}: a breeder": "razão de conversão {a}: um regenerador",
  "conversion ratio {a}: a converter": "razão de conversão {a}: um conversor",
});
