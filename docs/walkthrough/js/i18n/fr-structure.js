/* French: structure (Chapitre 1, de quoi est fait un noyau) */
WT.L.ch.structure = {
  num: "Chapitre 1", title: "De quoi est fait un noyau", short: "Structure",
  lead: "Avant que le moteur (notre logiciel de réactions) ne tire le moindre neutron, il lui faut une description du noyau cible : avec quelle force il tient ensemble, dans quels états d'énergie il peut se trouver et quelle forme il a.",
  html: `
<div class="step">
  <p>L'image montre un noyau de fer : une boule compacte de <em class="p">protons</em> et de <em class="n">neutrons</em> (les <b>nucléons</b>), liés par l'<b>interaction forte</b>, de très courte portée. Chaque nucléon ne sent que ses plus proches voisins, si bien que tous les noyaux ont à peu près la même densité.</p>
  <div class="ctl"><label for="st-n">Neutrons (le fer a 26 protons)</label><input id="st-n" type="range" data-bind="N" min="24" max="38" step="1" value="30" data-instant><output data-show="N" data-fmt="0"></output></div>
  <p>Faites glisser pour ajouter ou retirer des neutrons ; chaque choix est un <b>isotope</b> différent. Les barres montrent l'<b>énergie de liaison</b> par nucléon en MeV (millions d'électronvolts) : l'énergie nécessaire pour démonter le noyau. Elle est maximale près des isotopes stables.</p>
</div>
<div class="step">
  <h3>Le prix d'une particule arrachée</h3>
  <p>L'énergie qu'il faut pour arracher une particule est son <b>énergie de séparation</b> : <i>S<sub>n</sub></i> pour un neutron, <i>S<sub>p</sub></i> pour un proton, <i>S<sub>α</sub></i> pour une <b>particule alpha</b> (deux protons et deux neutrons liés ensemble). L'image représente le noyau comme un puits, l'énergie croissant vers le haut ; chaque extraction fait passer la particule du sommet au-delà de la ligne pointillée « libre », et le compteur enregistre le coût.</p>
  <div class="btns"><button class="btn ghost" data-act="pn">Arracher un neutron</button><button class="btn ghost" data-act="pp">Arracher un proton</button><button class="btn ghost" data-act="pa">Arracher une alpha</button></div>
  <p>Le moteur obtient chacune comme la différence entre deux masses nucléaires : mesurées quand c'est possible, tirées d'un modèle de masses sinon.</p>
  <div class="ctl"><label for="st-n2">Neutrons</label><input id="st-n2" type="range" data-bind="N" min="24" max="38" step="1" value="30" data-instant><output data-show="N" data-fmt="0"></output></div>
  <p>Changez le nombre de neutrons et arrachez de nouveau un neutron : <i>S<sub>n</sub></i> monte et descend en zigzag, car les nucléons s'apparient et, avec un nombre pair, le dernier est plus fortement lié. Une réaction ne peut éjecter une particule que si elle apporte assez d'énergie pour payer ce coût. Ces coûts sont les <b>seuils</b> de tout le calcul.</p>
</div>
<div class="step">
  <h3>Niveaux d'énergie, et la descente</h3>
  <p>Un noyau ne peut stocker que certaines quantités exactes d'énergie supplémentaire : les traits, ici pour le fer-56, avec l'<b>état fondamental</b> en bas. Chaque niveau a un <b>spin</b> <i>J</i> (moment angulaire) et une <b>parité</b>, + ou − (selon que son onde reste identique dans un miroir) ; 2<sup>+</sup> signifie spin 2, parité +.</p>
  <p>La boule orange est un noyau sur un niveau élevé. Il descend niveau par niveau, et chaque saut émet un <em class="g">photon</em> (un rayon gamma) qui emporte la différence d'énergie. L'épaisseur et le pourcentage des chemins donnent les probabilités mesurées de chaque saut, les <b>rapports d'embranchement</b>.</p>
  <div class="btns"><button class="btn" data-act="drop">Exciter le noyau</button></div>
  <p>Appuyez plusieurs fois : le même niveau rejoint l'état fondamental par des chemins différents. Le moteur garde une trentaine de niveaux mesurés par noyau, avec leurs probabilités ; plus haut, il traite les niveaux serrés comme un <b>continuum</b> lisse. Au-dessus de la ligne pointillée, <i>S<sub>n</sub></i>, le noyau peut émettre un neutron.</p>
</div>
<div class="step">
  <h3>Un niveau sans issue facile</h3>
  <p>Un niveau dont la seule issue exige un grand changement de spin, Δ<i>J</i>, se désexcite très lentement. À droite, 64 noyaux sont sur un tel niveau ; chacun attend un temps aléatoire, puis descend et un <em class="g">photon</em> s'échappe. Au bout d'une <b>demi-vie</b>, la moitié est descendue.</p>
  <div class="ctl"><label for="st-dj">Changement de spin ΔJ</label><input id="st-dj" type="range" data-bind="dJ" min="1" max="5" step="1" value="2" data-instant><output data-show="dJ" data-fmt="0"></output></div>
  <div class="ctl"><label for="st-eg">Énergie du photon (MeV)</label><input id="st-eg" type="range" data-bind="Eg" min="0.05" max="1.5" step="0.05" value="0.3"><output data-show="Eg" data-fmt="2"></output></div>
  <div class="btns"><button class="btn ghost" data-act="excite">Les exciter tous</button></div>
  <p>Augmentez Δ<i>J</i> et les photons sortent plus lentement : chaque unité de spin supplémentaire rend l'attente cent mille fois plus longue, voire davantage, et une énergie de photon plus faible l'allonge aussi (échelle logarithmique). Un niveau qui vit plus d'une seconde environ est un <b>isomère</b>, et le moteur le traite comme un point d'arrivée, au même titre que l'état fondamental.</p>
</div>
<div class="step">
  <h3>Rond, ou pas</h3>
  <p>Beaucoup de noyaux ne sont pas ronds. <i>β₂</i> (« bêta deux ») mesure l'étirement : 0 est une sphère, une valeur positive un noyau étiré comme un ballon de rugby, une valeur négative un noyau aplati en disque. L'échelle de droite montre les niveaux que produit chaque forme.</p>
  <p>Un noyau étiré peut tourner, ce qui donne les niveaux 0<sup>+</sup>, 2<sup>+</sup>, 4<sup>+</sup>, 6<sup>+</sup> avec des écarts qui croissent comme <i>J</i>(<i>J</i>+1) : un <b>rotor</b>. Un noyau rond peut onduler ; chaque quantum d'ondulation, un <b>phonon</b>, ajoute la même énergie, donc ses niveaux sont régulièrement espacés : un <b>vibrateur</b>.</p>
  <div class="ctl"><label for="st-beta">Déformation β₂</label><input id="st-beta" type="range" data-bind="beta" min="-0.3" max="0.45" step="0.01" value="0.28"><output data-show="beta" data-fmt="2"></output></div>
  <div class="btns"><button class="btn ghost" data-act="still">Immobile</button><button class="btn ghost" data-act="vib">En vibration</button><button class="btn ghost" data-act="rot">En rotation</button></div>
  <p>Faites varier <i>β₂</i> et appuyez sur les boutons : un étirement plus grand resserre les niveaux du rotor. Le moteur stocke les déformations de chaque noyau et une étiquette : sphérique, vibrateur ou rotor. Le chapitre 6 montre comment un neutron qui passe s'en sert.</p>
</div>
<div class="step">
  <h3>Des empreintes juste au-dessus du seuil</h3>
  <p>Un neutron lent qui rejoint la cible arrive juste au-dessus de <i>S<sub>n</sub></i>, dans la petite boîte de gauche. Le panneau de droite agrandit cette boîte des milliers de fois, l'énergie du neutron croissant de gauche à droite.</p>
  <div class="ctl"><label for="st-fe">Énergie du faisceau</label><input id="st-fe" type="range" data-bind="fe" min="0" max="1" step="0.001" value="0.3" data-instant><output id="st-fe-out"></output></div>
  <div class="btns"><button class="btn ghost" data-act="fplay" id="st-fplay">Mettre le balayage en pause</button></div>
  <p>À la plupart des énergies, le faisceau passe sans encombre. À certaines énergies précises, le neutron et le noyau ensemble coïncident avec un niveau caché, et une bonne partie du faisceau est absorbée : c'est une <b>résonance</b>. Sur un pic, le noyau dessiné gonfle : ce n'est pas un vrai changement de taille, mais la cible plus grande que le neutron « voit » effectivement quand son onde recouvre celle du noyau. Le noyau rend ensuite l'énergie sous forme de <em class="g">photon</em> ou de neutron. La courbe montre la fraction absorbée ; les barres marquent chaque résonance trouvée.</p>
  <div class="btns"><button class="btn ghost" data-act="fFe">Fer-56</button><button class="btn ghost" data-act="fAu">Or-197</button><button class="btn ghost" data-act="fU">Uranium-238</button></div>
  <p>Chaque noyau a son propre code-barres, à sa propre échelle : des milliers d'électronvolts entre les résonances du fer, quelques dizaines pour l'or et l'uranium. Trois moyennes le résument : <i>D₀</i>, l'écart moyen ; ⟨Γ<sub>γ</sub>⟩, la <b>largeur radiative</b>, presque la même pour tous les pics ; et <i>S₀</i>, la <b>fonction de force</b>, qui dit avec quelle facilité un neutron lent entre.</p>
  <p>Chacune sert à vérifier une étape ultérieure. Les paramètres de densité de niveaux du moteur ont été ajustés sur <i>D₀</i>, noyau par noyau ; ⟨Γ<sub>γ</sub>⟩ teste l'émission de photons, et <i>S₀</i> le modèle optique du chapitre suivant. Pour les noyaux non mesurés, le moteur utilise des tendances ajustées sur de nombreux noyaux.</p>
  <div class="aside">Dans le code : <code>structure/masses.py</code> (masses mesurées, masses de modèle au-delà, énergies de séparation), <code>structure/levels.py</code> (niveaux discrets, embranchements, isomères, spins estimés) et <code>levjpar.py</code> (facultatif, désactivé par défaut : réestime un spin de la liste qui est impossible pour ce noyau), <code>structure/deformation.py</code> (β₂ et l'étiquette sphérique/vibrateur/rotor) et <code>collrule.py</code> (facultatif, désactivé par défaut : choisit l'étiquette de la cible à partir de ses niveaux mesurés), <code>structure/resonances.py</code> (D₀, S₀, S₁, ⟨Γγ⟩).</div>
</div>`,
};
(function () {
  const L = {
    // scene: packed drop
    "{#}Fe": "{#}Fe",
    "{#} protons · {#} neutrons": "{#} protons · {#} neutrons",
    "binding energy per nucleon: about {#} MeV": "énergie de liaison par nucléon : environ {#} MeV",
    "binding per nucleon, one bar per isotope →": "liaison par nucléon, une barre par isotope →",
    // scene: well
    "free": "libre",
    "free: outside the nucleus": "libre : hors du noyau",
    "neutrons": "neutrons",
    "protons": "protons",
    "an alpha forms from the top pairs": "les paires du haut forment une alpha",
    "neutron {#}": "neutron {#}",
    "proton {#}": "proton {#}",
    "alpha {#}": "alpha {#}",
    "n {#}": "n {#}",
    "p {#}": "p {#}",
    "energy paid": "énergie payée",
    "energy to pull": "énergie pour arracher",
    "(MeV)": "(MeV)",
    "each one out (MeV)": "chacune (MeV)",
    "higher mark =": "repère plus haut =",
    "harder to remove": "plus difficile à arracher",
    "pulling out a neutron: {#} MeV paid": "arrachage d'un neutron : {#} MeV payés",
    "pulling out a proton: {#} MeV paid": "arrachage d'un proton : {#} MeV payés",
    "pulling out an alpha: {#} MeV paid": "arrachage d'une alpha : {#} MeV payés",
    // scene: levels and gamma drops
    "continuum: too many levels to list": "continuum : trop de niveaux pour les lister",
    "neutron threshold Sₙ ≈ {#} MeV": "seuil neutron Sₙ ≈ {#} MeV",
    "ground state": "état fondamental",
    "MeV": "MeV",
    "each line: an energy, a spin J and a parity (±)": "chaque trait : une énergie, un spin J et une parité (±)",
    "path width and % = measured odds of each hop": "épaisseur du chemin et % = probabilité mesurée de chaque saut",
    // scene: isomer
    "ground": "fondamental",
    "J = {#}/{#}": "J = {#}/{#}",
    "ΔJ = {#}": "ΔJ = {#}",
    "still excited: {#} of {#}": "encore excités : {#} sur {#}",
    "longer than a second: an isomer, a stop in its own right": "plus d'une seconde : un isomère, un point d'arrivée à part entière",
    "shown slowed down (log scale)": "affiché au ralenti (échelle log.)",
    "shown slowed down: the slower they pop, the longer the real wait (log scale)": "au ralenti : plus ils sortent lentement, plus l'attente réelle est longue (échelle log.)",
    // scene: shape
    "ripples at the surface: a vibrator": "ondulations en surface : un vibrateur",
    "stretched and rotating: a rotor": "étiré et en rotation : un rotor",
    "round: a sphere": "rond : une sphère",
    "stretched (prolate): a football": "étiré (prolate) : un ballon de rugby",
    "squashed: an oblate disc": "aplati : un disque oblate",
    "{#} phonons": "{#} phonons",
    "no regular": "pas de motif",
    "level pattern": "de niveaux régulier",
    "spacing grows like J(J+{#})": "l'écart croît comme J(J+{#})",
    "equal steps, one phonon each": "pas égaux, un phonon chacun",
    "its lowest levels": "ses niveaux les plus bas",
    "β₂ = {#}": "β₂ = {#}",
    // scene: resonance fingerprint
    "continuum": "continuum",
    "Sₙ ≈ {#} MeV": "Sₙ ≈ {#} MeV",
    "slow neutron": "neutron lent",
    "a slow neutron lands here:": "un neutron lent arrive ici :",
    "lands here": "arrive ici",
    "Sₙ + its kinetic energy": "Sₙ + son énergie cinétique",
    "×{#} million": "×{#} million",
    "×{#} thousand": "×{#} mille",
    "magnified": "agrandi",
    "swells on a peak: the size the neutron effectively “sees” (waves overlap), not a real size change": "gonfle sur un pic : la taille que le neutron « voit » effectivement (les ondes se recouvrent), pas un vrai changement de taille",
    "share taken in": "fraction absorbée",
    "share of the beam taken in": "fraction du faisceau absorbée",
    "{#} (Sₙ)": "{#} (Sₙ)",
    "{#} = exactly Sₙ": "{#} = exactement Sₙ",
    "{#} keV": "{#} keV",
    "{#} eV": "{#} eV",
    "neutron energy →": "énergie du neutron →",
    "neutron's kinetic energy →": "énergie cinétique du neutron →",
    "D₀ ≈ {#} keV: the average gap": "D₀ ≈ {#} keV : l'écart moyen",
    "D₀ ≈ {#} eV: the average gap": "D₀ ≈ {#} eV : l'écart moyen",
    "S₀: average peak strength": "S₀ : intensité moyenne des pics",
    "S₀: how strong the peaks are on average (how easily a neutron gets in)": "S₀ : intensité moyenne des pics (facilité d'entrée d'un neutron)",
    "⟨Γγ⟩ ≈ {#} eV: photon width": "⟨Γγ⟩ ≈ {#} eV : largeur radiative",
    "⟨Γγ⟩ ≈ {#} eV: photon width, about the same for every peak": "⟨Γγ⟩ ≈ {#} eV : largeur radiative, presque la même pour chaque pic",
    "⟨Γγ⟩ ≈ {#} eV: a hairline here": "⟨Γγ⟩ ≈ {#} eV : ici, un trait fin",
    "⟨Γγ⟩ ≈ {#} eV: a hairline here; neutrons widen these peaks": "⟨Γγ⟩ ≈ {#} eV : ici, un trait fin ; les neutrons élargissent ces pics",
    "peaks drawn about {#}× wider than life so they show": "pics dessinés environ {#}× plus larges qu'en réalité pour être visibles",
  };
  // beam readout and per-target labels
  for (const u of ["keV", "eV"]) L[`beam of neutrons at {#} ${u}`] = `faisceau de neutrons à {#} ${u}`;
  const EL = { iron: ["fer", "du fer"], gold: ["or", "de l'or"], uranium: ["uranium", "de l'uranium"] };
  for (const en in EL) {
    L[`${en}{#} levels`] = `niveaux ${EL[en][1]}{#}`;
    L[`${en}{#}: took in {#} of the last {#}`] = `${EL[en][0]}{#} : a absorbé {#} des {#} derniers`;
  }
  // isomer half-life in every unit fmtTime can produce
  const TU = { femtoseconds: "femtosecondes", picoseconds: "picosecondes", nanoseconds: "nanosecondes", microseconds: "microsecondes",
    milliseconds: "millisecondes", seconds: "secondes", minutes: "minutes", hours: "heures", days: "jours", years: "ans" };
  for (const en in TU) L[`half-life about {#} ${en}`] = `demi-vie d'environ {#} ${TU[en]}`;
  L["half-life about {#}×{#}^{#} years"] = "demi-vie d'environ {#}×{#}^{#} ans";
  Object.assign(WT.L.labels, L);
})();
