/* French: dose (Dose de rayonnement) */
WT.L.ch.dose = {
  num: "Leçon 3", title: "Dose de rayonnement", short: "Dose",
  html: `
<div class="step">
  <h3>Ce que mesure un sievert</h3>
  <p>La dose est d'abord de l'énergie absorbée par kilogramme de corps. Le <b>sievert</b> pondère ensuite cette énergie par le mal qu'elle fait : la même énergie apportée par des particules alpha compte vingt fois plus que par des rayons gamma, car elle est concentrée en quelques traces denses.</p>
  <div class="btns"><button class="btn ghost" data-act="rg" aria-pressed="true">Rayons gamma</button><button class="btn ghost" data-act="ra" aria-pressed="false">Particules alpha</button></div>
</div>
<div class="step">
  <h3>Les doses de tous les jours</h3>
  <p>Chaque graduation de cette tour vaut dix fois celle du dessous. Faites glisser la perle lumineuse pour comparer : un scanner du thorax équivaut à la dose de plusieurs milliers de bananes, une année de rayonnement naturel à quelques dizaines de vols.</p>
  <div class="ctl"><label for="ds-l">Dose</label><input id="ds-l" type="range" data-bind="ld" data-instant min="-7" max="1" step="0.02" value="-2.15"><output class="ds-out"></output></div>
</div>
<div class="step">
  <h3>Faites le compte de votre année</h3>
  <p>Chacun reçoit environ 2,4 millisieverts par an de la nature, surtout du radon, un gaz qui sort du sol. Ajoutez vos vols, vos examens et votre altitude.</p>
  <div class="ctl"><label for="ds-f">Vols transatlantiques</label><input id="ds-f" type="range" data-bind="fl" data-instant min="0" max="40" step="1" value="4"><output data-show="fl" data-fmt="0"></output></div>
  <div class="ctl"><label for="ds-ct">Scanners du thorax</label><input id="ds-ct" type="range" data-bind="ct" data-instant min="0" max="3" step="1" value="0"><output data-show="ct" data-fmt="0"></output></div>
  <div class="ctl"><label for="ds-h">Altitude du domicile (m)</label><input id="ds-h" type="range" data-bind="alt" data-instant min="0" max="3500" step="50" value="300"><output data-show="alt" data-fmt="0"></output></div>
</div>
<div class="step">
  <h3>Une forte dose d'un seul coup</h3>
  <p>En dessous d'environ 100 millisieverts, un éventuel risque de cancer supplémentaire est trop faible pour être mesuré ; les règles de sûreté supposent qu'il croît en proportion de la dose. Vers un sievert reçu d'un coup, les cellules sont touchées si souvent que le mal des rayons commence.</p>
  <div class="ctl"><label for="ds-a">Dose reçue d'un coup</label><input id="ds-a" type="range" data-bind="la" data-instant min="-3" max="1" step="0.02" value="-1"><output class="ds-out2"></output></div>
</div>`,
};

