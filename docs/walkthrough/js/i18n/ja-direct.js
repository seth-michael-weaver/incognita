/* Japanese: direct (第3章、直接反応) */
WT.L.ch.direct = {
  num: "第3章", title: "かすめる一撃", short: "直接反応",
  lead: "原子核に届いた中性子が、すべて飲み込まれるわけではありません。表面をかすめ、一度だけ押して、そのまま飛び去るものもあります。",
  html: `
<div class="step">
  <p>原子核をかすめるだけの中性子は、原子核を一度押して励起準位に上げ、ほとんど前方へ、わずかに遅くなって飛び去ることがあります。これが<b>直接反応</b>です。1段階だけで、約10⁻²²秒で終わります。ここでは中性子が原子核半径<i>R</i>を単位とした距離<i>b</i>、つまり<b>衝突パラメータ</b>のところを通過します。点線の輪は原子核の表皮です。</p>
  <div class="ctl"><label for="di-b">狙い b（半径単位）</label><input id="di-b" type="range" data-bind="b" min="0" max="1.5" step="0.01" value="1.0"><output data-show="b" data-fmt="2"></output></div>
  <p><i>b</i>を動かしてみましょう。約0.8より小さいと中性子は飲み込まれます。1付近ではかすめて、原子核を第1励起準位2⁺に残します。約1.2より大きいと外れて曲がるだけです。これが<b>弾性散乱</b>で、原子核は変化しません。</p>
</div>
<div class="step">
  <h3>伸びた原子核を回す</h3>
  <p>押されると、伸びた原子核（第1章）は回転し、<b>回転バンド</b>のはしご0⁺、2⁺、4⁺、6⁺、8⁺を上っていきます。中性子は原子核を押し上げ、原子核も押し返すので、どの準位も単独では求められません。エンジンはすべてを同時に解きます。これが<b>チャネル結合</b>で、各チャネルは1つの結果、ここではバンドの1つの準位を表します。</p>
  <div class="btns"><button class="btn" data-act="kick">1段押し上げる</button><button class="btn ghost" data-act="rpause">一時停止／再開</button></div>
  <div class="ctl"><label for="di-beta">変形 β₂</label><input id="di-beta" type="range" data-bind="beta2" min="0.05" max="0.4" step="0.01" value="0.25"><output data-show="beta2" data-fmt="2"></output></div>
  <p>弧はどの準位どうしがつながっているかを示します。全体の伸びである<i>λ</i> = 2は隣どうしを、より細かな膨らみである<i>λ</i> = 4は2つ先をつなぎます。<i>β₂</i>を動かしてみましょう。伸びが大きい原子核ほど準位どうしを強く結びつけ、弧が太くなります。バンドは入射波と一緒に解かれるので、透過係数にはバンドが持っていく分があらかじめ除かれています。</p>
</div>
<div class="step">
  <h3>球の表面のさざ波</h3>
  <p>丸い原子核は表面を波打たせることができ、その波のエネルギーは<b>フォノン</b>と呼ばれる等しい塊でやりとりされます。ラグビーボールと円盤の間を行き来する波（<i>λ</i> = 2）のフォノン1個で2⁺準位ができ、2個では2倍のエネルギーに0⁺、2⁺、4⁺の3準位ができます。そこへ達するには2回続けて押す必要があります。エンジンはこれらの準位を基底状態と一緒に解きます。</p>
  <div class="ctl"><label for="di-lam">波の形 λ</label><input id="di-lam" type="range" data-bind="lam" min="2" max="3" step="1" value="2" data-instant><output data-show="lam" data-fmt="0"></output></div>
  <div class="btns"><button class="btn ghost" data-act="ph1">フォノン1個</button><button class="btn ghost" data-act="ph2">フォノン2個</button></div>
  <p><i>λ</i> = 3にすると洋梨形の波になり、最初の準位は3⁻です。ボタンを押してフォノンを1個または2個加えてみましょう。</p>
</div>
<div class="step">
  <h3>一度だけ押す</h3>
  <p>ほとんどの準位ではつながりが弱く、一度押すだけで十分です。これが<b>DWBA</b>（歪曲波ボルン近似）です。第2章の入射波が、ポテンシャルが深い値からゼロへ落ちる縁で原子核を一度押します。波の山が当たるところで縁が光ります。外へ広がる円形の波は、原子核を励起したまま去った中性子です。</p>
  <div class="ctl"><label for="di-bd">準位の変形 β</label><input id="di-bd" type="range" data-bind="bd" min="0.02" max="0.4" step="0.01" value="0.2"><output data-show="bd" data-fmt="2"></output></div>
  <p><i>β</i>を動かすと、縁が強く揺れ、円が<i>β</i>²に比例して明るくなります。変形が2倍なら4倍です。エンジンは各準位の<i>β</i>を測定値から、測定がなければ系統的傾向から取ります。散乱された中性子が角度ごとにどう分布するかは、任意の追加出力です。</p>
</div>
<div class="step">
  <h3>原子核全体が動く</h3>
  <p>すべての核子がまとまって動くこともできます。膨張と収縮、つぶれと伸び、洋梨形への揺れです。これらが<b>巨大共鳴</b>です。この中重核では約7〜25 MeVの高さにあり、それぞれ幅が数MeVもあるので、1つの準位とはみなせません。こぶがそれぞれの<b>励起エネルギー</b>を示しています。</p>
  <p>エンジンは、原子核がどれだけ強く応答できるかに対する基本物理からの上限である<b>和則</b>で各巨大共鳴の全強度を決め、それを既知の最後の準位より上にこぶとして広げます。これらのこぶと高い準位への押し上げを合わせたものが<b>集団的連続領域</b>です。</p>
  <div class="btns"><button class="btn ghost" data-act="mono">呼吸</button><button class="btn ghost" data-act="quad">つぶれ</button><button class="btn ghost" data-act="oct">洋梨</button></div>
  <p>最もよく知られた、陽子が中性子に対して揺れ動くもの（巨大双極子共鳴）は、主に光を吸収・放出するので、第7章で扱います。</p>
</div>
<div class="step">
  <h3>軌道へまっすぐ</h3>
  <p>自由な中性子が井戸の空いた<b>軌道</b>（内部で1個の中性子に許されるエネルギー）にまっすぐ落ち込み、余ったエネルギーを<em class="g">光子</em>として放出することがあります。原子核は熱くなりません。これが<b>直接捕獲</b>です。エンジンは第2章と同じ井戸からこれを計算できます。外の自由な波、内の束縛軌道、それらをつなぐ光子です。任意機能で、既定ではオフです。</p>
  <div class="btns"><button class="btn" data-act="drop">中性子を落とす</button></div>
  <p>直接捕獲が最も重要になるのは、中性子のエネルギーを分け合う通常の経路が弱い場合、つまり準位が少なく間隔の広い軽い原子核や、安定から遠く離れた原子核です。</p>
</div>
<div class="step">
  <h3>直接反応が先に取り分を取る</h3>
  <p>エンジンは第2章の反応断面積を順番に分けます。まず直接反応、次に速い衝突、そして残りだけが複合核をつくります。図では各中性子が3つの運命のどれかをたどります。<b>直接</b>（かすめて飛び去る）、速い衝突（エネルギーが広がる前に核子を叩き出す：<b>前平衡</b>、第4章）、または飲み込まれる（<b>複合核</b>、第5章）です。山がそれぞれの数を数えます。</p>
  <div class="ctl"><label for="di-e">中性子エネルギー（MeV）</label><input id="di-e" type="range" data-bind="E" min="1" max="60" step="0.5" value="14"><output data-show="E" data-fmt="1"></output></div>
  <p>エネルギーを動かして、山が積み直されるのを見てみましょう。数MeVではほぼすべての中性子が飲み込まれます。数十MeVでは、直接反応と速い衝突が合わせて大きな割合を占めます。</p>
  <div class="aside">コードでは：<code>ecis/formfactor.py</code>、<code>ecis/coupling.py</code>、<code>ecis/solver.py</code>（変形ポテンシャル、回転体と振動体のチャネル結合）、<code>ecis/dwba.py</code>と<code>direct/dwba.py</code>（一度だけの押し、巨大共鳴、集団的連続領域）、<code>direct/racapcalc.py</code>（直接捕獲、任意、既定ではオフ）、<code>compound/normalization.py</code>（収支表）。</div>
</div>`,
};
Object.assign(WT.L.labels, {
  // scene: aim
  "skin (surface)": "表皮（表面）",
  "b = {#} R": "b = {#} R",
  "absorbed: its energy is shared by all nucleons": "吸収：エネルギーを全核子で分け合う",
  "{#}⁺ level": "{#}⁺準位",
  "one push leaves the nucleus on {#}⁺; neutron flies on": "一押しで原子核は{#}⁺に、中性子は飛び去る",
  "a miss: deflected, nucleus unchanged (elastic)": "外れ：曲がるだけ、原子核は不変（弾性）",
  // scene: rotor
  "at rest: {#}⁺": "静止：{#}⁺",
  "rotating: {#}⁺": "回転：{#}⁺",
  "rotating: {#}⁺ (paused)": "回転：{#}⁺（一時停止）",
  "λ = {#}": "λ = {#}",
  "levels solved together": "準位を同時に解く",
  // scene: vibrator
  "quadrupole ripple: football ↔ disc": "四重極の波：ラグビーボール ↔ 円盤",
  "octupole ripple: pear ↔ pear": "八重極の波：洋梨 ↔ 洋梨",
  "{#}⁺  no phonon": "{#}⁺  フォノンなし",
  "{#}⁺  one phonon": "{#}⁺  フォノン1個",
  "{#}⁻  one phonon": "{#}⁻  フォノン1個",
  "{#}⁺ {#}⁺ {#}⁺  two phonons": "{#}⁺ {#}⁺ {#}⁺  フォノン2個",
  "{#}⁺ {#}⁺ {#}⁺ {#}⁺  two phonons": "{#}⁺ {#}⁺ {#}⁺ {#}⁺  フォノン2個",
  "one push": "1回押す",
  "two pushes": "2回押す",
  "two phonons": "フォノン2個",
  "equal energy steps": "等しいエネルギー間隔",
  // scene: DWBA
  "rim: the push happens here": "縁：ここで押す",
  "incoming wave": "入射波",
  "outgoing: nucleus left excited": "出射：原子核は励起状態",
  "outgoing circles: the nucleus left on an excited level": "出ていく円：原子核は励起準位に",
  "push strength ∝ β²: {#}× that at β = {#}": "押す強さ ∝ β²：{#}倍（β = {#} 比）",
  // scene: giant resonances
  "breathing": "呼吸",
  "squash and stretch": "つぶれと伸び",
  "pear": "洋梨",
  "breathing (monopole)": "呼吸（単極）",
  "squash and stretch (quadrupole)": "つぶれと伸び（四重極）",
  "pear-shaped (octupole), low and high": "洋梨形（八重極）、低と高",
  "about {#} MeV up": "約{#} MeV",
  "last known level": "既知の最後の準位",
  "excitation energy (MeV) →": "励起エネルギー (MeV) →",
  // scene: direct capture
  "free: outside the nucleus": "自由：原子核の外",
  "empty orbit": "空の軌道",
  "drops straight in; a photon carries off the spare energy": "まっすぐ落ちる。余ったエネルギーは光子が運ぶ",
  // scene: ledger
  "direct": "直接",
  "fast (pre-eq.)": "速い（前平衡）",
  "compound": "複合核",
  "direct: grazed, flew on": "直接：かすめて飛び去る",
  "fast collision: one out at once": "速い衝突：1個がすぐ出る",
  "compound: swallowed": "複合核：飲み込まれる",
  "{#}% (model {#}%)": "{#}%（模型 {#}%）",
  "{#}% seen · model {#}%": "観測 {#}% · 模型 {#}%",
  "{#} MeV neutrons on a medium-mass nucleus (illustrative shares)": "{#} MeV中性子 → 中重核（割合は説明用）",
});
