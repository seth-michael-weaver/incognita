/* Dutch (Nederlands): fusion (Hoofdstuk 29, fusie-energie en de coulombbarrière) */
WT.L.ch.fusion = {
  num: "Hoofdstuk 29", title: "Fusie-energie en de coulombbarrière", short: "Fusie",
  lead: "Fusie werkt andersom dan splijting: twee lichte kernen smelten samen, en het paar weegt minder dan zijn delen.",
  html: `
<div class="step">
  <h3>Fusie-energie uit de bindingscurve</h3>
  <p>Voeg twee lichte kernen samen: als de nieuwe hoger op de bindingscurve zit, komt er energie vrij. Voorbij de ijzerpiek kost samenvoegen energie.</p>
  <div class="ctl"><label for="fu-a">Elke lichte kern A</label><input id="fu-a" type="range" data-bind="fuse" data-instant min="2" max="60" step="1" value="2"><output data-show="fuse" data-fmt="0"></output></div>
  <p class="ctl-result" id="fu-fuse-out" aria-live="polite"></p>
</div>
<div class="step">
  <h3>Coulombbarrière en tunnelen</h3>
  <p>Trek het deuteron naar achteren en laat los. Beide kernen zijn geladen, dus de meeste schoten ketsen af op de heuvel; een paar tunnelen erdoor.</p>
  <div class="ctl"><label for="fu-e">Duw (keV)</label><input id="fu-e" type="range" data-bind="lE" min="0.5" max="2.6" step="0.01" value="1.7"><output data-show="E" data-fmt="0"></output></div>
  <div class="btns"><button class="btn" data-act="fire">Schiet</button></div>
</div>
<div class="step">
  <h3>Reactieproducten en Q-waarde</h3>
  <p>Het samengevoegde paar is lichter dan de twee delen. De ontbrekende massa vliegt weg als snelle deeltjes.</p>
  <div class="btns fu-fuels"><button class="btn ghost" data-act="DT" aria-pressed="true">D–T</button> <button class="btn ghost" data-act="DD" aria-pressed="false">D–D</button> <button class="btn ghost" data-act="DHe" aria-pressed="false">D–³He</button> <button class="btn ghost" data-act="pB" aria-pressed="false">p–¹¹B</button></div>
</div>
<div class="step">
  <h3>Thermonucleaire reactiesnelheid</h3>
  <p>In een heet gas komen de snelste kernen erdoor. Elke flits is één fusie.</p>
  <div class="ctl"><label for="fu-t">Temperatuur (keV)</label><input id="fu-t" type="range" data-bind="lT" min="0" max="2" step="0.01" value="1"><output data-show="T" data-fmt="1"></output></div>
</div>`,
};

