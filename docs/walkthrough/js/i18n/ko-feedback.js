/* Korean: feedback (원자로의 안정성과 되먹임) */
WT.L.ch.feedback = {
  num: "강의 1", title: "원자로의 안정성과 되먹임", short: "되먹임",
  html: `
<div class="step">
  <h3>출력, 열, 반응도의 고리</h3>
  <p>출력이 커지면 연료와 물이 데워지고, 그 온도가 반응도 <i>ρ</i>를 바꾸며, 반응도가 다시 출력을 정합니다. 반응도를 계단처럼 더하고 신호가 고리를 도는 것을 지켜보세요. 계수가 음이면 되밀어냅니다.</p>
  <div class="ctl"><label for="fb-r">반응도 계단 (pcm)</label><input id="fb-r" type="range" data-bind="rs" data-instant min="50" max="300" step="10" value="200"><output data-show="rs" data-fmt="0"></output></div>
  <div class="btns"><button class="btn" data-act="fbIns">삽입</button> <button class="btn ghost" data-act="fbRes">초기화</button></div>
</div>
<div class="step">
  <h3>도플러: 빠른 브레이크</h3>
  <p>연료가 뜨거워지면 우라늄-238이 핵분열 없이 더 많은 중성자를 포획합니다(<a href="#doppler">도플러 넓어짐</a>). 연료는 몇 초 만에 데워지므로 이 브레이크가 가장 먼저 작동하며, 경수로에서는 언제나 음입니다. 여기서는 이것이 유일한 되먹임입니다.</p>
  <div class="ctl"><label for="fb-d">도플러 계수 (pcm/K)</label><input id="fb-d" type="range" data-bind="aD" data-instant min="-5" max="-1" step="0.1" value="-2.5"><output data-show="aD" data-fmt="1"></output></div>
  <div class="btns"><button class="btn" data-act="fbIns">삽입</button> <button class="btn ghost" data-act="fbRes">초기화</button></div>
</div>
<div class="step">
  <h3>감속재가 가세한다</h3>
  <p>따뜻한 물은 밀도가 낮아 중성자를 덜 잘 느리게 합니다. 보통의 붕소 농도에서 가압경수로는 이 때문에 감속재 계수도 음이 됩니다. 두 번째의 더 느린 브레이크가 생겨 출력이 더 낮은 곳에서 자리를 잡습니다.</p>
  <div class="ctl"><label for="fb-m">감속재 계수 (pcm/K)</label><input id="fb-m" type="range" data-bind="aM" data-instant min="-60" max="0" step="1" value="-30"><output data-show="aM" data-fmt="0"></output></div>
  <div class="btns"><button class="btn" data-act="fbIns">삽입</button> <button class="btn ghost" data-act="fbRes">초기화</button></div>
</div>
<div class="step">
  <h3>되먹임이 양일 때</h3>
  <p>냉각재 항이 양이고 도플러보다 크면, 출력이 커질수록 반응도도 커져 출력이 폭주합니다. 경수로는 음의 계수를 갖도록 설계됩니다. 저출력의 RBMK 같은 일부 설계는 양의 기포 계수를 가질 수 있었습니다.</p>
  <div class="ctl"><label for="fb-c">냉각재 계수 (pcm/K)</label><input id="fb-c" type="range" data-bind="aM" data-instant min="-60" max="150" step="5" value="150"><output data-show="aM" data-fmt="0"></output></div>
  <div class="btns"><button class="btn" data-act="fbIns">삽입</button> <button class="btn ghost" data-act="fbRes">초기화</button></div>
</div>`,
};

Object.assign(WT.L.labels, {
  "+{a} pcm": "+{a} pcm",
  "C dT/dt = P − h (T − Tc)": "C dT/dt = P − h (T − Tc)",
  "ρ = ρext + αD ΔTf + αM ΔTm": "ρ = ρext + αD ΔTf + αM ΔTm",
  "Doppler α_D = {a} pcm/K": "도플러 α_D = {a} pcm/K",
  "coolant α_C = {a} pcm/K": "냉각재 α_C = {a} pcm/K",
  "moderator α_M = {a} pcm/K": "감속재 α_M = {a} pcm/K",
  "inserted ρ_ext = {a}": "삽입한 ρ_ext = {a}",
  "P {#} %": "P {#} %",
  "chain": "연쇄",
  "chain reaction": "연쇄 반응",
  "heat": "열",
  "heats water": "물을 데움",
  "fuel +{#} K": "연료 +{#} K",
  "fuel {#} K": "연료 {#} K",
  "fuel ΔT +{#} K": "연료 ΔT +{#} K",
  "fuel ΔT {#} K": "연료 ΔT {#} K",
  "water +{#} K": "물 +{#} K",
  "water {#} K": "물 {#} K",
  "water ΔT +{#} K": "물 ΔT +{#} K",
  "water ΔT {#} K": "물 ΔT {#} K",
  "illustrative model": "설명용 모형",
  "last {#} s →": "최근 {#} s →",
  "last {#} seconds →": "최근 {#}초 →",
  "power": "출력",
  "power coefficient +{a} pcm per {#} % power: runs away": "출력 계수: 출력 {#} %당 +{a} pcm: 폭주",
  "power coefficient +{a} pcm per {#} %: runs away": "출력 계수 {#} %당 +{a} pcm: 폭주",
  "power coefficient {a} pcm per {#} % power: self-stabilising": "출력 계수: 출력 {#} %당 {a} pcm: 스스로 안정",
  "power coefficient {a} pcm per {#} %: settles": "출력 계수 {#} %당 {a} pcm: 안정됨",
  "power ran away · protection would shut it down": "출력 폭주 · 보호 계통이 정지시킬 것",
  "power ran away · in a real plant the protection system would shut it down": "출력 폭주 · 실제 발전소라면 보호 계통이 원자로를 정지시킬 것",
  "steady at {#} % · press Insert": "{#} %에서 일정 · 삽입을 누르세요",
  "steady at {#} % power · press Insert to add reactivity": "출력 {#} %에서 일정 · 삽입을 눌러 반응도를 더하세요",
  "αC +": "αC +",
  "αC {#}": "αC {#}",
  "αC −": "αC −",
  "αD −": "αD −",
  "αM +": "αM +",
  "αM {#}": "αM {#}",
  "αM −": "αM −",
  "ρ +{#} pcm": "ρ +{#} pcm",
  "ρ {#} pcm": "ρ {#} pcm",
});
