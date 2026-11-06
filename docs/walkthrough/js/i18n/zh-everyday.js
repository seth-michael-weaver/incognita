/* Simplified Chinese (简体中文): everyday (日常生活中的核技术) */
WT.L.ch.everyday = {
  num: "第4课", title: "日常生活中的核技术", short: "日常应用",
  html: `
<div class="step">
  <h3>PET 扫描</h3>
  <p>氟-18 示踪剂（半衰期 110 分钟）发射正电子，每个正电子都会变成两条背对背飞出的 511 keV 伽马射线。拖动热点：探测环为每一对射线画一条线，这些线交汇在示踪剂所在的位置。</p>
</div>
<div class="step">
  <h3>放射治疗</h3>
  <p>来自多个方向的射束在肿瘤上叠加，肿瘤得到全部剂量，而穿过健康组织的每条路径只得到其中一份。拖动以转动射束，让它们避开脊髓。</p>
  <div class="ctl"><label for="ev-n">射束</label><input id="ev-n" type="range" data-bind="nb" data-instant min="1" max="7" step="1" value="5"><output data-show="nb" data-fmt="0"></output></div>
  <div class="ctl"><label for="ev-r">转动</label><input id="ev-r" type="range" data-bind="rotd" data-instant min="0" max="360" step="1" value="20"><output class="ev-rot"></output></div>
</div>
<div class="step">
  <h3>锝-99m</h3>
  <p>大多数核医学检查所用的这种同位素发出 140 keV 的伽马射线，体外的相机就能看到；它的半衰期为 6 小时，一天后所剩无几。医院<a href="#chains-3">从钼-99 中“挤奶”得到它</a>。</p>
  <div class="ctl"><label for="ev-t">给药后的小时数</label><input id="ev-t" type="range" data-bind="th" data-instant min="0" max="48" step="0.5" value="0"><output data-show="th" data-fmt="1"></output></div>
</div>
<div class="step">
  <h3>碳定年</h3>
  <p>生物活着时不断摄入碳-14；死后碳-14 以 5730 年的半衰期衰变。设定年龄，或测量剩余量来读出年龄。</p>
  <div class="ctl"><label for="ev-a">年龄（年）</label><input id="ev-a" type="range" data-bind="age" data-instant min="0" max="50000" step="10" value="5300"><output class="ev-age"></output></div>
  <div class="ctl"><label for="ev-f">剩余碳-14（%）</label><input id="ev-f" type="range" data-bind="fr" data-instant min="0.3" max="100" step="0.1" value="52.7"><output class="ev-fr"></output></div>
</div>
<div class="step">
  <h3>烟雾探测器</h3>
  <p>一小粒密封的镅-241 向一道小空气间隙发射 α 粒子，产生的离子形成微弱电流。烟雾捕获离子，电流下降，警报响起。</p>
  <div class="ctl"><label for="ev-s">烟雾</label><input id="ev-s" type="range" data-bind="sm" data-instant min="0" max="1" step="0.01" value="0"><output class="ev-sm"></output></div>
</div>`,
};
Object.assign(WT.L.labels, {
  "Am{#}": "Am{#}",
  "Mo{#} ({#} h)": "Mo{#}（{#} h）",
  "Tc{#}m ({#} h)": "Tc{#}m（{#} h）",
  "a strong gamma signal, easy to image": "伽马信号强，容易成像",
  "alarm": "报警",
  "alpha particles make ions in the air": "α 粒子使空气电离",
  "americium{#} (sealed)": "镅{#}（密封）",
  "americium{#} · half-life {#} years · alphas reach about {#} cm in air": "镅{#} · 半衰期 {#} 年 · α 粒子在空气中射程约 {#} cm",
  "beyond ~{#} years too little is left to measure": "超过约 {#} 年，剩余量太少无法测量",
  "carbon{#}": "碳{#}",
  "clean air: steady current": "空气洁净：电流稳定",
  "current": "电流",
  "detector ring": "探测器环",
  "dose": "剂量",
  "fluorine{#} · half-life {#} min · {#} pairs recorded": "氟{#} · 半衰期 {#} min · 已记录 {#} 对",
  "gamma camera": "伽马相机",
  "half-life {#} y": "半衰期 {#} 年",
  "illustration": "示意图",
  "molybdenum{#}, half-life {#} h": "钼{#}，半衰期 {#} h",
  "nitrogen{#} (after a beta decay)": "氮{#}（β 衰变之后）",
  "pairs of {#} keV gamma rays, back to back": "成对的 {#} keV 伽马射线，背对背",
  "physical decay only": "仅物理衰变",
  "spinal cord": "脊髓",
  "technetium{#}m, half-life {#} h": "锝{#}m，半衰期 {#} h",
  "tracer": "示踪剂",
  "tumour": "肿瘤",
  "tumour {#} % · spinal cord {#} % · healthy tissue at most {#} %": "肿瘤 {#} % · 脊髓 {#} % · 健康组织至多 {#} %",
  "tumour {#} % · spinal cord {#} % · other tissue at most {#} %": "肿瘤 {#} % · 脊髓 {#} % · 其他组织至多 {#} %",
  "years": "年",
  "{#} beams cross: the tumour gets their sum": "{#} 条射束交汇：肿瘤得到它们的总和",
  "{#} h": "{#} h",
  "{#} h: {#} % left": "{#} h：剩余 {#} %",
  "{#} half-lives": "{#} 个半衰期",
  "{#} keV gamma rays": "{#} keV 伽马射线",
  "{#} of {#} left": "剩余 {#}/{#}",
  "{#} years · {#} % left": "{#} 年 · 剩余 {#} %",
  "Ötzi the Iceman, ~{#} y": "冰人奥茨，约 {#} 年",
  "tracer (drag me)": "示踪剂（拖动我）",
  "each decay: two {#} keV gamma rays, back to back": "每次衰变：两条 {#} keV 伽马射线，背对背",
  "one beam: more dose near the skin than in the tumour": "单束：皮肤附近的剂量比肿瘤还高",
  "a beam crosses the spinal cord: turn the beams": "有射束穿过脊髓：请转动射束",
  "fading: half is gone every {#} hours": "逐渐减弱：每 {#} 小时少一半",
  "after a day, about {#} % is left": "一天后约剩 {#} %",
  "nitrogen{#}": "氮{#}",
  "~{#} y: too little to measure": "约 {#} 年：太少，无法测量",
  "smoke: current down, alarm!": "有烟：电流下降，报警！",
  "some ions caught: current dipping": "部分离子被捕获：电流下降",
});