// canvas labels of chapters 29-32 (fusion, gamow, tokamak, blanket)
Object.assign(WT.L.labels, {
  "B": "B",
  "Copper{#}": "Koper{#}",
  "Coulomb hill": "coulombheuvel",
  "D–D": "D–D",
  "D–T": "D–T",
  "D–³He": "D–³He",
  "E = kT": "E = kT",
  "Gamow peak E₀": "gamowpiek E₀",
  "K {#} · field lines lost to the wall: {#}": "K {#} · veldlijnen verloren aan de wand: {#}",
  "Q = {#}": "Q = {#}",
  "Q = ∞: no heating needed": "Q = ∞: geen verwarming nodig",
  "Silicon{#} (SiC)": "Silicium{#} (SiC)",
  "Steel (iron{#})": "Staal (ijzer{#})",
  "Sun's core": "zonnekern",
  "TBR {#}": "TBR {#}",
  "Tungsten{#}": "Wolfraam{#}",
  "Vanadium{#}": "Vanadium{#}",
  "after {#} years at {#} MW/m² · {#} MeV neutrons only · σ from INCOGNITA library v{#}": "na {#} jaar bij {#} MW/m² · alleen neutronen van {#} MeV · σ uit INCOGNITA-bibliotheek v{#}",
  "almost never": "bijna nooit",
  "alpha {#} MeV": "alfa {#} MeV",
  "axis, q = {#}": "as, q = {#}",
  "binding per nucleon (MeV)": "binding per nucleon (MeV)",
  "bubble-chamber view, magnetic field into the page: charged products curl, the neutron leaves no track": "als in een bellenvat, magneetveld het scherm in: geladen producten krullen, het neutron laat geen spoor na",
  "burning on its own": "brandt vanzelf",
  "cooled down: plasma lost": "afgekoeld: plasma verloren",
  "cooling": "koelt af",
  "could not load the library file": "bibliotheekbestand niet geladen",
  "deuteron": "deuteron",
  "deuteron {#} keV": "deuteron {#} keV",
  "deuteron: pull back, let go": "deuteron: trek terug, laat los",
  "drag or tap a point; it runs on its own": "sleep of tik een punt; het loopt vanzelf",
  "easiest: {a} keV, nτT {b}": "makkelijkst: {a} keV, nτT {b}",
  "edge: q = {#} · lines that cross it are lost": "rand: q = {#} · lijnen erover gaan verloren",
  "electron {#} keV": "elektron {#} keV",
  "energy of the colliding pair (keV)": "energie van het botsende paar (keV)",
  "few are this fast": "weinig zijn zo snel",
  "fusion rate: {a} the rate at {b} keV": "fusiesnelheid: {a} die bij {b} keV",
  "grain boundary": "korrelgrens",
  "heating itself": "verwarmt zichzelf",
  "helium stays and gathers into bubbles; hydrogen mostly diffuses out": "helium blijft en klontert tot bellen; waterstof diffundeert grotendeels weg",
  "helium {#} appm": "helium {#} appm",
  "hill to climb: charge product Z₁Z₂ = {#}": "heuvel om te nemen: ladingsproduct Z₁Z₂ = {#}",
  "hold: heaters on (Q = fusion power / heating) · let go: heaters off, the plasma is on its own": "vasthouden: verwarming aan (Q = fusievermogen / verwarming) · loslaten: verwarming uit, plasma op zichzelf",
  "hydrogen {#} appm": "waterstof {#} appm",
  "ignition (Q = ∞)": "ontsteking (Q = ∞)",
  "kT (keV)": "kT (keV)",
  "kT {#} keV · E₀ {#} keV · width {#} keV": "kT {#} keV · E₀ {#} keV · breedte {#} keV",
  "kT {a} keV · D–T {b} m³/s · {c}× D–D": "kT {a} keV · D–T {b} m³/s · {c}× D–D",
  "keeps itself hot": "houdt zichzelf heet",
  "laps {#}": "rondes {#}",
  "lead–lithium": "lood–lithium",
  "liquid lithium": "vloeibaar lithium",
  "loading INCOGNITA's cross sections…": "werkzame doorsneden van INCOGNITA laden…",
  "missing {#} u  =  {#} MeV out": "ontbrekend {#} u  =  {#} MeV vrij",
  "n τE (s/m³)": "n τE (s/m³)",
  "negative: turns the other way": "negatief: draait andersom",
  "neutron escapes": "neutron ontsnapt",
  "peak near {#} keV": "piek rond {#} keV",
  "per fusion neutron · {#} neutrons · cross sections are simple fits": "per fusieneutron · {#} neutronen · doorsneden zijn eenvoudige fits",
  "plasma": "plasma",
  "product ×{a}": "product ×{a}",
  "push {a} keV · chance to tunnel head-on {b}": "duw {a} keV · tunnelkans frontaal {b}",
  "q = {#}": "q = {#}",
  "q = {#}/{#}: closes after {#} lap": "q = {#}/{#}: sluit na {#} ronde",
  "q = {#}/{#}: closes after {#} laps": "q = {#}/{#}: sluit na {#} rondes",
  "q = {#}: no simple fraction, the dots fill the circle": "q = {#}: geen eenvoudige breuk, de punten vullen de cirkel",
  "screen radius is logarithmic: {#} fm to {#} fm": "straal is logaritmisch: {#} fm tot {#} fm",
  "shield": "schild",
  "tap to fire": "tik: schiet",
  "the cut, flat": "doorsnede, plat",
  "time slowed {a}×": "tijd {a}× vertraagd",
  "tries {#} · fused {#}": "schoten {#} · fusies {#}",
  "tritium made, by depth": "gekweekt tritium per diepte",
  "triton": "triton",
  "tunnels more easily": "tunnelt makkelijker",
  "turns at {#} fm": "keert om bij {#} fm",
  "wall": "wand",
  "{#} MeV": "{#} MeV",
  "{#} cm": "{#} cm",
  "{#} in {a}": "{#} op {a}",
  "{#} keV": "{#} keV",
  "{#} keV = {#} million K": "{#} keV = {#} miljoen K",
  "{a} %": "{a} %",
  "{a} + {a} → {b}: about {c} MeV released": "{a} + {a} → {b}: ongeveer {c} MeV vrij",
  "{a} + {a} → {b}: costs {c} MeV": "{a} + {a} → {b}: kost {c} MeV",
  "{a} keV · chance {b}": "{a} keV · kans {b}",
  "{a} keV · nτ {b} · {c}": "{a} keV · nτ {b} · {c}",
  "{a} · two branches, equally likely": "{a} · twee takken, even waarschijnlijk",
  "{a} · ρ up to {b} · {c} turns a second": "{a} · ρ tot {b} · {c} omlopen per seconde",
  "σ at {#} MeV:  (n,α) {#} mb · (n,p) {#} mb · (n,{#}n) {#} mb": "σ bij {#} MeV:  (n,α) {#} mb · (n,p) {#} mb · (n,{#}n) {#} mb",
  "⁶Li {#} · ⁷Li {#} · (n,{#}n) {#}": "⁶Li {#} · ⁷Li {#} · (n,{#}n) {#}",
  "⁶Li {#} · ⁷Li {#} · (n,{#}n) {#} · captured {#} · leaked {#}": "⁶Li {#} · ⁷Li {#} · (n,{#}n) {#} · ingevangen {#} · ontsnapt {#}",
  "⟨σv⟩ (m³/s)": "⟨σv⟩ (m³/s)",
});
