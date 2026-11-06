/* Hindi: kinetics (रिएक्टर गतिकी: छह समूह और इनआवर समीकरण) */
WT.L.ch.kinetics = {
  num: "पाठ 1", title: "रिएक्टर गतिकी: छह समूह और इनआवर समीकरण", short: "गतिकी",
  html: `
<div class="step">
  <h3>देर से आने वाले न्यूट्रॉनों के छह समूह</h3>
  <p>विलंबित न्यूट्रॉन विखंडन उत्पादों के लगभग छह समूहों से आते हैं, जिनकी अर्ध-आयु 0.23 s से 56 s तक है (Keepin, यूरेनियम-235)। 2-s और 22-s समूह उनमें से अधिकतर छोड़ते हैं, जबकि दीर्घजीवी समूह प्रतीक्षारत भंडार का अधिकांश रखते हैं: औसत विलंब Σ <i>a</i><sub>i</sub>/<i>λ</i><sub>i</sub> ≈ 13 s। विखंडन रोकिए और देखिए कि हर समूह अपनी गति से कैसे घटता है।</p>
  <div class="btns"><button class="btn" data-act="kistop" aria-pressed="false">विखंडन रोकें</button></div>
</div>
<div class="step">
  <h3>इनआवर समीकरण</h3>
  <p>छह-समूह बिंदु गतिकी में <i>n</i> ∝ e<sup><i>ωt</i></sup> रखिए, तो <i>ρ</i> = <i>ω</i>Λ + Σ <i>β</i><sub>i</sub><i>ω</i>/(<i>ω</i> + <i>λ</i><sub>i</sub>) मिलता है: −<i>λ</i><sub>i</sub> पर स्थित ध्रुवों से बंटी सात शाखाएं। <i>ρ</i> में एक सोपान हर शाखा को एक बार काटता है; सबसे दाहिना मूल स्थिर काल <i>T</i> = 1/<i>ω</i><sub>1</sub> है, बाकी छह समाप्त हो जाते हैं।</p>
  <div class="ctl"><label for="ki-r1">अभिक्रियाशीलता ρ ($)</label><input id="ki-r1" type="range" data-bind="rd" data-instant min="-2" max="1.3" step="0.01" value="0.3"><output data-show="rd" data-fmt="2"></output></div>
</div>
<div class="step">
  <h3>तात्कालिक उछाल और तात्कालिक क्रांतिकता</h3>
  <p>अभिक्रियाशीलता का एक सोपान पहले मिलीसेकंडों में शक्ति को <i>P</i><sub>1</sub>/<i>P</i><sub>0</sub> ≈ <i>β</i>/(<i>β</i> − <i>ρ</i>) गुना उठाता है, फिर वह स्थिर काल पर बढ़ती है। <i>ρ</i> = 1 $ पर केवल तात्कालिक न्यूट्रॉन ही क्रांतिक होते हैं और काल सिमटकर Λ/(<i>ρ</i> − <i>β</i>) की ओर जाता है।</p>
  <div class="ctl"><label for="ki-r2">अभिक्रियाशीलता ρ ($)</label><input id="ki-r2" type="range" data-bind="rj" data-instant min="0.05" max="1.3" step="0.01" value="0.5"><output data-show="rj" data-fmt="2"></output></div>
</div>
<div class="step">
  <h3>स्क्रैम के बाद</h3>
  <p>बड़ी ऋणात्मक अभिक्रियाशीलता डालिए: शक्ति तुरंत लगभग <i>β</i>/(<i>β</i> − <i>ρ</i>) तक गिरती है, और फिर सबसे दीर्घजीवी समूह के क्षय से तेज़ नहीं गिर सकती। स्क्रैम कितना भी गहरा हो, काल −1/<i>λ</i><sub>1</sub> ≈ −80 s की ओर जाता है।</p>
  <div class="ctl"><label for="ki-r3">अभिक्रियाशीलता ρ ($)</label><input id="ki-r3" type="range" data-bind="rs" data-instant min="-30" max="-0.5" step="0.5" value="-10"><output data-show="rs" data-fmt="1"></output></div>
</div>`,
};

