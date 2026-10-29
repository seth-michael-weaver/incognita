/* Dutch (Nederlands): hauser (Hoofdstuk 22, Hauser–Feshbach kanaal voor kanaal) */
WT.L.ch.hauser = {
  num: "Hoofdstuk 22", title: "Hauser–Feshbach, kanaal voor kanaal", short: "Hauser–Feshbach",
  lead: "Hoofdstuk 9 vertelde de competitie tussen de uitgangen als deuren. Hier staat de formule achter die deuren, kanaal voor kanaal, en de correctie die ze nodig heeft wanneer maar een paar kanalen open zijn.",
  html: `
<div class="step">
  <h3>Een transmissie voor elk kanaal</h3>
  <p>Een <b>kanaal</b> is een volledig uitgangsadres: welk deeltje, in welke toestand de restkern achterblijft, het baanimpulsmoment <i>l</i> en het totale impulsmoment <i>j</i> = <i>l</i> ± ½ van het deeltje. Het optisch model van hoofdstuk 5 geeft elk kanaal een <b>transmissiecoëfficiënt</b> <i>T<sub>lj</sub></i>. De kolommen zijn die van het invallende neutron, voor een trefkern met spin 0.</p>
  <div class="ctl"><label for="hf-e">Neutronenergie (MeV)</label><input id="hf-e" type="range" data-bind="lgE" min="-3" max="0.7" step="0.01" value="-0.3"><output data-show="Eshow" data-fmt="3"></output></div>
  <p>Bij 1 keV is alleen <i>l</i> = 0 open, met <i>T</i> ≈ 2π<i>S</i><sub>0</sub>√<i>E</i>, een paar procent. Elke extra eenheid <i>l</i> kost bij lage energie ongeveer een factor (<i>kR</i>)², dus de kolommen gaan één voor één open naarmate de energie stijgt. Elke kolom voedt de compoundkern met het gewicht g<sub>J</sub><i>T</i>:</p>
  <div class="formula">σ<sub>CN</sub> = (π/k²) Σ<sub>J,π</sub> g<sub>J</sub> Σ<sub>lj</sub> T<sub>lj</sub> ,  g<sub>J</sub> = (2J+1) / [(2s+1)(2I+1)]</div>
</div>
<div class="step">
  <h3>Eén spin en pariteit tegelijk</h3>
  <p>Impulsmoment en pariteit zijn behouden, dus de compoundkern vervalt in elke <i>J</i><sup>π</sup> onafhankelijk. Binnen één blok concurreert elk open uitgangskanaal met zijn eigen <i>T</i>: elastisch terug naar de grondtoestand, inelastisch naar elk aangeslagen niveau (een kolom telt de (<i>l</i>, <i>j</i>) op die aan dezelfde <i>J</i> koppelen), het continuüm boven 3,6 MeV, waarvan de bins als vele kanalen tellen, gewogen met de niveaudichtheid, en vangst, samengenomen in één piepkleine <i>T</i><sub>γ</sub> = 2π⟨Γ<sub>γ</sub>⟩/<i>D</i>. De hoogten staan op een logaritmische schaal.</p>
  <div class="ctl"><label for="hf-j">Blok van spin en pariteit</label><input id="hf-j" type="range" data-bind="jb" min="0" max="9" step="1" value="2" data-instant><output data-show="jbShow" data-fmt="0"></output></div>
  <div class="ctl"><label for="hf-e2">Neutronenergie (MeV)</label><input id="hf-e2" type="range" data-bind="lgE" min="-3" max="0.7" step="0.01" value="-0.3"><output data-show="Eshow" data-fmt="3"></output></div>
  <p>De balk onderaan is de verdeling volgens <b>Hauser–Feshbach</b>: elke uitgang krijgt het aandeel <i>T<sub>b</sub></i>/Σ<i>T<sub>c</sub></i> van wat via kanaal <i>a</i> binnenkwam. Onder 0,85 MeV zijn alleen elastisch en vangst open, en elastisch neemt bijna alles.</p>
  <div class="formula">σ<sub>ab</sub> = (π/k²) Σ<sub>J,π</sub> g<sub>J</sub> T<sub>a</sub> T<sub>b</sub> / Σ<sub>c</sub> T<sub>c</sub> · W<sub>ab</sub></div>
</div>
<div class="step">
  <h3>Breedtefluctuaties</h3>
  <p>De gewone formule onderschat de elastische verstrooiing een weinig, en de correctie brengt een beetje flux vanuit de andere uitgangen terug. Dit is waarom.</p>
  <p>Met <i>W<sub>ab</sub></i> = 1 vermenigvuldigt de formule gemiddelden. De resonanties achter die gemiddelden hebben breedten die spreiden (Porter–Thomas, hoofdstuk 15), en bij elastische verstrooiing is de breedte die het neutron binnenlaat dezelfde breedte die het weer naar buiten laat, dus de twee zijn gecorreleerd. Voor elastisch is het gemiddelde van de producten dan groter dan het product van de gemiddelden, en de andere uitgangen verliezen wat elastisch wint.</p>
  <div class="btns"><button class="btn ghost" data-act="w0" aria-pressed="false">Zonder correctie</button><button class="btn ghost" data-act="w1" aria-pressed="true">Moldauer</button></div>
  <div class="ctl"><label for="hf-e3">Neutronenergie (MeV)</label><input id="hf-e3" type="range" data-bind="lgE" min="-3" max="0.7" step="0.01" value="-0.3"><output data-show="Eshow" data-fmt="3"></output></div>
  <p>De labels geven σ met de correctie gedeeld door σ zonder. Onder de eerste inelastische drempel neemt elastisch al bijna de hele flux en verandert het nauwelijks, terwijl vangst 10 tot 25 procent verliest. Tussen 1 en 1,5 MeV wint de compound-elastische verstrooiing 15 tot 35 procent en verliest het eerste 2⁺-niveau ongeveer een derde. Naarmate meer niveaus en het continuüm opengaan, wordt de compound-elastische verstrooiing een klein deel van de flux: haar eigen factor stijgt naar 2, maar wat ze van de andere uitgangen afneemt krimpt, en hun factoren keren terug naar 1. In het recept van Moldauer krijgt elk kanaal een aantal vrijheidsgraden ν<sub>c</sub>, en is <i>W</i> een eendimensionale integraal, uitgerekend met de 32-puntskwadratuur van Gauss–Laguerre uit TALYS.</p>
  <div class="formula">W<sub>ab</sub> = (1 + 2δ<sub>ab</sub>/ν<sub>a</sub>) ∫₀^∞ dx Π<sub>c</sub> (1 + 2T<sub>c</sub>x / ν<sub>c</sub>ΣT)<sup>−(δ<sub>ac</sub>+δ<sub>bc</sub>+ν<sub>c</sub>/2)</sup></div>
  <div class="formula">ν<sub>c</sub> = 1.78 + (T<sub>c</sub><sup>1.212</sup> − 0.78) e<sup>−0.228 ΣT</sup></div>
</div>
<div class="step">
  <h3>Moldauer en HRTW</h3>
  <p>De curven voeren dezelfde berekening uit over het hele energiebereik: de verhouding voor compound-elastische verstrooiing, voor het eerste 2⁺-niveau en voor vangst, met Moldauer doorgetrokken en het recept van <b>HRTW</b> gestippeld. HRTW vervangt de integraal door een elastische factor <i>W<sub>a</sub></i> en effectieve transmissies <i>V<sub>a</sub></i> die iteratief worden bepaald.</p>
  <div class="ctl"><label for="hf-e4">Neutronenergie (MeV)</label><input id="hf-e4" type="range" data-bind="lgE" min="-3" max="0.7" step="0.01" value="-0.3"><output data-show="Eshow" data-fmt="3"></output></div>
  <div class="formula">σ<sub>ab</sub> ∝ V<sub>a</sub>V<sub>b</sub> / ΣV<sub>c</sub> · [1 + δ<sub>ab</sub>(W<sub>a</sub> − 1)] ,  V<sub>a</sub> = T<sub>a</sub> / [1 + (W<sub>a</sub> − 1) V<sub>a</sub>/ΣV]</div>
  <p>Voor elastisch en inelastisch komen de twee goed overeen; voor vangst in het keV-gebied haalt HRTW er tot 10 procent meer af. Tussen 0,85 en 2 MeV wint vangst zelfs: daar wordt de totale breedte gedomineerd door een paar fluctuerende neutronbreedten, en het gemiddelde van 1/Γ is groter dan 1/⟨Γ⟩. Beide recepten zijn fits aan het exacte resultaat van de theorie van stochastische matrices (GOE), dat TALYS ook als drievoudige integraal aanbiedt. INCOGNITA port alle drie (<code>widthmode</code> 1, 2, 3); Moldauer is de standaard, toegepast voor invallende neutronen tot aan de neutronseparatie-energie van de trefkern.</p>
</div>
<div class="step">
  <h3>Grenzen van de elastische versterking</h3>
  <p>Hoe groot kan de elastische opstoot worden? Tussen twee en drie keer, afhankelijk van of de resonanties apart staan of overlappen.</p>
  <p>De limieten verklaren de grootte van het effect. Neem <i>N</i> gelijke kanalen zonder vangst en varieer hun som ΣT, die 2π maal de verhouding van de gemiddelde totale breedte tot de niveauafstand is, Γ/<i>D</i>. Bij geïsoleerde resonanties (ΣT ≪ 1) en veel kanalen volgt elke breedte Porter–Thomas met één vrijheidsgraad en is de elastische versterking ⟨Γ<sub>a</sub>²⟩/⟨Γ<sub>a</sub>⟩² = 3. Wanneer resonanties sterk overlappen (ΣT ≫ 2π), fluctueert de werkzame doorsnede als een willekeurige golf (Ericson-fluctuaties) en zakt de versterking naar 2.</p>
  <div class="ctl"><label for="hf-n">Open kanalen N</label><input id="hf-n" type="range" data-bind="nch" min="2" max="60" step="1" value="30" data-instant><output data-show="nch" data-fmt="0"></output></div>
  <p>Voor geïsoleerde resonanties met <i>N</i> kanalen is de exacte waarde 3<i>N</i>/(<i>N</i>+2) (de ruit): met maar twee kanalen kan de versterking niet boven 1,5 uitkomen, omdat de totale breedte dan even sterk fluctueert als de elastische. Het recept van Moldauer reproduceert deze limiet; HRTW blijft eronder wanneer veel zwakke kanalen open zijn. Het inzetje tekent resonanties met de breedte die bij het bewegende punt hoort. In de formule van Moldauer is de limiet voor veel kanalen 1 + 2/ν: ν → 1 voor geïsoleerde resonanties en ν → 1,78 wanneer ze overlappen. Dat geeft 2,12 bij volledige overlap in plaats van 2: een kleine fout van de fit.</p>
  <div class="aside">In de code: <code>compound/prepare.py</code> (uitgangskanalen en hun transmissies per <i>J</i><sup>π</sup>), <code>compound/target.py</code> (de sommen van Hauser–Feshbach), <code>compound/wfc.py</code> (Moldauer, HRTW en GOE, geport uit TALYS). De afbeelding rekent dezelfde formules uit met illustratieve ingrediënten: transmissies van een harde bol voor een ijzerachtige trefkern, zeven niveaus, een continuüm met constante temperatuur en één samengenomen vangstkanaal.</div>
</div>`,
};
(function () {
  const L = {
    // scene 1: T_lj columns
    "T = {#}": "T = {#}",
    "l={#}": "l={#}",
    "hollow: j = l − ½ · solid: j = l + ½": "hol: j = l − ½ · dicht: j = l + ½",
    "compound nucleus": "compoundkern",
    "E = {#} keV · kR = {#}": "E = {#} keV · kR = {#}",
    "E = {#} MeV · kR = {#}": "E = {#} MeV · kR = {#}",
    "transmission Tₗⱼ of the incident neutron": "transmissie Tₗⱼ van het invallende neutron",
    // scene 2: one J^pi block
    "elastic": "elastisch", "cont.": "cont.",
    "level energy (MeV) under each column": "niveau-energie (MeV) onder elke kolom",
    "residual level (energy in MeV) · n×: number of (l, j) channels summed": "niveau van de restkern (energie in MeV) · n×: aantal opgetelde (l, j)-kanalen",
    "{#}/{#}⁺ block · in through l = {#}, Tₐ = {#}": "blok {#}/{#}⁺ · binnen via l = {#}, Tₐ = {#}",
    "{#}/{#}⁻ block · in through l = {#}, Tₐ = {#}": "blok {#}/{#}⁻ · binnen via l = {#}, Tₐ = {#}",
    "elastic {#} %": "elastisch {#} %", "higher {#} %": "hoger {#} %",
    "Hauser–Feshbach split: T / ΣT for each exit": "verdeling volgens Hauser–Feshbach: T / ΣT voor elke uitgang",
    // scene 3: with and without the correction
    "closed": "dicht",
    "compound elastic": "compound-elastisch", "first {#}⁺ level": "eerste {#}⁺-niveau", "higher levels": "hogere niveaus", "capture": "vangst",
    "{#} mb": "{#} mb",
    "with Moldauer's correction": "met de correctie van Moldauer",
    "Hauser–Feshbach without correction": "Hauser–Feshbach zonder correctie",
    "compound formation {#} mb at {#} keV": "compoundvorming {#} mb bij {#} keV",
    "compound formation {#} mb at {#} MeV": "compoundvorming {#} mb bij {#} MeV",
    // scene 4: ratio curves
    "{#} keV": "{#} keV", "{#} MeV": "{#} MeV",
    "{#}⁺ opens": "{#}⁺ gaat open", "continuum": "continuüm", "continuum opens": "continuüm gaat open",
    "elastic ×{#} (Moldauer) · ×{#} (HRTW)": "elastisch ×{#} (Moldauer) · ×{#} (HRTW)",
    "capture ×{#} (Moldauer) · ×{#} (HRTW)": "vangst ×{#} (Moldauer) · ×{#} (HRTW)",
    "first {#}⁺ ×{#} (Moldauer) · ×{#} (HRTW)": "eerste {#}⁺ ×{#} (Moldauer) · ×{#} (HRTW)",
    "solid: Moldauer · dashed: HRTW": "doorgetrokken: Moldauer · gestippeld: HRTW",
    "σ with correction / σ without": "σ met correctie / σ zonder",
    // scene 5: the limits 3 and 2
    "ΣT = {#}πΓ/D →": "ΣT = {#}πΓ/D →",
    "elastic enhancement Wₐₐ": "elastische versterking Wₐₐ",
    "T → {#} per channel": "T → {#} per kanaal",
    "exact, isolated: {#}N/(N+{#}) = {#}": "exact, geïsoleerd: {#}N/(N+{#}) = {#}",
    "Porter–Thomas: {#}": "Porter–Thomas: {#}", "Ericson: {#}": "Ericson: {#}",
    "{#} channels · ΣT = {#} · Wₐₐ = {#}": "{#} kanalen · ΣT = {#} · Wₐₐ = {#}",
    "isolated resonances: Γ ≪ D": "geïsoleerde resonanties: Γ ≪ D",
    "resonances begin to overlap": "resonanties beginnen te overlappen",
    "strongly overlapping: Γ ≫ D": "sterk overlappend: Γ ≫ D",
  };
  // labels that carry a cross section printed as "12 b" or "3.4k b"
  for (const b of ["{#} b", "{#}k b"]) {
    L[b] = b;
    L[`σ(CN) ≈ ${b}`] = `σ(CN) ≈ ${b}`;
    L[`compound nucleus · σ(CN) ≈ ${b}`] = `compoundkern · σ(CN) ≈ ${b}`;
  }
  Object.assign(WT.L.labels, L);
})();
Object.assign(WT.L.glossary, {
  hrtw: {
    term: "HRTW", aliases: ["HRTW"],
    short: "Een recept voor breedtefluctuaties van Hofmann, Richert, Tepel en Weidenmüller: een elastische factor per kanaal en effectieve transmissies die iteratief worden bepaald.",
    more: "Het werd, net als dat van Moldauer, gefit aan numerieke berekeningen met stochastische matrices. TALYS biedt het aan als widthmode 2; Moldauer (1) is de standaard en de exacte drievoudige GOE-integraal (3) de referentie.",
    chapter: "hauser",
  },
  ericson: {
    term: "Ericson-fluctuaties", aliases: ["Ericson-fluctuaties", "ericsonfluctuaties"],
    short: "Willekeurige fluctuaties van een werkzame doorsnede met de energie wanneer veel resonanties overlappen, op een energieschaal die door hun gemiddelde totale breedte wordt bepaald.",
    more: "Ze zijn de limiet bij sterke overlap van dezelfde statistiek die voor geïsoleerde resonanties breedten volgens Porter–Thomas geeft. Daar gaat de elastische versterkingsfactor naar 2.",
    chapter: "hauser",
  },
});
/* attributes referenced in the English chapter script (for the structure check): data-act="w0" data-act="w1" data-show="jbShow" */
