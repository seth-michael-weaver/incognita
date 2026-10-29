/* French: neutrons (Chapitre 5, pourquoi les réacteurs fonctionnent aux neutrons) */
WT.L.ch.neutrons = {
  num: "Chapitre 5", title: "Pourquoi les réacteurs fonctionnent aux neutrons", short: "Pourquoi les neutrons",
  html: `
<div class="step">
  <p>Un proton est positif, tout comme les 82 protons du noyau. Les charges de même signe se repoussent : le proton est donc repoussé, et la poussée croît vite à mesure qu'il se rapproche (la flèche). Un proton lent s'arrête avant et fait demi-tour sans toucher le noyau. Ce n'est qu'au-dessus d'environ 13 MeV qu'il franchit la poussée ; juste en dessous, il lui arrive de passer quand même (<b>effet tunnel</b>). Le petit graphique montre la même poussée comme une colline d'énergie.</p>
  <div class="ctl"><label for="wn-e1">Énergie du proton (MeV)</label><input id="wn-e1" type="range" data-bind="Ep" data-instant min="0.5" max="20" step="0.1" value="6"><output data-show="Ep" data-fmt="1"></output></div>
</div>
<div class="step">
  <p>Un neutron n'a pas de charge : il entre à n'importe quelle vitesse. Rien ne le repousse, il n'y a donc pas de colline à gravir ; il lui suffit d'atteindre le noyau, et l'interaction forte l'attire alors à l'intérieur.</p>
  <div class="ctl"><label for="wn-e2">Énergie du neutron (lent → rapide)</label><input id="wn-e2" type="range" data-bind="lgEn" data-instant min="-1.6" max="7.3" step="0.01" value="-1.6"><output id="wn-en-out"></output></div>
  <p>Le curseur va de 0,025 eV, la vitesse d'un neutron à température ambiante, jusqu'à 20 MeV, près d'un milliard de fois plus. Jusqu'en bas, le neutron entre toujours.</p>
</div>
<div class="step">
  <p>Même les neutrons lents peuvent donc fissionner l'uranium dans un réacteur. Un noyau d'uranium-235 qui en avale un devient de l'uranium-236 avec un peu d'énergie en plus, assez pour osciller, s'étirer en un col et se casser en deux. Les deux morceaux s'écartent avec environ 200 MeV, et les deux ou trois nouveaux neutrons qu'ils projettent peuvent fissionner les noyaux suivants : c'est une réaction en chaîne.</p>
</div>`,
};
