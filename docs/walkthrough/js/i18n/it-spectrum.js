/* Italian: spectrum (Reattori veloci e termici) */
WT.L.ch.spectrum = {
  num: "Lezione 1", title: "Reattori veloci e termici", short: "Veloci o termici",
  html: `
<div class="step">
  <h3>Quanto sono veloci i neutroni</h3>
  <p>I neutroni nascono veloci, intorno a 2 MeV. In un reattore ad acqua rimbalzano sull'idrogeno finché non sono lenti quanto gli atomi dell'acqua stessa: <b>termici</b>. Un reattore veloce non ha moderatore, così restano veloci. Passa dall'uno all'altro.</p>
  <div class="ctl"><label for="spc-m1">Moderazione</label><input id="spc-m1" type="range" data-bind="mod" data-instant min="0" max="1" step="0.01" value="1"><output data-show="mod" data-fmt="2"></output></div>
</div>
<div class="step">
  <h3>Neutroni di scorta</h3>
  <p><i>η</i> è il numero di neutroni che un nucleo di combustibile restituisce per ogni neutrone che assorbe. Uno basta a mantenere la catena; per produrre nuovo combustibile (fertilizzazione) ne serve un secondo di scorta, quindi <i>η</i> ben sopra 2. Il plutonio-239 ci riesce solo con neutroni veloci.</p>
  <div class="ctl"><label for="spc-m2">Moderazione</label><input id="spc-m2" type="range" data-bind="mod" data-instant min="0" max="1" step="0.01" value="0"><output data-show="mod" data-fmt="2"></output></div>
</div>
<div class="step">
  <h3>Bruciare gli avanzi</h3>
  <p>Gli avanzi pesanti come l'americio per lo più inghiottono i neutroni lenti e diventano più pesanti. I neutroni veloci ne spezzano una parte molto maggiore, quindi un reattore veloce può bruciarli.</p>
  <div class="ctl"><label for="spc-m3">Moderazione</label><input id="spc-m3" type="range" data-bind="mod" data-instant min="0" max="1" step="0.01" value="0"><output data-show="mod" data-fmt="2"></output></div>
</div>
<div class="step">
  <h3>Il prezzo</h3>
  <p>Un neutrone lento ha molte più probabilità di provocare una fissione: a 1 MeV il bersaglio è centinaia di volte più piccolo. Per questo un nocciolo veloce richiede un combustibile molto più ricco, circa 15–25 % di plutonio invece del 3–5 % di uranio-235.</p>
  <div class="ctl"><label for="spc-m4">Moderazione</label><input id="spc-m4" type="range" data-bind="mod" data-instant min="0" max="1" step="0.01" value="1"><output data-show="mod" data-fmt="2"></output></div>
</div>`,
};

Object.assign(WT.L.labels, {
  "water: neutrons slow down": "acqua: i neutroni rallentano",
  "water reactor: hydrogen slows the neutrons": "reattore ad acqua: l'idrogeno rallenta i neutroni",
  "sodium: they stay fast": "sodio: restano veloci",
  "fast reactor: sodium barely slows them": "reattore veloce: il sodio li rallenta appena",
  "partly moderated": "in parte moderato",
  "{#} % split": "{#} % fissionati",
  "sodium": "sodio",
  "no moderator (sodium)": "nessun moderatore (sodio)",
  "water": "acqua",
  "thermal": "termici",
  "resonances": "risonanze",
  "slowing down (resonances)": "rallentamento (risonanze)",
  "fast": "veloci",
  "{#} eV": "{#} eV",
  "{#} keV": "{#} keV",
  "{#} MeV": "{#} MeV",
  "neutron energy →": "energia del neutrone →",
  "born ~{#} MeV": "nati a ~{#} MeV",
  "born near {#} MeV": "nati intorno a {#} MeV",
  "η = {#}: one to continue, one to breed": "η = {#}: uno per la catena, uno per fertilizzare",
  "average η: U{#} {#} · Pu{#} {#}": "η medio: U{#} {#} · Pu{#} {#}",
  "averaged over this spectrum:  η(U{#}) ≈ {#}   η(Pu{#}) ≈ {#}": "media su questo spettro:  η(U{#}) ≈ {#}   η(Pu{#}) ≈ {#}",
  "{#} b": "{#} b",
  "≈ {#} b": "≈ {#} b",
  "Pu{#} fission target": "bersaglio di fissione del Pu{#}",
  "Pu{#} fission cross section (target size)": "sezione d'urto di fissione del Pu{#} (dimensione del bersaglio)",
  "{#} MeV: a target ~{#} times smaller": "{#} MeV: un bersaglio ~{#} volte più piccolo",
  "at {#} MeV the target is about {#} times smaller than at {#} eV": "a {#} MeV il bersaglio è circa {#} volte più piccolo che a {#} eV",
  "most neutrons end up thermal": "quasi tutti finiscono termici",
  "most neutrons are slowed all the way to thermal": "quasi tutti i neutroni rallentano fino all'energia termica",
  "most stay between {#} keV and {#} MeV": "quasi tutti restano fra {#} keV e {#} MeV",
  "most neutrons stay between {#} keV and {#} MeV": "quasi tutti i neutroni restano fra {#} keV e {#} MeV",
  "many linger at in-between energies": "molti indugiano a energie intermedie",
  "many neutrons linger at in-between energies": "molti neutroni indugiano a energie intermedie",
  "thermal ≈ {#} eV, ~{#} km/s": "termici ≈ {#} eV, ~{#} km/s",
  "thermal: kT ≈ {#} eV in hot water, about {#} km/s": "termici: kT ≈ {#} eV in acqua calda, circa {#} km/s",
  "the rest are captured and grow heavier": "gli altri sono catturati e si appesantiscono",
  "the rest are captured: the nucleus just grows heavier": "gli altri sono catturati: il nucleo diventa solo più pesante",
  "illustrative shapes": "forme illustrative",
});
