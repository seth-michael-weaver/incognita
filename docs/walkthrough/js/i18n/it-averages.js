/* Italian: averages (Capitolo 18, dalle risonanze alle medie) */
WT.L.ch.averages = {
  num: "Capitolo 18", title: "Dalle risonanze alle medie", short: "Dalle risonanze alle medie",
  lead: "Il capitolo 10 ha disegnato scale di risonanze. Qui diventano sezioni d'urto: la formula della matrice R, la statistica dietro i parametri, l'effetto della temperatura e il modo in cui una media su molte risonanze diventa Hauser–Feshbach.",
  html: `
<div class="step">
  <h3>Matrice R, livello per livello</h3>
  <p>In un nucleo pesante, sotto pochi keV, ogni livello del nucleo composto si presenta da solo, e la sezione d'urto si scrive esattamente in termini di parametri dei livelli: energie <i>E</i><sub>λ</sub>, larghezze neutroniche ridotte e larghezze di cattura. Le valutazioni usano la teoria della <b>matrice R</b>, il più delle volte nella forma di <b>Reich–Moore</b>, che conserva l'interferenza fra i livelli nel canale neutronico e tratta i numerosi canali di cattura come un'unica larghezza di assorbimento.</p>
  <div class="formula">R(E) = Σ<sub>λ</sub> γ<sub>λ</sub>² / (E<sub>λ</sub> − E − iΓ<sub>λγ</sub>/2) ,  U = e<sup>−2iφ</sup> (1 + iPR) / (1 − iPR)</div>
  <div class="formula">σ<sub>tot</sub> = (2π/k²) g (1 − Re U) ,  σ<sub>γ</sub> = (π/k²) g (1 − |U|²)</div>
  <div class="btns"><button class="btn ghost" data-act="rm" aria-pressed="true">Reich–Moore</button><button class="btn ghost" data-act="bw" aria-pressed="false">Breit–Wigner a un livello</button></div>
  <p>La linea in alto è la sezione d'urto totale, quella in basso la cattura, per una scala di livelli in onda s su un bersaglio di spin 0, simile all'uranio-238. Fra un livello e l'altro la totale scende sotto la diffusione di potenziale, là dove l'ampiezza di risonanza e quella di potenziale si cancellano. La forma a un livello somma le sezioni d'urto dei livelli invece delle loro ampiezze; è vicina al vero sui picchi e sbagliata nelle valli, dove le code di molti livelli si sommano e la totale può perfino diventare negativa.</p>
</div>
<div class="step">
  <h3>La statistica dietro i parametri</h3>
  <p>Un nucleo non misurato non ha una scala, solo le sue medie: <i>D</i>₀, la funzione di forza <i>S</i>₀ = ⟨Γ<sub>n</sub>⁰⟩/<i>D</i>₀ e ⟨Γ<sub>γ</sub>⟩. La teoria delle matrici aleatorie fornisce il resto: le spaziature dei livelli con lo stesso spin e la stessa parità seguono la distribuzione di Wigner, le larghezze neutroniche ridotte seguono Porter–Thomas, una χ² con un grado di libertà.</p>
  <div class="formula">P(s) = (πs/2) e<sup>−πs²/4</sup> ,  P(y) = e<sup>−y/2</sup> / √(2πy) ,  s = spaziatura/D₀, y = Γ<sub>n</sub>⁰/⟨Γ<sub>n</sub>⁰⟩</div>
  <div class="btns"><button class="btn" data-act="more">Estrai altre dieci scale</button></div>
  <p>Gli istogrammi raccolgono spaziature e larghezze di tutte le scale estratte finora; le curve sono le due leggi. La larghezza di cattura, somma su centinaia di canali fotonici, fluttua appena, quindi si prende fissa.</p>
</div>
<div class="step">
  <h3>Il calore spalma i picchi</h3>
  <p>I nuclei del bersaglio si muovono. Un neutrone di energia <i>E</i> li incontra con una dispersione di energie relative di larghezza Δ = √(4<i>E</i> <i>kT</i>/<i>A</i>), e ogni risonanza è vista attraverso quella dispersione: è l'<b>allargamento Doppler</b>. Per un singolo livello il risultato è la funzione ψ, una lorentziana convoluta con una gaussiana.</p>
  <div class="formula">σ<sub>γ</sub>(E,T) = σ₀ (Γ<sub>γ</sub>/Γ) ψ(x, ξ) ,  x = 2(E − E<sub>λ</sub>)/Γ ,  ξ = Γ/Δ</div>
  <div class="ctl"><label for="av-t">Temperatura (K)</label><input id="av-t" type="range" data-bind="TK" min="0" max="3000" step="10" value="300"><output data-show="TK" data-fmt="0"></output></div>
  <p>La risonanza ingrandita è la più intensa fra le prime della scala; la linea tratteggiata è la sua forma a 0 K. Il calore abbassa il picco e allarga le ali, mentre l'area sotto il picco di cattura resta la stessa. In un campione spesso questo non è neutro: il picco è autoschermato e le ali no, quindi un combustibile più caldo cattura di più. È la retroazione Doppler di un reattore.</p>
</div>
<div class="step">
  <h3>La media è Hauser–Feshbach</h3>
  <p>Mediata su molte risonanze, la cattura diventa una funzione liscia dell'energia. La finestra scorre sulla scala e la sua media viene tracciata man mano; le linee lisce sono il valore di Hauser–Feshbach con le trasmissioni <i>T<sub>n</sub></i> = 2π⟨Γ<sub>n</sub>⟩/<i>D</i> e <i>T<sub>γ</sub></i> = 2π⟨Γ<sub>γ</sub>⟩/<i>D</i>.</p>
  <div class="ctl"><label for="av-w">Larghezza della finestra (livelli)</label><input id="av-w" type="range" data-bind="win" min="2" max="40" step="1" value="12" data-instant><output data-show="win" data-fmt="0"></output></div>
  <div class="btns"><button class="btn ghost" data-act="ladder">Un'altra scala</button></div>
  <p>Una finestra stretta si disperde molto: poche risonanze, larghezze di Porter–Thomas. Una larga si assesta sulla linea inferiore, quella con la correzione per le fluttuazioni delle larghezze. La linea superiore, il prodotto delle medie, è qui troppo alta del 25–47 per cento, soprattutto dove ⟨Γ<sub>n</sub>⟩ è da una a tre volte ⟨Γ<sub>γ</sub>⟩, da circa 100 eV a 1 keV. (Con onde p e più canali aperti la correzione è minore.) Per un solo canale neutronico con larghezze di Porter–Thomas e una larghezza di cattura fissa, il valore corretto è esatto: (2π²/k²<i>D</i>) <i>g</i> ⟨Γ<sub>n</sub>Γ<sub>γ</sub>/Γ⟩.</p>
</div>
<div class="step">
  <h3>Risolta, non risolta, liscia</h3>
  <p>Ciò che una misura risolve dipende dalla sua risoluzione in energia, che peggiora al crescere dell'energia. La linea è la sezione d'urto come la vede uno strumento, allargata da una risoluzione che cresce come <i>E</i><sup>3/2</sup>, come nel tempo di volo. A bassa energia ogni livello sta da solo e i suoi parametri si possono adattare: è la regione delle risonanze risolte. Più in alto i livelli si fondono in una banda fluttuante di cui è nota la statistica ma non i singoli picchi: è la regione non risolta, descritta da parametri medi e, per l'autoschermo, da tabelle di probabilità costruite da scale campionate. Ancora più su subentrano Hauser–Feshbach e il modello ottico.</p>
  <div class="ctl"><label for="av-r">Risoluzione dello strumento (relativa)</label><input id="av-r" type="range" data-bind="res" min="0.2" max="3" step="0.05" value="1"><output data-show="res" data-fmt="2"></output></div>
  <p>La libreria di INCOGNITA non ha ancora una regione delle risonanze risolte. Le sue curve sono medie di Hauser–Feshbach fino alle energie più basse; dove le risonanze misurate sono risolte, la pagina <a href="data.html" data-keep-lang>Ogni nuclide</a> segnala la curva come una media. I parametri di risonanza, e le sezioni d'urto puntuali allargate per effetto Doppler costruite a partire da essi, sono un lavoro in corso.</p>
  <div class="aside">Nel codice: <code>physics/resonance/ladder.py</code> (spaziature da matrici aleatorie, larghezze di Porter–Thomas, sezioni d'urto a un livello, insiemi di scale), <code>ladder_statistics.py</code> (le leggi messe alla prova su scale misurate), <code>compound/wfc.py</code> (la correzione per le fluttuazioni delle larghezze a cui convergono le medie). Le formule di Reich–Moore, ψ–χ e di risoluzione del disegno vengono calcolate qui, con parametri illustrativi simili a quelli dell'uranio-238; il motore di Hauser–Feshbach, e quindi la libreria, non calcola ancora sezioni d'urto nella regione delle risonanze.</div>
</div>`,
};
Object.assign(WT.L.labels, {
  // axes
  "{#} eV": "{#} eV", "{#} keV": "{#} keV",
  // R-matrix
  "potential scattering {#}πR′² ≈ {#} b": "diffusione di potenziale {#}πR′² ≈ {#} b",
  "Reich–Moore (dashed: single-level)": "Reich–Moore (tratteggio: a un livello)",
  "single-level Breit–Wigner (dashed: Reich–Moore)": "Breit–Wigner a un livello (tratteggio: Reich–Moore)",
  "total": "totale", "capture": "cattura",
  // statistics
  "spacings: Wigner": "spaziature: Wigner",
  "reduced neutron widths: Porter–Thomas": "larghezze neutroniche ridotte: Porter–Thomas",
  "s = spacing / D₀": "s = spaziatura / D₀",
  "y = Γn⁰ / ⟨Γn⁰⟩": "y = Γn⁰ / ⟨Γn⁰⟩",
  "{#} ladders · {#} spacings": "{#} scale · {#} spaziature",
  "s = {#}": "s = {#}",
  // Doppler
  "capture near the {#} eV resonance": "cattura vicino alla risonanza a {#} eV",
  "area {#} b·eV ({#} K: {#})": "area {#} b·eV ({#} K: {#})",
  "target nuclei at {#} K": "nuclei del bersaglio a {#} K",
  "target nuclei at rest": "nuclei del bersaglio in quiete",
  // averages
  "Hauser–Feshbach, no correction": "Hauser–Feshbach, senza correzione",
  "with width fluctuations": "con fluttuazioni delle larghezze",
  "average capture cross section": "sezione d'urto media di cattura",
  "{#} levels around {#} eV: {#} b · HF {#} b without, {#} b with the correction": "{#} livelli attorno a {#} eV: {#} b · HF {#} b senza, {#} b con la correzione",
  // resolved / unresolved
  "resolved": "risolta", "unresolved": "non risolta", "averaged": "mediata",
  "capture as measured with finite resolution · dashed: Hauser–Feshbach with fluctuations": "cattura misurata con risoluzione finita · tratteggio: Hauser–Feshbach con fluttuazioni",
  "resolution reaches D₀/{#} at {#} eV": "la risoluzione raggiunge D₀/{#} a {#} eV",
  "resolution reaches D₀/{#} at {#} keV": "la risoluzione raggiunge D₀/{#} a {#} keV",
  "time of flight: the arrival time measures the energy": "tempo di volo: il tempo di arrivo misura l'energia",
});
// labels that carry a cross section printed as "12 b" or "3.4k b", and axis ticks like "10⁻² b"
(function () {
  const L = WT.L.labels, B = ["{#} b", "{#}k b"];
  for (const b of B) {
    L[b] = b;
    for (const b2 of B) {
      L[`{#} eV · total ${b} · capture ${b2}`] = `{#} eV · totale ${b} · cattura ${b2}`;
      L[`Γ = {#} meV · Δ = {#} meV · peak ${b} ({#} K: ${b2})`] = `Γ = {#} meV · Δ = {#} meV · picco ${b} ({#} K: ${b2})`;
    }
  }
  for (const s of ["⁻⁴", "⁻³", "⁻²", "⁻¹", "¹", "²", "³", "⁴", "⁵"]) L[`{#}${s} b`] = `{#}${s} b`;
})();
Object.assign(WT.L.glossary, {
  rMatrix: {
    term: "Teoria della matrice R", aliases: ["matrice R", "teoria della matrice R"],
    short: "La descrizione esatta delle reazioni di risonanza mediante energie dei livelli e larghezze ridotte all'interno di un raggio di canale, raccordata alle onde libere all'esterno.",
    more: "Le valutazioni ne adattano i parametri alle risonanze misurate. Le forme di Breit–Wigner a un livello e a più livelli e quella di Reich–Moore sono approssimazioni della teoria completa.",
    chapter: "averages",
  },
  reichMoore: {
    term: "Reich–Moore", aliases: ["Reich–Moore"],
    short: "L'approssimazione della matrice R usata nella maggior parte delle valutazioni dei nuclei pesanti: i canali neutronici sono trattati in modo esatto, i numerosi canali fotonici come un'unica larghezza di assorbimento per livello.",
    chapter: "averages",
  },
  doppler: {
    term: "Allargamento Doppler", aliases: ["allargamento Doppler", "allargate per effetto Doppler"],
    short: "Lo sbavarsi delle risonanze per effetto del moto termico dei nuclei del bersaglio: il picco si abbassa e le ali si allargano, mentre l'area di un picco isolato resta la stessa.",
    formula: "Δ = √(4 E kT / A)",
    chapter: "averages",
  },
  resolvedRegion: {
    term: "Regioni delle risonanze risolte e non risolte", aliases: ["regione delle risonanze risolte", "regione non risolta"],
    short: "Sotto una certa energia ogni risonanza si misura singolarmente (regione risolta); sopra, se ne conoscono solo i parametri medi (regione non risolta), finché le medie diventano lisce.",
    more: "Nella regione non risolta l'autoschermo si tratta con tabelle di probabilità, distribuzioni della sezione d'urto costruite da scale di risonanze campionate.",
    chapter: "averages",
  },
});
