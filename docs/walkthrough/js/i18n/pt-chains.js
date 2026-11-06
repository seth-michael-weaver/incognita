/* Portuguese (pt-PT): chains (Cadeias de decaimento e equilíbrio) */
WT.L.ch.chains = {
  num: "Lição 4", title: "Cadeias de decaimento e equilíbrio", short: "Cadeias de decaimento",
  html: `
<div class="step">
  <h3>Pai, filho, neto</h3>
  <p>Muitas vezes o novo núcleo também é instável. O pai decai num filho, que por sua vez decai num neto estável. Os filhos acumulam-se e depois desaparecem; quanto se acumulam depende da rapidez com que decaem em comparação com o pai.</p>
  <div class="ctl"><label for="ch-t2">Meia-vida do filho (s)</label><input id="ch-t2" type="range" data-bind="T2" data-instant min="0.5" max="9" step="0.5" value="1.5"><output data-show="T2" data-fmt="1"></output></div>
  <div class="btns"><button class="btn ghost" data-act="refill">Amostra nova</button></div>
</div>
<div class="step">
  <h3>Equilíbrio secular: rádio e radão</h3>
  <p>O rádio-226 dura 1600 anos; o seu filho, o gás radão-222, apenas 3,8 dias. Num frasco fechado o radão acumula-se até decair tão depressa quanto é produzido: <i>A</i><sub>Rn</sub> = <i>A</i><sub>Ra</sub>(1 − e<sup>−λt</sup>), sendo λ a constante de decaimento do radão. Ao fim de algumas semanas, ambos decaem ao mesmo ritmo.</p>
  <div class="btns"><button class="btn" data-act="vent">Abrir o frasco</button></div>
</div>
<div class="step">
  <h3>Equilíbrio transitório: a vaca de tecnécio</h3>
  <p>Os hospitais recebem uma coluna de molibdénio-99 (66 horas) que vai produzindo tecnécio-99m (6 horas), o marcador médico mais usado. Extrai-se o tecnécio todas as manhãs e ele volta a crescer, acompanhando o molibdénio, que se esvai devagar.</p>
  <div class="btns"><button class="btn" data-act="milk">Ordenhar o gerador</button><button class="btn ghost" data-act="genre">Gerador novo</button></div>
</div>
<div class="step">
  <h3>Pela cadeia do urânio abaixo</h3>
  <p>O urânio-238 precisa de catorze passos para se tornar chumbo estável. Nesta carta, um decaimento alfa desce duas casas e anda duas para a esquerda; um decaimento beta sobe uma e anda uma para a esquerda. Num minério de urânio antigo e intacto, todos os membros decaem ao mesmo ritmo.</p>
  <div class="btns"><button class="btn" data-act="next">Decaimento seguinte</button><button class="btn ghost" data-act="restart">Recomeçar</button></div>
</div>`,
};

Object.assign(WT.L.labels, {
  /* step 1 */
  "parent {#}": "pai {#}",
  "daughter {#}": "filho {#}",
  "stable {#}": "estável {#}",
  "parent ({#} s): {#}": "pai ({#} s): {#}",
  "daughter ({#} s): {#}": "filho ({#} s): {#}",
  "granddaughter (stable): {#}": "neto (estável): {#}",
  "daughter peaks: {#} %": "pico do filho: {#} %",
  "{#} s": "{#} s",
  "illustrative half-lives": "meias-vidas ilustrativas",
  /* step 2 */
  "radium{#}": "rádio{#}",
  "radon{#} gas": "gás radão{#}",
  "radium": "rádio",
  "radium activity": "atividade do rádio",
  "radon": "radão",
  "radon activity": "atividade do radão",
  "{#} d": "{#} d",
  "days →": "dias →",
  "day {#}: radon at {#} % of radium": "dia {#}: radão a {#} % do rádio",
  "A(radon) = A(radium) × ({#} − exp(−λt))": "A(radão) = A(rádio) × ({#} − exp(−λt))",
  "A(Rn) = A(Ra) × ({#} − exp(−λt))": "A(Rn) = A(Ra) × ({#} − exp(−λt))",
  /* step 3 */
  "Mo{#}": "Mo{#}",
  "Tc{#}m out": "Tc{#}m extraído",
  "Tc{#}m to the patient": "Tc{#}m para o doente",
  "molybdenum{#}": "molibdénio{#}",
  "dashed: never milked": "tracejado: nunca ordenhado",
  "activity": "atividade",
  "{#} h since last milking · Tc{#}m at {#} % of Mo{#}": "{#} h desde a última ordenha · Tc{#}m a {#} % do Mo{#}",
  "regrows to its peak in about {#} hours": "volta ao pico em cerca de {#} horas",
  /* step 4 */
  "neutrons →": "neutrões →",
  "grey: stable": "cinzento: estável",
  "protons ↑": "protões ↑",
  "alpha: {#} p, {#} n": "alfa: {#} p, {#} n",
  "alpha: loses {#} protons and {#} neutrons": "alfa: perde {#} protões e {#} neutrões",
  "beta: n → p": "beta: n → p",
  "beta: a neutron becomes a proton": "beta: um neutrão torna-se protão",
  "U{#} · half-life {#} billion yr · alpha next": "U{#} · meia-vida {#} mil milhões de anos · segue-se alfa",
  "Th{#} · half-life {#} days · beta next": "Th{#} · meia-vida {#} dias · segue-se beta",
  "Pa{#}m · half-life {#} min · beta next": "Pa{#}m · meia-vida {#} min · segue-se beta",
  "U{#} · half-life {#} yr · alpha next": "U{#} · meia-vida {#} anos · segue-se alfa",
  "U-234 · half-life 245,000 yr · alpha next": "U-234 · meia-vida 245 000 anos · segue-se alfa",
  "Th{#} · half-life {#} yr · alpha next": "Th{#} · meia-vida {#} anos · segue-se alfa",
  "Th-230 · half-life 75,000 yr · alpha next": "Th-230 · meia-vida 75 000 anos · segue-se alfa",
  "Ra{#} · half-life {#} yr · alpha next": "Ra{#} · meia-vida {#} anos · segue-se alfa",
  "Rn{#} · half-life {#} days · alpha next": "Rn{#} · meia-vida {#} dias · segue-se alfa",
  "Po{#} · half-life {#} min · alpha next": "Po{#} · meia-vida {#} min · segue-se alfa",
  "Pb{#} · half-life {#} min · beta next": "Pb{#} · meia-vida {#} min · segue-se beta",
  "Bi{#} · half-life {#} min · beta next": "Bi{#} · meia-vida {#} min · segue-se beta",
  "Po{#} · half-life {#} µs · alpha next": "Po{#} · meia-vida {#} µs · segue-se alfa",
  "Pb{#} · half-life {#} years · beta next": "Pb{#} · meia-vida {#} anos · segue-se beta",
  "Bi{#} · half-life {#} days · beta next": "Bi{#} · meia-vida {#} dias · segue-se beta",
  "Po{#} · half-life {#} days · alpha next": "Po{#} · meia-vida {#} dias · segue-se alfa",
  "Pb{#}: stable, the chain ends": "Pb{#}: estável, fim da cadeia",
  "step {#} of {#} · tap the nucleus": "passo {#} de {#} · toca no núcleo",
});
