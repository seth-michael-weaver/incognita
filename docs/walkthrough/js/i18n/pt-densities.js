/* Portuguese (pt-PT): densities (Capítulo 24, Especialista) */
WT.L.ch.densities = {
  num: "Capítulo 24", title: "Densidades de níveis, unidas", short: "Densidades de níveis",
  lead: "O Capítulo 8 uniu uma prancha reta a uma encosta. Este capítulo escreve as duas, mostra como se encontra a junção a partir dos níveis contados e o que acontece quando não existe junção.",
  html: `
<div class="step">
  <h3>O gás de Fermi com efeitos de camadas amortecidos</h3>
  <p>A densidade de níveis por defeito do motor, ldmodel 1, é a composta de <b>Gilbert–Cameron</b>: um gás de Fermi a alta energia e uma temperatura constante abaixo. O gás de Fermi precisa de um número, o parâmetro de densidade de níveis <i>a</i>, e a baixa energia esse número sente as camadas. A forma de <b>Ignatyuk</b> deixa a correção de camadas δW atuar por inteiro a baixa excitação e desvanecer-se a um ritmo de amortecimento γ, de modo que <i>a</i>(<i>U</i>) tende para o valor suave <i>ã</i> quando o núcleo está quente.</p>
  <div class="formula">a(U) = ã [1 + δW (1 − e<sup>−γU</sup>) / U] ,  ã = αA + βA<sup>2/3</sup> ,  γ = γ₁ / A<sup>1/3</sup></div>
  <div class="ctl"><label for="ld-dw">Correção de camadas δW (MeV)</label><input id="ld-dw" type="range" data-bind="dW" min="-6" max="4" step="0.1" value="1"><output data-show="dW" data-fmt="1"></output></div>
  <div class="formula">ρ<sub>F</sub>(E) = exp(2√(aU)) / (12√2 σ a<sup>1/4</sup> U<sup>5/4</sup>) ,  U = E − Δ ,  σ² = 0.01389 A<sup>5/3</sup> √(aU) / ã</div>
  <p>As curvas de cima são <i>a</i>(<i>U</i>)/<i>ã</i> para vários δW; a tua está a negrito. Por baixo está ln ρ<sub>F</sub>. Um δW negativo (uma camada fechada) reduz a densidade em uma a duas ordens de grandeza, e a redução só se desvanece lentamente: <i>a</i>(<i>U</i>) regressa a <i>ã</i> como δW/<i>U</i>, de modo que mesmo a 20 MeV um δW de −6 MeV ainda custa um fator de cerca de 40. Δ é o desvio de emparelhamento, 12/√A por cada tipo de nucleão emparelhado.</p>
</div>
<div class="step">
  <h3>Uma reta tangente por baixo</h3>
  <p>Abaixo da energia de junção <i>E<sub>x</sub></i>, o gás de Fermi é substituído pela lei de <b>temperatura constante</b>. Duas condições fixam os seus dois parâmetros: o mesmo valor e o mesmo declive em <i>E<sub>x</sub></i>, pelo que a reta é aí a tangente a ln ρ<sub>F</sub>.</p>
  <div class="formula">ρ<sub>T</sub>(E) = (1/T) e<sup>(E − E₀)/T</sup> ,  1/T = d ln ρ<sub>F</sub>/dE |<sub>E<sub>x</sub></sub> ,  E₀ = E<sub>x</sub> − T ln[T ρ<sub>F</sub>(E<sub>x</sub>)]</div>
  <div class="ctl"><label for="ld-ex">Energia de junção Eₓ (MeV)</label><input id="ld-ex" type="range" data-bind="Ex" min="4.6" max="14" step="0.05" value="7"><output data-show="Ex" data-fmt="2"></output></div>
  <p>Desliza <i>E<sub>x</sub></i> e a tangente roda: uma junção mais alta dá um <i>T</i> mais alto (uma reta mais plana) e um <i>E</i>₀ mais baixo. Qualquer <i>E<sub>x</sub></i> dá uma curva suave. São os níveis contados que decidem qual é a correta.</p>
</div>
<div class="step">
  <h3>Encontrar a junção a partir dos níveis contados</h3>
  <p>A escada é o número de níveis conhecidos abaixo de <i>E</i>, em escala logarítmica. A lei de temperatura constante integra-se numa reta, <i>N</i>(<i>E</i>) = e<sup>(E − E₀)/T</sup> + const, que tem de reproduzir a contagem entre o nível <i>N<sub>L</sub></i> e o nível <i>N<sub>P</sub></i>, o troço do esquema que se julga completo. É uma equação para a única incógnita <i>E<sub>x</sub></i>.</p>
  <div class="formula">F(E<sub>x</sub>) = e<sup>(E<sub>P</sub>−E₀)/T</sup> − e<sup>(E<sub>L</sub>−E₀)/T</sup> − (N<sub>P</sub> − N<sub>L</sub>) = 0</div>
  <div class="ctl"><label for="ld-ex2">Eₓ de ensaio (MeV)</label><input id="ld-ex2" type="range" data-bind="Ex" min="4.6" max="14" step="0.05" value="7"><output data-show="Ex" data-fmt="2"></output></div>
  <p>O painel de baixo é <i>F</i>. O motor, como o TALYS, percorre um intervalo em 100 passos à procura de uma mudança de sinal e depois divide-o ao meio; o parêntese que encolhe mostra a bisseção. Onde <i>F</i> = 0, a reta de ensaio assenta na escada.</p>
</div>
<div class="step">
  <h3>Quando não há junção</h3>
  <p>Numa camada duplamente fechada, o gás de Fermi a baixa energia está tão reduzido que a sua temperatura se mantém baixa em toda a parte, e <i>F</i> nunca muda de sinal: não existe energia de junção. O TALYS toma então a temperatura empírica <i>T</i> = −0,25 + 10,2/√(<i>A</i>(1 + γδW)) e procura a energia em que o gás de Fermi tem essa temperatura. Perto de uma camada duplamente fechada, o gás de Fermi só atinge essa temperatura muito acima de qualquer junção razoável, ou nunca, pelo que também a junção recorre às sistemáticas, <i>E<sub>x</sub></i> = 2,33 + 253/<i>A</i> + Δ, e <i>E</i>₀ é fixado de modo que o valor seja contínuo.</p>
  <div class="btns"><button class="btn ghost" data-act="tang" aria-pressed="false">Tangente na energia de recurso</button></div>
  <p>O valor é contínuo, mas o <i>T</i> empírico não é a temperatura do gás de Fermi a essa energia, por isso o declive dá um salto. Com a entrada por defeito isto acontece para ²⁰⁵,²⁰⁶Tl, ²⁰⁶⁻²⁰⁹Pb e ²¹⁰Bi, com saltos de declive de 34 a 62 %; tirar aí <i>T</i> do gás de Fermi, como o TALYS já faz quando <i>E<sub>x</sub></i> é dado na entrada, repõe a tangente e altera a captura na região do chumbo até 20 a 30 %. O INCOGNITA reproduz aqui o TALYS; a alteração foi comunicada aos programadores do TALYS. A imagem é uma ilustração semelhante ao chumbo, com <i>ã</i> aumentado em 30 % para que o seu gás de Fermi fique abaixo da temperatura empírica até cerca de 24 MeV, para lá do intervalo de procura; o seu declive salta 62 %.</p>
</div>
<div class="step">
  <h3>O espaçamento D₀ como verificação</h3>
  <p>À energia de separação do neutrão, a densidade mede-se diretamente: o espaçamento médio <i>D</i>₀ das ressonâncias de onda s conta os estados do único spin e paridade a que um neutrão lento consegue chegar. Para um alvo de spin 0, é apenas <i>J</i><sup>π</sup> = ½⁺.</p>
  <div class="formula">1/D₀ = ρ(S<sub>n</sub>, ½, +) = ½ ρ<sub>F</sub>(S<sub>n</sub>) · (2J+1)/(2σ²) · e<sup>−(J+½)²/2σ²</sup></div>
  <div class="ctl"><label for="ld-as">Fator de escala em ã</label><input id="ld-as" type="range" data-bind="as" min="0.8" max="1.2" step="0.005" value="1"><output data-show="as" data-fmt="3"></output></div>
  <p>A imagem é para um núcleo composto semelhante ao ferro-57 com o <i>ã</i> global, face aos 25,4 ± 2,2 keV medidos. Uns poucos por cento em <i>ã</i> alteram <i>D</i>₀ em dezenas de por cento, por isso, onde <i>D</i>₀ está medido, a densidade em <i>S<sub>n</sub></i> fica bem fixada e, onde não está, é a maior incerteza isolada na captura. As avaliações ajustam <i>a</i> a <i>D</i>₀, e o mesmo faz a opção por defeito do TALYS, que o motor segue: para um núcleo com <i>D</i>₀ medido, lê um parâmetro de densidade de níveis ajustado a ele, e só usa a fórmula global para os restantes.</p>
  <div class="aside">No código: <code>density/parameters.py</code> (ã, amortecimento de Ignatyuk, emparelhamento, corte de spin), <code>density/models.py</code> (gás de Fermi, temperatura constante, tabelas), <code>density/matching.py</code> (a raiz da junção, o recurso empírico, os detalhes de precisão simples do próprio TALYS reproduzidos). A imagem usa os parâmetros globais do TALYS para ldmodel 1 com esquemas de níveis e correções de camadas ilustrativos (e, para o caso semelhante ao chumbo, <i>ã</i> × 1,3); o <i>D</i>₀ medido é o valor do RIPL para ⁵⁷Fe.</div>
</div>`,
};
(function () {
  const L = {
    "E (MeV)": "E (MeV)", "U (MeV)": "U (MeV)", "Eₓ (MeV)": "Eₓ (MeV)",
    "a(U) / ã": "a(U) / ã",
    "U = {#} MeV · a = {#} MeV⁻¹ · T ≈ √(U/a) = {#} MeV": "U = {#} MeV · a = {#} MeV⁻¹ · T ≈ √(U/a) = {#} MeV",
    "ρ_F (states per MeV), A = {#}": "ρ_F (estados por MeV), A = {#}",
    "dashed: δW = {#}": "tracejado: δW = {#}",
    "at {#} MeV: ×{#} against δW = {#}": "a {#} MeV: ×{#} face a δW = {#}",
    "at {#} MeV: ×{#}e{#} against δW = {#}": "a {#} MeV: ×{#}e{#} face a δW = {#}",
    "T = {#} MeV": "T = {#} MeV",
    "× e": "× e",
    "joint Eₓ = {#} MeV": "junção Eₓ = {#} MeV",
    "E₀ = {#} MeV": "E₀ = {#} MeV",
    "Fermi gas": "gás de Fermi",
    "constant temperature": "temperatura constante",
    "ln ρ (states per MeV), A = {#}": "ln ρ (estados por MeV), A = {#}",
    "levels {#}–{#}": "níveis {#}–{#}",
    "levels {#} to {#}: taken as complete": "níveis {#} a {#}: considerados completos",
    "number of levels below E": "número de níveis abaixo de E",
    "trial Eₓ = {#} MeV: the line gives {#} levels for {#} counted": "Eₓ de ensaio = {#} MeV: a reta dá {#} níveis para {#} contados",
    "F = {#}": "F = {#}",
    "F(Eₓ): predicted minus counted (signed log scale)": "F(Eₓ): previstos menos contados (escala log com sinal)",
    "bisection step {#}: [{#}, {#}]": "passo de bisseção {#}: [{#}, {#}]",
    "root Eₓ = {#} MeV": "raiz Eₓ = {#} MeV",
    "below: {#}/T with T = {#} MeV (Fermi-gas T)": "abaixo: {#}/T com T = {#} MeV (T do gás de Fermi)",
    "below: {#}/T with T = {#} MeV (empirical T)": "abaixo: {#}/T com T = {#} MeV (T empírico)",
    "above: Fermi gas, T = {#} MeV": "acima: gás de Fermi, T = {#} MeV",
    "slope jumps by {#} % at Eₓ = {#} MeV": "o declive salta {#} % em Eₓ = {#} MeV",
    "tangent at Eₓ = {#} MeV: no jump": "tangente em Eₓ = {#} MeV: sem salto",
    "ln ρ, lead-like nucleus (A = {#}, δW = {#} MeV)": "ln ρ, núcleo semelhante ao chumbo (A = {#}, δW = {#} MeV)",
    "F changes sign: a root exists": "F muda de sinal: existe uma raiz",
    "F(Eₓ) never reaches zero: no matching energy": "F(Eₓ) nunca chega a zero: não há energia de junção",
    "{#} keV": "{#} keV",
    "measured {#} ± {#} keV": "medido {#} ± {#} keV",
    "computed D₀ = {#} keV": "D₀ calculado = {#} keV",
    "s-wave resonances above Sₙ, {#} keV shown: about {#} levels": "ressonâncias de onda s acima de Sₙ, {#} keV visíveis: cerca de {#} níveis",
    "iron{#}-like compound nucleus, Sₙ = {#} MeV, spin and parity ½⁺": "núcleo composto semelhante ao ferro{#}, Sₙ = {#} MeV, spin e paridade ½⁺",
  };
  // rho(Sn) printed plainly or as "1.2e5"
  for (const r of ["{#}", "{#}e{#}"])
    L[`ã × {#} = {#} MeV⁻¹ · σ² = {#} · ρ(Sₙ) = ${r} per MeV`] = `ã × {#} = {#} MeV⁻¹ · σ² = {#} · ρ(Sₙ) = ${r} por MeV`;
  Object.assign(WT.L.labels, L);
})();
Object.assign(WT.L.glossary, {
  gilbertCameron: {
    term: "Gilbert–Cameron", aliases: ["Gilbert–Cameron", "Gilbert-Cameron"],
    short: "Uma densidade de níveis composta: uma lei de temperatura constante a baixa energia unida ao gás de Fermi acima de uma energia de junção, com o mesmo valor e o mesmo declive na junção.",
    more: "Proposta por A. Gilbert e A. G. W. Cameron em 1965. É a opção por defeito do TALYS e do motor (ldmodel 1), com o parâmetro de densidade de níveis dependente da energia de Ignatyuk.",
    chapter: "densities",
  },
  ignatyuk: {
    term: "Ignatyuk", aliases: ["Ignatyuk"],
    short: "A forma de Ignatyuk do parâmetro de densidade de níveis: a correção de camadas atua por inteiro a baixa excitação e desvanece-se com a energia, pelo que a(U) tende para o seu valor suave.",
    formula: "a(U) = ã [1 + δW (1 − e^(−γU)) / U]",
    chapter: "densities",
  },
});
