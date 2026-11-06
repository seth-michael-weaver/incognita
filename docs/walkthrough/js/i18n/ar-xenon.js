/* Arabic: xenon (التسمم بالزينون) */
WT.L.ch.xenon = {
  num: "الدرس 1", title: "التسمم بالزينون", short: "الزينون",
  html: `
<div class="step">
  <h3>سمّ يصنعه الانشطار</h3>
  <p>نحو 6.6 % من الانشطارات تؤدي، عبر اليود-135، إلى الزينون-135: أقوى ماصّ للنيوترونات معروف. يتراكم نحو يومين إلى أن تحرقه النيوترونات ويزيله الاضمحلال بالسرعة التي يتكوّن بها. والقدرة الأعلى تحرقه أسرع أيضًا، فيبلغ مستواه حدّ التشبع.</p>
  <div class="ctl"><label for="xe-p1">القدرة (%)</label><input id="xe-p1" type="range" data-bind="P" data-instant min="10" max="100" step="5" value="100"><output data-show="P" data-fmt="0"></output></div>
</div>
<div class="step">
  <h3>حفرة الزينون</h3>
  <p>أوقف المفاعل فيتوقف الحرق، لكن اليود المتكوّن أصلًا يستمر في التحول إلى زينون. يبلغ السمّ ذروته بعد نحو تسع ساعات، بأكثر مما تستطيع القضبان استعادته، فلا يمكن إعادة تشغيل المفاعل؛ ثم يتلاشى خلال يومين إلى ثلاثة.</p>
  <div class="ctl"><label for="xe-th">الساعات بعد الإيقاف</label><input id="xe-th" type="range" data-bind="th" data-instant min="0" max="72" step="0.5" value="9"><output data-show="th" data-fmt="1"></output></div>
</div>
<div class="step">
  <h3>الإيقاف وإعادة التشغيل</h3>
  <p>الآن يجري كل شيء حيًّا، ثلاث ساعات في الثانية. أوقف المفاعل ثم حاول إعادة تشغيله: داخل الحفرة يُرفض الطلب؛ وبعد ذلك تحرق النيوترونات الزينون. وتغيير القدرة وحده يؤرجح الزينون أيضًا لساعات.</p>
  <div class="ctl"><label for="xe-p3">القدرة (%)</label><input id="xe-p3" type="range" data-bind="P" data-instant min="10" max="100" step="5" value="100"><output data-show="P" data-fmt="0"></output></div>
  <div class="btns"><button class="btn" data-act="xeshut">أوقف</button><button class="btn ghost" data-act="xerestart">أعِد التشغيل</button></div>
</div>
<div class="step">
  <h3>تذبذبات الزينون</h3>
  <p>في قلب مفاعل كبير يرتبط الجانبان ارتباطًا ضعيفًا فقط. أدخِل القضبان في جانب واحد: الفيض الأقل هناك يحرق زينونًا أقل، فتنزاح القدرة إلى الجانب الآخر ثم ترتدّ، مرة في اليوم تقريبًا. وفي القلوب الأكبر يتعاظم التأرجح ما لم يخمده المشغّلون.</p>
  <div class="ctl"><label for="xe-wd">حجم القلب (م)</label><input id="xe-wd" type="range" data-bind="wd" data-instant min="1.5" max="3.5" step="0.1" value="3"><output data-show="wd" data-fmt="1"></output></div>
  <div class="btns"><button class="btn" data-act="xepush">أدخِل القضبان في الجانب الأيسر</button></div>
</div>`,
};
Object.assign(WT.L.labels, {
  "fission → iodine{#} ({#} h) → xenon{#} ({#} h) → Cs{#}": "انشطار ← اليود{#} ({#} ساعة) ← الزينون{#} ({#} ساعة) ← Cs{#}",
  "xenon{#} + n → Xe{#}: {#} million barns": "الزينون{#} + n ← Xe{#}: {#} مليون بارن",
  "fission → iodine{#} ({#} h) → xenon{#} ({#} h) → Cs{#}  ·  Xe{#} swallows neutrons: {#} million barns": "انشطار ← اليود{#} ({#} ساعة) ← الزينون{#} ({#} ساعة) ← Cs{#}  ·  Xe{#} يبتلع النيوترونات: {#} مليون بارن",
  "spare reactivity": "التفاعلية الاحتياطية",
  "spare reactivity the rods can give": "التفاعلية الاحتياطية التي تعطيها القضبان",
  "{#} h": "{#} ساعة",
  "equilibrium {#} %": "التوازن {#} %",
  "xenon worth (% of k)": "قيمة الزينون (% من k)",
  "{#} % power · {#} h after start-up · xenon {#} %": "القدرة {#} % · {#} ساعة بعد التشغيل · الزينون {#} %",
  "no restart": "لا إعادة تشغيل",
  "too poisoned to restart": "مسموم جدًا لإعادة التشغيل",
  "shutdown": "الإيقاف",
  "drag": "اسحب",
  "peak {#} % at {#} h": "الذروة {#} % عند {#} ساعة",
  "{#} h after shutdown · xenon {#} % · restart possible": "{#} ساعة بعد الإيقاف · الزينون {#} % · إعادة التشغيل ممكنة",
  "{#} h after shutdown · xenon {#} % · cannot restart": "{#} ساعة بعد الإيقاف · الزينون {#} % · لا يمكن إعادة التشغيل",
  "shut down": "متوقف",
  "refused: more xenon than spare reactivity": "مرفوض: الزينون أكثر من التفاعلية الاحتياطية",
  "restarted": "أُعيد التشغيل",
  "tap the core to shut down": "انقر القلب للإيقاف",
  "tap the core to restart": "انقر القلب لإعادة التشغيل",
  "power": "القدرة",
  "running at {#} % · xenon {#} %": "يعمل عند {#} % · الزينون {#} %",
  "shut down · in the pit · xenon {#} %": "متوقف · في الحفرة · الزينون {#} %",
  "shut down · restart possible · xenon {#} %": "متوقف · إعادة التشغيل ممكنة · الزينون {#} %",
  "left {#} %": "اليسار {#} %",
  "right {#} %": "اليمين {#} %",
  "tap a side to push rods in": "انقر جانبًا لإدخال القضبان",
  "more power left": "قدرة أكبر يسارًا",
  "more power right": "قدرة أكبر يمينًا",
  "swing period {#} h · {#} m core: the swing dies away": "دورة التأرجح {#} ساعة · قلب {#} م: يتلاشى التأرجح",
  "swing period {#} h · {#} m core: the swing dies away slowly": "دورة التأرجح {#} ساعة · قلب {#} م: يتلاشى التأرجح ببطء",
  "swing period {#} h · {#} m core: the swing grows": "دورة التأرجح {#} ساعة · قلب {#} م: يتعاظم التأرجح",
  "{#} m core: push the rods to start a swing": "قلب {#} م: أدخِل القضبان لبدء التأرجح",
  "illustration": "توضيح",
});
