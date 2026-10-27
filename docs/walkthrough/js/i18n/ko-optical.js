/* Korean: optical (17장, 광학 모형을 풀다) */
WT.L.ch.optical = {
  num: "17장", title: "광학 모형을 풀다", short: "광학 모형 풀이",
  lead: "2장에서는 광학 퍼텐셜을 흐린 유리 구슬로 그렸습니다. 여기서는 엔진이 실제로 쓰는 모습 그대로 보여 줍니다. 전역 매개변수화, 한 걸음씩 적분하는 지름 방향 슈뢰딩거 방정식, 그리고 파동을 투과 계수로 바꾸는 접속 조건입니다.",
  html: `
<div class="step">
  <h3>코닝–델라로슈 퍼텐셜</h3>
  <p>구형 표적에 입사하는 중성자와 양성자의 기본값은 <b>코닝–델라로슈</b>(Koning–Delaroche, KD03) 퍼텐셜입니다. 깊이가 에너지와 표적의 질량, 중성자 과잉에 따라 매끄럽게 변하는 우즈–색슨 모양들로 이루어져 있으며, 깊이는 전역 공식에서, 또는 철-56처럼 KD03이 하나씩 따로 맞춘 원자핵에서는 같은 꼴의 국소 맞춤에서 나옵니다. 그림은 철-56에 입사하는 중성자에 전역 공식을 씁니다. 실수부 우물(파랑)은 붙잡고, 허수부(빨강)는 흡수합니다. 흡수는 부피 전체에서, 그리고 낮은 에너지에서는 주로 표면의 얇은 껍데기에서 일어납니다.</p>
  <div class="ctl"><label for="op-e">중성자 에너지 (MeV)</label><input id="op-e" type="range" data-bind="E" min="0.1" max="80" step="0.1" value="5"><output data-show="E" data-fmt="1"></output></div>
  <div class="formula">U(r) = −V<sub>V</sub> f(r) − iW<sub>V</sub> f(r) + 4i a<sub>D</sub>W<sub>D</sub> df<sub>D</sub>/dr + 2(V<sub>so</sub> + iW<sub>so</sub>) (1/r) df<sub>so</sub>/dr ⟨l·σ⟩</div>
  <p>탐침 중성자들은 설정한 에너지로 지나가며, 흡수가 강한 곳에서 흐려집니다. 평균 자유 행로는 ħ<i>v</i>/2|<i>W</i>|입니다. 각 깊이는 페르미 에너지에서 잰 <i>E</i> − <i>E</i><sub>F</sub>의 함수입니다. 실수부 깊이는 천천히 줄고, 표면 흡수 <i>W</i><sub>D</sub>는 10 MeV 근처에서 최대가 되며, 부피 흡수 <i>W</i><sub>V</sub>는 꾸준히 커지다가 여기서는 약 45 MeV 위에서 표면 흡수를 앞지릅니다.</p>
</div>
<div class="step">
  <h3>지름 방향 방정식 적분하기</h3>
  <p>부분파마다 자기 지름 방향 방정식을 따릅니다. 엔진은 이를 <i>r</i> = 0에서 바깥쪽으로, 전체 복소 퍼텐셜을 거쳐 <b>누메로프 방법</b>으로 적분합니다. 누메로프 방법은 간격의 여섯제곱까지 정확한 3점 공식입니다.</p>
  <div class="formula">u″<sub>lj</sub>(r) = [ l(l+1)/r² + (2μ/ħ²) U<sub>lj</sub>(r) − k² ] u<sub>lj</sub>(r)</div>
  <div class="ctl"><label for="op-l">부분파 l</label><input id="op-l" type="range" data-bind="L" min="0" max="10" step="1" value="1" data-instant><output data-show="L" data-fmt="0"></output></div>
  <div class="ctl"><label for="op-e2">중성자 에너지 (MeV)</label><input id="op-e2" type="range" data-bind="E" min="0.1" max="80" step="0.1" value="5"><output data-show="E" data-fmt="1"></output></div>
  <p>실선은 시간에 따라 움직이는 파동 Re[<i>u</i> e<sup>−iωt</sup>]이고, 점선은 원자핵이 없을 때의 자유 파동입니다. 우물 안에서 파동은 더 짧아지고(중성자가 더 빠름) 더 작아집니다(흡수됨). 바깥에서는 위상이 밀린 채로 되돌아 나옵니다.</p>
</div>
<div class="step">
  <h3>파동에서 S와 T로</h3>
  <p>약 12 fm 너머에서는 퍼텐셜이 사라지므로, 파동은 들어오는 자유 파동과 나가는 자유 파동의 혼합 <i>u</i> ∝ <i>H</i><sup>−</sup> − <i>S</i> <i>H</i><sup>+</sup>여야 합니다. 적분한 <i>u</i>를 두 반지름에서 맞추면 <b>S 행렬</b> 원소 <i>S<sub>lj</sub></i>, 즉 위상을 포함한 나가는 파동의 진폭이 정해집니다.</p>
  <div class="btns"><button class="btn ghost" data-act="abs" aria-pressed="false">흡수 끄기</button></div>
  <div class="formula">S<sub>lj</sub> = η<sub>lj</sub> e<sup>2iδ<sub>lj</sub></sup> ,  T<sub>lj</sub> = 1 − |S<sub>lj</sub>|²</div>
  <p>점은 복소 평면 위의 <i>S</i>로, 단위원 안에 있습니다. 꼬리는 에너지가 0.1에서 40 MeV까지 훑는 동안의 경로입니다. 흡수가 없으면 |<i>S</i>| = 1이어서 점은 원 위를 달리고, 파동은 위상만 바뀌며, <i>T</i> = 0입니다. 원 안쪽으로 들어온 거리가 바로 복합핵과 다른 모든 반응이 받는 몫입니다.</p>
</div>
<div class="step">
  <h3>스핀–궤도 항이 j를 가른다</h3>
  <p><b>스핀–궤도</b> 항은 <i>j</i> = <i>l</i> + ½에는 인력, <i>j</i> = <i>l</i> − ½에는 척력으로 작용합니다. 표면에서 몇 MeV 정도로 작지만, 각 <i>l</i>의 두 투과 계수를 서로 떼어 놓으며, 표면을 스치는 부분파 근처에서 가장 크게 떼어 놓습니다.</p>
  <div class="ctl"><label for="op-e3">중성자 에너지 (MeV)</label><input id="op-e3" type="range" data-bind="E" min="0.1" max="80" step="0.1" value="5"><output data-show="E" data-fmt="1"></output></div>
  <div class="btns"><button class="btn ghost" data-act="so" aria-pressed="false">스핀–궤도 끄기</button></div>
  <p>하우저–페시바흐(16장)는 두 값을 따로 씁니다. 가중치를 붙여 더한 (<i>l</i>+1)<i>T</i><sub>l,l+½</sub> + <i>l</i> <i>T</i><sub>l,l−½</sub>는 반응 단면적을 거의 바꾸지 않습니다. 그래서 전체 단면적만으로는 스핀–궤도 세기가 거의 제한되지 않고, 편극 데이터가 필요합니다.</p>
</div>
<div class="step">
  <h3>단면적</h3>
  <p>부분파를 합하면 퍼텐셜을 맞추는 데 쓰는 관측량이 나옵니다. 반응 단면적은 빠져나간 선속을 세고, 전체 단면적은 앞방향 진폭에서 나오며, 둘의 차이가 형상 탄성 산란입니다.</p>
  <div class="formula">σ<sub>R</sub> = (π/k²) Σ<sub>l</sub> [(l+1)T<sub>l,l+½</sub> + l T<sub>l,l−½</sub>] ,  σ<sub>tot</sub> = (2π/k²) Σ<sub>lj</sub> (j+½)(1 − Re S<sub>lj</sub>)</div>
  <div class="ctl"><label for="op-e4">중성자 에너지 (MeV)</label><input id="op-e4" type="range" data-bind="E" min="0.2" max="50" step="0.1" value="5"><output data-show="E" data-fmt="1"></output></div>
  <p>KD03은 1 keV에서 200 MeV까지 많은 원자핵의 이런 데이터에 맞춘 것입니다. 철의 전체 단면적은 몇 MeV에서 3.5–4 b, 14 MeV에서 2.5 b인데, 이 원자핵에 따로 조정하지 않아도 넓은 극대까지 포함해 약 5퍼센트 안으로 나옵니다. 그 극대는 중성자 파장에 비춰 본 원자핵의 크기입니다.</p>
</div>
<div class="step">
  <h3>낮은 에너지 끝</h3>
  <p>몇 keV 아래에서는 s파만 중요하고, <i>T</i><sub>0</sub>는 √<i>E</i>에 비례해 커집니다. 이 로그–로그 그림에서 기울기가 2분의 1입니다. 비례 상수가 <b>세기 함수</b> <i>S</i><sub>0</sub> = <i>T</i><sub>0</sub>/(2π√<i>E</i>)(<i>E</i>는 eV 단위)이며, 공명 분석에서 Σ Γ<sub>n</sub><sup>0</sup>/Δ<i>E</i>로 측정하는 바로 그 양입니다.</p>
  <p>전역 퍼텐셜은 주로 MeV 에너지에서 맞춘 것이어서, 낮은 에너지 끝이 가장 약한 부분입니다. 철-56에 대해 이 퍼텐셜은 <i>S</i><sub>0</sub> ≈ 5.5 × 10⁻⁴를 주고 KD03 국소 맞춤도 거의 같은 값을 주지만, 측정값(RIPL)은 2.3 ± 0.6 × 10⁻⁴입니다. 철은 <i>A</i> ≈ 55 부근 3s 크기 공명의 봉우리 근처에 있어, <i>S</i><sub>0</sub>가 퍼텐셜에 가장 민감한 곳입니다. 그래서 측정된 <i>S</i><sub>0</sub>와 <i>S</i><sub>1</sub>은 엔진에 따로 넣는 선택적 입력입니다.</p>
  <div class="aside">코드에서: <code>omp/parameters.py</code>(KD03과 다른 전역 퍼텐셜), <code>omp/potential.py</code>(지름 방향 형태 인자), <code>omp/schrodinger.py</code>(누메로프 적분과 접속. 하전 입자에는 스티드(Steed) 방법으로 구한 쿨롱 함수를 쓰며, 구형 표적에서는 ECIS를 대신하고 ECIS의 T<sub>lj</sub>와 대조해 검증됨), <code>ecis/</code>(변형된 표적을 위한 결합 채널 이식), <code>omp/sfunc.py</code>(선택 사항: 측정된 S₀, S₁). 그림은 철-56에 입사하는 중성자에 대해 이 방정식을 비상대론적으로 직접 풉니다.</div>
</div>`,
};
(function () {
  const L = {
    // scene 1: potential
    "{#} fm": "{#} fm", "{#} MeV": "{#} MeV", "E = {#} MeV": "E = {#} MeV",
    "real well, depth {#} MeV": "실수부 우물, 깊이 {#} MeV",
    "surface absorption, peak {#} MeV": "표면 흡수, 최대 {#} MeV",
    "volume absorption {#} MeV": "부피 흡수 {#} MeV",
    "spin–orbit for l = {#}, j = {#}/{#}: {#} MeV": "스핀–궤도 (l = {#}, j = {#}/{#}): {#} MeV",
    "real": "실수부", "volume": "부피", "surface": "표면",
    "depths (MeV) against energy (MeV)": "에너지(MeV)에 따른 깊이(MeV)",
    // scene 2: wave
    "potential: real (blue), imaginary (red)": "퍼텐셜: 실수부 (파랑), 허수부 (빨강)",
    "nuclear surface": "원자핵 표면",
    "l = {#}, j = {#}+½ · E = {#} MeV · |S| = {#} · δ = {#}° · T = {#}": "l = {#}, j = {#}+½ · E = {#} MeV · |S| = {#} · δ = {#}° · T = {#}",
    "solid: the wave now · shaded: its size |u| · dashed: free wave": "실선: 현재 파동 · 음영: 크기 |u| · 점선: 자유 파동",
    // scene 3: S-matrix
    "Re S": "Re S", "Im S": "Im S",
    "|S| = {#}: nothing absorbed": "|S| = {#}: 흡수 없음",
    "l = {#}, j = {#}+½ · E = {#} MeV": "l = {#}, j = {#}+½ · E = {#} MeV",
    "|S| = {#} · T = {#} − |S|² = {#}": "|S| = {#} · T = {#} − |S|² = {#}",
    "l = {#}, j = {#}+½": "l = {#}, j = {#}+½",
    "|S| = {#}": "|S| = {#}",
    "T = {#} − |S|² = {#}": "T = {#} − |S|² = {#}",
    "trail: S as E runs {#} → {#} MeV": "꼬리: E가 {#} → {#} MeV로 갈 때의 S",
    "no absorption: S stays on the circle": "흡수 없음: S가 원 위에 머묾",
    // scene 4: spin-orbit
    "T = {#}": "T = {#}", "l": "l",
    "hollow: j = l − ½ · solid: j = l + ½": "속 빈 것: j = l − ½ · 속 찬 것: j = l + ½",
    "hollow (purple): j = l − ½ · solid (blue): j = l + ½": "속 빈 것 (보라): j = l − ½ · 속 찬 것 (파랑): j = l + ½",
    "reaction cross section {#} b (without spin–orbit {#} b)": "반응 단면적 {#} b (스핀–궤도 없이 {#} b)",
    "reaction cross section {#} b (spin–orbit off)": "반응 단면적 {#} b (스핀–궤도 끔)",
    "grazing l ≈ kR = {#}": "스치는 l ≈ kR = {#}",
    // scene 5: cross sections
    "{#} b": "{#} b", "{#} keV": "{#} keV", "{#} eV": "{#} eV",
    "total {#} b": "전체 {#} b",
    "reaction {#} b": "반응 {#} b",
    "shape elastic {#} b": "형상 탄성 {#} b",
    "n + ⁵⁶Fe, KD{#}, computed here": "n + ⁵⁶Fe, KD{#}, 여기서 계산",
    // scene 6: low energy
    "T₀ (s-wave)": "T₀ (s파)",
    "T₁ (p-wave, j = {#}/{#}): slope {#}/{#}": "T₁ (p파, j = {#}/{#}): 기울기 {#}/{#}",
    "dashed: {#}πS₀√E, slope ½": "점선: {#}πS₀√E, 기울기 ½",
    "S₀ = {#} × {#}⁻⁴ from this potential": "이 퍼텐셜에서 S₀ = {#} × {#}⁻⁴",
  };
  // mean free path: each value is a number or "> 100"
  for (const a of ["{#}", "> {#}"]) for (const b of ["{#}", "> {#}"])
    L[`mean free path: ${a} fm at the surface, ${b} fm in the centre`] = `평균 자유 행로: 표면에서 ${a} fm, 중심에서 ${b} fm`;
  Object.assign(WT.L.labels, L);
})();
Object.assign(WT.L.glossary, {
  koningDelaroche: {
    term: "코닝–델라로슈 퍼텐셜", aliases: ["코닝–델라로슈", "코닝-델라로슈", "Koning–Delaroche", "KD03"],
    short: "A. J. 코닝(Koning)과 J.-P. 델라로슈(Delaroche)의 중성자·양성자 전역 광학 퍼텐셜(2003)로, 1 keV에서 200 MeV, 질량수 24에서 209까지를 다룹니다.",
    more: "깊이, 반지름, 표면 퍼짐이 에너지, 질량, 중성자 과잉의 매끄러운 함수이며, 측정된 많은 단면적과 각분포에 한꺼번에 맞춘 것입니다. TALYS와 이 엔진에서 핵자의 기본 퍼텐셜입니다.",
    chapter: "optical",
  },
  numerov: {
    term: "누메로프 방법", aliases: ["누메로프 방법", "누메로프", "Numerov"],
    short: "지름 방향 슈뢰딩거 방정식처럼 1차 도함수 항이 없는 2계 방정식을 적분하는 3점 공식으로, 한 걸음당 오차가 h⁶ 차수입니다.",
    formula: "(1 − h²Q_n+1/12) u_n+1 = 2(1 + 5h²Q_n/12) u_n − (1 − h²Q_n−1/12) u_n−1",
    chapter: "optical",
  },
  sMatrix: {
    term: "S 행렬", aliases: ["S 행렬", "S-행렬", "S-matrix"],
    short: "들어오는 파동과 나가는 파동을 잇는 진폭들입니다. 한 부분파의 탄성 산란에서는 복소수 하나 S = η e^(2iδ)입니다.",
    more: "|S| = 1이면 아무것도 흡수되지 않고 위상 δ만 바뀝니다. 모자란 양 1 − |S|²이 투과 계수, 즉 반응으로 빠져나가는 선속입니다.",
    chapter: "optical",
  },
  spinOrbit: {
    term: "스핀–궤도 항", aliases: ["스핀–궤도", "스핀-궤도", "spin–orbit", "spin-orbit"],
    short: "핵자의 스핀이 궤도 각운동량과 평행한지 반평행한지에 따라 달라지는 핵 퍼텐셜의 부분입니다.",
    more: "j = l + ½에는 인력, j = l − ½에는 척력으로 작용하며 원자핵 표면에서 가장 큽니다. 같은 상호작용이 껍질 모형의 마법수를 만듭니다.",
    chapter: "optical",
  },
});
