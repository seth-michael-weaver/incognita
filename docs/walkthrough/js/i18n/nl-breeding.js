/* Dutch (Nederlands): breeding (Nieuwe brandstof kweken) */
WT.L.ch.breeding = {
  num: "Les 9", title: "Nieuwe brandstof kweken", short: "Kweken",
  html: `
<div class="step">
  <h3>Kweekbaar wordt splijtbaar</h3>
  <p>Uranium-238 splijt nauwelijks, maar kan wel een neutron invangen. Twee bètavervallen later (telkens wordt een neutron binnenin een proton) is het plutonium-239 geworden, dat makkelijk splijt. Thorium-232 doet hetzelfde en wordt uranium-233.</p>
  <div class="btns"><button class="btn ghost" data-act="bcU" aria-pressed="true">Uranium-238</button> <button class="btn ghost" data-act="bcT" aria-pressed="false">Thorium-232</button></div>
</div>
<div class="step">
  <h3>Het neutronenbudget</h3>
  <p>Elk neutron dat in splijtbare brandstof wordt geabsorbeerd, geeft <i>η</i> nieuwe neutronen terug. Eén moet de volgende splijting veroorzaken en sommige gaan verloren; wat overblijft, kan kweken. Met uranium-235 en trage neutronen ontstaan maar ongeveer 0,6 nieuwe splijtbare kernen per verbrande kern.</p>
  <div class="btns"><button class="btn ghost" data-act="bfU5" aria-pressed="true">U-235</button> <button class="btn ghost" data-act="bfP9" aria-pressed="false">Pu-239</button> <button class="btn ghost" data-act="bfU3" aria-pressed="false">U-233</button></div>
  <div class="btns"><button class="btn ghost" data-act="bsT" aria-pressed="true">Trage neutronen</button> <button class="btn ghost" data-act="bsF" aria-pressed="false">Snelle neutronen</button></div>
</div>
<div class="step">
  <h3>Snelle neutronen kweken</h3>
  <p>Om te kweken moet één neutron de keten voortzetten en minstens één nieuwe brandstof maken, dus <i>η</i> moet 2 met meer dan de verliezen overtreffen. Plutonium-239 in een snelle reactor geeft ongeveer 2,4: genoeg over.</p>
  <div class="ctl"><label for="br-l1">Verloren neutronen</label><input id="br-l1" type="range" data-bind="L" data-instant min="0.05" max="0.8" step="0.01" value="0.2"><output data-show="L" data-fmt="2"></output></div>
</div>
<div class="step">
  <h3>Thorium met trage neutronen</h3>
  <p>Met trage neutronen geeft plutonium-239 maar ongeveer 2,1, uranium-233 daarentegen 2,29. Die marge laat een thoriumreactor kweken met trage neutronen, als hij er heel weinig verspilt. Verlaag de verliezen tot hij kweekt.</p>
  <div class="ctl"><label for="br-l2">Verloren neutronen</label><input id="br-l2" type="range" data-bind="L" data-instant min="0.05" max="0.8" step="0.01" value="0.35"><output data-show="L" data-fmt="2"></output></div>
</div>
<div class="step">
  <h3>Conversieverhouding</h3>
  <p>De conversieverhouding is het aantal gemaakte splijtbare kernen per verbrande splijtbare kern. Onder 1 raakt de brandstof langzaam op (een converter, zoals de huidige waterreactoren); boven 1 eindigt de reactor met meer brandstof dan waarmee hij begon (een kweekreactor).</p>
  <div class="btns"><button class="btn ghost" data-act="bfU5" aria-pressed="true">U-235</button> <button class="btn ghost" data-act="bfP9" aria-pressed="false">Pu-239</button> <button class="btn ghost" data-act="bfU3" aria-pressed="false">U-233</button></div>
  <div class="btns"><button class="btn ghost" data-act="bsT" aria-pressed="true">Trage neutronen</button> <button class="btn ghost" data-act="bsF" aria-pressed="false">Snelle neutronen</button></div>
</div>`,
};

