/* German (Deutsch): burnup (Abbrand des Brennstoffs) */
WT.L.ch.burnup = {
  num: "Lektion 10", title: "Abbrand des Brennstoffs", short: "Abbrand",
  html: `
<div class="step">
  <h3>Eine Tablette im Lauf ihres Lebens</h3>
  <p>Hier sind tausend Atome aus einer frischen Brennstofftablette: 45 sind Uran-235, der Rest Uran-238. Lass den Reaktor laufen und sieh zu, wie sich das Uran-235 spaltet, während neue Atome erscheinen. Der <b>Abbrand</b> zählt die entnommene Energie in Gigawatt-Tagen pro Tonne Uran; Wasserreaktoren hören bei etwa 45–55 auf.</p>
  <div class="ctl"><label for="bu-d1">Volllasttage</label><input id="bu-d1" type="range" data-bind="d" data-instant min="0" max="1400" step="10" value="400"><output data-show="d" data-fmt="0"></output></div>
</div>
<div class="step">
  <h3>Plutonium macht mit</h3>
  <p>Uran-238 fängt Neutronen ein und wird zu Plutonium-239, das sich ebenfalls spaltet. Spät im Leben finden mehr als die Hälfte der Spaltungen im Plutonium statt; über das ganze Leben stammt etwa ein Drittel der Energie daraus.</p>
  <div class="ctl"><label for="bu-d2">Volllasttage</label><input id="bu-d2" type="range" data-bind="d" data-instant min="0" max="1400" step="10" value="1000"><output data-show="d" data-fmt="0"></output></div>
</div>
<div class="step">
  <h3>Gifte sammeln sich an</h3>
  <p>Jede Spaltung hinterlässt zwei Spaltprodukte, und einige davon schlucken Neutronen. Mit weniger Uran-235 und mehr Gift sinkt <i>k</i><sub>∞</sub> (neue Spaltungen pro Spaltung in einem unendlichen Gitter dieses Brennstoffs) allmählich, bis der Brennstoff allein keine Kette mehr aufrechterhalten kann.</p>
  <div class="ctl"><label for="bu-d3">Volllasttage</label><input id="bu-d3" type="range" data-bind="d" data-instant min="0" max="1400" step="10" value="700"><output data-show="d" data-fmt="0"></output></div>
</div>
<div class="step">
  <h3>Bor und Nachladungen</h3>
  <p>Ein Kern mischt frischen, mittelalten und alten Brennstoff. Frischer Brennstoff hat zu viel Reaktivität, also schluckt im Kühlwasser gelöstes Bor den Überschuss und wird langsam verdünnt. Erreicht es null, kommt das älteste Drittel heraus und frischer Brennstoff hinein.</p>
  <div class="ctl"><label for="bu-m">Volllastmonate</label><input id="bu-m" type="range" data-bind="m" data-instant min="0" max="54" step="0.5" value="8"><output data-show="m" data-fmt="1"></output></div>
</div>`,
};

Object.assign(WT.L.labels, {
  "GWd/t →": "GWd/t →",
  "boron (ppm)": "Bor (ppm)",
  "boron in the water (ppm)": "Bor im Wasser (ppm)",
  "burnup (GWd/t) →": "Abbrand (GWd/t) →",
  "can't keep a chain going alone": "hält allein keine Kette aufrecht",
  "cycle {a} months · fuel leaves at {b} GWd/t": "Zyklus {a} Monate · Brennstoff geht bei {b} GWd/t heraus",
  "each dot: one atom in a thousand": "jeder Punkt: ein Atom von tausend",
  "each dot: {#} atom in {#}": "jeder Punkt: {#} Atom von {#}",
  "energy so far": "Energie bisher",
  "fission products": "Spaltprodukte",
  "fission products (pairs)": "Spaltprodukte (Paare)",
  "fission products catch {a} % of neutrons": "Spaltprodukte fangen {a} % der Neutronen ein",
  "fissions": "Spaltungen",
  "fissions now": "Spaltungen jetzt",
  "fresh": "frisch",
  "illustrative model": "Modell zur Veranschaulichung",
  "k = {#}": "k = {#}",
  "k∞ = {a}": "k∞ = {a}",
  "k∞ reaches {#}": "k∞ erreicht {#}",
  "months at full power →": "Volllastmonate →",
  "months →": "Monate →",
  "one cycle old": "einen Zyklus alt",
  "other Pu": "übriges Pu",
  "other plutonium": "übriges Plutonium",
  "plutonium": "Plutonium",
  "plutonium's share": "Anteil des Plutoniums",
  "plutonium{#}": "Plutonium{#}",
  "reload": "Nachladung",
  "split": "gespalten",
  "this fuel alone can no longer keep a chain going": "dieser Brennstoff allein kann keine Kette mehr aufrechterhalten",
  "two cycles old": "zwei Zyklen alt",
  "typical discharge": "typischer Entladeabbrand",
  "typical discharge {#}–{#}": "typischer Entladeabbrand {#}–{#}",
  "uranium{#}": "Uran{#}",
  "uranium{#}: the remaining ~{#}–{#} %": "Uran{#}: die übrigen ~{#}–{#} %",
  "{#} cycle": "{#} Zyklus",
  "{#} cycles": "{#} Zyklen",
  "{a} days · burnup {b} GWd/t": "{a} Tage · Abbrand {b} GWd/t",
  "{a} in 1000": "{a} von 1000",
  "{a} ppm": "{a} ppm",
});
