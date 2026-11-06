/* Korean: xenon (제논 독작용) */
WT.L.ch.xenon = {
  num: "강의 1", title: "제논 독작용", short: "제논",
  html: `
<div class="step">
  <h3>핵분열이 만드는 독</h3>
  <p>핵분열의 약 6.6 %는 아이오딘-135를 거쳐 제논-135가 됩니다. 제논-135는 알려진 것 가운데 가장 강한 중성자 흡수체입니다. 약 이틀 동안 쌓이다가, 중성자가 태우고 붕괴가 없애는 속도가 생기는 속도와 같아지면 멈춥니다. 출력이 높으면 더 빨리 태우기도 하므로 농도는 포화됩니다.</p>
  <div class="ctl"><label for="xe-p1">출력 (%)</label><input id="xe-p1" type="range" data-bind="P" data-instant min="10" max="100" step="5" value="100"><output data-show="P" data-fmt="0"></output></div>
</div>
<div class="step">
  <h3>제논 구덩이</h3>
  <p>정지하면 태우는 일은 멈추지만, 이미 만들어진 아이오딘은 계속 제논으로 바뀝니다. 독은 약 9시간 뒤 최대가 되어 제어봉이 되돌려 줄 수 있는 양보다 많아지므로, 원자로는 재가동할 수 없습니다. 독은 2~3일에 걸쳐 사라집니다.</p>
  <div class="ctl"><label for="xe-th">정지 후 경과 시간 (h)</label><input id="xe-th" type="range" data-bind="th" data-instant min="0" max="72" step="0.5" value="9"><output data-show="th" data-fmt="1"></output></div>
</div>
<div class="step">
  <h3>정지와 재가동</h3>
  <p>이제 실시간으로, 1초에 3시간씩 흘러갑니다. 정지한 뒤 재가동해 보세요. 구덩이 안에서는 거부되고, 나중에는 중성자가 제논을 태워 없앱니다. 출력만 바꿔도 제논이 몇 시간 동안 출렁입니다.</p>
  <div class="ctl"><label for="xe-p3">출력 (%)</label><input id="xe-p3" type="range" data-bind="P" data-instant min="10" max="100" step="5" value="100"><output data-show="P" data-fmt="0"></output></div>
  <div class="btns"><button class="btn" data-act="xeshut">정지</button><button class="btn ghost" data-act="xerestart">재가동</button></div>
</div>
<div class="step">
  <h3>제논 진동</h3>
  <p>큰 노심에서는 양쪽이 느슨하게만 연결되어 있습니다. 한쪽에 제어봉을 밀어 넣으면 그쪽은 선속이 줄어 제논을 덜 태우므로, 출력이 건너편으로 옮겨 갔다가 다시 돌아옵니다. 대략 하루에 한 번입니다. 더 큰 노심에서는 운전원이 감쇠시키지 않으면 진동이 커집니다.</p>
  <div class="ctl"><label for="xe-wd">노심 크기 (m)</label><input id="xe-wd" type="range" data-bind="wd" data-instant min="1.5" max="3.5" step="0.1" value="3"><output data-show="wd" data-fmt="1"></output></div>
  <div class="btns"><button class="btn" data-act="xepush">왼쪽에 제어봉 밀어 넣기</button></div>
</div>`,
};

Object.assign(WT.L.labels, {
  "drag": "끌기",
  "equilibrium {#} %": "평형 {#} %",
  "fission → iodine{#} ({#} h) → xenon{#} ({#} h) → Cs{#}": "핵분열 → 아이오딘{#} ({#} h) → 제논{#} ({#} h) → Cs{#}",
  "fission → iodine{#} ({#} h) → xenon{#} ({#} h) → Cs{#}  ·  Xe{#} swallows neutrons: {#} million barns": "핵분열 → 아이오딘{#} ({#} h) → 제논{#} ({#} h) → Cs{#}  ·  Xe{#}의 중성자 흡수: {#}백만 반",
  "illustration": "예시 그림",
  "left {#} %": "왼쪽 {#} %",
  "more power left": "왼쪽 출력 증가",
  "more power right": "오른쪽 출력 증가",
  "no restart": "재가동 불가",
  "peak {#} % at {#} h": "최대 {#} % ({#} h)",
  "power": "출력",
  "refused: more xenon than spare reactivity": "거부됨: 제논이 여유 반응도보다 많음",
  "restarted": "재가동됨",
  "right {#} %": "오른쪽 {#} %",
  "running at {#} % · xenon {#} %": "{#} %로 운전 중 · 제논 {#} %",
  "shut down": "정지",
  "shut down · in the pit · xenon {#} %": "정지 · 구덩이 안 · 제논 {#} %",
  "shut down · restart possible · xenon {#} %": "정지 · 재가동 가능 · 제논 {#} %",
  "shut down · in the pit": "정지 · 구덩이 안",
  "shut down · restart possible": "정지 · 재가동 가능",
  "shutdown": "정지",
  "spare reactivity": "여유 반응도",
  "spare reactivity the rods can give": "제어봉이 줄 수 있는 여유 반응도",
  "swing period {#} h · {#} m core: the swing dies away": "진동 주기 {#} h · {#} m 노심: 진동이 잦아듦",
  "swing period {#} h · {#} m core: the swing dies away slowly": "진동 주기 {#} h · {#} m 노심: 진동이 천천히 잦아듦",
  "swing period {#} h · {#} m core: the swing grows": "진동 주기 {#} h · {#} m 노심: 진동이 커짐",
  "tap a side to push rods in": "한쪽을 눌러 제어봉 삽입",
  "tap the core to restart": "노심을 눌러 재가동",
  "tap the core to shut down": "노심을 눌러 정지",
  "too poisoned to restart": "독이 너무 많아 재가동 불가",
  "xenon worth (% of k)": "제논 반응도 가치 (k의 %)",
  "xenon{#} + n → Xe{#}: {#} million barns": "제논{#} + n → Xe{#}: {#}백만 반",
  "{#} % power · {#} h after start-up · xenon {#} %": "출력 {#} % · 기동 후 {#} h · 제논 {#} %",
  "{#} h": "{#}시간",
  "{#} h after shutdown · xenon {#} % · cannot restart": "정지 후 {#} h · 제논 {#} % · 재가동 불가",
  "{#} h after shutdown · xenon {#} % · restart possible": "정지 후 {#} h · 제논 {#} % · 재가동 가능",
  "{#} m core: push the rods to start a swing": "{#} m 노심: 제어봉을 밀어 진동을 일으키세요",
});
