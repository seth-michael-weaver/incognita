/* Danish: afterheat (Varme efter nedlukning) */
WT.L.ch.afterheat = {
  num: "Lektion 11", title: "Varme efter nedlukning", short: "Efterhenfaldsvarme",
  html: `
<div class="step">
  <h3>Kæden stopper</h3>
  <p>Når kontrolstavene falder ind, stopper spaltningen af atomer inden for omkring et minut. Men brændslet bliver ved med at gløde: fragmenterne fra tidligere spaltninger er radioaktive, og deres henfald afgiver stadig varme.</p>
  <div class="btns"><button class="btn" data-act="ahDrop">Slip stavene</button> <button class="btn ghost" data-act="ahUp">Genstart</button></div>
</div>
<div class="step">
  <h3>Den aftager langsomt</h3>
  <p>Lige efter nedlukningen er denne varme omkring 6–7 % af fuld effekt. Efter en time er den omkring 1 %, efter en dag omkring en halv procent, efter en uge en fjerdedel. Små andele, men af et meget stort tal.</p>
  <div class="ctl"><label for="ah-t">Tid siden nedlukning</label><input id="ah-t" type="range" data-bind="lt" data-instant min="0" max="7.5" step="0.01" value="3.56"></div>
</div>
<div class="step">
  <h3>Hold vandet i bevægelse</h3>
  <p>Derfor køles kernen også efter nedlukning. Pumper holder vandet strømmende forbi brændslet og fører varmen væk. Sluk dem, og temperaturen stiger, fordi varmen ikke har nogen steder at gøre af sig.</p>
  <div class="btns"><button class="btn ghost" data-act="ahPump" aria-pressed="true">Pumper</button></div>
</div>
<div class="step">
  <h3>Køling uden pumper</h3>
  <p>Varmt vand stiger op, og koldt vand synker. Et kredsløb op til et bassin, der ligger højere end kernen, holder vandet i bevægelse helt uden pumper. Flere nyere design forlader sig på dette i dagevis.</p>
  <div class="btns"><button class="btn ghost" data-act="ahPump" aria-pressed="false">Pumper</button> <button class="btn ghost" data-act="ahPass" aria-pressed="true">Passivt kredsløb</button></div>
</div>`,
};

Object.assign(WT.L.labels, {
  "3000 MW core: {a} MW, like {b} kettles": "3000 MW-kerne: {a} MW, som {b} elkedler",
  "for a 3000 MW core: {a} MW, as much as {b} electric kettles": "for en kerne på 3000 MW: {a} MW, lige så meget som {b} elkedler",
  "cooler": "køler",
  "core temperature": "kernetemperatur",
  "decaying fragments": "henfaldende fragmenter",
  "full power": "fuld effekt",
  "running at full power": "kører ved fuld effekt",
  "heat exchanger": "varmeveksler",
  "heat from decaying fragments": "varme fra henfaldende fragmenter",
  "heat from splitting atoms": "varme fra spaltning af atomer",
  "heat, as a share of full power": "varme, som andel af fuld effekt",
  "heat, share of full power": "varme, andel af fuld effekt",
  "illustration": "illustration",
  "normal": "normal",
  "pool, up high": "bassin, højt oppe",
  "pump off": "pumpe slukket",
  "pump on": "pumpe tændt",
  "pump running": "pumpe kører",
  "pump stopped": "pumpe stoppet",
  "pumps carry the heat away": "pumper fører varmen væk",
  "splitting atoms": "spaltning af atomer",
  "steady": "stabil",
  "steady, with no pumps": "stabil, uden pumper",
  "steady: natural circulation carries the heat away": "stabil: naturlig cirkulation fører varmen væk",
  "steady: the pumps carry the heat away": "stabil: pumperne fører varmen væk",
  "temperature": "temperatur",
  "temperature climbing": "temperaturen stiger",
  "temperature climbing: the heat has nowhere to go": "temperaturen stiger: varmen kan ingen steder komme hen",
  "the splitting dies away in about a minute": "spaltningen dør ud på omkring et minut",
  "the splitting dies away within about a minute": "spaltningen dør ud inden for omkring et minut",
  "the decay heat stays and fades slowly": "efterhenfaldsvarmen bliver og aftager langsomt",
  "the decay heat stays, and fades only slowly": "efterhenfaldsvarmen bliver og aftager kun langsomt",
  "boiling": "kogning",
  "the water starts to boil": "vandet begynder at koge",
  "too hot": "for varm",
  "too hot: cooling must be restored": "for varm: kølingen skal genoprettes",
  "too hot: the water would start to boil away; cooling must be restored": "for varm: vandet ville begynde at koge væk; kølingen skal genoprettes",
  "total heat: {a} % of full power": "samlet varme: {a} % af fuld effekt",
  "water pool, placed higher": "vandbassin, placeret højere",
  "{#} day": "{#} dag",
  "{#} hour": "{#} time",
  "{#} min": "{#} min",
  "{#} week": "{#} uge",
  "{#} year": "{#} år",
  "{a} after shutdown · heat {b} % of full power": "{a} efter nedlukning · varme {b} % af fuld effekt",
  "{a} after shutdown: {b} % of full power": "{a} efter nedlukning: {b} % af fuld effekt",
  "{a} after the rods dropped": "{a} efter at stavene faldt ind",
  "{a} days": "{a} dage",
  "{a} hours": "{a} timer",
  "{a} min": "{a} min",
  "{a} months": "{a} måneder",
  "{a} s": "{a} s",
});
