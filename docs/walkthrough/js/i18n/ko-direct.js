/* Korean: direct (6장, 직접 반응) */
WT.L.ch.direct = {
  num: "6장", title: "직접 반응", short: "직접 반응",
  lead: "원자핵에 도달한 중성자가 모두 삼켜지는 것은 아닙니다. 일부는 표면을 스치며 한 번 밀어 주고는 그대로 날아갑니다.",
  html: `
<div class="step">
  <p>원자핵을 살짝 스치기만 하는 중성자는 원자핵을 한 번 밀어 들뜬 준위로 올려놓고, 대부분 앞쪽으로, 속도는 아주 조금만 줄어든 채 날아갈 수 있습니다. 이것이 <b>직접 반응</b>입니다. 단 한 단계로, 약 10⁻²²초 만에 끝납니다. 여기서는 중성자가 핵반지름 <i>R</i> 단위로 잰 거리 <i>b</i>, 즉 <b>충돌 매개변수</b>만큼 떨어져 지나갑니다. 점선 고리는 원자핵의 표피(표면)입니다.</p>
  <div class="ctl"><label for="di-b">겨냥 b (반지름 단위)</label><input id="di-b" type="range" data-bind="b" min="0" max="1.5" step="0.01" value="1.0"><output data-show="b" data-fmt="2"></output></div>
  <p><i>b</i>를 움직여 보세요. 약 0.8보다 작으면 중성자는 삼켜집니다. 1 근처에서는 스치고 지나가면서 원자핵을 첫 번째 들뜬 준위인 2⁺에 남겨 둡니다. 약 1.2보다 크면 빗나가며 휘기만 합니다. 이것이 원자핵이 변하지 않는 <b>탄성 산란</b>입니다.</p>
</div>
<div class="step">
  <h3>변형된 원자핵의 회전 들뜸</h3>
  <p>한 번 밀어 주면 길쭉한 원자핵(1장)이 회전하기 시작하여 <b>회전 띠</b>의 사다리 0⁺, 2⁺, 4⁺, 6⁺, 8⁺을 따라 올라갑니다. 중성자가 원자핵을 밀어 올릴 수 있고 원자핵도 되밀 수 있으므로, 어떤 준위도 따로 떼어 계산할 수 없습니다. 엔진은 이들을 모두 함께 풉니다. 이것이 <b>결합 채널</b> 방법으로, 각 채널은 하나의 결과, 여기서는 띠의 한 준위에 해당합니다.</p>
  <div class="btns"><button class="btn" data-act="kick">한 준위 위로 밀기</button><button class="btn ghost" data-act="rpause">일시정지 / 재개</button></div>
  <div class="ctl"><label for="di-beta">변형 β₂</label><input id="di-beta" type="range" data-bind="beta2" min="0.05" max="0.4" step="0.01" value="0.25"><output data-show="beta2" data-fmt="2"></output></div>
  <p>호는 어떤 준위들이 연결되어 있는지를 보여 줍니다. 전체적인 늘어남인 <i>λ</i> = 2는 이웃한 준위를 잇고, 더 세밀한 불룩함인 <i>λ</i> = 4는 두 칸을 건너뜁니다. <i>β₂</i>를 움직여 보세요. 더 길쭉한 원자핵일수록 준위들을 더 강하게 연결하여 호가 굵어집니다. 띠를 들어오는 중성자와 함께 풀기 때문에, 엔진은 띠가 중성자를 정확히 몇 개 가져가는지 알고, 나머지만 다음 장들의 더 느린 경로로 넘깁니다.</p>
</div>
<div class="step">
  <h3>표면 진동</h3>
  <p>둥근 원자핵은 출렁일 수 있고, 출렁임 에너지는 <b>포논</b>이라는 같은 크기의 덩어리로 주어집니다. 럭비공과 원반 사이를 오가는 출렁임(<i>λ</i> = 2)의 포논 하나는 2⁺ 준위를 만들고, 포논 둘은 두 배의 에너지에 0⁺, 2⁺, 4⁺의 세 준위를 만듭니다. 여기에 도달하려면 연달아 두 번 밀어야 합니다. 엔진은 이 준위들을 바닥 상태와 함께 풉니다.</p>
  <div class="ctl"><label for="di-lam">출렁임 모양 λ</label><input id="di-lam" type="range" data-bind="lam" min="2" max="3" step="1" value="2" data-instant><output data-show="lam" data-fmt="0"></output></div>
  <div class="btns"><button class="btn ghost" data-act="ph1">포논 하나</button><button class="btn ghost" data-act="ph2">포논 둘</button></div>
  <p><i>λ</i> = 3으로 두면 배 모양의 출렁임이 되며, 그 첫 준위는 3⁻입니다. 버튼을 눌러 포논을 하나 또는 둘 더해 보세요.</p>
</div>
<div class="step">
  <h3>단일 단계 직접 반응</h3>
  <p>대부분의 준위는 연결이 약해서 한 번 미는 것으로 충분합니다. 이것이 <b>DWBA</b>(왜곡파 보른 근사)입니다. 5장의 들어오는 파동이 퍼텐셜이 깊은 값에서 0으로 떨어지는 가장자리에서 원자핵을 한 번 밉니다. 마루가 부딪치는 곳에서 가장자리가 빛납니다. 퍼져 나가는 원형 파동은 원자핵을 들뜬 상태로 남기고 떠난 중성자들입니다.</p>
  <div class="ctl"><label for="di-bd">준위의 변형 β</label><input id="di-bd" type="range" data-bind="bd" min="0.02" max="0.4" step="0.01" value="0.2"><output data-show="bd" data-fmt="2"></output></div>
  <p><i>β</i>를 움직여 보세요. 가장자리가 더 세게 흔들리고 원들이 <i>β</i>²에 비례하여 밝아집니다. 변형이 두 배면 네 배가 됩니다. 엔진은 각 준위의 <i>β</i>를 측정값에서, 알려진 값이 없으면 계통적 경향에서 가져옵니다. 산란된 중성자가 각도에 따라 어떻게 퍼지는지는 선택적인 추가 출력입니다.</p>
</div>
<div class="step">
  <h3>거대 공명</h3>
  <p>모든 핵자가 함께 움직일 수 있습니다. 숨 쉬듯 부풀었다 줄어들거나, 눌렸다 늘어나거나, 배 모양으로 흔들립니다. 이것이 <b>거대 공명</b>입니다. 이 중간 질량 원자핵에서는 약 7~25 MeV 위에 있으며, 각각 폭이 몇 MeV나 되어 하나의 준위로 보기에는 너무 넓습니다. 언덕 모양은 각각의 <b>들뜸 에너지</b>를 표시합니다.</p>
  <p>엔진은 각 공명의 전체 세기를 <b>합 규칙</b>, 즉 원자핵이 얼마나 강하게 반응할 수 있는지에 대해 기본 물리학이 정하는 한계로부터 정하고, 이를 마지막으로 알려진 준위 위에 언덕 모양으로 퍼뜨립니다. 이 언덕들과 높은 준위로의 밀기가 합쳐져 <b>집단 연속 영역</b>을 이룹니다.</p>
  <div class="btns"><button class="btn ghost" data-act="mono">숨쉬기</button><button class="btn ghost" data-act="quad">찌그러짐</button><button class="btn ghost" data-act="oct">배 모양</button></div>
  <p>가장 잘 알려진 것, 즉 양성자들이 중성자들에 맞서 출렁이는 거대 쌍극자 공명은 주로 빛을 흡수하고 방출하므로 10장에서 다룹니다.</p>
</div>
<div class="step">
  <h3>직접 포획</h3>
  <p>자유 중성자는 우물의 빈 <b>궤도</b>(안에 있는 중성자 하나에게 허용된 에너지)로 곧장 떨어지면서 남는 에너지를 <em class="g">광자</em>로 내보낼 수 있습니다. 원자핵은 전혀 달궈지지 않습니다. 이것이 <b>직접 포획</b>입니다. 엔진은 5장과 같은 우물로 이를 계산할 수 있습니다. 바깥의 자유 파동, 안쪽의 속박 궤도, 그리고 둘을 잇는 광자입니다. 이 계산은 선택 사항이며 기본값은 꺼져 있습니다.</p>
  <div class="btns"><button class="btn" data-act="drop">중성자 떨어뜨리기</button></div>
  <p>직접 포획은 중성자의 에너지를 나눠 갖는 일반적인 경로가 약한 곳에서 가장 중요합니다. 준위가 적고 간격이 넓은 가벼운 원자핵과 안정성에서 멀리 떨어진 원자핵이 그렇습니다.</p>
</div>
<div class="step">
  <h3>직접 선속과 복합핵 선속</h3>
  <p>엔진은 5장의 반응 단면적을 순서대로 나눕니다. 먼저 직접 반응, 다음으로 빠른 충돌이 몫을 가져가고, 나머지만 복합핵을 형성합니다. 그림에서 각 중성자는 세 가지 운명 중 하나를 맞습니다. <b>직접 반응</b>(스치고 계속 날아감), 빠른 충돌(에너지가 퍼지기 전에 핵자 하나를 쳐냄: <b>전평형</b>, 7장), 또는 삼켜짐(<b>복합핵</b>, 8장)입니다. 쌓인 더미가 그 수를 셉니다.</p>
  <div class="ctl"><label for="di-e">중성자 에너지 (MeV)</label><input id="di-e" type="range" data-bind="E" min="1" max="60" step="0.5" value="14"><output data-show="E" data-fmt="1"></output></div>
  <p>에너지를 바꾸며 더미가 다시 채워지는 것을 지켜보세요. 몇 MeV에서는 거의 모든 중성자가 삼켜집니다. 수십 MeV에서는 직접 반응과 빠른 충돌이 함께 큰 몫을 차지합니다.</p>
  <div class="aside">코드에서: <code>ecis/formfactor.py</code>, <code>ecis/coupling.py</code>, <code>ecis/solver.py</code>(변형 퍼텐셜, 회전체와 진동체의 결합 채널), <code>ecis/dwba.py</code>와 <code>direct/dwba.py</code>(한 번 밀기, 거대 공명, 집단 연속 영역), <code>direct/racapcalc.py</code>(직접 포획, 선택 사항, 기본값은 꺼짐), <code>compound/normalization.py</code>(장부).</div>
</div>`,
};
Object.assign(WT.L.labels, {
  // scene: aim
  "skin (surface)": "표피 (표면)",
  "b = {#} R": "b = {#} R",
  "absorbed: its energy is shared by all nucleons": "흡수: 에너지를 모든 핵자가 나눠 가짐",
  "{#}⁺ level": "{#}⁺ 준위",
  "one push leaves the nucleus on {#}⁺; neutron flies on": "한 번 밀어 원자핵이 {#}⁺에 남음, 중성자는 계속 비행",
  "a miss: deflected, nucleus unchanged (elastic)": "빗나감: 휘기만 하고 원자핵은 그대로 (탄성)",
  // scene: rotor
  "at rest: {#}⁺": "정지: {#}⁺",
  "rotating: {#}⁺": "회전: {#}⁺",
  "rotating: {#}⁺ (paused)": "회전: {#}⁺ (일시정지)",
  "λ = {#}": "λ = {#}",
  "levels solved together": "준위를 함께 풂",
  // scene: vibrator
  "quadrupole ripple: football ↔ disc": "사중극 출렁임: 럭비공 ↔ 원반",
  "octupole ripple: pear ↔ pear": "팔중극 출렁임: 배 ↔ 배",
  "{#}⁺  no phonon": "{#}⁺  포논 없음",
  "{#}⁺  one phonon": "{#}⁺  포논 하나",
  "{#}⁻  one phonon": "{#}⁻  포논 하나",
  "{#}⁺ {#}⁺ {#}⁺  two phonons": "{#}⁺ {#}⁺ {#}⁺  포논 둘",
  "{#}⁺ {#}⁺ {#}⁺ {#}⁺  two phonons": "{#}⁺ {#}⁺ {#}⁺ {#}⁺  포논 둘",
  "one push": "한 번 밀기",
  "two pushes": "두 번 밀기",
  "two phonons": "포논 둘",
  "equal energy steps": "같은 에너지 간격",
  // scene: DWBA
  "rim: the push happens here": "가장자리: 여기서 밀기가 일어남",
  "incoming wave": "들어오는 파동",
  "outgoing: nucleus left excited": "나가는 파동: 원자핵은 들뜬 상태",
  "outgoing circles: the nucleus left on an excited level": "나가는 원: 원자핵이 들뜬 준위에 남음",
  "push strength ∝ β²: {#}× that at β = {#}": "밀기 세기 ∝ β²: {#}배 (β = {#} 대비)",
  // scene: giant resonances
  "breathing": "숨쉬기",
  "squash and stretch": "눌림과 늘어남",
  "pear": "배 모양",
  "breathing (monopole)": "숨쉬기 (단극)",
  "squash and stretch (quadrupole)": "눌림과 늘어남 (사중극)",
  "pear-shaped (octupole), low and high": "배 모양 (팔중극), 낮은 것과 높은 것",
  "about {#} MeV up": "약 {#} MeV 위",
  "last known level": "마지막으로 알려진 준위",
  "excitation energy (MeV) →": "들뜸 에너지 (MeV) →",
  // scene: direct capture
  "free: outside the nucleus": "자유: 원자핵 밖",
  "empty orbit": "빈 궤도",
  "drops straight in; a photon carries off the spare energy": "곧장 떨어짐, 광자가 남는 에너지를 가져감",
  // scene: ledger
  "direct": "직접",
  "fast (pre-eq.)": "빠름 (전평형)",
  "compound": "복합핵",
  "direct: grazed, flew on": "직접: 스치고 날아감",
  "fast collision: one out at once": "빠른 충돌: 하나가 즉시 나감",
  "compound: swallowed": "복합핵: 삼켜짐",
  "{#}% (model {#}%)": "{#}% (모형 {#}%)",
  "{#}% seen · model {#}%": "관측 {#}% · 모형 {#}%",
  "{#} MeV neutrons on a medium-mass nucleus (illustrative shares)": "중간 질량 원자핵에 입사한 {#} MeV 중성자 (예시용 비율)",
});
