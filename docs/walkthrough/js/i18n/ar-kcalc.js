/* Arabic: kcalc (Computing criticality) */
WT.L.ch.kcalc = {
  num: "الدرس 1", title: "حساب الحرجية", short: "حساب k",
  html: `
<div class="step">
  <h3>المعايير المرجعية</h3>
  <p>أربعة تجميعات حرجة معدنية سريعة من ICSBEP، بمقياس رسم حقيقي. Godiva وJezebel كرتان عاريتان؛ أما Flattop-25 وFlattop-Pu فلهما عاكس من اليورانيوم الطبيعي.</p>
</div>
<div class="step">
  <h3><i>k</i><sub>eff</sub> المحسوب</h3>
  <p>OpenMC، طاقة مستمرة، هندسة ثلاثية الأبعاد. الأربعة كلها داخل ±1σ للمعيار. لا يُستخدم <i>k</i><sub>eff</sub> في الملاءمة.</p>
</div>
<div class="step">
  <h3>مقاطع الحساسية</h3>
  <p>الحساسية المرافقة لـ <i>k</i><sub>eff</sub> تجاه كل تفاعل، لكل وحدة ليثارجيا.</p>
  <div class="btns"><button class="btn ghost" data-act="se0" aria-pressed="true">Godiva</button><button class="btn ghost" data-act="se1" aria-pressed="false">Jezebel</button><button class="btn ghost" data-act="se2" aria-pressed="false">Flattop-Pu</button></div>
</div>
<div class="step">
  <h3>التحقق بالاضطراب المباشر</h3>
  <p>تغيّرات <i>k</i><sub>eff</sub> المتنبأ بها مقابل المعاد حسابها، لـ 63 مجموعة بيانات مضطربة.</p>
</div>
<div class="step">
  <h3>قلب المفاعل C5G7</h3>
  <p>ربع قلب OECD/NEA C5G7، 1056 قضيبًا من UO<sub>2</sub> وMOX: ثنائي الأبعاد، والامتداد ثلاثي الأبعاد مع إدخال قضبان التحكم. <i>k</i><sub>eff</sub> ضمن 19&nbsp;pcm من المرجع في الحالة الثنائية وضمن 9&nbsp;pcm في كل تكوين ثلاثي الأبعاد.</p>
  <div class="btns"><button class="btn ghost" data-act="c50" aria-pressed="true">2-D</button><button class="btn ghost" data-act="c51" aria-pressed="false">3-D</button><button class="btn ghost" data-act="c52" aria-pressed="false">قضبان A</button><button class="btn ghost" data-act="c53" aria-pressed="false">قضبان B</button></div>
</div>`,
};

Object.assign(WT.L.labels, {
  "{#} pcm  (±{#} benchmark)": "{#} pcm  (المعيار ±{#})",
  "+{#} pcm  (±{#} benchmark)": "+{#} pcm  (المعيار ±{#})",
  "Calculated − experimental k, with the benchmark ±{#}σ band": "k المحسوب − التجريبي، مع نطاق ±{#}σ للمعيار",
  "Drag to rotate": "اسحب للتدوير",
  "Godiva, integral sensitivity: ν {#}, fission {#} (% k per % change)": "Godiva, الحساسية التكاملية: ν {#}، الانشطار {#} (% من k لكل % تغيّر)",
  "Jezebel, integral sensitivity: ν {#}, fission {#} (% k per % change)": "Jezebel, الحساسية التكاملية: ν {#}، الانشطار {#} (% من k لكل % تغيّر)",
  "Flattop-Pu, integral sensitivity: ν {#}, fission {#} (% k per % change)": "Flattop-Pu, الحساسية التكاملية: ν {#}، الانشطار {#} (% من k لكل % تغيّر)",
  "Godiva: ν {#}, fission {#}": "Godiva: ν {#}، الانشطار {#}",
  "Jezebel: ν {#}, fission {#}": "Jezebel: ν {#}، الانشطار {#}",
  "Flattop-Pu: ν {#}, fission {#}": "Flattop-Pu: ν {#}، الانشطار {#}",
  "UO₂: {#} × mean": "UO₂: {#} × المتوسط",
  "MOX {#} %: {#} × mean": "MOX {#} %: {#} × المتوسط",
  "OpenMC re-solve, Δk (pcm)": "إعادة حساب OpenMC، Δk (pcm)",
  "Predicted from sensitivities, Δk (pcm)": "متنبأ به من الحساسيات، Δk (pcm)",
  "predicted Δk, pcm": "Δk المتنبأ به، pcm",
  "U{#} capture": "أسر U{#}",
  "Pu{#} capture": "أسر Pu{#}",
  "U{#} elastic": "تشتت مرن U{#}",
  "Pu{#} elastic": "تشتت مرن Pu{#}",
  "U{#} fission": "انشطار U{#}",
  "Pu{#} fission": "انشطار Pu{#}",
  "U{#} inelastic": "تشتت غير مرن U{#}",
  "Pu{#} inelastic": "تشتت غير مرن Pu{#}",
  "U{#} neutrons per fission (ν)": "نيوترونات لكل انشطار U{#} (ν)",
  "Pu{#} neutrons per fission (ν)": "نيوترونات لكل انشطار Pu{#} (ν)",
  "Relative pin power (hover a pin)": "القدرة النسبية للقضيب (مرّر المؤشر فوق قضيب)",
  "Relative pin power (tap a pin)": "القدرة النسبية للقضيب (المس قضيبًا)",
  "To scale.": "بمقياس حقيقي.",
  "To scale. Drag to rotate.": "بمقياس حقيقي. اسحب للتدوير.",
  "core {#} cm, reflector {#} cm": "القلب {#} سم، العاكس {#} سم",
  "radius {#} cm": "نصف القطر {#} سم",
  "{#} cm in {#} cm": "{#} سم في {#} سم",
  "k = {#}; reference {#} ({#} pcm)": "k = {#}؛ المرجع {#} ({#} pcm)",
  "k = {#}; reference {#} (+{#} pcm)": "k = {#}؛ المرجع {#} (+{#} pcm)",
  "k {#}, reference {#}": "k {#}، المرجع {#}",
  "plutonium in natural uranium": "بلوتونيوم داخل يورانيوم طبيعي",
  "plutonium metal": "بلوتونيوم معدني",
  "uranium{#} in natural uranium": "يورانيوم{#} داخل يورانيوم طبيعي",
  "uranium{#} metal": "يورانيوم{#} معدني",
  "water": "ماء",
  "×{#} of mean": "×{#} من المتوسط",
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
