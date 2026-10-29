/* Hindi: fission (अध्याय 12, विखंडन) */
WT.L.ch.fission = {
  num: "अध्याय 12", title: "विखंडन", short: "विखंडन",
  lead: "सबसे भारी नाभिकों के पास एक ऐसा निकास है जो हल्के नाभिकों के पास नहीं: एक कण बाहर फेंकने के बजाय पूरा नाभिक दो भागों में फट जाता है। यही विखंडन है।",
  html: `
<div class="step">
  <p>एक भारी नाभिक आवेशित द्रव की एक बूंद की तरह व्यवहार करता है। पृष्ठ तनाव (धूसर तीर) उसे गोल खींचता है; प्रोटॉन, जो सभी धनावेशित हैं, उसे अलग धकेलते हैं (लाल तीर)। यूरेनियम के लिए दोनों लगभग संतुलित हैं।</p>
  <div class="ctl"><label for="fis-d">बूंद को खींचें</label><input id="fis-d" type="range" data-bind="def" min="0" max="1" step="0.01" value="0"><output data-show="def" data-fmt="2"></output></div>
  <p>इसे खींचने के लिए स्लाइडर चलाइए और नीचे के छोटे ऊर्जा वक्र पर बिंदु देखिए। खिंचाव सतह बढ़ाता है, जिसमें ऊर्जा लगती है, पर आवेश को फैलाता है, जिससे ऊर्जा मुक्त होती है। वक्र के शीर्ष के पार आवेश जीतता है: एक ग्रीवा (neck) बनती है और दोनों आधे लगभग 200 MeV के साथ अलग उड़ जाते हैं।</p>
</div>
<div class="step">
  <h3>स्थितिज-ऊर्जा सतह</h3>
  <p>वक्र हर आकृति की ऊर्जा है, गोल (बाएं) से टूटे हुए (दाएं) तक। एक चिकनी द्रव बूंद एक पहाड़ी देती है, पर न्यूक्लिऑन ऊर्जा स्तरों को समूहों में भरते हैं, जिन्हें <b>कोश</b> (shells) कहते हैं, और सबसे भारी तत्वों में यह उसमें एक कूप खोद देता है: एक <b>दोहरे कूबड़ वाला अवरोध</b>, जहाँ नाभिक एक खिंची हुई आकृति में ठहर सकता है।</p>
  <p>इंजन यह वक्र मानकर नहीं चलता: वह इसे हर विरूपण (खिंचाव की मात्रा) पर ऊर्जा की एक सूक्ष्म गणना से बिंदु-दर-बिंदु पढ़ता है।</p>
</div>
<div class="step">
  <h3>अवरोध भेदन</h3>
  <p>गेंद पहली घाटी में उत्तेजित नाभिक है, नारंगी धराशायी रेखा की उत्तेजन ऊर्जा पर, 6 MeV की चोटी से नीचे। शास्त्रीय रूप से यह कभी पार नहीं कर सकता; क्वांटम यांत्रिकी इसे गहरे, वर्जित भाग से <b>सुरंगन</b> करने देती है, एक संभावना <i>T</i> के साथ जो उस भाग के मोटा होने पर चरघातांकी रूप से घटती है।</p>
  <div class="ctl"><label for="fis-e">उत्तेजन ऊर्जा</label><input id="fis-e" type="range" data-bind="E" min="3" max="8" step="0.05" value="5"><output data-show="E" data-fmt="2"></output></div>
  <p>ऊर्जा बढ़ाइए और वर्जित भाग के पतले होने के साथ <i>T</i> को चढ़ते देखिए। पाठ्यपुस्तक का शॉर्टकट (हिल–व्हीलर) चोटी को एक परवलय (नीली धराशायी) मानता है। इंजन वास्तविक आकृति का पालन करता है, जो नीचे की ओर अधिक चौड़ी है, इसलिए चोटी से बहुत नीचे इसकी संभावना कम होती है। <i>K</i> मापता है कि रास्ते में कितनी पहाड़ी है।</p>
  <div class="formula">T = 1 / (1 + e<sup>2K</sup>),  K = ∫ √(2μ(V−E)) dβ / ħ</div>
</div>
<div class="step">
  <h3>संक्रमण अवस्थाएं</h3>
  <p>चोटी पर के दरवाजे <b>संक्रमण अवस्थाएं</b> हैं, यानी अवरोध के ऊपर फैले नाभिक की क्वांटम अवस्थाएं। हर एक का एक प्रचक्रण और समता (0⁺, 2⁻, …) है और वह एक फाटक की तरह काम करती है; उसका प्रकाशित अंतराल दिखाता है कि वह कितनी खुली है। नाभिक केवल उन्हीं फाटकों से गुजरता है जो उसके अपने प्रचक्रण और समता से मेल खाते हों, और हर फाटक ऊर्जा के उसकी ऊंचाई पार करने पर धीरे-धीरे खुलता है।</p>
  <div class="ctl"><label for="fis-e2">उत्तेजन ऊर्जा</label><input id="fis-e2" type="range" data-bind="E" min="3" max="8" step="0.05" value="5"><output data-show="E" data-fmt="2"></output></div>
  <div class="btns"><button class="btn ghost" data-act="jpAll">कोई भी प्रचक्रण</button><button class="btn ghost" data-act="jp0">यौगिक 0⁺</button><button class="btn ghost" data-act="jp1">यौगिक 1⁻</button></div>
  <p>एक प्रचक्रण और समता चुनिए: केवल मेल खाते फाटक गिने जाते हैं, और कुल खुलाव घट जाता है। और ऊपर, फाटक एक <b>सातत्य</b> में घिर आते हैं, और इंजन उन्हें उनके घनत्व से गिनता है, जैसे साधारण स्तरों के लिए करता है।</p>
</div>
<div class="step">
  <h3>दोहरे कूबड़ वाले अवरोध</h3>
  <p>अब दोनों पहाड़ियां, हर एक पर एक फाटक (वृत्त; उसका भरा भाग दिखाता है कि वह कितना खुला है)। नाभिक बाईं ओर से आते हैं; जो पहली पहाड़ी पार करते हैं वे कूप में फंस जाते हैं, फाटकों के बीच उछलते रहते हैं जब तक किसी एक ओर से निकल न जाएं। संभावनाएं श्रेणी में जुड़े प्रतिरोधों की तरह मिलती हैं, इसलिए कठिन पहाड़ी ही अधिकतर निर्णय करती है।</p>
  <div class="ctl"><label for="fis-b">बाहरी पहाड़ी की ऊंचाई</label><input id="fis-b" type="range" data-bind="Bb" min="3.5" max="7.5" step="0.05" value="5.6"><output data-show="Bb" data-fmt="2"></output></div>
  <div class="formula">1/T = 1/T<sub>A</sub> + 1/T<sub>B</sub></div>
  <p>बाहरी पहाड़ी ऊंची कीजिए और विखंडन की ओर प्रवाह को घुटते देखिए, भीतरी फाटक चाहे कितना भी खुला हो।</p>
</div>
<div class="step">
  <h3>बहु-अवसर विखंडन</h3>
  <p>यूरेनियम-238 न्यूट्रॉन अवशोषित करके उत्तेजन <i>E</i>* (धराशायी रेखा) के साथ यूरेनियम-239 बन जाता है। यदि यह नहीं टूटता, तो इसके बजाय एक न्यूट्रॉन उत्सर्जित कर सकता है; रेखा नीचे गिरती है, और पीछे छूटा यूरेनियम-238, अभी भी गर्म, अपने अवरोध को आजमाता है: <b>द्वितीय-अवसर विखंडन</b>, (n,n′f)। ढेर इकट्ठा करते हैं कि हर नाभिक का अंत कैसे हुआ।</p>
  <div class="ctl"><label for="fis-en">न्यूट्रॉन ऊर्जा</label><input id="fis-en" type="range" data-bind="En" min="0" max="25" step="0.1" value="7"><output data-show="En" data-fmt="1"></output></div>
  <p>ऊर्जा बढ़ाइए और बाद के प्रयास सफल होने लगते हैं; लगभग 12 MeV पर तीसरा अवसर खुलता है। हर नया अवसर मापे गए <b>विखंडन अनुप्रस्थ काट</b> में एक सीढ़ी के रूप में दिखता है, यानी नाभिक के टूटने की संभावना: ऊपर दाईं ओर का छोटा ग्राफ उन सीढ़ियों को आपकी ऊर्जा के चिह्न के साथ खींचता है। इंजन यह गणना करता है कि यह कितनी बार टूटता है, न कि यह किन टुकड़ों में टूटता है।</p>
  <div class="aside">कोड में: <code>fission/wkb.py</code> (विरूपण-ऊर्जा पथ और WKB समाकल), <code>fission/barriers.py</code> (हिल–व्हीलर, संक्रमण अवस्थाएं, अवरोध का स्तर घनत्व), <code>fission/transmission.py</code> (श्रेणी में कूबड़, हर प्रचक्रण और समता के लिए T<sub>fis</sub>), <code>fission/chain.py</code> (कैस्केड के हर नाभिक के लिए अवरोध)।</div>
</div>
`,
};
Object.assign(WT.L.labels, {
  // drop
  "surface tension pulls it round": "पृष्ठ तनाव इसे गोल खींचता है",
  "the protons push it apart": "प्रोटॉन इसे अलग धकेलते हैं",
  "a charged drop, nearly round": "आवेशित बूंद, लगभग गोल",
  "stretched: more surface, charge further apart": "खिंची: अधिक सतह, आवेश अधिक दूर",
  "a neck forms": "ग्रीवा बनती है",
  "two fragments, carrying about {#} MeV": "दो खंड, लगभग {#} MeV के साथ",
  "energy of the drop": "बूंद की ऊर्जा",
  // landscape
  "ground state": "मूल अवस्था", "inner barrier": "भीतरी अवरोध", "second well": "दूसरा कूप",
  "outer barrier": "बाहरी अवरोध", "split (scission)": "टूटना (विच्छेदन)", "one smooth hill": "एक चिकनी पहाड़ी",
  "shell effects carving the second well": "कोश प्रभाव दूसरा कूप खोदते हैं",
  "round → stretched → necked → split": "गोल → खिंचा → ग्रीवा → टूटा",
  "stretch (deformation) →": "खिंचाव (विरूपण) →",
  // tunnel
  "forbidden zone": "वर्जित क्षेत्र",
  "excitation {#} MeV": "उत्तेजन {#} MeV",
  "hilltop {#} MeV": "चोटी {#} MeV",
  "parabola fit": "परवलय फिट",
  "passes over the top": "चोटी के ऊपर से पार",
  // gates
  "continuum: a density": "सातत्य: एक घनत्व",
  "continuum of gates: counted as a density": "फाटकों का सातत्य: घनत्व के रूप में गिना",
  "gates: transition states": "फाटक: संक्रमण अवस्थाएं",
  "E = {#} MeV": "E = {#} MeV",
  "all gates: total opening {#}": "सभी फाटक: कुल खुलाव {#}",
  "all gates: total opening {#} + {#} from the continuum": "सभी फाटक: कुल खुलाव {#} + सातत्य से {#}",
  "{#}⁺ gates only: total opening {#}": "केवल {#}⁺ फाटक: कुल खुलाव {#}",
  "{#}⁺ gates only: total opening {#} + {#} from the continuum": "केवल {#}⁺ फाटक: कुल खुलाव {#} + सातत्य से {#}",
  "{#}⁻ gates only: total opening {#}": "केवल {#}⁻ फाटक: कुल खुलाव {#}",
  "{#}⁻ gates only: total opening {#} + {#} from the continuum": "केवल {#}⁻ फाटक: कुल खुलाव {#} + सातत्य से {#}",
  // series
  "nuclei arriving →": "आते हुए नाभिक →",
  "trapped in the well": "कूप में फंसे",
  "fission": "विखंडन",
  "so far: {#} through, {#} turned back": "अब तक: {#} पार, {#} लौटे",
  // chance
  "²³⁹U*  E* = {#} MeV": "²³⁹U*  E* = {#} MeV", "²³⁸U*  E* = {#} MeV": "²³⁸U*  E* = {#} MeV", "²³⁷U*  E* = {#} MeV": "²³⁷U*  E* = {#} MeV",
  "↑ E* above the picture": "↑ E* चित्र से ऊपर",
  "fission!": "विखंडन!",
  "emits a neutron, cools, tries again": "न्यूट्रॉन छोड़ता, ठंडा होता, फिर कोशिश",
  "too cool to split: a photon, no fission": "टूटने के लिए बहुत ठंडा: फोटॉन, विखंडन नहीं",
  "attempt {#}: barrier {#} % open": "प्रयास {#}: अवरोध {#} % खुला",
  "{#}st chance (n,f)": "अवसर {#} (n,f)", "{#}nd chance (n,n′f)": "अवसर {#} (n,n′f)", "{#}rd chance (n,{#}nf)": "अवसर {#} (n,{#}nf)",
  "{#}st (n,f)": "#{#} (n,f)", "{#}nd (n,n′f)": "#{#} (n,n′f)", "{#}rd (n,{#}nf)": "#{#} (n,{#}nf)",
  "no fission": "विखंडन नहीं",
});
// labels carrying a transmission T, printed either as 0.12 or as 3.4·10⁻5 (two number shapes)
(function () {
  const L = WT.L.labels, F = ["{#}", "{#}·{#}⁻{#}"];
  for (const a of F) {
    L[`inner gate T ≈ ${a}`] = `भीतरी फाटक T ≈ ${a}`;
    L[`outer gate T ≈ ${a}`] = `बाहरी फाटक T ≈ ${a}`;
    L[`both hills: T ≈ ${a}, {#} % of what arrives gets through`] = `दोनों पहाड़ियां: T ≈ ${a}, आने वालों का {#} % पार`;
    for (const b of F) {
      L[`T ≈ ${a} real shape · ${b} parabola`] = `T ≈ ${a} वास्तविक आकृति · ${b} परवलय`;
      L[`chance to tunnel T ≈ ${a} on the real shape, ${b} on the parabola`] = `सुरंगन संभावना T ≈ ${a} वास्तविक आकृति पर, ${b} परवलय पर`;
    }
  }
})();

// canvas labels added 2026-10-29 (I18NLABELS_B)
Object.assign(WT.L.labels, {
  "chance to split vs neutron energy": "न्यूट्रॉन ऊर्जा के साथ विखंडन की संभावना",
  "{#}nd": "#{#}",
  "{#}rd": "#{#}",
});
