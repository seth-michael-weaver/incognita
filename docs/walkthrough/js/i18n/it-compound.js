/* Italian: compound (Capitolo 5, nucleo composto) */
WT.L.ch.compound = {
  num: "Capitolo 5", title: "Spartire l'energia", short: "Nucleo composto",
  lead: "Finiti i primi urti rapidi, tutti i nucleoni condividono l'energia. Questo stato assestato è il nucleo composto. Per prevedere che cosa farà dopo, il motore deve sapere in quanti modi può contenere la sua energia.",
  html: `
<div class="step">
  <p>Un neutrone colpisce un lato di un nucleo. La sua energia, più quella liberata dalla sua cattura, parte come un punto caldo (il bagliore arancione); gli urti la trasmettono, e in circa 10⁻²¹ secondi ogni nucleone ne porta una parte.</p>
  <div class="btns"><button class="btn" data-act="hit">Colpisci da un altro lato</button></div>
  <p>Premi il pulsante per mandare il neutrone da un altro lato. Il bagliore finisce sempre allo stesso modo: il nucleo ha <b>dimenticato come si è formato</b>. È il nucleo composto di Bohr. Da qui in poi contano solo tre cose: la sua energia, il suo spin (quanto ruota) e la sua parità (un'etichetta + o − per la sua simmetria speculare).</p>
</div>
<div class="step">
  <h3>Dai livelli separati a un continuo</h3>
  <p>La scala a sinistra contiene gli stati del nucleo, con l'energia che sale verso l'alto; la finestra a destra ingrandisce una fetta di 1 MeV attorno alla palla arancione. Vicino al fondo i pioli sono molto distanziati, e ognuno è stato misurato. Più in alto, i modi di spartire l'energia fra 56 nucleoni si moltiplicano finché i pioli si fondono in una banda compatta, il continuo.</p>
  <div class="ctl"><label for="cn-e">Energia di eccitazione</label><input id="cn-e" type="range" data-bind="E" min="0" max="20" step="0.1" value="6.5"><output data-show="E" data-fmt="1"></output></div>
  <p>Trascina l'energia di eccitazione (l'energia contenuta sopra lo stato più basso, in MeV) e osserva la finestra. La <b>densità dei livelli</b> ρ, stati per MeV, cresce più o meno come e<sup>2√(aE)</sup>, dove <i>a</i> fissa il ritmo di ogni nucleo: pochi per MeV a 3 MeV, centinaia vicino a 8 MeV (dove un neutrone potrebbe uscire), milioni verso 20 MeV. Lassù il motore lavora direttamente con ρ.</p>
</div>
<div class="step">
  <h3>Tre pezzi, uniti a una certa energia</h3>
  <p>L'altezza del terreno è la densità dei livelli in scala logaritmica, con l'energia verso destra. In basso a sinistra stanno i livelli contati. L'asse dritta è la legge a <b>temperatura costante</b>: ρ si moltiplica per e (circa 2,7) ogni <i>T</i> MeV, dove <i>T</i> è la temperatura nucleare. Il pendio è il <b>gas di Fermi</b>, che tratta i nucleoni come particelle indipendenti. Tranne che per i bersagli più pesanti, per cui legge densità tabulate, il motore usa questa coppia per impostazione predefinita.</p>
  <div class="ctl"><label for="cn-ex">Energia di raccordo</label><input id="cn-ex" type="range" data-bind="Ex" min="4.5" max="12" step="0.05" value="6"><output data-show="Ex" data-fmt="1"></output></div>
  <p>Trascina l'energia di raccordo: il giunto scivola lungo la collina e l'asse ruota per incontrarlo con la stessa altezza e la stessa pendenza. Le due pile in basso confrontano i livelli previsti dall'asse con quelli effettivamente contati. Solo un giunto li rende uguali; lì l'asse diventa verde. Quella è l'energia che sceglie il motore.</p>
</div>
<div class="step">
  <h3>Shell che si sciolgono</h3>
  <p>Livelli di singolo nucleone, due nucleoni ciascuno, per due nuclei. A sinistra, una shell chiusa: tutto ciò che sta sotto un grande gap è pieno, quindi ogni spostamento paga l'intero gap. A destra, un nucleo a metà shell con il livello più alto pieno a metà, quindi esistono subito spostamenti economici. Ogni contatore mostra quante configurazioni possono contenere quel calore.</p>
  <div class="ctl"><label for="cn-u">Calore (eccitazione)</label><input id="cn-u" type="range" data-bind="U" min="0" max="40" step="0.5" value="3"><output data-show="U" data-fmt="1"></output></div>
  <p>Aumenta il calore e guarda i nucleoni saltare. Con poco calore la shell chiusa è a corto di configurazioni; con abbastanza calore il gap smette di contare ed entrambi i conteggi crescono allo stesso modo. Il <b>parametro di densità dei livelli</b> <i>a</i> porta con sé questo effetto: gli aghi partono distanti e convergono sul valore liscio <i>ã</i> nell'arco di circa 10 MeV. Il motore attenua la correzione di shell δW con un ritmo γ:</p>
  <div class="formula">a(U) = ã · [1 + δW · (1 − e<sup>−γU</sup>) / U]</div>
</div>
<div class="step">
  <h3>Ordinati per spin e parità</h3>
  <p>Gli stati a una data energia cadono in cassetti secondo lo spin <i>J</i>, il momento angolare del nucleo: gettoni pieni per la parità +, vuoti per −. I cassetti centrali sono i più pieni, secondo (2<i>J</i>+1) e<sup>−(J+½)²/2σ²</sup>, dove il cutoff di spin σ fissa la larghezza. Le due parità risultano più o meno uguali.</p>
  <div class="ctl"><label for="cn-u2">Eccitazione</label><input id="cn-u2" type="range" data-bind="U2" min="1" max="30" step="0.5" value="8"><output data-show="U2" data-fmt="1"></output></div>
  <div class="btns"><button class="btn ghost" data-act="deform">Deforma il nucleo</button></div>
  <p>Fai salire l'eccitazione: σ cresce, perché un nucleo più caldo può portare più spin. Poi premi Deforma. Un nucleo a forma di pallone da rugby può anche ruotare nel suo insieme, quindi ogni cassetto guadagna stati (i gettoni blu): è l'<b>incremento collettivo</b>. Per impostazione predefinita il motore lo aggiunge solo per bersagli con più di circa 215 nucleoni.</p>
</div>
<div class="step">
  <h3>Tagliato in intervalli</h3>
  <p>Sopra l'ultimo livello contato il motore taglia il continuo in fette di uguale larghezza in energia, chiamate intervalli (bin). In ogni intervallo i punti si raccolgono in un blocco di ρ·ΔE stati (ΔE è la larghezza dell'intervallo), ordinati per spin e parità come sopra.</p>
  <div class="ctl"><label for="cn-emax">Cima della scala</label><input id="cn-emax" type="range" data-bind="Emax" min="8" max="30" step="0.5" value="14"><output data-show="Emax" data-fmt="1"></output></div>
  <div class="btns"><button class="btn ghost" data-act="rebin">Riordina</button></div>
  <p>Trascina la cima della scala, la massima energia che il neutrone può portare. Lo stesso numero di intervalli deve coprire più energia, quindi ciascuno diventa più alto. La palla arancione scende di intervallo in intervallo: ogni passo successivo (scegliere un'uscita, la cascata di fotoni, il percorso lungo la carta) lavora su questi intervalli. Qui ne sono disegnati dieci; il motore ne usa fino a 40.</p>
  <div class="aside">Nel codice: <code>density/parameters.py</code> (<i>a</i>(U) di Ignatyuk, cutoff di spin, distribuzione di Wigner, incremento collettivo), <code>density/models.py</code> (temperatura costante, gas di Fermi, tabelle), <code>density/matching.py</code> (l'energia di raccordo a partire dai livelli contati), <code>core/grids.py</code> (intervalli di eccitazione).</div>
</div>`,
};
(function () {
  const L = {
    // scene 1
    "a neutron comes in": "arriva un neutrone",
    "a hot spot: the energy is still local": "un punto caldo: l'energia è ancora localizzata",
    "equilibrium: every nucleon holds a share": "equilibrio: ogni nucleone ne ha una parte",
    "no trace left of where it was hit": "nessuna traccia di dove è stato colpito",
    // scene 2
    "ground state": "stato fondamentale",
    "{#}–{#} MeV, magnified": "{#}–{#} MeV, ingrandito",
    "no level in this slice": "nessun livello in questa fetta",
    "{#} rung in {#} MeV": "{#} piolo in {#} MeV",
    "{#} rungs in {#} MeV": "{#} pioli in {#} MeV",
    "{#} rung in this {#}-MeV slice": "{#} piolo in questa fetta di {#} MeV",
    "{#} rungs in this {#}-MeV slice": "{#} pioli in questa fetta di {#} MeV",
    "about {#} rungs: too close to draw": "circa {#} pioli: troppo fitti per disegnarli",
    "about {#}k rungs: too close to draw": "circa {#} mila pioli: troppo fitti per disegnarli",
    "about {#}M rungs: too close to draw": "circa {#} mln di pioli: troppo fitti per disegnarli",
    "about {#}B rungs: too close to draw": "circa {#} mld di pioli: troppo fitti per disegnarli",
    "about {#} rungs in this slice: too close to draw": "circa {#} pioli in questa fetta: troppo fitti per disegnarli",
    "about {#} thousand rungs in this slice: too close to draw": "circa {#} mila pioli in questa fetta: troppo fitti per disegnarli",
    "about {#} million rungs in this slice: too close to draw": "circa {#} milioni di pioli in questa fetta: troppo fitti per disegnarli",
    "about {#} billion rungs in this slice: too close to draw": "circa {#} miliardi di pioli in questa fetta: troppo fitti per disegnarli",
    "each one measured: energy, spin and parity": "ognuno misurato: energia, spin e parità",
    "the rungs are multiplying": "i pioli si moltiplicano",
    "a continuum: the engine uses ρ itself": "un continuo: il motore usa direttamente ρ",
    "≈ energy to free a neutron": "≈ energia per liberare un neutrone",
    "energy ↑": "energia ↑",
    // scene 3
    "gap: plank below the rungs": "scarto: asse sotto i pioli",
    "gap: plank above the rungs": "scarto: asse sopra i pioli",
    "counted levels": "livelli contati",
    "CT plank": "asse TC",
    "constant-temperature plank": "asse a temperatura costante",
    "Fermi-gas hillside": "pendio del gas di Fermi",
    "joint {#} MeV": "giunto {#} MeV",
    "energy →": "energia →",
    "+{#} more": "+{#} altri",
    "{#} counted": "{#} contati",
    "{#} predicted": "{#} previsti",
    "{#}+ predicted": "{#}+ previsti",
    "equal: the plank rests on the counted rungs": "uguali: l'asse poggia sui pioli contati",
    "too few: the plank is too steep and sinks": "troppo pochi: l'asse è troppo ripida e affonda",
    "too many: the plank is too shallow and floats": "troppi: l'asse è troppo piatta e galleggia",
    // scene 4
    "closed shell": "shell chiusa",
    "mid-shell": "metà shell",
    "gap": "gap",
    "no arrangement holds this heat": "nessuna configurazione contiene questo calore",
    "≈ {#} arrangement": "≈ {#} configurazione",
    "≈ {#} arrangements": "≈ {#} configurazioni",
    "≈ {#} thousand arrangements": "≈ {#} mila configurazioni",
    "≈ {#} million arrangements": "≈ {#} milioni di configurazioni",
    "≈ {#} billion arrangements": "≈ {#} miliardi di configurazioni",
    "a ≈ {#}": "a ≈ {#}",
    "cold: nobody can move": "freddo: nessuno può muoversi",
    "temperature ≈ {#} MeV": "temperatura ≈ {#} MeV",
    // scene 5
    "states at {#} MeV": "stati a {#} MeV",
    "spin J →": "spin J →",
    "+ parity": "parità +",
    "− parity": "parità −",
    "rotation ×{#}": "rotazione ×{#}",
    "added by rotation: ×{#} (a few drawn)": "aggiunti dalla rotazione: ×{#} (alcuni disegnati)",
    "spread σ ≈ {#}: most states near J ≈ {#}": "larghezza σ ≈ {#}: la maggior parte degli stati vicino a J ≈ {#}",
    "deformed: it can rotate": "deformato: può ruotare",
    "spherical": "sferico",
    // scene 6
    "≈ {#} thousand": "≈ {#} mila",
    "≈ {#} million": "≈ {#} milioni",
    "≈ {#} billion": "≈ {#} miliardi",
    "≈ {#}k": "≈ {#} mila",
    "≈ {#}M": "≈ {#} mln",
    "≈ {#}B": "≈ {#} mld",
    "{#} bins, each {#} MeV wide": "{#} intervalli, ciascuno largo {#} MeV",
    "counted": "contati",
    "states in each bin": "stati in ogni intervallo",
  };
  Object.assign(WT.L.labels, L);
})();
