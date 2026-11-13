/* Danish: data explorer (data.html, js/data.js) */
Object.assign(WT.L.ui, {
  lang_label: "Sprog", nav_teach: "Undervisere",
  brand: "Inde i en kernereaktion", nav_physics: "Fysikken", nav_data: "Alle nuklider", nav_board: "Sammenligninger", menu: "Menu", site_nav: "Websted",
  dx_title: "Alle nuklider · Inde i en kernereaktion",
  site_nav: "Websted", nav_walk: "Gennemgangen", nav_board: "Sammenligninger", nav_data: "Alle nuklider", nav_repo: "Kode på GitHub",
  dx_kicker: "INCOGNITA · dataudforsker",
  dx_h1: "Alle nuklider",
  dx_lede: "Motorens forudsagte neutrontværsnit for hver nuklid i biblioteket, ved siden af de kuraterede målinger af hver nuklid. Vælg en nuklid på kortet, eller søg efter en.",
  dx_lede_ver: "Kurverne er biblioteket v0.2.3 (november 2026), lavet med den samme motorversion, som scores på siden Sammenligninger (motoren fra 22. oktober 2026). De er ikke TERRA, dataproduktet på den side, der er tilpasset målinger. Hver kurve er motorens egen forudsigelse: ingen er tilpasset de målinger, der vises ved siden af, bortset fra at en nuklid markeret som forankret har sin kurve skaleret med én faktor, så dens stellare gennemsnit ved 30 keV svarer til den målte værdi. Motorens generelle indstillinger blev valgt én gang for alle nuklider ud fra mange målinger (også disse), så overensstemmelse for en målt nuklid er en rimelig test af modellen, men ikke en helt uafhængig. De fleste nuklider er aldrig blevet målt (ekstrapolerede), og deres bånd er brede.",
  dx_controls: "Kortets knapper", dx_search_label: "Find en nuklid", dx_search_ph: "Søg: U-235, Fe56, Au…",
  dx_colour: "Farv kortet efter", dx_m_tier: "Hvordan den kendes", dx_m_macs: "Indfangning ved 30 keV", dx_m_meas: "Målte data",
  dx_chart_h: "Nuklidkort",
  dx_chart_aria: "Nuklidkort: protoner opad, neutroner mod højre. Brug søgefeltet til at vælge en nuklid.",
  dx_hint: "Træk for at panorere, scroll eller knib for at zoome. Klik på et felt for at åbne det: nuklidets detaljer vises under kortet. Protoner opad, neutroner mod højre.",
  dx_full: "Vis hele energiområdet", dx_mk_thr: "tærskel", dx_mk_cb: "Coulombbarriere",
  dx_show_excl: "Vis punkter, som kurateringen udelukkede", dx_table: "Vis som tabel",
  dx_run_h: "Få disse tal selv", dx_copy: "Kopiér", dx_copied: "Kopieret",
  dx_repo_h: "Kør det selv",
  dx_repo_p: "Alt på denne side kommer fra det åbne repositorium: motoren, biblioteket og de kuraterede målinger. Du skal bruge Linux eller macOS, Python 3.12 og <a href=\"https://docs.astral.sh/uv/\">uv</a>.",
  credit_sub: "INCOGNITA-motoren er en portering af <a href=\"https://doi.org/10.1140/epja/s10050-023-01034-3\">TALYS-2</a> (A. J. Koning, S. Hilaire, S. Goriely) og bruger TALYS' database over kernestruktur. Det, INCOGNITA tilføjer, er <a href=\"./?lang=da#code\" data-keep-lang>listet, kontakt for kontakt, nederst på undervisningssiden</a>.",
  dx_repo_p2: "For at køre selve motoren skal du også have TALYS' strukturdatabase; README-filen forklarer, hvordan du henter den.",
  dx_repo_link: "seth-michael-weaver/incognita på GitHub →",
  dx_src: "Kilder: forudsigelser fra v0.2.3-biblioteket (<code>library/v0.2.3</code>); indfangningsmålinger fra EXFOR som kurateret i <code>data/curation</code>; (n,2n)-, (n,p)- og (n,α)-målinger fra benchmarkrækkerne i <code>incognita/bench</code> (under Z 26: EXFOR-rækker udvalgt efter de samme regler, <code>data/curation/inputs</code>). Målinger, som kurateringen udelukkede, er skjult, medmindre du beder om dem. Det valgfri stiplede overlag med evaluerede biblioteker (ENDF/B-VIII.1, JEFF-4.0, TENDL-2025) bygges af <code>scripts/build_site_overlay.py</code> udelukkende til visning; INCOGNITA læser det aldrig.",
  dx_t0: "Målt", dx_t1: "Forankret i en målt MACS", dx_t2: "Interpoleret (tæt på målte nuklider)", dx_t3: "Ekstrapoleret",
  dx_ts0: "målt", dx_ts1: "forankret", dx_ts2: "interpoleret", dx_ts3: "ekstrapoleret",
  dx_keep: "beholdt", dx_down: "nedvægtet", dx_excl: "udelukket", dx_fix: "enhed rettet",
  dx_cap: "Indfangning (n,γ)", dx_macs: "Stellart gennemsnit (MACS)", dx_nat: "naturlig",
  dx_l_cap: "indfangning målt", dx_l_thr: "kun (n,2n), (n,p) eller (n,α) målt", dx_l_none: "ingen måling i dette sæt",
  dx_l_macs: "forudsagt maxwellsk midlet indfangning ved kT = 30 keV (logaritmisk skala)", dx_l_nomacs: "ingen værdi",
  dx_capsets: "indfangningsdatasæt", dx_measured: "Målt",
  dx_outside: "uden for det validerede område (Z 26–83)", dx_flag: "opløste resonanser når ind i MACS-vinduet: foretræk en målt MACS",
  dx_nocurve: "ingen bibliotekskurve for denne post; målingerne kommer fra",
  dx_xE: "neutronenergi", dx_pred: "forudsigelse (bibliotek v0.2.3)",
  dx_res: "opløste resonanser: kurven er her et gennemsnit",
  dx_empty: "Intet at vise for denne reaktion.", dx_bands: "bånd: 68 % og 95 %", dx_band68: "bånd: 68 %",
  dx_meas_pts: "målt", dx_table_hint: "Brug »Vis som tabel« for at se værdierne.", dx_ds_h: "Målinger", dx_pts: "pkt.",
  dx_th_src: "Kilde", dx_th_val: "Værdi", dx_th_unc: "Område / usikkerhed", dx_th_cur: "Kuratering",
  dx_s_p: "protoner", dx_s_n: "neutroner", dx_s_macs: "indfangning i en stjerne ved 30 keV", dx_s_pts: "målte indfangningspunkter", dx_s_thr: "(n,2n)-, (n,p)-, (n,α)-punkter", dx_sets: "datasæt",
  dx_exfor_click: "klik på punktet for at åbne", dx_exfor_tap: "tryk igen, eller her, for at åbne",
  dx_mxw: "maxwellsk gennemsnit", dx_state: "tilstand", dx_cur: "kuratering", dx_fail: "Dataene kunne ikke indlæses.", dx_loading: "Indlæser", dx_nload: "Denne nuklid kunne ikke indlæses.", dx_retry: "Prøv igen",
});

