/* Hindi: dose (विकिरण खुराक) */
WT.L.ch.dose = {
  num: "पाठ 1", title: "विकिरण खुराक", short: "खुराक",
  html: `
<div class="step">
  <h3>सीवर्ट क्या मापता है</h3>
  <p>खुराक की शुरुआत शरीर के प्रति किलोग्राम सोखी गई ऊर्जा से होती है। फिर <b>सीवर्ट</b> उस ऊर्जा को उससे होने वाली हानि के अनुसार भार देता है: अल्फा कणों द्वारा दी गई वही ऊर्जा गामा किरणों की तुलना में बीस गुना अधिक गिनी जाती है, क्योंकि वह कुछ घने पथों में सिमटी होती है।</p>
  <div class="btns"><button class="btn ghost" data-act="rg" aria-pressed="true">गामा किरणें</button><button class="btn ghost" data-act="ra" aria-pressed="false">अल्फा कण</button></div>
</div>
<div class="step">
  <h3>रोजमर्रा की खुराकें</h3>
  <p>इस मीनार पर हर निशान अपने नीचे वाले का दस गुना है। तुलना के लिए चमकते मनके को खींचिए: छाती का CT स्कैन कई हजार केलों की खुराक है, एक वर्ष की प्राकृतिक पृष्ठभूमि कुछ दर्जन उड़ानों के बराबर।</p>
  <div class="ctl"><label for="ds-l">खुराक</label><input id="ds-l" type="range" data-bind="ld" data-instant min="-7" max="1" step="0.02" value="-2.15"><output class="ds-out"></output></div>
</div>
<div class="step">
  <h3>अपना वर्ष जोड़िए</h3>
  <p>हर किसी को प्रकृति से हर वर्ष लगभग 2.4 मिलीसीवर्ट मिलते हैं, ज्यादातर जमीन से निकलने वाली रेडॉन गैस से। अपनी उड़ानें, स्कैन और ऊंचाई जोड़िए।</p>
  <div class="ctl"><label for="ds-f">अटलांटिक पार उड़ानें</label><input id="ds-f" type="range" data-bind="fl" data-instant min="0" max="40" step="1" value="4"><output data-show="fl" data-fmt="0"></output></div>
  <div class="ctl"><label for="ds-ct">छाती के CT स्कैन</label><input id="ds-ct" type="range" data-bind="ct" data-instant min="0" max="3" step="1" value="0"><output data-show="ct" data-fmt="0"></output></div>
  <div class="ctl"><label for="ds-h">घर की ऊंचाई (m)</label><input id="ds-h" type="range" data-bind="alt" data-instant min="0" max="3500" step="50" value="300"><output data-show="alt" data-fmt="0"></output></div>
</div>
<div class="step">
  <h3>एक साथ बड़ी खुराक</h3>
  <p>लगभग 100 मिलीसीवर्ट से नीचे, कैंसर का कोई भी अतिरिक्त जोखिम इतना छोटा है कि मापा नहीं जा सकता; सुरक्षा नियम मानते हैं कि वह खुराक के अनुपात में बढ़ता है। एक साथ लगभग एक सीवर्ट पर कोशिकाओं पर इतनी बार चोट पड़ती है कि विकिरण रोग शुरू हो जाता है।</p>
  <div class="ctl"><label for="ds-a">एक साथ खुराक</label><input id="ds-a" type="range" data-bind="la" data-instant min="-3" max="1" step="0.02" value="-1"><output class="ds-out2"></output></div>
</div>`,
};
Object.assign(WT.L.labels, {
  "cell nuclei in a patch of body": "शरीर के एक टुकड़े में कोशिका-केंद्रक",
  "cell nuclei in a patch of body tissue": "शरीर के ऊतक के एक टुकड़े में कोशिका-केंद्रक",
  "{#} milligray of alpha: a few cells hit hard": "{#} मिलीग्रे अल्फा: कुछ कोशिकाओं पर गहरी चोट",
  "{#} milligray of gamma: about one track per cell": "{#} मिलीग्रे गामा: प्रति कोशिका लगभग एक पथ",
  "same energy · counts as {#} millisieverts": "वही ऊर्जा · {#} मिलीसीवर्ट गिनी जाती है",
  "counts as {#} millisievert": "{#} मिलीसीवर्ट गिनी जाती है",
  "illustration": "चित्रण",
  "{#} µSv": "{#} µSv", "{#} mSv": "{#} mSv", "{#} Sv": "{#} Sv", "mSv": "mSv",
  "typical values": "विशिष्ट मान",
  "radon in the air  {#}": "हवा में रेडॉन  {#}", "radon  {#}": "रेडॉन  {#}",
  "rocks and soil  {#}": "चट्टानें और मिट्टी  {#}", "ground  {#}": "जमीन  {#}",
  "food and water  {#}": "भोजन और पानी  {#}", "food  {#}": "भोजन  {#}",
  "cosmic rays at {#} m  {#}": "{#} m पर कॉस्मिक किरणें  {#}", "cosmic rays  {#}": "कॉस्मिक किरणें  {#}", "cosmic  {#}": "कॉस्मिक  {#}",
  "{#} flights  {#}": "{#} उड़ानें  {#}", "flights  {#}": "उड़ानें  {#}",
  "{#} chest CT  {#}": "{#} छाती CT  {#}", "CT  {#}": "CT  {#}",
  "average {#}": "औसत {#}", "world average {#} mSv": "विश्व औसत {#} mSv",
  "worker limit {#}": "कर्मी सीमा {#}", "worker limit {#} mSv": "कर्मी सीमा {#} mSv",
  "your year: {#} mSv": "आपका वर्ष: {#} mSv",
  "more than the yearly worker limit": "कर्मियों की वार्षिक सीमा से अधिक",
  "{#} times the world average": "विश्व औसत का {#} गुना",
  "close to the world average": "विश्व औसत के करीब",
  "tracks through each cell nucleus: about {#}": "हर कोशिका-केंद्रक से गुजरते पथ: लगभग {#}",
  "tracks through each cell nucleus: about {#} (a few drawn)": "हर कोशिका-केंद्रक से गुजरते पथ: लगभग {#} (कुछ ही दिखाए)",
  "tracks through each cell nucleus: about {#} thousand (a few drawn)": "हर कोशिका-केंद्रक से गुजरते पथ: लगभग {#} हजार (कुछ ही दिखाए)",
  "tracks through each cell nucleus: about {#} million (a few drawn)": "हर कोशिका-केंद्रक से गुजरते पथ: लगभग {#} मिलियन (कुछ ही दिखाए)",
  "no effect seen": "कोई प्रभाव नहीं दिखा",
  "risk assumed": "जोखिम माना गया",
  "small added risk assumed": "छोटा अतिरिक्त जोखिम माना गया",
  "sickness": "रोग",
  "lethal": "घातक",
  "often lethal": "प्रायः घातक",
});
(function () {
  const L = {}, UNITS = ["µSv", "mSv", "Sv"];
  // ladder items: long and short names, each followed by a dose in any unit
  const ITEMS = {
    "eating a banana": "एक केला खाना", "banana": "केला",
    "dental X-ray": "दांत का X-ray", "chest X-ray": "छाती का X-ray",
    "flight across the Atlantic": "अटलांटिक पार उड़ान", "Atlantic flight": "अटलांटिक उड़ान",
    "a year of natural background": "एक वर्ष की प्राकृतिक पृष्ठभूमि", "{#} yr background": "{#} वर्ष पृष्ठभूमि",
    "chest CT scan": "छाती का CT स्कैन", "chest CT": "छाती CT",
    "yearly limit for radiation workers": "विकिरण कर्मियों की वार्षिक सीमा", "worker limit/yr": "कर्मी सीमा/वर्ष",
    "a year on the Kerala coast (high spots)": "केरल तट पर एक वर्ष (उच्च स्थल)", "Kerala, {#} yr": "केरल, {#} वर्ष",
    "a year in the highest Ramsar homes": "रामसर के सबसे अधिक विकिरण वाले घरों में एक वर्ष", "Ramsar, {#} yr": "रामसर, {#} वर्ष",
    "at once: radiation sickness begins": "एक साथ: विकिरण रोग शुरू", "{#} Sv at once": "{#} Sv एक साथ",
    "at once: about half die untreated": "एक साथ: बिना इलाज लगभग आधे मरते हैं", "{#}–{#} Sv at once": "{#}–{#} Sv एक साथ",
  };
  for (const en in ITEMS) for (const u of UNITS) L[`${en}  ·  {#} ${u}`] = `${ITEMS[en]}  ·  {#} ${u}`;
  // the line under the ladder: bananas, flights, years of background
  const BIG = { "": "", " thousand": " हजार", " million": " मिलियन" };
  const MSG = {
    "any extra risk too small to measure": "अतिरिक्त जोखिम मापने के लिए बहुत छोटा",
    "no sickness; risk assumed to rise with dose": "कोई रोग नहीं; जोखिम खुराक के साथ बढ़ता माना जाता है",
    "radiation sickness: nausea, low blood counts": "विकिरण रोग: मतली, रक्त कोशिकाओं में कमी",
    "about half die without treatment": "बिना इलाज लगभग आधे मरते हैं",
  };
  for (const u of UNITS) {
    for (const b in BIG) {
      L[`{#} ${u}: the dose of {#}${b} bananas`] = `{#} ${u}: {#}${BIG[b]} केलों की खुराक`;
      for (const f in BIG) {
        L[`{#} ${u}: {#}${b} bananas, or {#}${f} flights`] = `{#} ${u}: {#}${BIG[b]} केले, या {#}${BIG[f]} उड़ानें`;
        L[`{#} ${u}: {#}${b} bananas, {#}${f} flights or {#} years of background`] = `{#} ${u}: {#}${BIG[b]} केले, {#}${BIG[f]} उड़ानें या {#} वर्ष की पृष्ठभूमि`;
      }
    }
    for (const m in MSG) L[`{#} ${u} at once: ${m}`] = `{#} ${u} एक साथ: ${MSG[m]}`;
  }
  Object.assign(WT.L.labels, L);
})();
