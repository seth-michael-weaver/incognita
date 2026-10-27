/* German (Deutsch): preeq (Kapitel 7, Präequilibrium) */
WT.L.ch.preeq = {
  num: "Kapitel 7", title: "Stöße vor der Ruhe", short: "Präequilibrium",
  lead: "Ein Neutron, das in einen Kern eindringt, teilt seine Energie nicht sofort mit allen. In den ersten Stößen trägt ein einzelnes Teilchen den Großteil davon, und dieses Teilchen kann direkt wieder hinausfliegen. Das ist das Präequilibrium: Emission, „bevor sich die Energie ausgleicht“.",
  html: `
<div class="step">
  <p>Zwei Töpfe, einer für <em class="p">Protonen</em> und einer für <em class="n">Neutronen</em>. Jede Kugel ist ein Nukleon auf einem Energieniveau, gezeichnet als Sprosse; die Sprossen sind von unten bis zur <b>Fermi-Kante</b> gefüllt. Ein Nukleon über der gestrichelten Linie „frei“ hat genug Energie, um zu entkommen. Die Engine verfolgt Protonen und Neutronen getrennt.</p>
  <p>Das einlaufende Neutron schwebt darüber und trägt die ganze Energie: seine eigene plus einige MeV (Millionen Elektronenvolt), die bei seinem Einfang frei werden.</p>
</div>
<div class="step">
  <h3>Paare anheben</h3>
  <p>Jeder Stoß hebt ein Nukleon auf eine leere Sprosse und hinterlässt ein <b>Loch</b> (einen offenen Ring). Teilchen über der Kante und Löcher darunter heißen beide <b>Exzitonen</b>. Der erste Stoß erzeugt 2 Teilchen und 1 Loch (n = 3); jeder weitere fügt ein Paar hinzu.</p>
  <div class="btns"><button class="btn" data-act="collide">Stoßen</button><button class="btn ghost" data-act="reset">Neu beginnen</button></div>
  <p>Drück ein paarmal auf Stoßen. Das angehobene Nukleon kann ein Proton oder ein Neutron sein, und die Engine zählt jede Sorte. Mit jedem Paar wird die Energie auf mehr Beteiligte verteilt, also sitzt das oberste Teilchen tiefer.</p>
</div>
<div class="step">
  <h3>Die Weggabelung auf jeder Stufe</h3>
  <p>Auf jeder Stufe entkommt das oberste Neutron entweder (Pfeil nach oben, nur wenn es über der Linie „frei“ liegt) oder stößt erneut (Pfeil nach unten); die Dicke zeigt die Wahrscheinlichkeit. Die Emissionsrate folgt aus dem <b>detaillierten Gleichgewicht</b>: aus der Wahrscheinlichkeit des umgekehrten Prozesses, der Absorption desselben Teilchens, die Kapitel 5 berechnet. Die Stoßrate ist die Stärke eines einzelnen Nukleon-Nukleon-Stoßes mal die Zahl der neuen Anordnungen, die er erreichen kann.</p>
  <div class="ctl"><label for="pe-n">Stufe (Exzitonen n)</label><input id="pe-n" type="range" data-bind="n" min="3" max="11" step="2" value="3" data-instant><output data-show="n" data-fmt="0"></output></div>
  <p>Zieh die Stufe nach oben. Am Anfang trägt ein Teilchen den Großteil der Energie, also ist das, was entkommt, schnell. Später ist die Energie dünn verteilt, und kaum etwas kommt heraus.</p>
</div>
<div class="step">
  <h3>Woher der schnelle Ausläufer kommt</h3>
  <p>Der Stapel rechts ist das <b>Spektrum</b>: wie viele Neutronen bei jeder Energie herauskommen, langsame links, schnelle rechts. Jede Reaktion durchläuft die Kette, bis das oberste Neutron entkommt, und seine Farbe sagt, wann: <em style="font-style:normal;color:var(--warm);font-weight:600">tiefes Orange</em> auf Stufe 3, später blasser, <em class="n">Blau</em>, wenn es erst herauskam, nachdem sich der Kern beruhigt hatte (Kapitel 8).</p>
  <div class="btns"><button class="btn" data-act="run">300 Reaktionen ablaufen lassen</button></div>
  <p>Stufe 3 baut ein breites, fast flaches Plateau auf, das bis zur Maximalenergie reicht. Spätere Stufen häufen sich tiefer an. Der blaue Buckel ist die <b>Verdampfung</b>: Sobald alle die Energie teilen, sickern nur noch langsame Neutronen heraus, wie Dampf aus einer heißen Flüssigkeit.</p>
  <div class="ctl"><label for="pe-e">Neutronenenergie</label><input id="pe-e" type="range" data-bind="E" min="5" max="60" step="0.5" value="20"><output data-show="E" data-fmt="1"></output></div>
  <p>Ändere die Energie des einlaufenden Neutrons: Ein neuer Durchgang läuft, und das Plateau reicht weiter. Verdampfung allein erzeugt nie schnelle Neutronen.</p>
</div>
<div class="step">
  <h3>Anordnungen zählen</h3>
  <p>Der Zähler geht jede Möglichkeit durch, Teilchen auf leere Sprossen und Löcher in besetzte Sprossen zu setzen, sodass ihre Energien zusammen die zu verteilende Energie ergeben (die Sprossen liegen hier 1 MeV auseinander). Nukleonen sind Fermionen: Keine zwei teilen sich eine Sprosse, also muss ein Teilchen auf einer leeren Sprosse landen, und ein Loch entsteht nur dort, wo ein Nukleon war. Das ist die <b>Pauli-Blockade</b>.</p>
  <div class="ctl"><label for="pe-u">Zu verteilende Energie (MeV)</label><input id="pe-u" type="range" data-bind="U" min="2" max="16" step="1" value="8" data-instant><output data-show="U" data-fmt="0"></output></div>
  <div class="btns"><button class="btn" data-act="addpair">Paar hinzufügen</button><button class="btn ghost" data-act="droppair">Paar entfernen</button></div>
  <p>Füge ein Paar hinzu, und die Zahl springt; erhöhe die Energie, und sie wächst ungefähr wie <i>E</i><sup>n−1</sup>. Diese Zahl, die <b>Teilchen-Loch-Zustandsdichte</b>, bestimmt die Stoßrate: mehr Anordnungen, mehr Ziele, zu denen ein Stoß führen kann. Die Engine zählt auf der echten Leiter, deren Sprossen Bruchteile eines MeV auseinanderliegen, und fügt eine Grenze hinzu, die du bei hoher Energie siehst: Ein Loch kann nicht unter dem Boden des Topfs liegen.</p>
</div>
<div class="step">
  <h3>Auch Cluster gehen</h3>
  <p>Auch kleine Cluster können früh hinausgehen. Beim <b>Pickup</b> schnappt sich ein Proton auf dem Weg nach draußen ein Neutron an der Oberfläche und verlässt den Kern mit ihm als <em class="n">Deuteron</em>; schnappt es sich zwei, ergibt das ein Triton oder Helium-3. Beim <b>Knockout</b> trifft das einlaufende Neutron ein <em class="a">Alphateilchen</em> (zwei Protonen und zwei Neutronen), das sich schon nahe der Oberfläche gebildet hat, und schlägt es heraus. Die Engine verwendet für beides die Formeln von Kalbach.</p>
  <div class="btns"><button class="btn ghost" data-act="pickup">Ein Neutron aufschnappen → d</button><button class="btn ghost" data-act="knock">Ein α herausschlagen</button></div>
  <p>Drück einen Knopf, um eines zu beobachten. Beide geben Deuteronen und Alphateilchen eigene schnelle Ausläufer, die knapp oberhalb der Energie beginnen, die das Herausziehen jedes einzelnen kostet.</p>
</div>
<div class="step">
  <h3>Ein zweites schnelles Teilchen</h3>
  <p>Bei hoher Energie kann ein zweites angehobenes Nukleon noch über der Linie „frei“ sitzen, wenn das erste Neutron geht, und ebenfalls entkommen, als schnelles Neutron oder Proton. Die Töpfe spielen eine Reaktion nach der anderen ab, mit gestauchter Energieskala.</p>
  <div class="ctl"><label for="pe-e2">Neutronenenergie</label><input id="pe-e2" type="range" data-bind="E" min="5" max="80" step="0.5" value="40"><output data-show="E" data-fmt="1"></output></div>
  <p>Ändere die Energie. Unterhalb von etwa 20 MeV schafft das zweite Nukleon die Linie selten; darüber geben immer mehr Reaktionen zwei schnelle Teilchen ab. Das ist das <b>mehrfache Präequilibrium</b>, das die Engine ab 20 MeV einbezieht. Was nicht hinausgegangen ist, wird zum Compoundkern des nächsten Kapitels. Unterhalb einiger MeV (des höchsten verwendeten diskreten Niveaus des Targets) überspringt die Engine die Kette ganz.</p>
  <div class="aside">Im Code: <code>preeq/exciton.py</code> (Zweikomponenten-Exzitonenkette, Stoß- und Emissionsraten), <code>density/particle_hole.py</code> (Teilchen-Loch-Zustandsdichten mit Pauli-Korrektur und Korrektur für den endlichen Topf), <code>preeq/complex.py</code> (Pickup, Stripping und α-Knockout nach Kalbach), <code>preeq/multi.py</code> (mehrfaches Präequilibrium), <code>compound/normalization.py</code> (Übergabe an den Compoundkern).</div>
</div>`,
};
Object.assign(WT.L.labels, {
  // wells
  "protons": "Protonen",
  "neutrons": "Neutronen",
  "Fermi": "Fermi",
  "Fermi surface": "Fermi-Kante",
  "free": "frei",
  "free: can escape": "frei: kann entkommen",
  "all the energy in one nucleon": "die ganze Energie in einem Nukleon",
  "{#} particle, {#} holes": "{#} Teilchen, {#} Löcher",
  // pairs
  "{#} particle, {#} holes: n = {#}": "{#} Teilchen, {#} Löcher: n = {#}",
  "{#} particle, {#} hole: n = {#}": "{#} Teilchen, {#} Loch: n = {#}",
  "{#} particles, {#} hole: n = {#}": "{#} Teilchen, {#} Loch: n = {#}",
  "{#} particles, {#} holes: n = {#}": "{#} Teilchen, {#} Löcher: n = {#}",
  "protons: {#} lifted, {#} hole": "Protonen: {#} angehoben, {#} Loch",
  "protons: {#} lifted, {#} holes": "Protonen: {#} angehoben, {#} Löcher",
  "neutrons: {#} lifted, {#} hole": "Neutronen: {#} angehoben, {#} Loch",
  "neutrons: {#} lifted, {#} holes": "Neutronen: {#} angehoben, {#} Löcher",
  "chain ends: the rest becomes a compound nucleus": "Kette endet: der Rest wird ein Compoundkern",
  // fork
  "about {#} MeV above surface": "etwa {#} MeV über der Kante",
  "escapes  {#}%": "entkommt  {#} %",
  "collides again  {#}%": "stößt erneut  {#} %",
  "below the free line: it cannot leave": "unter der Linie „frei“: kann nicht hinaus",
  "n = {#}: {#} particles, {#} hole, {#} MeV": "n = {#}: {#} Teilchen, {#} Loch, {#} MeV",
  "n = {#}: {#} particles, {#} holes, {#} MeV": "n = {#}: {#} Teilchen, {#} Löcher, {#} MeV",
  "stage n = {#}: {#} particles and {#} hole share {#} MeV": "Stufe n = {#}: {#} Teilchen und {#} Loch teilen {#} MeV",
  "stage n = {#}: {#} particles and {#} holes share {#} MeV": "Stufe n = {#}: {#} Teilchen und {#} Löcher teilen {#} MeV",
  // tail
  "max {#} MeV": "max. {#} MeV",
  "slow": "langsam",
  "fast →": "schnell →",
  "stage {#}": "Stufe {#}",
  "chain over: compound": "Kette vorbei: Compound",
  "left at:": "hinaus bei:",
  "neutron left at:": "Neutron hinaus bei:",
  "evaporation": "Verdampfung",
  "{#} of {#} landed · {#} left during the chain": "{#} von {#} gelandet · {#} während der Kette hinaus",
  // pauli
  "well bottom: no deeper hole": "Topfboden: kein tieferes Loch",
  "bottom of the well": "Boden des Topfs",
  "{#} MeV to share": "{#} MeV zu verteilen",
  "{#} particles · {#} hole": "{#} Teilchen · {#} Loch",
  "{#} particles · {#} holes": "{#} Teilchen · {#} Löcher",
  "ways, all counted": "Möglichkeiten, alle gezählt",
  "arrangements so far": "Anordnungen bisher",
  "one more pair: {#} ways": "ein Paar mehr: {#} Möglichkeiten",
  "never two on one rung · holes only where a nucleon was": "nie zwei auf einer Sprosse · Löcher nur, wo ein Nukleon war",
  "(first {#} shown as ticks)": "(die ersten {#} als Striche)",
  // cluster
  "a deuteron leaves": "ein Deuteron geht",
  "grabs a neutron at the edge": "schnappt sich ein Neutron am Rand",
  "a fast proton heads out": "ein schnelles Proton fliegt hinaus",
  "an α ({#} protons + {#} neutrons) waits at the edge": "ein α ({#} Protonen + {#} Neutronen) wartet am Rand",
  "knocked straight out": "direkt herausgeschlagen",
  // second
  "first fast neutron": "erstes schnelles Neutron",
  "second fast proton": "zweites schnelles Proton",
  "second fast neutron": "zweites schnelles Neutron",
  "below the free line: stays": "unter der Linie „frei“: bleibt",
  "below the free line: it stays": "unter der Linie „frei“: es bleibt",
  "the rest settles: compound nucleus": "der Rest beruhigt sich: Compoundkern",
  "{#} MeV carried in": "{#} MeV hineingetragen",
  "second fast particle in {#} of the last {#} reactions": "zweites schnelles Teilchen in {#} der letzten {#} Reaktionen",
});
