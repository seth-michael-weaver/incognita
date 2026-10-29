/* Korean: critical (21장, 임계) */
WT.L.ch.critical = {
  num: "21장", title: "임계와 원자로 제어", short: "임계",
  html: `
<div class="step">
  <h3>증배 인자</h3>
  <p>핵분열은 한 번에 몇 개의 중성자를 풀어놓고, 그 가운데 일부는 다음 핵분열을 일으키며 나머지는 사라집니다. <b>증배 인자</b> <i>k</i>는 핵분열 한 번이 새로운 핵분열 몇 번으로 이어지는가입니다. 세대마다 중성자가 <i>k</i>배가 됩니다. 1보다 크면 연쇄 반응이 커지고, 1보다 작으면 잦아듭니다.</p>
  <div class="ctl"><label for="cri-k">증배 k</label><input id="cri-k" type="range" data-bind="k" data-instant min="0.95" max="1.05" step="0.05" value="1.05"><output data-show="k" data-fmt="2"></output></div>
</div>
<div class="step">
  <h3>지연 중성자</h3>
  <p>중성자의 작은 몫(0.65%)은 먼저 붕괴하는 핵분열 조각에서 나와 몇 초 늦게 도착합니다. 이 늦은 중성자들이 속도를 정하므로 증가는 눈 깜짝할 사이에서 몇 분으로 느려집니다. 그래프는 10배 빠르게 재생됩니다.</p>
  <div class="ctl"><label for="cri-k2">증배 k</label><input id="cri-k2" type="range" data-bind="kd" data-instant min="0.998" max="1.002" step="0.0005" value="1.001"><output data-show="kd" data-fmt="4"></output></div>
  <div class="btns"><button class="btn ghost" data-act="delayed" aria-pressed="true">지연 중성자</button></div>
</div>
<div class="step">
  <h3>임계</h3>
  <p>임계 실험입니다. 출력이 일정하게 유지될 때까지 제어봉을 움직입니다. 그 설정에서 <i>k</i>는 정확히 1이고, 그 제어봉 위치가 곧 측정값입니다. 찾아 보세요. 표시창에 <i>k</i>가 소수점 다섯 자리까지 나옵니다.</p>
  <div class="ctl"><label for="cri-rod">제어봉 삽입 (%)</label><input id="cri-rod" type="range" data-bind="ins" data-instant min="35" max="75" step="1" value="45"><output data-show="ins" data-fmt="0"></output></div>
</div>`,
};
/* attributes referenced in the English chapter script (for the structure check): data-act="delayed" data-act="delayed" */
