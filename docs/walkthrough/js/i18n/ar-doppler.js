/* Arabic: doppler (الفصل 20، توسّع دوبلر) */
WT.L.ch.doppler = {
  num: "الفصل 20", title: "توسّع دوبلر", short: "دوبلر",
  html: `
<div class="step">
  <h3>الحركة الحرارية للهدف</h3>
  <p>وقود أسخن: ذراته تهتز أسرع. لم تعد كل ذرة يورانيوم ساكنة حين يصلها النيوترون.</p>
  <div class="ctl"><label for="dop-t1">درجة حرارة الوقود (K)</label><input id="dop-t1" type="range" data-bind="T" data-instant min="300" max="1500" step="10" value="600"><output data-show="T" data-fmt="0"></output></div>
</div>
<div class="step">
  <h3>توسّع دوبلر</h3>
  <p>المنحنى هو احتمال أن يلتقط اليورانيوم-238 نيوترونًا، مرسومًا مقابل طاقة النيوترون. وارتفاعه مساحة هدف بوحدة <b>البارن</b> (البارن الواحد 10<sup>−24</sup> cm²، وهو تقريبًا الحجم الذي تُظهره النواة للنيوترون). ولأن الذرات تتحرك، يلاقي بعضها النيوترون وجهًا لوجه ويهرب بعضها منه، فتتلطخ القمة الضيقة: أخفض وأعرض. ومساحتها تبقى كما هي.</p>
  <div class="ctl"><label for="dop-t2">درجة حرارة الوقود (K)</label><input id="dop-t2" type="range" data-bind="T" data-instant min="300" max="1500" step="10" value="1200"><output data-show="T" data-fmt="0"></output></div>
</div>
<div class="step">
  <h3>الحجب الذاتي للرنين</h3>
  <p>قرص الوقود سميك. النطاق المظلل هو حصة النيوترونات التي يوقفها عند كل طاقة. مركز القمة يوقف كل شيء أصلًا، ساخنًا كان أم باردًا، فلا تخسر القمة الأخفض شيئًا هناك؛ أما الجناحان الأعرض فيلتقطان أكثر. فيضيع عدد أكبر من النيوترونات في الأسر بدل أن يسبب انشطارًا، فتنخفض <i>k</i> من تلقاء نفسها. (<i>k</i> هي عدد الانشطارات الجديدة التي يؤدي إليها كل انشطار؛ يشرحها الفصل <a href="#critical">21</a>.)</p>
  <div class="ctl"><label for="dop-t3">درجة حرارة الوقود (K)</label><input id="dop-t3" type="range" data-bind="T" data-instant min="300" max="1500" step="10" value="900"><output data-show="T" data-fmt="0"></output></div>
</div>`
};
Object.assign(WT.L.labels, {
  "uranium atoms in the fuel": "ذرات اليورانيوم في الوقود",
  "{#} K": "{#} K",
  "caught in the peak": "مُلتقَط في القمة",
  "k": "k",
  "neutron energy (eV) →": "طاقة النيوترون (eV) →",
  "capture cross section": "المقطع العرضي للأسر",
  "peak {#}k barns · Doppler width {#} meV · area unchanged": "القمة {#} ألف بارن · عرض دوبلر {#} meV · المساحة ثابتة",
  "all stopped": "توقفت كلها",
  "wider wings catch more": "الجناحان الأعرض يلتقطان أكثر",
  "share of neutrons stopped in the fuel": "حصة النيوترونات الموقوفة في الوقود",
  "the peak's centre already stops everything; the wider wings catch more": "مركز القمة يوقف كل شيء أصلًا؛ والجناحان الأعرض يلتقطان أكثر",
});
