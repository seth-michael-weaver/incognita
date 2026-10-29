/* Portuguese (pt-PT): gamma (Capítulo 10, emissão de fotões) */
WT.L.ch.gamma = {
  num: "Capítulo 10", title: "Emissão de raios gama", short: "Fotões",
  lead: "Quando nenhuma partícula sai, o núcleo arrefece emitindo fotões: raios gama, partículas de luz de alta energia. Esta saída está aberta a qualquer energia.",
  html: `
<div class="step">
  <p>Um estado quente a 8 MeV (milhões de eletrão-volts) liberta fotões (γ); o monte junto à escada recolhe onde caem. Abaixo de 2 MeV, os estados são uns poucos degraus com nome; acima, uma multidão que se adensa rapidamente com a energia (pontos cinzentos). Cada fotão leva a energia do seu salto, <i>E<sub>γ</sub></i>, e é desenhado mais brilhante em proporção a <i>E<sub>γ</sub></i>³.</p>
  <div class="formula">T<sub>γ</sub>(E<sub>γ</sub>) = 2π · E<sub>γ</sub><sup>2l+1</sup> · f(E<sub>γ</sub>)</div>
  <p>Por palavras: a facilidade com que sai um fotão de energia <i>E<sub>γ</sub></i> (<i>T<sub>γ</sub></i>, a porta do fotão do capítulo 9) cresce como <i>E<sub>γ</sub></i>³ para o tipo mais comum de fotão (dipolar, <i>l</i> = 1), vezes a <b>função de intensidade gama</b> <i>f</i>: a facilidade com que este núcleo radia a essa energia. Depois, tem de encontrar um estado onde cair. Os saltos pequenos têm uma multidão de estados à espera, mas quase não conseguem sair; os grandes saem facilmente, mas encontram poucos estados. Os vencedores ficam a meio.</p>
  <div class="ctl"><label for="gm-e0">Energia inicial</label><input id="gm-e0" type="range" data-bind="E0" min="3" max="9" step="0.5" value="8"><output data-show="E0" data-fmt="1"></output></div>
  <div class="btns"><button class="btn" data-act="emit">Emitir 100</button></div>
  <p>O monte atinge o máximo uns MeV abaixo do início: a maioria dos fotões leva de 2 a 4 MeV. Muda a energia inicial e o máximo acompanha-a.</p>
</div>
<div class="step">
  <h3>A ressonância gigante dipolar</h3>
  <p>O grande pico à direita é a <b>ressonância gigante dipolar</b>: todos os protões (tracejados) a oscilar para trás e para a frente contra todos os neutrões (cheios). A sua frequência fixa a energia de fotão que o núcleo absorve e emite com mais facilidade. A curva é a função de intensidade gama <i>f</i>, em escala logarítmica (cada degrau para cima é dez vezes mais).</p>
  <div class="ctl"><label for="gm-a">Número de massa A</label><input id="gm-a" type="range" data-bind="A" min="40" max="240" step="1" value="112"><output data-show="A" data-fmt="0"></output></div>
  <p>Arrasta o número de massa A (protões mais neutrões): os núcleos pesados oscilam mais devagar e vibram perto de 12 a 14 MeV; os leves, perto de 20. Um núcleo em decaimento emite fotões de apenas alguns MeV, por isso o que mais importa é a cauda sombreada de baixa energia.</p>
</div>
<div class="step">
  <h3>Intensidade magnética a baixa energia</h3>
  <p>Um núcleo deformado também radia de forma magnética: os seus protões (tracejados) e neutrões (cheios), duas bolas de râguebi, balançam um contra o outro como as lâminas de uma tesoura. Este <b>modo tesoura</b> fica perto de 3 MeV. O <b>spin-flip</b> (inversão de spin), perto de 8 MeV, são nucleões individuais a inverter o seu spin (as setas pequenas), com qualquer forma.</p>
  <div class="ctl"><label for="gm-b">Deformação β₂</label><input id="gm-b" type="range" data-bind="beta" min="0" max="0.35" step="0.01" value="0.25"><output data-show="beta" data-fmt="2"></output></div>
  <p>Arrasta a deformação β₂ (0 é uma esfera). Quanto mais esticado, mais fotões de tesoura saem; uma esfera não tem nenhum. Às energias mais baixas a intensidade volta a subir: é o <b>upbend</b> (subida), um gotejar de fotões moles, que o motor enfraquece à medida que o núcleo se deforma. Uma opção, desligada por defeito, usa sistemáticas de tesoura mais intensas que concordam com as medições de Oslo (quatro a cinco vezes mais intensas no urânio).</p>
</div>
<div class="step">
  <h3>Cascatas gama</h3>
  <p>Uma cascata são fotões emitidos uns atrás dos outros, desde os intervalos no topo (estados demasiado densos para listar, capítulo 8) até aos níveis com nome, esticados para se poderem ler (degrau cheio paridade +, oco −). Aí o motor deixa de estimar e segue as <b>razões de ramificação</b> tabeladas: as probabilidades medidas de cada nível decair para cada um dos inferiores.</p>
  <div class="btns"><button class="btn" data-act="drop">Largar uma cascata</button></div>
  <p>Carrega no botão algumas vezes: a parte de cima muda de cada vez; o final segue um de poucos caminhos medidos.</p>
</div>
<div class="step">
  <h3>Produção de isómeros</h3>
  <p>O nível 11/2− a 0,40 MeV é um <b>isómero</b>: o seu spin é tão diferente do dos níveis abaixo que um fotão mal os consegue ligar, por isso vive de segundos a anos, e o que lá cai fica. O motor trata qualquer nível que viva mais de um segundo como um ponto final. Cada bola é uma cascata, que acaba no monte do isómero ou no do estado fundamental.</p>
  <div class="ctl"><label for="gm-j">Spin de entrada</label><input id="gm-j" type="range" data-bind="J0" min="0" max="8" step="1" value="2" data-instant><output id="gm-jout">5/2</output></div>
  <p>Arrasta o spin de entrada, onde as cascatas começam, e os montes recomeçam. A fração que acaba no isómero, a <b>razão isomérica</b>, depende dele: um início de spin alto alimenta o isómero de spin alto; um de spin baixo passa-lhe ao lado e desce até ao estado fundamental.</p>
</div>
<div class="step">
  <h3>Captura radiativa</h3>
  <p>Um núcleo que acabou de absorver um neutrão lento tem duas portas de saída (capítulo 9): fotões (em cima) e o neutrão que volta a sair (à direita). A abertura de cada porta é a sua <b>largura</b>, em eV: a rapidez com que o núcleo decai por ela. A largura radiativa quase não muda; a do neutrão cresce com a velocidade do neutrão.</p>
  <div class="ctl"><label for="gm-e">Energia do neutrão</label><input id="gm-e" type="range" data-bind="lgE" min="-2" max="3.3" step="0.02" value="0"><output id="gm-eout">1.0 keV</output></div>
  <p>Arrasta a energia do neutrão, de 10 eV a 2 MeV. A <b>captura</b>, (n,γ), significa que o neutrão fica e sai um fotão: a 10 eV ganha quase sempre e acima de alguns keV passa a ser uma fração pequena. A largura radiativa no limiar está medida para centenas de núcleos, e serve para verificar a função de intensidade gama. Por defeito o motor usa a sua; uma opção escala a função de intensidade de cada núcleo medido até as duas coincidirem.</p>
  <div class="aside">No código: <code>gamma/parameters.py</code> (intensidades E1 tabeladas; sistemáticas da ressonância gigante, spin-flip, tesoura e upbend), <code>gamma/strength.py</code> (<i>f</i>(E<sub>γ</sub>) para cada multipolo), <code>gamma/transmission.py</code> (T<sub>γ</sub> e a largura radiativa média), <code>structure/levels.py</code> (razões de ramificação, isómeros), <code>emission/multiple.py</code> (a cascata). Opcionais, desligadas por defeito: <code>gamma/scissors.py</code> (tesoura mais intensa), <code>gamma/ggnorm.py</code> (ajustar ao ⟨Γγ⟩ medido, até ao chumbo), <code>gamma/actphys.py</code> (ambas, para actinídeos).</div>
</div>`,
};
Object.assign(WT.L.labels, {
  // scene 1: emit
  "energy ↑": "energia ↑",
  "named levels": "níveis com nome",
  "a crowd of states": "uma multidão de estados",
  "{#} MeV": "{#} MeV",
  "hot state, {#} MeV": "estado quente, {#} MeV",
  "most photons ≈ {#} MeV": "mais frequentes ≈ {#} MeV",
  "small drops: faint (E³ tiny)": "saltos pequenos: ténues (E³ minúsculo)",
  "big drops: bright, but few states to land on": "saltos grandes: brilhantes, mas com poucos estados onde cair",
  // scene 2: gdr
  "protons": "protões",
  "neutrons": "neutrões",
  "A = {#}: rings at {#} MeV": "A = {#}: vibra a {#} MeV",
  "peak {#} MeV": "pico {#} MeV",
  "giant resonance at {#} MeV": "ressonância gigante a {#} MeV",
  "width ≈ {#} MeV": "largura ≈ {#} MeV",
  "decays use this": "a que é usada",
  "shaded: the tail decays use": "sombreado: a cauda que é usada",
  "photon energy (MeV) →": "energia do fotão (MeV) →",
  "photon strength f (log scale) ↑": "função de intensidade f (escala log) ↑",
  // scene 3: m1
  "a sphere has no blades: no scissors": "uma esfera não tem lâminas: sem tesoura",
  "scissors ≈ {#} MeV: strength {#} % of the most stretched": "tesoura ≈ {#} MeV: intensidade a {#} % da mais esticada",
  "spin-flip ≈ {#} MeV: steady, any shape (thick photons)": "spin-flip ≈ {#} MeV: constante, qualquer forma (fotões grossos)",
  "upbend below {#} MeV: soft photons, plenty at this shape": "upbend abaixo de {#} MeV: fotões moles, muitos com esta forma",
  "upbend below {#} MeV: soft photons, fewer at this shape": "upbend abaixo de {#} MeV: fotões moles, menos com esta forma",
  "upbend below {#} MeV: soft photons, few at this shape": "upbend abaixo de {#} MeV: fotões moles, poucos com esta forma",
  // scene 4: cascade
  "ground state": "estado fundamental",
  "isomer": "isómero",
  "isomer: long-lived": "isómero: vida longa",
  "bins: too dense to list": "intervalos: demasiado densos",
  "one photon at a time": "um fotão de cada vez",
  "measured branching ratios": "ramificações medidas",
  "▬ parity +   ▭ parity −": "▬ paridade +   ▭ paridade −",
  // scene 5: isomer
  "entrance: J = {#}/{#}": "entrada: J = {#}/{#}",
  "isomer: {#} ({#} %)": "isómero: {#} ({#} %)",
  "ground state: {#} ({#} %)": "estado fundamental: {#} ({#} %)",
  "many cascades: ≈ {#} % isomer": "muitas cascatas: ≈ {#} % isómero",
  "over many cascades from J = {#}/{#}: ≈ {#} % end on the isomer": "em muitas cascatas a partir de J = {#}/{#}: ≈ {#} % acabam no isómero",
  // scene 6: capture
  "photon door: {#} eV, barely changes": "porta do fotão: {#} eV, quase não muda",
  "captured (n,γ): {#} ({#} %)": "capturados (n,γ): {#} ({#} %)",
  "neutron: {#} eV": "neutrão: {#} eV",
  "neutron door: {#} eV, wider when faster": "porta do neutrão: {#} eV, mais larga se for mais rápido",
  "back out: {#} ({#} %)": "voltam a sair: {#} ({#} %)",
  "more doors open (target left excited)": "mais portas (alvo excitado)",
  "{#} eV neutrons →": "neutrões de {#} eV →",
  "{#} keV neutrons →": "neutrões de {#} keV →",
  "{#} MeV neutrons →": "neutrões de {#} MeV →",
  "slow neutrons: the photon door wins": "neutrões lentos: ganha a porta do fotão",
  "the neutron door wins; capture takes about {#} %": "ganha a porta do neutrão; a captura leva ≈ {#} %",
  "fast: capture is a rare event": "rápidos: a captura é um acontecimento raro",
});
