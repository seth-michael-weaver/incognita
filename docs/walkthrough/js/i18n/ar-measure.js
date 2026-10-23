/* Arabic: measure (chapter 11) */
WT.L.ch.measure = {
  num: "الفصل 11", title: "ما يخرج إلينا", short: "الكميات المقيسة",
  lead: "التجربة أو المفاعل أو النجم لا يرى إلا حفنة من الأعداد. يبيّن هذا الفصل كيف يحوّل المحرك ما يجري داخل النواة إلى تلك الأعداد.",
  html: `
<div class="step">
  <p>القرص الباهت حول كل نواة هو <b>مقطعها العرضي</b>: المساحة التي يجب أن يصيبها النيوترون كي يحدث تفاعل، لا الحجم الحقيقي للنواة. تصل حزمة من اليسار وتعبر رقاقة رقيقة من الأنوية؛ والجزء الذي يتفاعل منها يساوي تلك المساحة مضروبة في عدد الأنوية التي يصادفها. ووحدتها البارن (10⁻²⁴ cm²، أي ما يقارب مساحة وجه نواة يورانيوم).</p>
  <div class="ctl"><label for="mea-e">طاقة النيوترون (MeV)</label><input id="mea-e" type="range" data-bind="E" min="0.1" max="20" step="0.1" value="2"><output data-show="E" data-fmt="1"></output></div>
  <p>اخفض الطاقة فتنتفخ الأقراص: فالنيوترون البطيء موجة عريضة ويتفاعل من مسافة أبعد. وعند الطاقة العالية ينكمش القرص نحو حجم النواة نفسها.</p>
</div>
<div class="step">
  <h3>مع الطاقة تنفتح مخارج جديدة</h3>
  <p>كل باب مخرجٌ، أو <b>قناة</b>: يرتد النيوترون إلى الخارج (مرن)، أو يترك الهدف مثارًا (n′)، أو يقتلع نيوترونات إضافية (2n، 3n)، أو يُؤسر فلا تخرج إلا فوتونات (γ)، أو يخرج بدلًا منه بروتون أو جسيم α. الباب المقفل له <b>عتبة</b>: يتطلب التفاعل طاقة أكبر مما يحمله النيوترون.</p>
  <div class="ctl"><label for="mea-e2">طاقة النيوترون (MeV)</label><input id="mea-e2" type="range" data-bind="E" min="0.1" max="20" step="0.1" value="2"><output data-show="E" data-fmt="1"></output></div>
  <p>اسحب الطاقة إلى ما بعد عتبةٍ ما فينفتح ذلك الباب مع ومضة؛ وتمتلئ الدلاء بحسب حصة كل قناة، وكل باب جديد يأخذ جزءًا من حصص الأبواب الأخرى. تأتي العتبات من كتل الأنوية؛ أما الحصص فمن التنافس الموصوف في الفصل 6.</p>
</div>
<div class="step">
  <h3>ما يراه الكاشف</h3>
  <p>الكومتان هما النيوترونات التي تصل إلى النصف الأمامي والنصف الخلفي من حلقة من الكواشف، مرتبةً حسب الطاقة. الحزمة نبضية، لذا يعطي زمن طيران كل نيوترون طاقتَه: السريعة تصل أولًا.</p>
  <div class="ctl"><label for="mea-ein">الطاقة الساقطة (MeV)</label><input id="mea-ein" type="range" data-bind="Ein" min="5" max="60" step="0.5" value="30"><output data-show="Ein" data-fmt="0"></output></div>
  <p>في الكومتين سنام من النيوترونات البطيئة <b>المتبخرة</b>: تنفصل عن النواة المركبة بعد أن تتوزع الطاقة، بالتساوي في كل الاتجاهات. أما الكومة الأمامية وحدها فلها ذيل سريع طويل: نيوترونات <b>ما قبل التوازن</b>، التي تخرج من التصادمات الأولى وما زالت تتحرك تقريبًا مع الحزمة. ارفع الطاقة الساقطة فيكبر الذيل.</p>
</div>
<div class="step">
  <h3>إلى أين تذهب</h3>
  <p>تبيّن البتلة عدد النيوترونات الخارجة في كل اتجاه؛ والحزمة تصل من اليسار. النيوترونات المتبخرة نسيت الحزمة وتخرج بالتساوي في كل الاتجاهات؛ أما السريعة القادمة من ما قبل التوازن فتميل إلى الأمام. تحدد قاعدة كالباخ مقدار هذا الميل، بميل واحد <i>a</i> يزداد مع طاقة الخروج. ويستطيع المحرك أيضًا كتابة هذه التوزيعات الزاوية كمُخرَج اختياري.</p>
  <div class="ctl"><label for="mea-eo">طاقة الخروج (MeV)</label><input id="mea-eo" type="range" data-bind="Eout" min="1" max="45" step="0.5" value="25"><output data-show="Eout" data-fmt="1"></output></div>
  <p>اخفض طاقة الخروج فتستدير البتلة: فالنيوترونات البطيئة في معظمها متبخرة.</p>
  <div class="formula">dσ/dΩ ∝ e<sup>a cos θ</sup></div>
</div>
<div class="step">
  <h3>في نجم</h3>
  <p>تجمع الكومة السفلية طاقات النيوترونات المأسورة في الغاز الساخن لنجم. تتبع سرعاتها توزيع ماكسويل الذي تحدده درجة الحرارة <i>kT</i> (30 keV تعادل نحو 350 مليون درجة)؛ والآثار الأطول نيوترونات أسرع، وكل مرور قرب نواة قد ينتهي بومضة أسر.</p>
  <div class="ctl"><label for="mea-kt">درجة الحرارة kT (keV)</label><input id="mea-kt" type="range" data-bind="kT" min="5" max="100" step="1" value="30"><output data-show="kT" data-fmt="0"></output></div>
  <p>النيوترونات البطيئة تُؤسر بسهولة لكنها نادرًا ما تمر، والسريعة قليلة، لذا تأتي معظم حالات الأسر من نافذة عرضها بضع <i>kT</i>. والمعدل على الغاز كله هو <b>المقطع العرضي المتوسط على توزيع ماكسويل</b> (MACS)، بالمليبارن (mb). سخّن الغاز فتنزاح النافذة نحو طاقات أعلى، حيث يكون الهدف أصغر. وتُحسب MACS بتكامل منحنى الأسر الذي يعطيه المحرك.</p>
</div>
<div class="step">
  <h3>الهدف ساخن أيضًا</h3>
  <p>تبيّن الكرات أي جزء من أنوية الهدف يوجد في كل مستوى من مستوياته الدنيا عند هذه الدرجة. في النجم تكون بعض الأهداف مثارة مسبقًا، وكل مستوى مثار مدخلٌ مختلف إلى النواة المركبة نفسها. والمستوى ذو السبين <i>J</i> يستوعب أكثر لأن له 2<i>J</i>+1 اتجاهًا.</p>
  <div class="ctl"><label for="mea-kt2">درجة الحرارة kT (keV)</label><input id="mea-kt2" type="range" data-bind="kT" min="5" max="100" step="1" value="30"><output data-show="kT" data-fmt="0"></output></div>
  <p>ارفع درجة الحرارة وراقب الأنوية وهي تصعد. يحسب المعدل النجمي الأسر من كل مستوى مأهول ويجمع النتائج بهذه الحصص؛ ومجموع الأوزان هو دالة التجزئة <i>G</i>، ونسبة الناتج إلى المعدل من الحالة الأرضية هي <b>معامل التعزيز النجمي</b>. يستطيع المحرك فعل ذلك كخيار معطّل افتراضيًا؛ وفي العادة ينطلق كل هدف من حالته الأرضية.</p>
</div>
<div class="step">
  <h3>ما مدى اليقين في كل هذا؟</h3>
  <p>كل قرص باهت تشغيلٌ للمحرك بعد تحريك مدخلاته عشوائيًا: عمق البئر البصرية، وكثافة المستويات، والشدة الفوتونية، وكلٌّ منها معروف بهامش لا يتجاوز بضعة في المئة. والتشتت عبر تشغيلات كثيرة هو عدم يقين صادق: <b>مونت كارلو الشامل</b>.</p>
  <div class="btns"><button class="btn" data-act="tmc1">شغّل نسخة واحدة</button><button class="btn ghost" data-act="tmc">شغّل 10</button><button class="btn ghost" data-act="clear">امسح</button></div>
  <p>الحافة الحادة تعني أن المدخلات تحدد الجواب؛ والحافة الضبابية تعني أنها لا تحدده، وهناك تحديدًا تفيد القياسات الجديدة أكثر من غيرها.</p>
  <div class="aside">في الشيفرة: <code>emission/channels.py</code> (القنوات الحصرية والنوى المتبقية)، <code>specout.py</code> و<code>specang.py</code> (أطياف الخروج، والتوزيعات الزاوية، والمقاطع العرضية التفاضلية المزدوجة، ولا تُكتب إلا عند طلبها)، <code>astro/stellar.py</code> (الأسر من مستويات الهدف المأهولة حراريًا، اختياري)، <code>tmc.py</code> (أداة اعتيان مونت كارلو الشامل). وتُستخرج قيم MACS للحالة الأرضية من منحنيات الأسر في <code>validation/differential/core.py</code>.</div>
</div>`,
};
Object.assign(WT.L.labels, {
  // area
  "each disc: σ ≈ {#} b": "كل قرص: σ ≈ {#} b",
  "each disc: cross section σ ≈ {#} b, the area a neutron must hit": "كل قرص: المقطع العرضي σ ≈ {#} b، المساحة التي يجب إصابتها",
  "beam →": "الحزمة →",
  "nucleus's own face ≈ {#} b · {#} % reacts": "وجه النواة ≈ {#} b · يتفاعل {#} %",
  "the nucleus's own face ≈ {#} b · {#} % of the beam reacts in this foil": "وجه النواة نفسها ≈ {#} b · يتفاعل {#} % من الحزمة في هذه الرقاقة",
  "slow: the neutron's wave reaches well past the surface": "بطيء: موجة النيوترون تمتد إلى ما بعد السطح بكثير",
  "the target still looks bigger than the nucleus": "ما زال الهدف يبدو أكبر من النواة",
  "fast: close to the nucleus's own size": "سريع: قريب من حجم النواة نفسها",
  // doors
  "elastic": "مرن", "n′ inelastic": "n′ غير مرن", "{#}n": "{#}n", "γ capture": "أسر γ", "p": "p", "α": "α", "n′": "n′",
  "{#}n · {#} MeV": "{#}n · {#} MeV", "p · {#} MeV": "p · {#} MeV", "α · {#} MeV": "α · {#} MeV", "n′ inelastic · {#} MeV": "n′ غير مرن · {#} MeV",
  "opens at {#} MeV": "ينفتح عند {#} MeV",
  "{#} MeV": "{#} MeV",
  // detect
  "forward half": "النصف الأمامي", "backward half": "النصف الخلفي",
  "pulsed beam": "حزمة نبضية", "pulsed beam →": "حزمة نبضية →",
  "backward": "للخلف", "backward detectors": "الكواشف الخلفية",
  "forward": "للأمام", "forward detectors": "الكواشف الأمامية",
  "outgoing neutron energy from the flight time (MeV) →": "طاقة النيوترون الخارج من زمن الطيران (MeV) →",
  "fast tail": "ذيل سريع", "fast tail: pre-equilibrium": "ذيل سريع: ما قبل التوازن",
  "evaporated hump": "سنام التبخر", "hump: evaporated, every way alike": "السنام: متبخرة، بالتساوي في كل اتجاه",
  "{#} % leave before the energy is shared": "{#} % تخرج قبل توزّع الطاقة",
  // angle
  "beam": "الحزمة",
  "forward-to-backward ratio ≈ {#}  ·  slope a ≈ {#}": "نسبة الأمام إلى الخلف ≈ {#}  ·  الميل a ≈ {#}",
  "mostly evaporated: every direction alike": "معظمها متبخرة: كل الاتجاهات سواء",
  "a mix: the fast share leans forward": "مزيج: الحصة السريعة تميل للأمام",
  "mostly pre-equilibrium: strongly forward": "معظمها ما قبل التوازن: للأمام بقوة",
  "forward →": "للأمام →",
  // star
  "{#} keV": "{#} keV",
  "kT = {#} keV": "kT = {#} keV",
  "energies of captured neutrons": "طاقات النيوترونات المأسورة",
  "each capture drops here, by the neutron's energy: the window that counts": "كل أسر يسقط هنا حسب طاقة النيوترون: النافذة المهمة",
  "MACS ≈ {#} mb at kT = {#} keV · captures watched: {#}": "MACS ≈ {#} mb عند kT = {#} keV · حالات الأسر المرصودة: {#}",
  // hot target
  "{#}⁺  ground state": "{#}⁺  الحالة الأرضية", "{#}⁺  {#} keV": "{#}⁺  {#} keV",
  "target levels, with the share of nuclei sitting on each": "مستويات الهدف، مع حصة الأنوية في كل منها",
  "{#} % start from the ground state · partition function G ≈ {#}": "{#} % تنطلق من الحالة الأرضية · دالة التجزئة G ≈ {#}",
  // TMC
  "optical well": "البئر البصرية", "optical well depth": "عمق البئر البصرية",
  "level density": "كثافة المستويات", "photon strength": "الشدة الفوتونية",
  "σ ≈ {#} b ": "σ ≈ {#} b ", "σ ≈ {#} mb ": "σ ≈ {#} mb ",
  "σ ≈ {#} b ±{#} %": "σ ≈ {#} b ±{#} %", "σ ≈ {#} mb ±{#} %": "σ ≈ {#} mb ±{#} %",
  "dashed: best inputs · each disc drawn at its own scale": "المتقطع: أفضل المدخلات · كل قرص بمقياسه",
  "dashed ring: the best-value inputs · each energy drawn at its own scale (disc area ∝ σ)": "الحلقة المتقطعة: أفضل قيم المدخلات · كل طاقة بمقياسها (المساحة ∝ σ)",
  "{#} runs of the engine, each with its inputs nudged at random": "{#} تشغيلًا للمحرك، لكلٍّ منها مدخلات محرّكة عشوائيًا",
});
