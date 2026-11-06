/* Hindi: diffusion (क्रांतिक आकार और रिसाव) */
WT.L.ch.diffusion = {
  num: "पाठ 1", title: "क्रांतिक आकार और रिसाव", short: "क्रांतिक आकार",
  html: `
<div class="step">
  <h3>न्यूट्रॉन भटकते हैं, कुछ रिसते हैं</h3>
  <p>न्यूट्रॉन एक टक्कर से दूसरी टक्कर तक टेढ़ा-मेढ़ा चलता है, जब तक कोई चीज़ उसे अवशोषित न कर ले। किनारे के पास जन्मा न्यूट्रॉन भटककर बाहर निकल सकता है और खो सकता है। बड़े कोर में आयतन के अनुपात में सतह कम होती है, इसलिए कम अंश रिसता है।</p>
  <div class="ctl"><label for="df-w0">कोर की चौड़ाई (cm)</label><input id="df-w0" type="range" data-bind="w" data-instant min="20" max="200" step="2" value="60"><output data-show="w" data-fmt="0"></output></div>
</div>
<div class="step">
  <h3>फ्लक्स का आकार</h3>
  <p>न्यूट्रॉन आबादी एक ऐसे आकार में स्थिर हो जाती है जो किनारे पर लगभग शून्य तक गिरता है: पट्टिका में कोसाइन, गोले में sin(<i>r</i>)/<i>r</i>, बेलन में बेसेल फलन गुणा कोसाइन। उसे कितनी तीव्रता से मुड़ना पड़ता है, यह <b>ज्यामितीय बकलिंग</b> <i>B</i>² है।</p>
  <div class="btns"><button class="btn ghost" data-act="dfslab" aria-pressed="false">पट्टिका</button><button class="btn ghost" data-act="dfsph" aria-pressed="true">गोला</button><button class="btn ghost" data-act="dfcyl" aria-pressed="false">बेलन</button></div>
  <div class="ctl"><label for="df-w1">कोर की चौड़ाई (cm)</label><input id="df-w1" type="range" data-bind="w" data-instant min="20" max="200" step="2" value="80"><output data-show="w" data-fmt="0"></output></div>
</div>
<div class="step">
  <h3>क्रांतिक आकार</h3>
  <p>एक-समूह विसरण से <i>k</i><sub>eff</sub> = <i>k</i><sub>∞</sub> / (1 + <i>M</i>²<i>B</i>²) मिलता है, जहां जल रिएक्टर में प्रवास क्षेत्रफल <i>M</i>² लगभग 60 cm² है। कोर तब क्रांतिक होता है जब <i>B</i>² पदार्थ बकलिंग (<i>k</i><sub>∞</sub> − 1)/<i>M</i>² के बराबर हो। वह आकार ढूंढिए।</p>
  <div class="btns"><button class="btn ghost" data-act="dfslab" aria-pressed="false">पट्टिका</button><button class="btn ghost" data-act="dfsph" aria-pressed="true">गोला</button><button class="btn ghost" data-act="dfcyl" aria-pressed="false">बेलन</button></div>
  <div class="ctl"><label for="df-w2">कोर की चौड़ाई (cm)</label><input id="df-w2" type="range" data-bind="w" data-instant min="20" max="200" step="1" value="90"><output data-show="w" data-fmt="0"></output></div>
</div>
<div class="step">
  <h3>परावर्तक न्यूट्रॉन बचाता है</h3>
  <p>पट्टिका कोर को पानी से घेर दीजिए: बाहर निकलने वाले कुछ न्यूट्रॉन वापस प्रकीर्णित हो जाते हैं। फ्लक्स अब कोर के किनारे पर शून्य तक नहीं गिरता, इसलिए पतला कोर वही <i>k</i> पा लेता है; यह लाभ <b>परावर्तक बचत</b> है, यहां प्रति ओर लगभग 6 cm।</p>
  <div class="btns"><button class="btn ghost" data-act="dfrefl" aria-pressed="true">जल परावर्तक</button></div>
  <div class="ctl"><label for="df-w3">कोर की चौड़ाई (cm)</label><input id="df-w3" type="range" data-bind="w" data-instant min="20" max="120" step="1" value="44"><output data-show="w" data-fmt="0"></output></div>
</div>`,
};

