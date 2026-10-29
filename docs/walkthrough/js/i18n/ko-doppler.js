/* Korean: doppler (20장, 도플러) */
WT.L.ch.doppler = {
  num: "20장", title: "도플러 넓어짐", short: "도플러",
  html: `
<div class="step">
  <h3>표적의 열운동</h3>
  <p>연료가 뜨거워지면 원자가 더 빨리 떨립니다. 중성자가 도착할 때 우라늄 원자는 더 이상 가만히 있지 않습니다.</p>
  <div class="ctl"><label for="dop-t1">연료 온도 (K)</label><input id="dop-t1" type="range" data-bind="T" data-instant min="300" max="1500" step="10" value="600"><output data-show="T" data-fmt="0"></output></div>
</div>
<div class="step">
  <h3>도플러 넓어짐</h3>
  <p>곡선은 중성자의 에너지에 따라 우라늄-238이 중성자를 붙잡을 가능성을 그린 것입니다. 높이는 <b>반</b> 단위의 표적 넓이입니다(1 반은 10<sup>−24</sup> cm²로, 원자핵이 중성자에게 보이는 대략의 크기입니다). 원자가 움직이므로 어떤 것은 중성자와 정면으로 만나고 어떤 것은 중성자에게서 달아납니다. 그래서 좁은 봉우리가 번져 더 낮고 더 넓어집니다. 넓이는 그대로입니다.</p>
  <div class="ctl"><label for="dop-t2">연료 온도 (K)</label><input id="dop-t2" type="range" data-bind="T" data-instant min="300" max="1500" step="10" value="1200"><output data-show="T" data-fmt="0"></output></div>
</div>
<div class="step">
  <h3>공명 자기 차폐</h3>
  <p>연료 펠릿은 두껍습니다. 음영 띠는 각 에너지에서 펠릿이 멈추는 중성자의 몫입니다. 봉우리의 한가운데는 뜨겁든 차갑든 이미 모든 것을 멈추므로, 봉우리가 낮아져도 거기서는 잃는 것이 없습니다. 더 넓어진 날개가 더 많이 붙잡습니다. 더 많은 중성자가 핵분열을 일으키는 대신 포획으로 사라져서 <i>k</i>가 저절로 내려갑니다. (<i>k</i>는 핵분열 한 번이 새로운 핵분열 몇 번으로 이어지는가이며, <a href="#critical">21</a>장에서 설명합니다.)</p>
  <div class="ctl"><label for="dop-t3">연료 온도 (K)</label><input id="dop-t3" type="range" data-bind="T" data-instant min="300" max="1500" step="10" value="900"><output data-show="T" data-fmt="0"></output></div>
</div>`,
};

// canvas labels added 2026-10-29 (I18NLABELS_B)
Object.assign(WT.L.labels, {
  "uranium atoms in the fuel": "연료 속 우라늄 원자",
  "{#} K": "{#} K",
  "caught in the peak": "봉우리에서 포획",
  "k": "k",
  "neutron energy (eV) →": "중성자 에너지 (eV) →",
  "capture cross section": "포획 단면적",
  "peak {#}k barns · Doppler width {#} meV · area unchanged": "봉우리 {#}k 반 · 도플러 폭 {#} meV · 넓이 그대로",
  "all stopped": "모두 멈춤",
  "wider wings catch more": "넓어진 날개가 더 많이 붙잡음",
  "share of neutrons stopped in the fuel": "연료에서 멈춘 중성자의 몫",
  "the peak's centre already stops everything; the wider wings catch more": "봉우리 한가운데는 이미 모두 멈추고, 넓어진 날개가 더 많이 붙잡음",
});
