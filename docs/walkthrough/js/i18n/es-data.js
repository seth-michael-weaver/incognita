/* Spanish: data explorer (data.html, js/data.js) */
Object.assign(WT.es.ui, {
  lang_label: "Idioma", nav_teach: "Docentes",
  brand: "Dentro de una reacción nuclear", nav_physics: "La física", nav_data: "Todos los núclidos", nav_board: "Marcador", menu: "Menú", site_nav: "Sitio",
  dx_title: "Todos los núclidos · Dentro de una reacción nuclear",
  site_nav: "Sitio", nav_walk: "El recorrido", nav_board: "Marcador", nav_data: "Todos los núclidos", nav_repo: "Código en GitHub",
  dx_kicker: "INCOGNITA · explorador de datos",
  dx_h1: "Todos los núclidos",
  dx_lede: "Las secciones eficaces neutrónicas que predice el motor para cada núclido de la biblioteca, junto a las medidas depuradas de cada núclido. Elige un núclido en la carta o búscalo.",
  dx_lede_ver: "Las curvas son la biblioteca v0.2 (octubre de 2026), hecha con la misma versión del motor que se evalúa en el Marcador (el motor del 22 de octubre de 2026). No son TERRA, el producto de datos del Marcador que se ajusta a las medidas. Cada curva es la predicción del propio motor: ninguna se ajustó a las medidas que se muestran a su lado, salvo que un núclido marcado como anclado tiene su curva multiplicada por un único factor para que su promedio estelar a 30 keV coincida con el valor medido. Los ajustes generales del motor se eligieron una sola vez, para todos los núclidos, con muchas medidas (entre ellas estas), así que la coincidencia en un núclido medido es una prueba justa del modelo, aunque no del todo independiente. La mayoría de los núclidos nunca se han medido (son los extrapolados), y sus bandas son anchas.",
  dx_controls: "Controles de la carta", dx_search_label: "Buscar un núclido", dx_search_ph: "Buscar: U-235, Fe56, Au…",
  dx_colour: "Colorear la carta por", dx_m_tier: "Cómo se conoce", dx_m_macs: "Captura a 30 keV", dx_m_meas: "Datos medidos",
  dx_chart_h: "Carta de núclidos",
  dx_chart_aria: "Carta de núclidos: protones hacia arriba, neutrones hacia la derecha. Usa la búsqueda para elegir un núclido.",
  dx_hint: "Arrastra para mover, usa la rueda o pellizca para ampliar. Haz clic en un cuadro para abrirlo: los detalles del núclido aparecen debajo de la carta. Protones hacia arriba, neutrones hacia la derecha.",
  dx_full: "Mostrar todo el rango de energía", dx_mk_thr: "umbral", dx_mk_cb: "barrera de Coulomb",
  dx_show_excl: "Mostrar los puntos que la depuración excluyó", dx_table: "Ver como tabla",
  dx_run_h: "Obtén estos números tú mismo", dx_copy: "Copiar", dx_copied: "Copiado",
  dx_repo_h: "Ejecútalo tú mismo",
  dx_repo_p: "Todo lo que hay en esta página sale del repositorio abierto: el motor, la biblioteca y las medidas depuradas. Necesitas Linux o macOS, Python 3.12 y <a href=\"https://docs.astral.sh/uv/\">uv</a>.",
  credit_sub: "El motor INCOGNITA es un port de <a href=\"https://doi.org/10.1140/epja/s10050-023-01034-3\">TALYS-2</a> (A. J. Koning, S. Hilaire, S. Goriely) y usa la base de datos de estructura nuclear de TALYS. Lo que INCOGNITA añade está <a href=\"./?lang=es#code\">listado, interruptor por interruptor, al final de la página didáctica</a>.",
  dx_repo_p2: "Para ejecutar el propio motor hace falta además la base de datos de estructura de TALYS; el README explica cómo descargarla.",
  dx_repo_link: "seth-michael-weaver/incognita en GitHub →",
  dx_src: "Fuentes: predicciones de la biblioteca v0.2 (<code>library/v0.2</code>); medidas de captura de EXFOR depuradas en <code>data/curation</code>; medidas de (n,2n), (n,p) y (n,α) de las filas de referencia en <code>incognita/bench</code>. Las medidas que la depuración excluyó quedan ocultas salvo que las pidas. La superposición opcional (líneas discontinuas) de bibliotecas evaluadas (ENDF/B-VIII.1, JEFF-4.0, TENDL-2025) la genera <code>scripts/build_site_overlay.py</code> solo para mostrarla; INCOGNITA nunca la lee.",
  dx_t0: "Medido", dx_t1: "Anclado a una MACS medida", dx_t2: "Interpolado (cerca de núclidos medidos)", dx_t3: "Extrapolado",
  dx_ts0: "medido", dx_ts1: "anclado", dx_ts2: "interpolado", dx_ts3: "extrapolado",
  dx_keep: "conservado", dx_down: "con menos peso", dx_excl: "excluido", dx_fix: "unidad corregida",
  dx_cap: "Captura (n,γ)", dx_macs: "Promedio estelar (MACS)", dx_nat: "natural",
  dx_l_cap: "captura medida", dx_l_thr: "solo (n,2n), (n,p) o (n,α) medidos", dx_l_none: "sin medidas en este conjunto",
  dx_l_macs: "captura promediada sobre Maxwell predicha a kT = 30 keV (escala logarítmica)", dx_l_nomacs: "sin valor",
  dx_capsets: "conjuntos de datos de captura", dx_measured: "Medido",
  dx_outside: "fuera del rango validado (Z 26–83)", dx_flag: "las resonancias resueltas llegan a la ventana de la MACS: mejor usar una MACS medida",
  dx_nocurve: "sin curva de biblioteca para esta entrada; las medidas vienen de",
  dx_xE: "energía del neutrón", dx_pred: "predicción (biblioteca v0.2)",
  dx_res: "resonancias resueltas: aquí la curva es un promedio",
  dx_empty: "No hay nada que mostrar para esta reacción.", dx_bands: "bandas: 68 % y 95 %", dx_band68: "banda: 68 %",
  dx_meas_pts: "medidos", dx_table_hint: "Usa «Ver como tabla» para los valores.", dx_ds_h: "Medidas", dx_pts: "pts",
  dx_th_src: "Fuente", dx_th_val: "Valor", dx_th_unc: "Rango / incertidumbre", dx_th_cur: "Depuración",
  dx_s_p: "protones", dx_s_n: "neutrones", dx_s_macs: "captura en una estrella a 30 keV", dx_s_pts: "puntos de captura medidos", dx_s_thr: "puntos de (n,2n), (n,p), (n,α)", dx_sets: "conjuntos",
  dx_exfor_click: "haz clic en el punto para abrir", dx_exfor_tap: "toca otra vez, o aquí, para abrir",
  dx_mxw: "promedio de Maxwell", dx_state: "estado", dx_cur: "depuración", dx_fail: "No se pudieron cargar los datos.", dx_loading: "Cargando", dx_nload: "No se pudo cargar este núclido.", dx_retry: "Reintentar",
});

