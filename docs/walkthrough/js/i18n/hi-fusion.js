/* Hindi: fusion (अध्याय 29, संलयन ऊर्जा और कूलॉम अवरोध) */
WT.L.ch.fusion = {
  num: "अध्याय 29", title: "संलयन ऊर्जा और कूलॉम अवरोध", short: "संलयन",
  lead: "संलयन विखंडन से उलटी दिशा में चलता है: दो हल्के नाभिक जुड़ते हैं, और बना जोड़ा अपने भागों से हल्का होता है।",
  html: `
<div class="step">
  <h3>बंधन वक्र से संलयन ऊर्जा</h3>
  <p>दो हल्के नाभिकों को जोड़िए: यदि नया नाभिक बंधन वक्र पर ऊपर बैठता है, तो ऊर्जा निकलती है। लोहे के शिखर के पार जोड़ने में ऊर्जा लगती है।</p>
  <div class="ctl"><label for="fu-a">प्रत्येक हल्का नाभिक A</label><input id="fu-a" type="range" data-bind="fuse" data-instant min="2" max="60" step="1" value="2"><output data-show="fuse" data-fmt="0"></output></div>
  <p class="ctl-result" id="fu-fuse-out" aria-live="polite"></p>
</div>
<div class="step">
  <h3>कूलॉम अवरोध और सुरंगन</h3>
  <p>ड्यूटेरॉन को पीछे खींचिए और छोड़ दीजिए। दोनों नाभिक आवेशित हैं, इसलिए अधिकांश प्रहार पहाड़ी से टकराकर लौट आते हैं; कुछ सुरंगन से पार निकल जाते हैं।</p>
  <div class="ctl"><label for="fu-e">धक्का (keV)</label><input id="fu-e" type="range" data-bind="lE" min="0.5" max="2.6" step="0.01" value="1.7"><output data-show="E" data-fmt="0"></output></div>
  <div class="btns"><button class="btn" data-act="fire">दागें</button></div>
</div>
<div class="step">
  <h3>अभिक्रिया उत्पाद और Q-मान</h3>
  <p>जुड़ा हुआ जोड़ा दोनों भागों से हल्का है। लुप्त द्रव्यमान तेज़ कणों के रूप में उड़ जाता है।</p>
  <div class="btns fu-fuels"><button class="btn ghost" data-act="DT" aria-pressed="true">D–T</button> <button class="btn ghost" data-act="DD" aria-pressed="false">D–D</button> <button class="btn ghost" data-act="DHe" aria-pressed="false">D–³He</button> <button class="btn ghost" data-act="pB" aria-pressed="false">p–¹¹B</button></div>
</div>
<div class="step">
  <h3>तापनाभिकीय अभिक्रिया दर</h3>
  <p>गर्म गैस में सबसे तेज़ नाभिक पार निकलते हैं। हर चमक एक संलयन है।</p>
  <div class="ctl"><label for="fu-t">तापमान (keV)</label><input id="fu-t" type="range" data-bind="lT" min="0" max="2" step="0.01" value="1"><output data-show="T" data-fmt="1"></output></div>
</div>`,
};

