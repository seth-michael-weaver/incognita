/* German (Deutsch): everyday (Kernphysik im Alltag) */
WT.L.ch.everyday = {
  num: "Lektion 4", title: "Kernphysik im Alltag", short: "Alltag",
  html: `
<div class="step">
  <h3>PET-Scans</h3>
  <p>Ein Fluor-18-Tracer (Halbwertszeit 110 Minuten) sendet Positronen aus, und jedes wird zu zwei 511-keV-Gammaquanten, die genau entgegengesetzt davonfliegen. Zieh den heißen Fleck: Der Ring zieht für jedes Paar eine Linie, und die Linien kreuzen sich dort, wo der Tracer ist.</p>
</div>
<div class="step">
  <h3>Strahlentherapie</h3>
  <p>Strahlen aus mehreren Richtungen überlagern sich im Tumor, sodass er die volle Dosis erhält, während jeder Weg durch gesundes Gewebe nur einen Teil abbekommt. Zieh, um die Strahlen zu drehen, und halte sie vom Rückenmark fern.</p>
  <div class="ctl"><label for="ev-n">Strahlen</label><input id="ev-n" type="range" data-bind="nb" data-instant min="1" max="7" step="1" value="5"><output data-show="nb" data-fmt="0"></output></div>
  <div class="ctl"><label for="ev-r">Drehen</label><input id="ev-r" type="range" data-bind="rotd" data-instant min="0" max="360" step="1" value="20"><output class="ev-rot"></output></div>
</div>
<div class="step">
  <h3>Technetium-99m</h3>
  <p>Das Isotop hinter den meisten nuklearmedizinischen Untersuchungen gibt ein 140-keV-Gammaquant ab, das eine Kamera außerhalb des Körpers sehen kann, und bei 6 Stunden Halbwertszeit ist nach einem Tag wenig übrig. Krankenhäuser <a href="#chains-3">melken es aus Molybdän-99</a>.</p>
  <div class="ctl"><label for="ev-t">Stunden nach der Gabe</label><input id="ev-t" type="range" data-bind="th" data-instant min="0" max="48" step="0.5" value="0"><output data-show="th" data-fmt="1"></output></div>
</div>
<div class="step">
  <h3>Radiokarbondatierung</h3>
  <p>Lebewesen nehmen ständig Kohlenstoff-14 auf; nach dem Tod zerfällt er mit einer Halbwertszeit von 5730 Jahren. Stell das Alter ein, oder miss, was übrig ist, um das Alter abzulesen.</p>
  <div class="ctl"><label for="ev-a">Alter (Jahre)</label><input id="ev-a" type="range" data-bind="age" data-instant min="0" max="50000" step="10" value="5300"><output class="ev-age"></output></div>
  <div class="ctl"><label for="ev-f">Verbliebenes Kohlenstoff-14 (%)</label><input id="ev-f" type="range" data-bind="fr" data-instant min="0.3" max="100" step="0.1" value="52.7"><output class="ev-fr"></output></div>
</div>
<div class="step">
  <h3>Rauchmelder</h3>
  <p>Ein versiegeltes Körnchen Americium-241 schickt Alphateilchen über einen kleinen Luftspalt und erzeugt Ionen, die einen winzigen Strom tragen. Rauch fängt die Ionen ein, der Strom sinkt, und der Alarm ertönt.</p>
  <div class="ctl"><label for="ev-s">Rauch</label><input id="ev-s" type="range" data-bind="sm" data-instant min="0" max="1" step="0.01" value="0"><output class="ev-sm"></output></div>
</div>`,
};

Object.assign(WT.L.labels, {
  "{#} beams cross: the tumour gets their sum": "{#} Strahlen kreuzen sich: der Tumor erhält ihre Summe",
  "{#} h": "{#} h",
  "{#} h: {#} % left": "{#} h: {#} % übrig",
  "{#} half-lives": "{#} Halbwertszeiten",
  "{#} keV gamma rays": "{#}-keV-Gammaquanten",
  "{#} of {#} left": "{#} von {#} übrig",
  "{#} years · {#} % left": "{#} Jahre · {#} % übrig",
  "~{#} y: too little to measure": "~{#} a: zu wenig zum Messen",
  "a beam crosses the spinal cord: turn the beams": "ein Strahl kreuzt das Rückenmark: dreh die Strahlen",
  "a strong gamma signal, easy to image": "ein starkes Gammasignal, leicht abzubilden",
  "after a day, about {#} % is left": "nach einem Tag ist etwa {#} % übrig",
  "alarm": "Alarm",
  "alpha particles make ions in the air": "Alphateilchen erzeugen Ionen in der Luft",
  "Am{#}": "Am{#}",
  "americium{#} · half-life {#} years · alphas reach about {#} cm in air": "Americium{#} · Halbwertszeit {#} Jahre · Alphas fliegen etwa {#} cm weit in Luft",
  "americium{#} (sealed)": "Americium{#} (versiegelt)",
  "beyond ~{#} years too little is left to measure": "nach ~{#} Jahren ist zu wenig übrig, um es zu messen",
  "carbon{#}": "Kohlenstoff{#}",
  "clean air: steady current": "saubere Luft: gleichmäßiger Strom",
  "current": "Strom",
  "detector ring": "Detektorring",
  "dose": "Dosis",
  "each decay: two {#} keV gamma rays, back to back": "jeder Zerfall: zwei {#}-keV-Gammaquanten, entgegengesetzt",
  "fading: half is gone every {#} hours": "abklingend: alle {#} Stunden ist die Hälfte weg",
  "fluorine{#} · half-life {#} min · {#} pairs recorded": "Fluor{#} · Halbwertszeit {#} min · {#} Paare registriert",
  "gamma camera": "Gammakamera",
  "half-life {#} y": "Halbwertszeit {#} a",
  "illustration": "Illustration",
  "Mo{#} ({#} h)": "Mo{#} ({#} h)",
  "molybdenum{#}, half-life {#} h": "Molybdän{#}, Halbwertszeit {#} h",
  "nitrogen{#}": "Stickstoff{#}",
  "nitrogen{#} (after a beta decay)": "Stickstoff{#} (nach einem Betazerfall)",
  "one beam: more dose near the skin than in the tumour": "ein Strahl: mehr Dosis nahe der Haut als im Tumor",
  "Ötzi the Iceman, ~{#} y": "Ötzi, der Mann aus dem Eis, ~{#} a",
  "pairs of {#} keV gamma rays, back to back": "Paare von {#}-keV-Gammaquanten, entgegengesetzt",
  "physical decay only": "nur physikalischer Zerfall",
  "smoke: current down, alarm!": "Rauch: Strom fällt, Alarm!",
  "some ions caught: current dipping": "einige Ionen gefangen: Strom sinkt",
  "spinal cord": "Rückenmark",
  "Tc{#}m ({#} h)": "Tc{#}m ({#} h)",
  "technetium{#}m, half-life {#} h": "Technetium{#}m, Halbwertszeit {#} h",
  "tracer": "Tracer",
  "tracer (drag me)": "Tracer (zieh mich)",
  "tumour": "Tumor",
  "tumour {#} % · spinal cord {#} % · healthy tissue at most {#} %": "Tumor {#} % · Rückenmark {#} % · gesundes Gewebe höchstens {#} %",
  "tumour {#} % · spinal cord {#} % · other tissue at most {#} %": "Tumor {#} % · Rückenmark {#} % · übriges Gewebe höchstens {#} %",
  "years": "Jahre",
});
