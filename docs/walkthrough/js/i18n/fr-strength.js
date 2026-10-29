/* French: strength (Chapitre 25, expert: photon strength, transmission, <Gamma_gamma> and the cascade) */
WT.L.ch.strength = {
  num: "Chapitre 25", title: "La force gamma en détail", short: "Force gamma",
  lead: "Le chapitre 10 montrait quels photons un noyau chaud préfère. Ce chapitre écrit les fonctions de force, les suit jusqu'aux coefficients de transmission et à la largeur radiative moyenne, et fait tourner la cascade qu'elles gouvernent.",
  html: `
<div class="step">
  <h3>E1 : la queue de la résonance dipolaire géante</h3>
  <p>La <b>fonction de force gamma</b> <i>f<sub>XL</sub></i>(<i>E</i><sub>γ</sub>) est la probabilité réduite moyenne d'émission d'un photon de type <i>XL</i> : dipolaire électrique E1, dipolaire magnétique M1, etc. Pour E1, elle est dominée par la résonance dipolaire géante vers 18 MeV, mais la désexcitation depuis <i>S<sub>n</sub></i> utilise des photons de 1 à 7 MeV, loin dans sa queue, et toute la question est la forme de cette queue.</p>
  <div class="formula">f<sub>E1</sub> = K σ₀Γ₀ · E<sub>γ</sub> Γ(E<sub>γ</sub>,T) / [(E<sub>γ</sub>² − E₀²)² + E<sub>γ</sub>² Γ(E<sub>γ</sub>,T)²] / (1 − e<sup>−E<sub>γ</sub>/T</sup>) ,  Γ(E<sub>γ</sub>,T) = (Γ₀/E₀)(E<sub>γ</sub> + 4π²T²/E₀)</div>
  <div class="ctl"><label for="ps-t">Température des états finals T (MeV)</label><input id="ps-t" type="range" data-bind="T" min="0" max="1.5" step="0.01" value="0.7"><output data-show="T" data-fmt="2"></output></div>
  <p>La courbe en tirets est la lorentzienne standard (SLO), la forme ajustée sur la photoabsorption. Avec sa largeur constante, elle surestime la force dans la fenêtre de désexcitation d'un facteur 2 à 5, un défaut connu de longue date pour les noyaux sphériques. La courbe pleine est la lorentzienne modifiée simplifiée (<b>SMLO</b>) : sa largeur croît avec l'énergie du photon et avec la température des états finals, ce qui abaisse la queue dans la fenêtre tout en laissant une force finie à énergie de photon nulle, comme l'exigent les données de désexcitation. L'encadré agrandi montre ce plancher, sous 2 MeV : ramenez <i>T</i> à 0 et il disparaît.</p>
</div>
<div class="step">
  <h3>M1 : spin-flip, ciseaux, upbend</h3>
  <p>La force M1 est plus faible, mais pas négligeable : une résonance de spin-flip vers 41<i>A</i><sup>−1/3</sup> MeV, un mode ciseaux vers 3 MeV dans les noyaux déformés (dont la force croît comme β²), et un upbend, une remontée vers l'énergie de photon nulle observée dans les données de la méthode d'Oslo et dans les calculs de modèle en couches.</p>
  <div class="ctl"><label for="ps-b">Déformation β (ciseaux)</label><input id="ps-b" type="range" data-bind="beta" min="0" max="0.35" step="0.01" value="0.2"><output data-show="beta" data-fmt="2"></output></div>
  <div class="btns"><button class="btn ghost" data-act="up" aria-pressed="true">Upbend</button></div>
  <p>La courbe pâle à l'arrière-plan est E1. Aux plus basses énergies de photon, sous environ 2 MeV ici, l'upbend permet à M1 de l'égaler ou de la dépasser (le repère indique où), d'où son importance pour l'extrémité molle de la cascade et pour la capture loin de la stabilité. La M1 par défaut du moteur est la recommandation de l'AIEA avec upbend, tabulée noyau par noyau, et son E1 par défaut est la SMLO-2019 tabulée ; les formes analytiques utilisées ici remplacent ces tables.</p>
</div>
<div class="step">
  <h3>Brink–Axel</h3>
  <p>L'<b>hypothèse de Brink–Axel</b> veut que la force dépende de l'énergie du photon et non de l'état de départ du noyau : la même <i>f</i> vaut pour une résonance en <i>S<sub>n</sub></i> et pour un état à 4 MeV. (La SMLO garde une faible dépendance à travers <i>T</i>.) Chaque énergie de départ émet alors selon le coefficient de transmission multiplié par la densité d'états finals.</p>
  <div class="formula">T<sub>XL</sub>(E<sub>γ</sub>) = 2π E<sub>γ</sub><sup>2L+1</sup> f<sub>XL</sub>(E<sub>γ</sub>) ,  dΓ/dE<sub>γ</sub> ∝ T<sub>XL</sub>(E<sub>γ</sub>) ρ(E<sub>x</sub> − E<sub>γ</sub>)</div>
  <div class="ctl"><label for="ps-x">Énergie de départ Eₓ (MeV)</label><input id="ps-x" type="range" data-bind="Ex" min="2" max="7.6" step="0.05" value="7.6"><output data-show="Ex" data-fmt="2"></output></div>
  <p>Le produit d'un <i>E</i><sub>γ</sub>³<i>f</i> croissant et d'un ρ décroissant forme une bosse. Depuis <i>S<sub>n</sub></i>, elle culmine ici vers 4 à 5 MeV. Pour des départs plus bas, elle est coupée à l'énergie de départ ; sous l'énergie de raccordement, là où ρ est une exponentielle à température constante, la forme est la même quel que soit le départ, simplement tronquée. On teste l'hypothèse en comparant des forces extraites à différentes énergies d'excitation, ce que font les analyses de type Oslo.</p>
</div>
<div class="step">
  <h3>La largeur radiative moyenne</h3>
  <p>La somme sur tous les états finals accessibles par E1 ou M1 depuis les résonances en onde s (<i>J</i><sup>π</sup> = ½⁺ sur une cible de spin 0) donne leur largeur photonique totale moyenne. Elle est mesurée, à partir de la forme des résonances, pour quelques centaines de noyaux, et c'est le principal contrôle de la force en <i>S<sub>n</sub></i>.</p>
  <div class="formula">⟨Γ<sub>γ</sub>⟩ = D₀/2π · Σ<sub>XL</sub> Σ<sub>J′π′</sub> ∫₀^{S<sub>n</sub>} T<sub>XL</sub>(E<sub>γ</sub>) ρ(S<sub>n</sub> − E<sub>γ</sub>, J′, π′) dE<sub>γ</sub></div>
  <div class="ctl"><label for="ps-s">Facteur sur la force</label><input id="ps-s" type="range" data-bind="scale" min="0.3" max="8" step="0.01" value="1"><output data-show="scale" data-fmt="2"></output></div>
  <p>Les courbes montrent d'où vient la largeur, photon par photon : surtout de 3 à 7 MeV, et surtout E1, M1 ajoutant environ 15 %. Ici, avec des formes analytiques et une densité de niveaux schématique à la place des tables du moteur, la largeur vaut environ un sixième des 0,92 eV mesurés : c'est dire sa sensibilité à la densité de niveaux sous <i>S<sub>n</sub></i> et à la queue de la force. Les valeurs par défaut de TALYS, que suit le moteur, donnent environ 1,3 eV pour ce noyau. Le curseur applique le facteur global unique qu'ajusterait une évaluation : environ ×6 le ramène dans la bande mesurée. Dans le domaine du keV, la capture est presque proportionnelle à ⟨Γ<sub>γ</sub>⟩ lorsque Γ<sub>γ</sub> ≪ Γ<sub>n</sub> : un facteur ici est donc un facteur sur (n,γ). TALYS peut renormaliser la force sur un ⟨Γ<sub>γ</sub>⟩ mesuré (<code>gnorm</code>) ; dans INCOGNITA, cette renormalisation, appliquée à tous les noyaux de la cascade, est une option, désactivée par défaut.</p>
</div>
<div class="step">
  <h3>La cascade</h3>
  <p>Sous le premier photon, la même règle se répète : depuis chaque nouvelle énergie, le photon suivant est tiré selon <i>T</i>(<i>E</i><sub>γ</sub>) ρ(<i>E<sub>x</sub></i> − <i>E</i><sub>γ</sub>), jusqu'à ce que le noyau atteigne ses niveaux connus. Chaque histoire compte quelques photons ; leur spectre sommé est ce que voit un calorimètre après une capture.</p>
  <div class="btns"><button class="btn ghost" data-act="up2" aria-pressed="true">Upbend</button><button class="btn ghost" data-act="clear">Recommencer</button></div>
  <p>L'upbend ajoute des photons mous et augmente un peu la multiplicité. Le moteur ne tire pas d'histoires : il déplace des populations d'intervalle en intervalle, de haut en bas (chapitre 11), ce qui donne les mêmes moyennes sans bruit d'échantillonnage.</p>
  <div class="aside">Dans le code : <code>gamma/strength.py</code> (tous les modèles de force pris en charge par TALYS ; par défaut, les tables SMLO-2019 et la M1 de l'AIEA avec upbend), <code>gamma/parameters.py</code> (systématiques des résonances géantes, tables), <code>gamma/transmission.py</code> (T = 2π E<sup>2L+1</sup> f), <code>gamma/ggnorm.py</code> (normalisation facultative de ⟨Γγ⟩), <code>emission/</code> (la cascade). L'image utilise des formes analytiques et des systématiques pour un noyau de type fer 57 ; le ⟨Γγ⟩ mesuré est la valeur RIPL pour ⁵⁷Fe.</div>
</div>`,
};
Object.assign(WT.L.labels, {
  // axes
  "Eγ (MeV)": "Eγ (MeV)", "Sₙ": "Sₙ", "{#} eV": "{#} eV",
  // scene 1: E1
  "E{#} strength f (MeV⁻³), A = {#}": "force E{#} f (MeV⁻³), A = {#}",
  "photons that decay uses": "photons utilisés par la désexcitation",
  "GDR: E₀ = {#} MeV, Γ₀ = {#} MeV, σ₀ = {#} mb": "RDG : E₀ = {#} MeV, Γ₀ = {#} MeV, σ₀ = {#} mb",
  "dashed: SLO": "tirets : SLO",
  "at {#} MeV: SMLO / SLO = {#}": "à {#} MeV : SMLO / SLO = {#}",
  "protons against neutrons": "protons contre neutrons",
  // scene 2: M1
  "M{#} strength f (MeV⁻³), A = {#}": "force M{#} f (MeV⁻³), A = {#}",
  "spin-flip": "spin-flip",
  "scissors, β = {#}": "ciseaux, β = {#}",
  "upbend": "upbend",
  "faint: E{#} at T = {#} MeV": "pâle : E{#} à T = {#} MeV",
  "M{#} > E{#} below {#} MeV": "M{#} > E{#} sous {#} MeV",
  "E{#} dominates at every energy here": "ici, E{#} domine à toutes les énergies",
  "scissors: the two deformed clouds rock": "ciseaux : les deux nuages déformés basculent",
  // scene 3: Brink-Axel
  "from {#} MeV": "depuis {#} MeV",
  "peak at Eγ ≈ {#} MeV": "pic à Eγ ≈ {#} MeV",
  "primary spectrum T(Eγ) ρ(Eₓ − Eγ), each scaled to its peak": "spectre primaire T(Eγ) ρ(Eₓ − Eγ), chacun normalisé à son pic",
  // scene 4: <Gamma_gamma>
  "contribution to ⟨Γγ⟩ per MeV of photon energy: E{#} (yellow), M{#} (purple, on top)": "contribution à ⟨Γγ⟩ par MeV d'énergie de photon : E{#} (jaune), M{#} (violet, au-dessus)",
  "measured {#} eV": "mesuré {#} eV",
  "computed ⟨Γγ⟩ = {#} meV (E{#} {#} %, M{#} {#} %)": "⟨Γγ⟩ calculé = {#} meV (E{#} {#} %, M{#} {#} %)",
  // scene 5: cascade
  "all photons from all cascades": "tous les photons de toutes les cascades",
  "{#} cascades · mean multiplicity {#}": "{#} cascades · multiplicité moyenne {#}",
});
Object.assign(WT.L.glossary, {
  smlo: {
    term: "SMLO", aliases: ["SMLO"],
    short: "La lorentzienne modifiée simplifiée : une fonction de force E1 dont la largeur croît avec l'énergie du photon et avec la température des états finals.",
    more: "Proposée par V. Plujko et ses collaborateurs, et tabulée pour chaque noyau dans la base de données de fonctions de force photonique de l'AIEA (2019). L'E1 par défaut du moteur, comme celle de TALYS-2, est cette table SMLO-2019.",
    chapter: "strength",
  },
  brinkAxel: {
    term: "Hypothèse de Brink–Axel", aliases: ["hypothèse de Brink–Axel", "Brink–Axel"],
    short: "L'hypothèse selon laquelle la fonction de force gamma ne dépend que de l'énergie du photon, et non de l'énergie d'excitation de l'état qui l'émet.",
    more: "Elle permet qu'une seule force, mesurée ou calculée pour l'état fondamental, serve à toute la cascade. On la teste en extrayant des forces à différentes énergies d'excitation ; elle est approximativement vérifiée, des écarts étant débattus pour certains noyaux et certaines énergies.",
    chapter: "strength",
  },
});
/* attributes referenced in the English chapter script (for the structure check): data-act="up" data-act="up2" */
