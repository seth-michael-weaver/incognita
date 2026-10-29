/* Hindi: binding (अध्याय 3, नाभिक एक साथ क्यों टिके रहते हैं) */
WT.L.ch.binding = {
  num: "अध्याय 3", title: "नाभिक एक साथ क्यों टिके रहते हैं", short: "बंधन",
  html: `
<div class="step">
  <p>वक्र पर जितना ऊपर, उतना अधिक कसकर बंधा। हर बिंदु एक द्रव्यमान संख्या A (प्रोटॉनों और न्यूट्रॉनों की कुल गिनती) है, और उसकी ऊंचाई वह ऊर्जा है जो उस नाभिक को प्रति न्यूक्लिऑन पूरी तरह तोड़कर अलग करने में लगेगी। A को खींचिए और चिह्न पढ़िए: वक्र का मध्य भाग, लोहे और निकल के आसपास, सबसे ऊपर है।</p>
  <div class="ctl"><label for="bi-a">द्रव्यमान संख्या A</label><input id="bi-a" type="range" data-bind="pick" data-instant min="2" max="260" step="1" value="56"><output data-show="pick" data-fmt="0"></output></div>
</div>
<div class="step">
  <p>यूरेनियम को विखंडित कीजिए: दोनों टुकड़े वक्र पर उस यूरेनियम से ऊपर बैठते हैं जिससे वे बने थे, इसलिए वही न्यूक्लिऑन अब अधिक कसकर बंधे हैं और अंतर ऊर्जा के रूप में बाहर आता है। हल्का टुकड़ा चुनिए; भारी टुकड़ा 236 न्यूक्लिऑनों का शेष भाग है।</p>
  <div class="ctl"><label for="bi-f">हल्का टुकड़ा A</label><input id="bi-f" type="range" data-bind="frag" data-instant min="70" max="118" step="1" value="95"><output data-show="frag" data-fmt="0"></output></div>
  <p class="ctl-result" id="bi-split-out" aria-live="polite"></p>
  <p>विखंडन चाहे जैसा हो, यह लगभग 200 MeV है: ईंधन के एक अणु को जलाने पर मिलने वाले कुछ इलेक्ट्रॉन-वोल्ट से करोड़ों गुना अधिक।</p>
</div>
<div class="step">
  <p>दो हल्के नाभिकों को जोड़कर एक कीजिए। यदि नया नाभिक वक्र पर ऊपर बैठता है, तो ऊर्जा निकलती है। शिखर के पार जाने पर जोड़ने में उल्टे ऊर्जा लगती है।</p>
  <div class="ctl"><label for="bi-u">प्रत्येक हल्का नाभिक A</label><input id="bi-u" type="range" data-bind="fuse" data-instant min="2" max="60" step="1" value="2"><output data-show="fuse" data-fmt="0"></output></div>
  <p class="ctl-result" id="bi-fuse-out" aria-live="polite"></p>
</div>`,
};
