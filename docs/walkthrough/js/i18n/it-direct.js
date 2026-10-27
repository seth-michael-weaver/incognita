/* Italian: direct (Capitolo 6, reazioni dirette) */
WT.L.ch.direct = {
  num: "Capitolo 6", title: "Un colpo di striscio", short: "Reazioni dirette",
  lead: "Non ogni neutrone che raggiunge il nucleo viene inghiottito. Alcuni ne sfiorano la superficie, gli danno una spinta e proseguono il volo.",
  html: `
<div class="step">
  <p>Un neutrone che sfiora appena il nucleo può spingerlo una volta in un livello eccitato e proseguire, quasi sempre in avanti e solo un po' più lento. Questa è una <b>reazione diretta</b>: un solo passo, che si conclude in circa 10⁻²² secondi. Qui un neutrone passa a distanza <i>b</i>, il <b>parametro d'urto</b>, misurato in raggi nucleari <i>R</i>; l'anello punteggiato è la pelle del nucleo.</p>
  <div class="ctl"><label for="di-b">Mira b (in raggi)</label><input id="di-b" type="range" data-bind="b" min="0" max="1.5" step="0.01" value="1.0"><output data-show="b" data-fmt="2"></output></div>
  <p>Trascina <i>b</i>. Sotto circa 0,8 il neutrone viene inghiottito. Vicino a 1 sfiora il nucleo e lo lascia nel suo primo livello eccitato, 2⁺. Sopra circa 1,2 lo manca e viene solo deviato: <b>diffusione elastica</b>, con il nucleo invariato.</p>
</div>
<div class="step">
  <h3>Mettere in rotazione un nucleo allungato</h3>
  <p>Una spinta mette in rotazione un nucleo allungato (capitolo 1) e lo fa salire lungo la scala della sua <b>banda rotazionale</b>: 0⁺, 2⁺, 4⁺, 6⁺, 8⁺. Il neutrone può spingere il nucleo verso l'alto e il nucleo può restituire la spinta, quindi nessun livello si può calcolare da solo. Il motore li risolve tutti insieme: <b>canali accoppiati</b>, dove ogni canale è un esito, qui un livello della banda.</p>
  <div class="btns"><button class="btn" data-act="kick">Spingilo su di un livello</button><button class="btn ghost" data-act="rpause">Pausa / riprendi</button></div>
  <div class="ctl"><label for="di-beta">Deformazione β₂</label><input id="di-beta" type="range" data-bind="beta2" min="0.05" max="0.4" step="0.01" value="0.25"><output data-show="beta2" data-fmt="2"></output></div>
  <p>Gli archi mostrano quali livelli sono collegati: <i>λ</i> = 2, l'allungamento complessivo, collega i vicini; <i>λ</i> = 4, un rigonfiamento più fine, ne salta due. Trascina <i>β₂</i>: un nucleo più allungato collega i suoi livelli più fortemente, e gli archi si ispessiscono. Poiché la banda viene risolta insieme all'onda entrante, i coefficienti di trasmissione escludono già ciò che essa si prende.</p>
</div>
<div class="step">
  <h3>Increspature su una sfera</h3>
  <p>Un nucleo rotondo può incresparsi, e l'energia di increspatura arriva in pacchetti uguali chiamati <b>fononi</b>. Un fonone dell'increspatura pallone–disco (<i>λ</i> = 2) dà il livello 2⁺; due ne danno tre, 0⁺, 2⁺ e 4⁺, al doppio dell'energia. Per raggiungerli servono due spinte di fila. Il motore risolve questi livelli insieme allo stato fondamentale.</p>
  <div class="ctl"><label for="di-lam">Forma dell'increspatura λ</label><input id="di-lam" type="range" data-bind="lam" min="2" max="3" step="1" value="2" data-instant><output data-show="lam" data-fmt="0"></output></div>
  <div class="btns"><button class="btn ghost" data-act="ph1">Un fonone</button><button class="btn ghost" data-act="ph2">Due fononi</button></div>
  <p>Imposta <i>λ</i> = 3 per un'increspatura a forma di pera, il cui primo livello è 3⁻. Premi i pulsanti per aggiungere uno o due fononi.</p>
</div>
<div class="step">
  <h3>Una spinta, una volta</h3>
  <p>Per la maggior parte dei livelli il collegamento è debole e basta una spinta: la <b>DWBA</b> (approssimazione di Born a onde distorte). L'onda entrante del capitolo 5 spinge il nucleo una volta, sul bordo, dove il potenziale scende da profondo a zero; il bordo si illumina dove lo colpiscono le creste. L'onda circolare che si allarga sono i neutroni che hanno lasciato il nucleo eccitato.</p>
  <div class="ctl"><label for="di-bd">Deformazione del livello β</label><input id="di-bd" type="range" data-bind="bd" min="0.02" max="0.4" step="0.01" value="0.2"><output data-show="bd" data-fmt="2"></output></div>
  <p>Trascina <i>β</i>: il bordo oscilla di più e i cerchi si illuminano, come <i>β</i>²: doppia deformazione, quattro volte tanti. Il motore prende il <i>β</i> di ogni livello da valori misurati, o da sistematiche dove non se ne conosce nessuno. Come si distribuiscono in angolo i neutroni diffusi è un'uscita aggiuntiva opzionale.</p>
</div>
<div class="step">
  <h3>Si muove l'intero nucleo</h3>
  <p>Tutti i nucleoni possono muoversi insieme: respirare, schiacciarsi e allungarsi, oppure oscillare verso una forma a pera. Sono le <b>risonanze giganti</b>. In questo nucleo di massa media si trovano tra circa 7 e 25 MeV, ciascuna larga diversi MeV, troppo ampia per contare come un solo livello; le gobbe segnano l'<b>energia di eccitazione</b> di ciascuna.</p>
  <p>Il motore fissa l'intensità totale di ciascuna con una <b>regola di somma</b>, un limite dato dalla fisica di base a quanto fortemente un nucleo può rispondere, e la distribuisce come una gobba sopra l'ultimo livello noto. Queste gobbe, più le spinte verso livelli alti, formano il <b>continuo collettivo</b>.</p>
  <div class="btns"><button class="btn ghost" data-act="mono">Respiro</button><button class="btn ghost" data-act="quad">Schiacciamento</button><button class="btn ghost" data-act="oct">Pera</button></div>
  <p>La più nota, i protoni che oscillano contro i neutroni (la risonanza gigante di dipolo), soprattutto assorbe ed emette luce, quindi appartiene al capitolo 10.</p>
</div>
<div class="step">
  <h3>Dritto in un'orbita</h3>
  <p>Un neutrone libero può cadere direttamente in un'<b>orbita</b> vuota della buca (un'energia permessa per un neutrone all'interno) ed emettere l'energia in eccesso come un <em class="g">fotone</em>. Il nucleo non si riscalda mai. Questa è la <b>cattura diretta</b>. Il motore può calcolarla con la stessa buca del capitolo 5: l'onda libera fuori, l'orbita legata dentro, il fotone che le collega. È opzionale e disattivata per impostazione predefinita.</p>
  <div class="btns"><button class="btn" data-act="drop">Fai cadere un neutrone</button></div>
  <p>La cattura diretta conta soprattutto dove la via abituale, spartire l'energia del neutrone, è debole: nuclei leggeri e nuclei lontani dalla stabilità, con pochi livelli molto distanziati.</p>
</div>
<div class="step">
  <h3>Il diretto prende per primo la sua parte</h3>
  <p>Il motore ripartisce in ordine la sezione d'urto di reazione del capitolo 5: prima le reazioni dirette, poi le collisioni rapide, e solo ciò che resta forma un nucleo composto. Nell'immagine ogni neutrone va incontro a uno di tre destini: <b>diretto</b> (sfiora e prosegue), rapido (fa uscire un nucleone prima che l'energia si distribuisca: <b>pre-equilibrio</b>, capitolo 7) o inghiottito (un <b>nucleo composto</b>, capitolo 8). I mucchi li contano.</p>
  <div class="ctl"><label for="di-e">Energia del neutrone (MeV)</label><input id="di-e" type="range" data-bind="E" min="1" max="60" step="0.5" value="14"><output data-show="E" data-fmt="1"></output></div>
  <p>Trascina l'energia e guarda i mucchi riempirsi di nuovo. A pochi MeV quasi ogni neutrone viene inghiottito. A decine di MeV, reazioni dirette e collisioni rapide insieme ne prendono una grossa parte.</p>
  <div class="aside">Nel codice: <code>ecis/formfactor.py</code>, <code>ecis/coupling.py</code>, <code>ecis/solver.py</code> (potenziale deformato, canali accoppiati per rotori e vibratori), <code>ecis/dwba.py</code> e <code>direct/dwba.py</code> (spinta singola, risonanze giganti, continuo collettivo), <code>direct/racapcalc.py</code> (cattura diretta, opzionale, disattivata per impostazione predefinita), <code>compound/normalization.py</code> (la contabilità).</div>
</div>`,
};
Object.assign(WT.L.labels, {
  // scene: aim
  "skin (surface)": "pelle (superficie)",
  "b = {#} R": "b = {#} R",
  "absorbed: its energy is shared by all nucleons": "assorbito: la sua energia si distribuisce fra tutti i nucleoni",
  "{#}⁺ level": "livello {#}⁺",
  "one push leaves the nucleus on {#}⁺; neutron flies on": "una spinta lascia il nucleo in {#}⁺; il neutrone prosegue",
  "a miss: deflected, nucleus unchanged (elastic)": "mancato: deviato, nucleo invariato (elastica)",
  // scene: rotor
  "at rest: {#}⁺": "a riposo: {#}⁺",
  "rotating: {#}⁺": "in rotazione: {#}⁺",
  "rotating: {#}⁺ (paused)": "in rotazione: {#}⁺ (in pausa)",
  "λ = {#}": "λ = {#}",
  "levels solved together": "livelli risolti insieme",
  // scene: vibrator
  "quadrupole ripple: football ↔ disc": "increspatura di quadrupolo: pallone ↔ disco",
  "octupole ripple: pear ↔ pear": "increspatura di ottupolo: pera ↔ pera",
  "{#}⁺  no phonon": "{#}⁺  nessun fonone",
  "{#}⁺  one phonon": "{#}⁺  un fonone",
  "{#}⁻  one phonon": "{#}⁻  un fonone",
  "{#}⁺ {#}⁺ {#}⁺  two phonons": "{#}⁺ {#}⁺ {#}⁺  due fononi",
  "{#}⁺ {#}⁺ {#}⁺ {#}⁺  two phonons": "{#}⁺ {#}⁺ {#}⁺ {#}⁺  due fononi",
  "one push": "una spinta",
  "two pushes": "due spinte",
  "two phonons": "due fononi",
  "equal energy steps": "gradini di energia uguali",
  // scene: DWBA
  "rim: the push happens here": "bordo: qui avviene la spinta",
  "incoming wave": "onda entrante",
  "outgoing: nucleus left excited": "uscente: nucleo lasciato eccitato",
  "outgoing circles: the nucleus left on an excited level": "cerchi uscenti: il nucleo lasciato su un livello eccitato",
  "push strength ∝ β²: {#}× that at β = {#}": "intensità della spinta ∝ β²: {#}× quella a β = {#}",
  // scene: giant resonances
  "breathing": "respiro",
  "squash and stretch": "schiacciare e allungare",
  "pear": "pera",
  "breathing (monopole)": "respiro (monopolo)",
  "squash and stretch (quadrupole)": "schiacciare e allungare (quadrupolo)",
  "pear-shaped (octupole), low and high": "a pera (ottupolo), bassa e alta",
  "about {#} MeV up": "a circa {#} MeV",
  "last known level": "ultimo livello noto",
  "excitation energy (MeV) →": "energia di eccitazione (MeV) →",
  // scene: direct capture
  "free: outside the nucleus": "libero: fuori dal nucleo",
  "empty orbit": "orbita vuota",
  "drops straight in; a photon carries off the spare energy": "cade dritto dentro; un fotone porta via l'energia in eccesso",
  // scene: ledger
  "direct": "diretta",
  "fast (pre-eq.)": "rapida (pre-eq.)",
  "compound": "composto",
  "direct: grazed, flew on": "diretta: ha sfiorato, è proseguito",
  "fast collision: one out at once": "collisione rapida: uno esce subito",
  "compound: swallowed": "composto: inghiottito",
  "{#}% (model {#}%)": "{#}% (modello {#}%)",
  "{#}% seen · model {#}%": "{#}% visto · modello {#}%",
  "{#} MeV neutrons on a medium-mass nucleus (illustrative shares)": "neutroni da {#} MeV su un nucleo di massa media (quote illustrative)",
});
