/* French: xsec (Chapitre 2, section efficace) */
WT.L.ch.xsec = {
  num: "Chapitre 2", title: "Qu'est-ce qu'une section efficace ?", short: "Section efficace",
  html: `
<div class="step">
  <p>Chaque disque est la surface cible d'un noyau : sa <b>section efficace</b>, notée σ (sigma). L'image montre, vue de dessus, une fine feuille de noyaux sur laquelle des neutrons tombent en pluie, en des points aléatoires. Un neutron qui atterrit dans un disque réagit avec ce noyau (un éclair orange) ; celui qui atterrit entre les disques traverse sans rien faire (il s'estompe simplement).</p>
  <p>La part qui réagit est donc simplement la part de la feuille que couvrent les disques. Le petit carré noir est l'unité de surface, un <b>barn</b>, 10⁻²⁴ cm² : la vraie face d'un noyau fait environ un barn.</p>
  <div class="ctl"><label for="xs-e1">Énergie du neutron (eV)</label><input id="xs-e1" type="range" data-bind="lgE" data-instant min="-2.3" max="2" step="0.01" value="2"><output data-show="Eshow" data-fmt="2"></output></div>
</div>
<div class="step">
  <p>Les neutrons plus lents voient de plus grandes cibles. Le disque n'est pas la taille réelle du noyau : c'est la taille apparente du noyau pour un neutron de cette énergie, et un neutron lent s'attarde plus longtemps près du noyau, donc il a plus de chances d'être capturé. Pour la capture, σ croît ainsi comme 1/vitesse.</p>
  <p>La courbe sous la feuille est σ sur toutes les énergies (les deux échelles sont logarithmiques) ; le point orange marque l'énergie choisie. Descendez vers les neutrons les plus lents et regardez les disques grandir et la part des réactions grimper.</p>
  <div class="ctl"><label for="xs-e2">Énergie du neutron (eV)</label><input id="xs-e2" type="range" data-bind="lgE" data-instant min="-2.3" max="2" step="0.01" value="-1.6"><output data-show="Eshow" data-fmt="2"></output></div>
</div>
<div class="step">
  <p>À une résonance, la cible gonfle. À 7 eV, le neutron et le noyau ont exactement l'énergie de l'un des niveaux propres du noyau, si bien que le neutron est absorbé bien plus facilement : le disque grandit d'un facteur cinquante environ en surface, ici jusqu'à environ 400 barns.</p>
  <p>Écartez-vous un peu de 7 eV et le disque rétrécit aussitôt : le pic de la courbe est étroit. Les vrais noyaux ont beaucoup de pics de ce genre ; le chapitre 1 en a montré le code-barres.</p>
  <div class="ctl"><label for="xs-e3">Énergie du neutron (eV)</label><input id="xs-e3" type="range" data-bind="lgE" data-instant min="-2.3" max="2" step="0.005" value="0.845"><output data-show="Eshow" data-fmt="2"></output></div>
</div>`,
};

Object.assign(WT.L.labels, {
  "this square: {#} barn = {#}⁻²⁴ cm²": "ce carré : {#} barn = {#}⁻²⁴ cm²",
  "σ: the target area at each energy": "σ : la surface cible à chaque énergie",
  "σ ≈ {#} b · reacted {#} % · passed through {#} %": "σ ≈ {#} b · ont réagi {#} % · ont traversé {#} %",
  "each falling dot is a neutron: an orange flash means it hit a disc and reacted, a fading dot passed through": "chaque point qui tombe est un neutron : un éclair orange signifie qu'il a touché un disque et réagi, un point qui s'estompe a traversé",
});