Object.assign(WT.L.labels, {
  "drag the edge": "किनारा खींचें",
  "{#} cm": "{#} cm",
  "red: leaked": "लाल: रिस गए",
  "red: leaked out · blue: absorbed inside": "लाल: बाहर रिस गए · नीले: भीतर अवशोषित",
  "leak: walk {#} % · diffusion {#} %": "रिसाव: भ्रमण {#} % · विसरण {#} %",
  "leak: walk … · diffusion {#} %": "रिसाव: भ्रमण … · विसरण {#} %",
  "share leaking: random walk {#} % · diffusion theory {#} %": "रिसने वाला अंश: यादृच्छिक भ्रमण {#} % · विसरण सिद्धांत {#} %",
  "share leaking: random walk … · diffusion theory {#} %": "रिसने वाला अंश: यादृच्छिक भ्रमण … · विसरण सिद्धांत {#} %",
  "k_eff = k∞ × ({#} − leak) = {#}": "k_eff = k∞ × ({#} − रिसाव) = {#}",
  "water": "पानी",
  "slab core": "पट्टिका कोर",
  "slab": "पट्टिका",
  "sphere": "गोला",
  "cylinder": "बेलन",
  "flux across the middle": "बीच से होकर फ्लक्स",
  "−D∇²φ + Σₐφ = (νΣ_f / k) φ": "−D∇²φ + Σₐφ = (νΣ_f / k) φ",
  "B² = (π/a)² = {#} × {#}⁻⁴ cm⁻²": "B² = (π/a)² = {#} × {#}⁻⁴ cm⁻²",
  "B² = (π/R)² = {#} × {#}⁻⁴ cm⁻²": "B² = (π/R)² = {#} × {#}⁻⁴ cm⁻²",
  "B² = ({#}/R)² + (π/H)² = {#} × {#}⁻⁴ cm⁻²": "B² = ({#}/R)² + (π/H)² = {#} × {#}⁻⁴ cm⁻²",
  "{#} × {#}⁻⁴ cm⁻²": "{#} × {#}⁻⁴ cm⁻²",
  "slab {#} cm wide · smaller core → sharper bend → larger B²": "पट्टिका, {#} cm चौड़ी · छोटा कोर → तीव्र मोड़ → बड़ा B²",
  "sphere {#} cm wide · smaller core → sharper bend → larger B²": "गोला, {#} cm चौड़ा · छोटा कोर → तीव्र मोड़ → बड़ा B²",
  "cylinder {#} cm wide · smaller core → sharper bend → larger B²": "बेलन, {#} cm चौड़ा · छोटा कोर → तीव्र मोड़ → बड़ा B²",
  "k = {#}": "k = {#}",
  "critical {#} cm": "क्रांतिक {#} cm",
  "core width →": "कोर की चौड़ाई →",
  "critical: B² = B²ₘ, k_eff = {#}": "क्रांतिक: B² = B²ₘ, k_eff = {#}",
  "k_eff = {#} / ({#} + {#} cm² × {#}e{#} cm⁻²) = {#}": "k_eff = {#} / ({#} + {#} cm² × {#}e{#} cm⁻²) = {#}",
  "reflected: k_eff {#} · bare: {#} · savings {#} cm per side": "परावर्तक सहित: k_eff {#} · नग्न: {#} · बचत प्रति ओर {#} cm",
  "bare: k_eff {#} · critical at {#} cm": "नग्न: k_eff {#} · {#} cm पर क्रांतिक",
  "illustration": "चित्रण",
});
