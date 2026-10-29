/* Korean: tof (17장, 봉우리 측정) */
WT.L.ch.tof = {
  num: "17장", title: "비행시간 측정", short: "봉우리 측정",
  html: `
<div class="step">
  <p>중성자의 비행시간은 그 에너지를 알려 줍니다. 온갖 에너지를 가진 중성자의 짧은 펄스가 선원을 떠나 빈 관을 따라 검출기까지 달려가고, 빠른 것이 먼저 도착합니다. 관의 길이 <i>L</i>을 알고 있으므로 도착 시간 <i>t</i>마다 중성자의 속력이 나오고, 속력에서 에너지가 나옵니다.</p>
  <div class="formula">E = (72.3 · L / t)²   (E는 eV, L은 미터, t는 마이크로초)</div>
  <p>관 위의 시계는 펄스 이후의 실제 시간을 셉니다. 비행은 약 1400배 느리게 그려졌습니다. 관 아래에서는 마지막 도착이 에너지로 바뀝니다. 비행 거리를 끌어 보세요. 관이 길수록 같은 에너지들이 더 긴 시간에 퍼지므로 각각을 더 세밀하게 구별할 수 있습니다.</p>
  <div class="ctl"><label for="tof-l1">비행 거리 (m)</label><input id="tof-l1" type="range" data-bind="Lv" data-instant min="5" max="200" step="1" value="50"><output data-show="Lv" data-fmt="0"></output></div>
</div>
<div class="step">
  <p>얇은 시료에서는 홈이 단면적을 따라갑니다. 이제 빔 속에 시료가 놓여 있습니다. 6.7 eV 근처에서 시료의 원자핵은 공명을 일으켜 중성자를 붙잡으므로(섬광) 그 시간에 도착하는 중성자가 줄어듭니다. 차트는 시료가 있을 때와 없을 때의 계수를 비교합니다. 이것이 <b>투과율</b>로, 모든 중성자가 지나가면 1입니다.</p>
  <p>점은 흩어짐을 포함한 모의 계수이고, 실선은 검출기가 평균적으로 기록하는 것이며, 점선은 단면적 자체의 모양입니다. 시료가 얇으면 홈이 그 모양을 그대로 따라 합니다.</p>
  <div class="ctl"><label for="tof-d1">시료 두께 (µm)</label><input id="tof-d1" type="range" data-bind="lgT" data-instant min="0" max="3.5" step="0.01" value="0.5"><output data-show="thk" data-fmt="0"></output></div>
</div>
<div class="step">
  <p>두꺼운 시료에서는 홈이 포화합니다. 봉우리 에너지에서는 시료의 앞면이 모든 중성자를 붙잡아 가운데가 새까맣게 되고, 아무리 두껍게 해도 새까만 채로 남습니다. 홈은 옆으로 넓어지는 수밖에 없습니다. 이것이 <b>자기 차폐</b>입니다. 앞쪽 층이 뒤쪽을 가려 줍니다. 그래서 두꺼운 시료는 공명의 봉우리보다 날개에 대해 더 많은 것을 알려 줍니다.</p>
  <div class="ctl"><label for="tof-d2">시료 두께 (µm)</label><input id="tof-d2" type="range" data-bind="lgT" data-instant min="0" max="3.5" step="0.01" value="3"><output data-show="thk" data-fmt="0"></output></div>
</div>
<div class="step">
  <p>펄스가 길수록, 비행이 짧을수록 홈은 흐려집니다. 홈의 폭은 세 가지가 정하며 모두 차트 아래에 적혀 있습니다. 공명 자체의 폭, 열 때문에 시료의 원자가 떨려 충돌마다 에너지를 조금씩 번지게 하는 것(<b>도플러</b> 넓어짐), 그리고 시간 흐림입니다. 펄스가 길거나 관이 짧으면 도착 시간이, 따라서 에너지가 덜 확실해지기 때문입니다.</p>
  <p>펄스를 늘리거나 관을 줄여 보세요. 홈은 더 넓고 얕아지지만 그것이 덜어내는 중성자의 몫은 거의 같게 남습니다.</p>
  <div class="ctl"><label for="tof-p1">펄스 폭 (µs)</label><input id="tof-p1" type="range" data-bind="lgDt" data-instant min="-2" max="1" step="0.01" value="0.3"><output data-show="dt" data-fmt="2"></output></div>
  <div class="ctl"><label for="tof-l2">비행 거리 (m)</label><input id="tof-l2" type="range" data-bind="Lv" data-instant min="5" max="200" step="1" value="20"><output data-show="Lv" data-fmt="0"></output></div>
</div>
<div class="step">
  <p>INCOGNITA는 거꾸로 일합니다. 이런 측정 계수를 가지고, 같은 실험(두께, 열, 시간 흐림)을 거쳤을 때 이를 재현하는 공명이 무엇인지 묻습니다. 여기서 맞춤은 중성자 폭 Γ<sub>n</sub>(준위가 중성자를 얼마나 세게 붙드는가)이 거의 네 배 큰 추측(파란 곡선)에서 시작하여, 곡선이 점들을 지나갈 때까지 한 걸음씩 바꿔 나갑니다.</p>
  <p>표시창은 현재의 추측과 <b>어긋남</b>을 보여 줍니다. 1 근처이면 곡선이 계수의 흩어짐이 허락하는 만큼 점들에 가깝다는 뜻입니다. 실험을 바꾸면 새 계수로 맞춤이 다시 시작되어 거의 같은 폭에 이릅니다. 점들에 잘 맞출 수 없는 곳에서는 어긋남이 그렇게 말해 줍니다.</p>
  <div class="ctl"><label for="tof-l3">비행 거리 (m)</label><input id="tof-l3" type="range" data-bind="Lv" data-instant min="5" max="200" step="1" value="50"><output data-show="Lv" data-fmt="0"></output></div>
  <div class="ctl"><label for="tof-d3">시료 두께 (µm)</label><input id="tof-d3" type="range" data-bind="lgT" data-instant min="0" max="3.5" step="0.01" value="1.5"><output data-show="thk" data-fmt="0"></output></div>
  <div class="ctl"><label for="tof-p2">펄스 폭 (µs)</label><input id="tof-p2" type="range" data-bind="lgDt" data-instant min="-2" max="1" step="0.01" value="-1"><output data-show="dt" data-fmt="2"></output></div>
</div>`,
};
