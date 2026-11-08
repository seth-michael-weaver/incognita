/* Danish: spectrum (Hurtige og termiske reaktorer) */
WT.L.ch.spectrum = {
  num: "Lektion 8", title: "Hurtige og termiske reaktorer", short: "Hurtig vs termisk",
  html: `
<div class="step">
  <h3>Hvor hurtige neutronerne er</h3>
  <p>Neutroner fødes hurtige, nær 2 MeV. I en vandreaktor preller de af brint, indtil de er lige så langsomme som vandets egne atomer: <b>termiske</b>. En hurtig reaktor har ingen moderator, så de forbliver hurtige. Skub mellem de to.</p>
  <div class="ctl"><label for="spc-m1">Moderation</label><input id="spc-m1" type="range" data-bind="mod" data-instant min="0" max="1" step="0.01" value="1"><output data-show="mod" data-fmt="2"></output></div>
</div>
<div class="step">
  <h3>Overskydende neutroner</h3>
  <p><i>η</i> er, hvor mange neutroner en brændselskerne giver tilbage pr. neutron, den absorberer. Én holder kæden i gang; for at avle nyt brændsel skal der være en ekstra til overs, så <i>η</i> et godt stykke over 2. Plutonium-239 klarer det kun med hurtige neutroner.</p>
  <div class="ctl"><label for="spc-m2">Moderation</label><input id="spc-m2" type="range" data-bind="mod" data-instant min="0" max="1" step="0.01" value="0"><output data-show="mod" data-fmt="2"></output></div>
</div>
<div class="step">
  <h3>Brænd resterne</h3>
  <p>Tunge rester som americium sluger for det meste bare langsomme neutroner og bliver tungere. Hurtige neutroner spalter en meget større andel af dem, så en hurtig reaktor kan brænde dem.</p>
  <div class="ctl"><label for="spc-m3">Moderation</label><input id="spc-m3" type="range" data-bind="mod" data-instant min="0" max="1" step="0.01" value="0"><output data-show="mod" data-fmt="2"></output></div>
</div>
<div class="step">
  <h3>Prisen</h3>
  <p>En langsom neutron giver langt lettere fission: ved 1 MeV er målet hundredvis af gange mindre. En hurtig kerne kræver derfor meget rigere brændsel, cirka 15–25 % plutonium i stedet for 3–5 % uran-235.</p>
  <div class="ctl"><label for="spc-m4">Moderation</label><input id="spc-m4" type="range" data-bind="mod" data-instant min="0" max="1" step="0.01" value="1"><output data-show="mod" data-fmt="2"></output></div>
</div>`,
};

Object.assign(WT.L.labels, {
  "Pu{#} fission cross section (target size)": "fissionstværsnit for Pu{#} (målets størrelse)",
  "Pu{#} fission target": "Pu{#}-fissionsmål",
  "at {#} MeV the target is about {#} times smaller than at {#} eV": "ved {#} MeV er målet omkring {#} gange mindre end ved {#} eV",
  "average η: U{#} {#} · Pu{#} {#}": "gennemsnitlig η: U{#} {#} · Pu{#} {#}",
  "averaged over this spectrum:  η(U{#}) ≈ {#}   η(Pu{#}) ≈ {#}": "midlet over dette spektrum:  η(U{#}) ≈ {#}   η(Pu{#}) ≈ {#}",
  "born near {#} MeV": "født nær {#} MeV",
  "born ~{#} MeV": "født ~{#} MeV",
  "fast": "hurtig",
  "fast reactor: sodium barely slows them": "hurtig reaktor: natrium bremser dem knap",
  "illustrative shapes": "illustrative former",
  "many linger at in-between energies": "mange bliver hængende ved mellemliggende energier",
  "many neutrons linger at in-between energies": "mange neutroner bliver hængende ved mellemliggende energier",
  "most neutrons are slowed all the way to thermal": "de fleste neutroner bremses helt ned til termisk",
  "most neutrons end up thermal": "de fleste neutroner ender termiske",
  "most neutrons stay between {#} keV and {#} MeV": "de fleste neutroner bliver mellem {#} keV og {#} MeV",
  "most stay between {#} keV and {#} MeV": "de fleste bliver mellem {#} keV og {#} MeV",
  "neutron energy →": "neutronenergi →",
  "no moderator (sodium)": "ingen moderator (natrium)",
  "partly moderated": "delvist modereret",
  "resonances": "resonanser",
  "slowing down (resonances)": "nedbremsning (resonanser)",
  "sodium": "natrium",
  "sodium: they stay fast": "natrium: de forbliver hurtige",
  "the rest are captured and grow heavier": "resten indfanges og bliver tungere",
  "the rest are captured: the nucleus just grows heavier": "resten indfanges: kernen bliver bare tungere",
  "thermal": "termisk",
  "hot water: kT ≈ {#} eV": "varmt vand: kT ≈ {#} eV",
  "thermal: kT ≈ {#} eV in hot water, about {#} km/s": "termisk: kT ≈ {#} eV i varmt vand, omkring {#} km/s",
  "water": "vand",
  "water reactor: hydrogen slows the neutrons": "vandreaktor: brint bremser neutronerne",
  "water: neutrons slow down": "vand: neutronerne bremses",
  "{#} % split": "{#} % spaltet",
  "{#} MeV": "{#} MeV",
  "{#} MeV: a target ~{#} times smaller": "{#} MeV: et mål ~{#} gange mindre",
  "{#} b": "{#} b",
  "{#} eV": "{#} eV",
  "{#} keV": "{#} keV",
  "η = {#}: one to continue, one to breed": "η = {#}: én til at fortsætte, én til at avle",
  "≈ {#} b": "≈ {#} b",
});
