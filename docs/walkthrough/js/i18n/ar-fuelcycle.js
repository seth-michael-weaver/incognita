/* Arabic: fuelcycle (دورة الوقود) */
WT.L.ch.fuelcycle = {
  num: "الدرس 1", title: "دورة الوقود", short: "دورة الوقود",
  html: `
<div class="step">
  <h3>استخراج اليورانيوم</h3>
  <p>الخام في معظمه صخر، ولا يشكّل اليورانيوم-235، النوع الذي ينشطر بسهولة، سوى 0.7 % من اليورانيوم فيه.</p>
  <div class="ctl"><label for="fc-g">رتبة الخام (% يورانيوم)</label><input id="fc-g" type="range" data-bind="lg" data-instant min="-1.7" max="1.3" step="0.01" value="-1"></div>
</div>
<div class="step">
  <h3>التخصيب موازنة كتلة</h3>
  <p>يُقسَم اليورانيوم وهو في صورة غاز إلى تيار صغير أغنى باليورانيوم-235، هو الوقود، وتيار كبير مستنفَد، هو المخلّفات.</p>
  <div class="ctl"><label for="fc-p">تخصيب الوقود (% U-235)</label><input id="fc-p" type="range" data-bind="xp" data-instant min="3" max="5" step="0.05" value="4.5"><output data-show="xp" data-fmt="2"></output></div>
  <div class="ctl"><label for="fc-t">المخلّفات (% U-235)</label><input id="fc-t" type="range" data-bind="xt" data-instant min="0.15" max="0.35" step="0.01" value="0.25"><output data-show="xt" data-fmt="2"></output></div>
</div>
<div class="step">
  <h3>أقراص وقضبان وحزم</h3>
  <p>يُخبَز اليورانيوم المخصَّب في أقراص خزفية، ويُختم في قضبان، ويُجمع في حزم؛ و<a href="#reactor">الدرس التالي</a> يتبعها إلى القلب.</p>
  <div class="ctl"><label for="fc-f">الوقود (أطنان يورانيوم)</label><input id="fc-f" type="range" data-bind="ft" data-instant min="1" max="27" step="1" value="1"><output data-show="ft" data-fmt="0"></output></div>
</div>
<div class="step">
  <h3>سنوات في القلب</h3>
  <p>على مدى ثلاث إلى ست سنوات تنشطر نسبة مئوية قليلة من الذرات الثقيلة، تاركة نواتج انشطار وقليلًا من البلوتونيوم الجديد (<a href="#burnup">الاحتراق</a>).</p>
  <div class="ctl"><label for="fc-b">الاحتراق (GWd لكل طن)</label><input id="fc-b" type="range" data-bind="bu" data-instant min="0" max="60" step="1" value="50"><output data-show="bu" data-fmt="0"></output></div>
</div>
<div class="step">
  <h3>التبريد ثم طريقان</h3>
  <p>يبرد الوقود المستهلك في حوض ثم في حاويات جافة؛ وبعدها إمّا يُدفن عميقًا كما هو، أو يُعاد معالجته ليُستخدم يورانيومه وبلوتونيومه من جديد (<a href="#waste">الوقود المستهلك</a>، <a href="#breeding">التوليد</a>).</p>
  <div class="btns"><button class="btn ghost" data-act="frO" aria-pressed="true">دورة مفتوحة</button> <button class="btn ghost" data-act="frR" aria-pressed="false">إعادة المعالجة</button></div>
</div>`,
};
Object.assign(WT.L.labels, {
  "Convert": "التحويل",
  "Disposal": "التخلّص",
  "End": "النهاية",
  "Enrich": "التخصيب",
  "Fabricate": "التصنيع",
  "Mill": "الطحن",
  "Mine": "التعدين",
  "Pool · cask": "الحوض · الحاوية",
  "Reactor": "المفاعل",
  "Store": "التخزين",
  "about what a {#} MWe reactor loads in a year": "نحو ما يُحمِّله مفاعل {#} MWe في سنة",
  "assemblies": "الحزم",
  "assemblies of {#} rods": "حزم من {#} قضيبًا",
  "at least {#} years": "{#} سنوات على الأقل",
  "cask": "حاوية",
  "decades": "عقود",
  "decades in air": "عقود في الهواء",
  "deep repository, {#}–{#} m down": "مستودع عميق، على عمق {#}–{#} m",
  "dry cask": "حاوية جافة",
  "enrich": "تخصيب",
  "enrichment plant (UF₆ gas)": "محطة التخصيب (غاز UF₆)",
  "fission products": "نواتج الانشطار",
  "illustration": "توضيح",
  "minor actinides": "الأكتينيدات الثانوية",
  "most mines: above {#} %": "معظم المناجم: فوق {#} %",
  "of electricity from this tonne": "من الكهرباء من هذا الطن",
  "once-through: the whole tonne is disposed of": "دورة مفتوحة: يُتخلَّص من الطن كله",
  "one tonne of fuel: each square is {#} kg": "طن من الوقود: كل مربع {#} kg",
  "one tonne: each square {#} kg": "طن: كل مربع {#} kg",
  "pellets": "أقراص",
  "pellets, {#} cm tall": "أقراص بارتفاع {#} cm",
  "plutonium": "البلوتونيوم",
  "pool": "حوض",
  "recycle": "إعادة التدوير",
  "repository": "مستودع",
  "repository {#}–{#} m deep": "مستودع بعمق {#}–{#} m",
  "reprocess": "إعادة المعالجة",
  "richest, Canada: up to {#} %": "الأغنى، كندا: حتى {#} %",
  "rods, about {#} m long": "قضبان بطول نحو {#} m",
  "rods, {#} m": "قضبان، {#} m",
  "the rest: uranium{#}": "الباقي: اليورانيوم{#}",
  "the whole tonne": "الطن كله",
  "typical discharge {#}–{#}": "التفريغ المعتاد {#}–{#}",
  "uranium{#}": "اليورانيوم{#}",
  "uranium{#} (and {#})": "اليورانيوم{#} (و{#})",
  "{#} U atoms": "{#} ذرة U",
  "{#} are U{#}": "{#} منها U{#}",
  "{#} are uranium{#}": "{#} منها يورانيوم{#}",
  "{#} t used": "{#} t مستهلك",
  "{#} t used fuel": "{#} t وقود مستهلك",
  "{#} uranium atoms": "{#} ذرة يورانيوم",
  "≈ a big reactor's yearly reload": "≈ إعادة التحميل السنوية لمفاعل كبير",
  "≥ {#} years": "≥ {#} سنوات",
  "{a} t ore": "{a} t خام",
  "{a} t U₃O₈": "{a} t U₃O₈",
  "{a} t UF₆": "{a} t UF₆",
  "{#} t fuel + {a} t tails": "{#} t وقود + {a} t مخلّفات",
  "{a} t UO₂": "{a} t UO₂",
  "pool ≥ {#} years": "حوض ≥ {#} سنوات",
  "ore ≈ {a} t · block = {#} t": "خام ≈ {a} t · الكتلة = {#} t",
  "ore for one tonne of fuel: ≈ {a} t  (each block {#} t)": "الخام لطن واحد من الوقود: ≈ {a} t  (كل كتلة {#} t)",
  "{a} of one block": "{a} من كتلة واحدة",
  "{a} % U": "{a} % U",
  "grade {a} % U": "الرتبة {a} % U",
  "natural U {a} kg": "U طبيعي {a} kg",
  "natural uranium {a} kg": "يورانيوم طبيعي {a} kg",
  "{a} % U{#}": "{a} % U{#}",
  "fuel {#} kg": "وقود {#} kg",
  "tails {a} kg": "مخلّفات {a} kg",
  "feed/fuel = (xp − xt)/(xf − xt) = {a}": "التغذية/الوقود = (xp − xt)/(xf − xt) = {a}",
  "natural / fuel = (xp − xt) / (xf − xt) = ({a} − {b}) / ({c} − {b}) = {d}": "طبيعي / وقود = (xp − xt) / (xf − xt) = ({a} − {b}) / ({c} − {b}) = {d}",
  "≈ {a} SWU of separative work per kg of fuel": "≈ {a} SWU من عمل الفصل لكل kg وقود",
  "separative work ≈ {a} SWU per kg of fuel · lower tails: less uranium, more work": "عمل الفصل ≈ {a} SWU لكل kg وقود · مخلّفات أفقر: يورانيوم أقل، عمل أكثر",
  "{a} t uranium = {b} t UO₂": "{a} t يورانيوم = {b} t UO₂",
  "{a} t of enriched uranium, as {b} t of uranium dioxide (UO₂) ceramic": "{a} t من اليورانيوم المخصَّب، في صورة {b} t من خزف ثاني أكسيد اليورانيوم (UO₂)",
  "{a} % of the heavy atoms split": "انشطر {a} % من الذرات الثقيلة",
  "{a} GWd/t": "{a} GWd/t",
  "≈ {a} GWh of electricity": "≈ {a} GWh من الكهرباء",
  "reprocessing": "إعادة المعالجة",
  "uranium {a} t": "يورانيوم {a} t",
  "plutonium {a} kg": "بلوتونيوم {a} kg",
  "→ ≈ {a} t MOX fuel": "→ ≈ {a} t وقود MOX",
  "fission products + minor actinides {a} kg → ≈ {#} t glass": "نواتج الانشطار + الأكتينيدات الثانوية {a} kg → ≈ {#} t زجاج",
  "U {a} t → re-enrich": "U {a} t → إعادة تخصيب",
  "Pu {a} kg → MOX": "Pu {a} kg → MOX",
  "{a} kg waste → glass": "{a} kg نفايات → زجاج",
  "fission prod.": "نواتج الانشطار",
  "minor act.": "أكتينيدات ثانوية",
});
