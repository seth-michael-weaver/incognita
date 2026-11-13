/* French: data explorer (data.html, js/data.js) */
Object.assign(WT.L.ui, {
  lang_label: "Langue", nav_teach: "Enseignants",
  brand: "Au cœur d'une réaction nucléaire", nav_physics: "La physique", nav_data: "Tous les nucléides", nav_board: "Comparaisons", menu: "Menu", site_nav: "Site",
  dx_title: "Tous les nucléides · Au cœur d'une réaction nucléaire",
  site_nav: "Site", nav_walk: "Le parcours", nav_board: "Comparaisons", nav_data: "Tous les nucléides", nav_repo: "Code sur GitHub",
  dx_kicker: "INCOGNITA · explorateur de données",
  dx_h1: "Tous les nucléides",
  dx_lede: "Les sections efficaces neutroniques prédites par le moteur pour chaque nucléide de la bibliothèque, à côté des mesures sélectionnées de chaque nucléide. Choisissez un nucléide sur la carte, ou cherchez-le.",
  dx_lede_ver: "Les courbes sont la bibliothèque v0.2.3 (novembre 2026), produite avec la même version du moteur que celle notée sur la page Comparaisons (le moteur du 22 octobre 2026). Ce n'est pas TERRA, le produit de données présenté sur cette page, ajusté aux mesures. Chaque courbe est la prédiction du moteur lui-même : aucune n'a été ajustée aux mesures affichées à côté, sauf pour un nucléide marqué ancré, dont la courbe est multipliée par un seul facteur afin que sa moyenne stellaire à 30 keV égale la valeur mesurée. Les réglages généraux du moteur ont été choisis une fois pour tous les nucléides, à l'aide de nombreuses mesures (dont celles-ci) ; un accord sur un nucléide mesuré est donc une vérification honnête du modèle, mais pas entièrement indépendante. La plupart des nucléides n'ont jamais été mesurés (extrapolés), et leurs bandes sont larges.",
  dx_controls: "Commandes de la carte", dx_search_label: "Trouver un nucléide", dx_search_ph: "Rechercher : U-235, Fe56, Au…",
  dx_colour: "Colorer la carte selon", dx_m_tier: "Comment on le connaît", dx_m_macs: "Capture à 30 keV", dx_m_meas: "Données mesurées",
  dx_chart_h: "Carte des nucléides",
  dx_chart_aria: "Carte des nucléides : protons vers le haut, neutrons vers la droite. Utilisez la recherche pour choisir un nucléide.",
  dx_hint: "Faites glisser pour vous déplacer, utilisez la molette ou pincez pour zoomer. Cliquez sur une case pour l'ouvrir : les détails du nucléide s'affichent sous la carte. Protons vers le haut, neutrons vers la droite.",
  dx_full: "Afficher toute la plage d'énergie", dx_mk_thr: "seuil", dx_mk_cb: "barrière coulombienne",
  dx_show_excl: "Afficher les points exclus par la sélection", dx_table: "Afficher sous forme de tableau",
  dx_run_h: "Obtenez ces nombres vous-même", dx_copy: "Copier", dx_copied: "Copié",
  dx_repo_h: "Exécutez-le vous-même",
  dx_repo_p: "Tout ce qui figure sur cette page vient du dépôt ouvert : le moteur, la bibliothèque et les mesures sélectionnées. Il vous faut Linux ou macOS, Python 3.12 et <a href=\"https://docs.astral.sh/uv/\">uv</a>.",
  credit_sub: "Le moteur INCOGNITA est un portage de <a href=\"https://doi.org/10.1140/epja/s10050-023-01034-3\">TALYS-2</a> (A. J. Koning, S. Hilaire, S. Goriely) et utilise la base de données de structure nucléaire de TALYS. Ce qu'INCOGNITA ajoute est <a href=\"./?lang=fr#code\">détaillé, option par option, à la fin de la page pédagogique</a>.",
  dx_repo_p2: "Pour exécuter le moteur lui-même, il faut aussi la base de données de structure de TALYS ; le README explique comment la récupérer.",
  dx_repo_link: "seth-michael-weaver/incognita sur GitHub →",
  dx_src: "Sources : prédictions de la bibliothèque v0.2.3 (<code>library/v0.2.3</code>) ; mesures de capture issues d'EXFOR, sélectionnées dans <code>data/curation</code> ; mesures (n,2n), (n,p) et (n,α) issues des lignes de référence de <code>incognita/bench</code> (sous Z 26 : lignes EXFOR retenues selon les mêmes règles, <code>data/curation/inputs</code>). Les mesures écartées par la sélection sont masquées, sauf si vous les demandez. La superposition facultative (en tirets) des bibliothèques évaluées (ENDF/B-VIII.1, JEFF-4.0, TENDL-2025) est produite par <code>scripts/build_site_overlay.py</code> uniquement pour l'affichage ; INCOGNITA ne la lit jamais.",
  dx_t0: "Mesuré", dx_t1: "Ancré sur une MACS mesurée", dx_t2: "Interpolé (proche de nucléides mesurés)", dx_t3: "Extrapolé",
  dx_ts0: "mesuré", dx_ts1: "ancré", dx_ts2: "interpolé", dx_ts3: "extrapolé",
  dx_keep: "conservé", dx_down: "sous-pondéré", dx_excl: "exclu", dx_fix: "unité corrigée",
  dx_cap: "Capture (n,γ)", dx_macs: "Moyenne stellaire (MACS)", dx_nat: "naturel",
  dx_l_cap: "capture mesurée", dx_l_thr: "seulement (n,2n), (n,p) ou (n,α) mesurés", dx_l_none: "aucune mesure dans cet ensemble",
  dx_l_macs: "capture moyennée sur une maxwellienne prédite à kT = 30 keV (échelle logarithmique)", dx_l_nomacs: "pas de valeur",
  dx_capsets: "jeux de données de capture", dx_measured: "Mesuré",
  dx_outside: "hors du domaine validé (Z 26–83)", dx_flag: "les résonances résolues atteignent la fenêtre de la MACS : préférez une MACS mesurée",
  dx_nocurve: "pas de courbe de bibliothèque pour cette entrée ; les mesures proviennent de",
  dx_xE: "énergie du neutron", dx_pred: "prédiction (bibliothèque v0.2.3)",
  dx_res: "résonances résolues : ici, la courbe est une moyenne",
  dx_empty: "Rien à afficher pour cette réaction.", dx_bands: "bandes : 68 % et 95 %", dx_band68: "bande : 68 %",
  dx_meas_pts: "mesurés", dx_table_hint: "Utilisez « Afficher sous forme de tableau » pour les valeurs.", dx_ds_h: "Mesures", dx_pts: "pts",
  dx_th_src: "Source", dx_th_val: "Valeur", dx_th_unc: "Plage / incertitude", dx_th_cur: "Sélection",
  dx_s_p: "protons", dx_s_n: "neutrons", dx_s_macs: "capture dans une étoile à 30 keV", dx_s_pts: "points de capture mesurés", dx_s_thr: "points (n,2n), (n,p), (n,α)", dx_sets: "jeux",
  dx_exfor_click: "cliquez sur le point pour l'ouvrir", dx_exfor_tap: "touchez à nouveau, ou ici, pour l'ouvrir",
  dx_mxw: "moyenne maxwellienne", dx_state: "état", dx_cur: "sélection", dx_fail: "Impossible de charger les données.", dx_loading: "Chargement", dx_nload: "Impossible de charger ce nucléide.", dx_retry: "Réessayer",
});

