/* Portuguese (pt-PT): structure (Capítulo 1, de que é feito um núcleo) */
WT.L.ch.structure = {
  num: "Capítulo 1", title: "De que é feito um núcleo", short: "Estrutura",
  lead: "Antes de o motor (o nosso software de reações) disparar um único neutrão, precisa de uma descrição do núcleo alvo: com que força se mantém unido, em que estados de energia pode estar e que forma tem.",
  html: `
<div class="step">
  <p>A imagem mostra um núcleo de ferro: uma bola compacta de <em class="p">protões</em> e <em class="n">neutrões</em> (<b>nucleões</b>), unidos pela <b>força forte</b>, de alcance muito curto. Cada nucleão só sente os vizinhos mais próximos, por isso todos os núcleos têm mais ou menos a mesma densidade.</p>
  <div class="ctl"><label for="st-n">Neutrões (o ferro tem 26 protões)</label><input id="st-n" type="range" data-bind="N" min="24" max="38" step="1" value="30" data-instant><output data-show="N" data-fmt="0"></output></div>
  <p>Arrasta para acrescentar ou retirar neutrões; cada escolha é um <b>isótopo</b> diferente. As barras mostram a <b>energia de ligação</b> por nucleão em MeV (milhões de eletrão-volts): a energia necessária para desfazer o núcleo. É máxima perto dos isótopos estáveis.</p>
</div>
<div class="step">
  <h3>Energias de separação</h3>
  <p>A energia para tirar uma partícula é a sua <b>energia de separação</b>: <i>S<sub>n</sub></i> para um neutrão, <i>S<sub>p</sub></i> para um protão, <i>S<sub>α</sub></i> para uma <b>partícula alfa</b> (dois protões e dois neutrões ligados entre si). A imagem mostra o núcleo como um poço, com a energia a crescer para cima; cada extração leva a partícula do topo para lá da linha tracejada «livre», e o medidor regista o custo.</p>
  <div class="btns"><button class="btn ghost" data-act="pn">Tirar um neutrão</button><button class="btn ghost" data-act="pp">Tirar um protão</button><button class="btn ghost" data-act="pa">Tirar uma alfa</button></div>
  <p>O motor obtém cada uma como a diferença entre duas massas nucleares: medidas onde é possível, de um modelo de massas onde não é.</p>
  <div class="ctl"><label for="st-n2">Neutrões</label><input id="st-n2" type="range" data-bind="N" min="24" max="38" step="1" value="30" data-instant><output data-show="N" data-fmt="0"></output></div>
  <p>Arrasta o número de neutrões e volta a tirar um neutrão: <i>S<sub>n</sub></i> sobe e desce em ziguezague, porque os nucleões formam pares e, com um número par, o último fica mais ligado. Uma reação só pode expulsar uma partícula se trouxer energia suficiente para pagar esse custo. Estes custos são os <b>limiares</b> de todo o cálculo.</p>
</div>
<div class="step">
  <h3>Estados excitados e decaimento gama</h3>
  <p>Um núcleo só pode guardar certas quantidades exatas de energia extra: as linhas, aqui para o ferro-56, com o <b>estado fundamental</b> em baixo. Cada nível tem um <b>spin</b> <i>J</i> (momento angular) e uma <b>paridade</b>, + ou − (se a sua onda fica igual vista num espelho); 2<sup>+</sup> significa spin 2, paridade +.</p>
  <p>A bola laranja é um núcleo num nível alto. Desce nível a nível, e cada salto emite um <em class="g">fotão</em> (um raio gama) que leva a diferença de energia. A espessura e a percentagem dos caminhos são as probabilidades medidas de cada salto, as <b>razões de ramificação</b>.</p>
  <div class="btns"><button class="btn" data-act="drop">Excitar o núcleo</button></div>
  <p>Carrega várias vezes: o mesmo nível chega ao estado fundamental por caminhos diferentes. O motor guarda cerca de trinta níveis medidos por núcleo, com as suas probabilidades; mais acima, trata os níveis apinhados como um <b>contínuo</b> suave. Acima da linha tracejada, <i>S<sub>n</sub></i>, o núcleo pode emitir um neutrão.</p>
</div>
<div class="step">
  <h3>Isómeros: estados excitados de longa vida</h3>
  <p>Um nível cuja única saída exige uma grande mudança de spin, Δ<i>J</i>, decai muito devagar. À direita, 64 núcleos estão num nível assim; cada um espera um tempo aleatório, depois desce e sai um <em class="g">fotão</em>. Passada uma <b>semivida</b>, metade já desceu.</p>
  <div class="ctl"><label for="st-dj">Mudança de spin ΔJ</label><input id="st-dj" type="range" data-bind="dJ" min="1" max="5" step="1" value="2" data-instant><output data-show="dJ" data-fmt="0"></output></div>
  <div class="ctl"><label for="st-eg">Energia do fotão (MeV)</label><input id="st-eg" type="range" data-bind="Eg" min="0.05" max="1.5" step="0.05" value="0.3"><output data-show="Eg" data-fmt="2"></output></div>
  <div class="btns"><button class="btn ghost" data-act="excite">Excitá-los a todos</button></div>
  <p>Aumenta Δ<i>J</i> e os fotões saem mais devagar: cada unidade extra de spin torna a espera cem mil vezes mais longa ou mais, e uma energia de fotão menor também a alonga (em escala logarítmica). Um nível que vive mais de cerca de um segundo é um <b>isómero</b>, e o motor trata-o como um ponto final, tal como o estado fundamental.</p>
</div>
<div class="step">
  <h3>Deformação nuclear</h3>
  <p>Muitos núcleos não são redondos. <i>β₂</i> («beta dois») mede o alongamento: 0 é uma esfera, positivo é esticado como uma bola de râguebi, negativo é achatado como um disco. A escada à direita mostra os níveis que cada tipo produz.</p>
  <p>Um núcleo esticado pode rodar, e dá os níveis 0<sup>+</sup>, 2<sup>+</sup>, 4<sup>+</sup>, 6<sup>+</sup> com espaçamentos que crescem como <i>J</i>(<i>J</i>+1): um <b>rotor</b>. Um redondo pode ondular; cada unidade de ondulação, um <b>fonão</b>, acrescenta a mesma energia, por isso os seus níveis são igualmente espaçados: um <b>vibrador</b>.</p>
  <div class="ctl"><label for="st-beta">Deformação β₂</label><input id="st-beta" type="range" data-bind="beta" min="-0.3" max="0.45" step="0.01" value="0.28"><output data-show="beta" data-fmt="2"></output></div>
  <div class="btns"><button class="btn ghost" data-act="still">Parado</button><button class="btn ghost" data-act="vib">A vibrar</button><button class="btn ghost" data-act="rot">A rodar</button></div>
  <p>Arrasta <i>β₂</i> e carrega nos botões: um alongamento maior aproxima os níveis do rotor. Um vibrador é redondo em média, por isso o cursor fica quieto enquanto ele ondula; e uma esfera não pode rodar neste sentido (rodá-la não muda nada), pelo que perto de <i>β₂</i> = 0 a banda do rotor desaparece. O motor guarda deformações por núcleo e uma etiqueta: esférico, vibrador ou rotor. O capítulo 6 mostra como um neutrão que passa as usa.</p>
</div>
<div class="step">
  <h3>Parâmetros de ressonância acima do limiar neutrónico</h3>
  <p>Um neutrão lento que se junta ao alvo fica logo acima de <i>S<sub>n</sub></i>, na caixinha à esquerda. O painel da direita amplia essa caixa milhares de vezes, com a energia do neutrão da esquerda para a direita.</p>
  <div class="ctl"><label for="st-fe">Energia do feixe</label><input id="st-fe" type="range" data-bind="fe" min="0" max="1" step="0.001" value="0.3" data-instant><output id="st-fe-out"></output></div>
  <div class="btns"><button class="btn ghost" data-act="fplay" id="st-fplay">Pausar o varrimento</button></div>
  <p>Na maioria das energias o feixe passa sem mais. Em certas energias exatas, o neutrão mais o núcleo coincidem com um nível escondido e boa parte do feixe é capturada: uma <b>ressonância</b>. Num pico, o núcleo desenhado incha: não muda de tamanho real, é o alvo maior que o neutrão «vê» efetivamente quando a sua onda se sobrepõe à do núcleo. Depois o núcleo devolve a energia como um <em class="g">fotão</em> ou um neutrão. A curva mostra a fração capturada; as barras marcam cada ressonância encontrada.</p>
  <div class="btns"><button class="btn ghost" data-act="fFe">Ferro-56</button><button class="btn ghost" data-act="fAu">Ouro-197</button><button class="btn ghost" data-act="fU">Urânio-238</button></div>
  <p>Cada núcleo tem o seu próprio código de barras, à sua própria escala: milhares de eletrão-volts entre as ressonâncias do ferro, dezenas no ouro e no urânio. Três médias resumem-no: <i>D₀</i>, o espaçamento médio; ⟨Γ<sub>γ</sub>⟩, a <b>largura radiativa</b>, quase igual em todos os picos; e <i>S₀</i>, a <b>função de intensidade</b>, a facilidade com que entra um neutrão lento.</p>
  <p>Cada uma põe à prova um passo posterior. Os parâmetros de densidade de níveis do motor foram ajustados a <i>D₀</i>, núcleo a núcleo; ⟨Γ<sub>γ</sub>⟩ testa a emissão de fotões, e <i>S₀</i> o modelo ótico do capítulo seguinte. Para os núcleos não medidos, o motor usa tendências ajustadas sobre muitos núcleos.</p>
  <div class="aside">No código: <code>structure/masses.py</code> (massas medidas, massas de modelo para lá delas, energias de separação), <code>structure/levels.py</code> (níveis discretos, ramificações, isómeros, spins estimados) e <code>levjpar.py</code> (opcional, desligado por defeito: volta a estimar um spin da lista que é impossível para esse núcleo), <code>structure/deformation.py</code> (β₂ e a etiqueta esférico/vibrador/rotor) e <code>collrule.py</code> (opcional, desligado por defeito: escolhe a etiqueta do alvo a partir dos seus níveis medidos), <code>structure/resonances.py</code> (D₀, S₀, S₁, ⟨Γγ⟩).</div>
</div>`,
};
(function () {
  const L = {
    // scene: packed drop
    "{#}Fe": "{#}Fe",
    "{#} protons · {#} neutrons": "{#} protões · {#} neutrões",
    "binding energy per nucleon: about {#} MeV": "energia de ligação por nucleão: cerca de {#} MeV",
    "binding per nucleon, one bar per isotope →": "ligação por nucleão, uma barra por isótopo →",
    // scene: well
    "free": "livre",
    "free: outside the nucleus": "livre: fora do núcleo",
    "neutrons": "neutrões",
    "protons": "protões",
    "an alpha forms from the top pairs": "os pares do topo formam uma alfa",
    "neutron {#}": "neutrão {#}",
    "proton {#}": "protão {#}",
    "alpha {#}": "alfa {#}",
    "n {#}": "n {#}",
    "p {#}": "p {#}",
    "energy paid": "energia paga",
    "energy to pull": "energia para tirar",
    "(MeV)": "(MeV)",
    "each one out (MeV)": "cada uma (MeV)",
    "higher mark =": "marca mais alta =",
    "harder to remove": "mais difícil de tirar",
    "pulling out a neutron: {#} MeV paid": "a tirar um neutrão: {#} MeV pagos",
    "pulling out a proton: {#} MeV paid": "a tirar um protão: {#} MeV pagos",
    "pulling out an alpha: {#} MeV paid": "a tirar uma alfa: {#} MeV pagos",
    // scene: levels and gamma drops
    "continuum: too many levels to list": "contínuo: demasiados níveis para listar",
    "neutron threshold Sₙ ≈ {#} MeV": "limiar de neutrões Sₙ ≈ {#} MeV",
    "ground state": "estado fundamental",
    "MeV": "MeV",
    "each line: an energy, a spin J and a parity (±)": "cada linha: uma energia, um spin J e uma paridade (±)",
    "path width and % = measured odds of each hop": "espessura do caminho e % = probabilidade medida de cada salto",
    // scene: isomer
    "ground": "fundamental",
    "J = {#}/{#}": "J = {#}/{#}",
    "ΔJ = {#}": "ΔJ = {#}",
    "still excited: {#} of {#}": "ainda excitados: {#} de {#}",
    "longer than a second: an isomer, a stop in its own right": "mais de um segundo: um isómero, uma paragem por direito próprio",
    "shown slowed down (log scale)": "mostrado em câmara lenta (escala log.)",
    "shown slowed down: the slower they pop, the longer the real wait (log scale)": "em câmara lenta: quanto mais devagar saem, mais longa é a espera real (escala log.)",
    // scene: shape
    "ripples at the surface: a vibrator": "ondula à superfície: um vibrador",
    "stretched and rotating: a rotor": "esticado e a rodar: um rotor",
    "round: a sphere": "redondo: uma esfera",
    "stretched (prolate): a football": "esticado (prolato): uma bola de râguebi",
    "squashed: an oblate disc": "achatado: um disco oblato",
    "{#} phonons": "{#} fonões",
    "no regular": "sem padrão",
    "level pattern": "de níveis regular",
    "spacing grows like J(J+{#})": "o espaçamento cresce como J(J+{#})",
    "equal steps, one phonon each": "degraus iguais, um fonão cada",
    "its lowest levels": "os seus níveis mais baixos",
    "β₂ = {#}": "β₂ = {#}",
    // scene: resonance fingerprint
    "continuum": "contínuo",
    "Sₙ ≈ {#} MeV": "Sₙ ≈ {#} MeV",
    "slow neutron": "neutrão lento",
    "a slow neutron lands here:": "um neutrão lento fica aqui:",
    "lands here": "fica aqui",
    "Sₙ + its kinetic energy": "Sₙ + a sua energia cinética",
    "×{#} million": "×{#} milhões",
    "×{#} thousand": "×{#} mil",
    "magnified": "ampliado",
    "swells on a peak: the size the neutron effectively “sees” (waves overlap), not a real size change": "incha num pico: o tamanho que o neutrão “vê” efetivamente (as ondas sobrepõem-se), não uma mudança de tamanho real",
    "share taken in": "fração capturada",
    "share of the beam taken in": "fração do feixe capturada",
    "{#} (Sₙ)": "{#} (Sₙ)",
    "{#} = exactly Sₙ": "{#} = exatamente Sₙ",
    "{#} keV": "{#} keV",
    "{#} eV": "{#} eV",
    "neutron energy →": "energia do neutrão →",
    "neutron's kinetic energy →": "energia cinética do neutrão →",
    "D₀ ≈ {#} keV: the average gap": "D₀ ≈ {#} keV: o espaçamento médio",
    "D₀ ≈ {#} eV: the average gap": "D₀ ≈ {#} eV: o espaçamento médio",
    "S₀: average peak strength": "S₀: intensidade média dos picos",
    "S₀: how strong the peaks are on average (how easily a neutron gets in)": "S₀: intensidade média dos picos (a facilidade com que entra um neutrão)",
    "⟨Γγ⟩ ≈ {#} eV: photon width": "⟨Γγ⟩ ≈ {#} eV: largura radiativa",
    "⟨Γγ⟩ ≈ {#} eV: photon width, about the same for every peak": "⟨Γγ⟩ ≈ {#} eV: largura radiativa, quase igual em todos os picos",
    "⟨Γγ⟩ ≈ {#} eV: a hairline here": "⟨Γγ⟩ ≈ {#} eV: aqui, um fio",
    "⟨Γγ⟩ ≈ {#} eV: a hairline here; neutrons widen these peaks": "⟨Γγ⟩ ≈ {#} eV: aqui, um fio; os neutrões alargam estes picos",
    "peaks drawn about {#}× wider than life so they show": "picos desenhados cerca de {#}× mais largos do que na realidade para se verem",
  };
  // beam readout and per-target labels
  for (const u of ["keV", "eV"]) L[`beam of neutrons at {#} ${u}`] = `feixe de neutrões a {#} ${u}`;
  const EL = { iron: "ferro", gold: "ouro", uranium: "urânio" };
  for (const en in EL) {
    L[`${en}{#} levels`] = `níveis do ${EL[en]}{#}`;
    L[`${en}{#}: took in {#} of the last {#}`] = `${EL[en]}{#}: capturou {#} dos últimos {#}`;
  }
  // isomer half-life in every unit fmtTime can produce
  const TU = { femtoseconds: "femtossegundos", picoseconds: "picossegundos", nanoseconds: "nanossegundos", microseconds: "microssegundos",
    milliseconds: "milissegundos", seconds: "segundos", minutes: "minutos", hours: "horas", days: "dias", years: "anos" };
  for (const en in TU) L[`half-life about {#} ${en}`] = `semivida de cerca de {#} ${TU[en]}`;
  L["half-life about {#}×{#}^{#} years"] = "semivida de cerca de {#}×{#}^{#} anos";
  Object.assign(WT.L.labels, L);
})();
