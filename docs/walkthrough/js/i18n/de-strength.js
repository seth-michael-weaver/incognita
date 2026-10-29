/* German (Deutsch): strength (Kapitel 25, Photonenstärke im Detail) */
WT.L.ch.strength = {
  num: "Kapitel 25", title: "Photonenstärke im Detail", short: "Photonenstärke",
  lead: "Kapitel 10 hat gezeigt, welche Photonen ein heißer Kern bevorzugt. Dieses Kapitel schreibt die Stärkefunktionen hin, verfolgt sie bis zu den Transmissionskoeffizienten und der mittleren Strahlungsbreite und lässt die Kaskade ablaufen, die sie antreiben.",
  html: `
<div class="step">
  <h3>E1: der Ausläufer der Dipol-Riesenresonanz</h3>
  <p>Die <b>Photonenstärkefunktion</b> <i>f<sub>XL</sub></i>(<i>E</i><sub>γ</sub>) ist die mittlere reduzierte Wahrscheinlichkeit für ein Photon vom Typ <i>XL</i>: elektrischer Dipol E1, magnetischer Dipol M1 und so weiter. Bei E1 wird sie von der Dipol-Riesenresonanz nahe 18 MeV beherrscht, doch der Zerfall bei <i>S<sub>n</sub></i> nutzt Photonen von 1 bis 7 MeV, weit unten in ihrem Ausläufer, und die Form dieses Ausläufers ist die eigentliche Frage.</p>
  <div class="formula">f<sub>E1</sub> = K σ₀Γ₀ · E<sub>γ</sub> Γ(E<sub>γ</sub>,T) / [(E<sub>γ</sub>² − E₀²)² + E<sub>γ</sub>² Γ(E<sub>γ</sub>,T)²] / (1 − e<sup>−E<sub>γ</sub>/T</sup>) ,  Γ(E<sub>γ</sub>,T) = (Γ₀/E₀)(E<sub>γ</sub> + 4π²T²/E₀)</div>
  <div class="ctl"><label for="ps-t">Temperatur der Endzustände T (MeV)</label><input id="ps-t" type="range" data-bind="T" min="0" max="1.5" step="0.01" value="0.7"><output data-show="T" data-fmt="2"></output></div>
  <p>Die gestrichelte Linie ist die Standard-Lorentz-Kurve (SLO), die an die Photoabsorption angepasste Form. Mit ihrer konstanten Breite überschätzt sie die Stärke im Zerfallsfenster um einen Faktor 2 bis 5, ein seit Langem bekanntes Versagen bei sphärischen Kernen. Die durchgezogene Linie ist die vereinfachte modifizierte Lorentz-Kurve (<b>SMLO</b>): Ihre Breite wächst mit der Photonenenergie und mit der Temperatur der Endzustände. Das senkt den Ausläufer im Fenster, lässt aber bei verschwindender Photonenenergie eine endliche Stärke übrig, wie es Zerfallsdaten verlangen. Der Zoomkasten zeigt diesen Sockel unterhalb von 2 MeV: Zieh <i>T</i> auf 0, und er verschwindet.</p>
</div>
<div class="step">
  <h3>M1: Spin-Flip, Schere, Upbend</h3>
  <p>Die M1-Stärke ist schwächer, aber nicht vernachlässigbar: eine Spin-Flip-Resonanz nahe 41<i>A</i><sup>−1/3</sup> MeV, eine Scherenmode nahe 3 MeV in deformierten Kernen (mit einer Stärke, die wie β² wächst) und ein Upbend, ein Anstieg zu verschwindender Photonenenergie hin, der in Daten nach der Oslo-Methode und in Schalenmodellrechnungen auftritt.</p>
  <div class="ctl"><label for="ps-b">Deformation β (Schere)</label><input id="ps-b" type="range" data-bind="beta" min="0" max="0.35" step="0.01" value="0.2"><output data-show="beta" data-fmt="2"></output></div>
  <div class="btns"><button class="btn ghost" data-act="up" aria-pressed="true">Upbend</button></div>
  <p>Die blasse Linie dahinter ist E1. Bei den niedrigsten Photonenenergien, hier unterhalb von etwa 2 MeV, lässt der Upbend M1 mit ihr gleichziehen oder sie übertreffen (die Markierung zeigt, wo); deshalb zählt er für das weiche Ende der Kaskade und für den Einfang fern der Stabilität. Das voreingestellte M1 der Engine ist die IAEA-Empfehlung mit Upbend, pro Kern tabelliert, und ihr voreingestelltes E1 ist das tabellierte SMLO-2019; die geschlossenen Formeln hier stehen stellvertretend für diese Tabellen.</p>
</div>
<div class="step">
  <h3>Brink–Axel</h3>
  <p>Die <b>Brink–Axel-Hypothese</b> besagt, dass die Stärke von der Photonenenergie abhängt und nicht davon, wo der Kern startet: Dasselbe <i>f</i> gilt für eine Resonanz bei <i>S<sub>n</sub></i> und für einen Zustand bei 4 MeV. (SMLO behält über <i>T</i> eine schwache Abhängigkeit.) Jede Startenergie emittiert dann mit dem Transmissionskoeffizienten mal der Dichte der Endzustände.</p>
  <div class="formula">T<sub>XL</sub>(E<sub>γ</sub>) = 2π E<sub>γ</sub><sup>2L+1</sup> f<sub>XL</sub>(E<sub>γ</sub>) ,  dΓ/dE<sub>γ</sub> ∝ T<sub>XL</sub>(E<sub>γ</sub>) ρ(E<sub>x</sub> − E<sub>γ</sub>)</div>
  <div class="ctl"><label for="ps-x">Startenergie Eₓ (MeV)</label><input id="ps-x" type="range" data-bind="Ex" min="2" max="7.6" step="0.05" value="7.6"><output data-show="Ex" data-fmt="2"></output></div>
  <p>Das Produkt aus einem steigenden <i>E</i><sub>γ</sub>³<i>f</i> und einem fallenden ρ ergibt einen Buckel. Von <i>S<sub>n</sub></i> aus liegt sein Maximum hier bei etwa 4 bis 5 MeV. Bei tieferen Starts wird er an der Startenergie abgeschnitten; unterhalb der Anschlussenergie, wo ρ eine Exponentialfunktion konstanter Temperatur ist, hat er von jedem Start aus dieselbe Form, nur abgeschnitten. Geprüft wird die Hypothese, indem man bei verschiedenen Anregungsenergien extrahierte Stärken vergleicht, genau das tun Analysen vom Oslo-Typ.</p>
</div>
<div class="step">
  <h3>Die mittlere Strahlungsbreite</h3>
  <p>Die Summe über alle Endzustände, die von den s-Wellen-Resonanzen (<i>J</i><sup>π</sup> = ½⁺ an einem Target mit Spin 0) durch E1 oder M1 erreichbar sind, ergibt ihre mittlere totale Photonenbreite. Sie ist für einige hundert Kerne aus Resonanzformen gemessen und die wichtigste Kontrolle der Stärke bei <i>S<sub>n</sub></i>.</p>
  <div class="formula">⟨Γ<sub>γ</sub>⟩ = D₀/2π · Σ<sub>XL</sub> Σ<sub>J′π′</sub> ∫₀^{S<sub>n</sub>} T<sub>XL</sub>(E<sub>γ</sub>) ρ(S<sub>n</sub> − E<sub>γ</sub>, J′, π′) dE<sub>γ</sub></div>
  <div class="ctl"><label for="ps-s">Skalierung der Stärke</label><input id="ps-s" type="range" data-bind="scale" min="0.3" max="8" step="0.01" value="1"><output data-show="scale" data-fmt="2"></output></div>
  <p>Die Kurven zeigen, woher die Breite stammt, Photon für Photon: überwiegend von 3 bis 7 MeV und überwiegend aus E1, wobei M1 etwa 15 % beiträgt. Hier, mit geschlossenen Formeln und einer schematischen Niveaudichte anstelle der Tabellen der Engine, kommt die Breite auf etwa ein Sechstel der gemessenen 0,92 eV: So empfindlich hängt sie von der Niveaudichte unterhalb von <i>S<sub>n</sub></i> und vom Ausläufer der Stärke ab. Die Voreinstellungen von TALYS, denen die Engine folgt, ergeben für diesen Kern etwa 1,3 eV. Der Schieberegler wendet den einen Gesamtfaktor an, den eine Evaluation anpassen würde: etwa ×6 bringt sie ins gemessene Band. Der Einfang im keV-Bereich ist nahezu proportional zu ⟨Γ<sub>γ</sub>⟩, wenn Γ<sub>γ</sub> ≪ Γ<sub>n</sub>; ein Faktor hier ist also ein Faktor in (n,γ). TALYS kann die Stärke auf ein gemessenes ⟨Γ<sub>γ</sub>⟩ umskalieren (<code>gnorm</code>); in INCOGNITA ist diese Umskalierung, auf jeden Kern der Kaskade angewandt, ein optionaler Schalter, standardmäßig aus.</p>
</div>
<div class="step">
  <h3>Die Kaskade</h3>
  <p>Unterhalb des ersten Photons wiederholt sich dieselbe Regel: Von jeder neuen Energie aus wird das nächste Photon aus <i>T</i>(<i>E</i><sub>γ</sub>) ρ(<i>E<sub>x</sub></i> − <i>E</i><sub>γ</sub>) gezogen, bis der Kern seine bekannten Niveaus erreicht. Jede Historie besteht aus wenigen Photonen; ihr Summenspektrum ist das, was ein Kalorimeter nach dem Einfang sieht.</p>
  <div class="btns"><button class="btn ghost" data-act="up2" aria-pressed="true">Upbend</button><button class="btn ghost" data-act="clear">Neu beginnen</button></div>
  <p>Der Upbend fügt weiche Photonen hinzu und erhöht die Multiplizität ein wenig. Die Engine zieht keine Historien: Sie verschiebt Besetzungen Intervall für Intervall, von oben nach unten (Kapitel 11), was dieselben Mittelwerte ohne Stichprobenrauschen liefert.</p>
  <div class="aside">Im Code: <code>gamma/strength.py</code> (jedes Stärkemodell, das TALYS unterstützt; voreingestellt die SMLO-2019-Tabellen und das IAEA-M1 mit Upbend), <code>gamma/parameters.py</code> (Systematiken der Riesenresonanzen, Tabellen), <code>gamma/transmission.py</code> (T = 2π E<sup>2L+1</sup> f), <code>gamma/ggnorm.py</code> (optionale ⟨Γγ⟩-Normierung), <code>emission/</code> (die Kaskade). Das Bild verwendet geschlossene Formeln und Systematiken für einen eisen-57-artigen Kern; das gemessene ⟨Γγ⟩ ist der RIPL-Wert für ⁵⁷Fe.</div>
</div>`,
};
Object.assign(WT.L.labels, {
  // scene 1: E1
  "E{#} strength f (MeV⁻³), A = {#}": "E{#}-Stärke f (MeV⁻³), A = {#}",
  "Eγ (MeV)": "Eγ (MeV)",
  "photons that decay uses": "Photonen, die der Zerfall nutzt",
  "GDR: E₀ = {#} MeV, Γ₀ = {#} MeV, σ₀ = {#} mb": "GDR: E₀ = {#} MeV, Γ₀ = {#} MeV, σ₀ = {#} mb",
  "dashed: SLO": "gestrichelt: SLO",
  "at {#} MeV: SMLO / SLO = {#}": "bei {#} MeV: SMLO / SLO = {#}",
  "protons against neutrons": "Protonen gegen Neutronen",
  // scene 2: M1
  "M{#} strength f (MeV⁻³), A = {#}": "M{#}-Stärke f (MeV⁻³), A = {#}",
  "spin-flip": "Spin-Flip",
  "scissors, β = {#}": "Schere, β = {#}",
  "upbend": "Upbend",
  "faint: E{#} at T = {#} MeV": "blass: E{#} bei T = {#} MeV",
  "M{#} > E{#} below {#} MeV": "M{#} > E{#} unterhalb {#} MeV",
  "E{#} dominates at every energy here": "E{#} dominiert hier bei jeder Energie",
  "scissors: the two deformed clouds rock": "Schere: die beiden deformierten Wolken wippen",
  // scene 3: Brink-Axel
  "from {#} MeV": "ab {#} MeV",
  "peak at Eγ ≈ {#} MeV": "Maximum bei Eγ ≈ {#} MeV",
  "primary spectrum T(Eγ) ρ(Eₓ − Eγ), each scaled to its peak": "Primärspektrum T(Eγ) ρ(Eₓ − Eγ), jeweils auf sein Maximum skaliert",
  // scene 4: <Gamma_gamma>
  "contribution to ⟨Γγ⟩ per MeV of photon energy: E{#} (yellow), M{#} (purple, on top)": "Beitrag zu ⟨Γγ⟩ pro MeV Photonenenergie: E{#} (gelb), M{#} (violett, darüber)",
  "{#} eV": "{#} eV",
  "measured {#} eV": "gemessen {#} eV",
  "computed ⟨Γγ⟩ = {#} meV (E{#} {#} %, M{#} {#} %)": "berechnet ⟨Γγ⟩ = {#} meV (E{#} {#} %, M{#} {#} %)",
  // scene 5: cascades
  "Sₙ": "Sₙ",
  "all photons from all cascades": "alle Photonen aus allen Kaskaden",
  "{#} cascades · mean multiplicity {#}": "{#} Kaskaden · mittlere Multiplizität {#}",
});
Object.assign(WT.L.glossary, {
  smlo: {
    term: "SMLO", aliases: ["SMLO"],
    short: "Die vereinfachte modifizierte Lorentz-Kurve: eine E1-Stärkefunktion, deren Breite mit der Photonenenergie und mit der Temperatur der Endzustände wächst.",
    more: "Vorgeschlagen von V. Plujko und Mitarbeitern und für jeden Kern in der IAEA-Datenbank der Photonenstärkefunktionen (2019) tabelliert. Das voreingestellte E1 der Engine ist, wie bei TALYS-2, diese SMLO-2019-Tabelle.",
    chapter: "strength",
  },
  brinkAxel: {
    term: "Brink–Axel-Hypothese", aliases: ["Brink–Axel-Hypothese", "Brink–Axel"],
    short: "Die Annahme, dass die Photonenstärkefunktion nur von der Photonenenergie abhängt, nicht von der Anregungsenergie des emittierenden Zustands.",
    more: "Sie erlaubt es, eine einzige, für den Grundzustand gemessene oder berechnete Stärke für die ganze Kaskade zu verwenden. Geprüft wird sie, indem man Stärken bei verschiedenen Anregungsenergien extrahiert; sie gilt näherungsweise, wobei Abweichungen für bestimmte Kerne und Energien diskutiert werden.",
    chapter: "strength",
  },
});
/* attributes referenced in the English chapter script (for the structure check): data-act="up" data-act="up2" */

Object.assign(WT.L.labels, {
  "zoom: Eγ from {#} to {#} MeV": "Zoom: Eγ von {#} bis {#} MeV",
  "floor: stays above zero": "Boden: bleibt über null",
  "continuum:": "Kontinuum:",
  "dark = dense": "dunkel = dicht",
  "known levels": "bekannte Niveaus",
});
