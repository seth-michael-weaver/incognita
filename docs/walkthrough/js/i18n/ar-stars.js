/* Arabic: stars (من أين تأتي العناصر) */
WT.L.ch.stars = {
  num: "الدرس 1", title: "من أين تأتي العناصر", short: "النجوم",
  html: `
<div class="step">
  <h3>الاندماج يتوقف عند الحديد</h3>
  <p>تدمج النجوم النوى الخفيفة حتى الحديد؛ وكل ما هو أثقل تقريبًا يُبنى بإضافة النيوترونات.</p>
</div>
<div class="step">
  <h3>المسار البطيء</h3>
  <p>في النجوم العملاقة تصل النيوترونات نادرًا، فتضمحل النواة غير المستقرة بيتا أولًا: يتعرّج المسار على طول النوى المستقرة.</p>
  <div class="ctl"><label for="st-k">عمليات أسر النيوترونات</label><input id="st-k" type="range" data-bind="k" min="0" max="213" step="1" value="112"></div>
</div>
<div class="step">
  <h3>المسار السريع</h3>
  <p>في اندماج نجمين نيوترونيين تتدفق النيوترونات أسرع مما تستطيع النوى أن تضمحل؛ وبعدها تضمحل النوى الغنية بالنيوترونات عائدة إلى الاستقرار.</p>
  <div class="ctl"><label for="st-rt">الاضمحلال عودةً</label><input id="st-rt" type="range" data-bind="rt" min="0" max="1" step="0.01" value="0"></div>
</div>
<div class="step">
  <h3>الأعداد السحرية تصنع القمم</h3>
  <p>النوى ذات 50 أو 82 أو 126 نيوترونًا بالكاد تأسر، فتتراكم المادة هناك: قمم s عند السترونشيوم والباريوم والرصاص، وقمم r أخف قليلًا.</p>
  <div class="btns"><button class="btn ghost" data-act="stS" aria-pressed="true">قمم العملية s</button> <button class="btn ghost" data-act="stR" aria-pressed="true">قمم العملية r</button></div>
</div>
<div class="step">
  <h3>نادر حيث الأسر سهل</h3>
  <p>للنظائر التي لا تصنعها إلا العملية s، يبقى حاصل ضرب الوفرة Nₛ في المقطع العرضي للأسر σ شبه ثابت بين الأعداد السحرية. وσ هنا هي القيمة التي حسبها INCOGNITA عند 30 keV.</p>
  <div class="btns"><button class="btn ghost" data-act="stvs" aria-pressed="false">σ</button> <button class="btn ghost" data-act="stvn" aria-pressed="false">Nₛ</button> <button class="btn ghost" data-act="stvsn" aria-pressed="true">σ × Nₛ</button></div>
</div>
<div class="step">
  <h3>مقارنة بالقياسات</h3>
  <p>قيم INCOGNITA عند 30 keV مقسومة على القيم المقيسة، لـ 94 نويدة مستقرة (<a href="scoreboard.html">المقارنات</a>).</p>
</div>`,
};
Object.assign(WT.L.labels, {
  "A ≈ {#}": "A ≈ {#}",
  "Ba": "Ba",
  "Ba{#}": "Ba{#}",
  "Big Bang": "الانفجار العظيم",
  "Fe": "Fe",
  "H": "H",
  "He": "He",
  "INCOGNITA ÷ measured, {#} keV": "INCOGNITA ÷ المقيس، {#} keV",
  "INCOGNITA's {#} keV capture rate (MACS) ÷ measured": "معدل أسر INCOGNITA عند {#} keV (MACS) ÷ المقيس",
  "INCOGNITA: capture at {#} keV (MACS)": "INCOGNITA: الأسر عند {#} keV (MACS)",
  "Lodders et al. {#}": "Lodders et al. {#}",
  "Lu{#}": "Lu{#}",
  "N = {#}": "N = {#}",
  "O": "O",
  "Pb": "Pb",
  "Pb{#}": "Pb{#}",
  "Sm{#}": "Sm{#}",
  "Sn": "Sn",
  "Sr": "Sr",
  "Sr{#}": "Sr{#}",
  "abundances: Lodders, Palme & Gail {#}": "الوفرة: Lodders, Palme & Gail {#}",
  "abundances: Lodders, Palme & Gail {#} · point at the curve": "الوفرة: Lodders, Palme & Gail {#} · أشِر إلى المنحنى",
  "atoms per million silicon atoms (Solar System)": "ذرات لكل مليون ذرة سيليكون (المجموعة الشمسية)",
  "atoms per {#}⁶ silicon": "ذرات لكل {#}⁶ سيليكون",
  "beta decay (n → p)": "اضمحلال بيتا (n → p)",
  "flat between magic numbers, steps down at each": "مسطّح بين الأعداد السحرية، ينخفض درجة عند كلٍّ منها",
  "fusion": "اندماج",
  "fusion in stars": "الاندماج في النجوم",
  "made by neutron capture": "صُنع بأسر النيوترونات",
  "magic N: captures poorly, matter piles up": "N سحري: أسر ضعيف، تتراكم المادة",
  "magic neutron number: it captures poorly, so matter piles up here": "عدد نيوترونات سحري: أسره ضعيف، فتتراكم المادة هنا",
  "mass number A": "العدد الكتلي A",
  "mass number A (protons + neutrons)": "العدد الكتلي A (بروتونات + نيوترونات)",
  "mb": "mb",
  "nearly flat between magic numbers, a step down at each": "شبه مسطّح بين الأعداد السحرية، ودرجة نزول عند كلٍّ منها",
  "neutron capture": "أسر النيوترونات",
  "neutrons N →": "النيوترونات N →",
  "peaks: sources Lodders et al. {#}": "القمم: المصادر Lodders et al. {#}",
  "plus a weaker s-process (massive stars)": "إضافة إلى عملية s أضعف (النجوم الضخمة)",
  "r {#}": "r {#}",
  "r-path: illustration": "مسار r: توضيح",
  "r-peak Pt": "قمة r: Pt",
  "r-peak Se, Kr": "قمة r: Se، Kr",
  "r-peak Te, Xe": "قمة r: Te، Xe",
  "r-process: a flood of neutrons makes very neutron-rich nuclei": "العملية r: سيل من النيوترونات يصنع نوى غنية جدًا بالنيوترونات",
  "r-process: very neutron-rich nuclei": "العملية r: نوى غنية جدًا بالنيوترونات",
  "ringed: s-only isotopes · measured: compiled values (KADoNiS) · a development comparison, not an independent test": "المطوَّقة: نظائر s فقط · المقيس: قيم مجمَّعة (KADoNiS) · مقارنة أثناء التطوير، لا اختبار مستقل",
  "ringed: s-only · measured: KADoNiS": "المطوَّقة: s فقط · المقيس: KADoNiS",
  "s Ba": "s Ba",
  "s Pb": "s Pb",
  "s Sr": "s Sr",
  "s-only isotopes · bars: INCOGNITA {#} %": "نظائر s فقط · الأشرطة: INCOGNITA {#} %",
  "s-only isotopes · σ: INCOGNITA (bars: its {#} % range; open circle: scaled to a measurement) · Nₛ: Lodders et al. {#}": "نظائر s فقط · σ: INCOGNITA (الأشرطة: نطاقه {#} %؛ الدائرة المفرغة: معايَرة على قياس) · Nₛ: Lodders et al. {#}",
  "s-peak Ba": "قمة s: Ba",
  "s-peak Pb": "قمة s: Pb",
  "s-peak Sr": "قمة s: Sr",
  "seen in {#}: merger GW{#}": "رُصد في {#}: الاندماج GW{#}",
  "seen in {#}: the neutron-star merger GW{#} and its kilonova": "رُصد في {#}: اندماج النجمين النيوترونيين GW{#} ومستعره الكيلوي",
  "wait": "انتظار",
  "waiting point": "نقطة انتظار",
  "weak s-process too": "وعملية s ضعيفة أيضًا",
  "σ × Nₛ (mb × atoms per million Si)": "σ × Nₛ (mb × ذرات لكل مليون Si)",
  "σ × Nₛ (mb × atoms per {#}⁶ Si)": "σ × Nₛ (mb × ذرات لكل {#}⁶ Si)",
  "↑ protons Z": "↑ البروتونات Z",
  "A = {a}: mostly {b}, {c} atoms per million silicon": "A = {a}: غالبًا {b}، {c} ذرة لكل مليون سيليكون",
  "decayed back: r-made stable isotopes": "اضمحلت عائدة: نظائر مستقرة من صنع r",
  "decayed back: each lands on the most neutron-rich stable isobar": "اضمحلت عائدة: كلٌّ يستقر على أغنى متساوي الكتلة المستقر بالنيوترونات",
  "beta decays, A fixed": "اضمحلالات بيتا، A ثابت",
  "beta decays carry them back, mass number A fixed": "اضمحلالات بيتا تعيدها، والعدد الكتلي A ثابت",
  "{a} · N = {b} · σ = {c} mb": "{a} · N = {b} · σ = {c} mb",
  "{a} · N = {b} · INCOGNITA: σ = {c} mb at {#} keV": "{a} · N = {b} · INCOGNITA: σ = {c} mb عند {#} keV",
  "{a} · unstable: beta decay": "{a} · غير مستقر: اضمحلال بيتا",
  "{a} · unstable: it beta-decays before the next neutron": "{a} · غير مستقر: يضمحل بيتا قبل النيوترون التالي",
  "end: the lead–bismuth cycle": "النهاية: دورة الرصاص–البزموت",
  "end of the road: Bi{#} → Po{#} → alpha decay back to Pb{#}": "نهاية الطريق: Bi{#} → Po{#} → اضمحلال ألفا عودةً إلى Pb{#}",
  "drag along the path": "اسحب على المسار",
  "drag along the path, or use the slider": "اسحب على المسار، أو استخدم المنزلقة",
  "{a}: INCOGNITA σ = {b} mb": "{a}: INCOGNITA σ = {b} mb",
  "{a}: σ = {b} mb × Nₛ = {c} → σNₛ = {d}": "{a}: σ = {b} mb × Nₛ = {c} → σNₛ = {d}",
  " (σ scaled to a measured value)": " (σ معايَرة على قيمة مقيسة)",
  "σ alone: scattered": "σ وحدها: مبعثرة",
  "σ alone jumps around from isotope to isotope": "σ وحدها تقفز من نظير إلى آخر",
  "Nₛ alone: scattered": "Nₛ وحدها: مبعثرة",
  "Nₛ alone jumps around the other way": "Nₛ وحدها تقفز في الاتجاه المعاكس",
  "{a}: INCOGNITA's engine {b} (the library then scales to it)": "{a}: محرّك INCOGNITA {b} (ثم تُعايَر المكتبة على القياس)",
  "{a}: INCOGNITA σ = {b} mb, {c}": "{a}: INCOGNITA σ = {b} mb، {c}",
  "{a} nuclides · typical difference {b} %": "{a} نويدة · الفرق النموذجي {b} %",
  "{a} stable nuclides · typical difference {b} % (median), rms {c} %": "{a} نويدة مستقرة · الفرق النموذجي {b} % (الوسيط)، rms {c} %",
  "{a} % above measured": "أعلى من المقيس بـ {a} %",
  "{a} % below measured": "أدنى من المقيس بـ {a} %",
});
