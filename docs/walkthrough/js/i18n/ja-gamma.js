/* Japanese: gamma (第7章、光子放出) */
WT.L.ch.gamma = {
  num: "第7章", title: "光を放つ", short: "光子",
  lead: "粒子が出ていかないとき、原子核は光子、つまり高エネルギーの光の粒子であるガンマ線を放出して冷えていきます。この出口はどのエネルギーでも開いています。",
  html: `
<div class="step">
  <p>8 MeV（100万電子ボルト）の熱い状態が光子（γ）を放出します。はしごの横の山は、光子がどこへ着地したかを集めたものです。2 MeVより下では状態は名前のついた数段だけですが、その上ではエネルギーとともに急激に密になる群れ（灰色の点）です。各光子は落下分のエネルギー<i>E<sub>γ</sub></i>を運び去り、<i>E<sub>γ</sub></i>³に比例した明るさで描かれます。</p>
  <div class="formula">T<sub>γ</sub>(E<sub>γ</sub>) = 2π · E<sub>γ</sub><sup>2l+1</sup> · f(E<sub>γ</sub>)</div>
  <p><i>T<sub>γ</sub></i>は光子の透過係数（第6章の扉）で、双極子光子では<i>l</i> = 1、<i>f</i>は<b>光子強度関数</b>、つまりそのエネルギーで原子核がどれだけ放射しやすいかを表します。ある落下の確率は、<i>T<sub>γ</sub></i>に着地先の状態の群れを掛けたものです。小さな落下は多くの状態を見つけますが暗く、大きな落下は明るいものの着地先の状態は少ないのです。</p>
  <div class="ctl"><label for="gm-e0">出発エネルギー</label><input id="gm-e0" type="range" data-bind="E0" min="3" max="9" step="0.5" value="8"><output data-show="E0" data-fmt="1"></output></div>
  <div class="btns"><button class="btn" data-act="emit">100個放出</button></div>
  <p>山は出発点より数MeV下でピークになります。ほとんどの光子は2〜4 MeVを運びます。出発エネルギーを動かすと、ピークもついてきます。</p>
</div>
<div class="step">
  <h3>原子核全体が鳴る</h3>
  <p>右の大きなピークは<b>巨大双極子共鳴</b>です。すべての陽子（斜線、左）がすべての中性子（塗りつぶし）に対して揺れ動きます。その振動数が、原子核が最も吸収・放出しやすい光子エネルギーを決めます。曲線は光子強度関数<i>f</i>で、対数目盛（1段上がるごとに10倍）です。</p>
  <div class="ctl"><label for="gm-a">質量数 A</label><input id="gm-a" type="range" data-bind="A" min="40" max="240" step="1" value="112"><output data-show="A" data-fmt="0"></output></div>
  <p>質量数A（陽子数と中性子数の和）を動かしてみましょう。重い原子核ほどゆっくり揺れ、12〜14 MeV付近で鳴ります。軽い原子核では20 MeV付近です。崩壊する原子核が放出する光子はせいぜい数MeVなので、最も重要なのは影をつけた低エネルギー側の裾です。</p>
</div>
<div class="step">
  <h3>シザーズとアップベンド</h3>
  <p>変形した原子核は磁気的にも放射します。陽子（斜線）と中性子（塗りつぶし）の2つのラグビーボールが、はさみの刃のように互いに揺れ合うのです。この<b>シザーズモード</b>は約3 MeVにあります。約8 MeVの<b>スピン反転</b>は、個々の核子がスピンを反転させるもの（小さな矢印）で、どんな形でも起こります。</p>
  <div class="ctl"><label for="gm-b">変形 β₂</label><input id="gm-b" type="range" data-bind="beta" min="0" max="0.35" step="0.01" value="0.25"><output data-show="beta" data-fmt="2"></output></div>
  <p>変形β₂（0が球）を動かしてみましょう。伸びているほどシザーズの光子が多く飛び、球では出ません。最も低いエネルギーでは強度が再び上がります。これが<b>アップベンド</b>で、柔らかい光子が少しずつ出るもので、エンジンは原子核が変形するにつれてこれを弱めます。既定ではオフの任意スイッチで、オスロの測定に合うより強いシザーズの系統式を使うこともできます（ウランでは4〜5倍強くなります）。</p>
</div>
<div class="step">
  <h3>はしごを下る</h3>
  <p>カスケードとは、上のビン（列挙できないほど密な状態、第5章）から名前のついた準位まで、次々に放出される光子の列です。準位は読みやすいように引き伸ばしてあります（塗りつぶしの段はパリティ＋、白抜きは−）。そこでエンジンは推定をやめ、表になった<b>分岐比</b>、すなわち各準位がそれぞれの下の準位へ崩壊する測定された確率に従います。</p>
  <div class="btns"><button class="btn" data-act="drop">カスケードを落とす</button></div>
  <p>ボタンを何度か押してみましょう。上の部分は毎回変わりますが、終わりはいくつかの測定された経路のどれかをたどります。</p>
</div>
<div class="step">
  <h3>とどまる棚</h3>
  <p>0.40 MeVの11/2−準位は<b>核異性体</b>です。スピンが下の準位から大きく離れているため、光子ではほとんどつなげず、数秒から数年生き延びます。そこに着地したものはとどまります。エンジンは1秒より長く生きる準位をすべて終点として扱います。各玉が1つのカスケードで、核異性体の山か基底状態の山のどちらかで終わります。</p>
  <div class="ctl"><label for="gm-j">入射スピン</label><input id="gm-j" type="range" data-bind="J0" min="0" max="8" step="1" value="2" data-instant><output id="gm-jout">5/2</output></div>
  <p>カスケードの出発点である入射スピンを動かすと、山が積み直されます。核異性体で終わる割合、すなわち<b>異性体比</b>はこれに依存します。高スピンから出発すると高スピンの核異性体に流れ込み、低スピンから出発するとそれを素通りして基底状態へ滑り落ちます。</p>
</div>
<div class="step">
  <h3>捕獲</h3>
  <p>遅い中性子を吸収したばかりの原子核には、2つの出口の扉があります（第6章）。光子（上）と、中性子が再び出ていく扉（右）です。各扉の隙間がその<b>幅</b>で、単位はeVです。原子核がその扉を通じてどれだけ速く崩壊するかを表します。光子幅はほとんど変わりませんが、中性子幅は中性子の速さとともに大きくなります。</p>
  <div class="ctl"><label for="gm-e">中性子エネルギー</label><input id="gm-e" type="range" data-bind="lgE" min="-2" max="3.3" step="0.02" value="0"><output id="gm-eout">1.0 keV</output></div>
  <p>中性子エネルギーを10 eVから2 MeVまで動かしてみましょう。<b>捕獲</b>、(n,γ)とは、中性子がとどまり光子が出ていくことです。10 eVではほとんどの場合に捕獲が勝ち、数keVを超えるとわずかな割合になります。しきい値での光子幅は数百の原子核で測定されており、光子強度関数の検証になります。エンジンは既定では自前の値を使いますが、任意のスイッチで、測定のある各原子核の光子強度関数を両者が一致するまでスケールできます。</p>
  <div class="aside">コードでは：<code>gamma/parameters.py</code>（表になったE1強度、巨大共鳴・スピン反転・シザーズ・アップベンドの系統式）、<code>gamma/strength.py</code>（全多重極の<i>f</i>(E<sub>γ</sub>)）、<code>gamma/transmission.py</code>（T<sub>γ</sub>と平均放射幅）、<code>structure/levels.py</code>（分岐比、核異性体）、<code>emission/multiple.py</code>（カスケード）。任意、既定ではオフ：<code>gamma/scissors.py</code>（より強いシザーズ）、<code>gamma/ggnorm.py</code>（測定された⟨Γγ⟩に合わせる、鉛まで）、<code>gamma/actphys.py</code>（アクチノイド向けに両方）。</div>
</div>`,
};
Object.assign(WT.L.labels, {
  // scene 1: emit
  "energy ↑": "エネルギー ↑",
  "named levels": "名前のある準位",
  "a crowd of states": "状態の群れ",
  "{#} MeV": "{#} MeV",
  "hot state, {#} MeV": "熱い状態、{#} MeV",
  "most photons ≈ {#} MeV": "最頻 ≈ {#} MeV",
  "small drops: faint (E³ tiny)": "小さな落下：暗い（E³が小）",
  "big drops: bright, but few states to land on": "大きな落下：明るいが着地先は少ない",
  // scene 2: gdr
  "protons": "陽子",
  "neutrons": "中性子",
  "A = {#}: rings at {#} MeV": "A = {#}：{#} MeVで振動",
  "peak {#} MeV": "ピーク {#} MeV",
  "giant resonance at {#} MeV": "巨大共鳴 {#} MeV",
  "width ≈ {#} MeV": "幅 ≈ {#} MeV",
  "decays use this": "崩壊で使う部分",
  "shaded: the tail decays use": "影：崩壊で使う裾",
  "photon energy (MeV) →": "光子エネルギー (MeV) →",
  "photon strength f (log scale) ↑": "光子強度関数 f（対数目盛）↑",
  // scene 3: m1
  "a sphere has no blades: no scissors": "球には刃がない：シザーズなし",
  "scissors ≈ {#} MeV: strength {#} % of the most stretched": "シザーズ ≈ {#} MeV：強度は最大変形の{#}%",
  "spin-flip ≈ {#} MeV: steady, any shape (thick photons)": "スピン反転 ≈ {#} MeV：一定、形を問わない（太い光子）",
  "upbend below {#} MeV: soft photons, plenty at this shape": "アップベンド {#} MeV未満：柔らかい光子、この形では多い",
  "upbend below {#} MeV: soft photons, fewer at this shape": "アップベンド {#} MeV未満：柔らかい光子、この形ではやや少ない",
  "upbend below {#} MeV: soft photons, few at this shape": "アップベンド {#} MeV未満：柔らかい光子、この形では少ない",
  // scene 4: cascade
  "ground state": "基底状態",
  "isomer": "核異性体",
  "isomer: long-lived": "核異性体：長寿命",
  "bins: too dense to list": "ビン：密すぎて列挙不能",
  "one photon at a time": "光子を1個ずつ",
  "measured branching ratios": "測定された分岐比",
  "▬ parity +   ▭ parity −": "▬ パリティ＋   ▭ パリティ−",
  // scene 5: isomer
  "entrance: J = {#}/{#}": "入射：J = {#}/{#}",
  "isomer: {#} ({#} %)": "核異性体：{#}（{#}%）",
  "ground state: {#} ({#} %)": "基底状態：{#}（{#}%）",
  "many cascades: ≈ {#} % isomer": "多数のカスケード：核異性体 ≈ {#}%",
  "over many cascades from J = {#}/{#}: ≈ {#} % end on the isomer": "J = {#}/{#} からの多数のカスケード：≈ {#}%が核異性体で終わる",
  // scene 6: capture
  "photon door: {#} eV, barely changes": "光子の扉：{#} eV、ほぼ不変",
  "captured (n,γ): {#} ({#} %)": "捕獲 (n,γ)：{#}（{#}%）",
  "neutron: {#} eV": "中性子：{#} eV",
  "neutron door: {#} eV, wider when faster": "中性子の扉：{#} eV、速いほど広い",
  "back out: {#} ({#} %)": "再放出：{#}（{#}%）",
  "more doors open (target left excited)": "扉が増える（標的が励起状態に）",
  "{#} eV neutrons →": "{#} eV中性子 →",
  "{#} keV neutrons →": "{#} keV中性子 →",
  "{#} MeV neutrons →": "{#} MeV中性子 →",
  "slow neutrons: the photon door wins": "遅い中性子：光子の扉が勝つ",
  "the neutron door wins; capture takes about {#} %": "中性子の扉が勝つ。捕獲は約{#}%",
  "fast: capture is a rare event": "速い：捕獲はまれ",
});
