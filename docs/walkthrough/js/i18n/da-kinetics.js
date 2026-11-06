/* Danish: kinetics (Reaktorkinetik: seks grupper og inhour-ligningen) */
WT.L.ch.kinetics = {
  num: "Lektion 15", title: "Reaktorkinetik: seks grupper og inhour-ligningen", short: "Kinetik",
  html: `
<div class="step">
  <h3>Seks grupper af sene neutroner</h3>
  <p>Forsinkede neutroner kommer fra omkring seks grupper af fissionsprodukter med halveringstider fra 0,23 s til 56 s (Keepin, U-235). Grupperne på 2 s og 22 s udsender flest, mens de langlivede grupper rummer det meste af det ventende lager: middelforsinkelse Σ <i>a</i><sub>i</sub>/<i>λ</i><sub>i</sub> ≈ 13 s. Stop fissionerne, og se hver gruppe klinge af i sit eget tempo.</p>
  <div class="btns"><button class="btn" data-act="kistop" aria-pressed="false">Stop fissionerne</button></div>
</div>
<div class="step">
  <h3>Inhour-ligningen</h3>
  <p>Prøv <i>n</i> ∝ e<sup><i>ωt</i></sup> i punktkinetikken med seks grupper, og du får <i>ρ</i> = <i>ω</i>Λ + Σ <i>β</i><sub>i</sub><i>ω</i>/(<i>ω</i> + <i>λ</i><sub>i</sub>): syv grene adskilt af polerne ved −<i>λ</i><sub>i</sub>. Et spring i <i>ρ</i> skærer hver gren én gang; roden længst til højre er den stabile periode <i>T</i> = 1/<i>ω</i><sub>1</sub>, de andre seks dør ud.</p>
  <div class="ctl"><label for="ki-r1">Reaktivitet ρ ($)</label><input id="ki-r1" type="range" data-bind="rd" data-instant min="-2" max="1.3" step="0.01" value="0.3"><output data-show="rd" data-fmt="2"></output></div>
</div>
<div class="step">
  <h3>Promptspring og promptkritikalitet</h3>
  <p>Et reaktivitetsspring løfter først effekten inden for millisekunder med <i>P</i><sub>1</sub>/<i>P</i><sub>0</sub> ≈ <i>β</i>/(<i>β</i> − <i>ρ</i>), derefter stiger den med den stabile periode. Ved <i>ρ</i> = 1 $ er de prompte neutroner alene kritiske, og perioden falder sammen mod Λ/(<i>ρ</i> − <i>β</i>).</p>
  <div class="ctl"><label for="ki-r2">Reaktivitet ρ ($)</label><input id="ki-r2" type="range" data-bind="rj" data-instant min="0.05" max="1.3" step="0.01" value="0.5"><output data-show="rj" data-fmt="2"></output></div>
</div>
<div class="step">
  <h3>Efter et nødstop</h3>
  <p>Tilfør en stor negativ reaktivitet: effekten falder prompte til omkring <i>β</i>/(<i>β</i> − <i>ρ</i>) og kan derefter ikke falde hurtigere, end den længstlevende gruppe henfalder. Uanset hvor dybt nødstoppet er, går perioden mod −1/<i>λ</i><sub>1</sub> ≈ −80 s.</p>
  <div class="ctl"><label for="ki-r3">Reaktivitet ρ ($)</label><input id="ki-r3" type="range" data-bind="rs" data-instant min="-30" max="-0.5" step="0.5" value="-10"><output data-show="rs" data-fmt="1"></output></div>
</div>`,
};

Object.assign(WT.L.labels, {
  "Stop fissions": "Stop fissionerne",
  "Restart fissions": "Genstart fissionerne",
  "half-life · share emitted": "halveringstid · udsendt andel",
  "waiting stock": "ventende lager",
  "delayed neutrons out": "udsendte forsinkede neutroner",
  "Keepin six-group data": "Keepins seksgruppedata",
  "prompt critical": "promptkritisk",
  "drag ρ": "træk ρ",
  "drag the rods out": "træk stavene ud",
  "drag the rods in": "træk stavene ind",
  "power": "effekt",
  "power ×{#} speed": "effekt ×{#} hastighed",
  "{#} s after stopping · delayed emission {#} % of the start": "{#} s efter stop · forsinket udsendelse {#} % af starten",
  "mean delay Σ aᵢ/λᵢ = {#} s · β = {#} (U{#})": "middelforsinkelse Σ aᵢ/λᵢ = {#} s · β = {#} (U{#})",
  "prompt root": "prompt rod",
  "prompt root ≈ −(β−ρ)/Λ": "prompt rod ≈ −(β−ρ)/Λ",
  "ω ({#}/s), stretched": "ω ({#}/s), strakt",
  "ω ({#}/s), axis stretched (asinh)": "ω ({#}/s), akse strakt (asinh)",
  "ρ = {#}: power stays flat": "ρ = {#}: effekten forbliver flad",
  "stable period T = {#}/ω₁ = {#} ms": "stabil periode T = {#}/ω₁ = {#} ms",
  "stable period T = {#}/ω₁ = {#} s": "stabil periode T = {#}/ω₁ = {#} s",
  "stable period T = {#}/ω₁ = {#} min": "stabil periode T = {#}/ω₁ = {#} min",
  "stable period T = {#}/ω₁ = {#} h": "stabil periode T = {#}/ω₁ = {#} t",
  "prompt jump β/(β−ρ) = {#}": "promptspring β/(β−ρ) = {#}",
  "{#} s": "{#} s",
  "prompt critical · period {#} ms (Λ = {#} µs)": "promptkritisk · periode {#} ms (Λ = {#} µs)",
  "prompt critical · period {#} s (Λ = {#} µs)": "promptkritisk · periode {#} s (Λ = {#} µs)",
  "ρ = {#} $ · stable period {#} ms": "ρ = {#} $ · stabil periode {#} ms",
  "ρ = {#} $ · stable period {#} s": "ρ = {#} $ · stabil periode {#} s",
  "ρ = {#} $ · stable period {#} min": "ρ = {#} $ · stabil periode {#} min",
  "ρ = {#} $ · stable period {#} h": "ρ = {#} $ · stabil periode {#} t",
  "prompt drop to {#}": "promptfald til {#}",
  "slope e^(−t/{#} s)": "hældning e^(−t/{#} s)",
  "slope e^(−t / {#} s): the {#} s group": "hældning e^(−t / {#} s): gruppen på {#} s",
  "ρ = {#} $ · stable period {#} s (limit {#} s)": "ρ = {#} $ · stabil periode {#} s (grænse {#} s)",
  "ρ = {#} $ · stable period {#} min (limit {#} s)": "ρ = {#} $ · stabil periode {#} min (grænse {#} s)",
  "ρ = {#} $ · stable period {#} h (limit {#} s)": "ρ = {#} $ · stabil periode {#} t (grænse {#} s)",
});
