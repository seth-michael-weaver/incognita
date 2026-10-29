/* Japanese: slowing (第19章、中性子の減速) */
WT.L.ch.slowing = {
  num: "第19章", title: "中性子の減速", short: "減速",
  html: `
<div class="step">
  <p>水素に1回はね返されるたびに、エネルギーはおよそ半分になります。核分裂中性子は2 MeVで出発し、水の中ではね返りながら進みます。水素の原子核は中性子とほぼ同じ質量なので、ビリヤードの球と同じように、1回の衝突で平均して中性子のエネルギーの半分を渡します。</p>
  <p>グラフは、衝突のたびの中性子のエネルギーを描いています。横に並んだ目盛りは、1つ下がるごとにエネルギーが1000分の1になります。毎回同じ割合を失うので、破線のようにまっすぐ滑り降ります。約18回の衝突で中性子は0.025 eVの<b>熱</b>エネルギーに達し、そこでは温かい水が中性子を減速させるのと同じ頻度で加速させます。酸素は16倍重く、1回の衝突で奪うエネルギーはわずかなので、100回以上必要です。</p>
  <div class="btns"><button class="btn ghost" data-act="tgtH" aria-pressed="true">水素</button><button class="btn ghost" data-act="tgtO" aria-pressed="false">酸素</button><button class="btn" data-act="again">もう一度撃つ</button></div>
</div>
<div class="step">
  <p>約1 eV以下では、分子の結合が各衝突を左右します。水素はそれぞれ酸素につながっています（明るい線）。遅い中性子はもはや自由な水素に当たるのではなく、18倍重い分子全体に当たるので、単純な衝突ではほとんどエネルギーを奪えません。</p>
  <p>分子を回転させたり振動させたりすることもできますが、渡せるのは0.06、0.2、0.45 eVという決まった量ずつだけです（明るい閃光）。温かい分子は、こうした量を中性子に返すこともあります。グラフの1 eV以下の影をつけた帯が、これが効く領域です。結合を切ると、自由な水素との違いを比べられます。</p>
  <div class="btns"><button class="btn ghost" data-act="bind" aria-pressed="true">化学結合</button><button class="btn" data-act="again">もう一度撃つ</button></div>
</div>
<div class="step">
  <p>計算コードにはこれらすべてが表として必要です。それが<b>散乱則</b>という地図です。横軸は衝突の強さα（分子に渡される運動量で、かすめる程度なら小さく、正面衝突なら大きい）。縦軸は中性子が得る（上）または失う（下）エネルギーβで、水の熱エネルギー0.025 eVを単位に数えます。明るいほど起こりやすく、淡いほどまれです。</p>
  <p>輪郭は、選んだエネルギーの中性子が到達できる範囲です。もっているエネルギー以上は失えず、エネルギー変化ごとに可能な衝突の強さも限られます。エネルギーをドラッグすると輪郭は広がったり縮んだりします。結合がなければ地図は自由な水素ガスで、破線の反跳線に沿って明るい尾根が1本あるだけです。結合があると、分子の決まったエネルギー量が明るい縞として加わります。INCOGNITAは水とベリリウムについて独自の散乱則を計算しています：<a href="https://github.com/seth-michael-weaver/incognita/tree/main/library/tsl-v0.1" style="white-space:nowrap">tsl-v0.1</a>。</p>
  <div class="ctl"><label for="slo-e">中性子のエネルギー（eV）</label><input id="slo-e" type="range" data-bind="lgE" data-instant min="-2.3" max="0" step="0.01" value="-1"><output data-show="Eshow" data-fmt="3"></output></div>
  <div class="btns"><button class="btn ghost" data-act="bind" aria-pressed="true">化学結合</button></div>
</div>`,
};
/* attributes referenced in the English chapter script (for the structure check): data-act="${act}" */
