/* Danish: chains (Henfaldskæder og ligevægt) */
WT.L.ch.chains = {
  num: "Lektion 4", title: "Henfaldskæder og ligevægt", short: "Henfaldskæder",
  html: `
<div class="step">
  <h3>Moder, datter, barnebarn</h3>
  <p>Ofte er den nye kerne også ustabil. Moderen henfalder til en datter, som henfalder til et stabilt barnebarn. Døtre hober sig op og forsvinder så; hvor højt de hober sig op, afhænger af, hvor hurtigt de henfalder i forhold til moderen.</p>
  <div class="ctl"><label for="ch-t2">Datterens halveringstid (s)</label><input id="ch-t2" type="range" data-bind="T2" data-instant min="0.5" max="9" step="0.5" value="1.5"><output data-show="T2" data-fmt="1"></output></div>
  <div class="btns"><button class="btn ghost" data-act="refill">Ny prøve</button></div>
</div>
<div class="step">
  <h3>Sekulær ligevægt: radium og radon</h3>
  <p>Radium-226 holder 1600 år; dets datter, gassen radon-222, kun 3,8 dage. I en lukket krukke hober radonen sig op, indtil den henfalder lige så hurtigt, som den dannes: <i>A</i><sub>Rn</sub> = <i>A</i><sub>Ra</sub>(1 − e<sup>−λt</sup>), med λ radons henfaldskonstant. Efter et par uger henfalder begge lige hurtigt.</p>
  <div class="btns"><button class="btn" data-act="vent">Åbn krukken</button></div>
</div>
<div class="step">
  <h3>Transient ligevægt: technetium-koen</h3>
  <p>Hospitaler får en søjle med molybdæn-99 (66 timer), der hele tiden danner technetium-99m (6 timer), det mest brugte medicinske sporstof. Skyl technetiummet ud hver morgen, så vokser det igen og følger det langsomt aftagende molybdæn.</p>
  <div class="btns"><button class="btn" data-act="milk">Malk generatoren</button><button class="btn ghost" data-act="genre">Ny generator</button></div>
</div>
<div class="step">
  <h3>Ned ad urankæden</h3>
  <p>Uran-238 tager fjorten trin for at blive til stabilt bly. Et alfahenfald flytter to trin ned og to til venstre på dette kort, et betahenfald ét op og ét til venstre. I gammel, uforstyrret uranmalm henfalder hvert led lige hurtigt.</p>
  <div class="btns"><button class="btn" data-act="next">Næste henfald</button><button class="btn ghost" data-act="restart">Start forfra</button></div>
</div>`,
};

Object.assign(WT.L.labels, {
  "A(Rn) = A(Ra) × ({#} − exp(−λt))": "A(Rn) = A(Ra) × ({#} − exp(−λt))",
  "A(radon) = A(radium) × ({#} − exp(−λt))": "A(radon) = A(radium) × ({#} − exp(−λt))",
  "Bi{#} · half-life {#} days · beta next": "Bi{#} · halveringstid {#} dage · beta derefter",
  "Bi{#} · half-life {#} min · beta next": "Bi{#} · halveringstid {#} min · beta derefter",
  "Pa{#}m · half-life {#} min · beta next": "Pa{#}m · halveringstid {#} min · beta derefter",
  "Pb{#} · half-life {#} min · beta next": "Pb{#} · halveringstid {#} min · beta derefter",
  "Pb{#} · half-life {#} years · beta next": "Pb{#} · halveringstid {#} år · beta derefter",
  "Po{#} · half-life {#} days · alpha next": "Po{#} · halveringstid {#} dage · alfa derefter",
  "Po{#} · half-life {#} min · alpha next": "Po{#} · halveringstid {#} min · alfa derefter",
  "Po{#} · half-life {#} µs · alpha next": "Po{#} · halveringstid {#} µs · alfa derefter",
  "Ra{#} · half-life {#} yr · alpha next": "Ra{#} · halveringstid {#} år · alfa derefter",
  "Rn{#} · half-life {#} days · alpha next": "Rn{#} · halveringstid {#} dage · alfa derefter",
  "Tc{#}m out": "Tc{#}m ud",
  "Tc{#}m to the patient": "Tc{#}m til patienten",
  "Th{#} · half-life {#} days · beta next": "Th{#} · halveringstid {#} dage · beta derefter",
  "Th{#} · half-life {#} yr · alpha next": "Th{#} · halveringstid {#} år · alfa derefter",
  "U{#} · half-life {#} billion yr · alpha next": "U{#} · halveringstid {#} mia. år · alfa derefter",
  "U{#} · half-life {#} yr · alpha next": "U{#} · halveringstid {#} år · alfa derefter",
  "activity": "aktivitet",
  "alpha: loses {#} protons and {#} neutrons": "alfa: mister {#} protoner og {#} neutroner",
  "alpha: {#} p, {#} n": "alfa: {#} p, {#} n",
  "beta: a neutron becomes a proton": "beta: en neutron bliver til en proton",
  "beta: n → p": "beta: n → p",
  "dashed: never milked": "stiplet: aldrig malket",
  "daughter ({#} s): {#}": "datter ({#} s): {#}",
  "daughter peaks: {#} %": "datterens top: {#} %",
  "daughter {#}": "datter {#}",
  "day {#}: radon at {#} % of radium": "dag {#}: radon på {#} % af radium",
  "days →": "dage →",
  "granddaughter (stable): {#}": "barnebarn (stabilt): {#}",
  "grey: stable": "grå: stabil",
  "illustrative half-lives": "illustrative halveringstider",
  "molybdenum{#}": "molybdæn{#}",
  "neutrons →": "neutroner →",
  "parent ({#} s): {#}": "moder ({#} s): {#}",
  "parent {#}": "moder {#}",
  "protons ↑": "protoner ↑",
  "radium": "radium",
  "radium activity": "radiums aktivitet",
  "radium{#}": "radium{#}",
  "radon": "radon",
  "radon activity": "radons aktivitet",
  "radon{#} gas": "radon{#}-gas",
  "regrows to its peak in about {#} hours": "vokser igen til toppen på omkring {#} timer",
  "stable {#}": "stabil {#}",
  "step {#} of {#} · tap the nucleus": "trin {#} af {#} · tryk på kernen",
  "{#} d": "{#} d",
  "{#} h since last milking · Tc{#}m at {#} % of Mo{#}": "{#} t siden sidste malkning · Tc{#}m på {#} % af Mo{#}",
  "{#} s": "{#} s",
});
