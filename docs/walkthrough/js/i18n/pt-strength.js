/* Portuguese (pt-PT): strength (Capítulo 25, Especialista) */
WT.L.ch.strength = {
  num: "Capítulo 25", title: "Intensidade fotónica, em pormenor", short: "Intensidade fotónica",
  lead: "O Capítulo 10 mostrou que fotões prefere um núcleo quente. Este capítulo escreve as funções de intensidade, segue-as até aos coeficientes de transmissão e à largura radiativa média, e põe a correr a cascata que elas comandam.",
  html: `
<div class="step">
  <h3>E1: a cauda da ressonância dipolar gigante</h3>
  <p>A <b>função de intensidade fotónica</b> <i>f<sub>XL</sub></i>(<i>E</i><sub>γ</sub>) é a probabilidade reduzida média para um fotão de tipo <i>XL</i>: dipolo elétrico E1, dipolo magnético M1, e assim por diante. Para E1 é dominada pela ressonância dipolar gigante perto de 18 MeV, mas o decaimento em <i>S<sub>n</sub></i> usa fotões de 1 a 7 MeV, muito abaixo na sua cauda, e a forma dessa cauda é toda a questão.</p>
  <div class="formula">f<sub>E1</sub> = K σ₀Γ₀ · E<sub>γ</sub> Γ(E<sub>γ</sub>,T) / [(E<sub>γ</sub>² − E₀²)² + E<sub>γ</sub>² Γ(E<sub>γ</sub>,T)²] / (1 − e<sup>−E<sub>γ</sub>/T</sup>) ,  Γ(E<sub>γ</sub>,T) = (Γ₀/E₀)(E<sub>γ</sub> + 4π²T²/E₀)</div>
  <div class="ctl"><label for="ps-t">Temperatura dos estados finais T (MeV)</label><input id="ps-t" type="range" data-bind="T" min="0" max="1.5" step="0.01" value="0.7"><output data-show="T" data-fmt="2"></output></div>
  <p>A linha tracejada é a lorentziana padrão (SLO), a forma ajustada à fotoabsorção. Com a sua largura constante, sobrestima a intensidade na janela de decaimento por um fator de 2 a 5, uma falha conhecida há muito nos núcleos esféricos. A linha cheia é a lorentziana modificada simplificada (<b>SMLO</b>): a sua largura cresce com a energia do fotão e com a temperatura dos estados finais, o que baixa a cauda na janela mas deixa uma intensidade finita a energia fotónica nula, como exigem os dados de decaimento. A caixa de ampliação mostra esse patamar, abaixo de 2 MeV: arrasta <i>T</i> até 0 e ele desaparece.</p>
</div>
<div class="step">
  <h3>M1: inversão de spin, tesoura, upbend</h3>
  <p>A intensidade M1 é mais fraca, mas não desprezável: uma ressonância de inversão de spin perto de 41<i>A</i><sup>−1/3</sup> MeV, um modo tesoura perto de 3 MeV nos núcleos deformados (com intensidade a crescer como β²) e um upbend, uma subida para energia fotónica nula observada em dados do método de Oslo e em cálculos do modelo de camadas.</p>
  <div class="ctl"><label for="ps-b">Deformação β (tesoura)</label><input id="ps-b" type="range" data-bind="beta" min="0" max="0.35" step="0.01" value="0.2"><output data-show="beta" data-fmt="2"></output></div>
  <div class="btns"><button class="btn ghost" data-act="up" aria-pressed="true">Upbend</button></div>
  <p>A linha ténue por trás é a E1. Às energias fotónicas mais baixas, aqui abaixo de cerca de 2 MeV, o upbend permite à M1 rivalizar com ela ou superá-la (o marcador mostra onde), e é por isso que importa para o extremo suave da cascata e para a captura longe da estabilidade. A M1 por defeito do motor é a recomendação da IAEA com upbend, tabelada por núcleo, e a sua E1 por defeito é a SMLO-2019 tabelada; as formas fechadas aqui fazem as vezes dessas tabelas.</p>
</div>
<div class="step">
  <h3>Brink–Axel</h3>
  <p>A <b>hipótese de Brink–Axel</b> diz que a intensidade depende da energia do fotão e não do ponto de partida do núcleo: a mesma <i>f</i> vale para uma ressonância em <i>S<sub>n</sub></i> e para um estado a 4 MeV. (A SMLO mantém uma dependência fraca através de <i>T</i>.) Cada energia de partida emite então com o coeficiente de transmissão vezes a densidade de estados finais.</p>
  <div class="formula">T<sub>XL</sub>(E<sub>γ</sub>) = 2π E<sub>γ</sub><sup>2L+1</sup> f<sub>XL</sub>(E<sub>γ</sub>) ,  dΓ/dE<sub>γ</sub> ∝ T<sub>XL</sub>(E<sub>γ</sub>) ρ(E<sub>x</sub> − E<sub>γ</sub>)</div>
  <div class="ctl"><label for="ps-x">Energia de partida Eₓ (MeV)</label><input id="ps-x" type="range" data-bind="Ex" min="2" max="7.6" step="0.05" value="7.6"><output data-show="Ex" data-fmt="2"></output></div>
  <p>O produto de um <i>E</i><sub>γ</sub>³<i>f</i> crescente por um ρ decrescente faz uma bossa. A partir de <i>S<sub>n</sub></i>, aqui tem o máximo perto de 4 a 5 MeV. A partir de pontos mais baixos, é cortada na energia de partida; abaixo da energia de junção, onde ρ é uma exponencial de temperatura constante, a forma é a mesma de qualquer partida, apenas truncada. Põe-se a hipótese à prova comparando intensidades extraídas a diferentes energias de excitação, que é o que fazem as análises do tipo Oslo.</p>
</div>
<div class="step">
  <h3>A largura radiativa média</h3>
  <p>Somar sobre todos os estados finais acessíveis por E1 ou M1 a partir das ressonâncias de onda s (<i>J</i><sup>π</sup> = ½⁺ num alvo de spin 0) dá a sua largura fotónica total média. Está medida, a partir das formas das ressonâncias, para umas centenas de núcleos, e é a principal verificação da intensidade em <i>S<sub>n</sub></i>.</p>
  <div class="formula">⟨Γ<sub>γ</sub>⟩ = D₀/2π · Σ<sub>XL</sub> Σ<sub>J′π′</sub> ∫₀^{S<sub>n</sub>} T<sub>XL</sub>(E<sub>γ</sub>) ρ(S<sub>n</sub> − E<sub>γ</sub>, J′, π′) dE<sub>γ</sub></div>
  <div class="ctl"><label for="ps-s">Fator de escala da intensidade</label><input id="ps-s" type="range" data-bind="scale" min="0.3" max="8" step="0.01" value="1"><output data-show="scale" data-fmt="2"></output></div>
  <p>As curvas mostram de onde vem a largura, fotão a fotão: sobretudo de 3 a 7 MeV, e sobretudo E1, com a M1 a acrescentar cerca de 15 %. Aqui, com formas fechadas e uma densidade de níveis esquemática no lugar das tabelas do motor, a largura sai cerca de um sexto dos 0,92 eV medidos: tão sensível ela é à densidade de níveis abaixo de <i>S<sub>n</sub></i> e à cauda da intensidade. As opções por defeito do TALYS, que o motor segue, dão cerca de 1,3 eV para este núcleo. O cursor aplica o único fator global que uma avaliação ajustaria: cerca de ×6 coloca-a dentro da banda medida. A captura na região dos keV é quase proporcional a ⟨Γ<sub>γ</sub>⟩ quando Γ<sub>γ</sub> ≪ Γ<sub>n</sub>, por isso um fator aqui é um fator em (n,γ). O TALYS pode reescalar a intensidade para um ⟨Γ<sub>γ</sub>⟩ medido (<code>gnorm</code>); no INCOGNITA esse reescalamento, aplicado a todos os núcleos da cascata, é um interruptor opcional, desligado por defeito.</p>
</div>
<div class="step">
  <h3>A cascata</h3>
  <p>Abaixo do primeiro fotão a mesma regra repete-se: a partir de cada nova energia, o fotão seguinte é sorteado de <i>T</i>(<i>E</i><sub>γ</sub>) ρ(<i>E<sub>x</sub></i> − <i>E</i><sub>γ</sub>), até o núcleo chegar aos seus níveis conhecidos. Cada história são uns poucos fotões; o seu espectro somado é o que um calorímetro vê depois da captura.</p>
  <div class="btns"><button class="btn ghost" data-act="up2" aria-pressed="true">Upbend</button><button class="btn ghost" data-act="clear">Recomeçar</button></div>
  <p>O upbend acrescenta fotões suaves e um pouco de multiplicidade. O motor não sorteia histórias: desloca populações intervalo a intervalo, de cima para baixo (Capítulo 11), o que dá as mesmas médias sem ruído de amostragem.</p>
  <div class="aside">No código: <code>gamma/strength.py</code> (todos os modelos de intensidade que o TALYS suporta; por defeito, as tabelas SMLO-2019 e a M1 da IAEA com upbend), <code>gamma/parameters.py</code> (sistemáticas das ressonâncias gigantes, tabelas), <code>gamma/transmission.py</code> (T = 2π E<sup>2L+1</sup> f), <code>gamma/ggnorm.py</code> (normalização opcional de ⟨Γγ⟩), <code>emission/</code> (a cascata). A imagem usa formas fechadas e sistemáticas para um núcleo semelhante ao ferro-57; o ⟨Γγ⟩ medido é o valor do RIPL para ⁵⁷Fe.</div>
</div>`,
};
(function () {
  const L = {
    "Eγ (MeV)": "Eγ (MeV)",
    "E{#} strength f (MeV⁻³), A = {#}": "intensidade E{#} f (MeV⁻³), A = {#}",
    "M{#} strength f (MeV⁻³), A = {#}": "intensidade M{#} f (MeV⁻³), A = {#}",
    "photons that decay uses": "fotões que o decaimento usa",
    "GDR: E₀ = {#} MeV, Γ₀ = {#} MeV, σ₀ = {#} mb": "GDR: E₀ = {#} MeV, Γ₀ = {#} MeV, σ₀ = {#} mb",
    "dashed: SLO": "tracejado: SLO",
    "at {#} MeV: SMLO / SLO = {#}": "a {#} MeV: SMLO / SLO = {#}",
    "protons against neutrons": "protões contra neutrões",
    "spin-flip": "inversão de spin",
    "scissors, β = {#}": "tesoura, β = {#}",
    "upbend": "upbend",
    "faint: E{#} at T = {#} MeV": "ténue: E{#} a T = {#} MeV",
    "M{#} > E{#} below {#} MeV": "M{#} > E{#} abaixo de {#} MeV",
    "E{#} dominates at every energy here": "aqui a E{#} domina a todas as energias",
    "scissors: the two deformed clouds rock": "tesoura: as duas nuvens deformadas oscilam",
    "from {#} MeV": "a partir de {#} MeV",
    "peak at Eγ ≈ {#} MeV": "máximo em Eγ ≈ {#} MeV",
    "primary spectrum T(Eγ) ρ(Eₓ − Eγ), each scaled to its peak": "espectro primário T(Eγ) ρ(Eₓ − Eγ), cada um escalado ao seu máximo",
    "contribution to ⟨Γγ⟩ per MeV of photon energy: E{#} (yellow), M{#} (purple, on top)": "contribuição para ⟨Γγ⟩ por MeV de energia do fotão: E{#} (amarelo), M{#} (roxo, por cima)",
    "{#} eV": "{#} eV",
    "measured {#} eV": "medido {#} eV",
    "computed ⟨Γγ⟩ = {#} meV (E{#} {#} %, M{#} {#} %)": "⟨Γγ⟩ calculado = {#} meV (E{#} {#} %, M{#} {#} %)",
    "Sₙ": "Sₙ",
    "all photons from all cascades": "todos os fotões de todas as cascatas",
    "{#} cascades · mean multiplicity {#}": "{#} cascatas · multiplicidade média {#}",
  };
  Object.assign(WT.L.labels, L);
})();
Object.assign(WT.L.glossary, {
  smlo: {
    term: "SMLO", aliases: ["SMLO"],
    short: "A lorentziana modificada simplificada: uma função de intensidade E1 cuja largura cresce com a energia do fotão e com a temperatura dos estados finais.",
    more: "Proposta por V. Plujko e colaboradores, e tabelada para todos os núcleos na base de dados de funções de intensidade fotónica da IAEA (2019). A E1 por defeito do motor, tal como a do TALYS-2, é essa tabela SMLO-2019.",
    chapter: "strength",
  },
  brinkAxel: {
    term: "Hipótese de Brink–Axel", aliases: ["hipótese de Brink–Axel", "hipótese de Brink-Axel", "Brink–Axel", "Brink-Axel"],
    short: "A suposição de que a função de intensidade fotónica depende apenas da energia do fotão e não da energia de excitação do estado que o emite.",
    more: "Permite que uma única intensidade, medida ou calculada para o estado fundamental, sirva para toda a cascata. Põe-se à prova extraindo intensidades a diferentes energias de excitação; verifica-se aproximadamente, com desvios debatidos para núcleos e energias particulares.",
    chapter: "strength",
  },
});
/* i18n_check.sh counts these attribute strings found in the English script code (not in html): data-act="up" data-act="up2" */
