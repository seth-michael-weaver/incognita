/* Italian (Italiano): everyday (Il nucleare nella vita di tutti i giorni) */
WT.L.ch.everyday = {
  num: "Lezione 4", title: "Il nucleare nella vita di tutti i giorni", short: "Vita quotidiana",
  html: `
<div class="step">
  <h3>PET</h3>
  <p>Un tracciante al fluoro-18 (tempo di dimezzamento 110 minuti) emette positroni, e ciascuno diventa due raggi gamma da 511 keV che partono in versi opposti. Trascina il punto caldo: l'anello traccia una linea per ogni coppia, e le linee si incrociano dove si trova il tracciante.</p>
</div>
<div class="step">
  <h3>Radioterapia</h3>
  <p>Fasci da più direzioni si sovrappongono sul tumore, che riceve così la dose piena mentre ogni percorso nel tessuto sano ne riceve solo una parte. Trascina per ruotare i fasci e tenerli lontani dal midollo spinale.</p>
  <div class="ctl"><label for="ev-n">Fasci</label><input id="ev-n" type="range" data-bind="nb" data-instant min="1" max="7" step="1" value="5"><output data-show="nb" data-fmt="0"></output></div>
  <div class="ctl"><label for="ev-r">Rotazione</label><input id="ev-r" type="range" data-bind="rotd" data-instant min="0" max="360" step="1" value="20"><output class="ev-rot"></output></div>
</div>
<div class="step">
  <h3>Tecnezio-99m</h3>
  <p>L'isotopo della maggior parte degli esami di medicina nucleare emette un raggio gamma da 140 keV che una camera fuori dal corpo può vedere, e con un tempo di dimezzamento di 6 ore dopo un giorno ne resta poco. Gli ospedali <a href="#chains-3">lo mungono dal molibdeno-99</a>.</p>
  <div class="ctl"><label for="ev-t">Ore dopo la somministrazione</label><input id="ev-t" type="range" data-bind="th" data-instant min="0" max="48" step="0.5" value="0"><output data-show="th" data-fmt="1"></output></div>
</div>
<div class="step">
  <h3>Datazione al carbonio</h3>
  <p>Gli esseri viventi assorbono di continuo carbonio-14; dopo la morte decade con un tempo di dimezzamento di 5730 anni. Imposta l'età, oppure misura quanto ne resta per leggere l'età.</p>
  <div class="ctl"><label for="ev-a">Età (anni)</label><input id="ev-a" type="range" data-bind="age" data-instant min="0" max="50000" step="10" value="5300"><output class="ev-age"></output></div>
  <div class="ctl"><label for="ev-f">Carbonio-14 rimasto (%)</label><input id="ev-f" type="range" data-bind="fr" data-instant min="0.3" max="100" step="0.1" value="52.7"><output class="ev-fr"></output></div>
</div>
<div class="step">
  <h3>Rivelatori di fumo</h3>
  <p>Un granello sigillato di americio-241 lancia particelle alfa attraverso una piccola intercapedine d'aria, creando ioni che portano una corrente minuscola. Il fumo cattura gli ioni, la corrente cala e scatta l'allarme.</p>
  <div class="ctl"><label for="ev-s">Fumo</label><input id="ev-s" type="range" data-bind="sm" data-instant min="0" max="1" step="0.01" value="0"><output class="ev-sm"></output></div>
</div>`,
};

Object.assign(WT.L.labels, {
  "{#} beams cross: the tumour gets their sum": "{#} fasci si incrociano: il tumore riceve la loro somma",
  "{#} h": "{#} h",
  "{#} h: {#} % left": "{#} h: resta il {#} %",
  "{#} half-lives": "{#} tempi di dimezzamento",
  "{#} keV gamma rays": "raggi gamma da {#} keV",
  "{#} of {#} left": "ne restano {#} su {#}",
  "{#} years · {#} % left": "{#} anni · resta il {#} %",
  "~{#} y: too little to measure": "~{#} anni: troppo poco da misurare",
  "a beam crosses the spinal cord: turn the beams": "un fascio attraversa il midollo: ruota i fasci",
  "a strong gamma signal, easy to image": "un segnale gamma intenso, facile da visualizzare",
  "after a day, about {#} % is left": "dopo un giorno ne resta circa il {#} %",
  "alarm": "allarme",
  "alpha particles make ions in the air": "le particelle alfa creano ioni nell'aria",
  "Am{#}": "Am{#}",
  "americium{#} · half-life {#} years · alphas reach about {#} cm in air": "americio{#} · dimezzamento {#} anni · le alfa percorrono circa {#} cm in aria",
  "americium{#} (sealed)": "americio{#} (sigillato)",
  "beyond ~{#} years too little is left to measure": "oltre ~{#} anni ne resta troppo poco da misurare",
  "carbon{#}": "carbonio{#}",
  "clean air: steady current": "aria pulita: corrente stabile",
  "current": "corrente",
  "detector ring": "anello di rivelatori",
  "dose": "dose",
  "each decay: two {#} keV gamma rays, back to back": "ogni decadimento: due raggi gamma da {#} keV, in versi opposti",
  "fading: half is gone every {#} hours": "in calo: metà sparisce ogni {#} ore",
  "fluorine{#} · half-life {#} min · {#} pairs recorded": "fluoro{#} · dimezzamento {#} min · {#} coppie registrate",
  "gamma camera": "gamma camera",
  "half-life {#} y": "dimezzamento {#} anni",
  "illustration": "illustrazione",
  "Mo{#} ({#} h)": "Mo{#} ({#} h)",
  "molybdenum{#}, half-life {#} h": "molibdeno{#}, dimezzamento {#} h",
  "nitrogen{#}": "azoto{#}",
  "nitrogen{#} (after a beta decay)": "azoto{#} (dopo un decadimento beta)",
  "one beam: more dose near the skin than in the tumour": "un solo fascio: più dose vicino alla pelle che nel tumore",
  "Ötzi the Iceman, ~{#} y": "Ötzi, l'uomo venuto dal ghiaccio, ~{#} anni",
  "pairs of {#} keV gamma rays, back to back": "coppie di raggi gamma da {#} keV, in versi opposti",
  "physical decay only": "solo decadimento fisico",
  "smoke: current down, alarm!": "fumo: la corrente cala, allarme!",
  "some ions caught: current dipping": "alcuni ioni catturati: la corrente scende",
  "spinal cord": "midollo spinale",
  "Tc{#}m ({#} h)": "Tc{#}m ({#} h)",
  "technetium{#}m, half-life {#} h": "tecnezio{#}m, dimezzamento {#} h",
  "tracer": "tracciante",
  "tracer (drag me)": "tracciante (trascinami)",
  "tumour": "tumore",
  "tumour {#} % · spinal cord {#} % · healthy tissue at most {#} %": "tumore {#} % · midollo {#} % · tessuto sano al massimo {#} %",
  "tumour {#} % · spinal cord {#} % · other tissue at most {#} %": "tumore {#} % · midollo {#} % · altri tessuti al massimo {#} %",
  "years": "anni",
});