/* downloads and data access */
Object.assign(WT.L.ui, {
  dx_dl: "Télécharger ce nucléide :",
  dx_dl_note: "Chaque courbe et chaque point mesuré de ce nucléide, toutes réactions confondues, avec les unités, les sources et les identifiants EXFOR inscrits dans le fichier.",
  dx_access: "<b>Accès aux données.</b> Tout ce qui est affiché ici se trouve dans le dépôt, sous <a href=\"https://github.com/seth-michael-weaver/incognita/tree/main/library/v0.2.3\"><code>library/v0.2.3</code></a> : courbes de capture avec bandes à 68 / 95 % (<code>capture_v023.parquet</code>), moyennes maxwelliennes (<code>macs30_v023.csv</code>, <code>macs_kt_v023.csv</code>), taux stellaires (<code>rates_v023.csv</code>, <code>reaclib_v023.dat</code>) et les voies (n,2n), (n,p), (n,α) (<code>channels_v023.parquet</code>, <code>grid_np_v023.parquet</code>), vérifiés par <code>SHA256SUMS</code>. Pour un seul nucléide, les téléchargements CSV et JSON ci-dessus suffisent. Les mesures sélectionnées se trouvent dans <code>data/curation</code> ; elles proviennent d'EXFOR (Section des données nucléaires de l'AIEA) et conservent leurs identifiants EXFOR. Les données de la bibliothèque sont sous licence CC-BY-4.0. La version précédente, v0.1, reste dans <code>library/v0.1</code> ; le fichier <code>CHANGELOG.md</code> de <code>library/v0.2.3</code> indique ce qui a changé.",
});
Object.assign(WT.L.ui, {
  dx_lib: "Superposer des bibliothèques évaluées (comparaison seulement — INCOGNITA ne les utilise pas)",
  dx_eval: "évaluation", dx_lib_pd: "domaine public (États-Unis)", dx_lib_loading: "Chargement des bibliothèques…",
  dx_lib_bin: "bibliothèques : moyennes par intervalle",
  dx_lib_note: "Les lignes en tirets sont des bibliothèques évaluées de données nucléaires, affichées uniquement pour comparaison : INCOGNITA ne les utilise pas et elles ne figurent pas dans les téléchargements. Chacune est reconstruite à 0 K à partir du fichier ENDF-6 de la bibliothèque (NJOY) et moyennée sur les mêmes intervalles d'énergie que la courbe (moyennes en logarithme de l'énergie, si bien que les résonances sont lissées) ; la MACS utilise la courbe ponctuelle complète.",
  dx_lib_none: "Pas de fichier pour ce nucléide dans", dx_lib_notab: "Pas de valeur distincte pour cette réaction dans",
  dx_lib_held: "JENDL-5 sera ajoutée dès que ses conditions de redistribution des tables dérivées seront confirmées.",
});

