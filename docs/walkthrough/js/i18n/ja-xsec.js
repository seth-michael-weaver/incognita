/* Japanese: xsec (第2章、反応断面積) */
WT.L.ch.xsec = {
  num: "第2章", title: "反応断面積とは何か", short: "反応断面積",
  html: `
<div class="step">
  <p>それぞれの円板は、原子核の標的面積、つまり<b>断面積</b>（記号σ、シグマ）です。この図は、原子核を薄く敷き詰めた板を真上から見たもので、中性子がでたらめな位置に降り注ぎます。円板の内側に落ちた中性子はその原子核と反応し（オレンジ色の閃光）、円板と円板のあいだに落ちた中性子はそのまま通り抜けます（ただ薄れて消えます）。</p>
  <p>したがって、反応する割合は、円板が板のどれだけを覆っているかという割合そのものです。小さな黒い正方形が面積の単位、1<b>バーン</b>（10⁻²⁴ cm²）で、原子核の実際の断面の大きさはおよそ1バーンです。</p>
  <div class="ctl"><label for="xs-e1">中性子のエネルギー（eV）</label><input id="xs-e1" type="range" data-bind="lgE" data-instant min="-2.3" max="2" step="0.01" value="2"><output data-show="Eshow" data-fmt="2"></output></div>
</div>
<div class="step">
  <p>遅い中性子ほど、標的は大きく見えます。円板は原子核の実際の大きさではなく、このエネルギーの中性子に対して原子核がどれだけの大きさとしてふるまうかを表しています。遅い中性子は原子核の近くに長くとどまるので、捕獲されやすくなります。捕獲では、これによってσは速さの逆数（1/v）に比例して大きくなります。</p>
  <p>板の下の曲線は、全エネルギーにわたるσです（両軸とも対数目盛）。オレンジ色の点は選んだエネルギーを示します。いちばん遅い中性子までドラッグすると、円板が大きくなり、反応する割合が増えていくのがわかります。</p>
  <div class="ctl"><label for="xs-e2">中性子のエネルギー（eV）</label><input id="xs-e2" type="range" data-bind="lgE" data-instant min="-2.3" max="2" step="0.01" value="-1.6"><output data-show="Eshow" data-fmt="2"></output></div>
</div>
<div class="step">
  <p>共鳴では標的がふくらみます。7 eVでは、中性子と原子核を合わせたエネルギーがちょうど原子核自身の準位の1つに一致するため、はるかに取り込まれやすくなります。円板の面積は約50倍になり、ここでは約400バーンに達します。</p>
  <p>7 eVから少しずれるだけで円板はすぐに縮みます。曲線のピークは幅が狭いのです。実際の原子核にはこうしたピークが数多くあり、第1章ではそのバーコードを見ました。</p>
  <div class="ctl"><label for="xs-e3">中性子のエネルギー（eV）</label><input id="xs-e3" type="range" data-bind="lgE" data-instant min="-2.3" max="2" step="0.005" value="0.845"><output data-show="Eshow" data-fmt="2"></output></div>
</div>`,
};
