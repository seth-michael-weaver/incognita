/* French: xenon (Leçon 1, empoisonnement xénon) */
WT.L.ch.xenon = {
  num: "Leçon 1", title: "Empoisonnement xénon", short: "Xénon",
  html: `
<div class="step">
  <h3>Un poison créé par la fission</h3>
  <p>Environ 6,6 % des fissions conduisent, via l'iode-135, au xénon-135 : le plus puissant absorbant de neutrons connu. Il s'accumule pendant environ deux jours, jusqu'à ce que les neutrons le brûlent et que la décroissance l'élimine aussi vite qu'il se forme. Une puissance plus élevée le brûle aussi plus vite, si bien que le niveau sature.</p>
  <div class="ctl"><label for="xe-p1">Puissance (%)</label><input id="xe-p1" type="range" data-bind="P" data-instant min="10" max="100" step="5" value="100"><output data-show="P" data-fmt="0"></output></div>
</div>
<div class="step">
  <h3>Le pic xénon</h3>
  <p>À l'arrêt, la combustion cesse, mais l'iode déjà formé continue de se transformer en xénon. Le poison culmine environ neuf heures plus tard, au-delà de ce que les barres peuvent rendre : le réacteur ne peut pas redémarrer (c'est le temps mort xénon). Le poison s'estompe en deux à trois jours.</p>
  <div class="ctl"><label for="xe-th">Heures après l'arrêt</label><input id="xe-th" type="range" data-bind="th" data-instant min="0" max="72" step="0.5" value="9"><output data-show="th" data-fmt="1"></output></div>
</div>
<div class="step">
  <h3>Arrêter, redémarrer</h3>
  <p>Maintenant, tout se déroule en direct, trois heures par seconde. Arrêtez, puis essayez de redémarrer : pendant le temps mort, c'est refusé ; plus tard, les neutrons brûlent le xénon. Un simple changement de puissance fait lui aussi osciller le xénon pendant des heures.</p>
  <div class="ctl"><label for="xe-p3">Puissance (%)</label><input id="xe-p3" type="range" data-bind="P" data-instant min="10" max="100" step="5" value="100"><output data-show="P" data-fmt="0"></output></div>
  <div class="btns"><button class="btn" data-act="xeshut">Arrêter</button><button class="btn ghost" data-act="xerestart">Redémarrer</button></div>
</div>
<div class="step">
  <h3>Oscillations xénon</h3>
  <p>Dans un grand cœur, les deux moitiés ne sont que faiblement couplées. Enfoncez des barres d'un côté : moins de flux y brûle moins de xénon, la puissance se déplace donc de l'autre côté, puis revient, environ une fois par jour. Dans les cœurs plus grands, l'oscillation s'amplifie si les opérateurs ne l'amortissent pas.</p>
  <div class="ctl"><label for="xe-wd">Taille du cœur (m)</label><input id="xe-wd" type="range" data-bind="wd" data-instant min="1.5" max="3.5" step="0.1" value="3"><output data-show="wd" data-fmt="1"></output></div>
  <div class="btns"><button class="btn" data-act="xepush">Enfoncer des barres à gauche</button></div>
</div>`,
};
/* attributes referenced in the English chapter script (for the structure check): data-act="${act}" */

Object.assign(WT.L.labels, {
  "fission → iodine{#} ({#} h) → xenon{#} ({#} h) → Cs{#}": "fission → iode{#} ({#} h) → xénon{#} ({#} h) → Cs{#}",
  "xenon{#} + n → Xe{#}: {#} million barns": "xénon{#} + n → Xe{#} : {#} millions de barns",
  "fission → iodine{#} ({#} h) → xenon{#} ({#} h) → Cs{#}  ·  Xe{#} swallows neutrons: {#} million barns": "fission → iode{#} ({#} h) → xénon{#} ({#} h) → Cs{#}  ·  Xe{#} avale les neutrons : {#} millions de barns",
  "spare reactivity": "réserve de réactivité",
  "spare reactivity the rods can give": "réserve de réactivité des barres",
  "{#} h": "{#} h",
  "equilibrium {#} %": "équilibre {#} %",
  "xenon worth (% of k)": "antiréactivité xénon (% de k)",
  "{#} % power · {#} h after start-up · xenon {#} %": "puissance {#} % · {#} h après le démarrage · xénon {#} %",
  "no restart": "pas de redémarrage",
  "too poisoned to restart": "trop empoisonné pour redémarrer",
  "shutdown": "arrêt",
  "drag": "glisser",
  "peak {#} % at {#} h": "pic {#} % à {#} h",
  "{#} h after shutdown · xenon {#} % · restart possible": "{#} h après l'arrêt · xénon {#} % · redémarrage possible",
  "{#} h after shutdown · xenon {#} % · cannot restart": "{#} h après l'arrêt · xénon {#} % · redémarrage impossible",
  "shut down": "arrêté",
  "refused: more xenon than spare reactivity": "refusé : plus de xénon que de réserve de réactivité",
  "restarted": "redémarré",
  "tap the core to shut down": "touchez le cœur pour l'arrêter",
  "tap the core to restart": "touchez le cœur pour redémarrer",
  "power": "puissance",
  "running at {#} % · xenon {#} %": "en marche à {#} % · xénon {#} %",
  "shut down · in the pit · xenon {#} %": "arrêté · temps mort xénon · xénon {#} %",
  "shut down · restart possible · xenon {#} %": "arrêté · redémarrage possible · xénon {#} %",
  "left {#} %": "gauche {#} %",
  "right {#} %": "droite {#} %",
  "tap a side to push rods in": "touchez un côté pour y enfoncer des barres",
  "more power left": "plus de puissance à gauche",
  "more power right": "plus de puissance à droite",
  "swing period {#} h · {#} m core: the swing dies away": "période {#} h · cœur de {#} m : l'oscillation s'amortit",
  "swing period {#} h · {#} m core: the swing dies away slowly": "période {#} h · cœur de {#} m : l'oscillation s'amortit lentement",
  "swing period {#} h · {#} m core: the swing grows": "période {#} h · cœur de {#} m : l'oscillation s'amplifie",
  "{#} m core: push the rods to start a swing": "cœur de {#} m : enfoncez les barres pour lancer une oscillation",
  "illustration": "illustration",
});
