/* Japanese: hauser (第13章、ハウザー・フェッシュバッハ) */
WT.L.ch.hauser = {
  num: "第13章", title: "チャネルごとのハウザー・フェッシュバッハ", short: "ハウザー・フェッシュバッハ",
  lead: "第6章では、出口どうしの競争を扉として描きました。ここではその扉の背後にある式を、チャネルを1つずつたどって示し、開いているチャネルが少ないときに必要になる補正を説明します。",
  html: `
<div class="step">
  <h3>チャネルごとの透過係数</h3>
  <p><b>チャネル</b>とは、出口の完全な宛先のことです。どの粒子か、残留核がどの状態に残されるか、そして粒子の軌道角運動量<i>l</i>と全角運動量<i>j</i> = <i>l</i> ± ½です。第2章の光学模型が、そのそれぞれに<b>透過係数</b><i>T<sub>lj</sub></i>を与えます。柱は、スピン0の標的に入射する中性子のものです。</p>
  <div class="ctl"><label for="hf-e">中性子エネルギー（MeV）</label><input id="hf-e" type="range" data-bind="lgE" min="-3" max="0.7" step="0.01" value="-0.3"><output data-show="Eshow" data-fmt="3"></output></div>
  <p>1 keVでは<i>l</i> = 0だけが開いていて、<i>T</i> ≈ 2π<i>S</i><sub>0</sub>√<i>E</i>、つまり数パーセントです。低エネルギーでは<i>l</i>が1増えるごとにおよそ(<i>kR</i>)²倍ずつ小さくなるので、エネルギーが上がるにつれて柱は1本ずつ開いていきます。どの柱も、重みg<sub>J</sub><i>T</i>で複合核に流れ込みます。</p>
  <div class="formula">σ<sub>CN</sub> = (π/k²) Σ<sub>J,π</sub> g<sub>J</sub> Σ<sub>lj</sub> T<sub>lj</sub> ,  g<sub>J</sub> = (2J+1) / [(2s+1)(2I+1)]</div>
</div>
<div class="step">
  <h3>スピンとパリティを1つずつ</h3>
  <p>角運動量とパリティは保存されるので、複合核は<i>J</i><sup>π</sup>ごとに独立に崩壊します。1つのブロックの中では、開いているすべての出口チャネルがそれぞれの<i>T</i>で競争します。基底状態へ戻る弾性散乱、各励起準位への非弾性散乱（1本の柱は、同じ<i>J</i>に結合する(<i>l</i>, <i>j</i>)を合計したもの）、3.6 MeVより上の連続領域（そのビンは準位密度で重みづけされ、多数のチャネルとして数えられます）、そして1つの小さな<i>T</i><sub>γ</sub> = 2π⟨Γ<sub>γ</sub>⟩/<i>D</i>にまとめた捕獲です。高さは対数目盛です。</p>
  <div class="ctl"><label for="hf-j">スピンとパリティのブロック</label><input id="hf-j" type="range" data-bind="jb" min="0" max="9" step="1" value="2" data-instant><output data-show="jbShow" data-fmt="0"></output></div>
  <div class="ctl"><label for="hf-e2">中性子エネルギー（MeV）</label><input id="hf-e2" type="range" data-bind="lgE" min="-3" max="0.7" step="0.01" value="-0.3"><output data-show="Eshow" data-fmt="3"></output></div>
  <p>下の帯が<b>ハウザー・フェッシュバッハ</b>の分配です。チャネル<i>a</i>から入ってきたもののうち、各出口が<i>T<sub>b</sub></i>/Σ<i>T<sub>c</sub></i>の割合を受け取ります。0.85 MeVより下では弾性散乱と捕獲しか開いておらず、弾性散乱がほぼすべてを持っていきます。</p>
  <div class="formula">σ<sub>ab</sub> = (π/k²) Σ<sub>J,π</sub> g<sub>J</sub> T<sub>a</sub> T<sub>b</sub> / Σ<sub>c</sub> T<sub>c</sub> · W<sub>ab</sub></div>
</div>
<div class="step">
  <h3>幅ゆらぎ</h3>
  <p><i>W<sub>ab</sub></i> = 1なら、この式は平均どうしを掛け合わせているだけです。平均の背後にある共鳴の幅はばらつき（ポーター・トーマス分布、第10章）、しかも弾性散乱では中性子を入れる幅と出す幅が同じなので、両者には相関があります。そのため弾性散乱では積の平均が平均の積を上回り、弾性散乱が得た分だけほかの出口が失います。</p>
  <div class="btns"><button class="btn ghost" data-act="w0" aria-pressed="false">補正なし</button><button class="btn ghost" data-act="w1" aria-pressed="true">モルダウアー</button></div>
  <div class="ctl"><label for="hf-e3">中性子エネルギー（MeV）</label><input id="hf-e3" type="range" data-bind="lgE" min="-3" max="0.7" step="0.01" value="-0.3"><output data-show="Eshow" data-fmt="3"></output></div>
  <p>バッジは、補正ありのσを補正なしのσで割った値です。最初の非弾性散乱のしきい値より下では、弾性散乱がすでに流束のほぼすべてを取っているのでほとんど変わらず、捕獲は10〜25パーセント減ります。1〜1.5 MeVでは、複合核弾性散乱が15〜35パーセント増え、最初の2⁺準位は約3分の1減ります。さらに多くの準位と連続領域が開くと、複合核弾性散乱は流束のわずかな割合になります。その因子自体は2に向かって上がりますが、ほかから奪う量は小さくなり、ほかの因子は1へ戻っていきます。モルダウアーの処方では各チャネルに自由度の数ν<sub>c</sub>を与え、<i>W</i>は1次元の積分になります。これをTALYSの32点ガウス・ラゲール則で計算します。</p>
  <div class="formula">W<sub>ab</sub> = (1 + 2δ<sub>ab</sub>/ν<sub>a</sub>) ∫₀^∞ dx Π<sub>c</sub> (1 + 2T<sub>c</sub>x / ν<sub>c</sub>ΣT)<sup>−(δ<sub>ac</sub>+δ<sub>bc</sub>+ν<sub>c</sub>/2)</sup></div>
  <div class="formula">ν<sub>c</sub> = 1.78 + (T<sub>c</sub><sup>1.212</sup> − 0.78) e<sup>−0.228 ΣT</sup></div>
</div>
<div class="step">
  <h3>モルダウアーとHRTW</h3>
  <p>曲線は、同じ計算をエネルギー範囲全体で行ったものです。複合核弾性散乱、最初の2⁺準位、捕獲のそれぞれの比を、モルダウアーは実線、<b>HRTW</b>の処方は破線で示します。HRTWは積分の代わりに、弾性因子<i>W<sub>a</sub></i>と、反復で求める有効透過係数<i>V<sub>a</sub></i>を使います。</p>
  <div class="ctl"><label for="hf-e4">中性子エネルギー（MeV）</label><input id="hf-e4" type="range" data-bind="lgE" min="-3" max="0.7" step="0.01" value="-0.3"><output data-show="Eshow" data-fmt="3"></output></div>
  <div class="formula">σ<sub>ab</sub> ∝ V<sub>a</sub>V<sub>b</sub> / ΣV<sub>c</sub> · [1 + δ<sub>ab</sub>(W<sub>a</sub> − 1)] ,  V<sub>a</sub> = T<sub>a</sub> / [1 + (W<sub>a</sub> − 1) V<sub>a</sub>/ΣV]</div>
  <p>弾性散乱と非弾性散乱では、両者はよく一致します。keV領域の捕獲では、HRTWのほうが最大10パーセント多く減らします。0.85〜2 MeVでは捕獲がむしろ増えます。そこでは全幅がゆらぐ少数の中性子幅に支配され、1/Γの平均が1/⟨Γ⟩を上回るからです。どちらの処方も厳密なランダム行列（GOE）の結果への当てはめで、TALYSはその厳密な結果も三重積分として提供しています。INCOGNITAは3つすべてを移植しています（<code>widthmode</code> 1、2、3）。既定はモルダウアーで、標的の中性子分離エネルギーまでの入射中性子に適用されます。</p>
</div>
<div class="step">
  <h3>3と2のあいだ</h3>
  <p>極限を見ると、効果の大きさがわかります。捕獲のない<i>N</i>個の等しいチャネルをとり、その合計ΣTを変えてみます。ΣTは、平均全幅と準位間隔の比Γ/<i>D</i>の2π倍です。孤立した共鳴（ΣT ≪ 1）でチャネルが多いとき、各幅は自由度1のポーター・トーマス分布に従い、弾性増大は⟨Γ<sub>a</sub>²⟩/⟨Γ<sub>a</sub>⟩² = 3です。共鳴が強く重なり合うと（ΣT ≫ 2π）、断面積はランダムな波のようにゆらぎ（Ericsonゆらぎ）、増大は2に下がります。</p>
  <div class="ctl"><label for="hf-n">開いたチャネル数 N</label><input id="hf-n" type="range" data-bind="nch" min="2" max="60" step="1" value="30" data-instant><output data-show="nch" data-fmt="0"></output></div>
  <p><i>N</i>個の孤立したチャネルでは、厳密な値は3<i>N</i>/(<i>N</i>+2)です（ひし形）。チャネルが2つしかないと、増大は1.5を超えられません。そのときは全幅も弾性幅と同じだけゆらぐからです。モルダウアーの処方はこの極限を再現しますが、HRTWは弱いチャネルが多数開いているとそこまで届きません。挿入図は、動く点に対応する幅で共鳴を描いています。モルダウアーの式では多チャネル極限は1 + 2/νで、孤立した共鳴ではν → 1、重なり合うとν → 1.78です（完全な重なりで2.12になるのは、当てはめの小さな誤差です）。</p>
  <div class="aside">コードでは：<code>compound/prepare.py</code>（<i>J</i><sup>π</sup>ごとの出口チャネルとその透過係数）、<code>compound/target.py</code>（ハウザー・フェッシュバッハの和）、<code>compound/wfc.py</code>（モルダウアー、HRTW、GOE。TALYSから移植）。図は同じ式を説明用の材料で計算しています。鉄に似た標的に対する剛体球の透過係数、7つの準位、定温度模型の連続領域、そして1つにまとめた捕獲チャネルです。</div>
</div>`,
};
Object.assign(WT.L.labels, {
  // scene 1: incident T_lj
  "T = {#}": "T = {#}",
  "l={#}": "l={#}",
  "hollow: j = l − ½ · solid: j = l + ½": "白抜き：j = l − ½ · 塗りつぶし：j = l + ½",
  "compound nucleus": "複合核",
  "compound nucleus · σ(CN) ≈ {#} b": "複合核 · σ(CN) ≈ {#} b",
  "σ(CN) ≈ {#} b": "σ(CN) ≈ {#} b",
  "E = {#} MeV · kR = {#}": "E = {#} MeV · kR = {#}",
  "E = {#} keV · kR = {#}": "E = {#} keV · kR = {#}",
  "transmission Tₗⱼ of the incident neutron": "入射中性子の透過係数 Tₗⱼ",
  // scene 2: one J^pi block
  "elastic": "弾性", "cont.": "連続",
  "level energy (MeV) under each column": "各柱の下：準位エネルギー（MeV）",
  "residual level (energy in MeV) · n×: number of (l, j) channels summed": "残留核の準位（エネルギー、MeV）· n×：合計した(l, j)チャネルの数",
  "{#}/{#}⁺ block · in through l = {#}, Tₐ = {#}": "{#}/{#}⁺ブロック · l = {#}から入射、Tₐ = {#}",
  "{#}/{#}⁻ block · in through l = {#}, Tₐ = {#}": "{#}/{#}⁻ブロック · l = {#}から入射、Tₐ = {#}",
  "elastic {#} %": "弾性 {#} %", "higher {#} %": "高い準位 {#} %",
  "Hauser–Feshbach split: T / ΣT for each exit": "ハウザー・フェッシュバッハの分配：各出口の T / ΣT",
  // scene 3: HF vs WFC
  "closed": "閉じている",
  "compound elastic": "複合核弾性", "first {#}⁺ level": "最初の{#}⁺準位",
  "higher levels": "より高い準位", "capture": "捕獲",
  "{#} mb": "{#} mb",
  "with Moldauer's correction": "モルダウアーの補正あり",
  "Hauser–Feshbach without correction": "補正なしのハウザー・フェッシュバッハ",
  "compound formation {#} mb at {#} MeV": "複合核形成 {#} mb（{#} MeV）",
  "compound formation {#} mb at {#} keV": "複合核形成 {#} mb（{#} keV）",
  // scene 4: ratio curves
  "{#} keV": "{#} keV", "{#} MeV": "{#} MeV",
  "{#}⁺ opens": "{#}⁺が開く", "continuum": "連続領域", "continuum opens": "連続領域が開く",
  "elastic ×{#} (Moldauer) · ×{#} (HRTW)": "弾性 ×{#}（モルダウアー）· ×{#}（HRTW）",
  "capture ×{#} (Moldauer) · ×{#} (HRTW)": "捕獲 ×{#}（モルダウアー）· ×{#}（HRTW）",
  "first {#}⁺ ×{#} (Moldauer) · ×{#} (HRTW)": "最初の{#}⁺ ×{#}（モルダウアー）· ×{#}（HRTW）",
  "solid: Moldauer · dashed: HRTW": "実線：モルダウアー · 破線：HRTW",
  "σ with correction / σ without": "補正ありのσ / 補正なしのσ",
  // scene 5: limits
  "ΣT = {#}πΓ/D →": "ΣT = {#}πΓ/D →",
  "elastic enhancement Wₐₐ": "弾性増大 Wₐₐ",
  "T → {#} per channel": "チャネルあたり T → {#}",
  "exact, isolated: {#}N/(N+{#}) = {#}": "厳密値（孤立）：{#}N/(N+{#}) = {#}",
  "Porter–Thomas: {#}": "ポーター・トーマス：{#}",
  "Ericson: {#}": "Ericson：{#}",
  "{#} channels · ΣT = {#} · Wₐₐ = {#}": "{#}チャネル · ΣT = {#} · Wₐₐ = {#}",
  "isolated resonances: Γ ≪ D": "孤立した共鳴：Γ ≪ D",
  "resonances begin to overlap": "共鳴が重なり始める",
  "strongly overlapping: Γ ≫ D": "強く重なり合う：Γ ≫ D",
});
Object.assign(WT.L.glossary, {
  hrtw: {
    term: "HRTW", aliases: ["HRTW"],
    short: "Hofmann、Richert、Tepel、Weidenmüllerによる幅ゆらぎ補正の処方で、チャネルごとの弾性因子と、反復で求める有効透過係数を使います。",
    more: "モルダウアーのものと同じく、ランダム行列の数値計算に当てはめてつくられました。TALYSではwidthmode 2として選べます。既定はモルダウアー（1）で、厳密なGOEの三重積分（3）が基準です。",
    chapter: "hauser",
  },
  ericson: {
    term: "Ericsonゆらぎ", aliases: ["Ericsonゆらぎ"],
    short: "多数の共鳴が重なり合うときに断面積がエネルギーとともにランダムにゆらぐ現象で、そのエネルギースケールは共鳴の平均全幅で決まります。",
    more: "孤立した共鳴でポーター・トーマス分布の幅を生むのと同じ統計の、強い重なりの極限です。そこでは弾性増大因子は2に近づきます。",
    chapter: "hauser",
  },
});
