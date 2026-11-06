/* German (Deutsch): afterheat (Wärme nach der Abschaltung) */
WT.L.ch.afterheat = {
  num: "Lektion 11", title: "Wärme nach der Abschaltung", short: "Nachwärme",
  html: `
<div class="step">
  <h3>Die Kette stoppt</h3>
  <p>Das Einfallen der Steuerstäbe beendet die Spaltung der Atome innerhalb etwa einer Minute. Doch der Brennstoff glüht weiter: Die Bruchstücke früherer Spaltungen sind radioaktiv, und ihre Zerfälle geben noch Wärme ab.</p>
  <div class="btns"><button class="btn" data-act="ahDrop">Stäbe einfallen lassen</button> <button class="btn ghost" data-act="ahUp">Neu starten</button></div>
</div>
<div class="step">
  <h3>Sie klingt langsam ab</h3>
  <p>Direkt nach der Abschaltung beträgt diese Wärme etwa 6–7 % der vollen Leistung. Nach einer Stunde sind es etwa 1 %, nach einem Tag etwa ein halbes Prozent, nach einer Woche ein Viertel. Kleine Anteile, aber von einer sehr großen Zahl.</p>
  <div class="ctl"><label for="ah-t">Zeit seit der Abschaltung</label><input id="ah-t" type="range" data-bind="lt" data-instant min="0" max="7.5" step="0.01" value="3.56"></div>
</div>
<div class="step">
  <h3>Das Wasser in Bewegung halten</h3>
  <p>Deshalb wird der Kern auch nach der Abschaltung gekühlt. Pumpen halten das Wasser am Brennstoff vorbei in Fluss und tragen die Wärme ab. Schalte sie ab, und die Temperatur steigt, weil die Wärme nirgendwohin kann.</p>
  <div class="btns"><button class="btn ghost" data-act="ahPump" aria-pressed="true">Pumpen</button></div>
</div>
<div class="step">
  <h3>Kühlung ohne Pumpen</h3>
  <p>Heißes Wasser steigt auf, kaltes sinkt ab. Ein Kreislauf hinauf zu einem Becken, das höher als der Kern liegt, hält das Wasser ganz ohne Pumpen in Bewegung. Mehrere neuere Konzepte verlassen sich tagelang darauf.</p>
  <div class="btns"><button class="btn ghost" data-act="ahPump" aria-pressed="false">Pumpen</button> <button class="btn ghost" data-act="ahPass" aria-pressed="true">Passiver Kreislauf</button></div>
</div>`,
};

Object.assign(WT.L.labels, {
  "3000 MW core: {a} MW, like {b} kettles": "3000-MW-Kern: {a} MW, wie {b} Wasserkocher",
  "for a 3000 MW core: {a} MW, as much as {b} electric kettles": "bei einem 3000-MW-Kern: {a} MW, so viel wie {b} Wasserkocher",
  "cooler": "Kühler",
  "core temperature": "Kerntemperatur",
  "decaying fragments": "zerfallende Bruchstücke",
  "full power": "volle Leistung",
  "running at full power": "läuft mit voller Leistung",
  "heat exchanger": "Wärmetauscher",
  "heat from decaying fragments": "Wärme aus zerfallenden Bruchstücken",
  "heat from splitting atoms": "Wärme aus Atomspaltung",
  "heat, as a share of full power": "Wärme, als Anteil der vollen Leistung",
  "heat, share of full power": "Wärme, Anteil der vollen Leistung",
  "illustration": "Illustration",
  "normal": "normal",
  "pool, up high": "Becken, hoch gelegen",
  "pump off": "Pumpe aus",
  "pump on": "Pumpe an",
  "pump running": "Pumpe läuft",
  "pump stopped": "Pumpe gestoppt",
  "pumps carry the heat away": "Pumpen tragen die Wärme ab",
  "splitting atoms": "Atomspaltung",
  "steady": "stabil",
  "steady, with no pumps": "stabil, ohne Pumpen",
  "steady: natural circulation carries the heat away": "stabil: Naturumlauf trägt die Wärme ab",
  "steady: the pumps carry the heat away": "stabil: die Pumpen tragen die Wärme ab",
  "temperature": "Temperatur",
  "temperature climbing": "Temperatur steigt",
  "temperature climbing: the heat has nowhere to go": "Temperatur steigt: die Wärme kann nirgendwohin",
  "the splitting dies away in about a minute": "die Spaltung klingt in etwa einer Minute ab",
  "the splitting dies away within about a minute": "die Spaltung klingt innerhalb etwa einer Minute ab",
  "the decay heat stays and fades slowly": "die Nachwärme bleibt und klingt langsam ab",
  "the decay heat stays, and fades only slowly": "die Nachwärme bleibt und klingt nur langsam ab",
  "boiling": "Sieden",
  "the water starts to boil": "das Wasser beginnt zu sieden",
  "too hot": "zu heiß",
  "too hot: cooling must be restored": "zu heiß: die Kühlung muss wiederhergestellt werden",
  "too hot: the water would start to boil away; cooling must be restored": "zu heiß: das Wasser würde verdampfen; die Kühlung muss wiederhergestellt werden",
  "total heat: {a} % of full power": "Gesamtwärme: {a} % der vollen Leistung",
  "water pool, placed higher": "Wasserbecken, höher gelegen",
  "{#} day": "{#} Tag",
  "{#} hour": "{#} Stunde",
  "{#} min": "{#} min",
  "{#} week": "{#} Woche",
  "{#} year": "{#} Jahr",
  "{a} after shutdown · heat {b} % of full power": "{a} nach der Abschaltung · Wärme {b} % der vollen Leistung",
  "{a} after shutdown: {b} % of full power": "{a} nach der Abschaltung: {b} % der vollen Leistung",
  "{a} after the rods dropped": "{a} nach dem Einfallen der Stäbe",
  "{a} days": "{a} Tage",
  "{a} hours": "{a} Stunden",
  "{a} min": "{a} min",
  "{a} months": "{a} Monate",
  "{a} s": "{a} s",
});
