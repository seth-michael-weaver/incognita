/* German (Deutsch): exciton (Kapitel 26, das Exzitonenmodell in Zahlen) */
WT.L.ch.exciton = {
  num: "Kapitel 26", title: "Das Exzitonenmodell in Zahlen", short: "Exzitonenmodell",
  lead: "Kapitel 7 hat ein schnelles Neutron durch einige Stöße begleitet. Hier sind die Raten, die auf jeder Stufe entscheiden, ob als Nächstes ein weiterer Stoß oder ein Entkommen folgt, und das Spektrum, das sich aus ihnen ergibt.",
  html: `
<div class="step">
  <h3>Teilchen-Loch-Zustände zählen</h3>
  <p>Das Exzitonenmodell klassifiziert den Kern auf dem Weg ins Gleichgewicht nach der Zahl seiner angeregten Teilchen <i>p</i> und Löcher <i>h</i>, <i>n</i> = <i>p</i> + <i>h</i>. Ein Neutron, das in ein Target eindringt, beginnt bei <i>p</i> = 1, <i>h</i> = 0; jeder Stoß fügt ein Paar hinzu. Entscheidend ist auf jeder Stufe, auf wie viele Arten sich die Energie auf die <i>n</i> Exzitonen verteilen lässt: die Teilchen-Loch-Zustandsdichte.</p>
  <div class="formula">ω(p,h,E) = g<sup>n</sup> (E − A<sub>p,h</sub>)<sup>n−1</sup> / (p! h! (n−1)!) ,  A<sub>p,h</sub> = max(p,h)²/g − (p² + h² + p + h)/4g</div>
  <div class="ctl"><label for="ex-n">Teilchen p (Löcher p − 1)</label><input id="ex-n" type="range" data-bind="pp" min="2" max="6" step="1" value="3" data-instant><output data-show="pp" data-fmt="0"></output></div>
  <div class="btns"><button class="btn ghost" data-act="pauli" aria-pressed="true">Pauli-Korrektur</button></div>
  <p><i>g</i> ≈ <i>A</i>/15 MeV⁻¹ ist die Dichte der Einteilchenniveaus nahe der Fermi-Energie. <i>A<sub>p,h</sub></i> ist die <b>Pauli-Korrektur</b>: Zwei Teilchen können nicht dasselbe Niveau besetzen, also kosten die tiefsten Konfigurationen Energie, und die Dichte nahe der Schwelle sinkt. Die Skizze zeigt jeweils eine zufällig gezogene Konfiguration mit dem gewählten <i>p</i>.</p>
</div>
<div class="step">
  <h3>Tiefer hinein oder hinaus</h3>
  <p>Von jeder Stufe aus kann zweierlei geschehen. Ein Stoß erzeugt ein weiteres Paar, mit der Rate λ<sup>+</sup>, nach Fermis goldener Regel das Quadrat des Matrixelements mal der Dichte der erreichbaren Zustände. Oder ein Teilchen verlässt den Kern, mit der Rate <i>W</i>, die aus dem detaillierten Gleichgewicht folgt: aus dem inversen Wirkungsquerschnitt und dem Verhältnis der Zustandsdichten mit und ohne das entweichende Teilchen.</p>
  <div class="formula">λ<sup>+</sup>(n) = (2π/ħ) M² ω<sub>acc</sub> ,  W(p,h,ε) = (2s+1)/(π²ħ³) με σ<sub>inv</sub>(ε) ω(p−1,h,U) / ω(p,h,E)</div>
  <div class="ctl"><label for="ex-e">Neutronenenergie (MeV)</label><input id="ex-e" type="range" data-bind="Ein" min="5" max="60" step="0.5" value="20"><output data-show="Ein" data-fmt="1"></output></div>
  <p>Die Balken sind die beiden Raten auf jeder Stufe, auf logarithmischer Skala: λ<sup>+</sup> von der Größenordnung 10²² s⁻¹, <i>W</i> auf der ersten Stufe etwa ein Zehntel davon und mit jeder Stufe kleiner, denn jedes neue Paar verringert die Energie, die das führende Teilchen tragen kann. Die Engine nimmt M² in der Form von Koning und Duijvestijn, die mit der Energie pro Exziton abfällt:</p>
  <div class="formula">M² = (C₁ A<sub>p</sub> / A³) · [7.48 + 4.62×10⁵ / (E/(n A<sub>p</sub>) + 10.7)³]  MeV²</div>
</div>
<div class="step">
  <h3>Die Kette in der Zeit</h3>
  <p>Vernachlässigt man die seltenen Stöße, die ein Paar vernichten (die Never-come-back-Näherung), gehorchen die Besetzungen einer einfachen Kette: Jede Stufe füllt sich aus der vorherigen und leert sich in die nächste und ins Kontinuum. Die Balken lösen diese Mastergleichung; die Zeit ist in Einheiten von 10⁻²² s angegeben.</p>
  <div class="formula">dP(n)/dt = λ<sup>+</sup>(n−2) P(n−2) − [λ<sup>+</sup>(n) + W(n)] P(n)</div>
  <div class="ctl"><label for="ex-e2">Neutronenenergie (MeV)</label><input id="ex-e2" type="range" data-bind="Ein" min="5" max="60" step="0.5" value="20"><output data-show="Ein" data-fmt="1"></output></div>
  <p>Nach wenigen 10⁻²² s ist die ganze Kette durchlaufen. Der Anteil, der unterwegs entweicht, ist die Präequilibrium-Emission; der Rest wird, in der Engine wie in TALYS nach höchstens sechs Teilchen, an den Compoundkern übergeben. Die Integration über die Zeit gibt jeder Stufe eine Stärke τ(<i>n</i>)·<i>P</i>(<i>n</i>), und genau dieses Produkt berechnet die Engine.</p>
</div>
<div class="step">
  <h3>Woher der harte Ausläufer kommt</h3>
  <p>Das Emissionsspektrum ist die Summe über die Stufen aus Besetzung mal Lebensdauer mal Emissionsrate, dazu die Verdampfung dessen, was übrig bleibt. Die Stufe <i>n</i> = 3 allein, zwei Teilchen und ein Loch, erreicht die höchsten Austrittsenergien: Ihr Spektrum fällt zum Endpunkt hin nur linear ab. Jede spätere Stufe ist weicher.</p>
  <div class="formula">dσ/dε = σ<sub>CN</sub> Σ<sub>n</sub> P(n) τ(n) W(n,ε) + Verdampfung</div>
  <div class="ctl"><label for="ex-e3">Neutronenenergie (MeV)</label><input id="ex-e3" type="range" data-bind="Ein" min="5" max="60" step="0.5" value="20"><output data-show="Ein" data-fmt="1"></output></div>
  <p>Erhöhe die Energie, und das Spektrum wird härter: Der Präequilibrium-Ausläufer reicht bis zum Endpunkt, während der Verdampfungsbuckel bei 1 bis 2 MeV bleibt. Oberhalb von etwa 10 MeV lassen sich die gemessenen hochenergetischen Neutronen nur mit diesem Ausläufer reproduzieren.</p>
</div>
<div class="step">
  <h3>Wie groß der Anteil ist</h3>
  <p>Der Präequilibrium-Anteil an der Emission wächst mit der Einschussenergie, hier von einigen Prozent nahe 5 MeV auf etwa 40 Prozent bei 40 MeV. Er hängt von einer einzigen anpassbaren Konstante ab, der Gesamtgröße des Matrixelements: Eine schwächere Wechselwirkung bedeutet langsamere Äquilibrierung und mehr frühe Emission.</p>
  <div class="ctl"><label for="ex-c">Matrixelement-Konstante C₁</label><input id="ex-c" type="range" data-bind="c1" min="0.3" max="3" step="0.05" value="1"><output data-show="c1" data-fmt="2"></output></div>
  <p>Die gestrichelte Kurve ist C₁ = 1, der Standardwert der Engine; die durchgezogene folgt dem Regler. Halbiert man C₁, steigt der Anteil um einen Faktor 1,5 bis 1,9, nicht 2: Die Entkommwahrscheinlichkeit jeder Stufe ist W/(λ<sup>+</sup> + W), nicht W/λ<sup>+</sup>, und weniger Kerne erreichen die späteren Stufen.</p>
</div>
<div class="step">
  <h3>Zwei Komponenten und ein zweites Entkommen</h3>
  <p>Die Engine verfolgt Protonen und Neutronen getrennt (<i>p</i><sub>π</sub>, <i>h</i><sub>π</sub>, <i>p</i><sub>ν</sub>, <i>h</i><sub>ν</sub>), mit verschiedenen Matrixelementen für gleichartige und ungleichartige Paare, einer verringerten Potentialtiefe für den ersten Stoß nahe der Oberfläche und den Regeln von Kalbach für Cluster. Oberhalb von 20 MeV lässt sie außerdem den Restkern, der noch Exzitonen trägt, ein zweites schnelles Teilchen emittieren, bevor er ins Gleichgewicht kommt.</p>
  <div class="ctl"><label for="ex-e4">Neutronenenergie (MeV)</label><input id="ex-e4" type="range" data-bind="Ein" min="5" max="60" step="0.5" value="20"><output data-show="Ein" data-fmt="1"></output></div>
  <p>Die Kurve ist eine Spielzeugversion davon: nach einer ersten Emission aus der Drei-Exzitonen-Stufe die Wahrscheinlichkeit, dass das übrig gebliebene Teilchen des Restkerns vor seinem nächsten Stoß entweicht. Sie bleibt unterhalb von 20 MeV klein und wächst darüber, und genau dort schaltet die Engine das mehrfache Präequilibrium ein.</p>
  <div class="aside">Im Code: <code>density/particle_hole.py</code> (Williams-Dichten, Pauli- und Endlich-Topf-Korrekturen, eine und zwei Komponenten), <code>preeq/exciton.py</code> (Matrixelemente, Emissions- und Übergangsraten, Lebensdauern, die Never-come-back-Lösung), <code>preeq/complex.py</code> (Kalbach-Pickup, Stripping und Knockout), <code>preeq/multi.py</code> (mehrfaches Präequilibrium, standardmäßig ab 20 MeV). Das Bild ist einkomponentig, mit einem schematischen inversen Wirkungsquerschnitt, für ein eisen-56-artiges Target.</div>
</div>`,
};
Object.assign(WT.L.labels, {
  // scene 1: state densities
  "E (MeV)": "E (MeV)",
  "ω(p, h, E) per MeV": "ω(p, h, E) pro MeV",
  "{#}p{#}h": "{#}p{#}h",
  "dashed: no Pauli correction": "gestrichelt: ohne Pauli-Korrektur",
  "Fermi level": "Fermi-Niveau",
  "{#} particles, {#} holes": "{#} Teilchen, {#} Löcher",
  // scene 2: rates
  "rate (s⁻¹)": "Rate (s⁻¹)",
  "n = {#}": "n = {#}",
  "W/λ⁺ = {#}": "W/λ⁺ = {#}",
  "blue: λ⁺, the next collision · yellow: W, neutron escape": "blau: λ⁺, der nächste Stoß · gelb: W, Neutron entweicht",
  "E = {#} + Sₙ = {#} MeV · τ(n={#}) = {#} × {#}⁻²² s": "E = {#} + Sₙ = {#} MeV · τ(n={#}) = {#} × {#}⁻²² s",
  // scene 3: master equation
  "compound": "Compoundkern",
  "emitted before equilibrium: {#} % (of {#} % in the end)": "vor dem Gleichgewicht emittiert: {#} % (von am Ende {#} %)",
  "t = {#} × {#}⁻²² s": "t = {#} × {#}⁻²² s",
  // scene 4: spectrum
  "outgoing neutron energy ε (MeV)": "Energie des auslaufenden Neutrons ε (MeV)",
  "dσ/dε (mb/MeV)": "dσ/dε (mb/MeV)",
  "evaporation": "Verdampfung",
  "ε = {#} MeV: {#} % from n = {#}": "ε = {#} MeV: {#} % aus n = {#}",
  "pre-equilibrium {#} % of the emission · solid: total": "Präequilibrium {#} % der Emission · durchgezogen: gesamt",
  // scene 5: share
  "{#} MeV": "{#} MeV",
  "pre-equilibrium share of the emission": "Präequilibrium-Anteil an der Emission",
  "{#} MeV: {#} %": "{#} MeV: {#} %",
  "C₁ = {#} (dashed: {#})": "C₁ = {#} (gestrichelt: {#})",
  // scene 6: second escape
  "{#} MeV: multiple pre-equilibrium on": "{#} MeV: mehrfaches Präequilibrium an",
  "chance of a second fast emission (toy estimate)": "Wahrscheinlichkeit einer zweiten schnellen Emission (grobe Abschätzung)",
  "residual: {#}p{#}h": "Restkern: {#}p{#}h",
});
Object.assign(WT.L.glossary, {
  neverComeBack: {
    term: "Never-come-back-Näherung", aliases: ["Never-come-back-Näherung", "Never-come-back-Lösung"],
    short: "Die Näherung, dass Stöße zu Beginn der Äquilibrierung nur Teilchen-Loch-Paare hinzufügen und nie entfernen.",
    more: "Sie macht aus der Mastergleichung eine einfache Kette, die sich Stufe für Stufe integrieren lässt. Sie gilt, solange die Exzitonenzahl weit unter ihrem Gleichgewichtswert liegt, und genau dort findet die Präequilibrium-Emission statt.",
    chapter: "exciton",
  },
});
