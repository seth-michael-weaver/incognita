/* French: fusion (chapter 29) */
WT.L.ch.fusion = {
  num: "Chapitre 29", title: "L'énergie de fusion et la barrière coulombienne", short: "Fusion",
  lead: "La fusion va dans le sens inverse de la fission : deux noyaux légers s'unissent, et la paire pèse moins que ses parties.",
  html: `
<div class="step">
  <h3>L'énergie de fusion d'après la courbe de liaison</h3>
  <p>Unissez deux noyaux légers : si le nouveau se trouve plus haut sur la courbe de liaison, de l'énergie est libérée. Au-delà du pic du fer, l'union coûte de l'énergie.</p>
  <div class="ctl"><label for="fu-a">A de chaque noyau léger</label><input id="fu-a" type="range" data-bind="fuse" data-instant min="2" max="60" step="1" value="2"><output data-show="fuse" data-fmt="0"></output></div>
  <p class="ctl-result" id="fu-fuse-out" aria-live="polite"></p>
</div>
<div class="step">
  <h3>Barrière coulombienne et effet tunnel</h3>
  <p>Tirez le deutéron en arrière et lâchez-le. Les deux noyaux sont chargés : la plupart des tirs rebondissent sur la colline ; quelques-uns la traversent par effet tunnel.</p>
  <div class="ctl"><label for="fu-e">Poussée (keV)</label><input id="fu-e" type="range" data-bind="lE" min="0.5" max="2.6" step="0.01" value="1.7"><output data-show="E" data-fmt="0"></output></div>
  <div class="btns"><button class="btn" data-act="fire">Tirer</button></div>
</div>
<div class="step">
  <h3>Produits de réaction et valeur Q</h3>
  <p>La paire unie est plus légère que ses deux parties. La masse manquante s'envole sous forme de particules rapides.</p>
  <div class="btns fu-fuels"><button class="btn ghost" data-act="DT" aria-pressed="true">D–T</button> <button class="btn ghost" data-act="DD" aria-pressed="false">D–D</button> <button class="btn ghost" data-act="DHe" aria-pressed="false">D–³He</button> <button class="btn ghost" data-act="pB" aria-pressed="false">p–¹¹B</button></div>
</div>
<div class="step">
  <h3>Taux de réaction thermonucléaire</h3>
  <p>Dans un gaz chaud, les noyaux les plus rapides passent. Chaque éclair est une fusion.</p>
  <div class="ctl"><label for="fu-t">Température (keV)</label><input id="fu-t" type="range" data-bind="lT" min="0" max="2" step="0.01" value="1"><output data-show="T" data-fmt="1"></output></div>
</div>`,
};
Object.assign(WT.L.labels, {
  "B": "B",
  "Copper{#}": "Cuivre{#}",
  "Coulomb hill": "colline coulombienne",
  "D–D": "D–D",
  "D–T": "D–T",
  "D–³He": "D–³He",
  "E = kT": "E = kT",
  "Gamow peak E₀": "pic de Gamow E₀",
  "K {#} · field lines lost to the wall: {#}": "K {#} · lignes perdues vers la paroi : {#}",
  "Q = {#}": "Q = {#}",
  "Q = ∞: no heating needed": "Q = ∞ : aucun chauffage requis",
  "Silicon{#} (SiC)": "Silicium{#} (SiC)",
  "Steel (iron{#})": "Acier (fer{#})",
  "Sun's core": "cœur du Soleil",
  "TBR {#}": "TBR {#}",
  "Tungsten{#}": "Tungstène{#}",
  "Vanadium{#}": "Vanadium{#}",
  "after {#} years at {#} MW/m² · {#} MeV neutrons only · σ from INCOGNITA library v{#}": "après {#} ans à {#} MW/m² · neutrons de {#} MeV seuls · σ de la bibliothèque INCOGNITA v{#}",
  "almost never": "presque jamais",
  "alpha {#} MeV": "alpha {#} MeV",
  "axis, q = {#}": "axe, q = {#}",
  "binding per nucleon (MeV)": "liaison par nucléon (MeV)",
  "bubble-chamber view, magnetic field into the page: charged products curl, the neutron leaves no track": "vue en chambre à bulles, champ magnétique vers la page : les produits chargés s'enroulent, le neutron ne laisse pas de trace",
  "burning on its own": "brûle tout seul",
  "cooled down: plasma lost": "refroidi : plasma perdu",
  "cooling": "se refroidit",
  "could not load the library file": "impossible de charger la bibliothèque",
  "deuteron": "deutéron",
  "deuteron {#} keV": "deutéron {#} keV",
  "deuteron: pull back, let go": "deutéron : tirez, lâchez",
  "drag or tap a point; it runs on its own": "glissez ou touchez un point ; il évolue seul",
  "easiest: {a} keV, nτT {b}": "plus facile : {a} keV, nτT {b}",
  "edge: q = {#} · lines that cross it are lost": "bord : q = {#} · les lignes qui le franchissent sont perdues",
  "electron {#} keV": "électron {#} keV",
  "energy of the colliding pair (keV)": "énergie de la paire en collision (keV)",
  "few are this fast": "peu sont aussi rapides",
  "fusion rate: {a} the rate at {b} keV": "taux de fusion : {a} celui à {b} keV",
  "grain boundary": "joint de grain",
  "heating itself": "s'auto-chauffe",
  "helium stays and gathers into bubbles; hydrogen mostly diffuses out": "l'hélium reste et forme des bulles ; l'hydrogène s'échappe surtout par diffusion",
  "helium {#} appm": "hélium {#} appm",
  "hill to climb: charge product Z₁Z₂ = {#}": "colline à gravir : produit des charges Z₁Z₂ = {#}",
  "hold: heaters on (Q = fusion power / heating) · let go: heaters off, the plasma is on its own": "maintenir : chauffage actif (Q = puissance de fusion / chauffage) · lâcher : chauffage coupé, le plasma est seul",
  "hydrogen {#} appm": "hydrogène {#} appm",
  "ignition (Q = ∞)": "ignition (Q = ∞)",
  "kT (keV)": "kT (keV)",
  "kT {#} keV · E₀ {#} keV · width {#} keV": "kT {#} keV · E₀ {#} keV · largeur {#} keV",
  "kT {a} keV · D–T {b} m³/s · {c}× D–D": "kT {a} keV · D–T {b} m³/s · {c}× D–D",
  "keeps itself hot": "reste chaud tout seul",
  "laps {#}": "tours {#}",
  "lead–lithium": "plomb–lithium",
  "liquid lithium": "lithium liquide",
  "loading INCOGNITA's cross sections…": "chargement des sections efficaces d'INCOGNITA…",
  "missing {#} u  =  {#} MeV out": "manque {#} u  =  {#} MeV libérés",
  "n τE (s/m³)": "n τE (s/m³)",
  "negative: turns the other way": "négatif : tourne dans l'autre sens",
  "neutron escapes": "le neutron s'échappe",
  "peak near {#} keV": "pic vers {#} keV",
  "per fusion neutron · {#} neutrons · cross sections are simple fits": "par neutron de fusion · {#} neutrons · sections efficaces ajustées simplement",
  "plasma": "plasma",
  "product ×{a}": "produit ×{a}",
  "push {a} keV · chance to tunnel head-on {b}": "poussée {a} keV · probabilité de tunnel de face {b}",
  "q = {#}": "q = {#}",
  "q = {#}/{#}: closes after {#} lap": "q = {#}/{#} : se referme après {#} tour",
  "q = {#}/{#}: closes after {#} laps": "q = {#}/{#} : se referme après {#} tours",
  "q = {#}: no simple fraction, the dots fill the circle": "q = {#} : pas de fraction simple, les points remplissent le cercle",
  "screen radius is logarithmic: {#} fm to {#} fm": "rayon à l'écran logarithmique : de {#} fm à {#} fm",
  "shield": "protection",
  "tap to fire": "touchez pour tirer",
  "the cut, flat": "la coupe, à plat",
  "time slowed {a}×": "temps ralenti {a}×",
  "tries {#} · fused {#}": "essais {#} · fusions {#}",
  "tritium made, by depth": "tritium produit, selon la profondeur",
  "triton": "triton",
  "tunnels more easily": "passe plus facilement par effet tunnel",
  "turns at {#} fm": "fait demi-tour à {#} fm",
  "wall": "paroi",
  "{#} MeV": "{#} MeV",
  "{#} cm": "{#} cm",
  "{#} in {a}": "{#} sur {a}",
  "{#} keV": "{#} keV",
  "{#} keV = {#} million K": "{#} keV = {#} millions de K",
  "{a} %": "{a} %",
  "{a} + {a} → {b}: about {c} MeV released": "{a} + {a} → {b} : environ {c} MeV libérés",
  "{a} + {a} → {b}: costs {c} MeV": "{a} + {a} → {b} : coûte {c} MeV",
  "{a} keV · chance {b}": "{a} keV · probabilité {b}",
  "{a} keV · nτ {b} · {c}": "{a} keV · nτ {b} · {c}",
  "{a} · two branches, equally likely": "{a} · deux voies, également probables",
  "{a} · ρ up to {b} · {c} turns a second": "{a} · ρ jusqu'à {b} · {c} tours par seconde",
  "σ at {#} MeV:  (n,α) {#} mb · (n,p) {#} mb · (n,{#}n) {#} mb": "σ à {#} MeV :  (n,α) {#} mb · (n,p) {#} mb · (n,{#}n) {#} mb",
  "⁶Li {#} · ⁷Li {#} · (n,{#}n) {#}": "⁶Li {#} · ⁷Li {#} · (n,{#}n) {#}",
  "⁶Li {#} · ⁷Li {#} · (n,{#}n) {#} · captured {#} · leaked {#}": "⁶Li {#} · ⁷Li {#} · (n,{#}n) {#} · capturés {#} · fuites {#}",
  "⟨σv⟩ (m³/s)": "⟨σv⟩ (m³/s)",
});
