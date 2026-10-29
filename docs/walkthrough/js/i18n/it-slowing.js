/* Italian: slowing (Capitolo 19, moderazione dei neutroni) */
WT.L.ch.slowing = {
  num: "Capitolo 19", title: "Moderazione dei neutroni", short: "Rallentamento",
  html: `
<div class="step">
  <p>Ogni rimbalzo sull'idrogeno costa circa metà dell'energia. Un neutrone di fissione parte da 2 MeV e rimbalza attraverso l'acqua. Un nucleo di idrogeno pesa quanto il neutrone, quindi, come le palle da biliardo, a ogni rimbalzo gli cede in media metà dell'energia del neutrone.</p>
  <p>Il grafico mostra l'energia del neutrone dopo ogni rimbalzo; ogni etichetta lungo il lato ha mille volte meno energia. Perdere ogni volta la stessa frazione dà una discesa rettilinea, la linea tratteggiata. Dopo circa 18 rimbalzi il neutrone raggiunge l'energia <b>termica</b>, 0,025 eV, dove l'acqua calda lo risolleva tante volte quante lo rallenta. L'ossigeno è 16 volte più pesante: ogni rimbalzo sottrae poco, e ne servono più di cento.</p>
  <div class="btns"><button class="btn ghost" data-act="tgtH" aria-pressed="true">Idrogeno</button><button class="btn ghost" data-act="tgtO" aria-pressed="false">Ossigeno</button><button class="btn" data-act="again">Lancia ancora</button></div>
</div>
<div class="step">
  <p>Sotto circa 1 eV, i legami della molecola determinano ogni rimbalzo. Ogni idrogeno è legato al suo ossigeno (le linee chiare). Un neutrone lento non colpisce più un idrogeno libero: colpisce un'intera molecola, 18 volte più pesante, per cui un semplice rimbalzo sottrae quasi nulla.</p>
  <p>Può anche far oscillare o vibrare la molecola, ma solo cedendo una quantità fissa di energia per volta, 0,06, 0,2 o 0,45 eV (i lampi luminosi). Le molecole calde a volte restituiscono una tale quantità. Nel grafico, la fascia ombreggiata sotto 1 eV è dove questo conta. Disattiva il legame per confrontare con l'idrogeno libero.</p>
  <div class="btns"><button class="btn ghost" data-act="bind" aria-pressed="true">Legame chimico</button><button class="btn" data-act="again">Lancia ancora</button></div>
</div>
<div class="step">
  <p>Un codice di calcolo ha bisogno di tutto questo sotto forma di tabella: la <b>legge di diffusione</b>, la mappa. In orizzontale: quanto è forte l'urto, α (la spinta trasmessa alla molecola; piccola per un tocco di striscio, grande per un colpo frontale). In verticale: l'energia che il neutrone guadagna (su) o perde (giù), β, contata in unità dell'energia termica dell'acqua, 0,025 eV. Chiaro significa probabile, pallido significa raro.</p>
  <p>Il contorno è ciò che un neutrone dell'energia scelta può raggiungere: non può perdere più di quanto ha, e ogni variazione di energia consente solo un intervallo di urti. Trascina l'energia e il contorno si allarga o si restringe. Senza legame la mappa è quella del gas di idrogeno libero, un'unica cresta chiara lungo la linea tratteggiata del rinculo; con il legame la molecola aggiunge strisce chiare, le sue quantità fisse di energia. INCOGNITA calcola le proprie leggi per l'acqua e il berillio: <a href="https://github.com/seth-michael-weaver/incognita/tree/main/library/tsl-v0.1" style="white-space:nowrap">tsl-v0.1</a>.</p>
  <div class="ctl"><label for="slo-e">Energia del neutrone (eV)</label><input id="slo-e" type="range" data-bind="lgE" data-instant min="-2.3" max="0" step="0.01" value="-1"><output data-show="Eshow" data-fmt="3"></output></div>
  <div class="btns"><button class="btn ghost" data-act="bind" aria-pressed="true">Legame chimico</button></div>
</div>`,
};
/* attributes referenced in the English chapter script (for the structure check): data-act="${act}" */
