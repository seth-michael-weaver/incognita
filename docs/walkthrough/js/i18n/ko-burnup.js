/* Korean: burnup (핵연료 연소도) */
WT.L.ch.burnup = {
  num: "강의 1", title: "핵연료 연소도", short: "연소도",
  html: `
<div class="step">
  <h3>펠릿의 일생</h3>
  <p>새 연료 펠릿에서 원자 1000개를 가져왔습니다. 45개는 우라늄-235, 나머지는 우라늄-238입니다. 원자로를 돌리면서 우라늄-235가 쪼개지고 새 원자가 나타나는 것을 지켜보세요. <b>연소도</b>는 꺼낸 에너지를 우라늄 1톤당 기가와트일로 셉니다. 경수로 연료는 약 45–55에서 멈춥니다.</p>
  <div class="ctl"><label for="bu-d1">전출력 운전 일수</label><input id="bu-d1" type="range" data-bind="d" data-instant min="0" max="1400" step="10" value="400"><output data-show="d" data-fmt="0"></output></div>
</div>
<div class="step">
  <h3>플루토늄이 합류한다</h3>
  <p>우라늄-238은 중성자를 포획해 플루토늄-239가 되고, 이것도 쪼개집니다. 수명 후반에는 핵분열의 절반 이상이 플루토늄에서 일어나며, 수명 전체로 보면 에너지의 약 3분의 1이 플루토늄에서 나옵니다.</p>
  <div class="ctl"><label for="bu-d2">전출력 운전 일수</label><input id="bu-d2" type="range" data-bind="d" data-instant min="0" max="1400" step="10" value="1000"><output data-show="d" data-fmt="0"></output></div>
</div>
<div class="step">
  <h3>독물질이 쌓인다</h3>
  <p>핵분열 한 번마다 핵분열 생성물 두 개가 남고, 그 일부는 중성자를 빨아들입니다. 우라늄-235는 줄고 독물질은 늘면서 <i>k</i><sub>∞</sub>(이 연료로 된 무한 격자에서 핵분열 한 번당 새 핵분열 수)가 서서히 내려가, 결국 연료 혼자서는 연쇄를 유지할 수 없게 됩니다.</p>
  <div class="ctl"><label for="bu-d3">전출력 운전 일수</label><input id="bu-d3" type="range" data-bind="d" data-instant min="0" max="1400" step="10" value="700"><output data-show="d" data-fmt="0"></output></div>
</div>
<div class="step">
  <h3>붕소와 재장전</h3>
  <p>노심에는 새 연료, 중간 연료, 오래된 연료가 섞여 있습니다. 새 연료는 반응도가 너무 크므로 냉각수에 녹인 붕소가 남는 몫을 빨아들이고, 붕소는 서서히 희석됩니다. 붕소가 0에 이르면 가장 오래된 3분의 1을 꺼내고 새 연료를 넣습니다.</p>
  <div class="ctl"><label for="bu-m">전출력 운전 개월 수</label><input id="bu-m" type="range" data-bind="m" data-instant min="0" max="54" step="0.5" value="8"><output data-show="m" data-fmt="1"></output></div>
</div>`,
};

Object.assign(WT.L.labels, {
  "GWd/t →": "GWd/t →",
  "Pu": "Pu",
  "U{#}": "U{#}",
  "boron (ppm)": "붕소 (ppm)",
  "boron in the water (ppm)": "물속 붕소 (ppm)",
  "burnup (GWd/t) →": "연소도 (GWd/t) →",
  "can't keep a chain going alone": "혼자서는 연쇄 유지 불가",
  "this fuel alone can no longer keep a chain going": "이 연료만으로는 더 이상 연쇄를 유지할 수 없음",
  "k∞ reaches {#}": "k∞가 {#}에 도달",
  "cycle {a} months · fuel leaves at {b} GWd/t": "주기 {a}개월 · 연료 방출 시 {b} GWd/t",
  "each dot: one atom in a thousand": "점 하나: 원자 1000개 중 하나",
  "each dot: {#} atom in {#}": "점 하나: 원자 {#}/{#}",
  "energy so far": "지금까지의 에너지",
  "fission products": "핵분열 생성물",
  "fission products (pairs)": "핵분열 생성물 (쌍)",
  "fission products catch {a} % of neutrons": "핵분열 생성물이 중성자의 {a} %를 포획",
  "fissions": "핵분열",
  "fissions now": "현재 핵분열",
  "fresh": "새 연료",
  "one cycle old": "1주기 연료",
  "two cycles old": "2주기 연료",
  "{#} cycle": "{#}주기",
  "{#} cycles": "{#}주기",
  "illustrative model": "설명용 모형",
  "k = {#}": "k = {#}",
  "k∞ = {a}": "k∞ = {a}",
  "months at full power →": "전출력 개월 수 →",
  "months →": "개월 →",
  "other Pu": "기타 Pu",
  "other plutonium": "기타 플루토늄",
  "plutonium": "플루토늄",
  "plutonium's share": "플루토늄의 몫",
  "plutonium{#}": "플루토늄{#}",
  "uranium{#}": "우라늄{#}",
  "uranium{#}: the remaining ~{#}–{#} %": "우라늄{#}: 나머지 ~{#}–{#} %",
  "reload": "재장전",
  "split": "핵분열",
  "typical discharge": "일반적인 방출 연소도",
  "typical discharge {#}–{#}": "일반적인 방출 연소도 {#}–{#}",
  "{a} days · burnup {b} GWd/t": "{a}일 · 연소도 {b} GWd/t",
  "{a} in {#}": "{a}/{#}",
  "{a} ppm": "{a} ppm",
});
