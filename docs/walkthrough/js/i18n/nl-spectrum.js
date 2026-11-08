/* Dutch (Nederlands): spectrum (Snelle en thermische reactoren) */
WT.L.ch.spectrum = {
  num: "Les 8", title: "Snelle en thermische reactoren", short: "Snel vs thermisch",
  html: `
<div class="step">
  <h3>Hoe snel de neutronen zijn</h3>
  <p>Neutronen worden snel geboren, rond 2 MeV. In een waterreactor kaatsen ze tegen waterstof tot ze even traag zijn als de atomen van het water zelf: <b>thermisch</b>. Een snelle reactor heeft geen moderator, dus blijven ze snel. Schuif tussen de twee.</p>
  <div class="ctl"><label for="spc-m1">Moderatie</label><input id="spc-m1" type="range" data-bind="mod" data-instant min="0" max="1" step="0.01" value="1"><output data-show="mod" data-fmt="2"></output></div>
</div>
<div class="step">
  <h3>Neutronen over</h3>
  <p><i>η</i> is hoeveel neutronen een brandstofkern teruggeeft per geabsorbeerd neutron. Eén houdt de keten gaande; om nieuwe brandstof te kweken heb je er een tweede over nodig, dus <i>η</i> ruim boven 2. Plutonium-239 haalt dat alleen met snelle neutronen.</p>
  <div class="ctl"><label for="spc-m2">Moderatie</label><input id="spc-m2" type="range" data-bind="mod" data-instant min="0" max="1" step="0.01" value="0"><output data-show="mod" data-fmt="2"></output></div>
</div>
<div class="step">
  <h3>De restjes verbranden</h3>
  <p>Zware restjes zoals americium slokken trage neutronen meestal alleen op en worden zwaarder. Snelle neutronen splijten een veel groter deel ervan, dus een snelle reactor kan ze verbranden.</p>
  <div class="ctl"><label for="spc-m3">Moderatie</label><input id="spc-m3" type="range" data-bind="mod" data-instant min="0" max="1" step="0.01" value="0"><output data-show="mod" data-fmt="2"></output></div>
</div>
<div class="step">
  <h3>De prijs</h3>
  <p>Een traag neutron veroorzaakt veel eerder splijting: bij 1 MeV is het doelwit honderden keren kleiner. Een snelle kern heeft dus veel rijkere brandstof nodig, zo'n 15–25 % plutonium in plaats van 3–5 % uranium-235.</p>
  <div class="ctl"><label for="spc-m4">Moderatie</label><input id="spc-m4" type="range" data-bind="mod" data-instant min="0" max="1" step="0.01" value="1"><output data-show="mod" data-fmt="2"></output></div>
</div>`,
};

Object.assign(WT.L.labels, {
  "Pu{#} fission cross section (target size)": "splijtingsdoorsnede van Pu{#} (grootte van het doelwit)",
  "Pu{#} fission target": "Pu{#}-splijtingsdoelwit",
  "at {#} MeV the target is about {#} times smaller than at {#} eV": "bij {#} MeV is het doelwit ongeveer {#} keer kleiner dan bij {#} eV",
  "average η: U{#} {#} · Pu{#} {#}": "gemiddelde η: U{#} {#} · Pu{#} {#}",
  "averaged over this spectrum:  η(U{#}) ≈ {#}   η(Pu{#}) ≈ {#}": "gemiddeld over dit spectrum:  η(U{#}) ≈ {#}   η(Pu{#}) ≈ {#}",
  "born near {#} MeV": "geboren rond {#} MeV",
  "born ~{#} MeV": "geboren ~{#} MeV",
  "fast": "snel",
  "fast reactor: sodium barely slows them": "snelle reactor: natrium remt ze nauwelijks af",
  "illustrative shapes": "illustratieve vormen",
  "many linger at in-between energies": "veel blijven hangen bij tussenliggende energieën",
  "many neutrons linger at in-between energies": "veel neutronen blijven hangen bij tussenliggende energieën",
  "most neutrons are slowed all the way to thermal": "de meeste neutronen worden helemaal tot thermisch afgeremd",
  "most neutrons end up thermal": "de meeste neutronen worden thermisch",
  "most neutrons stay between {#} keV and {#} MeV": "de meeste neutronen blijven tussen {#} keV en {#} MeV",
  "most stay between {#} keV and {#} MeV": "de meeste blijven tussen {#} keV en {#} MeV",
  "neutron energy →": "neutronenergie →",
  "no moderator (sodium)": "geen moderator (natrium)",
  "partly moderated": "deels gemodereerd",
  "resonances": "resonanties",
  "slowing down (resonances)": "afremming (resonanties)",
  "sodium": "natrium",
  "sodium: they stay fast": "natrium: ze blijven snel",
  "the rest are captured and grow heavier": "de rest wordt ingevangen en wordt zwaarder",
  "the rest are captured: the nucleus just grows heavier": "de rest wordt ingevangen: de kern wordt alleen zwaarder",
  "thermal": "thermisch",
  "hot water: kT ≈ {#} eV": "heet water: kT ≈ {#} eV",
  "thermal: kT ≈ {#} eV in hot water, about {#} km/s": "thermisch: kT ≈ {#} eV in heet water, ongeveer {#} km/s",
  "water": "water",
  "water reactor: hydrogen slows the neutrons": "waterreactor: waterstof remt de neutronen af",
  "water: neutrons slow down": "water: neutronen remmen af",
  "{#} % split": "{#} % gespleten",
  "{#} MeV": "{#} MeV",
  "{#} MeV: a target ~{#} times smaller": "{#} MeV: doelwit ~{#} keer kleiner",
  "{#} b": "{#} b",
  "{#} eV": "{#} eV",
  "{#} keV": "{#} keV",
  "η = {#}: one to continue, one to breed": "η = {#}: één om door te gaan, één om te kweken",
  "≈ {#} b": "≈ {#} b",
});
