/* Korean: dose (방사선 선량) */
WT.L.ch.dose = {
  num: "강의 3", title: "방사선 선량", short: "선량",
  html: `
<div class="step">
  <h3>시버트가 재는 것</h3>
  <p>선량은 몸 1킬로그램이 흡수한 에너지에서 출발합니다. <b>시버트</b>는 그 에너지에 피해의 정도를 가중합니다. 같은 에너지라도 알파 입자로 전달되면 감마선보다 스무 배로 셉니다. 몇 개의 촘촘한 궤적에 몰려 있기 때문입니다.</p>
  <div class="btns"><button class="btn ghost" data-act="rg" aria-pressed="true">감마선</button><button class="btn ghost" data-act="ra" aria-pressed="false">알파 입자</button></div>
</div>
<div class="step">
  <h3>일상의 선량</h3>
  <p>이 탑의 눈금은 한 칸 올라갈 때마다 아래 칸의 열 배입니다. 빛나는 구슬을 끌어 비교해 보세요. 흉부 CT 한 번은 바나나 수천 개분의 선량이고, 1년 동안의 자연 배경 방사선은 비행 수십 번분입니다.</p>
  <div class="ctl"><label for="ds-l">선량</label><input id="ds-l" type="range" data-bind="ld" data-instant min="-7" max="1" step="0.02" value="-2.15"><output class="ds-out"></output></div>
</div>
<div class="step">
  <h3>나의 1년 쌓아 보기</h3>
  <p>누구나 자연에서 1년에 약 2.4밀리시버트를 받으며, 대부분은 땅에서 나오는 라돈 기체 때문입니다. 자신의 비행, 검사, 사는 곳의 고도를 더해 보세요.</p>
  <div class="ctl"><label for="ds-f">대서양 횡단 비행 횟수</label><input id="ds-f" type="range" data-bind="fl" data-instant min="0" max="40" step="1" value="4"><output data-show="fl" data-fmt="0"></output></div>
  <div class="ctl"><label for="ds-ct">흉부 CT 횟수</label><input id="ds-ct" type="range" data-bind="ct" data-instant min="0" max="3" step="1" value="0"><output data-show="ct" data-fmt="0"></output></div>
  <div class="ctl"><label for="ds-h">사는 곳의 고도 (m)</label><input id="ds-h" type="range" data-bind="alt" data-instant min="0" max="3500" step="50" value="300"><output data-show="alt" data-fmt="0"></output></div>
</div>
<div class="step">
  <h3>한꺼번에 받는 큰 선량</h3>
  <p>약 100밀리시버트 아래에서는 늘어나는 암 위험이 너무 작아 측정할 수 없습니다. 안전 규정은 그 위험이 선량에 비례해 커진다고 가정합니다. 한꺼번에 1시버트쯤 받으면 세포가 너무 자주 맞아 방사선병이 시작됩니다.</p>
  <div class="ctl"><label for="ds-a">한꺼번에 받는 선량</label><input id="ds-a" type="range" data-bind="la" data-instant min="-3" max="1" step="0.02" value="-1"><output class="ds-out2"></output></div>
</div>`,
};

