/* Portuguese (pt-PT): fisout (Capítulo 13, neutrões de fissão) */
WT.L.ch.fisout = {
  num: "Capítulo 13", title: "Neutrões de fissão", short: "Neutrões de fissão",
  html: `
<div class="step">
  <p>Cada fissão liberta dois ou três neutrões: 2,4 em média. Em cima, uma fissão de cada vez: o núcleo de urânio rasga-se em dois fragmentos e as bolas azuis saem disparadas. São os neutrões <b>prontos</b>, emitidos em muito menos de um milionésimo de segundo.</p>
  <p>O gráfico da esquerda conta quantas fissões libertaram 0, 1, 2, 3 … neutrões. As barras são as fissões que disparaste; a linha fina em cada barra é a fração medida. Dispara mais e as barras assentam sobre as linhas.</p>
  <div class="btns"><button class="btn" data-act="f100">100 fissões</button><button class="btn ghost" data-act="f1000">1000 fissões</button></div>
</div>
<div class="step">
  <p>Nascem rápidos: cerca de 2 MeV em média, uns 80 milhões de vezes a energia de um neutrão lento num reator à temperatura ambiente. O gráfico da direita ordena os neutrões prontos por energia. A linha é a forma medida (o espectro de Watt): uma bossa perto de 1 MeV e uma cauda longa até 10 MeV.</p>
  <p>Neutrões tão rápidos raramente causam a fissão seguinte no urânio-235, por isso um reator começa por os abrandar, como mostra um capítulo posterior.</p>
  <div class="btns"><button class="btn" data-act="f100">100 fissões</button><button class="btn ghost" data-act="f1000">1000 fissões</button></div>
</div>
<div class="step">
  <p>Alguns chegam segundos depois: 0,65 % de todos os neutrões. Certos fragmentos são tão ricos em neutrões que, quando decaem mais tarde, o novo núcleo não consegue reter um dos seus neutrões e deixa-o sair. Esse neutrão tem de esperar pelo decaimento, muitas vezes segundos.</p>
  <p>A linha de baixo é um relógio que começa na fissão, de 0,01 s a 100 s; cada marca é dez vezes mais tarde do que a anterior. A bola à esquerda representa todos os neutrões prontos, emitidos de uma vez. Cada pontinho é um neutrão retardado: viaja ao longo da linha enquanto dura a sua espera, num relógio acelerado 20 vezes, e fica onde por fim saiu. Estes poucos neutrões tardios são o que torna um reator controlável: abrandam a resposta da cadeia de milésimos de segundo para segundos.</p>
  <div class="btns"><button class="btn" data-act="f1000">1000 fissões</button><button class="btn ghost" data-act="clear">Limpar</button></div>
</div>`,
};

Object.assign(WT.L.labels, {
  "n + U{#} → two fragments + neutrons": "n + U{#} → dois fragmentos + neutrões",
  "prompt neutrons per fission": "neutrões prontos por fissão",
  "lines: measured shares": "linhas: frações medidas",
  "mean {#}": "média {#}",
  "prompt-neutron energy (MeV)": "energia dos neutrões prontos (MeV)",
  "mean {#} MeV": "média {#} MeV",
  "line: measured shape": "linha: forma medida",
  "prompt": "prontos",
  "time after fission · clock sped up {#}×": "tempo após a fissão · relógio acelerado {#}×",
  "delayed {#} of {#} ({#} %)": "retardados {#} de {#} ({#} %)",
  "{#} fissions": "{#} fissões",
});
