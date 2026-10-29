/* Italian: doppler (Capitolo 20, allargamento Doppler) */
WT.L.ch.doppler = {
  num: "Capitolo 20", title: "Allargamento Doppler", short: "Doppler",
  html: `
<div class="step">
  <h3>Agitazione termica del bersaglio</h3>
  <p>Combustibile più caldo: i suoi atomi si agitano più in fretta. Ogni atomo di uranio non è più fermo quando arriva un neutrone.</p>
  <div class="ctl"><label for="dop-t1">Temperatura del combustibile (K)</label><input id="dop-t1" type="range" data-bind="T" data-instant min="300" max="1500" step="10" value="600"><output data-show="T" data-fmt="0"></output></div>
</div>
<div class="step">
  <h3>Allargamento Doppler</h3>
  <p>La curva è la probabilità che l'uranio-238 catturi un neutrone, in funzione dell'energia del neutrone. La sua altezza è un'area bersaglio in <b>barn</b> (un barn è 10<sup>−24</sup> cm², più o meno la dimensione che un nucleo mostra a un neutrone). Poiché gli atomi si muovono, alcuni incontrano il neutrone frontalmente e altri gli sfuggono, così lo stretto picco si sfuma: più basso e più largo. La sua area resta la stessa.</p>
  <div class="ctl"><label for="dop-t2">Temperatura del combustibile (K)</label><input id="dop-t2" type="range" data-bind="T" data-instant min="300" max="1500" step="10" value="1200"><output data-show="T" data-fmt="0"></output></div>
</div>
<div class="step">
  <h3>Autoschermo delle risonanze</h3>
  <p>Una pastiglia di combustibile è spessa. La fascia ombreggiata è la frazione di neutroni che ferma a ciascuna energia. Il centro del picco ferma già tutto, a caldo o a freddo, quindi un picco più basso non perde nulla lì; le ali più larghe ne catturano di più. Più neutroni vanno persi per cattura invece di provocare fissione, e così <i>k</i> scende da solo. (<i>k</i> è il numero di nuove fissioni a cui porta ogni fissione; lo spiega il capitolo 21.)</p>
  <div class="ctl"><label for="dop-t3">Temperatura del combustibile (K)</label><input id="dop-t3" type="range" data-bind="T" data-instant min="300" max="1500" step="10" value="900"><output data-show="T" data-fmt="0"></output></div>
</div>`,
};
