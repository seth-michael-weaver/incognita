/* Italian: fusion (Capitolo 29, energia di fusione e barriera coulombiana) */
WT.L.ch.fusion = {
  num: "Capitolo 29", title: "L'energia di fusione e la barriera coulombiana", short: "Fusione",
  lead: "La fusione va nel verso opposto alla fissione: due nuclei leggeri si uniscono, e la coppia pesa meno delle sue parti.",
  html: `
<div class="step">
  <h3>L'energia di fusione dalla curva di legame</h3>
  <p>Unisci due nuclei leggeri: se il nuovo nucleo sta più in alto sulla curva di legame, viene liberata energia. Oltre il picco del ferro, l'unione costa energia.</p>
  <div class="ctl"><label for="fu-a">Ogni nucleo leggero A</label><input id="fu-a" type="range" data-bind="fuse" data-instant min="2" max="60" step="1" value="2"><output data-show="fuse" data-fmt="0"></output></div>
  <p class="ctl-result" id="fu-fuse-out" aria-live="polite"></p>
</div>
<div class="step">
  <h3>Barriera coulombiana ed effetto tunnel</h3>
  <p>Tira indietro il deutone e lascialo andare. Entrambi i nuclei sono carichi, quindi la maggior parte dei colpi rimbalza sulla collina; pochi la attraversano per effetto tunnel.</p>
  <div class="ctl"><label for="fu-e">Spinta (keV)</label><input id="fu-e" type="range" data-bind="lE" min="0.5" max="2.6" step="0.01" value="1.7"><output data-show="E" data-fmt="0"></output></div>
  <div class="btns"><button class="btn" data-act="fire">Lancia</button></div>
</div>
<div class="step">
  <h3>Prodotti di reazione e valore Q</h3>
  <p>La coppia unita è più leggera delle due parti. La massa mancante vola via sotto forma di particelle veloci.</p>
  <div class="btns fu-fuels"><button class="btn ghost" data-act="DT" aria-pressed="true">D–T</button> <button class="btn ghost" data-act="DD" aria-pressed="false">D–D</button> <button class="btn ghost" data-act="DHe" aria-pressed="false">D–³He</button> <button class="btn ghost" data-act="pB" aria-pressed="false">p–¹¹B</button></div>
</div>
<div class="step">
  <h3>Velocità di reazione termonucleare</h3>
  <p>In un gas caldo passano i nuclei più veloci. Ogni lampo è una fusione.</p>
  <div class="ctl"><label for="fu-t">Temperatura (keV)</label><input id="fu-t" type="range" data-bind="lT" min="0" max="2" step="0.01" value="1"><output data-show="T" data-fmt="1"></output></div>
</div>`,
};