/* library v0.2.3: a nuclide whose capture below 1 MeV hinges on one engine setting ({n}: the factor at 30 keV) */
Object.assign(WT.L.ui, {
  dx_mf_pe_lo: "Choix de modèle incertain : ce moteur laisse une particule s'échapper avant que le noyau ne se stabilise (émission de prééquilibre) à toutes les énergies, alors que TALYS ne le fait qu'au-dessus d'environ 1 MeV ; le choix de TALYS donne environ {n} fois moins de capture à 30 keV, et la bande à 95 % sous 1 MeV couvre les deux.",
  dx_mf_pe_hi: "Choix de modèle incertain : ce moteur laisse une particule s'échapper avant que le noyau ne se stabilise (émission de prééquilibre) à toutes les énergies, alors que TALYS ne le fait qu'au-dessus d'environ 1 MeV ; le choix de TALYS donne environ {n} fois plus de capture à 30 keV, et la bande à 95 % sous 1 MeV couvre les deux.",
  dx_mf_pe_near: "Choix de modèle incertain : ce moteur laisse une particule s'échapper avant que le noyau ne se stabilise (émission de prééquilibre) à toutes les énergies, alors que TALYS ne le fait qu'au-dessus d'environ 1 MeV ; le choix de TALYS concorde à 30 keV mais diffère de plus d'un facteur 2 ailleurs sous 1 MeV, et la bande à 95 % y couvre les deux.",
  dx_mf_fi_lo: "Choix de modèle incertain : sous 1 MeV, cette courbe dépend d'un réglage du moteur sur la façon dont le noyau franchit ses barrières de fission ; l'autre choix donne environ {n} fois moins de capture à 30 keV, et la bande à 95 % sous 1 MeV couvre les deux.",
  dx_mf_fi_hi: "Choix de modèle incertain : sous 1 MeV, cette courbe dépend d'un réglage du moteur sur la façon dont le noyau franchit ses barrières de fission ; l'autre choix donne environ {n} fois plus de capture à 30 keV, et la bande à 95 % sous 1 MeV couvre les deux.",
  dx_mf_fi_near: "Choix de modèle incertain : sous 1 MeV, cette courbe dépend d'un réglage du moteur sur la façon dont le noyau franchit ses barrières de fission ; l'autre choix concorde à 30 keV mais diffère de plus d'un facteur 2 ailleurs sous 1 MeV, et la bande à 95 % y couvre les deux.",
  dx_mf_gg_lo: "Cette courbe utilise une correction de la désexcitation gamma du noyau que TALYS et TENDL n'appliquent pas ; sans elle, la capture à 30 keV serait environ {n} fois plus faible.",
  dx_mf_gg_hi: "Cette courbe utilise une correction de la désexcitation gamma du noyau que TALYS et TENDL n'appliquent pas ; sans elle, la capture à 30 keV serait environ {n} fois plus forte.",
  dx_mf_gg_near: "Cette courbe utilise une correction de la désexcitation gamma du noyau que TALYS et TENDL n'appliquent pas ; sans elle, la capture à 30 keV serait à peu près la même.",
});

