/* Korean: economy (중성자 경제) */
WT.L.ch.economy = {
  num: "강의 1", title: "중성자 경제", short: "중성자 경제",
  html: `
<div class="step">
  <h3>중성자 1000개</h3>
  <p>빠른 중성자 1000개를 한 세대 동안 따라가 봅니다. 몇 개는 추가 핵분열을 일으키고, 일부는 밖으로 새고, 일부는 도중에 포획되며, 나머지는 우라늄-235를 쪼개 다음 1000개를 만듭니다. 여섯 인자를 곱하면 <i>k</i> = <i>η f p ε P</i><sub>FNL</sub> <i>P</i><sub>TNL</sub>입니다.</p>
</div>
<div class="step">
  <h3>농축</h3>
  <p>연료에 우라늄-235가 많을수록 더 많은 중성자가 핵분열을 일으키는 곳에 흡수됩니다. 천연 우라늄(0.7 %)과 보통 물로는 <i>k</i>가 결코 1에 이르지 못합니다.</p>
  <div class="ctl"><label for="eco-e">우라늄-235 (%)</label><input id="eco-e" type="range" data-bind="enr" min="0.7" max="5" step="0.1" value="3"><output data-show="enr" data-fmt="1"></output></div>
</div>
<div class="step">
  <h3>연료봉 사이의 물</h3>
  <p>물이 너무 적으면 감속 중인 중성자가 우라늄-238에 포획되고, 너무 많으면 물 자체가 중성자를 흡수합니다. 가장 좋은 비율이 있으며, 경수로는 그보다 조금 낮게 설계됩니다.</p>
  <div class="ctl"><label for="eco-m">연료 대비 물 (× 표준)</label><input id="eco-m" type="range" data-bind="m" min="0.3" max="4" step="0.05" value="1"><output data-show="m" data-fmt="2"></output></div>
</div>
<div class="step">
  <h3>크기</h3>
  <p>표면 가까이에서 태어난 중성자는 빠져나갈 수 있습니다. 작은 노심은 너무 많이 새고, 큰 노심은 붙잡아 둡니다. <i>k</i>가 1을 넘는 크기를 찾아보세요.</p>
  <div class="ctl"><label for="eco-s">노심 크기 (× 표준)</label><input id="eco-s" type="range" data-bind="s" min="0.3" max="2" step="0.05" value="0.6"><output data-show="s" data-fmt="2"></output></div>
</div>`,
};

Object.assign(WT.L.labels, {
  "fast fission": "고속 핵분열",
  "fast leak": "고속 누설",
  "leaks out, fast": "빠른 채로 누설",
  "U{#} catches": "U{#} 포획",
  "caught by U{#}": "U{#}에 포획",
  "slow leak": "열중성자 누설",
  "leaks out, slow": "느려진 뒤 누설",
  "water, steel…": "물, 강철…",
  "water, steel, boron": "물, 강철, 붕소",
  "P fast {#}": "P 고속 {#}",
  "P slow {#}": "P 열 {#}",
  "p {#}": "p {#}",
  "f {#}": "f {#}",
  "U{#}": "U{#}",
  "slowing": "감속",
  "slowing down": "감속 중",
  "{#} split U{#}": "{#}개가 U{#}를 쪼갬",
  "next: {#}": "다음: {#}",
  "next generation: {#}": "다음 세대: {#}",
  "k = {#}": "k = {#}",
  "critical: steady": "임계: 일정",
  "grows": "증가",
  "dies away": "잦아듦",
  "best ≈ {#}×": "최적 ≈ {#}×",
  "less water": "물 적게",
  "more water": "물 많이",
  "{#} % leak out": "{#} % 누설",
  "k = η {#} × f {#} × p {#} × ε {#} × P {#} × P {#}": "k = η {#} × f {#} × p {#} × ε {#} × P {#} × P {#}",
  "textbook set (D&H); trends illustrative": "교과서 값 (D&H), 경향은 설명용",
  "factors: textbook set (Duderstadt & Hamilton) at {#} %; slider trends illustrative": "인자: {#} %에서의 교과서 값 (Duderstadt & Hamilton), 슬라이더 경향은 설명용",
});
