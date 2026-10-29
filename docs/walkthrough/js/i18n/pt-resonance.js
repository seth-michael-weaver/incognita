/* Portuguese (pt-PT): resonance (chapter 10) */
WT.L.ch.resonance = {
  num: "Capítulo 15", title: "Ressonâncias", short: "Ressonâncias",
  lead: "A uma energia suficientemente baixa, um neutrão já não vê um núcleo liso e médio. Vê os níveis de energia individuais do núcleo composto, um a um.",
  html: `
<div class="step">
  <p>Cada pico é uma <b>ressonância</b>: um nível de energia do núcleo composto no qual pode cair um neutrão que tenha exatamente essa energia. A sua altura é a secção eficaz de <b>captura</b> nesse ponto (o neutrão é absorvido e saem fotões), em escala logarítmica; a sua largura é a largura da ressonância Γ, desenhada cerca de cem vezes mais larga do que é.</p>
  <div class="ctl"><label for="res-e">Energia do neutrão (eV)</label><input id="res-e" type="range" data-bind="En" min="0.5" max="300" step="0.1" value="30"><output data-show="En" data-fmt="1"></output></div>
  <p>O neutrão avança aos saltos em energia; onde aterra pode ser capturado, com um clarão de fotões. Sobre um pico a secção eficaz é de milhares de barns e a captura é quase certa; entre picos é de poucos barns. Arrasta a energia para o pousar num pico e depois entre dois.</p>
</div>
<div class="step">
  <h3>Repulsão de níveis</h3>
  <p>A fila do meio mostra como se dispõem os níveis reais: dois níveis com o mesmo spin e a mesma paridade repelem-se, por isso as quase coincidências são raras. A <b>teoria de matrizes aleatórias</b> descreve este padrão. Posições verdadeiramente aleatórias (fila de cima) agrupam-se e deixam lacunas.</p>
  <div class="btns"><button class="btn" data-act="again">Sortear de novo</button></div>
  <p>Sorteia de novo para obter outra amostra. ⟨r̃⟩ compara cada espaçamento com o seguinte: cerca de 0,39 para posições aleatórias, 0,53 para níveis que se repelem; o código usa o padrão com repulsão. Misturar duas sequências, por exemplo dois spins (fila de baixo), esconde em parte a repulsão.</p>
</div>
<div class="step">
  <h3>Flutuações de largura de Porter–Thomas</h3>
  <p>Agora a altura de cada pico é a sua <b>largura neutrónica</b> Γ<sub>n</sub> em escala linear: a força com que o nível se acopla a um neutrão. A tampa amarela é a sua largura γ Γ<sub>γ</sub>, a rapidez com que emite fotões; soma centenas de caminhos de fotões, por isso é quase igual para todos os níveis.</p>
  <div class="btns"><button class="btn" data-act="roll">Sortear uma largura</button><button class="btn ghost" data-act="equal">Larguras iguais</button><button class="btn ghost" data-act="pt">Porter–Thomas</button></div>
  <p>Um nível só tem uma maneira de se partir em neutrão mais alvo, por isso a sua largura comporta-se como o quadrado de um único número de distribuição normal. Sorteia um: a bola cai em <i>x</i>, <i>x</i>² passa a ser a altura do pico seguinte, e um ponto cai no monte. O monte acumula-se perto de zero com uma cauda longa, a lei de <b>Porter–Thomas</b>: a maioria dos níveis é fraca, alguns são enormes. Larguras iguais mostra, em vez disso, uma fila de picos médios.</p>
</div>
<div class="step">
  <h3>Escadas estatísticas de ressonâncias</h3>
  <p>Os picos saem agora de quatro médias que podes ajustar. Para um núcleo não medido só se podem prever estas médias: o espaçamento médio <i>D</i><sub>0</sub>; as <b>funções de intensidade</b> <i>S</i><sub>0</sub> e <i>S</i><sub>1</sub>, a largura neutrónica média por unidade de espaçamento para neutrões de onda s (de frente) e de onda p (descentrados); e a largura γ média. Com elas o código constrói uma <b>escada</b>: um conjunto aleatório de níveis com essas médias. Três têm cursores aqui; <i>S</i><sub>1</sub> fica fixo (o seu valor está escrito por baixo dos picos).</p>
  <div class="ctl"><label for="res-d0">Espaçamento D₀ (eV)</label><input id="res-d0" type="range" data-bind="D0" min="3" max="60" step="0.5" value="20"><output data-show="D0" data-fmt="1"></output></div>
  <div class="ctl"><label for="res-s0">Intensidade S₀ (×10⁻⁴)</label><input id="res-s0" type="range" data-bind="S0" min="0.2" max="3" step="0.05" value="1"><output data-show="S0" data-fmt="2"></output></div>
  <div class="ctl"><label for="res-gg">Largura γ ⟨Γγ⟩ (meV)</label><input id="res-gg" type="range" data-bind="Gg" min="10" max="80" step="1" value="23"><output data-show="Gg" data-fmt="0"></output></div>
  <p>Arrasta <i>D</i><sub>0</sub> e os picos afastam-se ou apinham-se. Os picos cheios são níveis de onda s (paridade positiva); os contornados, de onda p (paridade negativa). As larguras neutrónicas crescem como √<i>E</i> para as ondas s e como <i>E</i><sup>3/2</sup> para as ondas p, por isso os picos contornados começam baixos e crescem para a direita.</p>
</div>
<div class="step">
  <h3>A região térmica</h3>
  <p>Os mesmos picos numa escala de energia logarítmica, até milésimas de eV. Os neutrões de um reator abrandam ao ressaltar em núcleos leves, perdendo mais ou menos a mesma fração da sua energia de cada vez, por isso aqui todos os saltos têm o mesmo comprimento. Alguns ficam presos nos picos pelo caminho.</p>
  <div class="btns"><button class="btn" data-act="slow">Abrandar 10 neutrões</button></div>
  <p>Os que passam assentam à temperatura ambiente, 0,025 eV, a energia <b>térmica</b>, muito abaixo do primeiro pico. Aí a secção eficaz, a área do disco, é a soma das caudas das ressonâncias, incluindo níveis ligados logo abaixo de zero; as caudas crescem como 1/<i>v</i> (<i>v</i>, a velocidade do neutrão), por isso o fundo sobe para a esquerda. O que fica preso durante a descida mede-se com o <b>integral de ressonância</b>: a secção eficaz acima de 0,5 eV, com cada energia ponderada por 1/<i>E</i>.</p>
</div>
<div class="step">
  <h3>O que a estatística consegue prever</h3>
  <p>Cada fila é uma escada tirada dos mesmos quatro números, com um disco cuja área é a sua secção eficaz de captura térmica. O parêntese chega até ao pico que fixa esse valor, normalmente o mais próximo; a sua distância muda de escada para escada, e o disco varia por um fator de dez ou mais.</p>
  <div class="btns"><button class="btn" data-act="draw1">Sortear uma escada</button><button class="btn ghost" data-act="more">Sortear 20</button></div>
  <p>Cada valor cai no monte da direita. Para um núcleo não medido a resposta é uma dispersão de valores, não um único número, e nenhum modelo melhor a pode estreitar. O integral de ressonância, uma soma sobre muitos picos, dispersa-se menos. Onde os níveis estão afastados mais de cerca de 10 keV, como nos núcleos leves, nenhum fica perto da zona térmica: aí a captura é direta, e o código recusa-se a responder.</p>
  <div class="aside">No código: <code>physics/resonance/ladder.py</code> (espaçamentos de matrizes aleatórias, larguras de Porter–Thomas, secções eficazes de Breit–Wigner, captura térmica e integral de ressonância sobre um conjunto de escadas), <code>ladder_statistics.py</code> (as mesmas leis postas à prova com escadas medidas), <code>ensemble_runner.py</code>. Correm ao lado do motor de reações, não dentro dele.</div>
</div>`,
};
Object.assign(WT.L.labels, {
  // forest
  "{#} eV": "{#} eV", "+{#} eV": "+{#} eV",
  "height: peak capture (log) · width Γ ×{#}": "altura: captura máx. (log) · largura Γ ×{#}",
  "peak height: capture cross section (log scale) · width: resonance width Γ, drawn {#}× wide": "altura: secção eficaz de captura máxima (escala log) · largura Γ, desenhada {#}× mais larga",
  "D₀ {#} eV · S₀ {#}×{#}⁻⁴ · S₁ {#}×{#}⁻⁴ · ⟨Γγ⟩ {#} meV": "D₀ {#} eV · S₀ {#}×{#}⁻⁴ · S₁ {#}×{#}⁻⁴ · ⟨Γγ⟩ {#} meV",
  "s-wave (+ parity)": "onda s (paridade +)", "p-wave (− parity)": "onda p (paridade −)",
  "caught {#} times in {#} landings": "capturado {#} vezes em {#} aterragens",
  "each peak: one level of the compound nucleus": "cada pico: um nível do núcleo composto",
  "each peak: one level of the compound nucleus · about {#} eV apart": "cada pico: um nível do núcleo composto · afastados cerca de {#} eV",
  // spacing
  "random positions (Poisson)": "posições aleatórias (Poisson)",
  "repelling levels (random-matrix)": "níveis que se repelem (matrizes aleatórias)",
  "two repelling sequences mixed": "duas sequências que se repelem, misturadas",
  "clumps and gaps · ⟨r̃⟩ ≈ {#}": "grupos e lacunas · ⟨r̃⟩ ≈ {#}",
  "evenly kept apart · ⟨r̃⟩ ≈ {#}": "afastados com regularidade · ⟨r̃⟩ ≈ {#}",
  "repulsion half hidden · ⟨r̃⟩ ≈ {#}": "repulsão meio escondida · ⟨r̃⟩ ≈ {#}",
  "clumps and gaps · spacing ratio ⟨r̃⟩ ≈ {#}": "grupos e lacunas · razão de espaçamentos ⟨r̃⟩ ≈ {#}",
  "evenly kept apart · spacing ratio ⟨r̃⟩ ≈ {#}": "afastados com regularidade · razão de espaçamentos ⟨r̃⟩ ≈ {#}",
  "repulsion half hidden · spacing ratio ⟨r̃⟩ ≈ {#}": "repulsão meio escondida · razão de espaçamentos ⟨r̃⟩ ≈ {#}",
  "⟨r̃⟩: {#} if random, {#} for random-matrix": "⟨r̃⟩: {#} se aleatório, {#} com matrizes aleatórias",
  "same average spacing in every row · ⟨r̃⟩: {#} if random, {#} for random-matrix": "mesmo espaçamento médio em cada fila · ⟨r̃⟩: {#} se aleatório, {#} com matrizes aleatórias",
  // Porter-Thomas
  "height: neutron width Γn (linear)": "altura: largura neutrónica Γn (linear)",
  "peak height: neutron width Γn, linear scale": "altura: largura neutrónica Γn, escala linear",
  "yellow: γ width": "amarelo: largura γ",
  "yellow cap: γ width, nearly the same on every peak": "tampa amarela: largura γ, quase igual em todos",
  "equal widths: every peak the average": "larguras iguais: todos os picos na média",
  "rolled widths": "larguras sorteadas", "pile of rolled widths": "monte de larguras sorteadas",
  "× average": "× média", "(in units of the average)": "(em unidades da média)",
  "dashed: Porter–Thomas": "tracejado: Porter–Thomas", "dashed: the Porter–Thomas law": "tracejado: a lei de Porter–Thomas",
  "bell-curve number x": "número de distribuição normal x",
  "x = {#}  →  x² = {#}": "x = {#}  →  x² = {#}",
  "press Roll a width": "carrega em Sortear uma largura",
  // thermal
  "bound level {#} eV": "nível ligado {#} eV",
  "a bound level at {#} eV: its tail lifts this end": "um nível ligado a {#} eV: a sua cauda levanta este extremo",
  "resonance integral ≈ {#} b": "integral de ressonância ≈ {#} b",
  "resonance integral above {#} eV ≈ {#} b": "integral de ressonância acima de {#} eV ≈ {#} b",
  "{#}/v": "{#}/v",
  "caught by a peak on the way down: {#} · reached thermal: {#}": "presos num pico na descida: {#} · chegam a térmico: {#}",
  "each hop: one bounce, the same fraction of energy lost": "cada salto: um ressalto, perde-se a mesma fração de energia",
  // ensemble
  "thermal neutron": "neutrão térmico",
  "σ disc": "disco σ", "disc area = σ at {#} eV": "disco: área = σ a {#} eV",
  "{#}k": "{#}k",
  "thermal σ (b)": "σ térmica (b)", "thermal σ, barns": "σ térmica, barns",
  "{#} ladders · thermal ×{#} · res. integral ×{#}": "{#} escadas · térmica ×{#} · int. de ress. ×{#}",
});
// labels that carry a cross section printed as "12 b" or "3.4k b"
(function () {
  const L = WT.L.labels;
  for (const b of ["{#} b", "{#}k b"]) {
    L[b] = b;
    L[`σ ≈ ${b} · caught on {#} % of landings`] = `σ ≈ ${b} · capturado em {#} % das aterragens`;
    L[`σ ≈ ${b} · caught on <{#} % of landings`] = `σ ≈ ${b} · capturado em <{#} % das aterragens`;
    L[`thermal, {#} eV: σ ≈ ${b}`] = `térmico, {#} eV: σ ≈ ${b}`;
    L[`{#} ladders · thermal σ median ${b}, middle two thirds ×{#} · resonance integral only ×{#}`] =
      `{#} escadas · σ térmica mediana ${b}, dois terços centrais ×{#} · integral de ressonância só ×{#}`;
  }
})();
