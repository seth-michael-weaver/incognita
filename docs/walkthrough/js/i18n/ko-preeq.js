/* Korean: preeq (7장, 전평형) */
WT.L.ch.preeq = {
  num: "7장", title: "전평형 방출", short: "전평형",
  lead: "원자핵에 들어온 중성자는 자기 에너지를 한꺼번에 모두와 나누지 않습니다. 처음 몇 번의 충돌 동안에는 입자 하나가 에너지 대부분을 가지고 있고, 그 입자가 곧바로 튀어 나갈 수 있습니다. 이것이 전평형, 즉 “에너지가 고르게 퍼지기 전”의 방출입니다.",
  html: `
<div class="step">
  <p>우물이 두 개 있습니다. 하나는 <em class="p">양성자</em>용, 하나는 <em class="n">중성자</em>용입니다. 공 하나하나는 에너지 준위에 있는 핵자이며, 준위는 사다리의 가로대로 그려져 있습니다. 가로대는 아래에서부터 <b>페르미 면</b>까지 채워져 있습니다. 점선 “자유” 선보다 위에 있는 핵자는 탈출할 만큼의 에너지를 가집니다. 엔진은 양성자와 중성자를 따로 추적합니다.</p>
  <p>들어온 중성자는 위쪽에 떠 있으며 모든 에너지를 쥐고 있습니다. 자기 운동 에너지에 더해, 포획되면서 방출된 몇 MeV(백만 전자볼트)입니다.</p>
</div>
<div class="step">
  <h3>입자–구멍 들뜸</h3>
  <p>빠른 중성자가 바다 속의 핵자와 부딪혀 자기 에너지의 일부를 넘겨 줍니다. 그 핵자는 빈 가로대로 뛰어오르고, 떠난 자리는 비어 <b>구멍</b>(속이 빈 고리)이 됩니다. 그래서 부딪힐 때마다 <b>한 쌍</b>이 생깁니다. 들어 올려진 핵자 하나와 구멍 하나입니다. 물리학자들은 들어 올려진 핵자와 구멍을 함께 세어 <b>엑시톤</b>이라고 부릅니다. 첫 번째 충돌 뒤에는 3개(들어 올려진 핵자 2개, 구멍 1개)입니다.</p>
  <div class="btns"><button class="btn" data-act="collide">충돌</button><button class="btn ghost" data-act="reset">처음부터</button></div>
  <p>충돌 버튼을 눌러 한 번의 충돌을 지켜보세요. 뛰어드는 모습, 뛰어오르는 모습, 그리고 구멍입니다. 몇 번 반복해 보세요. 맞는 쪽은 양성자일 수도 중성자일 수도 있습니다. 충돌할 때마다 에너지를 더 많은 핵자가 나눠 가지므로, 들어 올려진 핵자는 저마다 더 낮은 곳에 놓이고, 빠른 입자가 탈출할 가능성은 점점 줄어듭니다.</p>
</div>
<div class="step">
  <h3>방출과 추가 충돌</h3>
  <p>각 단계에서 맨 위 중성자는 탈출하거나(위쪽 화살표, 자유 선보다 위에 있을 때만) 다시 충돌합니다(아래쪽 화살표). 굵기는 확률을 나타냅니다. 탈출 속도는 역과정에서 읽어 냅니다. 어떤 에너지의 중성자를 쉽게 삼키는 원자핵은 같은 에너지의 중성자를 쉽게 내보내기도 합니다. 얼마나 쉽게 삼키는지는 5장에서 이미 계산했습니다(이 양방향 규칙을 <b>세부 균형</b>이라고 합니다). 충돌 속도는 두 핵자가 얼마나 세게 부딪히는지에, 충돌 뒤 에너지를 나눌 수 있는 새로운 방법이 몇 가지인지를 곱한 것입니다.</p>
  <div class="ctl"><label for="pe-n">단계 (엑시톤 수 n)</label><input id="pe-n" type="range" data-bind="n" min="3" max="11" step="2" value="3" data-instant><output data-show="n" data-fmt="0"></output></div>
  <p>단계를 올려 보세요. 초기에는 입자 하나가 에너지 대부분을 쥐고 있으므로 탈출하는 입자가 빠릅니다. 나중에는 에너지가 얇게 퍼져서 빠져나가는 것이 거의 없습니다.</p>
</div>
<div class="step">
  <h3>전평형 스펙트럼</h3>
  <p>오른쪽 더미는 <b>스펙트럼</b>입니다. 각 에너지에서 중성자가 몇 개 나오는지를 보여 주며, 왼쪽이 느린 것, 오른쪽이 빠른 것입니다. 각 반응은 맨 위 중성자가 탈출할 때까지 사슬을 따라 진행되고, 색은 언제 나왔는지를 알려 줍니다. 3단계는 <em style="font-style:normal;color:var(--warm);font-weight:600">진한 주황</em>, 그 뒤로 갈수록 옅어지며, 원자핵이 잠잠해진 뒤에야 나왔다면(8장) <em class="n">파랑</em>입니다.</p>
  <div class="btns"><button class="btn" data-act="run">반응 300회 실행</button></div>
  <p>3단계는 최대 에너지 가까이까지 뻗는 넓고 낮은 둥근 언덕을 만들며, 그렇게 멀리까지 닿는 것은 이 단계뿐입니다. 이후 단계들은 더 낮은 곳에 쌓입니다. 파란 언덕은 <b>증발</b>입니다. 모두가 에너지를 나눠 가지면, 뜨거운 액체에서 김이 나오듯 느린 중성자만 조금씩 새어 나옵니다.</p>
  <div class="ctl"><label for="pe-e">중성자 에너지</label><input id="pe-e" type="range" data-bind="E" min="5" max="60" step="0.5" value="20"><output data-show="E" data-fmt="1"></output></div>
  <p>들어오는 중성자의 에너지를 바꿔 보세요. 새로 한 묶음이 실행되고 둥근 언덕이 더 멀리 뻗습니다. 증발만으로는 결코 빠른 중성자가 나오지 않습니다.</p>
</div>
<div class="step">
  <h3>입자–구멍 상태 밀도</h3>
  <p>계수기는 입자를 빈 가로대에, 구멍을 채워진 가로대에 놓아 그 에너지들의 합이 나눌 에너지와 같아지는 모든 방법을 하나하나 셉니다(여기서 가로대 간격은 1 MeV입니다). 핵자는 페르미온이므로 두 개가 한 가로대를 함께 쓸 수 없습니다. 따라서 입자는 빈 가로대에만 놓이고, 구멍은 핵자가 있던 자리에만 생깁니다. 이것이 <b>파울리 차단</b>입니다.</p>
  <div class="ctl"><label for="pe-u">나눌 에너지 (MeV)</label><input id="pe-u" type="range" data-bind="U" min="2" max="16" step="1" value="8" data-instant><output data-show="U" data-fmt="0"></output></div>
  <div class="btns"><button class="btn" data-act="addpair">한 쌍 추가</button><button class="btn ghost" data-act="droppair">한 쌍 제거</button></div>
  <p>한 쌍을 더하면 수가 껑충 뛰고, 에너지를 올리면 대략 <i>E</i><sup>n−1</sup>처럼 증가합니다. 이 수, 즉 <b>입자–구멍 상태 밀도</b>가 충돌률을 정합니다. 배치가 많을수록 충돌이 이어질 곳이 많아집니다. 엔진은 가로대 간격이 MeV의 몇 분의 일인 실제 사다리에서 세며, 높은 에너지에서 보이는 한계 하나를 더합니다. 구멍은 우물 바닥보다 아래에 있을 수 없습니다.</p>
</div>
<div class="step">
  <h3>덩어리 방출</h3>
  <p>작은 덩어리도 일찍 떠날 수 있습니다. <b>픽업</b>에서는 나가던 양성자가 표면의 중성자를 붙잡아 함께 <em class="n">중양성자</em>로 떠납니다. 둘을 붙잡으면 삼중양성자나 헬륨-3이 됩니다. <b>녹아웃</b>에서는 들어온 중성자가 표면 근처에 이미 만들어져 있던 <em class="a">알파 입자</em>(양성자 둘과 중성자 둘)를 쳐서 밖으로 내보냅니다. 엔진은 두 과정 모두 칼바흐(Kalbach)의 공식을 씁니다.</p>
  <div class="btns"><button class="btn ghost" data-act="pickup">중성자 픽업 → d</button><button class="btn ghost" data-act="knock">α 녹아웃</button></div>
  <p>버튼을 눌러 하나씩 지켜보세요. 두 과정 모두 중양성자와 알파 입자에 각자의 빠른 꼬리를 만들어 주며, 그 꼬리는 각 입자를 끄집어내는 데 드는 에너지 바로 위에서 시작합니다.</p>
</div>
<div class="step">
  <h3>다중 전평형 방출</h3>
  <p>높은 에너지에서는 첫 번째 충돌이 맞은 핵자에게도 많은 에너지를 줄 수 있습니다. 빠른 중성자가 떠날 때, 그 두 번째 핵자가 탈출에 필요한 8 MeV(자유 선)보다 여전히 더 많은 에너지를 가지고 있을 수 있고, 그러면 그것도 함께 날아갑니다. 한 번의 반응에서 빠른 입자가 둘 나오는 것입니다. 그림은 반응을 하나씩 다시 보여 주며 매 순간 무슨 일이 일어나는지 말해 줍니다. 각 공 옆의 숫자는 그 공의 에너지입니다.</p>
  <div class="ctl"><label for="pe-e2">중성자 에너지</label><input id="pe-e2" type="range" data-bind="E" min="5" max="80" step="0.5" value="40"><output data-show="E" data-fmt="1"></output></div>
  <p>에너지를 바꿔 보세요. 약 20 MeV 아래에서는 두 번째 핵자가 선을 넘는 일이 드뭅니다. 그 위에서는 점점 더 많은 반응이 빠른 입자 두 개를 내보냅니다. 이것이 <b>다중 전평형</b>이며, 엔진은 20 MeV 이상에서 이를 포함합니다. 떠나지 않은 것은 모두 다음 장의 복합핵이 됩니다. 몇 MeV(사용 중인 표적의 가장 높은 불연속 준위) 아래에서는 엔진이 사슬 전체를 건너뜁니다.</p>
  <div class="aside">코드에서: <code>preeq/exciton.py</code>(2성분 엑시톤 사슬, 충돌률과 탈출률), <code>density/particle_hole.py</code>(파울리 보정과 유한 우물 보정을 넣은 입자–구멍 상태 밀도), <code>preeq/complex.py</code>(칼바흐 픽업, 스트리핑, α 녹아웃), <code>preeq/multi.py</code>(다중 전평형), <code>compound/normalization.py</code>(복합핵으로 넘기기).</div>
</div>`,
};
Object.assign(WT.L.labels, {
  // wells
  "protons": "양성자",
  "neutrons": "중성자",
  "Fermi": "페르미",
  "Fermi surface": "페르미 면",
  "free": "자유",
  "free: can escape": "자유: 탈출 가능",
  "all the energy in one nucleon": "모든 에너지가 핵자 하나에",
  "{#} particle, {#} holes": "입자 {#}, 구멍 {#}",
  // pairs
  "{#} particle, {#} holes: n = {#}": "입자 {#}, 구멍 {#}: n = {#}",
  "{#} particle, {#} hole: n = {#}": "입자 {#}, 구멍 {#}: n = {#}",
  "{#} particles, {#} hole: n = {#}": "입자 {#}, 구멍 {#}: n = {#}",
  "{#} particles, {#} holes: n = {#}": "입자 {#}, 구멍 {#}: n = {#}",
  "protons: {#} lifted, {#} hole": "양성자: {#}개 올라감, 구멍 {#}",
  "protons: {#} lifted, {#} holes": "양성자: {#}개 올라감, 구멍 {#}",
  "neutrons: {#} lifted, {#} hole": "중성자: {#}개 올라감, 구멍 {#}",
  "neutrons: {#} lifted, {#} holes": "중성자: {#}개 올라감, 구멍 {#}",
  "chain ends: the rest becomes a compound nucleus": "사슬 끝: 나머지는 복합핵이 됨",
  // fork
  "about {#} MeV above surface": "페르미 면 위 약 {#} MeV",
  "escapes  {#}%": "탈출  {#}%",
  "collides again  {#}%": "재충돌  {#}%",
  "below the free line: it cannot leave": "자유 선 아래: 떠날 수 없음",
  "n = {#}: {#} particles, {#} hole, {#} MeV": "n = {#}: 입자 {#}, 구멍 {#}, {#} MeV",
  "n = {#}: {#} particles, {#} holes, {#} MeV": "n = {#}: 입자 {#}, 구멍 {#}, {#} MeV",
  "stage n = {#}: {#} particles and {#} hole share {#} MeV": "n = {#} 단계: 입자 {#}와 구멍 {#}이 {#} MeV를 나눔",
  "stage n = {#}: {#} particles and {#} holes share {#} MeV": "n = {#} 단계: 입자 {#}와 구멍 {#}이 {#} MeV를 나눔",
  // tail
  "max {#} MeV": "최대 {#} MeV",
  "slow": "느림",
  "fast →": "빠름 →",
  "stage {#}": "{#}단계",
  "chain over: compound": "사슬 끝: 복합핵",
  "left at:": "방출 시점:",
  "neutron left at:": "중성자 방출 시점:",
  "evaporation": "증발",
  "{#} of {#} landed · {#} left during the chain": "도착 {#} / {#} · 사슬 중 방출 {#}",
  // pauli
  "well bottom: no deeper hole": "우물 바닥: 더 깊은 구멍 없음",
  "bottom of the well": "우물 바닥",
  "{#} MeV to share": "나눌 에너지 {#} MeV",
  "{#} particles · {#} hole": "입자 {#} · 구멍 {#}",
  "{#} particles · {#} holes": "입자 {#} · 구멍 {#}",
  "ways, all counted": "가지, 모두 셈",
  "arrangements so far": "지금까지의 배치",
  "one more pair: {#} ways": "한 쌍 더: {#}가지",
  "never two on one rung · holes only where a nucleon was": "한 가로대에 둘은 불가 · 구멍은 핵자가 있던 자리에만",
  "(first {#} shown as ticks)": "(처음 {#}개를 눈금으로 표시)",
  // cluster
  "a deuteron leaves": "중양성자가 떠남",
  "grabs a neutron at the edge": "가장자리의 중성자를 붙잡음",
  "a fast proton heads out": "빠른 양성자가 나감",
  "an α ({#} protons + {#} neutrons) waits at the edge": "가장자리에서 기다리는 α (양성자 {#} + 중성자 {#})",
  "knocked straight out": "곧장 튕겨 나감",
  // second
  "first fast neutron": "첫 번째 빠른 중성자",
  "second fast proton": "두 번째 빠른 양성자",
  "second fast neutron": "두 번째 빠른 중성자",
  "below the free line: stays": "자유 선 아래: 남음",
  "below the free line: it stays": "자유 선 아래: 남음",
  "the rest settles: compound nucleus": "나머지는 잠잠해짐: 복합핵",
  "{#} MeV carried in": "들여온 에너지 {#} MeV",
  "second fast particle in {#} of the last {#} reactions": "두 번째 빠른 입자: {#}회 (최근 반응 {#}회 중)",
});

// canvas labels added 2026-10-29 (I18NLABELS_B)
Object.assign(WT.L.labels, {
  "bump {#}: a proton in the sea was hit, jumped up, and left a hole": "충돌 {#}: 바다의 양성자가 맞아 튀어 오르고 구멍을 남김",
  "bump!": "쾅!",
  "hole": "구멍",
  "lifted": "들어 올려짐",
  "free line: more than {#} MeV needed to get out": "자유선: 빠져나가려면 {#} MeV 넘게 필요",
  "a fast neutron comes in with {#} MeV": "빠른 중성자가 {#} MeV로 들어옴",
  "bump: it hits a neutron in the sea, which jumps up and leaves a hole": "충돌: 바다의 중성자를 때리고, 그 중성자가 튀어 올라 구멍을 남김",
  "neutron: {#} MeV": "중성자: {#} MeV",
});
