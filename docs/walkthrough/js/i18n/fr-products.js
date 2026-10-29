/* French: products (Chapitre 14, produits de fission et chaleur résiduelle) */
WT.L.ch.products = {
  num: "Chapitre 14", title: "Produits de fission et chaleur résiduelle", short: "Produits de fission",
  html: `
<div class="step">
  <p>Les morceaux sont inégaux : un léger, un lourd. Le graphique montre, pour chaque masse de fragment A (protons plus neutrons), la part des fissions qui le produisent. Deux bosses : les morceaux légers vers A = 95, les lourds vers 139. Une cassure en deux parts égales, vers A = 117, est une centaine de fois plus rare.</p>
  <p>Chaque ligne en tirets est dix fois plus haute que celle du dessous, si bien que les masses rares restent visibles. Touchez une barre ou faites glisser le curseur : en dessous figurent les deux morceaux de cette cassure. Leurs masses s'additionnent à 234 et non à 236 (uranium-235 plus le neutron), car environ 2,4 neutrons s'envolent aussi.</p>
  <div class="ctl"><label for="pr-a">A du fragment léger</label><input id="pr-a" type="range" data-bind="pick" data-instant min="70" max="117" step="1" value="95"><output data-show="pick" data-fmt="0"></output></div>
</div>
<div class="step">
  <p>Leurs désintégrations continuent de chauffer le combustible après l'arrêt. Les fragments sont radioactifs : ils se désintègrent l'un après l'autre, et chaque désintégration libère de la chaleur, que la réaction en chaîne tourne ou non.</p>
  <div class="ctl"><label for="pr-t">Temps après l'arrêt</label><input id="pr-t" type="range" data-bind="lgt" data-instant min="0" max="8.5" step="0.01" value="0"><output id="pr-tout">1 s</output></div>
  <p>Faites varier le temps. Une seconde après l'arrêt du réacteur, les désintégrations donnent encore environ 6 % de la pleine puissance ; après un jour, environ un demi pour cent ; après un an, quelques centièmes de pour cent, soit encore presque un mégawatt dans un grand réacteur. C'est pourquoi le combustible usé est gardé des années dans des piscines de refroidissement. La courbe est la règle empirique de Way–Wigner : une formule simple pour l'ensemble des désintégrations des fragments, après un an de fonctionnement. Les deux échelles sautent d'un facteur dix à chaque repère.</p>
</div>`,
};