/* pointwise library comparators below 1 keV and the measured thermal value (KONINGOVERLAY) */
Object.assign(WT.L.ui, {
  dx_eval_cmp: "bibliothèque évaluée · comparateur, pas INCOGNITA",
  dx_pw_leg2: "en trait plein sous 1 keV : ponctuel, 0 K",
  dx_lib_pw_dense: "Ce nucléide a beaucoup de résonances sous 1 keV ; il garde donc plus de points : cinq par pic de résonance, jusqu'à 5000 (avec un budget fixe de 500, beaucoup de pics de U-235 ou de Pu-239 seraient coupés).",
  dx_pw_short: "ponctuel à 0 K, sous 1 keV",
  dx_lib_pw: "Sous 1 keV, les mêmes bibliothèques sont tracées point par point, en traits fins continus : reconstruites à 0 K (NJOY RECONR, tolérance 0,01 %) et réduites à au plus {n} points par courbe, choisis pour garder les pics et les creux des résonances. Ce sont aussi des comparateurs : INCOGNITA n'a pas de courbe sous 1 keV.",
  dx_below_cv: "sous 1 keV : pas de courbe INCOGNITA, seulement des bibliothèques évaluées et des mesures",
  dx_below: "La courbe propre d'INCOGNITA commence à 1 keV ; en dessous, seuls les comparateurs et les mesures sont affichés.",
  dx_pw_tip: "bibliothèques évaluées (comparateurs), ponctuelles à 0 K ; pas de courbe INCOGNITA sous 1 keV",
  dx_th: "valeur thermique mesurée (EXFOR)",
  dx_th_sent: "Losange : section efficace de capture thermique mesurée σγ(0,0253 eV)",
  dx_th_mean: "moyenne pondérée de {n} entrées EXFOR",
  dx_th_abs: "absorption moins fission",
});

