/* German (Deutsch): halflife (Radioaktivität und Halbwertszeit) */
WT.L.ch.halflife = {
  num: "Lektion 1", title: "Radioaktivität und Halbwertszeit", short: "Halbwertszeit",
  lead: "Manche Atome sind instabil: Früher oder später zerfällt ihr Kern, sendet Strahlung aus und wird zu etwas anderem. Niemand kann sagen, wann ein einzelner zerfällt, und doch folgt eine ganze Probe einer Uhr, nach der man seine Uhr stellen kann.",
  html: `
<div class="step">
  <h3>Eine Probe, die zufällig zerfällt</h3>
  <p>Jede leuchtende Kugel ist ein instabiler Kern. Jeder kann in jedem Moment zerfallen, einen Strahlungsblitz aussenden und zu einem ruhigen, stabilen Atom werden. Tippe einen an, um ihn zerfallen zu lassen.</p>
  <div class="btns"><button class="btn" data-act="refill">Neue Probe</button></div>
</div>
<div class="step">
  <h3>Die Hälfte, dann wieder die Hälfte</h3>
  <p>Niemand kann sagen, welcher als Nächstes zerfällt, aber die Menge ist vorhersagbar: Nach einer <b>Halbwertszeit</b> ist etwa die Hälfte übrig, nach zwei ein Viertel, dann ein Achtel. Mach die Halbwertszeit länger oder kürzer.</p>
  <div class="ctl"><label for="hl-th">Halbwertszeit (Sekunden)</label><input id="hl-th" type="range" data-bind="Th" data-instant min="1" max="8" step="0.5" value="3"><output data-show="Th" data-fmt="1"></output></div>
  <div class="btns"><button class="btn ghost" data-act="refill">Neue Probe</button></div>
</div>
<div class="step">
  <h3>Kerne haben kein Gedächtnis</h3>
  <p>Verfolge einen Überlebenden. Egal wie lange er schon durchgehalten hat, seine Chance, eine weitere Halbwertszeit zu überstehen, bleibt eins zu zwei: Ein Kern altert nicht.</p>
  <div class="btns"><button class="btn ghost" data-act="tag">Einen anderen verfolgen</button><button class="btn ghost" data-act="refill">Neue Probe</button></div>
</div>
<div class="step">
  <h3>Echte Halbwertszeiten</h3>
  <p>Echte Isotope reichen von Tagen bis zu Milliarden Jahren. Auf dieser gestauchten Zeitachse stürzt jedes bei seiner eigenen Halbwertszeit eine Klippe hinab. Wähle eines und ziehe die Zeit nach vorn.</p>
  <div class="btns"><button class="btn ghost" data-act="iso0" aria-pressed="false">Iod-131</button><button class="btn ghost" data-act="iso1" aria-pressed="true">Cäsium-137</button><button class="btn ghost" data-act="iso2" aria-pressed="false">Kohlenstoff-14</button><button class="btn ghost" data-act="iso3" aria-pressed="false">Uran-238</button></div>
  <div class="ctl"><label for="hl-t1">Vergangene Zeit</label><input id="hl-t1" type="range" data-bind="lt" data-instant min="3" max="17.8" step="0.02" value="8.98"><output class="hl-tout"></output></div>
</div>
<div class="step">
  <h3>Aktivität: Zerfälle pro Sekunde</h3>
  <p>Je ein Gramm, nebeneinander. Eine kurze Halbwertszeit bedeutet viele Zerfälle pro Sekunde, aber nicht lange; eine lange Halbwertszeit glimmt schwach über Zeitalter. Ziehe die Zeit und sieh zu, wie die Lampen eine nach der anderen erlöschen.</p>
  <div class="ctl"><label for="hl-t2">Vergangene Zeit</label><input id="hl-t2" type="range" data-bind="lt" data-instant min="3" max="17.8" step="0.02" value="4.94"><output class="hl-tout"></output></div>
</div>`,
};

