/* Japanese: optical (第17章、光学模型を解く) */
WT.L.ch.optical = {
  num: "第17章", title: "光学模型を解く", short: "光学模型を解く",
  lead: "第2章では、光学ポテンシャルを曇ったガラス玉として描きました。ここではエンジンが実際に使う形で示します。大域的なパラメータ化、1ステップずつ積分する動径シュレーディンガー方程式、そして波を透過係数に変える接続条件です。",
  html: `
<div class="step">
  <h3>Koning–Delarocheポテンシャル</h3>
  <p>球形の標的に入射する中性子と陽子については、既定は<b>Koning–Delaroche</b>（KD03）のポテンシャルです。ウッズ・サクソン型の形で、その深さはエネルギー、および標的の質量数と中性子過剰に応じてなめらかに変わります。深さは大域的な式から、あるいは鉄56のようにKD03が1つずつ当てはめた原子核については、同じ形の局所的な当てはめから与えられます。図は鉄56に入射する中性子について大域的な式を使っています。実部の井戸（青）は束縛し、虚部（赤）は吸収します。吸収は体積部で起こるほか、低エネルギーでは主に表面の薄い層で起こります。</p>
  <div class="ctl"><label for="op-e">中性子エネルギー（MeV）</label><input id="op-e" type="range" data-bind="E" min="0.1" max="80" step="0.1" value="5"><output data-show="E" data-fmt="1"></output></div>
  <div class="formula">U(r) = −V<sub>V</sub> f(r) − iW<sub>V</sub> f(r) + 4i a<sub>D</sub>W<sub>D</sub> df<sub>D</sub>/dr + 2(V<sub>so</sub> + iW<sub>so</sub>) (1/r) df<sub>so</sub>/dr ⟨l·σ⟩</div>
  <p>探りの中性子は設定したエネルギーで横切り、吸収が効くところで薄れていきます。その平均自由行程はħ<i>v</i>/2|<i>W</i>|です。各深さは、フェルミエネルギーから測った<i>E</i> − <i>E</i><sub>F</sub>の関数です。実部の深さはゆっくり減少し、表面吸収<i>W</i><sub>D</sub>は10 MeV付近でピークとなり、体積吸収<i>W</i><sub>V</sub>は着実に増えて、ここでは約45 MeVより上で主役になります。</p>
</div>
<div class="step">
  <h3>動径方程式を積分する</h3>
  <p>部分波はそれぞれ固有の動径方程式に従います。エンジンはそれを<i>r</i> = 0から外向きに、複素ポテンシャル全体を通して<b>Numerov法</b>で積分します。刻み幅の6乗の精度をもつ3点公式です。</p>
  <div class="formula">u″<sub>lj</sub>(r) = [ l(l+1)/r² + (2μ/ħ²) U<sub>lj</sub>(r) − k² ] u<sub>lj</sub>(r)</div>
  <div class="ctl"><label for="op-l">部分波 l</label><input id="op-l" type="range" data-bind="L" min="0" max="10" step="1" value="1" data-instant><output data-show="L" data-fmt="0"></output></div>
  <div class="ctl"><label for="op-e2">中性子エネルギー（MeV）</label><input id="op-e2" type="range" data-bind="E" min="0.1" max="80" step="0.1" value="5"><output data-show="E" data-fmt="1"></output></div>
  <p>実線は時間とともに変化する波Re[<i>u</i> e<sup>−iωt</sup>]で、破線は原子核がない場合の自由な波です。井戸の内側では波は短く（中性子が速い）、小さく（吸収される）なり、外側では位相がずれて戻ってきます。</p>
</div>
<div class="step">
  <h3>波からSとTへ</h3>
  <p>約12 fmより外ではポテンシャルは消えており、波は入ってくる自由波と出ていく自由波の重ね合わせ<i>u</i> ∝ <i>H</i><sup>−</sup> − <i>S</i> <i>H</i><sup>+</sup>でなければなりません。積分した<i>u</i>を2つの半径で接続すると、<b>S行列</b>要素<i>S<sub>lj</sub></i>、すなわち位相を含めた出ていく波の振幅が決まります。</p>
  <div class="btns"><button class="btn ghost" data-act="abs" aria-pressed="false">吸収を切る</button></div>
  <div class="formula">S<sub>lj</sub> = η<sub>lj</sub> e<sup>2iδ<sub>lj</sub></sup> ,  T<sub>lj</sub> = 1 − |S<sub>lj</sub>|²</div>
  <p>点は複素平面上の<i>S</i>で、単位円の内側にあります。その軌跡は、エネルギーを0.1から40 MeVまで掃引したときの経路です。吸収がなければ|<i>S</i>| = 1で、点は円の上を動き、波は位相が変わるだけで<i>T</i> = 0です。円の内側へ入り込んだ距離が、複合核やほかのすべての反応が受け取る分です。</p>
</div>
<div class="step">
  <h3>スピン軌道項がjを分ける</h3>
  <p><b>スピン軌道</b>項は、<i>j</i> = <i>l</i> + ½では引力、<i>j</i> = <i>l</i> − ½では斥力です。表面で数MeVと小さいのですが、各<i>l</i>の2つの透過係数を引き離し、その効果は表面をかすめる部分波の近くで最も大きくなります。</p>
  <div class="ctl"><label for="op-e3">中性子エネルギー（MeV）</label><input id="op-e3" type="range" data-bind="E" min="0.1" max="80" step="0.1" value="5"><output data-show="E" data-fmt="1"></output></div>
  <div class="btns"><button class="btn ghost" data-act="so" aria-pressed="false">スピン軌道項を切る</button></div>
  <p>ハウザー・フェッシュバッハ（第16章）は両者を別々に使います。重みをつけて足し合わせた(<i>l</i>+1)<i>T</i><sub>l,l+½</sub> + <i>l</i> <i>T</i><sub>l,l−½</sub>では、反応断面積はほとんど変わりません。全断面積がスピン軌道項の強さをほとんど制約せず、偏極データが必要になるのはそのためです。</p>
</div>
<div class="step">
  <h3>断面積</h3>
  <p>部分波を足し合わせると、ポテンシャルの当てはめに使われる観測量が得られます。反応断面積は取り除かれた流束を数え、全断面積は前方振幅から決まり、その差が形状弾性散乱です。</p>
  <div class="formula">σ<sub>R</sub> = (π/k²) Σ<sub>l</sub> [(l+1)T<sub>l,l+½</sub> + l T<sub>l,l−½</sub>] ,  σ<sub>tot</sub> = (2π/k²) Σ<sub>lj</sub> (j+½)(1 − Re S<sub>lj</sub>)</div>
  <div class="ctl"><label for="op-e4">中性子エネルギー（MeV）</label><input id="op-e4" type="range" data-bind="E" min="0.2" max="50" step="0.1" value="5"><output data-show="E" data-fmt="1"></output></div>
  <p>KD03は、1 keVから200 MeVまで、多くの原子核のこうしたデータに当てはめられました。鉄の全断面積は数MeVで3.5〜4 b、14 MeVで2.5 bで、この原子核に合わせた調整なしに、幅の広い極大も含めて約5パーセント以内で再現されます。それらの極大は、中性子の波長に対して見た原子核の大きさの表れです。</p>
</div>
<div class="step">
  <h3>低エネルギーの端</h3>
  <p>数keVより下ではs波だけが効き、<i>T</i><sub>0</sub>は√<i>E</i>のように増えます。この両対数グラフでは傾き2分の1です。その定数が<b>強度関数</b><i>S</i><sub>0</sub> = <i>T</i><sub>0</sub>/(2π√<i>E</i>)（<i>E</i>はeV単位）で、共鳴解析がΣ Γ<sub>n</sub><sup>0</sup>/Δ<i>E</i>として測るのと同じ量です。</p>
  <p>大域的ポテンシャルは主にMeV領域で当てはめられており、低エネルギーの端は最も弱い点です。鉄56に対してこのポテンシャルは<i>S</i><sub>0</sub> ≈ 5.5 × 10⁻⁴を与え、KD03の局所的な当てはめもほぼ同じ値ですが、測定値（RIPL）は2.3 ± 0.6 × 10⁻⁴です。鉄は<i>A</i> ≈ 55付近の3sサイズ共鳴のピーク近くにあり、そこでは<i>S</i><sub>0</sub>がポテンシャルに最も敏感です。測定された<i>S</i><sub>0</sub>と<i>S</i><sub>1</sub>が、エンジンへの独立した任意の入力になっているのはそのためです。</p>
  <div class="aside">コードでは：<code>omp/parameters.py</code>（KD03とほかの大域的ポテンシャル）、<code>omp/potential.py</code>（動径形状因子）、<code>omp/schrodinger.py</code>（Numerov積分と接続。荷電粒子にはSteed法によるクーロン関数を使う。球形標的ではECISの代わりとなり、ECISのT<sub>lj</sub>と照合済み）、<code>ecis/</code>（変形標的のためのチャネル結合計算の移植）、<code>omp/sfunc.py</code>（任意：測定されたS₀、S₁）。図は鉄56に入射する中性子について、非相対論的に方程式そのものを解いています。</div>
</div>`,
};
(function () {
  const L = {
    // scene 1: the potential
    "{#} fm": "{#} fm", "{#} MeV": "{#} MeV", "{#} keV": "{#} keV", "{#} eV": "{#} eV", "{#} b": "{#} b",
    "real well, depth {#} MeV": "実部の井戸、深さ {#} MeV",
    "surface absorption, peak {#} MeV": "表面吸収、ピーク {#} MeV",
    "volume absorption {#} MeV": "体積吸収 {#} MeV",
    "spin–orbit for l = {#}, j = {#}/{#}: {#} MeV": "l = {#}, j = {#}/{#} のスピン軌道項：{#} MeV",
    "E = {#} MeV": "E = {#} MeV",
    "real": "実部", "volume": "体積", "surface": "表面",
    "depths (MeV) against energy (MeV)": "エネルギー（MeV）に対する深さ（MeV）",
    // scene 2: the radial wave
    "potential: real (blue), imaginary (red)": "ポテンシャル：実部（青）、虚部（赤）",
    "nuclear surface": "原子核表面",
    "l = {#}, j = {#}+½ · E = {#} MeV · |S| = {#} · δ = {#}° · T = {#}": "l = {#}, j = {#}+½ · E = {#} MeV · |S| = {#} · δ = {#}° · T = {#}",
    "solid: the wave now · shaded: its size |u| · dashed: free wave": "実線：現在の波 · 影：その大きさ |u| · 破線：自由な波",
    // scene 3: S in the complex plane
    "Re S": "Re S", "Im S": "Im S",
    "|S| = {#}: nothing absorbed": "|S| = {#}：吸収なし",
    "l = {#}, j = {#}+½ · E = {#} MeV": "l = {#}, j = {#}+½ · E = {#} MeV",
    "|S| = {#} · T = {#} − |S|² = {#}": "|S| = {#} · T = {#} − |S|² = {#}",
    "l = {#}, j = {#}+½": "l = {#}, j = {#}+½",
    "|S| = {#}": "|S| = {#}",
    "T = {#} − |S|² = {#}": "T = {#} − |S|² = {#}",
    "trail: S as E runs {#} → {#} MeV": "軌跡：E を {#} → {#} MeV と動かしたときの S",
    "no absorption: S stays on the circle": "吸収なし：Sは円の上にとどまる",
    // scene 4: spin-orbit
    "T = {#}": "T = {#}", "l": "l",
    "hollow: j = l − ½ · solid: j = l + ½": "白抜き：j = l − ½ · 塗りつぶし：j = l + ½",
    "hollow (purple): j = l − ½ · solid (blue): j = l + ½": "白抜き（紫）：j = l − ½ · 塗りつぶし（青）：j = l + ½",
    "reaction cross section {#} b (without spin–orbit {#} b)": "反応断面積 {#} b（スピン軌道項なしでは {#} b）",
    "reaction cross section {#} b (spin–orbit off)": "反応断面積 {#} b（スピン軌道項オフ）",
    "grazing l ≈ kR = {#}": "かすめる部分波 l ≈ kR = {#}",
    // scene 5: cross sections
    "total {#} b": "全断面積 {#} b", "reaction {#} b": "反応 {#} b", "shape elastic {#} b": "形状弾性 {#} b",
    "n + ⁵⁶Fe, KD{#}, computed here": "n + ⁵⁶Fe、KD{#}、ここで計算",
    // scene 6: T0 and S0
    "T₀ (s-wave)": "T₀（s波）",
    "T₁ (p-wave, j = {#}/{#}): slope {#}/{#}": "T₁（p波、j = {#}/{#}）：傾き {#}/{#}",
    "dashed: {#}πS₀√E, slope ½": "破線：{#}πS₀√E、傾き ½",
    "S₀ = {#} × {#}⁻⁴ from this potential": "このポテンシャルによる S₀ = {#} × {#}⁻⁴",
  };
  // the mean free path prints "> 100" when it is long, at the surface and in the centre independently
  for (const a of ["{#}", "> {#}"]) for (const b of ["{#}", "> {#}"])
    L[`mean free path: ${a} fm at the surface, ${b} fm in the centre`] = `平均自由行程：表面で ${a} fm、中心で ${b} fm`;
  Object.assign(WT.L.labels, L);
})();
Object.assign(WT.L.glossary, {
  koningDelaroche: {
    term: "Koning–Delarocheポテンシャル", aliases: ["Koning–Delaroche", "KD03"],
    short: "A. J. KoningとJ.-P. Delaroche（2003年）による中性子と陽子の大域的光学ポテンシャルで、1 keVから200 MeV、質量数24から209までを覆います。",
    more: "深さ、半径、ディフューズネスはエネルギー、質量数、中性子過剰のなめらかな関数で、大量の測定断面積と角度分布にまとめて1度だけ当てはめられています。TALYSでもエンジンでも、核子に対する既定です。",
    chapter: "optical",
  },
  numerov: {
    term: "Numerov法", aliases: ["Numerov法", "Numerov"],
    short: "動径シュレーディンガー方程式のように1階微分の項をもたない2階微分方程式を積分するための3点公式で、1ステップあたりの誤差はh⁶の次数です。",
    formula: "(1 − h²Q_n+1/12) u_n+1 = 2(1 + 5h²Q_n/12) u_n − (1 − h²Q_n−1/12) u_n−1",
    chapter: "optical",
  },
  sMatrix: {
    term: "S行列", aliases: ["S行列"],
    short: "入ってくる波と出ていく波を結びつける振幅で、1つの部分波の弾性散乱では1つの複素数S = η e^(2iδ)です。",
    more: "|S| = 1なら何も吸収されず、位相δだけが変わります。不足分1 − |S|²が透過係数、すなわち反応に取り込まれる流束です。",
    chapter: "optical",
  },
  spinOrbit: {
    term: "スピン軌道項", aliases: ["スピン軌道"],
    short: "核子のスピンが軌道角運動量と平行か反平行かによって変わる、原子核ポテンシャルの部分です。",
    more: "j = l + ½では引力、j = l − ½では斥力で、原子核表面でピークをもちます。同じ相互作用が殻模型の魔法数を生み出します。",
    chapter: "optical",
  },
});
