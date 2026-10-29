/* Japanese: preeq (第7章、前平衡) */
WT.L.ch.preeq = {
  num: "第7章", title: "前平衡放出", short: "前平衡",
  lead: "原子核に入った中性子は、そのエネルギーを一度に全員と分け合うわけではありません。最初の何回かの衝突のあいだは、1個の粒子がエネルギーの大部分をもっていて、その粒子はそのまま外へ飛び出すことができます。これが前平衡、つまり「エネルギーが均等になる前」の放出です。",
  html: `
<div class="step">
  <p>2つの井戸があり、一方は<em class="p">陽子</em>、もう一方は<em class="n">中性子</em>のものです。各玉はエネルギー準位にある核子で、準位ははしごの段として描かれています。段は下から<b>フェルミ面</b>まで埋まっています。点線の「自由」の線より上の核子は、外へ逃げ出せるだけのエネルギーをもっています。エンジンは陽子と中性子を別々に追跡します。</p>
  <p>入ってきた中性子は上に浮かんでいて、すべてのエネルギーをもっています。自身の運動エネルギーに加えて、捕獲によって解放された数MeV（100万電子ボルト）です。</p>
</div>
<div class="step">
  <h3>粒子・空孔励起</h3>
  <p>速い中性子は海の中の核子にぶつかり、エネルギーの一部を渡します。その核子は空いた段へ跳び上がり、もといた場所は空になります。これが<b>空孔</b>（白抜きの輪）です。つまりぶつかるたびに<b>対</b>ができます。持ち上げられた核子が1個増え、空孔が1個増えるのです。持ち上げられた核子と空孔をまとめて数え、<b>エキシトン</b>と呼びます。最初にぶつかったあとは3個（持ち上げられた核子2個と空孔1個）です。</p>
  <div class="btns"><button class="btn" data-act="collide">衝突させる</button><button class="btn ghost" data-act="reset">最初から</button></div>
  <p>「衝突させる」を押して、1回のぶつかりを見てみましょう。飛び込み、跳び上がり、空孔ができます。何度か繰り返してください。ぶつけられる核子は陽子のことも中性子のこともあります。ぶつかるたびにエネルギーはより多くの核子で分け合われるので、持ち上げられた核子はそれぞれ低くなり、速い粒子が逃げ出す確率も下がります。</p>
</div>
<div class="step">
  <h3>放出とさらなる衝突</h3>
  <p>各段階で、いちばん上の中性子は逃げ出す（上向きの矢印、自由の線より上にいる場合のみ）か、もう一度衝突する（下向きの矢印）かのどちらかです。矢印の太さが確率を表します。逃げ出す割合は逆の事象から読み取れます。あるエネルギーの中性子を吸収しやすい原子核は、そのエネルギーの中性子を放出しやすくもあるのです。どれだけ吸収しやすいかは第5章でもう計算しました（この双方向の規則を<b>詳細つり合い</b>と呼びます）。衝突の割合は、2つの核子がどれだけ強くぶつかるかに、ぶつかったあとエネルギーを分け合う新しい方法がいくつあるかを掛けたものです。</p>
  <div class="ctl"><label for="pe-n">段階（エキシトン数 n）</label><input id="pe-n" type="range" data-bind="n" min="3" max="11" step="2" value="3" data-instant><output data-show="n" data-fmt="0"></output></div>
  <p>段階を上げてみましょう。初めのうちは1個の粒子がエネルギーの大部分をもっているので、逃げ出すものは速いです。あとになるとエネルギーは薄く広がり、ほとんど出てこなくなります。</p>
</div>
<div class="step">
  <h3>前平衡スペクトル</h3>
  <p>右の山は<b>スペクトル</b>です。各エネルギーでどれだけの中性子が出てくるかを表し、左が遅く右が速い中性子です。各反応はいちばん上の中性子が逃げ出すまで連鎖を進め、その色がいつ逃げたかを示します。段階3なら<em style="font-style:normal;color:var(--warm);font-weight:600">濃いオレンジ</em>、あとになるほど淡く、原子核が落ち着いてから（第8章）出てきたものは<em class="n">青</em>です。</p>
  <div class="btns"><button class="btn" data-act="run">反応を300回実行</button></div>
  <p>段階3は、最大エネルギーのほぼ近くまで広がる幅広く低いドームをつくります。そこまで届くのはこの段階だけです。あとの段階はより低いところに積もります。青いこぶは<b>蒸発</b>です。全員がエネルギーを分け合うようになると、熱い液体から湯気が立つように、遅い中性子だけが少しずつ出てきます。</p>
  <div class="ctl"><label for="pe-e">中性子エネルギー</label><input id="pe-e" type="range" data-bind="E" min="5" max="60" step="0.5" value="20"><output data-show="E" data-fmt="1"></output></div>
  <p>入射中性子のエネルギーを動かすと、新しい一群が実行され、ドームがさらに伸びます。蒸発だけでは決して速い中性子は生まれません。</p>
</div>
<div class="step">
  <h3>粒子・空孔状態密度</h3>
  <p>カウンターは、粒子を空いた段に、空孔を埋まった段に置き、そのエネルギーの合計が分け合うべきエネルギーに等しくなるような置き方を、すべて数え上げていきます（ここでは段の間隔は1 MeVです）。核子はフェルミ粒子なので、2個が同じ段に入ることはありません。粒子は空いた段にしか入れず、空孔は核子がいた場所にしかできません。これが<b>パウリ・ブロッキング</b>です。</p>
  <div class="ctl"><label for="pe-u">分け合うエネルギー（MeV）</label><input id="pe-u" type="range" data-bind="U" min="2" max="16" step="1" value="8" data-instant><output data-show="U" data-fmt="0"></output></div>
  <div class="btns"><button class="btn" data-act="addpair">対を加える</button><button class="btn ghost" data-act="droppair">対を取り除く</button></div>
  <p>対を加えると数が跳ね上がり、エネルギーを上げるとおよそ<i>E</i><sup>n−1</sup>のように増えます。この数、<b>粒子・空孔状態密度</b>が衝突の割合を決めます。配置が多いほど、衝突の行き先も多いのです。エンジンは段の間隔がMeVの数分の1という実際のはしごで数え、高エネルギーで目に見える制限を1つ加えます。空孔は井戸の底より下には置けません。</p>
</div>
<div class="step">
  <h3>クラスター放出</h3>
  <p>小さなクラスターも早い段階で出ていくことがあります。<b>ピックアップ</b>では、外へ向かう陽子が表面で中性子をつかみ、一緒に<em class="n">重陽子</em>として出ていきます。2個つかめば三重陽子かヘリウム3になります。<b>ノックアウト</b>では、入射中性子が表面付近にすでにできている<em class="a">アルファ粒子</em>（陽子2個と中性子2個）に当たり、それを叩き出します。エンジンはどちらにもカルバッハの公式を使います。</p>
  <div class="btns"><button class="btn ghost" data-act="pickup">中性子をピックアップ → d</button><button class="btn ghost" data-act="knock">αをノックアウト</button></div>
  <p>ボタンを押して見てみましょう。どちらも重陽子やアルファ粒子に独自の速い裾を与え、その裾はそれぞれを取り出すのに必要なエネルギーのすぐ上から始まります。</p>
</div>
<div class="step">
  <h3>多重前平衡放出</h3>
  <p>高エネルギーでは、最初にぶつかったときにぶつけられた核子にも多くのエネルギーが渡ることがあります。速い中性子が出ていくとき、その2個目の核子がまだ、外へ出るのに必要な8 MeV（自由の線）より多くのエネルギーをもっていれば、それも飛び出します。1回の反応から速い粒子が2個出るのです。図は反応を1回ずつ再生し、各瞬間に何が起こるかを説明します。各玉の横の数はそのエネルギーです。</p>
  <div class="ctl"><label for="pe-e2">中性子エネルギー</label><input id="pe-e2" type="range" data-bind="E" min="5" max="80" step="0.5" value="40"><output data-show="E" data-fmt="1"></output></div>
  <p>エネルギーを動かしてみましょう。約20 MeV以下では2個目の核子が線を越えることはまれですが、それより上では、速い粒子を2個放出する反応がどんどん増えます。これが<b>多重前平衡放出</b>で、エンジンは20 MeV以上でこれを含めます。出ていかなかったものは、次章の複合核になります。数MeV（使用する標的の最も高い離散準位）以下では、エンジンはこの連鎖を完全に省きます。</p>
  <div class="aside">コードでは：<code>preeq/exciton.py</code>（2成分エキシトン連鎖、衝突と放出の割合）、<code>density/particle_hole.py</code>（パウリ補正と有限井戸補正つきの粒子・空孔状態密度）、<code>preeq/complex.py</code>（カルバッハのピックアップ、ストリッピング、αノックアウト）、<code>preeq/multi.py</code>（多重前平衡放出）、<code>compound/normalization.py</code>（複合核への引き渡し）。</div>
</div>`,
};
Object.assign(WT.L.labels, {
  // wells
  "protons": "陽子",
  "neutrons": "中性子",
  "Fermi": "フェルミ",
  "Fermi surface": "フェルミ面",
  "free": "自由",
  "free: can escape": "自由：逃げ出せる",
  "all the energy in one nucleon": "全エネルギーが1個の核子に",
  "{#} particle, {#} holes": "粒子{#}個、空孔{#}個",
  // pairs
  "{#} particle, {#} holes: n = {#}": "粒子{#}個、空孔{#}個：n = {#}",
  "{#} particle, {#} hole: n = {#}": "粒子{#}個、空孔{#}個：n = {#}",
  "{#} particles, {#} hole: n = {#}": "粒子{#}個、空孔{#}個：n = {#}",
  "{#} particles, {#} holes: n = {#}": "粒子{#}個、空孔{#}個：n = {#}",
  "protons: {#} lifted, {#} hole": "陽子：{#}個上へ、空孔{#}個",
  "protons: {#} lifted, {#} holes": "陽子：{#}個上へ、空孔{#}個",
  "neutrons: {#} lifted, {#} hole": "中性子：{#}個上へ、空孔{#}個",
  "neutrons: {#} lifted, {#} holes": "中性子：{#}個上へ、空孔{#}個",
  "chain ends: the rest becomes a compound nucleus": "連鎖終了：残りは複合核に",
  // fork
  "about {#} MeV above surface": "面の約{#} MeV上",
  "escapes  {#}%": "逃げる  {#}%",
  "collides again  {#}%": "再衝突  {#}%",
  "below the free line: it cannot leave": "自由の線より下：出られない",
  "n = {#}: {#} particles, {#} hole, {#} MeV": "n = {#}：粒子{#}個、空孔{#}個、{#} MeV",
  "n = {#}: {#} particles, {#} holes, {#} MeV": "n = {#}：粒子{#}個、空孔{#}個、{#} MeV",
  "stage n = {#}: {#} particles and {#} hole share {#} MeV": "段階 n = {#}：粒子{#}個と空孔{#}個で{#} MeVを分配",
  "stage n = {#}: {#} particles and {#} holes share {#} MeV": "段階 n = {#}：粒子{#}個と空孔{#}個で{#} MeVを分配",
  // tail
  "max {#} MeV": "最大 {#} MeV",
  "slow": "遅い",
  "fast →": "速い →",
  "stage {#}": "段階 {#}",
  "chain over: compound": "連鎖終了：複合核",
  "left at:": "放出時：",
  "neutron left at:": "中性子の放出時：",
  "evaporation": "蒸発",
  "{#} of {#} landed · {#} left during the chain": "着地 {#} / {#} · 連鎖中の放出 {#}",
  // pauli
  "well bottom: no deeper hole": "井戸の底：これより深い空孔なし",
  "bottom of the well": "井戸の底",
  "{#} MeV to share": "分配する{#} MeV",
  "{#} particles · {#} hole": "粒子{#}個 · 空孔{#}個",
  "{#} particles · {#} holes": "粒子{#}個 · 空孔{#}個",
  "ways, all counted": "通り（全数）",
  "arrangements so far": "これまでの配置数",
  "one more pair: {#} ways": "もう1対：{#}通り",
  "never two on one rung · holes only where a nucleon was": "1段に2個は不可 · 空孔は核子がいた所のみ",
  "(first {#} shown as ticks)": "（最初の{#}個を目盛りで表示）",
  // cluster
  "a deuteron leaves": "重陽子が出る",
  "grabs a neutron at the edge": "縁で中性子をつかむ",
  "a fast proton heads out": "速い陽子が外へ",
  "an α ({#} protons + {#} neutrons) waits at the edge": "α（陽子{#}個 + 中性子{#}個）が縁で待つ",
  "knocked straight out": "そのまま叩き出される",
  // second
  "first fast neutron": "1個目の速い中性子",
  "second fast proton": "2個目の速い陽子",
  "second fast neutron": "2個目の速い中性子",
  "below the free line: stays": "自由の線より下：残る",
  "below the free line: it stays": "自由の線より下：残る",
  "the rest settles: compound nucleus": "残りは落ち着く：複合核",
  "{#} MeV carried in": "持ち込み {#} MeV",
  "second fast particle in {#} of the last {#} reactions": "2個目の速い粒子：{#}回（直近{#}回の反応中）",
});
