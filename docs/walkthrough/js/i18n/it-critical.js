/* Italian: critical (Capitolo 21, criticità e controllo del reattore) */
WT.L.ch.critical = {
  num: "Capitolo 21", title: "Criticità e controllo del reattore", short: "Criticità",
  html: `
<div class="step">
  <h3>Il fattore di moltiplicazione</h3>
  <p>Ogni fissione libera alcuni neutroni; alcuni provocano le fissioni successive, gli altri si perdono. Il <b>fattore di moltiplicazione</b> <i>k</i> è il numero di nuove fissioni a cui porta una fissione: a ogni generazione i neutroni si moltiplicano per <i>k</i>. Sopra 1 la catena cresce, sotto 1 si spegne.</p>
  <div class="ctl"><label for="cri-k">Moltiplicazione k</label><input id="cri-k" type="range" data-bind="k" data-instant min="0.95" max="1.05" step="0.05" value="1.05"><output data-show="k" data-fmt="2"></output></div>
</div>
<div class="step">
  <h3>Neutroni ritardati</h3>
  <p>Una piccola parte dei neutroni (0,65 %) arriva con secondi di ritardo, da frammenti di fissione che prima decadono. Questi neutroni tardivi dettano il ritmo, così la crescita rallenta da un battito di ciglia a minuti. Il grafico procede a velocità ×10.</p>
  <div class="ctl"><label for="cri-k2">Moltiplicazione k</label><input id="cri-k2" type="range" data-bind="kd" data-instant min="0.998" max="1.002" step="0.0005" value="1.001"><output data-show="kd" data-fmt="4"></output></div>
  <div class="btns"><button class="btn ghost" data-act="delayed" aria-pressed="true">Neutroni ritardati</button></div>
</div>
<div class="step">
  <h3>Criticità</h3>
  <p>Un esperimento critico: muovi le barre di controllo finché la potenza resta costante. A quella regolazione <i>k</i> è esattamente 1, e quella posizione delle barre è la misura. Trovala: l'indicatore mostra <i>k</i> con cinque decimali.</p>
  <div class="ctl"><label for="cri-rod">Barre di controllo inserite (%)</label><input id="cri-rod" type="range" data-bind="ins" data-instant min="35" max="75" step="1" value="45"><output data-show="ins" data-fmt="0"></output></div>
</div>`,
};
/* attributes referenced in the English chapter script (for the structure check): data-act="delayed" data-act="delayed" */
