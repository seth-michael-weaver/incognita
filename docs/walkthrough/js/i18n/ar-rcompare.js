/* Arabic: rcompare (مقارنة أنواع المفاعلات) */
WT.L.ch.rcompare = {
  num: "الدرس 1", title: "مقارنة أنواع المفاعلات", short: "مقارنة",
  lead: "كل مفاعل هو اختيار لمهدِّئ ومبرِّد.",
  html: `
<div class="step">
  <h3>المهدِّئ والمبرِّد</h3>
  <p>اختر ما يبطئ النيوترونات وما ينقل الحرارة. انقر على نوع لزيارته.</p>
</div>
<div class="step">
  <h3>الأسخن أفضل</h3>
  <p>كلما كان المبرِّد أسخن عند خروجه من القلب، أمكن تحويل جزء أكبر من الحرارة إلى كهرباء.</p>
</div>
<div class="step">
  <h3>ما يعمل اليوم</h3>
  <p>معظم مفاعلات العالم من الأنواع الثلاثة الأولى المبرَّدة بالماء.</p>
</div>`,
};
Object.assign(WT.L.labels, {
  "ADS": "ADS",
  "AGR": "AGR",
  "BWR": "BWR",
  "GFR": "GFR",
  "HTGR": "HTGR",
  "LFR": "LFR",
  "MSR": "MSR",
  "Magnox": "Magnox",
  "Micro": "مصغَّر",
  "Oklo": "أوكلو",
  "PHWR": "PHWR",
  "PHWR ~{#} %": "PHWR ~{#} %",
  "PWR": "PWR",
  "RBMK": "RBMK",
  "SCWR": "SCWR",
  "SFR": "SFR",
  "SMR": "SMR",
  "TRIGA": "TRIGA",
  "VHTR": "VHTR",
  "about {#} power reactors in operation": "نحو {#} مفاعل قدرة قيد التشغيل",
  "about {#} reactors in all": "نحو {#} مفاعل إجمالًا",
  "boiling": "غليان",
  "boiling water": "ماء يغلي",
  "carries the heat ↓": "ينقل الحرارة ↓",
  "coolant out →": "خروج المبرِّد →",
  "coolant temperature leaving the core →": "حرارة المبرِّد الخارج من القلب →",
  "fast": "سريعة",
  "gas": "غاز",
  "graphite": "الغرافيت",
  "heavy water": "الماء الثقيل",
  "ideal (Carnot) limit": "الحد المثالي (كارنو)",
  "ideal limit": "الحد المثالي",
  "illustration": "توضيح",
  "light water": "الماء الخفيف",
  "liquid metal": "معدن سائل",
  "molten salt": "ملح منصهر",
  "none": "لا يوجد",
  "none (fast)": "لا يوجد (سريعة)",
  "others ~{#} %": "أخرى ~{#} %",
  "others: AGR, RBMK, fast reactors, HTR-PM": "أخرى: AGR وRBMK والمفاعلات السريعة وHTR-PM",
  "others: gas, graphite, fast, HTGR": "أخرى: غازية، غرافيتية، سريعة، HTGR",
  "salt": "ملح",
  "slows the neutrons →": "يبطئ النيوترونات →",
  "supercrit.": "فوق حرج",
  "supercritical water": "ماء فوق حرج",
  "the world's power reactors": "مفاعلات القدرة في العالم",
  "the world's power reactors, by type (rounded)": "مفاعلات القدرة في العالم حسب النوع (أرقام مقرَّبة)",
  "thermal": "حرارية",
  "water": "ماء",
  "what carries the heat ↓": "ما ينقل الحرارة ↓",
  "what slows the neutrons (moderator) →": "ما يبطئ النيوترونات (المهدِّئ) →",
  "{#} °C": "{#} °C",
  "↑ electricity": "↑ الكهرباء",
  "↑ share of heat turned into electricity": "↑ نسبة الحرارة المحوَّلة إلى كهرباء",
});
// hover line in the temperature chart
Object.assign(WT.L.labels, {
  "Pressurized water reactor: {#} °C, {#} %": "مفاعل الماء المضغوط: {#} °C، {#} %",
  "Boiling water reactor: {#} °C, {#} %": "مفاعل الماء المغلي: {#} °C، {#} %",
  "Pressurized heavy water reactor: {#} °C, {#} %": "مفاعل الماء الثقيل المضغوط: {#} °C، {#} %",
  "Graphite-moderated boiling water reactor: {#} °C, {#} %": "مفاعل الماء المغلي المهدَّأ بالغرافيت: {#} °C، {#} %",
  "Supercritical water reactor: {#} °C, {#} %": "مفاعل الماء فوق الحرج: {#} °C، {#} %",
  "Magnox: {#} °C, {#} %": "ماغنوكس: {#} °C، {#} %",
  "Advanced gas-cooled reactor: {#} °C, {#} %": "المفاعل المتقدم المبرَّد بالغاز: {#} °C، {#} %",
  "High-temperature gas reactor: {#} °C, {#} %": "مفاعل الغاز عالي الحرارة: {#} °C، {#} %",
  "Very-high-temperature reactor: {#} °C, {#} %": "مفاعل الحرارة فائقة الارتفاع: {#} °C، {#} %",
  "Sodium-cooled fast reactor: {#} °C, {#} %": "المفاعل السريع المبرَّد بالصوديوم: {#} °C، {#} %",
  "Lead-cooled fast reactor: {#} °C, {#} %": "المفاعل السريع المبرَّد بالرصاص: {#} °C، {#} %",
  "Gas-cooled fast reactor: {#} °C, {#} %": "المفاعل السريع المبرَّد بالغاز: {#} °C، {#} %",
  "Molten salt reactor: {#} °C, {#} %": "مفاعل الملح المنصهر: {#} °C، {#} %",
  "Small modular reactor: {#} °C, {#} %": "المفاعل المعياري الصغير: {#} °C، {#} %",
  "Heat-pipe microreactor: {#} °C, {#} %": "المفاعل الميكروي بالأنابيب الحرارية: {#} °C، {#} %",
});
