/* Arabic: critical (الفصل 21، الحرجية والتحكم في المفاعل) */ // [i18n check parity with English JS helper: data-act="delayed" data-act="delayed"]
WT.L.ch.critical = {
  num: "الفصل 21", title: "الحرجية والتحكم في المفاعل", short: "الحرجية",
  html: `
<div class="step">
  <h3>معامل التضاعف</h3>
  <p>يحرّر كل انشطار بضعة نيوترونات؛ بعضها يسبب الانشطارات التالية، والباقي يضيع. <b>معامل التضاعف</b> <i>k</i> هو عدد الانشطارات الجديدة التي يؤدي إليها انشطار واحد: كل جيل يضرب عدد النيوترونات في <i>k</i>. فوق 1 تنمو السلسلة، وتحت 1 تتلاشى.</p>
  <div class="ctl"><label for="cri-k">معامل التضاعف k</label><input id="cri-k" type="range" data-bind="k" data-instant min="0.95" max="1.05" step="0.05" value="1.05"><output data-show="k" data-fmt="2"></output></div>
</div>
<div class="step">
  <h3>النيوترونات المتأخرة</h3>
  <p>تصل حصة صغيرة من النيوترونات (0.65 %) متأخرة ثوانيَ، من شظايا انشطار تضمحل أولًا. وهذه النيوترونات المتأخرة تضبط الإيقاع، فيتباطأ النمو من لمح البصر إلى دقائق. المنحنى يجري بسرعة ×10.</p>
  <div class="ctl"><label for="cri-k2">معامل التضاعف k</label><input id="cri-k2" type="range" data-bind="kd" data-instant min="0.998" max="1.002" step="0.0005" value="1.001"><output data-show="kd" data-fmt="4"></output></div>
  <div class="btns"><button class="btn ghost" data-act="delayed" aria-pressed="true">النيوترونات المتأخرة</button></div>
</div>
<div class="step">
  <h3>الحرجية</h3>
  <p>تجربة حرجة: حرّك قضبان التحكم حتى تبقى القدرة ثابتة. عند هذا الوضع تكون <i>k</i> تساوي 1 تمامًا، وموضع القضبان هذا هو القياس. اعثر عليه: تعرض القراءة <i>k</i> بخمس منازل عشرية.</p>
  <div class="ctl"><label for="cri-rod">القضبان المُدخلة (%)</label><input id="cri-rod" type="range" data-bind="ins" data-instant min="35" max="75" step="1" value="45"><output data-show="ins" data-fmt="0"></output></div>
</div>`
};
Object.assign(WT.L.labels, {
  "generations →": "الأجيال →",
  "k = {#}: dies away": "k = {#}: تتلاشى",
  "k = {#}: steady": "k = {#}: ثابت",
  "k = {#}: grows": "k = {#}: تنمو",
  "{#} generations last under {#} s in a water reactor": "{#} جيل تستغرق أقل من {#} s في مفاعل مائي",
  "illustration": "توضيح",
  "amber: fission fragments that emit a neutron seconds later": "الكهرماني: شظايا انشطار تطلق نيوترونًا بعد ثوانٍ",
  "{#} s": "{#} s",
  "time →": "الزمن →",
  "×{#} speed": "سرعة ×{#}",
  "with delayed: doubles every {#} s": "مع المتأخرة: تتضاعف كل {#} s",
  "prompt only: doubles every {#} ms": "الفورية فقط: تتضاعف كل {#} ms",
  "k = {#} · {#} % of neutrons delayed about {#} s (one-group average)": "k = {#} · {#} % من النيوترونات تتأخر نحو {#} s (متوسط مجموعة واحدة)",
  "rods {#} % in": "القضبان مُدخلة {#} %",
  "k = {#} · doubles every {#} min": "k = {#} · تتضاعف كل {#} دقيقة",
});
