/* Portuguese (pt-PT): exciton (Capítulo 26, Especialista) */
WT.L.ch.exciton = {
  num: "Capítulo 26", title: "O modelo de excitões, em números", short: "Modelo de excitões",
  lead: "O Capítulo 7 seguiu um neutrão rápido ao longo de umas poucas colisões. Eis as taxas que decidem, em cada etapa, se o que vem a seguir é outra colisão ou uma fuga, e o espectro que elas formam no total.",
  html: `
<div class="step">
  <h3>Contar estados partícula–buraco</h3>
  <p>O modelo de excitões classifica o núcleo, a caminho do equilíbrio, pelo seu número de partículas excitadas <i>p</i> e de buracos <i>h</i>, <i>n</i> = <i>p</i> + <i>h</i>. Um neutrão que entra num alvo começa em <i>p</i> = 1, <i>h</i> = 0; cada colisão acrescenta um par. O que conta em cada etapa é de quantas maneiras a energia se pode repartir pelos <i>n</i> excitões: a densidade de estados partícula–buraco.</p>
  <div class="formula">ω(p,h,E) = g<sup>n</sup> (E − A<sub>p,h</sub>)<sup>n−1</sup> / (p! h! (n−1)!) ,  A<sub>p,h</sub> = max(p,h)²/g − (p² + h² + p + h)/4g</div>
  <div class="ctl"><label for="ex-n">Partículas p (buracos p − 1)</label><input id="ex-n" type="range" data-bind="pp" min="2" max="6" step="1" value="3" data-instant><output data-show="pp" data-fmt="0"></output></div>
  <div class="btns"><button class="btn ghost" data-act="pauli" aria-pressed="true">Correção de Pauli</button></div>
  <p><i>g</i> ≈ <i>A</i>/15 MeV⁻¹ é a densidade de níveis de partícula única perto da energia de Fermi. <i>A<sub>p,h</sub></i> é a correção de <b>Pauli</b>: duas partículas não podem partilhar um nível, por isso as configurações mais baixas custam energia e a densidade perto do limiar cai. As curvas são designadas pelas suas contagens: 3p2h significa 3 partículas e 2 buracos. O esboço mostra uma configuração de cada vez com o <i>p</i> escolhido, sorteada ao acaso: cada buraco é um nucleão em falta abaixo do nível de Fermi.</p>
</div>
<div class="step">
  <h3>Taxas de transição e de emissão</h3>
  <p>A partir de cada etapa podem acontecer duas coisas. Uma colisão cria outro par, à taxa λ<sup>+</sup>, que pela regra de ouro de Fermi é o quadrado do elemento de matriz vezes a densidade de estados que consegue alcançar. Ou uma partícula sai, à taxa <i>W</i>, dada pelo balanço detalhado a partir da secção eficaz inversa e da razão entre as densidades de estados com e sem a partícula que escapa.</p>
  <div class="formula">λ<sup>+</sup>(n) = (2π/ħ) M² ω<sub>acc</sub> ,  W(p,h,ε) = (2s+1)/(π²ħ³) με σ<sub>inv</sub>(ε) ω(p−1,h,U) / ω(p,h,E)</div>
  <div class="ctl"><label for="ex-e">Energia do neutrão (MeV)</label><input id="ex-e" type="range" data-bind="Ein" min="5" max="60" step="0.5" value="20"><output data-show="Ein" data-fmt="1"></output></div>
  <p>Cada etapa é identificada pelas suas contagens (2p1h: 2 partículas, 1 buraco). As barras são as duas taxas em cada etapa, em escala logarítmica: λ<sup>+</sup> da ordem de 10²² s⁻¹, <i>W</i> cerca de um décimo disso na primeira etapa e a descer a cada etapa, já que cada novo par dilui a energia que a partícula da frente pode levar. O motor tira M² da forma de Koning–Duijvestijn, que decresce com a energia por excitão:</p>
  <div class="formula">M² = (C₁ A<sub>p</sub> / A³) · [7.48 + 4.62×10⁵ / (E/(n A<sub>p</sub>) + 10.7)³]  MeV²</div>
</div>
<div class="step">
  <h3>A cadeia no tempo</h3>
  <p>Ignorando as raras colisões que removem um par (a aproximação never-come-back, «sem regresso»), as populações obedecem a uma cadeia simples: cada etapa enche-se a partir da anterior e esvazia-se para a seguinte e para o contínuo. As barras resolvem essa equação mestra; o tempo está em unidades de 10⁻²² s.</p>
  <div class="formula">dP(n)/dt = λ<sup>+</sup>(n−2) P(n−2) − [λ<sup>+</sup>(n) + W(n)] P(n)</div>
  <div class="ctl"><label for="ex-e2">Energia do neutrão (MeV)</label><input id="ex-e2" type="range" data-bind="Ein" min="5" max="60" step="0.5" value="20"><output data-show="Ein" data-fmt="1"></output></div>
  <p>A cadeia inteira termina em poucos 10⁻²² s. A fração que escapa pelo caminho é a emissão de pré-equilíbrio; o resto, depois de no máximo seis partículas no motor, como no TALYS, é entregue ao núcleo composto. A integração no tempo dá a cada etapa um peso τ(<i>n</i>)·<i>P</i>(<i>n</i>), e é esse produto que o motor calcula.</p>
</div>
<div class="step">
  <h3>A cauda de alta energia</h3>
  <p>O espectro de emissão é a soma, sobre as etapas, da população vezes o tempo de vida vezes a taxa de emissão, mais a evaporação do que resta. Só a etapa <i>n</i> = 3, duas partículas e um buraco, chega às energias de saída mais altas: o seu espectro só decresce linearmente até ao ponto final. Cada etapa posterior é mais suave.</p>
  <div class="formula">dσ/dε = σ<sub>CN</sub> Σ<sub>n</sub> P(n) τ(n) W(n,ε) + evaporação</div>
  <div class="ctl"><label for="ex-e3">Energia do neutrão (MeV)</label><input id="ex-e3" type="range" data-bind="Ein" min="5" max="60" step="0.5" value="20"><output data-show="Ein" data-fmt="1"></output></div>
  <p>Sobe a energia e o espectro endurece: a cauda de pré-equilíbrio estende-se até ao ponto final, enquanto a bossa de evaporação fica em 1 a 2 MeV. Acima de cerca de 10 MeV, os neutrões de alta energia medidos só se conseguem reproduzir com esta cauda.</p>
</div>
<div class="step">
  <h3>A fração de pré-equilíbrio</h3>
  <p>A fração da emissão que é de pré-equilíbrio cresce com a energia incidente, de uns poucos por cento perto de 5 MeV até cerca de 40 por cento a 40 MeV, aqui. Depende de uma constante ajustável, o tamanho global do elemento de matriz: uma interação mais fraca significa um equilíbrio mais lento e mais emissão precoce.</p>
  <div class="ctl"><label for="ex-c">Constante do elemento de matriz C₁</label><input id="ex-c" type="range" data-bind="c1" min="0.3" max="3" step="0.05" value="1"><output data-show="c1" data-fmt="2"></output></div>
  <p>A curva tracejada é C₁ = 1, a opção por defeito do motor; a cheia segue o cursor. Reduzir C₁ a metade aumenta a fração por um fator de 1,5 a 1,9, não de 2: a probabilidade de fuga de cada etapa é W/(λ<sup>+</sup> + W), não W/λ<sup>+</sup>, e menos núcleos sobrevivem até às etapas posteriores.</p>
</div>
<div class="step">
  <h3>Duas componentes, e uma segunda fuga</h3>
  <p>O motor segue protões e neutrões em separado (<i>p</i><sub>π</sub>, <i>h</i><sub>π</sub>, <i>p</i><sub>ν</sub>, <i>h</i><sub>ν</sub>), com elementos de matriz diferentes para pares iguais e diferentes, uma profundidade de poço reduzida para a primeira colisão perto da superfície e as regras de Kalbach para aglomerados. Acima de 20 MeV deixa também o núcleo residual, que ainda guarda excitões, emitir uma segunda partícula rápida antes de chegar ao equilíbrio.</p>
  <div class="ctl"><label for="ex-e4">Energia do neutrão (MeV)</label><input id="ex-e4" type="range" data-bind="Ein" min="5" max="60" step="0.5" value="20"><output data-show="Ein" data-fmt="1"></output></div>
  <p>A curva é uma versão de brincar disso: depois de uma primeira emissão a partir da etapa de três excitões, a probabilidade de a partícula que sobra no residual escapar antes da sua colisão seguinte. Mantém-se pequena abaixo de 20 MeV e cresce acima, que é onde o motor liga o pré-equilíbrio múltiplo.</p>
  <div class="aside">No código: <code>density/particle_hole.py</code> (densidades de Williams, correções de Pauli e de poço finito, uma e duas componentes), <code>preeq/exciton.py</code> (elementos de matriz, taxas de emissão e de transição, tempos de vida, a solução never-come-back), <code>preeq/complex.py</code> (recolha, stripping e arrancamento de Kalbach), <code>preeq/multi.py</code> (pré-equilíbrio múltiplo, por defeito a partir de 20 MeV). A imagem é de uma só componente, com uma secção eficaz inversa esquemática, para um alvo semelhante ao ferro-56.</div>
</div>`,
};
(function () {
  const L = {
    "E (MeV)": "E (MeV)",
    "ω(p, h, E) per MeV": "ω(p, h, E) por MeV",
    "{#}p{#}h": "{#}p{#}h",
    "dashed: no Pauli correction": "tracejado: sem correção de Pauli",
    "Fermi level": "nível de Fermi",
    "{#} particles, {#} holes": "{#} partículas, {#} buracos",
    "rate (s⁻¹)": "taxa (s⁻¹)",
    "n = {#}": "n = {#}",
    "W/λ⁺ = {#}": "W/λ⁺ = {#}",
    "blue: λ⁺, the next collision · yellow: W, neutron escape": "azul: λ⁺, a colisão seguinte · amarelo: W, fuga do neutrão",
    "E = {#} + Sₙ = {#} MeV · τ(n={#}) = {#} × {#}⁻²² s": "E = {#} + Sₙ = {#} MeV · τ(n={#}) = {#} × {#}⁻²² s",
    "compound": "composto",
    "{#} %": "{#} %",
    "emitted before equilibrium: {#} % (of {#} % in the end)": "emitido antes do equilíbrio: {#} % (de {#} % no final)",
    "t = {#} × {#}⁻²² s": "t = {#} × {#}⁻²² s",
    "outgoing neutron energy ε (MeV)": "energia do neutrão emitido ε (MeV)",
    "dσ/dε (mb/MeV)": "dσ/dε (mb/MeV)",
    "evaporation": "evaporação",
    "ε = {#} MeV: {#} % from n = {#}": "ε = {#} MeV: {#} % vindos de n = {#}",
    "pre-equilibrium {#} % of the emission · solid: total": "pré-equilíbrio: {#} % da emissão · cheia: total",
    "{#} MeV": "{#} MeV",
    "pre-equilibrium share of the emission": "fração de pré-equilíbrio na emissão",
    "{#} MeV: {#} %": "{#} MeV: {#} %",
    "C₁ = {#} (dashed: {#})": "C₁ = {#} (tracejado: {#})",
    "{#} MeV: multiple pre-equilibrium on": "{#} MeV: pré-equilíbrio múltiplo ligado",
    "chance of a second fast emission (toy estimate)": "probabilidade de uma segunda emissão rápida (estimativa simplificada)",
    "residual: {#}p{#}h": "residual: {#}p{#}h",
  };
  Object.assign(WT.L.labels, L);
})();
Object.assign(WT.L.glossary, {
  neverComeBack: {
    term: "Aproximação never-come-back", aliases: ["aproximação never-come-back", "never-come-back"],
    short: "A aproximação segundo a qual, no início do caminho para o equilíbrio, as colisões apenas acrescentam pares partícula–buraco e nunca os removem.",
    more: "Transforma a equação mestra numa cadeia simples, que se pode integrar etapa a etapa. É válida enquanto o número de excitões estiver muito abaixo do seu valor de equilíbrio, que é onde ocorre a emissão de pré-equilíbrio.",
    chapter: "exciton",
  },
});
/* i18n_check.sh counts these attribute strings found in the English script code (not in html): data-act="pauli" */
