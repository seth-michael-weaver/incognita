/* Hindi: spectrum (तेज और तापीय रिएक्टर) */
WT.L.ch.spectrum = {
  num: "पाठ 1", title: "तेज और तापीय रिएक्टर", short: "तेज बनाम तापीय",
  html: `
<div class="step">
  <h3>न्यूट्रॉन कितने तेज हैं</h3>
  <p>न्यूट्रॉन तेज पैदा होते हैं, लगभग 2 MeV पर। जल रिएक्टर में वे हाइड्रोजन से टकराते रहते हैं जब तक वे पानी के अपने परमाणुओं जितने धीमे न हो जाएं: <b>तापीय</b>। तेज रिएक्टर में मंदक नहीं होता, इसलिए वे तेज ही रहते हैं। दोनों के बीच स्लाइडर खिसकाइए।</p>
  <div class="ctl"><label for="spc-m1">मंदन</label><input id="spc-m1" type="range" data-bind="mod" data-instant min="0" max="1" step="0.01" value="1"><output data-show="mod" data-fmt="2"></output></div>
</div>
<div class="step">
  <h3>अतिरिक्त न्यूट्रॉन</h3>
  <p><i>η</i> यह है कि ईंधन का एक नाभिक हर अवशोषित न्यूट्रॉन के बदले कितने न्यूट्रॉन लौटाता है। एक श्रृंखला चलाए रखता है; नया ईंधन प्रजनित करने के लिए एक और बचा हुआ चाहिए, यानी <i>η</i> 2 से काफी ऊपर। प्लूटोनियम-239 ऐसा केवल तेज न्यूट्रॉनों के साथ कर पाता है।</p>
  <div class="ctl"><label for="spc-m2">मंदन</label><input id="spc-m2" type="range" data-bind="mod" data-instant min="0" max="1" step="0.01" value="0"><output data-show="mod" data-fmt="2"></output></div>
</div>
<div class="step">
  <h3>बचे हुए को जलाना</h3>
  <p>अमेरिसियम जैसे भारी बचे हुए नाभिक धीमे न्यूट्रॉनों को ज्यादातर बस निगल लेते हैं और भारी हो जाते हैं। तेज न्यूट्रॉन उनके कहीं बड़े हिस्से का विखंडन करते हैं, इसलिए तेज रिएक्टर उन्हें जला सकता है।</p>
  <div class="ctl"><label for="spc-m3">मंदन</label><input id="spc-m3" type="range" data-bind="mod" data-instant min="0" max="1" step="0.01" value="0"><output data-show="mod" data-fmt="2"></output></div>
</div>
<div class="step">
  <h3>कीमत</h3>
  <p>धीमा न्यूट्रॉन विखंडन कराने की कहीं अधिक संभावना रखता है: 1 MeV पर लक्ष्य सैकड़ों गुना छोटा होता है। इसलिए तेज कोर को कहीं अधिक समृद्ध ईंधन चाहिए, 3–5 % यूरेनियम-235 के बजाय लगभग 15–25 % प्लूटोनियम।</p>
  <div class="ctl"><label for="spc-m4">मंदन</label><input id="spc-m4" type="range" data-bind="mod" data-instant min="0" max="1" step="0.01" value="1"><output data-show="mod" data-fmt="2"></output></div>
</div>`,
};
Object.assign(WT.L.labels, {
  "U{#}": "U{#}",
  "Pu{#}": "Pu{#}",
  "Np{#}": "Np{#}",
  "Am{#}": "Am{#}",
  "Cm{#}": "Cm{#}",
  "{#} % split": "{#} % विखंडित",
  "water: neutrons slow down": "पानी: न्यूट्रॉन धीमे होते हैं",
  "water reactor: hydrogen slows the neutrons": "जल रिएक्टर: हाइड्रोजन न्यूट्रॉनों को धीमा करता है",
  "sodium: they stay fast": "सोडियम: वे तेज रहते हैं",
  "fast reactor: sodium barely slows them": "तेज रिएक्टर: सोडियम उन्हें मुश्किल से धीमा करता है",
  "partly moderated": "आंशिक मंदन",
  "sodium": "सोडियम",
  "no moderator (sodium)": "मंदक नहीं (सोडियम)",
  "water": "पानी",
  "thermal": "तापीय",
  "resonances": "अनुनाद",
  "slowing down (resonances)": "मंदन (अनुनाद)",
  "fast": "तेज",
  "{#} MeV": "{#} MeV",
  "{#} keV": "{#} keV",
  "{#} eV": "{#} eV",
  "neutron energy →": "न्यूट्रॉन ऊर्जा →",
  "born ~{#} MeV": "जन्म ~{#} MeV पर",
  "born near {#} MeV": "लगभग {#} MeV पर जन्म",
  "η = {#}: one to continue, one to breed": "η = {#}: एक श्रृंखला के लिए, एक प्रजनन के लिए",
  "average η: U{#} {#} · Pu{#} {#}": "औसत η: U{#} {#} · Pu{#} {#}",
  "averaged over this spectrum:  η(U{#}) ≈ {#}   η(Pu{#}) ≈ {#}": "इस स्पेक्ट्रम पर औसत:  η(U{#}) ≈ {#}   η(Pu{#}) ≈ {#}",
  "{#} b": "{#} b",
  "≈ {#} b": "≈ {#} b",
  "Pu{#} fission target": "Pu{#} विखंडन लक्ष्य",
  "Pu{#} fission cross section (target size)": "Pu{#} विखंडन अनुप्रस्थ काट (लक्ष्य का आकार)",
  "{#} MeV: a target ~{#} times smaller": "{#} MeV: लक्ष्य ~{#} गुना छोटा",
  "at {#} MeV the target is about {#} times smaller than at {#} eV": "{#} MeV पर लक्ष्य लगभग {#} गुना छोटा है, {#} eV की तुलना में",
  "most neutrons end up thermal": "अधिकांश न्यूट्रॉन अंत में तापीय होते हैं",
  "most neutrons are slowed all the way to thermal": "अधिकांश न्यूट्रॉन तापीय ऊर्जा तक पूरी तरह धीमे होते हैं",
  "most stay between {#} keV and {#} MeV": "अधिकांश {#} keV और {#} MeV के बीच रहते हैं",
  "most neutrons stay between {#} keV and {#} MeV": "अधिकांश न्यूट्रॉन {#} keV और {#} MeV के बीच रहते हैं",
  "many linger at in-between energies": "कई बीच की ऊर्जाओं पर ठहरते हैं",
  "many neutrons linger at in-between energies": "कई न्यूट्रॉन बीच की ऊर्जाओं पर ठहरे रहते हैं",
  "thermal ≈ {#} eV, ~{#} km/s": "तापीय ≈ {#} eV, ~{#} km/s",
  "thermal: kT ≈ {#} eV in hot water, about {#} km/s": "तापीय: गर्म पानी में kT ≈ {#} eV, लगभग {#} km/s",
  "the rest are captured and grow heavier": "बाकी प्रग्रहित होकर भारी हो जाते हैं",
  "the rest are captured: the nucleus just grows heavier": "बाकी प्रग्रहित होते हैं: नाभिक बस भारी हो जाता है",
  "illustrative shapes": "उदाहरणात्मक आकृतियां",
});
