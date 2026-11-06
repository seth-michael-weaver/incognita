/* Japanese: diffusion (臨界寸法と中性子の漏れ) */
WT.L.ch.diffusion = {
  num: "レッスン 1", title: "臨界寸法と中性子の漏れ", short: "臨界寸法",
  html: `
<div class="step">
  <h3>中性子はさまよい、一部は漏れる</h3>
  <p>中性子は衝突から衝突へとジグザグに進み、やがて何かに吸収されます。端の近くで生まれた中性子は、外へさまよい出て失われることがあります。炉心が大きいほど体積に対する表面積が小さくなるので、漏れる割合は小さくなります。</p>
  <div class="ctl"><label for="df-w0">炉心の幅（cm）</label><input id="df-w0" type="range" data-bind="w" data-instant min="20" max="200" step="2" value="60"><output data-show="w" data-fmt="0"></output></div>
</div>
<div class="step">
  <h3>中性子束の形</h3>
  <p>中性子の分布は、端でほぼ0になる1つの形に落ち着きます。平板では余弦、球ではsin(<i>r</i>)/<i>r</i>、円柱ではベッセル関数と余弦の積です。どれだけ急に曲がらなければならないかを表すのが<b>幾何学的バックリング</b><i>B</i>²です。</p>
  <div class="btns"><button class="btn ghost" data-act="dfslab" aria-pressed="false">平板</button><button class="btn ghost" data-act="dfsph" aria-pressed="true">球</button><button class="btn ghost" data-act="dfcyl" aria-pressed="false">円柱</button></div>
  <div class="ctl"><label for="df-w1">炉心の幅（cm）</label><input id="df-w1" type="range" data-bind="w" data-instant min="20" max="200" step="2" value="80"><output data-show="w" data-fmt="0"></output></div>
</div>
<div class="step">
  <h3>臨界寸法</h3>
  <p>1群拡散理論では<i>k</i><sub>eff</sub> = <i>k</i><sub>∞</sub> / (1 + <i>M</i>²<i>B</i>²)となります。移動面積<i>M</i>²は軽水炉で約60 cm²です。<i>B</i>²が材料バックリング(<i>k</i><sub>∞</sub> − 1)/<i>M</i>²に等しいとき、炉心は臨界になります。その大きさを見つけてください。</p>
  <div class="btns"><button class="btn ghost" data-act="dfslab" aria-pressed="false">平板</button><button class="btn ghost" data-act="dfsph" aria-pressed="true">球</button><button class="btn ghost" data-act="dfcyl" aria-pressed="false">円柱</button></div>
  <div class="ctl"><label for="df-w2">炉心の幅（cm）</label><input id="df-w2" type="range" data-bind="w" data-instant min="20" max="200" step="1" value="90"><output data-show="w" data-fmt="0"></output></div>
</div>
<div class="step">
  <h3>反射体は中性子を節約する</h3>
  <p>平板の炉心を水で囲むと、外へ出た中性子の一部が散乱して戻ってきます。中性子束は炉心の端で0まで下がらなくなるので、より薄い炉心で同じ<i>k</i>に届きます。この差が<b>反射体節約</b>で、ここでは片側約6 cmです。</p>
  <div class="btns"><button class="btn ghost" data-act="dfrefl" aria-pressed="true">水反射体</button></div>
  <div class="ctl"><label for="df-w3">炉心の幅（cm）</label><input id="df-w3" type="range" data-bind="w" data-instant min="20" max="120" step="1" value="44"><output data-show="w" data-fmt="0"></output></div>
</div>`,
};
Object.assign(WT.L.labels, {
  "B² = ({#}/R)² + (π/H)² = {#} × {#}⁻⁴ cm⁻²": "B² = ({#}/R)² + (π/H)² = {#} × {#}⁻⁴ cm⁻²",
  "B² = (π/R)² = {#} × {#}⁻⁴ cm⁻²": "B² = (π/R)² = {#} × {#}⁻⁴ cm⁻²",
  "B² = (π/a)² = {#} × {#}⁻⁴ cm⁻²": "B² = (π/a)² = {#} × {#}⁻⁴ cm⁻²",
  "{#} × {#}⁻⁴ cm⁻²": "{#} × {#}⁻⁴ cm⁻²",
  "bare: k_eff {#} · critical at {#} cm": "裸の炉心：k_eff {#} · 臨界 {#} cm",
  "core width →": "炉心の幅 →",
  "critical {#} cm": "臨界 {#} cm",
  "critical: B² = B²ₘ, k_eff = {#}": "臨界：B² = B²ₘ、k_eff = {#}",
  "cylinder": "円柱",
  "cylinder {#} cm wide · smaller core → sharper bend → larger B²": "幅 {#} cm の円柱 · 小さな炉心 → 急な曲がり → 大きな B²",
  "drag the edge": "端をドラッグ",
  "flux across the middle": "中央を横切る中性子束",
  "illustration": "イメージ図",
  "k = {#}": "k = {#}",
  "k_eff = k∞ × ({#} − leak) = {#}": "k_eff = k∞ × ({#} − 漏れ) = {#}",
  "k_eff = {#} / ({#} + {#} cm² × {#}e{#} cm⁻²) = {#}": "k_eff = {#} / ({#} + {#} cm² × {#}e{#} cm⁻²) = {#}",
  "leak: walk {#} % · diffusion {#} %": "漏れ：ランダムウォーク {#} % · 拡散 {#} %",
  "red: leaked": "赤：漏れた",
  "red: leaked out · blue: absorbed inside": "赤：外へ漏れた · 青：内部で吸収された",
  "reflected: k_eff {#} · bare: {#} · savings {#} cm per side": "反射体付き：k_eff {#} · 裸：{#} · 節約 片側 {#} cm",
  "share leaking: random walk {#} % · diffusion theory {#} %": "漏れる割合：ランダムウォーク {#} % · 拡散理論 {#} %",
  "slab": "平板",
  "slab core": "平板の炉心",
  "slab {#} cm wide · smaller core → sharper bend → larger B²": "幅 {#} cm の平板 · 小さな炉心 → 急な曲がり → 大きな B²",
  "sphere": "球",
  "sphere {#} cm wide · smaller core → sharper bend → larger B²": "幅 {#} cm の球 · 小さな炉心 → 急な曲がり → 大きな B²",
  "water": "水",
  "{#} cm": "{#} cm",
  "−D∇²φ + Σₐφ = (νΣ_f / k) φ": "−D∇²φ + Σₐφ = (νΣ_f / k) φ",
});
