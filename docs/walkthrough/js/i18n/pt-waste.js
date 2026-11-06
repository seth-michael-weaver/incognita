/* Portuguese (pt-PT): waste (O combustível irradiado ao longo do tempo) */
WT.L.ch.waste = {
  num: "Lição 1", title: "O combustível irradiado ao longo do tempo", short: "Combustível irradiado",
  html: `
<div class="step">
  <h3>O que sai do reator</h3>
  <p>Depois de quatro ou cinco anos no núcleo, uma pastilha de combustível continua a ser sobretudo urânio. Alguns por cento são <b>produtos de fissão</b>, os átomos cindidos. Cerca de 1 % é plutónio, e um vestígio são <b>actinídeos menores</b> mais pesados, como o amerício.</p>
  <div class="btns"><button class="btn" data-act="sort">Separar os átomos</button></div>
</div>
<div class="step">
  <h3>Os primeiros séculos</h3>
  <p>A curva compara a perigosidade do combustível irradiado, se fosse ingerido, com a do minério de urânio de que foi feito. De início dominam os produtos de fissão, mas a maioria tem períodos de semidesintegração de cerca de 30 anos: ao fim de uns 300 anos já desceram abaixo do minério.</p>
  <div class="ctl"><label for="wst-t1">Anos após a descarga</label><input id="wst-t1" type="range" data-bind="lt" data-instant min="0" max="6" step="0.01" value="1.5"><output data-show="yr" data-fmt="0"></output></div>
</div>
<div class="step">
  <h3>Depois, o plutónio</h3>
  <p>O que resta é plutónio e amerício, com períodos de semidesintegração de séculos a dezenas de milhares de anos. São eles que mantêm o combustível irradiado acima do nível do minério durante mais de cem mil anos.</p>
  <div class="ctl"><label for="wst-t2">Anos após a descarga</label><input id="wst-t2" type="range" data-bind="lt" data-instant min="0" max="6" step="0.01" value="4"><output data-show="yr" data-fmt="0"></output></div>
</div>
<div class="step">
  <h3>Reciclar e transmutar</h3>
  <p>Retira o plutónio e queima-o como combustível novo, e o tempo desce para cerca de dez mil anos. Cinde também os actinídeos menores em reatores rápidos, e só ficam os produtos de fissão: algumas centenas de anos.</p>
  <div class="btns"><button class="btn ghost" data-act="rp" aria-pressed="false">Reciclar o plutónio</button><button class="btn ghost" data-act="tm" aria-pressed="false">Transmutar os actinídeos menores</button></div>
</div>`,
};

Object.assign(WT.L.labels, {
  "Sort the atoms": "Separar os átomos",
  "Mix them again": "Voltar a misturar",
  "uranium": "urânio",
  "fission products": "produtos de fissão",
  "plutonium": "plutónio",
  "minor actinides": "actinídeos menores",
  "americium": "amerício",
  "fission prod.": "prod. de fissão",
  "minor act.": "act. menores",
  "a used fuel pellet, {#} atoms": "uma pastilha usada, {#} átomos",
  "a used fuel pellet, {#} atoms shown": "uma pastilha de combustível usada, {#} átomos representados",
  "the glow: fission products are the most radioactive": "o brilho: os produtos de fissão são os mais radioativos",
  "the glow: the fission products are by far the most radioactive part": "o brilho: os produtos de fissão são, de longe, a parte mais radioativa",
  "spent fuel": "combustível irradiado",
  "spent fuel, one tonne": "combustível irradiado, uma tonelada",
  "the ore": "o minério",
  "the ore it was made from": "o minério de origem",
  "1 yr": "1 ano",
  "{#} yr": "{#} anos",
  "1 million": "1 milhão",
  "{#} million": "{#} milhões",
  "uranium ore level": "nível do minério",
  "the uranium ore it was made from": "o minério de urânio de origem",
  "years after unloading (log scale) →": "anos após a descarga (escala log.) →",
  "hazard vs ore (log)": "perigosidade / minério (log.)",
  "hazard if swallowed, relative to the ore (log scale)": "perigosidade se ingerido, relativa ao minério (escala log.)",
  "Am, Cm, Np": "Am, Cm, Np",
  "americium, curium…": "amerício, cúrio…",
  "{#} years: {#} × the ore": "{#} anos: {#} × o minério",
  "below the ore it came from": "abaixo do minério de origem",
  "mostly from fission products": "sobretudo dos produtos de fissão",
  "mostly from plutonium": "sobretudo do plutónio",
  "mostly from americium": "sobretudo do amerício",
  "recycle + transmute": "reciclar + transmutar",
  "recycle Pu and transmute minor actinides": "reciclar o Pu e transmutar os actinídeos menores",
  "plutonium recycled": "plutónio reciclado",
  "plutonium recycled, minor actinides in the waste": "plutónio reciclado, actinídeos menores nos resíduos",
  "only minor actinides removed": "só os actinídeos menores retirados",
  "minor actinides removed, plutonium left in": "actinídeos menores retirados, plutónio mantido",
  "spent fuel as it is": "combustível irradiado tal como está",
  "spent fuel kept as it is": "combustível irradiado guardado tal como está",
  "reaches the ore level after ~{#} years": "atinge o nível do minério após ~{#} anos",
  "illustrative shape (after OECD-NEA)": "forma ilustrativa (segundo a NEA da OCDE)",
});
