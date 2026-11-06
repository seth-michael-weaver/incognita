/* German (Deutsch): kinetics (Reaktorkinetik: sechs Gruppen und die Inhour-Gleichung) */
WT.L.ch.kinetics = {
  num: "Lektion 15", title: "Reaktorkinetik: sechs Gruppen und die Inhour-Gleichung", short: "Kinetik",
  html: `
<div class="step">
  <h3>Sechs Gruppen später Neutronen</h3>
  <p>Verzögerte Neutronen stammen aus etwa sechs Gruppen von Spaltprodukten, mit Halbwertszeiten von 0,23 s bis 56 s (Keepin, U-235). Die 2-s- und die 22-s-Gruppe senden die meisten aus, während die langlebigen Gruppen den größten Teil des wartenden Vorrats halten: mittlere Verzögerung Σ <i>a</i><sub>i</sub>/<i>λ</i><sub>i</sub> ≈ 13 s. Stoppe die Spaltungen und sieh zu, wie jede Gruppe in ihrem eigenen Tempo abklingt.</p>
  <div class="btns"><button class="btn" data-act="kistop" aria-pressed="false">Spaltungen stoppen</button></div>
</div>
<div class="step">
  <h3>Die Inhour-Gleichung</h3>
  <p>Setzt man <i>n</i> ∝ e<sup><i>ωt</i></sup> in die Punktkinetik mit sechs Gruppen ein, erhält man <i>ρ</i> = <i>ω</i>Λ + Σ <i>β</i><sub>i</sub><i>ω</i>/(<i>ω</i> + <i>λ</i><sub>i</sub>): sieben Äste, getrennt durch die Pole bei −<i>λ</i><sub>i</sub>. Ein Sprung in <i>ρ</i> trifft jeden Ast einmal; die Wurzel ganz rechts ist die stabile Periode <i>T</i> = 1/<i>ω</i><sub>1</sub>, die anderen sechs klingen ab.</p>
  <div class="ctl"><label for="ki-r1">Reaktivität ρ ($)</label><input id="ki-r1" type="range" data-bind="rd" data-instant min="-2" max="1.3" step="0.01" value="0.3"><output data-show="rd" data-fmt="2"></output></div>
</div>
<div class="step">
  <h3>Prompter Sprung und prompte Kritikalität</h3>
  <p>Ein Reaktivitätssprung hebt die Leistung zuerst innerhalb von Millisekunden um <i>P</i><sub>1</sub>/<i>P</i><sub>0</sub> ≈ <i>β</i>/(<i>β</i> − <i>ρ</i>), dann steigt sie mit der stabilen Periode. Bei <i>ρ</i> = 1 $ sind die prompten Neutronen allein kritisch, und die Periode bricht auf Λ/(<i>ρ</i> − <i>β</i>) zusammen.</p>
  <div class="ctl"><label for="ki-r2">Reaktivität ρ ($)</label><input id="ki-r2" type="range" data-bind="rj" data-instant min="0.05" max="1.3" step="0.01" value="0.5"><output data-show="rj" data-fmt="2"></output></div>
</div>
<div class="step">
  <h3>Nach einer Schnellabschaltung</h3>
  <p>Bringe große negative Reaktivität ein: Die Leistung fällt prompt auf etwa <i>β</i>/(<i>β</i> − <i>ρ</i>) und kann danach nicht schneller sinken, als die langlebigste Gruppe zerfällt. Wie tief die Schnellabschaltung auch ist, die Periode strebt gegen −1/<i>λ</i><sub>1</sub> ≈ −80 s.</p>
  <div class="ctl"><label for="ki-r3">Reaktivität ρ ($)</label><input id="ki-r3" type="range" data-bind="rs" data-instant min="-30" max="-0.5" step="0.5" value="-10"><output data-show="rs" data-fmt="1"></output></div>
</div>`,
};

Object.assign(WT.L.labels, {
  "Stop fissions": "Spaltungen stoppen",
  "Restart fissions": "Spaltungen wieder starten",
  "half-life · share emitted": "Halbwertszeit · emittierter Anteil",
  "waiting stock": "wartender Vorrat",
  "delayed neutrons out": "abgegebene verzögerte Neutronen",
  "Keepin six-group data": "Sechs-Gruppen-Daten nach Keepin",
  "prompt critical": "prompt kritisch",
  "drag ρ": "ρ ziehen",
  "drag the rods out": "Stäbe herausziehen",
  "drag the rods in": "Stäbe einfahren",
  "power": "Leistung",
  "power ×{#} speed": "Leistung ×{#} Tempo",
  "{#} s after stopping · delayed emission {#} % of the start": "{#} s nach dem Stoppen · verzögerte Emission {#} % des Anfangswerts",
  "mean delay Σ aᵢ/λᵢ = {#} s · β = {#} (U{#})": "mittlere Verzögerung Σ aᵢ/λᵢ = {#} s · β = {#} (U{#})",
  "prompt root": "prompte Wurzel",
  "prompt root ≈ −(β−ρ)/Λ": "prompte Wurzel ≈ −(β−ρ)/Λ",
  "ω ({#}/s), stretched": "ω ({#}/s), gestreckt",
  "ω ({#}/s), axis stretched (asinh)": "ω ({#}/s), Achse gestreckt (asinh)",
  "ρ = {#}: power stays flat": "ρ = {#}: Leistung bleibt konstant",
  "stable period T = {#}/ω₁ = {#} ms": "stabile Periode T = {#}/ω₁ = {#} ms",
  "stable period T = {#}/ω₁ = {#} s": "stabile Periode T = {#}/ω₁ = {#} s",
  "stable period T = {#}/ω₁ = {#} min": "stabile Periode T = {#}/ω₁ = {#} min",
  "stable period T = {#}/ω₁ = {#} h": "stabile Periode T = {#}/ω₁ = {#} h",
  "prompt jump β/(β−ρ) = {#}": "prompter Sprung β/(β−ρ) = {#}",
  "{#} s": "{#} s",
  "prompt critical · period {#} ms (Λ = {#} µs)": "prompt kritisch · Periode {#} ms (Λ = {#} µs)",
  "prompt critical · period {#} s (Λ = {#} µs)": "prompt kritisch · Periode {#} s (Λ = {#} µs)",
  "ρ = {#} $ · stable period {#} ms": "ρ = {#} $ · stabile Periode {#} ms",
  "ρ = {#} $ · stable period {#} s": "ρ = {#} $ · stabile Periode {#} s",
  "ρ = {#} $ · stable period {#} min": "ρ = {#} $ · stabile Periode {#} min",
  "ρ = {#} $ · stable period {#} h": "ρ = {#} $ · stabile Periode {#} h",
  "prompt drop to {#}": "prompter Abfall auf {#}",
  "slope e^(−t/{#} s)": "Steigung e^(−t/{#} s)",
  "slope e^(−t / {#} s): the {#} s group": "Steigung e^(−t / {#} s): die {#}-s-Gruppe",
  "ρ = {#} $ · stable period {#} s (limit {#} s)": "ρ = {#} $ · stabile Periode {#} s (Grenze {#} s)",
  "ρ = {#} $ · stable period {#} min (limit {#} s)": "ρ = {#} $ · stabile Periode {#} min (Grenze {#} s)",
  "ρ = {#} $ · stable period {#} h (limit {#} s)": "ρ = {#} $ · stabile Periode {#} h (Grenze {#} s)",
});
