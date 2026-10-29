/* German (Deutsch): gamma (Kapitel 10, Photonen) */
WT.L.ch.gamma = {
  num: "Kapitel 10", title: "Gammastrahlungsemission", short: "Photonen",
  lead: "Wenn kein Teilchen hinausgeht, kühlt der Kern ab, indem er Photonen aussendet: Gammastrahlen, Teilchen hochenergetischen Lichts. Dieser Ausgang ist bei jeder Energie offen.",
  html: `
<div class="step">
  <p>Ein heißer Zustand bei 8 MeV (Millionen Elektronenvolt) gibt Photonen (γ) ab; der Stapel neben der Leiter sammelt, wo sie landen. Unterhalb von 2 MeV sind die Zustände einige benannte Sprossen; darüber ein Gedränge, das mit der Energie steil dichter wird (graue Punkte). Jedes Photon trägt die Energie seines Sprungs fort, <i>E<sub>γ</sub></i>, und wird proportional zu <i>E<sub>γ</sub></i>³ heller gezeichnet.</p>
  <div class="formula">T<sub>γ</sub>(E<sub>γ</sub>) = 2π · E<sub>γ</sub><sup>2l+1</sup> · f(E<sub>γ</sub>)</div>
  <p>In Worten: Wie leicht ein Photon der Energie <i>E<sub>γ</sub></i> hinauskommt (<i>T<sub>γ</sub></i>, die Photonentür aus Kapitel 9), wächst für die häufige Photonenart (Dipol, <i>l</i> = 1) wie <i>E<sub>γ</sub></i>³, mal die <b>Photonenstärke</b> <i>f</i>: wie bereitwillig dieser Kern bei dieser Energie strahlt. Dann muss es noch einen Zustand finden, in dem es landet. Kleine Sprünge haben ein Gedränge von Zuständen, die warten, kommen aber kaum hinaus; große Sprünge kommen leicht hinaus, finden aber wenige Zustände. Die Gewinner liegen dazwischen.</p>
  <div class="ctl"><label for="gm-e0">Startenergie</label><input id="gm-e0" type="range" data-bind="E0" min="3" max="9" step="0.5" value="8"><output data-show="E0" data-fmt="1"></output></div>
  <div class="btns"><button class="btn" data-act="emit">100 aussenden</button></div>
  <p>Der Stapel hat sein Maximum einige MeV unterhalb des Starts: Die meisten Photonen tragen 2 bis 4 MeV. Verschieb die Startenergie, und das Maximum folgt.</p>
</div>
<div class="step">
  <h3>Die Dipol-Riesenresonanz</h3>
  <p>Der große Peak rechts ist die <b>Dipol-Riesenresonanz</b>: alle Protonen (schraffiert) schwappen hin und her gegen alle Neutronen (gefüllt). Ihre Frequenz legt die Photonenenergie fest, die der Kern am bereitwilligsten absorbiert und emittiert. Die Kurve ist die Photonenstärke <i>f</i>, auf logarithmischer Skala (jede Stufe nach oben ist zehnmal mehr).</p>
  <div class="ctl"><label for="gm-a">Massenzahl A</label><input id="gm-a" type="range" data-bind="A" min="40" max="240" step="1" value="112"><output data-show="A" data-fmt="0"></output></div>
  <p>Ändere die Massenzahl A (Protonen plus Neutronen): Schwere Kerne schwappen langsamer und klingen bei etwa 12 bis 14 MeV; leichte bei etwa 20. Ein zerfallender Kern sendet Photonen von nur einigen MeV aus, also zählt vor allem der schattierte Ausläufer bei niedriger Energie.</p>
</div>
<div class="step">
  <h3>Magnetische Stärke bei niedriger Energie</h3>
  <p>Ein deformierter Kern strahlt auch magnetisch: Seine Protonen (schraffiert) und Neutronen (gefüllt), zwei Footballs, wippen gegeneinander wie Scherenblätter. Diese <b>Scherenmode</b> liegt nahe 3 MeV. Der <b>Spin-Flip</b>, nahe 8 MeV, besteht aus einzelnen Nukleonen, die ihren Spin umklappen (die kleinen Pfeile), in jeder Form.</p>
  <div class="ctl"><label for="gm-b">Deformation β₂</label><input id="gm-b" type="range" data-bind="beta" min="0" max="0.35" step="0.01" value="0.25"><output data-show="beta" data-fmt="2"></output></div>
  <p>Ändere die Deformation β₂ (0 ist eine Kugel). Je gestreckter, desto mehr Scherenphotonen fliegen; eine Kugel hat keine. Bei den niedrigsten Energien steigt die Stärke wieder an: der <b>Upbend</b>, ein Rinnsal weicher Photonen, den die Engine abschwächt, wenn sich der Kern deformiert. Ein optionaler Schalter, standardmäßig aus, verwendet stärkere Scheren-Systematiken, die zu Oslo-Messungen passen (in Uran vier- bis fünfmal stärker).</p>
</div>
<div class="step">
  <h3>Gammakaskaden</h3>
  <p>Eine Kaskade sind Photonen, die nacheinander ausgesendet werden, von den Intervallen oben (Zustände, die zu dicht zum Auflisten sind, Kapitel 8) hinunter zu den benannten Niveaus, gestreckt, damit man sie lesen kann (volle Sprosse Parität +, hohle −). Dort hört die Engine auf zu schätzen und folgt den tabellierten <b>Verzweigungsverhältnissen</b>: den gemessenen Wahrscheinlichkeiten jedes Niveaus, in jedes tiefere zu zerfallen.</p>
  <div class="btns"><button class="btn" data-act="drop">Eine Kaskade fallen lassen</button></div>
  <p>Drück den Knopf ein paarmal: Der obere Teil ändert sich jedes Mal; das Ende folgt einem von wenigen gemessenen Wegen.</p>
</div>
<div class="step">
  <h3>Isomerproduktion</h3>
  <p>Das 11/2−-Niveau bei 0,40 MeV ist ein <b>Isomer</b>: Sein Spin liegt so weit von dem der Niveaus darunter entfernt, dass ein Photon sie kaum verbinden kann, also lebt es Sekunden bis Jahre, und was dort landet, bleibt. Die Engine behandelt jedes Niveau, das länger als eine Sekunde lebt, als Endpunkt. Jede Kugel ist eine Kaskade, die im Stapel des Isomers oder in dem des Grundzustands endet.</p>
  <div class="ctl"><label for="gm-j">Eingangsspin</label><input id="gm-j" type="range" data-bind="J0" min="0" max="8" step="1" value="2" data-instant><output id="gm-jout">5/2</output></div>
  <p>Ändere den Eingangsspin, bei dem die Kaskaden beginnen, und die Stapel beginnen neu. Der Anteil, der auf dem Isomer endet, das <b>Isomerenverhältnis</b>, hängt davon ab: Ein Start mit hohem Spin speist das Isomer mit hohem Spin; ein Start mit niedrigem Spin rutscht daran vorbei in den Grundzustand.</p>
</div>
<div class="step">
  <h3>Strahlungseinfang</h3>
  <p>Ein Kern, der gerade ein langsames Neutron absorbiert hat, hat zwei Ausgangstüren (Kapitel 9): Photonen (oben) und das Neutron, das wieder hinausgeht (rechts). Der Spalt jeder Tür ist ihre <b>Breite</b>, in eV: wie schnell der Kern durch sie zerfällt. Die Photonenbreite ändert sich kaum; die Neutronenbreite wächst mit der Geschwindigkeit des Neutrons.</p>
  <div class="ctl"><label for="gm-e">Neutronenenergie</label><input id="gm-e" type="range" data-bind="lgE" min="-2" max="3.3" step="0.02" value="0"><output id="gm-eout">1.0 keV</output></div>
  <p>Ändere die Neutronenenergie, von 10 eV bis 2 MeV. <b>Einfang</b>, (n,γ), heißt: Das Neutron bleibt, und ein Photon geht: Bei 10 eV gewinnt er meistens, oberhalb einiger keV wird er zu einem kleinen Anteil. Die Photonenbreite an der Schwelle ist für Hunderte von Kernen gemessen, eine Kontrolle der Photonenstärke. Standardmäßig verwendet die Engine ihre eigene; ein optionaler Schalter skaliert die Photonenstärke jedes gemessenen Kerns, bis beide übereinstimmen.</p>
  <div class="aside">Im Code: <code>gamma/parameters.py</code> (tabellierte E1-Stärken; Systematiken für Riesenresonanz, Spin-Flip, Schere und Upbend), <code>gamma/strength.py</code> (<i>f</i>(E<sub>γ</sub>) für jede Multipolordnung), <code>gamma/transmission.py</code> (T<sub>γ</sub> und die mittlere Strahlungsbreite), <code>structure/levels.py</code> (Verzweigungsverhältnisse, Isomere), <code>emission/multiple.py</code> (die Kaskade). Optional, standardmäßig aus: <code>gamma/scissors.py</code> (stärkere Schere), <code>gamma/ggnorm.py</code> (Anpassung an das gemessene ⟨Γγ⟩, bis Blei), <code>gamma/actphys.py</code> (beides, für Aktiniden).</div>
</div>`,
};
Object.assign(WT.L.labels, {
  // scene 1: emit
  "energy ↑": "Energie ↑",
  "named levels": "benannte Niveaus",
  "a crowd of states": "ein Gedränge von Zuständen",
  "{#} MeV": "{#} MeV",
  "hot state, {#} MeV": "heißer Zustand, {#} MeV",
  "most photons ≈ {#} MeV": "meiste Photonen ≈ {#} MeV",
  "small drops: faint (E³ tiny)": "kleine Sprünge: schwach (E³ winzig)",
  "big drops: bright, but few states to land on": "große Sprünge: hell, aber wenige Zielzustände",
  // scene 2: gdr
  "protons": "Protonen",
  "neutrons": "Neutronen",
  "A = {#}: rings at {#} MeV": "A = {#}: klingt bei {#} MeV",
  "peak {#} MeV": "Peak {#} MeV",
  "giant resonance at {#} MeV": "Riesenresonanz bei {#} MeV",
  "width ≈ {#} MeV": "Breite ≈ {#} MeV",
  "decays use this": "Zerfälle nutzen das",
  "shaded: the tail decays use": "schattiert: der genutzte Ausläufer",
  "photon energy (MeV) →": "Photonenenergie (MeV) →",
  "photon strength f (log scale) ↑": "Photonenstärke f (log. Skala) ↑",
  // scene 3: m1
  "a sphere has no blades: no scissors": "eine Kugel hat keine Blätter: keine Schere",
  "scissors ≈ {#} MeV: strength {#} % of the most stretched": "Schere ≈ {#} MeV: Stärke {#} % der gestrecktesten",
  "spin-flip ≈ {#} MeV: steady, any shape (thick photons)": "Spin-Flip ≈ {#} MeV: gleichbleibend, jede Form (dicke Photonen)",
  "upbend below {#} MeV: soft photons, plenty at this shape": "Upbend unter {#} MeV: weiche Photonen, viele bei dieser Form",
  "upbend below {#} MeV: soft photons, fewer at this shape": "Upbend unter {#} MeV: weiche Photonen, weniger bei dieser Form",
  "upbend below {#} MeV: soft photons, few at this shape": "Upbend unter {#} MeV: weiche Photonen, wenige bei dieser Form",
  // scene 4: cascade
  "ground state": "Grundzustand",
  "isomer": "Isomer",
  "isomer: long-lived": "Isomer: langlebig",
  "bins: too dense to list": "Intervalle: zu dicht zum Auflisten",
  "one photon at a time": "ein Photon nach dem anderen",
  "measured branching ratios": "gemessene Verzweigungen",
  "▬ parity +   ▭ parity −": "▬ Parität +   ▭ Parität −",
  // scene 5: isomer
  "entrance: J = {#}/{#}": "Eingang: J = {#}/{#}",
  "isomer: {#} ({#} %)": "Isomer: {#} ({#} %)",
  "ground state: {#} ({#} %)": "Grundzustand: {#} ({#} %)",
  "many cascades: ≈ {#} % isomer": "viele Kaskaden: ≈ {#} % Isomer",
  "over many cascades from J = {#}/{#}: ≈ {#} % end on the isomer": "über viele Kaskaden ab J = {#}/{#}: ≈ {#} % enden im Isomer",
  // scene 6: capture
  "photon door: {#} eV, barely changes": "Photonentür: {#} eV, ändert sich kaum",
  "captured (n,γ): {#} ({#} %)": "eingefangen (n,γ): {#} ({#} %)",
  "neutron: {#} eV": "Neutron: {#} eV",
  "neutron door: {#} eV, wider when faster": "Neutronentür: {#} eV, breiter, je schneller",
  "back out: {#} ({#} %)": "wieder hinaus: {#} ({#} %)",
  "more doors open (target left excited)": "mehr Türen offen (Target angeregt)",
  "{#} eV neutrons →": "{#}-eV-Neutronen →",
  "{#} keV neutrons →": "{#}-keV-Neutronen →",
  "{#} MeV neutrons →": "{#}-MeV-Neutronen →",
  "slow neutrons: the photon door wins": "langsame Neutronen: die Photonentür gewinnt",
  "the neutron door wins; capture takes about {#} %": "die Neutronentür gewinnt; der Einfang nimmt etwa {#} %",
  "fast: capture is a rare event": "schnell: Einfang ist ein seltenes Ereignis",
});
