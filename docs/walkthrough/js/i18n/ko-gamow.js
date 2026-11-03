/* Korean: gamow (30장, 가모프 봉우리와 점화) */
WT.L.ch.gamow = {
  num: "30장", title: "가모프 봉우리와 점화", short: "가모프 봉우리",
  lead: "뜨거운 플라스마는 좁은 에너지 창을 통해 탑니다. 터널링할 만큼 빠르고, 의미가 있을 만큼 흔한 에너지입니다.",
  html: `
<div class="step">
  <h3>가모프 봉우리</h3>
  <p>빠른 원자핵은 드물지만, 빠른 원자핵일수록 터널링이 쉽습니다. 둘을 곱한 것이 빛납니다. 이것이 가모프 봉우리입니다. 온도 선을 끌어 보세요.</p>
  <div class="ctl"><label for="gw-t">온도 kT (keV)</label><input id="gw-t" type="range" data-bind="lT" min="0" max="2" step="0.01" value="1"><output data-show="T" data-fmt="1"></output></div>
  <div class="formula">E₀ = (E<sub>G</sub> (kT)² / 4)<sup>1/3</sup> · 폭 4√(E₀kT/3)</div>
</div>
<div class="step">
  <h3>연료의 반응도</h3>
  <p>창 전체를 더하면 반응도 ⟨σv⟩가 나옵니다. 장치가 도달할 수 있는 어떤 온도에서도 D–T가 압도적으로 앞섭니다.</p>
  <div class="ctl"><label for="gw-t2">온도 kT (keV)</label><input id="gw-t2" type="range" data-bind="lT" min="0" max="2" step="0.01" value="1"><output data-show="T" data-fmt="1"></output></div>
  <div class="formula">⟨σv⟩ = ∫ σ(E) v f(E) dE</div>
</div>
<div class="step">
  <h3>로슨 조건과 점화</h3>
  <p>플라스마를 원하는 온도와 가둠 정도로 끌어다 놓고 손을 떼세요. 맨 위 곡선보다 위에서는 스스로 뜨거움을 유지합니다.</p>
  <div class="btns"><button class="btn" data-act="lowgo">약한 장치로 해 보기</button> <button class="btn ghost" data-act="higo">강한 장치로 해 보기</button></div>
  <div class="formula">점화: n τ<sub>E</sub> T ≳ 3·10²¹ keV s m⁻³</div>
</div>`,
};
