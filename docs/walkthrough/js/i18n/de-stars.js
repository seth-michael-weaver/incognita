/* German (Deutsch): stars (Woher die Elemente kommen) */
WT.L.ch.stars = {
  num: "Lektion 1", title: "Woher die Elemente kommen", short: "Sterne",
  html: `
<div class="step">
  <h3>Die Fusion endet beim Eisen</h3>
  <p>Sterne verschmelzen leichte Kerne bis hinauf zum Eisen; fast alles Schwerere entsteht durch Anlagern von Neutronen.</p>
</div>
<div class="step">
  <h3>Der langsame Weg</h3>
  <p>In Riesensternen kommen Neutronen selten, sodass ein instabiler Kern zuerst einen Betazerfall macht: Der Pfad läuft im Zickzack an den stabilen Kernen entlang.</p>
  <div class="ctl"><label for="st-k">Neutroneneinfänge</label><input id="st-k" type="range" data-bind="k" min="0" max="213" step="1" value="112"></div>
</div>
<div class="step">
  <h3>Der schnelle Weg</h3>
  <p>Bei einer Neutronensternverschmelzung strömen Neutronen schneller ein, als Kerne zerfallen können; danach zerfallen die neutronenreichen Kerne zurück zur Stabilität.</p>
  <div class="ctl"><label for="st-rt">Zurückzerfallen</label><input id="st-rt" type="range" data-bind="rt" min="0" max="1" step="0.01" value="0"></div>
</div>
<div class="step">
  <h3>Magische Zahlen machen Maxima</h3>
  <p>Kerne mit 50, 82 oder 126 Neutronen fangen kaum ein, also staut sich dort Materie: s-Maxima bei Strontium, Barium und Blei, r-Maxima etwas leichter.</p>
  <div class="btns"><button class="btn ghost" data-act="stS" aria-pressed="true">s-Prozess-Maxima</button> <button class="btn ghost" data-act="stR" aria-pressed="true">r-Prozess-Maxima</button></div>
</div>
<div class="step">
  <h3>Selten, wo Einfang leicht ist</h3>
  <p>Für Isotope, die nur im s-Prozess entstehen, bleibt die Häufigkeit Nₛ mal Einfangquerschnitt σ zwischen magischen Zahlen nahezu konstant. σ ist hier der von INCOGNITA berechnete Wert bei 30 keV.</p>
  <div class="btns"><button class="btn ghost" data-act="stvs" aria-pressed="false">σ</button> <button class="btn ghost" data-act="stvn" aria-pressed="false">Nₛ</button> <button class="btn ghost" data-act="stvsn" aria-pressed="true">σ × Nₛ</button></div>
</div>
<div class="step">
  <h3>Mit Messungen verglichen</h3>
  <p>Die 30-keV-Werte von INCOGNITA geteilt durch gemessene, für 94 stabile Nuklide (<a href="scoreboard.html">Rangliste</a>).</p>
</div>`,
};

