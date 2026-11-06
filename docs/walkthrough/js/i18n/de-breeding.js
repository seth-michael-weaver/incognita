/* German (Deutsch): breeding (Neuen Brennstoff erbrüten) */
WT.L.ch.breeding = {
  num: "Lektion 9", title: "Neuen Brennstoff erbrüten", short: "Brüten",
  html: `
<div class="step">
  <h3>Aus Brutstoff wird Spaltstoff</h3>
  <p>Uran-238 spaltet sich kaum, kann aber ein Neutron einfangen. Zwei Betazerfälle später (jedes Mal wird ein Neutron im Inneren zu einem Proton) ist es zu Plutonium-239 geworden, das sich leicht spaltet. Thorium-232 macht dasselbe und wird zu Uran-233.</p>
  <div class="btns"><button class="btn ghost" data-act="bcU" aria-pressed="true">Uran-238</button> <button class="btn ghost" data-act="bcT" aria-pressed="false">Thorium-232</button></div>
</div>
<div class="step">
  <h3>Die Neutronenbilanz</h3>
  <p>Jedes im spaltbaren Brennstoff absorbierte Neutron gibt <i>η</i> neue Neutronen zurück. Eines muss die nächste Spaltung auslösen, und einige gehen verloren; was übrig bleibt, kann brüten. Mit Uran-235 und langsamen Neutronen entstehen pro verbranntem Kern nur etwa 0,6 neue spaltbare Kerne.</p>
  <div class="btns"><button class="btn ghost" data-act="bfU5" aria-pressed="true">U-235</button> <button class="btn ghost" data-act="bfP9" aria-pressed="false">Pu-239</button> <button class="btn ghost" data-act="bfU3" aria-pressed="false">U-233</button></div>
  <div class="btns"><button class="btn ghost" data-act="bsT" aria-pressed="true">Langsame Neutronen</button> <button class="btn ghost" data-act="bsF" aria-pressed="false">Schnelle Neutronen</button></div>
</div>
<div class="step">
  <h3>Schnelle Neutronen brüten</h3>
  <p>Zum Brüten muss ein Neutron die Kette fortsetzen und mindestens eines neuen Brennstoff erzeugen, also muss <i>η</i> die 2 um mehr als die Verluste übertreffen. Plutonium-239 in einem schnellen Reaktor liefert etwa 2,4: genug Reserve.</p>
  <div class="ctl"><label for="br-l1">Verlorene Neutronen</label><input id="br-l1" type="range" data-bind="L" data-instant min="0.05" max="0.8" step="0.01" value="0.2"><output data-show="L" data-fmt="2"></output></div>
</div>
<div class="step">
  <h3>Thorium mit langsamen Neutronen</h3>
  <p>Mit langsamen Neutronen liefert Plutonium-239 nur etwa 2,1, Uran-233 dagegen 2,29. Dieser Spielraum erlaubt es einem Thoriumreaktor, mit langsamen Neutronen zu brüten, wenn er nur sehr wenige verschwendet. Senke die Verluste, bis er brütet.</p>
  <div class="ctl"><label for="br-l2">Verlorene Neutronen</label><input id="br-l2" type="range" data-bind="L" data-instant min="0.05" max="0.8" step="0.01" value="0.35"><output data-show="L" data-fmt="2"></output></div>
</div>
<div class="step">
  <h3>Konversionsrate</h3>
  <p>Die Konversionsrate ist die Zahl der erzeugten spaltbaren Kerne pro verbranntem spaltbarem Kern. Unter 1 geht der Brennstoff langsam zur Neige (ein Konverter, wie die heutigen Wasserreaktoren); über 1 hat der Reaktor am Ende mehr Brennstoff als zu Beginn (ein Brüter).</p>
  <div class="btns"><button class="btn ghost" data-act="bfU5" aria-pressed="true">U-235</button> <button class="btn ghost" data-act="bfP9" aria-pressed="false">Pu-239</button> <button class="btn ghost" data-act="bfU3" aria-pressed="false">U-233</button></div>
  <div class="btns"><button class="btn ghost" data-act="bsT" aria-pressed="true">Langsame Neutronen</button> <button class="btn ghost" data-act="bsF" aria-pressed="false">Schnelle Neutronen</button></div>
</div>`,
};

