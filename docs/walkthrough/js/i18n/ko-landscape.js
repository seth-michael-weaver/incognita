/* Korean: landscape (4장, 지형) */
WT.L.ch.landscape = {
  num: "4장", title: "원자핵의 지형", short: "지형",
  lead: "사람이 지금까지 만든 모든 원자핵이 한 장의 지도에 있습니다. 지금까지 3,338개이고, 영원히 지속되는 것은 252개뿐입니다.",
  html: `
<div class="step">
  <h3>핵종 도표</h3>
  <p>작은 사각형 하나하나는 실험에서 실제로 관측된 원자핵 하나입니다. 가로로는 중성자 수, 세로로는 양성자 수를 셉니다. 옅은 사각형은 관측은 되었지만 질량은 아직 재지 못하고 추정만 한 것입니다. <b>짙은</b> 사각형은 결코 붕괴하지 않는 252개입니다. 나머지는 붕괴하는데, 주황색은 눈 깜짝할 사이에, 파란색은 몇 해가 지나서야 붕괴합니다. <em style="font-style:normal;color:var(--proton);font-weight:600">빨간</em> 줄은 슬라이더로 고른 원소, 곧 그 원소의 알려진 모든 동위원소입니다.</p>
  <div class="ctl"><label for="ls-z">원소 보기 (양성자 수 Z)</label><input id="ls-z" type="range" data-bind="zSel" data-instant min="1" max="110" step="1" value="26"><output data-show="zSel" data-fmt="0"></output></div>
  <p class="ctl-result" id="ls-z-out" aria-live="polite"></p>
</div>
<div class="step">
  <h3>핵종 도표 위의 결합 에너지</h3>
  <p>이제 각 사각형은 <b>핵자당 결합 에너지</b>, 곧 중성자나 양성자 하나가 얼마나 단단히 붙들려 있는가(3장)에 따라 색이 칠해져 있습니다. 안정한 원자핵은 결합이 강한 능선을 따라 놓입니다. 거기서 벗어나 중성자가 너무 많거나 양성자가 너무 많으면 결합이 약해집니다. 가장 강한 것은 니켈-62입니다. 가는 선은 원자핵이 유난히 단단히 결합하는 <b>마법수</b>(8, 20, 28, 50, 82, 126)를 표시합니다.</p>
</div>
<div class="step">
  <h3>안정을 향한 베타 붕괴</h3>
  <p>핵자의 총수(<b>질량수</b> A)가 같은 원자핵은 지도 위에서 <em style="font-style:normal;color:var(--proton);font-weight:600">빨간색</em>으로 표시된 대각선 위에 놓입니다. 쪼개진 우라늄 원자핵의 조각처럼 중성자가 너무 많은 상태에서 출발합니다. <b>베타 붕괴</b>에서는 중성자 하나가 양성자로 바뀌므로, 원자핵은 그 선을 따라 더 단단히 결합한 가운데 쪽으로 한 칸씩, 능선에 닿아 멈출 때까지 거듭 나아갑니다. 작은 그래프는 같은 사슬을 원자핵이 굴러 내려가는 골짜기로 보여 줍니다. A = 137을 해 보세요. 사슬은 원자로 사고의 오래 사는 생성물인 세슘-137을 지나갑니다.</p>
  <div class="ctl"><label for="ls-a">질량수 A</label><input id="ls-a" type="range" data-bind="aSel" data-instant min="8" max="250" step="1" value="137"><output data-show="aSel" data-fmt="0"></output></div>
  <p class="ctl-result" id="ls-a-out" aria-live="polite"></p>
</div>
<div class="step">
  <h3>INCOGNITA가 다루는 범위</h3>
  <p>같은 지도를 이번에는 우리 라이브러리가 각 원자핵에 대해 가진 것에 따라 칠했습니다. <em style="font-style:normal;color:var(--fission);font-weight:600">초록색</em>은 측정된 공명으로부터 평가한 것입니다. 나머지는 엔진만으로 만든 모델 파일을 가지고 있습니다. <b>짙은색</b>은 안정하거나 오래 사는 것(A 등급), <em style="font-style:normal;color:var(--accent);font-weight:600">파란색</em>은 하루가 넘는 것(B 등급), <em style="font-style:normal;color:var(--warm);font-weight:600">주황색</em>은 더 짧게 사는 것(C 등급)입니다. 회색은 라이브러리에 없는 것으로, 대부분 가장 가벼운 원자핵과 엔진이 돌릴 수 없는 몇 개입니다.</p>
</div>`,
};

// canvas labels added 2026-10-29 (I18NLABELS_B)
Object.assign(WT.L.labels, {
  "neutrons N →": "중성자 수 N →",
  "protons Z ↑": "양성자 수 Z ↑",
  "Fe: all its isotopes": "Fe: 모든 동위원소",
  "stable": "안정",
  "lives years": "수년 생존",
  "gone in a blink": "눈 깜짝할 사이",
  "red: Fe (your pick)": "빨강: Fe (선택한 원소)",
  "nickel{#}: most tightly bound": "니켈{#}: 가장 단단히 결합",
  "held most tightly": "가장 단단히 결합",
  "middle": "중간",
  "held least": "가장 약하게 결합",
  "red: the A = {#} chain": "빨강: A = {#} 사슬",
  "A = {#}: deeper = more tightly bound": "A = {#}: 깊을수록 더 단단히 결합",
  "protons Z →": "양성자 수 Z →",
  "measured resonances": "측정된 공명",
  "tier A": "A 등급",
  "tier B": "B 등급",
  "tier C": "C 등급",
  "not in library": "라이브러리에 없음",
});
