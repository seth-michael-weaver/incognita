/* French: critical (Chapitre 20, criticité et pilotage du réacteur) */
WT.L.ch.critical = {
  num: "Chapitre 20", title: "Criticité et pilotage du réacteur", short: "Criticité",
  html: `
<div class="step">
  <h3>Le facteur de multiplication</h3>
  <p>Chaque fission libère quelques neutrons ; certains provoquent les fissions suivantes, les autres sont perdus. Le <b>facteur de multiplication</b> <i>k</i> est le nombre de nouvelles fissions auquel mène une fission : à chaque génération, les neutrons sont multipliés par <i>k</i>. Au-dessus de 1, la chaîne croît ; en dessous de 1, elle s'éteint.</p>
  <div class="ctl"><label for="cri-k">Multiplication k</label><input id="cri-k" type="range" data-bind="k" data-instant min="0.95" max="1.05" step="0.05" value="1.05"><output data-show="k" data-fmt="2"></output></div>
</div>
<div class="step">
  <h3>Les neutrons retardés</h3>
  <p>Une petite part des neutrons (0,65 %) arrive avec des secondes de retard, issue de fragments de fission qui se désintègrent d'abord. Ces retardataires imposent le rythme, si bien que la croissance passe d'un clin d'œil à des minutes. Le tracé tourne à une vitesse ×10.</p>
  <div class="ctl"><label for="cri-k2">Multiplication k</label><input id="cri-k2" type="range" data-bind="kd" data-instant min="0.998" max="1.002" step="0.0005" value="1.001"><output data-show="kd" data-fmt="4"></output></div>
  <div class="btns"><button class="btn ghost" data-act="delayed" aria-pressed="true">Neutrons retardés</button></div>
</div>
<div class="step">
  <h3>La criticité</h3>
  <p>Une expérience critique : déplacez les barres de commande jusqu'à ce que la puissance reste plate. Dans ce réglage, <i>k</i> vaut exactement 1, et cette position des barres est la mesure. Trouvez-la : l'affichage donne <i>k</i> avec cinq décimales.</p>
  <div class="ctl"><label for="cri-rod">Barres de commande enfoncées (%)</label><input id="cri-rod" type="range" data-bind="ins" data-instant min="35" max="75" step="1" value="45"><output data-show="ins" data-fmt="0"></output></div>
</div>`,
};
/* attributes referenced in the English chapter script (for the structure check): data-act="delayed" data-act="delayed" */
