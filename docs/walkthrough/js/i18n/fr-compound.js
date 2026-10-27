/* French: compound (Chapitre 8) */
WT.L.ch.compound = {
  num: "Chapitre 8", title: "Partager l'énergie", short: "Noyau composé",
  lead: "Une fois les premières collisions rapides terminées, tous les nucléons partagent l'énergie. Cet état apaisé est le noyau composé. Pour prédire ce qu'il fera ensuite, le moteur doit savoir de combien de façons il peut stocker son énergie.",
  html: `
<div class="step">
  <p>Un neutron frappe un côté d'un noyau. Son énergie, plus celle libérée par sa capture, forme d'abord un point chaud (la lueur orange) ; les collisions la transmettent et, en environ 10⁻²¹ seconde, chaque nucléon en porte une part.</p>
  <div class="btns"><button class="btn" data-act="hit">Frapper d'un autre côté</button></div>
  <p>Appuyez sur le bouton pour envoyer le neutron d'un autre côté. La lueur finit toujours de la même façon : le noyau a <b>oublié comment il s'est formé</b>. C'est le noyau composé de Bohr. À partir de là, seules trois données comptent : son énergie, son spin (à quel point il tourne) et sa parité (une étiquette + ou − pour sa symétrie miroir).</p>
</div>
<div class="step">
  <h3>Des niveaux séparés à un continuum</h3>
  <p>L'échelle de gauche contient les états du noyau, l'énergie croissant vers le haut ; la fenêtre de droite agrandit une tranche de 1 MeV autour de la boule orange. Près du bas, les barreaux sont très espacés, et chacun a été mesuré. Plus haut, les façons de répartir l'énergie entre 56 nucléons se multiplient jusqu'à ce que les barreaux se fondent en une bande continue : le continuum.</p>
  <div class="ctl"><label for="cn-e">Énergie d'excitation</label><input id="cn-e" type="range" data-bind="E" min="0" max="20" step="0.1" value="6.5"><output data-show="E" data-fmt="1"></output></div>
  <p>Faites varier l'énergie d'excitation (l'énergie stockée au-dessus de l'état le plus bas, en MeV) et regardez la fenêtre. La <b>densité de niveaux</b> ρ, en états par MeV, croît à peu près comme e<sup>2√(aE)</sup>, où <i>a</i> fixe le rythme propre à chaque noyau : quelques-uns par MeV à 3 MeV, des centaines vers 8 MeV (où un neutron pourrait s'échapper), des millions à 20 MeV. Là-haut, le moteur travaille directement avec ρ.</p>
</div>
<div class="step">
  <h3>Trois morceaux, raccordés à une énergie</h3>
  <p>La hauteur du relief est la densité de niveaux en échelle logarithmique, l'énergie croissant vers la droite. En bas à gauche se trouvent les niveaux comptés. La planche droite est la loi à <b>température constante</b> : ρ est multipliée par e (environ 2,7) tous les <i>T</i> MeV, où <i>T</i> est la température nucléaire. Le versant est le <b>gaz de Fermi</b>, qui traite les nucléons comme des particules indépendantes. Sauf pour les cibles les plus lourdes, pour lesquelles il lit des densités tabulées, le moteur utilise ce couple par défaut.</p>
  <div class="ctl"><label for="cn-ex">Énergie de raccordement</label><input id="cn-ex" type="range" data-bind="Ex" min="4.5" max="12" step="0.05" value="6"><output data-show="Ex" data-fmt="1"></output></div>
  <p>Faites varier l'énergie de raccordement : le point de jonction glisse le long du versant, et la planche pivote pour le rejoindre avec la même hauteur et la même pente. Les deux piles du dessous comparent les niveaux prédits par la planche à ceux réellement comptés. Un seul point de jonction les rend égaux ; la planche devient alors verte. C'est l'énergie que choisit le moteur.</p>
</div>
<div class="step">
  <h3>Des couches qui fondent</h3>
  <p>Niveaux individuels de nucléons, deux nucléons chacun, pour deux noyaux. À gauche, une couche fermée : tout ce qui est sous un grand écart est plein, donc tout déplacement coûte l'écart entier. À droite, un noyau de milieu de couche avec un niveau supérieur à moitié plein, donc des déplacements bon marché existent tout de suite. Chaque compteur indique combien de configurations peuvent contenir la chaleur donnée.</p>
  <div class="ctl"><label for="cn-u">Chaleur (excitation)</label><input id="cn-u" type="range" data-bind="U" min="0" max="40" step="0.5" value="3"><output data-show="U" data-fmt="1"></output></div>
  <p>Augmentez la chaleur et regardez les nucléons sauter. À faible chaleur, la couche fermée manque de configurations ; avec assez de chaleur, l'écart ne compte plus et les deux comptes croissent de la même façon. Le <b>paramètre de densité de niveaux</b> <i>a</i> traduit cela : les aiguilles partent séparées et convergent vers la valeur lissée <i>ã</i> sur environ 10 MeV. Le moteur atténue la correction de couches δW à un rythme γ :</p>
  <div class="formula">a(U) = ã · [1 + δW · (1 − e<sup>−γU</sup>) / U]</div>
</div>
<div class="step">
  <h3>Triés par spin et parité</h3>
  <p>Les états à une énergie donnée se rangent dans des tiroirs selon leur spin <i>J</i>, le moment angulaire du noyau : jetons pleins pour la parité +, creux pour la parité −. Les tiroirs du milieu se remplissent le plus, selon (2<i>J</i>+1) e<sup>−(J+½)²/2σ²</sup>, où le paramètre de coupure en spin σ fixe l'étalement. Les deux parités sont à peu près à égalité.</p>
  <div class="ctl"><label for="cn-u2">Excitation</label><input id="cn-u2" type="range" data-bind="U2" min="1" max="30" step="0.5" value="8"><output data-show="U2" data-fmt="1"></output></div>
  <div class="btns"><button class="btn ghost" data-act="deform">Déformer le noyau</button></div>
  <p>Augmentez l'excitation : σ grandit, car un noyau plus chaud peut porter plus de spin. Appuyez ensuite sur Déformer. Un noyau en forme de ballon de rugby peut aussi tourner d'un bloc, donc chaque tiroir gagne des états (les jetons bleus) : c'est l'<b>amplification collective</b>. Par défaut, le moteur ne l'ajoute que pour les cibles de plus d'environ 215 nucléons.</p>
</div>
<div class="step">
  <h3>Découpé en intervalles</h3>
  <p>Au-dessus du dernier niveau compté, le moteur découpe le continuum en tranches de même largeur en énergie, appelées intervalles (bins). Dans chaque intervalle, les points se regroupent en un bloc de ρ·ΔE états (ΔE est la largeur de l'intervalle), triés par spin et parité comme ci-dessus.</p>
  <div class="ctl"><label for="cn-emax">Haut de l'échelle</label><input id="cn-emax" type="range" data-bind="Emax" min="8" max="30" step="0.5" value="14"><output data-show="Emax" data-fmt="1"></output></div>
  <div class="btns"><button class="btn ghost" data-act="rebin">Trier à nouveau</button></div>
  <p>Faites varier le haut de l'échelle, l'énergie maximale que le neutron peut apporter. Le même nombre d'intervalles doit couvrir plus d'énergie, donc chacun grandit. La boule orange descend d'intervalle en intervalle : toutes les étapes suivantes (le choix d'une sortie, la cascade de photons, le parcours sur la carte) travaillent sur ces intervalles. Dix sont dessinés ici ; le moteur en utilise jusqu'à 40.</p>
  <div class="aside">Dans le code : <code>density/parameters.py</code> (<i>a</i>(U) d'Ignatyuk, coupure en spin, distribution de Wigner, amplification collective), <code>density/models.py</code> (température constante, gaz de Fermi, tables), <code>density/matching.py</code> (l'énergie de raccordement à partir des niveaux comptés), <code>core/grids.py</code> (intervalles d'excitation).</div>
</div>`,
};
(function () {
  const L = {
    // scene 1
    "a neutron comes in": "un neutron arrive",
    "a hot spot: the energy is still local": "un point chaud : l'énergie est encore localisée",
    "equilibrium: every nucleon holds a share": "équilibre : chaque nucléon en détient une part",
    "no trace left of where it was hit": "plus aucune trace de l'endroit de l'impact",
    // scene 2
    "ground state": "état fondamental",
    "{#}–{#} MeV, magnified": "{#}–{#} MeV, agrandi",
    "no level in this slice": "aucun niveau dans cette tranche",
    "{#} rung in {#} MeV": "{#} barreau dans {#} MeV",
    "{#} rungs in {#} MeV": "{#} barreaux dans {#} MeV",
    "{#} rung in this {#}-MeV slice": "{#} barreau dans cette tranche de {#} MeV",
    "{#} rungs in this {#}-MeV slice": "{#} barreaux dans cette tranche de {#} MeV",
    "about {#} rungs: too close to draw": "environ {#} barreaux : trop serrés pour les dessiner",
    "about {#}k rungs: too close to draw": "environ {#} mille barreaux : trop serrés pour les dessiner",
    "about {#}M rungs: too close to draw": "environ {#} M de barreaux : trop serrés pour les dessiner",
    "about {#}B rungs: too close to draw": "environ {#} Md de barreaux : trop serrés pour les dessiner",
    "about {#} rungs in this slice: too close to draw": "environ {#} barreaux dans cette tranche : trop serrés pour les dessiner",
    "about {#} thousand rungs in this slice: too close to draw": "environ {#} mille barreaux dans cette tranche : trop serrés pour les dessiner",
    "about {#} million rungs in this slice: too close to draw": "environ {#} millions de barreaux dans cette tranche : trop serrés pour les dessiner",
    "about {#} billion rungs in this slice: too close to draw": "environ {#} milliards de barreaux dans cette tranche : trop serrés pour les dessiner",
    "each one measured: energy, spin and parity": "chacun mesuré : énergie, spin et parité",
    "the rungs are multiplying": "les barreaux se multiplient",
    "a continuum: the engine uses ρ itself": "un continuum : le moteur utilise ρ directement",
    "≈ energy to free a neutron": "≈ énergie pour libérer un neutron",
    "energy ↑": "énergie ↑",
    // scene 3
    "gap: plank below the rungs": "écart : planche sous les barreaux",
    "gap: plank above the rungs": "écart : planche au-dessus des barreaux",
    "counted levels": "niveaux comptés",
    "CT plank": "planche TC",
    "constant-temperature plank": "planche à température constante",
    "Fermi-gas hillside": "versant du gaz de Fermi",
    "joint {#} MeV": "jonction {#} MeV",
    "energy →": "énergie →",
    "+{#} more": "+{#} de plus",
    "{#} counted": "{#} comptés",
    "{#} predicted": "{#} prédits",
    "{#}+ predicted": "{#}+ prédits",
    "equal: the plank rests on the counted rungs": "égaux : la planche repose sur les barreaux comptés",
    "too few: the plank is too steep and sinks": "trop peu : la planche est trop raide et s'enfonce",
    "too many: the plank is too shallow and floats": "trop : la planche est trop plate et flotte",
    // scene 4
    "closed shell": "couche fermée",
    "mid-shell": "milieu de couche",
    "gap": "écart",
    "no arrangement holds this heat": "aucune configuration ne contient cette chaleur",
    "≈ {#} arrangement": "≈ {#} configuration",
    "≈ {#} arrangements": "≈ {#} configurations",
    "≈ {#} thousand arrangements": "≈ {#} mille configurations",
    "≈ {#} million arrangements": "≈ {#} millions de configurations",
    "≈ {#} billion arrangements": "≈ {#} milliards de configurations",
    "a ≈ {#}": "a ≈ {#}",
    "cold: nobody can move": "froid : personne ne peut bouger",
    "temperature ≈ {#} MeV": "température ≈ {#} MeV",
    // scene 5
    "states at {#} MeV": "états à {#} MeV",
    "spin J →": "spin J →",
    "+ parity": "parité +",
    "− parity": "parité −",
    "rotation ×{#}": "rotation ×{#}",
    "added by rotation: ×{#} (a few drawn)": "ajoutés par la rotation : ×{#} (quelques-uns dessinés)",
    "spread σ ≈ {#}: most states near J ≈ {#}": "étalement σ ≈ {#} : la plupart des états vers J ≈ {#}",
    "deformed: it can rotate": "déformé : il peut tourner",
    "spherical": "sphérique",
    // scene 6
    "≈ {#} thousand": "≈ {#} mille",
    "≈ {#} million": "≈ {#} millions",
    "≈ {#} billion": "≈ {#} milliards",
    "≈ {#}k": "≈ {#} k",
    "≈ {#}M": "≈ {#} M",
    "≈ {#}B": "≈ {#} Md",
    "{#} bins, each {#} MeV wide": "{#} intervalles de {#} MeV chacun",
    "counted": "comptés",
    "states in each bin": "états par intervalle",
  };
  Object.assign(WT.L.labels, L);
})();
