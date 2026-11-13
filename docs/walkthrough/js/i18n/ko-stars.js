/* Korean: stars (원소는 어디에서 왔을까) */
WT.L.ch.stars = {
  num: "강의 1", title: "원소는 어디에서 왔을까", short: "별",
  html: `
<div class="step">
  <h3>핵융합은 철에서 멈춘다</h3>
  <p>별은 가벼운 원자핵을 철까지 융합합니다. 그보다 무거운 것은 거의 모두 중성자를 더해 만들어집니다.</p>
</div>
<div class="step">
  <h3>느린 길</h3>
  <p>거성에서는 중성자가 드물게 오므로 불안정한 핵은 먼저 베타 붕괴합니다. 경로는 안정한 핵을 따라 지그재그로 나아갑니다.</p>
  <div class="ctl"><label for="st-k">중성자 포획 횟수</label><input id="st-k" type="range" data-bind="k" min="0" max="213" step="1" value="112"></div>
</div>
<div class="step">
  <h3>빠른 길</h3>
  <p>중성자별 병합에서는 원자핵이 붕괴하는 것보다 빠르게 중성자가 쏟아져 들어옵니다. 그 뒤 중성자가 많은 핵들이 다시 안정 쪽으로 붕괴합니다.</p>
  <div class="ctl"><label for="st-rt">되돌아 붕괴</label><input id="st-rt" type="range" data-bind="rt" min="0" max="1" step="0.01" value="0"></div>
</div>
<div class="step">
  <h3>마법수가 봉우리를 만든다</h3>
  <p>중성자가 50, 82, 126개인 핵은 거의 포획하지 않아 물질이 그곳에 쌓입니다. s-봉우리는 스트론튬, 바륨, 납에, r-봉우리는 조금 더 가벼운 쪽에 있습니다.</p>
  <div class="btns"><button class="btn ghost" data-act="stS" aria-pressed="true">s-과정 봉우리</button> <button class="btn ghost" data-act="stR" aria-pressed="true">r-과정 봉우리</button></div>
</div>
<div class="step">
  <h3>포획이 쉬운 곳은 드물다</h3>
  <p>s-과정만으로 만들어지는 동위원소에서는 존재비 Nₛ와 포획 단면적 σ의 곱이 마법수 사이에서 거의 일정합니다. 여기서 σ는 INCOGNITA가 30 keV에서 계산한 값입니다.</p>
  <div class="btns"><button class="btn ghost" data-act="stvs" aria-pressed="false">σ</button> <button class="btn ghost" data-act="stvn" aria-pressed="false">Nₛ</button> <button class="btn ghost" data-act="stvsn" aria-pressed="true">σ × Nₛ</button></div>
</div>
<div class="step">
  <h3>측정값과 대조</h3>
  <p>INCOGNITA의 30 keV 값을 측정값으로 나눈 것, 안정 핵종 94개(<a href="scoreboard.html">비교</a>).</p>
</div>`,
};
Object.assign(WT.L.labels, {
  "A ≈ {#}": "A ≈ {#}",
  "Ba": "Ba",
  "Ba{#}": "Ba{#}",
  "Big Bang": "빅뱅",
  "Fe": "Fe",
  "H": "H",
  "He": "He",
  "INCOGNITA ÷ measured, {#} keV": "INCOGNITA ÷ 측정값, {#} keV",
  "INCOGNITA's {#} keV capture rate (MACS) ÷ measured": "INCOGNITA의 {#} keV 포획률 (MACS) ÷ 측정값",
  "INCOGNITA: capture at {#} keV (MACS)": "INCOGNITA: {#} keV에서의 포획 (MACS)",
  "Lodders et al. {#}": "Lodders et al. {#}",
  "Lu{#}": "Lu{#}",
  "N = {#}": "N = {#}",
  "O": "O",
  "Pb": "Pb",
  "Pb{#}": "Pb{#}",
  "Sm{#}": "Sm{#}",
  "Sn": "Sn",
  "Sr": "Sr",
  "Sr{#}": "Sr{#}",
  "abundances: Lodders, Palme & Gail {#}": "존재비: Lodders, Palme & Gail {#}",
  "abundances: Lodders, Palme & Gail {#} · point at the curve": "존재비: Lodders, Palme & Gail {#} · 곡선을 가리켜 보세요",
  "atoms per million silicon atoms (Solar System)": "규소 원자 100만 개당 원자 수 (태양계)",
  "atoms per {#}⁶ silicon": "규소 {#}⁶개당 원자 수",
  "beta decay (n → p)": "베타 붕괴 (n → p)",
  "flat between magic numbers, steps down at each": "마법수 사이는 평평, 마법수마다 한 계단 내려감",
  "fusion": "핵융합",
  "fusion in stars": "별 속 핵융합",
  "made by neutron capture": "중성자 포획으로 생성",
  "magic N: captures poorly, matter piles up": "마법수 N: 포획이 어려워 물질이 쌓임",
  "magic neutron number: it captures poorly, so matter piles up here": "중성자 마법수: 포획이 어려워 물질이 여기에 쌓인다",
  "mass number A": "질량수 A",
  "mass number A (protons + neutrons)": "질량수 A (양성자 + 중성자)",
  "mb": "mb",
  "nearly flat between magic numbers, a step down at each": "마법수 사이는 거의 평평, 마법수마다 한 계단 아래로",
  "neutron capture": "중성자 포획",
  "neutrons N →": "중성자 수 N →",
  "peaks: sources Lodders et al. {#}": "봉우리: 출처 Lodders et al. {#}",
  "plus a weaker s-process (massive stars)": "그리고 더 약한 s-과정 (무거운 별)",
  "r {#}": "r {#}",
  "r-path: illustration": "r-경로: 예시 그림",
  "r-peak Pt": "r-봉우리 Pt",
  "r-peak Se, Kr": "r-봉우리 Se, Kr",
  "r-peak Te, Xe": "r-봉우리 Te, Xe",
  "r-process: a flood of neutrons makes very neutron-rich nuclei": "r-과정: 쏟아지는 중성자가 중성자가 매우 많은 핵을 만든다",
  "r-process: very neutron-rich nuclei": "r-과정: 중성자가 매우 많은 핵",
  "ringed: s-only isotopes · measured: compiled values (KADoNiS) · a development comparison, not an independent test": "고리 표시: s-과정 전용 동위원소 · 측정값: 편집 값 (KADoNiS) · 개발 중 비교이며 독립적인 검증이 아님",
  "ringed: s-only · measured: KADoNiS": "고리 표시: s 전용 · 측정값: KADoNiS",
  "s Ba": "s Ba",
  "s Pb": "s Pb",
  "s Sr": "s Sr",
  "s-only isotopes · bars: INCOGNITA {#} %": "s-과정 전용 동위원소 · 막대: INCOGNITA {#} %",
  "s-only isotopes · σ: INCOGNITA (bars: its {#} % range; open circle: scaled to a measurement) · Nₛ: Lodders et al. {#}": "s-과정 전용 동위원소 · σ: INCOGNITA (막대: {#} % 범위, 빈 원: 측정값에 맞춰 보정) · Nₛ: Lodders et al. {#}",
  "s-peak Ba": "s-봉우리 Ba",
  "s-peak Pb": "s-봉우리 Pb",
  "s-peak Sr": "s-봉우리 Sr",
  "seen in {#}: merger GW{#}": "{#}년 관측: 병합 GW{#}",
  "seen in {#}: the neutron-star merger GW{#} and its kilonova": "{#}년 관측: 중성자별 병합 GW{#}과 그 킬로노바",
  "wait": "대기",
  "waiting point": "대기점",
  "weak s-process too": "약한 s-과정도",
  "σ × Nₛ (mb × atoms per million Si)": "σ × Nₛ (mb × Si 100만 개당 원자 수)",
  "σ × Nₛ (mb × atoms per {#}⁶ Si)": "σ × Nₛ (mb × Si {#}⁶개당 원자 수)",
  "↑ protons Z": "↑ 양성자 수 Z",
  "A = {a}: mostly {b}, {c} atoms per million silicon": "A = {a}: 주로 {b}, 규소 100만 개당 {c}개",
  "decayed back: r-made stable isotopes": "되돌아 붕괴: r-과정이 만든 안정 동위원소",
  "decayed back: each lands on the most neutron-rich stable isobar": "되돌아 붕괴: 각각 중성자가 가장 많은 안정 동중핵에 도달",
  "beta decays, A fixed": "베타 붕괴, A 고정",
  "beta decays carry them back, mass number A fixed": "베타 붕괴가 되돌려 놓는다, 질량수 A는 그대로",
  "{a} · N = {b} · σ = {c} mb": "{a} · N = {b} · σ = {c} mb",
  "{a} · N = {b} · INCOGNITA: σ = {c} mb at {#} keV": "{a} · N = {b} · INCOGNITA: σ = {c} mb ({#} keV)",
  "{a} · unstable: beta decay": "{a} · 불안정: 베타 붕괴",
  "{a} · unstable: it beta-decays before the next neutron": "{a} · 불안정: 다음 중성자가 오기 전에 베타 붕괴",
  "end: the lead–bismuth cycle": "끝: 납–비스무트 순환",
  "end of the road: Bi{#} → Po{#} → alpha decay back to Pb{#}": "길의 끝: Bi{#} → Po{#} → 알파 붕괴로 Pb{#}로 돌아감",
  "drag along the path": "경로를 따라 끄세요",
  "drag along the path, or use the slider": "경로를 따라 끌거나 슬라이더를 쓰세요",
  "{a}: INCOGNITA σ = {b} mb": "{a}: INCOGNITA σ = {b} mb",
  "{a}: σ = {b} mb × Nₛ = {c} → σNₛ = {d}": "{a}: σ = {b} mb × Nₛ = {c} → σNₛ = {d}",
  " (σ scaled to a measured value)": " (σ는 측정값에 맞춰 보정)",
  "σ alone: scattered": "σ만: 흩어짐",
  "σ alone jumps around from isotope to isotope": "σ만 보면 동위원소마다 크게 들쭉날쭉하다",
  "Nₛ alone: scattered": "Nₛ만: 흩어짐",
  "Nₛ alone jumps around the other way": "Nₛ만 보면 반대 방향으로 들쭉날쭉하다",
  "{a}: INCOGNITA's engine {b} (the library then scales to it)": "{a}: INCOGNITA 엔진 {b} (라이브러리는 이후 측정값에 맞춤)",
  "{a}: INCOGNITA σ = {b} mb, {c}": "{a}: INCOGNITA σ = {b} mb, {c}",
  "{a} nuclides · typical difference {b} %": "핵종 {a}개 · 전형적 차이 {b} %",
  "{a} stable nuclides · typical difference {b} % (median), rms {c} %": "안정 핵종 {a}개 · 전형적 차이 {b} % (중앙값), rms {c} %",
  "{a} % above measured": "측정값보다 {a} % 높음",
  "{a} % below measured": "측정값보다 {a} % 낮음",
});
