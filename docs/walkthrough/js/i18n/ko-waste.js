/* Korean: waste (시간에 따른 사용후핵연료) */
WT.L.ch.waste = {
  num: "강의 1", title: "시간에 따른 사용후핵연료", short: "사용후핵연료",
  html: `
<div class="step">
  <h3>무엇이 나오는가</h3>
  <p>노심에서 4~5년을 보낸 연료 펠릿도 여전히 대부분 우라늄입니다. 몇 퍼센트는 쪼개진 원자인 <b>핵분열 생성물</b>입니다. 약 1 %는 플루토늄이고, 아메리슘 같은 더 무거운 <b>부악티늄족</b>이 미량 들어 있습니다.</p>
  <div class="btns"><button class="btn" data-act="sort">원자 분류하기</button></div>
</div>
<div class="step">
  <h3>처음 몇백 년</h3>
  <p>곡선은 사용후핵연료를 삼켰을 때의 위해도를, 그 연료를 만든 우라늄 광석의 위해도와 비교합니다. 처음에는 핵분열 생성물이 지배하지만 대부분 반감기가 30년 안팎이어서, 300년쯤 지나면 광석 수준 아래로 줄어듭니다.</p>
  <div class="ctl"><label for="wst-t1">꺼낸 뒤 지난 햇수</label><input id="wst-t1" type="range" data-bind="lt" data-instant min="0" max="6" step="0.01" value="1.5"><output data-show="yr" data-fmt="0"></output></div>
</div>
<div class="step">
  <h3>그다음은 플루토늄</h3>
  <p>남는 것은 반감기가 수백 년에서 수만 년인 플루토늄과 아메리슘입니다. 이들 때문에 사용후핵연료는 10만 년 넘게 광석 수준 위에 머뭅니다.</p>
  <div class="ctl"><label for="wst-t2">꺼낸 뒤 지난 햇수</label><input id="wst-t2" type="range" data-bind="lt" data-instant min="0" max="6" step="0.01" value="4"><output data-show="yr" data-fmt="0"></output></div>
</div>
<div class="step">
  <h3>재활용과 핵변환</h3>
  <p>플루토늄을 꺼내 새 연료로 태우면 그 기간은 약 1만 년으로 줄어듭니다. 부악티늄족까지 고속로에서 쪼개면 핵분열 생성물만 남아, 몇백 년이면 됩니다.</p>
  <div class="btns"><button class="btn ghost" data-act="rp" aria-pressed="false">플루토늄 재활용</button><button class="btn ghost" data-act="tm" aria-pressed="false">부악티늄족 핵변환</button></div>
</div>`,
};

Object.assign(WT.L.labels, {
  "Sort the atoms": "원자 분류하기",
  "Mix them again": "다시 섞기",
  "uranium": "우라늄",
  "fission products": "핵분열 생성물",
  "fission prod.": "핵분열 생성물",
  "plutonium": "플루토늄",
  "minor actinides": "부악티늄족",
  "minor act.": "부악티늄족",
  "~{#} %": "~{#} %",
  "a used fuel pellet, {#} atoms": "사용한 연료 펠릿, 원자 {#}개",
  "a used fuel pellet, {#} atoms shown": "사용한 연료 펠릿, 원자 {#}개 표시",
  "the glow: fission products are the most radioactive": "빛: 핵분열 생성물이 방사능이 가장 큼",
  "the glow: the fission products are by far the most radioactive part": "빛: 핵분열 생성물이 단연 방사능이 가장 큰 부분",
  "spent fuel": "사용후핵연료",
  "spent fuel, one tonne": "사용후핵연료 1톤",
  "the ore": "광석",
  "the ore it was made from": "원료가 된 광석",
  "{#} yr": "{#}년",
  "uranium ore level": "우라늄 광석 수준",
  "the uranium ore it was made from": "원료가 된 우라늄 광석",
  "{#} million": "{#}백만",
  "years after unloading (log scale) →": "꺼낸 뒤 햇수 (로그 눈금) →",
  "hazard vs ore (log)": "광석 대비 위해도 (로그)",
  "hazard if swallowed, relative to the ore (log scale)": "삼켰을 때의 위해도, 광석 대비 (로그 눈금)",
  "Am, Cm, Np": "Am, Cm, Np",
  "americium, curium…": "아메리슘, 퀴륨…",
  "americium": "아메리슘",
  "{#} years: {#} × the ore": "{#}년: 광석의 {#}배",
  "below the ore it came from": "원료 광석보다 낮음",
  "mostly from fission products": "주로 핵분열 생성물 때문",
  "mostly from plutonium": "주로 플루토늄 때문",
  "mostly from americium": "주로 아메리슘 때문",
  "reaches the ore level after ~{#} years": "~{#}년 뒤 광석 수준에 도달",
  "recycle + transmute": "재활용 + 핵변환",
  "recycle Pu and transmute minor actinides": "Pu 재활용과 부악티늄족 핵변환",
  "plutonium recycled": "플루토늄 재활용",
  "plutonium recycled, minor actinides in the waste": "플루토늄 재활용, 부악티늄족은 폐기물에 남음",
  "only minor actinides removed": "부악티늄족만 제거",
  "minor actinides removed, plutonium left in": "부악티늄족 제거, 플루토늄은 남음",
  "spent fuel as it is": "사용후핵연료 그대로",
  "spent fuel kept as it is": "사용후핵연료를 그대로 둔 경우",
  "illustrative shape (after OECD-NEA)": "설명용 모양 (OECD-NEA 참고)",
});
