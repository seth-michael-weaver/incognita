/* German (Deutsch): fusion (Kapitel 29, Fusionsenergie und die Coulomb-Barriere) */
WT.L.ch.fusion = {
  num: "Kapitel 29", title: "Fusionsenergie und die Coulomb-Barriere", short: "Fusion",
  lead: "Fusion läuft andersherum als Spaltung: Zwei leichte Kerne verbinden sich, und das Paar wiegt weniger als seine Teile.",
  html: `
<div class="step">
  <h3>Fusionsenergie aus der Bindungskurve</h3>
  <p>Verbinde zwei leichte Kerne: Liegt der neue höher auf der Bindungskurve, wird Energie frei. Jenseits des Eisengipfels kostet das Verbinden Energie.</p>
  <div class="ctl"><label for="fu-a">Jeder leichte Kern A</label><input id="fu-a" type="range" data-bind="fuse" data-instant min="2" max="60" step="1" value="2"><output data-show="fuse" data-fmt="0"></output></div>
  <p class="ctl-result" id="fu-fuse-out" aria-live="polite"></p>
</div>
<div class="step">
  <h3>Coulomb-Barriere und Tunneln</h3>
  <p>Zieh das Deuteron zurück und lass los. Beide Kerne sind geladen, also prallen die meisten Schüsse am Hügel ab; einige wenige tunneln hindurch.</p>
  <div class="ctl"><label for="fu-e">Schub (keV)</label><input id="fu-e" type="range" data-bind="lE" min="0.5" max="2.6" step="0.01" value="1.7"><output data-show="E" data-fmt="0"></output></div>
  <div class="btns"><button class="btn" data-act="fire">Abschießen</button></div>
</div>
<div class="step">
  <h3>Reaktionsprodukte und Q-Wert</h3>
  <p>Das verbundene Paar ist leichter als die beiden Teile. Die fehlende Masse fliegt als schnelle Teilchen davon.</p>
  <div class="btns fu-fuels"><button class="btn ghost" data-act="DT" aria-pressed="true">D–T</button> <button class="btn ghost" data-act="DD" aria-pressed="false">D–D</button> <button class="btn ghost" data-act="DHe" aria-pressed="false">D–³He</button> <button class="btn ghost" data-act="pB" aria-pressed="false">p–¹¹B</button></div>
</div>
<div class="step">
  <h3>Thermonukleare Reaktionsrate</h3>
  <p>In einem heißen Gas kommen die schnellsten Kerne durch. Jeder Blitz ist eine Fusion.</p>
  <div class="ctl"><label for="fu-t">Temperatur (keV)</label><input id="fu-t" type="range" data-bind="lT" min="0" max="2" step="0.01" value="1"><output data-show="T" data-fmt="1"></output></div>
</div>`,
};

