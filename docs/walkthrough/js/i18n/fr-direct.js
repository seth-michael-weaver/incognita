/* French: direct (Chapitre 6, réactions directes) */
WT.L.ch.direct = {
  num: "Chapitre 6", title: "Réactions directes", short: "Réactions directes",
  lead: "Tous les neutrons qui atteignent le noyau ne sont pas avalés. Certains effleurent sa surface, lui donnent une seule poussée et poursuivent leur route.",
  html: `
<div class="step">
  <p>Un neutron qui ne fait qu'effleurer le noyau peut le pousser une fois vers un niveau excité et poursuivre sa route, surtout vers l'avant et à peine ralenti. C'est une <b>réaction directe</b> : une seule étape, terminée en environ 10⁻²² seconde. Ici, un neutron passe à une distance <i>b</i>, le <b>paramètre d'impact</b>, mesurée en rayons nucléaires <i>R</i> ; l'anneau pointillé est la peau du noyau.</p>
  <div class="ctl"><label for="di-b">Visée b (en rayons)</label><input id="di-b" type="range" data-bind="b" min="0" max="1.5" step="0.01" value="1.0"><output data-show="b" data-fmt="2"></output></div>
  <p>Faites varier <i>b</i>. En dessous d'environ 0,8, le neutron est avalé. Vers 1, il effleure le noyau et le laisse sur son premier niveau excité, 2⁺. Au-delà d'environ 1,2, il passe à côté et se contente d'être dévié : c'est la <b>diffusion élastique</b>, le noyau reste inchangé.</p>
</div>
<div class="step">
  <h3>Excitation rotationnelle des noyaux déformés</h3>
  <p>Une poussée met en rotation un noyau étiré (chapitre 1) et le fait monter l'échelle de sa <b>bande rotationnelle</b> : 0⁺, 2⁺, 4⁺, 6⁺, 8⁺. Le neutron peut faire monter le noyau et le noyau peut le repousser en retour, donc aucun niveau ne peut se calculer isolément. Le moteur les résout tous ensemble : ce sont les <b>voies couplées</b>, où chaque voie est une issue possible, ici un niveau de la bande.</p>
  <div class="btns"><button class="btn" data-act="kick">Le pousser d'un niveau</button><button class="btn ghost" data-act="rpause">Pause / reprise</button></div>
  <div class="ctl"><label for="di-beta">Déformation β₂</label><input id="di-beta" type="range" data-bind="beta2" min="0.05" max="0.4" step="0.01" value="0.25"><output data-show="beta2" data-fmt="2"></output></div>
  <p>Les arcs montrent quels niveaux sont reliés : <i>λ</i> = 2, l'étirement d'ensemble, relie les voisins ; <i>λ</i> = 4, un renflement plus fin, saute d'un niveau sur deux. Faites varier <i>β₂</i> : un noyau plus étiré relie plus fortement ses niveaux, et les arcs s'épaississent. Comme la bande est calculée conjointement avec le neutron incident, le moteur sait exactement combien de neutrons elle prélève, et ne transmet que le reste aux voies plus lentes des chapitres suivants.</p>
</div>
<div class="step">
  <h3>Vibrations de surface</h3>
  <p>Un noyau rond peut onduler, et l'énergie d'ondulation vient par paquets égaux appelés <b>phonons</b>. Un phonon de l'ondulation ballon-disque (<i>λ</i> = 2) donne le niveau 2⁺ ; deux en donnent trois, 0⁺, 2⁺ et 4⁺, à une énergie double. Pour les atteindre, il faut deux poussées successives. Le moteur résout ces niveaux en même temps que l'état fondamental.</p>
  <div class="ctl"><label for="di-lam">Forme de l'ondulation λ</label><input id="di-lam" type="range" data-bind="lam" min="2" max="3" step="1" value="2" data-instant><output data-show="lam" data-fmt="0"></output></div>
  <div class="btns"><button class="btn ghost" data-act="ph1">Un phonon</button><button class="btn ghost" data-act="ph2">Deux phonons</button></div>
  <p>Réglez <i>λ</i> = 3 pour une ondulation en forme de poire, dont le premier niveau est 3⁻. Appuyez sur les boutons pour ajouter un ou deux phonons.</p>
</div>
<div class="step">
  <h3>Réactions directes en une étape</h3>
  <p>Pour la plupart des niveaux, le couplage est faible et une seule poussée suffit : c'est la <b>DWBA</b> (approximation de Born en ondes distordues). L'onde incidente du chapitre 5 pousse le noyau une fois, au bord, là où le potentiel passe de profond à zéro ; le bord s'illumine là où frappent les crêtes. L'onde circulaire qui s'étend représente les neutrons qui ont laissé le noyau excité.</p>
  <div class="ctl"><label for="di-bd">Déformation β du niveau</label><input id="di-bd" type="range" data-bind="bd" min="0.02" max="0.4" step="0.01" value="0.2"><output data-show="bd" data-fmt="2"></output></div>
  <p>Faites varier <i>β</i> : le bord oscille plus fort et les cercles s'éclairent, comme <i>β</i>² : deux fois plus de déformation, quatre fois plus de neutrons. Le moteur prend le <i>β</i> de chaque niveau dans les valeurs mesurées, ou dans des systématiques quand aucune n'est connue. La distribution angulaire des neutrons diffusés est une sortie supplémentaire facultative.</p>
</div>
<div class="step">
  <h3>Résonances géantes</h3>
  <p>Tous les nucléons peuvent bouger ensemble : respirer, s'aplatir et s'étirer, ou osciller en forme de poire. Ce sont les <b>résonances géantes</b>. Dans ce noyau de masse moyenne, elles se situent entre environ 7 et 25 MeV, chacune large de plusieurs MeV, trop large pour compter comme un seul niveau ; les bosses marquent l'<b>énergie d'excitation</b> de chacune.</p>
  <p>Le moteur fixe l'intensité totale de chacune grâce à une <b>règle de somme</b>, une limite issue de la physique fondamentale sur la force avec laquelle un noyau peut répondre, et la répartit en une bosse au-dessus du dernier niveau connu. Ces bosses, plus les poussées vers des niveaux élevés, forment le <b>continuum collectif</b>.</p>
  <div class="btns"><button class="btn ghost" data-act="mono">Respiration</button><button class="btn ghost" data-act="quad">Aplatissement</button><button class="btn ghost" data-act="oct">Poire</button></div>
  <p>La plus connue, où les protons oscillent contre les neutrons (la résonance dipolaire géante), absorbe et émet surtout de la lumière ; elle relève donc du chapitre 10.</p>
</div>
<div class="step">
  <h3>Capture directe</h3>
  <p>Un neutron libre peut tomber directement sur une <b>orbite</b> vide du puits (une énergie permise pour un neutron à l'intérieur) et évacuer l'énergie en trop sous forme de <em class="g">photon</em>. Le noyau ne s'échauffe jamais. C'est la <b>capture directe</b>. Le moteur peut la calculer à partir du même puits qu'au chapitre 5 : l'onde libre à l'extérieur, l'orbite liée à l'intérieur, le photon qui les relie. Elle est facultative et désactivée par défaut.</p>
  <div class="btns"><button class="btn" data-act="drop">Faire tomber un neutron</button></div>
  <p>La capture directe compte surtout là où la voie habituelle, le partage de l'énergie du neutron, est faible : noyaux légers et noyaux loin de la stabilité, avec peu de niveaux, très espacés.</p>
</div>
<div class="step">
  <h3>Flux direct et flux composé</h3>
  <p>Le moteur répartit la section efficace de réaction du chapitre 5 dans l'ordre : d'abord les réactions directes, puis les collisions rapides, et seul le reste forme un noyau composé. Dans l'image, chaque neutron connaît l'un de trois sorts : <b>direct</b> (il effleure et poursuit sa route), rapide (il éjecte un nucléon avant que l'énergie ne se répartisse : le <b>prééquilibre</b>, chapitre 7) ou avalé (un <b>noyau composé</b>, chapitre 8). Les piles les comptent.</p>
  <div class="ctl"><label for="di-e">Énergie du neutron (MeV)</label><input id="di-e" type="range" data-bind="E" min="1" max="60" step="0.5" value="14"><output data-show="E" data-fmt="1"></output></div>
  <p>Faites varier l'énergie et regardez les piles se remplir à nouveau. À quelques MeV, presque tous les neutrons sont avalés. À plusieurs dizaines de MeV, réactions directes et collisions rapides en prennent ensemble une grande partie.</p>
  <div class="aside">Dans le code : <code>ecis/formfactor.py</code>, <code>ecis/coupling.py</code>, <code>ecis/solver.py</code> (potentiel déformé, voies couplées pour rotors et vibrateurs), <code>ecis/dwba.py</code> et <code>direct/dwba.py</code> (poussée unique, résonances géantes, continuum collectif), <code>direct/racapcalc.py</code> (capture directe, facultative, désactivée par défaut), <code>compound/normalization.py</code> (le bilan).</div>
</div>`,
};
Object.assign(WT.L.labels, {
  // scene: aim
  "skin (surface)": "peau (surface)",
  "b = {#} R": "b = {#} R",
  "absorbed: its energy is shared by all nucleons": "absorbé : son énergie se répartit sur tous les nucléons",
  "{#}⁺ level": "niveau {#}⁺",
  "one push leaves the nucleus on {#}⁺; neutron flies on": "une poussée laisse le noyau en {#}⁺ ; le neutron poursuit",
  "a miss: deflected, nucleus unchanged (elastic)": "raté : dévié, noyau inchangé (élastique)",
  // scene: rotor
  "at rest: {#}⁺": "au repos : {#}⁺",
  "rotating: {#}⁺": "en rotation : {#}⁺",
  "rotating: {#}⁺ (paused)": "en rotation : {#}⁺ (en pause)",
  "λ = {#}": "λ = {#}",
  "levels solved together": "niveaux résolus ensemble",
  // scene: vibrator
  "quadrupole ripple: football ↔ disc": "ondulation quadripolaire : ballon ↔ disque",
  "octupole ripple: pear ↔ pear": "ondulation octupolaire : poire ↔ poire",
  "{#}⁺  no phonon": "{#}⁺  aucun phonon",
  "{#}⁺  one phonon": "{#}⁺  un phonon",
  "{#}⁻  one phonon": "{#}⁻  un phonon",
  "{#}⁺ {#}⁺ {#}⁺  two phonons": "{#}⁺ {#}⁺ {#}⁺  deux phonons",
  "{#}⁺ {#}⁺ {#}⁺ {#}⁺  two phonons": "{#}⁺ {#}⁺ {#}⁺ {#}⁺  deux phonons",
  "one push": "une poussée",
  "two pushes": "deux poussées",
  "two phonons": "deux phonons",
  "equal energy steps": "pas d'énergie égaux",
  // scene: DWBA
  "rim: the push happens here": "bord : la poussée a lieu ici",
  "incoming wave": "onde incidente",
  "outgoing: nucleus left excited": "sortante : noyau laissé excité",
  "outgoing circles: the nucleus left on an excited level": "cercles sortants : le noyau laissé sur un niveau excité",
  "push strength ∝ β²: {#}× that at β = {#}": "force de la poussée ∝ β² : {#}× celle à β = {#}",
  // scene: giant resonances
  "breathing": "respiration",
  "squash and stretch": "aplatir et étirer",
  "pear": "poire",
  "breathing (monopole)": "respiration (monopôle)",
  "squash and stretch (quadrupole)": "aplatir et étirer (quadripôle)",
  "pear-shaped (octupole), low and high": "en poire (octupôle), basse et haute",
  "about {#} MeV up": "vers {#} MeV",
  "last known level": "dernier niveau connu",
  "excitation energy (MeV) →": "énergie d'excitation (MeV) →",
  // scene: direct capture
  "free: outside the nucleus": "libre : hors du noyau",
  "empty orbit": "orbite vide",
  "drops straight in; a photon carries off the spare energy": "tombe directement ; un photon emporte l'énergie en trop",
  // scene: ledger
  "direct": "direct",
  "fast (pre-eq.)": "rapide (prééq.)",
  "compound": "composé",
  "direct: grazed, flew on": "direct : a effleuré, est reparti",
  "fast collision: one out at once": "collision rapide : un sort aussitôt",
  "compound: swallowed": "composé : avalé",
  "{#}% (model {#}%)": "{#} % (modèle {#} %)",
  "{#}% seen · model {#}%": "{#} % vus · modèle {#} %",
  "{#} MeV neutrons on a medium-mass nucleus (illustrative shares)": "neutrons de {#} MeV sur un noyau de masse moyenne (parts indicatives)",
});
