/* Italian: dose (Dose di radiazione) */
WT.L.ch.dose = {
  num: "Lezione 3", title: "Dose di radiazione", short: "Dose",
  html: `
<div class="step">
  <h3>Che cosa misura un sievert</h3>
  <p>La dose parte dall'energia assorbita per chilogrammo di corpo. Il <b>sievert</b> pesa poi quell'energia in base al danno che fa: la stessa energia portata da particelle alfa conta venti volte più che con i raggi gamma, perché è concentrata in poche tracce dense.</p>
  <div class="btns"><button class="btn ghost" data-act="rg" aria-pressed="true">Raggi gamma</button><button class="btn ghost" data-act="ra" aria-pressed="false">Particelle alfa</button></div>
</div>
<div class="step">
  <h3>Dosi di tutti i giorni</h3>
  <p>Ogni tacca di questa torre vale dieci volte quella sotto. Trascina la perla luminosa per confrontare: una TAC al torace è la dose di molte migliaia di banane, un anno di fondo naturale qualche decina di voli.</p>
  <div class="ctl"><label for="ds-l">Dose</label><input id="ds-l" type="range" data-bind="ld" data-instant min="-7" max="1" step="0.02" value="-2.15"><output class="ds-out"></output></div>
</div>
<div class="step">
  <h3>Somma il tuo anno</h3>
  <p>Tutti ricevono circa 2,4 millisievert all'anno dalla natura, soprattutto dal radon, un gas che sale dal suolo. Aggiungi i tuoi voli, i tuoi esami e la tua altitudine.</p>
  <div class="ctl"><label for="ds-f">Voli transatlantici</label><input id="ds-f" type="range" data-bind="fl" data-instant min="0" max="40" step="1" value="4"><output data-show="fl" data-fmt="0"></output></div>
  <div class="ctl"><label for="ds-ct">TAC al torace</label><input id="ds-ct" type="range" data-bind="ct" data-instant min="0" max="3" step="1" value="0"><output data-show="ct" data-fmt="0"></output></div>
  <div class="ctl"><label for="ds-h">Altitudine di casa (m)</label><input id="ds-h" type="range" data-bind="alt" data-instant min="0" max="3500" step="50" value="300"><output data-show="alt" data-fmt="0"></output></div>
</div>
<div class="step">
  <h3>Una dose forte tutta in una volta</h3>
  <p>Sotto circa 100 millisievert, un eventuale rischio di cancro in più è troppo piccolo per essere misurato; le norme di sicurezza assumono che cresca in proporzione alla dose. Attorno a un sievert ricevuto in una volta, le cellule vengono colpite così spesso che inizia la malattia da radiazioni.</p>
  <div class="ctl"><label for="ds-a">Dose in una volta</label><input id="ds-a" type="range" data-bind="la" data-instant min="-3" max="1" step="0.02" value="-1"><output class="ds-out2"></output></div>
</div>`,
};

