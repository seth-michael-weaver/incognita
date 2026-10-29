/* Korean: products (15장, 핵분열 생성물) */
WT.L.ch.products = {
  num: "15장", title: "핵분열 생성물과 붕괴열", short: "핵분열 생성물",
  html: `
<div class="step">
  <p>조각들은 크기가 같지 않아서 하나는 가볍고 하나는 무겁습니다. 차트는 조각 질량 A(양성자와 중성자의 합)마다 그것을 만드는 핵분열의 몫을 보여 줍니다. 봉우리가 둘입니다. 가벼운 조각은 A = 95 근처, 무거운 조각은 139 근처입니다. A = 117 근처의 균등 분할은 약 100배 드뭅니다.</p>
  <p>점선은 아래 것보다 각각 열 배 높아서 드문 질량도 보입니다. 막대를 누르거나 슬라이더를 끌어 보세요. 아래에 그 분할의 두 조각이 나옵니다. 두 질량의 합은 236(우라늄-235 더하기 중성자)이 아니라 234입니다. 약 2.4개의 중성자가 함께 날아가기 때문입니다.</p>
  <div class="ctl"><label for="pr-a">가벼운 조각 A</label><input id="pr-a" type="range" data-bind="pick" data-instant min="70" max="117" step="1" value="95"><output data-show="pick" data-fmt="0"></output></div>
</div>
<div class="step">
  <p>이 조각들의 붕괴는 정지한 뒤에도 연료를 계속 데웁니다. 조각들은 방사성이어서 차례로 붕괴하고, 붕괴할 때마다 연쇄 반응이 돌든 말든 열이 나옵니다.</p>
  <div class="ctl"><label for="pr-t">정지 후 시간</label><input id="pr-t" type="range" data-bind="lgt" data-instant min="0" max="8.5" step="0.01" value="0"><output id="pr-tout">1 s</output></div>
  <p>시간을 끌어 보세요. 원자로가 멈춘 지 1초 뒤에도 붕괴는 여전히 전출력의 약 6%를 내고, 하루 뒤에는 약 0.5%, 1년 뒤에는 100분의 몇 퍼센트로, 큰 원자로에서는 그래도 1메가와트 가까이 됩니다. 사용 후 연료를 몇 년 동안 냉각 수조에 두는 이유입니다. 곡선은 Way–Wigner 어림 법칙으로, 1년간 가동한 뒤 모든 조각의 붕괴를 합친 간단한 식 하나입니다. 두 눈금 모두 표시마다 열 배씩 뜁니다.</p>
</div>`,
};

// canvas labels added 2026-10-29 (I18NLABELS_B)
Object.assign(WT.L.labels, {
  "fragment mass number A →": "조각 질량수 A →",
  "share of fissions that make it (each line ×{#})": "그 조각을 만드는 핵분열의 몫 (선마다 ×{#})",
  "Rb{#} · {#} %": "Rb{#} · {#} %",
  "Xe{#} · {#} %": "Xe{#} · {#} %",
  "+ about {#} neutrons": "+ 중성자 약 {#}개",
  "{#} % of full power": "전출력의 {#} %",
  "≈ {#} MW in a {#} MW reactor · {#} s after shutdown": "≈ {#} MW ({#} MW 원자로) · 정지 후 {#} s",
  "{#} min": "{#}분",
  "{#} h": "{#}시간",
  "{#} day": "{#}일",
  "{#} yr": "{#}년",
  "time after shutdown (each mark much later) →": "정지 후 시간 (눈금마다 훨씬 뒤) →",
  "Way–Wigner rule of thumb, after a year at full power": "Way–Wigner 어림 법칙, 전출력 1년 가동 후",
});
