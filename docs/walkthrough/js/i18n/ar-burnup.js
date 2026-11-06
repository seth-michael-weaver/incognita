/* Arabic: burnup (احتراق الوقود) */
WT.L.ch.burnup = {
  num: "الدرس 1", title: "احتراق الوقود", short: "الاحتراق",
  html: `
<div class="step">
  <h3>قرص وقود طوال عمره</h3>
  <p>هذه ألف ذرة من قرص وقود جديد: 45 منها يورانيوم-235 والباقي يورانيوم-238. شغّل المفاعل وراقب اليورانيوم-235 ينشطر بينما تظهر ذرات جديدة. <b>الاحتراق</b> يعدّ الطاقة المستخرجة، بالغيغاواط-يوم لكل طن من اليورانيوم؛ ومفاعلات الماء تتوقف عند نحو 45–55.</p>
  <div class="ctl"><label for="bu-d1">أيام بالقدرة الكاملة</label><input id="bu-d1" type="range" data-bind="d" data-instant min="0" max="1400" step="10" value="400"><output data-show="d" data-fmt="0"></output></div>
</div>
<div class="step">
  <h3>البلوتونيوم ينضم</h3>
  <p>يلتقط اليورانيوم-238 نيوترونات فيصير بلوتونيوم-239، وهو ينشطر أيضًا. في أواخر العمر يحدث أكثر من نصف الانشطارات في البلوتونيوم؛ وعلى امتداد العمر كله يأتي منه نحو ثلث الطاقة.</p>
  <div class="ctl"><label for="bu-d2">أيام بالقدرة الكاملة</label><input id="bu-d2" type="range" data-bind="d" data-instant min="0" max="1400" step="10" value="1000"><output data-show="d" data-fmt="0"></output></div>
</div>
<div class="step">
  <h3>السموم تتراكم</h3>
  <p>كل انشطار يخلّف ناتجَي انشطار، وبعضها يمتص النيوترونات. ومع يورانيوم-235 أقل وسموم أكثر، تنحدر <i>k</i><sub>∞</sub> (الانشطارات الجديدة لكل انشطار في شبكة لا نهائية من هذا الوقود) حتى يعجز الوقود وحده عن إبقاء السلسلة مستمرة.</p>
  <div class="ctl"><label for="bu-d3">أيام بالقدرة الكاملة</label><input id="bu-d3" type="range" data-bind="d" data-instant min="0" max="1400" step="10" value="700"><output data-show="d" data-fmt="0"></output></div>
</div>
<div class="step">
  <h3>البورون وإعادة التحميل</h3>
  <p>يمزج القلب وقودًا جديدًا ومتوسط العمر وقديمًا. الوقود الجديد ذو تفاعلية زائدة، فيمتص البورون المذاب في ماء التبريد الفائض ويُخفَّف ببطء. وحين يبلغ الصفر يخرج الثلث الأقدم ويدخل وقود جديد.</p>
  <div class="ctl"><label for="bu-m">أشهر بالقدرة الكاملة</label><input id="bu-m" type="range" data-bind="m" data-instant min="0" max="54" step="0.5" value="8"><output data-show="m" data-fmt="1"></output></div>
</div>`,
};
Object.assign(WT.L.labels, {
  "illustrative model": "نموذج توضيحي",
  "{a} days · burnup {b} GWd/t": "{a} يوم · الاحتراق {b} GWd/t",
  "uranium{#}": "اليورانيوم{#}",
  "plutonium{#}": "البلوتونيوم{#}",
  "other Pu": "Pu آخر",
  "other plutonium": "بلوتونيوم آخر",
  "fission products": "نواتج الانشطار",
  "fission products (pairs)": "نواتج الانشطار (أزواج)",
  "{a} in {#}": "{a} من {#}",
  "uranium{#}: the remaining ~{#}–{#} %": "اليورانيوم{#}: الباقي ~{#}–{#} %",
  "plutonium's share": "حصة البلوتونيوم",
  "fissions": "الانشطارات",
  "fissions now": "الانشطارات الآن",
  "energy so far": "الطاقة حتى الآن",
  "U{#}": "U{#}",
  "Pu": "Pu",
  "split": "منشطرة",
  "plutonium": "البلوتونيوم",
  "each dot: {#} atom in {#}": "كل نقطة: {#} ذرة من {#}",
  "each dot: one atom in a thousand": "كل نقطة: ذرة واحدة من ألف",
  "k = {#}": "k = {#}",
  "GWd/t →": "GWd/t →",
  "burnup (GWd/t) →": "الاحتراق (GWd/t) →",
  "typical discharge": "التفريغ المعتاد",
  "typical discharge {#}–{#}": "التفريغ المعتاد {#}–{#}",
  "can't keep a chain going alone": "لا يُبقي السلسلة وحده",
  "this fuel alone can no longer keep a chain going": "هذا الوقود وحده لم يعد يُبقي السلسلة مستمرة",
  "k∞ reaches {#}": "k∞ تبلغ {#}",
  "k∞ = {a}": "k∞ = {a}",
  "fission products catch {a} % of neutrons": "نواتج الانشطار تلتقط {a} % من النيوترونات",
  "fresh": "جديد",
  "{#} cycle": "{#} دورة",
  "one cycle old": "عمره دورة واحدة",
  "{#} cycles": "{#} دورة",
  "two cycles old": "عمره دورتان",
  "reload": "إعادة تحميل",
  "boron (ppm)": "البورون (ppm)",
  "boron in the water (ppm)": "البورون في الماء (ppm)",
  "months →": "الأشهر →",
  "months at full power →": "أشهر بالقدرة الكاملة →",
  "{a} ppm": "{a} ppm",
  "cycle {a} months · fuel leaves at {b} GWd/t": "الدورة {a} أشهر · يخرج الوقود عند {b} GWd/t",
});
