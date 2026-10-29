/* French: landscape (Chapitre 4, le paysage des noyaux) */
WT.L.ch.landscape = {
  num: "Chapitre 4", title: "Le paysage des noyaux", short: "Paysage",
  lead: "Tous les noyaux que l'on ait jamais fabriqués, sur une seule carte : 3 338 à ce jour, et seuls 252 durent éternellement.",
  html: `
<div class="step">
  <h3>La carte des nucléides</h3>
  <p>Chaque petit carré est un noyau qui a réellement été observé lors d'une expérience : les neutrons se comptent vers la droite, les protons vers le haut. Les carrés pâles ont été observés, mais leur masse n'a pas encore été pesée, seulement estimée. Les carrés <b>sombres</b> sont les 252 qui ne se désintègrent jamais. Les autres se défont, les orange en un clin d'œil, les bleus seulement après des années. La ligne <em style="font-style:normal;color:var(--proton);font-weight:600">rouge</em> est l'élément choisi avec le curseur : tous ses isotopes connus.</p>
  <div class="ctl"><label for="ls-z">Regarder l'élément (protons Z)</label><input id="ls-z" type="range" data-bind="zSel" data-instant min="1" max="110" step="1" value="26"><output data-show="zSel" data-fmt="0"></output></div>
  <p class="ctl-result" id="ls-z-out" aria-live="polite"></p>
</div>
<div class="step">
  <h3>L'énergie de liaison sur la carte</h3>
  <p>Maintenant, chaque carré est coloré selon son <b>énergie de liaison par nucléon</b>, c'est-à-dire la force avec laquelle chaque neutron ou proton est retenu (chapitre 3). Les noyaux stables se trouvent le long d'une crête de forte liaison ; si l'on s'en écarte, avec trop de neutrons ou trop de protons, la liaison diminue. Le plus fortement lié de tous est le nickel-62. Les fines lignes marquent les <b>nombres magiques</b> (8, 20, 28, 50, 82, 126), pour lesquels les noyaux sont particulièrement bien liés.</p>
</div>
<div class="step">
  <h3>La désintégration bêta vers la stabilité</h3>
  <p>Les noyaux ayant le même nombre total de nucléons (le même <b>nombre de masse</b> A) se trouvent sur une diagonale de la carte, montrée en <em style="font-style:normal;color:var(--proton);font-weight:600">rouge</em>. Partez d'un excès de neutrons, comme les fragments d'un noyau d'uranium cassé. Dans la <b>désintégration bêta</b>, un neutron se change en proton : le noyau avance donc d'une place le long de sa ligne vers le milieu, plus fortement lié, encore et encore, jusqu'à atteindre la crête et s'arrêter. Le petit graphique montre la même chaîne comme une vallée dans laquelle le noyau dévale. Essayez A = 137 : la chaîne passe par le césium-137, le produit à longue durée de vie des accidents de réacteur.</p>
  <div class="ctl"><label for="ls-a">Nombre de masse A</label><input id="ls-a" type="range" data-bind="aSel" data-instant min="8" max="250" step="1" value="137"><output data-show="aSel" data-fmt="0"></output></div>
  <p class="ctl-result" id="ls-a-out" aria-live="polite"></p>
</div>
<div class="step">
  <h3>La couverture d'INCOGNITA</h3>
  <p>La même carte, colorée selon ce que notre bibliothèque contient pour chaque noyau. <em style="font-style:normal;color:var(--fission);font-weight:600">Vert</em> : évalué à partir de ses résonances mesurées. Les autres ont un fichier de modèle construit par le seul moteur : <b>sombre</b> pour les noyaux stables ou de longue durée de vie (niveau A), <em style="font-style:normal;color:var(--accent);font-weight:600">bleu</em> pour plus d'un jour (niveau B), <em style="font-style:normal;color:var(--warm);font-weight:600">orange</em> pour les durées de vie plus courtes (niveau C). Les gris ne sont pas dans la bibliothèque (surtout les noyaux les plus légers, et quelques-uns que le moteur ne sait pas traiter).</p>
</div>`,
};

Object.assign(WT.L.labels, {
  "neutrons N →": "neutrons N →",
  "protons Z ↑": "protons Z ↑",
  "Fe: all its isotopes": "Fe : tous ses isotopes",
  "stable": "stable",
  "lives years": "vit des années",
  "gone in a blink": "disparu en un clin d'œil",
  "red: Fe (your pick)": "rouge : Fe (votre choix)",
  "nickel{#}: most tightly bound": "nickel{#} : le plus lié",
  "held most tightly": "le plus lié",
  "middle": "intermédiaire",
  "held least": "le moins lié",
  "red: the A = {#} chain": "rouge : la chaîne A = {#}",
  "A = {#}: deeper = more tightly bound": "A = {#} : plus bas = plus lié",
  "protons Z →": "protons Z →",
  "measured resonances": "résonances mesurées",
  "tier A": "niveau A",
  "tier B": "niveau B",
  "tier C": "niveau C",
  "not in library": "hors bibliothèque",
});
