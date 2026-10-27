/* German (Deutsch): decay (Kapitel 9, einen Ausgang wählen) */
WT.L.ch.decay = {
  num: "Kapitel 9", title: "Einen Ausgang wählen", short: "Zerfall",
  lead: "Der Compoundkern muss seine Energie loswerden, indem er ein Teilchen oder ein Photon aussendet. Dieses Kapitel zeichnet jeden Ausweg als Tür. Die Aufgabe der Engine ist es, anzugeben, welcher Anteil des Flusses (des Stroms der hier ankommenden Reaktionen) durch jede Tür hinausgeht.",
  html: `
<div class="step">
  <p>Eine Tür pro Ausgang: ein <em class="g">Photon</em> (γ), ein <em class="n">Neutron</em> (n), ein <em class="p">Proton</em> (p), ein <em class="a">Alphateilchen</em> (α: zwei Protonen und zwei Neutronen) und, nur bei schweren Kernen, die <em class="f">Spaltung</em> (Teilung in zwei). Der helle Spalt in jeder Tür ist der Anteil dieses Ausgangs, und die Kugeln strömen mit denselben Raten hinaus; graue Türen sind zu. Da der Kern vergessen hat, wie er entstanden ist, nutzt er jede Tür b im Verhältnis zu einem Gewicht:</p>
  <div class="formula">Anteil<sub>b</sub> = T<sub>b</sub> · ρ<sub>b</sub> / Σ<sub>c</sub> T<sub>c</sub> · ρ<sub>c</sub></div>
  <p>Der <b>Transmissionskoeffizient</b> <i>T</i> ist die Wahrscheinlichkeit, dass ein Teilchen, das den Rand erreicht, hindurchkommt; für Teilchen stammt er aus dem optischen Modell aus Kapitel 5, rückwärts angewandt. Die <b>Niveaudichte</b> ρ, neben jeder Tür notiert, zählt die Zustände, in denen der zurückbleibende Kern landen kann. Die Aufteilung nach <i>T</i> mal ρ ist die <b>Hauser–Feshbach</b>-Regel. Bei 10 MeV nimmt die Neutronentür fast alles.</p>
</div>
<div class="step">
  <h3>Warum die meisten Teilchen langsam herauskommen</h3>
  <p>Die Neutronentür, aufgeteilt nach der Austrittsenergie ε (langsam links, schnell rechts). Der Spalt <i>T</i>(ε) jeder Tür wird für schnellere Neutronen breiter. Darunter liegt das Gedränge der Zustände, in denen der zurückbleibende Kern sein kann: Ein langsames Neutron lässt den Großteil der Energie zurück, wo es Zustände in Hülle und Fülle gibt, also schrumpft das Gedränge nach rechts.</p>
  <div class="ctl"><label for="dc-sp">Verfügbare Energie</label><input id="dc-sp" type="range" data-bind="spare" min="1" max="12" step="0.5" value="5"><output data-show="spare" data-fmt="1"></output></div>
  <p>Tür × Gedränge macht den Stapel zu einem Buckel, dem <b>Verdampfungsspektrum</b>, wie Dampf, der aus einer heißen Flüssigkeit entweicht. Ändere die verfügbare Energie (in MeV, Millionen Elektronenvolt): Der Stapel beginnt neu, und sein Maximum bleibt nahe 1 MeV, festgelegt durch die Kerntemperatur. Zusätzliche Energie macht vor allem den zurückbleibenden Kern heißer.</p>
</div>
<div class="step">
  <h3>Geladene Teilchen müssen klettern</h3>
  <p>Die Energie eines Protons in jedem Abstand r vom Zentrum: innen ein Topf, außen ein Hügel aus der elektrischen (Coulomb-)Abstoßung, der wie 1/r abfällt. Unterhalb der Hügelspitze kann das Proton, das im Topf hin- und herrasselt, nur durch den schattierten Abschnitt <b>tunneln</b>, ein Quanteneffekt, der bei vielen Stößen gegen die Wand einmal gelingt.</p>
  <div class="ctl"><label for="dc-ce">Teilchenenergie</label><input id="dc-ce" type="range" data-bind="eps" min="0.5" max="12" step="0.1" value="3"><output data-show="eps" data-fmt="1"></output></div>
  <div class="btns"><button class="btn ghost" data-act="toggleAlpha">Proton / Alpha wechseln</button></div>
  <p>Senke die Energie und sieh zu, wie der Tunnel breiter wird; wechsle dann zum Alpha, dessen zwei Ladungen vor einem etwa doppelt so hohen Hügel stehen. Deshalb gewinnen ungeladene Neutronen meist, sobald sie hinauskönnen, und deshalb zählen Proton- und Alpha-Ausgänge vor allem bei leichten Kernen und hohen Energien.</p>
</div>
<div class="step">
  <h3>Türen öffnen sich eine nach der anderen</h3>
  <p>Jede Teilchentür öffnet sich erst oberhalb ihrer <b>Separationsenergie</b>, der Kosten, um dieses Teilchen herauszuziehen: hier 8 MeV für ein Neutron, 9 für ein Proton, 7 für ein Alpha. Unterhalb der 8 MeV des Neutrons gibt fast jeder Zerfall Licht ab.</p>
  <div class="ctl"><label for="dc-e">Anregungsenergie</label><input id="dc-e" type="range" data-bind="E" min="5" max="24" step="0.1" value="7"><output data-show="E" data-fmt="1"></output></div>
  <p>Zieh die Anregungsenergie über 8 MeV. Innerhalb von etwa 1 MeV schwingt die Neutronentür weit auf, und der Photonenanteil fällt auf ein Hundertstel. Die Proton- und Alphatüren leuchten später auf und bleiben schmal, gebremst von ihren Coulomb-Hügeln.</p>
</div>
<div class="step">
  <h3>Spin und Parität müssen aufgehen</h3>
  <p>Der Compoundkern (oben) hat den Spin <i>J</i>; die Zustände des zurückbleibenden Kerns liegen darunter in Schubladen nach Spin <i>J</i>′. Das Neutron trägt die Differenz von Spin und Parität fort: Verlässt es den Kern mit Bahndrehimpuls <i>l</i>, ändert es den Spin um bis zu <i>l</i> + ½ und kehrt die Parität um, wenn <i>l</i> ungerade ist. Größeres <i>l</i> bedeutet eine schmalere Tür; die Tür jeder Schublade ist das kleinste <i>l</i>, das sie erreicht. Volle Landungen behalten die Parität; hohle kehren sie um.</p>
  <div class="ctl"><label for="dc-j">Compoundspin J</label><input id="dc-j" type="range" data-bind="J" min="0" max="10" step="1" value="2" data-instant><output id="dc-jout">5/2</output></div>
  <p>Erhöhe <i>J</i>. Die offenen Türen rutschen zu Schubladen mit hohem Spin, die wenige Zustände enthalten, während die vollen Schubladen hinter geschlossenen Türen liegen. Ein Compoundkern mit hohem Spin sendet nur zögerlich Teilchen aus, und das gibt Photonen und Isomeren (langlebigen Zuständen, Kapitel 10) ihre Chance.</p>
</div>
<div class="step">
  <h3>Der Weg, auf dem du hereinkamst</h3>
  <p>Bei niedriger Energie ist der Compoundkern eine Reihe scharfer <b>Resonanzen</b>, Energien, bei denen das Neutron leicht absorbiert wird; acht sind gezeichnet, eine pro Zeile. Jede hat zufällige Türbreiten: den Eingang (den Neutronenkanal) links, Breite <i>x</i>, und die anderen Türen, hier meist Photonen, rechts, Breiten <i>y</i>.</p>
  <div class="btns"><button class="btn" data-act="fire">40 Neutronen abfeuern</button><button class="btn ghost" data-act="reroll">Neue Resonanzen</button></div>
  <p>Ein Neutron tritt mit einer Wahrscheinlichkeit proportional zu <i>x<sub>i</sub></i> in die Resonanz <i>i</i> ein und verlässt sie durch den Eingang mit der Wahrscheinlichkeit <i>x<sub>i</sub></i> / (<i>x<sub>i</sub></i> + Σ<i>y</i>). Zeilen mit breitem Eingang lassen mehr Neutronen herein und schicken mehr wieder hinaus, also übertrifft der wahre Anteil, der zurückkommt (ein <b>Mittelwert von Produkten</b>), die Schätzung aus mittleren Breiten (ein <b>Produkt von Mittelwerten</b>). Das Verhältnis ist die <b>elastische Überhöhung</b>, und die <b>Breitenfluktuationskorrektur</b> verschiebt diesen Fluss von den anderen Türen zum Eingang.</p>
  <div class="ctl"><label for="dc-n">Andere Türen</label><input id="dc-n" type="range" data-bind="Nch" min="1" max="12" step="1" value="2" data-instant><output data-show="Nch" data-fmt="0"></output></div>
  <p>Füge Türen hinzu. Bei vielen Ausgängen schwankt ihre Gesamtbreite nicht mehr, also zählt die Korrektur vor allem dort, wo wenige Türen offen sind. Die Engine wendet sie mit der Formel von Moldauer an, für einfallende Neutronen bis zur Neutronenseparationsenergie des Targets, und lässt sie darüber weg.</p>
</div>
<div class="step">
  <h3>Was zum Verteilen übrig bleibt</h3>
  <p>Nicht jedes absorbierte Neutron bildet einen Compoundkern. Manche treffen einmal streifend und fliegen davon (direkte Reaktionen, Kapitel 6); manche stoßen ein- oder zweimal herum und schießen schnell hinaus (Präequilibrium, Kapitel 7). Nur der Rest bleibt und heizt den Kern auf. Die Zähler verbuchen jedes Schicksal.</p>
  <div class="ctl"><label for="dc-einc">Neutronenenergie</label><input id="dc-einc" type="range" data-bind="Einc" min="1" max="30" step="0.5" value="8"><output data-show="Einc" data-fmt="1"></output></div>
  <p>Nur die, die bleiben, nehmen am Wettbewerb der Türen teil. Ändere die Neutronenenergie: Bei einigen MeV bleiben fast alle; bei 30 MeV ist etwa die Hälfte gegangen, bevor das Gleichgewicht erreicht ist.</p>
  <div class="aside">Im Code: <code>compound/prepare.py</code> (Ausgangsgewichte T·ρ pro Spin und Parität, Auswahlregeln), <code>compound/target.py</code> (erster Zerfall mit Breitenfluktuationen), <code>compound/continuum.py</code> (Zerfall jedes späteren Intervalls), <code>compound/wfc.py</code> (Korrekturen nach Moldauer, HRTW, GOE), <code>compound/normalization.py</code> (für den Compoundkern verbleibender Fluss), <code>omp/inverse.py</code> (Türen rückwärts).</div>
</div>`,
};
(function () {
  const L = {
    "{#} MeV": "{#} MeV",
    "n": "n", "p": "p", "fission": "Spaltung",
    "heavy only": "nur schwere",
    "heavy nuclei only": "nur schwere Kerne",
    "shut below {#} MeV": "zu unter {#} MeV",
    "the neutron door takes nearly everything": "die Neutronentür nimmt fast alles",
    "below the neutron threshold, nearly all decays emit light": "unter der Neutronenschwelle senden fast alle Zerfälle Licht aus",
    "the doors share the decays": "die Türen teilen sich die Zerfälle",
    // hump
    "{#} MeV to spare": "{#} MeV verfügbar",
    "door gap = T(ε)": "Türspalt = T(ε)",
    "doors: one per neutron energy ε, gap = T(ε)": "Türen: eine pro Neutronenenergie ε, Spalt = T(ε)",
    "× states left behind": "× zurückbleibende Zustände",
    "× states the leftover nucleus can be in: many after a slow neutron": "× mögliche Zustände des Restkerns: viele nach einem langsamen Neutron",
    "most ≈ {#} MeV": "Maximum ≈ {#} MeV",
    "= the pile": "= der Stapel",
    "= where the neutrons land: the evaporation spectrum": "= wo die Neutronen landen: das Verdampfungsspektrum",
    "slow": "langsam",
    "slow neutrons": "langsame Neutronen",
    "fast: {#} MeV →": "schnell: {#} MeV →",
    "fast: {#} MeV (beyond, up to {#}, almost none)": "schnell: {#} MeV (darüber, bis {#}, fast keine)",
    "fast: {#}": "schnell: {#}",
    "fast: {#} MeV, the neutron takes it all": "schnell: {#} MeV, das Neutron nimmt alles",
    // coulomb
    "well ↓": "Topf ↓",
    "well (much deeper) ↓": "Topf (viel tiefer) ↓",
    "hilltop ≈ {#} MeV": "Hügelspitze ≈ {#} MeV",
    "falls as {#}/r": "fällt wie {#}/r",
    "Coulomb hill, falling as {#}/r": "Coulomb-Hügel, fällt wie {#}/r",
    "tunnel: wider than the picture": "Tunnel: breiter als das Bild",
    "tunnel {#} fm": "Tunnel {#} fm",
    "proton energy {#} MeV": "Protonenenergie {#} MeV",
    "alpha energy {#} MeV": "Alphaenergie {#} MeV",
    "proton energy {#} MeV ↑": "Protonenenergie {#} MeV ↑",
    "alpha energy {#} MeV ↑": "Alphaenergie {#} MeV ↑",
    "above the hilltop: it rolls straight out": "über der Hügelspitze: rollt direkt hinaus",
    "below the top, must tunnel: nearly every knock gets through": "unter der Spitze, muss tunneln: fast jeder Stoß kommt durch",
    "below the top, must tunnel: about {#} knock in {#} gets through": "unter der Spitze, muss tunneln: etwa {#} Stoß von {#} kommt durch",
    "below the top, must tunnel: about {#} knock in {#} × {#}^{#} gets through": "unter der Spitze, muss tunneln: etwa {#} Stoß von {#} × {#}^{#} kommt durch",
    "out": "draußen",
    "through after {#} knock": "durch nach {#} Stoß",
    "through after {#} knocks": "durch nach {#} Stößen",
    "knocks so far: {#}": "Stöße bisher: {#}",
    "distance r from the centre (fm) →": "Abstand r vom Zentrum (fm) →",
    // spin
    "J = {#}/{#}, parity +": "J = {#}/{#}, Parität +",
    "l={#}": "l={#}",
    "leftover states by spin J′ →": "Restzustände nach Spin J′ →",
    "drawers: states of the leftover nucleus by spin J′ (faint: states it holds) →": "Schubladen: Zustände des Restkerns nach Spin J′ (blass: enthaltene Zustände) →",
    "open doors reach {#} %": "offene Türen erreichen {#} %",
    "open doors reach about {#} % of the states": "offene Türen erreichen etwa {#} % der Zustände",
    "● parity kept (even l)   ○ flipped (odd l)": "● Parität bleibt (gerades l)   ○ umgekehrt (ungerades l)",
    // wfc
    "entrance x": "Eingang x",
    "entrance, width x": "Eingang, Breite x",
    "{#} other doors, y": "{#} andere Türen, y",
    "{#} other door, widths y": "{#} andere Tür, Breiten y",
    "{#} other doors, widths y": "{#} andere Türen, Breiten y",
    "back out the entrance: {#} of {#}": "zurück durch den Eingang: {#} von {#}",
    "out another door: {#}": "durch eine andere Tür: {#}",
    // norm
    "absorbed neutrons, {#} MeV →": "absorbierte Neutronen, {#} MeV →",
    "direct: {#} %": "direkt: {#} %",
    "pre-equilibrium: {#} %": "Präequilibrium: {#} %",
    "compound nucleus: {#} %": "Compoundkern: {#} %",
    "one glancing hit on the surface": "ein Streiftreffer an der Oberfläche",
    "a knock or two, then out fast": "ein, zwei Stöße, dann schnell hinaus",
    "stayed: on to the door competition": "geblieben: weiter zum Wettbewerb der Türen",
  };
  // door hint with level-count wording (fmt: "1", "N", "N thousand", "N million") and T possibly in e-notation
  const cnt = [["{#} state", "{#} Zustand"], ["{#} states", "{#} Zustände"], ["{#} thousand states", "{#} Tausend Zustände"], ["{#} million states", "{#} Millionen Zustände"]];
  for (const [e, s] of cnt) {
    L[`weak door × ≈ ${e}`] = `schwache Tür × ≈ ${s}`;
    L[`T ≈ {#} × ≈ ${e}`] = `T ≈ {#} × ≈ ${s}`;
    L[`T ≈ {#}e{#} × ≈ ${e}`] = `T ≈ {#}e{#} × ≈ ${s}`;
  }
  // share comparisons: each pct is "{#} %" or "≈ {#} %"
  const P = ["{#} %", "≈ {#} %"];
  for (const a of P) for (const b of P) {
    L[`back out ${a}, not ${b}: × {#}`] = `zurück ${a}, nicht ${b}: × {#}`;
    L[`share back out: average of products ${a} · product of averages ${b} · × {#}`] = `zurück: Mittelwert der Produkte ${a} · Produkt der Mittelwerte ${b} · × {#}`;
    L[`other doors ${a}, not ${b}`] = `andere Türen ${a}, nicht ${b}`;
    L[`other doors together: ${a} instead of ${b}`] = `andere Türen zusammen: ${a} statt ${b}`;
  }
  Object.assign(WT.L.labels, L);
})();
