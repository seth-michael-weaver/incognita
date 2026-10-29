/* Korean: fission (12장, 핵분열) */
WT.L.ch.fission = {
  num: "12장", title: "핵분열", short: "핵분열",
  lead: "가장 무거운 원자핵에는 가벼운 원자핵에 없는 출구가 있습니다. 입자 하나를 내던지는 대신 원자핵 전체가 둘로 찢어지는 것입니다. 이것이 핵분열입니다.",
  html: `
<div class="step">
  <p>무거운 원자핵은 전하를 띤 액체 방울처럼 행동합니다. 표면 장력(회색 화살표)은 방울을 둥글게 당기고, 모두 양전하를 띤 양성자들은 방울을 밀어 벌립니다(빨간 화살표). 우라늄에서는 두 힘이 거의 균형을 이룹니다.</p>
  <div class="ctl"><label for="fis-d">방울 늘이기</label><input id="fis-d" type="range" data-bind="def" min="0" max="1" step="0.01" value="0"><output data-show="def" data-fmt="2"></output></div>
  <p>슬라이더로 방울을 늘이면서 아래 작은 에너지 곡선 위의 점을 지켜보세요. 늘이면 표면이 넓어져 에너지가 들지만, 전하가 퍼지면서 에너지가 방출됩니다. 곡선의 꼭대기를 지나면 전하가 이깁니다. 잘록한 목이 생기고 두 조각이 약 200 MeV를 가지고 날아갑니다.</p>
</div>
<div class="step">
  <h3>퍼텐셜 에너지 곡면</h3>
  <p>곡선은 둥근 모양(왼쪽)부터 쪼개진 모양(오른쪽)까지 모든 모양의 에너지입니다. 매끄러운 액체 방울이라면 언덕이 하나뿐이지만, 핵자들은 <b>껍질</b>이라 불리는 무리를 지어 에너지 준위를 채우고, 가장 무거운 원소에서는 이것이 언덕에 우물을 파 놓습니다. 이것이 원자핵이 늘어난 모양으로 머무를 수 있는 <b>이중 봉우리 장벽</b>입니다.</p>
  <p>엔진은 이 곡선을 가정하지 않습니다. 변형(늘어난 정도)마다 에너지를 계산한 미시적 계산에서 한 점씩 읽어 옵니다.</p>
</div>
<div class="step">
  <h3>장벽 투과</h3>
  <p>공은 첫 번째 골짜기에 있는 들뜬 원자핵으로, 6 MeV 언덕 꼭대기보다 낮은 주황색 점선의 들뜸 에너지에 있습니다. 고전적으로는 결코 넘어갈 수 없지만, 양자역학은 더 어둡게 칠한 금지 영역을 <b>터널링</b>으로 통과하게 해 줍니다. 그 확률 <i>T</i>는 금지 영역이 두꺼워질수록 지수적으로 줄어듭니다.</p>
  <div class="ctl"><label for="fis-e">들뜸 에너지</label><input id="fis-e" type="range" data-bind="E" min="3" max="8" step="0.05" value="5"><output data-show="E" data-fmt="2"></output></div>
  <p>에너지를 올리면서 금지 영역이 얇아지고 <i>T</i>가 커지는 것을 지켜보세요. 교과서식 지름길(힐–휠러, Hill–Wheeler)은 언덕 꼭대기를 포물선(파란 점선)으로 다룹니다. 엔진은 아래로 갈수록 넓어지는 실제 모양을 따르므로, 꼭대기보다 한참 아래에서는 확률이 더 작습니다. <i>K</i>는 앞을 가로막은 언덕이 얼마나 되는지를 나타냅니다.</p>
  <div class="formula">T = 1 / (1 + e<sup>2K</sup>),  K = ∫ √(2μ(V−E)) dβ / ħ</div>
</div>
<div class="step">
  <h3>전이 상태</h3>
  <p>언덕 꼭대기의 문들은 장벽 위로 늘어난 원자핵의 양자 상태인 <b>전이 상태</b>입니다. 각각 스핀과 반전성(0⁺, 2⁻, …)을 가지며 하나의 관문 역할을 합니다. 밝은 틈이 얼마나 열려 있는지를 보여 줍니다. 원자핵은 자신의 스핀과 반전성에 맞는 관문만 통과할 수 있고, 각 관문은 에너지가 그 높이를 지나면서 서서히 열립니다.</p>
  <div class="ctl"><label for="fis-e2">들뜸 에너지</label><input id="fis-e2" type="range" data-bind="E" min="3" max="8" step="0.05" value="5"><output data-show="E" data-fmt="2"></output></div>
  <div class="btns"><button class="btn ghost" data-act="jpAll">모든 스핀</button><button class="btn ghost" data-act="jp0">복합핵 0⁺</button><button class="btn ghost" data-act="jp1">복합핵 1⁻</button></div>
  <p>스핀과 반전성을 하나 골라 보세요. 맞는 관문만 계산에 들어가므로 전체 열림이 줄어듭니다. 더 높은 곳에서는 관문들이 빽빽하게 모여 <b>연속 영역</b>을 이루고, 엔진은 일반 준위에서처럼 그 밀도로 관문을 셉니다.</p>
</div>
<div class="step">
  <h3>이중 봉우리 장벽</h3>
  <p>이제 두 언덕이 모두 있고, 각각 관문(원, 채워진 부분이 열린 정도)이 하나씩 있습니다. 원자핵들은 왼쪽에서 도착합니다. 첫 번째 언덕을 넘은 원자핵은 우물에 갇혀 두 관문 사이를 튕겨 다니다가 어느 한쪽으로 빠져나갑니다. 확률은 직렬로 연결한 저항처럼 합쳐지므로, 대체로 더 어려운 언덕이 결과를 정합니다.</p>
  <div class="ctl"><label for="fis-b">바깥 언덕 높이</label><input id="fis-b" type="range" data-bind="Bb" min="3.5" max="7.5" step="0.05" value="5.6"><output data-show="Bb" data-fmt="2"></output></div>
  <div class="formula">1/T = 1/T<sub>A</sub> + 1/T<sub>B</sub></div>
  <p>바깥 언덕을 높이면, 안쪽 관문이 아무리 열려 있어도 핵분열로 가는 흐름이 막히는 것을 볼 수 있습니다.</p>
</div>
<div class="step">
  <h3>다중 기회 핵분열</h3>
  <p>우라늄-238은 중성자를 흡수하여 들뜸 에너지 <i>E</i>*(점선)를 가진 우라늄-239가 됩니다. 쪼개지지 않으면 대신 중성자를 내보낼 수 있습니다. 그러면 선이 내려가고, 뒤에 남은 여전히 뜨거운 우라늄-238이 자신의 장벽에 도전합니다. 이것이 <b>2차 기회</b> 핵분열 (n,n′f)입니다. 더미에는 각 원자핵이 어떻게 끝났는지가 모입니다.</p>
  <div class="ctl"><label for="fis-en">중성자 에너지</label><input id="fis-en" type="range" data-bind="En" min="0" max="25" step="0.1" value="7"><output data-show="En" data-fmt="1"></output></div>
  <p>에너지를 올리면 나중의 시도들도 성공하기 시작하고, 12 MeV 근처에서 세 번째 기회가 열립니다. 새 기회는 원자핵이 쪼개질 가능성인 측정된 <b>핵분열 단면적</b>에 계단으로 나타납니다. 오른쪽 위의 작은 그래프가 그 계단들을 그리고 지금 에너지를 표시합니다. 엔진은 원자핵이 얼마나 자주 쪼개지는지를 계산하며, 어떤 조각으로 쪼개지는지는 계산하지 않습니다.</p>
  <div class="aside">코드에서: <code>fission/wkb.py</code>(변형 에너지 경로와 WKB 적분), <code>fission/barriers.py</code>(힐–휠러, 전이 상태, 장벽 준위 밀도), <code>fission/transmission.py</code>(직렬 봉우리, 스핀과 반전성별 T<sub>fis</sub>), <code>fission/chain.py</code>(캐스케이드의 모든 원자핵에 대한 장벽).</div>
</div>`,
};
Object.assign(WT.L.labels, {
  // drop
  "surface tension pulls it round": "표면 장력이 둥글게 당김",
  "the protons push it apart": "양성자들이 밀어 벌림",
  "a charged drop, nearly round": "전하를 띤 방울, 거의 둥긂",
  "stretched: more surface, charge further apart": "늘어남: 표면 증가, 전하가 더 멀어짐",
  "a neck forms": "잘록한 목이 생김",
  "two fragments, carrying about {#} MeV": "두 조각, 약 {#} MeV를 가짐",
  "energy of the drop": "방울의 에너지",
  // landscape
  "ground state": "바닥 상태", "inner barrier": "안쪽 장벽", "second well": "두 번째 우물",
  "outer barrier": "바깥 장벽", "split (scission)": "쪼개짐 (절단점)", "one smooth hill": "매끄러운 언덕 하나",
  "shell effects carving the second well": "껍질 효과가 두 번째 우물을 팜",
  "round → stretched → necked → split": "둥긂 → 늘어남 → 목 생김 → 쪼개짐",
  "stretch (deformation) →": "늘어남 (변형) →",
  // tunnel
  "forbidden zone": "금지 영역",
  "excitation {#} MeV": "들뜸 {#} MeV",
  "hilltop {#} MeV": "꼭대기 {#} MeV",
  "parabola fit": "포물선 근사",
  "passes over the top": "꼭대기 위로 넘어감",
  // gates
  "continuum: a density": "연속 영역: 밀도",
  "continuum of gates: counted as a density": "관문의 연속 영역: 밀도로 셈",
  "gates: transition states": "관문: 전이 상태",
  "E = {#} MeV": "E = {#} MeV",
  "all gates: total opening {#}": "모든 관문: 전체 열림 {#}",
  "all gates: total opening {#} + {#} from the continuum": "모든 관문: 전체 열림 {#} + 연속 영역 {#}",
  "{#}⁺ gates only: total opening {#}": "{#}⁺ 관문만: 전체 열림 {#}",
  "{#}⁺ gates only: total opening {#} + {#} from the continuum": "{#}⁺ 관문만: 전체 열림 {#} + 연속 영역 {#}",
  "{#}⁻ gates only: total opening {#}": "{#}⁻ 관문만: 전체 열림 {#}",
  "{#}⁻ gates only: total opening {#} + {#} from the continuum": "{#}⁻ 관문만: 전체 열림 {#} + 연속 영역 {#}",
  // series
  "nuclei arriving →": "도착하는 원자핵 →",
  "trapped in the well": "우물에 갇힘",
  "fission": "핵분열",
  "so far: {#} through, {#} turned back": "지금까지: {#}개 통과, {#}개 되돌아감",
  // chance
  "²³⁹U*  E* = {#} MeV": "²³⁹U*  E* = {#} MeV", "²³⁸U*  E* = {#} MeV": "²³⁸U*  E* = {#} MeV", "²³⁷U*  E* = {#} MeV": "²³⁷U*  E* = {#} MeV",
  "↑ E* above the picture": "↑ E*는 그림 위쪽",
  "fission!": "핵분열!",
  "emits a neutron, cools, tries again": "중성자를 내보내고 식은 뒤 재도전",
  "too cool to split: a photon, no fission": "쪼개지기엔 너무 차가움: 광자 방출, 핵분열 없음",
  "attempt {#}: barrier {#} % open": "{#}번째 시도: 장벽 {#}% 열림",
  "{#}st chance (n,f)": "{#}차 기회 (n,f)", "{#}nd chance (n,n′f)": "{#}차 기회 (n,n′f)", "{#}rd chance (n,{#}nf)": "{#}차 기회 (n,{#}nf)",
  "{#}st (n,f)": "{#}차 (n,f)", "{#}nd (n,n′f)": "{#}차 (n,n′f)", "{#}rd (n,{#}nf)": "{#}차 (n,{#}nf)",
  "no fission": "핵분열 없음",
});
// labels carrying a transmission T, printed either as 0.12 or as 3.4·10⁻5 (two number shapes)
(function () {
  const L = WT.L.labels, F = ["{#}", "{#}·{#}⁻{#}"];
  for (const a of F) {
    L[`inner gate T ≈ ${a}`] = `안쪽 관문 T ≈ ${a}`;
    L[`outer gate T ≈ ${a}`] = `바깥 관문 T ≈ ${a}`;
    L[`both hills: T ≈ ${a}, {#} % of what arrives gets through`] = `두 언덕 모두: T ≈ ${a}, 도착한 것의 {#}% 통과`;
    for (const b of F) {
      L[`T ≈ ${a} real shape · ${b} parabola`] = `T ≈ ${a} 실제 모양 · ${b} 포물선`;
      L[`chance to tunnel T ≈ ${a} on the real shape, ${b} on the parabola`] = `터널링 확률 T ≈ ${a} (실제 모양), ${b} (포물선)`;
    }
  }
})();

// canvas labels added 2026-10-29 (I18NLABELS_B)
Object.assign(WT.L.labels, {
  "chance to split vs neutron energy": "중성자 에너지에 따른 분열 확률",
  "{#}nd": "{#}차",
  "{#}rd": "{#}차",
});
