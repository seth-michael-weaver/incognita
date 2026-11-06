/* Arabic: waste (الوقود المستهلك عبر الزمن) */
WT.L.ch.waste = {
  num: "الدرس 1", title: "الوقود المستهلك عبر الزمن", short: "الوقود المستهلك",
  html: `
<div class="step">
  <h3>ماذا يخرج من المفاعل</h3>
  <p>بعد أربع أو خمس سنوات في قلب المفاعل يبقى قرص الوقود يورانيوم في معظمه. بضعة في المئة منه <b>نواتج انشطار</b>، أي الذرات المنقسمة. ونحو 1 % بلوتونيوم، وأثر ضئيل من <b>أكتينيدات ثانوية</b> أثقل مثل الأمريسيوم.</p>
  <div class="btns"><button class="btn" data-act="sort">افرز الذرات</button></div>
</div>
<div class="step">
  <h3>القرون الأولى</h3>
  <p>يقارن المنحنى خطر الوقود المستهلك إذا ابتُلع بخطر خام اليورانيوم الذي صُنع منه. في البداية تطغى نواتج الانشطار، لكن عمر النصف لمعظمها نحو 30 سنة: وبعد قرابة 300 سنة تهبط تحت مستوى الخام.</p>
  <div class="ctl"><label for="wst-t1">السنوات بعد التفريغ</label><input id="wst-t1" type="range" data-bind="lt" data-instant min="0" max="6" step="0.01" value="1.5"><output data-show="yr" data-fmt="0"></output></div>
</div>
<div class="step">
  <h3>ثم البلوتونيوم</h3>
  <p>يبقى البلوتونيوم والأمريسيوم، وأعمار النصف لهما من قرون إلى عشرات آلاف السنين. وهما يُبقيان الوقود المستهلك فوق مستوى الخام أكثر من مئة ألف سنة.</p>
  <div class="ctl"><label for="wst-t2">السنوات بعد التفريغ</label><input id="wst-t2" type="range" data-bind="lt" data-instant min="0" max="6" step="0.01" value="4"><output data-show="yr" data-fmt="0"></output></div>
</div>
<div class="step">
  <h3>إعادة التدوير والتحويل</h3>
  <p>استخرج البلوتونيوم واحرقه وقودًا جديدًا، فتنخفض المدة إلى نحو عشرة آلاف سنة. واشطر أيضًا الأكتينيدات الثانوية في مفاعلات سريعة، فلا يبقى إلا نواتج الانشطار: بضع مئات من السنين.</p>
  <div class="btns"><button class="btn ghost" data-act="rp" aria-pressed="false">أعد تدوير البلوتونيوم</button><button class="btn ghost" data-act="tm" aria-pressed="false">حوّل الأكتينيدات الثانوية</button></div>
</div>`,
};
Object.assign(WT.L.labels, {
  "Sort the atoms": "افرز الذرات",
  "Mix them again": "اخلطها من جديد",
  "uranium": "اليورانيوم",
  "fission products": "نواتج الانشطار",
  "fission prod.": "نواتج الانشطار",
  "plutonium": "البلوتونيوم",
  "minor actinides": "الأكتينيدات الثانوية",
  "minor act.": "أكتينيدات ثانوية",
  "a used fuel pellet, {#} atoms": "قرص وقود مستهلك، {#} ذرة",
  "a used fuel pellet, {#} atoms shown": "قرص وقود مستهلك، معروضة منه {#} ذرة",
  "the glow: fission products are the most radioactive": "التوهج: نواتج الانشطار هي الأشد إشعاعًا",
  "the glow: the fission products are by far the most radioactive part": "التوهج: نواتج الانشطار هي الجزء الأشد إشعاعًا بفارق كبير",
  "spent fuel": "الوقود المستهلك",
  "spent fuel, one tonne": "الوقود المستهلك، طن واحد",
  "the ore": "الخام",
  "the ore it was made from": "الخام الذي صُنع منه",
  "{#} yr": "{#} سنة",
  "{#} million": "{#} مليون",
  "uranium ore level": "مستوى خام اليورانيوم",
  "the uranium ore it was made from": "خام اليورانيوم الذي صُنع منه",
  "years after unloading (log scale) →": "السنوات بعد التفريغ (مقياس لوغاريتمي) →",
  "hazard vs ore (log)": "الخطر مقارنة بالخام (لوغاريتمي)",
  "hazard if swallowed, relative to the ore (log scale)": "الخطر عند الابتلاع، نسبةً إلى الخام (مقياس لوغاريتمي)",
  "Am, Cm, Np": "Am, Cm, Np",
  "americium, curium…": "الأمريسيوم، الكوريوم…",
  "{#} years: {#} × the ore": "{#} سنة: {#} × الخام",
  "below the ore it came from": "تحت الخام الذي جاء منه",
  "mostly from fission products": "معظمه من نواتج الانشطار",
  "mostly from plutonium": "معظمه من البلوتونيوم",
  "mostly from americium": "معظمه من الأمريسيوم",
  "recycle + transmute": "إعادة تدوير + تحويل",
  "recycle Pu and transmute minor actinides": "إعادة تدوير Pu وتحويل الأكتينيدات الثانوية",
  "plutonium recycled": "البلوتونيوم مُعاد تدويره",
  "plutonium recycled, minor actinides in the waste": "البلوتونيوم مُعاد تدويره، والأكتينيدات الثانوية في النفايات",
  "only minor actinides removed": "أُزيلت الأكتينيدات الثانوية فقط",
  "minor actinides removed, plutonium left in": "أُزيلت الأكتينيدات الثانوية، وبقي البلوتونيوم",
  "spent fuel as it is": "الوقود المستهلك كما هو",
  "spent fuel kept as it is": "الوقود المستهلك محفوظًا كما هو",
  "reaches the ore level after ~{#} years": "يبلغ مستوى الخام بعد ~{#} سنة",
  "reaches the ore level after ~{#},{#} years": "يبلغ مستوى الخام بعد ~{#},{#} سنة",
  "illustrative shape (after OECD-NEA)": "شكل توضيحي (عن OECD-NEA)",
});
