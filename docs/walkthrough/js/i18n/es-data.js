/* Spanish: data explorer (data.html, js/data.js) */
Object.assign(WT.es.ui, {
  lang_label: "Idioma", nav_teach: "Docentes",
  brand: "Dentro de una reacción nuclear", nav_physics: "La física", nav_data: "Todos los núclidos", nav_board: "Comparaciones", menu: "Menú", site_nav: "Sitio",
  dx_title: "Todos los núclidos · Dentro de una reacción nuclear",
  site_nav: "Sitio", nav_walk: "El recorrido", nav_board: "Comparaciones", nav_data: "Todos los núclidos", nav_repo: "Código en GitHub",
  dx_kicker: "INCOGNITA · explorador de datos",
  dx_h1: "Todos los núclidos",
  dx_lede: "Las secciones eficaces neutrónicas que predice el motor para cada núclido de la biblioteca, junto a las medidas depuradas de cada núclido. Elige un núclido en la carta o búscalo.",
  dx_lede_ver: "Las curvas son la biblioteca v0.2.3 (noviembre de 2026), hecha con la misma versión del motor que se evalúa en la página Comparaciones (el motor del 22 de octubre de 2026). No son TERRA, el producto de datos de esa página que se ajusta a las medidas. Cada curva es la predicción del propio motor: ninguna se ajustó a las medidas que se muestran a su lado, salvo que un núclido marcado como anclado tiene su curva multiplicada por un único factor para que su promedio estelar a 30 keV coincida con el valor medido. Los ajustes generales del motor se eligieron una sola vez, para todos los núclidos, con muchas medidas (entre ellas estas), así que la coincidencia en un núclido medido es una prueba justa del modelo, aunque no del todo independiente. La mayoría de los núclidos nunca se han medido (son los extrapolados), y sus bandas son anchas.",
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
  dx_src: "Fuentes: predicciones de la biblioteca v0.2.3 (<code>library/v0.2.3</code>); medidas de captura de EXFOR depuradas en <code>data/curation</code>; medidas de (n,2n), (n,p) y (n,α) de las filas de referencia en <code>incognita/bench</code> (por debajo de Z 26: filas de EXFOR elegidas con las mismas reglas, <code>data/curation/inputs</code>). Las medidas que la depuración excluyó quedan ocultas salvo que las pidas. La superposición opcional (líneas discontinuas) de bibliotecas evaluadas (ENDF/B-VIII.1, JEFF-4.0, TENDL-2025) la genera <code>scripts/build_site_overlay.py</code> solo para mostrarla; INCOGNITA nunca la lee.",
  dx_t0: "Medido", dx_t1: "Anclado a una MACS medida", dx_t2: "Interpolado (cerca de núclidos medidos)", dx_t3: "Extrapolado",
  dx_ts0: "medido", dx_ts1: "anclado", dx_ts2: "interpolado", dx_ts3: "extrapolado",
  dx_keep: "conservado", dx_down: "con menos peso", dx_excl: "excluido", dx_fix: "unidad corregida",
  dx_cap: "Captura (n,γ)", dx_macs: "Promedio estelar (MACS)", dx_nat: "natural",
  dx_l_cap: "captura medida", dx_l_thr: "solo (n,2n), (n,p) o (n,α) medidos", dx_l_none: "sin medidas en este conjunto",
  dx_l_macs: "captura promediada sobre Maxwell predicha a kT = 30 keV (escala logarítmica)", dx_l_nomacs: "sin valor",
  dx_capsets: "conjuntos de datos de captura", dx_measured: "Medido",
  dx_outside: "fuera del rango validado (Z 26–83)", dx_flag: "las resonancias resueltas llegan a la ventana de la MACS: mejor usar una MACS medida",
  dx_nocurve: "sin curva de biblioteca para esta entrada; las medidas vienen de",
  dx_xE: "energía del neutrón", dx_pred: "predicción (biblioteca v0.2.3)",
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
  dx_access: "<b>Acceso a los datos.</b> Todo lo que se muestra aquí está en el repositorio, en <a href=\"https://github.com/seth-michael-weaver/incognita/tree/main/library/v0.2.3\"><code>library/v0.2.3</code></a>: curvas de captura con bandas del 68 / 95 % (<code>capture_v023.parquet</code>), promedios de Maxwell (<code>macs30_v023.csv</code>, <code>macs_kt_v023.csv</code>), tasas estelares (<code>rates_v023.csv</code>, <code>reaclib_v023.dat</code>) y los canales (n,2n), (n,p), (n,α) (<code>channels_v023.parquet</code>, <code>grid_np_v023.parquet</code>), comprobados con <code>SHA256SUMS</code>. Para un solo núclido bastan las descargas CSV y JSON de arriba. Las medidas depuradas están en <code>data/curation</code>; proceden de EXFOR (Sección de Datos Nucleares del OIEA) y conservan sus identificadores EXFOR. Los datos de la biblioteca son CC-BY-4.0. La versión anterior, v0.1, sigue en <code>library/v0.1</code>; el archivo <code>CHANGELOG.md</code> de <code>library/v0.2.3</code> explica qué cambió.",
});
Object.assign(WT.es.ui, {
  dx_lib: "Superponer bibliotecas evaluadas (solo para comparar — INCOGNITA no las usa)",
  dx_eval: "evaluación", dx_lib_pd: "dominio público (EE. UU.)", dx_lib_loading: "Cargando las bibliotecas…",
  dx_lib_bin: "bibliotecas: promedios por intervalo",
  dx_lib_note: "Las líneas discontinuas son bibliotecas evaluadas de datos nucleares, mostradas solo para comparar: INCOGNITA no las usa y no están en las descargas. Cada una se reconstruye a 0 K a partir del archivo ENDF-6 de la biblioteca (NJOY) y se promedia sobre los mismos intervalos de energía que la curva (promedios en el logaritmo de la energía, así que las resonancias quedan suavizadas); la MACS usa la curva puntual completa.",
  dx_lib_none: "No hay archivo para este núclido en", dx_lib_notab: "No hay un valor separado para esta reacción en",
  dx_lib_held: "JENDL-5 se añadirá cuando se confirmen sus condiciones para redistribuir tablas derivadas.",
});