// canvas labels of chapters 29-32 (fusion, gamow, tokamak, blanket)
Object.assign(WT.L.labels, {
  "B": "B",
  "Copper{#}": "Kupfer{#}",
  "Coulomb hill": "Coulomb-Hügel",
  "D–D": "D–D",
  "D–T": "D–T",
  "D–³He": "D–³He",
  "E = kT": "E = kT",
  "Gamow peak E₀": "Gamow-Peak E₀",
  "K {#} · field lines lost to the wall: {#}": "K {#} · Feldlinien an die Wand verloren: {#}",
  "Q = {#}": "Q = {#}",
  "Q = ∞: no heating needed": "Q = ∞: keine Heizung nötig",
  "Silicon{#} (SiC)": "Silizium{#} (SiC)",
  "Steel (iron{#})": "Stahl (Eisen{#})",
  "Sun's core": "Sonnenkern",
  "TBR {#}": "TBR {#}",
  "Tungsten{#}": "Wolfram{#}",
  "Vanadium{#}": "Vanadium{#}",
  "after {#} years at {#} MW/m² · {#} MeV neutrons only · σ from INCOGNITA library v{#}": "nach {#} Jahren bei {#} MW/m² · nur {#}-MeV-Neutronen · σ aus INCOGNITA-Bibliothek v{#}",
  "almost never": "fast nie",
  "alpha {#} MeV": "Alpha {#} MeV",
  "axis, q = {#}": "Achse, q = {#}",
  "binding per nucleon (MeV)": "Bindung pro Nukleon (MeV)",
  "bubble-chamber view, magnetic field into the page: charged products curl, the neutron leaves no track": "Blasenkammer-Ansicht, Magnetfeld in die Seite: geladene Produkte krümmen sich, das Neutron hinterlässt keine Spur",
  "burning on its own": "brennt von selbst",
  "cooled down: plasma lost": "abgekühlt: Plasma verloren",
  "cooling": "kühlt ab",
  "could not load the library file": "Bibliotheksdatei nicht ladbar",
  "deuteron": "Deuteron",
  "deuteron {#} keV": "Deuteron {#} keV",
  "deuteron: pull back, let go": "Deuteron: zurückziehen, loslassen",
  "drag or tap a point; it runs on its own": "Punkt ziehen oder tippen; es läuft allein",
  "easiest: {a} keV, nτT {b}": "optimal: {a} keV, nτT {b}",
  "edge: q = {#} · lines that cross it are lost": "Rand: q = {#} · Linien darüber sind verloren",
  "electron {#} keV": "Elektron {#} keV",
  "energy of the colliding pair (keV)": "Energie des Stoßpaars (keV)",
  "few are this fast": "selten so schnell",
  "fusion rate: {a} the rate at {b} keV": "Fusionsrate: {a} der Rate bei {b} keV",
  "grain boundary": "Korngrenze",
  "heating itself": "heizt sich selbst",
  "helium stays and gathers into bubbles; hydrogen mostly diffuses out": "Helium bleibt und sammelt sich in Blasen; Wasserstoff diffundiert meist hinaus",
  "helium {#} appm": "Helium {#} appm",
  "hill to climb: charge product Z₁Z₂ = {#}": "Hügelhöhe: Ladungsprodukt Z₁Z₂ = {#}",
  "hold: heaters on (Q = fusion power / heating) · let go: heaters off, the plasma is on its own": "halten: Heizung an (Q = Fusionsleistung / Heizung) · loslassen: Heizung aus, das Plasma ist auf sich gestellt",
  "hydrogen {#} appm": "Wasserstoff {#} appm",
  "ignition (Q = ∞)": "Zündung (Q = ∞)",
  "kT (keV)": "kT (keV)",
  "kT {#} keV · E₀ {#} keV · width {#} keV": "kT {#} keV · E₀ {#} keV · Breite {#} keV",
  "kT {a} keV · D–T {b} m³/s · {c}× D–D": "kT {a} keV · D–T {b} m³/s · {c}× D–D",
  "keeps itself hot": "hält sich heiß",
  "laps {#}": "Umläufe {#}",
  "lead–lithium": "Blei–Lithium",
  "liquid lithium": "flüssiges Lithium",
  "loading INCOGNITA's cross sections…": "lade INCOGNITAs Wirkungsquerschnitte…",
  "missing {#} u  =  {#} MeV out": "fehlende {#} u  =  {#} MeV frei",
  "n τE (s/m³)": "n τE (s/m³)",
  "negative: turns the other way": "negativ: dreht andersherum",
  "neutron escapes": "Neutron entweicht",
  "peak near {#} keV": "Maximum bei {#} keV",
  "per fusion neutron · {#} neutrons · cross sections are simple fits": "pro Fusionsneutron · {#} Neutronen · Wirkungsquerschnitte als einfache Fits",
  "plasma": "Plasma",
  "product ×{a}": "Produkt ×{a}",
  "push {a} keV · chance to tunnel head-on {b}": "Schub {a} keV · Tunnelchance frontal {b}",
  "q = {#}": "q = {#}",
  "q = {#}/{#}: closes after {#} lap": "q = {#}/{#}: schließt nach {#} Umlauf",
  "q = {#}/{#}: closes after {#} laps": "q = {#}/{#}: schließt nach {#} Umläufen",
  "q = {#}: no simple fraction, the dots fill the circle": "q = {#}: kein einfacher Bruch, die Punkte füllen den Kreis",
  "screen radius is logarithmic: {#} fm to {#} fm": "Radius logarithmisch: {#} fm bis {#} fm",
  "shield": "Schild",
  "tap to fire": "tippen: los",
  "the cut, flat": "Schnitt, flach",
  "time slowed {a}×": "Zeitlupe {a}×",
  "tries {#} · fused {#}": "Schüsse {#} · Fusionen {#}",
  "tritium made, by depth": "Tritium nach Tiefe",
  "triton": "Triton",
  "tunnels more easily": "tunnelt leichter",
  "turns at {#} fm": "kehrt um bei {#} fm",
  "wall": "Wand",
  "{#} MeV": "{#} MeV",
  "{#} cm": "{#} cm",
  "{#} in {a}": "{#} zu {a}",
  "{#} keV": "{#} keV",
  "{#} keV = {#} million K": "{#} keV = {#} Millionen K",
  "{a} %": "{a} %",
  "{a} + {a} → {b}: about {c} MeV released": "{a} + {a} → {b}: etwa {c} MeV frei",
  "{a} + {a} → {b}: costs {c} MeV": "{a} + {a} → {b}: kostet {c} MeV",
  "{a} keV · chance {b}": "{a} keV · Chance {b}",
  "{a} keV · nτ {b} · {c}": "{a} keV · nτ {b} · {c}",
  "{a} · two branches, equally likely": "{a} · zwei Zweige, gleich wahrscheinlich",
  "{a} · ρ up to {b} · {c} turns a second": "{a} · ρ bis {b} · {c} Umläufe pro Sekunde",
  "σ at {#} MeV:  (n,α) {#} mb · (n,p) {#} mb · (n,{#}n) {#} mb": "σ bei {#} MeV:  (n,α) {#} mb · (n,p) {#} mb · (n,{#}n) {#} mb",
  "⁶Li {#} · ⁷Li {#} · (n,{#}n) {#}": "⁶Li {#} · ⁷Li {#} · (n,{#}n) {#}",
  "⁶Li {#} · ⁷Li {#} · (n,{#}n) {#} · captured {#} · leaked {#}": "⁶Li {#} · ⁷Li {#} · (n,{#}n) {#} · eingefangen {#} · entwichen {#}",
  "⟨σv⟩ (m³/s)": "⟨σv⟩ (m³/s)",
});
