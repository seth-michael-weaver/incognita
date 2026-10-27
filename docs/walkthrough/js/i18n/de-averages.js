/* German (Deutsch): averages (Kapitel 27, von Resonanzen zu Mittelwerten) */
WT.L.ch.averages = {
  num: "Kapitel 27", title: "Von Resonanzen zu Mittelwerten", short: "Resonanzen zu Mittelwerten",
  lead: "Kapitel 15 hat Resonanzleitern gezeichnet. Hier erscheinen sie als Wirkungsquerschnitte: die R-Matrix-Formel, die Statistik hinter den Parametern, der Einfluss der Temperatur und wie ein Mittel über viele Resonanzen zu Hauser–Feshbach wird.",
  html: `
<div class="step">
  <h3>R-Matrix, Niveau für Niveau</h3>
  <p>Unterhalb einiger keV zeigt sich in einem schweren Kern jedes Compoundniveau einzeln, und der Wirkungsquerschnitt lässt sich exakt durch Niveauparameter ausdrücken: Energien <i>E</i><sub>λ</sub>, reduzierte Neutronenbreiten und Einfangbreiten. Evaluationen verwenden die <b>R-Matrix-Theorie</b>, meist in der <b>Reich–Moore</b>-Form, die die Interferenz zwischen den Niveaus im Neutronenkanal beibehält und die vielen Einfangkanäle als eine einzige absorptive Breite behandelt.</p>
  <div class="formula">R(E) = Σ<sub>λ</sub> γ<sub>λ</sub>² / (E<sub>λ</sub> − E − iΓ<sub>λγ</sub>/2) ,  U = e<sup>−2iφ</sup> (1 + iPR) / (1 − iPR)</div>
  <div class="formula">σ<sub>tot</sub> = (2π/k²) g (1 − Re U) ,  σ<sub>γ</sub> = (π/k²) g (1 − |U|²)</div>
  <div class="btns"><button class="btn ghost" data-act="rm" aria-pressed="true">Reich–Moore</button><button class="btn ghost" data-act="bw" aria-pressed="false">Einniveau-Breit–Wigner</button></div>
  <p>Die obere Kurve ist der totale Wirkungsquerschnitt, die untere der Einfang, für eine Leiter von s-Wellen-Niveaus an einem Target mit Spin 0, ähnlich Uran-238. Zwischen den Niveaus fällt der totale Wirkungsquerschnitt unter die Potentialstreuung, wo sich Resonanz- und Potentialamplitude auslöschen. Die Einniveau-Form addiert die Wirkungsquerschnitte der Niveaus statt ihrer Amplituden; an den Peaks liegt sie nahe, in den Tälern aber falsch, wo sich die Ausläufer vieler Niveaus aufsummieren und der totale Wirkungsquerschnitt sogar negativ werden kann.</p>
</div>
<div class="step">
  <h3>Die Statistik hinter den Parametern</h3>
  <p>Ein nicht gemessener Kern hat keine Leiter, nur ihre Mittelwerte: <i>D</i>₀, die Stärkefunktion <i>S</i>₀ = ⟨Γ<sub>n</sub>⁰⟩/<i>D</i>₀ und ⟨Γ<sub>γ</sub>⟩. Den Rest liefert die Theorie der Zufallsmatrizen: Die Abstände von Niveaus gleichen Spins und gleicher Parität folgen der Wigner-Verteilung, die reduzierten Neutronenbreiten folgen Porter–Thomas, einer χ²-Verteilung mit einem Freiheitsgrad.</p>
  <div class="formula">P(s) = (πs/2) e<sup>−πs²/4</sup> ,  P(y) = e<sup>−y/2</sup> / √(2πy) ,  s = Abstand/D₀, y = Γ<sub>n</sub>⁰/⟨Γ<sub>n</sub>⁰⟩</div>
  <div class="btns"><button class="btn" data-act="more">Zehn weitere Leitern ziehen</button></div>
  <p>Die Histogramme sammeln die Abstände und Breiten aller bisher gezogenen Leitern; die Kurven sind die beiden Gesetze. Die Einfangbreite, eine Summe über Hunderte von Photonenkanälen, schwankt kaum und wird daher als fest angenommen.</p>
</div>
<div class="step">
  <h3>Wärme verschmiert die Peaks</h3>
  <p>Die Targetkerne bewegen sich. Ein Neutron der Energie <i>E</i> trifft sie mit einer Streuung der Relativenergien der Breite Δ = √(4<i>E</i> <i>kT</i>/<i>A</i>), und jede Resonanz wird durch diese Streuung hindurch gesehen: die <b>Doppler-Verbreiterung</b>. Für ein einzelnes Niveau ergibt sich die ψ-Funktion, eine mit einer Gaußkurve gefaltete Lorentzkurve.</p>
  <div class="formula">σ<sub>γ</sub>(E,T) = σ₀ (Γ<sub>γ</sub>/Γ) ψ(x, ξ) ,  x = 2(E − E<sub>λ</sub>)/Γ ,  ξ = Γ/Δ</div>
  <div class="ctl"><label for="av-t">Temperatur (K)</label><input id="av-t" type="range" data-bind="TK" min="0" max="3000" step="10" value="300"><output data-show="TK" data-fmt="0"></output></div>
  <p>Die vergrößerte Resonanz ist die stärkste unter den untersten Niveaus der Leiter; die gestrichelte Linie ist ihre Form bei 0 K. Wärme senkt den Peak und verbreitert die Flanken, während die Fläche unter dem Einfangpeak gleich bleibt. In einer dicken Probe ist das nicht neutral: Der Peak ist selbstabgeschirmt, die Flanken sind es nicht, also fängt heißerer Brennstoff mehr ein. Das ist die Doppler-Rückkopplung eines Reaktors.</p>
</div>
<div class="step">
  <h3>Das Mittel ist Hauser–Feshbach</h3>
  <p>Über viele Resonanzen gemittelt wird der Einfang zu einer glatten Funktion der Energie. Das Fenster gleitet über die Leiter, und sein Mittelwert wird unterwegs aufgetragen; die glatten Kurven sind der Hauser–Feshbach-Wert mit den Transmissionen <i>T<sub>n</sub></i> = 2π⟨Γ<sub>n</sub>⟩/<i>D</i> und <i>T<sub>γ</sub></i> = 2π⟨Γ<sub>γ</sub>⟩/<i>D</i>.</p>
  <div class="ctl"><label for="av-w">Fensterbreite (Niveaus)</label><input id="av-w" type="range" data-bind="win" min="2" max="40" step="1" value="12" data-instant><output data-show="win" data-fmt="0"></output></div>
  <div class="btns"><button class="btn ghost" data-act="ladder">Andere Leiter</button></div>
  <p>Ein schmales Fenster streut stark: wenige Resonanzen, Porter–Thomas-Breiten. Ein breites pendelt sich auf der unteren Kurve ein, der mit der Breitenfluktuationskorrektur. Die obere Kurve, das Produkt der Mittelwerte, liegt hier 25 bis 47 Prozent zu hoch, am meisten dort, wo ⟨Γ<sub>n</sub>⟩ das Ein- bis Dreifache von ⟨Γ<sub>γ</sub>⟩ beträgt, von etwa 100 eV bis 1 keV. (Mit p-Wellen und mehr offenen Kanälen ist die Korrektur kleiner.) Für einen Neutronenkanal mit Porter–Thomas-Breiten und fester Einfangbreite ist der korrigierte Wert exakt: (2π²/k²<i>D</i>) <i>g</i> ⟨Γ<sub>n</sub>Γ<sub>γ</sub>/Γ⟩.</p>
</div>
<div class="step">
  <h3>Aufgelöst, unaufgelöst, glatt</h3>
  <p>Was eine Messung auflöst, hängt von ihrer Energieauflösung ab, und die wird mit steigender Energie schlechter. Die Kurve ist der Wirkungsquerschnitt, wie ihn ein Instrument sieht, verbreitert durch eine Auflösung, die wie <i>E</i><sup>3/2</sup> wächst, wie bei Flugzeitmessungen. Bei niedriger Energie steht jedes Niveau für sich, und seine Parameter lassen sich anpassen: der aufgelöste Resonanzbereich. Weiter oben verschmelzen die Niveaus zu einem fluktuierenden Band, dessen Statistik bekannt ist, nicht aber seine einzelnen Peaks: der unaufgelöste Bereich, beschrieben durch mittlere Parameter und, für die Selbstabschirmung, durch Wahrscheinlichkeitstabellen aus gezogenen Leitern. Darüber übernehmen Hauser–Feshbach und das optische Modell.</p>
  <div class="ctl"><label for="av-r">Instrumentenauflösung (relativ)</label><input id="av-r" type="range" data-bind="res" min="0.2" max="3" step="0.05" value="1"><output data-show="res" data-fmt="2"></output></div>
  <p>Die Bibliothek von INCOGNITA hat noch keinen aufgelösten Resonanzbereich. Ihre Kurven sind Hauser–Feshbach-Mittelwerte bis hinunter zu den niedrigsten Energien; wo gemessene Resonanzen aufgelöst sind, kennzeichnet die Seite <a href="data.html" data-keep-lang>Alle Nuklide</a> die Kurve als Mittelwert. Resonanzparameter und die daraus erzeugten Doppler-verbreiterten punktweisen Wirkungsquerschnitte sind in Arbeit.</p>
  <div class="aside">Im Code: <code>physics/resonance/ladder.py</code> (Abstände nach Zufallsmatrizen, Porter–Thomas-Breiten, Einniveau-Wirkungsquerschnitte, Ensembles), <code>ladder_statistics.py</code> (die Gesetze an gemessenen Leitern getestet), <code>compound/wfc.py</code> (die Breitenfluktuationskorrektur, gegen die die Mittelwerte konvergieren). Die Reich–Moore-, ψ–χ- und Auflösungsformeln im Bild werden hier ausgewertet, mit illustrativen, Uran-238-ähnlichen Parametern; die Hauser–Feshbach-Engine und damit die Bibliothek berechnen noch keine Wirkungsquerschnitte im Resonanzbereich.</div>
</div>`,
};
(function () {
  const L = {
    // axes
    "{#} eV": "{#} eV", "{#} keV": "{#} keV", "{#} b": "{#} b",
    "{#}⁻¹ b": "{#}⁻¹ b", "{#}¹ b": "{#}¹ b", "{#}² b": "{#}² b", "{#}³ b": "{#}³ b", "{#}⁴ b": "{#}⁴ b",
    // scene 1
    "potential scattering {#}πR′² ≈ {#} b": "Potentialstreuung {#}πR′² ≈ {#} b",
    "Reich–Moore (dashed: single-level)": "Reich–Moore (gestrichelt: Einniveau)",
    "single-level Breit–Wigner (dashed: Reich–Moore)": "Einniveau-Breit–Wigner (gestrichelt: Reich–Moore)",
    "total": "total", "capture": "Einfang",
    // scene 2
    "spacings: Wigner": "Abstände: Wigner",
    "s = spacing / D₀": "s = Abstand / D₀",
    "reduced neutron widths: Porter–Thomas": "reduzierte Neutronenbreiten: Porter–Thomas",
    "y = Γn⁰ / ⟨Γn⁰⟩": "y = Γn⁰ / ⟨Γn⁰⟩",
    "{#} ladders · {#} spacings": "{#} Leitern · {#} Abstände",
    "s = {#}": "s = {#}",
    // scene 3
    "capture near the {#} eV resonance": "Einfang nahe der Resonanz bei {#} eV",
    "area {#} b·eV ({#} K: {#})": "Fläche {#} b·eV ({#} K: {#})",
    "target nuclei at {#} K": "Targetkerne bei {#} K",
    "target nuclei at rest": "Targetkerne in Ruhe",
    // scene 4
    "Hauser–Feshbach, no correction": "Hauser–Feshbach, ohne Korrektur",
    "with width fluctuations": "mit Breitenfluktuationen",
    "average capture cross section": "mittlerer Einfangquerschnitt",
    "{#} levels around {#} eV: {#} b · HF {#} b without, {#} b with the correction": "{#} Niveaus um {#} eV: {#} b · HF {#} b ohne, {#} b mit Korrektur",
    // scene 5
    "resolved": "aufgelöst", "unresolved": "unaufgelöst", "averaged": "gemittelt",
    "capture as measured with finite resolution · dashed: Hauser–Feshbach with fluctuations": "Einfang, gemessen mit endlicher Auflösung · gestrichelt: Hauser–Feshbach mit Fluktuationen",
    "resolution reaches D₀/{#} at {#} eV": "Auflösung erreicht D₀/{#} bei {#} eV",
    "resolution reaches D₀/{#} at {#} keV": "Auflösung erreicht D₀/{#} bei {#} keV",
    "time of flight: the arrival time measures the energy": "Flugzeit: Die Ankunftszeit misst die Energie",
  };
  // labels that carry cross sections printed as "12 b" or "3.4k b" (each value independently)
  const B = ["{#} b", "{#}k b"];
  for (const a of B) for (const b of B) {
    L[`{#} eV · total ${a} · capture ${b}`] = `{#} eV · total ${a} · Einfang ${b}`;
    L[`Γ = {#} meV · Δ = {#} meV · peak ${a} ({#} K: ${b})`] = `Γ = {#} meV · Δ = {#} meV · Peak ${a} ({#} K: ${b})`;
  }
  L["{#}k b"] = "{#}k b";
  Object.assign(WT.L.labels, L);
})();
Object.assign(WT.L.glossary, {
  rMatrix: {
    term: "R-Matrix-Theorie", aliases: ["R-Matrix-Theorie", "R-Matrix-Formel", "R-Matrix"],
    short: "Die exakte Beschreibung von Resonanzreaktionen durch Niveauenergien und reduzierte Breiten innerhalb eines Kanalradius, außerhalb angeschlossen an freie Wellen.",
    more: "Evaluationen passen ihre Parameter an gemessene Resonanzen an. Die Einniveau- und Mehrniveau-Breit–Wigner-Formen sowie die Reich–Moore-Form sind Näherungen der vollständigen Theorie.",
    chapter: "averages",
  },
  reichMoore: {
    term: "Reich–Moore", aliases: ["Reich–Moore-Form", "Reich–Moore"],
    short: "Die R-Matrix-Näherung, die in den meisten Evaluationen schwerer Kerne verwendet wird: Die Neutronenkanäle werden exakt behandelt, die vielen Photonenkanäle als eine absorptive Breite pro Niveau.",
    chapter: "averages",
  },
  doppler: {
    term: "Doppler-Verbreiterung", aliases: ["Doppler-Verbreiterung", "Doppler-verbreiterten"],
    short: "Das Verschmieren von Resonanzen durch die thermische Bewegung der Targetkerne: Der Peak sinkt und die Flanken werden breiter, während die Fläche eines isolierten Peaks gleich bleibt.",
    formula: "Δ = √(4 E kT / A)",
    chapter: "averages",
  },
  resolvedRegion: {
    term: "Aufgelöster und unaufgelöster Resonanzbereich", aliases: ["aufgelöste Resonanzbereich", "aufgelösten Resonanzbereich", "aufgelöster Resonanzbereich", "unaufgelöste Bereich", "unaufgelösten Bereich", "unaufgelöster Bereich"],
    short: "Unterhalb einer gewissen Energie wird jede Resonanz einzeln gemessen (aufgelöst); darüber kennt man nur ihre mittleren Parameter (unaufgelöst), bis die Mittelwerte glatt werden.",
    more: "Im unaufgelösten Bereich wird die Selbstabschirmung mit Wahrscheinlichkeitstabellen behandelt, Verteilungen des Wirkungsquerschnitts, die aus gezogenen Resonanzleitern aufgebaut werden.",
    chapter: "averages",
  },
});
