/* Spanish: spectrum (Reactores rápidos y térmicos) */
WT.L.ch.spectrum = {
  num: "Lección 1", title: "Reactores rápidos y térmicos", short: "Rápido o térmico",
  html: `
<div class="step">
  <h3>Lo rápidos que van los neutrones</h3>
  <p>Los neutrones nacen rápidos, cerca de 2 MeV. En un reactor de agua rebotan contra el hidrógeno hasta ir tan lentos como los propios átomos del agua: <b>térmicos</b>. Un reactor rápido no tiene moderador, así que siguen siendo rápidos. Desliza entre los dos.</p>
  <div class="ctl"><label for="spc-m1">Moderación</label><input id="spc-m1" type="range" data-bind="mod" data-instant min="0" max="1" step="0.01" value="1"><output data-show="mod" data-fmt="2"></output></div>
</div>
<div class="step">
  <h3>Neutrones de sobra</h3>
  <p><i>η</i> es cuántos neutrones devuelve un núcleo de combustible por cada neutrón que absorbe. Uno mantiene la cadena; para generar combustible nuevo hace falta un segundo de sobra, así que <i>η</i> claramente por encima de 2. El plutonio-239 solo lo consigue con neutrones rápidos.</p>
  <div class="ctl"><label for="spc-m2">Moderación</label><input id="spc-m2" type="range" data-bind="mod" data-instant min="0" max="1" step="0.01" value="0"><output data-show="mod" data-fmt="2"></output></div>
</div>
<div class="step">
  <h3>Quemar los restos</h3>
  <p>Los restos pesados como el americio casi siempre se limitan a tragarse los neutrones lentos y volverse más pesados. Los neutrones rápidos fisionan una parte mucho mayor de ellos, así que un reactor rápido puede quemarlos.</p>
  <div class="ctl"><label for="spc-m3">Moderación</label><input id="spc-m3" type="range" data-bind="mod" data-instant min="0" max="1" step="0.01" value="0"><output data-show="mod" data-fmt="2"></output></div>
</div>
<div class="step">
  <h3>El precio</h3>
  <p>Un neutrón lento tiene muchas más probabilidades de causar una fisión: a 1 MeV el blanco es cientos de veces más pequeño. Por eso un núcleo rápido necesita un combustible mucho más rico, en torno a un 15–25 % de plutonio en lugar de un 3–5 % de uranio-235.</p>
  <div class="ctl"><label for="spc-m4">Moderación</label><input id="spc-m4" type="range" data-bind="mod" data-instant min="0" max="1" step="0.01" value="1"><output data-show="mod" data-fmt="2"></output></div>
</div>`,
};

Object.assign(WT.L.labels, {
  "water: neutrons slow down": "agua: los neutrones se frenan",
  "water reactor: hydrogen slows the neutrons": "reactor de agua: el hidrógeno frena los neutrones",
  "sodium: they stay fast": "sodio: siguen rápidos",
  "fast reactor: sodium barely slows them": "reactor rápido: el sodio apenas los frena",
  "partly moderated": "parcialmente moderado",
  "{#} % split": "{#} % se fisiona",
  "sodium": "sodio",
  "no moderator (sodium)": "sin moderador (sodio)",
  "water": "agua",
  "thermal": "térmico",
  "resonances": "resonancias",
  "slowing down (resonances)": "moderación (resonancias)",
  "fast": "rápido",
  "{#} eV": "{#} eV",
  "{#} keV": "{#} keV",
  "{#} MeV": "{#} MeV",
  "neutron energy →": "energía del neutrón →",
  "born ~{#} MeV": "nacen a ~{#} MeV",
  "born near {#} MeV": "nacen cerca de {#} MeV",
  "η = {#}: one to continue, one to breed": "η = {#}: uno para seguir, otro para regenerar",
  "average η: U{#} {#} · Pu{#} {#}": "η media: U{#} {#} · Pu{#} {#}",
  "averaged over this spectrum:  η(U{#}) ≈ {#}   η(Pu{#}) ≈ {#}": "promedio en este espectro:  η(U{#}) ≈ {#}   η(Pu{#}) ≈ {#}",
  "{#} b": "{#} b",
  "Pu{#} fission target": "blanco de fisión del Pu{#}",
  "Pu{#} fission cross section (target size)": "sección eficaz de fisión del Pu{#} (tamaño del blanco)",
  "{#} MeV: a target ~{#} times smaller": "{#} MeV: un blanco ~{#} veces menor",
  "at {#} MeV the target is about {#} times smaller than at {#} eV": "a {#} MeV el blanco es unas {#} veces menor que a {#} eV",
  "most neutrons end up thermal": "la mayoría acaban térmicos",
  "most neutrons are slowed all the way to thermal": "la mayoría de los neutrones se frenan hasta la energía térmica",
  "most stay between {#} keV and {#} MeV": "la mayoría siguen entre {#} keV y {#} MeV",
  "most neutrons stay between {#} keV and {#} MeV": "la mayoría de los neutrones siguen entre {#} keV y {#} MeV",
  "many linger at in-between energies": "muchos se quedan en energías intermedias",
  "many neutrons linger at in-between energies": "muchos neutrones se quedan en energías intermedias",
  "thermal ≈ {#} eV, ~{#} km/s": "térmico ≈ {#} eV, ~{#} km/s",
  "thermal: kT ≈ {#} eV in hot water, about {#} km/s": "térmico: kT ≈ {#} eV en agua caliente, unos {#} km/s",
  "the rest are captured and grow heavier": "los demás capturan y se hacen más pesados",
  "the rest are captured: the nucleus just grows heavier": "el resto son capturas: el núcleo solo se vuelve más pesado",
  "illustrative shapes": "formas ilustrativas",
});
