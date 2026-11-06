/* Korean: rays (알파, 베타, 감마, 중성자) */
WT.L.ch.rays = {
  num: "강의 2", title: "알파, 베타, 감마, 중성자", short: "방사선",
  html: `
<div class="step">
  <h3>네 가지 방사선</h3>
  <p><em class="a">알파</em>는 양성자 둘과 중성자 둘이 뭉친 무거운 덩어리입니다. <b>베타</b>는 빠른 전자입니다. <em class="g">감마</em>는 빛인데, 에너지가 너무 커서 눈에 보이지 않습니다. <em class="n">중성자</em>는 전하가 전혀 없습니다. 이들은 저마다 다른 것에 막힙니다.</p>
</div>
<div class="step">
  <h3>종이와 알루미늄</h3>
  <p>알파 입자는 크고 전하를 띠어 곧바로 원자들과 부딪칩니다. 그래서 종이 한 장이면 막힙니다. 베타 전자는 더 멀리 가지만, 몇 밀리미터의 알루미늄이면 역시 막힙니다.</p>
  <div class="btns"><button class="btn ghost" data-act="sh_paper" aria-pressed="true">종이</button><button class="btn ghost" data-act="sh_al" aria-pressed="false">알루미늄</button></div>
</div>
<div class="step">
  <h3>감마선: 절반씩 줄 뿐, 0은 없다</h3>
  <p>감마선은 전하가 없어 대개 원자 곁을 그냥 지나갑니다. 납 1센티미터마다 모든 감마선이 붙잡힐 확률은 똑같으므로, 한 겹마다 남은 양이 절반이 됩니다. 빔은 약해지지만 결코 완전히 0이 되지는 않습니다.</p>
  <div class="ctl"><label for="ry-pb">납 (cm)</label><input id="ry-pb" type="range" data-bind="pb" data-instant min="0" max="5" step="0.1" value="1"><output data-show="pb" data-fmt="1"></output></div>
</div>
<div class="step">
  <h3>중성자: 납으로는 부족하다</h3>
  <p>무거운 납 원자핵에 부딪힌 중성자는 볼링공에 맞은 탁구공과 같아서 속도를 그대로 유지합니다. 물속의 수소는 중성자와 무게가 같으므로 부딪힐 때마다 중성자가 느려지고, 결국 흡수될 만큼 느려집니다.</p>
  <div class="btns"><button class="btn ghost" data-act="nm_pb" aria-pressed="true">납</button><button class="btn ghost" data-act="nm_water" aria-pressed="false">물</button></div>
  <div class="ctl"><label for="ry-nx">두께 (cm)</label><input id="ry-nx" type="range" data-bind="nx" data-instant min="0" max="60" step="1" value="30"><output data-show="nx" data-fmt="0"></output></div>
</div>
<div class="step">
  <h3>차폐체 만들기</h3>
  <p>네 빔이 모두 멈출 때까지 층을 쌓아 보세요. 감마선은 정확히 0이 되지 않고, 아주 작은 몫으로 줄어들 뿐입니다.</p>
  <div class="btns"><button class="btn ghost" data-act="add_paper">+ 종이</button><button class="btn ghost" data-act="add_al">+ 알루미늄</button><button class="btn ghost" data-act="add_pb">+ 납</button><button class="btn ghost" data-act="add_water">+ 물</button><button class="btn" data-act="clear">비우기</button></div>
</div>`,
};

Object.assign(WT.L.labels, {
  "alpha": "알파",
  "beta": "베타",
  "gamma": "감마",
  "neutron": "중성자",
  "paper": "종이",
  "Al {#} mm": "Al {#} mm",
  "aluminium {#} mm": "알루미늄 {#} mm",
  "lead {#} cm": "납 {#} cm",
  "water {#} cm": "물 {#} cm",
  "no shield": "차폐 없음",
  "all four beams stopped": "네 빔 모두 멈춤",
  "all four stopped": "넷 모두 멈춤",
  "each source fires a steady beam": "각 선원이 일정한 빔을 쏩니다",
  "flash = stopped inside the shield": "번쩍임 = 차폐체 안에서 멈춤",
  "flash = stopped": "번쩍임 = 멈춤",
  "four beams": "네 빔",
  "not to scale": "축척 아님",
  "stopped": "멈춤",
  "all through": "모두 통과",
  "{#} % through": "{#} % 통과",
  "{#} in {#}": "{#}/{#}",
  "{#} in {#} million": "{#}/{#}백만",
  "{#} in a billion": "10억 분의 {#}",
  "drag ↔": "끌기 ↔",
  "gamma rays (caesium{#})": "감마선 (세슘{#})",
  "cm of lead": "납 두께 (cm)",
  "share still going": "아직 나아가는 몫",
  "gets through: {#} % · halved every {#} mm of lead": "통과: {#} % · 납 {#} mm마다 절반",
  "gets through: {#} in {#} · halved every {#} mm of lead": "통과: {#}/{#} · 납 {#} mm마다 절반",
  "gets through: {#} in {#} million · halved every {#} mm of lead": "통과: {#}/{#}백만 · 납 {#} mm마다 절반",
  "gets through: {#} in a billion · halved every {#} mm of lead": "통과: 10억 분의 {#} · 납 {#} mm마다 절반",
  "through: all · halved every {#} mm": "통과: 전부 · {#} mm마다 절반",
  "through: {#} % · halved every {#} mm": "통과: {#} % · {#} mm마다 절반",
  "through: {#} in {#} · halved every {#} mm": "통과: {#}/{#} · {#} mm마다 절반",
  "through: {#} in {#} million · halved every {#} mm": "통과: {#}/{#}백만 · {#} mm마다 절반",
  "through: {#} in a billion · halved every {#} mm": "통과: 10억 분의 {#} · {#} mm마다 절반",
  "counted: {#} of {#}": "셈: {#}/{#}",
  "got through {#} % · bounced back {#} % · slowed and caught {#} %": "통과 {#} % · 되튐 {#} % · 느려져 흡수 {#} %",
  "through {#} % · back {#} % · caught {#} %": "통과 {#} % · 되튐 {#} % · 흡수 {#} %",
  "bright = fast neutron · red = hydrogen nucleus knocked away · green flash = swallowed": "밝음 = 빠른 중성자 · 빨강 = 튕겨 나간 수소 원자핵 · 초록 번쩍임 = 흡수",
  "bright = fast · dim = slowed": "밝음 = 빠름 · 흐림 = 느려짐",
  "simplified model": "단순화한 모형",
});
