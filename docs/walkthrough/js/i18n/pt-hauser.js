/* Portuguese (pt-PT): hauser (Capítulo 13, Especialista) */
WT.L.ch.hauser = {
  num: "Capítulo 13", title: "Hauser–Feshbach, canal a canal", short: "Hauser–Feshbach",
  lead: "O Capítulo 6 contou a competição entre as saídas como um jogo de portas. Eis a fórmula por trás das portas, um canal de cada vez, e a correção de que precisa quando só há poucos canais abertos.",
  html: `
<div class="step">
  <h3>Uma transmissão para cada canal</h3>
  <p>Um <b>canal</b> é um endereço de saída completo: que partícula sai, em que estado fica o núcleo residual, o momento angular orbital <i>l</i> e o momento angular total <i>j</i> = <i>l</i> ± ½ da partícula. O modelo ótico do Capítulo 2 dá a cada um um <b>coeficiente de transmissão</b> <i>T<sub>lj</sub></i>. As colunas são as do neutrão incidente, para um alvo de spin 0.</p>
  <div class="ctl"><label for="hf-e">Energia do neutrão (MeV)</label><input id="hf-e" type="range" data-bind="lgE" min="-3" max="0.7" step="0.01" value="-0.3"><output data-show="Eshow" data-fmt="3"></output></div>
  <p>A 1 keV só está aberto <i>l</i> = 0, com <i>T</i> ≈ 2π<i>S</i><sub>0</sub>√<i>E</i>, uns poucos por cento. Cada unidade extra de <i>l</i> custa, a baixa energia, cerca de um fator (<i>kR</i>)², por isso as colunas abrem-se uma a uma à medida que a energia sobe. Cada coluna alimenta o núcleo composto com o peso g<sub>J</sub><i>T</i>:</p>
  <div class="formula">σ<sub>CN</sub> = (π/k²) Σ<sub>J,π</sub> g<sub>J</sub> Σ<sub>lj</sub> T<sub>lj</sub> ,  g<sub>J</sub> = (2J+1) / [(2s+1)(2I+1)]</div>
</div>
<div class="step">
  <h3>Um spin e uma paridade de cada vez</h3>
  <p>O momento angular e a paridade conservam-se, por isso o núcleo composto decai de forma independente em cada <i>J</i><sup>π</sup>. Dentro de um bloco, cada canal de saída aberto compete com o seu próprio <i>T</i>: a elástica, de volta ao estado fundamental; a inelástica, para cada nível excitado (uma coluna soma os (<i>l</i>, <i>j</i>) que acoplam ao mesmo <i>J</i>); o contínuo acima de 3,6 MeV, cujos intervalos contam como muitos canais, ponderados pela densidade de níveis; e a captura, agrupada num único <i>T</i><sub>γ</sub> = 2π⟨Γ<sub>γ</sub>⟩/<i>D</i>, minúsculo. As alturas estão em escala logarítmica.</p>
  <div class="ctl"><label for="hf-j">Bloco de spin e paridade</label><input id="hf-j" type="range" data-bind="jb" min="0" max="9" step="1" value="2" data-instant><output data-show="jbShow" data-fmt="0"></output></div>
  <div class="ctl"><label for="hf-e2">Energia do neutrão (MeV)</label><input id="hf-e2" type="range" data-bind="lgE" min="-3" max="0.7" step="0.01" value="-0.3"><output data-show="Eshow" data-fmt="3"></output></div>
  <p>A barra em baixo é a repartição de <b>Hauser–Feshbach</b>: cada saída leva a fração <i>T<sub>b</sub></i>/Σ<i>T<sub>c</sub></i> do que entrou pelo canal <i>a</i>. Abaixo de 0,85 MeV só estão abertas a elástica e a captura, e a elástica leva quase tudo.</p>
  <div class="formula">σ<sub>ab</sub> = (π/k²) Σ<sub>J,π</sub> g<sub>J</sub> T<sub>a</sub> T<sub>b</sub> / Σ<sub>c</sub> T<sub>c</sub> · W<sub>ab</sub></div>
</div>
<div class="step">
  <h3>Flutuações de larguras</h3>
  <p>Com <i>W<sub>ab</sub></i> = 1, a fórmula multiplica médias. Mas as ressonâncias por trás das médias têm larguras dispersas (Porter–Thomas, Capítulo 10) e, na dispersão elástica, a largura que deixa o neutrão entrar é a mesma que o deixa sair, pelo que as duas estão correlacionadas. Para a elástica, a média dos produtos excede então o produto das médias, e as outras saídas perdem o que a elástica ganha.</p>
  <div class="btns"><button class="btn ghost" data-act="w0" aria-pressed="false">Sem correção</button><button class="btn ghost" data-act="w1" aria-pressed="true">Moldauer</button></div>
  <div class="ctl"><label for="hf-e3">Energia do neutrão (MeV)</label><input id="hf-e3" type="range" data-bind="lgE" min="-3" max="0.7" step="0.01" value="-0.3"><output data-show="Eshow" data-fmt="3"></output></div>
  <p>Os distintivos dão σ com a correção dividida por σ sem ela. Abaixo do primeiro limiar inelástico, a elástica já leva quase todo o fluxo e quase não muda, enquanto a captura perde 10 a 25 por cento. Entre 1 e 1,5 MeV, a elástica composta ganha 15 a 35 por cento, e o primeiro nível 2⁺ perde cerca de um terço. À medida que se abrem mais níveis e o contínuo, a elástica composta passa a ser uma fração pequena do fluxo: o seu próprio fator sobe em direção a 2, mas o que tira às outras diminui, e os fatores destas regressam a 1. Na receita de Moldauer cada canal recebe um número de graus de liberdade ν<sub>c</sub>, e <i>W</i> é um integral a uma dimensão, calculado com a regra de Gauss–Laguerre de 32 pontos do TALYS.</p>
  <div class="formula">W<sub>ab</sub> = (1 + 2δ<sub>ab</sub>/ν<sub>a</sub>) ∫₀^∞ dx Π<sub>c</sub> (1 + 2T<sub>c</sub>x / ν<sub>c</sub>ΣT)<sup>−(δ<sub>ac</sub>+δ<sub>bc</sub>+ν<sub>c</sub>/2)</sup></div>
  <div class="formula">ν<sub>c</sub> = 1.78 + (T<sub>c</sub><sup>1.212</sup> − 0.78) e<sup>−0.228 ΣT</sup></div>
</div>
<div class="step">
  <h3>Moldauer e HRTW</h3>
  <p>As curvas repetem o mesmo cálculo em toda a gama de energias: a razão para a elástica composta, para o primeiro nível 2⁺ e para a captura, com Moldauer a cheio e a receita <b>HRTW</b> a tracejado. A HRTW substitui o integral por um fator elástico <i>W<sub>a</sub></i> e por transmissões efetivas <i>V<sub>a</sub></i> obtidas por iteração.</p>
  <div class="ctl"><label for="hf-e4">Energia do neutrão (MeV)</label><input id="hf-e4" type="range" data-bind="lgE" min="-3" max="0.7" step="0.01" value="-0.3"><output data-show="Eshow" data-fmt="3"></output></div>
  <div class="formula">σ<sub>ab</sub> ∝ V<sub>a</sub>V<sub>b</sub> / ΣV<sub>c</sub> · [1 + δ<sub>ab</sub>(W<sub>a</sub> − 1)] ,  V<sub>a</sub> = T<sub>a</sub> / [1 + (W<sub>a</sub> − 1) V<sub>a</sub>/ΣV]</div>
  <p>As duas concordam de perto para a elástica e a inelástica; para a captura na região dos keV, a HRTW retira até mais 10 por cento. Entre 0,85 e 2 MeV a captura chega a ganhar: aí a largura total é dominada por umas poucas larguras neutrónicas que flutuam, e a média de 1/Γ excede 1/⟨Γ⟩. Ambas as receitas são ajustes ao resultado exato de matrizes aleatórias (GOE), que o TALYS também oferece como um integral triplo. O INCOGNITA adapta as três (<code>widthmode</code> 1, 2, 3); Moldauer é a opção por defeito, aplicada a neutrões incidentes até à energia de separação do neutrão do alvo.</p>
</div>
<div class="step">
  <h3>Entre 3 e 2</h3>
  <p>Os limites explicam o tamanho do efeito. Toma <i>N</i> canais iguais, sem captura, e faz variar a sua soma ΣT, que é 2π vezes a razão entre a largura total média e o espaçamento dos níveis, Γ/<i>D</i>. Com ressonâncias isoladas (ΣT ≪ 1) e muitos canais, cada largura segue Porter–Thomas com um grau de liberdade, e o reforço elástico é ⟨Γ<sub>a</sub>²⟩/⟨Γ<sub>a</sub>⟩² = 3. Quando as ressonâncias se sobrepõem fortemente (ΣT ≫ 2π), a secção eficaz flutua como uma onda aleatória (flutuações de Ericson) e o reforço desce para 2.</p>
  <div class="ctl"><label for="hf-n">Canais abertos N</label><input id="hf-n" type="range" data-bind="nch" min="2" max="60" step="1" value="30" data-instant><output data-show="nch" data-fmt="0"></output></div>
  <p>Para <i>N</i> canais isolados o valor exato é 3<i>N</i>/(<i>N</i>+2) (o losango): com apenas dois canais o reforço não pode passar de 1,5, porque a largura total flutua então tanto como a elástica. A receita de Moldauer reproduz este limite; a HRTW fica aquém dele quando há muitos canais fracos abertos. A inserção desenha ressonâncias com a largura que corresponde ao ponto em movimento. Na fórmula de Moldauer, o limite de muitos canais é 1 + 2/ν: ν → 1 para ressonâncias isoladas, ν → 1,78 quando se sobrepõem (2,12, o pequeno erro do ajuste na sobreposição total).</p>
  <div class="aside">No código: <code>compound/prepare.py</code> (canais de saída e as suas transmissões por <i>J</i><sup>π</sup>), <code>compound/target.py</code> (as somas de Hauser–Feshbach), <code>compound/wfc.py</code> (Moldauer, HRTW e GOE, adaptados do TALYS). A imagem avalia as mesmas fórmulas com ingredientes ilustrativos: transmissões de esfera dura para um alvo semelhante ao ferro, sete níveis, um contínuo de temperatura constante e um único canal de captura agrupado.</div>
</div>`,
};
(function () {
  const L = {
    // scene 1
    "T = {#}": "T = {#}",
    "hollow: j = l − ½ · solid: j = l + ½": "oco: j = l − ½ · cheio: j = l + ½",
    "compound nucleus": "núcleo composto",
    "compound nucleus · σ(CN) ≈ {#} b": "núcleo composto · σ(CN) ≈ {#} b",
    "σ(CN) ≈ {#} b": "σ(CN) ≈ {#} b",
    "E = {#} MeV · kR = {#}": "E = {#} MeV · kR = {#}",
    "E = {#} keV · kR = {#}": "E = {#} keV · kR = {#}",
    "transmission Tₗⱼ of the incident neutron": "transmissão Tₗⱼ do neutrão incidente",
    // scene 2
    "elastic": "elástica", "cont.": "cont.",
    "level energy (MeV) under each column": "energia do nível (MeV) sob cada coluna",
    "residual level (energy in MeV) · n×: number of (l, j) channels summed": "nível residual (energia em MeV) · n×: número de canais (l, j) somados",
    "{#}/{#}⁺ block · in through l = {#}, Tₐ = {#}": "bloco {#}/{#}⁺ · entra por l = {#}, Tₐ = {#}",
    "{#}/{#}⁻ block · in through l = {#}, Tₐ = {#}": "bloco {#}/{#}⁻ · entra por l = {#}, Tₐ = {#}",
    "elastic {#} %": "elástica {#} %",
    "higher {#} %": "superiores {#} %",
    "Hauser–Feshbach split: T / ΣT for each exit": "repartição de Hauser–Feshbach: T / ΣT para cada saída",
    // scene 3
    "closed": "fechado",
    "compound elastic": "elástica composta",
    "first {#}⁺ level": "primeiro nível {#}⁺",
    "higher levels": "níveis superiores",
    "capture": "captura",
    "{#} mb": "{#} mb",
    "with Moldauer's correction": "com a correção de Moldauer",
    "Hauser–Feshbach without correction": "Hauser–Feshbach sem correção",
    "compound formation {#} mb at {#} MeV": "formação do núcleo composto: {#} mb a {#} MeV",
    "compound formation {#} mb at {#} keV": "formação do núcleo composto: {#} mb a {#} keV",
    // scene 4
    "{#}⁺ opens": "abre-se o {#}⁺",
    "continuum": "contínuo",
    "continuum opens": "abre-se o contínuo",
    "elastic ×{#} (Moldauer) · ×{#} (HRTW)": "elástica ×{#} (Moldauer) · ×{#} (HRTW)",
    "capture ×{#} (Moldauer) · ×{#} (HRTW)": "captura ×{#} (Moldauer) · ×{#} (HRTW)",
    "first {#}⁺ ×{#} (Moldauer) · ×{#} (HRTW)": "primeiro {#}⁺ ×{#} (Moldauer) · ×{#} (HRTW)",
    "solid: Moldauer · dashed: HRTW": "cheio: Moldauer · tracejado: HRTW",
    "σ with correction / σ without": "σ com correção / σ sem correção",
    // scene 5
    "ΣT = {#}πΓ/D →": "ΣT = {#}πΓ/D →",
    "elastic enhancement Wₐₐ": "reforço elástico Wₐₐ",
    "T → {#} per channel": "T → {#} por canal",
    "exact, isolated: {#}N/(N+{#}) = {#}": "exato, isoladas: {#}N/(N+{#}) = {#}",
    "Porter–Thomas: {#}": "Porter–Thomas: {#}",
    "Ericson: {#}": "Ericson: {#}",
    "{#} channels · ΣT = {#} · Wₐₐ = {#}": "{#} canais · ΣT = {#} · Wₐₐ = {#}",
    "isolated resonances: Γ ≪ D": "ressonâncias isoladas: Γ ≪ D",
    "resonances begin to overlap": "as ressonâncias começam a sobrepor-se",
    "strongly overlapping: Γ ≫ D": "fortemente sobrepostas: Γ ≫ D",
  };
  Object.assign(WT.L.labels, L);
})();
Object.assign(WT.L.glossary, {
  hrtw: {
    term: "HRTW", aliases: ["HRTW"],
    short: "Uma receita de flutuação de larguras de Hofmann, Richert, Tepel e Weidenmüller: um fator elástico por canal e transmissões efetivas obtidas por iteração.",
    more: "Tal como a de Moldauer, foi ajustada a cálculos numéricos de matrizes aleatórias. O TALYS oferece-a como widthmode 2; Moldauer (1) é a opção por defeito e o integral triplo exato do GOE (3) é a referência.",
    chapter: "hauser",
  },
  ericson: {
    term: "Flutuações de Ericson", aliases: ["flutuações de Ericson", "flutuação de Ericson"],
    short: "Flutuações aleatórias de uma secção eficaz com a energia quando muitas ressonâncias se sobrepõem, numa escala de energia fixada pela sua largura total média.",
    more: "São o limite de sobreposição forte da mesma estatística que dá as larguras de Porter–Thomas para ressonâncias isoladas. Nesse limite, o fator de reforço elástico tende para 2.",
    chapter: "hauser",
  },
});
