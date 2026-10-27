/* Japanese: decay (第9章、崩壊) */
WT.L.ch.decay = {
  num: "第9章", title: "出口を選ぶ", short: "崩壊",
  lead: "複合核は、粒子か光子を放出してエネルギーを手放さなければなりません。この章では、それぞれの出口を1枚の扉として描きます。エンジンの仕事は、流束（ここに到達する反応の流れ）のうちどれだけの割合が各扉から出ていくかを示すことです。",
  html: `
<div class="step">
  <p>出口ごとに1枚の扉があります。<em class="g">光子</em>（γ）、<em class="n">中性子</em>（n）、<em class="p">陽子</em>（p）、<em class="a">アルファ粒子</em>（α：陽子2個と中性子2個）、そして重い原子核に限り<em class="f">核分裂</em>（2つに割れること）です。各扉の光っている隙間がその出口の割合で、玉も同じ割合で流れ出ていきます。灰色の扉は閉じています。どのようにできたかを忘れた原子核は、各扉bを重みに比例して使います。</p>
  <div class="formula">割合<sub>b</sub> = T<sub>b</sub> · ρ<sub>b</sub> / Σ<sub>c</sub> T<sub>c</sub> · ρ<sub>c</sub></div>
  <p><b>透過係数</b><i>T</i>は、縁に達した粒子が通り抜ける確率です。粒子の場合は、第5章の光学模型を逆向きに使って求めます。各扉の横に書かれた<b>準位密度</b>ρは、残された原子核が行き着ける状態の数を数えたものです。<i>T</i>×ρで分け合うのが<b>ハウザー・フェッシュバッハ</b>の規則です。10 MeVでは中性子の扉がほぼすべてを持っていきます。</p>
</div>
<div class="step">
  <h3>ほとんどの粒子が遅く出てくる理由</h3>
  <p>中性子の扉を、出ていくエネルギーεごとに分けたものです（左が遅く、右が速い）。各扉の隙間<i>T</i>(ε)は、速い中性子ほど広がります。その下には、残された原子核がとりうる状態の群れがあります。遅い中性子はエネルギーの大部分を後に残し、そこでは状態が豊富なので、群れは右へ行くほど小さくなります。</p>
  <div class="ctl"><label for="dc-sp">余剰エネルギー</label><input id="dc-sp" type="range" data-bind="spare" min="1" max="12" step="0.5" value="5"><output data-show="spare" data-fmt="1"></output></div>
  <p>扉×群れで、山はこぶの形になります。これが<b>蒸発スペクトル</b>で、熱い液体から立ちのぼる湯気のようなものです。余剰エネルギー（MeV、100万電子ボルト単位）を動かしてみましょう。山は積み直されますが、そのピークは原子核温度で決まる約1 MeV付近にとどまります。余分なエネルギーは主に残された原子核をより熱くするのです。</p>
</div>
<div class="step">
  <h3>荷電粒子は登らなければならない</h3>
  <p>中心からの距離rごとの陽子のエネルギーです。内側は井戸で、外側には電気的（クーロン）斥力による丘があり、1/rのように下がっていきます。丘の頂上より低いエネルギーでは、井戸の中で跳ね回る陽子は、影をつけた区間を<b>トンネル</b>で抜けるしかありません。これは量子効果で、壁に何度もぶつかるうち一度だけ成功します。</p>
  <div class="ctl"><label for="dc-ce">粒子のエネルギー</label><input id="dc-ce" type="range" data-bind="eps" min="0.5" max="12" step="0.1" value="3"><output data-show="eps" data-fmt="1"></output></div>
  <div class="btns"><button class="btn ghost" data-act="toggleAlpha">陽子／α粒子を切り替え</button></div>
  <p>エネルギーを下げて、トンネルが広がるのを見てみましょう。次にα粒子に切り替えると、電荷が2つあるため約2倍の高さの丘に向き合います。電荷のない中性子が、出られるようになると普通は勝ってしまうのはこのためで、陽子やα粒子の出口が重要になるのは主に軽い原子核と高いエネルギーの場合です。</p>
</div>
<div class="step">
  <h3>扉は1枚ずつ開く</h3>
  <p>各粒子の扉は、その粒子を取り出すコストである<b>分離エネルギー</b>より上でしか開きません。ここでは中性子が8 MeV、陽子が9 MeV、α粒子が7 MeVです。中性子の8 MeVより下では、ほぼすべての崩壊が光を出します。</p>
  <div class="ctl"><label for="dc-e">励起エネルギー</label><input id="dc-e" type="range" data-bind="E" min="5" max="24" step="0.1" value="7"><output data-show="E" data-fmt="1"></output></div>
  <p>励起エネルギーを8 MeVより上へ動かしてみましょう。約1 MeV以内で中性子の扉が大きく開き、光子の割合は100分の1に落ちます。陽子とα粒子の扉はもっと後で光り、クーロンの丘に阻まれて狭いままです。</p>
</div>
<div class="step">
  <h3>スピンとパリティはつり合わなければならない</h3>
  <p>複合核（上）はスピン<i>J</i>をもちます。残された原子核の状態は、下にスピン<i>J</i>′ごとの引き出しとして並んでいます。中性子はスピンとパリティの差を持ち去ります。軌道角運動量<i>l</i>で出ていく中性子は、スピンを最大<i>l</i> + ½だけ変え、<i>l</i>が奇数ならパリティを反転させます。<i>l</i>が大きいほど扉は狭くなります。各引き出しの扉は、そこに届く最小の<i>l</i>のものです。塗りつぶしの着地はパリティを保ち、白抜きは反転します。</p>
  <div class="ctl"><label for="dc-j">複合核のスピン J</label><input id="dc-j" type="range" data-bind="J" min="0" max="10" step="1" value="2" data-instant><output id="dc-jout">5/2</output></div>
  <p><i>J</i>を上げてみましょう。開いた扉は状態の少ない高スピンの引き出しのほうへ移り、状態でいっぱいの引き出しは閉じた扉の向こうに残ります。高スピンの複合核はなかなか粒子を放出しないので、光子や核異性体（長寿命の状態、第10章）に機会が回ってきます。</p>
</div>
<div class="step">
  <h3>入ってきた道</h3>
  <p>低エネルギーでは、複合核は鋭い<b>共鳴</b>の集まりです。共鳴とは中性子が吸収されやすいエネルギーのことで、ここでは1行に1つずつ8個描いています。それぞれの扉の幅はランダムです。左が入口（中性子チャネル）で幅<i>x</i>、右がその他の扉（ここではほとんど光子）で幅<i>y</i>です。</p>
  <div class="btns"><button class="btn" data-act="fire">中性子を40個撃つ</button><button class="btn ghost" data-act="reroll">新しい共鳴</button></div>
  <p>中性子は<i>x<sub>i</sub></i>に比例する確率で共鳴<i>i</i>に入り、<i>x<sub>i</sub></i> / (<i>x<sub>i</sub></i> + Σ<i>y</i>)の確率で入口から出ていきます。入口の広い行ほど多くの中性子が入り、多くを送り返すので、戻ってくる本当の割合（<b>積の平均</b>）は平均幅から見積もった値（<b>平均の積</b>）を上回ります。その比が<b>弾性増大</b>で、<b>幅ゆらぎ補正</b>はその分の流束をその他の扉から入口へ移します。</p>
  <div class="ctl"><label for="dc-n">その他の扉</label><input id="dc-n" type="range" data-bind="Nch" min="1" max="12" step="1" value="2" data-instant><output data-show="Nch" data-fmt="0"></output></div>
  <p>扉を増やしてみましょう。出口が多いと全幅のゆらぎがなくなるので、この補正が最も重要になるのは開いている扉が少ないときです。エンジンはモルダウアーの公式でこれを、標的の中性子分離エネルギーまでの入射中性子に適用し、それより上では省きます。</p>
</div>
<div class="step">
  <h3>分け合うために残るもの</h3>
  <p>吸収された中性子がすべて複合核をつくるわけではありません。一度かすめて当たって飛び去るもの（直接反応、第6章）もあれば、一度か二度ぶつかって速く飛び出すもの（前平衡、第7章）もあります。残りだけがとどまって原子核を温めます。カウンターがそれぞれの運命を数えます。</p>
  <div class="ctl"><label for="dc-einc">中性子エネルギー</label><input id="dc-einc" type="range" data-bind="Einc" min="1" max="30" step="0.5" value="8"><output data-show="Einc" data-fmt="1"></output></div>
  <p>扉の競争に加わるのは、とどまったものだけです。中性子エネルギーを動かしてみましょう。数MeVではほぼすべてがとどまり、30 MeVでは約半数が平衡に達する前に出ていきます。</p>
  <div class="aside">コードでは：<code>compound/prepare.py</code>（スピンとパリティごとの出口の重みT·ρ、選択則）、<code>compound/target.py</code>（幅ゆらぎを含む最初の崩壊）、<code>compound/continuum.py</code>（その後の各ビンの崩壊）、<code>compound/wfc.py</code>（Moldauer、HRTW、GOEの補正）、<code>compound/normalization.py</code>（複合核に残る流束）、<code>omp/inverse.py</code>（扉を逆向きに使う）。</div>
</div>`,
};
(function () {
  const L = {
    "{#} MeV": "{#} MeV",
    "n": "n", "p": "p", "fission": "核分裂",
    "heavy only": "重い核のみ",
    "heavy nuclei only": "重い原子核のみ",
    "shut below {#} MeV": "{#} MeV未満は閉",
    "the neutron door takes nearly everything": "中性子の扉がほぼすべてを取る",
    "below the neutron threshold, nearly all decays emit light": "中性子しきい値未満：ほぼすべて光を放出",
    "the doors share the decays": "扉が崩壊を分け合う",
    // hump
    "{#} MeV to spare": "余剰 {#} MeV",
    "door gap = T(ε)": "隙間 = T(ε)",
    "doors: one per neutron energy ε, gap = T(ε)": "扉：中性子エネルギーεごとに1枚、隙間 = T(ε)",
    "× states left behind": "× 残る状態",
    "× states the leftover nucleus can be in: many after a slow neutron": "× 残る原子核の状態数：遅い中性子の後ほど多い",
    "most ≈ {#} MeV": "最多 ≈ {#} MeV",
    "= the pile": "= 山",
    "= where the neutrons land: the evaporation spectrum": "= 中性子の行き先：蒸発スペクトル",
    "slow": "遅い",
    "slow neutrons": "遅い中性子",
    "fast: {#} MeV →": "速い：{#} MeV →",
    "fast: {#} MeV (beyond, up to {#}, almost none)": "速い：{#} MeV（その先{#}までほぼゼロ）",
    "fast: {#}": "速い：{#}",
    "fast: {#} MeV, the neutron takes it all": "速い：{#} MeV、中性子が全部持ち去る",
    // coulomb
    "well ↓": "井戸 ↓",
    "well (much deeper) ↓": "井戸（はるかに深い）↓",
    "hilltop ≈ {#} MeV": "頂上 ≈ {#} MeV",
    "falls as {#}/r": "{#}/r で減少",
    "Coulomb hill, falling as {#}/r": "クーロンの丘、{#}/r で減少",
    "tunnel: wider than the picture": "トンネル：図より広い",
    "tunnel {#} fm": "トンネル {#} fm",
    "proton energy {#} MeV": "陽子エネルギー {#} MeV",
    "alpha energy {#} MeV": "α粒子エネルギー {#} MeV",
    "proton energy {#} MeV ↑": "陽子エネルギー {#} MeV ↑",
    "alpha energy {#} MeV ↑": "α粒子エネルギー {#} MeV ↑",
    "above the hilltop: it rolls straight out": "頂上より上：そのまま転がり出る",
    "below the top, must tunnel: nearly every knock gets through": "頂上より下でトンネル：ほぼ毎回通過",
    "below the top, must tunnel: about {#} knock in {#} gets through": "頂上より下でトンネル：通過は約{#}回 / {#}回",
    "below the top, must tunnel: about {#} knock in {#} × {#}^{#} gets through": "頂上より下でトンネル：通過は約{#}回 / {#} × {#}^{#}回",
    "out": "外へ",
    "through after {#} knock": "{#}回目で通過",
    "through after {#} knocks": "{#}回目で通過",
    "knocks so far: {#}": "これまでの衝突：{#}回",
    "distance r from the centre (fm) →": "中心からの距離 r (fm) →",
    // spin
    "J = {#}/{#}, parity +": "J = {#}/{#}、パリティ ＋",
    "l={#}": "l={#}",
    "leftover states by spin J′ →": "残る状態（スピンJ′別）→",
    "drawers: states of the leftover nucleus by spin J′ (faint: states it holds) →": "引き出し：残る原子核のスピンJ′別の状態（淡色：状態数）→",
    "open doors reach {#} %": "開いた扉は{#}%に届く",
    "open doors reach about {#} % of the states": "開いた扉は状態の約{#}%に届く",
    "● parity kept (even l)   ○ flipped (odd l)": "● パリティ保存（l偶数）   ○ 反転（l奇数）",
    // wfc
    "entrance x": "入口 x",
    "entrance, width x": "入口、幅 x",
    "{#} other doors, y": "その他の扉{#}枚、y",
    "{#} other door, widths y": "その他の扉{#}枚、幅 y",
    "{#} other doors, widths y": "その他の扉{#}枚、幅 y",
    "back out the entrance: {#} of {#}": "入口から戻る：{#} / {#}",
    "out another door: {#}": "他の扉から：{#}",
    // norm
    "absorbed neutrons, {#} MeV →": "吸収された中性子、{#} MeV →",
    "direct: {#} %": "直接：{#}%",
    "pre-equilibrium: {#} %": "前平衡：{#}%",
    "compound nucleus: {#} %": "複合核：{#}%",
    "one glancing hit on the surface": "表面を一度かすめる",
    "a knock or two, then out fast": "1、2回ぶつかって速く出る",
    "stayed: on to the door competition": "とどまる：扉の競争へ",
  };
  // door hint with level-count wording (fmt: "1", "N", "N thousand", "N million") and T possibly in e-notation
  const cnt = [["{#} state", "{#}状態"], ["{#} states", "{#}状態"], ["{#} thousand states", "{#}千状態"], ["{#} million states", "{#}百万状態"]];
  for (const [e, s] of cnt) {
    L[`weak door × ≈ ${e}`] = `弱い扉 × ≈ ${s}`;
    L[`T ≈ {#} × ≈ ${e}`] = `T ≈ {#} × ≈ ${s}`;
    L[`T ≈ {#}e{#} × ≈ ${e}`] = `T ≈ {#}e{#} × ≈ ${s}`;
  }
  // share comparisons: each pct is "{#} %" or "≈ {#} %"
  const P = ["{#} %", "≈ {#} %"];
  for (const a of P) for (const b of P) {
    L[`back out ${a}, not ${b}: × {#}`] = `戻る ${a}（${b}ではない）：× {#}`;
    L[`share back out: average of products ${a} · product of averages ${b} · × {#}`] = `戻る割合：積の平均 ${a} · 平均の積 ${b} · × {#}`;
    L[`other doors ${a}, not ${b}`] = `他の扉 ${a}（${b}ではない）`;
    L[`other doors together: ${a} instead of ${b}`] = `他の扉の合計：${a}（${b}ではなく）`;
  }
  Object.assign(WT.L.labels, L);
})();
