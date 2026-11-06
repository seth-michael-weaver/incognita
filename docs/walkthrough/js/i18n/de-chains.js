/* German (Deutsch): chains (Zerfallsketten und Gleichgewicht) */
WT.L.ch.chains = {
  num: "Lektion 4", title: "Zerfallsketten und Gleichgewicht", short: "Zerfallsketten",
  html: `
<div class="step">
  <h3>Mutter, Tochter, Enkelin</h3>
  <p>Oft ist auch der neue Kern instabil. Die Mutter zerfällt in eine Tochter, die in eine stabile Enkelin zerfällt. Töchter häufen sich an und verblassen dann; wie hoch sie sich anhäufen, hängt davon ab, wie schnell sie im Vergleich zur Mutter zerfallen.</p>
  <div class="ctl"><label for="ch-t2">Halbwertszeit der Tochter (s)</label><input id="ch-t2" type="range" data-bind="T2" data-instant min="0.5" max="9" step="0.5" value="1.5"><output data-show="T2" data-fmt="1"></output></div>
  <div class="btns"><button class="btn ghost" data-act="refill">Neue Probe</button></div>
</div>
<div class="step">
  <h3>Säkulares Gleichgewicht: Radium und Radon</h3>
  <p>Radium-226 hält 1600 Jahre; seine Tochter, das Gas Radon-222, nur 3,8 Tage. In einem verschlossenen Gefäß sammelt sich das Radon an, bis es so schnell zerfällt, wie es entsteht: <i>A</i><sub>Rn</sub> = <i>A</i><sub>Ra</sub>(1 − e<sup>−λt</sup>), mit λ der Zerfallskonstante des Radons. Nach ein paar Wochen zerfallen beide gleich schnell.</p>
  <div class="btns"><button class="btn" data-act="vent">Gefäß öffnen</button></div>
</div>
<div class="step">
  <h3>Transientes Gleichgewicht: die Technetium-Kuh</h3>
  <p>Krankenhäuser bekommen eine Säule mit Molybdän-99 (66 Stunden), die ständig Technetium-99m (6 Stunden) nachbildet, den meistgenutzten medizinischen Tracer. Spült man das Technetium jeden Morgen heraus, wächst es wieder nach und folgt dem langsam abklingenden Molybdän.</p>
  <div class="btns"><button class="btn" data-act="milk">Generator melken</button><button class="btn ghost" data-act="genre">Neuer Generator</button></div>
</div>
<div class="step">
  <h3>Die Uran-Zerfallsreihe hinab</h3>
  <p>Uran-238 braucht vierzehn Schritte, bis es zu stabilem Blei wird. Ein Alphazerfall führt auf dieser Karte zwei Schritte nach unten und zwei nach links, ein Betazerfall einen nach oben und einen nach links. In altem, ungestörtem Uranerz zerfällt jedes Glied gleich schnell.</p>
  <div class="btns"><button class="btn" data-act="next">Nächster Zerfall</button><button class="btn ghost" data-act="restart">Neu beginnen</button></div>
</div>`,
};

Object.assign(WT.L.labels, {
  "A(Rn) = A(Ra) × ({#} − exp(−λt))": "A(Rn) = A(Ra) × ({#} − exp(−λt))",
  "A(radon) = A(radium) × ({#} − exp(−λt))": "A(Radon) = A(Radium) × ({#} − exp(−λt))",
  "Bi{#} · half-life {#} days · beta next": "Bi{#} · Halbwertszeit {#} Tage · als Nächstes Beta",
  "Bi{#} · half-life {#} min · beta next": "Bi{#} · Halbwertszeit {#} min · als Nächstes Beta",
  "Pa{#}m · half-life {#} min · beta next": "Pa{#}m · Halbwertszeit {#} min · als Nächstes Beta",
  "Pb{#} · half-life {#} min · beta next": "Pb{#} · Halbwertszeit {#} min · als Nächstes Beta",
  "Pb{#} · half-life {#} years · beta next": "Pb{#} · Halbwertszeit {#} Jahre · als Nächstes Beta",
  "Po{#} · half-life {#} days · alpha next": "Po{#} · Halbwertszeit {#} Tage · als Nächstes Alpha",
  "Po{#} · half-life {#} min · alpha next": "Po{#} · Halbwertszeit {#} min · als Nächstes Alpha",
  "Po{#} · half-life {#} µs · alpha next": "Po{#} · Halbwertszeit {#} µs · als Nächstes Alpha",
  "Ra{#} · half-life {#} yr · alpha next": "Ra{#} · Halbwertszeit {#} a · als Nächstes Alpha",
  "Rn{#} · half-life {#} days · alpha next": "Rn{#} · Halbwertszeit {#} Tage · als Nächstes Alpha",
  "Tc{#}m out": "Tc{#}m entnommen",
  "Tc{#}m to the patient": "Tc{#}m zum Patienten",
  "Th{#} · half-life {#} days · beta next": "Th{#} · Halbwertszeit {#} Tage · als Nächstes Beta",
  "Th{#} · half-life {#} yr · alpha next": "Th{#} · Halbwertszeit {#} a · als Nächstes Alpha",
  "U{#} · half-life {#} billion yr · alpha next": "U{#} · Halbwertszeit {#} Mrd. a · als Nächstes Alpha",
  "U{#} · half-life {#} yr · alpha next": "U{#} · Halbwertszeit {#} a · als Nächstes Alpha",
  "activity": "Aktivität",
  "alpha: loses {#} protons and {#} neutrons": "Alpha: verliert {#} Protonen und {#} Neutronen",
  "alpha: {#} p, {#} n": "Alpha: {#} p, {#} n",
  "beta: a neutron becomes a proton": "Beta: ein Neutron wird zum Proton",
  "beta: n → p": "Beta: n → p",
  "dashed: never milked": "gestrichelt: nie gemolken",
  "daughter ({#} s): {#}": "Tochter ({#} s): {#}",
  "daughter peaks: {#} %": "Maximum der Tochter: {#} %",
  "daughter {#}": "Tochter {#}",
  "day {#}: radon at {#} % of radium": "Tag {#}: Radon bei {#} % des Radiums",
  "days →": "Tage →",
  "granddaughter (stable): {#}": "Enkelin (stabil): {#}",
  "grey: stable": "grau: stabil",
  "illustrative half-lives": "Halbwertszeiten zur Veranschaulichung",
  "molybdenum{#}": "Molybdän{#}",
  "neutrons →": "Neutronen →",
  "parent ({#} s): {#}": "Mutter ({#} s): {#}",
  "parent {#}": "Mutter {#}",
  "protons ↑": "Protonen ↑",
  "radium": "Radium",
  "radium activity": "Aktivität des Radiums",
  "radium{#}": "Radium{#}",
  "radon": "Radon",
  "radon activity": "Aktivität des Radons",
  "radon{#} gas": "Radon{#}-Gas",
  "regrows to its peak in about {#} hours": "wächst in etwa {#} Stunden wieder zum Maximum",
  "stable {#}": "stabil {#}",
  "step {#} of {#} · tap the nucleus": "Schritt {#} von {#} · tippe den Kern an",
  "{#} d": "{#} d",
  "{#} h since last milking · Tc{#}m at {#} % of Mo{#}": "{#} h seit dem letzten Melken · Tc{#}m bei {#} % von Mo{#}",
  "{#} s": "{#} s",
});
