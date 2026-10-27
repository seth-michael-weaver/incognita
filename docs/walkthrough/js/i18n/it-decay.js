/* Italian: decay (Capitolo 9, decadimento) */
WT.L.ch.decay = {
  num: "Capitolo 9", title: "Scegliere un'uscita", short: "Decadimento",
  lead: "Il nucleo composto deve liberarsi della sua energia emettendo una particella o un fotone. Questo capitolo disegna ogni via d'uscita come una porta. Il compito del motore è dire quale parte del flusso (la corrente di reazioni che arriva qui) esce da ciascuna porta.",
  html: `
<div class="step">
  <p>Una porta per ogni uscita: un <em class="g">fotone</em> (γ), un <em class="n">neutrone</em> (n), un <em class="p">protone</em> (p), una <em class="a">particella alfa</em> (α: due protoni e due neutroni) e, solo per i nuclei pesanti, la <em class="f">fissione</em> (la scissione in due). Il varco illuminato in ogni porta è la quota di quell'uscita, e le palline escono con gli stessi ritmi; le porte grigie sono chiuse. Avendo dimenticato come si è formato, il nucleo usa ogni porta b in proporzione a un peso:</p>
  <div class="formula">quota<sub>b</sub> = T<sub>b</sub> · ρ<sub>b</sub> / Σ<sub>c</sub> T<sub>c</sub> · ρ<sub>c</sub></div>
  <p>Il <b>coefficiente di trasmissione</b> <i>T</i> è la probabilità che una particella che arriva al bordo lo attraversi; per le particelle viene dal modello ottico del capitolo 5, applicato al contrario. La <b>densità dei livelli</b> ρ, scritta accanto a ogni porta, conta gli stati in cui può finire il nucleo residuo. Ripartire secondo <i>T</i> per ρ è la regola di <b>Hauser–Feshbach</b>. A 10 MeV la porta del neutrone prende quasi tutto.</p>
</div>
<div class="step">
  <h3>Perché la maggior parte delle particelle esce lenta</h3>
  <p>La porta del neutrone, divisa secondo l'energia di uscita ε (lenti a sinistra, veloci a destra). Il varco <i>T</i>(ε) di ogni porta si allarga per i neutroni più veloci. Sotto c'è la folla di stati in cui può trovarsi il nucleo residuo: un neutrone lento lascia indietro quasi tutta l'energia, dove gli stati abbondano, quindi le folle si riducono verso destra.</p>
  <div class="ctl"><label for="dc-sp">Energia disponibile</label><input id="dc-sp" type="range" data-bind="spare" min="1" max="12" step="0.5" value="5"><output data-show="spare" data-fmt="1"></output></div>
  <p>Porta × folla fa del mucchio una gobba, lo <b>spettro di evaporazione</b>, come il vapore che lascia un liquido caldo. Trascina l'energia disponibile (in MeV, milioni di elettronvolt): il mucchio ricomincia, e il suo picco resta vicino a 1 MeV, fissato dalla temperatura nucleare. L'energia in più rende soprattutto più caldo il nucleo residuo.</p>
</div>
<div class="step">
  <h3>Le particelle cariche devono arrampicarsi</h3>
  <p>L'energia di un protone a ogni distanza r dal centro: una buca dentro e, fuori, una collina dovuta alla repulsione elettrica (coulombiana), che decresce come 1/r. Sotto la cima il protone, che rimbalza nella buca, può solo attraversare per <b>effetto tunnel</b> il tratto ombreggiato, un effetto quantistico che riesce una volta su molti colpi contro la parete.</p>
  <div class="ctl"><label for="dc-ce">Energia della particella</label><input id="dc-ce" type="range" data-bind="eps" min="0.5" max="12" step="0.1" value="3"><output data-show="eps" data-fmt="1"></output></div>
  <div class="btns"><button class="btn ghost" data-act="toggleAlpha">Cambia protone / alfa</button></div>
  <p>Abbassa l'energia e guarda il tunnel allargarsi; poi passa all'alfa, le cui due cariche affrontano una collina alta circa il doppio. Ecco perché i neutroni, privi di carica, di solito vincono non appena possono uscire, e perché le uscite di protoni e alfa contano soprattutto per i nuclei leggeri e ad alte energie.</p>
</div>
<div class="step">
  <h3>Le porte si aprono una alla volta</h3>
  <p>Ogni porta di particella si apre solo sopra la sua <b>energia di separazione</b>, il costo per estrarre quella particella: qui 8 MeV per un neutrone, 9 per un protone, 7 per un'alfa. Sotto gli 8 MeV del neutrone, quasi ogni decadimento emette luce.</p>
  <div class="ctl"><label for="dc-e">Energia di eccitazione</label><input id="dc-e" type="range" data-bind="E" min="5" max="24" step="0.1" value="7"><output data-show="E" data-fmt="1"></output></div>
  <p>Trascina l'energia di eccitazione oltre 8 MeV. Nel giro di circa 1 MeV la porta del neutrone si spalanca e la quota del fotone cala di cento volte. Le porte di protone e alfa si illuminano più tardi e restano strette, frenate dalle loro colline coulombiane.</p>
</div>
<div class="step">
  <h3>Spin e parità devono tornare</h3>
  <p>Il nucleo composto (in alto) ha spin <i>J</i>; sotto, gli stati del nucleo residuo stanno in cassetti secondo lo spin <i>J</i>′. Il neutrone porta via la differenza di spin e parità: uscendo con momento angolare orbitale <i>l</i>, cambia lo spin fino a <i>l</i> + ½ e inverte la parità quando <i>l</i> è dispari. Un <i>l</i> maggiore significa una porta più stretta; la porta di ogni cassetto è quella con il più piccolo <i>l</i> che lo raggiunge. Gli arrivi pieni conservano la parità; quelli vuoti la invertono.</p>
  <div class="ctl"><label for="dc-j">Spin del composto J</label><input id="dc-j" type="range" data-bind="J" min="0" max="10" step="1" value="2" data-instant><output id="dc-jout">5/2</output></div>
  <p>Fai salire <i>J</i>. Le porte aperte scivolano verso i cassetti ad alto spin, che contengono pochi stati, mentre i cassetti pieni restano dietro porte chiuse. Un nucleo composto ad alto spin è lento a emettere particelle, e questo dà una possibilità ai fotoni e agli isomeri (stati a vita lunga, capitolo 10).</p>
</div>
<div class="step">
  <h3>La strada da cui sei entrato</h3>
  <p>A bassa energia il nucleo composto è un insieme di <b>risonanze</b> strette, energie a cui il neutrone viene assorbito facilmente; ne sono disegnate otto, una per riga. Ognuna ha larghezze di porta casuali: l'ingresso (il canale del neutrone) a sinistra, di larghezza <i>x</i>, e le altre porte, qui soprattutto fotoni, a destra, di larghezze <i>y</i>.</p>
  <div class="btns"><button class="btn" data-act="fire">Lancia 40 neutroni</button><button class="btn ghost" data-act="reroll">Nuove risonanze</button></div>
  <p>Un neutrone entra nella risonanza <i>i</i> con probabilità proporzionale a <i>x<sub>i</sub></i> ed esce dall'ingresso con probabilità <i>x<sub>i</sub></i> / (<i>x<sub>i</sub></i> + Σ<i>y</i>). Le righe con un ingresso largo ricevono più neutroni e ne rimandano fuori di più, quindi la vera quota che torna fuori (una <b>media di prodotti</b>) supera la stima ottenuta dalle larghezze medie (un <b>prodotto di medie</b>). Il rapporto è l'<b>aumento elastico</b>, e la <b>correzione per le fluttuazioni delle larghezze</b> sposta quel flusso dalle altre porte all'ingresso.</p>
  <div class="ctl"><label for="dc-n">Altre porte</label><input id="dc-n" type="range" data-bind="Nch" min="1" max="12" step="1" value="2" data-instant><output data-show="Nch" data-fmt="0"></output></div>
  <p>Aggiungi porte. Con molte uscite la loro larghezza totale smette di fluttuare, quindi la correzione conta soprattutto dove sono aperte poche porte. Il motore la applica, con la formula di Moldauer, ai neutroni incidenti fino all'energia di separazione del neutrone del bersaglio, e la omette al di sopra.</p>
</div>
<div class="step">
  <h3>Che cosa resta da spartire</h3>
  <p>Non ogni neutrone assorbito forma un nucleo composto. Alcuni danno un colpo di striscio e volano via (reazioni dirette, capitolo 6); altri urtano una o due volte e schizzano fuori veloci (pre-equilibrio, capitolo 7). Solo i rimanenti restano e riscaldano il nucleo. I contatori registrano ogni destino.</p>
  <div class="ctl"><label for="dc-einc">Energia del neutrone</label><input id="dc-einc" type="range" data-bind="Einc" min="1" max="30" step="0.5" value="8"><output data-show="Einc" data-fmt="1"></output></div>
  <p>Solo quelli che restano entrano nella competizione fra le porte. Trascina l'energia del neutrone: a pochi MeV restano quasi tutti; a 30 MeV circa la metà se n'è andata prima di raggiungere l'equilibrio.</p>
  <div class="aside">Nel codice: <code>compound/prepare.py</code> (pesi d'uscita T·ρ per spin e parità, regole di selezione), <code>compound/target.py</code> (primo decadimento con fluttuazioni delle larghezze), <code>compound/continuum.py</code> (decadimento di ogni intervallo successivo), <code>compound/wfc.py</code> (correzioni di Moldauer, HRTW, GOE), <code>compound/normalization.py</code> (flusso rimasto per il nucleo composto), <code>omp/inverse.py</code> (porte percorse al contrario).</div>
</div>`,
};
(function () {
  const L = {
    "{#} MeV": "{#} MeV",
    "n": "n", "p": "p", "fission": "fissione",
    "heavy only": "solo pesanti",
    "heavy nuclei only": "solo nuclei pesanti",
    "shut below {#} MeV": "chiusa sotto {#} MeV",
    "the neutron door takes nearly everything": "la porta del neutrone prende quasi tutto",
    "below the neutron threshold, nearly all decays emit light": "sotto la soglia del neutrone, quasi tutti i decadimenti emettono luce",
    "the doors share the decays": "le porte si spartiscono i decadimenti",
    // hump
    "{#} MeV to spare": "{#} MeV disponibili",
    "door gap = T(ε)": "varco = T(ε)",
    "doors: one per neutron energy ε, gap = T(ε)": "porte: una per energia ε del neutrone, varco = T(ε)",
    "× states left behind": "× stati lasciati",
    "× states the leftover nucleus can be in: many after a slow neutron": "× stati possibili del nucleo residuo: molti dopo un neutrone lento",
    "most ≈ {#} MeV": "massimo ≈ {#} MeV",
    "= the pile": "= il mucchio",
    "= where the neutrons land: the evaporation spectrum": "= dove arrivano i neutroni: lo spettro di evaporazione",
    "slow": "lenti",
    "slow neutrons": "neutroni lenti",
    "fast: {#} MeV →": "veloci: {#} MeV →",
    "fast: {#} MeV (beyond, up to {#}, almost none)": "veloci: {#} MeV (oltre, fino a {#}, quasi nessuno)",
    "fast: {#}": "veloci: {#}",
    "fast: {#} MeV, the neutron takes it all": "veloci: {#} MeV, il neutrone prende tutto",
    // coulomb
    "well ↓": "buca ↓",
    "well (much deeper) ↓": "buca (molto più profonda) ↓",
    "hilltop ≈ {#} MeV": "cima ≈ {#} MeV",
    "falls as {#}/r": "cala come {#}/r",
    "Coulomb hill, falling as {#}/r": "collina coulombiana, cala come {#}/r",
    "tunnel: wider than the picture": "tunnel: più largo dell'immagine",
    "tunnel {#} fm": "tunnel {#} fm",
    "proton energy {#} MeV": "energia del protone {#} MeV",
    "alpha energy {#} MeV": "energia dell'alfa {#} MeV",
    "proton energy {#} MeV ↑": "energia del protone {#} MeV ↑",
    "alpha energy {#} MeV ↑": "energia dell'alfa {#} MeV ↑",
    "above the hilltop: it rolls straight out": "sopra la cima: rotola subito fuori",
    "below the top, must tunnel: nearly every knock gets through": "sotto la cima, effetto tunnel: passa quasi a ogni colpo",
    "below the top, must tunnel: about {#} knock in {#} gets through": "sotto la cima, effetto tunnel: passa circa {#} colpo su {#}",
    "below the top, must tunnel: about {#} knock in {#} × {#}^{#} gets through": "sotto la cima, effetto tunnel: passa circa {#} colpo su {#} × {#}^{#}",
    "out": "fuori",
    "through after {#} knock": "passato dopo {#} colpo",
    "through after {#} knocks": "passato dopo {#} colpi",
    "knocks so far: {#}": "colpi finora: {#}",
    "distance r from the centre (fm) →": "distanza r dal centro (fm) →",
    // spin
    "J = {#}/{#}, parity +": "J = {#}/{#}, parità +",
    "l={#}": "l={#}",
    "leftover states by spin J′ →": "stati residui per spin J′ →",
    "drawers: states of the leftover nucleus by spin J′ (faint: states it holds) →": "cassetti: stati del nucleo residuo per spin J′ (tenue: stati contenuti) →",
    "open doors reach {#} %": "le porte aperte raggiungono il {#} %",
    "open doors reach about {#} % of the states": "le porte aperte raggiungono circa il {#} % degli stati",
    "● parity kept (even l)   ○ flipped (odd l)": "● parità conservata (l pari)   ○ invertita (l dispari)",
    // wfc
    "entrance x": "ingresso x",
    "entrance, width x": "ingresso, larghezza x",
    "{#} other doors, y": "{#} altre porte, y",
    "{#} other door, widths y": "{#} altra porta, larghezze y",
    "{#} other doors, widths y": "{#} altre porte, larghezze y",
    "back out the entrance: {#} of {#}": "di nuovo fuori dall'ingresso: {#} su {#}",
    "out another door: {#}": "da un'altra porta: {#}",
    // norm
    "absorbed neutrons, {#} MeV →": "neutroni assorbiti, {#} MeV →",
    "direct: {#} %": "dirette: {#} %",
    "pre-equilibrium: {#} %": "pre-equilibrio: {#} %",
    "compound nucleus: {#} %": "nucleo composto: {#} %",
    "one glancing hit on the surface": "un colpo di striscio sulla superficie",
    "a knock or two, then out fast": "un urto o due, poi fuori veloce",
    "stayed: on to the door competition": "rimasto: alla competizione fra le porte",
  };
  // door hint with level-count wording (fmt: "1", "N", "N thousand", "N million") and T possibly in e-notation
  const cnt = [["{#} state", "{#} stato"], ["{#} states", "{#} stati"], ["{#} thousand states", "{#} mila stati"], ["{#} million states", "{#} milioni di stati"]];
  for (const [e, s] of cnt) {
    L[`weak door × ≈ ${e}`] = `porta debole × ≈ ${s}`;
    L[`T ≈ {#} × ≈ ${e}`] = `T ≈ {#} × ≈ ${s}`;
    L[`T ≈ {#}e{#} × ≈ ${e}`] = `T ≈ {#}e{#} × ≈ ${s}`;
  }
  // share comparisons: each pct is "{#} %" or "≈ {#} %"
  const P = ["{#} %", "≈ {#} %"];
  for (const a of P) for (const b of P) {
    L[`back out ${a}, not ${b}: × {#}`] = `tornano fuori ${a}, non ${b}: × {#}`;
    L[`share back out: average of products ${a} · product of averages ${b} · × {#}`] = `quota di ritorno: media di prodotti ${a} · prodotto di medie ${b} · × {#}`;
    L[`other doors ${a}, not ${b}`] = `altre porte ${a}, non ${b}`;
    L[`other doors together: ${a} instead of ${b}`] = `altre porte insieme: ${a} invece di ${b}`;
  }
  Object.assign(WT.L.labels, L);
})();
