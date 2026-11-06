/* Arabic: afterheat (الحرارة بعد الإيقاف) */
WT.L.ch.afterheat = {
  num: "الدرس 1", title: "الحرارة بعد الإيقاف", short: "حرارة الاضمحلال",
  html: `
<div class="step">
  <h3>السلسلة تتوقف</h3>
  <p>إسقاط قضبان التحكم يوقف انشطار الذرات في غضون دقيقة تقريبًا. لكن الوقود يظل متوهجًا: فالشظايا التي خلّفتها الانشطارات السابقة مشعة، واضمحلالاتها لا تزال تطلق حرارة.</p>
  <div class="btns"><button class="btn" data-act="ahDrop">أسقِط القضبان</button> <button class="btn ghost" data-act="ahUp">أعِد التشغيل</button></div>
</div>
<div class="step">
  <h3>تخبو ببطء</h3>
  <p>بعد الإيقاف مباشرة تبلغ هذه الحرارة نحو 6–7 % من القدرة الكاملة. وبعد ساعة نحو 1 %، وبعد يوم نحو نصف في المئة، وبعد أسبوع ربعًا في المئة. حصص صغيرة، لكنها من رقم كبير جدًا.</p>
  <div class="ctl"><label for="ah-t">الزمن منذ الإيقاف</label><input id="ah-t" type="range" data-bind="lt" data-instant min="0" max="7.5" step="0.01" value="3.56"></div>
</div>
<div class="step">
  <h3>أبقِ الماء جاريًا</h3>
  <p>لذلك يُبرَّد القلب بعد الإيقاف أيضًا. تُبقي المضخات الماء متدفقًا حول الوقود فتحمل الحرارة بعيدًا. أوقفها فترتفع درجة الحرارة، لأن الحرارة لا تجد منفذًا.</p>
  <div class="btns"><button class="btn ghost" data-act="ahPump" aria-pressed="true">المضخات</button></div>
</div>
<div class="step">
  <h3>تبريد بلا مضخات</h3>
  <p>الماء الساخن يصعد والماء البارد يهبط. وحلقة تصعد إلى حوض موضوع أعلى من القلب تُبقي الماء جاريًا بلا أي مضخات. وتعتمد عدة تصاميم حديثة على ذلك لأيام.</p>
  <div class="btns"><button class="btn ghost" data-act="ahPump" aria-pressed="false">المضخات</button> <button class="btn ghost" data-act="ahPass" aria-pressed="true">الحلقة السلبية</button></div>
</div>`,
};
Object.assign(WT.L.labels, {
  "{a} s": "{a} s",
  "{a} min": "{a} دقيقة",
  "{a} hours": "{a} ساعة",
  "{a} days": "{a} يوم",
  "{a} months": "{a} شهر",
  "illustration": "توضيح",
  "splitting atoms": "انشطار الذرات",
  "heat from splitting atoms": "حرارة من انشطار الذرات",
  "decaying fragments": "اضمحلال الشظايا",
  "heat from decaying fragments": "حرارة من اضمحلال الشظايا",
  "full power": "القدرة الكاملة",
  "running at full power": "يعمل بالقدرة الكاملة",
  "{a} after the rods dropped": "{a} بعد سقوط القضبان",
  "total heat: {a} % of full power": "الحرارة الكلية: {a} % من القدرة الكاملة",
  "the splitting dies away in about a minute": "يخمد الانشطار في نحو دقيقة",
  "the splitting dies away within about a minute": "يخمد الانشطار في غضون دقيقة تقريبًا",
  "the decay heat stays and fades slowly": "حرارة الاضمحلال تبقى وتخبو ببطء",
  "the decay heat stays, and fades only slowly": "حرارة الاضمحلال تبقى، ولا تخبو إلا ببطء",
  "{#} min": "{#} دقيقة",
  "{#} hour": "{#} ساعة",
  "{#} day": "{#} يوم",
  "{#} week": "{#} أسبوع",
  "{#} year": "{#} سنة",
  "heat, share of full power": "الحرارة، حصة من القدرة الكاملة",
  "heat, as a share of full power": "الحرارة كحصة من القدرة الكاملة",
  "{a} after shutdown: {b} % of full power": "{a} بعد الإيقاف: {b} % من القدرة الكاملة",
  "{#} MW core: {a} MW, like {b} kettles": "قلب {#} MW: {a} MW، مثل {b} غلاية",
  "for a {#} MW core: {a} MW, as much as {b} electric kettles": "لقلب قدرته {#} MW: {a} MW، بقدر {b} غلاية كهربائية",
  "pool, up high": "حوض في الأعلى",
  "water pool, placed higher": "حوض ماء، موضوع أعلى",
  "cooler": "مبرِّد",
  "heat exchanger": "مبادل حراري",
  "pump on": "المضخة تعمل",
  "pump running": "المضخة تعمل",
  "pump off": "المضخة متوقفة",
  "pump stopped": "المضخة متوقفة",
  "boiling": "غليان",
  "the water starts to boil": "يبدأ الماء بالغليان",
  "normal": "طبيعي",
  "too hot": "ساخن جدًا",
  "temperature": "درجة الحرارة",
  "core temperature": "درجة حرارة القلب",
  "{a} after shutdown · heat {b} % of full power": "{a} بعد الإيقاف · الحرارة {b} % من القدرة الكاملة",
  "too hot: cooling must be restored": "ساخن جدًا: يجب استعادة التبريد",
  "too hot: the water would start to boil away; cooling must be restored": "ساخن جدًا: سيبدأ الماء بالتبخر؛ يجب استعادة التبريد",
  "temperature climbing": "درجة الحرارة ترتفع",
  "temperature climbing: the heat has nowhere to go": "درجة الحرارة ترتفع: الحرارة لا تجد منفذًا",
  "pumps carry the heat away": "المضخات تحمل الحرارة بعيدًا",
  "steady: the pumps carry the heat away": "مستقر: المضخات تحمل الحرارة بعيدًا",
  "steady, with no pumps": "مستقر، بلا مضخات",
  "steady: natural circulation carries the heat away": "مستقر: الدوران الطبيعي يحمل الحرارة بعيدًا",
  "steady": "مستقر",
});
