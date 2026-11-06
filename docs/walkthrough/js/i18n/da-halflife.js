/* Danish: halflife (Radioaktivitet og halveringstid) */
WT.L.ch.halflife = {
  num: "Lektion 1", title: "Radioaktivitet og halveringstid", short: "Halveringstid",
  lead: "Nogle atomer er ustabile: før eller siden henfalder deres kerne, udsender stråling og bliver til noget andet. Ingen kan sige, hvornår en bestemt kerne går, men en hel prøve følger alligevel et ur, man kan stille sit ur efter.",
  html: `
<div class="step">
  <h3>En prøve, der henfalder tilfældigt</h3>
  <p>Hver glødende kugle er en ustabil kerne. Enhver af dem kan henfalde når som helst, udsende et glimt af stråling og blive et roligt, stabilt atom. Tryk på en for at få den til at henfalde.</p>
  <div class="btns"><button class="btn" data-act="refill">Ny prøve</button></div>
</div>
<div class="step">
  <h3>Halvdelen, og så halvdelen igen</h3>
  <p>Ingen kan sige, hvilken der går næste gang, men mængden er forudsigelig: efter én <b>halveringstid</b> er omkring halvdelen tilbage, efter to en fjerdedel, så en ottendedel. Gør halveringstiden længere eller kortere.</p>
  <div class="ctl"><label for="hl-th">Halveringstid (sekunder)</label><input id="hl-th" type="range" data-bind="Th" data-instant min="1" max="8" step="0.5" value="3"><output data-show="Th" data-fmt="1"></output></div>
  <div class="btns"><button class="btn ghost" data-act="refill">Ny prøve</button></div>
</div>
<div class="step">
  <h3>Kerner har ingen hukommelse</h3>
  <p>Følg én overlever. Uanset hvor længe den allerede har holdt, er dens chance for at holde én halveringstid mere stadig én til to: en kerne ældes ikke.</p>
  <div class="btns"><button class="btn ghost" data-act="tag">Følg en anden</button><button class="btn ghost" data-act="refill">Ny prøve</button></div>
</div>
<div class="step">
  <h3>Rigtige halveringstider</h3>
  <p>Rigtige isotoper spænder fra dage til milliarder af år. På denne udstrakte tidslinje falder hver af dem ud over en klippe ved sin egen halveringstid. Vælg en, og træk tiden fremad.</p>
  <div class="btns"><button class="btn ghost" data-act="iso0" aria-pressed="false">Jod-131</button><button class="btn ghost" data-act="iso1" aria-pressed="true">Cæsium-137</button><button class="btn ghost" data-act="iso2" aria-pressed="false">Kulstof-14</button><button class="btn ghost" data-act="iso3" aria-pressed="false">Uran-238</button></div>
  <div class="ctl"><label for="hl-t1">Forløbet tid</label><input id="hl-t1" type="range" data-bind="lt" data-instant min="3" max="17.8" step="0.02" value="8.98"><output class="hl-tout"></output></div>
</div>
<div class="step">
  <h3>Aktivitet: henfald pr. sekund</h3>
  <p>Ét gram af hver, side om side. En kort halveringstid betyder mange henfald hvert sekund, men ikke længe; en lang halveringstid gløder svagt i evigheder. Træk tiden, og se lamperne gå ud én efter én.</p>
  <div class="ctl"><label for="hl-t2">Forløbet tid</label><input id="hl-t2" type="range" data-bind="lt" data-instant min="3" max="17.8" step="0.02" value="4.94"><output class="hl-tout"></output></div>
</div>`,
};

