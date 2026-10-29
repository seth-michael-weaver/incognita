/* Italian: strength (Capitolo 25, funzioni di forza fotonica in dettaglio) */
WT.L.ch.strength = {
  num: "Capitolo 25", title: "Forza fotonica, in dettaglio", short: "Forza fotonica",
  lead: "Il capitolo 10 ha mostrato quali fotoni preferisce un nucleo caldo. Questo capitolo scrive le funzioni di forza, le segue fino ai coefficienti di trasmissione e alla larghezza radiativa media, e fa girare la cascata che esse governano.",
  html: `
<div class="step">
  <h3>E1: la coda della risonanza gigante di dipolo</h3>
  <p>La <b>funzione di forza fotonica</b> <i>f<sub>XL</sub></i>(<i>E</i><sub>γ</sub>) è la probabilità ridotta media per un fotone di tipo <i>XL</i>: dipolo elettrico E1, dipolo magnetico M1 e così via. Per E1 è dominata dalla risonanza gigante di dipolo vicino a 18 MeV, ma il decadimento a <i>S<sub>n</sub></i> usa fotoni da 1 a 7 MeV, molto in basso sulla sua coda, e tutta la questione sta nella forma della coda.</p>
  <div class="formula">f<sub>E1</sub> = K σ₀Γ₀ · E<sub>γ</sub> Γ(E<sub>γ</sub>,T) / [(E<sub>γ</sub>² − E₀²)² + E<sub>γ</sub>² Γ(E<sub>γ</sub>,T)²] / (1 − e<sup>−E<sub>γ</sub>/T</sup>) ,  Γ(E<sub>γ</sub>,T) = (Γ₀/E₀)(E<sub>γ</sub> + 4π²T²/E₀)</div>
  <div class="ctl"><label for="ps-t">Temperatura degli stati finali T (MeV)</label><input id="ps-t" type="range" data-bind="T" min="0" max="1.5" step="0.01" value="0.7"><output data-show="T" data-fmt="2"></output></div>
  <p>La linea tratteggiata è la lorentziana standard (SLO), la forma adattata ai dati di fotoassorbimento. Con la sua larghezza costante sovrastima la forza nella finestra del decadimento di un fattore da 2 a 5, un difetto noto da tempo per i nuclei sferici. La linea continua è la lorentziana modificata semplificata (<b>SMLO</b>): la sua larghezza cresce con l'energia del fotone e con la temperatura degli stati finali, il che abbassa la coda nella finestra ma lascia una forza finita a energia del fotone nulla, come richiedono i dati di decadimento. Il riquadro d'ingrandimento mostra quel fondo, sotto 2 MeV: porta <i>T</i> a 0 e scompare.</p>
</div>
<div class="step">
  <h3>M1: spin-flip, forbice, upbend</h3>
  <p>La forza M1 è più debole ma non trascurabile: una risonanza di spin-flip vicino a 41<i>A</i><sup>−1/3</sup> MeV, un modo a forbice vicino a 3 MeV nei nuclei deformati (con forza che cresce come β²) e un upbend, una risalita verso energia del fotone nulla osservata nei dati del metodo di Oslo e nei calcoli a modello a shell.</p>
  <div class="ctl"><label for="ps-b">Deformazione β (forbice)</label><input id="ps-b" type="range" data-bind="beta" min="0" max="0.35" step="0.01" value="0.2"><output data-show="beta" data-fmt="2"></output></div>
  <div class="btns"><button class="btn ghost" data-act="up" aria-pressed="true">Upbend</button></div>
  <p>La linea tenue sullo sfondo è E1. Alle energie del fotone più basse, qui sotto circa 2 MeV, l'upbend permette a M1 di eguagliarla o superarla (il segno mostra dove): per questo conta per l'estremo morbido della cascata e per la cattura lontano dalla stabilità. L'M1 predefinita del motore è la raccomandazione IAEA con upbend, tabulata nucleo per nucleo, e la sua E1 predefinita è la SMLO-2019 tabulata; le forme analitiche usate qui fanno le veci di quelle tabelle.</p>
</div>
<div class="step">
  <h3>Brink–Axel</h3>
  <p>L'<b>ipotesi di Brink–Axel</b> afferma che la forza dipende dall'energia del fotone e non dal punto di partenza del nucleo: la stessa <i>f</i> vale per una risonanza a <i>S<sub>n</sub></i> e per uno stato a 4 MeV. (La SMLO conserva una debole dipendenza attraverso <i>T</i>.) Ogni energia di partenza emette allora con il coefficiente di trasmissione moltiplicato per la densità degli stati finali.</p>
  <div class="formula">T<sub>XL</sub>(E<sub>γ</sub>) = 2π E<sub>γ</sub><sup>2L+1</sup> f<sub>XL</sub>(E<sub>γ</sub>) ,  dΓ/dE<sub>γ</sub> ∝ T<sub>XL</sub>(E<sub>γ</sub>) ρ(E<sub>x</sub> − E<sub>γ</sub>)</div>
  <div class="ctl"><label for="ps-x">Energia di partenza Eₓ (MeV)</label><input id="ps-x" type="range" data-bind="Ex" min="2" max="7.6" step="0.05" value="7.6"><output data-show="Ex" data-fmt="2"></output></div>
  <p>Il prodotto di un <i>E</i><sub>γ</sub>³<i>f</i> crescente e di una ρ decrescente forma una gobba. Partendo da <i>S<sub>n</sub></i>, qui il picco cade fra 4 e 5 MeV. Da partenze più basse la gobba è tagliata all'energia di partenza; sotto l'energia di raccordo, dove ρ è un esponenziale a temperatura costante, la forma è la stessa da ogni partenza, solo troncata. L'ipotesi si verifica confrontando forze estratte a diverse energie di eccitazione, ciò che fanno le analisi di tipo Oslo.</p>
</div>
<div class="step">
  <h3>La larghezza radiativa media</h3>
  <p>Sommando su tutti gli stati finali raggiungibili per E1 o M1 dalle risonanze in onda s (<i>J</i><sup>π</sup> = ½⁺ su un bersaglio di spin 0) si ottiene la loro larghezza fotonica totale media. Si misura, dalle forme delle risonanze, per qualche centinaio di nuclei, ed è la principale verifica della forza a <i>S<sub>n</sub></i>.</p>
  <div class="formula">⟨Γ<sub>γ</sub>⟩ = D₀/2π · Σ<sub>XL</sub> Σ<sub>J′π′</sub> ∫₀^{S<sub>n</sub>} T<sub>XL</sub>(E<sub>γ</sub>) ρ(S<sub>n</sub> − E<sub>γ</sub>, J′, π′) dE<sub>γ</sub></div>
  <div class="ctl"><label for="ps-s">Fattore di scala sulla forza</label><input id="ps-s" type="range" data-bind="scale" min="0.3" max="8" step="0.01" value="1"><output data-show="scale" data-fmt="2"></output></div>
  <p>Le curve mostrano da dove viene la larghezza, fotone per fotone: soprattutto da 3 a 7 MeV, e soprattutto E1, con M1 che aggiunge circa il 15 %. Qui, con forme analitiche e una densità dei livelli schematica al posto delle tabelle del motore, la larghezza risulta circa un sesto dei 0,92 eV misurati: tanto è sensibile alla densità dei livelli sotto <i>S<sub>n</sub></i> e alla coda della forza. Le impostazioni predefinite di TALYS, che il motore segue, danno circa 1,3 eV per questo nucleo. Il cursore applica l'unico fattore complessivo che una valutazione adatterebbe: circa ×6 lo porta nella fascia misurata. La cattura nella regione dei keV è quasi proporzionale a ⟨Γ<sub>γ</sub>⟩ quando Γ<sub>γ</sub> ≪ Γ<sub>n</sub>, quindi un fattore qui è un fattore su (n,γ). TALYS può riscalare la forza su un ⟨Γ<sub>γ</sub>⟩ misurato (<code>gnorm</code>); in INCOGNITA quel riscalamento, applicato a ogni nucleo della cascata, è un'opzione facoltativa, disattivata per impostazione predefinita.</p>
</div>
<div class="step">
  <h3>La cascata</h3>
  <p>Sotto il primo fotone la stessa regola si ripete: da ogni nuova energia il fotone successivo si estrae da <i>T</i>(<i>E</i><sub>γ</sub>) ρ(<i>E<sub>x</sub></i> − <i>E</i><sub>γ</sub>), finché il nucleo raggiunge i suoi livelli noti. Ogni storia conta pochi fotoni; il loro spettro sommato è ciò che vede un calorimetro dopo la cattura.</p>
  <div class="btns"><button class="btn ghost" data-act="up2" aria-pressed="true">Upbend</button><button class="btn ghost" data-act="clear">Ricomincia</button></div>
  <p>L'upbend aggiunge fotoni morbidi e un poco di molteplicità. Il motore non estrae storie: sposta le popolazioni intervallo per intervallo, dall'alto verso il basso (capitolo 11), il che dà le stesse medie senza rumore di campionamento.</p>
  <div class="aside">Nel codice: <code>gamma/strength.py</code> (tutti i modelli di forza supportati da TALYS; predefinite le tabelle SMLO-2019 e la M1 IAEA con upbend), <code>gamma/parameters.py</code> (sistematiche delle risonanze giganti, tabelle), <code>gamma/transmission.py</code> (T = 2π E<sup>2L+1</sup> f), <code>gamma/ggnorm.py</code> (normalizzazione facoltativa su ⟨Γγ⟩), <code>emission/</code> (la cascata). Il disegno usa forme analitiche e sistematiche per un nucleo simile al ferro-57; il ⟨Γγ⟩ misurato è il valore RIPL per il ⁵⁷Fe.</div>
</div>`,
};
Object.assign(WT.L.labels, {
  "Eγ (MeV)": "Eγ (MeV)", "Sₙ": "Sₙ",
  // E1
  "E{#} strength f (MeV⁻³), A = {#}": "forza E{#} f (MeV⁻³), A = {#}",
  "photons that decay uses": "fotoni usati nel decadimento",
  "GDR: E₀ = {#} MeV, Γ₀ = {#} MeV, σ₀ = {#} mb": "GDR: E₀ = {#} MeV, Γ₀ = {#} MeV, σ₀ = {#} mb",
  "dashed: SLO": "tratteggio: SLO",
  "at {#} MeV: SMLO / SLO = {#}": "a {#} MeV: SMLO / SLO = {#}",
  "protons against neutrons": "protoni contro neutroni",
  // M1
  "M{#} strength f (MeV⁻³), A = {#}": "forza M{#} f (MeV⁻³), A = {#}",
  "spin-flip": "spin-flip",
  "scissors, β = {#}": "forbice, β = {#}",
  "upbend": "upbend",
  "faint: E{#} at T = {#} MeV": "tenue: E{#} a T = {#} MeV",
  "M{#} > E{#} below {#} MeV": "M{#} > E{#} sotto {#} MeV",
  "E{#} dominates at every energy here": "qui E{#} domina a ogni energia",
  "scissors: the two deformed clouds rock": "forbice: le due nubi deformate oscillano",
  // Brink-Axel
  "from {#} MeV": "da {#} MeV",
  "peak at Eγ ≈ {#} MeV": "picco a Eγ ≈ {#} MeV",
  "primary spectrum T(Eγ) ρ(Eₓ − Eγ), each scaled to its peak": "spettro primario T(Eγ) ρ(Eₓ − Eγ), ciascuno normalizzato al suo picco",
  // radiative width
  "contribution to ⟨Γγ⟩ per MeV of photon energy: E{#} (yellow), M{#} (purple, on top)": "contributo a ⟨Γγ⟩ per MeV di energia del fotone: E{#} (giallo), M{#} (viola, sopra)",
  "{#} eV": "{#} eV",
  "measured {#} eV": "misurato {#} eV",
  "computed ⟨Γγ⟩ = {#} meV (E{#} {#} %, M{#} {#} %)": "⟨Γγ⟩ calcolato = {#} meV (E{#} {#} %, M{#} {#} %)",
  // cascade
  "all photons from all cascades": "tutti i fotoni di tutte le cascate",
  "{#} cascades · mean multiplicity {#}": "{#} cascate · molteplicità media {#}",
});
Object.assign(WT.L.glossary, {
  smlo: {
    term: "SMLO", aliases: ["SMLO"],
    short: "La lorentziana modificata semplificata: una funzione di forza E1 la cui larghezza cresce con l'energia del fotone e con la temperatura degli stati finali.",
    more: "Proposta da V. Plujko e collaboratori, e tabulata per ogni nucleo nella banca dati IAEA delle funzioni di forza fotonica (2019). La E1 predefinita del motore, come quella di TALYS-2, è questa tabella SMLO-2019.",
    chapter: "strength",
  },
  brinkAxel: {
    term: "Ipotesi di Brink–Axel", aliases: ["ipotesi di Brink–Axel", "Brink–Axel"],
    short: "L'assunzione che la funzione di forza fotonica dipenda solo dall'energia del fotone e non dall'energia di eccitazione dello stato che lo emette.",
    more: "Permette a un'unica forza, misurata o calcolata per lo stato fondamentale, di servire l'intera cascata. Si verifica estraendo le forze a diverse energie di eccitazione; vale in modo approssimato, con deviazioni dibattute per nuclei ed energie particolari.",
    chapter: "strength",
  },
});
/* attributes referenced in the English chapter script (for the structure check): data-act="up" data-act="up2" */

Object.assign(WT.L.labels, {
  "zoom: Eγ from {#} to {#} MeV": "zoom: Eγ da {#} a {#} MeV",
  "floor: stays above zero": "pavimento: resta sopra zero",
  "continuum:": "continuo:",
  "dark = dense": "scuro = denso",
  "known levels": "livelli noti",
});
