/* German (Deutsch): critical (Kapitel 21, Kritikalität und Reaktorsteuerung) */
/* (structure-check parity with ch/critical.js script selectors: data-act="delayed" data-act="delayed") */
WT.L.ch.critical = {
  num: "Kapitel 21", title: "Kritikalität und Reaktorsteuerung", short: "Kritikalität",
  html: `
<div class="step">
  <h3>Der Multiplikationsfaktor</h3>
  <p>Jede Spaltung setzt einige Neutronen frei; manche lösen die nächsten Spaltungen aus, der Rest geht verloren. Der <b>Multiplikationsfaktor</b> <i>k</i> gibt an, zu wie vielen neuen Spaltungen eine Spaltung führt: Jede Generation vervielfacht die Neutronen um den Faktor <i>k</i>. Über 1 wächst die Kette, unter 1 stirbt sie ab.</p>
  <div class="ctl"><label for="cri-k">Multiplikation k</label><input id="cri-k" type="range" data-bind="k" data-instant min="0.95" max="1.05" step="0.05" value="1.05"><output data-show="k" data-fmt="2"></output></div>
</div>
<div class="step">
  <h3>Verzögerte Neutronen</h3>
  <p>Ein kleiner Anteil der Neutronen (0,65 %) kommt Sekunden zu spät, von Spaltfragmenten, die erst zerfallen müssen. Diese späten Neutronen bestimmen das Tempo, sodass das Wachstum von einem Augenblick auf Minuten gedehnt wird. Das Diagramm läuft mit zehnfacher Geschwindigkeit.</p>
  <div class="ctl"><label for="cri-k2">Multiplikation k</label><input id="cri-k2" type="range" data-bind="kd" data-instant min="0.998" max="1.002" step="0.0005" value="1.001"><output data-show="kd" data-fmt="4"></output></div>
  <div class="btns"><button class="btn ghost" data-act="delayed" aria-pressed="true">Verzögerte Neutronen</button></div>
</div>
<div class="step">
  <h3>Kritikalität</h3>
  <p>Ein kritisches Experiment: Bewege die Steuerstäbe, bis die Leistung konstant bleibt. Bei dieser Einstellung ist <i>k</i> genau 1, und diese Stabposition ist die Messung. Finde sie: Die Anzeige zeigt <i>k</i> auf fünf Dezimalstellen.</p>
  <div class="ctl"><label for="cri-rod">Steuerstäbe eingefahren (%)</label><input id="cri-rod" type="range" data-bind="ins" data-instant min="35" max="75" step="1" value="45"><output data-show="ins" data-fmt="0"></output></div>
</div>`,
};

Object.assign(WT.L.labels, {
  "generations →": "Generationen →",
  "k = {#}: dies away": "k = {#}: stirbt ab",
  "k = {#}: steady": "k = {#}: konstant",
  "k = {#}: grows": "k = {#}: wächst",
  "{#} generations last under {#} s in a water reactor": "{#} Generationen dauern im Wasserreaktor unter {#} s",
  "illustration": "Illustration",
  "amber: fission fragments that emit a neutron seconds later": "bernsteinfarben: Spaltfragmente, die Sekunden später ein Neutron abgeben",
  "{#} s": "{#} s",
  "time →": "Zeit →",
  "×{#} speed": "×{#} Tempo",
  "with delayed: doubles every {#} s": "mit verzögerten: verdoppelt sich alle {#} s",
  "prompt only: doubles every {#} ms": "nur prompte: verdoppelt sich alle {#} ms",
  "k = {#} · {#} % of neutrons delayed about {#} s (one-group average)": "k = {#} · {#} % der Neutronen um etwa {#} s verzögert (Ein-Gruppen-Mittel)",
  "rods {#} % in": "Stäbe {#} % eingefahren",
  "k = {#} · doubles every {#} min": "k = {#} · verdoppelt sich alle {#} min",
});
