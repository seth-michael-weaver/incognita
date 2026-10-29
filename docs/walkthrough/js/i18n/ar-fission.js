/* Arabic: fission (chapter 9) */
WT.L.ch.fission = {
  num: "الفصل 12", title: "الانشطار", short: "الانشطار",
  lead: "للأنوية الأثقل مخرج تفتقر إليه الأنوية الخفيفة: فبدلًا من أن تقذف جسيمًا، تنكسر النواة كلها إلى قسمين. هذا هو الانشطار.",
  html: `
<div class="step">
  <p>تتصرف النواة الثقيلة كقطرة من سائل مشحون. يحافظ التوتر السطحي (الأسهم الرمادية) على استدارتها، بينما تدفعها البروتونات، وكلها موجبة الشحنة، إلى التفكك (الأسهم الحمراء). في اليورانيوم تكاد القوتان تتوازنان.</p>
  <div class="ctl"><label for="fis-d">مُطّ القطرة</label><input id="fis-d" type="range" data-bind="def" min="0" max="1" step="0.01" value="0"><output data-show="def" data-fmt="2"></output></div>
  <p>اسحب لتمطّها وراقب النقطة على منحنى الطاقة الصغير في الأسفل. المطّ يزيد السطح، وهذا يكلّف طاقة، لكنه يوزّع الشحنة على مسافة أكبر، وهذا يحرّر طاقة. بعد تجاوز قمة المنحنى تنتصر الشحنة: يتكوّن عنق وينطلق النصفان بطاقة تقارب 200 MeV.</p>
</div>
<div class="step">
  <h3>سطح الطاقة الكامنة</h3>
  <p>المنحنى هو الطاقة لكل شكل، من الشكل المستدير (يسارًا) إلى الشكل المنقسم (يمينًا). تعطي القطرة السائلة الملساء تلًّا واحدًا، لكن النيوكليونات تملأ مستويات الطاقة على شكل مجموعات تُسمّى <b>القشرات</b>، وفي أثقل العناصر يحفر هذا بئرًا في التل: <b>حاجز ذو سنامين</b>، يمكن للنواة أن تبقى فيه مدة بشكل ممطوط.</p>
  <p>لا يفترض المحرك هذا المنحنى افتراضًا: بل يقرؤه نقطةً نقطة من حساب مجهري للطاقة عند كل تشوه (درجة المطّ).</p>
</div>
<div class="step">
  <h3>النفاذ عبر الحاجز</h3>
  <p>الكرة هي النواة المثارة في الوادي الأول، عند طاقة الإثارة المبيّنة بالخط البرتقالي المتقطع، تحت القمة البالغة 6 MeV. وفق الفيزياء الكلاسيكية لا يمكنها العبور أبدًا؛ أما ميكانيكا الكم فتسمح لها باختراق الجزء الأغمق المحظور عبر <b>النفق الكمومي</b>، باحتمال <i>T</i> يتناقص أسّيًا كلما ازداد ذلك الجزء سُمكًا.</p>
  <div class="ctl"><label for="fis-e">طاقة الإثارة</label><input id="fis-e" type="range" data-bind="E" min="3" max="8" step="0.05" value="5"><output data-show="E" data-fmt="2"></output></div>
  <p>ارفع الطاقة وراقب كيف يكبر <i>T</i> مع ترقّق الجزء المحظور. الاختصار المعروف في الكتب الدراسية (هيل–ويلر) يعامل القمة كقطع مكافئ (الأزرق المتقطع). أما المحرك فيتبع الشكل الحقيقي، الأعرض في الأسفل، لذا يكون احتماله أصغر عند الطاقات البعيدة تحت القمة. يقيس <i>K</i> مقدار التل الواقع في الطريق.</p>
  <div class="formula">T = 1 / (1 + e<sup>2K</sup>),  K = ∫ √(2μ(V−E)) dβ / ħ</div>
</div>
<div class="step">
  <h3>حالات الانتقال</h3>
  <p>البوابات عند القمة هي <b>حالات الانتقال</b>، أي الحالات الكمومية للنواة الممطوطة فوق الحاجز. لكلٍّ منها سبين وتماثل (0⁺، 2⁻، …) وتعمل كبوابة؛ وتدل فتحتها المضيئة على مدى انفتاحها. لا تمر النواة إلا عبر البوابات التي لها السبين والتماثل نفساهما، وتنفتح كل بوابة تدريجيًا كلما تجاوزت الطاقة ارتفاعها.</p>
  <div class="ctl"><label for="fis-e2">طاقة الإثارة</label><input id="fis-e2" type="range" data-bind="E" min="3" max="8" step="0.05" value="5"><output data-show="E" data-fmt="2"></output></div>
  <div class="btns"><button class="btn ghost" data-act="jpAll">أي سبين</button><button class="btn ghost" data-act="jp0">نواة مركبة 0⁺</button><button class="btn ghost" data-act="jp1">نواة مركبة 1⁻</button></div>
  <p>اختر سبينًا وتماثلًا: لا تُحسب إلا البوابات المطابقة، فينخفض الانفتاح الكلي. وعند طاقات أعلى تتزاحم البوابات في <b>متصل</b>، فيعدّها المحرك بكثافتها، كما يفعل مع المستويات العادية.</p>
</div>
<div class="step">
  <h3>حواجز ثنائية السنام</h3>
  <p>الآن التلّان معًا، ولكلٍّ منهما بوابته (الدائرة؛ يدل جزؤها المملوء على مدى انفتاحها). تصل الأنوية من اليسار؛ وما يعبر منها التل الأول يُحتجز في البئر، ويرتد بين البوابتين حتى يخرج من أحد الجانبين. تتركب الاحتمالات كما تتركب المقاومات على التوالي، لذا فإن التل الأصعب هو صاحب الكلمة الأكبر.</p>
  <div class="ctl"><label for="fis-b">ارتفاع التل الخارجي</label><input id="fis-b" type="range" data-bind="Bb" min="3.5" max="7.5" step="0.05" value="5.6"><output data-show="Bb" data-fmt="2"></output></div>
  <div class="formula">1/T = 1/T<sub>A</sub> + 1/T<sub>B</sub></div>
  <p>ارفع التل الخارجي وراقب كيف يختنق التدفق نحو الانشطار، مهما كانت البوابة الداخلية مفتوحة.</p>
</div>
<div class="step">
  <h3>الانشطار متعدد الفرص</h3>
  <p>يمتص اليورانيوم-238 النيوترون فيصبح يورانيوم-239 بطاقة إثارة <i>E</i>* (الخط المتقطع). إن لم ينشطر، فقد يُطلق نيوترونًا؛ فينخفض الخط، ويحاول اليورانيوم-238 المتبقي، وهو ما زال ساخنًا، عبور حاجزه الخاص: انشطار <b>الفرصة الثانية</b>، (n,n′f). تجمع الأكوام الطريقة التي انتهت بها كل نواة.</p>
  <div class="ctl"><label for="fis-en">طاقة النيوترون</label><input id="fis-en" type="range" data-bind="En" min="0" max="25" step="0.1" value="7"><output data-show="En" data-fmt="1"></output></div>
  <p>ارفع الطاقة فتبدأ المحاولات اللاحقة بالنجاح؛ وتنفتح فرصة ثالثة قرب 12 MeV. تظهر كل فرصة جديدة كدرجة في <b>المقطع العرضي للانشطار</b> المقيس، أي احتمال أن تنشطر النواة: يرسم الرسم الصغير في أعلى اليمين هذه الدرجات مع تعليم طاقتك. يحسب المحرك عدد مرات الانشطار، لا الشظايا التي تنتج عنه.</p>
  <div class="aside">في الشيفرة: <code>fission/wkb.py</code> (مسار طاقة التشوه وتكاملات WKB)، <code>fission/barriers.py</code> (هيل–ويلر، حالات الانتقال، كثافة المستويات عند الحاجز)، <code>fission/transmission.py</code> (السنامان على التوالي، T<sub>fis</sub> لكل سبين وتماثل)، <code>fission/chain.py</code> (الحواجز لكل نواة في الشلال).</div>
</div>`,
};
Object.assign(WT.L.labels, {
  // drop
  "surface tension pulls it round": "التوتر السطحي يجعلها مستديرة",
  "the protons push it apart": "البروتونات تدفعها للتفكك",
  "a charged drop, nearly round": "قطرة مشحونة، شبه مستديرة",
  "stretched: more surface, charge further apart": "ممطوطة: سطح أكبر، وشحنة أكثر تباعدًا",
  "a neck forms": "يتكوّن عنق",
  "two fragments, carrying about {#} MeV": "شظيتان، تحملان نحو {#} MeV",
  "energy of the drop": "طاقة القطرة",
  // landscape
  "ground state": "الحالة الأرضية", "inner barrier": "الحاجز الداخلي", "second well": "البئر الثانية",
  "outer barrier": "الحاجز الخارجي", "split (scission)": "الانقسام (الانفصال)", "one smooth hill": "تل أملس واحد",
  "shell effects carving the second well": "تأثيرات القشرة تحفر البئر الثانية",
  "round → stretched → necked → split": "مستديرة ← ممطوطة ← بعنق ← منقسمة",
  "stretch (deformation) →": "المطّ (التشوه) →",
  // tunnel
  "forbidden zone": "المنطقة المحظورة",
  "excitation {#} MeV": "الإثارة {#} MeV",
  "hilltop {#} MeV": "القمة {#} MeV",
  "parabola fit": "ملاءمة القطع المكافئ",
  "passes over the top": "تمر فوق القمة",
  // gates
  "continuum: a density": "المتصل: كثافة",
  "continuum of gates: counted as a density": "متصل من البوابات: يُعدّ ككثافة",
  "gates: transition states": "البوابات: حالات الانتقال",
  "E = {#} MeV": "E = {#} MeV",
  "all gates: total opening {#}": "كل البوابات: الانفتاح الكلي {#}",
  "all gates: total opening {#} + {#} from the continuum": "كل البوابات: الانفتاح الكلي {#} + {#} من المتصل",
  "{#}⁺ gates only: total opening {#}": "بوابات {#}⁺ فقط: الانفتاح الكلي {#}",
  "{#}⁺ gates only: total opening {#} + {#} from the continuum": "بوابات {#}⁺ فقط: الانفتاح الكلي {#} + {#} من المتصل",
  "{#}⁻ gates only: total opening {#}": "بوابات {#}⁻ فقط: الانفتاح الكلي {#}",
  "{#}⁻ gates only: total opening {#} + {#} from the continuum": "بوابات {#}⁻ فقط: الانفتاح الكلي {#} + {#} من المتصل",
  // series
  "nuclei arriving →": "أنوية تصل →",
  "trapped in the well": "محتجزة في البئر",
  "fission": "الانشطار",
  "so far: {#} through, {#} turned back": "حتى الآن: عبر {#}، وارتد {#}",
  // chance
  "²³⁹U*  E* = {#} MeV": "²³⁹U*  E* = {#} MeV", "²³⁸U*  E* = {#} MeV": "²³⁸U*  E* = {#} MeV", "²³⁷U*  E* = {#} MeV": "²³⁷U*  E* = {#} MeV",
  "↑ E* above the picture": "↑ E* فوق حدود الرسم",
  "fission!": "انشطار!",
  "emits a neutron, cools, tries again": "تُطلق نيوترونًا، تبرد، وتحاول مجددًا",
  "too cool to split: a photon, no fission": "أبرد من أن تنشطر: فوتون، بلا انشطار",
  "attempt {#}: barrier {#} % open": "المحاولة {#}: الحاجز مفتوح {#} %",
  "{#}st chance (n,f)": "الفرصة {#} (n,f)", "{#}nd chance (n,n′f)": "الفرصة {#} (n,n′f)", "{#}rd chance (n,{#}nf)": "الفرصة {#} (n,{#}nf)",
  "{#}st (n,f)": "الفرصة {#} (n,f)", "{#}nd (n,n′f)": "الفرصة {#} (n,n′f)", "{#}rd (n,{#}nf)": "الفرصة {#} (n,{#}nf)",
  "no fission": "بلا انشطار",
});
// labels carrying a transmission T, printed either as 0.12 or as 3.4·10⁻5 (two number shapes)
(function () {
  const L = WT.L.labels, F = ["{#}", "{#}·{#}⁻{#}"];
  for (const a of F) {
    L[`inner gate T ≈ ${a}`] = `البوابة الداخلية T ≈ ${a}`;
    L[`outer gate T ≈ ${a}`] = `البوابة الخارجية T ≈ ${a}`;
    L[`both hills: T ≈ ${a}, {#} % of what arrives gets through`] = `التلّان معًا: T ≈ ${a}، يعبر {#} % مما يصل`;
    for (const b of F) {
      L[`T ≈ ${a} real shape · ${b} parabola`] = `T ≈ ${a} الشكل الحقيقي · ${b} القطع المكافئ`;
      L[`chance to tunnel T ≈ ${a} on the real shape, ${b} on the parabola`] = `احتمال النفق T ≈ ${a} للشكل الحقيقي، ${b} للقطع المكافئ`;
    }
  }
})();
