/* Arabic: reactor (كيف يولّد المفاعل الكهرباء) */
WT.L.ch.reactor = {
  num: "الدرس 1", title: "كيف يولّد المفاعل الكهرباء", short: "المفاعل",
  html: `
<div class="step">
  <h3>الوقود</h3>
  <p>يُخبَز اليورانيوم في أقراص خزفية بحجم طرف الإصبع، تُرصّ في قضبان معدنية طويلة، ثم تُجمع القضبان في حزم. يعطي القرص الواحد من الحرارة تقريبًا ما يعطيه حرق طن من الفحم.</p>
  <div class="ctl"><label for="rea-z">تصغير العرض</label><input id="rea-z" type="range" data-bind="z" min="0" max="3" step="0.01" value="0"><output data-show="z" data-fmt="1"></output></div>
</div>
<div class="step">
  <h3>انشطار الذرات يصنع الحرارة</h3>
  <p>في قلب المفاعل تسخّن ذرات اليورانيوم المنشطرة الماء الصاعد بمحاذاة القضبان. والماء نفسه يبطئ النيوترونات لتتمكن من شطر ذرات أخرى. والضغط العالي يمنعه من الغليان، حتى عند 325 °C.</p>
</div>
<div class="step">
  <h3>البخار يدير التوربين</h3>
  <p>ينقل الماء الساخن حرارته عبر أنابيب رفيعة إلى دارة ثانية تغلي. يدير البخار توربينًا ومولّدًا، ثم يعيده ماء النهر أو البحر البارد إلى ماء. ويصبح نحو ثلث الحرارة كهرباء.</p>
</div>
<div class="step">
  <h3>قضبان التحكم</h3>
  <p>تمتص قضبان التحكم النيوترونات. أدخِلها فينشطر عدد أقل من الذرات: حرارة أقل، وبخار أقل، وكهرباء أقل. اسحبها فترتفع القدرة.</p>
  <div class="ctl"><label for="rea-rod">القضبان المُدخلة (%)</label><input id="rea-rod" type="range" data-bind="ins" data-instant min="0" max="100" step="1" value="15"><output data-show="ins" data-fmt="0"></output></div>
</div>`,
};
Object.assign(WT.L.labels, {
  "reactor": "المفاعل",
  "reactor vessel": "وعاء المفاعل",
  "control rods": "قضبان التحكم",
  "core": "القلب",
  "steam gen.": "مولّد البخار",
  "steam generator": "مولّد البخار",
  "turbine": "التوربين",
  "gen.": "المولّد",
  "generator": "المولّد",
  "condenser": "المكثّف",
  "sea or river water": "ماء البحر أو النهر",
  "{#} °C out": "خروج {#} °C",
  "{#} °C in": "دخول {#} °C",
  "steam ~{#} °C": "بخار ~{#} °C",
  "{#} bar: hot, but no boiling": "{#} bar: ساخن، لكن بلا غليان",
  "{#} bar keeps the water liquid at {#} °C": "ضغط {#} bar يُبقي الماء سائلًا عند {#} °C",
  "the water also slows the neutrons": "والماء يبطئ النيوترونات أيضًا",
  "the water carries the heat and slows the neutrons": "الماء ينقل الحرارة ويبطئ النيوترونات",
  "heat {#} MW": "الحرارة {#} MW",
  "electric {#} MW": "كهرباء {#} MW",
  "electricity {#} MW": "الكهرباء {#} MW",
  "chain stopped; fuel still warm (afterheat)": "توقفت السلسلة؛ الوقود ما زال دافئًا (حرارة متبقية)",
  "chain reaction stopped; the fuel still gives off afterheat": "توقف التفاعل المتسلسل؛ والوقود ما زال يطلق حرارة متبقية",
  "turbine speed fixed by the grid; more steam, more push": "الشبكة تثبّت سرعة التوربين؛ بخار أكثر، دفع أقوى",
  "the turbine's speed is fixed by the grid; more steam pushes harder": "سرعة التوربين تثبّتها الشبكة؛ والبخار الأكثر يدفع بقوة أكبر",
  "{#}/{#} of the heat goes to the water": "{#}/{#} من الحرارة تذهب إلى الماء",
  "about two thirds of the heat leaves through the condenser": "نحو ثلثي الحرارة يخرج عبر المكثّف",
  "illustration": "توضيح",
  "drag sideways to zoom": "اسحب جانبيًا للتكبير والتصغير",
  "drag sideways to zoom out": "اسحب جانبيًا لتصغير العرض",
  "UO₂ pellet, {#} cm": "قرص UO₂، {#} cm",
  "uranium oxide pellet, about {#} cm": "قرص أكسيد اليورانيوم، نحو {#} cm",
  "{#} tonne of coal": "{#} طن من الفحم",
  "about {#} tonne of coal (or {#} m³ of gas)": "نحو {#} طن من الفحم (أو {#} m³ من الغاز)",
  "same heat, roughly": "الحرارة نفسها تقريبًا",
  "fuel rod, ~{#} m": "قضيب وقود، ~{#} m",
  "fuel rod, about {#} m long": "قضيب وقود، طوله نحو {#} m",
  "~{#} pellets inside": "~{#} قرصًا بداخله",
  "about {#} pellets in a metal tube": "نحو {#} قرصًا في أنبوب معدني",
  "(not to scale)": "(ليس بمقياس الرسم)",
  "assembly: {#} rods": "الحزمة: {#} قضيبًا",
  "fuel assembly from above: {#} rods": "حزمة الوقود من أعلى: {#} قضيبًا",
  "rings: control-rod guide tubes": "الحلقات: أنابيب توجيه قضبان التحكم",
  "rings: tubes the control rods slide into": "الحلقات: أنابيب تنزلق فيها قضبان التحكم",
  "core: {#} assemblies": "القلب: {#} حزمة",
  "the core from above: {#} assemblies": "قلب المفاعل من أعلى: {#} حزمة",
  "~{#} rods, ~{#} m across": "~{#} قضيب، قطره ~{#} m",
  "about {#} rods in a cylinder about {#} m across": "نحو {#} قضيب في أسطوانة قطرها نحو {#} m",
  "pellet": "القرص",
  "rod": "القضيب",
  "assembly": "الحزمة",
});
