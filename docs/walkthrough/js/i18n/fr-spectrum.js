/* French: spectrum (Réacteurs rapides et thermiques) */
WT.L.ch.spectrum = {
  num: "Leçon 1", title: "Réacteurs rapides et thermiques", short: "Rapide ou thermique",
  html: `
<div class="step">
  <h3>La vitesse des neutrons</h3>
  <p>Les neutrons naissent rapides, vers 2 MeV. Dans un réacteur à eau, ils rebondissent sur l'hydrogène jusqu'à devenir aussi lents que les atomes de l'eau eux-mêmes : <b>thermiques</b>. Un réacteur à neutrons rapides n'a pas de modérateur, ils restent donc rapides. Passez de l'un à l'autre.</p>
  <div class="ctl"><label for="spc-m1">Modération</label><input id="spc-m1" type="range" data-bind="mod" data-instant min="0" max="1" step="0.01" value="1"><output data-show="mod" data-fmt="2"></output></div>
</div>
<div class="step">
  <h3>Des neutrons en réserve</h3>
  <p><i>η</i> est le nombre de neutrons qu'un noyau de combustible rend par neutron absorbé. Un seul suffit à entretenir la chaîne ; pour produire du nouveau combustible (surgénération), il en faut un second en réserve, donc <i>η</i> nettement au-dessus de 2. Le plutonium 239 n'y parvient qu'avec des neutrons rapides.</p>
  <div class="ctl"><label for="spc-m2">Modération</label><input id="spc-m2" type="range" data-bind="mod" data-instant min="0" max="1" step="0.01" value="0"><output data-show="mod" data-fmt="2"></output></div>
</div>
<div class="step">
  <h3>Brûler les restes</h3>
  <p>Les restes lourds comme l'américium se contentent le plus souvent d'avaler les neutrons lents et de s'alourdir. Les neutrons rapides en fissionnent une part bien plus grande : un réacteur rapide peut donc les brûler.</p>
  <div class="ctl"><label for="spc-m3">Modération</label><input id="spc-m3" type="range" data-bind="mod" data-instant min="0" max="1" step="0.01" value="0"><output data-show="mod" data-fmt="2"></output></div>
</div>
<div class="step">
  <h3>Le prix à payer</h3>
  <p>Un neutron lent a bien plus de chances de provoquer une fission : à 1 MeV, la cible est des centaines de fois plus petite. Un cœur rapide demande donc un combustible bien plus riche, quelque 15–25 % de plutonium au lieu de 3–5 % d'uranium 235.</p>
  <div class="ctl"><label for="spc-m4">Modération</label><input id="spc-m4" type="range" data-bind="mod" data-instant min="0" max="1" step="0.01" value="1"><output data-show="mod" data-fmt="2"></output></div>
</div>`,
};

Object.assign(WT.L.labels, {
  "water: neutrons slow down": "eau : les neutrons ralentissent",
  "water reactor: hydrogen slows the neutrons": "réacteur à eau : l'hydrogène ralentit les neutrons",
  "sodium: they stay fast": "sodium : ils restent rapides",
  "fast reactor: sodium barely slows them": "réacteur rapide : le sodium les ralentit à peine",
  "partly moderated": "partiellement modéré",
  "{#} % split": "{#} % fissionnés",
  "sodium": "sodium",
  "no moderator (sodium)": "sans modérateur (sodium)",
  "water": "eau",
  "thermal": "thermique",
  "resonances": "résonances",
  "slowing down (resonances)": "ralentissement (résonances)",
  "fast": "rapide",
  "{#} eV": "{#} eV",
  "{#} keV": "{#} keV",
  "{#} MeV": "{#} MeV",
  "neutron energy →": "énergie du neutron →",
  "born ~{#} MeV": "nés à ~{#} MeV",
  "born near {#} MeV": "nés vers {#} MeV",
  "η = {#}: one to continue, one to breed": "η = {#} : un pour continuer, un pour surgénérer",
  "average η: U{#} {#} · Pu{#} {#}": "η moyen : U{#} {#} · Pu{#} {#}",
  "averaged over this spectrum:  η(U{#}) ≈ {#}   η(Pu{#}) ≈ {#}": "moyenne sur ce spectre :  η(U{#}) ≈ {#}   η(Pu{#}) ≈ {#}",
  "{#} b": "{#} b",
  "Pu{#} fission target": "cible de fission du Pu{#}",
  "Pu{#} fission cross section (target size)": "section efficace de fission du Pu{#} (taille de la cible)",
  "{#} MeV: a target ~{#} times smaller": "{#} MeV : une cible ~{#} fois plus petite",
  "at {#} MeV the target is about {#} times smaller than at {#} eV": "à {#} MeV, la cible est environ {#} fois plus petite qu'à {#} eV",
  "most neutrons end up thermal": "la plupart finissent thermiques",
  "most neutrons are slowed all the way to thermal": "la plupart des neutrons sont ralentis jusqu'au thermique",
  "most stay between {#} keV and {#} MeV": "la plupart restent entre {#} keV et {#} MeV",
  "most neutrons stay between {#} keV and {#} MeV": "la plupart des neutrons restent entre {#} keV et {#} MeV",
  "many linger at in-between energies": "beaucoup s'attardent aux énergies intermédiaires",
  "many neutrons linger at in-between energies": "beaucoup de neutrons s'attardent aux énergies intermédiaires",
  "hot water: kT ≈ {#} eV": "eau chaude : kT ≈ {#} eV",
  "thermal: kT ≈ {#} eV in hot water, about {#} km/s": "thermique : kT ≈ {#} eV dans l'eau chaude, environ {#} km/s",
  "the rest are captured and grow heavier": "les autres sont capturés et s'alourdissent",
  "the rest are captured: the nucleus just grows heavier": "les autres sont capturés : le noyau s'alourdit, simplement",
  "illustrative shapes": "formes illustratives",
});
