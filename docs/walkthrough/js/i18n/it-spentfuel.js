/* Italian (Italiano): spentfuel (Il combustibile esaurito, nuclide per nuclide) */
WT.L.ch.spentfuel = {
  num: "Lezione 1", title: "Il combustibile esaurito, nuclide per nuclide", short: "Nuclide per nuclide",
  html: `
<div class="step">
  <h3>Che cosa contiene</h3>
  <p>Una tonnellata di combustibile PWR un anno dopo lo scarico (arricchito al 4,2 %, 50 GWd/t): quasi tutta la massa è uranio, quasi tutta l'attività sta in pochi chilogrammi.</p>
</div>
<div class="step">
  <h3>Attività o radiotossicità</h3>
  <p>I becquerel contano i decadimenti; i sievert pesano ciascun decadimento per il danno in caso di ingestione, il che dà più peso agli emettitori alfa.</p>
  <div class="btns"><button class="btn ghost" data-act="mA" aria-pressed="false">Attività (Bq)</button> <button class="btn ghost" data-act="mT" aria-pressed="true">Radiotossicità (Sv)</button></div>
</div>
<div class="step">
  <h3>Chi domina e quando</h3>
  <p>Passa sopra una banda o toccala per vederne il nome; trascina lungo l'asse del tempo per metterle in ordine.</p>
</div>
<div class="step">
  <h3>Ricicla il plutonio</h3>
  <p>Il ritrattamento dopo quattro anni toglie il plutonio (e con esso l'uranio). Quanto ne resta?</p>
  <div class="btns"><span class="sf-k" style="font:600 13px var(--sans);color:var(--soft);margin-right:4px;align-self:center">Pu rimosso</span> <button class="btn ghost" data-act="pu0" aria-pressed="true">0 %</button> <button class="btn ghost" data-act="pu99" aria-pressed="false">99 %</button> <button class="btn ghost" data-act="pu999" aria-pressed="false">99,9 %</button></div>
</div>
<div class="step">
  <h3>Rimuovi anche gli attinidi minori</h3>
  <p>Togli anche americio, curio e nettunio: allora è l'1 % o lo 0,1 % che resta a decidere il tempo.</p>
  <div class="btns"><span class="sf-k" style="font:600 13px var(--sans);color:var(--soft);margin-right:4px;align-self:center">Pu rimosso</span> <button class="btn ghost" data-act="pu0" aria-pressed="true">0 %</button> <button class="btn ghost" data-act="pu99" aria-pressed="false">99 %</button> <button class="btn ghost" data-act="pu999" aria-pressed="false">99,9 %</button></div>
  <div class="btns"><span class="sf-k" style="font:600 13px var(--sans);color:var(--soft);margin-right:4px;align-self:center">Am, Cm, Np rimossi</span> <button class="btn ghost" data-act="ma0" aria-pressed="true">0 %</button> <button class="btn ghost" data-act="ma99" aria-pressed="false">99 %</button> <button class="btn ghost" data-act="ma999" aria-pressed="false">99,9 %</button></div>
</div>`,
};

Object.assign(WT.L.labels, {
  "{#} g": "{#} g",
  "{#} kg": "{#} kg",
  "{#} million": "{#} milione",
  "{#} years:": "{#} anni:",
  "{#} yr": "{#} anni",
  "{#}¹⁰ Bq": "{#}¹⁰ Bq",
  "{#}¹³ Bq": "{#}¹³ Bq",
  "{#}¹⁶ Bq": "{#}¹⁶ Bq",
  "activity": "attività",
  "activity after {#} year (log scale)": "attività dopo {#} anno (scala log.)",
  "Am{#}": "Am{#}",
  "Am{#} {#} %": "Am{#} {#} %",
  "below the ore after ≈ {#} years": "sotto il minerale dopo ≈ {#} anni",
  "Cm{#}": "Cm{#}",
  "computed · band height = share": "calcolato · altezza della banda = quota",
  "computed (Bateman decay, ICRP{#}) · band height = share of the total": "calcolato (decadimento di Bateman, ICRP{#}) · altezza della banda = quota del totale",
  "Cs{#}": "Cs{#}",
  "drag along the time axis · hover a band": "trascina lungo l'asse del tempo · passa sopra una banda",
  "drag the time · tap a band": "trascina il tempo · tocca una banda",
  "I{#}": "I{#}",
  "inventory: OECD-NEA {#} ({#} %, {#} GWd/t) + computed fission products": "inventario: OCSE-NEA {#} ({#} %, {#} GWd/t) + prodotti di fissione calcolati",
  "mass": "massa",
  "mass (log scale)": "massa (scala log.)",
  "most of the {#} kg of fission products is stable; activity includes short-lived daughters": "quasi tutti i {#} kg di prodotti di fissione sono stabili; l'attività include i figli a vita breve",
  "NEA {#} + computed": "NEA {#} + calcolato",
  "Np{#}": "Np{#}",
  "once-through": "ciclo aperto",
  "once-through (no recycling)": "ciclo aperto (senza riciclo)",
  "ore: {#}×{#}⁵ Sv": "minerale: {#}×{#}⁵ Sv",
  "other fission products": "altri prodotti di fissione",
  "other FP": "altri PF",
  "other FP: mostly stable": "altri PF: quasi tutti stabili",
  "Pu{#}": "Pu{#}",
  "Pu{#} {#} %": "Pu{#} {#} %",
  "radiotoxicity ÷ ore": "radiotossicità ÷ minerale",
  "radiotoxicity if swallowed (Sv), relative to the ore": "radiotossicità per ingestione (Sv), relativa al minerale",
  "reprocessing at {#} yr": "ritrattamento a {#} anni",
  "Sr{#}": "Sr{#}",
  "Sr{#} + Y{#}": "Sr{#} + Y{#}",
  "still above the ore after a million years": "ancora sopra il minerale dopo un milione di anni",
  "Tc{#}": "Tc{#}",
  "the ore it came from: {#} t natural uranium + daughters = {#}×{#}⁵ Sv": "il minerale di origine: {#} t di uranio naturale + figli = {#}×{#}⁵ Sv",
  "then mostly Am{#} ({#} %)": "poi soprattutto Am{#} ({#} %)",
  "then mostly Np{#} ({#} %)": "poi soprattutto Np{#} ({#} %)",
  "then mostly Pb{#} + Po{#} ({#} %)": "poi soprattutto Pb{#} + Po{#} ({#} %)",
  "then mostly Pu{#} ({#} %)": "poi soprattutto Pu{#} ({#} %)",
  "then mostly Sr{#} + Y{#} ({#} %)": "poi soprattutto Sr{#} + Y{#} ({#} %)",
  "uranium": "uranio",
  "years after unloading (log scale) →": "anni dopo lo scarico (scala log.) →",
});
