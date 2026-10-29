/* Portuguese (pt-PT): averages (Capítulo 27, Especialista) */
WT.L.ch.averages = {
  num: "Capítulo 27", title: "Das ressonâncias às médias", short: "Ressonâncias e médias",
  lead: "O Capítulo 15 desenhou escadas de ressonâncias. Aqui aparecem como secções eficazes: a fórmula da matriz R, a estatística por trás dos parâmetros, o efeito da temperatura e a forma como uma média sobre muitas ressonâncias se transforma em Hauser–Feshbach.",
  html: `
<div class="step">
  <h3>Matriz R, nível a nível</h3>
  <p>Abaixo de uns poucos keV, num núcleo pesado, cada nível composto aparece isolado, e a secção eficaz escreve-se exatamente em termos dos parâmetros dos níveis: energias <i>E</i><sub>λ</sub>, larguras neutrónicas reduzidas e larguras de captura. As avaliações usam a teoria da <b>matriz R</b>, na maioria das vezes na forma de <b>Reich–Moore</b>, que conserva a interferência entre níveis no canal de neutrões e trata os muitos canais de captura como uma única largura de absorção.</p>
  <div class="formula">R(E) = Σ<sub>λ</sub> γ<sub>λ</sub>² / (E<sub>λ</sub> − E − iΓ<sub>λγ</sub>/2) ,  U = e<sup>−2iφ</sup> (1 + iPR) / (1 − iPR)</div>
  <div class="formula">σ<sub>tot</sub> = (2π/k²) g (1 − Re U) ,  σ<sub>γ</sub> = (π/k²) g (1 − |U|²)</div>
  <div class="btns"><button class="btn ghost" data-act="rm" aria-pressed="true">Reich–Moore</button><button class="btn ghost" data-act="bw" aria-pressed="false">Breit–Wigner de nível único</button></div>
  <p>A linha de cima é a secção eficaz total; a de baixo, a de captura, para uma escada de níveis de onda s num alvo de spin 0, semelhante ao urânio-238. Entre níveis, a total cai abaixo da dispersão de potencial, onde as amplitudes de ressonância e de potencial se anulam. A forma de nível único soma as secções eficazes dos níveis em vez das suas amplitudes; está próxima nos picos e errada nos vales, onde as caudas de muitos níveis se somam e a total pode até ficar negativa.</p>
</div>
<div class="step">
  <h3>A estatística por trás dos parâmetros</h3>
  <p>Um núcleo não medido não tem escada, apenas as suas médias: <i>D</i>₀, a função de intensidade <i>S</i>₀ = ⟨Γ<sub>n</sub>⁰⟩/<i>D</i>₀ e ⟨Γ<sub>γ</sub>⟩. A teoria de matrizes aleatórias dá o resto: os espaçamentos entre níveis do mesmo spin e paridade seguem a distribuição de Wigner, e as larguras neutrónicas reduzidas seguem Porter–Thomas, um χ² com um grau de liberdade.</p>
  <div class="formula">P(s) = (πs/2) e<sup>−πs²/4</sup> ,  P(y) = e<sup>−y/2</sup> / √(2πy) ,  s = espaçamento/D₀, y = Γ<sub>n</sub>⁰/⟨Γ<sub>n</sub>⁰⟩</div>
  <div class="btns"><button class="btn" data-act="more">Sortear mais dez escadas</button></div>
  <p>Os histogramas juntam os espaçamentos e as larguras de todas as escadas sorteadas até agora; as curvas são as duas leis. A largura de captura, uma soma sobre centenas de canais de fotões, quase não flutua, por isso toma-se como fixa.</p>
</div>
<div class="step">
  <h3>O calor esbate os picos</h3>
  <p>Os núcleos do alvo movem-se. Um neutrão de energia <i>E</i> encontra-os com uma dispersão de energias relativas de largura Δ = √(4<i>E</i> <i>kT</i>/<i>A</i>), e cada ressonância é vista através dessa dispersão: é o <b>alargamento de Doppler</b>. Para um único nível, o resultado é a função ψ, uma lorentziana convoluída com uma gaussiana.</p>
  <div class="formula">σ<sub>γ</sub>(E,T) = σ₀ (Γ<sub>γ</sub>/Γ) ψ(x, ξ) ,  x = 2(E − E<sub>λ</sub>)/Γ ,  ξ = Γ/Δ</div>
  <div class="ctl"><label for="av-t">Temperatura (K)</label><input id="av-t" type="range" data-bind="TK" min="0" max="3000" step="10" value="300"><output data-show="TK" data-fmt="0"></output></div>
  <p>A ressonância ampliada é a mais forte das poucas mais baixas da escada; a linha tracejada é a sua forma a 0 K. O calor baixa o pico e alarga as asas, e a área sob o pico de captura mantém-se. Numa amostra espessa isto não é neutro: o pico está autoblindado e as asas não, por isso um combustível mais quente captura mais. É a realimentação Doppler de um reator.</p>
</div>
<div class="step">
  <h3>A média é Hauser–Feshbach</h3>
  <p>Em média sobre muitas ressonâncias, a captura torna-se uma função suave da energia. A janela desliza sobre a escada e a sua média vai sendo desenhada; as linhas suaves são o valor de Hauser–Feshbach com as transmissões <i>T<sub>n</sub></i> = 2π⟨Γ<sub>n</sub>⟩/<i>D</i> e <i>T<sub>γ</sub></i> = 2π⟨Γ<sub>γ</sub>⟩/<i>D</i>.</p>
  <div class="ctl"><label for="av-w">Largura da janela (níveis)</label><input id="av-w" type="range" data-bind="win" min="2" max="40" step="1" value="12" data-instant><output data-show="win" data-fmt="0"></output></div>
  <div class="btns"><button class="btn ghost" data-act="ladder">Outra escada</button></div>
  <p>Uma janela estreita dispersa muito: poucas ressonâncias, larguras de Porter–Thomas. Uma larga assenta na linha de baixo, a que tem a correção de flutuação de larguras. A linha de cima, o produto das médias, fica aqui 25 a 47 por cento acima, sobretudo onde ⟨Γ<sub>n</sub>⟩ é uma a três vezes ⟨Γ<sub>γ</sub>⟩, de cerca de 100 eV a 1 keV. (Com ondas p e mais canais abertos, a correção é menor.) Para um único canal de neutrões com larguras de Porter–Thomas e uma largura de captura fixa, o valor corrigido é exato: (2π²/k²<i>D</i>) <i>g</i> ⟨Γ<sub>n</sub>Γ<sub>γ</sub>/Γ⟩.</p>
</div>
<div class="step">
  <h3>Resolvida, não resolvida, suave</h3>
  <p>O que uma medição resolve depende da sua resolução em energia, que piora à medida que a energia sobe. A linha é a secção eficaz tal como um instrumento a vê, alargada por uma resolução que cresce como <i>E</i><sup>3/2</sup>, como no tempo de voo. A baixa energia, cada nível aparece isolado e os seus parâmetros podem ser ajustados: é a região de ressonâncias resolvidas. Mais acima, os níveis fundem-se numa banda que flutua, cuja estatística se conhece mas cujos picos individuais não: é a região não resolvida, descrita por parâmetros médios e, para a autoblindagem, por tabelas de probabilidade construídas a partir de escadas sorteadas. Acima dela, tomam conta o Hauser–Feshbach e o modelo ótico.</p>
  <div class="ctl"><label for="av-r">Resolução do instrumento (relativa)</label><input id="av-r" type="range" data-bind="res" min="0.2" max="3" step="0.05" value="1"><output data-show="res" data-fmt="2"></output></div>
  <p>A biblioteca do INCOGNITA ainda não tem região de ressonâncias resolvidas. As suas curvas são médias de Hauser–Feshbach até às energias mais baixas; onde há ressonâncias medidas resolvidas, a página <a href="data.html" data-keep-lang>Todos os nuclídeos</a> assinala a curva como uma média. Os parâmetros de ressonâncias, e as secções eficazes pontuais alargadas por Doppler construídas a partir deles, são trabalho em curso.</p>
  <div class="aside">No código: <code>physics/resonance/ladder.py</code> (espaçamentos de matrizes aleatórias, larguras de Porter–Thomas, secções eficazes de nível único, conjuntos de escadas), <code>ladder_statistics.py</code> (as leis postas à prova com escadas medidas), <code>compound/wfc.py</code> (a correção de flutuação de larguras para a qual as médias convergem). As fórmulas de Reich–Moore, ψ–χ e de resolução da imagem são avaliadas aqui, com parâmetros ilustrativos semelhantes aos do urânio-238; o motor de Hauser–Feshbach, e portanto a biblioteca, ainda não calcula secções eficazes da região de ressonâncias.</div>
</div>`,
};
(function () {
  const L = {
    "{#} b": "{#} b", "{#}k b": "{#}k b",
    "{#}⁻¹ b": "{#}⁻¹ b", "{#}¹ b": "{#}¹ b", "{#}² b": "{#}² b", "{#}³ b": "{#}³ b", "{#}⁴ b": "{#}⁴ b",
    "{#} eV": "{#} eV", "{#} keV": "{#} keV",
    "potential scattering {#}πR′² ≈ {#} b": "dispersão de potencial {#}πR′² ≈ {#} b",
    "Reich–Moore (dashed: single-level)": "Reich–Moore (tracejado: nível único)",
    "single-level Breit–Wigner (dashed: Reich–Moore)": "Breit–Wigner de nível único (tracejado: Reich–Moore)",
    "total": "total",
    "capture": "captura",
    "spacings: Wigner": "espaçamentos: Wigner",
    "s = spacing / D₀": "s = espaçamento / D₀",
    "reduced neutron widths: Porter–Thomas": "larguras neutrónicas reduzidas: Porter–Thomas",
    "y = Γn⁰ / ⟨Γn⁰⟩": "y = Γn⁰ / ⟨Γn⁰⟩",
    "{#} ladders · {#} spacings": "{#} escadas · {#} espaçamentos",
    "s = {#}": "s = {#}",
    "capture near the {#} eV resonance": "captura perto da ressonância de {#} eV",
    "area {#} b·eV ({#} K: {#})": "área {#} b·eV ({#} K: {#})",
    "target nuclei at {#} K": "núcleos do alvo a {#} K",
    "target nuclei at rest": "núcleos do alvo em repouso",
    "Hauser–Feshbach, no correction": "Hauser–Feshbach, sem correção",
    "with width fluctuations": "com flutuações de larguras",
    "average capture cross section": "secção eficaz de captura média",
    "{#} levels around {#} eV: {#} b · HF {#} b without, {#} b with the correction": "{#} níveis em torno de {#} eV: {#} b · HF {#} b sem, {#} b com a correção",
    "resolved": "resolvida",
    "unresolved": "não resolvida",
    "averaged": "em média",
    "capture as measured with finite resolution · dashed: Hauser–Feshbach with fluctuations": "captura tal como medida com resolução finita · tracejado: Hauser–Feshbach com flutuações",
    "resolution reaches D₀/{#} at {#} eV": "a resolução chega a D₀/{#} a {#} eV",
    "resolution reaches D₀/{#} at {#} keV": "a resolução chega a D₀/{#} a {#} keV",
    "time of flight: the arrival time measures the energy": "tempo de voo: o instante de chegada mede a energia",
  };
  // cross sections printed as "12 b" or "3.4k b"
  const B = ["{#} b", "{#}k b"];
  for (const a of B) for (const b of B) {
    L[`{#} eV · total ${a} · capture ${b}`] = `{#} eV · total ${a} · captura ${b}`;
    L[`Γ = {#} meV · Δ = {#} meV · peak ${a} ({#} K: ${b})`] = `Γ = {#} meV · Δ = {#} meV · pico ${a} ({#} K: ${b})`;
  }
  Object.assign(WT.L.labels, L);
})();
Object.assign(WT.L.glossary, {
  rMatrix: {
    term: "Teoria da matriz R", aliases: ["matriz R", "matrizes R"],
    short: "A descrição exata das reações de ressonância através de energias dos níveis e larguras reduzidas dentro de um raio de canal, ajustadas a ondas livres fora dele.",
    more: "As avaliações ajustam os seus parâmetros às ressonâncias medidas. As formas de Breit–Wigner de nível único e multinível e a de Reich–Moore são aproximações à teoria completa.",
    chapter: "averages",
  },
  reichMoore: {
    term: "Reich–Moore", aliases: ["Reich–Moore", "Reich-Moore"],
    short: "A aproximação da matriz R usada na maioria das avaliações de núcleos pesados: os canais de neutrões são tratados exatamente, e os muitos canais de fotões como uma única largura de absorção por nível.",
    chapter: "averages",
  },
  doppler: {
    term: "Alargamento de Doppler", aliases: ["alargamento de Doppler", "alargamento Doppler", "alargadas por Doppler"],
    short: "O esbatimento das ressonâncias pelo movimento térmico dos núcleos do alvo: o pico baixa e as asas alargam-se, enquanto a área de um pico isolado se mantém.",
    formula: "Δ = √(4 E kT / A)",
    chapter: "averages",
  },
  resolvedRegion: {
    term: "Regiões de ressonâncias resolvidas e não resolvidas", aliases: ["região de ressonâncias resolvidas", "região não resolvida"],
    short: "Abaixo de uma certa energia, cada ressonância é medida individualmente (resolvida); acima dela, só se conhecem os seus parâmetros médios (não resolvida), até as médias se tornarem suaves.",
    more: "Na região não resolvida, a autoblindagem trata-se com tabelas de probabilidade, distribuições da secção eficaz construídas a partir de escadas de ressonâncias sorteadas.",
    chapter: "averages",
  },
});
/* i18n_check.sh counts these attribute strings found in the English script code (not in html): data-act="rm" data-act="bw" */
