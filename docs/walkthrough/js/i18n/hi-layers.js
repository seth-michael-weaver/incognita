/* Hindi: layers (अध्याय 21). The scoreboard counts come from WT.board (js/scoreboard-data.js, loaded first), as in
 * js/ch/layers.js; a missing block or field drops the number, not the sentence. */
(function () {
  const B = WT.board || {};
  const nOf = (v) => (typeof v === "number" && isFinite(v) ? v : null);
  const tally = (o) => {
    if (!o) return null;
    const w = nOf(o.WIN), t = nOf(o.TIE), l = nOf(o.LOSS);
    if (w === null || t === null || l === null) return null;
    return { w, t, l, d: nOf(o.decided) ?? w + t + l };
  };
  const TE = tally(B.incognita), TT = tally(B.terra);
  const LIBS = B.terra && Array.isArray(B.terra.by_rival) ? B.terra.by_rival.map((r) => r && r.rival).filter((s) => typeof s === "string") : [];
  const ASOF = (() => {
    const m = /^(\d{4})-(\d{2})-(\d{2})$/.exec(B.asof || ""); if (!m) return null;
    const mah = ["जनवरी", "फरवरी", "मार्च", "अप्रैल", "मई", "जून", "जुलाई", "अगस्त", "सितंबर", "अक्टूबर", "नवंबर", "दिसंबर"][+m[2] - 1];
    return mah ? `${+m[3]} ${mah} ${m[1]}` : null;
  })();
  const figs = (T) => (T ? `<div class="figs" aria-label="${T.w} जीत, ${T.t} बराबरी, ${T.l} हार"><div class="w"><b>${T.w}</b><span>जीत</span></div><div><b>${T.t}</b><span>बराबरी</span></div><div class="l"><b>${T.l}</b><span>हार</span></div></div>` : "");
  const libs = LIBS.length ? `प्रमुख मूल्यांकित डेटा लाइब्रेरियों (${LIBS.join(", ")})` : "प्रमुख मूल्यांकित डेटा लाइब्रेरियों";
  const engineScore = TE ? ` ऐसी ${TE.d} तुलनाओं में से यह ${TE.w} में स्पष्ट रूप से आगे है, ${TE.t} में बराबर है और ${TE.l} में पीछे है।` : "";
  const terraScore = TT ? `${libs} के विरुद्ध यह ${TT.d} तुलनाओं में से ${TT.w} में आगे है, ${TT.t} में बराबर है और ${TT.l} में पीछे है।` : `इसकी तुलना ${libs} से की जाती है।`;

  WT.L.ch.layers = {
    num: "अध्याय 21", title: "मॉडल की परतें कैसे बनी हैं", short: "परतें",
    lead: "हम जो देते हैं, वह इंजन के ऊपर परतों में बना है, और हर परत को मापनों के विरुद्ध अपनी जगह कमानी होती है।",
    html: `
<div class="step">
  <div class="layer-chip on">उपयोग में</div>
  <h3>परत 1 · हर नाभिक के लिए एक नियम</h3>
  <p>नीली रेखा एक अभिक्रिया के लिए इंजन का पूर्वानुमान है। इंजन सबसे निचली परत है: हर न्यूक्लाइड के लिए वही भौतिकी और वही वैश्विक सेटिंग्स, और इसमें कुछ भी किसी एक नाभिक के अनुप्रस्थ काट पर फिट नहीं किया गया है।</p>
  <div class="btns"><button class="btn ghost" data-act="reveal" aria-pressed="false">मापन दिखाएं</button></div>
  <p>इससे यह मापनों के विरुद्ध और उन्हीं नाभिकों पर चलाए गए अन्य मॉडल कोडों के विरुद्ध परखने योग्य बनता है। यह अंधा परीक्षण नहीं है: वैश्विक सेटिंग्स इन्हीं तुलनाओं को देखते हुए चुनी गई थीं।${engineScore}</p>
  ${figs(TE)}
</div>
<div class="step">
  <div class="layer-chip null">परखी गई: अभी लाभ नहीं</div>
  <h3>परत 2 · हर नाभिक के अपने मापन</h3>
  <p>यह परत वैश्विक नियम की जगह हर नाभिक के अपने मापे गए मान रखती है: उसका स्तर अंतराल D0, उसके सामर्थ्य फलन S0 और S1 (वह धीमे न्यूट्रॉनों को कितनी आसानी से अवशोषित करता है), उसकी औसत गामा चौड़ाई ⟨Γγ⟩ और उसके ज्ञात ऊर्जा स्तर।</p>
  <div class="btns"><button class="btn ghost" data-act="ms0" aria-pressed="true">वैश्विक नियम</button><button class="btn ghost" data-act="ms1" aria-pressed="false">अपने मापन</button></div>
  <p>इसे चालू कीजिए और रेखा मुश्किल से हिलती है। अब तक के परीक्षणों में कोई समग्र लाभ नहीं मिला: जो एक रूपांतर देहली के पास की अभिक्रिया में मदद करता है, वह न्यूट्रॉन प्रग्रहण को खराब कर देता है। इसलिए यह परत अभी बंद रहती है।</p>
</div>
<div class="step">
  <div class="layer-chip cand">उम्मीदवार</div>
  <h3>परत 3 · अच्छे डेटा का अनुसरण (TERRA)</h3>
  <p>जहाँ किसी अभिक्रिया का अच्छा मापन हुआ है, वहाँ रेखा को मापनों का अनुसरण करना चाहिए। तीसरी परत, TERRA, जहाँ अच्छा डेटा है वहाँ इंजन की रेखा उससे होकर खींचती है, और जहाँ नहीं है वहाँ इंजन पर लौट आती है।</p>
  <div class="ctl"><label for="lay-cov">मापी गई ऊर्जा परास का हिस्सा (%)</label><input id="lay-cov" type="range" data-bind="cov" min="0" max="1" step="0.01" value="0.45"><output data-show="covPct" data-fmt="0"></output></div>
  <p>${terraScore} इनमें से अधिकांश इन-सैंपल हैं: TERRA ने वे मापन देखे हैं, जैसे लाइब्रेरियों ने भी।</p>
  ${figs(TT)}
</div>
<div class="step">
  <div class="layer-chip wip">काम जारी</div>
  <h3>परत 4 · ईमानदार त्रुटि पट्टियां</h3>
  <p>सबसे ऊपरी परत रेखा के चारों ओर एक बैंड रखती है जिसमें सच्चा मान लगभग तीन में से दो बार होना चाहिए (68 % बैंड): जहाँ अच्छा डेटा उसे पक्का करता है वहाँ संकरा, जहाँ नहीं वहाँ चौड़ा।</p>
  <div class="ctl"><label for="lay-band">बैंड की चौड़ाई · भीतर के मापन (%)</label><input id="lay-band" type="range" data-bind="band" min="0.2" max="2.5" step="0.05" value="1"><output data-show="inside" data-fmt="0"></output></div>
  <p>इसे खींचिए और भीतर के मापन गिनिए। बहुत संकरा, तो बैंड ऐसी परिशुद्धता का दावा करता है जो उसके पास नहीं; बहुत चौड़ा, तो वह कुछ नहीं कहता। इंजन का अपना बैंड अभी अपनाया नहीं गया है: सभी अभिक्रियाओं को मिलाने पर यह लक्ष्य पर है, पर अभी हर अभिक्रिया परिवार में नहीं। TERRA के अपने बैंड हैं, और वे ऊपर की उसकी तुलनाओं का हिस्सा हैं।</p>
</div>
<div class="step">
  <h3>वर्तमान स्थिति</h3>
  <p>कोई परत मापनों के विरुद्ध परखे जाने के बाद ही अपनाई जाती है, और मदद न करे तो बंद रहती है। आज इंजन उपयोग में है और TERRA उम्मीदवार है; मापी-गई-संरचना परत और इंजन का अनिश्चितता बैंड अभी परखे जा रहे हैं।</p>
  <p><a href="scoreboard.html" data-keep-lang>पूरा स्कोरबोर्ड देखें →</a> हर वह तुलना जो हम नहीं जीतते, हर प्रतिद्वंद्वी, और उसे कैसे पढ़ें।</p>
  <div class="aside">${ASOF ? `${ASOF} तक के अंक, परियोजना के` : "अंक परियोजना के"} शोध रजिस्टर से। चित्र के वक्र केवल उदाहरण के लिए हैं।</div>
</div>`,
  };
})();
Object.assign(WT.L.labels, {
  "{#} · engine": "{#} · इंजन",
  "{#} · measured structure": "{#} · मापी गई संरचना",
  "{#} · TERRA: anchored to data": "{#} · TERRA: डेटा से जुड़ा",
  "{#} · uncertainty band": "{#} · अनिश्चितता बैंड",
  "measured here": "यहाँ मापा गया",
  "neutron energy →": "न्यूट्रॉन ऊर्जा →",
  "how often the reaction happens": "अभिक्रिया कितनी बार होती है",
  "hollow dots: measurements the engine is compared with": "खोखले बिंदु: वे मापन जिनसे इंजन की तुलना होती है",
  "own measured values: the line barely moves": "अपने मापे गए मान: रेखा मुश्किल से हिलती है",
  "global rule": "वैश्विक नियम",
  "no measurements: TERRA falls back to the engine": "कोई मापन नहीं: TERRA इंजन पर लौटता है",
  "solid: follows the data · dashed: the engine alone": "ठोस: डेटा का अनुसरण · धराशायी: केवल इंजन",
  "{#} of {#} measurements inside the band (aim: about {#} %)": "{#} / {#} मापन बैंड के भीतर (लक्ष्य: लगभग {#} %)",
  "no measurements to check the band against": "बैंड जांचने के लिए कोई मापन नहीं",
});
Object.assign(WT.L.ui, { nav_board: "स्कोरबोर्ड" });
/* attributes referenced in the English chapter script (for the structure check): data-act="${act}" */
