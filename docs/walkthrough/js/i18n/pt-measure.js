/* Portuguese (pt-PT): measure (chapter 11) */
WT.L.ch.measure = {
  num: "Capítulo 11", title: "O que sai", short: "Observáveis",
  lead: "Uma experiência, um reator ou uma estrela só veem um punhado de números. Este capítulo mostra como o motor transforma o que acontece dentro do núcleo nesses números.",
  html: `
<div class="step">
  <p>O disco pálido à volta de cada núcleo é a sua <b>secção eficaz</b>: a área que um neutrão tem de acertar para que ocorra uma reação, não o tamanho real do núcleo. Um feixe chega da esquerda e atravessa uma folha fina de núcleos; a fração que reage é essa área vezes o número de núcleos que encontra. A unidade é o barn (10⁻²⁴ cm², mais ou menos a face de um núcleo de urânio).</p>
  <div class="ctl"><label for="mea-e">Energia do neutrão (MeV)</label><input id="mea-e" type="range" data-bind="E" min="0.1" max="20" step="0.1" value="2"><output data-show="E" data-fmt="1"></output></div>
  <p>Baixa a energia e os discos incham: um neutrão lento é uma onda larga e reage a partir de mais longe. A alta energia o disco encolhe até ao próprio núcleo.</p>
</div>
<div class="step">
  <h3>Com a energia abrem-se novas saídas</h3>
  <p>Cada porta é uma saída, ou <b>canal</b>: o neutrão ressalta para fora (elástico), deixa o alvo excitado (n′), arranca mais neutrões (2n, 3n), é capturado e só saem fotões (γ), ou sai em vez disso um protão ou uma partícula α. Uma porta com cadeado tem um <b>limiar</b>: a reação custa mais energia do que a que o neutrão traz.</p>
  <div class="ctl"><label for="mea-e2">Energia do neutrão (MeV)</label><input id="mea-e2" type="range" data-bind="E" min="0.1" max="20" step="0.1" value="2"><output data-show="E" data-fmt="1"></output></div>
  <p>Arrasta a energia para lá de um limiar e essa porta abre-se com um clarão; os baldes enchem-se conforme a fração de cada canal, e cada porta nova tira parte às outras. Os limiares vêm das massas dos núcleos; as frações, da competição do capítulo 6.</p>
</div>
<div class="step">
  <h3>O que um detetor vê</h3>
  <p>Os dois montes são os neutrões que chegam à metade dianteira e à metade traseira de um anel de detetores, ordenados por energia. O feixe é pulsado, por isso o tempo de voo de cada neutrão dá a sua energia: os rápidos chegam primeiro.</p>
  <div class="ctl"><label for="mea-ein">Energia incidente (MeV)</label><input id="mea-ein" type="range" data-bind="Ein" min="5" max="60" step="0.5" value="30"><output data-show="Ein" data-fmt="0"></output></div>
  <p>Os dois montes têm uma bossa de neutrões lentos, <b>evaporados</b>: libertam-se do núcleo composto depois de a energia estar repartida, igualmente em todas as direções. Só o monte dianteiro tem uma longa cauda rápida: neutrões de <b>pré-equilíbrio</b>, que saem das primeiras colisões ainda a mover-se mais ou menos com o feixe. Sobe a energia incidente e a cauda cresce.</p>
</div>
<div class="step">
  <h3>Para onde vão</h3>
  <p>A pétala mostra quantos neutrões saem em cada direção; o feixe chega da esquerda. Os evaporados esqueceram o feixe e saem igualmente em todas as direções; os rápidos de pré-equilíbrio inclinam-se para a frente. A regra de Kalbach fixa quanto, com um único declive <i>a</i> que cresce com a energia de saída. O motor também pode escrever estas distribuições angulares, como saída opcional.</p>
  <div class="ctl"><label for="mea-eo">Energia de saída (MeV)</label><input id="mea-eo" type="range" data-bind="Eout" min="1" max="45" step="0.5" value="25"><output data-show="Eout" data-fmt="1"></output></div>
  <p>Baixa a energia de saída e a pétala arredonda-se: os neutrões lentos são sobretudo evaporados.</p>
  <div class="formula">dσ/dΩ ∝ e<sup>a cos θ</sup></div>
</div>
<div class="step">
  <h3>Numa estrela</h3>
  <p>O monte de baixo recolhe as energias dos neutrões capturados no gás quente de uma estrela. As suas velocidades seguem uma distribuição de Maxwell fixada pela temperatura <i>kT</i> (30 keV são cerca de 350 milhões de graus); os rastos mais longos são neutrões mais rápidos, e cada passagem junto a um núcleo pode acabar num clarão de captura.</p>
  <div class="ctl"><label for="mea-kt">Temperatura kT (keV)</label><input id="mea-kt" type="range" data-bind="kT" min="5" max="100" step="1" value="30"><output data-show="kT" data-fmt="0"></output></div>
  <p>Os neutrões lentos são capturados com facilidade mas passam raramente, e os rápidos são poucos, por isso a maioria das capturas vem de uma janela com alguns <i>kT</i> de largura. A taxa sobre todo o gás é a <b>secção eficaz de média maxwelliana</b> (MACS), em milibarns (mb). Aquece o gás e a janela desloca-se para energias mais altas, onde o alvo é mais pequeno. A MACS obtém-se integrando a curva de captura do motor.</p>
</div>
<div class="step">
  <h3>O alvo também está quente</h3>
  <p>As bolas mostram que fração dos núcleos do alvo está em cada um dos seus níveis mais baixos a esta temperatura. Numa estrela alguns alvos já estão excitados, e cada nível excitado é uma entrada diferente para o mesmo núcleo composto. Um nível com spin <i>J</i> acolhe mais porque tem 2<i>J</i>+1 orientações.</p>
  <div class="ctl"><label for="mea-kt2">Temperatura kT (keV)</label><input id="mea-kt2" type="range" data-bind="kT" min="5" max="100" step="1" value="30"><output data-show="kT" data-fmt="0"></output></div>
  <p>Sobe a temperatura e vê os núcleos a subir. Uma taxa estelar calcula a captura a partir de cada nível povoado e soma os resultados com estas frações; os pesos somam a função de partição <i>G</i>, e a razão face à taxa a partir do estado fundamental é o <b>fator de reforço estelar</b>. O motor pode fazê-lo como opção, desligada por defeito; normalmente cada alvo parte do seu estado fundamental.</p>
</div>
<div class="step">
  <h3>Que grau de certeza tem tudo isto?</h3>
  <p>Cada disco ténue é uma execução do motor com os seus dados de entrada alterados ao acaso: a profundidade do poço ótico, a densidade de níveis e a intensidade fotónica, cada uma conhecida só com uma margem de alguns por cento. A dispersão de muitas execuções é uma incerteza honesta: <b>Monte Carlo total</b>.</p>
  <div class="btns"><button class="btn" data-act="tmc1">Executar uma variante</button><button class="btn ghost" data-act="tmc">Executar 10</button><button class="btn ghost" data-act="clear">Limpar</button></div>
  <p>Um contorno nítido significa que os dados de entrada fixam a resposta; um contorno difuso, que não, e é aí que novas medições ajudariam mais.</p>
  <div class="aside">No código: <code>emission/channels.py</code> (canais exclusivos e residuais), <code>specout.py</code> e <code>specang.py</code> (espectros de saída, distribuições angulares e secções eficazes duplamente diferenciais, escritos só se forem pedidos), <code>astro/stellar.py</code> (captura a partir de níveis do alvo povoados termicamente, opcional), <code>tmc.py</code> (o amostrador de Monte Carlo total). As MACS do estado fundamental obtêm-se das curvas de captura em <code>validation/differential/core.py</code>.</div>
</div>`,
};
Object.assign(WT.L.labels, {
  // area
  "each disc: σ ≈ {#} b": "cada disco: σ ≈ {#} b",
  "each disc: cross section σ ≈ {#} b, the area a neutron must hit": "cada disco: secção eficaz σ ≈ {#} b, a área a acertar",
  "beam →": "feixe →",
  "nucleus's own face ≈ {#} b · {#} % reacts": "face do núcleo ≈ {#} b · reage {#} %",
  "the nucleus's own face ≈ {#} b · {#} % of the beam reacts in this foil": "a face do próprio núcleo ≈ {#} b · nesta folha reage {#} % do feixe",
  "slow: the neutron's wave reaches well past the surface": "lento: a onda do neutrão vai muito além da superfície",
  "the target still looks bigger than the nucleus": "o alvo ainda parece maior do que o núcleo",
  "fast: close to the nucleus's own size": "rápido: perto do tamanho do próprio núcleo",
  // doors
  "elastic": "elástico", "n′ inelastic": "n′ inelástico", "{#}n": "{#}n", "γ capture": "captura γ", "p": "p", "α": "α", "n′": "n′",
  "{#}n · {#} MeV": "{#}n · {#} MeV", "p · {#} MeV": "p · {#} MeV", "α · {#} MeV": "α · {#} MeV", "n′ inelastic · {#} MeV": "n′ inelástico · {#} MeV",
  "opens at {#} MeV": "abre a {#} MeV",
  "{#} MeV": "{#} MeV",
  // detect
  "forward half": "metade dianteira", "backward half": "metade traseira",
  "pulsed beam": "feixe pulsado", "pulsed beam →": "feixe pulsado →",
  "backward": "trás", "backward detectors": "detetores traseiros",
  "forward": "frente", "forward detectors": "detetores dianteiros",
  "outgoing neutron energy from the flight time (MeV) →": "energia do neutrão emitido pelo tempo de voo (MeV) →",
  "fast tail": "cauda rápida", "fast tail: pre-equilibrium": "cauda rápida: pré-equilíbrio",
  "evaporated hump": "bossa evaporada", "hump: evaporated, every way alike": "bossa: evaporados, igual em todas as direções",
  "{#} % leave before the energy is shared": "{#} % saem antes de a energia se repartir",
  // angle
  "beam": "feixe",
  "forward-to-backward ratio ≈ {#}  ·  slope a ≈ {#}": "razão frente/trás ≈ {#}  ·  declive a ≈ {#}",
  "mostly evaporated: every direction alike": "sobretudo evaporados: todas as direções por igual",
  "a mix: the fast share leans forward": "uma mistura: a parte rápida inclina-se para a frente",
  "mostly pre-equilibrium: strongly forward": "sobretudo pré-equilíbrio: muito para a frente",
  "forward →": "frente →",
  // star
  "{#} keV": "{#} keV",
  "kT = {#} keV": "kT = {#} keV",
  "energies of captured neutrons": "energias dos neutrões capturados",
  "each capture drops here, by the neutron's energy: the window that counts": "cada captura cai aqui segundo a energia do neutrão: a janela que conta",
  "MACS ≈ {#} mb at kT = {#} keV · captures watched: {#}": "MACS ≈ {#} mb a kT = {#} keV · capturas observadas: {#}",
  // hot target
  "{#}⁺  ground state": "{#}⁺  fundamental", "{#}⁺  {#} keV": "{#}⁺  {#} keV",
  "target levels, with the share of nuclei sitting on each": "níveis do alvo, com a fração de núcleos em cada um",
  "{#} % start from the ground state · partition function G ≈ {#}": "{#} % partem do estado fundamental · função de partição G ≈ {#}",
  // TMC
  "optical well": "poço ótico", "optical well depth": "profundidade do poço ótico",
  "level density": "densidade de níveis", "photon strength": "intensidade fotónica",
  "σ ≈ {#} b ": "σ ≈ {#} b ", "σ ≈ {#} mb ": "σ ≈ {#} mb ",
  "σ ≈ {#} b ±{#} %": "σ ≈ {#} b ±{#} %", "σ ≈ {#} mb ±{#} %": "σ ≈ {#} mb ±{#} %",
  "dashed: best inputs · each disc drawn at its own scale": "tracejado: melhores dados · cada disco à sua escala",
  "dashed ring: the best-value inputs · each energy drawn at its own scale (disc area ∝ σ)": "anel tracejado: dados de melhor valor · cada energia à sua própria escala (área ∝ σ)",
  "{#} runs of the engine, each with its inputs nudged at random": "{#} execuções do motor, cada uma com os dados de entrada alterados ao acaso",
});
