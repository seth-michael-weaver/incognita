/* Spanish: waste (El combustible gastado con el tiempo) */
WT.L.ch.waste = {
  num: "Lección 1", title: "El combustible gastado con el tiempo", short: "Combustible gastado",
  html: `
<div class="step">
  <h3>Lo que sale del reactor</h3>
  <p>Tras cuatro o cinco años en el núcleo, una pastilla de combustible sigue siendo sobre todo uranio. Un pequeño porcentaje son <b>productos de fisión</b>, los átomos partidos. Alrededor del 1 % es plutonio, y una traza son <b>actínidos minoritarios</b> más pesados, como el americio.</p>
  <div class="btns"><button class="btn" data-act="sort">Ordenar los átomos</button></div>
</div>
<div class="step">
  <h3>Los primeros siglos</h3>
  <p>La curva compara la peligrosidad del combustible gastado, si se ingiriera, con la del mineral de uranio del que se fabricó. Al principio dominan los productos de fisión, pero la mayoría tienen periodos de semidesintegración de unos 30 años: al cabo de unos 300 años ya han caído por debajo del mineral.</p>
  <div class="ctl"><label for="wst-t1">Años tras la descarga</label><input id="wst-t1" type="range" data-bind="lt" data-instant min="0" max="6" step="0.01" value="1.5"><output data-show="yr" data-fmt="0"></output></div>
</div>
<div class="step">
  <h3>Después, el plutonio</h3>
  <p>Lo que queda es plutonio y americio, con periodos de semidesintegración de siglos a decenas de miles de años. Mantienen el combustible gastado por encima del nivel del mineral durante más de cien mil años.</p>
  <div class="ctl"><label for="wst-t2">Años tras la descarga</label><input id="wst-t2" type="range" data-bind="lt" data-instant min="0" max="6" step="0.01" value="4"><output data-show="yr" data-fmt="0"></output></div>
</div>
<div class="step">
  <h3>Reciclar y transmutar</h3>
  <p>Separa el plutonio y quémalo como combustible nuevo, y el plazo baja a unos diez mil años. Fisiona además los actínidos minoritarios en reactores rápidos y solo quedan los productos de fisión: unos pocos cientos de años.</p>
  <div class="btns"><button class="btn ghost" data-act="rp" aria-pressed="false">Reciclar el plutonio</button><button class="btn ghost" data-act="tm" aria-pressed="false">Transmutar los actínidos minoritarios</button></div>
</div>`,
};

Object.assign(WT.L.labels, {
  "{#} million": "{#} millones",
  "Sort the atoms": "Ordenar los átomos",
  "Mix them again": "Mezclarlos de nuevo",
  "uranium": "uranio",
  "fission products": "productos de fisión",
  "plutonium": "plutonio",
  "minor actinides": "actínidos minoritarios",
  "americium": "americio",
  "fission prod.": "prod. de fisión",
  "minor act.": "act. minorit.",
  "a used fuel pellet, {#} atoms": "una pastilla gastada, {#} átomos",
  "a used fuel pellet, {#} atoms shown": "una pastilla de combustible gastado, se muestran {#} átomos",
  "the glow: fission products are the most radioactive": "el brillo: los productos de fisión, los más radiactivos",
  "the glow: the fission products are by far the most radioactive part": "el brillo: los productos de fisión son, con diferencia, la parte más radiactiva",
  "spent fuel": "combustible gastado",
  "spent fuel, one tonne": "combustible gastado, una tonelada",
  "the ore": "el mineral",
  "the ore it was made from": "el mineral de origen",
  "1 yr": "1 año",
  "{#} yr": "{#} años",
  "1 million": "1 millón",
  "uranium ore level": "nivel del mineral",
  "the uranium ore it was made from": "el mineral de uranio de origen",
  "years after unloading (log scale) →": "años tras la descarga (escala log.) →",
  "hazard vs ore (log)": "peligrosidad / mineral (log.)",
  "hazard if swallowed, relative to the ore (log scale)": "peligrosidad si se ingiere, relativa al mineral (escala log.)",
  "Am, Cm, Np": "Am, Cm, Np",
  "americium, curium…": "americio, curio…",
  "{#} years: {#} × the ore": "{#} años: {#} × el mineral",
  "below the ore it came from": "por debajo del mineral de origen",
  "mostly from fission products": "sobre todo por los productos de fisión",
  "mostly from plutonium": "sobre todo por el plutonio",
  "mostly from americium": "sobre todo por el americio",
  "recycle + transmute": "reciclar + transmutar",
  "recycle Pu and transmute minor actinides": "reciclar el Pu y transmutar los actínidos minoritarios",
  "plutonium recycled": "plutonio reciclado",
  "plutonium recycled, minor actinides in the waste": "plutonio reciclado, actínidos minoritarios en los residuos",
  "only minor actinides removed": "solo se retiran los actínidos minoritarios",
  "minor actinides removed, plutonium left in": "actínidos minoritarios retirados, el plutonio se queda",
  "spent fuel as it is": "combustible gastado tal cual",
  "spent fuel kept as it is": "combustible gastado guardado tal cual",
  "reaches the ore level after ~{#} years": "alcanza el nivel del mineral tras ~{#} años",
  "illustrative shape (after OECD-NEA)": "forma ilustrativa (según la NEA de la OCDE)",
});
