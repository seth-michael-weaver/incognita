/* Arabic: tof (الفصل 16، قياسات زمن الطيران) */
WT.L.ch.tof = {
  num: "الفصل 16", title: "قياسات زمن الطيران", short: "قياس القمم",
  html: `
<div class="step">
  <p>زمن طيران النيوترون يكشف طاقته. تغادر المصدر نبضة قصيرة من نيوترونات بطاقات شتى وتتسابق في أنبوب فارغ نحو الكاشف؛ فتصل السريعة أولًا. طول الأنبوب <i>L</i> معلوم، فيعطي كل زمن وصول <i>t</i> سرعة النيوترون، وتعطي السرعةُ طاقتَه:</p>
  <div class="formula">E = (72.3 · L / t)²   (E بالإلكترون فولت، L بالأمتار، t بالميكروثواني)</div>
  <p>تعدّ الساعة فوق الأنبوب الزمن الحقيقي منذ النبضة؛ ويُرسم الطيران أبطأ بنحو 1400 مرة. وتحت الأنبوب يتحول آخر وصول إلى طاقة. اسحب مسار الطيران: الأنبوب الأطول ينشر الطاقات نفسها على زمن أطول، فيُميَّز بعضها عن بعض بدقة أكبر.</p>
  <div class="ctl"><label for="tof-l1">مسار الطيران (m)</label><input id="tof-l1" type="range" data-bind="Lv" data-instant min="5" max="200" step="1" value="50"><output data-show="Lv" data-fmt="0"></output></div>
</div>
<div class="step">
  <p>عينة رقيقة: الانخفاض يرسم المقطع العرضي. توجد الآن عينة في الحزمة. قرب 6.7 eV تملك أنويتها رنينًا فتلتقط النيوترونات (الومضات)، فيصل عدد أقل عند الزمن المقابل. يقارن المخطط العدّ مع العينة وبدونها: <b>النفاذية</b>، وتساوي 1 حين يعبر كل نيوترون.</p>
  <p>النقاط أعداد محاكاة بتشتتها؛ والخط المتصل ما يسجله الكاشف في المتوسط؛ والخط المتقطع شكل المقطع العرضي نفسه. مع العينة الرقيقة ينسخ الانخفاض ذلك الشكل.</p>
  <div class="ctl"><label for="tof-d1">سماكة العينة (µm)</label><input id="tof-d1" type="range" data-bind="lgT" data-instant min="0" max="3.5" step="0.01" value="0.5"><output data-show="thk" data-fmt="0"></output></div>
</div>
<div class="step">
  <p>عينة سميكة: الانخفاض يشبع. عند طاقة القمة تلتقط مقدمة العينة كل نيوترون، فيسودّ المركز ويبقى أسود مهما زدت السماكة؛ ولا يستطيع الانخفاض أن ينمو إلا باتساعه نحو جانبيه. هذا هو <b>الحجب الذاتي</b>: الطبقات الأمامية تحجب الخلفية. وعندئذ تخبرنا العينة السميكة عن أجنحة الرنين أكثر مما تخبرنا عن قمته.</p>
  <div class="ctl"><label for="tof-d2">سماكة العينة (µm)</label><input id="tof-d2" type="range" data-bind="lgT" data-instant min="0" max="3.5" step="0.01" value="3"><output data-show="thk" data-fmt="0"></output></div>
</div>
<div class="step">
  <p>نبضات أطول وطيران أقصر: ينطمس الانخفاض. ثلاثة أشياء تحدد عرض الانخفاض، وكلها مكتوبة تحت المخطط: عرض الرنين نفسه؛ واهتزاز ذرات العينة بالحرارة الذي يلطّخ طاقة كل تصادم قليلًا (توسيع <b>دوبلر</b>)؛ وضبابية التوقيت، لأن النبضة الأطول أو الأنبوب الأقصر يجعل كل زمن وصول، ومن ثم كل طاقة، أقل يقينًا.</p>
  <p>أطِل النبضة أو قصِّر الأنبوب: يصبح الانخفاض أعرض وأضحل، مع أن حصة النيوترونات التي يزيلها تبقى تقريبًا كما هي.</p>
  <div class="ctl"><label for="tof-p1">عرض النبضة (µs)</label><input id="tof-p1" type="range" data-bind="lgDt" data-instant min="-2" max="1" step="0.01" value="0.3"><output data-show="dt" data-fmt="2"></output></div>
  <div class="ctl"><label for="tof-l2">مسار الطيران (m)</label><input id="tof-l2" type="range" data-bind="Lv" data-instant min="5" max="200" step="1" value="20"><output data-show="Lv" data-fmt="0"></output></div>
</div>
<div class="step">
  <p>يعمل INCOGNITA بالعكس: يأخذ أعدادًا مقيسة كهذه ويسأل أي رنين، إذا مرّ بالتجربة نفسها (السماكة والحرارة وضبابية التوقيت)، يعيد إنتاجها. هنا يبدأ الضبط من تخمين عرضه النيوتروني Γ<sub>n</sub> (مدى تمسك المستوى بالنيوترونات) أكبر من الصواب بنحو أربعة أضعاف (المنحنى الأزرق)، ويغيّره خطوة خطوة حتى يمر المنحنى بالنقاط.</p>
  <p>يعرض المؤشر التخمين الحالي و<b>عدم المطابقة</b>: نحو 1 يعني أن المنحنى قريب من النقاط بقدر ما يسمح به تشتت العدّ. غيّر التجربة فيبدأ الضبط من جديد، من أعداد جديدة، ويستقر قرب العرض نفسه؛ وحيث لا يستطيع مطابقة النقاط جيدًا، يخبرك عدم المطابقة بذلك.</p>
  <div class="ctl"><label for="tof-l3">مسار الطيران (m)</label><input id="tof-l3" type="range" data-bind="Lv" data-instant min="5" max="200" step="1" value="50"><output data-show="Lv" data-fmt="0"></output></div>
  <div class="ctl"><label for="tof-d3">سماكة العينة (µm)</label><input id="tof-d3" type="range" data-bind="lgT" data-instant min="0" max="3.5" step="0.01" value="1.5"><output data-show="thk" data-fmt="0"></output></div>
  <div class="ctl"><label for="tof-p2">عرض النبضة (µs)</label><input id="tof-p2" type="range" data-bind="lgDt" data-instant min="-2" max="1" step="0.01" value="-1"><output data-show="dt" data-fmt="2"></output></div>
</div>`,
};
Object.assign(WT.L.labels, {
  "pulsed source": "مصدر نبضي",
  "detector": "الكاشف",
  "L = {#} m · clock: {#} ms since the pulse": "L = {#} m · الساعة: {#} ms منذ النبضة",
  "transmission": "النفاذية",
  "cross-section shape (scaled)": "شكل المقطع العرضي (مُقيَّس)",
  "what the detector records": "ما يسجله الكاشف",
  "simulated counts": "أعداد محاكاة",
  "fast neutrons arrive first, slow ones later: the clock sorts them by energy": "السريعة تصل أولًا والبطيئة لاحقًا: الساعة ترتّبها بحسب الطاقة",
  "L = {#} m · clock: {#} µs since the pulse": "L = {#} m · الساعة: {#} µs منذ النبضة",
  "last arrival: t = {#} µs → E = ({#} × {#} / {#})² = {#} eV": "آخر وصول: t = {#} µs → E = ({#} × {#} / {#})² = {#} eV",
  "last arrival: t = {#} ms → E = ({#} × {#} / {#})² = {#} eV": "آخر وصول: t = {#} ms → E = ({#} × {#} / {#})² = {#} eV",
  "sample": "العينة",
  "L = {#} m · {#} eV arrives after {#} ms": "L = {#} m · {#} eV يصل بعد {#} ms",
  "sample {#} µm · dip {#} % deep": "العينة {#} µm · عمق الانخفاض {#} %",
  "sample {#} µm · dip {#} % deep: black in the centre": "العينة {#} µm · عمق الانخفاض {#} %: أسود في المركز",
  "L = {#} m · {#} eV arrives after {#} µs": "L = {#} m · {#} eV يصل بعد {#} µs",
  "width from timing {#} meV · from heat (Doppler) {#} meV · the resonance's own {#} meV": "العرض من التوقيت {#} meV · من الحرارة (دوبلر) {#} meV · عرض الرنين نفسه {#} meV",
  "the fit's current guess": "التخمين الحالي للضبط",
  "fit: Γn = {#} meV (put into the simulation: {#}) · misfit {#}": "الضبط: Γn = {#} meV (في المحاكاة: {#}) · عدم المطابقة {#}",
});
