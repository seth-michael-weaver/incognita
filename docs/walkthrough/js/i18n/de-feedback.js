/* German (Deutsch): feedback (Reaktorstabilität und Rückkopplung) */
WT.L.ch.feedback = {
  num: "Lektion 12", title: "Reaktorstabilität und Rückkopplung", short: "Rückkopplung",
  html: `
<div class="step">
  <h3>Ein Kreislauf: Leistung, Wärme, Reaktivität</h3>
  <p>Mehr Leistung heizt Brennstoff und Wasser auf, und ihre Temperaturen ändern die Reaktivität <i>ρ</i>, die die Leistung bestimmt. Füge einen Reaktivitätssprung hinzu und sieh zu, wie das Signal den Kreis durchläuft. Mit negativen Koeffizienten drückt es zurück.</p>
  <div class="ctl"><label for="fb-r">Reaktivitätssprung (pcm)</label><input id="fb-r" type="range" data-bind="rs" data-instant min="50" max="300" step="10" value="200"><output data-show="rs" data-fmt="0"></output></div>
  <div class="btns"><button class="btn" data-act="fbIns">Einbringen</button> <button class="btn ghost" data-act="fbRes">Zurücksetzen</button></div>
</div>
<div class="step">
  <h3>Doppler: die schnelle Bremse</h3>
  <p>Heißerer Brennstoff fängt mehr Neutronen in Uran-238 ohne Spaltung ein (<a href="#doppler">Doppler-Verbreiterung</a>). Brennstoff erwärmt sich innerhalb von Sekunden, also wirkt diese Bremse zuerst, und in Wasserreaktoren ist sie immer negativ. Hier ist sie die einzige Rückkopplung.</p>
  <div class="ctl"><label for="fb-d">Doppler-Koeffizient (pcm/K)</label><input id="fb-d" type="range" data-bind="aD" data-instant min="-5" max="-1" step="0.1" value="-2.5"><output data-show="aD" data-fmt="1"></output></div>
  <div class="btns"><button class="btn" data-act="fbIns">Einbringen</button> <button class="btn ghost" data-act="fbRes">Zurücksetzen</button></div>
</div>
<div class="step">
  <h3>Der Moderator kommt hinzu</h3>
  <p>Wärmeres Wasser ist weniger dicht und bremst Neutronen daher schlechter. In einem Druckwasserreaktor bei normaler Borkonzentration macht das auch den Moderatorkoeffizienten negativ: eine zweite, langsamere Bremse, und die Leistung pendelt sich niedriger ein.</p>
  <div class="ctl"><label for="fb-m">Moderatorkoeffizient (pcm/K)</label><input id="fb-m" type="range" data-bind="aM" data-instant min="-60" max="0" step="1" value="-30"><output data-show="aM" data-fmt="0"></output></div>
  <div class="btns"><button class="btn" data-act="fbIns">Einbringen</button> <button class="btn ghost" data-act="fbRes">Zurücksetzen</button></div>
</div>
<div class="step">
  <h3>Wenn die Rückkopplung positiv ist</h3>
  <p>Ist der Kühlmittelterm positiv und überwiegt den Doppler-Effekt, bedeutet mehr Leistung mehr Reaktivität, und die Leistung läuft davon. Wasserreaktoren werden mit negativen Koeffizienten ausgelegt; manche Bauarten, etwa der RBMK bei niedriger Leistung, konnten einen positiven Dampfblasenkoeffizienten haben.</p>
  <div class="ctl"><label for="fb-c">Kühlmittelkoeffizient (pcm/K)</label><input id="fb-c" type="range" data-bind="aM" data-instant min="-60" max="150" step="5" value="150"><output data-show="aM" data-fmt="0"></output></div>
  <div class="btns"><button class="btn" data-act="fbIns">Einbringen</button> <button class="btn ghost" data-act="fbRes">Zurücksetzen</button></div>
</div>`,
};

Object.assign(WT.L.labels, {
  "+{a} pcm": "+{a} pcm",
  "C dT/dt = P − h (T − Tc)": "C dT/dt = P − h (T − Tc)",
  "Doppler α_D = {a} pcm/K": "Doppler α_D = {a} pcm/K",
  "P {#} %": "P {#} %",
  "chain": "Kette",
  "chain reaction": "Kettenreaktion",
  "coolant α_C = {a} pcm/K": "Kühlmittel α_C = {a} pcm/K",
  "fuel +{#} K": "Brennstoff +{#} K",
  "fuel {#} K": "Brennstoff {#} K",
  "fuel ΔT +{#} K": "Brennstoff ΔT +{#} K",
  "fuel ΔT {#} K": "Brennstoff ΔT {#} K",
  "heat": "Wärme",
  "heats water": "heizt Wasser",
  "illustrative model": "Modell zur Veranschaulichung",
  "inserted ρ_ext = {a}": "eingebracht ρ_ext = {a}",
  "last {#} s →": "letzte {#} s →",
  "last {#} seconds →": "letzte {#} Sekunden →",
  "moderator α_M = {a} pcm/K": "Moderator α_M = {a} pcm/K",
  "power": "Leistung",
  "power coefficient +{a} pcm per 100 % power: runs away": "Leistungskoeffizient +{a} pcm pro 100 % Leistung: läuft davon",
  "power coefficient +{a} pcm per 100 %: runs away": "Leistungskoeffizient +{a} pcm pro 100 %: läuft davon",
  "power coefficient {a} pcm per 100 % power: self-stabilising": "Leistungskoeffizient {a} pcm pro 100 % Leistung: selbststabilisierend",
  "power coefficient {a} pcm per 100 %: settles": "Leistungskoeffizient {a} pcm pro 100 %: pendelt sich ein",
  "power ran away · protection would shut it down": "Leistung lief davon · der Schutz würde abschalten",
  "power ran away · in a real plant the protection system would shut it down": "Leistung lief davon · in einer echten Anlage würde das Reaktorschutzsystem abschalten",
  "steady at {#} % · press Insert": "stabil bei {#} % · drücke Einbringen",
  "steady at {#} % power · press Insert to add reactivity": "stabil bei {#} % Leistung · drücke Einbringen, um Reaktivität hinzuzufügen",
  "water +{#} K": "Wasser +{#} K",
  "water {#} K": "Wasser {#} K",
  "water ΔT +{#} K": "Wasser ΔT +{#} K",
  "water ΔT {#} K": "Wasser ΔT {#} K",
  "αC +": "αC +",
  "αC −": "αC −",
  "αD −": "αD −",
  "αM {#}": "αM {#}",
  "αM −": "αM −",
  "ρ +{#} pcm": "ρ +{#} pcm",
  "ρ = ρext + αD ΔTf + αM ΔTm": "ρ = ρext + αD ΔTf + αM ΔTm",
  "ρ {#} pcm": "ρ {#} pcm",
});
