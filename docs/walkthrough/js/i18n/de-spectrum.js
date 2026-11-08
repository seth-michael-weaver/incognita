/* German (Deutsch): spectrum (Schnelle und thermische Reaktoren) */
WT.L.ch.spectrum = {
  num: "Lektion 8", title: "Schnelle und thermische Reaktoren", short: "Schnell vs. thermisch",
  html: `
<div class="step">
  <h3>Wie schnell die Neutronen sind</h3>
  <p>Neutronen entstehen schnell, bei etwa 2 MeV. In einem Wasserreaktor prallen sie an Wasserstoff ab, bis sie so langsam sind wie die Atome des Wassers selbst: <b>thermisch</b>. Ein schneller Reaktor hat keinen Moderator, also bleiben sie schnell. Schiebe zwischen beiden hin und her.</p>
  <div class="ctl"><label for="spc-m1">Moderation</label><input id="spc-m1" type="range" data-bind="mod" data-instant min="0" max="1" step="0.01" value="1"><output data-show="mod" data-fmt="2"></output></div>
</div>
<div class="step">
  <h3>Überzählige Neutronen</h3>
  <p><i>η</i> gibt an, wie viele Neutronen ein Brennstoffkern pro absorbiertem Neutron zurückgibt. Eines hält die Kette in Gang; um neuen Brennstoff zu erbrüten, braucht man ein zweites übrig, also <i>η</i> deutlich über 2. Plutonium-239 schafft das nur mit schnellen Neutronen.</p>
  <div class="ctl"><label for="spc-m2">Moderation</label><input id="spc-m2" type="range" data-bind="mod" data-instant min="0" max="1" step="0.01" value="0"><output data-show="mod" data-fmt="2"></output></div>
</div>
<div class="step">
  <h3>Die Reste verbrennen</h3>
  <p>Schwere Reste wie Americium schlucken langsame Neutronen meist nur und werden schwerer. Schnelle Neutronen spalten einen viel größeren Anteil davon, also kann ein schneller Reaktor sie verbrennen.</p>
  <div class="ctl"><label for="spc-m3">Moderation</label><input id="spc-m3" type="range" data-bind="mod" data-instant min="0" max="1" step="0.01" value="0"><output data-show="mod" data-fmt="2"></output></div>
</div>
<div class="step">
  <h3>Der Preis</h3>
  <p>Ein langsames Neutron löst viel eher eine Spaltung aus: Bei 1 MeV ist die Zielscheibe hundertfach kleiner. Ein schneller Kern braucht daher viel reicheren Brennstoff, etwa 15–25 % Plutonium statt 3–5 % Uran-235.</p>
  <div class="ctl"><label for="spc-m4">Moderation</label><input id="spc-m4" type="range" data-bind="mod" data-instant min="0" max="1" step="0.01" value="1"><output data-show="mod" data-fmt="2"></output></div>
</div>`,
};

Object.assign(WT.L.labels, {
  "Pu{#} fission cross section (target size)": "Spaltquerschnitt von Pu{#} (Größe der Zielscheibe)",
  "Pu{#} fission target": "Pu{#}-Spaltzielscheibe",
  "at {#} MeV the target is about {#} times smaller than at {#} eV": "bei {#} MeV ist die Zielscheibe etwa {#}-mal kleiner als bei {#} eV",
  "average η: U{#} {#} · Pu{#} {#}": "mittleres η: U{#} {#} · Pu{#} {#}",
  "averaged over this spectrum:  η(U{#}) ≈ {#}   η(Pu{#}) ≈ {#}": "gemittelt über dieses Spektrum:  η(U{#}) ≈ {#}   η(Pu{#}) ≈ {#}",
  "born near {#} MeV": "entstanden bei etwa {#} MeV",
  "born ~{#} MeV": "entstanden ~{#} MeV",
  "fast": "schnell",
  "fast reactor: sodium barely slows them": "schneller Reaktor: Natrium bremst sie kaum",
  "illustrative shapes": "schematische Verläufe",
  "many linger at in-between energies": "viele verweilen bei mittleren Energien",
  "many neutrons linger at in-between energies": "viele Neutronen verweilen bei mittleren Energien",
  "most neutrons are slowed all the way to thermal": "die meisten Neutronen werden bis auf thermisch abgebremst",
  "most neutrons end up thermal": "die meisten Neutronen werden thermisch",
  "most neutrons stay between {#} keV and {#} MeV": "die meisten Neutronen bleiben zwischen {#} keV und {#} MeV",
  "most stay between {#} keV and {#} MeV": "die meisten bleiben zwischen {#} keV und {#} MeV",
  "neutron energy →": "Neutronenenergie →",
  "no moderator (sodium)": "kein Moderator (Natrium)",
  "partly moderated": "teilweise moderiert",
  "resonances": "Resonanzen",
  "slowing down (resonances)": "Abbremsung (Resonanzen)",
  "sodium": "Natrium",
  "sodium: they stay fast": "Natrium: sie bleiben schnell",
  "the rest are captured and grow heavier": "der Rest wird eingefangen und wird schwerer",
  "the rest are captured: the nucleus just grows heavier": "der Rest wird eingefangen: der Kern wird nur schwerer",
  "thermal": "thermisch",
  "hot water: kT ≈ {#} eV": "heißes Wasser: kT ≈ {#} eV",
  "thermal: kT ≈ {#} eV in hot water, about {#} km/s": "thermisch: kT ≈ {#} eV in heißem Wasser, etwa {#} km/s",
  "water": "Wasser",
  "water reactor: hydrogen slows the neutrons": "Wasserreaktor: Wasserstoff bremst die Neutronen",
  "water: neutrons slow down": "Wasser: Neutronen werden abgebremst",
  "{#} % split": "{#} % gespalten",
  "{#} MeV": "{#} MeV",
  "{#} MeV: a target ~{#} times smaller": "{#} MeV: Zielscheibe ~{#}-mal kleiner",
  "{#} b": "{#} b",
  "{#} eV": "{#} eV",
  "{#} keV": "{#} keV",
  "η = {#}: one to continue, one to breed": "η = {#}: eines zum Weitermachen, eines zum Brüten",
  "≈ {#} b": "≈ {#} b",
});