/* library v0.2.3: a nuclide whose capture below 1 MeV hinges on one engine setting ({n}: the factor at 30 keV) */
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

/* INCOGNITA's own capture below 1 keV */
Object.assign(WT.L.ui, {
  dx_rr_b1k: "Por debajo de 1 keV",
  dx_rr_own: "ajuste de resonancias propio de INCOGNITA a datos medidos (hasta 300 eV; resonancias estadísticas de 300 eV a 1 keV)",
  dx_rr_stat: "resonancias estadísticas a partir de los parámetros medios propios de INCOGNITA, no las resonancias medidas: las posiciones de los picos son una muestra al azar; en muchos núclidos, la integral de resonancia suele quedar dentro de un factor 2 de la medida",
  dx_rr_anch: "; pasa por la captura térmica medida",
  dx_rr_sm_a: "estimación suave de INCOGNITA que pasa por la captura térmica medida; sin resonancias dibujadas",
  dx_rr_sm: "estimación suave de INCOGNITA; los valores térmicos reales pueden diferir en órdenes de magnitud",
  dx_rr_k_own: "ajuste de resonancias propio",
  dx_rr_k_stat: "resonancias estadísticas (no los picos reales)",
  dx_rr_k_sm: "estimación suave (sin resonancias)",
  dx_below_rr: "por debajo de 1 keV: {k} de INCOGNITA",
  dx_below_own: "Por debajo de 1 keV, la línea continua es el ajuste de resonancias propio de INCOGNITA a datos de captura medidos, hasta 300 eV; de 300 eV a 1 keV usa resonancias estadísticas. Se une a la predicción en 1 keV.",
  dx_below_stat: "Por debajo de 1 keV, la línea de trazo y punto es la estimación estadística de INCOGNITA: resonancias con el espaciado y las anchuras medios propios de INCOGNITA, colocadas al azar, así que un pico concreto no coincide con los reales. Probada en núclidos cuya integral de resonancia no se usó en el ajuste, solía quedar dentro de un factor 2 de la medida, y no mejor: desviación mediana ×1,9, 54 % dentro de ×2.",
  dx_below_sm_a: "Por debajo de 1 keV, la línea de puntos es la estimación suave de INCOGNITA: una curva 1/v que pasa por la captura térmica medida, enlazada con el valor en 1 keV. No se dibujan resonancias, así que entre 1 eV y 1 keV, aproximadamente, la sección eficaz real puede ser mucho mayor en sus picos.",
  dx_below_sm: "Por debajo de 1 keV, la línea de puntos es la estimación suave de INCOGNITA: el valor en 1 keV prolongado como 1/v, sin resonancias ni medida que lo fije. Los valores térmicos reales pueden diferir de ella en órdenes de magnitud.",
  dx_below_anch: "Está forzada a pasar por un valor medido de captura térmica, {v} b.",
  dx_rr_anch_diff: "El rombo es un promedio aparte de entradas EXFOR y difiere de ese valor.",
  dx_rr_ri: "Integral de resonancia de la captura por encima de 0,5 eV para este núclido: INCOGNITA {m} b, medida {e} b.",
  dx_rr_ri_used: "Ese valor medido se usó para elegir esta muestra al azar, así que el acuerdo no es una prueba.",
  dx_rr_ri_hold: "Ese valor medido no se usó para hacer esta curva.",
  dx_pw_tip_rr: "bibliotecas evaluadas (comparadores), puntuales a 0 K",
  dx_lib_pw_rr: "Por debajo de 1 keV las mismas bibliotecas se dibujan punto a punto, con líneas finas continuas: reconstruidas a 0 K (NJOY RECONR, tolerancia del 0,01 %) y reducidas a un máximo de {n} puntos por curva, elegidos para conservar los picos y los valles de las resonancias. También son comparadores, no INCOGNITA.",
  dx_tr_h: "Hasta qué punto fiarse de esto",
  dx_tr_t0: "Núcleo medido. La curva sigue siendo la predicción propia del motor, no ajustada a estas medidas; pero los ajustes globales del motor se eligieron con muchos núcleos, este entre ellos, así que una coincidencia aquí es una comprobación, no una prueba independiente.",
  dx_tr_t1: "Anclado. La curva del motor se escala con un único factor a un promedio estelar medido a 30 keV, así que su forma sigue siendo la del modelo. El nivel, mantenido de la v0.1, significa que la biblioteca no tenía secciones eficaces de captura medidas de este núcleo; las medidas depuradas que se muestran abajo, si las hay, no se usaron para la curva.",
  dx_tr_t2: "Interpolado. No medido, pero a dos neutrones o protones como mucho de núcleos medidos; la curva es la predicción del modelo.",
  dx_tr_t3: "Extrapolado. No medido y fuera del nivel interpolado de la biblioteca (ese nivel exige también datos de estructura, y su regla deja fuera algunos núcleos contiguos a núcleos medidos): la curva es solo el modelo, sin ninguna medida con la que comprobarla.",
  dx_t4: "No medido (Z < 26)", dx_t5: "Medido (nivel de la biblioteca sin actualizar)", dx_ts4: "no medido", dx_ts5: "medido", dx_t6: "Medido (Z < 26)", dx_ts6: "medido",
  dx_tr_t4: "No medido. No hay ninguna medida de captura depurada de este núcleo: ninguna en EXFOR, o la depuración las excluyó todas. La curva es solo el modelo. Por debajo de Z ≈ 20 la captura pasa por resonancias individuales que este motor estadístico no describe: lee la curva como una estimación aproximada.",
  dx_tr_t5: "Núcleo medido. La biblioteca aún lo clasifica como interpolado o extrapolado (el nivel se mantuvo de la v0.1), pero existen medidas de captura depuradas de él, que se muestran abajo. La curva es la predicción propia del motor, no ajustada a ellas, así que compararlas es una comprobación del modelo.",
  dx_tr_t6: "Núcleo medido. Abajo se muestran medidas de captura de EXFOR depuradas (la misma depuración automática que desde Z 26; ninguna persona ha revisado sus decisiones para estos núcleos ligeros). La curva es la predicción del motor, no ajustada a ellas. Por debajo de Z ≈ 20 la captura pasa por resonancias individuales que este motor estadístico no describe: lee la curva como una estimación aproximada.",
  dx_tr_out: "Fuera de Z 26–83, el intervalo que cubre la validación de la biblioteca.",
  dx_tr_mf: "Marca de forma del modelo: un ajuste del motor cambia aquí la captura en más de un factor 2 (ver la nota de arriba). Ninguna medida puede decidir entre las dos opciones; las bandas por debajo de 1 MeV se ensanchan para contener ambas.",
  dx_tr_mf_gg: "Marca de forma del modelo: el valor depende de la corrección del motor para una anchura de desintegración gamma que falta (ver la nota de arriba); la banda no se ensancha por ello.",
  dx_tr_b_ok: "las bandas cubren lo indicado (si acaso, anchas)",
  dx_tr_b_unm: "bandas comprobadas solo en núcleos medidos, no en núcleos como este",
  dx_tr_b_narrow: "banda probablemente demasiado estrecha: cubrió de menos",
  dx_tr_b_none: "sin banda",
  dx_tr_b_macs: "banda no comprobada por separado",
  dx_tr_e: "error de comparación típicamente ×{f} ({n} núcleos medidos, Z {z}; comparación de desarrollo)",
  dx_tr_e_none: "no hay comparación con medidas para esta región",
  dx_tr_src: "Nivel y marcas: README de library/v0.2. Bandas: una comprobación de cobertura frente a medidas (5 núcleos de prueba, octubre de 2026), en la que las bandas de captura, fisión y dispersión elástica cubrieron lo indicado y las de los canales con umbral y la total cubrieron de menos. Errores: la página <a href=\"scoreboard.html\" data-keep-lang>Comparaciones</a>, media cuadrática de log10(motor / medido); no es una prueba independiente, porque las reglas del motor se eligieron mirándola.",
});
// less text (2026-11-06)
Object.assign(WT.L.ui, { dx_hint2: "Arrastra para mover · desplaza para ampliar · haz clic en un cuadro", dx_more_nuc: "Detalles: cuánto fiarse, fuentes, código", dx_about: "Sobre los datos, descargas y código" });
Object.assign(WT.L.ui, { dx_cmp: "comparación" });
// R-matrix evaluation (light nuclei)
Object.assign(WT.L.ui, {"dx_el": "Elástica (n,n)", "dx_rm_name": "Evaluación de matriz R de INCOGNITA", "dx_rm_h": "Nuestro modelo para este núclido", "dx_rm_what": "Dispersión elástica de neutrones en carbono-12 a partir del propio ajuste de matriz R multinivel de INCOGNITA a datos medidos de EXFOR de las secciones eficaces total y elástica. Antes de publicarse superó comprobaciones fijadas de antemano: el patrón de carbono del OIEA, mediciones de la sección eficaz total no usadas en el ajuste, un procesamiento de ida y vuelta con NJOY y un benchmark de criticidad con grafito (PCI-001).", "dx_rm_range": "Rango de energía: de {lo} a {hi}; por encima no hay curva de INCOGNITA.", "dx_rm_caveat": "Advertencia: χ²/grado de libertad en la muestra {c}; dos conjuntos de datos inclinados señalados; las comprobaciones están calibradas pero tienen poca potencia estadística.", "dx_rm_nocap": "La captura no se modela: la pestaña de captura muestra solo mediciones.", "dx_rm_report": "Leer el informe"});
// measured resonances below 1 keV + energy-band strip (2026-11-07)
Object.assign(WT.es.ui, { "dx_rr_meas": "resonancias medidas por experimentadores (parámetros de resonancia de EXFOR), reunidas por INCOGNITA; los espines, anchuras radiativas y niveles débiles no medidos proceden de la estadística propia de INCOGNITA", "dx_rr_own_t": "ajuste Reich–Moore de resonancias propio de INCOGNITA a datos de transmisión medidos de EXFOR, de 10 µeV a 1 keV; no es un archivo de biblioteca", "dx_rr_k_meas": "resonancias medidas (parámetros de EXFOR)", "dx_below_meas": "Por debajo de 1 keV, la línea continua usa energías y anchuras de resonancia que los experimentadores midieron y publicaron en EXFOR, combinadas entre experimentos; no es un ajuste de INCOGNITA. Donde no se midió un espín o una anchura radiativa, lo aporta la estadística propia de INCOGNITA, y los niveles débiles que los experimentos no podían ver se añaden estadísticamente (sus posiciones no son predicciones). Se une a la predicción en 1 keV.", "dx_below_own_t": "Por debajo de 1 keV, la línea continua es el ajuste Reich–Moore de resonancias propio de INCOGNITA a datos de transmisión medidos de EXFOR. Se une a la predicción en 1 keV. La nota junto al núclido indica qué conjuntos de datos se usaron y cómo se compara el ajuste con los datos no usados en el ajuste.", "dx_band_th": "térmica", "dx_band_th_s": "térmica", "dx_band_th_x": "térm.", "dx_band_rr": "resonancias", "dx_band_rr0": "región de resonancias", "dx_band_rr_s": "resonancias", "dx_band_rr_x": "res.", "dx_band_ur": "resonancias promediadas", "dx_band_ur_s": "promediadas", "dx_band_ur_x": "prom.", "dx_band_f": "rápida", "dx_band_f_s": "rápida", "dx_band_f_x": "rápida", "dx_band_all": "todas las energías" });

