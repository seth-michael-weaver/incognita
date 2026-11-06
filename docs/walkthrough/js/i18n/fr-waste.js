/* French: waste (Le combustible usé au fil du temps) */
WT.L.ch.waste = {
  num: "Leçon 1", title: "Le combustible usé au fil du temps", short: "Combustible usé",
  html: `
<div class="step">
  <h3>Ce qui ressort du réacteur</h3>
  <p>Après quatre ou cinq ans dans le cœur, une pastille de combustible reste surtout de l'uranium. Quelques pour cent sont des <b>produits de fission</b>, les atomes scindés. Environ 1 % est du plutonium, et une trace correspond à des <b>actinides mineurs</b> plus lourds, comme l'américium.</p>
  <div class="btns"><button class="btn" data-act="sort">Trier les atomes</button></div>
</div>
<div class="step">
  <h3>Les premiers siècles</h3>
  <p>La courbe compare la nocivité du combustible usé, s'il était avalé, à celle du minerai d'uranium dont il est issu. Au début, les produits de fission dominent, mais la plupart ont une demi-vie d'environ 30 ans : au bout de quelque 300 ans, ils sont passés sous le niveau du minerai.</p>
  <div class="ctl"><label for="wst-t1">Années après le déchargement</label><input id="wst-t1" type="range" data-bind="lt" data-instant min="0" max="6" step="0.01" value="1.5"><output data-show="yr" data-fmt="0"></output></div>
</div>
<div class="step">
  <h3>Puis le plutonium</h3>
  <p>Restent le plutonium et l'américium, dont les demi-vies vont de quelques siècles à des dizaines de milliers d'années. Ils maintiennent le combustible usé au-dessus du niveau du minerai pendant plus de cent mille ans.</p>
  <div class="ctl"><label for="wst-t2">Années après le déchargement</label><input id="wst-t2" type="range" data-bind="lt" data-instant min="0" max="6" step="0.01" value="4"><output data-show="yr" data-fmt="0"></output></div>
</div>
<div class="step">
  <h3>Recycler et transmuter</h3>
  <p>Retirez le plutonium et brûlez-le comme nouveau combustible : la durée tombe à environ dix mille ans. Fissionnez aussi les actinides mineurs dans des réacteurs à neutrons rapides, et il ne reste que les produits de fission : quelques centaines d'années.</p>
  <div class="btns"><button class="btn ghost" data-act="rp" aria-pressed="false">Recycler le plutonium</button><button class="btn ghost" data-act="tm" aria-pressed="false">Transmuter les actinides mineurs</button></div>
</div>`,
};

Object.assign(WT.L.labels, {
  "Sort the atoms": "Trier les atomes",
  "Mix them again": "Les mélanger à nouveau",
  "uranium": "uranium",
  "fission products": "produits de fission",
  "plutonium": "plutonium",
  "minor actinides": "actinides mineurs",
  "americium": "américium",
  "fission prod.": "prod. de fission",
  "minor act.": "act. mineurs",
  "a used fuel pellet, {#} atoms": "une pastille usée, {#} atomes",
  "a used fuel pellet, {#} atoms shown": "une pastille de combustible usé, {#} atomes représentés",
  "the glow: fission products are the most radioactive": "la lueur : les produits de fission, les plus radioactifs",
  "the glow: the fission products are by far the most radioactive part": "la lueur : les produits de fission sont de loin la partie la plus radioactive",
  "spent fuel": "combustible usé",
  "spent fuel, one tonne": "combustible usé, une tonne",
  "the ore": "le minerai",
  "the ore it was made from": "le minerai d'origine",
  "1 yr": "1 an",
  "{#} yr": "{#} ans",
  "{#} million": "{#} million",
  "uranium ore level": "niveau du minerai",
  "the uranium ore it was made from": "le minerai d'uranium d'origine",
  "years after unloading (log scale) →": "années après le déchargement (échelle log) →",
  "hazard vs ore (log)": "nocivité / minerai (log)",
  "hazard if swallowed, relative to the ore (log scale)": "nocivité en cas d'ingestion, rapportée au minerai (échelle log)",
  "Am, Cm, Np": "Am, Cm, Np",
  "americium, curium…": "américium, curium…",
  "{#} years: {#} × the ore": "{#} ans : {#} × le minerai",
  "below the ore it came from": "sous le niveau du minerai d'origine",
  "mostly from fission products": "surtout due aux produits de fission",
  "mostly from plutonium": "surtout due au plutonium",
  "mostly from americium": "surtout due à l'américium",
  "recycle + transmute": "recyclage + transmutation",
  "recycle Pu and transmute minor actinides": "recyclage du Pu et transmutation des actinides mineurs",
  "plutonium recycled": "plutonium recyclé",
  "plutonium recycled, minor actinides in the waste": "plutonium recyclé, actinides mineurs dans les déchets",
  "only minor actinides removed": "seuls les actinides mineurs retirés",
  "minor actinides removed, plutonium left in": "actinides mineurs retirés, plutonium laissé",
  "spent fuel as it is": "combustible usé tel quel",
  "spent fuel kept as it is": "combustible usé conservé tel quel",
  "reaches the ore level after ~{#} years": "atteint le niveau du minerai après ~{#} ans",
  "illustrative shape (after OECD-NEA)": "forme illustrative (d'après l'AEN de l'OCDE)",
});
