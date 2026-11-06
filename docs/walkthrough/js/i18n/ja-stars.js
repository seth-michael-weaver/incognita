/* Japanese: stars (元素はどこから来たのか) */
WT.L.ch.stars = {
  num: "レッスン 1", title: "元素はどこから来たのか", short: "星",
  html: `
<div class="step">
  <h3>核融合は鉄で止まる</h3>
  <p>星は軽い原子核を鉄まで融合します。それより重いものはほぼすべて、中性子を加えることでつくられます。</p>
</div>
<div class="step">
  <h3>ゆっくりした道</h3>
  <p>巨星では中性子がまれにしか来ないので、不安定な原子核はまずベータ崩壊します。道筋は安定な原子核に沿ってジグザグに進みます。</p>
  <div class="ctl"><label for="st-k">中性子捕獲の回数</label><input id="st-k" type="range" data-bind="k" min="0" max="213" step="1" value="112"></div>
</div>
<div class="step">
  <h3>速い道</h3>
  <p>中性子星の合体では、原子核が崩壊するより速く中性子がなだれ込みます。その後、中性子過剰な原子核は安定へと崩壊して戻ります。</p>
  <div class="ctl"><label for="st-rt">崩壊して戻る</label><input id="st-rt" type="range" data-bind="rt" min="0" max="1" step="0.01" value="0"></div>
</div>
<div class="step">
  <h3>魔法数がピークをつくる</h3>
  <p>中性子が50、82、126個の原子核はほとんど捕獲しないので、物質がそこにたまります。sピークはストロンチウム、バリウム、鉛に、rピークは少し軽い側に。</p>
  <div class="btns"><button class="btn ghost" data-act="stS" aria-pressed="true">s過程のピーク</button> <button class="btn ghost" data-act="stR" aria-pressed="true">r過程のピーク</button></div>
</div>
<div class="step">
  <h3>捕獲しやすいものは少ない</h3>
  <p>s過程だけでつくられる同位体では、存在度Nₛと捕獲断面積σの積が魔法数の間でほぼ一定です。ここでのσはINCOGNITAが30 keVで計算した値です。</p>
  <div class="btns"><button class="btn ghost" data-act="stvs" aria-pressed="false">σ</button> <button class="btn ghost" data-act="stvn" aria-pressed="false">Nₛ</button> <button class="btn ghost" data-act="stvsn" aria-pressed="true">σ × Nₛ</button></div>
</div>
<div class="step">
  <h3>測定値との照合</h3>
  <p>INCOGNITAの30 keVの値を測定値で割ったもの、94の安定核種について（<a href="scoreboard.html">成績表</a>）。</p>
</div>`,
};
Object.assign(WT.L.labels, {
  "A ≈ {#}": "A ≈ {#}",
  "Ba": "Ba",
  "Ba{#}": "Ba{#}",
  "Big Bang": "ビッグバン",
  "Fe": "Fe",
  "H": "H",
  "He": "He",
  "INCOGNITA ÷ measured, {#} keV": "INCOGNITA ÷ 測定値、{#} keV",
  "INCOGNITA's {#} keV capture rate (MACS) ÷ measured": "INCOGNITA の {#} keV 捕獲率（MACS）÷ 測定値",
  "INCOGNITA: capture at {#} keV (MACS)": "INCOGNITA：{#} keV での捕獲（MACS）",
  "Lodders et al. {#}": "Lodders et al. {#}",
  "Lu{#}": "Lu{#}",
  "N = {#}": "N = {#}",
  "O": "O",
  "Pb": "Pb",
  "Pb{#}": "Pb{#}",
  "Sm{#}": "Sm{#}",
  "Sn": "Sn",
  "Sr": "Sr",
  "Sr{#}": "Sr{#}",
  "abundances: Lodders, Palme & Gail {#}": "存在度：Lodders, Palme & Gail {#}",
  "abundances: Lodders, Palme & Gail {#} · point at the curve": "存在度：Lodders, Palme & Gail {#} · 曲線を指してください",
  "atoms per million silicon atoms (Solar System)": "ケイ素原子100万個あたりの原子数（太陽系）",
  "atoms per {#}⁶ silicon": "ケイ素 {#}⁶ 個あたりの原子数",
  "beta decay (n → p)": "ベータ崩壊（n → p）",
  "flat between magic numbers, steps down at each": "魔法数の間は平ら、各魔法数で段差",
  "fusion": "核融合",
  "fusion in stars": "星の中の核融合",
  "made by neutron capture": "中性子捕獲でつくられる",
  "magic N: captures poorly, matter piles up": "魔法数 N：捕獲しにくく、物質がたまる",
  "magic neutron number: it captures poorly, so matter piles up here": "中性子の魔法数：捕獲しにくいので、物質がここにたまる",
  "mass number A": "質量数 A",
  "mass number A (protons + neutrons)": "質量数 A（陽子 + 中性子）",
  "mb": "mb",
  "nearly flat between magic numbers, a step down at each": "魔法数の間はほぼ平ら、各魔法数で一段下がる",
  "neutron capture": "中性子捕獲",
  "neutrons N →": "中性子数 N →",
  "peaks: sources Lodders et al. {#}": "ピーク：出典 Lodders et al. {#}",
  "plus a weaker s-process (massive stars)": "加えて弱い s 過程（大質量星）",
  "r {#}": "r {#}",
  "r-path: illustration": "r 過程の道筋：イメージ図",
  "r-peak Pt": "r ピーク Pt",
  "r-peak Se, Kr": "r ピーク Se、Kr",
  "r-peak Te, Xe": "r ピーク Te、Xe",
  "r-process: a flood of neutrons makes very neutron-rich nuclei": "r 過程：中性子の洪水が非常に中性子過剰な原子核をつくる",
  "r-process: very neutron-rich nuclei": "r 過程：非常に中性子過剰な原子核",
  "ringed: s-only isotopes · measured: compiled values (KADoNiS) · a development comparison, not a blind test": "丸囲み：s 過程のみの同位体 · 測定値：評価集の値（KADoNiS）· 開発中の比較で、ブラインドテストではない",
  "ringed: s-only · measured: KADoNiS": "丸囲み：s のみ · 測定値：KADoNiS",
  "s Ba": "s Ba",
  "s Pb": "s Pb",
  "s Sr": "s Sr",
  "s-only isotopes · bars: INCOGNITA {#} %": "s 過程のみの同位体 · バー：INCOGNITA {#} %",
  "s-only isotopes · σ: INCOGNITA (bars: its {#} % range; open circle: scaled to a measurement) · Nₛ: Lodders et al. {#}": "s 過程のみの同位体 · σ：INCOGNITA（バー：その {#} % 範囲、白丸：測定値に合わせて規格化）· Nₛ：Lodders et al. {#}",
  "s-peak Ba": "s ピーク Ba",
  "s-peak Pb": "s ピーク Pb",
  "s-peak Sr": "s ピーク Sr",
  "seen in {#}: merger GW{#}": "{#} 年に観測：合体 GW{#}",
  "seen in {#}: the neutron-star merger GW{#} and its kilonova": "{#} 年に観測：中性子星合体 GW{#} とそのキロノバ",
  "wait": "待機",
  "waiting point": "待機点",
  "weak s-process too": "弱い s 過程も",
  "σ × Nₛ (mb × atoms per million Si)": "σ × Nₛ（mb × Si 100万個あたりの原子数）",
  "σ × Nₛ (mb × atoms per {#}⁶ Si)": "σ × Nₛ（mb × Si {#}⁶ 個あたりの原子数）",
  "↑ protons Z": "↑ 陽子数 Z",
  "A = {a}: mostly {b}, {c} atoms per million silicon": "A = {a}：主に {b}、ケイ素100万個あたり {c} 個",
  "decayed back: r-made stable isotopes": "崩壊して戻った：r 過程でできた安定同位体",
  "decayed back: each lands on the most neutron-rich stable isobar": "崩壊して戻った：それぞれ最も中性子過剰な安定同重体に落ち着く",
  "beta decays, A fixed": "ベータ崩壊、A は一定",
  "beta decays carry them back, mass number A fixed": "ベータ崩壊で戻っていく、質量数 A は一定",
  "{a} · N = {b} · σ = {c} mb": "{a} · N = {b} · σ = {c} mb",
  "{a} · N = {b} · INCOGNITA: σ = {c} mb at {#} keV": "{a} · N = {b} · INCOGNITA：σ = {c} mb（{#} keV）",
  "{a} · unstable: beta decay": "{a} · 不安定：ベータ崩壊",
  "{a} · unstable: it beta-decays before the next neutron": "{a} · 不安定：次の中性子が来る前にベータ崩壊する",
  "end: the lead–bismuth cycle": "終点：鉛–ビスマスのサイクル",
  "end of the road: Bi{#} → Po{#} → alpha decay back to Pb{#}": "行き止まり：Bi{#} → Po{#} → アルファ崩壊で Pb{#} に戻る",
  "drag along the path": "道筋に沿ってドラッグ",
  "drag along the path, or use the slider": "道筋に沿ってドラッグするか、スライダーを使う",
  "{a}: INCOGNITA σ = {b} mb": "{a}：INCOGNITA σ = {b} mb",
  "{a}: σ = {b} mb × Nₛ = {c} → σNₛ = {d}": "{a}：σ = {b} mb × Nₛ = {c} → σNₛ = {d}",
  " (σ scaled to a measured value)": "（σ は測定値に合わせて規格化）",
  "σ alone: scattered": "σ だけ：ばらばら",
  "σ alone jumps around from isotope to isotope": "σ だけでは同位体ごとに大きく跳ねる",
  "Nₛ alone: scattered": "Nₛ だけ：ばらばら",
  "Nₛ alone jumps around the other way": "Nₛ だけでは逆向きに跳ねる",
  "{a}: INCOGNITA's engine {b} (the library then scales to it)": "{a}：INCOGNITA のエンジン {b}（ライブラリはその後測定値に合わせる）",
  "{a}: INCOGNITA σ = {b} mb, {c}": "{a}：INCOGNITA σ = {b} mb、{c}",
  "{a} nuclides · typical difference {b} %": "{a} 核種 · 典型的な差 {b} %",
  "{a} stable nuclides · typical difference {b} % (median), rms {c} %": "安定核種 {a} · 典型的な差 {b} %（中央値）、rms {c} %",
  "{a} % above measured": "測定値より {a} % 高い",
  "{a} % below measured": "測定値より {a} % 低い",
});
