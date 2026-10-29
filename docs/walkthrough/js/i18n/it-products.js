/* Italian: products (Capitolo 15, prodotti di fissione e calore di decadimento) */
WT.L.ch.products = {
  num: "Capitolo 15", title: "Prodotti di fissione e calore di decadimento", short: "Prodotti di fissione",
  html: `
<div class="step">
  <p>I pezzi sono disuguali: uno leggero, uno pesante. Il grafico mostra, per ogni massa A del frammento (protoni più neutroni), la frazione di fissioni che lo produce. Due gobbe: i pezzi leggeri vicino ad A = 95, quelli pesanti vicino a 139. Una divisione simmetrica, vicino ad A = 117, è circa cento volte più rara.</p>
  <p>Ogni linea tratteggiata è dieci volte più alta di quella sotto, così si vedono anche le masse rare. Tocca una barra o trascina il cursore: sotto compaiono i due pezzi di quella divisione. La somma delle loro masse è 234, non 236 (uranio-235 più il neutrone), perché volano via anche circa 2,4 neutroni.</p>
  <div class="ctl"><label for="pr-a">Frammento leggero A</label><input id="pr-a" type="range" data-bind="pick" data-instant min="70" max="117" step="1" value="95"><output data-show="pick" data-fmt="0"></output></div>
</div>
<div class="step">
  <p>I loro decadimenti continuano a scaldare il combustibile dopo lo spegnimento. I frammenti sono radioattivi: decadono uno dopo l'altro, e ogni decadimento libera calore, sia che la reazione a catena proceda o no.</p>
  <div class="ctl"><label for="pr-t">Tempo dopo lo spegnimento</label><input id="pr-t" type="range" data-bind="lgt" data-instant min="0" max="8.5" step="0.01" value="0"><output id="pr-tout">1 s</output></div>
  <p>Trascina il tempo. Un secondo dopo l'arresto del reattore, i decadimenti danno ancora circa il 6 % della piena potenza; dopo un giorno, circa mezzo per cento; dopo un anno, qualche centesimo di per cento, che in un grande reattore è ancora quasi un megawatt. Per questo il combustibile esausto resta per anni in piscine di raffreddamento. La curva è la regola empirica di Way–Wigner: un'unica formula semplice per i decadimenti di tutti i frammenti insieme, dopo un anno di funzionamento. Entrambe le scale saltano di un fattore dieci a ogni tacca.</p>
</div>`,
};

Object.assign(WT.L.labels, {
  "fragment mass number A →": "numero di massa del frammento A →",
  "share of fissions that make it (each line ×{#})": "frazione di fissioni che lo producono (ogni linea ×{#})",
  "Rb{#} · {#} %": "Rb{#} · {#} %",
  "Xe{#} · {#} %": "Xe{#} · {#} %",
  "+ about {#} neutrons": "+ circa {#} neutroni",
  "{#} % of full power": "{#} % della piena potenza",
  "≈ {#} MW in a {#} MW reactor · {#} s after shutdown": "≈ {#} MW in un reattore da {#} MW · {#} s dopo lo spegnimento",
  "{#} min": "{#} min",
  "{#} h": "{#} h",
  "{#} day": "{#} giorno",
  "{#} yr": "{#} anno",
  "time after shutdown (each mark much later) →": "tempo dopo lo spegnimento (ogni tacca molto più tardi) →",
  "Way–Wigner rule of thumb, after a year at full power": "regola empirica di Way–Wigner, dopo un anno a piena potenza",
});
