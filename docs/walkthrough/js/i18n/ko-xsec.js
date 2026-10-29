/* Korean: xsec (2장, 단면적) */
WT.L.ch.xsec = {
  num: "2장", title: "단면적이란 무엇인가", short: "단면적",
  html: `
<div class="step">
  <p>각 원반은 원자핵의 표적 넓이, 곧 <b>단면적</b>이며 σ(시그마)로 씁니다. 그림은 얇은 원자핵 판을 바로 위에서 내려다본 것이고, 중성자가 무작위 지점에 비처럼 쏟아집니다. 원반 안에 떨어진 중성자는 그 원자핵과 반응하고(주황색 섬광), 원반 사이에 떨어진 중성자는 그대로 지나갑니다(그냥 흐려집니다).</p>
  <p>그러므로 반응하는 몫은 단지 원반이 덮은 판의 몫입니다. 작은 검은 사각형은 넓이의 단위인 1 <b>반</b>(barn), 10⁻²⁴ cm²입니다. 실제 원자핵의 단면은 약 1 반입니다.</p>
  <div class="ctl"><label for="xs-e1">중성자 에너지 (eV)</label><input id="xs-e1" type="range" data-bind="lgE" data-instant min="-2.3" max="2" step="0.01" value="2"><output data-show="Eshow" data-fmt="2"></output></div>
</div>
<div class="step">
  <p>느린 중성자에게는 표적이 더 크게 보입니다. 원반은 원자핵의 실제 크기가 아니라, 이 에너지의 중성자에게 원자핵이 얼마나 크게 작용하는가입니다. 느린 중성자는 원자핵 곁에 더 오래 머물러 붙잡힐 가능성이 더 큽니다. 포획에서는 이 때문에 σ가 1/속력처럼 커집니다.</p>
  <p>판 아래의 곡선은 모든 에너지에 걸친 σ입니다(두 눈금 모두 로그). 주황색 점은 고른 에너지를 표시합니다. 가장 느린 중성자까지 끌어내리며 원반이 커지고 반응하는 몫이 오르는 것을 지켜보세요.</p>
  <div class="ctl"><label for="xs-e2">중성자 에너지 (eV)</label><input id="xs-e2" type="range" data-bind="lgE" data-instant min="-2.3" max="2" step="0.01" value="-1.6"><output data-show="Eshow" data-fmt="2"></output></div>
</div>
<div class="step">
  <p>공명에서는 표적이 부풀어 오릅니다. 7 eV에서는 중성자와 원자핵이 가진 에너지가 원자핵 자신의 준위 하나와 정확히 같아서 훨씬 쉽게 받아들여집니다. 원반의 넓이는 약 쉰 배로 커져 여기서는 약 400 반이 됩니다.</p>
  <p>7 eV에서 조금만 벗어나도 원반은 곧바로 줄어듭니다. 곡선의 봉우리가 좁기 때문입니다. 실제 원자핵에는 이런 봉우리가 많으며, 1장에서 그 바코드를 보았습니다.</p>
  <div class="ctl"><label for="xs-e3">중성자 에너지 (eV)</label><input id="xs-e3" type="range" data-bind="lgE" data-instant min="-2.3" max="2" step="0.005" value="0.845"><output data-show="Eshow" data-fmt="2"></output></div>
</div>`,
};
