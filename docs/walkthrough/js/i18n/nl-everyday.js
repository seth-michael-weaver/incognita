/* Dutch (Nederlands): everyday (Kernfysica in het dagelijks leven) */
WT.L.ch.everyday = {
  num: "Les 4", title: "Kernfysica in het dagelijks leven", short: "Dagelijks leven",
  html: `
<div class="step">
  <h3>PET-scans</h3>
  <p>Een fluor-18-tracer (halveringstijd 110 minuten) zendt positronen uit, en elk ervan wordt twee gammastralen van 511 keV die precies tegengesteld wegvliegen. Sleep de hete plek: de ring trekt voor elk paar een lijn, en de lijnen kruisen elkaar waar de tracer zit.</p>
</div>
<div class="step">
  <h3>Radiotherapie</h3>
  <p>Bundels uit verschillende richtingen overlappen in de tumor, zodat die de volle dosis krijgt terwijl elk pad door gezond weefsel maar een deel krijgt. Sleep om de bundels te draaien en houd ze weg van het ruggenmerg.</p>
  <div class="ctl"><label for="ev-n">Bundels</label><input id="ev-n" type="range" data-bind="nb" data-instant min="1" max="7" step="1" value="5"><output data-show="nb" data-fmt="0"></output></div>
  <div class="ctl"><label for="ev-r">Draaien</label><input id="ev-r" type="range" data-bind="rotd" data-instant min="0" max="360" step="1" value="20"><output class="ev-rot"></output></div>
</div>
<div class="step">
  <h3>Technetium-99m</h3>
  <p>De isotoop achter de meeste nucleair-geneeskundige scans zendt een gammastraal van 140 keV uit die een camera buiten het lichaam kan zien, en met een halveringstijd van 6 uur is er na een dag weinig over. Ziekenhuizen <a href="#chains-3">melken het uit molybdeen-99</a>.</p>
  <div class="ctl"><label for="ev-t">Uren na toediening</label><input id="ev-t" type="range" data-bind="th" data-instant min="0" max="48" step="0.5" value="0"><output data-show="th" data-fmt="1"></output></div>
</div>
<div class="step">
  <h3>Koolstofdatering</h3>
  <p>Levende wezens nemen voortdurend koolstof-14 op; na de dood vervalt het met een halveringstijd van 5730 jaar. Stel de leeftijd in, of meet wat er over is om de leeftijd af te lezen.</p>
  <div class="ctl"><label for="ev-a">Leeftijd (jaar)</label><input id="ev-a" type="range" data-bind="age" data-instant min="0" max="50000" step="10" value="5300"><output class="ev-age"></output></div>
  <div class="ctl"><label for="ev-f">Resterend koolstof-14 (%)</label><input id="ev-f" type="range" data-bind="fr" data-instant min="0.3" max="100" step="0.1" value="52.7"><output class="ev-fr"></output></div>
</div>
<div class="step">
  <h3>Rookmelders</h3>
  <p>Een verzegeld korreltje americium-241 stuurt alfadeeltjes over een kleine luchtspleet en maakt ionen die een piepkleine stroom dragen. Rook vangt de ionen, de stroom daalt en het alarm gaat af.</p>
  <div class="ctl"><label for="ev-s">Rook</label><input id="ev-s" type="range" data-bind="sm" data-instant min="0" max="1" step="0.01" value="0"><output class="ev-sm"></output></div>
</div>`,
};

Object.assign(WT.L.labels, {
  "{#} beams cross: the tumour gets their sum": "{#} bundels kruisen: de tumor krijgt hun som",
  "{#} h": "{#} u",
  "{#} h: {#} % left": "{#} u: {#} % over",
  "{#} half-lives": "{#} halveringstijden",
  "{#} keV gamma rays": "gammastralen van {#} keV",
  "{#} of {#} left": "{#} van {#} over",
  "{#} years · {#} % left": "{#} jaar · {#} % over",
  "~{#} y: too little to measure": "~{#} j: te weinig om te meten",
  "a beam crosses the spinal cord: turn the beams": "een bundel kruist het ruggenmerg: draai de bundels",
  "a strong gamma signal, easy to image": "een sterk gammasignaal, makkelijk in beeld te brengen",
  "after a day, about {#} % is left": "na een dag is er ongeveer {#} % over",
  "alarm": "alarm",
  "alpha particles make ions in the air": "alfadeeltjes maken ionen in de lucht",
  "Am{#}": "Am{#}",
  "americium{#} · half-life {#} years · alphas reach about {#} cm in air": "americium{#} · halveringstijd {#} jaar · alfa's komen ongeveer {#} cm ver in lucht",
  "americium{#} (sealed)": "americium{#} (verzegeld)",
  "beyond ~{#} years too little is left to measure": "na ~{#} jaar is er te weinig over om te meten",
  "carbon{#}": "koolstof{#}",
  "clean air: steady current": "schone lucht: constante stroom",
  "current": "stroom",
  "detector ring": "detectorring",
  "dose": "dosis",
  "each decay: two {#} keV gamma rays, back to back": "elk verval: twee gammastralen van {#} keV, tegengesteld",
  "fading: half is gone every {#} hours": "afnemend: elke {#} uur is de helft weg",
  "fluorine{#} · half-life {#} min · {#} pairs recorded": "fluor{#} · halveringstijd {#} min · {#} paren geregistreerd",
  "gamma camera": "gammacamera",
  "half-life {#} y": "halveringstijd {#} j",
  "illustration": "illustratie",
  "Mo{#} ({#} h)": "Mo{#} ({#} u)",
  "molybdenum{#}, half-life {#} h": "molybdeen{#}, halveringstijd {#} u",
  "nitrogen{#}": "stikstof{#}",
  "nitrogen{#} (after a beta decay)": "stikstof{#} (na een bètaverval)",
  "one beam: more dose near the skin than in the tumour": "één bundel: meer dosis bij de huid dan in de tumor",
  "Ötzi the Iceman, ~{#} y": "Ötzi de ijsmummie, ~{#} j",
  "pairs of {#} keV gamma rays, back to back": "paren gammastralen van {#} keV, tegengesteld",
  "physical decay only": "alleen fysisch verval",
  "smoke: current down, alarm!": "rook: stroom omlaag, alarm!",
  "some ions caught: current dipping": "enkele ionen gevangen: stroom zakt",
  "spinal cord": "ruggenmerg",
  "Tc{#}m ({#} h)": "Tc{#}m ({#} u)",
  "technetium{#}m, half-life {#} h": "technetium{#}m, halveringstijd {#} u",
  "tracer": "tracer",
  "tracer (drag me)": "tracer (sleep mij)",
  "tumour": "tumor",
  "tumour {#} % · spinal cord {#} % · healthy tissue at most {#} %": "tumor {#} % · ruggenmerg {#} % · gezond weefsel hoogstens {#} %",
  "tumour {#} % · spinal cord {#} % · other tissue at most {#} %": "tumor {#} % · ruggenmerg {#} % · ander weefsel hoogstens {#} %",
  "years": "jaar",
});
