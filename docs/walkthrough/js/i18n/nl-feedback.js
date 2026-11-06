/* Dutch (Nederlands): feedback (Reactorstabiliteit en terugkoppeling) */
WT.L.ch.feedback = {
  num: "Les 12", title: "Reactorstabiliteit en terugkoppeling", short: "Terugkoppeling",
  html: `
<div class="step">
  <h3>Een kringloop: vermogen, warmte, reactiviteit</h3>
  <p>Meer vermogen verwarmt de brandstof en het water, en hun temperaturen veranderen de reactiviteit <i>ρ</i>, die het vermogen bepaalt. Voeg een reactiviteitssprong toe en kijk hoe het signaal de kringloop rondgaat. Met negatieve coëfficiënten duwt het terug.</p>
  <div class="ctl"><label for="fb-r">Reactiviteitssprong (pcm)</label><input id="fb-r" type="range" data-bind="rs" data-instant min="50" max="300" step="10" value="200"><output data-show="rs" data-fmt="0"></output></div>
  <div class="btns"><button class="btn" data-act="fbIns">Invoeren</button> <button class="btn ghost" data-act="fbRes">Resetten</button></div>
</div>
<div class="step">
  <h3>Doppler: de snelle rem</h3>
  <p>Hetere brandstof vangt meer neutronen in uranium-238 zonder splijting (<a href="#doppler">dopplerverbreding</a>). Brandstof warmt binnen seconden op, dus deze rem werkt als eerste, en in waterreactoren is hij altijd negatief. Hier is hij de enige terugkoppeling.</p>
  <div class="ctl"><label for="fb-d">Dopplercoëfficiënt (pcm/K)</label><input id="fb-d" type="range" data-bind="aD" data-instant min="-5" max="-1" step="0.1" value="-2.5"><output data-show="aD" data-fmt="1"></output></div>
  <div class="btns"><button class="btn" data-act="fbIns">Invoeren</button> <button class="btn ghost" data-act="fbRes">Resetten</button></div>
</div>
<div class="step">
  <h3>De moderator doet mee</h3>
  <p>Warmer water is minder dicht en remt neutronen dus minder goed af. In een drukwaterreactor bij normale boorconcentraties maakt dit de moderatorcoëfficiënt ook negatief: een tweede, tragere rem, en het vermogen stabiliseert lager.</p>
  <div class="ctl"><label for="fb-m">Moderatorcoëfficiënt (pcm/K)</label><input id="fb-m" type="range" data-bind="aM" data-instant min="-60" max="0" step="1" value="-30"><output data-show="aM" data-fmt="0"></output></div>
  <div class="btns"><button class="btn" data-act="fbIns">Invoeren</button> <button class="btn ghost" data-act="fbRes">Resetten</button></div>
</div>
<div class="step">
  <h3>Als de terugkoppeling positief is</h3>
  <p>Als de koelmiddelterm positief is en zwaarder weegt dan Doppler, betekent meer vermogen meer reactiviteit en loopt het vermogen op hol. Waterreactoren worden ontworpen met negatieve coëfficiënten; sommige ontwerpen, zoals de RBMK bij laag vermogen, konden een positieve dampbellencoëfficiënt hebben.</p>
  <div class="ctl"><label for="fb-c">Koelmiddelcoëfficiënt (pcm/K)</label><input id="fb-c" type="range" data-bind="aM" data-instant min="-60" max="150" step="5" value="150"><output data-show="aM" data-fmt="0"></output></div>
  <div class="btns"><button class="btn" data-act="fbIns">Invoeren</button> <button class="btn ghost" data-act="fbRes">Resetten</button></div>
</div>`,
};

Object.assign(WT.L.labels, {
  "+{a} pcm": "+{a} pcm",
  "C dT/dt = P − h (T − Tc)": "C dT/dt = P − h (T − Tc)",
  "Doppler α_D = {a} pcm/K": "Doppler α_D = {a} pcm/K",
  "P {#} %": "P {#} %",
  "chain": "keten",
  "chain reaction": "kettingreactie",
  "coolant α_C = {a} pcm/K": "koelmiddel α_C = {a} pcm/K",
  "fuel +{#} K": "brandstof +{#} K",
  "fuel {#} K": "brandstof {#} K",
  "fuel ΔT +{#} K": "brandstof ΔT +{#} K",
  "fuel ΔT {#} K": "brandstof ΔT {#} K",
  "heat": "warmte",
  "heats water": "verwarmt water",
  "illustrative model": "illustratief model",
  "inserted ρ_ext = {a}": "ingevoerd ρ_ext = {a}",
  "last {#} s →": "laatste {#} s →",
  "last {#} seconds →": "laatste {#} seconden →",
  "moderator α_M = {a} pcm/K": "moderator α_M = {a} pcm/K",
  "power": "vermogen",
  "power coefficient +{a} pcm per 100 % power: runs away": "vermogenscoëfficiënt +{a} pcm per 100 % vermogen: loopt op hol",
  "power coefficient +{a} pcm per 100 %: runs away": "vermogenscoëfficiënt +{a} pcm per 100 %: loopt op hol",
  "power coefficient {a} pcm per 100 % power: self-stabilising": "vermogenscoëfficiënt {a} pcm per 100 % vermogen: zelfstabiliserend",
  "power coefficient {a} pcm per 100 %: settles": "vermogenscoëfficiënt {a} pcm per 100 %: stabiliseert",
  "power ran away · protection would shut it down": "vermogen op hol · de beveiliging zou afschakelen",
  "power ran away · in a real plant the protection system would shut it down": "vermogen op hol · in een echte centrale zou het beveiligingssysteem afschakelen",
  "steady at {#} % · press Insert": "stabiel op {#} % · druk op Invoeren",
  "steady at {#} % power · press Insert to add reactivity": "stabiel op {#} % vermogen · druk op Invoeren om reactiviteit toe te voegen",
  "water +{#} K": "water +{#} K",
  "water {#} K": "water {#} K",
  "water ΔT +{#} K": "water ΔT +{#} K",
  "water ΔT {#} K": "water ΔT {#} K",
  "αC +": "αC +",
  "αC −": "αC −",
  "αD −": "αD −",
  "αM {#}": "αM {#}",
  "αM −": "αM −",
  "ρ +{#} pcm": "ρ +{#} pcm",
  "ρ = ρext + αD ΔTf + αM ΔTm": "ρ = ρext + αD ΔTf + αM ΔTm",
  "ρ {#} pcm": "ρ {#} pcm",
});
