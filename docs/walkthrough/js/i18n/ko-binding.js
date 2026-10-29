/* Korean: binding (3장, 결합) */
WT.L.ch.binding = {
  num: "3장", title: "원자핵은 왜 뭉쳐 있는가", short: "결합",
  html: `
<div class="step">
  <p>곡선에서 높을수록 더 단단히 결합되어 있습니다. 각 점은 질량수 A(양성자와 중성자의 수) 하나이고, 그 높이는 그 원자핵을 완전히 뜯어내는 데 핵자당 드는 에너지입니다. A를 끌어 보면서 표시기를 읽어 보세요. 곡선의 가운데, 철과 니켈 근처가 꼭대기입니다.</p>
  <div class="ctl"><label for="bi-a">질량수 A</label><input id="bi-a" type="range" data-bind="pick" data-instant min="2" max="260" step="1" value="56"><output data-show="pick" data-fmt="0"></output></div>
</div>
<div class="step">
  <p>우라늄을 쪼개 보세요. 두 조각 모두 원래의 우라늄보다 곡선 위에서 더 높은 곳에 있으므로, 같은 핵자들이 더 단단히 결합하게 되고 그 차이가 에너지로 나옵니다. 가벼운 쪽 조각을 고르세요. 무거운 쪽은 236개 핵자 가운데 나머지입니다.</p>
  <div class="ctl"><label for="bi-f">가벼운 조각 A</label><input id="bi-f" type="range" data-bind="frag" data-instant min="70" max="118" step="1" value="95"><output data-show="frag" data-fmt="0"></output></div>
  <p class="ctl-result" id="bi-split-out" aria-live="polite"></p>
  <p>어떻게 쪼개든 약 200 MeV입니다. 연료 분자 하나를 태워 얻는 몇 전자볼트의 수천만 배입니다.</p>
</div>
<div class="step">
  <p>가벼운 원자핵 둘을 하나로 합쳐 보세요. 새 원자핵이 곡선에서 더 높은 곳에 있으면 에너지가 나옵니다. 꼭대기를 지나면 합치는 데 오히려 에너지가 듭니다.</p>
  <div class="ctl"><label for="bi-u">가벼운 원자핵 하나의 A</label><input id="bi-u" type="range" data-bind="fuse" data-instant min="2" max="60" step="1" value="2"><output data-show="fuse" data-fmt="0"></output></div>
  <p class="ctl-result" id="bi-fuse-out" aria-live="polite"></p>
</div>`,
};
