/* Arabic: economy (اقتصاد النيوترونات) */
WT.L.ch.economy = {
  num: "الدرس 1", title: "اقتصاد النيوترونات", short: "اقتصاد النيوترونات",
  html: `
<div class="step">
  <h3>ألف نيوترون</h3>
  <p>تتبّع 1000 نيوترون سريع عبر جيل واحد. قليل منها يسبب انشطارات إضافية، وبعضها يتسرب إلى الخارج، وبعضها يُؤسر في الطريق، والباقي يشطر اليورانيوم-235 ليصنع الألف التالية. ستة عوامل حاصل ضربها <i>k</i> = <i>η f p ε P</i><sub>FNL</sub> <i>P</i><sub>TNL</sub>.</p>
</div>
<div class="step">
  <h3>التخصيب</h3>
  <p>كلما زاد اليورانيوم-235 في الوقود زاد عدد النيوترونات الممتصة حيث تسبب الانشطار. ومع اليورانيوم الطبيعي (0.7 %) والماء العادي لا تبلغ <i>k</i> القيمة 1 أبدًا.</p>
  <div class="ctl"><label for="eco-e">اليورانيوم-235 (%)</label><input id="eco-e" type="range" data-bind="enr" min="0.7" max="5" step="0.1" value="3"><output data-show="enr" data-fmt="1"></output></div>
</div>
<div class="step">
  <h3>الماء بين القضبان</h3>
  <p>ماء قليل جدًا، فيأسر اليورانيوم-238 النيوترونات وهي تتباطأ؛ ماء كثير جدًا، فيمتصها الماء نفسه. هناك نسبة مثلى، والمفاعلات المائية تُبنى دونها بقليل.</p>
  <div class="ctl"><label for="eco-m">الماء إلى الوقود (× المعتاد)</label><input id="eco-m" type="range" data-bind="m" min="0.3" max="4" step="0.05" value="1"><output data-show="m" data-fmt="2"></output></div>
</div>
<div class="step">
  <h3>الحجم</h3>
  <p>النيوترونات المولودة قرب السطح يمكنها الإفلات. القلب الصغير يسرّب الكثير منها؛ والأكبر يحتفظ بها. اعثر على الحجم الذي تتجاوز عنده <i>k</i> القيمة 1.</p>
  <div class="ctl"><label for="eco-s">حجم القلب (× المعتاد)</label><input id="eco-s" type="range" data-bind="s" min="0.3" max="2" step="0.05" value="0.6"><output data-show="s" data-fmt="2"></output></div>
</div>`,
};
Object.assign(WT.L.labels, {
  "fast fission": "انشطار سريع",
  "fast leak": "تسرب سريع",
  "leaks out, fast": "تتسرب، سريعة",
  "U{#} catches": "أسر U{#}",
  "caught by U{#}": "يأسرها U{#}",
  "slow leak": "تسرب بطيء",
  "leaks out, slow": "تتسرب، بطيئة",
  "water, steel…": "ماء، فولاذ…",
  "water, steel, boron": "ماء، فولاذ، بورون",
  "P fast {#}": "P سريع {#}",
  "P slow {#}": "P بطيء {#}",
  "p {#}": "p {#}",
  "f {#}": "f {#}",
  "slowing": "الإبطاء",
  "slowing down": "الإبطاء",
  "{#} split U{#}": "{#} تشطر U{#}",
  "U{#}": "U{#}",
  "next: {#}": "التالي: {#}",
  "next generation: {#}": "الجيل التالي: {#}",
  "k = {#}": "k = {#}",
  "critical: steady": "حرج: ثابت",
  "grows": "تنمو",
  "dies away": "تتلاشى",
  "best ≈ {#}×": "الأمثل ≈ {#}×",
  "less water": "ماء أقل",
  "more water": "ماء أكثر",
  "{#} % leak out": "{#} % تتسرب",
  "k = η {#} × f {#} × p {#} × ε {#} × P {#} × P {#}": "k = η {#} × f {#} × p {#} × ε {#} × P {#} × P {#}",
  "textbook set (D&H); trends illustrative": "قيم مرجعية (D&H)؛ الاتجاهات توضيحية",
  "factors: textbook set (Duderstadt & Hamilton) at {#} %; slider trends illustrative": "العوامل: قيم مرجعية (Duderstadt & Hamilton) عند {#} %؛ واتجاهات المنزلقات توضيحية",
});
