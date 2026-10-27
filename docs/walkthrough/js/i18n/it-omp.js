/* Italian: omp (Capitolo 5, il modello ottico) */
WT.L.ch.omp = {
  num: "Capitolo 5", title: "Una sfera di cristallo offuscata", short: "Modello ottico",
  lead: "Prima di tutto, il motore si pone una domanda più semplice: come appare il nucleo a un neutrone in arrivo?",
  html: `
<div class="step">
  <p>In meccanica quantistica un neutrone è anche un'onda. L'immagine ne mostra una che arriva da sinistra, con le creste come bande luminose, verso un nucleo (il cerchio tratteggiato). Ancora niente agisce su di essa, quindi le creste lo attraversano senza cambiare.</p>
  <div class="ctl"><label for="omp-e">Energia del neutrone (MeV)</label><input id="omp-e" type="range" data-bind="E" min="0.2" max="40" step="0.1" value="8"><output data-show="E" data-fmt="1"></output></div>
  <p>Trascina l'energia e guarda in basso la lunghezza d'onda, in femtometri (fm, 10⁻¹⁵ m). I neutroni lenti hanno onde lunghe: sotto circa 9 MeV una lunghezza d'onda è più larga di tutto questo nucleo.</p>
</div>
<div class="step">
  <h3>La parte reale attrae</h3>
  <p>Il <b>potenziale ottico</b> è la forza media che tutto il nucleo esercita sul neutrone. La sua <em>parte reale</em> è una buca profonda circa 50 MeV: dentro, il neutrone accelera, quindi le creste si addensano. Il motore le dà una forma di Woods–Saxon, piatta e profonda al centro, che svanisce dolcemente a zero sulla superficie.</p>
</div>
<div class="step">
  <h3>La parte immaginaria assorbe</h3>
  <p>L'ombra dietro il nucleo sono i neutroni persi nelle reazioni. La <em>parte immaginaria</em> del potenziale li rappresenta: riduce l'onda invece di deviarla, soprattutto vicino alla superficie (l'anello colorato).</p>
  <div class="ctl"><label for="omp-w">Assorbimento W (MeV)</label><input id="omp-w" type="range" data-bind="W" min="0" max="14" step="0.5" value="7"><output data-show="W" data-fmt="1"></output></div>
  <p>Porta <i>W</i> a 0 e l'ombra si riempie: niente assorbimento, niente reazioni. Da qui il nome di modello ottico: il nucleo è una sfera di vetro offuscata che in parte devia e in parte assorbe.</p>
</div>
<div class="step">
  <h3>La mira conta</h3>
  <p>Visto di fronte, il bersaglio si divide in anelli, uno per ogni <b>onda parziale</b> <i>l</i> = 0, 1, 2, … Un neutrone che passa a distanza <i>b</i> dal centro porta un <b>momento angolare</b> <i>l</i> ≈ <i>k b</i>, dove <i>k</i> cresce con l'energia. Più un anello è scuro, più è grande il suo <b>coefficiente di trasmissione</b> <i>T<sub>l</sub></i>: la probabilità che un neutrone di quell'anello venga assorbito.</p>
  <div class="ctl"><label for="omp-e3">Energia del neutrone (MeV)</label><input id="omp-e3" type="range" data-bind="E" min="0.2" max="40" step="0.1" value="8"><output data-show="E" data-fmt="1"></output></div>
  <div class="btns"><button class="btn" data-act="fire">Lancia 200 neutroni</button></div>
  <p>I lampi arancioni sono neutroni assorbiti; le barre confrontano la frazione assorbita in ogni anello con il <i>T<sub>l</sub></i> del modello (il segno). Gli anelli interni assorbono quasi tutto, quelli esterni lasciano passare i neutroni. A bassa energia gli anelli sono enormi e conta solo <i>l</i> = 0.</p>
</div>
<div class="step">
  <h3>Passare accanto al nucleo</h3>
  <p>Un neutrone con molto momento angolare passa troppo lontano per toccare il nucleo: è la <b>barriera centrifuga</b>. Visto dall'alto, ogni neutrone qui appartiene a una stessa onda parziale <i>l</i>, quindi passa alla stessa <b>distanza di passaggio</b> <i>b</i> ≈ (<i>l</i>+½)/<i>k</i> (il cerchio tratteggiato).</p>
  <p>Ma ogni neutrone è un'onda, sfumata su circa una lunghezza d'onda ridotta λ̄ (l'alone). Anche quando la sua traiettoria manca il bersaglio, il bordo sfumato può sfiorare la superficie ed entrare: l'<b>effetto tunnel</b>.</p>
  <div class="ctl"><label for="omp-l">Onda parziale l</label><input id="omp-l" type="range" data-bind="L" min="0" max="8" step="1" value="3" data-instant><output data-show="L" data-fmt="0"></output></div>
  <div class="ctl"><label for="omp-e2">Energia (MeV)</label><input id="omp-e2" type="range" data-bind="E" min="0.2" max="40" step="0.1" value="8"><output data-show="E" data-fmt="1"></output></div>
  <p>Aumenta <i>l</i> e la traiettoria si allontana: ne entrano meno. Aumenta l'energia e la stessa <i>l</i> passa più vicino, con meno sfumatura. Il motore calcola ogni <i>T<sub>l</sub></i> in modo esatto risolvendo l'equazione di Schrödinger attraverso il potenziale completo; <i>S</i> misura quanta onda torna fuori.</p>
  <div class="formula">T<sub>lj</sub> = 1 − |S<sub>lj</sub>|²</div>
</div>
<div class="step">
  <h3>Sommare il bersaglio</h3>
  <p>Il disco a destra è quanto grande appare il nucleo al neutrone: la <b>sezione d'urto di reazione</b>, in barn (10⁻²⁴ cm²). Ogni anello vi aggiunge la sua area per <i>T<sub>l</sub></i>. Il cerchio tratteggiato è la dimensione geometrica.</p>
  <div class="ctl"><label for="omp-e4">Energia del neutrone (MeV)</label><input id="omp-e4" type="range" data-bind="E" min="0.2" max="40" step="0.1" value="8"><output data-show="E" data-fmt="1"></output></div>
  <div class="btns"><button class="btn ghost" data-act="sum">Somma di nuovo</button></div>
  <p>Cambia l'energia e la somma riparte: a bassa energia uno o due anelli grandi formano quasi tutto il disco; ad alta energia molti anelli sottili aggiungono spicchi e il disco si avvicina alla dimensione geometrica.</p>
  <div class="formula">σ<sub>R</sub> = (π/k²) Σ (2l+1) T<sub>l</sub></div>
  <p>I <i>T<sub>l</sub></i> alimentano il resto del motore: decidono quanto spesso si forma ogni spin del nucleo eccitato e, all'inverso, con quale facilità ogni particella torna fuori.</p>
  <div class="aside">Nel codice: <code>omp/parameters.py</code> (potenziale globale di Koning–Delaroche; potenziali dispersivi per gli attinidi), <code>omp/schrodinger.py</code> (integrazione di Numerov e raccordo coulombiano), <code>omp/inverse.py</code> (particelle uscenti per bilancio dettagliato), <code>omp/regional.py</code> (opzionale, disattivato per impostazione predefinita: un aggiustamento regionale della buca per bersagli deformati di terre rare, adattato a S₀ e S₁ misurati).</div>
</div>`,
};
Object.assign(WT.L.labels, {
  "absorbing surface": "superficie assorbente",
  "shadow: neutrons lost to reactions": "ombra: neutroni persi nelle reazioni",
  "wavelength {#} fm   ·   nucleus {#} fm across": "lunghezza d'onda {#} fm   ·   nucleo di {#} fm",
  "crests crowd inside the well": "le creste si addensano nella buca",
  "l={#}": "l={#}",
  "nuclear radius": "raggio nucleare",
  "reaction cross section ≈ {#} b": "sezione d'urto di reazione ≈ {#} b",
  "geometric size π(R+λ̄)² ≈ {#} b · darker ring = more absorbed · orange flash = absorbed": "dim. geom. π(R+λ̄)² ≈ {#} b · più scuro = più assorbito · arancione = assorbito",
  "absorbed, ring by ring": "assorbiti, anello per anello",
  "bar: your neutrons · tick: model Tₗ": "barra: i tuoi · segno: Tₗ",
  "rings: shade = Tₗ": "anelli: tonalità = Tₗ",
  "geometric size π(R+λ̄)²": "dimensione geometrica π(R+λ̄)²",
  "reaction cross section": "sezione d'urto di reazione",
  "ring l={#}: ({#}l+{#})·Tₗ·π/k² = +{#} b": "anello l={#}: ({#}l+{#})·Tₗ·π/k² = +{#} b",
  "all {#} rings added": "sommati tutti i {#} anelli",
  "σ_R = {#} b": "σ_R = {#} b",
  "geometric {#} b": "geometrica {#} b",
  "geometric {#} b · darker = more absorbed · orange = absorbed": "geometrica {#} b · più scuro = più assorbito · arancione = assorbito",
  "swing distance b ≈ (l+½)/k = {#} fm": "distanza di passaggio b ≈ (l+½)/k = {#} fm",
  "nuclear radius R = {#} fm · wave fuzz λ̄ = {#} fm": "raggio nucleare R = {#} fm · sfumatura λ̄ = {#} fm",
  "path crosses the nucleus: most get in": "la traiettoria attraversa il nucleo: quasi tutti entrano",
  "path misses the nucleus: only the fuzzy edge can tunnel in": "la traiettoria passa fuori: solo il bordo sfumato entra per effetto tunnel",
  "absorbed {#} of {#} · model Tₗ = {#}": "assorbiti {#} su {#} · Tₗ del modello = {#}",
});
