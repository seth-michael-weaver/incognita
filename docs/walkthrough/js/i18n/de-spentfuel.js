/* German (Deutsch): spentfuel (Abgebrannter Brennstoff, Nuklid für Nuklid) */
WT.L.ch.spentfuel = {
  num: "Lektion 1", title: "Abgebrannter Brennstoff, Nuklid für Nuklid", short: "Nuklid für Nuklid",
  html: `
<div class="step">
  <h3>Was drinsteckt</h3>
  <p>Eine Tonne DWR-Brennstoff ein Jahr nach dem Entladen (4,2 % angereichert, 50 GWd/t): Fast die ganze Masse ist Uran, fast die ganze Aktivität steckt in wenigen Kilogramm.</p>
</div>
<div class="step">
  <h3>Aktivität oder Radiotoxizität</h3>
  <p>Becquerel zählen Zerfälle; Sievert gewichten jeden Zerfall nach seinem Schaden beim Verschlucken, was die Alphastrahler hervorhebt.</p>
  <div class="btns"><button class="btn ghost" data-act="mA" aria-pressed="false">Aktivität (Bq)</button> <button class="btn ghost" data-act="mT" aria-pressed="true">Radiotoxizität (Sv)</button></div>
</div>
<div class="step">
  <h3>Wer wann dominiert</h3>
  <p>Fahr mit der Maus über ein Band oder tippe darauf, um es zu benennen; zieh entlang der Zeitachse, um sie zu ordnen.</p>
</div>
<div class="step">
  <h3>Das Plutonium rezyklieren</h3>
  <p>Wiederaufarbeitung nach vier Jahren holt das Plutonium heraus (und das Uran mit). Wie viel bleibt zurück?</p>
  <div class="btns"><span class="sf-k" style="font:600 13px var(--sans);color:var(--soft);margin-right:4px;align-self:center">Pu abgetrennt</span> <button class="btn ghost" data-act="pu0" aria-pressed="true">0 %</button> <button class="btn ghost" data-act="pu99" aria-pressed="false">99 %</button> <button class="btn ghost" data-act="pu999" aria-pressed="false">99,9 %</button></div>
</div>
<div class="step">
  <h3>Auch die minoren Actinoide abtrennen</h3>
  <p>Hol auch Americium, Curium und Neptunium heraus: Dann bestimmt das 1 % oder 0,1 %, das zurückbleibt, die Zeit.</p>
  <div class="btns"><span class="sf-k" style="font:600 13px var(--sans);color:var(--soft);margin-right:4px;align-self:center">Pu abgetrennt</span> <button class="btn ghost" data-act="pu0" aria-pressed="true">0 %</button> <button class="btn ghost" data-act="pu99" aria-pressed="false">99 %</button> <button class="btn ghost" data-act="pu999" aria-pressed="false">99,9 %</button></div>
  <div class="btns"><span class="sf-k" style="font:600 13px var(--sans);color:var(--soft);margin-right:4px;align-self:center">Am, Cm, Np abgetrennt</span> <button class="btn ghost" data-act="ma0" aria-pressed="true">0 %</button> <button class="btn ghost" data-act="ma99" aria-pressed="false">99 %</button> <button class="btn ghost" data-act="ma999" aria-pressed="false">99,9 %</button></div>
</div>`,
};

Object.assign(WT.L.labels, {
  "{#} g": "{#} g",
  "{#} kg": "{#} kg",
  "{#} million": "{#} Million",
  "{#} years:": "{#} Jahre:",
  "{#} yr": "{#} a",
  "{#}¹⁰ Bq": "{#}¹⁰ Bq",
  "{#}¹³ Bq": "{#}¹³ Bq",
  "{#}¹⁶ Bq": "{#}¹⁶ Bq",
  "activity": "Aktivität",
  "activity after {#} year (log scale)": "Aktivität nach {#} Jahr (log. Skala)",
  "Am{#}": "Am{#}",
  "Am{#} {#} %": "Am{#} {#} %",
  "below the ore after ≈ {#} years": "unter dem Erz nach ≈ {#} Jahren",
  "Cm{#}": "Cm{#}",
  "computed · band height = share": "berechnet · Bandhöhe = Anteil",
  "computed (Bateman decay, ICRP{#}) · band height = share of the total": "berechnet (Bateman-Zerfall, ICRP{#}) · Bandhöhe = Anteil am Gesamtwert",
  "Cs{#}": "Cs{#}",
  "drag along the time axis · hover a band": "entlang der Zeitachse ziehen · über ein Band fahren",
  "drag the time · tap a band": "Zeit ziehen · Band antippen",
  "I{#}": "I{#}",
  "inventory: OECD-NEA {#} ({#} %, {#} GWd/t) + computed fission products": "Inventar: OECD-NEA {#} ({#} %, {#} GWd/t) + berechnete Spaltprodukte",
  "mass": "Masse",
  "mass (log scale)": "Masse (log. Skala)",
  "most of the {#} kg of fission products is stable; activity includes short-lived daughters": "der Großteil der {#} kg Spaltprodukte ist stabil; die Aktivität enthält kurzlebige Töchter",
  "NEA {#} + computed": "NEA {#} + berechnet",
  "Np{#}": "Np{#}",
  "once-through": "direkte Endlagerung",
  "once-through (no recycling)": "direkte Endlagerung (ohne Rezyklierung)",
  "ore: {#}×{#}⁵ Sv": "Erz: {#}×{#}⁵ Sv",
  "other fission products": "übrige Spaltprodukte",
  "other FP": "übrige SP",
  "other FP: mostly stable": "übrige SP: meist stabil",
  "Pu{#}": "Pu{#}",
  "Pu{#} {#} %": "Pu{#} {#} %",
  "radiotoxicity ÷ ore": "Radiotoxizität ÷ Erz",
  "radiotoxicity if swallowed (Sv), relative to the ore": "Radiotoxizität beim Verschlucken (Sv), relativ zum Erz",
  "reprocessing at {#} yr": "Wiederaufarbeitung nach {#} a",
  "Sr{#}": "Sr{#}",
  "Sr{#} + Y{#}": "Sr{#} + Y{#}",
  "still above the ore after a million years": "nach einer Million Jahren noch über dem Erz",
  "Tc{#}": "Tc{#}",
  "the ore it came from: {#} t natural uranium + daughters = {#}×{#}⁵ Sv": "das Erz, aus dem er stammt: {#} t Natururan + Töchter = {#}×{#}⁵ Sv",
  "then mostly Am{#} ({#} %)": "dann vor allem Am{#} ({#} %)",
  "then mostly Np{#} ({#} %)": "dann vor allem Np{#} ({#} %)",
  "then mostly Pb{#} + Po{#} ({#} %)": "dann vor allem Pb{#} + Po{#} ({#} %)",
  "then mostly Pu{#} ({#} %)": "dann vor allem Pu{#} ({#} %)",
  "then mostly Sr{#} + Y{#} ({#} %)": "dann vor allem Sr{#} + Y{#} ({#} %)",
  "uranium": "Uran",
  "years after unloading (log scale) →": "Jahre nach dem Entladen (log. Skala) →",
});
