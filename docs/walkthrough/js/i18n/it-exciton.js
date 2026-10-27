/* Italian: exciton (Capitolo 26, il modello a eccitoni in numeri) */
WT.L.ch.exciton = {
  num: "Capitolo 26", title: "Il modello a eccitoni, in numeri", short: "Modello a eccitoni",
  lead: "Il capitolo 7 ha seguito un neutrone veloce attraverso poche collisioni. Ecco i tassi che decidono, a ogni stadio, se il passo successivo sarà un'altra collisione o una fuga, e lo spettro che ne risulta sommandoli.",
  html: `
<div class="step">
  <h3>Contare gli stati particella–lacuna</h3>
  <p>Il modello a eccitoni classifica il nucleo in cammino verso l'equilibrio secondo il numero di particelle eccitate <i>p</i> e di lacune <i>h</i>, con <i>n</i> = <i>p</i> + <i>h</i>. Un neutrone che entra in un bersaglio parte da <i>p</i> = 1, <i>h</i> = 0; ogni collisione aggiunge una coppia. A ogni stadio conta in quanti modi l'energia può essere ripartita fra gli <i>n</i> eccitoni: la densità di stati particella–lacuna.</p>
  <div class="formula">ω(p,h,E) = g<sup>n</sup> (E − A<sub>p,h</sub>)<sup>n−1</sup> / (p! h! (n−1)!) ,  A<sub>p,h</sub> = max(p,h)²/g − (p² + h² + p + h)/4g</div>
  <div class="ctl"><label for="ex-n">Particelle p (lacune p − 1)</label><input id="ex-n" type="range" data-bind="pp" min="2" max="6" step="1" value="3" data-instant><output data-show="pp" data-fmt="0"></output></div>
  <div class="btns"><button class="btn ghost" data-act="pauli" aria-pressed="true">Correzione di Pauli</button></div>
  <p><i>g</i> ≈ <i>A</i>/15 MeV⁻¹ è la densità dei livelli di particella singola vicino all'energia di Fermi. <i>A<sub>p,h</sub></i> è la correzione di <b>Pauli</b>: due particelle non possono occupare lo stesso livello, quindi le configurazioni più basse costano energia e la densità vicino alla soglia cala. Lo schema mostra una configurazione alla volta con il <i>p</i> scelto, estratta a caso.</p>
</div>
<div class="step">
  <h3>Andare più a fondo o uscire</h3>
  <p>Da ogni stadio possono accadere due cose. Una collisione crea un'altra coppia, con il tasso λ<sup>+</sup>, che per la regola d'oro di Fermi è l'elemento di matrice al quadrato per la densità degli stati che può raggiungere. Oppure una particella esce, con il tasso <i>W</i>, dato dal bilancio dettagliato a partire dalla sezione d'urto inversa e dal rapporto fra le densità di stati con e senza la particella che sfugge.</p>
  <div class="formula">λ<sup>+</sup>(n) = (2π/ħ) M² ω<sub>acc</sub> ,  W(p,h,ε) = (2s+1)/(π²ħ³) με σ<sub>inv</sub>(ε) ω(p−1,h,U) / ω(p,h,E)</div>
  <div class="ctl"><label for="ex-e">Energia del neutrone (MeV)</label><input id="ex-e" type="range" data-bind="Ein" min="5" max="60" step="0.5" value="20"><output data-show="Ein" data-fmt="1"></output></div>
  <p>Le barre sono i due tassi a ogni stadio, in scala logatassica: λ<sup>+</sup> dell'ordine di 10²² s⁻¹, <i>W</i> circa un decimo di esso al primo stadio e in calo a ogni stadio, perché ogni nuova coppia assottiglia l'energia che la particella di testa può portare via. Il motore prende M² dalla forma di Koning–Duijvestijn, che cala con l'energia per eccitone:</p>
  <div class="formula">M² = (C₁ A<sub>p</sub> / A³) · [7.48 + 4.62×10⁵ / (E/(n A<sub>p</sub>) + 10.7)³]  MeV²</div>
</div>
<div class="step">
  <h3>La catena nel tempo</h3>
  <p>Trascurando le rare collisioni che tolgono una coppia (l'approssimazione never-come-back), le popolazioni obbediscono a una catena semplice: ogni stadio si riempie da quello precedente e si svuota nel successivo e nel continuo. Le barre risolvono questa equazione maestra; il tempo è in unità di 10⁻²² s.</p>
  <div class="formula">dP(n)/dt = λ<sup>+</sup>(n−2) P(n−2) − [λ<sup>+</sup>(n) + W(n)] P(n)</div>
  <div class="ctl"><label for="ex-e2">Energia del neutrone (MeV)</label><input id="ex-e2" type="range" data-bind="Ein" min="5" max="60" step="0.5" value="20"><output data-show="Ein" data-fmt="1"></output></div>
  <p>L'intera catena si esaurisce in pochi 10⁻²² s. La quota che sfugge lungo il percorso è l'emissione di pre-equilibrio; il resto, dopo al massimo sei particelle nel motore, come in TALYS, passa al nucleo composto. L'integrazione nel tempo dà a ogni stadio un peso τ(<i>n</i>)·<i>P</i>(<i>n</i>), ed è questo prodotto che il motore calcola.</p>
</div>
<div class="step">
  <h3>Da dove viene la coda dura</h3>
  <p>Lo spettro di emissione è la somma sugli stadi di popolazione per vita media per tasso di emissione, più l'evaporazione di ciò che resta. Il solo stadio <i>n</i> = 3, due particelle e una lacuna, raggiunge le energie d'uscita più alte: il suo spettro cala solo linearmente verso il punto finale. Ogni stadio successivo è più morbido.</p>
  <div class="formula">dσ/dε = σ<sub>CN</sub> Σ<sub>n</sub> P(n) τ(n) W(n,ε) + evaporazione</div>
  <div class="ctl"><label for="ex-e3">Energia del neutrone (MeV)</label><input id="ex-e3" type="range" data-bind="Ein" min="5" max="60" step="0.5" value="20"><output data-show="Ein" data-fmt="1"></output></div>
  <p>Alza l'energia e lo spettro si indurisce: la coda di pre-equilibrio si allunga fino al punto finale mentre la gobba di evaporazione resta fra 1 e 2 MeV. Sopra circa 10 MeV i neutroni di alta energia misurati si possono riprodurre solo con questa coda.</p>
</div>
<div class="step">
  <h3>Quanto pesa</h3>
  <p>La quota dell'emissione che è di pre-equilibrio cresce con l'energia incidente, da qualche per cento vicino a 5 MeV a circa il 40 per cento a 40 MeV in questo esempio. Dipende da un'unica costante regolabile, la scala complessiva dell'elemento di matrice: un'interazione più debole significa un'equilibrazione più lenta e più emissione precoce.</p>
  <div class="ctl"><label for="ex-c">Costante dell'elemento di matrice C₁</label><input id="ex-c" type="range" data-bind="c1" min="0.3" max="3" step="0.05" value="1"><output data-show="c1" data-fmt="2"></output></div>
  <p>La curva tratteggiata è C₁ = 1, il valore predefinito del motore; quella continua segue il cursore. Dimezzare C₁ aumenta la quota di un fattore da 1,5 a 1,9, non 2: la probabilità di fuga di ogni stadio è W/(λ<sup>+</sup> + W), non W/λ<sup>+</sup>, e meno nuclei sopravvivono fino agli stadi successivi.</p>
</div>
<div class="step">
  <h3>Due componenti e una seconda fuga</h3>
  <p>Il motore segue protoni e neutroni separatamente (<i>p</i><sub>π</sub>, <i>h</i><sub>π</sub>, <i>p</i><sub>ν</sub>, <i>h</i><sub>ν</sub>), con elementi di matrice diversi per coppie simili e dissimili, una buca meno profonda per la prima collisione vicino alla superficie e le regole di Kalbach per i cluster. Sopra 20 MeV permette anche al nucleo residuo, che contiene ancora eccitoni, di emettere una seconda particella veloce prima di equilibrarsi.</p>
  <div class="ctl"><label for="ex-e4">Energia del neutrone (MeV)</label><input id="ex-e4" type="range" data-bind="Ein" min="5" max="60" step="0.5" value="20"><output data-show="Ein" data-fmt="1"></output></div>
  <p>La curva ne è una versione giocattolo: dopo una prima emissione dallo stadio a tre eccitoni, la probabilità che la particella rimasta nel residuo sfugga prima della collisione successiva. Resta piccola sotto 20 MeV e cresce sopra, ed è lì che il motore attiva il pre-equilibrio multiplo.</p>
  <div class="aside">Nel codice: <code>density/particle_hole.py</code> (densità di Williams, correzioni di Pauli e di buca finita, a una e a due componenti), <code>preeq/exciton.py</code> (elementi di matrice, tassi di emissione e di transizione, vite medie, la soluzione never-come-back), <code>preeq/complex.py</code> (pickup, stripping e knockout di Kalbach), <code>preeq/multi.py</code> (pre-equilibrio multiplo, da 20 MeV per impostazione predefinita). Il disegno è a una componente, con una sezione d'urto inversa schematica, per un bersaglio simile al ferro-56.</div>
</div>`,
};
Object.assign(WT.L.labels, {
  "E (MeV)": "E (MeV)",
  // state densities
  "ω(p, h, E) per MeV": "ω(p, h, E) per MeV",
  "{#}p{#}h": "{#}p{#}h",
  "dashed: no Pauli correction": "tratteggio: senza correzione di Pauli",
  "Fermi level": "livello di Fermi",
  "{#} particles, {#} holes": "{#} particelle, {#} lacune",
  // rates
  "rate (s⁻¹)": "tasso (s⁻¹)",
  "n = {#}": "n = {#}",
  "W/λ⁺ = {#}": "W/λ⁺ = {#}",
  "blue: λ⁺, the next collision · yellow: W, neutron escape": "blu: λ⁺, la collisione successiva · giallo: W, fuga del neutrone",
  "E = {#} + Sₙ = {#} MeV · τ(n={#}) = {#} × {#}⁻²² s": "E = {#} + Sₙ = {#} MeV · τ(n={#}) = {#} × {#}⁻²² s",
  // chain
  "compound": "composto",
  "emitted before equilibrium: {#} % (of {#} % in the end)": "emesso prima dell'equilibrio: {#} % (su {#} % alla fine)",
  "t = {#} × {#}⁻²² s": "t = {#} × {#}⁻²² s",
  // spectrum
  "outgoing neutron energy ε (MeV)": "energia del neutrone uscente ε (MeV)",
  "dσ/dε (mb/MeV)": "dσ/dε (mb/MeV)",
  "evaporation": "evaporazione",
  "ε = {#} MeV: {#} % from n = {#}": "ε = {#} MeV: {#} % da n = {#}",
  "pre-equilibrium {#} % of the emission · solid: total": "pre-equilibrio {#} % dell'emissione · continua: totale",
  // share
  "{#} MeV": "{#} MeV",
  "pre-equilibrium share of the emission": "quota di pre-equilibrio dell'emissione",
  "{#} MeV: {#} %": "{#} MeV: {#} %",
  "C₁ = {#} (dashed: {#})": "C₁ = {#} (tratteggio: {#})",
  // second escape
  "{#} MeV: multiple pre-equilibrium on": "{#} MeV: pre-equilibrio multiplo attivo",
  "chance of a second fast emission (toy estimate)": "probabilità di una seconda emissione veloce (stima giocattolo)",
  "residual: {#}p{#}h": "residuo: {#}p{#}h",
});
Object.assign(WT.L.glossary, {
  neverComeBack: {
    term: "Approssimazione never-come-back", aliases: ["approssimazione never-come-back", "never-come-back"],
    short: "L'approssimazione per cui, nelle prime fasi dell'equilibrazione, le collisioni aggiungono soltanto coppie particella–lacuna e non ne tolgono mai.",
    more: "Trasforma l'equazione maestra in una catena semplice, integrabile uno stadio alla volta. Vale finché il numero di eccitoni è molto al di sotto del suo valore di equilibrio, cioè proprio dove avviene l'emissione di pre-equilibrio.",
    chapter: "exciton",
  },
});
