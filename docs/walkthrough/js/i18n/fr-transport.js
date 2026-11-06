/* French: transport (Leçon 1, transport des neutrons et Monte Carlo) */
WT.L.ch.transport = {
  num: "Leçon 1", title: "Transport des neutrons et Monte Carlo", short: "Monte Carlo",
  html: `
<div class="step">
  <h3>L'équation du transport</h3>
  <p>Rigoureusement, les neutrons obéissent à l'équation de Boltzmann pour le flux angulaire <i>ψ</i>(<b>r</b>, <b>Ω</b>, <i>E</i>) : <b>Ω</b>·∇<i>ψ</i> + Σ<sub>t</sub><i>ψ</i> = ∫∫Σ<sub>s</sub><i>ψ</i>′ d<b>Ω</b>′d<i>E</i>′ + (<i>χ</i>/4π<i>k</i>)∫<i>ν</i>Σ<sub>f</sub><i>φ</i>′ d<i>E</i>′. Le Monte Carlo la résout en jouant les neutrons un par un : un vol de <i>s</i> = −ln <i>ξ</i> / Σ<sub>t</sub>, puis une diffusion, une capture ou une fission.</p>
  <div class="btns"><button class="btn" data-act="trnew">Nouveau neutron</button></div>
</div>
<div class="step">
  <h3>Là où la diffusion échoue</h3>
  <p>La théorie de la diffusion suppose un flux presque identique dans toutes les directions. C'est faux à un ou deux libres parcours d'une surface et dans les absorbants forts. Comparez-la au flux Monte Carlo dans une plaque à source uniforme en augmentant l'absorption.</p>
  <div class="ctl"><label for="tr-pa">Absorption Σ<sub>a</sub>/Σ<sub>t</sub></label><input id="tr-pa" type="range" data-bind="pa" data-instant min="0.05" max="0.8" step="0.05" value="0.5"><output data-show="pa" data-fmt="2"></output></div>
</div>
<div class="step">
  <h3>L'itération de puissance</h3>
  <p>Pour <i>k</i><sub>eff</sub>, les sites de fission de chaque génération deviennent la source de la suivante ; <i>k</i> est le nombre de sites mis en banque par neutron lancé. Partez d'une mauvaise estimation, tous les neutrons sur un bord, et regardez la source s'étaler vers le mode fondamental.</p>
  <div class="btns"><button class="btn" data-act="trbad">Repartir d'une mauvaise estimation</button></div>
</div>
<div class="step">
  <h3>La source a-t-elle convergé ?</h3>
  <p>L'entropie de Shannon <i>H</i> = −Σ <i>p</i><sub>b</sub> log<sub>2</sub> <i>p</i><sub>b</sub> de la source répartie en cases se stabilise une fois la source installée ; alors seulement on moyenne les générations. La barre d'erreur sur <i>k</i> diminue comme 1/√<i>N</i> avec le nombre d'histoires.</p>
  <div class="ctl"><label for="tr-n">Histoires par génération</label><input id="tr-n" type="range" data-bind="nh" data-instant min="100" max="2000" step="100" value="400"><output data-show="nh" data-fmt="0"></output></div>
</div>`,
};

Object.assign(WT.L.labels, {
  "vacuum": "vide",
  "glow: collision density": "lueur : densité de collisions",
  "amber glow: where collisions pile up": "lueur ambre : là où les collisions s'accumulent",
  "tap the slab to start neutrons": "touchez la plaque pour lancer des neutrons",
  "scatter": "diffusion",
  "capture": "capture",
  "fission": "fission",
  "leak": "fuite",
  "chance to fly at least s:  e^(−Σₜ s)": "probabilité de voler au moins s :  e^(−Σₜ s)",
  "{#} free paths": "{#} libres parcours",
  "ξ = {#}  →  s = −ln ξ / Σₜ = {#} free paths": "ξ = {#}  →  s = −ln ξ / Σₜ = {#} libres parcours",
  "infinite medium S/Σₐ": "milieu infini S/Σₐ",
  "Monte Carlo": "Monte Carlo",
  "diffusion": "diffusion",
  "flux": "flux",
  "diffusion vs Monte Carlo: +{#} % at the surface, +{#} % in the middle": "diffusion / Monte Carlo : +{#} % en surface, +{#} % au milieu",
  "diffusion vs Monte Carlo: +{#} % at the surface, {#} % in the middle": "diffusion / Monte Carlo : +{#} % en surface, {#} % au milieu",
  "diffusion vs Monte Carlo: {#} % at the surface, +{#} % in the middle": "diffusion / Monte Carlo : {#} % en surface, +{#} % au milieu",
  "diffusion vs Monte Carlo: {#} % at the surface, {#} % in the middle": "diffusion / Monte Carlo : {#} % en surface, {#} % au milieu",
  "tap: drop the source there": "touchez : la source y est placée",
  "tap the slab to drop the whole source there": "touchez la plaque pour y placer toute la source",
  "generation {#}": "génération {#}",
  "source · dashed: fundamental mode": "source · tirets : mode fondamental",
  "fission source · dashed: fundamental mode": "source de fission · tirets : mode fondamental",
  "source entropy H (bits)": "entropie de la source H (bits)",
  "inactive | active": "inactives | actives",
  "inactive  |  active generations": "générations inactives  |  actives",
  "k per generation": "k par génération",
  "generation {#}: k = {#} · H = {#} bits": "génération {#} : k = {#} · H = {#} bits",
  "starting…": "démarrage…",
  "k_eff = {#} ± {#} ({#} × {#} histories) · diffusion {#}": "k_eff = {#} ± {#} ({#} × {#} histoires) · diffusion {#}",
  "{#} generations, averaging starts after {#}": "{#} générations, moyenne après {#}",
  "illustrative one-group data": "données à un groupe, illustratives",
});
