/* Arabic: structure (الفصل 1، مِمَّ تتكون النواة) */
WT.L.ch.structure = {
  num: "الفصل 1", title: "مِمَّ تتكون النواة", short: "البنية",
  lead: "قبل أن يطلق المحرك (برنامجنا لحساب التفاعلات) نيوترونًا واحدًا، يحتاج إلى وصف للنواة الهدف: ما مدى تماسكها، وما حالات الطاقة التي يمكن أن تكون فيها، وما شكلها.",
  html: `
<div class="step">
  <p>تُظهر الصورة نواة حديد: كرة متراصة من <em class="p">البروتونات</em> و<em class="n">النيوترونات</em> (<b>النيوكليونات</b>)، تربطها <b>القوة النووية الشديدة</b> القصيرة المدى جدًا. لا يشعر كل نيوكليون إلا بجيرانه الأقرب، ولذلك تكون كثافة الأنوية كلها متقاربة.</p>
  <div class="ctl"><label for="st-n">النيوترونات (في الحديد 26 بروتونًا)</label><input id="st-n" type="range" data-bind="N" min="24" max="38" step="1" value="30" data-instant><output data-show="N" data-fmt="0"></output></div>
  <p>اسحب لإضافة نيوترونات أو إزالتها؛ فكل اختيار <b>نظير</b> مختلف. تُظهر الأعمدة <b>طاقة الربط</b> لكل نيوكليون بوحدة MeV (مليون إلكترون فولت): أي الطاقة اللازمة لتفكيك النواة. وتبلغ أقصاها قرب النظائر المستقرة.</p>
</div>
<div class="step">
  <h3>كلفة انتزاع جسيم واحد</h3>
  <p>الطاقة اللازمة لانتزاع جسيم هي <b>طاقة الفصل</b> الخاصة به: <i>S<sub>n</sub></i> للنيوترون، و<i>S<sub>p</sub></i> للبروتون، و<i>S<sub>α</sub></i> لـ<b>جسيم ألفا</b> (بروتونان ونيوترونان مرتبطة معًا). تعرض الصورة النواة على شكل بئر، والطاقة نحو الأعلى؛ كل عملية انتزاع ترفع الجسيم الأعلى إلى ما وراء الخط المتقطع «حر»، ويسجّل العدّاد الكلفة.</p>
  <div class="btns"><button class="btn ghost" data-act="pn">انتزع نيوترونًا</button><button class="btn ghost" data-act="pp">انتزع بروتونًا</button><button class="btn ghost" data-act="pa">انتزع جسيم ألفا</button></div>
  <p>يحصل المحرك على كل منها بوصفها الفرق بين كتلتين نوويتين: مقيستين حيث أمكن، ومن نموذج للكتل حيث لا يمكن.</p>
  <div class="ctl"><label for="st-n2">النيوترونات</label><input id="st-n2" type="range" data-bind="N" min="24" max="38" step="1" value="30" data-instant><output data-show="N" data-fmt="0"></output></div>
  <p>اسحب عدد النيوترونات وانتزع نيوترونًا مرة أخرى: ترتفع <i>S<sub>n</sub></i> وتنخفض بشكل متعرج، لأن النيوكليونات تتزاوج، وعندما يكون العدد زوجيًا يكون آخرها أشد ارتباطًا. لا يستطيع تفاعلٌ أن يطرد جسيمًا إلا إذا وفّر طاقة كافية لدفع هذه الكلفة. وهذه الكلف هي <b>العتبات</b> في الحساب كله.</p>
</div>
<div class="step">
  <h3>مستويات الطاقة، والهبوط</h3>
  <p>لا تستطيع النواة أن تختزن إلا مقادير محددة بدقة من الطاقة الإضافية: هي الخطوط، المعروضة هنا للحديد-56، و<b>الحالة الأرضية</b> في الأسفل. لكل مستوى <b>سبين</b> <i>J</i> (زخم زاوي) و<b>تماثل</b>، + أو − (هل تبدو موجته كما هي في المرآة)؛ فالرمز 2<sup>+</sup> يعني سبين 2 وتماثل +.</p>
  <p>الكرة البرتقالية نواة في مستوى مرتفع. تهبط مستوى بعد مستوى، وكل قفزة تُطلق <em class="g">فوتونًا</em> (شعاع غاما) يحمل فرق الطاقة. سُمك المسارات ونسبتها المئوية هما الاحتمالات المقيسة لكل قفزة، أي <b>نسب التفرع</b>.</p>
  <div class="btns"><button class="btn" data-act="drop">أثِر النواة</button></div>
  <p>اضغطه عدة مرات: يصل المستوى نفسه إلى الحالة الأرضية عبر طرق مختلفة. يحفظ المحرك نحو ثلاثين مستوى مقيسًا لكل نواة مع احتمالاتها؛ وأعلى من ذلك يعامل المستويات المتزاحمة على أنها <b>متصل</b> أملس. فوق الخط المتقطع <i>S<sub>n</sub></i> يمكن للنواة أن تطلق نيوترونًا.</p>
</div>
<div class="step">
  <h3>مستوى بلا مخرج سهل</h3>
  <p>المستوى الذي لا مخرج له إلا بتغيّر كبير في السبين، Δ<i>J</i>، يضمحل ببطء شديد. على اليمين 64 نواة في مستوى كهذا؛ تنتظر كل منها زمنًا عشوائيًا، ثم تهبط ويخرج <em class="g">فوتون</em>. وبعد انقضاء <b>عمر النصف</b> يكون نصفها قد هبط.</p>
  <div class="ctl"><label for="st-dj">تغيّر السبين ΔJ</label><input id="st-dj" type="range" data-bind="dJ" min="1" max="5" step="1" value="2" data-instant><output data-show="dJ" data-fmt="0"></output></div>
  <div class="ctl"><label for="st-eg">طاقة الفوتون (MeV)</label><input id="st-eg" type="range" data-bind="Eg" min="0.05" max="1.5" step="0.05" value="0.3"><output data-show="Eg" data-fmt="2"></output></div>
  <div class="btns"><button class="btn ghost" data-act="excite">أثِرها جميعًا</button></div>
  <p>ارفع Δ<i>J</i> فتخرج الفوتونات أبطأ: كل وحدة سبين إضافية تجعل الانتظار أطول بمئة ألف مرة أو أكثر، وطاقة الفوتون الأصغر تطيله أيضًا (على مقياس لوغاريتمي). المستوى الذي يعيش أكثر من ثانية تقريبًا هو <b>أيزومر</b>، ويعامله المحرك نقطةَ نهاية، مثل الحالة الأرضية تمامًا.</p>
</div>
<div class="step">
  <h3>كروية أم لا</h3>
  <p>كثير من الأنوية ليست كروية. يقيس <i>β₂</i> («بيتا اثنان») مقدار الاستطالة: 0 كرة، والقيمة الموجبة استطالة مثل كرة القدم الأمريكية، والسالبة تفلطح مثل القرص. يُظهر السلّم على اليمين المستويات التي ينتجها كل نوع.</p>
  <p>النواة المستطيلة تستطيع الدوران، فتعطي المستويات 0<sup>+</sup> و2<sup>+</sup> و4<sup>+</sup> و6<sup>+</sup> بفواصل تكبر مثل <i>J</i>(<i>J</i>+1): إنها <b>نواة دوّارة</b>. أما النواة الكروية فتستطيع أن تتموج؛ وكل وحدة تموّج، أي <b>فونون</b>، تضيف الطاقة نفسها، فتكون مستوياتها متساوية التباعد: إنها <b>نواة مهتزة</b>.</p>
  <div class="ctl"><label for="st-beta">التشوه β₂</label><input id="st-beta" type="range" data-bind="beta" min="-0.3" max="0.45" step="0.01" value="0.28"><output data-show="beta" data-fmt="2"></output></div>
  <div class="btns"><button class="btn ghost" data-act="still">ساكنة</button><button class="btn ghost" data-act="vib">مهتزة</button><button class="btn ghost" data-act="rot">دوّارة</button></div>
  <p>اسحب <i>β₂</i> واضغط الأزرار: كلما زادت الاستطالة تقاربت مستويات النواة الدوارة أكثر. يحفظ المحرك قيم التشوه لكل نواة ووسمًا: كروية أو مهتزة أو دوّارة. ويبيّن الفصل 6 كيف يستخدمها نيوترون عابر.</p>
</div>
<div class="step">
  <h3>بصمات فوق العتبة مباشرة</h3>
  <p>النيوترون البطيء الذي يندمج مع الهدف يستقر فوق <i>S<sub>n</sub></i> مباشرة، في الصندوق الصغير على اليسار. وتكبّر اللوحة على اليمين ذلك الصندوق آلاف المرات، وطاقة النيوترون فيها من اليسار إلى اليمين.</p>
  <div class="ctl"><label for="st-fe">طاقة الحزمة</label><input id="st-fe" type="range" data-bind="fe" min="0" max="1" step="0.001" value="0.3" data-instant><output id="st-fe-out"></output></div>
  <div class="btns"><button class="btn ghost" data-act="fplay" id="st-fplay">أوقف المسح مؤقتًا</button></div>
  <p>عند معظم الطاقات تعبر الحزمة دون أن يحدث شيء. أما عند طاقات محددة بدقة، فيوافق النيوترونُ مع النواة مستوى مخفيًا، ويُؤسر جزء كبير من الحزمة: إنه <b>الرنين</b>. عند القمة تنتفخ النواة المرسومة: لا يتغير حجمها الحقيقي، بل هو الهدف الأكبر الذي «يراه» النيوترون فعليًا حين تتراكب موجته مع موجة النواة. ثم تعيد النواة الطاقة على شكل <em class="g">فوتون</em> أو نيوترون. يُظهر المنحنى الكسر المأسور؛ وتعلّم الأعمدة كل رنين يُعثر عليه.</p>
  <div class="btns"><button class="btn ghost" data-act="fFe">الحديد-56</button><button class="btn ghost" data-act="fAu">الذهب-197</button><button class="btn ghost" data-act="fU">اليورانيوم-238</button></div>
  <p>لكل نواة شيفرة أعمدة خاصة بها، وبمقياسها الخاص: آلاف الإلكترون فولت بين رنينات الحديد، وعشرات في الذهب واليورانيوم. وتلخصها ثلاثة متوسطات: <i>D₀</i>، أي متوسط التباعد؛ و⟨Γ<sub>γ</sub>⟩، أي <b>العرض الفوتوني</b>، وهو متقارب في جميع القمم؛ و<i>S₀</i>، أي <b>دالة القوة</b>، وتعبّر عن سهولة دخول نيوترون بطيء.</p>
  <p>كل منها يختبر خطوة لاحقة. فقد ضُبطت بارامترات كثافة المستويات في المحرك على <i>D₀</i>، نواةً نواة؛ ويختبر ⟨Γ<sub>γ</sub>⟩ انبعاث الفوتونات، ويختبر <i>S₀</i> النموذج البصري في الفصل التالي. وللأنوية غير المقيسة، يستخدم المحرك اتجاهات مضبوطة على أنوية كثيرة.</p>
  <div class="aside">في الشيفرة: <code>structure/masses.py</code> (الكتل المقيسة، وكتل النموذج فيما وراءها، وطاقات الفصل)، <code>structure/levels.py</code> (المستويات المنفصلة، والتفرعات، والأيزومرات، والسبينات المقدّرة) و<code>levjpar.py</code> (اختياري، ومعطّل افتراضيًا: يعيد تقدير سبين في القائمة يستحيل على تلك النواة)، <code>structure/deformation.py</code> (β₂ ووسم كروية/مهتزة/دوّارة) و<code>collrule.py</code> (اختياري، ومعطّل افتراضيًا: يختار وسم الهدف من مستوياته المقيسة)، <code>structure/resonances.py</code> (D₀ وS₀ وS₁ و⟨Γγ⟩).</div>
</div>`,
};
(function () {
  const L = {
    // scene: packed drop
    "{#}Fe": "{#}Fe",
    "{#} protons · {#} neutrons": "{#} بروتون · {#} نيوترون",
    "binding energy per nucleon: about {#} MeV": "طاقة الربط لكل نيوكليون: نحو {#} MeV",
    "binding per nucleon, one bar per isotope →": "الربط لكل نيوكليون، عمود لكل نظير →",
    // scene: well
    "free": "حر",
    "free: outside the nucleus": "حر: خارج النواة",
    "neutrons": "نيوترونات",
    "protons": "بروتونات",
    "an alpha forms from the top pairs": "الأزواج العليا تكوّن جسيم ألفا",
    "neutron {#}": "نيوترون {#}",
    "proton {#}": "بروتون {#}",
    "alpha {#}": "ألفا {#}",
    "n {#}": "n {#}",
    "p {#}": "p {#}",
    "energy paid": "الطاقة المدفوعة",
    "energy to pull": "طاقة الانتزاع",
    "(MeV)": "(MeV)",
    "each one out (MeV)": "لكل جسيم (MeV)",
    "higher mark =": "علامة أعلى =",
    "harder to remove": "انتزاع أصعب",
    "pulling out a neutron: {#} MeV paid": "انتزاع نيوترون: دُفع {#} MeV",
    "pulling out a proton: {#} MeV paid": "انتزاع بروتون: دُفع {#} MeV",
    "pulling out an alpha: {#} MeV paid": "انتزاع جسيم ألفا: دُفع {#} MeV",
    // scene: levels and gamma drops
    "continuum: too many levels to list": "المتصل: مستويات أكثر من أن تُحصى",
    "neutron threshold Sₙ ≈ {#} MeV": "عتبة النيوترون Sₙ ≈ {#} MeV",
    "ground state": "الحالة الأرضية",
    "MeV": "MeV",
    "each line: an energy, a spin J and a parity (±)": "كل خط: طاقة وسبين J وتماثل (±)",
    "path width and % = measured odds of each hop": "سُمك المسار و% = الاحتمال المقيس لكل قفزة",
    // scene: isomer
    "ground": "الأرضية",
    "J = {#}/{#}": "J = {#}/{#}",
    "ΔJ = {#}": "ΔJ = {#}",
    "still excited: {#} of {#}": "ما زالت مثارة: {#} من {#}",
    "longer than a second: an isomer, a stop in its own right": "أكثر من ثانية: أيزومر، محطة قائمة بذاتها",
    "shown slowed down (log scale)": "معروض بالحركة البطيئة (مقياس لوغاريتمي)",
    "shown slowed down: the slower they pop, the longer the real wait (log scale)": "بالحركة البطيئة: كلما أبطأت، طال الانتظار الحقيقي (مقياس لوغاريتمي)",
    // scene: shape
    "ripples at the surface: a vibrator": "تموجات على السطح: نواة مهتزة",
    "stretched and rotating: a rotor": "مستطيلة ودوّارة: نواة دوّارة",
    "round: a sphere": "مستديرة: كرة",
    "stretched (prolate): a football": "مستطيلة (متطاولة): ككرة القدم",
    "squashed: an oblate disc": "مفلطحة: قرص",
    "{#} phonons": "{#} فونون",
    "no regular": "لا نمط",
    "level pattern": "منتظم للمستويات",
    "spacing grows like J(J+{#})": "التباعد يكبر مثل J(J+{#})",
    "equal steps, one phonon each": "خطوات متساوية، فونون لكل منها",
    "its lowest levels": "أدنى مستوياتها",
    "β₂ = {#}": "β₂ = {#}",
    // scene: resonance fingerprint
    "continuum": "المتصل",
    "Sₙ ≈ {#} MeV": "Sₙ ≈ {#} MeV",
    "slow neutron": "نيوترون بطيء",
    "a slow neutron lands here:": "يستقر نيوترون بطيء هنا:",
    "lands here": "يستقر هنا",
    "Sₙ + its kinetic energy": "Sₙ + طاقته الحركية",
    "×{#} million": "×{#} مليون",
    "×{#} thousand": "×{#} ألف",
    "magnified": "مكبَّر",
    "swells on a peak: the size the neutron effectively “sees” (waves overlap), not a real size change": "تنتفخ عند القمة: الحجم الذي «يراه» النيوترون فعليًا (تراكب الموجات)، لا تغيّر حقيقي في الحجم",
    "share taken in": "الكسر المأسور",
    "share of the beam taken in": "كسر الحزمة المأسور",
    "{#} (Sₙ)": "{#} (Sₙ)",
    "{#} = exactly Sₙ": "{#} = Sₙ تمامًا",
    "{#} keV": "{#} keV",
    "{#} eV": "{#} eV",
    "neutron energy →": "طاقة النيوترون →",
    "neutron's kinetic energy →": "الطاقة الحركية للنيوترون →",
    "D₀ ≈ {#} keV: the average gap": "D₀ ≈ {#} keV: متوسط التباعد",
    "D₀ ≈ {#} eV: the average gap": "D₀ ≈ {#} eV: متوسط التباعد",
    "S₀: average peak strength": "S₀: متوسط شدة القمم",
    "S₀: how strong the peaks are on average (how easily a neutron gets in)": "S₀: متوسط شدة القمم (مدى سهولة دخول النيوترون)",
    "⟨Γγ⟩ ≈ {#} eV: photon width": "⟨Γγ⟩ ≈ {#} eV: العرض الفوتوني",
    "⟨Γγ⟩ ≈ {#} eV: photon width, about the same for every peak": "⟨Γγ⟩ ≈ {#} eV: العرض الفوتوني، متقارب في كل القمم",
    "⟨Γγ⟩ ≈ {#} eV: a hairline here": "⟨Γγ⟩ ≈ {#} eV: خط رفيع هنا",
    "⟨Γγ⟩ ≈ {#} eV: a hairline here; neutrons widen these peaks": "⟨Γγ⟩ ≈ {#} eV: خط رفيع هنا؛ النيوترونات توسّع هذه القمم",
    "peaks drawn about {#}× wider than life so they show": "القمم مرسومة أعرض بنحو {#}× من الواقع لتظهر",
  };
  // beam readout and per-target labels
  for (const u of ["keV", "eV"]) L[`beam of neutrons at {#} ${u}`] = `حزمة نيوترونات عند {#} ${u}`;
  const EL = { iron: "الحديد", gold: "الذهب", uranium: "اليورانيوم" };
  for (const en in EL) {
    L[`${en}{#} levels`] = `مستويات ${EL[en]}{#}`;
    L[`${en}{#}: took in {#} of the last {#}`] = `${EL[en]}{#}: أسر {#} من آخر {#}`;
  }
  // isomer half-life in every unit fmtTime can produce
  const TU = { femtoseconds: "فمتوثانية", picoseconds: "بيكوثانية", nanoseconds: "نانوثانية", microseconds: "ميكروثانية",
    milliseconds: "ملي ثانية", seconds: "ثانية", minutes: "دقيقة", hours: "ساعة", days: "يوم", years: "سنة" };
  for (const en in TU) L[`half-life about {#} ${en}`] = `عمر النصف نحو {#} ${TU[en]}`;
  L["half-life about {#}×{#}^{#} years"] = "عمر النصف نحو {#}×{#}^{#} سنة";
  Object.assign(WT.L.labels, L);
})();
