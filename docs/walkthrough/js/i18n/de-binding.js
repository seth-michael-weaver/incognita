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
</div>
<div class="step">
  <p>Verschmilz zwei leichte Kerne zu einem. Liegt der neue Kern höher auf der Kurve, wird Energie frei. Jenseits des Gipfels kostet das Verschmelzen stattdessen Energie.</p>
  <div class="ctl"><label for="bi-u">Jeder leichte Kern A</label><input id="bi-u" type="range" data-bind="fuse" data-instant min="2" max="60" step="1" value="2"><output data-show="fuse" data-fmt="0"></output></div>
  <p class="ctl-result" id="bi-fuse-out" aria-live="polite"></p>
</div>`,
};
