/* Hindi: sandbox (एक रिएक्टर बनाइए) */
WT.L.ch.sandbox = {
  num: "पाठ 1", title: "एक रिएक्टर बनाइए", short: "रिएक्टर बनाइए", lead: "ईंधन, मंदक, शीतलक और आकार चुनिए, और देखिए कि क्या शृंखला अभिक्रिया ख़ुद को चालू रख सकती है। एक सरलीकृत पाठ्यपुस्तक मॉडल।",
  html: `
<div class="step">
  <h3>चार गुणक</h3>
  <p>यदि कोई न्यूट्रॉन रिसकर बाहर न जाए, तो अवशोषित हर न्यूट्रॉन से <i>k</i><sub>∞</sub> = <i>η f p ε</i> नए न्यूट्रॉन बनेंगे; प्राकृतिक यूरेनियम का यह ग्रेफाइट ढेर बस इतना कर पाता है।</p>
</div>
<div class="step">
  <h3>मंदक चुनिए</h3>
  <p>प्राकृतिक यूरेनियम के साथ केवल भारी पानी या ग्रेफाइट ही <i>k</i><sub>∞</sub> को 1 से ऊपर ले जाते हैं: हल्का पानी न्यूट्रॉनों को अच्छी तरह धीमा करता है पर बहुत अधिक अवशोषित करता है।</p>
  <div class="btns" role="group" aria-label="मंदक"><button class="btn ghost" data-act="mo_h2o">हल्का पानी</button> <button class="btn ghost" data-act="mo_d2o">भारी पानी</button> <button class="btn ghost" data-act="mo_c">ग्रेफाइट</button></div>
  <div class="ctl"><label for="sb-m1">प्रति ईंधन मंदक</label><input id="sb-m1" type="range" data-bind="lm" min="-0.5" max="2.3" step="0.01" value="0.3"><output class="sb-m"></output></div>
</div>
<div class="step">
  <h3>ईंधन संवर्धित कीजिए</h3>
  <p>कुछ प्रतिशत यूरेनियम-235 से साधारण पानी काम करने लगता है, इसीलिए आज के अधिकांश रिएक्टर इसी का उपयोग करते हैं।</p>
  <div class="btns" role="group" aria-label="ईंधन"><button class="btn ghost" data-act="fu_nat">प्राकृतिक U</button> <button class="btn ghost" data-act="fu_leu">संवर्धित U</button> <button class="btn ghost" data-act="fu_mox">MOX (Pu)</button> <button class="btn ghost" data-act="fu_th">थोरियम + U-233</button></div>
  <div class="ctl"><label for="sb-e1">विखंडनीय अंश (%)</label><input id="sb-e1" type="range" data-bind="enr" min="0.7" max="30" step="0.1" value="3"><output data-show="enr" data-fmt="1"></output></div>
</div>
<div class="step">
  <h3>आकार और रिसाव</h3>
  <p>न्यूट्रॉन सतह से निकल जाते हैं, इसलिए <i>k</i> = <i>k</i><sub>∞</sub> / (1 + <i>M</i>²<i>B</i>²)। प्राकृतिक यूरेनियम के इस ग्रेफाइट ढेर का किनारा खींचकर बिंदुदार वलय तक ले जाइए।</p>
  <div class="ctl"><label for="sb-r1">कोर त्रिज्या (m)</label><input id="sb-r1" type="range" data-bind="R" min="0.2" max="6" step="0.05" value="2"><output data-show="R" data-fmt="2"></output></div>
</div>
<div class="step">
  <h3>जब शीतलक उबलता है</h3>
  <p>पानी से ठंडे किए जाने वाले ग्रेफाइट कोर में उबलने से <i>k</i> बढ़ता है, क्योंकि पानी धीमा करने से अधिक अवशोषित करता था: चेर्नोबिल में RBMK का दोष। दूसरे शीतलक आज़माइए।</p>
  <div class="btns" role="group" aria-label="शीतलक"><button class="btn ghost" data-act="co_h2o">पानी</button> <button class="btn ghost" data-act="co_gas">CO₂ / हीलियम</button> <button class="btn ghost" data-act="co_na">सोडियम</button></div>
</div>
<div class="step">
  <h3>अपना बनाइए</h3>
  <p>कुछ भी चलेगा। तीव्र रिएक्टर में मंदक नहीं होता और उसे कहीं अधिक विखंडनीय ईंधन चाहिए।</p>
  <div class="btns" role="group" aria-label="ईंधन"><button class="btn ghost" data-act="fu_nat">प्राकृतिक U</button> <button class="btn ghost" data-act="fu_leu">संवर्धित U</button> <button class="btn ghost" data-act="fu_mox">MOX (Pu)</button> <button class="btn ghost" data-act="fu_th">थोरियम + U-233</button></div>
  <div class="ctl"><label for="sb-e2">विखंडनीय अंश (%)</label><input id="sb-e2" type="range" data-bind="enr" min="0.7" max="30" step="0.1" value="3"><output data-show="enr" data-fmt="1"></output></div>
  <div class="btns" role="group" aria-label="मंदक"><button class="btn ghost" data-act="mo_none">मंदक नहीं</button> <button class="btn ghost" data-act="mo_h2o">हल्का पानी</button> <button class="btn ghost" data-act="mo_d2o">भारी पानी</button> <button class="btn ghost" data-act="mo_c">ग्रेफाइट</button></div>
  <div class="ctl"><label for="sb-m2">प्रति ईंधन मंदक</label><input id="sb-m2" type="range" data-bind="lm" min="-0.5" max="2.3" step="0.01" value="0.3"><output class="sb-m"></output></div>
  <div class="btns" role="group" aria-label="शीतलक"><button class="btn ghost" data-act="co_h2o">पानी</button> <button class="btn ghost" data-act="co_d2o">भारी पानी</button> <button class="btn ghost" data-act="co_gas">CO₂ / हीलियम</button> <button class="btn ghost" data-act="co_na">सोडियम</button> <button class="btn ghost" data-act="co_pb">सीसा</button> <button class="btn ghost" data-act="co_salt">पिघला लवण</button></div>
  <div class="ctl"><label for="sb-r2">कोर त्रिज्या (m)</label><input id="sb-r2" type="range" data-bind="R" min="0.2" max="6" step="0.05" value="2"><output data-show="R" data-fmt="2"></output></div>
</div>`,
};
Object.assign(WT.L.labels, {
  "CO₂ / helium gas coolant": "CO₂ / हीलियम गैस शीतलक",
  "MOX {#} % Pu": "MOX {#} % Pu",
  "MOX, {#} % plutonium{#}": "MOX, {#} % प्लूटोनियम{#}",
  "R {#} m": "R {#} m",
  "absorbed in fuel": "ईंधन में अवशोषित",
  "can never sustain a chain, at any size": "किसी भी आकार पर शृंखला नहीं चल सकती",
  "caught by fuel": "ईंधन द्वारा पकड़े गए",
  "coolant boils away: k ↑": "शीतलक उबलकर उड़ जाता है: k ↑",
  "coolant boils: k ↑": "शीतलक उबलता है: k ↑",
  "coolant boils: k ≈": "शीतलक उबलता है: k ≈",
  "coolant lost: k barely changes": "शीतलक गया: k लगभग नहीं बदलता",
  "coolant lost: k ↑": "शीतलक गया: k ↑",
  "critical size": "क्रांतिक आकार",
  "escape capture": "प्रग्रहण से बचे",
  "f": "f",
  "fast fission": "तेज विखंडन",
  "fission": "विखंडन",
  "fuel": "ईंधन",
  "fuel heats up: k ↓ (Doppler)": "ईंधन गर्म होता है: k ↓ (डॉप्लर)",
  "fuel hotter: k ↓": "ईंधन गर्म: k ↓",
  "graphite moderator": "ग्रेफाइट मंदक",
  "graphite moderator · CO₂ / helium gas coolant": "ग्रेफाइट मंदक · CO₂ / हीलियम गैस शीतलक",
  "graphite moderator · water coolant": "ग्रेफाइट मंदक · पानी शीतलक",
  "k": "k",
  "k∞": "k∞",
  "leak": "रिसाव",
  "leak out": "रिसकर बाहर",
  "light water moderator": "हल्का पानी मंदक",
  "light water moderator · water coolant": "हल्का पानी मंदक · पानी शीतलक",
  "mod./cool.": "मंदक/शीतलक",
  "moderator, coolant": "मंदक, शीतलक",
  "natural U": "प्राकृतिक U",
  "natural uranium ({#} % U{#})": "प्राकृतिक यूरेनियम ({#} % U{#})",
  "never critical": "कभी क्रांतिक नहीं",
  "no chain, any size": "किसी आकार पर शृंखला नहीं",
  "no leakage": "रिसाव नहीं",
  "no moderator: a fast reactor · sodium coolant": "मंदक नहीं: तीव्र रिएक्टर · सोडियम शीतलक",
  "no moderator: fast": "मंदक नहीं: तीव्र",
  "no size is big enough": "कोई आकार पर्याप्त बड़ा नहीं",
  "p": "p",
  "per fuel absorption": "प्रति ईंधन अवशोषण",
  "radius {#} m": "त्रिज्या {#} m",
  "radius {#} m · drag the edge": "त्रिज्या {#} m · किनारा खींचें",
  "simplified model": "सरलीकृत मॉडल",
  "simplified one-group model · illustration": "सरलीकृत एक-समूह मॉडल · चित्रण",
  "stays in": "भीतर रहते हैं",
  "stays in (M² {#} cm²)": "भीतर रहते हैं (M² {#} cm²)",
  "sustains a chain, {#} % to spare (ρ)": "शृंखला चलती है, {#} % अतिरिक्त (ρ)",
  "sustains: +{#} % spare": "चलती है: +{#} % अतिरिक्त",
  "too small: critical at radius {#} m": "बहुत छोटा: त्रिज्या {#} m पर क्रांतिक",
  "too small: needs {#} m": "बहुत छोटा: {#} m चाहिए",
  "uranium, {#} % U{#}": "यूरेनियम, {#} % U{#}",
  "water boils: k ↑": "पानी उबलता है: k ↑",
  "water boils: k ↓": "पानी उबलता है: k ↓",
  "water coolant": "पानी शीतलक",
  "water heats or boils: k ↑": "पानी गर्म हो या उबले: k ↑",
  "water heats or boils: k ↓": "पानी गर्म हो या उबले: k ↓",
  "where the neutrons go": "न्यूट्रॉन कहाँ जाते हैं",
  "{#} % U{#}": "{#} % U{#}",
  "enriched U": "संवर्धित U",
  "light water": "हल्का पानी",
  "heavy water": "भारी पानी",
  "lead": "सीसा",
  "molten salt": "पिघला लवण",
  "sodium": "सोडियम",
  "coolant": "शीतलक",
  "= η f, if nothing leaked": "= η f, यदि कुछ न रिसे",
  "= η f p ε, if nothing leaked": "= η f p ε, यदि कुछ न रिसे",
  "stays in: {#} / ({#} + M²B²), M² = {#} cm²": "भीतर रहते हैं: {#} / ({#} + M²B²), M² = {#} cm²",
  "neutrons per absorption in fuel": "ईंधन में प्रति अवशोषण न्यूट्रॉन",
  "share absorbed in fuel": "ईंधन में अवशोषित अंश",
  "no slowing down, no resonance loss": "धीमा होना नहीं, अनुनाद हानि नहीं",
  "escape capture while slowing": "धीमा होते समय प्रग्रहण से बचना",
  "fast fission counted in η": "तीव्र विखंडन η में शामिल",
  "bonus from fast fission": "तीव्र विखंडन से अतिरिक्त",
  "thorium, {#} % U{#}": "थोरियम, {#} % U{#}",
  "Th + {#} % U{#}": "Th + {#} % U{#}",
  "uranium, {#} % U{#} (highly enriched)": "यूरेनियम, {#} % U{#} (उच्च संवर्धित)",
  "critical at {#} m": "{#} m पर क्रांतिक",
  "coolant heats: k ↑": "शीतलक गर्म होता है: k ↑",
  "coolant heats: k ↓": "शीतलक गर्म होता है: k ↓",
  "coolant boils away: k ↓": "शीतलक उबलकर उड़ जाता है: k ↓",
  "coolant lost: k ↓": "शीतलक गया: k ↓",
  "heavy water coolant": "भारी पानी शीतलक",
  "sodium coolant": "सोडियम शीतलक",
  "lead coolant": "सीसा शीतलक",
  "molten salt coolant": "पिघला लवण शीतलक",
  "heavy water moderator": "भारी पानी मंदक",
  "heavy water moderator · heavy water coolant": "भारी पानी मंदक · भारी पानी शीतलक",
  "heavy water moderator · water coolant": "भारी पानी मंदक · पानी शीतलक",
  "graphite moderator · sodium coolant": "ग्रेफाइट मंदक · सोडियम शीतलक",
  "no moderator: a fast reactor · lead coolant": "मंदक नहीं: तीव्र रिएक्टर · सीसा शीतलक",
  "no moderator: a fast reactor · CO₂ / helium gas coolant": "मंदक नहीं: तीव्र रिएक्टर · CO₂ / हीलियम गैस शीतलक",
  "no moderator: a fast reactor · molten salt coolant": "मंदक नहीं: तीव्र रिएक्टर · पिघला लवण शीतलक",
  "water moderates": "पानी मंदन करता है",
  "heavy water moderates": "भारी पानी मंदन करता है",
  "no moderator, but the water moderates": "मंदक नहीं, पर पानी मंदन करता है",
  "no moderator, but the heavy water moderates": "मंदक नहीं, पर भारी पानी मंदन करता है",
});
