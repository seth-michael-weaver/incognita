/* Danish (Dansk): everyday (Kernefysik i hverdagen) */
WT.L.ch.everyday = {
  num: "Lektion 4", title: "Kernefysik i hverdagen", short: "Hverdagen",
  html: `
<div class="step">
  <h3>PET-skanninger</h3>
  <p>Et fluor-18-sporstof (halveringstid 110 minutter) udsender positroner, og hver af dem bliver til to gammastråler på 511 keV, der flyver i hver sin retning. Træk i den varme plet: ringen tegner en linje for hvert par, og linjerne krydser hinanden, hvor sporstoffet er.</p>
</div>
<div class="step">
  <h3>Strålebehandling</h3>
  <p>Stråler fra flere retninger overlapper i tumoren, så den får den fulde dosis, mens hver vej gennem rask væv kun får en del. Træk for at dreje strålerne og hold dem væk fra rygmarven.</p>
  <div class="ctl"><label for="ev-n">Stråler</label><input id="ev-n" type="range" data-bind="nb" data-instant min="1" max="7" step="1" value="5"><output data-show="nb" data-fmt="0"></output></div>
  <div class="ctl"><label for="ev-r">Drej</label><input id="ev-r" type="range" data-bind="rotd" data-instant min="0" max="360" step="1" value="20"><output class="ev-rot"></output></div>
</div>
<div class="step">
  <h3>Technetium-99m</h3>
  <p>Isotopen bag de fleste nuklearmedicinske skanninger udsender en gammastråle på 140 keV, som et kamera uden for kroppen kan se, og med en halveringstid på 6 timer er der kun lidt tilbage efter et døgn. Hospitaler <a href="#chains-3">malker det fra molybdæn-99</a>.</p>
  <div class="ctl"><label for="ev-t">Timer efter dosen</label><input id="ev-t" type="range" data-bind="th" data-instant min="0" max="48" step="0.5" value="0"><output data-show="th" data-fmt="1"></output></div>
</div>
<div class="step">
  <h3>Kulstof-14-datering</h3>
  <p>Levende væsener optager hele tiden kulstof-14; efter døden henfalder det med en halveringstid på 5730 år. Indstil alderen, eller mål hvad der er tilbage for at aflæse alderen.</p>
  <div class="ctl"><label for="ev-a">Alder (år)</label><input id="ev-a" type="range" data-bind="age" data-instant min="0" max="50000" step="10" value="5300"><output class="ev-age"></output></div>
  <div class="ctl"><label for="ev-f">Tilbageværende kulstof-14 (%)</label><input id="ev-f" type="range" data-bind="fr" data-instant min="0.3" max="100" step="0.1" value="52.7"><output class="ev-fr"></output></div>
</div>
<div class="step">
  <h3>Røgalarmer</h3>
  <p>Et forseglet gran americium-241 sender alfapartikler over en lille luftspalte og danner ioner, der bærer en lillebitte strøm. Røg fanger ionerne, strømmen falder, og alarmen lyder.</p>
  <div class="ctl"><label for="ev-s">Røg</label><input id="ev-s" type="range" data-bind="sm" data-instant min="0" max="1" step="0.01" value="0"><output class="ev-sm"></output></div>
</div>`,
};

Object.assign(WT.L.labels, {
  "{#} beams cross: the tumour gets their sum": "{#} stråler krydser: tumoren får deres sum",
  "{#} h": "{#} t",
  "{#} h: {#} % left": "{#} t: {#} % tilbage",
  "{#} half-lives": "{#} halveringstider",
  "{#} keV gamma rays": "gammastråler på {#} keV",
  "{#} of {#} left": "{#} af {#} tilbage",
  "{#} years · {#} % left": "{#} år · {#} % tilbage",
  "~{#} y: too little to measure": "~{#} år: for lidt at måle",
  "a beam crosses the spinal cord: turn the beams": "en stråle krydser rygmarven: drej strålerne",
  "a strong gamma signal, easy to image": "et stærkt gammasignal, let at afbilde",
  "after a day, about {#} % is left": "efter et døgn er der omkring {#} % tilbage",
  "alarm": "alarm",
  "alpha particles make ions in the air": "alfapartikler danner ioner i luften",
  "Am{#}": "Am{#}",
  "americium{#} · half-life {#} years · alphas reach about {#} cm in air": "americium{#} · halveringstid {#} år · alfaer når omkring {#} cm i luft",
  "americium{#} (sealed)": "americium{#} (forseglet)",
  "beyond ~{#} years too little is left to measure": "efter ~{#} år er der for lidt tilbage at måle",
  "carbon{#}": "kulstof{#}",
  "clean air: steady current": "ren luft: jævn strøm",
  "current": "strøm",
  "detector ring": "detektorring",
  "dose": "dosis",
  "each decay: two {#} keV gamma rays, back to back": "hvert henfald: to gammastråler på {#} keV, modsatrettede",
  "fading: half is gone every {#} hours": "aftagende: halvdelen er væk hver {#}. time",
  "fluorine{#} · half-life {#} min · {#} pairs recorded": "fluor{#} · halveringstid {#} min · {#} par registreret",
  "gamma camera": "gammakamera",
  "half-life {#} y": "halveringstid {#} år",
  "illustration": "illustration",
  "Mo{#} ({#} h)": "Mo{#} ({#} t)",
  "molybdenum{#}, half-life {#} h": "molybdæn{#}, halveringstid {#} t",
  "nitrogen{#}": "kvælstof{#}",
  "nitrogen{#} (after a beta decay)": "kvælstof{#} (efter et betahenfald)",
  "one beam: more dose near the skin than in the tumour": "én stråle: mere dosis ved huden end i tumoren",
  "Ötzi the Iceman, ~{#} y": "Ötzi, ismanden, ~{#} år",
  "pairs of {#} keV gamma rays, back to back": "par af gammastråler på {#} keV, modsatrettede",
  "physical decay only": "kun fysisk henfald",
  "smoke: current down, alarm!": "røg: strømmen falder, alarm!",
  "some ions caught: current dipping": "nogle ioner fanget: strømmen dykker",
  "spinal cord": "rygmarv",
  "Tc{#}m ({#} h)": "Tc{#}m ({#} t)",
  "technetium{#}m, half-life {#} h": "technetium{#}m, halveringstid {#} t",
  "tracer": "sporstof",
  "tracer (drag me)": "sporstof (træk i mig)",
  "tumour": "tumor",
  "tumour {#} % · spinal cord {#} % · healthy tissue at most {#} %": "tumor {#} % · rygmarv {#} % · rask væv højst {#} %",
  "tumour {#} % · spinal cord {#} % · other tissue at most {#} %": "tumor {#} % · rygmarv {#} % · andet væv højst {#} %",
  "years": "år",
});
