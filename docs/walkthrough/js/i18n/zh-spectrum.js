/* Chinese: spectrum (快堆与热堆) */
WT.L.ch.spectrum = {
  num: "第1课", title: "快堆与热堆", short: "快堆与热堆",
  html: `
<div class="step">
  <h3>中子有多快</h3>
  <p>中子诞生时速度很快，能量约 2 MeV。在水堆中，它们不断与氢碰撞弹开，直到慢得和水本身的原子一样：这就是<b>热中子</b>。快堆没有慢化剂，所以中子一直保持快速。在两者之间滑动看看。</p>
  <div class="ctl"><label for="spc-m1">慢化程度</label><input id="spc-m1" type="range" data-bind="mod" data-instant min="0" max="1" step="0.01" value="1"><output data-show="mod" data-fmt="2"></output></div>
</div>
<div class="step">
  <h3>多余的中子</h3>
  <p><i>η</i> 是燃料原子核每吸收一个中子所放回的中子数。一个用来维持链式反应；要增殖新燃料，还需要多出一个，所以 <i>η</i> 要明显大于 2。钚-239 只有在快中子下才能做到这一点。</p>
  <div class="ctl"><label for="spc-m2">慢化程度</label><input id="spc-m2" type="range" data-bind="mod" data-instant min="0" max="1" step="0.01" value="0"><output data-show="mod" data-fmt="2"></output></div>
</div>
<div class="step">
  <h3>烧掉剩余物</h3>
  <p>像镅这样的重剩余物，遇到慢中子时大多只是把它吞下，变得更重。快中子能使其中大得多的一部分裂变，所以快堆可以把它们烧掉。</p>
  <div class="ctl"><label for="spc-m3">慢化程度</label><input id="spc-m3" type="range" data-bind="mod" data-instant min="0" max="1" step="0.01" value="0"><output data-show="mod" data-fmt="2"></output></div>
</div>
<div class="step">
  <h3>代价</h3>
  <p>慢中子引起裂变的可能性要大得多：在 1 MeV 时，靶子要小几百倍。所以快堆芯需要富集得多的燃料，约 15–25 % 的钚，而不是 3–5 % 的铀-235。</p>
  <div class="ctl"><label for="spc-m4">慢化程度</label><input id="spc-m4" type="range" data-bind="mod" data-instant min="0" max="1" step="0.01" value="1"><output data-show="mod" data-fmt="2"></output></div>
</div>`,
};
Object.assign(WT.L.labels, {
  // core slice
  "water reactor: hydrogen slows the neutrons": "水堆：氢使中子慢化",
  "water: neutrons slow down": "水：中子被慢化",
  "fast reactor: sodium barely slows them": "快堆：钠几乎不使它们减速",
  "sodium: they stay fast": "钠：中子保持快速",
  "partly moderated": "部分慢化",
  "no moderator (sodium)": "无慢化剂（钠）",
  "sodium": "钠",
  "water": "水",
  // minor actinides
  "Pu{#}": "Pu{#}", "Np{#}": "Np{#}", "Am{#}": "Am{#}", "Cm{#}": "Cm{#}", "U{#}": "U{#}",
  "{#} % split": "{#} % 裂变",
  "the rest are captured and grow heavier": "其余被俘获，变得更重",
  "the rest are captured: the nucleus just grows heavier": "其余被俘获：原子核只是变得更重",
  // spectrum
  "thermal": "热中子",
  "resonances": "共振区",
  "slowing down (resonances)": "慢化（共振区）",
  "fast": "快中子",
  "{#} eV": "{#} eV",
  "{#} keV": "{#} keV",
  "{#} MeV": "{#} MeV",
  "neutron energy →": "中子能量 →",
  "born ~{#} MeV": "诞生时约 {#} MeV",
  "born near {#} MeV": "诞生时约 {#} MeV",
  "most neutrons end up thermal": "大多数中子最终成为热中子",
  "most neutrons are slowed all the way to thermal": "大多数中子一直被慢化到热能区",
  "most stay between {#} keV and {#} MeV": "大多数停留在 {#} keV 到 {#} MeV 之间",
  "most neutrons stay between {#} keV and {#} MeV": "大多数中子停留在 {#} keV 到 {#} MeV 之间",
  "many linger at in-between energies": "许多中子滞留在中间能量",
  "many neutrons linger at in-between energies": "许多中子在中间能量上滞留",
  "hot water: kT ≈ {#} eV": "热水中：kT ≈ {#} eV",
  "thermal: kT ≈ {#} eV in hot water, about {#} km/s": "热中子：在热水中 kT ≈ {#} eV，约 {#} km/s",
  // eta
  "η = {#}: one to continue, one to breed": "η = {#}：一个维持链式反应，一个用于增殖",
  "average η: U{#} {#} · Pu{#} {#}": "平均 η：U{#} {#} · Pu{#} {#}",
  "averaged over this spectrum:  η(U{#}) ≈ {#}   η(Pu{#}) ≈ {#}": "对此能谱平均：  η(U{#}) ≈ {#}   η(Pu{#}) ≈ {#}",
  // cross section
  "{#} b": "{#} b",
  "≈ {#} b": "≈ {#} b",
  "Pu{#} fission target": "Pu{#} 裂变靶子",
  "Pu{#} fission cross section (target size)": "Pu{#} 裂变截面（靶子大小）",
  "{#} MeV: a target ~{#} times smaller": "{#} MeV：靶子约小 {#} 倍",
  "at {#} MeV the target is about {#} times smaller than at {#} eV": "在 {#} MeV 时，靶子约小 {#} 倍（与 {#} eV 时相比）",
  "illustrative shapes": "示意性形状",
});
