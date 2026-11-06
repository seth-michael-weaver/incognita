/* Spanish: breeding (La reproducción de combustible) */
WT.L.ch.breeding = {
  num: "Lección 1", title: "La reproducción de combustible", short: "Reproducción",
  html: `
<div class="step">
  <h3>Lo fértil se vuelve fisible</h3>
  <p>El uranio-238 apenas se fisiona, pero puede capturar un neutrón. Dos desintegraciones beta después (cada vez, un neutrón del núcleo se convierte en protón) se ha convertido en plutonio-239, que se fisiona con facilidad. El torio-232 hace lo mismo y se convierte en uranio-233.</p>
  <div class="btns"><button class="btn ghost" data-act="bcU" aria-pressed="true">Uranio-238</button> <button class="btn ghost" data-act="bcT" aria-pressed="false">Torio-232</button></div>
</div>
<div class="step">
  <h3>El balance de neutrones</h3>
  <p>Cada neutrón absorbido en el combustible fisible devuelve <i>η</i> neutrones nuevos. Uno debe provocar la fisión siguiente y algunos se pierden; lo que sobra puede reproducir combustible. Con uranio-235 y neutrones lentos solo se forman unos 0,6 núcleos fisibles nuevos por cada uno quemado.</p>
  <div class="btns"><button class="btn ghost" data-act="bfU5" aria-pressed="true">U-235</button> <button class="btn ghost" data-act="bfP9" aria-pressed="false">Pu-239</button> <button class="btn ghost" data-act="bfU3" aria-pressed="false">U-233</button></div>
  <div class="btns"><button class="btn ghost" data-act="bsT" aria-pressed="true">Neutrones lentos</button> <button class="btn ghost" data-act="bsF" aria-pressed="false">Neutrones rápidos</button></div>
</div>
<div class="step">
  <h3>Los neutrones rápidos reproducen</h3>
  <p>Para reproducir, un neutrón debe continuar la cadena y al menos otro debe crear combustible nuevo, así que <i>η</i> tiene que superar 2 por más que las pérdidas. El plutonio-239 en un reactor rápido da unos 2,4: margen de sobra.</p>
  <div class="ctl"><label for="br-l1">Neutrones perdidos</label><input id="br-l1" type="range" data-bind="L" data-instant min="0.05" max="0.8" step="0.01" value="0.2"><output data-show="L" data-fmt="2"></output></div>
</div>
<div class="step">
  <h3>Torio con neutrones lentos</h3>
  <p>Con neutrones lentos el plutonio-239 da solo unos 2,1, pero el uranio-233 da 2,29. Ese margen permite a un reactor de torio reproducir con neutrones lentos, si desperdicia muy pocos. Baja las pérdidas hasta que reproduzca.</p>
  <div class="ctl"><label for="br-l2">Neutrones perdidos</label><input id="br-l2" type="range" data-bind="L" data-instant min="0.05" max="0.8" step="0.01" value="0.35"><output data-show="L" data-fmt="2"></output></div>
</div>
<div class="step">
  <h3>La razón de conversión</h3>
  <p>La razón de conversión es el número de núcleos fisibles creados por cada núcleo fisible quemado. Por debajo de 1 el combustible se agota poco a poco (un convertidor, como los reactores de agua actuales); por encima de 1 el reactor termina con más combustible del que tenía al empezar (un reproductor).</p>
  <div class="btns"><button class="btn ghost" data-act="bfU5" aria-pressed="true">U-235</button> <button class="btn ghost" data-act="bfP9" aria-pressed="false">Pu-239</button> <button class="btn ghost" data-act="bfU3" aria-pressed="false">U-233</button></div>
  <div class="btns"><button class="btn ghost" data-act="bsT" aria-pressed="true">Neutrones lentos</button> <button class="btn ghost" data-act="bsF" aria-pressed="false">Neutrones rápidos</button></div>
</div>`,
};

