/* Korean: resonance (15장, 공명) */
WT.L.ch.resonance = {
  num: "15장", title: "공명", short: "공명",
  lead: "에너지가 충분히 낮으면 중성자는 더 이상 매끄럽게 평균된 원자핵을 보지 않습니다. 복합핵의 개별 에너지 준위를 하나씩 보게 됩니다.",
  html: `
<div class="step">
  <p>봉우리 하나하나가 <b>공명</b>입니다. 정확히 그 에너지를 가진 중성자가 떨어져 들어갈 수 있는 복합핵의 에너지 준위입니다. 높이는 그 에너지에서의 <b>포획</b> 단면적(중성자가 흡수되고 광자가 나감)을 로그 눈금으로 나타내고, 폭은 공명 폭 Γ로서 실제보다 약 백 배 넓게 그렸습니다.</p>
  <div class="ctl"><label for="res-e">중성자 에너지 (eV)</label><input id="res-e" type="range" data-bind="En" min="0.5" max="300" step="0.1" value="30"><output data-show="En" data-fmt="1"></output></div>
  <p>중성자가 에너지를 따라 깡충깡충 이동하다가, 내려앉은 곳에서 광자의 섬광과 함께 포획될 수 있습니다. 봉우리 위에서는 단면적이 수천 반이어서 포획이 거의 확실하고, 봉우리 사이에서는 몇 반에 불과합니다. 에너지를 움직여 봉우리 위에 세워 보고, 그다음 두 봉우리 사이에 세워 보세요.</p>
</div>
<div class="step">
  <h3>준위 반발</h3>
  <p>가운데 줄은 실제 준위가 놓이는 방식을 보여 줍니다. 스핀과 반전성이 같은 두 준위는 서로 밀어내므로 거의 겹치는 일이 드뭅니다. <b>무작위 행렬 이론</b>이 이 패턴을 설명합니다. 완전히 무작위한 위치(위쪽 줄)는 뭉치기도 하고 틈을 남기기도 합니다.</p>
  <div class="btns"><button class="btn" data-act="again">다시 뽑기</button></div>
  <p>다시 뽑기를 눌러 새 표본을 만들어 보세요. ⟨r̃⟩는 각 간격을 다음 간격과 비교한 값으로, 무작위일 때 약 0.39, 서로 밀어내는 준위일 때 0.53입니다. 코드는 밀어내는 패턴을 사용합니다. 두 수열, 예를 들어 두 스핀(아래쪽 줄)을 섞으면 밀어냄이 일부 가려집니다.</p>
</div>
<div class="step">
  <h3>포터–토머스 폭 요동</h3>
  <p>이제 각 봉우리의 높이는 선형 눈금으로 나타낸 <b>중성자 폭</b> Γ<sub>n</sub>, 즉 그 준위가 중성자와 얼마나 강하게 결합하는지입니다. 노란 모자는 광자를 얼마나 빨리 내보내는지를 나타내는 γ 폭 Γ<sub>γ</sub>입니다. γ 폭은 수백 가지 광자 경로를 합한 것이어서 모든 준위에서 거의 같습니다.</p>
  <div class="btns"><button class="btn" data-act="roll">폭 뽑기</button><button class="btn ghost" data-act="equal">같은 폭</button><button class="btn ghost" data-act="pt">포터–토머스</button></div>
  <p>한 준위가 중성자와 표적으로 갈라지는 방법은 하나뿐이므로, 그 폭은 종 모양 분포를 따르는 수 하나를 제곱한 것처럼 행동합니다. 하나를 뽑아 보세요. 공이 <i>x</i>에 떨어지고, <i>x</i>²가 다음 봉우리의 높이가 되며, 점 하나가 더미에 떨어집니다. 더미는 0 근처에 몰리고 꼬리가 깁니다. 이것이 <b>포터–토머스</b> 법칙입니다. 대부분의 준위는 약하고, 몇몇은 엄청나게 강합니다. 같은 폭 버튼은 대신 평균 크기의 봉우리를 한 줄로 보여 줍니다.</p>
</div>
<div class="step">
  <h3>통계적 공명 사다리</h3>
  <p>이제 봉우리는 직접 정할 수 있는 네 개의 평균값에서 나옵니다. 측정되지 않은 원자핵에 대해서는 이 평균값들만 예측할 수 있습니다. 평균 간격 <i>D</i><sub>0</sub>, s파(정면) 중성자와 p파(중심에서 벗어난) 중성자에 대해 간격 단위당 평균 중성자 폭인 <b>세기 함수</b> <i>S</i><sub>0</sub>와 <i>S</i><sub>1</sub>, 그리고 평균 γ 폭입니다. 코드는 이로부터 <b>사다리</b>, 즉 그 평균값을 갖는 무작위 준위 집합 하나를 만듭니다. 여기서는 세 개에 슬라이더가 있고, <i>S</i><sub>1</sub>은 고정되어 있습니다(그 값은 봉우리 아래에 적혀 있습니다).</p>
  <div class="ctl"><label for="res-d0">간격 D₀ (eV)</label><input id="res-d0" type="range" data-bind="D0" min="3" max="60" step="0.5" value="20"><output data-show="D0" data-fmt="1"></output></div>
  <div class="ctl"><label for="res-s0">세기 S₀ (×10⁻⁴)</label><input id="res-s0" type="range" data-bind="S0" min="0.2" max="3" step="0.05" value="1"><output data-show="S0" data-fmt="2"></output></div>
  <div class="ctl"><label for="res-gg">γ 폭 ⟨Γγ⟩ (meV)</label><input id="res-gg" type="range" data-bind="Gg" min="10" max="80" step="1" value="23"><output data-show="Gg" data-fmt="0"></output></div>
  <p><i>D</i><sub>0</sub>을 바꾸면 봉우리들이 흩어지거나 모여듭니다. 속이 찬 봉우리는 s파 준위(양의 반전성), 테두리만 있는 봉우리는 p파 준위(음의 반전성)입니다. 중성자 폭은 s파에서 √<i>E</i>, p파에서 <i>E</i><sup>3/2</sup>처럼 커지므로, 테두리만 있는 봉우리는 낮게 시작해서 오른쪽으로 갈수록 높아집니다.</p>
</div>
<div class="step">
  <h3>열 영역</h3>
  <p>같은 봉우리들을 천분의 몇 eV까지 내려가는 로그 에너지 눈금으로 그렸습니다. 원자로의 중성자는 가벼운 원자핵에 튕기며 느려지는데, 매번 에너지의 거의 같은 비율을 잃으므로 여기서는 한 번 튈 때마다 같은 길이를 이동합니다. 일부는 도중에 봉우리에 붙잡힙니다.</p>
  <div class="btns"><button class="btn" data-act="slow">중성자 10개 감속</button></div>
  <p>통과한 중성자들은 첫 봉우리보다 한참 아래인 상온의 에너지 0.025 eV, 즉 <b>열중성자</b> 에너지에 자리 잡습니다. 거기서 단면적(원판의 넓이)은 0 바로 아래의 속박 준위를 포함한 공명들의 꼬리를 합한 것입니다. 꼬리는 1/<i>v</i>(<i>v</i>는 중성자의 속력)처럼 커지므로 바닥이 왼쪽으로 갈수록 올라갑니다. 내려오는 도중에 붙잡히는 양은 <b>공명 적분</b>으로 측정합니다. 0.5 eV 위의 단면적을 각 에너지마다 1/<i>E</i>의 가중치를 주어 합한 것입니다.</p>
</div>
<div class="step">
  <h3>통계가 예측할 수 있는 것</h3>
  <p>각 줄은 같은 네 수로부터 뽑은 사다리 하나이며, 원판의 넓이는 그 사다리의 열중성자 포획 단면적입니다. 괄호는 그 값을 정하는 봉우리, 대개 가장 가까운 봉우리까지 이어집니다. 그 거리는 사다리마다 달라지고, 원판은 열 배 이상 오르내립니다.</p>
  <div class="btns"><button class="btn" data-act="draw1">사다리 뽑기</button><button class="btn ghost" data-act="more">20개 뽑기</button></div>
  <p>각 값은 오른쪽 더미에 떨어집니다. 측정되지 않은 원자핵에 대한 답은 하나의 수가 아니라 값의 퍼짐이며, 어떤 더 나은 모형도 이를 좁힐 수 없습니다. 많은 봉우리에 걸친 합인 공명 적분은 덜 퍼집니다. 가벼운 원자핵처럼 준위 간격이 약 10 keV보다 넓은 경우에는 열에너지 근처에 준위가 없습니다. 그곳의 포획은 직접 포획이며, 코드는 답을 내지 않습니다.</p>
  <div class="aside">코드에서: <code>physics/resonance/ladder.py</code>(무작위 행렬 간격, 포터–토머스 폭, 브라이트–위그너 단면적, 앙상블에 대한 열중성자 포획과 공명 적분), <code>ladder_statistics.py</code>(측정된 사다리로 같은 법칙을 검증), <code>ensemble_runner.py</code>. 이들은 반응 엔진 안이 아니라 그 옆에서 실행됩니다.</div>
</div>`,
};
Object.assign(WT.L.labels, {
  // forest
  "{#} eV": "{#} eV", "+{#} eV": "+{#} eV",
  "height: peak capture (log) · width Γ ×{#}": "높이: 최대 포획 (로그) · 폭 Γ ×{#}",
  "peak height: capture cross section (log scale) · width: resonance width Γ, drawn {#}× wide": "높이: 포획 단면적 (로그 눈금) · 폭: 공명 폭 Γ, {#}배 넓게 그림",
  "D₀ {#} eV · S₀ {#}×{#}⁻⁴ · S₁ {#}×{#}⁻⁴ · ⟨Γγ⟩ {#} meV": "D₀ {#} eV · S₀ {#}×{#}⁻⁴ · S₁ {#}×{#}⁻⁴ · ⟨Γγ⟩ {#} meV",
  "s-wave (+ parity)": "s파 (+ 반전성)", "p-wave (− parity)": "p파 (− 반전성)",
  "caught {#} times in {#} landings": "포획 {#}회 / 착지 {#}회",
  "each peak: one level of the compound nucleus": "봉우리 하나: 복합핵의 준위 하나",
  "each peak: one level of the compound nucleus · about {#} eV apart": "봉우리 하나: 복합핵의 준위 하나 · 간격 약 {#} eV",
  // spacing
  "random positions (Poisson)": "무작위 위치 (푸아송)",
  "repelling levels (random-matrix)": "서로 밀어내는 준위 (무작위 행렬)",
  "two repelling sequences mixed": "밀어내는 두 수열을 섞음",
  "clumps and gaps · ⟨r̃⟩ ≈ {#}": "뭉침과 틈 · ⟨r̃⟩ ≈ {#}",
  "evenly kept apart · ⟨r̃⟩ ≈ {#}": "고르게 떨어짐 · ⟨r̃⟩ ≈ {#}",
  "repulsion half hidden · ⟨r̃⟩ ≈ {#}": "밀어냄이 반쯤 가려짐 · ⟨r̃⟩ ≈ {#}",
  "clumps and gaps · spacing ratio ⟨r̃⟩ ≈ {#}": "뭉침과 틈 · 간격 비 ⟨r̃⟩ ≈ {#}",
  "evenly kept apart · spacing ratio ⟨r̃⟩ ≈ {#}": "고르게 떨어짐 · 간격 비 ⟨r̃⟩ ≈ {#}",
  "repulsion half hidden · spacing ratio ⟨r̃⟩ ≈ {#}": "밀어냄이 반쯤 가려짐 · 간격 비 ⟨r̃⟩ ≈ {#}",
  "⟨r̃⟩: {#} if random, {#} for random-matrix": "⟨r̃⟩: 무작위 {#}, 무작위 행렬 {#}",
  "same average spacing in every row · ⟨r̃⟩: {#} if random, {#} for random-matrix": "모든 줄의 평균 간격은 같음 · ⟨r̃⟩: 무작위 {#}, 무작위 행렬 {#}",
  // Porter-Thomas
  "height: neutron width Γn (linear)": "높이: 중성자 폭 Γn (선형)",
  "peak height: neutron width Γn, linear scale": "봉우리 높이: 중성자 폭 Γn, 선형 눈금",
  "yellow: γ width": "노랑: γ 폭",
  "yellow cap: γ width, nearly the same on every peak": "노란 모자: γ 폭, 모든 봉우리에서 거의 같음",
  "equal widths: every peak the average": "같은 폭: 모든 봉우리가 평균값",
  "rolled widths": "뽑은 폭", "pile of rolled widths": "뽑은 폭의 더미",
  "× average": "× 평균", "(in units of the average)": "(평균 단위)",
  "dashed: Porter–Thomas": "점선: 포터–토머스", "dashed: the Porter–Thomas law": "점선: 포터–토머스 법칙",
  "bell-curve number x": "종 모양 분포의 수 x",
  "x = {#}  →  x² = {#}": "x = {#}  →  x² = {#}",
  "press Roll a width": "‘폭 뽑기’를 누르세요",
  // thermal
  "bound level {#} eV": "속박 준위 {#} eV",
  "a bound level at {#} eV: its tail lifts this end": "{#} eV의 속박 준위: 그 꼬리가 이쪽 끝을 들어 올림",
  "resonance integral ≈ {#} b": "공명 적분 ≈ {#} b",
  "resonance integral above {#} eV ≈ {#} b": "{#} eV 이상 공명 적분 ≈ {#} b",
  "{#}/v": "{#}/v",
  "caught by a peak on the way down: {#} · reached thermal: {#}": "내려오다 봉우리에 붙잡힘: {#} · 열에너지 도달: {#}",
  "each hop: one bounce, the same fraction of energy lost": "한 번 튈 때마다 같은 비율의 에너지를 잃음",
  // ensemble
  "thermal neutron": "열중성자",
  "σ disc": "σ 원판", "disc area = σ at {#} eV": "원판 넓이 = {#} eV에서의 σ",
  "{#}k": "{#}k",
  "thermal σ (b)": "열중성자 σ (b)", "thermal σ, barns": "열중성자 σ, 반",
  "{#} ladders · thermal ×{#} · res. integral ×{#}": "사다리 {#}개 · 열중성자 ×{#} · 공명 적분 ×{#}",
});
// labels that carry a cross section printed as "12 b" or "3.4k b"
(function () {
  const L = WT.L.labels;
  for (const b of ["{#} b", "{#}k b"]) {
    L[b] = b;
    L[`σ ≈ ${b} · caught on {#} % of landings`] = `σ ≈ ${b} · 착지의 {#}%에서 포획`;
    L[`σ ≈ ${b} · caught on <{#} % of landings`] = `σ ≈ ${b} · 착지의 <{#}%에서 포획`;
    L[`thermal, {#} eV: σ ≈ ${b}`] = `열중성자, {#} eV: σ ≈ ${b}`;
    L[`{#} ladders · thermal σ median ${b}, middle two thirds ×{#} · resonance integral only ×{#}`] =
      `사다리 {#}개 · 열중성자 σ 중앙값 ${b}, 가운데 3분의 2 ×{#} · 공명 적분은 ×{#}뿐`;
  }
})();
