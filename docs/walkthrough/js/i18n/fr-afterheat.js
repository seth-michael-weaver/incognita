/* French: afterheat (La chaleur après l'arrêt) */
WT.L.ch.afterheat = {
  num: "Leçon 1", title: "La chaleur après l'arrêt", short: "Chaleur résiduelle",
  html: `
<div class="step">
  <h3>La chaîne s'arrête</h3>
  <p>Faire chuter les barres de commande arrête la fission des atomes en une minute environ. Mais le combustible reste incandescent : les fragments laissés par les fissions précédentes sont radioactifs, et leurs désintégrations dégagent encore de la chaleur.</p>
  <div class="btns"><button class="btn" data-act="ahDrop">Faire chuter les barres</button> <button class="btn ghost" data-act="ahUp">Redémarrer</button></div>
</div>
<div class="step">
  <h3>Elle décroît, lentement</h3>
  <p>Juste après l'arrêt, cette chaleur vaut environ 6–7 % de la pleine puissance. Au bout d'une heure, environ 1 % ; au bout d'un jour, environ un demi pour cent ; au bout d'une semaine, un quart de pour cent. De petites parts, mais d'un très grand nombre.</p>
  <div class="ctl"><label for="ah-t">Temps depuis l'arrêt</label><input id="ah-t" type="range" data-bind="lt" data-instant min="0" max="7.5" step="0.01" value="3.56"></div>
</div>
<div class="step">
  <h3>Faire circuler l'eau</h3>
  <p>Le cœur est donc refroidi aussi après l'arrêt. Des pompes font circuler l'eau le long du combustible et emportent la chaleur. Arrêtez-les et la température monte, car la chaleur n'a nulle part où aller.</p>
  <div class="btns"><button class="btn ghost" data-act="ahPump" aria-pressed="true">Pompes</button></div>
</div>
<div class="step">
  <h3>Refroidir sans pompes</h3>
  <p>L'eau chaude monte et l'eau froide descend. Une boucle qui monte jusqu'à une piscine placée plus haut que le cœur fait circuler l'eau sans aucune pompe. Plusieurs conceptions récentes comptent sur ce principe pendant des jours.</p>
  <div class="btns"><button class="btn ghost" data-act="ahPump" aria-pressed="false">Pompes</button> <button class="btn ghost" data-act="ahPass" aria-pressed="true">Boucle passive</button></div>
</div>`,
};

Object.assign(WT.L.labels, {
  "illustration": "illustration",
  // scene 1: the rods drop
  "splitting atoms": "fissions",
  "heat from splitting atoms": "chaleur des fissions",
  "decaying fragments": "désintégrations",
  "heat from decaying fragments": "chaleur des fragments qui se désintègrent",
  "full power": "pleine puissance",
  "running at full power": "en marche à pleine puissance",
  "{a} after the rods dropped": "{a} après la chute des barres",
  "{a} s": "{a} s",
  "{a} min": "{a} min",
  "{a} hours": "{a} heures",
  "{a} days": "{a} jours",
  "{a} months": "{a} mois",
  "total heat: {a} % of full power": "chaleur totale : {a} % de la pleine puissance",
  "the splitting dies away in about a minute": "les fissions s'éteignent en une minute environ",
  "the splitting dies away within about a minute": "les fissions s'éteignent en une minute environ",
  "the decay heat stays and fades slowly": "la chaleur résiduelle reste et décroît lentement",
  "the decay heat stays, and fades only slowly": "la chaleur résiduelle demeure, et ne décroît que lentement",
  // scene 2: the fading curve
  "{#} min": "{#} min",
  "{#} hour": "{#} heure",
  "{#} day": "{#} jour",
  "{#} week": "{#} semaine",
  "{#} year": "{#} an",
  "heat, share of full power": "chaleur, part de la pleine puissance",
  "heat, as a share of full power": "chaleur, en part de la pleine puissance",
  "{a} after shutdown: {b} % of full power": "{a} après l'arrêt : {b} % de la pleine puissance",
  "{#} MW core: {a} MW, like {b} kettles": "cœur de {#} MW : {a} MW, soit {b} bouilloires",
  "for a {#} MW core: {a} MW, as much as {b} electric kettles": "pour un cœur de {#} MW : {a} MW, autant que {b} bouilloires électriques",
  // scenes 3-4: cooling
  "pool, up high": "piscine en hauteur",
  "water pool, placed higher": "piscine d'eau, placée plus haut",
  "cooler": "refroidisseur",
  "heat exchanger": "échangeur de chaleur",
  "pump on": "pompe en marche",
  "pump running": "pompe en marche",
  "pump off": "pompe arrêtée",
  "pump stopped": "pompe arrêtée",
  "boiling": "ébullition",
  "the water starts to boil": "l'eau commence à bouillir",
  "normal": "normale",
  "too hot": "trop chaud",
  "temperature": "température",
  "core temperature": "température du cœur",
  "{a} after shutdown · heat {b} % of full power": "{a} après l'arrêt · chaleur {b} % de la pleine puissance",
  "too hot: cooling must be restored": "trop chaud : il faut rétablir le refroidissement",
  "too hot: the water would start to boil away; cooling must be restored": "trop chaud : l'eau commencerait à s'évaporer ; il faut rétablir le refroidissement",
  "temperature climbing": "la température monte",
  "temperature climbing: the heat has nowhere to go": "la température monte : la chaleur n'a nulle part où aller",
  "pumps carry the heat away": "les pompes évacuent la chaleur",
  "steady: the pumps carry the heat away": "stable : les pompes évacuent la chaleur",
  "steady, with no pumps": "stable, sans pompes",
  "steady: natural circulation carries the heat away": "stable : la circulation naturelle évacue la chaleur",
  "steady": "stable",
});
