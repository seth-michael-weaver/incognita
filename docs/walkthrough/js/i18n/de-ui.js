/* German (Deutsch): static page text (index.html data-i18n keys) and kit UI strings */
Object.assign(WT.L.ui, {
  lang_label: "Sprache", nav_teach: "Lehrende",
  brand: "Im Inneren einer Kernreaktion", nav_physics: "Die Physik", nav_data: "Alle Nuklide", nav_board: "Rangliste", menu: "Menü", site_nav: "Website",
  ways_h: "Weitere Einstiege", ways_more: "Oder scroll einfach weiter: Hier beginnt die Physik ↓",
  way1_k: "Erkunden", way1_t: "Alle Nuklide", way1_p: "Vorhergesagte Wirkungsquerschnitte für 6168 Nuklide neben jeder kuratierten Messung. Such dir ein beliebiges Isotop und sieh dir jeden Datensatz an.", way1_go: "Zu den Daten →",
  way2_k: "Vergleichen", way2_t: "Rangliste", way2_p: "Wie die Engine und ihr Datenprodukt im Vergleich mit anderen Reaktionscodes und Bibliotheken abschneiden, gemessen an Experimenten, die Niederlagen zuerst.", way2_go: "Zu den Ergebnissen →",
  way3_k: "Ausführen", way3_t: "Der Code", way3_p: "Alles hier ist offen. Klon das Repository, schlag jede Kurve nach oder lass die Engine selbst laufen.", way3_go: "GitHub →",
  title: "Im Inneren einer Kernreaktion",
  kicker: "Eine interaktive Erklärung der Reaktions-Engine INCOGNITA",
  h1: "Im Inneren einer Kernreaktion",
  hero1: "Schieß ein Neutron auf einen Atomkern, und etwas kommt wieder heraus. Vielleicht das Neutron selbst, abgeprallt. Vielleicht ein Proton, ein Alphateilchen (ein fest gebundenes Bündel aus 2 Protonen und 2 Neutronen) oder ein Lichtblitz. Ein schwerer Kern kann sich sogar in zwei Teile spalten.",
  hero2: "Was davon passiert, und wie oft? Diese Seite zeigt Schritt für Schritt, wie unsere Software diese Frage beantwortet. Scroll nach unten und probier unterwegs die Regler aus. Die Bilder folgen derselben Physik wie die Engine; die Zahlen darin dienen der Veranschaulichung.",
  scrollcue: "Scrollen, um zu beginnen ↓",
  hero_tag: "Eine visuelle Erkundung der Kernphysik",
  hero_aud: "Für Studierende und alle, die neu in der Kernphysik sind, und für die Lehrenden, die sie unterrichten. Fachleute: Die Daten zu jedem Nuklid stehen unter <a href=\"data.html\" data-keep-lang>Alle Nuklide</a>.",
  hero_fire: "Neutron abfeuern",
  hero_hint: "oder klick irgendwo ins Bild",
  credit_idx: "Die Engine INCOGNITA ist eine Portierung von <a href=\"https://doi.org/10.1140/epja/s10050-023-01034-3\">TALYS-2</a> (A. J. Koning, S. Hilaire, S. Goriely) und nutzt die Kernstrukturdatenbank von TALYS. Was INCOGNITA hinzufügt, ist <a href=\"#code\">am Ende dieser Seite Schalter für Schalter aufgelistet</a>.",
  coda_h2: "Wo das im Code steckt",
  coda_p1: "Jede Stufe oben ist ein Paket in <code>physics/hf</code>, und die Engine ruft sie in genau der Reihenfolge auf, in der du sie gerade gelesen hast. Die Engine ist eine Portierung von TALYS-2.x, dem etablierten Reaktionscode. Was sie hinzufügt, liegt hinter benannten Schaltern in denselben Paketen: Die meisten sind standardmäßig aus, einige Korrekturen sind an, und jede lässt sich einzeln auf das reine TALYS zurückschalten.",
  coda_table: `
    <thead><tr><th>Kapitel</th><th>Was es macht</th><th>Code</th></tr></thead>
    <tbody>
      <tr><td><a href="#structure">1</a></td><td>Massen, Niveaus, Deformation, Resonanzdaten</td><td><code>structure/</code></td></tr>
      <tr><td><a href="#omp">5</a></td><td>Optisches Modell, Transmissionskoeffizienten (wie leicht Teilchen hinein- und herauskommen)</td><td><code>omp/</code></td></tr>
      <tr><td><a href="#direct">6</a></td><td>Gekoppelte Kanäle, DWBA, Riesenresonanzen, direkter Einfang (optional)</td><td><code>ecis/</code>, <code>direct/</code></td></tr>
      <tr><td><a href="#preeq">7</a></td><td>Präequilibrium: Exzitonenmodell, Pickup und Knockout, Mehrfachemission</td><td><code>preeq/</code>, <code>density/particle_hole.py</code></td></tr>
      <tr><td><a href="#compound">8</a></td><td>Niveaudichten (Zustände pro MeV), Spinverteilung</td><td><code>density/</code></td></tr>
      <tr><td><a href="#decay">9</a></td><td>Einen Ausgang wählen (Hauser–Feshbach), Breitenfluktuationen</td><td><code>compound/</code></td></tr>
      <tr><td><a href="#gamma">10</a></td><td>Photonenstärke und γ-Transmission; diskrete Niveaus und Isomere</td><td><code>gamma/</code><br><code>structure/levels.py</code></td></tr>
      <tr><td><a href="#cascade">11</a></td><td>Die Kaskade aus Teilchen- und γ-Emissionen, exklusive Kanäle, Restkerne</td><td><code>emission/</code></td></tr>
      <tr><td><a href="#fission">12</a></td><td>Spaltbarrieren und Transmission</td><td><code>fission/</code></td></tr>
      <tr><td><a href="#measure">17</a></td><td>Emissionsspektren, Winkelverteilungen und doppelt differentielle Wirkungsquerschnitte (optional, nur Ausgabe)</td><td><code>specout.py</code><br><code>specang.py</code></td></tr>
      <tr><td><a href="#measure">17</a></td><td>Einfang an thermisch angeregten Targets und stellare Raten (optional)</td><td><code>astro/stellar.py</code></td></tr>
      <tr><td><a href="#measure">17</a></td><td>Unsicherheit über viele zufällige Varianten (Total Monte Carlo)</td><td><code>tmc.py</code></td></tr>
      <tr><td></td><td>Das Steuerprogramm, das die Stufen der Reihe nach ausführt, und optionale C-Kernels für mehr Tempo</td><td><code>engine.py</code><br><code>engine_c.py</code>, <code>native/</code></td></tr>
      <tr><td></td><td>Alle Standardwerte und Optionen, einmal zu Beginn eingelesen; außerdem die pro Nuklid angepassten Parameter von TENDL, angewandt wie in TALYS (optional)</td><td><code>input/</code></td></tr>
    </tbody>
  `,
  coda_h3_added: "Über TALYS hinaus hinzugefügt",
  coda_p_added: "Mit <b>An</b> markierte Zeilen laufen standardmäßig, sodass ein Standardlauf nicht mehr exakt mit TALYS übereinstimmt; jede lässt sich mit einem Schlüsselwort oder einer Umgebungsvariablen zurückschalten. Der Rest bleibt aus, solange er nicht gesetzt wird.",
  coda_table_added: `
    <thead><tr><th>Kapitel</th><th>Was es ändert</th><th>Code</th></tr></thead>
    <tbody>
      <tr><td><a href="#cascade">11</a></td><td><b>An.</b> Geschlossene Flussbilanz: Restkerne bis hinunter zu 10⁻⁹ mb behalten (TALYS: 10⁻³ mb), Restkerne einen Schritt jenseits des Kaskadenfensters von TALYS behalten, bis zu 8 von jedem Ejektil in exklusiven Kanälen, alle wiederholten Zerfallszweige eines Niveaus gezählt</td><td><code>emission/fluxclose.py</code><br><code>emission/channels.py</code><br><code>kevleak2.py</code></td></tr>
      <tr><td><a href="#decay">9</a></td><td><b>An.</b> Das oberste Intervall des ersten Compoundkerns wird so gefüllt, wie primäre Photonen es füllen (gewichtet mit E<sub>γ</sub>³), nicht gleichmäßig</td><td><code>compound/nnleak.py</code></td></tr>
      <tr><td><a href="#decay">9</a></td><td><b>An.</b> Keine gemittelte compound-elastische Streuung unterhalb der ersten Resonanzen (unter 1 keV), wo die elastische Streuung Potentialstreuung ist</td><td><code>lowepot.py</code></td></tr>
      <tr><td><a href="#decay">9</a></td><td><b>An.</b> Deformierte Targets ohne Spaltung: Neutronenausgänge zu Niveaus außerhalb der gekoppelten Bande nutzen die Transmission aus gekoppelten Kanälen</td><td><code>compound/ccexitnb.py</code></td></tr>
      <tr><td><a href="#omp">5</a></td><td><b>An.</b> Die Alphaemission sieht ein Potential, das von der Temperatur des Restkerns abhängt; Alpha-Projektile treten über das Alphamodell 6 ein; die Potentiale für Triton und Helion berücksichtigen die Größe des Projektils</td><td><code>omp/alphatemp.py</code><br><code>alphaentr.py</code><br><code>omp/tfold.py</code></td></tr>
      <tr><td><a href="#fission">12</a></td><td><b>An.</b> Exakte eindimensionale Transmission durch jeden Buckel der Barriere</td><td><code>fission/wkb.py</code></td></tr>
      <tr><td><a href="#gamma">10</a></td><td><b>An.</b> E1/M1-Stärkefaktoren pro Kern, sofern ein Lauf sie vorgibt, ersetzt durch eine einzige globale Funktion der Deformation</td><td><code>gamma/ftglobal.py</code></td></tr>
      <tr><td><a href="#compound">8</a></td><td><b>An.</b> Targets ohne eigenen gemessenen Resonanzabstand D₀: Die Kontinuums-Niveaudichte des Targets oberhalb von max(E<sub>cut</sub> + 2, S<sub>n</sub> − 6) MeV wird um einen Faktor aus einer einzigen globalen Regel erhöht, die von Paritäts-, Schalen- und Deformationsmerkmalen abhängt. Eingeführt, um die Niederlage bei (n,p) nahe der Schwelle gegen die Standardeingabe von TALYS-2 in ein Remis zu verwandeln; sie verschlechtert einige Sichten zu Einfang, (n,2n) und (n,α) geringfügig, ein akzeptierter und protokollierter Schaden</td><td><code>density/npwindow.py</code></td></tr>
      <tr><td><a href="#gamma">10</a></td><td>Eine stärkere Scherenmode in deformierten Kernen, aus neueren Systematiken, die zu Oslo-Messungen passen (etwa 4–5× bei Aktiniden); oder eine Variante, die ihre Energie und Stärke mit der Deformation skaliert</td><td><code>gamma/scissors.py</code></td></tr>
      <tr><td><a href="#gamma">10</a></td><td>Photonenstärke so umskaliert, dass jeder Kern seine gemessene Strahlungsstärke ⟨Γγ⟩/D₀ trifft, für jeden Kern der Kaskade, nicht nur den ersten</td><td><code>gamma/ggnorm.py</code></td></tr>
      <tr><td><a href="#gamma">10</a></td><td>Stärkere Scherenmode und ⟨Γγ⟩-Normierung nur für die schwersten Kerne (Z ≥ 88), gedacht für den Einfang bei keV-Energien</td><td><code>gamma/actphys.py</code></td></tr>
      <tr><td><a href="#gamma">10</a></td><td>Eine eigene E1-Breitenkonstante statt der aus TENDL abgeleiteten Tabelle von TALYS (das mitgelieferte Rezept ohne Daten setzt sie)</td><td><code>gamma/e1_width.py</code></td></tr>
      <tr><td><a href="#gamma">10</a></td><td>Kollektive E2-Stärke von Rotationsbanden im Quasikontinuum</td><td><code>gamma/isoe2.py</code></td></tr>
      <tr><td><a href="#omp">5</a></td><td>Eine regionale Anpassung des optischen Topfs für deformierte Targets der Seltenen Erden, angepasst an gemessene S₀ und S₁ ohne Einfangdaten</td><td><code>omp/regional.py</code></td></tr>
      <tr><td><a href="#omp">5</a></td><td>Gemessene Neutronenstärkefunktionen S₀, S₁ legen die Neutronentransmission bei niedriger Energie fest</td><td><code>omp/sfunc.py</code></td></tr>
      <tr><td><a href="#direct">6</a></td><td>Direkter Einfang in gebundene Orbitale, mit einer Korrektur am Original: Im unveränderten TALYS liefert er null, sofern nicht auch jede Ausgabe des optischen Modells angefordert wird</td><td><code>direct/racapcalc.py</code></td></tr>
      <tr><td><a href="#direct">6</a></td><td>Das Kopplungsschema des Targets (Rotor, Vibrator, sphärisch), gewählt anhand seiner gemessenen Niveaus</td><td><code>structure/collrule.py</code></td></tr>
      <tr><td><a href="#structure">1</a></td><td>Das Kontinuum beginnt dort, wo das gemessene Niveauschema nicht mehr vollständig ist</td><td><code>structure/levcomplete.py</code></td></tr>
      <tr><td><a href="#structure">1</a></td><td>Ein Niveau, dessen aufgeführter Spin für seinen Kern unmöglich ist (ganzzahlig bei ungeradem A), wird als Niveau mit unbekanntem Spin behandelt</td><td><code>structure/levjpar.py</code></td></tr>
      <tr><td><a href="#compound">8</a></td><td>Niveaudichte mit konstanter Temperatur, verankert am vollständigen Teil der diskreten Niveaus</td><td><code>density/ctwindow2.py</code></td></tr>
      <tr><td><a href="#fission">12</a></td><td>Rotationsbanden von Übergangszuständen an den Sattelpunkten der Spaltung</td><td><code>fission/barriers.py</code></td></tr>
      <tr><td><a href="#resonance">15</a></td><td>Einfang, wenn nur wenige Resonanzen ins stellare Fenster fallen: der typische Wert einer Resonanzleiter statt des Mittelwerts</td><td><code>fewres.py</code></td></tr>
      <tr><td></td><td>Vier Schutzmechanismen fern der Stabilität: direkter Fluss durch Unitarität begrenzt, eine Grenze für die Fermi-Energie, keine Standard-Kollektivität für ug-Kerne, Spinverteilung des Präequilibriums normiert</td><td><code>engphys.py</code></td></tr>
    </tbody>
  `,
  coda_h3_outside: "Außerhalb der Engine",
  coda_p_outside: "Einige Teile der Geschichte laufen neben der Engine statt in ihr. Die statistischen Resonanzleitern aus <a href=\"#resonance\">Kapitel 15</a> liegen in <code>physics/resonance/</code>. Die Maxwell-Mittelwerte (MACS) aus <a href=\"#measure\">Kapitel 17</a> werden nach dem Lauf aus den Einfangkurven der Engine gefaltet, in <code>validation/differential/core.py</code>; der Einfang an thermisch angeregten Targets und die stellare Rate stammen dagegen aus der Engine selbst (<code>astro/stellar.py</code>, optional). Die Verankerungsschicht aus <a href=\"#layers\">Kapitel 21</a> liegt in <code>incognita/terra/</code>.",
  close: "Schließen",
  chapters: "Kapitel",
  nav_board: "Rangliste", nav_data_short: "Daten",
  coda_repo: "Der Code, die Bibliothek und die kuratierten Messungen sind offen: <a href=\"https://github.com/seth-michael-weaver/incognita\">seth-michael-weaver/incognita auf GitHub</a>. Du kannst jede Vorhersage selbst auf der Seite <a href=\"data.html\" data-keep-lang>Alle Nuklide</a> nachschlagen oder das Repository klonen und selbst ausführen.",
  diagram: "Diagramm",
});

