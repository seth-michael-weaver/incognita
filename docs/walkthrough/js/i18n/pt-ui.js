/* Portuguese (pt-PT): static page text (index.html data-i18n keys) and kit UI strings */
Object.assign(WT.L.ui, {
  lang_label: "Língua", nav_teach: "Docentes",
  brand: "Dentro de uma reação nuclear", nav_physics: "A física", nav_data: "Todos os nuclídeos", nav_board: "Quadro de resultados", menu: "Menu", site_nav: "Sítio",
  ways_h: "Mais formas de entrar", ways_more: "Ou continua a descer: a física começa aqui ↓",
  way1_k: "Explora", way1_t: "Todos os nuclídeos", way1_p: "Secções eficazes previstas para 6168 nuclídeos ao lado de cada medição curada. Procura qualquer isótopo e vê todos os conjuntos de dados.", way1_go: "Abrir os dados →",
  way2_k: "Compara", way2_t: "Quadro de resultados", way2_p: "Como o motor e o seu produto de dados se comparam com outros códigos de reações e bibliotecas, avaliados face às medições, com as derrotas primeiro.", way2_go: "Ver os resultados →",
  way3_k: "Executa", way3_t: "O código", way3_p: "Tudo o que está aqui é aberto. Clona o repositório, consulta qualquer curva ou executa tu mesmo o motor.", way3_go: "GitHub →",
  title: "Dentro de uma reação nuclear",
  kicker: "Uma explicação interativa do motor de reações INCOGNITA",
  h1: "Dentro de uma reação nuclear",
  hero1: "Dispara um neutrão contra um núcleo atómico e algo volta a sair. Pode ser o próprio neutrão, que ressalta. Pode ser um protão, uma partícula alfa (um aglomerado compacto de 2 protões e 2 neutrões) ou um clarão de luz. Um núcleo pesado pode até partir-se em dois.",
  hero2: "Qual destas coisas acontece, e com que frequência? Esta página mostra, passo a passo, como o nosso software responde a essa pergunta. Desce a página e experimenta os controlos pelo caminho. As imagens seguem a mesma física que o motor; os números que mostram são ilustrativos.",
  scrollcue: "Desce para começar ↓",
  hero_tag: "Uma exploração visual da física nuclear",
  hero_aud: "Para estudantes e para quem está a começar em física nuclear, e para os docentes que os ensinam. Profissionais: os dados de cada nuclídeo estão em <a href=\"data.html\" data-keep-lang>Todos os nuclídeos</a>.",
  hero_fire: "Dispara um neutrão",
  hero_hint: "ou clica em qualquer parte da imagem",
  credit_idx: "O motor INCOGNITA é uma adaptação (port) do <a href=\"https://doi.org/10.1140/epja/s10050-023-01034-3\">TALYS-2</a> (A. J. Koning, S. Hilaire, S. Goriely) e usa a base de dados de estrutura nuclear do TALYS. O que o INCOGNITA acrescenta está <a href=\"#code\">listado, interruptor a interruptor, no fim desta página</a>.",
  coda_h2: "Onde isto vive no código",
  coda_p1: "Cada etapa acima é um pacote em <code>physics/hf</code>, e o motor chama-os pela ordem em que acabaste de os ler. O motor é uma adaptação do TALYS-2.x, o código de reações de referência. O que acrescenta está atrás de interruptores com nome dentro dos mesmos pacotes: a maioria está desligada por defeito, algumas correções estão ligadas, e cada uma pode ser revertida, por si só, para o TALYS original.",
  coda_table: `
    <thead><tr><th>Capítulo</th><th>O que faz</th><th>Código</th></tr></thead>
    <tbody>
      <tr><td><a href="#structure">1</a></td><td>Massas, níveis, deformação, dados de ressonâncias</td><td><code>structure/</code></td></tr>
      <tr><td><a href="#omp">5</a></td><td>Modelo ótico, coeficientes de transmissão (com que facilidade as partículas entram e saem)</td><td><code>omp/</code></td></tr>
      <tr><td><a href="#direct">6</a></td><td>Canais acoplados, DWBA, ressonâncias gigantes, captura direta (opcional)</td><td><code>ecis/</code>, <code>direct/</code></td></tr>
      <tr><td><a href="#preeq">7</a></td><td>Pré-equilíbrio: modelo de excitões, captura e arranque de nucleões, emissão múltipla</td><td><code>preeq/</code>, <code>density/particle_hole.py</code></td></tr>
      <tr><td><a href="#compound">8</a></td><td>Densidades de níveis (estados por MeV), distribuição de spin</td><td><code>density/</code></td></tr>
      <tr><td><a href="#decay">9</a></td><td>Escolher uma saída (Hauser–Feshbach), flutuações de larguras</td><td><code>compound/</code></td></tr>
      <tr><td><a href="#gamma">10</a></td><td>Função de intensidade gama e transmissão γ; níveis discretos e isómeros</td><td><code>gamma/</code><br><code>structure/levels.py</code></td></tr>
      <tr><td><a href="#cascade">11</a></td><td>A cascata de emissões de partículas e γ, canais exclusivos, residuais</td><td><code>emission/</code></td></tr>
      <tr><td><a href="#fission">12</a></td><td>Barreiras de fissão e transmissão</td><td><code>fission/</code></td></tr>
      <tr><td><a href="#measure">17</a></td><td>Espectros de emissão, distribuições angulares e secções eficazes duplamente diferenciais (opcional, só de saída)</td><td><code>specout.py</code><br><code>specang.py</code></td></tr>
      <tr><td><a href="#measure">17</a></td><td>Captura em alvos termicamente excitados e taxas estelares (opcional)</td><td><code>astro/stellar.py</code></td></tr>
      <tr><td><a href="#measure">17</a></td><td>Incerteza a partir de muitas variantes aleatórias (Monte Carlo total)</td><td><code>tmc.py</code></td></tr>
      <tr><td></td><td>O programa que executa as etapas por ordem, e núcleos de cálculo opcionais em C para ganhar velocidade</td><td><code>engine.py</code><br><code>engine_c.py</code>, <code>native/</code></td></tr>
      <tr><td></td><td>Todos os valores por defeito e opções, lidos uma vez no arranque; também os parâmetros ajustados por nuclídeo do TENDL, aplicados como o TALYS os aplica (opcional)</td><td><code>input/</code></td></tr>
    </tbody>
  `,
  coda_h3_added: "Acrescentado para além do TALYS",
  coda_p_added: "As linhas marcadas como <b>Ligado</b> funcionam por defeito, pelo que uma execução por defeito já não coincide exatamente com o TALYS; cada uma pode ser desligada com uma palavra-chave ou uma variável de ambiente. As restantes ficam desligadas, salvo se forem ativadas.",
  coda_table_added: `
    <thead><tr><th>Capítulo</th><th>O que muda</th><th>Código</th></tr></thead>
    <tbody>
      <tr><td><a href="#cascade">11</a></td><td><b>Ligado.</b> Contabilidade do fluxo fechada: residuais conservados até 10⁻⁹ mb (TALYS: 10⁻³ mb), residuais um passo além da janela de cascata do TALYS conservados, até 8 de cada partícula emitida nos canais exclusivos, todos os ramos de desexcitação repetidos de um nível contados</td><td><code>emission/fluxclose.py</code><br><code>emission/channels.py</code><br><code>kevleak2.py</code></td></tr>
      <tr><td><a href="#decay">9</a></td><td><b>Ligado.</b> O intervalo superior do primeiro núcleo composto é preenchido como os fotões primários o preenchem (com peso E<sub>γ</sub>³), e não de forma uniforme</td><td><code>compound/nnleak.py</code></td></tr>
      <tr><td><a href="#decay">9</a></td><td><b>Ligado.</b> Sem elástica composta média abaixo das primeiras ressonâncias (menos de 1 keV), onde a elástica é dispersão de potencial</td><td><code>lowepot.py</code></td></tr>
      <tr><td><a href="#decay">9</a></td><td><b>Ligado.</b> Alvos deformados sem fissão: as saídas de neutrões para níveis fora da banda acoplada usam a transmissão de canais acoplados</td><td><code>compound/ccexitnb.py</code></td></tr>
      <tr><td><a href="#omp">5</a></td><td><b>Ligado.</b> A emissão alfa vê um potencial que depende da temperatura do residual; os projéteis alfa entram com o modelo alfa 6; os potenciais de tritão e helião incluem o tamanho do projétil</td><td><code>omp/alphatemp.py</code><br><code>alphaentr.py</code><br><code>omp/tfold.py</code></td></tr>
      <tr><td><a href="#fission">12</a></td><td><b>Ligado.</b> Transmissão unidimensional exata através de cada bossa da barreira</td><td><code>fission/wkb.py</code></td></tr>
      <tr><td><a href="#gamma">10</a></td><td><b>Ligado.</b> Os fatores de intensidade E1/M1 por núcleo, quando uma execução os fornece, são substituídos por uma única função global da deformação</td><td><code>gamma/ftglobal.py</code></td></tr>
      <tr><td><a href="#compound">8</a></td><td><b>Ligado.</b> Alvos sem um espaçamento de ressonâncias D₀ medido próprio: a densidade de níveis do contínuo do alvo acima de max(E<sub>cut</sub> + 2, S<sub>n</sub> − 6) MeV é aumentada por um fator dado por uma única regra global de características de paridade, camadas e deformação. Acrescentado para transformar em empate a derrota em (n,p) perto do limiar face à entrada por omissão do TALYS-2; piora ligeiramente algumas vistas de captura, (n,2n) e (n,α), um dano aceite e registado</td><td><code>density/npwindow.py</code></td></tr>
      <tr><td><a href="#gamma">10</a></td><td>Um modo tesoura mais intenso em núcleos deformados, com sistemáticas mais recentes que coincidem com medições de Oslo (cerca de 4–5× nos actinídeos); ou uma variante que escala a sua energia e intensidade com a deformação</td><td><code>gamma/scissors.py</code></td></tr>
      <tr><td><a href="#gamma">10</a></td><td>Função de intensidade gama reescalada para que cada núcleo coincida com a sua intensidade radiativa medida ⟨Γγ⟩/D₀, em todos os núcleos da cascata, não só no primeiro</td><td><code>gamma/ggnorm.py</code></td></tr>
      <tr><td><a href="#gamma">10</a></td><td>Modo tesoura mais intenso e normalização de ⟨Γγ⟩ só para os núcleos mais pesados (Z ≥ 88), pensados para a captura a energias de keV</td><td><code>gamma/actphys.py</code></td></tr>
      <tr><td><a href="#gamma">10</a></td><td>A nossa própria constante de largura E1 em vez da tabela do TALYS derivada do TENDL (fixada pela receita sem dados que distribuímos)</td><td><code>gamma/e1_width.py</code></td></tr>
      <tr><td><a href="#gamma">10</a></td><td>Intensidade E2 coletiva das bandas rotacionais no quase-contínuo</td><td><code>gamma/isoe2.py</code></td></tr>
      <tr><td><a href="#omp">5</a></td><td>Um ajuste regional do poço ótico para alvos deformados de terras raras, ajustado a S₀ e S₁ medidos sem dados de captura</td><td><code>omp/regional.py</code></td></tr>
      <tr><td><a href="#omp">5</a></td><td>As funções de intensidade neutrónica medidas S₀, S₁ fixam a transmissão de neutrões a baixa energia</td><td><code>omp/sfunc.py</code></td></tr>
      <tr><td><a href="#direct">6</a></td><td>Captura direta em órbitas ligadas, com uma correção ao original: no TALYS padrão devolve zero, salvo se também forem pedidas todas as saídas do modelo ótico</td><td><code>direct/racapcalc.py</code></td></tr>
      <tr><td><a href="#direct">6</a></td><td>O esquema de acoplamento do alvo (rotor, vibrador, esférico) escolhido a partir dos seus níveis medidos</td><td><code>structure/collrule.py</code></td></tr>
      <tr><td><a href="#structure">1</a></td><td>O contínuo começa onde o esquema de níveis medido deixa de estar completo</td><td><code>structure/levcomplete.py</code></td></tr>
      <tr><td><a href="#structure">1</a></td><td>Um nível cujo spin listado é impossível para o seu núcleo (inteiro com A ímpar) é tratado como um nível de spin desconhecido</td><td><code>structure/levjpar.py</code></td></tr>
      <tr><td><a href="#compound">8</a></td><td>Densidade de níveis de temperatura constante ancorada na parte completa dos níveis discretos</td><td><code>density/ctwindow2.py</code></td></tr>
      <tr><td><a href="#fission">12</a></td><td>Bandas rotacionais de estados de transição nos pontos de sela da fissão</td><td><code>fission/barriers.py</code></td></tr>
      <tr><td><a href="#resonance">15</a></td><td>Captura onde só umas poucas ressonâncias caem na janela estelar: o valor típico de uma escada de ressonâncias em vez da média</td><td><code>fewres.py</code></td></tr>
      <tr><td></td><td>Quatro salvaguardas longe da estabilidade: fluxo direto limitado pela unitariedade, um limite para a energia de Fermi, sem coletividade por defeito em núcleos ímpar-ímpar, repartição de spin do pré-equilíbrio normalizada</td><td><code>engphys.py</code></td></tr>
    </tbody>
  `,
  coda_h3_outside: "Fora do motor",
  coda_p_outside: "Algumas partes da história funcionam ao lado do motor e não dentro dele. As escadas estatísticas de ressonâncias do <a href=\"#resonance\">capítulo 15</a> vivem em <code>physics/resonance/</code>. As médias maxwellianas (MACS) do <a href=\"#measure\">capítulo 17</a> são obtidas depois da execução a partir das curvas de captura do motor, em <code>validation/differential/core.py</code>; em contrapartida, a captura em alvos termicamente excitados e a taxa estelar vêm do próprio motor (<code>astro/stellar.py</code>, opcional). A camada de ancoragem do <a href=\"#layers\">capítulo 21</a> vive em <code>incognita/terra/</code>.",
  close: "Fechar",
  chapters: "Capítulos",
  nav_board: "Quadro de resultados", nav_data_short: "Dados",
  coda_repo: "O código, a biblioteca e as medições curadas são abertos: <a href=\"https://github.com/seth-michael-weaver/incognita\">seth-michael-weaver/incognita no GitHub</a>. Podes consultar qualquer previsão na página <a href=\"data.html?lang=pt\">Todos os nuclídeos</a>, ou clonar o repositório e executá-lo.",
  diagram: "Diagrama",
});

