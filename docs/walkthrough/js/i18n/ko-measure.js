/* Korean: measure (17장, 관측량) */
WT.L.ch.measure = {
  num: "17장", title: "밖으로 나오는 것", short: "관측량",
  lead: "실험이든 원자로든 별이든, 보는 것은 몇 개의 수뿐입니다. 이 장에서는 엔진이 원자핵 안에서 일어나는 일을 어떻게 그런 수로 바꾸는지 보여 드립니다.",
  html: `
<div class="step">
  <p>각 원자핵을 둘러싼 옅은 원판이 그 <b>단면적</b>입니다. 반응이 일어나려면 중성자가 맞혀야 하는 넓이이며, 원자핵의 실제 크기가 아닙니다. 빔이 왼쪽에서 원자핵으로 된 얇은 박막을 지나갑니다. 반응하는 비율은 그 넓이에 빔이 만나는 원자핵의 수를 곱한 것입니다. 단위는 반(barn, 10⁻²⁴ cm², 우라늄 원자핵의 단면 정도)입니다.</p>
  <div class="ctl"><label for="mea-e">중성자 에너지 (MeV)</label><input id="mea-e" type="range" data-bind="E" min="0.1" max="20" step="0.1" value="2"><output data-show="E" data-fmt="1"></output></div>
  <p>에너지를 낮추면 원판이 부풀어 오릅니다. 느린 중성자는 넓게 퍼진 파동이어서 더 먼 곳에서도 반응합니다. 높은 에너지에서는 원판이 원자핵 자체의 크기로 줄어듭니다.</p>
</div>
<div class="step">
  <h3>에너지와 함께 열리는 새 출구</h3>
  <p>문 하나가 출구, 즉 <b>채널</b> 하나입니다. 중성자가 튕겨 나오거나(탄성), 표적을 들뜬 상태로 남기거나(n′), 중성자를 더 쳐내거나(2n, 3n), 포획되어 광자만 나가거나(γ), 대신 양성자나 α 입자가 나갈 수 있습니다. 자물쇠가 채워진 문에는 <b>문턱 에너지</b>가 있습니다. 그 반응에는 중성자가 가져온 것보다 많은 에너지가 듭니다.</p>
  <div class="ctl"><label for="mea-e2">중성자 에너지 (MeV)</label><input id="mea-e2" type="range" data-bind="E" min="0.1" max="20" step="0.1" value="2"><output data-show="E" data-fmt="1"></output></div>
  <p>에너지를 문턱 너머로 올리면 그 문이 번쩍 열립니다. 양동이는 각 채널의 몫만큼 채워지고, 새로 열린 문은 다른 문의 몫을 가져갑니다. 문턱은 원자핵들의 질량에서, 몫은 9장의 경쟁에서 나옵니다.</p>
</div>
<div class="step">
  <h3>검출기가 보는 것</h3>
  <p>두 더미는 검출기 고리의 앞쪽 절반과 뒤쪽 절반에 도달한 중성자를 에너지별로 분류한 것입니다. 빔이 펄스로 나오므로 각 중성자의 비행시간으로 에너지를 알 수 있습니다. 빠른 중성자가 먼저 도착합니다.</p>
  <div class="ctl"><label for="mea-ein">입사 에너지 (MeV)</label><input id="mea-ein" type="range" data-bind="Ein" min="5" max="60" step="0.5" value="30"><output data-show="Ein" data-fmt="0"></output></div>
  <p>두 더미 모두 느린 <b>증발</b> 중성자의 언덕이 있습니다. 에너지가 고루 나뉜 뒤 복합핵에서 끓어 나오는 중성자로, 모든 방향으로 똑같이 나옵니다. 긴 빠른 꼬리는 앞쪽 더미에만 있습니다. 이것은 첫 충돌들에서 대략 빔 방향으로 움직이며 떠나는 <b>전평형</b> 중성자입니다. 입사 에너지를 올리면 꼬리가 길어집니다.</p>
</div>
<div class="step">
  <h3>어느 방향으로 가는가</h3>
  <p>꽃잎 모양은 각 방향으로 중성자가 몇 개 나가는지를 보여 주며, 빔은 왼쪽에서 들어옵니다. 증발 중성자는 빔을 잊어버려 모든 방향으로 똑같이 나가고, 빠른 전평형 중성자는 앞쪽으로 기웁니다. 얼마나 기우는지는 칼바흐의 규칙이 나가는 에너지와 함께 커지는 기울기 <i>a</i> 하나로 정합니다. 엔진은 선택적 출력으로 이 각분포도 내보낼 수 있습니다.</p>
  <div class="ctl"><label for="mea-eo">방출 에너지 (MeV)</label><input id="mea-eo" type="range" data-bind="Eout" min="1" max="45" step="0.5" value="25"><output data-show="Eout" data-fmt="1"></output></div>
  <p>방출 에너지를 낮추면 꽃잎이 둥글어집니다. 느린 중성자는 대부분 증발 중성자입니다.</p>
  <div class="formula">dσ/dΩ ∝ e<sup>a cos θ</sup></div>
</div>
<div class="step">
  <h3>별 속에서</h3>
  <p>아래 더미에는 별의 뜨거운 기체 속에서 포획된 중성자들의 에너지가 모입니다. 그 속력은 온도 <i>kT</i>가 정하는 맥스웰 분포를 따릅니다(30 keV는 약 3억 5천만 도). 꼬리가 길수록 빠른 중성자이며, 원자핵 곁을 지날 때마다 포획 섬광으로 끝날 수 있습니다.</p>
  <div class="ctl"><label for="mea-kt">온도 kT (keV)</label><input id="mea-kt" type="range" data-bind="kT" min="5" max="100" step="1" value="30"><output data-show="kT" data-fmt="0"></output></div>
  <p>느린 중성자는 붙잡기는 쉽지만 드물게 지나가고, 빠른 중성자는 수가 적으므로, 대부분의 포획은 폭이 몇 <i>kT</i>인 창에서 일어납니다. 기체 전체에 대한 비율이 밀리반(mb) 단위의 <b>맥스웰 평균 단면적</b>(MACS)입니다. 기체를 데우면 창이 표적이 더 작은 높은 에너지 쪽으로 이동합니다. MACS는 엔진의 포획 곡선을 접어(적분하여) 얻습니다.</p>
</div>
<div class="step">
  <h3>표적도 뜨겁다</h3>
  <p>공들은 이 온도에서 표적 원자핵 중 어느 만큼이 가장 낮은 각 준위에 있는지를 보여 줍니다. 별 속에서는 일부 표적이 이미 들떠 있으며, 들뜬 준위 하나하나는 같은 복합핵으로 들어가는 서로 다른 입구입니다. 스핀 <i>J</i>인 준위는 2<i>J</i>+1개의 방향을 가지므로 더 많이 담습니다.</p>
  <div class="ctl"><label for="mea-kt2">온도 kT (keV)</label><input id="mea-kt2" type="range" data-bind="kT" min="5" max="100" step="1" value="30"><output data-show="kT" data-fmt="0"></output></div>
  <p>온도를 올리며 원자핵들이 위로 올라가는 것을 지켜보세요. 항성 반응률은 채워진 각 준위에서 포획을 계산하고 그 결과를 이 비율로 더합니다. 가중치의 합이 분배 함수 <i>G</i>이고, 바닥 상태 반응률에 대한 비가 <b>항성 증강 인자</b>입니다. 엔진은 이를 선택 사항으로(기본값은 꺼짐) 계산할 수 있으며, 보통은 모든 표적이 바닥 상태에서 출발합니다.</p>
</div>
<div class="step">
  <h3>이 모든 것을 얼마나 확신할 수 있을까?</h3>
  <p>희미한 원판 하나하나는 입력을 무작위로 살짝 바꾼 엔진의 실행 한 번입니다. 광학 우물의 깊이, 준위 밀도, 감마 세기 함수는 모두 몇 퍼센트 이내로만 알려져 있습니다. 많은 실행의 퍼짐이 정직한 불확도이며, 이것이 <b>전체 몬테카를로</b>(Total Monte Carlo)입니다.</p>
  <div class="btns"><button class="btn" data-act="tmc1">변종 하나 실행</button><button class="btn ghost" data-act="tmc">10회 실행</button><button class="btn ghost" data-act="clear">지우기</button></div>
  <p>테두리가 선명하면 입력이 답을 단단히 고정한다는 뜻이고, 흐릿하면 그렇지 않다는 뜻입니다. 바로 그런 곳에서 새 측정이 가장 큰 도움이 됩니다.</p>
  <div class="aside">코드에서: <code>emission/channels.py</code>(배타적 채널과 잔류핵), <code>specout.py</code>와 <code>specang.py</code>(방출 스펙트럼, 각분포, 이중 미분 단면적, 요청할 때만 출력), <code>astro/stellar.py</code>(열적으로 채워진 표적 준위로부터의 포획, 선택 사항), <code>tmc.py</code>(전체 몬테카를로 표본 추출기). 바닥 상태 MACS는 <code>validation/differential/core.py</code>에서 포획 곡선을 접어 얻습니다.</div>
</div>`,
};
Object.assign(WT.L.labels, {
  // area
  "each disc: σ ≈ {#} b": "원판 하나: σ ≈ {#} b",
  "each disc: cross section σ ≈ {#} b, the area a neutron must hit": "원판 하나: 단면적 σ ≈ {#} b, 중성자가 맞혀야 하는 넓이",
  "beam →": "빔 →",
  "nucleus's own face ≈ {#} b · {#} % reacts": "원자핵 자체 단면 ≈ {#} b · {#}% 반응",
  "the nucleus's own face ≈ {#} b · {#} % of the beam reacts in this foil": "원자핵 자체 단면 ≈ {#} b · 이 박막에서 빔의 {#}%가 반응",
  "slow: the neutron's wave reaches well past the surface": "느림: 중성자 파동이 표면 훨씬 바깥까지 닿음",
  "the target still looks bigger than the nucleus": "표적이 아직 원자핵보다 크게 보임",
  "fast: close to the nucleus's own size": "빠름: 원자핵 자체 크기에 가까움",
  // doors
  "elastic": "탄성", "n′ inelastic": "n′ 비탄성", "{#}n": "{#}n", "γ capture": "γ 포획", "p": "p", "α": "α", "n′": "n′",
  "{#}n · {#} MeV": "{#}n · {#} MeV", "p · {#} MeV": "p · {#} MeV", "α · {#} MeV": "α · {#} MeV", "n′ inelastic · {#} MeV": "n′ 비탄성 · {#} MeV",
  "opens at {#} MeV": "{#} MeV에서 열림",
  "{#} MeV": "{#} MeV",
  // detect
  "forward half": "앞쪽 절반", "backward half": "뒤쪽 절반",
  "pulsed beam": "펄스 빔", "pulsed beam →": "펄스 빔 →",
  "backward": "뒤쪽", "backward detectors": "뒤쪽 검출기",
  "forward": "앞쪽", "forward detectors": "앞쪽 검출기",
  "outgoing neutron energy from the flight time (MeV) →": "비행시간으로 구한 방출 중성자 에너지 (MeV) →",
  "fast tail": "빠른 꼬리", "fast tail: pre-equilibrium": "빠른 꼬리: 전평형",
  "evaporated hump": "증발 언덕", "hump: evaporated, every way alike": "언덕: 증발, 모든 방향으로 같음",
  "{#} % leave before the energy is shared": "{#}%가 에너지가 나뉘기 전에 떠남",
  // angle
  "beam": "빔",
  "forward-to-backward ratio ≈ {#}  ·  slope a ≈ {#}": "앞/뒤 비 ≈ {#}  ·  기울기 a ≈ {#}",
  "mostly evaporated: every direction alike": "대부분 증발: 모든 방향으로 같음",
  "a mix: the fast share leans forward": "혼합: 빠른 몫이 앞으로 기욺",
  "mostly pre-equilibrium: strongly forward": "대부분 전평형: 강하게 앞쪽",
  "forward →": "앞쪽 →",
  // star
  "{#} keV": "{#} keV",
  "kT = {#} keV": "kT = {#} keV",
  "energies of captured neutrons": "포획된 중성자의 에너지",
  "each capture drops here, by the neutron's energy: the window that counts": "포획마다 중성자 에너지 위치에 쌓임: 중요한 창",
  "MACS ≈ {#} mb at kT = {#} keV · captures watched: {#}": "MACS ≈ {#} mb (kT = {#} keV) · 관찰한 포획: {#}",
  // hot target
  "{#}⁺  ground state": "{#}⁺  바닥 상태", "{#}⁺  {#} keV": "{#}⁺  {#} keV",
  "target levels, with the share of nuclei sitting on each": "표적 준위와 각 준위에 있는 원자핵의 비율",
  "{#} % start from the ground state · partition function G ≈ {#}": "{#}%가 바닥 상태에서 출발 · 분배 함수 G ≈ {#}",
  // TMC
  "optical well": "광학 우물", "optical well depth": "광학 우물 깊이",
  "level density": "준위 밀도", "photon strength": "감마 세기 함수",
  "σ ≈ {#} b ": "σ ≈ {#} b ", "σ ≈ {#} mb ": "σ ≈ {#} mb ",
  "σ ≈ {#} b ±{#} %": "σ ≈ {#} b ±{#}%", "σ ≈ {#} mb ±{#} %": "σ ≈ {#} mb ±{#}%",
  "dashed: best inputs · each disc drawn at its own scale": "점선: 최적 입력 · 원판마다 고유한 축척",
  "dashed ring: the best-value inputs · each energy drawn at its own scale (disc area ∝ σ)": "점선 고리: 최적값 입력 · 에너지마다 고유한 축척 (원판 넓이 ∝ σ)",
  "{#} runs of the engine, each with its inputs nudged at random": "엔진 {#}회 실행, 매번 입력을 무작위로 살짝 바꿈",
});
