/* Korean: compound (8장, 복합핵) */
WT.L.ch.compound = {
  num: "8장", title: "복합핵", short: "복합핵",
  lead: "처음의 빠른 충돌이 끝나면 모든 핵자가 에너지를 나눠 갖습니다. 이렇게 자리 잡은 상태가 복합핵입니다. 복합핵이 다음에 무엇을 할지 예측하려면, 엔진은 복합핵이 에너지를 담을 수 있는 방법이 몇 가지인지 알아야 합니다.",
  html: `
<div class="step">
  <p>중성자가 원자핵의 한쪽을 때립니다. 중성자의 에너지와 포획으로 방출된 에너지는 처음에 뜨거운 점(주황색 빛)으로 시작합니다. 충돌을 거치며 에너지가 전달되고, 약 10⁻²¹초 안에 모든 핵자가 제 몫을 나눠 갖습니다.</p>
  <div class="btns"><button class="btn" data-act="hit">다른 쪽에서 때리기</button></div>
  <p>버튼을 눌러 중성자를 다른 쪽에서 들여보내 보세요. 빛은 언제나 같은 모습으로 끝납니다. 원자핵은 <b>자신이 어떻게 만들어졌는지 잊어버린</b> 것입니다. 이것이 보어(Bohr)의 복합핵입니다. 이제부터는 세 가지만 중요합니다. 에너지, 스핀(얼마나 회전하는가), 그리고 반전성(거울 대칭을 나타내는 + 또는 − 꼬리표)입니다.</p>
</div>
<div class="step">
  <h3>불연속 준위에서 연속 영역으로</h3>
  <p>왼쪽 사다리에는 원자핵의 상태들이 있고, 위로 갈수록 에너지가 높습니다. 오른쪽 창은 주황색 공 주위의 1 MeV 조각을 확대합니다. 바닥 근처에서는 가로대 사이가 멀고 하나하나가 측정되어 있습니다. 더 위로 가면 56개 핵자가 에너지를 나누는 방법이 늘어나, 결국 가로대가 흐려져 꽉 찬 띠, 즉 연속 영역이 됩니다.</p>
  <div class="ctl"><label for="cn-e">들뜸 에너지</label><input id="cn-e" type="range" data-bind="E" min="0" max="20" step="0.1" value="6.5"><output data-show="E" data-fmt="1"></output></div>
  <p>들뜸 에너지(가장 낮은 상태보다 위에 담긴 에너지, MeV 단위)를 바꾸며 창을 지켜보세요. MeV당 상태의 수인 <b>준위 밀도</b> ρ는 대략 e<sup>2√(aE)</sup>처럼 증가하며, <i>a</i>가 원자핵마다 그 속도를 정합니다. 3 MeV에서는 MeV당 몇 개, 8 MeV 근처(중성자가 빠져나갈 수 있는 곳)에서는 수백 개, 20 MeV에 이르면 수백만 개입니다. 그 높이에서 엔진은 ρ 자체를 가지고 계산합니다.</p>
</div>
<div class="step">
  <h3>합성 준위 밀도</h3>
  <p>지형의 높이는 로그 눈금으로 나타낸 준위 밀도이고, 오른쪽으로 갈수록 에너지가 높습니다. 왼쪽 아래에는 세어 낸 준위들이 있습니다. 곧은 널빤지는 <b>일정 온도</b> 법칙입니다. 핵온도를 <i>T</i>라 할 때 <i>T</i> MeV마다 ρ가 e배(약 2.7배)가 됩니다. 언덕 비탈은 핵자를 서로 독립인 입자로 다루는 <b>페르미 기체</b>입니다. 표로 만든 밀도를 읽어 오는 가장 무거운 표적을 제외하면, 엔진은 기본적으로 이 한 쌍을 사용합니다.</p>
  <div class="ctl"><label for="cn-ex">접속 에너지</label><input id="cn-ex" type="range" data-bind="Ex" min="4.5" max="12" step="0.05" value="6"><output data-show="Ex" data-fmt="1"></output></div>
  <p>접속 에너지를 바꿔 보세요. 이음매가 언덕을 따라 미끄러지고, 널빤지가 같은 높이와 기울기로 만나도록 회전합니다. 아래의 두 더미는 널빤지가 예측하는 준위와 실제로 세어 낸 준위를 비교합니다. 둘을 같게 만드는 이음매는 하나뿐이며, 그때 널빤지가 초록색으로 바뀝니다. 그것이 엔진이 고르는 에너지입니다.</p>
</div>
<div class="step">
  <h3>껍질 효과와 그 감쇠</h3>
  <p>두 원자핵의 단일 핵자 준위로, 준위마다 핵자 두 개가 들어갑니다. 왼쪽은 닫힌 껍질입니다. 큰 간격 아래가 모두 차 있어서 어떤 이동이든 간격 전체만큼의 대가를 치러야 합니다. 오른쪽은 맨 위 준위가 반쯤 찬 껍질 중간의 원자핵이어서, 값싼 이동이 곧바로 가능합니다. 각 계수기는 주어진 열을 담는 배치가 몇 가지인지 보여 줍니다.</p>
  <div class="ctl"><label for="cn-u">열 (들뜸)</label><input id="cn-u" type="range" data-bind="U" min="0" max="40" step="0.5" value="3"><output data-show="U" data-fmt="1"></output></div>
  <p>열을 올리며 핵자들이 뛰어오르는 것을 지켜보세요. 열이 적을 때 닫힌 껍질은 배치가 턱없이 부족합니다. 열이 충분하면 간격은 더 이상 중요하지 않고 두 수가 비슷하게 늘어납니다. 엔진은 이를 원자핵마다 숫자 하나, 곧 <b>준위 밀도 매개변수</b> <i>a</i>로 요약합니다. <i>a</i>가 클수록 열에 따라 배치의 수가 더 빨리 늘어납니다. 바늘들이 원자핵별로 이를 보여 줍니다. 서로 떨어져 출발하여 약 10 MeV에 걸쳐 둘 다 같은 매끄러운 값(<i>ã</i>, "a-틸데"라고 읽음), 곧 껍질 간격이 없는 원자핵이 가질 값으로 모입니다.</p>
  <p>그래서 엔진은 각 원자핵을 껍질 효과, 곧 간격이 지니는 추가 에너지(δW라고 씁니다)와 함께 출발시키고, 열이 오를수록 그 효과가 사라지게 합니다.</p>
  <div class="aside">공식: <i>a</i>(<i>U</i>) = <i>ã</i> · [1 + δW · (1 − e<sup>−γ<i>U</i></sup>) / <i>U</i>]. 여기서 <i>U</i>는 열이고, γ(감마, 여기서는 MeV당 약 0.1이며 무거운 원자핵에서는 더 작음)는 껍질 효과가 얼마나 빨리 사라지는지를 나타냅니다.</div>
</div>
<div class="step">
  <h3>스핀과 반전성의 분포</h3>
  <p>한 에너지의 상태들은 원자핵의 각운동량인 스핀 <i>J</i>에 따라 서랍에 나뉘어 들어갑니다. + 반전성은 속이 찬 토큰, −는 속이 빈 토큰입니다. 가운데 서랍이 가장 많이 차며, (2<i>J</i>+1) e<sup>−(J+½)²/2σ²</sup>를 따릅니다. 여기서 스핀 차단 매개변수 σ가 퍼짐을 정합니다. 두 반전성은 거의 같은 수로 나옵니다.</p>
  <div class="ctl"><label for="cn-u2">들뜸</label><input id="cn-u2" type="range" data-bind="U2" min="1" max="30" step="0.5" value="8"><output data-show="U2" data-fmt="1"></output></div>
  <div class="btns"><button class="btn ghost" data-act="deform">원자핵 변형하기</button></div>
  <p>들뜸을 올려 보세요. 더 뜨거운 원자핵은 더 큰 스핀을 지닐 수 있으므로 σ가 커집니다. 이제 변형 버튼을 누르세요. 럭비공 모양의 원자핵은 전체로서 회전할 수도 있어서 모든 서랍에 상태가 늘어납니다(파란 토큰). 이것이 <b>집단 증강</b>입니다. 엔진은 기본적으로 핵자가 약 215개보다 많은 표적에만 이를 더합니다.</p>
</div>
<div class="step">
  <h3>연속 영역의 에너지 구간</h3>
  <p>마지막으로 세어 낸 준위 위에서는 엔진이 연속 영역을 같은 에너지 폭의 조각, 즉 구간(bin)으로 자릅니다. 각 구간 안에서 점들은 ρ·ΔE개 상태(ΔE는 구간 폭)를 담은 하나의 덩어리로 합쳐지며, 위와 같이 스핀과 반전성으로 분류됩니다.</p>
  <div class="ctl"><label for="cn-emax">사다리 꼭대기</label><input id="cn-emax" type="range" data-bind="Emax" min="8" max="30" step="0.5" value="14"><output data-show="Emax" data-fmt="1"></output></div>
  <div class="btns"><button class="btn ghost" data-act="rebin">다시 분류</button></div>
  <p>중성자가 가져올 수 있는 최대 에너지인 사다리 꼭대기를 바꿔 보세요. 같은 수의 구간이 더 넓은 에너지를 덮어야 하므로 각 구간이 높아집니다. 주황색 공은 구간에서 구간으로 떨어집니다. 이후의 모든 단계(출구 고르기, 광자 캐스케이드, 핵종 도표를 따라 내려가기)는 이 구간들 위에서 이루어집니다. 여기에는 열 개를 그렸고, 엔진은 최대 40개를 씁니다.</p>
  <div class="aside">코드에서: <code>density/parameters.py</code>(이그나티우크 <i>a</i>(U), 스핀 차단, 위그너 분포, 집단 증강), <code>density/models.py</code>(일정 온도, 페르미 기체, 표), <code>density/matching.py</code>(세어 낸 준위로부터 구한 접속 에너지), <code>core/grids.py</code>(들뜸 에너지 구간).</div>
</div>`,
};
(function () {
  const L = {
    // scene 1
    "a neutron comes in": "중성자가 들어옴",
    "a hot spot: the energy is still local": "뜨거운 점: 에너지가 아직 한곳에",
    "equilibrium: every nucleon holds a share": "평형: 모든 핵자가 제 몫을 가짐",
    "no trace left of where it was hit": "어디를 맞았는지 흔적이 없음",
    // scene 2
    "ground state": "바닥 상태",
    "{#}–{#} MeV, magnified": "{#}–{#} MeV, 확대",
    "no level in this slice": "이 구간에 준위 없음",
    "{#} rung in {#} MeV": "가로대 {#}개 / {#} MeV",
    "{#} rungs in {#} MeV": "가로대 {#}개 / {#} MeV",
    "{#} rung in this {#}-MeV slice": "가로대 {#}개 ({#} MeV 구간)",
    "{#} rungs in this {#}-MeV slice": "가로대 {#}개 ({#} MeV 구간)",
    "about {#} rungs: too close to draw": "가로대 약 {#}개: 너무 촘촘해 그릴 수 없음",
    "about {#}k rungs: too close to draw": "가로대 약 {#}천 개: 너무 촘촘해 그릴 수 없음",
    "about {#}M rungs: too close to draw": "가로대 약 {#}백만 개: 너무 촘촘해 그릴 수 없음",
    "about {#}B rungs: too close to draw": "가로대 약 {#}십억 개: 너무 촘촘해 그릴 수 없음",
    "about {#} rungs in this slice: too close to draw": "이 구간에 가로대 약 {#}개: 너무 촘촘해 그릴 수 없음",
    "about {#} thousand rungs in this slice: too close to draw": "이 구간에 가로대 약 {#}천 개: 너무 촘촘해 그릴 수 없음",
    "about {#} million rungs in this slice: too close to draw": "이 구간에 가로대 약 {#}백만 개: 너무 촘촘해 그릴 수 없음",
    "about {#} billion rungs in this slice: too close to draw": "이 구간에 가로대 약 {#}십억 개: 너무 촘촘해 그릴 수 없음",
    "each one measured: energy, spin and parity": "하나하나 측정됨: 에너지, 스핀, 반전성",
    "the rungs are multiplying": "가로대가 늘어나는 중",
    "a continuum: the engine uses ρ itself": "연속 영역: 엔진은 ρ 자체를 사용",
    "≈ energy to free a neutron": "≈ 중성자를 떼어 내는 에너지",
    "energy ↑": "에너지 ↑",
    // scene 3
    "gap: plank below the rungs": "차이: 널빤지가 가로대보다 아래",
    "gap: plank above the rungs": "차이: 널빤지가 가로대보다 위",
    "counted levels": "세어 낸 준위",
    "CT plank": "CT 널빤지",
    "constant-temperature plank": "일정 온도 널빤지",
    "Fermi-gas hillside": "페르미 기체 비탈",
    "joint {#} MeV": "이음매 {#} MeV",
    "energy →": "에너지 →",
    "+{#} more": "+{#}개 더",
    "{#} counted": "{#}개 셈",
    "{#} predicted": "{#}개 예측",
    "{#}+ predicted": "{#}개 이상 예측",
    "equal: the plank rests on the counted rungs": "같음: 널빤지가 세어 낸 가로대 위에 놓임",
    "too few: the plank is too steep and sinks": "너무 적음: 널빤지가 너무 가팔라 가라앉음",
    "too many: the plank is too shallow and floats": "너무 많음: 널빤지가 너무 완만해 뜸",
    // scene 4
    "closed shell": "닫힌 껍질",
    "mid-shell": "껍질 중간",
    "gap": "간격",
    "no arrangement holds this heat": "이 열을 담는 배치 없음",
    "≈ {#} arrangement": "≈ {#}가지 배치",
    "≈ {#} arrangements": "≈ {#}가지 배치",
    "≈ {#} thousand arrangements": "≈ {#}천 가지 배치",
    "≈ {#} million arrangements": "≈ {#}백만 가지 배치",
    "≈ {#} billion arrangements": "≈ {#}십억 가지 배치",
    "a ≈ {#}": "a ≈ {#}",
    "cold: nobody can move": "차가움: 아무도 움직일 수 없음",
    "temperature ≈ {#} MeV": "온도 ≈ {#} MeV",
    // scene 5
    "states at {#} MeV": "{#} MeV의 상태",
    "spin J →": "스핀 J →",
    "+ parity": "+ 반전성",
    "− parity": "− 반전성",
    "rotation ×{#}": "회전 ×{#}",
    "added by rotation: ×{#} (a few drawn)": "회전으로 추가: ×{#} (일부만 그림)",
    "spread σ ≈ {#}: most states near J ≈ {#}": "퍼짐 σ ≈ {#}: 대부분 J ≈ {#} 근처",
    "deformed: it can rotate": "변형됨: 회전 가능",
    "spherical": "구형",
    // scene 6
    "≈ {#} thousand": "≈ {#}천",
    "≈ {#} million": "≈ {#}백만",
    "≈ {#} billion": "≈ {#}십억",
    "≈ {#}k": "≈ {#}천",
    "≈ {#}M": "≈ {#}백만",
    "≈ {#}B": "≈ {#}십억",
    "{#} bins, each {#} MeV wide": "구간 {#}개, 각 {#} MeV 폭",
    "counted": "세어 낸 수",
    "states in each bin": "구간별 상태 수",
  };
  Object.assign(WT.L.labels, L);
})();
