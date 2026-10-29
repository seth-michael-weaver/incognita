/* Italian: measure (Capitolo 17, osservabili) */
WT.L.ch.measure = {
  num: "Capitolo 17", title: "Osservabili", short: "Osservabili",
  lead: "Un esperimento, un reattore o una stella vedono solo una manciata di numeri. Questo capitolo mostra come il motore trasforma in quei numeri ciò che accade dentro il nucleo.",
  html: `
<div class="step">
  <p>Il disco pallido attorno a ogni nucleo è la sua <b>sezione d'urto</b>: l'area che un neutrone deve colpire perché avvenga una reazione, non la dimensione reale del nucleo. Un fascio arriva da sinistra e attraversa una lamina sottile di nuclei; la frazione che reagisce è quell'area per il numero di nuclei che incontra. L'unità è il barn (10⁻²⁴ cm², circa la sezione di un nucleo di uranio).</p>
  <div class="ctl"><label for="mea-e">Energia del neutrone (MeV)</label><input id="mea-e" type="range" data-bind="E" min="0.1" max="20" step="0.1" value="2"><output data-show="E" data-fmt="1"></output></div>
  <p>Abbassa l'energia e i dischi si gonfiano: un neutrone lento è un'onda ampia e reagisce da più lontano. Ad alta energia il disco si restringe verso il nucleo stesso.</p>
</div>
<div class="step">
  <h3>Funzioni di eccitazione</h3>
  <p>Ogni porta è un'uscita, o <b>canale</b>: il neutrone rimbalza fuori (elastico), lascia il bersaglio eccitato (n′), fa uscire altri neutroni (2n, 3n), viene catturato ed escono solo fotoni (γ), oppure esce al suo posto un protone o una particella α. Una porta col lucchetto ha una <b>soglia</b>: la reazione costa più energia di quella che porta il neutrone.</p>
  <div class="ctl"><label for="mea-e2">Energia del neutrone (MeV)</label><input id="mea-e2" type="range" data-bind="E" min="0.1" max="20" step="0.1" value="2"><output data-show="E" data-fmt="1"></output></div>
  <p>Trascina l'energia oltre una soglia e quella porta si apre con un lampo; i secchi si riempiono secondo la quota di ogni canale, e ogni nuova porta toglie quota alle altre. Le soglie vengono dalle masse dei nuclei; le quote, dalla competizione del capitolo 9.</p>
</div>
<div class="step">
  <h3>Spettri di emissione</h3>
  <p>I due mucchi sono i neutroni che raggiungono la metà anteriore e quella posteriore di un anello di rivelatori, ordinati per energia. Il fascio è pulsato, quindi il tempo di volo di ogni neutrone ne dà l'energia: i veloci arrivano per primi.</p>
  <div class="ctl"><label for="mea-ein">Energia incidente (MeV)</label><input id="mea-ein" type="range" data-bind="Ein" min="5" max="60" step="0.5" value="30"><output data-show="Ein" data-fmt="0"></output></div>
  <p>Entrambi i mucchi hanno una gobba di neutroni lenti, <b>evaporati</b>: escono dal nucleo composto una volta spartita l'energia, ugualmente in tutte le direzioni. Solo il mucchio anteriore ha una lunga coda veloce: neutroni di <b>pre-equilibrio</b>, che escono dai primi urti muovendosi ancora più o meno con il fascio. Aumenta l'energia incidente e la coda cresce.</p>
</div>
<div class="step">
  <h3>Distribuzioni angolari</h3>
  <p>Il petalo mostra quanti neutroni escono in ogni direzione; il fascio arriva da sinistra. I neutroni evaporati hanno dimenticato il fascio ed escono ugualmente in ogni direzione; quelli veloci di pre-equilibrio pendono in avanti. La regola di Kalbach fissa quanto, con un'unica pendenza <i>a</i> che cresce con l'energia di uscita. Il motore può scrivere anche queste distribuzioni angolari, come uscita opzionale.</p>
  <div class="ctl"><label for="mea-eo">Energia di uscita (MeV)</label><input id="mea-eo" type="range" data-bind="Eout" min="1" max="45" step="0.5" value="25"><output data-show="Eout" data-fmt="1"></output></div>
  <p>Abbassa l'energia di uscita e il petalo si arrotonda: i neutroni lenti sono soprattutto evaporati.</p>
  <div class="formula">dσ/dΩ ∝ e<sup>a cos θ</sup></div>
</div>
<div class="step">
  <h3>Sezioni d'urto mediate su Maxwelliana</h3>
  <p>Il mucchio in basso raccoglie le energie dei neutroni catturati nel gas caldo di una stella. Le loro velocità seguono una distribuzione di Maxwell fissata dalla temperatura <i>kT</i> (30 keV sono circa 350 milioni di gradi); le scie più lunghe sono neutroni più veloci, e ogni passaggio vicino a un nucleo può finire in un lampo di cattura.</p>
  <div class="ctl"><label for="mea-kt">Temperatura kT (keV)</label><input id="mea-kt" type="range" data-bind="kT" min="5" max="100" step="1" value="30"><output data-show="kT" data-fmt="0"></output></div>
  <p>I neutroni lenti si catturano facilmente ma passano di rado, e quelli veloci sono pochi, quindi la maggior parte delle catture viene da una finestra larga pochi <i>kT</i>. Il tasso su tutto il gas è la <b>sezione d'urto mediata su una maxwelliana</b> (MACS), in millibarn (mb). Riscalda il gas e la finestra si sposta verso energie più alte, dove il bersaglio è più piccolo. La MACS si ottiene integrando la curva di cattura del motore.</p>
</div>
<div class="step">
  <h3>Bersagli eccitati termicamente</h3>
  <p>Le palline mostrano quale quota dei nuclei bersaglio si trova su ciascuno dei suoi livelli più bassi a questa temperatura. In una stella alcuni bersagli sono già eccitati, e ogni livello eccitato è un ingresso diverso allo stesso nucleo composto. Un livello con spin <i>J</i> ne ospita di più perché ha 2<i>J</i>+1 orientazioni.</p>
  <div class="ctl"><label for="mea-kt2">Temperatura kT (keV)</label><input id="mea-kt2" type="range" data-bind="kT" min="5" max="100" step="1" value="30"><output data-show="kT" data-fmt="0"></output></div>
  <p>Aumenta la temperatura e guarda i nuclei salire. Un tasso stellare calcola la cattura da ogni livello popolato e somma i risultati con queste quote; i pesi sommati danno la funzione di partizione <i>G</i>, e il rapporto con il tasso dallo stato fondamentale è il <b>fattore di incremento stellare</b>. Il motore può farlo come opzione, disattivata per impostazione predefinita; normalmente ogni bersaglio parte dal suo stato fondamentale.</p>
</div>
<div class="step">
  <h3>Incertezze e covarianze</h3>
  <p>Ogni disco tenue è un'esecuzione del motore con i suoi dati d'ingresso spostati a caso: la profondità della buca ottica, la densità dei livelli e la forza fotonica, ciascuna nota solo entro qualche per cento. La dispersione di molte esecuzioni è un'incertezza onesta: il <b>Total Monte Carlo</b>.</p>
  <div class="btns"><button class="btn" data-act="tmc1">Esegui una variante</button><button class="btn ghost" data-act="tmc">Esegui 10</button><button class="btn ghost" data-act="clear">Cancella</button></div>
  <p>Un bordo netto significa che i dati d'ingresso fissano la risposta; un bordo sfumato significa di no, ed è lì che nuove misure aiuterebbero di più.</p>
  <div class="aside">Nel codice: <code>emission/channels.py</code> (canali esclusivi e residui), <code>specout.py</code> e <code>specang.py</code> (spettri in uscita, distribuzioni angolari e sezioni d'urto doppiamente differenziali, scritti solo su richiesta), <code>astro/stellar.py</code> (cattura da livelli del bersaglio popolati termicamente, opzionale), <code>tmc.py</code> (il campionatore Total Monte Carlo). Le MACS dallo stato fondamentale si ottengono dalle curve di cattura in <code>validation/differential/core.py</code>.</div>
</div>`,
};
Object.assign(WT.L.labels, {
  // area
  "each disc: σ ≈ {#} b": "ogni disco: σ ≈ {#} b",
  "each disc: cross section σ ≈ {#} b, the area a neutron must hit": "ogni disco: sezione d'urto σ ≈ {#} b, l'area da colpire",
  "beam →": "fascio →",
  "nucleus's own face ≈ {#} b · {#} % reacts": "sezione del nucleo ≈ {#} b · reagisce il {#} %",
  "the nucleus's own face ≈ {#} b · {#} % of the beam reacts in this foil": "la sezione del nucleo stesso ≈ {#} b · in questa lamina reagisce il {#} % del fascio",
  "slow: the neutron's wave reaches well past the surface": "lento: l'onda del neutrone arriva ben oltre la superficie",
  "the target still looks bigger than the nucleus": "il bersaglio appare ancora più grande del nucleo",
  "fast: close to the nucleus's own size": "veloce: vicino alla dimensione del nucleo",
  // doors
  "elastic": "elastico", "n′ inelastic": "n′ anelastico", "{#}n": "{#}n", "γ capture": "cattura γ", "p": "p", "α": "α", "n′": "n′",
  "{#}n · {#} MeV": "{#}n · {#} MeV", "p · {#} MeV": "p · {#} MeV", "α · {#} MeV": "α · {#} MeV", "n′ inelastic · {#} MeV": "n′ anelastico · {#} MeV",
  "opens at {#} MeV": "si apre a {#} MeV",
  "{#} MeV": "{#} MeV",
  // detect
  "forward half": "metà anteriore", "backward half": "metà posteriore",
  "pulsed beam": "fascio pulsato", "pulsed beam →": "fascio pulsato →",
  "backward": "indietro", "backward detectors": "rivelatori posteriori",
  "forward": "avanti", "forward detectors": "rivelatori anteriori",
  "outgoing neutron energy from the flight time (MeV) →": "energia del neutrone uscente dal tempo di volo (MeV) →",
  "fast tail": "coda veloce", "fast tail: pre-equilibrium": "coda veloce: pre-equilibrio",
  "evaporated hump": "gobba evaporata", "hump: evaporated, every way alike": "gobba: evaporati, uguali in ogni direzione",
  "{#} % leave before the energy is shared": "il {#} % esce prima che l'energia sia spartita",
  // angle
  "beam": "fascio",
  "forward-to-backward ratio ≈ {#}  ·  slope a ≈ {#}": "rapporto avanti/indietro ≈ {#}  ·  pendenza a ≈ {#}",
  "mostly evaporated: every direction alike": "soprattutto evaporati: ogni direzione uguale",
  "a mix: the fast share leans forward": "un misto: la parte veloce pende in avanti",
  "mostly pre-equilibrium: strongly forward": "soprattutto pre-equilibrio: molto in avanti",
  "forward →": "avanti →",
  // star
  "{#} keV": "{#} keV",
  "kT = {#} keV": "kT = {#} keV",
  "energies of captured neutrons": "energie dei neutroni catturati",
  "each capture drops here, by the neutron's energy: the window that counts": "ogni cattura cade qui secondo l'energia del neutrone: la finestra che conta",
  "MACS ≈ {#} mb at kT = {#} keV · captures watched: {#}": "MACS ≈ {#} mb a kT = {#} keV · catture osservate: {#}",
  // hot target
  "{#}⁺  ground state": "{#}⁺  stato fondamentale", "{#}⁺  {#} keV": "{#}⁺  {#} keV",
  "target levels, with the share of nuclei sitting on each": "livelli del bersaglio, con la quota di nuclei su ciascuno",
  "{#} % start from the ground state · partition function G ≈ {#}": "il {#} % parte dallo stato fondamentale · funzione di partizione G ≈ {#}",
  // TMC
  "optical well": "buca ottica", "optical well depth": "profondità della buca ottica",
  "level density": "densità dei livelli", "photon strength": "forza fotonica",
  "σ ≈ {#} b ": "σ ≈ {#} b ", "σ ≈ {#} mb ": "σ ≈ {#} mb ",
  "σ ≈ {#} b ±{#} %": "σ ≈ {#} b ±{#} %", "σ ≈ {#} mb ±{#} %": "σ ≈ {#} mb ±{#} %",
  "dashed: best inputs · each disc drawn at its own scale": "tratteggio: dati migliori · ogni disco nella sua scala",
  "dashed ring: the best-value inputs · each energy drawn at its own scale (disc area ∝ σ)": "anello tratteggiato: i dati di valore migliore · ogni energia nella sua scala (area ∝ σ)",
  "{#} runs of the engine, each with its inputs nudged at random": "{#} esecuzioni del motore, ciascuna con i dati d'ingresso spostati a caso",
});
