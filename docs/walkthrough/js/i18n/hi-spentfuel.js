/* Hindi: spentfuel (प्रयुक्त ईंधन, नाभिक-दर-नाभिक) */
WT.L.ch.spentfuel = {
  num: "पाठ 1", title: "प्रयुक्त ईंधन, नाभिक-दर-नाभिक", short: "नाभिक-दर-नाभिक",
  html: `
<div class="step">
  <h3>अंदर क्या है</h3>
  <p>निकालने के एक वर्ष बाद PWR ईंधन का एक टन (4.2 % संवर्धित, 50 GWd/t): लगभग सारा द्रव्यमान यूरेनियम है, लगभग सारी सक्रियता कुछ किलोग्राम में है।</p>
</div>
<div class="step">
  <h3>सक्रियता या रेडियोविषाक्तता</h3>
  <p>बेकरेल क्षयों को गिनता है; सीवर्ट हर क्षय को निगलने पर उसके नुकसान से तौलता है, जिससे अल्फा उत्सर्जक ऊपर आ जाते हैं।</p>
  <div class="btns"><button class="btn ghost" data-act="mA" aria-pressed="false">सक्रियता (Bq)</button> <button class="btn ghost" data-act="mT" aria-pressed="true">रेडियोविषाक्तता (Sv)</button></div>
</div>
<div class="step">
  <h3>कब कौन हावी</h3>
  <p>किसी पट्टी का नाम देखने के लिए उस पर माउस रखें या टैप करें; उन्हें क्रम देने के लिए समय-अक्ष के साथ खींचें।</p>
</div>
<div class="step">
  <h3>प्लूटोनियम का पुनर्चक्रण</h3>
  <p>चार वर्ष पर पुनर्संसाधन प्लूटोनियम (और उसके साथ यूरेनियम) निकाल लेता है। कितना पीछे छूटता है?</p>
  <div class="btns"><span class="sf-k" style="font:600 13px var(--sans);color:var(--soft);margin-right:4px;align-self:center">Pu removed</span> <button class="btn ghost" data-act="pu0" aria-pressed="true">0 %</button> <button class="btn ghost" data-act="pu99" aria-pressed="false">99 %</button> <button class="btn ghost" data-act="pu999" aria-pressed="false">99.9 %</button></div>
</div>
<div class="step">
  <h3>लघु ऐक्टिनाइड भी हटाइए</h3>
  <p>अमेरिशियम, क्यूरियम और नेप्च्यूनियम भी निकालिए: तब पीछे छूटा 1 % या 0.1 % समय तय करता है।</p>
  <div class="btns"><span class="sf-k" style="font:600 13px var(--sans);color:var(--soft);margin-right:4px;align-self:center">Pu removed</span> <button class="btn ghost" data-act="pu0" aria-pressed="true">0 %</button> <button class="btn ghost" data-act="pu99" aria-pressed="false">99 %</button> <button class="btn ghost" data-act="pu999" aria-pressed="false">99.9 %</button></div>
  <div class="btns"><span class="sf-k" style="font:600 13px var(--sans);color:var(--soft);margin-right:4px;align-self:center">Am, Cm, Np removed</span> <button class="btn ghost" data-act="ma0" aria-pressed="true">0 %</button> <button class="btn ghost" data-act="ma99" aria-pressed="false">99 %</button> <button class="btn ghost" data-act="ma999" aria-pressed="false">99.9 %</button></div>
</div>`,
};
Object.assign(WT.L.labels, {
  "Am{#}": "Am{#}",
  "Am{#} {#} %": "Am{#} {#} %",
  "Cm{#}": "Cm{#}",
  "Cs{#}": "Cs{#}",
  "I{#}": "I{#}",
  "NEA {#} + computed": "NEA {#} + परिकलित",
  "Np{#}": "Np{#}",
  "Pu{#}": "Pu{#}",
  "Pu{#} {#} %": "Pu{#} {#} %",
  "Sr{#}": "Sr{#}",
  "Sr{#} + Y{#}": "Sr{#} + Y{#}",
  "Tc{#}": "Tc{#}",
  "activity": "सक्रियता",
  "activity after {#} year (log scale)": "{#} वर्ष बाद सक्रियता (लघुगणकीय पैमाना)",
  "below the ore after ≈ {#} years": "≈ {#} वर्ष बाद अयस्क से नीचे",
  "computed (Bateman decay, ICRP{#}) · band height = share of the total": "परिकलित (बेटमैन क्षय, ICRP{#}) · पट्टी की ऊँचाई = कुल में हिस्सा",
  "computed · band height = share": "परिकलित · पट्टी ऊँचाई = हिस्सा",
  "drag along the time axis · hover a band": "समय-अक्ष के साथ खींचें · पट्टी पर माउस रखें",
  "inventory: OECD-NEA {#} ({#} %, {#} GWd/t) + computed fission products": "भंडार: OECD-NEA {#} ({#} %, {#} GWd/t) + परिकलित विखंडन उत्पाद",
  "mass": "द्रव्यमान",
  "mass (log scale)": "द्रव्यमान (लघुगणकीय पैमाना)",
  "most of the {#} kg of fission products is stable; activity includes short-lived daughters": "{#} kg विखंडन उत्पादों का अधिकांश स्थिर है; सक्रियता में अल्पायु संतति शामिल",
  "once-through": "वन्स-थ्रू",
  "once-through (no recycling)": "वन्स-थ्रू (पुनर्चक्रण नहीं)",
  "ore: {#}×{#}⁵ Sv": "अयस्क: {#}×{#}⁵ Sv",
  "other FP": "अन्य FP",
  "other FP: mostly stable": "अन्य FP: अधिकतर स्थिर",
  "other fission products": "अन्य विखंडन उत्पाद",
  "radiotoxicity if swallowed (Sv), relative to the ore": "निगलने पर रेडियोविषाक्तता (Sv), अयस्क के सापेक्ष",
  "radiotoxicity ÷ ore": "रेडियोविषाक्तता ÷ अयस्क",
  "reprocessing at {#} yr": "{#} वर्ष पर पुनर्संसाधन",
  "the ore it came from: {#} t natural uranium + daughters = {#}×{#}⁵ Sv": "जिस अयस्क से आया: {#} t प्राकृतिक यूरेनियम + संतति = {#}×{#}⁵ Sv",
  "then mostly Am{#} ({#} %)": "तब मुख्यतः Am{#} ({#} %)",
  "then mostly Pb{#} + Po{#} ({#} %)": "तब मुख्यतः Pb{#} + Po{#} ({#} %)",
  "then mostly Sr{#} + Y{#} ({#} %)": "तब मुख्यतः Sr{#} + Y{#} ({#} %)",
  "uranium": "यूरेनियम",
  "years after unloading (log scale) →": "निकालने के बाद वर्ष (लघुगणकीय पैमाना) →",
  "{#} g": "{#} g",
  "{#} kg": "{#} kg",
  "{#} million": "{#} मिलियन",
  "{#} years:": "{#} वर्ष:",
  "{#} yr": "{#} वर्ष",
  "{#}¹³ Bq": "{#}¹³ Bq",
  "{#}¹⁰ Bq": "{#}¹⁰ Bq",
  "{#}¹⁶ Bq": "{#}¹⁶ Bq",
  "other Am, Cm": "अन्य Am, Cm",
  "decay daughters (Ra, Pb, Po, Th…)": "क्षय संतति (Ra, Pb, Po, Th…)",
  "daughters": "संतति",
  "still above the ore after a million years": "दस लाख वर्ष बाद भी अयस्क से ऊपर",
  "drag the time · tap a band": "समय खींचें · पट्टी टैप करें",
  "activity ÷ ore": "सक्रियता ÷ अयस्क",
  "activity (Bq), relative to the ore": "सक्रियता (Bq), अयस्क के सापेक्ष",
});
