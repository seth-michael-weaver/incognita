/* Hindi: chains (क्षय श्रृंखलाएं और साम्यावस्था) */
WT.L.ch.chains = {
  num: "पाठ 1", title: "क्षय श्रृंखलाएं और साम्यावस्था", short: "क्षय श्रृंखलाएं",
  html: `
<div class="step">
  <h3>जनक, संतति, पौत्र</h3>
  <p>अक्सर नया नाभिक भी अस्थिर होता है। जनक क्षय होकर संतति बनता है, जो आगे क्षय होकर एक स्थिर पौत्र नाभिक बनती है। संतति नाभिक पहले जमा होते हैं, फिर घटते हैं; वे कितने जमा होते हैं, यह इस पर निर्भर है कि वे जनक की तुलना में कितनी जल्दी क्षय होते हैं।</p>
  <div class="ctl"><label for="ch-t2">संतति की अर्ध-आयु (s)</label><input id="ch-t2" type="range" data-bind="T2" data-instant min="0.5" max="9" step="0.5" value="1.5"><output data-show="T2" data-fmt="1"></output></div>
  <div class="btns"><button class="btn ghost" data-act="refill">नया नमूना</button></div>
</div>
<div class="step">
  <h3>दीर्घकालिक साम्यावस्था: रेडियम और रेडॉन</h3>
  <p>रेडियम-226 1600 वर्ष टिकता है; उसकी संतति, रेडॉन-222 गैस, केवल 3.8 दिन। एक बंद जार में रेडॉन तब तक जमा होती है जब तक वह उतनी ही तेजी से क्षय न होने लगे जितनी तेजी से बनती है: <i>A</i><sub>Rn</sub> = <i>A</i><sub>Ra</sub>(1 − e<sup>−λt</sup>), जहां λ रेडॉन की क्षय दर है। कुछ सप्ताह बाद दोनों एक ही दर से क्षय होते हैं।</p>
  <div class="btns"><button class="btn" data-act="vent">जार खोलिए</button></div>
</div>
<div class="step">
  <h3>क्षणिक साम्यावस्था: टेक्नीशियम गाय</h3>
  <p>अस्पतालों को मोलिब्डेनम-99 (66 घंटे) का एक स्तंभ मिलता है जो लगातार टेक्नीशियम-99m (6 घंटे) बनाता रहता है, जो सबसे अधिक प्रयुक्त चिकित्सा अनुरेखक है। हर सुबह टेक्नीशियम को धोकर निकालिए और वह फिर बढ़ आता है, धीरे-धीरे घटते मोलिब्डेनम के साथ-साथ।</p>
  <div class="btns"><button class="btn" data-act="milk">जनरेटर को दुहिए</button><button class="btn ghost" data-act="genre">नया जनरेटर</button></div>
</div>
<div class="step">
  <h3>यूरेनियम श्रृंखला में नीचे</h3>
  <p>यूरेनियम-238 को स्थिर सीसा बनने में चौदह चरण लगते हैं। इस चार्ट पर अल्फा क्षय दो खाने नीचे और दो बाएं ले जाता है, बीटा क्षय एक ऊपर और एक बाएं। पुराने, अछूते यूरेनियम अयस्क में हर सदस्य एक ही दर से क्षय होता है।</p>
  <div class="btns"><button class="btn" data-act="next">अगला क्षय</button><button class="btn ghost" data-act="restart">फिर से शुरू</button></div>
</div>`,
};
Object.assign(WT.L.labels, {
  "parent {#}": "जनक {#}",
  "daughter {#}": "संतति {#}",
  "stable {#}": "स्थिर {#}",
  "parent ({#} s): {#}": "जनक ({#} s): {#}",
  "daughter ({#} s): {#}": "संतति ({#} s): {#}",
  "granddaughter (stable): {#}": "पौत्र (स्थिर): {#}",
  "daughter peaks: {#} %": "संतति का शिखर: {#} %",
  "{#} s": "{#} s",
  "illustrative half-lives": "चित्रण हेतु अर्ध-आयु",
  "radium{#}": "रेडियम{#}",
  "radon{#} gas": "रेडॉन{#} गैस",
  "radium": "रेडियम",
  "radium activity": "रेडियम सक्रियता",
  "{#} d": "{#} दिन",
  "days →": "दिन →",
  "radon": "रेडॉन",
  "radon activity": "रेडॉन सक्रियता",
  "day {#}: radon at {#} % of radium": "दिन {#}: रेडॉन, रेडियम का {#} %",
  "A(Rn) = A(Ra) × ({#} − exp(−λt))": "A(Rn) = A(Ra) × ({#} − exp(−λt))",
  "A(radon) = A(radium) × ({#} − exp(−λt))": "A(रेडॉन) = A(रेडियम) × ({#} − exp(−λt))",
  "Mo{#}": "Mo{#}",
  "Tc{#}m out": "Tc{#}m बाहर",
  "Tc{#}m to the patient": "Tc{#}m रोगी तक",
  "molybdenum{#}": "मोलिब्डेनम{#}",
  "dashed: never milked": "टूटी रेखा: कभी नहीं दुहा",
  "activity": "सक्रियता",
  "{#} h since last milking · Tc{#}m at {#} % of Mo{#}": "पिछली बार दुहने के {#} घंटे बाद · Tc{#}m: {#} % (Mo{#} के सापेक्ष)",
  "regrows to its peak in about {#} hours": "लगभग {#} घंटे में फिर शिखर तक बढ़ता है",
  "Pb": "Pb", "Bi": "Bi", "Po": "Po", "At": "At", "Rn": "Rn", "Fr": "Fr", "Ra": "Ra", "Ac": "Ac", "Th": "Th", "Pa": "Pa", "U": "U",
  "neutrons →": "न्यूट्रॉन →",
  "grey: stable": "धूसर: स्थिर",
  "protons ↑": "प्रोटॉन ↑",
  "alpha: {#} p, {#} n": "अल्फा: {#} p, {#} n",
  "alpha: loses {#} protons and {#} neutrons": "अल्फा: {#} प्रोटॉन और {#} न्यूट्रॉन खोता है",
  "beta: n → p": "बीटा: n → p",
  "beta: a neutron becomes a proton": "बीटा: एक न्यूट्रॉन प्रोटॉन बन जाता है",
  "U{#} · half-life {#} billion yr · alpha next": "U{#} · अर्ध-आयु {#} अरब वर्ष · आगे अल्फा",
  "Th{#} · half-life {#} days · beta next": "Th{#} · अर्ध-आयु {#} दिन · आगे बीटा",
  "Pa{#}m · half-life {#} min · beta next": "Pa{#}m · अर्ध-आयु {#} मिनट · आगे बीटा",
  "U{#} · half-life {#} yr · alpha next": "U{#} · अर्ध-आयु {#} वर्ष · आगे अल्फा",
  "Th{#} · half-life {#} yr · alpha next": "Th{#} · अर्ध-आयु {#} वर्ष · आगे अल्फा",
  "Ra{#} · half-life {#} yr · alpha next": "Ra{#} · अर्ध-आयु {#} वर्ष · आगे अल्फा",
  "Rn{#} · half-life {#} days · alpha next": "Rn{#} · अर्ध-आयु {#} दिन · आगे अल्फा",
  "Po{#} · half-life {#} min · alpha next": "Po{#} · अर्ध-आयु {#} मिनट · आगे अल्फा",
  "Pb{#} · half-life {#} min · beta next": "Pb{#} · अर्ध-आयु {#} मिनट · आगे बीटा",
  "Bi{#} · half-life {#} min · beta next": "Bi{#} · अर्ध-आयु {#} मिनट · आगे बीटा",
  "Po{#} · half-life {#} µs · alpha next": "Po{#} · अर्ध-आयु {#} µs · आगे अल्फा",
  "Pb{#} · half-life {#} years · beta next": "Pb{#} · अर्ध-आयु {#} वर्ष · आगे बीटा",
  "Bi{#} · half-life {#} days · beta next": "Bi{#} · अर्ध-आयु {#} दिन · आगे बीटा",
  "Po{#} · half-life {#} days · alpha next": "Po{#} · अर्ध-आयु {#} दिन · आगे अल्फा",
  "Pb{#}: stable, the chain ends": "Pb{#}: स्थिर, श्रृंखला समाप्त",
  "step {#} of {#} · tap the nucleus": "चरण {#} / {#} · नाभिक पर टैप कीजिए",
});
