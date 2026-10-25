/* German (Deutsch): data explorer (data.html, js/data.js) */
Object.assign(WT.L.ui, {
  lang_label: "Sprache", nav_teach: "Lehrende",
  brand: "Im Inneren einer Kernreaktion", nav_physics: "Die Physik", nav_data: "Alle Nuklide", nav_board: "Rangliste", menu: "Menü", site_nav: "Website",
  dx_title: "Alle Nuklide · Im Inneren einer Kernreaktion",
  site_nav: "Website", nav_walk: "Der Rundgang", nav_board: "Rangliste", nav_data: "Alle Nuklide", nav_repo: "Code auf GitHub",
  dx_kicker: "INCOGNITA · Daten-Explorer",
  dx_h1: "Alle Nuklide",
  dx_lede: "Die von der Engine vorhergesagten Neutronenwirkungsquerschnitte für jedes Nuklid der Bibliothek, neben den kuratierten Messungen jedes Nuklids. Wähl ein Nuklid auf der Karte oder such danach.",
  dx_lede_ver: "Die Kurven sind die Bibliothek v0.2 (Oktober 2026), erstellt mit derselben Engine-Version, die die Rangliste bewertet (der Engine vom 22. Oktober 2026). Sie sind nicht TERRA, das Datenprodukt der Rangliste, das an Messungen angepasst ist. Jede Kurve ist die eigene Vorhersage der Engine: Keine wurde an die daneben gezeigten Messungen angepasst; nur bei einem als verankert markierten Nuklid ist die Kurve mit einem einzigen Faktor skaliert, sodass ihr stellarer Mittelwert bei 30 keV dem gemessenen Wert entspricht. Die allgemeinen Einstellungen der Engine wurden einmal für alle Nuklide anhand vieler Messungen gewählt (auch dieser), daher ist eine Übereinstimmung bei einem gemessenen Nuklid eine faire Prüfung des Modells, wenn auch keine völlig unabhängige. Die meisten Nuklide wurden nie gemessen (extrapoliert), und ihre Bänder sind breit.",
  dx_controls: "Steuerung der Karte", dx_search_label: "Nuklid suchen", dx_search_ph: "Suche: U-235, Fe56, Au…",
  dx_colour: "Karte einfärben nach", dx_m_tier: "Wie es bekannt ist", dx_m_macs: "Einfang bei 30 keV", dx_m_meas: "Messdaten",
  dx_chart_h: "Nuklidkarte",
  dx_chart_aria: "Nuklidkarte: Protonen nach oben, Neutronen nach rechts. Nutze das Suchfeld, um ein Nuklid zu wählen.",
  dx_hint: "Ziehen zum Verschieben, Scrollen oder Zwei-Finger-Geste zum Zoomen. Klick auf ein Feld öffnet es: Die Details zum Nuklid erscheinen unter der Karte. Protonen nach oben, Neutronen nach rechts.",
  dx_full: "Gesamten Energiebereich zeigen", dx_mk_thr: "Schwelle", dx_mk_cb: "Coulombbarriere",
  dx_show_excl: "Von der Kuratierung ausgeschlossene Punkte zeigen", dx_table: "Als Tabelle zeigen",
  dx_run_h: "Diese Zahlen selbst erzeugen", dx_copy: "Kopieren", dx_copied: "Kopiert",
  dx_repo_h: "Selbst ausführen",
  dx_repo_p: "Alles auf dieser Seite stammt aus dem offenen Repository: die Engine, die Bibliothek und die kuratierten Messungen. Du brauchst Linux oder macOS, Python 3.12 und <a href=\"https://docs.astral.sh/uv/\">uv</a>.",
  credit_sub: "Die Engine INCOGNITA ist eine Portierung von <a href=\"https://doi.org/10.1140/epja/s10050-023-01034-3\">TALYS-2</a> (A. J. Koning, S. Hilaire, S. Goriely) und nutzt die Kernstrukturdatenbank von TALYS. Was INCOGNITA hinzufügt, ist <a href=\"./?lang=de#code\" data-keep-lang>am Ende der Lehrseite Schalter für Schalter aufgelistet</a>.",
  dx_repo_p2: "Um die Engine selbst laufen zu lassen, braucht man außerdem die Strukturdatenbank von TALYS; die README erklärt, wie man sie herunterlädt.",
  dx_repo_link: "seth-michael-weaver/incognita auf GitHub →",
  dx_src: "Quellen: Vorhersagen aus der Bibliothek v0.2 (<code>library/v0.2</code>); Einfangmessungen aus EXFOR, kuratiert in <code>data/curation</code>; Messungen zu (n,2n), (n,p) und (n,α) aus den Benchmark-Zeilen in <code>incognita/bench</code>. Von der Kuratierung ausgeschlossene Messungen sind verborgen, solange du sie nicht anforderst. Die optionale gestrichelte Überlagerung evaluierter Bibliotheken (ENDF/B-VIII.1, JEFF-4.0, TENDL-2025) erzeugt <code>scripts/build_site_overlay.py</code> nur zur Anzeige; INCOGNITA liest sie nie.",
  dx_t0: "Gemessen", dx_t1: "An einem gemessenen MACS verankert", dx_t2: "Interpoliert (nahe an gemessenen Nukliden)", dx_t3: "Extrapoliert",
  dx_ts0: "gemessen", dx_ts1: "verankert", dx_ts2: "interpoliert", dx_ts3: "extrapoliert",
  dx_keep: "behalten", dx_down: "heruntergewichtet", dx_excl: "ausgeschlossen", dx_fix: "Einheit korrigiert",
  dx_cap: "Einfang (n,γ)", dx_macs: "Stellarer Mittelwert (MACS)", dx_nat: "natürlich",
  dx_l_cap: "Einfang gemessen", dx_l_thr: "nur (n,2n), (n,p) oder (n,α) gemessen", dx_l_none: "keine Messung in diesem Satz",
  dx_l_macs: "vorhergesagter Maxwell-gemittelter Einfang bei kT = 30 keV (log. Skala)", dx_l_nomacs: "kein Wert",
  dx_capsets: "Einfang-Datensätze", dx_measured: "Gemessen",
  dx_outside: "außerhalb des validierten Bereichs (Z 26–83)", dx_flag: "aufgelöste Resonanzen reichen ins MACS-Fenster: lieber einen gemessenen MACS verwenden",
  dx_nocurve: "keine Bibliothekskurve für diesen Eintrag; die Messungen stammen von",
  dx_xE: "Neutronenenergie", dx_pred: "Vorhersage (Bibliothek v0.2)",
  dx_res: "aufgelöste Resonanzen: die Kurve ist hier ein Mittelwert",
  dx_empty: "Für diese Reaktion gibt es nichts anzuzeigen.", dx_bands: "Bänder: 68 % und 95 %", dx_band68: "Band: 68 %",
  dx_meas_pts: "gemessen", dx_table_hint: "Nutze „Als Tabelle zeigen“ für die Werte.", dx_ds_h: "Messungen", dx_pts: "Pkt.",
  dx_th_src: "Quelle", dx_th_val: "Wert", dx_th_unc: "Bereich / Unsicherheit", dx_th_cur: "Kuratierung",
  dx_s_p: "Protonen", dx_s_n: "Neutronen", dx_s_macs: "Einfang in einem Stern bei 30 keV", dx_s_pts: "gemessene Einfangpunkte", dx_s_thr: "Punkte zu (n,2n), (n,p), (n,α)", dx_sets: "Datensätze",
  dx_exfor_click: "Punkt anklicken zum Öffnen", dx_exfor_tap: "noch einmal oder hier tippen zum Öffnen",
  dx_mxw: "Maxwell-Mittelwert", dx_state: "Zustand", dx_cur: "Kuratierung", dx_fail: "Die Daten konnten nicht geladen werden.", dx_loading: "Wird geladen", dx_nload: "Dieses Nuklid konnte nicht geladen werden.", dx_retry: "Erneut versuchen",
});

