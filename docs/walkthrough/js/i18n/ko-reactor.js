/* Korean: reactor (원자로가 전기를 만드는 방법) */
WT.L.ch.reactor = {
  num: "강의 1", title: "원자로가 전기를 만드는 방법", short: "원자로",
  html: `
<div class="step">
  <h3>연료</h3>
  <p>우라늄은 손가락 끝만 한 세라믹 펠릿으로 구워져 긴 금속 봉 속에 쌓이고, 그 봉들이 다발로 묶여 집합체가 됩니다. 펠릿 하나가 내는 열은 석탄 1톤을 태운 것과 맞먹습니다.</p>
  <div class="ctl"><label for="rea-z">축소</label><input id="rea-z" type="range" data-bind="z" min="0" max="3" step="0.01" value="0"><output data-show="z" data-fmt="1"></output></div>
</div>
<div class="step">
  <h3>원자를 쪼개면 열이 난다</h3>
  <p>노심에서 쪼개지는 우라늄 원자가 봉 사이로 흘러 올라가는 물을 데웁니다. 같은 물이 중성자를 느리게 만들어 더 많은 원자를 쪼갤 수 있게 합니다. 높은 압력 덕분에 물은 325 °C에서도 끓지 않습니다.</p>
</div>
<div class="step">
  <h3>증기가 터빈을 돌린다</h3>
  <p>뜨거운 물은 가는 관을 통해 열을 두 번째 회로로 넘기고, 그곳의 물이 끓습니다. 증기는 터빈과 발전기를 돌린 뒤, 차가운 강물이나 바닷물에 식어 다시 물이 됩니다. 열의 약 3분의 1이 전기가 됩니다.</p>
</div>
<div class="step">
  <h3>제어봉</h3>
  <p>제어봉은 중성자를 빨아들입니다. 밀어 넣으면 쪼개지는 원자가 줄어 열도, 증기도, 전기도 줄어듭니다. 빼내면 출력이 올라갑니다.</p>
  <div class="ctl"><label for="rea-rod">제어봉 삽입 (%)</label><input id="rea-rod" type="range" data-bind="ins" data-instant min="0" max="100" step="1" value="15"><output data-show="ins" data-fmt="0"></output></div>
</div>`,
};

Object.assign(WT.L.labels, {
  "reactor": "원자로",
  "reactor vessel": "원자로 용기",
  "core": "노심",
  "control rods": "제어봉",
  "steam gen.": "증기 발생기",
  "steam generator": "증기 발생기",
  "turbine": "터빈",
  "gen.": "발전기",
  "generator": "발전기",
  "condenser": "복수기",
  "sea or river water": "바닷물 또는 강물",
  "{#} °C out": "출구 {#} °C",
  "{#} °C in": "입구 {#} °C",
  "steam ~{#} °C": "증기 ~{#} °C",
  "{#} bar: hot, but no boiling": "{#} bar: 뜨겁지만 끓지 않음",
  "{#} bar keeps the water liquid at {#} °C": "{#} bar가 {#} °C에서도 물을 액체로 유지",
  "the water also slows the neutrons": "물은 중성자도 느리게 함",
  "the water carries the heat and slows the neutrons": "물이 열을 나르고 중성자를 느리게 함",
  "heat {#} MW": "열 {#} MW",
  "electric {#} MW": "전기 {#} MW",
  "electricity {#} MW": "전기 {#} MW",
  "chain stopped; fuel still warm (afterheat)": "연쇄 정지, 연료는 아직 따뜻함 (잔열)",
  "chain reaction stopped; the fuel still gives off afterheat": "연쇄 반응 정지, 연료는 아직 잔열을 냄",
  "turbine speed fixed by the grid; more steam, more push": "터빈 속도는 전력망이 고정, 증기가 많을수록 더 세게 밂",
  "the turbine's speed is fixed by the grid; more steam pushes harder": "터빈 속도는 전력망이 고정하며, 증기가 많을수록 더 세게 밉니다",
  "{#}/{#} of the heat goes to the water": "열의 {#}/{#}이 물로 감",
  "about two thirds of the heat leaves through the condenser": "열의 약 3분의 2가 복수기로 빠져나감",
  "illustration": "예시 그림",
  "drag sideways to zoom": "옆으로 끌어 확대·축소",
  "drag sideways to zoom out": "옆으로 끌어 축소",
  "UO₂ pellet, {#} cm": "UO₂ 펠릿, {#} cm",
  "uranium oxide pellet, about {#} cm": "산화우라늄 펠릿, 약 {#} cm",
  "{#} tonne of coal": "석탄 {#}톤",
  "about {#} tonne of coal (or {#} m³ of gas)": "석탄 약 {#}톤 (또는 가스 {#} m³)",
  "same heat, roughly": "대략 같은 열",
  "fuel rod, ~{#} m": "연료봉, ~{#} m",
  "fuel rod, about {#} m long": "연료봉, 길이 약 {#} m",
  "~{#} pellets inside": "펠릿 ~{#}개",
  "about {#} pellets in a metal tube": "금속관 속 펠릿 약 {#}개",
  "(not to scale)": "(축척 아님)",
  "assembly: {#} rods": "집합체: 봉 {#}개",
  "fuel assembly from above: {#} rods": "위에서 본 핵연료 집합체: 봉 {#}개",
  "rings: control-rod guide tubes": "고리: 제어봉 안내관",
  "rings: tubes the control rods slide into": "고리: 제어봉이 미끄러져 들어가는 관",
  "core: {#} assemblies": "노심: 집합체 {#}개",
  "the core from above: {#} assemblies": "위에서 본 노심: 집합체 {#}개",
  "~{#} rods, ~{#} m across": "봉 ~{#}개, 지름 ~{#} m",
  "about {#} rods in a cylinder about {#} m across": "봉 약 {#}개, 지름 약 {#} m의 원기둥",
  "pellet": "펠릿",
  "rod": "봉",
  "assembly": "집합체",
});
