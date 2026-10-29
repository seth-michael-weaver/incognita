/* Italian: densities (Capitolo 24, densità dei livelli raccordate) */
WT.L.ch.densities = {
  num: "Capitolo 24", title: "Densità dei livelli, raccordate", short: "Densità dei livelli",
  lead: "Il capitolo 8 univa un'asse dritta a un pendio. Questo capitolo scrive le due formule, mostra come si trova il punto di raccordo a partire dai livelli contati e che cosa succede quando un raccordo non esiste.",
  html: `
<div class="step">
  <h3>Il gas di Fermi con effetti di shell smorzati</h3>
  <p>La densità dei livelli predefinita del motore è la composizione di <b>Gilbert–Cameron</b>: un gas di Fermi ad alta energia, una temperatura costante più in basso. Il gas di Fermi richiede un solo numero, il parametro di densità dei livelli <i>a</i>, e a bassa energia quel numero risente delle shell. La forma di <b>Ignatyuk</b> fa agire in pieno la correzione di shell δW a bassa eccitazione e la smorza con un tasso γ, così che <i>a</i>(<i>U</i>) tenda al valore liscio <i>ã</i> quando il nucleo è caldo.</p>
  <div class="formula">a(U) = ã [1 + δW (1 − e<sup>−γU</sup>) / U] ,  ã = αA + βA<sup>2/3</sup> ,  γ = γ₁ / A<sup>1/3</sup></div>
  <div class="ctl"><label for="ld-dw">Correzione di shell δW (MeV)</label><input id="ld-dw" type="range" data-bind="dW" min="-6" max="4" step="0.1" value="1"><output data-show="dW" data-fmt="1"></output></div>
  <div class="formula">ρ<sub>F</sub>(E) = exp(2√(aU)) / (12√2 σ a<sup>1/4</sup> U<sup>5/4</sup>) ,  U = E − Δ ,  σ² = 0.01389 A<sup>5/3</sup> √(aU) / ã</div>
  <p>Le curve in alto sono <i>a</i>(<i>U</i>)/<i>ã</i> per diversi valori di δW; la tua è in grassetto. Sotto c'è ln ρ<sub>F</sub>. Un δW negativo (una shell chiusa) sopprime la densità di uno o due ordini di grandezza, e la soppressione svanisce solo lentamente: <i>a</i>(<i>U</i>) torna a <i>ã</i> come δW/<i>U</i>, così che anche a 20 MeV un δW di −6 MeV costa ancora un fattore di circa 40. Δ è lo spostamento di accoppiamento (pairing), 12/√A per ciascun tipo di nucleone accoppiato.</p>
</div>
<div class="step">
  <h3>Una retta tangente più in basso</h3>
  <p>Sotto l'energia di raccordo <i>E<sub>x</sub></i> il gas di Fermi viene sostituito dalla legge a <b>temperatura costante</b>. Due condizioni ne fissano i due parametri: uguale valore e uguale pendenza in <i>E<sub>x</sub></i>, quindi la retta è la tangente a ln ρ<sub>F</sub> in quel punto.</p>
  <div class="formula">ρ<sub>T</sub>(E) = (1/T) e<sup>(E − E₀)/T</sup> ,  1/T = d ln ρ<sub>F</sub>/dE |<sub>E<sub>x</sub></sub> ,  E₀ = E<sub>x</sub> − T ln[T ρ<sub>F</sub>(E<sub>x</sub>)]</div>
  <div class="ctl"><label for="ld-ex">Energia di raccordo Eₓ (MeV)</label><input id="ld-ex" type="range" data-bind="Ex" min="4.6" max="14" step="0.05" value="7"><output data-show="Ex" data-fmt="2"></output></div>
  <p>Fai scorrere <i>E<sub>x</sub></i> e la tangente ruota: un raccordo più alto dà una <i>T</i> più alta (una retta più piatta) e un <i>E</i>₀ più basso. Qualunque <i>E<sub>x</sub></i> produce una curva liscia. Sono i livelli contati a decidere quale sia quella giusta.</p>
</div>
<div class="step">
  <h3>Trovare il raccordo dai livelli contati</h3>
  <p>La scalinata è il numero di livelli noti sotto <i>E</i>, in scala logaritmica. Integrata, la legge a temperatura costante dà una retta, <i>N</i>(<i>E</i>) = e<sup>(E − E₀)/T</sup> + cost, che deve riprodurre il conteggio fra il livello <i>N<sub>L</sub></i> e il livello <i>N<sub>P</sub></i>, il tratto dello schema dei livelli ritenuto completo. È un'equazione per l'unica incognita <i>E<sub>x</sub></i>.</p>
  <div class="formula">F(E<sub>x</sub>) = e<sup>(E<sub>P</sub>−E₀)/T</sup> − e<sup>(E<sub>L</sub>−E₀)/T</sup> − (N<sub>P</sub> − N<sub>L</sub>) = 0</div>
  <div class="ctl"><label for="ld-ex2">Eₓ di prova (MeV)</label><input id="ld-ex2" type="range" data-bind="Ex" min="4.6" max="14" step="0.05" value="7"><output data-show="Ex" data-fmt="2"></output></div>
  <p>Il pannello in basso è <i>F</i>. Il motore, come TALYS, percorre un intervallo in 100 passi cercando un cambio di segno, poi lo biseca; la forbice che si stringe mostra la bisezione. Dove <i>F</i> = 0 la retta di prova si appoggia sulla scalinata.</p>
</div>
<div class="step">
  <h3>Quando il raccordo non c'è</h3>
  <p>A volte le due curve non si possono raccordare in modo liscio. In un nucleo con shell chiuse sia di protoni sia di neutroni, come il piombo-208, il gas di Fermi è trattenuto così in basso che nessuna retta tangente incontra i livelli contati: non esiste un'energia di raccordo. Il codice ripiega allora su regole empiriche per la temperatura e per il raccordo. I due pezzi si incontrano comunque, ma con uno spigolo: i valori coincidono e le pendenze no.</p>
  <div class="btns"><button class="btn ghost" data-act="tang" aria-pressed="false">Tangente all'energia di ripiego</button></div>
  <p>Premi il pulsante per vedere invece la tangente liscia. Con l'input predefinito lo spigolo compare per sette nuclei intorno al piombo, e rimuoverlo sposta la loro cattura neutronica fino al 20–30 %. Qui INCOGNITA riproduce TALYS; la modifica è stata segnalata agli sviluppatori di TALYS.</p>
  <div class="aside">I dettagli: per una doppia chiusura di shell il gas di Fermi a bassa energia resta freddo ovunque, e <i>F</i> non cambia mai segno. TALYS prende allora la temperatura empirica <i>T</i> = −0,25 + 10,2/√(<i>A</i>(1 + γδW)) e cerca l'energia in cui il gas di Fermi ha quella temperatura. Vicino a una doppia chiusura di shell la raggiunge solo molto al di sopra di qualunque raccordo ragionevole, o mai, quindi anche il raccordo ripiega sulle sistematiche, <i>E<sub>x</sub></i> = 2,33 + 253/<i>A</i> + Δ, e <i>E</i>₀ viene fissato in modo che il valore sia continuo. La <i>T</i> empirica non è la temperatura del gas di Fermi a quell'energia, quindi la pendenza salta: con l'input predefinito per ²⁰⁵,²⁰⁶Tl, ²⁰⁶⁻²⁰⁹Pb e ²¹⁰Bi, del 34–62 %. Prendere lì <i>T</i> dal gas di Fermi, come TALYS fa già quando <i>E<sub>x</sub></i> è dato nell'input, ripristina la tangente. Il disegno è un'illustrazione per un nucleo simile al piombo, con <i>ã</i> aumentato del 30 % così che il suo gas di Fermi resti sotto la temperatura empirica fino a circa 24 MeV, oltre l'intervallo di ricerca; la sua pendenza salta del 62 %.</div>
</div>
<div class="step">
  <h3>La spaziatura D₀ come verifica</h3>
  <p>All'energia di separazione del neutrone la densità si misura direttamente: la spaziatura media <i>D</i>₀ delle risonanze in onda s conta gli stati dell'unico spin e dell'unica parità che un neutrone lento può raggiungere. Per un bersaglio di spin 0 si tratta del solo <i>J</i><sup>π</sup> = ½⁺.</p>
  <div class="formula">1/D₀ = ρ(S<sub>n</sub>, ½, +) = ½ ρ<sub>F</sub>(S<sub>n</sub>) · (2J+1)/(2σ²) · e<sup>−(J+½)²/2σ²</sup></div>
  <div class="ctl"><label for="ld-as">Fattore di scala su ã</label><input id="ld-as" type="range" data-bind="as" min="0.8" max="1.2" step="0.005" value="1"><output data-show="as" data-fmt="3"></output></div>
  <p>Il disegno riguarda un nucleo composto simile al ferro-57 con l'<i>ã</i> globale, confrontato con il valore misurato di 25,4 ± 2,2 keV. Pochi punti percentuali su <i>ã</i> spostano <i>D</i>₀ di decine di punti percentuali: dove <i>D</i>₀ è misurato, la densità in <i>S<sub>n</sub></i> è ben vincolata, e dove non lo è, rappresenta la maggiore singola incertezza sulla cattura. Le valutazioni regolano <i>a</i> su <i>D</i>₀, e così fa l'impostazione predefinita di TALYS, che il motore segue: per un nucleo con <i>D</i>₀ misurato legge un parametro di densità dei livelli adattato a esso, e usa la formula globale solo per gli altri.</p>
  <div class="aside">Nel codice: <code>density/parameters.py</code> (ã, smorzamento di Ignatyuk, pairing, cutoff di spin), <code>density/models.py</code> (gas di Fermi, temperatura costante, tabelle), <code>density/matching.py</code> (la radice del raccordo, il ripiego empirico, i dettagli in singola precisione di TALYS riprodotti fedelmente). Il disegno usa i parametri globali di TALYS per ldmodel 1 con schemi di livelli e correzioni di shell illustrativi (e, per il caso simile al piombo, <i>ã</i> × 1,3); il <i>D</i>₀ misurato è il valore RIPL per il ⁵⁷Fe.</div>
</div>`,
};
Object.assign(WT.L.labels, {
  // axes
  "E (MeV)": "E (MeV)", "U (MeV)": "U (MeV)", "Eₓ (MeV)": "Eₓ (MeV)", "a(U) / ã": "a(U) / ã",
  "F = {#}": "F = {#}", "× e": "× e",
  // step 1
  "U = {#} MeV · a = {#} MeV⁻¹ · T ≈ √(U/a) = {#} MeV": "U = {#} MeV · a = {#} MeV⁻¹ · T ≈ √(U/a) = {#} MeV",
  "ρ_F (states per MeV), A = {#}": "ρ_F (stati per MeV), A = {#}",
  "dashed: δW = {#}": "tratteggio: δW = {#}",
  "at {#} MeV: ×{#} against δW = {#}": "a {#} MeV: ×{#} rispetto a δW = {#}",
  "at {#} MeV: ×{#}e{#} against δW = {#}": "a {#} MeV: ×{#}e{#} rispetto a δW = {#}",
  // step 2
  "T = {#} MeV": "T = {#} MeV",
  "joint Eₓ = {#} MeV": "raccordo Eₓ = {#} MeV",
  "E₀ = {#} MeV": "E₀ = {#} MeV",
  "Fermi gas": "gas di Fermi",
  "constant temperature": "temperatura costante",
  "ln ρ (states per MeV), A = {#}": "ln ρ (stati per MeV), A = {#}",
  // step 3
  "levels {#}–{#}": "livelli {#}–{#}",
  "levels {#} to {#}: taken as complete": "livelli da {#} a {#}: ritenuti completi",
  "number of levels below E": "numero di livelli sotto E",
  "trial Eₓ = {#} MeV: the line gives {#} levels for {#} counted": "Eₓ di prova = {#} MeV: la retta dà {#} livelli contro {#} contati",
  "F(Eₓ): predicted minus counted (signed log scale)": "F(Eₓ): previsti meno contati (scala log con segno)",
  "bisection step {#}: [{#}, {#}]": "passo di bisezione {#}: [{#}, {#}]",
  "root Eₓ = {#} MeV": "radice Eₓ = {#} MeV",
  // step 4
  "below: {#}/T with T = {#} MeV (Fermi-gas T)": "sotto: {#}/T con T = {#} MeV (T del gas di Fermi)",
  "below: {#}/T with T = {#} MeV (empirical T)": "sotto: {#}/T con T = {#} MeV (T empirica)",
  "above: Fermi gas, T = {#} MeV": "sopra: gas di Fermi, T = {#} MeV",
  "slope jumps by {#} % at Eₓ = {#} MeV": "la pendenza salta del {#} % a Eₓ = {#} MeV",
  "tangent at Eₓ = {#} MeV: no jump": "tangente a Eₓ = {#} MeV: nessun salto",
  "ln ρ, lead-like nucleus (A = {#}, δW = {#} MeV)": "ln ρ, nucleo simile al piombo (A = {#}, δW = {#} MeV)",
  "F changes sign: a root exists": "F cambia segno: esiste una radice",
  "F(Eₓ) never reaches zero: no matching energy": "F(Eₓ) non arriva mai a zero: nessuna energia di raccordo",
  // step 5
  "{#} keV": "{#} keV",
  "measured {#} ± {#} keV": "misurato {#} ± {#} keV",
  "computed D₀ = {#} keV": "D₀ calcolato = {#} keV",
  "ã × {#} = {#} MeV⁻¹ · σ² = {#} · ρ(Sₙ) = {#} per MeV": "ã × {#} = {#} MeV⁻¹ · σ² = {#} · ρ(Sₙ) = {#} per MeV",
  "ã × {#} = {#} MeV⁻¹ · σ² = {#} · ρ(Sₙ) = {#}e{#} per MeV": "ã × {#} = {#} MeV⁻¹ · σ² = {#} · ρ(Sₙ) = {#}e{#} per MeV",
  "s-wave resonances above Sₙ, {#} keV shown: about {#} levels": "risonanze in onda s sopra Sₙ, {#} keV mostrati: circa {#} livelli",
  "iron{#}-like compound nucleus, Sₙ = {#} MeV, spin and parity ½⁺": "nucleo composto simile al ferro{#}, Sₙ = {#} MeV, spin e parità ½⁺",
});
Object.assign(WT.L.glossary, {
  gilbertCameron: {
    term: "Gilbert–Cameron", aliases: ["Gilbert–Cameron"],
    short: "Una densità dei livelli composita: una legge a temperatura costante a bassa energia raccordata al gas di Fermi sopra un'energia di raccordo, con uguale valore e uguale pendenza nel punto di giunzione.",
    more: "Proposta da A. Gilbert e A. G. W. Cameron nel 1965. È la scelta predefinita di TALYS e del motore (ldmodel 1), con il parametro di densità dei livelli dipendente dall'energia di Ignatyuk.",
    chapter: "densities",
  },
  ignatyuk: {
    term: "Ignatyuk", aliases: ["Ignatyuk"],
    short: "La forma di Ignatyuk del parametro di densità dei livelli: la correzione di shell agisce in pieno a bassa eccitazione e si attenua con l'energia, così che a(U) tende al suo valore liscio.",
    formula: "a(U) = ã [1 + δW (1 − e^(−γU)) / U]",
    chapter: "densities",
  },
});
/* attributes referenced in the English chapter script (for the structure check): data-act="tang" */
