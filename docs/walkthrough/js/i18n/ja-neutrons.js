/* Japanese: neutrons (第5章、原子炉はなぜ中性子で動くのか) */
WT.L.ch.neutrons = {
  num: "第5章", title: "原子炉はなぜ中性子で動くのか", short: "なぜ中性子か",
  html: `
<div class="step">
  <p>陽子は正の電荷をもち、原子核の82個の陽子も同じです。同じ符号の電荷は反発するので、陽子は押し返され、近づくほどその力は急に強まります（矢印）。遅い陽子は手前で止まり、触れることなく引き返します。約13 MeVを超えて初めてこの壁を越えられ、それより少し低いときでも、ときどきすり抜けることがあります（<b>トンネル効果</b>）。小さなグラフは、同じ反発をエネルギーの丘として描いたものです。</p>
  <div class="ctl"><label for="wn-e1">陽子のエネルギー（MeV）</label><input id="wn-e1" type="range" data-bind="Ep" data-instant min="0.5" max="20" step="0.1" value="6"><output data-show="Ep" data-fmt="1"></output></div>
</div>
<div class="step">
  <p>中性子は電荷をもたないので、どんな速さでも入り込めます。押し返すものがないので登るべき丘はなく、原子核に届きさえすれば、あとは強い力が引き込みます。</p>
  <div class="ctl"><label for="wn-e2">中性子のエネルギー（遅い → 速い）</label><input id="wn-e2" type="range" data-bind="lgEn" data-instant min="-1.6" max="7.3" step="0.01" value="-1.6"><output id="wn-en-out"></output></div>
  <p>スライダーは、室温の中性子の速さである0.025 eVから、その約10億倍の20 MeVまで動きます。どこまで下げても、中性子は入り込みます。</p>
</div>
<div class="step">
  <p>だから原子炉では、遅い中性子でもウランを分裂させられます。ウラン235の原子核が中性子を1個のみ込むとウラン236になり、少し余分なエネルギーをもちます。それだけで原子核は揺れ、くびれをつくって伸び、2つに割れるのに十分です。2つの破片は約200 MeVで飛び散り、そのとき放出される2、3個の新しい中性子が次の原子核を分裂させます。これが連鎖反応です。</p>
</div>`,
};
