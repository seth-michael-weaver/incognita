/* Italian: chains (Catene di decadimento ed equilibrio) */
WT.L.ch.chains = {
  num: "Lezione 4", title: "Catene di decadimento ed equilibrio", short: "Catene di decadimento",
  html: `
<div class="step">
  <h3>Padre, figlio, nipote</h3>
  <p>Spesso anche il nuovo nucleo è instabile. Il padre decade in un figlio, che a sua volta decade in un nipote stabile. I figli si accumulano e poi svaniscono; quanto in alto arrivano dipende da quanto in fretta decadono rispetto al padre.</p>
  <div class="ctl"><label for="ch-t2">Tempo di dimezzamento del figlio (s)</label><input id="ch-t2" type="range" data-bind="T2" data-instant min="0.5" max="9" step="0.5" value="1.5"><output data-show="T2" data-fmt="1"></output></div>
  <div class="btns"><button class="btn ghost" data-act="refill">Nuovo campione</button></div>
</div>
<div class="step">
  <h3>Equilibrio secolare: radio e radon</h3>
  <p>Il radio-226 dura 1600 anni; suo figlio, il gas radon-222, appena 3,8 giorni. In un barattolo sigillato il radon si accumula finché decade alla stessa velocità con cui si forma: <i>A</i><sub>Rn</sub> = <i>A</i><sub>Ra</sub>(1 − e<sup>−λt</sup>), dove λ è la costante di decadimento del radon. Dopo qualche settimana i due decadono allo stesso ritmo.</p>
  <div class="btns"><button class="btn" data-act="vent">Apri il barattolo</button></div>
</div>
<div class="step">
  <h3>Equilibrio transitorio: la mucca al tecnezio</h3>
  <p>Gli ospedali ricevono una colonna di molibdeno-99 (66 ore) che produce di continuo tecnezio-99m (6 ore), il tracciante medico più usato. Ogni mattina si estrae il tecnezio, che poi ricresce seguendo il molibdeno che lentamente si esaurisce.</p>
  <div class="btns"><button class="btn" data-act="milk">Mungi il generatore</button><button class="btn ghost" data-act="genre">Nuovo generatore</button></div>
</div>
<div class="step">
  <h3>Lungo la catena dell'uranio</h3>
  <p>L'uranio-238 impiega quattordici passi per diventare piombo stabile. Su questa carta un decadimento alfa sposta di due caselle in basso e due a sinistra, un decadimento beta di una in alto e una a sinistra. In un vecchio minerale di uranio rimasto indisturbato, ogni membro decade allo stesso ritmo.</p>
  <div class="btns"><button class="btn" data-act="next">Decadimento successivo</button><button class="btn ghost" data-act="restart">Ricomincia</button></div>
</div>`,
};

Object.assign(WT.L.labels, {
  /* step 1 */
  "parent {#}": "padre {#}",
  "daughter {#}": "figlio {#}",
  "stable {#}": "stabile {#}",
  "parent ({#} s): {#}": "padre ({#} s): {#}",
  "daughter ({#} s): {#}": "figlio ({#} s): {#}",
  "granddaughter (stable): {#}": "nipote (stabile): {#}",
  "daughter peaks: {#} %": "picco del figlio: {#} %",
  "{#} s": "{#} s",
  "illustrative half-lives": "emivite illustrative",
  /* step 2 */
  "radium{#}": "radio{#}",
  "radon{#} gas": "radon{#} (gas)",
  "radium": "radio",
  "radium activity": "attività del radio",
  "radon": "radon",
  "radon activity": "attività del radon",
  "{#} d": "{#} g",
  "days →": "giorni →",
  "day {#}: radon at {#} % of radium": "giorno {#}: radon al {#} % del radio",
  "A(radon) = A(radium) × ({#} − exp(−λt))": "A(radon) = A(radio) × ({#} − exp(−λt))",
  /* step 3 */
  "Tc{#}m out": "Tc{#}m estratto",
  "Tc{#}m to the patient": "Tc{#}m al paziente",
  "molybdenum{#}": "molibdeno{#}",
  "dashed: never milked": "tratteggio: mai munto",
  "activity": "attività",
  "{#} h since last milking · Tc{#}m at {#} % of Mo{#}": "{#} h dall'ultima mungitura · Tc{#}m al {#} % del Mo{#}",
  "regrows to its peak in about {#} hours": "ricresce fino al picco in circa {#} ore",
  /* step 4 */
  "neutrons →": "neutroni →",
  "grey: stable": "grigio: stabile",
  "protons ↑": "protoni ↑",
  "alpha: {#} p, {#} n": "alfa: {#} p, {#} n",
  "alpha: loses {#} protons and {#} neutrons": "alfa: perde {#} protoni e {#} neutroni",
  "beta: n → p": "beta: n → p",
  "beta: a neutron becomes a proton": "beta: un neutrone diventa un protone",
  "U{#} · half-life {#} billion yr · alpha next": "U{#} · emivita {#} miliardi di anni · poi alfa",
  "Th{#} · half-life {#} days · beta next": "Th{#} · emivita {#} giorni · poi beta",
  "Pa{#}m · half-life {#} min · beta next": "Pa{#}m · emivita {#} min · poi beta",
  "U{#} · half-life {#} yr · alpha next": "U{#} · emivita {#} anni · poi alfa",
  "Th{#} · half-life {#} yr · alpha next": "Th{#} · emivita {#} anni · poi alfa",
  "Ra{#} · half-life {#} yr · alpha next": "Ra{#} · emivita {#} anni · poi alfa",
  "Rn{#} · half-life {#} days · alpha next": "Rn{#} · emivita {#} giorni · poi alfa",
  "Po{#} · half-life {#} min · alpha next": "Po{#} · emivita {#} min · poi alfa",
  "Pb{#} · half-life {#} min · beta next": "Pb{#} · emivita {#} min · poi beta",
  "Bi{#} · half-life {#} min · beta next": "Bi{#} · emivita {#} min · poi beta",
  "Po{#} · half-life {#} µs · alpha next": "Po{#} · emivita {#} µs · poi alfa",
  "Pb{#} · half-life {#} years · beta next": "Pb{#} · emivita {#} anni · poi beta",
  "Bi{#} · half-life {#} days · beta next": "Bi{#} · emivita {#} giorni · poi beta",
  "Po{#} · half-life {#} days · alpha next": "Po{#} · emivita {#} giorni · poi alfa",
  "Pb{#}: stable, the chain ends": "Pb{#}: stabile, la catena finisce",
  "step {#} of {#} · tap the nucleus": "passo {#} di {#} · tocca il nucleo",
});
