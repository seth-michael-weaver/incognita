/* Arabic: slowing (الفصل 19، إبطاء النيوترونات) */ // [i18n check parity with English JS helper: data-act="${act}"]
WT.L.ch.slowing = {
  num: "الفصل 19", title: "إبطاء النيوترونات", short: "الإبطاء",
  html: `
<div class="step">
  <p>كل ارتداد عن الهيدروجين يكلّف نحو نصف الطاقة. يبدأ نيوترون الانشطار بطاقة 2 MeV ويرتدّ عبر الماء. نواة الهيدروجين تزن مثل النيوترون، فكما في كرات البلياردو، يمنحها كل ارتداد في المتوسط نصف طاقة النيوترون.</p>
  <p>يرسم المخطط طاقة النيوترون بعد كل ارتداد؛ وكل تسمية على الجانب تعني طاقة أقل بألف مرة. وفقدان النسبة نفسها في كل مرة يصنع انزلاقًا مستقيمًا، هو الخط المتقطع. بعد نحو 18 ارتدادًا يبلغ النيوترون الطاقة <b>الحرارية</b>، 0.025 eV، حيث يدفعه الماء الدافئ إلى أعلى بقدر ما يبطئه. الأكسجين أثقل بـ16 مرة: كل ارتداد يأخذ منه القليل، ويحتاج إلى أكثر من مئة ارتداد.</p>
  <div class="btns"><button class="btn ghost" data-act="tgtH" aria-pressed="true">الهيدروجين</button><button class="btn ghost" data-act="tgtO" aria-pressed="false">الأكسجين</button><button class="btn" data-act="again">أطلِق مجددًا</button></div>
</div>
<div class="step">
  <p>تحت نحو 1 eV تصوغ الروابط في الجزيء كل ارتداد. فكل ذرة هيدروجين مرتبطة بذرة الأكسجين (الخطوط الساطعة). لم يعد النيوترون البطيء يصطدم بهيدروجين حر: إنه يصطدم بجزيء كامل أثقل بـ18 مرة، فلا يأخذ الارتداد البسيط منه إلا القليل جدًا.</p>
  <p>ويمكنه أيضًا أن يجعل الجزيء يتأرجح أو يهتز، لكن فقط بتسليمه مقدارًا ثابتًا من الطاقة في كل مرة: 0.06 أو 0.2 أو 0.45 eV (الومضات الساطعة). والجزيئات الدافئة تعيد أحيانًا مقدارًا كهذا. وعلى المخطط، النطاق المظلل تحت 1 eV هو الموضع الذي يهمّ فيه ذلك. أوقف الارتباط للمقارنة مع الهيدروجين الحر.</p>
  <div class="btns"><button class="btn ghost" data-act="bind" aria-pressed="true">الارتباط الكيميائي</button><button class="btn" data-act="again">أطلِق مجددًا</button></div>
</div>
<div class="step">
  <p>تحتاج شيفرة الحاسوب إلى كل هذا في جدول: <b>قانون التشتت</b>، أي الخريطة. على المحور الأفقي: شدة الطرقة، α (الدفعة المسلَّمة للجزيء؛ صغيرة للمسّ العابر، كبيرة للضربة المباشرة). وعلى المحور الرأسي: الطاقة التي يكسبها النيوترون (إلى أعلى) أو يفقدها (إلى أسفل)، β، مقيسة بوحدات الطاقة الحرارية للماء، 0.025 eV. اللون الساطع يعني احتمالًا كبيرًا، والباهت يعني ندرة.</p>
  <p>الحد المرسوم هو ما يمكن أن يبلغه نيوترون بالطاقة المختارة: فلا يستطيع أن يفقد أكثر مما يملك، وكل تغير في الطاقة يسمح بمدى محدود من الطرقات فقط. حرّك الطاقة فيكبر الحد أو يصغر. بلا ارتباط تكون الخريطة غاز هيدروجين حرًا، وهي حافة ساطعة واحدة على امتداد خط الارتداد المتقطع؛ ومع الارتباط يضيف الجزيء أشرطة ساطعة هي مقاديره الثابتة من الطاقة. يحسب INCOGNITA قوانينه الخاصة للماء والبريليوم: <a href="https://github.com/seth-michael-weaver/incognita/tree/main/library/tsl-v0.1" style="white-space:nowrap">tsl-v0.1</a>.</p>
  <div class="ctl"><label for="slo-e">طاقة النيوترون (eV)</label><input id="slo-e" type="range" data-bind="lgE" data-instant min="-2.3" max="0" step="0.01" value="-1"><output data-show="Eshow" data-fmt="3"></output></div>
  <div class="btns"><button class="btn ghost" data-act="bind" aria-pressed="true">الارتباط الكيميائي</button></div>
</div>`
};
Object.assign(WT.L.labels, {
  "water · neutron hits hydrogen": "ماء · نيوترون يصطدم بالهيدروجين",
  "thermal · kT ≈ {#} eV": "حراري · kT ≈ {#} eV",
  "{#} meV": "{#} meV",
  "collisions →": "التصادمات →",
  "energy": "الطاقة",
  "typical bounce: energy × {#} (theory × {#}) · {#} bounces to thermal": "الارتداد النموذجي: الطاقة × {#} (النظرية × {#}) · {#} ارتدادًا حتى الحرارية",
  "typical: the average step along the dashed line (energy shares multiply, so the average is taken on this scale)": "النموذجي: متوسط الخطوة على الخط المتقطع (حصص الطاقة تتضاعف ضربًا، فيؤخذ المتوسط على هذا المقياس)",
  "bright line: a bond holding H to its O": "خط ساطع: رابطة تشد H إلى O",
  "bright flash: the neutron left a fixed amount of energy in the molecule": "ومضة ساطعة: ترك النيوترون مقدارًا ثابتًا من الطاقة في الجزيء",
  "below {#} eV: the bonds shape each bounce": "تحت {#} eV: الروابط تصوغ كل ارتداد",
  "free-atom recoil": "ارتداد ذرة حرة",
  "α: how hard the knock (momentum handed over) →": "α: شدة الطرقة (الزخم المنقول) →",
  "β: the neutron's energy change, in units of kT = {#} eV": "β: تغير طاقة النيوترون بوحدات kT = {#} eV",
  "gain ↑": "كسب ↑",
  "loss ↓": "فقدان ↓",
  "outline: reachable from {#} eV": "الحد: ما يمكن بلوغه من {#} eV",
  "rare → likely": "نادر ← محتمل",
  "scattering law S(α,β) · hydrogen bound in water": "قانون التشتت S(α,β) · هيدروجين مرتبط في الماء",
  "stripes: energy lost to the molecule in fixed amounts": "الأشرطة: طاقة تُعطى للجزيء بمقادير ثابتة",
});
