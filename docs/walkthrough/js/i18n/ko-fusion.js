/* Korean: fusion (29장, 핵융합 에너지와 쿨롱 장벽) */
WT.L.ch.fusion = {
  num: "29장", title: "핵융합 에너지와 쿨롱 장벽", short: "핵융합",
  lead: "핵융합은 핵분열과 반대 방향으로 진행됩니다. 가벼운 원자핵 둘이 합쳐지고, 합쳐진 쌍은 부분들을 더한 것보다 가볍습니다.",
  html: `
<div class="step">
  <h3>결합 곡선에서 얻는 핵융합 에너지</h3>
  <p>가벼운 원자핵 둘을 합쳐 보세요. 새 원자핵이 결합 곡선에서 더 높은 곳에 있으면 에너지가 나옵니다. 철 봉우리를 지나면 합치는 데 오히려 에너지가 듭니다.</p>
  <div class="ctl"><label for="fu-a">가벼운 원자핵 하나의 A</label><input id="fu-a" type="range" data-bind="fuse" data-instant min="2" max="60" step="1" value="2"><output data-show="fuse" data-fmt="0"></output></div>
  <p class="ctl-result" id="fu-fuse-out" aria-live="polite"></p>
</div>
<div class="step">
  <h3>쿨롱 장벽과 터널링</h3>
  <p>중양성자를 뒤로 당겼다가 놓으세요. 두 원자핵 모두 전하를 띠므로 대부분은 언덕에 튕겨 나오고, 몇몇만 터널링으로 빠져나갑니다.</p>
  <div class="ctl"><label for="fu-e">미는 힘 (keV)</label><input id="fu-e" type="range" data-bind="lE" min="0.5" max="2.6" step="0.01" value="1.7"><output data-show="E" data-fmt="0"></output></div>
  <div class="btns"><button class="btn" data-act="fire">발사</button></div>
</div>
<div class="step">
  <h3>반응 생성물과 Q 값</h3>
  <p>합쳐진 쌍은 두 부분보다 가볍습니다. 사라진 질량은 빠른 입자가 되어 날아갑니다.</p>
  <div class="btns fu-fuels"><button class="btn ghost" data-act="DT" aria-pressed="true">D–T</button> <button class="btn ghost" data-act="DD" aria-pressed="false">D–D</button> <button class="btn ghost" data-act="DHe" aria-pressed="false">D–³He</button> <button class="btn ghost" data-act="pB" aria-pressed="false">p–¹¹B</button></div>
</div>
<div class="step">
  <h3>열핵 반응률</h3>
  <p>뜨거운 기체에서는 가장 빠른 원자핵들이 빠져나갑니다. 번쩍임 하나가 핵융합 한 번입니다.</p>
  <div class="ctl"><label for="fu-t">온도 (keV)</label><input id="fu-t" type="range" data-bind="lT" min="0" max="2" step="0.01" value="1"><output data-show="T" data-fmt="1"></output></div>
</div>`,
};

