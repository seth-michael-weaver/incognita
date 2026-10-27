/* Korean: hauser (16장, 채널별 하우저–페시바흐와 폭 요동) */
WT.L.ch.hauser = {
  num: "16장", title: "채널 하나하나의 하우저–페시바흐", short: "하우저–페시바흐",
  lead: "6장에서는 출구 사이의 경쟁을 문으로 이야기했습니다. 여기서는 그 문 뒤에 있는 공식을 채널 하나씩 살펴보고, 열린 채널이 몇 개뿐일 때 공식에 필요한 보정을 다룹니다.",
  html: `
<div class="step">
  <h3>채널마다 투과 계수 하나</h3>
  <p><b>채널</b>은 완전한 출구 주소입니다. 어떤 입자인지, 잔류핵이 어떤 상태에 남는지, 그리고 그 입자의 궤도 각운동량 <i>l</i>과 전체 각운동량 <i>j</i> = <i>l</i> ± ½까지 정합니다. 2장의 광학 모형은 각 채널에 <b>투과 계수</b> <i>T<sub>lj</sub></i>를 하나씩 줍니다. 기둥들은 스핀 0인 표적에 들어오는 입사 중성자의 것입니다.</p>
  <div class="ctl"><label for="hf-e">중성자 에너지 (MeV)</label><input id="hf-e" type="range" data-bind="lgE" min="-3" max="0.7" step="0.01" value="-0.3"><output data-show="Eshow" data-fmt="3"></output></div>
  <p>1 keV에서는 <i>l</i> = 0만 열려 있고, <i>T</i> ≈ 2π<i>S</i><sub>0</sub>√<i>E</i>로 몇 퍼센트에 불과합니다. 낮은 에너지에서는 <i>l</i>이 하나 늘 때마다 대략 (<i>kR</i>)²배만큼 작아지므로, 에너지가 올라감에 따라 기둥이 하나씩 열립니다. 각 기둥은 g<sub>J</sub><i>T</i>의 가중치로 복합핵을 채웁니다.</p>
  <div class="formula">σ<sub>CN</sub> = (π/k²) Σ<sub>J,π</sub> g<sub>J</sub> Σ<sub>lj</sub> T<sub>lj</sub> ,  g<sub>J</sub> = (2J+1) / [(2s+1)(2I+1)]</div>
</div>
<div class="step">
  <h3>스핀과 반전성을 하나씩</h3>
  <p>각운동량과 반전성은 보존되므로, 복합핵은 각 <i>J</i><sup>π</sup>에서 서로 독립적으로 붕괴합니다. 한 블록 안에서는 열린 출구 채널이 모두 자기 <i>T</i>를 가지고 경쟁합니다. 바닥 상태로 돌아가는 탄성, 각 들뜬 준위로 가는 비탄성(기둥 하나는 같은 <i>J</i>에 결합하는 (<i>l</i>, <i>j</i>)를 합한 것), 3.6 MeV 위의 연속 영역(각 구간이 준위 밀도로 가중된 여러 채널로 셈해짐), 그리고 아주 작은 <i>T</i><sub>γ</sub> = 2π⟨Γ<sub>γ</sub>⟩/<i>D</i> 하나로 묶은 포획입니다. 높이는 로그 눈금입니다.</p>
  <div class="ctl"><label for="hf-j">스핀·반전성 블록</label><input id="hf-j" type="range" data-bind="jb" min="0" max="9" step="1" value="2" data-instant><output data-show="jbShow" data-fmt="0"></output></div>
  <div class="ctl"><label for="hf-e2">중성자 에너지 (MeV)</label><input id="hf-e2" type="range" data-bind="lgE" min="-3" max="0.7" step="0.01" value="-0.3"><output data-show="Eshow" data-fmt="3"></output></div>
  <p>아래쪽 막대가 <b>하우저–페시바흐</b> 분배입니다. 각 출구는 채널 <i>a</i>로 들어온 것 가운데 <i>T<sub>b</sub></i>/Σ<i>T<sub>c</sub></i>의 몫을 가져갑니다. 0.85 MeV 아래에서는 탄성과 포획만 열려 있고, 탄성이 거의 전부를 가져갑니다.</p>
  <div class="formula">σ<sub>ab</sub> = (π/k²) Σ<sub>J,π</sub> g<sub>J</sub> T<sub>a</sub> T<sub>b</sub> / Σ<sub>c</sub> T<sub>c</sub> · W<sub>ab</sub></div>
</div>
<div class="step">
  <h3>폭 요동</h3>
  <p><i>W<sub>ab</sub></i> = 1이면 이 공식은 평균끼리 곱합니다. 평균 뒤에 있는 공명들의 폭은 제각각 흩어져 있고(포터–토머스, 10장), 탄성 산란에서는 중성자를 들여보내는 폭과 내보내는 폭이 같은 폭이므로 둘은 상관되어 있습니다. 그래서 탄성에서는 곱의 평균이 평균의 곱보다 커지고, 탄성이 얻는 만큼 다른 출구가 잃습니다.</p>
  <div class="btns"><button class="btn ghost" data-act="w0" aria-pressed="false">보정 없음</button><button class="btn ghost" data-act="w1" aria-pressed="true">몰다우어</button></div>
  <div class="ctl"><label for="hf-e3">중성자 에너지 (MeV)</label><input id="hf-e3" type="range" data-bind="lgE" min="-3" max="0.7" step="0.01" value="-0.3"><output data-show="Eshow" data-fmt="3"></output></div>
  <p>표지는 보정한 σ를 보정하지 않은 σ로 나눈 값입니다. 첫 비탄성 문턱 아래에서는 탄성이 이미 선속을 거의 다 가져가므로 거의 변하지 않고, 포획은 10–25퍼센트를 잃습니다. 1–1.5 MeV에서는 복합핵 탄성이 15–35퍼센트를 얻고, 첫 2⁺ 준위는 약 3분의 1을 잃습니다. 더 많은 준위와 연속 영역이 열리면 복합핵 탄성은 선속의 작은 몫이 됩니다. 그 자신의 인자는 2 쪽으로 올라가지만 다른 출구에서 가져가는 양이 줄어들어, 그들의 인자는 1 쪽으로 돌아갑니다. 몰다우어의 처방에서는 각 채널이 자유도 ν<sub>c</sub>를 하나씩 받고, <i>W</i>는 1차원 적분으로, TALYS의 32점 가우스–라게르 구적법으로 계산합니다.</p>
  <div class="formula">W<sub>ab</sub> = (1 + 2δ<sub>ab</sub>/ν<sub>a</sub>) ∫₀^∞ dx Π<sub>c</sub> (1 + 2T<sub>c</sub>x / ν<sub>c</sub>ΣT)<sup>−(δ<sub>ac</sub>+δ<sub>bc</sub>+ν<sub>c</sub>/2)</sup></div>
  <div class="formula">ν<sub>c</sub> = 1.78 + (T<sub>c</sub><sup>1.212</sup> − 0.78) e<sup>−0.228 ΣT</sup></div>
</div>
<div class="step">
  <h3>몰다우어와 HRTW</h3>
  <p>곡선들은 같은 계산을 에너지 범위 전체에 걸쳐 수행한 것입니다. 복합핵 탄성, 첫 2⁺ 준위, 포획에 대한 비를 몰다우어는 실선으로, <b>HRTW</b> 처방은 점선으로 그렸습니다. HRTW는 적분 대신 탄성 인자 <i>W<sub>a</sub></i>와 반복법으로 구한 유효 투과 계수 <i>V<sub>a</sub></i>를 씁니다.</p>
  <div class="ctl"><label for="hf-e4">중성자 에너지 (MeV)</label><input id="hf-e4" type="range" data-bind="lgE" min="-3" max="0.7" step="0.01" value="-0.3"><output data-show="Eshow" data-fmt="3"></output></div>
  <div class="formula">σ<sub>ab</sub> ∝ V<sub>a</sub>V<sub>b</sub> / ΣV<sub>c</sub> · [1 + δ<sub>ab</sub>(W<sub>a</sub> − 1)] ,  V<sub>a</sub> = T<sub>a</sub> / [1 + (W<sub>a</sub> − 1) V<sub>a</sub>/ΣV]</div>
  <p>탄성과 비탄성에서는 둘이 잘 일치합니다. keV 영역의 포획에서는 HRTW가 최대 10퍼센트를 더 깎습니다. 0.85–2 MeV 사이에서는 포획이 오히려 늘어납니다. 그곳에서는 전체 폭을 요동하는 몇 개의 중성자 폭이 좌우하므로 1/Γ의 평균이 1/⟨Γ⟩보다 커지기 때문입니다. 두 처방 모두 정확한 무작위 행렬(GOE) 결과에 맞춘 근사식이며, TALYS는 이 정확한 결과도 3중 적분으로 제공합니다. INCOGNITA는 셋을 모두 이식했습니다(<code>widthmode</code> 1, 2, 3). 기본값은 몰다우어이며, 입사 중성자 에너지가 표적의 중성자 분리 에너지 이하일 때 적용됩니다.</p>
</div>
<div class="step">
  <h3>3과 2 사이</h3>
  <p>극한을 보면 효과의 크기를 이해할 수 있습니다. 포획 없이 똑같은 채널 <i>N</i>개를 두고, 그 합 ΣT를 바꿔 봅니다. ΣT는 평균 전체 폭과 준위 간격의 비 Γ/<i>D</i>의 2π배입니다. 공명이 고립되어 있고(ΣT ≪ 1) 채널이 많으면 각 폭은 자유도 1의 포터–토머스 분포를 따르고, 탄성 증강은 ⟨Γ<sub>a</sub>²⟩/⟨Γ<sub>a</sub>⟩² = 3입니다. 공명이 크게 겹치면(ΣT ≫ 2π) 단면적은 무작위 파동처럼 요동하고(에릭슨 요동), 증강은 2로 떨어집니다.</p>
  <div class="ctl"><label for="hf-n">열린 채널 N</label><input id="hf-n" type="range" data-bind="nch" min="2" max="60" step="1" value="30" data-instant><output data-show="nch" data-fmt="0"></output></div>
  <p>고립된 채널 <i>N</i>개에 대한 정확한 값은 3<i>N</i>/(<i>N</i>+2)(마름모)입니다. 채널이 두 개뿐이면 전체 폭도 탄성 폭만큼 요동하므로 증강은 1.5를 넘을 수 없습니다. 몰다우어의 처방은 이 극한을 재현하지만, HRTW는 약한 채널이 많이 열려 있을 때 이에 못 미칩니다. 삽입 그림은 움직이는 점에 해당하는 폭으로 공명을 그립니다. 몰다우어의 공식에서 채널이 많을 때의 극한은 1 + 2/ν이고, 고립된 공명에서는 ν → 1, 겹칠 때는 ν → 1.78입니다(2.12는 완전히 겹칠 때 근사식이 내는 작은 오차입니다).</p>
  <div class="aside">코드에서: <code>compound/prepare.py</code>(<i>J</i><sup>π</sup>별 출구 채널과 그 투과 계수), <code>compound/target.py</code>(하우저–페시바흐 합), <code>compound/wfc.py</code>(TALYS에서 이식한 몰다우어, HRTW, GOE). 그림은 같은 공식을 예시용 재료로 계산합니다. 철과 비슷한 표적에 대한 강체구 투과 계수, 준위 일곱 개, 일정 온도 연속 영역, 하나로 묶은 포획 채널입니다.</div>
</div>`,
};
(function () {
  const L = {
    // scene 1: incident T_lj
    "T = {#}": "T = {#}",
    "l={#}": "l={#}",
    "hollow: j = l − ½ · solid: j = l + ½": "속 빈 것: j = l − ½ · 속 찬 것: j = l + ½",
    "compound nucleus": "복합핵",
    "compound nucleus · σ(CN) ≈ {#} b": "복합핵 · σ(CN) ≈ {#} b",
    "σ(CN) ≈ {#} b": "σ(CN) ≈ {#} b",
    "E = {#} MeV · kR = {#}": "E = {#} MeV · kR = {#}",
    "E = {#} keV · kR = {#}": "E = {#} keV · kR = {#}",
    "transmission Tₗⱼ of the incident neutron": "입사 중성자의 투과 계수 Tₗⱼ",
    // scene 2: one J^pi block
    "elastic": "탄성", "cont.": "연속",
    "level energy (MeV) under each column": "기둥 아래: 준위 에너지 (MeV)",
    "residual level (energy in MeV) · n×: number of (l, j) channels summed": "잔류핵 준위 (에너지, MeV) · n×: 합한 (l, j) 채널 수",
    "{#}/{#}⁺ block · in through l = {#}, Tₐ = {#}": "{#}/{#}⁺ 블록 · 입사 l = {#}, Tₐ = {#}",
    "{#}/{#}⁻ block · in through l = {#}, Tₐ = {#}": "{#}/{#}⁻ 블록 · 입사 l = {#}, Tₐ = {#}",
    "elastic {#} %": "탄성 {#}%", "higher {#} %": "높은 준위 {#}%",
    "Hauser–Feshbach split: T / ΣT for each exit": "하우저–페시바흐 분배: 출구마다 T / ΣT",
    // scene 3: HF vs WFC
    "closed": "닫힘",
    "compound elastic": "복합핵 탄성", "first {#}⁺ level": "첫 {#}⁺ 준위",
    "higher levels": "높은 준위", "capture": "포획",
    "{#} mb": "{#} mb",
    "with Moldauer's correction": "몰다우어 보정 적용",
    "Hauser–Feshbach without correction": "보정 없는 하우저–페시바흐",
    "compound formation {#} mb at {#} MeV": "복합핵 형성 {#} mb ({#} MeV)",
    "compound formation {#} mb at {#} keV": "복합핵 형성 {#} mb ({#} keV)",
    // scene 4: ratio curves
    "{#} keV": "{#} keV", "{#} MeV": "{#} MeV",
    "{#}⁺ opens": "{#}⁺ 열림", "continuum": "연속 영역", "continuum opens": "연속 영역 열림",
    "elastic ×{#} (Moldauer) · ×{#} (HRTW)": "탄성 ×{#} (몰다우어) · ×{#} (HRTW)",
    "capture ×{#} (Moldauer) · ×{#} (HRTW)": "포획 ×{#} (몰다우어) · ×{#} (HRTW)",
    "first {#}⁺ ×{#} (Moldauer) · ×{#} (HRTW)": "첫 {#}⁺ ×{#} (몰다우어) · ×{#} (HRTW)",
    "solid: Moldauer · dashed: HRTW": "실선: 몰다우어 · 점선: HRTW",
    "σ with correction / σ without": "보정한 σ / 보정 없는 σ",
    // scene 5: limits
    "ΣT = {#}πΓ/D →": "ΣT = {#}πΓ/D →",
    "elastic enhancement Wₐₐ": "탄성 증강 Wₐₐ",
    "T → {#} per channel": "채널마다 T → {#}",
    "exact, isolated: {#}N/(N+{#}) = {#}": "정확한 값, 고립: {#}N/(N+{#}) = {#}",
    "Porter–Thomas: {#}": "포터–토머스: {#}",
    "Ericson: {#}": "에릭슨: {#}",
    "{#} channels · ΣT = {#} · Wₐₐ = {#}": "채널 {#}개 · ΣT = {#} · Wₐₐ = {#}",
    "isolated resonances: Γ ≪ D": "고립된 공명: Γ ≪ D",
    "resonances begin to overlap": "공명이 겹치기 시작함",
    "strongly overlapping: Γ ≫ D": "크게 겹침: Γ ≫ D",
  };
  Object.assign(WT.L.labels, L);
})();
Object.assign(WT.L.glossary, {
  hrtw: {
    term: "HRTW", aliases: ["HRTW"],
    short: "호프만(Hofmann), 리케르트(Richert), 테펠(Tepel), 바이덴뮐러(Weidenmüller)의 폭 요동 처방으로, 채널마다 탄성 인자를 두고 유효 투과 계수를 반복법으로 구합니다.",
    more: "몰다우어의 처방처럼 무작위 행렬 수치 계산에 맞춘 것입니다. TALYS에서는 widthmode 2이며, 몰다우어(1)가 기본값이고 정확한 GOE 3중 적분(3)이 기준입니다.",
    chapter: "hauser",
  },
  ericson: {
    term: "에릭슨 요동", aliases: ["에릭슨 요동", "Ericson fluctuations"],
    short: "많은 공명이 겹칠 때 단면적이 에너지에 따라 무작위로 요동하는 현상으로, 요동의 에너지 규모는 공명들의 평균 전체 폭이 정합니다.",
    more: "고립된 공명에서 포터–토머스 폭을 주는 바로 그 통계의 강한 겹침 극한입니다. 이 극한에서 탄성 증강 인자는 2에 가까워집니다.",
    chapter: "hauser",
  },
});
