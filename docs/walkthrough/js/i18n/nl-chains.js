/* Dutch (Nederlands): chains (Vervalketens en evenwicht) */
WT.L.ch.chains = {
  num: "Les 4", title: "Vervalketens en evenwicht", short: "Vervalketens",
  html: `
<div class="step">
  <h3>Moeder, dochter, kleindochter</h3>
  <p>Vaak is de nieuwe kern ook instabiel. De moeder vervalt naar een dochter, die vervalt naar een stabiele kleindochter. Dochters stapelen zich op en verdwijnen dan; hoe hoog ze zich opstapelen, hangt af van hoe snel ze vervallen vergeleken met de moeder.</p>
  <div class="ctl"><label for="ch-t2">Halveringstijd dochter (s)</label><input id="ch-t2" type="range" data-bind="T2" data-instant min="0.5" max="9" step="0.5" value="1.5"><output data-show="T2" data-fmt="1"></output></div>
  <div class="btns"><button class="btn ghost" data-act="refill">Nieuw monster</button></div>
</div>
<div class="step">
  <h3>Seculier evenwicht: radium en radon</h3>
  <p>Radium-226 gaat 1600 jaar mee; zijn dochter, het gas radon-222, maar 3,8 dagen. In een afgesloten pot hoopt het radon zich op tot het even snel vervalt als het ontstaat: <i>A</i><sub>Rn</sub> = <i>A</i><sub>Ra</sub>(1 − e<sup>−λt</sup>), met λ de vervalconstante van radon. Na een paar weken vervallen beide even snel.</p>
  <div class="btns"><button class="btn" data-act="vent">Open de pot</button></div>
</div>
<div class="step">
  <h3>Transiënt evenwicht: de technetiumkoe</h3>
  <p>Ziekenhuizen krijgen een kolom met molybdeen-99 (66 uur) die steeds technetium-99m (6 uur) aanmaakt, de meestgebruikte medische tracer. Spoel het technetium elke ochtend eruit en het groeit weer aan, het langzaam afnemende molybdeen volgend.</p>
  <div class="btns"><button class="btn" data-act="milk">Melk de generator</button><button class="btn ghost" data-act="genre">Nieuwe generator</button></div>
</div>
<div class="step">
  <h3>De uraniumreeks af</h3>
  <p>Uranium-238 heeft veertien stappen nodig om stabiel lood te worden. Een alfaverval gaat op deze kaart twee stappen omlaag en twee naar links, een bètaverval één omhoog en één naar links. In oud, ongestoord uraniumerts vervalt elk lid even snel.</p>
  <div class="btns"><button class="btn" data-act="next">Volgend verval</button><button class="btn ghost" data-act="restart">Opnieuw beginnen</button></div>
</div>`,
};

Object.assign(WT.L.labels, {
  "A(Rn) = A(Ra) × ({#} − exp(−λt))": "A(Rn) = A(Ra) × ({#} − exp(−λt))",
  "A(radon) = A(radium) × ({#} − exp(−λt))": "A(radon) = A(radium) × ({#} − exp(−λt))",
  "Bi{#} · half-life {#} days · beta next": "Bi{#} · halveringstijd {#} dagen · hierna bèta",
  "Bi{#} · half-life {#} min · beta next": "Bi{#} · halveringstijd {#} min · hierna bèta",
  "Pa{#}m · half-life {#} min · beta next": "Pa{#}m · halveringstijd {#} min · hierna bèta",
  "Pb{#} · half-life {#} min · beta next": "Pb{#} · halveringstijd {#} min · hierna bèta",
  "Pb{#} · half-life {#} years · beta next": "Pb{#} · halveringstijd {#} jaar · hierna bèta",
  "Po{#} · half-life {#} days · alpha next": "Po{#} · halveringstijd {#} dagen · hierna alfa",
  "Po{#} · half-life {#} min · alpha next": "Po{#} · halveringstijd {#} min · hierna alfa",
  "Po{#} · half-life {#} µs · alpha next": "Po{#} · halveringstijd {#} µs · hierna alfa",
  "Ra{#} · half-life {#} yr · alpha next": "Ra{#} · halveringstijd {#} jr · hierna alfa",
  "Rn{#} · half-life {#} days · alpha next": "Rn{#} · halveringstijd {#} dagen · hierna alfa",
  "Tc{#}m out": "Tc{#}m eruit",
  "Tc{#}m to the patient": "Tc{#}m naar de patiënt",
  "Th{#} · half-life {#} days · beta next": "Th{#} · halveringstijd {#} dagen · hierna bèta",
  "Th{#} · half-life {#} yr · alpha next": "Th{#} · halveringstijd {#} jr · hierna alfa",
  "U{#} · half-life {#} billion yr · alpha next": "U{#} · halveringstijd {#} miljard jr · hierna alfa",
  "U{#} · half-life {#} yr · alpha next": "U{#} · halveringstijd {#} jr · hierna alfa",
  "activity": "activiteit",
  "alpha: loses {#} protons and {#} neutrons": "alfa: verliest {#} protonen en {#} neutronen",
  "alpha: {#} p, {#} n": "alfa: {#} p, {#} n",
  "beta: a neutron becomes a proton": "bèta: een neutron wordt een proton",
  "beta: n → p": "bèta: n → p",
  "dashed: never milked": "gestreept: nooit gemolken",
  "daughter ({#} s): {#}": "dochter ({#} s): {#}",
  "daughter peaks: {#} %": "piek van de dochter: {#} %",
  "daughter {#}": "dochter {#}",
  "day {#}: radon at {#} % of radium": "dag {#}: radon op {#} % van radium",
  "days →": "dagen →",
  "granddaughter (stable): {#}": "kleindochter (stabiel): {#}",
  "grey: stable": "grijs: stabiel",
  "illustrative half-lives": "illustratieve halveringstijden",
  "molybdenum{#}": "molybdeen{#}",
  "neutrons →": "neutronen →",
  "parent ({#} s): {#}": "moeder ({#} s): {#}",
  "parent {#}": "moeder {#}",
  "protons ↑": "protonen ↑",
  "radium": "radium",
  "radium activity": "activiteit radium",
  "radium{#}": "radium{#}",
  "radon": "radon",
  "radon activity": "activiteit radon",
  "radon{#} gas": "radon{#}-gas",
  "regrows to its peak in about {#} hours": "groeit in ongeveer {#} uur weer naar zijn piek",
  "stable {#}": "stabiel {#}",
  "step {#} of {#} · tap the nucleus": "stap {#} van {#} · tik op de kern",
  "{#} d": "{#} d",
  "{#} h since last milking · Tc{#}m at {#} % of Mo{#}": "{#} u sinds laatste keer melken · Tc{#}m op {#} % van Mo{#}",
  "{#} s": "{#} s",
});
