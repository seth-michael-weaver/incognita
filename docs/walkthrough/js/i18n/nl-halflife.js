/* Dutch (Nederlands): halflife (Radioactiviteit en halveringstijd) */
WT.L.ch.halflife = {
  num: "Les 1", title: "Radioactiviteit en halveringstijd", short: "Halveringstijd",
  lead: "Sommige atomen zijn instabiel: vroeg of laat valt hun kern uiteen, zendt straling uit en wordt iets anders. Niemand kan zeggen wanneer één kern gaat, en toch volgt een heel monster een klok waar je je horloge op gelijk kunt zetten.",
  html: `
<div class="step">
  <h3>Een monster dat willekeurig vervalt</h3>
  <p>Elk gloeiend bolletje is een instabiele kern. Elke kern kan op elk moment vervallen, een flits straling uitzenden en een rustig, stabiel atoom worden. Tik er een aan om hem te laten vervallen.</p>
  <div class="btns"><button class="btn" data-act="refill">Nieuw monster</button></div>
</div>
<div class="step">
  <h3>De helft, en dan weer de helft</h3>
  <p>Niemand kan zeggen welke als volgende gaat, maar de menigte is voorspelbaar: na één <b>halveringstijd</b> is ongeveer de helft over, na twee een kwart, dan een achtste. Maak de halveringstijd langer of korter.</p>
  <div class="ctl"><label for="hl-th">Halveringstijd (seconden)</label><input id="hl-th" type="range" data-bind="Th" data-instant min="1" max="8" step="0.5" value="3"><output data-show="Th" data-fmt="1"></output></div>
  <div class="btns"><button class="btn ghost" data-act="refill">Nieuw monster</button></div>
</div>
<div class="step">
  <h3>Kernen hebben geen geheugen</h3>
  <p>Volg één overlevende. Hoe lang hij het ook al volhoudt, zijn kans om nog een halveringstijd te overleven blijft één op twee: een kern veroudert niet.</p>
  <div class="btns"><button class="btn ghost" data-act="tag">Volg een andere</button><button class="btn ghost" data-act="refill">Nieuw monster</button></div>
</div>
<div class="step">
  <h3>Echte halveringstijden</h3>
  <p>Echte isotopen lopen van dagen tot miljarden jaren. Op deze uitgerekte tijdlijn valt elk van een klif bij zijn eigen halveringstijd. Kies er een en sleep de tijd vooruit.</p>
  <div class="btns"><button class="btn ghost" data-act="iso0" aria-pressed="false">Jodium-131</button><button class="btn ghost" data-act="iso1" aria-pressed="true">Cesium-137</button><button class="btn ghost" data-act="iso2" aria-pressed="false">Koolstof-14</button><button class="btn ghost" data-act="iso3" aria-pressed="false">Uranium-238</button></div>
  <div class="ctl"><label for="hl-t1">Verstreken tijd</label><input id="hl-t1" type="range" data-bind="lt" data-instant min="3" max="17.8" step="0.02" value="8.98"><output class="hl-tout"></output></div>
</div>
<div class="step">
  <h3>Activiteit: vervallen per seconde</h3>
  <p>Van elk één gram, naast elkaar. Een korte halveringstijd betekent veel vervallen per seconde, maar niet lang; een lange halveringstijd gloeit eeuwenlang zwak na. Sleep de tijd en kijk hoe de lampen een voor een uitgaan.</p>
  <div class="ctl"><label for="hl-t2">Verstreken tijd</label><input id="hl-t2" type="range" data-bind="lt" data-instant min="3" max="17.8" step="0.02" value="4.94"><output class="hl-tout"></output></div>
</div>`,
};

