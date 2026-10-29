/* Italian: static page text (index.html data-i18n keys) and kit UI strings */
Object.assign(WT.L.ui, {
  lang_label: "Lingua", nav_teach: "Docenti",
  brand: "Dentro una reazione nucleare", nav_physics: "La fisica", nav_data: "Tutti i nuclidi", nav_board: "Classifica", menu: "Menu", site_nav: "Sito",
  ways_h: "Altre porte d'ingresso", ways_more: "Oppure continua a scorrere: la fisica comincia qui ↓",
  way1_k: "Esplora", way1_t: "Tutti i nuclidi", way1_p: "Sezioni d'urto previste per 6168 nuclidi accanto a ogni misura revisionata. Cerca qualsiasi isotopo e guarda ogni insieme di dati.", way1_go: "Apri i dati →",
  way2_k: "Confronta", way2_t: "Classifica", way2_p: "Come il motore e il suo prodotto di dati si confrontano con altri codici di reazione e altre librerie, giudicati rispetto alle misure, sconfitte per prime.", way2_go: "Vedi i punteggi →",
  way3_k: "Eseguilo", way3_t: "Il codice", way3_p: "Qui tutto è aperto. Clona il repository, consulta qualsiasi curva o esegui tu stesso il motore.", way3_go: "GitHub →",
  title: "Dentro una reazione nucleare",
  kicker: "Una spiegazione interattiva del motore di reazioni INCOGNITA",
  h1: "Dentro una reazione nucleare",
  hero1: "Lancia un neutrone contro un nucleo atomico e qualcosa torna fuori. Può essere il neutrone stesso, che rimbalza. Può essere un protone, una particella alfa (un gruppo compatto di 2 protoni e 2 neutroni) o un lampo di luce. Un nucleo pesante può perfino spezzarsi in due.",
  hero2: "Quale di queste cose succede, e con che frequenza? Questa pagina mostra, un passo alla volta, come il nostro software risponde a questa domanda. Scorri verso il basso e prova i comandi lungo la strada. Le immagini seguono la stessa fisica del motore; i numeri che mostrano sono illustrativi.",
  scrollcue: "Scorri per cominciare ↓",
  hero_tag: "Un'esplorazione visiva della fisica nucleare",
  hero_aud: "Per gli studenti e per chi si avvicina alla fisica nucleare, e per i docenti che insegnano loro. Addetti ai lavori: i dati di ogni nuclide sono in <a href=\"data.html\" data-keep-lang>Tutti i nuclidi</a>.",
  hero_fire: "Lancia un neutrone",
  hero_hint: "o fai clic in un punto qualsiasi dell'immagine",
  credit_idx: "Il motore INCOGNITA è un port di <a href=\"https://doi.org/10.1140/epja/s10050-023-01034-3\">TALYS-2</a> (A. J. Koning, S. Hilaire, S. Goriely) e usa la banca dati di struttura nucleare di TALYS. Ciò che INCOGNITA aggiunge è <a href=\"#code\">elencato, opzione per opzione, alla fine di questa pagina</a>.",
  coda_h2: "Dove vive tutto questo nel codice",
  coda_p1: "Ogni fase descritta sopra è un pacchetto in <code>physics/hf</code>, e il motore li chiama nell'ordine in cui li hai appena letti. Il motore è un port di TALYS-2.x, il consolidato codice di reazioni. Ciò che aggiunge sta dietro opzioni con un nome all'interno degli stessi pacchetti: la maggior parte è disattivata per impostazione predefinita, alcune correzioni sono attive, e ciascuna può essere riportata da sola al TALYS originale.",
  coda_table: `
    <thead><tr><th>Capitolo</th><th>Che cosa fa</th><th>Codice</th></tr></thead>
    <tbody>
      <tr><td><a href="#structure">1</a></td><td>Masse, livelli, deformazione, dati di risonanza</td><td><code>structure/</code></td></tr>
      <tr><td><a href="#omp">5</a></td><td>Modello ottico, coefficienti di trasmissione (con quale facilità le particelle entrano ed escono)</td><td><code>omp/</code></td></tr>
      <tr><td><a href="#direct">6</a></td><td>Canali accoppiati, DWBA, risonanze giganti, cattura diretta (opzionale)</td><td><code>ecis/</code>, <code>direct/</code></td></tr>
      <tr><td><a href="#preeq">7</a></td><td>Pre-equilibrio: modello a eccitoni, pickup e knockout, emissione multipla</td><td><code>preeq/</code>, <code>density/particle_hole.py</code></td></tr>
      <tr><td><a href="#compound">8</a></td><td>Densità dei livelli (stati per MeV), distribuzione dello spin</td><td><code>density/</code></td></tr>
      <tr><td><a href="#decay">9</a></td><td>Scegliere un'uscita (Hauser–Feshbach), fluttuazioni delle larghezze</td><td><code>compound/</code></td></tr>
      <tr><td><a href="#gamma">10</a></td><td>Funzione di forza fotonica e trasmissione γ; livelli discreti e isomeri</td><td><code>gamma/</code><br><code>structure/levels.py</code></td></tr>
      <tr><td><a href="#cascade">11</a></td><td>La cascata di emissioni di particelle e γ, canali esclusivi, residui</td><td><code>emission/</code></td></tr>
      <tr><td><a href="#fission">12</a></td><td>Barriere di fissione e trasmissione</td><td><code>fission/</code></td></tr>
      <tr><td><a href="#measure">17</a></td><td>Spettri di emissione, distribuzioni angolari e sezioni d'urto doppiamente differenziali (opzionale, solo in uscita)</td><td><code>specout.py</code><br><code>specang.py</code></td></tr>
      <tr><td><a href="#measure">17</a></td><td>Cattura su bersagli eccitati termicamente e tassi stellari (opzionale)</td><td><code>astro/stellar.py</code></td></tr>
      <tr><td><a href="#measure">17</a></td><td>Incertezza con molte varianti casuali (Total Monte Carlo)</td><td><code>tmc.py</code></td></tr>
      <tr><td></td><td>Il programma che esegue le fasi in ordine, e nuclei di calcolo opzionali in C per la velocità</td><td><code>engine.py</code><br><code>engine_c.py</code>, <code>native/</code></td></tr>
      <tr><td></td><td>Tutti i valori predefiniti e le opzioni, letti una volta all'inizio; anche i parametri adattati nuclide per nuclide di TENDL, applicati come li applica TALYS (opzionale)</td><td><code>input/</code></td></tr>
    </tbody>
  `,
  coda_h3_added: "Aggiunto oltre TALYS",
  coda_p_added: "Le righe segnate <b>Attivo</b> funzionano per impostazione predefinita, quindi un'esecuzione predefinita non coincide più esattamente con TALYS; ciascuna si può disattivare con una parola chiave o una variabile d'ambiente. Le altre restano disattivate se non le attivi.",
  coda_table_added: `
    <thead><tr><th>Capitolo</th><th>Che cosa cambia</th><th>Codice</th></tr></thead>
    <tbody>
      <tr><td><a href="#cascade">11</a></td><td><b>Attivo.</b> Contabilità del flusso chiusa: residui conservati fino a 10⁻⁹ mb (TALYS: 10⁻³ mb), conservati i residui un passo oltre la finestra di cascata di TALYS, fino a 8 di ciascuna particella emessa nei canali esclusivi, contati tutti i rami di diseccitazione ripetuti di un livello</td><td><code>emission/fluxclose.py</code><br><code>emission/channels.py</code><br><code>kevleak2.py</code></td></tr>
      <tr><td><a href="#decay">9</a></td><td><b>Attivo.</b> L'intervallo più alto del primo nucleo composto viene riempito come lo riempiono i fotoni primari (con peso E<sub>γ</sub>³), non in modo uniforme</td><td><code>compound/nnleak.py</code></td></tr>
      <tr><td><a href="#decay">9</a></td><td><b>Attivo.</b> Niente elastica composta mediata sotto le prime risonanze (sotto 1 keV), dove l'elastica è diffusione di potenziale</td><td><code>lowepot.py</code></td></tr>
      <tr><td><a href="#decay">9</a></td><td><b>Attivo.</b> Bersagli deformati senza fissione: le uscite di neutroni verso livelli fuori dalla banda accoppiata usano la trasmissione a canali accoppiati</td><td><code>compound/ccexitnb.py</code></td></tr>
      <tr><td><a href="#omp">5</a></td><td><b>Attivo.</b> L'emissione alfa vede un potenziale che dipende dalla temperatura del residuo; i proiettili alfa entrano con il modello alfa 6; i potenziali di tritone ed elione includono le dimensioni del proiettile</td><td><code>omp/alphatemp.py</code><br><code>alphaentr.py</code><br><code>omp/tfold.py</code></td></tr>
      <tr><td><a href="#fission">12</a></td><td><b>Attivo.</b> Trasmissione unidimensionale esatta attraverso ciascuna gobba della barriera</td><td><code>fission/wkb.py</code></td></tr>
      <tr><td><a href="#gamma">10</a></td><td><b>Attivo.</b> I fattori di intensità E1/M1 per singolo nucleo, quando un'esecuzione li fornisce, sono sostituiti da un'unica funzione globale della deformazione</td><td><code>gamma/ftglobal.py</code></td></tr>
      <tr><td><a href="#compound">8</a></td><td><b>Attivo.</b> Bersagli senza una propria spaziatura delle risonanze D₀ misurata: la densità dei livelli del continuo del bersaglio sopra max(E<sub>cut</sub> + 2, S<sub>n</sub> − 6) MeV viene aumentata di un fattore dato da un'unica regola globale basata su parità, shell e deformazione. Aggiunta per trasformare in pareggio la sconfitta in (n,p) vicino alla soglia contro l'input predefinito di TALYS-2; peggiora leggermente alcune viste di cattura, (n,2n) e (n,α), un danno accettato e registrato</td><td><code>density/npwindow.py</code></td></tr>
      <tr><td><a href="#gamma">10</a></td><td>Un modo a forbice più intenso nei nuclei deformati, da sistematiche più recenti che concordano con le misure di Oslo (circa 4–5× negli attinidi); oppure una variante che scala la sua energia e la sua intensità con la deformazione</td><td><code>gamma/scissors.py</code></td></tr>
      <tr><td><a href="#gamma">10</a></td><td>Funzione di forza fotonica riscalata perché ogni nucleo riproduca la sua intensità radiativa misurata ⟨Γγ⟩/D₀, per tutti i nuclei della cascata, non solo il primo</td><td><code>gamma/ggnorm.py</code></td></tr>
      <tr><td><a href="#gamma">10</a></td><td>Modo a forbice più intenso e normalizzazione di ⟨Γγ⟩ solo per i nuclei più pesanti (Z ≥ 88), pensati per la cattura a energie di keV</td><td><code>gamma/actphys.py</code></td></tr>
      <tr><td><a href="#gamma">10</a></td><td>Una nostra costante per la larghezza E1 al posto della tabella di TALYS derivata da TENDL (la imposta la ricetta senza dati che distribuiamo)</td><td><code>gamma/e1_width.py</code></td></tr>
      <tr><td><a href="#gamma">10</a></td><td>Intensità E2 collettiva delle bande rotazionali nel quasi-continuo</td><td><code>gamma/isoe2.py</code></td></tr>
      <tr><td><a href="#omp">5</a></td><td>Un aggiustamento regionale della buca ottica per bersagli deformati di terre rare, adattato a S₀ e S₁ misurati senza dati di cattura</td><td><code>omp/regional.py</code></td></tr>
      <tr><td><a href="#omp">5</a></td><td>Le funzioni di forza neutroniche misurate S₀, S₁ fissano la trasmissione dei neutroni a bassa energia</td><td><code>omp/sfunc.py</code></td></tr>
      <tr><td><a href="#direct">6</a></td><td>Cattura diretta in orbite legate, con una correzione dell'originale: nel TALYS standard restituisce zero a meno che non si richiedano anche tutte le uscite del modello ottico</td><td><code>direct/racapcalc.py</code></td></tr>
      <tr><td><a href="#direct">6</a></td><td>Lo schema di accoppiamento del bersaglio (rotore, vibratore, sferico) scelto in base ai suoi livelli misurati</td><td><code>structure/collrule.py</code></td></tr>
      <tr><td><a href="#structure">1</a></td><td>Il continuo comincia dove lo schema dei livelli misurato smette di essere completo</td><td><code>structure/levcomplete.py</code></td></tr>
      <tr><td><a href="#structure">1</a></td><td>Un livello il cui spin elencato è impossibile per il suo nucleo (intero con A dispari) viene trattato come un livello di spin sconosciuto</td><td><code>structure/levjpar.py</code></td></tr>
      <tr><td><a href="#compound">8</a></td><td>Densità dei livelli a temperatura costante ancorata alla parte completa dei livelli discreti</td><td><code>density/ctwindow2.py</code></td></tr>
      <tr><td><a href="#fission">12</a></td><td>Bande rotazionali degli stati di transizione nei punti di sella della fissione</td><td><code>fission/barriers.py</code></td></tr>
      <tr><td><a href="#resonance">15</a></td><td>Cattura dove solo poche risonanze cadono nella finestra stellare: il valore tipico di una scala di risonanze invece della media</td><td><code>fewres.py</code></td></tr>
      <tr><td></td><td>Quattro salvaguardie lontano dalla stabilità: flusso diretto limitato dall'unitarietà, un limite all'energia di Fermi, nessuna collettività predefinita per i nuclei dispari-dispari, distribuzione dello spin del pre-equilibrio normalizzata</td><td><code>engphys.py</code></td></tr>
    </tbody>
  `,
  coda_h3_outside: "Fuori dal motore",
  coda_p_outside: "Alcune parti della storia girano accanto al motore e non al suo interno. Le scale statistiche di risonanze del <a href=\"#resonance\">capitolo 15</a> vivono in <code>physics/resonance/</code>. Le medie maxwelliane (MACS) del <a href=\"#measure\">capitolo 17</a> si ottengono dopo l'esecuzione a partire dalle curve di cattura del motore, in <code>validation/differential/core.py</code>; la cattura su bersagli eccitati termicamente e il tasso stellare, invece, li calcola il motore stesso (<code>astro/stellar.py</code>, opzionale). Lo strato di ancoraggio del <a href=\"#layers\">capitolo 21</a> vive in <code>incognita/terra/</code>.",
  close: "Chiudi",
  chapters: "Capitoli",
  nav_board: "Classifica", nav_data_short: "Dati",
  coda_repo: "Il codice, la libreria e le misure revisionate sono aperti: <a href=\"https://github.com/seth-michael-weaver/incognita\">seth-michael-weaver/incognita su GitHub</a>. Puoi consultare tu stesso qualsiasi previsione nella pagina <a href=\"data.html?lang=it\" data-keep-lang>Tutti i nuclidi</a>, oppure clonare il repository ed eseguirlo.",
  diagram: "Diagramma",
});