Object.assign(WT.L.labels, {
  "+ n": "+ n",
  "Th{#} (fertile)": "Th{#} (kweekbaar)",
  "U{#} (fertile)": "U{#} (kweekbaar)",
  "a batch of {a} waiting · day {b}": "een partij {a} wacht · dag {b}",
  "after {#} months, {#} % has become U{#}": "na {#} maanden is {#} % U{#} geworden",
  "after {#} weeks, {#} % has become Pu{#}": "na {#} weken is {#} % Pu{#} geworden",
  "antineutrino": "antineutrino",
  "breed": "kweken",
  "breeds: Th{#} → U{#}": "kweekt: Th{#} → U{#}",
  "breeds: U{#} → Pu{#}": "kweekt: U{#} → Pu{#}",
  "burned {a}": "verbrand {a}",
  "catch": "invangst",
  "chain": "keten",
  "conversion ratio {a}: a converter": "conversieverhouding {a}: een converter",
  "conversion ratio {a}: a breeder": "conversieverhouding {a}: een kweekreactor",
  "conversion ratio ≈ η − 1 − lost = {a}: breeds": "conversieverhouding ≈ η − 1 − verloren = {a}: kweekt",
  "conversion ratio ≈ η − 1 − lost = {a}: breeds, makes more fuel than it burns": "conversieverhouding ≈ η − 1 − verloren = {a}: kweekt, maakt meer brandstof dan hij verbrandt",
  "conversion ratio ≈ η − 1 − lost = {a}: converts": "conversieverhouding ≈ η − 1 − verloren = {a}: converteert",
  "conversion ratio ≈ η − 1 − lost = {a}: converts, makes less fuel than it burns": "conversieverhouding ≈ η − 1 − verloren = {a}: converteert, maakt minder brandstof dan hij verbrandt",
  "electron": "elektron",
  "fast neutrons": "snelle neutronen",
  "fertile": "kweekbaar",
  "fertile: barely splits": "kweekbaar: splijt nauwelijks",
  "fissile": "splijtbaar",
  "fissile: splits easily": "splijtbaar: splijt makkelijk",
  "illustration": "illustratie",
  "lost": "verloren",
  "lost: water, steel, poisons, leakage": "verloren: water, staal, gifstoffen, lekkage",
  "made {a}": "gemaakt {a}",
  "neutrons out per neutron absorbed in the fuel": "neutronen eruit per in de brandstof geabsorbeerd neutron",
  "neutrons per absorption": "neutronen per absorptie",
  "next fission": "volgende splijting",
  "next fission: keeps the chain going": "volgende splijting: houdt de keten gaande",
  "slow neutrons": "trage neutronen",
  "slow step: Np{#}, half-life {#} d": "trage stap: Np{#}, halveringstijd {#} d",
  "slow step: Pa{#}, half-life {#} d": "trage stap: Pa{#}, halveringstijd {#} d",
  "split": "gespleten",
  "split (fission products)": "gespleten (splijtingsproducten)",
  "the slow step is Np{#} (half-life {#} days)": "de trage stap is Np{#} (halveringstijd {#} dagen)",
  "the slow step is Pa{#} (half-life {#} days)": "de trage stap is Pa{#} (halveringstijd {#} dagen)",
  "{#} d": "{#} d",
  "{#} min": "{#} min",
  "{#} p": "{#} p",
  "{#} protons": "{#} protonen",
  "{#}: breeding line": "{#}: kweekgrens",
  "{a} % now {b}": "{a} % nu {b}",
  "{a} per absorption": "{a} per absorptie",
  "{a} waiting: day {b}": "{a} wacht: dag {b}",
  "{a} · fast neutrons": "{a} · snelle neutronen",
  "{a} · slow neutrons": "{a} · trage neutronen",
  "η = {a}": "η = {a}",
  "η ≈ {a}": "η ≈ {a}",
});