Object.assign(WT.L.ui, { pause_sweep: "Pausar o varrimento", play_sweep: "Retomar o varrimento" });

/* course mode: audience note, chapter level tags, per-step links */
Object.assign(WT.L.ui, {
  audience: '<b>Para quem é:</b> para qualquer pessoa curiosa. Os primeiros capítulos não exigem conhecimentos de física; os últimos chegam ao nível de investigação. Cada capítulo tem uma etiqueta: <span class="lvl l0">Introdutório</span>, <span class="lvl l1">Intermédio</span>, <span class="lvl l2">Avançado</span> ou <span class="lvl l3">Especialista</span>. Queres usá-lo nas aulas? Consulta o <a href="instructors.html" data-keep-lang>guia para docentes</a>.',
  lvl0: "Introdutório", lvl1: "Intermédio", lvl2: "Avançado", lvl3: "Especialista", lvl_title: "Nível",
  xp_kicker: "Segunda parte · Especialista", xp_h: "A fundo",
  xp_p: "Até aqui, os capítulos contaram cada etapa como uma imagem. Os seis que se seguem abrem essas mesmas etapas: as fórmulas que o motor avalia, as aproximações que contêm e os pontos onde cedem. Foram escritos para avaliadores, autores de modelos e estudantes de pós-graduação. Os desenhos avaliam as fórmulas em tempo real, com dados de entrada ilustrativos.",
  step_link: "Copiar uma ligação para este passo", link_copied: "Ligação copiada",
});
