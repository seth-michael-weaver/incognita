/* Hindi: gamow (अध्याय 30, गैमो शिखर और प्रज्वलन) */
WT.L.ch.gamow = {
  num: "अध्याय 30", title: "गैमो शिखर और प्रज्वलन", short: "गैमो शिखर",
  lead: "गर्म प्लाज्मा ऊर्जाओं की एक संकरी खिड़की से जलता है: सुरंगन के लिए पर्याप्त तेज़, और मायने रखने लायक आम।",
  html: `
<div class="step">
  <h3>गैमो शिखर</h3>
  <p>कम ही नाभिक तेज़ होते हैं; तेज़ नाभिक आसानी से सुरंगन करते हैं। दोनों का गुणनफल चमकता है: गैमो शिखर। तापमान रेखा को खींचिए।</p>
  <div class="ctl"><label for="gw-t">तापमान kT (keV)</label><input id="gw-t" type="range" data-bind="lT" min="0" max="2" step="0.01" value="1"><output data-show="T" data-fmt="1"></output></div>
  <div class="formula">E₀ = (E<sub>G</sub> (kT)² / 4)<sup>1/3</sup> · चौड़ाई 4√(E₀kT/3)</div>
</div>
<div class="step">
  <h3>ईंधनों की अभिक्रियाशीलता</h3>
  <p>पूरी खिड़की को जोड़िए तो अभिक्रियाशीलता ⟨σv⟩ मिलती है। किसी मशीन की पहुंच वाले हर तापमान पर D–T बहुत आगे है।</p>
  <div class="ctl"><label for="gw-t2">तापमान kT (keV)</label><input id="gw-t2" type="range" data-bind="lT" min="0" max="2" step="0.01" value="1"><output data-show="T" data-fmt="1"></output></div>
  <div class="formula">⟨σv⟩ = ∫ σ(E) v f(E) dE</div>
</div>
<div class="step">
  <h3>लॉसन मानदंड और प्रज्वलन</h3>
  <p>प्लाज्मा को किसी तापमान और परिरोध तक खींचिए, फिर छोड़ दीजिए। सबसे ऊपरी वक्र के ऊपर वह खुद को गर्म रखता है।</p>
  <div class="btns"><button class="btn" data-act="lowgo">कमजोर मशीन आजमाएं</button> <button class="btn ghost" data-act="higo">मजबूत मशीन आजमाएं</button></div>
  <div class="formula">प्रज्वलन: n τ<sub>E</sub> T ≳ 3·10²¹ keV s m⁻³</div>
</div>`,
};
