/* Italian: landscape (Capitolo 4, il paesaggio dei nuclei) */
WT.L.ch.landscape = {
  num: "Capitolo 4", title: "Il paesaggio dei nuclei", short: "Paesaggio",
  lead: "Ogni nucleo che qualcuno abbia mai prodotto, su un'unica mappa: finora 3.338, e solo 252 durano per sempre.",
  html: `
<div class="step">
  <h3>La carta dei nuclidi</h3>
  <p>Ogni quadratino è un nucleo che è stato effettivamente osservato in un esperimento: i neutroni si contano in orizzontale, i protoni in verticale. I quadratini chiari sono stati osservati, ma la loro massa non è ancora stata pesata, solo stimata. I quadratini <b>scuri</b> sono i 252 che non decadono mai. Gli altri si disfano, quelli arancioni in un lampo, quelli blu solo dopo anni. La riga <em style="font-style:normal;color:var(--proton);font-weight:600">rossa</em> è l'elemento scelto con il cursore: tutti i suoi isotopi noti.</p>
  <div class="ctl"><label for="ls-z">Guarda l'elemento (protoni Z)</label><input id="ls-z" type="range" data-bind="zSel" data-instant min="1" max="110" step="1" value="26"><output data-show="zSel" data-fmt="0"></output></div>
  <p class="ctl-result" id="ls-z-out" aria-live="polite"></p>
</div>
<div class="step">
  <h3>L'energia di legame sulla carta</h3>
  <p>Ora ogni quadratino è colorato secondo la sua <b>energia di legame per nucleone</b>, cioè quanto saldamente è trattenuto ogni neutrone o protone (capitolo 3). I nuclei stabili si dispongono lungo una cresta di forte legame; allontanandosene, con troppi neutroni o troppi protoni, il legame cala. Il più forte di tutti è il nichel-62. Le linee sottili segnano i <b>numeri magici</b> (8, 20, 28, 50, 82, 126), dove i nuclei sono legati in modo particolarmente stretto.</p>
</div>
<div class="step">
  <h3>Decadimento beta verso la stabilità</h3>
  <p>I nuclei con lo stesso numero totale di nucleoni (lo stesso <b>numero di massa</b> A) giacciono su una linea diagonale della mappa, mostrata in <em style="font-style:normal;color:var(--proton);font-weight:600">rosso</em>. Si parte con troppi neutroni, come i frammenti di un nucleo di uranio spezzato. Nel <b>decadimento beta</b> un neutrone diventa un protone, quindi il nucleo fa un passo lungo la sua linea verso il centro, più saldamente legato, ancora e ancora, finché raggiunge la cresta e si ferma. Il piccolo grafico mostra la stessa catena come una valle in cui il nucleo rotola. Prova A = 137: la catena passa per il cesio-137, il prodotto di lunga vita degli incidenti nei reattori.</p>
  <div class="ctl"><label for="ls-a">Numero di massa A</label><input id="ls-a" type="range" data-bind="aSel" data-instant min="8" max="250" step="1" value="137"><output data-show="aSel" data-fmt="0"></output></div>
  <p class="ctl-result" id="ls-a-out" aria-live="polite"></p>
</div>
<div class="step">
  <h3>La copertura di INCOGNITA</h3>
  <p>La stessa mappa, colorata secondo ciò che la nostra libreria contiene per ogni nucleo. <em style="font-style:normal;color:var(--fission);font-weight:600">Verde</em>: valutato a partire dalle sue risonanze misurate. Gli altri hanno un file di modello costruito dal solo motore: <b>scuro</b> per i nuclei stabili o di lunga vita (livello A), <em style="font-style:normal;color:var(--accent);font-weight:600">blu</em> per più di un giorno (livello B), <em style="font-style:normal;color:var(--warm);font-weight:600">arancione</em> per quelli di vita più breve (livello C). I grigi non sono nella libreria (per lo più i nuclei più leggeri, e alcuni che il motore non riesce a calcolare).</p>
</div>`,
};

Object.assign(WT.L.labels, {
  "neutrons N →": "neutroni N →",
  "protons Z ↑": "protoni Z ↑",
  "Fe: all its isotopes": "Fe: tutti i suoi isotopi",
  "stable": "stabile",
  "lives years": "vive anni",
  "gone in a blink": "sparisce in un lampo",
  "red: Fe (your pick)": "rosso: Fe (la tua scelta)",
  "nickel{#}: most tightly bound": "nichel{#}: il più legato",
  "held most tightly": "il più legato",
  "middle": "intermedio",
  "held least": "il meno legato",
  "red: the A = {#} chain": "rosso: la catena A = {#}",
  "A = {#}: deeper = more tightly bound": "A = {#}: più in basso = più legato",
  "protons Z →": "protoni Z →",
  "measured resonances": "risonanze misurate",
  "tier A": "livello A",
  "tier B": "livello B",
  "tier C": "livello C",
  "not in library": "non in libreria",
});
