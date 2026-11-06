/* Dutch (Nederlands): kinetics (Reactorkinetiek: zes groepen en de inhour-vergelijking) */
WT.L.ch.kinetics = {
  num: "Les 15", title: "Reactorkinetiek: zes groepen en de inhour-vergelijking", short: "Kinetiek",
  html: `
<div class="step">
  <h3>Zes groepen late neutronen</h3>
  <p>Vertraagde neutronen komen uit ongeveer zes groepen splijtingsproducten, met halveringstijden van 0,23 s tot 56 s (Keepin, U-235). De groepen van 2 s en 22 s zenden er de meeste uit, terwijl de langlevende groepen het grootste deel van de wachtende voorraad vasthouden: gemiddelde vertraging Σ <i>a</i><sub>i</sub>/<i>λ</i><sub>i</sub> ≈ 13 s. Stop de splijtingen en kijk hoe elke groep in zijn eigen tempo uitdooft.</p>
  <div class="btns"><button class="btn" data-act="kistop" aria-pressed="false">Stop de splijtingen</button></div>
</div>
<div class="step">
  <h3>De inhour-vergelijking</h3>
  <p>Probeer <i>n</i> ∝ e<sup><i>ωt</i></sup> in de puntkinetiek met zes groepen en je krijgt <i>ρ</i> = <i>ω</i>Λ + Σ <i>β</i><sub>i</sub><i>ω</i>/(<i>ω</i> + <i>λ</i><sub>i</sub>): zeven takken, gescheiden door de polen bij −<i>λ</i><sub>i</sub>. Een sprong in <i>ρ</i> snijdt elke tak één keer; de meest rechtse wortel is de stabiele periode <i>T</i> = 1/<i>ω</i><sub>1</sub>, de andere zes sterven uit.</p>
  <div class="ctl"><label for="ki-r1">Reactiviteit ρ ($)</label><input id="ki-r1" type="range" data-bind="rd" data-instant min="-2" max="1.3" step="0.01" value="0.3"><output data-show="rd" data-fmt="2"></output></div>
</div>
<div class="step">
  <h3>Promptsprong en prompt kritiek</h3>
  <p>Een reactiviteitssprong tilt het vermogen eerst binnen milliseconden op met <i>P</i><sub>1</sub>/<i>P</i><sub>0</sub> ≈ <i>β</i>/(<i>β</i> − <i>ρ</i>), daarna stijgt het met de stabiele periode. Bij <i>ρ</i> = 1 $ zijn de prompte neutronen alleen al kritiek en klapt de periode in naar Λ/(<i>ρ</i> − <i>β</i>).</p>
  <div class="ctl"><label for="ki-r2">Reactiviteit ρ ($)</label><input id="ki-r2" type="range" data-bind="rj" data-instant min="0.05" max="1.3" step="0.01" value="0.5"><output data-show="rj" data-fmt="2"></output></div>
</div>
<div class="step">
  <h3>Na een scram</h3>
  <p>Voer een grote negatieve reactiviteit in: het vermogen zakt prompt tot ongeveer <i>β</i>/(<i>β</i> − <i>ρ</i>) en kan daarna niet sneller dalen dan de langstlevende groep vervalt. Hoe diep de scram ook is, de periode nadert −1/<i>λ</i><sub>1</sub> ≈ −80 s.</p>
  <div class="ctl"><label for="ki-r3">Reactiviteit ρ ($)</label><input id="ki-r3" type="range" data-bind="rs" data-instant min="-30" max="-0.5" step="0.5" value="-10"><output data-show="rs" data-fmt="1"></output></div>
</div>`,
};

Object.assign(WT.L.labels, {
  "Stop fissions": "Stop de splijtingen",
  "Restart fissions": "Herstart de splijtingen",
  "half-life · share emitted": "halveringstijd · uitgezonden deel",
  "waiting stock": "wachtende voorraad",
  "delayed neutrons out": "uitgezonden vertraagde neutronen",
  "Keepin six-group data": "zesgroepsdata van Keepin",
  "prompt critical": "prompt kritiek",
  "drag ρ": "sleep ρ",
  "drag the rods out": "sleep de staven eruit",
  "drag the rods in": "sleep de staven erin",
  "power": "vermogen",
  "power ×{#} speed": "vermogen ×{#} snelheid",
  "{#} s after stopping · delayed emission {#} % of the start": "{#} s na het stoppen · vertraagde emissie {#} % van de start",
  "mean delay Σ aᵢ/λᵢ = {#} s · β = {#} (U{#})": "gemiddelde vertraging Σ aᵢ/λᵢ = {#} s · β = {#} (U{#})",
  "prompt root": "prompte wortel",
  "prompt root ≈ −(β−ρ)/Λ": "prompte wortel ≈ −(β−ρ)/Λ",
  "ω ({#}/s), stretched": "ω ({#}/s), uitgerekt",
  "ω ({#}/s), axis stretched (asinh)": "ω ({#}/s), as uitgerekt (asinh)",
  "ρ = {#}: power stays flat": "ρ = {#}: vermogen blijft vlak",
  "stable period T = {#}/ω₁ = {#} ms": "stabiele periode T = {#}/ω₁ = {#} ms",
  "stable period T = {#}/ω₁ = {#} s": "stabiele periode T = {#}/ω₁ = {#} s",
  "stable period T = {#}/ω₁ = {#} min": "stabiele periode T = {#}/ω₁ = {#} min",
  "stable period T = {#}/ω₁ = {#} h": "stabiele periode T = {#}/ω₁ = {#} u",
  "prompt jump β/(β−ρ) = {#}": "promptsprong β/(β−ρ) = {#}",
  "{#} s": "{#} s",
  "prompt critical · period {#} ms (Λ = {#} µs)": "prompt kritiek · periode {#} ms (Λ = {#} µs)",
  "prompt critical · period {#} s (Λ = {#} µs)": "prompt kritiek · periode {#} s (Λ = {#} µs)",
  "ρ = {#} $ · stable period {#} ms": "ρ = {#} $ · stabiele periode {#} ms",
  "ρ = {#} $ · stable period {#} s": "ρ = {#} $ · stabiele periode {#} s",
  "ρ = {#} $ · stable period {#} min": "ρ = {#} $ · stabiele periode {#} min",
  "ρ = {#} $ · stable period {#} h": "ρ = {#} $ · stabiele periode {#} u",
  "prompt drop to {#}": "promptdaling tot {#}",
  "slope e^(−t/{#} s)": "helling e^(−t/{#} s)",
  "slope e^(−t / {#} s): the {#} s group": "helling e^(−t / {#} s): de groep van {#} s",
  "ρ = {#} $ · stable period {#} s (limit {#} s)": "ρ = {#} $ · stabiele periode {#} s (limiet {#} s)",
  "ρ = {#} $ · stable period {#} min (limit {#} s)": "ρ = {#} $ · stabiele periode {#} min (limiet {#} s)",
  "ρ = {#} $ · stable period {#} h (limit {#} s)": "ρ = {#} $ · stabiele periode {#} u (limiet {#} s)",
});