/* downloads and data access */
Object.assign(WT.L.ui, {
  dx_dl: "Download denne nuklid:",
  dx_dl_note: "Alle kurver og målte punkter for denne nuklid, alle reaktioner, med enheder, kilder og EXFOR-id'er skrevet ind i filen.",
  dx_access: "<b>Adgang til data.</b> Alt, hvad der vises her, ligger i repositoriet under <a href=\"https://github.com/seth-michael-weaver/incognita/tree/main/library/v0.2.3\"><code>library/v0.2.3</code></a>: indfangningskurver med 68 / 95 %-bånd (<code>capture_v023.parquet</code>), maxwellske gennemsnit (<code>macs30_v023.csv</code>, <code>macs_kt_v023.csv</code>), stellare rater (<code>rates_v023.csv</code>, <code>reaclib_v023.dat</code>) og kanalerne (n,2n), (n,p), (n,α) (<code>channels_v023.parquet</code>, <code>grid_np_v023.parquet</code>), kontrolleret med <code>SHA256SUMS</code>. For en enkelt nuklid er CSV- og JSON-downloadene ovenfor nok. De kuraterede målinger ligger i <code>data/curation</code>; de stammer fra EXFOR (IAEA's Nuclear Data Section) og beholder deres EXFOR-id'er. Biblioteksdataene er CC-BY-4.0. Den tidligere version v0.1 bliver i <code>library/v0.1</code>; <code>CHANGELOG.md</code> i <code>library/v0.2.3</code> fortæller, hvad der er ændret.",
});
Object.assign(WT.L.ui, {
  dx_lib: "Læg evaluerede biblioteker ovenpå (kun til sammenligning — bruges ikke af INCOGNITA)",
  dx_eval: "evaluering", dx_lib_pd: "offentligt domæne (USA)", dx_lib_loading: "Indlæser bibliotekerne…",
  dx_lib_bin: "biblioteker: intervalgennemsnit",
  dx_lib_note: "De stiplede linjer er evaluerede kernedatabiblioteker, vist kun til sammenligning: INCOGNITA bruger dem ikke, og de er ikke med i downloadene. Hvert bibliotek rekonstrueres ved 0 K ud fra bibliotekets ENDF-6-fil (NJOY) og midles over de samme energiintervaller som kurven (gennemsnit i logaritmen af energien, så resonanserne udglattes); MACS bruger den fulde punktvise kurve.",
  dx_lib_none: "Ingen fil for denne nuklid i", dx_lib_notab: "Ingen separat værdi for denne reaktion i",
  dx_lib_held: "JENDL-5 tilføjes, når dets betingelser for at videredistribuere afledte tabeller er bekræftet.",
});

