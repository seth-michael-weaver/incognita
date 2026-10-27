/* Portuguese (pt-PT): optical (Capítulo 23, Especialista) */
WT.L.ch.optical = {
  num: "Capítulo 23", title: "O modelo ótico, resolvido", short: "Modelo ótico, resolvido",
  lead: "O Capítulo 5 desenhou o potencial ótico como uma bola de vidro baço. Aqui aparece como o motor o usa: uma parametrização global, uma equação de Schrödinger radial integrada passo a passo e uma condição de ajuste que transforma a onda em coeficientes de transmissão.",
  html: `
<div class="step">
  <h3>O potencial de Koning–Delaroche</h3>
  <p>Para neutrões e protões em alvos esféricos, a opção por defeito é o potencial de <b>Koning–Delaroche</b> (KD03): formas de Woods–Saxon cujas profundidades variam suavemente com a energia e com a massa e o excesso de neutrões do alvo, a partir de uma fórmula global ou, para os núcleos que o KD03 ajustou um a um, como o ferro-56, de um ajuste local da mesma forma. A imagem usa a fórmula global para neutrões em ferro-56. O poço real (azul) liga; as partes imaginárias (vermelho) absorvem, no volume e, sobretudo a baixa energia, numa camada fina à superfície.</p>
  <div class="ctl"><label for="op-e">Energia do neutrão (MeV)</label><input id="op-e" type="range" data-bind="E" min="0.1" max="80" step="0.1" value="5"><output data-show="E" data-fmt="1"></output></div>
  <div class="formula">U(r) = −V<sub>V</sub> f(r) − iW<sub>V</sub> f(r) + 4i a<sub>D</sub>W<sub>D</sub> df<sub>D</sub>/dr + 2(V<sub>so</sub> + iW<sub>so</sub>) (1/r) df<sub>so</sub>/dr ⟨l·σ⟩</div>
  <p>Os neutrões de sonda atravessam à energia que escolheres e desvanecem-se onde a absorção morde: o seu livre percurso médio é ħ<i>v</i>/2|<i>W</i>|. Cada profundidade é função de <i>E</i> − <i>E</i><sub>F</sub>, medida a partir da energia de Fermi: a profundidade real desce lentamente, a absorção de superfície <i>W</i><sub>D</sub> tem o máximo perto de 10 MeV e a absorção de volume <i>W</i><sub>V</sub> cresce continuamente até dominar, aqui acima de cerca de 45 MeV.</p>
</div>
<div class="step">
  <h3>Integrar a equação radial</h3>
  <p>Cada onda parcial obedece à sua própria equação radial. O motor integra-a para fora a partir de <i>r</i> = 0 com o <b>método de Numerov</b>, uma regra de três pontos exata até à sexta potência do passo, através do potencial complexo completo.</p>
  <div class="formula">u″<sub>lj</sub>(r) = [ l(l+1)/r² + (2μ/ħ²) U<sub>lj</sub>(r) − k² ] u<sub>lj</sub>(r)</div>
  <div class="ctl"><label for="op-l">Onda parcial l</label><input id="op-l" type="range" data-bind="L" min="0" max="10" step="1" value="1" data-instant><output data-show="L" data-fmt="0"></output></div>
  <div class="ctl"><label for="op-e2">Energia do neutrão (MeV)</label><input id="op-e2" type="range" data-bind="E" min="0.1" max="80" step="0.1" value="5"><output data-show="E" data-fmt="1"></output></div>
  <p>A linha cheia é a onda no tempo, Re[<i>u</i> e<sup>−iωt</sup>]; a linha tracejada é a onda livre, como se o núcleo não existisse. Dentro do poço a onda é mais curta (o neutrão é mais rápido) e mais pequena (absorvida); fora, regressa desfasada.</p>
</div>
<div class="step">
  <h3>Da onda a S e T</h3>
  <p>Para lá de cerca de 12 fm o potencial anulou-se e a onda tem de ser uma mistura de uma onda livre que entra e de outra que sai, <i>u</i> ∝ <i>H</i><sup>−</sup> − <i>S</i> <i>H</i><sup>+</sup>. Ajustar a <i>u</i> integrada em dois raios fixa o elemento <i>S<sub>lj</sub></i> da <b>matriz S</b>: a amplitude que sai, com a sua fase.</p>
  <div class="btns"><button class="btn ghost" data-act="abs" aria-pressed="false">Desligar a absorção</button></div>
  <div class="formula">S<sub>lj</sub> = η<sub>lj</sub> e<sup>2iδ<sub>lj</sub></sup> ,  T<sub>lj</sub> = 1 − |S<sub>lj</sub>|²</div>
  <p>O ponto é <i>S</i> no plano complexo, dentro do círculo unitário; o seu rasto é o caminho que percorre enquanto a energia varre de 0,1 a 40 MeV. Sem absorção, |<i>S</i>| = 1: o ponto corre sobre o círculo, a onda só muda de fase e <i>T</i> = 0. A distância para dentro do círculo é o que recebem o núcleo composto e todas as outras reações.</p>
</div>
<div class="step">
  <h3>O spin–órbita separa j</h3>
  <p>O termo de <b>spin–órbita</b> é atrativo para <i>j</i> = <i>l</i> + ½ e repulsivo para <i>j</i> = <i>l</i> − ½. É pequeno, uns poucos MeV à superfície, mas afasta as duas transmissões de cada <i>l</i>, sobretudo perto da onda parcial que roça a superfície.</p>
  <div class="ctl"><label for="op-e3">Energia do neutrão (MeV)</label><input id="op-e3" type="range" data-bind="E" min="0.1" max="80" step="0.1" value="5"><output data-show="E" data-fmt="1"></output></div>
  <div class="btns"><button class="btn ghost" data-act="so" aria-pressed="false">Desligar o spin–órbita</button></div>
  <p>O Hauser–Feshbach (Capítulo 22) usa as duas em separado; somadas com os seus pesos, (<i>l</i>+1)<i>T</i><sub>l,l+½</sub> + <i>l</i> <i>T</i><sub>l,l−½</sub>, dão uma secção eficaz de reação quase inalterada, e é por isso que as secções eficazes totais quase não restringem a intensidade do spin–órbita e são precisos dados de polarização.</p>
</div>
<div class="step">
  <h3>As secções eficazes</h3>
  <p>Somar as ondas parciais dá os observáveis a que o potencial é ajustado. A secção eficaz de reação conta o fluxo removido, a secção eficaz total decorre da amplitude para a frente, e a sua diferença é a dispersão elástica de forma.</p>
  <div class="formula">σ<sub>R</sub> = (π/k²) Σ<sub>l</sub> [(l+1)T<sub>l,l+½</sub> + l T<sub>l,l−½</sub>] ,  σ<sub>tot</sub> = (2π/k²) Σ<sub>lj</sub> (j+½)(1 − Re S<sub>lj</sub>)</div>
  <div class="ctl"><label for="op-e4">Energia do neutrão (MeV)</label><input id="op-e4" type="range" data-bind="E" min="0.2" max="50" step="0.1" value="5"><output data-show="E" data-fmt="1"></output></div>
  <p>O KD03 foi ajustado a dados destes para muitos núcleos, de 1 keV a 200 MeV; a secção eficaz total do ferro, entre 3,5 e 4 b a poucos MeV e 2,5 b a 14 MeV, sai com cerca de 5 por cento de desvio, sem qualquer ajuste a este núcleo, máximos largos incluídos: são o tamanho do núcleo visto face ao comprimento de onda do neutrão.</p>
</div>
<div class="step">
  <h3>O extremo de baixa energia</h3>
  <p>Abaixo de uns poucos keV só conta a onda s, e <i>T</i><sub>0</sub> cresce como √<i>E</i>: um declive de um meio neste gráfico log–log. A constante é a <b>função de intensidade</b> <i>S</i><sub>0</sub> = <i>T</i><sub>0</sub>/(2π√<i>E</i>), com <i>E</i> em eV, a mesma grandeza que as análises de ressonâncias medem como Σ Γ<sub>n</sub><sup>0</sup>/Δ<i>E</i>.</p>
  <p>Um potencial global é ajustado sobretudo a energias de MeV, e o seu extremo de baixa energia é o seu ponto mais fraco. Para o ferro-56, este dá <i>S</i><sub>0</sub> ≈ 5,5 × 10⁻⁴, e o ajuste local do KD03 quase o mesmo, enquanto o valor medido (RIPL) é 2,3 ± 0,6 × 10⁻⁴: o ferro está perto do máximo da ressonância de tamanho 3s, em torno de <i>A</i> ≈ 55, onde <i>S</i><sub>0</sub> é mais sensível ao potencial. É por isso que os <i>S</i><sub>0</sub> e <i>S</i><sub>1</sub> medidos são uma entrada separada e opcional do motor.</p>
  <div class="aside">No código: <code>omp/parameters.py</code> (o KD03 e os outros potenciais globais), <code>omp/potential.py</code> (os fatores de forma radiais), <code>omp/schrodinger.py</code> (integração de Numerov e ajuste, com funções de Coulomb pelo método de Steed para partículas carregadas; substitui o ECIS para alvos esféricos e é verificado face aos T<sub>lj</sub> do ECIS), <code>ecis/</code> (a adaptação de canais acoplados para alvos deformados), <code>omp/sfunc.py</code> (opcional: S₀, S₁ medidos). A imagem resolve a própria equação, de forma não relativista, para neutrões em ferro-56.</div>
</div>`,
};
(function () {
  const L = {
    "{#} fm": "{#} fm",
    "real well, depth {#} MeV": "poço real, profundidade {#} MeV",
    "surface absorption, peak {#} MeV": "absorção de superfície, máximo {#} MeV",
    "volume absorption {#} MeV": "absorção de volume {#} MeV",
    "spin–orbit for l = {#}, j = {#}/{#}: {#} MeV": "spin–órbita para l = {#}, j = {#}/{#}: {#} MeV",
    "real": "real", "volume": "volume", "surface": "superfície",
    "depths (MeV) against energy (MeV)": "profundidades (MeV) em função da energia (MeV)",
    "potential: real (blue), imaginary (red)": "potencial: real (azul), imaginário (vermelho)",
    "nuclear surface": "superfície nuclear",
    "l = {#}, j = {#}+½ · E = {#} MeV · |S| = {#} · δ = {#}° · T = {#}": "l = {#}, j = {#}+½ · E = {#} MeV · |S| = {#} · δ = {#}° · T = {#}",
    "solid: the wave now · shaded: its size |u| · dashed: free wave": "cheia: a onda agora · sombreado: o seu tamanho |u| · tracejada: onda livre",
    "Re S": "Re S", "Im S": "Im S",
    "|S| = {#}: nothing absorbed": "|S| = {#}: nada absorvido",
    "l = {#}, j = {#}+½ · E = {#} MeV": "l = {#}, j = {#}+½ · E = {#} MeV",
    "l = {#}, j = {#}+½": "l = {#}, j = {#}+½",
    "|S| = {#} · T = {#} − |S|² = {#}": "|S| = {#} · T = {#} − |S|² = {#}",
    "|S| = {#}": "|S| = {#}",
    "T = {#} − |S|² = {#}": "T = {#} − |S|² = {#}",
    "trail: S as E runs {#} → {#} MeV": "rasto: S enquanto E percorre {#} → {#} MeV",
    "no absorption: S stays on the circle": "sem absorção: S fica sobre o círculo",
    "T = {#}": "T = {#}",
    "l": "l",
    "hollow: j = l − ½ · solid: j = l + ½": "oco: j = l − ½ · cheio: j = l + ½",
    "hollow (purple): j = l − ½ · solid (blue): j = l + ½": "oco (roxo): j = l − ½ · cheio (azul): j = l + ½",
    "reaction cross section {#} b (without spin–orbit {#} b)": "secção eficaz de reação {#} b (sem spin–órbita {#} b)",
    "reaction cross section {#} b (spin–orbit off)": "secção eficaz de reação {#} b (spin–órbita desligado)",
    "grazing l ≈ kR = {#}": "l rasante ≈ kR = {#}",
    "{#} b": "{#} b",
    "total {#} b": "total {#} b",
    "reaction {#} b": "reação {#} b",
    "shape elastic {#} b": "elástica de forma {#} b",
    "n + ⁵⁶Fe, KD{#}, computed here": "n + ⁵⁶Fe, KD{#}, calculado aqui",
    "T₀ (s-wave)": "T₀ (onda s)",
    "T₁ (p-wave, j = {#}/{#}): slope {#}/{#}": "T₁ (onda p, j = {#}/{#}): declive {#}/{#}",
    "dashed: {#}πS₀√E, slope ½": "tracejado: {#}πS₀√E, declive ½",
    "S₀ = {#} × {#}⁻⁴ from this potential": "S₀ = {#} × {#}⁻⁴ com este potencial",
  };
  // mean free path: either number may be printed as "> 100"
  for (const a of ["{#}", "> {#}"]) for (const b of ["{#}", "> {#}"])
    L[`mean free path: ${a} fm at the surface, ${b} fm in the centre`] = `livre percurso médio: ${a} fm à superfície, ${b} fm no centro`;
  Object.assign(WT.L.labels, L);
})();
Object.assign(WT.L.glossary, {
  koningDelaroche: {
    term: "Potencial de Koning–Delaroche", aliases: ["Koning–Delaroche", "Koning-Delaroche", "KD03"],
    short: "O potencial ótico global para neutrões e protões de A. J. Koning e J.-P. Delaroche (2003), de 1 keV a 200 MeV e para massas de 24 a 209.",
    more: "As suas profundidades, raios e difusividades são funções suaves da energia, da massa e do excesso de neutrões, ajustadas de uma só vez a um vasto conjunto de secções eficazes e distribuições angulares medidas. É a opção por defeito para nucleões no TALYS e no motor.",
    chapter: "optical",
  },
  numerov: {
    term: "Método de Numerov", aliases: ["método de Numerov", "Numerov"],
    short: "Uma regra de três pontos para integrar equações de segunda ordem sem termo de primeira derivada, como a equação de Schrödinger radial, com um erro da ordem de h⁶ por passo.",
    formula: "(1 − h²Q_n+1/12) u_n+1 = 2(1 + 5h²Q_n/12) u_n − (1 − h²Q_n−1/12) u_n−1",
    chapter: "optical",
  },
  sMatrix: {
    term: "Matriz S", aliases: ["matriz S", "matrizes S"],
    short: "As amplitudes que ligam ondas que entram a ondas que saem; para a dispersão elástica numa onda parcial, um único número complexo S = η e^(2iδ).",
    more: "|S| = 1 significa que nada é absorvido e só muda a fase δ; o défice 1 − |S|² é o coeficiente de transmissão, o fluxo que vai para as reações.",
    chapter: "optical",
  },
  spinOrbit: {
    term: "Termo de spin–órbita", aliases: ["spin–órbita", "spin-órbita"],
    short: "A parte do potencial nuclear que depende de o spin do nucleão ser paralelo ou antiparalelo ao seu momento angular orbital.",
    more: "É atrativo para j = l + ½ e repulsivo para j = l − ½, com o máximo à superfície nuclear. A mesma interação produz os números mágicos do modelo de camadas.",
    chapter: "optical",
  },
});
