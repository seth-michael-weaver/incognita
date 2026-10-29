/* Italian: gamma (Capitolo 10, emissione di fotoni) */
WT.L.ch.gamma = {
  num: "Capitolo 10", title: "Emissione di raggi gamma", short: "Fotoni",
  lead: "Quando nessuna particella esce, il nucleo si raffredda emettendo fotoni: raggi gamma, particelle di luce ad alta energia. Questa uscita è aperta a qualsiasi energia.",
  html: `
<div class="step">
  <p>Uno stato caldo a 8 MeV (milioni di elettronvolt) emette fotoni (γ); il mucchio accanto alla scala raccoglie dove arrivano. Sotto 2 MeV gli stati sono pochi pioli con un nome; sopra, una folla che si infittisce rapidamente con l'energia (punti grigi). Ogni fotone porta via l'energia del suo salto, <i>E<sub>γ</sub></i>, ed è disegnato più luminoso in proporzione a <i>E<sub>γ</sub></i>³.</p>
  <div class="formula">T<sub>γ</sub>(E<sub>γ</sub>) = 2π · E<sub>γ</sub><sup>2l+1</sup> · f(E<sub>γ</sub>)</div>
  <p>In parole: la facilità con cui un fotone di energia <i>E<sub>γ</sub></i> esce (<i>T<sub>γ</sub></i>, la porta del fotone del capitolo 9) cresce come <i>E<sub>γ</sub></i>³ per il tipo comune di fotone (dipolo, <i>l</i> = 1), moltiplicata per la <b>funzione di forza fotonica</b> <i>f</i>: con quale facilità questo nucleo irraggia a quell'energia. Poi deve trovare uno stato in cui atterrare. I salti piccoli hanno una folla di stati in attesa ma escono a stento; quelli grandi escono con facilità ma trovano pochi stati. I vincitori stanno nel mezzo.</p>
  <div class="ctl"><label for="gm-e0">Energia iniziale</label><input id="gm-e0" type="range" data-bind="E0" min="3" max="9" step="0.5" value="8"><output data-show="E0" data-fmt="1"></output></div>
  <div class="btns"><button class="btn" data-act="emit">Emetti 100</button></div>
  <p>Il mucchio ha il massimo qualche MeV sotto il punto di partenza: la maggior parte dei fotoni porta da 2 a 4 MeV. Sposta l'energia iniziale e il massimo la segue.</p>
</div>
<div class="step">
  <h3>La risonanza gigante di dipolo</h3>
  <p>Il grande picco a destra è la <b>risonanza gigante di dipolo</b>: tutti i protoni (tratteggiati) che oscillano avanti e indietro contro tutti i neutroni (pieni). La sua frequenza fissa l'energia di fotone che il nucleo assorbe ed emette più facilmente. La curva è la funzione di forza fotonica <i>f</i>, in scala logaritmica (ogni gradino in su vale dieci volte di più).</p>
  <div class="ctl"><label for="gm-a">Numero di massa A</label><input id="gm-a" type="range" data-bind="A" min="40" max="240" step="1" value="112"><output data-show="A" data-fmt="0"></output></div>
  <p>Trascina il numero di massa A (protoni più neutroni): i nuclei pesanti oscillano più lentamente e risuonano verso 12–14 MeV; quelli leggeri vicino a 20. Un nucleo che decade emette fotoni di pochi MeV, quindi ciò che conta di più è la coda ombreggiata a bassa energia.</p>
</div>
<div class="step">
  <h3>Forza magnetica a bassa energia</h3>
  <p>Un nucleo deformato irraggia anche in modo magnetico: i suoi protoni (tratteggiati) e i suoi neutroni (pieni), due palloni da rugby, oscillano l'uno contro l'altro come le lame di una forbice. Questo <b>modo a forbice</b> sta vicino a 3 MeV. Lo <b>spin-flip</b>, vicino a 8 MeV, è dato da singoli nucleoni che invertono il loro spin (le frecce piccole), con qualsiasi forma.</p>
  <div class="ctl"><label for="gm-b">Deformazione β₂</label><input id="gm-b" type="range" data-bind="beta" min="0" max="0.35" step="0.01" value="0.25"><output data-show="beta" data-fmt="2"></output></div>
  <p>Trascina la deformazione β₂ (0 è una sfera). Più il nucleo è allungato, più fotoni a forbice escono; una sfera non ne ha. Alle energie più basse la forza risale: è l'<b>upbend</b>, uno stillicidio di fotoni soffici, che il motore indebolisce man mano che il nucleo si deforma. Un'opzione, disattivata per impostazione predefinita, usa sistematiche della forbice più intense che concordano con le misure di Oslo (da quattro a cinque volte più intense nell'uranio).</p>
</div>
<div class="step">
  <h3>Cascate gamma</h3>
  <p>Una cascata è una serie di fotoni emessi uno dopo l'altro, dagli intervalli in alto (stati troppo fitti per elencarli, capitolo 8) fino ai livelli con un nome, allargati perché si possano leggere (piolo pieno parità +, vuoto −). Lì il motore smette di stimare e segue i <b>rapporti di diramazione</b> tabulati: le probabilità misurate che ogni livello decada verso ciascuno di quelli più bassi.</p>
  <div class="btns"><button class="btn" data-act="drop">Fai partire una cascata</button></div>
  <p>Premi il pulsante qualche volta: la parte alta cambia ogni volta; il finale segue uno di pochi percorsi misurati.</p>
</div>
<div class="step">
  <h3>Produzione di isomeri</h3>
  <p>Il livello 11/2− a 0,40 MeV è un <b>isomero</b>: il suo spin è così lontano da quello dei livelli sottostanti che un fotone riesce a stento a collegarli, quindi vive da secondi ad anni, e ciò che vi arriva resta lì. Il motore tratta ogni livello che vive più di un secondo come un punto d'arrivo. Ogni pallina è una cascata, che finisce nel mucchio dell'isomero o in quello dello stato fondamentale.</p>
  <div class="ctl"><label for="gm-j">Spin d'ingresso</label><input id="gm-j" type="range" data-bind="J0" min="0" max="8" step="1" value="2" data-instant><output id="gm-jout">5/2</output></div>
  <p>Trascina lo spin d'ingresso, da cui partono le cascate, e i mucchi ricominciano. La quota che finisce sull'isomero, il <b>rapporto isomerico</b>, dipende da esso: una partenza ad alto spin alimenta l'isomero ad alto spin; una a basso spin gli scivola accanto fino allo stato fondamentale.</p>
</div>
<div class="step">
  <h3>Cattura radiativa</h3>
  <p>Un nucleo che ha appena assorbito un neutrone lento ha due porte d'uscita (capitolo 9): i fotoni (in alto) e il neutrone che torna fuori (a destra). Il varco di ogni porta è la sua <b>larghezza</b>, in eV: quanto velocemente il nucleo decade attraverso di essa. La larghezza radiativa cambia appena; quella neutronica cresce con la velocità del neutrone.</p>
  <div class="ctl"><label for="gm-e">Energia del neutrone</label><input id="gm-e" type="range" data-bind="lgE" min="-2" max="3.3" step="0.02" value="0"><output id="gm-eout">1.0 keV</output></div>
  <p>Trascina l'energia del neutrone, da 10 eV a 2 MeV. La <b>cattura</b>, (n,γ), significa che il neutrone resta ed esce un fotone: a 10 eV vince quasi sempre e sopra pochi keV diventa una piccola quota. La larghezza radiativa alla soglia è misurata per centinaia di nuclei, ed è una verifica della funzione di forza fotonica. Per impostazione predefinita il motore usa la propria; un'opzione riscala la funzione di forza di ogni nucleo misurato finché le due concordano.</p>
  <div class="aside">Nel codice: <code>gamma/parameters.py</code> (intensità E1 tabulate; sistematiche di risonanza gigante, spin-flip, forbice e upbend), <code>gamma/strength.py</code> (<i>f</i>(E<sub>γ</sub>) per ogni multipolo), <code>gamma/transmission.py</code> (T<sub>γ</sub> e la larghezza radiativa media), <code>structure/levels.py</code> (rapporti di diramazione, isomeri), <code>emission/multiple.py</code> (la cascata). Opzionali, disattivati per impostazione predefinita: <code>gamma/scissors.py</code> (forbice più intensa), <code>gamma/ggnorm.py</code> (accordo con il ⟨Γγ⟩ misurato, fino al piombo), <code>gamma/actphys.py</code> (entrambi, per gli attinidi).</div>
</div>`,
};
Object.assign(WT.L.labels, {
  // scene 1: emit
  "energy ↑": "energia ↑",
  "named levels": "livelli con nome",
  "a crowd of states": "una folla di stati",
  "{#} MeV": "{#} MeV",
  "hot state, {#} MeV": "stato caldo, {#} MeV",
  "most photons ≈ {#} MeV": "fotoni più frequenti ≈ {#} MeV",
  "small drops: faint (E³ tiny)": "salti piccoli: deboli (E³ minuscolo)",
  "big drops: bright, but few states to land on": "salti grandi: luminosi, ma pochi stati d'arrivo",
  // scene 2: gdr
  "protons": "protoni",
  "neutrons": "neutroni",
  "A = {#}: rings at {#} MeV": "A = {#}: risuona a {#} MeV",
  "peak {#} MeV": "picco {#} MeV",
  "giant resonance at {#} MeV": "risonanza gigante a {#} MeV",
  "width ≈ {#} MeV": "larghezza ≈ {#} MeV",
  "decays use this": "usata nei decadimenti",
  "shaded: the tail decays use": "ombreggiata: la coda usata nei decadimenti",
  "photon energy (MeV) →": "energia del fotone (MeV) →",
  "photon strength f (log scale) ↑": "forza fotonica f (scala log) ↑",
  // scene 3: m1
  "a sphere has no blades: no scissors": "una sfera non ha lame: niente forbice",
  "scissors ≈ {#} MeV: strength {#} % of the most stretched": "forbice ≈ {#} MeV: intensità al {#} % del più allungato",
  "spin-flip ≈ {#} MeV: steady, any shape (thick photons)": "spin-flip ≈ {#} MeV: costante, ogni forma (fotoni spessi)",
  "upbend below {#} MeV: soft photons, plenty at this shape": "upbend sotto {#} MeV: fotoni soffici, molti con questa forma",
  "upbend below {#} MeV: soft photons, fewer at this shape": "upbend sotto {#} MeV: fotoni soffici, meno con questa forma",
  "upbend below {#} MeV: soft photons, few at this shape": "upbend sotto {#} MeV: fotoni soffici, pochi con questa forma",
  // scene 4: cascade
  "ground state": "stato fondamentale",
  "isomer": "isomero",
  "isomer: long-lived": "isomero: vita lunga",
  "bins: too dense to list": "intervalli: troppo fitti",
  "one photon at a time": "un fotone alla volta",
  "measured branching ratios": "diramazioni misurate",
  "▬ parity +   ▭ parity −": "▬ parità +   ▭ parità −",
  // scene 5: isomer
  "entrance: J = {#}/{#}": "ingresso: J = {#}/{#}",
  "isomer: {#} ({#} %)": "isomero: {#} ({#} %)",
  "ground state: {#} ({#} %)": "stato fondamentale: {#} ({#} %)",
  "many cascades: ≈ {#} % isomer": "molte cascate: ≈ {#} % isomero",
  "over many cascades from J = {#}/{#}: ≈ {#} % end on the isomer": "su molte cascate da J = {#}/{#}: ≈ {#} % finisce sull'isomero",
  // scene 6: capture
  "photon door: {#} eV, barely changes": "porta del fotone: {#} eV, cambia appena",
  "captured (n,γ): {#} ({#} %)": "catturati (n,γ): {#} ({#} %)",
  "neutron: {#} eV": "neutrone: {#} eV",
  "neutron door: {#} eV, wider when faster": "porta del neutrone: {#} eV, più larga se più veloce",
  "back out: {#} ({#} %)": "di nuovo fuori: {#} ({#} %)",
  "more doors open (target left excited)": "più porte aperte (bersaglio eccitato)",
  "{#} eV neutrons →": "neutroni da {#} eV →",
  "{#} keV neutrons →": "neutroni da {#} keV →",
  "{#} MeV neutrons →": "neutroni da {#} MeV →",
  "slow neutrons: the photon door wins": "neutroni lenti: vince la porta del fotone",
  "the neutron door wins; capture takes about {#} %": "vince la porta del neutrone; la cattura prende circa il {#} %",
  "fast: capture is a rare event": "veloci: la cattura è un evento raro",
});

Object.assign(WT.L.labels, {
  "{#} cascades from J = {#}/{#}: ≈ {#} % end on the isomer": "{#} cascate da J = {#}/{#}: ≈ {#} % finiscono sull'isomero",
});