/* library v0.2.3: a nuclide whose capture below 1 MeV hinges on one engine setting ({n}: the factor at 30 keV) */
Object.assign(WT.L.ui, {
  dx_mf_pe_lo: "Usikkert modelvalg: denne motor lader ved alle energier en partikel slippe ud, før kernen falder til ro (præligevægtsemission), mens TALYS først gør det over omkring 1 MeV; TALYS-valget giver omkring {n} gange mindre indfangning ved 30 keV, og 95 %-båndet under 1 MeV dækker begge.",
  dx_mf_pe_hi: "Usikkert modelvalg: denne motor lader ved alle energier en partikel slippe ud, før kernen falder til ro (præligevægtsemission), mens TALYS først gør det over omkring 1 MeV; TALYS-valget giver omkring {n} gange mere indfangning ved 30 keV, og 95 %-båndet under 1 MeV dækker begge.",
  dx_mf_pe_near: "Usikkert modelvalg: denne motor lader ved alle energier en partikel slippe ud, før kernen falder til ro (præligevægtsemission), mens TALYS først gør det over omkring 1 MeV; TALYS-valget stemmer ved 30 keV, men afviger mere end en faktor 2 andre steder under 1 MeV, og 95 %-båndet dækker dér begge.",
  dx_mf_fi_lo: "Usikkert modelvalg: under 1 MeV afhænger denne kurve af én motorindstilling for, hvordan kernen passerer sine fissionsbarrierer; det andet valg giver omkring {n} gange mindre indfangning ved 30 keV, og 95 %-båndet under 1 MeV dækker begge.",
  dx_mf_fi_hi: "Usikkert modelvalg: under 1 MeV afhænger denne kurve af én motorindstilling for, hvordan kernen passerer sine fissionsbarrierer; det andet valg giver omkring {n} gange mere indfangning ved 30 keV, og 95 %-båndet under 1 MeV dækker begge.",
  dx_mf_fi_near: "Usikkert modelvalg: under 1 MeV afhænger denne kurve af én motorindstilling for, hvordan kernen passerer sine fissionsbarrierer; det andet valg stemmer ved 30 keV, men afviger mere end en faktor 2 andre steder under 1 MeV, og 95 %-båndet dækker dér begge.",
  dx_mf_gg_lo: "Denne kurve bruger en korrektion af kernens gammahenfald, som TALYS og TENDL ikke anvender; uden den ville indfangningen ved 30 keV være omkring {n} gange mindre.",
  dx_mf_gg_hi: "Denne kurve bruger en korrektion af kernens gammahenfald, som TALYS og TENDL ikke anvender; uden den ville indfangningen ved 30 keV være omkring {n} gange større.",
  dx_mf_gg_near: "Denne kurve bruger en korrektion af kernens gammahenfald, som TALYS og TENDL ikke anvender; uden den ville indfangningen ved 30 keV være omtrent den samme.",
});

