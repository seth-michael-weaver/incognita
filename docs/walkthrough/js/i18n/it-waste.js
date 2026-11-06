/* Italian: waste (Il combustibile esaurito nel tempo) */
WT.L.ch.waste = {
  num: "Lezione 1", title: "Il combustibile esaurito nel tempo", short: "Combustibile esaurito",
  html: `
<div class="step">
  <h3>Che cosa esce dal reattore</h3>
  <p>Dopo quattro o cinque anni nel nocciolo, una pastiglia di combustibile è ancora in gran parte uranio. Qualche percento sono <b>prodotti di fissione</b>, gli atomi spezzati. Circa l'1 % è plutonio, e una traccia sono <b>attinidi minori</b> più pesanti, come l'americio.</p>
  <div class="btns"><button class="btn" data-act="sort">Ordina gli atomi</button></div>
</div>
<div class="step">
  <h3>I primi secoli</h3>
  <p>La curva confronta la pericolosità del combustibile esaurito, se ingerito, con quella del minerale di uranio da cui è stato ricavato. All'inizio dominano i prodotti di fissione, ma la maggior parte ha un tempo di dimezzamento di circa 30 anni: dopo circa 300 anni sono scesi sotto il livello del minerale.</p>
  <div class="ctl"><label for="wst-t1">Anni dallo scarico</label><input id="wst-t1" type="range" data-bind="lt" data-instant min="0" max="6" step="0.01" value="1.5"><output data-show="yr" data-fmt="0"></output></div>
</div>
<div class="step">
  <h3>Poi il plutonio</h3>
  <p>Restano plutonio e americio, con tempi di dimezzamento che vanno da secoli a decine di migliaia di anni. Tengono il combustibile esaurito sopra il livello del minerale per oltre centomila anni.</p>
  <div class="ctl"><label for="wst-t2">Anni dallo scarico</label><input id="wst-t2" type="range" data-bind="lt" data-instant min="0" max="6" step="0.01" value="4"><output data-show="yr" data-fmt="0"></output></div>
</div>
<div class="step">
  <h3>Riciclare e trasmutare</h3>
  <p>Estrai il plutonio e brucialo come nuovo combustibile: il tempo scende a circa diecimila anni. Fissiona anche gli attinidi minori in reattori veloci, e restano solo i prodotti di fissione: qualche centinaio di anni.</p>
  <div class="btns"><button class="btn ghost" data-act="rp" aria-pressed="false">Ricicla il plutonio</button><button class="btn ghost" data-act="tm" aria-pressed="false">Trasmuta gli attinidi minori</button></div>
</div>`,
};

Object.assign(WT.L.labels, {
  "{#} million": "{#} milioni",
  "Sort the atoms": "Ordina gli atomi",
  "Mix them again": "Mescolali di nuovo",
  "uranium": "uranio",
  "fission products": "prodotti di fissione",
  "plutonium": "plutonio",
  "minor actinides": "attinidi minori",
  "americium": "americio",
  "fission prod.": "prod. di fissione",
  "minor act.": "att. minori",
  "a used fuel pellet, {#} atoms": "una pastiglia esaurita, {#} atomi",
  "a used fuel pellet, {#} atoms shown": "una pastiglia di combustibile esaurito, {#} atomi mostrati",
  "the glow: fission products are the most radioactive": "il bagliore: i prodotti di fissione, i più radioattivi",
  "the glow: the fission products are by far the most radioactive part": "il bagliore: i prodotti di fissione sono di gran lunga la parte più radioattiva",
  "spent fuel": "combustibile esaurito",
  "spent fuel, one tonne": "combustibile esaurito, una tonnellata",
  "the ore": "il minerale",
  "the ore it was made from": "il minerale di partenza",
  "{#} yr": "{#} a",
  "1 million": "1 milione",
  "uranium ore level": "livello del minerale",
  "the uranium ore it was made from": "il minerale di uranio di partenza",
  "years after unloading (log scale) →": "anni dallo scarico (scala log.) →",
  "hazard vs ore (log)": "pericolosità / minerale (log.)",
  "hazard if swallowed, relative to the ore (log scale)": "pericolosità se ingerito, rispetto al minerale (scala log.)",
  "Am, Cm, Np": "Am, Cm, Np",
  "americium, curium…": "americio, curio…",
  "{#} years: {#} × the ore": "{#} anni: {#} × il minerale",
  "below the ore it came from": "sotto il minerale di partenza",
  "mostly from fission products": "soprattutto dai prodotti di fissione",
  "mostly from plutonium": "soprattutto dal plutonio",
  "mostly from americium": "soprattutto dall'americio",
  "recycle + transmute": "riciclo + trasmutazione",
  "recycle Pu and transmute minor actinides": "riciclo del Pu e trasmutazione degli attinidi minori",
  "plutonium recycled": "plutonio riciclato",
  "plutonium recycled, minor actinides in the waste": "plutonio riciclato, attinidi minori nelle scorie",
  "only minor actinides removed": "rimossi solo gli attinidi minori",
  "minor actinides removed, plutonium left in": "attinidi minori rimossi, plutonio lasciato",
  "spent fuel as it is": "combustibile esaurito così com'è",
  "spent fuel kept as it is": "combustibile esaurito conservato così com'è",
  "reaches the ore level after ~{#} years": "raggiunge il livello del minerale dopo ~{#} anni",
  "reaches the ore level after ~170,000 years": "raggiunge il livello del minerale dopo ~170.000 anni",
  "reaches the ore level after ~160,000 years": "raggiunge il livello del minerale dopo ~160.000 anni",
  "reaches the ore level after ~10,000 years": "raggiunge il livello del minerale dopo ~10.000 anni",
  "illustrative shape (after OECD-NEA)": "forma illustrativa (da OCSE-NEA)",
});
