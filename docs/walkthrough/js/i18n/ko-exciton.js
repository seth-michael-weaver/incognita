/* Korean: exciton (17장, 수로 보는 엑시톤 모형) */
WT.L.ch.exciton = {
  num: "17장", title: "수로 보는 엑시톤 모형", short: "엑시톤 모형",
  lead: "4장에서는 빠른 중성자 하나가 몇 번 충돌하는 과정을 따라갔습니다. 여기서는 각 단계에서 다음 일이 또 한 번의 충돌일지 탈출일지를 정하는 비율들과, 그 비율들이 모여 만드는 스펙트럼을 다룹니다.",
  html: `
<div class="step">
  <h3>입자–구멍 상태 세기</h3>
  <p>엑시톤 모형은 평형으로 가는 도중의 원자핵을 들뜬 입자의 수 <i>p</i>와 구멍의 수 <i>h</i>, 그리고 <i>n</i> = <i>p</i> + <i>h</i>로 분류합니다. 표적에 들어온 중성자는 <i>p</i> = 1, <i>h</i> = 0에서 출발하고, 충돌할 때마다 쌍이 하나씩 늘어납니다. 각 단계에서 중요한 것은 에너지를 <i>n</i>개의 엑시톤이 나눠 가질 수 있는 방법의 수, 즉 입자–구멍 상태 밀도입니다.</p>
  <div class="formula">ω(p,h,E) = g<sup>n</sup> (E − A<sub>p,h</sub>)<sup>n−1</sup> / (p! h! (n−1)!) ,  A<sub>p,h</sub> = max(p,h)²/g − (p² + h² + p + h)/4g</div>
  <div class="ctl"><label for="ex-n">입자 p (구멍 p − 1)</label><input id="ex-n" type="range" data-bind="pp" min="2" max="6" step="1" value="3" data-instant><output data-show="pp" data-fmt="0"></output></div>
  <div class="btns"><button class="btn ghost" data-act="pauli" aria-pressed="true">파울리 보정</button></div>
  <p><i>g</i> ≈ <i>A</i>/15 MeV⁻¹는 페르미 에너지 근처의 단일 입자 준위 밀도입니다. <i>A<sub>p,h</sub></i>는 <b>파울리</b> 보정입니다. 두 입자가 한 준위를 함께 쓸 수 없으므로 가장 낮은 배치에도 에너지가 들고, 문턱 근처의 밀도가 떨어집니다. 그림은 고른 <i>p</i>를 갖는 배치 하나를 무작위로 뽑아 한 번에 하나씩 보여 줍니다.</p>
</div>
<div class="step">
  <h3>더 깊이 들어가거나, 빠져나가거나</h3>
  <p>각 단계에서는 두 가지 일이 일어날 수 있습니다. 충돌이 쌍을 하나 더 만드는 비율이 λ<sup>+</sup>이며, 페르미 황금률에 따라 행렬 요소의 제곱 곱하기 도달 가능한 상태의 밀도입니다. 또는 입자가 떠나는데, 그 비율 <i>W</i>는 세부 균형에 따라 역반응 단면적과, 탈출하는 입자가 있을 때와 없을 때의 상태 밀도 비로 주어집니다.</p>
  <div class="formula">λ<sup>+</sup>(n) = (2π/ħ) M² ω<sub>acc</sub> ,  W(p,h,ε) = (2s+1)/(π²ħ³) με σ<sub>inv</sub>(ε) ω(p−1,h,U) / ω(p,h,E)</div>
  <div class="ctl"><label for="ex-e">중성자 에너지 (MeV)</label><input id="ex-e" type="range" data-bind="Ein" min="5" max="60" step="0.5" value="20"><output data-show="Ein" data-fmt="1"></output></div>
  <p>막대는 각 단계의 두 비율을 로그 눈금으로 나타낸 것입니다. λ<sup>+</sup>는 10²² s⁻¹ 정도이고, <i>W</i>는 첫 단계에서 그 10분의 1쯤이며 단계마다 줄어듭니다. 새 쌍이 생길 때마다 앞장선 입자가 가져갈 수 있는 에너지가 줄기 때문입니다. 엔진은 M²를 코닝–다위베스테인(Koning–Duijvestijn) 형태에서 가져오며, 이 값은 엑시톤당 에너지가 커질수록 줄어듭니다.</p>
  <div class="formula">M² = (C₁ A<sub>p</sub> / A³) · [7.48 + 4.62×10⁵ / (E/(n A<sub>p</sub>) + 10.7)³]  MeV²</div>
</div>
<div class="step">
  <h3>시간에 따른 사슬</h3>
  <p>쌍을 없애는 드문 충돌을 무시하면(되돌아오지 않음 근사), 개체수는 단순한 사슬을 따릅니다. 각 단계는 앞 단계에서 채워지고, 다음 단계와 연속 영역으로 비워집니다. 막대는 이 주 방정식을 돌린 것이며, 시간의 단위는 10⁻²² s입니다.</p>
  <div class="formula">dP(n)/dt = λ<sup>+</sup>(n−2) P(n−2) − [λ<sup>+</sup>(n) + W(n)] P(n)</div>
  <div class="ctl"><label for="ex-e2">중성자 에너지 (MeV)</label><input id="ex-e2" type="range" data-bind="Ein" min="5" max="60" step="0.5" value="20"><output data-show="Ein" data-fmt="1"></output></div>
  <p>사슬 전체가 10⁻²² s의 몇 배 안에 끝납니다. 도중에 빠져나가는 몫이 전평형 방출이고, 나머지는 엔진에서 TALYS처럼 입자가 최대 여섯 개가 된 뒤 복합핵으로 넘겨집니다. 시간으로 적분하면 각 단계에 세기 τ(<i>n</i>)·<i>P</i>(<i>n</i>)가 주어지며, 엔진이 계산하는 것은 바로 이 곱입니다.</p>
</div>
<div class="step">
  <h3>딱딱한 꼬리는 어디서 오는가</h3>
  <p>방출 스펙트럼은 단계마다 개체수 곱하기 수명 곱하기 방출 비율을 합하고, 남은 것의 증발을 더한 것입니다. 입자 둘과 구멍 하나인 <i>n</i> = 3 단계만이 가장 높은 방출 에너지까지 닿습니다. 그 스펙트럼은 끝점 쪽으로 선형으로만 줄어듭니다. 뒤의 단계일수록 더 부드럽습니다.</p>
  <div class="formula">dσ/dε = σ<sub>CN</sub> Σ<sub>n</sub> P(n) τ(n) W(n,ε) + 증발</div>
  <div class="ctl"><label for="ex-e3">중성자 에너지 (MeV)</label><input id="ex-e3" type="range" data-bind="Ein" min="5" max="60" step="0.5" value="20"><output data-show="Ein" data-fmt="1"></output></div>
  <p>에너지를 올리면 스펙트럼이 딱딱해집니다. 전평형 꼬리는 끝점까지 뻗지만 증발 언덕은 1–2 MeV에 머뭅니다. 약 10 MeV 위에서는 측정된 고에너지 중성자를 이 꼬리 없이는 재현할 수 없습니다.</p>
</div>
<div class="step">
  <h3>몫은 얼마나 큰가</h3>
  <p>방출 가운데 전평형의 몫은 입사 에너지와 함께 커져, 여기서는 5 MeV 근처의 몇 퍼센트에서 40 MeV의 약 40퍼센트까지 늘어납니다. 이 몫은 조정 가능한 상수 하나, 즉 행렬 요소의 전체 크기에 달려 있습니다. 상호작용이 약할수록 평형이 느려지고 이른 방출이 많아집니다.</p>
  <div class="ctl"><label for="ex-c">행렬 요소 상수 C₁</label><input id="ex-c" type="range" data-bind="c1" min="0.3" max="3" step="0.05" value="1"><output data-show="c1" data-fmt="2"></output></div>
  <p>점선 곡선은 엔진의 기본값 C₁ = 1이고, 실선은 슬라이더를 따릅니다. C₁을 절반으로 줄이면 몫은 2배가 아니라 1.5–1.9배 커집니다. 각 단계의 탈출 확률은 W/λ<sup>+</sup>가 아니라 W/(λ<sup>+</sup> + W)이고, 뒤 단계까지 살아남는 원자핵도 줄어들기 때문입니다.</p>
</div>
<div class="step">
  <h3>두 성분, 그리고 두 번째 탈출</h3>
  <p>엔진은 양성자와 중성자를 따로 추적합니다(<i>p</i><sub>π</sub>, <i>h</i><sub>π</sub>, <i>p</i><sub>ν</sub>, <i>h</i><sub>ν</sub>). 같은 종류의 쌍과 다른 종류의 쌍에 서로 다른 행렬 요소를 쓰고, 표면 근처의 첫 충돌에는 줄인 우물 깊이를 쓰며, 클러스터에는 칼바흐의 규칙을 씁니다. 20 MeV 위에서는 아직 엑시톤을 품고 있는 잔류핵이 평형에 이르기 전에 두 번째 빠른 입자를 내보내는 것도 허용합니다.</p>
  <div class="ctl"><label for="ex-e4">중성자 에너지 (MeV)</label><input id="ex-e4" type="range" data-bind="Ein" min="5" max="60" step="0.5" value="20"><output data-show="Ein" data-fmt="1"></output></div>
  <p>곡선은 이를 장난감처럼 단순화한 것입니다. 세 엑시톤 단계에서 첫 방출이 일어난 뒤, 잔류핵에 남은 입자가 다음 충돌 전에 탈출할 확률입니다. 20 MeV 아래에서는 작게 머물다가 그 위에서 커지며, 엔진이 다중 전평형을 켜는 곳도 바로 거기입니다.</p>
  <div class="aside">코드에서: <code>density/particle_hole.py</code>(윌리엄스 밀도, 파울리 보정과 유한 우물 보정, 단일 성분과 두 성분), <code>preeq/exciton.py</code>(행렬 요소, 방출 비율과 전이 비율, 수명, 되돌아오지 않음 근사의 해), <code>preeq/complex.py</code>(칼바흐 픽업, 스트리핑, 녹아웃), <code>preeq/multi.py</code>(다중 전평형, 기본적으로 20 MeV부터). 그림은 철-56과 비슷한 표적에 대해 도식적인 역반응 단면적을 쓴 단일 성분 모형입니다.</div>
</div>`,
};
(function () {
  const L = {
    "E (MeV)": "E (MeV)", "{#} MeV": "{#} MeV",
    // scene 1: state densities
    "ω(p, h, E) per MeV": "ω(p, h, E), MeV당",
    "{#}p{#}h": "{#}p{#}h",
    "dashed: no Pauli correction": "점선: 파울리 보정 없음",
    "Fermi level": "페르미 준위",
    "{#} particles, {#} holes": "입자 {#}개, 구멍 {#}개",
    // scene 2: rates
    "rate (s⁻¹)": "비율 (s⁻¹)",
    "n = {#}": "n = {#}",
    "W/λ⁺ = {#}": "W/λ⁺ = {#}",
    "blue: λ⁺, the next collision · yellow: W, neutron escape": "파랑: λ⁺, 다음 충돌 · 노랑: W, 중성자 탈출",
    "E = {#} + Sₙ = {#} MeV · τ(n={#}) = {#} × {#}⁻²² s": "E = {#} + Sₙ = {#} MeV · τ(n={#}) = {#} × {#}⁻²² s",
    // scene 3: chain
    "compound": "복합핵",
    "emitted before equilibrium: {#} % (of {#} % in the end)": "평형 전에 방출: {#}% (최종 {#}% 중)",
    "t = {#} × {#}⁻²² s": "t = {#} × {#}⁻²² s",
    // scene 4: spectrum
    "outgoing neutron energy ε (MeV)": "방출 중성자 에너지 ε (MeV)",
    "dσ/dε (mb/MeV)": "dσ/dε (mb/MeV)",
    "evaporation": "증발",
    "ε = {#} MeV: {#} % from n = {#}": "ε = {#} MeV: {#}%가 n = {#}에서",
    "pre-equilibrium {#} % of the emission · solid: total": "전평형이 방출의 {#}% · 실선: 전체",
    // scene 5: share
    "pre-equilibrium share of the emission": "방출 중 전평형의 몫",
    "{#} MeV: {#} %": "{#} MeV: {#}%",
    "C₁ = {#} (dashed: {#})": "C₁ = {#} (점선: {#})",
    // scene 6: multiple pre-equilibrium
    "{#} MeV: multiple pre-equilibrium on": "{#} MeV: 다중 전평형 켜짐",
    "chance of a second fast emission (toy estimate)": "두 번째 빠른 방출의 확률 (간이 추정)",
    "residual: {#}p{#}h": "잔류핵: {#}p{#}h",
  };
  Object.assign(WT.L.labels, L);
})();
Object.assign(WT.L.glossary, {
  neverComeBack: {
    term: "되돌아오지 않음 근사", aliases: ["되돌아오지 않음 근사", "never-come-back"],
    short: "평형에 이르는 초기 단계에서는 충돌이 입자–구멍 쌍을 더하기만 하고 결코 없애지 않는다는 근사입니다.",
    more: "이 근사로 주 방정식이 단계별로 적분할 수 있는 단순한 사슬이 됩니다. 엑시톤 수가 평형값보다 훨씬 작을 때 성립하며, 전평형 방출이 일어나는 곳이 바로 거기입니다.",
    chapter: "exciton",
  },
});
