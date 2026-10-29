/* Portuguese (pt-PT): binding (Capítulo 3, energia de ligação) */
WT.L.ch.binding = {
  num: "Capítulo 3", title: "Porque é que os núcleos se mantêm unidos", short: "Ligação",
  html: `
<div class="step">
  <p>Mais alto na curva significa mais fortemente ligado. Cada ponto é um número de massa A (o número de protões mais neutrões), e a sua altura é a energia necessária, por nucleão, para separar completamente esse núcleo. Arrasta A e leia o marcador: o meio da curva, à volta do ferro e do níquel, é o topo.</p>
  <div class="ctl"><label for="bi-a">Número de massa A</label><input id="bi-a" type="range" data-bind="pick" data-instant min="2" max="260" step="1" value="56"><output data-show="pick" data-fmt="0"></output></div>
</div>
<div class="step">
  <p>Divide o urânio: os dois pedaços ficam mais acima na curva do que o urânio de onde vieram, de modo que os mesmos nucleões acabam mais fortemente ligados e a diferença sai como energia. Escolhe o fragmento mais leve; o mais pesado é o resto dos 236 nucleões.</p>
  <div class="ctl"><label for="bi-f">A do fragmento mais leve</label><input id="bi-f" type="range" data-bind="frag" data-instant min="70" max="118" step="1" value="95"><output data-show="frag" data-fmt="0"></output></div>
  <p class="ctl-result" id="bi-split-out" aria-live="polite"></p>
  <p>Seja qual for a divisão, são cerca de 200 MeV: dezenas de milhões de vezes os poucos eletrão-volts que a queima de uma molécula de combustível dá.</p>
</div>
<div class="step">
  <p>Junta dois núcleos leves num só. Se o novo núcleo ficar mais acima na curva, é libertada energia. Depois do máximo, juntar custa energia.</p>
  <div class="ctl"><label for="bi-u">A de cada núcleo leve</label><input id="bi-u" type="range" data-bind="fuse" data-instant min="2" max="60" step="1" value="2"><output data-show="fuse" data-fmt="0"></output></div>
  <p class="ctl-result" id="bi-fuse-out" aria-live="polite"></p>
</div>`,
};
