/* Korean: kcalc (Computing criticality) */
WT.L.ch.kcalc = {
  num: "강의 1", title: "임계도 계산", short: "k 계산",
  html: `
<div class="step">
  <h3>벤치마크</h3>
  <p>ICSBEP의 고속 금속 임계 집합체 네 개를 실제 축척으로 보여 줍니다. Godiva와 Jezebel은 반사체 없는 구이고, Flattop-25와 Flattop-Pu는 천연 우라늄 반사체를 둘렀습니다.</p>
</div>
<div class="step">
  <h3>계산된 <i>k</i><sub>eff</sub></h3>
  <p>OpenMC, 연속 에너지, 3차원 형상. 네 개 모두 벤치마크 ±1σ 안에 있습니다. <i>k</i><sub>eff</sub>는 피팅에 쓰이지 않습니다.</p>
</div>
<div class="step">
  <h3>민감도 프로파일</h3>
  <p>각 반응에 대한 <i>k</i><sub>eff</sub>의 수반 민감도, 레타지 단위당.</p>
  <div class="btns"><button class="btn ghost" data-act="se0" aria-pressed="true">Godiva</button><button class="btn ghost" data-act="se1" aria-pressed="false">Jezebel</button><button class="btn ghost" data-act="se2" aria-pressed="false">Flattop-Pu</button></div>
</div>
<div class="step">
  <h3>직접 섭동으로 검증</h3>
  <p>민감도로 예측한 <i>k</i><sub>eff</sub> 변화와 다시 계산한 변화의 비교, 섭동된 데이터 세트 63개.</p>
</div>
<div class="step">
  <h3>C5G7 원자로 노심</h3>
  <p>OECD/NEA C5G7, 2차원 1/4 노심, UO<sub>2</sub>와 MOX 연료봉 1,056개. <i>k</i><sub>eff</sub>는 기준값과 −19&nbsp;pcm 차이, 연료봉 출력 최대 오차 0.13&nbsp;%.</p>
</div>`,
};

Object.assign(WT.L.labels, {
  "{#} pcm  (±{#} benchmark)": "{#} pcm  (벤치마크 ±{#})",
  "+{#} pcm  (±{#} benchmark)": "+{#} pcm  (벤치마크 ±{#})",
  "Calculated − experimental k, with the benchmark ±{#}σ band": "계산 − 실험 k, 벤치마크 ±{#}σ 범위와 함께",
  "Drag to rotate": "드래그해 회전",
  "Godiva, integral sensitivity: ν {#}, fission {#} (% k per % change)": "Godiva, 적분 민감도: ν {#}, 핵분열 {#} (변화 1 %당 k의 %)",
  "Jezebel, integral sensitivity: ν {#}, fission {#} (% k per % change)": "Jezebel, 적분 민감도: ν {#}, 핵분열 {#} (변화 1 %당 k의 %)",
  "Flattop-Pu, integral sensitivity: ν {#}, fission {#} (% k per % change)": "Flattop-Pu, 적분 민감도: ν {#}, 핵분열 {#} (변화 1 %당 k의 %)",
  "Godiva: ν {#}, fission {#}": "Godiva: ν {#}, 핵분열 {#}",
  "Jezebel: ν {#}, fission {#}": "Jezebel: ν {#}, 핵분열 {#}",
  "Flattop-Pu: ν {#}, fission {#}": "Flattop-Pu: ν {#}, 핵분열 {#}",
  "UO₂: {#} × mean": "UO₂: {#} × 평균",
  "MOX {#} %: {#} × mean": "MOX {#} %: {#} × 평균",
  "OpenMC re-solve, Δk (pcm)": "OpenMC 재계산, Δk (pcm)",
  "Predicted from sensitivities, Δk (pcm)": "민감도로 예측, Δk (pcm)",
  "predicted Δk, pcm": "예측 Δk, pcm",
  "U{#} capture": "U{#} 포획",
  "Pu{#} capture": "Pu{#} 포획",
  "U{#} elastic": "U{#} 탄성",
  "Pu{#} elastic": "Pu{#} 탄성",
  "U{#} fission": "U{#} 핵분열",
  "Pu{#} fission": "Pu{#} 핵분열",
  "U{#} inelastic": "U{#} 비탄성",
  "Pu{#} inelastic": "Pu{#} 비탄성",
  "U{#} neutrons per fission (ν)": "U{#} 핵분열당 중성자 (ν)",
  "Pu{#} neutrons per fission (ν)": "Pu{#} 핵분열당 중성자 (ν)",
  "Relative pin power (hover a pin)": "연료봉 상대 출력 (연료봉에 마우스를 올리세요)",
  "Relative pin power (tap a pin)": "연료봉 상대 출력 (연료봉을 탭하세요)",
  "To scale.": "실제 축척.",
  "To scale. Drag to rotate.": "실제 축척. 드래그해 회전.",
  "core {#} cm, reflector {#} cm": "노심 {#} cm, 반사체 {#} cm",
  "radius {#} cm": "반지름 {#} cm",
  "{#} cm in {#} cm": "{#} cm / {#} cm",
  "k = {#}; reference {#} ({#} pcm)": "k = {#}; 기준값 {#} ({#} pcm)",
  "k {#}, reference {#}": "k {#}, 기준값 {#}",
  "plutonium in natural uranium": "천연 우라늄 속 플루토늄",
  "plutonium metal": "플루토늄 금속",
  "uranium{#} in natural uranium": "천연 우라늄 속 우라늄{#}",
  "uranium{#} metal": "우라늄{#} 금속",
  "water": "물",
  "×{#} of mean": "평균의 ×{#}",
  "U{#} ν": "U{#} ν",
  "Pu{#} ν": "Pu{#} ν",
  "Godiva   k = {#}": "Godiva   k = {#}",
  "Godiva {#}": "Godiva {#}",
  "Godiva: rms {#} pcm": "Godiva: rms {#} pcm",
  "Jezebel   k = {#}": "Jezebel   k = {#}",
  "Jezebel {#}": "Jezebel {#}",
  "Jezebel: rms {#} pcm": "Jezebel: rms {#} pcm",
  "Flattop-Pu   k = {#}": "Flattop-Pu   k = {#}",
  "Flattop-Pu {#}": "Flattop-Pu {#}",
  "Flattop-Pu: rms {#} pcm": "Flattop-Pu: rms {#} pcm",
  "Flattop{#}   k = {#}": "Flattop{#}   k = {#}",
  "Flattop{#} {#}": "Flattop{#} {#}",
  "{#} pcm (±{#})": "{#} pcm (±{#})",
  "+{#} pcm (±{#})": "+{#} pcm (±{#})",
  "{#} cm": "{#} cm",
  "{#} keV": "{#} keV",
  "{#} MeV": "{#} MeV",
  "OpenMC Δk": "OpenMC Δk"
});
