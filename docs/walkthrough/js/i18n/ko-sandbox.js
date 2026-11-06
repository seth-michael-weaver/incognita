/* Korean: sandbox (원자로 만들기) */
WT.L.ch.sandbox = {
  num: "강의 1", title: "원자로 만들기", short: "원자로 만들기", lead: "연료, 감속재, 냉각재, 크기를 골라 연쇄 반응이 스스로 이어질 수 있는지 확인합니다. 교과서식 단순화 모형입니다.",
  html: `
<div class="step">
  <h3>네 가지 인자</h3>
  <p>중성자가 새어 나가지 않는다면 흡수된 중성자 하나마다 <i>k</i><sub>∞</sub> = <i>η f p ε</i>개의 새 중성자가 생깁니다. 이 천연 우라늄 흑연 파일은 간신히 넘깁니다.</p>
</div>
<div class="step">
  <h3>감속재 고르기</h3>
  <p>천연 우라늄으로는 중수나 흑연만이 <i>k</i><sub>∞</sub>를 1보다 크게 만듭니다. 경수는 중성자를 잘 감속하지만 너무 많이 흡수합니다.</p>
  <div class="btns" role="group" aria-label="감속재"><button class="btn ghost" data-act="mo_h2o">경수</button> <button class="btn ghost" data-act="mo_d2o">중수</button> <button class="btn ghost" data-act="mo_c">흑연</button></div>
  <div class="ctl"><label for="sb-m1">연료당 감속재</label><input id="sb-m1" type="range" data-bind="lm" min="-0.5" max="2.3" step="0.01" value="0.3"><output class="sb-m"></output></div>
</div>
<div class="step">
  <h3>연료 농축하기</h3>
  <p>우라늄-235가 몇 퍼센트만 있으면 보통 물로도 됩니다. 오늘날 대부분의 원자로가 그렇게 하는 이유입니다.</p>
  <div class="btns" role="group" aria-label="연료"><button class="btn ghost" data-act="fu_nat">천연 U</button> <button class="btn ghost" data-act="fu_leu">농축 U</button> <button class="btn ghost" data-act="fu_mox">MOX(Pu)</button> <button class="btn ghost" data-act="fu_th">토륨 + U-233</button></div>
  <div class="ctl"><label for="sb-e1">핵분열성 비율(%)</label><input id="sb-e1" type="range" data-bind="enr" min="0.7" max="30" step="0.1" value="3"><output data-show="enr" data-fmt="1"></output></div>
</div>
<div class="step">
  <h3>크기와 누설</h3>
  <p>중성자는 표면으로 빠져나가므로 <i>k</i> = <i>k</i><sub>∞</sub> / (1 + <i>M</i>²<i>B</i>²)입니다. 이 천연 우라늄 흑연 파일의 가장자리를 점선 원까지 끌어 보세요.</p>
  <div class="ctl"><label for="sb-r1">노심 반지름(m)</label><input id="sb-r1" type="range" data-bind="R" min="0.2" max="6" step="0.05" value="2"><output data-show="R" data-fmt="2"></output></div>
</div>
<div class="step">
  <h3>냉각재가 끓으면</h3>
  <p>물로 냉각하는 흑연 노심에서는 끓으면 <i>k</i>가 올라갑니다. 물이 감속보다 흡수를 더 많이 했기 때문입니다. 체르노빌 RBMK의 결함입니다. 다른 냉각재도 시험해 보세요.</p>
  <div class="btns" role="group" aria-label="냉각재"><button class="btn ghost" data-act="co_h2o">물</button> <button class="btn ghost" data-act="co_gas">CO₂ / 헬륨</button> <button class="btn ghost" data-act="co_na">소듐</button></div>
</div>
<div class="step">
  <h3>직접 만들기</h3>
  <p>무엇이든 됩니다. 고속로에는 감속재가 없고 핵분열성 연료가 훨씬 많이 필요합니다.</p>
  <div class="btns" role="group" aria-label="연료"><button class="btn ghost" data-act="fu_nat">천연 U</button> <button class="btn ghost" data-act="fu_leu">농축 U</button> <button class="btn ghost" data-act="fu_mox">MOX(Pu)</button> <button class="btn ghost" data-act="fu_th">토륨 + U-233</button></div>
  <div class="ctl"><label for="sb-e2">핵분열성 비율(%)</label><input id="sb-e2" type="range" data-bind="enr" min="0.7" max="30" step="0.1" value="3"><output data-show="enr" data-fmt="1"></output></div>
  <div class="btns" role="group" aria-label="감속재"><button class="btn ghost" data-act="mo_none">감속재 없음</button> <button class="btn ghost" data-act="mo_h2o">경수</button> <button class="btn ghost" data-act="mo_d2o">중수</button> <button class="btn ghost" data-act="mo_c">흑연</button></div>
  <div class="ctl"><label for="sb-m2">연료당 감속재</label><input id="sb-m2" type="range" data-bind="lm" min="-0.5" max="2.3" step="0.01" value="0.3"><output class="sb-m"></output></div>
  <div class="btns" role="group" aria-label="냉각재"><button class="btn ghost" data-act="co_h2o">물</button> <button class="btn ghost" data-act="co_d2o">중수</button> <button class="btn ghost" data-act="co_gas">CO₂ / 헬륨</button> <button class="btn ghost" data-act="co_na">소듐</button> <button class="btn ghost" data-act="co_pb">납</button> <button class="btn ghost" data-act="co_salt">용융염</button></div>
  <div class="ctl"><label for="sb-r2">노심 반지름(m)</label><input id="sb-r2" type="range" data-bind="R" min="0.2" max="6" step="0.05" value="2"><output data-show="R" data-fmt="2"></output></div>
</div>`,
};
Object.assign(WT.L.labels, {
  "CO₂ / helium gas coolant": "CO₂ / 헬륨 기체 냉각재",
  "MOX {#} % Pu": "MOX {#} % Pu",
  "MOX, {#} % plutonium{#}": "MOX, {#} % 플루토늄{#}",
  "R {#} m": "R {#} m",
  "absorbed in fuel": "연료에 흡수",
  "can never sustain a chain, at any size": "어떤 크기에서도 연쇄를 유지할 수 없다",
  "caught by fuel": "연료에 포획",
  "coolant boils away: k ↑": "냉각재가 끓어 없어짐: k ↑",
  "coolant boils: k ↑": "냉각재 비등: k ↑",
  "coolant boils: k ≈": "냉각재 비등: k ≈",
  "coolant lost: k barely changes": "냉각재 상실: k 거의 불변",
  "coolant lost: k ↑": "냉각재 상실: k ↑",
  "critical size": "임계 크기",
  "escape capture": "포획 회피",
  "f": "f",
  "fast fission": "고속 핵분열",
  "fission": "핵분열",
  "fuel": "연료",
  "fuel heats up: k ↓ (Doppler)": "연료가 뜨거워짐: k ↓ (도플러)",
  "fuel hotter: k ↓": "연료 온도 상승: k ↓",
  "graphite moderator": "흑연 감속재",
  "graphite moderator · CO₂ / helium gas coolant": "흑연 감속재 · CO₂ / 헬륨 기체 냉각재",
  "graphite moderator · water coolant": "흑연 감속재 · 물 냉각재",
  "k": "k",
  "k∞": "k∞",
  "leak": "누설",
  "leak out": "누설",
  "light water moderator": "경수 감속재",
  "light water moderator · water coolant": "경수 감속재 · 물 냉각재",
  "mod./cool.": "감속/냉각",
  "moderator, coolant": "감속재, 냉각재",
  "natural U": "천연 U",
  "natural uranium ({#} % U{#})": "천연 우라늄 ({#} % U{#})",
  "never critical": "결코 임계 안 됨",
  "no chain, any size": "어떤 크기든 연쇄 없음",
  "no leakage": "누설 없음",
  "no moderator: a fast reactor · sodium coolant": "감속재 없음: 고속로 · 소듐 냉각재",
  "no moderator: fast": "감속재 없음: 고속로",
  "no size is big enough": "어떤 크기도 충분하지 않다",
  "p": "p",
  "per fuel absorption": "연료 흡수당",
  "radius {#} m": "반지름 {#} m",
  "radius {#} m · drag the edge": "반지름 {#} m · 가장자리를 끄세요",
  "simplified model": "단순화한 모형",
  "simplified one-group model · illustration": "단순화한 1군 모형 · 예시 그림",
  "stays in": "남음",
  "stays in (M² {#} cm²)": "남음 (M² {#} cm²)",
  "sustains a chain, {#} % to spare (ρ)": "연쇄 유지, 여유 {#} % (ρ)",
  "sustains: +{#} % spare": "유지: 여유 +{#} %",
  "too small: critical at radius {#} m": "너무 작다: 반지름 {#} m에서 임계",
  "too small: needs {#} m": "너무 작다: {#} m 필요",
  "uranium, {#} % U{#}": "우라늄, {#} % U{#}",
  "water boils: k ↑": "물 비등: k ↑",
  "water boils: k ↓": "물 비등: k ↓",
  "water coolant": "물 냉각재",
  "water heats or boils: k ↑": "물 가열·비등: k ↑",
  "water heats or boils: k ↓": "물 가열·비등: k ↓",
  "where the neutrons go": "중성자가 가는 곳",
  "{#} % U{#}": "{#} % U{#}",
  "enriched U": "농축 U",
  "light water": "경수",
  "heavy water": "중수",
  "lead": "납",
  "molten salt": "용융염",
  "sodium": "나트륨",
  "coolant": "냉각재",
  "= η f, if nothing leaked": "= η f, 누설이 없다면",
  "= η f p ε, if nothing leaked": "= η f p ε, 누설이 없다면",
  "stays in: {#} / ({#} + M²B²), M² = {#} cm²": "남음: {#} / ({#} + M²B²), M² = {#} cm²",
  "neutrons per absorption in fuel": "연료 흡수당 중성자 수",
  "share absorbed in fuel": "연료에 흡수되는 비율",
  "no slowing down, no resonance loss": "감속 없음, 공명 손실 없음",
  "escape capture while slowing": "감속 중 포획 회피",
  "fast fission counted in η": "고속 핵분열은 η에 포함",
  "bonus from fast fission": "고속 핵분열의 덤",
  "thorium, {#} % U{#}": "토륨, {#} % U{#}",
  "Th + {#} % U{#}": "Th + {#} % U{#}",
  "uranium, {#} % U{#} (highly enriched)": "우라늄, {#} % U{#} (고농축)",
  "critical at {#} m": "{#} m에서 임계",
  "coolant heats: k ↑": "냉각재 가열: k ↑",
  "coolant heats: k ↓": "냉각재 가열: k ↓",
  "coolant boils away: k ↓": "냉각재가 끓어 없어짐: k ↓",
  "coolant lost: k ↓": "냉각재 상실: k ↓",
  "heavy water coolant": "중수 냉각재",
  "sodium coolant": "소듐 냉각재",
  "lead coolant": "납 냉각재",
  "molten salt coolant": "용융염 냉각재",
  "heavy water moderator": "중수 감속재",
  "heavy water moderator · heavy water coolant": "중수 감속재 · 중수 냉각재",
  "heavy water moderator · water coolant": "중수 감속재 · 물 냉각재",
  "graphite moderator · sodium coolant": "흑연 감속재 · 소듐 냉각재",
  "no moderator: a fast reactor · lead coolant": "감속재 없음: 고속로 · 납 냉각재",
  "no moderator: a fast reactor · CO₂ / helium gas coolant": "감속재 없음: 고속로 · CO₂ / 헬륨 기체 냉각재",
  "no moderator: a fast reactor · molten salt coolant": "감속재 없음: 고속로 · 용융염 냉각재",
  "water moderates": "물이 감속",
  "heavy water moderates": "중수가 감속",
  "no moderator, but the water moderates": "감속재 없음, 하지만 물이 감속",
  "no moderator, but the heavy water moderates": "감속재 없음, 하지만 중수가 감속",
});
