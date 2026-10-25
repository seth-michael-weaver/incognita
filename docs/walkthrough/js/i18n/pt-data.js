/* Portuguese (pt-PT): data explorer (data.html, js/data.js) */
Object.assign(WT.L.ui, {
  lang_label: "Língua", nav_teach: "Docentes",
  brand: "Dentro de uma reação nuclear", nav_physics: "A física", nav_data: "Todos os nuclídeos", nav_board: "Quadro de resultados", menu: "Menu", site_nav: "Sítio",
  dx_title: "Todos os nuclídeos · Dentro de uma reação nuclear",
  site_nav: "Sítio", nav_walk: "O percurso", nav_board: "Quadro de resultados", nav_data: "Todos os nuclídeos", nav_repo: "Código no GitHub",
  dx_kicker: "INCOGNITA · explorador de dados",
  dx_h1: "Todos os nuclídeos",
  dx_lede: "As secções eficazes de neutrões que o motor prevê para cada nuclídeo da biblioteca, ao lado das medições curadas de cada nuclídeo. Escolhe um nuclídeo na carta ou procura-o.",
  dx_lede_ver: "As curvas são a biblioteca v0.2 (outubro de 2026), feita com a mesma versão do motor que o Quadro de resultados pontua (o motor de 22 de outubro de 2026). Não são o TERRA, o produto de dados do Quadro de resultados que é ajustado às medições. Cada curva é a previsão do próprio motor: nenhuma foi ajustada às medições mostradas ao lado, exceto num nuclídeo marcado como ancorado, cuja curva é multiplicada por um único fator para que a sua média estelar a 30 keV iguale o valor medido. As definições gerais do motor foram escolhidas uma só vez, para todos os nuclídeos, com muitas medições (incluindo estas), por isso a concordância num nuclídeo medido é uma verificação justa do modelo, embora não totalmente independente. A maioria dos nuclídeos nunca foi medida (extrapolados), e as suas bandas são largas.",
  dx_controls: "Controlos da carta", dx_search_label: "Procurar um nuclídeo", dx_search_ph: "Procurar: U-235, Fe56, Au…",
  dx_colour: "Colorir a carta por", dx_m_tier: "Como é conhecido", dx_m_macs: "Captura a 30 keV", dx_m_meas: "Dados medidos",
  dx_chart_h: "Carta de nuclídeos",
  dx_chart_aria: "Carta de nuclídeos: protões para cima, neutrões para a direita. Usa a pesquisa para escolher um nuclídeo.",
  dx_hint: "Arrasta para mover, usa a roda ou faz pinça para ampliar. Clica num quadrado para o abrir: os detalhes do nuclídeo aparecem por baixo da carta. Protões para cima, neutrões para a direita.",
  dx_full: "Mostrar toda a gama de energia", dx_mk_thr: "limiar", dx_mk_cb: "barreira de Coulomb",
  dx_show_excl: "Mostrar os pontos que a curadoria excluiu", dx_table: "Ver como tabela",
  dx_run_h: "Obtém tu mesmo estes números", dx_copy: "Copiar", dx_copied: "Copiado",
  dx_repo_h: "Executa-o tu mesmo",
  dx_repo_p: "Tudo o que está nesta página vem do repositório aberto: o motor, a biblioteca e as medições curadas. Precisas de Linux ou macOS, Python 3.12 e <a href=\"https://docs.astral.sh/uv/\">uv</a>.",
  credit_sub: "O motor INCOGNITA é uma adaptação (port) do <a href=\"https://doi.org/10.1140/epja/s10050-023-01034-3\">TALYS-2</a> (A. J. Koning, S. Hilaire, S. Goriely) e usa a base de dados de estrutura nuclear do TALYS. O que o INCOGNITA acrescenta está <a href=\"./?lang=pt#code\">listado, interruptor a interruptor, no fim da página didática</a>.",
  dx_repo_p2: "Para executar o próprio motor é ainda preciso a base de dados de estrutura do TALYS; o README explica como descarregá-la.",
  dx_repo_link: "seth-michael-weaver/incognita no GitHub →",
  dx_src: "Fontes: previsões da biblioteca v0.2 (<code>library/v0.2</code>); medições de captura do EXFOR curadas em <code>data/curation</code>; medições de (n,2n), (n,p) e (n,α) das linhas de referência em <code>incognita/bench</code>. As medições que a curadoria excluiu ficam ocultas, salvo se as pedires. A sobreposição opcional (linhas tracejadas) de bibliotecas avaliadas (ENDF/B-VIII.1, JEFF-4.0, TENDL-2025) é gerada por <code>scripts/build_site_overlay.py</code> apenas para ser mostrada; o INCOGNITA nunca a lê.",
  dx_t0: "Medido", dx_t1: "Ancorado a uma MACS medida", dx_t2: "Interpolado (perto de nuclídeos medidos)", dx_t3: "Extrapolado",
  dx_ts0: "medido", dx_ts1: "ancorado", dx_ts2: "interpolado", dx_ts3: "extrapolado",
  dx_keep: "mantido", dx_down: "com menos peso", dx_excl: "excluído", dx_fix: "unidade corrigida",
  dx_cap: "Captura (n,γ)", dx_macs: "Média estelar (MACS)", dx_nat: "natural",
  dx_l_cap: "captura medida", dx_l_thr: "só (n,2n), (n,p) ou (n,α) medidos", dx_l_none: "sem medições neste conjunto",
  dx_l_macs: "captura média maxwelliana prevista a kT = 30 keV (escala logarítmica)", dx_l_nomacs: "sem valor",
  dx_capsets: "conjuntos de dados de captura", dx_measured: "Medido",
  dx_outside: "fora do intervalo validado (Z 26–83)", dx_flag: "as ressonâncias resolvidas chegam à janela da MACS: é melhor usar uma MACS medida",
  dx_nocurve: "sem curva de biblioteca para esta entrada; as medições vêm de",
  dx_xE: "energia do neutrão", dx_pred: "previsão (biblioteca v0.2)",
  dx_res: "ressonâncias resolvidas: aqui a curva é uma média",
  dx_empty: "Não há nada para mostrar para esta reação.", dx_bands: "bandas: 68 % e 95 %", dx_band68: "banda: 68 %",
  dx_meas_pts: "medidos", dx_table_hint: "Usa «Ver como tabela» para os valores.", dx_ds_h: "Medições", dx_pts: "pts",
  dx_th_src: "Fonte", dx_th_val: "Valor", dx_th_unc: "Intervalo / incerteza", dx_th_cur: "Curadoria",
  dx_s_p: "protões", dx_s_n: "neutrões", dx_s_macs: "captura numa estrela a 30 keV", dx_s_pts: "pontos de captura medidos", dx_s_thr: "pontos de (n,2n), (n,p), (n,α)", dx_sets: "conjuntos",
  dx_exfor_click: "clica no ponto para abrir", dx_exfor_tap: "toca outra vez, ou aqui, para abrir",
  dx_mxw: "média maxwelliana", dx_state: "estado", dx_cur: "curadoria", dx_fail: "Não foi possível carregar os dados.", dx_loading: "A carregar", dx_nload: "Não foi possível carregar este nuclídeo.", dx_retry: "Tentar de novo",
});