Object.assign(WT.L.labels, {
  "{#} µSv": "{#} µSv",
  "{#} mSv": "{#} mSv",
  "{#} Sv": "{#} Sv",
  "mSv": "mSv",
  "cell nuclei in a patch of body": "몸 한 부분의 세포핵들",
  "cell nuclei in a patch of body tissue": "몸 조직 한 부분의 세포핵들",
  "{#} milligray of alpha: a few cells hit hard": "알파 {#} 밀리그레이: 소수의 세포가 세게 맞음",
  "{#} milligray of gamma: about one track per cell": "감마 {#} 밀리그레이: 세포마다 궤적 약 하나",
  "same energy · counts as {#} millisieverts": "같은 에너지 · {#} 밀리시버트로 셈",
  "counts as {#} millisievert": "{#} 밀리시버트로 셈",
  "illustration": "예시 그림",
  "eating a banana  ·  {#} µSv": "바나나 한 개 먹기  ·  {#} µSv",
  "banana  ·  {#} µSv": "바나나  ·  {#} µSv",
  "dental X-ray  ·  {#} µSv": "치과 X선  ·  {#} µSv",
  "chest X-ray  ·  {#} µSv": "흉부 X선  ·  {#} µSv",
  "flight across the Atlantic  ·  {#} µSv": "대서양 횡단 비행  ·  {#} µSv",
  "Atlantic flight  ·  {#} µSv": "대서양 비행  ·  {#} µSv",
  "a year of natural background  ·  {#} mSv": "1년 자연 배경 방사선  ·  {#} mSv",
  "{#} yr background  ·  {#} mSv": "배경 방사선 {#}년  ·  {#} mSv",
  "chest CT scan  ·  {#} mSv": "흉부 CT 촬영  ·  {#} mSv",
  "chest CT  ·  {#} mSv": "흉부 CT  ·  {#} mSv",
  "yearly limit for radiation workers  ·  {#} mSv": "방사선 작업 종사자 연간 한도  ·  {#} mSv",
  "worker limit/yr  ·  {#} mSv": "종사자 연간 한도  ·  {#} mSv",
  "a year on the Kerala coast (high spots)  ·  {#} mSv": "케랄라 해안에서 1년 (높은 곳)  ·  {#} mSv",
  "Kerala, {#} yr  ·  {#} mSv": "케랄라 {#}년  ·  {#} mSv",
  "a year in the highest Ramsar homes  ·  {#} mSv": "람사르의 가장 높은 집에서 1년  ·  {#} mSv",
  "Ramsar, {#} yr  ·  {#} mSv": "람사르 {#}년  ·  {#} mSv",
  "at once: radiation sickness begins  ·  {#} Sv": "한꺼번에: 방사선병 시작  ·  {#} Sv",
  "at once: about half die untreated  ·  {#} Sv": "한꺼번에: 치료하지 않으면 약 절반 사망  ·  {#} Sv",
  "{#} Sv at once  ·  {#} Sv": "한꺼번에 {#} Sv  ·  {#} Sv",
  "{#}–{#} Sv at once  ·  {#} Sv": "한꺼번에 {#}–{#} Sv  ·  {#} Sv",
  "typical values": "대표값",
  "{#} µSv: the dose of {#} bananas": "{#} µSv: 바나나 {#}개분의 선량",
  "{#} mSv: the dose of {#} bananas": "{#} mSv: 바나나 {#}개분의 선량",
  "{#} µSv: {#} bananas, or {#} flights": "{#} µSv: 바나나 {#}개, 또는 비행 {#}번",
  "{#} µSv: {#} thousand bananas, or {#} flights": "{#} µSv: 바나나 {#}천 개, 또는 비행 {#}번",
  "{#} µSv: {#} million bananas, or {#} flights": "{#} µSv: 바나나 {#}백만 개, 또는 비행 {#}번",
  "{#} µSv: {#} bananas, or {#} thousand flights": "{#} µSv: 바나나 {#}개, 또는 비행 {#}천 번",
  "{#} µSv: {#} thousand bananas, or {#} thousand flights": "{#} µSv: 바나나 {#}천 개, 또는 비행 {#}천 번",
  "{#} µSv: {#} million bananas, or {#} thousand flights": "{#} µSv: 바나나 {#}백만 개, 또는 비행 {#}천 번",
  "{#} mSv: {#} bananas, or {#} flights": "{#} mSv: 바나나 {#}개, 또는 비행 {#}번",
  "{#} mSv: {#} thousand bananas, or {#} flights": "{#} mSv: 바나나 {#}천 개, 또는 비행 {#}번",
  "{#} mSv: {#} million bananas, or {#} flights": "{#} mSv: 바나나 {#}백만 개, 또는 비행 {#}번",
  "{#} mSv: {#} bananas, or {#} thousand flights": "{#} mSv: 바나나 {#}개, 또는 비행 {#}천 번",
  "{#} mSv: {#} thousand bananas, or {#} thousand flights": "{#} mSv: 바나나 {#}천 개, 또는 비행 {#}천 번",
  "{#} mSv: {#} million bananas, or {#} thousand flights": "{#} mSv: 바나나 {#}백만 개, 또는 비행 {#}천 번",
  "{#} Sv: {#} bananas, or {#} flights": "{#} Sv: 바나나 {#}개, 또는 비행 {#}번",
  "{#} Sv: {#} thousand bananas, or {#} flights": "{#} Sv: 바나나 {#}천 개, 또는 비행 {#}번",
  "{#} Sv: {#} million bananas, or {#} flights": "{#} Sv: 바나나 {#}백만 개, 또는 비행 {#}번",
  "{#} Sv: {#} bananas, or {#} thousand flights": "{#} Sv: 바나나 {#}개, 또는 비행 {#}천 번",
  "{#} Sv: {#} thousand bananas, or {#} thousand flights": "{#} Sv: 바나나 {#}천 개, 또는 비행 {#}천 번",
  "{#} Sv: {#} million bananas, or {#} thousand flights": "{#} Sv: 바나나 {#}백만 개, 또는 비행 {#}천 번",
  "{#} mSv: {#} bananas, {#} flights or {#} years of background": "{#} mSv: 바나나 {#}개, 비행 {#}번 또는 배경 방사선 {#}년",
  "{#} mSv: {#} thousand bananas, {#} flights or {#} years of background": "{#} mSv: 바나나 {#}천 개, 비행 {#}번 또는 배경 방사선 {#}년",
  "{#} mSv: {#} million bananas, {#} flights or {#} years of background": "{#} mSv: 바나나 {#}백만 개, 비행 {#}번 또는 배경 방사선 {#}년",
  "{#} mSv: {#} bananas, {#} thousand flights or {#} years of background": "{#} mSv: 바나나 {#}개, 비행 {#}천 번 또는 배경 방사선 {#}년",
  "{#} mSv: {#} thousand bananas, {#} thousand flights or {#} years of background": "{#} mSv: 바나나 {#}천 개, 비행 {#}천 번 또는 배경 방사선 {#}년",
  "{#} mSv: {#} million bananas, {#} thousand flights or {#} years of background": "{#} mSv: 바나나 {#}백만 개, 비행 {#}천 번 또는 배경 방사선 {#}년",
  "{#} Sv: {#} bananas, {#} flights or {#} years of background": "{#} Sv: 바나나 {#}개, 비행 {#}번 또는 배경 방사선 {#}년",
  "{#} Sv: {#} thousand bananas, {#} flights or {#} years of background": "{#} Sv: 바나나 {#}천 개, 비행 {#}번 또는 배경 방사선 {#}년",
  "{#} Sv: {#} million bananas, {#} flights or {#} years of background": "{#} Sv: 바나나 {#}백만 개, 비행 {#}번 또는 배경 방사선 {#}년",
  "{#} Sv: {#} bananas, {#} thousand flights or {#} years of background": "{#} Sv: 바나나 {#}개, 비행 {#}천 번 또는 배경 방사선 {#}년",
  "{#} Sv: {#} thousand bananas, {#} thousand flights or {#} years of background": "{#} Sv: 바나나 {#}천 개, 비행 {#}천 번 또는 배경 방사선 {#}년",
  "{#} Sv: {#} million bananas, {#} thousand flights or {#} years of background": "{#} Sv: 바나나 {#}백만 개, 비행 {#}천 번 또는 배경 방사선 {#}년",
  "radon in the air  {#}": "공기 중 라돈  {#}",
  "radon  {#}": "라돈  {#}",
  "rocks and soil  {#}": "암석과 토양  {#}",
  "ground  {#}": "땅  {#}",
  "food and water  {#}": "음식과 물  {#}",
  "food  {#}": "음식  {#}",
  "cosmic rays  {#}": "우주선  {#}",
  "cosmic rays at {#} m  {#}": "고도 {#} m의 우주선  {#}",
  "cosmic  {#}": "우주선  {#}",
  "{#} flights  {#}": "비행 {#}번  {#}",
  "flights  {#}": "비행  {#}",
  "{#} chest CT  {#}": "흉부 CT {#}번  {#}",
  "CT  {#}": "CT  {#}",
  "average {#}": "평균 {#}",
  "world average {#} mSv": "세계 평균 {#} mSv",
  "worker limit {#}": "종사자 한도 {#}",
  "worker limit {#} mSv": "종사자 한도 {#} mSv",
  "your year: {#} mSv": "나의 1년: {#} mSv",
  "more than the yearly worker limit": "종사자 연간 한도보다 많음",
  "{#} times the world average": "세계 평균의 {#}배",
  "close to the world average": "세계 평균과 비슷함",
  "tracks through each cell nucleus: about {#}": "세포핵 하나를 지나는 궤적: 약 {#}개",
  "tracks through each cell nucleus: about {#} (a few drawn)": "세포핵 하나를 지나는 궤적: 약 {#}개 (일부만 그림)",
  "tracks through each cell nucleus: about {#} thousand (a few drawn)": "세포핵 하나를 지나는 궤적: 약 {#}천 개 (일부만 그림)",
  "tracks through each cell nucleus: about {#} million (a few drawn)": "세포핵 하나를 지나는 궤적: 약 {#}백만 개 (일부만 그림)",
  "no effect seen": "관찰된 영향 없음",
  "risk assumed": "위험 가정",
  "small added risk assumed": "작은 추가 위험 가정",
  "sickness": "방사선병",
  "lethal": "치사",
  "often lethal": "자주 치사",
  "{#} mSv at once: any extra risk too small to measure": "한꺼번에 {#} mSv: 추가 위험은 측정하기엔 너무 작음",
  "{#} Sv at once: any extra risk too small to measure": "한꺼번에 {#} Sv: 추가 위험은 측정하기엔 너무 작음",
  "{#} mSv at once: no sickness; risk assumed to rise with dose": "한꺼번에 {#} mSv: 병은 없음, 위험은 선량에 따라 커진다고 가정",
  "{#} Sv at once: no sickness; risk assumed to rise with dose": "한꺼번에 {#} Sv: 병은 없음, 위험은 선량에 따라 커진다고 가정",
  "{#} mSv at once: radiation sickness: nausea, low blood counts": "한꺼번에 {#} mSv: 방사선병: 메스꺼움, 혈구 수 감소",
  "{#} Sv at once: radiation sickness: nausea, low blood counts": "한꺼번에 {#} Sv: 방사선병: 메스꺼움, 혈구 수 감소",
  "{#} mSv at once: about half die without treatment": "한꺼번에 {#} mSv: 치료하지 않으면 약 절반 사망",
  "{#} Sv at once: about half die without treatment": "한꺼번에 {#} Sv: 치료하지 않으면 약 절반 사망",
});
