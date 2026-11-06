/* Portuguese (pt-PT): spectrum (Reatores rápidos e térmicos) */
WT.L.ch.spectrum = {
  num: "Lição 1", title: "Reatores rápidos e térmicos", short: "Rápido ou térmico",
  html: `
<div class="step">
  <h3>A rapidez dos neutrões</h3>
  <p>Os neutrões nascem rápidos, perto de 2 MeV. Num reator de água ressaltam no hidrogénio até ficarem tão lentos como os próprios átomos da água: <b>térmicos</b>. Um reator rápido não tem moderador, por isso continuam rápidos. Desliza entre os dois.</p>
  <div class="ctl"><label for="spc-m1">Moderação</label><input id="spc-m1" type="range" data-bind="mod" data-instant min="0" max="1" step="0.01" value="1"><output data-show="mod" data-fmt="2"></output></div>
</div>
<div class="step">
  <h3>Neutrões de sobra</h3>
  <p><i>η</i> é o número de neutrões que um núcleo de combustível devolve por cada neutrão que absorve. Um mantém a cadeia; para regenerar combustível novo é preciso um segundo de sobra, portanto <i>η</i> bem acima de 2. O plutónio-239 só o consegue com neutrões rápidos.</p>
  <div class="ctl"><label for="spc-m2">Moderação</label><input id="spc-m2" type="range" data-bind="mod" data-instant min="0" max="1" step="0.01" value="0"><output data-show="mod" data-fmt="2"></output></div>
</div>
<div class="step">
  <h3>Queimar os restos</h3>
  <p>Restos pesados como o amerício limitam-se quase sempre a engolir os neutrões lentos e a ficar mais pesados. Os neutrões rápidos cindem uma fração muito maior deles, por isso um reator rápido consegue queimá-los.</p>
  <div class="ctl"><label for="spc-m3">Moderação</label><input id="spc-m3" type="range" data-bind="mod" data-instant min="0" max="1" step="0.01" value="0"><output data-show="mod" data-fmt="2"></output></div>
</div>
<div class="step">
  <h3>O preço</h3>
  <p>Um neutrão lento tem muito mais probabilidade de causar fissão: a 1 MeV o alvo é centenas de vezes mais pequeno. Por isso um núcleo rápido precisa de combustível muito mais rico, uns 15–25 % de plutónio em vez de 3–5 % de urânio-235.</p>
  <div class="ctl"><label for="spc-m4">Moderação</label><input id="spc-m4" type="range" data-bind="mod" data-instant min="0" max="1" step="0.01" value="1"><output data-show="mod" data-fmt="2"></output></div>
</div>`,
};

Object.assign(WT.L.labels, {
  "water: neutrons slow down": "água: os neutrões abrandam",
  "water reactor: hydrogen slows the neutrons": "reator de água: o hidrogénio abranda os neutrões",
  "sodium: they stay fast": "sódio: continuam rápidos",
  "fast reactor: sodium barely slows them": "reator rápido: o sódio mal os abranda",
  "partly moderated": "parcialmente moderado",
  "{#} % split": "{#} % cindidos",
  "sodium": "sódio",
  "no moderator (sodium)": "sem moderador (sódio)",
  "water": "água",
  "thermal": "térmicos",
  "resonances": "ressonâncias",
  "slowing down (resonances)": "abrandamento (ressonâncias)",
  "fast": "rápidos",
  "{#} eV": "{#} eV",
  "{#} keV": "{#} keV",
  "{#} MeV": "{#} MeV",
  "neutron energy →": "energia do neutrão →",
  "born ~{#} MeV": "nascem a ~{#} MeV",
  "born near {#} MeV": "nascem perto de {#} MeV",
  "η = {#}: one to continue, one to breed": "η = {#}: um para continuar, um para regenerar",
  "average η: U{#} {#} · Pu{#} {#}": "η médio: U{#} {#} · Pu{#} {#}",
  "averaged over this spectrum:  η(U{#}) ≈ {#}   η(Pu{#}) ≈ {#}": "média neste espetro:  η(U{#}) ≈ {#}   η(Pu{#}) ≈ {#}",
  "{#} b": "{#} b",
  "Pu{#} fission target": "alvo de fissão do Pu{#}",
  "Pu{#} fission cross section (target size)": "secção eficaz de fissão do Pu{#} (tamanho do alvo)",
  "{#} MeV: a target ~{#} times smaller": "{#} MeV: um alvo ~{#} vezes menor",
  "at {#} MeV the target is about {#} times smaller than at {#} eV": "a {#} MeV o alvo é cerca de {#} vezes menor do que a {#} eV",
  "most neutrons end up thermal": "a maioria acaba térmica",
  "most neutrons are slowed all the way to thermal": "a maioria dos neutrões abranda até à energia térmica",
  "most stay between {#} keV and {#} MeV": "a maioria fica entre {#} keV e {#} MeV",
  "most neutrons stay between {#} keV and {#} MeV": "a maioria dos neutrões fica entre {#} keV e {#} MeV",
  "many linger at in-between energies": "muitos demoram-se em energias intermédias",
  "many neutrons linger at in-between energies": "muitos neutrões demoram-se em energias intermédias",
  "thermal ≈ {#} eV, ~{#} km/s": "térmico ≈ {#} eV, ~{#} km/s",
  "thermal: kT ≈ {#} eV in hot water, about {#} km/s": "térmico: kT ≈ {#} eV em água quente, cerca de {#} km/s",
  "the rest are captured and grow heavier": "os restantes são capturados e ficam mais pesados",
  "the rest are captured: the nucleus just grows heavier": "os restantes são capturados: o núcleo apenas fica mais pesado",
  "illustrative shapes": "formas ilustrativas",
});
