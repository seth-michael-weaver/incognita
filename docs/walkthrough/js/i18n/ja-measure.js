/* Japanese: measure (第12章、観測量) */
WT.L.ch.measure = {
  num: "第12章", title: "出てくるもの", short: "観測量",
  lead: "実験も原子炉も恒星も、目にするのはほんの一握りの数値だけです。この章では、エンジンが原子核の内部で起きることをどのようにそれらの数値に変えるかを示します。",
  html: `
<div class="step">
  <p>各原子核のまわりの淡い円盤が、その<b>断面積</b>です。反応が起きるために中性子が当たらなければならない面積であり、原子核の実際の大きさではありません。ビームは左から原子核の薄い箔を通り抜けます。反応する割合は、その面積に、ビームが出会う原子核の数を掛けたものです。単位はバーン（10⁻²⁴ cm²、ウラン原子核の断面とほぼ同じ）です。</p>
  <div class="ctl"><label for="mea-e">中性子エネルギー（MeV）</label><input id="mea-e" type="range" data-bind="E" min="0.1" max="20" step="0.1" value="2"><output data-show="E" data-fmt="1"></output></div>
  <p>エネルギーを下げると円盤が膨らみます。遅い中性子は幅の広い波なので、より遠くから反応するのです。高エネルギーでは、円盤は原子核そのものの大きさへと縮んでいきます。</p>
</div>
<div class="step">
  <h3>エネルギーとともに新しい出口が開く</h3>
  <p>各扉が1つの出口、すなわち<b>チャネル</b>です。中性子が跳ね返って出ていく（弾性）、標的を励起状態に残して出ていく（n′）、さらに中性子を叩き出す（2n、3n）、捕獲されて光子だけが出ていく（γ）、あるいは代わりに陽子やα粒子が出ていく、のいずれかです。南京錠のかかった扉には<b>しきい値</b>があり、反応に必要なエネルギーが中性子の持ち込む分を上回っています。</p>
  <div class="ctl"><label for="mea-e2">中性子エネルギー（MeV）</label><input id="mea-e2" type="range" data-bind="E" min="0.1" max="20" step="0.1" value="2"><output data-show="E" data-fmt="1"></output></div>
  <p>エネルギーをしきい値より上に動かすと、その扉がぱっと開きます。バケツは各チャネルの割合まで満たされ、新しい扉はそれぞれ他の扉から割合を奪います。しきい値は原子核の質量から、割合は第6章の競争から決まります。</p>
</div>
<div class="step">
  <h3>検出器に見えるもの</h3>
  <p>2つの山は、リング状の検出器の前方半分と後方半分に届いた中性子を、エネルギーごとに分けたものです。ビームはパルス状なので、各中性子の飛行時間からエネルギーがわかります。速いものが先に届きます。</p>
  <div class="ctl"><label for="mea-ein">入射エネルギー（MeV）</label><input id="mea-ein" type="range" data-bind="Ein" min="5" max="60" step="0.5" value="30"><output data-show="Ein" data-fmt="0"></output></div>
  <p>どちらの山にも、遅い<b>蒸発</b>中性子のこぶがあります。エネルギーが分け合われた後に複合核から沸き出すもので、どの方向にも同じように出ていきます。長く速い裾があるのは前方の山だけです。これが<b>前平衡</b>中性子で、最初の衝突から出ていくため、まだおおむねビームの向きに動いています。入射エネルギーを上げると、裾が伸びます。</p>
</div>
<div class="step">
  <h3>どちらへ向かうか</h3>
  <p>花びらは、各方向にどれだけの中性子が出ていくかを示します。ビームは左から来ます。蒸発した中性子はビームのことを忘れていて、どの方向にも同じように出ていきます。速い前平衡の中性子は前方に傾きます。どれだけ傾くかはカルバッハの規則が決め、出ていくエネルギーとともに大きくなる1つの傾き<i>a</i>で表されます。エンジンはこれらの角度分布も任意の出力として書き出せます。</p>
  <div class="ctl"><label for="mea-eo">放出エネルギー（MeV）</label><input id="mea-eo" type="range" data-bind="Eout" min="1" max="45" step="0.5" value="25"><output data-show="Eout" data-fmt="1"></output></div>
  <p>放出エネルギーを下げると花びらは丸くなります。遅い中性子はほとんどが蒸発によるものだからです。</p>
  <div class="formula">dσ/dΩ ∝ e<sup>a cos θ</sup></div>
</div>
<div class="step">
  <h3>恒星の中で</h3>
  <p>下の山は、恒星の熱いガスの中で捕獲された中性子のエネルギーを集めたものです。中性子の速さは温度<i>kT</i>で決まるマクスウェル分布に従います（30 keVは約3億5000万度）。軌跡が長いほど速い中性子で、原子核のそばを通るたびに捕獲の閃光で終わることがあります。</p>
  <div class="ctl"><label for="mea-kt">温度 kT（keV）</label><input id="mea-kt" type="range" data-bind="kT" min="5" max="100" step="1" value="30"><output data-show="kT" data-fmt="0"></output></div>
  <p>遅い中性子は捕まりやすいもののめったに通りかからず、速い中性子は数が少ないので、捕獲の大部分は幅が<i>kT</i>の数倍の窓から来ます。ガス全体での率が<b>マクスウェル平均断面積</b>（MACS）で、単位はミリバーン（mb）です。ガスを熱すると窓は高いエネルギー側へ移り、そこでは標的は小さくなります。MACSはエンジンの捕獲曲線を畳み込んで求めます。</p>
</div>
<div class="step">
  <h3>標的も熱い</h3>
  <p>玉は、この温度で標的原子核のうちどれだけの割合が最も低いいくつかの準位にいるかを示しています。恒星の中では一部の標的がすでに励起されていて、各励起準位は同じ複合核への別の入口になります。スピン<i>J</i>の準位は2<i>J</i>+1通りの向きをもつので、より多くを収容します。</p>
  <div class="ctl"><label for="mea-kt2">温度 kT（keV）</label><input id="mea-kt2" type="range" data-bind="kT" min="5" max="100" step="1" value="30"><output data-show="kT" data-fmt="0"></output></div>
  <p>温度を上げて、原子核が上へ移っていくのを見てみましょう。恒星内での率は、占有された各準位からの捕獲を計算し、その結果をこれらの割合で足し合わせます。重みの和が分配関数<i>G</i>で、基底状態からの率との比が<b>恒星内増大因子</b>です。エンジンは任意機能としてこれを計算できますが、既定ではオフで、通常はすべての標的が基底状態から出発します。</p>
</div>
<div class="step">
  <h3>どれほど確かなのか</h3>
  <p>淡い円盤の1つ1つは、入力をランダムに少しずらしてエンジンを1回実行した結果です。光学ポテンシャルの井戸の深さ、準位密度、光子強度関数は、どれも数パーセントの精度でしかわかっていません。多数の実行のばらつきが、正直な不確かさになります。これが<b>トータル・モンテカルロ</b>です。</p>
  <div class="btns"><button class="btn" data-act="tmc1">変種を1回実行</button><button class="btn ghost" data-act="tmc">10回実行</button><button class="btn ghost" data-act="clear">消去</button></div>
  <p>縁がくっきりしていれば入力が答えを決めており、ぼやけていればそうではありません。新しい測定が最も役立つのはそこです。</p>
  <div class="aside">コードでは：<code>emission/channels.py</code>（排他的チャネルと残留核）、<code>specout.py</code>と<code>specang.py</code>（放出スペクトル、角度分布、二重微分断面積。要求されたときのみ出力）、<code>astro/stellar.py</code>（熱的に占有された標的準位からの捕獲、任意）、<code>tmc.py</code>（トータル・モンテカルロのサンプラー）。基底状態のMACSは<code>validation/differential/core.py</code>で捕獲曲線を畳み込んで求めます。</div>
</div>`,
};
Object.assign(WT.L.labels, {
  // area
  "each disc: σ ≈ {#} b": "各円盤：σ ≈ {#} b",
  "each disc: cross section σ ≈ {#} b, the area a neutron must hit": "各円盤：断面積 σ ≈ {#} b、中性子が当てるべき面積",
  "beam →": "ビーム →",
  "nucleus's own face ≈ {#} b · {#} % reacts": "原子核自体の断面 ≈ {#} b · {#}%が反応",
  "the nucleus's own face ≈ {#} b · {#} % of the beam reacts in this foil": "原子核自体の断面 ≈ {#} b · この箔でビームの{#}%が反応",
  "slow: the neutron's wave reaches well past the surface": "遅い：中性子の波は表面のはるか外まで届く",
  "the target still looks bigger than the nucleus": "標的はまだ原子核より大きく見える",
  "fast: close to the nucleus's own size": "速い：原子核自体の大きさに近い",
  // doors
  "elastic": "弾性", "n′ inelastic": "n′ 非弾性", "{#}n": "{#}n", "γ capture": "γ捕獲", "p": "p", "α": "α", "n′": "n′",
  "{#}n · {#} MeV": "{#}n · {#} MeV", "p · {#} MeV": "p · {#} MeV", "α · {#} MeV": "α · {#} MeV", "n′ inelastic · {#} MeV": "n′ 非弾性 · {#} MeV",
  "opens at {#} MeV": "{#} MeVで開く",
  "{#} MeV": "{#} MeV",
  // detect
  "forward half": "前方半分", "backward half": "後方半分",
  "pulsed beam": "パルスビーム", "pulsed beam →": "パルスビーム →",
  "backward": "後方", "backward detectors": "後方検出器",
  "forward": "前方", "forward detectors": "前方検出器",
  "outgoing neutron energy from the flight time (MeV) →": "飛行時間から求めた放出中性子エネルギー (MeV) →",
  "fast tail": "速い裾", "fast tail: pre-equilibrium": "速い裾：前平衡",
  "evaporated hump": "蒸発のこぶ", "hump: evaporated, every way alike": "こぶ：蒸発、全方向に同じ",
  "{#} % leave before the energy is shared": "{#}%はエネルギー分配前に放出",
  // angle
  "beam": "ビーム",
  "forward-to-backward ratio ≈ {#}  ·  slope a ≈ {#}": "前方／後方比 ≈ {#}  ·  傾き a ≈ {#}",
  "mostly evaporated: every direction alike": "大半が蒸発：全方向に同じ",
  "a mix: the fast share leans forward": "混合：速い分が前方に傾く",
  "mostly pre-equilibrium: strongly forward": "大半が前平衡：強く前方へ",
  "forward →": "前方 →",
  // star
  "{#} keV": "{#} keV",
  "kT = {#} keV": "kT = {#} keV",
  "energies of captured neutrons": "捕獲された中性子のエネルギー",
  "each capture drops here, by the neutron's energy: the window that counts": "各捕獲が中性子エネルギーごとにここへ：効いてくる窓",
  "MACS ≈ {#} mb at kT = {#} keV · captures watched: {#}": "MACS ≈ {#} mb（kT = {#} keV）· 観測した捕獲：{#}",
  // hot target
  "{#}⁺  ground state": "{#}⁺  基底状態", "{#}⁺  {#} keV": "{#}⁺  {#} keV",
  "target levels, with the share of nuclei sitting on each": "標的の準位と、各準位にいる原子核の割合",
  "{#} % start from the ground state · partition function G ≈ {#}": "{#}%が基底状態から出発 · 分配関数 G ≈ {#}",
  // TMC
  "optical well": "光学ポテンシャルの井戸", "optical well depth": "光学ポテンシャルの井戸の深さ",
  "level density": "準位密度", "photon strength": "光子強度関数",
  "σ ≈ {#} b ": "σ ≈ {#} b ", "σ ≈ {#} mb ": "σ ≈ {#} mb ",
  "σ ≈ {#} b ±{#} %": "σ ≈ {#} b ±{#}%", "σ ≈ {#} mb ±{#} %": "σ ≈ {#} mb ±{#}%",
  "dashed: best inputs · each disc drawn at its own scale": "点線：最良の入力 · 各円盤は独自の縮尺",
  "dashed ring: the best-value inputs · each energy drawn at its own scale (disc area ∝ σ)": "点線の輪：最良値の入力 · 各エネルギーは独自の縮尺（円盤の面積 ∝ σ）",
  "{#} runs of the engine, each with its inputs nudged at random": "エンジンを{#}回実行、各回で入力をランダムにずらす",
});
