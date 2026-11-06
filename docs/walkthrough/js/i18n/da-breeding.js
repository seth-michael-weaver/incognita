/* Danish: breeding (Avl af nyt brændsel) */
WT.L.ch.breeding = {
  num: "Lektion 9", title: "Avl af nyt brændsel", short: "Avl",
  html: `
<div class="step">
  <h3>Fertilt bliver fissilt</h3>
  <p>Uran-238 spaltes næsten ikke, men det kan fange en neutron. To betahenfald senere (hver gang bliver en neutron indeni til en proton) er det blevet til plutonium-239, som let spaltes. Thorium-232 gør det samme og bliver til uran-233.</p>
  <div class="btns"><button class="btn ghost" data-act="bcU" aria-pressed="true">Uran-238</button> <button class="btn ghost" data-act="bcT" aria-pressed="false">Thorium-232</button></div>
</div>
<div class="step">
  <h3>Neutronbudgettet</h3>
  <p>Hver neutron, der absorberes i fissilt brændsel, giver <i>η</i> nye neutroner tilbage. Én skal give den næste fission, og nogle går tabt; det, der er tilbage, kan avle. Med uran-235 og langsomme neutroner dannes kun omkring 0,6 nye fissile kerner pr. brændt kerne.</p>
  <div class="btns"><button class="btn ghost" data-act="bfU5" aria-pressed="true">U-235</button> <button class="btn ghost" data-act="bfP9" aria-pressed="false">Pu-239</button> <button class="btn ghost" data-act="bfU3" aria-pressed="false">U-233</button></div>
  <div class="btns"><button class="btn ghost" data-act="bsT" aria-pressed="true">Langsomme neutroner</button> <button class="btn ghost" data-act="bsF" aria-pressed="false">Hurtige neutroner</button></div>
</div>
<div class="step">
  <h3>Hurtige neutroner avler</h3>
  <p>For at avle skal én neutron føre kæden videre, og mindst én skal lave nyt brændsel, så <i>η</i> skal overgå 2 med mere end tabene. Plutonium-239 i en hurtig reaktor giver omkring 2,4: nok til overs.</p>
  <div class="ctl"><label for="br-l1">Tabte neutroner</label><input id="br-l1" type="range" data-bind="L" data-instant min="0.05" max="0.8" step="0.01" value="0.2"><output data-show="L" data-fmt="2"></output></div>
</div>
<div class="step">
  <h3>Thorium med langsomme neutroner</h3>
  <p>Med langsomme neutroner giver plutonium-239 kun omkring 2,1, men uran-233 giver 2,29. Den margin lader en thoriumreaktor avle med langsomme neutroner, hvis den spilder meget få. Sænk tabene, indtil den avler.</p>
  <div class="ctl"><label for="br-l2">Tabte neutroner</label><input id="br-l2" type="range" data-bind="L" data-instant min="0.05" max="0.8" step="0.01" value="0.35"><output data-show="L" data-fmt="2"></output></div>
</div>
<div class="step">
  <h3>Konverteringsforhold</h3>
  <p>Konverteringsforholdet er antallet af dannede fissile kerner pr. brændt fissil kerne. Under 1 slipper brændslet langsomt op (en konverter, som nutidens vandreaktorer); over 1 ender reaktoren med mere brændsel, end den startede med (en formeringsreaktor).</p>
  <div class="btns"><button class="btn ghost" data-act="bfU5" aria-pressed="true">U-235</button> <button class="btn ghost" data-act="bfP9" aria-pressed="false">Pu-239</button> <button class="btn ghost" data-act="bfU3" aria-pressed="false">U-233</button></div>
  <div class="btns"><button class="btn ghost" data-act="bsT" aria-pressed="true">Langsomme neutroner</button> <button class="btn ghost" data-act="bsF" aria-pressed="false">Hurtige neutroner</button></div>
</div>`,
};

Object.assign(WT.L.labels, {
  "+ n": "+ n",
  "Th{#} (fertile)": "Th{#} (fertil)",
  "U{#} (fertile)": "U{#} (fertil)",
  "a batch of {a} waiting · day {b}": "et parti {a} venter · dag {b}",
  "after {#} months, {#} % has become U{#}": "efter {#} måneder er {#} % blevet til U{#}",
  "after {#} weeks, {#} % has become Pu{#}": "efter {#} uger er {#} % blevet til Pu{#}",
  "antineutrino": "antineutrino",
  "breed": "avl",
  "breeds: Th{#} → U{#}": "avler: Th{#} → U{#}",
  "breeds: U{#} → Pu{#}": "avler: U{#} → Pu{#}",
  "burned {a}": "brændt {a}",
  "catch": "indfangning",
  "chain": "kæde",
  "conversion ratio {a}: a converter": "konverteringsforhold {a}: en konverter",
  "conversion ratio {a}: a breeder": "konverteringsforhold {a}: en formeringsreaktor",
  "conversion ratio ≈ η − 1 − lost = {a}: breeds": "konverteringsforhold ≈ η − 1 − tabt = {a}: avler",
  "conversion ratio ≈ η − 1 − lost = {a}: breeds, makes more fuel than it burns": "konverteringsforhold ≈ η − 1 − tabt = {a}: avler, laver mere brændsel, end den brænder",
  "conversion ratio ≈ η − 1 − lost = {a}: converts": "konverteringsforhold ≈ η − 1 − tabt = {a}: konverterer",
  "conversion ratio ≈ η − 1 − lost = {a}: converts, makes less fuel than it burns": "konverteringsforhold ≈ η − 1 − tabt = {a}: konverterer, laver mindre brændsel, end den brænder",
  "electron": "elektron",
  "fast neutrons": "hurtige neutroner",
  "fertile": "fertil",
  "fertile: barely splits": "fertil: spaltes næsten ikke",
  "fissile": "fissil",
  "fissile: splits easily": "fissil: spaltes let",
  "illustration": "illustration",
  "lost": "tabt",
  "lost: water, steel, poisons, leakage": "tabt: vand, stål, gifte, lækage",
  "made {a}": "dannet {a}",
  "neutrons out per neutron absorbed in the fuel": "neutroner ud pr. neutron absorberet i brændslet",
  "neutrons per absorption": "neutroner pr. absorption",
  "next fission": "næste fission",
  "next fission: keeps the chain going": "næste fission: holder kæden i gang",
  "slow neutrons": "langsomme neutroner",
  "slow step: Np{#}, half-life {#} d": "langsomt trin: Np{#}, halveringstid {#} d",
  "slow step: Pa{#}, half-life {#} d": "langsomt trin: Pa{#}, halveringstid {#} d",
  "split": "spaltet",
  "split (fission products)": "spaltet (fissionsprodukter)",
  "the slow step is Np{#} (half-life {#} days)": "det langsomme trin er Np{#} (halveringstid {#} dage)",
  "the slow step is Pa{#} (half-life {#} days)": "det langsomme trin er Pa{#} (halveringstid {#} dage)",
  "{#} d": "{#} d",
  "{#} min": "{#} min",
  "{#} p": "{#} p",
  "{#} protons": "{#} protoner",
  "{#}: breeding line": "{#}: avlsgrænse",
  "{a} % now {b}": "{a} % nu {b}",
  "{a} per absorption": "{a} pr. absorption",
  "{a} waiting: day {b}": "{a} venter: dag {b}",
  "{a} · fast neutrons": "{a} · hurtige neutroner",
  "{a} · slow neutrons": "{a} · langsomme neutroner",
  "η = {a}": "η = {a}",
  "η ≈ {a}": "η ≈ {a}",
});
