/* Hindi: halflife (रेडियोधर्मिता और अर्ध-आयु) */
WT.L.ch.halflife = {
  num: "पाठ 1", title: "रेडियोधर्मिता और अर्ध-आयु", short: "अर्ध-आयु",
  lead: "कुछ परमाणु अस्थिर होते हैं: देर-सबेर उनका नाभिक फूटता है, विकिरण छोड़ता है और कुछ और बन जाता है। कोई नहीं बता सकता कि कोई एक नाभिक कब फूटेगा, फिर भी पूरा नमूना ऐसी घड़ी की तरह चलता है जिससे आप अपनी घड़ी मिला सकें।",
  html: `
<div class="step">
  <h3>यादृच्छिक रूप से फूटता नमूना</h3>
  <p>हर चमकती गेंद एक अस्थिर नाभिक है। कोई भी किसी भी क्षण फूट सकता है: विकिरण की एक चमक छोड़कर वह एक शांत, स्थिर परमाणु बन जाता है। किसी एक पर टैप कीजिए ताकि वह फूट जाए।</p>
  <div class="btns"><button class="btn" data-act="refill">नया नमूना</button></div>
</div>
<div class="step">
  <h3>आधा, फिर उसका आधा</h3>
  <p>कोई नहीं बता सकता कि अगला कौन फूटेगा, पर पूरी भीड़ का व्यवहार अनुमान योग्य है: एक <b>अर्ध-आयु</b> के बाद लगभग आधे बचते हैं, दो के बाद एक चौथाई, फिर आठवां हिस्सा। अर्ध-आयु को लंबा या छोटा कीजिए।</p>
  <div class="ctl"><label for="hl-th">अर्ध-आयु (सेकंड)</label><input id="hl-th" type="range" data-bind="Th" data-instant min="1" max="8" step="0.5" value="3"><output data-show="Th" data-fmt="1"></output></div>
  <div class="btns"><button class="btn ghost" data-act="refill">नया नमूना</button></div>
</div>
<div class="step">
  <h3>नाभिकों की कोई स्मृति नहीं होती</h3>
  <p>एक बचे हुए नाभिक पर नजर रखिए। वह पहले ही कितना भी टिक चुका हो, एक और अर्ध-आयु तक टिकने की उसकी संभावना अब भी दो में एक है: नाभिक बूढ़ा नहीं होता।</p>
  <div class="btns"><button class="btn ghost" data-act="tag">दूसरा चुनिए</button><button class="btn ghost" data-act="refill">नया नमूना</button></div>
</div>
<div class="step">
  <h3>वास्तविक अर्ध-आयु</h3>
  <p>वास्तविक समस्थानिकों की अर्ध-आयु दिनों से लेकर अरबों वर्षों तक होती है। इस खिंची हुई समय-रेखा पर हर समस्थानिक अपनी अर्ध-आयु पर एक खड़ी ढलान से गिर जाता है। एक चुनिए और समय को आगे खींचिए।</p>
  <div class="btns"><button class="btn ghost" data-act="iso0" aria-pressed="false">आयोडीन-131</button><button class="btn ghost" data-act="iso1" aria-pressed="true">सीज़ियम-137</button><button class="btn ghost" data-act="iso2" aria-pressed="false">कार्बन-14</button><button class="btn ghost" data-act="iso3" aria-pressed="false">यूरेनियम-238</button></div>
  <div class="ctl"><label for="hl-t1">बीता समय</label><input id="hl-t1" type="range" data-bind="lt" data-instant min="3" max="17.8" step="0.02" value="8.98"><output class="hl-tout"></output></div>
</div>
<div class="step">
  <h3>सक्रियता: प्रति सेकंड क्षय</h3>
  <p>हर एक का एक ग्राम, अगल-बगल। छोटी अर्ध-आयु का मतलब है हर सेकंड बहुत से क्षय, पर ज्यादा देर तक नहीं; लंबी अर्ध-आयु वाला नमूना युगों तक मंद चमकता है। समय खींचिए और लैंपों को एक-एक करके बुझते देखिए।</p>
  <div class="ctl"><label for="hl-t2">बीता समय</label><input id="hl-t2" type="range" data-bind="lt" data-instant min="3" max="17.8" step="0.02" value="4.94"><output class="hl-tout"></output></div>
</div>`,
};
Object.assign(WT.L.labels, {
  "survived {#} half-lives": "{#} अर्ध-आयु तक बचा",
  "chance to last one more: {#} in {#}": "एक और तक टिकने की संभावना: {#}/{#}",
  "survived {#} half-lives · still {#} in {#}": "{#} अर्ध-आयु तक बचा · अब भी {#}/{#}",
  "it popped: follow another": "यह फूट गया: दूसरे पर नजर रखिए",
  "{#} of {#} still unstable": "अब भी अस्थिर: {#} / {#}",
  "{#} half-life": "{#} अर्ध-आयु",
  "half-lives →": "अर्ध-आयु →",
  "nuclei left": "बचे नाभिक",
  "{#} of {#} left · half-life {#} s": "बचे: {#} / {#} · अर्ध-आयु {#} s",
  "every survivor has the same 1-in-2 chance per half-life": "हर बचे नाभिक की प्रति अर्ध-आयु वही संभावना: 2 में 1",
  "illustrative half-life": "चित्रण हेतु अर्ध-आयु",
  "{#} hour": "{#} घंटा", "{#} h": "{#} घंटे",
  "{#} day": "{#} दिन", "{#} d": "{#} दिन",
  "{#} year": "{#} वर्ष", "{#} yr": "{#} वर्ष",
  "{#} years": "{#} वर्ष",
  "{#}³ yr": "{#}³ वर्ष", "{#}⁶ yr": "{#}⁶ वर्ष", "{#}⁹ yr": "{#}⁹ वर्ष",
  "{#} million years": "{#} मिलियन वर्ष",
  "{#} billion years": "{#} अरब वर्ष",
  "drag": "खींचिए",
  "iodine{#} · half-life {#} days": "आयोडीन{#} · अर्ध-आयु {#} दिन",
  "caesium{#} · half-life {#} years": "सीज़ियम{#} · अर्ध-आयु {#} वर्ष",
  "carbon{#} · half-life {#} years": "कार्बन{#} · अर्ध-आयु {#} वर्ष",
  "uranium{#} · half-life {#} billion years": "यूरेनियम{#} · अर्ध-आयु {#} अरब वर्ष",
  "medicine, fission product": "चिकित्सा, विखंडन उत्पाद",
  "fission product": "विखंडन उत्पाद",
  "radiocarbon dating": "रेडियोकार्बन काल-निर्धारण",
  "natural uranium": "प्राकृतिक यूरेनियम",
  "I{#}": "I{#}", "Cs{#}": "Cs{#}", "C{#}": "C{#}", "U{#}": "U{#}",
  "iodine{#}": "आयोडीन{#}", "caesium{#}": "सीज़ियम{#}", "carbon{#}": "कार्बन{#}", "uranium{#}": "यूरेनियम{#}",
  "all": "सभी",
  "½ {#} days": "½ {#} दिन", "½ {#} years": "½ {#} वर्ष",
  "½ {#} billion years": "½ {#} अरब वर्ष", "½ {#} bn years": "½ {#} अरब वर्ष",
  "~{#} /s": "~{#} /s", "almost none": "लगभग शून्य",
  "{#} /s": "{#} /s", "under {#} /s": "{#} /s से कम",
  "pops per second (log)": "प्रति सेकंड क्षय (लॉग)",
  "pops per second, {#} gram (each line ×{#})": "प्रति सेकंड क्षय, {#} ग्राम (हर रेखा ×{#})",
});
(function () {
  const L = {};
  const U = { minutes: "मिनट", hours: "घंटे", days: "दिन", months: "महीने", years: "वर्ष",
    "thousand years": "हजार वर्ष", "million years": "मिलियन वर्ष", "billion years": "अरब वर्ष" };
  for (const en in U) {
    L[`{#} % left after {#} ${en}`] = `{#} % बचे, {#} ${U[en]} बाद`;
    L[`under {#} % left after {#} ${en}`] = `{#} % से कम बचे, {#} ${U[en]} बाद`;
    L[`one gram of each, after {#} ${en}`] = `हर एक का एक ग्राम, {#} ${U[en]} बाद`;
  }
  for (const e of ["³", "⁴", "⁵", "⁶", "⁷", "⁸", "⁹", "¹⁰", "¹¹", "¹²", "¹³", "¹⁴", "¹⁵", "¹⁶"]) L[`{#}×{#}${e} /s`] = `{#}×{#}${e} /s`;
  Object.assign(WT.L.labels, L);
})();
