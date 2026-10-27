/* German (Deutsch): hauser (Kapitel 22, Hauser–Feshbach Kanal für Kanal, mit Breitenfluktuationen) */
WT.L.ch.hauser = {
  num: "Kapitel 22", title: "Hauser–Feshbach, Kanal für Kanal", short: "Hauser–Feshbach",
  lead: "Kapitel 9 hat den Wettbewerb der Ausgänge als Türen erzählt. Hier steht die Formel hinter den Türen, ein Kanal nach dem anderen, und die Korrektur, die sie braucht, wenn nur wenige Kanäle offen sind.",
  html: `
<div class="step">
  <h3>Eine Transmission für jeden Kanal</h3>
  <p>Ein <b>Kanal</b> ist eine vollständige Ausgangsadresse: welches Teilchen, in welchem Zustand der Restkern zurückbleibt, der Bahndrehimpuls <i>l</i> und der Gesamtdrehimpuls <i>j</i> = <i>l</i> ± ½ des Teilchens. Das optische Modell aus Kapitel 5 gibt jedem Kanal einen <b>Transmissionskoeffizienten</b> <i>T<sub>lj</sub></i>. Die Säulen gehören zum einlaufenden Neutron, für ein Target mit Spin 0.</p>
  <div class="ctl"><label for="hf-e">Neutronenenergie (MeV)</label><input id="hf-e" type="range" data-bind="lgE" min="-3" max="0.7" step="0.01" value="-0.3"><output data-show="Eshow" data-fmt="3"></output></div>
  <p>Bei 1 keV ist nur <i>l</i> = 0 offen, mit <i>T</i> ≈ 2π<i>S</i><sub>0</sub>√<i>E</i>, einige Prozent. Jede weitere Einheit von <i>l</i> kostet bei niedriger Energie etwa einen Faktor (<i>kR</i>)², daher öffnen sich die Säulen mit steigender Energie eine nach der anderen. Jede Säule speist den Compoundkern mit dem Gewicht g<sub>J</sub><i>T</i>:</p>
  <div class="formula">σ<sub>CN</sub> = (π/k²) Σ<sub>J,π</sub> g<sub>J</sub> Σ<sub>lj</sub> T<sub>lj</sub> ,  g<sub>J</sub> = (2J+1) / [(2s+1)(2I+1)]</div>
</div>
<div class="step">
  <h3>Ein Spin und eine Parität nach der anderen</h3>
  <p>Drehimpuls und Parität sind erhalten, also zerfällt der Compoundkern in jedem <i>J</i><sup>π</sup> unabhängig. Innerhalb eines Blocks konkurriert jeder offene Ausgangskanal mit seinem eigenen <i>T</i>: elastisch zurück in den Grundzustand, inelastisch zu jedem angeregten Niveau (eine Säule summiert die (<i>l</i>, <i>j</i>), die an dasselbe <i>J</i> koppeln), das Kontinuum oberhalb von 3,6 MeV, dessen Intervalle als viele Kanäle zählen, gewichtet mit der Niveaudichte, und der Einfang, zusammengefasst in ein einziges winziges <i>T</i><sub>γ</sub> = 2π⟨Γ<sub>γ</sub>⟩/<i>D</i>. Die Höhen sind logarithmisch aufgetragen.</p>
  <div class="ctl"><label for="hf-j">Block aus Spin und Parität</label><input id="hf-j" type="range" data-bind="jb" min="0" max="9" step="1" value="2" data-instant><output data-show="jbShow" data-fmt="0"></output></div>
  <div class="ctl"><label for="hf-e2">Neutronenenergie (MeV)</label><input id="hf-e2" type="range" data-bind="lgE" min="-3" max="0.7" step="0.01" value="-0.3"><output data-show="Eshow" data-fmt="3"></output></div>
  <p>Der Balken unten ist die <b>Hauser–Feshbach</b>-Aufteilung: Jeder Ausgang erhält den Anteil <i>T<sub>b</sub></i>/Σ<i>T<sub>c</sub></i> dessen, was durch den Kanal <i>a</i> hereinkam. Unterhalb von 0,85 MeV sind nur der elastische Kanal und der Einfang offen, und der elastische nimmt fast alles.</p>
  <div class="formula">σ<sub>ab</sub> = (π/k²) Σ<sub>J,π</sub> g<sub>J</sub> T<sub>a</sub> T<sub>b</sub> / Σ<sub>c</sub> T<sub>c</sub> · W<sub>ab</sub></div>
</div>
<div class="step">
  <h3>Breitenfluktuationen</h3>
  <p>Mit <i>W<sub>ab</sub></i> = 1 multipliziert die Formel Mittelwerte. Die Resonanzen hinter den Mittelwerten haben streuende Breiten (Porter–Thomas, Kapitel 15), und bei elastischer Streuung ist die Breite, die das Neutron hereinlässt, dieselbe, die es wieder hinauslässt; beide sind also korreliert. Für den elastischen Kanal übersteigt dann der Mittelwert der Produkte das Produkt der Mittelwerte, und die übrigen Ausgänge verlieren, was der elastische gewinnt.</p>
  <div class="btns"><button class="btn ghost" data-act="w0" aria-pressed="false">Ohne Korrektur</button><button class="btn ghost" data-act="w1" aria-pressed="true">Moldauer</button></div>
  <div class="ctl"><label for="hf-e3">Neutronenenergie (MeV)</label><input id="hf-e3" type="range" data-bind="lgE" min="-3" max="0.7" step="0.01" value="-0.3"><output data-show="Eshow" data-fmt="3"></output></div>
  <p>Die Marken geben σ mit Korrektur geteilt durch σ ohne an. Unterhalb der ersten inelastischen Schwelle nimmt der elastische Kanal schon fast den ganzen Fluss und ändert sich kaum, während der Einfang 10 bis 25 Prozent verliert. Zwischen 1 und 1,5 MeV gewinnt die compound-elastische Streuung 15 bis 35 Prozent, und das erste 2⁺-Niveau verliert etwa ein Drittel. Wenn sich weitere Niveaus und das Kontinuum öffnen, wird der compound-elastische Anteil am Fluss klein: Sein eigener Faktor steigt in Richtung 2, doch was er den anderen wegnimmt, schrumpft, und deren Faktoren kehren in Richtung 1 zurück. In Moldauers Rezept erhält jeder Kanal eine Zahl von Freiheitsgraden ν<sub>c</sub>, und <i>W</i> ist ein eindimensionales Integral, ausgewertet mit der 32-Punkte-Gauß–Laguerre-Regel von TALYS.</p>
  <div class="formula">W<sub>ab</sub> = (1 + 2δ<sub>ab</sub>/ν<sub>a</sub>) ∫₀^∞ dx Π<sub>c</sub> (1 + 2T<sub>c</sub>x / ν<sub>c</sub>ΣT)<sup>−(δ<sub>ac</sub>+δ<sub>bc</sub>+ν<sub>c</sub>/2)</sup></div>
  <div class="formula">ν<sub>c</sub> = 1.78 + (T<sub>c</sub><sup>1.212</sup> − 0.78) e<sup>−0.228 ΣT</sup></div>
</div>
<div class="step">
  <h3>Moldauer und HRTW</h3>
  <p>Die Kurven führen dieselbe Rechnung über den ganzen Energiebereich: das Verhältnis für die compound-elastische Streuung, für das erste 2⁺-Niveau und für den Einfang, Moldauer durchgezogen und das <b>HRTW</b>-Rezept gestrichelt. HRTW ersetzt das Integral durch einen elastischen Faktor <i>W<sub>a</sub></i> und effektive Transmissionen <i>V<sub>a</sub></i>, die iterativ bestimmt werden.</p>
  <div class="ctl"><label for="hf-e4">Neutronenenergie (MeV)</label><input id="hf-e4" type="range" data-bind="lgE" min="-3" max="0.7" step="0.01" value="-0.3"><output data-show="Eshow" data-fmt="3"></output></div>
  <div class="formula">σ<sub>ab</sub> ∝ V<sub>a</sub>V<sub>b</sub> / ΣV<sub>c</sub> · [1 + δ<sub>ab</sub>(W<sub>a</sub> − 1)] ,  V<sub>a</sub> = T<sub>a</sub> / [1 + (W<sub>a</sub> − 1) V<sub>a</sub>/ΣV]</div>
  <p>Für elastische und inelastische Streuung stimmen beide eng überein; beim Einfang im keV-Bereich zieht HRTW bis zu 10 Prozent mehr ab. Zwischen 0,85 und 2 MeV gewinnt der Einfang sogar: Dort wird die Gesamtbreite von wenigen fluktuierenden Neutronenbreiten bestimmt, und der Mittelwert von 1/Γ übersteigt 1/⟨Γ⟩. Beide Rezepte sind Anpassungen an das exakte Ergebnis der Zufallsmatrizen (GOE), das TALYS auch als Dreifachintegral anbietet. INCOGNITA portiert alle drei (<code>widthmode</code> 1, 2, 3); Standard ist Moldauer, angewandt für einlaufende Neutronen bis zur Neutronenseparationsenergie des Targets.</p>
</div>
<div class="step">
  <h3>Zwischen 3 und 2</h3>
  <p>Die Grenzfälle erklären die Größe des Effekts. Nimm <i>N</i> gleiche Kanäle ohne Einfang und variiere ihre Summe ΣT, das 2π-Fache des Verhältnisses von mittlerer Gesamtbreite zu Niveauabstand, Γ/<i>D</i>. Bei isolierten Resonanzen (ΣT ≪ 1) und vielen Kanälen folgt jede Breite Porter–Thomas mit einem Freiheitsgrad, und die elastische Überhöhung beträgt ⟨Γ<sub>a</sub>²⟩/⟨Γ<sub>a</sub>⟩² = 3. Überlappen die Resonanzen stark (ΣT ≫ 2π), fluktuiert der Wirkungsquerschnitt wie eine Zufallswelle (Ericson-Fluktuationen), und die Überhöhung fällt auf 2.</p>
  <div class="ctl"><label for="hf-n">Offene Kanäle N</label><input id="hf-n" type="range" data-bind="nch" min="2" max="60" step="1" value="30" data-instant><output data-show="nch" data-fmt="0"></output></div>
  <p>Für <i>N</i> isolierte Kanäle ist der exakte Wert 3<i>N</i>/(<i>N</i>+2) (die Raute): Bei nur zwei Kanälen kann die Überhöhung 1,5 nicht übersteigen, weil die Gesamtbreite dann ebenso stark fluktuiert wie die elastische. Moldauers Rezept gibt diesen Grenzwert wieder; HRTW bleibt darunter, wenn viele schwache Kanäle offen sind. Der Einschub zeichnet Resonanzen mit der Breite, die zum wandernden Punkt gehört. In Moldauers Formel ist der Grenzwert für viele Kanäle 1 + 2/ν: ν → 1 für isolierte Resonanzen, ν → 1,78 bei Überlapp (2,12, der kleine Fehler der Anpassung bei vollem Überlapp).</p>
  <div class="aside">Im Code: <code>compound/prepare.py</code> (Ausgangskanäle und ihre Transmissionen pro <i>J</i><sup>π</sup>), <code>compound/target.py</code> (die Hauser–Feshbach-Summen), <code>compound/wfc.py</code> (Moldauer, HRTW und GOE, aus TALYS portiert). Das Bild wertet dieselben Formeln mit illustrativen Zutaten aus: Transmissionen einer harten Kugel für ein eisenähnliches Target, sieben Niveaus, ein Kontinuum konstanter Temperatur und ein zusammengefasster Einfangkanal.</div>
</div>`,
};
(function () {
  const L = {
    // scene 1: incident T_lj
    "T = {#}": "T = {#}",
    "l={#}": "l={#}",
    "hollow: j = l − ½ · solid: j = l + ½": "hohl: j = l − ½ · voll: j = l + ½",
    "compound nucleus": "Compoundkern",
    "compound nucleus · σ(CN) ≈ {#} b": "Compoundkern · σ(CN) ≈ {#} b",
    "σ(CN) ≈ {#} b": "σ(CN) ≈ {#} b",
    "E = {#} MeV · kR = {#}": "E = {#} MeV · kR = {#}",
    "E = {#} keV · kR = {#}": "E = {#} keV · kR = {#}",
    "transmission Tₗⱼ of the incident neutron": "Transmission Tₗⱼ des einlaufenden Neutrons",
    // scene 2: one J^pi block
    "elastic": "elastisch", "cont.": "Kont.",
    "level energy (MeV) under each column": "Niveauenergie (MeV) unter jeder Säule",
    "residual level (energy in MeV) · n×: number of (l, j) channels summed": "Niveau des Restkerns (Energie in MeV) · n×: Zahl der summierten (l, j)-Kanäle",
    "{#}/{#}⁺ block · in through l = {#}, Tₐ = {#}": "Block {#}/{#}⁺ · Eingang über l = {#}, Tₐ = {#}",
    "{#}/{#}⁻ block · in through l = {#}, Tₐ = {#}": "Block {#}/{#}⁻ · Eingang über l = {#}, Tₐ = {#}",
    "elastic {#} %": "elastisch {#} %", "higher {#} %": "höhere {#} %",
    "Hauser–Feshbach split: T / ΣT for each exit": "Hauser–Feshbach-Aufteilung: T / ΣT für jeden Ausgang",
    // scene 3: HF vs WFC
    "closed": "geschlossen",
    "compound elastic": "compound-elastisch", "first {#}⁺ level": "erstes {#}⁺-Niveau",
    "higher levels": "höhere Niveaus", "capture": "Einfang",
    "{#} mb": "{#} mb",
    "with Moldauer's correction": "mit Moldauers Korrektur",
    "Hauser–Feshbach without correction": "Hauser–Feshbach ohne Korrektur",
    "compound formation {#} mb at {#} MeV": "Compoundbildung {#} mb bei {#} MeV",
    "compound formation {#} mb at {#} keV": "Compoundbildung {#} mb bei {#} keV",
    // scene 4: ratio curves
    "{#} keV": "{#} keV", "{#} MeV": "{#} MeV",
    "{#}⁺ opens": "{#}⁺ öffnet", "continuum": "Kontinuum", "continuum opens": "Kontinuum öffnet",
    "elastic ×{#} (Moldauer) · ×{#} (HRTW)": "elastisch ×{#} (Moldauer) · ×{#} (HRTW)",
    "capture ×{#} (Moldauer) · ×{#} (HRTW)": "Einfang ×{#} (Moldauer) · ×{#} (HRTW)",
    "first {#}⁺ ×{#} (Moldauer) · ×{#} (HRTW)": "erstes {#}⁺ ×{#} (Moldauer) · ×{#} (HRTW)",
    "solid: Moldauer · dashed: HRTW": "durchgezogen: Moldauer · gestrichelt: HRTW",
    "σ with correction / σ without": "σ mit Korrektur / σ ohne",
    // scene 5: limits
    "ΣT = {#}πΓ/D →": "ΣT = {#}πΓ/D →",
    "elastic enhancement Wₐₐ": "elastische Überhöhung Wₐₐ",
    "T → {#} per channel": "T → {#} pro Kanal",
    "exact, isolated: {#}N/(N+{#}) = {#}": "exakt, isoliert: {#}N/(N+{#}) = {#}",
    "Porter–Thomas: {#}": "Porter–Thomas: {#}",
    "Ericson: {#}": "Ericson: {#}",
    "{#} channels · ΣT = {#} · Wₐₐ = {#}": "{#} Kanäle · ΣT = {#} · Wₐₐ = {#}",
    "isolated resonances: Γ ≪ D": "isolierte Resonanzen: Γ ≪ D",
    "resonances begin to overlap": "Resonanzen beginnen zu überlappen",
    "strongly overlapping: Γ ≫ D": "stark überlappend: Γ ≫ D",
  };
  Object.assign(WT.L.labels, L);
})();
Object.assign(WT.L.glossary, {
  hrtw: {
    term: "HRTW", aliases: ["HRTW"],
    short: "Ein Rezept für die Breitenfluktuationskorrektur von Hofmann, Richert, Tepel und Weidenmüller: ein elastischer Faktor pro Kanal und effektive Transmissionen, iterativ bestimmt.",
    more: "Es wurde, wie das von Moldauer, an numerische Rechnungen mit Zufallsmatrizen angepasst. TALYS bietet es als widthmode 2 an; Moldauer (1) ist der Standard und das exakte GOE-Dreifachintegral (3) die Referenz.",
    chapter: "hauser",
  },
  ericson: {
    term: "Ericson-Fluktuationen", aliases: ["Ericson-Fluktuationen"],
    short: "Zufällige Schwankungen eines Wirkungsquerschnitts mit der Energie, wenn viele Resonanzen überlappen, auf einer Energieskala, die ihre mittlere Gesamtbreite festlegt.",
    more: "Sie sind der Grenzfall starken Überlapps derselben Statistik, die bei isolierten Resonanzen Porter–Thomas-Breiten liefert. Dort strebt der Faktor der elastischen Überhöhung gegen 2.",
    chapter: "hauser",
  },
});
