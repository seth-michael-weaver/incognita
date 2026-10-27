/* French: fission (chapter 9) */
WT.L.ch.fission = {
  num: "Chapitre 12", title: "Se casser en deux", short: "Fission",
  lead: "Les noyaux les plus lourds disposent d'une sortie qui manque aux plus légers : au lieu d'expulser une particule, le noyau tout entier se déchire en deux. C'est la fission.",
  html: `
<div class="step">
  <p>Un noyau lourd se comporte comme une goutte de liquide chargé. La tension superficielle (flèches grises) la maintient ronde ; les protons, tous chargés positivement, la poussent à se séparer (flèches rouges). Pour l'uranium, les deux s'équilibrent presque.</p>
  <div class="ctl"><label for="fis-d">Étirer la goutte</label><input id="fis-d" type="range" data-bind="def" min="0" max="1" step="0.01" value="0"><output data-show="def" data-fmt="2"></output></div>
  <p>Faites glisser pour l'étirer et observez le point sur la petite courbe d'énergie en dessous. L'étirer ajoute de la surface, ce qui coûte de l'énergie, mais éloigne les charges, ce qui en libère. Passé le sommet de la courbe, la charge l'emporte : un col se forme et les deux moitiés s'écartent avec environ 200 MeV.</p>
</div>
<div class="step">
  <h3>Le paysage des formes</h3>
  <p>La courbe donne l'énergie de chaque forme, de ronde (à gauche) à cassée (à droite). Une goutte liquide lisse ne donne qu'une colline, mais les nucléons remplissent les niveaux d'énergie par groupes, appelés <b>couches</b>, et dans les éléments les plus lourds cela y creuse un puits : une <b>barrière à double bosse</b>, où le noyau peut s'attarder sous une forme étirée.</p>
  <p>Le moteur ne suppose pas cette courbe : il la lit point par point dans un calcul microscopique de l'énergie à chaque déformation (degré d'étirement).</p>
</div>
<div class="step">
  <h3>Traverser la colline par effet tunnel</h3>
  <p>La bille est le noyau excité dans la première vallée, à l'énergie d'excitation de la ligne orange en tirets, sous le sommet à 6 MeV. Classiquement, elle ne peut jamais passer ; la mécanique quantique lui permet de traverser par <b>effet tunnel</b> la zone plus sombre, interdite, avec une probabilité <i>T</i> qui chute exponentiellement à mesure que cette zone s'épaissit.</p>
  <div class="ctl"><label for="fis-e">Énergie d'excitation</label><input id="fis-e" type="range" data-bind="E" min="3" max="8" step="0.05" value="5"><output data-show="E" data-fmt="2"></output></div>
  <p>Augmentez l'énergie et regardez <i>T</i> grimper à mesure que la zone interdite s'amincit. Le raccourci des manuels (Hill–Wheeler) traite le sommet comme une parabole (en tirets bleus). Le moteur suit la forme réelle, plus large vers le bas : loin sous le sommet, sa probabilité est donc plus faible. <i>K</i> mesure la quantité de colline à franchir.</p>
  <div class="formula">T = 1 / (1 + e<sup>2K</sup>),  K = ∫ √(2μ(V−E)) dβ / ħ</div>
</div>
<div class="step">
  <h3>Des portes au sommet</h3>
  <p>Les portes au sommet sont les <b>états de transition</b>, les états quantiques du noyau étiré au-dessus de la barrière. Chacun a un spin et une parité (0⁺, 2⁻, …) et agit comme une porte ; sa fente éclairée montre à quel point elle est ouverte. Un noyau ne passe que par les portes de même spin et de même parité que lui, et chacune s'ouvre progressivement à mesure que l'énergie dépasse sa hauteur.</p>
  <div class="ctl"><label for="fis-e2">Énergie d'excitation</label><input id="fis-e2" type="range" data-bind="E" min="3" max="8" step="0.05" value="5"><output data-show="E" data-fmt="2"></output></div>
  <div class="btns"><button class="btn ghost" data-act="jpAll">Tout spin</button><button class="btn ghost" data-act="jp0">Composé 0⁺</button><button class="btn ghost" data-act="jp1">Composé 1⁻</button></div>
  <p>Choisissez un spin et une parité : seules les portes correspondantes comptent, et l'ouverture totale baisse. Plus haut, les portes s'entassent en un <b>continuum</b>, et le moteur les compte par leur densité, comme il le fait pour les niveaux ordinaires.</p>
</div>
<div class="step">
  <h3>Deux collines en série</h3>
  <p>Voici maintenant les deux collines, chacune avec sa porte (le cercle ; sa partie remplie indique son ouverture). Les noyaux arrivent par la gauche ; ceux qui franchissent la première colline sont piégés dans le puits, rebondissant entre les portes jusqu'à sortir d'un côté ou de l'autre. Les probabilités se combinent comme des résistances en série : c'est surtout la colline la plus difficile qui décide.</p>
  <div class="ctl"><label for="fis-b">Hauteur de la colline extérieure</label><input id="fis-b" type="range" data-bind="Bb" min="3.5" max="7.5" step="0.05" value="5.6"><output data-show="Bb" data-fmt="2"></output></div>
  <div class="formula">1/T = 1/T<sub>A</sub> + 1/T<sub>B</sub></div>
  <p>Relevez la colline extérieure et regardez le flux vers la fission s'étrangler, aussi ouverte que soit la porte intérieure.</p>
</div>
<div class="step">
  <h3>Plus d'une chance</h3>
  <p>L'uranium 238 absorbe le neutron et devient de l'uranium 239 avec une excitation <i>E</i>* (ligne en tirets). S'il ne se casse pas, il peut émettre un neutron à la place ; la ligne descend, et l'uranium 238 qui reste, encore chaud, tente sa propre barrière : c'est la fission de <b>seconde chance</b>, (n,n′f). Les piles recueillent la façon dont chaque noyau a fini.</p>
  <div class="ctl"><label for="fis-en">Énergie du neutron</label><input id="fis-en" type="range" data-bind="En" min="0" max="25" step="0.1" value="7"><output data-show="En" data-fmt="1"></output></div>
  <p>Augmentez l'énergie et les tentatives suivantes commencent à réussir ; une troisième chance s'ouvre vers 12 MeV. Chaque nouvelle chance apparaît comme une marche dans la <b>section efficace de fission</b> mesurée, la probabilité que le noyau se casse. Le moteur calcule à quelle fréquence il se casse, pas en quels fragments.</p>
  <div class="aside">Dans le code : <code>fission/wkb.py</code> (le chemin d'énergie de déformation et les intégrales WKB), <code>fission/barriers.py</code> (Hill–Wheeler, états de transition, densité de niveaux à la barrière), <code>fission/transmission.py</code> (bosses en série, T<sub>fis</sub> par spin et parité), <code>fission/chain.py</code> (barrières pour chaque noyau de la cascade).</div>
</div>`,
};
Object.assign(WT.L.labels, {
  // drop
  "surface tension pulls it round": "la tension superficielle l'arrondit",
  "the protons push it apart": "les protons l'écartent",
  "a charged drop, nearly round": "une goutte chargée, presque ronde",
  "stretched: more surface, charge further apart": "étirée : plus de surface, charges plus éloignées",
  "a neck forms": "un col se forme",
  "two fragments, carrying about {#} MeV": "deux fragments, emportant environ {#} MeV",
  "energy of the drop": "énergie de la goutte",
  // landscape
  "ground state": "état fondamental", "inner barrier": "barrière intérieure", "second well": "second puits",
  "outer barrier": "barrière extérieure", "split (scission)": "cassée (scission)", "one smooth hill": "une seule colline lisse",
  "shell effects carving the second well": "les effets de couche creusent le second puits",
  "round → stretched → necked → split": "ronde → étirée → avec col → cassée",
  "stretch (deformation) →": "étirement (déformation) →",
  // tunnel
  "forbidden zone": "zone interdite",
  "excitation {#} MeV": "excitation {#} MeV",
  "hilltop {#} MeV": "sommet {#} MeV",
  "parabola fit": "ajustement parabolique",
  "passes over the top": "passe par-dessus le sommet",
  // gates
  "continuum: a density": "continuum : une densité",
  "continuum of gates: counted as a density": "continuum de portes : compté comme une densité",
  "gates: transition states": "portes : états de transition",
  "E = {#} MeV": "E = {#} MeV",
  "all gates: total opening {#}": "toutes les portes : ouverture totale {#}",
  "all gates: total opening {#} + {#} from the continuum": "toutes les portes : ouverture totale {#} + {#} du continuum",
  "{#}⁺ gates only: total opening {#}": "portes {#}⁺ seules : ouverture totale {#}",
  "{#}⁺ gates only: total opening {#} + {#} from the continuum": "portes {#}⁺ seules : ouverture totale {#} + {#} du continuum",
  "{#}⁻ gates only: total opening {#}": "portes {#}⁻ seules : ouverture totale {#}",
  "{#}⁻ gates only: total opening {#} + {#} from the continuum": "portes {#}⁻ seules : ouverture totale {#} + {#} du continuum",
  // series
  "nuclei arriving →": "noyaux qui arrivent →",
  "trapped in the well": "piégés dans le puits",
  "fission": "fission",
  "so far: {#} through, {#} turned back": "jusqu'ici : {#} passés, {#} repartis",
  // chance
  "²³⁹U*  E* = {#} MeV": "²³⁹U*  E* = {#} MeV", "²³⁸U*  E* = {#} MeV": "²³⁸U*  E* = {#} MeV", "²³⁷U*  E* = {#} MeV": "²³⁷U*  E* = {#} MeV",
  "↑ E* above the picture": "↑ E* au-dessus de l'image",
  "fission!": "fission !",
  "emits a neutron, cools, tries again": "émet un neutron, refroidit, réessaie",
  "too cool to split: a photon, no fission": "trop froid pour se casser : un photon, pas de fission",
  "attempt {#}: barrier {#} % open": "tentative {#} : barrière ouverte à {#} %",
  "{#}st chance (n,f)": "{#}re chance (n,f)", "{#}nd chance (n,n′f)": "{#}e chance (n,n′f)", "{#}rd chance (n,{#}nf)": "{#}e chance (n,{#}nf)",
  "{#}st (n,f)": "{#}re (n,f)", "{#}nd (n,n′f)": "{#}e (n,n′f)", "{#}rd (n,{#}nf)": "{#}e (n,{#}nf)",
  "no fission": "pas de fission",
});
// labels carrying a transmission T, printed either as 0.12 or as 3.4·10⁻5 (two number shapes)
(function () {
  const L = WT.L.labels, F = ["{#}", "{#}·{#}⁻{#}"];
  for (const a of F) {
    L[`inner gate T ≈ ${a}`] = `porte intérieure T ≈ ${a}`;
    L[`outer gate T ≈ ${a}`] = `porte extérieure T ≈ ${a}`;
    L[`both hills: T ≈ ${a}, {#} % of what arrives gets through`] = `les deux collines : T ≈ ${a}, {#} % de ce qui arrive passe`;
    for (const b of F) {
      L[`T ≈ ${a} real shape · ${b} parabola`] = `T ≈ ${a} forme réelle · ${b} parabole`;
      L[`chance to tunnel T ≈ ${a} on the real shape, ${b} on the parabola`] = `probabilité de tunnel T ≈ ${a} avec la forme réelle, ${b} avec la parabole`;
    }
  }
})();
