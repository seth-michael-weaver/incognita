/* German (Deutsch): structure (Kapitel 1, woraus ein Kern besteht) */
WT.L.ch.structure = {
  num: "Kapitel 1", title: "Woraus ein Kern besteht", short: "Struktur",
  lead: "Bevor die Engine (unsere Reaktionssoftware) auch nur ein Neutron abfeuert, braucht sie eine Beschreibung des Targetkerns: wie fest er zusammenhält, in welchen Energiezuständen er sein kann und welche Form er hat.",
  html: `
<div class="step">
  <p>Das Bild zeigt einen Eisenkern: eine dicht gepackte Kugel aus <em class="p">Protonen</em> und <em class="n">Neutronen</em> (<b>Nukleonen</b>), zusammengehalten von der kurzreichweitigen <b>starken Kraft</b>. Jedes Nukleon spürt nur seine nächsten Nachbarn, deshalb hat jeder Kern ungefähr dieselbe Dichte.</p>
  <div class="ctl"><label for="st-n">Neutronen (Eisen hat 26 Protonen)</label><input id="st-n" type="range" data-bind="N" min="24" max="38" step="1" value="30" data-instant><output data-show="N" data-fmt="0"></output></div>
  <p>Zieh am Regler, um Neutronen hinzuzufügen oder zu entfernen; jede Wahl ist ein anderes <b>Isotop</b>. Die Balken zeigen die <b>Bindungsenergie</b> pro Nukleon in MeV (Millionen Elektronenvolt): die Energie, die nötig ist, um den Kern zu zerlegen. Sie erreicht ihr Maximum nahe den stabilen Isotopen.</p>
</div>
<div class="step">
  <h3>Separationsenergien</h3>
  <p>Die Energie, um ein Teilchen herauszuziehen, ist seine <b>Separationsenergie</b>: <i>S<sub>n</sub></i> für ein Neutron, <i>S<sub>p</sub></i> für ein Proton, <i>S<sub>α</sub></i> für ein <b>Alphateilchen</b> (zwei Protonen und zwei Neutronen, fest aneinander gebunden). Das Bild zeigt den Kern als Topf, die Energie nach oben aufgetragen; jedes Herausziehen hebt das oberste Teilchen über die gestrichelte Linie „frei“, und die Anzeige verbucht die Kosten.</p>
  <div class="btns"><button class="btn ghost" data-act="pn">Neutron herausziehen</button><button class="btn ghost" data-act="pp">Proton herausziehen</button><button class="btn ghost" data-act="pa">Alpha herausziehen</button></div>
  <p>Die Engine erhält jede davon als Differenz zweier Kernmassen: gemessen, wo möglich, sonst aus einem Massenmodell.</p>
  <div class="ctl"><label for="st-n2">Neutronen</label><input id="st-n2" type="range" data-bind="N" min="24" max="38" step="1" value="30" data-instant><output data-show="N" data-fmt="0"></output></div>
  <p>Ändere die Neutronenzahl und zieh noch einmal ein Neutron heraus: <i>S<sub>n</sub></i> springt im Zickzack, weil sich Nukleonen paaren und eine gerade Anzahl das letzte fester hält. Eine Reaktion kann ein Teilchen nur dann herauswerfen, wenn sie genug Energie mitbringt, um diese Kosten zu bezahlen. Diese Kosten sind die <b>Schwellen</b> der ganzen Rechnung.</p>
</div>
<div class="step">
  <h3>Angeregte Zustände und Gamma-Zerfall</h3>
  <p>Ein Kern kann nur bestimmte, exakte Mengen zusätzlicher Energie aufnehmen: die Linien, hier für Eisen-56, mit dem <b>Grundzustand</b> ganz unten. Jedes Niveau hat einen <b>Spin</b> <i>J</i> (Drehimpuls) und eine <b>Parität</b>, + oder − (ob seine Welle im Spiegel gleich aussieht); 2<sup>+</sup> bedeutet Spin 2, Parität +.</p>
  <p>Die orange Kugel ist ein Kern auf einem hohen Niveau. Er fällt Niveau für Niveau nach unten, und jeder Sprung wirft ein <em class="g">Photon</em> (einen Gammastrahl) ab, das die Energiedifferenz trägt. Breite und Prozentwert der Pfade sind die gemessenen Wahrscheinlichkeiten jedes Sprungs, die <b>Verzweigungsverhältnisse</b>.</p>
  <div class="btns"><button class="btn" data-act="drop">Kern anregen</button></div>
  <p>Drück ein paarmal: Dasselbe Niveau erreicht den Grundzustand auf verschiedenen Wegen. Die Engine führt etwa dreißig gemessene Niveaus pro Kern samt ihren Wahrscheinlichkeiten; weiter oben behandelt sie die dicht gedrängten Niveaus als glattes <b>Kontinuum</b>. Oberhalb der gestrichelten Linie, <i>S<sub>n</sub></i>, kann der Kern ein Neutron aussenden.</p>
</div>
<div class="step">
  <h3>Isomere: langlebige angeregte Zustände</h3>
  <p>Ein Niveau, dessen einziger Weg nach unten eine große Spinänderung Δ<i>J</i> erfordert, zerfällt sehr langsam. Rechts sitzen 64 Kerne auf so einem Niveau; jeder wartet eine zufällige Zeit, fällt dann hinunter, und ein <em class="g">Photon</em> springt heraus. Nach einer <b>Halbwertszeit</b> ist die Hälfte gefallen.</p>
  <div class="ctl"><label for="st-dj">Spinänderung ΔJ</label><input id="st-dj" type="range" data-bind="dJ" min="1" max="5" step="1" value="2" data-instant><output data-show="dJ" data-fmt="0"></output></div>
  <div class="ctl"><label for="st-eg">Photonenenergie (MeV)</label><input id="st-eg" type="range" data-bind="Eg" min="0.05" max="1.5" step="0.05" value="0.3"><output data-show="Eg" data-fmt="2"></output></div>
  <div class="btns"><button class="btn ghost" data-act="excite">Alle anregen</button></div>
  <p>Erhöhe Δ<i>J</i>, und das Aufblitzen wird langsamer: Jede zusätzliche Spineinheit macht die Wartezeit hunderttausendmal länger oder mehr, und eine kleinere Photonenenergie verlängert sie ebenfalls (logarithmisch dargestellt). Ein Niveau, das länger als etwa eine Sekunde lebt, ist ein <b>Isomer</b>, und die Engine behandelt es als Endpunkt, wie den Grundzustand.</p>
</div>
<div class="step">
  <h3>Kerndeformation</h3>
  <p>Viele Kerne sind nicht rund. <i>β₂</i> („Beta-zwei“) misst die Streckung: 0 ist eine Kugel, positiv ist gestreckt wie ein American Football, negativ ist zu einer Scheibe plattgedrückt. Die Leiter rechts zeigt die Niveaus, die jede Form hervorbringt.</p>
  <p>Ein gestreckter Kern kann rotieren und liefert dann Niveaus 0<sup>+</sup>, 2<sup>+</sup>, 4<sup>+</sup>, 6<sup>+</sup> mit Abständen, die wie <i>J</i>(<i>J</i>+1) wachsen: ein <b>Rotor</b>. Ein runder Kern kann schwingen; jedes Schwingungsquant, ein <b>Phonon</b>, fügt dieselbe Energie hinzu, also liegen seine Niveaus in gleichen Abständen: ein <b>Vibrator</b>.</p>
  <div class="ctl"><label for="st-beta">Deformation β₂</label><input id="st-beta" type="range" data-bind="beta" min="-0.3" max="0.45" step="0.01" value="0.28"><output data-show="beta" data-fmt="2"></output></div>
  <div class="btns"><button class="btn ghost" data-act="still">Ruhend</button><button class="btn ghost" data-act="vib">Schwingend</button><button class="btn ghost" data-act="rot">Rotierend</button></div>
  <p>Zieh an <i>β₂</i> und drück die Knöpfe: Eine stärkere Streckung rückt die Niveaus des Rotors enger zusammen. Ein Vibrator ist im Mittel rund, daher ruht der Regler, während er schwingt; und eine Kugel kann in diesem Sinn nicht rotieren (Drehen ändert nichts), daher verschwindet die Rotorbande nahe <i>β₂</i> = 0. Die Engine speichert für jeden Kern die Deformationen und eine Kennung: sphärisch, Vibrator oder Rotor. Kapitel 6 zeigt, wie ein vorbeifliegendes Neutron sie nutzt.</p>
</div>
<div class="step">
  <h3>Resonanzparameter oberhalb der Neutronenschwelle</h3>
  <p>Ein langsames Neutron, das sich dem Target anschließt, landet knapp über <i>S<sub>n</sub></i>, im kleinen Kasten links. Das rechte Feld vergrößert diesen Kasten tausendfach, die Neutronenenergie läuft von links nach rechts.</p>
  <div class="ctl"><label for="st-fe">Strahlenergie</label><input id="st-fe" type="range" data-bind="fe" min="0" max="1" step="0.001" value="0.3" data-instant><output id="st-fe-out"></output></div>
  <div class="btns"><button class="btn ghost" data-act="fplay" id="st-fplay">Durchlauf anhalten</button></div>
  <p>Bei den meisten Energien geht der Strahl einfach hindurch. Bei bestimmten exakten Energien passen Neutron und Kern zusammen genau zu einem verborgenen Niveau, und ein großer Teil des Strahls wird aufgenommen: eine <b>Resonanz</b>. Auf einem Peak schwillt der gezeichnete Kern an: keine echte Größenänderung, sondern das größere Ziel, das das Neutron effektiv sieht, wenn seine Welle mit der des Kerns überlappt. Der Kern gibt die Energie dann als <em class="g">Photon</em> oder Neutron wieder ab. Die Kurve zeigt den aufgenommenen Anteil; die Balken markieren jede gefundene Resonanz.</p>
  <div class="btns"><button class="btn ghost" data-act="fFe">Eisen-56</button><button class="btn ghost" data-act="fAu">Gold-197</button><button class="btn ghost" data-act="fU">Uran-238</button></div>
  <p>Jeder Kern hat seinen eigenen Strichcode in seinem eigenen Maßstab: Tausende Elektronenvolt zwischen den Resonanzen von Eisen, einige zehn bei Gold und Uran. Drei Mittelwerte fassen ihn zusammen: <i>D₀</i>, der mittlere Abstand; ⟨Γ<sub>γ</sub>⟩, die <b>Photonenbreite</b>, für jeden Peak fast gleich; und <i>S₀</i>, die <b>Stärkefunktion</b>, also wie leicht ein langsames Neutron hineinkommt.</p>
  <p>Jeder davon prüft einen späteren Schritt. Die Niveaudichteparameter der Engine wurden Kern für Kern an <i>D₀</i> angepasst; ⟨Γ<sub>γ</sub>⟩ testet die Photonenemission, <i>S₀</i> das optische Modell des nächsten Kapitels. Für nicht gemessene Kerne nutzt die Engine Trends, die über viele Kerne angepasst wurden.</p>
  <div class="aside">Im Code: <code>structure/masses.py</code> (gemessene Massen, jenseits davon Modellmassen, Separationsenergien), <code>structure/levels.py</code> (diskrete Niveaus, Verzweigungen, Isomere, geschätzte Spins) und <code>levjpar.py</code> (optional, standardmäßig aus: schätzt einen aufgeführten Spin neu, der für den Kern unmöglich ist), <code>structure/deformation.py</code> (β₂ und die Kennung sphärisch/Vibrator/Rotor) und <code>collrule.py</code> (optional, standardmäßig aus: wählt die Kennung des Targets anhand seiner gemessenen Niveaus), <code>structure/resonances.py</code> (D₀, S₀, S₁, ⟨Γγ⟩).</div>
</div>`,
};
(function () {
  const L = {
    // scene: packed drop
    "{#}Fe": "{#}Fe",
    "{#} protons · {#} neutrons": "{#} Protonen · {#} Neutronen",
    "binding energy per nucleon: about {#} MeV": "Bindungsenergie pro Nukleon: etwa {#} MeV",
    "binding per nucleon, one bar per isotope →": "Bindung pro Nukleon, ein Balken pro Isotop →",
    // scene: well
    "free": "frei",
    "free: outside the nucleus": "frei: außerhalb des Kerns",
    "neutrons": "Neutronen",
    "protons": "Protonen",
    "an alpha forms from the top pairs": "aus den obersten Paaren bildet sich ein Alpha",
    "neutron {#}": "Neutron {#}",
    "proton {#}": "Proton {#}",
    "alpha {#}": "Alpha {#}",
    "n {#}": "n {#}",
    "p {#}": "p {#}",
    "energy paid": "bezahlte Energie",
    "energy to pull": "Energie zum Herausziehen",
    "(MeV)": "(MeV)",
    "each one out (MeV)": "pro Teilchen (MeV)",
    "higher mark =": "höhere Marke =",
    "harder to remove": "schwerer zu entfernen",
    "pulling out a neutron: {#} MeV paid": "Neutron herausgezogen: {#} MeV bezahlt",
    "pulling out a proton: {#} MeV paid": "Proton herausgezogen: {#} MeV bezahlt",
    "pulling out an alpha: {#} MeV paid": "Alpha herausgezogen: {#} MeV bezahlt",
    // scene: levels and gamma drops
    "continuum: too many levels to list": "Kontinuum: zu viele Niveaus zum Auflisten",
    "neutron threshold Sₙ ≈ {#} MeV": "Neutronenschwelle Sₙ ≈ {#} MeV",
    "ground state": "Grundzustand",
    "MeV": "MeV",
    "each line: an energy, a spin J and a parity (±)": "jede Linie: eine Energie, ein Spin J und eine Parität (±)",
    "path width and % = measured odds of each hop": "Pfadbreite und % = gemessene Wahrscheinlichkeit jedes Sprungs",
    // scene: isomer
    "ground": "Grund",
    "J = {#}/{#}": "J = {#}/{#}",
    "ΔJ = {#}": "ΔJ = {#}",
    "still excited: {#} of {#}": "noch angeregt: {#} von {#}",
    "longer than a second: an isomer, a stop in its own right": "länger als eine Sekunde: ein Isomer, eine eigene Endstation",
    "shown slowed down (log scale)": "verlangsamt dargestellt (log. Skala)",
    "shown slowed down: the slower they pop, the longer the real wait (log scale)": "verlangsamt: je langsamer das Aufblitzen, desto länger die echte Wartezeit (log. Skala)",
    // scene: shape
    "ripples at the surface: a vibrator": "Wellen an der Oberfläche: ein Vibrator",
    "stretched and rotating: a rotor": "gestreckt und rotierend: ein Rotor",
    "round: a sphere": "rund: eine Kugel",
    "stretched (prolate): a football": "gestreckt (prolat): ein Football",
    "squashed: an oblate disc": "plattgedrückt: eine oblate Scheibe",
    "{#} phonons": "{#} Phononen",
    "no regular": "kein regelmäßiges",
    "level pattern": "Niveaumuster",
    "spacing grows like J(J+{#})": "Abstand wächst wie J(J+{#})",
    "equal steps, one phonon each": "gleiche Stufen, je ein Phonon",
    "its lowest levels": "seine tiefsten Niveaus",
    "β₂ = {#}": "β₂ = {#}",
    // scene: resonance fingerprint
    "continuum": "Kontinuum",
    "Sₙ ≈ {#} MeV": "Sₙ ≈ {#} MeV",
    "slow neutron": "langsames Neutron",
    "a slow neutron lands here:": "ein langsames Neutron landet hier:",
    "lands here": "landet hier",
    "Sₙ + its kinetic energy": "Sₙ + seine kinetische Energie",
    "×{#} million": "×{#} Millionen",
    "×{#} thousand": "×{#} Tausend",
    "magnified": "vergrößert",
    "swells on a peak: the size the neutron effectively “sees” (waves overlap), not a real size change": "schwillt auf einem Peak an: die Größe, die das Neutron effektiv „sieht“ (Wellen überlappen), keine echte Größenänderung",
    "share taken in": "aufgenommener Anteil",
    "share of the beam taken in": "aufgenommener Anteil des Strahls",
    "{#} (Sₙ)": "{#} (Sₙ)",
    "{#} = exactly Sₙ": "{#} = genau Sₙ",
    "{#} keV": "{#} keV",
    "{#} eV": "{#} eV",
    "neutron energy →": "Neutronenenergie →",
    "neutron's kinetic energy →": "kinetische Energie des Neutrons →",
    "D₀ ≈ {#} keV: the average gap": "D₀ ≈ {#} keV: der mittlere Abstand",
    "D₀ ≈ {#} eV: the average gap": "D₀ ≈ {#} eV: der mittlere Abstand",
    "S₀: average peak strength": "S₀: mittlere Peakstärke",
    "S₀: how strong the peaks are on average (how easily a neutron gets in)": "S₀: mittlere Stärke der Peaks (wie leicht ein Neutron hineinkommt)",
    "⟨Γγ⟩ ≈ {#} eV: photon width": "⟨Γγ⟩ ≈ {#} eV: Photonenbreite",
    "⟨Γγ⟩ ≈ {#} eV: photon width, about the same for every peak": "⟨Γγ⟩ ≈ {#} eV: Photonenbreite, für jeden Peak fast gleich",
    "⟨Γγ⟩ ≈ {#} eV: a hairline here": "⟨Γγ⟩ ≈ {#} eV: hier haarfein",
    "⟨Γγ⟩ ≈ {#} eV: a hairline here; neutrons widen these peaks": "⟨Γγ⟩ ≈ {#} eV: hier haarfein; Neutronen verbreitern diese Peaks",
    "peaks drawn about {#}× wider than life so they show": "Peaks etwa {#}× breiter gezeichnet als in Wirklichkeit, damit man sie sieht",
  };
  // beam readout and per-target labels
  for (const u of ["keV", "eV"]) L[`beam of neutrons at {#} ${u}`] = `Neutronenstrahl bei {#} ${u}`;
  const EL = { iron: "Eisen", gold: "Gold", uranium: "Uran" };
  for (const en in EL) {
    L[`${en}{#} levels`] = `Niveaus von ${EL[en]}{#}`;
    L[`${en}{#}: took in {#} of the last {#}`] = `${EL[en]}{#}: {#} der letzten {#} aufgenommen`;
  }
  // isomer half-life in every unit fmtTime can produce
  const TU = { femtoseconds: "Femtosekunden", picoseconds: "Pikosekunden", nanoseconds: "Nanosekunden", microseconds: "Mikrosekunden",
    milliseconds: "Millisekunden", seconds: "Sekunden", minutes: "Minuten", hours: "Stunden", days: "Tage", years: "Jahre" };
  for (const en in TU) L[`half-life about {#} ${en}`] = `Halbwertszeit etwa {#} ${TU[en]}`;
  L["half-life about {#}×{#}^{#} years"] = "Halbwertszeit etwa {#}×{#}^{#} Jahre";
  Object.assign(WT.L.labels, L);
})();
