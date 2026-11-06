/* Hindi: rwater (जल-शीतित रिएक्टर) */
WT.L.ch.rwater = {
  num: "पाठ 1", title: "जल-शीतित रिएक्टर", short: "जल रिएक्टर",
  lead: "आज लगभग हर बिजली रिएक्टर पानी से ठंडा किया जाता है। अंतर इसमें है कि पानी ऊष्मा को बाहर कैसे ले जाता है।",
  html: `
<div class="step">
  <h3>दाबित जल (PWR)</h3>
  <p>उच्च दाब पर पानी ऊष्मा को भाप जनित्र तक ले जाता है; दूसरा लूप भाप बनाता है।</p>
</div>
<div class="step">
  <h3>क्वथन जल (BWR)</h3>
  <p>पानी कोर में ही उबलता है और भाप सीधे टरबाइन में जाती है: केवल एक लूप।</p>
</div>
<div class="step">
  <h3>भारी पानी (CANDU)</h3>
  <p>भारी पानी न्यूट्रॉनों को धीमा करता है, पर उन्हें बहुत कम सोखता है, इसलिए प्राकृतिक यूरेनियम ही काफी है।</p>
</div>
<div class="step">
  <h3>ग्रेफाइट और उबलता पानी (RBMK)</h3>
  <p>ग्रेफाइट न्यूट्रॉनों को धीमा करता है; पानी सैकड़ों अलग-अलग नलियों में उबलता है।</p>
</div>
<div class="step">
  <h3>छोटा मॉड्यूलर (SMR)</h3>
  <p>एक छोटा PWR, जिसमें सब कुछ एक ही पात्र में है और जो कारखाने में बनता है।</p>
</div>
<div class="step">
  <h3>अतिक्रांतिक जल (SCWR)</h3>
  <p>221 bar से ऊपर पानी कभी नहीं उबलता, इसलिए वह अधिक गर्म चल सकता है और अधिक ऊष्मा को बिजली में बदल सकता है।</p>
</div>`,
};
Object.assign(WT.L.labels, {
  "BWR": "BWR",
  "CANDU; Canada, India, Romania, Argentina": "CANDU; कनाडा, भारत, रोमानिया, अर्जेंटीना",
  "Generation IV design, not yet built": "चौथी पीढ़ी का डिज़ाइन, अभी बना नहीं",
  "NuScale (US), Linglong One (China)": "NuScale (अमेरिका), लिंगलोंग वन (चीन)",
  "PHWR": "PHWR",
  "PWR": "PWR",
  "RBMK": "RBMK",
  "SCWR": "SCWR",
  "SMR": "SMR",
  "about {#} % of reactors; US, Japan, Sweden": "लगभग {#} % रिएक्टर; अमेरिका, जापान, स्वीडन",
  "about {#} in {#} of the world's reactors": "दुनिया के हर {#} में से लगभग {#} रिएक्टर",
  "all in one vessel": "सब एक पात्र में",
  "boiling water in tubes": "नलियों में उबलता पानी",
  "boils in the core": "कोर में उबलता है",
  "calandria: cool heavy water": "कैलेंड्रिया: ठंडा भारी पानी",
  "calandria: cool heavy water slows the neutrons": "कैलेंड्रिया: ठंडा भारी पानी न्यूट्रॉनों को धीमा करता है",
  "condenser": "संघनित्र",
  "control rods from below": "नियंत्रण छड़ें नीचे से",
  "coolant out": "शीतलक निकास",
  "core": "कोर",
  "core, pump-free loop and steam generator in one vessel": "कोर, बिना पंप का लूप और भाप जनित्र एक ही पात्र में",
  "electricity": "बिजली",
  "gen.": "जनित्र",
  "generator": "जनित्र",
  "graphite": "ग्रेफाइट",
  "graphite blocks slow the neutrons": "ग्रेफाइट खंड न्यूट्रॉनों को धीमा करते हैं",
  "horizontal pressure tubes, refuelled while running": "क्षैतिज दाब नलियां, चलते-चलते ईंधन बदला जाता है",
  "illustration": "चित्रण",
  "outlet": "निकास",
  "pressure": "दाब",
  "pressure tubes": "दाब नलियां",
  "reactor vessel": "रिएक्टर पात्र",
  "rods from below": "छड़ें नीचे से",
  "steam gen.": "भाप जनित्र",
  "steam generator": "भाप जनित्र",
  "the Chernobyl type; a few still run in Russia": "चेर्नोबिल वाला प्रकार; रूस में कुछ अब भी चलते हैं",
  "thermal neutrons · moderator: graphite · coolant: boiling water": "तापीय न्यूट्रॉन · मंदक: ग्रेफाइट · शीतलक: उबलता पानी",
  "thermal neutrons · moderator: heavy water · coolant: heavy water": "तापीय न्यूट्रॉन · मंदक: भारी पानी · शीतलक: भारी पानी",
  "thermal neutrons · moderator: light water · coolant: boiling water": "तापीय न्यूट्रॉन · मंदक: हल्का पानी · शीतलक: उबलता पानी",
  "thermal neutrons · moderator: light water · coolant: supercritical water": "तापीय न्यूट्रॉन · मंदक: हल्का पानी · शीतलक: अतिक्रांतिक पानी",
  "thermal neutrons · moderator: light water · coolant: water": "तापीय न्यूट्रॉन · मंदक: हल्का पानी · शीतलक: पानी",
  "thermal · mod.: graphite · cool.: boiling water": "तापीय · मंदक: ग्रेफाइट · शीतलक: उबलता पानी",
  "thermal · mod.: heavy water · cool.: heavy water": "तापीय · मंदक: भारी पानी · शीतलक: भारी पानी",
  "thermal · mod.: light water · cool.: boiling water": "तापीय · मंदक: हल्का पानी · शीतलक: उबलता पानी",
  "thermal · mod.: light water · cool.: supercritical water": "तापीय · मंदक: हल्का पानी · शीतलक: अतिक्रांतिक पानी",
  "thermal · mod.: light water · cool.: water": "तापीय · मंदक: हल्का पानी · शीतलक: पानी",
  "turbine": "टरबाइन",
  "vessel": "पात्र",
  "water boils in the core": "पानी कोर में उबलता है",
  "water boils in ~{#} pressure tubes": "पानी ~{#} दाब नलियों में उबलता है",
  "{#} bar": "{#} bar",
  "{#} bar: hotter than boiling, still one fluid": "{#} bar: क्वथनांक से अधिक गर्म, फिर भी एक ही तरल",
  "{#} bar: never boils": "{#} bar: कभी नहीं उबलता",
  "{#} °C": "{#} °C",
});
