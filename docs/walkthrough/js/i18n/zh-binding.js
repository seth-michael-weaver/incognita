/* Simplified Chinese: binding (第 3 章，为什么原子核能聚在一起) */
WT.L.ch.binding = {
  num: "第 3 章", title: "原子核为什么能聚在一起", short: "结合能",
  html: `
<div class="step">
  <p>曲线上越高，结合得越紧。每个点对应一个质量数 A（质子数加中子数），其高度是把该原子核完全拆开时、平均每个核子所需的能量。拖动 A 并读出标记点：曲线中部，即铁和镍附近，是最高点。</p>
  <div class="ctl"><label for="bi-a">质量数 A</label><input id="bi-a" type="range" data-bind="pick" data-instant min="2" max="260" step="1" value="56"><output data-show="pick" data-fmt="0"></output></div>
</div>
<div class="step">
  <p>让铀裂开：两块碎片在曲线上都比原来的铀更高，所以同样的核子结合得更紧，差额就以能量的形式放出。选择较轻的碎片；较重的碎片是 236 个核子中剩下的部分。</p>
  <div class="ctl"><label for="bi-f">较轻碎片的 A</label><input id="bi-f" type="range" data-bind="frag" data-instant min="70" max="118" step="1" value="95"><output data-show="frag" data-fmt="0"></output></div>
  <p class="ctl-result" id="bi-split-out" aria-live="polite"></p>
  <p>无论怎样分裂，大约都是 200 MeV：是燃烧一个燃料分子所得几电子伏特的数千万倍。</p>
</div>
<div class="step">
  <p>把两个轻核聚合成一个。如果新的原子核在曲线上更高，就会放出能量。越过峰值之后，聚合反而要消耗能量。</p>
  <div class="ctl"><label for="bi-u">每个轻核的 A</label><input id="bi-u" type="range" data-bind="fuse" data-instant min="2" max="60" step="1" value="2"><output data-show="fuse" data-fmt="0"></output></div>
  <p class="ctl-result" id="bi-fuse-out" aria-live="polite"></p>
</div>`,
};
