/* German (Deutsch): doppler (Kapitel 20, Doppler-Verbreiterung) */
WT.L.ch.doppler = {
  num: "Kapitel 20", title: "Doppler-Verbreiterung", short: "Doppler",
  html: `
<div class="step">
  <h3>Wärmebewegung des Targets</h3>
  <p>Heißerer Brennstoff: Seine Atome zittern schneller. Jedes Uranatom ruht nicht mehr, wenn ein Neutron eintrifft.</p>
  <div class="ctl"><label for="dop-t1">Brennstofftemperatur (K)</label><input id="dop-t1" type="range" data-bind="T" data-instant min="300" max="1500" step="10" value="600"><output data-show="T" data-fmt="0"></output></div>
</div>
<div class="step">
  <h3>Doppler-Verbreiterung</h3>
  <p>Die Kurve zeigt die Wahrscheinlichkeit, dass Uran-238 ein Neutron einfängt, aufgetragen über der Neutronenenergie. Ihre Höhe ist eine Zielfläche in <b>Barn</b> (ein Barn sind 10<sup>−24</sup> cm², ungefähr die Größe, die ein Kern einem Neutron zeigt). Weil sich die Atome bewegen, begegnen einige dem Neutron frontal und andere laufen davon, sodass der schmale Peak verschmiert: niedriger und breiter. Seine Fläche bleibt gleich.</p>
  <div class="ctl"><label for="dop-t2">Brennstofftemperatur (K)</label><input id="dop-t2" type="range" data-bind="T" data-instant min="300" max="1500" step="10" value="1200"><output data-show="T" data-fmt="0"></output></div>
</div>
<div class="step">
  <h3>Resonanz-Selbstabschirmung</h3>
  <p>Eine Brennstofftablette ist dick. Das schattierte Band ist der Anteil der Neutronen, den sie bei jeder Energie stoppt. Die Mitte des Peaks stoppt schon alles, heiß oder kalt, ein niedrigerer Peak verliert dort also nichts; die breiteren Flügel fangen mehr ein. Mehr Neutronen gehen durch Einfang verloren, statt Spaltungen auszulösen, und <i>k</i> sinkt von selbst. (<i>k</i> gibt an, zu wie vielen neuen Spaltungen jede Spaltung führt; Kapitel <a href="#critical">21</a> erklärt es.)</p>
  <div class="ctl"><label for="dop-t3">Brennstofftemperatur (K)</label><input id="dop-t3" type="range" data-bind="T" data-instant min="300" max="1500" step="10" value="900"><output data-show="T" data-fmt="0"></output></div>
</div>`,
};

Object.assign(WT.L.labels, {
  "uranium atoms in the fuel": "Uranatome im Brennstoff",
  "{#} K": "{#} K",
  "caught in the peak": "im Peak eingefangen",
  "k": "k",
  "neutron energy (eV) →": "Neutronenenergie (eV) →",
  "capture cross section": "Einfangquerschnitt",
  "peak {#}k barns · Doppler width {#} meV · area unchanged": "Peak {#}k Barn · Doppler-Breite {#} meV · Fläche gleich",
  "all stopped": "alle gestoppt",
  "wider wings catch more": "breitere Flügel fangen mehr",
  "share of neutrons stopped in the fuel": "Anteil der im Brennstoff gestoppten Neutronen",
  "the peak's centre already stops everything; the wider wings catch more": "die Peakmitte stoppt schon alles; die breiteren Flügel fangen mehr",
});
