/* Hindi: tokamak (अध्याय 31, चुंबकीय परिरोध) */
WT.L.ch.tokamak = {
  num: "अध्याय 31", title: "चुंबकीय परिरोध", short: "परिरोध",
  lead: "कोई दीवार 10 करोड़ डिग्री की गैस को छू नहीं सकती। चुंबकीय क्षेत्र उसे थाम सकता है, क्योंकि आवेशित कण क्षेत्र रेखाओं को पार नहीं कर सकते।",
  html: `
<div class="step">
  <h3>चुंबकीय क्षेत्र में घूर्णन</h3>
  <p>क्षेत्र के आर-पार आवेश केवल चक्कर लगा सकता है; क्षेत्र के साथ-साथ वह फिसलता है। चित्र को घुमाने के लिए खींचिए।</p>
  <div class="ctl"><label for="tk-b">क्षेत्र B (टेस्ला)</label><input id="tk-b" type="range" data-bind="B" min="1" max="12" step="0.1" value="5"><output data-show="B" data-fmt="1"></output></div>
  <div class="btns tk-sp"><button class="btn ghost" data-act="spd" aria-pressed="true">ड्यूटेरॉन</button> <button class="btn ghost" data-act="spa" aria-pressed="false">अल्फा</button> <button class="btn ghost" data-act="spe" aria-pressed="false">इलेक्ट्रॉन</button></div>
  <div class="formula">ρ = √(2mE) / (|q| B)</div>
</div>
<div class="step">
  <h3>टोरॉइडी क्षेत्र रेखाएं और सुरक्षा गुणांक</h3>
  <p>सीधे क्षेत्र के सिरे खुले होते हैं, इसलिए उसे मोड़कर छल्ला बनाइए और ऐंठ दीजिए: यही टोकामैक है। हर चक्कर वहां एक बिंदु छोड़ता है जहां रेखा काट को पार करती है।</p>
  <div class="ctl"><label for="tk-q">सुरक्षा गुणांक q</label><input id="tk-q" type="range" data-bind="q" min="1" max="4" step="0.01" value="2.62" data-instant><output data-show="q" data-fmt="2"></output></div>
  <div class="btns"><button class="btn ghost" data-act="q32">q = 3/2</button> <button class="btn ghost" data-act="q2">q = 2</button> <button class="btn ghost" data-act="qg">q = स्वर्णिम</button></div>
</div>
<div class="step">
  <h3>चुंबकीय द्वीप और क्षेत्र-रेखा अराजकता</h3>
  <p>क्षेत्र की लहरें सतहों को वहां चुंबकीय द्वीपों में फाड़ देती हैं जहां q एक सरल भिन्न है, फिर अराजकता में। क्षेत्र रेखा शुरू करने के लिए क्लिक कीजिए।</p>
  <div class="ctl"><label for="tk-k">विक्षोभ K</label><input id="tk-k" type="range" data-bind="K" min="0" max="6" step="0.05" value="1.5" data-instant><output data-show="K" data-fmt="2"></output></div>
  <div class="formula">ψ′ = ψ − (K/2π) ψ′/(1+ψ′) sin θ<br>θ′ = θ + 2π/q(ψ′) − (K/2π) cos θ/(1+ψ′)²</div>
</div>`,
};