/* downloads and data access */
Object.assign(WT.L.ui, {
  dx_dl: "Descarregar este nuclídeo:",
  dx_dl_note: "Todas as curvas e todos os pontos medidos deste nuclídeo, todas as reações, com unidades, fontes e identificadores EXFOR escritos no ficheiro.",
  dx_access: "<b>Acesso aos dados.</b> Tudo o que aqui se mostra está no repositório, em <a href=\"https://github.com/seth-michael-weaver/incognita/tree/main/library/v0.2\"><code>library/v0.2</code></a>: curvas de captura com bandas de 68 / 95 % (<code>capture_v02.parquet</code>), médias maxwellianas (<code>macs30_v02.csv</code>, <code>macs_kt_v02.csv</code>), taxas estelares (<code>rates_v02.csv</code>, <code>reaclib_v02.dat</code>) e os canais (n,2n), (n,p), (n,α) (<code>channels_v02.parquet</code>, <code>grid_np_v02.parquet</code>), verificados com <code>SHA256SUMS</code>. Para um só nuclídeo, bastam as transferências CSV e JSON acima. As medições curadas estão em <code>data/curation</code>; provêm do EXFOR (Secção de Dados Nucleares da AIEA) e mantêm os seus identificadores EXFOR. Os dados da biblioteca são CC-BY-4.0. A versão anterior, v0.1, continua em <code>library/v0.1</code>; o ficheiro <code>CHANGELOG.md</code> em <code>library/v0.2</code> explica o que mudou.",
});
Object.assign(WT.L.ui, {
  dx_lib: "Sobrepor bibliotecas avaliadas (só para comparar — o INCOGNITA não as usa)",
  dx_eval: "avaliação", dx_lib_pd: "domínio público (EUA)", dx_lib_loading: "A carregar as bibliotecas…",
  dx_lib_bin: "bibliotecas: médias por intervalo",
  dx_lib_note: "As linhas tracejadas são bibliotecas avaliadas de dados nucleares, mostradas apenas para comparação: o INCOGNITA não as usa e não estão nas transferências. Cada uma é reconstruída a 0 K a partir do ficheiro ENDF-6 da biblioteca (NJOY) e calculada em média sobre os mesmos intervalos de energia que a curva (médias no logaritmo da energia, pelo que as ressonâncias ficam suavizadas); a MACS usa a curva pontual completa.",
  dx_lib_none: "Não há ficheiro para este nuclídeo em", dx_lib_notab: "Não há um valor separado para esta reação em",
  dx_lib_held: "O JENDL-5 será acrescentado quando forem confirmadas as suas condições para redistribuir tabelas derivadas.",
});

