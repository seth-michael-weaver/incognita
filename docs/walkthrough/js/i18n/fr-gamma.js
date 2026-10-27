/* French: gamma (Chapter 7, photon emission) */
WT.L.ch.gamma = {
  num: "Chapitre 10", title: "Émettre de la lumière", short: "Photons",
  lead: "Quand aucune particule ne sort, le noyau se refroidit en émettant des photons : des rayons gamma, des particules de lumière de haute énergie. Cette sortie est ouverte à toutes les énergies.",
  html: `
<div class="step">
  <p>Un état chaud à 8 MeV (millions d'électronvolts) émet des photons (γ) ; la pile à côté de l'échelle recueille les endroits où ils aboutissent. Sous 2 MeV, les états sont quelques barreaux nommés ; au-dessus, une foule qui s'épaissit très vite avec l'énergie (points gris). Chaque photon emporte l'énergie de sa chute, <i>E<sub>γ</sub></i>, et il est dessiné d'autant plus brillant que <i>E<sub>γ</sub></i>³ est grand.</p>
  <div class="formula">T<sub>γ</sub>(E<sub>γ</sub>) = 2π · E<sub>γ</sub><sup>2l+1</sup> · f(E<sub>γ</sub>)</div>
  <p><i>T<sub>γ</sub></i> est le coefficient de transmission du photon (la porte du chapitre 9), <i>l</i> = 1 pour les photons dipolaires, et <i>f</i> est la <b>fonction de force gamma</b> : la facilité avec laquelle le noyau rayonne à cette énergie. La probabilité d'une chute est <i>T<sub>γ</sub></i> multiplié par la foule d'états où elle aboutit : les petites chutes trouvent beaucoup d'états mais sont faibles ; les grandes sont brillantes mais en trouvent peu.</p>
  <div class="ctl"><label for="gm-e0">Énergie de départ</label><input id="gm-e0" type="range" data-bind="E0" min="3" max="9" step="0.5" value="8"><output data-show="E0" data-fmt="1"></output></div>
  <div class="btns"><button class="btn" data-act="emit">En émettre 100</button></div>
  <p>La pile culmine quelques MeV sous le départ : la plupart des photons emportent de 2 à 4 MeV. Déplacez l'énergie de départ, et le pic suit.</p>
</div>
<div class="step">
  <h3>Tout le noyau vibre</h3>
  <p>Le grand pic de droite est la <b>résonance dipolaire géante</b> : tous les protons (hachurés, à gauche) oscillant contre tous les neutrons (pleins). Sa fréquence fixe l'énergie de photon que le noyau absorbe et émet le plus facilement. La courbe est la fonction de force gamma <i>f</i>, en échelle logarithmique (chaque cran vers le haut vaut dix fois plus).</p>
  <div class="ctl"><label for="gm-a">Nombre de masse A</label><input id="gm-a" type="range" data-bind="A" min="40" max="240" step="1" value="112"><output data-show="A" data-fmt="0"></output></div>
  <p>Faites glisser le nombre de masse A (protons plus neutrons) : les noyaux lourds oscillent plus lentement et vibrent vers 12 à 14 MeV ; les légers, vers 20. Un noyau qui se désexcite émet des photons de quelques MeV seulement, si bien que ce qui compte le plus, c'est la queue ombrée de basse énergie.</p>
</div>
<div class="step">
  <h3>Les ciseaux et l'upbend</h3>
  <p>Un noyau déformé rayonne aussi de façon magnétique : ses protons (hachurés) et ses neutrons (pleins), deux ballons de rugby, basculent l'un contre l'autre comme les lames d'une paire de ciseaux. Ce <b>mode ciseaux</b> se situe vers 3 MeV. Le <b>spin-flip</b> (renversement de spin), vers 8 MeV, correspond à des nucléons isolés qui retournent leur spin (les petites flèches), quelle que soit la forme.</p>
  <div class="ctl"><label for="gm-b">Déformation β₂</label><input id="gm-b" type="range" data-bind="beta" min="0" max="0.35" step="0.01" value="0.25"><output data-show="beta" data-fmt="2"></output></div>
  <p>Faites glisser la déformation β₂ (0 correspond à une sphère). Plus le noyau est étiré, plus il émet de photons de ciseaux ; une sphère n'en émet aucun. Aux énergies les plus basses, la force remonte : c'est l'<b>upbend</b> (remontée), un filet de photons mous, que le moteur affaiblit à mesure que le noyau se déforme. Une option, désactivée par défaut, utilise des systématiques de ciseaux plus intenses, en accord avec les mesures d'Oslo (quatre à cinq fois plus intenses dans l'uranium).</p>
</div>
<div class="step">
  <h3>En descendant l'échelle</h3>
  <p>Une cascade, ce sont des photons émis l'un après l'autre, depuis les intervalles du haut (des états trop denses pour être listés, chapitre 8) jusqu'aux niveaux nommés, étirés pour être lisibles (barreau plein parité +, creux −). Là, le moteur cesse d'estimer et suit les <b>rapports d'embranchement</b> tabulés : les probabilités mesurées que chaque niveau se désexcite vers chacun des niveaux inférieurs.</p>
  <div class="btns"><button class="btn" data-act="drop">Lâcher une cascade</button></div>
  <p>Appuyez plusieurs fois sur le bouton : la partie haute change à chaque fois ; la fin suit l'un des quelques chemins mesurés.</p>
</div>
<div class="step">
  <h3>Des paliers qui retiennent</h3>
  <p>Le niveau 11/2− à 0,40 MeV est un <b>isomère</b> : son spin est si éloigné de celui des niveaux inférieurs qu'un photon peut à peine les relier ; il vit donc de quelques secondes à des années, et tout ce qui y aboutit y reste. Le moteur traite tout niveau vivant plus d'une seconde comme un point final. Chaque bille est une cascade, qui finit dans la pile de l'isomère ou dans celle de l'état fondamental.</p>
  <div class="ctl"><label for="gm-j">Spin d'entrée</label><input id="gm-j" type="range" data-bind="J0" min="0" max="8" step="1" value="2" data-instant><output id="gm-jout">5/2</output></div>
  <p>Faites glisser le spin d'entrée, là où les cascades commencent, et les piles repartent de zéro. La fraction qui aboutit sur l'isomère, le <b>rapport isomérique</b>, en dépend : un départ de spin élevé alimente l'isomère de spin élevé ; un départ de spin faible le contourne et descend jusqu'à l'état fondamental.</p>
</div>
<div class="step">
  <h3>Capture</h3>
  <p>Un noyau qui vient d'absorber un neutron lent a deux portes de sortie (chapitre 9) : les photons (en haut) et le neutron qui ressort (à droite). L'ouverture de chaque porte est sa <b>largeur</b>, en eV : la rapidité avec laquelle le noyau se désexcite par cette voie. La largeur photon varie à peine ; la largeur neutron croît avec la vitesse du neutron.</p>
  <div class="ctl"><label for="gm-e">Énergie du neutron</label><input id="gm-e" type="range" data-bind="lgE" min="-2" max="3.3" step="0.02" value="0"><output id="gm-eout">1.0 keV</output></div>
  <p>Faites glisser l'énergie du neutron, de 10 eV à 2 MeV. La <b>capture</b>, (n,γ), signifie que le neutron reste et qu'un photon sort : elle l'emporte presque toujours à 10 eV et ne représente plus qu'une petite fraction au-delà de quelques keV. La largeur photon au seuil est mesurée pour des centaines de noyaux, ce qui permet de vérifier la fonction de force gamma. Par défaut, le moteur utilise la sienne ; une option ajuste la fonction de force de chaque noyau mesuré jusqu'à ce que les deux concordent.</p>
  <div class="aside">Dans le code : <code>gamma/parameters.py</code> (forces E1 tabulées ; systématiques de la résonance géante, du spin-flip, des ciseaux et de l'upbend), <code>gamma/strength.py</code> (<i>f</i>(E<sub>γ</sub>) pour chaque multipôle), <code>gamma/transmission.py</code> (T<sub>γ</sub> et la largeur radiative moyenne), <code>structure/levels.py</code> (rapports d'embranchement, isomères), <code>emission/multiple.py</code> (la cascade). Facultatifs, désactivés par défaut : <code>gamma/scissors.py</code> (ciseaux plus intenses), <code>gamma/ggnorm.py</code> (ajuster au ⟨Γγ⟩ mesuré, jusqu'au plomb), <code>gamma/actphys.py</code> (les deux, pour les actinides).</div>
</div>`,
};
Object.assign(WT.L.labels, {
  // scene 1: emit
  "energy ↑": "énergie ↑",
  "named levels": "niveaux nommés",
  "a crowd of states": "une foule d'états",
  "{#} MeV": "{#} MeV",
  "hot state, {#} MeV": "état chaud, {#} MeV",
  "most photons ≈ {#} MeV": "le plus souvent ≈ {#} MeV",
  "small drops: faint (E³ tiny)": "petites chutes : faibles (E³ minuscule)",
  "big drops: bright, but few states to land on": "grandes chutes : brillantes, mais peu d'états où aboutir",
  // scene 2: gdr
  "protons": "protons",
  "neutrons": "neutrons",
  "A = {#}: rings at {#} MeV": "A = {#} : vibre à {#} MeV",
  "peak {#} MeV": "pic {#} MeV",
  "giant resonance at {#} MeV": "résonance géante à {#} MeV",
  "width ≈ {#} MeV": "largeur ≈ {#} MeV",
  "decays use this": "celle qui sert",
  "shaded: the tail decays use": "ombré : la queue qui sert",
  "photon energy (MeV) →": "énergie du photon (MeV) →",
  "photon strength f (log scale) ↑": "fonction de force f (échelle log) ↑",
  // scene 3: m1
  "a sphere has no blades: no scissors": "une sphère n'a pas de lames : pas de ciseaux",
  "scissors ≈ {#} MeV: strength {#} % of the most stretched": "ciseaux ≈ {#} MeV : force à {#} % du plus étiré",
  "spin-flip ≈ {#} MeV: steady, any shape (thick photons)": "spin-flip ≈ {#} MeV : stable, toute forme (photons épais)",
  "upbend below {#} MeV: soft photons, plenty at this shape": "upbend sous {#} MeV : photons mous, nombreux à cette forme",
  "upbend below {#} MeV: soft photons, fewer at this shape": "upbend sous {#} MeV : photons mous, moins nombreux à cette forme",
  "upbend below {#} MeV: soft photons, few at this shape": "upbend sous {#} MeV : photons mous, rares à cette forme",
  // scene 4: cascade
  "ground state": "état fondamental",
  "isomer": "isomère",
  "isomer: long-lived": "isomère : longue durée de vie",
  "bins: too dense to list": "intervalles : trop denses",
  "one photon at a time": "un photon à la fois",
  "measured branching ratios": "embranchements mesurés",
  "▬ parity +   ▭ parity −": "▬ parité +   ▭ parité −",
  // scene 5: isomer
  "entrance: J = {#}/{#}": "entrée : J = {#}/{#}",
  "isomer: {#} ({#} %)": "isomère : {#} ({#} %)",
  "ground state: {#} ({#} %)": "état fondamental : {#} ({#} %)",
  "many cascades: ≈ {#} % isomer": "nombreuses cascades : ≈ {#} % isomère",
  "over many cascades from J = {#}/{#}: ≈ {#} % end on the isomer": "sur de nombreuses cascades depuis J = {#}/{#} : ≈ {#} % finissent sur l'isomère",
  // scene 6: capture
  "photon door: {#} eV, barely changes": "porte du photon : {#} eV, varie à peine",
  "captured (n,γ): {#} ({#} %)": "capturés (n,γ) : {#} ({#} %)",
  "neutron: {#} eV": "neutron : {#} eV",
  "neutron door: {#} eV, wider when faster": "porte du neutron : {#} eV, plus large s'il va vite",
  "back out: {#} ({#} %)": "ressortis : {#} ({#} %)",
  "more doors open (target left excited)": "plus de portes (cible laissée excitée)",
  "{#} eV neutrons →": "neutrons de {#} eV →",
  "{#} keV neutrons →": "neutrons de {#} keV →",
  "{#} MeV neutrons →": "neutrons de {#} MeV →",
  "slow neutrons: the photon door wins": "neutrons lents : la porte du photon l'emporte",
  "the neutron door wins; capture takes about {#} %": "la porte du neutron l'emporte ; la capture prend ≈ {#} %",
  "fast: capture is a rare event": "rapides : la capture est un événement rare",
});
