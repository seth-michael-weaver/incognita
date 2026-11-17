/* German: kcalc (Computing criticality) */
WT.L.ch.kcalc = {
  num: "Lektion 1", title: "Kritikalität berechnen", short: "k berechnen",
  html: `
<div class="step">
  <h3>Die Benchmarks</h3>
  <p>Vier schnelle metallische kritische Anordnungen aus dem ICSBEP, maßstabsgetreu. Godiva und Jezebel sind nackte Kugeln; Flattop-25 und Flattop-Pu haben einen Reflektor aus Natururan.</p>
</div>
<div class="step">
  <h3>Berechnetes <i>k</i><sub>eff</sub></h3>
  <p>OpenMC, kontinuierliche Energie, 3-D-Geometrie. Alle vier liegen innerhalb ±1σ des Benchmarks. <i>k</i><sub>eff</sub> wird in der Anpassung nicht verwendet.</p>
</div>
<div class="step">
  <h3>Sensitivitätsprofile</h3>
  <p>Adjungierte Sensitivität von <i>k</i><sub>eff</sub> für jede Reaktion, pro Lethargieeinheit.</p>
  <div class="btns"><button class="btn ghost" data-act="se0" aria-pressed="true">Godiva</button><button class="btn ghost" data-act="se1" aria-pressed="false">Jezebel</button><button class="btn ghost" data-act="se2" aria-pressed="false">Flattop-Pu</button></div>
</div>
<div class="step">
  <h3>Geprüft durch direkte Störung</h3>
  <p>Vorhergesagte gegen neu berechnete Änderungen von <i>k</i><sub>eff</sub>, 63 gestörte Datensätze.</p>
</div>
<div class="step">
  <h3>Reaktorkern C5G7</h3>
  <p>OECD/NEA C5G7, 2-D-Viertelkern, 1056 UO<sub>2</sub>- und MOX-Stäbe. <i>k</i><sub>eff</sub> −19&nbsp;pcm von der Referenz; maximaler Stableistungsfehler 0,13&nbsp;%.</p>
</div>`,
};

Object.assign(WT.L.labels, {
  "{#} pcm  (±{#} benchmark)": "{#} pcm  (Benchmark ±{#})",
  "+{#} pcm  (±{#} benchmark)": "+{#} pcm  (Benchmark ±{#})",
  "Calculated − experimental k, with the benchmark ±{#}σ band": "Berechnetes − experimentelles k, mit dem ±{#}σ-Band des Benchmarks",
  "Drag to rotate": "Ziehen zum Drehen",
  "Godiva, integral sensitivity: ν {#}, fission {#} (% k per % change)": "Godiva, integrale Sensitivität: ν {#}, Spaltung {#} (% k pro % Änderung)",
  "Jezebel, integral sensitivity: ν {#}, fission {#} (% k per % change)": "Jezebel, integrale Sensitivität: ν {#}, Spaltung {#} (% k pro % Änderung)",
  "Flattop-Pu, integral sensitivity: ν {#}, fission {#} (% k per % change)": "Flattop-Pu, integrale Sensitivität: ν {#}, Spaltung {#} (% k pro % Änderung)",
  "Godiva: ν {#}, fission {#}": "Godiva: ν {#}, Spaltung {#}",
  "Jezebel: ν {#}, fission {#}": "Jezebel: ν {#}, Spaltung {#}",
  "Flattop-Pu: ν {#}, fission {#}": "Flattop-Pu: ν {#}, Spaltung {#}",
  "UO₂: {#} × mean": "UO₂: {#} × Mittel",
  "MOX {#} %: {#} × mean": "MOX {#} %: {#} × Mittel",
  "OpenMC re-solve, Δk (pcm)": "OpenMC-Neuberechnung, Δk (pcm)",
  "Predicted from sensitivities, Δk (pcm)": "Aus Sensitivitäten vorhergesagt, Δk (pcm)",
  "predicted Δk, pcm": "vorhergesagtes Δk, pcm",
  "U{#} capture": "U{#} Einfang",
  "Pu{#} capture": "Pu{#} Einfang",
  "U{#} elastic": "U{#} elastisch",
  "Pu{#} elastic": "Pu{#} elastisch",
  "U{#} fission": "U{#} Spaltung",
  "Pu{#} fission": "Pu{#} Spaltung",
  "U{#} inelastic": "U{#} inelastisch",
  "Pu{#} inelastic": "Pu{#} inelastisch",
  "U{#} neutrons per fission (ν)": "U{#} Neutronen pro Spaltung (ν)",
  "Pu{#} neutrons per fission (ν)": "Pu{#} Neutronen pro Spaltung (ν)",
  "Relative pin power (hover a pin)": "Relative Stableistung (Zeiger auf einen Stab)",
  "Relative pin power (tap a pin)": "Relative Stableistung (Stab antippen)",
  "To scale.": "Maßstabsgetreu.",
  "To scale. Drag to rotate.": "Maßstabsgetreu. Ziehen zum Drehen.",
  "core {#} cm, reflector {#} cm": "Kern {#} cm, Reflektor {#} cm",
  "radius {#} cm": "Radius {#} cm",
  "{#} cm in {#} cm": "{#} cm in {#} cm",
  "k = {#}; reference {#} ({#} pcm)": "k = {#}; Referenz {#} ({#} pcm)",
  "k {#}, reference {#}": "k {#}, Referenz {#}",
  "plutonium in natural uranium": "Plutonium in Natururan",
  "plutonium metal": "Plutoniummetall",
  "uranium{#} in natural uranium": "Uran{#} in Natururan",
  "uranium{#} metal": "Uran{#}-Metall",
  "water": "Wasser",
  "×{#} of mean": "×{#} des Mittels",
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
