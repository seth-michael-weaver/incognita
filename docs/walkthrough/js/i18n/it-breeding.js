/* Italian: breeding (La fertilizzazione del combustibile) */
WT.L.ch.breeding = {
  num: "Lezione 1", title: "La fertilizzazione del combustibile", short: "Fertilizzazione",
  html: `
<div class="step">
  <h3>Da fertile a fissile</h3>
  <p>L'uranio-238 si scinde a fatica, ma può catturare un neutrone. Due decadimenti beta dopo (ogni volta un neutrone al suo interno diventa un protone) è diventato plutonio-239, che si scinde facilmente. Il torio-232 fa lo stesso e diventa uranio-233.</p>
  <div class="btns"><button class="btn ghost" data-act="bcU" aria-pressed="true">Uranio-238</button> <button class="btn ghost" data-act="bcT" aria-pressed="false">Torio-232</button></div>
</div>
<div class="step">
  <h3>Il bilancio neutronico</h3>
  <p>Ogni neutrone assorbito nel combustibile fissile ne restituisce <i>η</i> nuovi. Uno deve provocare la fissione successiva e alcuni vanno persi; quello che resta può fertilizzare. Con l'uranio-235 e neutroni lenti si producono solo circa 0,6 nuovi nuclei fissili per ogni nucleo bruciato.</p>
  <div class="btns"><button class="btn ghost" data-act="bfU5" aria-pressed="true">U-235</button> <button class="btn ghost" data-act="bfP9" aria-pressed="false">Pu-239</button> <button class="btn ghost" data-act="bfU3" aria-pressed="false">U-233</button></div>
  <div class="btns"><button class="btn ghost" data-act="bsT" aria-pressed="true">Neutroni lenti</button> <button class="btn ghost" data-act="bsF" aria-pressed="false">Neutroni veloci</button></div>
</div>
<div class="step">
  <h3>I neutroni veloci fertilizzano</h3>
  <p>Per fertilizzare, un neutrone deve proseguire la catena e almeno un altro deve produrre nuovo combustibile, quindi <i>η</i> deve superare 2 di più delle perdite. Il plutonio-239 in un reattore veloce dà circa 2,4: margine in abbondanza.</p>
  <div class="ctl"><label for="br-l1">Neutroni persi</label><input id="br-l1" type="range" data-bind="L" data-instant min="0.05" max="0.8" step="0.01" value="0.2"><output data-show="L" data-fmt="2"></output></div>
</div>
<div class="step">
  <h3>Il torio con neutroni lenti</h3>
  <p>Con neutroni lenti il plutonio-239 dà solo circa 2,1, ma l'uranio-233 dà 2,29. Questo margine permette a un reattore al torio di fertilizzare con neutroni lenti, se ne spreca pochissimi. Riduci le perdite finché fertilizza.</p>
  <div class="ctl"><label for="br-l2">Neutroni persi</label><input id="br-l2" type="range" data-bind="L" data-instant min="0.05" max="0.8" step="0.01" value="0.35"><output data-show="L" data-fmt="2"></output></div>
</div>
<div class="step">
  <h3>Rapporto di conversione</h3>
  <p>Il rapporto di conversione è il numero di nuclei fissili prodotti per ogni nucleo fissile bruciato. Sotto 1 il combustibile si esaurisce lentamente (un convertitore, come gli attuali reattori ad acqua); sopra 1 il reattore finisce con più combustibile di quanto ne avesse all'inizio (un autofertilizzante).</p>
  <div class="btns"><button class="btn ghost" data-act="bfU5" aria-pressed="true">U-235</button> <button class="btn ghost" data-act="bfP9" aria-pressed="false">Pu-239</button> <button class="btn ghost" data-act="bfU3" aria-pressed="false">U-233</button></div>
  <div class="btns"><button class="btn ghost" data-act="bsT" aria-pressed="true">Neutroni lenti</button> <button class="btn ghost" data-act="bsF" aria-pressed="false">Neutroni veloci</button></div>
</div>`,
};

