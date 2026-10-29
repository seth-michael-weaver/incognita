/* German (Deutsch): cascade (Kapitel 11, über die Nuklidkarte hinab) */
WT.L.ch.cascade = {
  num: "Kapitel 11", title: "Die Emissionskaskade", short: "Kaskade",
  lead: "Eine Emission ist selten das Ende: Der zurückbleibende Kern ist oft heiß genug, um erneut zu emittieren.",
  html: `
<div class="step">
  <p>Ein Neutron hat den Compoundkern (links) verlassen, und der <b>Restkern</b>, den es zurücklässt (rechts), ist noch heiß. Die orange Kugel ist die Energie. Der Grundzustand des Restkerns liegt um die <b>Separationsenergie</b> S<sub>n</sub> des Neutrons höher, die Kosten, um es herauszuziehen.</p>
  <p>Jedes Mal, wenn ein Neutron hinausgeht, fällt die Kugel um die kinetische Energie des Neutrons. Wo sie stoppt, ist die <b>Anregung</b> des Restkerns, seine überschüssige Energie; die Punkte rechts zählen die Landungen.</p>
  <div class="ctl"><label for="cs-e">Neutronenenergie</label><input id="cs-e" type="range" data-bind="E" min="1" max="30" step="0.5" value="15"><output data-show="E" data-fmt="1"></output></div>
  <p>Emittierte Neutronen sind meist langsam, also sind die meisten Fälle kurz. Blaue Punkte liegen über der gestrichelten Neutronenschwelle: Sie können sich ein zweites Neutron leisten, die (n,2n)-Reaktion. Unterhalb von etwa 11 MeV kommt keiner dorthin.</p>
</div>
<div class="step">
  <h3>Sequentielle Emission über die Karte</h3>
  <p>Die Ströme sind Reaktionen, die über eine Ecke der <b>Nuklidkarte</b> wandern, auf der die Kerne nach Neutronenzahl N (waagrecht) und Protonenzahl Z (senkrecht) angeordnet sind. Jede beginnt im umrandeten Compound-Feld; jedes Feld ist nach der Reaktion benannt, die dort endet.</p>
  <p>Ein ausgesandtes <em class="n">Neutron</em> bewegt sich ein Feld nach links, ein <em class="p">Proton</em> eines nach unten, ein <em class="a">Alphateilchen</em> (zwei Protonen, zwei Neutronen) zwei diagonal. Die Stromstärke zeigt, wie viel diesen Schritt nimmt; Tönung und Prozentwert zeigen, wo Reaktionen enden.</p>
  <div class="ctl"><label for="cs-e4">Neutronenenergie</label><input id="cs-e4" type="range" data-bind="E" min="1" max="30" step="0.5" value="14"><output data-show="E" data-fmt="1"></output></div>
  <div class="btns"><button class="btn" data-act="fire">200 Reaktionen abfeuern</button></div>
  <p>Zieh an der Energie: Bei wenigen MeV bleibt fast alles auf dem Targetfeld stehen; weiter oben reichen die Ströme weiter. Jeder Schritt kostet 7 bis 11 MeV Separationsenergie, also umfasst der Weg selbst bei 30 MeV höchstens drei oder vier Schritte.</p>
</div>
<div class="step">
  <h3>Bilanzierung der Besetzung</h3>
  <p>Die Engine leert jeden Kern von oben nach unten, eine Energiescheibe, ein <b>Intervall</b>, nach der anderen. Rechts: der Restkern der ersten Emission; links: sein Tochterkern, mit einem Neutron weniger. Orange Kugeln sind Reaktionen, die in jedem Intervall warten. Die Intervalle sind hier 1 MeV breit; die Engine verwendet etwa 40 pro Kern, bemessen nach der verfügbaren Energie.</p>
  <p>Während die Markierung ein Intervall überstreicht, nimmt jede Kugel einen Ausgang nach dem Wettbewerb aus Kapitel 9: Ein Photon (<em class="g">γ</em>) lässt sie in ein tieferes Intervall fallen, ein <em class="n">Neutron</em> bringt sie in den Tochterkern, ein Proton oder Alpha nimmt sie aus dem Bild. Unterhalb aller Schwellen tragen Photonen den Rest in den Grundzustand (grau). Dann wird der Tochterkern abgearbeitet.</p>
  <div class="ctl"><label for="cs-e3">Neutronenenergie</label><input id="cs-e3" type="range" data-bind="E" min="8" max="30" step="0.5" value="18"><output data-show="E" data-fmt="1"></output></div>
  <div class="btns"><button class="btn ghost" data-act="restart">Neu beginnen</button></div>
  <p>Photonen fallen nur nach unten, und jeder Kern ist fertig, bevor seine Töchter drankommen, also landet nichts in einem bereits geleerten Intervall.</p>
</div>
<div class="step">
  <h3>Exklusive Reaktionskanäle</h3>
  <p>Es läuft jeweils eine Reaktion ab: Die Markierung springt über die Karte, und jedes ausgesandte Teilchen fällt in die Ablage. Jeder Kanal läuft bei einer Energie ab, bei der er wirklich stattfindet (oben im Bild): (n,3n) bei 25 MeV, da drei Neutronen hier mehr als 20 MeV kosten; Einfang, (n,γ), bei 1 MeV. Die volle Ablage benennt den <b>exklusiven Kanal</b>, etwa (n,2n); Photonen zählen nicht. Die Engine gibt jedem Kanal seinen eigenen Wirkungsquerschnitt (seine Wahrscheinlichkeit, ausgedrückt als effektive Zielfläche).</p>
  <div class="btns"><button class="btn ghost" data-act="next">Nächster Kanal</button></div>
  <p>Geh sie durch. (n,np) läuft zweimal ab, einmal das Neutron zuerst, einmal das Proton zuerst: dasselbe Feld, dieselbe Ablage, ein Kanal. Dann erreicht ein geisterhaftes Deuteron (ein gebundenes Proton und Neutron) dieses Feld mit einem Sprung: Seine Ablage zeigt d, ein anderer Kanal, (n,d).</p>
</div>
<div class="step">
  <h3>Restkernproduktion</h3>
  <p>Jedes Feld enthält jetzt Regale: dunkel für den <b>Grundzustand</b>, grün (auf zwei Feldern) für ein <b>Isomer</b>, einen angeregten Zustand, der langlebig genug ist, um als eigenes Produkt zu zählen. Die Stapelhöhe ist die <b>Restkernproduktion</b>: wie viel von jedem Kern die Reaktionen erzeugt haben.</p>
  <div class="ctl"><label for="cs-e2">Neutronenenergie</label><input id="cs-e2" type="range" data-bind="E" min="1" max="30" step="0.5" value="14"><output data-show="E" data-fmt="1"></output></div>
  <div class="btns"><button class="btn" data-act="fire">200 Reaktionen abfeuern</button></div>
  <p>Ändere die Energie: Der nächste Durchgang verwendet sie, und alte Stapel verblassen. Die Produktion wandert vom Start weg, wenn mehr Teilchen hinausgehen können. Jede Geschichte endet in einem Regal, und eine Aktivierungsmessung sieht genau diese Stapel: Bestrahl eine Probe und zähl dann die Zerfälle jedes Produkts.</p>
  <div class="aside">Im Code: <code>emission/multiple.py</code> (die Schleife über Kerne und Intervalle, die γ-Kaskade), <code>emission/feeding.py</code> (Gitter und Eingaben für jeden Kern der Kette), <code>compound/continuum.py</code> (der Zerfall eines Intervalls), <code>emission/channels.py</code> (exklusive Kanäle, Restkernproduktion, Isomerenzweige), <code>emission/binary.py</code> (die Bilanz der ersten Emission).</div>
</div>`,
};
Object.assign(WT.L.labels, {
  // reaction names on the squares (unchanged in German)
  "(n,γ)": "(n,γ)", "(n,n′)": "(n,n′)", "(n,{#}n)": "(n,{#}n)", "(n,p)": "(n,p)", "(n,np)": "(n,np)", "(n,{#}np)": "(n,{#}np)",
  "(n,{#}p)": "(n,{#}p)", "(n,n{#}p)": "(n,n{#}p)", "(n,α)": "(n,α)", "(n,nα)": "(n,nα)",
  "compound": "Compound", "target": "Target",
  "N{#}": "N{#}", "N": "N", "N+{#}": "N+{#}", "Z": "Z", "Z{#}": "Z{#}",
  "neutron number →": "Neutronenzahl →",
  // scene 1
  "levels": "Niveaus",
  "Sₙ {#} MeV": "Sₙ {#} MeV", "Sₙ = {#} MeV": "Sₙ = {#} MeV",
  "ground": "Grund",
  "residual": "Restkern", "residual (one neutron fewer)": "Restkern (ein Neutron weniger)",
  "n threshold": "n-Schwelle", "its neutron threshold": "seine Neutronenschwelle",
  "{#} MeV": "{#} MeV",
  "drop = neutron's kinetic energy": "Fall = kinetische Energie des Neutrons",
  "{#} % land above the threshold: a second neutron can leave": "{#} % landen über der Schwelle: ein zweites Neutron kann gehen",
  "<{#} % land above the threshold: a second neutron can leave": "<{#} % landen über der Schwelle: ein zweites Neutron kann gehen",
  "all land below the threshold: only photons remain": "alle landen unter der Schwelle: nur Photonen bleiben",
  "{#} % above threshold: (n,{#}n) possible": "{#} % über der Schwelle: (n,{#}n) möglich",
  "<{#} % above threshold: (n,{#}n) possible": "<{#} % über der Schwelle: (n,{#}n) möglich",
  "all below threshold: photons only": "alle unter der Schwelle: nur Photonen",
  // scene 2
  "incoming neutron: {#} MeV": "einfallendes Neutron: {#} MeV",
  "shade and % = where reactions end": "Tönung und % = wo Reaktionen enden",
  "stream width = flow · shade and % = share of reactions that end in that nucleus": "Strombreite = Fluss · Tönung und % = Anteil der Reaktionen, die in diesem Kern enden",
  // scene 3
  "residual (first step)": "Restkern (erster Schritt)",
  "daughter: n fewer": "Tochter: ein n weniger", "daughter (one neutron fewer)": "Tochter (ein Neutron weniger)",
  "now: {#}–{#} MeV": "jetzt: {#}–{#} MeV", "{#}–{#} MeV": "{#}–{#} MeV",
  "done: {#} left by proton or alpha, the rest sit on ground states": "fertig: {#} per Proton oder Alpha hinaus, der Rest sitzt in Grundzuständen",
  "done: everything sits on a ground state": "fertig: alles sitzt in einem Grundzustand",
  "orange ball = reactions waiting in a bin · grey = settled on the ground state · pale bins = already emptied": "orange Kugel = wartende Reaktionen · grau = im Grundzustand angekommen · blasse Intervalle = schon geleert",
  // scene 4
  "collected": "gesammelt",
  "tray: d": "Ablage: d",
  "a deuteron lands on the same square, but its tray reads d: channel (n,d)": "ein Deuteron landet auf demselben Feld, aber seine Ablage zeigt d: Kanal (n,d)",
  "tray: n n  →  (n,{#}n)": "Ablage: n n  →  (n,{#}n)",
  "tray: n  →  (n,n′)": "Ablage: n  →  (n,n′)",
  "tray: p  →  (n,p)": "Ablage: p  →  (n,p)",
  "tray: n p  →  (n,np)": "Ablage: n p  →  (n,np)",
  "tray: n p  →  (n,np) · same square, same tray": "Ablage: n p  →  (n,np) · dasselbe Feld, dieselbe Ablage",
  "tray: a  →  (n,α)": "Ablage: a  →  (n,α)",
  "tray: n n n  →  (n,{#}n)": "Ablage: n n n  →  (n,{#}n)",
  "tray empty, only photons: (n,γ), capture": "Ablage leer, nur Photonen: (n,γ), Einfang",
  "each emitted particle falls into the tray": "jedes ausgesandte Teilchen fällt in die Ablage",
  "no particle gets out: only photons": "kein Teilchen kommt hinaus: nur Photonen",
  "incoming neutron: {#} MeV · channel {#} of {#}": "einfallendes Neutron: {#} MeV · Kanal {#} von {#}",
  // scene 5
  "isomer": "Isomer",
  "batch of {#} at {#} MeV": "Durchgang mit {#} bei {#} MeV",
  "ink shelf: ground state · green: isomer": "dunkles Regal: Grundzustand · grün: Isomer",
  "ink shelf: ground state · green shelf: isomer · pile height = how much of that nucleus was made": "dunkles Regal: Grundzustand · grünes Regal: Isomer · Stapelhöhe = wie viel von diesem Kern entstand",
});
