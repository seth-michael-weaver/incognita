/* French: preeq (Chapitre 7, prééquilibre) */
WT.L.ch.preeq = {
  num: "Chapitre 7", title: "Émission de prééquilibre", short: "Prééquilibre",
  lead: "Un neutron qui entre dans un noyau ne partage pas son énergie avec tout le monde d'un coup. Pendant les premières collisions, une seule particule en détient l'essentiel, et cette particule peut ressortir aussitôt. C'est le prééquilibre : une émission « avant que l'énergie ne s'égalise ».",
  html: `
<div class="step">
  <p>Deux puits, l'un pour les <em class="p">protons</em>, l'autre pour les <em class="n">neutrons</em>. Chaque boule est un nucléon sur un niveau d'énergie, dessiné comme un barreau ; les barreaux sont remplis depuis le bas jusqu'à la <b>surface de Fermi</b>. Un nucléon au-dessus de la ligne pointillée « libre » a assez d'énergie pour s'échapper. Le moteur suit séparément les protons et les neutrons.</p>
  <p>Le neutron incident plane au-dessus et détient toute l'énergie : la sienne plus plusieurs MeV (millions d'électronvolts) libérés par sa capture.</p>
</div>
<div class="step">
  <h3>Excitations particule-trou</h3>
  <p>Le neutron rapide heurte un nucléon de la mer et lui cède une partie de son énergie. Ce nucléon saute sur un barreau vide, et la place qu'il a quittée est maintenant vide : un <b>trou</b> (l'anneau ouvert). Chaque choc crée donc une <b>paire</b> : un nucléon soulevé de plus et un trou. Les physiciens comptent ensemble les nucléons soulevés et les trous et les appellent <b>excitons</b> : après le premier choc, il y en a 3 (2 soulevés, 1 trou).</p>
  <div class="btns"><button class="btn" data-act="collide">Collision</button><button class="btn ghost" data-act="reset">Recommencer</button></div>
  <p>Appuyez sur Collision et observez un choc : le plongeon, le saut, le trou. Recommencez plusieurs fois. Le nucléon touché peut être un proton ou un neutron. À chaque choc, l'énergie est partagée entre plus de nucléons : chaque nucléon soulevé se trouve plus bas, et le rapide a moins de chances de s'échapper.</p>
</div>
<div class="step">
  <h3>Émission ou nouvelles collisions</h3>
  <p>À chaque étape, le neutron du haut soit s'échappe (flèche vers le haut, seulement s'il est au-dessus de la ligne libre), soit subit une nouvelle collision (flèche vers le bas) ; l'épaisseur indique les probabilités. La vitesse d'échappement se déduit de l'événement inverse : un noyau qui avale facilement un neutron d'une certaine énergie en laisse aussi facilement partir un de cette énergie. Le chapitre 5 a déjà calculé avec quelle facilité il l'avale (cette règle à double sens s'appelle le <b>bilan détaillé</b>). La vitesse de collision, c'est la violence avec laquelle deux nucléons se heurtent, multipliée par le nombre de nouvelles façons de partager l'énergie après le choc.</p>
  <div class="ctl"><label for="pe-n">Étape (excitons n)</label><input id="pe-n" type="range" data-bind="n" min="3" max="11" step="2" value="3" data-instant><output data-show="n" data-fmt="0"></output></div>
  <p>Faites monter l'étape. Au début, une particule détient l'essentiel de l'énergie, donc ce qui s'échappe est rapide. Plus tard, l'énergie est diluée et peu de chose sort.</p>
</div>
<div class="step">
  <h3>Le spectre de prééquilibre</h3>
  <p>La pile de droite est le <b>spectre</b> : combien de neutrons sortent à chaque énergie, les lents à gauche, les rapides à droite. Chaque réaction déroule la chaîne jusqu'à ce que le neutron du haut s'échappe, et sa couleur indique quand : <em style="font-style:normal;color:var(--warm);font-weight:600">orange foncé</em> à l'étape 3, plus pâle ensuite, <em class="n">bleu</em> s'il n'est sorti qu'après que le noyau s'est calmé (chapitre 8).</p>
  <div class="btns"><button class="btn" data-act="run">Lancer 300 réactions</button></div>
  <p>L'étape 3 construit un large dôme bas qui s'étend presque jusqu'à l'énergie maximale, la seule étape à aller si loin. Les étapes suivantes s'empilent plus bas. La bosse bleue est l'<b>évaporation</b> : une fois que tous partagent l'énergie, seuls des neutrons lents s'échappent au compte-gouttes, comme la vapeur d'un liquide chaud.</p>
  <div class="ctl"><label for="pe-e">Énergie du neutron</label><input id="pe-e" type="range" data-bind="E" min="5" max="60" step="0.5" value="20"><output data-show="E" data-fmt="1"></output></div>
  <p>Faites varier l'énergie du neutron incident : une nouvelle série démarre et le dôme s'étend plus loin. L'évaporation seule ne produit jamais de neutrons rapides.</p>
</div>
<div class="step">
  <h3>Densités d'états particule-trou</h3>
  <p>Le compteur passe en revue toutes les façons de placer des particules sur des barreaux vides et des trous dans des barreaux pleins de sorte que leurs énergies totalisent l'énergie à partager (les barreaux sont ici espacés de 1 MeV). Les nucléons sont des fermions : deux d'entre eux ne partagent jamais un barreau, donc une particule doit arriver sur un barreau vide et un trou ne s'ouvre que là où se trouvait un nucléon. C'est le <b>blocage de Pauli</b>.</p>
  <div class="ctl"><label for="pe-u">Énergie à partager (MeV)</label><input id="pe-u" type="range" data-bind="U" min="2" max="16" step="1" value="8" data-instant><output data-show="U" data-fmt="0"></output></div>
  <div class="btns"><button class="btn" data-act="addpair">Ajouter une paire</button><button class="btn ghost" data-act="droppair">Retirer une paire</button></div>
  <p>Ajoutez une paire et le compte bondit ; augmentez l'énergie et il croît à peu près comme <i>E</i><sup>n−1</sup>. Ce compte, la <b>densité d'états particule–trou</b>, fixe le taux de collision : plus il y a de configurations, plus une collision a de destinations possibles. Le moteur compte sur la vraie échelle, avec des barreaux espacés d'une fraction de MeV, et ajoute une limite visible à haute énergie : un trou ne peut pas se trouver sous le fond du puits.</p>
</div>
<div class="step">
  <h3>Émission d'agrégats</h3>
  <p>De petits agrégats peuvent aussi partir tôt. Dans un <b>pick-up</b>, un proton en train de sortir attrape un neutron à la surface et repart avec lui sous forme de <em class="n">deutéron</em> ; s'il en attrape deux, il donne un triton ou un hélium-3. Dans un <b>knock-out</b>, le neutron incident frappe une <em class="a">particule alpha</em> (deux protons et deux neutrons) déjà formée près de la surface et l'éjecte. Le moteur utilise les formules de Kalbach pour les deux.</p>
  <div class="btns"><button class="btn ghost" data-act="pickup">Attraper un neutron → d</button><button class="btn ghost" data-act="knock">Éjecter une α</button></div>
  <p>Appuyez sur un bouton pour en voir un. Les deux donnent aux deutérons et aux alphas leurs propres queues rapides, qui commencent juste au-dessus de l'énergie qu'il faut pour arracher chacun.</p>
</div>
<div class="step">
  <h3>Émission multiple de prééquilibre</h3>
  <p>À haute énergie, le premier choc peut aussi donner beaucoup d'énergie au nucléon touché. Quand le neutron rapide part, ce deuxième nucléon peut encore avoir plus que les 8 MeV dont il a besoin pour sortir (la ligne libre), et il s'envole alors lui aussi : deux particules rapides pour une seule réaction. L'image rejoue une réaction à la fois et dit ce qui se passe à chaque instant ; le nombre à côté de chaque boule est son énergie.</p>
  <div class="ctl"><label for="pe-e2">Énergie du neutron</label><input id="pe-e2" type="range" data-bind="E" min="5" max="80" step="0.5" value="40"><output data-show="E" data-fmt="1"></output></div>
  <p>Faites varier l'énergie. En dessous d'environ 20 MeV, le deuxième nucléon franchit rarement la ligne ; au-delà, de plus en plus de réactions émettent deux particules rapides. C'est le <b>prééquilibre multiple</b>, que le moteur inclut à partir de 20 MeV. Tout ce qui n'est pas parti devient le noyau composé du chapitre suivant. En dessous de quelques MeV (le plus haut niveau discret utilisé pour la cible), le moteur saute entièrement la chaîne.</p>
  <div class="aside">Dans le code : <code>preeq/exciton.py</code> (chaîne d'excitons à deux composantes, taux de collision et d'émission), <code>density/particle_hole.py</code> (densités d'états particule–trou avec corrections de Pauli et de puits fini), <code>preeq/complex.py</code> (pick-up, stripping et knock-out α de Kalbach), <code>preeq/multi.py</code> (prééquilibre multiple), <code>compound/normalization.py</code> (passage au noyau composé).</div>
</div>`,
};
Object.assign(WT.L.labels, {
  // wells
  "protons": "protons",
  "neutrons": "neutrons",
  "Fermi": "Fermi",
  "Fermi surface": "surface de Fermi",
  "free": "libre",
  "free: can escape": "libre : peut s'échapper",
  "all the energy in one nucleon": "toute l'énergie dans un nucléon",
  "{#} particle, {#} holes": "{#} particule, {#} trous",
  // pairs
  "{#} particle, {#} holes: n = {#}": "{#} particule, {#} trous : n = {#}",
  "{#} particle, {#} hole: n = {#}": "{#} particule, {#} trou : n = {#}",
  "{#} particles, {#} hole: n = {#}": "{#} particules, {#} trou : n = {#}",
  "{#} particles, {#} holes: n = {#}": "{#} particules, {#} trous : n = {#}",
  "protons: {#} lifted, {#} hole": "protons : {#} soulevé(s), {#} trou",
  "protons: {#} lifted, {#} holes": "protons : {#} soulevé(s), {#} trous",
  "neutrons: {#} lifted, {#} hole": "neutrons : {#} soulevé(s), {#} trou",
  "neutrons: {#} lifted, {#} holes": "neutrons : {#} soulevé(s), {#} trous",
  "chain ends: the rest becomes a compound nucleus": "fin de chaîne : le reste forme un noyau composé",
  // fork
  "about {#} MeV above surface": "environ {#} MeV au-dessus de la surface",
  "escapes  {#}%": "s'échappe  {#} %",
  "collides again  {#}%": "nouvelle collision  {#} %",
  "below the free line: it cannot leave": "sous la ligne libre : il ne peut pas sortir",
  "n = {#}: {#} particles, {#} hole, {#} MeV": "n = {#} : {#} particules, {#} trou, {#} MeV",
  "n = {#}: {#} particles, {#} holes, {#} MeV": "n = {#} : {#} particules, {#} trous, {#} MeV",
  "stage n = {#}: {#} particles and {#} hole share {#} MeV": "étape n = {#} : {#} particules et {#} trou se partagent {#} MeV",
  "stage n = {#}: {#} particles and {#} holes share {#} MeV": "étape n = {#} : {#} particules et {#} trous se partagent {#} MeV",
  // tail
  "max {#} MeV": "max. {#} MeV",
  "slow": "lent",
  "fast →": "rapide →",
  "stage {#}": "étape {#}",
  "chain over: compound": "fin de chaîne : composé",
  "left at:": "sorti à :",
  "neutron left at:": "sorti à :",
  "evaporation": "évaporation",
  "{#} of {#} landed · {#} left during the chain": "{#} sur {#} arrivés · {#} sortis pendant la chaîne",
  // pauli
  "well bottom: no deeper hole": "fond du puits : pas de trou plus profond",
  "bottom of the well": "fond du puits",
  "{#} MeV to share": "{#} MeV à partager",
  "{#} particles · {#} hole": "{#} particules · {#} trou",
  "{#} particles · {#} holes": "{#} particules · {#} trous",
  "ways, all counted": "façons, toutes comptées",
  "arrangements so far": "configurations jusqu'ici",
  "one more pair: {#} ways": "une paire de plus : {#} façons",
  "never two on one rung · holes only where a nucleon was": "jamais deux sur un barreau · trous seulement là où était un nucléon",
  "(first {#} shown as ticks)": "(les {#} premières en repères)",
  // cluster
  "a deuteron leaves": "un deutéron s'en va",
  "grabs a neutron at the edge": "attrape un neutron au bord",
  "a fast proton heads out": "un proton rapide sort",
  "an α ({#} protons + {#} neutrons) waits at the edge": "une α ({#} protons + {#} neutrons) attend au bord",
  "knocked straight out": "éjectée d'un coup",
  // second
  "first fast neutron": "premier neutron rapide",
  "second fast proton": "deuxième proton rapide",
  "second fast neutron": "deuxième neutron rapide",
  "below the free line: stays": "sous la ligne libre : reste",
  "below the free line: it stays": "sous la ligne libre : il reste",
  "the rest settles: compound nucleus": "le reste se calme : noyau composé",
  "{#} MeV carried in": "{#} MeV apportés",
  "second fast particle in {#} of the last {#} reactions": "deuxième particule rapide dans {#} des {#} dernières réactions",
});
