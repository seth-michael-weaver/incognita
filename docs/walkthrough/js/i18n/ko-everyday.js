/* Korean: everyday (생활 속의 원자력) */
WT.L.ch.everyday = {
  num: "강의 4", title: "생활 속의 원자력", short: "생활 속에서",
  html: `
<div class="step">
  <h3>PET 검사</h3>
  <p>플루오린-18 추적자(반감기 110분)는 양전자를 내고, 양전자 하나하나가 서로 반대 방향으로 날아가는 511 keV 감마선 두 개로 바뀝니다. 뜨거운 점을 끌어 보세요. 링이 쌍마다 선을 긋고, 선들은 추적자가 있는 곳에서 교차합니다.</p>
</div>
<div class="step">
  <h3>방사선 치료</h3>
  <p>여러 방향의 빔이 종양에서 겹치므로 종양은 전체 선량을 받고, 건강한 조직을 지나는 각 경로는 그 일부만 받습니다. 끌어서 빔을 돌려 척수를 피하세요.</p>
  <div class="ctl"><label for="ev-n">빔</label><input id="ev-n" type="range" data-bind="nb" data-instant min="1" max="7" step="1" value="5"><output data-show="nb" data-fmt="0"></output></div>
  <div class="ctl"><label for="ev-r">회전</label><input id="ev-r" type="range" data-bind="rotd" data-instant min="0" max="360" step="1" value="20"><output class="ev-rot"></output></div>
</div>
<div class="step">
  <h3>테크네튬-99m</h3>
  <p>핵의학 검사 대부분에 쓰이는 이 동위원소는 몸 밖의 카메라가 볼 수 있는 140 keV 감마선을 내고, 반감기가 6시간이라 하루가 지나면 거의 남지 않습니다. 병원은 <a href="#chains-3">몰리브덴-99에서 이것을 "짜냅니다"</a>.</p>
  <div class="ctl"><label for="ev-t">투여 후 시간</label><input id="ev-t" type="range" data-bind="th" data-instant min="0" max="48" step="0.5" value="0"><output data-show="th" data-fmt="1"></output></div>
</div>
<div class="step">
  <h3>탄소 연대 측정</h3>
  <p>살아 있는 생물은 탄소-14를 계속 받아들이고, 죽은 뒤에는 탄소-14가 반감기 5730년으로 붕괴합니다. 나이를 정하거나, 남은 양을 재서 나이를 읽어 보세요.</p>
  <div class="ctl"><label for="ev-a">나이(년)</label><input id="ev-a" type="range" data-bind="age" data-instant min="0" max="50000" step="10" value="5300"><output class="ev-age"></output></div>
  <div class="ctl"><label for="ev-f">남은 탄소-14(%)</label><input id="ev-f" type="range" data-bind="fr" data-instant min="0.3" max="100" step="0.1" value="52.7"><output class="ev-fr"></output></div>
</div>
<div class="step">
  <h3>연기 감지기</h3>
  <p>밀봉된 아메리슘-241 한 조각이 작은 공기 틈으로 알파 입자를 보내 아주 작은 전류를 나르는 이온을 만듭니다. 연기가 이온을 붙잡으면 전류가 떨어지고 경보가 울립니다.</p>
  <div class="ctl"><label for="ev-s">연기</label><input id="ev-s" type="range" data-bind="sm" data-instant min="0" max="1" step="0.01" value="0"><output class="ev-sm"></output></div>
</div>`,
};
Object.assign(WT.L.labels, {
  "Am{#}": "Am{#}",
  "Mo{#} ({#} h)": "Mo{#} ({#}시간)",
  "Tc{#}m ({#} h)": "Tc{#}m ({#}시간)",
  "a strong gamma signal, easy to image": "감마 신호가 강해 영상화가 쉽다",
  "alarm": "경보",
  "alpha particles make ions in the air": "알파 입자가 공기 중에 이온을 만든다",
  "americium{#} (sealed)": "아메리슘{#} (밀봉)",
  "americium{#} · half-life {#} years · alphas reach about {#} cm in air": "아메리슘{#} · 반감기 {#}년 · 알파의 공기 중 비정 약 {#} cm",
  "beyond ~{#} years too little is left to measure": "약 {#}년이 넘으면 남은 양이 너무 적어 측정 불가",
  "carbon{#}": "탄소{#}",
  "clean air: steady current": "깨끗한 공기: 전류 일정",
  "current": "전류",
  "detector ring": "검출기 링",
  "dose": "선량",
  "fluorine{#} · half-life {#} min · {#} pairs recorded": "플루오린{#} · 반감기 {#}분 · 기록된 쌍 {#}",
  "gamma camera": "감마 카메라",
  "half-life {#} y": "반감기 {#}년",
  "illustration": "예시 그림",
  "molybdenum{#}, half-life {#} h": "몰리브덴{#}, 반감기 {#}시간",
  "nitrogen{#} (after a beta decay)": "질소{#} (베타 붕괴 뒤)",
  "pairs of {#} keV gamma rays, back to back": "반대 방향으로 나가는 {#} keV 감마선 쌍",
  "physical decay only": "물리적 붕괴만",
  "spinal cord": "척수",
  "technetium{#}m, half-life {#} h": "테크네튬{#}m, 반감기 {#}시간",
  "tracer": "추적자",
  "tumour": "종양",
  "tumour {#} % · spinal cord {#} % · healthy tissue at most {#} %": "종양 {#} % · 척수 {#} % · 건강한 조직 최대 {#} %",
  "tumour {#} % · spinal cord {#} % · other tissue at most {#} %": "종양 {#} % · 척수 {#} % · 기타 조직 최대 {#} %",
  "years": "년",
  "{#} beams cross: the tumour gets their sum": "빔 {#}개 교차: 종양은 그 합을 받는다",
  "{#} h": "{#}시간",
  "{#} h: {#} % left": "{#}시간: {#} % 남음",
  "{#} half-lives": "반감기 {#}번",
  "{#} keV gamma rays": "{#} keV 감마선",
  "{#} of {#} left": "{#}/{#} 남음",
  "{#} years · {#} % left": "{#}년 · {#} % 남음",
  "Ötzi the Iceman, ~{#} y": "아이스맨 외치, 약 {#}년",
  "tracer (drag me)": "추적자 (끌어 보세요)",
  "each decay: two {#} keV gamma rays, back to back": "붕괴마다 반대 방향으로 나가는 {#} keV 감마선 두 개",
  "one beam: more dose near the skin than in the tumour": "빔 하나: 종양보다 피부 근처 선량이 크다",
  "a beam crosses the spinal cord: turn the beams": "빔이 척수를 지난다: 빔을 돌리세요",
  "fading: half is gone every {#} hours": "약해지는 중: {#}시간마다 절반이 사라짐",
  "after a day, about {#} % is left": "하루 뒤 약 {#} % 남음",
  "nitrogen{#}": "질소{#}",
  "~{#} y: too little to measure": "약 {#}년: 너무 적어 측정 불가",
  "smoke: current down, alarm!": "연기: 전류 감소, 경보!",
  "some ions caught: current dipping": "이온 일부 포획: 전류 감소 중",
});
