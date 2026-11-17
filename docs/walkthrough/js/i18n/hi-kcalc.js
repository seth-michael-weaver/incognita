/* Hindi: kcalc (Computing criticality) */
WT.L.ch.kcalc = {
  num: "पाठ 1", title: "क्रांतिकता की गणना", short: "k की गणना",
  html: `
<div class="step">
  <h3>बेंचमार्क</h3>
  <p>ICSBEP के चार तीव्र धात्विक क्रांतिक संयोजन, पैमाने पर। Godiva और Jezebel बिना परावर्तक के गोले हैं; Flattop-25 और Flattop-Pu में प्राकृतिक यूरेनियम का परावर्तक है।</p>
</div>
<div class="step">
  <h3>परिकलित <i>k</i><sub>eff</sub></h3>
  <p>OpenMC, सतत ऊर्जा, 3-D ज्यामिति। चारों बेंचमार्क के ±1σ के भीतर हैं। फ़िट में <i>k</i><sub>eff</sub> का उपयोग नहीं होता।</p>
</div>
<div class="step">
  <h3>संवेदनशीलता प्रोफ़ाइल</h3>
  <p>हर अभिक्रिया के प्रति <i>k</i><sub>eff</sub> की सहायक (adjoint) संवेदनशीलता, प्रति इकाई लेथार्जी।</p>
  <div class="btns"><button class="btn ghost" data-act="se0" aria-pressed="true">Godiva</button><button class="btn ghost" data-act="se1" aria-pressed="false">Jezebel</button><button class="btn ghost" data-act="se2" aria-pressed="false">Flattop-Pu</button></div>
</div>
<div class="step">
  <h3>प्रत्यक्ष विक्षोभ से सत्यापन</h3>
  <p>संवेदनशीलता से अनुमानित बनाम दोबारा परिकलित <i>k</i><sub>eff</sub> परिवर्तन, 63 विक्षुब्ध डेटा सेट।</p>
</div>
<div class="step">
  <h3>C5G7 रिएक्टर कोर</h3>
  <p>OECD/NEA C5G7, 2-D चौथाई कोर, UO<sub>2</sub> और MOX की 1,056 छड़ें। <i>k</i><sub>eff</sub> संदर्भ से −19&nbsp;pcm; छड़ शक्ति की अधिकतम त्रुटि 0.13&nbsp;%।</p>
</div>`,
};

Object.assign(WT.L.labels, {
  "{#} pcm  (±{#} benchmark)": "{#} pcm  (बेंचमार्क ±{#})",
  "+{#} pcm  (±{#} benchmark)": "+{#} pcm  (बेंचमार्क ±{#})",
  "Calculated − experimental k, with the benchmark ±{#}σ band": "परिकलित − प्रायोगिक k, बेंचमार्क के ±{#}σ बैंड के साथ",
  "Drag to rotate": "घुमाने के लिए खींचें",
  "Godiva, integral sensitivity: ν {#}, fission {#} (% k per % change)": "Godiva, समाकल संवेदनशीलता: ν {#}, विखंडन {#} (प्रति % परिवर्तन k का %)",
  "Jezebel, integral sensitivity: ν {#}, fission {#} (% k per % change)": "Jezebel, समाकल संवेदनशीलता: ν {#}, विखंडन {#} (प्रति % परिवर्तन k का %)",
  "Flattop-Pu, integral sensitivity: ν {#}, fission {#} (% k per % change)": "Flattop-Pu, समाकल संवेदनशीलता: ν {#}, विखंडन {#} (प्रति % परिवर्तन k का %)",
  "Godiva: ν {#}, fission {#}": "Godiva: ν {#}, विखंडन {#}",
  "Jezebel: ν {#}, fission {#}": "Jezebel: ν {#}, विखंडन {#}",
  "Flattop-Pu: ν {#}, fission {#}": "Flattop-Pu: ν {#}, विखंडन {#}",
  "UO₂: {#} × mean": "UO₂: {#} × माध्य",
  "MOX {#} %: {#} × mean": "MOX {#} %: {#} × माध्य",
  "OpenMC re-solve, Δk (pcm)": "OpenMC पुनर्गणना, Δk (pcm)",
  "Predicted from sensitivities, Δk (pcm)": "संवेदनशीलता से अनुमानित, Δk (pcm)",
  "predicted Δk, pcm": "अनुमानित Δk, pcm",
  "U{#} capture": "U{#} प्रग्रहण",
  "Pu{#} capture": "Pu{#} प्रग्रहण",
  "U{#} elastic": "U{#} प्रत्यास्थ",
  "Pu{#} elastic": "Pu{#} प्रत्यास्थ",
  "U{#} fission": "U{#} विखंडन",
  "Pu{#} fission": "Pu{#} विखंडन",
  "U{#} inelastic": "U{#} अप्रत्यास्थ",
  "Pu{#} inelastic": "Pu{#} अप्रत्यास्थ",
  "U{#} neutrons per fission (ν)": "U{#} प्रति विखंडन न्यूट्रॉन (ν)",
  "Pu{#} neutrons per fission (ν)": "Pu{#} प्रति विखंडन न्यूट्रॉन (ν)",
  "Relative pin power (hover a pin)": "छड़ की सापेक्ष शक्ति (किसी छड़ पर पॉइंटर रखें)",
  "Relative pin power (tap a pin)": "छड़ की सापेक्ष शक्ति (किसी छड़ को टैप करें)",
  "To scale.": "पैमाने पर।",
  "To scale. Drag to rotate.": "पैमाने पर। घुमाने के लिए खींचें।",
  "core {#} cm, reflector {#} cm": "कोर {#} cm, परावर्तक {#} cm",
  "radius {#} cm": "त्रिज्या {#} cm",
  "{#} cm in {#} cm": "{#} cm / {#} cm",
  "k = {#}; reference {#} ({#} pcm)": "k = {#}; संदर्भ {#} ({#} pcm)",
  "k {#}, reference {#}": "k {#}, संदर्भ {#}",
  "plutonium in natural uranium": "प्राकृतिक यूरेनियम में प्लूटोनियम",
  "plutonium metal": "प्लूटोनियम धातु",
  "uranium{#} in natural uranium": "प्राकृतिक यूरेनियम में यूरेनियम{#}",
  "uranium{#} metal": "यूरेनियम{#} धातु",
  "water": "पानी",
  "×{#} of mean": "माध्य का ×{#}",
  "U{#} ν": "U{#} ν",
  "Pu{#} ν": "Pu{#} ν",
  "Godiva   k = {#}": "Godiva   k = {#}",
  "Godiva {#}": "Godiva {#}",
  "Godiva: rms {#} pcm": "Godiva: rms {#} pcm",
  "Jezebel   k = {#}": "Jezebel   k = {#}",
  "Jezebel {#}": "Jezebel {#}",
  "Jezebel: rms {#} pcm": "Jezebel: rms {#} pcm",
  "Flattop-Pu   k = {#}": "Flattop-Pu   k = {#}",
  "Flattop-Pu {#}": "Flattop-Pu {#}",
  "Flattop-Pu: rms {#} pcm": "Flattop-Pu: rms {#} pcm",
  "Flattop{#}   k = {#}": "Flattop{#}   k = {#}",
  "Flattop{#} {#}": "Flattop{#} {#}",
  "{#} pcm (±{#})": "{#} pcm (±{#})",
  "+{#} pcm (±{#})": "+{#} pcm (±{#})",
  "{#} cm": "{#} cm",
  "{#} keV": "{#} keV",
  "{#} MeV": "{#} MeV",
  "OpenMC Δk": "OpenMC Δk"
});
