/* Hindi: slowing (अध्याय 19, न्यूट्रॉन मंदन) */
WT.L.ch.slowing = {
  num: "अध्याय 19", title: "न्यूट्रॉन मंदन", short: "धीमा होना",
  html: `
<div class="step">
  <p>हाइड्रोजन से हर टकराव में लगभग आधी ऊर्जा चली जाती है। एक विखंडन न्यूट्रॉन 2 MeV से शुरू होकर पानी में टकराता चलता है। हाइड्रोजन नाभिक का भार न्यूट्रॉन के बराबर होता है, इसलिए बिलियर्ड की गेंदों की तरह हर टकराव औसतन न्यूट्रॉन की आधी ऊर्जा आगे सौंप देता है।</p>
  <p>चार्ट हर टकराव के बाद न्यूट्रॉन की ऊर्जा आलेखित करता है; किनारे पर हर अगला लेबल हजार गुना कम ऊर्जा दर्शाता है। हर बार समान अंश खोने से एक सीधी ढलान बनती है, बिंदीदार रेखा। लगभग 18 टकरावों के बाद न्यूट्रॉन <b>तापीय</b> ऊर्जा, 0.025 eV, पर पहुंचता है, जहां गर्म पानी उसे उतनी ही बार ऊपर उछालता है जितनी बार वह धीमा होता है। ऑक्सीजन 16 गुना भारी है: हर टकराव थोड़ा-सा ही लेता है, और सौ से अधिक चाहिए।</p>
  <div class="btns"><button class="btn ghost" data-act="tgtH" aria-pressed="true">हाइड्रोजन</button><button class="btn ghost" data-act="tgtO" aria-pressed="false">ऑक्सीजन</button><button class="btn" data-act="again">फिर दागें</button></div>
</div>
<div class="step">
  <p>लगभग 1 eV से नीचे, अणु के बंधन हर टकराव का स्वरूप तय करते हैं। हर हाइड्रोजन अपनी ऑक्सीजन से बंधा है (चमकीली रेखाएं)। धीमा न्यूट्रॉन अब मुक्त हाइड्रोजन से नहीं टकराता: वह पूरे अणु से टकराता है, जो 18 गुना भारी है, इसलिए साधारण टकराव लगभग कुछ नहीं लेता।</p>
  <p>वह अणु को घुमा या कंपा भी सकता है, पर केवल एक बार में निश्चित मात्रा की ऊर्जा देकर, 0.06, 0.2 या 0.45 eV (चमकीली चमकें)। गर्म अणु कभी-कभी ऐसी मात्रा वापस भी दे देते हैं। चार्ट पर 1 eV से नीचे की छायांकित पट्टी वह जगह है जहां यह मायने रखता है। मुक्त हाइड्रोजन से तुलना के लिए बंधन बंद कीजिए।</p>
  <div class="btns"><button class="btn ghost" data-act="bind" aria-pressed="true">रासायनिक बंधन</button><button class="btn" data-act="again">फिर दागें</button></div>
</div>
<div class="step">
  <p>कंप्यूटर कोड को यह सब एक तालिका के रूप में चाहिए: <b>प्रकीर्णन नियम</b>, यह नक्शा। आड़े: चोट कितनी जोर की है, α (अणु को दिया गया धक्का; हल्के स्पर्श के लिए छोटा, सीधी चोट के लिए बड़ा)। ऊपर-नीचे: न्यूट्रॉन की प्राप्त की (ऊपर) या खोई (नीचे) ऊर्जा, β, पानी की तापीय ऊर्जा 0.025 eV की इकाइयों में गिनी। चमकीला मतलब संभावित, हल्का मतलब दुर्लभ।</p>
  <p>रूपरेखा वह है जहां तक चुनी हुई ऊर्जा का न्यूट्रॉन पहुंच सकता है: वह अपने पास जितना है उससे अधिक नहीं खो सकता, और हर ऊर्जा-परिवर्तन के लिए चोटों की केवल एक सीमा संभव है। ऊर्जा खींचिए और रूपरेखा बढ़ती या घटती है। बंधन के बिना नक्शा मुक्त हाइड्रोजन गैस का है, बिंदीदार प्रतिक्षेप रेखा के साथ एक चमकीली मेड़; बंधन के साथ अणु चमकीली धारियां जोड़ता है, अपनी निश्चित ऊर्जा-मात्राओं की। INCOGNITA पानी और बेरिलियम के लिए अपने प्रकीर्णन नियम स्वयं गणना करता है: <a href="https://github.com/seth-michael-weaver/incognita/tree/main/library/tsl-v0.1" style="white-space:nowrap">tsl-v0.1</a>।</p>
  <div class="ctl"><label for="slo-e">न्यूट्रॉन ऊर्जा (eV)</label><input id="slo-e" type="range" data-bind="lgE" data-instant min="-2.3" max="0" step="0.01" value="-1"><output data-show="Eshow" data-fmt="3"></output></div>
  <div class="btns"><button class="btn ghost" data-act="bind" aria-pressed="true">रासायनिक बंधन</button></div>
</div>`,
};
/* attributes referenced in the English chapter script (for the structure check): data-act="${act}" */

// canvas labels added 2026-10-29 (I18NLABELS_B)
Object.assign(WT.L.labels, {
  "water · neutron hits hydrogen": "पानी · न्यूट्रॉन हाइड्रोजन से टकराता है",
  "thermal · kT ≈ {#} eV": "तापीय · kT ≈ {#} eV",
  "{#} meV": "{#} meV",
  "collisions →": "टकराव →",
  "energy": "ऊर्जा",
  "typical bounce: energy × {#} (theory × {#}) · {#} bounces to thermal": "सामान्य टकराव: ऊर्जा × {#} (सिद्धांत × {#}) · तापीय तक {#} टकराव",
  "typical: the average step along the dashed line (energy shares multiply, so the average is taken on this scale)": "सामान्य: बिंदीदार रेखा पर औसत कदम (ऊर्जा के अंश गुणा होते हैं, इसलिए औसत इसी पैमाने पर)",
  "bright line: a bond holding H to its O": "चमकीली रेखा: H को उसके O से जोड़ने वाला बंधन",
  "bright flash: the neutron left a fixed amount of energy in the molecule": "चमकीली चमक: न्यूट्रॉन ने अणु में निश्चित मात्रा की ऊर्जा छोड़ी",
  "below {#} eV: the bonds shape each bounce": "{#} eV से नीचे: बंधन हर टकराव तय करते हैं",
  "free-atom recoil": "मुक्त-परमाणु प्रतिक्षेप",
  "α: how hard the knock (momentum handed over) →": "α: चोट कितनी जोर की (दिया गया संवेग) →",
  "β: the neutron's energy change, in units of kT = {#} eV": "β: न्यूट्रॉन का ऊर्जा-परिवर्तन, kT = {#} eV की इकाइयों में",
  "gain ↑": "लाभ ↑",
  "loss ↓": "हानि ↓",
  "outline: reachable from {#} eV": "रूपरेखा: {#} eV से पहुंच योग्य",
  "rare → likely": "दुर्लभ → संभावित",
  "scattering law S(α,β) · hydrogen bound in water": "प्रकीर्णन नियम S(α,β) · पानी में बंधा हाइड्रोजन",
  "stripes: energy lost to the molecule in fixed amounts": "धारियां: निश्चित मात्राओं में अणु को दी गई ऊर्जा",
});
