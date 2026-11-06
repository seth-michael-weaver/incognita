/* Arabic: everyday (النووي في الحياة اليومية) */
WT.L.ch.everyday = {
  num: "الدرس 4", title: "النووي في الحياة اليومية", short: "الحياة اليومية",
  html: `
<div class="step">
  <h3>التصوير PET</h3>
  <p>يُطلق مقتفٍ من الفلور-18 (عمر النصف 110 دقائق) بوزيترونات، يتحوّل كلٌّ منها إلى شعاعَي غاما بطاقة 511 keV ينطلقان في اتجاهين متعاكسين. اسحب البقعة الساخنة: ترسم الحلقة خطًّا لكل زوج، وتتقاطع الخطوط حيث يوجد المقتفي.</p>
</div>
<div class="step">
  <h3>العلاج الإشعاعي</h3>
  <p>تتراكب حِزم من عدة اتجاهات على الورم، فيتلقى الجرعة كاملة بينما لا ينال كل مسار عبر النسيج السليم إلا حصة منها. اسحب لتدوير الحِزم وإبعادها عن الحبل الشوكي.</p>
  <div class="ctl"><label for="ev-n">الحِزم</label><input id="ev-n" type="range" data-bind="nb" data-instant min="1" max="7" step="1" value="5"><output data-show="nb" data-fmt="0"></output></div>
  <div class="ctl"><label for="ev-r">تدوير</label><input id="ev-r" type="range" data-bind="rotd" data-instant min="0" max="360" step="1" value="20"><output class="ev-rot"></output></div>
</div>
<div class="step">
  <h3>التكنيشيوم-99m</h3>
  <p>النظير الذي تقوم عليه معظم فحوص الطب النووي يُصدر شعاع غاما بطاقة 140 keV تراه كاميرا خارج الجسم، ومع عمر نصف قدره 6 ساعات لا يبقى منه إلا القليل بعد يوم. تستخلصه المستشفيات <a href="#chains-3">«حلبًا» من الموليبدنوم-99</a>.</p>
  <div class="ctl"><label for="ev-t">ساعات بعد الجرعة</label><input id="ev-t" type="range" data-bind="th" data-instant min="0" max="48" step="0.5" value="0"><output data-show="th" data-fmt="1"></output></div>
</div>
<div class="step">
  <h3>التأريخ بالكربون</h3>
  <p>تظل الكائنات الحية تمتص الكربون-14؛ وبعد الموت يضمحل بعمر نصف قدره 5730 سنة. اضبط العمر، أو قِس ما تبقّى لتقرأ العمر.</p>
  <div class="ctl"><label for="ev-a">العمر (سنوات)</label><input id="ev-a" type="range" data-bind="age" data-instant min="0" max="50000" step="10" value="5300"><output class="ev-age"></output></div>
  <div class="ctl"><label for="ev-f">الكربون-14 المتبقي (%)</label><input id="ev-f" type="range" data-bind="fr" data-instant min="0.3" max="100" step="0.1" value="52.7"><output class="ev-fr"></output></div>
</div>
<div class="step">
  <h3>كواشف الدخان</h3>
  <p>ذرّة مختومة من الأمريسيوم-241 ترسل جسيمات ألفا عبر فجوة هوائية صغيرة، فتُنتج أيونات تحمل تيارًا ضئيلًا. يلتقط الدخان الأيونات فيهبط التيار ويدوّي الإنذار.</p>
  <div class="ctl"><label for="ev-s">الدخان</label><input id="ev-s" type="range" data-bind="sm" data-instant min="0" max="1" step="0.01" value="0"><output class="ev-sm"></output></div>
</div>`,
};
Object.assign(WT.L.labels, {
  "Am{#}": "Am{#}",
  "Mo{#} ({#} h)": "Mo{#} ({#} ساعة)",
  "Tc{#}m ({#} h)": "Tc{#}m ({#} ساعة)",
  "a strong gamma signal, easy to image": "إشارة غاما قوية، سهلة التصوير",
  "alarm": "إنذار",
  "alpha particles make ions in the air": "جسيمات ألفا تؤيّن الهواء",
  "americium{#} (sealed)": "الأمريسيوم{#} (مختوم)",
  "americium{#} · half-life {#} years · alphas reach about {#} cm in air": "الأمريسيوم{#} · عمر النصف {#} سنة · مدى ألفا في الهواء نحو {#} cm",
  "beyond ~{#} years too little is left to measure": "بعد ~{#} سنة يبقى أقل من أن يُقاس",
  "carbon{#}": "الكربون{#}",
  "clean air: steady current": "هواء نظيف: تيار ثابت",
  "current": "التيار",
  "detector ring": "حلقة الكواشف",
  "dose": "الجرعة",
  "fluorine{#} · half-life {#} min · {#} pairs recorded": "الفلور{#} · عمر النصف {#} دقيقة · سُجّل {#} زوجًا",
  "gamma camera": "كاميرا غاما",
  "half-life {#} y": "عمر النصف {#} سنة",
  "illustration": "توضيح",
  "molybdenum{#}, half-life {#} h": "الموليبدنوم{#}، عمر النصف {#} ساعة",
  "nitrogen{#} (after a beta decay)": "النيتروجين{#} (بعد اضمحلال بيتا)",
  "pairs of {#} keV gamma rays, back to back": "أزواج من أشعة غاما {#} keV متعاكسة",
  "physical decay only": "الاضمحلال الفيزيائي فقط",
  "spinal cord": "الحبل الشوكي",
  "technetium{#}m, half-life {#} h": "التكنيشيوم{#}m، عمر النصف {#} ساعة",
  "tracer": "المقتفي",
  "tumour": "الورم",
  "tumour {#} % · spinal cord {#} % · healthy tissue at most {#} %": "الورم {#} % · الحبل الشوكي {#} % · النسيج السليم {#} % كحد أقصى",
  "tumour {#} % · spinal cord {#} % · other tissue at most {#} %": "الورم {#} % · الحبل الشوكي {#} % · أنسجة أخرى {#} % كحد أقصى",
  "years": "سنوات",
  "{#} beams cross: the tumour gets their sum": "{#} حِزم تتقاطع: ينال الورم مجموعها",
  "{#} h": "{#} ساعة",
  "{#} h: {#} % left": "{#} ساعة: بقي {#} %",
  "{#} half-lives": "{#} أعمار نصف",
  "{#} keV gamma rays": "أشعة غاما {#} keV",
  "{#} of {#} left": "بقي {#} من {#}",
  "{#} years · {#} % left": "{#} سنة · بقي {#} %",
  "Ötzi the Iceman, ~{#} y": "أوتزي رجل الجليد، ~{#} سنة",
  "tracer (drag me)": "المقتفي (اسحبني)",
  "each decay: two {#} keV gamma rays, back to back": "كل اضمحلال: شعاعا غاما {#} keV متعاكسان",
  "one beam: more dose near the skin than in the tumour": "حزمة واحدة: جرعة قرب الجلد أكبر منها في الورم",
  "a beam crosses the spinal cord: turn the beams": "حزمة تعبر الحبل الشوكي: دوِّر الحِزم",
  "fading: half is gone every {#} hours": "يخبو: يذهب النصف كل {#} ساعات",
  "after a day, about {#} % is left": "بعد يوم يبقى نحو {#} %",
  "nitrogen{#}": "النيتروجين{#}",
  "~{#} y: too little to measure": "~{#} سنة: أقل من أن يُقاس",
  "smoke: current down, alarm!": "دخان: هبط التيار، إنذار!",
  "some ions caught: current dipping": "بعض الأيونات التُقطت: التيار يهبط",
});
