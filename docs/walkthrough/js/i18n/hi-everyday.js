/* Hindi: everyday (रोज़मर्रा के जीवन में नाभिकीय तकनीक) */
WT.L.ch.everyday = {
  num: "पाठ 4", title: "रोज़मर्रा के जीवन में नाभिकीय तकनीक", short: "रोज़मर्रा",
  html: `
<div class="step">
  <h3>PET स्कैन</h3>
  <p>फ्लोरीन-18 ट्रेसर (अर्ध-आयु 110 मिनट) पॉज़िट्रॉन उत्सर्जित करता है, और हर पॉज़िट्रॉन 511 keV की दो गामा किरणों में बदल जाता है जो विपरीत दिशाओं में उड़ती हैं। गर्म बिंदु को खींचिए: वलय हर जोड़ी के लिए एक रेखा खींचता है, और रेखाएँ वहाँ काटती हैं जहाँ ट्रेसर है।</p>
</div>
<div class="step">
  <h3>विकिरण चिकित्सा</h3>
  <p>कई दिशाओं से आती किरण-पुंज ट्यूमर पर एक-दूसरे पर पड़ती हैं, इसलिए ट्यूमर को पूरी खुराक मिलती है जबकि स्वस्थ ऊतक से गुज़रने वाले हर पथ को उसका केवल एक हिस्सा। पुंजों को घुमाने और मेरुरज्जु से दूर रखने के लिए खींचिए।</p>
  <div class="ctl"><label for="ev-n">किरण-पुंज</label><input id="ev-n" type="range" data-bind="nb" data-instant min="1" max="7" step="1" value="5"><output data-show="nb" data-fmt="0"></output></div>
  <div class="ctl"><label for="ev-r">घुमाव</label><input id="ev-r" type="range" data-bind="rotd" data-instant min="0" max="360" step="1" value="20"><output class="ev-rot"></output></div>
</div>
<div class="step">
  <h3>टेक्नीशियम-99m</h3>
  <p>अधिकांश नाभिकीय चिकित्सा स्कैनों के पीछे का यह समस्थानिक 140 keV की गामा किरण देता है जिसे शरीर के बाहर का कैमरा देख सकता है, और 6 घंटे की अर्ध-आयु के कारण एक दिन बाद बहुत कम बचता है। अस्पताल इसे <a href="#chains-3">मॉलिब्डेनम-99 से "दुहते" हैं</a>।</p>
  <div class="ctl"><label for="ev-t">खुराक के बाद घंटे</label><input id="ev-t" type="range" data-bind="th" data-instant min="0" max="48" step="0.5" value="0"><output data-show="th" data-fmt="1"></output></div>
</div>
<div class="step">
  <h3>कार्बन डेटिंग</h3>
  <p>जीवित प्राणी कार्बन-14 लेते रहते हैं; मृत्यु के बाद यह 5730 वर्ष की अर्ध-आयु से क्षयित होता है। आयु सेट कीजिए, या बचे हुए को मापकर आयु पढ़िए।</p>
  <div class="ctl"><label for="ev-a">आयु (वर्ष)</label><input id="ev-a" type="range" data-bind="age" data-instant min="0" max="50000" step="10" value="5300"><output class="ev-age"></output></div>
  <div class="ctl"><label for="ev-f">बचा कार्बन-14 (%)</label><input id="ev-f" type="range" data-bind="fr" data-instant min="0.3" max="100" step="0.1" value="52.7"><output class="ev-fr"></output></div>
</div>
<div class="step">
  <h3>धुआँ संसूचक</h3>
  <p>अमेरिशियम-241 का एक सीलबंद कण एक छोटे वायु-अंतराल में अल्फा कण भेजता है, जिससे आयन बनते हैं जो एक बहुत छोटी धारा ले जाते हैं। धुआँ आयनों को पकड़ लेता है, धारा गिरती है, और अलार्म बजता है।</p>
  <div class="ctl"><label for="ev-s">धुआँ</label><input id="ev-s" type="range" data-bind="sm" data-instant min="0" max="1" step="0.01" value="0"><output class="ev-sm"></output></div>
</div>`,
};
Object.assign(WT.L.labels, {
  "Am{#}": "Am{#}",
  "Mo{#} ({#} h)": "Mo{#} ({#} घंटे)",
  "Tc{#}m ({#} h)": "Tc{#}m ({#} घंटे)",
  "a strong gamma signal, easy to image": "प्रबल गामा संकेत, चित्र लेना आसान",
  "alarm": "अलार्म",
  "alpha particles make ions in the air": "अल्फा कण हवा में आयन बनाते हैं",
  "americium{#} (sealed)": "अमेरिशियम{#} (सीलबंद)",
  "americium{#} · half-life {#} years · alphas reach about {#} cm in air": "अमेरिशियम{#} · अर्ध-आयु {#} वर्ष · अल्फा हवा में लगभग {#} cm तक",
  "beyond ~{#} years too little is left to measure": "~{#} वर्ष के बाद मापने लायक बहुत कम बचता है",
  "carbon{#}": "कार्बन{#}",
  "clean air: steady current": "स्वच्छ हवा: स्थिर धारा",
  "current": "धारा",
  "detector ring": "संसूचक वलय",
  "dose": "खुराक",
  "fluorine{#} · half-life {#} min · {#} pairs recorded": "फ्लोरीन{#} · अर्ध-आयु {#} मिनट · {#} जोड़ियाँ दर्ज",
  "gamma camera": "गामा कैमरा",
  "half-life {#} y": "अर्ध-आयु {#} वर्ष",
  "illustration": "चित्रण",
  "molybdenum{#}, half-life {#} h": "मॉलिब्डेनम{#}, अर्ध-आयु {#} घंटे",
  "nitrogen{#} (after a beta decay)": "नाइट्रोजन{#} (बीटा क्षय के बाद)",
  "pairs of {#} keV gamma rays, back to back": "{#} keV गामा किरणों की जोड़ियाँ, विपरीत दिशाओं में",
  "physical decay only": "केवल भौतिक क्षय",
  "spinal cord": "मेरुरज्जु",
  "technetium{#}m, half-life {#} h": "टेक्नीशियम{#}m, अर्ध-आयु {#} घंटे",
  "tracer": "ट्रेसर",
  "tumour": "ट्यूमर",
  "tumour {#} % · spinal cord {#} % · healthy tissue at most {#} %": "ट्यूमर {#} % · मेरुरज्जु {#} % · स्वस्थ ऊतक अधिकतम {#} %",
  "tumour {#} % · spinal cord {#} % · other tissue at most {#} %": "ट्यूमर {#} % · मेरुरज्जु {#} % · अन्य ऊतक अधिकतम {#} %",
  "years": "वर्ष",
  "{#} beams cross: the tumour gets their sum": "{#} पुंज मिलते हैं: ट्यूमर को उनका योग मिलता है",
  "{#} h": "{#} घंटे",
  "{#} h: {#} % left": "{#} घंटे: {#} % बचा",
  "{#} half-lives": "{#} अर्ध-आयु",
  "{#} keV gamma rays": "{#} keV गामा किरणें",
  "{#} of {#} left": "{#}/{#} बचे",
  "{#} years · {#} % left": "{#} वर्ष · {#} % बचा",
  "Ötzi the Iceman, ~{#} y": "हिममानव ओत्ज़ी, ~{#} वर्ष",
  "tracer (drag me)": "ट्रेसर (मुझे खींचें)",
  "each decay: two {#} keV gamma rays, back to back": "हर क्षय: विपरीत दिशाओं में दो {#} keV गामा किरणें",
  "one beam: more dose near the skin than in the tumour": "एक पुंज: ट्यूमर से अधिक खुराक त्वचा के पास",
  "a beam crosses the spinal cord: turn the beams": "एक पुंज मेरुरज्जु को पार करता है: पुंज घुमाइए",
  "fading: half is gone every {#} hours": "घटता हुआ: हर {#} घंटे में आधा चला जाता है",
  "after a day, about {#} % is left": "एक दिन बाद लगभग {#} % बचता है",
  "nitrogen{#}": "नाइट्रोजन{#}",
  "~{#} y: too little to measure": "~{#} वर्ष: मापने को बहुत कम",
  "smoke: current down, alarm!": "धुआँ: धारा गिरी, अलार्म!",
  "some ions caught: current dipping": "कुछ आयन पकड़े गए: धारा घट रही है",
});
