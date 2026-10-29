/* Italian: binding (Capitolo 3, perché i nuclei stanno insieme) */
WT.L.ch.binding = {
  num: "Capitolo 3", title: "Perché i nuclei stanno insieme", short: "Legame",
  html: `
<div class="step">
  <p>Più in alto sulla curva significa più fortemente legato. Ogni punto è un numero di massa A (il numero di protoni più neutroni) e la sua altezza è l'energia che servirebbe, per nucleone, per separare completamente quel nucleo. Trascina A e leggi il marcatore: la parte centrale della curva, intorno a ferro e nichel, è la cima.</p>
  <div class="ctl"><label for="bi-a">Numero di massa A</label><input id="bi-a" type="range" data-bind="pick" data-instant min="2" max="260" step="1" value="56"><output data-show="pick" data-fmt="0"></output></div>
</div>
<div class="step">
  <p>Spezza l'uranio: entrambi i pezzi stanno più in alto sulla curva dell'uranio da cui provengono, quindi gli stessi nucleoni finiscono legati più strettamente e la differenza esce sotto forma di energia. Scegli il frammento più leggero; quello più pesante è il resto dei 236 nucleoni.</p>
  <div class="ctl"><label for="bi-f">Frammento più leggero A</label><input id="bi-f" type="range" data-bind="frag" data-instant min="70" max="118" step="1" value="95"><output data-show="frag" data-fmt="0"></output></div>
  <p class="ctl-result" id="bi-split-out" aria-live="polite"></p>
  <p>Qualunque sia la divisione, sono circa 200 MeV: decine di milioni di volte i pochi elettronvolt che dà la combustione di una molecola di combustibile.</p>
</div>
<div class="step">
  <p>Unisci due nuclei leggeri in uno. Se il nuovo nucleo sta più in alto sulla curva, viene liberata energia. Oltre il picco, invece, l'unione costa energia.</p>
  <div class="ctl"><label for="bi-u">Ogni nucleo leggero A</label><input id="bi-u" type="range" data-bind="fuse" data-instant min="2" max="60" step="1" value="2"><output data-show="fuse" data-fmt="0"></output></div>
  <p class="ctl-result" id="bi-fuse-out" aria-live="polite"></p>
</div>`,
};
