/* Hindi: afterheat (बंद करने के बाद ऊष्मा) */
WT.L.ch.afterheat = {
  num: "पाठ 1", title: "बंद करने के बाद ऊष्मा", short: "क्षय ऊष्मा",
  html: `
<div class="step">
  <h3>शृंखला रुकती है</h3>
  <p>नियंत्रण छड़ें गिराने से लगभग एक मिनट में परमाणुओं का विखंडन रुक जाता है। पर ईंधन दहकता रहता है: पहले के विखंडनों से बचे टुकड़े रेडियोधर्मी हैं, और उनके क्षय अब भी ऊष्मा देते हैं।</p>
  <div class="btns"><button class="btn" data-act="ahDrop">छड़ें गिराइए</button> <button class="btn ghost" data-act="ahUp">फिर से चालू</button></div>
</div>
<div class="step">
  <h3>यह धीरे-धीरे घटती है</h3>
  <p>बंद होने के ठीक बाद यह ऊष्मा पूर्ण शक्ति की लगभग 6–7 % होती है। एक घंटे बाद लगभग 1 %, एक दिन बाद लगभग आधा प्रतिशत, एक सप्ताह बाद चौथाई प्रतिशत। छोटे हिस्से, पर एक बहुत बड़ी संख्या के।</p>
  <div class="ctl"><label for="ah-t">बंद होने के बाद का समय</label><input id="ah-t" type="range" data-bind="lt" data-instant min="0" max="7.5" step="0.01" value="3.56"></div>
</div>
<div class="step">
  <h3>पानी बहता रहे</h3>
  <p>इसलिए कोर को बंद होने के बाद भी ठंडा किया जाता है। पंप ईंधन के पास से पानी बहाते रहते हैं और ऊष्मा ले जाते हैं। उन्हें बंद कीजिए और तापमान चढ़ता है, क्योंकि ऊष्मा के जाने की कोई जगह नहीं।</p>
  <div class="btns"><button class="btn ghost" data-act="ahPump" aria-pressed="true">पंप</button></div>
</div>
<div class="step">
  <h3>पंपों के बिना शीतलन</h3>
  <p>गर्म पानी ऊपर उठता है और ठंडा पानी नीचे बैठता है। कोर से ऊंचे रखे एक कुंड तक जाने वाला लूप बिना किसी पंप के पानी को चलाता रहता है। कई नए डिज़ाइन दिनों तक इसी पर निर्भर रहते हैं।</p>
  <div class="btns"><button class="btn ghost" data-act="ahPump" aria-pressed="false">पंप</button> <button class="btn ghost" data-act="ahPass" aria-pressed="true">निष्क्रिय लूप</button></div>
</div>`,
};
Object.assign(WT.L.labels, {
  "{a} s": "{a} s",
  "{a} min": "{a} मिनट",
  "{a} hours": "{a} घंटे",
  "{a} days": "{a} दिन",
  "{a} months": "{a} महीने",
  "illustration": "चित्रण",
  "splitting atoms": "विखंडित होते परमाणु",
  "heat from splitting atoms": "विखंडित होते परमाणुओं से ऊष्मा",
  "decaying fragments": "क्षय होते टुकड़े",
  "heat from decaying fragments": "क्षय होते टुकड़ों से ऊष्मा",
  "full power": "पूर्ण शक्ति",
  "running at full power": "पूर्ण शक्ति पर चालू",
  "{a} after the rods dropped": "छड़ें गिरने के {a} बाद",
  "total heat: {a} % of full power": "कुल ऊष्मा: पूर्ण शक्ति का {a} %",
  "the splitting dies away in about a minute": "विखंडन लगभग एक मिनट में थम जाता है",
  "the splitting dies away within about a minute": "विखंडन लगभग एक मिनट के भीतर थम जाता है",
  "the decay heat stays and fades slowly": "क्षय ऊष्मा बनी रहती है, धीरे-धीरे घटती है",
  "the decay heat stays, and fades only slowly": "क्षय ऊष्मा बनी रहती है, और बहुत धीरे-धीरे ही घटती है",
  "{#} min": "{#} मिनट",
  "{#} hour": "{#} घंटा",
  "{#} day": "{#} दिन",
  "{#} week": "{#} सप्ताह",
  "{#} year": "{#} वर्ष",
  "heat, share of full power": "ऊष्मा, पूर्ण शक्ति का अंश",
  "heat, as a share of full power": "ऊष्मा, पूर्ण शक्ति के अंश के रूप में",
  "{a} after shutdown: {b} % of full power": "बंद होने के {a} बाद: पूर्ण शक्ति का {b} %",
  "{#} MW core: {a} MW, like {b} kettles": "{#} MW कोर: {a} MW, {b} केतलियों जितना",
  "for a {#} MW core: {a} MW, as much as {b} electric kettles": "{#} MW कोर के लिए: {a} MW, {b} बिजली की केतलियों जितना",
  "pool, up high": "ऊंचा कुंड",
  "water pool, placed higher": "पानी का कुंड, ऊंचाई पर",
  "cooler": "शीतक",
  "heat exchanger": "ऊष्मा विनिमयक",
  "pump on": "पंप चालू",
  "pump running": "पंप चल रहा है",
  "pump off": "पंप बंद",
  "pump stopped": "पंप रुका हुआ",
  "boiling": "उबल रहा है",
  "the water starts to boil": "पानी उबलने लगता है",
  "normal": "सामान्य",
  "too hot": "बहुत गर्म",
  "temperature": "तापमान",
  "core temperature": "कोर तापमान",
  "{a} after shutdown · heat {b} % of full power": "बंद होने के {a} बाद · ऊष्मा पूर्ण शक्ति का {b} %",
  "too hot: cooling must be restored": "बहुत गर्म: शीतलन बहाल करना होगा",
  "too hot: the water would start to boil away; cooling must be restored": "बहुत गर्म: पानी उबलकर उड़ने लगेगा; शीतलन बहाल करना होगा",
  "temperature climbing": "तापमान चढ़ रहा है",
  "temperature climbing: the heat has nowhere to go": "तापमान चढ़ रहा है: ऊष्मा के जाने की कोई जगह नहीं",
  "pumps carry the heat away": "पंप ऊष्मा ले जाते हैं",
  "steady: the pumps carry the heat away": "स्थिर: पंप ऊष्मा ले जाते हैं",
  "steady, with no pumps": "स्थिर, बिना पंपों के",
  "steady: natural circulation carries the heat away": "स्थिर: प्राकृतिक परिसंचरण ऊष्मा ले जाता है",
  "steady": "स्थिर",
});