Object.assign(WT.L.labels, {
  "survived {#} half-lives": "{#} Halbwertszeiten überlebt",
  "chance to last one more: {#} in {#}": "Chance auf eine weitere: {#} zu {#}",
  "survived {#} half-lives · still {#} in {#}": "{#} Halbwertszeiten überlebt · weiter {#} zu {#}",
  "it popped: follow another": "zerfallen: verfolge einen anderen",
  "{#} of {#} still unstable": "{#} von {#} noch instabil",
  "{#} half-life": "{#} Halbwertszeit",
  "half-lives →": "Halbwertszeiten →",
  "nuclei left": "verbliebene Kerne",
  "{#} of {#} left · half-life {#} s": "{#} von {#} übrig · Halbwertszeit {#} s",
  "every survivor has the same {#}-in{#} chance per half-life": "jeder Überlebende hat pro Halbwertszeit dieselbe Chance von {#} zu {#}",
  "illustrative half-life": "Halbwertszeit zur Veranschaulichung",
  "{#} hour": "{#} Stunde",
  "{#} h": "{#} h",
  "{#} day": "{#} Tag",
  "{#} d": "{#} d",
  "{#} year": "{#} Jahr",
  "{#} yr": "{#} a",
  "{#} years": "{#} Jahre",
  "{#}³ yr": "{#}³ a",
  "{#}⁶ yr": "{#}⁶ a",
  "{#}⁹ yr": "{#}⁹ a",
  "{#} million years": "{#} Millionen Jahre",
  "{#} billion years": "{#} Milliarden Jahre",
  "drag": "ziehen",
  "iodine{#} · half-life {#} days": "Iod{#} · Halbwertszeit {#} Tage",
  "caesium{#} · half-life {#} years": "Cäsium{#} · Halbwertszeit {#} Jahre",
  "carbon{#} · half-life {#} years": "Kohlenstoff{#} · Halbwertszeit {#} Jahre",
  "uranium{#} · half-life {#} billion years": "Uran{#} · Halbwertszeit {#} Milliarden Jahre",
  "medicine, fission product": "Medizin, Spaltprodukt",
  "fission product": "Spaltprodukt",
  "radiocarbon dating": "Radiokarbondatierung",
  "natural uranium": "Natururan",
  "all": "alle",
  "{#} % left after {#} minutes": "{#} % übrig nach {#} Minuten",
  "{#} % left after {#} hours": "{#} % übrig nach {#} Stunden",
  "{#} % left after {#} days": "{#} % übrig nach {#} Tagen",
  "{#} % left after {#} months": "{#} % übrig nach {#} Monaten",
  "{#} % left after {#} years": "{#} % übrig nach {#} Jahren",
  "{#} % left after {#} thousand years": "{#} % übrig nach {#} Tausend Jahren",
  "{#} % left after {#} million years": "{#} % übrig nach {#} Millionen Jahren",
  "{#} % left after {#} billion years": "{#} % übrig nach {#} Milliarden Jahren",
  "under {#} % left after {#} minutes": "unter {#} % übrig nach {#} Minuten",
  "under {#} % left after {#} hours": "unter {#} % übrig nach {#} Stunden",
  "under {#} % left after {#} days": "unter {#} % übrig nach {#} Tagen",
  "under {#} % left after {#} months": "unter {#} % übrig nach {#} Monaten",
  "under {#} % left after {#} years": "unter {#} % übrig nach {#} Jahren",
  "under {#} % left after {#} thousand years": "unter {#} % übrig nach {#} Tausend Jahren",
  "under {#} % left after {#} million years": "unter {#} % übrig nach {#} Millionen Jahren",
  "under {#} % left after {#} billion years": "unter {#} % übrig nach {#} Milliarden Jahren",
  "iodine{#}": "Iod{#}",
  "caesium{#}": "Cäsium{#}",
  "carbon{#}": "Kohlenstoff{#}",
  "uranium{#}": "Uran{#}",
  "½ {#} days": "½ {#} Tage",
  "½ {#} years": "½ {#} Jahre",
  "½ {#} billion years": "½ {#} Milliarden Jahre",
  "½ {#} bn years": "½ {#} Mrd. Jahre",
  "almost none": "fast keine",
  "{#} /s": "{#} /s",
  "~{#} /s": "~{#} /s",
  "pops per second (log)": "Zerfälle pro Sekunde (log)",
  "pops per second, {#} gram (each line ×{#})": "Zerfälle pro Sekunde, {#} Gramm (jede Linie ×{#})",
  "one gram of each, after {#} minutes": "je ein Gramm, nach {#} Minuten",
  "one gram of each, after {#} hours": "je ein Gramm, nach {#} Stunden",
  "one gram of each, after {#} days": "je ein Gramm, nach {#} Tagen",
  "one gram of each, after {#} months": "je ein Gramm, nach {#} Monaten",
  "one gram of each, after {#} years": "je ein Gramm, nach {#} Jahren",
  "one gram of each, after {#} thousand years": "je ein Gramm, nach {#} Tausend Jahren",
  "one gram of each, after {#} million years": "je ein Gramm, nach {#} Millionen Jahren",
  "one gram of each, after {#} billion years": "je ein Gramm, nach {#} Milliarden Jahren",
});
