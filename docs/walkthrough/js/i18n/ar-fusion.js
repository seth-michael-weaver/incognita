/* Arabic: fusion (الفصل 29، طاقة الاندماج وحاجز كولوم) */
WT.L.ch.fusion = {
  num: "الفصل 29", title: "طاقة الاندماج وحاجز كولوم", short: "الاندماج",
  lead: "يسير الاندماج في الاتجاه المعاكس للانشطار: تتحد نواتان خفيفتان، ويكون الزوج أخف من مجموع أجزائه.",
  html: `
<div class="step">
  <h3>طاقة الاندماج من منحنى الربط</h3>
  <p>ادمج نواتين خفيفتين: إن كانت النواة الجديدة أعلى على منحنى الربط تحررت طاقة. وبعد قمة الحديد يكلّف الدمج طاقة.</p>
  <div class="ctl"><label for="fu-a">كل نواة خفيفة A</label><input id="fu-a" type="range" data-bind="fuse" data-instant min="2" max="60" step="1" value="2"><output data-show="fuse" data-fmt="0"></output></div>
  <p class="ctl-result" id="fu-fuse-out" aria-live="polite"></p>
</div>
<div class="step">
  <h3>حاجز كولوم والنفق الكمومي</h3>
  <p>اسحب الديوترون إلى الخلف ثم أفلته. النواتان كلتاهما مشحونتان، فترتد معظم الرميات عن التل؛ وقليل منها يعبره بالنفق الكمومي.</p>
  <div class="ctl"><label for="fu-e">الدفع (keV)</label><input id="fu-e" type="range" data-bind="lE" min="0.5" max="2.6" step="0.01" value="1.7"><output data-show="E" data-fmt="0"></output></div>
  <div class="btns"><button class="btn" data-act="fire">أطلق</button></div>
</div>
<div class="step">
  <h3>نواتج التفاعل وقيمة Q</h3>
  <p>الزوج المندمج أخف من الجزأين. والكتلة المفقودة تنطلق على هيئة جسيمات سريعة.</p>
  <div class="btns fu-fuels"><button class="btn ghost" data-act="DT" aria-pressed="true">D–T</button> <button class="btn ghost" data-act="DD" aria-pressed="false">D–D</button> <button class="btn ghost" data-act="DHe" aria-pressed="false">D–³He</button> <button class="btn ghost" data-act="pB" aria-pressed="false">p–¹¹B</button></div>
</div>
<div class="step">
  <h3>معدل التفاعل النووي الحراري</h3>
  <p>في غاز ساخن تعبر أسرع الأنوية. وكل وميض هو اندماج واحد.</p>
  <div class="ctl"><label for="fu-t">درجة الحرارة (keV)</label><input id="fu-t" type="range" data-bind="lT" min="0" max="2" step="0.01" value="1"><output data-show="T" data-fmt="1"></output></div>
</div>`,
};
Object.assign(WT.L.labels, {
  "B": "B",
  "Copper{#}": "النحاس{#}",
  "Coulomb hill": "تل كولوم",
  "D–D": "D–D",
  "D–T": "D–T",
  "D–³He": "D–³He",
  "E = kT": "E = kT",
  "Gamow peak E₀": "قمة غامو E₀",
  "K {#} · field lines lost to the wall: {#}": "K {#} · خطوط مجال فُقدت إلى الجدار: {#}",
  "Q = {#}": "Q = {#}",
  "Q = ∞: no heating needed": "Q = ∞: لا حاجة إلى تسخين",
  "Silicon{#} (SiC)": "السيليكون{#} (SiC)",
  "Steel (iron{#})": "فولاذ (حديد{#})",
  "Sun's core": "قلب الشمس",
  "TBR {#}": "TBR {#}",
  "Tungsten{#}": "التنغستن{#}",
  "Vanadium{#}": "الفاناديوم{#}",
  "after {#} years at {#} MW/m² · {#} MeV neutrons only · σ from INCOGNITA library v{#}": "بعد {#} سنة عند {#} MW/m² · نيوترونات {#} MeV فقط · σ من مكتبة INCOGNITA v{#}",
  "almost never": "نادرًا جدًا",
  "alpha {#} MeV": "ألفا {#} MeV",
  "axis, q = {#}": "المحور، q = {#}",
  "binding per nucleon (MeV)": "الربط لكل نيوكليون (MeV)",
  "bubble-chamber view, magnetic field into the page: charged products curl, the neutron leaves no track": "منظر حجرة فقاعات، والمجال المغناطيسي داخل الصفحة: تلتفّ النواتج المشحونة، ولا يترك النيوترون أثرًا",
  "burning on its own": "تحترق وحدها",
  "cooled down: plasma lost": "بردت: فُقدت البلازما",
  "cooling": "تبرد",
  "could not load the library file": "تعذّر تحميل ملف المكتبة",
  "deuteron": "ديوترون",
  "deuteron {#} keV": "ديوترون {#} keV",
  "deuteron: pull back, let go": "الديوترون: اسحب للخلف ثم أفلت",
  "drag or tap a point; it runs on its own": "اسحب أو انقر نقطة؛ وتسير وحدها",
  "easiest: {a} keV, nτT {b}": "الأسهل: {a} keV، nτT {b}",
  "edge: q = {#} · lines that cross it are lost": "الحافة: q = {#} · الخطوط التي تعبرها تُفقد",
  "electron {#} keV": "إلكترون {#} keV",
  "energy of the colliding pair (keV)": "طاقة الزوج المتصادم (keV)",
  "few are this fast": "قلّة بهذه السرعة",
  "fusion rate: {a} the rate at {b} keV": "معدل الاندماج: {a} المعدل عند {b} keV",
  "grain boundary": "حدّ الحبيبات",
  "heating itself": "تسخّن نفسها",
  "helium stays and gathers into bubbles; hydrogen mostly diffuses out": "يبقى الهيليوم ويتجمع فقاعات؛ ويخرج معظم الهيدروجين بالانتشار",
  "helium {#} appm": "هيليوم {#} appm",
  "hill to climb: charge product Z₁Z₂ = {#}": "التل المطلوب تسلّقه: حاصل الشحنتين Z₁Z₂ = {#}",
  "hold: heaters on (Q = fusion power / heating) · let go: heaters off, the plasma is on its own": "اضغط: التسخين يعمل (Q = قدرة الاندماج / التسخين) · أفلت: التسخين متوقف، والبلازما وحدها",
  "hydrogen {#} appm": "هيدروجين {#} appm",
  "ignition (Q = ∞)": "الاشتعال (Q = ∞)",
  "kT (keV)": "kT (keV)",
  "kT {#} keV · E₀ {#} keV · width {#} keV": "kT {#} keV · E₀ {#} keV · العرض {#} keV",
  "kT {a} keV · D–T {b} m³/s · {c}× D–D": "kT {a} keV · D–T {b} m³/s · {c}× D–D",
  "keeps itself hot": "تحافظ على حرارتها",
  "laps {#}": "الدورات {#}",
  "lead–lithium": "رصاص–ليثيوم",
  "liquid lithium": "ليثيوم سائل",
  "loading INCOGNITA's cross sections…": "جارٍ تحميل مقاطع INCOGNITA العرضية…",
  "missing {#} u  =  {#} MeV out": "نقص {#} u  =  {#} MeV محرَّرة",
  "n τE (s/m³)": "n τE (s/m³)",
  "negative: turns the other way": "سالبة: تدور في الاتجاه المعاكس",
  "neutron escapes": "نيوترون يفلت",
  "peak near {#} keV": "القمة قرب {#} keV",
  "per fusion neutron · {#} neutrons · cross sections are simple fits": "لكل نيوترون اندماج · {#} نيوترون · المقاطع العرضية ملاءمات بسيطة",
  "plasma": "بلازما",
  "product ×{a}": "حاصل الضرب ×{a}",
  "push {a} keV · chance to tunnel head-on {b}": "الدفع {a} keV · فرصة النفق وجهًا لوجه {b}",
  "q = {#}": "q = {#}",
  "q = {#}/{#}: closes after {#} lap": "q = {#}/{#}: ينغلق بعد {#} دورة",
  "q = {#}/{#}: closes after {#} laps": "q = {#}/{#}: ينغلق بعد {#} دورات",
  "q = {#}: no simple fraction, the dots fill the circle": "q = {#}: ليس كسرًا بسيطًا، فالنقاط تملأ الدائرة",
  "screen radius is logarithmic: {#} fm to {#} fm": "نصف القطر على الشاشة لوغاريتمي: من {#} fm إلى {#} fm",
  "shield": "الدرع",
  "tap to fire": "انقر للإطلاق",
  "the cut, flat": "المقطع، مبسوطًا",
  "time slowed {a}×": "الزمن مبطّأ {a}×",
  "tries {#} · fused {#}": "المحاولات {#} · المندمجة {#}",
  "tritium made, by depth": "التريتيوم المنتَج حسب العمق",
  "triton": "تريتون",
  "tunnels more easily": "تعبر بالنفق أسهل",
  "turns at {#} fm": "يرتد عند {#} fm",
  "wall": "الجدار",
  "{#} MeV": "{#} MeV",
  "{#} cm": "{#} سم",
  "{#} in {a}": "{#} من {a}",
  "{#} keV": "{#} keV",
  "{#} keV = {#} million K": "{#} keV = {#} مليون K",
  "{a} %": "{a} %",
  "{a} + {a} → {b}: about {c} MeV released": "{a} + {a} → {b}: تتحرر نحو {c} MeV",
  "{a} + {a} → {b}: costs {c} MeV": "{a} + {a} → {b}: يكلّف {c} MeV",
  "{a} keV · chance {b}": "{a} keV · الفرصة {b}",
  "{a} keV · nτ {b} · {c}": "{a} keV · nτ {b} · {c}",
  "{a} · two branches, equally likely": "{a} · فرعان متساويا الاحتمال",
  "{a} · ρ up to {b} · {c} turns a second": "{a} · ρ حتى {b} · {c} دورة في الثانية",
  "σ at {#} MeV:  (n,α) {#} mb · (n,p) {#} mb · (n,{#}n) {#} mb": "σ عند {#} MeV:  (n,α) {#} mb · (n,p) {#} mb · (n,{#}n) {#} mb",
  "⁶Li {#} · ⁷Li {#} · (n,{#}n) {#}": "⁶Li {#} · ⁷Li {#} · (n,{#}n) {#}",
  "⁶Li {#} · ⁷Li {#} · (n,{#}n) {#} · captured {#} · leaked {#}": "⁶Li {#} · ⁷Li {#} · (n,{#}n) {#} · مُلتقَط {#} · متسرّب {#}",
  "⟨σv⟩ (m³/s)": "⟨σv⟩ (m³/s)",
});