Object.assign(WT.L.labels, {
  "survived {#} half-lives": "overlevet {#} halveringstider",
  "chance to last one more: {#} in {#}": "chance for én mere: {#} til {#}",
  "survived {#} half-lives · still {#} in {#}": "overlevet {#} halveringstider · stadig {#} til {#}",
  "it popped: follow another": "den henfaldt: følg en anden",
  "{#} of {#} still unstable": "{#} af {#} stadig ustabile",
  "{#} half-life": "{#} halveringstid",
  "half-lives →": "halveringstider →",
  "nuclei left": "tilbageværende kerner",
  "{#} of {#} left · half-life {#} s": "{#} af {#} tilbage · halveringstid {#} s",
  "every survivor has the same {#}-in{#} chance per half-life": "hver overlever har samme chance, {#} til {#}, pr. halveringstid",
  "illustrative half-life": "illustrativ halveringstid",
  "{#} hour": "{#} time",
  "{#} h": "{#} t",
  "{#} day": "{#} dag",
  "{#} d": "{#} d",
  "{#} year": "{#} år",
  "{#} yr": "{#} år",
  "{#} years": "{#} år",
  "{#}³ yr": "{#}³ år",
  "{#}⁶ yr": "{#}⁶ år",
  "{#}⁹ yr": "{#}⁹ år",
  "{#} million years": "{#} millioner år",
  "{#} billion years": "{#} milliarder år",
  "drag": "træk",
  "iodine{#} · half-life {#} days": "jod{#} · halveringstid {#} dage",
  "caesium{#} · half-life {#} years": "cæsium{#} · halveringstid {#} år",
  "carbon{#} · half-life {#} years": "kulstof{#} · halveringstid {#} år",
  "uranium{#} · half-life {#} billion years": "uran{#} · halveringstid {#} milliarder år",
  "medicine, fission product": "medicin, fissionsprodukt",
  "fission product": "fissionsprodukt",
  "radiocarbon dating": "kulstof-14-datering",
  "natural uranium": "naturligt uran",
  "all": "alle",
  "{#} % left after {#} minutes": "{#} % tilbage efter {#} minutter",
  "{#} % left after {#} hours": "{#} % tilbage efter {#} timer",
  "{#} % left after {#} days": "{#} % tilbage efter {#} dage",
  "{#} % left after {#} months": "{#} % tilbage efter {#} måneder",
  "{#} % left after {#} years": "{#} % tilbage efter {#} år",
  "{#} % left after {#} thousand years": "{#} % tilbage efter {#} tusind år",
  "{#} % left after {#} million years": "{#} % tilbage efter {#} millioner år",
  "{#} % left after {#} billion years": "{#} % tilbage efter {#} milliarder år",
  "under {#} % left after {#} minutes": "under {#} % tilbage efter {#} minutter",
  "under {#} % left after {#} hours": "under {#} % tilbage efter {#} timer",
  "under {#} % left after {#} days": "under {#} % tilbage efter {#} dage",
  "under {#} % left after {#} months": "under {#} % tilbage efter {#} måneder",
  "under {#} % left after {#} years": "under {#} % tilbage efter {#} år",
  "under {#} % left after {#} thousand years": "under {#} % tilbage efter {#} tusind år",
  "under {#} % left after {#} million years": "under {#} % tilbage efter {#} millioner år",
  "under {#} % left after {#} billion years": "under {#} % tilbage efter {#} milliarder år",
  "iodine{#}": "jod{#}",
  "caesium{#}": "cæsium{#}",
  "carbon{#}": "kulstof{#}",
  "uranium{#}": "uran{#}",
  "½ {#} days": "½ {#} dage",
  "½ {#} years": "½ {#} år",
  "½ {#} billion years": "½ {#} milliarder år",
  "½ {#} bn years": "½ {#} mia. år",
  "almost none": "næsten ingen",
  "{#} /s": "{#} /s",
  "~{#} /s": "~{#} /s",
  "pops per second (log)": "henfald pr. sekund (log)",
  "pops per second, {#} gram (each line ×{#})": "henfald pr. sekund, {#} gram (hver linje ×{#})",
  "one gram of each, after {#} minutes": "ét gram af hver, efter {#} minutter",
  "one gram of each, after {#} hours": "ét gram af hver, efter {#} timer",
  "one gram of each, after {#} days": "ét gram af hver, efter {#} dage",
  "one gram of each, after {#} months": "ét gram af hver, efter {#} måneder",
  "one gram of each, after {#} years": "ét gram af hver, efter {#} år",
  "one gram of each, after {#} thousand years": "ét gram af hver, efter {#} tusind år",
  "one gram of each, after {#} million years": "ét gram af hver, efter {#} millioner år",
  "one gram of each, after {#} billion years": "ét gram af hver, efter {#} milliarder år",
});
