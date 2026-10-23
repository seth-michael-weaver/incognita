/* Korean: structure (1장, 원자핵은 무엇으로 이루어져 있는가) */
WT.L.ch.structure = {
  num: "1장", title: "원자핵은 무엇으로 이루어져 있는가", short: "구조",
  lead: "엔진(우리의 핵반응 소프트웨어)은 중성자를 하나라도 쏘기 전에 표적 원자핵에 대한 설명이 필요합니다. 얼마나 단단히 뭉쳐 있는지, 어떤 에너지 상태에 있을 수 있는지, 어떤 모양인지를 알아야 합니다.",
  html: `
<div class="step">
  <p>그림은 철 원자핵입니다. <em class="p">양성자</em>와 <em class="n">중성자</em>(<b>핵자</b>)가 빽빽하게 뭉친 공으로, 도달 거리가 짧은 <b>강한 상호작용</b>이 이들을 붙잡고 있습니다. 각 핵자는 가장 가까운 이웃만 느끼기 때문에 모든 원자핵의 밀도는 거의 같습니다.</p>
  <div class="ctl"><label for="st-n">중성자 수 (철의 양성자는 26개)</label><input id="st-n" type="range" data-bind="N" min="24" max="38" step="1" value="30" data-instant><output data-show="N" data-fmt="0"></output></div>
  <p>슬라이더를 움직여 중성자를 더하거나 빼 보세요. 각각이 서로 다른 <b>동위원소</b>입니다. 막대는 핵자당 <b>결합 에너지</b>를 MeV(백만 전자볼트) 단위로 보여 줍니다. 원자핵을 산산이 떼어 놓는 데 필요한 에너지입니다. 이 값은 안정한 동위원소 근처에서 가장 큽니다.</p>
</div>
<div class="step">
  <h3>하나를 끄집어내는 비용</h3>
  <p>입자 하나를 끄집어내는 데 드는 에너지가 그 입자의 <b>분리 에너지</b>입니다. 중성자는 <i>S<sub>n</sub></i>, 양성자는 <i>S<sub>p</sub></i>, <b>알파 입자</b>(양성자 둘과 중성자 둘이 결합한 것)는 <i>S<sub>α</sub></i>입니다. 그림은 원자핵을 위로 갈수록 에너지가 높아지는 우물로 나타냅니다. 끄집어낼 때마다 맨 위 입자가 점선으로 된 "자유" 선 너머로 올라가고, 계기가 그 비용을 기록합니다.</p>
  <div class="btns"><button class="btn ghost" data-act="pn">중성자 꺼내기</button><button class="btn ghost" data-act="pp">양성자 꺼내기</button><button class="btn ghost" data-act="pa">알파 꺼내기</button></div>
  <p>엔진은 각 분리 에너지를 두 핵질량의 차이로 구합니다. 가능한 경우에는 측정값을, 그렇지 않으면 질량 모형의 값을 씁니다.</p>
  <div class="ctl"><label for="st-n2">중성자 수</label><input id="st-n2" type="range" data-bind="N" min="24" max="38" step="1" value="30" data-instant><output data-show="N" data-fmt="0"></output></div>
  <p>중성자 수를 바꾸고 다시 중성자를 꺼내 보세요. <i>S<sub>n</sub></i>이 지그재그로 오르내립니다. 핵자들이 짝을 이루기 때문에 짝수 개일 때 마지막 핵자를 더 단단히 붙잡습니다. 반응은 이 비용을 치를 만큼의 에너지를 가져올 때에만 입자를 내보낼 수 있습니다. 이 비용들이 계산 전체의 <b>문턱 에너지</b>입니다.</p>
</div>
<div class="step">
  <h3>에너지 준위, 그리고 아래로 떨어지기</h3>
  <p>원자핵은 정확히 정해진 양의 여분 에너지만 가질 수 있습니다. 여기 철-56에 대해 그려진 선들이 그것이며, 맨 아래가 <b>바닥 상태</b>입니다. 각 준위에는 <b>스핀</b> <i>J</i>(각운동량)와 <b>반전성</b> + 또는 −(파동이 거울에 비쳐도 같아 보이는지 여부)가 있습니다. 2<sup>+</sup>는 스핀 2, 반전성 +를 뜻합니다.</p>
  <p>주황색 공은 높은 준위에 있는 원자핵입니다. 한 번에 한 준위씩 떨어지며, 건너뛸 때마다 에너지 차이를 실어 나르는 <em class="g">광자</em>(감마선)를 내놓습니다. 경로의 굵기와 백분율은 각 전이의 측정된 확률, 즉 <b>갈래비</b>입니다.</p>
  <div class="btns"><button class="btn" data-act="drop">원자핵 들뜨게 하기</button></div>
  <p>몇 번 눌러 보세요. 같은 준위에서 출발해도 서로 다른 경로로 바닥 상태에 이릅니다. 엔진은 원자핵마다 측정된 준위를 서른 개쯤 확률과 함께 보관하고, 그보다 위에서는 빽빽한 준위들을 매끄러운 <b>연속 영역</b>으로 다룹니다. 점선 <i>S<sub>n</sub></i>보다 위에서는 원자핵이 중성자를 방출할 수 있습니다.</p>
</div>
<div class="step">
  <h3>쉽게 내려갈 길이 없는 준위</h3>
  <p>내려가는 유일한 길이 큰 스핀 변화 Δ<i>J</i>를 요구하는 준위는 매우 느리게 붕괴합니다. 오른쪽에는 이런 준위에 있는 원자핵 64개가 있습니다. 각각 무작위한 시간만큼 기다렸다가 떨어지면서 <em class="g">광자</em>를 튀어 내보냅니다. <b>반감기</b> 하나가 지나면 절반이 떨어집니다.</p>
  <div class="ctl"><label for="st-dj">스핀 변화 ΔJ</label><input id="st-dj" type="range" data-bind="dJ" min="1" max="5" step="1" value="2" data-instant><output data-show="dJ" data-fmt="0"></output></div>
  <div class="ctl"><label for="st-eg">광자 에너지 (MeV)</label><input id="st-eg" type="range" data-bind="Eg" min="0.05" max="1.5" step="0.05" value="0.3"><output data-show="Eg" data-fmt="2"></output></div>
  <div class="btns"><button class="btn ghost" data-act="excite">모두 들뜨게 하기</button></div>
  <p>Δ<i>J</i>를 올리면 튀어나오는 속도가 느려집니다. 스핀이 한 단위 늘 때마다 기다리는 시간이 십만 배 이상 길어지고, 광자 에너지가 낮아도 길어집니다(로그 눈금으로 표시). 약 1초보다 오래 사는 준위는 <b>핵이성질체</b>이며, 엔진은 이를 바닥 상태처럼 하나의 종착점으로 다룹니다.</p>
</div>
<div class="step">
  <h3>둥근가, 아닌가</h3>
  <p>많은 원자핵은 둥글지 않습니다. <i>β₂</i>("베타 2")는 늘어난 정도를 나타냅니다. 0은 구형, 양수는 럭비공처럼 길쭉하게 늘어난 모양, 음수는 원반처럼 납작하게 눌린 모양입니다. 오른쪽 사다리는 각 모양이 만드는 준위를 보여 줍니다.</p>
  <p>길쭉한 원자핵은 회전할 수 있어서 간격이 <i>J</i>(<i>J</i>+1)처럼 커지는 준위 0<sup>+</sup>, 2<sup>+</sup>, 4<sup>+</sup>, 6<sup>+</sup>를 만듭니다. 이것이 <b>회전체</b>입니다. 둥근 원자핵은 표면이 출렁일 수 있습니다. 출렁임의 한 단위인 <b>포논</b>은 매번 같은 에너지를 더하므로 준위 간격이 고릅니다. 이것이 <b>진동체</b>입니다.</p>
  <div class="ctl"><label for="st-beta">변형 β₂</label><input id="st-beta" type="range" data-bind="beta" min="-0.3" max="0.45" step="0.01" value="0.28"><output data-show="beta" data-fmt="2"></output></div>
  <div class="btns"><button class="btn ghost" data-act="still">정지</button><button class="btn ghost" data-act="vib">진동</button><button class="btn ghost" data-act="rot">회전</button></div>
  <p><i>β₂</i>를 바꾸고 버튼을 눌러 보세요. 더 많이 늘어날수록 회전체의 준위들이 서로 가까워집니다. 엔진은 원자핵마다 변형값과 함께 구형, 진동체, 회전체 중 하나의 꼬리표를 저장합니다. 지나가는 중성자가 이를 어떻게 이용하는지는 3장에서 보여 드립니다.</p>
</div>
<div class="step">
  <h3>문턱 바로 위의 지문</h3>
  <p>표적에 합류하는 느린 중성자는 <i>S<sub>n</sub></i> 바로 위, 왼쪽의 작은 상자 안에 떨어집니다. 오른쪽 패널은 그 상자를 수천 배 확대한 것으로, 중성자 에너지가 왼쪽에서 오른쪽으로 증가합니다.</p>
  <div class="ctl"><label for="st-fe">빔 에너지</label><input id="st-fe" type="range" data-bind="fe" min="0" max="1" step="0.001" value="0.3" data-instant><output id="st-fe-out"></output></div>
  <div class="btns"><button class="btn ghost" data-act="fplay" id="st-fplay">훑기 일시정지</button></div>
  <p>대부분의 에너지에서 빔은 그대로 통과합니다. 그러나 정확히 정해진 몇몇 에너지에서는 중성자와 원자핵을 합친 것이 숨은 준위와 맞아떨어져 빔의 상당 부분이 흡수됩니다. 이것이 <b>공명</b>입니다. 봉우리에서는 그려진 원자핵이 부풀어 오릅니다. 실제로 크기가 변하는 것이 아니라, 중성자의 파동이 원자핵의 파동과 겹칠 때 중성자가 사실상 보게 되는 더 큰 표적을 나타냅니다. 그 뒤 원자핵은 에너지를 <em class="g">광자</em>나 중성자로 돌려줍니다. 곡선은 흡수된 비율을, 막대는 찾아낸 각 공명을 표시합니다.</p>
  <div class="btns"><button class="btn ghost" data-act="fFe">철-56</button><button class="btn ghost" data-act="fAu">금-197</button><button class="btn ghost" data-act="fU">우라늄-238</button></div>
  <p>원자핵마다 고유한 눈금을 가진 고유한 바코드가 있습니다. 철의 공명 사이 간격은 수천 전자볼트이고, 금과 우라늄은 수십 전자볼트입니다. 세 가지 평균값이 이를 요약합니다. 평균 간격 <i>D₀</i>, 모든 봉우리에서 거의 같은 <b>광자 폭</b> ⟨Γ<sub>γ</sub>⟩, 그리고 느린 중성자가 얼마나 쉽게 들어가는지를 나타내는 <b>세기 함수</b> <i>S₀</i>입니다.</p>
  <p>각각은 이후 단계를 검증합니다. 엔진의 준위 밀도 매개변수는 원자핵마다 <i>D₀</i>에 맞춘 것이고, ⟨Γ<sub>γ</sub>⟩는 광자 방출을, <i>S₀</i>는 다음 장의 광학 모형을 시험합니다. 측정되지 않은 원자핵에 대해서는 많은 원자핵에 걸쳐 맞춘 경향을 사용합니다.</p>
  <div class="aside">코드에서: <code>structure/masses.py</code>(측정 질량, 그 바깥의 모형 질량, 분리 에너지), <code>structure/levels.py</code>(불연속 준위, 갈래비, 핵이성질체, 추정 스핀)와 <code>levjpar.py</code>(선택 사항, 기본값은 꺼짐: 원자핵에 불가능한 스핀이 목록에 있으면 다시 추정), <code>structure/deformation.py</code>(β₂와 구형/진동체/회전체 꼬리표)와 <code>collrule.py</code>(선택 사항, 기본값은 꺼짐: 측정된 준위로부터 표적의 꼬리표를 선택), <code>structure/resonances.py</code>(D₀, S₀, S₁, ⟨Γγ⟩).</div>
</div>`,
};
(function () {
  const L = {
    // scene: packed drop
    "{#}Fe": "{#}Fe",
    "{#} protons · {#} neutrons": "양성자 {#}개 · 중성자 {#}개",
    "binding energy per nucleon: about {#} MeV": "핵자당 결합 에너지: 약 {#} MeV",
    "binding per nucleon, one bar per isotope →": "핵자당 결합 에너지, 동위원소당 막대 하나 →",
    // scene: well
    "free": "자유",
    "free: outside the nucleus": "자유: 원자핵 밖",
    "neutrons": "중성자",
    "protons": "양성자",
    "an alpha forms from the top pairs": "맨 위 쌍들이 알파를 이룸",
    "neutron {#}": "중성자 {#}",
    "proton {#}": "양성자 {#}",
    "alpha {#}": "알파 {#}",
    "n {#}": "n {#}",
    "p {#}": "p {#}",
    "energy paid": "치른 에너지",
    "energy to pull": "꺼내는 데 드는",
    "(MeV)": "(MeV)",
    "each one out (MeV)": "에너지 (MeV)",
    "higher mark =": "표시가 높을수록",
    "harder to remove": "꺼내기 어려움",
    "pulling out a neutron: {#} MeV paid": "중성자 꺼내기: {#} MeV 소모",
    "pulling out a proton: {#} MeV paid": "양성자 꺼내기: {#} MeV 소모",
    "pulling out an alpha: {#} MeV paid": "알파 꺼내기: {#} MeV 소모",
    // scene: levels and gamma drops
    "continuum: too many levels to list": "연속 영역: 준위가 너무 많아 나열 불가",
    "neutron threshold Sₙ ≈ {#} MeV": "중성자 문턱 Sₙ ≈ {#} MeV",
    "ground state": "바닥 상태",
    "MeV": "MeV",
    "each line: an energy, a spin J and a parity (±)": "각 선: 에너지, 스핀 J, 반전성(±)",
    "path width and % = measured odds of each hop": "경로 굵기와 % = 각 전이의 측정 확률",
    // scene: isomer
    "ground": "바닥",
    "J = {#}/{#}": "J = {#}/{#}",
    "ΔJ = {#}": "ΔJ = {#}",
    "still excited: {#} of {#}": "아직 들뜬 상태: {#} / {#}",
    "longer than a second: an isomer, a stop in its own right": "1초 이상: 핵이성질체, 그 자체로 하나의 종착점",
    "shown slowed down (log scale)": "느리게 표시 (로그 눈금)",
    "shown slowed down: the slower they pop, the longer the real wait (log scale)": "느리게 표시: 천천히 튈수록 실제 대기 시간이 김 (로그 눈금)",
    // scene: shape
    "ripples at the surface: a vibrator": "표면이 출렁임: 진동체",
    "stretched and rotating: a rotor": "늘어나서 회전: 회전체",
    "round: a sphere": "둥긂: 구형",
    "stretched (prolate): a football": "길쭉함(장구형): 럭비공",
    "squashed: an oblate disc": "납작함: 편구형 원반",
    "{#} phonons": "포논 {#}개",
    "no regular": "규칙적인 준위",
    "level pattern": "패턴 없음",
    "spacing grows like J(J+{#})": "간격이 J(J+{#})처럼 증가",
    "equal steps, one phonon each": "같은 간격, 한 칸에 포논 하나",
    "its lowest levels": "가장 낮은 준위들",
    "β₂ = {#}": "β₂ = {#}",
    // scene: resonance fingerprint
    "continuum": "연속 영역",
    "Sₙ ≈ {#} MeV": "Sₙ ≈ {#} MeV",
    "slow neutron": "느린 중성자",
    "a slow neutron lands here:": "느린 중성자가 떨어지는 곳:",
    "lands here": "도착 지점",
    "Sₙ + its kinetic energy": "Sₙ + 운동 에너지",
    "×{#} million": "×{#}백만",
    "×{#} thousand": "×{#}천",
    "magnified": "확대",
    "swells on a peak: the size the neutron effectively “sees” (waves overlap), not a real size change": "봉우리에서 부풂: 중성자가 사실상 “보는” 크기(파동의 겹침)이며 실제 크기 변화가 아님",
    "share taken in": "흡수 비율",
    "share of the beam taken in": "빔 중 흡수된 비율",
    "{#} (Sₙ)": "{#} (Sₙ)",
    "{#} = exactly Sₙ": "{#} = 정확히 Sₙ",
    "{#} keV": "{#} keV",
    "{#} eV": "{#} eV",
    "neutron energy →": "중성자 에너지 →",
    "neutron's kinetic energy →": "중성자 운동 에너지 →",
    "D₀ ≈ {#} keV: the average gap": "D₀ ≈ {#} keV: 평균 간격",
    "D₀ ≈ {#} eV: the average gap": "D₀ ≈ {#} eV: 평균 간격",
    "S₀: average peak strength": "S₀: 봉우리의 평균 세기",
    "S₀: how strong the peaks are on average (how easily a neutron gets in)": "S₀: 봉우리의 평균 세기 (중성자가 들어가기 쉬운 정도)",
    "⟨Γγ⟩ ≈ {#} eV: photon width": "⟨Γγ⟩ ≈ {#} eV: 광자 폭",
    "⟨Γγ⟩ ≈ {#} eV: photon width, about the same for every peak": "⟨Γγ⟩ ≈ {#} eV: 광자 폭, 모든 봉우리에서 거의 같음",
    "⟨Γγ⟩ ≈ {#} eV: a hairline here": "⟨Γγ⟩ ≈ {#} eV: 여기서는 머리카락 굵기",
    "⟨Γγ⟩ ≈ {#} eV: a hairline here; neutrons widen these peaks": "⟨Γγ⟩ ≈ {#} eV: 여기서는 머리카락 굵기, 중성자가 봉우리를 넓힘",
    "peaks drawn about {#}× wider than life so they show": "잘 보이도록 봉우리를 실제보다 약 {#}배 넓게 그림",
  };
  // beam readout and per-target labels
  for (const u of ["keV", "eV"]) L[`beam of neutrons at {#} ${u}`] = `중성자 빔 {#} ${u}`;
  const EL = { iron: "철", gold: "금", uranium: "우라늄" };
  for (const en in EL) {
    L[`${en}{#} levels`] = `${EL[en]}{#} 준위`;
    L[`${en}{#}: took in {#} of the last {#}`] = `${EL[en]}{#}: {#}개 흡수 (최근 {#}개 중)`;
  }
  // isomer half-life in every unit fmtTime can produce
  const TU = { femtoseconds: "펨토초", picoseconds: "피코초", nanoseconds: "나노초", microseconds: "마이크로초",
    milliseconds: "밀리초", seconds: "초", minutes: "분", hours: "시간", days: "일", years: "년" };
  for (const en in TU) L[`half-life about {#} ${en}`] = `반감기 약 {#}${TU[en]}`;
  L["half-life about {#}×{#}^{#} years"] = "반감기 약 {#}×{#}^{#}년";
  Object.assign(WT.L.labels, L);
})();
