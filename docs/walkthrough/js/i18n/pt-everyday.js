/* Portuguese (Português): everyday (O nuclear no dia a dia) */
WT.L.ch.everyday = {
  num: "Lição 4", title: "O nuclear no dia a dia", short: "Dia a dia",
  html: `
<div class="step">
  <h3>Exames PET</h3>
  <p>Um marcador de flúor-18 (meia-vida de 110 minutos) emite positrões, e cada um transforma-se em dois raios gama de 511 keV que partem em sentidos opostos. Arraste o ponto quente: o anel traça uma linha para cada par, e as linhas cruzam-se onde está o marcador.</p>
</div>
<div class="step">
  <h3>Radioterapia</h3>
  <p>Feixes de várias direções sobrepõem-se no tumor, que recebe assim a dose completa, enquanto cada trajeto por tecido saudável recebe apenas uma parte. Arraste para rodar os feixes e mantê-los longe da medula espinal.</p>
  <div class="ctl"><label for="ev-n">Feixes</label><input id="ev-n" type="range" data-bind="nb" data-instant min="1" max="7" step="1" value="5"><output data-show="nb" data-fmt="0"></output></div>
  <div class="ctl"><label for="ev-r">Rodar</label><input id="ev-r" type="range" data-bind="rotd" data-instant min="0" max="360" step="1" value="20"><output class="ev-rot"></output></div>
</div>
<div class="step">
  <h3>Tecnécio-99m</h3>
  <p>O isótopo da maioria dos exames de medicina nuclear emite um raio gama de 140 keV que uma câmara fora do corpo consegue ver, e com uma meia-vida de 6 horas resta pouco ao fim de um dia. Os hospitais <a href="#chains-3">extraem-no do molibdénio-99</a>.</p>
  <div class="ctl"><label for="ev-t">Horas após a dose</label><input id="ev-t" type="range" data-bind="th" data-instant min="0" max="48" step="0.5" value="0"><output data-show="th" data-fmt="1"></output></div>
</div>
<div class="step">
  <h3>Datação por carbono</h3>
  <p>Os seres vivos estão sempre a absorver carbono-14; depois da morte, ele decai com uma meia-vida de 5730 anos. Defina a idade, ou meça o que resta para ler a idade.</p>
  <div class="ctl"><label for="ev-a">Idade (anos)</label><input id="ev-a" type="range" data-bind="age" data-instant min="0" max="50000" step="10" value="5300"><output class="ev-age"></output></div>
  <div class="ctl"><label for="ev-f">Carbono-14 restante (%)</label><input id="ev-f" type="range" data-bind="fr" data-instant min="0.3" max="100" step="0.1" value="52.7"><output class="ev-fr"></output></div>
</div>
<div class="step">
  <h3>Detetores de fumo</h3>
  <p>Um grão selado de amerício-241 envia partículas alfa através de uma pequena camada de ar, criando iões que transportam uma corrente minúscula. O fumo captura os iões, a corrente cai e o alarme soa.</p>
  <div class="ctl"><label for="ev-s">Fumo</label><input id="ev-s" type="range" data-bind="sm" data-instant min="0" max="1" step="0.01" value="0"><output class="ev-sm"></output></div>
</div>`,
};

Object.assign(WT.L.labels, {
  "{#} beams cross: the tumour gets their sum": "{#} feixes cruzam-se: o tumor recebe a soma",
  "{#} h": "{#} h",
  "{#} h: {#} % left": "{#} h: restam {#} %",
  "{#} half-lives": "{#} meias-vidas",
  "{#} keV gamma rays": "raios gama de {#} keV",
  "{#} of {#} left": "restam {#} de {#}",
  "{#} years · {#} % left": "{#} anos · restam {#} %",
  "~{#} y: too little to measure": "~{#} anos: pouco demais para medir",
  "a beam crosses the spinal cord: turn the beams": "um feixe atravessa a medula: rode os feixes",
  "a strong gamma signal, easy to image": "um sinal gama forte, fácil de obter em imagem",
  "after a day, about {#} % is left": "ao fim de um dia restam cerca de {#} %",
  "alarm": "alarme",
  "alpha particles make ions in the air": "as partículas alfa criam iões no ar",
  "Am{#}": "Am{#}",
  "americium{#} · half-life {#} years · alphas reach about {#} cm in air": "amerício{#} · meia-vida {#} anos · as alfas percorrem cerca de {#} cm no ar",
  "americium{#} (sealed)": "amerício{#} (selado)",
  "beyond ~{#} years too little is left to measure": "para lá de ~{#} anos resta demasiado pouco para medir",
  "carbon{#}": "carbono{#}",
  "clean air: steady current": "ar limpo: corrente estável",
  "current": "corrente",
  "detector ring": "anel de detetores",
  "dose": "dose",
  "each decay: two {#} keV gamma rays, back to back": "cada decaimento: dois raios gama de {#} keV, em sentidos opostos",
  "fading: half is gone every {#} hours": "a desvanecer: metade desaparece a cada {#} horas",
  "fluorine{#} · half-life {#} min · {#} pairs recorded": "flúor{#} · meia-vida {#} min · {#} pares registados",
  "gamma camera": "câmara gama",
  "half-life {#} y": "meia-vida {#} anos",
  "illustration": "ilustração",
  "Mo{#} ({#} h)": "Mo{#} ({#} h)",
  "molybdenum{#}, half-life {#} h": "molibdénio{#}, meia-vida {#} h",
  "nitrogen{#}": "azoto{#}",
  "nitrogen{#} (after a beta decay)": "azoto{#} (após um decaimento beta)",
  "one beam: more dose near the skin than in the tumour": "um só feixe: mais dose junto à pele do que no tumor",
  "Ötzi the Iceman, ~{#} y": "Ötzi, o Homem do Gelo, ~{#} anos",
  "pairs of {#} keV gamma rays, back to back": "pares de raios gama de {#} keV, em sentidos opostos",
  "physical decay only": "só decaimento físico",
  "smoke: current down, alarm!": "fumo: a corrente cai, alarme!",
  "some ions caught: current dipping": "alguns iões capturados: a corrente desce",
  "spinal cord": "medula espinal",
  "Tc{#}m ({#} h)": "Tc{#}m ({#} h)",
  "technetium{#}m, half-life {#} h": "tecnécio{#}m, meia-vida {#} h",
  "tracer": "marcador",
  "tracer (drag me)": "marcador (arraste-me)",
  "tumour": "tumor",
  "tumour {#} % · spinal cord {#} % · healthy tissue at most {#} %": "tumor {#} % · medula {#} % · tecido saudável no máximo {#} %",
  "tumour {#} % · spinal cord {#} % · other tissue at most {#} %": "tumor {#} % · medula {#} % · outros tecidos no máximo {#} %",
  "years": "anos",
});
