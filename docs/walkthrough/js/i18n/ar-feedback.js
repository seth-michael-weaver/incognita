/* Arabic: feedback (استقرار المفاعل والتغذية الراجعة) */
WT.L.ch.feedback = {
  num: "الدرس 1", title: "استقرار المفاعل والتغذية الراجعة", short: "التغذية الراجعة",
  html: `
<div class="step">
  <h3>حلقة: القدرة، الحرارة، التفاعلية</h3>
  <p>القدرة الأكبر تسخّن الوقود والماء، ودرجتا حرارتهما تغيّران التفاعلية <i>ρ</i>، وهي التي تحدد القدرة. أضف خطوة من التفاعلية وراقب الإشارة تدور في الحلقة. ومع المعاملات السالبة تدفع الحلقة في الاتجاه المعاكس.</p>
  <div class="ctl"><label for="fb-r">خطوة التفاعلية (pcm)</label><input id="fb-r" type="range" data-bind="rs" data-instant min="50" max="300" step="10" value="200"><output data-show="rs" data-fmt="0"></output></div>
  <div class="btns"><button class="btn" data-act="fbIns">أدخِل</button> <button class="btn ghost" data-act="fbRes">إعادة الضبط</button></div>
</div>
<div class="step">
  <h3>دوبلر: المكبح السريع</h3>
  <p>الوقود الأسخن يلتقط نيوترونات أكثر في اليورانيوم-238 دون انشطار (<a href="#doppler">توسّع دوبلر</a>). يسخن الوقود في ثوانٍ، فيعمل هذا المكبح أولًا، وهو في مفاعلات الماء سالب دائمًا. وهنا هو التغذية الراجعة الوحيدة.</p>
  <div class="ctl"><label for="fb-d">معامل دوبلر (pcm/K)</label><input id="fb-d" type="range" data-bind="aD" data-instant min="-5" max="-1" step="0.1" value="-2.5"><output data-show="aD" data-fmt="1"></output></div>
  <div class="btns"><button class="btn" data-act="fbIns">أدخِل</button> <button class="btn ghost" data-act="fbRes">إعادة الضبط</button></div>
</div>
<div class="step">
  <h3>المهدِّئ ينضم</h3>
  <p>الماء الأدفأ أقل كثافة، فيُبطئ النيوترونات بكفاءة أقل. وفي مفاعل الماء المضغوط عند مستويات البورون المعتادة يجعل هذا معامل المهدِّئ سالبًا أيضًا: مكبح ثانٍ أبطأ، فتستقر القدرة عند مستوى أدنى.</p>
  <div class="ctl"><label for="fb-m">معامل المهدِّئ (pcm/K)</label><input id="fb-m" type="range" data-bind="aM" data-instant min="-60" max="0" step="1" value="-30"><output data-show="aM" data-fmt="0"></output></div>
  <div class="btns"><button class="btn" data-act="fbIns">أدخِل</button> <button class="btn ghost" data-act="fbRes">إعادة الضبط</button></div>
</div>
<div class="step">
  <h3>حين تكون التغذية الراجعة موجبة</h3>
  <p>إذا كان حدّ المبرِّد موجبًا ويفوق دوبلر، فالقدرة الأكبر تعني تفاعلية أكبر فتنفلت القدرة. تُصمَّم مفاعلات الماء بمعاملات سالبة؛ وبعض التصاميم، مثل RBMK عند القدرة المنخفضة، قد يكون لها معامل فراغ موجب.</p>
  <div class="ctl"><label for="fb-c">معامل المبرِّد (pcm/K)</label><input id="fb-c" type="range" data-bind="aM" data-instant min="-60" max="150" step="5" value="150"><output data-show="aM" data-fmt="0"></output></div>
  <div class="btns"><button class="btn" data-act="fbIns">أدخِل</button> <button class="btn ghost" data-act="fbRes">إعادة الضبط</button></div>
</div>`,
};
Object.assign(WT.L.labels, {
  "heat": "حرارة",
  "heats water": "تسخّن الماء",
  "chain": "السلسلة",
  "chain reaction": "التفاعل المتسلسل",
  "αM +": "αM +",
  "αM −": "αM −",
  "αM {#}": "αM {#}",
  "αC +": "αC +",
  "αC −": "αC −",
  "αC {#}": "αC {#}",
  "αD −": "αD −",
  "P {#} %": "P {#} %",
  "fuel +{#} K": "الوقود +{#} K",
  "fuel {#} K": "الوقود {#} K",
  "fuel ΔT +{#} K": "الوقود ΔT +{#} K",
  "fuel ΔT {#} K": "الوقود ΔT {#} K",
  "water +{#} K": "الماء +{#} K",
  "water {#} K": "الماء {#} K",
  "water ΔT +{#} K": "الماء ΔT +{#} K",
  "water ΔT {#} K": "الماء ΔT {#} K",
  "ρ +{#} pcm": "ρ +{#} pcm",
  "ρ {#} pcm": "ρ {#} pcm",
  "ρ = ρext + αD ΔTf + αM ΔTm": "ρ = ρext + αD ΔTf + αM ΔTm",
  "C dT/dt = P − h (T − Tc)": "C dT/dt = P − h (T − Tc)",
  "Doppler α_D = {a} pcm/K": "دوبلر α_D = {a} pcm/K",
  "coolant α_C = {a} pcm/K": "المبرِّد α_C = {a} pcm/K",
  "moderator α_M = {a} pcm/K": "المهدِّئ α_M = {a} pcm/K",
  "inserted ρ_ext = {a}": "المُدخَل ρ_ext = {a}",
  "+{a} pcm": "+{a} pcm",
  "power": "القدرة",
  "last {#} s →": "آخر {#} s →",
  "last {#} seconds →": "آخر {#} ثانية →",
  "power ran away · protection would shut it down": "انفلتت القدرة · الحماية كانت ستوقفه",
  "power ran away · in a real plant the protection system would shut it down": "انفلتت القدرة · في محطة حقيقية كان نظام الحماية سيوقف المفاعل",
  "steady at {#} % · press Insert": "مستقر عند {#} % · اضغط أدخِل",
  "steady at {#} % power · press Insert to add reactivity": "مستقر عند {#} % من القدرة · اضغط أدخِل لإضافة تفاعلية",
  "power coefficient {a} pcm per {#} %: settles": "معامل القدرة {a} pcm لكل {#} %: يستقر",
  "power coefficient {a} pcm per {#} % power: self-stabilising": "معامل القدرة {a} pcm لكل {#} % من القدرة: استقرار ذاتي",
  "power coefficient +{a} pcm per {#} %: runs away": "معامل القدرة +{a} pcm لكل {#} %: تنفلت",
  "power coefficient +{a} pcm per {#} % power: runs away": "معامل القدرة +{a} pcm لكل {#} % من القدرة: تنفلت",
  "illustrative model": "نموذج توضيحي",
});