/* pointwise library comparators below 1 keV and the measured thermal value (KONINGOVERLAY) */
Object.assign(WT.L.ui, {
  dx_eval_cmp: "evalueret bibliotek · sammenligning, ikke INCOGNITA",
  dx_pw_leg2: "fuldt optrukket under 1 keV: punktvis, 0 K",
  dx_lib_pw_dense: "Denne nuklid har mange resonanser under 1 keV og beholder derfor flere punkter: fem pr. resonanstop, op til 5000 (med et fast budget på 500 ville mange toppe i U-235 eller Pu-239 blive skåret af).",
  dx_pw_short: "punktvis ved 0 K, under 1 keV",
  dx_lib_pw: "Under 1 keV tegnes de samme biblioteker punktvis som tynde, fuldt optrukne linjer: rekonstrueret ved 0 K (NJOY RECONR, tolerance 0,01 %) og udtyndet til højst {n} punkter pr. kurve, valgt så resonansernes toppe og dale bevares. De er også kun til sammenligning: INCOGNITA har ingen kurve under 1 keV.",
  dx_below_cv: "under 1 keV: ingen INCOGNITA-kurve, kun evaluerede biblioteker og målinger",
  dx_below: "INCOGNITAs egen kurve begynder ved 1 keV; derunder vises kun sammenligninger og målinger.",
  dx_pw_tip: "evaluerede biblioteker (sammenligning), punktvis ved 0 K; ingen INCOGNITA-kurve under 1 keV",
  dx_th: "målt termisk værdi (EXFOR)",
  dx_th_sent: "Rombe: målt termisk indfangningstværsnit σγ(0,0253 eV)",
  dx_th_mean: "vægtet gennemsnit af {n} EXFOR-poster",
  dx_th_abs: "absorption minus fission",
});

