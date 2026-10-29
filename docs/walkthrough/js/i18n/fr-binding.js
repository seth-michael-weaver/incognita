/* French: binding (Chapitre 3, pourquoi les noyaux tiennent ensemble) */
WT.L.ch.binding = {
  num: "Chapitre 3", title: "Pourquoi les noyaux tiennent ensemble", short: "Liaison",
  html: `
<div class="step">
  <p>Plus on est haut sur la courbe, plus le noyau est fortement lié. Chaque point correspond à un nombre de masse A (le nombre de protons plus de neutrons), et sa hauteur est l'énergie qu'il faudrait, par nucléon, pour démonter complètement ce noyau. Faites varier A et lisez le marqueur : le milieu de la courbe, autour du fer et du nickel, en est le sommet.</p>
  <div class="ctl"><label for="bi-a">Nombre de masse A</label><input id="bi-a" type="range" data-bind="pick" data-instant min="2" max="260" step="1" value="56"><output data-show="pick" data-fmt="0"></output></div>
</div>
<div class="step">
  <p>Cassez l'uranium : les deux morceaux se trouvent plus haut sur la courbe que l'uranium dont ils viennent, si bien que les mêmes nucléons finissent liés plus fortement et que la différence sort sous forme d'énergie. Choisissez le fragment le plus léger ; le plus lourd est le reste des 236 nucléons.</p>
  <div class="ctl"><label for="bi-f">A du fragment léger</label><input id="bi-f" type="range" data-bind="frag" data-instant min="70" max="118" step="1" value="95"><output data-show="frag" data-fmt="0"></output></div>
  <p class="ctl-result" id="bi-split-out" aria-live="polite"></p>
  <p>Quelle que soit la cassure, cela fait environ 200 MeV : des dizaines de millions de fois les quelques électronvolts que donne la combustion d'une molécule de combustible.</p>
</div>
<div class="step">
  <p>Réunissez deux noyaux légers en un seul. Si le nouveau noyau se trouve plus haut sur la courbe, de l'énergie est libérée. Au-delà du sommet, la réunion coûte de l'énergie au contraire.</p>
  <div class="ctl"><label for="bi-u">A de chaque noyau léger</label><input id="bi-u" type="range" data-bind="fuse" data-instant min="2" max="60" step="1" value="2"><output data-show="fuse" data-fmt="0"></output></div>
  <p class="ctl-result" id="bi-fuse-out" aria-live="polite"></p>
</div>`,
};

Object.assign(WT.L.labels, {
  "mass number A →": "nombre de masse A →",
  "binding energy per nucleon (MeV)": "énergie de liaison par nucléon (MeV)",
  "Ni{#}: most tightly bound": "Ni{#} : le plus lié",
  "measured masses (AME{#})": "masses mesurées (AME{#})",
  "Fe{#}: {#} MeV per nucleon · {#} MeV in all": "Fe{#} : {#} MeV par nucléon · {#} MeV au total",
});