/* INCOGNITA's own capture below 1 keV */
Object.assign(WT.L.ui, {
  dx_rr_b1k: "Sous 1 keV",
  dx_rr_own: "ajustement des résonances propre à INCOGNITA sur des données mesurées (jusqu'à 300 eV ; résonances statistiques de 300 eV à 1 keV)",
  dx_rr_stat: "résonances statistiques tirées des paramètres moyens propres à INCOGNITA, pas les résonances mesurées : la position des pics est un tirage au hasard ; sur de nombreux nucléides, l'intégrale de résonance est typiquement à un facteur 2 près de la mesure",
  dx_rr_anch: " ; passe par la capture thermique mesurée",
  dx_rr_sm_a: "estimation lisse d'INCOGNITA passant par la capture thermique mesurée ; aucune résonance tracée",
  dx_rr_sm: "estimation lisse d'INCOGNITA ; les vraies valeurs thermiques peuvent différer de plusieurs ordres de grandeur",
  dx_rr_k_own: "propre ajustement des résonances",
  dx_rr_k_stat: "résonances statistiques (pas les vrais pics)",
  dx_rr_k_sm: "estimation lisse (sans résonances)",
  dx_below_rr: "sous 1 keV : {k} d'INCOGNITA",
  dx_below_own: "Sous 1 keV, le trait plein est l'ajustement des résonances propre à INCOGNITA sur des données de capture mesurées, jusqu'à 300 eV ; de 300 eV à 1 keV, il utilise des résonances statistiques. Il rejoint la prédiction à 1 keV.",
  dx_below_stat: "Sous 1 keV, le trait mixte est l'estimation statistique d'INCOGNITA : des résonances avec l'espacement et les largeurs moyens propres à INCOGNITA, placées au hasard ; un pic isolé ne correspond donc pas aux vrais. Testée sur des nucléides dont l'intégrale de résonance n'avait pas servi à l'ajustement, elle était typiquement à un facteur 2 près de la mesure, pas mieux : écart médian ×1,9, 54 % à moins de ×2.",
  dx_below_sm_a: "Sous 1 keV, le pointillé est l'estimation lisse d'INCOGNITA : une courbe en 1/v passant par la capture thermique mesurée, raccordée à la valeur à 1 keV. Aucune résonance n'est tracée ; entre environ 1 eV et 1 keV, la vraie section efficace peut donc être bien plus haute à ses pics.",
  dx_below_sm: "Sous 1 keV, le pointillé est l'estimation lisse d'INCOGNITA : la valeur à 1 keV prolongée en 1/v, sans résonances et sans mesure pour la fixer. Les vraies valeurs thermiques peuvent en différer de plusieurs ordres de grandeur.",
  dx_below_anch: "Elle est forcée à passer par une valeur de capture thermique mesurée, {v} b.",
  dx_rr_anch_diff: "Le losange est une moyenne distincte d'entrées EXFOR et en diffère.",
  dx_rr_ri: "Intégrale de résonance de la capture au-dessus de 0,5 eV pour ce nucléide : INCOGNITA {m} b, mesure {e} b.",
  dx_rr_ri_used: "Cette valeur mesurée a servi à choisir ce tirage au hasard : l'accord n'est donc pas un test.",
  dx_rr_ri_hold: "Cette valeur mesurée n'a pas servi à faire cette courbe.",
  dx_pw_tip_rr: "bibliothèques évaluées (comparateurs), ponctuelles à 0 K",
  dx_lib_pw_rr: "Sous 1 keV, les mêmes bibliothèques sont tracées point par point, en traits fins continus : reconstruites à 0 K (NJOY RECONR, tolérance 0,01 %) et réduites à au plus {n} points par courbe, choisis pour garder les pics et les creux des résonances. Ce sont aussi des comparateurs : pas INCOGNITA.",
  dx_tr_h: "Jusqu’où s’y fier",
  dx_tr_t0: "Noyau mesuré. La courbe reste la prédiction propre du moteur, non ajustée à ces mesures ; mais les réglages globaux du moteur ont été choisis à l’aide de nombreux noyaux, dont celui-ci, donc un accord ici est une vérification, pas un test indépendant.",
  dx_tr_t1: "Ancré. La courbe du moteur est mise à l’échelle par un seul facteur sur une moyenne stellaire mesurée à 30 keV, sa forme reste donc celle du modèle. Ce niveau, conservé depuis la v0.1, signifie que la bibliothèque n’avait pas de section efficace de capture mesurée pour ce noyau ; les mesures sélectionnées affichées ci-dessous, s’il y en a, n’ont pas servi à la courbe.",
  dx_tr_t2: "Interpolé. Non mesuré, mais à deux neutrons ou protons au plus de noyaux mesurés ; la courbe est la prédiction du modèle.",
  dx_tr_t3: "Extrapolé. Non mesuré et hors du niveau interpolé de la bibliothèque (ce niveau exige aussi des données de structure, et sa règle laisse de côté certains noyaux voisins immédiats de noyaux mesurés) : la courbe est le modèle seul, sans mesure pour la vérifier.",
  dx_t4: "Non mesuré (Z < 26)", dx_t5: "Mesuré (niveau de la bibliothèque non mis à jour)", dx_ts4: "non mesuré", dx_ts5: "mesuré", dx_t6: "Mesuré (Z < 26)", dx_ts6: "mesuré",
  dx_tr_t4: "Non mesuré. Aucune mesure de capture sélectionnée pour ce noyau : aucune dans EXFOR, ou la sélection les a toutes exclues. La courbe est le modèle seul. En dessous de Z ≈ 20, la capture passe par des résonances individuelles que ce moteur statistique ne décrit pas : lisez la courbe comme une estimation grossière.",
  dx_tr_t5: "Noyau mesuré. La bibliothèque le classe encore comme interpolé ou extrapolé (niveau conservé depuis la v0.1), mais des mesures de capture sélectionnées existent et sont affichées ci-dessous. La courbe est la prédiction propre du moteur, non ajustée à ces mesures : les comparer est donc un test du modèle.",
  dx_tr_t6: "Noyau mesuré. Des mesures de capture EXFOR sélectionnées sont affichées ci-dessous (la même sélection automatique qu’à partir de Z 26 ; personne n’a relu ses décisions pour ces noyaux légers). La courbe est la prédiction du moteur, non ajustée à ces mesures. En dessous de Z ≈ 20, la capture passe par des résonances individuelles que ce moteur statistique ne décrit pas : lisez la courbe comme une estimation grossière.",
  dx_tr_out: "Hors de Z 26–83, le domaine que couvre la validation de la bibliothèque.",
  dx_tr_mf: "Marque de forme du modèle : un réglage du moteur change ici la capture de plus d’un facteur 2 (voir la note plus haut). Aucune mesure ne peut trancher entre les deux choix ; les bandes sous 1 MeV sont élargies pour contenir les deux.",
  dx_tr_mf_gg: "Marque de forme du modèle : la valeur repose sur la correction, par le moteur, d’une largeur de désexcitation gamma manquante (voir la note plus haut) ; la bande n’est pas élargie pour cela.",
  dx_tr_b_ok: "les bandes couvrent comme annoncé (plutôt larges)",
  dx_tr_b_unm: "bandes vérifiées seulement sur des noyaux mesurés, pas sur des noyaux comme celui-ci",
  dx_tr_b_narrow: "bande sans doute trop étroite : elle a sous-couvert",
  dx_tr_b_none: "pas de bande",
  dx_tr_b_macs: "bande non vérifiée à part",
  dx_tr_e: "erreur de comparaison typiquement ×{f} ({n} noyaux mesurés, Z {z} ; comparaison de développement)",
  dx_tr_e_none: "aucune comparaison avec des mesures pour cette région",
  dx_tr_src: "Catégorie et marques : README de library/v0.2. Bandes : une vérification de couverture face aux mesures (5 noyaux test, octobre 2026), où les bandes de capture, de fission et de diffusion élastique ont couvert comme annoncé, et celles des voies à seuil et de la section totale ont sous-couvert. Erreurs : la page <a href=\"scoreboard.html\" data-keep-lang>Comparaisons</a>, moyenne quadratique de log10(moteur / mesure) ; ce n’est pas un test indépendant, car les règles du moteur ont été choisies en le regardant.",
});
// less text (2026-11-06)
Object.assign(WT.L.ui, { dx_hint2: "Glissez pour déplacer · molette pour zoomer · cliquez sur une case", dx_more_nuc: "Détails : quelle confiance, sources, code", dx_about: "À propos des données, téléchargements et code" });
Object.assign(WT.L.ui, { dx_cmp: "comparaison" });
// R-matrix evaluation (light nuclei)
Object.assign(WT.L.ui, {"dx_el": "Élastique (n,n)", "dx_rm_name": "Évaluation en matrice R d’INCOGNITA", "dx_rm_h": "Notre modèle pour ce nucléide", "dx_rm_what": "Diffusion élastique des neutrons sur le carbone 12, issue de l’ajustement en matrice R multiniveau propre à INCOGNITA sur des données EXFOR mesurées des sections efficaces totale et élastique. Avant sa publication, elle a passé des contrôles fixés à l’avance : l’étalon carbone de l’AIEA, des mesures de section efficace totale non utilisées dans l’ajustement, un aller-retour de traitement NJOY et un benchmark de criticité au graphite (PCI-001).", "dx_rm_range": "Domaine d’énergie : de {lo} à {hi} ; pas de courbe INCOGNITA au-delà.", "dx_rm_caveat": "Réserve : χ²/degré de liberté sur l’échantillon {c} ; deux jeux de données inclinés signalés ; les contrôles sont calibrés mais statistiquement peu puissants.", "dx_rm_nocap": "La capture n’est pas modélisée : l’onglet capture ne montre que des mesures.", "dx_rm_report": "Lire le rapport"});
// measured resonances below 1 keV + energy-band strip (2026-11-07)
Object.assign(WT.L.ui, { "dx_rr_meas": "résonances mesurées par des expérimentateurs (paramètres de résonance EXFOR), rassemblées par INCOGNITA ; les spins, largeurs radiatives et niveaux faibles non mesurés viennent des statistiques propres à INCOGNITA", "dx_rr_own_t": "ajustement Reich–Moore des résonances propre à INCOGNITA sur des données de transmission EXFOR mesurées, de 10 µeV à 1 keV ; pas un fichier de bibliothèque", "dx_rr_k_meas": "résonances mesurées (paramètres EXFOR)", "dx_below_meas": "Sous 1 keV, la ligne continue utilise des énergies et des largeurs de résonance que des expérimentateurs ont mesurées et publiées dans EXFOR, fusionnées d’une expérience à l’autre ; ce n’est pas un ajustement d’INCOGNITA. Lorsqu’un spin ou une largeur radiative n’a pas été mesuré, les statistiques propres à INCOGNITA le fournissent, et les niveaux faibles que les expériences ne pouvaient pas voir sont ajoutés statistiquement (leurs positions ne sont pas des prédictions). Elle rejoint la prédiction à 1 keV.", "dx_below_own_t": "Sous 1 keV, la ligne continue est l’ajustement Reich–Moore des résonances propre à INCOGNITA sur des données de transmission EXFOR mesurées. Elle rejoint la prédiction à 1 keV. La note à côté du nucléide indique quels jeux de données ont été utilisés et comment l’ajustement se compare aux données non utilisées dans l’ajustement.", "dx_band_th": "thermique", "dx_band_th_s": "thermique", "dx_band_th_x": "therm.", "dx_band_rr": "résonances", "dx_band_rr0": "domaine des résonances", "dx_band_rr_s": "résonances", "dx_band_rr_x": "rés.", "dx_band_ur": "résonances moyennées", "dx_band_ur_s": "moyennées", "dx_band_ur_x": "moy.", "dx_band_f": "rapide", "dx_band_f_s": "rapide", "dx_band_f_x": "rapide", "dx_band_all": "toutes énergies" });

