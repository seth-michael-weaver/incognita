/* Arabic: binding (الفصل 3، لماذا تتماسك النوى؟) */
WT.L.ch.binding = {
  num: "الفصل 3", title: "لماذا تتماسك النوى", short: "طاقة الربط",
  html: `
<div class="step">
  <p>كلما ارتفعت على المنحنى زاد الترابط. كل نقطة تمثل عددًا كتليًا A واحدًا (عدد البروتونات مضافًا إليه النيوترونات)، وارتفاعها هو الطاقة اللازمة، لكل نيوكليون، لتفكيك تلك النواة بالكامل. اسحب A واقرأ العلامة: وسط المنحنى، حول الحديد والنيكل، هو القمة.</p>
  <div class="ctl"><label for="bi-a">العدد الكتلي A</label><input id="bi-a" type="range" data-bind="pick" data-instant min="2" max="260" step="1" value="56"><output data-show="pick" data-fmt="0"></output></div>
</div>
<div class="step">
  <p>اشطر اليورانيوم: يقع الجزآن كلاهما أعلى على المنحنى من اليورانيوم الذي جاءا منه، فتنتهي النيوكليونات نفسها أشد ترابطًا، ويخرج الفرق على هيئة طاقة. اختر الشظية الأخف؛ والأثقل هي باقي النيوكليونات الـ 236.</p>
  <div class="ctl"><label for="bi-f">الشظية الأخف A</label><input id="bi-f" type="range" data-bind="frag" data-instant min="70" max="118" step="1" value="95"><output data-show="frag" data-fmt="0"></output></div>
  <p class="ctl-result" id="bi-split-out" aria-live="polite"></p>
  <p>مهما كان الانشطار، فهو نحو 200 MeV: أكبر بعشرات الملايين من المرات من الإلكترون فولتات القليلة التي يعطيها احتراق جزيء واحد من الوقود.</p>
</div>
<div class="step">
  <p>ادمج نواتين خفيفتين في نواة واحدة. إن كانت النواة الجديدة أعلى على المنحنى تحررت طاقة. وبعد القمة يكلّف الدمج طاقة بدلًا من ذلك.</p>
  <div class="ctl"><label for="bi-u">كل نواة خفيفة A</label><input id="bi-u" type="range" data-bind="fuse" data-instant min="2" max="60" step="1" value="2"><output data-show="fuse" data-fmt="0"></output></div>
  <p class="ctl-result" id="bi-fuse-out" aria-live="polite"></p>
</div>`,
};
Object.assign(WT.L.labels, {
  "mass number A →": "العدد الكتلي A →",
  "binding energy per nucleon (MeV)": "طاقة الربط لكل نيوكليون (MeV)",
  "Ni{#}: most tightly bound": "Ni{#}: الأشد ارتباطًا",
  "measured masses (AME{#})": "كتل مقيسة (AME{#})",
  "Fe{#}: {#} MeV per nucleon · {#} MeV in all": "Fe{#}: {#} MeV لكل نيوكليون · {#} MeV إجمالًا",
});