Object.assign(WT.L.labels, {
  /* step 1: tissue */
  "cell nuclei in a patch of body": "noyaux de cellules d'un bout de corps",
  "cell nuclei in a patch of body tissue": "noyaux de cellules dans un fragment de tissu",
  "{#} milligray of alpha: a few cells hit hard": "{#} milligray d'alpha : quelques cellules durement touchées",
  "{#} milligray of gamma: about one track per cell": "{#} milligray de gamma : environ une trace par cellule",
  "same energy · counts as {#} millisieverts": "même énergie · compte pour {#} millisieverts",
  "counts as {#} millisievert": "compte pour {#} millisievert",
  "illustration": "illustration",
  /* step 2: the ladder */
  "eating a banana  ·  {#} µSv": "manger une banane  ·  {#} µSv",
  "dental X-ray  ·  {#} µSv": "radio dentaire  ·  {#} µSv",
  "chest X-ray  ·  {#} µSv": "radio du thorax  ·  {#} µSv",
  "flight across the Atlantic  ·  {#} µSv": "vol transatlantique  ·  {#} µSv",
  "a year of natural background  ·  {#} mSv": "un an de rayonnement naturel  ·  {#} mSv",
  "chest CT scan  ·  {#} mSv": "scanner du thorax  ·  {#} mSv",
  "yearly limit for radiation workers  ·  {#} mSv": "limite annuelle des travailleurs exposés  ·  {#} mSv",
  "a year on the Kerala coast (high spots)  ·  {#} mSv": "un an sur la côte du Kerala (points chauds)  ·  {#} mSv",
  "a year in the highest Ramsar homes  ·  {#} mSv": "un an dans les maisons les plus exposées de Ramsar  ·  {#} mSv",
  "at once: radiation sickness begins  ·  {#} Sv": "d'un coup : début du mal des rayons  ·  {#} Sv",
  "at once: about half die untreated  ·  {#} Sv": "d'un coup : environ la moitié meurt sans soins  ·  {#} Sv",
  "banana  ·  {#} µSv": "banane  ·  {#} µSv",
  "Atlantic flight  ·  {#} µSv": "vol transatlantique  ·  {#} µSv",
  "{#} yr background  ·  {#} mSv": "{#} an naturel  ·  {#} mSv",
  "chest CT  ·  {#} mSv": "scanner thorax  ·  {#} mSv",
  "worker limit/yr  ·  {#} mSv": "limite travailleur/an  ·  {#} mSv",
  "Kerala, {#} yr  ·  {#} mSv": "Kerala, {#} an  ·  {#} mSv",
  "Ramsar, {#} yr  ·  {#} mSv": "Ramsar, {#} an  ·  {#} mSv",
  "{#} Sv at once  ·  {#} Sv": "{#} Sv d'un coup  ·  {#} Sv",
  "{#}–{#} Sv at once  ·  {#} Sv": "{#}–{#} Sv d'un coup  ·  {#} Sv",
  "{#} µSv: the dose of {#} bananas": "{#} µSv : la dose de {#} bananes",
  "{#} µSv: the dose of {#} thousand bananas": "{#} µSv : la dose de {#} mille bananes",
  "{#} µSv: {#} bananas, or {#} flights": "{#} µSv : {#} bananes, ou {#} vols",
  "{#} µSv: {#} thousand bananas, or {#} flights": "{#} µSv : {#} mille bananes, ou {#} vols",
  "{#} µSv: {#} million bananas, or {#} flights": "{#} µSv : {#} millions de bananes, ou {#} vols",
  "{#} µSv: {#} bananas, or {#} thousand flights": "{#} µSv : {#} bananes, ou {#} mille vols",
  "{#} µSv: {#} thousand bananas, or {#} thousand flights": "{#} µSv : {#} mille bananes, ou {#} mille vols",
  "{#} µSv: {#} million bananas, or {#} thousand flights": "{#} µSv : {#} millions de bananes, ou {#} mille vols",
  "{#} mSv: {#} bananas, or {#} flights": "{#} mSv : {#} bananes, ou {#} vols",
  "{#} mSv: {#} thousand bananas, or {#} flights": "{#} mSv : {#} mille bananes, ou {#} vols",
  "{#} mSv: {#} million bananas, or {#} flights": "{#} mSv : {#} millions de bananes, ou {#} vols",
  "{#} mSv: {#} bananas, or {#} thousand flights": "{#} mSv : {#} bananes, ou {#} mille vols",
  "{#} mSv: {#} thousand bananas, or {#} thousand flights": "{#} mSv : {#} mille bananes, ou {#} mille vols",
  "{#} mSv: {#} million bananas, or {#} thousand flights": "{#} mSv : {#} millions de bananes, ou {#} mille vols",
  "{#} Sv: {#} bananas, or {#} flights": "{#} Sv : {#} bananes, ou {#} vols",
  "{#} Sv: {#} thousand bananas, or {#} flights": "{#} Sv : {#} mille bananes, ou {#} vols",
  "{#} Sv: {#} million bananas, or {#} flights": "{#} Sv : {#} millions de bananes, ou {#} vols",
  "{#} Sv: {#} bananas, or {#} thousand flights": "{#} Sv : {#} bananes, ou {#} mille vols",
  "{#} Sv: {#} thousand bananas, or {#} thousand flights": "{#} Sv : {#} mille bananes, ou {#} mille vols",
  "{#} Sv: {#} million bananas, or {#} thousand flights": "{#} Sv : {#} millions de bananes, ou {#} mille vols",
  "{#} µSv: {#} bananas, {#} flights or {#} years of background": "{#} µSv : {#} bananes, {#} vols ou {#} ans de rayonnement naturel",
  "{#} µSv: {#} thousand bananas, {#} flights or {#} years of background": "{#} µSv : {#} mille bananes, {#} vols ou {#} ans de rayonnement naturel",
  "{#} µSv: {#} million bananas, {#} flights or {#} years of background": "{#} µSv : {#} millions de bananes, {#} vols ou {#} ans de rayonnement naturel",
  "{#} µSv: {#} bananas, {#} thousand flights or {#} years of background": "{#} µSv : {#} bananes, {#} mille vols ou {#} ans de rayonnement naturel",
  "{#} µSv: {#} thousand bananas, {#} thousand flights or {#} years of background": "{#} µSv : {#} mille bananes, {#} mille vols ou {#} ans de rayonnement naturel",
  "{#} µSv: {#} million bananas, {#} thousand flights or {#} years of background": "{#} µSv : {#} millions de bananes, {#} mille vols ou {#} ans de rayonnement naturel",
  "{#} mSv: {#} bananas, {#} flights or {#} years of background": "{#} mSv : {#} bananes, {#} vols ou {#} ans de rayonnement naturel",
  "{#} mSv: {#} thousand bananas, {#} flights or {#} years of background": "{#} mSv : {#} mille bananes, {#} vols ou {#} ans de rayonnement naturel",
  "{#} mSv: {#} million bananas, {#} flights or {#} years of background": "{#} mSv : {#} millions de bananes, {#} vols ou {#} ans de rayonnement naturel",
  "{#} mSv: {#} bananas, {#} thousand flights or {#} years of background": "{#} mSv : {#} bananes, {#} mille vols ou {#} ans de rayonnement naturel",
  "{#} mSv: {#} thousand bananas, {#} thousand flights or {#} years of background": "{#} mSv : {#} mille bananes, {#} mille vols ou {#} ans de rayonnement naturel",
  "{#} mSv: {#} million bananas, {#} thousand flights or {#} years of background": "{#} mSv : {#} millions de bananes, {#} mille vols ou {#} ans de rayonnement naturel",
  "{#} Sv: {#} bananas, {#} flights or {#} years of background": "{#} Sv : {#} bananes, {#} vols ou {#} ans de rayonnement naturel",
  "{#} Sv: {#} thousand bananas, {#} flights or {#} years of background": "{#} Sv : {#} mille bananes, {#} vols ou {#} ans de rayonnement naturel",
  "{#} Sv: {#} million bananas, {#} flights or {#} years of background": "{#} Sv : {#} millions de bananes, {#} vols ou {#} ans de rayonnement naturel",
  "{#} Sv: {#} bananas, {#} thousand flights or {#} years of background": "{#} Sv : {#} bananes, {#} mille vols ou {#} ans de rayonnement naturel",
  "{#} Sv: {#} thousand bananas, {#} thousand flights or {#} years of background": "{#} Sv : {#} mille bananes, {#} mille vols ou {#} ans de rayonnement naturel",
  "{#} Sv: {#} million bananas, {#} thousand flights or {#} years of background": "{#} Sv : {#} millions de bananes, {#} mille vols ou {#} ans de rayonnement naturel",
  "typical values": "valeurs typiques",
  /* step 3: your year */
  "average {#}": "moyenne {#}",
  "world average {#} mSv": "moyenne mondiale {#} mSv",
  "worker limit {#}": "limite travailleur {#}",
  "worker limit {#} mSv": "limite travailleur {#} mSv",
  "radon in the air  {#}": "radon dans l'air  {#}",
  "radon  {#}": "radon  {#}",
  "rocks and soil  {#}": "roches et sols  {#}",
  "ground  {#}": "sol  {#}",
  "food and water  {#}": "aliments et eau  {#}",
  "food  {#}": "aliments  {#}",
  "cosmic rays at {#} m  {#}": "rayons cosmiques à {#} m  {#}",
  "cosmic rays  {#}": "rayons cosmiques  {#}",
  "cosmic  {#}": "cosmique  {#}",
  "{#} flights  {#}": "{#} vols  {#}",
  "flights  {#}": "vols  {#}",
  "{#} chest CT  {#}": "{#} scanner thorax  {#}",
  "CT  {#}": "scanner  {#}",
  "your year: {#} mSv": "votre année : {#} mSv",
  "more than the yearly worker limit": "plus que la limite annuelle des travailleurs",
  "{#} times the world average": "{#} fois la moyenne mondiale",
  "close to the world average": "proche de la moyenne mondiale",
  /* step 4: dose at once */
  "tracks through each cell nucleus: about {#}": "traces par noyau de cellule : environ {#}",
  "tracks through each cell nucleus: about {#} (a few drawn)": "traces par noyau de cellule : environ {#} (quelques-unes dessinées)",
  "tracks through each cell nucleus: about {#} thousand (a few drawn)": "traces par noyau de cellule : environ {#} mille (quelques-unes dessinées)",
  "no effect seen": "aucun effet observé",
  "risk assumed": "risque supposé",
  "small added risk assumed": "léger risque supplémentaire supposé",
  "sickness": "mal des rayons",
  "lethal": "létal",
  "often lethal": "souvent létal",
  "{#} µSv at once: any extra risk too small to measure": "{#} µSv d'un coup : risque éventuel trop faible pour être mesuré",
  "{#} mSv at once: any extra risk too small to measure": "{#} mSv d'un coup : risque éventuel trop faible pour être mesuré",
  "{#} mSv at once: no sickness; risk assumed to rise with dose": "{#} mSv d'un coup : pas de maladie ; risque supposé croître avec la dose",
  "{#} Sv at once: no sickness; risk assumed to rise with dose": "{#} Sv d'un coup : pas de maladie ; risque supposé croître avec la dose",
  "{#} Sv at once: radiation sickness: nausea, low blood counts": "{#} Sv d'un coup : mal des rayons, nausées, chute des globules",
  "{#} Sv at once: about half die without treatment": "{#} Sv d'un coup : environ la moitié meurt sans traitement",
});
