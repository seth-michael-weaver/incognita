/* Portuguese (pt-PT): products (Capítulo 14, produtos de fissão e calor de decaimento) */
WT.L.ch.products = {
  num: "Capítulo 14", title: "Produtos de fissão e calor de decaimento", short: "Produtos de fissão",
  html: `
<div class="step">
  <p>Os pedaços são desiguais: um leve, um pesado. O gráfico mostra, para cada massa de fragmento A (protões mais neutrões), a fração de fissões que a produz. Duas bossas: pedaços leves perto de A = 95, pesados perto de 139. Uma divisão igual, perto de A = 117, é cerca de cem vezes mais rara.</p>
  <p>Cada linha tracejada é dez vezes mais alta do que a de baixo, para que as massas raras ainda se vejam. Toca numa barra ou arrasta o cursor: por baixo estão os dois pedaços dessa divisão. As suas massas somam 234, e não 236 (urânio-235 mais o neutrão), porque cerca de 2,4 neutrões também saem disparados.</p>
  <div class="ctl"><label for="pr-a">A do fragmento leve</label><input id="pr-a" type="range" data-bind="pick" data-instant min="70" max="117" step="1" value="95"><output data-show="pick" data-fmt="0"></output></div>
</div>
<div class="step">
  <p>Os seus decaimentos continuam a aquecer o combustível depois da paragem. Os fragmentos são radioativos: decaem um após outro, e cada decaimento liberta calor, quer a reação em cadeia continue ou não.</p>
  <div class="ctl"><label for="pr-t">Tempo após a paragem</label><input id="pr-t" type="range" data-bind="lgt" data-instant min="0" max="8.5" step="0.01" value="0"><output id="pr-tout">1 s</output></div>
  <p>Arrasta o tempo. Um segundo depois de o reator parar, os decaimentos ainda dão cerca de 6 % da potência total; ao fim de um dia, cerca de meio por cento; ao fim de um ano, algumas centésimas de por cento, ainda quase um megawatt num reator grande. É por isso que o combustível usado fica anos em piscinas de arrefecimento. A curva é a regra empírica de Way–Wigner: uma fórmula simples para os decaimentos de todos os fragmentos em conjunto, após um ano de funcionamento. As duas escalas saltam por um fator de dez em cada marca.</p>
</div>`,
};
