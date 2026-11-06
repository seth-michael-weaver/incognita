/* Arabic: spentfuel (الوقود المستهلك نويدةً نويدة) */
WT.L.ch.spentfuel = {
  num: "الدرس 1", title: "الوقود المستهلك نويدةً نويدة", short: "نويدةً نويدة",
  html: `
<div class="step">
  <h3>ماذا في الداخل</h3>
  <p>طن من وقود PWR بعد عام من تفريغه (مخصَّب 4.2 %، 50 GWd/t): الكتلة كلها تقريبًا يورانيوم، والنشاط كله تقريبًا في بضعة كيلوغرامات.</p>
</div>
<div class="step">
  <h3>النشاط أم السمية الإشعاعية</h3>
  <p>البكريل يعدّ الاضمحلالات؛ والسيفرت يزن كل اضمحلال بضرره إذا ابتُلع، مما يرفع مصدِرات ألفا.</p>
  <div class="btns"><button class="btn ghost" data-act="mA" aria-pressed="false">النشاط (Bq)</button> <button class="btn ghost" data-act="mT" aria-pressed="true">السمية الإشعاعية (Sv)</button></div>
</div>
<div class="step">
  <h3>من يهيمن ومتى</h3>
  <p>مرِّر المؤشر فوق شريط أو المسه لمعرفة اسمه؛ واسحب على محور الزمن لترتيبها.</p>
</div>
<div class="step">
  <h3>أعِد تدوير البلوتونيوم</h3>
  <p>إعادة المعالجة بعد أربع سنوات تُخرج البلوتونيوم (ومعه اليورانيوم). كم يبقى خلفها؟</p>
  <div class="btns"><span class="sf-k" style="font:600 13px var(--sans);color:var(--soft);margin-right:4px;align-self:center">Pu removed</span> <button class="btn ghost" data-act="pu0" aria-pressed="true">0 %</button> <button class="btn ghost" data-act="pu99" aria-pressed="false">99 %</button> <button class="btn ghost" data-act="pu999" aria-pressed="false">99.9 %</button></div>
</div>
<div class="step">
  <h3>أزِل الأكتينيدات الثانوية أيضًا</h3>
  <p>أخرِج الأمريسيوم والكوريوم والنبتونيوم كذلك: عندها يحدّد الـ 1 % أو 0.1 % المتبقي الزمن.</p>
  <div class="btns"><span class="sf-k" style="font:600 13px var(--sans);color:var(--soft);margin-right:4px;align-self:center">Pu removed</span> <button class="btn ghost" data-act="pu0" aria-pressed="true">0 %</button> <button class="btn ghost" data-act="pu99" aria-pressed="false">99 %</button> <button class="btn ghost" data-act="pu999" aria-pressed="false">99.9 %</button></div>
  <div class="btns"><span class="sf-k" style="font:600 13px var(--sans);color:var(--soft);margin-right:4px;align-self:center">Am, Cm, Np removed</span> <button class="btn ghost" data-act="ma0" aria-pressed="true">0 %</button> <button class="btn ghost" data-act="ma99" aria-pressed="false">99 %</button> <button class="btn ghost" data-act="ma999" aria-pressed="false">99.9 %</button></div>
</div>`,
};
Object.assign(WT.L.labels, {
  "Am{#}": "Am{#}",
  "Am{#} {#} %": "Am{#} {#} %",
  "Cm{#}": "Cm{#}",
  "Cs{#}": "Cs{#}",
  "I{#}": "I{#}",
  "NEA {#} + computed": "NEA {#} + محسوب",
  "Np{#}": "Np{#}",
  "Pu{#}": "Pu{#}",
  "Pu{#} {#} %": "Pu{#} {#} %",
  "Sr{#}": "Sr{#}",
  "Sr{#} + Y{#}": "Sr{#} + Y{#}",
  "Tc{#}": "Tc{#}",
  "activity": "النشاط",
  "activity after {#} year (log scale)": "النشاط بعد {#} سنة (مقياس لوغاريتمي)",
  "below the ore after ≈ {#} years": "تحت الخام بعد ≈ {#} سنة",
  "computed (Bateman decay, ICRP{#}) · band height = share of the total": "محسوب (اضمحلال باتمان، ICRP{#}) · ارتفاع الشريط = الحصة من المجموع",
  "computed · band height = share": "محسوب · ارتفاع الشريط = الحصة",
  "drag along the time axis · hover a band": "اسحب على محور الزمن · مرِّر فوق شريط",
  "inventory: OECD-NEA {#} ({#} %, {#} GWd/t) + computed fission products": "المخزون: OECD-NEA {#} ({#} %، {#} GWd/t) + نواتج انشطار محسوبة",
  "mass": "الكتلة",
  "mass (log scale)": "الكتلة (مقياس لوغاريتمي)",
  "most of the {#} kg of fission products is stable; activity includes short-lived daughters": "معظم الـ {#} kg من نواتج الانشطار مستقر؛ والنشاط يشمل البنات قصيرة العمر",
  "once-through": "دورة مفتوحة",
  "once-through (no recycling)": "دورة مفتوحة (بلا إعادة تدوير)",
  "ore: {#}×{#}⁵ Sv": "الخام: {#}×{#}⁵ Sv",
  "other FP": "نواتج انشطار أخرى",
  "other FP: mostly stable": "نواتج انشطار أخرى: مستقرة غالبًا",
  "other fission products": "نواتج انشطار أخرى",
  "radiotoxicity if swallowed (Sv), relative to the ore": "السمية الإشعاعية عند الابتلاع (Sv) نسبةً إلى الخام",
  "radiotoxicity ÷ ore": "السمية الإشعاعية ÷ الخام",
  "reprocessing at {#} yr": "إعادة المعالجة عند {#} سنة",
  "the ore it came from: {#} t natural uranium + daughters = {#}×{#}⁵ Sv": "الخام الذي جاء منه: {#} t يورانيوم طبيعي + البنات = {#}×{#}⁵ Sv",
  "then mostly Am{#} ({#} %)": "حينها غالبًا Am{#} ({#} %)",
  "then mostly Pb{#} + Po{#} ({#} %)": "حينها غالبًا Pb{#} + Po{#} ({#} %)",
  "then mostly Sr{#} + Y{#} ({#} %)": "حينها غالبًا Sr{#} + Y{#} ({#} %)",
  "uranium": "اليورانيوم",
  "years after unloading (log scale) →": "السنوات بعد التفريغ (مقياس لوغاريتمي) →",
  "{#} g": "{#} g",
  "{#} kg": "{#} kg",
  "{#} million": "{#} مليون",
  "{#} years:": "{#} سنة:",
  "{#} yr": "{#} سنة",
  "{#}¹³ Bq": "{#}¹³ Bq",
  "{#}¹⁰ Bq": "{#}¹⁰ Bq",
  "{#}¹⁶ Bq": "{#}¹⁶ Bq",
  "other Am, Cm": "Am و Cm أخرى",
  "decay daughters (Ra, Pb, Po, Th…)": "بنات الاضمحلال (Ra، Pb، Po، Th…)",
  "daughters": "البنات",
  "still above the ore after a million years": "ما زال فوق الخام بعد مليون سنة",
  "drag the time · tap a band": "اسحب الزمن · المس شريطًا",
  "activity ÷ ore": "النشاط ÷ الخام",
  "activity (Bq), relative to the ore": "النشاط (Bq) نسبةً إلى الخام",
});
