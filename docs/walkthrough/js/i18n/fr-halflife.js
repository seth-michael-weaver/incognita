/* French: halflife (Radioactivité et demi-vie) */
WT.L.ch.halflife = {
  num: "Leçon 1", title: "Radioactivité et demi-vie", short: "Demi-vie",
  lead: "Certains atomes sont instables : tôt ou tard, leur noyau éclate, émet un rayonnement et devient autre chose. Personne ne peut dire quand un noyau donné se désintégrera, et pourtant un échantillon entier suit une horloge d'une régularité parfaite.",
  html: `
<div class="step">
  <h3>Un échantillon qui éclate au hasard</h3>
  <p>Chaque boule lumineuse est un noyau instable. N'importe lequel peut éclater à tout moment, émettre un éclair de rayonnement et devenir un atome calme et stable. Touchez-en un pour le faire éclater.</p>
  <div class="btns"><button class="btn" data-act="refill">Nouvel échantillon</button></div>
</div>
<div class="step">
  <h3>La moitié, puis encore la moitié</h3>
  <p>Personne ne peut dire lequel partira ensuite, mais la foule est prévisible : après une <b>demi-vie</b>, il en reste environ la moitié, après deux un quart, puis un huitième. Allongez ou raccourcissez la demi-vie.</p>
  <div class="ctl"><label for="hl-th">Demi-vie (secondes)</label><input id="hl-th" type="range" data-bind="Th" data-instant min="1" max="8" step="0.5" value="3"><output data-show="Th" data-fmt="1"></output></div>
  <div class="btns"><button class="btn ghost" data-act="refill">Nouvel échantillon</button></div>
</div>
<div class="step">
  <h3>Les noyaux n'ont pas de mémoire</h3>
  <p>Suivez un survivant. Quel que soit le temps qu'il a déjà tenu, sa chance de tenir une demi-vie de plus reste d'une sur deux : un noyau ne vieillit pas.</p>
  <div class="btns"><button class="btn ghost" data-act="tag">En suivre un autre</button><button class="btn ghost" data-act="refill">Nouvel échantillon</button></div>
</div>
<div class="step">
  <h3>De vraies demi-vies</h3>
  <p>Les isotopes réels vont de quelques jours à des milliards d'années. Sur cette échelle de temps étirée, chacun tombe d'une falaise à sa propre demi-vie. Choisissez-en un et faites avancer le temps.</p>
  <div class="btns"><button class="btn ghost" data-act="iso0" aria-pressed="false">Iode-131</button><button class="btn ghost" data-act="iso1" aria-pressed="true">Césium-137</button><button class="btn ghost" data-act="iso2" aria-pressed="false">Carbone-14</button><button class="btn ghost" data-act="iso3" aria-pressed="false">Uranium-238</button></div>
  <div class="ctl"><label for="hl-t1">Temps écoulé</label><input id="hl-t1" type="range" data-bind="lt" data-instant min="3" max="17.8" step="0.02" value="8.98"><output class="hl-tout"></output></div>
</div>
<div class="step">
  <h3>L'activité : des désintégrations par seconde</h3>
  <p>Un gramme de chacun, côte à côte. Une demi-vie courte signifie beaucoup de désintégrations chaque seconde, mais pas longtemps ; une demi-vie longue luit faiblement pendant des âges. Faites avancer le temps et regardez les lampes s'éteindre une à une.</p>
  <div class="ctl"><label for="hl-t2">Temps écoulé</label><input id="hl-t2" type="range" data-bind="lt" data-instant min="3" max="17.8" step="0.02" value="4.94"><output class="hl-tout"></output></div>
</div>`,
};

