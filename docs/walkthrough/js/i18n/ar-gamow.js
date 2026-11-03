/* Arabic: gamow (الفصل 30، قمة غامو والاشتعال) */
WT.L.ch.gamow = {
  num: "الفصل 30", title: "قمة غامو والاشتعال", short: "قمة غامو",
  lead: "تحترق البلازما الساخنة عبر نافذة ضيقة من الطاقات: سريعة بما يكفي لتعبر بالنفق الكمومي، وشائعة بما يكفي لتُحدث فرقًا.",
  html: `
<div class="step">
  <h3>قمة غامو</h3>
  <p>الأنوية السريعة قليلة، لكن السريعة تعبر بالنفق الكمومي بسهولة أكبر. ويتوهّج حاصل ضربهما: قمة غامو. اسحب خط درجة الحرارة.</p>
  <div class="ctl"><label for="gw-t">درجة الحرارة kT (keV)</label><input id="gw-t" type="range" data-bind="lT" min="0" max="2" step="0.01" value="1"><output data-show="T" data-fmt="1"></output></div>
  <div class="formula">E₀ = (E<sub>G</sub> (kT)² / 4)<sup>1/3</sup> · العرض 4√(E₀kT/3)</div>
</div>
<div class="step">
  <h3>تفاعلية أنواع الوقود</h3>
  <p>اجمع النافذة كلها تحصل على التفاعلية ⟨σv⟩. يتفوق D–T بفارق كبير عند أي درجة حرارة تستطيع آلةٌ بلوغها.</p>
  <div class="ctl"><label for="gw-t2">درجة الحرارة kT (keV)</label><input id="gw-t2" type="range" data-bind="lT" min="0" max="2" step="0.01" value="1"><output data-show="T" data-fmt="1"></output></div>
  <div class="formula">⟨σv⟩ = ∫ σ(E) v f(E) dE</div>
</div>
<div class="step">
  <h3>معيار لوسون والاشتعال</h3>
  <p>اسحب البلازما إلى درجة حرارة وزمن حصر، ثم أفلتها. فوق المنحنى العلوي تحافظ على حرارتها بنفسها.</p>
  <div class="btns"><button class="btn" data-act="lowgo">جرّب آلة ضعيفة</button> <button class="btn ghost" data-act="higo">جرّب آلة قوية</button></div>
  <div class="formula">الاشتعال: n τ<sub>E</sub> T ≳ 3·10²¹ keV s m⁻³</div>
</div>`,
};