/* site menu: 'More Nuclear Topics' link (nav.js), also on pages that do not load the ui file */
Object.assign(WT.L.ui, { nav_topics: "Autres sujets nucléaires" });

/* C-12 elastic tab: natural-carbon curve, unfitted totals, IAEA standard, ENDF/B-VIII.1 comparator */
Object.assign(WT.L.ui, {"dx_rm_natc": "Matrice R d’INCOGNITA, carbone naturel", "dx_rm_cmp": "Ici la courbe est le carbone naturel, comme les mesures et l’étalon : 98,93 % du C-12 d’INCOGNITA plus 1,07 % de C-13 issu d’ENDF/B-VIII.1, qui donne le pic étroit à 153 keV ; la courbe du C-12 pur est dans les téléchargements. Elle s’accorde avec l’étalon neutronique AIEA 2017 à {dev} % près (plus grand |z| {z}) ; sur les sections totales non utilisées dans l’ajustement, χ²/N = {chi} ; tous les contrôles sont passés. EXFOR {set} se situe {off} % sous INCOGNITA et ENDF/B-VIII.1 : un décalage dans la normalisation de ce jeu.", "dx_ho": "sections totales mesurées non utilisées dans l’ajustement, natC", "dx_ho_tip": "non utilisée dans l’ajustement : comparée seulement après l’ajustement final", "dx_bin": "moyennées par intervalles logarithmiques d’énergie", "dx_bin_tip": "moyenne de {n} points mesurés non ajustés ± son erreur type", "dx_std": "étalon neutronique AIEA 2017 (natC élastique)", "dx_std_dev": "INCOGNITA / étalon − 1", "dx_lib_el": "Trait tireté : ENDF/B-VIII.1 élastique pour le carbone naturel (98,93 % C-12 + 1,07 % C-13), point par point à 0 K, pour comparaison seulement : INCOGNITA ne l’utilise pas et elle n’est pas dans les téléchargements."});
