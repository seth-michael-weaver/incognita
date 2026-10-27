/* French: static page text (index.html data-i18n keys) and kit UI strings */
Object.assign(WT.L.ui, {
  lang_label: "Langue", nav_teach: "Enseignants",
  brand: "Au cœur d'une réaction nucléaire", nav_physics: "La physique", nav_data: "Tous les nucléides", nav_board: "Tableau des scores", menu: "Menu", site_nav: "Site",
  ways_h: "D'autres portes d'entrée", ways_more: "Ou continuez à défiler : la physique commence ici ↓",
  way1_k: "Explorer", way1_t: "Tous les nucléides", way1_p: "Sections efficaces prédites pour 6168 nucléides, à côté de chaque mesure sélectionnée. Cherchez n'importe quel isotope et voyez tous ses jeux de données.", way1_go: "Ouvrir les données →",
  way2_k: "Comparer", way2_t: "Tableau des scores", way2_p: "Comment le moteur et ses données se comparent à d'autres codes de réactions et bibliothèques, jugés face aux mesures, défaites en premier.", way2_go: "Voir les scores →",
  way3_k: "Exécuter", way3_t: "Le code", way3_p: "Tout ici est ouvert. Clonez le dépôt, consultez n'importe quelle courbe ou exécutez le moteur vous-même.", way3_go: "GitHub →",
  title: "Au cœur d'une réaction nucléaire",
  kicker: "Une explication interactive du moteur de réactions INCOGNITA",
  h1: "Au cœur d'une réaction nucléaire",
  hero1: "Lancez un neutron sur un noyau atomique, et quelque chose en ressort. Ce peut être le neutron lui-même, qui rebondit. Ce peut être un proton, une particule alpha (un petit amas serré de 2 protons et 2 neutrons) ou un éclair de lumière. Un noyau lourd peut même se casser en deux.",
  hero2: "Lequel de ces événements se produit, et à quelle fréquence ? Cette page montre pas à pas comment notre logiciel répond à cette question. Faites défiler la page et essayez les commandes en chemin. Les images suivent la même physique que le moteur ; les nombres qu'elles affichent sont indicatifs.",
  scrollcue: "Faites défiler pour commencer ↓",
  hero_tag: "Un neutron. Un noyau. Bien des façons d'en finir.",
  hero_aud: "Pour les étudiants et toute personne qui découvre la physique nucléaire, et pour les enseignants qui les forment. Professionnels : les données de chaque nucléide sont dans <a href=\"data.html\" data-keep-lang>Tous les nucléides</a>.",
  hero_fire: "Lancer un neutron",
  hero_hint: "ou cliquez n'importe où sur l'image",
  credit_idx: "Le moteur INCOGNITA est un portage de <a href=\"https://doi.org/10.1140/epja/s10050-023-01034-3\">TALYS-2</a> (A. J. Koning, S. Hilaire, S. Goriely) et utilise la base de données de structure nucléaire de TALYS. Ce qu'INCOGNITA ajoute est <a href=\"#code\">détaillé, option par option, à la fin de cette page</a>.",
  coda_h2: "Où cela se trouve dans le code",
  coda_p1: "Chaque étape ci-dessus est un paquet de <code>physics/hf</code>, et le moteur les appelle dans l'ordre où vous venez de les lire. Le moteur est un portage de TALYS-2.x, le code de réactions de référence. Ce qu'il ajoute se trouve derrière des options nommées, dans ces mêmes paquets : la plupart sont désactivées par défaut, quelques corrections sont activées, et chacune peut être ramenée séparément au comportement de TALYS d'origine.",
  coda_table: `
    <thead><tr><th>Chapitre</th><th>Ce qu'il fait</th><th>Code</th></tr></thead>
    <tbody>
      <tr><td><a href="#structure">1</a></td><td>Masses, niveaux, déformation, données de résonances</td><td><code>structure/</code></td></tr>
      <tr><td><a href="#omp">2</a></td><td>Modèle optique, coefficients de transmission (avec quelle facilité les particules entrent et sortent)</td><td><code>omp/</code></td></tr>
      <tr><td><a href="#direct">3</a></td><td>Voies couplées, DWBA, résonances géantes, capture directe (facultative)</td><td><code>ecis/</code>, <code>direct/</code></td></tr>
      <tr><td><a href="#preeq">4</a></td><td>Prééquilibre : modèle d'excitons, pick-up et knock-out, émission multiple</td><td><code>preeq/</code>, <code>density/particle_hole.py</code></td></tr>
      <tr><td><a href="#compound">5</a></td><td>Densités de niveaux (états par MeV), distribution en spin</td><td><code>density/</code></td></tr>
      <tr><td><a href="#decay">6</a></td><td>Choisir une sortie (Hauser–Feshbach), fluctuations des largeurs</td><td><code>compound/</code></td></tr>
      <tr><td><a href="#gamma">7</a></td><td>Fonction de force gamma et transmission γ ; niveaux discrets et isomères</td><td><code>gamma/</code><br><code>structure/levels.py</code></td></tr>
      <tr><td><a href="#cascade">8</a></td><td>La cascade d'émissions de particules et de γ, voies exclusives, résidus</td><td><code>emission/</code></td></tr>
      <tr><td><a href="#fission">9</a></td><td>Barrières de fission et transmission</td><td><code>fission/</code></td></tr>
      <tr><td><a href="#measure">12</a></td><td>Spectres d'émission, distributions angulaires et sections efficaces doublement différentielles (facultatif, en sortie seulement)</td><td><code>specout.py</code><br><code>specang.py</code></td></tr>
      <tr><td><a href="#measure">12</a></td><td>Capture sur des cibles excitées thermiquement et taux stellaires (facultatif)</td><td><code>astro/stellar.py</code></td></tr>
      <tr><td><a href="#measure">12</a></td><td>Incertitude par de nombreuses variantes aléatoires (Total Monte Carlo)</td><td><code>tmc.py</code></td></tr>
      <tr><td></td><td>Le pilote qui exécute les étapes dans l'ordre, et des noyaux de calcul optionnels en C pour la vitesse</td><td><code>engine.py</code><br><code>engine_c.py</code>, <code>native/</code></td></tr>
      <tr><td></td><td>Toutes les valeurs par défaut et options, lues une fois au démarrage ; ainsi que les paramètres ajustés par nucléide de TENDL, appliqués comme TALYS les applique (facultatif)</td><td><code>input/</code></td></tr>
    </tbody>
  `,
  coda_h3_added: "Ajouts par rapport à TALYS",
  coda_p_added: "Les lignes marquées <b>Activé</b> s'exécutent par défaut, si bien qu'un calcul par défaut ne reproduit plus exactement TALYS ; chacune peut être désactivée par un mot-clé ou une variable d'environnement. Les autres restent désactivées sauf si on les active.",
  coda_table_added: `
    <thead><tr><th>Chapitre</th><th>Ce qu'il change</th><th>Code</th></tr></thead>
    <tbody>
      <tr><td><a href="#cascade">8</a></td><td><b>Activé.</b> Bilan du flux bouclé : résidus conservés jusqu'à 10⁻⁹ mb (TALYS : 10⁻³ mb), résidus situés un pas au-delà de la fenêtre de cascade de TALYS conservés, jusqu'à 8 particules de chaque type émises dans les voies exclusives, toutes les branches de désexcitation répétées d'un niveau comptées</td><td><code>emission/fluxclose.py</code><br><code>emission/channels.py</code><br><code>kevleak2.py</code></td></tr>
      <tr><td><a href="#decay">6</a></td><td><b>Activé.</b> L'intervalle supérieur du premier noyau composé est rempli comme le remplissent les photons primaires (pondéré par E<sub>γ</sub>³), et non uniformément</td><td><code>compound/nnleak.py</code></td></tr>
      <tr><td><a href="#decay">6</a></td><td><b>Activé.</b> Pas d'élastique composé moyenné sous les premières résonances (moins de 1 keV), là où l'élastique est une diffusion potentielle</td><td><code>lowepot.py</code></td></tr>
      <tr><td><a href="#decay">6</a></td><td><b>Activé.</b> Cibles déformées sans fission : les sorties neutroniques vers des niveaux hors de la bande couplée utilisent la transmission des voies couplées</td><td><code>compound/ccexitnb.py</code></td></tr>
      <tr><td><a href="#omp">2</a></td><td><b>Activé.</b> L'émission alpha voit un potentiel qui dépend de la température du noyau résiduel ; les projectiles alpha entrent par le modèle alpha 6 ; les potentiels du triton et de l'hélion tiennent compte de la taille du projectile</td><td><code>omp/alphatemp.py</code><br><code>alphaentr.py</code><br><code>omp/tfold.py</code></td></tr>
      <tr><td><a href="#fission">9</a></td><td><b>Activé.</b> Transmission unidimensionnelle exacte à travers chaque bosse de la barrière</td><td><code>fission/wkb.py</code></td></tr>
      <tr><td><a href="#gamma">7</a></td><td><b>Activé.</b> Les facteurs d'intensité E1/M1 propres à chaque noyau, quand un calcul les fournit, sont remplacés par une seule fonction globale de la déformation</td><td><code>gamma/ftglobal.py</code></td></tr>
      <tr><td><a href="#compound">5</a></td><td><b>Activé.</b> Cibles sans espacement de résonances D₀ mesuré qui leur soit propre : la densité de niveaux du continuum de la cible au-dessus de max(E<sub>cut</sub> + 2, S<sub>n</sub> − 6) MeV est relevée d'un facteur donné par une seule règle globale fondée sur la parité, les couches et la déformation. Ajoutée pour transformer en égalité la défaite en (n,p) près du seuil face à l'entrée par défaut de TALYS-2 ; elle dégrade légèrement quelques vues de capture, (n,2n) et (n,α), un dommage accepté et consigné</td><td><code>density/npwindow.py</code></td></tr>
      <tr><td><a href="#gamma">7</a></td><td>Un mode ciseaux plus intense dans les noyaux déformés, d'après des systématiques récentes en accord avec les mesures d'Oslo (environ 4–5× dans les actinides) ; ou une variante dont l'énergie et l'intensité varient avec la déformation</td><td><code>gamma/scissors.py</code></td></tr>
      <tr><td><a href="#gamma">7</a></td><td>Fonction de force gamma renormalisée pour que chaque noyau reproduise son intensité radiative mesurée ⟨Γγ⟩/D₀, pour tous les noyaux de la cascade et pas seulement le premier</td><td><code>gamma/ggnorm.py</code></td></tr>
      <tr><td><a href="#gamma">7</a></td><td>Mode ciseaux plus intense et normalisation de ⟨Γγ⟩ pour les noyaux les plus lourds seulement (Z ≥ 88), en visant la capture aux énergies du keV</td><td><code>gamma/actphys.py</code></td></tr>
      <tr><td><a href="#gamma">7</a></td><td>Notre propre constante de largeur E1 à la place de la table de TALYS issue de TENDL (la recette sans données fournie la fixe)</td><td><code>gamma/e1_width.py</code></td></tr>
      <tr><td><a href="#gamma">7</a></td><td>Intensité E2 collective des bandes rotationnelles dans le quasi-continuum</td><td><code>gamma/isoe2.py</code></td></tr>
      <tr><td><a href="#omp">2</a></td><td>Un ajustement régional du puits optique pour les cibles déformées des terres rares, ajusté sur les S₀ et S₁ mesurés, sans données de capture</td><td><code>omp/regional.py</code></td></tr>
      <tr><td><a href="#omp">2</a></td><td>Les fonctions de force neutronique mesurées S₀, S₁ fixent la transmission des neutrons à basse énergie</td><td><code>omp/sfunc.py</code></td></tr>
      <tr><td><a href="#direct">3</a></td><td>Capture directe sur des orbites liées, avec une correction du code d'origine : dans TALYS standard, elle vaut zéro à moins de demander aussi toutes les sorties du modèle optique</td><td><code>direct/racapcalc.py</code></td></tr>
      <tr><td><a href="#direct">3</a></td><td>Le schéma de couplage de la cible (rotor, vibrateur, sphérique) choisi d'après ses niveaux mesurés</td><td><code>structure/collrule.py</code></td></tr>
      <tr><td><a href="#structure">1</a></td><td>Le continuum commence là où le schéma de niveaux mesuré cesse d'être complet</td><td><code>structure/levcomplete.py</code></td></tr>
      <tr><td><a href="#structure">1</a></td><td>Un niveau dont le spin tabulé est impossible pour son noyau (entier pour A impair) est traité comme un niveau de spin inconnu</td><td><code>structure/levjpar.py</code></td></tr>
      <tr><td><a href="#compound">5</a></td><td>Densité de niveaux à température constante ancrée sur la partie complète des niveaux discrets</td><td><code>density/ctwindow2.py</code></td></tr>
      <tr><td><a href="#fission">9</a></td><td>Bandes rotationnelles d'états de transition aux points selles de la fission</td><td><code>fission/barriers.py</code></td></tr>
      <tr><td><a href="#resonance">10</a></td><td>Capture lorsque seules quelques résonances tombent dans la fenêtre stellaire : la valeur typique d'une série de résonances au lieu de la moyenne</td><td><code>fewres.py</code></td></tr>
      <tr><td></td><td>Quatre garde-fous loin de la stabilité : flux direct plafonné par l'unitarité, une limite sur l'énergie de Fermi, pas de collectivité par défaut pour les noyaux impair-impair, dispersion en spin du prééquilibre normalisée</td><td><code>engphys.py</code></td></tr>
    </tbody>
  `,
  coda_h3_outside: "En dehors du moteur",
  coda_p_outside: "Certaines parties de l'histoire tournent à côté du moteur plutôt qu'à l'intérieur. Les séries statistiques de résonances du <a href=\"#resonance\">chapitre 10</a> se trouvent dans <code>physics/resonance/</code>. Les moyennes maxwelliennes (MACS) du <a href=\"#measure\">chapitre 12</a> sont calculées après coup à partir des courbes de capture du moteur, dans <code>validation/differential/core.py</code> ; en revanche, la capture sur des cibles excitées thermiquement et le taux stellaire sont calculés par le moteur lui-même (<code>astro/stellar.py</code>, facultatif). La couche d'ancrage du <a href=\"#layers\">chapitre 15</a> se trouve dans <code>incognita/terra/</code>.",
  close: "Fermer",
  chapters: "Chapitres",
  nav_board: "Tableau des scores", nav_data_short: "Données",
  coda_repo: "Le code, la bibliothèque et les mesures sélectionnées sont ouverts : <a href=\"https://github.com/seth-michael-weaver/incognita\">seth-michael-weaver/incognita sur GitHub</a>. Vous pouvez consulter vous-même n'importe quelle prédiction sur la page <a href=\"data.html?lang=fr\">Tous les nucléides</a>, ou cloner le dépôt et l'exécuter.",
  diagram: "Schéma",
});

