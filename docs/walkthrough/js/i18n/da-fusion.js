/* Danish: fusion (chapter 29) */
WT.L.ch.fusion = {
  num: "Kapitel 29", title: "Fusionsenergi og Coulombbarrieren", short: "Fusion",
  lead: "Fusion går den modsatte vej af fission: to lette kerner smelter sammen, og parret vejer mindre end delene.",
  html: `
<div class="step">
  <h3>Fusionsenergi ud fra bindingskurven</h3>
  <p>Slå to lette kerner sammen: hvis den nye ligger højere på bindingskurven, frigives der energi. Forbi jerntoppen koster sammensmeltning energi.</p>
  <div class="ctl"><label for="fu-a">Hver let kerne A</label><input id="fu-a" type="range" data-bind="fuse" data-instant min="2" max="60" step="1" value="2"><output data-show="fuse" data-fmt="0"></output></div>
  <p class="ctl-result" id="fu-fuse-out" aria-live="polite"></p>
</div>
<div class="step">
  <h3>Coulombbarrieren og tunnelering</h3>
  <p>Træk deuteronen tilbage, og giv slip. Begge kerner er ladede, så de fleste skud preller af på bakken; nogle få tunnelerer igennem.</p>
  <div class="ctl"><label for="fu-e">Skub (keV)</label><input id="fu-e" type="range" data-bind="lE" min="0.5" max="2.6" step="0.01" value="1.7"><output data-show="E" data-fmt="0"></output></div>
  <div class="btns"><button class="btn" data-act="fire">Skyd</button></div>
</div>
<div class="step">
  <h3>Reaktionsprodukter og Q-værdi</h3>
  <p>Det sammensmeltede par er lettere end de to dele. Den manglende masse flyver væk som hurtige partikler.</p>
  <div class="btns fu-fuels"><button class="btn ghost" data-act="DT" aria-pressed="true">D–T</button> <button class="btn ghost" data-act="DD" aria-pressed="false">D–D</button> <button class="btn ghost" data-act="DHe" aria-pressed="false">D–³He</button> <button class="btn ghost" data-act="pB" aria-pressed="false">p–¹¹B</button></div>
</div>
<div class="step">
  <h3>Termonuklear reaktionsrate</h3>
  <p>I en varm gas kommer de hurtigste kerner igennem. Hvert glimt er én fusion.</p>
  <div class="ctl"><label for="fu-t">Temperatur (keV)</label><input id="fu-t" type="range" data-bind="lT" min="0" max="2" step="0.01" value="1"><output data-show="T" data-fmt="1"></output></div>
</div>`,
};
Object.assign(WT.L.labels, {
  "B": "B",
  "Copper{#}": "Kobber{#}",
  "Coulomb hill": "Coulombbakke",
  "D–D": "D–D",
  "D–T": "D–T",
  "D–³He": "D–³He",
  "E = kT": "E = kT",
  "Gamow peak E₀": "Gamow-top E₀",
  "K {#} · field lines lost to the wall: {#}": "K {#} · feltlinjer tabt til væggen: {#}",
  "Q = {#}": "Q = {#}",
  "Q = ∞: no heating needed": "Q = ∞: ingen opvarmning nødvendig",
  "Silicon{#} (SiC)": "Silicium{#} (SiC)",
  "Steel (iron{#})": "Stål (jern{#})",
  "Sun's core": "Solens kerne",
  "TBR {#}": "TBR {#}",
  "Tungsten{#}": "Wolfram{#}",
  "Vanadium{#}": "Vanadium{#}",
  "after {#} years at {#} MW/m² · {#} MeV neutrons only · σ from INCOGNITA library v{#}": "efter {#} år ved {#} MW/m² · kun {#} MeV-neutroner · σ fra INCOGNITAs bibliotek v{#}",
  "almost never": "næsten aldrig",
  "alpha {#} MeV": "alfa {#} MeV",
  "axis, q = {#}": "akse, q = {#}",
  "binding per nucleon (MeV)": "binding pr. nukleon (MeV)",
  "bubble-chamber view, magnetic field into the page: charged products curl, the neutron leaves no track": "boblekammerbillede, magnetfelt ind i siden: ladede produkter krummer, neutronen efterlader intet spor",
  "burning on its own": "brænder af sig selv",
  "cooled down: plasma lost": "afkølet: plasmaet tabt",
  "cooling": "afkøles",
  "could not load the library file": "kunne ikke indlæse biblioteksfilen",
  "deuteron": "deuteron",
  "deuteron {#} keV": "deuteron {#} keV",
  "deuteron: pull back, let go": "deuteron: træk tilbage, giv slip",
  "drag or tap a point; it runs on its own": "træk eller tryk på et punkt; det kører selv",
  "easiest: {a} keV, nτT {b}": "lettest: {a} keV, nτT {b}",
  "edge: q = {#} · lines that cross it are lost": "kant: q = {#} · linjer, der krydser den, er tabt",
  "electron {#} keV": "elektron {#} keV",
  "energy of the colliding pair (keV)": "det kolliderende pars energi (keV)",
  "few are this fast": "få er så hurtige",
  "fusion rate: {a} the rate at {b} keV": "fusionsrate: {a} raten ved {b} keV",
  "grain boundary": "korngrænse",
  "heating itself": "varmer sig selv op",
  "helium stays and gathers into bubbles; hydrogen mostly diffuses out": "helium bliver og samles i bobler; brint diffunderer for det meste ud",
  "helium {#} appm": "helium {#} appm",
  "hill to climb: charge product Z₁Z₂ = {#}": "bakke at bestige: ladningsprodukt Z₁Z₂ = {#}",
  "hold: heaters on (Q = fusion power / heating) · let go: heaters off, the plasma is on its own": "hold: opvarmning til (Q = fusionseffekt / opvarmning) · giv slip: opvarmning fra, plasmaet klarer sig selv",
  "hydrogen {#} appm": "brint {#} appm",
  "ignition (Q = ∞)": "antændelse (Q = ∞)",
  "kT (keV)": "kT (keV)",
  "kT {#} keV · E₀ {#} keV · width {#} keV": "kT {#} keV · E₀ {#} keV · bredde {#} keV",
  "kT {a} keV · D–T {b} m³/s · {c}× D–D": "kT {a} keV · D–T {b} m³/s · {c}× D–D",
  "keeps itself hot": "holder sig selv varm",
  "laps {#}": "omgange {#}",
  "lead–lithium": "bly–lithium",
  "liquid lithium": "flydende lithium",
  "loading INCOGNITA's cross sections…": "indlæser INCOGNITAs tværsnit…",
  "missing {#} u  =  {#} MeV out": "mangler {#} u  =  {#} MeV ud",
  "n τE (s/m³)": "n τE (s/m³)",
  "negative: turns the other way": "negativ: drejer den anden vej",
  "neutron escapes": "neutronen slipper væk",
  "peak near {#} keV": "top nær {#} keV",
  "per fusion neutron · {#} neutrons · cross sections are simple fits": "pr. fusionsneutron · {#} neutroner · tværsnit er simple tilpasninger",
  "plasma": "plasma",
  "product ×{a}": "produkt ×{a}",
  "push {a} keV · chance to tunnel head-on {b}": "skub {a} keV · chance for at tunnelere frontalt {b}",
  "q = {#}": "q = {#}",
  "q = {#}/{#}: closes after {#} lap": "q = {#}/{#}: lukker efter {#} omgang",
  "q = {#}/{#}: closes after {#} laps": "q = {#}/{#}: lukker efter {#} omgange",
  "q = {#}: no simple fraction, the dots fill the circle": "q = {#}: ingen simpel brøk, prikkerne fylder cirklen",
  "screen radius is logarithmic: {#} fm to {#} fm": "radius på skærmen er logaritmisk: {#} fm til {#} fm",
  "shield": "skjold",
  "tap to fire": "tryk for at skyde",
  "the cut, flat": "snittet, fladt",
  "time slowed {a}×": "tiden sænket {a}×",
  "tries {#} · fused {#}": "forsøg {#} · fusioneret {#}",
  "tritium made, by depth": "dannet tritium efter dybde",
  "triton": "triton",
  "tunnels more easily": "tunnelerer lettere",
  "turns at {#} fm": "vender ved {#} fm",
  "wall": "væg",
  "{#} MeV": "{#} MeV",
  "{#} cm": "{#} cm",
  "{#} in {a}": "{#} ud af {a}",
  "{#} keV": "{#} keV",
  "{#} keV = {#} million K": "{#} keV = {#} millioner K",
  "{a} %": "{a} %",
  "{a} + {a} → {b}: about {c} MeV released": "{a} + {a} → {b}: omkring {c} MeV frigivet",
  "{a} + {a} → {b}: costs {c} MeV": "{a} + {a} → {b}: koster {c} MeV",
  "{a} keV · chance {b}": "{a} keV · chance {b}",
  "{a} keV · nτ {b} · {c}": "{a} keV · nτ {b} · {c}",
  "{a} · two branches, equally likely": "{a} · to grene, lige sandsynlige",
  "{a} · ρ up to {b} · {c} turns a second": "{a} · ρ op til {b} · {c} omløb i sekundet",
  "σ at {#} MeV:  (n,α) {#} mb · (n,p) {#} mb · (n,{#}n) {#} mb": "σ ved {#} MeV:  (n,α) {#} mb · (n,p) {#} mb · (n,{#}n) {#} mb",
  "⁶Li {#} · ⁷Li {#} · (n,{#}n) {#}": "⁶Li {#} · ⁷Li {#} · (n,{#}n) {#}",
  "⁶Li {#} · ⁷Li {#} · (n,{#}n) {#} · captured {#} · leaked {#}": "⁶Li {#} · ⁷Li {#} · (n,{#}n) {#} · indfanget {#} · lækket {#}",
  "⟨σv⟩ (m³/s)": "⟨σv⟩ (m³/s)",
});
