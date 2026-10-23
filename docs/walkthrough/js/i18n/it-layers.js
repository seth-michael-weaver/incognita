/* Italian: layers (Capitolo 12). The scoreboard counts come from WT.board (js/scoreboard-data.js, loaded first), as in
 * js/ch/layers.js; a missing block or field drops the number, not the sentence. */
(function () {
  const B = WT.board || {};
  const nOf = (v) => (typeof v === "number" && isFinite(v) ? v : null);
  const tally = (o) => {
    if (!o) return null;
    const w = nOf(o.WIN), t = nOf(o.TIE), l = nOf(o.LOSS);
    if (w === null || t === null || l === null) return null;
    return { w, t, l, d: nOf(o.decided) ?? w + t + l };
  };
  const TE = tally(B.incognita), TT = tally(B.terra);
  const LIBS = B.terra && Array.isArray(B.terra.by_rival) ? B.terra.by_rival.map((r) => r && r.rival).filter((s) => typeof s === "string") : [];
  const ASOF = (() => {
    const m = /^(\d{4})-(\d{2})-(\d{2})$/.exec(B.asof || ""); if (!m) return null;
    const mese = ["gennaio", "febbraio", "marzo", "aprile", "maggio", "giugno", "luglio", "agosto", "settembre", "ottobre", "novembre", "dicembre"][+m[2] - 1];
    return mese ? `${+m[3]} ${mese} ${m[1]}` : null;
  })();
  const figs = (T) => (T ? `<div class="figs" aria-label="${T.w} vittorie, ${T.t} pareggi, ${T.l} sconfitte"><div class="w"><b>${T.w}</b><span>vittoria</span></div><div><b>${T.t}</b><span>pareggio</span></div><div class="l"><b>${T.l}</b><span>sconfitta</span></div></div>` : "");
  const libs = LIBS.length ? `le principali librerie di dati valutati (${LIBS.join(", ")})` : "le principali librerie di dati valutati";
  const engineScore = TE ? ` Su ${TE.d} di quei confronti, è nettamente avanti in ${TE.w}, pareggia in ${TE.t} ed è indietro in ${TE.l}.` : "";
  const terraScore = TT ? `Contro ${libs}, è avanti in ${TT.w} confronti su ${TT.d}, pareggia in ${TT.t} ed è indietro in ${TT.l}.` : `Viene confrontato con ${libs}.`;

  WT.L.ch.layers = {
    num: "Capitolo 12", title: "Come è stratificato il modello", short: "Strati",
    lead: "Ciò che forniamo è costruito a strati sopra il motore, e ogni strato deve guadagnarsi il suo posto confrontandosi con le misure.",
    html: `
<div class="step">
  <div class="layer-chip on">In uso</div>
  <h3>Strato 1 · Una regola per ogni nucleo</h3>
  <p>La linea blu è la previsione del motore per una reazione. Il motore è lo strato di base: la stessa fisica e le stesse impostazioni globali per ogni nuclide, mai adattate alle sezioni d'urto su cui viene giudicato.</p>
  <div class="btns"><button class="btn ghost" data-act="reveal" aria-pressed="false">Mostra le misure</button></div>
  <p>Questo lo rende verificabile: viene valutato su misure che non ha mai visto, contro altri codici di modello eseguiti sugli stessi nuclei.${engineScore}</p>
  ${figs(TE)}
</div>
<div class="step">
  <div class="layer-chip null">Provato: ancora nessun guadagno</div>
  <h3>Strato 2 · Le misure proprie di ogni nucleo</h3>
  <p>Questo strato sostituisce la regola globale con i valori misurati di ogni nucleo: la sua spaziatura dei livelli D0, le sue funzioni di forza S0 e S1 (con quale facilità assorbe neutroni lenti), la sua larghezza gamma media ⟨Γγ⟩ e i suoi livelli di energia noti.</p>
  <div class="btns"><button class="btn ghost" data-act="ms0" aria-pressed="true">Regola globale</button><button class="btn ghost" data-act="ms1" aria-pressed="false">Misure proprie</button></div>
  <p>Attivalo e la linea si muove appena. Le prove finora non hanno trovato un guadagno complessivo: l'unica variante che aiuta una reazione vicino alla sua soglia peggiora la cattura neutronica. Per ora quindi questo strato resta disattivato.</p>
</div>
<div class="step">
  <div class="layer-chip cand">Candidato</div>
  <h3>Strato 3 · Seguire i dati buoni (TERRA)</h3>
  <p>Dove una reazione è stata misurata bene, la linea dovrebbe seguire le misure. Il terzo strato, TERRA, fa passare la linea del motore per i dati buoni dove esistono e torna al motore dove mancano.</p>
  <div class="ctl"><label for="lay-cov">Parte dell'intervallo di energia misurata (%)</label><input id="lay-cov" type="range" data-bind="cov" min="0" max="1" step="0.01" value="0.45"><output data-show="covPct" data-fmt="0"></output></div>
  <p>${terraScore} La maggior parte di questi confronti è nel campione: TERRA ha visto quelle misure, come le librerie.</p>
  ${figs(TT)}
</div>
<div class="step">
  <div class="layer-chip wip">In corso</div>
  <h3>Strato 4 · Barre d'errore oneste</h3>
  <p>Lo strato più alto mette attorno alla linea una banda che dovrebbe contenere il valore vero circa due volte su tre (una banda al 68 %): stretta dove i dati buoni la fissano, più larga dove no.</p>
  <div class="ctl"><label for="lay-band">Larghezza della banda · misure dentro (%)</label><input id="lay-band" type="range" data-bind="band" min="0.2" max="2.5" step="0.05" value="1"><output data-show="inside" data-fmt="0"></output></div>
  <p>Trascinala e conta le misure che restano dentro. Troppo stretta, e la banda dichiara una precisione che non ha; troppo larga, e non dice nulla. La banda propria del motore non è ancora adottata: è centrata quando si mettono insieme tutte le reazioni, ma non ancora in ogni famiglia di reazioni. TERRA porta le sue bande, che fanno parte dei suoi confronti qui sopra.</p>
</div>
<div class="step">
  <h3>A che punto siamo</h3>
  <p>Uno strato viene adottato solo dopo essere stato provato contro le misure, e resta disattivato se non aiuta. Oggi il motore è in uso e TERRA è un candidato; lo strato della struttura misurata e la banda di incertezza del motore sono ancora in prova.</p>
  <p><a href="scoreboard.html" data-keep-lang>Vedi la classifica completa →</a> Ogni confronto che non vinciamo, ogni rivale, e come leggerla.</p>
  <div class="aside">${ASOF ? `Punteggi al ${ASOF}, dal` : "Punteggi dal"} registro di ricerca del progetto. Le curve dell'immagine sono illustrative.</div>
</div>`,
  };
})();
Object.assign(WT.L.labels, {
  "{#} · blind engine": "{#} · motore cieco",
  "{#} · measured structure": "{#} · struttura misurata",
  "{#} · TERRA: anchored to data": "{#} · TERRA: ancorato ai dati",
  "{#} · uncertainty band": "{#} · banda di incertezza",
  "measured here": "misurato qui",
  "neutron energy →": "energia del neutrone →",
  "how often the reaction happens": "quanto spesso avviene la reazione",
  "hollow dots: measurements the engine never saw": "punti vuoti: misure mai viste dal motore",
  "own measured values: the line barely moves": "valori misurati propri: la linea si muove appena",
  "global rule": "regola globale",
  "no measurements: TERRA falls back to the engine": "nessuna misura: TERRA torna al motore",
  "solid: follows the data · dashed: the engine alone": "continua: segue i dati · tratteggiata: solo il motore",
  "{#} of {#} measurements inside the band (aim: about {#} %)": "{#} misure su {#} dentro la banda (obiettivo: circa il {#} %)",
  "no measurements to check the band against": "nessuna misura con cui verificare la banda",
});
Object.assign(WT.L.ui, { nav_board: "Classifica" });
