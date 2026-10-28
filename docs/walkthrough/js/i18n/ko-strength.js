/* Korean: strength (25장, 광자 세기 자세히 보기) */
WT.L.ch.strength = {
  num: "25장", title: "광자 세기, 자세히", short: "광자 세기",
  lead: "10장에서는 뜨거운 원자핵이 어떤 광자를 선호하는지 보았습니다. 이 장에서는 세기 함수를 식으로 적고, 그것이 투과 계수와 평균 복사 폭으로 이어지는 과정을 따라간 뒤, 그 세기 함수가 이끄는 캐스케이드를 직접 돌려 봅니다.",
  html: `
<div class="step">
  <h3>E1: 거대 쌍극자 공명의 꼬리</h3>
  <p><b>광자 세기 함수</b> <i>f<sub>XL</sub></i>(<i>E</i><sub>γ</sub>)는 유형 <i>XL</i>(전기 쌍극자 E1, 자기 쌍극자 M1 등)인 광자의 평균 환산 확률입니다. E1에서는 18 MeV 근처의 거대 쌍극자 공명이 지배적이지만, <i>S<sub>n</sub></i>에서의 붕괴는 그 꼬리 한참 아래인 1–7 MeV의 광자를 쓰므로, 꼬리의 모양이 문제의 전부입니다.</p>
  <div class="formula">f<sub>E1</sub> = K σ₀Γ₀ · E<sub>γ</sub> Γ(E<sub>γ</sub>,T) / [(E<sub>γ</sub>² − E₀²)² + E<sub>γ</sub>² Γ(E<sub>γ</sub>,T)²] / (1 − e<sup>−E<sub>γ</sub>/T</sup>) ,  Γ(E<sub>γ</sub>,T) = (Γ₀/E₀)(E<sub>γ</sub> + 4π²T²/E₀)</div>
  <div class="ctl"><label for="ps-t">나중 상태의 온도 T (MeV)</label><input id="ps-t" type="range" data-bind="T" min="0" max="1.5" step="0.01" value="0.7"><output data-show="T" data-fmt="2"></output></div>
  <p>점선은 광흡수에 맞춘 모양인 표준 로렌츠형(SLO)입니다. 폭이 일정하기 때문에 붕괴 창에서 세기를 2–5배 과대평가하며, 이는 구형 원자핵에서 오래전부터 알려진 실패입니다. 실선은 단순화된 수정 로렌츠형(<b>SMLO</b>)입니다. 폭이 광자 에너지와 나중 상태의 온도에 따라 커지므로 창 안의 꼬리는 낮아지지만, 붕괴 데이터가 요구하듯 광자 에너지 0에서도 유한한 세기가 남습니다. <i>T</i>를 0으로 끌어내리면 그 낮은 에너지의 바닥이 사라집니다.</p>
</div>
<div class="step">
  <h3>M1: 스핀 뒤집기, 가위, 상향 굴곡</h3>
  <p>M1 세기는 더 약하지만 무시할 수는 없습니다. 41<i>A</i><sup>−1/3</sup> MeV 근처의 스핀 뒤집기 공명, 변형된 원자핵에서 3 MeV 근처에 나타나는 가위 모드(세기가 β²에 비례해 커짐), 그리고 오슬로 방법 데이터와 껍질 모형 계산에서 보이는, 광자 에너지 0 쪽으로 솟아오르는 상향 굴곡이 있습니다.</p>
  <div class="ctl"><label for="ps-b">변형 β (가위 모드)</label><input id="ps-b" type="range" data-bind="beta" min="0" max="0.35" step="0.01" value="0.2"><output data-show="beta" data-fmt="2"></output></div>
  <div class="btns"><button class="btn ghost" data-act="up" aria-pressed="true">상향 굴곡</button></div>
  <p>뒤쪽의 흐린 선은 E1입니다. 가장 낮은 광자 에너지, 여기서는 약 2 MeV 아래에서는 상향 굴곡 덕분에 M1이 E1에 맞먹거나 넘어설 수 있으며(표시가 그 위치를 보여 줌), 그래서 M1은 캐스케이드의 부드러운 끝과 안정성에서 먼 원자핵의 포획에 중요합니다. 엔진의 기본 M1은 상향 굴곡을 포함한 IAEA 권고값으로 원자핵마다 표로 주어지고, 기본 E1은 표로 된 SMLO-2019입니다. 여기의 닫힌 형태 식은 그 표들을 대신하는 것입니다.</p>
</div>
<div class="step">
  <h3>브링크–액셀</h3>
  <p><b>브링크–액셀 가설</b>은 세기가 광자 에너지에만 의존하고 원자핵이 어디서 출발하는지에는 의존하지 않는다는 것입니다. <i>S<sub>n</sub></i>의 공명에도, 4 MeV의 상태에도 같은 <i>f</i>가 적용됩니다(SMLO는 <i>T</i>를 통해 약한 의존성을 남깁니다). 그러면 각 출발 에너지는 투과 계수 곱하기 나중 상태의 밀도로 광자를 내보냅니다.</p>
  <div class="formula">T<sub>XL</sub>(E<sub>γ</sub>) = 2π E<sub>γ</sub><sup>2L+1</sup> f<sub>XL</sub>(E<sub>γ</sub>) ,  dΓ/dE<sub>γ</sub> ∝ T<sub>XL</sub>(E<sub>γ</sub>) ρ(E<sub>x</sub> − E<sub>γ</sub>)</div>
  <div class="ctl"><label for="ps-x">출발 에너지 Eₓ (MeV)</label><input id="ps-x" type="range" data-bind="Ex" min="2" max="7.6" step="0.05" value="7.6"><output data-show="Ex" data-fmt="2"></output></div>
  <p>커지는 <i>E</i><sub>γ</sub>³<i>f</i>와 줄어드는 ρ의 곱이 언덕을 만듭니다. <i>S<sub>n</sub></i>에서 출발하면 여기서는 4–5 MeV 근처에서 최대가 됩니다. 더 낮은 곳에서 출발하면 출발 에너지에서 잘립니다. ρ가 일정 온도 지수 함수인 접속 에너지 아래에서는 어디서 출발하든 모양이 같고 잘리기만 합니다. 서로 다른 들뜸 에너지에서 추출한 세기를 비교하면 이 가설을 시험할 수 있으며, 오슬로형 분석이 바로 그렇게 합니다.</p>
</div>
<div class="step">
  <h3>평균 복사 폭</h3>
  <p>s파 공명(스핀 0 표적에서 <i>J</i><sup>π</sup> = ½⁺)에서 E1이나 M1으로 닿을 수 있는 모든 나중 상태에 대해 합하면, 그 공명들의 평균 전체 광자 폭이 나옵니다. 이 값은 공명 모양으로부터 수백 개 원자핵에서 측정되었으며, <i>S<sub>n</sub></i>에서의 세기를 점검하는 주된 수단입니다.</p>
  <div class="formula">⟨Γ<sub>γ</sub>⟩ = D₀/2π · Σ<sub>XL</sub> Σ<sub>J′π′</sub> ∫₀^{S<sub>n</sub>} T<sub>XL</sub>(E<sub>γ</sub>) ρ(S<sub>n</sub> − E<sub>γ</sub>, J′, π′) dE<sub>γ</sub></div>
  <div class="ctl"><label for="ps-s">세기에 곱하는 배율</label><input id="ps-s" type="range" data-bind="scale" min="0.3" max="8" step="0.01" value="1"><output data-show="scale" data-fmt="2"></output></div>
  <p>곡선은 폭이 어디서 오는지를 광자별로 보여 줍니다. 대부분 3–7 MeV이고 대부분 E1이며, M1이 약 15%를 더합니다. 여기서는 엔진의 표 대신 닫힌 형태 식과 도식적인 준위 밀도를 썼기 때문에 폭이 측정값 0.92 eV의 약 6분의 1로 나옵니다. 폭은 <i>S<sub>n</sub></i> 아래의 준위 밀도와 세기의 꼬리에 그만큼 민감합니다. 엔진이 따르는 TALYS의 기본값은 이 원자핵에 대해 약 1.3 eV를 줍니다. 슬라이더는 평가에서 맞출 법한 전체 배율 하나를 적용합니다. Γ<sub>γ</sub> ≪ Γ<sub>n</sub>일 때 keV 영역의 포획은 ⟨Γ<sub>γ</sub>⟩에 거의 비례하므로, 여기서의 배율은 곧 (n,γ)의 배율입니다. TALYS는 세기를 측정된 ⟨Γ<sub>γ</sub>⟩에 맞춰 다시 조정할 수 있습니다(<code>gnorm</code>). INCOGNITA에서는 캐스케이드의 모든 원자핵에 적용되는 이 재조정이 선택 스위치이며, 기본으로 꺼져 있습니다.</p>
</div>
<div class="step">
  <h3>캐스케이드</h3>
  <p>첫 광자 아래에서도 같은 규칙이 되풀이됩니다. 새 에너지마다 다음 광자를 <i>T</i>(<i>E</i><sub>γ</sub>) ρ(<i>E<sub>x</sub></i> − <i>E</i><sub>γ</sub>)에서 뽑고, 원자핵이 알려진 준위에 닿을 때까지 계속합니다. 이력 하나는 광자 몇 개로 이루어지며, 이들을 합한 스펙트럼이 포획 뒤에 열량계가 보는 것입니다.</p>
  <div class="btns"><button class="btn ghost" data-act="up2" aria-pressed="true">상향 굴곡</button><button class="btn ghost" data-act="clear">다시 시작</button></div>
  <p>상향 굴곡은 부드러운 광자를 더하고 다중도를 조금 늘립니다. 엔진은 이력을 뽑지 않습니다. 개체군을 구간별로 위에서 아래로 옮기며(11장), 표본 잡음 없이 같은 평균을 얻습니다.</p>
  <div class="aside">코드에서: <code>gamma/strength.py</code>(TALYS가 지원하는 모든 세기 모형. 기본값은 SMLO-2019 표와 상향 굴곡을 포함한 IAEA M1), <code>gamma/parameters.py</code>(거대 공명 계통성, 표), <code>gamma/transmission.py</code>(T = 2π E<sup>2L+1</sup> f), <code>gamma/ggnorm.py</code>(선택 사항: ⟨Γγ⟩ 규격화), <code>emission/</code>(캐스케이드). 그림은 철-57과 비슷한 원자핵에 대해 닫힌 형태 식과 계통성을 씁니다. 측정된 ⟨Γγ⟩는 ⁵⁷Fe에 대한 RIPL 값입니다.</div>
</div>`,
};
(function () {
  const L = {
    "Eγ (MeV)": "Eγ (MeV)",
    // scene 1: E1
    "E{#} strength f (MeV⁻³), A = {#}": "E{#} 세기 f (MeV⁻³), A = {#}",
    "photons that decay uses": "붕괴에 쓰이는 광자",
    "GDR: E₀ = {#} MeV, Γ₀ = {#} MeV, σ₀ = {#} mb": "GDR: E₀ = {#} MeV, Γ₀ = {#} MeV, σ₀ = {#} mb",
    "dashed: SLO": "점선: SLO",
    "at {#} MeV: SMLO / SLO = {#}": "{#} MeV에서: SMLO / SLO = {#}",
    "protons against neutrons": "양성자 대 중성자",
    // scene 2: M1
    "M{#} strength f (MeV⁻³), A = {#}": "M{#} 세기 f (MeV⁻³), A = {#}",
    "spin-flip": "스핀 뒤집기",
    "scissors, β = {#}": "가위 모드, β = {#}",
    "upbend": "상향 굴곡",
    "faint: E{#} at T = {#} MeV": "흐린 선: E{#} (T = {#} MeV)",
    "M{#} > E{#} below {#} MeV": "M{#} > E{#}: {#} MeV 아래",
    "E{#} dominates at every energy here": "여기서는 모든 에너지에서 E{#}이 우세",
    "scissors: the two deformed clouds rock": "가위 모드: 변형된 두 구름이 흔들림",
    // scene 3: Brink-Axel
    "from {#} MeV": "{#} MeV에서 출발",
    "peak at Eγ ≈ {#} MeV": "최대 Eγ ≈ {#} MeV",
    "primary spectrum T(Eγ) ρ(Eₓ − Eγ), each scaled to its peak": "1차 스펙트럼 T(Eγ) ρ(Eₓ − Eγ), 각각 최댓값으로 규격화",
    // scene 4: <Gamma_gamma>
    "contribution to ⟨Γγ⟩ per MeV of photon energy: E{#} (yellow), M{#} (purple, on top)": "광자 에너지 MeV당 ⟨Γγ⟩ 기여: E{#} (노랑), M{#} (보라, 위에 쌓음)",
    "{#} eV": "{#} eV",
    "measured {#} eV": "측정값 {#} eV",
    "computed ⟨Γγ⟩ = {#} meV (E{#} {#} %, M{#} {#} %)": "계산된 ⟨Γγ⟩ = {#} meV (E{#} {#}%, M{#} {#}%)",
    // scene 5: cascade
    "Sₙ": "Sₙ",
    "all photons from all cascades": "모든 캐스케이드의 모든 광자",
    "{#} cascades · mean multiplicity {#}": "캐스케이드 {#}개 · 평균 다중도 {#}",
  };
  Object.assign(WT.L.labels, L);
})();
Object.assign(WT.L.glossary, {
  smlo: {
    term: "SMLO", aliases: ["SMLO"],
    short: "단순화된 수정 로렌츠형(simplified modified Lorentzian)으로, 폭이 광자 에너지와 나중 상태의 온도에 따라 커지는 E1 세기 함수입니다.",
    more: "V. 플류코(Plujko)와 동료들이 제안했고, IAEA 광자 세기 함수 데이터베이스(2019)에 모든 원자핵에 대해 표로 실려 있습니다. 엔진의 기본 E1은 TALYS-2와 마찬가지로 이 SMLO-2019 표입니다.",
    chapter: "strength",
  },
  brinkAxel: {
    term: "브링크–액셀 가설", aliases: ["브링크–액셀 가설", "브링크–액셀", "브링크-액셀", "Brink–Axel"],
    short: "광자 세기 함수가 광자 에너지에만 의존하고, 광자를 내보내는 상태의 들뜸 에너지에는 의존하지 않는다는 가정입니다.",
    more: "덕분에 바닥 상태에 대해 측정하거나 계산한 세기 하나로 캐스케이드 전체를 다룰 수 있습니다. 서로 다른 들뜸 에너지에서 세기를 추출해 시험하며, 대체로 성립하지만 특정 원자핵과 에너지에서의 벗어남은 논쟁 중입니다.",
    chapter: "strength",
  },
});
