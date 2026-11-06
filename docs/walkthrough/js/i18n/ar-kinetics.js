/* Arabic: kinetics (حركية المفاعل: المجموعات الست ومعادلة الساعة العكسية) */
WT.L.ch.kinetics = {
  num: "الدرس 1", title: "حركية المفاعل: المجموعات الست ومعادلة الساعة العكسية", short: "الحركية",
  html: `
<div class="step">
  <h3>ست مجموعات من النيوترونات المتأخرة</h3>
  <p>تأتي النيوترونات المتأخرة من نحو ست مجموعات من نواتج الانشطار، بأعمار نصف من 0.23 s إلى 56 s (كيبن، U-235). مجموعتا 2 s و22 s تطلقان معظمها، بينما تحتفظ المجموعات الطويلة العمر بمعظم المخزون المنتظر: متوسط التأخر Σ <i>a</i><sub>i</sub>/<i>λ</i><sub>i</sub> ≈ 13 s. أوقف الانشطارات وراقب كل مجموعة تنضب بإيقاعها الخاص.</p>
  <div class="btns"><button class="btn" data-act="kistop" aria-pressed="false">أوقف الانشطارات</button></div>
</div>
<div class="step">
  <h3>معادلة الساعة العكسية</h3>
  <p>عوّض <i>n</i> ∝ e<sup><i>ωt</i></sup> في الحركية النقطية ذات المجموعات الست فتحصل على <i>ρ</i> = <i>ω</i>Λ + Σ <i>β</i><sub>i</sub><i>ω</i>/(<i>ω</i> + <i>λ</i><sub>i</sub>): سبعة فروع تفصلها الأقطاب عند −<i>λ</i><sub>i</sub>. والقفزة في <i>ρ</i> تلاقي كل فرع مرة واحدة؛ والجذر الأيمن هو الدور المستقر <i>T</i> = 1/<i>ω</i><sub>1</sub>، والستة الأخرى تتلاشى.</p>
  <div class="ctl"><label for="ki-r1">التفاعلية ρ ($)</label><input id="ki-r1" type="range" data-bind="rd" data-instant min="-2" max="1.3" step="0.01" value="0.3"><output data-show="rd" data-fmt="2"></output></div>
</div>
<div class="step">
  <h3>القفزة الفورية والحرجية الفورية</h3>
  <p>قفزة في التفاعلية ترفع القدرة أولًا خلال أجزاء من الألف من الثانية بنسبة <i>P</i><sub>1</sub>/<i>P</i><sub>0</sub> ≈ <i>β</i>/(<i>β</i> − <i>ρ</i>)، ثم ترتفع على الدور المستقر. وعند <i>ρ</i> = 1 $ تكون النيوترونات الفورية وحدها حرجة، وينهار الدور نحو Λ/(<i>ρ</i> − <i>β</i>).</p>
  <div class="ctl"><label for="ki-r2">التفاعلية ρ ($)</label><input id="ki-r2" type="range" data-bind="rj" data-instant min="0.05" max="1.3" step="0.01" value="0.5"><output data-show="rj" data-fmt="2"></output></div>
</div>
<div class="step">
  <h3>بعد الإيقاف الطارئ</h3>
  <p>أدخِل تفاعلية سالبة كبيرة: تهبط القدرة فورًا إلى نحو <i>β</i>/(<i>β</i> − <i>ρ</i>)، ثم لا يمكنها أن تنخفض أسرع من اضمحلال أطول المجموعات عمرًا. ومهما كان الإيقاف الطارئ عميقًا، يقترب الدور من −1/<i>λ</i><sub>1</sub> ≈ −80 s.</p>
  <div class="ctl"><label for="ki-r3">التفاعلية ρ ($)</label><input id="ki-r3" type="range" data-bind="rs" data-instant min="-30" max="-0.5" step="0.5" value="-10"><output data-show="rs" data-fmt="1"></output></div>
</div>`,
};
Object.assign(WT.L.labels, {
  "Stop fissions": "أوقف الانشطارات",
  "Restart fissions": "استأنف الانشطارات",
  "half-life · share emitted": "عمر النصف · الحصة المنبعثة",
  "waiting stock": "المخزون المنتظر",
  "delayed neutrons out": "النيوترونات المتأخرة الخارجة",
  "{#} s": "{#} s",
  "{#} s after stopping · delayed emission {#} % of the start": "{#} s بعد الإيقاف · الانبعاث المتأخر {#} % من البداية",
  "mean delay Σ aᵢ/λᵢ = {#} s · β = {#} (U{#})": "متوسط التأخر Σ aᵢ/λᵢ = {#} s · β = {#} (U{#})",
  "Keepin six-group data": "بيانات كيبن للمجموعات الست",
  "prompt critical": "حرجية فورية",
  "drag ρ": "اسحب ρ",
  "prompt root": "الجذر الفوري",
  "prompt root ≈ −(β−ρ)/Λ": "الجذر الفوري ≈ −(β−ρ)/Λ",
  "ω ({#}/s), stretched": "ω ({#}/s)، ممطوط",
  "ω ({#}/s), axis stretched (asinh)": "ω ({#}/s)، محور ممطوط (asinh)",
  "ρ = {#}: power stays flat": "ρ = {#}: القدرة تبقى ثابتة",
  "stable period T = {#}/ω₁ = {#} ms": "الدور المستقر T = {#}/ω₁ = {#} ms",
  "stable period T = {#}/ω₁ = {#} s": "الدور المستقر T = {#}/ω₁ = {#} s",
  "stable period T = {#}/ω₁ = {#} min": "الدور المستقر T = {#}/ω₁ = {#} دقيقة",
  "stable period T = {#}/ω₁ = {#} h": "الدور المستقر T = {#}/ω₁ = {#} ساعة",
  "drag the rods out": "اسحب القضبان إلى الخارج",
  "prompt jump β/(β−ρ) = {#}": "القفزة الفورية β/(β−ρ) = {#}",
  "power": "القدرة",
  "prompt critical · period {#} ms (Λ = {#} µs)": "حرجية فورية · الدور {#} ms (Λ = {#} µs)",
  "prompt critical · period {#} s (Λ = {#} µs)": "حرجية فورية · الدور {#} s (Λ = {#} µs)",
  "prompt critical · period {#} min (Λ = {#} µs)": "حرجية فورية · الدور {#} دقيقة (Λ = {#} µs)",
  "prompt critical · period {#} h (Λ = {#} µs)": "حرجية فورية · الدور {#} ساعة (Λ = {#} µs)",
  "ρ = {#} $ · stable period {#} ms": "ρ = {#} $ · الدور المستقر {#} ms",
  "ρ = {#} $ · stable period {#} s": "ρ = {#} $ · الدور المستقر {#} s",
  "ρ = {#} $ · stable period {#} min": "ρ = {#} $ · الدور المستقر {#} دقيقة",
  "ρ = {#} $ · stable period {#} h": "ρ = {#} $ · الدور المستقر {#} ساعة",
  "drag the rods in": "اسحب القضبان إلى الداخل",
  "prompt drop to {#}": "هبوط فوري إلى {#}",
  "slope e^(−t/{#} s)": "الميل e^(−t/{#} s)",
  "slope e^(−t / {#} s): the {#} s group": "الميل e^(−t / {#} s): مجموعة {#} s",
  "power ×{#} speed": "القدرة، سرعة ×{#}",
  "ρ = {#} $ · stable period {#} ms (limit {#} s)": "ρ = {#} $ · الدور المستقر {#} ms (الحد {#} s)",
  "ρ = {#} $ · stable period {#} s (limit {#} s)": "ρ = {#} $ · الدور المستقر {#} s (الحد {#} s)",
  "ρ = {#} $ · stable period {#} min (limit {#} s)": "ρ = {#} $ · الدور المستقر {#} دقيقة (الحد {#} s)",
  "ρ = {#} $ · stable period {#} h (limit {#} s)": "ρ = {#} $ · الدور المستقر {#} ساعة (الحد {#} s)",
});
