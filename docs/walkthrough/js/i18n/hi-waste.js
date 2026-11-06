/* Hindi: waste (समय के साथ प्रयुक्त ईंधन) */
WT.L.ch.waste = {
  num: "पाठ 1", title: "समय के साथ प्रयुक्त ईंधन", short: "प्रयुक्त ईंधन",
  html: `
<div class="step">
  <h3>बाहर क्या निकलता है</h3>
  <p>कोर में चार-पांच वर्ष बिताने के बाद भी ईंधन की गोली ज्यादातर यूरेनियम ही होती है। कुछ प्रतिशत <b>विखंडन उत्पाद</b> हैं, यानी टूटे हुए परमाणु। लगभग 1 % प्लूटोनियम है, और थोड़ी-सी मात्रा भारी <b>लघु ऐक्टिनाइड</b> की है, जैसे अमेरिसियम।</p>
  <div class="btns"><button class="btn" data-act="sort">परमाणु छांटें</button></div>
</div>
<div class="step">
  <h3>पहली शताब्दियां</h3>
  <p>वक्र निगल लिए जाने पर प्रयुक्त ईंधन के खतरे की तुलना उस यूरेनियम अयस्क से करता है जिससे वह बना था। शुरू में विखंडन उत्पाद हावी रहते हैं, पर उनमें से अधिकांश की अर्ध-आयु लगभग 30 वर्ष है: करीब 300 वर्ष बाद वे अयस्क से नीचे आ जाते हैं।</p>
  <div class="ctl"><label for="wst-t1">निकालने के बाद वर्ष</label><input id="wst-t1" type="range" data-bind="lt" data-instant min="0" max="6" step="0.01" value="1.5"><output data-show="yr" data-fmt="0"></output></div>
</div>
<div class="step">
  <h3>फिर प्लूटोनियम</h3>
  <p>जो बचता है वह प्लूटोनियम और अमेरिसियम है, जिनकी अर्ध-आयु सैकड़ों से लेकर हजारों-दसियों हजार वर्ष तक है। वे प्रयुक्त ईंधन को एक लाख वर्ष से भी अधिक समय तक अयस्क के स्तर से ऊपर रखते हैं।</p>
  <div class="ctl"><label for="wst-t2">निकालने के बाद वर्ष</label><input id="wst-t2" type="range" data-bind="lt" data-instant min="0" max="6" step="0.01" value="4"><output data-show="yr" data-fmt="0"></output></div>
</div>
<div class="step">
  <h3>पुनर्चक्रण और रूपांतरण</h3>
  <p>प्लूटोनियम को निकालकर नए ईंधन के रूप में जला दें, तो यह समय घटकर लगभग दस हजार वर्ष रह जाता है। लघु ऐक्टिनाइडों को भी तेज रिएक्टरों में विखंडित कर दें, तो केवल विखंडन उत्पाद बचते हैं: कुछ सौ वर्ष।</p>
  <div class="btns"><button class="btn ghost" data-act="rp" aria-pressed="false">प्लूटोनियम पुनर्चक्रित करें</button><button class="btn ghost" data-act="tm" aria-pressed="false">लघु ऐक्टिनाइड रूपांतरित करें</button></div>
</div>`,
};
Object.assign(WT.L.labels, {
  "Sort the atoms": "परमाणु छांटें",
  "Mix them again": "फिर से मिलाएं",
  "uranium": "यूरेनियम",
  "fission products": "विखंडन उत्पाद",
  "fission prod.": "विखंडन उत्पाद",
  "plutonium": "प्लूटोनियम",
  "minor actinides": "लघु ऐक्टिनाइड",
  "minor act.": "लघु ऐक्टि.",
  "a used fuel pellet, {#} atoms": "प्रयुक्त ईंधन गोली, {#} परमाणु",
  "a used fuel pellet, {#} atoms shown": "प्रयुक्त ईंधन की गोली, {#} परमाणु दिखाए गए",
  "the glow: fission products are the most radioactive": "चमक: विखंडन उत्पाद सबसे अधिक रेडियोधर्मी हैं",
  "the glow: the fission products are by far the most radioactive part": "चमक: विखंडन उत्पाद कहीं अधिक रेडियोधर्मी हिस्सा हैं",
  "spent fuel": "प्रयुक्त ईंधन",
  "spent fuel, one tonne": "प्रयुक्त ईंधन, एक टन",
  "the ore": "अयस्क",
  "the ore it was made from": "जिस अयस्क से बना",
  "{#} yr": "{#} वर्ष",
  "{#} million": "{#} मिलियन",
  "uranium ore level": "यूरेनियम अयस्क स्तर",
  "the uranium ore it was made from": "जिस यूरेनियम अयस्क से बना",
  "years after unloading (log scale) →": "निकालने के बाद वर्ष (लघुगणकीय पैमाना) →",
  "hazard vs ore (log)": "खतरा बनाम अयस्क (लघुगणकीय)",
  "hazard if swallowed, relative to the ore (log scale)": "निगलने पर खतरा, अयस्क के सापेक्ष (लघुगणकीय पैमाना)",
  "Am, Cm, Np": "Am, Cm, Np",
  "americium, curium…": "अमेरिसियम, क्यूरियम…",
  "{#} years: {#} × the ore": "{#} वर्ष: अयस्क का {#} ×",
  "below the ore it came from": "अपने मूल अयस्क से नीचे",
  "mostly from fission products": "मुख्यतः विखंडन उत्पादों से",
  "mostly from plutonium": "मुख्यतः प्लूटोनियम से",
  "mostly from americium": "मुख्यतः अमेरिसियम से",
  "recycle + transmute": "पुनर्चक्रण + रूपांतरण",
  "recycle Pu and transmute minor actinides": "Pu का पुनर्चक्रण और लघु ऐक्टिनाइडों का रूपांतरण",
  "plutonium recycled": "प्लूटोनियम पुनर्चक्रित",
  "plutonium recycled, minor actinides in the waste": "प्लूटोनियम पुनर्चक्रित, लघु ऐक्टिनाइड अपशिष्ट में",
  "only minor actinides removed": "केवल लघु ऐक्टिनाइड हटाए",
  "minor actinides removed, plutonium left in": "लघु ऐक्टिनाइड हटाए, प्लूटोनियम शेष",
  "spent fuel as it is": "प्रयुक्त ईंधन जैसा है",
  "spent fuel kept as it is": "प्रयुक्त ईंधन जैसा का तैसा रखा",
  "reaches the ore level after ~{#} years": "~{#} वर्ष बाद अयस्क स्तर तक पहुंचता है",
  "reaches the ore level after ~{#},{#} years": "~{#},{#} वर्ष बाद अयस्क स्तर तक पहुंचता है",
  "illustrative shape (after OECD-NEA)": "उदाहरणात्मक आकृति (OECD-NEA के आधार पर)",
});
