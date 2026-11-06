/* Arabic: sandbox (ابنِ مفاعلًا) */
WT.L.ch.sandbox = {
  num: "الدرس 1", title: "ابنِ مفاعلًا", short: "ابنِ مفاعلًا", lead: "اختر وقودًا ومهدِّئًا ومبرِّدًا وحجمًا، وانظر هل يستطيع التفاعل المتسلسل أن يستمر ذاتيًا. نموذج كتب دراسية مبسّط.",
  html: `
<div class="step">
  <h3>العوامل الأربعة</h3>
  <p>لو لم يتسرّب أي نيوترون، لأدّى كل نيوترون ممتَص إلى <i>k</i><sub>∞</sub> = <i>η f p ε</i> نيوترونًا جديدًا؛ وهذه الكومة الغرافيتية من اليورانيوم الطبيعي تبلغ ذلك بالكاد.</p>
</div>
<div class="step">
  <h3>اختر مهدِّئًا</h3>
  <p>مع اليورانيوم الطبيعي، لا يرفع <i>k</i><sub>∞</sub> فوق 1 إلا الماء الثقيل أو الغرافيت: الماء الخفيف يبطئ النيوترونات جيدًا لكنه يمتص الكثير منها.</p>
  <div class="btns" role="group" aria-label="المهدِّئ"><button class="btn ghost" data-act="mo_h2o">الماء الخفيف</button> <button class="btn ghost" data-act="mo_d2o">الماء الثقيل</button> <button class="btn ghost" data-act="mo_c">الغرافيت</button></div>
  <div class="ctl"><label for="sb-m1">المهدِّئ لكل وحدة وقود</label><input id="sb-m1" type="range" data-bind="lm" min="-0.5" max="2.3" step="0.01" value="0.3"><output class="sb-m"></output></div>
</div>
<div class="step">
  <h3>خصِّب الوقود</h3>
  <p>بضعة في المئة من اليورانيوم-235 تكفي ليعمل الماء العادي، ولهذا تستخدمه معظم مفاعلات اليوم.</p>
  <div class="btns" role="group" aria-label="الوقود"><button class="btn ghost" data-act="fu_nat">U طبيعي</button> <button class="btn ghost" data-act="fu_leu">U مخصَّب</button> <button class="btn ghost" data-act="fu_mox">MOX (Pu)</button> <button class="btn ghost" data-act="fu_th">ثوريوم + U-233</button></div>
  <div class="ctl"><label for="sb-e1">حصة المادة الانشطارية (%)</label><input id="sb-e1" type="range" data-bind="enr" min="0.7" max="30" step="0.1" value="3"><output data-show="enr" data-fmt="1"></output></div>
</div>
<div class="step">
  <h3>الحجم والتسرّب</h3>
  <p>تفلت النيوترونات عبر السطح، لذا <i>k</i> = <i>k</i><sub>∞</sub> / (1 + <i>M</i>²<i>B</i>²). اسحب حافة هذه الكومة الغرافيتية من اليورانيوم الطبيعي حتى الحلقة المتقطعة.</p>
  <div class="ctl"><label for="sb-r1">نصف قطر القلب (m)</label><input id="sb-r1" type="range" data-bind="R" min="0.2" max="6" step="0.05" value="2"><output data-show="R" data-fmt="2"></output></div>
</div>
<div class="step">
  <h3>حين يغلي المبرِّد</h3>
  <p>في قلب غرافيتي يُبرَّد بالماء، يرفع الغليان <i>k</i>، لأن الماء كان يمتص أكثر مما يبطئ: عيب مفاعل RBMK في تشيرنوبل. جرّب مبرِّدات أخرى.</p>
  <div class="btns" role="group" aria-label="المبرِّد"><button class="btn ghost" data-act="co_h2o">ماء</button> <button class="btn ghost" data-act="co_gas">CO₂ / هيليوم</button> <button class="btn ghost" data-act="co_na">صوديوم</button></div>
</div>
<div class="step">
  <h3>ابنِ مفاعلك</h3>
  <p>كل شيء مسموح. المفاعل السريع بلا مهدِّئ ويحتاج إلى وقود انشطاري أكثر بكثير.</p>
  <div class="btns" role="group" aria-label="الوقود"><button class="btn ghost" data-act="fu_nat">U طبيعي</button> <button class="btn ghost" data-act="fu_leu">U مخصَّب</button> <button class="btn ghost" data-act="fu_mox">MOX (Pu)</button> <button class="btn ghost" data-act="fu_th">ثوريوم + U-233</button></div>
  <div class="ctl"><label for="sb-e2">حصة المادة الانشطارية (%)</label><input id="sb-e2" type="range" data-bind="enr" min="0.7" max="30" step="0.1" value="3"><output data-show="enr" data-fmt="1"></output></div>
  <div class="btns" role="group" aria-label="المهدِّئ"><button class="btn ghost" data-act="mo_none">بلا مهدِّئ</button> <button class="btn ghost" data-act="mo_h2o">الماء الخفيف</button> <button class="btn ghost" data-act="mo_d2o">الماء الثقيل</button> <button class="btn ghost" data-act="mo_c">الغرافيت</button></div>
  <div class="ctl"><label for="sb-m2">المهدِّئ لكل وحدة وقود</label><input id="sb-m2" type="range" data-bind="lm" min="-0.5" max="2.3" step="0.01" value="0.3"><output class="sb-m"></output></div>
  <div class="btns" role="group" aria-label="المبرِّد"><button class="btn ghost" data-act="co_h2o">ماء</button> <button class="btn ghost" data-act="co_d2o">الماء الثقيل</button> <button class="btn ghost" data-act="co_gas">CO₂ / هيليوم</button> <button class="btn ghost" data-act="co_na">صوديوم</button> <button class="btn ghost" data-act="co_pb">رصاص</button> <button class="btn ghost" data-act="co_salt">ملح منصهر</button></div>
  <div class="ctl"><label for="sb-r2">نصف قطر القلب (m)</label><input id="sb-r2" type="range" data-bind="R" min="0.2" max="6" step="0.05" value="2"><output data-show="R" data-fmt="2"></output></div>
</div>`,
};
Object.assign(WT.L.labels, {
  "CO₂ / helium gas coolant": "مبرِّد غازي CO₂ / هيليوم",
  "MOX {#} % Pu": "MOX {#} % Pu",
  "MOX, {#} % plutonium{#}": "MOX، {#} % بلوتونيوم{#}",
  "R {#} m": "R {#} m",
  "absorbed in fuel": "يُمتص في الوقود",
  "can never sustain a chain, at any size": "لا يمكن أن يستمر التسلسل بأي حجم",
  "caught by fuel": "أسره الوقود",
  "coolant boils away: k ↑": "المبرِّد يتبخر كله: k ↑",
  "coolant boils: k ↑": "المبرِّد يغلي: k ↑",
  "coolant boils: k ≈": "المبرِّد يغلي: k ≈",
  "coolant lost: k barely changes": "فُقد المبرِّد: k لا يكاد يتغير",
  "coolant lost: k ↑": "فُقد المبرِّد: k ↑",
  "critical size": "الحجم الحرج",
  "escape capture": "تفلت من الأسر",
  "f": "f",
  "fast fission": "انشطار سريع",
  "fission": "الانشطار",
  "fuel": "الوقود",
  "fuel heats up: k ↓ (Doppler)": "الوقود يسخن: k ↓ (دوبلر)",
  "fuel hotter: k ↓": "الوقود أسخن: k ↓",
  "graphite moderator": "مهدِّئ غرافيتي",
  "graphite moderator · CO₂ / helium gas coolant": "مهدِّئ غرافيتي · مبرِّد غازي CO₂ / هيليوم",
  "graphite moderator · water coolant": "مهدِّئ غرافيتي · مبرِّد مائي",
  "k": "k",
  "k∞": "k∞",
  "leak": "تسرب",
  "leak out": "تتسرّب",
  "light water moderator": "مهدِّئ من الماء الخفيف",
  "light water moderator · water coolant": "مهدِّئ من الماء الخفيف · مبرِّد مائي",
  "mod./cool.": "مهدِّئ/مبرِّد",
  "moderator, coolant": "المهدِّئ، المبرِّد",
  "natural U": "U طبيعي",
  "natural uranium ({#} % U{#})": "يورانيوم طبيعي ({#} % U{#})",
  "never critical": "لا يبلغ الحرجية أبدًا",
  "no chain, any size": "لا تسلسل بأي حجم",
  "no leakage": "بلا تسرّب",
  "no moderator: a fast reactor · sodium coolant": "بلا مهدِّئ: مفاعل سريع · مبرِّد صوديوم",
  "no moderator: fast": "بلا مهدِّئ: سريع",
  "no size is big enough": "لا حجم كبير بما يكفي",
  "p": "p",
  "per fuel absorption": "لكل امتصاص في الوقود",
  "radius {#} m": "نصف القطر {#} m",
  "radius {#} m · drag the edge": "نصف القطر {#} m · اسحب الحافة",
  "simplified model": "نموذج مبسّط",
  "simplified one-group model · illustration": "نموذج مبسّط بمجموعة واحدة · توضيح",
  "stays in": "تبقى داخله",
  "stays in (M² {#} cm²)": "تبقى داخله (M² {#} cm²)",
  "sustains a chain, {#} % to spare (ρ)": "يستمر التسلسل بفائض {#} % (ρ)",
  "sustains: +{#} % spare": "يستمر: فائض +{#} %",
  "too small: critical at radius {#} m": "صغير جدًا: حرج عند نصف قطر {#} m",
  "too small: needs {#} m": "صغير جدًا: يلزم {#} m",
  "uranium, {#} % U{#}": "يورانيوم، {#} % U{#}",
  "water boils: k ↑": "الماء يغلي: k ↑",
  "water boils: k ↓": "الماء يغلي: k ↓",
  "water coolant": "مبرِّد مائي",
  "water heats or boils: k ↑": "الماء يسخن أو يغلي: k ↑",
  "water heats or boils: k ↓": "الماء يسخن أو يغلي: k ↓",
  "where the neutrons go": "أين تذهب النيوترونات",
  "{#} % U{#}": "{#} % U{#}",
  "enriched U": "U مخصَّب",
  "light water": "الماء الخفيف",
  "heavy water": "الماء الثقيل",
  "lead": "رصاص",
  "molten salt": "ملح منصهر",
  "sodium": "الصوديوم",
  "coolant": "المبرِّد",
  "= η f, if nothing leaked": "= η f، لو لم يتسرّب شيء",
  "= η f p ε, if nothing leaked": "= η f p ε، لو لم يتسرّب شيء",
  "stays in: {#} / ({#} + M²B²), M² = {#} cm²": "تبقى داخله: {#} / ({#} + M²B²)، M² = {#} cm²",
  "neutrons per absorption in fuel": "نيوترونات لكل امتصاص في الوقود",
  "share absorbed in fuel": "الحصة الممتصة في الوقود",
  "no slowing down, no resonance loss": "لا إبطاء، لا فقد رنيني",
  "escape capture while slowing": "الإفلات من الأسر أثناء الإبطاء",
  "fast fission counted in η": "الانشطار السريع محسوب في η",
  "bonus from fast fission": "مكسب من الانشطار السريع",
  "thorium, {#} % U{#}": "ثوريوم، {#} % U{#}",
  "Th + {#} % U{#}": "Th + {#} % U{#}",
  "uranium, {#} % U{#} (highly enriched)": "يورانيوم، {#} % U{#} (عالي التخصيب)",
  "critical at {#} m": "حرج عند {#} m",
  "coolant heats: k ↑": "المبرِّد يسخن: k ↑",
  "coolant heats: k ↓": "المبرِّد يسخن: k ↓",
  "coolant boils away: k ↓": "المبرِّد يتبخر كله: k ↓",
  "coolant lost: k ↓": "فُقد المبرِّد: k ↓",
  "heavy water coolant": "مبرِّد من الماء الثقيل",
  "sodium coolant": "مبرِّد صوديوم",
  "lead coolant": "مبرِّد رصاص",
  "molten salt coolant": "مبرِّد من ملح منصهر",
  "heavy water moderator": "مهدِّئ من الماء الثقيل",
  "heavy water moderator · heavy water coolant": "مهدِّئ من الماء الثقيل · مبرِّد من الماء الثقيل",
  "heavy water moderator · water coolant": "مهدِّئ من الماء الثقيل · مبرِّد مائي",
  "graphite moderator · sodium coolant": "مهدِّئ غرافيتي · مبرِّد صوديوم",
  "no moderator: a fast reactor · lead coolant": "بلا مهدِّئ: مفاعل سريع · مبرِّد رصاص",
  "no moderator: a fast reactor · CO₂ / helium gas coolant": "بلا مهدِّئ: مفاعل سريع · مبرِّد غازي CO₂ / هيليوم",
  "no moderator: a fast reactor · molten salt coolant": "بلا مهدِّئ: مفاعل سريع · مبرِّد من ملح منصهر",
  "water moderates": "الماء يهدِّئ",
  "heavy water moderates": "الماء الثقيل يهدِّئ",
  "no moderator, but the water moderates": "بلا مهدِّئ، لكن الماء يهدِّئ",
  "no moderator, but the heavy water moderates": "بلا مهدِّئ، لكن الماء الثقيل يهدِّئ",
});
