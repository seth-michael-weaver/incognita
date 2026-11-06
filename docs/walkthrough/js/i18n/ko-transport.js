/* Korean: transport (중성자 수송과 몬테카를로) */
WT.L.ch.transport = {
  num: "강의 1", title: "중성자 수송과 몬테카를로", short: "몬테카를로",
  html: `
<div class="step">
  <h3>수송 방정식</h3>
  <p>정확히 말하면 중성자는 각선속 <i>ψ</i>(<b>r</b>, <b>Ω</b>, <i>E</i>)에 대한 볼츠만 방정식을 따릅니다. <b>Ω</b>·∇<i>ψ</i> + Σ<sub>t</sub><i>ψ</i> = ∫∫Σ<sub>s</sub><i>ψ</i>′ d<b>Ω</b>′d<i>E</i>′ + (<i>χ</i>/4π<i>k</i>)∫<i>ν</i>Σ<sub>f</sub><i>φ</i>′ d<i>E</i>′. 몬테카를로는 중성자를 하나씩 놀려서 이 방정식을 풉니다. <i>s</i> = −ln <i>ξ</i> / Σ<sub>t</sub>만큼 날아간 뒤 산란하거나, 포획되거나, 핵분열을 일으킵니다.</p>
  <div class="btns"><button class="btn" data-act="trnew">새 중성자</button></div>
</div>
<div class="step">
  <h3>확산 이론이 틀리는 곳</h3>
  <p>확산 이론은 모든 방향의 선속이 거의 같다고 가정합니다. 이 가정은 표면에서 자유 행로 한두 개 안쪽과 강한 흡수체 속에서 깨집니다. 균일한 선원이 있는 평판에서 흡수를 키우며 몬테카를로 선속과 비교해 보세요.</p>
  <div class="ctl"><label for="tr-pa">흡수 Σ<sub>a</sub>/Σ<sub>t</sub></label><input id="tr-pa" type="range" data-bind="pa" data-instant min="0.05" max="0.8" step="0.05" value="0.5"><output data-show="pa" data-fmt="2"></output></div>
</div>
<div class="step">
  <h3>거듭제곱 반복</h3>
  <p><i>k</i><sub>eff</sub>를 구할 때는 각 세대의 핵분열 위치가 다음 세대의 선원이 되며, <i>k</i>는 출발한 중성자 하나당 저장된 위치의 수입니다. 모든 중성자를 한쪽 가장자리에 둔 나쁜 추측에서 출발해, 선원이 기본 모드로 퍼져 가는 것을 지켜보세요.</p>
  <div class="btns"><button class="btn" data-act="trbad">나쁜 추측에서 다시 시작</button></div>
</div>
<div class="step">
  <h3>선원은 수렴했는가?</h3>
  <p>구간으로 나눈 선원의 섀넌 엔트로피 <i>H</i> = −Σ <i>p</i><sub>b</sub> log<sub>2</sub> <i>p</i><sub>b</sub>는 선원이 자리를 잡으면 평평해집니다. 그때부터만 세대들을 평균합니다. <i>k</i>의 오차 막대는 센 이력 수에 따라 1/√<i>N</i>로 줄어듭니다.</p>
  <div class="ctl"><label for="tr-n">세대당 이력 수</label><input id="tr-n" type="range" data-bind="nh" data-instant min="100" max="2000" step="100" value="400"><output data-show="nh" data-fmt="0"></output></div>
</div>`,
};

Object.assign(WT.L.labels, {
  "Monte Carlo": "몬테카를로",
  "amber glow: where collisions pile up": "호박색 빛: 충돌이 몰리는 곳",
  "capture": "포획",
  "chance to fly at least s:  e^(−Σₜ s)": "적어도 s만큼 날아갈 확률:  e^(−Σₜ s)",
  "diffusion": "확산",
  "diffusion vs Monte Carlo: +{#} % at the surface, +{#} % in the middle": "확산 대 몬테카를로: 표면 +{#} %, 가운데 +{#} %",
  "diffusion vs Monte Carlo: +{#} % at the surface, {#} % in the middle": "확산 대 몬테카를로: 표면 +{#} %, 가운데 {#} %",
  "diffusion vs Monte Carlo: {#} % at the surface, +{#} % in the middle": "확산 대 몬테카를로: 표면 {#} %, 가운데 +{#} %",
  "diffusion vs Monte Carlo: {#} % at the surface, {#} % in the middle": "확산 대 몬테카를로: 표면 {#} %, 가운데 {#} %",
  "fission": "핵분열",
  "fission source · dashed: fundamental mode": "핵분열 선원 · 점선: 기본 모드",
  "flux": "선속",
  "generation {#}": "{#}세대",
  "generation {#}: k = {#} · H = {#} bits": "{#}세대: k = {#} · H = {#} 비트",
  "glow: collision density": "빛: 충돌 밀도",
  "illustrative one-group data": "설명용 1군 데이터",
  "inactive  |  active generations": "비활성  |  활성 세대",
  "inactive | active": "비활성 | 활성",
  "infinite medium S/Σₐ": "무한 매질 S/Σₐ",
  "k per generation": "세대별 k",
  "k_eff = {#} ± {#} ({#} × {#} histories) · diffusion {#}": "k_eff = {#} ± {#} ({#} × {#} 이력) · 확산 {#}",
  "leak": "누설",
  "scatter": "산란",
  "source entropy H (bits)": "선원 엔트로피 H (비트)",
  "source · dashed: fundamental mode": "선원 · 점선: 기본 모드",
  "starting…": "시작 중…",
  "tap the slab to drop the whole source there": "평판을 눌러 선원 전체를 그곳에 놓기",
  "tap the slab to start neutrons": "평판을 눌러 중성자 출발",
  "tap: drop the source there": "누르기: 선원을 그곳에",
  "vacuum": "진공",
  "{#} free paths": "자유 행로 {#}개",
  "{#} generations, averaging starts after {#}": "{#}세대, 평균은 {#}세대 이후부터",
  "ξ = {#}  →  s = −ln ξ / Σₜ = {#} free paths": "ξ = {#}  →  s = −ln ξ / Σₜ = 자유 행로 {#}개",
});
