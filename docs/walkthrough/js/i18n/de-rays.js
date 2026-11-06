/* German (Deutsch): rays (Alpha, Beta, Gamma und Neutronen) */
WT.L.ch.rays = {
  num: "Lektion 2", title: "Alpha, Beta, Gamma und Neutronen", short: "Strahlung",
  html: `
<div class="step">
  <h3>Vier Arten von Strahlung</h3>
  <p><em class="a">Alpha</em> ist ein schwerer Klumpen aus zwei Protonen und zwei Neutronen. <b>Beta</b> ist ein schnelles Elektron. <em class="g">Gamma</em> ist Licht, viel zu energiereich, um es zu sehen. <em class="n">Neutronen</em> tragen überhaupt keine Ladung. Jede Art wird von etwas anderem gestoppt.</p>
</div>
<div class="step">
  <h3>Papier und Aluminium</h3>
  <p>Alphateilchen sind groß und geladen, also prallen sie sofort mit Atomen zusammen: Ein Blatt Papier stoppt sie. Beta-Elektronen kommen weiter, aber ein paar Millimeter Aluminium stoppen auch sie.</p>
  <div class="btns"><button class="btn ghost" data-act="sh_paper" aria-pressed="true">Papier</button><button class="btn ghost" data-act="sh_al" aria-pressed="false">Aluminium</button></div>
</div>
<div class="step">
  <h3>Gammastrahlen: halbiert, nie null</h3>
  <p>Gammastrahlen haben keine Ladung und fliegen meist an Atomen vorbei. Jeder Zentimeter Blei gibt jedem einzelnen dieselbe Chance, eingefangen zu werden, also halbiert jede Schicht, was übrig ist. Der Strahl wird schwächer, erreicht aber nie ganz null.</p>
  <div class="ctl"><label for="ry-pb">Blei (cm)</label><input id="ry-pb" type="range" data-bind="pb" data-instant min="0" max="5" step="0.1" value="1"><output data-show="pb" data-fmt="1"></output></div>
</div>
<div class="step">
  <h3>Neutronen: Blei reicht nicht</h3>
  <p>Ein Neutron, das von einem schweren Bleikern abprallt, ist wie ein Tischtennisball, der auf eine Bowlingkugel trifft: Es behält seine Geschwindigkeit. Wasserstoff im Wasser wiegt so viel wie ein Neutron, also bremst jeder Stoß es ab, bis es langsam genug ist, um verschluckt zu werden.</p>
  <div class="btns"><button class="btn ghost" data-act="nm_pb" aria-pressed="true">Blei</button><button class="btn ghost" data-act="nm_water" aria-pressed="false">Wasser</button></div>
  <div class="ctl"><label for="ry-nx">Dicke (cm)</label><input id="ry-nx" type="range" data-bind="nx" data-instant min="0" max="60" step="1" value="30"><output data-show="nx" data-fmt="0"></output></div>
</div>
<div class="step">
  <h3>Baue eine Abschirmung</h3>
  <p>Staple Schichten, bis alle vier Strahlen gestoppt sind. Gammastrahlen fallen nie auf genau null, nur auf einen winzigen Anteil.</p>
  <div class="btns"><button class="btn ghost" data-act="add_paper">+ Papier</button><button class="btn ghost" data-act="add_al">+ Aluminium</button><button class="btn ghost" data-act="add_pb">+ Blei</button><button class="btn ghost" data-act="add_water">+ Wasser</button><button class="btn" data-act="clear">Leeren</button></div>
</div>`,
};

Object.assign(WT.L.labels, {
  "Al {#} mm": "Al {#} mm",
  "all four beams stopped": "alle vier Strahlen gestoppt",
  "all four stopped": "alle vier gestoppt",
  "all through": "alles durch",
  "alpha": "Alpha",
  "aluminium {#} mm": "Aluminium {#} mm",
  "beta": "Beta",
  "bright = fast neutron · red = hydrogen nucleus knocked away · green flash = swallowed": "hell = schnelles Neutron · rot = weggestoßener Wasserstoffkern · grüner Blitz = verschluckt",
  "bright = fast · dim = slowed": "hell = schnell · matt = abgebremst",
  "cm of lead": "cm Blei",
  "counted: {#} of {#}": "gezählt: {#} von {#}",
  "drag ↔": "ziehen ↔",
  "each source fires a steady beam": "jede Quelle sendet einen stetigen Strahl",
  "flash = stopped": "Blitz = gestoppt",
  "flash = stopped inside the shield": "Blitz = in der Abschirmung gestoppt",
  "four beams": "vier Strahlen",
  "gamma": "Gamma",
  "gamma rays (caesium{#})": "Gammastrahlen (Cäsium{#})",
  "gets through: {#} % · halved every {#} mm of lead": "kommt durch: {#} % · halbiert alle {#} mm Blei",
  "gets through: {#} in {#} · halved every {#} mm of lead": "kommt durch: {#} von {#} · halbiert alle {#} mm Blei",
  "gets through: {#} in {#} million · halved every {#} mm of lead": "kommt durch: {#} von {#} Millionen · halbiert alle {#} mm Blei",
  "got through {#} % · bounced back {#} % · slowed and caught {#} %": "durchgekommen {#} % · zurückgeprallt {#} % · abgebremst und eingefangen {#} %",
  "lead {#} cm": "Blei {#} cm",
  "neutron": "Neutron",
  "no shield": "keine Abschirmung",
  "not to scale": "nicht maßstabsgetreu",
  "paper": "Papier",
  "share still going": "Anteil noch unterwegs",
  "simplified model": "vereinfachtes Modell",
  "stopped": "gestoppt",
  "through {#} % · back {#} % · caught {#} %": "durch {#} % · zurück {#} % · eingefangen {#} %",
  "through: all · halved every {#} mm": "durch: alles · halbiert alle {#} mm",
  "through: {#} % · halved every {#} mm": "durch: {#} % · halbiert alle {#} mm",
  "through: {#} in {#} · halved every {#} mm": "durch: {#} von {#} · halbiert alle {#} mm",
  "water {#} cm": "Wasser {#} cm",
  "{#} % through": "{#} % durch",
  "{#} in {#}": "{#} von {#}",
  "{#} in {#} million": "{#} von {#} Millionen",
  "{#} in a billion": "{#} von einer Milliarde",
});
