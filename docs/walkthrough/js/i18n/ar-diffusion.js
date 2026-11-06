/* Arabic: diffusion (الحجم الحرج والتسرب) */
WT.L.ch.diffusion = {
  num: "الدرس 1", title: "الحجم الحرج والتسرب", short: "الحجم الحرج",
  html: `
<div class="step">
  <h3>النيوترونات تتجول، وبعضها يتسرب</h3>
  <p>يتعرّج النيوترون من تصادم إلى تصادم حتى يمتصه شيء ما. وإذا وُلد قرب الحافة فقد يتجول إلى الخارج ويضيع. القلب الأكبر سطحه أصغر بالنسبة إلى حجمه، فتتسرب منه حصة أصغر.</p>
  <div class="ctl"><label for="df-w0">عرض القلب (سم)</label><input id="df-w0" type="range" data-bind="w" data-instant min="20" max="200" step="2" value="60"><output data-show="w" data-fmt="0"></output></div>
</div>
<div class="step">
  <h3>شكل الفيض</h3>
  <p>تستقر جمهرة النيوترونات على شكل واحد يهبط إلى الصفر تقريبًا عند الحافة: جيب تمام عبر اللوح، وsin(<i>r</i>)/<i>r</i> في الكرة، ودالة بسل مضروبة في جيب تمام في الأسطوانة. ومدى حدة انحنائه هو <b>التحدب الهندسي</b> <i>B</i>².</p>
  <div class="btns"><button class="btn ghost" data-act="dfslab" aria-pressed="false">لوح</button><button class="btn ghost" data-act="dfsph" aria-pressed="true">كرة</button><button class="btn ghost" data-act="dfcyl" aria-pressed="false">أسطوانة</button></div>
  <div class="ctl"><label for="df-w1">عرض القلب (سم)</label><input id="df-w1" type="range" data-bind="w" data-instant min="20" max="200" step="2" value="80"><output data-show="w" data-fmt="0"></output></div>
</div>
<div class="step">
  <h3>الحجم الحرج</h3>
  <p>يعطي الانتشار أحادي المجموعة <i>k</i><sub>eff</sub> = <i>k</i><sub>∞</sub> / (1 + <i>M</i>²<i>B</i>²)، حيث مساحة الهجرة <i>M</i>² نحو 60 cm² في مفاعل مائي. يكون القلب حرجًا حين يساوي <i>B</i>² التحدبَ المادي (<i>k</i><sub>∞</sub> − 1)/<i>M</i>². اعثر على ذلك الحجم.</p>
  <div class="btns"><button class="btn ghost" data-act="dfslab" aria-pressed="false">لوح</button><button class="btn ghost" data-act="dfsph" aria-pressed="true">كرة</button><button class="btn ghost" data-act="dfcyl" aria-pressed="false">أسطوانة</button></div>
  <div class="ctl"><label for="df-w2">عرض القلب (سم)</label><input id="df-w2" type="range" data-bind="w" data-instant min="20" max="200" step="1" value="90"><output data-show="w" data-fmt="0"></output></div>
</div>
<div class="step">
  <h3>العاكس يوفّر النيوترونات</h3>
  <p>أحِط قلبًا لوحيًا بالماء: بعض النيوترونات الخارجة تتشتت عائدة. لم يعد الفيض يهبط إلى الصفر عند حافة القلب، فيبلغ قلبٌ أرقّ قيمة <i>k</i> نفسها؛ وهذا المكسب هو <b>توفير العاكس</b>، وهو هنا نحو 6 سم في كل جانب.</p>
  <div class="btns"><button class="btn ghost" data-act="dfrefl" aria-pressed="true">عاكس مائي</button></div>
  <div class="ctl"><label for="df-w3">عرض القلب (سم)</label><input id="df-w3" type="range" data-bind="w" data-instant min="20" max="120" step="1" value="44"><output data-show="w" data-fmt="0"></output></div>
</div>`,
};
Object.assign(WT.L.labels, {
  "drag the edge": "اسحب الحافة",
  "{#} cm": "{#} سم",
  "red: leaked": "الأحمر: تسرّب",
  "red: leaked out · blue: absorbed inside": "الأحمر: تسرّب إلى الخارج · الأزرق: امتُص في الداخل",
  "leak: walk {#} % · diffusion {#} %": "التسرب: التجوال {#} % · الانتشار {#} %",
  "leak: walk … · diffusion {#} %": "التسرب: التجوال … · الانتشار {#} %",
  "share leaking: random walk {#} % · diffusion theory {#} %": "حصة التسرب: التجوال العشوائي {#} % · نظرية الانتشار {#} %",
  "share leaking: random walk … · diffusion theory {#} %": "حصة التسرب: التجوال العشوائي … · نظرية الانتشار {#} %",
  "k_eff = k∞ × ({#} − leak) = {#}": "k_eff = k∞ × ({#} − التسرب) = {#}",
  "water": "ماء",
  "slab core": "قلب لوحي",
  "slab": "لوح",
  "sphere": "كرة",
  "cylinder": "أسطوانة",
  "flux across the middle": "الفيض عبر المنتصف",
  "−D∇²φ + Σₐφ = (νΣ_f / k) φ": "−D∇²φ + Σₐφ = (νΣ_f / k) φ",
  "B² = (π/a)² = {#} × {#}⁻⁴ cm⁻²": "B² = (π/a)² = {#} × {#}⁻⁴ cm⁻²",
  "B² = (π/R)² = {#} × {#}⁻⁴ cm⁻²": "B² = (π/R)² = {#} × {#}⁻⁴ cm⁻²",
  "B² = ({#}/R)² + (π/H)² = {#} × {#}⁻⁴ cm⁻²": "B² = ({#}/R)² + (π/H)² = {#} × {#}⁻⁴ cm⁻²",
  "{#} × {#}⁻⁴ cm⁻²": "{#} × {#}⁻⁴ cm⁻²",
  "k = {#}": "k = {#}",
  "k_eff = {#} / ({#} + {#} cm² × {#}e{#} cm⁻²) = {#}": "k_eff = {#} / ({#} + {#} cm² × {#}e{#} cm⁻²) = {#}",
  "slab {#} cm wide · smaller core → sharper bend → larger B²": "لوح بعرض {#} سم · قلب أصغر ← انحناء أحدّ ← B² أكبر",
  "sphere {#} cm wide · smaller core → sharper bend → larger B²": "كرة بعرض {#} سم · قلب أصغر ← انحناء أحدّ ← B² أكبر",
  "cylinder {#} cm wide · smaller core → sharper bend → larger B²": "أسطوانة بعرض {#} سم · قلب أصغر ← انحناء أحدّ ← B² أكبر",
  "critical {#} cm": "حرج عند {#} سم",
  "core width →": "عرض القلب →",
  "critical: B² = B²ₘ, k_eff = {#}": "حرج: B² = B²ₘ، k_eff = {#}",
  "reflected: k_eff {#} · bare: {#} · savings {#} cm per side": "مع العاكس: k_eff {#} · عارٍ: {#} · التوفير {#} سم لكل جانب",
  "bare: k_eff {#} · critical at {#} cm": "عارٍ: k_eff {#} · حرج عند {#} سم",
  "illustration": "توضيح",
});
