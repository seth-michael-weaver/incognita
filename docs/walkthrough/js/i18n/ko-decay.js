/* Korean: decay (9장, 출구 고르기) */
WT.L.ch.decay = {
  num: "9장", title: "복합핵의 붕괴", short: "붕괴",
  lead: "복합핵은 입자나 광자를 내보내 에너지를 털어 내야 합니다. 이 장에서는 빠져나가는 길 하나하나를 문으로 그립니다. 엔진이 할 일은 선속(이곳에 도착하는 반응의 흐름) 중 어느 만큼이 각 문으로 나가는지 말하는 것입니다.",
  html: `
<div class="step">
  <p>출구마다 문이 하나씩 있습니다. <em class="g">광자</em>(γ), <em class="n">중성자</em>(n), <em class="p">양성자</em>(p), <em class="a">알파 입자</em>(α: 양성자 둘과 중성자 둘), 그리고 무거운 원자핵에만 있는 <em class="f">핵분열</em>(둘로 쪼개짐)입니다. 각 문의 밝은 틈은 그 출구의 몫이며, 공들도 같은 비율로 흘러나옵니다. 회색 문은 닫혀 있습니다. 자신이 어떻게 만들어졌는지 잊어버린 원자핵은 각 문 b를 가중치에 비례하여 사용합니다.</p>
  <div class="formula">몫<sub>b</sub> = T<sub>b</sub> · ρ<sub>b</sub> / Σ<sub>c</sub> T<sub>c</sub> · ρ<sub>c</sub></div>
  <p><b>투과 계수</b> <i>T</i>는 가장자리에 도달한 입자가 빠져나갈 확률이며, 입자의 경우 5장의 광학 모형을 거꾸로 돌려 얻습니다. 각 문 옆에 적힌 <b>준위 밀도</b> ρ는 남은 원자핵이 도달할 수 있는 상태의 수를 셉니다. <i>T</i> 곱하기 ρ로 나누는 것이 <b>하우저–페시바흐</b> 규칙입니다. 10 MeV에서는 중성자 문이 거의 모든 것을 가져갑니다.</p>
</div>
<div class="step">
  <h3>증발 스펙트럼</h3>
  <p>중성자 문을 나가는 에너지 ε에 따라 나눈 것입니다(왼쪽이 느림, 오른쪽이 빠름). 각 문의 틈 <i>T</i>(ε)는 중성자가 빠를수록 넓어집니다. 그 아래에는 남은 원자핵이 있을 수 있는 상태의 무리가 있습니다. 느린 중성자는 에너지 대부분을 남겨 두고 가는데, 그곳에는 상태가 풍부하므로 무리는 오른쪽으로 갈수록 줄어듭니다.</p>
  <div class="ctl"><label for="dc-sp">여유 에너지</label><input id="dc-sp" type="range" data-bind="spare" min="1" max="12" step="0.5" value="5"><output data-show="spare" data-fmt="1"></output></div>
  <p>문 × 무리가 더미를 언덕 모양으로 만듭니다. 뜨거운 액체에서 김이 빠져나가는 것과 비슷한 <b>증발 스펙트럼</b>입니다. 여유 에너지(MeV, 백만 전자볼트)를 바꿔 보세요. 더미가 다시 쌓이는데, 봉우리는 핵온도가 정하는 1 MeV 근처에 머뭅니다. 여분의 에너지는 대부분 남은 원자핵을 더 뜨겁게 만들 뿐입니다.</p>
</div>
<div class="step">
  <h3>방출에서의 쿨롱 장벽</h3>
  <p>중심에서 거리 r에 따른 양성자의 에너지입니다. 안쪽은 우물이고, 바깥쪽은 전기적(쿨롱) 반발로 생긴 언덕으로 1/r처럼 줄어듭니다. 언덕 꼭대기보다 낮은 에너지에서는 우물 안에서 덜컹거리는 양성자가 음영 부분을 <b>터널링</b>으로만 통과할 수 있습니다. 벽을 여러 번 두드려야 한 번 성공하는 양자 효과입니다. 확률은 4장에서와 같은 방식으로 구합니다. 그 구간이 넓고 높을수록 “10<sup>N</sup>번 두드려 한 번”의 0이 더 많아집니다.</p>
  <div class="ctl"><label for="dc-ce">입자 에너지</label><input id="dc-ce" type="range" data-bind="eps" min="0.5" max="12" step="0.1" value="3"><output data-show="eps" data-fmt="1"></output></div>
  <div class="btns"><button class="btn ghost" data-act="toggleAlpha">양성자 / 알파 전환</button></div>
  <p>에너지를 내리며 터널이 넓어지는 것을 지켜보세요. 그다음 알파로 바꿔 보세요. 전하가 둘인 알파는 약 두 배 높은 언덕을 마주합니다. 그래서 전하가 없는 중성자는 떠날 수만 있으면 대개 이기며, 양성자와 알파 출구는 주로 가벼운 원자핵과 높은 에너지에서 중요합니다.</p>
</div>
<div class="step">
  <h3>채널 문턱</h3>
  <p>각 입자의 문은 그 입자를 끄집어내는 비용인 <b>분리 에너지</b>보다 위에서만 열립니다. 여기서는 중성자가 8 MeV, 양성자가 9 MeV, 알파가 7 MeV입니다. 중성자의 8 MeV보다 아래에서는 거의 모든 붕괴가 빛을 냅니다.</p>
  <div class="ctl"><label for="dc-e">들뜸 에너지</label><input id="dc-e" type="range" data-bind="E" min="5" max="24" step="0.1" value="7"><output data-show="E" data-fmt="1"></output></div>
  <p>들뜸 에너지를 8 MeV 너머로 올려 보세요. 약 1 MeV 안에서 중성자 문이 활짝 열리고 광자의 몫은 백분의 일로 떨어집니다. 알파의 문은 7 MeV에서 가장 먼저 잠금이 풀리지만 거의 열리지 않습니다. 쿨롱 언덕(4장)이 훨씬 높은 에너지까지 문을 거의 닫아 두기 때문입니다. 양성자의 문은 9 MeV에서 잠금이 풀리며, 마찬가지로 자기 언덕에 막혀 좁게 남습니다.</p>
</div>
<div class="step">
  <h3>각운동량과 반전성의 보존</h3>
  <p>복합핵(위)은 스핀 <i>J</i>를 가집니다. 남은 원자핵의 상태들은 아래에서 스핀 <i>J</i>′별 서랍에 들어 있습니다. 중성자는 스핀과 반전성의 차이를 가지고 나갑니다. 궤도 각운동량 <i>l</i>로 떠나면 스핀을 최대 <i>l</i> + ½만큼 바꾸고, <i>l</i>이 홀수이면 반전성을 뒤집습니다. <i>l</i>이 클수록 문이 좁아집니다. 각 서랍의 문은 그 서랍에 닿는 가장 작은 <i>l</i>입니다. 속이 찬 착지는 반전성을 유지하고, 속이 빈 착지는 뒤집습니다.</p>
  <div class="ctl"><label for="dc-j">복합핵 스핀 J</label><input id="dc-j" type="range" data-bind="J" min="0" max="10" step="1" value="2" data-instant><output id="dc-jout">5/2</output></div>
  <p><i>J</i>를 올려 보세요. 열린 문들이 상태가 적은 고스핀 서랍 쪽으로 옮겨 가고, 가득 찬 서랍은 닫힌 문 뒤에 놓입니다. 고스핀 복합핵은 입자를 잘 내보내지 못하므로, 광자와 핵이성질체(오래 사는 상태, 10장)에게 기회가 돌아갑니다.</p>
</div>
<div class="step">
  <h3>탄성 증강</h3>
  <p>낮은 에너지에서 복합핵은 날카로운 <b>공명</b>, 즉 중성자가 쉽게 흡수되는 에너지들의 모임입니다. 여기에는 한 줄에 하나씩 여덟 개를 그렸습니다. 각 공명의 문 폭은 무작위입니다. 왼쪽은 입구(중성자 채널)로 폭이 <i>x</i>이고, 오른쪽은 다른 문들로 여기서는 대부분 광자이며 폭이 <i>y</i>입니다.</p>
  <div class="btns"><button class="btn" data-act="fire">중성자 40개 발사</button><button class="btn ghost" data-act="reroll">새 공명</button></div>
  <p>발사 버튼을 누르고 중성자를 따라가 보세요. 중성자는 그 줄의 입구 폭 <i>x</i>에 비례해 줄 안으로 들어갑니다. 안에 들어가면 폭에 비례해 나가는 길을 고릅니다. <i>x</i> / (<i>x</i> + Σ<i>y</i>)의 확률로 입구를 통해 되돌아가고, 그렇지 않으면 다른 문 중 하나로 나갑니다. 쟁반이 어디로 갔는지 셉니다.</p>
  <p>핵심은 이렇습니다. 입구가 넓은 줄은 더 많은 중성자를 받아들이고 더 많이 되돌려 보내기도 합니다. 그래서 평균 폭만으로 짐작하는 것보다 더 많은 중성자가 되돌아옵니다. 실제로 되돌아가는 몫(<b>곱의 평균</b>)이 단순한 어림값(<b>평균의 곱</b>)보다 큽니다. 둘 다 맨 위에 적혀 있습니다.</p>
  <p>그 비가 <b>탄성 증강</b>입니다. 엔진의 <b>폭 요동 보정</b>이 이를 적용합니다. 그만큼의 추가 선속을 다른 문에서 입구로 옮기는 것입니다.</p>
  <div class="ctl"><label for="dc-n">다른 문</label><input id="dc-n" type="range" data-bind="Nch" min="1" max="12" step="1" value="2" data-instant><output data-show="Nch" data-fmt="0"></output></div>
  <p>문을 늘려 보세요. 출구가 많으면 전체 폭이 더 이상 요동하지 않으므로, 이 보정은 열린 문이 적을 때 가장 중요합니다. 엔진은 입사 중성자 에너지가 표적의 중성자 분리 에너지 이하일 때 몰다우어(Moldauer)의 공식으로 이를 적용하고, 그 위에서는 적용하지 않습니다.</p>
</div>
<div class="step">
  <h3>직접 반응 뒤의 선속</h3>
  <p>이 장의 문들은 실제로 남아 있는 중성자만 나눕니다. 6장과 7장이 이미 제 몫을 가져갔습니다. 일부 중성자는 한 번 스치듯 부딪히고 날아가며(직접 반응), 일부는 한두 번 부딪힌 뒤 빠르게 튀어 나갑니다(전평형). 나머지만 안에 남아 원자핵을 달굽니다. 오른쪽의 계수기가 각 운명을 집계합니다. 남는 것들은 원자핵을 떠나지 않으며, 그저 세어질 뿐입니다.</p>
  <div class="ctl"><label for="dc-einc">중성자 에너지</label><input id="dc-einc" type="range" data-bind="Einc" min="1" max="30" step="0.5" value="8"><output data-show="Einc" data-fmt="1"></output></div>
  <p>남은 것만 문 경쟁에 참가합니다. 중성자 에너지를 바꿔 보세요. 몇 MeV에서는 거의 모두 남지만, 30 MeV가 되면 약 절반이 평형에 이르기 전에 떠납니다.</p>
  <div class="aside">코드에서: <code>compound/prepare.py</code>(스핀과 반전성별 출구 가중치 T·ρ, 선택 규칙), <code>compound/target.py</code>(폭 요동을 넣은 첫 붕괴), <code>compound/continuum.py</code>(이후 모든 구간의 붕괴), <code>compound/wfc.py</code>(Moldauer, HRTW, GOE 보정), <code>compound/normalization.py</code>(복합핵에 남은 선속), <code>omp/inverse.py</code>(거꾸로 돌린 문).</div>
</div>`,
};
(function () {
  const L = {
    "{#} MeV": "{#} MeV",
    "n": "n", "p": "p", "fission": "핵분열",
    "heavy only": "무거운 핵만",
    "heavy nuclei only": "무거운 원자핵만",
    "shut below {#} MeV": "{#} MeV 아래에서 닫힘",
    "the neutron door takes nearly everything": "중성자 문이 거의 모두 가져감",
    "below the neutron threshold, nearly all decays emit light": "중성자 문턱 아래: 거의 모든 붕괴가 빛을 냄",
    "the doors share the decays": "문들이 붕괴를 나눠 가짐",
    // hump
    "{#} MeV to spare": "여유 {#} MeV",
    "door gap = T(ε)": "문 틈 = T(ε)",
    "doors: one per neutron energy ε, gap = T(ε)": "문: 중성자 에너지 ε마다 하나, 틈 = T(ε)",
    "× states left behind": "× 남은 상태",
    "× states the leftover nucleus can be in: many after a slow neutron": "× 남은 원자핵이 가질 수 있는 상태: 느린 중성자 뒤엔 많음",
    "most ≈ {#} MeV": "최빈값 ≈ {#} MeV",
    "= the pile": "= 더미",
    "= where the neutrons land: the evaporation spectrum": "= 중성자가 쌓이는 곳: 증발 스펙트럼",
    "slow": "느림",
    "slow neutrons": "느린 중성자",
    "fast: {#} MeV →": "빠름: {#} MeV →",
    "fast: {#} MeV (beyond, up to {#}, almost none)": "빠름: {#} MeV (그 너머 {#}까지는 거의 없음)",
    "fast: {#}": "빠름: {#}",
    "fast: {#} MeV, the neutron takes it all": "빠름: {#} MeV, 중성자가 전부 가져감",
    // coulomb
    "well ↓": "우물 ↓",
    "well (much deeper) ↓": "우물 (훨씬 깊음) ↓",
    "hilltop ≈ {#} MeV": "꼭대기 ≈ {#} MeV",
    "falls as {#}/r": "{#}/r처럼 감소",
    "Coulomb hill, falling as {#}/r": "쿨롱 언덕, {#}/r처럼 감소",
    "tunnel: wider than the picture": "터널: 그림보다 넓음",
    "tunnel {#} fm": "터널 {#} fm",
    "proton energy {#} MeV": "양성자 에너지 {#} MeV",
    "alpha energy {#} MeV": "알파 에너지 {#} MeV",
    "proton energy {#} MeV ↑": "양성자 에너지 {#} MeV ↑",
    "alpha energy {#} MeV ↑": "알파 에너지 {#} MeV ↑",
    "above the hilltop: it rolls straight out": "꼭대기 위: 곧장 굴러 나감",
    "below the top, must tunnel: nearly every knock gets through": "꼭대기 아래, 터널링: 거의 매번 통과",
    "below the top, must tunnel: about {#} knock in {#} gets through": "꼭대기 아래, 터널링: 약 {#}/{#}번꼴로 통과",
    "below the top, must tunnel: about {#} knock in {#} × {#}^{#} gets through": "꼭대기 아래, 터널링: 약 {#}/({#} × {#}^{#})번꼴로 통과",
    "out": "밖",
    "through after {#} knock": "{#}번 두드린 뒤 통과",
    "through after {#} knocks": "{#}번 두드린 뒤 통과",
    "knocks so far: {#}": "두드린 횟수: {#}",
    "distance r from the centre (fm) →": "중심으로부터 거리 r (fm) →",
    // spin
    "J = {#}/{#}, parity +": "J = {#}/{#}, 반전성 +",
    "l={#}": "l={#}",
    "leftover states by spin J′ →": "스핀 J′별 남은 상태 →",
    "drawers: states of the leftover nucleus by spin J′ (faint: states it holds) →": "서랍: 스핀 J′별 남은 원자핵의 상태 (흐린 것: 담긴 상태) →",
    "open doors reach {#} %": "열린 문이 닿는 상태 {#}%",
    "open doors reach about {#} % of the states": "열린 문이 상태의 약 {#}%에 닿음",
    "● parity kept (even l)   ○ flipped (odd l)": "● 반전성 유지 (짝수 l)   ○ 뒤집힘 (홀수 l)",
    // wfc
    "entrance x": "입구 x",
    "entrance, width x": "입구, 폭 x",
    "{#} other doors, y": "다른 문 {#}개, y",
    "{#} other door, widths y": "다른 문 {#}개, 폭 y",
    "{#} other doors, widths y": "다른 문 {#}개, 폭 y",
    "back out the entrance: {#} of {#}": "입구로 되돌아감: {#} / {#}",
    "out another door: {#}": "다른 문으로 나감: {#}",
    // norm
    "absorbed neutrons, {#} MeV →": "흡수된 중성자, {#} MeV →",
    "direct: {#} %": "직접: {#}%",
    "pre-equilibrium: {#} %": "전평형: {#}%",
    "compound nucleus: {#} %": "복합핵: {#}%",
    "one glancing hit on the surface": "표면을 한 번 스침",
    "a knock or two, then out fast": "한두 번 부딪힌 뒤 빠르게 나감",
    "stayed: on to the door competition": "남음: 문 경쟁으로",
  };
  // door hint with level-count wording (fmt: "1", "N", "N thousand", "N million") and T possibly in e-notation
  const cnt = [["{#} state", "상태 {#}개"], ["{#} states", "상태 {#}개"], ["{#} thousand states", "상태 {#}천 개"], ["{#} million states", "상태 {#}백만 개"]];
  for (const [e, s] of cnt) {
    L[`weak door × ≈ ${e}`] = `약한 문 × ≈ ${s}`;
    L[`T ≈ {#} × ≈ ${e}`] = `T ≈ {#} × ≈ ${s}`;
    L[`T ≈ {#}e{#} × ≈ ${e}`] = `T ≈ {#}e{#} × ≈ ${s}`;
  }
  // share comparisons: each pct is "{#} %" or "≈ {#} %"
  const P = ["{#} %", "≈ {#} %"];
  for (const a of P) for (const b of P) {
    L[`back out ${a}, not ${b}: × {#}`] = `되돌아감 ${a} (${b} 아님): × {#}`;
    L[`share back out: average of products ${a} · product of averages ${b} · × {#}`] = `되돌아가는 몫: 곱의 평균 ${a} · 평균의 곱 ${b} · × {#}`;
    L[`other doors ${a}, not ${b}`] = `다른 문 ${a} (${b} 아님)`;
    L[`other doors together: ${a} instead of ${b}`] = `다른 문 합계: ${a} (${b} 대신)`;
  }
  Object.assign(WT.L.labels, L);
})();
