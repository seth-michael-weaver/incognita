/* German (Deutsch): landscape (Kapitel 4, die Landschaft der Nuklide) */
WT.L.ch.landscape = {
  num: "Kapitel 4", title: "Die Landschaft der Nuklide", short: "Landschaft",
  lead: "Jeder Kern, den je jemand erzeugt hat, auf einer Karte: bisher 3 338, und nur 252 halten ewig.",
  html: `
<div class="step">
  <h3>Die Nuklidkarte</h3>
  <p>Jedes kleine Quadrat ist ein Kern, der tatsächlich in einem Experiment beobachtet wurde: Die Neutronen zählen nach rechts, die Protonen nach oben. Blasse Quadrate wurden beobachtet, aber ihre Masse ist noch nicht gewogen, nur abgeschätzt. Die <b>dunklen</b> Quadrate sind die 252, die nie zerfallen. Die anderen zerfallen, orangefarbene im Nu, blaue erst nach Jahren. Die <em style="font-style:normal;color:var(--proton);font-weight:600">rote</em> Reihe ist das Element, das du mit dem Regler wählst: alle seine bekannten Isotope.</p>
  <div class="ctl"><label for="ls-z">Element ansehen (Protonen Z)</label><input id="ls-z" type="range" data-bind="zSel" data-instant min="1" max="110" step="1" value="26"><output data-show="zSel" data-fmt="0"></output></div>
  <p class="ctl-result" id="ls-z-out" aria-live="polite"></p>
</div>
<div class="step">
  <h3>Bindungsenergie über die Karte</h3>
  <p>Jetzt ist jedes Quadrat nach seiner <b>Bindungsenergie pro Nukleon</b> gefärbt, also danach, wie fest jedes Neutron oder Proton gehalten wird (Kapitel 3). Die stabilen Kerne liegen auf einem Grat starker Bindung; entfernt man sich davon, mit zu vielen Neutronen oder zu vielen Protonen, sinkt die Bindung. Am stärksten gebunden ist Nickel-62. Die dünnen Linien markieren die <b>magischen Zahlen</b> (8, 20, 28, 50, 82, 126), bei denen Kerne besonders fest gebunden sind.</p>
</div>
<div class="step">
  <h3>Beta-Zerfall zur Stabilität</h3>
  <p>Kerne mit derselben Gesamtzahl an Nukleonen (derselben <b>Massenzahl</b> A) liegen auf einer Diagonalen über die Karte, <em style="font-style:normal;color:var(--proton);font-weight:600">rot</em> dargestellt. Man beginnt mit zu vielen Neutronen, wie bei den Bruchstücken eines gespaltenen Urankerns. Beim <b>Beta-Zerfall</b> wird ein Neutron zu einem Proton, der Kern rückt also einen Platz entlang seiner Linie zur fester gebundenen Mitte, immer wieder, bis er den Grat erreicht und anhält. Das kleine Diagramm zeigt dieselbe Kette als Tal, in das der Kern hinabrollt. Probiere A = 137: Die Kette führt über Caesium-137, das langlebige Produkt von Reaktorunfällen.</p>
  <div class="ctl"><label for="ls-a">Massenzahl A</label><input id="ls-a" type="range" data-bind="aSel" data-instant min="8" max="250" step="1" value="137"><output data-show="aSel" data-fmt="0"></output></div>
  <p class="ctl-result" id="ls-a-out" aria-live="polite"></p>
</div>
<div class="step">
  <h3>Abdeckung durch INCOGNITA</h3>
  <p>Dieselbe Karte, gefärbt danach, was unsere Bibliothek für jeden Kern enthält. <em style="font-style:normal;color:var(--fission);font-weight:600">Grün</em>: aus seinen gemessenen Resonanzen evaluiert. Die übrigen haben eine Modelldatei, die allein von der Engine erzeugt wurde: <b>dunkel</b> für stabile oder langlebige (Stufe A), <em style="font-style:normal;color:var(--accent);font-weight:600">blau</em> für mehr als einen Tag (Stufe B), <em style="font-style:normal;color:var(--warm);font-weight:600">orange</em> für kurzlebigere (Stufe C). Graue sind nicht in der Bibliothek (meist die leichtesten Kerne und einige, die die Engine nicht rechnen kann).</p>
</div>`
};

Object.assign(WT.L.labels, {
  "neutrons N →": "Neutronen N →",
  "protons Z ↑": "Protonen Z ↑",
  "Fe: all its isotopes": "Fe: alle seine Isotope",
  "stable": "stabil",
  "lives years": "lebt Jahre",
  "gone in a blink": "im Nu zerfallen",
  "red: Fe (your pick)": "rot: Fe (deine Wahl)",
  "nickel{#}: most tightly bound": "Nickel{#}: am festesten gebunden",
  "held most tightly": "am festesten gebunden",
  "middle": "mittel",
  "held least": "am schwächsten gebunden",
  "red: the A = {#} chain": "rot: die Kette A = {#}",
  "A = {#}: deeper = more tightly bound": "A = {#}: tiefer = fester gebunden",
  "protons Z →": "Protonen Z →",
  "measured resonances": "gemessene Resonanzen",
  "tier A": "Stufe A",
  "tier B": "Stufe B",
  "tier C": "Stufe C",
  "not in library": "nicht in der Bibliothek",
});
