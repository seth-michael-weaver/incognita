/* Arabic: spectrum (المفاعلات السريعة والحرارية) */
WT.L.ch.spectrum = {
  num: "الدرس 1", title: "المفاعلات السريعة والحرارية", short: "سريع أم حراري",
  html: `
<div class="step">
  <h3>ما مدى سرعة النيوترونات</h3>
  <p>تولد النيوترونات سريعة، بطاقة نحو 2 MeV. في المفاعل المائي ترتد عن الهيدروجين حتى تصير بطيئة كذرات الماء نفسها: <b>حرارية</b>. أما المفاعل السريع فلا مهدّئ فيه، فتبقى سريعة. حرّك المنزلق بين الحالتين.</p>
  <div class="ctl"><label for="spc-m1">التهدئة</label><input id="spc-m1" type="range" data-bind="mod" data-instant min="0" max="1" step="0.01" value="1"><output data-show="mod" data-fmt="2"></output></div>
</div>
<div class="step">
  <h3>نيوترونات فائضة</h3>
  <p><i>η</i> هو عدد النيوترونات التي تعيدها نواة الوقود عن كل نيوترون تمتصه. واحد يُبقي السلسلة مستمرة؛ ولتوليد وقود جديد تحتاج إلى ثانٍ فائض، أي <i>η</i> أكبر من 2 بوضوح. ولا يبلغ البلوتونيوم-239 ذلك إلا بالنيوترونات السريعة.</p>
  <div class="ctl"><label for="spc-m2">التهدئة</label><input id="spc-m2" type="range" data-bind="mod" data-instant min="0" max="1" step="0.01" value="0"><output data-show="mod" data-fmt="2"></output></div>
</div>
<div class="step">
  <h3>حرق البقايا</h3>
  <p>البقايا الثقيلة مثل الأمريسيوم تبتلع النيوترونات البطيئة في الغالب فتزداد ثقلًا فحسب. أما النيوترونات السريعة فتشطر حصة أكبر منها بكثير، لذا يستطيع المفاعل السريع حرقها.</p>
  <div class="ctl"><label for="spc-m3">التهدئة</label><input id="spc-m3" type="range" data-bind="mod" data-instant min="0" max="1" step="0.01" value="0"><output data-show="mod" data-fmt="2"></output></div>
</div>
<div class="step">
  <h3>الثمن</h3>
  <p>النيوترون البطيء أرجح بكثير أن يسبب انشطارًا: عند 1 MeV يصغر الهدف مئات المرات. لذا يحتاج القلب السريع إلى وقود أغنى بكثير، نحو 15–25 % بلوتونيوم بدل 3–5 % يورانيوم-235.</p>
  <div class="ctl"><label for="spc-m4">التهدئة</label><input id="spc-m4" type="range" data-bind="mod" data-instant min="0" max="1" step="0.01" value="1"><output data-show="mod" data-fmt="2"></output></div>
</div>`,
};
Object.assign(WT.L.labels, {
  "U{#}": "U{#}",
  "Pu{#}": "Pu{#}",
  "Np{#}": "Np{#}",
  "Am{#}": "Am{#}",
  "Cm{#}": "Cm{#}",
  "{#} % split": "{#} % تنشطر",
  "water: neutrons slow down": "الماء: النيوترونات تتباطأ",
  "water reactor: hydrogen slows the neutrons": "مفاعل مائي: الهيدروجين يبطئ النيوترونات",
  "sodium: they stay fast": "الصوديوم: تبقى سريعة",
  "fast reactor: sodium barely slows them": "مفاعل سريع: الصوديوم لا يكاد يبطئها",
  "partly moderated": "تهدئة جزئية",
  "sodium": "الصوديوم",
  "no moderator (sodium)": "بلا مهدّئ (الصوديوم)",
  "water": "ماء",
  "thermal": "حرارية",
  "resonances": "الرنينات",
  "slowing down (resonances)": "الإبطاء (الرنينات)",
  "fast": "سريعة",
  "{#} MeV": "{#} MeV",
  "{#} keV": "{#} keV",
  "{#} eV": "{#} eV",
  "neutron energy →": "طاقة النيوترون →",
  "born ~{#} MeV": "تولد عند ~{#} MeV",
  "born near {#} MeV": "تولد قرب {#} MeV",
  "η = {#}: one to continue, one to breed": "η = {#}: واحد للاستمرار، وواحد للتوليد",
  "average η: U{#} {#} · Pu{#} {#}": "متوسط η: U{#} {#} · Pu{#} {#}",
  "averaged over this spectrum:  η(U{#}) ≈ {#}   η(Pu{#}) ≈ {#}": "المتوسط على هذا الطيف:  η(U{#}) ≈ {#}   η(Pu{#}) ≈ {#}",
  "{#} b": "{#} b",
  "≈ {#} b": "≈ {#} b",
  "Pu{#} fission target": "هدف انشطار Pu{#}",
  "Pu{#} fission cross section (target size)": "المقطع العرضي لانشطار Pu{#} (حجم الهدف)",
  "{#} MeV: a target ~{#} times smaller": "{#} MeV: هدف أصغر ~{#} مرة",
  "at {#} MeV the target is about {#} times smaller than at {#} eV": "عند {#} MeV يكون الهدف أصغر بنحو {#} مرة منه عند {#} eV",
  "most neutrons end up thermal": "معظم النيوترونات تنتهي حرارية",
  "most neutrons are slowed all the way to thermal": "معظم النيوترونات تُبطَّأ حتى الطاقة الحرارية",
  "most stay between {#} keV and {#} MeV": "معظمها يبقى بين {#} keV و{#} MeV",
  "most neutrons stay between {#} keV and {#} MeV": "معظم النيوترونات تبقى بين {#} keV و{#} MeV",
  "many linger at in-between energies": "كثير منها يمكث عند طاقات وسطى",
  "many neutrons linger at in-between energies": "كثير من النيوترونات يمكث عند طاقات وسطى",
  "hot water: kT ≈ {#} eV": "في الماء الساخن: kT ≈ {#} eV",
  "thermal: kT ≈ {#} eV in hot water, about {#} km/s": "حرارية: kT ≈ {#} eV في الماء الساخن، نحو {#} km/s",
  "the rest are captured and grow heavier": "والباقي يُؤسر فيزداد ثقلًا",
  "the rest are captured: the nucleus just grows heavier": "والباقي يُؤسر: تزداد النواة ثقلًا فحسب",
  "illustrative shapes": "أشكال توضيحية",
});