Object.assign(WT.L.ui, { pause_sweep: "Durchlauf anhalten", play_sweep: "Durchlauf abspielen" });

/* course mode: audience note, chapter level tags, per-step links */
Object.assign(WT.L.ui, {
  audience: '<b>Für wen:</b> für alle, die neugierig sind. Die ersten Kapitel brauchen keine Physikkenntnisse; spätere gehen bis auf Forschungsniveau. Jedes Kapitel trägt eine Marke: <span class="lvl l0">Einstieg</span>, <span class="lvl l1">Mittelstufe</span>, <span class="lvl l2">Fortgeschritten</span> oder <span class="lvl l3">Experte</span>. Du willst damit unterrichten? Sieh dir den <a href="instructors.html" data-keep-lang>Leitfaden für Lehrende</a> an.',
  lvl0: "Einstieg", lvl1: "Mittelstufe", lvl2: "Fortgeschritten", lvl3: "Experte", lvl_title: "Niveau",
  step_link: "Link zu diesem Schritt kopieren", link_copied: "Link kopiert",
});

/* part divider before the Expert chapters (index.html) */
Object.assign(WT.L.ui, {
  xp_kicker: "Teil zwei · Experte",
  xp_h: "Ins Detail",
  xp_p: "Bisher wurde jeder Schritt als Bild erzählt. Die sechs folgenden Kapitel öffnen dieselben Schritte: die Formeln, die die Engine auswertet, die Näherungen darin und die Stellen, an denen sie an ihre Grenzen stoßen. Sie richten sich an Evaluatoren, Modellentwickler und Doktoranden. Die Zeichnungen werten die Formeln live aus, mit illustrativen Eingabewerten.",
});
