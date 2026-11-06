/* Arabic: transport (انتقال النيوترونات وطريقة مونت كارلو) */
WT.L.ch.transport = {
  num: "الدرس 1", title: "انتقال النيوترونات وطريقة مونت كارلو", short: "مونت كارلو",
  html: `
<div class="step">
  <h3>معادلة الانتقال</h3>
  <p>بدقة، تخضع النيوترونات لمعادلة بولتزمان للفيض الزاوي <i>ψ</i>(<b>r</b>, <b>Ω</b>, <i>E</i>): <b>Ω</b>·∇<i>ψ</i> + Σ<sub>t</sub><i>ψ</i> = ∫∫Σ<sub>s</sub><i>ψ</i>′ d<b>Ω</b>′d<i>E</i>′ + (<i>χ</i>/4π<i>k</i>)∫<i>ν</i>Σ<sub>f</sub><i>φ</i>′ d<i>E</i>′. وتحلّها طريقة مونت كارلو بتشغيل النيوترونات واحدًا تلو الآخر: يطير مسافة <i>s</i> = −ln <i>ξ</i> / Σ<sub>t</sub>، ثم يتشتت، أو يؤسَر، أو يسبب انشطارًا.</p>
  <div class="btns"><button class="btn" data-act="trnew">نيوترون جديد</button></div>
</div>
<div class="step">
  <h3>حيث يخفق الانتشار</h3>
  <p>يفترض الانتشار أن الفيض متساوٍ تقريبًا في كل الاتجاهات. ويخفق ذلك ضمن مسار حر أو اثنين من السطح وفي المواد الشديدة الامتصاص. قارنه بفيض مونت كارلو في لوح ذي مصدر منتظم وأنت ترفع الامتصاص.</p>
  <div class="ctl"><label for="tr-pa">الامتصاص Σ<sub>a</sub>/Σ<sub>t</sub></label><input id="tr-pa" type="range" data-bind="pa" data-instant min="0.05" max="0.8" step="0.05" value="0.5"><output data-show="pa" data-fmt="2"></output></div>
</div>
<div class="step">
  <h3>تكرار القدرة</h3>
  <p>لحساب <i>k</i><sub>eff</sub>، تصبح مواقع انشطار كل جيل مصدرَ الجيل التالي؛ و<i>k</i> هو عدد المواقع المحفوظة لكل نيوترون أُطلق. ابدأ من تخمين سيئ، كل النيوترونات عند حافة واحدة، وراقب المصدر ينتشر إلى النمط الأساسي.</p>
  <div class="btns"><button class="btn" data-act="trbad">ابدأ من جديد بتخمين سيئ</button></div>
</div>
<div class="step">
  <h3>هل تقارب المصدر؟</h3>
  <p>إنتروبيا شانون <i>H</i> = −Σ <i>p</i><sub>b</sub> log<sub>2</sub> <i>p</i><sub>b</sub> للمصدر المقسّم إلى خانات تستقر حين يستقر المصدر؛ وعندها فقط تُحسب متوسطات الأجيال. ويتقلص هامش الخطأ في <i>k</i> بنسبة 1/√<i>N</i> مع عدد التواريخ المحسوبة.</p>
  <div class="ctl"><label for="tr-n">التواريخ في كل جيل</label><input id="tr-n" type="range" data-bind="nh" data-instant min="100" max="2000" step="100" value="400"><output data-show="nh" data-fmt="0"></output></div>
</div>`,
};
Object.assign(WT.L.labels, {
  "vacuum": "فراغ",
  "glow: collision density": "التوهج: كثافة التصادمات",
  "amber glow: where collisions pile up": "التوهج الكهرماني: حيث تتراكم التصادمات",
  "tap the slab to start neutrons": "انقر اللوح لإطلاق نيوترونات",
  "scatter": "تشتت",
  "capture": "أسر",
  "fission": "الانشطار",
  "leak": "تسرب",
  "chance to fly at least s:  e^(−Σₜ s)": "احتمال الطيران مسافة s على الأقل:  e^(−Σₜ s)",
  "{#} free paths": "{#} مسار حر",
  "ξ = {#}  →  s = −ln ξ / Σₜ = {#} free paths": "ξ = {#}  →  s = −ln ξ / Σₜ = {#} مسار حر",
  "infinite medium S/Σₐ": "وسط لانهائي S/Σₐ",
  "Monte Carlo": "مونت كارلو",
  "diffusion": "الانتشار",
  "flux": "الفيض",
  "diffusion vs Monte Carlo: +{#} % at the surface, +{#} % in the middle": "الانتشار مقابل مونت كارلو: +{#} % عند السطح، +{#} % في المنتصف",
  "diffusion vs Monte Carlo: +{#} % at the surface, {#} % in the middle": "الانتشار مقابل مونت كارلو: +{#} % عند السطح، {#} % في المنتصف",
  "diffusion vs Monte Carlo: {#} % at the surface, +{#} % in the middle": "الانتشار مقابل مونت كارلو: {#} % عند السطح، +{#} % في المنتصف",
  "diffusion vs Monte Carlo: {#} % at the surface, {#} % in the middle": "الانتشار مقابل مونت كارلو: {#} % عند السطح، {#} % في المنتصف",
  "tap: drop the source there": "انقر: ضع المصدر هناك",
  "tap the slab to drop the whole source there": "انقر اللوح لوضع المصدر كله هناك",
  "generation {#}": "الجيل {#}",
  "source · dashed: fundamental mode": "المصدر · المتقطع: النمط الأساسي",
  "fission source · dashed: fundamental mode": "مصدر الانشطار · المتقطع: النمط الأساسي",
  "source entropy H (bits)": "إنتروبيا المصدر H (بت)",
  "inactive | active": "نشطة | غير نشطة",
  "inactive  |  active generations": "أجيال نشطة  |  غير نشطة",
  "k per generation": "k لكل جيل",
  "generation {#}: k = {#} · H = {#} bits": "الجيل {#}: k = {#} · H = {#} بت",
  "starting…": "البدء…",
  "k_eff = {#} ± {#} ({#} × {#} histories) · diffusion {#}": "k_eff = {#} ± {#} ({#} × {#} تاريخ) · الانتشار {#}",
  "{#} generations, averaging starts after {#}": "{#} جيل، يبدأ حساب المتوسط بعد {#}",
  "illustrative one-group data": "بيانات توضيحية أحادية المجموعة",
});