/* downloads and data access */
Object.assign(WT.es.ui, {
  dx_dl: "Descargar este núclido:",
  dx_dl_note: "Cada curva y cada punto medido de este núclido, todas las reacciones, con unidades, fuentes e identificadores EXFOR escritos en el archivo.",
  dx_access: "<b>Acceso a los datos.</b> Todo lo que se muestra aquí está en el repositorio, en <a href=\"https://github.com/seth-michael-weaver/incognita/tree/main/library/v0.2\"><code>library/v0.2</code></a>: curvas de captura con bandas del 68 / 95 % (<code>capture_v02.parquet</code>), promedios de Maxwell (<code>macs30_v02.csv</code>, <code>macs_kt_v02.csv</code>), tasas estelares (<code>rates_v02.csv</code>, <code>reaclib_v02.dat</code>) y los canales (n,2n), (n,p), (n,α) (<code>channels_v02.parquet</code>, <code>grid_np_v02.parquet</code>), comprobados con <code>SHA256SUMS</code>. Para un solo núclido bastan las descargas CSV y JSON de arriba. Las medidas depuradas están en <code>data/curation</code>; proceden de EXFOR (Sección de Datos Nucleares del OIEA) y conservan sus identificadores EXFOR. Los datos de la biblioteca son CC-BY-4.0. La versión anterior, v0.1, sigue en <code>library/v0.1</code>; el archivo <code>CHANGELOG.md</code> de <code>library/v0.2</code> explica qué cambió.",
});
Object.assign(WT.es.ui, {
  dx_lib: "Superponer bibliotecas evaluadas (solo para comparar — INCOGNITA no las usa)",
  dx_eval: "evaluación", dx_lib_pd: "dominio público (EE. UU.)", dx_lib_loading: "Cargando las bibliotecas…",
  dx_lib_bin: "bibliotecas: promedios por intervalo",
  dx_lib_note: "Las líneas discontinuas son bibliotecas evaluadas de datos nucleares, mostradas solo para comparar: INCOGNITA no las usa y no están en las descargas. Cada una se reconstruye a 0 K a partir del archivo ENDF-6 de la biblioteca (NJOY) y se promedia sobre los mismos intervalos de energía que la curva (promedios en el logaritmo de la energía, así que las resonancias quedan suavizadas); la MACS usa la curva puntual completa.",
  dx_lib_none: "No hay archivo para este núclido en", dx_lib_notab: "No hay un valor separado para esta reacción en",
  dx_lib_held: "JENDL-5 se añadirá cuando se confirmen sus condiciones para redistribuir tablas derivadas.",
});

