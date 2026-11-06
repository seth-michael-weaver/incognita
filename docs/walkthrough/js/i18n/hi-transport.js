/* Hindi: transport (न्यूट्रॉन परिवहन और मॉन्टे कार्लो) */
WT.L.ch.transport = {
  num: "पाठ 1", title: "न्यूट्रॉन परिवहन और मॉन्टे कार्लो", short: "मॉन्टे कार्लो",
  html: `
<div class="step">
  <h3>परिवहन समीकरण</h3>
  <p>ठीक-ठीक कहें तो न्यूट्रॉन कोणीय फ्लक्स <i>ψ</i>(<b>r</b>, <b>Ω</b>, <i>E</i>) के लिए बोल्ट्ज़मान समीकरण का पालन करते हैं: <b>Ω</b>·∇<i>ψ</i> + Σ<sub>t</sub><i>ψ</i> = ∫∫Σ<sub>s</sub><i>ψ</i>′ d<b>Ω</b>′d<i>E</i>′ + (<i>χ</i>/4π<i>k</i>)∫<i>ν</i>Σ<sub>f</sub><i>φ</i>′ d<i>E</i>′। मॉन्टे कार्लो इसे न्यूट्रॉनों को एक-एक करके चलाकर हल करता है: <i>s</i> = −ln <i>ξ</i> / Σ<sub>t</sub> उड़ो, फिर प्रकीर्णित हो, प्रगृहीत हो, या विखंडन कराओ।</p>
  <div class="btns"><button class="btn" data-act="trnew">नया न्यूट्रॉन</button></div>
</div>
<div class="step">
  <h3>जहां विसरण विफल होता है</h3>
  <p>विसरण मानता है कि हर दिशा में फ्लक्स लगभग समान है। यह किसी सतह से एक-दो मुक्त पथ के भीतर और प्रबल अवशोषकों में विफल हो जाता है। एकसमान स्रोत वाली पट्टिका में अवशोषण बढ़ाते हुए इसकी तुलना मॉन्टे कार्लो फ्लक्स से कीजिए।</p>
  <div class="ctl"><label for="tr-pa">अवशोषण Σ<sub>a</sub>/Σ<sub>t</sub></label><input id="tr-pa" type="range" data-bind="pa" data-instant min="0.05" max="0.8" step="0.05" value="0.5"><output data-show="pa" data-fmt="2"></output></div>
</div>
<div class="step">
  <h3>घात पुनरावृत्ति</h3>
  <p><i>k</i><sub>eff</sub> के लिए, हर पीढ़ी के विखंडन स्थल अगली पीढ़ी का स्रोत बनते हैं; <i>k</i> प्रति आरंभ किए गए न्यूट्रॉन जमा हुए स्थलों की संख्या है। एक गलत अनुमान से शुरू कीजिए, हर न्यूट्रॉन एक किनारे पर, और देखिए कि स्रोत कैसे फैलकर मूल मोड बन जाता है।</p>
  <div class="btns"><button class="btn" data-act="trbad">गलत अनुमान से फिर शुरू करें</button></div>
</div>
<div class="step">
  <h3>क्या स्रोत अभिसरित हुआ?</h3>
  <p>खानों में बंटे स्रोत की शैनन एन्ट्रॉपी <i>H</i> = −Σ <i>p</i><sub>b</sub> log<sub>2</sub> <i>p</i><sub>b</sub> स्रोत के स्थिर होते ही समतल हो जाती है; तभी पीढ़ियों का औसत लिया जाता है। <i>k</i> की त्रुटि-सीमा गिने गए इतिहासों के साथ 1/√<i>N</i> की तरह सिकुड़ती है।</p>
  <div class="ctl"><label for="tr-n">प्रति पीढ़ी इतिहास</label><input id="tr-n" type="range" data-bind="nh" data-instant min="100" max="2000" step="100" value="400"><output data-show="nh" data-fmt="0"></output></div>
</div>`,
};

Object.assign(WT.L.labels, {
  "vacuum": "निर्वात",
  "glow: collision density": "चमक: टक्कर घनत्व",
  "amber glow: where collisions pile up": "पीली चमक: जहां टक्करें जमा होती हैं",
  "tap the slab to start neutrons": "न्यूट्रॉन छोड़ने के लिए पट्टिका पर टैप करें",
  "scatter": "प्रकीर्णन",
  "capture": "प्रग्रहण",
  "fission": "विखंडन",
  "leak": "रिसाव",
  "chance to fly at least s:  e^(−Σₜ s)": "कम से कम s उड़ने की संभावना:  e^(−Σₜ s)",
  "{#} free paths": "{#} मुक्त पथ",
  "ξ = {#}  →  s = −ln ξ / Σₜ = {#} free paths": "ξ = {#}  →  s = −ln ξ / Σₜ = {#} मुक्त पथ",
  "infinite medium S/Σₐ": "अनंत माध्यम S/Σₐ",
  "Monte Carlo": "मॉन्टे कार्लो",
  "diffusion": "विसरण",
  "flux": "फ्लक्स",
  "diffusion vs Monte Carlo: +{#} % at the surface, +{#} % in the middle": "विसरण बनाम मॉन्टे कार्लो: सतह पर +{#} %, बीच में +{#} %",
  "diffusion vs Monte Carlo: +{#} % at the surface, {#} % in the middle": "विसरण बनाम मॉन्टे कार्लो: सतह पर +{#} %, बीच में {#} %",
  "diffusion vs Monte Carlo: {#} % at the surface, +{#} % in the middle": "विसरण बनाम मॉन्टे कार्लो: सतह पर {#} %, बीच में +{#} %",
  "diffusion vs Monte Carlo: {#} % at the surface, {#} % in the middle": "विसरण बनाम मॉन्टे कार्लो: सतह पर {#} %, बीच में {#} %",
  "tap: drop the source there": "टैप: स्रोत वहां रखें",
  "tap the slab to drop the whole source there": "पूरा स्रोत वहां रखने के लिए पट्टिका पर टैप करें",
  "generation {#}": "पीढ़ी {#}",
  "source · dashed: fundamental mode": "स्रोत · धराशायी: मूल मोड",
  "fission source · dashed: fundamental mode": "विखंडन स्रोत · धराशायी: मूल मोड",
  "source entropy H (bits)": "स्रोत एन्ट्रॉपी H (बिट)",
  "inactive | active": "निष्क्रिय | सक्रिय",
  "inactive  |  active generations": "निष्क्रिय  |  सक्रिय पीढ़ियां",
  "k per generation": "प्रति पीढ़ी k",
  "generation {#}: k = {#} · H = {#} bits": "पीढ़ी {#}: k = {#} · H = {#} बिट",
  "starting…": "शुरू हो रहा है…",
  "k_eff = {#} ± {#} ({#} × {#} histories) · diffusion {#}": "k_eff = {#} ± {#} ({#} × {#} इतिहास) · विसरण {#}",
  "{#} generations, averaging starts after {#}": "{#} पीढ़ियां, औसत {#} के बाद शुरू",
  "illustrative one-group data": "उदाहरणार्थ एक-समूह आंकड़े",
});
