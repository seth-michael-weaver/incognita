/* Arabic: rays (ألفا وبيتا وغاما والنيوترونات) */
WT.L.ch.rays = {
  num: "الدرس 1", title: "ألفا وبيتا وغاما والنيوترونات", short: "الإشعاع",
  html: `
<div class="step">
  <h3>أربعة أنواع من الإشعاع</h3>
  <p>جسيم <em class="a">ألفا</em> كتلة ثقيلة من بروتونين ونيوترونين. و<b>بيتا</b> إلكترون سريع. و<em class="g">غاما</em> ضوء أعلى طاقة بكثير من أن نراه. أما <em class="n">النيوترونات</em> فلا تحمل أي شحنة. ولكلٍّ منها ما يوقفه.</p>
</div>
<div class="step">
  <h3>الورق والألومنيوم</h3>
  <p>جسيمات ألفا كبيرة ومشحونة، فتصطدم بالذرات فورًا: ورقة واحدة توقفها. إلكترونات بيتا تذهب أبعد، لكن بضعة مليمترات من الألومنيوم توقفها أيضًا.</p>
  <div class="btns"><button class="btn ghost" data-act="sh_paper" aria-pressed="true">ورق</button><button class="btn ghost" data-act="sh_al" aria-pressed="false">ألومنيوم</button></div>
</div>
<div class="step">
  <h3>أشعة غاما: تتنصّف ولا تنعدم</h3>
  <p>أشعة غاما بلا شحنة، وغالبًا ما تمر بجوار الذرات. كل سنتيمتر من الرصاص يعطي كل شعاع الفرصة نفسها ليُلتقط، فتنصّف كل شريحة ما تبقى. يخفت الشعاع لكنه لا يبلغ الصفر تمامًا أبدًا.</p>
  <div class="ctl"><label for="ry-pb">الرصاص (cm)</label><input id="ry-pb" type="range" data-bind="pb" data-instant min="0" max="5" step="0.1" value="1"><output data-show="pb" data-fmt="1"></output></div>
</div>
<div class="step">
  <h3>النيوترونات: الرصاص لا يكفي</h3>
  <p>نيوترون يرتد عن نواة رصاص ثقيلة ككرة تنس طاولة تصطدم بكرة بولينغ: يحتفظ بسرعته. أما الهيدروجين في الماء فكتلته مثل كتلة النيوترون، فكل اصطدام يبطئه، حتى يصير بطيئًا بما يكفي ليُبتلع.</p>
  <div class="btns"><button class="btn ghost" data-act="nm_pb" aria-pressed="true">رصاص</button><button class="btn ghost" data-act="nm_water" aria-pressed="false">ماء</button></div>
  <div class="ctl"><label for="ry-nx">السُّمك (cm)</label><input id="ry-nx" type="range" data-bind="nx" data-instant min="0" max="60" step="1" value="30"><output data-show="nx" data-fmt="0"></output></div>
</div>
<div class="step">
  <h3>ابنِ درعًا</h3>
  <p>كدّس الطبقات حتى تتوقف الحزم الأربع كلها. أشعة غاما لا تهبط إلى الصفر تمامًا أبدًا، بل إلى حصة ضئيلة فقط.</p>
  <div class="btns"><button class="btn ghost" data-act="add_paper">+ ورق</button><button class="btn ghost" data-act="add_al">+ ألومنيوم</button><button class="btn ghost" data-act="add_pb">+ رصاص</button><button class="btn ghost" data-act="add_water">+ ماء</button><button class="btn" data-act="clear">مسح</button></div>
</div>`,
};
Object.assign(WT.L.labels, {
  "drag ↔": "اسحب ↔",
  "paper": "ورق",
  "aluminium {#} mm": "ألومنيوم {#} mm",
  "Al {#} mm": "Al {#} mm",
  "lead {#} cm": "رصاص {#} cm",
  "water {#} cm": "ماء {#} cm",
  "no shield": "بلا درع",
  "alpha": "ألفا", "beta": "بيتا", "gamma": "غاما", "neutron": "نيوترون",
  "stopped": "توقف",
  "all through": "يعبر كله",
  "{#} % through": "يعبر {#} %",
  "{#} in {#}": "{#} من {#}",
  "{#} in {#} million": "{#} من {#} مليون",
  "{#} in a billion": "{#} من مليار",
  "all four stopped": "توقفت الأربعة كلها",
  "all four beams stopped": "توقفت الحزم الأربع كلها",
  "flash = stopped inside the shield": "الومضة = توقف داخل الدرع",
  "each source fires a steady beam": "كل مصدر يطلق حزمة ثابتة",
  "flash = stopped": "الومضة = توقف",
  "four beams": "أربع حزم",
  "not to scale": "ليس بمقياس الرسم",
  "gamma rays (caesium{#})": "أشعة غاما (السيزيوم{#})",
  "cm of lead": "cm من الرصاص",
  "share still going": "الحصة التي ما زالت تعبر",
  "through: all · halved every {#} mm": "يعبر: الكل · يتنصّف كل {#} mm",
  "through: stopped · halved every {#} mm": "يعبر: لا شيء · يتنصّف كل {#} mm",
  "through: {#} % · halved every {#} mm": "يعبر: {#} % · يتنصّف كل {#} mm",
  "through: {#} in {#} · halved every {#} mm": "يعبر: {#} من {#} · يتنصّف كل {#} mm",
  "through: {#} in {#} million · halved every {#} mm": "يعبر: {#} من {#} مليون · يتنصّف كل {#} mm",
  "through: {#} in a billion · halved every {#} mm": "يعبر: {#} من مليار · يتنصّف كل {#} mm",
  "gets through: {#} % · halved every {#} mm of lead": "يعبر: {#} % · يتنصّف كل {#} mm من الرصاص",
  "gets through: {#} in {#} · halved every {#} mm of lead": "يعبر: {#} من {#} · يتنصّف كل {#} mm من الرصاص",
  "gets through: {#} in {#} million · halved every {#} mm of lead": "يعبر: {#} من {#} مليون · يتنصّف كل {#} mm من الرصاص",
  "gets through: {#} in a billion · halved every {#} mm of lead": "يعبر: {#} من مليار · يتنصّف كل {#} mm من الرصاص",
  "gets through: stopped · halved every {#} mm of lead": "يعبر: لا شيء · يتنصّف كل {#} mm من الرصاص",
  "counted: {#} of {#}": "المعدود: {#} من {#}",
  "through {#} % · back {#} % · caught {#} %": "عبر {#} % · ارتد {#} % · التُقط {#} %",
  "got through {#} % · bounced back {#} % · slowed and caught {#} %": "عبر {#} % · ارتد {#} % · تباطأ والتُقط {#} %",
  "bright = fast · dim = slowed": "الساطع = سريع · الخافت = متباطئ",
  "bright = fast neutron · red = hydrogen nucleus knocked away · green flash = swallowed": "الساطع = نيوترون سريع · الأحمر = نواة هيدروجين مقذوفة · الومضة الخضراء = ابتُلع",
  "simplified model": "نموذج مبسّط",
});
