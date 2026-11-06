/* Korean: breeding (새 연료의 증식) */
WT.L.ch.breeding = {
  num: "강의 1", title: "새 연료의 증식", short: "증식",
  html: `
<div class="step">
  <h3>친원료가 핵분열성 물질이 된다</h3>
  <p>우라늄-238은 거의 쪼개지지 않지만 중성자를 포획할 수는 있습니다. 베타 붕괴를 두 번 거치면(매번 안의 중성자 하나가 양성자로 바뀝니다) 쉽게 쪼개지는 플루토늄-239가 됩니다. 토륨-232도 같은 과정을 거쳐 우라늄-233이 됩니다.</p>
  <div class="btns"><button class="btn ghost" data-act="bcU" aria-pressed="true">우라늄-238</button> <button class="btn ghost" data-act="bcT" aria-pressed="false">토륨-232</button></div>
</div>
<div class="step">
  <h3>중성자 수지</h3>
  <p>핵분열성 연료에 흡수된 중성자 하나는 새 중성자 <i>η</i>개를 돌려줍니다. 하나는 다음 핵분열을 일으켜야 하고 일부는 잃어버리며, 남는 것이 증식에 쓰일 수 있습니다. 우라늄-235와 느린 중성자로는 하나를 태울 때 새 핵분열성 원자핵이 약 0.6개만 만들어집니다.</p>
  <div class="btns"><button class="btn ghost" data-act="bfU5" aria-pressed="true">U-235</button> <button class="btn ghost" data-act="bfP9" aria-pressed="false">Pu-239</button> <button class="btn ghost" data-act="bfU3" aria-pressed="false">U-233</button></div>
  <div class="btns"><button class="btn ghost" data-act="bsT" aria-pressed="true">느린 중성자</button> <button class="btn ghost" data-act="bsF" aria-pressed="false">빠른 중성자</button></div>
</div>
<div class="step">
  <h3>빠른 중성자는 증식한다</h3>
  <p>증식하려면 중성자 하나는 연쇄를 이어 가고 적어도 하나는 새 연료를 만들어야 하므로, <i>η</i>가 손실분 이상으로 2를 넘어야 합니다. 고속로 속 플루토늄-239는 약 2.4를 주므로 여유가 있습니다.</p>
  <div class="ctl"><label for="br-l1">잃는 중성자</label><input id="br-l1" type="range" data-bind="L" data-instant min="0.05" max="0.8" step="0.01" value="0.2"><output data-show="L" data-fmt="2"></output></div>
</div>
<div class="step">
  <h3>느린 중성자와 토륨</h3>
  <p>느린 중성자에서 플루토늄-239는 약 2.1밖에 주지 않지만, 우라늄-233은 2.29를 줍니다. 이 여유 덕분에 토륨 원자로는 중성자를 아주 적게 낭비한다면 느린 중성자로도 증식할 수 있습니다. 증식할 때까지 손실을 낮춰 보세요.</p>
  <div class="ctl"><label for="br-l2">잃는 중성자</label><input id="br-l2" type="range" data-bind="L" data-instant min="0.05" max="0.8" step="0.01" value="0.35"><output data-show="L" data-fmt="2"></output></div>
</div>
<div class="step">
  <h3>전환비</h3>
  <p>전환비는 핵분열성 원자핵 하나를 태울 때 새로 만들어지는 핵분열성 원자핵의 수입니다. 1보다 작으면 연료가 서서히 줄고(오늘날의 경수로 같은 전환로), 1보다 크면 원자로는 처음보다 많은 연료를 가지고 끝납니다(증식로).</p>
  <div class="btns"><button class="btn ghost" data-act="bfU5" aria-pressed="true">U-235</button> <button class="btn ghost" data-act="bfP9" aria-pressed="false">Pu-239</button> <button class="btn ghost" data-act="bfU3" aria-pressed="false">U-233</button></div>
  <div class="btns"><button class="btn ghost" data-act="bsT" aria-pressed="true">느린 중성자</button> <button class="btn ghost" data-act="bsF" aria-pressed="false">빠른 중성자</button></div>
</div>`,
};

