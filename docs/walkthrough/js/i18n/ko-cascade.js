/* Korean: cascade (11장, 핵종 도표를 따라 내려가기) */
WT.L.ch.cascade = {
  num: "11장", title: "방출 캐스케이드", short: "캐스케이드",
  lead: "방출이 한 번으로 끝나는 일은 드뭅니다. 뒤에 남은 원자핵은 다시 방출할 만큼 뜨거운 경우가 많습니다.",
  html: `
<div class="step">
  <p>중성자 하나가 복합핵(왼쪽)을 떠났고, 그 뒤에 남은 <b>잔류핵</b>(오른쪽)은 아직 뜨겁습니다. 주황색 공이 에너지입니다. 잔류핵의 바닥 상태는 중성자를 끄집어내는 비용인 <b>분리 에너지</b> S<sub>n</sub>만큼 더 높은 곳에 있습니다.</p>
  <p>중성자가 떠날 때마다 공은 그 중성자의 운동 에너지만큼 떨어집니다. 공이 멈춘 곳이 잔류핵의 여분 에너지인 <b>들뜸</b>이며, 오른쪽 점들이 착지 횟수를 셉니다.</p>
  <div class="ctl"><label for="cs-e">중성자 에너지</label><input id="cs-e" type="range" data-bind="E" min="1" max="30" step="0.5" value="15"><output data-show="E" data-fmt="1"></output></div>
  <p>방출되는 중성자는 대개 느리므로 대부분의 낙하는 짧습니다. 파란 점은 점선으로 된 중성자 문턱보다 위에 있어 두 번째 중성자를 내보낼 여유가 있습니다. 이것이 (n,2n) 반응입니다. 약 11 MeV 아래에서는 하나도 그곳에 이르지 못합니다.</p>
</div>
<div class="step">
  <h3>도표를 가로지르는 연속 방출</h3>
  <p>흐름들은 <b>핵종 도표</b>의 한구석을 가로질러 걷는 반응들입니다. 핵종 도표는 원자핵을 중성자 수 N(가로)과 양성자 수 Z(세로)로 배치한 지도입니다. 각 반응은 테두리가 그려진 복합핵 칸에서 출발하며, 각 칸에는 그곳에서 끝나는 반응의 이름이 붙어 있습니다.</p>
  <p><em class="n">중성자</em>가 나가면 한 칸 왼쪽으로, <em class="p">양성자</em>가 나가면 한 칸 아래로, <em class="a">알파 입자</em>(양성자 둘, 중성자 둘)가 나가면 대각선으로 두 칸 움직입니다. 흐름의 폭은 그 걸음을 내딛는 양이고, 명암과 백분율은 반응이 끝나는 곳입니다.</p>
  <div class="ctl"><label for="cs-e4">중성자 에너지</label><input id="cs-e4" type="range" data-bind="E" min="1" max="30" step="0.5" value="14"><output data-show="E" data-fmt="1"></output></div>
  <div class="btns"><button class="btn" data-act="fire">반응 200회 발사</button></div>
  <p>에너지를 바꿔 보세요. 몇 MeV에서는 거의 모든 것이 표적 칸에서 멈추고, 에너지가 높을수록 흐름이 더 멀리 닿습니다. 한 걸음마다 분리 에너지 7~11 MeV가 들기 때문에, 30 MeV에서도 걸음은 많아야 서너 번입니다.</p>
</div>
<div class="step">
  <h3>개체수 장부 정리</h3>
  <p>엔진은 각 원자핵을 위에서 아래로, 한 번에 에너지 조각 하나, 즉 <b>구간</b> 하나씩 비웁니다. 오른쪽은 첫 방출의 잔류핵이고, 왼쪽은 중성자가 하나 적은 그 딸핵입니다. 주황색 공은 각 구간에서 기다리는 반응입니다. 여기서는 구간이 1 MeV이며, 엔진은 원자핵마다 사용 가능한 에너지에 맞춘 크기로 약 40개를 씁니다.</p>
  <p>표시기가 한 구간을 훑을 때 각 공은 9장의 경쟁에 따라 출구를 택합니다. <em class="g">광자</em>(γ)는 공을 더 낮은 구간으로 떨어뜨리고, <em class="n">중성자</em>는 딸핵으로 옮기며, 양성자나 알파는 그림 밖으로 데려갑니다. 모든 문턱 아래에서는 광자가 나머지를 바닥 상태(회색)로 실어 나릅니다. 그런 다음 딸핵을 훑습니다.</p>
  <div class="ctl"><label for="cs-e3">중성자 에너지</label><input id="cs-e3" type="range" data-bind="E" min="8" max="30" step="0.5" value="18"><output data-show="E" data-fmt="1"></output></div>
  <div class="btns"><button class="btn ghost" data-act="restart">처음부터</button></div>
  <p>광자는 아래로만 떨어지고 각 원자핵은 딸핵보다 먼저 처리가 끝나므로, 이미 비운 구간에 무언가 도착하는 일은 없습니다.</p>
</div>
<div class="step">
  <h3>배타적 반응 채널</h3>
  <p>반응을 한 번에 하나씩 재생합니다. 표시기가 도표 위를 뛰어다니고, 방출된 입자는 하나씩 쟁반에 떨어집니다. 각 채널은 실제로 일어나는 에너지에서 재생됩니다(그림 위쪽). (n,3n)은 여기서 중성자 세 개에 20 MeV 넘게 들기 때문에 25 MeV에서, 포획 (n,γ)는 1 MeV에서 재생합니다. 가득 찬 쟁반이 (n,2n) 같은 <b>배타적 채널</b>의 이름이 됩니다. 광자는 세지 않습니다. 엔진은 각 채널에 고유한 단면적(유효 표적 넓이로 나타낸 일어날 가능성)을 줍니다.</p>
  <div class="btns"><button class="btn ghost" data-act="next">다음 채널</button></div>
  <p>하나씩 넘겨 보세요. (n,np)는 중성자가 먼저인 경우와 양성자가 먼저인 경우로 두 번 재생됩니다. 같은 칸, 같은 쟁반이므로 하나의 채널입니다. 이어서 유령 중양성자(양성자와 중성자가 결합한 것)가 한 번에 그 칸에 도착합니다. 그 쟁반에는 d라고 적혀 있으므로 다른 채널인 (n,d)입니다.</p>
</div>
<div class="step">
  <h3>잔류핵 생성</h3>
  <p>이제 각 칸에는 선반이 있습니다. 먹색은 <b>바닥 상태</b>, 초록색(두 칸에 있음)은 별개의 생성물로 칠 만큼 오래 사는 들뜬 상태인 <b>핵이성질체</b>입니다. 더미의 높이는 <b>잔류핵 생성</b>, 즉 반응이 각 원자핵을 얼마나 만들어 냈는지입니다.</p>
  <div class="ctl"><label for="cs-e2">중성자 에너지</label><input id="cs-e2" type="range" data-bind="E" min="1" max="30" step="0.5" value="14"><output data-show="E" data-fmt="1"></output></div>
  <div class="btns"><button class="btn" data-act="fire">반응 200회 발사</button></div>
  <p>에너지를 바꿔 보세요. 다음 묶음이 그 값을 쓰고 이전 더미는 흐려집니다. 더 많은 입자가 떠날 수 있게 되면서 생성은 출발점에서 멀어집니다. 모든 내력은 어떤 선반 위에서 끝나며, 방사화 측정은 정확히 이 더미들을 봅니다. 시료에 방사선을 쬔 다음 각 생성물의 붕괴를 세는 것입니다.</p>
  <div class="aside">코드에서: <code>emission/multiple.py</code>(원자핵과 구간에 대한 반복, γ 캐스케이드), <code>emission/feeding.py</code>(사슬에 있는 모든 원자핵의 격자와 입력), <code>compound/continuum.py</code>(한 구간의 붕괴), <code>emission/channels.py</code>(배타적 채널, 잔류핵 생성, 핵이성질체 갈래), <code>emission/binary.py</code>(첫 방출의 장부 정리).</div>
</div>`,
};
Object.assign(WT.L.labels, {
  // reaction names on the squares (unchanged in Korean)
  "(n,γ)": "(n,γ)", "(n,n′)": "(n,n′)", "(n,{#}n)": "(n,{#}n)", "(n,p)": "(n,p)", "(n,np)": "(n,np)", "(n,{#}np)": "(n,{#}np)",
  "(n,{#}p)": "(n,{#}p)", "(n,n{#}p)": "(n,n{#}p)", "(n,α)": "(n,α)", "(n,nα)": "(n,nα)",
  "compound": "복합핵", "target": "표적",
  "N{#}": "N{#}", "N": "N", "N+{#}": "N+{#}", "Z": "Z", "Z{#}": "Z{#}",
  "neutron number →": "중성자 수 →",
  // scene 1
  "levels": "준위",
  "Sₙ {#} MeV": "Sₙ {#} MeV", "Sₙ = {#} MeV": "Sₙ = {#} MeV",
  "ground": "바닥",
  "residual": "잔류핵", "residual (one neutron fewer)": "잔류핵 (중성자 하나 적음)",
  "n threshold": "n 문턱", "its neutron threshold": "잔류핵의 중성자 문턱",
  "{#} MeV": "{#} MeV",
  "drop = neutron's kinetic energy": "낙하 = 중성자의 운동 에너지",
  "{#} % land above the threshold: a second neutron can leave": "{#}%가 문턱 위에 착지: 두 번째 중성자 방출 가능",
  "<{#} % land above the threshold: a second neutron can leave": "<{#}%가 문턱 위에 착지: 두 번째 중성자 방출 가능",
  "all land below the threshold: only photons remain": "모두 문턱 아래에 착지: 광자만 남음",
  "{#} % above threshold: (n,{#}n) possible": "문턱 위 {#}%: (n,{#}n) 가능",
  "<{#} % above threshold: (n,{#}n) possible": "문턱 위 <{#}%: (n,{#}n) 가능",
  "all below threshold: photons only": "모두 문턱 아래: 광자만",
  // scene 2
  "incoming neutron: {#} MeV": "입사 중성자: {#} MeV",
  "shade and % = where reactions end": "명암과 % = 반응이 끝나는 곳",
  "stream width = flow · shade and % = share of reactions that end in that nucleus": "흐름 폭 = 선속 · 명암과 % = 그 원자핵에서 끝나는 반응의 몫",
  // scene 3
  "residual (first step)": "잔류핵 (첫 걸음)",
  "daughter: n fewer": "딸핵: n 하나 적음", "daughter (one neutron fewer)": "딸핵 (중성자 하나 적음)",
  "now: {#}–{#} MeV": "현재: {#}–{#} MeV", "{#}–{#} MeV": "{#}–{#} MeV",
  "done: {#} left by proton or alpha, the rest sit on ground states": "완료: {#}개는 양성자나 알파로 떠나고 나머지는 바닥 상태에",
  "done: everything sits on a ground state": "완료: 모두 바닥 상태에 있음",
  "orange ball = reactions waiting in a bin · grey = settled on the ground state · pale bins = already emptied": "주황 공 = 구간에서 대기 중인 반응 · 회색 = 바닥 상태에 안착 · 옅은 구간 = 이미 비움",
  // scene 4
  "collected": "모은 입자",
  "tray: d": "쟁반: d",
  "a deuteron lands on the same square, but its tray reads d: channel (n,d)": "중양성자가 같은 칸에 도착하지만 쟁반은 d: 채널 (n,d)",
  "tray: n n  →  (n,{#}n)": "쟁반: n n  →  (n,{#}n)",
  "tray: n  →  (n,n′)": "쟁반: n  →  (n,n′)",
  "tray: p  →  (n,p)": "쟁반: p  →  (n,p)",
  "tray: n p  →  (n,np)": "쟁반: n p  →  (n,np)",
  "tray: n p  →  (n,np) · same square, same tray": "쟁반: n p  →  (n,np) · 같은 칸, 같은 쟁반",
  "tray: a  →  (n,α)": "쟁반: a  →  (n,α)",
  "tray: n n n  →  (n,{#}n)": "쟁반: n n n  →  (n,{#}n)",
  "tray empty, only photons: (n,γ), capture": "빈 쟁반, 광자만: (n,γ), 포획",
  "each emitted particle falls into the tray": "방출된 입자는 하나씩 쟁반에 떨어짐",
  "no particle gets out: only photons": "나가는 입자 없음: 광자만",
  "incoming neutron: {#} MeV · channel {#} of {#}": "입사 중성자: {#} MeV · 채널 {#}/{#}",
  // scene 5
  "isomer": "핵이성질체",
  "batch of {#} at {#} MeV": "{#}개 묶음, {#} MeV",
  "ink shelf: ground state · green: isomer": "먹색 선반: 바닥 상태 · 초록: 핵이성질체",
  "ink shelf: ground state · green shelf: isomer · pile height = how much of that nucleus was made": "먹색 선반: 바닥 상태 · 초록 선반: 핵이성질체 · 더미 높이 = 그 원자핵의 생성량",
});
