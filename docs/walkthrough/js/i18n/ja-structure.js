/* Japanese: structure (第1章、原子核は何でできているか) */
WT.L.ch.structure = {
  num: "第1章", title: "原子核は何でできているか", short: "構造",
  lead: "エンジン（私たちの反応計算ソフトウェア）は、中性子を1個撃ち込む前に、標的原子核の記述を必要とします。どれだけ強く結びついているか、どんなエネルギー状態をとりうるか、そしてどんな形をしているか、です。",
  html: `
<div class="step">
  <p>図は鉄の原子核です。<em class="p">陽子</em>と<em class="n">中性子</em>（<b>核子</b>）がぎっしり詰まった球で、到達距離の短い<b>強い力</b>で結びついています。各核子はすぐ隣の核子しか感じないので、どの原子核もほぼ同じ密度をもちます。</p>
  <div class="ctl"><label for="st-n">中性子数（鉄の陽子は26個）</label><input id="st-n" type="range" data-bind="N" min="24" max="38" step="1" value="30" data-instant><output data-show="N" data-fmt="0"></output></div>
  <p>ドラッグして中性子を増やしたり減らしたりしてみましょう。選ぶたびに別の<b>同位体</b>になります。棒グラフは核子あたりの<b>結合エネルギー</b>をMeV（100万電子ボルト）で示します。原子核をばらばらにするのに必要なエネルギーです。安定同位体の付近で最大になります。</p>
</div>
<div class="step">
  <h3>1個取り出すためのコスト</h3>
  <p>粒子を1個取り出すのに必要なエネルギーが<b>分離エネルギー</b>です。中性子なら<i>S<sub>n</sub></i>、陽子なら<i>S<sub>p</sub></i>、<b>アルファ粒子</b>（陽子2個と中性子2個が結合したもの）なら<i>S<sub>α</sub></i>です。図では原子核を井戸として描き、上ほどエネルギーが高くなります。取り出すたびにいちばん上の粒子が点線の「自由」の線の外へ持ち上げられ、メーターがそのコストを記録します。</p>
  <div class="btns"><button class="btn ghost" data-act="pn">中性子を取り出す</button><button class="btn ghost" data-act="pp">陽子を取り出す</button><button class="btn ghost" data-act="pa">α粒子を取り出す</button></div>
  <p>エンジンはそれぞれを2つの原子核の質量の差として求めます。質量は可能なかぎり測定値を使い、測定がなければ質量模型から求めます。</p>
  <div class="ctl"><label for="st-n2">中性子数</label><input id="st-n2" type="range" data-bind="N" min="24" max="38" step="1" value="30" data-instant><output data-show="N" data-fmt="0"></output></div>
  <p>中性子数を動かして、もう一度中性子を取り出してみましょう。<i>S<sub>n</sub></i>はジグザグに変わります。核子は対をつくり、偶数個のときは最後の1個がより強く束縛されるからです。反応で粒子が飛び出せるのは、このコストを払えるだけのエネルギーを持ち込んだときだけです。これらのコストが、計算全体の<b>しきい値</b>になります。</p>
</div>
<div class="step">
  <h3>エネルギー準位と、その落ち方</h3>
  <p>原子核が余分にもてるエネルギーは、決まった値だけです。それが横線で、ここでは鉄56の例を示し、いちばん下が<b>基底状態</b>です。各準位は<b>スピン</b><i>J</i>（角運動量）と<b>パリティ</b>＋または−（波動が鏡に映しても同じに見えるかどうか）をもちます。2<sup>+</sup>はスピン2、パリティ＋という意味です。</p>
  <p>オレンジの玉は高い準位にある原子核です。1段ずつ落ちていき、そのたびにエネルギー差を運ぶ<em class="g">光子</em>（ガンマ線）を放出します。経路の太さとパーセントは各遷移の測定された確率、つまり<b>分岐比</b>です。</p>
  <div class="btns"><button class="btn" data-act="drop">原子核を励起する</button></div>
  <p>何度か押してみましょう。同じ準位から、さまざまな経路で基底状態に達します。エンジンは原子核ごとに約30個の測定済み準位をその確率とともに保持し、それより上では密集した準位をなめらかな<b>連続領域</b>として扱います。点線<i>S<sub>n</sub></i>より上では、原子核は中性子を放出できます。</p>
</div>
<div class="step">
  <h3>簡単には下りられない準位</h3>
  <p>下りる道が大きなスピン変化Δ<i>J</i>を必要とする経路しかない準位は、非常にゆっくり崩壊します。右側では64個の原子核がそのような準位にいます。それぞれランダムな時間だけ待ってから落ち、<em class="g">光子</em>が飛び出します。<b>半減期</b>が1回たつと、半数が落ちています。</p>
  <div class="ctl"><label for="st-dj">スピン変化 ΔJ</label><input id="st-dj" type="range" data-bind="dJ" min="1" max="5" step="1" value="2" data-instant><output data-show="dJ" data-fmt="0"></output></div>
  <div class="ctl"><label for="st-eg">光子エネルギー（MeV）</label><input id="st-eg" type="range" data-bind="Eg" min="0.05" max="1.5" step="0.05" value="0.3"><output data-show="Eg" data-fmt="2"></output></div>
  <div class="btns"><button class="btn ghost" data-act="excite">すべて励起する</button></div>
  <p>Δ<i>J</i>を上げると、飛び出しが遅くなります。スピンが1単位増えるごとに待ち時間は10万倍以上長くなり、光子エネルギーが低くても長くなります（対数目盛で表示）。寿命がおよそ1秒より長い準位は<b>核異性体</b>で、エンジンはこれを基底状態と同様に終点として扱います。</p>
</div>
<div class="step">
  <h3>丸いか、丸くないか</h3>
  <p>多くの原子核は丸くありません。<i>β₂</i>（「ベータ・ツー」）は引き伸ばしの度合いを表します。0なら球、正ならアメリカンフットボールのように伸び、負なら円盤のようにつぶれた形です。右のはしごは、それぞれの形がつくる準位を示します。</p>
  <p>引き伸ばされた原子核は回転でき、0<sup>+</sup>、2<sup>+</sup>、4<sup>+</sup>、6<sup>+</sup>の準位を、<i>J</i>(<i>J</i>+1)のように広がる間隔でつくります。これが<b>回転体</b>です。丸い原子核は表面を波打たせることができます。波打ちの1単位、すなわち<b>フォノン</b>は毎回同じエネルギーを加えるので、準位は等間隔に並びます。これが<b>振動体</b>です。</p>
  <div class="ctl"><label for="st-beta">変形 β₂</label><input id="st-beta" type="range" data-bind="beta" min="-0.3" max="0.45" step="0.01" value="0.28"><output data-show="beta" data-fmt="2"></output></div>
  <div class="btns"><button class="btn ghost" data-act="still">静止</button><button class="btn ghost" data-act="vib">振動</button><button class="btn ghost" data-act="rot">回転</button></div>
  <p><i>β₂</i>を動かしてボタンを押してみましょう。伸びが大きいほど、回転体の準位は互いに近づきます。エンジンは原子核ごとの変形と、球形・振動体・回転体のいずれかという分類を保存しています。第3章では、通りすがりの中性子がそれをどう使うかを示します。</p>
</div>
<div class="step">
  <h3>しきい値のすぐ上の指紋</h3>
  <p>標的に加わった遅い中性子は、<i>S<sub>n</sub></i>のすぐ上、左側の小さな箱の中に着地します。右のパネルはその箱を数千倍に拡大したもので、中性子エネルギーが左から右へ増えていきます。</p>
  <div class="ctl"><label for="st-fe">ビームエネルギー</label><input id="st-fe" type="range" data-bind="fe" min="0" max="1" step="0.001" value="0.3" data-instant><output id="st-fe-out"></output></div>
  <div class="btns"><button class="btn ghost" data-act="fplay" id="st-fplay">掃引を一時停止</button></div>
  <p>ほとんどのエネルギーでは、ビームはそのまま素通りします。ところが特定のエネルギーでは、中性子と原子核の組が隠れた準位にぴったり合い、ビームの多くが取り込まれます。これが<b>共鳴</b>です。ピークの上では描かれた原子核が膨らみます。実際に大きさが変わるのではなく、中性子の波が原子核の波と重なることで、中性子から見た実効的な標的が大きくなるのです。その後、原子核はエネルギーを<em class="g">光子</em>か中性子として返します。曲線は取り込まれた割合を示し、棒は見つかった共鳴の位置を示します。</p>
  <div class="btns"><button class="btn ghost" data-act="fFe">鉄56</button><button class="btn ghost" data-act="fAu">金197</button><button class="btn ghost" data-act="fU">ウラン238</button></div>
  <p>原子核はそれぞれ固有のスケールで固有のバーコードをもちます。鉄の共鳴の間隔は数千電子ボルト、金やウランでは数十電子ボルトです。これを3つの平均値で要約します。平均の間隔<i>D₀</i>、どのピークでもほぼ同じ<b>光子幅</b>⟨Γ<sub>γ</sub>⟩、そして遅い中性子がどれだけ入りやすいかを表す<b>強度関数</b><i>S₀</i>です。</p>
  <p>それぞれが後の段階の検証に使われます。エンジンの準位密度パラメータは原子核ごとに<i>D₀</i>に合わせてあり、⟨Γ<sub>γ</sub>⟩は光子放出を、<i>S₀</i>は次章の光学模型を検証します。測定のない原子核については、多くの原子核にわたって当てはめた系統的傾向を使います。</p>
  <div class="aside">コードでは：<code>structure/masses.py</code>（測定質量、その外側では模型の質量、分離エネルギー）、<code>structure/levels.py</code>（離散準位、分岐比、核異性体、推定スピン）と<code>levjpar.py</code>（任意、既定ではオフ：その原子核にありえないスピンが登録されていれば推定し直す）、<code>structure/deformation.py</code>（β₂と球形・振動体・回転体の分類）と<code>collrule.py</code>（任意、既定ではオフ：標的の分類を測定済み準位から選ぶ）、<code>structure/resonances.py</code>（D₀、S₀、S₁、⟨Γγ⟩）。</div>
</div>`,
};
(function () {
  const L = {
    // scene: packed drop
    "{#}Fe": "{#}Fe",
    "{#} protons · {#} neutrons": "陽子{#}個 · 中性子{#}個",
    "binding energy per nucleon: about {#} MeV": "核子あたりの結合エネルギー：約{#} MeV",
    "binding per nucleon, one bar per isotope →": "核子あたりの結合、同位体ごとに1本 →",
    // scene: well
    "free": "自由",
    "free: outside the nucleus": "自由：原子核の外",
    "neutrons": "中性子",
    "protons": "陽子",
    "an alpha forms from the top pairs": "上の対からα粒子ができる",
    "neutron {#}": "中性子 {#}",
    "proton {#}": "陽子 {#}",
    "alpha {#}": "α {#}",
    "n {#}": "n {#}",
    "p {#}": "p {#}",
    "energy paid": "払ったエネルギー",
    "energy to pull": "取り出すエネルギー",
    "(MeV)": "(MeV)",
    "each one out (MeV)": "1個ごと (MeV)",
    "higher mark =": "印が高い =",
    "harder to remove": "取り出しにくい",
    "pulling out a neutron: {#} MeV paid": "中性子を取り出す：{#} MeV",
    "pulling out a proton: {#} MeV paid": "陽子を取り出す：{#} MeV",
    "pulling out an alpha: {#} MeV paid": "α粒子を取り出す：{#} MeV",
    // scene: levels and gamma drops
    "continuum: too many levels to list": "連続領域：準位が多すぎて列挙不能",
    "neutron threshold Sₙ ≈ {#} MeV": "中性子しきい値 Sₙ ≈ {#} MeV",
    "ground state": "基底状態",
    "MeV": "MeV",
    "each line: an energy, a spin J and a parity (±)": "各線：エネルギー、スピンJ、パリティ(±)",
    "path width and % = measured odds of each hop": "経路の太さと% = 各遷移の測定確率",
    // scene: isomer
    "ground": "基底",
    "J = {#}/{#}": "J = {#}/{#}",
    "ΔJ = {#}": "ΔJ = {#}",
    "still excited: {#} of {#}": "励起のまま：{#} / {#}",
    "longer than a second: an isomer, a stop in its own right": "1秒以上：核異性体、独立した終点",
    "shown slowed down (log scale)": "スロー表示（対数目盛）",
    "shown slowed down: the slower they pop, the longer the real wait (log scale)": "スロー表示：遅いほど実際の待ち時間も長い（対数目盛）",
    // scene: shape
    "ripples at the surface: a vibrator": "表面が波打つ：振動体",
    "stretched and rotating: a rotor": "伸びて回転：回転体",
    "round: a sphere": "丸い：球",
    "stretched (prolate): a football": "伸びた形（プロレート）：ラグビーボール",
    "squashed: an oblate disc": "つぶれた形：オブレートな円盤",
    "{#} phonons": "フォノン{#}個",
    "no regular": "規則的な",
    "level pattern": "準位パターンなし",
    "spacing grows like J(J+{#})": "間隔は J(J+{#}) のように増加",
    "equal steps, one phonon each": "等間隔、1段ごとにフォノン1個",
    "its lowest levels": "最低の準位",
    "β₂ = {#}": "β₂ = {#}",
    // scene: resonance fingerprint
    "continuum": "連続領域",
    "Sₙ ≈ {#} MeV": "Sₙ ≈ {#} MeV",
    "slow neutron": "遅い中性子",
    "a slow neutron lands here:": "遅い中性子はここに着地：",
    "lands here": "ここに着地",
    "Sₙ + its kinetic energy": "Sₙ + 運動エネルギー",
    "×{#} million": "×{#}百万",
    "×{#} thousand": "×{#}千",
    "magnified": "拡大",
    "swells on a peak: the size the neutron effectively “sees” (waves overlap), not a real size change": "ピークで膨らむ：中性子が実効的に「見る」大きさ（波の重なり）で、実際の大きさの変化ではない",
    "share taken in": "取り込まれた割合",
    "share of the beam taken in": "ビームが取り込まれた割合",
    "{#} (Sₙ)": "{#} (Sₙ)",
    "{#} = exactly Sₙ": "{#} = ちょうど Sₙ",
    "{#} keV": "{#} keV",
    "{#} eV": "{#} eV",
    "neutron energy →": "中性子エネルギー →",
    "neutron's kinetic energy →": "中性子の運動エネルギー →",
    "D₀ ≈ {#} keV: the average gap": "D₀ ≈ {#} keV：平均間隔",
    "D₀ ≈ {#} eV: the average gap": "D₀ ≈ {#} eV：平均間隔",
    "S₀: average peak strength": "S₀：ピークの平均強度",
    "S₀: how strong the peaks are on average (how easily a neutron gets in)": "S₀：ピークの平均強度（中性子の入りやすさ）",
    "⟨Γγ⟩ ≈ {#} eV: photon width": "⟨Γγ⟩ ≈ {#} eV：光子幅",
    "⟨Γγ⟩ ≈ {#} eV: photon width, about the same for every peak": "⟨Γγ⟩ ≈ {#} eV：光子幅、どのピークでもほぼ同じ",
    "⟨Γγ⟩ ≈ {#} eV: a hairline here": "⟨Γγ⟩ ≈ {#} eV：ここでは髪の毛ほど",
    "⟨Γγ⟩ ≈ {#} eV: a hairline here; neutrons widen these peaks": "⟨Γγ⟩ ≈ {#} eV：ここでは髪の毛ほど。中性子がピークを広げる",
    "peaks drawn about {#}× wider than life so they show": "見やすいようピーク幅を約{#}倍に拡大して描画",
  };
  // beam readout and per-target labels
  for (const u of ["keV", "eV"]) L[`beam of neutrons at {#} ${u}`] = `中性子ビーム {#} ${u}`;
  const EL = { iron: "鉄", gold: "金", uranium: "ウラン" };
  for (const en in EL) {
    L[`${en}{#} levels`] = `${EL[en]}{#}の準位`;
    L[`${en}{#}: took in {#} of the last {#}`] = `${EL[en]}{#}：{#}個を吸収（直近{#}個中）`;
  }
  // isomer half-life in every unit fmtTime can produce
  const TU = { femtoseconds: "フェムト秒", picoseconds: "ピコ秒", nanoseconds: "ナノ秒", microseconds: "マイクロ秒",
    milliseconds: "ミリ秒", seconds: "秒", minutes: "分", hours: "時間", days: "日", years: "年" };
  for (const en in TU) L[`half-life about {#} ${en}`] = `半減期 約{#} ${TU[en]}`;
  L["half-life about {#}×{#}^{#} years"] = "半減期 約{#}×{#}^{#} 年";
  Object.assign(WT.L.labels, L);
})();
