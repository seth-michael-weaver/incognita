/* Italian: diffusion (Lezione 1, dimensione critica e fughe) */
WT.L.ch.diffusion = {
  num: "Lezione 1", title: "Dimensione critica e fughe", short: "Dimensione critica",
  html: `
<div class="step">
  <h3>I neutroni vagano, alcuni sfuggono</h3>
  <p>Un neutrone procede a zigzag da una collisione all'altra finché qualcosa non lo assorbe. Se nasce vicino al bordo, può vagare fuori ed essere perso. Un nocciolo più grande ha meno superficie rispetto al suo volume, quindi ne sfugge una frazione minore.</p>
  <div class="ctl"><label for="df-w0">Larghezza del nocciolo (cm)</label><input id="df-w0" type="range" data-bind="w" data-instant min="20" max="200" step="2" value="60"><output data-show="w" data-fmt="0"></output></div>
</div>
<div class="step">
  <h3>La forma del flusso</h3>
  <p>La popolazione di neutroni si assesta su un'unica forma che scende quasi a zero al bordo: un coseno in una lastra, sin(<i>r</i>)/<i>r</i> in una sfera, una funzione di Bessel per un coseno in un cilindro. Quanto bruscamente deve curvarsi è il <b>buckling geometrico</b> <i>B</i>².</p>
  <div class="btns"><button class="btn ghost" data-act="dfslab" aria-pressed="false">Lastra</button><button class="btn ghost" data-act="dfsph" aria-pressed="true">Sfera</button><button class="btn ghost" data-act="dfcyl" aria-pressed="false">Cilindro</button></div>
  <div class="ctl"><label for="df-w1">Larghezza del nocciolo (cm)</label><input id="df-w1" type="range" data-bind="w" data-instant min="20" max="200" step="2" value="80"><output data-show="w" data-fmt="0"></output></div>
</div>
<div class="step">
  <h3>Dimensione critica</h3>
  <p>La diffusione a un gruppo dà <i>k</i><sub>eff</sub> = <i>k</i><sub>∞</sub> / (1 + <i>M</i>²<i>B</i>²), con un'area di migrazione <i>M</i>² di circa 60 cm² in un reattore ad acqua. Il nocciolo è critico quando <i>B</i>² è uguale al buckling materiale (<i>k</i><sub>∞</sub> − 1)/<i>M</i>². Trova quella dimensione.</p>
  <div class="btns"><button class="btn ghost" data-act="dfslab" aria-pressed="false">Lastra</button><button class="btn ghost" data-act="dfsph" aria-pressed="true">Sfera</button><button class="btn ghost" data-act="dfcyl" aria-pressed="false">Cilindro</button></div>
  <div class="ctl"><label for="df-w2">Larghezza del nocciolo (cm)</label><input id="df-w2" type="range" data-bind="w" data-instant min="20" max="200" step="1" value="90"><output data-show="w" data-fmt="0"></output></div>
</div>
<div class="step">
  <h3>Un riflettore risparmia neutroni</h3>
  <p>Circonda d'acqua un nocciolo a lastra: una parte dei neutroni che escono viene rimandata indietro. Il flusso non scende più a zero al bordo del nocciolo, così un nocciolo più sottile raggiunge lo stesso <i>k</i>; il guadagno è il <b>risparmio di riflettore</b>, qui circa 6 cm per lato.</p>
  <div class="btns"><button class="btn ghost" data-act="dfrefl" aria-pressed="true">Riflettore ad acqua</button></div>
  <div class="ctl"><label for="df-w3">Larghezza del nocciolo (cm)</label><input id="df-w3" type="range" data-bind="w" data-instant min="20" max="120" step="1" value="44"><output data-show="w" data-fmt="0"></output></div>
</div>`,
};
/* attributes referenced in the English chapter script (for the structure check): data-act="${a}" data-act="dfrefl" */

Object.assign(WT.L.labels, {
  "drag the edge": "trascina il bordo",
  "{#} cm": "{#} cm",
  "red: leaked": "rosso: sfuggito",
  "red: leaked out · blue: absorbed inside": "rosso: sfuggito · blu: assorbito all'interno",
  "leak: walk {#} % · diffusion {#} %": "fughe: cammino {#} % · diffusione {#} %",
  "leak: walk … · diffusion {#} %": "fughe: cammino … · diffusione {#} %",
  "share leaking: random walk {#} % · diffusion theory {#} %": "frazione che sfugge: cammino casuale {#} % · teoria della diffusione {#} %",
  "share leaking: random walk … · diffusion theory {#} %": "frazione che sfugge: cammino casuale … · teoria della diffusione {#} %",
  "k_eff = k∞ × ({#} − leak) = {#}": "k_eff = k∞ × ({#} − fughe) = {#}",
  "water": "acqua",
  "slab core": "nocciolo a lastra",
  "slab": "lastra",
  "sphere": "sfera",
  "cylinder": "cilindro",
  "flux across the middle": "flusso lungo la mezzeria",
  "slab {#} cm wide · smaller core → sharper bend → larger B²": "lastra larga {#} cm · nocciolo più piccolo → curva più stretta → B² maggiore",
  "sphere {#} cm wide · smaller core → sharper bend → larger B²": "sfera larga {#} cm · nocciolo più piccolo → curva più stretta → B² maggiore",
  "cylinder {#} cm wide · smaller core → sharper bend → larger B²": "cilindro largo {#} cm · nocciolo più piccolo → curva più stretta → B² maggiore",
  "critical {#} cm": "critico {#} cm",
  "core width →": "larghezza del nocciolo →",
  "critical: B² = B²ₘ, k_eff = {#}": "critico: B² = B²ₘ, k_eff = {#}",
  "reflected: k_eff {#} · bare: {#} · savings {#} cm per side": "con riflettore: k_eff {#} · nudo: {#} · risparmio {#} cm per lato",
  "bare: k_eff {#} · critical at {#} cm": "nudo: k_eff {#} · critico a {#} cm",
  "illustration": "illustrazione",
});
