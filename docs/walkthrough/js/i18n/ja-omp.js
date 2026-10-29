/* Japanese: omp (第5章、光学模型) */
WT.L.ch.omp = {
  num: "第5章", title: "光学模型", short: "光学模型",
  lead: "エンジンはまず、もっと単純な問いを立てます。やって来る中性子には、原子核はどう見えるのでしょうか。",
  html: `
<div class="step">
  <p>量子力学では、中性子は波でもあります。図は左から転がり込んでくる波を示しています。明るい帯が波の山で、その先に原子核（点線の円）があります。まだ何も波に作用していないので、山はそのまま通り抜けます。</p>
  <div class="ctl"><label for="omp-e">中性子エネルギー（MeV）</label><input id="omp-e" type="range" data-bind="E" min="0.2" max="40" step="0.1" value="8"><output data-show="E" data-fmt="1"></output></div>
  <p>エネルギーを動かして、下に表示される波長をフェムトメートル（fm、10⁻¹⁵ m）単位で見てみましょう。遅い中性子ほど波長は長く、約9 MeV以下では1波長がこの原子核全体より広くなります。</p>
</div>
<div class="step">
  <h3>実ポテンシャル：屈折</h3>
  <p><b>光学ポテンシャル</b>は、原子核全体が中性子に及ぼす平均的な力です。その<em>実部</em>は深さ約50 MeVの井戸です。中性子は内部で速くなるので、山の間隔が詰まります。エンジンはこれにウッズ・サクソン型の形を与えます。中心では平らで深く、表面でなめらかにゼロへ減っていく形です。</p>
</div>
<div class="step">
  <h3>虚ポテンシャル：吸収</h3>
  <p>原子核の後ろの影は、反応で失われた中性子です。ポテンシャルの<em>虚部</em>がこれを表します。虚部は波を曲げるのではなく小さくし、主に表面付近（色のついた輪）で働きます。</p>
  <div class="ctl"><label for="omp-w">吸収 W（MeV）</label><input id="omp-w" type="range" data-bind="W" min="0" max="14" step="0.5" value="7"><output data-show="W" data-fmt="1"></output></div>
  <p><i>W</i>を0にすると影が埋まります。吸収がなければ反応もありません。光学模型という名前はここから来ています。原子核は、光を一部曲げ一部吸収する曇ったガラス玉なのです。</p>
</div>
<div class="step">
  <h3>部分波と衝突パラメータ</h3>
  <p>正面から見ると、標的はいくつもの輪に分かれ、輪の1つ1つが<b>部分波</b><i>l</i> = 0, 1, 2, …に対応します。中心から距離<i>b</i>のところを通る中性子は<b>角運動量</b><i>l</i> ≈ <i>k b</i>をもち、<i>k</i>はエネルギーとともに大きくなります。輪が暗いほど、その<b>透過係数</b><i>T<sub>l</sub></i>、すなわちその輪の中性子が吸収される確率が大きいことを表します。</p>
  <div class="ctl"><label for="omp-e3">中性子エネルギー（MeV）</label><input id="omp-e3" type="range" data-bind="E" min="0.2" max="40" step="0.1" value="8"><output data-show="E" data-fmt="1"></output></div>
  <div class="btns"><button class="btn" data-act="fire">中性子を200個撃つ</button></div>
  <p>オレンジの閃光は吸収された中性子です。棒グラフは各輪で吸収された割合を、模型の<i>T<sub>l</sub></i>（目盛り）と比べます。内側の輪はほぼすべてを吸収し、外側の輪は中性子を通してしまいます。低エネルギーでは輪がとても大きく、<i>l</i> = 0だけが重要です。</p>
</div>
<div class="step">
  <h3>遠心力障壁</h3>
  <p>角運動量の大きな中性子は外側を通りすぎて、原子核に触れられません。これが<b>遠心力障壁</b>です。上から見ると、ここにある中性子はすべて同じ部分波<i>l</i>に属するので、同じ<b>すれ違い距離</b><i>b</i> ≈ (<i>l</i>+½)/<i>k</i>（点線の円）を通ります。</p>
  <p>しかし中性子はそれぞれ波であり、換算波長λ̄ほどの幅にぼやけています（光の輪）。経路が外れていても、ぼやけた縁が表面をかすめて中に入ることがあります。これが<b>トンネル効果</b>です。</p>
  <div class="ctl"><label for="omp-l">部分波 l</label><input id="omp-l" type="range" data-bind="L" min="0" max="8" step="1" value="3" data-instant><output data-show="L" data-fmt="0"></output></div>
  <div class="ctl"><label for="omp-e2">エネルギー（MeV）</label><input id="omp-e2" type="range" data-bind="E" min="0.2" max="40" step="0.1" value="8"><output data-show="E" data-fmt="1"></output></div>
  <p><i>l</i>を上げると経路は外へ移り、入る中性子が減ります。エネルギーを上げると、同じ<i>l</i>でもより近くを通り、ぼやけも小さくなります。エンジンはポテンシャル全体にわたってシュレーディンガー方程式（量子力学の波動方程式）を解き、各<i>T<sub>l</sub></i>を正確に求めます。波を送り込み、吸収されずにどれだけ戻ってくるかを測ります。戻ってくる波が<i>S</i>で、その2乗|<i>S</i>|²が戻ってくる割合です。戻ってこなかった分は原子核に取り込まれたのであり、その不足分が<i>T<sub>l</sub></i>です。</p>
  <div class="formula">T<sub>lj</sub> = 1 − |S<sub>lj</sub>|²</div>
</div>
<div class="step">
  <h3>反応断面積</h3>
  <p>右の円盤は、中性子から見た原子核の大きさ、すなわち<b>反応断面積</b>で、単位はバーン（10⁻²⁴ cm²）です。各輪はその面積に<i>T<sub>l</sub></i>を掛けた分を加えます。点線の円は幾何学的な大きさです。</p>
  <div class="ctl"><label for="omp-e4">中性子エネルギー（MeV）</label><input id="omp-e4" type="range" data-bind="E" min="0.2" max="40" step="0.1" value="8"><output data-show="E" data-fmt="1"></output></div>
  <div class="btns"><button class="btn ghost" data-act="sum">もう一度足し合わせる</button></div>
  <p>エネルギーを変えると、和の計算がやり直されます。低エネルギーでは大きな輪1つか2つで円盤のほとんどができ、高エネルギーでは多数の細い輪が少しずつ加わって、円盤は幾何学的な大きさに近づきます。</p>
  <div class="formula">σ<sub>R</sub> = (π/k²) Σ (2l+1) T<sub>l</sub></div>
  <p><i>T<sub>l</sub></i>はエンジンの残りの部分に供給されます。励起された原子核の各スピンがどれくらいの頻度でできるかを決め、逆向きに使えば、各粒子がどれだけ容易に外へ出られるかを決めます。</p>
  <div class="aside">コードでは：<code>omp/parameters.py</code>（Koning–Delarocheの大域的ポテンシャル、アクチノイドには分散型ポテンシャル）、<code>omp/schrodinger.py</code>（Numerov積分とクーロン波動関数への接続）、<code>omp/inverse.py</code>（詳細つり合いによる放出粒子）、<code>omp/regional.py</code>（任意、既定ではオフ：変形した希土類標的向けの井戸の領域的な調整で、測定されたS₀とS₁に合わせたもの）。</div>
</div>`,
};
Object.assign(WT.L.labels, {
  "absorbing surface": "吸収する表面",
  "shadow: neutrons lost to reactions": "影：反応で失われた中性子",
  "wavelength {#} fm   ·   nucleus {#} fm across": "波長 {#} fm   ·   原子核の直径 {#} fm",
  "crests crowd inside the well": "井戸の中で山が詰まる",
  "l={#}": "l={#}",
  "nuclear radius": "原子核半径",
  "reaction cross section ≈ {#} b": "反応断面積 ≈ {#} b",
  "geometric size π(R+λ̄)² ≈ {#} b · darker ring = more absorbed · orange flash = absorbed": "幾何学的大きさ π(R+λ̄)² ≈ {#} b · 暗い輪 = 吸収大 · オレンジ = 吸収",
  "absorbed, ring by ring": "輪ごとの吸収",
  "bar: your neutrons · tick: model Tₗ": "棒：撃った中性子 · 目盛り：模型のTₗ",
  "rings: shade = Tₗ": "輪：濃さ = Tₗ",
  "geometric size π(R+λ̄)²": "幾何学的大きさ π(R+λ̄)²",
  "reaction cross section": "反応断面積",
  "ring l={#}: ({#}l+{#})·Tₗ·π/k² = +{#} b": "輪 l={#}：({#}l+{#})·Tₗ·π/k² = +{#} b",
  "all {#} rings added": "{#}個の輪をすべて加算",
  "σ_R = {#} b": "σ_R = {#} b",
  "geometric {#} b": "幾何学的 {#} b",
  "geometric {#} b · darker = more absorbed · orange = absorbed": "幾何学的 {#} b · 暗い = 吸収大 · オレンジ = 吸収",
  "swing distance b ≈ (l+½)/k = {#} fm": "すれ違い距離 b ≈ (l+½)/k = {#} fm",
  "nuclear radius R = {#} fm · wave fuzz λ̄ = {#} fm": "原子核半径 R = {#} fm · 波のぼやけ λ̄ = {#} fm",
  "path crosses the nucleus: most get in": "経路が原子核を横切る：大半が入る",
  "path misses the nucleus: only the fuzzy edge can tunnel in": "経路が原子核を外れる：ぼやけた縁だけがトンネル",
  "absorbed {#} of {#} · model Tₗ = {#}": "吸収 {#} / {#} · 模型のTₗ = {#}",
});