Object.assign(WT.L.labels, {
  "survived {#} half-lives": "{#} halveringstijden overleefd",
  "chance to last one more: {#} in {#}": "kans op nog één: {#} op {#}",
  "survived {#} half-lives · still {#} in {#}": "{#} halveringstijden overleefd · nog steeds {#} op {#}",
  "it popped: follow another": "vervallen: volg een andere",
  "{#} of {#} still unstable": "{#} van {#} nog instabiel",
  "{#} half-life": "{#} halveringstijd",
  "half-lives →": "halveringstijden →",
  "nuclei left": "resterende kernen",
  "{#} of {#} left · half-life {#} s": "{#} van {#} over · halveringstijd {#} s",
  "every survivor has the same {#}-in{#} chance per half-life": "elke overlevende heeft per halveringstijd dezelfde kans van {#} op {#}",
  "illustrative half-life": "illustratieve halveringstijd",
  "{#} hour": "{#} uur",
  "{#} h": "{#} u",
  "{#} day": "{#} dag",
  "{#} d": "{#} d",
  "{#} year": "{#} jaar",
  "{#} yr": "{#} jr",
  "{#} years": "{#} jaar",
  "{#}³ yr": "{#}³ jr",
  "{#}⁶ yr": "{#}⁶ jr",
  "{#}⁹ yr": "{#}⁹ jr",
  "{#} million years": "{#} miljoen jaar",
  "{#} billion years": "{#} miljard jaar",
  "drag": "sleep",
  "iodine{#} · half-life {#} days": "jodium{#} · halveringstijd {#} dagen",
  "caesium{#} · half-life {#} years": "cesium{#} · halveringstijd {#} jaar",
  "carbon{#} · half-life {#} years": "koolstof{#} · halveringstijd {#} jaar",
  "uranium{#} · half-life {#} billion years": "uranium{#} · halveringstijd {#} miljard jaar",
  "medicine, fission product": "geneeskunde, splijtingsproduct",
  "fission product": "splijtingsproduct",
  "radiocarbon dating": "koolstofdatering",
  "natural uranium": "natuurlijk uranium",
  "all": "alle",
  "{#} % left after {#} minutes": "{#} % over na {#} minuten",
  "{#} % left after {#} hours": "{#} % over na {#} uur",
  "{#} % left after {#} days": "{#} % over na {#} dagen",
  "{#} % left after {#} months": "{#} % over na {#} maanden",
  "{#} % left after {#} years": "{#} % over na {#} jaar",
  "{#} % left after {#} thousand years": "{#} % over na {#} duizend jaar",
  "{#} % left after {#} million years": "{#} % over na {#} miljoen jaar",
  "{#} % left after {#} billion years": "{#} % over na {#} miljard jaar",
  "under {#} % left after {#} minutes": "minder dan {#} % over na {#} minuten",
  "under {#} % left after {#} hours": "minder dan {#} % over na {#} uur",
  "under {#} % left after {#} days": "minder dan {#} % over na {#} dagen",
  "under {#} % left after {#} months": "minder dan {#} % over na {#} maanden",
  "under {#} % left after {#} years": "minder dan {#} % over na {#} jaar",
  "under {#} % left after {#} thousand years": "minder dan {#} % over na {#} duizend jaar",
  "under {#} % left after {#} million years": "minder dan {#} % over na {#} miljoen jaar",
  "under {#} % left after {#} billion years": "minder dan {#} % over na {#} miljard jaar",
  "iodine{#}": "jodium{#}",
  "caesium{#}": "cesium{#}",
  "carbon{#}": "koolstof{#}",
  "uranium{#}": "uranium{#}",
  "½ {#} days": "½ {#} dagen",
  "½ {#} years": "½ {#} jaar",
  "½ {#} billion years": "½ {#} miljard jaar",
  "½ {#} bn years": "½ {#} mld. jaar",
  "almost none": "bijna geen",
  "{#} /s": "{#} /s",
  "~{#} /s": "~{#} /s",
  "pops per second (log)": "vervallen per seconde (log)",
  "pops per second, {#} gram (each line ×{#})": "vervallen per seconde, {#} gram (elke lijn ×{#})",
  "one gram of each, after {#} minutes": "van elk één gram, na {#} minuten",
  "one gram of each, after {#} hours": "van elk één gram, na {#} uur",
  "one gram of each, after {#} days": "van elk één gram, na {#} dagen",
  "one gram of each, after {#} months": "van elk één gram, na {#} maanden",
  "one gram of each, after {#} years": "van elk één gram, na {#} jaar",
  "one gram of each, after {#} thousand years": "van elk één gram, na {#} duizend jaar",
  "one gram of each, after {#} million years": "van elk één gram, na {#} miljoen jaar",
  "one gram of each, after {#} billion years": "van elk één gram, na {#} miljard jaar",
});
