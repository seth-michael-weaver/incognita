/* Portuguese (pt-PT): compound (chapter 5) */
WT.L.ch.compound = {
  num: "Capítulo 5", title: "Partilhar a energia", short: "Núcleo composto",
  lead: "Quando terminam as primeiras colisões rápidas, todos os nucleões partilham a energia. Este estado assente é o núcleo composto. Para prever o que fará a seguir, o motor precisa de saber de quantas maneiras pode guardar a sua energia.",
  html: `
<div class="step">
  <p>Um neutrão choca contra um lado de um núcleo. A sua energia, mais a que se liberta ao ser capturado, começa como um ponto quente (o brilho laranja); as colisões vão-na passando, e em cerca de 10⁻²¹ segundos cada nucleão leva uma parte.</p>
  <div class="btns"><button class="btn" data-act="hit">Atingir de outro lado</button></div>
  <p>Carrega no botão para lançar o neutrão de outro lado. O brilho acaba sempre da mesma maneira: o núcleo <b>esqueceu como se formou</b>. É o núcleo composto de Bohr. A partir daqui só contam três dados: a sua energia, o seu spin (quanto roda) e a sua paridade (uma etiqueta + ou − para a sua simetria de espelho).</p>
</div>
<div class="step">
  <h3>De níveis separados a um contínuo</h3>
  <p>A escada da esquerda contém os estados do núcleo, com a energia para cima; a janela da direita amplia uma faixa de 1 MeV à volta da bola laranja. Perto do fundo os degraus estão muito afastados, e cada um foi medido. Mais acima, as maneiras de repartir a energia entre 56 nucleões multiplicam-se até os degraus se fundirem numa banda contínua, o contínuo.</p>
  <div class="ctl"><label for="cn-e">Energia de excitação</label><input id="cn-e" type="range" data-bind="E" min="0" max="20" step="0.1" value="6.5"><output data-show="E" data-fmt="1"></output></div>
  <p>Arrasta a energia de excitação (a energia guardada acima do estado mais baixo, em MeV) e observa a janela. A <b>densidade de níveis</b> ρ, estados por MeV, cresce aproximadamente como e<sup>2√(aE)</sup>, onde <i>a</i> marca o ritmo de cada núcleo: alguns por MeV a 3 MeV, centenas perto de 8 MeV (onde um neutrão poderia escapar), milhões perto de 20 MeV. Lá em cima o motor trabalha com a própria ρ.</p>
</div>
<div class="step">
  <h3>Três peças unidas numa energia</h3>
  <p>A altura do terreno é a densidade de níveis em escala logarítmica, com a energia para a direita. Em baixo à esquerda estão os níveis contados. A prancha reta é a lei de <b>temperatura constante</b>: ρ multiplica-se por e (cerca de 2,7) a cada <i>T</i> MeV, onde <i>T</i> é a temperatura nuclear. A encosta é o <b>gás de Fermi</b>, que trata os nucleões como partículas independentes. Exceto para os alvos mais pesados, para os quais lê densidades tabeladas, o motor usa este par por defeito.</p>
  <div class="ctl"><label for="cn-ex">Energia de junção</label><input id="cn-ex" type="range" data-bind="Ex" min="4.5" max="12" step="0.05" value="6"><output data-show="Ex" data-fmt="1"></output></div>
  <p>Arrasta a energia de junção: a união desliza pela colina e a prancha roda para a encontrar com a mesma altura e o mesmo declive. As duas pilhas em baixo comparam os níveis que a prancha prevê com os realmente contados. Só uma união os iguala; aí a prancha fica verde. É essa a energia que o motor escolhe.</p>
</div>
<div class="step">
  <h3>Camadas que se fundem</h3>
  <p>Níveis de um só nucleão, dois nucleões por nível, para dois núcleos. À esquerda, uma camada fechada: tudo o que está abaixo de um grande hiato está cheio, por isso qualquer movimento paga o hiato inteiro. À direita, um núcleo de meio de camada com o nível superior meio cheio, por isso há movimentos baratos desde o início. Cada contador mostra quantas configurações admitem esse calor.</p>
  <div class="ctl"><label for="cn-u">Calor (excitação)</label><input id="cn-u" type="range" data-bind="U" min="0" max="40" step="0.5" value="3"><output data-show="U" data-fmt="1"></output></div>
  <p>Sobe o calor e vê como os nucleões saltam. Com pouco calor, faltam configurações à camada fechada; com calor suficiente o hiato deixa de importar e ambas as contagens crescem da mesma maneira. O <b>parâmetro de densidade de níveis</b> <i>a</i> traduz isto: os ponteiros começam afastados e convergem para o valor suave <i>ã</i> ao longo de cerca de 10 MeV. O motor esbate a correção de camadas δW a um ritmo γ:</p>
  <div class="formula">a(U) = ã · [1 + δW · (1 − e<sup>−γU</sup>) / U]</div>
</div>
<div class="step">
  <h3>Ordenados por spin e paridade</h3>
  <p>Os estados de uma energia caem em gavetas segundo o spin <i>J</i>, o momento angular do núcleo: fichas cheias para paridade +, ocas para −. As gavetas do meio são as que mais se enchem, seguindo (2<i>J</i>+1) e<sup>−(J+½)²/2σ²</sup>, onde o corte de spin σ fixa a largura. As duas paridades saem mais ou menos iguais.</p>
  <div class="ctl"><label for="cn-u2">Excitação</label><input id="cn-u2" type="range" data-bind="U2" min="1" max="30" step="0.5" value="8"><output data-show="U2" data-fmt="1"></output></div>
  <div class="btns"><button class="btn ghost" data-act="deform">Deformar o núcleo</button></div>
  <p>Sobe a excitação: σ cresce, porque um núcleo mais quente pode ter mais spin. Depois carrega em Deformar. Um núcleo com forma de bola de râguebi também pode rodar como um todo, por isso cada gaveta ganha estados (as fichas azuis): é o <b>reforço coletivo</b>. Por defeito, o motor só o acrescenta para alvos com mais de cerca de 215 nucleões.</p>
</div>
<div class="step">
  <h3>Cortado em intervalos</h3>
  <p>Acima do último nível contado, o motor corta o contínuo em faixas de igual largura em energia, chamadas intervalos (bins). Em cada intervalo os pontos juntam-se num bloco de ρ·ΔE estados (ΔE é a largura do intervalo), repartido por spin e paridade como acima.</p>
  <div class="ctl"><label for="cn-emax">Topo da escada</label><input id="cn-emax" type="range" data-bind="Emax" min="8" max="30" step="0.5" value="14"><output data-show="Emax" data-fmt="1"></output></div>
  <div class="btns"><button class="btn ghost" data-act="rebin">Reordenar</button></div>
  <p>Arrasta o topo da escada, a maior energia que o neutrão pode trazer. O mesmo número de intervalos tem de cobrir mais energia, por isso cada um fica mais alto. A bola laranja desce de intervalo em intervalo: cada passo seguinte (escolher uma saída, a cascata de fotões, o percurso pela carta) trabalha sobre estes intervalos. Aqui desenham-se dez; o motor usa até 40.</p>
  <div class="aside">No código: <code>density/parameters.py</code> (<i>a</i>(U) de Ignatyuk, corte de spin, distribuição de Wigner, reforço coletivo), <code>density/models.py</code> (temperatura constante, gás de Fermi, tabelas), <code>density/matching.py</code> (a energia de junção a partir dos níveis contados), <code>core/grids.py</code> (intervalos de excitação).</div>
</div>`,
};
(function () {
  const L = {
    // scene 1
    "a neutron comes in": "chega um neutrão",
    "a hot spot: the energy is still local": "um ponto quente: a energia ainda está localizada",
    "equilibrium: every nucleon holds a share": "equilíbrio: cada nucleão tem uma parte",
    "no trace left of where it was hit": "não fica rasto de onde foi atingido",
    // scene 2
    "ground state": "estado fundamental",
    "{#}–{#} MeV, magnified": "{#}–{#} MeV, ampliado",
    "no level in this slice": "nenhum nível nesta faixa",
    "{#} rung in {#} MeV": "{#} degrau em {#} MeV",
    "{#} rungs in {#} MeV": "{#} degraus em {#} MeV",
    "{#} rung in this {#}-MeV slice": "{#} degrau nesta faixa de {#} MeV",
    "{#} rungs in this {#}-MeV slice": "{#} degraus nesta faixa de {#} MeV",
    "about {#} rungs: too close to draw": "cerca de {#} degraus: impossível desenhá-los",
    "about {#}k rungs: too close to draw": "cerca de {#} mil degraus: impossível desenhá-los",
    "about {#}M rungs: too close to draw": "cerca de {#} M de degraus: impossível desenhá-los",
    "about {#}B rungs: too close to draw": "cerca de {#} mil M de degraus: impossível desenhá-los",
    "about {#} rungs in this slice: too close to draw": "cerca de {#} degraus nesta faixa: impossível desenhá-los",
    "about {#} thousand rungs in this slice: too close to draw": "cerca de {#} mil degraus nesta faixa: impossível desenhá-los",
    "about {#} million rungs in this slice: too close to draw": "cerca de {#} milhões de degraus nesta faixa: impossível desenhá-los",
    "about {#} billion rungs in this slice: too close to draw": "cerca de {#} mil milhões de degraus nesta faixa: impossível desenhá-los",
    "each one measured: energy, spin and parity": "cada um medido: energia, spin e paridade",
    "the rungs are multiplying": "os degraus multiplicam-se",
    "a continuum: the engine uses ρ itself": "um contínuo: o motor usa a própria ρ",
    "≈ energy to free a neutron": "≈ energia para libertar um neutrão",
    "energy ↑": "energia ↑",
    // scene 3
    "gap: plank below the rungs": "desvio: prancha abaixo dos degraus",
    "gap: plank above the rungs": "desvio: prancha acima dos degraus",
    "counted levels": "níveis contados",
    "CT plank": "prancha TC",
    "constant-temperature plank": "prancha de temperatura constante",
    "Fermi-gas hillside": "encosta do gás de Fermi",
    "joint {#} MeV": "união {#} MeV",
    "energy →": "energia →",
    "+{#} more": "+{#} mais",
    "{#} counted": "{#} contados",
    "{#} predicted": "{#} previstos",
    "{#}+ predicted": "{#}+ previstos",
    "equal: the plank rests on the counted rungs": "iguais: a prancha assenta nos degraus contados",
    "too few: the plank is too steep and sinks": "poucos: a prancha é demasiado inclinada e afunda",
    "too many: the plank is too shallow and floats": "demasiados: a prancha é demasiado plana e flutua",
    // scene 4
    "closed shell": "camada fechada",
    "mid-shell": "meio de camada",
    "gap": "hiato",
    "no arrangement holds this heat": "nenhuma configuração admite este calor",
    "≈ {#} arrangement": "≈ {#} configuração",
    "≈ {#} arrangements": "≈ {#} configurações",
    "≈ {#} thousand arrangements": "≈ {#} mil configurações",
    "≈ {#} million arrangements": "≈ {#} milhões de configurações",
    "≈ {#} billion arrangements": "≈ {#} mil milhões de configurações",
    "a ≈ {#}": "a ≈ {#}",
    "cold: nobody can move": "frio: ninguém se pode mexer",
    "temperature ≈ {#} MeV": "temperatura ≈ {#} MeV",
    // scene 5
    "states at {#} MeV": "estados a {#} MeV",
    "spin J →": "spin J →",
    "+ parity": "paridade +",
    "− parity": "paridade −",
    "rotation ×{#}": "rotação ×{#}",
    "added by rotation: ×{#} (a few drawn)": "acrescentados pela rotação: ×{#} (desenham-se alguns)",
    "spread σ ≈ {#}: most states near J ≈ {#}": "largura σ ≈ {#}: a maioria dos estados perto de J ≈ {#}",
    "deformed: it can rotate": "deformado: pode rodar",
    "spherical": "esférico",
    // scene 6
    "≈ {#} thousand": "≈ {#} mil",
    "≈ {#} million": "≈ {#} milhões",
    "≈ {#} billion": "≈ {#} mil milhões",
    "≈ {#}k": "≈ {#} mil",
    "≈ {#}M": "≈ {#} M",
    "≈ {#}B": "≈ {#} mil M",
    "{#} bins, each {#} MeV wide": "{#} intervalos de {#} MeV cada",
    "counted": "contados",
    "states in each bin": "estados em cada intervalo",
  };
  Object.assign(WT.L.labels, L);
})();
