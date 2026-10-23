/* Japanese: cascade (第8章、カスケード) */
WT.L.ch.cascade = {
  num: "第8章", title: "核図表を下る", short: "カスケード",
  lead: "1回の放出で終わることはまれです。後に残された原子核は、もう一度放出できるほど熱いことが多いのです。",
  html: `
<div class="step">
  <p>中性子が複合核（左）を離れ、後に残された<b>残留核</b>（右）はまだ熱い状態です。オレンジの玉がエネルギーです。残留核の基底状態は、中性子を取り出すコストである<b>分離エネルギー</b>S<sub>n</sub>の分だけ高い位置にあります。</p>
  <p>中性子が出ていくたびに、玉は中性子の運動エネルギーの分だけ落ちます。止まった位置が残留核の<b>励起エネルギー</b>、つまり余剰エネルギーです。右の点は着地の数を数えています。</p>
  <div class="ctl"><label for="cs-e">中性子エネルギー</label><input id="cs-e" type="range" data-bind="E" min="1" max="30" step="0.5" value="15"><output data-show="E" data-fmt="1"></output></div>
  <p>放出される中性子はたいてい遅いので、ほとんどの落下は短くなります。青い点は点線の中性子しきい値より上にあり、2個目の中性子を出す余裕があります。これが(n,2n)反応です。約11 MeVより下では、そこまで届くものはありません。</p>
</div>
<div class="step">
  <h3>核図表を歩く</h3>
  <p>流れは、<b>核図表</b>の一角を歩いていく反応です。核図表は原子核を中性子数N（横）と陽子数Z（縦）で並べた地図です。どの反応も枠で囲まれた複合核のマスから始まり、各マスにはそこで終わる反応の名前がついています。</p>
  <p><em class="n">中性子</em>が出ると1マス左へ、<em class="p">陽子</em>なら1マス下へ、<em class="a">アルファ粒子</em>（陽子2個と中性子2個）なら斜めに2マス動きます。流れの幅はその一歩をたどる量で、濃さとパーセントは反応がどこで終わるかを示します。</p>
  <div class="btns"><button class="btn" data-act="fire">反応を200回実行</button></div>
  <p>一歩ごとに7〜11 MeVの分離エネルギーがかかるので、30 MeVでも歩けるのはせいぜい3、4歩です。</p>
</div>
<div class="step">
  <h3>上から下へ、ビンごとに</h3>
  <p>エンジンは各原子核を上から順に、エネルギーの薄切り、すなわち<b>ビン</b>を1つずつ空にしていきます。右は最初の放出で生じた残留核、左はその娘核で、中性子が1個少ないものです。オレンジの玉は各ビンで待っている反応です。ここではビンは1 MeVですが、エンジンは利用できるエネルギーに合わせて原子核ごとに約40個使います。</p>
  <p>目印がビンを通過すると、各玉は第6章の競争によって出口を選びます。光子（<em class="g">γ</em>）なら下のビンへ落ち、<em class="n">中性子</em>なら娘核へ移り、陽子やα粒子なら図の外へ出ます。すべてのしきい値より下では、光子が残りを基底状態（灰色）まで運びます。その後、娘核が掃引されます。</p>
  <div class="ctl"><label for="cs-e3">中性子エネルギー</label><input id="cs-e3" type="range" data-bind="E" min="8" max="30" step="0.5" value="18"><output data-show="E" data-fmt="1"></output></div>
  <div class="btns"><button class="btn ghost" data-act="restart">最初から</button></div>
  <p>光子は下へ落ちるだけで、各原子核はその娘核より先に処理が終わるので、すでに空になったビンに何かが着地することはありません。</p>
</div>
<div class="step">
  <h3>履歴に名前をつける</h3>
  <p>反応を1つずつ再生します。目印が核図表の上を跳び、放出された粒子はそれぞれトレイに落ちます。いっぱいになったトレイが<b>排他的チャネル</b>の名前、たとえば(n,2n)を表します。光子は数えません。エンジンは各チャネルに固有の断面積（実効的な標的面積として表した起こりやすさ）を与えます。</p>
  <div class="btns"><button class="btn ghost" data-act="next">次のチャネル</button></div>
  <p>順に見ていきましょう。(n,np)は2回再生されます。中性子が先の場合と陽子が先の場合で、マスもトレイも同じなので1つのチャネルです。次に、幽霊のような重陽子（陽子と中性子が束縛したもの）が1回の跳びでそのマスに達します。そのトレイにはdと書かれ、別のチャネル(n,d)になります。</p>
</div>
<div class="step">
  <h3>すべてはどこで終わるか</h3>
  <p>各マスには棚があります。墨色は<b>基底状態</b>、緑（2つのマス）は<b>核異性体</b>で、別の生成物として数えるほど長寿命の励起状態です。山の高さが<b>残留核生成</b>、つまり反応によって各原子核がどれだけつくられたかを表します。</p>
  <div class="ctl"><label for="cs-e2">中性子エネルギー</label><input id="cs-e2" type="range" data-bind="E" min="1" max="30" step="0.5" value="14"><output data-show="E" data-fmt="1"></output></div>
  <div class="btns"><button class="btn" data-act="fire">反応を200回実行</button></div>
  <p>エネルギーを動かすと、次の一群はその値を使い、古い山は薄れていきます。より多くの粒子が出られるようになると、生成は出発点から遠ざかります。どの履歴も棚の上で終わり、放射化測定が見るのはまさにこの山です。試料を照射し、各生成物の崩壊を数えるのです。</p>
  <div class="aside">コードでは：<code>emission/multiple.py</code>（原子核とビンにわたるループ、γ線カスケード）、<code>emission/feeding.py</code>（連鎖の各原子核の格子と入力）、<code>compound/continuum.py</code>（1つのビンの崩壊）、<code>emission/channels.py</code>（排他的チャネル、残留核生成、核異性体への分岐）、<code>emission/binary.py</code>（最初の放出の記録）。</div>
</div>`,
};
Object.assign(WT.L.labels, {
  // reaction names on the squares (unchanged)
  "(n,γ)": "(n,γ)", "(n,n′)": "(n,n′)", "(n,{#}n)": "(n,{#}n)", "(n,p)": "(n,p)", "(n,np)": "(n,np)", "(n,{#}np)": "(n,{#}np)",
  "(n,{#}p)": "(n,{#}p)", "(n,n{#}p)": "(n,n{#}p)", "(n,α)": "(n,α)", "(n,nα)": "(n,nα)",
  "compound": "複合核", "target": "標的",
  "N{#}": "N{#}", "N": "N", "N+{#}": "N+{#}", "Z": "Z", "Z{#}": "Z{#}",
  "neutron number →": "中性子数 →",
  // scene 1
  "levels": "準位",
  "Sₙ {#} MeV": "Sₙ {#} MeV", "Sₙ = {#} MeV": "Sₙ = {#} MeV",
  "ground": "基底",
  "residual": "残留核", "residual (one neutron fewer)": "残留核（中性子1個少ない）",
  "n threshold": "nしきい値", "its neutron threshold": "その中性子しきい値",
  "{#} MeV": "{#} MeV",
  "drop = neutron's kinetic energy": "落下 = 中性子の運動エネルギー",
  "{#} % land above the threshold: a second neutron can leave": "{#}%がしきい値より上：2個目の中性子が出られる",
  "<{#} % land above the threshold: a second neutron can leave": "<{#}%がしきい値より上：2個目の中性子が出られる",
  "all land below the threshold: only photons remain": "すべてしきい値より下：残るは光子のみ",
  "{#} % above threshold: (n,{#}n) possible": "{#}%がしきい値より上：(n,{#}n)が可能",
  "<{#} % above threshold: (n,{#}n) possible": "<{#}%がしきい値より上：(n,{#}n)が可能",
  "all below threshold: photons only": "すべてしきい値より下：光子のみ",
  // scene 2
  "incoming neutron: {#} MeV": "入射中性子：{#} MeV",
  "shade and % = where reactions end": "濃さと% = 反応の終点",
  "stream width = flow · shade and % = share of reactions that end in that nucleus": "幅 = 流れ · 濃さと% = その原子核で終わる反応の割合",
  // scene 3
  "residual (first step)": "残留核（第1段）",
  "daughter: n fewer": "娘核：n 1個少ない", "daughter (one neutron fewer)": "娘核（中性子1個少ない）",
  "now: {#}–{#} MeV": "現在：{#}–{#} MeV", "{#}–{#} MeV": "{#}–{#} MeV",
  "done: {#} left by proton or alpha, the rest sit on ground states": "完了：{#}個は陽子かα粒子で離脱、残りは基底状態",
  "done: everything sits on a ground state": "完了：すべて基底状態",
  "orange ball = reactions waiting in a bin · grey = settled on the ground state · pale bins = already emptied": "オレンジの玉 = ビンで待つ反応 · 灰色 = 基底状態に落ち着いた · 淡いビン = 処理済み",
  // scene 4
  "collected": "収集",
  "tray: d": "トレイ：d",
  "a deuteron lands on the same square, but its tray reads d: channel (n,d)": "重陽子も同じマスに着くが、トレイはd：チャネル(n,d)",
  "tray: n n  →  (n,{#}n)": "トレイ：n n  →  (n,{#}n)",
  "tray: n  →  (n,n′)": "トレイ：n  →  (n,n′)",
  "tray: p  →  (n,p)": "トレイ：p  →  (n,p)",
  "tray: n p  →  (n,np)": "トレイ：n p  →  (n,np)",
  "tray: n p  →  (n,np) · same square, same tray": "トレイ：n p  →  (n,np) · 同じマス、同じトレイ",
  "tray: a  →  (n,α)": "トレイ：a  →  (n,α)",
  "tray: n n n  →  (n,{#}n)": "トレイ：n n n  →  (n,{#}n)",
  "tray empty, only photons: (n,γ), capture": "トレイは空、光子のみ：(n,γ)、捕獲",
  "each emitted particle falls into the tray": "放出された粒子はトレイに落ちる",
  "no particle gets out: only photons": "粒子は出ない：光子のみ",
  "incoming neutron: {#} MeV · channel {#} of {#}": "入射中性子：{#} MeV · チャネル {#} / {#}",
  // scene 5
  "isomer": "核異性体",
  "batch of {#} at {#} MeV": "{#}個の一群（{#} MeV）",
  "ink shelf: ground state · green: isomer": "墨色：基底状態 · 緑：核異性体",
  "ink shelf: ground state · green shelf: isomer · pile height = how much of that nucleus was made": "墨色の棚：基底状態 · 緑の棚：核異性体 · 山の高さ = その原子核の生成量",
});