Object.assign(WT.L.labels, {
  "illustration": "ilustración",
  // scene 1: the chain
  "{#} protons": "{#} protones",
  "{#} p": "{#} p",
  "fertile": "fértil",
  "fertile: barely splits": "fértil: apenas se fisiona",
  "fissile": "fisible",
  "fissile: splits easily": "fisible: se fisiona fácilmente",
  "+ n": "+ n",
  "catch": "captura",
  "{#} min": "{#} min",
  "{#} d": "{#} d",
  "e⁻": "e⁻",
  "electron": "electrón",
  "antineutrino": "antineutrino",
  "{a} waiting: day {b}": "{a} en espera: día {b}",
  "a batch of {a} waiting · day {b}": "un lote de {a} en espera · día {b}",
  "{a} % now {b}": "{a} % ya es {b}",
  "after {#} weeks, {#} % has become Pu{#}": "tras {#} semanas, el {#} % ya es Pu{#}",
  "after {#} months, {#} % has become U{#}": "tras {#} meses, el {#} % ya es U{#}",
  "slow step: Np{#}, half-life {#} d": "paso lento: Np{#}, semivida {#} d",
  "slow step: Pa{#}, half-life {#} d": "paso lento: Pa{#}, semivida {#} d",
  "the slow step is Np{#} (half-life {#} days)": "el paso lento es el Np{#} (semivida {#} días)",
  "the slow step is Pa{#} (half-life {#} days)": "el paso lento es el Pa{#} (semivida {#} días)",
  // scenes 2-4: the neutron budget
  "slow neutrons": "neutrones lentos",
  "fast neutrons": "neutrones rápidos",
  "next fission": "fisión siguiente",
  "next fission: keeps the chain going": "fisión siguiente: mantiene la cadena",
  "U{#} → Pu{#}": "U{#} → Pu{#}",
  "Th{#} → U{#}": "Th{#} → U{#}",
  "breeds: U{#} → Pu{#}": "reproduce: U{#} → Pu{#}",
  "breeds: Th{#} → U{#}": "reproduce: Th{#} → U{#}",
  "lost": "perdidos",
  "lost: water, steel, poisons, leakage": "perdidos: agua, acero, venenos, fugas",
  "{a} per absorption": "{a} por absorción",
  "chain": "cadena",
  "breed": "reproduce",
  "η = {a}": "η = {a}",
  "η ≈ {a}": "η ≈ {a}",
  "{#}: breeding line": "{#}: umbral de reproducción",
  "neutrons per absorption": "neutrones por absorción",
  "neutrons out per neutron absorbed in the fuel": "neutrones emitidos por neutrón absorbido en el combustible",
  "conversion ratio ≈ η − {#} − lost = {a}: breeds": "razón de conversión ≈ η − {#} − pérdidas = {a}: reproduce",
  "conversion ratio ≈ η − {#} − lost = {a}: breeds, makes more fuel than it burns": "razón de conversión ≈ η − {#} − pérdidas = {a}: reproduce, crea más combustible del que quema",
  "conversion ratio ≈ η − {#} − lost = {a}: converts": "razón de conversión ≈ η − {#} − pérdidas = {a}: convierte",
  "conversion ratio ≈ η − {#} − lost = {a}: converts, makes less fuel than it burns": "razón de conversión ≈ η − {#} − pérdidas = {a}: convierte, crea menos combustible del que quema",
  // scene 5: conversion ratio
  "Th{#}": "Th{#}",
  "U{#} (fertile)": "U{#} (fértil)",
  "Th{#} (fertile)": "Th{#} (fértil)",
  "split": "fisionados",
  "split (fission products)": "fisionados (productos de fisión)",
  "burned {a}": "quemados {a}",
  "made {a}": "creados {a}",
  "{a} · slow neutrons": "{a} · neutrones lentos",
  "{a} · fast neutrons": "{a} · neutrones rápidos",
  "conversion ratio {a}: a breeder": "razón de conversión {a}: un reproductor",
  "conversion ratio {a}: a converter": "razón de conversión {a}: un convertidor",
});
