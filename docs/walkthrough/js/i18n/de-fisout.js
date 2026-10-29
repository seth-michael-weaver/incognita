/* German (Deutsch): fisout (Kapitel 14, Spaltneutronen) */
WT.L.ch.fisout = {
  num: "Kapitel 14", title: "Spaltneutronen", short: "Spaltneutronen",
  html: `
<div class="step">
  <p>Jede Spaltung setzt zwei oder drei Neutronen frei: im Mittel 2,4. Oben eine Spaltung nach der anderen: Der Urankern zerreißt in zwei Bruchstücke, und die blauen Kugeln fliegen davon. Das sind die <b>prompten</b> Neutronen, in weit weniger als einer Millionstelsekunde draußen.</p>
  <p>Das linke Diagramm zählt, wie viele Spaltungen 0, 1, 2, 3 … Neutronen freisetzten. Die Balken sind die Spaltungen, die du ausgelöst hast; die dünne Linie auf jedem Balken ist der gemessene Anteil. Löse mehr aus, und die Balken legen sich auf die Linien.</p>
  <div class="btns"><button class="btn" data-act="f100">100 Spaltungen</button><button class="btn ghost" data-act="f1000">1000 Spaltungen</button></div>
</div>
<div class="step">
  <p>Sie entstehen schnell: im Mittel etwa 2 MeV, rund 80 Millionen Mal die Energie eines langsamen Neutrons in einem Reaktor bei Raumtemperatur. Das rechte Diagramm sortiert die prompten Neutronen nach Energie. Die Linie ist die gemessene Form (das Watt-Spektrum): ein Buckel bei etwa 1 MeV und ein langer Ausläufer bis 10 MeV.</p>
  <p>Solch schnelle Neutronen lösen in Uran-235 selten die nächste Spaltung aus, ein Reaktor bremst sie deshalb zuerst ab, wie ein späteres Kapitel zeigt.</p>
  <div class="btns"><button class="btn" data-act="f100">100 Spaltungen</button><button class="btn ghost" data-act="f1000">1000 Spaltungen</button></div>
</div>
<div class="step">
  <p>Einige kommen Sekunden später: 0,65 % aller Neutronen. Manche Bruchstücke sind so neutronenreich, dass der neue Kern bei ihrem späteren Zerfall eines seiner Neutronen nicht halten kann und es freigibt. Dieses Neutron muss auf den Zerfall warten, oft Sekunden.</p>
  <p>Die untere Linie ist eine Uhr, die bei der Spaltung startet, von 0,01 s bis 100 s; jeder Strich liegt zehnmal später als der vorige. Die Kugel links steht für alle prompten Neutronen, auf einmal draußen. Jeder kleine Punkt ist ein verzögertes Neutron: Es wandert die Linie entlang, solange seine Wartezeit läuft, auf einer um das 20-Fache beschleunigten Uhr, und bleibt dort liegen, wo es schließlich herauskam. Diese wenigen späten Neutronen machen einen Reaktor steuerbar: Sie verlangsamen die Antwort der Kettenreaktion von Tausendstelsekunden auf Sekunden.</p>
  <div class="btns"><button class="btn" data-act="f1000">1000 Spaltungen</button><button class="btn ghost" data-act="clear">Löschen</button></div>
</div>`,
};

Object.assign(WT.L.labels, {
  "n + U{#} → two fragments + neutrons": "n + U{#} → zwei Bruchstücke + Neutronen",
  "prompt neutrons per fission": "prompte Neutronen pro Spaltung",
  "lines: measured shares": "Linien: gemessene Anteile",
  "mean {#}": "Mittel {#}",
  "prompt-neutron energy (MeV)": "Energie prompter Neutronen (MeV)",
  "mean {#} MeV": "Mittel {#} MeV",
  "line: measured shape": "Linie: gemessene Form",
  "prompt": "prompt",
  "time after fission · clock sped up {#}×": "Zeit nach der Spaltung · Uhr {#}× beschleunigt",
  "delayed {#} of {#} ({#} %)": "verzögert {#} von {#} ({#} %)",
  "{#} fissions": "{#} Spaltungen",
});