Object.assign(WT.L.labels, {
  "+ n": "+ n",
  "Np{#}": "Np{#}",
  "Pa{#}": "Pa{#}",
  "Pu{#}": "Pu{#}",
  "Th{#}": "Th{#}",
  "U{#}": "U{#}",
  "Th{#} (fertile)": "Th{#} (친원료)",
  "U{#} (fertile)": "U{#} (친원료)",
  "Th{#} → U{#}": "Th{#} → U{#}",
  "U{#} → Pu{#}": "U{#} → Pu{#}",
  "a batch of {a} waiting · day {b}": "{a} 한 무리가 대기 중 · {b}일째",
  "{a} waiting: day {b}": "{a} 대기: {b}일째",
  "after {#} months, {#} % has become U{#}": "{#}개월 뒤 {#} %가 U{#}로 바뀜",
  "after {#} weeks, {#} % has become Pu{#}": "{#}주 뒤 {#} %가 Pu{#}로 바뀜",
  "antineutrino": "반중성미자",
  "electron": "전자",
  "e⁻": "e⁻",
  "breed": "증식",
  "chain": "연쇄",
  "lost": "손실",
  "catch": "포획",
  "breeds: Th{#} → U{#}": "증식: Th{#} → U{#}",
  "breeds: U{#} → Pu{#}": "증식: U{#} → Pu{#}",
  "burned {a}": "태운 것 {a}",
  "made {a}": "만든 것 {a}",
  "conversion ratio {a}: a breeder": "전환비 {a}: 증식로",
  "conversion ratio {a}: a converter": "전환비 {a}: 전환로",
  "conversion ratio ≈ η − {#} − lost = {a}: breeds": "전환비 ≈ η − {#} − 손실 = {a}: 증식",
  "conversion ratio ≈ η − {#} − lost = {a}: breeds, makes more fuel than it burns": "전환비 ≈ η − {#} − 손실 = {a}: 증식, 태우는 것보다 많은 연료를 만듦",
  "conversion ratio ≈ η − {#} − lost = {a}: converts": "전환비 ≈ η − {#} − 손실 = {a}: 전환",
  "conversion ratio ≈ η − {#} − lost = {a}: converts, makes less fuel than it burns": "전환비 ≈ η − {#} − 손실 = {a}: 전환, 태우는 것보다 적은 연료를 만듦",
  "fast neutrons": "빠른 중성자",
  "slow neutrons": "느린 중성자",
  "{a} · fast neutrons": "{a} · 빠른 중성자",
  "{a} · slow neutrons": "{a} · 느린 중성자",
  "fertile": "친원료",
  "fertile: barely splits": "친원료: 거의 쪼개지지 않음",
  "fissile": "핵분열성",
  "fissile: splits easily": "핵분열성: 쉽게 쪼개짐",
  "illustration": "예시 그림",
  "lost: water, steel, poisons, leakage": "손실: 물, 강철, 독물질, 누설",
  "neutrons out per neutron absorbed in the fuel": "연료에 흡수된 중성자 하나당 나오는 중성자",
  "neutrons per absorption": "흡수당 중성자",
  "next fission": "다음 핵분열",
  "next fission: keeps the chain going": "다음 핵분열: 연쇄를 이어 감",
  "slow step: Np{#}, half-life {#} d": "느린 단계: Np{#}, 반감기 {#}일",
  "slow step: Pa{#}, half-life {#} d": "느린 단계: Pa{#}, 반감기 {#}일",
  "the slow step is Np{#} (half-life {#} days)": "느린 단계는 Np{#} (반감기 {#}일)",
  "the slow step is Pa{#} (half-life {#} days)": "느린 단계는 Pa{#} (반감기 {#}일)",
  "split": "핵분열",
  "split (fission products)": "핵분열 (핵분열 생성물)",
  "{#} d": "{#}일",
  "{#} min": "{#}분",
  "{#} p": "{#} p",
  "{#} protons": "양성자 {#}개",
  "{#}: breeding line": "{#}: 증식선",
  "{a} % now {b}": "{a} %가 이제 {b}",
  "{a} per absorption": "흡수당 {a}",
  "η = {a}": "η = {a}",
  "η ≈ {a}": "η ≈ {a}",
});
