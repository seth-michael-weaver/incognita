/* Dutch (Nederlands): data explorer (data.html, js/data.js) */
Object.assign(WT.L.ui, {
  lang_label: "Taal", nav_teach: "Docenten",
  brand: "Binnen in een kernreactie", nav_physics: "De natuurkunde", nav_data: "Alle nucliden", nav_board: "Scorebord", menu: "Menu", site_nav: "Site",
  dx_title: "Alle nucliden · Binnen in een kernreactie",
  site_nav: "Site", nav_walk: "De rondleiding", nav_board: "Scorebord", nav_data: "Alle nucliden", nav_repo: "Code op GitHub",
  dx_kicker: "INCOGNITA · dataverkenner",
  dx_h1: "Alle nucliden",
  dx_lede: "De door de motor voorspelde werkzame doorsneden voor neutronen voor elke nuclide in de bibliotheek, naast de gecureerde metingen van elke nuclide. Kies een nuclide op de kaart, of zoek er een op.",
  dx_lede_ver: "De curves zijn de bibliotheek v0.2 (oktober 2026), gemaakt met dezelfde motorversie die het Scorebord scoort (de motor van 22 oktober 2026). Het is niet TERRA, het dataproduct op het Scorebord dat aan metingen is aangepast. Elke curve is de eigen voorspelling van de motor: geen enkele is aangepast aan de metingen ernaast, behalve dat bij een nuclide gemarkeerd als verankerd de curve met één factor is geschaald, zodat het stellair gemiddelde bij 30 keV gelijk is aan de gemeten waarde. De algemene instellingen van de motor zijn één keer gekozen, voor alle nucliden, met veel metingen (ook deze), dus overeenstemming bij een gemeten nuclide is een eerlijke toets van het model, al is die niet volledig onafhankelijk. De meeste nucliden zijn nooit gemeten (geëxtrapoleerd), en hun banden zijn breed.",
  dx_controls: "Bediening van de kaart", dx_search_label: "Zoek een nuclide", dx_search_ph: "Zoek: U-235, Fe56, Au…",
  dx_colour: "Kleur de kaart op", dx_m_tier: "Hoe het bekend is", dx_m_macs: "Vangst bij 30 keV", dx_m_meas: "Gemeten data",
  dx_chart_h: "Nuclidenkaart",
  dx_chart_aria: "Nuclidenkaart: protonen omhoog, neutronen naar rechts. Gebruik het zoekvak om een nuclide te kiezen.",
  dx_hint: "Sleep om te verschuiven, scrol of knijp om te zoomen. Klik op een vakje om het te openen: de details van de nuclide verschijnen onder de kaart. Protonen omhoog, neutronen naar rechts.",
  dx_full: "Toon het hele energiebereik", dx_mk_thr: "drempel", dx_mk_cb: "coulombbarrière",
  dx_show_excl: "Toon punten die de curatie heeft uitgesloten", dx_table: "Toon als tabel",
  dx_run_h: "Bereken deze getallen zelf", dx_copy: "Kopiëren", dx_copied: "Gekopieerd",
  dx_repo_h: "Draai het zelf",
  dx_repo_p: "Alles op deze pagina komt uit de open repository: de motor, de bibliotheek en de gecureerde metingen. Je hebt Linux of macOS nodig, Python 3.12 en <a href=\"https://docs.astral.sh/uv/\">uv</a>.",
  credit_sub: "De INCOGNITA-motor is een port van <a href=\"https://doi.org/10.1140/epja/s10050-023-01034-3\">TALYS-2</a> (A. J. Koning, S. Hilaire, S. Goriely) en gebruikt de kernstructuurdatabase van TALYS. Wat INCOGNITA toevoegt, staat <a href=\"./?lang=nl#code\">schakelaar voor schakelaar onderaan de uitlegpagina</a>.",
  dx_repo_p2: "Om de motor zelf te draaien heb je ook de structuurdatabase van TALYS nodig; de README legt uit hoe je die ophaalt.",
  dx_repo_link: "seth-michael-weaver/incognita op GitHub →",
  dx_src: "Bronnen: voorspellingen uit de bibliotheek v0.2 (<code>library/v0.2</code>); vangstmetingen uit EXFOR, gecureerd in <code>data/curation</code>; metingen van (n,2n), (n,p) en (n,α) uit de benchmarkrijen in <code>incognita/bench</code>. Metingen die de curatie heeft uitgesloten, zijn verborgen tenzij je erom vraagt. De optionele gestippelde overlay van geëvalueerde bibliotheken (ENDF/B-VIII.1, JEFF-4.0, TENDL-2025) wordt alleen voor weergave gebouwd door <code>scripts/build_site_overlay.py</code>; INCOGNITA leest hem nooit in.",
  dx_t0: "Gemeten", dx_t1: "Verankerd aan een gemeten MACS", dx_t2: "Geïnterpoleerd (dicht bij gemeten nucliden)", dx_t3: "Geëxtrapoleerd",
  dx_ts0: "gemeten", dx_ts1: "verankerd", dx_ts2: "geïnterpoleerd", dx_ts3: "geëxtrapoleerd",
  dx_keep: "behouden", dx_down: "lager gewogen", dx_excl: "uitgesloten", dx_fix: "eenheid gecorrigeerd",
  dx_cap: "Vangst (n,γ)", dx_macs: "Stellair gemiddelde (MACS)", dx_nat: "natuurlijk",
  dx_l_cap: "vangst gemeten", dx_l_thr: "alleen (n,2n), (n,p) of (n,α) gemeten", dx_l_none: "geen meting in deze set",
  dx_l_macs: "voorspelde maxwelliaans gemiddelde vangst bij kT = 30 keV (log. schaal)", dx_l_nomacs: "geen waarde",
  dx_capsets: "vangstdatasets", dx_measured: "Gemeten",
  dx_outside: "buiten het gevalideerde bereik (Z 26–83)", dx_flag: "opgeloste resonanties reiken tot in het MACS-venster: gebruik liever een gemeten MACS",
  dx_nocurve: "geen bibliotheekcurve voor deze invoer; de metingen komen uit",
  dx_xE: "neutronenergie", dx_pred: "voorspelling (bibliotheek v0.2)",
  dx_res: "opgeloste resonanties: de curve is hier een gemiddelde",
  dx_empty: "Niets te tonen voor deze reactie.", dx_bands: "banden: 68 % en 95 %", dx_band68: "band: 68 %",
  dx_meas_pts: "gemeten", dx_table_hint: "Gebruik ‘Toon als tabel’ voor de waarden.", dx_ds_h: "Metingen", dx_pts: "ptn",
  dx_th_src: "Bron", dx_th_val: "Waarde", dx_th_unc: "Bereik / onzekerheid", dx_th_cur: "Curatie",
  dx_s_p: "protonen", dx_s_n: "neutronen", dx_s_macs: "vangst in een ster bij 30 keV", dx_s_pts: "gemeten vangstpunten", dx_s_thr: "punten voor (n,2n), (n,p), (n,α)", dx_sets: "datasets",
  dx_exfor_click: "klik op het punt om te openen", dx_exfor_tap: "tik nog eens, of hier, om te openen",
  dx_mxw: "maxwelliaans gemiddelde", dx_state: "toestand", dx_cur: "curatie", dx_fail: "De data konden niet worden geladen.", dx_loading: "Laden", dx_nload: "Deze nuclide kon niet worden geladen.", dx_retry: "Opnieuw proberen",
});

