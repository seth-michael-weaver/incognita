/* Japanese: compound (第8章、複合核) */
WT.L.ch.compound = {
  num: "第8章", title: "複合核", short: "複合核",
  lead: "最初の速い衝突が終わると、すべての核子がエネルギーを分け合います。この落ち着いた状態が複合核です。それが次に何をするかを予測するために、エンジンは複合核がエネルギーを何通りの仕方で保持できるかを知る必要があります。",
  html: `
<div class="step">
  <p>中性子が原子核の片側に当たります。そのエネルギーは、捕獲で解放されたエネルギーと合わせて、最初は1か所に集まった熱い点（オレンジの光）です。衝突によって次々と受け渡され、約10⁻²¹秒のうちにすべての核子が分け前をもつようになります。</p>
  <div class="btns"><button class="btn" data-act="hit">別の側から当てる</button></div>
  <p>ボタンを押して、中性子を別の側から入れてみましょう。光は必ず同じ状態に落ち着きます。原子核は<b>どのようにできたかを忘れてしまう</b>のです。これがボーアの複合核です。ここから先で意味をもつのは3つの事実だけです。エネルギー、スピン（どれだけ回転しているか）、そしてパリティ（鏡映対称性を表す＋か−のラベル）です。</p>
</div>
<div class="step">
  <h3>離散準位から連続領域へ</h3>
  <p>左のはしごは原子核の状態を表し、上ほどエネルギーが高くなります。右の窓はオレンジの玉のまわり1 MeV分を拡大しています。下のほうでは段の間隔が広く、1つ1つが測定されています。上へ行くと、56個の核子でエネルギーを分け合う仕方が増えていき、ついには段がぼやけて一様な帯、すなわち連続領域になります。</p>
  <div class="ctl"><label for="cn-e">励起エネルギー</label><input id="cn-e" type="range" data-bind="E" min="0" max="20" step="0.1" value="6.5"><output data-show="E" data-fmt="1"></output></div>
  <p>励起エネルギー（最低の状態より上に蓄えられたエネルギー、MeV単位）を動かして、窓を見てみましょう。1 MeVあたりの状態数である<b>準位密度</b>ρは、およそe<sup>2√(aE)</sup>のように増えます。<i>a</i>は原子核ごとの増え方の速さを決めます。3 MeVでは1 MeVあたり数個、（中性子が逃げ出せる）8 MeV付近では数百個、20 MeVでは数百万個です。そこではエンジンはρそのものを使って計算します。</p>
</div>
<div class="step">
  <h3>複合準位密度</h3>
  <p>地形の高さは対数目盛での準位密度で、右へ行くほどエネルギーが高くなります。左下には数え上げた準位があります。まっすぐな板は<b>定温度模型</b>です。ρは<i>T</i> MeVごとにe倍（約2.7倍）になり、<i>T</i>は原子核温度です。丘の斜面は<b>フェルミガス</b>で、核子を独立な粒子として扱います。表になった密度を読み込む最も重い標的を除き、エンジンは既定でこの組み合わせを使います。</p>
  <div class="ctl"><label for="cn-ex">接続エネルギー</label><input id="cn-ex" type="range" data-bind="Ex" min="4.5" max="12" step="0.05" value="6"><output data-show="Ex" data-fmt="1"></output></div>
  <p>接続エネルギーを動かしてみましょう。つなぎ目が丘に沿って滑り、板は同じ高さと傾きでそこに合うように回転します。下の2つの柱は、板が予測する準位の数と実際に数えた準位の数を比べています。両者が等しくなるつなぎ目は1つだけで、そこで板が緑色に変わります。それがエンジンの選ぶエネルギーです。</p>
</div>
<div class="step">
  <h3>殻効果とその減衰</h3>
  <p>2つの原子核の1核子準位で、各準位には核子が2個ずつ入ります。左は閉殻で、大きなすき間より下がすべて埋まっているので、どんな移動にもすき間全体の分のエネルギーが必要です。右は殻の中間にある原子核で、いちばん上の準位が半分しか埋まっていないため、安い移動がすぐに可能です。各カウンターは、与えられた熱を保持できる配置の数を示します。</p>
  <div class="ctl"><label for="cn-u">熱（励起）</label><input id="cn-u" type="range" data-bind="U" min="0" max="40" step="0.5" value="3"><output data-show="U" data-fmt="1"></output></div>
  <p>熱を上げて、核子が跳び移る様子を見てみましょう。熱が低いと閉殻は配置の数が乏しいままですが、十分な熱があればすき間は問題でなくなり、両方の数は同じように増えます。エンジンはこれを原子核ごとに1つの数、<b>準位密度パラメータ</b><i>a</i>にまとめます。<i>a</i>が大きいほど、熱とともに配置の数が速く増えます。針は各原子核についてそれを示しており、離れたところから始まって、約10 MeVかけて両方が同じなめらかな値（<i>ã</i>と書き、「エー・チルダ」と読みます）に落ち着きます。これは殻のすき間をもたない原子核がもつはずの値です。</p>
  <p>そこでエンジンは、各原子核をまず殻効果（そのすき間が生む余分なエネルギーで、δWと書きます）とともに始め、熱が上がるにつれてその効果を弱めていきます。</p>
  <div class="aside">式は <i>a</i>(<i>U</i>) = <i>ã</i> · [1 + δW · (1 − e<sup>−γ<i>U</i></sup>) / <i>U</i>] です。<i>U</i>は熱、γ（ガンマ。ここでは約0.1 /MeV、重い原子核ではそれより小さい）は殻効果が弱まる速さを表します。</div>
</div>
<div class="step">
  <h3>スピンとパリティの分布</h3>
  <p>あるエネルギーでの状態は、原子核の角運動量であるスピン<i>J</i>ごとの引き出しに分けられます。＋パリティは塗りつぶしの玉、−は白抜きの玉です。真ん中の引き出しがいちばんよく埋まり、(2<i>J</i>+1) e<sup>−(J+½)²/2σ²</sup>に従います。スピンカットオフσが広がりを決めます。2つのパリティはほぼ同数になります。</p>
  <div class="ctl"><label for="cn-u2">励起</label><input id="cn-u2" type="range" data-bind="U2" min="1" max="30" step="0.5" value="8"><output data-show="U2" data-fmt="1"></output></div>
  <div class="btns"><button class="btn ghost" data-act="deform">原子核を変形させる</button></div>
  <p>励起を上げると、σが大きくなります。熱い原子核ほど大きなスピンを担えるからです。次に「原子核を変形させる」を押してみましょう。ラグビーボール形の原子核は全体として回転することもできるので、どの引き出しにも状態が増えます（青い玉）。これが<b>集団的増大</b>です。エンジンは既定では、核子数が約215より多い標的にだけこれを加えます。</p>
</div>
<div class="step">
  <h3>連続領域のエネルギービン</h3>
  <p>数え上げた最後の準位より上では、エンジンは連続領域を等しいエネルギー幅の薄切りに分けます。これをビンと呼びます。各ビンでは点が1つのブロック、ρ·ΔE個の状態（ΔEはビンの幅）にまとまり、上と同じようにスピンとパリティで仕分けられます。</p>
  <div class="ctl"><label for="cn-emax">はしごの上端</label><input id="cn-emax" type="range" data-bind="Emax" min="8" max="30" step="0.5" value="14"><output data-show="Emax" data-fmt="1"></output></div>
  <div class="btns"><button class="btn ghost" data-act="rebin">もう一度仕分ける</button></div>
  <p>中性子が持ち込める最大のエネルギーであるはしごの上端を動かしてみましょう。同じ数のビンでより広いエネルギーを覆わなければならないので、各ビンは背が高くなります。オレンジの玉はビンからビンへと落ちていきます。この後のすべての段階（出口の選択、光子カスケード、核図表を下る歩み）は、これらのビンの上で行われます。ここでは10個描いていますが、エンジンは最大40個使います。</p>
  <div class="aside">コードでは：<code>density/parameters.py</code>（Ignatyukの<i>a</i>(U)、スピンカットオフ、ウィグナー分布、集団的増大）、<code>density/models.py</code>（定温度模型、フェルミガス、数表）、<code>density/matching.py</code>（数え上げた準位から接続エネルギーを求める）、<code>core/grids.py</code>（励起エネルギーのビン）。</div>
</div>`,
};
(function () {
  const L = {
    // scene 1
    "a neutron comes in": "中性子が入射",
    "a hot spot: the energy is still local": "熱い点：エネルギーはまだ局所的",
    "equilibrium: every nucleon holds a share": "平衡：全核子が分け前をもつ",
    "no trace left of where it was hit": "どこに当たったかの痕跡はない",
    // scene 2
    "ground state": "基底状態",
    "{#}–{#} MeV, magnified": "{#}–{#} MeV（拡大）",
    "no level in this slice": "この範囲に準位なし",
    "{#} rung in {#} MeV": "{#}段 / {#} MeV",
    "{#} rungs in {#} MeV": "{#}段 / {#} MeV",
    "{#} rung in this {#}-MeV slice": "{#}段（この{#} MeV幅）",
    "{#} rungs in this {#}-MeV slice": "{#}段（この{#} MeV幅）",
    "about {#} rungs: too close to draw": "約{#}段：密すぎて描けない",
    "about {#}k rungs: too close to draw": "約{#}千段：密すぎて描けない",
    "about {#}M rungs: too close to draw": "約{#}百万段：密すぎて描けない",
    "about {#}B rungs: too close to draw": "約{#}十億段：密すぎて描けない",
    "about {#} rungs in this slice: too close to draw": "この範囲に約{#}段：密すぎて描けない",
    "about {#} thousand rungs in this slice: too close to draw": "この範囲に約{#}千段：密すぎて描けない",
    "about {#} million rungs in this slice: too close to draw": "この範囲に約{#}百万段：密すぎて描けない",
    "about {#} billion rungs in this slice: too close to draw": "この範囲に約{#}十億段：密すぎて描けない",
    "each one measured: energy, spin and parity": "1つずつ測定済み：エネルギー、スピン、パリティ",
    "the rungs are multiplying": "段が増えていく",
    "a continuum: the engine uses ρ itself": "連続領域：エンジンはρそのものを使う",
    "≈ energy to free a neutron": "≈ 中性子を解放するエネルギー",
    "energy ↑": "エネルギー ↑",
    // scene 3
    "gap: plank below the rungs": "ずれ：板が段より下",
    "gap: plank above the rungs": "ずれ：板が段より上",
    "counted levels": "数えた準位",
    "CT plank": "定温度の板",
    "constant-temperature plank": "定温度模型の板",
    "Fermi-gas hillside": "フェルミガスの斜面",
    "joint {#} MeV": "接続点 {#} MeV",
    "energy →": "エネルギー →",
    "+{#} more": "ほか{#}",
    "{#} counted": "数えた {#}",
    "{#} predicted": "予測 {#}",
    "{#}+ predicted": "予測 {#}+",
    "equal: the plank rests on the counted rungs": "一致：板が数えた段に乗る",
    "too few: the plank is too steep and sinks": "少なすぎ：板が急すぎて沈む",
    "too many: the plank is too shallow and floats": "多すぎ：板がゆるすぎて浮く",
    // scene 4
    "closed shell": "閉殻",
    "mid-shell": "殻の中間",
    "gap": "すき間",
    "no arrangement holds this heat": "この熱を保持できる配置なし",
    "≈ {#} arrangement": "≈ {#}通り",
    "≈ {#} arrangements": "≈ {#}通り",
    "≈ {#} thousand arrangements": "≈ {#}千通り",
    "≈ {#} million arrangements": "≈ {#}百万通り",
    "≈ {#} billion arrangements": "≈ {#}十億通り",
    "a ≈ {#}": "a ≈ {#}",
    "cold: nobody can move": "冷たい：誰も動けない",
    "temperature ≈ {#} MeV": "温度 ≈ {#} MeV",
    // scene 5
    "states at {#} MeV": "{#} MeVでの状態",
    "spin J →": "スピン J →",
    "+ parity": "＋パリティ",
    "− parity": "−パリティ",
    "rotation ×{#}": "回転 ×{#}",
    "added by rotation: ×{#} (a few drawn)": "回転による追加：×{#}（一部を描画）",
    "spread σ ≈ {#}: most states near J ≈ {#}": "広がり σ ≈ {#}：大半は J ≈ {#} 付近",
    "deformed: it can rotate": "変形：回転できる",
    "spherical": "球形",
    // scene 6
    "≈ {#} thousand": "≈ {#}千",
    "≈ {#} million": "≈ {#}百万",
    "≈ {#} billion": "≈ {#}十億",
    "≈ {#}k": "≈ {#}千",
    "≈ {#}M": "≈ {#}百万",
    "≈ {#}B": "≈ {#}十億",
    "{#} bins, each {#} MeV wide": "ビン{#}個、各{#} MeV幅",
    "counted": "数えた準位",
    "states in each bin": "各ビンの状態数",
  };
  Object.assign(WT.L.labels, L);
})();
