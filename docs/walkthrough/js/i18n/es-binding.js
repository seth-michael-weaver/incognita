/* Spanish: binding (Chapter 3, why nuclei hold together) */
WT.es.ch.binding = {
  num: "Capítulo 3", title: "Por qué los núcleos se mantienen unidos", short: "Ligadura",
  html: `
<div class="step">
  <p>Más arriba en la curva significa más fuertemente ligado. Cada punto es un número másico A (la suma de protones y neutrones), y su altura es la energía que haría falta, por nucleón, para separar por completo ese núcleo. Arrastra A y lee el marcador: la parte central de la curva, en torno al hierro y el níquel, es la cima.</p>
  <div class="ctl"><label for="bi-a">Número másico A</label><input id="bi-a" type="range" data-bind="pick" data-instant min="2" max="260" step="1" value="56"><output data-show="pick" data-fmt="0"></output></div>
</div>
<div class="step">
  <p>Divide el uranio: los dos fragmentos quedan más arriba en la curva que el uranio del que vienen, de modo que los mismos nucleones acaban ligados con más fuerza y la diferencia sale como energía. Elige el fragmento más ligero; el más pesado es el resto de los 236 nucleones.</p>
  <div class="ctl"><label for="bi-f">A del fragmento más ligero</label><input id="bi-f" type="range" data-bind="frag" data-instant min="70" max="118" step="1" value="95"><output data-show="frag" data-fmt="0"></output></div>
  <p class="ctl-result" id="bi-split-out" aria-live="polite"></p>
  <p>Sea cual sea la división, son unos 200 MeV: decenas de millones de veces los pocos electronvoltios que da quemar una molécula de combustible.</p>
</div>
<div class="step">
  <p>Une dos núcleos ligeros en uno. Si el núcleo nuevo queda más arriba en la curva, se libera energía. Pasado el máximo, unir cuesta energía en lugar de liberarla.</p>
  <div class="ctl"><label for="bi-u">A de cada núcleo ligero</label><input id="bi-u" type="range" data-bind="fuse" data-instant min="2" max="60" step="1" value="2"><output data-show="fuse" data-fmt="0"></output></div>
  <p class="ctl-result" id="bi-fuse-out" aria-live="polite"></p>
</div>`,
};

Object.assign(WT.L.labels, {
  "mass number A →": "número másico A →",
  "binding energy per nucleon (MeV)": "energía de ligadura por nucleón (MeV)",
  "Ni{#}: most tightly bound": "Ni{#}: el más ligado",
  "measured masses (AME{#})": "masas medidas (AME{#})",
  "Fe{#}: {#} MeV per nucleon · {#} MeV in all": "Fe{#}: {#} MeV por nucleón · {#} MeV en total",
});
