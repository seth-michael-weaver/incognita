/* Portuguese (pt-PT): omp (Capítulo 5, o modelo ótico) */
WT.L.ch.omp = {
  num: "Capítulo 5", title: "Uma bola de cristal enevoada", short: "Modelo ótico",
  lead: "Antes de mais nada, o motor faz uma pergunta mais simples: como é que o núcleo se apresenta a um neutrão que chega?",
  html: `
<div class="step">
  <p>Em mecânica quântica, um neutrão é também uma onda. A imagem mostra uma a chegar da esquerda, com as cristas como faixas brilhantes, em direção a um núcleo (o círculo tracejado). Ainda nada atua sobre ela, por isso as cristas atravessam-no sem mudar.</p>
  <div class="ctl"><label for="omp-e">Energia do neutrão (MeV)</label><input id="omp-e" type="range" data-bind="E" min="0.2" max="40" step="0.1" value="8"><output data-show="E" data-fmt="1"></output></div>
  <p>Arrasta a energia e observa, em baixo, o comprimento de onda, em femtómetros (fm, 10⁻¹⁵ m). Os neutrões lentos têm ondas longas: abaixo de cerca de 9 MeV, um comprimento de onda é mais largo do que todo este núcleo.</p>
</div>
<div class="step">
  <h3>A parte real atrai</h3>
  <p>O <b>potencial ótico</b> é a força média de todo o núcleo sobre o neutrão. A sua <em>parte real</em> é um poço com cerca de 50 MeV de profundidade: lá dentro o neutrão acelera, por isso as cristas aproximam-se umas das outras. O motor dá-lhe uma forma de Woods–Saxon, plana e funda no centro, que se desvanece suavemente até zero na superfície.</p>
</div>
<div class="step">
  <h3>A parte imaginária absorve</h3>
  <p>A sombra atrás do núcleo são os neutrões perdidos em reações. A <em>parte imaginária</em> do potencial representa-os: encolhe a onda em vez de a desviar, sobretudo perto da superfície (o anel colorido).</p>
  <div class="ctl"><label for="omp-w">Absorção W (MeV)</label><input id="omp-w" type="range" data-bind="W" min="0" max="14" step="0.5" value="7"><output data-show="W" data-fmt="1"></output></div>
  <p>Leva <i>W</i> a 0 e a sombra desaparece: sem absorção não há reações. Daí o nome de modelo ótico: o núcleo é uma bola de vidro enevoada que em parte desvia e em parte absorve.</p>
</div>
<div class="step">
  <h3>A pontaria conta</h3>
  <p>Visto de frente, o alvo divide-se em anéis, um por cada <b>onda parcial</b> <i>l</i> = 0, 1, 2, … Um neutrão que passa a uma distância <i>b</i> do centro transporta um <b>momento angular</b> <i>l</i> ≈ <i>k b</i>, em que <i>k</i> cresce com a energia. Quanto mais escuro é um anel, maior é o seu <b>coeficiente de transmissão</b> <i>T<sub>l</sub></i>: a probabilidade de um neutrão nesse anel ser absorvido.</p>
  <div class="ctl"><label for="omp-e3">Energia do neutrão (MeV)</label><input id="omp-e3" type="range" data-bind="E" min="0.2" max="40" step="0.1" value="8"><output data-show="E" data-fmt="1"></output></div>
  <div class="btns"><button class="btn" data-act="fire">Disparar 200 neutrões</button></div>
  <p>Os clarões cor de laranja são neutrões absorvidos; as barras comparam a fração absorvida em cada anel com o <i>T<sub>l</sub></i> do modelo (a marca). Os anéis interiores absorvem quase tudo; os exteriores deixam passar os neutrões. A baixa energia os anéis são enormes e só <i>l</i> = 0 conta.</p>
</div>
<div class="step">
  <h3>Passar ao lado do núcleo</h3>
  <p>Um neutrão com muito momento angular passa demasiado longe para tocar no núcleo: é a <b>barreira centrífuga</b>. Visto de cima, cada neutrão aqui pertence a uma mesma onda parcial <i>l</i>, por isso passa à mesma <b>distância de passagem</b> <i>b</i> ≈ (<i>l</i>+½)/<i>k</i> (o círculo tracejado).</p>
  <p>Mas cada neutrão é uma onda, esbatida ao longo de cerca de um comprimento de onda reduzido λ̄ (o halo). Mesmo quando a trajetória falha, a orla difusa pode roçar a superfície e entrar: o <b>efeito túnel</b>.</p>
  <div class="ctl"><label for="omp-l">Onda parcial l</label><input id="omp-l" type="range" data-bind="L" min="0" max="8" step="1" value="3" data-instant><output data-show="L" data-fmt="0"></output></div>
  <div class="ctl"><label for="omp-e2">Energia (MeV)</label><input id="omp-e2" type="range" data-bind="E" min="0.2" max="40" step="0.1" value="8"><output data-show="E" data-fmt="1"></output></div>
  <p>Aumenta <i>l</i> e a trajetória afasta-se: entram menos. Aumenta a energia e a mesma <i>l</i> passa mais perto, menos esbatida. O motor calcula cada <i>T<sub>l</sub></i> de forma exata, resolvendo a equação de Schrödinger através do potencial completo; <i>S</i> mede quanta onda volta a sair.</p>
  <div class="formula">T<sub>lj</sub> = 1 − |S<sub>lj</sub>|²</div>
</div>
<div class="step">
  <h3>Somar o alvo</h3>
  <p>O disco à direita mostra o tamanho que o núcleo parece ter para o neutrão: a <b>secção eficaz de reação</b>, em barns (10⁻²⁴ cm²). Cada anel acrescenta-lhe a sua área vezes <i>T<sub>l</sub></i>. O círculo tracejado é o tamanho geométrico.</p>
  <div class="ctl"><label for="omp-e4">Energia do neutrão (MeV)</label><input id="omp-e4" type="range" data-bind="E" min="0.2" max="40" step="0.1" value="8"><output data-show="E" data-fmt="1"></output></div>
  <div class="btns"><button class="btn ghost" data-act="sum">Somar de novo</button></div>
  <p>Muda a energia e a soma recomeça: a baixa energia, um ou dois anéis grandes formam quase todo o disco; a alta energia, muitos anéis finos acrescentam fatias e o disco aproxima-se do tamanho geométrico.</p>
  <div class="formula">σ<sub>R</sub> = (π/k²) Σ (2l+1) T<sub>l</sub></div>
  <p>Os <i>T<sub>l</sub></i> alimentam o resto do motor: decidem com que frequência se forma cada spin do núcleo excitado e, no sentido inverso, com que facilidade cada partícula volta a sair.</p>
  <div class="aside">No código: <code>omp/parameters.py</code> (potencial global de Koning–Delaroche; potenciais dispersivos para actinídeos), <code>omp/schrodinger.py</code> (integração de Numerov e ajuste coulombiano), <code>omp/inverse.py</code> (partículas emitidas por balanço detalhado), <code>omp/regional.py</code> (opcional, desligado por defeito: um ajuste regional do poço para alvos deformados de terras raras, ajustado a S₀ e S₁ medidos).</div>
</div>`,
};
Object.assign(WT.L.labels, {
  "absorbing surface": "superfície absorvente",
  "shadow: neutrons lost to reactions": "sombra: neutrões perdidos em reações",
  "wavelength {#} fm   ·   nucleus {#} fm across": "comprimento de onda {#} fm   ·   núcleo de {#} fm",
  "crests crowd inside the well": "as cristas apertam-se no poço",
  "l={#}": "l={#}",
  "nuclear radius": "raio nuclear",
  "reaction cross section ≈ {#} b": "secção eficaz de reação ≈ {#} b",
  "geometric size π(R+λ̄)² ≈ {#} b · darker ring = more absorbed · orange flash = absorbed": "tamanho geom. π(R+λ̄)² ≈ {#} b · mais escuro = mais absorção · laranja = absorvido",
  "absorbed, ring by ring": "absorvidos, anel a anel",
  "bar: your neutrons · tick: model Tₗ": "barra: os teus · marca: Tₗ",
  "rings: shade = Tₗ": "anéis: tom = Tₗ",
  "geometric size π(R+λ̄)²": "tamanho geométrico π(R+λ̄)²",
  "reaction cross section": "secção eficaz de reação",
  "ring l={#}: ({#}l+{#})·Tₗ·π/k² = +{#} b": "anel l={#}: ({#}l+{#})·Tₗ·π/k² = +{#} b",
  "all {#} rings added": "os {#} anéis somados",
  "σ_R = {#} b": "σ_R = {#} b",
  "geometric {#} b": "geométrico {#} b",
  "geometric {#} b · darker = more absorbed · orange = absorbed": "geométrico {#} b · mais escuro = mais absorção · laranja = absorvido",
  "swing distance b ≈ (l+½)/k = {#} fm": "distância de passagem b ≈ (l+½)/k = {#} fm",
  "nuclear radius R = {#} fm · wave fuzz λ̄ = {#} fm": "raio nuclear R = {#} fm · esbatimento λ̄ = {#} fm",
  "path crosses the nucleus: most get in": "a trajetória cruza o núcleo: quase todos entram",
  "path misses the nucleus: only the fuzzy edge can tunnel in": "a trajetória passa ao lado: só a orla difusa entra por túnel",
  "absorbed {#} of {#} · model Tₗ = {#}": "absorvidos {#} de {#} · Tₗ do modelo = {#}",
});
