/* Korean: spentfuel (사용후핵연료, 핵종별로) */
WT.L.ch.spentfuel = {
  num: "강의 1", title: "사용후핵연료, 핵종별로", short: "핵종별로",
  html: `
<div class="step">
  <h3>안에 무엇이 있나</h3>
  <p>꺼낸 지 1년 된 PWR 연료 1톤(농축도 4.2 %, 50 GWd/t): 질량은 거의 모두 우라늄이고, 방사능은 거의 모두 몇 킬로그램에 몰려 있습니다.</p>
</div>
<div class="step">
  <h3>방사능이냐 방사독성이냐</h3>
  <p>베크렐은 붕괴 수를 셉니다. 시버트는 삼켰을 때의 해로움으로 각 붕괴에 가중치를 주므로 알파 방출체가 커집니다.</p>
  <div class="btns"><button class="btn ghost" data-act="mA" aria-pressed="false">방사능(Bq)</button> <button class="btn ghost" data-act="mT" aria-pressed="true">방사독성(Sv)</button></div>
</div>
<div class="step">
  <h3>언제 누가 지배하나</h3>
  <p>띠에 마우스를 올리거나 탭하면 이름이 나옵니다. 시간 축을 따라 끌면 순위가 바뀝니다.</p>
</div>
<div class="step">
  <h3>플루토늄 재활용</h3>
  <p>4년 뒤의 재처리로 플루토늄을(우라늄도 함께) 꺼냅니다. 얼마나 남겨질까요?</p>
  <div class="btns"><span class="sf-k" style="font:600 13px var(--sans);color:var(--soft);margin-right:4px;align-self:center">Pu removed</span> <button class="btn ghost" data-act="pu0" aria-pressed="true">0 %</button> <button class="btn ghost" data-act="pu99" aria-pressed="false">99 %</button> <button class="btn ghost" data-act="pu999" aria-pressed="false">99.9 %</button></div>
</div>
<div class="step">
  <h3>부악티늄족도 제거하기</h3>
  <p>아메리슘, 퀴륨, 넵투늄도 꺼내면 남겨진 1 % 또는 0.1 %가 시간을 결정합니다.</p>
  <div class="btns"><span class="sf-k" style="font:600 13px var(--sans);color:var(--soft);margin-right:4px;align-self:center">Pu removed</span> <button class="btn ghost" data-act="pu0" aria-pressed="true">0 %</button> <button class="btn ghost" data-act="pu99" aria-pressed="false">99 %</button> <button class="btn ghost" data-act="pu999" aria-pressed="false">99.9 %</button></div>
  <div class="btns"><span class="sf-k" style="font:600 13px var(--sans);color:var(--soft);margin-right:4px;align-self:center">Am, Cm, Np removed</span> <button class="btn ghost" data-act="ma0" aria-pressed="true">0 %</button> <button class="btn ghost" data-act="ma99" aria-pressed="false">99 %</button> <button class="btn ghost" data-act="ma999" aria-pressed="false">99.9 %</button></div>
</div>`,
};
Object.assign(WT.L.labels, {
  "Am{#}": "Am{#}",
  "Am{#} {#} %": "Am{#} {#} %",
  "Cm{#}": "Cm{#}",
  "Cs{#}": "Cs{#}",
  "I{#}": "I{#}",
  "NEA {#} + computed": "NEA {#} + 계산",
  "Np{#}": "Np{#}",
  "Pu{#}": "Pu{#}",
  "Pu{#} {#} %": "Pu{#} {#} %",
  "Sr{#}": "Sr{#}",
  "Sr{#} + Y{#}": "Sr{#} + Y{#}",
  "Tc{#}": "Tc{#}",
  "activity": "방사능",
  "activity after {#} year (log scale)": "{#}년 뒤 방사능 (로그 눈금)",
  "below the ore after ≈ {#} years": "약 {#}년 뒤 광석 아래로",
  "computed (Bateman decay, ICRP{#}) · band height = share of the total": "계산값 (Bateman 붕괴, ICRP{#}) · 띠 높이 = 전체 중 비율",
  "computed · band height = share": "계산값 · 띠 높이 = 비율",
  "drag along the time axis · hover a band": "시간 축을 따라 끌기 · 띠 위에 올리기",
  "inventory: OECD-NEA {#} ({#} %, {#} GWd/t) + computed fission products": "재고량: OECD-NEA {#} ({#} %, {#} GWd/t) + 계산한 핵분열 생성물",
  "mass": "질량",
  "mass (log scale)": "질량 (로그 눈금)",
  "most of the {#} kg of fission products is stable; activity includes short-lived daughters": "핵분열 생성물 {#} kg 대부분은 안정; 방사능에는 수명이 짧은 딸핵종 포함",
  "once-through": "일회 통과",
  "once-through (no recycling)": "일회 통과 (재활용 없음)",
  "ore: {#}×{#}⁵ Sv": "광석: {#}×{#}⁵ Sv",
  "other FP": "기타 FP",
  "other FP: mostly stable": "기타 FP: 대부분 안정",
  "other fission products": "기타 핵분열 생성물",
  "radiotoxicity if swallowed (Sv), relative to the ore": "삼켰을 때의 방사독성 (Sv), 광석 대비",
  "radiotoxicity ÷ ore": "방사독성 ÷ 광석",
  "reprocessing at {#} yr": "{#}년에 재처리",
  "the ore it came from: {#} t natural uranium + daughters = {#}×{#}⁵ Sv": "원래 광석: 천연 우라늄 {#} t + 딸핵종 = {#}×{#}⁵ Sv",
  "then mostly Am{#} ({#} %)": "그때는 주로 Am{#} ({#} %)",
  "then mostly Pb{#} + Po{#} ({#} %)": "그때는 주로 Pb{#} + Po{#} ({#} %)",
  "then mostly Sr{#} + Y{#} ({#} %)": "그때는 주로 Sr{#} + Y{#} ({#} %)",
  "uranium": "우라늄",
  "years after unloading (log scale) →": "꺼낸 뒤 햇수 (로그 눈금) →",
  "{#} g": "{#} g",
  "{#} kg": "{#} kg",
  "{#} million": "{#}백만",
  "{#} years:": "{#}년:",
  "{#} yr": "{#}년",
  "{#}¹³ Bq": "{#}¹³ Bq",
  "{#}¹⁰ Bq": "{#}¹⁰ Bq",
  "{#}¹⁶ Bq": "{#}¹⁶ Bq",
  "other Am, Cm": "기타 Am, Cm",
  "decay daughters (Ra, Pb, Po, Th…)": "붕괴 딸핵종 (Ra, Pb, Po, Th…)",
  "daughters": "딸핵종",
  "still above the ore after a million years": "100만 년 뒤에도 여전히 광석보다 위",
  "drag the time · tap a band": "시간을 끌기 · 띠를 탭",
  "activity ÷ ore": "방사능 ÷ 광석",
  "activity (Bq), relative to the ore": "방사능 (Bq), 광석 대비",
});
