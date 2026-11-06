/* Hindi: rays (अल्फा, बीटा, गामा और न्यूट्रॉन) */
WT.L.ch.rays = {
  num: "पाठ 1", title: "अल्फा, बीटा, गामा और न्यूट्रॉन", short: "विकिरण",
  html: `
<div class="step">
  <h3>विकिरण के चार प्रकार</h3>
  <p><em class="a">अल्फा</em> दो प्रोटॉनों और दो न्यूट्रॉनों का एक भारी गुच्छा है। <b>बीटा</b> एक तेज इलेक्ट्रॉन है। <em class="g">गामा</em> प्रकाश है, पर इतना ऊर्जावान कि दिखाई नहीं देता। <em class="n">न्यूट्रॉनों</em> पर कोई आवेश नहीं होता। हर एक को अलग-अलग चीजें रोकती हैं।</p>
</div>
<div class="step">
  <h3>कागज और एल्युमिनियम</h3>
  <p>अल्फा कण बड़े और आवेशित होते हैं, इसलिए वे तुरंत परमाणुओं से टकराते हैं: कागज की एक शीट उन्हें रोक देती है। बीटा इलेक्ट्रॉन आगे जाते हैं, पर कुछ मिलीमीटर एल्युमिनियम उन्हें भी रोक देता है।</p>
  <div class="btns"><button class="btn ghost" data-act="sh_paper" aria-pressed="true">कागज</button><button class="btn ghost" data-act="sh_al" aria-pressed="false">एल्युमिनियम</button></div>
</div>
<div class="step">
  <h3>गामा किरणें: आधी होती हैं, शून्य कभी नहीं</h3>
  <p>गामा किरणों पर कोई आवेश नहीं होता और वे प्रायः परमाणुओं के पास से निकल जाती हैं। सीसे का हर सेंटीमीटर हर किरण को पकड़े जाने की वही संभावना देता है, इसलिए हर परत बचे हुए को आधा कर देती है। किरण-पुंज मंद होता जाता है पर कभी पूरी तरह शून्य नहीं होता।</p>
  <div class="ctl"><label for="ry-pb">सीसा (cm)</label><input id="ry-pb" type="range" data-bind="pb" data-instant min="0" max="5" step="0.1" value="1"><output data-show="pb" data-fmt="1"></output></div>
</div>
<div class="step">
  <h3>न्यूट्रॉन: सीसा काफी नहीं</h3>
  <p>भारी सीसा नाभिक से टकराता न्यूट्रॉन वैसा ही है जैसे टेबल-टेनिस की गेंद बॉलिंग की गेंद से टकराए: उसकी चाल बनी रहती है। पानी में हाइड्रोजन का भार न्यूट्रॉन जितना ही है, इसलिए हर टक्कर उसे धीमा करती है, जब तक वह इतना धीमा न हो जाए कि निगल लिया जाए।</p>
  <div class="btns"><button class="btn ghost" data-act="nm_pb" aria-pressed="true">सीसा</button><button class="btn ghost" data-act="nm_water" aria-pressed="false">पानी</button></div>
  <div class="ctl"><label for="ry-nx">मोटाई (cm)</label><input id="ry-nx" type="range" data-bind="nx" data-instant min="0" max="60" step="1" value="30"><output data-show="nx" data-fmt="0"></output></div>
</div>
<div class="step">
  <h3>एक कवच बनाइए</h3>
  <p>परतें तब तक जोड़िए जब तक चारों पुंज रुक न जाएं। गामा किरणें कभी ठीक शून्य तक नहीं गिरतीं, केवल एक बहुत छोटे अंश तक।</p>
  <div class="btns"><button class="btn ghost" data-act="add_paper">+ कागज</button><button class="btn ghost" data-act="add_al">+ एल्युमिनियम</button><button class="btn ghost" data-act="add_pb">+ सीसा</button><button class="btn ghost" data-act="add_water">+ पानी</button><button class="btn" data-act="clear">साफ करें</button></div>
</div>`,
};
Object.assign(WT.L.labels, {
  "drag ↔": "खींचिए ↔",
  "paper": "कागज",
  "aluminium {#} mm": "एल्युमिनियम {#} mm",
  "Al {#} mm": "Al {#} mm",
  "lead {#} cm": "सीसा {#} cm",
  "water {#} cm": "पानी {#} cm",
  "no shield": "कोई कवच नहीं",
  "alpha": "अल्फा", "beta": "बीटा", "gamma": "गामा", "neutron": "न्यूट्रॉन",
  "stopped": "रुका",
  "all through": "सब पार",
  "{#} % through": "{#} % पार",
  "{#} in {#}": "{#}/{#}",
  "{#} in {#} million": "{#}/{#} मिलियन",
  "{#} in a billion": "अरब में {#}",
  "all four stopped": "चारों रुके",
  "all four beams stopped": "चारों पुंज रुके",
  "flash = stopped inside the shield": "चमक = कवच के भीतर रुका",
  "each source fires a steady beam": "हर स्रोत एक स्थिर पुंज छोड़ता है",
  "flash = stopped": "चमक = रुका",
  "four beams": "चार पुंज",
  "not to scale": "पैमाने पर नहीं",
  "gamma rays (caesium{#})": "गामा किरणें (सीज़ियम{#})",
  "cm of lead": "सीसे के cm",
  "share still going": "आगे जाता अंश",
  "through: all · halved every {#} mm": "पार: सब · हर {#} mm पर आधा",
  "through: {#} % · halved every {#} mm": "पार: {#} % · हर {#} mm पर आधा",
  "through: {#} in {#} · halved every {#} mm": "पार: {#}/{#} · हर {#} mm पर आधा",
  "through: {#} in {#} million · halved every {#} mm": "पार: {#}/{#} मिलियन · हर {#} mm पर आधा",
  "gets through: {#} % · halved every {#} mm of lead": "पार होता है: {#} % · सीसे के हर {#} mm पर आधा",
  "gets through: {#} in {#} · halved every {#} mm of lead": "पार होता है: {#}/{#} · सीसे के हर {#} mm पर आधा",
  "gets through: {#} in {#} million · halved every {#} mm of lead": "पार होता है: {#}/{#} मिलियन · सीसे के हर {#} mm पर आधा",
  "counted: {#} of {#}": "गिने गए: {#} / {#}",
  "through {#} % · back {#} % · caught {#} %": "पार {#} % · वापस {#} % · पकड़े {#} %",
  "got through {#} % · bounced back {#} % · slowed and caught {#} %": "पार हुए {#} % · लौट आए {#} % · धीमे होकर पकड़े गए {#} %",
  "bright = fast · dim = slowed": "चमकीला = तेज · मंद = धीमा",
  "bright = fast neutron · red = hydrogen nucleus knocked away · green flash = swallowed": "चमकीला = तेज न्यूट्रॉन · लाल = धकेला गया हाइड्रोजन नाभिक · हरी चमक = निगला गया",
  "simplified model": "सरलीकृत मॉडल",
});