/* downloads and data access */
Object.assign(WT.L.ui, {
  dx_dl: "Dieses Nuklid herunterladen:",
  dx_dl_note: "Jede Kurve und jeder Messpunkt zu diesem Nuklid, alle Reaktionen, mit Einheiten, Quellen und EXFOR-Kennungen in der Datei.",
  dx_access: "<b>Datenzugang.</b> Alles, was hier gezeigt wird, liegt im Repository unter <a href=\"https://github.com/seth-michael-weaver/incognita/tree/main/library/v0.2\"><code>library/v0.2</code></a>: Einfangkurven mit 68-/95-%-Bändern (<code>capture_v02.parquet</code>), Maxwell-Mittelwerte (<code>macs30_v02.csv</code>, <code>macs_kt_v02.csv</code>), stellare Raten (<code>rates_v02.csv</code>, <code>reaclib_v02.dat</code>) und die Kanäle (n,2n), (n,p), (n,α) (<code>channels_v02.parquet</code>, <code>grid_np_v02.parquet</code>), geprüft über <code>SHA256SUMS</code>. Für ein einzelnes Nuklid reichen die CSV- und JSON-Downloads oben. Die kuratierten Messungen liegen in <code>data/curation</code>; sie stammen aus EXFOR (Nuclear Data Section der IAEA) und behalten ihre EXFOR-Kennungen. Die Bibliotheksdaten stehen unter CC-BY-4.0. Die frühere Version v0.1 bleibt in <code>library/v0.1</code>; <code>CHANGELOG.md</code> in <code>library/v0.2</code> beschreibt, was sich geändert hat.",
});
Object.assign(WT.L.ui, {
  dx_lib: "Evaluierte Bibliotheken überlagern (nur zum Vergleich — INCOGNITA nutzt sie nicht)",
  dx_eval: "Evaluierung", dx_lib_pd: "gemeinfrei (USA)", dx_lib_loading: "Bibliotheken werden geladen…",
  dx_lib_bin: "Bibliotheken: Intervallmittelwerte",
  dx_lib_note: "Die gestrichelten Linien sind evaluierte Kerndatenbibliotheken, nur zum Vergleich gezeigt: INCOGNITA nutzt sie nicht, und sie sind nicht in den Downloads enthalten. Jede wird bei 0 K aus der ENDF-6-Datei der Bibliothek rekonstruiert (NJOY) und über dieselben Energieintervalle gemittelt wie die Kurve (Mittelwerte im Logarithmus der Energie, sodass Resonanzen geglättet werden); der MACS nutzt die vollständige punktweise Kurve.",
  dx_lib_none: "Keine Datei für dieses Nuklid in", dx_lib_notab: "Kein eigener Wert für diese Reaktion in",
  dx_lib_held: "JENDL-5 kommt hinzu, sobald seine Bedingungen für die Weitergabe abgeleiteter Tabellen bestätigt sind.",
});

