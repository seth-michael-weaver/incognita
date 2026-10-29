/* Hindi: doppler (अध्याय 20, डॉप्लर विस्तारण) */
WT.L.ch.doppler = {
  num: "अध्याय 20", title: "डॉप्लर विस्तारण", short: "डॉप्लर",
  html: `
<div class="step">
  <h3>लक्ष्य की ऊष्मीय गति</h3>
  <p>ईंधन जितना गर्म, उसके परमाणु उतनी तेजी से कांपते हैं। जब न्यूट्रॉन पहुंचता है, तब हर यूरेनियम परमाणु अब स्थिर नहीं बैठा होता।</p>
  <div class="ctl"><label for="dop-t1">ईंधन ताप (K)</label><input id="dop-t1" type="range" data-bind="T" data-instant min="300" max="1500" step="10" value="600"><output data-show="T" data-fmt="0"></output></div>
</div>
<div class="step">
  <h3>डॉप्लर विस्तारण</h3>
  <p>वक्र न्यूट्रॉन की ऊर्जा के सापेक्ष यूरेनियम-238 द्वारा न्यूट्रॉन पकड़ने की संभावना है। उसकी ऊंचाई <b>बार्न</b> में एक लक्ष्य-क्षेत्रफल है (एक बार्न 10<sup>−24</sup> cm² है, मोटे तौर पर वह आकार जो नाभिक न्यूट्रॉन को दिखाता है)। क्योंकि परमाणु गतिमान हैं, कुछ न्यूट्रॉन से आमने-सामने मिलते हैं और कुछ उससे दूर भागते हैं, इसलिए संकरा शिखर फैल जाता है: नीचा और चौड़ा। उसका क्षेत्रफल वही रहता है।</p>
  <div class="ctl"><label for="dop-t2">ईंधन ताप (K)</label><input id="dop-t2" type="range" data-bind="T" data-instant min="300" max="1500" step="10" value="1200"><output data-show="T" data-fmt="0"></output></div>
</div>
<div class="step">
  <h3>अनुनाद स्व-परिरक्षण</h3>
  <p>ईंधन की गोली मोटी होती है। छायांकित पट्टी हर ऊर्जा पर उसके द्वारा रोके गए न्यूट्रॉनों का अंश है। शिखर का केंद्र पहले से ही सब कुछ रोक लेता है, गर्म हो या ठंडा, इसलिए नीचे शिखर से वहां कुछ नहीं खोता; चौड़े पंख अधिक पकड़ते हैं। अधिक न्यूट्रॉन विखंडन कराने के बजाय प्रग्रहण में खो जाते हैं, इसलिए <i>k</i> अपने आप घट जाता है। (<i>k</i> यह है कि एक विखंडन से कितने नए विखंडन होते हैं; अध्याय <a href="#critical">21</a> इसे समझाता है।)</p>
  <div class="ctl"><label for="dop-t3">ईंधन ताप (K)</label><input id="dop-t3" type="range" data-bind="T" data-instant min="300" max="1500" step="10" value="900"><output data-show="T" data-fmt="0"></output></div>
</div>`,
};

// canvas labels added 2026-10-29 (I18NLABELS_B)
Object.assign(WT.L.labels, {
  "uranium atoms in the fuel": "ईंधन में यूरेनियम परमाणु",
  "{#} K": "{#} K",
  "caught in the peak": "शिखर में पकड़े गए",
  "k": "k",
  "neutron energy (eV) →": "न्यूट्रॉन ऊर्जा (eV) →",
  "capture cross section": "प्रग्रहण अनुप्रस्थ काट",
  "peak {#}k barns · Doppler width {#} meV · area unchanged": "शिखर {#}k बार्न · डॉप्लर चौड़ाई {#} meV · क्षेत्रफल वही",
  "all stopped": "सब रुके",
  "wider wings catch more": "चौड़े पंख अधिक पकड़ते हैं",
  "share of neutrons stopped in the fuel": "ईंधन में रुके न्यूट्रॉनों का अंश",
  "the peak's centre already stops everything; the wider wings catch more": "शिखर का केंद्र पहले से सब रोकता है; चौड़े पंख अधिक पकड़ते हैं",
});
