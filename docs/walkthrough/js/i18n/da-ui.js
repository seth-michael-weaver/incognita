/* Danish: static page text (index.html data-i18n keys) and kit UI strings */
Object.assign(WT.L.ui, {
  lang_label: "Sprog", nav_teach: "Undervisere",
  brand: "Inde i en kernereaktion", nav_physics: "Fysikken", nav_data: "Alle nuklider", nav_board: "Resultattavle", menu: "Menu", site_nav: "Websted",
  ways_h: "Flere veje ind", ways_more: "Eller bliv ved med at scrolle: fysikken begynder her ↓",
  way1_k: "Udforsk", way1_t: "Alle nuklider", way1_p: "Forudsagte tværsnit for 6168 nuklider ved siden af hver kurateret måling. Søg efter en hvilken som helst isotop, og se alle datasæt.", way1_go: "Åbn dataene →",
  way2_k: "Sammenlign", way2_t: "Resultattavle", way2_p: "Hvordan motoren og dens dataprodukt klarer sig over for andre reaktionskoder og biblioteker, bedømt mod målinger, med nederlagene først.", way2_go: "Se resultaterne →",
  way3_k: "Kør den", way3_t: "Koden", way3_p: "Alt her er åbent. Klon repositoriet, slå en hvilken som helst kurve op, eller kør motoren selv.", way3_go: "GitHub →",
  title: "Inde i en kernereaktion",
  kicker: "En interaktiv forklaring af reaktionsmotoren INCOGNITA",
  h1: "Inde i en kernereaktion",
  hero1: "Skyd en neutron mod en atomkerne, og noget kommer ud igen. Det kan være neutronen selv, der preller af. Det kan være en proton, en alfapartikel (en tæt klump af 2 protoner og 2 neutroner) eller et glimt af lys. En tung kerne kan endda splitte i to.",
  hero2: "Hvad af det sker, og hvor ofte? Denne side gennemgår trin for trin, hvordan vores software besvarer det spørgsmål. Scroll ned, og prøv knapperne og skyderne undervejs. Billederne følger den samme fysik som motoren; tallene i dem er illustrative.",
  scrollcue: "Scroll for at begynde ↓",
  hero_tag: "Én neutron. Én kerne. Mange måder, det kan ende på.",
  hero_aud: "Til studerende og alle, der er nye i kernefysik, og til de undervisere, der underviser dem. Fagfolk: data for hver nuklid findes under <a href=\"data.html\" data-keep-lang>Alle nuklider</a>.",
  hero_fire: "Skyd en neutron",
  hero_hint: "eller klik et vilkårligt sted på billedet",
  credit_idx: "INCOGNITA-motoren er en portering af <a href=\"https://doi.org/10.1140/epja/s10050-023-01034-3\">TALYS-2</a> (A. J. Koning, S. Hilaire, S. Goriely) og bruger TALYS' database over kernestruktur. Det, INCOGNITA tilføjer, er <a href=\"#code\">listet, kontakt for kontakt, nederst på denne side</a>.",
  coda_h2: "Hvor det her findes i koden",
  coda_p1: "Hvert trin ovenfor er en pakke i <code>physics/hf</code>, og motoren kalder dem i den rækkefølge, du lige har læst dem. Motoren er en portering af TALYS-2.x, den veletablerede reaktionskode. Det, den tilføjer, ligger bag navngivne kontakter i de samme pakker: de fleste er slået fra som standard, nogle få rettelser er slået til, og hver enkelt kan for sig selv skiftes tilbage til almindelig TALYS.",
  coda_table: `
    <thead><tr><th>Kapitel</th><th>Hvad det gør</th><th>Kode</th></tr></thead>
    <tbody>
      <tr><td><a href="#structure">1</a></td><td>Masser, niveauer, deformation, resonansdata</td><td><code>structure/</code></td></tr>
      <tr><td><a href="#omp">2</a></td><td>Optisk model, transmissionskoefficienter (hvor let partikler kommer ind og ud)</td><td><code>omp/</code></td></tr>
      <tr><td><a href="#direct">3</a></td><td>Koblede kanaler, DWBA, kæmperesonanser, direkte indfangning (valgfri)</td><td><code>ecis/</code>, <code>direct/</code></td></tr>
      <tr><td><a href="#preeq">4</a></td><td>Præligevægt: excitonmodel, pickup og knockout, multipel emission</td><td><code>preeq/</code>, <code>density/particle_hole.py</code></td></tr>
      <tr><td><a href="#compound">5</a></td><td>Niveautætheder (tilstande pr. MeV), spinfordeling</td><td><code>density/</code></td></tr>
      <tr><td><a href="#decay">6</a></td><td>Valg af udgang (Hauser–Feshbach), breddefluktuationer</td><td><code>compound/</code></td></tr>
      <tr><td><a href="#gamma">7</a></td><td>Fotonstyrke og γ-transmission; diskrete niveauer og isomerer</td><td><code>gamma/</code><br><code>structure/levels.py</code></td></tr>
      <tr><td><a href="#cascade">8</a></td><td>Kaskaden af partikel- og γ-emissioner, eksklusive kanaler, restkerner</td><td><code>emission/</code></td></tr>
      <tr><td><a href="#fission">9</a></td><td>Fissionsbarrierer og transmission</td><td><code>fission/</code></td></tr>
      <tr><td><a href="#measure">11</a></td><td>Emissionsspektre, vinkelfordelinger og dobbeltdifferentielle tværsnit (valgfri, kun output)</td><td><code>specout.py</code><br><code>specang.py</code></td></tr>
      <tr><td><a href="#measure">11</a></td><td>Indfangning på termisk exciterede targetkerner og stellare rater (valgfri)</td><td><code>astro/stellar.py</code></td></tr>
      <tr><td><a href="#measure">11</a></td><td>Usikkerhed via mange tilfældige varianter (Total Monte Carlo)</td><td><code>tmc.py</code></td></tr>
      <tr><td></td><td>Styreprogrammet, der kører trinnene i rækkefølge, og valgfrie C-kerner for hastighedens skyld</td><td><code>engine.py</code><br><code>engine_c.py</code>, <code>native/</code></td></tr>
      <tr><td></td><td>Alle standardværdier og indstillinger, læst én gang ved start; også TENDL's tilpassede parametre pr. nuklid, anvendt sådan som TALYS anvender dem (valgfri)</td><td><code>input/</code></td></tr>
    </tbody>
  `,
  coda_h3_added: "Tilføjet ud over TALYS",
  coda_p_added: "Rækker markeret <b>Til</b> kører som standard, så en standardkørsel stemmer ikke længere præcist med TALYS; hver af dem kan slås tilbage med ét nøgleord eller én miljøvariabel. Resten er slået fra, medmindre de sættes.",
  coda_table_added: `
    <thead><tr><th>Kapitel</th><th>Hvad det ændrer</th><th>Kode</th></tr></thead>
    <tbody>
      <tr><td><a href="#cascade">8</a></td><td><b>Til.</b> Fluxregnskabet lukket: restkerner beholdt ned til 10⁻⁹ mb (TALYS: 10⁻³ mb), restkerner ét trin ud over TALYS' kaskadevindue beholdt, op til 8 af hver udsendt partikel i eksklusive kanaler, alle et niveaus gentagne henfaldsgrene talt med</td><td><code>emission/fluxclose.py</code><br><code>emission/channels.py</code><br><code>kevleak2.py</code></td></tr>
      <tr><td><a href="#decay">6</a></td><td><b>Til.</b> Det øverste interval i den første compoundkerne fyldes, sådan som primære fotoner fylder det (vægtet med E<sub>γ</sub>³), ikke jævnt</td><td><code>compound/nnleak.py</code></td></tr>
      <tr><td><a href="#decay">6</a></td><td><b>Til.</b> Ingen midlet compound-elastisk under de første resonanser (under 1 keV), hvor den elastiske del er potentialspredning</td><td><code>lowepot.py</code></td></tr>
      <tr><td><a href="#decay">6</a></td><td><b>Til.</b> Deformerede targetkerner uden fission: neutronudgange til niveauer uden for det koblede bånd bruger transmissionen fra koblede kanaler</td><td><code>compound/ccexitnb.py</code></td></tr>
      <tr><td><a href="#omp">2</a></td><td><b>Til.</b> Alfaemission ser et potential, der afhænger af restkernens temperatur; alfaprojektiler kommer ind via alfamodel 6; triton- og helionpotentialer medtager projektilets størrelse</td><td><code>omp/alphatemp.py</code><br><code>alphaentr.py</code><br><code>omp/tfold.py</code></td></tr>
      <tr><td><a href="#fission">9</a></td><td><b>Til.</b> Eksakt endimensional transmission gennem hver pukkel i barrieren</td><td><code>fission/wkb.py</code></td></tr>
      <tr><td><a href="#gamma">7</a></td><td><b>Til.</b> Styrkefaktorer for E1/M1 pr. kerne, hvor en kørsel angiver dem, erstattes af én global funktion af deformationen</td><td><code>gamma/ftglobal.py</code></td></tr>
      <tr><td><a href="#compound">5</a></td><td><b>Til.</b> Targets uden deres egen målte resonansafstand D₀: targetets niveautæthed i kontinuet over max(E<sub>cut</sub> + 2, S<sub>n</sub> − 6) MeV hæves med en faktor fra én global regel ud fra paritet, skaller og deformation. Tilføjet for at gøre nederlaget i (n,p) nær tærsklen over for TALYS-2’s standardinput til uafgjort; den gør nogle få visninger af indfangning, (n,2n) og (n,α) en smule dårligere, en accepteret og registreret skade</td><td><code>density/npwindow.py</code></td></tr>
      <tr><td><a href="#gamma">7</a></td><td>En stærkere saksetilstand i deformerede kerner, fra nyere systematik, der stemmer med Oslo-målinger (omkring 4–5× i aktinider); eller en variant, der skalerer dens energi og styrke med deformationen</td><td><code>gamma/scissors.py</code></td></tr>
      <tr><td><a href="#gamma">7</a></td><td>Fotonstyrken skaleret, så hver kerne rammer sin målte strålingsstyrke ⟨Γγ⟩/D₀, for alle kerner i kaskaden, ikke kun den første</td><td><code>gamma/ggnorm.py</code></td></tr>
      <tr><td><a href="#gamma">7</a></td><td>Stærkere saksetilstand og ⟨Γγ⟩-normering kun for de tungeste kerner (Z ≥ 88), rettet mod indfangning ved keV-energier</td><td><code>gamma/actphys.py</code></td></tr>
      <tr><td><a href="#gamma">7</a></td><td>Vores egen E1-breddekonstant i stedet for TALYS' tabel afledt af TENDL (den medfølgende opskrift uden data sætter den)</td><td><code>gamma/e1_width.py</code></td></tr>
      <tr><td><a href="#gamma">7</a></td><td>Kollektiv E2-styrke fra rotationsbånd i kvasikontinuet</td><td><code>gamma/isoe2.py</code></td></tr>
      <tr><td><a href="#omp">2</a></td><td>En regional justering af den optiske brønd for deformerede targetkerner blandt de sjældne jordarter, tilpasset målte S₀ og S₁ uden indfangningsdata</td><td><code>omp/regional.py</code></td></tr>
      <tr><td><a href="#omp">2</a></td><td>Målte neutronstyrkefunktioner S₀, S₁ fastlægger neutrontransmissionen ved lav energi</td><td><code>omp/sfunc.py</code></td></tr>
      <tr><td><a href="#direct">3</a></td><td>Direkte indfangning i bundne baner, med en rettelse af originalen: i standard-TALYS giver den nul, medmindre alle output fra den optiske model også bestilles</td><td><code>direct/racapcalc.py</code></td></tr>
      <tr><td><a href="#direct">3</a></td><td>Targetkernens koblingsskema (rotor, vibrator, sfærisk) valgt ud fra dens målte niveauer</td><td><code>structure/collrule.py</code></td></tr>
      <tr><td><a href="#structure">1</a></td><td>Kontinuet begynder, hvor det målte niveauskema holder op med at være komplet</td><td><code>structure/levcomplete.py</code></td></tr>
      <tr><td><a href="#structure">1</a></td><td>Et niveau, hvis listede spin er umuligt for dets kerne (heltalligt ved ulige A), behandles som et niveau med ukendt spin</td><td><code>structure/levjpar.py</code></td></tr>
      <tr><td><a href="#compound">5</a></td><td>Niveautæthed med konstant temperatur forankret i den komplette del af de diskrete niveauer</td><td><code>density/ctwindow2.py</code></td></tr>
      <tr><td><a href="#fission">9</a></td><td>Rotationsbånd af overgangstilstande ved fissionens sadelpunkter</td><td><code>fission/barriers.py</code></td></tr>
      <tr><td><a href="#resonance">10</a></td><td>Indfangning, hvor kun få resonanser falder i det stellare vindue: den typiske værdi for én resonansstige i stedet for gennemsnittet</td><td><code>fewres.py</code></td></tr>
      <tr><td></td><td>Fire sikkerhedsværn langt fra stabilitet: direkte flux begrænset af unitaritet, en grænse for Fermienergien, ingen standardkollektivitet for ulige-ulige kerner, præligevægtens spinfordeling normeret</td><td><code>engphys.py</code></td></tr>
    </tbody>
  `,
  coda_h3_outside: "Uden for motoren",
  coda_p_outside: "Nogle dele af historien kører ved siden af motoren i stedet for inde i den. De statistiske resonansstiger fra <a href=\"#resonance\">kapitel 10</a> ligger i <code>physics/resonance/</code>. De maxwellske middelværdier (MACS) fra <a href=\"#measure\">kapitel 11</a> foldes ud fra motorens indfangningskurver efter kørslen, i <code>validation/differential/core.py</code>; indfangning på termisk exciterede targetkerner og den stellare rate kommer derimod fra motoren selv (<code>astro/stellar.py</code>, valgfri). Forankringslaget fra <a href=\"#layers\">kapitel 12</a> ligger i <code>incognita/terra/</code>.",
  close: "Luk",
  chapters: "Kapitler",
  nav_board: "Resultattavle", nav_data_short: "Data",
  coda_repo: "Koden, biblioteket og de kuraterede målinger er åbne: <a href=\"https://github.com/seth-michael-weaver/incognita\">seth-michael-weaver/incognita på GitHub</a>. Du kan selv slå enhver forudsigelse op på siden <a href=\"data.html?lang=da\" data-keep-lang>Alle nuklider</a> eller klone repositoriet og køre det.",
  diagram: "Diagram",
});

Object.assign(WT.L.ui, { pause_sweep: "Sæt gennemløbet på pause", play_sweep: "Genoptag gennemløbet" });

/* course mode: audience note, chapter level tags, per-step links */
Object.assign(WT.L.ui, {
  audience: '<b>Hvem det er til:</b> alle, der er nysgerrige. De første kapitler kræver ingen fysik; de senere går helt op på forskningsniveau. Hvert kapitel har et mærke: <span class="lvl l0">Intro</span>, <span class="lvl l1">Mellem</span> eller <span class="lvl l2">Avanceret</span>. Vil du bruge det i undervisningen? Se <a href="instructors.html" data-keep-lang>vejledningen for undervisere</a>.',
  lvl0: "Intro", lvl1: "Mellem", lvl2: "Avanceret", lvl_title: "Niveau",
  step_link: "Kopiér et link til dette trin", link_copied: "Link kopieret",
});
