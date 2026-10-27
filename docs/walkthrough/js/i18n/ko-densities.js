/* Korean: densities (24장, 준위 밀도 접속하기) */
WT.L.ch.densities = {
  num: "24장", title: "준위 밀도, 접속하기", short: "준위 밀도",
  lead: "8장에서는 곧은 널빤지를 비탈에 이어 붙였습니다. 이 장에서는 둘을 식으로 적고, 세어 낸 준위로부터 이음매를 찾는 방법과 이음매가 없을 때 어떤 일이 일어나는지를 보여 줍니다.",
  html: `
<div class="step">
  <h3>껍질 효과가 감쇠하는 페르미 기체</h3>
  <p>엔진의 기본 준위 밀도인 ldmodel 1은 <b>길버트–캐머런</b> 복합형입니다. 높은 에너지에서는 페르미 기체, 그 아래에서는 일정 온도 법칙입니다. 페르미 기체에는 수 하나, 즉 준위 밀도 매개변수 <i>a</i>가 필요한데, 낮은 에너지에서는 이 수가 껍질의 영향을 받습니다. <b>이그나티우크</b>의 형태에서는 껍질 보정 δW가 낮은 들뜸에서 온전히 작용하다가 감쇠율 γ로 사라지므로, 원자핵이 뜨거워지면 <i>a</i>(<i>U</i>)는 매끄러운 값 <i>ã</i>에 다가갑니다.</p>
  <div class="formula">a(U) = ã [1 + δW (1 − e<sup>−γU</sup>) / U] ,  ã = αA + βA<sup>2/3</sup> ,  γ = γ₁ / A<sup>1/3</sup></div>
  <div class="ctl"><label for="ld-dw">껍질 보정 δW (MeV)</label><input id="ld-dw" type="range" data-bind="dW" min="-6" max="4" step="0.1" value="1"><output data-show="dW" data-fmt="1"></output></div>
  <div class="formula">ρ<sub>F</sub>(E) = exp(2√(aU)) / (12√2 σ a<sup>1/4</sup> U<sup>5/4</sup>) ,  U = E − Δ ,  σ² = 0.01389 A<sup>5/3</sup> √(aU) / ã</div>
  <p>위쪽 곡선들은 여러 δW에 대한 <i>a</i>(<i>U</i>)/<i>ã</i>이며, 지금 고른 값은 굵게 그렸습니다. 그 아래는 ln ρ<sub>F</sub>입니다. 음의 δW(닫힌 껍질)는 밀도를 한두 자릿수 억누르며, 이 억눌림은 아주 천천히 사라집니다. <i>a</i>(<i>U</i>)는 δW/<i>U</i>처럼 <i>ã</i>로 돌아가므로, 20 MeV에서도 −6 MeV의 δW는 여전히 약 40배의 차이를 냅니다. Δ는 짝짓기 이동으로, 짝을 이룬 핵자 종류마다 12/√A입니다.</p>
</div>
<div class="step">
  <h3>아래쪽의 접선</h3>
  <p>접속 에너지 <i>E<sub>x</sub></i> 아래에서는 페르미 기체 대신 <b>일정 온도</b> 법칙을 씁니다. 두 조건이 이 법칙의 두 매개변수를 정합니다. <i>E<sub>x</sub></i>에서 값이 같고 기울기가 같아야 하므로, 이 직선은 그 점에서 ln ρ<sub>F</sub>에 그은 접선입니다.</p>
  <div class="formula">ρ<sub>T</sub>(E) = (1/T) e<sup>(E − E₀)/T</sup> ,  1/T = d ln ρ<sub>F</sub>/dE |<sub>E<sub>x</sub></sub> ,  E₀ = E<sub>x</sub> − T ln[T ρ<sub>F</sub>(E<sub>x</sub>)]</div>
  <div class="ctl"><label for="ld-ex">접속 에너지 Eₓ (MeV)</label><input id="ld-ex" type="range" data-bind="Ex" min="4.6" max="14" step="0.05" value="7"><output data-show="Ex" data-fmt="2"></output></div>
  <p><i>E<sub>x</sub></i>를 움직이면 접선이 돌아갑니다. 이음매가 높을수록 <i>T</i>는 높아지고(직선이 완만해짐) <i>E</i>₀는 낮아집니다. 어떤 <i>E<sub>x</sub></i>를 골라도 매끄러운 곡선이 됩니다. 어느 것이 옳은지는 세어 낸 준위가 정합니다.</p>
</div>
<div class="step">
  <h3>세어 낸 준위로 이음매 찾기</h3>
  <p>계단은 <i>E</i> 아래에 있는 알려진 준위의 수를 로그 눈금으로 나타낸 것입니다. 일정 온도 법칙을 적분하면 직선 <i>N</i>(<i>E</i>) = e<sup>(E − E₀)/T</sup> + 상수가 되며, 이 직선은 준위 <i>N<sub>L</sub></i>에서 준위 <i>N<sub>P</sub></i>까지, 즉 준위 도식에서 완전하다고 여겨지는 구간의 개수를 재현해야 합니다. 이것이 미지수 하나 <i>E<sub>x</sub></i>에 대한 방정식 하나입니다.</p>
  <div class="formula">F(E<sub>x</sub>) = e<sup>(E<sub>P</sub>−E₀)/T</sup> − e<sup>(E<sub>L</sub>−E₀)/T</sup> − (N<sub>P</sub> − N<sub>L</sub>) = 0</div>
  <div class="ctl"><label for="ld-ex2">시험 Eₓ (MeV)</label><input id="ld-ex2" type="range" data-bind="Ex" min="4.6" max="14" step="0.05" value="7"><output data-show="Ex" data-fmt="2"></output></div>
  <p>아래 칸이 <i>F</i>입니다. 엔진은 TALYS처럼 한 구간을 100단계로 훑어 부호가 바뀌는 곳을 찾은 다음, 그곳을 이분법으로 좁힙니다. 줄어드는 괄호가 이분법을 보여 줍니다. <i>F</i> = 0인 곳에서 시험 직선이 계단 위에 놓입니다.</p>
</div>
<div class="step">
  <h3>이음매가 없을 때</h3>
  <p>이중으로 닫힌 껍질에서는 낮은 에너지의 페르미 기체가 너무 억눌려 온도가 어디서나 낮게 머물고, <i>F</i>의 부호가 끝내 바뀌지 않습니다. 접속 에너지가 없는 것입니다. 그러면 TALYS는 경험적 온도 <i>T</i> = −0.25 + 10.2/√(<i>A</i>(1 + γδW))를 쓰고, 페르미 기체가 그 온도가 되는 에너지를 찾습니다. 이중으로 닫힌 껍질 근처에서는 페르미 기체가 그 온도에 이르는 곳이 합리적인 이음매보다 훨씬 위이거나 아예 없으므로, 이음매도 계통성 <i>E<sub>x</sub></i> = 2.33 + 253/<i>A</i> + Δ로 물러나고, 값이 연속이 되도록 <i>E</i>₀를 정합니다.</p>
  <div class="btns"><button class="btn ghost" data-act="tang" aria-pressed="false">대체 에너지에서의 접선</button></div>
  <p>값은 연속이지만, 경험적 <i>T</i>는 그 에너지에서의 페르미 기체 온도가 아니므로 기울기가 튑니다. 기본 입력에서는 ²⁰⁵,²⁰⁶Tl, ²⁰⁶⁻²⁰⁹Pb, ²¹⁰Bi에서 이런 일이 일어나며, 기울기가 34–62% 튑니다. 그곳에서 <i>T</i>를 페르미 기체에서 가져오면(입력에 <i>E<sub>x</sub></i>를 줄 때 TALYS가 이미 그렇게 하듯) 접선이 회복되고, 납 영역의 포획이 최대 20–30% 움직입니다. INCOGNITA는 여기서 TALYS를 그대로 재현하며, 이 변경 사항은 TALYS 개발자들에게 보고되었습니다. 그림은 납과 비슷한 원자핵을 예시로 든 것으로, <i>ã</i>를 30% 올려 페르미 기체가 탐색 범위를 넘어 약 24 MeV까지 경험적 온도 아래에 머물게 했습니다. 기울기는 62% 튑니다.</p>
</div>
<div class="step">
  <h3>점검 수단으로서의 간격 D₀</h3>
  <p>중성자 분리 에너지에서는 밀도를 직접 측정할 수 있습니다. s파 공명의 평균 간격 <i>D</i>₀는 느린 중성자가 닿을 수 있는 한 가지 스핀과 반전성의 상태를 셉니다. 스핀 0인 표적이라면 <i>J</i><sup>π</sup> = ½⁺ 하나뿐입니다.</p>
  <div class="formula">1/D₀ = ρ(S<sub>n</sub>, ½, +) = ½ ρ<sub>F</sub>(S<sub>n</sub>) · (2J+1)/(2σ²) · e<sup>−(J+½)²/2σ²</sup></div>
  <div class="ctl"><label for="ld-as">ã에 곱하는 배율</label><input id="ld-as" type="range" data-bind="as" min="0.8" max="1.2" step="0.005" value="1"><output data-show="as" data-fmt="3"></output></div>
  <p>그림은 전역 <i>ã</i>를 쓴 철-57과 비슷한 복합핵의 경우로, 측정값 25.4 ± 2.2 keV와 비교합니다. <i>ã</i>를 몇 퍼센트만 바꿔도 <i>D</i>₀는 수십 퍼센트 움직이므로, <i>D</i>₀가 측정된 곳에서는 <i>S<sub>n</sub></i>에서의 밀도가 잘 고정되고, 측정되지 않은 곳에서는 이것이 포획에서 가장 큰 단일 불확도가 됩니다. 평가에서는 <i>a</i>를 <i>D</i>₀에 맞춰 조정하며, 엔진이 따르는 TALYS의 기본값도 그렇게 합니다. <i>D</i>₀가 측정된 원자핵에서는 그에 맞춘 준위 밀도 매개변수를 읽어 들이고, 전역 공식은 나머지 원자핵에만 씁니다.</p>
  <div class="aside">코드에서: <code>density/parameters.py</code>(ã, 이그나티우크 감쇠, 짝짓기, 스핀 차단), <code>density/models.py</code>(페르미 기체, 일정 온도, 표), <code>density/matching.py</code>(접속 근, 경험적 대체값, TALYS 고유의 단정밀도 세부 사항까지 재현). 그림은 ldmodel 1에 대한 TALYS의 전역 매개변수를 쓰고, 준위 도식과 껍질 보정은 예시용입니다(납과 비슷한 경우에는 <i>ã</i> × 1.3). 측정된 <i>D</i>₀는 ⁵⁷Fe에 대한 RIPL 값입니다.</div>
</div>`,
};
(function () {
  const L = {
    // scene 1: a(U) and rho_F
    "a(U) / ã": "a(U) / ã",
    "U (MeV)": "U (MeV)",
    "E (MeV)": "E (MeV)",
    "U = {#} MeV · a = {#} MeV⁻¹ · T ≈ √(U/a) = {#} MeV": "U = {#} MeV · a = {#} MeV⁻¹ · T ≈ √(U/a) = {#} MeV",
    "ρ_F (states per MeV), A = {#}": "ρ_F (MeV당 상태 수), A = {#}",
    "dashed: δW = {#}": "점선: δW = {#}",
    "at {#} MeV: ×{#} against δW = {#}": "{#} MeV에서: ×{#} (δW = {#} 대비)",
    "at {#} MeV: ×{#}e{#} against δW = {#}": "{#} MeV에서: ×{#}e{#} (δW = {#} 대비)",
    // scene 2: tangent
    "T = {#} MeV": "T = {#} MeV",
    "× e": "× e",
    "joint Eₓ = {#} MeV": "이음매 Eₓ = {#} MeV",
    "E₀ = {#} MeV": "E₀ = {#} MeV",
    "Fermi gas": "페르미 기체",
    "constant temperature": "일정 온도",
    "ln ρ (states per MeV), A = {#}": "ln ρ (MeV당 상태 수), A = {#}",
    // scene 3: matching
    "levels {#}–{#}": "준위 {#}–{#}",
    "levels {#} to {#}: taken as complete": "준위 {#}–{#}: 완전하다고 간주",
    "number of levels below E": "E 아래의 준위 수",
    "trial Eₓ = {#} MeV: the line gives {#} levels for {#} counted": "시험 Eₓ = {#} MeV: 직선은 준위 {#}개, 센 것은 {#}개",
    "F = {#}": "F = {#}",
    "Eₓ (MeV)": "Eₓ (MeV)",
    "F(Eₓ): predicted minus counted (signed log scale)": "F(Eₓ): 예측 빼기 셈 (부호 있는 로그 눈금)",
    "bisection step {#}: [{#}, {#}]": "이분법 {#}단계: [{#}, {#}]",
    "root Eₓ = {#} MeV": "근 Eₓ = {#} MeV",
    // scene 4: no joint
    "below: {#}/T with T = {#} MeV (Fermi-gas T)": "아래: {#}/T, T = {#} MeV (페르미 기체 T)",
    "below: {#}/T with T = {#} MeV (empirical T)": "아래: {#}/T, T = {#} MeV (경험적 T)",
    "above: Fermi gas, T = {#} MeV": "위: 페르미 기체, T = {#} MeV",
    "slope jumps by {#} % at Eₓ = {#} MeV": "기울기가 {#}% 튐 (Eₓ = {#} MeV)",
    "tangent at Eₓ = {#} MeV: no jump": "Eₓ = {#} MeV에서 접선: 튐 없음",
    "ln ρ, lead-like nucleus (A = {#}, δW = {#} MeV)": "ln ρ, 납과 비슷한 원자핵 (A = {#}, δW = {#} MeV)",
    "F changes sign: a root exists": "F의 부호가 바뀜: 근이 있음",
    "F(Eₓ) never reaches zero: no matching energy": "F(Eₓ)가 0에 닿지 않음: 접속 에너지 없음",
    // scene 5: D0
    "{#} keV": "{#} keV",
    "measured {#} ± {#} keV": "측정값 {#} ± {#} keV",
    "computed D₀ = {#} keV": "계산된 D₀ = {#} keV",
    "ã × {#} = {#} MeV⁻¹ · σ² = {#} · ρ(Sₙ) = {#} per MeV": "ã × {#} = {#} MeV⁻¹ · σ² = {#} · ρ(Sₙ) = MeV당 {#}",
    "ã × {#} = {#} MeV⁻¹ · σ² = {#} · ρ(Sₙ) = {#}e{#} per MeV": "ã × {#} = {#} MeV⁻¹ · σ² = {#} · ρ(Sₙ) = MeV당 {#}e{#}",
    "s-wave resonances above Sₙ, {#} keV shown: about {#} levels": "Sₙ 위의 s파 공명, {#} keV 구간 표시: 준위 약 {#}개",
    "iron{#}-like compound nucleus, Sₙ = {#} MeV, spin and parity ½⁺": "철{#}과 비슷한 복합핵, Sₙ = {#} MeV, 스핀·반전성 ½⁺",
  };
  Object.assign(WT.L.labels, L);
})();
Object.assign(WT.L.glossary, {
  gilbertCameron: {
    term: "길버트–캐머런", aliases: ["길버트–캐머런", "길버트-캐머런", "Gilbert–Cameron"],
    short: "복합형 준위 밀도입니다. 낮은 에너지의 일정 온도 법칙을 접속 에너지 위의 페르미 기체에 이어 붙이며, 이음매에서 값과 기울기가 같습니다.",
    more: "1965년 A. 길버트(Gilbert)와 A. G. W. 캐머런(Cameron)이 제안했습니다. 이그나티우크의 에너지 의존 준위 밀도 매개변수와 함께 TALYS와 이 엔진의 기본값(ldmodel 1)입니다.",
    chapter: "densities",
  },
  ignatyuk: {
    term: "이그나티우크", aliases: ["이그나티우크", "Ignatyuk"],
    short: "이그나티우크(Ignatyuk) 형태의 준위 밀도 매개변수입니다. 껍질 보정이 낮은 들뜸에서 온전히 작용하다가 에너지가 높아지면 사라지므로, a(U)는 매끄러운 값에 다가갑니다.",
    formula: "a(U) = ã [1 + δW (1 − e^(−γU)) / U]",
    chapter: "densities",
  },
});
