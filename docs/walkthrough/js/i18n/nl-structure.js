/* Dutch (Nederlands): structure (Hoofdstuk 1, waar een kern uit bestaat) */
WT.L.ch.structure = {
  num: "Hoofdstuk 1", title: "Waar een kern uit bestaat", short: "Structuur",
  lead: "Voordat de motor (onze reactiesoftware) ook maar één neutron afschiet, heeft hij een beschrijving van de trefkern nodig: hoe stevig die bij elkaar blijft, in welke energietoestanden hij kan zijn en welke vorm hij heeft.",
  html: `
<div class="step">
  <p>De afbeelding toont een ijzerkern: een dicht opeengepakte bol van <em class="p">protonen</em> en <em class="n">neutronen</em> (<b>nucleonen</b>), bijeengehouden door de <b>sterke kernkracht</b>, die maar een heel korte dracht heeft. Elk nucleon voelt alleen zijn naaste buren, dus elke kern heeft ongeveer dezelfde dichtheid.</p>
  <div class="ctl"><label for="st-n">Neutronen (ijzer heeft 26 protonen)</label><input id="st-n" type="range" data-bind="N" min="24" max="38" step="1" value="30" data-instant><output data-show="N" data-fmt="0"></output></div>
  <p>Sleep om neutronen toe te voegen of weg te halen; elke keuze is een ander <b>isotoop</b>. De staafjes tonen de <b>bindingsenergie</b> per nucleon in MeV (miljoen elektronvolt): de energie die nodig is om de kern uit elkaar te trekken. Die is het grootst rond de stabiele isotopen.</p>
</div>
<div class="step">
  <h3>Separatie-energieën</h3>
  <p>De energie om één deeltje eruit te halen is zijn <b>separatie-energie</b>: <i>S<sub>n</sub></i> voor een neutron, <i>S<sub>p</sub></i> voor een proton, <i>S<sub>α</sub></i> voor een <b>alfadeeltje</b> (twee protonen en twee neutronen die aan elkaar gebonden zijn). De afbeelding toont de kern als een put, met de energie naar boven; elke keer dat je trekt, wordt het bovenste deeltje voorbij de gestippelde lijn ‘vrij’ getild, en de meter houdt de kosten bij.</p>
  <div class="btns"><button class="btn ghost" data-act="pn">Haal een neutron eruit</button><button class="btn ghost" data-act="pp">Haal een proton eruit</button><button class="btn ghost" data-act="pa">Haal een alfa eruit</button></div>
  <p>De motor berekent elk ervan als het verschil tussen twee kernmassa's: gemeten waar dat kan, uit een massamodel waar dat niet kan.</p>
  <div class="ctl"><label for="st-n2">Neutronen</label><input id="st-n2" type="range" data-bind="N" min="24" max="38" step="1" value="30" data-instant><output data-show="N" data-fmt="0"></output></div>
  <p>Sleep het aantal neutronen en haal opnieuw een neutron eruit: <i>S<sub>n</sub></i> zigzagt, omdat nucleonen paren vormen en bij een even aantal het laatste steviger vastzit. Een reactie kan een deeltje alleen uitstoten als ze genoeg energie meebrengt om deze prijs te betalen. Deze kosten zijn de <b>drempels</b> van de hele berekening.</p>
</div>
<div class="step">
  <h3>Aangeslagen toestanden en gammaverval</h3>
  <p>Een kern kan alleen bepaalde exacte hoeveelheden extra energie bevatten: de lijnen, hier voor ijzer-56, met de <b>grondtoestand</b> onderaan. Elk niveau heeft een <b>spin</b> <i>J</i> (impulsmoment) en een <b>pariteit</b>, + of − (of zijn golf er in een spiegel hetzelfde uitziet); 2<sup>+</sup> betekent spin 2, pariteit +.</p>
  <p>Het oranje bolletje is een kern op een hoog niveau. Hij valt niveau voor niveau omlaag, en bij elke sprong komt er een <em class="g">foton</em> (een gammastraal) vrij dat het energieverschil meeneemt. De dikte en het percentage van de paden zijn de gemeten kansen op elke sprong, de <b>vertakkingsverhoudingen</b>.</p>
  <div class="btns"><button class="btn" data-act="drop">Breng de kern in aangeslagen toestand</button></div>
  <p>Druk er een paar keer op: hetzelfde niveau bereikt de grondtoestand langs verschillende routes. De motor houdt per kern zo'n dertig gemeten niveaus bij, met hun kansen; hoger op behandelt hij de opeengepakte niveaus als een glad <b>continuüm</b>. Boven de gestippelde lijn, <i>S<sub>n</sub></i>, kan de kern een neutron uitzenden.</p>
</div>
<div class="step">
  <h3>Isomeren: langlevende aangeslagen toestanden</h3>
  <p>Een niveau waarvan de enige weg omlaag een grote spinverandering Δ<i>J</i> vraagt, vervalt heel langzaam. Rechts zitten 64 kernen op zo'n niveau; elke kern wacht een willekeurige tijd, valt dan omlaag en er springt een <em class="g">foton</em> uit. Na één <b>halveringstijd</b> is de helft gevallen.</p>
  <div class="ctl"><label for="st-dj">Spinverandering ΔJ</label><input id="st-dj" type="range" data-bind="dJ" min="1" max="5" step="1" value="2" data-instant><output data-show="dJ" data-fmt="0"></output></div>
  <div class="ctl"><label for="st-eg">Fotonenergie (MeV)</label><input id="st-eg" type="range" data-bind="Eg" min="0.05" max="1.5" step="0.05" value="0.3"><output data-show="Eg" data-fmt="2"></output></div>
  <div class="btns"><button class="btn ghost" data-act="excite">Breng ze allemaal in aangeslagen toestand</button></div>
  <p>Verhoog Δ<i>J</i> en het uitspringen gaat trager: elke extra eenheid spin maakt het wachten honderdduizend keer langer of meer, en een lagere fotonenergie verlengt het ook (op een logaritmische schaal getoond). Een niveau dat langer leeft dan ongeveer een seconde is een <b>isomeer</b>, en de motor behandelt het als een eindpunt, net als de grondtoestand.</p>
</div>
<div class="step">
  <h3>Kernvervorming</h3>
  <p>Veel kernen zijn niet rond. <i>β₂</i> (‘bèta-twee’) meet de uitrekking: 0 is een bol, positief is uitgerekt als een rugbybal, negatief is platgedrukt tot een schijf. De ladder rechts toont de niveaus die elke soort oplevert.</p>
  <p>Een uitgerekte kern kan roteren en geeft dan niveaus 0<sup>+</sup>, 2<sup>+</sup>, 4<sup>+</sup>, 6<sup>+</sup> met afstanden die groeien als <i>J</i>(<i>J</i>+1): een <b>rotor</b>. Een ronde kern kan rimpelen; elke eenheid rimpeling, een <b>fonon</b>, voegt dezelfde energie toe, dus zijn niveaus liggen op gelijke afstanden: een <b>vibrator</b>.</p>
  <div class="ctl"><label for="st-beta">Vervorming β₂</label><input id="st-beta" type="range" data-bind="beta" min="-0.3" max="0.45" step="0.01" value="0.28"><output data-show="beta" data-fmt="2"></output></div>
  <div class="btns"><button class="btn ghost" data-act="still">Stil</button><button class="btn ghost" data-act="vib">Trillend</button><button class="btn ghost" data-act="rot">Roterend</button></div>
  <p>Sleep <i>β₂</i> en druk op de knoppen: een grotere uitrekking trekt de niveaus van de rotor dichter naar elkaar. Een vibrator is gemiddeld rond, dus het schuifje rust terwijl hij rimpelt; en een bol kan in deze zin niet roteren (draaien verandert niets), dus bij <i>β₂</i> = 0 verdwijnt de rotorband. De motor slaat per kern vervormingen op en een label: sferisch, vibrator of rotor. Hoofdstuk 6 laat zien hoe een passerend neutron die gebruikt.</p>
</div>
<div class="step">
  <h3>Resonantieparameters boven de neutronendrempel</h3>
  <p>Een langzaam neutron dat zich bij de trefkern voegt, komt net boven <i>S<sub>n</sub></i> terecht, in het kleine kader links. Het rechterpaneel vergroot dat kader duizenden keren, met de neutronenergie van links naar rechts.</p>
  <div class="ctl"><label for="st-fe">Bundelenergie</label><input id="st-fe" type="range" data-bind="fe" min="0" max="1" step="0.001" value="0.3" data-instant><output id="st-fe-out"></output></div>
  <div class="btns"><button class="btn ghost" data-act="fplay" id="st-fplay">Doorloop pauzeren</button></div>
  <p>Bij de meeste energieën gaat de bundel er gewoon doorheen. Bij bepaalde exacte energieën passen neutron plus kern precies op een verborgen niveau en wordt een groot deel van de bundel opgenomen: een <b>resonantie</b>. Op een piek zwelt de getekende kern op: geen echte verandering van grootte, maar het grotere doel dat het neutron in feite ziet wanneer zijn golf overlapt met die van de kern. Daarna geeft de kern de energie terug als een <em class="g">foton</em> of een neutron. De curve toont het opgenomen deel; de streepjes markeren elke gevonden resonantie.</p>
  <div class="btns"><button class="btn ghost" data-act="fFe">IJzer-56</button><button class="btn ghost" data-act="fAu">Goud-197</button><button class="btn ghost" data-act="fU">Uranium-238</button></div>
  <p>Elke kern heeft zijn eigen streepjescode, op zijn eigen schaal: duizenden elektronvolt tussen de resonanties van ijzer, tientallen bij goud en uranium. Drie gemiddelden vatten het samen: <i>D₀</i>, de gemiddelde afstand; ⟨Γ<sub>γ</sub>⟩, de <b>fotonbreedte</b>, bijna hetzelfde voor elke piek; en <i>S₀</i>, de <b>sterktefunctie</b>, hoe makkelijk een langzaam neutron binnenkomt.</p>
  <p>Elk ervan toetst een latere stap. De niveaudichtheidsparameters van de motor zijn kern voor kern aan <i>D₀</i> gefit; ⟨Γ<sub>γ</sub>⟩ toetst de fotonemissie, <i>S₀</i> het optisch model van het volgende hoofdstuk. Voor niet-gemeten kernen gebruikt de motor trends die over veel kernen zijn gefit.</p>
  <div class="aside">In de code: <code>structure/masses.py</code> (gemeten massa's, modelmassa's daarbuiten, separatie-energieën), <code>structure/levels.py</code> (discrete niveaus, vertakkingen, isomeren, geschatte spins) en <code>levjpar.py</code> (optioneel, standaard uit: schat een opgegeven spin die voor de kern onmogelijk is opnieuw), <code>structure/deformation.py</code> (β₂ en het label sferisch/vibrator/rotor) en <code>collrule.py</code> (optioneel, standaard uit: kiest het label van de trefkern op basis van zijn gemeten niveaus), <code>structure/resonances.py</code> (D₀, S₀, S₁, ⟨Γγ⟩).</div>
</div>`,
};
(function () {
  const L = {
    // scene: packed drop
    "{#}Fe": "{#}Fe",
    "{#} protons · {#} neutrons": "{#} protonen · {#} neutronen",
    "binding energy per nucleon: about {#} MeV": "bindingsenergie per nucleon: ongeveer {#} MeV",
    "binding per nucleon, one bar per isotope →": "binding per nucleon, één staaf per isotoop →",
    // scene: well
    "free": "vrij",
    "free: outside the nucleus": "vrij: buiten de kern",
    "neutrons": "neutronen",
    "protons": "protonen",
    "an alpha forms from the top pairs": "de bovenste paren vormen een alfa",
    "neutron {#}": "neutron {#}",
    "proton {#}": "proton {#}",
    "alpha {#}": "alfa {#}",
    "n {#}": "n {#}",
    "p {#}": "p {#}",
    "energy paid": "betaalde energie",
    "energy to pull": "energie om eruit",
    "(MeV)": "(MeV)",
    "each one out (MeV)": "te halen (MeV)",
    "higher mark =": "hoger streepje =",
    "harder to remove": "moeilijker te verwijderen",
    "pulling out a neutron: {#} MeV paid": "neutron eruit: {#} MeV betaald",
    "pulling out a proton: {#} MeV paid": "proton eruit: {#} MeV betaald",
    "pulling out an alpha: {#} MeV paid": "alfa eruit: {#} MeV betaald",
    // scene: levels and gamma drops
    "continuum: too many levels to list": "continuüm: te veel niveaus om op te sommen",
    "neutron threshold Sₙ ≈ {#} MeV": "neutrondrempel Sₙ ≈ {#} MeV",
    "ground state": "grondtoestand",
    "MeV": "MeV",
    "each line: an energy, a spin J and a parity (±)": "elke lijn: een energie, een spin J en een pariteit (±)",
    "path width and % = measured odds of each hop": "paddikte en % = gemeten kans op elke sprong",
    // scene: isomer
    "ground": "grond",
    "J = {#}/{#}": "J = {#}/{#}",
    "ΔJ = {#}": "ΔJ = {#}",
    "still excited: {#} of {#}": "nog aangeslagen: {#} van {#}",
    "longer than a second: an isomer, a stop in its own right": "langer dan een seconde: een isomeer, een eindstation op zich",
    "shown slowed down (log scale)": "vertraagd getoond (log. schaal)",
    "shown slowed down: the slower they pop, the longer the real wait (log scale)": "vertraagd: hoe trager ze uitspringen, hoe langer het echte wachten (log. schaal)",
    // scene: shape
    "ripples at the surface: a vibrator": "rimpelt aan het oppervlak: een vibrator",
    "stretched and rotating: a rotor": "uitgerekt en roterend: een rotor",
    "round: a sphere": "rond: een bol",
    "stretched (prolate): a football": "uitgerekt (prolaat): een rugbybal",
    "squashed: an oblate disc": "platgedrukt: een oblate schijf",
    "{#} phonons": "{#} fononen",
    "no regular": "geen regelmatig",
    "level pattern": "niveaupatroon",
    "spacing grows like J(J+{#})": "afstand groeit als J(J+{#})",
    "equal steps, one phonon each": "gelijke stappen, één fonon per stap",
    "its lowest levels": "zijn laagste niveaus",
    "β₂ = {#}": "β₂ = {#}",
    // scene: resonance fingerprint
    "continuum": "continuüm",
    "Sₙ ≈ {#} MeV": "Sₙ ≈ {#} MeV",
    "slow neutron": "langzaam neutron",
    "a slow neutron lands here:": "een langzaam neutron komt hier:",
    "lands here": "komt hier",
    "Sₙ + its kinetic energy": "Sₙ + zijn kinetische energie",
    "×{#} million": "×{#} miljoen",
    "×{#} thousand": "×{#} duizend",
    "magnified": "vergroot",
    "swells on a peak: the size the neutron effectively “sees” (waves overlap), not a real size change": "zwelt op een piek: de grootte die het neutron in feite ‘ziet’ (golven overlappen), geen echte groottewijziging",
    "share taken in": "opgenomen deel",
    "share of the beam taken in": "opgenomen deel van de bundel",
    "{#} (Sₙ)": "{#} (Sₙ)",
    "{#} = exactly Sₙ": "{#} = precies Sₙ",
    "{#} keV": "{#} keV",
    "{#} eV": "{#} eV",
    "neutron energy →": "neutronenergie →",
    "neutron's kinetic energy →": "kinetische energie van het neutron →",
    "D₀ ≈ {#} keV: the average gap": "D₀ ≈ {#} keV: de gemiddelde afstand",
    "D₀ ≈ {#} eV: the average gap": "D₀ ≈ {#} eV: de gemiddelde afstand",
    "S₀: average peak strength": "S₀: gemiddelde piekhoogte",
    "S₀: how strong the peaks are on average (how easily a neutron gets in)": "S₀: hoe sterk de pieken gemiddeld zijn (hoe makkelijk een neutron binnenkomt)",
    "⟨Γγ⟩ ≈ {#} eV: photon width": "⟨Γγ⟩ ≈ {#} eV: fotonbreedte",
    "⟨Γγ⟩ ≈ {#} eV: photon width, about the same for every peak": "⟨Γγ⟩ ≈ {#} eV: fotonbreedte, ongeveer gelijk voor elke piek",
    "⟨Γγ⟩ ≈ {#} eV: a hairline here": "⟨Γγ⟩ ≈ {#} eV: hier haarfijn",
    "⟨Γγ⟩ ≈ {#} eV: a hairline here; neutrons widen these peaks": "⟨Γγ⟩ ≈ {#} eV: hier haarfijn; neutronen verbreden deze pieken",
    "peaks drawn about {#}× wider than life so they show": "pieken zo'n {#}× breder getekend dan echt, zodat je ze ziet",
  };
  // beam readout and per-target labels
  for (const u of ["keV", "eV"]) L[`beam of neutrons at {#} ${u}`] = `neutronenbundel van {#} ${u}`;
  const EL = { iron: "ijzer", gold: "goud", uranium: "uranium" };
  for (const en in EL) {
    L[`${en}{#} levels`] = `niveaus van ${EL[en]}{#}`;
    L[`${en}{#}: took in {#} of the last {#}`] = `${EL[en]}{#}: nam {#} van de laatste {#} op`;
  }
  // isomer half-life in every unit fmtTime can produce
  const TU = { femtoseconds: "femtoseconden", picoseconds: "picoseconden", nanoseconds: "nanoseconden", microseconds: "microseconden",
    milliseconds: "milliseconden", seconds: "seconden", minutes: "minuten", hours: "uur", days: "dagen", years: "jaar" };
  for (const en in TU) L[`half-life about {#} ${en}`] = `halveringstijd ongeveer {#} ${TU[en]}`;
  L["half-life about {#}×{#}^{#} years"] = "halveringstijd ongeveer {#}×{#}^{#} jaar";
  Object.assign(WT.L.labels, L);
})();
