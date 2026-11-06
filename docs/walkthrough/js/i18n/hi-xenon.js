/* Hindi: xenon (ज़ेनॉन विषाक्तता) */
WT.L.ch.xenon = {
  num: "पाठ 1", title: "ज़ेनॉन विषाक्तता", short: "ज़ेनॉन",
  html: `
<div class="step">
  <h3>विखंडन से बना विष</h3>
  <p>लगभग 6.6 % विखंडन आयोडीन-135 के रास्ते ज़ेनॉन-135 तक पहुंचते हैं: यह ज्ञात सबसे प्रबल न्यूट्रॉन अवशोषक है। यह लगभग दो दिन तक बढ़ता है, जब तक न्यूट्रॉन इसे जलाकर और क्षय इसे उतनी ही तेज़ी से हटा न दें जितनी तेज़ी से यह बनता है। अधिक शक्ति इसे तेज़ी से जलाती भी है, इसलिए स्तर संतृप्त हो जाता है।</p>
  <div class="ctl"><label for="xe-p1">शक्ति (%)</label><input id="xe-p1" type="range" data-bind="P" data-instant min="10" max="100" step="5" value="100"><output data-show="P" data-fmt="0"></output></div>
</div>
<div class="step">
  <h3>ज़ेनॉन गर्त</h3>
  <p>रिएक्टर बंद करते ही जलना रुक जाता है, पर पहले से बना आयोडीन ज़ेनॉन में बदलता रहता है। विष लगभग नौ घंटे बाद शिखर पर पहुंचता है, उससे अधिक जितना छड़ें वापस दे सकती हैं, इसलिए रिएक्टर फिर से चालू नहीं हो सकता; यह दो से तीन दिन में घटता है।</p>
  <div class="ctl"><label for="xe-th">बंद होने के बाद घंटे</label><input id="xe-th" type="range" data-bind="th" data-instant min="0" max="72" step="0.5" value="9"><output data-show="th" data-fmt="1"></output></div>
</div>
<div class="step">
  <h3>बंद करें, फिर चालू करें</h3>
  <p>अब यह सजीव चलता है, प्रति सेकंड तीन घंटे। बंद कीजिए, फिर चालू करने का प्रयास कीजिए: गर्त के भीतर यह अस्वीकार हो जाता है; बाद में न्यूट्रॉन ज़ेनॉन को जला देते हैं। केवल शक्ति बदलने से भी ज़ेनॉन घंटों तक ऊपर-नीचे होता है।</p>
  <div class="ctl"><label for="xe-p3">शक्ति (%)</label><input id="xe-p3" type="range" data-bind="P" data-instant min="10" max="100" step="5" value="100"><output data-show="P" data-fmt="0"></output></div>
  <div class="btns"><button class="btn" data-act="xeshut">बंद करें</button><button class="btn ghost" data-act="xerestart">फिर चालू करें</button></div>
</div>
<div class="step">
  <h3>ज़ेनॉन दोलन</h3>
  <p>बड़े कोर में दोनों हिस्से केवल ढीले ढंग से जुड़े होते हैं। एक ओर छड़ें डालिए: वहां कम फ्लक्स कम ज़ेनॉन जलाता है, इसलिए शक्ति दूसरी ओर खिसकती है, फिर लौटती है, लगभग दिन में एक बार। बड़े कोर में यह दोलन बढ़ता जाता है, जब तक संचालक उसे अवमंदित न करें।</p>
  <div class="ctl"><label for="xe-wd">कोर का आकार (m)</label><input id="xe-wd" type="range" data-bind="wd" data-instant min="1.5" max="3.5" step="0.1" value="3"><output data-show="wd" data-fmt="1"></output></div>
  <div class="btns"><button class="btn" data-act="xepush">बाईं ओर छड़ें डालें</button></div>
</div>`,
};

Object.assign(WT.L.labels, {
  "fission → iodine{#} ({#} h) → xenon{#} ({#} h) → Cs{#}": "विखंडन → आयोडीन{#} ({#} घंटे) → ज़ेनॉन{#} ({#} घंटे) → Cs{#}",
  "xenon{#} + n → Xe{#}: {#} million barns": "ज़ेनॉन{#} + n → Xe{#}: {#} मिलियन बार्न",
  "fission → iodine{#} ({#} h) → xenon{#} ({#} h) → Cs{#}  ·  Xe{#} swallows neutrons: {#} million barns": "विखंडन → आयोडीन{#} ({#} घंटे) → ज़ेनॉन{#} ({#} घंटे) → Cs{#}  ·  Xe{#} न्यूट्रॉन निगलता है: {#} मिलियन बार्न",
  "spare reactivity": "अतिरिक्त अभिक्रियाशीलता",
  "spare reactivity the rods can give": "छड़ों से मिल सकने वाली अतिरिक्त अभिक्रियाशीलता",
  "{#} h": "{#} घंटे",
  "equilibrium {#} %": "साम्यावस्था {#} %",
  "xenon worth (% of k)": "ज़ेनॉन का प्रभाव (k का %)",
  "{#} % power · {#} h after start-up · xenon {#} %": "{#} % शक्ति · चालू होने के {#} घंटे बाद · ज़ेनॉन {#} %",
  "no restart": "पुनः चालू नहीं",
  "too poisoned to restart": "पुनः चालू करने के लिए बहुत विषाक्त",
  "shutdown": "बंद",
  "drag": "खींचिए",
  "peak {#} % at {#} h": "शिखर {#} %, {#} घंटे पर",
  "{#} h after shutdown · xenon {#} % · restart possible": "बंद होने के {#} घंटे बाद · ज़ेनॉन {#} % · पुनः चालू संभव",
  "{#} h after shutdown · xenon {#} % · cannot restart": "बंद होने के {#} घंटे बाद · ज़ेनॉन {#} % · पुनः चालू नहीं हो सकता",
  "shut down": "बंद",
  "refused: more xenon than spare reactivity": "अस्वीकृत: ज़ेनॉन अतिरिक्त अभिक्रियाशीलता से अधिक",
  "restarted": "फिर चालू",
  "tap the core to shut down": "बंद करने के लिए कोर पर टैप करें",
  "tap the core to restart": "फिर चालू करने के लिए कोर पर टैप करें",
  "power": "शक्ति",
  "running at {#} % · xenon {#} %": "{#} % पर चालू · ज़ेनॉन {#} %",
  "shut down · in the pit · xenon {#} %": "बंद · गर्त में · ज़ेनॉन {#} %",
  "shut down · restart possible · xenon {#} %": "बंद · पुनः चालू संभव · ज़ेनॉन {#} %",
  "left {#} %": "बाएं {#} %",
  "right {#} %": "दाएं {#} %",
  "tap a side to push rods in": "छड़ें डालने के लिए किसी ओर टैप करें",
  "more power left": "बाईं ओर अधिक शक्ति",
  "more power right": "दाईं ओर अधिक शक्ति",
  "swing period {#} h · {#} m core: the swing dies away": "दोलन आवर्त {#} घंटे · {#} m कोर: दोलन समाप्त होता है",
  "swing period {#} h · {#} m core: the swing dies away slowly": "दोलन आवर्त {#} घंटे · {#} m कोर: दोलन धीरे-धीरे समाप्त होता है",
  "swing period {#} h · {#} m core: the swing grows": "दोलन आवर्त {#} घंटे · {#} m कोर: दोलन बढ़ता है",
  "{#} m core: push the rods to start a swing": "{#} m कोर: दोलन शुरू करने के लिए छड़ें डालें",
  "illustration": "चित्रण",
});
