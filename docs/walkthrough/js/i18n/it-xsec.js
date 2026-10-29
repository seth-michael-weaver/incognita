/* Italian: xsec (Capitolo 2, che cos'è una sezione d'urto) */
WT.L.ch.xsec = {
  num: "Capitolo 2", title: "Che cos'è una sezione d'urto?", short: "Sezione d'urto",
  html: `
<div class="step">
  <p>Ogni disco è l'area bersaglio di un nucleo: la sua <b>sezione d'urto</b>, indicata con σ (sigma). L'immagine guarda dall'alto un sottile foglio di nuclei mentre i neutroni piovono su di esso in punti casuali. Un neutrone che cade dentro un disco reagisce con quel nucleo (un lampo arancione); uno che cade tra i dischi passa dritto (sfuma e basta).</p>
  <p>Perciò la parte che reagisce è semplicemente la parte del foglio coperta dai dischi. Il piccolo quadrato nero è l'unità di area, un <b>barn</b>, 10⁻²⁴ cm²: la faccia reale di un nucleo è circa un barn.</p>
  <div class="ctl"><label for="xs-e1">Energia del neutrone (eV)</label><input id="xs-e1" type="range" data-bind="lgE" data-instant min="-2.3" max="2" step="0.01" value="2"><output data-show="Eshow" data-fmt="2"></output></div>
</div>
<div class="step">
  <p>I neutroni più lenti vedono bersagli più grandi. Il disco non è la dimensione reale del nucleo: è quanto grande il nucleo si comporta per un neutrone a questa energia, e un neutrone lento si trattiene più a lungo vicino al nucleo, quindi ha più probabilità di essere catturato. Per la cattura questo fa crescere σ come 1/velocità.</p>
  <p>La curva sotto il foglio è σ a tutte le energie (entrambe le scale sono logaritmiche); il punto arancione segna l'energia scelta. Trascina verso il basso, fino ai neutroni più lenti, e osserva i dischi crescere e la parte che ha reagito salire.</p>
  <div class="ctl"><label for="xs-e2">Energia del neutrone (eV)</label><input id="xs-e2" type="range" data-bind="lgE" data-instant min="-2.3" max="2" step="0.01" value="-1.6"><output data-show="Eshow" data-fmt="2"></output></div>
</div>
<div class="step">
  <p>A una risonanza il bersaglio si gonfia. A 7 eV il neutrone più il nucleo hanno esattamente l'energia di uno dei livelli del nucleo stesso, che viene quindi assorbito molto più facilmente: l'area del disco cresce di circa cinquanta volte, qui fino a circa 400 barn.</p>
  <p>Spostati di poco da 7 eV e il disco si restringe subito: il picco della curva è stretto. I nuclei reali hanno molti picchi di questo tipo; il capitolo 1 ne ha mostrato il codice a barre.</p>
  <div class="ctl"><label for="xs-e3">Energia del neutrone (eV)</label><input id="xs-e3" type="range" data-bind="lgE" data-instant min="-2.3" max="2" step="0.005" value="0.845"><output data-show="Eshow" data-fmt="2"></output></div>
</div>`,
};
