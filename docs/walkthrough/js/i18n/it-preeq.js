/* Italian: preeq (Capitolo 7, pre-equilibrio) */
WT.L.ch.preeq = {
  num: "Capitolo 7", title: "Urti prima della quiete", short: "Pre-equilibrio",
  lead: "Un neutrone che entra in un nucleo non spartisce la sua energia con tutti in una volta. Durante i primi urti una sola particella ne conserva la maggior parte, e quella particella può schizzare di nuovo fuori. Questo è il pre-equilibrio: emissione “prima che l'energia si distribuisca in modo uniforme”.",
  html: `
<div class="step">
  <p>Due buche, una per i <em class="p">protoni</em> e una per i <em class="n">neutroni</em>. Ogni pallina è un nucleone su un livello di energia, disegnato come un piolo; i pioli sono riempiti dal basso fino alla <b>superficie di Fermi</b>. Un nucleone sopra la linea tratteggiata “libero” ha energia sufficiente per uscire. Il motore segue protoni e neutroni separatamente.</p>
  <p>Il neutrone entrante sta sospeso sopra, con tutta l'energia: la sua più diversi MeV (milioni di elettronvolt) liberati dalla sua cattura.</p>
</div>
<div class="step">
  <h3>Sollevare coppie</h3>
  <p>Ogni urto solleva un nucleone su un piolo vuoto e lascia dietro di sé una <b>lacuna</b> (un anello vuoto). Le particelle sopra la superficie e le lacune sotto di essa si chiamano tutte <b>eccitoni</b>. Il primo urto produce 2 particelle e 1 lacuna (n = 3); ogni urto successivo aggiunge un'altra coppia.</p>
  <div class="btns"><button class="btn" data-act="collide">Urta</button><button class="btn ghost" data-act="reset">Ricomincia</button></div>
  <p>Premi Urta qualche volta. Il nucleone sollevato può essere un protone o un neutrone, e il motore conta ciascun tipo. A ogni coppia l'energia si divide in più parti, quindi la particella più in alto sta più in basso.</p>
</div>
<div class="step">
  <h3>Il bivio a ogni stadio</h3>
  <p>A ogni stadio il neutrone più in alto o sfugge (freccia verso l'alto, solo se è sopra la linea libera) o urta di nuovo (freccia verso il basso); lo spessore indica la probabilità. Il tasso di fuga discende dal <b>bilancio dettagliato</b>: dalla probabilità del processo inverso, che la stessa particella venga assorbita, calcolata nel capitolo 5. Il tasso d'urto è l'intensità di un urto nucleone–nucleone per il numero di nuove configurazioni che può raggiungere.</p>
  <div class="ctl"><label for="pe-n">Stadio (eccitoni n)</label><input id="pe-n" type="range" data-bind="n" min="3" max="11" step="2" value="3" data-instant><output data-show="n" data-fmt="0"></output></div>
  <p>Fai salire lo stadio. All'inizio una particella ha quasi tutta l'energia, quindi ciò che sfugge è veloce. Più tardi l'energia è molto diluita, ed esce poco.</p>
</div>
<div class="step">
  <h3>Da dove viene la coda veloce</h3>
  <p>Il mucchio a destra è lo <b>spettro</b>: quanti neutroni escono a ogni energia, i lenti a sinistra, i veloci a destra. Ogni reazione percorre la catena finché il neutrone più in alto sfugge, e il suo colore dice quando: <em style="font-style:normal;color:var(--warm);font-weight:600">arancione intenso</em> allo stadio 3, più pallido dopo, <em class="n">blu</em> se è uscito solo dopo che il nucleo si è calmato (capitolo 8).</p>
  <div class="btns"><button class="btn" data-act="run">Esegui 300 reazioni</button></div>
  <p>Lo stadio 3 forma un ripiano ampio, quasi piatto, che arriva fino all'energia massima. Gli stadi successivi si accumulano più in basso. La gobba blu è l'<b>evaporazione</b>: quando tutti condividono l'energia, escono solo neutroni lenti, come il vapore da un liquido caldo.</p>
  <div class="ctl"><label for="pe-e">Energia del neutrone</label><input id="pe-e" type="range" data-bind="E" min="5" max="60" step="0.5" value="20"><output data-show="E" data-fmt="1"></output></div>
  <p>Trascina l'energia del neutrone entrante: parte un nuovo gruppo e il ripiano si allunga. L'evaporazione da sola non produce mai neutroni veloci.</p>
</div>
<div class="step">
  <h3>Contare le configurazioni</h3>
  <p>Il contatore scorre ogni modo di mettere particelle su pioli vuoti e lacune su pioli pieni in modo che le loro energie diano in somma l'energia da spartire (qui i pioli distano 1 MeV). I nucleoni sono fermioni: due non possono stare sullo stesso piolo, quindi una particella deve finire su un piolo vuoto e una lacuna si apre solo dove c'era un nucleone. È il <b>blocco di Pauli</b>.</p>
  <div class="ctl"><label for="pe-u">Energia da spartire (MeV)</label><input id="pe-u" type="range" data-bind="U" min="2" max="16" step="1" value="8" data-instant><output data-show="U" data-fmt="0"></output></div>
  <div class="btns"><button class="btn" data-act="addpair">Aggiungi una coppia</button><button class="btn ghost" data-act="droppair">Togli una coppia</button></div>
  <p>Aggiungi una coppia e il conteggio salta in alto; aumenta l'energia e cresce più o meno come <i>E</i><sup>n−1</sup>. Questo conteggio, la <b>densità di stati particella–lacuna</b>, fissa il tasso d'urto: più configurazioni, più destinazioni per un urto. Il motore conta sulla scala vera, con pioli distanti una frazione di MeV, e aggiunge un limite che si vede ad alta energia: una lacuna non può stare sotto il fondo della buca.</p>
</div>
<div class="step">
  <h3>Escono anche i cluster</h3>
  <p>Anche piccoli cluster possono uscire presto. In un <b>pickup</b>, un protone in uscita afferra un neutrone in superficie ed esce con esso come <em class="n">deutone</em>; afferrandone due dà un tritone o un elio-3. In un <b>knockout</b>, il neutrone entrante colpisce una <em class="a">particella alfa</em> (due protoni e due neutroni) già formata vicino alla superficie e la fa uscire. Il motore usa le formule di Kalbach per entrambi.</p>
  <div class="btns"><button class="btn ghost" data-act="pickup">Afferra un neutrone → d</button><button class="btn ghost" data-act="knock">Espelli una α</button></div>
  <p>Premi un pulsante per vederne uno. Entrambi danno a deutoni e alfa le loro code veloci, che cominciano appena sopra l'energia che costa estrarre ciascuno.</p>
</div>
<div class="step">
  <h3>Un secondo veloce</h3>
  <p>Ad alta energia, un secondo nucleone sollevato può trovarsi ancora sopra la linea libera quando il primo neutrone esce, e sfuggire anch'esso, come neutrone o protone veloce. Le buche ripropongono una reazione alla volta, con la scala dell'energia compressa.</p>
  <div class="ctl"><label for="pe-e2">Energia del neutrone</label><input id="pe-e2" type="range" data-bind="E" min="5" max="80" step="0.5" value="40"><output data-show="E" data-fmt="1"></output></div>
  <p>Trascina l'energia. Sotto circa 20 MeV il secondo nucleone supera di rado la linea; sopra, sempre più reazioni emettono due particelle veloci. È il <b>pre-equilibrio multiplo</b>, che il motore include da 20 MeV in su. Ciò che non è uscito diventa il nucleo composto del prossimo capitolo. Sotto pochi MeV (il livello discreto più alto del bersaglio in uso) il motore salta del tutto la catena.</p>
  <div class="aside">Nel codice: <code>preeq/exciton.py</code> (catena di eccitoni a due componenti, tassi d'urto e di fuga), <code>density/particle_hole.py</code> (densità di stati particella–lacuna con correzioni di Pauli e di buca finita), <code>preeq/complex.py</code> (pickup, stripping e knockout α di Kalbach), <code>preeq/multi.py</code> (pre-equilibrio multiplo), <code>compound/normalization.py</code> (passaggio al nucleo composto).</div>
</div>`,
};
Object.assign(WT.L.labels, {
  // wells
  "protons": "protoni",
  "neutrons": "neutroni",
  "Fermi": "Fermi",
  "Fermi surface": "superficie di Fermi",
  "free": "libero",
  "free: can escape": "libero: può uscire",
  "all the energy in one nucleon": "tutta l'energia in un nucleone",
  "{#} particle, {#} holes": "{#} particella, {#} lacune",
  // pairs
  "{#} particle, {#} holes: n = {#}": "{#} particella, {#} lacune: n = {#}",
  "{#} particle, {#} hole: n = {#}": "{#} particella, {#} lacuna: n = {#}",
  "{#} particles, {#} hole: n = {#}": "{#} particelle, {#} lacuna: n = {#}",
  "{#} particles, {#} holes: n = {#}": "{#} particelle, {#} lacune: n = {#}",
  "protons: {#} lifted, {#} hole": "protoni: {#} sollevati, {#} lacuna",
  "protons: {#} lifted, {#} holes": "protoni: {#} sollevati, {#} lacune",
  "neutrons: {#} lifted, {#} hole": "neutroni: {#} sollevati, {#} lacuna",
  "neutrons: {#} lifted, {#} holes": "neutroni: {#} sollevati, {#} lacune",
  "chain ends: the rest becomes a compound nucleus": "fine della catena: il resto diventa un nucleo composto",
  // fork
  "about {#} MeV above surface": "circa {#} MeV sopra la superficie",
  "escapes  {#}%": "sfugge  {#} %",
  "collides again  {#}%": "urta di nuovo  {#} %",
  "below the free line: it cannot leave": "sotto la linea libera: non può uscire",
  "n = {#}: {#} particles, {#} hole, {#} MeV": "n = {#}: {#} particelle, {#} lacuna, {#} MeV",
  "n = {#}: {#} particles, {#} holes, {#} MeV": "n = {#}: {#} particelle, {#} lacune, {#} MeV",
  "stage n = {#}: {#} particles and {#} hole share {#} MeV": "stadio n = {#}: {#} particelle e {#} lacuna si spartiscono {#} MeV",
  "stage n = {#}: {#} particles and {#} holes share {#} MeV": "stadio n = {#}: {#} particelle e {#} lacune si spartiscono {#} MeV",
  // tail
  "max {#} MeV": "max {#} MeV",
  "slow": "lento",
  "fast →": "veloce →",
  "stage {#}": "stadio {#}",
  "chain over: compound": "fine catena: composto",
  "left at:": "uscito a:",
  "neutron left at:": "neutrone uscito a:",
  "evaporation": "evaporazione",
  "{#} of {#} landed · {#} left during the chain": "{#} su {#} arrivati · {#} usciti durante la catena",
  // pauli
  "well bottom: no deeper hole": "fondo della buca: nessuna lacuna più in basso",
  "bottom of the well": "fondo della buca",
  "{#} MeV to share": "{#} MeV da spartire",
  "{#} particles · {#} hole": "{#} particelle · {#} lacuna",
  "{#} particles · {#} holes": "{#} particelle · {#} lacune",
  "ways, all counted": "modi, tutti contati",
  "arrangements so far": "configurazioni finora",
  "one more pair: {#} ways": "una coppia in più: {#} modi",
  "never two on one rung · holes only where a nucleon was": "mai due su un piolo · lacune solo dove c'era un nucleone",
  "(first {#} shown as ticks)": "(le prime {#} come tacche)",
  // cluster
  "a deuteron leaves": "esce un deutone",
  "grabs a neutron at the edge": "afferra un neutrone sul bordo",
  "a fast proton heads out": "un protone veloce sta uscendo",
  "an α ({#} protons + {#} neutrons) waits at the edge": "una α ({#} protoni + {#} neutroni) attende sul bordo",
  "knocked straight out": "espulsa di colpo",
  // second
  "first fast neutron": "primo neutrone veloce",
  "second fast proton": "secondo protone veloce",
  "second fast neutron": "secondo neutrone veloce",
  "below the free line: stays": "sotto la linea libera: resta",
  "below the free line: it stays": "sotto la linea libera: resta",
  "the rest settles: compound nucleus": "il resto si calma: nucleo composto",
  "{#} MeV carried in": "{#} MeV portati dentro",
  "second fast particle in {#} of the last {#} reactions": "seconda particella veloce in {#} delle ultime {#} reazioni",
});