/* INCOGNITA's own capture below 1 keV */
Object.assign(WT.L.ui, {
  dx_rr_b1k: "Under 1 keV",
  dx_rr_own: "INCOGNITAs egen resonanstilpasning til målte data (op til 300 eV; statistiske resonanser fra 300 eV til 1 keV)",
  dx_rr_stat: "statistiske resonanser ud fra INCOGNITAs egne gennemsnitlige parametre, ikke de målte resonanser: toppenes placering er én tilfældig stikprøve; over mange nuklider ligger resonansintegralet typisk inden for en faktor 2 af målingen",
  dx_rr_anch: "; går gennem den målte termiske indfangning",
  dx_rr_sm_a: "INCOGNITAs glatte skøn gennem den målte termiske indfangning; ingen resonanser tegnet",
  dx_rr_sm: "INCOGNITAs glatte skøn; de rigtige termiske værdier kan afvige med flere størrelsesordener",
  dx_rr_k_own: "egen resonanstilpasning",
  dx_rr_k_stat: "statistiske resonanser (ikke de rigtige toppe)",
  dx_rr_k_sm: "glat skøn (uden resonanser)",
  dx_below_rr: "under 1 keV: INCOGNITAs {k}",
  dx_below_own: "Under 1 keV er den fuldt optrukne linje INCOGNITAs egen resonanstilpasning til målte indfangningsdata op til 300 eV; fra 300 eV til 1 keV bruger den statistiske resonanser. Ved 1 keV møder den forudsigelsen.",
  dx_below_stat: "Under 1 keV er streg-prik-linjen INCOGNITAs statistiske skøn: resonanser med INCOGNITAs egen gennemsnitlige afstand og bredder, placeret tilfældigt, så de enkelte toppe passer ikke med de rigtige. Testet på nuklider, hvis resonansintegral ikke blev brugt i tilpasningen, lå det typisk inden for en faktor 2 af målingen og ikke bedre: medianafvigelse ×1,9, 54 % inden for ×2.",
  dx_below_sm_a: "Under 1 keV er den prikkede linje INCOGNITAs glatte skøn: en 1/v-kurve gennem den målte termiske indfangning, forbundet med værdien ved 1 keV. Der er ikke tegnet resonanser, så mellem ca. 1 eV og 1 keV kan det rigtige tværsnit være langt højere i sine toppe.",
  dx_below_sm: "Under 1 keV er den prikkede linje INCOGNITAs glatte skøn: værdien ved 1 keV forlænget som 1/v, uden resonanser og uden en måling, der fastlægger den. De rigtige termiske værdier kan afvige fra den med flere størrelsesordener.",
  dx_below_anch: "Den er tvunget gennem en målt termisk indfangningsværdi, {v} b.",
  dx_rr_anch_diff: "Ruden er et separat gennemsnit af EXFOR-poster og afviger fra den.",
  dx_rr_ri: "Resonansintegral for indfangning over 0,5 eV for denne nuklide: INCOGNITA {m} b, målt {e} b.",
  dx_rr_ri_used: "Den målte værdi blev brugt til at vælge denne tilfældige stikprøve, så overensstemmelsen er ikke en test.",
  dx_rr_ri_hold: "Den målte værdi blev ikke brugt til at lave denne kurve.",
  dx_pw_tip_rr: "evaluerede biblioteker (til sammenligning), punktvis ved 0 K",
  dx_lib_pw_rr: "Under 1 keV tegnes de samme biblioteker punktvis som tynde, fuldt optrukne linjer: rekonstrueret ved 0 K (NJOY RECONR, tolerance 0,01 %) og udtyndet til højst {n} punkter pr. kurve, valgt så resonansernes toppe og dale bevares. De er også kun til sammenligning, ikke INCOGNITA.",
  dx_tr_h: "Hvor meget man kan stole på dette",
  dx_tr_t0: "Målt kerne. Kurven er stadig motorens egen forudsigelse, ikke tilpasset disse målinger; men motorens globale indstillinger blev valgt ud fra mange kerner, også denne, så overensstemmelse her er et tjek, ikke en uafhængig test.",
  dx_tr_t1: "Forankret. Motorens kurve er skaleret med én faktor til et målt stellart gennemsnit ved 30 keV, så formen er stadig modellens. Niveauet, bevaret fra v0.1, betyder at biblioteket ikke havde målte indfangningstværsnit for kernen; eventuelle kuraterede målinger vist nedenfor er ikke brugt til kurven.",
  dx_tr_t2: "Interpoleret. Ikke målt, men højst to neutroner eller protoner fra målte kerner; kurven er modellens forudsigelse.",
  dx_tr_t3: "Ekstrapoleret. Ikke målt og ikke i bibliotekets interpolerede niveau (det kræver også strukturdata, og reglen udelader nogle kerner lige ved siden af målte): kurven er modellen alene, uden en måling at tjekke den mod.",
  dx_t4: "Ikke målt (Z < 26)", dx_t5: "Målt (bibliotekets niveau ikke opdateret)", dx_ts4: "ikke målt", dx_ts5: "målt", dx_t6: "Målt (Z < 26)", dx_ts6: "målt",
  dx_tr_t4: "Ikke målt. Ingen kurateret indfangningsmåling af denne kerne: ingen i EXFOR, eller kurateringen udelukkede dem alle. Kurven er modellen alene. Under Z ≈ 20 går indfangning gennem enkelte resonanser, som denne statistiske motor ikke beskriver: læs kurven som et groft skøn.",
  dx_tr_t5: "Målt kerne. Biblioteket angiver den stadig som interpoleret eller ekstrapoleret (niveauet er bevaret fra v0.1), men der findes kuraterede indfangningsmålinger, vist nedenfor. Kurven er motorens egen forudsigelse, ikke tilpasset dem, så en sammenligning er en test af modellen.",
  dx_tr_t6: "Målt kerne. Kuraterede EXFOR-indfangningsmålinger vises nedenfor (samme automatiske kuratering som fra Z 26 og op; ingen person har gennemgået dens afgørelser for disse lette kerner). Kurven er motorens forudsigelse, ikke tilpasset dem. Under Z ≈ 20 går indfangning gennem enkelte resonanser, som denne statistiske motor ikke beskriver: læs kurven som et groft skøn.",
  dx_tr_out: "Uden for Z 26–83, det område bibliotekets validering dækker.",
  dx_tr_mf: "Modelform-flag: én indstilling i motoren ændrer indfangningen her med mere end en faktor 2 (se noten ovenfor). Ingen måling kan afgøre valget mellem de to; båndene under 1 MeV er gjort bredere, så de rummer begge.",
  dx_tr_mf_gg: "Modelform-flag: værdien bygger på motorens rettelse af en manglende gamma-henfaldsbredde (se noten ovenfor); båndet er ikke gjort bredere for det.",
  dx_tr_b_ok: "båndene dækker som angivet (snarere brede)",
  dx_tr_b_unm: "båndene er kun tjekket på målte kerner, ikke på kerner som denne",
  dx_tr_b_narrow: "båndet er sandsynligvis for smalt: det dækkede for lidt",
  dx_tr_b_none: "intet bånd vist",
  dx_tr_b_macs: "båndet er ikke tjekket for sig",
  dx_tr_e: "sammenligningsfejl typisk ×{f} ({n} målte kerner, Z {z}; udviklingssammenligning)",
  dx_tr_e_none: "ingen sammenligning med målinger for dette område",
  dx_tr_src: "Niveau og flag: README for library/v0.2. Bånd: et dækningstjek mod målinger (5 testkerner, oktober 2026), hvor båndene for indfangning, fission og elastisk spredning dækkede som angivet, og tærskelkanalerne og det totale tværsnit dækkede for lidt. Fejl: siden <a href=\"scoreboard.html\" data-keep-lang>Sammenligninger</a>, kvadratisk gennemsnit af log10(motor / målt); den er ikke en uafhængig test, fordi motorens regler blev valgt med blik på den.",
});
// less text (2026-11-06)
Object.assign(WT.L.ui, { dx_hint2: "Træk for at flytte · rul for at zoome · klik på et felt", dx_more_nuc: "Detaljer: hvor meget man kan stole på det, kilder, kode", dx_about: "Om dataene, downloads og kode" });
Object.assign(WT.L.ui, { dx_cmp: "til sammenligning" });
// R-matrix evaluation (light nuclei)
Object.assign(WT.L.ui, {"dx_el": "Elastisk (n,n)", "dx_rm_name": "INCOGNITA R-matrix-evaluering", "dx_rm_h": "Vores model for denne kerne", "dx_rm_what": "Elastisk spredning af neutroner på kulstof-12 fra INCOGNITAs egen R-matrix-tilpasning med flere niveauer til målte EXFOR-data for det totale og det elastiske tværsnit. Før offentliggørelsen bestod den kontroller fastlagt på forhånd: IAEA’s kulstofstandard, målinger af det totale tværsnit uden for tilpasningen, en NJOY-behandlingsrunde og en grafit-kritikalitetsbenchmark (PCI-001).", "dx_rm_range": "Energiområde: {lo} til {hi}; ingen INCOGNITA-kurve derover.", "dx_rm_caveat": "Forbehold: χ²/frihedsgrad i stikprøven {c}; to hældende datasæt markeret; kontrollerne er kalibrerede men har lav statistisk styrke.", "dx_rm_nocap": "Indfangning modelleres ikke: fanen indfangning viser kun målinger.", "dx_rm_report": "Læs rapporten"});
// measured resonances below 1 keV + energy-band strip (2026-11-07)
Object.assign(WT.L.ui, { "dx_rr_meas": "resonanser målt af eksperimentatorer (EXFOR-resonansparametre), samlet af INCOGNITA; spin, strålingsbredder og svage niveauer, der ikke er målt, kommer fra INCOGNITAs egen statistik", "dx_rr_own_t": "INCOGNITAs egen Reich–Moore-resonanstilpasning til målte EXFOR-transmissionsdata, fra 10 µeV til 1 keV; ikke en biblioteksfil", "dx_rr_k_meas": "målte resonanser (EXFOR-parametre)", "dx_below_meas": "Under 1 keV bruger den fuldt optrukne linje resonansenergier og -bredder, som eksperimentatorer har målt og rapporteret i EXFOR, slået sammen på tværs af eksperimenter; den er ikke en tilpasning lavet af INCOGNITA. Hvor et spin eller en strålingsbredde ikke er målt, leverer INCOGNITAs egen statistik værdien, og svage niveauer, som eksperimenterne ikke kunne se, tilføjes statistisk (deres placeringer er ikke forudsigelser). Ved 1 keV går den over i forudsigelsen.", "dx_below_own_t": "Under 1 keV er den fuldt optrukne linje INCOGNITAs egen Reich–Moore-resonanstilpasning til målte EXFOR-transmissionsdata. Ved 1 keV går den over i forudsigelsen. Noten ved nukliden fortæller, hvilke datasæt der er brugt, og hvordan tilpasningen klarer sig over for data, der ikke indgik i tilpasningen.", "dx_band_th": "termisk", "dx_band_th_s": "termisk", "dx_band_th_x": "term.", "dx_band_rr": "resonanser", "dx_band_rr0": "resonansområde", "dx_band_rr_s": "resonanser", "dx_band_rr_x": "res.", "dx_band_ur": "midlede resonanser", "dx_band_ur_s": "midlet", "dx_band_ur_x": "midl.", "dx_band_f": "hurtig", "dx_band_f_s": "hurtig", "dx_band_f_x": "hurtig", "dx_band_all": "alle energier" });

