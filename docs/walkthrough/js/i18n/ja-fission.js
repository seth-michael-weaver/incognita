/* Japanese: fission (第12章、核分裂) */
WT.L.ch.fission = {
  num: "第12章", title: "2つに割れる", short: "核分裂",
  lead: "最も重い原子核には、軽い原子核にはない出口があります。粒子を1個放り出す代わりに、原子核全体が2つに裂けるのです。これが核分裂です。",
  html: `
<div class="step">
  <p>重い原子核は、電荷を帯びた液体のしずくのようにふるまいます。表面張力（灰色の矢印）がしずくを丸く引き締め、すべて正の電荷をもつ陽子がしずくを押し広げます（赤い矢印）。ウランでは両者がほぼつり合っています。</p>
  <div class="ctl"><label for="fis-d">しずくを引き伸ばす</label><input id="fis-d" type="range" data-bind="def" min="0" max="1" step="0.01" value="0"><output data-show="def" data-fmt="2"></output></div>
  <p>ドラッグして引き伸ばし、下の小さなエネルギー曲線上の点を見てみましょう。引き伸ばすと表面が増えてエネルギーが必要になりますが、電荷が広がってエネルギーが解放されます。曲線の頂上を越えると電荷が勝ち、くびれができて、2つの半分が約200 MeVをもって飛び離れます。</p>
</div>
<div class="step">
  <h3>形の地形</h3>
  <p>曲線は、丸い形（左）から分裂した形（右）までのあらゆる形のエネルギーです。なめらかな液滴模型では丘が1つになるだけですが、核子はまとまりごとにエネルギー準位を埋めていき（これが<b>殻構造</b>です）、最も重い元素ではこれが曲線に井戸を刻みます。こうしてできるのが<b>二重こぶ障壁</b>で、原子核は引き伸ばされた形でしばらくとどまることができます。</p>
  <p>エンジンはこの曲線を仮定するのではなく、各変形（引き伸ばしの量）でのエネルギーを求めた微視的計算から、1点ずつ読み取ります。</p>
</div>
<div class="step">
  <h3>丘をトンネルで抜ける</h3>
  <p>玉は最初の谷にいる励起した原子核で、オレンジの点線の励起エネルギーにあり、6 MeVの頂上より低いところにいます。古典的には決して越えられませんが、量子力学では暗く塗られた禁止領域を<b>トンネル</b>で抜けることができます。その確率<i>T</i>は、禁止領域が厚くなるにつれて指数関数的に小さくなります。</p>
  <div class="ctl"><label for="fis-e">励起エネルギー</label><input id="fis-e" type="range" data-bind="E" min="3" max="8" step="0.05" value="5"><output data-show="E" data-fmt="2"></output></div>
  <p>エネルギーを上げて、禁止領域が薄くなるにつれ<i>T</i>が上がるのを見てみましょう。教科書的な近道（ヒル・ホイーラー）は頂上を放物線（青い点線）として扱います。エンジンは実際の形をたどります。実際の形は低いところほど幅が広いので、頂上よりずっと下では確率がより小さくなります。<i>K</i>は行く手をふさぐ丘の量を表します。</p>
  <div class="formula">T = 1 / (1 + e<sup>2K</sup>),  K = ∫ √(2μ(V−E)) dβ / ħ</div>
</div>
<div class="step">
  <h3>頂上の門</h3>
  <p>頂上の扉は<b>遷移状態</b>、すなわち障壁の上で引き伸ばされた原子核の量子状態です。それぞれスピンとパリティ（0⁺、2⁻、…）をもち、門の役割を果たします。光っている隙間が、門がどれだけ開いているかを示します。原子核は自分のスピンとパリティに合う門しか通れず、各門はエネルギーがその高さを越えるにつれて徐々に開きます。</p>
  <div class="ctl"><label for="fis-e2">励起エネルギー</label><input id="fis-e2" type="range" data-bind="E" min="3" max="8" step="0.05" value="5"><output data-show="E" data-fmt="2"></output></div>
  <div class="btns"><button class="btn ghost" data-act="jpAll">任意のスピン</button><button class="btn ghost" data-act="jp0">複合核 0⁺</button><button class="btn ghost" data-act="jp1">複合核 1⁻</button></div>
  <p>スピンとパリティを1つ選ぶと、合う門だけが数えられ、全体の開きは小さくなります。さらに上では門が密集して<b>連続領域</b>になり、エンジンは通常の準位と同じように、その密度で門を数えます。</p>
</div>
<div class="step">
  <h3>直列に並んだ2つの丘</h3>
  <p>今度は丘が2つあり、それぞれに門があります（円で、塗られた部分が開き具合です）。原子核は左からやって来ます。最初の丘を越えたものは井戸に閉じ込められ、どちらかの側から出るまで門の間を跳ね返ります。確率は直列抵抗のように組み合わさるので、越えにくいほうの丘がほぼ結果を決めます。</p>
  <div class="ctl"><label for="fis-b">外側の丘の高さ</label><input id="fis-b" type="range" data-bind="Bb" min="3.5" max="7.5" step="0.05" value="5.6"><output data-show="Bb" data-fmt="2"></output></div>
  <div class="formula">1/T = 1/T<sub>A</sub> + 1/T<sub>B</sub></div>
  <p>外側の丘を高くしてみましょう。内側の門がどれだけ開いていても、核分裂への流れは詰まってしまいます。</p>
</div>
<div class="step">
  <h3>チャンスは1回だけではない</h3>
  <p>ウラン238は中性子を吸収して、励起エネルギー<i>E</i>*（点線）のウラン239になります。分裂しなければ代わりに中性子を放出することがあり、線が下がります。後に残ったウラン238はまだ熱く、今度は自分の障壁に挑みます。これが<b>第2チャンス核分裂</b>、(n,n′f)です。山は各原子核がどう終わったかを集めます。</p>
  <div class="ctl"><label for="fis-en">中性子エネルギー</label><input id="fis-en" type="range" data-bind="En" min="0" max="25" step="0.1" value="7"><output data-show="En" data-fmt="1"></output></div>
  <p>エネルギーを上げると、後の挑戦も成功しはじめ、約12 MeVで第3のチャンスが開きます。新しいチャンスはそれぞれ、原子核がどれだけ分裂しやすいかを表す、測定された<b>核分裂断面積</b>の階段として現れます。エンジンが計算するのはどれだけの頻度で分裂するかであって、どんな破片に分裂するかではありません。</p>
  <div class="aside">コードでは：<code>fission/wkb.py</code>（変形エネルギーの経路とWKB積分）、<code>fission/barriers.py</code>（ヒル・ホイーラー、遷移状態、障壁上の準位密度）、<code>fission/transmission.py</code>（直列のこぶ、スピンとパリティごとのT<sub>fis</sub>）、<code>fission/chain.py</code>（カスケードの各原子核の障壁）。</div>
</div>`,
};
Object.assign(WT.L.labels, {
  // drop
  "surface tension pulls it round": "表面張力が丸く引き締める",
  "the protons push it apart": "陽子が押し広げる",
  "a charged drop, nearly round": "帯電したしずく、ほぼ球形",
  "stretched: more surface, charge further apart": "伸びる：表面が増え、電荷が離れる",
  "a neck forms": "くびれができる",
  "two fragments, carrying about {#} MeV": "2つの破片、約{#} MeVを運ぶ",
  "energy of the drop": "しずくのエネルギー",
  // landscape
  "ground state": "基底状態", "inner barrier": "内側障壁", "second well": "第2の井戸",
  "outer barrier": "外側障壁", "split (scission)": "分裂（切断）", "one smooth hill": "なめらかな丘1つ",
  "shell effects carving the second well": "殻効果が第2の井戸を刻む",
  "round → stretched → necked → split": "球形 → 伸長 → くびれ → 分裂",
  "stretch (deformation) →": "伸び（変形）→",
  // tunnel
  "forbidden zone": "禁止領域",
  "excitation {#} MeV": "励起 {#} MeV",
  "hilltop {#} MeV": "頂上 {#} MeV",
  "parabola fit": "放物線近似",
  "passes over the top": "頂上を越える",
  // gates
  "continuum: a density": "連続領域：密度",
  "continuum of gates: counted as a density": "門の連続領域：密度で数える",
  "gates: transition states": "門：遷移状態",
  "E = {#} MeV": "E = {#} MeV",
  "all gates: total opening {#}": "全部の門：開きの合計 {#}",
  "all gates: total opening {#} + {#} from the continuum": "全部の門：開きの合計 {#} + 連続領域から{#}",
  "{#}⁺ gates only: total opening {#}": "{#}⁺の門のみ：開きの合計 {#}",
  "{#}⁺ gates only: total opening {#} + {#} from the continuum": "{#}⁺の門のみ：開きの合計 {#} + 連続領域から{#}",
  "{#}⁻ gates only: total opening {#}": "{#}⁻の門のみ：開きの合計 {#}",
  "{#}⁻ gates only: total opening {#} + {#} from the continuum": "{#}⁻の門のみ：開きの合計 {#} + 連続領域から{#}",
  // series
  "nuclei arriving →": "到着する原子核 →",
  "trapped in the well": "井戸に閉じ込め",
  "fission": "核分裂",
  "so far: {#} through, {#} turned back": "これまで：通過 {#}、引き返し {#}",
  // chance
  "²³⁹U*  E* = {#} MeV": "²³⁹U*  E* = {#} MeV", "²³⁸U*  E* = {#} MeV": "²³⁸U*  E* = {#} MeV", "²³⁷U*  E* = {#} MeV": "²³⁷U*  E* = {#} MeV",
  "↑ E* above the picture": "↑ E*は図の上方",
  "fission!": "核分裂！",
  "emits a neutron, cools, tries again": "中性子を放出し、冷えて再挑戦",
  "too cool to split: a photon, no fission": "冷えすぎて分裂不能：光子放出、核分裂なし",
  "attempt {#}: barrier {#} % open": "挑戦{#}：障壁の開き {#}%",
  "{#}st chance (n,f)": "第{#}チャンス (n,f)", "{#}nd chance (n,n′f)": "第{#}チャンス (n,n′f)", "{#}rd chance (n,{#}nf)": "第{#}チャンス (n,{#}nf)",
  "{#}st (n,f)": "第{#} (n,f)", "{#}nd (n,n′f)": "第{#} (n,n′f)", "{#}rd (n,{#}nf)": "第{#} (n,{#}nf)",
  "no fission": "核分裂なし",
});
// labels carrying a transmission T, printed either as 0.12 or as 3.4·10⁻5 (two number shapes)
(function () {
  const L = WT.L.labels, F = ["{#}", "{#}·{#}⁻{#}"];
  for (const a of F) {
    L[`inner gate T ≈ ${a}`] = `内側の門 T ≈ ${a}`;
    L[`outer gate T ≈ ${a}`] = `外側の門 T ≈ ${a}`;
    L[`both hills: T ≈ ${a}, {#} % of what arrives gets through`] = `両方の丘：T ≈ ${a}、到着分の{#}%が通過`;
    for (const b of F) {
      L[`T ≈ ${a} real shape · ${b} parabola`] = `T ≈ ${a} 実際の形 · ${b} 放物線`;
      L[`chance to tunnel T ≈ ${a} on the real shape, ${b} on the parabola`] = `トンネル確率 T ≈ ${a}（実際の形）、${b}（放物線）`;
    }
  }
})();
