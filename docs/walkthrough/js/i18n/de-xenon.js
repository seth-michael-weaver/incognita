/* German (Deutsch): xenon (Xenonvergiftung) */
WT.L.ch.xenon = {
  num: "Lektion 13", title: "Xenonvergiftung", short: "Xenon",
  html: `
<div class="step">
  <h3>Ein Gift aus der Spaltung</h3>
  <p>Etwa 6,6 % der Spaltungen führen über Iod-135 zu Xenon-135, dem stärksten bekannten Neutronenabsorber. Es baut sich etwa zwei Tage lang auf, bis Neutronen es so schnell verbrennen und der Zerfall es so schnell entfernt, wie es entsteht. Höhere Leistung verbrennt es auch schneller, also sättigt sich der Pegel.</p>
  <div class="ctl"><label for="xe-p1">Leistung (%)</label><input id="xe-p1" type="range" data-bind="P" data-instant min="10" max="100" step="5" value="100"><output data-show="P" data-fmt="0"></output></div>
</div>
<div class="step">
  <h3>Das Xenonloch</h3>
  <p>Nach dem Abschalten hört das Verbrennen auf, aber das bereits gebildete Iod wandelt sich weiter in Xenon um. Das Gift erreicht etwa neun Stunden später sein Maximum, mehr als die Stäbe ausgleichen können, also kann der Reaktor nicht wieder anfahren; es klingt über zwei bis drei Tage ab.</p>
  <div class="ctl"><label for="xe-th">Stunden nach der Abschaltung</label><input id="xe-th" type="range" data-bind="th" data-instant min="0" max="72" step="0.5" value="9"><output data-show="th" data-fmt="1"></output></div>
</div>
<div class="step">
  <h3>Abschalten, wieder anfahren</h3>
  <p>Jetzt läuft es live, drei Stunden pro Sekunde. Schalte ab und versuche dann wieder anzufahren: Im Xenonloch wird es verweigert; später brennen die Neutronen das Xenon weg. Schon eine Leistungsänderung allein lässt das Xenon stundenlang schwanken.</p>
  <div class="ctl"><label for="xe-p3">Leistung (%)</label><input id="xe-p3" type="range" data-bind="P" data-instant min="10" max="100" step="5" value="100"><output data-show="P" data-fmt="0"></output></div>
  <div class="btns"><button class="btn" data-act="xeshut">Abschalten</button><button class="btn ghost" data-act="xerestart">Wieder anfahren</button></div>
</div>
<div class="step">
  <h3>Xenonschwingungen</h3>
  <p>In einem großen Kern sind die beiden Seiten nur lose gekoppelt. Fahre Stäbe in eine Seite ein: Weniger Fluss dort verbrennt weniger Xenon, also wandert die Leistung hinüber und schwingt dann zurück, etwa einmal am Tag. In größeren Kernen wächst die Schwingung, wenn das Betriebspersonal sie nicht dämpft.</p>
  <div class="ctl"><label for="xe-wd">Kerngröße (m)</label><input id="xe-wd" type="range" data-bind="wd" data-instant min="1.5" max="3.5" step="0.1" value="3"><output data-show="wd" data-fmt="1"></output></div>
  <div class="btns"><button class="btn" data-act="xepush">Stäbe links einfahren</button></div>
</div>`,
};

Object.assign(WT.L.labels, {
  "drag": "ziehen",
  "equilibrium {#} %": "Gleichgewicht {#} %",
  "fission → iodine{#} ({#} h) → xenon{#} ({#} h) → Cs{#}": "Spaltung → Iod{#} ({#} h) → Xenon{#} ({#} h) → Cs{#}",
  "fission → iodine{#} ({#} h) → xenon{#} ({#} h) → Cs{#}  ·  Xe{#} swallows neutrons: {#} million barns": "Spaltung → Iod{#} ({#} h) → Xenon{#} ({#} h) → Cs{#}  ·  Xe{#} schluckt Neutronen: {#} Millionen Barn",
  "illustration": "Illustration",
  "left {#} %": "links {#} %",
  "more power left": "mehr Leistung links",
  "more power right": "mehr Leistung rechts",
  "no restart": "kein Wiederanfahren",
  "peak {#} % at {#} h": "Maximum {#} % bei {#} h",
  "power": "Leistung",
  "refused: more xenon than spare reactivity": "verweigert: mehr Xenon als Reaktivitätsreserve",
  "restarted": "wieder angefahren",
  "right {#} %": "rechts {#} %",
  "running at {#} % · xenon {#} %": "läuft mit {#} % · Xenon {#} %",
  "shut down": "abgeschaltet",
  "shut down · in the pit · xenon {#} %": "abgeschaltet · im Xenonloch · Xenon {#} %",
  "shut down · restart possible · xenon {#} %": "abgeschaltet · Wiederanfahren möglich · Xenon {#} %",
  "shutdown": "Abschaltung",
  "spare reactivity": "Reaktivitätsreserve",
  "spare reactivity the rods can give": "Reaktivitätsreserve der Stäbe",
  "swing period {#} h · {#} m core: the swing dies away": "Schwingungsdauer {#} h · {#}-m-Kern: die Schwingung klingt ab",
  "swing period {#} h · {#} m core: the swing dies away slowly": "Schwingungsdauer {#} h · {#}-m-Kern: die Schwingung klingt langsam ab",
  "swing period {#} h · {#} m core: the swing grows": "Schwingungsdauer {#} h · {#}-m-Kern: die Schwingung wächst",
  "tap a side to push rods in": "tippe eine Seite an, um Stäbe einzufahren",
  "tap the core to restart": "tippe den Kern an, um wieder anzufahren",
  "tap the core to shut down": "tippe den Kern an, um abzuschalten",
  "too poisoned to restart": "zu stark vergiftet zum Wiederanfahren",
  "xenon worth (% of k)": "Xenonwert (% von k)",
  "xenon{#} + n → Xe{#}: {#} million barns": "Xenon{#} + n → Xe{#}: {#} Millionen Barn",
  "{#} % power · {#} h after start-up · xenon {#} %": "{#} % Leistung · {#} h nach dem Anfahren · Xenon {#} %",
  "{#} h": "{#} h",
  "{#} h after shutdown · xenon {#} % · cannot restart": "{#} h nach der Abschaltung · Xenon {#} % · kein Wiederanfahren möglich",
  "{#} h after shutdown · xenon {#} % · restart possible": "{#} h nach der Abschaltung · Xenon {#} % · Wiederanfahren möglich",
  "{#} m core: push the rods to start a swing": "{#}-m-Kern: Stäbe einfahren, um eine Schwingung anzustoßen",
});
