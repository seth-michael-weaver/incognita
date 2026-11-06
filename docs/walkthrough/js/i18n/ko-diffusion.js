/* Korean: diffusion (임계 크기와 누설) */
WT.L.ch.diffusion = {
  num: "강의 1", title: "임계 크기와 누설", short: "임계 크기",
  html: `
<div class="step">
  <h3>중성자는 헤매고, 일부는 샌다</h3>
  <p>중성자는 무언가에 흡수될 때까지 충돌에서 충돌로 지그재그로 움직입니다. 가장자리 가까이에서 태어나면 밖으로 헤매어 나가 잃어버릴 수 있습니다. 노심이 클수록 부피에 비해 표면이 작으므로 새는 몫이 줄어듭니다.</p>
  <div class="ctl"><label for="df-w0">노심 폭 (cm)</label><input id="df-w0" type="range" data-bind="w" data-instant min="20" max="200" step="2" value="60"><output data-show="w" data-fmt="0"></output></div>
</div>
<div class="step">
  <h3>선속의 모양</h3>
  <p>중성자 분포는 가장자리에서 거의 0으로 떨어지는 하나의 모양으로 자리 잡습니다. 평판에서는 코사인, 구에서는 sin(<i>r</i>)/<i>r</i>, 원기둥에서는 베셀 함수와 코사인의 곱입니다. 얼마나 급하게 휘어야 하는지가 <b>기하학적 버클링</b> <i>B</i>²입니다.</p>
  <div class="btns"><button class="btn ghost" data-act="dfslab" aria-pressed="false">평판</button><button class="btn ghost" data-act="dfsph" aria-pressed="true">구</button><button class="btn ghost" data-act="dfcyl" aria-pressed="false">원기둥</button></div>
  <div class="ctl"><label for="df-w1">노심 폭 (cm)</label><input id="df-w1" type="range" data-bind="w" data-instant min="20" max="200" step="2" value="80"><output data-show="w" data-fmt="0"></output></div>
</div>
<div class="step">
  <h3>임계 크기</h3>
  <p>1군 확산 이론은 <i>k</i><sub>eff</sub> = <i>k</i><sub>∞</sub> / (1 + <i>M</i>²<i>B</i>²)를 주며, 경수로에서 이동 면적 <i>M</i>²은 약 60 cm²입니다. <i>B</i>²이 재료 버클링 (<i>k</i><sub>∞</sub> − 1)/<i>M</i>²과 같아지면 노심은 임계입니다. 그 크기를 찾아보세요.</p>
  <div class="btns"><button class="btn ghost" data-act="dfslab" aria-pressed="false">평판</button><button class="btn ghost" data-act="dfsph" aria-pressed="true">구</button><button class="btn ghost" data-act="dfcyl" aria-pressed="false">원기둥</button></div>
  <div class="ctl"><label for="df-w2">노심 폭 (cm)</label><input id="df-w2" type="range" data-bind="w" data-instant min="20" max="200" step="1" value="90"><output data-show="w" data-fmt="0"></output></div>
</div>
<div class="step">
  <h3>반사체는 중성자를 아낀다</h3>
  <p>평판 노심을 물로 둘러싸 보세요. 빠져나간 중성자 일부가 산란되어 되돌아옵니다. 선속이 노심 가장자리에서 더 이상 0으로 떨어지지 않으므로 더 얇은 노심으로 같은 <i>k</i>에 이릅니다. 그 이득이 <b>반사체 절약</b>이며, 여기서는 한쪽에 약 6 cm입니다.</p>
  <div class="btns"><button class="btn ghost" data-act="dfrefl" aria-pressed="true">물 반사체</button></div>
  <div class="ctl"><label for="df-w3">노심 폭 (cm)</label><input id="df-w3" type="range" data-bind="w" data-instant min="20" max="120" step="1" value="44"><output data-show="w" data-fmt="0"></output></div>
</div>`,
};

Object.assign(WT.L.labels, {
  "B² = ({#}/R)² + (π/H)² = {#} × {#}⁻⁴ cm⁻²": "B² = ({#}/R)² + (π/H)² = {#} × {#}⁻⁴ cm⁻²",
  "B² = (π/R)² = {#} × {#}⁻⁴ cm⁻²": "B² = (π/R)² = {#} × {#}⁻⁴ cm⁻²",
  "B² = (π/a)² = {#} × {#}⁻⁴ cm⁻²": "B² = (π/a)² = {#} × {#}⁻⁴ cm⁻²",
  "{#} × {#}⁻⁴ cm⁻²": "{#} × {#}⁻⁴ cm⁻²",
  "bare: k_eff {#} · critical at {#} cm": "맨노심: k_eff {#} · {#} cm에서 임계",
  "core width →": "노심 폭 →",
  "critical {#} cm": "임계 {#} cm",
  "critical: B² = B²ₘ, k_eff = {#}": "임계: B² = B²ₘ, k_eff = {#}",
  "cylinder": "원기둥",
  "cylinder {#} cm wide · smaller core → sharper bend → larger B²": "폭 {#} cm 원기둥 · 작은 노심 → 급한 휨 → 큰 B²",
  "drag the edge": "가장자리를 끌기",
  "flux across the middle": "가운데를 가로지르는 선속",
  "illustration": "예시 그림",
  "k = {#}": "k = {#}",
  "k_eff = k∞ × ({#} − leak) = {#}": "k_eff = k∞ × ({#} − 누설) = {#}",
  "k_eff = {#} / ({#} + {#} cm² × {#}e{#} cm⁻²) = {#}": "k_eff = {#} / ({#} + {#} cm² × {#}e{#} cm⁻²) = {#}",
  "leak: walk {#} % · diffusion {#} %": "누설: 무작위 걷기 {#} % · 확산 {#} %",
  "red: leaked": "빨강: 누설",
  "red: leaked out · blue: absorbed inside": "빨강: 밖으로 샘 · 파랑: 안에서 흡수",
  "reflected: k_eff {#} · bare: {#} · savings {#} cm per side": "반사체 있음: k_eff {#} · 맨노심: {#} · 한쪽 절약 {#} cm",
  "share leaking: random walk {#} % · diffusion theory {#} %": "새는 몫: 무작위 걷기 {#} % · 확산 이론 {#} %",
  "slab": "평판",
  "slab core": "평판 노심",
  "slab {#} cm wide · smaller core → sharper bend → larger B²": "폭 {#} cm 평판 · 작은 노심 → 급한 휨 → 큰 B²",
  "sphere": "구",
  "sphere {#} cm wide · smaller core → sharper bend → larger B²": "폭 {#} cm 구 · 작은 노심 → 급한 휨 → 큰 B²",
  "water": "물",
  "{#} cm": "{#} cm",
  "−D∇²φ + Σₐφ = (νΣ_f / k) φ": "−D∇²φ + Σₐφ = (νΣ_f / k) φ",
});
