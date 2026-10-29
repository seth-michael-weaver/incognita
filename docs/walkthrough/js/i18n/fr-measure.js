/* French: measure (chapter 11) */
WT.L.ch.measure = {
  num: "Chapitre 17", title: "Observables", short: "Observables",
  lead: "Une expérience, un réacteur ou une étoile ne voient qu'une poignée de nombres. Ce chapitre montre comment le moteur transforme ce qui se passe dans le noyau en ces nombres.",
  html: `
<div class="step">
  <p>Le disque pâle autour de chaque noyau est sa <b>section efficace</b> : la surface qu'un neutron doit toucher pour qu'une réaction ait lieu, et non la taille réelle du noyau. Un faisceau arrive de la gauche et traverse une mince feuille de noyaux ; la fraction qui réagit est cette surface multipliée par le nombre de noyaux rencontrés. L'unité est le barn (10⁻²⁴ cm², à peu près la face d'un noyau d'uranium).</p>
  <div class="ctl"><label for="mea-e">Énergie du neutron (MeV)</label><input id="mea-e" type="range" data-bind="E" min="0.1" max="20" step="0.1" value="2"><output data-show="E" data-fmt="1"></output></div>
  <p>Baissez l'énergie et les disques gonflent : un neutron lent est une onde étendue et réagit de plus loin. À haute énergie, le disque se réduit jusqu'au noyau lui-même.</p>
</div>
<div class="step">
  <h3>Fonctions d'excitation</h3>
  <p>Chaque porte est une sortie, ou <b>voie</b> : le neutron rebondit (élastique), laisse la cible excitée (n′), arrache d'autres neutrons (2n, 3n), est capturé et seuls des photons sortent (γ), ou bien c'est un proton ou une particule α qui sort. Une porte cadenassée a un <b>seuil</b> : la réaction coûte plus d'énergie que le neutron n'en apporte.</p>
  <div class="ctl"><label for="mea-e2">Énergie du neutron (MeV)</label><input id="mea-e2" type="range" data-bind="E" min="0.1" max="20" step="0.1" value="2"><output data-show="E" data-fmt="1"></output></div>
  <p>Faites glisser l'énergie au-delà d'un seuil et cette porte s'ouvre dans un éclair ; les seaux se remplissent selon la part de chaque voie, et chaque nouvelle porte prend une part aux autres. Les seuils viennent des masses des noyaux ; les parts, de la compétition du chapitre 9.</p>
</div>
<div class="step">
  <h3>Spectres d'émission</h3>
  <p>Les deux piles sont les neutrons qui atteignent la moitié avant et la moitié arrière d'un anneau de détecteurs, triés par énergie. Le faisceau est pulsé : le temps de vol de chaque neutron donne donc son énergie, les rapides arrivant en premier.</p>
  <div class="ctl"><label for="mea-ein">Énergie incidente (MeV)</label><input id="mea-ein" type="range" data-bind="Ein" min="5" max="60" step="0.5" value="30"><output data-show="Ein" data-fmt="0"></output></div>
  <p>Les deux piles ont une bosse de neutrons lents, <b>évaporés</b> : ils s'échappent du noyau composé une fois l'énergie partagée, de la même façon dans toutes les directions. Seule la pile avant a une longue queue rapide : des neutrons de <b>prééquilibre</b>, qui partent dès les premières collisions en se déplaçant encore à peu près dans le sens du faisceau. Augmentez l'énergie incidente et la queue grandit.</p>
</div>
<div class="step">
  <h3>Distributions angulaires</h3>
  <p>Le pétale montre combien de neutrons partent dans chaque direction ; le faisceau arrive de la gauche. Les neutrons évaporés ont oublié le faisceau et partent de la même façon dans toutes les directions ; les rapides du prééquilibre penchent vers l'avant. La règle de Kalbach fixe dans quelle mesure, avec une seule pente <i>a</i> qui croît avec l'énergie de sortie. Le moteur peut aussi écrire ces distributions angulaires, en sortie facultative.</p>
  <div class="ctl"><label for="mea-eo">Énergie de sortie (MeV)</label><input id="mea-eo" type="range" data-bind="Eout" min="1" max="45" step="0.5" value="25"><output data-show="Eout" data-fmt="1"></output></div>
  <p>Baissez l'énergie de sortie et le pétale s'arrondit : les neutrons lents sont surtout des neutrons évaporés.</p>
  <div class="formula">dσ/dΩ ∝ e<sup>a cos θ</sup></div>
</div>
<div class="step">
  <h3>Sections efficaces moyennées sur une maxwellienne</h3>
  <p>La pile du bas recueille les énergies des neutrons capturés dans le gaz chaud d'une étoile. Leurs vitesses suivent une distribution de Maxwell fixée par la température <i>kT</i> (30 keV correspondent à environ 350 millions de degrés) ; les traînées plus longues sont des neutrons plus rapides, et chaque passage près d'un noyau peut finir par un éclair de capture.</p>
  <div class="ctl"><label for="mea-kt">Température kT (keV)</label><input id="mea-kt" type="range" data-bind="kT" min="5" max="100" step="1" value="30"><output data-show="kT" data-fmt="0"></output></div>
  <p>Les neutrons lents sont faciles à capturer mais passent rarement, et les rapides sont peu nombreux : la plupart des captures proviennent d'une fenêtre large de quelques <i>kT</i>. Le taux sur l'ensemble du gaz est la <b>section efficace moyennée sur une maxwellienne</b> (MACS), en millibarns (mb). Chauffez le gaz et la fenêtre glisse vers les hautes énergies, où la cible est plus petite. La MACS est obtenue en intégrant la courbe de capture du moteur.</p>
</div>
<div class="step">
  <h3>Cibles thermiquement excitées</h3>
  <p>Les billes montrent quelle fraction des noyaux cibles se trouve sur chacun de leurs niveaux les plus bas à cette température. Dans une étoile, certaines cibles sont déjà excitées, et chaque niveau excité est une entrée différente vers le même noyau composé. Un niveau de spin <i>J</i> en accueille davantage, car il possède 2<i>J</i>+1 orientations.</p>
  <div class="ctl"><label for="mea-kt2">Température kT (keV)</label><input id="mea-kt2" type="range" data-bind="kT" min="5" max="100" step="1" value="30"><output data-show="kT" data-fmt="0"></output></div>
  <p>Augmentez la température et regardez les noyaux monter. Un taux stellaire calcule la capture depuis chaque niveau peuplé et additionne les résultats avec ces parts ; la somme des poids est la fonction de partition <i>G</i>, et le rapport au taux depuis l'état fondamental est le <b>facteur d'amplification stellaire</b>. Le moteur peut le faire en option, désactivée par défaut ; normalement, chaque cible part de son état fondamental.</p>
</div>
<div class="step">
  <h3>Incertitudes et covariances</h3>
  <p>Chaque disque pâle est un calcul du moteur avec ses données d'entrée perturbées au hasard : la profondeur du puits optique, la densité de niveaux et la fonction de force gamma, chacune connue seulement à quelques pour cent près. La dispersion de nombreux calculs est une incertitude honnête : le <b>Total Monte Carlo</b>.</p>
  <div class="btns"><button class="btn" data-act="tmc1">Lancer une variante</button><button class="btn ghost" data-act="tmc">En lancer 10</button><button class="btn ghost" data-act="clear">Effacer</button></div>
  <p>Un bord net signifie que les données d'entrée fixent la réponse ; un bord flou, qu'elles ne la fixent pas, et c'est là que de nouvelles mesures aideraient le plus.</p>
  <div class="aside">Dans le code : <code>emission/channels.py</code> (voies exclusives et résidus), <code>specout.py</code> et <code>specang.py</code> (spectres de sortie, distributions angulaires et sections efficaces doublement différentielles, écrits seulement sur demande), <code>astro/stellar.py</code> (capture depuis des niveaux de la cible peuplés thermiquement, facultatif), <code>tmc.py</code> (l'échantillonneur Total Monte Carlo). Les MACS depuis l'état fondamental sont obtenues à partir des courbes de capture dans <code>validation/differential/core.py</code>.</div>
</div>`,
};
Object.assign(WT.L.labels, {
  // area
  "each disc: σ ≈ {#} b": "chaque disque : σ ≈ {#} b",
  "each disc: cross section σ ≈ {#} b, the area a neutron must hit": "chaque disque : section efficace σ ≈ {#} b, la surface à toucher",
  "beam →": "faisceau →",
  "nucleus's own face ≈ {#} b · {#} % reacts": "face du noyau ≈ {#} b · {#} % réagit",
  "the nucleus's own face ≈ {#} b · {#} % of the beam reacts in this foil": "la face du noyau lui-même ≈ {#} b · {#} % du faisceau réagit dans cette feuille",
  "slow: the neutron's wave reaches well past the surface": "lent : l'onde du neutron porte bien au-delà de la surface",
  "the target still looks bigger than the nucleus": "la cible paraît encore plus grande que le noyau",
  "fast: close to the nucleus's own size": "rapide : proche de la taille du noyau lui-même",
  // doors
  "elastic": "élastique", "n′ inelastic": "n′ inélastique", "{#}n": "{#}n", "γ capture": "capture γ", "p": "p", "α": "α", "n′": "n′",
  "{#}n · {#} MeV": "{#}n · {#} MeV", "p · {#} MeV": "p · {#} MeV", "α · {#} MeV": "α · {#} MeV", "n′ inelastic · {#} MeV": "n′ inélastique · {#} MeV",
  "opens at {#} MeV": "s'ouvre à {#} MeV",
  "{#} MeV": "{#} MeV",
  // detect
  "forward half": "moitié avant", "backward half": "moitié arrière",
  "pulsed beam": "faisceau pulsé", "pulsed beam →": "faisceau pulsé →",
  "backward": "arrière", "backward detectors": "détecteurs arrière",
  "forward": "avant", "forward detectors": "détecteurs avant",
  "outgoing neutron energy from the flight time (MeV) →": "énergie du neutron sortant d'après le temps de vol (MeV) →",
  "fast tail": "queue rapide", "fast tail: pre-equilibrium": "queue rapide : prééquilibre",
  "evaporated hump": "bosse d'évaporation", "hump: evaporated, every way alike": "bosse : évaporés, toutes directions pareilles",
  "{#} % leave before the energy is shared": "{#} % partent avant le partage de l'énergie",
  // angle
  "beam": "faisceau",
  "forward-to-backward ratio ≈ {#}  ·  slope a ≈ {#}": "rapport avant/arrière ≈ {#}  ·  pente a ≈ {#}",
  "mostly evaporated: every direction alike": "surtout évaporés : toutes directions pareilles",
  "a mix: the fast share leans forward": "un mélange : la part rapide penche vers l'avant",
  "mostly pre-equilibrium: strongly forward": "surtout prééquilibre : fortement vers l'avant",
  "forward →": "avant →",
  // star
  "{#} keV": "{#} keV",
  "kT = {#} keV": "kT = {#} keV",
  "energies of captured neutrons": "énergies des neutrons capturés",
  "each capture drops here, by the neutron's energy: the window that counts": "chaque capture tombe ici selon l'énergie du neutron : la fenêtre qui compte",
  "MACS ≈ {#} mb at kT = {#} keV · captures watched: {#}": "MACS ≈ {#} mb à kT = {#} keV · captures observées : {#}",
  // hot target
  "{#}⁺  ground state": "{#}⁺  fondamental", "{#}⁺  {#} keV": "{#}⁺  {#} keV",
  "target levels, with the share of nuclei sitting on each": "niveaux de la cible, avec la part de noyaux sur chacun",
  "{#} % start from the ground state · partition function G ≈ {#}": "{#} % partent de l'état fondamental · fonction de partition G ≈ {#}",
  // TMC
  "optical well": "puits optique", "optical well depth": "profondeur du puits optique",
  "level density": "densité de niveaux", "photon strength": "fonction de force gamma",
  "σ ≈ {#} b ": "σ ≈ {#} b ", "σ ≈ {#} mb ": "σ ≈ {#} mb ",
  "σ ≈ {#} b ±{#} %": "σ ≈ {#} b ±{#} %", "σ ≈ {#} mb ±{#} %": "σ ≈ {#} mb ±{#} %",
  "dashed: best inputs · each disc drawn at its own scale": "tirets : meilleures entrées · chaque disque à son échelle",
  "dashed ring: the best-value inputs · each energy drawn at its own scale (disc area ∝ σ)": "anneau en tirets : entrées de meilleure valeur · chaque énergie à sa propre échelle (aire ∝ σ)",
  "{#} runs of the engine, each with its inputs nudged at random": "{#} calculs du moteur, chacun avec ses entrées perturbées au hasard",
});
