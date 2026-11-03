/* German (Deutsch): binding (Kapitel 3, Warum Kerne zusammenhalten) */
WT.L.ch.binding = {
  num: "Kapitel 3", title: "Warum Kerne zusammenhalten", short: "Bindung",
  html: `
<div class="step">
  <p>Höher auf der Kurve heißt fester gebunden. Jeder Punkt ist eine Massenzahl A (die Anzahl von Protonen plus Neutronen), und seine Höhe ist die Energie, die pro Nukleon nötig wäre, um diesen Kern vollständig auseinanderzureißen. Zieh A und lies die Markierung ab: Die Mitte der Kurve, um Eisen und Nickel, ist der Gipfel.</p>
  <div class="ctl"><label for="bi-a">Massenzahl A</label><input id="bi-a" type="range" data-bind="pick" data-instant min="2" max="260" step="1" value="56"><output data-show="pick" data-fmt="0"></output></div>
</div>
<div class="step">
  <p>Spalte Uran: Beide Bruchstücke liegen höher auf der Kurve als das Uran, aus dem sie entstanden, dieselben Nukleonen sind also fester gebunden, und der Unterschied wird als Energie frei. Wähle das leichtere Bruchstück; das schwerere sind die übrigen der 236 Nukleonen.</p>
  <div class="ctl"><label for="bi-f">Leichteres Bruchstück A</label><input id="bi-f" type="range" data-bind="frag" data-instant min="70" max="118" step="1" value="95"><output data-show="frag" data-fmt="0"></output></div>
  <p class="ctl-result" id="bi-split-out" aria-live="polite"></p>
  <p>Wie auch immer die Teilung ausfällt, es sind etwa 200 MeV: zig Millionen Mal die wenigen Elektronenvolt, die das Verbrennen eines Brennstoffmoleküls liefert.</p>
  <p>Leichte Kerne setzen auf dem umgekehrten Weg Energie frei, durch Verschmelzen: <a href="#fusion">→ Fusion</a>.</p>
</div>`,
};

Object.assign(WT.L.labels, {
  "mass number A →": "Massenzahl A →",
  "binding energy per nucleon (MeV)": "Bindungsenergie pro Nukleon (MeV)",
  "Ni{#}: most tightly bound": "Ni{#}: am festesten gebunden",
  "measured masses (AME{#})": "gemessene Massen (AME{#})",
  "Fe{#}: {#} MeV per nucleon · {#} MeV in all": "Fe{#}: {#} MeV pro Nukleon · {#} MeV insgesamt",
});
