/* Danish: structure (Kapitel 1, hvad en kerne består af) */
WT.L.ch.structure = {
  num: "Kapitel 1", title: "Hvad en kerne består af", short: "Struktur",
  lead: "Før motoren (vores reaktionssoftware) affyrer en eneste neutron, skal den have en beskrivelse af målkernen: hvor fast den hænger sammen, hvilke energitilstande den kan være i, og hvilken form den har.",
  html: `
<div class="step">
  <p>Billedet viser en jernkerne: en tætpakket kugle af <em class="p">protoner</em> og <em class="n">neutroner</em> (<b>nukleoner</b>), holdt sammen af den kortrækkende <b>stærke kernekraft</b>. Hver nukleon mærker kun sine nærmeste naboer, så alle kerner har omtrent samme massefylde.</p>
  <div class="ctl"><label for="st-n">Neutroner (jern har 26 protoner)</label><input id="st-n" type="range" data-bind="N" min="24" max="38" step="1" value="30" data-instant><output data-show="N" data-fmt="0"></output></div>
  <p>Træk for at tilføje eller fjerne neutroner; hvert valg er en anden <b>isotop</b>. Søjlerne viser <b>bindingsenergien</b> per nukleon i MeV (millioner elektronvolt): den energi, der skal til for at trække kernen fra hinanden. Den topper nær de stabile isotoper.</p>
</div>
<div class="step">
  <h3>Prisen for at trække én ud</h3>
  <p>Energien til at trække én partikel ud er dens <b>separationsenergi</b>: <i>S<sub>n</sub></i> for en neutron, <i>S<sub>p</sub></i> for en proton, <i>S<sub>α</sub></i> for en <b>alfapartikel</b> (to protoner og to neutroner bundet sammen). Billedet viser kernen som en brønd med energien opad; hvert træk løfter den øverste partikel ud forbi den stiplede "fri"-linje, og måleren registrerer prisen.</p>
  <div class="btns"><button class="btn ghost" data-act="pn">Træk en neutron ud</button><button class="btn ghost" data-act="pp">Træk en proton ud</button><button class="btn ghost" data-act="pa">Træk en alfa ud</button></div>
  <p>Motoren får hver af dem som forskellen mellem to kernemasser: målte, hvor det er muligt, ellers fra en massemodel.</p>
  <div class="ctl"><label for="st-n2">Neutroner</label><input id="st-n2" type="range" data-bind="N" min="24" max="38" step="1" value="30" data-instant><output data-show="N" data-fmt="0"></output></div>
  <p>Træk i antallet af neutroner og træk en neutron ud igen: <i>S<sub>n</sub></i> går i zigzag, fordi nukleoner danner par, og et lige antal holder fastere på den sidste. En reaktion kan kun kaste en partikel ud, hvis den bringer energi nok til at betale denne pris. Disse priser er hele beregningens <b>tærskler</b>.</p>
</div>
<div class="step">
  <h3>Energiniveauer, og faldet nedad</h3>
  <p>En kerne kan kun rumme bestemte, præcise mængder ekstra energi: linjerne, her for jern-56, med <b>grundtilstanden</b> nederst. Hvert niveau har et <b>spin</b> <i>J</i> (impulsmoment) og en <b>paritet</b>, + eller − (om dets bølge ser ens ud i et spejl); 2<sup>+</sup> betyder spin 2, paritet +.</p>
  <p>Den orange kugle er en kerne på et højt niveau. Den falder ét niveau ad gangen, og hvert hop kaster en <em class="g">foton</em> (en gammastråle) af sig, som bærer energiforskellen. Banernes bredde og procent er de målte odds for hvert hop, <b>forgreningsforholdene</b>.</p>
  <div class="btns"><button class="btn" data-act="drop">Excitér kernen</button></div>
  <p>Tryk et par gange: samme niveau når grundtilstanden ad forskellige veje. Motoren gemmer omkring tredive målte niveauer per kerne med deres odds; højere oppe behandler den de tætpakkede niveauer som et jævnt <b>kontinuum</b>. Over den stiplede linje, <i>S<sub>n</sub></i>, kan kernen udsende en neutron.</p>
</div>
<div class="step">
  <h3>Et niveau uden nem vej ned</h3>
  <p>Et niveau, hvis eneste vej ned kræver en stor spinændring, Δ<i>J</i>, henfalder meget langsomt. Til højre sidder 64 kerner på sådan et niveau; hver venter en tilfældig tid, falder så ned, og en <em class="g">foton</em> springer ud. Halvdelen er faldet efter én <b>halveringstid</b>.</p>
  <div class="ctl"><label for="st-dj">Spinændring ΔJ</label><input id="st-dj" type="range" data-bind="dJ" min="1" max="5" step="1" value="2" data-instant><output data-show="dJ" data-fmt="0"></output></div>
  <div class="ctl"><label for="st-eg">Fotonenergi (MeV)</label><input id="st-eg" type="range" data-bind="Eg" min="0.05" max="1.5" step="0.05" value="0.3"><output data-show="Eg" data-fmt="2"></output></div>
  <div class="btns"><button class="btn ghost" data-act="excite">Excitér dem alle</button></div>
  <p>Hæv Δ<i>J</i>, og glimtene bliver sjældnere: hver ekstra enhed spin gør ventetiden hundrede tusind gange længere eller mere, og lavere fotonenergi forlænger den også (vist på logaritmisk skala). Et niveau, der lever længere end ca. et sekund, er en <b>isomer</b>, og motoren behandler det som et endepunkt, ligesom grundtilstanden.</p>
</div>
<div class="step">
  <h3>Rund, eller ej</h3>
  <p>Mange kerner er ikke runde. <i>β₂</i> ("beta-to") måler strækningen: 0 er en kugle, positiv er strakt som en amerikansk fodbold, negativ er trykket flad til en skive. Stigen til højre viser de niveauer, hver slags giver.</p>
  <p>En aflang kerne kan rotere og giver niveauerne 0<sup>+</sup>, 2<sup>+</sup>, 4<sup>+</sup>, 6<sup>+</sup> med afstande, der vokser som <i>J</i>(<i>J</i>+1): en <b>rotor</b>. En rund kerne kan kruse; hver enhed krusning, en <b>fonon</b>, tilføjer samme energi, så dens niveauer ligger med lige store afstande: en <b>vibrator</b>.</p>
  <div class="ctl"><label for="st-beta">Deformation β₂</label><input id="st-beta" type="range" data-bind="beta" min="-0.3" max="0.45" step="0.01" value="0.28"><output data-show="beta" data-fmt="2"></output></div>
  <div class="btns"><button class="btn ghost" data-act="still">I ro</button><button class="btn ghost" data-act="vib">Vibrerende</button><button class="btn ghost" data-act="rot">Roterende</button></div>
  <p>Træk i <i>β₂</i> og tryk på knapperne: en større strækning trækker rotorens niveauer tættere sammen. Motoren gemmer deformationer per kerne og en mærkat: sfærisk, vibrator eller rotor. Kapitel 3 viser, hvordan en forbipasserende neutron bruger dem.</p>
</div>
<div class="step">
  <h3>Fingeraftryk lige over tærsklen</h3>
  <p>En langsom neutron, der forener sig med målkernen, lander lige over <i>S<sub>n</sub></i>, i den lille boks til venstre. Panelet til højre forstørrer den boks tusindvis af gange, med neutronenergien fra venstre mod højre.</p>
  <div class="ctl"><label for="st-fe">Stråleenergi</label><input id="st-fe" type="range" data-bind="fe" min="0" max="1" step="0.001" value="0.3" data-instant><output id="st-fe-out"></output></div>
  <div class="btns"><button class="btn ghost" data-act="fplay" id="st-fplay">Sæt gennemløbet på pause</button></div>
  <p>Ved de fleste energier går strålen lige igennem. Ved visse præcise energier passer neutronen plus kernen til et skjult niveau, og meget af strålen optages: en <b>resonans</b>. På en top svulmer den tegnede kerne op: ikke en virkelig størrelsesændring, men det større mål, neutronen reelt ser, når dens bølge overlapper kernens. Kernen giver derefter energien tilbage som en <em class="g">foton</em> eller en neutron. Kurven viser den optagne andel; stregerne markerer hver fundet resonans.</p>
  <div class="btns"><button class="btn ghost" data-act="fFe">Jern-56</button><button class="btn ghost" data-act="fAu">Guld-197</button><button class="btn ghost" data-act="fU">Uran-238</button></div>
  <p>Hver kerne har sin egen stregkode i sin egen skala: tusindvis af elektronvolt mellem jernets resonanser, titals for guld og uran. Tre gennemsnit opsummerer den: <i>D₀</i>, den gennemsnitlige afstand; ⟨Γ<sub>γ</sub>⟩, <b>fotonbredden</b>, næsten ens for alle toppe; og <i>S₀</i>, <b>styrkefunktionen</b>, hvor let en langsom neutron kommer ind.</p>
  <p>Hver af dem tjekker et senere trin. Motorens niveautæthedsparametre blev tilpasset <i>D₀</i>, kerne for kerne; ⟨Γ<sub>γ</sub>⟩ tester fotonemission, <i>S₀</i> den optiske model i næste kapitel. For ikke-målte kerner bruger motoren tendenser tilpasset på tværs af mange kerner.</p>
  <div class="aside">I koden: <code>structure/masses.py</code> (målte masser, modelmasser uden for dem, separationsenergier), <code>structure/levels.py</code> (diskrete niveauer, forgreninger, isomerer, gættede spin) og <code>levjpar.py</code> (valgfri, slået fra som standard: gætter igen et opført spin, der er umuligt for kernen), <code>structure/deformation.py</code> (β₂ og mærkaten sfærisk/vibrator/rotor) og <code>collrule.py</code> (valgfri, slået fra som standard: vælger målkernens mærkat ud fra dens målte niveauer), <code>structure/resonances.py</code> (D₀, S₀, S₁, ⟨Γγ⟩).</div>
</div>`,
};
(function () {
  const L = {
    // scene: packed drop
    "{#}Fe": "{#}Fe",
    "{#} protons · {#} neutrons": "{#} protoner · {#} neutroner",
    "binding energy per nucleon: about {#} MeV": "bindingsenergi per nukleon: ca. {#} MeV",
    "binding per nucleon, one bar per isotope →": "binding per nukleon, én søjle per isotop →",
    // scene: well
    "free": "fri",
    "free: outside the nucleus": "fri: uden for kernen",
    "neutrons": "neutroner",
    "protons": "protoner",
    "an alpha forms from the top pairs": "de øverste par danner en alfa",
    "neutron {#}": "neutron {#}",
    "proton {#}": "proton {#}",
    "alpha {#}": "alfa {#}",
    "n {#}": "n {#}",
    "p {#}": "p {#}",
    "energy paid": "betalt energi",
    "energy to pull": "energi for at",
    "(MeV)": "(MeV)",
    "each one out (MeV)": "trække hver ud (MeV)",
    "higher mark =": "højere mærke =",
    "harder to remove": "sværere at fjerne",
    "pulling out a neutron: {#} MeV paid": "trækker en neutron ud: {#} MeV betalt",
    "pulling out a proton: {#} MeV paid": "trækker en proton ud: {#} MeV betalt",
    "pulling out an alpha: {#} MeV paid": "trækker en alfa ud: {#} MeV betalt",
    // scene: levels and gamma drops
    "continuum: too many levels to list": "kontinuum: for mange niveauer at opliste",
    "neutron threshold Sₙ ≈ {#} MeV": "neutrontærskel Sₙ ≈ {#} MeV",
    "ground state": "grundtilstand",
    "MeV": "MeV",
    "each line: an energy, a spin J and a parity (±)": "hver linje: en energi, et spin J og en paritet (±)",
    "path width and % = measured odds of each hop": "banebredde og % = målte odds for hvert hop",
    // scene: isomer
    "ground": "grund",
    "J = {#}/{#}": "J = {#}/{#}",
    "ΔJ = {#}": "ΔJ = {#}",
    "still excited: {#} of {#}": "stadig exciteret: {#} af {#}",
    "longer than a second: an isomer, a stop in its own right": "længere end et sekund: en isomer, et selvstændigt stop",
    "shown slowed down (log scale)": "vist i slowmotion (log-skala)",
    "shown slowed down: the slower they pop, the longer the real wait (log scale)": "vist i slowmotion: jo langsommere glimt, jo længere reel ventetid (log-skala)",
    // scene: shape
    "ripples at the surface: a vibrator": "kruser ved overfladen: en vibrator",
    "stretched and rotating: a rotor": "aflang og roterende: en rotor",
    "round: a sphere": "rund: en kugle",
    "stretched (prolate): a football": "strakt (prolat): en fodbold",
    "squashed: an oblate disc": "fladtrykt: en oblat skive",
    "{#} phonons": "{#} fononer",
    "no regular": "intet regelmæssigt",
    "level pattern": "niveaumønster",
    "spacing grows like J(J+{#})": "afstanden vokser som J(J+{#})",
    "equal steps, one phonon each": "lige store trin, én fonon hver",
    "its lowest levels": "dens laveste niveauer",
    "β₂ = {#}": "β₂ = {#}",
    // scene: resonance fingerprint
    "continuum": "kontinuum",
    "Sₙ ≈ {#} MeV": "Sₙ ≈ {#} MeV",
    "slow neutron": "langsom neutron",
    "a slow neutron lands here:": "en langsom neutron lander her:",
    "lands here": "lander her",
    "Sₙ + its kinetic energy": "Sₙ + dens kinetiske energi",
    "×{#} million": "×{#} millioner",
    "×{#} thousand": "×{#} tusind",
    "magnified": "forstørret",
    "swells on a peak: the size the neutron effectively “sees” (waves overlap), not a real size change": "svulmer på en top: den størrelse, neutronen reelt “ser” (bølgerne overlapper), ikke en virkelig størrelsesændring",
    "share taken in": "optaget andel",
    "share of the beam taken in": "andel af strålen optaget",
    "{#} (Sₙ)": "{#} (Sₙ)",
    "{#} = exactly Sₙ": "{#} = præcis Sₙ",
    "{#} keV": "{#} keV",
    "{#} eV": "{#} eV",
    "neutron energy →": "neutronenergi →",
    "neutron's kinetic energy →": "neutronens kinetiske energi →",
    "D₀ ≈ {#} keV: the average gap": "D₀ ≈ {#} keV: den gennemsnitlige afstand",
    "D₀ ≈ {#} eV: the average gap": "D₀ ≈ {#} eV: den gennemsnitlige afstand",
    "S₀: average peak strength": "S₀: gennemsnitlig topstyrke",
    "S₀: how strong the peaks are on average (how easily a neutron gets in)": "S₀: toppenes gennemsnitlige styrke (hvor let en neutron kommer ind)",
    "⟨Γγ⟩ ≈ {#} eV: photon width": "⟨Γγ⟩ ≈ {#} eV: fotonbredde",
    "⟨Γγ⟩ ≈ {#} eV: photon width, about the same for every peak": "⟨Γγ⟩ ≈ {#} eV: fotonbredde, omtrent ens for alle toppe",
    "⟨Γγ⟩ ≈ {#} eV: a hairline here": "⟨Γγ⟩ ≈ {#} eV: her en hårfin streg",
    "⟨Γγ⟩ ≈ {#} eV: a hairline here; neutrons widen these peaks": "⟨Γγ⟩ ≈ {#} eV: her en hårfin streg; neutroner gør toppene bredere",
    "peaks drawn about {#}× wider than life so they show": "toppe tegnet ca. {#}× bredere end i virkeligheden, så de kan ses",
  };
  // beam readout and per-target labels
  for (const u of ["keV", "eV"]) L[`beam of neutrons at {#} ${u}`] = `neutronstråle ved {#} ${u}`;
  const EL = { iron: "jern", gold: "guld", uranium: "uran" };
  for (const en in EL) {
    L[`${en}{#} levels`] = `niveauer i ${EL[en]}{#}`;
    L[`${en}{#}: took in {#} of the last {#}`] = `${EL[en]}{#}: optog {#} af de seneste {#}`;
  }
  // isomer half-life in every unit fmtTime can produce
  const TU = { femtoseconds: "femtosekunder", picoseconds: "picosekunder", nanoseconds: "nanosekunder", microseconds: "mikrosekunder",
    milliseconds: "millisekunder", seconds: "sekunder", minutes: "minutter", hours: "timer", days: "dage", years: "år" };
  for (const en in TU) L[`half-life about {#} ${en}`] = `halveringstid ca. {#} ${TU[en]}`;
  L["half-life about {#}×{#}^{#} years"] = "halveringstid ca. {#}×{#}^{#} år";
  Object.assign(WT.L.labels, L);
})();
