/* German (Deutsch): direct (Kapitel 3, direkte Reaktionen) */
WT.L.ch.direct = {
  num: "Kapitel 3", title: "Ein Streifschuss", short: "Direkte Reaktionen",
  lead: "Nicht jedes Neutron, das den Kern erreicht, wird verschluckt. Manche streifen seine Oberfläche, geben ihm einen einzigen Stoß und fliegen weiter.",
  html: `
<div class="step">
  <p>Ein Neutron, das den Kern nur streift, kann ihn einmal in ein angeregtes Niveau stoßen und weiterfliegen, meist nach vorn und nur wenig langsamer. Das ist eine <b>direkte Reaktion</b>: ein einziger Schritt, nach etwa 10⁻²² Sekunden vorbei. Hier fliegt ein Neutron im Abstand <i>b</i> vorbei, dem <b>Stoßparameter</b>, gemessen in Kernradien <i>R</i>; der gepunktete Ring ist die Haut des Kerns.</p>
  <div class="ctl"><label for="di-b">Zielabstand b (in Radien)</label><input id="di-b" type="range" data-bind="b" min="0" max="1.5" step="0.01" value="1.0"><output data-show="b" data-fmt="2"></output></div>
  <p>Zieh an <i>b</i>. Unterhalb von etwa 0,8 wird das Neutron verschluckt. Nahe 1 streift es den Kern und lässt ihn in seinem ersten angeregten Niveau zurück, 2⁺. Oberhalb von etwa 1,2 verfehlt es ihn und wird nur abgelenkt: <b>elastische Streuung</b>, der Kern bleibt unverändert.</p>
</div>
<div class="step">
  <h3>Einen gestreckten Kern in Drehung versetzen</h3>
  <p>Ein Stoß versetzt einen gestreckten Kern (Kapitel 1) in Rotation, die Leiter seiner <b>Rotationsbande</b> hinauf: 0⁺, 2⁺, 4⁺, 6⁺, 8⁺. Das Neutron kann den Kern hinaufstoßen, und der Kern kann zurückstoßen, daher lässt sich kein Niveau allein berechnen. Die Engine löst sie alle gemeinsam: <b>gekoppelte Kanäle</b>, wobei jeder Kanal ein Ausgang ist, hier ein Niveau der Bande.</p>
  <div class="btns"><button class="btn" data-act="kick">Ein Niveau hinaufstoßen</button><button class="btn ghost" data-act="rpause">Pause / weiter</button></div>
  <div class="ctl"><label for="di-beta">Deformation β₂</label><input id="di-beta" type="range" data-bind="beta2" min="0.05" max="0.4" step="0.01" value="0.25"><output data-show="beta2" data-fmt="2"></output></div>
  <p>Die Bögen zeigen, welche Niveaus verbunden sind: <i>λ</i> = 2, die Gesamtstreckung, verbindet Nachbarn; <i>λ</i> = 4, eine feinere Ausbuchtung, überspringt eines. Zieh an <i>β₂</i>: Ein stärker gestreckter Kern koppelt seine Niveaus stärker, und die Bögen werden dicker. Da die Bande zusammen mit der einlaufenden Welle gelöst wird, lassen die Transmissionskoeffizienten bereits weg, was sie wegnimmt.</p>
</div>
<div class="step">
  <h3>Wellen auf einer Kugel</h3>
  <p>Ein runder Kern kann schwingen, und Schwingungsenergie kommt in gleich großen Paketen, den <b>Phononen</b>. Ein Phonon der Football-zu-Scheibe-Schwingung (<i>λ</i> = 2) ergibt das 2⁺-Niveau; zwei ergeben drei Niveaus, 0⁺, 2⁺ und 4⁺, bei doppelter Energie. Um sie zu erreichen, braucht es zwei Stöße hintereinander. Die Engine löst diese Niveaus zusammen mit dem Grundzustand.</p>
  <div class="ctl"><label for="di-lam">Schwingungsform λ</label><input id="di-lam" type="range" data-bind="lam" min="2" max="3" step="1" value="2" data-instant><output data-show="lam" data-fmt="0"></output></div>
  <div class="btns"><button class="btn ghost" data-act="ph1">Ein Phonon</button><button class="btn ghost" data-act="ph2">Zwei Phononen</button></div>
  <p>Stell <i>λ</i> = 3 ein für eine birnenförmige Schwingung, deren erstes Niveau 3⁻ ist. Drück die Knöpfe, um ein oder zwei Phononen hinzuzufügen.</p>
</div>
<div class="step">
  <h3>Ein Stoß, ein einziges Mal</h3>
  <p>Für die meisten Niveaus ist die Kopplung schwach, und ein Stoß reicht: <b>DWBA</b> (Bornsche Näherung mit verzerrten Wellen). Die einlaufende Welle aus Kapitel 2 stößt den Kern einmal an, am Rand, wo das Potential von tief auf null abfällt; der Rand leuchtet, wo die Wellenberge auftreffen. Die sich ausbreitende Kreiswelle sind die Neutronen, die den Kern angeregt zurückgelassen haben.</p>
  <div class="ctl"><label for="di-bd">Deformation β des Niveaus</label><input id="di-bd" type="range" data-bind="bd" min="0.02" max="0.4" step="0.01" value="0.2"><output data-show="bd" data-fmt="2"></output></div>
  <p>Zieh an <i>β</i>: Der Rand wackelt stärker, und die Kreise werden heller, wie <i>β</i>²: doppelte Deformation, viermal so viele. Die Engine nimmt das <i>β</i> jedes Niveaus aus Messwerten oder, wo keiner bekannt ist, aus Systematiken. Wie sich die gestreuten Neutronen über die Winkel verteilen, ist eine optionale Zusatzausgabe.</p>
</div>
<div class="step">
  <h3>Der ganze Kern bewegt sich</h3>
  <p>Alle Nukleonen können sich gemeinsam bewegen: atmen, sich stauchen und strecken oder in eine Birnenform schwingen. Das sind <b>Riesenresonanzen</b>. In diesem mittelschweren Kern liegen sie etwa 7 bis 25 MeV hoch, jede mehrere MeV breit, zu breit, um als ein Niveau zu zählen; die Buckel markieren die <b>Anregungsenergie</b> jeder einzelnen.</p>
  <p>Die Engine legt die Gesamtstärke jeder Resonanz über eine <b>Summenregel</b> fest, eine Grenze aus der Grundlagenphysik dafür, wie stark ein Kern reagieren kann, und verteilt sie als Buckel oberhalb des letzten bekannten Niveaus. Diese Buckel bilden zusammen mit Stößen in hohe Niveaus das <b>kollektive Kontinuum</b>.</p>
  <div class="btns"><button class="btn ghost" data-act="mono">Atmen</button><button class="btn ghost" data-act="quad">Stauchen</button><button class="btn ghost" data-act="oct">Birne</button></div>
  <p>Die bekannteste, bei der Protonen gegen Neutronen schwappen (die Dipol-Riesenresonanz), absorbiert und emittiert vor allem Licht und gehört deshalb in Kapitel 7.</p>
</div>
<div class="step">
  <h3>Direkt in ein Orbital</h3>
  <p>Ein freies Neutron kann direkt in ein leeres <b>Orbital</b> des Topfs fallen (eine erlaubte Energie für ein einzelnes Neutron darin) und die überschüssige Energie als <em class="g">Photon</em> abgeben. Der Kern heizt sich dabei nie auf. Das ist der <b>direkte Einfang</b>. Die Engine kann ihn mit demselben Topf wie in Kapitel 2 berechnen: die freie Welle außen, das gebundene Orbital innen, das Photon als Verbindung. Er ist optional und standardmäßig aus.</p>
  <div class="btns"><button class="btn" data-act="drop">Ein Neutron hineinfallen lassen</button></div>
  <p>Der direkte Einfang zählt vor allem dort, wo der übliche Weg, das Verteilen der Neutronenenergie, schwach ist: bei leichten Kernen und bei Kernen fern der Stabilität, mit wenigen, weit auseinanderliegenden Niveaus.</p>
</div>
<div class="step">
  <h3>Direkte Reaktionen nehmen sich zuerst ihren Anteil</h3>
  <p>Die Engine teilt den Reaktionsquerschnitt aus Kapitel 2 der Reihe nach auf: zuerst direkte Reaktionen, dann schnelle Stöße, und nur der Rest bildet einen Compoundkern. Im Bild erleidet jedes Neutron eines von drei Schicksalen: <b>direkt</b> (streift und fliegt weiter), schnell (schlägt ein Nukleon heraus, bevor sich die Energie verteilt: <b>Präequilibrium</b>, Kapitel 4) oder verschluckt (ein <b>Compoundkern</b>, Kapitel 5). Die Stapel zählen sie.</p>
  <div class="ctl"><label for="di-e">Neutronenenergie (MeV)</label><input id="di-e" type="range" data-bind="E" min="1" max="60" step="0.5" value="14"><output data-show="E" data-fmt="1"></output></div>
  <p>Ändere die Energie und sieh zu, wie sich die Stapel neu füllen. Bei einigen MeV wird fast jedes Neutron verschluckt. Bei einigen zehn MeV nehmen direkte Reaktionen und schnelle Stöße zusammen einen großen Teil ein.</p>
  <div class="aside">Im Code: <code>ecis/formfactor.py</code>, <code>ecis/coupling.py</code>, <code>ecis/solver.py</code> (deformiertes Potential, gekoppelte Kanäle für Rotoren und Vibratoren), <code>ecis/dwba.py</code> und <code>direct/dwba.py</code> (einzelner Stoß, Riesenresonanzen, kollektives Kontinuum), <code>direct/racapcalc.py</code> (direkter Einfang, optional, standardmäßig aus), <code>compound/normalization.py</code> (die Bilanz).</div>
</div>`,
};
Object.assign(WT.L.labels, {
  // scene: aim
  "skin (surface)": "Haut (Oberfläche)",
  "b = {#} R": "b = {#} R",
  "absorbed: its energy is shared by all nucleons": "absorbiert: seine Energie verteilt sich auf alle Nukleonen",
  "{#}⁺ level": "{#}⁺-Niveau",
  "one push leaves the nucleus on {#}⁺; neutron flies on": "ein Stoß lässt den Kern auf {#}⁺; das Neutron fliegt weiter",
  "a miss: deflected, nucleus unchanged (elastic)": "verfehlt: abgelenkt, Kern unverändert (elastisch)",
  // scene: rotor
  "at rest: {#}⁺": "in Ruhe: {#}⁺",
  "rotating: {#}⁺": "rotierend: {#}⁺",
  "rotating: {#}⁺ (paused)": "rotierend: {#}⁺ (pausiert)",
  "λ = {#}": "λ = {#}",
  "levels solved together": "Niveaus gemeinsam gelöst",
  // scene: vibrator
  "quadrupole ripple: football ↔ disc": "Quadrupolschwingung: Football ↔ Scheibe",
  "octupole ripple: pear ↔ pear": "Oktupolschwingung: Birne ↔ Birne",
  "{#}⁺  no phonon": "{#}⁺  kein Phonon",
  "{#}⁺  one phonon": "{#}⁺  ein Phonon",
  "{#}⁻  one phonon": "{#}⁻  ein Phonon",
  "{#}⁺ {#}⁺ {#}⁺  two phonons": "{#}⁺ {#}⁺ {#}⁺  zwei Phononen",
  "{#}⁺ {#}⁺ {#}⁺ {#}⁺  two phonons": "{#}⁺ {#}⁺ {#}⁺ {#}⁺  zwei Phononen",
  "one push": "ein Stoß",
  "two pushes": "zwei Stöße",
  "two phonons": "zwei Phononen",
  "equal energy steps": "gleiche Energiestufen",
  // scene: DWBA
  "rim: the push happens here": "Rand: hier passiert der Stoß",
  "incoming wave": "einlaufende Welle",
  "outgoing: nucleus left excited": "auslaufend: Kern angeregt zurückgelassen",
  "outgoing circles: the nucleus left on an excited level": "auslaufende Kreise: Kern in einem angeregten Niveau zurückgelassen",
  "push strength ∝ β²: {#}× that at β = {#}": "Stoßstärke ∝ β²: {#}× so viel wie bei β = {#}",
  // scene: giant resonances
  "breathing": "Atmen",
  "squash and stretch": "Stauchen und Strecken",
  "pear": "Birne",
  "breathing (monopole)": "Atmen (Monopol)",
  "squash and stretch (quadrupole)": "Stauchen und Strecken (Quadrupol)",
  "pear-shaped (octupole), low and high": "birnenförmig (Oktupol), tief und hoch",
  "about {#} MeV up": "etwa {#} MeV hoch",
  "last known level": "letztes bekanntes Niveau",
  "excitation energy (MeV) →": "Anregungsenergie (MeV) →",
  // scene: direct capture
  "free: outside the nucleus": "frei: außerhalb des Kerns",
  "empty orbit": "leeres Orbital",
  "drops straight in; a photon carries off the spare energy": "fällt direkt hinein; ein Photon trägt die überschüssige Energie fort",
  // scene: ledger
  "direct": "direkt",
  "fast (pre-eq.)": "schnell (Präeq.)",
  "compound": "Compound",
  "direct: grazed, flew on": "direkt: gestreift, weitergeflogen",
  "fast collision: one out at once": "schneller Stoß: sofort eines heraus",
  "compound: swallowed": "Compound: verschluckt",
  "{#}% (model {#}%)": "{#} % (Modell {#} %)",
  "{#}% seen · model {#}%": "{#} % gesehen · Modell {#} %",
  "{#} MeV neutrons on a medium-mass nucleus (illustrative shares)": "{#}-MeV-Neutronen auf einen mittelschweren Kern (veranschaulichende Anteile)",
});
