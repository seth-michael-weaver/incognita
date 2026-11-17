/* Dutch: kcalc (Computing criticality) */
WT.L.ch.kcalc = {
  num: "Les 1", title: "Kritikaliteit berekenen", short: "k berekenen",
  html: `
<div class="step">
  <h3>De benchmarks</h3>
  <p>Vier snelle metalen kritische opstellingen uit het ICSBEP, op schaal. Godiva en Jezebel zijn kale bollen; Flattop-25 en Flattop-Pu hebben een reflector van natuurlijk uranium.</p>
</div>
<div class="step">
  <h3>Berekende <i>k</i><sub>eff</sub></h3>
  <p>OpenMC, continue energie, 3-D-geometrie. Alle vier liggen binnen ±1σ van de benchmark. <i>k</i><sub>eff</sub> wordt niet in de fit gebruikt.</p>
</div>
<div class="step">
  <h3>Gevoeligheidsprofielen</h3>
  <p>Geadjungeerde gevoeligheid van <i>k</i><sub>eff</sub> voor elke reactie, per eenheid lethargie.</p>
  <div class="btns"><button class="btn ghost" data-act="se0" aria-pressed="true">Godiva</button><button class="btn ghost" data-act="se1" aria-pressed="false">Jezebel</button><button class="btn ghost" data-act="se2" aria-pressed="false">Flattop-Pu</button></div>
</div>
<div class="step">
  <h3>Gecontroleerd met directe verstoring</h3>
  <p>Voorspelde tegen opnieuw berekende veranderingen van <i>k</i><sub>eff</sub>, 63 verstoorde datasets.</p>
</div>
<div class="step">
  <h3>Reactorkern C5G7</h3>
  <p>OECD/NEA C5G7-kwartkern, 1056 UO<sub>2</sub>- en MOX-staven: in 2-D en in de 3-D-uitbreiding met ingeschoven regelstaven. <i>k</i><sub>eff</sub> binnen 19&nbsp;pcm van de referentie in 2-D en binnen 9&nbsp;pcm in elke 3-D-configuratie.</p>
  <div class="btns"><button class="btn ghost" data-act="c50" aria-pressed="true">2-D</button><button class="btn ghost" data-act="c51" aria-pressed="false">3-D</button><button class="btn ghost" data-act="c52" aria-pressed="false">Staven A</button><button class="btn ghost" data-act="c53" aria-pressed="false">Staven B</button></div>
</div>`,
};

Object.assign(WT.L.labels, {
  "{#} pcm  (±{#} benchmark)": "{#} pcm  (benchmark ±{#})",
  "+{#} pcm  (±{#} benchmark)": "+{#} pcm  (benchmark ±{#})",
  "Calculated − experimental k, with the benchmark ±{#}σ band": "Berekende − experimentele k, met de ±{#}σ-band van de benchmark",
  "Drag to rotate": "Sleep om te draaien",
  "Godiva, integral sensitivity: ν {#}, fission {#} (% k per % change)": "Godiva, integrale gevoeligheid: ν {#}, splijting {#} (% k per % verandering)",
  "Jezebel, integral sensitivity: ν {#}, fission {#} (% k per % change)": "Jezebel, integrale gevoeligheid: ν {#}, splijting {#} (% k per % verandering)",
  "Flattop-Pu, integral sensitivity: ν {#}, fission {#} (% k per % change)": "Flattop-Pu, integrale gevoeligheid: ν {#}, splijting {#} (% k per % verandering)",
  "Godiva: ν {#}, fission {#}": "Godiva: ν {#}, splijting {#}",
  "Jezebel: ν {#}, fission {#}": "Jezebel: ν {#}, splijting {#}",
  "Flattop-Pu: ν {#}, fission {#}": "Flattop-Pu: ν {#}, splijting {#}",
  "UO₂: {#} × mean": "UO₂: {#} × gemiddelde",
  "MOX {#} %: {#} × mean": "MOX {#} %: {#} × gemiddelde",
  "OpenMC re-solve, Δk (pcm)": "OpenMC opnieuw berekend, Δk (pcm)",
  "Predicted from sensitivities, Δk (pcm)": "Voorspeld uit gevoeligheden, Δk (pcm)",
  "predicted Δk, pcm": "voorspelde Δk, pcm",
  "U{#} capture": "U{#} vangst",
  "Pu{#} capture": "Pu{#} vangst",
  "U{#} elastic": "U{#} elastisch",
  "Pu{#} elastic": "Pu{#} elastisch",
  "U{#} fission": "U{#} splijting",
  "Pu{#} fission": "Pu{#} splijting",
  "U{#} inelastic": "U{#} inelastisch",
  "Pu{#} inelastic": "Pu{#} inelastisch",
  "U{#} neutrons per fission (ν)": "U{#} neutronen per splijting (ν)",
  "Pu{#} neutrons per fission (ν)": "Pu{#} neutronen per splijting (ν)",
  "Relative pin power (hover a pin)": "Relatief staafvermogen (wijs een staaf aan)",
  "Relative pin power (tap a pin)": "Relatief staafvermogen (tik op een staaf)",
  "To scale.": "Op schaal.",
  "To scale. Drag to rotate.": "Op schaal. Sleep om te draaien.",
  "core {#} cm, reflector {#} cm": "kern {#} cm, reflector {#} cm",
  "radius {#} cm": "straal {#} cm",
  "{#} cm in {#} cm": "{#} cm in {#} cm",
  "k = {#}; reference {#} ({#} pcm)": "k = {#}; referentie {#} ({#} pcm)",
  "k = {#}; reference {#} (+{#} pcm)": "k = {#}; referentie {#} (+{#} pcm)",
  "k {#}, reference {#}": "k {#}, referentie {#}",
  "plutonium in natural uranium": "plutonium in natuurlijk uranium",
  "plutonium metal": "plutoniummetaal",
  "uranium{#} in natural uranium": "uranium{#} in natuurlijk uranium",
  "uranium{#} metal": "uranium{#}-metaal",
  "water": "water",
  "×{#} of mean": "×{#} van het gemiddelde",
  "U{#} ν": "U{#} ν",
  "Pu{#} ν": "Pu{#} ν",
  "Godiva   k = {#}": "Godiva   k = {#}",
  "Godiva {#}": "Godiva {#}",
  "Godiva: rms {#} pcm": "Godiva: rms {#} pcm",
  "Jezebel   k = {#}": "Jezebel   k = {#}",
  "Jezebel {#}": "Jezebel {#}",
  "Jezebel: rms {#} pcm": "Jezebel: rms {#} pcm",
  "Flattop-Pu   k = {#}": "Flattop-Pu   k = {#}",
  "Flattop-Pu {#}": "Flattop-Pu {#}",
  "Flattop-Pu: rms {#} pcm": "Flattop-Pu: rms {#} pcm",
  "Flattop{#}   k = {#}": "Flattop{#}   k = {#}",
  "Flattop{#} {#}": "Flattop{#} {#}",
  "{#} pcm (±{#})": "{#} pcm (±{#})",
  "+{#} pcm (±{#})": "+{#} pcm (±{#})",
  "{#} cm": "{#} cm",
  "{#} keV": "{#} keV",
  "{#} MeV": "{#} MeV",
  "OpenMC Δk": "OpenMC Δk"
});
