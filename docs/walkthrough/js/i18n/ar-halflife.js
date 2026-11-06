/* Arabic: halflife (النشاط الإشعاعي وعمر النصف) */
WT.L.ch.halflife = {
  num: "الدرس 1", title: "النشاط الإشعاعي وعمر النصف", short: "عمر النصف",
  lead: "بعض الذرات غير مستقرة: عاجلًا أو آجلًا تتفكك نواتها، فتطلق إشعاعًا وتصير شيئًا آخر. لا أحد يستطيع أن يقول متى ستتفكك نواة بعينها، لكن العينة كلها تتبع ساعة يمكنك أن تضبط ساعتك عليها.",
  html: `
<div class="step">
  <h3>عينة تتفكك عشوائيًا</h3>
  <p>كل كرة متوهجة نواة غير مستقرة. قد تتفكك أي واحدة منها في أي لحظة، فتطلق ومضة إشعاع وتستقر ذرةً هادئة مستقرة. انقر على واحدة لتجعلها تتفكك.</p>
  <div class="btns"><button class="btn" data-act="refill">عينة جديدة</button></div>
</div>
<div class="step">
  <h3>النصف، ثم نصف النصف</h3>
  <p>لا أحد يعرف أيها ستتفكك تاليًا، لكن الجمع يمكن التنبؤ به: بعد <b>عمر نصف</b> واحد يبقى نحو النصف، وبعد اثنين الربع، ثم الثُّمن. اجعل عمر النصف أطول أو أقصر.</p>
  <div class="ctl"><label for="hl-th">عمر النصف (ثوانٍ)</label><input id="hl-th" type="range" data-bind="Th" data-instant min="1" max="8" step="0.5" value="3"><output data-show="Th" data-fmt="1"></output></div>
  <div class="btns"><button class="btn ghost" data-act="refill">عينة جديدة</button></div>
</div>
<div class="step">
  <h3>الأنوية بلا ذاكرة</h3>
  <p>تابع نواة واحدة باقية. مهما طال بقاؤها، تظل فرصتها في البقاء عمر نصف آخر واحدة من اثنتين: النواة لا تشيخ.</p>
  <div class="btns"><button class="btn ghost" data-act="tag">تابع غيرها</button><button class="btn ghost" data-act="refill">عينة جديدة</button></div>
</div>
<div class="step">
  <h3>أعمار نصف حقيقية</h3>
  <p>تمتد أعمار النصف للنظائر الحقيقية من أيام إلى مليارات السنين. على هذا المحور الزمني الممطوط يسقط كل نظير من جرف عند عمر نصفه. اختر واحدًا واسحب الزمن إلى الأمام.</p>
  <div class="btns"><button class="btn ghost" data-act="iso0" aria-pressed="false">اليود-131</button><button class="btn ghost" data-act="iso1" aria-pressed="true">السيزيوم-137</button><button class="btn ghost" data-act="iso2" aria-pressed="false">الكربون-14</button><button class="btn ghost" data-act="iso3" aria-pressed="false">اليورانيوم-238</button></div>
  <div class="ctl"><label for="hl-t1">الزمن المنقضي</label><input id="hl-t1" type="range" data-bind="lt" data-instant min="3" max="17.8" step="0.02" value="8.98"><output class="hl-tout"></output></div>
</div>
<div class="step">
  <h3>النشاط: تفككات في الثانية</h3>
  <p>غرام واحد من كل نظير، جنبًا إلى جنب. عمر النصف القصير يعني تفككات كثيرة كل ثانية، لكن لا يدوم طويلًا؛ أما عمر النصف الطويل فيتوهج خافتًا دهورًا. اسحب الزمن وشاهد المصابيح تنطفئ واحدًا تلو الآخر.</p>
  <div class="ctl"><label for="hl-t2">الزمن المنقضي</label><input id="hl-t2" type="range" data-bind="lt" data-instant min="3" max="17.8" step="0.02" value="4.94"><output class="hl-tout"></output></div>
</div>`,
};
Object.assign(WT.L.labels, {
  "survived {#} half-lives": "بقيت {#} عمر نصف",
  "chance to last one more: {#} in {#}": "فرصة البقاء عمر نصف آخر: {#} من {#}",
  "survived {#} half-lives · still {#} in {#}": "بقيت {#} عمر نصف · ما زالت {#} من {#}",
  "it popped: follow another": "تفككت: تابع غيرها",
  "{#} of {#} still unstable": "{#} من {#} ما زالت غير مستقرة",
  "{#} half-life": "{#} عمر نصف",
  "half-lives →": "أعمار النصف →",
  "nuclei left": "الأنوية الباقية",
  "{#} of {#} left · half-life {#} s": "بقي {#} من {#} · عمر النصف {#} s",
  "every survivor has the same {#}-in{#} chance per half-life": "لكل نواة باقية الفرصة نفسها، {#} من {#}، في كل عمر نصف",
  "every survivor has the same 1-in-2 chance per half-life": "لكل نواة باقية الفرصة نفسها، 1 من 2، في كل عمر نصف",
  "illustrative half-life": "عمر نصف توضيحي",
  "{#} hour": "{#} ساعة", "{#} h": "{#} ساعة",
  "{#} day": "{#} يوم", "{#} d": "{#} يوم",
  "{#} year": "{#} سنة", "{#} yr": "{#} سنة",
  "{#} years": "{#} سنة",
  "{#}³ yr": "{#}³ سنة", "{#}⁶ yr": "{#}⁶ سنة", "{#}⁹ yr": "{#}⁹ سنة",
  "{#} million years": "{#} مليون سنة",
  "{#} billion years": "{#} مليار سنة",
  "drag": "اسحب",
  "iodine{#} · half-life {#} days": "اليود{#} · عمر النصف {#} يوم",
  "caesium{#} · half-life {#} years": "السيزيوم{#} · عمر النصف {#} سنة",
  "carbon{#} · half-life {#} years": "الكربون{#} · عمر النصف {#} سنة",
  "uranium{#} · half-life {#} billion years": "اليورانيوم{#} · عمر النصف {#} مليار سنة",
  "medicine, fission product": "الطب، ناتج انشطار",
  "fission product": "ناتج انشطار",
  "radiocarbon dating": "التأريخ بالكربون المشع",
  "natural uranium": "اليورانيوم الطبيعي",
  "I{#}": "I{#}", "Cs{#}": "Cs{#}", "C{#}": "C{#}", "U{#}": "U{#}",
  "iodine{#}": "اليود{#}", "caesium{#}": "السيزيوم{#}", "carbon{#}": "الكربون{#}", "uranium{#}": "اليورانيوم{#}",
  "all": "الكل",
  "{#} % left after {#} minutes": "بقي {#} % بعد {#} دقيقة",
  "{#} % left after {#} hours": "بقي {#} % بعد {#} ساعة",
  "{#} % left after {#} days": "بقي {#} % بعد {#} يوم",
  "{#} % left after {#} months": "بقي {#} % بعد {#} شهر",
  "{#} % left after {#} years": "بقي {#} % بعد {#} سنة",
  "{#} % left after {#} thousand years": "بقي {#} % بعد {#} ألف سنة",
  "{#} % left after {#} million years": "بقي {#} % بعد {#} مليون سنة",
  "{#} % left after {#} billion years": "بقي {#} % بعد {#} مليار سنة",
  "under {#} % left after {#} minutes": "بقي أقل من {#} % بعد {#} دقيقة",
  "under {#} % left after {#} hours": "بقي أقل من {#} % بعد {#} ساعة",
  "under {#} % left after {#} days": "بقي أقل من {#} % بعد {#} يوم",
  "under {#} % left after {#} months": "بقي أقل من {#} % بعد {#} شهر",
  "under {#} % left after {#} years": "بقي أقل من {#} % بعد {#} سنة",
  "under {#} % left after {#} thousand years": "بقي أقل من {#} % بعد {#} ألف سنة",
  "under {#} % left after {#} million years": "بقي أقل من {#} % بعد {#} مليون سنة",
  "under {#} % left after {#} billion years": "بقي أقل من {#} % بعد {#} مليار سنة",
  "½ {#} days": "½ {#} يوم", "½ {#} years": "½ {#} سنة",
  "½ {#} billion years": "½ {#} مليار سنة", "½ {#} bn years": "½ {#} مليار سنة",
  "~{#} /s": "~{#} /s", "almost none": "لا شيء تقريبًا",
  "{#} /s": "{#} /s", "under {#} /s": "أقل من {#} /s",
  "{#}×{#}³ /s": "{#}×{#}³ /s", "{#}×{#}⁴ /s": "{#}×{#}⁴ /s", "{#}×{#}⁵ /s": "{#}×{#}⁵ /s",
  "{#}×{#}⁶ /s": "{#}×{#}⁶ /s", "{#}×{#}⁷ /s": "{#}×{#}⁷ /s", "{#}×{#}⁸ /s": "{#}×{#}⁸ /s",
  "{#}×{#}⁹ /s": "{#}×{#}⁹ /s", "{#}×{#}¹⁰ /s": "{#}×{#}¹⁰ /s", "{#}×{#}¹¹ /s": "{#}×{#}¹¹ /s",
  "{#}×{#}¹² /s": "{#}×{#}¹² /s", "{#}×{#}¹³ /s": "{#}×{#}¹³ /s", "{#}×{#}¹⁴ /s": "{#}×{#}¹⁴ /s",
  "{#}×{#}¹⁵ /s": "{#}×{#}¹⁵ /s", "{#}×{#}¹⁶ /s": "{#}×{#}¹⁶ /s",
  "pops per second (log)": "تفككات في الثانية (لوغاريتمي)",
  "pops per second, {#} gram (each line ×{#})": "تفككات في الثانية، {#} غرام (كل خط ×{#})",
  "one gram of each, after {#} minutes": "غرام من كلٍّ، بعد {#} دقيقة",
  "one gram of each, after {#} hours": "غرام من كلٍّ، بعد {#} ساعة",
  "one gram of each, after {#} days": "غرام من كلٍّ، بعد {#} يوم",
  "one gram of each, after {#} months": "غرام من كلٍّ، بعد {#} شهر",
  "one gram of each, after {#} years": "غرام من كلٍّ، بعد {#} سنة",
  "one gram of each, after {#} thousand years": "غرام من كلٍّ، بعد {#} ألف سنة",
  "one gram of each, after {#} million years": "غرام من كلٍّ، بعد {#} مليون سنة",
  "one gram of each, after {#} billion years": "غرام من كلٍّ، بعد {#} مليار سنة",
});
