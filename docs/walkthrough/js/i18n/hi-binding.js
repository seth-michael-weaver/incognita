/* Hindi: binding (अध्याय 3, नाभिक एक साथ क्यों टिके रहते हैं) */
WT.L.ch.binding = {
  num: "अध्याय 3", title: "नाभिक एक साथ क्यों टिके रहते हैं", short: "बंधन",
  html: `
<div class="step">
  <p>वक्र पर जितना ऊपर, उतना अधिक कसकर बंधा। हर बिंदु एक द्रव्यमान संख्या A (प्रोटॉनों और न्यूट्रॉनों की कुल गिनती) है, और उसकी ऊंचाई वह ऊर्जा है जो उस नाभिक को पूरी तरह तोड़कर अलग करने में प्रति न्यूक्लिऑन लगेगी। A को खींचिए और चिह्न पढ़िए: वक्र का मध्य भाग, लोहे और निकल के आसपास, सबसे ऊपर है।</p>
  <div class="ctl"><label for="bi-a">द्रव्यमान संख्या A</label><input id="bi-a" type="range" data-bind="pick" data-instant min="2" max="260" step="1" value="56"><output data-show="pick" data-fmt="0"></output></div>
</div>
<div class="step">
  <p>यूरेनियम को विखंडित कीजिए: दोनों टुकड़े वक्र पर उस यूरेनियम से ऊपर बैठते हैं जिससे वे बने थे, इसलिए वही न्यूक्लिऑन अब अधिक कसकर बंधे हैं और अंतर ऊर्जा के रूप में बाहर आता है। हल्का टुकड़ा चुनिए; भारी टुकड़ा 236 न्यूक्लिऑनों का शेष भाग है।</p>
  <div class="ctl"><label for="bi-f">हल्का टुकड़ा A</label><input id="bi-f" type="range" data-bind="frag" data-instant min="70" max="118" step="1" value="95"><output data-show="frag" data-fmt="0"></output></div>
  <p class="ctl-result" id="bi-split-out" aria-live="polite"></p>
  <p>विखंडन चाहे जैसा हो, यह लगभग 200 MeV है: ईंधन के एक अणु को जलाने पर मिलने वाले कुछ इलेक्ट्रॉन-वोल्ट से करोड़ों गुना अधिक।</p>
  <p>हल्के नाभिक उलटे रास्ते से, जुड़कर, ऊर्जा छोड़ते हैं: <a href="topics.html#fusion" data-keep-lang>→ संलयन</a>।</p>
</div>`,
};

// canvas labels added 2026-10-29 (I18NLABELS_B)
Object.assign(WT.L.labels, {
  "mass number A →": "द्रव्यमान संख्या A →",
  "binding energy per nucleon (MeV)": "प्रति न्यूक्लिऑन बंधन ऊर्जा (MeV)",
  "Ni{#}: most tightly bound": "Ni{#}: सबसे कसकर बंधा",
  "measured masses (AME{#})": "मापे गए द्रव्यमान (AME{#})",
  "Fe{#}: {#} MeV per nucleon · {#} MeV in all": "Fe{#}: प्रति न्यूक्लिऑन {#} MeV · कुल {#} MeV",
});
