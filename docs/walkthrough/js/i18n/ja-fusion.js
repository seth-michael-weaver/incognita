/* Japanese: fusion (第29章、核融合とクーロン障壁) */
WT.L.ch.fusion = {
  num: "第29章", title: "核融合エネルギーとクーロン障壁", short: "核融合",
  lead: "核融合は核分裂と逆向きに進みます。2つの軽い原子核が結合し、できた組は部品の合計より軽くなります。",
  html: `
<div class="step">
  <h3>結合エネルギー曲線から見た核融合エネルギー</h3>
  <p>2つの軽い原子核を結合させます。新しい原子核が結合エネルギー曲線の高い位置にあれば、エネルギーが放出されます。鉄のピークを越えると、結合させるにはエネルギーが必要になります。</p>
  <div class="ctl"><label for="fu-a">それぞれの軽い原子核の A</label><input id="fu-a" type="range" data-bind="fuse" data-instant min="2" max="60" step="1" value="2"><output data-show="fuse" data-fmt="0"></output></div>
  <p class="ctl-result" id="fu-fuse-out" aria-live="polite"></p>
</div>
<div class="step">
  <h3>クーロン障壁とトンネル効果</h3>
  <p>重陽子を引いて放してみましょう。どちらの原子核も電荷をもつので、ほとんどの球は丘にはね返されます。ごく一部がトンネルで抜けます。</p>
  <div class="ctl"><label for="fu-e">押す強さ（keV）</label><input id="fu-e" type="range" data-bind="lE" min="0.5" max="2.6" step="0.01" value="1.7"><output data-show="E" data-fmt="0"></output></div>
  <div class="btns"><button class="btn" data-act="fire">発射</button></div>
</div>
<div class="step">
  <h3>反応生成物とQ値</h3>
  <p>結合した組は2つの部品より軽くなります。消えた質量は、速い粒子となって飛び去ります。</p>
  <div class="btns fu-fuels"><button class="btn ghost" data-act="DT" aria-pressed="true">D–T</button> <button class="btn ghost" data-act="DD" aria-pressed="false">D–D</button> <button class="btn ghost" data-act="DHe" aria-pressed="false">D–³He</button> <button class="btn ghost" data-act="pB" aria-pressed="false">p–¹¹B</button></div>
</div>
<div class="step">
  <h3>熱核反応率</h3>
  <p>熱いガスの中では、いちばん速い原子核が障壁を抜けます。光が1回またたくごとに、核融合が1回起きています。</p>
  <div class="ctl"><label for="fu-t">温度（keV）</label><input id="fu-t" type="range" data-bind="lT" min="0" max="2" step="0.01" value="1"><output data-show="T" data-fmt="1"></output></div>
</div>`,
};
Object.assign(WT.L.labels, {
  "B": "B",
  "Copper{#}": "銅{#}",
  "Coulomb hill": "クーロンの丘",
  "D–D": "D–D",
  "D–T": "D–T",
  "D–³He": "D–³He",
  "E = kT": "E = kT",
  "Gamow peak E₀": "ガモフピーク E₀",
  "K {#} · field lines lost to the wall: {#}": "K {#} · 壁に失われた磁力線：{#}",
  "Q = {#}": "Q = {#}",
  "Q = ∞: no heating needed": "Q = ∞：加熱不要",
  "Silicon{#} (SiC)": "ケイ素{#}（SiC）",
  "Steel (iron{#})": "鋼（鉄{#}）",
  "Sun's core": "太陽中心",
  "TBR {#}": "TBR {#}",
  "Tungsten{#}": "タングステン{#}",
  "Vanadium{#}": "バナジウム{#}",
  "after {#} years at {#} MW/m² · {#} MeV neutrons only · σ from INCOGNITA library v{#}": "{#}年後、{#} MW/m² · {#} MeV中性子のみ · σはINCOGNITAライブラリv{#}",
  "almost never": "ほぼ起きない",
  "alpha {#} MeV": "α {#} MeV",
  "axis, q = {#}": "磁気軸、q = {#}",
  "binding per nucleon (MeV)": "核子あたりの結合（MeV）",
  "bubble-chamber view, magnetic field into the page: charged products curl, the neutron leaves no track": "泡箱の眺め、磁場は紙面の奥向き：荷電生成物は曲がり、中性子は跡を残さない",
  "burning on its own": "自力で燃焼中",
  "cooled down: plasma lost": "冷えた：プラズマ消失",
  "cooling": "冷却中",
  "could not load the library file": "ライブラリを読み込めません",
  "deuteron": "重陽子",
  "deuteron {#} keV": "重陽子 {#} keV",
  "deuteron: pull back, let go": "重陽子：引いて、放す",
  "drag or tap a point; it runs on its own": "点をドラッグかタップ、あとは自動",
  "easiest: {a} keV, nτT {b}": "最も容易：{a} keV、nτT {b}",
  "edge: q = {#} · lines that cross it are lost": "端：q = {#} · 越えた線は失われる",
  "electron {#} keV": "電子 {#} keV",
  "energy of the colliding pair (keV)": "衝突する組のエネルギー（keV）",
  "few are this fast": "これほど速いのは少数",
  "fusion rate: {a} the rate at {b} keV": "核融合率：{b} keVでの{a}",
  "grain boundary": "結晶粒界",
  "heating itself": "自己加熱",
  "helium stays and gathers into bubbles; hydrogen mostly diffuses out": "ヘリウムは残って泡に、水素は大半が拡散で抜ける",
  "helium {#} appm": "ヘリウム {#} appm",
  "hill to climb: charge product Z₁Z₂ = {#}": "登る丘：電荷の積 Z₁Z₂ = {#}",
  "hold: heaters on (Q = fusion power / heating) · let go: heaters off, the plasma is on its own": "押す：加熱オン（Q = 核融合出力 / 加熱）· 放す：加熱オフ、プラズマだけ",
  "hydrogen {#} appm": "水素 {#} appm",
  "ignition (Q = ∞)": "点火（Q = ∞）",
  "kT (keV)": "kT（keV）",
  "kT {#} keV · E₀ {#} keV · width {#} keV": "kT {#} keV · E₀ {#} keV · 幅 {#} keV",
  "kT {a} keV · D–T {b} m³/s · {c}× D–D": "kT {a} keV · D–T {b} m³/s · D–Dの{c}倍",
  "keeps itself hot": "自力で高温維持",
  "laps {#}": "周回 {#}",
  "lead–lithium": "鉛–リチウム",
  "liquid lithium": "液体リチウム",
  "loading INCOGNITA's cross sections…": "INCOGNITAの断面積を読み込み中…",
  "missing {#} u  =  {#} MeV out": "欠損 {#} u  =  {#} MeV放出",
  "n τE (s/m³)": "n τE（s/m³）",
  "negative: turns the other way": "負：逆向きに回る",
  "neutron escapes": "中性子が脱出",
  "peak near {#} keV": "ピーク約{#} keV",
  "per fusion neutron · {#} neutrons · cross sections are simple fits": "核融合中性子1個あたり · 中性子{#}個 · 断面積は簡易フィット",
  "plasma": "プラズマ",
  "product ×{a}": "積 ×{a}",
  "push {a} keV · chance to tunnel head-on {b}": "押す {a} keV · 正面トンネル確率 {b}",
  "q = {#}": "q = {#}",
  "q = {#}/{#}: closes after {#} lap": "q = {#}/{#}：{#}周で閉じる",
  "q = {#}/{#}: closes after {#} laps": "q = {#}/{#}：{#}周で閉じる",
  "q = {#}: no simple fraction, the dots fill the circle": "q = {#}：簡単な分数でなく、点が円を埋める",
  "screen radius is logarithmic: {#} fm to {#} fm": "半径は対数目盛：{#} fm～{#} fm",
  "shield": "遮蔽",
  "tap to fire": "タップで発射",
  "the cut, flat": "断面を平らに",
  "time slowed {a}×": "時間を{a}分の1に",
  "tries {#} · fused {#}": "試行 {#} · 融合 {#}",
  "tritium made, by depth": "深さごとの生成トリチウム",
  "triton": "三重陽子",
  "tunnels more easily": "トンネルしやすい",
  "turns at {#} fm": "{#} fmで折り返す",
  "wall": "壁",
  "{#} MeV": "{#} MeV",
  "{#} cm": "{#} cm",
  "{#} in {a}": "{a}回に{#}回",
  "{#} keV": "{#} keV",
  "{#} keV = {#} million K": "{#} keV = {#}百万K",
  "{a} %": "{a} %",
  "{a} + {a} → {b}: about {c} MeV released": "{a} + {a} → {b}：約{c} MeVを放出",
  "{a} + {a} → {b}: costs {c} MeV": "{a} + {a} → {b}：{c} MeVが必要",
  "{a} keV · chance {b}": "{a} keV · 確率 {b}",
  "{a} keV · nτ {b} · {c}": "{a} keV · nτ {b} · {c}",
  "{a} · two branches, equally likely": "{a} · 2つの分岐、確率は等しい",
  "{a} · ρ up to {b} · {c} turns a second": "{a} · ρ最大{b} · 毎秒{c}回転",
  "σ at {#} MeV:  (n,α) {#} mb · (n,p) {#} mb · (n,{#}n) {#} mb": "{#} MeVのσ：(n,α) {#} mb · (n,p) {#} mb · (n,{#}n) {#} mb",
  "⁶Li {#} · ⁷Li {#} · (n,{#}n) {#}": "⁶Li {#} · ⁷Li {#} · (n,{#}n) {#}",
  "⁶Li {#} · ⁷Li {#} · (n,{#}n) {#} · captured {#} · leaked {#}": "⁶Li {#} · ⁷Li {#} · (n,{#}n) {#} · 吸収 {#} · 漏れ {#}",
  "⟨σv⟩ (m³/s)": "⟨σv⟩（m³/s）",
});