/* downloads and data access */
Object.assign(WT.L.ui, {
  dx_dl: "Download deze nuclide:",
  dx_dl_note: "Elke curve en elk gemeten punt voor deze nuclide, alle reacties, met eenheden, bronnen en EXFOR-id's in het bestand.",
  dx_access: "<b>Toegang tot de data.</b> Alles wat hier getoond wordt, staat in de repository onder <a href=\"https://github.com/seth-michael-weaver/incognita/tree/main/library/v0.2\"><code>library/v0.2</code></a>: vangstcurven met banden van 68 / 95 % (<code>capture_v02.parquet</code>), maxwelliaanse gemiddelden (<code>macs30_v02.csv</code>, <code>macs_kt_v02.csv</code>), stellaire snelheden (<code>rates_v02.csv</code>, <code>reaclib_v02.dat</code>) en de kanalen (n,2n), (n,p), (n,α) (<code>channels_v02.parquet</code>, <code>grid_np_v02.parquet</code>), gecontroleerd met <code>SHA256SUMS</code>. Voor één nuclide zijn de CSV- en JSON-downloads hierboven genoeg. De gecureerde metingen staan in <code>data/curation</code>; ze komen uit EXFOR (IAEA Nuclear Data Section) en behouden hun EXFOR-id's. De bibliotheekdata vallen onder CC-BY-4.0. De eerdere versie v0.1 blijft in <code>library/v0.1</code>; <code>CHANGELOG.md</code> in <code>library/v0.2</code> zegt wat er veranderd is.",
});
Object.assign(WT.L.ui, {
  dx_lib: "Geëvalueerde bibliotheken eroverheen leggen (alleen ter vergelijking — INCOGNITA gebruikt ze niet)",
  dx_eval: "evaluatie", dx_lib_pd: "publiek domein (VS)", dx_lib_loading: "Bibliotheken laden…",
  dx_lib_bin: "bibliotheken: bingemiddelden",
  dx_lib_note: "De gestippelde lijnen zijn geëvalueerde kerndatabibliotheken, alleen ter vergelijking getoond: INCOGNITA gebruikt ze niet en ze zitten niet in de downloads. Elke bibliotheek is bij 0 K gereconstrueerd uit haar ENDF-6-bestand (NJOY) en gemiddeld over dezelfde energiebins als de curve (gemiddelden in de logaritme van de energie, dus resonanties worden gladgestreken); de MACS gebruikt de volledige puntsgewijze curve.",
  dx_lib_none: "Geen bestand voor deze nuclide in", dx_lib_notab: "Geen aparte waarde voor deze reactie in",
  dx_lib_held: "JENDL-5 wordt toegevoegd zodra de voorwaarden voor het herverdelen van afgeleide tabellen bevestigd zijn.",
});

