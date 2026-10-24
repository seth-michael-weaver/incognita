/* Japanese: densities (第15章、準位密度の接続) */
WT.L.ch.densities = {
  num: "第15章", title: "準位密度をつなぐ", short: "準位密度",
  lead: "第5章では、まっすぐな板を丘の斜面につなぎました。この章では両方を式で書き下し、数え上げた準位からつなぎ目をどう見つけるか、そしてつなぎ目が存在しないときに何が起こるかを示します。",
  html: `
<div class="step">
  <h3>殻効果が減衰するフェルミガス</h3>
  <p>エンジンの既定の準位密度ldmodel 1は、<b>Gilbert–Cameron</b>型の複合模型です。高エネルギーではフェルミガス、その下では定温度模型を使います。フェルミガスに必要な数は準位密度パラメータ<i>a</i>の1つだけですが、低エネルギーではこの数が殻の影響を受けます。<b>Ignatyuk</b>の形では、殻補正δWが低い励起では完全に効き、減衰率γで弱まっていくので、原子核が熱くなると<i>a</i>(<i>U</i>)はなめらかな値<i>ã</i>に近づきます。</p>
  <div class="formula">a(U) = ã [1 + δW (1 − e<sup>−γU</sup>) / U] ,  ã = αA + βA<sup>2/3</sup> ,  γ = γ₁ / A<sup>1/3</sup></div>
  <div class="ctl"><label for="ld-dw">殻補正 δW（MeV）</label><input id="ld-dw" type="range" data-bind="dW" min="-6" max="4" step="0.1" value="1"><output data-show="dW" data-fmt="1"></output></div>
  <div class="formula">ρ<sub>F</sub>(E) = exp(2√(aU)) / (12√2 σ a<sup>1/4</sup> U<sup>5/4</sup>) ,  U = E − Δ ,  σ² = 0.01389 A<sup>5/3</sup> √(aU) / ã</div>
  <p>上の曲線はいくつかのδWに対する<i>a</i>(<i>U</i>)/<i>ã</i>で、設定した値のものが太線です。その下がln ρ<sub>F</sub>です。負のδW（閉殻）は密度を1〜2桁抑え、その抑制はゆっくりとしか消えません。<i>a</i>(<i>U</i>)はδW/<i>U</i>のように<i>ã</i>へ戻るので、20 MeVでも−6 MeVのδWはなお約40倍の差を生みます。Δは対シフトで、対をつくる核子の種類ごとに12/√Aです。</p>
</div>
<div class="step">
  <h3>下側の接線</h3>
  <p>接続エネルギー<i>E<sub>x</sub></i>より下では、フェルミガスは<b>定温度</b>模型の式に置き換えられます。その2つのパラメータは2つの条件、すなわち<i>E<sub>x</sub></i>で値と傾きがそれぞれ等しいことで決まるので、直線はそこでのln ρ<sub>F</sub>の接線になります。</p>
  <div class="formula">ρ<sub>T</sub>(E) = (1/T) e<sup>(E − E₀)/T</sup> ,  1/T = d ln ρ<sub>F</sub>/dE |<sub>E<sub>x</sub></sub> ,  E₀ = E<sub>x</sub> − T ln[T ρ<sub>F</sub>(E<sub>x</sub>)]</div>
  <div class="ctl"><label for="ld-ex">接続エネルギー Eₓ（MeV）</label><input id="ld-ex" type="range" data-bind="Ex" min="4.6" max="14" step="0.05" value="7"><output data-show="Ex" data-fmt="2"></output></div>
  <p><i>E<sub>x</sub></i>を動かすと接線が振れます。つなぎ目が高いほど<i>T</i>は高く（直線は平らに）、<i>E</i>₀は低くなります。どの<i>E<sub>x</sub></i>でもなめらかな曲線が得られます。どれが正しいかは、数え上げた準位が決めます。</p>
</div>
<div class="step">
  <h3>数え上げた準位からつなぎ目を見つける</h3>
  <p>階段は<i>E</i>より下にある既知の準位の数で、対数目盛です。定温度模型の式を積分すると直線<i>N</i>(<i>E</i>) = e<sup>(E − E₀)/T</sup> + 定数になり、これが準位<i>N<sub>L</sub></i>から準位<i>N<sub>P</sub></i>まで、つまり準位図のうち完全と考えられる範囲の数を再現しなければなりません。これが、1つの未知数<i>E<sub>x</sub></i>に対する1つの方程式です。</p>
  <div class="formula">F(E<sub>x</sub>) = e<sup>(E<sub>P</sub>−E₀)/T</sup> − e<sup>(E<sub>L</sub>−E₀)/T</sup> − (N<sub>P</sub> − N<sub>L</sub>) = 0</div>
  <div class="ctl"><label for="ld-ex2">試行 Eₓ（MeV）</label><input id="ld-ex2" type="range" data-bind="Ex" min="4.6" max="14" step="0.05" value="7"><output data-show="Ex" data-fmt="2"></output></div>
  <p>下のパネルが<i>F</i>です。エンジンはTALYSと同じく、区間を100ステップで走査して符号の変化を探し、それから二分法で絞り込みます。縮んでいく区間が二分法を示しています。<i>F</i> = 0となるところで、試行の直線が階段の上に乗ります。</p>
</div>
<div class="step">
  <h3>つなぎ目がないとき</h3>
  <p>二重閉殻では低エネルギーのフェルミガスがあまりに抑えられているため、その温度はどこでも低いままで、<i>F</i>は符号を変えません。接続エネルギーが存在しないのです。そのときTALYSは経験的な温度<i>T</i> = −0.25 + 10.2/√(<i>A</i>(1 + γδW))をとり、フェルミガスがその温度になるエネルギーを探します。二重閉殻の近くでは、フェルミガスがその温度に達するのは妥当なつなぎ目よりはるか上か、あるいはまったく達しないので、つなぎ目も系統式<i>E<sub>x</sub></i> = 2.33 + 253/<i>A</i> + Δに頼り、値が連続になるように<i>E</i>₀を決めます。</p>
  <div class="btns"><button class="btn ghost" data-act="tang" aria-pressed="false">代替エネルギーでの接線</button></div>
  <p>値は連続ですが、経験的な<i>T</i>はそのエネルギーでのフェルミガスの温度ではないので、傾きが跳びます。既定の入力では、これは²⁰⁵,²⁰⁶Tl、²⁰⁶⁻²⁰⁹Pb、²¹⁰Biで起こり、傾きの跳びは34〜62 %です。そこで<i>T</i>をフェルミガスからとると（入力で<i>E<sub>x</sub></i>が与えられたときには、TALYSもすでにそうしています）、接線が回復し、鉛領域の捕獲は最大20〜30 %変わります。INCOGNITAはここではTALYSを再現しています。この変更はTALYSの開発者に報告済みです。図は鉛に似た例で、<i>ã</i>を30 %引き上げてあるため、そのフェルミガスは探索範囲を超えた約24 MeVまで経験的な温度より下にとどまります。傾きの跳びは62 %です。</p>
</div>
<div class="step">
  <h3>検証としての間隔D₀</h3>
  <p>中性子分離エネルギーでは、密度が直接測定されます。s波共鳴の平均間隔<i>D</i>₀は、遅い中性子が到達できる1つのスピンとパリティの状態を数えたものです。スピン0の標的では<i>J</i><sup>π</sup> = ½⁺だけです。</p>
  <div class="formula">1/D₀ = ρ(S<sub>n</sub>, ½, +) = ½ ρ<sub>F</sub>(S<sub>n</sub>) · (2J+1)/(2σ²) · e<sup>−(J+½)²/2σ²</sup></div>
  <div class="ctl"><label for="ld-as">ãにかける倍率</label><input id="ld-as" type="range" data-bind="as" min="0.8" max="1.2" step="0.005" value="1"><output data-show="as" data-fmt="3"></output></div>
  <p>図は鉄57に似た複合核を大域的な<i>ã</i>で計算したもので、測定値25.4 ± 2.2 keVと比べています。<i>ã</i>が数パーセント変わると、<i>D</i>₀は数十パーセント動きます。したがって<i>D</i>₀が測定されている原子核では<i>S<sub>n</sub></i>での密度がよく固定され、測定されていない原子核では、それが捕獲における単独で最大の不確かさになります。評価では<i>a</i>を<i>D</i>₀に合わせて調整し、エンジンが従うTALYSの既定もそうしています。<i>D</i>₀が測定されている原子核では、それに当てはめた準位密度パラメータを読み込み、大域的な式はそれ以外の原子核にだけ使います。</p>
  <div class="aside">コードでは：<code>density/parameters.py</code>（ã、Ignatyukの減衰、対効果、スピンカットオフ）、<code>density/models.py</code>（フェルミガス、定温度模型、数表）、<code>density/matching.py</code>（接続の根、経験的な代替値、TALYS独自の単精度の細部まで再現）。図はldmodel 1に対するTALYSの大域的パラメータを、説明用の準位図と殻補正とともに使っています（鉛に似た例では<i>ã</i> × 1.3）。測定された<i>D</i>₀は⁵⁷FeのRIPL値です。</div>
</div>`,
};
Object.assign(WT.L.labels, {
  // axes
  "E (MeV)": "E (MeV)", "U (MeV)": "U (MeV)", "Eₓ (MeV)": "Eₓ (MeV)", "{#} keV": "{#} keV",
  // scene 1: Ignatyuk a(U) and the Fermi gas
  "a(U) / ã": "a(U) / ã",
  "U = {#} MeV · a = {#} MeV⁻¹ · T ≈ √(U/a) = {#} MeV": "U = {#} MeV · a = {#} MeV⁻¹ · T ≈ √(U/a) = {#} MeV",
  "ρ_F (states per MeV), A = {#}": "ρ_F（状態数/MeV）、A = {#}",
  "dashed: δW = {#}": "破線：δW = {#}",
  "at {#} MeV: ×{#} against δW = {#}": "{#} MeVで ×{#}（δW = {#}と比べて）",
  "at {#} MeV: ×{#}e{#} against δW = {#}": "{#} MeVで ×{#}e{#}（δW = {#}と比べて）",
  // scene 2: the tangent
  "T = {#} MeV": "T = {#} MeV", "× e": "× e",
  "joint Eₓ = {#} MeV": "つなぎ目 Eₓ = {#} MeV",
  "E₀ = {#} MeV": "E₀ = {#} MeV",
  "Fermi gas": "フェルミガス", "constant temperature": "定温度",
  "ln ρ (states per MeV), A = {#}": "ln ρ（状態数/MeV）、A = {#}",
  // scene 3: staircase and bisection
  "levels {#}–{#}": "準位 {#}–{#}",
  "levels {#} to {#}: taken as complete": "準位 {#}〜{#}：完全とみなす",
  "number of levels below E": "E より下の準位数",
  "trial Eₓ = {#} MeV: the line gives {#} levels for {#} counted": "試行 Eₓ = {#} MeV：直線は{#}準位（数えたのは{#}準位）",
  "F = {#}": "F = {#}",
  "F(Eₓ): predicted minus counted (signed log scale)": "F(Eₓ)：予測数 − 実数（符号つき対数目盛）",
  "bisection step {#}: [{#}, {#}]": "二分法 {#}回目：[{#}, {#}]",
  "root Eₓ = {#} MeV": "根 Eₓ = {#} MeV",
  // scene 4: no root
  "below: {#}/T with T = {#} MeV (Fermi-gas T)": "下側：{#}/T、T = {#} MeV（フェルミガスのT）",
  "below: {#}/T with T = {#} MeV (empirical T)": "下側：{#}/T、T = {#} MeV（経験的なT）",
  "above: Fermi gas, T = {#} MeV": "上側：フェルミガス、T = {#} MeV",
  "slope jumps by {#} % at Eₓ = {#} MeV": "傾きの跳び {#} %（Eₓ = {#} MeV）",
  "tangent at Eₓ = {#} MeV: no jump": "Eₓ = {#} MeVで接線：跳びなし",
  "ln ρ, lead-like nucleus (A = {#}, δW = {#} MeV)": "ln ρ、鉛に似た原子核（A = {#}, δW = {#} MeV）",
  "F changes sign: a root exists": "Fは符号を変える：根が存在する",
  "F(Eₓ) never reaches zero: no matching energy": "F(Eₓ)はゼロに達しない：接続エネルギーなし",
  // scene 5: D0
  "measured {#} ± {#} keV": "測定値 {#} ± {#} keV",
  "computed D₀ = {#} keV": "計算値 D₀ = {#} keV",
  "ã × {#} = {#} MeV⁻¹ · σ² = {#} · ρ(Sₙ) = {#} per MeV": "ã × {#} = {#} MeV⁻¹ · σ² = {#} · ρ(Sₙ) = {#} /MeV",
  "ã × {#} = {#} MeV⁻¹ · σ² = {#} · ρ(Sₙ) = {#}e{#} per MeV": "ã × {#} = {#} MeV⁻¹ · σ² = {#} · ρ(Sₙ) = {#}e{#} /MeV",
  "s-wave resonances above Sₙ, {#} keV shown: about {#} levels": "Sₙより上のs波共鳴、{#} keV分を表示：約{#}準位",
  // "iron-57" is read as the number −57, refilled here as "鉄-57"
  "iron{#}-like compound nucleus, Sₙ = {#} MeV, spin and parity ½⁺": "鉄{#}に似た複合核、Sₙ = {#} MeV、スピンとパリティ ½⁺",
});
Object.assign(WT.L.glossary, {
  gilbertCameron: {
    term: "Gilbert–Cameron", aliases: ["Gilbert–Cameron"],
    short: "低エネルギーの定温度模型の式を、接続エネルギーより上のフェルミガスにつないだ複合的な準位密度で、つなぎ目で値と傾きが等しくなるようにします。",
    more: "1965年にA. GilbertとA. G. W. Cameronが提案しました。TALYSとエンジンの既定（ldmodel 1）で、Ignatyukのエネルギー依存の準位密度パラメータと組み合わせて使います。",
    chapter: "densities",
  },
  ignatyuk: {
    term: "Ignatyuk", aliases: ["Ignatyuk"],
    short: "Ignatyukによる準位密度パラメータの形です。殻補正は低い励起では完全に効き、エネルギーとともに弱まるので、a(U)はなめらかな値に近づきます。",
    formula: "a(U) = ã [1 + δW (1 − e^(−γU)) / U]",
    chapter: "densities",
  },
});