/* site menu: 'More Nuclear Topics' link (nav.js), also on pages that do not load the ui file */
Object.assign(WT.L.ui, { nav_topics: "Flere nukleare emner" });

/* C-12 elastic tab: natural-carbon curve, unfitted totals, IAEA standard, ENDF/B-VIII.1 comparator */
Object.assign(WT.L.ui, {"dx_rm_natc": "INCOGNITA R-matrix, naturligt kulstof", "dx_rm_cmp": "Her er kurven naturligt kulstof, ligesom målingerne og standarden: 98,93 % af INCOGNITAs C-12 plus 1,07 % C-13 fra ENDF/B-VIII.1, som giver den smalle top ved 153 keV; kurven for rent C-12 ligger i downloads. Den stemmer med IAEA-neutronstandarden 2017 inden for {dev} % (største |z| {z}); på de totale tværsnit, der ikke indgik i tilpasningen, er χ²/N = {chi}; alle kontroller bestået. EXFOR {set} ligger {off} % under både INCOGNITA og ENDF/B-VIII.1: en forskydning i det datasæts normering.", "dx_ho": "målte totale tværsnit uden for tilpasningen, natC", "dx_ho_tip": "ikke brugt i tilpasningen: først sammenlignet efter den endelige tilpasning", "dx_bin": "midlet i logaritmiske energiintervaller", "dx_bin_tip": "middel af {n} ikke-tilpassede målepunkter ± dets standardfejl", "dx_std": "IAEA-neutronstandard 2017 (natC elastisk)", "dx_std_dev": "INCOGNITA / standard − 1", "dx_lib_el": "Stiplet linje: ENDF/B-VIII.1 elastisk for naturligt kulstof (98,93 % C-12 + 1,07 % C-13), punktvis ved 0 K, kun til sammenligning: INCOGNITA bruger den ikke, og den er ikke i downloads."});
