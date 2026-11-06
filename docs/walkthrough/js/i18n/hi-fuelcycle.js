/* Hindi: fuelcycle (ईंधन चक्र) */
WT.L.ch.fuelcycle = {
  num: "पाठ 1", title: "ईंधन चक्र", short: "ईंधन चक्र",
  html: `
<div class="step">
  <h3>यूरेनियम खोदकर निकालना</h3>
  <p>अयस्क ज़्यादातर चट्टान है, और उसमें मौजूद यूरेनियम का केवल 0.7 % यूरेनियम-235 है, वह प्रकार जो आसानी से विखंडित होता है।</p>
  <div class="ctl"><label for="fc-g">अयस्क श्रेणी (% यूरेनियम)</label><input id="fc-g" type="range" data-bind="lg" data-instant min="-1.7" max="1.3" step="0.01" value="-1"></div>
</div>
<div class="step">
  <h3>संवर्धन एक द्रव्यमान संतुलन है</h3>
  <p>गैस के रूप में यूरेनियम को यूरेनियम-235 से समृद्ध एक छोटी धारा, यानी ईंधन, और एक बड़ी क्षीण धारा, यानी टेल्स, में बाँटा जाता है।</p>
  <div class="ctl"><label for="fc-p">ईंधन संवर्धन (% U-235)</label><input id="fc-p" type="range" data-bind="xp" data-instant min="3" max="5" step="0.05" value="4.5"><output data-show="xp" data-fmt="2"></output></div>
  <div class="ctl"><label for="fc-t">टेल्स (% U-235)</label><input id="fc-t" type="range" data-bind="xt" data-instant min="0.15" max="0.35" step="0.01" value="0.25"><output data-show="xt" data-fmt="2"></output></div>
</div>
<div class="step">
  <h3>गोलियाँ, छड़ें, असेंबली</h3>
  <p>संवर्धित यूरेनियम को सिरेमिक गोलियों में पकाया जाता है, छड़ों में सील किया जाता है और असेंबलियों में बाँधा जाता है; <a href="#reactor">अगला पाठ</a> उन्हें कोर तक ले जाता है।</p>
  <div class="ctl"><label for="fc-f">ईंधन (टन यूरेनियम)</label><input id="fc-f" type="range" data-bind="ft" data-instant min="1" max="27" step="1" value="1"><output data-show="ft" data-fmt="0"></output></div>
</div>
<div class="step">
  <h3>कोर में वर्ष</h3>
  <p>तीन से छह वर्षों में कुछ प्रतिशत भारी परमाणु विखंडित होते हैं, जिससे विखंडन उत्पाद और कुछ नया प्लूटोनियम बचता है (<a href="#burnup">बर्नअप</a>)।</p>
  <div class="ctl"><label for="fc-b">बर्नअप (GWd प्रति टन)</label><input id="fc-b" type="range" data-bind="bu" data-instant min="0" max="60" step="1" value="50"><output data-show="bu" data-fmt="0"></output></div>
</div>
<div class="step">
  <h3>ठंडा करना, फिर दो रास्ते</h3>
  <p>प्रयुक्त ईंधन पहले एक कुंड में और फिर शुष्क कास्क में ठंडा होता है; उसके बाद उसे या तो जैसा है वैसा ही गहराई में दफ़नाया जाता है, या पुनर्संसाधित किया जाता है ताकि उसका यूरेनियम और प्लूटोनियम फिर इस्तेमाल हो (<a href="#waste">प्रयुक्त ईंधन</a>, <a href="#breeding">प्रजनन</a>)।</p>
  <div class="btns"><button class="btn ghost" data-act="frO" aria-pressed="true">वन्स-थ्रू</button> <button class="btn ghost" data-act="frR" aria-pressed="false">पुनर्संसाधन</button></div>
</div>`,
};
Object.assign(WT.L.labels, {
  "Convert": "रूपांतरण",
  "Disposal": "निपटान",
  "End": "अंत",
  "Enrich": "संवर्धन",
  "Fabricate": "निर्माण",
  "Mill": "मिलिंग",
  "Mine": "खनन",
  "Pool · cask": "कुंड · कास्क",
  "Reactor": "रिएक्टर",
  "Store": "भंडारण",
  "about what a {#} MWe reactor loads in a year": "लगभग उतना जितना {#} MWe रिएक्टर एक वर्ष में भरता है",
  "assemblies": "असेंबली",
  "assemblies of {#} rods": "{#} छड़ों की असेंबली",
  "at least {#} years": "कम से कम {#} वर्ष",
  "cask": "कास्क",
  "decades": "दशक",
  "decades in air": "हवा में दशकों तक",
  "deep repository, {#}–{#} m down": "गहरा भंडार, {#}–{#} m नीचे",
  "dry cask": "शुष्क कास्क",
  "enrich": "संवर्धन",
  "enrichment plant (UF₆ gas)": "संवर्धन संयंत्र (UF₆ गैस)",
  "fission products": "विखंडन उत्पाद",
  "illustration": "चित्रण",
  "minor actinides": "लघु ऐक्टिनाइड",
  "most mines: above {#} %": "अधिकांश खानें: {#} % से ऊपर",
  "of electricity from this tonne": "इस एक टन से बिजली",
  "once-through: the whole tonne is disposed of": "वन्स-थ्रू: पूरा टन निपटाया जाता है",
  "one tonne of fuel: each square is {#} kg": "एक टन ईंधन: हर वर्ग {#} kg",
  "one tonne: each square {#} kg": "एक टन: हर वर्ग {#} kg",
  "pellets": "गोलियाँ",
  "pellets, {#} cm tall": "गोलियाँ, {#} cm ऊँची",
  "plutonium": "प्लूटोनियम",
  "pool": "कुंड",
  "recycle": "पुनर्चक्रण",
  "repository": "भंडार",
  "repository {#}–{#} m deep": "भंडार {#}–{#} m गहरा",
  "reprocess": "पुनर्संसाधन",
  "richest, Canada: up to {#} %": "सबसे समृद्ध, कनाडा: {#} % तक",
  "rods, about {#} m long": "छड़ें, लगभग {#} m लंबी",
  "rods, {#} m": "छड़ें, {#} m",
  "the rest: uranium{#}": "शेष: यूरेनियम{#}",
  "the whole tonne": "पूरा टन",
  "typical discharge {#}–{#}": "सामान्य निष्कासन {#}–{#}",
  "uranium{#}": "यूरेनियम{#}",
  "uranium{#} (and {#})": "यूरेनियम{#} (और {#})",
  "{#} U atoms": "{#} U परमाणु",
  "{#} are U{#}": "इनमें {#} U{#} हैं",
  "{#} are uranium{#}": "इनमें {#} यूरेनियम{#} हैं",
  "{#} t used": "{#} t प्रयुक्त",
  "{#} t used fuel": "{#} t प्रयुक्त ईंधन",
  "{#} uranium atoms": "{#} यूरेनियम परमाणु",
  "≈ a big reactor's yearly reload": "≈ बड़े रिएक्टर का वार्षिक पुनर्भरण",
  "≥ {#} years": "≥ {#} वर्ष",
  "{a} t ore": "{a} t अयस्क",
  "{a} t U₃O₈": "{a} t U₃O₈",
  "{a} t UF₆": "{a} t UF₆",
  "{#} t fuel + {a} t tails": "{#} t ईंधन + {a} t टेल्स",
  "{a} t UO₂": "{a} t UO₂",
  "pool ≥ {#} years": "कुंड ≥ {#} वर्ष",
  "ore ≈ {a} t · block = {#} t": "अयस्क ≈ {a} t · खंड = {#} t",
  "ore for one tonne of fuel: ≈ {a} t  (each block {#} t)": "एक टन ईंधन के लिए अयस्क: ≈ {a} t  (हर खंड {#} t)",
  "{a} of one block": "एक खंड का {a}",
  "{a} % U": "{a} % U",
  "grade {a} % U": "श्रेणी {a} % U",
  "natural U {a} kg": "प्राकृतिक U {a} kg",
  "natural uranium {a} kg": "प्राकृतिक यूरेनियम {a} kg",
  "{a} % U{#}": "{a} % U{#}",
  "fuel {#} kg": "ईंधन {#} kg",
  "tails {a} kg": "टेल्स {a} kg",
  "feed/fuel = (xp − xt)/(xf − xt) = {a}": "फ़ीड/ईंधन = (xp − xt)/(xf − xt) = {a}",
  "natural / fuel = (xp − xt) / (xf − xt) = ({a} − {b}) / ({c} − {b}) = {d}": "प्राकृतिक / ईंधन = (xp − xt) / (xf − xt) = ({a} − {b}) / ({c} − {b}) = {d}",
  "≈ {a} SWU of separative work per kg of fuel": "प्रति kg ईंधन ≈ {a} SWU पृथक्करण कार्य",
  "separative work ≈ {a} SWU per kg of fuel · lower tails: less uranium, more work": "पृथक्करण कार्य ≈ {a} SWU प्रति kg ईंधन · कम टेल्स: कम यूरेनियम, अधिक कार्य",
  "{a} t uranium = {b} t UO₂": "{a} t यूरेनियम = {b} t UO₂",
  "{a} t of enriched uranium, as {b} t of uranium dioxide (UO₂) ceramic": "{a} t संवर्धित यूरेनियम, {b} t यूरेनियम डाइऑक्साइड (UO₂) सिरेमिक के रूप में",
  "{a} % of the heavy atoms split": "{a} % भारी परमाणु विखंडित",
  "{a} GWd/t": "{a} GWd/t",
  "≈ {a} GWh of electricity": "≈ {a} GWh बिजली",
  "reprocessing": "पुनर्संसाधन",
  "uranium {a} t": "यूरेनियम {a} t",
  "plutonium {a} kg": "प्लूटोनियम {a} kg",
  "→ ≈ {a} t MOX fuel": "→ ≈ {a} t MOX ईंधन",
  "fission products + minor actinides {a} kg → ≈ {#} t glass": "विखंडन उत्पाद + लघु ऐक्टिनाइड {a} kg → ≈ {#} t काँच",
  "U {a} t → re-enrich": "U {a} t → पुनः संवर्धन",
  "Pu {a} kg → MOX": "Pu {a} kg → MOX",
  "{a} kg waste → glass": "{a} kg अपशिष्ट → काँच",
  "fission prod.": "विखंडन उत्पाद",
  "minor act.": "लघु ऐक्टि.",
});
