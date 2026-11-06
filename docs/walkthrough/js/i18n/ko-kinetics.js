/* Korean: kinetics (원자로 동특성: 6군과 인아워 방정식) */
WT.L.ch.kinetics = {
  num: "강의 1", title: "원자로 동특성: 6군과 인아워 방정식", short: "동특성",
  html: `
<div class="step">
  <h3>늦게 오는 중성자의 여섯 군</h3>
  <p>지연 중성자는 반감기가 0.23 s에서 56 s에 이르는 약 여섯 군의 핵분열 생성물에서 나옵니다(Keepin, U-235). 대부분은 2초 군과 22초 군이 내놓지만, 기다리는 재고의 대부분은 수명이 긴 군이 쥐고 있습니다. 평균 지연은 Σ <i>a</i><sub>i</sub>/<i>λ</i><sub>i</sub> ≈ 13 s입니다. 핵분열을 멈추고 각 군이 저마다의 속도로 줄어드는 것을 지켜보세요.</p>
  <div class="btns"><button class="btn" data-act="kistop" aria-pressed="false">핵분열 멈추기</button></div>
</div>
<div class="step">
  <h3>인아워 방정식</h3>
  <p>6군 점 동특성 방정식에 <i>n</i> ∝ e<sup><i>ωt</i></sup>를 넣으면 <i>ρ</i> = <i>ω</i>Λ + Σ <i>β</i><sub>i</sub><i>ω</i>/(<i>ω</i> + <i>λ</i><sub>i</sub>)를 얻습니다. −<i>λ</i><sub>i</sub>의 극으로 나뉜 일곱 가지가 있습니다. <i>ρ</i>의 계단은 각 가지와 한 번씩 만나며, 가장 오른쪽 근이 안정 주기 <i>T</i> = 1/<i>ω</i><sub>1</sub>이고 나머지 여섯은 사라집니다.</p>
  <div class="ctl"><label for="ki-r1">반응도 ρ ($)</label><input id="ki-r1" type="range" data-bind="rd" data-instant min="-2" max="1.3" step="0.01" value="0.3"><output data-show="rd" data-fmt="2"></output></div>
</div>
<div class="step">
  <h3>즉발 도약과 즉발 임계</h3>
  <p>반응도 계단은 먼저 몇 밀리초 안에 출력을 <i>P</i><sub>1</sub>/<i>P</i><sub>0</sub> ≈ <i>β</i>/(<i>β</i> − <i>ρ</i>)만큼 끌어올리고, 그다음 안정 주기로 증가시킵니다. <i>ρ</i> = 1 $에서는 즉발 중성자만으로 임계가 되어 주기가 Λ/(<i>ρ</i> − <i>β</i>) 쪽으로 무너집니다.</p>
  <div class="ctl"><label for="ki-r2">반응도 ρ ($)</label><input id="ki-r2" type="range" data-bind="rj" data-instant min="0.05" max="1.3" step="0.01" value="0.5"><output data-show="rj" data-fmt="2"></output></div>
</div>
<div class="step">
  <h3>스크램 이후</h3>
  <p>큰 음의 반응도를 넣으면 출력은 즉시 약 <i>β</i>/(<i>β</i> − <i>ρ</i>)로 떨어지고, 그 뒤로는 수명이 가장 긴 군이 붕괴하는 속도보다 빨리 줄어들 수 없습니다. 스크램이 아무리 깊어도 주기는 −1/<i>λ</i><sub>1</sub> ≈ −80 s에 다가갑니다.</p>
  <div class="ctl"><label for="ki-r3">반응도 ρ ($)</label><input id="ki-r3" type="range" data-bind="rs" data-instant min="-30" max="-0.5" step="0.5" value="-10"><output data-show="rs" data-fmt="1"></output></div>
</div>`,
};

Object.assign(WT.L.labels, {
  "Keepin six-group data": "Keepin 6군 데이터",
  "Stop fissions": "핵분열 멈추기",
  "Restart fissions": "핵분열 재개",
  "delayed neutrons out": "나오는 지연 중성자",
  "drag the rods in": "제어봉을 끌어 넣기",
  "drag the rods out": "제어봉을 끌어 빼기",
  "drag ρ": "ρ 끌기",
  "half-life · share emitted": "반감기 · 방출 몫",
  "mean delay Σ aᵢ/λᵢ = {#} s · β = {#} (U{#})": "평균 지연 Σ aᵢ/λᵢ = {#} s · β = {#} (U{#})",
  "power": "출력",
  "power ×{#} speed": "출력 ×{#} 배속",
  "prompt critical": "즉발 임계",
  "prompt critical · period {#} ms (Λ = {#} µs)": "즉발 임계 · 주기 {#} ms (Λ = {#} µs)",
  "prompt critical · period {#} s (Λ = {#} µs)": "즉발 임계 · 주기 {#} s (Λ = {#} µs)",
  "prompt critical · period {#} min (Λ = {#} µs)": "즉발 임계 · 주기 {#}분 (Λ = {#} µs)",
  "prompt critical · period {#} h (Λ = {#} µs)": "즉발 임계 · 주기 {#}시간 (Λ = {#} µs)",
  "prompt drop to {#}": "{#}로 즉발 강하",
  "prompt jump β/(β−ρ) = {#}": "즉발 도약 β/(β−ρ) = {#}",
  "prompt root": "즉발 근",
  "prompt root ≈ −(β−ρ)/Λ": "즉발 근 ≈ −(β−ρ)/Λ",
  "slope e^(−t / {#} s): the {#} s group": "기울기 e^(−t / {#} s): {#} s 군",
  "slope e^(−t/{#} s)": "기울기 e^(−t/{#} s)",
  "stable period T = {#}/ω₁ = {#} ms": "안정 주기 T = {#}/ω₁ = {#} ms",
  "stable period T = {#}/ω₁ = {#} s": "안정 주기 T = {#}/ω₁ = {#} s",
  "stable period T = {#}/ω₁ = {#} min": "안정 주기 T = {#}/ω₁ = {#}분",
  "stable period T = {#}/ω₁ = {#} h": "안정 주기 T = {#}/ω₁ = {#}시간",
  "ρ = {#}: power stays flat": "ρ = {#}: 출력이 일정함",
  "waiting stock": "기다리는 재고",
  "{#} s": "{#} s",
  "{#} ms": "{#} ms",
  "{#} min": "{#}분",
  "{#} h": "{#}시간",
  "{#} s after stopping · delayed emission {#} % of the start": "멈춘 뒤 {#} s · 지연 방출은 처음의 {#} %",
  "ρ = {#} $ · stable period {#} min": "ρ = {#} $ · 안정 주기 {#}분",
  "ρ = {#} $ · stable period {#} ms": "ρ = {#} $ · 안정 주기 {#} ms",
  "ρ = {#} $ · stable period {#} s": "ρ = {#} $ · 안정 주기 {#} s",
  "ρ = {#} $ · stable period {#} h": "ρ = {#} $ · 안정 주기 {#}시간",
  "ρ = {#} $ · stable period {#} s (limit {#} s)": "ρ = {#} $ · 안정 주기 {#} s (한계 {#} s)",
  "ρ = {#} $ · stable period {#} min (limit {#} s)": "ρ = {#} $ · 안정 주기 {#}분 (한계 {#} s)",
  "ρ = {#} $ · stable period {#} ms (limit {#} s)": "ρ = {#} $ · 안정 주기 {#} ms (한계 {#} s)",
  "ω ({#}/s), axis stretched (asinh)": "ω ({#}/s), 축 늘임 (asinh)",
  "ω ({#}/s), stretched": "ω ({#}/s), 늘임",
});
