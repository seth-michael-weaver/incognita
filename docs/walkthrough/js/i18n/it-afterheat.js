/* Italian: afterheat (Il calore dopo lo spegnimento) */
WT.L.ch.afterheat = {
  num: "Lezione 1", title: "Il calore dopo lo spegnimento", short: "Calore di decadimento",
  html: `
<div class="step">
  <h3>La catena si ferma</h3>
  <p>Far cadere le barre di controllo ferma la scissione degli atomi in circa un minuto. Ma il combustibile continua a scaldare: i frammenti lasciati dalle fissioni precedenti sono radioattivi, e i loro decadimenti producono ancora calore.</p>
  <div class="btns"><button class="btn" data-act="ahDrop">Fai cadere le barre</button> <button class="btn ghost" data-act="ahUp">Riavvia</button></div>
</div>
<div class="step">
  <h3>Cala, lentamente</h3>
  <p>Subito dopo lo spegnimento questo calore vale circa il 6–7 % della piena potenza. Dopo un'ora è circa l'1 %, dopo un giorno circa mezzo punto percentuale, dopo una settimana un quarto. Quote piccole, ma di un numero molto grande.</p>
  <div class="ctl"><label for="ah-t">Tempo dallo spegnimento</label><input id="ah-t" type="range" data-bind="lt" data-instant min="0" max="7.5" step="0.01" value="3.56"></div>
</div>
<div class="step">
  <h3>Tenere l'acqua in movimento</h3>
  <p>Per questo il nocciolo va raffreddato anche dopo lo spegnimento. Le pompe fanno scorrere l'acqua lungo il combustibile e portano via il calore. Spegnile e la temperatura sale, perché il calore non ha dove andare.</p>
  <div class="btns"><button class="btn ghost" data-act="ahPump" aria-pressed="true">Pompe</button></div>
</div>
<div class="step">
  <h3>Raffreddare senza pompe</h3>
  <p>L'acqua calda sale e quella fredda scende. Un circuito che arriva a una piscina posta più in alto del nocciolo fa circolare l'acqua senza alcuna pompa. Diversi progetti recenti contano su questo per giorni.</p>
  <div class="btns"><button class="btn ghost" data-act="ahPump" aria-pressed="false">Pompe</button> <button class="btn ghost" data-act="ahPass" aria-pressed="true">Circuito passivo</button></div>
</div>`,
};

Object.assign(WT.L.labels, {
  "illustration": "illustrazione",
  // scene 1: the rods drop
  "splitting atoms": "fissioni",
  "heat from splitting atoms": "calore dalle fissioni",
  "decaying fragments": "decadimenti",
  "heat from decaying fragments": "calore dai frammenti che decadono",
  "full power": "piena potenza",
  "running at full power": "in funzione a piena potenza",
  "{a} after the rods dropped": "{a} dalla caduta delle barre",
  "{a} s": "{a} s",
  "{a} min": "{a} min",
  "{a} hours": "{a} ore",
  "{a} days": "{a} giorni",
  "{a} months": "{a} mesi",
  "total heat: {a} % of full power": "calore totale: {a} % della piena potenza",
  "the splitting dies away in about a minute": "le fissioni si spengono in circa un minuto",
  "the splitting dies away within about a minute": "le fissioni si spengono in circa un minuto",
  "the decay heat stays and fades slowly": "il calore di decadimento resta e cala piano",
  "the decay heat stays, and fades only slowly": "il calore di decadimento resta, e cala solo lentamente",
  // scene 2: the fading curve
  "{#} min": "{#} min",
  "{#} hour": "{#} ora",
  "{#} day": "{#} giorno",
  "{#} week": "{#} settimana",
  "{#} year": "{#} anno",
  "heat, share of full power": "calore, quota della piena potenza",
  "heat, as a share of full power": "calore, come quota della piena potenza",
  "{a} after shutdown: {b} % of full power": "{a} dallo spegnimento: {b} % della piena potenza",
  "{#} MW core: {a} MW, like {b} kettles": "nocciolo da {#} MW: {a} MW, come {b} bollitori",
  "for a {#} MW core: {a} MW, as much as {b} electric kettles": "per un nocciolo da {#} MW: {a} MW, quanto {b} bollitori elettrici",
  // scenes 3-4: cooling
  "pool, up high": "piscina in alto",
  "water pool, placed higher": "piscina d'acqua, posta più in alto",
  "cooler": "scambiatore",
  "heat exchanger": "scambiatore di calore",
  "pump on": "pompa accesa",
  "pump running": "pompa in funzione",
  "pump off": "pompa spenta",
  "pump stopped": "pompa ferma",
  "boiling": "ebollizione",
  "the water starts to boil": "l'acqua comincia a bollire",
  "normal": "normale",
  "too hot": "troppo caldo",
  "temperature": "temperatura",
  "core temperature": "temperatura del nocciolo",
  "{a} after shutdown · heat {b} % of full power": "{a} dallo spegnimento · calore {b} % della piena potenza",
  "too hot: cooling must be restored": "troppo caldo: ripristinare il raffreddamento",
  "too hot: the water would start to boil away; cooling must be restored": "troppo caldo: l'acqua comincerebbe a evaporare; bisogna ripristinare il raffreddamento",
  "temperature climbing": "la temperatura sale",
  "temperature climbing: the heat has nowhere to go": "la temperatura sale: il calore non ha dove andare",
  "pumps carry the heat away": "le pompe portano via il calore",
  "steady: the pumps carry the heat away": "stabile: le pompe portano via il calore",
  "steady, with no pumps": "stabile, senza pompe",
  "steady: natural circulation carries the heat away": "stabile: la circolazione naturale porta via il calore",
  "steady": "stabile",
});