Object.assign(WT.L.labels, {
  " (scaled to a measured value)": " (auf einen Messwert skaliert)",
  " (σ scaled to a measured value)": " (σ auf einen Messwert skaliert)",
  "{a} % above measured": "{a} % über dem Messwert",
  "{a} % below measured": "{a} % unter dem Messwert",
  "{a} nuclides · typical difference {b} %": "{a} Nuklide · typische Abweichung {b} %",
  "{a} stable nuclides · typical difference {b} % (median), rms {c} %": "{a} stabile Nuklide · typische Abweichung {b} % (Median), rms {c} %",
  "{a}: INCOGNITA σ = {b} mb": "{a}: INCOGNITA σ = {b} mb",
  "{a}: INCOGNITA σ = {b} mb, {c}": "{a}: INCOGNITA σ = {b} mb, {c}",
  "{a}: INCOGNITA's engine {b} (the library then scales to it)": "{a}: INCOGNITA-Rechnung {b} (die Bibliothek skaliert dann darauf)",
  "{a}: σ = {b} mb × Nₛ = {c} → σNₛ = {d}": "{a}: σ = {b} mb × Nₛ = {c} → σNₛ = {d}",
  "↑ protons Z": "↑ Protonen Z",
  "A = {a}: mostly {b}, {c} atoms per million silicon": "A = {a}: überwiegend {b}, {c} Atome pro Million Silizium",
  "A ≈ {#}": "A ≈ {#}",
  "abundances: Lodders, Palme & Gail {#}": "Häufigkeiten: Lodders, Palme & Gail {#}",
  "abundances: Lodders, Palme & Gail {#} · point at the curve": "Häufigkeiten: Lodders, Palme & Gail {#} · auf die Kurve zeigen",
  "atoms per {#}⁶ silicon": "Atome pro {#}⁶ Silizium",
  "atoms per million silicon atoms (Solar System)": "Atome pro Million Siliziumatome (Sonnensystem)",
  "Ba": "Ba",
  "Ba{#}": "Ba{#}",
  "beta decay (n → p)": "Betazerfall (n → p)",
  "beta decays carry them back, mass number A fixed": "Betazerfälle bringen sie zurück, Massenzahl A bleibt",
  "beta decays, A fixed": "Betazerfälle, A fest",
  "Big Bang": "Urknall",
  "decayed back: each lands on the most neutron-rich stable isobar": "zurückzerfallen: jeder landet beim neutronenreichsten stabilen Isobar",
  "decayed back: r-made stable isotopes": "zurückzerfallen: im r-Prozess entstandene stabile Isotope",
  "drag along the path": "entlang des Pfads ziehen",
  "drag along the path, or use the slider": "entlang des Pfads ziehen oder den Schieberegler nutzen",
  "end of the road: Bi{#} → Po{#} → alpha decay back to Pb{#}": "Endstation: Bi{#} → Po{#} → Alphazerfall zurück zu Pb{#}",
  "end: the lead–bismuth cycle": "Ende: der Blei-Bismut-Zyklus",
  "Fe": "Fe",
  "flat between magic numbers, steps down at each": "flach zwischen magischen Zahlen, an jeder eine Stufe nach unten",
  "fusion": "Fusion",
  "fusion in stars": "Fusion in Sternen",
  "H": "H",
  "He": "He",
  "INCOGNITA ÷ measured, {#} keV": "INCOGNITA ÷ gemessen, {#} keV",
  "INCOGNITA: capture at {#} keV (MACS)": "INCOGNITA: Einfang bei {#} keV (MACS)",
  "INCOGNITA's {#} keV capture rate (MACS) ÷ measured": "Einfangrate von INCOGNITA bei {#} keV (MACS) ÷ gemessen",
  "Lodders et al. {#}": "Lodders et al. {#}",
  "Lu{#}": "Lu{#}",
  "made by neutron capture": "durch Neutroneneinfang entstanden",
  "magic N: captures poorly, matter piles up": "magisches N: fängt schlecht ein, Materie staut sich",
  "magic neutron number: it captures poorly, so matter piles up here": "magische Neutronenzahl: fängt schlecht ein, also staut sich hier Materie",
  "mass number A": "Massenzahl A",
  "mass number A (protons + neutrons)": "Massenzahl A (Protonen + Neutronen)",
  "mb": "mb",
  "N = {#}": "N = {#}",
  "nearly flat between magic numbers, a step down at each": "nahezu flach zwischen magischen Zahlen, an jeder eine Stufe nach unten",
  "neutron capture": "Neutroneneinfang",
  "neutrons N →": "Neutronen N →",
  "Nₛ alone jumps around the other way": "Nₛ allein springt in die Gegenrichtung",
  "Nₛ alone: scattered": "Nₛ allein: gestreut",
  "O": "O",
  "Pb": "Pb",
  "Pb{#}": "Pb{#}",
  "peaks: sources Lodders et al. {#}": "Maxima: Quellen Lodders et al. {#}",
  "plus a weaker s-process (massive stars)": "plus ein schwächerer s-Prozess (massereiche Sterne)",
  "r {#}": "r {#}",
  "r-path: illustration": "r-Pfad: Illustration",
  "r-peak Pt": "r-Maximum Pt",
  "r-peak Se, Kr": "r-Maximum Se, Kr",
  "r-peak Te, Xe": "r-Maximum Te, Xe",
  "r-process: a flood of neutrons makes very neutron-rich nuclei": "r-Prozess: eine Neutronenflut erzeugt sehr neutronenreiche Kerne",
  "r-process: very neutron-rich nuclei": "r-Prozess: sehr neutronenreiche Kerne",
  "ringed: s-only · measured: KADoNiS": "umringt: nur s · gemessen: KADoNiS",
  "ringed: s-only isotopes · measured: compiled values (KADoNiS) · a development comparison, not a blind test": "umringt: reine s-Isotope · gemessen: kompilierte Werte (KADoNiS) · ein Entwicklungsvergleich, kein Blindtest",
  "s Ba": "s Ba",
  "s Pb": "s Pb",
  "s Sr": "s Sr",
  "s-only isotopes · bars: INCOGNITA {#} %": "reine s-Isotope · Balken: INCOGNITA {#} %",
  "s-only isotopes · σ: INCOGNITA (bars: its {#} % range; open circle: scaled to a measurement) · Nₛ: Lodders et al. {#}": "reine s-Isotope · σ: INCOGNITA (Balken: ihr {#}-%-Bereich; offener Kreis: auf eine Messung skaliert) · Nₛ: Lodders et al. {#}",
  "s-peak Ba": "s-Maximum Ba",
  "s-peak Pb": "s-Maximum Pb",
  "s-peak Sr": "s-Maximum Sr",
  "seen in {#}: merger GW{#}": "beobachtet {#}: Verschmelzung GW{#}",
  "seen in {#}: the neutron-star merger GW{#} and its kilonova": "beobachtet {#}: die Neutronensternverschmelzung GW{#} und ihre Kilonova",
  "Sm{#}": "Sm{#}",
  "Sn": "Sn",
  "Sr": "Sr",
  "Sr{#}": "Sr{#}",
  "wait": "warten",
  "waiting point": "Wartepunkt",
  "weak s-process too": "auch schwacher s-Prozess",
  "σ × Nₛ (mb × atoms per {#}⁶ Si)": "σ × Nₛ (mb × Atome pro {#}⁶ Si)",
  "σ × Nₛ (mb × atoms per million Si)": "σ × Nₛ (mb × Atome pro Million Si)",
  "σ alone jumps around from isotope to isotope": "σ allein springt von Isotop zu Isotop",
});
