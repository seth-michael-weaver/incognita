/* Italian: resonance (Capitolo 10, risonanze) */
WT.L.ch.resonance = {
  num: "Capitolo 10", title: "Picchi stretti", short: "Risonanze",
  lead: "A energia abbastanza bassa un neutrone non vede più un nucleo liscio e mediato. Vede i singoli livelli di energia del nucleo composto, uno alla volta.",
  html: `
<div class="step">
  <p>Ogni picco è una <b>risonanza</b>: un livello di energia del nucleo composto in cui può cadere un neutrone che abbia esattamente quell'energia. La sua altezza è la sezione d'urto di <b>cattura</b> in quel punto (il neutrone viene assorbito, escono fotoni), in scala logaritmica; la sua larghezza è la larghezza di risonanza Γ, disegnata circa cento volte più grande del vero.</p>
  <div class="ctl"><label for="res-e">Energia del neutrone (eV)</label><input id="res-e" type="range" data-bind="En" min="0.5" max="300" step="0.1" value="30"><output data-show="En" data-fmt="1"></output></div>
  <p>Il neutrone avanza a salti in energia; dove arriva può essere catturato, in un lampo di fotoni. Su un picco la sezione d'urto è di migliaia di barn e la cattura è quasi certa; fra i picchi è di pochi barn. Trascina l'energia per fermarlo su un picco, poi fra due.</p>
</div>
<div class="step">
  <h3>I picchi mantengono le distanze</h3>
  <p>La riga centrale mostra come si dispongono i livelli reali: due livelli con lo stesso spin e la stessa parità si respingono, quindi le quasi coincidenze sono rare. La <b>teoria delle matrici aleatorie</b> descrive questo schema. Posizioni davvero casuali (riga in alto) si raggruppano e lasciano vuoti.</p>
  <div class="btns"><button class="btn" data-act="again">Estrai di nuovo</button></div>
  <p>Estrai di nuovo per un nuovo campione. ⟨r̃⟩ confronta ogni spaziatura con la successiva: circa 0,39 per posizioni casuali, 0,53 per livelli che si respingono; il codice usa lo schema con repulsione. Mescolare due sequenze, per esempio due spin (riga in basso), nasconde in parte la repulsione.</p>
</div>
<div class="step">
  <h3>Le altezze si disperdono moltissimo</h3>
  <p>Ora l'altezza di ogni picco è la sua <b>larghezza neutronica</b> Γ<sub>n</sub> in scala lineare: quanto fortemente il livello si accoppia a un neutrone. Il cappuccio giallo è la sua larghezza γ Γ<sub>γ</sub>, la rapidità con cui emette fotoni; somma centinaia di percorsi di fotoni, quindi è quasi uguale per ogni livello.</p>
  <div class="btns"><button class="btn" data-act="roll">Estrai una larghezza</button><button class="btn ghost" data-act="equal">Larghezze uguali</button><button class="btn ghost" data-act="pt">Porter–Thomas</button></div>
  <p>Un livello ha un solo modo di spezzarsi in neutrone più bersaglio, quindi la sua larghezza si comporta come il quadrato di un unico numero a campana. Estraine uno: la pallina cade in <i>x</i>, <i>x</i>² diventa l'altezza del picco successivo e un punto cade nel mucchio. Il mucchio si addensa vicino a zero con una coda lunga, la legge di <b>Porter–Thomas</b>: la maggior parte dei livelli è debole, pochi sono enormi. Larghezze uguali mostra invece una fila di picchi medi.</p>
</div>
<div class="step">
  <h3>Una scala da quattro numeri</h3>
  <p>I picchi ora nascono da quattro medie che puoi impostare. Per un nucleo non misurato si possono prevedere solo queste medie: la spaziatura media <i>D</i><sub>0</sub>; le <b>funzioni di forza</b> <i>S</i><sub>0</sub> e <i>S</i><sub>1</sub>, la larghezza neutronica media per unità di spaziatura per neutroni in onda s (frontali) e in onda p (decentrati); e la larghezza γ media. Da queste il codice costruisce una <b>scala</b>: un insieme casuale di livelli con quelle medie.</p>
  <div class="ctl"><label for="res-d0">Spaziatura D₀ (eV)</label><input id="res-d0" type="range" data-bind="D0" min="3" max="60" step="0.5" value="20"><output data-show="D0" data-fmt="1"></output></div>
  <div class="ctl"><label for="res-s0">Forza S₀ (×10⁻⁴)</label><input id="res-s0" type="range" data-bind="S0" min="0.2" max="3" step="0.05" value="1"><output data-show="S0" data-fmt="2"></output></div>
  <div class="ctl"><label for="res-gg">Larghezza γ ⟨Γγ⟩ (meV)</label><input id="res-gg" type="range" data-bind="Gg" min="10" max="80" step="1" value="23"><output data-show="Gg" data-fmt="0"></output></div>
  <p>Trascina <i>D</i><sub>0</sub> e i picchi si allargano o si affollano. I picchi pieni sono livelli in onda s (parità positiva), quelli col solo contorno in onda p (parità negativa). Le larghezze neutroniche crescono come √<i>E</i> per le onde s e come <i>E</i><sup>3/2</sup> per le onde p, quindi i picchi col contorno partono bassi e crescono verso destra.</p>
</div>
<div class="step">
  <h3>Giù fino all'energia termica</h3>
  <p>Gli stessi picchi su una scala di energia logaritmica, fino ai millesimi di eV. I neutroni di un reattore rallentano rimbalzando su nuclei leggeri, perdendo ogni volta più o meno la stessa frazione della loro energia, quindi qui ogni salto ha la stessa lunghezza. Alcuni vengono catturati dai picchi lungo la strada.</p>
  <div class="btns"><button class="btn" data-act="slow">Rallenta 10 neutroni</button></div>
  <p>Quelli che passano si assestano a temperatura ambiente, 0,025 eV, l'energia <b>termica</b>, molto sotto il primo picco. Lì la sezione d'urto, l'area del disco, è la somma delle code delle risonanze, compresi livelli legati appena sotto lo zero; le code crescono come 1/<i>v</i> (<i>v</i> è la velocità del neutrone), quindi il fondo sale verso sinistra. Ciò che viene catturato durante la discesa si misura con l'<b>integrale di risonanza</b>: la sezione d'urto sopra 0,5 eV, con ogni energia pesata per 1/<i>E</i>.</p>
</div>
<div class="step">
  <h3>Solo la statistica è prevedibile</h3>
  <p>Ogni riga è una scala estratta dagli stessi quattro numeri, con un disco la cui area è la sua sezione d'urto di cattura termica. La parentesi arriva fino al picco che fissa quel valore, di solito il più vicino; la sua distanza cambia da una scala all'altra, e il disco varia di un fattore dieci o più.</p>
  <div class="btns"><button class="btn" data-act="draw1">Estrai una scala</button><button class="btn ghost" data-act="more">Estrai 20</button></div>
  <p>Ogni valore cade nel mucchio a destra. Per un nucleo non misurato la risposta è una dispersione di valori, non un singolo numero, e nessun modello migliore può restringerla. L'integrale di risonanza, una somma su molti picchi, si disperde meno. Dove i livelli distano più di circa 10 keV, come nei nuclei leggeri, nessuno è vicino all'energia termica: lì la cattura è diretta, e il codice si rifiuta di rispondere.</p>
  <div class="aside">Nel codice: <code>physics/resonance/ladder.py</code> (spaziature da matrici aleatorie, larghezze di Porter–Thomas, sezioni d'urto di Breit–Wigner, cattura termica e integrale di risonanza su un insieme di scale), <code>ladder_statistics.py</code> (le stesse leggi messe alla prova su scale misurate), <code>ensemble_runner.py</code>. Funzionano accanto al motore di reazioni, non al suo interno.</div>
</div>`,
};
Object.assign(WT.L.labels, {
  // forest
  "{#} eV": "{#} eV", "+{#} eV": "+{#} eV",
  "height: peak capture (log) · width Γ ×{#}": "altezza: cattura al picco (log) · larghezza Γ ×{#}",
  "peak height: capture cross section (log scale) · width: resonance width Γ, drawn {#}× wide": "altezza: sezione d'urto di cattura (scala log) · larghezza Γ, disegnata {#}× più larga",
  "D₀ {#} eV · S₀ {#}×{#}⁻⁴ · S₁ {#}×{#}⁻⁴ · ⟨Γγ⟩ {#} meV": "D₀ {#} eV · S₀ {#}×{#}⁻⁴ · S₁ {#}×{#}⁻⁴ · ⟨Γγ⟩ {#} meV",
  "s-wave (+ parity)": "onda s (parità +)", "p-wave (− parity)": "onda p (parità −)",
  "caught {#} times in {#} landings": "catturato {#} volte su {#} arrivi",
  "each peak: one level of the compound nucleus": "ogni picco: un livello del nucleo composto",
  "each peak: one level of the compound nucleus · about {#} eV apart": "ogni picco: un livello del nucleo composto · distanti circa {#} eV",
  // spacing
  "random positions (Poisson)": "posizioni casuali (Poisson)",
  "repelling levels (random-matrix)": "livelli che si respingono (matrici aleatorie)",
  "two repelling sequences mixed": "due sequenze con repulsione, mescolate",
  "clumps and gaps · ⟨r̃⟩ ≈ {#}": "gruppi e vuoti · ⟨r̃⟩ ≈ {#}",
  "evenly kept apart · ⟨r̃⟩ ≈ {#}": "distanziati con regolarità · ⟨r̃⟩ ≈ {#}",
  "repulsion half hidden · ⟨r̃⟩ ≈ {#}": "repulsione in parte nascosta · ⟨r̃⟩ ≈ {#}",
  "clumps and gaps · spacing ratio ⟨r̃⟩ ≈ {#}": "gruppi e vuoti · rapporto di spaziature ⟨r̃⟩ ≈ {#}",
  "evenly kept apart · spacing ratio ⟨r̃⟩ ≈ {#}": "distanziati con regolarità · rapporto di spaziature ⟨r̃⟩ ≈ {#}",
  "repulsion half hidden · spacing ratio ⟨r̃⟩ ≈ {#}": "repulsione in parte nascosta · rapporto di spaziature ⟨r̃⟩ ≈ {#}",
  "⟨r̃⟩: {#} if random, {#} for random-matrix": "⟨r̃⟩: {#} se casuale, {#} con matrici aleatorie",
  "same average spacing in every row · ⟨r̃⟩: {#} if random, {#} for random-matrix": "stessa spaziatura media in ogni riga · ⟨r̃⟩: {#} se casuale, {#} con matrici aleatorie",
  // Porter-Thomas
  "height: neutron width Γn (linear)": "altezza: larghezza neutronica Γn (lineare)",
  "peak height: neutron width Γn, linear scale": "altezza: larghezza neutronica Γn, scala lineare",
  "yellow: γ width": "giallo: larghezza γ",
  "yellow cap: γ width, nearly the same on every peak": "cappuccio giallo: larghezza γ, quasi uguale ovunque",
  "equal widths: every peak the average": "larghezze uguali: ogni picco nella media",
  "rolled widths": "larghezze estratte", "pile of rolled widths": "mucchio di larghezze estratte",
  "× average": "× media", "(in units of the average)": "(in unità della media)",
  "dashed: Porter–Thomas": "tratteggio: Porter–Thomas", "dashed: the Porter–Thomas law": "tratteggio: la legge di Porter–Thomas",
  "bell-curve number x": "numero a campana x",
  "x = {#}  →  x² = {#}": "x = {#}  →  x² = {#}",
  "press Roll a width": "premi Estrai una larghezza",
  // thermal
  "bound level {#} eV": "livello legato {#} eV",
  "a bound level at {#} eV: its tail lifts this end": "un livello legato a {#} eV: la sua coda solleva questo estremo",
  "resonance integral ≈ {#} b": "integrale di risonanza ≈ {#} b",
  "resonance integral above {#} eV ≈ {#} b": "integrale di risonanza sopra {#} eV ≈ {#} b",
  "{#}/v": "{#}/v",
  "caught by a peak on the way down: {#} · reached thermal: {#}": "catturati da un picco scendendo: {#} · arrivati a energia termica: {#}",
  "each hop: one bounce, the same fraction of energy lost": "ogni salto: un rimbalzo, persa la stessa frazione di energia",
  // ensemble
  "thermal neutron": "neutrone termico",
  "σ disc": "disco σ", "disc area = σ at {#} eV": "area del disco = σ a {#} eV",
  "{#}k": "{#}k",
  "thermal σ (b)": "σ termica (b)", "thermal σ, barns": "σ termica, barn",
  "{#} ladders · thermal ×{#} · res. integral ×{#}": "{#} scale · termica ×{#} · int. di ris. ×{#}",
});
// labels that carry a cross section printed as "12 b" or "3.4k b"
(function () {
  const L = WT.L.labels;
  for (const b of ["{#} b", "{#}k b"]) {
    L[b] = b;
    L[`σ ≈ ${b} · caught on {#} % of landings`] = `σ ≈ ${b} · catturato nel {#} % degli arrivi`;
    L[`σ ≈ ${b} · caught on <{#} % of landings`] = `σ ≈ ${b} · catturato in <{#} % degli arrivi`;
    L[`thermal, {#} eV: σ ≈ ${b}`] = `termico, {#} eV: σ ≈ ${b}`;
    L[`{#} ladders · thermal σ median ${b}, middle two thirds ×{#} · resonance integral only ×{#}`] =
      `{#} scale · σ termica mediana ${b}, due terzi centrali ×{#} · integrale di risonanza solo ×{#}`;
  }
})();