Object.assign(WT.L.labels, {
  "Stop fissions": "विखंडन रोकें",
  "Restart fissions": "विखंडन फिर शुरू करें",
  "half-life · share emitted": "अर्ध-आयु · उत्सर्जित अंश",
  "waiting stock": "प्रतीक्षारत भंडार",
  "delayed neutrons out": "निकलते विलंबित न्यूट्रॉन",
  "{#} s": "{#} s",
  "{#} s after stopping · delayed emission {#} % of the start": "रोकने के {#} s बाद · विलंबित उत्सर्जन आरंभ का {#} %",
  "mean delay Σ aᵢ/λᵢ = {#} s · β = {#} (U{#})": "औसत विलंब Σ aᵢ/λᵢ = {#} s · β = {#} (U{#})",
  "Keepin six-group data": "Keepin के छह-समूह आंकड़े",
  "prompt critical": "तात्कालिक क्रांतिक",
  "drag ρ": "ρ खींचें",
  "prompt root": "तात्कालिक मूल",
  "prompt root ≈ −(β−ρ)/Λ": "तात्कालिक मूल ≈ −(β−ρ)/Λ",
  "ω ({#}/s), stretched": "ω ({#}/s), खिंचा हुआ",
  "ω ({#}/s), axis stretched (asinh)": "ω ({#}/s), अक्ष खिंचा हुआ (asinh)",
  "ρ = {#}: power stays flat": "ρ = {#}: शक्ति स्थिर रहती है",
  "stable period T = {#}/ω₁ = {#} ms": "स्थिर काल T = {#}/ω₁ = {#} ms",
  "stable period T = {#}/ω₁ = {#} s": "स्थिर काल T = {#}/ω₁ = {#} s",
  "stable period T = {#}/ω₁ = {#} min": "स्थिर काल T = {#}/ω₁ = {#} मिनट",
  "stable period T = {#}/ω₁ = {#} h": "स्थिर काल T = {#}/ω₁ = {#} घंटे",
  "drag the rods out": "छड़ें बाहर खींचें",
  "prompt jump β/(β−ρ) = {#}": "तात्कालिक उछाल β/(β−ρ) = {#}",
  "power": "शक्ति",
  "prompt critical · period {#} ms (Λ = {#} µs)": "तात्कालिक क्रांतिक · काल {#} ms (Λ = {#} µs)",
  "prompt critical · period {#} s (Λ = {#} µs)": "तात्कालिक क्रांतिक · काल {#} s (Λ = {#} µs)",
  "prompt critical · period {#} min (Λ = {#} µs)": "तात्कालिक क्रांतिक · काल {#} मिनट (Λ = {#} µs)",
  "prompt critical · period {#} h (Λ = {#} µs)": "तात्कालिक क्रांतिक · काल {#} घंटे (Λ = {#} µs)",
  "ρ = {#} $ · stable period {#} ms": "ρ = {#} $ · स्थिर काल {#} ms",
  "ρ = {#} $ · stable period {#} s": "ρ = {#} $ · स्थिर काल {#} s",
  "ρ = {#} $ · stable period {#} min": "ρ = {#} $ · स्थिर काल {#} मिनट",
  "ρ = {#} $ · stable period {#} h": "ρ = {#} $ · स्थिर काल {#} घंटे",
  "drag the rods in": "छड़ें भीतर धकेलें",
  "prompt drop to {#}": "तात्कालिक गिरावट {#} तक",
  "slope e^(−t/{#} s)": "ढलान e^(−t/{#} s)",
  "slope e^(−t / {#} s): the {#} s group": "ढलान e^(−t / {#} s): {#} s वाला समूह",
  "power ×{#} speed": "शक्ति, ×{#} गति",
  "ρ = {#} $ · stable period {#} ms (limit {#} s)": "ρ = {#} $ · स्थिर काल {#} ms (सीमा {#} s)",
  "ρ = {#} $ · stable period {#} s (limit {#} s)": "ρ = {#} $ · स्थिर काल {#} s (सीमा {#} s)",
  "ρ = {#} $ · stable period {#} min (limit {#} s)": "ρ = {#} $ · स्थिर काल {#} मिनट (सीमा {#} s)",
  "ρ = {#} $ · stable period {#} h (limit {#} s)": "ρ = {#} $ · स्थिर काल {#} घंटे (सीमा {#} s)",
});
