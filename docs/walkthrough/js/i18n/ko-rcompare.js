/* Korean: rcompare (원자로 유형 비교) */
WT.L.ch.rcompare = {
  num: "강의 1", title: "원자로 유형 비교", short: "비교",
  lead: "모든 원자로는 감속재와 냉각재를 무엇으로 고르느냐의 문제입니다.",
  html: `
<div class="step">
  <h3>감속재와 냉각재</h3>
  <p>중성자를 감속시킬 물질과 열을 나를 물질을 고르세요. 유형을 누르면 해당 단계로 이동합니다.</p>
</div>
<div class="step">
  <h3>뜨거울수록 유리하다</h3>
  <p>냉각재가 노심을 떠날 때의 온도가 높을수록 더 많은 열을 전기로 바꿀 수 있습니다.</p>
</div>
<div class="step">
  <h3>현재 가동 중인 원자로</h3>
  <p>세계 원자로의 대부분은 앞의 세 가지 수냉식 유형입니다.</p>
</div>`,
};
Object.assign(WT.L.labels, {
  "ADS": "ADS",
  "AGR": "AGR",
  "BWR": "BWR",
  "GFR": "GFR",
  "HTGR": "HTGR",
  "LFR": "LFR",
  "MSR": "MSR",
  "Magnox": "Magnox",
  "Micro": "초소형",
  "Oklo": "오클로",
  "PHWR": "PHWR",
  "PHWR ~{#} %": "PHWR 약 {#} %",
  "PWR": "PWR",
  "RBMK": "RBMK",
  "SCWR": "SCWR",
  "SFR": "SFR",
  "SMR": "SMR",
  "TRIGA": "TRIGA",
  "VHTR": "VHTR",
  "about {#} power reactors in operation": "약 {#}기의 발전용 원자로가 가동 중",
  "about {#} reactors in all": "모두 약 {#}기",
  "boiling": "끓음",
  "boiling water": "끓는 물",
  "carries the heat ↓": "열을 나르는 것 ↓",
  "coolant out →": "냉각재 출구 →",
  "coolant temperature leaving the core →": "노심을 떠나는 냉각재 온도 →",
  "fast": "고속",
  "gas": "가스",
  "graphite": "흑연",
  "heavy water": "중수",
  "ideal (Carnot) limit": "이상적(카르노) 한계",
  "ideal limit": "이상적 한계",
  "illustration": "예시 그림",
  "light water": "경수",
  "liquid metal": "액체 금속",
  "molten salt": "용융염",
  "none": "없음",
  "none (fast)": "없음(고속)",
  "others ~{#} %": "기타 약 {#} %",
  "others: AGR, RBMK, fast reactors, HTR-PM": "기타: AGR, RBMK, 고속로, HTR-PM",
  "others: gas, graphite, fast, HTGR": "기타: 가스, 흑연, 고속로, HTGR",
  "salt": "용융염",
  "slows the neutrons →": "중성자 감속 →",
  "supercrit.": "초임계수",
  "supercritical water": "초임계수",
  "the world's power reactors": "세계의 발전용 원자로",
  "the world's power reactors, by type (rounded)": "세계의 발전용 원자로, 유형별(반올림)",
  "thermal": "열",
  "water": "물",
  "what carries the heat ↓": "무엇이 열을 나르나 ↓",
  "what slows the neutrons (moderator) →": "무엇이 중성자를 감속시키나(감속재) →",
  "{#} °C": "{#} °C",
  "↑ electricity": "↑ 전기",
  "↑ share of heat turned into electricity": "↑ 전기로 바뀌는 열의 비율",
});
// hover line in the temperature chart
Object.assign(WT.L.labels, {
  "Pressurized water reactor: {#} °C, {#} %": "가압경수로: {#} °C, {#} %",
  "Boiling water reactor: {#} °C, {#} %": "비등경수로: {#} °C, {#} %",
  "Pressurized heavy water reactor: {#} °C, {#} %": "가압중수로: {#} °C, {#} %",
  "Graphite-moderated boiling water reactor: {#} °C, {#} %": "흑연감속 비등경수로: {#} °C, {#} %",
  "Supercritical water reactor: {#} °C, {#} %": "초임계수로: {#} °C, {#} %",
  "Magnox: {#} °C, {#} %": "마그녹스: {#} °C, {#} %",
  "Advanced gas-cooled reactor: {#} °C, {#} %": "개량형 가스냉각로: {#} °C, {#} %",
  "High-temperature gas reactor: {#} °C, {#} %": "고온가스로: {#} °C, {#} %",
  "Very-high-temperature reactor: {#} °C, {#} %": "초고온가스로: {#} °C, {#} %",
  "Sodium-cooled fast reactor: {#} °C, {#} %": "소듐냉각 고속로: {#} °C, {#} %",
  "Lead-cooled fast reactor: {#} °C, {#} %": "납냉각 고속로: {#} °C, {#} %",
  "Gas-cooled fast reactor: {#} °C, {#} %": "가스냉각 고속로: {#} °C, {#} %",
  "Molten salt reactor: {#} °C, {#} %": "용융염 원자로: {#} °C, {#} %",
  "Small modular reactor: {#} °C, {#} %": "소형 모듈 원자로: {#} °C, {#} %",
  "Heat-pipe microreactor: {#} °C, {#} %": "히트파이프 초소형 원자로: {#} °C, {#} %",
});
