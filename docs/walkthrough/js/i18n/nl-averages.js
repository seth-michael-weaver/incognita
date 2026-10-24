/* Dutch (Nederlands): averages (Hoofdstuk 18, van resonanties naar gemiddelden) */
WT.L.ch.averages = {
  num: "Hoofdstuk 18", title: "Van resonanties naar gemiddelden", short: "Resonanties naar gemiddelden",
  lead: "Hoofdstuk 10 tekende resonantieladders. Hier verschijnen ze als werkzame doorsneden: de formule van de R-matrix, de statistiek achter de parameters, het effect van de temperatuur, en hoe een gemiddelde over veel resonanties overgaat in Hauser–Feshbach.",
  html: `
<div class="step">
  <h3>R-matrix, niveau voor niveau</h3>
  <p>Onder een paar keV verschijnt in een zware kern elk compoundniveau afzonderlijk, en wordt de werkzame doorsnede exact uitgedrukt in niveauparameters: energieën <i>E</i><sub>λ</sub>, gereduceerde neutronbreedten en vangstbreedten. Evaluaties gebruiken de theorie van de <b>R-matrix</b>, meestal in de vorm van <b>Reich–Moore</b>, die de interferentie tussen niveaus in het neutronkanaal behoudt en de vele vangstkanalen behandelt als één absorberende breedte.</p>
  <div class="formula">R(E) = Σ<sub>λ</sub> γ<sub>λ</sub>² / (E<sub>λ</sub> − E − iΓ<sub>λγ</sub>/2) ,  U = e<sup>−2iφ</sup> (1 + iPR) / (1 − iPR)</div>
  <div class="formula">σ<sub>tot</sub> = (2π/k²) g (1 − Re U) ,  σ<sub>γ</sub> = (π/k²) g (1 − |U|²)</div>
  <div class="btns"><button class="btn ghost" data-act="rm" aria-pressed="true">Reich–Moore</button><button class="btn ghost" data-act="bw" aria-pressed="false">Breit–Wigner voor één niveau</button></div>
  <p>De bovenste lijn is de totale werkzame doorsnede, de onderste vangst, voor één ladder van s-golfniveaus op een trefkern met spin 0, vergelijkbaar met uranium-238. Tussen de niveaus zakt het totaal onder de potentiaalverstrooiing, waar resonantie- en potentiaalamplitude elkaar uitdoven. De vorm voor één niveau telt de werkzame doorsneden van de niveaus op in plaats van hun amplitudes; die klopt goed bij de pieken en is fout in de dalen, waar de staarten van veel niveaus optellen en het totaal zelfs negatief kan worden.</p>
</div>
<div class="step">
  <h3>De statistiek achter de parameters</h3>
  <p>Een niet-gemeten kern heeft geen ladder, alleen zijn gemiddelden: <i>D</i>₀, de sterktefunctie <i>S</i>₀ = ⟨Γ<sub>n</sub>⁰⟩/<i>D</i>₀ en ⟨Γ<sub>γ</sub>⟩. De theorie van stochastische matrices levert de rest: afstanden tussen niveaus met dezelfde spin en pariteit volgen de Wigner-verdeling, gereduceerde neutronbreedten volgen Porter–Thomas, een χ² met één vrijheidsgraad.</p>
  <div class="formula">P(s) = (πs/2) e<sup>−πs²/4</sup> ,  P(y) = e<sup>−y/2</sup> / √(2πy) ,  s = afstand/D₀, y = Γ<sub>n</sub>⁰/⟨Γ<sub>n</sub>⁰⟩</div>
  <div class="btns"><button class="btn" data-act="more">Trek nog tien ladders</button></div>
  <p>De histogrammen verzamelen de afstanden en breedten van elke ladder die tot nu toe is getrokken; de curven zijn de twee wetten. De vangstbreedte, een som over honderden fotonkanalen, fluctueert nauwelijks, dus die wordt vast genomen.</p>
</div>
<div class="step">
  <h3>Warmte smeert de pieken uit</h3>
  <p>De trefkernen bewegen. Een neutron met energie <i>E</i> ontmoet ze met een spreiding in relatieve energie van breedte Δ = √(4<i>E</i> <i>kT</i>/<i>A</i>), en elke resonantie wordt door die spreiding heen gezien: <b>dopplerverbreding</b>. Voor één niveau is het resultaat de ψ-functie, een lorentziaan geconvolueerd met een gaussiaan.</p>
  <div class="formula">σ<sub>γ</sub>(E,T) = σ₀ (Γ<sub>γ</sub>/Γ) ψ(x, ξ) ,  x = 2(E − E<sub>λ</sub>)/Γ ,  ξ = Γ/Δ</div>
  <div class="ctl"><label for="av-t">Temperatuur (K)</label><input id="av-t" type="range" data-bind="TK" min="0" max="3000" step="10" value="300"><output data-show="TK" data-fmt="0"></output></div>
  <p>De vergrote resonantie is de sterkste van de laagste paar in de ladder; de gestippelde lijn is haar vorm bij 0 K. Warmte verlaagt de piek en verbreedt de flanken, en het oppervlak onder de vangstpiek blijft gelijk. In een dik monster is dat niet neutraal: de piek is zelfafgeschermd en de flanken niet, dus een hetere splijtstof vangt meer. Dit is de dopplerterugkoppeling van een reactor.</p>
</div>
<div class="step">
  <h3>Het gemiddelde is Hauser–Feshbach</h3>
  <p>Gemiddeld over veel resonanties wordt vangst een gladde functie van de energie. Het venster glijdt over de ladder en zijn gemiddelde wordt onderweg uitgezet; de gladde lijnen zijn de waarde volgens Hauser–Feshbach met de transmissies <i>T<sub>n</sub></i> = 2π⟨Γ<sub>n</sub>⟩/<i>D</i> en <i>T<sub>γ</sub></i> = 2π⟨Γ<sub>γ</sub>⟩/<i>D</i>.</p>
  <div class="ctl"><label for="av-w">Vensterbreedte (niveaus)</label><input id="av-w" type="range" data-bind="win" min="2" max="40" step="1" value="12" data-instant><output data-show="win" data-fmt="0"></output></div>
  <div class="btns"><button class="btn ghost" data-act="ladder">Andere ladder</button></div>
  <p>Een smal venster spreidt sterk: een paar resonanties, breedten volgens Porter–Thomas. Een breed venster komt tot rust op de onderste lijn, die met de breedtefluctuatiecorrectie. De bovenste lijn, het product van gemiddelden, ligt hier 25 tot 47 procent te hoog, het meest waar ⟨Γ<sub>n</sub>⟩ één tot drie keer ⟨Γ<sub>γ</sub>⟩ is, van ongeveer 100 eV tot 1 keV. (Met p-golven en meer open kanalen is de correctie kleiner.) Voor één neutronkanaal met breedten volgens Porter–Thomas en een vaste vangstbreedte is de gecorrigeerde waarde exact: (2π²/k²<i>D</i>) <i>g</i> ⟨Γ<sub>n</sub>Γ<sub>γ</sub>/Γ⟩.</p>
</div>
<div class="step">
  <h3>Opgelost, niet opgelost, glad</h3>
  <p>Wat een meting oplost, hangt af van haar energieresolutie, die slechter wordt naarmate de energie stijgt. De lijn is de werkzame doorsnede zoals een instrument haar ziet, verbreed door een resolutie die groeit als <i>E</i><sup>3/2</sup>, zoals bij vluchttijdmetingen. Bij lage energie staat elk niveau apart en kunnen zijn parameters worden gefit: het opgeloste resonantiegebied. Hoger smelten de niveaus samen tot een fluctuerende band waarvan de statistiek bekend is maar de afzonderlijke pieken niet: het niet-opgeloste gebied, beschreven met gemiddelde parameters en, voor zelfafscherming, met waarschijnlijkheidstabellen die uit getrokken ladders zijn opgebouwd. Daarboven nemen Hauser–Feshbach en het optisch model het over.</p>
  <div class="ctl"><label for="av-r">Resolutie van het instrument (relatief)</label><input id="av-r" type="range" data-bind="res" min="0.2" max="3" step="0.05" value="1"><output data-show="res" data-fmt="2"></output></div>
  <p>De bibliotheek van INCOGNITA heeft nog geen opgelost resonantiegebied. Haar curven zijn gemiddelden volgens Hauser–Feshbach tot aan de laagste energieën; waar gemeten resonanties opgelost zijn, markeert de pagina <a href="data.html" data-keep-lang>Alle nucliden</a> de curve als gemiddelde. Resonantieparameters, en de daaruit opgebouwde dopplerverbrede puntsgewijze werkzame doorsneden, zijn in ontwikkeling.</p>
  <div class="aside">In de code: <code>physics/resonance/ladder.py</code> (afstanden uit stochastische matrices, breedten volgens Porter–Thomas, werkzame doorsneden voor één niveau, ensembles), <code>ladder_statistics.py</code> (de wetten getoetst op gemeten ladders), <code>compound/wfc.py</code> (de breedtefluctuatiecorrectie waar de gemiddelden naartoe convergeren). De formules voor Reich–Moore, ψ–χ en de resolutie in de afbeelding worden hier uitgerekend, met illustratieve parameters vergelijkbaar met uranium-238; de Hauser–Feshbach-motor, en dus de bibliotheek, berekent nog geen werkzame doorsneden in het resonantiegebied.</div>
</div>`,
};
(function () {
  const L = {
    // axes
    "{#} eV": "{#} eV", "{#} keV": "{#} keV",
    // scene 1: Reich-Moore against SLBW
    "potential scattering {#}πR′² ≈ {#} b": "potentiaalverstrooiing {#}πR′² ≈ {#} b",
    "Reich–Moore (dashed: single-level)": "Reich–Moore (gestippeld: één niveau)",
    "single-level Breit–Wigner (dashed: Reich–Moore)": "Breit–Wigner voor één niveau (gestippeld: Reich–Moore)",
    "total": "totaal", "capture": "vangst",
    // scene 2: statistics
    "spacings: Wigner": "afstanden: Wigner",
    "s = spacing / D₀": "s = afstand / D₀",
    "reduced neutron widths: Porter–Thomas": "gereduceerde neutronbreedten: Porter–Thomas",
    "y = Γn⁰ / ⟨Γn⁰⟩": "y = Γn⁰ / ⟨Γn⁰⟩",
    "{#} ladders · {#} spacings": "{#} ladders · {#} afstanden",
    "s = {#}": "s = {#}",
    // scene 3: Doppler
    "capture near the {#} eV resonance": "vangst bij de resonantie van {#} eV",
    "area {#} b·eV ({#} K: {#})": "oppervlak {#} b·eV ({#} K: {#})",
    "target nuclei at {#} K": "trefkernen bij {#} K",
    "target nuclei at rest": "trefkernen in rust",
    // scene 4: window averages
    "Hauser–Feshbach, no correction": "Hauser–Feshbach, zonder correctie",
    "with width fluctuations": "met breedtefluctuaties",
    "average capture cross section": "gemiddelde werkzame doorsnede voor vangst",
    "{#} levels around {#} eV: {#} b · HF {#} b without, {#} b with the correction": "{#} niveaus rond {#} eV: {#} b · HF {#} b zonder, {#} b met de correctie",
    // scene 5: regions
    "resolved": "opgelost", "unresolved": "niet opgelost", "averaged": "gemiddeld",
    "capture as measured with finite resolution · dashed: Hauser–Feshbach with fluctuations": "vangst zoals gemeten met eindige resolutie · gestippeld: Hauser–Feshbach met fluctuaties",
    "resolution reaches D₀/{#} at {#} eV": "resolutie bereikt D₀/{#} bij {#} eV",
    "resolution reaches D₀/{#} at {#} keV": "resolutie bereikt D₀/{#} bij {#} keV",
    "time of flight: the arrival time measures the energy": "vluchttijd: de aankomsttijd meet de energie",
  };
  // axis labels 1 b, 10⁻¹ b, 10² b ...
  for (const s of ["⁻¹", "¹", "²", "³", "⁴"]) L[`{#}${s} b`] = `{#}${s} b`;
  // labels that carry a cross section printed as "12 b" or "3.4k b"
  const B = ["{#} b", "{#}k b"];
  for (const b of B) {
    L[b] = b;
    for (const b2 of B) {
      L[`{#} eV · total ${b} · capture ${b2}`] = `{#} eV · totaal ${b} · vangst ${b2}`;
      L[`Γ = {#} meV · Δ = {#} meV · peak ${b} ({#} K: ${b2})`] = `Γ = {#} meV · Δ = {#} meV · piek ${b} ({#} K: ${b2})`;
    }
  }
  Object.assign(WT.L.labels, L);
})();
Object.assign(WT.L.glossary, {
  rMatrix: {
    term: "R-matrixtheorie", aliases: ["R-matrix"],
    short: "De exacte beschrijving van resonantiereacties met niveau-energieën en gereduceerde breedten binnen een kanaalstraal, aangesloten op vrije golven daarbuiten.",
    more: "Evaluaties fitten haar parameters aan gemeten resonanties. Breit–Wigner voor één en voor meer niveaus en de vorm van Reich–Moore zijn benaderingen van de volledige theorie.",
    chapter: "averages",
  },
  reichMoore: {
    term: "Reich–Moore", aliases: ["Reich–Moore"],
    short: "De benadering van de R-matrix die in de meeste evaluaties van zware kernen wordt gebruikt: de neutronkanalen worden exact behandeld, de vele fotonkanalen als één absorberende breedte per niveau.",
    chapter: "averages",
  },
  doppler: {
    term: "Dopplerverbreding", aliases: ["dopplerverbreding"],
    short: "Het uitsmeren van resonanties door de thermische beweging van de trefkernen: de piek zakt en de flanken worden breder, terwijl het oppervlak van een geïsoleerde piek gelijk blijft.",
    formula: "Δ = √(4 E kT / A)",
    chapter: "averages",
  },
  resolvedRegion: {
    term: "Opgelost en niet-opgelost resonantiegebied", aliases: ["opgeloste resonantiegebied", "opgelost resonantiegebied", "niet-opgeloste gebied", "niet-opgelost gebied"],
    short: "Onder een zekere energie wordt elke resonantie afzonderlijk gemeten (opgelost); daarboven zijn alleen hun gemiddelde parameters bekend (niet opgelost), totdat de gemiddelden glad worden.",
    more: "In het niet-opgeloste gebied wordt zelfafscherming behandeld met waarschijnlijkheidstabellen: verdelingen van de werkzame doorsnede die uit getrokken resonantieladders zijn opgebouwd.",
    chapter: "averages",
  },
});