Object.assign(WT.L.labels, {
  "survived {#} half-lives": "a survécu {#} demi-vies",
  "chance to last one more: {#} in {#}": "chance d'en tenir une de plus : {#} sur {#}",
  "survived {#} half-lives · still {#} in {#}": "a survécu {#} demi-vies · toujours {#} sur {#}",
  "it popped: follow another": "il a éclaté : suivez-en un autre",
  "{#} of {#} still unstable": "{#} sur {#} encore instables",
  "{#} half-life": "{#} demi-vie",
  "1 half-life": "1 demi-vie",
  "half-lives →": "demi-vies →",
  "nuclei left": "noyaux restants",
  "{#} of {#} left · half-life {#} s": "{#} sur {#} restants · demi-vie {#} s",
  "every survivor has the same 1-in-2 chance per half-life": "chaque survivant a la même chance, 1 sur 2, par demi-vie",
  "every survivor has the same {#}-in{#} chance per half-life": "chaque survivant a la même chance, {#} sur {#}, par demi-vie",
  "illustrative half-life": "demi-vie illustrative",
  "{#} hour": "{#} heure",
  "{#} day": "{#} jour",
  "{#} d": "{#} j",
  "{#} year": "{#} an",
  "{#} yr": "{#} ans",
  "{#} years": "{#} ans",
  "10³ yr": "10³ a",
  "10⁶ yr": "10⁶ a",
  "10⁹ yr": "10⁹ a",
  "{#}³ yr": "{#}³ a",
  "{#}⁶ yr": "{#}⁶ a",
  "{#}⁹ yr": "{#}⁹ a",
  "{#} million years": "{#} million d'années",
  "{#} billion years": "{#} milliard d'années",
  "drag": "glisser",
  "iodine{#} · half-life {#} days": "iode{#} · demi-vie {#} jours",
  "caesium{#} · half-life {#} years": "césium{#} · demi-vie {#} ans",
  "carbon{#} · half-life {#} years": "carbone{#} · demi-vie {#} ans",
  "uranium{#} · half-life {#} billion years": "uranium{#} · demi-vie {#} milliards d'années",
  "medicine, fission product": "médecine, produit de fission",
  "fission product": "produit de fission",
  "radiocarbon dating": "datation au carbone 14",
  "natural uranium": "uranium naturel",
  "all": "tout",
  "{#} % left after {#} minutes": "il reste {#} % après {#} minutes",
  "{#} % left after {#} hours": "il reste {#} % après {#} heures",
  "{#} % left after {#} days": "il reste {#} % après {#} jours",
  "{#} % left after {#} months": "il reste {#} % après {#} mois",
  "{#} % left after {#} years": "il reste {#} % après {#} ans",
  "{#} % left after {#} thousand years": "il reste {#} % après {#} mille ans",
  "{#} % left after {#} million years": "il reste {#} % après {#} millions d'années",
  "{#} % left after {#} billion years": "il reste {#} % après {#} milliards d'années",
  "under {#} % left after {#} minutes": "il reste moins de {#} % après {#} minutes",
  "under {#} % left after {#} hours": "il reste moins de {#} % après {#} heures",
  "under {#} % left after {#} days": "il reste moins de {#} % après {#} jours",
  "under {#} % left after {#} months": "il reste moins de {#} % après {#} mois",
  "under {#} % left after {#} years": "il reste moins de {#} % après {#} ans",
  "under {#} % left after {#} thousand years": "il reste moins de {#} % après {#} mille ans",
  "under {#} % left after {#} million years": "il reste moins de {#} % après {#} millions d'années",
  "under {#} % left after {#} billion years": "il reste moins de {#} % après {#} milliards d'années",
  "iodine{#}": "iode{#}",
  "caesium{#}": "césium{#}",
  "carbon{#}": "carbone{#}",
  "uranium{#}": "uranium{#}",
  "½ {#} days": "½ {#} jours",
  "½ {#} years": "½ {#} ans",
  "½ {#} billion years": "½ {#} milliards d'années",
  "½ {#} bn years": "½ {#} Md d'années",
  "almost none": "presque rien",
  "pops per second (log)": "désintégrations par s (log)",
  "pops per second, {#} gram (each line ×{#})": "désintégrations par seconde, {#} gramme (chaque ligne ×{#})",
  "one gram of each, after {#} minutes": "un gramme de chacun, après {#} minutes",
  "one gram of each, after {#} hours": "un gramme de chacun, après {#} heures",
  "one gram of each, after {#} days": "un gramme de chacun, après {#} jours",
  "one gram of each, after {#} months": "un gramme de chacun, après {#} mois",
  "one gram of each, after {#} years": "un gramme de chacun, après {#} ans",
  "one gram of each, after {#} thousand years": "un gramme de chacun, après {#} mille ans",
  "one gram of each, after {#} million years": "un gramme de chacun, après {#} millions d'années",
  "one gram of each, after {#} billion years": "un gramme de chacun, après {#} milliards d'années",
});
