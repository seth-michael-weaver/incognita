/* Korean: slowing (19장, 감속) */
WT.L.ch.slowing = {
  num: "19장", title: "중성자 감속", short: "감속",
  html: `
<div class="step">
  <p>수소에 한 번 튕길 때마다 에너지의 절반쯤을 잃습니다. 핵분열 중성자는 2 MeV에서 시작하여 물속에서 튕깁니다. 수소 원자핵은 중성자와 질량이 같으므로, 당구공처럼 한 번 튕길 때마다 평균적으로 중성자 에너지의 절반을 넘겨 받습니다.</p>
  <p>차트는 튕길 때마다의 중성자 에너지를 그립니다. 옆으로 눈금 하나는 에너지가 천 배 줄었다는 뜻입니다. 매번 같은 몫을 잃으므로 점선처럼 곧은 미끄럼이 됩니다. 약 18번 튕기면 중성자는 <b>열</b> 에너지인 0.025 eV에 이르며, 거기서는 따뜻한 물이 중성자를 느리게 하는 만큼 자주 끌어올리기도 합니다. 산소는 16배 무거워서 한 번에 조금만 가져가고, 백 번이 넘게 필요합니다.</p>
  <div class="btns"><button class="btn ghost" data-act="tgtH" aria-pressed="true">수소</button><button class="btn ghost" data-act="tgtO" aria-pressed="false">산소</button><button class="btn" data-act="again">다시 발사</button></div>
</div>
<div class="step">
  <p>약 1 eV 아래에서는 분자의 결합이 튕김의 모양을 정합니다. 수소는 저마다 산소에 묶여 있습니다(밝은 선). 느린 중성자는 더 이상 자유로운 수소를 때리지 않고 18배 무거운 분자 전체를 때리므로, 단순한 튕김은 거의 아무것도 가져가지 못합니다.</p>
  <p>분자를 흔들거나 떨게 할 수도 있지만, 0.06, 0.2, 0.45 eV처럼 정해진 양씩만 넘겨 줄 수 있습니다(밝은 섬광). 따뜻한 분자는 가끔 그런 양을 되돌려 주기도 합니다. 차트에서 1 eV 아래의 음영 띠가 이것이 중요해지는 곳입니다. 결합을 꺼서 자유 수소와 비교해 보세요.</p>
  <div class="btns"><button class="btn ghost" data-act="bind" aria-pressed="true">화학 결합</button><button class="btn" data-act="again">다시 발사</button></div>
</div>
<div class="step">
  <p>컴퓨터 코드에는 이 모든 것이 표로 필요합니다. <b>산란 법칙</b>, 곧 지도입니다. 가로축은 충돌이 얼마나 센가, 곧 α(분자에게 넘겨 준 충격으로, 스치면 작고 정면으로 맞으면 큽니다)입니다. 세로축은 중성자가 얻는(위) 또는 잃는(아래) 에너지 β로, 물의 열 에너지 0.025 eV 단위로 셉니다. 밝으면 가능성이 크고 옅으면 드뭅니다.</p>
  <p>윤곽선은 고른 에너지의 중성자가 닿을 수 있는 범위입니다. 가진 것보다 더 잃을 수 없고, 에너지 변화마다 허용되는 충돌의 범위가 한정됩니다. 에너지를 끌면 윤곽이 커지거나 줄어듭니다. 결합이 없으면 지도는 자유 수소 기체이며, 점선 반동선을 따라 밝은 능선 하나가 놓입니다. 결합이 있으면 분자가 정해진 에너지 양에 해당하는 밝은 줄무늬를 더합니다. INCOGNITA는 물과 베릴륨에 대한 자체 법칙을 계산합니다: <a href="https://github.com/seth-michael-weaver/incognita/tree/main/library/tsl-v0.1" style="white-space:nowrap">tsl-v0.1</a>.</p>
  <div class="ctl"><label for="slo-e">중성자 에너지 (eV)</label><input id="slo-e" type="range" data-bind="lgE" data-instant min="-2.3" max="0" step="0.01" value="-1"><output data-show="Eshow" data-fmt="3"></output></div>
  <div class="btns"><button class="btn ghost" data-act="bind" aria-pressed="true">화학 결합</button></div>
</div>`,
};
/* attributes referenced in the English chapter script (for the structure check): data-act="${act}" */
