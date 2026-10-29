/* Dutch (Nederlands): neutrons (Hoofdstuk 4, waarom reactoren op neutronen draaien) */
WT.L.ch.neutrons = {
  num: "Hoofdstuk 4", title: "Waarom reactoren op neutronen draaien", short: "Waarom neutronen",
  html: `
<div class="step">
  <p>Een proton is positief, en de 82 protonen van de kern ook. Gelijke ladingen stoten elkaar af, dus het proton wordt weggeduwd, en de duw groeit snel naarmate het dichterbij komt (de pijl). Een langzaam proton stopt vóór de kern en keert om zonder hem te raken. Pas boven ongeveer 13 MeV komt het over de duw heen; net daaronder glipt het soms toch door (<b>tunnelen</b>). De kleine grafiek toont dezelfde duw als een energieheuvel.</p>
  <div class="ctl"><label for="wn-e1">Protonenergie (MeV)</label><input id="wn-e1" type="range" data-bind="Ep" data-instant min="0.5" max="20" step="0.1" value="6"><output data-show="Ep" data-fmt="1"></output></div>
</div>
<div class="step">
  <p>Een neutron heeft geen lading: het komt bij elke snelheid binnen. Niets duwt het weg, dus er is geen heuvel te beklimmen; het hoeft alleen de kern te bereiken, en dan trekt de sterke kernkracht het naar binnen.</p>
  <div class="ctl"><label for="wn-e2">Neutronenergie (langzaam → snel)</label><input id="wn-e2" type="range" data-bind="lgEn" data-instant min="-1.6" max="7.3" step="0.01" value="-1.6"><output id="wn-en-out"></output></div>
  <p>De schuif loopt van 0,025 eV, de snelheid van een neutron bij kamertemperatuur, tot 20 MeV, bijna een miljard keer meer. Helemaal naar beneden komt het neutron nog steeds binnen.</p>
</div>
<div class="step">
  <p>Dus zelfs langzame neutronen kunnen in een reactor uranium splijten. Een uranium-235-kern die er een opslokt, wordt uranium-236 met een beetje extra energie, genoeg om te wiebelen, zich uit te rekken tot een hals en in tweeën te breken. De twee stukken vliegen met ongeveer 200 MeV uit elkaar, en de twee of drie nieuwe neutronen die ze uitwerpen kunnen de volgende kernen splijten: een kettingreactie.</p>
</div>`,
};
Object.assign(WT.L.labels, {
  "+{#} charge: the push grows as the proton gets closer": "+{#} lading: de duw groeit naarmate het proton nadert",
  "lead{#}": "lood-{#}",
  "closest approach": "kleinste afstand",
  "proton · {#} MeV": "proton · {#} MeV",
  "energy vs distance": "energie tegen afstand",
  "hill ≈ {#} MeV": "heuvel ≈ {#} MeV",
  "pushed back · about {#} in {#}³ tunnels through": "teruggeduwd · ongeveer {#} op de {#}³ tunnelt erdoor",
  "no charge, no push": "geen lading, geen duw",
  "neutron · {#} eV": "neutron · {#} eV",
  "even this crawling neutron gets in": "zelfs dit kruipende neutron komt erin",
  "≈ {#} MeV released": "≈ {#} MeV vrijgekomen",
  "two fragments + {#} new neutrons": "twee brokstukken + {#} nieuwe neutronen",
  "a slow neutron + U{#} → two fragments, {#}–{#} new neutrons, about {#} MeV": "langzaam neutron + U{#} → twee brokstukken, {#}–{#} nieuwe neutronen, ca. {#} MeV",
  "a proton this slow could never get in": "zo'n langzaam proton komt er nooit in",
});