// canvas labels of the fusion part (chapters 29-32)
Object.assign(WT.L.labels, {
  "B": "B",
  "Copper{#}": "तांबा{#}",
  "Coulomb hill": "कूलॉम पहाड़ी",
  "D–D": "D–D",
  "D–T": "D–T",
  "D–³He": "D–³He",
  "E = kT": "E = kT",
  "Gamow peak E₀": "गैमो शिखर E₀",
  "K {#} · field lines lost to the wall: {#}": "K {#} · दीवार पर खोई क्षेत्र रेखाएं: {#}",
  "Q = {#}": "Q = {#}",
  "Q = ∞: no heating needed": "Q = ∞: तापन की जरूरत नहीं",
  "Silicon{#} (SiC)": "सिलिकॉन{#} (SiC)",
  "Steel (iron{#})": "इस्पात (लोहा{#})",
  "Sun's core": "सूर्य का केंद्र",
  "TBR {#}": "TBR {#}",
  "Tungsten{#}": "टंगस्टन{#}",
  "Vanadium{#}": "वैनेडियम{#}",
  "after {#} years at {#} MW/m² · {#} MeV neutrons only · σ from INCOGNITA library v{#}": "{#} वर्ष बाद, {#} MW/m² पर · केवल {#} MeV न्यूट्रॉन · σ: INCOGNITA लाइब्रेरी v{#}",
  "almost never": "लगभग कभी नहीं",
  "alpha {#} MeV": "अल्फा {#} MeV",
  "axis, q = {#}": "अक्ष, q = {#}",
  "binding per nucleon (MeV)": "प्रति न्यूक्लिऑन बंधन (MeV)",
  "bubble-chamber view, magnetic field into the page: charged products curl, the neutron leaves no track": "बुलबुला-कक्ष दृश्य, चुंबकीय क्षेत्र पृष्ठ के भीतर: आवेशित उत्पाद मुड़ते हैं, न्यूट्रॉन कोई पथ नहीं छोड़ता",
  "burning on its own": "अपने आप जल रहा है",
  "cooled down: plasma lost": "ठंडा हुआ: प्लाज्मा खोया",
  "cooling": "ठंडा होता",
  "could not load the library file": "लाइब्रेरी फाइल लोड नहीं हो सकी",
  "deuteron": "ड्यूटेरॉन",
  "deuteron {#} keV": "ड्यूटेरॉन {#} keV",
  "deuteron: pull back, let go": "ड्यूटेरॉन: पीछे खींचें, छोड़ें",
  "drag or tap a point; it runs on its own": "कोई बिंदु खींचें या टैप करें; यह अपने आप चलता है",
  "easiest: {a} keV, nτT {b}": "सबसे आसान: {a} keV, nτT {b}",
  "edge: q = {#} · lines that cross it are lost": "किनारा: q = {#} · इसे पार करने वाली रेखाएं खो जाती हैं",
  "electron {#} keV": "इलेक्ट्रॉन {#} keV",
  "energy of the colliding pair (keV)": "टकराते जोड़े की ऊर्जा (keV)",
  "few are this fast": "इतने तेज़ कम ही हैं",
  "fusion rate: {a} the rate at {b} keV": "संलयन दर: {b} keV वाली दर का {a}",
  "grain boundary": "कण सीमा",
  "heating itself": "खुद को गर्म कर रहा है",
  "helium stays and gathers into bubbles; hydrogen mostly diffuses out": "हीलियम रुककर बुलबुलों में जमा होता है; हाइड्रोजन ज्यादातर विसरित होकर निकल जाता है",
  "helium {#} appm": "हीलियम {#} appm",
  "hill to climb: charge product Z₁Z₂ = {#}": "चढ़ने को पहाड़ी: आवेश गुणनफल Z₁Z₂ = {#}",
  "hold: heaters on (Q = fusion power / heating) · let go: heaters off, the plasma is on its own": "दबाए रखें: हीटर चालू (Q = संलयन शक्ति / तापन) · छोड़ें: हीटर बंद, प्लाज्मा अपने भरोसे",
  "hydrogen {#} appm": "हाइड्रोजन {#} appm",
  "ignition (Q = ∞)": "प्रज्वलन (Q = ∞)",
  "kT (keV)": "kT (keV)",
  "kT {#} keV · E₀ {#} keV · width {#} keV": "kT {#} keV · E₀ {#} keV · चौड़ाई {#} keV",
  "kT {a} keV · D–T {b} m³/s · {c}× D–D": "kT {a} keV · D–T {b} m³/s · D–D का {c}×",
  "keeps itself hot": "खुद को गर्म रखता है",
  "laps {#}": "चक्कर {#}",
  "lead–lithium": "सीसा–लिथियम",
  "liquid lithium": "द्रव लिथियम",
  "loading INCOGNITA's cross sections…": "INCOGNITA के अनुप्रस्थ काट लोड हो रहे हैं…",
  "missing {#} u  =  {#} MeV out": "लुप्त {#} u  =  {#} MeV बाहर",
  "n τE (s/m³)": "n τE (s/m³)",
  "negative: turns the other way": "ऋणात्मक: उलटी दिशा में घूमता है",
  "neutron escapes": "न्यूट्रॉन निकल जाता है",
  "peak near {#} keV": "शिखर लगभग {#} keV पर",
  "per fusion neutron · {#} neutrons · cross sections are simple fits": "प्रति संलयन न्यूट्रॉन · {#} न्यूट्रॉन · अनुप्रस्थ काट सरल फिट हैं",
  "plasma": "प्लाज्मा",
  "product ×{a}": "गुणनफल ×{a}",
  "push {a} keV · chance to tunnel head-on {b}": "धक्का {a} keV · सीधी टक्कर में सुरंगन संभावना {b}",
  "q = {#}": "q = {#}",
  "q = {#}/{#}: closes after {#} lap": "q = {#}/{#}: {#} चक्कर के बाद बंद",
  "q = {#}/{#}: closes after {#} laps": "q = {#}/{#}: {#} चक्करों के बाद बंद",
  "q = {#}: no simple fraction, the dots fill the circle": "q = {#}: सरल भिन्न नहीं, बिंदु वृत्त भर देते हैं",
  "screen radius is logarithmic: {#} fm to {#} fm": "स्क्रीन त्रिज्या लघुगणकीय: {#} fm से {#} fm",
  "shield": "कवच",
  "tap to fire": "टैप: दागें",
  "the cut, flat": "काट, समतल",
  "time slowed {a}×": "समय {a}× धीमा",
  "tries {#} · fused {#}": "प्रयास {#} · संलयित {#}",
  "tritium made, by depth": "गहराई के अनुसार बना ट्रिटियम",
  "triton": "ट्राइटॉन",
  "tunnels more easily": "आसानी से सुरंगन",
  "turns at {#} fm": "{#} fm पर लौटता है",
  "wall": "दीवार",
  "{#} MeV": "{#} MeV",
  "{#} cm": "{#} cm",
  "{#} in {a}": "{a} में {#}",
  "{#} keV": "{#} keV",
  "{#} keV = {#} million K": "{#} keV = {#} मिलियन K",
  "{a} %": "{a} %",
  "{a} + {a} → {b}: about {c} MeV released": "{a} + {a} → {b}: लगभग {c} MeV मुक्त",
  "{a} + {a} → {b}: costs {c} MeV": "{a} + {a} → {b}: {c} MeV खर्च",
  "{a} keV · chance {b}": "{a} keV · संभावना {b}",
  "{a} keV · nτ {b} · {c}": "{a} keV · nτ {b} · {c}",
  "{a} · two branches, equally likely": "{a} · दो शाखाएं, समान संभावना",
  "{a} · ρ up to {b} · {c} turns a second": "{a} · ρ अधिकतम {b} · {c} चक्कर प्रति सेकंड",
  "σ at {#} MeV:  (n,α) {#} mb · (n,p) {#} mb · (n,{#}n) {#} mb": "{#} MeV पर σ:  (n,α) {#} mb · (n,p) {#} mb · (n,{#}n) {#} mb",
  "⁶Li {#} · ⁷Li {#} · (n,{#}n) {#}": "⁶Li {#} · ⁷Li {#} · (n,{#}n) {#}",
  "⁶Li {#} · ⁷Li {#} · (n,{#}n) {#} · captured {#} · leaked {#}": "⁶Li {#} · ⁷Li {#} · (n,{#}n) {#} · पकड़े गए {#} · रिसे {#}",
  "⟨σv⟩ (m³/s)": "⟨σv⟩ (m³/s)",
});
