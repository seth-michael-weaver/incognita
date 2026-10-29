/* Russian: binding (Глава 3, почему ядра держатся вместе) */
WT.L.ch.binding = {
  num: "Глава 3", title: "Почему ядра держатся вместе", short: "Связь",
  html: `
<div class="step">
  <p>Чем выше точка на кривой, тем прочнее связь. Каждая точка — одно массовое число A (число протонов плюс нейтронов), а её высота — энергия, которую нужно затратить в расчёте на один нуклон, чтобы полностью разобрать это ядро. Перемещайте A и следите за маркером: вершина кривой приходится на середину, около железа и никеля.</p>
  <div class="ctl"><label for="bi-a">Массовое число A</label><input id="bi-a" type="range" data-bind="pick" data-instant min="2" max="260" step="1" value="56"><output data-show="pick" data-fmt="0"></output></div>
</div>
<div class="step">
  <p>Разделите уран: оба осколка лежат на кривой выше, чем породивший их уран, то есть те же нуклоны оказываются связаны прочнее, а разность выделяется в виде энергии. Выберите более лёгкий осколок; более тяжёлый — это остаток из 236 нуклонов.</p>
  <div class="ctl"><label for="bi-f">Более лёгкий осколок A</label><input id="bi-f" type="range" data-bind="frag" data-instant min="70" max="118" step="1" value="95"><output data-show="frag" data-fmt="0"></output></div>
  <p class="ctl-result" id="bi-split-out" aria-live="polite"></p>
  <p>При любом способе деления выходит около 200 MeV: в десятки миллионов раз больше нескольких электронвольт, которые даёт сгорание одной молекулы топлива.</p>
</div>
<div class="step">
  <p>Соедините два лёгких ядра в одно. Если новое ядро лежит на кривой выше, энергия выделяется. За вершиной слияние, наоборот, требует затрат энергии.</p>
  <div class="ctl"><label for="bi-u">A каждого лёгкого ядра</label><input id="bi-u" type="range" data-bind="fuse" data-instant min="2" max="60" step="1" value="2"><output data-show="fuse" data-fmt="0"></output></div>
  <p class="ctl-result" id="bi-fuse-out" aria-live="polite"></p>
</div>`,
};
