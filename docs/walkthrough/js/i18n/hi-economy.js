/* Hindi: economy (न्यूट्रॉन अर्थव्यवस्था) */
WT.L.ch.economy = {
  num: "पाठ 1", title: "न्यूट्रॉन अर्थव्यवस्था", short: "न्यूट्रॉन अर्थव्यवस्था",
  html: `
<div class="step">
  <h3>एक हजार न्यूट्रॉन</h3>
  <p>1000 तेज न्यूट्रॉनों को एक पीढ़ी तक देखिए। कुछ अतिरिक्त विखंडन कराते हैं, कुछ बाहर रिस जाते हैं, कुछ रास्ते में पकड़ लिए जाते हैं, और बाकी यूरेनियम-235 का विखंडन करके अगले हजार बनाते हैं। छह गुणक मिलकर <i>k</i> = <i>η f p ε P</i><sub>FNL</sub> <i>P</i><sub>TNL</sub> बनाते हैं।</p>
</div>
<div class="step">
  <h3>संवर्धन</h3>
  <p>ईंधन में अधिक यूरेनियम-235 (ऊँचा संवर्धन स्तर) का अर्थ है कि अधिक न्यूट्रॉन वहां अवशोषित होते हैं जहां वे विखंडन कराते हैं। प्राकृतिक यूरेनियम (0.7 %) और साधारण पानी के साथ <i>k</i> कभी 1 तक नहीं पहुंचता।</p>
  <div class="ctl"><label for="eco-e">यूरेनियम-235 (%)</label><input id="eco-e" type="range" data-bind="enr" min="0.7" max="5" step="0.1" value="3"><output data-show="enr" data-fmt="1"></output></div>
</div>
<div class="step">
  <h3>छड़ों के बीच पानी</h3>
  <p>पानी बहुत कम हो तो धीमे होते न्यूट्रॉनों को यूरेनियम-238 पकड़ लेता है; बहुत अधिक हो तो पानी खुद उन्हें सोख लेता है। एक सर्वोत्तम अनुपात होता है, और जल रिएक्टर उससे थोड़ा नीचे बनाए जाते हैं।</p>
  <div class="ctl"><label for="eco-m">प्रति ईंधन पानी (× सामान्य)</label><input id="eco-m" type="range" data-bind="m" min="0.3" max="4" step="0.05" value="1"><output data-show="m" data-fmt="2"></output></div>
</div>
<div class="step">
  <h3>आकार</h3>
  <p>सतह के पास जन्मे न्यूट्रॉन बाहर निकल सकते हैं। छोटा कोर बहुत अधिक न्यूट्रॉन खो देता है; बड़ा उन्हें रोके रखता है। वह आकार ढूंढिए जहां <i>k</i> 1 को पार करता है।</p>
  <div class="ctl"><label for="eco-s">कोर का आकार (× सामान्य)</label><input id="eco-s" type="range" data-bind="s" min="0.3" max="2" step="0.05" value="0.6"><output data-show="s" data-fmt="2"></output></div>
</div>`,
};
Object.assign(WT.L.labels, {
  "fast fission": "तेज विखंडन",
  "fast leak": "तेज रिसाव",
  "leaks out, fast": "रिसाव, तेज",
  "U{#} catches": "U{#} पकड़ता है",
  "caught by U{#}": "U{#} द्वारा पकड़े गए",
  "slow leak": "धीमा रिसाव",
  "leaks out, slow": "रिसाव, धीमे",
  "water, steel…": "पानी, इस्पात…",
  "water, steel, boron": "पानी, इस्पात, बोरॉन",
  "P fast {#}": "P तेज {#}",
  "P slow {#}": "P धीमे {#}",
  "p {#}": "p {#}",
  "f {#}": "f {#}",
  "slowing": "मंदन",
  "slowing down": "मंदन",
  "{#} split U{#}": "{#} U{#} का विखंडन",
  "U{#}": "U{#}",
  "next: {#}": "अगली: {#}",
  "next generation: {#}": "अगली पीढ़ी: {#}",
  "k = {#}": "k = {#}",
  "critical: steady": "क्रांतिक: स्थिर",
  "grows": "बढ़ती है",
  "dies away": "समाप्त होती है",
  "best ≈ {#}×": "सर्वोत्तम ≈ {#}×",
  "less water": "कम पानी",
  "more water": "अधिक पानी",
  "{#} % leak out": "{#} % रिस जाते हैं",
  "k = η {#} × f {#} × p {#} × ε {#} × P {#} × P {#}": "k = η {#} × f {#} × p {#} × ε {#} × P {#} × P {#}",
  "textbook set (D&H); trends illustrative": "पाठ्यपुस्तक मान (D&H); रुझान उदाहरणात्मक",
  "factors: textbook set (Duderstadt & Hamilton) at {#} %; slider trends illustrative": "गुणक: पाठ्यपुस्तक मान (Duderstadt & Hamilton) {#} % पर; स्लाइडर के रुझान उदाहरणात्मक",
});
