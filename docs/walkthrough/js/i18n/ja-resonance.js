/* Japanese: resonance (第15章、共鳴) */
WT.L.ch.resonance = {
  num: "第15章", title: "鋭いピーク", short: "共鳴",
  lead: "エネルギーが十分に低くなると、中性子にはもう、なめらかに平均された原子核は見えません。見えるのは複合核の個々のエネルギー準位で、それも1つずつです。",
  html: `
<div class="step">
  <p>各ピークが1つの<b>共鳴</b>です。共鳴とは複合核のエネルギー準位で、ちょうどそのエネルギーをもつ中性子が落ち込むことができます。ピークの高さはそこでの<b>捕獲</b>断面積（中性子が吸収され光子が出る）を対数目盛で表し、幅は共鳴幅Γで、実際の約100倍の幅で描いています。</p>
  <div class="ctl"><label for="res-e">中性子エネルギー（eV）</label><input id="res-e" type="range" data-bind="En" min="0.5" max="300" step="0.1" value="30"><output data-show="En" data-fmt="1"></output></div>
  <p>中性子はエネルギー軸に沿って跳ねていき、着地したところで光子の閃光とともに捕獲されることがあります。ピークの上では断面積は数千バーンに達し、捕獲はほぼ確実です。ピークの間では数バーンです。エネルギーを動かして、ピークの上に止めたり、2つのピークの間に止めたりしてみましょう。</p>
</div>
<div class="step">
  <h3>ピークは互いに距離を保つ</h3>
  <p>真ん中の行は、実際の準位の並び方を示しています。同じスピンとパリティをもつ2つの準位は反発し合うので、ほとんど重なることはまれです。この並び方を記述するのが<b>ランダム行列理論</b>です。まったくランダムな位置（上の行）では、固まったり隙間ができたりします。</p>
  <div class="btns"><button class="btn" data-act="again">もう一度描く</button></div>
  <p>「もう一度描く」で新しいサンプルが出ます。⟨r̃⟩は各間隔を次の間隔と比べたもので、ランダムなら約0.39、反発し合う準位なら0.53です。コードは反発し合うパターンを使います。2つの系列、たとえば2つのスピン（下の行）を混ぜると、反発は部分的に隠れます。</p>
</div>
<div class="step">
  <h3>高さは激しくばらつく</h3>
  <p>今度は各ピークの高さが、線形目盛での<b>中性子幅</b>Γ<sub>n</sub>、つまりその準位が中性子とどれだけ強く結合しているかを表します。黄色の帽子はγ幅Γ<sub>γ</sub>で、光子をどれだけ速く放出するかを表します。何百もの光子の経路を足し合わせたものなので、どの準位でもほぼ同じです。</p>
  <div class="btns"><button class="btn" data-act="roll">幅を1つ引く</button><button class="btn ghost" data-act="equal">等しい幅</button><button class="btn ghost" data-act="pt">ポーター・トーマス</button></div>
  <p>準位が中性子と標的に分かれる道は1つしかないので、その幅は正規分布に従う1つの数の2乗のようにふるまいます。1つ引いてみましょう。玉が<i>x</i>に着地し、<i>x</i>²が次のピークの高さになり、点が1つ山に落ちます。山はゼロ付近に集まり、長い裾を引きます。これが<b>ポーター・トーマス分布</b>です。ほとんどの準位は弱く、ごく一部が巨大です。「等しい幅」では、代わりに平均的なピークが並びます。</p>
</div>
<div class="step">
  <h3>4つの数からつくる共鳴列</h3>
  <p>今度のピークは、設定できる4つの平均値から生成されます。測定のない原子核について予測できるのはこれらの平均値だけです。平均準位間隔<i>D</i><sub>0</sub>、s波（正面衝突）とp波（中心から外れた）中性子についての単位間隔あたりの平均中性子幅である<b>強度関数</b><i>S</i><sub>0</sub>と<i>S</i><sub>1</sub>、そして平均γ幅です。コードはこれらから<b>共鳴列</b>、すなわちこれらの平均値をもつランダムな準位の組を1つつくります。</p>
  <div class="ctl"><label for="res-d0">間隔 D₀（eV）</label><input id="res-d0" type="range" data-bind="D0" min="3" max="60" step="0.5" value="20"><output data-show="D0" data-fmt="1"></output></div>
  <div class="ctl"><label for="res-s0">強度 S₀（×10⁻⁴）</label><input id="res-s0" type="range" data-bind="S0" min="0.2" max="3" step="0.05" value="1"><output data-show="S0" data-fmt="2"></output></div>
  <div class="ctl"><label for="res-gg">γ幅 ⟨Γγ⟩（meV）</label><input id="res-gg" type="range" data-bind="Gg" min="10" max="80" step="1" value="23"><output data-show="Gg" data-fmt="0"></output></div>
  <p><i>D</i><sub>0</sub>を動かすと、ピークが広がったり密集したりします。塗りつぶしのピークはs波の準位（正パリティ）、輪郭だけのピークはp波（負パリティ）です。中性子幅はs波では√<i>E</i>、p波では<i>E</i><sup>3/2</sup>のように増えるので、輪郭のピークは低く始まり、右へ行くほど高くなります。</p>
</div>
<div class="step">
  <h3>熱エネルギーまで下りる</h3>
  <p>同じピークを、1000分の1 eVまでの対数エネルギー目盛で描いたものです。原子炉の中性子は軽い原子核に跳ね返りながら減速し、そのたびにエネルギーのほぼ同じ割合を失うので、ここでは跳びの長さがどれも同じになります。途中でピークにつかまるものもあります。</p>
  <div class="btns"><button class="btn" data-act="slow">中性子10個を減速させる</button></div>
  <p>通り抜けたものは室温の0.025 eV、すなわち<b>熱エネルギー</b>に落ち着きます。これは最初のピークよりはるかに下です。そこでの断面積（円盤の面積）は、ゼロのすぐ下にある束縛準位も含めた共鳴の裾の和です。裾は1/<i>v</i>（<i>v</i>は中性子の速さ）のように増えるので、地面は左へ行くほど高くなります。下りる途中で捕まる量を測るのが<b>共鳴積分</b>で、0.5 eV以上の断面積を、各エネルギーに1/<i>E</i>の重みをつけて足し合わせたものです。</p>
</div>
<div class="step">
  <h3>予測できるのは統計だけ</h3>
  <p>各行は同じ4つの数から引いた1つの共鳴列で、円盤の面積はその熱中性子捕獲断面積です。かぎ括弧はその値を決めるピーク、普通は最も近いピークまで伸びています。その距離は共鳴列ごとに変わり、円盤は10倍以上も変動します。</p>
  <div class="btns"><button class="btn" data-act="draw1">共鳴列を1つ引く</button><button class="btn ghost" data-act="more">20個引く</button></div>
  <p>各値は右の山に落ちます。測定のない原子核では、答えは1つの数ではなく値の広がりであり、どれほど良い模型でもそれを狭めることはできません。多数のピークにわたる和である共鳴積分は、ばらつきがより小さくなります。軽い原子核のように準位の間隔が約10 keVを超えると、熱エネルギーの近くに準位はありません。そこでの捕獲は直接捕獲であり、コードは答えを出しません。</p>
  <div class="aside">コードでは：<code>physics/resonance/ladder.py</code>（ランダム行列の間隔、ポーター・トーマス分布の幅、Breit–Wigner断面積、アンサンブル上での熱中性子捕獲と共鳴積分）、<code>ladder_statistics.py</code>（同じ法則を測定された共鳴列で検証）、<code>ensemble_runner.py</code>。これらは反応エンジンの内部ではなく、その横で動きます。</div>
</div>`,
};
Object.assign(WT.L.labels, {
  // forest
  "{#} eV": "{#} eV", "+{#} eV": "+{#} eV",
  "height: peak capture (log) · width Γ ×{#}": "高さ：ピーク捕獲（対数）· 幅 Γ ×{#}",
  "peak height: capture cross section (log scale) · width: resonance width Γ, drawn {#}× wide": "高さ：捕獲断面積（対数目盛）· 幅：共鳴幅Γ（{#}倍で描画）",
  "D₀ {#} eV · S₀ {#}×{#}⁻⁴ · S₁ {#}×{#}⁻⁴ · ⟨Γγ⟩ {#} meV": "D₀ {#} eV · S₀ {#}×{#}⁻⁴ · S₁ {#}×{#}⁻⁴ · ⟨Γγ⟩ {#} meV",
  "s-wave (+ parity)": "s波（＋パリティ）", "p-wave (− parity)": "p波（−パリティ）",
  "caught {#} times in {#} landings": "捕獲 {#}回 / 着地 {#}回",
  "each peak: one level of the compound nucleus": "各ピーク：複合核の準位1つ",
  "each peak: one level of the compound nucleus · about {#} eV apart": "各ピーク：複合核の準位1つ · 間隔約{#} eV",
  // spacing
  "random positions (Poisson)": "ランダムな位置（ポアソン）",
  "repelling levels (random-matrix)": "反発する準位（ランダム行列）",
  "two repelling sequences mixed": "反発する2系列の混合",
  "clumps and gaps · ⟨r̃⟩ ≈ {#}": "固まりと隙間 · ⟨r̃⟩ ≈ {#}",
  "evenly kept apart · ⟨r̃⟩ ≈ {#}": "均等に離れる · ⟨r̃⟩ ≈ {#}",
  "repulsion half hidden · ⟨r̃⟩ ≈ {#}": "反発が半ば隠れる · ⟨r̃⟩ ≈ {#}",
  "clumps and gaps · spacing ratio ⟨r̃⟩ ≈ {#}": "固まりと隙間 · 間隔比 ⟨r̃⟩ ≈ {#}",
  "evenly kept apart · spacing ratio ⟨r̃⟩ ≈ {#}": "均等に離れる · 間隔比 ⟨r̃⟩ ≈ {#}",
  "repulsion half hidden · spacing ratio ⟨r̃⟩ ≈ {#}": "反発が半ば隠れる · 間隔比 ⟨r̃⟩ ≈ {#}",
  "⟨r̃⟩: {#} if random, {#} for random-matrix": "⟨r̃⟩：ランダムなら{#}、ランダム行列なら{#}",
  "same average spacing in every row · ⟨r̃⟩: {#} if random, {#} for random-matrix": "どの行も平均間隔は同じ · ⟨r̃⟩：ランダムなら{#}、ランダム行列なら{#}",
  // Porter-Thomas
  "height: neutron width Γn (linear)": "高さ：中性子幅 Γn（線形）",
  "peak height: neutron width Γn, linear scale": "ピークの高さ：中性子幅 Γn、線形目盛",
  "yellow: γ width": "黄色：γ幅",
  "yellow cap: γ width, nearly the same on every peak": "黄色の帽子：γ幅、どのピークでもほぼ同じ",
  "equal widths: every peak the average": "等しい幅：全ピークが平均値",
  "rolled widths": "引いた幅", "pile of rolled widths": "引いた幅の山",
  "× average": "× 平均", "(in units of the average)": "（平均を単位として）",
  "dashed: Porter–Thomas": "点線：ポーター・トーマス", "dashed: the Porter–Thomas law": "点線：ポーター・トーマス分布",
  "bell-curve number x": "正規分布の数 x",
  "x = {#}  →  x² = {#}": "x = {#}  →  x² = {#}",
  "press Roll a width": "「幅を1つ引く」を押す",
  // thermal
  "bound level {#} eV": "束縛準位 {#} eV",
  "a bound level at {#} eV: its tail lifts this end": "{#} eVの束縛準位：その裾がこの端を持ち上げる",
  "resonance integral ≈ {#} b": "共鳴積分 ≈ {#} b",
  "resonance integral above {#} eV ≈ {#} b": "{#} eV以上の共鳴積分 ≈ {#} b",
  "{#}/v": "{#}/v",
  "caught by a peak on the way down: {#} · reached thermal: {#}": "途中でピークに捕獲：{#} · 熱エネルギーに到達：{#}",
  "each hop: one bounce, the same fraction of energy lost": "1回の跳び：1回の衝突、同じ割合のエネルギーを失う",
  // ensemble
  "thermal neutron": "熱中性子",
  "σ disc": "σの円盤", "disc area = σ at {#} eV": "円盤の面積 = {#} eVでのσ",
  "{#}k": "{#}k",
  "thermal σ (b)": "熱中性子σ (b)", "thermal σ, barns": "熱中性子σ、バーン",
  "{#} ladders · thermal ×{#} · res. integral ×{#}": "共鳴列{#}個 · 熱 ×{#} · 共鳴積分 ×{#}",
});
// labels that carry a cross section printed as "12 b" or "3.4k b"
(function () {
  const L = WT.L.labels;
  for (const b of ["{#} b", "{#}k b"]) {
    L[b] = b;
    L[`σ ≈ ${b} · caught on {#} % of landings`] = `σ ≈ ${b} · 着地の{#}%で捕獲`;
    L[`σ ≈ ${b} · caught on <{#} % of landings`] = `σ ≈ ${b} · 着地の<{#}%で捕獲`;
    L[`thermal, {#} eV: σ ≈ ${b}`] = `熱エネルギー {#} eV：σ ≈ ${b}`;
    L[`{#} ladders · thermal σ median ${b}, middle two thirds ×{#} · resonance integral only ×{#}`] =
      `共鳴列{#}個 · 熱中性子σの中央値 ${b}、中央3分の2で ×{#} · 共鳴積分はわずか ×{#}`;
  }
})();
