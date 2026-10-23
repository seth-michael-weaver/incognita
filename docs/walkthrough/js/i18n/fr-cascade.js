/* French: cascade (chapter 8) */
WT.L.ch.cascade = {
  num: "Chapitre 8", title: "En descendant la carte", short: "Cascade",
  lead: "Une émission est rarement la fin : le noyau laissé derrière est souvent assez chaud pour émettre à nouveau.",
  html: `
<div class="step">
  <p>Un neutron a quitté le noyau composé (à gauche), et le <b>noyau résiduel</b> qu'il laisse derrière lui (à droite) est encore chaud. La bille orange représente l'énergie. L'état fondamental du résiduel est plus haut de l'<b>énergie de séparation</b> S<sub>n</sub> du neutron, le prix à payer pour l'arracher.</p>
  <p>Chaque fois qu'un neutron sort, la bille descend de l'énergie cinétique du neutron. L'endroit où elle s'arrête est l'<b>excitation</b> du résiduel, son énergie en surplus ; les points de droite comptent les arrivées.</p>
  <div class="ctl"><label for="cs-e">Énergie du neutron</label><input id="cs-e" type="range" data-bind="E" min="1" max="30" step="0.5" value="15"><output data-show="E" data-fmt="1"></output></div>
  <p>Les neutrons émis sont en général lents, donc la plupart des chutes sont courtes. Les points bleus sont au-dessus du seuil neutron en tirets : ils peuvent s'offrir un second neutron, la réaction (n,2n). Sous environ 11 MeV, aucun n'y parvient.</p>
</div>
<div class="step">
  <h3>Une promenade sur la carte</h3>
  <p>Les flux sont des réactions qui parcourent un coin de la <b>carte des nucléides</b>, les noyaux rangés par nombre de neutrons N (horizontalement) et nombre de protons Z (verticalement). Chacune part de la case encadrée du noyau composé ; chaque case porte le nom de la réaction qui s'y termine.</p>
  <p>Un <em class="n">neutron</em> émis déplace d'une case vers la gauche, un <em class="p">proton</em> d'une case vers le bas, une <em class="a">particule alpha</em> (deux protons, deux neutrons) de deux cases en diagonale. La largeur du flux indique combien de réactions font ce pas ; la teinte et le pourcentage, où elles se terminent.</p>
  <div class="btns"><button class="btn" data-act="fire">Lancer 200 réactions</button></div>
  <p>Chaque pas coûte de 7 à 11 MeV d'énergie de séparation : même à 30 MeV, la promenade compte au plus trois ou quatre pas.</p>
</div>
<div class="step">
  <h3>De haut en bas, intervalle par intervalle</h3>
  <p>Le moteur vide chaque noyau de haut en bas, une tranche d'énergie, ou <b>intervalle</b>, à la fois. À droite, le résiduel de la première émission ; à gauche, son noyau fils, avec un neutron de moins. Les billes orange sont des réactions en attente dans chaque intervalle. Ici, les intervalles font 1 MeV ; le moteur en utilise environ 40 par noyau, dimensionnés selon l'énergie disponible.</p>
  <p>Quand le marqueur balaie un intervalle, chaque bille prend une sortie selon la compétition du chapitre 6 : un photon (<em class="g">γ</em>) la fait descendre dans un intervalle inférieur, un <em class="n">neutron</em> la fait passer dans le noyau fils, un proton ou une alpha la fait sortir de l'image. Sous tous les seuils, les photons conduisent le reste à l'état fondamental (gris). Puis le noyau fils est balayé à son tour.</p>
  <div class="ctl"><label for="cs-e3">Énergie du neutron</label><input id="cs-e3" type="range" data-bind="E" min="8" max="30" step="0.5" value="18"><output data-show="E" data-fmt="1"></output></div>
  <div class="btns"><button class="btn ghost" data-act="restart">Recommencer</button></div>
  <p>Les photons ne font que descendre, et chaque noyau est traité avant ses fils : rien n'arrive donc dans un intervalle déjà vidé.</p>
</div>
<div class="step">
  <h3>Nommer l'histoire</h3>
  <p>Une seule réaction se déroule à la fois : le marqueur saute sur la carte et chaque particule émise tombe dans le plateau. Le plateau rempli nomme la <b>voie exclusive</b>, par exemple (n,2n) ; les photons ne comptent pas. Le moteur donne à chaque voie sa propre section efficace (sa probabilité, exprimée comme une surface effective de la cible).</p>
  <div class="btns"><button class="btn ghost" data-act="next">Voie suivante</button></div>
  <p>Parcourez-les. (n,np) se déroule deux fois, d'abord neutron puis proton, ensuite l'inverse : même case, même plateau, une seule voie. Puis un deutéron fantôme (un proton et un neutron liés) atteint cette case en un seul saut : son plateau indique d, une autre voie, (n,d).</p>
</div>
<div class="step">
  <h3>Où tout se termine</h3>
  <p>Chaque case porte maintenant des étagères : encre pour l'<b>état fondamental</b>, vert (sur deux cases) pour un <b>isomère</b>, un état excité qui vit assez longtemps pour compter comme un produit distinct. La hauteur de la pile est la <b>production de résidus</b> : la quantité de chaque noyau fabriquée par les réactions.</p>
  <div class="ctl"><label for="cs-e2">Énergie du neutron</label><input id="cs-e2" type="range" data-bind="E" min="1" max="30" step="0.5" value="14"><output data-show="E" data-fmt="1"></output></div>
  <div class="btns"><button class="btn" data-act="fire">Lancer 200 réactions</button></div>
  <p>Faites glisser l'énergie : le lot suivant l'utilise et les anciennes piles s'estompent. La production s'éloigne du point de départ à mesure que davantage de particules peuvent sortir. Chaque histoire se termine sur une étagère, et une mesure par activation voit exactement ces piles : on irradie un échantillon, puis on compte les désintégrations de chaque produit.</p>
  <div class="aside">Dans le code : <code>emission/multiple.py</code> (la boucle sur les noyaux et les intervalles, la cascade γ), <code>emission/feeding.py</code> (grilles et données d'entrée pour chaque noyau de la chaîne), <code>compound/continuum.py</code> (la désexcitation d'un intervalle), <code>emission/channels.py</code> (voies exclusives, production de résidus, branches isomériques), <code>emission/binary.py</code> (le bilan de la première émission).</div>
</div>`,
};
Object.assign(WT.L.labels, {
  // reaction names on the squares (unchanged in French)
  "(n,γ)": "(n,γ)", "(n,n′)": "(n,n′)", "(n,{#}n)": "(n,{#}n)", "(n,p)": "(n,p)", "(n,np)": "(n,np)", "(n,{#}np)": "(n,{#}np)",
  "(n,{#}p)": "(n,{#}p)", "(n,n{#}p)": "(n,n{#}p)", "(n,α)": "(n,α)", "(n,nα)": "(n,nα)",
  "compound": "composé", "target": "cible",
  "N{#}": "N{#}", "N": "N", "N+{#}": "N+{#}", "Z": "Z", "Z{#}": "Z{#}",
  "neutron number →": "nombre de neutrons →",
  // scene 1
  "levels": "niveaux",
  "Sₙ {#} MeV": "Sₙ {#} MeV", "Sₙ = {#} MeV": "Sₙ = {#} MeV",
  "ground": "fondamental",
  "residual": "résiduel", "residual (one neutron fewer)": "résiduel (un neutron de moins)",
  "n threshold": "seuil n", "its neutron threshold": "son seuil neutron",
  "{#} MeV": "{#} MeV",
  "drop = neutron's kinetic energy": "chute = énergie cinétique du neutron",
  "{#} % land above the threshold: a second neutron can leave": "{#} % au-dessus du seuil : un second neutron peut sortir",
  "<{#} % land above the threshold: a second neutron can leave": "<{#} % au-dessus du seuil : un second neutron peut sortir",
  "all land below the threshold: only photons remain": "tous sous le seuil : il ne reste que des photons",
  "{#} % above threshold: (n,{#}n) possible": "{#} % au-dessus du seuil : (n,{#}n) possible",
  "<{#} % above threshold: (n,{#}n) possible": "<{#} % au-dessus du seuil : (n,{#}n) possible",
  "all below threshold: photons only": "tous sous le seuil : photons seulement",
  // scene 2
  "incoming neutron: {#} MeV": "neutron incident : {#} MeV",
  "shade and % = where reactions end": "teinte et % = où elles finissent",
  "stream width = flow · shade and % = share of reactions that end in that nucleus": "largeur = flux · teinte et % = part des réactions qui finissent dans ce noyau",
  // scene 3
  "residual (first step)": "résiduel (premier pas)",
  "daughter: n fewer": "fils : un n de moins", "daughter (one neutron fewer)": "fils (un neutron de moins)",
  "now: {#}–{#} MeV": "en cours : {#}–{#} MeV", "{#}–{#} MeV": "{#}–{#} MeV",
  "done: {#} left by proton or alpha, the rest sit on ground states": "terminé : {#} sortis par proton ou alpha, le reste est dans les états fondamentaux",
  "done: everything sits on a ground state": "terminé : tout est dans un état fondamental",
  "orange ball = reactions waiting in a bin · grey = settled on the ground state · pale bins = already emptied": "bille orange = réactions en attente · gris = dans l'état fondamental · intervalles pâles = déjà vidés",
  // scene 4
  "collected": "collecté",
  "tray: d": "plateau : d",
  "a deuteron lands on the same square, but its tray reads d: channel (n,d)": "un deutéron arrive sur la même case, mais son plateau indique d : voie (n,d)",
  "tray: n n  →  (n,{#}n)": "plateau : n n  →  (n,{#}n)",
  "tray: n  →  (n,n′)": "plateau : n  →  (n,n′)",
  "tray: p  →  (n,p)": "plateau : p  →  (n,p)",
  "tray: n p  →  (n,np)": "plateau : n p  →  (n,np)",
  "tray: n p  →  (n,np) · same square, same tray": "plateau : n p  →  (n,np) · même case, même plateau",
  "tray: a  →  (n,α)": "plateau : a  →  (n,α)",
  "tray: n n n  →  (n,{#}n)": "plateau : n n n  →  (n,{#}n)",
  "tray empty, only photons: (n,γ), capture": "plateau vide, seulement des photons : (n,γ), capture",
  "each emitted particle falls into the tray": "chaque particule émise tombe dans le plateau",
  "no particle gets out: only photons": "aucune particule ne sort : seulement des photons",
  "incoming neutron: {#} MeV · channel {#} of {#}": "neutron incident : {#} MeV · voie {#} sur {#}",
  // scene 5
  "isomer": "isomère",
  "batch of {#} at {#} MeV": "lot de {#} à {#} MeV",
  "ink shelf: ground state · green: isomer": "encre : état fondamental · vert : isomère",
  "ink shelf: ground state · green shelf: isomer · pile height = how much of that nucleus was made": "encre : fondamental · vert : isomère · hauteur = quantité produite de ce noyau",
});
