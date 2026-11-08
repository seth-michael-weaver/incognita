/* Korean: spectrum (고속로와 열중성자로) */
WT.L.ch.spectrum = {
  num: "강의 1", title: "고속로와 열중성자로", short: "고속 대 열",
  html: `
<div class="step">
  <h3>중성자는 얼마나 빠른가</h3>
  <p>중성자는 2 MeV 근처의 빠른 상태로 태어납니다. 경수로에서는 수소와 부딪히며 튀다가 결국 물 원자들 자체만큼 느려지는데, 이것이 <b>열중성자</b>입니다. 고속로에는 감속재가 없어 중성자가 빠른 채로 남습니다. 둘 사이를 오가 보세요.</p>
  <div class="ctl"><label for="spc-m1">감속 정도</label><input id="spc-m1" type="range" data-bind="mod" data-instant min="0" max="1" step="0.01" value="1"><output data-show="mod" data-fmt="2"></output></div>
</div>
<div class="step">
  <h3>여분의 중성자</h3>
  <p><i>η</i>는 연료 원자핵이 중성자 하나를 흡수할 때 되돌려주는 중성자의 수입니다. 하나는 연쇄를 이어 가는 데 쓰이고, 새 연료를 증식하려면 하나가 더 남아야 하므로 <i>η</i>가 2보다 꽤 커야 합니다. 플루토늄-239는 빠른 중성자에서만 그렇게 됩니다.</p>
  <div class="ctl"><label for="spc-m2">감속 정도</label><input id="spc-m2" type="range" data-bind="mod" data-instant min="0" max="1" step="0.01" value="0"><output data-show="mod" data-fmt="2"></output></div>
</div>
<div class="step">
  <h3>남은 것 태우기</h3>
  <p>아메리슘 같은 무거운 잔여물은 느린 중성자를 대개 삼키기만 하고 더 무거워집니다. 빠른 중성자는 그중 훨씬 많은 몫을 쪼개므로, 고속로는 이들을 태울 수 있습니다.</p>
  <div class="ctl"><label for="spc-m3">감속 정도</label><input id="spc-m3" type="range" data-bind="mod" data-instant min="0" max="1" step="0.01" value="0"><output data-show="mod" data-fmt="2"></output></div>
</div>
<div class="step">
  <h3>그 대가</h3>
  <p>느린 중성자가 핵분열을 일으킬 확률이 훨씬 큽니다. 1 MeV에서는 표적이 수백 배 작습니다. 그래서 고속 노심에는 훨씬 진한 연료가 필요하며, 우라늄-235 3–5 % 대신 플루토늄 15–25 % 정도가 들어갑니다.</p>
  <div class="ctl"><label for="spc-m4">감속 정도</label><input id="spc-m4" type="range" data-bind="mod" data-instant min="0" max="1" step="0.01" value="1"><output data-show="mod" data-fmt="2"></output></div>
</div>`,
};

Object.assign(WT.L.labels, {
  "U{#}": "U{#}",
  "Pu{#}": "Pu{#}",
  "Np{#}": "Np{#}",
  "Am{#}": "Am{#}",
  "Cm{#}": "Cm{#}",
  "water reactor: hydrogen slows the neutrons": "경수로: 수소가 중성자를 느리게 함",
  "water: neutrons slow down": "물: 중성자가 느려짐",
  "fast reactor: sodium barely slows them": "고속로: 나트륨은 거의 느리게 하지 않음",
  "sodium: they stay fast": "나트륨: 빠른 채로 남음",
  "partly moderated": "부분 감속",
  "no moderator (sodium)": "감속재 없음 (나트륨)",
  "sodium": "나트륨",
  "water": "물",
  "thermal": "열",
  "resonances": "공명",
  "slowing down (resonances)": "감속 (공명)",
  "fast": "고속",
  "{#} eV": "{#} eV",
  "{#} keV": "{#} keV",
  "{#} MeV": "{#} MeV",
  "neutron energy →": "중성자 에너지 →",
  "born ~{#} MeV": "탄생 ~{#} MeV",
  "born near {#} MeV": "{#} MeV 근처에서 탄생",
  "most neutrons end up thermal": "대부분의 중성자가 열중성자가 됨",
  "most neutrons are slowed all the way to thermal": "대부분의 중성자가 열에너지까지 완전히 느려짐",
  "most stay between {#} keV and {#} MeV": "대부분 {#} keV와 {#} MeV 사이에 머묾",
  "most neutrons stay between {#} keV and {#} MeV": "대부분의 중성자가 {#} keV와 {#} MeV 사이에 머묾",
  "many linger at in-between energies": "많은 중성자가 중간 에너지에 머묾",
  "many neutrons linger at in-between energies": "많은 중성자가 중간 에너지에 오래 머묾",
  "hot water: kT ≈ {#} eV": "뜨거운 물: kT ≈ {#} eV",
  "thermal: kT ≈ {#} eV in hot water, about {#} km/s": "열: 뜨거운 물에서 kT ≈ {#} eV, 약 {#} km/s",
  "η = {#}: one to continue, one to breed": "η = {#}: 하나는 연쇄용, 하나는 증식용",
  "average η: U{#} {#} · Pu{#} {#}": "평균 η: U{#} {#} · Pu{#} {#}",
  "averaged over this spectrum:  η(U{#}) ≈ {#}   η(Pu{#}) ≈ {#}": "이 스펙트럼에 대한 평균:  η(U{#}) ≈ {#}   η(Pu{#}) ≈ {#}",
  "{#} % split": "{#} % 핵분열",
  "the rest are captured and grow heavier": "나머지는 포획되어 더 무거워짐",
  "the rest are captured: the nucleus just grows heavier": "나머지는 포획됨: 원자핵이 무거워질 뿐",
  "{#} b": "{#} b",
  "≈ {#} b": "≈ {#} b",
  "Pu{#} fission target": "Pu{#} 핵분열 표적",
  "Pu{#} fission cross section (target size)": "Pu{#} 핵분열 단면적 (표적 크기)",
  "{#} MeV: a target ~{#} times smaller": "{#} MeV: 표적이 ~{#}배 작음",
  "at {#} MeV the target is about {#} times smaller than at {#} eV": "{#} MeV의 표적은 약 {#}배 작음 ({#} eV 대비)",
  "illustrative shapes": "설명용 모양",
});
