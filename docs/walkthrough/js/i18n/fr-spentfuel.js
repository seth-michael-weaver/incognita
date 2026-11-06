/* French (Français): spentfuel (Le combustible usé, nucléide par nucléide) */
WT.L.ch.spentfuel = {
  num: "Leçon 1", title: "Le combustible usé, nucléide par nucléide", short: "Nucléide par nucléide",
  html: `
<div class="step">
  <h3>Ce qu'il contient</h3>
  <p>Une tonne de combustible de REP un an après le déchargement (enrichi à 4,2 %, 50 GWj/t) : presque toute la masse est de l'uranium, presque toute l'activité tient dans quelques kilogrammes.</p>
</div>
<div class="step">
  <h3>Activité ou radiotoxicité</h3>
  <p>Les becquerels comptent les désintégrations ; les sieverts pondèrent chacune par sa nocivité en cas d'ingestion, ce qui fait ressortir les émetteurs alpha.</p>
  <div class="btns"><button class="btn ghost" data-act="mA" aria-pressed="false">Activité (Bq)</button> <button class="btn ghost" data-act="mT" aria-pressed="true">Radiotoxicité (Sv)</button></div>
</div>
<div class="step">
  <h3>Qui domine, et quand</h3>
  <p>Survolez ou touchez une bande pour la nommer ; faites glisser le long de l'axe du temps pour les classer.</p>
</div>
<div class="step">
  <h3>Recycler le plutonium</h3>
  <p>Le retraitement au bout de quatre ans retire le plutonium (et l'uranium avec). Combien en reste-t-il ?</p>
  <div class="btns"><span class="sf-k" style="font:600 13px var(--sans);color:var(--soft);margin-right:4px;align-self:center">Pu retiré</span> <button class="btn ghost" data-act="pu0" aria-pressed="true">0 %</button> <button class="btn ghost" data-act="pu99" aria-pressed="false">99 %</button> <button class="btn ghost" data-act="pu999" aria-pressed="false">99,9 %</button></div>
</div>
<div class="step">
  <h3>Retirer aussi les actinides mineurs</h3>
  <p>Retirez aussi l'américium, le curium et le neptunium : c'est alors le 1 % ou le 0,1 % restant qui fixe la durée.</p>
  <div class="btns"><span class="sf-k" style="font:600 13px var(--sans);color:var(--soft);margin-right:4px;align-self:center">Pu retiré</span> <button class="btn ghost" data-act="pu0" aria-pressed="true">0 %</button> <button class="btn ghost" data-act="pu99" aria-pressed="false">99 %</button> <button class="btn ghost" data-act="pu999" aria-pressed="false">99,9 %</button></div>
  <div class="btns"><span class="sf-k" style="font:600 13px var(--sans);color:var(--soft);margin-right:4px;align-self:center">Am, Cm, Np retirés</span> <button class="btn ghost" data-act="ma0" aria-pressed="true">0 %</button> <button class="btn ghost" data-act="ma99" aria-pressed="false">99 %</button> <button class="btn ghost" data-act="ma999" aria-pressed="false">99,9 %</button></div>
</div>`,
};

Object.assign(WT.L.labels, {
  "{#} g": "{#} g",
  "{#} kg": "{#} kg",
  "{#} million": "{#} million",
  "{#} years:": "{#} ans :",
  "{#} yr": "{#} ans",
  "{#}¹⁰ Bq": "{#}¹⁰ Bq",
  "{#}¹³ Bq": "{#}¹³ Bq",
  "{#}¹⁶ Bq": "{#}¹⁶ Bq",
  "activity": "activité",
  "activity after {#} year (log scale)": "activité après {#} an (échelle log)",
  "Am{#}": "Am{#}",
  "Am{#} {#} %": "Am{#} {#} %",
  "below the ore after ≈ {#} years": "sous le minerai après ≈ {#} ans",
  "Cm{#}": "Cm{#}",
  "computed · band height = share": "calculé · hauteur de bande = part",
  "computed (Bateman decay, ICRP{#}) · band height = share of the total": "calculé (décroissance de Bateman, CIPR{#}) · hauteur de bande = part du total",
  "Cs{#}": "Cs{#}",
  "drag along the time axis · hover a band": "faites glisser le long de l'axe du temps · survolez une bande",
  "drag the time · tap a band": "faites glisser le temps · touchez une bande",
  "I{#}": "I{#}",
  "inventory: OECD-NEA {#} ({#} %, {#} GWd/t) + computed fission products": "inventaire : OCDE-AEN {#} ({#} %, {#} GWj/t) + produits de fission calculés",
  "mass": "masse",
  "mass (log scale)": "masse (échelle log)",
  "most of the {#} kg of fission products is stable; activity includes short-lived daughters": "l'essentiel des {#} kg de produits de fission est stable ; l'activité inclut les descendants à vie courte",
  "NEA {#} + computed": "AEN {#} + calcul",
  "Np{#}": "Np{#}",
  "once-through": "cycle ouvert",
  "once-through (no recycling)": "cycle ouvert (sans recyclage)",
  "ore: {#}×{#}⁵ Sv": "minerai : {#}×{#}⁵ Sv",
  "other fission products": "autres produits de fission",
  "other FP": "autres PF",
  "other FP: mostly stable": "autres PF : surtout stables",
  "Pu{#}": "Pu{#}",
  "Pu{#} {#} %": "Pu{#} {#} %",
  "radiotoxicity ÷ ore": "radiotoxicité ÷ minerai",
  "radiotoxicity if swallowed (Sv), relative to the ore": "radiotoxicité par ingestion (Sv), rapportée au minerai",
  "reprocessing at {#} yr": "retraitement à {#} ans",
  "Sr{#}": "Sr{#}",
  "Sr{#} + Y{#}": "Sr{#} + Y{#}",
  "still above the ore after a million years": "encore au-dessus du minerai après un million d'années",
  "Tc{#}": "Tc{#}",
  "the ore it came from: {#} t natural uranium + daughters = {#}×{#}⁵ Sv": "le minerai d'origine : {#} t d'uranium naturel + descendants = {#}×{#}⁵ Sv",
  "then mostly Am{#} ({#} %)": "puis surtout Am{#} ({#} %)",
  "then mostly Np{#} ({#} %)": "puis surtout Np{#} ({#} %)",
  "then mostly Pb{#} + Po{#} ({#} %)": "puis surtout Pb{#} + Po{#} ({#} %)",
  "then mostly Pu{#} ({#} %)": "puis surtout Pu{#} ({#} %)",
  "then mostly Sr{#} + Y{#} ({#} %)": "puis surtout Sr{#} + Y{#} ({#} %)",
  "uranium": "uranium",
  "years after unloading (log scale) →": "années après le déchargement (échelle log) →",
});