/* library v0.2: a nuclide whose capture below 1 MeV hinges on one engine setting ({n}: the factor at 30 keV) */
Object.assign(WT.L.ui, {
  dx_mf_pe_lo: "Unsichere Modellwahl: Diese Engine lässt bei allen Energien ein Teilchen entweichen, bevor sich der Kern beruhigt hat (Präequilibrium-Emission), TALYS dagegen erst oberhalb von etwa 1 MeV; die TALYS-Wahl ergibt bei 30 keV etwa {n}-mal weniger Einfang, und das 95-%-Band unterhalb von 1 MeV deckt beide ab.",
  dx_mf_pe_hi: "Unsichere Modellwahl: Diese Engine lässt bei allen Energien ein Teilchen entweichen, bevor sich der Kern beruhigt hat (Präequilibrium-Emission), TALYS dagegen erst oberhalb von etwa 1 MeV; die TALYS-Wahl ergibt bei 30 keV etwa {n}-mal mehr Einfang, und das 95-%-Band unterhalb von 1 MeV deckt beide ab.",
  dx_mf_pe_near: "Unsichere Modellwahl: Diese Engine lässt bei allen Energien ein Teilchen entweichen, bevor sich der Kern beruhigt hat (Präequilibrium-Emission), TALYS dagegen erst oberhalb von etwa 1 MeV; die TALYS-Wahl stimmt bei 30 keV überein, weicht aber anderswo unterhalb von 1 MeV um mehr als den Faktor 2 ab, und das 95-%-Band deckt dort beide ab.",
  dx_mf_fi_lo: "Unsichere Modellwahl: Unterhalb von 1 MeV hängt diese Kurve von einer Engine-Einstellung dafür ab, wie der Kern seine Spaltbarrieren überwindet; die andere Wahl ergibt bei 30 keV etwa {n}-mal weniger Einfang, und das 95-%-Band unterhalb von 1 MeV deckt beide ab.",
  dx_mf_fi_hi: "Unsichere Modellwahl: Unterhalb von 1 MeV hängt diese Kurve von einer Engine-Einstellung dafür ab, wie der Kern seine Spaltbarrieren überwindet; die andere Wahl ergibt bei 30 keV etwa {n}-mal mehr Einfang, und das 95-%-Band unterhalb von 1 MeV deckt beide ab.",
  dx_mf_fi_near: "Unsichere Modellwahl: Unterhalb von 1 MeV hängt diese Kurve von einer Engine-Einstellung dafür ab, wie der Kern seine Spaltbarrieren überwindet; die andere Wahl stimmt bei 30 keV überein, weicht aber anderswo unterhalb von 1 MeV um mehr als den Faktor 2 ab, und das 95-%-Band deckt dort beide ab.",
  dx_mf_gg_lo: "Diese Kurve verwendet eine Korrektur des Gammazerfalls des Kerns, die TALYS und TENDL nicht anwenden; ohne sie wäre der Einfang bei 30 keV etwa {n}-mal kleiner.",
  dx_mf_gg_hi: "Diese Kurve verwendet eine Korrektur des Gammazerfalls des Kerns, die TALYS und TENDL nicht anwenden; ohne sie wäre der Einfang bei 30 keV etwa {n}-mal größer.",
  dx_mf_gg_near: "Diese Kurve verwendet eine Korrektur des Gammazerfalls des Kerns, die TALYS und TENDL nicht anwenden; ohne sie wäre der Einfang bei 30 keV ungefähr gleich.",
});

