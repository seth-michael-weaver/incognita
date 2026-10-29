/* Italian: optical (Capitolo 23, il modello ottico risolto) */
WT.L.ch.optical = {
  num: "Capitolo 23", title: "Il modello ottico, risolto", short: "Modello ottico, risolto",
  lead: "Il capitolo 5 ha disegnato il potenziale ottico come una sfera di cristallo offuscata. Qui lo vediamo come lo usa il motore: una parametrizzazione globale, un'equazione di Schrödinger radiale integrata passo dopo passo e una condizione di raccordo che trasforma l'onda in coefficienti di trasmissione.",
  html: `
<div class="step">
  <h3>Il potenziale di Koning–Delaroche</h3>
  <p>Per neutroni e protoni su bersagli sferici il potenziale predefinito è quello di <b>Koning–Delaroche</b> (KD03): forme di Woods–Saxon le cui profondità variano con continuità con l'energia, con la massa del bersaglio e con il suo eccesso di neutroni, secondo una formula globale oppure, per i nuclei che KD03 ha adattato uno per uno, come il ferro-56, secondo un adattamento locale della stessa forma. La figura usa la formula globale per neutroni sul ferro-56. La buca reale (blu) lega; le parti immaginarie (rosso) assorbono, nel volume e, soprattutto a bassa energia, in un guscio sottile sulla superficie.</p>
  <div class="ctl"><label for="op-e">Energia del neutrone (MeV)</label><input id="op-e" type="range" data-bind="E" min="0.1" max="80" step="0.1" value="5"><output data-show="E" data-fmt="1"></output></div>
  <div class="formula">U(r) = −V<sub>V</sub> f(r) − iW<sub>V</sub> f(r) + 4i a<sub>D</sub>W<sub>D</sub> df<sub>D</sub>/dr + 2(V<sub>so</sub> + iW<sub>so</sub>) (1/r) df<sub>so</sub>/dr ⟨l·σ⟩</div>
  <p>I neutroni sonda attraversano il nucleo all'energia impostata e svaniscono dove l'assorbimento morde: il loro cammino libero medio è ħ<i>v</i>/2|<i>W</i>|. Ogni profondità è funzione di <i>E</i> − <i>E</i><sub>F</sub>, misurata dall'energia di Fermi: la profondità reale cala lentamente, l'assorbimento superficiale <i>W</i><sub>D</sub> ha un massimo vicino a 10 MeV e l'assorbimento di volume <i>W</i><sub>V</sub> cresce con regolarità fino a prevalere, qui sopra circa 45 MeV.</p>
</div>
<div class="step">
  <h3>Integrare l'equazione radiale</h3>
  <p>Ogni onda parziale obbedisce alla propria equazione radiale. Il motore la integra verso l'esterno a partire da <i>r</i> = 0 con il <b>metodo di Numerov</b>, una regola a tre punti accurata fino alla sesta potenza del passo, attraverso l'intero potenziale complesso.</p>
  <div class="formula">u″<sub>lj</sub>(r) = [ l(l+1)/r² + (2μ/ħ²) U<sub>lj</sub>(r) − k² ] u<sub>lj</sub>(r)</div>
  <div class="ctl"><label for="op-l">Onda parziale l</label><input id="op-l" type="range" data-bind="L" min="0" max="10" step="1" value="1" data-instant><output data-show="L" data-fmt="0"></output></div>
  <div class="ctl"><label for="op-e2">Energia del neutrone (MeV)</label><input id="op-e2" type="range" data-bind="E" min="0.1" max="80" step="0.1" value="5"><output data-show="E" data-fmt="1"></output></div>
  <p>La linea continua è l'onda nel tempo, Re[<i>u</i> e<sup>−iωt</sup>]; quella tratteggiata è l'onda libera, come se il nucleo non ci fosse. Dentro la buca l'onda è più corta (il neutrone è più veloce) e più piccola (assorbita); fuori, ritorna sfasata.</p>
</div>
<div class="step">
  <h3>Dall'onda a S e T</h3>
  <p>Oltre circa 12 fm il potenziale si è annullato e l'onda deve essere una combinazione di un'onda libera entrante e di una uscente, <i>u</i> ∝ <i>H</i><sup>−</sup> − <i>S</i> <i>H</i><sup>+</sup>. Il raccordo della <i>u</i> integrata in due raggi fissa l'elemento <i>S<sub>lj</sub></i> della <b>matrice S</b>: l'ampiezza uscente, con la sua fase.</p>
  <div class="btns"><button class="btn ghost" data-act="abs" aria-pressed="false">Spegni l'assorbimento</button></div>
  <div class="formula">S<sub>lj</sub> = η<sub>lj</sub> e<sup>2iδ<sub>lj</sub></sup> ,  T<sub>lj</sub> = 1 − |S<sub>lj</sub>|²</div>
  <p>Il punto è <i>S</i> nel piano complesso, dentro il cerchio unitario; la sua scia è il percorso mentre l'energia va da 0,1 a 40 MeV. Senza assorbimento |<i>S</i>| = 1: il punto corre sul cerchio, l'onda cambia solo fase e <i>T</i> = 0. La distanza all'interno del cerchio è ciò che ricevono il nucleo composto e ogni altra reazione.</p>
</div>
<div class="step">
  <h3>Lo spin–orbita separa j</h3>
  <p>Il termine di <b>spin–orbita</b> è attrattivo per <i>j</i> = <i>l</i> + ½ e repulsivo per <i>j</i> = <i>l</i> − ½. È piccolo, qualche MeV sulla superficie, ma separa le due trasmissioni di ogni <i>l</i>, soprattutto vicino all'onda parziale che sfiora la superficie.</p>
  <div class="ctl"><label for="op-e3">Energia del neutrone (MeV)</label><input id="op-e3" type="range" data-bind="E" min="0.1" max="80" step="0.1" value="5"><output data-show="E" data-fmt="1"></output></div>
  <div class="btns"><button class="btn ghost" data-act="so" aria-pressed="false">Spegni lo spin–orbita</button></div>
  <p>Hauser–Feshbach (capitolo 22) le usa separatamente; sommate con i loro pesi, (<i>l</i>+1)<i>T</i><sub>l,l+½</sub> + <i>l</i> <i>T</i><sub>l,l−½</sub>, danno una sezione d'urto di reazione quasi invariata: per questo le sezioni d'urto totali vincolano poco l'intensità dello spin–orbita e servono dati di polarizzazione.</p>
</div>
<div class="step">
  <h3>Le sezioni d'urto</h3>
  <p>Sommando le onde parziali si ottengono le osservabili su cui il potenziale viene adattato. La sezione d'urto di reazione conta il flusso rimosso, la sezione d'urto totale segue dall'ampiezza in avanti e la loro differenza è la diffusione elastica di forma (shape elastic).</p>
  <div class="formula">σ<sub>R</sub> = (π/k²) Σ<sub>l</sub> [(l+1)T<sub>l,l+½</sub> + l T<sub>l,l−½</sub>] ,  σ<sub>tot</sub> = (2π/k²) Σ<sub>lj</sub> (j+½)(1 − Re S<sub>lj</sub>)</div>
  <div class="ctl"><label for="op-e4">Energia del neutrone (MeV)</label><input id="op-e4" type="range" data-bind="E" min="0.2" max="50" step="0.1" value="5"><output data-show="E" data-fmt="1"></output></div>
  <p>KD03 è stato adattato a dati di questo tipo per molti nuclei, da 1 keV a 200 MeV; la sezione d'urto totale del ferro, fra 3,5 e 4 b a pochi MeV e 2,5 b a 14 MeV, esce entro circa il 5 per cento senza alcun aggiustamento su questo nucleo, compresi i larghi massimi: sono la dimensione del nucleo vista contro la lunghezza d'onda del neutrone.</p>
</div>
<div class="step">
  <h3>L'estremo a bassa energia</h3>
  <p>Sotto qualche keV conta solo l'onda s, e <i>T</i><sub>0</sub> cresce come √<i>E</i>: una pendenza di un mezzo in questo grafico log–log. La costante è la <b>funzione di forza</b> <i>S</i><sub>0</sub> = <i>T</i><sub>0</sub>/(2π√<i>E</i>), con <i>E</i> in eV, la stessa grandezza che le analisi delle risonanze misurano come Σ Γ<sub>n</sub><sup>0</sup>/Δ<i>E</i>.</p>
  <p>Un potenziale globale è adattato soprattutto a energie dell'ordine del MeV, e il suo estremo a bassa energia è il punto più debole. Per il ferro-56 questo dà <i>S</i><sub>0</sub> ≈ 5,5 × 10⁻⁴, e l'adattamento locale di KD03 quasi lo stesso, mentre il valore misurato (RIPL) è 2,3 ± 0,6 × 10⁻⁴: il ferro si trova vicino al picco della risonanza di dimensione 3s intorno ad <i>A</i> ≈ 55, dove <i>S</i><sub>0</sub> è più sensibile al potenziale. Per questo i valori misurati di <i>S</i><sub>0</sub> e <i>S</i><sub>1</sub> sono un dato d'ingresso separato e facoltativo del motore.</p>
  <div class="aside">Nel codice: <code>omp/parameters.py</code> (KD03 e gli altri potenziali globali), <code>omp/potential.py</code> (i fattori di forma radiali), <code>omp/schrodinger.py</code> (integrazione di Numerov e raccordo, con le funzioni coulombiane calcolate con il metodo di Steed per le particelle cariche; sostituisce ECIS per i bersagli sferici ed è verificato rispetto ai T<sub>lj</sub> di ECIS), <code>ecis/</code> (il porting a canali accoppiati per i bersagli deformati), <code>omp/sfunc.py</code> (facoltativo: S₀, S₁ misurati). La figura risolve l'equazione da sé, in modo non relativistico, per neutroni sul ferro-56.</div>
</div>`,
};
Object.assign(WT.L.labels, {
  // axes and units
  "{#} fm": "{#} fm", "{#} MeV": "{#} MeV", "{#} keV": "{#} keV", "{#} eV": "{#} eV", "{#} b": "{#} b",
  "E = {#} MeV": "E = {#} MeV", "T = {#}": "T = {#}", "l": "l",
  // the potential
  "real well, depth {#} MeV": "buca reale, profondità {#} MeV",
  "surface absorption, peak {#} MeV": "assorbimento superficiale, picco {#} MeV",
  "volume absorption {#} MeV": "assorbimento di volume {#} MeV",
  "spin–orbit for l = {#}, j = {#}/{#}: {#} MeV": "spin–orbita per l = {#}, j = {#}/{#}: {#} MeV",
  "mean free path: {#} fm at the surface, {#} fm in the centre": "cammino libero medio: {#} fm sulla superficie, {#} fm al centro",
  "mean free path: {#} fm at the surface, > {#} fm in the centre": "cammino libero medio: {#} fm sulla superficie, > {#} fm al centro",
  "mean free path: > {#} fm at the surface, {#} fm in the centre": "cammino libero medio: > {#} fm sulla superficie, {#} fm al centro",
  "mean free path: > {#} fm at the surface, > {#} fm in the centre": "cammino libero medio: > {#} fm sulla superficie, > {#} fm al centro",
  "real": "reale", "volume": "volume", "surface": "superficie",
  "depths (MeV) against energy (MeV)": "profondità (MeV) in funzione dell'energia (MeV)",
  // the wave
  "potential: real (blue), imaginary (red)": "potenziale: reale (blu), immaginario (rosso)",
  "nuclear surface": "superficie nucleare",
  "l = {#}, j = {#}+½ · E = {#} MeV · |S| = {#} · δ = {#}° · T = {#}": "l = {#}, j = {#}+½ · E = {#} MeV · |S| = {#} · δ = {#}° · T = {#}",
  "solid: the wave now · shaded: its size |u| · dashed: free wave": "continua: l'onda ora · ombreggiato: la sua ampiezza |u| · tratteggio: onda libera",
  // S-matrix
  "Re S": "Re S", "Im S": "Im S",
  "|S| = {#}: nothing absorbed": "|S| = {#}: nulla assorbito",
  "l = {#}, j = {#}+½ · E = {#} MeV": "l = {#}, j = {#}+½ · E = {#} MeV",
  "|S| = {#} · T = {#} − |S|² = {#}": "|S| = {#} · T = {#} − |S|² = {#}",
  "l = {#}, j = {#}+½": "l = {#}, j = {#}+½",
  "|S| = {#}": "|S| = {#}",
  "T = {#} − |S|² = {#}": "T = {#} − |S|² = {#}",
  "trail: S as E runs {#} → {#} MeV": "scia: S mentre E va {#} → {#} MeV",
  "no absorption: S stays on the circle": "nessun assorbimento: S resta sul cerchio",
  // spin-orbit
  "hollow: j = l − ½ · solid: j = l + ½": "vuote: j = l − ½ · piene: j = l + ½",
  "hollow (purple): j = l − ½ · solid (blue): j = l + ½": "vuote (viola): j = l − ½ · piene (blu): j = l + ½",
  "reaction cross section {#} b (without spin–orbit {#} b)": "sezione d'urto di reazione {#} b (senza spin–orbita {#} b)",
  "reaction cross section {#} b (spin–orbit off)": "sezione d'urto di reazione {#} b (spin–orbita spento)",
  "grazing l ≈ kR = {#}": "l radente ≈ kR = {#}",
  // cross sections
  "total {#} b": "totale {#} b", "reaction {#} b": "reazione {#} b", "shape elastic {#} b": "elastica di forma {#} b",
  "n + ⁵⁶Fe, KD{#}, computed here": "n + ⁵⁶Fe, KD{#}, calcolato qui",
  // low energy
  "T₀ (s-wave)": "T₀ (onda s)",
  "T₁ (p-wave, j = {#}/{#}): slope {#}/{#}": "T₁ (onda p, j = {#}/{#}): pendenza {#}/{#}",
  "dashed: {#}πS₀√E, slope ½": "tratteggio: {#}πS₀√E, pendenza ½",
  "S₀ = {#} × {#}⁻⁴ from this potential": "S₀ = {#} × {#}⁻⁴ da questo potenziale",
});
Object.assign(WT.L.glossary, {
  koningDelaroche: {
    term: "Potenziale di Koning–Delaroche", aliases: ["potenziale di Koning–Delaroche", "Koning–Delaroche", "Koning-Delaroche", "KD03"],
    short: "Il potenziale ottico globale per neutroni e protoni di A. J. Koning e J.-P. Delaroche (2003), da 1 keV a 200 MeV e per masse da 24 a 209.",
    more: "Profondità, raggi e diffusività sono funzioni regolari dell'energia, della massa e dell'eccesso di neutroni, adattate una volta per tutte a un ampio insieme di sezioni d'urto e distribuzioni angolari misurate. È il potenziale predefinito per i nucleoni in TALYS e nel motore.",
    chapter: "optical",
  },
  numerov: {
    term: "Metodo di Numerov", aliases: ["metodo di Numerov", "integrazione di Numerov", "Numerov"],
    short: "Una regola a tre punti per integrare equazioni del secondo ordine prive del termine di derivata prima, come l'equazione di Schrödinger radiale, con un errore dell'ordine di h⁶ per passo.",
    formula: "(1 − h²Q_n+1/12) u_n+1 = 2(1 + 5h²Q_n/12) u_n − (1 − h²Q_n−1/12) u_n−1",
    chapter: "optical",
  },
  sMatrix: {
    term: "Matrice S", aliases: ["matrice S", "matrici S"],
    short: "Le ampiezze che collegano onde entranti e uscenti; per la diffusione elastica in un'onda parziale, un solo numero complesso S = η e^(2iδ).",
    more: "|S| = 1 significa che nulla viene assorbito e cambia solo la fase δ; lo scarto 1 − |S|² è il coefficiente di trasmissione, il flusso sottratto verso le reazioni.",
    chapter: "optical",
  },
  spinOrbit: {
    term: "Termine di spin–orbita", aliases: ["termine di spin–orbita", "spin–orbita", "spin-orbita"],
    short: "La parte del potenziale nucleare che dipende dal fatto che lo spin del nucleone sia parallelo o antiparallelo al suo momento angolare orbitale.",
    more: "È attrattivo per j = l + ½ e repulsivo per j = l − ½, con il massimo sulla superficie nucleare. La stessa interazione produce i numeri magici del modello a shell.",
    chapter: "optical",
  },
});
/* attributes referenced in the English chapter script (for the structure check): data-act="${act}" */
