/* Italian: xenon (Lezione 1, avvelenamento da xeno) */
WT.L.ch.xenon = {
  num: "Lezione 1", title: "Avvelenamento da xeno", short: "Xeno",
  html: `
<div class="step">
  <h3>Un veleno prodotto dalla fissione</h3>
  <p>Circa il 6,6 % delle fissioni porta, attraverso lo iodio-135, allo xeno-135: il più forte assorbitore di neutroni conosciuto. Si accumula per circa due giorni, finché i neutroni non lo bruciano e il decadimento non lo elimina con la stessa rapidità con cui si forma. A potenza più alta viene anche bruciato più in fretta, così il livello si satura.</p>
  <div class="ctl"><label for="xe-p1">Potenza (%)</label><input id="xe-p1" type="range" data-bind="P" data-instant min="10" max="100" step="5" value="100"><output data-show="P" data-fmt="0"></output></div>
</div>
<div class="step">
  <h3>Il pozzo di xeno</h3>
  <p>Allo spegnimento la combustione si ferma, ma lo iodio già prodotto continua a trasformarsi in xeno. Il veleno raggiunge il massimo circa nove ore dopo, più di quanto le barre possano restituire, e il reattore non può ripartire; poi si attenua in due o tre giorni.</p>
  <div class="ctl"><label for="xe-th">Ore dallo spegnimento</label><input id="xe-th" type="range" data-bind="th" data-instant min="0" max="72" step="0.5" value="9"><output data-show="th" data-fmt="1"></output></div>
</div>
<div class="step">
  <h3>Spegnere, ripartire</h3>
  <p>Ora tutto scorre dal vivo, tre ore al secondo. Spegni, poi prova a ripartire: dentro il pozzo la ripartenza è rifiutata; più tardi i neutroni bruciano lo xeno. Anche un semplice cambio di potenza fa oscillare lo xeno per ore.</p>
  <div class="ctl"><label for="xe-p3">Potenza (%)</label><input id="xe-p3" type="range" data-bind="P" data-instant min="10" max="100" step="5" value="100"><output data-show="P" data-fmt="0"></output></div>
  <div class="btns"><button class="btn" data-act="xeshut">Spegni</button><button class="btn ghost" data-act="xerestart">Riparti</button></div>
</div>
<div class="step">
  <h3>Oscillazioni di xeno</h3>
  <p>In un nocciolo grande le due metà sono accoppiate solo debolmente. Inserisci le barre da un lato: lì il flusso minore brucia meno xeno, così la potenza si sposta dall'altra parte, poi torna indietro, circa una volta al giorno. Nei noccioli più grandi l'oscillazione cresce, a meno che gli operatori non la smorzino.</p>
  <div class="ctl"><label for="xe-wd">Dimensione del nocciolo (m)</label><input id="xe-wd" type="range" data-bind="wd" data-instant min="1.5" max="3.5" step="0.1" value="3"><output data-show="wd" data-fmt="1"></output></div>
  <div class="btns"><button class="btn" data-act="xepush">Inserisci le barre a sinistra</button></div>
</div>`,
};
/* attributes referenced in the English chapter script (for the structure check): data-act="${act}" */

Object.assign(WT.L.labels, {
  "fission → iodine{#} ({#} h) → xenon{#} ({#} h) → Cs{#}": "fissione → iodio{#} ({#} h) → xeno{#} ({#} h) → Cs{#}",
  "xenon{#} + n → Xe{#}: {#} million barns": "xeno{#} + n → Xe{#}: {#} milioni di barn",
  "fission → iodine{#} ({#} h) → xenon{#} ({#} h) → Cs{#}  ·  Xe{#} swallows neutrons: {#} million barns": "fissione → iodio{#} ({#} h) → xeno{#} ({#} h) → Cs{#}  ·  Xe{#} inghiotte neutroni: {#} milioni di barn",
  "spare reactivity": "riserva di reattività",
  "spare reactivity the rods can give": "riserva di reattività delle barre",
  "{#} h": "{#} h",
  "equilibrium {#} %": "equilibrio {#} %",
  "xenon worth (% of k)": "antireattività dello xeno (% di k)",
  "{#} % power · {#} h after start-up · xenon {#} %": "potenza {#} % · {#} h dall'avvio · xeno {#} %",
  "no restart": "niente ripartenza",
  "too poisoned to restart": "troppo avvelenato per ripartire",
  "shutdown": "spegnimento",
  "drag": "trascina",
  "peak {#} % at {#} h": "picco {#} % a {#} h",
  "{#} h after shutdown · xenon {#} % · restart possible": "{#} h dallo spegnimento · xeno {#} % · ripartenza possibile",
  "{#} h after shutdown · xenon {#} % · cannot restart": "{#} h dallo spegnimento · xeno {#} % · impossibile ripartire",
  "shut down": "spento",
  "refused: more xenon than spare reactivity": "rifiutato: più xeno che riserva di reattività",
  "restarted": "ripartito",
  "tap the core to shut down": "tocca il nocciolo per spegnere",
  "tap the core to restart": "tocca il nocciolo per ripartire",
  "power": "potenza",
  "running at {#} % · xenon {#} %": "in marcia al {#} % · xeno {#} %",
  "shut down · in the pit · xenon {#} %": "spento · nel pozzo · xeno {#} %",
  "shut down · restart possible · xenon {#} %": "spento · ripartenza possibile · xeno {#} %",
  "left {#} %": "sinistra {#} %",
  "right {#} %": "destra {#} %",
  "tap a side to push rods in": "tocca un lato per inserire le barre",
  "more power left": "più potenza a sinistra",
  "more power right": "più potenza a destra",
  "swing period {#} h · {#} m core: the swing dies away": "periodo {#} h · nocciolo di {#} m: l'oscillazione si smorza",
  "swing period {#} h · {#} m core: the swing dies away slowly": "periodo {#} h · nocciolo di {#} m: l'oscillazione si smorza lentamente",
  "swing period {#} h · {#} m core: the swing grows": "periodo {#} h · nocciolo di {#} m: l'oscillazione cresce",
  "{#} m core: push the rods to start a swing": "nocciolo di {#} m: inserisci le barre per avviare un'oscillazione",
  "illustration": "illustrazione",
});