Object.assign(WT.L.labels, {
  "illustration": "illustrazione",
  // scene 1: the chain
  "{#} protons": "{#} protoni",
  "{#} p": "{#} p",
  "fertile": "fertile",
  "fertile: barely splits": "fertile: si scinde a fatica",
  "fissile": "fissile",
  "fissile: splits easily": "fissile: si scinde facilmente",
  "+ n": "+ n",
  "catch": "cattura",
  "{#} min": "{#} min",
  "{#} d": "{#} g",
  "e⁻": "e⁻",
  "electron": "elettrone",
  "antineutrino": "antineutrino",
  "{a} waiting: day {b}": "{a} in attesa: giorno {b}",
  "a batch of {a} waiting · day {b}": "un lotto di {a} in attesa · giorno {b}",
  "{a} % now {b}": "{a} % già {b}",
  "after {#} weeks, {#} % has become Pu{#}": "dopo {#} settimane, il {#} % è diventato Pu{#}",
  "after {#} months, {#} % has become U{#}": "dopo {#} mesi, il {#} % è diventato U{#}",
  "slow step: Np{#}, half-life {#} d": "passo lento: Np{#}, emivita {#} g",
  "slow step: Pa{#}, half-life {#} d": "passo lento: Pa{#}, emivita {#} g",
  "the slow step is Np{#} (half-life {#} days)": "il passo lento è Np{#} (emivita {#} giorni)",
  "the slow step is Pa{#} (half-life {#} days)": "il passo lento è Pa{#} (emivita {#} giorni)",
  // scenes 2-4: the neutron budget
  "slow neutrons": "neutroni lenti",
  "fast neutrons": "neutroni veloci",
  "next fission": "fissione successiva",
  "next fission: keeps the chain going": "fissione successiva: mantiene la catena",
  "U{#} → Pu{#}": "U{#} → Pu{#}",
  "Th{#} → U{#}": "Th{#} → U{#}",
  "breeds: U{#} → Pu{#}": "fertilizza: U{#} → Pu{#}",
  "breeds: Th{#} → U{#}": "fertilizza: Th{#} → U{#}",
  "lost": "persi",
  "lost: water, steel, poisons, leakage": "persi: acqua, acciaio, veleni, fughe",
  "{a} per absorption": "{a} per assorbimento",
  "chain": "catena",
  "breed": "fertilizza",
  "η = {a}": "η = {a}",
  "η ≈ {a}": "η ≈ {a}",
  "{#}: breeding line": "{#}: soglia di fertilizzazione",
  "neutrons per absorption": "neutroni per assorbimento",
  "neutrons out per neutron absorbed in the fuel": "neutroni emessi per neutrone assorbito nel combustibile",
  "conversion ratio ≈ η − {#} − lost = {a}: breeds": "rapporto di conversione ≈ η − {#} − persi = {a}: fertilizza",
  "conversion ratio ≈ η − {#} − lost = {a}: breeds, makes more fuel than it burns": "rapporto di conversione ≈ η − {#} − persi = {a}: fertilizza, produce più combustibile di quanto ne bruci",
  "conversion ratio ≈ η − {#} − lost = {a}: converts": "rapporto di conversione ≈ η − {#} − persi = {a}: converte",
  "conversion ratio ≈ η − {#} − lost = {a}: converts, makes less fuel than it burns": "rapporto di conversione ≈ η − {#} − persi = {a}: converte, produce meno combustibile di quanto ne bruci",
  // scene 5: conversion ratio
  "Th{#}": "Th{#}",
  "U{#} (fertile)": "U{#} (fertile)",
  "Th{#} (fertile)": "Th{#} (fertile)",
  "split": "fissionati",
  "split (fission products)": "fissionati (prodotti di fissione)",
  "burned {a}": "bruciati {a}",
  "made {a}": "prodotti {a}",
  "{a} · slow neutrons": "{a} · neutroni lenti",
  "{a} · fast neutrons": "{a} · neutroni veloci",
  "conversion ratio {a}: a breeder": "rapporto di conversione {a}: autofertilizzante",
  "conversion ratio {a}: a converter": "rapporto di conversione {a}: convertitore",
});
