/* German (Deutsch): products (Kapitel 15, Spaltprodukte und Nachwärme) */
WT.L.ch.products = {
  num: "Kapitel 15", title: "Spaltprodukte und Nachwärme", short: "Spaltprodukte",
  html: `
<div class="step">
  <p>Die Stücke sind ungleich: ein leichtes, ein schweres. Das Diagramm zeigt für jede Bruchstückmasse A (Protonen plus Neutronen) den Anteil der Spaltungen, die sie erzeugen. Zwei Buckel: leichte Stücke bei A = 95, schwere bei 139. Eine gleichmäßige Teilung, bei A = 117, ist etwa hundertmal seltener.</p>
  <p>Jede gestrichelte Linie liegt zehnmal höher als die darunter, damit auch die seltenen Massen sichtbar bleiben. Tippe auf einen Balken oder zieh den Regler: Unten stehen die beiden Stücke dieser Teilung. Ihre Massen ergeben zusammen 234, nicht 236 (Uran-235 plus das Neutron), weil etwa 2,4 Neutronen ebenfalls davonfliegen.</p>
  <div class="ctl"><label for="pr-a">Leichtes Bruchstück A</label><input id="pr-a" type="range" data-bind="pick" data-instant min="70" max="117" step="1" value="95"><output data-show="pick" data-fmt="0"></output></div>
</div>
<div class="step">
  <p>Ihre Zerfälle heizen den Brennstoff nach der Abschaltung weiter. Die Bruchstücke sind radioaktiv: Sie zerfallen eines nach dem anderen, und jeder Zerfall gibt Wärme ab, ob die Kettenreaktion läuft oder nicht.</p>
  <div class="ctl"><label for="pr-t">Zeit nach der Abschaltung</label><input id="pr-t" type="range" data-bind="lgt" data-instant min="0" max="8.5" step="0.01" value="0"><output id="pr-tout">1 s</output></div>
  <p>Zieh die Zeit. Eine Sekunde nach dem Stillstand des Reaktors liefern die Zerfälle noch etwa 6 % der vollen Leistung; nach einem Tag etwa ein halbes Prozent; nach einem Jahr einige Hundertstel Prozent, in einem großen Reaktor immer noch fast ein Megawatt. Deshalb wird abgebrannter Brennstoff jahrelang in Kühlbecken aufbewahrt. Die Kurve ist die Faustregel von Way und Wigner: eine einfache Formel für die Zerfälle aller Bruchstücke zusammen, nach einem Jahr Betrieb. Beide Skalen springen an jeder Marke um den Faktor zehn.</p>
</div>`,
};

Object.assign(WT.L.labels, {
  "fragment mass number A →": "Massenzahl des Bruchstücks A →",
  "share of fissions that make it (each line ×{#})": "Anteil der Spaltungen, die es erzeugen (jede Linie ×{#})",
  "Rb{#} · {#} %": "Rb{#} · {#} %",
  "Xe{#} · {#} %": "Xe{#} · {#} %",
  "+ about {#} neutrons": "+ etwa {#} Neutronen",
  "{#} % of full power": "{#} % der vollen Leistung",
  "≈ {#} MW in a {#} MW reactor · {#} s after shutdown": "≈ {#} MW in einem {#}-MW-Reaktor · {#} s nach Abschaltung",
  "{#} min": "{#} min",
  "{#} h": "{#} h",
  "{#} day": "{#} Tag",
  "{#} yr": "{#} Jahr",
  "time after shutdown (each mark much later) →": "Zeit nach Abschaltung (jede Marke viel später) →",
  "Way–Wigner rule of thumb, after a year at full power": "Faustregel nach Way und Wigner, nach einem Jahr Volllast",
});
