/* Italian: kcalc (Computing criticality) */
WT.L.ch.kcalc = {
  num: "Lezione 1", title: "Calcolo della criticità", short: "Calcolo di k",
  html: `
<div class="step">
  <h3>I benchmark</h3>
  <p>Quattro assemblaggi critici veloci metallici dell’ICSBEP, in scala. Godiva e Jezebel sono sfere nude; Flattop-25 e Flattop-Pu hanno un riflettore di uranio naturale.</p>
</div>
<div class="step">
  <h3><i>k</i><sub>eff</sub> calcolato</h3>
  <p>OpenMC, energia continua, geometria 3-D. Tutti e quattro rientrano nel ±1σ del benchmark. <i>k</i><sub>eff</sub> non è usato nel fit.</p>
</div>
<div class="step">
  <h3>Profili di sensibilità</h3>
  <p>Sensibilità aggiunta di <i>k</i><sub>eff</sub> a ogni reazione, per unità di letargia.</p>
  <div class="btns"><button class="btn ghost" data-act="se0" aria-pressed="true">Godiva</button><button class="btn ghost" data-act="se1" aria-pressed="false">Jezebel</button><button class="btn ghost" data-act="se2" aria-pressed="false">Flattop-Pu</button></div>
</div>
<div class="step">
  <h3>Verificato con perturbazione diretta</h3>
  <p>Variazioni di <i>k</i><sub>eff</sub> previste contro ricalcolate, 63 insiemi di dati perturbati.</p>
</div>
<div class="step">
  <h3>Nocciolo del reattore C5G7</h3>
  <p>OCSE/NEA C5G7, quarto di nocciolo 2-D, 1056 barrette di UO<sub>2</sub> e MOX. <i>k</i><sub>eff</sub> a −19&nbsp;pcm dal riferimento; errore massimo di potenza per barretta 0,13&nbsp;%.</p>
</div>`,
};

Object.assign(WT.L.labels, {
  "{#} pcm  (±{#} benchmark)": "{#} pcm  (benchmark ±{#})",
  "+{#} pcm  (±{#} benchmark)": "+{#} pcm  (benchmark ±{#})",
  "Calculated − experimental k, with the benchmark ±{#}σ band": "k calcolato − sperimentale, con la banda ±{#}σ del benchmark",
  "Drag to rotate": "Trascina per ruotare",
  "Godiva, integral sensitivity: ν {#}, fission {#} (% k per % change)": "Godiva, sensibilità integrale: ν {#}, fissione {#} (% di k per % di variazione)",
  "Jezebel, integral sensitivity: ν {#}, fission {#} (% k per % change)": "Jezebel, sensibilità integrale: ν {#}, fissione {#} (% di k per % di variazione)",
  "Flattop-Pu, integral sensitivity: ν {#}, fission {#} (% k per % change)": "Flattop-Pu, sensibilità integrale: ν {#}, fissione {#} (% di k per % di variazione)",
  "Godiva: ν {#}, fission {#}": "Godiva: ν {#}, fissione {#}",
  "Jezebel: ν {#}, fission {#}": "Jezebel: ν {#}, fissione {#}",
  "Flattop-Pu: ν {#}, fission {#}": "Flattop-Pu: ν {#}, fissione {#}",
  "UO₂: {#} × mean": "UO₂: {#} × media",
  "MOX {#} %: {#} × mean": "MOX {#} %: {#} × media",
  "OpenMC re-solve, Δk (pcm)": "Ricalcolo OpenMC, Δk (pcm)",
  "Predicted from sensitivities, Δk (pcm)": "Previsto dalle sensibilità, Δk (pcm)",
  "predicted Δk, pcm": "Δk previsto, pcm",
  "U{#} capture": "cattura U{#}",
  "Pu{#} capture": "cattura Pu{#}",
  "U{#} elastic": "elastico U{#}",
  "Pu{#} elastic": "elastico Pu{#}",
  "U{#} fission": "fissione U{#}",
  "Pu{#} fission": "fissione Pu{#}",
  "U{#} inelastic": "anelastico U{#}",
  "Pu{#} inelastic": "anelastico Pu{#}",
  "U{#} neutrons per fission (ν)": "neutroni per fissione U{#} (ν)",
  "Pu{#} neutrons per fission (ν)": "neutroni per fissione Pu{#} (ν)",
  "Relative pin power (hover a pin)": "Potenza relativa per barretta (passa su una barretta)",
  "Relative pin power (tap a pin)": "Potenza relativa per barretta (tocca una barretta)",
  "To scale.": "In scala.",
  "To scale. Drag to rotate.": "In scala. Trascina per ruotare.",
  "core {#} cm, reflector {#} cm": "nocciolo {#} cm, riflettore {#} cm",
  "radius {#} cm": "raggio {#} cm",
  "{#} cm in {#} cm": "{#} cm in {#} cm",
  "k = {#}; reference {#} ({#} pcm)": "k = {#}; riferimento {#} ({#} pcm)",
  "k {#}, reference {#}": "k {#}, riferimento {#}",
  "plutonium in natural uranium": "plutonio in uranio naturale",
  "plutonium metal": "plutonio metallico",
  "uranium{#} in natural uranium": "uranio{#} in uranio naturale",
  "uranium{#} metal": "uranio{#} metallico",
  "water": "acqua",
  "×{#} of mean": "×{#} della media",
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
