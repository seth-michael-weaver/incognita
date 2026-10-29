/* French: tof (Chapitre 17, mesures par temps de vol) */
WT.L.ch.tof = {
  num: "Chapitre 16", title: "Mesures par temps de vol", short: "Mesurer les pics",
  html: `
<div class="step">
  <p>Le temps de vol d'un neutron donne son énergie. Une brève impulsion de neutrons de toutes énergies quitte la source et file dans un tube vide jusqu'au détecteur ; les plus rapides arrivent les premiers. La longueur <i>L</i> du tube est connue, donc chaque temps d'arrivée <i>t</i> donne la vitesse du neutron, et la vitesse donne son énergie :</p>
  <div class="formula">E = (72,3 · L / t)²   (E en eV, L en mètres, t en microsecondes)</div>
  <p>L'horloge au-dessus du tube compte le temps réel depuis l'impulsion ; le vol est dessiné environ 1400 fois plus lentement. Sous le tube, la dernière arrivée est convertie en énergie. Faites varier la longueur de vol : un tube plus long étale les mêmes énergies sur un temps plus long, de sorte que chacune se distingue plus finement.</p>
  <div class="ctl"><label for="tof-l1">Longueur de vol (m)</label><input id="tof-l1" type="range" data-bind="Lv" data-instant min="5" max="200" step="1" value="50"><output data-show="Lv" data-fmt="0"></output></div>
</div>
<div class="step">
  <p>Échantillon mince : le creux reproduit la section efficace. Un échantillon se trouve maintenant dans le faisceau. Près de 6,7 eV, ses noyaux ont une résonance et captent les neutrons (les éclairs), de sorte que moins de neutrons arrivent au moment correspondant. Le graphique compare les comptages avec et sans échantillon : la <b>transmission</b>, égale à 1 quand tous les neutrons passent.</p>
  <p>Les points sont des comptages simulés, avec leur dispersion ; la ligne continue est ce que le détecteur enregistre en moyenne ; la ligne en tirets est la forme de la section efficace elle-même. Avec un échantillon mince, le creux en copie la forme.</p>
  <div class="ctl"><label for="tof-d1">Épaisseur de l'échantillon (µm)</label><input id="tof-d1" type="range" data-bind="lgT" data-instant min="0" max="3.5" step="0.01" value="0.5"><output data-show="thk" data-fmt="0"></output></div>
</div>
<div class="step">
  <p>Échantillon épais : le creux sature. À l'énergie du pic, l'avant de l'échantillon capte tous les neutrons, si bien que le centre devient noir et le reste, aussi épais que soit l'échantillon ; le creux ne peut plus grandir qu'en s'élargissant sur ses côtés. C'est l'<b>autoprotection</b> : les couches avant protègent les couches arrière. Un échantillon épais renseigne alors davantage sur les ailes de la résonance que sur son pic.</p>
  <div class="ctl"><label for="tof-d2">Épaisseur de l'échantillon (µm)</label><input id="tof-d2" type="range" data-bind="lgT" data-instant min="0" max="3.5" step="0.01" value="3"><output data-show="thk" data-fmt="0"></output></div>
</div>
<div class="step">
  <p>Impulsions plus longues, vols plus courts : le creux s'estompe. Trois choses fixent la largeur d'un creux, toutes écrites sous le graphique : la largeur propre de la résonance ; l'agitation thermique des atomes de l'échantillon, qui brouille un peu l'énergie de chaque collision (élargissement <b>Doppler</b>) ; et le flou temporel, car une impulsion plus longue ou un tube plus court rend chaque temps d'arrivée, donc chaque énergie, moins certain.</p>
  <p>Allongez l'impulsion ou raccourcissez le tube : le creux devient plus large et moins profond, bien que la part de neutrons qu'il retire reste à peu près la même.</p>
  <div class="ctl"><label for="tof-p1">Largeur de l'impulsion (µs)</label><input id="tof-p1" type="range" data-bind="lgDt" data-instant min="-2" max="1" step="0.01" value="0.3"><output data-show="dt" data-fmt="2"></output></div>
  <div class="ctl"><label for="tof-l2">Longueur de vol (m)</label><input id="tof-l2" type="range" data-bind="Lv" data-instant min="5" max="200" step="1" value="20"><output data-show="Lv" data-fmt="0"></output></div>
</div>
<div class="step">
  <p>INCOGNITA procède à l'envers : à partir de comptages mesurés comme ceux-ci, il cherche quelle résonance, soumise à cette même expérience (épaisseur, chaleur, flou temporel), les reproduit. Ici l'ajustement part d'une hypothèse dont la largeur neutronique Γ<sub>n</sub> (la force avec laquelle le niveau retient les neutrons) est près de quatre fois trop grande (la courbe bleue), et la modifie pas à pas jusqu'à ce que la courbe passe par les points.</p>
  <p>L'affichage montre l'hypothèse courante et le <b>désaccord</b> : environ 1 signifie que la courbe est aussi proche des points que le permet leur dispersion de comptage. Changez l'expérience et l'ajustement recommence, à partir de nouveaux comptages, et aboutit près de la même largeur ; là où il ne peut pas bien rejoindre les points, le désaccord le dit.</p>
  <div class="ctl"><label for="tof-l3">Longueur de vol (m)</label><input id="tof-l3" type="range" data-bind="Lv" data-instant min="5" max="200" step="1" value="50"><output data-show="Lv" data-fmt="0"></output></div>
  <div class="ctl"><label for="tof-d3">Épaisseur de l'échantillon (µm)</label><input id="tof-d3" type="range" data-bind="lgT" data-instant min="0" max="3.5" step="0.01" value="1.5"><output data-show="thk" data-fmt="0"></output></div>
  <div class="ctl"><label for="tof-p2">Largeur de l'impulsion (µs)</label><input id="tof-p2" type="range" data-bind="lgDt" data-instant min="-2" max="1" step="0.01" value="-1"><output data-show="dt" data-fmt="2"></output></div>
</div>`,
};
