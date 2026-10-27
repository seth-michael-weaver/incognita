/* Italian: hauser (Capitolo 16, Hauser–Feshbach canale per canale) */
WT.L.ch.hauser = {
  num: "Capitolo 16", title: "Hauser–Feshbach, canale per canale", short: "Hauser–Feshbach",
  lead: "Il capitolo 6 ha raccontato la competizione fra le uscite come una serie di porte. Ecco la formula che sta dietro le porte, un canale alla volta, e la correzione che le serve quando i canali aperti sono pochi.",
  html: `
<div class="step">
  <h3>Una trasmissione per ogni canale</h3>
  <p>Un <b>canale</b> è un indirizzo d'uscita completo: quale particella, in quale stato resta il nucleo residuo, il momento angolare orbitale <i>l</i> e il momento totale <i>j</i> = <i>l</i> ± ½ della particella. Il modello ottico del capitolo 2 assegna a ciascuno un <b>coefficiente di trasmissione</b> <i>T<sub>lj</sub></i>. Le colonne sono quelle del neutrone incidente, per un bersaglio di spin 0.</p>
  <div class="ctl"><label for="hf-e">Energia del neutrone (MeV)</label><input id="hf-e" type="range" data-bind="lgE" min="-3" max="0.7" step="0.01" value="-0.3"><output data-show="Eshow" data-fmt="3"></output></div>
  <p>A 1 keV è aperto solo <i>l</i> = 0, con <i>T</i> ≈ 2π<i>S</i><sub>0</sub>√<i>E</i>, qualche per cento. A bassa energia ogni unità in più di <i>l</i> costa circa un fattore (<i>kR</i>)², quindi le colonne si aprono una dopo l'altra al crescere dell'energia. Ogni colonna alimenta il nucleo composto con il peso g<sub>J</sub><i>T</i>:</p>
  <div class="formula">σ<sub>CN</sub> = (π/k²) Σ<sub>J,π</sub> g<sub>J</sub> Σ<sub>lj</sub> T<sub>lj</sub> ,  g<sub>J</sub> = (2J+1) / [(2s+1)(2I+1)]</div>
</div>
<div class="step">
  <h3>Uno spin e una parità alla volta</h3>
  <p>Momento angolare e parità si conservano, quindi il nucleo composto decade in modo indipendente in ogni <i>J</i><sup>π</sup>. Dentro un blocco ogni canale d'uscita aperto compete con il proprio <i>T</i>: l'elastico, che torna allo stato fondamentale; l'anelastico verso ogni livello eccitato (una colonna somma le coppie (<i>l</i>, <i>j</i>) che si accoppiano allo stesso <i>J</i>); il continuo sopra 3,6 MeV, i cui intervalli valgono come tanti canali, pesati con la densità dei livelli; e la cattura, riunita in un unico, minuscolo <i>T</i><sub>γ</sub> = 2π⟨Γ<sub>γ</sub>⟩/<i>D</i>. Le altezze sono in scala logaritmica.</p>
  <div class="ctl"><label for="hf-j">Blocco di spin e parità</label><input id="hf-j" type="range" data-bind="jb" min="0" max="9" step="1" value="2" data-instant><output data-show="jbShow" data-fmt="0"></output></div>
  <div class="ctl"><label for="hf-e2">Energia del neutrone (MeV)</label><input id="hf-e2" type="range" data-bind="lgE" min="-3" max="0.7" step="0.01" value="-0.3"><output data-show="Eshow" data-fmt="3"></output></div>
  <p>La barra in basso è la ripartizione di <b>Hauser–Feshbach</b>: ogni uscita prende la quota <i>T<sub>b</sub></i>/Σ<i>T<sub>c</sub></i> di ciò che è entrato dal canale <i>a</i>. Sotto 0,85 MeV sono aperti solo l'elastico e la cattura, e l'elastico prende quasi tutto.</p>
  <div class="formula">σ<sub>ab</sub> = (π/k²) Σ<sub>J,π</sub> g<sub>J</sub> T<sub>a</sub> T<sub>b</sub> / Σ<sub>c</sub> T<sub>c</sub> · W<sub>ab</sub></div>
</div>
<div class="step">
  <h3>Fluttuazioni delle larghezze</h3>
  <p>Con <i>W<sub>ab</sub></i> = 1 la formula moltiplica delle medie. Ma le risonanze dietro quelle medie hanno larghezze che si disperdono (Porter–Thomas, capitolo 10), e nella diffusione elastica la larghezza che fa entrare il neutrone è la stessa che lo fa uscire: le due sono correlate. Per l'elastico la media dei prodotti supera allora il prodotto delle medie, e le altre uscite perdono ciò che l'elastico guadagna.</p>
  <div class="btns"><button class="btn ghost" data-act="w0" aria-pressed="false">Senza correzione</button><button class="btn ghost" data-act="w1" aria-pressed="true">Moldauer</button></div>
  <div class="ctl"><label for="hf-e3">Energia del neutrone (MeV)</label><input id="hf-e3" type="range" data-bind="lgE" min="-3" max="0.7" step="0.01" value="-0.3"><output data-show="Eshow" data-fmt="3"></output></div>
  <p>I riquadri riportano σ con la correzione divisa per σ senza. Sotto la prima soglia anelastica l'elastico prende già quasi tutto il flusso e cambia appena, mentre la cattura perde dal 10 al 25 per cento. Fra 1 e 1,5 MeV, l'elastico composto guadagna dal 15 al 35 per cento e il primo livello 2⁺ perde circa un terzo. Man mano che si aprono altri livelli e il continuo, l'elastico composto diventa una piccola quota del flusso: il suo fattore sale verso 2, ma ciò che sottrae agli altri si riduce, e i loro fattori tornano verso 1. Nella ricetta di Moldauer ogni canale riceve un numero di gradi di libertà ν<sub>c</sub>, e <i>W</i> è un integrale unidimensionale, calcolato con la regola di Gauss–Laguerre a 32 punti di TALYS.</p>
  <div class="formula">W<sub>ab</sub> = (1 + 2δ<sub>ab</sub>/ν<sub>a</sub>) ∫₀^∞ dx Π<sub>c</sub> (1 + 2T<sub>c</sub>x / ν<sub>c</sub>ΣT)<sup>−(δ<sub>ac</sub>+δ<sub>bc</sub>+ν<sub>c</sub>/2)</sup></div>
  <div class="formula">ν<sub>c</sub> = 1.78 + (T<sub>c</sub><sup>1.212</sup> − 0.78) e<sup>−0.228 ΣT</sup></div>
</div>
<div class="step">
  <h3>Moldauer e HRTW</h3>
  <p>Le curve ripetono lo stesso calcolo su tutto l'intervallo di energia: il rapporto per l'elastico composto, per il primo livello 2⁺ e per la cattura, con Moldauer a tratto continuo e la ricetta <b>HRTW</b> tratteggiata. HRTW sostituisce l'integrale con un fattore elastico <i>W<sub>a</sub></i> e con trasmissioni efficaci <i>V<sub>a</sub></i> trovate per iterazione.</p>
  <div class="ctl"><label for="hf-e4">Energia del neutrone (MeV)</label><input id="hf-e4" type="range" data-bind="lgE" min="-3" max="0.7" step="0.01" value="-0.3"><output data-show="Eshow" data-fmt="3"></output></div>
  <div class="formula">σ<sub>ab</sub> ∝ V<sub>a</sub>V<sub>b</sub> / ΣV<sub>c</sub> · [1 + δ<sub>ab</sub>(W<sub>a</sub> − 1)] ,  V<sub>a</sub> = T<sub>a</sub> / [1 + (W<sub>a</sub> − 1) V<sub>a</sub>/ΣV]</div>
  <p>Le due concordano molto bene per l'elastico e l'anelastico; per la cattura nella regione dei keV HRTW toglie fino al 10 per cento in più. Fra 0,85 e 2 MeV la cattura addirittura guadagna: lì la larghezza totale è dominata da poche larghezze neutroniche fluttuanti, e la media di 1/Γ supera 1/⟨Γ⟩. Entrambe le ricette sono adattamenti al risultato esatto delle matrici aleatorie (GOE), che TALYS offre anche come integrale triplo. INCOGNITA le porta tutte e tre (<code>widthmode</code> 1, 2, 3); quella predefinita è Moldauer, applicata ai neutroni incidenti fino all'energia di separazione del neutrone del bersaglio.</p>
</div>
<div class="step">
  <h3>Fra 3 e 2</h3>
  <p>I casi limite spiegano l'entità dell'effetto. Prendi <i>N</i> canali uguali e niente cattura, e fai variare la loro somma ΣT, che vale 2π volte il rapporto fra la larghezza totale media e la spaziatura dei livelli, Γ/<i>D</i>. Con risonanze isolate (ΣT ≪ 1) e molti canali, ogni larghezza segue Porter–Thomas con un grado di libertà e l'aumento elastico è ⟨Γ<sub>a</sub>²⟩/⟨Γ<sub>a</sub>⟩² = 3. Quando le risonanze si sovrappongono fortemente (ΣT ≫ 2π) la sezione d'urto fluttua come un'onda casuale (fluttuazioni di Ericson) e l'aumento scende a 2.</p>
  <div class="ctl"><label for="hf-n">Canali aperti N</label><input id="hf-n" type="range" data-bind="nch" min="2" max="60" step="1" value="30" data-instant><output data-show="nch" data-fmt="0"></output></div>
  <p>Per <i>N</i> canali isolati il valore esatto è 3<i>N</i>/(<i>N</i>+2) (il rombo): con due soli canali l'aumento non può superare 1,5, perché allora la larghezza totale fluttua quanto quella elastica. La ricetta di Moldauer riproduce questo limite; HRTW resta al di sotto quando sono aperti molti canali deboli. Il riquadro disegna risonanze con la larghezza che corrisponde al punto in movimento. Nella formula di Moldauer il limite a molti canali è 1 + 2/ν: ν → 1 per risonanze isolate, ν → 1,78 quando si sovrappongono (2,12, il piccolo errore dell'adattamento a sovrapposizione completa).</p>
  <div class="aside">Nel codice: <code>compound/prepare.py</code> (i canali d'uscita e le loro trasmissioni per ogni <i>J</i><sup>π</sup>), <code>compound/target.py</code> (le somme di Hauser–Feshbach), <code>compound/wfc.py</code> (Moldauer, HRTW e GOE, portati da TALYS). Il disegno valuta le stesse formule con ingredienti illustrativi: trasmissioni di sfera dura per un bersaglio simile al ferro, sette livelli, un continuo a temperatura costante e un unico canale di cattura riassuntivo.</div>
</div>`,
};
Object.assign(WT.L.labels, {
  // scene 1: incident T_lj
  "T = {#}": "T = {#}",
  "l={#}": "l={#}",
  "hollow: j = l − ½ · solid: j = l + ½": "vuote: j = l − ½ · piene: j = l + ½",
  "compound nucleus": "nucleo composto",
  "compound nucleus · σ(CN) ≈ {#} b": "nucleo composto · σ(CN) ≈ {#} b",
  "σ(CN) ≈ {#} b": "σ(CN) ≈ {#} b",
  "E = {#} MeV · kR = {#}": "E = {#} MeV · kR = {#}",
  "E = {#} keV · kR = {#}": "E = {#} keV · kR = {#}",
  "transmission Tₗⱼ of the incident neutron": "trasmissione Tₗⱼ del neutrone incidente",
  // scene 2: one J^pi block
  "elastic": "elastico", "cont.": "cont.",
  "level energy (MeV) under each column": "energia del livello (MeV) sotto ogni colonna",
  "residual level (energy in MeV) · n×: number of (l, j) channels summed": "livello residuo (energia in MeV) · n×: numero di canali (l, j) sommati",
  "{#}/{#}⁺ block · in through l = {#}, Tₐ = {#}": "blocco {#}/{#}⁺ · ingresso con l = {#}, Tₐ = {#}",
  "{#}/{#}⁻ block · in through l = {#}, Tₐ = {#}": "blocco {#}/{#}⁻ · ingresso con l = {#}, Tₐ = {#}",
  "elastic {#} %": "elastico {#} %",
  "higher {#} %": "superiori {#} %",
  "Hauser–Feshbach split: T / ΣT for each exit": "ripartizione di Hauser–Feshbach: T / ΣT per ogni uscita",
  // scene 3: HF vs WFC
  "compound elastic": "elastico composto",
  "first {#}⁺ level": "primo livello {#}⁺",
  "higher levels": "livelli superiori",
  "capture": "cattura",
  "closed": "chiuso",
  "{#} mb": "{#} mb",
  "with Moldauer's correction": "con la correzione di Moldauer",
  "Hauser–Feshbach without correction": "Hauser–Feshbach senza correzione",
  "compound formation {#} mb at {#} MeV": "formazione del nucleo composto {#} mb a {#} MeV",
  "compound formation {#} mb at {#} keV": "formazione del nucleo composto {#} mb a {#} keV",
  // scene 4: ratio curves
  "{#} keV": "{#} keV", "{#} MeV": "{#} MeV",
  "{#}⁺ opens": "si apre il {#}⁺",
  "continuum": "continuo", "continuum opens": "si apre il continuo",
  "elastic ×{#} (Moldauer) · ×{#} (HRTW)": "elastico ×{#} (Moldauer) · ×{#} (HRTW)",
  "capture ×{#} (Moldauer) · ×{#} (HRTW)": "cattura ×{#} (Moldauer) · ×{#} (HRTW)",
  "first {#}⁺ ×{#} (Moldauer) · ×{#} (HRTW)": "primo {#}⁺ ×{#} (Moldauer) · ×{#} (HRTW)",
  "solid: Moldauer · dashed: HRTW": "continua: Moldauer · tratteggiata: HRTW",
  "σ with correction / σ without": "σ con correzione / σ senza",
  // scene 5: limits
  "ΣT = {#}πΓ/D →": "ΣT = {#}πΓ/D →",
  "elastic enhancement Wₐₐ": "aumento elastico Wₐₐ",
  "T → {#} per channel": "T → {#} per canale",
  "exact, isolated: {#}N/(N+{#}) = {#}": "esatto, isolate: {#}N/(N+{#}) = {#}",
  "Porter–Thomas: {#}": "Porter–Thomas: {#}",
  "Ericson: {#}": "Ericson: {#}",
  "{#} channels · ΣT = {#} · Wₐₐ = {#}": "{#} canali · ΣT = {#} · Wₐₐ = {#}",
  "isolated resonances: Γ ≪ D": "risonanze isolate: Γ ≪ D",
  "resonances begin to overlap": "le risonanze iniziano a sovrapporsi",
  "strongly overlapping: Γ ≫ D": "forte sovrapposizione: Γ ≫ D",
});
Object.assign(WT.L.glossary, {
  hrtw: {
    term: "HRTW", aliases: ["HRTW"],
    short: "Una ricetta per le fluttuazioni delle larghezze dovuta a Hofmann, Richert, Tepel e Weidenmüller: un fattore elastico per canale e trasmissioni efficaci trovate per iterazione.",
    more: "Come quella di Moldauer, è stata adattata a calcoli numerici con matrici aleatorie. TALYS la offre come widthmode 2; Moldauer (1) è la scelta predefinita e l'integrale triplo GOE esatto (3) il riferimento.",
    chapter: "hauser",
  },
  ericson: {
    term: "Fluttuazioni di Ericson", aliases: ["fluttuazioni di Ericson"],
    short: "Fluttuazioni casuali di una sezione d'urto con l'energia quando molte risonanze si sovrappongono, su una scala di energia fissata dalla loro larghezza totale media.",
    more: "Sono il limite di forte sovrapposizione della stessa statistica che, per risonanze isolate, dà le larghezze di Porter–Thomas. In quel limite il fattore di aumento elastico tende a 2.",
    chapter: "hauser",
  },
});
