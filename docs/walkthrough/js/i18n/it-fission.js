/* Italian: fission (Capitolo 12, fissione) */
WT.L.ch.fission = {
  num: "Capitolo 12", title: "Fissione", short: "Fissione",
  lead: "I nuclei più pesanti hanno un'uscita che a quelli leggeri manca: invece di espellere una particella, l'intero nucleo si strappa in due. Questa è la fissione.",
  html: `
<div class="step">
  <p>Un nucleo pesante si comporta come una goccia di liquido carico. La tensione superficiale (frecce grigie) la tiene rotonda; i protoni, tutti con carica positiva, la spingono a separarsi (frecce rosse). Nell'uranio le due forze quasi si equilibrano.</p>
  <div class="ctl"><label for="fis-d">Allunga la goccia</label><input id="fis-d" type="range" data-bind="def" min="0" max="1" step="0.01" value="0"><output data-show="def" data-fmt="2"></output></div>
  <p>Trascina per allungarla e guarda il punto sulla piccola curva di energia qui sotto. Allungarla aggiunge superficie, il che costa energia, ma distribuisce la carica, il che libera energia. Oltre la cima della curva vince la carica: si forma un collo e le due metà volano via con circa 200 MeV.</p>
</div>
<div class="step">
  <h3>La superficie di energia potenziale</h3>
  <p>La curva è l'energia per ogni forma, da rotonda (a sinistra) a spezzata (a destra). Una goccia liquida liscia dà una sola collina, ma i nucleoni riempiono i livelli di energia a gruppi, chiamati <b>shell</b>, e negli elementi più pesanti questo scava una buca nella collina: una <b>barriera a doppia gobba</b>, dove il nucleo può indugiare in una forma allungata.</p>
  <p>Il motore non dà per scontata questa curva: la legge punto per punto da un calcolo microscopico dell'energia a ogni deformazione (grado di allungamento).</p>
</div>
<div class="step">
  <h3>Penetrazione della barriera</h3>
  <p>La palla è il nucleo eccitato nella prima valle, all'energia di eccitazione della linea tratteggiata arancione, sotto la cima di 6 MeV. Secondo la fisica classica non può mai passare; la meccanica quantistica le permette di attraversare per <b>effetto tunnel</b> la parte più scura e proibita, con una probabilità <i>T</i> che cala esponenzialmente man mano che quella parte si ispessisce.</p>
  <div class="ctl"><label for="fis-e">Energia di eccitazione</label><input id="fis-e" type="range" data-bind="E" min="3" max="8" step="0.05" value="5"><output data-show="E" data-fmt="2"></output></div>
  <p>Aumenta l'energia e guarda <i>T</i> crescere mentre la parte proibita si assottiglia. La scorciatoia dei libri di testo (Hill–Wheeler) tratta la cima come una parabola (blu tratteggiata). Il motore segue la forma reale, più larga in basso, quindi molto sotto la cima la sua probabilità è minore. <i>K</i> misura quanta collina c'è di mezzo.</p>
  <div class="formula">T = 1 / (1 + e<sup>2K</sup>),  K = ∫ √(2μ(V−E)) dβ / ħ</div>
</div>
<div class="step">
  <h3>Stati di transizione</h3>
  <p>Le porte sulla cima sono gli <b>stati di transizione</b>, gli stati quantistici del nucleo allungato sopra la barriera. Ciascuno ha uno spin e una parità (0⁺, 2⁻, …) e fa da cancello; il suo varco illuminato mostra quanto è aperto. Un nucleo passa solo attraverso i cancelli con il suo stesso spin e la sua stessa parità, e ciascuno si apre gradualmente man mano che l'energia ne supera l'altezza.</p>
  <div class="ctl"><label for="fis-e2">Energia di eccitazione</label><input id="fis-e2" type="range" data-bind="E" min="3" max="8" step="0.05" value="5"><output data-show="E" data-fmt="2"></output></div>
  <div class="btns"><button class="btn ghost" data-act="jpAll">Qualsiasi spin</button><button class="btn ghost" data-act="jp0">Composto 0⁺</button><button class="btn ghost" data-act="jp1">Composto 1⁻</button></div>
  <p>Scegli uno spin e una parità: contano solo i cancelli corrispondenti, e l'apertura totale cala. Più in alto i cancelli si affollano in un <b>continuo</b>, e il motore li conta in base alla loro densità, come fa con i livelli ordinari.</p>
</div>
<div class="step">
  <h3>Barriere a doppia gobba</h3>
  <p>Ora entrambe le colline, ciascuna con un cancello (il cerchio; la parte piena indica quanto è aperto). I nuclei arrivano da sinistra; quelli che superano la prima collina restano intrappolati nella buca, rimbalzando fra i cancelli finché escono da una parte o dall'altra. Le probabilità si combinano come resistenze in serie, quindi a decidere è soprattutto la collina più difficile.</p>
  <div class="ctl"><label for="fis-b">Altezza della collina esterna</label><input id="fis-b" type="range" data-bind="Bb" min="3.5" max="7.5" step="0.05" value="5.6"><output data-show="Bb" data-fmt="2"></output></div>
  <div class="formula">1/T = 1/T<sub>A</sub> + 1/T<sub>B</sub></div>
  <p>Alza la collina esterna e guarda il flusso verso la fissione strozzarsi, per quanto aperto sia il cancello interno.</p>
</div>
<div class="step">
  <h3>Fissione a più possibilità</h3>
  <p>L'uranio-238 assorbe il neutrone e diventa uranio-239 con eccitazione <i>E</i>* (linea tratteggiata). Se non si spezza, può invece emettere un neutrone; la linea scende, e l'uranio-238 che resta, ancora caldo, tenta la propria barriera: fissione di <b>seconda possibilità</b>, (n,n′f). I mucchi raccolgono come è finito ogni nucleo.</p>
  <div class="ctl"><label for="fis-en">Energia del neutrone</label><input id="fis-en" type="range" data-bind="En" min="0" max="25" step="0.1" value="7"><output data-show="En" data-fmt="1"></output></div>
  <p>Aumenta l'energia e i tentativi successivi cominciano a riuscire; una terza possibilità si apre vicino a 12 MeV. Ogni nuova possibilità appare come un gradino nella <b>sezione d'urto di fissione</b> misurata, quanto è probabile che il nucleo si spezzi: il piccolo grafico in alto a destra disegna quei gradini, con la tua energia segnata. Il motore calcola quanto spesso si spezza, non in quali frammenti.</p>
  <div class="aside">Nel codice: <code>fission/wkb.py</code> (il cammino dell'energia di deformazione e gli integrali WKB), <code>fission/barriers.py</code> (Hill–Wheeler, stati di transizione, la densità dei livelli sulla barriera), <code>fission/transmission.py</code> (gobbe in serie, T<sub>fis</sub> per spin e parità), <code>fission/chain.py</code> (barriere per ogni nucleo della cascata).</div>
</div>`,
};
Object.assign(WT.L.labels, {
  // drop
  "surface tension pulls it round": "la tensione superficiale la arrotonda",
  "the protons push it apart": "i protoni la spingono a separarsi",
  "a charged drop, nearly round": "una goccia carica, quasi rotonda",
  "stretched: more surface, charge further apart": "allungata: più superficie, carica più distante",
  "a neck forms": "si forma un collo",
  "two fragments, carrying about {#} MeV": "due frammenti, con circa {#} MeV",
  "energy of the drop": "energia della goccia",
  // landscape
  "ground state": "stato fondamentale", "inner barrier": "barriera interna", "second well": "seconda buca",
  "outer barrier": "barriera esterna", "split (scission)": "spezzata (scissione)", "one smooth hill": "una sola collina liscia",
  "shell effects carving the second well": "gli effetti di shell scavano la seconda buca",
  "round → stretched → necked → split": "rotonda → allungata → con collo → spezzata",
  "stretch (deformation) →": "allungamento (deformazione) →",
  // tunnel
  "forbidden zone": "zona proibita",
  "excitation {#} MeV": "eccitazione {#} MeV",
  "hilltop {#} MeV": "cima {#} MeV",
  "parabola fit": "parabola approssimante",
  "passes over the top": "passa sopra la cima",
  // gates
  "continuum: a density": "continuo: una densità",
  "continuum of gates: counted as a density": "continuo di cancelli: contato come densità",
  "gates: transition states": "cancelli: stati di transizione",
  "E = {#} MeV": "E = {#} MeV",
  "all gates: total opening {#}": "tutti i cancelli: apertura totale {#}",
  "all gates: total opening {#} + {#} from the continuum": "tutti i cancelli: apertura totale {#} + {#} dal continuo",
  "{#}⁺ gates only: total opening {#}": "solo cancelli {#}⁺: apertura totale {#}",
  "{#}⁺ gates only: total opening {#} + {#} from the continuum": "solo cancelli {#}⁺: apertura totale {#} + {#} dal continuo",
  "{#}⁻ gates only: total opening {#}": "solo cancelli {#}⁻: apertura totale {#}",
  "{#}⁻ gates only: total opening {#} + {#} from the continuum": "solo cancelli {#}⁻: apertura totale {#} + {#} dal continuo",
  // series
  "nuclei arriving →": "nuclei in arrivo →",
  "trapped in the well": "intrappolati nella buca",
  "fission": "fissione",
  "so far: {#} through, {#} turned back": "finora: {#} passati, {#} respinti",
  // chance
  "²³⁹U*  E* = {#} MeV": "²³⁹U*  E* = {#} MeV", "²³⁸U*  E* = {#} MeV": "²³⁸U*  E* = {#} MeV", "²³⁷U*  E* = {#} MeV": "²³⁷U*  E* = {#} MeV",
  "↑ E* above the picture": "↑ E* sopra l'immagine",
  "fission!": "fissione!",
  "emits a neutron, cools, tries again": "emette un neutrone, si raffredda, riprova",
  "too cool to split: a photon, no fission": "troppo freddo per spezzarsi: un fotone, niente fissione",
  "attempt {#}: barrier {#} % open": "tentativo {#}: barriera aperta al {#} %",
  "{#}st chance (n,f)": "{#}ª possibilità (n,f)", "{#}nd chance (n,n′f)": "{#}ª possibilità (n,n′f)", "{#}rd chance (n,{#}nf)": "{#}ª possibilità (n,{#}nf)",
  "{#}st (n,f)": "{#}ª (n,f)", "{#}nd (n,n′f)": "{#}ª (n,n′f)", "{#}rd (n,{#}nf)": "{#}ª (n,{#}nf)",
  "no fission": "niente fissione",
});
// labels carrying a transmission T, printed either as 0.12 or as 3.4·10⁻5 (two number shapes)
(function () {
  const L = WT.L.labels, F = ["{#}", "{#}·{#}⁻{#}"];
  for (const a of F) {
    L[`inner gate T ≈ ${a}`] = `cancello interno T ≈ ${a}`;
    L[`outer gate T ≈ ${a}`] = `cancello esterno T ≈ ${a}`;
    L[`both hills: T ≈ ${a}, {#} % of what arrives gets through`] = `entrambe le colline: T ≈ ${a}, passa il {#} % di ciò che arriva`;
    for (const b of F) {
      L[`T ≈ ${a} real shape · ${b} parabola`] = `T ≈ ${a} forma reale · ${b} parabola`;
      L[`chance to tunnel T ≈ ${a} on the real shape, ${b} on the parabola`] = `probabilità di tunnel T ≈ ${a} con la forma reale, ${b} con la parabola`;
    }
  }
})();
