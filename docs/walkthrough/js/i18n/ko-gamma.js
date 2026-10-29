/* Korean: gamma (10장, 광자) */
WT.L.ch.gamma = {
  num: "10장", title: "감마선 방출", short: "광자",
  lead: "입자가 하나도 떠나지 않으면 원자핵은 광자, 곧 높은 에너지의 빛 알갱이인 감마선을 내보내며 식습니다. 이 출구는 모든 에너지에서 열려 있습니다.",
  html: `
<div class="step">
  <p>8 MeV(백만 전자볼트)의 뜨거운 상태가 광자(γ)를 내보냅니다. 사다리 옆의 더미에는 광자가 도착한 곳이 모입니다. 2 MeV 아래의 상태들은 이름이 붙은 몇 개의 가로대이고, 그 위는 에너지와 함께 가파르게 빽빽해지는 무리(회색 점)입니다. 각 광자는 떨어진 만큼의 에너지 <i>E<sub>γ</sub></i>를 가져가며, <i>E<sub>γ</sub></i>³에 비례하여 밝게 그려집니다.</p>
  <div class="formula">T<sub>γ</sub>(E<sub>γ</sub>) = 2π · E<sub>γ</sub><sup>2l+1</sup> · f(E<sub>γ</sub>)</div>
  <p>말로 하면 이렇습니다. 에너지 <i>E<sub>γ</sub></i>의 광자가 얼마나 쉽게 빠져나오는가(<i>T<sub>γ</sub></i>, 9장의 광자의 문)는 흔한 종류의 광자(쌍극자, <i>l</i> = 1)에서 <i>E<sub>γ</sub></i>³처럼 커지고, 여기에 <b>광자 세기</b> <i>f</i>, 곧 이 원자핵이 그 에너지에서 얼마나 쉽게 복사하는지가 곱해집니다. 그다음 광자는 내려앉을 상태를 찾아야 합니다. 작게 떨어지면 상태는 많이 기다리고 있지만 거의 빠져나오지 못하고, 크게 떨어지면 쉽게 빠져나오지만 상태가 적습니다. 이긴 쪽은 그 사이에 있습니다.</p>
  <div class="ctl"><label for="gm-e0">시작 에너지</label><input id="gm-e0" type="range" data-bind="E0" min="3" max="9" step="0.5" value="8"><output data-show="E0" data-fmt="1"></output></div>
  <div class="btns"><button class="btn" data-act="emit">100개 방출</button></div>
  <p>더미는 시작점보다 몇 MeV 아래에서 가장 높습니다. 대부분의 광자가 2~4 MeV를 가져갑니다. 시작 에너지를 옮기면 봉우리도 따라 움직입니다.</p>
</div>
<div class="step">
  <h3>거대 쌍극자 공명</h3>
  <p>오른쪽의 큰 봉우리는 <b>거대 쌍극자 공명</b>입니다. 모든 양성자(빗금)가 모든 중성자(채움)에 맞서 앞뒤로 출렁이는 운동입니다. 그 진동수가 원자핵이 가장 쉽게 흡수하고 방출하는 광자 에너지를 정합니다. 곡선은 로그 눈금(한 칸 올라갈 때마다 열 배)으로 그린 광자 세기 <i>f</i>입니다.</p>
  <div class="ctl"><label for="gm-a">질량수 A</label><input id="gm-a" type="range" data-bind="A" min="40" max="240" step="1" value="112"><output data-show="A" data-fmt="0"></output></div>
  <p>질량수 A(양성자 수 더하기 중성자 수)를 바꿔 보세요. 무거운 원자핵은 더 느리게 출렁여 12~14 MeV 근처에서 울리고, 가벼운 원자핵은 20 MeV 근처에서 울립니다. 붕괴하는 원자핵은 몇 MeV짜리 광자만 내보내므로, 가장 중요한 것은 음영으로 표시된 낮은 에너지 꼬리입니다.</p>
</div>
<div class="step">
  <h3>낮은 에너지의 자기 세기</h3>
  <p>변형된 원자핵은 자기적으로도 복사합니다. 두 개의 럭비공인 양성자(빗금)와 중성자(채움)가 가위의 날처럼 서로 엇갈려 흔들립니다. 이 <b>가위 모드</b>는 3 MeV 근처에 있습니다. 8 MeV 근처의 <b>스핀 뒤집기</b>는 모양과 상관없이 개별 핵자가 스핀을 뒤집는 것(작은 화살표)입니다.</p>
  <div class="ctl"><label for="gm-b">변형 β₂</label><input id="gm-b" type="range" data-bind="beta" min="0" max="0.35" step="0.01" value="0.25"><output data-show="beta" data-fmt="2"></output></div>
  <p>변형 β₂(0은 구형)를 바꿔 보세요. 더 길쭉할수록 가위 모드 광자가 많이 날아가고, 구형에는 하나도 없습니다. 가장 낮은 에너지에서는 세기가 다시 올라갑니다. 이것이 부드러운 광자가 조금씩 나오는 <b>상향 굴곡</b>(upbend)이며, 엔진은 원자핵이 변형될수록 이를 약하게 합니다. 기본값이 꺼져 있는 선택 스위치를 켜면 오슬로(Oslo) 측정에 맞는 더 강한 가위 모드 계통성(우라늄에서 네다섯 배 강함)을 씁니다.</p>
</div>
<div class="step">
  <h3>감마 캐스케이드</h3>
  <p>캐스케이드는 위쪽 구간(목록으로 만들기에는 너무 빽빽한 상태, 8장)에서 이름 붙은 준위까지 차례로 방출되는 광자들입니다. 준위는 읽을 수 있도록 늘려 그렸습니다(속이 찬 가로대는 반전성 +, 빈 것은 −). 거기서부터 엔진은 어림하기를 멈추고 표로 정리된 <b>갈래비</b>, 즉 각 준위가 아래의 각 준위로 붕괴하는 측정된 확률을 따릅니다.</p>
  <div class="btns"><button class="btn" data-act="drop">캐스케이드 떨어뜨리기</button></div>
  <p>버튼을 몇 번 눌러 보세요. 위쪽 부분은 매번 달라지지만, 끝부분은 측정된 몇 가지 경로 중 하나를 따릅니다.</p>
</div>
<div class="step">
  <h3>핵이성질체 생성</h3>
  <p>0.40 MeV의 11/2− 준위는 <b>핵이성질체</b>입니다. 스핀이 아래 준위들과 너무 달라 광자가 이들을 거의 이어 주지 못하므로, 몇 초에서 몇 년까지 살아남고 그곳에 도착한 것은 그대로 머뭅니다. 엔진은 1초보다 오래 사는 준위를 모두 종착점으로 다룹니다. 공 하나가 캐스케이드 하나이며, 핵이성질체의 더미나 바닥 상태의 더미에서 끝납니다.</p>
  <div class="ctl"><label for="gm-j">입구 스핀</label><input id="gm-j" type="range" data-bind="J0" min="0" max="8" step="1" value="2" data-instant><output id="gm-jout">5/2</output></div>
  <p>캐스케이드가 시작되는 입구 스핀을 바꾸면 더미가 다시 쌓입니다. 핵이성질체에서 끝나는 몫인 <b>이성질체 비</b>는 이 값에 따라 달라집니다. 고스핀에서 시작하면 고스핀 핵이성질체로 흘러가고, 저스핀에서 시작하면 그것을 지나쳐 바닥 상태로 미끄러집니다.</p>
</div>
<div class="step">
  <h3>복사 포획</h3>
  <p>느린 중성자를 막 흡수한 원자핵에는 출구 문이 두 개 있습니다(9장). 광자(위)와 다시 나가는 중성자(오른쪽)입니다. 각 문의 틈은 eV 단위의 <b>폭</b>, 즉 원자핵이 그 문을 통해 얼마나 빨리 붕괴하는지입니다. 광자 폭은 거의 변하지 않고, 중성자 폭은 중성자의 속력과 함께 커집니다.</p>
  <div class="ctl"><label for="gm-e">중성자 에너지</label><input id="gm-e" type="range" data-bind="lgE" min="-2" max="3.3" step="0.02" value="0"><output id="gm-eout">1.0 keV</output></div>
  <p>중성자 에너지를 10 eV에서 2 MeV까지 바꿔 보세요. <b>포획</b> (n,γ)는 중성자가 남고 광자가 떠나는 것입니다. 10 eV에서는 대부분 포획이 이기지만, 몇 keV 위에서는 작은 몫이 됩니다. 문턱에서의 광자 폭은 수백 개 원자핵에 대해 측정되어 있어 감마 세기 함수를 검증하는 데 쓰입니다. 엔진은 기본적으로 자체 값을 쓰며, 선택 스위치를 켜면 측정된 원자핵마다 둘이 일치할 때까지 감마 세기 함수를 조정합니다.</p>
  <div class="aside">코드에서: <code>gamma/parameters.py</code>(표로 정리된 E1 세기, 거대 공명·스핀 뒤집기·가위 모드·상향 굴곡의 계통성), <code>gamma/strength.py</code>(모든 다중극에 대한 <i>f</i>(E<sub>γ</sub>)), <code>gamma/transmission.py</code>(T<sub>γ</sub>와 평균 복사 폭), <code>structure/levels.py</code>(갈래비, 핵이성질체), <code>emission/multiple.py</code>(캐스케이드). 선택 사항, 기본값은 꺼짐: <code>gamma/scissors.py</code>(더 강한 가위 모드), <code>gamma/ggnorm.py</code>(납까지 측정된 ⟨Γγ⟩에 맞춤), <code>gamma/actphys.py</code>(악티늄족에 둘 다 적용).</div>
</div>`,
};
Object.assign(WT.L.labels, {
  // scene 1: emit
  "energy ↑": "에너지 ↑",
  "named levels": "이름 붙은 준위",
  "a crowd of states": "상태의 무리",
  "{#} MeV": "{#} MeV",
  "hot state, {#} MeV": "뜨거운 상태, {#} MeV",
  "most photons ≈ {#} MeV": "가장 흔한 광자 ≈ {#} MeV",
  "small drops: faint (E³ tiny)": "작은 낙하: 희미함 (E³ 작음)",
  "big drops: bright, but few states to land on": "큰 낙하: 밝지만 도착할 상태가 적음",
  // scene 2: gdr
  "protons": "양성자",
  "neutrons": "중성자",
  "A = {#}: rings at {#} MeV": "A = {#}: {#} MeV에서 울림",
  "peak {#} MeV": "봉우리 {#} MeV",
  "giant resonance at {#} MeV": "거대 공명 {#} MeV",
  "width ≈ {#} MeV": "폭 ≈ {#} MeV",
  "decays use this": "붕괴에 쓰이는 부분",
  "shaded: the tail decays use": "음영: 붕괴에 쓰이는 꼬리",
  "photon energy (MeV) →": "광자 에너지 (MeV) →",
  "photon strength f (log scale) ↑": "감마 세기 함수 f (로그 눈금) ↑",
  // scene 3: m1
  "a sphere has no blades: no scissors": "구형에는 날이 없음: 가위 모드 없음",
  "scissors ≈ {#} MeV: strength {#} % of the most stretched": "가위 모드 ≈ {#} MeV: 최대 변형 대비 세기 {#}%",
  "spin-flip ≈ {#} MeV: steady, any shape (thick photons)": "스핀 뒤집기 ≈ {#} MeV: 모양과 무관하게 일정 (굵은 광자)",
  "upbend below {#} MeV: soft photons, plenty at this shape": "{#} MeV 아래 상향 굴곡: 부드러운 광자, 이 모양에선 많음",
  "upbend below {#} MeV: soft photons, fewer at this shape": "{#} MeV 아래 상향 굴곡: 부드러운 광자, 이 모양에선 줄어듦",
  "upbend below {#} MeV: soft photons, few at this shape": "{#} MeV 아래 상향 굴곡: 부드러운 광자, 이 모양에선 적음",
  // scene 4: cascade
  "ground state": "바닥 상태",
  "isomer": "핵이성질체",
  "isomer: long-lived": "핵이성질체: 긴 수명",
  "bins: too dense to list": "구간: 너무 빽빽해 나열 불가",
  "one photon at a time": "한 번에 광자 하나",
  "measured branching ratios": "측정된 갈래비",
  "▬ parity +   ▭ parity −": "▬ 반전성 +   ▭ 반전성 −",
  // scene 5: isomer
  "entrance: J = {#}/{#}": "입구: J = {#}/{#}",
  "isomer: {#} ({#} %)": "핵이성질체: {#} ({#}%)",
  "ground state: {#} ({#} %)": "바닥 상태: {#} ({#}%)",
  "many cascades: ≈ {#} % isomer": "많은 캐스케이드: 핵이성질체 ≈ {#}%",
  "over many cascades from J = {#}/{#}: ≈ {#} % end on the isomer": "J = {#}/{#}에서 시작한 많은 캐스케이드 중 ≈ {#}%가 핵이성질체에서 끝남",
  // scene 6: capture
  "photon door: {#} eV, barely changes": "광자 문: {#} eV, 거의 변하지 않음",
  "captured (n,γ): {#} ({#} %)": "포획 (n,γ): {#} ({#}%)",
  "neutron: {#} eV": "중성자: {#} eV",
  "neutron door: {#} eV, wider when faster": "중성자 문: {#} eV, 빠를수록 넓음",
  "back out: {#} ({#} %)": "되돌아 나감: {#} ({#}%)",
  "more doors open (target left excited)": "더 많은 문이 열림 (표적이 들뜬 채 남음)",
  "{#} eV neutrons →": "{#} eV 중성자 →",
  "{#} keV neutrons →": "{#} keV 중성자 →",
  "{#} MeV neutrons →": "{#} MeV 중성자 →",
  "slow neutrons: the photon door wins": "느린 중성자: 광자 문이 이김",
  "the neutron door wins; capture takes about {#} %": "중성자 문이 이김, 포획은 약 {#}%",
  "fast: capture is a rare event": "빠른 중성자: 포획은 드문 사건",
});
