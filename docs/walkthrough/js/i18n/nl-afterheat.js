/* Dutch (Nederlands): afterheat (Warmte na het afschakelen) */
WT.L.ch.afterheat = {
  num: "Les 11", title: "Warmte na het afschakelen", short: "Nawarmte",
  html: `
<div class="step">
  <h3>De keten stopt</h3>
  <p>Het laten vallen van de regelstaven stopt het splijten van atomen binnen ongeveer een minuut. Maar de brandstof blijft gloeien: de brokstukken van eerdere splijtingen zijn radioactief, en hun verval geeft nog steeds warmte af.</p>
  <div class="btns"><button class="btn" data-act="ahDrop">Laat de staven vallen</button> <button class="btn ghost" data-act="ahUp">Herstarten</button></div>
</div>
<div class="step">
  <h3>Het zakt langzaam weg</h3>
  <p>Vlak na het afschakelen is deze warmte ongeveer 6–7 % van het volle vermogen. Na een uur is het ongeveer 1 %, na een dag ongeveer een half procent, na een week een kwart. Kleine aandelen, maar van een heel groot getal.</p>
  <div class="ctl"><label for="ah-t">Tijd sinds afschakelen</label><input id="ah-t" type="range" data-bind="lt" data-instant min="0" max="7.5" step="0.01" value="3.56"></div>
</div>
<div class="step">
  <h3>Houd het water in beweging</h3>
  <p>Daarom wordt de kern ook na het afschakelen gekoeld. Pompen houden water langs de brandstof stromen en voeren de warmte af. Zet ze uit en de temperatuur stijgt, omdat de warmte nergens heen kan.</p>
  <div class="btns"><button class="btn ghost" data-act="ahPump" aria-pressed="true">Pompen</button></div>
</div>
<div class="step">
  <h3>Koelen zonder pompen</h3>
  <p>Heet water stijgt en koel water zakt. Een kringloop naar een bassin dat hoger ligt dan de kern houdt het water helemaal zonder pompen in beweging. Verscheidene nieuwere ontwerpen vertrouwen hier dagenlang op.</p>
  <div class="btns"><button class="btn ghost" data-act="ahPump" aria-pressed="false">Pompen</button> <button class="btn ghost" data-act="ahPass" aria-pressed="true">Passieve kringloop</button></div>
</div>`,
};

Object.assign(WT.L.labels, {
  "3000 MW core: {a} MW, like {b} kettles": "kern van 3000 MW: {a} MW, als {b} waterkokers",
  "for a 3000 MW core: {a} MW, as much as {b} electric kettles": "voor een kern van 3000 MW: {a} MW, evenveel als {b} waterkokers",
  "cooler": "koeler",
  "core temperature": "kerntemperatuur",
  "decaying fragments": "vervallende brokstukken",
  "full power": "vol vermogen",
  "running at full power": "draait op vol vermogen",
  "heat exchanger": "warmtewisselaar",
  "heat from decaying fragments": "warmte van vervallende brokstukken",
  "heat from splitting atoms": "warmte van splijtende atomen",
  "heat, as a share of full power": "warmte, als aandeel van vol vermogen",
  "heat, share of full power": "warmte, aandeel van vol vermogen",
  "illustration": "illustratie",
  "normal": "normaal",
  "pool, up high": "bassin, hoog",
  "pump off": "pomp uit",
  "pump on": "pomp aan",
  "pump running": "pomp draait",
  "pump stopped": "pomp gestopt",
  "pumps carry the heat away": "pompen voeren de warmte af",
  "splitting atoms": "splijtende atomen",
  "steady": "stabiel",
  "steady, with no pumps": "stabiel, zonder pompen",
  "steady: natural circulation carries the heat away": "stabiel: natuurlijke circulatie voert de warmte af",
  "steady: the pumps carry the heat away": "stabiel: de pompen voeren de warmte af",
  "temperature": "temperatuur",
  "temperature climbing": "temperatuur stijgt",
  "temperature climbing: the heat has nowhere to go": "temperatuur stijgt: de warmte kan nergens heen",
  "the splitting dies away in about a minute": "het splijten sterft uit in ongeveer een minuut",
  "the splitting dies away within about a minute": "het splijten sterft uit binnen ongeveer een minuut",
  "the decay heat stays and fades slowly": "de vervalwarmte blijft en neemt langzaam af",
  "the decay heat stays, and fades only slowly": "de vervalwarmte blijft, en neemt maar langzaam af",
  "boiling": "koken",
  "the water starts to boil": "het water begint te koken",
  "too hot": "te heet",
  "too hot: cooling must be restored": "te heet: de koeling moet hersteld worden",
  "too hot: the water would start to boil away; cooling must be restored": "te heet: het water zou gaan wegkoken; de koeling moet hersteld worden",
  "total heat: {a} % of full power": "totale warmte: {a} % van vol vermogen",
  "water pool, placed higher": "waterbassin, hoger geplaatst",
  "{#} day": "{#} dag",
  "{#} hour": "{#} uur",
  "{#} min": "{#} min",
  "{#} week": "{#} week",
  "{#} year": "{#} jaar",
  "{a} after shutdown · heat {b} % of full power": "{a} na afschakelen · warmte {b} % van vol vermogen",
  "{a} after shutdown: {b} % of full power": "{a} na afschakelen: {b} % van vol vermogen",
  "{a} after the rods dropped": "{a} nadat de staven vielen",
  "{a} days": "{a} dagen",
  "{a} hours": "{a} uur",
  "{a} min": "{a} min",
  "{a} months": "{a} maanden",
  "{a} s": "{a} s",
});
