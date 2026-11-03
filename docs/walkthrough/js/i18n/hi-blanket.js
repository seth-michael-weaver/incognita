/* Hindi: blanket (अध्याय 32, प्रजनन ब्लैंकेट और प्रथम दीवार) */
WT.L.ch.blanket = {
  num: "अध्याय 32", title: "प्रजनन ब्लैंकेट और प्रथम दीवार", short: "ब्लैंकेट",
  lead: "ट्रिटियम प्रकृति में लगभग नहीं मिलता। D–T संयंत्र को अपने प्लाज्मा के बनाए न्यूट्रॉनों से लिथियम से अपना ट्रिटियम खुद प्रजनित करना पड़ता है।",
  html: `
<div class="step">
  <h3>ट्रिटियम प्रजनन अनुपात</h3>
  <p>हर न्यूट्रॉन तब तक भटकता है जब तक लिथियम उसे पकड़कर एक ट्राइटॉन न बना दे। हर चमकता बिंदु एक ट्राइटॉन है।</p>
  <div class="ctl"><label for="bk-e">लिथियम-6 हिस्सा (%)</label><input id="bk-e" type="range" data-bind="enr" min="7.5" max="90" step="0.5" value="90" data-instant><output data-show="enr" data-fmt="1"></output></div>
  <div class="ctl"><label for="bk-d">प्रजनक गहराई (cm)</label><input id="bk-d" type="range" data-bind="depth" min="10" max="100" step="1" value="60" data-instant><output data-show="depth" data-fmt="0"></output></div>
  <div class="formula">TBR = (⁶Li(n,t) + ⁷Li(n,n′t)) / n<sub>संलयन</sub> &gt; 1</div>
</div>
<div class="step">
  <h3>(n,2n) से न्यूट्रॉन गुणन</h3>
  <p>सीसे से टकराने वाला 14 MeV न्यूट्रॉन एक दूसरा न्यूट्रॉन बाहर निकाल सकता है: (n,2n)। केवल लिथियम से तुलना कीजिए।</p>
  <div class="btns bk-m"><button class="btn ghost" data-act="pbli" aria-pressed="true">सीसा–लिथियम</button> <button class="btn ghost" data-act="li" aria-pressed="false">केवल लिथियम</button></div>
  <div class="ctl"><label for="bk-e2">लिथियम-6 हिस्सा (%)</label><input id="bk-e2" type="range" data-bind="enr" min="7.5" max="90" step="0.5" value="90" data-instant><output data-show="enr" data-fmt="1"></output></div>
</div>
<div class="step">
  <h3>प्रथम दीवार में हीलियम और हाइड्रोजन</h3>
  <p>प्रथम दीवार पूरे 14 MeV पुंज को झेलती है। उसके भीतर हीलियम और हाइड्रोजन उन दरों पर जमा होते हैं जिनकी गणना INCOGNITA करता है।</p>
  <div class="btns bk-w"><button class="btn ghost" data-act="wFe" aria-pressed="true">इस्पात</button> <button class="btn ghost" data-act="wW" aria-pressed="false">टंगस्टन</button> <button class="btn ghost" data-act="wV" aria-pressed="false">वैनेडियम</button> <button class="btn ghost" data-act="wCu" aria-pressed="false">तांबा</button> <button class="btn ghost" data-act="wSi" aria-pressed="false">SiC</button></div>
  <div class="ctl"><label for="bk-l">दीवार भार (MW/m²)</label><input id="bk-l" type="range" data-bind="load" min="0.5" max="3" step="0.1" value="1" data-instant><output data-show="load" data-fmt="1"></output></div>
  <div class="ctl"><label for="bk-y">वर्ष</label><input id="bk-y" type="range" data-bind="yrs" min="0" max="10" step="0.1" value="2" data-instant><output data-show="yrs" data-fmt="1"></output></div>
  <div class="formula">appm = σ(14.1 MeV) · φ · t · 10⁶</div>
  <div class="aside">अनुप्रस्थ काट: INCOGNITA की लाइब्रेरी v0.2 (<code>library/v0.2/channels_v02.parquet</code>), वही वक्र जो <a href="data.html#Fe-56" data-keep-lang>सभी न्यूक्लाइड</a> में हैं।</div>
</div>`,
};
