/* German (Deutsch): xsec (Kapitel 2, Was ist ein Wirkungsquerschnitt?) */
WT.L.ch.xsec = {
  num: "Kapitel 2", title: "Was ist ein Wirkungsquerschnitt?", short: "Wirkungsquerschnitt",
  html: `
<div class="step">
  <p>Jede Scheibe ist die Zielfläche eines Kerns: sein <b>Wirkungsquerschnitt</b>, geschrieben σ (Sigma). Das Bild blickt senkrecht auf eine dünne Schicht aus Kernen, während Neutronen an zufälligen Stellen darauf prasseln. Ein Neutron, das innerhalb einer Scheibe landet, reagiert mit diesem Kern (ein oranger Blitz); eines, das zwischen den Scheiben landet, fliegt einfach hindurch (es verblasst nur).</p>
  <p>Der Anteil, der reagiert, ist also schlicht der Anteil der Schicht, den die Scheiben bedecken. Das kleine schwarze Quadrat ist die Flächeneinheit, ein <b>Barn</b>, 10⁻²⁴ cm²: die wahre Stirnfläche eines Kerns beträgt etwa ein Barn.</p>
  <div class="ctl"><label for="xs-e1">Neutronenenergie (eV)</label><input id="xs-e1" type="range" data-bind="lgE" data-instant min="-2.3" max="2" step="0.01" value="2"><output data-show="Eshow" data-fmt="2"></output></div>
</div>
<div class="step">
  <p>Langsamere Neutronen sehen größere Ziele. Die Scheibe ist nicht die wirkliche Größe des Kerns: Sie zeigt, wie groß der Kern für ein Neutron dieser Energie wirkt, und ein langsames Neutron verweilt länger in der Nähe des Kerns und wird deshalb eher eingefangen. Beim Einfang wächst σ dadurch wie 1/Geschwindigkeit.</p>
  <p>Die Kurve unter der Schicht ist σ über alle Energien (beide Skalen sind logarithmisch); der orange Punkt markiert die gewählte Energie. Zieh hinunter zu den langsamsten Neutronen und sieh zu, wie die Scheiben wachsen und der reagierte Anteil steigt.</p>
  <div class="ctl"><label for="xs-e2">Neutronenenergie (eV)</label><input id="xs-e2" type="range" data-bind="lgE" data-instant min="-2.3" max="2" step="0.01" value="-1.6"><output data-show="Eshow" data-fmt="2"></output></div>
</div>
<div class="step">
  <p>Bei einer Resonanz schwillt das Ziel an. Bei 7 eV haben Neutron und Kern zusammen genau die Energie eines der eigenen Niveaus des Kerns, er nimmt es also weit leichter auf: Die Scheibe wächst um etwa das Fünfzigfache an Fläche, hier auf etwa 400 Barn.</p>
  <p>Geh ein wenig von 7 eV weg, und die Scheibe schrumpft sofort wieder: Der Peak der Kurve ist schmal. Echte Kerne haben viele solcher Peaks; Kapitel 1 hat ihren Strichcode gezeigt.</p>
  <div class="ctl"><label for="xs-e3">Neutronenenergie (eV)</label><input id="xs-e3" type="range" data-bind="lgE" data-instant min="-2.3" max="2" step="0.005" value="0.845"><output data-show="Eshow" data-fmt="2"></output></div>
</div>`,
};
