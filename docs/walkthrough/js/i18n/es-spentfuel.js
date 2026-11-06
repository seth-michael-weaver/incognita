/* Spanish (Español): spentfuel (El combustible gastado, nucleido a nucleido) */
WT.L.ch.spentfuel = {
  num: "Lección 1", title: "El combustible gastado, nucleido a nucleido", short: "Nucleido a nucleido",
  html: `
<div class="step">
  <h3>Qué hay dentro</h3>
  <p>Una tonelada de combustible de PWR un año después de la descarga (enriquecido al 4,2 %, 50 GWd/t): casi toda la masa es uranio, casi toda la actividad está en unos pocos kilogramos.</p>
</div>
<div class="step">
  <h3>Actividad o radiotoxicidad</h3>
  <p>Los becquerelios cuentan desintegraciones; los sieverts ponderan cada una por su daño si se ingiere, lo que realza a los emisores alfa.</p>
  <div class="btns"><button class="btn ghost" data-act="mA" aria-pressed="false">Actividad (Bq)</button> <button class="btn ghost" data-act="mT" aria-pressed="true">Radiotoxicidad (Sv)</button></div>
</div>
<div class="step">
  <h3>Quién domina y cuándo</h3>
  <p>Pasa el cursor o toca una banda para nombrarla; arrastra a lo largo del eje del tiempo para ordenarlas.</p>
</div>
<div class="step">
  <h3>Reciclar el plutonio</h3>
  <p>El reprocesado a los cuatro años saca el plutonio (y el uranio con él). ¿Cuánto queda?</p>
  <div class="btns"><span class="sf-k" style="font:600 13px var(--sans);color:var(--soft);margin-right:4px;align-self:center">Pu retirado</span> <button class="btn ghost" data-act="pu0" aria-pressed="true">0 %</button> <button class="btn ghost" data-act="pu99" aria-pressed="false">99 %</button> <button class="btn ghost" data-act="pu999" aria-pressed="false">99,9 %</button></div>
</div>
<div class="step">
  <h3>Retira también los actínidos minoritarios</h3>
  <p>Saca también el americio, el curio y el neptunio: entonces el 1 % o el 0,1 % que queda decide el tiempo.</p>
  <div class="btns"><span class="sf-k" style="font:600 13px var(--sans);color:var(--soft);margin-right:4px;align-self:center">Pu retirado</span> <button class="btn ghost" data-act="pu0" aria-pressed="true">0 %</button> <button class="btn ghost" data-act="pu99" aria-pressed="false">99 %</button> <button class="btn ghost" data-act="pu999" aria-pressed="false">99,9 %</button></div>
  <div class="btns"><span class="sf-k" style="font:600 13px var(--sans);color:var(--soft);margin-right:4px;align-self:center">Am, Cm, Np retirados</span> <button class="btn ghost" data-act="ma0" aria-pressed="true">0 %</button> <button class="btn ghost" data-act="ma99" aria-pressed="false">99 %</button> <button class="btn ghost" data-act="ma999" aria-pressed="false">99,9 %</button></div>
</div>`,
};

Object.assign(WT.L.labels, {
  "{#} g": "{#} g",
  "{#} kg": "{#} kg",
  "{#} million": "{#} millón",
  "{#} years:": "{#} años:",
  "{#} yr": "{#} años",
  "{#}¹⁰ Bq": "{#}¹⁰ Bq",
  "{#}¹³ Bq": "{#}¹³ Bq",
  "{#}¹⁶ Bq": "{#}¹⁶ Bq",
  "activity": "actividad",
  "activity after {#} year (log scale)": "actividad tras {#} año (escala log.)",
  "Am{#}": "Am{#}",
  "Am{#} {#} %": "Am{#} {#} %",
  "below the ore after ≈ {#} years": "por debajo del mineral tras ≈ {#} años",
  "Cm{#}": "Cm{#}",
  "computed · band height = share": "calculado · altura de banda = fracción",
  "computed (Bateman decay, ICRP{#}) · band height = share of the total": "calculado (decaimiento de Bateman, ICRP{#}) · altura de banda = fracción del total",
  "Cs{#}": "Cs{#}",
  "drag along the time axis · hover a band": "arrastra por el eje del tiempo · pasa sobre una banda",
  "drag the time · tap a band": "arrastra el tiempo · toca una banda",
  "I{#}": "I{#}",
  "inventory: OECD-NEA {#} ({#} %, {#} GWd/t) + computed fission products": "inventario: OCDE-NEA {#} ({#} %, {#} GWd/t) + productos de fisión calculados",
  "mass": "masa",
  "mass (log scale)": "masa (escala log.)",
  "most of the {#} kg of fission products is stable; activity includes short-lived daughters": "la mayor parte de los {#} kg de productos de fisión es estable; la actividad incluye descendientes de vida corta",
  "NEA {#} + computed": "NEA {#} + calculado",
  "Np{#}": "Np{#}",
  "once-through": "ciclo abierto",
  "once-through (no recycling)": "ciclo abierto (sin reciclado)",
  "ore: {#}×{#}⁵ Sv": "mineral: {#}×{#}⁵ Sv",
  "other fission products": "otros productos de fisión",
  "other FP": "otros PF",
  "other FP: mostly stable": "otros PF: casi todos estables",
  "Pu{#}": "Pu{#}",
  "Pu{#} {#} %": "Pu{#} {#} %",
  "radiotoxicity ÷ ore": "radiotoxicidad ÷ mineral",
  "radiotoxicity if swallowed (Sv), relative to the ore": "radiotoxicidad por ingestión (Sv), relativa al mineral",
  "reprocessing at {#} yr": "reprocesado a los {#} años",
  "Sr{#}": "Sr{#}",
  "Sr{#} + Y{#}": "Sr{#} + Y{#}",
  "still above the ore after a million years": "aún por encima del mineral tras un millón de años",
  "Tc{#}": "Tc{#}",
  "the ore it came from: {#} t natural uranium + daughters = {#}×{#}⁵ Sv": "el mineral de origen: {#} t de uranio natural + descendientes = {#}×{#}⁵ Sv",
  "then mostly Am{#} ({#} %)": "luego sobre todo Am{#} ({#} %)",
  "then mostly Np{#} ({#} %)": "luego sobre todo Np{#} ({#} %)",
  "then mostly Pb{#} + Po{#} ({#} %)": "luego sobre todo Pb{#} + Po{#} ({#} %)",
  "then mostly Pu{#} ({#} %)": "luego sobre todo Pu{#} ({#} %)",
  "then mostly Sr{#} + Y{#} ({#} %)": "luego sobre todo Sr{#} + Y{#} ({#} %)",
  "uranium": "uranio",
  "years after unloading (log scale) →": "años tras la descarga (escala log.) →",
});
