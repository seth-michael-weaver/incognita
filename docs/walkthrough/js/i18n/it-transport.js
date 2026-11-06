/* Italian: transport (Lezione 1, trasporto dei neutroni e Monte Carlo) */
WT.L.ch.transport = {
  num: "Lezione 1", title: "Trasporto dei neutroni e Monte Carlo", short: "Monte Carlo",
  html: `
<div class="step">
  <h3>L'equazione del trasporto</h3>
  <p>In modo esatto, i neutroni obbediscono all'equazione di Boltzmann per il flusso angolare <i>ψ</i>(<b>r</b>, <b>Ω</b>, <i>E</i>): <b>Ω</b>·∇<i>ψ</i> + Σ<sub>t</sub><i>ψ</i> = ∫∫Σ<sub>s</sub><i>ψ</i>′ d<b>Ω</b>′d<i>E</i>′ + (<i>χ</i>/4π<i>k</i>)∫<i>ν</i>Σ<sub>f</sub><i>φ</i>′ d<i>E</i>′. Il Monte Carlo la risolve giocando i neutroni uno alla volta: un volo di <i>s</i> = −ln <i>ξ</i> / Σ<sub>t</sub>, poi una diffusione, una cattura o una fissione.</p>
  <div class="btns"><button class="btn" data-act="trnew">Nuovo neutrone</button></div>
</div>
<div class="step">
  <h3>Dove la diffusione fallisce</h3>
  <p>La teoria della diffusione presuppone un flusso quasi uguale in tutte le direzioni. Questo non vale entro uno o due liberi cammini da una superficie e negli assorbitori forti. Confrontala con il flusso Monte Carlo in una lastra con sorgente uniforme mentre aumenti l'assorbimento.</p>
  <div class="ctl"><label for="tr-pa">Assorbimento Σ<sub>a</sub>/Σ<sub>t</sub></label><input id="tr-pa" type="range" data-bind="pa" data-instant min="0.05" max="0.8" step="0.05" value="0.5"><output data-show="pa" data-fmt="2"></output></div>
</div>
<div class="step">
  <h3>Iterazione di potenza</h3>
  <p>Per <i>k</i><sub>eff</sub>, i siti di fissione di ogni generazione diventano la sorgente della generazione successiva; <i>k</i> è il numero di siti accumulati per neutrone lanciato. Parti da una stima sbagliata, con tutti i neutroni su un bordo, e guarda la sorgente distribuirsi nel modo fondamentale.</p>
  <div class="btns"><button class="btn" data-act="trbad">Riparti da una stima sbagliata</button></div>
</div>
<div class="step">
  <h3>La sorgente è convergita?</h3>
  <p>L'entropia di Shannon <i>H</i> = −Σ <i>p</i><sub>b</sub> log<sub>2</sub> <i>p</i><sub>b</sub> della sorgente suddivisa in intervalli si stabilizza quando la sorgente si è assestata; solo allora si fa la media sulle generazioni. La barra d'errore su <i>k</i> si riduce come 1/√<i>N</i> con il numero di storie contate.</p>
  <div class="ctl"><label for="tr-n">Storie per generazione</label><input id="tr-n" type="range" data-bind="nh" data-instant min="100" max="2000" step="100" value="400"><output data-show="nh" data-fmt="0"></output></div>
</div>`,
};

Object.assign(WT.L.labels, {
  "vacuum": "vuoto",
  "glow: collision density": "bagliore: densità di collisioni",
  "amber glow: where collisions pile up": "bagliore ambra: dove le collisioni si accumulano",
  "tap the slab to start neutrons": "tocca la lastra per lanciare neutroni",
  "scatter": "diffusione",
  "capture": "cattura",
  "fission": "fissione",
  "leak": "fuga",
  "chance to fly at least s:  e^(−Σₜ s)": "probabilità di volare almeno s:  e^(−Σₜ s)",
  "{#} free paths": "{#} liberi cammini",
  "ξ = {#}  →  s = −ln ξ / Σₜ = {#} free paths": "ξ = {#}  →  s = −ln ξ / Σₜ = {#} liberi cammini",
  "infinite medium S/Σₐ": "mezzo infinito S/Σₐ",
  "Monte Carlo": "Monte Carlo",
  "diffusion": "diffusione",
  "flux": "flusso",
  "diffusion vs Monte Carlo: +{#} % at the surface, +{#} % in the middle": "diffusione vs Monte Carlo: +{#} % in superficie, +{#} % al centro",
  "diffusion vs Monte Carlo: +{#} % at the surface, {#} % in the middle": "diffusione vs Monte Carlo: +{#} % in superficie, {#} % al centro",
  "diffusion vs Monte Carlo: {#} % at the surface, +{#} % in the middle": "diffusione vs Monte Carlo: {#} % in superficie, +{#} % al centro",
  "diffusion vs Monte Carlo: {#} % at the surface, {#} % in the middle": "diffusione vs Monte Carlo: {#} % in superficie, {#} % al centro",
  "tap: drop the source there": "tocca: la sorgente va lì",
  "tap the slab to drop the whole source there": "tocca la lastra per mettere lì tutta la sorgente",
  "generation {#}": "generazione {#}",
  "source · dashed: fundamental mode": "sorgente · tratteggio: modo fondamentale",
  "fission source · dashed: fundamental mode": "sorgente di fissione · tratteggio: modo fondamentale",
  "source entropy H (bits)": "entropia della sorgente H (bit)",
  "inactive | active": "inattive | attive",
  "inactive  |  active generations": "generazioni inattive  |  attive",
  "k per generation": "k per generazione",
  "generation {#}: k = {#} · H = {#} bits": "generazione {#}: k = {#} · H = {#} bit",
  "starting…": "avvio…",
  "k_eff = {#} ± {#} ({#} × {#} histories) · diffusion {#}": "k_eff = {#} ± {#} ({#} × {#} storie) · diffusione {#}",
  "{#} generations, averaging starts after {#}": "{#} generazioni, la media parte dopo {#}",
  "illustrative one-group data": "dati illustrativi a un gruppo",
});
