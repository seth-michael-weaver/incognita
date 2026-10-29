/* Hindi: critical (अध्याय 21, क्रांतिकता और रिएक्टर नियंत्रण) */
WT.L.ch.critical = {
  num: "अध्याय 21", title: "क्रांतिकता और रिएक्टर नियंत्रण", short: "क्रांतिकता",
  html: `
<div class="step">
  <h3>गुणन गुणांक</h3>
  <p>हर विखंडन कुछ न्यूट्रॉन मुक्त करता है; कुछ अगले विखंडन कराते हैं, बाकी खो जाते हैं। <b>गुणन गुणांक</b> <i>k</i> यह है कि एक विखंडन से कितने नए विखंडन होते हैं: हर पीढ़ी न्यूट्रॉनों को <i>k</i> से गुणा करती है। 1 से ऊपर श्रृंखला बढ़ती है, 1 से नीचे मंद पड़ जाती है।</p>
  <div class="ctl"><label for="cri-k">गुणन k</label><input id="cri-k" type="range" data-bind="k" data-instant min="0.95" max="1.05" step="0.05" value="1.05"><output data-show="k" data-fmt="2"></output></div>
</div>
<div class="step">
  <h3>विलंबित न्यूट्रॉन</h3>
  <p>न्यूट्रॉनों का एक छोटा अंश (0.65 %) सेकंडों देर से आता है, उन विखंडन टुकड़ों से जो पहले क्षय होते हैं। वही देर से आने वाले गति तय करते हैं, इसलिए वृद्धि पलक झपकने से मिनटों तक धीमी हो जाती है। आलेख ×10 गति से चलता है।</p>
  <div class="ctl"><label for="cri-k2">गुणन k</label><input id="cri-k2" type="range" data-bind="kd" data-instant min="0.998" max="1.002" step="0.0005" value="1.001"><output data-show="kd" data-fmt="4"></output></div>
  <div class="btns"><button class="btn ghost" data-act="delayed" aria-pressed="true">विलंबित न्यूट्रॉन</button></div>
</div>
<div class="step">
  <h3>क्रांतिकता</h3>
  <p>एक क्रांतिक प्रयोग: नियंत्रण छड़ों को तब तक हिलाइए जब तक शक्ति स्थिर न रहे। उस सेटिंग पर <i>k</i> ठीक 1 होता है, और छड़ की वह स्थिति ही मापन है। उसे ढूंढिए: पाठ्यांक <i>k</i> को पांच दशमलव स्थानों तक दिखाता है।</p>
  <div class="ctl"><label for="cri-rod">नियंत्रण छड़ें भीतर (%)</label><input id="cri-rod" type="range" data-bind="ins" data-instant min="35" max="75" step="1" value="45"><output data-show="ins" data-fmt="0"></output></div>
</div>`,
};
/* attributes referenced in the English chapter script (for the structure check): data-act="delayed" data-act="delayed" */
