/* Arabic: layers (chapter 12). The scoreboard counts come from WT.board (js/scoreboard-data.js, loaded first), as in // [i18n check parity with English helper: data-act="${act}"]
 * js/ch/layers.js; a missing block or field drops the number, not the sentence. */
(function () {
  const B = WT.board || {};
  const nOf = (v) => (typeof v === "number" && isFinite(v) ? v : null);
  const tally = (o) => {
    if (!o) return null;
    const w = nOf(o.WIN), t = nOf(o.TIE), l = nOf(o.LOSS);
    if (w === null || t === null || l === null) return null;
    return { w, t, l, d: nOf(o.decided) ?? w + t + l };
  };
  const TE = tally(B.incognita), TT = tally(B.terra);
  const LIBS = B.terra && Array.isArray(B.terra.by_rival) ? B.terra.by_rival.map((r) => r && r.rival).filter((s) => typeof s === "string") : [];
  const ASOF = (() => {
    const m = /^(\d{4})-(\d{2})-(\d{2})$/.exec(B.asof || ""); if (!m) return null;
    const mes = ["يناير", "فبراير", "مارس", "أبريل", "مايو", "يونيو", "يوليو", "أغسطس", "سبتمبر", "أكتوبر", "نوفمبر", "ديسمبر"][+m[2] - 1];
    return mes ? `${+m[3]} ${mes} ${m[1]}` : null;
  })();
  const figs = (T) => (T ? `<div class="figs" aria-label="${T.w} فوزًا، ${T.t} تعادلًا، ${T.l} خسارة"><div class="w"><b>${T.w}</b><span>فوز</span></div><div><b>${T.t}</b><span>تعادل</span></div><div class="l"><b>${T.l}</b><span>خسارة</span></div></div>` : "");
  const libs = LIBS.length ? `مكتبات البيانات المقيَّمة الرئيسية (${LIBS.join(", ")})` : "مكتبات البيانات المقيَّمة الرئيسية";
  const engineScore = TE ? ` ومن بين ${TE.d} من هذه المقارنات، يتقدم بوضوح في ${TE.w}، ويتعادل في ${TE.t}، ويتأخر في ${TE.l}.` : "";
  const terraScore = TT ? `في مقابل ${libs}، يتقدم في ${TT.w} من ${TT.d} مقارنة، ويتعادل في ${TT.t}، ويتأخر في ${TT.l}.` : `تجري مقارنته مع ${libs}.`;

  WT.L.ch.layers = {
    num: "الفصل 21", title: "كيف يُبنى النموذج طبقةً فوق طبقة", short: "الطبقات",
    lead: "ما نقدمه يُبنى على شكل طبقات فوق المحرك، وعلى كل طبقة أن تستحق مكانها أمام القياسات.",
    html: `
<div class="step">
  <div class="layer-chip on">قيد الاستخدام</div>
  <h3>الطبقة 1 · قاعدة واحدة لكل نواة</h3>
  <p>الخط الأزرق هو تنبؤ المحرك لتفاعل ما. المحرك هو الطبقة السفلى: الفيزياء نفسها والإعدادات العامة نفسها لكل النويدات، ولا شيء فيه مُعايَر على المقاطع العرضية لأي نواة بعينها.</p>
  <div class="btns"><button class="btn ghost" data-act="reveal" aria-pressed="false">أظهر القياسات</button></div>
  <p>وهذا ما يجعله قابلًا للاختبار بالقياسات وفي مقابل شيفرات نمذجة أخرى حُسبت على الأنوية نفسها. وليس هذا اختبارًا أعمى: فقد اختيرت الإعدادات العامة ونحن نراقب هذه المقارنات نفسها.${engineScore}</p>
  ${figs(TE)}
</div>
<div class="step">
  <div class="layer-chip null">جُرّبت: لا تحسّن بعد</div>
  <h3>الطبقة 2 · القياسات الخاصة بكل نواة</h3>
  <p>تستبدل هذه الطبقة بالقاعدة العامة القيمَ المقيسة لكل نواة: تباعد المستويات D0، ودالتي القوة S0 وS1 (مدى سهولة امتصاصها للنيوترونات البطيئة)، ومتوسط عرض غاما ⟨Γγ⟩، ومستويات الطاقة المعروفة لها.</p>
  <div class="btns"><button class="btn ghost" data-act="ms0" aria-pressed="true">القاعدة العامة</button><button class="btn ghost" data-act="ms1" aria-pressed="false">القياسات الخاصة</button></div>
  <p>فعّلها وستلاحظ أن الخط بالكاد يتحرك. لم تجد الاختبارات حتى الآن تحسنًا شاملًا: فالصيغة الوحيدة التي تفيد تفاعلًا قرب عتبته تُسيء إلى أسر النيوترونات. لذلك تبقى هذه الطبقة معطلة في الوقت الحالي.</p>
</div>
<div class="step">
  <div class="layer-chip cand">مرشّحة</div>
  <h3>الطبقة 3 · اتباع البيانات الجيدة (TERRA)</h3>
  <p>حيث يكون التفاعل مقيسًا جيدًا، ينبغي للخط أن يتبع القياسات. الطبقة الثالثة، TERRA، تمرّر خط المحرك عبر البيانات الجيدة حيث وُجدت، وتعود إلى المحرك حيث لا توجد.</p>
  <div class="ctl"><label for="lay-cov">الجزء المقيس من مدى الطاقة (%)</label><input id="lay-cov" type="range" data-bind="cov" min="0" max="1" step="0.01" value="0.45"><output data-show="covPct" data-fmt="0"></output></div>
  <p>${terraScore} ومعظمها داخل العينة: فقد رأت TERRA تلك القياسات، كما رأتها المكتبات.</p>
  ${figs(TT)}
</div>
<div class="step">
  <div class="layer-chip wip">قيد التطوير</div>
  <h3>الطبقة 4 · أشرطة خطأ صادقة</h3>
  <p>تضع الطبقة العليا حول الخط نطاقًا ينبغي أن يحتوي القيمة الحقيقية نحو مرتين من كل ثلاث (نطاق 68 %): ضيقًا حيث تثبّته البيانات الجيدة، وأعرض حيث لا توجد.</p>
  <div class="ctl"><label for="lay-band">عرض النطاق · القياسات داخله (%)</label><input id="lay-band" type="range" data-bind="band" min="0.2" max="2.5" step="0.05" value="1"><output data-show="inside" data-fmt="0"></output></div>
  <p>اسحبه وعُدّ القياسات التي تقع داخله. إن كان ضيقًا جدًا فهو يعد بدقة لا يملكها؛ وإن كان عريضًا جدًا فلا يقول شيئًا. لم يُعتمد نطاق المحرك نفسه بعد: فهو صحيح حين تُجمع التفاعلات كلها، لكنه ليس صحيحًا بعد في كل عائلة من التفاعلات. أما TERRA فلها نطاقاتها الخاصة، وهي جزء من مقارناتها المذكورة أعلاه.</p>
</div>
<div class="step">
  <h3>الوضع الحالي</h3>
  <p>لا تُعتمد أي طبقة إلا بعد اختبارها أمام القياسات، وتبقى معطلة إن لم تُفِد. اليوم المحرك قيد الاستخدام وTERRA مرشّحة؛ أما طبقة البنية المقيسة ونطاق عدم اليقين الخاص بالمحرك فما زالا قيد الاختبار.</p>
  <p><a href="scoreboard.html" data-keep-lang>اعرض لوحة النتائج كاملة ←</a> كل المقارنات التي لا نفوز بها، وكل منافس، وكيفية قراءتها.</p>
  <div class="aside">${ASOF ? `النتائج حتى ${ASOF}، من` : "النتائج من"} سجل البحث الخاص بالمشروع. المنحنيات في الرسم توضيحية.</div>
</div>`,
  };
})();
Object.assign(WT.L.labels, {
  "{#} · engine": "{#} · المحرك",
  "{#} · measured structure": "{#} · البنية المقيسة",
  "{#} · TERRA: anchored to data": "{#} · TERRA: مثبّت على البيانات",
  "{#} · uncertainty band": "{#} · نطاق عدم اليقين",
  "measured here": "مقيس هنا",
  "neutron energy →": "طاقة النيوترون →",
  "how often the reaction happens": "كم مرة يحدث التفاعل",
  "hollow dots: measurements the engine is compared with": "النقاط المجوفة: القياسات التي يُقارَن بها المحرك",
  "own measured values: the line barely moves": "القيم المقيسة الخاصة: الخط بالكاد يتحرك",
  "global rule": "القاعدة العامة",
  "no measurements: TERRA falls back to the engine": "لا قياسات: تعود TERRA إلى المحرك",
  "solid: follows the data · dashed: the engine alone": "المتصل: يتبع البيانات · المتقطع: المحرك وحده",
  "{#} of {#} measurements inside the band (aim: about {#} %)": "{#} من {#} قياسًا داخل النطاق (الهدف: نحو {#} %)",
  "no measurements to check the band against": "لا قياسات يمكن فحص النطاق بها",
});
Object.assign(WT.L.ui, { nav_board: "لوحة النتائج" });
