/* Hindi: rcompare (रिएक्टर प्रकारों की तुलना) */
WT.L.ch.rcompare = {
  num: "पाठ 1", title: "रिएक्टर प्रकारों की तुलना", short: "तुलना",
  lead: "हर रिएक्टर मंदक और शीतलक का एक चुनाव है।",
  html: `
<div class="step">
  <h3>मंदक और शीतलक</h3>
  <p>चुनिए कि न्यूट्रॉनों को क्या धीमा करे और ऊष्मा को क्या ले जाए। किसी प्रकार पर टैप करके उसे देखें।</p>
</div>
<div class="step">
  <h3>जितना गर्म, उतना बेहतर</h3>
  <p>शीतलक कोर से जितना गर्म निकलता है, ऊष्मा का उतना बड़ा हिस्सा बिजली बन सकता है।</p>
</div>
<div class="step">
  <h3>आज क्या चल रहा है</h3>
  <p>दुनिया के अधिकांश रिएक्टर पहले तीन जल-शीतित प्रकारों के हैं।</p>
</div>`,
};
Object.assign(WT.L.labels, {
  "ADS": "ADS",
  "AGR": "AGR",
  "BWR": "BWR",
  "GFR": "GFR",
  "HTGR": "HTGR",
  "LFR": "LFR",
  "MSR": "MSR",
  "Magnox": "मैग्नॉक्स",
  "Micro": "माइक्रो",
  "Oklo": "Oklo",
  "PHWR": "PHWR",
  "PHWR ~{#} %": "PHWR ~{#} %",
  "PWR": "PWR",
  "RBMK": "RBMK",
  "SCWR": "SCWR",
  "SFR": "SFR",
  "SMR": "SMR",
  "TRIGA": "TRIGA",
  "VHTR": "VHTR",
  "about {#} power reactors in operation": "लगभग {#} बिजली रिएक्टर चालू हैं",
  "about {#} reactors in all": "कुल लगभग {#} रिएक्टर",
  "boiling": "उबल रहा है",
  "boiling water": "उबलता पानी",
  "carries the heat ↓": "ऊष्मा ले जाता है ↓",
  "coolant out →": "शीतलक निकास →",
  "coolant temperature leaving the core →": "कोर से निकलते शीतलक का तापमान →",
  "fast": "तेज",
  "gas": "गैस",
  "graphite": "ग्रेफाइट",
  "heavy water": "भारी पानी",
  "ideal (Carnot) limit": "आदर्श (कार्नो) सीमा",
  "ideal limit": "आदर्श सीमा",
  "illustration": "चित्रण",
  "light water": "हल्का पानी",
  "liquid metal": "द्रव धातु",
  "molten salt": "पिघला लवण",
  "none": "कोई नहीं",
  "none (fast)": "कोई नहीं (तेज)",
  "others ~{#} %": "अन्य ~{#} %",
  "others: AGR, RBMK, fast reactors, HTR-PM": "अन्य: AGR, RBMK, तेज रिएक्टर, HTR-PM",
  "others: gas, graphite, fast, HTGR": "अन्य: गैस, ग्रेफाइट, तेज, HTGR",
  "salt": "लवण",
  "slows the neutrons →": "न्यूट्रॉनों को धीमा करता है →",
  "supercrit.": "अतिक्रांतिक",
  "supercritical water": "अतिक्रांतिक पानी",
  "the world's power reactors": "दुनिया के बिजली रिएक्टर",
  "the world's power reactors, by type (rounded)": "दुनिया के बिजली रिएक्टर, प्रकार के अनुसार (पूर्णांकित)",
  "thermal": "तापीय",
  "water": "पानी",
  "what carries the heat ↓": "ऊष्मा को क्या ले जाता है ↓",
  "what slows the neutrons (moderator) →": "न्यूट्रॉनों को क्या धीमा करता है (मंदक) →",
  "{#} °C": "{#} °C",
  "↑ electricity": "↑ बिजली",
  "↑ share of heat turned into electricity": "↑ ऊष्मा का बिजली में बदला हिस्सा",
});
// hover line in the temperature chart
Object.assign(WT.L.labels, {
  "Pressurized water reactor: {#} °C, {#} %": "दाबित जल रिएक्टर: {#} °C, {#} %",
  "Boiling water reactor: {#} °C, {#} %": "क्वथन जल रिएक्टर: {#} °C, {#} %",
  "Pressurized heavy water reactor: {#} °C, {#} %": "दाबित भारी जल रिएक्टर: {#} °C, {#} %",
  "Graphite-moderated boiling water reactor: {#} °C, {#} %": "ग्रेफाइट-मंदित क्वथन जल रिएक्टर: {#} °C, {#} %",
  "Supercritical water reactor: {#} °C, {#} %": "अतिक्रांतिक जल रिएक्टर: {#} °C, {#} %",
  "Magnox: {#} °C, {#} %": "मैग्नॉक्स: {#} °C, {#} %",
  "Advanced gas-cooled reactor: {#} °C, {#} %": "उन्नत गैस-शीतित रिएक्टर: {#} °C, {#} %",
  "High-temperature gas reactor: {#} °C, {#} %": "उच्च-तापमान गैस रिएक्टर: {#} °C, {#} %",
  "Very-high-temperature reactor: {#} °C, {#} %": "अति-उच्च-तापमान रिएक्टर: {#} °C, {#} %",
  "Sodium-cooled fast reactor: {#} °C, {#} %": "सोडियम-शीतित फास्ट रिएक्टर: {#} °C, {#} %",
  "Lead-cooled fast reactor: {#} °C, {#} %": "सीसा-शीतित फास्ट रिएक्टर: {#} °C, {#} %",
  "Gas-cooled fast reactor: {#} °C, {#} %": "गैस-शीतित फास्ट रिएक्टर: {#} °C, {#} %",
  "Molten salt reactor: {#} °C, {#} %": "पिघला लवण रिएक्टर: {#} °C, {#} %",
  "Small modular reactor: {#} °C, {#} %": "लघु मॉड्यूलर रिएक्टर: {#} °C, {#} %",
  "Heat-pipe microreactor: {#} °C, {#} %": "हीट-पाइप माइक्रोरिएक्टर: {#} °C, {#} %",
});
