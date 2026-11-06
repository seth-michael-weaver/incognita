/* Spanish: halflife (Radiactividad y semivida) */
WT.L.ch.halflife = {
  num: "Lección 1", title: "Radiactividad y semivida", short: "Semivida",
  lead: "Algunos átomos son inestables: tarde o temprano su núcleo estalla, emite radiación y se convierte en otra cosa. Nadie puede decir cuándo le tocará a uno concreto, y aun así una muestra entera sigue un reloj tan fiable como el tuyo.",
  html: `
<div class="step">
  <h3>Una muestra que estalla al azar</h3>
  <p>Cada bola brillante es un núcleo inestable. Cualquiera puede estallar en cualquier momento, lanzar un destello de radiación y quedar como un átomo tranquilo y estable. Toca uno para hacerlo estallar.</p>
  <div class="btns"><button class="btn" data-act="refill">Muestra nueva</button></div>
</div>
<div class="step">
  <h3>La mitad, y otra vez la mitad</h3>
  <p>Nadie puede decir cuál será el siguiente, pero el conjunto es predecible: tras una <b>semivida</b> queda más o menos la mitad, tras dos una cuarta parte, luego una octava. Alarga o acorta la semivida.</p>
  <div class="ctl"><label for="hl-th">Semivida (segundos)</label><input id="hl-th" type="range" data-bind="Th" data-instant min="1" max="8" step="0.5" value="3"><output data-show="Th" data-fmt="1"></output></div>
  <div class="btns"><button class="btn ghost" data-act="refill">Muestra nueva</button></div>
</div>
<div class="step">
  <h3>Los núcleos no tienen memoria</h3>
  <p>Sigue a un superviviente. Por mucho que haya durado ya, su probabilidad de durar una semivida más sigue siendo de una entre dos: un núcleo no envejece.</p>
  <div class="btns"><button class="btn ghost" data-act="tag">Seguir a otro</button><button class="btn ghost" data-act="refill">Muestra nueva</button></div>
</div>
<div class="step">
  <h3>Semividas reales</h3>
  <p>Los isótopos reales van de días a miles de millones de años. En esta escala de tiempo estirada, cada uno cae por un precipicio en su propia semivida. Elige uno y arrastra el tiempo hacia delante.</p>
  <div class="btns"><button class="btn ghost" data-act="iso0" aria-pressed="false">Yodo-131</button><button class="btn ghost" data-act="iso1" aria-pressed="true">Cesio-137</button><button class="btn ghost" data-act="iso2" aria-pressed="false">Carbono-14</button><button class="btn ghost" data-act="iso3" aria-pressed="false">Uranio-238</button></div>
  <div class="ctl"><label for="hl-t1">Tiempo transcurrido</label><input id="hl-t1" type="range" data-bind="lt" data-instant min="3" max="17.8" step="0.02" value="8.98"><output class="hl-tout"></output></div>
</div>
<div class="step">
  <h3>Actividad: desintegraciones por segundo</h3>
  <p>Un gramo de cada uno, uno al lado del otro. Una semivida corta significa muchas desintegraciones por segundo, pero durante poco tiempo; una semivida larga brilla débilmente durante eras. Arrastra el tiempo y mira cómo se apagan las lámparas una a una.</p>
  <div class="ctl"><label for="hl-t2">Tiempo transcurrido</label><input id="hl-t2" type="range" data-bind="lt" data-instant min="3" max="17.8" step="0.02" value="4.94"><output class="hl-tout"></output></div>
</div>`,
};