/* library v0.2: a nuclide whose capture below 1 MeV hinges on one engine setting ({n}: the factor at 30 keV) */
Object.assign(WT.L.ui, {
  dx_mf_pe_lo: "Escolha de modelo incerta: este motor deixa uma partícula escapar antes de o núcleo estabilizar (emissão de pré-equilíbrio) a todas as energias, enquanto o TALYS só o faz acima de cerca de 1 MeV; a escolha do TALYS dá cerca de {n} vezes menos captura a 30 keV, e a banda de 95 % abaixo de 1 MeV cobre ambas.",
  dx_mf_pe_hi: "Escolha de modelo incerta: este motor deixa uma partícula escapar antes de o núcleo estabilizar (emissão de pré-equilíbrio) a todas as energias, enquanto o TALYS só o faz acima de cerca de 1 MeV; a escolha do TALYS dá cerca de {n} vezes mais captura a 30 keV, e a banda de 95 % abaixo de 1 MeV cobre ambas.",
  dx_mf_pe_near: "Escolha de modelo incerta: este motor deixa uma partícula escapar antes de o núcleo estabilizar (emissão de pré-equilíbrio) a todas as energias, enquanto o TALYS só o faz acima de cerca de 1 MeV; a escolha do TALYS concorda a 30 keV, mas difere mais de um fator 2 noutras energias abaixo de 1 MeV, e aí a banda de 95 % cobre ambas.",
  dx_mf_fi_lo: "Escolha de modelo incerta: abaixo de 1 MeV esta curva depende de uma definição do motor sobre a forma como o núcleo atravessa as suas barreiras de fissão; a outra escolha dá cerca de {n} vezes menos captura a 30 keV, e a banda de 95 % abaixo de 1 MeV cobre ambas.",
  dx_mf_fi_hi: "Escolha de modelo incerta: abaixo de 1 MeV esta curva depende de uma definição do motor sobre a forma como o núcleo atravessa as suas barreiras de fissão; a outra escolha dá cerca de {n} vezes mais captura a 30 keV, e a banda de 95 % abaixo de 1 MeV cobre ambas.",
  dx_mf_fi_near: "Escolha de modelo incerta: abaixo de 1 MeV esta curva depende de uma definição do motor sobre a forma como o núcleo atravessa as suas barreiras de fissão; a outra escolha concorda a 30 keV, mas difere mais de um fator 2 noutras energias abaixo de 1 MeV, e aí a banda de 95 % cobre ambas.",
  dx_mf_gg_lo: "Esta curva usa uma correção do decaimento gama do núcleo que o TALYS e o TENDL não aplicam; sem ela, a captura a 30 keV seria cerca de {n} vezes menor.",
  dx_mf_gg_hi: "Esta curva usa uma correção do decaimento gama do núcleo que o TALYS e o TENDL não aplicam; sem ela, a captura a 30 keV seria cerca de {n} vezes maior.",
  dx_mf_gg_near: "Esta curva usa uma correção do decaimento gama do núcleo que o TALYS e o TENDL não aplicam; sem ela, a captura a 30 keV seria aproximadamente a mesma.",
});

/* pointwise library comparators below 1 keV and the measured thermal value (KONINGOVERLAY) */
Object.assign(WT.L.ui, {
  dx_eval_cmp: "biblioteca avaliada · comparação, não INCOGNITA",
  dx_pw_leg2: "linha contínua abaixo de 1 keV: pontual, 0 K",
  dx_lib_pw_dense: "Este nuclídeo tem muitas ressonâncias abaixo de 1 keV, por isso guarda mais pontos: cinco por pico de ressonância, até 5000 (com um orçamento fixo de 500, muitos picos do U-235 ou do Pu-239 seriam cortados).",
  dx_pw_short: "pontual a 0 K, abaixo de 1 keV",
  dx_lib_pw: "Abaixo de 1 keV as mesmas bibliotecas são desenhadas ponto a ponto, em linhas finas contínuas: reconstruídas a 0 K (NJOY RECONR, tolerância de 0,01 %) e reduzidas a no máximo {n} pontos por curva, escolhidos para manter os picos e os vales das ressonâncias. Também são só para comparação: a INCOGNITA não tem curva abaixo de 1 keV.",
  dx_below_cv: "abaixo de 1 keV: sem curva da INCOGNITA, só bibliotecas avaliadas e medições",
  dx_below: "A curva própria da INCOGNITA começa em 1 keV; abaixo disso só aparecem comparações e medições.",
  dx_pw_tip: "bibliotecas avaliadas (comparação), pontuais a 0 K; sem curva da INCOGNITA abaixo de 1 keV",
  dx_th: "valor térmico medido (EXFOR)",
  dx_th_sent: "Losango: seção de choque de captura térmica medida σγ(0,0253 eV)",
  dx_th_mean: "média ponderada de {n} entradas do EXFOR",
  dx_th_abs: "absorção menos fissão",
});
