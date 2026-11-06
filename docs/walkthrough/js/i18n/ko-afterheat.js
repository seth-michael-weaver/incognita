/* Korean: afterheat (정지 후의 열) */
WT.L.ch.afterheat = {
  num: "강의 1", title: "정지 후의 열", short: "잔열",
  html: `
<div class="step">
  <h3>연쇄가 멈춘다</h3>
  <p>제어봉을 떨어뜨리면 약 1분 안에 원자의 분열이 멈춥니다. 그래도 연료는 계속 빛납니다. 앞서 쪼개진 조각들이 방사성이어서, 그 붕괴가 여전히 열을 내기 때문입니다.</p>
  <div class="btns"><button class="btn" data-act="ahDrop">제어봉 떨어뜨리기</button> <button class="btn ghost" data-act="ahUp">재가동</button></div>
</div>
<div class="step">
  <h3>천천히 줄어든다</h3>
  <p>정지 직후 이 열은 전출력의 약 6–7 %입니다. 1시간 뒤에는 약 1 %, 하루 뒤에는 약 0.5 %, 일주일 뒤에는 0.25 %입니다. 작은 비율이지만 아주 큰 수의 비율입니다.</p>
  <div class="ctl"><label for="ah-t">정지 후 경과 시간</label><input id="ah-t" type="range" data-bind="lt" data-instant min="0" max="7.5" step="0.01" value="3.56"></div>
</div>
<div class="step">
  <h3>물을 계속 흐르게</h3>
  <p>그래서 노심은 정지한 뒤에도 냉각합니다. 펌프가 연료 곁으로 물을 계속 흘려 열을 실어 나릅니다. 펌프를 끄면 열이 갈 곳이 없어 온도가 올라갑니다.</p>
  <div class="btns"><button class="btn ghost" data-act="ahPump" aria-pressed="true">펌프</button></div>
</div>
<div class="step">
  <h3>펌프 없는 냉각</h3>
  <p>뜨거운 물은 올라가고 차가운 물은 가라앉습니다. 노심보다 높이 둔 수조까지 이어진 회로는 펌프 없이도 물을 계속 흐르게 합니다. 여러 신형 설계가 며칠 동안 이 방식에 의지합니다.</p>
  <div class="btns"><button class="btn ghost" data-act="ahPump" aria-pressed="false">펌프</button> <button class="btn ghost" data-act="ahPass" aria-pressed="true">피동 회로</button></div>
</div>`,
};

Object.assign(WT.L.labels, {
  "cooler": "냉각기",
  "heat exchanger": "열교환기",
  "core temperature": "노심 온도",
  "temperature": "온도",
  "decaying fragments": "붕괴하는 조각",
  "splitting atoms": "분열하는 원자",
  "heat from decaying fragments": "붕괴하는 조각의 열",
  "heat from splitting atoms": "분열하는 원자의 열",
  "for a {#} MW core: {a} MW, as much as {b} electric kettles": "{#} MW 노심이면: {a} MW, 전기 주전자 {b}개만큼",
  "{#} MW core: {a} MW, like {b} kettles": "{#} MW 노심: {a} MW, 주전자 {b}개",
  "heat, as a share of full power": "열, 전출력 대비 비율",
  "heat, share of full power": "열, 전출력 대비",
  "illustration": "예시 그림",
  "normal": "정상",
  "too hot": "너무 뜨거움",
  "pool, up high": "높은 곳의 수조",
  "water pool, placed higher": "더 높이 둔 수조",
  "pump off": "펌프 꺼짐",
  "pump on": "펌프 켜짐",
  "pump running": "펌프 작동 중",
  "pump stopped": "펌프 정지",
  "pumps carry the heat away": "펌프가 열을 실어 나름",
  "steady": "안정",
  "steady, with no pumps": "펌프 없이 안정",
  "steady: natural circulation carries the heat away": "안정: 자연 순환이 열을 실어 나름",
  "steady: the pumps carry the heat away": "안정: 펌프가 열을 실어 나름",
  "temperature climbing": "온도 상승 중",
  "temperature climbing: the heat has nowhere to go": "온도 상승 중: 열이 갈 곳이 없음",
  "too hot: cooling must be restored": "너무 뜨거움: 냉각을 복구해야 함",
  "too hot: the water would start to boil away; cooling must be restored": "너무 뜨거움: 물이 끓어 없어지기 시작함, 냉각을 복구해야 함",
  "boiling": "끓음",
  "the water starts to boil": "물이 끓기 시작함",
  "the splitting dies away in about a minute": "분열은 약 1분이면 잦아듦",
  "the splitting dies away within about a minute": "분열은 약 1분 안에 잦아듦",
  "the decay heat stays and fades slowly": "붕괴열은 남아 천천히 줄어듦",
  "the decay heat stays, and fades only slowly": "붕괴열은 남아 아주 천천히 줄어듦",
  "full power": "전출력",
  "running at full power": "전출력 운전 중",
  "total heat: {a} % of full power": "전체 열: 전출력의 {a} %",
  "{a} after shutdown · heat {b} % of full power": "정지 후 {a} · 열은 전출력의 {b} %",
  "{a} after shutdown: {b} % of full power": "정지 후 {a}: 전출력의 {b} %",
  "{a} after the rods dropped": "제어봉 낙하 후 {a}",
  "{#} min": "{#}분",
  "{#} hour": "{#}시간",
  "{#} day": "{#}일",
  "{#} week": "{#}주",
  "{#} year": "{#}년",
  "{a} s": "{a}초",
  "{a} min": "{a}분",
  "{a} hours": "{a}시간",
  "{a} days": "{a}일",
  "{a} months": "{a}개월",
});
