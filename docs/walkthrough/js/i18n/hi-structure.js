/* Hindi: structure (अध्याय 1, नाभिक किससे बना है) */
WT.L.ch.structure = {
  num: "अध्याय 1", title: "नाभिक किससे बना है", short: "संरचना",
  lead: "इंजन (हमारा अभिक्रिया सॉफ्टवेयर) एक भी न्यूट्रॉन दागने से पहले लक्ष्य नाभिक का विवरण चाहता है: वह कितनी मजबूती से बंधा है, किन ऊर्जा अवस्थाओं में हो सकता है, और उसकी आकृति कैसी है।",
  html: `
<div class="step">
  <p>चित्र एक लोहे का नाभिक दिखाता है: <em class="p">प्रोटॉनों</em> और <em class="n">न्यूट्रॉनों</em> (<b>न्यूक्लिऑनों</b>) की एक ठसाठस भरी गेंद, जिसे कम परास वाला <b>प्रबल बल</b> बांधे रखता है। हर न्यूक्लिऑन केवल अपने निकटतम पड़ोसियों को महसूस करता है, इसलिए हर नाभिक का घनत्व लगभग समान होता है।</p>
  <div class="ctl"><label for="st-n">न्यूट्रॉन (लोहे में 26 प्रोटॉन हैं)</label><input id="st-n" type="range" data-bind="N" min="24" max="38" step="1" value="30" data-instant><output data-show="N" data-fmt="0"></output></div>
  <p>न्यूट्रॉन जोड़ने या हटाने के लिए खींचिए; हर विकल्प एक अलग <b>समस्थानिक</b> (isotope) है। पट्टियां प्रति न्यूक्लिऑन <b>बंधन ऊर्जा</b> MeV (मिलियन इलेक्ट्रॉन-वोल्ट) में दिखाती हैं: नाभिक को अलग-अलग करने के लिए आवश्यक ऊर्जा। यह स्थायी समस्थानिकों के पास अधिकतम होती है।</p>
</div>
<div class="step">
  <h3>एक कण बाहर निकालने की कीमत</h3>
  <p>एक कण को बाहर निकालने की ऊर्जा उसकी <b>पृथक्करण ऊर्जा</b> है: न्यूट्रॉन के लिए <i>S<sub>n</sub></i>, प्रोटॉन के लिए <i>S<sub>p</sub></i>, <b>अल्फा कण</b> (दो प्रोटॉन और दो न्यूट्रॉन एक साथ बंधे हुए) के लिए <i>S<sub>α</sub></i>। चित्र नाभिक को एक कूप के रूप में दिखाता है, ऊर्जा ऊपर की ओर बढ़ती है; हर खिंचाव सबसे ऊपर के कण को धराशायी "मुक्त" रेखा के पार उठा देता है, और मीटर कीमत दर्ज करता है।</p>
  <div class="btns"><button class="btn ghost" data-act="pn">न्यूट्रॉन निकालें</button><button class="btn ghost" data-act="pp">प्रोटॉन निकालें</button><button class="btn ghost" data-act="pa">अल्फा निकालें</button></div>
  <p>इंजन हर एक को दो नाभिकीय द्रव्यमानों के अंतर के रूप में प्राप्त करता है: जहाँ संभव हो मापा गया, जहाँ नहीं वहाँ द्रव्यमान मॉडल से।</p>
  <div class="ctl"><label for="st-n2">न्यूट्रॉन</label><input id="st-n2" type="range" data-bind="N" min="24" max="38" step="1" value="30" data-instant><output data-show="N" data-fmt="0"></output></div>
  <p>न्यूट्रॉनों की संख्या बदलिए और फिर से एक न्यूट्रॉन निकालिए: <i>S<sub>n</sub></i> टेढ़ा-मेढ़ा ऊपर-नीचे होता है, क्योंकि न्यूक्लिऑन जोड़े बनाते हैं और सम संख्या अंतिम न्यूक्लिऑन को अधिक कसकर पकड़ती है। कोई अभिक्रिया किसी कण को तभी बाहर फेंक सकती है जब वह यह कीमत चुकाने लायक ऊर्जा लाए। ये कीमतें पूरी गणना की <b>देहलियां</b> (thresholds) हैं।</p>
</div>
<div class="step">
  <h3>ऊर्जा स्तर, और नीचे गिरना</h3>
  <p>एक नाभिक अतिरिक्त ऊर्जा की केवल कुछ निश्चित मात्राएं ही रख सकता है: ये रेखाएं, यहाँ लोहा-56 के लिए, सबसे नीचे <b>मूल अवस्था</b> के साथ। हर स्तर का एक <b>प्रचक्रण</b> (spin) <i>J</i> (कोणीय संवेग) और एक <b>समता</b> (parity), + या −, होती है (कि दर्पण में उसकी तरंग वैसी ही दिखती है या नहीं); 2<sup>+</sup> का अर्थ है प्रचक्रण 2, समता +।</p>
  <p>नारंगी गेंद एक ऊंचे स्तर पर स्थित नाभिक है। यह एक-एक स्तर नीचे गिरती है, और हर छलांग एक <em class="g">फोटॉन</em> (एक गामा किरण) फेंकती है जो ऊर्जा का अंतर ले जाता है। रास्तों की चौड़ाई और प्रतिशत हर छलांग की मापी गई संभावना हैं, यानी <b>शाखन अनुपात</b>।</p>
  <div class="btns"><button class="btn" data-act="drop">नाभिक को उत्तेजित करें</button></div>
  <p>इसे कुछ बार दबाइए: वही स्तर अलग-अलग रास्तों से मूल अवस्था तक पहुंचता है। इंजन हर नाभिक के लगभग तीस मापे गए स्तर उनकी संभावनाओं के साथ रखता है; उससे ऊपर वह भीड़ भरे स्तरों को एक चिकने <b>सातत्य</b> (continuum) के रूप में लेता है। धराशायी रेखा <i>S<sub>n</sub></i> के ऊपर नाभिक एक न्यूट्रॉन उत्सर्जित कर सकता है।</p>
</div>
<div class="step">
  <h3>ऐसा स्तर जिससे नीचे आना आसान नहीं</h3>
  <p>जिस स्तर से नीचे आने का एकमात्र रास्ता प्रचक्रण में बड़ा परिवर्तन, Δ<i>J</i>, मांगता है, उसका क्षय बहुत धीरे होता है। दाईं ओर 64 नाभिक ऐसे स्तर पर बैठे हैं; हर एक यादृच्छिक समय तक प्रतीक्षा करता है, फिर गिरता है और एक <em class="g">फोटॉन</em> निकल आता है। एक <b>अर्ध-आयु</b> के बाद आधे गिर चुके होते हैं।</p>
  <div class="ctl"><label for="st-dj">प्रचक्रण परिवर्तन ΔJ</label><input id="st-dj" type="range" data-bind="dJ" min="1" max="5" step="1" value="2" data-instant><output data-show="dJ" data-fmt="0"></output></div>
  <div class="ctl"><label for="st-eg">फोटॉन ऊर्जा (MeV)</label><input id="st-eg" type="range" data-bind="Eg" min="0.05" max="1.5" step="0.05" value="0.3"><output data-show="Eg" data-fmt="2"></output></div>
  <div class="btns"><button class="btn ghost" data-act="excite">सभी को उत्तेजित करें</button></div>
  <p>Δ<i>J</i> बढ़ाइए और फोटॉन निकलना धीमा हो जाता है: प्रचक्रण की हर अतिरिक्त इकाई प्रतीक्षा को एक लाख गुना या उससे भी अधिक लंबा कर देती है, और कम फोटॉन ऊर्जा भी इसे लंबा करती है (लघुगणकीय पैमाने पर दिखाया गया)। जो स्तर लगभग एक सेकंड से अधिक जीवित रहता है, वह <b>समावयवी</b> (isomer) है, और इंजन उसे मूल अवस्था की तरह एक अंतिम बिंदु मानता है।</p>
</div>
<div class="step">
  <h3>गोल, या नहीं</h3>
  <p>कई नाभिक गोल नहीं होते। <i>β₂</i> ("बीटा-टू") खिंचाव को मापता है: 0 एक गोला है, धनात्मक का अर्थ है अमेरिकी फुटबॉल की तरह खिंचा हुआ, ऋणात्मक का अर्थ है चपटा होकर तश्तरी जैसा। दाईं ओर की सीढ़ी दिखाती है कि हर प्रकार कैसे स्तर बनाता है।</p>
  <p>खिंचा हुआ नाभिक घूम सकता है, जिससे स्तर 0<sup>+</sup>, 2<sup>+</sup>, 4<sup>+</sup>, 6<sup>+</sup> बनते हैं जिनके अंतराल <i>J</i>(<i>J</i>+1) की तरह बढ़ते हैं: एक <b>घूर्णक</b> (rotor)। गोल नाभिक लहरा सकता है; लहर की हर इकाई, एक <b>फोनॉन</b>, समान ऊर्जा जोड़ती है, इसलिए इसके स्तर समान दूरी पर होते हैं: एक <b>कंपनशील नाभिक</b> (vibrator)।</p>
  <div class="ctl"><label for="st-beta">विरूपण β₂</label><input id="st-beta" type="range" data-bind="beta" min="-0.3" max="0.45" step="0.01" value="0.28"><output data-show="beta" data-fmt="2"></output></div>
  <div class="btns"><button class="btn ghost" data-act="still">स्थिर</button><button class="btn ghost" data-act="vib">कंपन</button><button class="btn ghost" data-act="rot">घूर्णन</button></div>
  <p><i>β₂</i> को खींचिए और बटन दबाइए: अधिक खिंचाव घूर्णक के स्तरों को पास ले आता है। इंजन हर नाभिक के लिए विरूपण और एक टैग रखता है: गोलीय, कंपनशील या घूर्णक। अध्याय 6 दिखाता है कि पास से गुजरता न्यूट्रॉन इनका उपयोग कैसे करता है।</p>
</div>
<div class="step">
  <h3>देहली के ठीक ऊपर उंगलियों के निशान</h3>
  <p>लक्ष्य से जुड़ने वाला एक धीमा न्यूट्रॉन <i>S<sub>n</sub></i> के ठीक ऊपर पहुंचता है, बाईं ओर के छोटे बॉक्स में। दायां पैनल उस बॉक्स को हजारों गुना बड़ा करके दिखाता है, न्यूट्रॉन ऊर्जा बाएं से दाएं बढ़ती है।</p>
  <div class="ctl"><label for="st-fe">किरणपुंज ऊर्जा</label><input id="st-fe" type="range" data-bind="fe" min="0" max="1" step="0.001" value="0.3" data-instant><output id="st-fe-out"></output></div>
  <div class="btns"><button class="btn ghost" data-act="fplay" id="st-fplay">स्वीप रोकें</button></div>
  <p>अधिकांश ऊर्जाओं पर किरणपुंज सीधे पार निकल जाता है। कुछ निश्चित ऊर्जाओं पर न्यूट्रॉन और नाभिक मिलकर एक छिपे स्तर से मेल खाते हैं और किरणपुंज का बड़ा भाग भीतर ले लिया जाता है: एक <b>अनुनाद</b>। शिखर पर बनाया गया नाभिक फूल जाता है: यह आकार का वास्तविक परिवर्तन नहीं है, बल्कि वह बड़ा लक्ष्य है जो न्यूट्रॉन प्रभावी रूप से देखता है जब उसकी तरंग नाभिक की तरंग पर चढ़ती है। फिर नाभिक ऊर्जा को एक <em class="g">फोटॉन</em> या एक न्यूट्रॉन के रूप में लौटा देता है। वक्र भीतर लिया गया भाग दिखाता है; पट्टियां मिले हर अनुनाद को चिह्नित करती हैं।</p>
  <div class="btns"><button class="btn ghost" data-act="fFe">लोहा-56</button><button class="btn ghost" data-act="fAu">सोना-197</button><button class="btn ghost" data-act="fU">यूरेनियम-238</button></div>
  <p>हर नाभिक का अपना बारकोड अपने पैमाने पर है: लोहे के अनुनादों के बीच हजारों इलेक्ट्रॉन-वोल्ट, सोने और यूरेनियम के लिए दसियों। तीन औसत इसका सार देते हैं: <i>D₀</i>, औसत अंतराल; ⟨Γ<sub>γ</sub>⟩, <b>फोटॉन चौड़ाई</b>, जो हर शिखर के लिए लगभग समान है; और <i>S₀</i>, <b>सामर्थ्य फलन</b> (strength function), यानी एक धीमा न्यूट्रॉन कितनी आसानी से भीतर जाता है।</p>
  <p>हर एक किसी बाद के चरण की जांच करता है। इंजन के स्तर-घनत्व प्राचल <i>D₀</i> पर, नाभिक-दर-नाभिक, फिट किए गए थे; ⟨Γ<sub>γ</sub>⟩ फोटॉन उत्सर्जन को परखता है, <i>S₀</i> अगले अध्याय के प्रकाशीय मॉडल को। जिन नाभिकों का मापन नहीं हुआ, उनके लिए इंजन कई नाभिकों पर फिट की गई प्रवृत्तियों का उपयोग करता है।</p>
  <div class="aside">कोड में: <code>structure/masses.py</code> (मापे गए द्रव्यमान, उनसे आगे मॉडल द्रव्यमान, पृथक्करण ऊर्जाएं), <code>structure/levels.py</code> (विविक्त स्तर, शाखन, समावयवी, अनुमानित प्रचक्रण) और <code>levjpar.py</code> (वैकल्पिक, डिफॉल्ट रूप से बंद: नाभिक के लिए असंभव सूचीबद्ध प्रचक्रण का फिर से अनुमान लगाता है), <code>structure/deformation.py</code> (β₂ और गोलीय/कंपनशील/घूर्णक टैग) और <code>collrule.py</code> (वैकल्पिक, डिफॉल्ट रूप से बंद: लक्ष्य का टैग उसके मापे गए स्तरों से चुनता है), <code>structure/resonances.py</code> (D₀, S₀, S₁, ⟨Γγ⟩)।</div>
</div>
`,
};
(function () {
  const L = {
    // scene: packed drop
    "{#}Fe": "{#}Fe",
    "{#} protons · {#} neutrons": "{#} प्रोटॉन · {#} न्यूट्रॉन",
    "binding energy per nucleon: about {#} MeV": "प्रति न्यूक्लिऑन बंधन ऊर्जा: लगभग {#} MeV",
    "binding per nucleon, one bar per isotope →": "प्रति न्यूक्लिऑन बंधन, हर समस्थानिक की एक पट्टी →",
    // scene: well
    "free": "मुक्त",
    "free: outside the nucleus": "मुक्त: नाभिक के बाहर",
    "neutrons": "न्यूट्रॉन",
    "protons": "प्रोटॉन",
    "an alpha forms from the top pairs": "ऊपर के जोड़ों से अल्फा बनता है",
    "neutron {#}": "न्यूट्रॉन {#}",
    "proton {#}": "प्रोटॉन {#}",
    "alpha {#}": "अल्फा {#}",
    "n {#}": "n {#}",
    "p {#}": "p {#}",
    "energy paid": "चुकाई गई ऊर्जा",
    "energy to pull": "निकालने की ऊर्जा",
    "(MeV)": "(MeV)",
    "each one out (MeV)": "हर एक (MeV)",
    "higher mark =": "ऊंचा निशान =",
    "harder to remove": "निकालना कठिन",
    "pulling out a neutron: {#} MeV paid": "न्यूट्रॉन निकाला: {#} MeV चुकाए",
    "pulling out a proton: {#} MeV paid": "प्रोटॉन निकाला: {#} MeV चुकाए",
    "pulling out an alpha: {#} MeV paid": "अल्फा निकाला: {#} MeV चुकाए",
    // scene: levels and gamma drops
    "continuum: too many levels to list": "सातत्य: सूची के लिए बहुत अधिक स्तर",
    "neutron threshold Sₙ ≈ {#} MeV": "न्यूट्रॉन देहली Sₙ ≈ {#} MeV",
    "ground state": "मूल अवस्था",
    "MeV": "MeV",
    "each line: an energy, a spin J and a parity (±)": "हर रेखा: एक ऊर्जा, प्रचक्रण J और समता (±)",
    "path width and % = measured odds of each hop": "रास्ते की चौड़ाई और % = हर छलांग की मापी गई संभावना",
    // scene: isomer
    "ground": "मूल",
    "J = {#}/{#}": "J = {#}/{#}",
    "ΔJ = {#}": "ΔJ = {#}",
    "still excited: {#} of {#}": "अभी उत्तेजित: {#}, कुल {#} में से",
    "longer than a second: an isomer, a stop in its own right": "एक सेकंड से अधिक: समावयवी, अपने आप में एक पड़ाव",
    "shown slowed down (log scale)": "धीमा करके दिखाया (लघुगणकीय)",
    "shown slowed down: the slower they pop, the longer the real wait (log scale)": "धीमा करके दिखाया: जितना धीमे निकलें, वास्तविक प्रतीक्षा उतनी लंबी (लघुगणकीय)",
    // scene: shape
    "ripples at the surface: a vibrator": "सतह पर लहरें: कंपनशील",
    "stretched and rotating: a rotor": "खिंचा और घूमता: घूर्णक",
    "round: a sphere": "गोल: एक गोला",
    "stretched (prolate): a football": "खिंचा (दीर्घवृत्तीय): फुटबॉल",
    "squashed: an oblate disc": "चपटा: तश्तरी",
    "{#} phonons": "{#} फोनॉन",
    "no regular": "कोई नियमित",
    "level pattern": "स्तर पैटर्न नहीं",
    "spacing grows like J(J+{#})": "अंतराल J(J+{#}) की तरह बढ़ता है",
    "equal steps, one phonon each": "समान कदम, हर एक में एक फोनॉन",
    "its lowest levels": "इसके सबसे निचले स्तर",
    "β₂ = {#}": "β₂ = {#}",
    // scene: resonance fingerprint
    "continuum": "सातत्य",
    "Sₙ ≈ {#} MeV": "Sₙ ≈ {#} MeV",
    "slow neutron": "धीमा न्यूट्रॉन",
    "a slow neutron lands here:": "धीमा न्यूट्रॉन यहाँ पहुंचता है:",
    "lands here": "यहाँ पहुंचता है",
    "Sₙ + its kinetic energy": "Sₙ + इसकी गतिज ऊर्जा",
    "×{#} million": "×{#} मिलियन",
    "×{#} thousand": "×{#} हजार",
    "magnified": "आवर्धित",
    "swells on a peak: the size the neutron effectively “sees” (waves overlap), not a real size change": "शिखर पर फूलता है: वह आकार जो न्यूट्रॉन प्रभावी रूप से “देखता” है (तरंगें मिलती हैं), वास्तविक आकार परिवर्तन नहीं",
    "share taken in": "भीतर लिया गया भाग",
    "share of the beam taken in": "किरणपुंज का भीतर लिया गया भाग",
    "{#} (Sₙ)": "{#} (Sₙ)",
    "{#} = exactly Sₙ": "{#} = ठीक Sₙ",
    "{#} keV": "{#} keV",
    "{#} eV": "{#} eV",
    "neutron energy →": "न्यूट्रॉन ऊर्जा →",
    "neutron's kinetic energy →": "न्यूट्रॉन की गतिज ऊर्जा →",
    "D₀ ≈ {#} keV: the average gap": "D₀ ≈ {#} keV: औसत अंतराल",
    "D₀ ≈ {#} eV: the average gap": "D₀ ≈ {#} eV: औसत अंतराल",
    "S₀: average peak strength": "S₀: शिखरों की औसत सामर्थ्य",
    "S₀: how strong the peaks are on average (how easily a neutron gets in)": "S₀: शिखर औसतन कितने प्रबल हैं (न्यूट्रॉन कितनी आसानी से भीतर जाता है)",
    "⟨Γγ⟩ ≈ {#} eV: photon width": "⟨Γγ⟩ ≈ {#} eV: फोटॉन चौड़ाई",
    "⟨Γγ⟩ ≈ {#} eV: photon width, about the same for every peak": "⟨Γγ⟩ ≈ {#} eV: फोटॉन चौड़ाई, हर शिखर के लिए लगभग समान",
    "⟨Γγ⟩ ≈ {#} eV: a hairline here": "⟨Γγ⟩ ≈ {#} eV: यहाँ एक बाल जितनी",
    "⟨Γγ⟩ ≈ {#} eV: a hairline here; neutrons widen these peaks": "⟨Γγ⟩ ≈ {#} eV: यहाँ बाल जितनी; न्यूट्रॉन इन शिखरों को चौड़ा करते हैं",
    "peaks drawn about {#}× wider than life so they show": "शिखर लगभग {#}× चौड़े बनाए गए हैं ताकि दिखें",
  };
  // beam readout and per-target labels
  for (const u of ["keV", "eV"]) L[`beam of neutrons at {#} ${u}`] = `{#} ${u} पर न्यूट्रॉन किरणपुंज`;
  const EL = { iron: "लोहा", gold: "सोना", uranium: "यूरेनियम" };
  for (const en in EL) {
    L[`${en}{#} levels`] = `${EL[en]}{#} के स्तर`;
    L[`${en}{#}: took in {#} of the last {#}`] = `${EL[en]}{#}: {#} भीतर लिए, पिछले {#} में से`;
  }
  // isomer half-life in every unit fmtTime can produce
  const TU = { femtoseconds: "फेम्टोसेकंड", picoseconds: "पिकोसेकंड", nanoseconds: "नैनोसेकंड", microseconds: "माइक्रोसेकंड",
    milliseconds: "मिलीसेकंड", seconds: "सेकंड", minutes: "मिनट", hours: "घंटे", days: "दिन", years: "वर्ष" };
  for (const en in TU) L[`half-life about {#} ${en}`] = `अर्ध-आयु लगभग {#} ${TU[en]}`;
  L["half-life about {#}×{#}^{#} years"] = "अर्ध-आयु लगभग {#}×{#}^{#} वर्ष";
  Object.assign(WT.L.labels, L);
})();
