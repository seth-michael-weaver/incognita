/* Dutch (Nederlands): xenon (Xenonvergiftiging) */
WT.L.ch.xenon = {
  num: "Les 13", title: "Xenonvergiftiging", short: "Xenon",
  html: `
<div class="step">
  <h3>Een gif gemaakt door splijting</h3>
  <p>Ongeveer 6,6 % van de splijtingen leidt via jodium-135 tot xenon-135: de sterkste bekende neutronenabsorbeerder. Het bouwt zich ongeveer twee dagen op, tot neutronen het verbranden en verval het verwijdert even snel als het ontstaat. Hoger vermogen verbrandt het ook sneller, dus het niveau verzadigt.</p>
  <div class="ctl"><label for="xe-p1">Vermogen (%)</label><input id="xe-p1" type="range" data-bind="P" data-instant min="10" max="100" step="5" value="100"><output data-show="P" data-fmt="0"></output></div>
</div>
<div class="step">
  <h3>De xenonput</h3>
  <p>Schakel af en het verbranden stopt, maar het al gemaakte jodium blijft in xenon overgaan. Het gif piekt ongeveer negen uur later, meer dan de staven kunnen compenseren, dus de reactor kan niet herstarten; het neemt af over twee tot drie dagen.</p>
  <div class="ctl"><label for="xe-th">Uren na afschakelen</label><input id="xe-th" type="range" data-bind="th" data-instant min="0" max="72" step="0.5" value="9"><output data-show="th" data-fmt="1"></output></div>
</div>
<div class="step">
  <h3>Afschakelen, herstarten</h3>
  <p>Nu loopt het live, drie uur per seconde. Schakel af en probeer dan te herstarten: in de put wordt het geweigerd; later branden de neutronen het xenon weg. Alleen al een vermogensverandering laat het xenon urenlang schommelen.</p>
  <div class="ctl"><label for="xe-p3">Vermogen (%)</label><input id="xe-p3" type="range" data-bind="P" data-instant min="10" max="100" step="5" value="100"><output data-show="P" data-fmt="0"></output></div>
  <div class="btns"><button class="btn" data-act="xeshut">Afschakelen</button><button class="btn ghost" data-act="xerestart">Herstarten</button></div>
</div>
<div class="step">
  <h3>Xenonoscillaties</h3>
  <p>In een grote kern zijn de twee kanten maar losjes gekoppeld. Duw staven in één kant: minder flux daar verbrandt minder xenon, dus het vermogen schuift naar de andere kant en zwaait dan terug, ongeveer eens per dag. In grotere kernen groeit de schommeling, tenzij de operators haar dempen.</p>
  <div class="ctl"><label for="xe-wd">Kerngrootte (m)</label><input id="xe-wd" type="range" data-bind="wd" data-instant min="1.5" max="3.5" step="0.1" value="3"><output data-show="wd" data-fmt="1"></output></div>
  <div class="btns"><button class="btn" data-act="xepush">Duw staven in de linkerkant</button></div>
</div>`,
};

Object.assign(WT.L.labels, {
  "drag": "sleep",
  "equilibrium {#} %": "evenwicht {#} %",
  "fission → iodine{#} ({#} h) → xenon{#} ({#} h) → Cs{#}": "splijting → jodium{#} ({#} u) → xenon{#} ({#} u) → Cs{#}",
  "fission → iodine{#} ({#} h) → xenon{#} ({#} h) → Cs{#}  ·  Xe{#} swallows neutrons: {#} million barns": "splijting → jodium{#} ({#} u) → xenon{#} ({#} u) → Cs{#}  ·  Xe{#} slokt neutronen op: {#} miljoen barn",
  "illustration": "illustratie",
  "left {#} %": "links {#} %",
  "more power left": "meer vermogen links",
  "more power right": "meer vermogen rechts",
  "no restart": "geen herstart",
  "peak {#} % at {#} h": "piek {#} % bij {#} u",
  "power": "vermogen",
  "refused: more xenon than spare reactivity": "geweigerd: meer xenon dan reservereactiviteit",
  "restarted": "herstart",
  "right {#} %": "rechts {#} %",
  "running at {#} % · xenon {#} %": "draait op {#} % · xenon {#} %",
  "shut down": "afgeschakeld",
  "shut down · in the pit · xenon {#} %": "afgeschakeld · in de put · xenon {#} %",
  "shut down · restart possible · xenon {#} %": "afgeschakeld · herstart mogelijk · xenon {#} %",
  "shutdown": "afschakeling",
  "spare reactivity": "reservereactiviteit",
  "spare reactivity the rods can give": "reservereactiviteit van de staven",
  "swing period {#} h · {#} m core: the swing dies away": "periode {#} u · kern van {#} m: de schommeling sterft uit",
  "swing period {#} h · {#} m core: the swing dies away slowly": "periode {#} u · kern van {#} m: de schommeling sterft langzaam uit",
  "swing period {#} h · {#} m core: the swing grows": "periode {#} u · kern van {#} m: de schommeling groeit",
  "tap a side to push rods in": "tik op een kant om staven in te duwen",
  "tap the core to restart": "tik op de kern om te herstarten",
  "tap the core to shut down": "tik op de kern om af te schakelen",
  "too poisoned to restart": "te vergiftigd om te herstarten",
  "xenon worth (% of k)": "xenonwaarde (% van k)",
  "xenon{#} + n → Xe{#}: {#} million barns": "xenon{#} + n → Xe{#}: {#} miljoen barn",
  "{#} % power · {#} h after start-up · xenon {#} %": "{#} % vermogen · {#} u na opstarten · xenon {#} %",
  "{#} h": "{#} u",
  "{#} h after shutdown · xenon {#} % · cannot restart": "{#} u na afschakelen · xenon {#} % · geen herstart mogelijk",
  "{#} h after shutdown · xenon {#} % · restart possible": "{#} u na afschakelen · xenon {#} % · herstart mogelijk",
  "{#} m core: push the rods to start a swing": "kern van {#} m: duw de staven om een schommeling te starten",
});
