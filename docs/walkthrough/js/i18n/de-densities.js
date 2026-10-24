/* German (Deutsch): densities (Kapitel 15, Niveaudichten, angeschlossen) */
WT.L.ch.densities = {
  num: "Kapitel 15", title: "Niveaudichten, angeschlossen", short: "Niveaudichten",
  lead: "Kapitel 5 hat eine gerade Planke an einen Hang angesetzt. Dieses Kapitel schreibt beide hin, zeigt, wie die Anschlussstelle aus den gezählten Niveaus bestimmt wird, und was geschieht, wenn es keine gibt.",
  html: `
<div class="step">
  <h3>Das Fermi-Gas mit gedämpften Schaleneffekten</h3>
  <p>Die Standard-Niveaudichte der Engine, ldmodel 1, ist die zusammengesetzte Dichte nach <b>Gilbert–Cameron</b>: oben ein Fermi-Gas, darunter eine konstante Temperatur. Das Fermi-Gas braucht eine einzige Zahl, den Niveaudichteparameter <i>a</i>, und bei niedriger Energie spürt diese Zahl die Schalen. In der Form nach <b>Ignatyuk</b> wirkt die Schalenkorrektur δW bei niedriger Anregung voll und klingt mit einer Dämpfungsrate γ ab, sodass <i>a</i>(<i>U</i>) gegen den glatten Wert <i>ã</i> strebt, sobald der Kern heiß ist.</p>
  <div class="formula">a(U) = ã [1 + δW (1 − e<sup>−γU</sup>) / U] ,  ã = αA + βA<sup>2/3</sup> ,  γ = γ₁ / A<sup>1/3</sup></div>
  <div class="ctl"><label for="ld-dw">Schalenkorrektur δW (MeV)</label><input id="ld-dw" type="range" data-bind="dW" min="-6" max="4" step="0.1" value="1"><output data-show="dW" data-fmt="1"></output></div>
  <div class="formula">ρ<sub>F</sub>(E) = exp(2√(aU)) / (12√2 σ a<sup>1/4</sup> U<sup>5/4</sup>) ,  U = E − Δ ,  σ² = 0.01389 A<sup>5/3</sup> √(aU) / ã</div>
  <p>Die oberen Kurven zeigen <i>a</i>(<i>U</i>)/<i>ã</i> für mehrere δW; deine ist fett gezeichnet. Darunter steht ln ρ<sub>F</sub>. Ein negatives δW (eine abgeschlossene Schale) drückt die Dichte um ein bis zwei Größenordnungen herab, und die Unterdrückung klingt nur langsam ab: <i>a</i>(<i>U</i>) kehrt wie δW/<i>U</i> zu <i>ã</i> zurück, sodass selbst bei 20 MeV ein δW von −6 MeV noch einen Faktor von etwa 40 kostet. Δ ist die Paarungsverschiebung, 12/√A für jede gepaarte Nukleonensorte.</p>
</div>
<div class="step">
  <h3>Eine Tangente darunter</h3>
  <p>Unterhalb der Anschlussenergie <i>E<sub>x</sub></i> wird das Fermi-Gas durch das Gesetz der <b>konstanten Temperatur</b> ersetzt. Zwei Bedingungen legen seine zwei Parameter fest: gleicher Wert und gleiche Steigung bei <i>E<sub>x</sub></i>; die Gerade ist dort also die Tangente an ln ρ<sub>F</sub>.</p>
  <div class="formula">ρ<sub>T</sub>(E) = (1/T) e<sup>(E − E₀)/T</sup> ,  1/T = d ln ρ<sub>F</sub>/dE |<sub>E<sub>x</sub></sub> ,  E₀ = E<sub>x</sub> − T ln[T ρ<sub>F</sub>(E<sub>x</sub>)]</div>
  <div class="ctl"><label for="ld-ex">Anschlussenergie Eₓ (MeV)</label><input id="ld-ex" type="range" data-bind="Ex" min="4.6" max="14" step="0.05" value="7"><output data-show="Ex" data-fmt="2"></output></div>
  <p>Verschiebe <i>E<sub>x</sub></i>, und die Tangente schwenkt: Eine höher liegende Anschlussstelle ergibt ein höheres <i>T</i> (eine flachere Gerade) und ein tieferes <i>E</i>₀. Jedes <i>E<sub>x</sub></i> liefert eine glatte Kurve. Welche die richtige ist, entscheiden die gezählten Niveaus.</p>
</div>
<div class="step">
  <h3>Die Anschlussstelle aus den gezählten Niveaus</h3>
  <p>Die Treppe ist die Zahl der bekannten Niveaus unterhalb von <i>E</i>, auf logarithmischer Skala. Integriert ergibt das Gesetz der konstanten Temperatur eine Gerade, <i>N</i>(<i>E</i>) = e<sup>(E − E₀)/T</sup> + const, und diese muss die Zahl der Niveaus zwischen Niveau <i>N<sub>L</sub></i> und Niveau <i>N<sub>P</sub></i> wiedergeben, dem Abschnitt des Niveauschemas, der als vollständig gilt. Das ist eine Gleichung für die eine Unbekannte <i>E<sub>x</sub></i>.</p>
  <div class="formula">F(E<sub>x</sub>) = e<sup>(E<sub>P</sub>−E₀)/T</sup> − e<sup>(E<sub>L</sub>−E₀)/T</sup> − (N<sub>P</sub> − N<sub>L</sub>) = 0</div>
  <div class="ctl"><label for="ld-ex2">Versuchswert Eₓ (MeV)</label><input id="ld-ex2" type="range" data-bind="Ex" min="4.6" max="14" step="0.05" value="7"><output data-show="Ex" data-fmt="2"></output></div>
  <p>Das untere Feld zeigt <i>F</i>. Wie TALYS tastet die Engine ein Intervall in 100 Schritten nach einem Vorzeichenwechsel ab und halbiert es dann fortlaufend (Bisektion); die schrumpfende Klammer zeigt das. Wo <i>F</i> = 0 ist, liegt die Versuchsgerade auf der Treppe.</p>
</div>
<div class="step">
  <h3>Wenn es keine Anschlussstelle gibt</h3>
  <p>Bei einem doppelt magischen Kern ist das Fermi-Gas bei niedriger Energie so stark unterdrückt, dass seine Temperatur überall niedrig bleibt und <i>F</i> nie das Vorzeichen wechselt: Es gibt keine Anschlussenergie. TALYS nimmt dann die empirische Temperatur <i>T</i> = −0,25 + 10,2/√(<i>A</i>(1 + γδW)) und sucht die Energie, bei der das Fermi-Gas diese Temperatur hat. Nahe einem doppelt magischen Kern erreicht das Fermi-Gas diese Temperatur erst weit oberhalb jeder sinnvollen Anschlussstelle oder nie, also greift auch die Anschlussstelle auf Systematiken zurück, <i>E<sub>x</sub></i> = 2,33 + 253/<i>A</i> + Δ, und <i>E</i>₀ wird so festgelegt, dass der Wert stetig ist.</p>
  <div class="btns"><button class="btn ghost" data-act="tang" aria-pressed="false">Tangente bei der Ersatzenergie</button></div>
  <p>Der Wert ist stetig, doch das empirische <i>T</i> ist nicht die Fermi-Gas-Temperatur bei dieser Energie, also springt die Steigung. Mit der Standardeingabe tritt das bei ²⁰⁵,²⁰⁶Tl, ²⁰⁶⁻²⁰⁹Pb und ²¹⁰Bi auf, mit Steigungssprüngen von 34 bis 62 %. Nimmt man <i>T</i> dort aus dem Fermi-Gas, wie es TALYS bereits tut, wenn <i>E<sub>x</sub></i> in der Eingabe vorgegeben ist, so ist die Tangente wiederhergestellt, und der Einfang in der Bleiregion ändert sich um bis zu 20 bis 30 %. INCOGNITA reproduziert hier TALYS; die Änderung wurde den TALYS-Entwicklern gemeldet. Das Bild ist eine bleiähnliche Illustration, bei der <i>ã</i> um 30 % erhöht ist, sodass ihr Fermi-Gas bis etwa 24 MeV, jenseits des Suchbereichs, unterhalb der empirischen Temperatur bleibt; ihre Steigung springt um 62 %.</p>
</div>
<div class="step">
  <h3>Der Abstand D₀ als Prüfstein</h3>
  <p>Bei der Neutronenseparationsenergie wird die Dichte direkt gemessen: Der mittlere Abstand <i>D</i>₀ der s-Wellen-Resonanzen zählt die Zustände mit dem einen Spin und der einen Parität, die ein langsames Neutron erreichen kann. Für ein Target mit Spin 0 ist das allein <i>J</i><sup>π</sup> = ½⁺.</p>
  <div class="formula">1/D₀ = ρ(S<sub>n</sub>, ½, +) = ½ ρ<sub>F</sub>(S<sub>n</sub>) · (2J+1)/(2σ²) · e<sup>−(J+½)²/2σ²</sup></div>
  <div class="ctl"><label for="ld-as">Skalierung von ã</label><input id="ld-as" type="range" data-bind="as" min="0.8" max="1.2" step="0.005" value="1"><output data-show="as" data-fmt="3"></output></div>
  <p>Das Bild gilt für einen eisen-57-ähnlichen Compoundkern mit dem globalen <i>ã</i>, verglichen mit dem gemessenen Wert 25,4 ± 2,2 keV. Wenige Prozent an <i>ã</i> verschieben <i>D</i>₀ um Dutzende Prozent: Wo <i>D</i>₀ gemessen ist, ist die Dichte bei <i>S<sub>n</sub></i> gut festgelegt, und wo nicht, ist sie die größte einzelne Unsicherheit im Einfang. Evaluationen passen <i>a</i> an <i>D</i>₀ an, und ebenso die Voreinstellung von TALYS, der die Engine folgt: Für einen Kern mit gemessenem <i>D</i>₀ liest sie einen daran angepassten Niveaudichteparameter ein und verwendet die globale Formel nur für die übrigen.</p>
  <div class="aside">Im Code: <code>density/parameters.py</code> (ã, Ignatyuk-Dämpfung, Paarung, Spin-Cutoff), <code>density/models.py</code> (Fermi-Gas, konstante Temperatur, Tabellen), <code>density/matching.py</code> (die Nullstelle für den Anschluss, der empirische Ersatz, die Eigenheiten der einfachen Genauigkeit von TALYS nachgebildet). Das Bild verwendet die globalen TALYS-Parameter für ldmodel 1 mit illustrativen Niveauschemata und Schalenkorrekturen (und, für den bleiähnlichen Fall, <i>ã</i> × 1,3); das gemessene <i>D</i>₀ ist der RIPL-Wert für ⁵⁷Fe.</div>
</div>`,
};
Object.assign(WT.L.labels, {
  // axes
  "E (MeV)": "E (MeV)", "Eₓ (MeV)": "Eₓ (MeV)", "U (MeV)": "U (MeV)", "a(U) / ã": "a(U) / ã",
  "F = {#}": "F = {#}", "T = {#} MeV": "T = {#} MeV", "E₀ = {#} MeV": "E₀ = {#} MeV", "× e": "× e",
  // scene 1
  "U = {#} MeV · a = {#} MeV⁻¹ · T ≈ √(U/a) = {#} MeV": "U = {#} MeV · a = {#} MeV⁻¹ · T ≈ √(U/a) = {#} MeV",
  "ρ_F (states per MeV), A = {#}": "ρ_F (Zustände pro MeV), A = {#}",
  "dashed: δW = {#}": "gestrichelt: δW = {#}",
  "at {#} MeV: ×{#} against δW = {#}": "bei {#} MeV: ×{#} gegenüber δW = {#}",
  "at {#} MeV: ×{#}e{#} against δW = {#}": "bei {#} MeV: ×{#}e{#} gegenüber δW = {#}",
  // scene 2
  "joint Eₓ = {#} MeV": "Anschluss Eₓ = {#} MeV",
  "Fermi gas": "Fermi-Gas",
  "constant temperature": "konstante Temperatur",
  "ln ρ (states per MeV), A = {#}": "ln ρ (Zustände pro MeV), A = {#}",
  // scene 3
  "levels {#} to {#}: taken as complete": "Niveaus {#} bis {#}: als vollständig angenommen",
  "levels {#}–{#}": "Niveaus {#}–{#}",
  "number of levels below E": "Zahl der Niveaus unterhalb von E",
  "trial Eₓ = {#} MeV: the line gives {#} levels for {#} counted": "Versuch Eₓ = {#} MeV: die Gerade ergibt {#} Niveaus bei {#} gezählten",
  "F(Eₓ): predicted minus counted (signed log scale)": "F(Eₓ): vorhergesagt minus gezählt (vorzeichenbehaftete log. Skala)",
  "bisection step {#}: [{#}, {#}]": "Bisektionsschritt {#}: [{#}; {#}]",
  "root Eₓ = {#} MeV": "Nullstelle Eₓ = {#} MeV",
  // scene 4
  "below: {#}/T with T = {#} MeV (Fermi-gas T)": "unten: {#}/T mit T = {#} MeV (Fermi-Gas-T)",
  "below: {#}/T with T = {#} MeV (empirical T)": "unten: {#}/T mit T = {#} MeV (empirisches T)",
  "above: Fermi gas, T = {#} MeV": "oben: Fermi-Gas, T = {#} MeV",
  "slope jumps by {#} % at Eₓ = {#} MeV": "Steigung springt um {#} % bei Eₓ = {#} MeV",
  "tangent at Eₓ = {#} MeV: no jump": "Tangente bei Eₓ = {#} MeV: kein Sprung",
  "ln ρ, lead-like nucleus (A = {#}, δW = {#} MeV)": "ln ρ, bleiähnlicher Kern (A = {#}, δW = {#} MeV)",
  "F changes sign: a root exists": "F wechselt das Vorzeichen: es gibt eine Nullstelle",
  "F(Eₓ) never reaches zero: no matching energy": "F(Eₓ) erreicht nie null: keine Anschlussenergie",
  // scene 5
  "{#} keV": "{#} keV",
  "measured {#} ± {#} keV": "gemessen {#} ± {#} keV",
  "computed D₀ = {#} keV": "berechnet D₀ = {#} keV",
  "ã × {#} = {#} MeV⁻¹ · σ² = {#} · ρ(Sₙ) = {#} per MeV": "ã × {#} = {#} MeV⁻¹ · σ² = {#} · ρ(Sₙ) = {#} pro MeV",
  "ã × {#} = {#} MeV⁻¹ · σ² = {#} · ρ(Sₙ) = {#}e{#} per MeV": "ã × {#} = {#} MeV⁻¹ · σ² = {#} · ρ(Sₙ) = {#}e{#} pro MeV",
  "s-wave resonances above Sₙ, {#} keV shown: about {#} levels": "s-Wellen-Resonanzen oberhalb von Sₙ, {#} keV gezeigt: etwa {#} Niveaus",
  "iron{#}-like compound nucleus, Sₙ = {#} MeV, spin and parity ½⁺": "eisen{#}-ähnlicher Compoundkern, Sₙ = {#} MeV, Spin und Parität ½⁺",
});
Object.assign(WT.L.glossary, {
  gilbertCameron: {
    term: "Gilbert–Cameron", aliases: ["Gilbert–Cameron"],
    short: "Eine zusammengesetzte Niveaudichte: ein Gesetz konstanter Temperatur bei niedriger Energie, oberhalb einer Anschlussenergie an das Fermi-Gas angeschlossen, mit gleichem Wert und gleicher Steigung an der Anschlussstelle.",
    more: "Vorgeschlagen 1965 von A. Gilbert und A. G. W. Cameron. Es ist das Standardmodell von TALYS und der Engine (ldmodel 1), mit dem energieabhängigen Niveaudichteparameter nach Ignatyuk.",
    chapter: "densities",
  },
  ignatyuk: {
    term: "Ignatyuk", aliases: ["Ignatyuk"],
    short: "Ignatyuks Form des Niveaudichteparameters: Die Schalenkorrektur wirkt bei niedriger Anregung voll und klingt mit der Energie ab, sodass a(U) gegen seinen glatten Wert strebt.",
    formula: "a(U) = ã [1 + δW (1 − e^(−γU)) / U]",
    chapter: "densities",
  },
});