Object.assign(WT.L.labels, {
  /* step 1: tissue */
  "cell nuclei in a patch of body": "nuclei cellulari in un lembo di corpo",
  "cell nuclei in a patch of body tissue": "nuclei cellulari in un lembo di tessuto",
  "{#} milligray of alpha: a few cells hit hard": "{#} milligray di alfa: poche cellule colpite duramente",
  "{#} milligray of gamma: about one track per cell": "{#} milligray di gamma: circa una traccia per cellula",
  "same energy · counts as {#} millisieverts": "stessa energia · conta come {#} millisievert",
  "counts as {#} millisievert": "conta come {#} millisievert",
  "illustration": "illustrazione",
  /* step 2: the ladder */
  "eating a banana  ·  {#} µSv": "mangiare una banana  ·  {#} µSv",
  "dental X-ray  ·  {#} µSv": "radiografia dentale  ·  {#} µSv",
  "chest X-ray  ·  {#} µSv": "radiografia del torace  ·  {#} µSv",
  "flight across the Atlantic  ·  {#} µSv": "volo transatlantico  ·  {#} µSv",
  "a year of natural background  ·  {#} mSv": "un anno di fondo naturale  ·  {#} mSv",
  "chest CT scan  ·  {#} mSv": "TAC al torace  ·  {#} mSv",
  "yearly limit for radiation workers  ·  {#} mSv": "limite annuo per i lavoratori esposti  ·  {#} mSv",
  "a year on the Kerala coast (high spots)  ·  {#} mSv": "un anno sulla costa del Kerala (punti più alti)  ·  {#} mSv",
  "a year in the highest Ramsar homes  ·  {#} mSv": "un anno nelle case più esposte di Ramsar  ·  {#} mSv",
  "at once: radiation sickness begins  ·  {#} Sv": "in una volta: inizia la malattia da radiazioni  ·  {#} Sv",
  "at once: about half die untreated  ·  {#} Sv": "in una volta: senza cure muore circa la metà  ·  {#} Sv",
  "banana  ·  {#} µSv": "banana  ·  {#} µSv",
  "Atlantic flight  ·  {#} µSv": "volo transatlantico  ·  {#} µSv",
  "{#} yr background  ·  {#} mSv": "fondo di {#} anno  ·  {#} mSv",
  "chest CT  ·  {#} mSv": "TAC torace  ·  {#} mSv",
  "worker limit/yr  ·  {#} mSv": "limite lavoratori/anno  ·  {#} mSv",
  "Kerala, {#} yr  ·  {#} mSv": "Kerala, {#} anno  ·  {#} mSv",
  "Ramsar, {#} yr  ·  {#} mSv": "Ramsar, {#} anno  ·  {#} mSv",
  "{#} Sv at once  ·  {#} Sv": "{#} Sv in una volta  ·  {#} Sv",
  "{#}–{#} Sv at once  ·  {#} Sv": "{#}–{#} Sv in una volta  ·  {#} Sv",
  "{#} µSv: the dose of {#} bananas": "{#} µSv: la dose di {#} banane",
  "{#} µSv: the dose of {#} thousand bananas": "{#} µSv: la dose di {#} mila banane",
  "typical values": "valori tipici",
  /* step 3: your year */
  "average {#}": "media {#}",
  "world average {#} mSv": "media mondiale {#} mSv",
  "worker limit {#}": "limite lavoratori {#}",
  "worker limit {#} mSv": "limite lavoratori {#} mSv",
  "radon in the air  {#}": "radon nell'aria  {#}",
  "radon  {#}": "radon  {#}",
  "rocks and soil  {#}": "rocce e suolo  {#}",
  "ground  {#}": "suolo  {#}",
  "food and water  {#}": "cibo e acqua  {#}",
  "food  {#}": "cibo  {#}",
  "cosmic rays at {#} m  {#}": "raggi cosmici a {#} m  {#}",
  "cosmic rays  {#}": "raggi cosmici  {#}",
  "cosmic  {#}": "cosmici  {#}",
  "{#} flights  {#}": "{#} voli  {#}",
  "flights  {#}": "voli  {#}",
  "{#} chest CT  {#}": "{#} TAC torace  {#}",
  "CT  {#}": "TAC  {#}",
  "your year: {#} mSv": "il tuo anno: {#} mSv",
  "more than the yearly worker limit": "più del limite annuo per i lavoratori",
  "{#} times the world average": "{#} volte la media mondiale",
  "close to the world average": "vicino alla media mondiale",
  /* step 4: dose at once */
  "tracks through each cell nucleus: about {#}": "tracce per nucleo cellulare: circa {#}",
  "tracks through each cell nucleus: about {#} (a few drawn)": "tracce per nucleo cellulare: circa {#} (ne disegniamo poche)",
  "tracks through each cell nucleus: about {#} thousand (a few drawn)": "tracce per nucleo cellulare: circa {#} mila (ne disegniamo poche)",
  "no effect seen": "nessun effetto osservato",
  "risk assumed": "rischio ipotizzato",
  "small added risk assumed": "piccolo rischio aggiuntivo ipotizzato",
  "sickness": "malattia",
  "lethal": "letale",
  "often lethal": "spesso letale",
  "{#} µSv at once: any extra risk too small to measure": "{#} µSv in una volta: un eventuale rischio è troppo piccolo da misurare",
  "{#} mSv at once: any extra risk too small to measure": "{#} mSv in una volta: un eventuale rischio è troppo piccolo da misurare",
  "{#} mSv at once: no sickness; risk assumed to rise with dose": "{#} mSv in una volta: nessuna malattia; si assume che il rischio cresca con la dose",
  "{#} Sv at once: no sickness; risk assumed to rise with dose": "{#} Sv in una volta: nessuna malattia; si assume che il rischio cresca con la dose",
  "{#} Sv at once: radiation sickness: nausea, low blood counts": "{#} Sv in una volta: malattia da radiazioni, nausea, calo dei globuli",
  "{#} Sv at once: about half die without treatment": "{#} Sv in una volta: senza cure muore circa la metà",
  /* step 2 bottom line: every unit x banana size x flight size */
  "{#} µSv: {#} bananas, or {#} flights": "{#} µSv: {#} banane o {#} voli",
  "{#} µSv: {#} bananas, or {#} thousand flights": "{#} µSv: {#} banane o {#} mila voli",
  "{#} µSv: {#} thousand bananas, or {#} flights": "{#} µSv: {#} mila banane o {#} voli",
  "{#} µSv: {#} thousand bananas, or {#} thousand flights": "{#} µSv: {#} mila banane o {#} mila voli",
  "{#} µSv: {#} million bananas, or {#} flights": "{#} µSv: {#} milioni di banane o {#} voli",
  "{#} µSv: {#} million bananas, or {#} thousand flights": "{#} µSv: {#} milioni di banane o {#} mila voli",
  "{#} mSv: {#} bananas, or {#} flights": "{#} mSv: {#} banane o {#} voli",
  "{#} mSv: {#} bananas, or {#} thousand flights": "{#} mSv: {#} banane o {#} mila voli",
  "{#} mSv: {#} thousand bananas, or {#} flights": "{#} mSv: {#} mila banane o {#} voli",
  "{#} mSv: {#} thousand bananas, or {#} thousand flights": "{#} mSv: {#} mila banane o {#} mila voli",
  "{#} mSv: {#} million bananas, or {#} flights": "{#} mSv: {#} milioni di banane o {#} voli",
  "{#} mSv: {#} million bananas, or {#} thousand flights": "{#} mSv: {#} milioni di banane o {#} mila voli",
  "{#} Sv: {#} bananas, or {#} flights": "{#} Sv: {#} banane o {#} voli",
  "{#} Sv: {#} bananas, or {#} thousand flights": "{#} Sv: {#} banane o {#} mila voli",
  "{#} Sv: {#} thousand bananas, or {#} flights": "{#} Sv: {#} mila banane o {#} voli",
  "{#} Sv: {#} thousand bananas, or {#} thousand flights": "{#} Sv: {#} mila banane o {#} mila voli",
  "{#} Sv: {#} million bananas, or {#} flights": "{#} Sv: {#} milioni di banane o {#} voli",
  "{#} Sv: {#} million bananas, or {#} thousand flights": "{#} Sv: {#} milioni di banane o {#} mila voli",
  "{#} µSv: {#} bananas, {#} flights or {#} years of background": "{#} µSv: {#} banane, {#} voli o {#} anni di fondo naturale",
  "{#} µSv: {#} bananas, {#} thousand flights or {#} years of background": "{#} µSv: {#} banane, {#} mila voli o {#} anni di fondo naturale",
  "{#} µSv: {#} thousand bananas, {#} flights or {#} years of background": "{#} µSv: {#} mila banane, {#} voli o {#} anni di fondo naturale",
  "{#} µSv: {#} thousand bananas, {#} thousand flights or {#} years of background": "{#} µSv: {#} mila banane, {#} mila voli o {#} anni di fondo naturale",
  "{#} µSv: {#} million bananas, {#} flights or {#} years of background": "{#} µSv: {#} milioni di banane, {#} voli o {#} anni di fondo naturale",
  "{#} µSv: {#} million bananas, {#} thousand flights or {#} years of background": "{#} µSv: {#} milioni di banane, {#} mila voli o {#} anni di fondo naturale",
  "{#} mSv: {#} bananas, {#} flights or {#} years of background": "{#} mSv: {#} banane, {#} voli o {#} anni di fondo naturale",
  "{#} mSv: {#} bananas, {#} thousand flights or {#} years of background": "{#} mSv: {#} banane, {#} mila voli o {#} anni di fondo naturale",
  "{#} mSv: {#} thousand bananas, {#} flights or {#} years of background": "{#} mSv: {#} mila banane, {#} voli o {#} anni di fondo naturale",
  "{#} mSv: {#} thousand bananas, {#} thousand flights or {#} years of background": "{#} mSv: {#} mila banane, {#} mila voli o {#} anni di fondo naturale",
  "{#} mSv: {#} million bananas, {#} flights or {#} years of background": "{#} mSv: {#} milioni di banane, {#} voli o {#} anni di fondo naturale",
  "{#} mSv: {#} million bananas, {#} thousand flights or {#} years of background": "{#} mSv: {#} milioni di banane, {#} mila voli o {#} anni di fondo naturale",
  "{#} Sv: {#} bananas, {#} flights or {#} years of background": "{#} Sv: {#} banane, {#} voli o {#} anni di fondo naturale",
  "{#} Sv: {#} bananas, {#} thousand flights or {#} years of background": "{#} Sv: {#} banane, {#} mila voli o {#} anni di fondo naturale",
  "{#} Sv: {#} thousand bananas, {#} flights or {#} years of background": "{#} Sv: {#} mila banane, {#} voli o {#} anni di fondo naturale",
  "{#} Sv: {#} thousand bananas, {#} thousand flights or {#} years of background": "{#} Sv: {#} mila banane, {#} mila voli o {#} anni di fondo naturale",
  "{#} Sv: {#} million bananas, {#} flights or {#} years of background": "{#} Sv: {#} milioni di banane, {#} voli o {#} anni di fondo naturale",
  "{#} Sv: {#} million bananas, {#} thousand flights or {#} years of background": "{#} Sv: {#} milioni di banane, {#} mila voli o {#} anni di fondo naturale",
});
