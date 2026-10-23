/* Italian: structure (Capitolo 1, di che cosa è fatto un nucleo) */
WT.L.ch.structure = {
  num: "Capitolo 1", title: "Di che cosa è fatto un nucleo", short: "Struttura",
  lead: "Prima che il motore (il nostro software di reazioni) lanci un solo neutrone, gli serve una descrizione del nucleo bersaglio: quanto è legato, in quali stati di energia può trovarsi e che forma ha.",
  html: `
<div class="step">
  <p>L'immagine mostra un nucleo di ferro: una palla compatta di <em class="p">protoni</em> e <em class="n">neutroni</em> (<b>nucleoni</b>), tenuti insieme dalla <b>forza forte</b>, a cortissimo raggio. Ogni nucleone sente solo i vicini più prossimi, quindi tutti i nuclei hanno più o meno la stessa densità.</p>
  <div class="ctl"><label for="st-n">Neutroni (il ferro ha 26 protoni)</label><input id="st-n" type="range" data-bind="N" min="24" max="38" step="1" value="30" data-instant><output data-show="N" data-fmt="0"></output></div>
  <p>Trascina per aggiungere o togliere neutroni; ogni scelta è un <b>isotopo</b> diverso. Le barre mostrano l'<b>energia di legame</b> per nucleone in MeV (milioni di elettronvolt): l'energia necessaria per smontare il nucleo. È massima vicino agli isotopi stabili.</p>
</div>
<div class="step">
  <h3>Quanto costa estrarne uno</h3>
  <p>L'energia per estrarre una particella è la sua <b>energia di separazione</b>: <i>S<sub>n</sub></i> per un neutrone, <i>S<sub>p</sub></i> per un protone, <i>S<sub>α</sub></i> per una <b>particella alfa</b> (due protoni e due neutroni legati insieme). L'immagine mostra il nucleo come una buca, con l'energia verso l'alto; ogni estrazione porta la particella più in alto oltre la linea tratteggiata «libera», e il misuratore registra il costo.</p>
  <div class="btns"><button class="btn ghost" data-act="pn">Estrai un neutrone</button><button class="btn ghost" data-act="pp">Estrai un protone</button><button class="btn ghost" data-act="pa">Estrai un'alfa</button></div>
  <p>Il motore ricava ciascuna come differenza tra due masse nucleari: misurate dove possibile, da un modello di masse dove no.</p>
  <div class="ctl"><label for="st-n2">Neutroni</label><input id="st-n2" type="range" data-bind="N" min="24" max="38" step="1" value="30" data-instant><output data-show="N" data-fmt="0"></output></div>
  <p>Trascina il numero di neutroni ed estrai di nuovo un neutrone: <i>S<sub>n</sub></i> va a zigzag, perché i nucleoni si accoppiano e con un numero pari l'ultimo è legato più forte. Una reazione può espellere una particella solo se porta abbastanza energia da pagarne il costo. Questi costi sono le <b>soglie</b> di tutto il calcolo.</p>
</div>
<div class="step">
  <h3>Livelli di energia, e la discesa</h3>
  <p>Un nucleo può contenere solo certe quantità esatte di energia in più: le linee, qui per il ferro-56, con lo <b>stato fondamentale</b> in basso. Ogni livello ha uno <b>spin</b> <i>J</i> (momento angolare) e una <b>parità</b>, + o − (se la sua onda appare uguale in uno specchio); 2<sup>+</sup> significa spin 2, parità +.</p>
  <p>La palla arancione è un nucleo su un livello alto. Scende un livello alla volta, e ogni salto emette un <em class="g">fotone</em> (un raggio gamma) che porta via la differenza di energia. Lo spessore e la percentuale dei percorsi sono le probabilità misurate di ogni salto, i <b>rapporti di diramazione</b>.</p>
  <div class="btns"><button class="btn" data-act="drop">Eccita il nucleo</button></div>
  <p>Premilo qualche volta: lo stesso livello raggiunge lo stato fondamentale per strade diverse. Il motore conserva una trentina di livelli misurati per nucleo, con le loro probabilità; più in alto tratta i livelli affollati come un <b>continuo</b> uniforme. Sopra la linea tratteggiata, <i>S<sub>n</sub></i>, il nucleo può emettere un neutrone.</p>
</div>
<div class="step">
  <h3>Un livello senza una via facile verso il basso</h3>
  <p>Un livello la cui unica via di discesa richiede un grande cambiamento di spin, Δ<i>J</i>, decade molto lentamente. A destra, 64 nuclei stanno su un livello così; ognuno aspetta un tempo casuale, poi scende e salta fuori un <em class="g">fotone</em>. Dopo un <b>tempo di dimezzamento</b> ne è sceso la metà.</p>
  <div class="ctl"><label for="st-dj">Cambiamento di spin ΔJ</label><input id="st-dj" type="range" data-bind="dJ" min="1" max="5" step="1" value="2" data-instant><output data-show="dJ" data-fmt="0"></output></div>
  <div class="ctl"><label for="st-eg">Energia del fotone (MeV)</label><input id="st-eg" type="range" data-bind="Eg" min="0.05" max="1.5" step="0.05" value="0.3"><output data-show="Eg" data-fmt="2"></output></div>
  <div class="btns"><button class="btn ghost" data-act="excite">Eccitali tutti</button></div>
  <p>Aumenta Δ<i>J</i> e i fotoni escono più piano: ogni unità di spin in più rende l'attesa centomila volte più lunga o anche di più, e un'energia del fotone più bassa la allunga ancora (in scala logaritmica). Un livello che vive più di circa un secondo è un <b>isomero</b>, e il motore lo tratta come un punto d'arrivo, come lo stato fondamentale.</p>
</div>
<div class="step">
  <h3>Rotondo, oppure no</h3>
  <p>Molti nuclei non sono rotondi. <i>β₂</i> («beta due») misura l'allungamento: 0 è una sfera, positivo è allungato come un pallone da football americano, negativo è schiacciato come un disco. La scala a destra mostra i livelli che produce ciascun tipo.</p>
  <p>Un nucleo allungato può ruotare, e dà livelli 0<sup>+</sup>, 2<sup>+</sup>, 4<sup>+</sup>, 6<sup>+</sup> con distanze che crescono come <i>J</i>(<i>J</i>+1): un <b>rotore</b>. Uno rotondo può incresparsi; ogni unità di increspatura, un <b>fonone</b>, aggiunge la stessa energia, quindi i suoi livelli sono equidistanti: un <b>vibratore</b>.</p>
  <div class="ctl"><label for="st-beta">Deformazione β₂</label><input id="st-beta" type="range" data-bind="beta" min="-0.3" max="0.45" step="0.01" value="0.28"><output data-show="beta" data-fmt="2"></output></div>
  <div class="btns"><button class="btn ghost" data-act="still">Fermo</button><button class="btn ghost" data-act="vib">Vibrante</button><button class="btn ghost" data-act="rot">Rotante</button></div>
  <p>Trascina <i>β₂</i> e premi i pulsanti: un allungamento maggiore avvicina i livelli del rotore. Il motore conserva le deformazioni nucleo per nucleo e un'etichetta: sferico, vibratore o rotore. Il capitolo 3 mostra come le usa un neutrone di passaggio.</p>
</div>
<div class="step">
  <h3>Impronte appena sopra la soglia</h3>
  <p>Un neutrone lento che si unisce al bersaglio arriva appena sopra <i>S<sub>n</sub></i>, nel riquadro piccolo a sinistra. Il pannello a destra ingrandisce quel riquadro migliaia di volte, con l'energia del neutrone da sinistra a destra.</p>
  <div class="ctl"><label for="st-fe">Energia del fascio</label><input id="st-fe" type="range" data-bind="fe" min="0" max="1" step="0.001" value="0.3" data-instant><output id="st-fe-out"></output></div>
  <div class="btns"><button class="btn ghost" data-act="fplay" id="st-fplay">Metti in pausa la scansione</button></div>
  <p>Alla maggior parte delle energie il fascio passa dritto. A certe energie esatte, il neutrone più il nucleo coincidono con un livello nascosto e buona parte del fascio viene assorbita: una <b>risonanza</b>. Su un picco il nucleo disegnato si gonfia: non è un vero cambiamento di dimensione, ma il bersaglio più grande che il neutrone vede in effetti quando la sua onda si sovrappone a quella del nucleo. Poi il nucleo restituisce l'energia come un <em class="g">fotone</em> o un neutrone. La curva mostra la frazione assorbita; le barre segnano ogni risonanza trovata.</p>
  <div class="btns"><button class="btn ghost" data-act="fFe">Ferro-56</button><button class="btn ghost" data-act="fAu">Oro-197</button><button class="btn ghost" data-act="fU">Uranio-238</button></div>
  <p>Ogni nucleo ha il suo codice a barre, alla sua scala: migliaia di elettronvolt tra le risonanze del ferro, decine per l'oro e l'uranio. Tre medie lo riassumono: <i>D₀</i>, la spaziatura media; ⟨Γ<sub>γ</sub>⟩, la <b>larghezza radiativa</b>, quasi uguale per ogni picco; e <i>S₀</i>, la <b>funzione di forza</b>, con quale facilità entra un neutrone lento.</p>
  <p>Ognuna mette alla prova un passo successivo. I parametri di densità dei livelli del motore sono stati adattati a <i>D₀</i>, nucleo per nucleo; ⟨Γ<sub>γ</sub>⟩ mette alla prova l'emissione di fotoni, <i>S₀</i> il modello ottico del capitolo successivo. Per i nuclei non misurati il motore usa andamenti adattati su molti nuclei.</p>
  <div class="aside">Nel codice: <code>structure/masses.py</code> (masse misurate, masse di modello oltre quelle, energie di separazione), <code>structure/levels.py</code> (livelli discreti, diramazioni, isomeri, spin stimati) e <code>levjpar.py</code> (opzionale, disattivato per impostazione predefinita: stima di nuovo uno spin elencato che è impossibile per il nucleo), <code>structure/deformation.py</code> (β₂ e l'etichetta sferico/vibratore/rotore) e <code>collrule.py</code> (opzionale, disattivato per impostazione predefinita: sceglie l'etichetta del bersaglio in base ai suoi livelli misurati), <code>structure/resonances.py</code> (D₀, S₀, S₁, ⟨Γγ⟩).</div>
</div>`,
};
(function () {
  const L = {
    // scene: packed drop
    "{#}Fe": "{#}Fe",
    "{#} protons · {#} neutrons": "{#} protoni · {#} neutroni",
    "binding energy per nucleon: about {#} MeV": "energia di legame per nucleone: circa {#} MeV",
    "binding per nucleon, one bar per isotope →": "legame per nucleone, una barra per isotopo →",
    // scene: well
    "free": "libera",
    "free: outside the nucleus": "libera: fuori dal nucleo",
    "neutrons": "neutroni",
    "protons": "protoni",
    "an alpha forms from the top pairs": "le coppie in alto formano un'alfa",
    "neutron {#}": "neutrone {#}",
    "proton {#}": "protone {#}",
    "alpha {#}": "alfa {#}",
    "n {#}": "n {#}",
    "p {#}": "p {#}",
    "energy paid": "energia pagata",
    "energy to pull": "energia per estrarre",
    "(MeV)": "(MeV)",
    "each one out (MeV)": "ciascuna (MeV)",
    "higher mark =": "segno più alto =",
    "harder to remove": "più difficile da estrarre",
    "pulling out a neutron: {#} MeV paid": "estrazione di un neutrone: {#} MeV pagati",
    "pulling out a proton: {#} MeV paid": "estrazione di un protone: {#} MeV pagati",
    "pulling out an alpha: {#} MeV paid": "estrazione di un'alfa: {#} MeV pagati",
    // scene: levels and gamma drops
    "continuum: too many levels to list": "continuo: troppi livelli da elencare",
    "neutron threshold Sₙ ≈ {#} MeV": "soglia neutronica Sₙ ≈ {#} MeV",
    "ground state": "stato fondamentale",
    "MeV": "MeV",
    "each line: an energy, a spin J and a parity (±)": "ogni linea: un'energia, uno spin J e una parità (±)",
    "path width and % = measured odds of each hop": "spessore del percorso e % = probabilità misurata di ogni salto",
    // scene: isomer
    "ground": "fondamentale",
    "J = {#}/{#}": "J = {#}/{#}",
    "ΔJ = {#}": "ΔJ = {#}",
    "still excited: {#} of {#}": "ancora eccitati: {#} su {#}",
    "longer than a second: an isomer, a stop in its own right": "più di un secondo: un isomero, una tappa a sé",
    "shown slowed down (log scale)": "mostrato al rallentatore (scala log.)",
    "shown slowed down: the slower they pop, the longer the real wait (log scale)": "al rallentatore: più lenti escono, più lunga è l'attesa reale (scala log.)",
    // scene: shape
    "ripples at the surface: a vibrator": "si increspa in superficie: un vibratore",
    "stretched and rotating: a rotor": "allungato e rotante: un rotore",
    "round: a sphere": "rotondo: una sfera",
    "stretched (prolate): a football": "allungato (prolato): un pallone",
    "squashed: an oblate disc": "schiacciato: un disco oblato",
    "{#} phonons": "{#} fononi",
    "no regular": "nessuno schema",
    "level pattern": "regolare di livelli",
    "spacing grows like J(J+{#})": "la distanza cresce come J(J+{#})",
    "equal steps, one phonon each": "gradini uguali, un fonone ciascuno",
    "its lowest levels": "i suoi livelli più bassi",
    "β₂ = {#}": "β₂ = {#}",
    // scene: resonance fingerprint
    "continuum": "continuo",
    "Sₙ ≈ {#} MeV": "Sₙ ≈ {#} MeV",
    "slow neutron": "neutrone lento",
    "a slow neutron lands here:": "un neutrone lento arriva qui:",
    "lands here": "arriva qui",
    "Sₙ + its kinetic energy": "Sₙ + la sua energia cinetica",
    "×{#} million": "×{#} milioni",
    "×{#} thousand": "×{#} mila",
    "magnified": "ingrandito",
    "swells on a peak: the size the neutron effectively “sees” (waves overlap), not a real size change": "si gonfia su un picco: la dimensione che il neutrone “vede” in effetti (le onde si sovrappongono), non un vero cambiamento di dimensione",
    "share taken in": "frazione assorbita",
    "share of the beam taken in": "frazione del fascio assorbita",
    "{#} (Sₙ)": "{#} (Sₙ)",
    "{#} = exactly Sₙ": "{#} = esattamente Sₙ",
    "{#} keV": "{#} keV",
    "{#} eV": "{#} eV",
    "neutron energy →": "energia del neutrone →",
    "neutron's kinetic energy →": "energia cinetica del neutrone →",
    "D₀ ≈ {#} keV: the average gap": "D₀ ≈ {#} keV: la spaziatura media",
    "D₀ ≈ {#} eV: the average gap": "D₀ ≈ {#} eV: la spaziatura media",
    "S₀: average peak strength": "S₀: intensità media dei picchi",
    "S₀: how strong the peaks are on average (how easily a neutron gets in)": "S₀: intensità media dei picchi (con quale facilità entra un neutrone)",
    "⟨Γγ⟩ ≈ {#} eV: photon width": "⟨Γγ⟩ ≈ {#} eV: larghezza radiativa",
    "⟨Γγ⟩ ≈ {#} eV: photon width, about the same for every peak": "⟨Γγ⟩ ≈ {#} eV: larghezza radiativa, quasi uguale per ogni picco",
    "⟨Γγ⟩ ≈ {#} eV: a hairline here": "⟨Γγ⟩ ≈ {#} eV: qui, un filo",
    "⟨Γγ⟩ ≈ {#} eV: a hairline here; neutrons widen these peaks": "⟨Γγ⟩ ≈ {#} eV: qui, un filo; i neutroni allargano questi picchi",
    "peaks drawn about {#}× wider than life so they show": "picchi disegnati circa {#}× più larghi del vero perché si vedano",
  };
  // beam readout and per-target labels
  for (const u of ["keV", "eV"]) L[`beam of neutrons at {#} ${u}`] = `fascio di neutroni a {#} ${u}`;
  const EL = { iron: ["del ferro", "ferro"], gold: ["dell'oro", "oro"], uranium: ["dell'uranio", "uranio"] };
  for (const en in EL) {
    L[`${en}{#} levels`] = `livelli ${EL[en][0]}{#}`;
    L[`${en}{#}: took in {#} of the last {#}`] = `${EL[en][1]}{#}: ne ha assorbiti {#} degli ultimi {#}`;
  }
  // isomer half-life in every unit fmtTime can produce
  const TU = { femtoseconds: "femtosecondi", picoseconds: "picosecondi", nanoseconds: "nanosecondi", microseconds: "microsecondi",
    milliseconds: "millisecondi", seconds: "secondi", minutes: "minuti", hours: "ore", days: "giorni", years: "anni" };
  for (const en in TU) L[`half-life about {#} ${en}`] = `dimezzamento in circa {#} ${TU[en]}`;
  L["half-life about {#}×{#}^{#} years"] = "dimezzamento in circa {#}×{#}^{#} anni";
  Object.assign(WT.L.labels, L);
})();
