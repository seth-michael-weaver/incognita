/* Arabic: static page text (index.html data-i18n keys) and kit UI strings */
Object.assign(WT.L.ui, {
  lang_label: "اللغة", nav_teach: "للمعلمين",
  brand: "داخل تفاعل نووي", nav_physics: "الفيزياء", nav_data: "كل النويدات", nav_board: "لوحة النتائج", menu: "القائمة", site_nav: "الموقع",
  ways_h: "طرق أخرى للدخول", ways_more: "أو تابع النزول: الفيزياء تبدأ من هنا ↓",
  way1_k: "استكشف", way1_t: "كل النويدات", way1_p: "مقاطع عرضية متنبأ بها لـ 6168 نويدة إلى جانب كل قياس منقّح. ابحث عن أي نظير واطّلع على كل مجموعة بيانات.", way1_go: "افتح البيانات ←",
  way2_k: "قارن", way2_t: "لوحة النتائج", way2_p: "كيف يُقارَن المحرك ومنتج بياناته بشيفرات التفاعلات والمكتبات الأخرى، بالحكم عليها مقابل القياسات، مع عرض الخسائر أولًا.", way2_go: "اطّلع على النتائج ←",
  way3_k: "شغّله", way3_t: "الشيفرة", way3_p: "كل ما هنا مفتوح المصدر. انسخ المستودع، أو اطّلع على أي منحنى، أو شغّل المحرك بنفسك.", way3_go: "GitHub ←",
  title: "داخل تفاعل نووي",
  kicker: "شرح تفاعلي لمحرك التفاعلات INCOGNITA",
  h1: "داخل تفاعل نووي",
  hero1: "أطلق نيوترونًا نحو نواة ذرية فيخرج منها شيء ما. قد يكون النيوترون نفسه وقد ارتد. وقد يكون بروتونًا، أو جسيم ألفا (عنقودًا متماسكًا من بروتونين ونيوترونين)، أو ومضة ضوء. بل قد تنقسم النواة الثقيلة إلى قسمين.",
  hero2: "أيّ هذه الأمور يحدث، وكم مرة؟ تشرح هذه الصفحة، خطوة بخطوة، كيف يجيب برنامجنا عن هذا السؤال. مرّر الصفحة إلى الأسفل وجرّب أدوات التحكم في طريقك. تتبع الرسوم الفيزياء نفسها التي يتبعها المحرك، أما الأرقام التي تعرضها فهي توضيحية.",
  scrollcue: "مرّر للبدء ↓",
  hero_tag: "نيوترون واحد. نواة واحدة. نهايات كثيرة.",
  hero_fire: "أطلق نيوترونًا",
  hero_hint: "أو انقر في أي مكان من الصورة",
  credit_idx: "محرك INCOGNITA نقلٌ برمجي لـ <a href=\"https://doi.org/10.1140/epja/s10050-023-01034-3\">TALYS-2</a> (A. J. Koning، S. Hilaire، S. Goriely) ويستخدم قاعدة بيانات البنية النووية الخاصة بـ TALYS. ما يضيفه INCOGNITA <a href=\"#code\">مُدرَج، مفتاحًا مفتاحًا، في آخر هذه الصفحة</a>.",
  coda_h2: "أين يوجد هذا في الشيفرة",
  coda_p1: "كل مرحلة مما سبق حزمة في <code>physics/hf</code>، ويستدعيها المحرك بالترتيب الذي قرأتها به للتو. المحرك نقلٌ برمجي لـ TALYS-2.x، شيفرة التفاعلات الراسخة. وما يضيفه موضوع خلف مفاتيح مسمّاة داخل الحزم نفسها: معظمها معطّل افتراضيًا، وبعض التصحيحات مفعّلة، ويمكن إرجاع كل منها على حدة إلى TALYS الأصلي.",
  coda_table: `
    <thead><tr><th>الفصل</th><th>ما يفعله</th><th>الشيفرة</th></tr></thead>
    <tbody>
      <tr><td><a href="#structure">1</a></td><td>الكتل، المستويات، التشوه، بيانات الرنين</td><td><code>structure/</code></td></tr>
      <tr><td><a href="#omp">2</a></td><td>النموذج البصري، معاملات النفاذ (مدى سهولة دخول الجسيمات وخروجها)</td><td><code>omp/</code></td></tr>
      <tr><td><a href="#direct">3</a></td><td>القنوات المقترنة، DWBA، الرنينات العملاقة، الأسر المباشر (اختياري)</td><td><code>ecis/</code>, <code>direct/</code></td></tr>
      <tr><td><a href="#preeq">4</a></td><td>ما قبل التوازن: نموذج الإكسيتونات، التقاط النيوكليونات والإطاحة بها، الانبعاث المتعدد</td><td><code>preeq/</code>, <code>density/particle_hole.py</code></td></tr>
      <tr><td><a href="#compound">5</a></td><td>كثافات المستويات (حالات لكل MeV)، توزيع السبين</td><td><code>density/</code></td></tr>
      <tr><td><a href="#decay">6</a></td><td>اختيار مخرج (هاوزر–فيشباخ)، تقلبات العرض</td><td><code>compound/</code></td></tr>
      <tr><td><a href="#gamma">7</a></td><td>دالة قوة غاما ونفاذ γ؛ المستويات المنفصلة والأيزومرات</td><td><code>gamma/</code><br><code>structure/levels.py</code></td></tr>
      <tr><td><a href="#cascade">8</a></td><td>شلال انبعاث الجسيمات وأشعة γ، القنوات الحصرية، النوى المتبقية</td><td><code>emission/</code></td></tr>
      <tr><td><a href="#fission">9</a></td><td>حواجز الانشطار والنفاذ</td><td><code>fission/</code></td></tr>
      <tr><td><a href="#measure">11</a></td><td>أطياف الانبعاث، التوزيعات الزاوية والمقاطع العرضية التفاضلية المزدوجة (اختياري، للإخراج فقط)</td><td><code>specout.py</code><br><code>specang.py</code></td></tr>
      <tr><td><a href="#measure">11</a></td><td>الأسر في أهداف مثارة حراريًا والمعدلات النجمية (اختياري)</td><td><code>astro/stellar.py</code></td></tr>
      <tr><td><a href="#measure">11</a></td><td>عدم اليقين عبر متغيرات عشوائية كثيرة (مونت كارلو الشامل)</td><td><code>tmc.py</code></td></tr>
      <tr><td></td><td>البرنامج الذي ينفّذ المراحل بالترتيب، ونوى حسابية اختيارية مكتوبة بلغة C لزيادة السرعة</td><td><code>engine.py</code><br><code>engine_c.py</code>, <code>native/</code></td></tr>
      <tr><td></td><td>كل القيم الافتراضية والخيارات، تُقرأ مرة واحدة عند البدء؛ وكذلك بارامترات TENDL المضبوطة لكل نويدة، تُطبَّق كما يطبّقها TALYS (اختياري)</td><td><code>input/</code></td></tr>
    </tbody>
  `,
  coda_h3_added: "إضافات تتجاوز TALYS",
  coda_p_added: "الصفوف المعلَّمة بـ <b>مفعّل</b> تعمل افتراضيًا، لذا لم يعد التشغيل الافتراضي يطابق TALYS تمامًا؛ ويمكن تعطيل كل منها بكلمة مفتاحية أو بمتغير بيئة. أما البقية فتبقى معطّلة ما لم تُفعَّل.",
  coda_table_added: `
    <thead><tr><th>الفصل</th><th>ما الذي يتغير</th><th>الشيفرة</th></tr></thead>
    <tbody>
      <tr><td><a href="#cascade">8</a></td><td><b>مفعّل.</b> محاسبة مغلقة للتدفق: النوى المتبقية محفوظة حتى 10⁻⁹ mb (في TALYS: 10⁻³ mb)، والنوى المتبقية الواقعة بعد نافذة الشلال في TALYS بخطوة محفوظة، وحتى 8 من كل جسيم منبعث في القنوات الحصرية، وتُحتسب كل فروع إزالة الإثارة المتكررة لمستوى ما</td><td><code>emission/fluxclose.py</code><br><code>emission/channels.py</code><br><code>kevleak2.py</code></td></tr>
      <tr><td><a href="#decay">6</a></td><td><b>مفعّل.</b> تُملأ الفترة العليا للنواة المركبة الأولى كما تملؤها الفوتونات الأولية (بوزن E<sub>γ</sub>³)، لا بشكل منتظم</td><td><code>compound/nnleak.py</code></td></tr>
      <tr><td><a href="#decay">6</a></td><td><b>مفعّل.</b> لا تشتت مرن مركب متوسط تحت الرنينات الأولى (أقل من 1 keV)، حيث يكون التشتت المرن تشتت جهد</td><td><code>lowepot.py</code></td></tr>
      <tr><td><a href="#decay">6</a></td><td><b>مفعّل.</b> الأهداف المشوهة غير الانشطارية: مخارج النيوترونات إلى مستويات خارج الحزمة المقترنة تستخدم نفاذ القنوات المقترنة</td><td><code>compound/ccexitnb.py</code></td></tr>
      <tr><td><a href="#omp">2</a></td><td><b>مفعّل.</b> انبعاث ألفا يرى جهدًا يعتمد على درجة حرارة النواة المتبقية؛ وقذائف ألفا تدخل بنموذج ألفا 6؛ وجهود التريتون والهيليون تتضمن حجم القذيفة</td><td><code>omp/alphatemp.py</code><br><code>alphaentr.py</code><br><code>omp/tfold.py</code></td></tr>
      <tr><td><a href="#fission">9</a></td><td><b>مفعّل.</b> نفاذ أحادي البعد دقيق عبر كل حدبة من حدبات الحاجز</td><td><code>fission/wkb.py</code></td></tr>
      <tr><td><a href="#gamma">7</a></td><td><b>مفعّل.</b> معاملات شدة E1/M1 الخاصة بكل نواة، حين يوفرها التشغيل، تُستبدل بدالة عامة واحدة للتشوه</td><td><code>gamma/ftglobal.py</code></td></tr>
      <tr><td><a href="#gamma">7</a></td><td>نمط مقص أقوى في الأنوية المشوهة، بمنهجيات أحدث تطابق قياسات أوسلو (نحو 4 إلى 5 أضعاف في الأكتينيدات)؛ أو صيغة بديلة تُقيِّس طاقته وشدته بالتشوه</td><td><code>gamma/scissors.py</code></td></tr>
      <tr><td><a href="#gamma">7</a></td><td>دالة قوة غاما معاد تقييسها لتطابق كل نواة شدتها الإشعاعية المقيسة ⟨Γγ⟩/D₀، في كل أنوية الشلال لا الأولى فقط</td><td><code>gamma/ggnorm.py</code></td></tr>
      <tr><td><a href="#gamma">7</a></td><td>نمط مقص أقوى وتقييس ⟨Γγ⟩ للأنوية الأثقل فقط (Z ≥ 88)، موجّهان للأسر عند طاقات keV</td><td><code>gamma/actphys.py</code></td></tr>
      <tr><td><a href="#gamma">7</a></td><td>ثابت عرض E1 خاص بنا بدلًا من جدول TALYS المشتق من TENDL (تثبّته الوصفة الخالية من البيانات التي ننشرها)</td><td><code>gamma/e1_width.py</code></td></tr>
      <tr><td><a href="#gamma">7</a></td><td>شدة E2 الجماعية للحزم الدورانية في شبه المتصل</td><td><code>gamma/isoe2.py</code></td></tr>
      <tr><td><a href="#omp">2</a></td><td>ضبط إقليمي للبئر البصري للأهداف المشوهة من العناصر الأرضية النادرة، مضبوط على S₀ وS₁ المقيسين دون بيانات أسر</td><td><code>omp/regional.py</code></td></tr>
      <tr><td><a href="#omp">2</a></td><td>دالتا القوة النيوترونية المقيستان S₀ وS₁ تحددان نفاذ النيوترونات عند الطاقات المنخفضة</td><td><code>omp/sfunc.py</code></td></tr>
      <tr><td><a href="#direct">3</a></td><td>الأسر المباشر إلى مدارات مقيدة، مع تصحيح للأصل: في TALYS القياسي يعيد صفرًا ما لم تُطلب أيضًا كل مخرجات النموذج البصري</td><td><code>direct/racapcalc.py</code></td></tr>
      <tr><td><a href="#direct">3</a></td><td>مخطط اقتران الهدف (دوّار، مهتز، كروي) مختار انطلاقًا من مستوياته المقيسة</td><td><code>structure/collrule.py</code></td></tr>
      <tr><td><a href="#structure">1</a></td><td>يبدأ المتصل حيث يتوقف مخطط المستويات المقيس عن أن يكون مكتملًا</td><td><code>structure/levcomplete.py</code></td></tr>
      <tr><td><a href="#structure">1</a></td><td>المستوى الذي يكون سبينه المُدرَج مستحيلًا لنواته (عدد صحيح عند A فردي) يُعامَل كمستوى مجهول السبين</td><td><code>structure/levjpar.py</code></td></tr>
      <tr><td><a href="#compound">5</a></td><td>كثافة مستويات بدرجة حرارة ثابتة مثبّتة على الجزء المكتمل من المستويات المنفصلة</td><td><code>density/ctwindow2.py</code></td></tr>
      <tr><td><a href="#fission">9</a></td><td>حزم دورانية لحالات الانتقال عند نقاط السرج في الانشطار</td><td><code>fission/barriers.py</code></td></tr>
      <tr><td><a href="#resonance">10</a></td><td>الأسر حيث لا يقع في النافذة النجمية سوى عدد قليل من الرنينات: القيمة النموذجية لسلّم الرنينات بدلًا من المتوسط</td><td><code>fewres.py</code></td></tr>
      <tr><td></td><td>أربع ضمانات بعيدًا عن الاستقرار: تدفق مباشر محدود بالأحادية (unitarity)، وحد لطاقة فيرمي، ولا جماعية افتراضية في الأنوية فردية-فردية، وتوزيع سبين ما قبل التوازن مُقيَّس</td><td><code>engphys.py</code></td></tr>
    </tbody>
  `,
  coda_h3_outside: "خارج المحرك",
  coda_p_outside: "بعض أجزاء القصة تعمل إلى جانب المحرك لا داخله. سلالم الرنينات الإحصائية في <a href=\"#resonance\">الفصل 10</a> موجودة في <code>physics/resonance/</code>. ومتوسطات ماكسويل (MACS) في <a href=\"#measure\">الفصل 11</a> تُحسب بعد التشغيل من منحنيات الأسر التي يعطيها المحرك، في <code>validation/differential/core.py</code>؛ أما الأسر في الأهداف المثارة حراريًا والمعدل النجمي فيحسبهما المحرك نفسه (<code>astro/stellar.py</code>، اختياري). وطبقة الربط في <a href=\"#layers\">الفصل 12</a> موجودة في <code>incognita/terra/</code>.",
  close: "إغلاق",
  chapters: "الفصول",
  nav_board: "لوحة النتائج", nav_data_short: "البيانات",
  coda_repo: "الشيفرة والمكتبة والقياسات المنقّحة كلها مفتوحة: <a href=\"https://github.com/seth-michael-weaver/incognita\">seth-michael-weaver/incognita على GitHub</a>. يمكنك الاطلاع بنفسك على أي تنبؤ في صفحة <a href=\"data.html?lang=ar\">كل النويدات</a>، أو نسخ المستودع وتشغيله.",
  diagram: "رسم تخطيطي",
});

Object.assign(WT.L.ui, { pause_sweep: "إيقاف المسح مؤقتًا", play_sweep: "استئناف المسح" });

/* course mode: audience note, chapter level tags, per-step links */
Object.assign(WT.L.ui, {
  audience: '<b>لمن هذه الصفحة:</b> لكل شخص فضولي. الفصول الأولى لا تتطلب معرفة بالفيزياء، والأخيرة تبلغ مستوى البحث العلمي. يحمل كل فصل وسمًا: <span class="lvl l0">تمهيدي</span> أو <span class="lvl l1">متوسط</span> أو <span class="lvl l2">متقدم</span>. أتريد استخدامها في الصف؟ اطّلع على <a href="instructors.html" data-keep-lang>دليل المعلمين</a>.',
  lvl0: "تمهيدي", lvl1: "متوسط", lvl2: "متقدم", lvl_title: "المستوى",
  step_link: "انسخ رابطًا إلى هذه الخطوة", link_copied: "تم نسخ الرابط",
});
