/* Japanese: slowing (第19章、中性子の減速) */
WT.L.ch.slowing = {
  num: "第19章", title: "中性子の減速", short: "減速",
  html: `
<div class="step">
  <p>水素に1回はね返されるたびに、エネルギーはおよそ半分になります。核分裂中性子は2 MeVで出発し、水の中ではね返りながら進みます。水素の原子核は中性子とほぼ同じ質量なので、ビリヤードの球と同じように、1回の衝突で平均して中性子のエネルギーの半分を渡します。</p>
  <p>グラフは、衝突のたびの中性子のエネルギーを描いています。縦軸の目盛りは、1つ下がるごとにエネルギーが1000分の1になります。毎回同じ割合を失うので、破線のようにまっすぐ滑り降ります。約18回の衝突で中性子は0.025 eVの<b>熱</b>エネルギーに達し、そこでは温かい水が中性子を減速させるのと同じ頻度で加速させます。酸素は16倍重く、1回の衝突で奪うエネルギーはわずかなので、100回以上必要です。</p>
  <div class="btns"><button class="btn ghost" data-act="tgtH" aria-pressed="true">水素</button><button class="btn ghost" data-act="tgtO" aria-pressed="false">酸素</button><button class="btn" data-act="again">もう一度撃つ</button></div>
</div>
<div class="step">
  <p>約1 eV以下では、分子の結合が各衝突を左右します。水素はそれぞれ酸素につながっています（明るい線）。遅い中性子はもはや自由な水素に当たるのではなく、18倍重い分子全体に当たるので、単純な衝突ではほとんどエネルギーを奪えません。</p>
  <p>分子を回転させたり振動させたりすることもできますが、渡せるのは0.06、0.2、0.45 eVという決まった量ずつだけです（明るい閃光）。温かい分子は、こうした量を中性子に返すこともあります。グラフの1 eV以下の影をつけた帯が、これが効く領域です。結合をオフにすると、自由な水素と比べられます。</p>
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

// canvas labels added 2026-10-29 (I18NLABELS_B)
Object.assign(WT.L.labels, {
  "water · neutron hits hydrogen": "水 · 中性子が水素に衝突",
  "thermal · kT ≈ {#} eV": "熱エネルギー · kT ≈ {#} eV",
  "{#} meV": "{#} meV",
  "collisions →": "衝突回数 →",
  "energy": "エネルギー",
  "typical bounce: energy × {#} (theory × {#}) · {#} bounces to thermal": "典型的な衝突：エネルギー × {#}（理論 × {#}）· 熱まで {#} 回",
  "typical: the average step along the dashed line (energy shares multiply, so the average is taken on this scale)": "典型値：破線に沿った平均の一歩（エネルギーの割合は掛け合わさるので、この目盛りで平均）",
  "bright line: a bond holding H to its O": "明るい線：H を O につなぐ結合",
  "bright flash: the neutron left a fixed amount of energy in the molecule": "明るい閃光：中性子が分子に決まった量のエネルギーを残した",
  "below {#} eV: the bonds shape each bounce": "{#} eV 以下：結合が各衝突を左右する",
  "free-atom recoil": "自由原子の反跳",
  "α: how hard the knock (momentum handed over) →": "α：衝突の強さ（渡される運動量）→",
  "β: the neutron's energy change, in units of kT = {#} eV": "β：中性子のエネルギー変化（単位 kT = {#} eV）",
  "gain ↑": "獲得 ↑",
  "loss ↓": "損失 ↓",
  "outline: reachable from {#} eV": "輪郭：{#} eV から到達可能",
  "rare → likely": "まれ → 起こりやすい",
  "scattering law S(α,β) · hydrogen bound in water": "散乱則 S(α,β) · 水中で結合した水素",
  "stripes: energy lost to the molecule in fixed amounts": "縞：決まった量ずつ分子に渡したエネルギー",
});
