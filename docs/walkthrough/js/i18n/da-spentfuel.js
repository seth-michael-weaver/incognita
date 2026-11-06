/* Danish (Dansk): spentfuel (Brugt brændsel, nuklid for nuklid) */
WT.L.ch.spentfuel = {
  num: "Lektion 1", title: "Brugt brændsel, nuklid for nuklid", short: "Nuklid for nuklid",
  html: `
<div class="step">
  <h3>Hvad der er indeni</h3>
  <p>Ét ton PWR-brændsel et år efter udtagning (4,2 % beriget, 50 GWd/t): næsten hele massen er uran, næsten hele aktiviteten sidder i nogle få kilogram.</p>
</div>
<div class="step">
  <h3>Aktivitet eller radiotoksicitet</h3>
  <p>Becquerel tæller henfald; sievert vægter hvert henfald efter dets skade, hvis det sluges, hvilket løfter alfastrålerne.</p>
  <div class="btns"><button class="btn ghost" data-act="mA" aria-pressed="false">Aktivitet (Bq)</button> <button class="btn ghost" data-act="mT" aria-pressed="true">Radiotoksicitet (Sv)</button></div>
</div>
<div class="step">
  <h3>Hvem dominerer hvornår</h3>
  <p>Hold musen over et bånd eller tryk på det for at navngive det; træk langs tidsaksen for at rangordne dem.</p>
</div>
<div class="step">
  <h3>Genbrug plutoniummet</h3>
  <p>Oparbejdning efter fire år tager plutoniummet ud (og uranet med). Hvor meget bliver tilbage?</p>
  <div class="btns"><span class="sf-k" style="font:600 13px var(--sans);color:var(--soft);margin-right:4px;align-self:center">Pu fjernet</span> <button class="btn ghost" data-act="pu0" aria-pressed="true">0 %</button> <button class="btn ghost" data-act="pu99" aria-pressed="false">99 %</button> <button class="btn ghost" data-act="pu999" aria-pressed="false">99,9 %</button></div>
</div>
<div class="step">
  <h3>Fjern også de mindre actinider</h3>
  <p>Tag også americium, curium og neptunium ud: så er det den 1 % eller 0,1 %, der bliver tilbage, som bestemmer tiden.</p>
  <div class="btns"><span class="sf-k" style="font:600 13px var(--sans);color:var(--soft);margin-right:4px;align-self:center">Pu fjernet</span> <button class="btn ghost" data-act="pu0" aria-pressed="true">0 %</button> <button class="btn ghost" data-act="pu99" aria-pressed="false">99 %</button> <button class="btn ghost" data-act="pu999" aria-pressed="false">99,9 %</button></div>
  <div class="btns"><span class="sf-k" style="font:600 13px var(--sans);color:var(--soft);margin-right:4px;align-self:center">Am, Cm, Np fjernet</span> <button class="btn ghost" data-act="ma0" aria-pressed="true">0 %</button> <button class="btn ghost" data-act="ma99" aria-pressed="false">99 %</button> <button class="btn ghost" data-act="ma999" aria-pressed="false">99,9 %</button></div>
</div>`,
};

Object.assign(WT.L.labels, {
  "{#} g": "{#} g",
  "{#} kg": "{#} kg",
  "{#} million": "{#} million",
  "{#} years:": "{#} år:",
  "{#} yr": "{#} år",
  "{#}¹⁰ Bq": "{#}¹⁰ Bq",
  "{#}¹³ Bq": "{#}¹³ Bq",
  "{#}¹⁶ Bq": "{#}¹⁶ Bq",
  "activity": "aktivitet",
  "activity after {#} year (log scale)": "aktivitet efter {#} år (log. skala)",
  "Am{#}": "Am{#}",
  "Am{#} {#} %": "Am{#} {#} %",
  "below the ore after ≈ {#} years": "under malmen efter ≈ {#} år",
  "Cm{#}": "Cm{#}",
  "computed · band height = share": "beregnet · båndhøjde = andel",
  "computed (Bateman decay, ICRP{#}) · band height = share of the total": "beregnet (Bateman-henfald, ICRP{#}) · båndhøjde = andel af totalen",
  "Cs{#}": "Cs{#}",
  "drag along the time axis · hover a band": "træk langs tidsaksen · hold over et bånd",
  "drag the time · tap a band": "træk i tiden · tryk på et bånd",
  "I{#}": "I{#}",
  "inventory: OECD-NEA {#} ({#} %, {#} GWd/t) + computed fission products": "inventar: OECD-NEA {#} ({#} %, {#} GWd/t) + beregnede fissionsprodukter",
  "mass": "masse",
  "mass (log scale)": "masse (log. skala)",
  "most of the {#} kg of fission products is stable; activity includes short-lived daughters": "det meste af de {#} kg fissionsprodukter er stabilt; aktiviteten omfatter kortlivede døtre",
  "NEA {#} + computed": "NEA {#} + beregnet",
  "Np{#}": "Np{#}",
  "once-through": "direkte deponering",
  "once-through (no recycling)": "direkte deponering (intet genbrug)",
  "ore: {#}×{#}⁵ Sv": "malm: {#}×{#}⁵ Sv",
  "other fission products": "andre fissionsprodukter",
  "other FP": "andre FP",
  "other FP: mostly stable": "andre FP: mest stabile",
  "Pu{#}": "Pu{#}",
  "Pu{#} {#} %": "Pu{#} {#} %",
  "radiotoxicity ÷ ore": "radiotoksicitet ÷ malm",
  "radiotoxicity if swallowed (Sv), relative to the ore": "radiotoksicitet ved indtagelse (Sv), i forhold til malmen",
  "reprocessing at {#} yr": "oparbejdning efter {#} år",
  "Sr{#}": "Sr{#}",
  "Sr{#} + Y{#}": "Sr{#} + Y{#}",
  "still above the ore after a million years": "stadig over malmen efter en million år",
  "Tc{#}": "Tc{#}",
  "the ore it came from: {#} t natural uranium + daughters = {#}×{#}⁵ Sv": "malmen det kom fra: {#} t naturligt uran + døtre = {#}×{#}⁵ Sv",
  "then mostly Am{#} ({#} %)": "derefter mest Am{#} ({#} %)",
  "then mostly Np{#} ({#} %)": "derefter mest Np{#} ({#} %)",
  "then mostly Pb{#} + Po{#} ({#} %)": "derefter mest Pb{#} + Po{#} ({#} %)",
  "then mostly Pu{#} ({#} %)": "derefter mest Pu{#} ({#} %)",
  "then mostly Sr{#} + Y{#} ({#} %)": "derefter mest Sr{#} + Y{#} ({#} %)",
  "uranium": "uran",
  "years after unloading (log scale) →": "år efter udtagning (log. skala) →",
});