/* library v0.2: a nuclide whose capture below 1 MeV hinges on one engine setting ({n}: the factor at 30 keV) */
Object.assign(WT.L.ui, {
  dx_mf_pe_lo: "Elección de modelo incierta: este motor deja que una partícula escape antes de que el núcleo alcance el equilibrio (emisión de preequilibrio) a todas las energías, mientras que TALYS solo lo hace por encima de 1 MeV aproximadamente; la elección de TALYS da unas {n} veces menos captura a 30 keV, y la banda del 95 % por debajo de 1 MeV cubre ambas.",
  dx_mf_pe_hi: "Elección de modelo incierta: este motor deja que una partícula escape antes de que el núcleo alcance el equilibrio (emisión de preequilibrio) a todas las energías, mientras que TALYS solo lo hace por encima de 1 MeV aproximadamente; la elección de TALYS da unas {n} veces más captura a 30 keV, y la banda del 95 % por debajo de 1 MeV cubre ambas.",
  dx_mf_pe_near: "Elección de modelo incierta: este motor deja que una partícula escape antes de que el núcleo alcance el equilibrio (emisión de preequilibrio) a todas las energías, mientras que TALYS solo lo hace por encima de 1 MeV aproximadamente; la elección de TALYS coincide con esta curva a 30 keV, pero difiere en más de un factor 2 en otras energías por debajo de 1 MeV, y allí la banda del 95 % cubre ambas.",
  dx_mf_fi_lo: "Elección de modelo incierta: por debajo de 1 MeV esta curva depende de un ajuste del motor sobre cómo el núcleo atraviesa sus barreras de fisión; la otra elección da unas {n} veces menos captura a 30 keV, y la banda del 95 % por debajo de 1 MeV cubre ambas.",
  dx_mf_fi_hi: "Elección de modelo incierta: por debajo de 1 MeV esta curva depende de un ajuste del motor sobre cómo el núcleo atraviesa sus barreras de fisión; la otra elección da unas {n} veces más captura a 30 keV, y la banda del 95 % por debajo de 1 MeV cubre ambas.",
  dx_mf_fi_near: "Elección de modelo incierta: por debajo de 1 MeV esta curva depende de un ajuste del motor sobre cómo el núcleo atraviesa sus barreras de fisión; la otra elección coincide con esta curva a 30 keV, pero difiere en más de un factor 2 en otras energías por debajo de 1 MeV, y allí la banda del 95 % cubre ambas.",
  dx_mf_gg_lo: "Esta curva usa una corrección de la desexcitación gamma del núcleo que TALYS y TENDL no aplican; sin ella, la captura a 30 keV sería unas {n} veces menor.",
  dx_mf_gg_hi: "Esta curva usa una corrección de la desexcitación gamma del núcleo que TALYS y TENDL no aplican; sin ella, la captura a 30 keV sería unas {n} veces mayor.",
  dx_mf_gg_near: "Esta curva usa una corrección de la desexcitación gamma del núcleo que TALYS y TENDL no aplican; sin ella, la captura a 30 keV sería más o menos la misma.",
});

/* pointwise library comparators below 1 keV and the measured thermal value (KONINGOVERLAY) */
Object.assign(WT.L.ui, {
  dx_eval_cmp: "biblioteca evaluada · comparador, no INCOGNITA",
  dx_pw_leg2: "línea continua por debajo de 1 keV: puntual, 0 K",
  dx_lib_pw_dense: "Este nucleido tiene muchas resonancias por debajo de 1 keV, así que conserva más puntos: cinco por pico de resonancia, hasta 5000 (con un presupuesto fijo de 500 se cortarían muchos picos de U-235 o Pu-239).",
  dx_pw_short: "puntual a 0 K, por debajo de 1 keV",
  dx_lib_pw: "Por debajo de 1 keV las mismas bibliotecas se dibujan punto a punto, con líneas finas continuas: reconstruidas a 0 K (NJOY RECONR, tolerancia del 0,01 %) y reducidas a un máximo de {n} puntos por curva, elegidos para conservar los picos y los valles de las resonancias. También son comparadores: INCOGNITA no tiene curva por debajo de 1 keV.",
  dx_below_cv: "por debajo de 1 keV: no hay curva de INCOGNITA, solo bibliotecas evaluadas y mediciones",
  dx_below: "La curva propia de INCOGNITA empieza en 1 keV; por debajo solo se muestran comparadores y mediciones.",
  dx_pw_tip: "bibliotecas evaluadas (comparadores), puntuales a 0 K; sin curva de INCOGNITA por debajo de 1 keV",
  dx_th: "valor térmico medido (EXFOR)",
  dx_th_sent: "Rombo: sección eficaz de captura térmica medida σγ(0,0253 eV)",
  dx_th_mean: "media ponderada de {n} entradas de EXFOR",
  dx_th_abs: "absorción menos fisión",
});
