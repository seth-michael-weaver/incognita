/* Hindi: stars (तत्व कहाँ से आते हैं) */
WT.L.ch.stars = {
  num: "पाठ 1", title: "तत्व कहाँ से आते हैं", short: "तारे",
  html: `
<div class="step">
  <h3>संलयन लोहे पर रुकता है</h3>
  <p>तारे हल्के नाभिकों को लोहे तक जोड़ते हैं; उससे भारी लगभग सब कुछ न्यूट्रॉन जोड़कर बनता है।</p>
</div>
<div class="step">
  <h3>धीमा रास्ता</h3>
  <p>विशाल तारों में न्यूट्रॉन कभी-कभार आते हैं, इसलिए अस्थिर नाभिक पहले बीटा-क्षय करता है: रास्ता स्थिर नाभिकों के साथ टेढ़ा-मेढ़ा चलता है।</p>
  <div class="ctl"><label for="st-k">न्यूट्रॉन प्रग्रहण</label><input id="st-k" type="range" data-bind="k" min="0" max="213" step="1" value="112"></div>
</div>
<div class="step">
  <h3>तेज़ रास्ता</h3>
  <p>न्यूट्रॉन तारों के विलय में न्यूट्रॉन इतनी तेज़ी से भरते हैं कि नाभिक क्षयित नहीं हो पाते; बाद में न्यूट्रॉन-समृद्ध नाभिक क्षयित होकर स्थिरता की ओर लौटते हैं।</p>
  <div class="ctl"><label for="st-rt">वापस क्षय</label><input id="st-rt" type="range" data-bind="rt" min="0" max="1" step="0.01" value="0"></div>
</div>
<div class="step">
  <h3>जादुई संख्याएँ शिखर बनाती हैं</h3>
  <p>50, 82 या 126 न्यूट्रॉन वाले नाभिक मुश्किल से प्रग्रहण करते हैं, इसलिए पदार्थ वहाँ जमा होता है: स्ट्रॉन्शियम, बेरियम और सीसे पर s-शिखर, r-शिखर थोड़े हल्के।</p>
  <div class="btns"><button class="btn ghost" data-act="stS" aria-pressed="true">s-प्रक्रिया शिखर</button> <button class="btn ghost" data-act="stR" aria-pressed="true">r-प्रक्रिया शिखर</button></div>
</div>
<div class="step">
  <h3>जहाँ प्रग्रहण आसान, वहाँ दुर्लभ</h3>
  <p>केवल s-प्रक्रिया से बने समस्थानिकों के लिए बहुलता Nₛ गुणा प्रग्रहण अनुप्रस्थ काट σ जादुई संख्याओं के बीच लगभग स्थिर रहता है। यहाँ σ INCOGNITA का 30 keV पर परिकलित मान है।</p>
  <div class="btns"><button class="btn ghost" data-act="stvs" aria-pressed="false">σ</button> <button class="btn ghost" data-act="stvn" aria-pressed="false">Nₛ</button> <button class="btn ghost" data-act="stvsn" aria-pressed="true">σ × Nₛ</button></div>
</div>
<div class="step">
  <h3>मापनों से जाँचा गया</h3>
  <p>INCOGNITA के 30 keV मान, मापे गए मानों से विभाजित, 94 स्थिर न्यूक्लाइडों के लिए (<a href="scoreboard.html">तुलनाएँ</a>)।</p>
</div>`,
};
Object.assign(WT.L.labels, {
  "A ≈ {#}": "A ≈ {#}",
  "Ba": "Ba",
  "Ba{#}": "Ba{#}",
  "Big Bang": "बिग बैंग",
  "Fe": "Fe",
  "H": "H",
  "He": "He",
  "INCOGNITA ÷ measured, {#} keV": "INCOGNITA ÷ मापित, {#} keV",
  "INCOGNITA's {#} keV capture rate (MACS) ÷ measured": "INCOGNITA की {#} keV प्रग्रहण दर (MACS) ÷ मापित",
  "INCOGNITA: capture at {#} keV (MACS)": "INCOGNITA: {#} keV पर प्रग्रहण (MACS)",
  "Lodders et al. {#}": "Lodders et al. {#}",
  "Lu{#}": "Lu{#}",
  "N = {#}": "N = {#}",
  "O": "O",
  "Pb": "Pb",
  "Pb{#}": "Pb{#}",
  "Sm{#}": "Sm{#}",
  "Sn": "Sn",
  "Sr": "Sr",
  "Sr{#}": "Sr{#}",
  "abundances: Lodders, Palme & Gail {#}": "बहुलताएँ: Lodders, Palme & Gail {#}",
  "abundances: Lodders, Palme & Gail {#} · point at the curve": "बहुलताएँ: Lodders, Palme & Gail {#} · वक्र पर इंगित करें",
  "atoms per million silicon atoms (Solar System)": "प्रति दस लाख सिलिकॉन परमाणु परमाणु (सौर मंडल)",
  "atoms per {#}⁶ silicon": "प्रति {#}⁶ सिलिकॉन परमाणु",
  "beta decay (n → p)": "बीटा क्षय (n → p)",
  "flat between magic numbers, steps down at each": "जादुई संख्याओं के बीच समतल, हर एक पर एक सीढ़ी नीचे",
  "fusion": "संलयन",
  "fusion in stars": "तारों में संलयन",
  "made by neutron capture": "न्यूट्रॉन प्रग्रहण से बने",
  "magic N: captures poorly, matter piles up": "जादुई N: प्रग्रहण कम, पदार्थ जमा होता है",
  "magic neutron number: it captures poorly, so matter piles up here": "जादुई न्यूट्रॉन संख्या: प्रग्रहण कम, इसलिए पदार्थ यहाँ जमा होता है",
  "mass number A": "द्रव्यमान संख्या A",
  "mass number A (protons + neutrons)": "द्रव्यमान संख्या A (प्रोटॉन + न्यूट्रॉन)",
  "mb": "mb",
  "nearly flat between magic numbers, a step down at each": "जादुई संख्याओं के बीच लगभग समतल, हर एक पर एक सीढ़ी नीचे",
  "neutron capture": "न्यूट्रॉन प्रग्रहण",
  "neutrons N →": "न्यूट्रॉन N →",
  "peaks: sources Lodders et al. {#}": "शिखर: स्रोत Lodders et al. {#}",
  "plus a weaker s-process (massive stars)": "साथ में एक कमज़ोर s-प्रक्रिया (भारी तारे)",
  "r {#}": "r {#}",
  "r-path: illustration": "r-पथ: चित्रण",
  "r-peak Pt": "r-शिखर Pt",
  "r-peak Se, Kr": "r-शिखर Se, Kr",
  "r-peak Te, Xe": "r-शिखर Te, Xe",
  "r-process: a flood of neutrons makes very neutron-rich nuclei": "r-प्रक्रिया: न्यूट्रॉनों की बाढ़ बहुत न्यूट्रॉन-समृद्ध नाभिक बनाती है",
  "r-process: very neutron-rich nuclei": "r-प्रक्रिया: बहुत न्यूट्रॉन-समृद्ध नाभिक",
  "ringed: s-only isotopes · measured: compiled values (KADoNiS) · a development comparison, not an independent test": "घेरे में: केवल-s समस्थानिक · मापित: संकलित मान (KADoNiS) · विकास के दौरान तुलना, स्वतंत्र परीक्षण नहीं",
  "ringed: s-only · measured: KADoNiS": "घेरे में: केवल-s · मापित: KADoNiS",
  "s Ba": "s Ba",
  "s Pb": "s Pb",
  "s Sr": "s Sr",
  "s-only isotopes · bars: INCOGNITA {#} %": "केवल-s समस्थानिक · पट्टियाँ: INCOGNITA {#} %",
  "s-only isotopes · σ: INCOGNITA (bars: its {#} % range; open circle: scaled to a measurement) · Nₛ: Lodders et al. {#}": "केवल-s समस्थानिक · σ: INCOGNITA (पट्टियाँ: इसकी {#} % सीमा; खुला वृत्त: मापन के अनुसार स्केल) · Nₛ: Lodders et al. {#}",
  "s-peak Ba": "s-शिखर Ba",
  "s-peak Pb": "s-शिखर Pb",
  "s-peak Sr": "s-शिखर Sr",
  "seen in {#}: merger GW{#}": "{#} में देखा गया: विलय GW{#}",
  "seen in {#}: the neutron-star merger GW{#} and its kilonova": "{#} में देखा गया: न्यूट्रॉन तारा विलय GW{#} और उसका किलोनोवा",
  "wait": "प्रतीक्षा",
  "waiting point": "प्रतीक्षा बिंदु",
  "weak s-process too": "कमज़ोर s-प्रक्रिया भी",
  "σ × Nₛ (mb × atoms per million Si)": "σ × Nₛ (mb × प्रति दस लाख Si परमाणु)",
  "σ × Nₛ (mb × atoms per {#}⁶ Si)": "σ × Nₛ (mb × प्रति {#}⁶ Si परमाणु)",
  "↑ protons Z": "↑ प्रोटॉन Z",
  "A = {a}: mostly {b}, {c} atoms per million silicon": "A = {a}: मुख्यतः {b}, प्रति दस लाख सिलिकॉन {c} परमाणु",
  "decayed back: r-made stable isotopes": "वापस क्षयित: r-निर्मित स्थिर समस्थानिक",
  "decayed back: each lands on the most neutron-rich stable isobar": "वापस क्षयित: हर एक सबसे न्यूट्रॉन-समृद्ध स्थिर समभारिक पर पहुँचता है",
  "beta decays, A fixed": "बीटा क्षय, A स्थिर",
  "beta decays carry them back, mass number A fixed": "बीटा क्षय उन्हें वापस लाते हैं, द्रव्यमान संख्या A स्थिर",
  "{a} · N = {b} · σ = {c} mb": "{a} · N = {b} · σ = {c} mb",
  "{a} · N = {b} · INCOGNITA: σ = {c} mb at {#} keV": "{a} · N = {b} · INCOGNITA: σ = {c} mb, {#} keV पर",
  "{a} · unstable: beta decay": "{a} · अस्थिर: बीटा क्षय",
  "{a} · unstable: it beta-decays before the next neutron": "{a} · अस्थिर: अगले न्यूट्रॉन से पहले बीटा-क्षय करता है",
  "end: the lead–bismuth cycle": "अंत: सीसा–बिस्मथ चक्र",
  "end of the road: Bi{#} → Po{#} → alpha decay back to Pb{#}": "रास्ते का अंत: Bi{#} → Po{#} → अल्फा क्षय से वापस Pb{#}",
  "drag along the path": "पथ के साथ खींचें",
  "drag along the path, or use the slider": "पथ के साथ खींचें, या स्लाइडर का उपयोग करें",
  "{a}: INCOGNITA σ = {b} mb": "{a}: INCOGNITA σ = {b} mb",
  "{a}: σ = {b} mb × Nₛ = {c} → σNₛ = {d}": "{a}: σ = {b} mb × Nₛ = {c} → σNₛ = {d}",
  " (σ scaled to a measured value)": " (σ एक मापित मान के अनुसार स्केल)",
  "σ alone: scattered": "केवल σ: बिखरा",
  "σ alone jumps around from isotope to isotope": "केवल σ समस्थानिक-दर-समस्थानिक उछलता है",
  "Nₛ alone: scattered": "केवल Nₛ: बिखरा",
  "Nₛ alone jumps around the other way": "केवल Nₛ उल्टी दिशा में उछलता है",
  "{a}: INCOGNITA's engine {b} (the library then scales to it)": "{a}: INCOGNITA इंजन {b} (फिर लाइब्रेरी मापन के अनुसार स्केल होती है)",
  "{a}: INCOGNITA σ = {b} mb, {c}": "{a}: INCOGNITA σ = {b} mb, {c}",
  "{a} nuclides · typical difference {b} %": "{a} न्यूक्लाइड · सामान्य अंतर {b} %",
  "{a} stable nuclides · typical difference {b} % (median), rms {c} %": "{a} स्थिर न्यूक्लाइड · सामान्य अंतर {b} % (माध्यिका), rms {c} %",
  "{a} % above measured": "मापित से {a} % ऊपर",
  "{a} % below measured": "मापित से {a} % नीचे",
});
