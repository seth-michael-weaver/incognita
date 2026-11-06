/* Arabic: chains (سلاسل الاضمحلال والتوازن) */
WT.L.ch.chains = {
  num: "الدرس 1", title: "سلاسل الاضمحلال والتوازن", short: "سلاسل الاضمحلال",
  html: `
<div class="step">
  <h3>الأم والبنت والحفيدة</h3>
  <p>كثيرًا ما تكون النواة الجديدة غير مستقرة هي الأخرى. تضمحل الأم إلى بنت، وتضمحل البنت إلى حفيدة مستقرة. تتراكم البنات ثم تتلاشى؛ ومقدار تراكمها يتوقف على سرعة اضمحلالها مقارنةً بالأم.</p>
  <div class="ctl"><label for="ch-t2">عمر النصف للبنت (s)</label><input id="ch-t2" type="range" data-bind="T2" data-instant min="0.5" max="9" step="0.5" value="1.5"><output data-show="T2" data-fmt="1"></output></div>
  <div class="btns"><button class="btn ghost" data-act="refill">عينة جديدة</button></div>
</div>
<div class="step">
  <h3>التوازن القرني: الراديوم والرادون</h3>
  <p>يدوم الراديوم-226 نحو 1600 سنة؛ أما بنته، غاز الرادون-222، فلا يدوم إلا 3.8 يوم. في وعاء محكم يتراكم الرادون حتى يضمحل بالسرعة نفسها التي يتكوّن بها: <i>A</i><sub>Rn</sub> = <i>A</i><sub>Ra</sub>(1 − e<sup>−λt</sup>)، حيث λ معدل اضمحلال الرادون. وبعد بضعة أسابيع يتفكك الاثنان بالمعدل نفسه.</p>
  <div class="btns"><button class="btn" data-act="vent">افتح الوعاء</button></div>
</div>
<div class="step">
  <h3>التوازن العابر: بقرة التكنيشيوم</h3>
  <p>تحصل المستشفيات على عمود من الموليبدنوم-99 (66 ساعة) يظل ينتج التكنيشيوم-99m (6 ساعات)، أكثر المقتفيات الطبية استخدامًا. اغسل التكنيشيوم منه كل صباح فينمو من جديد، متبعًا الموليبدنوم الذي يخبو ببطء.</p>
  <div class="btns"><button class="btn" data-act="milk">احلب المولّد</button><button class="btn ghost" data-act="genre">مولّد جديد</button></div>
</div>
<div class="step">
  <h3>نزولًا في سلسلة اليورانيوم</h3>
  <p>يحتاج اليورانيوم-238 إلى أربع عشرة خطوة ليصير رصاصًا مستقرًا. اضمحلال ألفا ينقل النواة خطوتين إلى الأسفل وخطوتين إلى اليسار على هذا المخطط، واضمحلال بيتا خطوة إلى الأعلى وخطوة إلى اليسار. وفي خام يورانيوم قديم لم يُمس يتفكك كل عضو في السلسلة بالمعدل نفسه.</p>
  <div class="btns"><button class="btn" data-act="next">الاضمحلال التالي</button><button class="btn ghost" data-act="restart">ابدأ من جديد</button></div>
</div>`,
};
Object.assign(WT.L.labels, {
  "parent {#}": "الأم {#}",
  "daughter {#}": "البنت {#}",
  "stable {#}": "مستقرة {#}",
  "parent ({#} s): {#}": "الأم ({#} s): {#}",
  "daughter ({#} s): {#}": "البنت ({#} s): {#}",
  "granddaughter (stable): {#}": "الحفيدة (مستقرة): {#}",
  "daughter peaks: {#} %": "ذروة البنت: {#} %",
  "{#} s": "{#} s",
  "illustrative half-lives": "أعمار نصف توضيحية",
  "radium{#}": "الراديوم{#}",
  "radon{#} gas": "غاز الرادون{#}",
  "radium": "الراديوم",
  "radium activity": "نشاط الراديوم",
  "{#} d": "{#} يوم",
  "days →": "الأيام →",
  "radon": "الرادون",
  "radon activity": "نشاط الرادون",
  "day {#}: radon at {#} % of radium": "اليوم {#}: الرادون عند {#} % من الراديوم",
  "A(Rn) = A(Ra) × ({#} − exp(−λt))": "A(Rn) = A(Ra) × ({#} − exp(−λt))",
  "A(radon) = A(radium) × ({#} − exp(−λt))": "A(Rn) = A(Ra) × ({#} − exp(−λt))",
  "Mo{#}": "Mo{#}",
  "Tc{#}m out": "Tc{#}m خارج",
  "Tc{#}m to the patient": "Tc{#}m إلى المريض",
  "molybdenum{#}": "الموليبدنوم{#}",
  "dashed: never milked": "المتقطع: دون حلب",
  "activity": "النشاط",
  "{#} h since last milking · Tc{#}m at {#} % of Mo{#}": "{#} ساعة منذ آخر حلب · Tc{#}m عند {#} % من Mo{#}",
  "regrows to its peak in about {#} hours": "يعود إلى ذروته في نحو {#} ساعة",
  "Pb": "Pb", "Bi": "Bi", "Po": "Po", "At": "At", "Rn": "Rn", "Fr": "Fr", "Ra": "Ra", "Ac": "Ac", "Th": "Th", "Pa": "Pa", "U": "U",
  "neutrons →": "النيوترونات →",
  "grey: stable": "الرمادي: مستقر",
  "protons ↑": "البروتونات ↑",
  "alpha: {#} p, {#} n": "ألفا: {#} p، {#} n",
  "alpha: loses {#} protons and {#} neutrons": "ألفا: تفقد {#} بروتون و{#} نيوترون",
  "beta: n → p": "بيتا: n → p",
  "beta: a neutron becomes a proton": "بيتا: نيوترون يصير بروتونًا",
  "U{#} · half-life {#} billion yr · alpha next": "U{#} · عمر النصف {#} مليار سنة · التالي ألفا",
  "Th{#} · half-life {#} days · beta next": "Th{#} · عمر النصف {#} يوم · التالي بيتا",
  "Pa{#}m · half-life {#} min · beta next": "Pa{#}m · عمر النصف {#} دقيقة · التالي بيتا",
  "U{#} · half-life {#} yr · alpha next": "U{#} · عمر النصف {#} سنة · التالي ألفا",
  "Th{#} · half-life {#} yr · alpha next": "Th{#} · عمر النصف {#} سنة · التالي ألفا",
  "Ra{#} · half-life {#} yr · alpha next": "Ra{#} · عمر النصف {#} سنة · التالي ألفا",
  "Rn{#} · half-life {#} days · alpha next": "Rn{#} · عمر النصف {#} يوم · التالي ألفا",
  "Po{#} · half-life {#} min · alpha next": "Po{#} · عمر النصف {#} دقيقة · التالي ألفا",
  "Pb{#} · half-life {#} min · beta next": "Pb{#} · عمر النصف {#} دقيقة · التالي بيتا",
  "Bi{#} · half-life {#} min · beta next": "Bi{#} · عمر النصف {#} دقيقة · التالي بيتا",
  "Po{#} · half-life {#} µs · alpha next": "Po{#} · عمر النصف {#} µs · التالي ألفا",
  "Pb{#} · half-life {#} years · beta next": "Pb{#} · عمر النصف {#} سنة · التالي بيتا",
  "Bi{#} · half-life {#} days · beta next": "Bi{#} · عمر النصف {#} يوم · التالي بيتا",
  "Po{#} · half-life {#} days · alpha next": "Po{#} · عمر النصف {#} يوم · التالي ألفا",
  "Pb{#}: stable, the chain ends": "Pb{#}: مستقر، وتنتهي السلسلة",
  "step {#} of {#} · tap the nucleus": "الخطوة {#} من {#} · انقر على النواة",
});
