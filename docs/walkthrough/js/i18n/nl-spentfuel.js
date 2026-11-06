/* Dutch (Nederlands): spentfuel (Gebruikte brandstof, nuclide voor nuclide) */
WT.L.ch.spentfuel = {
  num: "Les 1", title: "Gebruikte brandstof, nuclide voor nuclide", short: "Nuclide voor nuclide",
  html: `
<div class="step">
  <h3>Wat erin zit</h3>
  <p>Eén ton PWR-brandstof een jaar na het ontladen (4,2 % verrijkt, 50 GWd/t): bijna alle massa is uranium, bijna alle activiteit zit in een paar kilogram.</p>
</div>
<div class="step">
  <h3>Activiteit of radiotoxiciteit</h3>
  <p>Becquerels tellen vervallen; sieverts wegen elk verval naar de schade bij inslikken, wat de alfastralers zwaarder laat wegen.</p>
  <div class="btns"><button class="btn ghost" data-act="mA" aria-pressed="false">Activiteit (Bq)</button> <button class="btn ghost" data-act="mT" aria-pressed="true">Radiotoxiciteit (Sv)</button></div>
</div>
<div class="step">
  <h3>Wie wanneer domineert</h3>
  <p>Wijs een band aan of tik erop om hem te benoemen; sleep langs de tijdas om ze te rangschikken.</p>
</div>
<div class="step">
  <h3>Recycle het plutonium</h3>
  <p>Opwerking na vier jaar haalt het plutonium eruit (en het uranium mee). Hoeveel blijft er achter?</p>
  <div class="btns"><span class="sf-k" style="font:600 13px var(--sans);color:var(--soft);margin-right:4px;align-self:center">Pu verwijderd</span> <button class="btn ghost" data-act="pu0" aria-pressed="true">0 %</button> <button class="btn ghost" data-act="pu99" aria-pressed="false">99 %</button> <button class="btn ghost" data-act="pu999" aria-pressed="false">99,9 %</button></div>
</div>
<div class="step">
  <h3>Verwijder ook de minor actiniden</h3>
  <p>Haal ook americium, curium en neptunium eruit: dan bepaalt de 1 % of 0,1 % die achterblijft de tijd.</p>
  <div class="btns"><span class="sf-k" style="font:600 13px var(--sans);color:var(--soft);margin-right:4px;align-self:center">Pu verwijderd</span> <button class="btn ghost" data-act="pu0" aria-pressed="true">0 %</button> <button class="btn ghost" data-act="pu99" aria-pressed="false">99 %</button> <button class="btn ghost" data-act="pu999" aria-pressed="false">99,9 %</button></div>
  <div class="btns"><span class="sf-k" style="font:600 13px var(--sans);color:var(--soft);margin-right:4px;align-self:center">Am, Cm, Np verwijderd</span> <button class="btn ghost" data-act="ma0" aria-pressed="true">0 %</button> <button class="btn ghost" data-act="ma99" aria-pressed="false">99 %</button> <button class="btn ghost" data-act="ma999" aria-pressed="false">99,9 %</button></div>
</div>`,
};

Object.assign(WT.L.labels, {
  "{#} g": "{#} g",
  "{#} kg": "{#} kg",
  "{#} million": "{#} miljoen",
  "{#} years:": "{#} jaar:",
  "{#} yr": "{#} j",
  "{#}¹⁰ Bq": "{#}¹⁰ Bq",
  "{#}¹³ Bq": "{#}¹³ Bq",
  "{#}¹⁶ Bq": "{#}¹⁶ Bq",
  "activity": "activiteit",
  "activity after {#} year (log scale)": "activiteit na {#} jaar (log. schaal)",
  "Am{#}": "Am{#}",
  "Am{#} {#} %": "Am{#} {#} %",
  "below the ore after ≈ {#} years": "onder het erts na ≈ {#} jaar",
  "Cm{#}": "Cm{#}",
  "computed · band height = share": "berekend · bandhoogte = aandeel",
  "computed (Bateman decay, ICRP{#}) · band height = share of the total": "berekend (Bateman-verval, ICRP{#}) · bandhoogte = aandeel in het totaal",
  "Cs{#}": "Cs{#}",
  "drag along the time axis · hover a band": "sleep langs de tijdas · wijs een band aan",
  "drag the time · tap a band": "sleep de tijd · tik op een band",
  "I{#}": "I{#}",
  "inventory: OECD-NEA {#} ({#} %, {#} GWd/t) + computed fission products": "inventaris: OECD-NEA {#} ({#} %, {#} GWd/t) + berekende splijtingsproducten",
  "mass": "massa",
  "mass (log scale)": "massa (log. schaal)",
  "most of the {#} kg of fission products is stable; activity includes short-lived daughters": "het meeste van de {#} kg splijtingsproducten is stabiel; de activiteit omvat kortlevende dochters",
  "NEA {#} + computed": "NEA {#} + berekend",
  "Np{#}": "Np{#}",
  "once-through": "directe berging",
  "once-through (no recycling)": "directe berging (geen recycling)",
  "ore: {#}×{#}⁵ Sv": "erts: {#}×{#}⁵ Sv",
  "other fission products": "overige splijtingsproducten",
  "other FP": "overige SP",
  "other FP: mostly stable": "overige SP: meest stabiel",
  "Pu{#}": "Pu{#}",
  "Pu{#} {#} %": "Pu{#} {#} %",
  "radiotoxicity ÷ ore": "radiotoxiciteit ÷ erts",
  "radiotoxicity if swallowed (Sv), relative to the ore": "radiotoxiciteit bij inslikken (Sv), ten opzichte van het erts",
  "reprocessing at {#} yr": "opwerking na {#} j",
  "Sr{#}": "Sr{#}",
  "Sr{#} + Y{#}": "Sr{#} + Y{#}",
  "still above the ore after a million years": "na een miljoen jaar nog boven het erts",
  "Tc{#}": "Tc{#}",
  "the ore it came from: {#} t natural uranium + daughters = {#}×{#}⁵ Sv": "het erts waaruit het kwam: {#} t natuurlijk uranium + dochters = {#}×{#}⁵ Sv",
  "then mostly Am{#} ({#} %)": "dan vooral Am{#} ({#} %)",
  "then mostly Np{#} ({#} %)": "dan vooral Np{#} ({#} %)",
  "then mostly Pb{#} + Po{#} ({#} %)": "dan vooral Pb{#} + Po{#} ({#} %)",
  "then mostly Pu{#} ({#} %)": "dan vooral Pu{#} ({#} %)",
  "then mostly Sr{#} + Y{#} ({#} %)": "dan vooral Sr{#} + Y{#} ({#} %)",
  "uranium": "uranium",
  "years after unloading (log scale) →": "jaren na ontladen (log. schaal) →",
});
