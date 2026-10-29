/* French: slowing (Chapitre 18, modération des neutrons) */
WT.L.ch.slowing = {
  num: "Chapitre 18", title: "Modération des neutrons", short: "Ralentissement",
  html: `
<div class="step">
  <p>Chaque rebond sur l'hydrogène coûte environ la moitié de l'énergie. Un neutron de fission part à 2 MeV et rebondit dans l'eau. Un noyau d'hydrogène pèse autant que le neutron : comme des boules de billard, chaque rebond lui retire en moyenne la moitié de l'énergie du neutron.</p>
  <p>Le graphique trace l'énergie du neutron après chaque rebond ; chaque graduation sur le côté représente mille fois moins d'énergie. Perdre la même part à chaque fois donne une descente en ligne droite, la ligne en tirets. Après environ 18 rebonds, le neutron atteint l'énergie <b>thermique</b>, 0,025 eV, où l'eau tiède le relance aussi souvent qu'elle le ralentit. L'oxygène est 16 fois plus lourd : chaque rebond n'enlève que peu, et il en faut plus d'une centaine.</p>
  <div class="btns"><button class="btn ghost" data-act="tgtH" aria-pressed="true">Hydrogène</button><button class="btn ghost" data-act="tgtO" aria-pressed="false">Oxygène</button><button class="btn" data-act="again">Tirer à nouveau</button></div>
</div>
<div class="step">
  <p>En dessous d'environ 1 eV, ce sont les liaisons de la molécule qui façonnent chaque rebond. Chaque hydrogène est attaché à son oxygène (les lignes brillantes). Un neutron lent ne frappe plus un hydrogène libre : il frappe une molécule entière, 18 fois plus lourde, si bien qu'un rebond simple ne prend presque rien.</p>
  <p>Il peut aussi faire tourner ou vibrer la molécule, mais seulement en cédant une quantité d'énergie fixe à la fois, 0,06, 0,2 ou 0,45 eV (les éclairs brillants). Les molécules tièdes rendent parfois une telle quantité. Sur le graphique, la bande ombrée sous 1 eV est la zone où cela compte. Désactivez la liaison pour comparer avec l'hydrogène libre.</p>
  <div class="btns"><button class="btn ghost" data-act="bind" aria-pressed="true">Liaison chimique</button><button class="btn" data-act="again">Tirer à nouveau</button></div>
</div>
<div class="step">
  <p>Un code de calcul a besoin de tout cela sous forme de table : la <b>loi de diffusion</b>, la carte. En abscisse : la force du choc, α (la poussée transmise à la molécule ; faible pour un effleurement, grande pour un choc frontal). En ordonnée : l'énergie que le neutron gagne (vers le haut) ou perd (vers le bas), β, comptée en unités de l'énergie thermique de l'eau, 0,025 eV. Brillant signifie probable, pâle signifie rare.</p>
  <p>Le contour est ce qu'un neutron de l'énergie choisie peut atteindre : il ne peut pas perdre plus qu'il n'a, et chaque variation d'énergie n'autorise qu'un domaine de chocs. Faites varier l'énergie et le contour grandit ou rétrécit. Sans liaison, la carte est celle d'un gaz d'hydrogène libre, une seule crête brillante le long de la ligne de recul en tirets ; avec la liaison, la molécule ajoute des bandes brillantes, ses quantités d'énergie fixes. INCOGNITA calcule ses propres lois pour l'eau et le béryllium : <a href="https://github.com/seth-michael-weaver/incognita/tree/main/library/tsl-v0.1" style="white-space:nowrap">tsl-v0.1</a>.</p>
  <div class="ctl"><label for="slo-e">Énergie du neutron (eV)</label><input id="slo-e" type="range" data-bind="lgE" data-instant min="-2.3" max="0" step="0.01" value="-1"><output data-show="Eshow" data-fmt="3"></output></div>
  <div class="btns"><button class="btn ghost" data-act="bind" aria-pressed="true">Liaison chimique</button></div>
</div>`,
};
/* attributes referenced in the English chapter script (for the structure check): data-act="${act}" */

Object.assign(WT.L.labels, {
  "water · neutron hits hydrogen": "eau · le neutron heurte l'hydrogène",
  "thermal · kT ≈ {#} eV": "thermique · kT ≈ {#} eV",
  "{#} meV": "{#} meV",
  "collisions →": "collisions →",
  "energy": "énergie",
  "typical bounce: energy × {#} (theory × {#}) · {#} bounces to thermal": "rebond typique : énergie × {#} (théorie × {#}) · {#} rebonds jusqu'au thermique",
  "typical: the average step along the dashed line (energy shares multiply, so the average is taken on this scale)": "typique : le pas moyen le long de la ligne en tirets (les parts d'énergie se multiplient, la moyenne est donc prise sur cette échelle)",
  "bright line: a bond holding H to its O": "ligne brillante : une liaison qui tient H à son O",
  "bright flash: the neutron left a fixed amount of energy in the molecule": "éclair : le neutron a laissé une quantité d'énergie fixe dans la molécule",
  "below {#} eV: the bonds shape each bounce": "sous {#} eV : les liaisons façonnent chaque rebond",
  "free-atom recoil": "recul d'atome libre",
  "α: how hard the knock (momentum handed over) →": "α : force du choc (quantité de mouvement transmise) →",
  "β: the neutron's energy change, in units of kT = {#} eV": "β : variation d'énergie du neutron, en unités de kT = {#} eV",
  "gain ↑": "gain ↑",
  "loss ↓": "perte ↓",
  "outline: reachable from {#} eV": "contour : accessible depuis {#} eV",
  "rare → likely": "rare → probable",
  "scattering law S(α,β) · hydrogen bound in water": "loi de diffusion S(α,β) · hydrogène lié dans l'eau",
  "stripes: energy lost to the molecule in fixed amounts": "bandes : énergie cédée à la molécule par quantités fixes",
});
