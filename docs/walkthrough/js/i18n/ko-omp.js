/* Korean: omp (5장, 광학 모형) */
WT.L.ch.omp = {
  num: "5장", title: "흐린 수정 구슬", short: "광학 모형",
  lead: "엔진은 무엇보다 먼저 더 단순한 질문을 던집니다. 들어오는 중성자에게 원자핵은 어떻게 보일까요?",
  html: `
<div class="step">
  <p>양자역학에서 중성자는 파동이기도 합니다. 그림은 왼쪽에서 굴러 들어오는 파동 하나를 보여 주는데, 밝은 띠가 마루이고 그 앞에 원자핵(점선 원)이 있습니다. 아직은 아무것도 파동에 작용하지 않으므로 마루가 그대로 통과합니다.</p>
  <div class="ctl"><label for="omp-e">중성자 에너지 (MeV)</label><input id="omp-e" type="range" data-bind="E" min="0.2" max="40" step="0.1" value="8"><output data-show="E" data-fmt="1"></output></div>
  <p>에너지를 바꿔 가며 아래쪽에 펨토미터(fm, 10⁻¹⁵ m) 단위로 표시된 파장을 살펴보세요. 느린 중성자는 파장이 깁니다. 약 9 MeV 아래에서는 파장 하나가 이 원자핵 전체보다 넓습니다.</p>
</div>
<div class="step">
  <h3>실수부는 끌어당긴다</h3>
  <p><b>광학 퍼텐셜</b>은 원자핵 전체가 중성자에 미치는 평균적인 힘입니다. 그 <em>실수부</em>는 깊이 약 50 MeV의 우물입니다. 중성자가 그 안에서 빨라지므로 마루가 촘촘해집니다. 엔진은 이 우물에 우즈–색슨(Woods–Saxon) 모양을 줍니다. 가운데는 평평하고 깊으며, 표면에서 부드럽게 0으로 줄어듭니다.</p>
</div>
<div class="step">
  <h3>허수부는 흡수한다</h3>
  <p>원자핵 뒤의 그림자는 반응으로 사라진 중성자들입니다. 퍼텐셜의 <em>허수부</em>가 이를 나타냅니다. 허수부는 파동을 휘게 하는 대신 줄어들게 하며, 주로 표면 근처(색칠된 고리)에서 작용합니다.</p>
  <div class="ctl"><label for="omp-w">흡수 W (MeV)</label><input id="omp-w" type="range" data-bind="W" min="0" max="14" step="0.5" value="7"><output data-show="W" data-fmt="1"></output></div>
  <p><i>W</i>를 0으로 내리면 그림자가 채워집니다. 흡수가 없으면 반응도 없습니다. 광학 모형이라는 이름도 여기서 왔습니다. 원자핵은 빛을 일부는 휘게 하고 일부는 흡수하는 흐린 유리 구슬과 같습니다.</p>
</div>
<div class="step">
  <h3>겨냥이 중요하다</h3>
  <p>정면에서 보면 표적은 여러 고리로 나뉘며, 고리마다 하나의 <b>부분파</b> <i>l</i> = 0, 1, 2, …에 해당합니다. 중심에서 거리 <i>b</i>만큼 떨어져 지나가는 중성자는 <b>각운동량</b> <i>l</i> ≈ <i>k b</i>를 가지며, <i>k</i>는 에너지가 높을수록 커집니다. 고리가 어두울수록 그 <b>투과 계수</b> <i>T<sub>l</sub></i>, 즉 그 고리의 중성자가 흡수될 확률이 큽니다.</p>
  <div class="ctl"><label for="omp-e3">중성자 에너지 (MeV)</label><input id="omp-e3" type="range" data-bind="E" min="0.2" max="40" step="0.1" value="8"><output data-show="E" data-fmt="1"></output></div>
  <div class="btns"><button class="btn" data-act="fire">중성자 200개 발사</button></div>
  <p>주황색 섬광은 흡수된 중성자입니다. 막대는 고리마다 흡수된 비율을 모형의 <i>T<sub>l</sub></i>(눈금 표시)과 비교합니다. 안쪽 고리는 거의 모두 흡수하고, 바깥쪽 고리는 중성자를 통과시킵니다. 낮은 에너지에서는 고리가 매우 크고 <i>l</i> = 0만 중요합니다.</p>
</div>
<div class="step">
  <h3>원자핵 곁을 스쳐 지나가기</h3>
  <p>각운동량이 큰 중성자는 너무 바깥쪽으로 지나가서 원자핵에 닿지 못합니다. 이것이 <b>원심력 장벽</b>입니다. 위에서 내려다보면 여기 있는 중성자는 모두 같은 부분파 <i>l</i>에 속하므로 같은 <b>스침 거리</b> <i>b</i> ≈ (<i>l</i>+½)/<i>k</i>(점선 원)에서 지나갑니다.</p>
  <p>하지만 중성자 하나하나는 파동이어서 약 환산 파장 λ̄ 정도(빛나는 테두리)로 퍼져 있습니다. 경로가 빗나가더라도 흐릿한 가장자리가 표면을 스치며 안으로 들어갈 수 있습니다. 이것이 <b>터널 효과</b>입니다.</p>
  <div class="ctl"><label for="omp-l">부분파 l</label><input id="omp-l" type="range" data-bind="L" min="0" max="8" step="1" value="3" data-instant><output data-show="L" data-fmt="0"></output></div>
  <div class="ctl"><label for="omp-e2">에너지 (MeV)</label><input id="omp-e2" type="range" data-bind="E" min="0.2" max="40" step="0.1" value="8"><output data-show="E" data-fmt="1"></output></div>
  <p><i>l</i>을 올리면 경로가 바깥으로 밀려나 들어가는 중성자가 줄어듭니다. 에너지를 올리면 같은 <i>l</i>이 더 가까이 지나가고 퍼짐도 줄어듭니다. 엔진은 전체 퍼텐셜에 대해 슈뢰딩거 방정식을 풀어 각 <i>T<sub>l</sub></i>을 정확히 구합니다. <i>S</i>는 파동이 얼마나 되돌아 나오는지를 나타냅니다.</p>
  <div class="formula">T<sub>lj</sub> = 1 − |S<sub>lj</sub>|²</div>
</div>
<div class="step">
  <h3>표적의 크기를 더하기</h3>
  <p>오른쪽 원판은 중성자에게 원자핵이 얼마나 크게 보이는지, 즉 <b>반응 단면적</b>을 반(barn, 10⁻²⁴ cm²) 단위로 나타냅니다. 각 고리는 자기 넓이에 <i>T<sub>l</sub></i>을 곱한 만큼 더합니다. 점선 원은 기하학적 크기입니다.</p>
  <div class="ctl"><label for="omp-e4">중성자 에너지 (MeV)</label><input id="omp-e4" type="range" data-bind="E" min="0.2" max="40" step="0.1" value="8"><output data-show="E" data-fmt="1"></output></div>
  <div class="btns"><button class="btn ghost" data-act="sum">다시 더하기</button></div>
  <p>에너지를 바꾸면 덧셈이 다시 시작됩니다. 낮은 에너지에서는 큰 고리 한두 개가 원판의 거의 전부를 이루고, 높은 에너지에서는 얇은 고리 여럿이 조금씩 보태어 원판이 기하학적 크기에 가까워집니다.</p>
  <div class="formula">σ<sub>R</sub> = (π/k²) Σ (2l+1) T<sub>l</sub></div>
  <p><i>T<sub>l</sub></i>은 엔진의 나머지 부분으로 전달됩니다. 이 값들은 들뜬 원자핵의 각 스핀이 얼마나 자주 만들어지는지를 정하고, 거꾸로 적용하면 각 입자가 얼마나 쉽게 다시 빠져나오는지를 정합니다.</p>
  <div class="aside">코드에서: <code>omp/parameters.py</code>(Koning–Delaroche 전역 퍼텐셜, 악티늄족용 분산 퍼텐셜), <code>omp/schrodinger.py</code>(누메로프 적분과 쿨롱 접속), <code>omp/inverse.py</code>(세부 균형으로 구한 방출 입자), <code>omp/regional.py</code>(선택 사항, 기본값은 꺼짐: 변형된 희토류 표적에 대한 우물의 지역적 조정으로, 측정된 S₀와 S₁에 맞춤).</div>
</div>`,
};
Object.assign(WT.L.labels, {
  "absorbing surface": "흡수하는 표면",
  "shadow: neutrons lost to reactions": "그림자: 반응으로 사라진 중성자",
  "wavelength {#} fm   ·   nucleus {#} fm across": "파장 {#} fm   ·   원자핵 지름 {#} fm",
  "crests crowd inside the well": "우물 안에서 마루가 촘촘해짐",
  "l={#}": "l={#}",
  "nuclear radius": "핵반지름",
  "reaction cross section ≈ {#} b": "반응 단면적 ≈ {#} b",
  "geometric size π(R+λ̄)² ≈ {#} b · darker ring = more absorbed · orange flash = absorbed": "기하학적 크기 π(R+λ̄)² ≈ {#} b · 어두울수록 많이 흡수 · 주황 섬광 = 흡수",
  "absorbed, ring by ring": "고리별 흡수",
  "bar: your neutrons · tick: model Tₗ": "막대: 발사한 중성자 · 눈금: 모형 Tₗ",
  "rings: shade = Tₗ": "고리: 명암 = Tₗ",
  "geometric size π(R+λ̄)²": "기하학적 크기 π(R+λ̄)²",
  "reaction cross section": "반응 단면적",
  "ring l={#}: ({#}l+{#})·Tₗ·π/k² = +{#} b": "고리 l={#}: ({#}l+{#})·Tₗ·π/k² = +{#} b",
  "all {#} rings added": "고리 {#}개 모두 더함",
  "σ_R = {#} b": "σ_R = {#} b",
  "geometric {#} b": "기하학적 {#} b",
  "geometric {#} b · darker = more absorbed · orange = absorbed": "기하학적 {#} b · 어두울수록 많이 흡수 · 주황 = 흡수",
  "swing distance b ≈ (l+½)/k = {#} fm": "스침 거리 b ≈ (l+½)/k = {#} fm",
  "nuclear radius R = {#} fm · wave fuzz λ̄ = {#} fm": "핵반지름 R = {#} fm · 파동 퍼짐 λ̄ = {#} fm",
  "path crosses the nucleus: most get in": "경로가 원자핵을 통과: 대부분 들어감",
  "path misses the nucleus: only the fuzzy edge can tunnel in": "경로가 원자핵을 빗나감: 흐린 가장자리만 터널링",
  "absorbed {#} of {#} · model Tₗ = {#}": "흡수 {#}개 / 전체 {#}개 · 모형 Tₗ = {#}",
});
