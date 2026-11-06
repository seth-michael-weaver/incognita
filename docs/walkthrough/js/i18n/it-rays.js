/* Italian: rays (Alfa, beta, gamma e neutroni) */
WT.L.ch.rays = {
  num: "Lezione 2", title: "Alfa, beta, gamma e neutroni", short: "Radiazioni",
  html: `
<div class="step">
  <h3>Quattro tipi di radiazione</h3>
  <p>L'<em class="a">alfa</em> è un grumo pesante di due protoni e due neutroni. Il <b>beta</b> è un elettrone veloce. Il <em class="g">gamma</em> è luce, troppo energetica per essere vista. I <em class="n">neutroni</em> non hanno alcuna carica. Ciascuno viene fermato da cose diverse.</p>
</div>
<div class="step">
  <h3>Carta e alluminio</h3>
  <p>Le particelle alfa sono grosse e cariche, quindi urtano subito gli atomi: un foglio di carta le ferma. Gli elettroni beta vanno più lontano, ma anche loro si fermano in pochi millimetri di alluminio.</p>
  <div class="btns"><button class="btn ghost" data-act="sh_paper" aria-pressed="true">Carta</button><button class="btn ghost" data-act="sh_al" aria-pressed="false">Alluminio</button></div>
</div>
<div class="step">
  <h3>Raggi gamma: dimezzati, mai azzerati</h3>
  <p>I raggi gamma non hanno carica e di solito passano accanto agli atomi. Ogni centimetro di piombo dà a ciascuno la stessa probabilità di essere fermato, quindi ogni strato dimezza ciò che resta. Il fascio si affievolisce ma non arriva mai del tutto a zero.</p>
  <div class="ctl"><label for="ry-pb">Piombo (cm)</label><input id="ry-pb" type="range" data-bind="pb" data-instant min="0" max="5" step="0.1" value="1"><output data-show="pb" data-fmt="1"></output></div>
</div>
<div class="step">
  <h3>Neutroni: il piombo non basta</h3>
  <p>Un neutrone che rimbalza su un pesante nucleo di piombo è una pallina da ping-pong che colpisce una palla da bowling: conserva la sua velocità. L'idrogeno dell'acqua pesa quanto un neutrone, quindi ogni urto lo rallenta, finché è abbastanza lento da essere catturato.</p>
  <div class="btns"><button class="btn ghost" data-act="nm_pb" aria-pressed="true">Piombo</button><button class="btn ghost" data-act="nm_water" aria-pressed="false">Acqua</button></div>
  <div class="ctl"><label for="ry-nx">Spessore (cm)</label><input id="ry-nx" type="range" data-bind="nx" data-instant min="0" max="60" step="1" value="30"><output data-show="nx" data-fmt="0"></output></div>
</div>
<div class="step">
  <h3>Costruisci uno schermo</h3>
  <p>Impila strati finché tutti e quattro i fasci sono fermati. I raggi gamma non scendono mai esattamente a zero, solo a una frazione minuscola.</p>
  <div class="btns"><button class="btn ghost" data-act="add_paper">+ Carta</button><button class="btn ghost" data-act="add_al">+ Alluminio</button><button class="btn ghost" data-act="add_pb">+ Piombo</button><button class="btn ghost" data-act="add_water">+ Acqua</button><button class="btn" data-act="clear">Svuota</button></div>
</div>`,
};

Object.assign(WT.L.labels, {
  "alpha": "alfa",
  "beta": "beta",
  "gamma": "gamma",
  "neutron": "neutrone",
  "paper": "carta",
  "aluminium {#} mm": "alluminio {#} mm",
  "Al {#} mm": "Al {#} mm",
  "lead {#} cm": "piombo {#} cm",
  "water {#} cm": "acqua {#} cm",
  "no shield": "nessuno schermo",
  "stopped": "fermati",
  "all through": "passano tutti",
  "{#} % through": "passa il {#} %",
  "{#} in {#}": "{#} su {#}",
  "{#} in {#} million": "{#} su {#} milioni",
  "{#} in a billion": "{#} su un miliardo",
  "drag ↔": "trascina ↔",
  "all four stopped": "tutti e quattro fermati",
  "all four beams stopped": "tutti e quattro i fasci fermati",
  "flash = stopped inside the shield": "lampo = fermato nello schermo",
  "each source fires a steady beam": "ogni sorgente emette un fascio continuo",
  "flash = stopped": "lampo = fermato",
  "four beams": "quattro fasci",
  "not to scale": "non in scala",
  "gamma rays (caesium{#})": "raggi gamma (cesio{#})",
  "cm of lead": "cm di piombo",
  "share still going": "frazione che passa ancora",
  "through: all · halved every {#} mm": "passano: tutti · metà ogni {#} mm",
  "through: {#} % · halved every {#} mm": "passa: {#} % · metà ogni {#} mm",
  "through: {#} in {#} · halved every {#} mm": "passa: {#} su {#} · metà ogni {#} mm",
  "gets through: {#} % · halved every {#} mm of lead": "passa: {#} % · dimezzato ogni {#} mm di piombo",
  "gets through: {#} in {#} · halved every {#} mm of lead": "passa: {#} su {#} · dimezzato ogni {#} mm di piombo",
  "counted: {#} of {#}": "contati: {#} su {#}",
  "through {#} % · back {#} % · caught {#} %": "passano {#} % · indietro {#} % · catturati {#} %",
  "got through {#} % · bounced back {#} % · slowed and caught {#} %": "passati {#} % · rimbalzati indietro {#} % · rallentati e catturati {#} %",
  "bright = fast · dim = slowed": "chiaro = veloce · tenue = rallentato",
  "bright = fast neutron · red = hydrogen nucleus knocked away · green flash = swallowed": "chiaro = neutrone veloce · rosso = nucleo di idrogeno sbalzato via · lampo verde = catturato",
  "simplified model": "modello semplificato",
});
