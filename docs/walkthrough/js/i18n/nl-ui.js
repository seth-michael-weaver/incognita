/* Dutch (Nederlands): static page text (index.html data-i18n keys) and kit UI strings */
Object.assign(WT.L.ui, {
  lang_label: "Taal", nav_teach: "Docenten",
  brand: "Binnen in een kernreactie", nav_physics: "De natuurkunde", nav_data: "Alle nucliden", nav_board: "Scorebord", menu: "Menu", site_nav: "Site",
  ways_h: "Meer manieren om te beginnen", ways_more: "Of scrol gewoon verder: de natuurkunde begint hier ↓",
  way1_k: "Verken", way1_t: "Alle nucliden", way1_p: "Voorspelde werkzame doorsneden voor 6168 nucliden naast elke gecureerde meting. Zoek elk isotoop op en bekijk elke dataset.", way1_go: "Open de data →",
  way2_k: "Vergelijk", way2_t: "Scorebord", way2_p: "Hoe de motor en zijn dataproduct zich verhouden tot andere reactiecodes en bibliotheken, beoordeeld aan de hand van metingen, met de nederlagen voorop.", way2_go: "Bekijk de scores →",
  way3_k: "Draai het zelf", way3_t: "De code", way3_p: "Alles hier is open. Kloon de repository, zoek elke curve op of draai de motor zelf.", way3_go: "GitHub →",
  title: "Binnen in een kernreactie",
  kicker: "Een interactieve uitleg van de reactiemotor INCOGNITA",
  h1: "Binnen in een kernreactie",
  hero1: "Schiet een neutron op een atoomkern af en er komt iets terug naar buiten. Dat kan het neutron zelf zijn, dat terugkaatst. Het kan een proton zijn, een alfadeeltje (een compact groepje van 2 protonen en 2 neutronen) of een lichtflits. Een zware kern kan zelfs in tweeën splijten.",
  hero2: "Welke van deze dingen gebeurt er, en hoe vaak? Deze pagina laat stap voor stap zien hoe onze software die vraag beantwoordt. Scrol naar beneden en probeer onderweg de knoppen en schuifjes uit. De afbeeldingen volgen dezelfde natuurkunde als de motor; de getallen erin zijn ter illustratie.",
  scrollcue: "Scrol om te beginnen ↓",
  hero_tag: "Eén neutron. Eén kern. Veel manieren waarop het kan aflopen.",
  hero_aud: "Voor studenten en iedereen die nieuw is in de kernfysica, en voor de docenten die hen lesgeven. Vakmensen: de gegevens van elke nuclide staan onder <a href=\"data.html\" data-keep-lang>Alle nucliden</a>.",
  hero_fire: "Schiet een neutron af",
  hero_hint: "of klik ergens op de afbeelding",
  credit_idx: "De INCOGNITA-motor is een port van <a href=\"https://doi.org/10.1140/epja/s10050-023-01034-3\">TALYS-2</a> (A. J. Koning, S. Hilaire, S. Goriely) en gebruikt de kernstructuurdatabase van TALYS. Wat INCOGNITA toevoegt, staat <a href=\"#code\">schakelaar voor schakelaar onderaan deze pagina</a>.",
  coda_h2: "Waar dit in de code zit",
  coda_p1: "Elke stap hierboven is een pakket in <code>physics/hf</code>, en de motor roept ze aan in de volgorde waarin je ze net hebt gelezen. De motor is een port van TALYS-2.x, de gevestigde reactiecode. Wat hij toevoegt, zit achter benoemde schakelaars in dezelfde pakketten: de meeste staan standaard uit, een paar correcties staan aan, en elke schakelaar kan afzonderlijk terug naar gewone TALYS.",
  coda_table: `
    <thead><tr><th>Hoofdstuk</th><th>Wat het doet</th><th>Code</th></tr></thead>
    <tbody>
      <tr><td><a href="#structure">1</a></td><td>Massa's, niveaus, vervorming, resonantiedata</td><td><code>structure/</code></td></tr>
      <tr><td><a href="#omp">2</a></td><td>Optisch model, transmissiecoëfficiënten (hoe makkelijk deeltjes naar binnen en naar buiten komen)</td><td><code>omp/</code></td></tr>
      <tr><td><a href="#direct">3</a></td><td>Gekoppelde kanalen, DWBA, gigantische resonanties, directe vangst (optioneel)</td><td><code>ecis/</code>, <code>direct/</code></td></tr>
      <tr><td><a href="#preeq">4</a></td><td>Pre-evenwicht: excitonmodel, pick-up en knock-out, meervoudige emissie</td><td><code>preeq/</code>, <code>density/particle_hole.py</code></td></tr>
      <tr><td><a href="#compound">5</a></td><td>Niveaudichtheden (toestanden per MeV), spinverdeling</td><td><code>density/</code></td></tr>
      <tr><td><a href="#decay">6</a></td><td>Een uitgang kiezen (Hauser–Feshbach), breedtefluctuaties</td><td><code>compound/</code></td></tr>
      <tr><td><a href="#gamma">7</a></td><td>Fotonsterkte en γ-transmissie; discrete niveaus en isomeren</td><td><code>gamma/</code><br><code>structure/levels.py</code></td></tr>
      <tr><td><a href="#cascade">8</a></td><td>De cascade van deeltjes- en γ-emissies, exclusieve kanalen, restkernen</td><td><code>emission/</code></td></tr>
      <tr><td><a href="#fission">9</a></td><td>Splijtingsbarrières en transmissie</td><td><code>fission/</code></td></tr>
      <tr><td><a href="#measure">11</a></td><td>Emissiespectra, hoekverdelingen en dubbel-differentiële werkzame doorsneden (optioneel, alleen uitvoer)</td><td><code>specout.py</code><br><code>specang.py</code></td></tr>
      <tr><td><a href="#measure">11</a></td><td>Vangst op thermisch aangeslagen trefkernen en stellaire snelheden (optioneel)</td><td><code>astro/stellar.py</code></td></tr>
      <tr><td><a href="#measure">11</a></td><td>Onzekerheid via vele willekeurige varianten (Total Monte Carlo)</td><td><code>tmc.py</code></td></tr>
      <tr><td></td><td>Het stuurprogramma dat de stappen op volgorde uitvoert, en optionele C-kernels voor snelheid</td><td><code>engine.py</code><br><code>engine_c.py</code>, <code>native/</code></td></tr>
      <tr><td></td><td>Alle standaardwaarden en opties, één keer aan het begin ingelezen; ook de per nuclide gefitte parameters van TENDL, toegepast zoals TALYS ze toepast (optioneel)</td><td><code>input/</code></td></tr>
    </tbody>
  `,
  coda_h3_added: "Toegevoegd bovenop TALYS",
  coda_p_added: "Rijen met <b>Aan</b> draaien standaard mee, dus een standaardrun komt niet meer exact overeen met TALYS; elk ervan kan met één sleutelwoord of omgevingsvariabele worden teruggezet. De rest blijft uit tenzij je het aanzet.",
  coda_table_added: `
    <thead><tr><th>Hoofdstuk</th><th>Wat het verandert</th><th>Code</th></tr></thead>
    <tbody>
      <tr><td><a href="#cascade">8</a></td><td><b>Aan.</b> Fluxboekhouding sluitend: restkernen bewaard tot 10⁻⁹ mb (TALYS: 10⁻³ mb), restkernen één stap voorbij het cascadevenster van TALYS bewaard, tot 8 van elk uitgezonden deeltje in exclusieve kanalen, alle herhaalde vervalstakken van een niveau meegeteld</td><td><code>emission/fluxclose.py</code><br><code>emission/channels.py</code><br><code>kevleak2.py</code></td></tr>
      <tr><td><a href="#decay">6</a></td><td><b>Aan.</b> De bovenste bin van de eerste compoundkern wordt gevuld zoals primaire fotonen hem vullen (gewogen met E<sub>γ</sub>³), niet gelijkmatig</td><td><code>compound/nnleak.py</code></td></tr>
      <tr><td><a href="#decay">6</a></td><td><b>Aan.</b> Geen gemiddelde compound-elastische verstrooiing onder de eerste resonanties (onder 1 keV), waar elastisch potentiaalverstrooiing is</td><td><code>lowepot.py</code></td></tr>
      <tr><td><a href="#decay">6</a></td><td><b>Aan.</b> Vervormde trefkernen zonder splijting: neutronuitgangen naar niveaus buiten de gekoppelde band gebruiken de transmissie uit gekoppelde kanalen</td><td><code>compound/ccexitnb.py</code></td></tr>
      <tr><td><a href="#omp">2</a></td><td><b>Aan.</b> Alfa-emissie ziet een potentiaal die afhangt van de temperatuur van de restkern; alfaprojectielen komen binnen via alfamodel 6; triton- en helionpotentialen houden rekening met de grootte van het projectiel</td><td><code>omp/alphatemp.py</code><br><code>alphaentr.py</code><br><code>omp/tfold.py</code></td></tr>
      <tr><td><a href="#fission">9</a></td><td><b>Aan.</b> Exacte eendimensionale transmissie door elke bult van de barrière</td><td><code>fission/wkb.py</code></td></tr>
      <tr><td><a href="#gamma">7</a></td><td><b>Aan.</b> Sterktefactoren voor E1/M1 per kern, waar een run ze meegeeft, vervangen door één globale functie van de vervorming</td><td><code>gamma/ftglobal.py</code></td></tr>
      <tr><td><a href="#compound">5</a></td><td><b>Aan.</b> Targets zonder eigen gemeten resonantieafstand D₀: de niveaudichtheid van het continuüm van de target boven max(E<sub>cut</sub> + 2, S<sub>n</sub> − 6) MeV wordt verhoogd met een factor uit één globale regel op basis van pariteit, schillen en vervorming. Toegevoegd om de nederlaag bij (n,p) bij de drempel tegenover de standaardinvoer van TALYS-2 in een gelijkspel om te zetten; maakt enkele kijken op vangst, (n,2n) en (n,α) iets slechter, een aanvaarde en vastgelegde schade</td><td><code>density/npwindow.py</code></td></tr>
      <tr><td><a href="#gamma">7</a></td><td>Een sterkere schaarmodus in vervormde kernen, uit nieuwere systematiek die overeenkomt met Oslo-metingen (ongeveer 4–5× bij actiniden); of een variant die energie en sterkte ervan met de vervorming schaalt</td><td><code>gamma/scissors.py</code></td></tr>
      <tr><td><a href="#gamma">7</a></td><td>Fotonsterkte herschaald zodat elke kern zijn gemeten stralingssterkte ⟨Γγ⟩/D₀ haalt, voor elke kern in de cascade, niet alleen de eerste</td><td><code>gamma/ggnorm.py</code></td></tr>
      <tr><td><a href="#gamma">7</a></td><td>Sterkere schaarmodus en ⟨Γγ⟩-normalisatie alleen voor de zwaarste kernen (Z ≥ 88), gericht op vangst bij keV-energieën</td><td><code>gamma/actphys.py</code></td></tr>
      <tr><td><a href="#gamma">7</a></td><td>Onze eigen E1-breedteconstante in plaats van de uit TENDL afgeleide tabel van TALYS (het meegeleverde recept zonder data stelt hem in)</td><td><code>gamma/e1_width.py</code></td></tr>
      <tr><td><a href="#gamma">7</a></td><td>Collectieve E2-sterkte van rotatiebanden in het quasicontinuüm</td><td><code>gamma/isoe2.py</code></td></tr>
      <tr><td><a href="#omp">2</a></td><td>Een regionale aanpassing van de optische put voor vervormde trefkernen uit de zeldzame aarden, gefit aan gemeten S₀ en S₁ zonder vangstdata</td><td><code>omp/regional.py</code></td></tr>
      <tr><td><a href="#omp">2</a></td><td>Gemeten neutronsterktefuncties S₀, S₁ leggen de neutrontransmissie bij lage energie vast</td><td><code>omp/sfunc.py</code></td></tr>
      <tr><td><a href="#direct">3</a></td><td>Directe vangst in gebonden banen, met een correctie op het origineel: in standaard-TALYS levert het nul op, tenzij ook alle uitvoer van het optisch model wordt opgevraagd</td><td><code>direct/racapcalc.py</code></td></tr>
      <tr><td><a href="#direct">3</a></td><td>Het koppelingsschema van de trefkern (rotor, vibrator, sferisch) gekozen op basis van zijn gemeten niveaus</td><td><code>structure/collrule.py</code></td></tr>
      <tr><td><a href="#structure">1</a></td><td>Het continuüm begint waar het gemeten niveauschema niet meer volledig is</td><td><code>structure/levcomplete.py</code></td></tr>
      <tr><td><a href="#structure">1</a></td><td>Een niveau waarvan de opgegeven spin onmogelijk is voor zijn kern (geheeltallig bij oneven A) wordt behandeld als een niveau met onbekende spin</td><td><code>structure/levjpar.py</code></td></tr>
      <tr><td><a href="#compound">5</a></td><td>Niveaudichtheid met constante temperatuur, verankerd op het volledige deel van de discrete niveaus</td><td><code>density/ctwindow2.py</code></td></tr>
      <tr><td><a href="#fission">9</a></td><td>Rotatiebanden van overgangstoestanden op de zadelpunten van de splijting</td><td><code>fission/barriers.py</code></td></tr>
      <tr><td><a href="#resonance">10</a></td><td>Vangst waar maar een paar resonanties in het stellaire venster vallen: de typische waarde van één resonantieladder in plaats van het gemiddelde</td><td><code>fewres.py</code></td></tr>
      <tr><td></td><td>Vier beveiligingen ver van de stabiliteit: directe flux begrensd door unitariteit, een limiet op de fermi-energie, standaard geen collectiviteit voor oneven-oneven kernen, spinspreiding van het pre-evenwicht genormaliseerd</td><td><code>engphys.py</code></td></tr>
    </tbody>
  `,
  coda_h3_outside: "Buiten de motor",
  coda_p_outside: "Sommige delen van het verhaal draaien naast de motor in plaats van erin. De statistische resonantieladders van <a href=\"#resonance\">hoofdstuk 10</a> staan in <code>physics/resonance/</code>. De maxwelliaanse gemiddelden (MACS) van <a href=\"#measure\">hoofdstuk 11</a> worden na de run uit de vangstcurven van de motor berekend, in <code>validation/differential/core.py</code>; vangst op thermisch aangeslagen trefkernen en de stellaire snelheid komen daarentegen uit de motor zelf (<code>astro/stellar.py</code>, optioneel). De verankeringslaag van <a href=\"#layers\">hoofdstuk 12</a> staat in <code>incognita/terra/</code>.",
  close: "Sluiten",
  chapters: "Hoofdstukken",
  nav_board: "Scorebord", nav_data_short: "Data",
  coda_repo: "De code, de bibliotheek en de gecureerde metingen zijn open: <a href=\"https://github.com/seth-michael-weaver/incognita\">seth-michael-weaver/incognita op GitHub</a>. Je kunt elke voorspelling zelf opzoeken op de pagina <a href=\"data.html\" data-keep-lang>Alle nucliden</a>, of de repository klonen en hem draaien.",
  diagram: "Diagram",
});

Object.assign(WT.L.ui, { pause_sweep: "Doorloop pauzeren", play_sweep: "Doorloop afspelen" });

/* course mode: audience note, chapter level tags, per-step links */
Object.assign(WT.L.ui, {
  audience: '<b>Voor wie:</b> voor iedereen die nieuwsgierig is. Voor de eerste hoofdstukken heb je geen natuurkunde nodig; de latere gaan tot onderzoeksniveau. Elk hoofdstuk heeft een label: <span class="lvl l0">Inleidend</span>, <span class="lvl l1">Halfgevorderd</span> of <span class="lvl l2">Gevorderd</span>. Wil je het in de les gebruiken? Bekijk de <a href="instructors.html" data-keep-lang>handleiding voor docenten</a>.',
  lvl0: "Inleidend", lvl1: "Halfgevorderd", lvl2: "Gevorderd", lvl_title: "Niveau",
  step_link: "Kopieer een link naar deze stap", link_copied: "Link gekopieerd",
});
