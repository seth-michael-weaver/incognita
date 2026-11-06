/* Hindi: feedback (रिएक्टर स्थिरता और प्रतिपुष्टि) */
WT.L.ch.feedback = {
  num: "पाठ 1", title: "रिएक्टर स्थिरता और प्रतिपुष्टि", short: "प्रतिपुष्टि",
  html: `
<div class="step">
  <h3>एक लूप: शक्ति, ऊष्मा, अभिक्रियाशीलता</h3>
  <p>अधिक शक्ति ईंधन और पानी को गर्म करती है, और उनके तापमान अभिक्रियाशीलता <i>ρ</i> को बदलते हैं, जो शक्ति तय करती है। अभिक्रियाशीलता का एक चरण जोड़िए और संकेत को लूप में घूमते देखिए। ऋणात्मक गुणांकों के साथ लूप उसे पीछे धकेलता है।</p>
  <div class="ctl"><label for="fb-r">अभिक्रियाशीलता चरण (pcm)</label><input id="fb-r" type="range" data-bind="rs" data-instant min="50" max="300" step="10" value="200"><output data-show="rs" data-fmt="0"></output></div>
  <div class="btns"><button class="btn" data-act="fbIns">डालिए</button> <button class="btn ghost" data-act="fbRes">रीसेट</button></div>
</div>
<div class="step">
  <h3>डॉप्लर: तेज ब्रेक</h3>
  <p>गर्म ईंधन यूरेनियम-238 में बिना विखंडन के अधिक न्यूट्रॉन पकड़ता है (<a href="#doppler">डॉप्लर विस्तारण</a>)। ईंधन सेकंडों में गर्म होता है, इसलिए यह ब्रेक सबसे पहले लगता है, और जल रिएक्टरों में यह सदा ऋणात्मक होता है। यहां यही एकमात्र प्रतिपुष्टि है।</p>
  <div class="ctl"><label for="fb-d">डॉप्लर गुणांक (pcm/K)</label><input id="fb-d" type="range" data-bind="aD" data-instant min="-5" max="-1" step="0.1" value="-2.5"><output data-show="aD" data-fmt="1"></output></div>
  <div class="btns"><button class="btn" data-act="fbIns">डालिए</button> <button class="btn ghost" data-act="fbRes">रीसेट</button></div>
</div>
<div class="step">
  <h3>मंदक भी जुड़ता है</h3>
  <p>गर्म पानी कम घना होता है, इसलिए न्यूट्रॉनों को कम अच्छी तरह धीमा करता है। दाबित जल रिएक्टर में सामान्य बोरॉन स्तर पर इससे मंदक गुणांक भी ऋणात्मक हो जाता है: दूसरा, धीमा ब्रेक, और शक्ति नीचे स्थिर होती है।</p>
  <div class="ctl"><label for="fb-m">मंदक गुणांक (pcm/K)</label><input id="fb-m" type="range" data-bind="aM" data-instant min="-60" max="0" step="1" value="-30"><output data-show="aM" data-fmt="0"></output></div>
  <div class="btns"><button class="btn" data-act="fbIns">डालिए</button> <button class="btn ghost" data-act="fbRes">रीसेट</button></div>
</div>
<div class="step">
  <h3>जब प्रतिपुष्टि धनात्मक हो</h3>
  <p>यदि शीतलक का पद धनात्मक है और डॉप्लर पर भारी पड़ता है, तो अधिक शक्ति का अर्थ है अधिक अभिक्रियाशीलता, और शक्ति बेकाबू हो जाती है। जल रिएक्टर ऋणात्मक गुणांकों के साथ डिज़ाइन किए जाते हैं; कुछ डिज़ाइनों में, जैसे कम शक्ति पर RBMK में, रिक्ति गुणांक धनात्मक हो सकता था।</p>
  <div class="ctl"><label for="fb-c">शीतलक गुणांक (pcm/K)</label><input id="fb-c" type="range" data-bind="aM" data-instant min="-60" max="150" step="5" value="150"><output data-show="aM" data-fmt="0"></output></div>
  <div class="btns"><button class="btn" data-act="fbIns">डालिए</button> <button class="btn ghost" data-act="fbRes">रीसेट</button></div>
</div>`,
};
Object.assign(WT.L.labels, {
  "heat": "ऊष्मा",
  "heats water": "पानी गर्म करती है",
  "chain": "शृंखला",
  "chain reaction": "शृंखला अभिक्रिया",
  "αM +": "αM +",
  "αM −": "αM −",
  "αM {#}": "αM {#}",
  "αC +": "αC +",
  "αC −": "αC −",
  "αC {#}": "αC {#}",
  "αD −": "αD −",
  "P {#} %": "P {#} %",
  "fuel +{#} K": "ईंधन +{#} K",
  "fuel {#} K": "ईंधन {#} K",
  "fuel ΔT +{#} K": "ईंधन ΔT +{#} K",
  "fuel ΔT {#} K": "ईंधन ΔT {#} K",
  "water +{#} K": "पानी +{#} K",
  "water {#} K": "पानी {#} K",
  "water ΔT +{#} K": "पानी ΔT +{#} K",
  "water ΔT {#} K": "पानी ΔT {#} K",
  "ρ +{#} pcm": "ρ +{#} pcm",
  "ρ {#} pcm": "ρ {#} pcm",
  "ρ = ρext + αD ΔTf + αM ΔTm": "ρ = ρext + αD ΔTf + αM ΔTm",
  "C dT/dt = P − h (T − Tc)": "C dT/dt = P − h (T − Tc)",
  "Doppler α_D = {a} pcm/K": "डॉप्लर α_D = {a} pcm/K",
  "coolant α_C = {a} pcm/K": "शीतलक α_C = {a} pcm/K",
  "moderator α_M = {a} pcm/K": "मंदक α_M = {a} pcm/K",
  "inserted ρ_ext = {a}": "डाला गया ρ_ext = {a}",
  "+{a} pcm": "+{a} pcm",
  "power": "शक्ति",
  "last {#} s →": "पिछले {#} s →",
  "last {#} seconds →": "पिछले {#} सेकंड →",
  "power ran away · protection would shut it down": "शक्ति बेकाबू · सुरक्षा प्रणाली इसे बंद कर देती",
  "power ran away · in a real plant the protection system would shut it down": "शक्ति बेकाबू · असली संयंत्र में सुरक्षा प्रणाली इसे बंद कर देती",
  "steady at {#} % · press Insert": "{#} % पर स्थिर · ‘डालिए’ दबाइए",
  "steady at {#} % power · press Insert to add reactivity": "{#} % शक्ति पर स्थिर · अभिक्रियाशीलता जोड़ने के लिए ‘डालिए’ दबाइए",
  "power coefficient {a} pcm per {#} %: settles": "शक्ति गुणांक {a} pcm प्रति {#} %: स्थिर होती है",
  "power coefficient {a} pcm per {#} % power: self-stabilising": "शक्ति गुणांक {a} pcm प्रति {#} % शक्ति: स्व-स्थिरीकरण",
  "power coefficient +{a} pcm per {#} %: runs away": "शक्ति गुणांक +{a} pcm प्रति {#} %: बेकाबू",
  "power coefficient +{a} pcm per {#} % power: runs away": "शक्ति गुणांक +{a} pcm प्रति {#} % शक्ति: बेकाबू",
  "illustrative model": "उदाहरणात्मक मॉडल",
});
