/* Hindi: breeding (नए ईंधन का प्रजनन) */
WT.L.ch.breeding = {
  num: "पाठ 1", title: "नए ईंधन का प्रजनन", short: "प्रजनन",
  html: `
<div class="step">
  <h3>उर्वर बनता है विखंडनीय</h3>
  <p>यूरेनियम-238 मुश्किल से ही विखंडित होता है, पर वह एक न्यूट्रॉन पकड़ सकता है। दो बीटा क्षय के बाद (हर बार भीतर का एक न्यूट्रॉन प्रोटॉन में बदलता है) वह प्लूटोनियम-239 बन जाता है, जो आसानी से विखंडित होता है। थोरियम-232 भी यही करता है और यूरेनियम-233 बन जाता है।</p>
  <div class="btns"><button class="btn ghost" data-act="bcU" aria-pressed="true">यूरेनियम-238</button> <button class="btn ghost" data-act="bcT" aria-pressed="false">थोरियम-232</button></div>
</div>
<div class="step">
  <h3>न्यूट्रॉन बजट</h3>
  <p>विखंडनीय ईंधन में अवशोषित हर न्यूट्रॉन <i>η</i> नए न्यूट्रॉन लौटाता है। एक को अगला विखंडन कराना होता है और कुछ खो जाते हैं; जो बचता है वह प्रजनन कर सकता है। यूरेनियम-235 और धीमे न्यूट्रॉनों के साथ हर जले हुए नाभिक पर केवल लगभग 0.6 नए विखंडनीय नाभिक बनते हैं।</p>
  <div class="btns"><button class="btn ghost" data-act="bfU5" aria-pressed="true">U-235</button> <button class="btn ghost" data-act="bfP9" aria-pressed="false">Pu-239</button> <button class="btn ghost" data-act="bfU3" aria-pressed="false">U-233</button></div>
  <div class="btns"><button class="btn ghost" data-act="bsT" aria-pressed="true">धीमे न्यूट्रॉन</button> <button class="btn ghost" data-act="bsF" aria-pressed="false">तेज न्यूट्रॉन</button></div>
</div>
<div class="step">
  <h3>तेज न्यूट्रॉन प्रजनन करते हैं</h3>
  <p>प्रजनन के लिए एक न्यूट्रॉन को शृंखला जारी रखनी है और कम से कम एक को नया ईंधन बनाना है, इसलिए <i>η</i> को 2 से, हानियों से अधिक अंतर से, बड़ा होना चाहिए। तेज रिएक्टर में प्लूटोनियम-239 लगभग 2.4 देता है: पर्याप्त से अधिक।</p>
  <div class="ctl"><label for="br-l1">खोए न्यूट्रॉन</label><input id="br-l1" type="range" data-bind="L" data-instant min="0.05" max="0.8" step="0.01" value="0.2"><output data-show="L" data-fmt="2"></output></div>
</div>
<div class="step">
  <h3>धीमे न्यूट्रॉनों के साथ थोरियम</h3>
  <p>धीमे न्यूट्रॉनों के साथ प्लूटोनियम-239 केवल लगभग 2.1 देता है, पर यूरेनियम-233 2.29 देता है। यही अंतर थोरियम रिएक्टर को धीमे न्यूट्रॉनों से प्रजनन करने देता है, बशर्ते वह बहुत कम न्यूट्रॉन गंवाए। हानियां तब तक घटाइए जब तक प्रजनन न होने लगे।</p>
  <div class="ctl"><label for="br-l2">खोए न्यूट्रॉन</label><input id="br-l2" type="range" data-bind="L" data-instant min="0.05" max="0.8" step="0.01" value="0.35"><output data-show="L" data-fmt="2"></output></div>
</div>
<div class="step">
  <h3>रूपांतरण अनुपात</h3>
  <p>रूपांतरण अनुपात यह है कि हर जले हुए विखंडनीय नाभिक पर कितने नए विखंडनीय नाभिक बनते हैं। 1 से नीचे ईंधन धीरे-धीरे घटता है (रूपांतरक, आज के जल रिएक्टरों की तरह); 1 से ऊपर रिएक्टर के अंत में शुरुआत से अधिक ईंधन होता है (प्रजनक)।</p>
  <div class="btns"><button class="btn ghost" data-act="bfU5" aria-pressed="true">U-235</button> <button class="btn ghost" data-act="bfP9" aria-pressed="false">Pu-239</button> <button class="btn ghost" data-act="bfU3" aria-pressed="false">U-233</button></div>
  <div class="btns"><button class="btn ghost" data-act="bsT" aria-pressed="true">धीमे न्यूट्रॉन</button> <button class="btn ghost" data-act="bsF" aria-pressed="false">तेज न्यूट्रॉन</button></div>
</div>`,
};
Object.assign(WT.L.labels, {
  "illustration": "चित्रण",
  "U{#}": "U{#}",
  "Np{#}": "Np{#}",
  "Pu{#}": "Pu{#}",
  "Th{#}": "Th{#}",
  "Pa{#}": "Pa{#}",
  "{#} p": "{#} p",
  "{#} protons": "{#} प्रोटॉन",
  "fertile": "उर्वर",
  "fertile: barely splits": "उर्वर: मुश्किल से विखंडित",
  "fissile": "विखंडनीय",
  "fissile: splits easily": "विखंडनीय: आसानी से विखंडित",
  "+ n": "+ n",
  "catch": "प्रग्रहण",
  "{#} min": "{#} मिनट",
  "{#} d": "{#} दिन",
  "e⁻": "e⁻",
  "electron": "इलेक्ट्रॉन",
  "antineutrino": "प्रतिन्यूट्रिनो",
  "{a} waiting: day {b}": "{a} प्रतीक्षा में: दिन {b}",
  "a batch of {a} waiting · day {b}": "{a} का एक समूह प्रतीक्षा में · दिन {b}",
  "{a} % now {b}": "{a} % अब {b}",
  "after {#} weeks, {#} % has become Pu{#}": "{#} सप्ताह बाद {#} % Pu{#} बन चुका है",
  "after {#} months, {#} % has become U{#}": "{#} महीने बाद {#} % U{#} बन चुका है",
  "slow step: Np{#}, half-life {#} d": "धीमा चरण: Np{#}, अर्ध-आयु {#} दिन",
  "the slow step is Np{#} (half-life {#} days)": "धीमा चरण Np{#} है (अर्ध-आयु {#} दिन)",
  "slow step: Pa{#}, half-life {#} d": "धीमा चरण: Pa{#}, अर्ध-आयु {#} दिन",
  "the slow step is Pa{#} (half-life {#} days)": "धीमा चरण Pa{#} है (अर्ध-आयु {#} दिन)",
  "slow neutrons": "धीमे न्यूट्रॉन",
  "fast neutrons": "तेज न्यूट्रॉन",
  "next fission": "अगला विखंडन",
  "U{#} → Pu{#}": "U{#} → Pu{#}",
  "Th{#} → U{#}": "Th{#} → U{#}",
  "lost": "खोए",
  "next fission: keeps the chain going": "अगला विखंडन: शृंखला जारी रखता है",
  "breeds: U{#} → Pu{#}": "प्रजनन: U{#} → Pu{#}",
  "breeds: Th{#} → U{#}": "प्रजनन: Th{#} → U{#}",
  "lost: water, steel, poisons, leakage": "खोए: पानी, इस्पात, विष, रिसाव",
  "{a} per absorption": "{a} प्रति अवशोषण",
  "chain": "शृंखला",
  "breed": "प्रजनन",
  "η ≈ {a}": "η ≈ {a}",
  "η = {a}": "η = {a}",
  "{#}: breeding line": "{#}: प्रजनन रेखा",
  "neutrons per absorption": "न्यूट्रॉन प्रति अवशोषण",
  "neutrons out per neutron absorbed in the fuel": "ईंधन में अवशोषित प्रति न्यूट्रॉन निकलने वाले न्यूट्रॉन",
  "conversion ratio ≈ η − {#} − lost = {a}: breeds": "रूपांतरण अनुपात ≈ η − {#} − हानि = {a}: प्रजनन",
  "conversion ratio ≈ η − {#} − lost = {a}: breeds, makes more fuel than it burns": "रूपांतरण अनुपात ≈ η − {#} − हानि = {a}: प्रजनन, जितना जलाता है उससे अधिक ईंधन बनाता है",
  "conversion ratio ≈ η − {#} − lost = {a}: converts": "रूपांतरण अनुपात ≈ η − {#} − हानि = {a}: रूपांतरण",
  "conversion ratio ≈ η − {#} − lost = {a}: converts, makes less fuel than it burns": "रूपांतरण अनुपात ≈ η − {#} − हानि = {a}: रूपांतरण, जितना जलाता है उससे कम ईंधन बनाता है",
  "U{#} (fertile)": "U{#} (उर्वर)",
  "Th{#} (fertile)": "Th{#} (उर्वर)",
  "split": "विखंडित",
  "split (fission products)": "विखंडित (विखंडन उत्पाद)",
  "burned {a}": "जले {a}",
  "made {a}": "बने {a}",
  "{a} · slow neutrons": "{a} · धीमे न्यूट्रॉन",
  "{a} · fast neutrons": "{a} · तेज न्यूट्रॉन",
  "conversion ratio {a}: a breeder": "रूपांतरण अनुपात {a}: प्रजनक",
  "conversion ratio {a}: a converter": "रूपांतरण अनुपात {a}: रूपांतरक",
});
