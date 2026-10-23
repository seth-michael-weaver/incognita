/* German (Deutsch): compound (Kapitel 5, der Compoundkern) */
WT.L.ch.compound = {
  num: "Kapitel 5", title: "Die Energie teilen", short: "Compoundkern",
  lead: "Sobald die ersten schnellen Stöße vorbei sind, teilen sich alle Nukleonen die Energie. Dieser beruhigte Zustand ist der Compoundkern. Um vorherzusagen, was er als Nächstes tut, muss die Engine wissen, auf wie viele Arten er seine Energie halten kann.",
  html: `
<div class="step">
  <p>Ein Neutron trifft eine Seite eines Kerns. Seine Energie und die bei seinem Einfang frei werdende Energie bilden zunächst einen heißen Fleck (das orange Leuchten); Stöße geben sie weiter, und innerhalb von etwa 10⁻²¹ Sekunden trägt jedes Nukleon einen Anteil.</p>
  <div class="btns"><button class="btn" data-act="hit">Von einer anderen Seite treffen</button></div>
  <p>Drück den Knopf, um das Neutron von einer anderen Seite hineinzuschicken. Das Leuchten endet immer gleich: Der Kern hat <b>vergessen, wie er entstanden ist</b>. Das ist Bohrs Compoundkern. Von hier an zählen nur noch drei Dinge: seine Energie, sein Spin (wie stark er rotiert) und seine Parität (ein Etikett + oder − für seine Spiegelsymmetrie).</p>
</div>
<div class="step">
  <h3>Von einzelnen Niveaus zum Kontinuum</h3>
  <p>Die Leiter links enthält die Zustände des Kerns, die Energie steigt nach oben; das Fenster rechts vergrößert einen 1 MeV breiten Ausschnitt um die orange Kugel. Ganz unten liegen die Sprossen weit auseinander, und jede wurde gemessen. Weiter oben vervielfachen sich die Möglichkeiten, die Energie auf 56 Nukleonen zu verteilen, bis die Sprossen zu einem durchgehenden Band verschwimmen, dem Kontinuum.</p>
  <div class="ctl"><label for="cn-e">Anregungsenergie</label><input id="cn-e" type="range" data-bind="E" min="0" max="20" step="0.1" value="6.5"><output data-show="E" data-fmt="1"></output></div>
  <p>Ändere die Anregungsenergie (die Energie oberhalb des tiefsten Zustands, in MeV) und beobachte das Fenster. Die <b>Niveaudichte</b> ρ, Zustände pro MeV, wächst ungefähr wie e<sup>2√(aE)</sup>, wobei <i>a</i> das Tempo jedes Kerns bestimmt: einige pro MeV bei 3 MeV, Hunderte nahe 8 MeV (wo ein Neutron entkommen könnte), Millionen bei 20 MeV. Dort oben arbeitet die Engine mit ρ selbst.</p>
</div>
<div class="step">
  <h3>Drei Stücke, bei einer Energie verbunden</h3>
  <p>Die Höhe des Geländes ist die Niveaudichte auf logarithmischer Skala, die Energie nach rechts. Unten links stehen die gezählten Niveaus. Die gerade Planke ist das Gesetz der <b>konstanten Temperatur</b>: ρ vervielfacht sich alle <i>T</i> MeV um e (etwa 2,7), wobei <i>T</i> die Kerntemperatur ist. Der Hang ist das <b>Fermi-Gas</b>, das die Nukleonen als unabhängige Teilchen behandelt. Außer bei den schwersten Targets, für die sie tabellierte Dichten liest, verwendet die Engine standardmäßig dieses Paar.</p>
  <div class="ctl"><label for="cn-ex">Anschlussenergie</label><input id="cn-ex" type="range" data-bind="Ex" min="4.5" max="12" step="0.05" value="6"><output data-show="Ex" data-fmt="1"></output></div>
  <p>Ändere die Anschlussenergie: Die Verbindungsstelle gleitet den Hang entlang, und die Planke dreht sich, um sie mit derselben Höhe und Steigung zu treffen. Die zwei Stapel darunter vergleichen die Niveaus, die die Planke vorhersagt, mit den tatsächlich gezählten. Nur eine Verbindungsstelle macht sie gleich; dort wird die Planke grün. Das ist die Energie, die die Engine wählt.</p>
</div>
<div class="step">
  <h3>Schalen, die schmelzen</h3>
  <p>Einteilchenniveaus, je zwei Nukleonen, für zwei Kerne. Links eine abgeschlossene Schale: Alles unterhalb einer großen Lücke ist voll, also bezahlt jede Bewegung die ganze Lücke. Rechts ein Kern in der Schalenmitte mit halb vollem obersten Niveau, sodass es sofort billige Bewegungen gibt. Jeder Zähler zeigt, wie viele Anordnungen die gegebene Wärme aufnehmen.</p>
  <div class="ctl"><label for="cn-u">Wärme (Anregung)</label><input id="cn-u" type="range" data-bind="U" min="0" max="40" step="0.5" value="3"><output data-show="U" data-fmt="1"></output></div>
  <p>Erhöhe die Wärme und sieh den Nukleonen beim Springen zu. Bei wenig Wärme fehlen der abgeschlossenen Schale die Anordnungen; mit genug Wärme spielt die Lücke keine Rolle mehr, und beide Zahlen wachsen gleich. Der <b>Niveaudichteparameter</b> <i>a</i> erfasst das: Die Nadeln starten auseinander und laufen über etwa 10 MeV auf den glatten Wert <i>ã</i> zu. Die Engine lässt die Schalenkorrektur δW mit einer Rate γ abklingen:</p>
  <div class="formula">a(U) = ã · [1 + δW · (1 − e<sup>−γU</sup>) / U]</div>
</div>
<div class="step">
  <h3>Nach Spin und Parität sortiert</h3>
  <p>Die Zustände bei einer Energie fallen nach dem Spin <i>J</i>, dem Drehimpuls des Kerns, in Schubladen: volle Marken für Parität +, hohle für −. Die mittleren Schubladen füllen sich am meisten, gemäß (2<i>J</i>+1) e<sup>−(J+½)²/2σ²</sup>, wobei der Spin-Cutoff σ die Breite festlegt. Die beiden Paritäten kommen etwa gleich oft vor.</p>
  <div class="ctl"><label for="cn-u2">Anregung</label><input id="cn-u2" type="range" data-bind="U2" min="1" max="30" step="0.5" value="8"><output data-show="U2" data-fmt="1"></output></div>
  <div class="btns"><button class="btn ghost" data-act="deform">Kern deformieren</button></div>
  <p>Erhöhe die Anregung: σ wächst, weil ein heißerer Kern mehr Spin tragen kann. Drück dann auf Deformieren. Ein footballförmiger Kern kann außerdem als Ganzes rotieren, also gewinnt jede Schublade Zustände hinzu (die blauen Marken): die <b>kollektive Verstärkung</b>. Standardmäßig fügt die Engine sie nur für Targets mit mehr als etwa 215 Nukleonen hinzu.</p>
</div>
<div class="step">
  <h3>In Intervalle zerlegt</h3>
  <p>Oberhalb des letzten gezählten Niveaus zerlegt die Engine das Kontinuum in Scheiben gleicher Energiebreite, die Intervalle (Bins). In jedem Intervall fallen die Punkte zu einem Block aus ρ·ΔE Zuständen zusammen (ΔE ist die Intervallbreite), sortiert nach Spin und Parität wie oben.</p>
  <div class="ctl"><label for="cn-emax">Oberes Ende der Leiter</label><input id="cn-emax" type="range" data-bind="Emax" min="8" max="30" step="0.5" value="14"><output data-show="Emax" data-fmt="1"></output></div>
  <div class="btns"><button class="btn ghost" data-act="rebin">Neu sortieren</button></div>
  <p>Ändere das obere Ende der Leiter, die größte Energie, die das Neutron mitbringen kann. Dieselbe Zahl von Intervallen muss mehr Energie abdecken, also wird jedes höher. Die orange Kugel fällt von Intervall zu Intervall: Jeder spätere Schritt (einen Ausgang wählen, die Photonenkaskade, der Weg hinab über die Nuklidkarte) arbeitet mit diesen Intervallen. Hier sind zehn gezeichnet; die Engine verwendet bis zu 40.</p>
  <div class="aside">Im Code: <code>density/parameters.py</code> (Ignatyuk-<i>a</i>(U), Spin-Cutoff, Wigner-Verteilung, kollektive Verstärkung), <code>density/models.py</code> (konstante Temperatur, Fermi-Gas, Tabellen), <code>density/matching.py</code> (die Anschlussenergie aus den gezählten Niveaus), <code>core/grids.py</code> (Anregungsintervalle).</div>
</div>`,
};
(function () {
  const L = {
    // scene 1
    "a neutron comes in": "ein Neutron kommt herein",
    "a hot spot: the energy is still local": "ein heißer Fleck: die Energie ist noch lokal",
    "equilibrium: every nucleon holds a share": "Gleichgewicht: jedes Nukleon trägt einen Anteil",
    "no trace left of where it was hit": "keine Spur mehr davon, wo er getroffen wurde",
    // scene 2
    "ground state": "Grundzustand",
    "{#}–{#} MeV, magnified": "{#}–{#} MeV, vergrößert",
    "no level in this slice": "kein Niveau in diesem Ausschnitt",
    "{#} rung in {#} MeV": "{#} Sprosse in {#} MeV",
    "{#} rungs in {#} MeV": "{#} Sprossen in {#} MeV",
    "{#} rung in this {#}-MeV slice": "{#} Sprosse in diesem {#}-MeV-Ausschnitt",
    "{#} rungs in this {#}-MeV slice": "{#} Sprossen in diesem {#}-MeV-Ausschnitt",
    "about {#} rungs: too close to draw": "etwa {#} Sprossen: zu dicht zum Zeichnen",
    "about {#}k rungs: too close to draw": "etwa {#} Tsd. Sprossen: zu dicht zum Zeichnen",
    "about {#}M rungs: too close to draw": "etwa {#} Mio. Sprossen: zu dicht zum Zeichnen",
    "about {#}B rungs: too close to draw": "etwa {#} Mrd. Sprossen: zu dicht zum Zeichnen",
    "about {#} rungs in this slice: too close to draw": "etwa {#} Sprossen in diesem Ausschnitt: zu dicht zum Zeichnen",
    "about {#} thousand rungs in this slice: too close to draw": "etwa {#} Tausend Sprossen in diesem Ausschnitt: zu dicht zum Zeichnen",
    "about {#} million rungs in this slice: too close to draw": "etwa {#} Millionen Sprossen in diesem Ausschnitt: zu dicht zum Zeichnen",
    "about {#} billion rungs in this slice: too close to draw": "etwa {#} Milliarden Sprossen in diesem Ausschnitt: zu dicht zum Zeichnen",
    "each one measured: energy, spin and parity": "jede gemessen: Energie, Spin und Parität",
    "the rungs are multiplying": "die Sprossen vervielfachen sich",
    "a continuum: the engine uses ρ itself": "ein Kontinuum: die Engine nutzt ρ selbst",
    "≈ energy to free a neutron": "≈ Energie, um ein Neutron freizusetzen",
    "energy ↑": "Energie ↑",
    // scene 3
    "gap: plank below the rungs": "Lücke: Planke unter den Sprossen",
    "gap: plank above the rungs": "Lücke: Planke über den Sprossen",
    "counted levels": "gezählte Niveaus",
    "CT plank": "KT-Planke",
    "constant-temperature plank": "Planke der konstanten Temperatur",
    "Fermi-gas hillside": "Fermi-Gas-Hang",
    "joint {#} MeV": "Verbindung {#} MeV",
    "energy →": "Energie →",
    "+{#} more": "+{#} weitere",
    "{#} counted": "{#} gezählt",
    "{#} predicted": "{#} vorhergesagt",
    "{#}+ predicted": "{#}+ vorhergesagt",
    "equal: the plank rests on the counted rungs": "gleich: die Planke liegt auf den gezählten Sprossen",
    "too few: the plank is too steep and sinks": "zu wenige: die Planke ist zu steil und sinkt",
    "too many: the plank is too shallow and floats": "zu viele: die Planke ist zu flach und schwebt",
    // scene 4
    "closed shell": "abgeschlossene Schale",
    "mid-shell": "Schalenmitte",
    "gap": "Lücke",
    "no arrangement holds this heat": "keine Anordnung nimmt diese Wärme auf",
    "≈ {#} arrangement": "≈ {#} Anordnung",
    "≈ {#} arrangements": "≈ {#} Anordnungen",
    "≈ {#} thousand arrangements": "≈ {#} Tausend Anordnungen",
    "≈ {#} million arrangements": "≈ {#} Millionen Anordnungen",
    "≈ {#} billion arrangements": "≈ {#} Milliarden Anordnungen",
    "a ≈ {#}": "a ≈ {#}",
    "cold: nobody can move": "kalt: keiner kann sich bewegen",
    "temperature ≈ {#} MeV": "Temperatur ≈ {#} MeV",
    // scene 5
    "states at {#} MeV": "Zustände bei {#} MeV",
    "spin J →": "Spin J →",
    "+ parity": "Parität +",
    "− parity": "Parität −",
    "rotation ×{#}": "Rotation ×{#}",
    "added by rotation: ×{#} (a few drawn)": "durch Rotation hinzu: ×{#} (einige gezeichnet)",
    "spread σ ≈ {#}: most states near J ≈ {#}": "Breite σ ≈ {#}: die meisten Zustände nahe J ≈ {#}",
    "deformed: it can rotate": "deformiert: er kann rotieren",
    "spherical": "sphärisch",
    // scene 6
    "≈ {#} thousand": "≈ {#} Tausend",
    "≈ {#} million": "≈ {#} Millionen",
    "≈ {#} billion": "≈ {#} Milliarden",
    "≈ {#}k": "≈ {#} Tsd.",
    "≈ {#}M": "≈ {#} Mio.",
    "≈ {#}B": "≈ {#} Mrd.",
    "{#} bins, each {#} MeV wide": "{#} Intervalle, je {#} MeV breit",
    "counted": "gezählt",
    "states in each bin": "Zustände pro Intervall",
  };
  Object.assign(WT.L.labels, L);
})();
