/* German (Deutsch): fission (Kapitel 12, Kernspaltung) */
WT.L.ch.fission = {
  num: "Kapitel 12", title: "Kernspaltung", short: "Spaltung",
  lead: "Die schwersten Kerne haben einen Ausgang, der leichteren fehlt: Statt ein Teilchen hinauszuwerfen, reißt der ganze Kern in zwei Teile. Das ist die Kernspaltung.",
  html: `
<div class="step">
  <p>Ein schwerer Kern verhält sich wie ein Tropfen geladener Flüssigkeit. Die Oberflächenspannung (graue Pfeile) zieht ihn rund; die Protonen, alle positiv geladen, drücken ihn auseinander (rote Pfeile). Bei Uran halten sich beide fast die Waage.</p>
  <div class="ctl"><label for="fis-d">Tropfen strecken</label><input id="fis-d" type="range" data-bind="def" min="0" max="1" step="0.01" value="0"><output data-show="def" data-fmt="2"></output></div>
  <p>Zieh am Regler, um ihn zu strecken, und beobachte den Punkt auf der kleinen Energiekurve darunter. Strecken vergrößert die Oberfläche, was Energie kostet, verteilt aber die Ladung, was Energie freisetzt. Jenseits des Kurvengipfels gewinnt die Ladung: Ein Hals bildet sich, und die Hälften fliegen mit etwa 200 MeV auseinander.</p>
</div>
<div class="step">
  <h3>Die Potentialenergiefläche</h3>
  <p>Die Kurve ist die Energie für jede Form, von rund (links) bis gespalten (rechts). Ein glatter Flüssigkeitstropfen ergibt einen einzigen Hügel, doch Nukleonen füllen Energieniveaus in Gruppen, den <b>Schalen</b>, und in den schwersten Elementen gräbt das eine Mulde hinein: eine <b>Doppelhöckerbarriere</b>, in der der Kern in einer gestreckten Form verweilen kann.</p>
  <p>Die Engine nimmt diese Kurve nicht einfach an: Sie liest sie Punkt für Punkt aus einer mikroskopischen Rechnung der Energie bei jeder Deformation (dem Maß der Streckung).</p>
</div>
<div class="step">
  <h3>Barrieredurchdringung</h3>
  <p>Die Kugel ist der angeregte Kern in der ersten Mulde, bei der Anregungsenergie der orange gestrichelten Linie, unterhalb des 6 MeV hohen Gipfels. Klassisch kann er nie hinüber; die Quantenmechanik lässt ihn durch den dunkleren, verbotenen Teil <b>tunneln</b>, mit einer Wahrscheinlichkeit <i>T</i>, die exponentiell fällt, je dicker dieser Teil ist.</p>
  <div class="ctl"><label for="fis-e">Anregungsenergie</label><input id="fis-e" type="range" data-bind="E" min="3" max="8" step="0.05" value="5"><output data-show="E" data-fmt="2"></output></div>
  <p>Erhöhe die Energie und sieh zu, wie <i>T</i> steigt, während der verbotene Teil dünner wird. Die Lehrbuch-Abkürzung (Hill–Wheeler) behandelt den Gipfel als Parabel (blau gestrichelt). Die Engine folgt der echten Form, die weiter unten breiter ist, also ist ihre Wahrscheinlichkeit weit unterhalb des Gipfels kleiner. <i>K</i> misst, wie viel Hügel im Weg ist.</p>
  <div class="formula">T = 1 / (1 + e<sup>2K</sup>),  K = ∫ √(2μ(V−E)) dβ / ħ</div>
</div>
<div class="step">
  <h3>Übergangszustände</h3>
  <p>Die Türen auf dem Gipfel sind die <b>Übergangszustände</b>, die Quantenzustände des über die Barriere gestreckten Kerns. Jeder hat einen Spin und eine Parität (0⁺, 2⁻, …) und wirkt als Tor; sein heller Spalt zeigt, wie offen es ist. Ein Kern kommt nur durch Tore, die zu seinem eigenen Spin und seiner Parität passen, und jedes öffnet sich allmählich, wenn die Energie seine Höhe überschreitet.</p>
  <div class="ctl"><label for="fis-e2">Anregungsenergie</label><input id="fis-e2" type="range" data-bind="E" min="3" max="8" step="0.05" value="5"><output data-show="E" data-fmt="2"></output></div>
  <div class="btns"><button class="btn ghost" data-act="jpAll">Beliebiger Spin</button><button class="btn ghost" data-act="jp0">Compound 0⁺</button><button class="btn ghost" data-act="jp1">Compound 1⁻</button></div>
  <p>Wähl einen Spin und eine Parität: Nur passende Tore zählen, und die gesamte Öffnung sinkt. Weiter oben drängen sich die Tore zu einem <b>Kontinuum</b>, und die Engine zählt sie über ihre Dichte, wie bei gewöhnlichen Niveaus.</p>
</div>
<div class="step">
  <h3>Doppelhöckrige Barrieren</h3>
  <p>Jetzt beide Hügel, jeder mit einem Tor (der Kreis; sein gefüllter Teil zeigt, wie offen es ist). Kerne kommen von links; die den ersten Hügel überwinden, sind in der Mulde gefangen und pendeln zwischen den Toren, bis sie in die eine oder andere Richtung hinausgehen. Die Wahrscheinlichkeiten kombinieren sich wie in Reihe geschaltete Widerstände, also entscheidet vor allem der schwierigere Hügel.</p>
  <div class="ctl"><label for="fis-b">Höhe des äußeren Hügels</label><input id="fis-b" type="range" data-bind="Bb" min="3.5" max="7.5" step="0.05" value="5.6"><output data-show="Bb" data-fmt="2"></output></div>
  <div class="formula">1/T = 1/T<sub>A</sub> + 1/T<sub>B</sub></div>
  <p>Erhöhe den äußeren Hügel und sieh zu, wie der Fluss zur Spaltung versiegt, egal wie offen das innere Tor ist.</p>
</div>
<div class="step">
  <h3>Multi-Chance-Spaltung</h3>
  <p>Uran-238 absorbiert das Neutron und wird zu Uran-239 mit der Anregung <i>E</i>* (gestrichelte Linie). Spaltet es sich nicht, kann es stattdessen ein Neutron aussenden; die Linie sinkt, und das zurückbleibende, noch heiße Uran-238 versucht es an seiner eigenen Barriere: Spaltung mit <b>zweiter Chance</b>, (n,n′f). Die Stapel sammeln, wie jeder Kern geendet hat.</p>
  <div class="ctl"><label for="fis-en">Neutronenenergie</label><input id="fis-en" type="range" data-bind="En" min="0" max="25" step="0.1" value="7"><output data-show="En" data-fmt="1"></output></div>
  <p>Erhöhe die Energie, und spätere Versuche beginnen zu gelingen; eine dritte Chance öffnet sich nahe 12 MeV. Jede neue Chance zeigt sich als Stufe im gemessenen <b>Spaltquerschnitt</b>, also darin, wie wahrscheinlich sich der Kern spaltet: Der kleine Graph oben rechts zeichnet diese Stufen, mit deiner Energie markiert. Die Engine berechnet, wie oft er sich spaltet, nicht in welche Bruchstücke.</p>
  <div class="aside">Im Code: <code>fission/wkb.py</code> (der Pfad der Deformationsenergie und die WKB-Integrale), <code>fission/barriers.py</code> (Hill–Wheeler, Übergangszustände, die Niveaudichte auf der Barriere), <code>fission/transmission.py</code> (Höcker in Reihe, T<sub>fis</sub> pro Spin und Parität), <code>fission/chain.py</code> (Barrieren für jeden Kern der Kaskade).</div>
</div>`,
};
Object.assign(WT.L.labels, {
  // drop
  "surface tension pulls it round": "Oberflächenspannung zieht ihn rund",
  "the protons push it apart": "die Protonen drücken ihn auseinander",
  "a charged drop, nearly round": "ein geladener Tropfen, fast rund",
  "stretched: more surface, charge further apart": "gestreckt: mehr Oberfläche, Ladung weiter verteilt",
  "a neck forms": "ein Hals bildet sich",
  "two fragments, carrying about {#} MeV": "zwei Bruchstücke mit etwa {#} MeV",
  "energy of the drop": "Energie des Tropfens",
  // landscape
  "ground state": "Grundzustand", "inner barrier": "innere Barriere", "second well": "zweite Mulde",
  "outer barrier": "äußere Barriere", "split (scission)": "gespalten (Szission)", "one smooth hill": "ein glatter Hügel",
  "shell effects carving the second well": "Schaleneffekte graben die zweite Mulde",
  "round → stretched → necked → split": "rund → gestreckt → eingeschnürt → gespalten",
  "stretch (deformation) →": "Streckung (Deformation) →",
  // tunnel
  "forbidden zone": "verbotene Zone",
  "excitation {#} MeV": "Anregung {#} MeV",
  "hilltop {#} MeV": "Gipfel {#} MeV",
  "parabola fit": "Parabelanpassung",
  "passes over the top": "geht über den Gipfel",
  // gates
  "continuum: a density": "Kontinuum: eine Dichte",
  "continuum of gates: counted as a density": "Kontinuum der Tore: als Dichte gezählt",
  "gates: transition states": "Tore: Übergangszustände",
  "E = {#} MeV": "E = {#} MeV",
  "all gates: total opening {#}": "alle Tore: Gesamtöffnung {#}",
  "all gates: total opening {#} + {#} from the continuum": "alle Tore: Gesamtöffnung {#} + {#} aus dem Kontinuum",
  "{#}⁺ gates only: total opening {#}": "nur {#}⁺-Tore: Gesamtöffnung {#}",
  "{#}⁺ gates only: total opening {#} + {#} from the continuum": "nur {#}⁺-Tore: Gesamtöffnung {#} + {#} aus dem Kontinuum",
  "{#}⁻ gates only: total opening {#}": "nur {#}⁻-Tore: Gesamtöffnung {#}",
  "{#}⁻ gates only: total opening {#} + {#} from the continuum": "nur {#}⁻-Tore: Gesamtöffnung {#} + {#} aus dem Kontinuum",
  // series
  "nuclei arriving →": "ankommende Kerne →",
  "trapped in the well": "in der Mulde gefangen",
  "fission": "Spaltung",
  "so far: {#} through, {#} turned back": "bisher: {#} durch, {#} umgekehrt",
  // chance
  "²³⁹U*  E* = {#} MeV": "²³⁹U*  E* = {#} MeV", "²³⁸U*  E* = {#} MeV": "²³⁸U*  E* = {#} MeV", "²³⁷U*  E* = {#} MeV": "²³⁷U*  E* = {#} MeV",
  "↑ E* above the picture": "↑ E* oberhalb des Bildes",
  "fission!": "Spaltung!",
  "emits a neutron, cools, tries again": "sendet ein Neutron aus, kühlt ab, versucht es erneut",
  "too cool to split: a photon, no fission": "zu kühl zum Spalten: ein Photon, keine Spaltung",
  "attempt {#}: barrier {#} % open": "Versuch {#}: Barriere {#} % offen",
  "{#}st chance (n,f)": "{#}. Chance (n,f)", "{#}nd chance (n,n′f)": "{#}. Chance (n,n′f)", "{#}rd chance (n,{#}nf)": "{#}. Chance (n,{#}nf)",
  "{#}st (n,f)": "{#}. (n,f)", "{#}nd (n,n′f)": "{#}. (n,n′f)", "{#}rd (n,{#}nf)": "{#}. (n,{#}nf)",
  "no fission": "keine Spaltung",
});
// labels carrying a transmission T, printed either as 0.12 or as 3.4·10⁻5 (two number shapes)
(function () {
  const L = WT.L.labels, F = ["{#}", "{#}·{#}⁻{#}"];
  for (const a of F) {
    L[`inner gate T ≈ ${a}`] = `inneres Tor T ≈ ${a}`;
    L[`outer gate T ≈ ${a}`] = `äußeres Tor T ≈ ${a}`;
    L[`both hills: T ≈ ${a}, {#} % of what arrives gets through`] = `beide Hügel: T ≈ ${a}, {#} % des Ankommenden kommen durch`;
    for (const b of F) {
      L[`T ≈ ${a} real shape · ${b} parabola`] = `T ≈ ${a} echte Form · ${b} Parabel`;
      L[`chance to tunnel T ≈ ${a} on the real shape, ${b} on the parabola`] = `Tunnelwahrscheinlichkeit T ≈ ${a} bei echter Form, ${b} bei der Parabel`;
    }
  }
})();

Object.assign(WT.L.labels, {
  "chance to split vs neutron energy": "Spaltwahrscheinlichkeit über Neutronenenergie",
  "{#}nd": "{#}.",
  "{#}rd": "{#}.",
});