/* pointwise library comparators below 1 keV and the measured thermal value (KONINGOVERLAY) */
Object.assign(WT.L.ui, {
  dx_eval_cmp: "evaluierte Bibliothek · Vergleich, nicht INCOGNITA",
  dx_pw_leg2: "durchgezogen unter 1 keV: punktweise, 0 K",
  dx_lib_pw_dense: "Dieses Nuklid hat unter 1 keV viele Resonanzen und behält daher mehr Punkte: fünf je Resonanzspitze, bis zu 5000 (mit festen 500 Punkten würden viele Spitzen von U-235 oder Pu-239 abgeschnitten).",
  dx_pw_short: "punktweise bei 0 K, unter 1 keV",
  dx_lib_pw: "Unter 1 keV werden dieselben Bibliotheken punktweise als dünne durchgezogene Linien gezeichnet: bei 0 K rekonstruiert (NJOY RECONR, Toleranz 0,01 %) und auf höchstens {n} Punkte je Kurve ausgedünnt, so gewählt, dass die Spitzen und Täler der Resonanzen erhalten bleiben. Auch sie dienen nur dem Vergleich: INCOGNITA hat unter 1 keV keine Kurve.",
  dx_below_cv: "unter 1 keV: keine INCOGNITA-Kurve, nur evaluierte Bibliotheken und Messungen",
  dx_below: "INCOGNITAs eigene Kurve beginnt bei 1 keV; darunter werden nur Vergleichsdaten und Messungen gezeigt.",
  dx_pw_tip: "evaluierte Bibliotheken (Vergleich), punktweise bei 0 K; unter 1 keV keine INCOGNITA-Kurve",
  dx_th: "gemessener thermischer Wert (EXFOR)",
  dx_th_sent: "Raute: gemessener thermischer Einfangquerschnitt σγ(0,0253 eV)",
  dx_th_mean: "gewichtetes Mittel aus {n} EXFOR-Einträgen",
  dx_th_abs: "Absorption minus Spaltung",
});
