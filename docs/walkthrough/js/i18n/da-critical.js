/* Danish: critical (Kapitel 20, kritikalitet og reaktorstyring) */
WT.L.ch.critical = {
  num: "Kapitel 20", title: "Kritikalitet og reaktorstyring", short: "Kritikalitet",
  html: `
<div class="step">
  <h3>Multiplikationsfaktoren</h3>
  <p>Hver fission frigør nogle få neutroner; nogle forårsager de næste fissioner, resten går tabt. <b>Multiplikationsfaktoren</b> <i>k</i> er, hvor mange nye fissioner én fission fører til: hver generation multiplicerer neutronerne med <i>k</i>. Over 1 vokser kæden, under 1 dør den ud.</p>
  <div class="ctl"><label for="cri-k">Multiplikation k</label><input id="cri-k" type="range" data-bind="k" data-instant min="0.95" max="1.05" step="0.05" value="1.05"><output data-show="k" data-fmt="2"></output></div>
</div>
<div class="step">
  <h3>Forsinkede neutroner</h3>
  <p>En lille andel af neutronerne (0,65 %) kommer sekunder for sent, fra fissionsfragmenter, der først skal henfalde. Disse sene bestemmer tempoet, så væksten går fra et øjeblik til minutter. Grafen kører ti gange hurtigere.</p>
  <div class="ctl"><label for="cri-k2">Multiplikation k</label><input id="cri-k2" type="range" data-bind="kd" data-instant min="0.998" max="1.002" step="0.0005" value="1.001"><output data-show="kd" data-fmt="4"></output></div>
  <div class="btns"><button class="btn ghost" data-act="delayed" aria-pressed="true">Forsinkede neutroner</button></div>
</div>
<div class="step">
  <h3>Kritikalitet</h3>
  <p>Et kritisk eksperiment: flyt kontrolstavene, til effekten holder sig flad. Ved den indstilling er <i>k</i> præcis 1, og stavenes position er målingen. Find den: aflæsningen viser <i>k</i> med fem decimaler.</p>
  <div class="ctl"><label for="cri-rod">Kontrolstave inde (%)</label><input id="cri-rod" type="range" data-bind="ins" data-instant min="35" max="75" step="1" value="45"><output data-show="ins" data-fmt="0"></output></div>
</div>
`,
};
/* attributes referenced in the English chapter script (for the structure check): data-act="delayed" data-act="delayed" */