Object.assign(WT.L.ui, { pause_sweep: "Mettre le balayage en pause", play_sweep: "Reprendre le balayage" });

/* course mode: audience note, chapter level tags, per-step links */
Object.assign(WT.L.ui, {
  audience: '<b>Pour qui :</b> toute personne curieuse. Les premiers chapitres ne demandent aucune connaissance en physique ; les derniers vont jusqu\'au niveau de la recherche. Chaque chapitre porte une étiquette : <span class="lvl l0">Initiation</span>, <span class="lvl l1">Intermédiaire</span>, <span class="lvl l2">Avancé</span> ou <span class="lvl l3">Expert</span>. Vous enseignez ? Consultez le <a href="instructors.html" data-keep-lang>guide pour les enseignants</a>.',
  lvl0: "Initiation", lvl1: "Intermédiaire", lvl2: "Avancé", lvl3: "Expert", lvl_title: "Niveau",
  step_link: "Copier un lien vers cette étape", link_copied: "Lien copié",
  xp_kicker: "Deuxième partie · Expert",
  xp_h: "Dans le détail",
  xp_p: "Jusqu'ici, chaque étape a été racontée par une image. Les six chapitres qui suivent ouvrent ces mêmes étapes : les formules que le moteur évalue, les approximations qu'elles contiennent et les endroits où elles atteignent leurs limites. Ils s'adressent aux évaluateurs, aux développeurs de modèles et aux doctorants. Les schémas évaluent les formules en direct, avec des entrées indicatives.",
});