/* site menu: 'More Nuclear Topics' link (nav.js), also on pages that do not load the ui file */
Object.assign(WT.L.ui, { nav_topics: "Más temas nucleares" });

/* C-12 elastic tab: natural-carbon curve, unfitted totals, IAEA standard, ENDF/B-VIII.1 comparator */
Object.assign(WT.L.ui, {"dx_rm_natc": "Matriz R de INCOGNITA, carbono natural", "dx_rm_cmp": "Aquí la curva es carbono natural, como las medidas y el estándar: 98,93 % del C-12 de INCOGNITA más 1,07 % de C-13 de ENDF/B-VIII.1, que produce el pico estrecho en 153 keV; la curva de C-12 puro está en las descargas. Concuerda con el estándar de neutrones del OIEA 2017 dentro del {dev} % (mayor |z| {z}); en las secciones totales no usadas en el ajuste χ²/N = {chi}; superó todas las comprobaciones. EXFOR {set} queda un {off} % por debajo de INCOGNITA y de ENDF/B-VIII.1: un desfase en la normalización de ese conjunto.", "dx_ho": "secciones totales medidas no usadas en el ajuste, natC", "dx_ho_tip": "no usada en el ajuste: comparada solo después del ajuste final", "dx_bin": "promediadas en intervalos logarítmicos de energía", "dx_bin_tip": "media de {n} puntos medidos no ajustados ± su error estándar", "dx_std": "estándar de neutrones del OIEA 2017 (natC elástica)", "dx_std_dev": "INCOGNITA / estándar − 1", "dx_lib_el": "Línea discontinua: ENDF/B-VIII.1 elástica para carbono natural (98,93 % C-12 + 1,07 % C-13), punto a punto a 0 K, solo como comparación: INCOGNITA no la usa y no está en las descargas."});