Object.assign(WT.L.labels, {
  "B": "B",
  "Copper{#}": "Rame{#}",
  "Coulomb hill": "collina coulombiana",
  "D–D": "D–D",
  "D–T": "D–T",
  "D–³He": "D–³He",
  "E = kT": "E = kT",
  "Gamow peak E₀": "picco di Gamow E₀",
  "K {#} · field lines lost to the wall: {#}": "K {#} · linee di campo perse sulla parete: {#}",
  "Q = {#}": "Q = {#}",
  "Q = ∞: no heating needed": "Q = ∞: nessun riscaldamento",
  "Silicon{#} (SiC)": "Silicio{#} (SiC)",
  "Steel (iron{#})": "Acciaio (ferro{#})",
  "Sun's core": "centro del Sole",
  "TBR {#}": "TBR {#}",
  "Tungsten{#}": "Tungsteno{#}",
  "Vanadium{#}": "Vanadio{#}",
  "after {#} years at {#} MW/m² · {#} MeV neutrons only · σ from INCOGNITA library v{#}": "dopo {#} anni a {#} MW/m² · solo neutroni da {#} MeV · σ dalla libreria INCOGNITA v{#}",
  "almost never": "quasi mai",
  "alpha {#} MeV": "alfa {#} MeV",
  "axis, q = {#}": "asse, q = {#}",
  "binding per nucleon (MeV)": "legame per nucleone (MeV)",
  "bubble-chamber view, magnetic field into the page: charged products curl, the neutron leaves no track": "camera a bolle, campo magnetico entrante nella pagina: i prodotti carichi curvano, il neutrone non lascia traccia",
  "burning on its own": "brucia da solo",
  "cooled down: plasma lost": "raffreddato: plasma perso",
  "cooling": "si raffredda",
  "could not load the library file": "impossibile caricare il file della libreria",
  "deuteron": "deutone",
  "deuteron {#} keV": "deutone {#} keV",
  "deuteron: pull back, let go": "deutone: tira indietro, lascia",
  "drag or tap a point; it runs on its own": "trascina o tocca un punto; poi va da solo",
  "easiest: {a} keV, nτT {b}": "più facile: {a} keV, nτT {b}",
  "edge: q = {#} · lines that cross it are lost": "bordo: q = {#} · le linee che lo passano si perdono",
  "electron {#} keV": "elettrone {#} keV",
  "energy of the colliding pair (keV)": "energia della coppia che si urta (keV)",
  "few are this fast": "pochi sono così veloci",
  "fusion rate: {a} the rate at {b} keV": "tasso di fusione: {a} quello a {b} keV",
  "grain boundary": "bordo di grano",
  "heating itself": "si autoriscalda",
  "helium stays and gathers into bubbles; hydrogen mostly diffuses out": "l'elio resta e forma bolle; l'idrogeno quasi tutto diffonde fuori",
  "helium {#} appm": "elio {#} appm",
  "hill to climb: charge product Z₁Z₂ = {#}": "collina da scalare: prodotto delle cariche Z₁Z₂ = {#}",
  "hold: heaters on (Q = fusion power / heating) · let go: heaters off, the plasma is on its own": "tieni premuto: riscaldamento acceso (Q = potenza di fusione / riscaldamento) · rilascia: spento, il plasma è da solo",
  "hydrogen {#} appm": "idrogeno {#} appm",
  "ignition (Q = ∞)": "ignizione (Q = ∞)",
  "kT (keV)": "kT (keV)",
  "kT {#} keV · E₀ {#} keV · width {#} keV": "kT {#} keV · E₀ {#} keV · larghezza {#} keV",
  "kT {a} keV · D–T {b} m³/s · {c}× D–D": "kT {a} keV · D–T {b} m³/s · {c}× D–D",
  "keeps itself hot": "resta caldo da solo",
  "laps {#}": "giri {#}",
  "lead–lithium": "piombo–litio",
  "liquid lithium": "litio liquido",
  "loading INCOGNITA's cross sections…": "carico le sezioni d'urto di INCOGNITA…",
  "missing {#} u  =  {#} MeV out": "mancano {#} u  =  {#} MeV liberati",
  "n τE (s/m³)": "n τE (s/m³)",
  "negative: turns the other way": "negativo: gira al contrario",
  "neutron escapes": "il neutrone sfugge",
  "peak near {#} keV": "picco vicino a {#} keV",
  "per fusion neutron · {#} neutrons · cross sections are simple fits": "per neutrone di fusione · {#} neutroni · sezioni d'urto da semplici fit",
  "plasma": "plasma",
  "product ×{a}": "prodotto ×{a}",
  "push {a} keV · chance to tunnel head-on {b}": "spinta {a} keV · probabilità di tunnel frontale {b}",
  "q = {#}": "q = {#}",
  "q = {#}/{#}: closes after {#} lap": "q = {#}/{#}: si chiude dopo {#} giro",
  "q = {#}/{#}: closes after {#} laps": "q = {#}/{#}: si chiude dopo {#} giri",
  "q = {#}: no simple fraction, the dots fill the circle": "q = {#}: nessuna frazione semplice, i punti riempiono il cerchio",
  "screen radius is logarithmic: {#} fm to {#} fm": "raggio sullo schermo logaritmico: da {#} fm a {#} fm",
  "shield": "schermo",
  "tap to fire": "tocca per lanciare",
  "the cut, flat": "la sezione, in piano",
  "time slowed {a}×": "tempo rallentato {a}×",
  "tries {#} · fused {#}": "tentativi {#} · fusioni {#}",
  "tritium made, by depth": "trizio prodotto, per profondità",
  "triton": "tritone",
  "tunnels more easily": "passa meglio per tunnel",
  "turns at {#} fm": "si inverte a {#} fm",
  "wall": "parete",
  "{#} MeV": "{#} MeV",
  "{#} cm": "{#} cm",
  "{#} in {a}": "{#} su {a}",
  "{#} keV": "{#} keV",
  "{#} keV = {#} million K": "{#} keV = {#} milioni di K",
  "{a} %": "{a} %",
  "{a} + {a} → {b}: about {c} MeV released": "{a} + {a} → {b}: liberati circa {c} MeV",
  "{a} + {a} → {b}: costs {c} MeV": "{a} + {a} → {b}: costa {c} MeV",
  "{a} keV · chance {b}": "{a} keV · probabilità {b}",
  "{a} keV · nτ {b} · {c}": "{a} keV · nτ {b} · {c}",
  "{a} · two branches, equally likely": "{a} · due rami, ugualmente probabili",
  "{a} · ρ up to {b} · {c} turns a second": "{a} · ρ fino a {b} · {c} giri al secondo",
  "σ at {#} MeV:  (n,α) {#} mb · (n,p) {#} mb · (n,{#}n) {#} mb": "σ a {#} MeV:  (n,α) {#} mb · (n,p) {#} mb · (n,{#}n) {#} mb",
  "⁶Li {#} · ⁷Li {#} · (n,{#}n) {#}": "⁶Li {#} · ⁷Li {#} · (n,{#}n) {#}",
  "⁶Li {#} · ⁷Li {#} · (n,{#}n) {#} · captured {#} · leaked {#}": "⁶Li {#} · ⁷Li {#} · (n,{#}n) {#} · catturati {#} · sfuggiti {#}",
  "⟨σv⟩ (m³/s)": "⟨σv⟩ (m³/s)",
});
