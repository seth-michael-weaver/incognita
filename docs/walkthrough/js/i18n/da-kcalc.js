/* Danish: kcalc (Computing criticality) */
WT.L.ch.kcalc = {
  num: "Lektion 1", title: "Beregning af kritikalitet", short: "Beregning af k",
  html: `
<div class="step">
  <h3>Benchmarkene</h3>
  <p>Fire hurtige metalliske kritiske opstillinger fra ICSBEP, i skala. Godiva og Jezebel er nøgne kugler; Flattop-25 og Flattop-Pu har en reflektor af naturligt uran.</p>
</div>
<div class="step">
  <h3>Beregnet <i>k</i><sub>eff</sub></h3>
  <p>OpenMC, kontinuerlig energi, 3-D-geometri. Alle fire ligger inden for benchmarkens ±1σ. <i>k</i><sub>eff</sub> bruges ikke i tilpasningen.</p>
</div>
<div class="step">
  <h3>Følsomhedsprofiler</h3>
  <p>Adjungeret følsomhed af <i>k</i><sub>eff</sub> for hver reaktion, pr. letargienhed.</p>
  <div class="btns"><button class="btn ghost" data-act="se0" aria-pressed="true">Godiva</button><button class="btn ghost" data-act="se1" aria-pressed="false">Jezebel</button><button class="btn ghost" data-act="se2" aria-pressed="false">Flattop-Pu</button></div>
</div>
<div class="step">
  <h3>Kontrolleret ved direkte perturbation</h3>
  <p>Forudsagte mod genberegnede ændringer i <i>k</i><sub>eff</sub>, 63 perturberede datasæt.</p>
</div>
<div class="step">
  <h3>Reaktorkerne C5G7</h3>
  <p>OECD/NEA C5G7-kvartkerne, 1056 UO<sub>2</sub>- og MOX-stave: i 2-D og i 3-D-udvidelsen med indskudte kontrolstave. <i>k</i><sub>eff</sub> inden for 19&nbsp;pcm af referencen i 2-D og inden for 9&nbsp;pcm i hver 3-D-konfiguration.</p>
  <div class="btns"><button class="btn ghost" data-act="c50" aria-pressed="true">2-D</button><button class="btn ghost" data-act="c51" aria-pressed="false">3-D</button><button class="btn ghost" data-act="c52" aria-pressed="false">Stave A</button><button class="btn ghost" data-act="c53" aria-pressed="false">Stave B</button></div>
</div>`,
};

Object.assign(WT.L.labels, {
  "{#} pcm  (±{#} benchmark)": "{#} pcm  (benchmark ±{#})",
  "+{#} pcm  (±{#} benchmark)": "+{#} pcm  (benchmark ±{#})",
  "Calculated − experimental k, with the benchmark ±{#}σ band": "Beregnet − eksperimentelt k, med benchmarkens ±{#}σ-bånd",
  "Drag to rotate": "Træk for at dreje",
  "Godiva, integral sensitivity: ν {#}, fission {#} (% k per % change)": "Godiva, integral følsomhed: ν {#}, fission {#} (% k pr. % ændring)",
  "Jezebel, integral sensitivity: ν {#}, fission {#} (% k per % change)": "Jezebel, integral følsomhed: ν {#}, fission {#} (% k pr. % ændring)",
  "Flattop-Pu, integral sensitivity: ν {#}, fission {#} (% k per % change)": "Flattop-Pu, integral følsomhed: ν {#}, fission {#} (% k pr. % ændring)",
  "Godiva: ν {#}, fission {#}": "Godiva: ν {#}, fission {#}",
  "Jezebel: ν {#}, fission {#}": "Jezebel: ν {#}, fission {#}",
  "Flattop-Pu: ν {#}, fission {#}": "Flattop-Pu: ν {#}, fission {#}",
  "UO₂: {#} × mean": "UO₂: {#} × middel",
  "MOX {#} %: {#} × mean": "MOX {#} %: {#} × middel",
  "OpenMC re-solve, Δk (pcm)": "OpenMC-genberegning, Δk (pcm)",
  "Predicted from sensitivities, Δk (pcm)": "Forudsagt fra følsomheder, Δk (pcm)",
  "predicted Δk, pcm": "forudsagt Δk, pcm",
  "U{#} capture": "U{#} indfangning",
  "Pu{#} capture": "Pu{#} indfangning",
  "U{#} elastic": "U{#} elastisk",
  "Pu{#} elastic": "Pu{#} elastisk",
  "U{#} fission": "U{#} fission",
  "Pu{#} fission": "Pu{#} fission",
  "U{#} inelastic": "U{#} uelastisk",
  "Pu{#} inelastic": "Pu{#} uelastisk",
  "U{#} neutrons per fission (ν)": "U{#} neutroner pr. fission (ν)",
  "Pu{#} neutrons per fission (ν)": "Pu{#} neutroner pr. fission (ν)",
  "Relative pin power (hover a pin)": "Relativ stav-effekt (peg på en stav)",
  "Relative pin power (tap a pin)": "Relativ stav-effekt (tryk på en stav)",
  "To scale.": "I skala.",
  "To scale. Drag to rotate.": "I skala. Træk for at dreje.",
  "core {#} cm, reflector {#} cm": "kerne {#} cm, reflektor {#} cm",
  "radius {#} cm": "radius {#} cm",
  "{#} cm in {#} cm": "{#} cm i {#} cm",
  "k = {#}; reference {#} ({#} pcm)": "k = {#}; reference {#} ({#} pcm)",
  "k = {#}; reference {#} (+{#} pcm)": "k = {#}; reference {#} (+{#} pcm)",
  "k {#}, reference {#}": "k {#}, reference {#}",
  "plutonium in natural uranium": "plutonium i naturligt uran",
  "plutonium metal": "plutoniummetal",
  "uranium{#} in natural uranium": "uran{#} i naturligt uran",
  "uranium{#} metal": "uran{#}-metal",
  "water": "vand",
  "×{#} of mean": "×{#} af middel",
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
