/* Hindi: reactor (रिएक्टर बिजली कैसे बनाता है) */
WT.L.ch.reactor = {
  num: "पाठ 1", title: "रिएक्टर बिजली कैसे बनाता है", short: "रिएक्टर",
  html: `
<div class="step">
  <h3>ईंधन</h3>
  <p>यूरेनियम को उंगली के पोर जितनी सिरेमिक गोलियों में पकाया जाता है, गोलियां लंबी धातु की छड़ों में भरी जाती हैं, और छड़ों को जोड़कर असेंबली बनाई जाती हैं। एक गोली लगभग उतनी ऊष्मा देती है जितनी एक टन कोयला जलाने से मिलती है।</p>
  <div class="ctl"><label for="rea-z">दूर से देखें</label><input id="rea-z" type="range" data-bind="z" min="0" max="3" step="0.01" value="0"><output data-show="z" data-fmt="1"></output></div>
</div>
<div class="step">
  <h3>परमाणुओं का विखंडन ऊष्मा देता है</h3>
  <p>कोर में टूटते यूरेनियम परमाणु छड़ों के पास से ऊपर बहते पानी को गर्म करते हैं। वही पानी न्यूट्रॉनों को धीमा करता है ताकि वे और परमाणुओं का विखंडन कर सकें। ऊंचा दाब उसे 325 °C पर भी उबलने नहीं देता।</p>
</div>
<div class="step">
  <h3>भाप टरबाइन घुमाती है</h3>
  <p>गर्म पानी अपनी ऊष्मा पतली नलियों के जरिए दूसरे परिपथ को देता है, जहां पानी उबलता है। भाप टरबाइन और जनित्र को घुमाती है, फिर नदी या समुद्र का ठंडा पानी उसे वापस पानी बना देता है। लगभग एक तिहाई ऊष्मा बिजली बनती है।</p>
</div>
<div class="step">
  <h3>नियंत्रण छड़ें</h3>
  <p>नियंत्रण छड़ें न्यूट्रॉनों को सोख लेती हैं। उन्हें भीतर धकेलिए तो कम परमाणु टूटते हैं: कम ऊष्मा, कम भाप, कम बिजली। बाहर खींचिए तो शक्ति बढ़ती है।</p>
  <div class="ctl"><label for="rea-rod">नियंत्रण छड़ें भीतर (%)</label><input id="rea-rod" type="range" data-bind="ins" data-instant min="0" max="100" step="1" value="15"><output data-show="ins" data-fmt="0"></output></div>
</div>`,
};
Object.assign(WT.L.labels, {
  "reactor": "रिएक्टर",
  "reactor vessel": "रिएक्टर पात्र",
  "control rods": "नियंत्रण छड़ें",
  "core": "कोर",
  "steam gen.": "भाप जनित्र",
  "steam generator": "भाप जनित्र",
  "turbine": "टरबाइन",
  "gen.": "जनित्र",
  "generator": "जनित्र",
  "condenser": "संघनित्र",
  "sea or river water": "समुद्र या नदी का पानी",
  "{#} °C out": "{#} °C बाहर",
  "{#} °C in": "{#} °C भीतर",
  "steam ~{#} °C": "भाप ~{#} °C",
  "{#} bar: hot, but no boiling": "{#} bar: गर्म, पर उबाल नहीं",
  "{#} bar keeps the water liquid at {#} °C": "{#} bar पानी को {#} °C पर भी द्रव रखता है",
  "the water also slows the neutrons": "पानी न्यूट्रॉनों को धीमा भी करता है",
  "the water carries the heat and slows the neutrons": "पानी ऊष्मा ले जाता है और न्यूट्रॉनों को धीमा करता है",
  "heat {#} MW": "ऊष्मा {#} MW",
  "electric {#} MW": "विद्युत {#} MW",
  "electricity {#} MW": "बिजली {#} MW",
  "chain stopped; fuel still warm (afterheat)": "श्रृंखला रुकी; ईंधन अभी भी गर्म (अवशिष्ट ऊष्मा)",
  "chain reaction stopped; the fuel still gives off afterheat": "श्रृंखला अभिक्रिया रुकी; ईंधन अभी भी अवशिष्ट ऊष्मा देता है",
  "turbine speed fixed by the grid; more steam, more push": "टरबाइन की गति ग्रिड तय करता है; अधिक भाप, अधिक धक्का",
  "the turbine's speed is fixed by the grid; more steam pushes harder": "टरबाइन की गति ग्रिड से बंधी है; अधिक भाप जोर से धकेलती है",
  "{#}/{#} of the heat goes to the water": "{#}/{#} ऊष्मा पानी में जाती है",
  "about two thirds of the heat leaves through the condenser": "लगभग दो तिहाई ऊष्मा संघनित्र से बाहर जाती है",
  "illustration": "चित्रण",
  "drag sideways to zoom": "ज़ूम के लिए बगल में खींचें",
  "drag sideways to zoom out": "दूर से देखने के लिए बगल में खींचें",
  "UO₂ pellet, {#} cm": "UO₂ गोली, {#} cm",
  "uranium oxide pellet, about {#} cm": "यूरेनियम ऑक्साइड गोली, लगभग {#} cm",
  "{#} tonne of coal": "{#} टन कोयला",
  "about {#} tonne of coal (or {#} m³ of gas)": "लगभग {#} टन कोयला (या {#} m³ गैस)",
  "same heat, roughly": "लगभग उतनी ही ऊष्मा",
  "fuel rod, ~{#} m": "ईंधन छड़, ~{#} m",
  "fuel rod, about {#} m long": "ईंधन छड़, लगभग {#} m लंबी",
  "~{#} pellets inside": "भीतर ~{#} गोलियां",
  "about {#} pellets in a metal tube": "धातु की नली में लगभग {#} गोलियां",
  "(not to scale)": "(पैमाने पर नहीं)",
  "assembly: {#} rods": "असेंबली: {#} छड़ें",
  "fuel assembly from above: {#} rods": "ऊपर से ईंधन असेंबली: {#} छड़ें",
  "rings: control-rod guide tubes": "छल्ले: नियंत्रण-छड़ की गाइड नलियां",
  "rings: tubes the control rods slide into": "छल्ले: वे नलियां जिनमें नियंत्रण छड़ें सरकती हैं",
  "core: {#} assemblies": "कोर: {#} असेंबली",
  "the core from above: {#} assemblies": "ऊपर से कोर: {#} असेंबली",
  "~{#} rods, ~{#} m across": "~{#} छड़ें, ~{#} m व्यास",
  "about {#} rods in a cylinder about {#} m across": "लगभग {#} छड़ें, लगभग {#} m व्यास के बेलन में",
  "pellet": "गोली",
  "rod": "छड़",
  "assembly": "असेंबली",
});