Object.assign(WT.L.ui, { pause_sweep: "Metti in pausa la scansione", play_sweep: "Riprendi la scansione" });

/* course mode: audience note, chapter level tags, per-step links */
Object.assign(WT.L.ui, {
  audience: '<b>A chi si rivolge:</b> a chiunque sia curioso. I primi capitoli non richiedono conoscenze di fisica; gli ultimi arrivano al livello della ricerca. Ogni capitolo porta un\'etichetta: <span class="lvl l0">Introduzione</span>, <span class="lvl l1">Intermedio</span>, <span class="lvl l2">Avanzato</span> o <span class="lvl l3">Esperto</span>. Vuoi usarlo a lezione? Consulta la <a href="instructors.html" data-keep-lang>guida per i docenti</a>.',
  lvl0: "Introduzione", lvl1: "Intermedio", lvl2: "Avanzato", lvl3: "Esperto", lvl_title: "Livello",
  xp_kicker: "Parte seconda · Esperto",
  xp_h: "Nel dettaglio",
  xp_p: "Finora i capitoli hanno raccontato ogni passo con un'immagine. I sei che seguono aprono gli stessi passi: le formule che il motore calcola, le approssimazioni che contengono e i punti in cui vanno in difficoltà. Sono scritti per valutatori di dati nucleari, sviluppatori di modelli e studenti di dottorato. I disegni calcolano le formule in tempo reale, con dati d'ingresso illustrativi.",
  step_link: "Copia un link a questo passo", link_copied: "Link copiato",
});
