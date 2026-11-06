/* Korean: chains (붕괴 사슬과 평형) */
WT.L.ch.chains = {
  num: "강의 4", title: "붕괴 사슬과 평형", short: "붕괴 사슬",
  html: `
<div class="step">
  <h3>어미핵, 딸핵, 손녀핵</h3>
  <p>새로 생긴 원자핵도 불안정한 경우가 많습니다. 어미핵이 붕괴하여 딸핵이 되고, 딸핵은 다시 붕괴하여 안정한 손녀핵이 됩니다. 딸핵은 쌓였다가 사라지는데, 얼마나 높이 쌓이는지는 어미핵에 비해 얼마나 빨리 붕괴하는지에 달려 있습니다.</p>
  <div class="ctl"><label for="ch-t2">딸핵 반감기 (s)</label><input id="ch-t2" type="range" data-bind="T2" data-instant min="0.5" max="9" step="0.5" value="1.5"><output data-show="T2" data-fmt="1"></output></div>
  <div class="btns"><button class="btn ghost" data-act="refill">새 시료</button></div>
</div>
<div class="step">
  <h3>영년 평형: 라듐과 라돈</h3>
  <p>라듐-226은 1600년을 가지만, 그 딸핵인 라돈-222 기체는 3.8일뿐입니다. 밀봉한 병 속에서 라돈은 만들어지는 만큼 붕괴할 때까지 쌓입니다. <i>A</i><sub>Rn</sub> = <i>A</i><sub>Ra</sub>(1 − e<sup>−λt</sup>)이며, λ는 라돈의 붕괴 상수입니다. 몇 주가 지나면 둘은 같은 비율로 붕괴합니다.</p>
  <div class="btns"><button class="btn" data-act="vent">병 열기</button></div>
</div>
<div class="step">
  <h3>과도 평형: 테크네튬 카우</h3>
  <p>병원은 몰리브데넘-99(66시간)가 담긴 칼럼을 받는데, 이것이 가장 많이 쓰이는 의료용 추적자인 테크네튬-99m(6시간)을 계속 만들어 냅니다. 아침마다 테크네튬을 씻어 내면 다시 자라나며, 천천히 줄어드는 몰리브데넘을 따라갑니다.</p>
  <div class="btns"><button class="btn" data-act="milk">발생기에서 추출</button><button class="btn ghost" data-act="genre">새 발생기</button></div>
</div>
<div class="step">
  <h3>우라늄 사슬을 따라 내려가기</h3>
  <p>우라늄-238은 열네 단계를 거쳐 안정한 납이 됩니다. 이 도표에서 알파 붕괴는 아래로 두 칸, 왼쪽으로 두 칸, 베타 붕괴는 위로 한 칸, 왼쪽으로 한 칸 움직입니다. 오래되어 교란되지 않은 우라늄 광석에서는 모든 구성원이 같은 비율로 붕괴합니다.</p>
  <div class="btns"><button class="btn" data-act="next">다음 붕괴</button><button class="btn ghost" data-act="restart">처음부터</button></div>
</div>`,
};

Object.assign(WT.L.labels, {
  "Pb": "Pb",
  "Bi": "Bi",
  "Po": "Po",
  "At": "At",
  "Rn": "Rn",
  "Fr": "Fr",
  "Ra": "Ra",
  "Ac": "Ac",
  "Th": "Th",
  "Pa": "Pa",
  "U": "U",
  "parent ({#} s): {#}": "어미핵 ({#} s): {#}",
  "daughter ({#} s): {#}": "딸핵 ({#} s): {#}",
  "granddaughter (stable): {#}": "손녀핵 (안정): {#}",
  "parent {#}": "어미핵 {#}",
  "daughter {#}": "딸핵 {#}",
  "stable {#}": "안정 {#}",
  "daughter peaks: {#} %": "딸핵 최대: {#} %",
  "{#} s": "{#} s",
  "illustrative half-lives": "설명용 반감기",
  "radium{#}": "라듐{#}",
  "radon{#} gas": "라돈{#} 기체",
  "radium": "라듐",
  "radium activity": "라듐 방사능",
  "radon": "라돈",
  "radon activity": "라돈 방사능",
  "{#} d": "{#}일",
  "days →": "일 →",
  "day {#}: radon at {#} % of radium": "{#}일째: 라돈이 라듐의 {#} %",
  "A(Rn) = A(Ra) × ({#} − exp(−λt))": "A(Rn) = A(Ra) × ({#} − exp(−λt))",
  "A(radon) = A(radium) × ({#} − exp(−λt))": "A(라돈) = A(라듐) × ({#} − exp(−λt))",
  "Mo{#}": "Mo{#}",
  "molybdenum{#}": "몰리브데넘{#}",
  "Tc{#}m out": "Tc{#}m 추출",
  "Tc{#}m to the patient": "Tc{#}m을 환자에게",
  "dashed: never milked": "점선: 추출하지 않은 경우",
  "activity": "방사능",
  "{#} h since last milking · Tc{#}m at {#} % of Mo{#}": "마지막 추출 후 {#}시간 · Tc{#}m이 Mo{#}의 {#} %",
  "regrows to its peak in about {#} hours": "약 {#}시간 만에 최댓값까지 다시 자람",
  "neutrons →": "중성자 →",
  "protons ↑": "양성자 ↑",
  "grey: stable": "회색: 안정",
  "alpha: loses {#} protons and {#} neutrons": "알파: 양성자 {#}개와 중성자 {#}개를 잃음",
  "alpha: {#} p, {#} n": "알파: {#} p, {#} n",
  "beta: a neutron becomes a proton": "베타: 중성자가 양성자로 바뀜",
  "beta: n → p": "베타: n → p",
  "U{#} · half-life {#} billion yr · alpha next": "U{#} · 반감기 {#}십억 년 · 다음은 알파",
  "U{#} · half-life {#} yr · alpha next": "U{#} · 반감기 {#}년 · 다음은 알파",
  "Th{#} · half-life {#} days · beta next": "Th{#} · 반감기 {#}일 · 다음은 베타",
  "Th{#} · half-life {#} yr · alpha next": "Th{#} · 반감기 {#}년 · 다음은 알파",
  "Pa{#}m · half-life {#} min · beta next": "Pa{#}m · 반감기 {#}분 · 다음은 베타",
  "Ra{#} · half-life {#} yr · alpha next": "Ra{#} · 반감기 {#}년 · 다음은 알파",
  "Rn{#} · half-life {#} days · alpha next": "Rn{#} · 반감기 {#}일 · 다음은 알파",
  "Po{#} · half-life {#} min · alpha next": "Po{#} · 반감기 {#}분 · 다음은 알파",
  "Po{#} · half-life {#} µs · alpha next": "Po{#} · 반감기 {#} µs · 다음은 알파",
  "Po{#} · half-life {#} days · alpha next": "Po{#} · 반감기 {#}일 · 다음은 알파",
  "Pb{#} · half-life {#} min · beta next": "Pb{#} · 반감기 {#}분 · 다음은 베타",
  "Pb{#} · half-life {#} years · beta next": "Pb{#} · 반감기 {#}년 · 다음은 베타",
  "Bi{#} · half-life {#} min · beta next": "Bi{#} · 반감기 {#}분 · 다음은 베타",
  "Bi{#} · half-life {#} days · beta next": "Bi{#} · 반감기 {#}일 · 다음은 베타",
  "Pb{#}: stable, the chain ends": "Pb{#}: 안정, 사슬 끝",
  "step {#} of {#} · tap the nucleus": "{#}/{#}단계 · 원자핵을 누르세요",
});
