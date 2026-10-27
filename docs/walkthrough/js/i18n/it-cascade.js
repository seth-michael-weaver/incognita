/* Italian: cascade (Capitolo 11, la cascata) */
WT.L.ch.cascade = {
  num: "Capitolo 11", title: "Giù per la carta", short: "Cascata",
  lead: "Un'emissione raramente è la fine: il nucleo che resta è spesso ancora abbastanza caldo da emettere di nuovo.",
  html: `
<div class="step">
  <p>Un neutrone è uscito dal nucleo composto (a sinistra), e il <b>nucleo residuo</b> che lascia (a destra) è ancora caldo. La palla arancione è l'energia. Lo stato fondamentale del residuo sta più in alto, di quanto vale l'<b>energia di separazione</b> S<sub>n</sub> del neutrone, il costo per estrarlo.</p>
  <p>Ogni volta che esce un neutrone, la palla scende di quanto vale l'energia cinetica del neutrone. Dove si ferma è l'<b>eccitazione</b> del residuo, la sua energia in avanzo; i punti a destra contano gli arrivi.</p>
  <div class="ctl"><label for="cs-e">Energia del neutrone</label><input id="cs-e" type="range" data-bind="E" min="1" max="30" step="0.5" value="15"><output data-show="E" data-fmt="1"></output></div>
  <p>I neutroni emessi sono di solito lenti, quindi la maggior parte delle discese è breve. I punti blu stanno sopra la soglia neutronica tratteggiata: possono permettersi un secondo neutrone, la reazione (n,2n). Sotto circa 11 MeV nessuno ci arriva.</p>
</div>
<div class="step">
  <h3>Una passeggiata sulla carta</h3>
  <p>Le correnti sono reazioni che attraversano un angolo della <b>carta dei nuclidi</b>, i nuclei disposti secondo il numero di neutroni N (in orizzontale) e il numero di protoni Z (in verticale). Ciascuna parte dalla casella evidenziata del nucleo composto; ogni casella porta il nome della reazione che finisce lì.</p>
  <p>Un <em class="n">neutrone</em> emesso sposta di una casella a sinistra, un <em class="p">protone</em> di una in basso, una <em class="a">particella alfa</em> (due protoni, due neutroni) di due in diagonale. La larghezza della corrente è quanto compie quel passo; la tonalità e la percentuale indicano dove finiscono le reazioni.</p>
  <div class="btns"><button class="btn" data-act="fire">Lancia 200 reazioni</button></div>
  <p>Ogni passo costa da 7 a 11 MeV di energia di separazione, quindi anche a 30 MeV il percorso conta al massimo tre o quattro passi.</p>
</div>
<div class="step">
  <h3>Dall'alto in basso, intervallo per intervallo</h3>
  <p>Il motore svuota ogni nucleo dall'alto in basso, una fetta di energia, o <b>intervallo</b>, alla volta. A destra, il residuo della prima emissione; a sinistra, suo figlio, con un neutrone in meno. Le palle arancioni sono reazioni in attesa in ogni intervallo. Qui gli intervalli sono di 1 MeV; il motore ne usa circa 40 per nucleo, dimensionati sull'energia disponibile.</p>
  <p>Quando l'indicatore passa su un intervallo, ogni palla prende un'uscita secondo la competizione del capitolo 9: un fotone (<em class="g">γ</em>) la fa scendere a un intervallo più basso, un <em class="n">neutrone</em> la porta nel figlio, un protone o un'alfa la portano fuori dall'immagine. Sotto tutte le soglie, i fotoni portano il resto allo stato fondamentale (grigio). Poi tocca al figlio.</p>
  <div class="ctl"><label for="cs-e3">Energia del neutrone</label><input id="cs-e3" type="range" data-bind="E" min="8" max="30" step="0.5" value="18"><output data-show="E" data-fmt="1"></output></div>
  <div class="btns"><button class="btn ghost" data-act="restart">Ricomincia</button></div>
  <p>I fotoni scendono soltanto, e ogni nucleo viene completato prima dei suoi figli, quindi niente arriva su un intervallo già svuotato.</p>
</div>
<div class="step">
  <h3>Dare un nome alla storia</h3>
  <p>Si riproduce una reazione alla volta: l'indicatore salta sulla carta e ogni particella emessa cade nel vassoio. Il vassoio pieno dà il nome al <b>canale esclusivo</b>, come (n,2n); i fotoni non contano. Il motore assegna a ogni canale la sua sezione d'urto (la sua probabilità, espressa come un'area efficace del bersaglio).</p>
  <div class="btns"><button class="btn ghost" data-act="next">Canale successivo</button></div>
  <p>Scorrili. (n,np) viene riprodotto due volte, prima con il neutrone e poi con il protone: stessa casella, stesso vassoio, un solo canale. Poi un deutone fantasma (un protone e un neutrone legati) raggiunge quella casella con un solo salto: il suo vassoio dice d, un canale diverso, (n,d).</p>
</div>
<div class="step">
  <h3>Dove finisce tutto</h3>
  <p>Ogni casella ora ha dei ripiani: color inchiostro per lo <b>stato fondamentale</b>, verde (in due caselle) per un <b>isomero</b>, uno stato eccitato che vive abbastanza da contare come un prodotto a sé. L'altezza del mucchio è la <b>produzione di residui</b>: quanto di ogni nucleo hanno prodotto le reazioni.</p>
  <div class="ctl"><label for="cs-e2">Energia del neutrone</label><input id="cs-e2" type="range" data-bind="E" min="1" max="30" step="0.5" value="14"><output data-show="E" data-fmt="1"></output></div>
  <div class="btns"><button class="btn" data-act="fire">Lancia 200 reazioni</button></div>
  <p>Trascina l'energia: il prossimo gruppo la usa e i mucchi vecchi sbiadiscono. La produzione si allontana dal punto di partenza man mano che possono uscire più particelle. Ogni storia finisce su un ripiano, e una misura per attivazione vede esattamente questi mucchi: si irraggia un campione, poi si contano i decadimenti di ogni prodotto.</p>
  <div class="aside">Nel codice: <code>emission/multiple.py</code> (il ciclo su nuclei e intervalli, la cascata γ), <code>emission/feeding.py</code> (griglie e dati d'ingresso per ogni nucleo della catena), <code>compound/continuum.py</code> (il decadimento di un intervallo), <code>emission/channels.py</code> (canali esclusivi, produzione di residui, rami isomerici), <code>emission/binary.py</code> (la contabilità della prima emissione).</div>
</div>`,
};
Object.assign(WT.L.labels, {
  // reaction names on the squares (unchanged in Italian)
  "(n,γ)": "(n,γ)", "(n,n′)": "(n,n′)", "(n,{#}n)": "(n,{#}n)", "(n,p)": "(n,p)", "(n,np)": "(n,np)", "(n,{#}np)": "(n,{#}np)",
  "(n,{#}p)": "(n,{#}p)", "(n,n{#}p)": "(n,n{#}p)", "(n,α)": "(n,α)", "(n,nα)": "(n,nα)",
  "compound": "composto", "target": "bersaglio",
  "N{#}": "N{#}", "N": "N", "N+{#}": "N+{#}", "Z": "Z", "Z{#}": "Z{#}",
  "neutron number →": "numero di neutroni →",
  // scene 1
  "levels": "livelli",
  "Sₙ {#} MeV": "Sₙ {#} MeV", "Sₙ = {#} MeV": "Sₙ = {#} MeV",
  "ground": "fondamentale",
  "residual": "residuo", "residual (one neutron fewer)": "residuo (un neutrone in meno)",
  "n threshold": "soglia n", "its neutron threshold": "la sua soglia neutronica",
  "{#} MeV": "{#} MeV",
  "drop = neutron's kinetic energy": "discesa = energia cinetica del neutrone",
  "{#} % land above the threshold: a second neutron can leave": "{#} % arriva sopra la soglia: può uscire un secondo neutrone",
  "<{#} % land above the threshold: a second neutron can leave": "<{#} % arriva sopra la soglia: può uscire un secondo neutrone",
  "all land below the threshold: only photons remain": "tutti arrivano sotto la soglia: restano solo fotoni",
  "{#} % above threshold: (n,{#}n) possible": "{#} % sopra la soglia: (n,{#}n) possibile",
  "<{#} % above threshold: (n,{#}n) possible": "<{#} % sopra la soglia: (n,{#}n) possibile",
  "all below threshold: photons only": "tutti sotto la soglia: solo fotoni",
  // scene 2
  "incoming neutron: {#} MeV": "neutrone incidente: {#} MeV",
  "shade and % = where reactions end": "tonalità e % = dove finiscono",
  "stream width = flow · shade and % = share of reactions that end in that nucleus": "larghezza = flusso · tonalità e % = quota di reazioni che finiscono in quel nucleo",
  // scene 3
  "residual (first step)": "residuo (primo passo)",
  "daughter: n fewer": "figlio: un n in meno", "daughter (one neutron fewer)": "figlio (un neutrone in meno)",
  "now: {#}–{#} MeV": "ora: {#}–{#} MeV", "{#}–{#} MeV": "{#}–{#} MeV",
  "done: {#} left by proton or alpha, the rest sit on ground states": "fatto: {#} usciti con protone o alfa, il resto è negli stati fondamentali",
  "done: everything sits on a ground state": "fatto: tutto è in uno stato fondamentale",
  "orange ball = reactions waiting in a bin · grey = settled on the ground state · pale bins = already emptied": "palla arancione = reazioni in attesa · grigio = nello stato fondamentale · intervalli chiari = già svuotati",
  // scene 4
  "collected": "raccolto",
  "tray: d": "vassoio: d",
  "a deuteron lands on the same square, but its tray reads d: channel (n,d)": "un deutone arriva nella stessa casella, ma il suo vassoio dice d: canale (n,d)",
  "tray: n n  →  (n,{#}n)": "vassoio: n n  →  (n,{#}n)",
  "tray: n  →  (n,n′)": "vassoio: n  →  (n,n′)",
  "tray: p  →  (n,p)": "vassoio: p  →  (n,p)",
  "tray: n p  →  (n,np)": "vassoio: n p  →  (n,np)",
  "tray: n p  →  (n,np) · same square, same tray": "vassoio: n p  →  (n,np) · stessa casella, stesso vassoio",
  "tray: a  →  (n,α)": "vassoio: a  →  (n,α)",
  "tray: n n n  →  (n,{#}n)": "vassoio: n n n  →  (n,{#}n)",
  "tray empty, only photons: (n,γ), capture": "vassoio vuoto, solo fotoni: (n,γ), cattura",
  "each emitted particle falls into the tray": "ogni particella emessa cade nel vassoio",
  "no particle gets out: only photons": "nessuna particella esce: solo fotoni",
  "incoming neutron: {#} MeV · channel {#} of {#}": "neutrone incidente: {#} MeV · canale {#} di {#}",
  // scene 5
  "isomer": "isomero",
  "batch of {#} at {#} MeV": "gruppo di {#} a {#} MeV",
  "ink shelf: ground state · green: isomer": "inchiostro: stato fondamentale · verde: isomero",
  "ink shelf: ground state · green shelf: isomer · pile height = how much of that nucleus was made": "ripiano inchiostro: fondamentale · verde: isomero · altezza = quanto di quel nucleo è stato prodotto",
});
