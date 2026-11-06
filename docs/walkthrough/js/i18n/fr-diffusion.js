/* French: diffusion (Leçon 1, taille critique et fuites) */
WT.L.ch.diffusion = {
  num: "Leçon 1", title: "Taille critique et fuites", short: "Taille critique",
  html: `
<div class="step">
  <h3>Les neutrons errent, certains s'échappent</h3>
  <p>Un neutron zigzague de collision en collision jusqu'à ce qu'il soit absorbé. S'il naît près du bord, il peut sortir en errant et être perdu. Un cœur plus grand a moins de surface pour son volume : une part plus faible s'échappe.</p>
  <div class="ctl"><label for="df-w0">Largeur du cœur (cm)</label><input id="df-w0" type="range" data-bind="w" data-instant min="20" max="200" step="2" value="60"><output data-show="w" data-fmt="0"></output></div>
</div>
<div class="step">
  <h3>La forme du flux</h3>
  <p>La population de neutrons prend une forme unique qui tombe à peu près à zéro au bord : un cosinus dans une plaque, sin(<i>r</i>)/<i>r</i> dans une sphère, une fonction de Bessel fois un cosinus dans un cylindre. La force avec laquelle elle doit se courber est le <b>laplacien géométrique</b> <i>B</i>².</p>
  <div class="btns"><button class="btn ghost" data-act="dfslab" aria-pressed="false">Plaque</button><button class="btn ghost" data-act="dfsph" aria-pressed="true">Sphère</button><button class="btn ghost" data-act="dfcyl" aria-pressed="false">Cylindre</button></div>
  <div class="ctl"><label for="df-w1">Largeur du cœur (cm)</label><input id="df-w1" type="range" data-bind="w" data-instant min="20" max="200" step="2" value="80"><output data-show="w" data-fmt="0"></output></div>
</div>
<div class="step">
  <h3>La taille critique</h3>
  <p>La diffusion à un groupe donne <i>k</i><sub>eff</sub> = <i>k</i><sub>∞</sub> / (1 + <i>M</i>²<i>B</i>²), avec une aire de migration <i>M</i>² d'environ 60 cm² dans un réacteur à eau. Le cœur est critique quand <i>B</i>² égale le laplacien matières (<i>k</i><sub>∞</sub> − 1)/<i>M</i>². Trouvez cette taille.</p>
  <div class="btns"><button class="btn ghost" data-act="dfslab" aria-pressed="false">Plaque</button><button class="btn ghost" data-act="dfsph" aria-pressed="true">Sphère</button><button class="btn ghost" data-act="dfcyl" aria-pressed="false">Cylindre</button></div>
  <div class="ctl"><label for="df-w2">Largeur du cœur (cm)</label><input id="df-w2" type="range" data-bind="w" data-instant min="20" max="200" step="1" value="90"><output data-show="w" data-fmt="0"></output></div>
</div>
<div class="step">
  <h3>Un réflecteur économise des neutrons</h3>
  <p>Entourez un cœur en plaque d'eau : une partie des neutrons qui sortent sont renvoyés. Le flux ne tombe plus à zéro au bord du cœur, si bien qu'un cœur plus mince atteint le même <i>k</i> ; le gain est l'<b>économie de réflecteur</b>, ici environ 6 cm par côté.</p>
  <div class="btns"><button class="btn ghost" data-act="dfrefl" aria-pressed="true">Réflecteur en eau</button></div>
  <div class="ctl"><label for="df-w3">Largeur du cœur (cm)</label><input id="df-w3" type="range" data-bind="w" data-instant min="20" max="120" step="1" value="44"><output data-show="w" data-fmt="0"></output></div>
</div>`,
};
/* attributes referenced in the English chapter script (for the structure check): data-act="${a}" data-act="dfrefl" */

Object.assign(WT.L.labels, {
  "drag the edge": "glissez le bord",
  "{#} cm": "{#} cm",
  "red: leaked": "rouge : échappé",
  "red: leaked out · blue: absorbed inside": "rouge : échappé · bleu : absorbé à l'intérieur",
  "leak: walk {#} % · diffusion {#} %": "fuites : marche {#} % · diffusion {#} %",
  "leak: walk … · diffusion {#} %": "fuites : marche … · diffusion {#} %",
  "share leaking: random walk {#} % · diffusion theory {#} %": "part des fuites : marche aléatoire {#} % · théorie de la diffusion {#} %",
  "share leaking: random walk … · diffusion theory {#} %": "part des fuites : marche aléatoire … · théorie de la diffusion {#} %",
  "k_eff = k∞ × ({#} − leak) = {#}": "k_eff = k∞ × ({#} − fuites) = {#}",
  "water": "eau",
  "slab core": "cœur en plaque",
  "slab": "plaque",
  "sphere": "sphère",
  "cylinder": "cylindre",
  "flux across the middle": "flux à travers le milieu",
  "slab {#} cm wide · smaller core → sharper bend → larger B²": "plaque de {#} cm · cœur plus petit → courbure plus forte → B² plus grand",
  "sphere {#} cm wide · smaller core → sharper bend → larger B²": "sphère de {#} cm · cœur plus petit → courbure plus forte → B² plus grand",
  "cylinder {#} cm wide · smaller core → sharper bend → larger B²": "cylindre de {#} cm · cœur plus petit → courbure plus forte → B² plus grand",
  "critical {#} cm": "critique {#} cm",
  "core width →": "largeur du cœur →",
  "critical: B² = B²ₘ, k_eff = {#}": "critique : B² = B²ₘ, k_eff = {#}",
  "reflected: k_eff {#} · bare: {#} · savings {#} cm per side": "avec réflecteur : k_eff {#} · nu : {#} · économie {#} cm par côté",
  "bare: k_eff {#} · critical at {#} cm": "nu : k_eff {#} · critique à {#} cm",
  "illustration": "illustration",
});
