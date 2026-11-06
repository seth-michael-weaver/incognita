/* Arabic: breeding (توليد وقود جديد) */
WT.L.ch.breeding = {
  num: "الدرس 1", title: "توليد وقود جديد", short: "التوليد",
  html: `
<div class="step">
  <h3>المادة الخصبة تصير انشطارية</h3>
  <p>اليورانيوم-238 لا يكاد ينشطر، لكنه يستطيع التقاط نيوترون. وبعد اضمحلالين بيتا (يتحول في كل مرة نيوترون في داخله إلى بروتون) يصير بلوتونيوم-239، وهو ينشطر بسهولة. والثوريوم-232 يفعل الشيء نفسه فيصير يورانيوم-233.</p>
  <div class="btns"><button class="btn ghost" data-act="bcU" aria-pressed="true">اليورانيوم-238</button> <button class="btn ghost" data-act="bcT" aria-pressed="false">الثوريوم-232</button></div>
</div>
<div class="step">
  <h3>ميزانية النيوترونات</h3>
  <p>كل نيوترون يُمتص في الوقود الانشطاري يعيد <i>η</i> نيوترونًا جديدًا. واحد منها يجب أن يسبب الانشطار التالي، وبعضها يضيع؛ وما يتبقى يمكنه أن يولّد وقودًا. مع اليورانيوم-235 والنيوترونات البطيئة لا تتكوّن إلا نحو 0.6 نواة انشطارية جديدة مقابل كل نواة تحترق.</p>
  <div class="btns"><button class="btn ghost" data-act="bfU5" aria-pressed="true">U-235</button> <button class="btn ghost" data-act="bfP9" aria-pressed="false">Pu-239</button> <button class="btn ghost" data-act="bfU3" aria-pressed="false">U-233</button></div>
  <div class="btns"><button class="btn ghost" data-act="bsT" aria-pressed="true">نيوترونات بطيئة</button> <button class="btn ghost" data-act="bsF" aria-pressed="false">نيوترونات سريعة</button></div>
</div>
<div class="step">
  <h3>النيوترونات السريعة تولّد</h3>
  <p>للتوليد يجب أن يواصل نيوترون واحد السلسلة وأن يصنع واحد على الأقل وقودًا جديدًا، لذا يجب أن تتجاوز <i>η</i> العدد 2 بأكثر من المفقود. والبلوتونيوم-239 في مفاعل سريع يعطي نحو 2.4: ما يكفي ويزيد.</p>
  <div class="ctl"><label for="br-l1">النيوترونات المفقودة</label><input id="br-l1" type="range" data-bind="L" data-instant min="0.05" max="0.8" step="0.01" value="0.2"><output data-show="L" data-fmt="2"></output></div>
</div>
<div class="step">
  <h3>الثوريوم مع النيوترونات البطيئة</h3>
  <p>مع النيوترونات البطيئة لا يعطي البلوتونيوم-239 إلا نحو 2.1، أما اليورانيوم-233 فيعطي 2.29. هذا الهامش يتيح لمفاعل ثوريوم أن يولّد بالنيوترونات البطيئة، إن كان يهدر القليل جدًا منها. اخفض المفقود حتى يبدأ التوليد.</p>
  <div class="ctl"><label for="br-l2">النيوترونات المفقودة</label><input id="br-l2" type="range" data-bind="L" data-instant min="0.05" max="0.8" step="0.01" value="0.35"><output data-show="L" data-fmt="2"></output></div>
</div>
<div class="step">
  <h3>نسبة التحويل</h3>
  <p>نسبة التحويل هي عدد الأنوية الانشطارية المصنوعة مقابل كل نواة انشطارية تحترق. تحت 1 ينفد الوقود ببطء (مفاعل محوِّل، مثل مفاعلات الماء اليوم)؛ وفوق 1 ينتهي المفاعل بوقود أكثر مما بدأ به (مفاعل مولِّد).</p>
  <div class="btns"><button class="btn ghost" data-act="bfU5" aria-pressed="true">U-235</button> <button class="btn ghost" data-act="bfP9" aria-pressed="false">Pu-239</button> <button class="btn ghost" data-act="bfU3" aria-pressed="false">U-233</button></div>
  <div class="btns"><button class="btn ghost" data-act="bsT" aria-pressed="true">نيوترونات بطيئة</button> <button class="btn ghost" data-act="bsF" aria-pressed="false">نيوترونات سريعة</button></div>
</div>`,
};
Object.assign(WT.L.labels, {
  "illustration": "توضيح",
  "U{#}": "U{#}",
  "Np{#}": "Np{#}",
  "Pu{#}": "Pu{#}",
  "Th{#}": "Th{#}",
  "Pa{#}": "Pa{#}",
  "{#} p": "{#} p",
  "{#} protons": "{#} بروتونًا",
  "fertile": "خصبة",
  "fertile: barely splits": "خصبة: لا تكاد تنشطر",
  "fissile": "انشطارية",
  "fissile: splits easily": "انشطارية: تنشطر بسهولة",
  "+ n": "+ n",
  "catch": "التقاط",
  "{#} min": "{#} دقيقة",
  "{#} d": "{#} يوم",
  "e⁻": "e⁻",
  "electron": "إلكترون",
  "antineutrino": "نيوترينو مضاد",
  "{a} waiting: day {b}": "{a} تنتظر: اليوم {b}",
  "a batch of {a} waiting · day {b}": "دفعة من {a} تنتظر · اليوم {b}",
  "{a} % now {b}": "{a} % صارت {b}",
  "after {#} weeks, {#} % has become Pu{#}": "بعد {#} أسبوع، صار {#} % منها Pu{#}",
  "after {#} months, {#} % has become U{#}": "بعد {#} أشهر، صار {#} % منها U{#}",
  "slow step: Np{#}, half-life {#} d": "الخطوة البطيئة: Np{#}، عمر النصف {#} يوم",
  "the slow step is Np{#} (half-life {#} days)": "الخطوة البطيئة هي Np{#} (عمر النصف {#} يوم)",
  "slow step: Pa{#}, half-life {#} d": "الخطوة البطيئة: Pa{#}، عمر النصف {#} يوم",
  "the slow step is Pa{#} (half-life {#} days)": "الخطوة البطيئة هي Pa{#} (عمر النصف {#} يوم)",
  "slow neutrons": "نيوترونات بطيئة",
  "fast neutrons": "نيوترونات سريعة",
  "next fission": "الانشطار التالي",
  "U{#} → Pu{#}": "U{#} → Pu{#}",
  "Th{#} → U{#}": "Th{#} → U{#}",
  "lost": "مفقود",
  "next fission: keeps the chain going": "الانشطار التالي: يُبقي السلسلة مستمرة",
  "breeds: U{#} → Pu{#}": "يولّد: U{#} → Pu{#}",
  "breeds: Th{#} → U{#}": "يولّد: Th{#} → U{#}",
  "lost: water, steel, poisons, leakage": "مفقود: ماء، فولاذ، سموم، تسرّب",
  "{a} per absorption": "{a} لكل امتصاص",
  "chain": "السلسلة",
  "breed": "توليد",
  "η ≈ {a}": "η ≈ {a}",
  "η = {a}": "η = {a}",
  "{#}: breeding line": "{#}: خط التوليد",
  "neutrons per absorption": "نيوترونات لكل امتصاص",
  "neutrons out per neutron absorbed in the fuel": "النيوترونات الخارجة لكل نيوترون يُمتص في الوقود",
  "conversion ratio ≈ η − {#} − lost = {a}: breeds": "نسبة التحويل ≈ η − {#} − المفقود = {a}: يولّد",
  "conversion ratio ≈ η − {#} − lost = {a}: breeds, makes more fuel than it burns": "نسبة التحويل ≈ η − {#} − المفقود = {a}: يولّد، يصنع وقودًا أكثر مما يحرق",
  "conversion ratio ≈ η − {#} − lost = {a}: converts": "نسبة التحويل ≈ η − {#} − المفقود = {a}: يحوّل",
  "conversion ratio ≈ η − {#} − lost = {a}: converts, makes less fuel than it burns": "نسبة التحويل ≈ η − {#} − المفقود = {a}: يحوّل، يصنع وقودًا أقل مما يحرق",
  "U{#} (fertile)": "U{#} (خصبة)",
  "Th{#} (fertile)": "Th{#} (خصبة)",
  "split": "منشطرة",
  "split (fission products)": "منشطرة (نواتج انشطار)",
  "burned {a}": "احترق {a}",
  "made {a}": "تكوّن {a}",
  "{a} · slow neutrons": "{a} · نيوترونات بطيئة",
  "{a} · fast neutrons": "{a} · نيوترونات سريعة",
  "conversion ratio {a}: a breeder": "نسبة التحويل {a}: مفاعل مولِّد",
  "conversion ratio {a}: a converter": "نسبة التحويل {a}: مفاعل محوِّل",
});