Object.assign(WT.L.labels, {
  "+ n": "+ n",
  "Th{#} (fertile)": "Th{#} (Brutstoff)",
  "U{#} (fertile)": "U{#} (Brutstoff)",
  "a batch of {a} waiting · day {b}": "eine Charge {a} wartet · Tag {b}",
  "after {#} months, {#} % has become U{#}": "nach {#} Monaten sind {#} % zu U{#} geworden",
  "after {#} weeks, {#} % has become Pu{#}": "nach {#} Wochen sind {#} % zu Pu{#} geworden",
  "antineutrino": "Antineutrino",
  "breed": "brüten",
  "breeds: Th{#} → U{#}": "brütet: Th{#} → U{#}",
  "breeds: U{#} → Pu{#}": "brütet: U{#} → Pu{#}",
  "burned {a}": "verbrannt {a}",
  "catch": "Einfang",
  "chain": "Kette",
  "conversion ratio {a}: a converter": "Konversionsrate {a}: ein Konverter",
  "conversion ratio {a}: a breeder": "Konversionsrate {a}: ein Brüter",
  "conversion ratio ≈ η − 1 − lost = {a}: breeds": "Konversionsrate ≈ η − 1 − verloren = {a}: brütet",
  "conversion ratio ≈ η − 1 − lost = {a}: breeds, makes more fuel than it burns": "Konversionsrate ≈ η − 1 − verloren = {a}: brütet, erzeugt mehr Brennstoff als er verbrennt",
  "conversion ratio ≈ η − 1 − lost = {a}: converts": "Konversionsrate ≈ η − 1 − verloren = {a}: konvertiert",
  "conversion ratio ≈ η − 1 − lost = {a}: converts, makes less fuel than it burns": "Konversionsrate ≈ η − 1 − verloren = {a}: konvertiert, erzeugt weniger Brennstoff als er verbrennt",
  "electron": "Elektron",
  "fast neutrons": "schnelle Neutronen",
  "fertile": "Brutstoff",
  "fertile: barely splits": "Brutstoff: spaltet sich kaum",
  "fissile": "spaltbar",
  "fissile: splits easily": "spaltbar: spaltet sich leicht",
  "illustration": "Illustration",
  "lost": "verloren",
  "lost: water, steel, poisons, leakage": "verloren: Wasser, Stahl, Gifte, Leckage",
  "made {a}": "erzeugt {a}",
  "neutrons out per neutron absorbed in the fuel": "Neutronen pro im Brennstoff absorbiertem Neutron",
  "neutrons per absorption": "Neutronen pro Absorption",
  "next fission": "nächste Spaltung",
  "next fission: keeps the chain going": "nächste Spaltung: hält die Kette in Gang",
  "slow neutrons": "langsame Neutronen",
  "slow step: Np{#}, half-life {#} d": "langsamer Schritt: Np{#}, Halbwertszeit {#} d",
  "slow step: Pa{#}, half-life {#} d": "langsamer Schritt: Pa{#}, Halbwertszeit {#} d",
  "split": "gespalten",
  "split (fission products)": "gespalten (Spaltprodukte)",
  "the slow step is Np{#} (half-life {#} days)": "der langsame Schritt ist Np{#} (Halbwertszeit {#} Tage)",
  "the slow step is Pa{#} (half-life {#} days)": "der langsame Schritt ist Pa{#} (Halbwertszeit {#} Tage)",
  "{#} d": "{#} d",
  "{#} min": "{#} min",
  "{#} p": "{#} p",
  "{#} protons": "{#} Protonen",
  "{#}: breeding line": "{#}: Brutgrenze",
  "{a} % now {b}": "{a} % jetzt {b}",
  "{a} per absorption": "{a} pro Absorption",
  "{a} waiting: day {b}": "{a} wartet: Tag {b}",
  "{a} · fast neutrons": "{a} · schnelle Neutronen",
  "{a} · slow neutrons": "{a} · langsame Neutronen",
  "η = {a}": "η = {a}",
  "η ≈ {a}": "η ≈ {a}",
});
