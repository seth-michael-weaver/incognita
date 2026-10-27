/* Korean: averages (27장, 공명에서 평균으로) */
WT.L.ch.averages = {
  num: "27장", title: "공명에서 평균으로", short: "공명에서 평균으로",
  lead: "15장에서는 공명 사다리를 그렸습니다. 여기서는 그것을 단면적으로 보여 줍니다. R 행렬 공식, 매개변수 뒤의 통계, 온도의 효과, 그리고 많은 공명에 대한 평균이 어떻게 하우저–페시바흐가 되는지입니다.",
  html: `
<div class="step">
  <h3>R 행렬, 준위 하나하나</h3>
  <p>무거운 원자핵에서 몇 keV 아래로 내려가면 복합핵 준위가 하나하나 따로 드러나고, 단면적은 준위 매개변수, 즉 에너지 <i>E</i><sub>λ</sub>, 환산 중성자 폭, 포획 폭으로 정확히 표현됩니다. 평가에서는 <b>R 행렬</b> 이론을 쓰며, 가장 흔히 <b>라이히–무어</b> 형태를 씁니다. 이 형태는 중성자 채널에서 준위 사이의 간섭을 유지하고, 많은 포획 채널을 흡수 폭 하나로 다룹니다.</p>
  <div class="formula">R(E) = Σ<sub>λ</sub> γ<sub>λ</sub>² / (E<sub>λ</sub> − E − iΓ<sub>λγ</sub>/2) ,  U = e<sup>−2iφ</sup> (1 + iPR) / (1 − iPR)</div>
  <div class="formula">σ<sub>tot</sub> = (2π/k²) g (1 − Re U) ,  σ<sub>γ</sub> = (π/k²) g (1 − |U|²)</div>
  <div class="btns"><button class="btn ghost" data-act="rm" aria-pressed="true">라이히–무어</button><button class="btn ghost" data-act="bw" aria-pressed="false">단일 준위 브라이트–위그너</button></div>
  <p>위쪽 선은 전체 단면적, 아래쪽 선은 포획으로, 우라늄-238과 비슷한 스핀 0 표적의 s파 준위 사다리 하나에 대한 것입니다. 준위 사이에서는 공명 진폭과 퍼텐셜 진폭이 상쇄되는 곳에서 전체 단면적이 퍼텐셜 산란 아래로 떨어집니다. 단일 준위 형태는 준위들의 진폭 대신 단면적을 더합니다. 봉우리에서는 비슷하지만 골짜기에서는 틀리는데, 그곳에서는 여러 준위의 꼬리가 쌓여 전체 단면적이 음수가 되기도 합니다.</p>
</div>
<div class="step">
  <h3>매개변수 뒤의 통계</h3>
  <p>측정되지 않은 원자핵에는 사다리가 없고 평균값만 있습니다. <i>D</i>₀, 세기 함수 <i>S</i>₀ = ⟨Γ<sub>n</sub>⁰⟩/<i>D</i>₀, 그리고 ⟨Γ<sub>γ</sub>⟩입니다. 나머지는 무작위 행렬 이론이 줍니다. 스핀과 반전성이 같은 준위들의 간격은 위그너 간격 법칙을 따르고, 환산 중성자 폭은 자유도 1의 χ²인 포터–토머스 분포를 따릅니다.</p>
  <div class="formula">P(s) = (πs/2) e<sup>−πs²/4</sup> ,  P(y) = e<sup>−y/2</sup> / √(2πy) ,  s = 간격/D₀, y = Γ<sub>n</sub>⁰/⟨Γ<sub>n</sub>⁰⟩</div>
  <div class="btns"><button class="btn" data-act="more">사다리 열 개 더 뽑기</button></div>
  <p>막대그래프는 지금까지 뽑은 모든 사다리의 간격과 폭을 모은 것이고, 곡선은 두 법칙입니다. 포획 폭은 수백 개 광자 채널의 합이어서 거의 요동하지 않으므로 고정값으로 둡니다.</p>
</div>
<div class="step">
  <h3>열이 봉우리를 번지게 한다</h3>
  <p>표적 원자핵은 움직입니다. 에너지 <i>E</i>인 중성자는 폭 Δ = √(4<i>E</i> <i>kT</i>/<i>A</i>)로 퍼진 상대 에너지로 그들을 만나며, 각 공명은 그 퍼짐을 거쳐 보입니다. 이것이 <b>도플러 넓어짐</b>입니다. 단일 준위의 경우 결과는 로렌츠형과 가우스형을 합성곱한 ψ 함수입니다.</p>
  <div class="formula">σ<sub>γ</sub>(E,T) = σ₀ (Γ<sub>γ</sub>/Γ) ψ(x, ξ) ,  x = 2(E − E<sub>λ</sub>)/Γ ,  ξ = Γ/Δ</div>
  <div class="ctl"><label for="av-t">온도 (K)</label><input id="av-t" type="range" data-bind="TK" min="0" max="3000" step="10" value="300"><output data-show="TK" data-fmt="0"></output></div>
  <p>확대한 공명은 사다리의 가장 낮은 몇 개 가운데 가장 강한 것이며, 점선은 0 K에서의 모양입니다. 열은 봉우리를 낮추고 날개를 넓히며, 포획 봉우리 아래 넓이는 그대로 유지됩니다. 두꺼운 시료에서는 이것이 중립적이지 않습니다. 봉우리는 자기 차폐되고 날개는 그렇지 않으므로, 더 뜨거운 연료가 더 많이 포획합니다. 이것이 원자로의 도플러 되먹임입니다.</p>
</div>
<div class="step">
  <h3>평균은 하우저–페시바흐다</h3>
  <p>많은 공명에 대해 평균하면 포획은 에너지의 매끄러운 함수가 됩니다. 창이 사다리 위를 미끄러지며 그 평균을 그려 나갑니다. 매끄러운 선은 투과 계수 <i>T<sub>n</sub></i> = 2π⟨Γ<sub>n</sub>⟩/<i>D</i>와 <i>T<sub>γ</sub></i> = 2π⟨Γ<sub>γ</sub>⟩/<i>D</i>를 쓴 하우저–페시바흐 값입니다.</p>
  <div class="ctl"><label for="av-w">창 폭 (준위 수)</label><input id="av-w" type="range" data-bind="win" min="2" max="40" step="1" value="12" data-instant><output data-show="win" data-fmt="0"></output></div>
  <div class="btns"><button class="btn ghost" data-act="ladder">다른 사다리</button></div>
  <p>좁은 창은 크게 흩어집니다. 공명 몇 개에 포터–토머스 폭이니까요. 넓은 창은 아래쪽 선, 즉 폭 요동 보정을 넣은 선에 자리 잡습니다. 위쪽 선인 평균의 곱은 여기서 25–47퍼센트 너무 높으며, ⟨Γ<sub>n</sub>⟩이 ⟨Γ<sub>γ</sub>⟩의 1–3배인 약 100 eV에서 1 keV 사이에서 가장 많이 벗어납니다. (p파와 더 많은 열린 채널이 있으면 보정은 더 작습니다.) 포터–토머스 폭을 갖는 중성자 채널 하나와 고정된 포획 폭에서는 보정된 값이 정확합니다. (2π²/k²<i>D</i>) <i>g</i> ⟨Γ<sub>n</sub>Γ<sub>γ</sub>/Γ⟩입니다.</p>
</div>
<div class="step">
  <h3>분해, 비분해, 매끄러움</h3>
  <p>측정이 무엇을 분해할 수 있는지는 에너지 분해능에 달려 있으며, 분해능은 에너지가 올라갈수록 나빠집니다. 선은 기기가 보는 단면적으로, 비행시간 측정에서처럼 <i>E</i><sup>3/2</sup>에 비례해 커지는 분해능으로 넓어져 있습니다. 낮은 에너지에서는 준위가 하나씩 따로 서 있어 그 매개변수를 맞출 수 있습니다. 이것이 분해 공명 영역입니다. 더 위에서는 준위들이 합쳐져 요동하는 띠가 되는데, 그 통계는 알지만 개별 봉우리는 알 수 없습니다. 이것이 비분해 영역으로, 평균 매개변수로 기술하며 자기 차폐에는 뽑은 사다리로 만든 확률표를 씁니다. 그보다 위에서는 하우저–페시바흐와 광학 모형이 이어받습니다.</p>
  <div class="ctl"><label for="av-r">기기 분해능 (상대값)</label><input id="av-r" type="range" data-bind="res" min="0.2" max="3" step="0.05" value="1"><output data-show="res" data-fmt="2"></output></div>
  <p>INCOGNITA의 라이브러리에는 아직 분해 공명 영역이 없습니다. 그 곡선들은 가장 낮은 에너지까지 하우저–페시바흐 평균이며, 측정된 공명이 분해되는 곳에서는 <a href="data.html" data-keep-lang>모든 핵종</a> 페이지가 그 곡선을 평균으로 표시합니다. 공명 매개변수와, 그것으로 만든 도플러 넓어짐을 적용한 점별 단면적은 작업 중입니다.</p>
  <div class="aside">코드에서: <code>physics/resonance/ladder.py</code>(무작위 행렬 간격, 포터–토머스 폭, 단일 준위 단면적, 앙상블), <code>ladder_statistics.py</code>(측정된 사다리로 시험한 법칙들), <code>compound/wfc.py</code>(평균이 수렴하는 폭 요동 보정). 그림의 라이히–무어, ψ–χ, 분해능 공식은 우라늄-238과 비슷한 예시용 매개변수로 여기서 계산한 것이며, 하우저–페시바흐 엔진, 따라서 라이브러리는 아직 공명 영역 단면적을 계산하지 않습니다.</div>
</div>`,
};
(function () {
  const L = {
    "{#} eV": "{#} eV", "{#} keV": "{#} keV", "{#} b": "{#} b",
    // scene 1: R-matrix
    "potential scattering {#}πR′² ≈ {#} b": "퍼텐셜 산란 {#}πR′² ≈ {#} b",
    "Reich–Moore (dashed: single-level)": "라이히–무어 (점선: 단일 준위)",
    "single-level Breit–Wigner (dashed: Reich–Moore)": "단일 준위 브라이트–위그너 (점선: 라이히–무어)",
    "total": "전체", "capture": "포획",
    // scene 2: statistics
    "spacings: Wigner": "간격: 위그너",
    "s = spacing / D₀": "s = 간격 / D₀",
    "reduced neutron widths: Porter–Thomas": "환산 중성자 폭: 포터–토머스",
    "y = Γn⁰ / ⟨Γn⁰⟩": "y = Γn⁰ / ⟨Γn⁰⟩",
    "{#} ladders · {#} spacings": "사다리 {#}개 · 간격 {#}개",
    "s = {#}": "s = {#}",
    // scene 3: Doppler
    "capture near the {#} eV resonance": "{#} eV 공명 근처의 포획",
    "area {#} b·eV ({#} K: {#})": "넓이 {#} b·eV ({#} K: {#})",
    "target nuclei at {#} K": "표적 원자핵 {#} K",
    "target nuclei at rest": "정지한 표적 원자핵",
    // scene 4: averages
    "Hauser–Feshbach, no correction": "하우저–페시바흐, 보정 없음",
    "with width fluctuations": "폭 요동 포함",
    "average capture cross section": "평균 포획 단면적",
    "{#} levels around {#} eV: {#} b · HF {#} b without, {#} b with the correction": "준위 {#}개, {#} eV 근처: {#} b · HF 보정 없이 {#} b, 보정하면 {#} b",
    // scene 5: regions
    "resolved": "분해", "unresolved": "비분해", "averaged": "평균",
    "capture as measured with finite resolution · dashed: Hauser–Feshbach with fluctuations": "유한한 분해능으로 측정한 포획 · 점선: 요동을 넣은 하우저–페시바흐",
    "resolution reaches D₀/{#} at {#} eV": "분해능이 D₀/{#}에 도달: {#} eV",
    "resolution reaches D₀/{#} at {#} keV": "분해능이 D₀/{#}에 도달: {#} keV",
    "time of flight: the arrival time measures the energy": "비행시간: 도착 시간이 에너지를 잰다",
  };
  // axis labels "1 b", "10² b", "10⁻¹ b"
  for (const s of ["⁻³", "⁻²", "⁻¹", "¹", "²", "³", "⁴", "⁵", "⁶"]) L[`{#}${s} b`] = `{#}${s} b`;
  // cross sections print as "12 b" or "3.4k b"
  for (const a of ["{#} b", "{#}k b"]) for (const b of ["{#} b", "{#}k b"]) {
    L[`{#} eV · total ${a} · capture ${b}`] = `{#} eV · 전체 ${a} · 포획 ${b}`;
    L[`Γ = {#} meV · Δ = {#} meV · peak ${a} ({#} K: ${b})`] = `Γ = {#} meV · Δ = {#} meV · 최대 ${a} ({#} K: ${b})`;
  }
  Object.assign(WT.L.labels, L);
})();
Object.assign(WT.L.glossary, {
  rMatrix: {
    term: "R 행렬 이론", aliases: ["R 행렬", "R-행렬", "R-matrix"],
    short: "채널 반지름 안쪽의 준위 에너지와 환산 폭으로 공명 반응을 정확히 기술하고, 바깥쪽의 자유 파동에 접속하는 이론입니다.",
    more: "평가에서는 그 매개변수를 측정된 공명에 맞춥니다. 단일 준위·다준위 브라이트–위그너와 라이히–무어 형태는 완전한 이론의 근사입니다.",
    chapter: "averages",
  },
  reichMoore: {
    term: "라이히–무어", aliases: ["라이히–무어", "라이히-무어", "Reich–Moore"],
    short: "무거운 원자핵 평가 대부분에 쓰이는 R 행렬 근사입니다. 중성자 채널은 정확히 다루고, 많은 광자 채널은 준위마다 흡수 폭 하나로 다룹니다.",
    chapter: "averages",
  },
  doppler: {
    term: "도플러 넓어짐", aliases: ["도플러 넓어짐", "Doppler broadening"],
    short: "표적 원자핵의 열운동 때문에 공명이 번지는 현상입니다. 봉우리는 낮아지고 날개는 넓어지지만, 고립된 봉우리의 넓이는 그대로입니다.",
    formula: "Δ = √(4 E kT / A)",
    chapter: "averages",
  },
  resolvedRegion: {
    term: "분해 공명 영역과 비분해 공명 영역", aliases: ["분해 공명 영역", "비분해 영역", "비분해 공명 영역"],
    short: "어떤 에너지 아래에서는 각 공명을 따로 측정할 수 있고(분해), 그 위에서는 평균 매개변수만 알려져 있습니다(비분해). 더 올라가면 평균이 매끄러워집니다.",
    more: "비분해 영역에서는 자기 차폐를 확률표, 즉 뽑은 공명 사다리로 만든 단면적의 분포로 다룹니다.",
    chapter: "averages",
  },
});