// canvas labels of the fusion part (chapters 29-32)
Object.assign(WT.L.labels, {
  "B": "B",
  "Copper{#}": "구리{#}",
  "Coulomb hill": "쿨롱 언덕",
  "D–D": "D–D",
  "D–T": "D–T",
  "D–³He": "D–³He",
  "E = kT": "E = kT",
  "Gamow peak E₀": "가모프 봉우리 E₀",
  "K {#} · field lines lost to the wall: {#}": "K {#} · 벽으로 잃은 자기력선: {#}",
  "Q = {#}": "Q = {#}",
  "Q = ∞: no heating needed": "Q = ∞: 가열 필요 없음",
  "Silicon{#} (SiC)": "규소{#} (SiC)",
  "Steel (iron{#})": "강철 (철{#})",
  "Sun's core": "태양 중심핵",
  "TBR {#}": "TBR {#}",
  "Tungsten{#}": "텅스텐{#}",
  "Vanadium{#}": "바나듐{#}",
  "after {#} years at {#} MW/m² · {#} MeV neutrons only · σ from INCOGNITA library v{#}": "{#}년 후, {#} MW/m² · {#} MeV 중성자만 · σ: INCOGNITA 라이브러리 v{#}",
  "almost never": "거의 없음",
  "alpha {#} MeV": "알파 {#} MeV",
  "axis, q = {#}": "축, q = {#}",
  "binding per nucleon (MeV)": "핵자당 결합 (MeV)",
  "bubble-chamber view, magnetic field into the page: charged products curl, the neutron leaves no track": "거품 상자 보기, 자기장은 화면 안쪽: 하전 생성물은 휘고, 중성자는 궤적이 없음",
  "burning on its own": "스스로 타는 중",
  "cooled down: plasma lost": "식음: 플라스마 잃음",
  "cooling": "식는 중",
  "could not load the library file": "라이브러리 파일을 불러오지 못함",
  "deuteron": "중양성자",
  "deuteron {#} keV": "중양성자 {#} keV",
  "deuteron: pull back, let go": "중양성자: 당겼다가 놓기",
  "drag or tap a point; it runs on its own": "점을 끌거나 탭하세요. 저절로 진행됩니다",
  "easiest: {a} keV, nτT {b}": "가장 쉬움: {a} keV, nτT {b}",
  "edge: q = {#} · lines that cross it are lost": "가장자리: q = {#} · 넘는 선은 잃음",
  "electron {#} keV": "전자 {#} keV",
  "energy of the colliding pair (keV)": "충돌하는 쌍의 에너지 (keV)",
  "few are this fast": "이만큼 빠른 것은 드묾",
  "fusion rate: {a} the rate at {b} keV": "핵융합률: {b} keV일 때의 {a}",
  "grain boundary": "결정립계",
  "heating itself": "스스로 가열 중",
  "helium stays and gathers into bubbles; hydrogen mostly diffuses out": "헬륨은 남아 거품으로 모이고, 수소는 대부분 확산되어 빠져나감",
  "helium {#} appm": "헬륨 {#} appm",
  "hill to climb: charge product Z₁Z₂ = {#}": "올라야 할 언덕: 전하 곱 Z₁Z₂ = {#}",
  "hold: heaters on (Q = fusion power / heating) · let go: heaters off, the plasma is on its own": "누르는 동안: 가열 켬 (Q = 핵융합 출력 / 가열) · 놓으면: 가열 끔, 플라스마 혼자",
  "hydrogen {#} appm": "수소 {#} appm",
  "ignition (Q = ∞)": "점화 (Q = ∞)",
  "kT (keV)": "kT (keV)",
  "kT {#} keV · E₀ {#} keV · width {#} keV": "kT {#} keV · E₀ {#} keV · 폭 {#} keV",
  "kT {a} keV · D–T {b} m³/s · {c}× D–D": "kT {a} keV · D–T {b} m³/s · D–D의 {c}배",
  "keeps itself hot": "스스로 뜨거움 유지",
  "laps {#}": "바퀴 수 {#}",
  "lead–lithium": "납–리튬",
  "liquid lithium": "액체 리튬",
  "loading INCOGNITA's cross sections…": "INCOGNITA 단면적 불러오는 중…",
  "missing {#} u  =  {#} MeV out": "사라진 {#} u  =  {#} MeV 방출",
  "n τE (s/m³)": "n τE (s/m³)",
  "negative: turns the other way": "음수: 반대로 돎",
  "neutron escapes": "중성자 탈출",
  "peak near {#} keV": "{#} keV 부근 봉우리",
  "per fusion neutron · {#} neutrons · cross sections are simple fits": "핵융합 중성자당 · 중성자 {#}개 · 단면적은 단순 맞춤",
  "plasma": "플라스마",
  "product ×{a}": "곱 ×{a}",
  "push {a} keV · chance to tunnel head-on {b}": "미는 힘 {a} keV · 정면 터널링 확률 {b}",
  "q = {#}": "q = {#}",
  "q = {#}/{#}: closes after {#} lap": "q = {#}/{#}: {#}바퀴 후 닫힘",
  "q = {#}/{#}: closes after {#} laps": "q = {#}/{#}: {#}바퀴 후 닫힘",
  "q = {#}: no simple fraction, the dots fill the circle": "q = {#}: 간단한 분수 아님, 점이 원을 채움",
  "screen radius is logarithmic: {#} fm to {#} fm": "화면 반지름은 로그 눈금: {#} fm ~ {#} fm",
  "shield": "차폐체",
  "tap to fire": "탭하여 발사",
  "the cut, flat": "단면, 펼친 모습",
  "time slowed {a}×": "시간 {a}배 느리게",
  "tries {#} · fused {#}": "시도 {#} · 융합 {#}",
  "tritium made, by depth": "깊이별 생성 삼중수소",
  "triton": "삼중양성자",
  "tunnels more easily": "터널링이 더 쉬움",
  "turns at {#} fm": "{#} fm에서 되돌아감",
  "wall": "벽",
  "{#} MeV": "{#} MeV",
  "{#} cm": "{#} cm",
  "{#} in {a}": "{a}번에 {#}번",
  "{#} keV": "{#} keV",
  "{#} keV = {#} million K": "{#} keV = {#}백만 K",
  "{a} %": "{a}%",
  "{a} + {a} → {b}: about {c} MeV released": "{a} + {a} → {b}: 약 {c} MeV 방출",
  "{a} + {a} → {b}: costs {c} MeV": "{a} + {a} → {b}: {c} MeV 소모",
  "{a} keV · chance {b}": "{a} keV · 확률 {b}",
  "{a} keV · nτ {b} · {c}": "{a} keV · nτ {b} · {c}",
  "{a} · two branches, equally likely": "{a} · 두 갈래, 같은 확률",
  "{a} · ρ up to {b} · {c} turns a second": "{a} · ρ 최대 {b} · 초당 {c}바퀴",
  "σ at {#} MeV:  (n,α) {#} mb · (n,p) {#} mb · (n,{#}n) {#} mb": "{#} MeV에서 σ:  (n,α) {#} mb · (n,p) {#} mb · (n,{#}n) {#} mb",
  "⁶Li {#} · ⁷Li {#} · (n,{#}n) {#}": "⁶Li {#} · ⁷Li {#} · (n,{#}n) {#}",
  "⁶Li {#} · ⁷Li {#} · (n,{#}n) {#} · captured {#} · leaked {#}": "⁶Li {#} · ⁷Li {#} · (n,{#}n) {#} · 포획 {#} · 누설 {#}",
  "⟨σv⟩ (m³/s)": "⟨σv⟩ (m³/s)",
});
