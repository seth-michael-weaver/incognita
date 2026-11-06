/* German (Deutsch): transport (Neutronentransport und Monte Carlo) */
WT.L.ch.transport = {
  num: "Lektion 16", title: "Neutronentransport und Monte Carlo", short: "Monte Carlo",
  html: `
<div class="step">
  <h3>Die Transportgleichung</h3>
  <p>Exakt gehorchen die Neutronen der Boltzmann-Gleichung für den Winkelfluss <i>ψ</i>(<b>r</b>, <b>Ω</b>, <i>E</i>): <b>Ω</b>·∇<i>ψ</i> + Σ<sub>t</sub><i>ψ</i> = ∫∫Σ<sub>s</sub><i>ψ</i>′ d<b>Ω</b>′d<i>E</i>′ + (<i>χ</i>/4π<i>k</i>)∫<i>ν</i>Σ<sub>f</sub><i>φ</i>′ d<i>E</i>′. Monte Carlo löst sie, indem es Neutronen einzeln durchspielt: fliege <i>s</i> = −ln <i>ξ</i> / Σ<sub>t</sub>, dann streue, werde eingefangen oder löse eine Spaltung aus.</p>
  <div class="btns"><button class="btn" data-act="trnew">Neues Neutron</button></div>
</div>
<div class="step">
  <h3>Wo die Diffusion versagt</h3>
  <p>Die Diffusion nimmt in jeder Richtung nahezu denselben Fluss an. Das versagt innerhalb von ein, zwei freien Weglängen von einer Oberfläche und in starken Absorbern. Vergleiche sie mit dem Monte-Carlo-Fluss in einer Platte mit gleichmäßiger Quelle, während du die Absorption erhöhst.</p>
  <div class="ctl"><label for="tr-pa">Absorption Σ<sub>a</sub>/Σ<sub>t</sub></label><input id="tr-pa" type="range" data-bind="pa" data-instant min="0.05" max="0.8" step="0.05" value="0.5"><output data-show="pa" data-fmt="2"></output></div>
</div>
<div class="step">
  <h3>Potenziteration</h3>
  <p>Für <i>k</i><sub>eff</sub> werden die Spaltorte jeder Generation zur Quelle der nächsten; <i>k</i> ist die Zahl der gespeicherten Orte pro gestartetem Neutron. Beginne mit einer schlechten Schätzung, jedes Neutron an einem Rand, und sieh zu, wie sich die Quelle zur Grundmode ausbreitet.</p>
  <div class="btns"><button class="btn" data-act="trbad">Mit schlechter Schätzung neu starten</button></div>
</div>
<div class="step">
  <h3>Ist die Quelle konvergiert?</h3>
  <p>Die Shannon-Entropie <i>H</i> = −Σ <i>p</i><sub>b</sub> log<sub>2</sub> <i>p</i><sub>b</sub> der in Klassen eingeteilten Quelle flacht ab, sobald sich die Quelle eingependelt hat; erst dann werden Generationen gemittelt. Der Fehlerbalken von <i>k</i> schrumpft wie 1/√<i>N</i> mit der Zahl der gezählten Historien.</p>
  <div class="ctl"><label for="tr-n">Historien pro Generation</label><input id="tr-n" type="range" data-bind="nh" data-instant min="100" max="2000" step="100" value="400"><output data-show="nh" data-fmt="0"></output></div>
</div>`,
};

Object.assign(WT.L.labels, {
  "vacuum": "Vakuum",
  "tap the slab to start neutrons": "tippe die Platte an, um Neutronen zu starten",
  "chance to fly at least s:  e^(−Σₜ s)": "Chance, mindestens s zu fliegen:  e^(−Σₜ s)",
  "infinite medium S/Σₐ": "unendliches Medium S/Σₐ",
  "Monte Carlo": "Monte Carlo",
  "diffusion": "Diffusion",
  "flux": "Fluss",
  "source entropy H (bits)": "Quellentropie H (Bit)",
  "k per generation": "k pro Generation",
  "illustrative one-group data": "Ein-Gruppen-Daten zur Veranschaulichung",
  "scatter": "Streuung",
  "capture": "Einfang",
  "fission": "Spaltung",
  "leak": "Leckage",
  "glow: collision density": "Leuchten: Stoßdichte",
  "amber glow: where collisions pile up": "bernsteinfarbenes Leuchten: wo sich Stöße häufen",
  "{#} free paths": "{#} freie Weglängen",
  "ξ = {#}  →  s = −ln ξ / Σₜ = {#} free paths": "ξ = {#}  →  s = −ln ξ / Σₜ = {#} freie Weglängen",
  "diffusion vs Monte Carlo: +{#} % at the surface, +{#} % in the middle": "Diffusion vs. Monte Carlo: +{#} % an der Oberfläche, +{#} % in der Mitte",
  "diffusion vs Monte Carlo: +{#} % at the surface, {#} % in the middle": "Diffusion vs. Monte Carlo: +{#} % an der Oberfläche, {#} % in der Mitte",
  "diffusion vs Monte Carlo: {#} % at the surface, +{#} % in the middle": "Diffusion vs. Monte Carlo: {#} % an der Oberfläche, +{#} % in der Mitte",
  "diffusion vs Monte Carlo: {#} % at the surface, {#} % in the middle": "Diffusion vs. Monte Carlo: {#} % an der Oberfläche, {#} % in der Mitte",
  "tap: drop the source there": "tippen: Quelle dorthin setzen",
  "tap the slab to drop the whole source there": "tippe die Platte an, um die ganze Quelle dorthin zu setzen",
  "generation {#}": "Generation {#}",
  "source · dashed: fundamental mode": "Quelle · gestrichelt: Grundmode",
  "fission source · dashed: fundamental mode": "Spaltquelle · gestrichelt: Grundmode",
  "inactive | active": "inaktiv | aktiv",
  "inactive  |  active generations": "inaktive  |  aktive Generationen",
  "generation {#}: k = {#} · H = {#} bits": "Generation {#}: k = {#} · H = {#} Bit",
  "starting…": "startet …",
  "k_eff = {#} ± {#} ({#} × {#} histories) · diffusion {#}": "k_eff = {#} ± {#} ({#} × {#} Historien) · Diffusion {#}",
  "{#} generations, averaging starts after {#}": "{#} Generationen, Mittelung beginnt nach {#}",
});