Object.assign(WT.L.labels, {
  /* live sample */
  "survived {#} half-lives": "sobrevivió {#} semividas",
  "chance to last one more: {#} in {#}": "probabilidad de durar otra: {#} de {#}",
  "survived {#} half-lives · still {#} in {#}": "sobrevivió {#} semividas · sigue {#} de {#}",
  "it popped: follow another": "se desintegró: sigue a otro",
  "{#} of {#} still unstable": "{#} de {#} aún inestables",
  "1 half-life": "1 semivida",
  "{#} half-life": "{#} semivida",
  "half-lives →": "semividas →",
  "nuclei left": "núcleos restantes",
  "{#} of {#} left · half-life {#} s": "quedan {#} de {#} · semivida {#} s",
  "every survivor has the same 1-in-2 chance per half-life": "cada superviviente tiene la misma probabilidad, 1 de 2, por semivida",
  "every survivor has the same {#}-in{#} chance per half-life": "cada superviviente tiene la misma probabilidad, {#} de {#}, por semivida",
  "illustrative half-life": "semivida ilustrativa",
  /* time axis ticks */
  "{#} hour": "{#} hora",
  "{#} h": "{#} h",
  "{#} day": "{#} día",
  "{#} d": "{#} d",
  "{#} year": "{#} año",
  "{#} yr": "{#} años",
  "1000 years": "1000 años",
  "10³ yr": "10³ a",
  "10⁶ yr": "10⁶ a",
  "10⁹ yr": "10⁹ a",
  "{#}³ yr": "{#}³ a",
  "{#}⁶ yr": "{#}⁶ a",
  "{#}⁹ yr": "{#}⁹ a",
  "1 million years": "1 millón de años",
  "1 billion years": "mil millones de años",
  "drag": "arrastra",
  /* time strings (fmtT) */
  "{#} minutes": "{#} minutos",
  "{#} hours": "{#} horas",
  "{#} days": "{#} días",
  "{#} months": "{#} meses",
  "{#} years": "{#} años",
  "{#} thousand years": "{#} mil años",
  "{#} million years": "{#} millones de años",
  "{#} billion years": "{#} mil millones de años",
  /* real isotopes */
  "iodine{#} · half-life {#} days": "yodo{#} · semivida {#} días",
  "caesium{#} · half-life {#} years": "cesio{#} · semivida {#} años",
  "carbon{#} · half-life {#} years": "carbono{#} · semivida {#} años",
  "carbon-14 · half-life 5,700 years": "carbono-14 · semivida 5700 años",
  "uranium{#} · half-life {#} billion years": "uranio{#} · semivida {#} mil millones de años",
  "medicine, fission product": "medicina, producto de fisión",
  "fission product": "producto de fisión",
  "radiocarbon dating": "datación por radiocarbono",
  "natural uranium": "uranio natural",
  "all": "todo",
  "{#} % left after {#} minutes": "queda el {#} % tras {#} minutos",
  "{#} % left after {#} hours": "queda el {#} % tras {#} horas",
  "{#} % left after {#} days": "queda el {#} % tras {#} días",
  "{#} % left after {#} months": "queda el {#} % tras {#} meses",
  "{#} % left after {#} years": "queda el {#} % tras {#} años",
  "{#} % left after {#} thousand years": "queda el {#} % tras {#} mil años",
  "{#} % left after {#} million years": "queda el {#} % tras {#} millones de años",
  "{#} % left after {#} billion years": "queda el {#} % tras {#} mil millones de años",
  "under {#} % left after {#} minutes": "queda menos del {#} % tras {#} minutos",
  "under {#} % left after {#} hours": "queda menos del {#} % tras {#} horas",
  "under {#} % left after {#} days": "queda menos del {#} % tras {#} días",
  "under {#} % left after {#} months": "queda menos del {#} % tras {#} meses",
  "under {#} % left after {#} years": "queda menos del {#} % tras {#} años",
  "under {#} % left after {#} thousand years": "queda menos del {#} % tras {#} mil años",
  "under {#} % left after {#} million years": "queda menos del {#} % tras {#} millones de años",
  "under {#} % left after {#} billion years": "queda menos del {#} % tras {#} mil millones de años",
  /* activity of one gram */
  "iodine{#}": "yodo{#}",
  "caesium{#}": "cesio{#}",
  "carbon{#}": "carbono{#}",
  "uranium{#}": "uranio{#}",
  "½ {#} days": "½ {#} días",
  "½ {#} years": "½ {#} años",
  "½ 5,700 years": "½ 5700 años",
  "½ {#} billion years": "½ {#} mil millones de años",
  "½ {#} bn years": "½ {#} mil M años",
  "almost none": "casi nada",
  "{#} /s": "{#} /s",
  "~{#} /s": "~{#} /s",
  "{#}×{#}¹ /s": "{#}×{#}¹ /s",
  "{#}×{#}² /s": "{#}×{#}² /s",
  "{#}×{#}³ /s": "{#}×{#}³ /s",
  "{#}×{#}⁴ /s": "{#}×{#}⁴ /s",
  "{#}×{#}⁵ /s": "{#}×{#}⁵ /s",
  "{#}×{#}⁶ /s": "{#}×{#}⁶ /s",
  "{#}×{#}⁷ /s": "{#}×{#}⁷ /s",
  "{#}×{#}⁸ /s": "{#}×{#}⁸ /s",
  "{#}×{#}⁹ /s": "{#}×{#}⁹ /s",
  "{#}×{#}¹⁰ /s": "{#}×{#}¹⁰ /s",
  "{#}×{#}¹¹ /s": "{#}×{#}¹¹ /s",
  "{#}×{#}¹² /s": "{#}×{#}¹² /s",
  "{#}×{#}¹³ /s": "{#}×{#}¹³ /s",
  "{#}×{#}¹⁴ /s": "{#}×{#}¹⁴ /s",
  "{#}×{#}¹⁵ /s": "{#}×{#}¹⁵ /s",
  "{#}×{#}¹⁶ /s": "{#}×{#}¹⁶ /s",
  "pops per second (log)": "desintegraciones/s (log)",
  "pops per second, {#} gram (each line ×{#})": "desintegraciones por segundo, {#} gramo (cada línea ×{#})",
  "one gram of each, after {#} minutes": "un gramo de cada uno, tras {#} minutos",
  "one gram of each, after {#} hours": "un gramo de cada uno, tras {#} horas",
  "one gram of each, after {#} days": "un gramo de cada uno, tras {#} días",
  "one gram of each, after {#} months": "un gramo de cada uno, tras {#} meses",
  "one gram of each, after {#} years": "un gramo de cada uno, tras {#} años",
  "one gram of each, after {#} thousand years": "un gramo de cada uno, tras {#} mil años",
  "one gram of each, after {#} million years": "un gramo de cada uno, tras {#} millones de años",
  "one gram of each, after {#} billion years": "un gramo de cada uno, tras {#} mil millones de años",
});
