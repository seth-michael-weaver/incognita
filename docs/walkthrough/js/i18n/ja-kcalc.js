/* Japanese: kcalc (Computing criticality) */
WT.L.ch.kcalc = {
  num: "レッスン 1", title: "臨界計算", short: "k の計算",
  html: `
<div class="step">
  <h3>ベンチマーク</h3>
  <p>ICSBEP の高速金属臨界集合体 4 体を実寸比で示します。Godiva と Jezebel は裸の球、Flattop-25 と Flattop-Pu は天然ウラン反射体付きです。</p>
</div>
<div class="step">
  <h3>計算した <i>k</i><sub>eff</sub></h3>
  <p>OpenMC、連続エネルギー、3 次元形状。4 体ともベンチマークの ±1σ 内です。<i>k</i><sub>eff</sub> はフィッティングに使っていません。</p>
</div>
<div class="step">
  <h3>感度プロファイル</h3>
  <p>各反応に対する <i>k</i><sub>eff</sub> の随伴感度（レサジー単位あたり）。</p>
  <div class="btns"><button class="btn ghost" data-act="se0" aria-pressed="true">Godiva</button><button class="btn ghost" data-act="se1" aria-pressed="false">Jezebel</button><button class="btn ghost" data-act="se2" aria-pressed="false">Flattop-Pu</button></div>
</div>
<div class="step">
  <h3>直接摂動による検証</h3>
  <p>感度から予測した <i>k</i><sub>eff</sub> 変化と再計算結果の比較。摂動データセット 63 組。</p>
</div>
<div class="step">
  <h3>C5G7 炉心</h3>
  <p>OECD/NEA C5G7、2 次元 1/4 炉心、UO<sub>2</sub> と MOX の燃料棒 1,056 本。<i>k</i><sub>eff</sub> は参照値から −19&nbsp;pcm、燃料棒出力の最大誤差 0.13&nbsp;%。</p>
</div>`,
};

Object.assign(WT.L.labels, {
  "{#} pcm  (±{#} benchmark)": "{#} pcm  (ベンチマーク ±{#})",
  "+{#} pcm  (±{#} benchmark)": "+{#} pcm  (ベンチマーク ±{#})",
  "Calculated − experimental k, with the benchmark ±{#}σ band": "計算 − 実験の k とベンチマークの ±{#}σ 帯",
  "Drag to rotate": "ドラッグで回転",
  "Godiva, integral sensitivity: ν {#}, fission {#} (% k per % change)": "Godiva, 積分感度：ν {#}、核分裂 {#}（1 % 変化あたりの k の %）",
  "Jezebel, integral sensitivity: ν {#}, fission {#} (% k per % change)": "Jezebel, 積分感度：ν {#}、核分裂 {#}（1 % 変化あたりの k の %）",
  "Flattop-Pu, integral sensitivity: ν {#}, fission {#} (% k per % change)": "Flattop-Pu, 積分感度：ν {#}、核分裂 {#}（1 % 変化あたりの k の %）",
  "Godiva: ν {#}, fission {#}": "Godiva: ν {#}、核分裂 {#}",
  "Jezebel: ν {#}, fission {#}": "Jezebel: ν {#}、核分裂 {#}",
  "Flattop-Pu: ν {#}, fission {#}": "Flattop-Pu: ν {#}、核分裂 {#}",
  "UO₂: {#} × mean": "UO₂: {#} × 平均",
  "MOX {#} %: {#} × mean": "MOX {#} %: {#} × 平均",
  "OpenMC re-solve, Δk (pcm)": "OpenMC 再計算、Δk (pcm)",
  "Predicted from sensitivities, Δk (pcm)": "感度からの予測、Δk (pcm)",
  "predicted Δk, pcm": "予測 Δk、pcm",
  "U{#} capture": "U{#} 捕獲",
  "Pu{#} capture": "Pu{#} 捕獲",
  "U{#} elastic": "U{#} 弾性散乱",
  "Pu{#} elastic": "Pu{#} 弾性散乱",
  "U{#} fission": "U{#} 核分裂",
  "Pu{#} fission": "Pu{#} 核分裂",
  "U{#} inelastic": "U{#} 非弾性散乱",
  "Pu{#} inelastic": "Pu{#} 非弾性散乱",
  "U{#} neutrons per fission (ν)": "U{#} 核分裂あたりの中性子数 (ν)",
  "Pu{#} neutrons per fission (ν)": "Pu{#} 核分裂あたりの中性子数 (ν)",
  "Relative pin power (hover a pin)": "燃料棒の相対出力（燃料棒にポインタを合わせる）",
  "Relative pin power (tap a pin)": "燃料棒の相対出力（燃料棒をタップ）",
  "To scale.": "実寸比。",
  "To scale. Drag to rotate.": "実寸比。ドラッグで回転。",
  "core {#} cm, reflector {#} cm": "炉心 {#} cm、反射体 {#} cm",
  "radius {#} cm": "半径 {#} cm",
  "{#} cm in {#} cm": "{#} cm / {#} cm",
  "k = {#}; reference {#} ({#} pcm)": "k = {#}；参照値 {#}（{#} pcm）",
  "k {#}, reference {#}": "k {#}、参照値 {#}",
  "plutonium in natural uranium": "天然ウラン中のプルトニウム",
  "plutonium metal": "プルトニウム金属",
  "uranium{#} in natural uranium": "天然ウラン中のウラン{#}",
  "uranium{#} metal": "ウラン{#} 金属",
  "water": "水",
  "×{#} of mean": "平均の ×{#}",
  "U{#} ν": "U{#} ν",
  "Pu{#} ν": "Pu{#} ν",
  "Godiva   k = {#}": "Godiva   k = {#}",
  "Godiva {#}": "Godiva {#}",
  "Godiva: rms {#} pcm": "Godiva: rms {#} pcm",
  "Jezebel   k = {#}": "Jezebel   k = {#}",
  "Jezebel {#}": "Jezebel {#}",
  "Jezebel: rms {#} pcm": "Jezebel: rms {#} pcm",
  "Flattop-Pu   k = {#}": "Flattop-Pu   k = {#}",
  "Flattop-Pu {#}": "Flattop-Pu {#}",
  "Flattop-Pu: rms {#} pcm": "Flattop-Pu: rms {#} pcm",
  "Flattop{#}   k = {#}": "Flattop{#}   k = {#}",
  "Flattop{#} {#}": "Flattop{#} {#}",
  "{#} pcm (±{#})": "{#} pcm (±{#})",
  "+{#} pcm (±{#})": "+{#} pcm (±{#})",
  "{#} cm": "{#} cm",
  "{#} keV": "{#} keV",
  "{#} MeV": "{#} MeV",
  "OpenMC Δk": "OpenMC Δk"
});
