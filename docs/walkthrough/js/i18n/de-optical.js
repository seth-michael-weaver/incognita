/* German (Deutsch): optical (Kapitel 23, das optische Modell, gelöst) */
WT.L.ch.optical = {
  num: "Kapitel 23", title: "Das optische Modell, gelöst", short: "Optisches Modell, gelöst",
  lead: "Kapitel 5 hat das optische Potential als trübe Glaskugel gezeichnet. Hier erscheint es so, wie die Engine es verwendet: eine globale Parametrisierung, eine radiale Schrödinger-Gleichung, Schritt für Schritt integriert, und eine Anschlussbedingung, die aus der Welle Transmissionskoeffizienten macht.",
  html: `
<div class="step">
  <h3>Das Koning–Delaroche-Potential</h3>
  <p>Für Neutronen und Protonen an sphärischen Targets ist das Potential von <b>Koning–Delaroche</b> (KD03) die Voreinstellung: Woods–Saxon-Formen, deren Tiefen sich glatt mit der Energie sowie mit Masse und Neutronenüberschuss des Targets ändern, aus einer globalen Formel oder, für die Kerne, die KD03 einzeln angepasst hat, etwa Eisen-56, aus einer lokalen Anpassung derselben Form. Das Bild verwendet die globale Formel für Neutronen an Eisen-56. Der reelle Topf (blau) bindet; die imaginären Anteile (rot) absorbieren, im Volumen und, bei niedriger Energie vor allem, in einer dünnen Schale an der Oberfläche.</p>
  <div class="ctl"><label for="op-e">Neutronenenergie (MeV)</label><input id="op-e" type="range" data-bind="E" min="0.1" max="80" step="0.1" value="5"><output data-show="E" data-fmt="1"></output></div>
  <div class="formula">U(r) = −V<sub>V</sub> f(r) − iW<sub>V</sub> f(r) + 4i a<sub>D</sub>W<sub>D</sub> df<sub>D</sub>/dr + 2(V<sub>so</sub> + iW<sub>so</sub>) (1/r) df<sub>so</sub>/dr ⟨l·σ⟩</div>
  <p>Die Probeneutronen laufen bei der eingestellten Energie hindurch und verblassen dort, wo die Absorption greift: Ihre mittlere freie Weglänge ist ħ<i>v</i>/2|<i>W</i>|. Jede Tiefe ist eine Funktion von <i>E</i> − <i>E</i><sub>F</sub>, gemessen ab der Fermi-Energie: Die reelle Tiefe fällt langsam, die Oberflächenabsorption <i>W</i><sub>D</sub> hat ihr Maximum nahe 10 MeV, und die Volumenabsorption <i>W</i><sub>V</sub> wächst stetig, bis sie überwiegt, hier oberhalb von etwa 45 MeV.</p>
</div>
<div class="step">
  <h3>Die Radialgleichung integrieren</h3>
  <p>Jede Partialwelle gehorcht ihrer eigenen Radialgleichung. Die Engine integriert sie von <i>r</i> = 0 nach außen mit dem <b>Numerov-Verfahren</b>, einer Dreipunktformel, die bis zur sechsten Potenz der Schrittweite genau ist, durch das volle komplexe Potential.</p>
  <div class="formula">u″<sub>lj</sub>(r) = [ l(l+1)/r² + (2μ/ħ²) U<sub>lj</sub>(r) − k² ] u<sub>lj</sub>(r)</div>
  <div class="ctl"><label for="op-l">Partialwelle l</label><input id="op-l" type="range" data-bind="L" min="0" max="10" step="1" value="1" data-instant><output data-show="L" data-fmt="0"></output></div>
  <div class="ctl"><label for="op-e2">Neutronenenergie (MeV)</label><input id="op-e2" type="range" data-bind="E" min="0.1" max="80" step="0.1" value="5"><output data-show="E" data-fmt="1"></output></div>
  <p>Die durchgezogene Linie ist die Welle in der Zeit, Re[<i>u</i> e<sup>−iωt</sup>]; die gestrichelte ist die freie Welle, als wäre der Kern nicht da. Im Topf ist die Welle kürzer (das Neutron ist schneller) und kleiner (absorbiert); außerhalb kommt sie phasenverschoben zurück.</p>
</div>
<div class="step">
  <h3>Von der Welle zu S und T</h3>
  <p>Jenseits von etwa 12 fm ist das Potential verschwunden, und die Welle muss eine Mischung aus einer einlaufenden und einer auslaufenden freien Welle sein, <i>u</i> ∝ <i>H</i><sup>−</sup> − <i>S</i> <i>H</i><sup>+</sup>. Der Anschluss des integrierten <i>u</i> an zwei Radien legt das <b>S-Matrix-Element</b> <i>S<sub>lj</sub></i> fest: die auslaufende Amplitude samt ihrer Phase.</p>
  <div class="btns"><button class="btn ghost" data-act="abs" aria-pressed="false">Absorption ausschalten</button></div>
  <div class="formula">S<sub>lj</sub> = η<sub>lj</sub> e<sup>2iδ<sub>lj</sub></sup> ,  T<sub>lj</sub> = 1 − |S<sub>lj</sub>|²</div>
  <p>Der Punkt ist <i>S</i> in der komplexen Ebene, innerhalb des Einheitskreises; seine Spur ist der Weg, während die Energie von 0,1 bis 40 MeV durchläuft. Ohne Absorption gilt |<i>S</i>| = 1: Der Punkt läuft auf dem Kreis, die Welle ändert nur ihre Phase, und <i>T</i> = 0. Der Abstand nach innen vom Kreis ist das, was der Compoundkern und jede andere Reaktion erhalten.</p>
</div>
<div class="step">
  <h3>Der Spin–Bahn-Term spaltet j auf</h3>
  <p>Der <b>Spin–Bahn-Term</b> ist anziehend für <i>j</i> = <i>l</i> + ½ und abstoßend für <i>j</i> = <i>l</i> − ½. Er ist klein, einige MeV an der Oberfläche, schiebt aber die beiden Transmissionen jedes <i>l</i> auseinander, am stärksten nahe der Partialwelle, die die Oberfläche streift.</p>
  <div class="ctl"><label for="op-e3">Neutronenenergie (MeV)</label><input id="op-e3" type="range" data-bind="E" min="0.1" max="80" step="0.1" value="5"><output data-show="E" data-fmt="1"></output></div>
  <div class="btns"><button class="btn ghost" data-act="so" aria-pressed="false">Spin–Bahn ausschalten</button></div>
  <p>Hauser–Feshbach (Kapitel 22) verwendet beide getrennt; mit ihren Gewichten summiert, (<i>l</i>+1)<i>T</i><sub>l,l+½</sub> + <i>l</i> <i>T</i><sub>l,l−½</sub>, ergeben sie den Reaktionsquerschnitt nahezu unverändert. Deshalb schränken totale Wirkungsquerschnitte die Stärke des Spin–Bahn-Terms kaum ein, und man braucht Polarisationsdaten.</p>
</div>
<div class="step">
  <h3>Die Wirkungsquerschnitte</h3>
  <p>Die Summe über die Partialwellen liefert die Observablen, an die das Potential angepasst wird. Der Reaktionsquerschnitt zählt den entfernten Fluss, der totale Wirkungsquerschnitt folgt aus der Vorwärtsamplitude, und ihre Differenz ist die formelastische Streuung (Shape-Elastic).</p>
  <div class="formula">σ<sub>R</sub> = (π/k²) Σ<sub>l</sub> [(l+1)T<sub>l,l+½</sub> + l T<sub>l,l−½</sub>] ,  σ<sub>tot</sub> = (2π/k²) Σ<sub>lj</sub> (j+½)(1 − Re S<sub>lj</sub>)</div>
  <div class="ctl"><label for="op-e4">Neutronenenergie (MeV)</label><input id="op-e4" type="range" data-bind="E" min="0.2" max="50" step="0.1" value="5"><output data-show="E" data-fmt="1"></output></div>
  <p>KD03 wurde an solche Daten für viele Kerne, von 1 keV bis 200 MeV, angepasst; der totale Wirkungsquerschnitt von Eisen, zwischen 3,5 und 4 b bei einigen MeV und 2,5 b bei 14 MeV, ergibt sich ohne Anpassung an diesen Kern auf etwa 5 Prozent genau, breite Maxima eingeschlossen: Sie sind die Kerngröße, gesehen im Verhältnis zur Wellenlänge des Neutrons.</p>
</div>
<div class="step">
  <h3>Das Niederenergie-Ende</h3>
  <p>Unterhalb einiger keV zählt nur die s-Welle, und <i>T</i><sub>0</sub> wächst wie √<i>E</i>: eine Steigung von einhalb in dieser doppelt-logarithmischen Darstellung. Die Konstante ist die <b>Stärkefunktion</b> <i>S</i><sub>0</sub> = <i>T</i><sub>0</sub>/(2π√<i>E</i>), mit <i>E</i> in eV, dieselbe Größe, die Resonanzanalysen als Σ Γ<sub>n</sub><sup>0</sup>/Δ<i>E</i> messen.</p>
  <p>Ein globales Potential wird vor allem bei MeV-Energien angepasst, und sein Niederenergie-Ende ist seine schwächste Stelle. Für Eisen-56 liefert dieses hier <i>S</i><sub>0</sub> ≈ 5,5 × 10⁻⁴, und die lokale KD03-Anpassung fast dasselbe, während der gemessene Wert (RIPL) 2,3 ± 0,6 × 10⁻⁴ beträgt: Eisen liegt nahe dem Maximum der 3s-Größenresonanz um <i>A</i> ≈ 55, wo <i>S</i><sub>0</sub> am empfindlichsten auf das Potential reagiert. Deshalb sind die gemessenen <i>S</i><sub>0</sub> und <i>S</i><sub>1</sub> eine eigene, optionale Eingabe der Engine.</p>
  <div class="aside">Im Code: <code>omp/parameters.py</code> (KD03 und die anderen globalen Potentiale), <code>omp/potential.py</code> (die radialen Formfaktoren), <code>omp/schrodinger.py</code> (Numerov-Integration und Anschluss, mit Coulomb-Funktionen nach dem Verfahren von Steed für geladene Teilchen; ersetzt ECIS für sphärische Targets und ist gegen die T<sub>lj</sub> von ECIS geprüft), <code>ecis/</code> (die Portierung der gekoppelten Kanäle für deformierte Targets), <code>omp/sfunc.py</code> (optional: gemessene S₀, S₁). Das Bild löst die Gleichung selbst, nichtrelativistisch, für Neutronen an Eisen-56.</div>
</div>`,
};
(function () {
  const L = {
    // axes and units
    "{#} fm": "{#} fm", "{#} MeV": "{#} MeV", "{#} keV": "{#} keV", "{#} eV": "{#} eV", "{#} b": "{#} b",
    // scene 1: potential
    "real well, depth {#} MeV": "reeller Topf, Tiefe {#} MeV",
    "surface absorption, peak {#} MeV": "Oberflächenabsorption, Maximum {#} MeV",
    "volume absorption {#} MeV": "Volumenabsorption {#} MeV",
    "spin–orbit for l = {#}, j = {#}/{#}: {#} MeV": "Spin–Bahn für l = {#}, j = {#}/{#}: {#} MeV",
    "E = {#} MeV": "E = {#} MeV",
    "mean free path: {#} fm at the surface, {#} fm in the centre": "mittlere freie Weglänge: {#} fm an der Oberfläche, {#} fm im Zentrum",
    "mean free path: {#} fm at the surface, > {#} fm in the centre": "mittlere freie Weglänge: {#} fm an der Oberfläche, > {#} fm im Zentrum",
    "mean free path: > {#} fm at the surface, {#} fm in the centre": "mittlere freie Weglänge: > {#} fm an der Oberfläche, {#} fm im Zentrum",
    "mean free path: > {#} fm at the surface, > {#} fm in the centre": "mittlere freie Weglänge: > {#} fm an der Oberfläche, > {#} fm im Zentrum",
    "real": "reell", "volume": "Volumen", "surface": "Oberfläche",
    "depths (MeV) against energy (MeV)": "Tiefen (MeV) gegen Energie (MeV)",
    // scene 2: wave
    "potential: real (blue), imaginary (red)": "Potential: reell (blau), imaginär (rot)",
    "nuclear surface": "Kernoberfläche",
    "l = {#}, j = {#}+½ · E = {#} MeV · |S| = {#} · δ = {#}° · T = {#}": "l = {#}, j = {#}+½ · E = {#} MeV · |S| = {#} · δ = {#}° · T = {#}",
    "solid: the wave now · shaded: its size |u| · dashed: free wave": "durchgezogen: die Welle jetzt · schattiert: ihre Größe |u| · gestrichelt: freie Welle",
    // scene 3: S-matrix
    "Re S": "Re S", "Im S": "Im S",
    "|S| = {#}: nothing absorbed": "|S| = {#}: nichts absorbiert",
    "l = {#}, j = {#}+½ · E = {#} MeV": "l = {#}, j = {#}+½ · E = {#} MeV",
    "|S| = {#} · T = {#} − |S|² = {#}": "|S| = {#} · T = {#} − |S|² = {#}",
    "l = {#}, j = {#}+½": "l = {#}, j = {#}+½",
    "|S| = {#}": "|S| = {#}",
    "T = {#} − |S|² = {#}": "T = {#} − |S|² = {#}",
    "trail: S as E runs {#} → {#} MeV": "Spur: S, während E von {#} → {#} MeV läuft",
    "no absorption: S stays on the circle": "keine Absorption: S bleibt auf dem Kreis",
    // scene 4: spin-orbit
    "T = {#}": "T = {#}", "l": "l",
    "hollow: j = l − ½ · solid: j = l + ½": "hohl: j = l − ½ · voll: j = l + ½",
    "hollow (purple): j = l − ½ · solid (blue): j = l + ½": "hohl (violett): j = l − ½ · voll (blau): j = l + ½",
    "reaction cross section {#} b (without spin–orbit {#} b)": "Reaktionsquerschnitt {#} b (ohne Spin–Bahn {#} b)",
    "reaction cross section {#} b (spin–orbit off)": "Reaktionsquerschnitt {#} b (Spin–Bahn aus)",
    "grazing l ≈ kR = {#}": "streifend l ≈ kR = {#}",
    // scene 5: cross sections
    "total {#} b": "total {#} b",
    "reaction {#} b": "Reaktion {#} b",
    "shape elastic {#} b": "formelastisch {#} b",
    "n + ⁵⁶Fe, KD{#}, computed here": "n + ⁵⁶Fe, KD{#}, hier berechnet",
    // scene 6: S0
    "T₀ (s-wave)": "T₀ (s-Welle)",
    "T₁ (p-wave, j = {#}/{#}): slope {#}/{#}": "T₁ (p-Welle, j = {#}/{#}): Steigung {#}/{#}",
    "dashed: {#}πS₀√E, slope ½": "gestrichelt: {#}πS₀√E, Steigung ½",
    "S₀ = {#} × {#}⁻⁴ from this potential": "S₀ = {#} × {#}⁻⁴ aus diesem Potential",
  };
  Object.assign(WT.L.labels, L);
})();
Object.assign(WT.L.glossary, {
  koningDelaroche: {
    term: "Koning–Delaroche-Potential", aliases: ["Koning–Delaroche-Potential", "Koning–Delaroche", "KD03"],
    short: "Das globale optische Potential für Neutronen und Protonen von A. J. Koning und J.-P. Delaroche (2003), von 1 keV bis 200 MeV und für Massen von 24 bis 209.",
    more: "Seine Tiefen, Radien und Diffusitäten sind glatte Funktionen von Energie, Masse und Neutronenüberschuss, einmal an einen großen Bestand gemessener Wirkungsquerschnitte und Winkelverteilungen angepasst. Es ist die Voreinstellung für Nukleonen in TALYS und in der Engine.",
    chapter: "optical",
  },
  numerov: {
    term: "Numerov-Verfahren", aliases: ["Numerov-Verfahren", "Numerov-Verfahrens", "Numerov-Integration", "Numerov"],
    short: "Eine Dreipunktformel zur Integration von Differentialgleichungen zweiter Ordnung ohne Term mit der ersten Ableitung, etwa der radialen Schrödinger-Gleichung, mit einem Fehler der Ordnung h⁶ pro Schritt.",
    formula: "(1 − h²Q_n+1/12) u_n+1 = 2(1 + 5h²Q_n/12) u_n − (1 − h²Q_n−1/12) u_n−1",
    chapter: "optical",
  },
  sMatrix: {
    term: "S-Matrix", aliases: ["S-Matrix-Element", "S-Matrix-Elements", "S-Matrix"],
    short: "Die Amplituden, die einlaufende und auslaufende Wellen verbinden; für elastische Streuung in einer Partialwelle eine einzige komplexe Zahl S = η e^(2iδ).",
    more: "|S| = 1 bedeutet, dass nichts absorbiert wird und sich nur die Phase δ ändert; der Fehlbetrag 1 − |S|² ist der Transmissionskoeffizient, der in Reaktionen abgezweigte Fluss.",
    chapter: "optical",
  },
  spinOrbit: {
    term: "Spin–Bahn-Term", aliases: ["Spin–Bahn-Term", "Spin–Bahn-Terms", "Spin–Bahn", "Spin-Bahn"],
    short: "Der Teil des Kernpotentials, der davon abhängt, ob der Spin des Nukleons parallel oder antiparallel zu seinem Bahndrehimpuls steht.",
    more: "Er ist anziehend für j = l + ½ und abstoßend für j = l − ½ und hat sein Maximum an der Kernoberfläche. Dieselbe Wechselwirkung erzeugt die magischen Zahlen des Schalenmodells.",
    chapter: "optical",
  },
});
