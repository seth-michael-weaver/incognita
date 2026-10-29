/* German (Deutsch): measure (Kapitel 17, Observablen) */
WT.L.ch.measure = {
  num: "Kapitel 17", title: "Observablen", short: "Observablen",
  lead: "Ein Experiment, ein Reaktor oder ein Stern sieht nur eine Handvoll Zahlen. Dieses Kapitel zeigt, wie die Engine das, was im Kern geschieht, in diese Zahlen übersetzt.",
  html: `
<div class="step">
  <p>Die blasse Scheibe um jeden Kern ist sein <b>Wirkungsquerschnitt</b>: die Fläche, die ein Neutron treffen muss, damit eine Reaktion stattfindet, nicht die tatsächliche Größe des Kerns. Ein Strahl kommt von links durch eine dünne Folie aus Kernen; der Anteil, der reagiert, ist diese Fläche mal der Zahl der Kerne, die er trifft. Die Einheit ist das Barn (10⁻²⁴ cm², etwa die Querschnittsfläche eines Urankerns).</p>
  <div class="ctl"><label for="mea-e">Neutronenenergie (MeV)</label><input id="mea-e" type="range" data-bind="E" min="0.1" max="20" step="0.1" value="2"><output data-show="E" data-fmt="1"></output></div>
  <p>Senke die Energie, und die Scheiben schwellen an: Ein langsames Neutron ist eine breite Welle und reagiert aus größerer Entfernung. Bei hoher Energie schrumpft die Scheibe auf den Kern selbst zu.</p>
</div>
<div class="step">
  <h3>Anregungsfunktionen</h3>
  <p>Jede Tür ist ein Ausgang, ein <b>Kanal</b>: Das Neutron prallt ab (elastisch), lässt das Target angeregt zurück (n′), schlägt weitere Neutronen heraus (2n, 3n), wird eingefangen, wobei nur Photonen hinausgehen (γ), oder stattdessen geht ein Proton oder ein α-Teilchen. Eine Tür mit Vorhängeschloss hat eine <b>Schwelle</b>: Die Reaktion kostet mehr Energie, als das Neutron mitbringt.</p>
  <div class="ctl"><label for="mea-e2">Neutronenenergie (MeV)</label><input id="mea-e2" type="range" data-bind="E" min="0.1" max="20" step="0.1" value="2"><output data-show="E" data-fmt="1"></output></div>
  <p>Zieh die Energie über eine Schwelle, und diese Tür springt auf; die Eimer füllen sich bis zum Anteil jedes Kanals, und jede neue Tür nimmt den anderen Anteile ab. Die Schwellen ergeben sich aus den Massen der Kerne; die Anteile aus dem Wettbewerb aus Kapitel 9.</p>
</div>
<div class="step">
  <h3>Emissionsspektren</h3>
  <p>Die beiden Stapel sind die Neutronen, die die vordere und die hintere Hälfte eines Detektorrings erreichen, sortiert nach Energie. Der Strahl ist gepulst, also gibt die Flugzeit jedes Neutrons seine Energie an: Schnelle kommen zuerst an.</p>
  <div class="ctl"><label for="mea-ein">Einfallsenergie (MeV)</label><input id="mea-ein" type="range" data-bind="Ein" min="5" max="60" step="0.5" value="30"><output data-show="Ein" data-fmt="0"></output></div>
  <p>Beide Stapel haben einen Buckel aus langsamen, <b>verdampften</b> Neutronen: Sie verdampfen aus dem Compoundkern, sobald die Energie verteilt ist, in alle Richtungen gleich. Nur der vordere Stapel hat einen langen schnellen Ausläufer: Neutronen aus dem <b>Präequilibrium</b>, die bei den ersten Stößen hinausgehen und sich noch ungefähr mit dem Strahl bewegen. Erhöhe die Einfallsenergie, und der Ausläufer wächst.</p>
</div>
<div class="step">
  <h3>Winkelverteilungen</h3>
  <p>Das Blütenblatt zeigt, wie viele Neutronen in jede Richtung hinausgehen; der Strahl kommt von links. Verdampfte Neutronen haben den Strahl vergessen und gehen in alle Richtungen gleich; schnelle aus dem Präequilibrium neigen sich nach vorn. Die Regel von Kalbach legt fest, wie stark, mit einer einzigen Steigung <i>a</i>, die mit der Austrittsenergie wächst. Die Engine kann diese Winkelverteilungen als optionale Ausgabe ebenfalls herausschreiben.</p>
  <div class="ctl"><label for="mea-eo">Austrittsenergie (MeV)</label><input id="mea-eo" type="range" data-bind="Eout" min="1" max="45" step="0.5" value="25"><output data-show="Eout" data-fmt="1"></output></div>
  <p>Senke die Austrittsenergie, und das Blütenblatt wird runder: Langsame Neutronen sind überwiegend verdampft.</p>
  <div class="formula">dσ/dΩ ∝ e<sup>a cos θ</sup></div>
</div>
<div class="step">
  <h3>Maxwell-gemittelte Wirkungsquerschnitte</h3>
  <p>Der Stapel unten sammelt die Energien von Neutronen, die im heißen Gas eines Sterns eingefangen werden. Ihre Geschwindigkeiten folgen einer Maxwell-Verteilung, die durch die Temperatur <i>kT</i> bestimmt ist (30 keV sind etwa 350 Millionen Grad); längere Spuren bedeuten schnellere Neutronen, und jeder Vorbeiflug an einem Kern kann mit einem Einfangblitz enden.</p>
  <div class="ctl"><label for="mea-kt">Temperatur kT (keV)</label><input id="mea-kt" type="range" data-bind="kT" min="5" max="100" step="1" value="30"><output data-show="kT" data-fmt="0"></output></div>
  <p>Langsame Neutronen sind leicht zu fangen, kommen aber selten vorbei, und schnelle gibt es wenige, also stammen die meisten Einfänge aus einem Fenster von einigen <i>kT</i> Breite. Die Rate über das ganze Gas ist der <b>Maxwell-gemittelte Wirkungsquerschnitt</b> (MACS), in Millibarn (mb). Heiz das Gas auf, und das Fenster rutscht zu höherer Energie, wo das Ziel kleiner ist. Der MACS wird aus der Einfangkurve der Engine gefaltet.</p>
</div>
<div class="step">
  <h3>Thermisch angeregte Targets</h3>
  <p>Die Kugeln zeigen, welcher Anteil der Targetkerne bei dieser Temperatur auf jedem seiner tiefsten Niveaus sitzt. In einem Stern sind manche Targets bereits angeregt, und jedes angeregte Niveau ist ein anderer Eingang zum selben Compoundkern. Ein Niveau mit Spin <i>J</i> nimmt mehr auf, weil es 2<i>J</i>+1 Orientierungen hat.</p>
  <div class="ctl"><label for="mea-kt2">Temperatur kT (keV)</label><input id="mea-kt2" type="range" data-bind="kT" min="5" max="100" step="1" value="30"><output data-show="kT" data-fmt="0"></output></div>
  <p>Erhöhe die Temperatur und sieh zu, wie Kerne nach oben wandern. Eine stellare Rate berechnet den Einfang aus jedem besetzten Niveau und addiert die Ergebnisse mit diesen Anteilen; die Gewichte summieren sich zur Zustandssumme <i>G</i>, und das Verhältnis zur Rate aus dem Grundzustand ist der <b>stellare Verstärkungsfaktor</b>. Die Engine kann das als Option, standardmäßig aus; normalerweise startet jedes Target im Grundzustand.</p>
</div>
<div class="step">
  <h3>Unsicherheiten und Kovarianzen</h3>
  <p>Jede blasse Scheibe ist ein Lauf der Engine mit zufällig verschobenen Eingaben: die Tiefe des optischen Topfs, die Niveaudichte und die Photonenstärke, jede nur auf einige Prozent genau bekannt. Die Streuung vieler Läufe ist eine ehrliche Unsicherheit: <b>Total Monte Carlo</b>.</p>
  <div class="btns"><button class="btn" data-act="tmc1">Eine Variante rechnen</button><button class="btn ghost" data-act="tmc">10 rechnen</button><button class="btn ghost" data-act="clear">Leeren</button></div>
  <p>Ein scharfer Rand bedeutet, dass die Eingaben die Antwort festlegen; ein verschwommener Rand bedeutet, dass sie es nicht tun, und genau dort würden neue Messungen am meisten helfen.</p>
  <div class="aside">Im Code: <code>emission/channels.py</code> (exklusive Kanäle und Restkerne), <code>specout.py</code> und <code>specang.py</code> (Austrittsspektren, Winkelverteilungen und doppelt differentielle Wirkungsquerschnitte, nur auf Anforderung geschrieben), <code>astro/stellar.py</code> (Einfang aus thermisch besetzten Targetniveaus, optional), <code>tmc.py</code> (der Total-Monte-Carlo-Sampler). MACS für den Grundzustand werden aus den Einfangkurven in <code>validation/differential/core.py</code> gefaltet.</div>
</div>`,
};
Object.assign(WT.L.labels, {
  // area
  "each disc: σ ≈ {#} b": "jede Scheibe: σ ≈ {#} b",
  "each disc: cross section σ ≈ {#} b, the area a neutron must hit": "jede Scheibe: Wirkungsquerschnitt σ ≈ {#} b, die Fläche, die ein Neutron treffen muss",
  "beam →": "Strahl →",
  "nucleus's own face ≈ {#} b · {#} % reacts": "Fläche des Kerns ≈ {#} b · {#} % reagieren",
  "the nucleus's own face ≈ {#} b · {#} % of the beam reacts in this foil": "Fläche des Kerns selbst ≈ {#} b · {#} % des Strahls reagieren in dieser Folie",
  "slow: the neutron's wave reaches well past the surface": "langsam: die Welle des Neutrons reicht weit über die Oberfläche",
  "the target still looks bigger than the nucleus": "das Ziel wirkt noch größer als der Kern",
  "fast: close to the nucleus's own size": "schnell: nahe der Größe des Kerns selbst",
  // doors
  "elastic": "elastisch", "n′ inelastic": "n′ inelastisch", "{#}n": "{#}n", "γ capture": "γ-Einfang", "p": "p", "α": "α", "n′": "n′",
  "{#}n · {#} MeV": "{#}n · {#} MeV", "p · {#} MeV": "p · {#} MeV", "α · {#} MeV": "α · {#} MeV", "n′ inelastic · {#} MeV": "n′ inelastisch · {#} MeV",
  "opens at {#} MeV": "öffnet bei {#} MeV",
  "{#} MeV": "{#} MeV",
  // detect
  "forward half": "vordere Hälfte", "backward half": "hintere Hälfte",
  "pulsed beam": "gepulster Strahl", "pulsed beam →": "gepulster Strahl →",
  "backward": "rückwärts", "backward detectors": "Rückwärtsdetektoren",
  "forward": "vorwärts", "forward detectors": "Vorwärtsdetektoren",
  "outgoing neutron energy from the flight time (MeV) →": "Austrittsenergie der Neutronen aus der Flugzeit (MeV) →",
  "fast tail": "schneller Ausläufer", "fast tail: pre-equilibrium": "schneller Ausläufer: Präequilibrium",
  "evaporated hump": "Verdampfungsbuckel", "hump: evaporated, every way alike": "Buckel: verdampft, in alle Richtungen gleich",
  "{#} % leave before the energy is shared": "{#} % gehen, bevor die Energie verteilt ist",
  // angle
  "beam": "Strahl",
  "forward-to-backward ratio ≈ {#}  ·  slope a ≈ {#}": "Vorwärts/Rückwärts-Verhältnis ≈ {#}  ·  Steigung a ≈ {#}",
  "mostly evaporated: every direction alike": "überwiegend verdampft: alle Richtungen gleich",
  "a mix: the fast share leans forward": "eine Mischung: der schnelle Anteil neigt sich nach vorn",
  "mostly pre-equilibrium: strongly forward": "überwiegend Präequilibrium: stark nach vorn",
  "forward →": "vorwärts →",
  // star
  "{#} keV": "{#} keV",
  "kT = {#} keV": "kT = {#} keV",
  "energies of captured neutrons": "Energien der eingefangenen Neutronen",
  "each capture drops here, by the neutron's energy: the window that counts": "jeder Einfang fällt hier hin, nach Neutronenenergie: das Fenster, das zählt",
  "MACS ≈ {#} mb at kT = {#} keV · captures watched: {#}": "MACS ≈ {#} mb bei kT = {#} keV · beobachtete Einfänge: {#}",
  // hot target
  "{#}⁺  ground state": "{#}⁺  Grundzustand", "{#}⁺  {#} keV": "{#}⁺  {#} keV",
  "target levels, with the share of nuclei sitting on each": "Targetniveaus, mit dem Anteil der Kerne auf jedem",
  "{#} % start from the ground state · partition function G ≈ {#}": "{#} % starten im Grundzustand · Zustandssumme G ≈ {#}",
  // TMC
  "optical well": "optischer Topf", "optical well depth": "Tiefe des optischen Topfs",
  "level density": "Niveaudichte", "photon strength": "Photonenstärke",
  "σ ≈ {#} b ": "σ ≈ {#} b ", "σ ≈ {#} mb ": "σ ≈ {#} mb ",
  "σ ≈ {#} b ±{#} %": "σ ≈ {#} b ±{#} %", "σ ≈ {#} mb ±{#} %": "σ ≈ {#} mb ±{#} %",
  "dashed: best inputs · each disc drawn at its own scale": "gestrichelt: beste Eingaben · jede Scheibe im eigenen Maßstab",
  "dashed ring: the best-value inputs · each energy drawn at its own scale (disc area ∝ σ)": "gestrichelter Ring: Eingaben mit Bestwerten · jede Energie im eigenen Maßstab (Scheibenfläche ∝ σ)",
  "{#} runs of the engine, each with its inputs nudged at random": "{#} Läufe der Engine, jeder mit zufällig verschobenen Eingaben",
});