/* library v0.2: a nuclide whose capture below 1 MeV hinges on one engine setting ({n}: the factor at 30 keV) */
Object.assign(WT.L.ui, {
  dx_mf_pe_lo: "Onzekere modelkeuze: deze motor laat bij alle energieën een deeltje ontsnappen voordat de kern tot rust komt (pre-evenwichtsemissie), terwijl TALYS dat pas boven ongeveer 1 MeV doet; de TALYS-keuze geeft bij 30 keV ongeveer {n} keer minder vangst, en de 95%-band onder 1 MeV dekt beide.",
  dx_mf_pe_hi: "Onzekere modelkeuze: deze motor laat bij alle energieën een deeltje ontsnappen voordat de kern tot rust komt (pre-evenwichtsemissie), terwijl TALYS dat pas boven ongeveer 1 MeV doet; de TALYS-keuze geeft bij 30 keV ongeveer {n} keer meer vangst, en de 95%-band onder 1 MeV dekt beide.",
  dx_mf_pe_near: "Onzekere modelkeuze: deze motor laat bij alle energieën een deeltje ontsnappen voordat de kern tot rust komt (pre-evenwichtsemissie), terwijl TALYS dat pas boven ongeveer 1 MeV doet; de TALYS-keuze komt bij 30 keV overeen, maar wijkt elders onder 1 MeV meer dan een factor 2 af, en de 95%-band dekt daar beide.",
  dx_mf_fi_lo: "Onzekere modelkeuze: onder 1 MeV hangt deze curve af van één motorinstelling voor hoe de kern zijn splijtingsbarrières passeert; de andere keuze geeft bij 30 keV ongeveer {n} keer minder vangst, en de 95%-band onder 1 MeV dekt beide.",
  dx_mf_fi_hi: "Onzekere modelkeuze: onder 1 MeV hangt deze curve af van één motorinstelling voor hoe de kern zijn splijtingsbarrières passeert; de andere keuze geeft bij 30 keV ongeveer {n} keer meer vangst, en de 95%-band onder 1 MeV dekt beide.",
  dx_mf_fi_near: "Onzekere modelkeuze: onder 1 MeV hangt deze curve af van één motorinstelling voor hoe de kern zijn splijtingsbarrières passeert; de andere keuze komt bij 30 keV overeen, maar wijkt elders onder 1 MeV meer dan een factor 2 af, en de 95%-band dekt daar beide.",
  dx_mf_gg_lo: "Deze curve gebruikt een correctie op het gammaverval van de kern die TALYS en TENDL niet toepassen; zonder die correctie zou de vangst bij 30 keV ongeveer {n} keer kleiner zijn.",
  dx_mf_gg_hi: "Deze curve gebruikt een correctie op het gammaverval van de kern die TALYS en TENDL niet toepassen; zonder die correctie zou de vangst bij 30 keV ongeveer {n} keer groter zijn.",
  dx_mf_gg_near: "Deze curve gebruikt een correctie op het gammaverval van de kern die TALYS en TENDL niet toepassen; zonder die correctie zou de vangst bij 30 keV ongeveer gelijk zijn.",
});

/* pointwise library comparators below 1 keV and the measured thermal value (KONINGOVERLAY) */
Object.assign(WT.L.ui, {
  dx_eval_cmp: "geëvalueerde bibliotheek · vergelijking, niet INCOGNITA",
  dx_pw_leg2: "doorgetrokken onder 1 keV: puntsgewijs, 0 K",
  dx_lib_pw_dense: "Deze nuclide heeft veel resonanties onder 1 keV en houdt daarom meer punten: vijf per resonantiepiek, tot 5000 (met een vast budget van 500 zouden veel pieken van U-235 of Pu-239 worden afgekapt).",
  dx_pw_short: "puntsgewijs bij 0 K, onder 1 keV",
  dx_lib_pw: "Onder 1 keV worden dezelfde bibliotheken puntsgewijs getekend, als dunne doorgetrokken lijnen: gereconstrueerd bij 0 K (NJOY RECONR, tolerantie 0,01 %) en uitgedund tot hooguit {n} punten per kromme, zo gekozen dat de pieken en dalen van de resonanties blijven. Ook dit is alleen ter vergelijking: INCOGNITA heeft onder 1 keV geen kromme.",
  dx_below_cv: "onder 1 keV: geen INCOGNITA-kromme, alleen geëvalueerde bibliotheken en metingen",
  dx_below: "De eigen kromme van INCOGNITA begint bij 1 keV; daaronder staan alleen vergelijkingen en metingen.",
  dx_pw_tip: "geëvalueerde bibliotheken (vergelijking), puntsgewijs bij 0 K; geen INCOGNITA-kromme onder 1 keV",
  dx_th: "gemeten thermische waarde (EXFOR)",
  dx_th_sent: "Ruit: gemeten thermische vangstdoorsnede σγ(0,0253 eV)",
  dx_th_mean: "gewogen gemiddelde van {n} EXFOR-gegevens",
  dx_th_abs: "absorptie min splijting",
});
