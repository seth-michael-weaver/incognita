/* Hindi: burnup (ईंधन बर्नअप) */
WT.L.ch.burnup = {
  num: "पाठ 1", title: "ईंधन बर्नअप", short: "बर्नअप",
  html: `
<div class="step">
  <h3>एक गोली का जीवन</h3>
  <p>यहां ताजा ईंधन गोली के एक हजार परमाणु हैं: 45 यूरेनियम-235 हैं, बाकी यूरेनियम-238। रिएक्टर चलाइए और देखिए कि यूरेनियम-235 विखंडित होता है और नए परमाणु प्रकट होते हैं। <b>बर्नअप</b> निकाली गई ऊर्जा गिनता है, गीगावाट-दिन प्रति टन यूरेनियम में; जल रिएक्टर लगभग 45–55 पर रुकते हैं।</p>
  <div class="ctl"><label for="bu-d1">पूर्ण शक्ति पर दिन</label><input id="bu-d1" type="range" data-bind="d" data-instant min="0" max="1400" step="10" value="400"><output data-show="d" data-fmt="0"></output></div>
</div>
<div class="step">
  <h3>प्लूटोनियम भी जुड़ता है</h3>
  <p>यूरेनियम-238 न्यूट्रॉन पकड़कर प्लूटोनियम-239 बनता है, जो भी विखंडित होता है। जीवन के अंत में आधे से अधिक विखंडन प्लूटोनियम में होते हैं; पूरे जीवन में लगभग एक तिहाई ऊर्जा उसी से आती है।</p>
  <div class="ctl"><label for="bu-d2">पूर्ण शक्ति पर दिन</label><input id="bu-d2" type="range" data-bind="d" data-instant min="0" max="1400" step="10" value="1000"><output data-show="d" data-fmt="0"></output></div>
</div>
<div class="step">
  <h3>विष जमा होते हैं</h3>
  <p>हर विखंडन दो विखंडन उत्पाद छोड़ता है, और उनमें से कुछ न्यूट्रॉन सोख लेते हैं। यूरेनियम-235 घटने और विष बढ़ने से <i>k</i><sub>∞</sub> (इस ईंधन की अनंत जाली में प्रति विखंडन नए विखंडन) धीरे-धीरे घटता है, जब तक ईंधन अकेले शृंखला चालू नहीं रख पाता।</p>
  <div class="ctl"><label for="bu-d3">पूर्ण शक्ति पर दिन</label><input id="bu-d3" type="range" data-bind="d" data-instant min="0" max="1400" step="10" value="700"><output data-show="d" data-fmt="0"></output></div>
</div>
<div class="step">
  <h3>बोरॉन और ईंधन बदलना</h3>
  <p>कोर में ताजा, मध्यम आयु का और पुराना ईंधन मिला होता है। ताजे ईंधन में अभिक्रियाशीलता बहुत अधिक होती है, इसलिए शीतलक जल में घुला बोरॉन अतिरिक्त को सोख लेता है और धीरे-धीरे तनु किया जाता है। जब वह शून्य पर पहुंचता है, सबसे पुराना एक तिहाई बाहर जाता है और ताजा ईंधन भीतर आता है।</p>
  <div class="ctl"><label for="bu-m">पूर्ण शक्ति पर महीने</label><input id="bu-m" type="range" data-bind="m" data-instant min="0" max="54" step="0.5" value="8"><output data-show="m" data-fmt="1"></output></div>
</div>`,
};
Object.assign(WT.L.labels, {
  "illustrative model": "उदाहरणात्मक मॉडल",
  "{a} days · burnup {b} GWd/t": "{a} दिन · बर्नअप {b} GWd/t",
  "uranium{#}": "यूरेनियम{#}",
  "plutonium{#}": "प्लूटोनियम{#}",
  "other Pu": "अन्य Pu",
  "other plutonium": "अन्य प्लूटोनियम",
  "fission products": "विखंडन उत्पाद",
  "fission products (pairs)": "विखंडन उत्पाद (जोड़े)",
  "{a} in {#}": "{#} में {a}",
  "uranium{#}: the remaining ~{#}–{#} %": "यूरेनियम{#}: शेष ~{#}–{#} %",
  "plutonium's share": "प्लूटोनियम का हिस्सा",
  "fissions": "विखंडन",
  "fissions now": "अभी के विखंडन",
  "energy so far": "अब तक की ऊर्जा",
  "U{#}": "U{#}",
  "Pu": "Pu",
  "split": "विखंडित",
  "plutonium": "प्लूटोनियम",
  "each dot: {#} atom in {#}": "हर बिंदु: {#} परमाणु / {#}",
  "each dot: one atom in a thousand": "हर बिंदु: हजार में एक परमाणु",
  "k = {#}": "k = {#}",
  "GWd/t →": "GWd/t →",
  "burnup (GWd/t) →": "बर्नअप (GWd/t) →",
  "typical discharge": "सामान्य निष्कासन",
  "typical discharge {#}–{#}": "सामान्य निष्कासन {#}–{#}",
  "can't keep a chain going alone": "अकेले शृंखला नहीं चला सकता",
  "this fuel alone can no longer keep a chain going": "यह ईंधन अकेले अब शृंखला चालू नहीं रख सकता",
  "k∞ reaches {#}": "k∞ {#} पर पहुंचता है",
  "k∞ = {a}": "k∞ = {a}",
  "fission products catch {a} % of neutrons": "विखंडन उत्पाद {a} % न्यूट्रॉन पकड़ते हैं",
  "fresh": "ताजा",
  "{#} cycle": "{#} चक्र",
  "one cycle old": "एक चक्र पुराना",
  "{#} cycles": "{#} चक्र",
  "two cycles old": "दो चक्र पुराना",
  "reload": "ईंधन बदलाव",
  "boron (ppm)": "बोरॉन (ppm)",
  "boron in the water (ppm)": "पानी में बोरॉन (ppm)",
  "months →": "महीने →",
  "months at full power →": "पूर्ण शक्ति पर महीने →",
  "{a} ppm": "{a} ppm",
  "cycle {a} months · fuel leaves at {b} GWd/t": "चक्र {a} महीने · ईंधन {b} GWd/t पर निकलता है",
});
