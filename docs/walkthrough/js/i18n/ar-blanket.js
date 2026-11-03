/* Arabic: blanket (الفصل 32، الغطاء المولِّد والجدار الأول) */
WT.L.ch.blanket = {
  num: "الفصل 32", title: "الغطاء المولِّد والجدار الأول", short: "الغطاء المولِّد",
  lead: "يكاد التريتيوم لا يوجد في الطبيعة. على محطة D–T أن تولّد تريتيومها بنفسها من الليثيوم، مستخدمةً النيوترونات التي تنتجها بلازماها.",
  html: `
<div class="step">
  <h3>نسبة توليد التريتيوم</h3>
  <p>يتجوّل كل نيوترون حتى يلتقطه الليثيوم فيصنع تريتونًا. كل نقطة متوهجة هي تريتون واحد.</p>
  <div class="ctl"><label for="bk-e">حصة الليثيوم-6 (%)</label><input id="bk-e" type="range" data-bind="enr" min="7.5" max="90" step="0.5" value="90" data-instant><output data-show="enr" data-fmt="1"></output></div>
  <div class="ctl"><label for="bk-d">عمق طبقة التوليد (سم)</label><input id="bk-d" type="range" data-bind="depth" min="10" max="100" step="1" value="60" data-instant><output data-show="depth" data-fmt="0"></output></div>
  <div class="formula">TBR = (⁶Li(n,t) + ⁷Li(n,n′t)) / n<sub>الاندماج</sub> &gt; 1</div>
</div>
<div class="step">
  <h3>تكاثر النيوترونات بالتفاعل (n,2n)</h3>
  <p>يمكن لنيوترون طاقته 14 MeV يصطدم بالرصاص أن يطرد نيوترونًا ثانيًا: (n,2n). قارن بالليثيوم وحده.</p>
  <div class="btns bk-m"><button class="btn ghost" data-act="pbli" aria-pressed="true">رصاص–ليثيوم</button> <button class="btn ghost" data-act="li" aria-pressed="false">ليثيوم فقط</button></div>
  <div class="ctl"><label for="bk-e2">حصة الليثيوم-6 (%)</label><input id="bk-e2" type="range" data-bind="enr" min="7.5" max="90" step="0.5" value="90" data-instant><output data-show="enr" data-fmt="1"></output></div>
</div>
<div class="step">
  <h3>الهيليوم والهيدروجين في الجدار الأول</h3>
  <p>يتلقى الجدار الأول حزمة الـ 14 MeV كاملة. ويتراكم الهيليوم والهيدروجين داخله، بالمعدلات التي تحسبها INCOGNITA.</p>
  <div class="btns bk-w"><button class="btn ghost" data-act="wFe" aria-pressed="true">فولاذ</button> <button class="btn ghost" data-act="wW" aria-pressed="false">تنغستن</button> <button class="btn ghost" data-act="wV" aria-pressed="false">فاناديوم</button> <button class="btn ghost" data-act="wCu" aria-pressed="false">نحاس</button> <button class="btn ghost" data-act="wSi" aria-pressed="false">SiC</button></div>
  <div class="ctl"><label for="bk-l">حمل الجدار (MW/m²)</label><input id="bk-l" type="range" data-bind="load" min="0.5" max="3" step="0.1" value="1" data-instant><output data-show="load" data-fmt="1"></output></div>
  <div class="ctl"><label for="bk-y">السنوات</label><input id="bk-y" type="range" data-bind="yrs" min="0" max="10" step="0.1" value="2" data-instant><output data-show="yrs" data-fmt="1"></output></div>
  <div class="formula">appm = σ(14.1 MeV) · φ · t · 10⁶</div>
  <div class="aside">المقاطع العرضية: مكتبة INCOGNITA الإصدار v0.2 (<code>library/v0.2/channels_v02.parquet</code>)، وهي المنحنيات نفسها في <a href="data.html#Fe-56" data-keep-lang>كل النويدات</a>.</div>
</div>`,
};
