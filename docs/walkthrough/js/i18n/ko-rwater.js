/* Korean: rwater (수냉식 원자로) */
WT.L.ch.rwater = {
  num: "강의 1", title: "수냉식 원자로", short: "수냉식",
  lead: "오늘날 거의 모든 발전용 원자로는 물로 냉각합니다. 원자로마다 물이 열을 밖으로 실어 나르는 방식이 다릅니다.",
  html: `
<div class="step">
  <h3>가압경수로(PWR)</h3>
  <p>높은 압력의 물이 열을 증기 발생기로 옮기고, 두 번째 루프에서 증기를 만듭니다.</p>
</div>
<div class="step">
  <h3>비등경수로(BWR)</h3>
  <p>물이 노심 안에서 바로 끓고, 증기는 곧장 터빈으로 갑니다. 루프가 하나뿐입니다.</p>
</div>
<div class="step">
  <h3>중수로(CANDU)</h3>
  <p>중수는 중성자를 거의 흡수하지 않고 감속시키므로 천연 우라늄만으로도 충분합니다.</p>
</div>
<div class="step">
  <h3>흑연감속 비등수로(RBMK)</h3>
  <p>흑연이 중성자를 감속시키고, 물은 수백 개의 개별 관 안에서 끓습니다.</p>
</div>
<div class="step">
  <h3>소형 모듈 원자로(SMR)</h3>
  <p>모든 것을 하나의 용기에 담은 작은 가압경수로로, 공장에서 제작합니다.</p>
</div>
<div class="step">
  <h3>초임계수로(SCWR)</h3>
  <p>221 bar 이상에서는 물이 끓지 않으므로 더 뜨겁게 운전해 더 많은 열을 전기로 바꿀 수 있습니다.</p>
</div>`,
};
Object.assign(WT.L.labels, {
  "BWR": "BWR",
  "CANDU; Canada, India, Romania, Argentina": "CANDU: 캐나다, 인도, 루마니아, 아르헨티나",
  "Generation IV design, not yet built": "4세대 설계, 아직 건설되지 않음",
  "NuScale (US), Linglong One (China)": "NuScale(미국), 링룽 1호(중국)",
  "PHWR": "PHWR",
  "PWR": "PWR",
  "RBMK": "RBMK",
  "SCWR": "SCWR",
  "SMR": "SMR",
  "about {#} % of reactors; US, Japan, Sweden": "원자로의 약 {#} %: 미국, 일본, 스웨덴",
  "about {#} in {#} of the world's reactors": "세계 원자로의 약 {#}/{#}",
  "all in one vessel": "모두 한 용기 안에",
  "boiling water in tubes": "관 속에서 끓는 물",
  "boils in the core": "노심에서 끓음",
  "calandria: cool heavy water": "칼란드리아: 차가운 중수",
  "calandria: cool heavy water slows the neutrons": "칼란드리아: 차가운 중수가 중성자를 감속",
  "condenser": "복수기",
  "control rods from below": "제어봉은 아래에서 삽입",
  "coolant out": "냉각재 출구",
  "core": "노심",
  "core, pump-free loop and steam generator in one vessel": "노심, 펌프 없는 순환 루프, 증기 발생기가 한 용기 안에",
  "electricity": "전기",
  "gen.": "발전기",
  "generator": "발전기",
  "graphite": "흑연",
  "graphite blocks slow the neutrons": "흑연 블록이 중성자를 감속",
  "horizontal pressure tubes, refuelled while running": "수평 압력관, 운전 중 연료 교체",
  "illustration": "예시 그림",
  "outlet": "출구",
  "pressure": "압력",
  "pressure tubes": "압력관",
  "reactor vessel": "원자로 용기",
  "rods from below": "제어봉은 아래에서",
  "steam gen.": "증기 발생기",
  "steam generator": "증기 발생기",
  "the Chernobyl type; a few still run in Russia": "체르노빌형, 러시아에서 몇 기가 아직 가동 중",
  "thermal neutrons · moderator: graphite · coolant: boiling water": "열중성자 · 감속재: 흑연 · 냉각재: 끓는 물",
  "thermal neutrons · moderator: heavy water · coolant: heavy water": "열중성자 · 감속재: 중수 · 냉각재: 중수",
  "thermal neutrons · moderator: light water · coolant: boiling water": "열중성자 · 감속재: 경수 · 냉각재: 끓는 물",
  "thermal neutrons · moderator: light water · coolant: supercritical water": "열중성자 · 감속재: 경수 · 냉각재: 초임계수",
  "thermal neutrons · moderator: light water · coolant: water": "열중성자 · 감속재: 경수 · 냉각재: 물",
  "thermal · mod.: graphite · cool.: boiling water": "열 · 감속: 흑연 · 냉각: 끓는 물",
  "thermal · mod.: heavy water · cool.: heavy water": "열 · 감속: 중수 · 냉각: 중수",
  "thermal · mod.: light water · cool.: boiling water": "열 · 감속: 경수 · 냉각: 끓는 물",
  "thermal · mod.: light water · cool.: supercritical water": "열 · 감속: 경수 · 냉각: 초임계수",
  "thermal · mod.: light water · cool.: water": "열 · 감속: 경수 · 냉각: 물",
  "turbine": "터빈",
  "vessel": "용기",
  "water boils in the core": "물이 노심에서 끓음",
  "water boils in ~{#} pressure tubes": "약 {#}개의 압력관 속에서 물이 끓음",
  "{#} bar": "{#} bar",
  "{#} bar: hotter than boiling, still one fluid": "{#} bar: 끓는점보다 뜨겁지만 여전히 한 가지 상의 유체",
  "{#} bar: never boils": "{#} bar: 절대 끓지 않음",
  "{#} °C": "{#} °C",
});
