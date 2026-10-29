/* Dutch (Nederlands): fission (Hoofdstuk 12, splijting) */
WT.L.ch.fission = {
  num: "Hoofdstuk 12", title: "Splijting", short: "Splijting",
  lead: "De zwaarste kernen hebben een uitgang die lichtere missen: in plaats van één deeltje uit te stoten, scheurt de hele kern in tweeën. Dit is splijting.",
  html: `
<div class="step">
  <p>Een zware kern gedraagt zich als een druppel geladen vloeistof. De oppervlaktespanning (grijze pijlen) trekt hem rond; de protonen, allemaal positief geladen, duwen hem uit elkaar (rode pijlen). Bij uranium zijn die twee bijna even sterk.</p>
  <div class="ctl"><label for="fis-d">Rek de druppel uit</label><input id="fis-d" type="range" data-bind="def" min="0" max="1" step="0.01" value="0"><output data-show="def" data-fmt="2"></output></div>
  <p>Sleep om hem uit te rekken en kijk naar de stip op de kleine energiecurve eronder. Uitrekken voegt oppervlak toe, wat energie kost, maar spreidt de lading, wat energie vrijmaakt. Voorbij de top van de curve wint de lading: er vormt zich een hals en de helften vliegen met ongeveer 200 MeV uit elkaar.</p>
</div>
<div class="step">
  <h3>Het potentiaalenergieoppervlak</h3>
  <p>De curve is de energie voor elke vorm, van rond (links) tot gesplitst (rechts). Een gladde vloeistofdruppel geeft één heuvel, maar nucleonen vullen energieniveaus in groepen, <b>schillen</b> genoemd, en bij de zwaarste elementen kerft dat er een put in: een <b>barrière met twee bulten</b>, waar de kern in een uitgerekte vorm kan blijven hangen.</p>
  <p>De motor neemt deze curve niet aan: hij leest haar punt voor punt uit een microscopische berekening van de energie bij elke vervorming (mate van uitrekking).</p>
</div>
<div class="step">
  <h3>Barrièredoordringing</h3>
  <p>Het bolletje is de aangeslagen kern in het eerste dal, op de excitatie-energie van de oranje gestippelde lijn, onder de top van 6 MeV. Klassiek kan hij nooit oversteken; de quantummechanica laat hem door het donkere, verboden deel <b>tunnelen</b>, met een kans <i>T</i> die exponentieel daalt naarmate dat deel dikker wordt.</p>
  <div class="ctl"><label for="fis-e">Excitatie-energie</label><input id="fis-e" type="range" data-bind="E" min="3" max="8" step="0.05" value="5"><output data-show="E" data-fmt="2"></output></div>
  <p>Verhoog de energie en kijk hoe <i>T</i> stijgt terwijl het verboden deel dunner wordt. De vuistregel uit het leerboek (Hill–Wheeler) behandelt de top als een parabool (blauw gestippeld). De motor volgt de echte vorm, die lager breder is, dus ver onder de top is zijn kans kleiner. <i>K</i> meet hoeveel heuvel er in de weg staat.</p>
  <div class="formula">T = 1 / (1 + e<sup>2K</sup>),  K = ∫ √(2μ(V−E)) dβ / ħ</div>
</div>
<div class="step">
  <h3>Overgangstoestanden</h3>
  <p>De deuren op de top zijn de <b>overgangstoestanden</b>, de quantumtoestanden van de kern die over de barrière is uitgerekt. Elk heeft een spin en pariteit (0⁺, 2⁻, …) en werkt als een poort; de verlichte opening toont hoe ver ze openstaat. Een kern gaat alleen door poorten die bij zijn eigen spin en pariteit passen, en elke poort gaat geleidelijk open naarmate de energie haar hoogte passeert.</p>
  <div class="ctl"><label for="fis-e2">Excitatie-energie</label><input id="fis-e2" type="range" data-bind="E" min="3" max="8" step="0.05" value="5"><output data-show="E" data-fmt="2"></output></div>
  <div class="btns"><button class="btn ghost" data-act="jpAll">Elke spin</button><button class="btn ghost" data-act="jp0">Compound 0⁺</button><button class="btn ghost" data-act="jp1">Compound 1⁻</button></div>
  <p>Kies één spin en pariteit: alleen passende poorten tellen, en de totale opening daalt. Hoger op dringen de poorten samen tot een <b>continuüm</b>, en de motor telt ze via hun dichtheid, zoals hij dat ook bij gewone niveaus doet.</p>
</div>
<div class="step">
  <h3>Barrières met twee bulten</h3>
  <p>Nu beide heuvels, elk met een poort (de cirkel; het gevulde deel is hoe ver ze openstaat). Kernen komen van links; wie de eerste heuvel over komt, zit gevangen in de put en kaatst heen en weer tussen de poorten tot hij er aan de ene of de andere kant uit gaat. De kansen combineren als weerstanden in serie, dus de moeilijkste heuvel beslist grotendeels.</p>
  <div class="ctl"><label for="fis-b">Hoogte buitenste heuvel</label><input id="fis-b" type="range" data-bind="Bb" min="3.5" max="7.5" step="0.05" value="5.6"><output data-show="Bb" data-fmt="2"></output></div>
  <div class="formula">1/T = 1/T<sub>A</sub> + 1/T<sub>B</sub></div>
  <p>Sleep de buitenste heuvel omhoog en kijk hoe de stroom naar splijting stokt, hoe ver de binnenste poort ook openstaat.</p>
</div>
<div class="step">
  <h3>Splijting met meerdere kansen</h3>
  <p>Uranium-238 absorbeert het neutron en wordt uranium-239 met excitatie <i>E</i>* (gestippelde lijn). Als het niet splijt, kan het in plaats daarvan een neutron uitzenden; de lijn zakt, en het achtergebleven uranium-238, nog steeds heet, probeert zijn eigen barrière: splijting <b>bij de tweede kans</b>, (n,n′f). De stapels verzamelen hoe elke kern eindigde.</p>
  <div class="ctl"><label for="fis-en">Neutronenergie</label><input id="fis-en" type="range" data-bind="En" min="0" max="25" step="0.1" value="7"><output data-show="En" data-fmt="1"></output></div>
  <p>Verhoog de energie en latere pogingen beginnen te slagen; rond 12 MeV gaat een derde kans open. Elke nieuwe kans verschijnt als een trede in de gemeten <b>werkzame doorsnede voor splijting</b>, hoe waarschijnlijk het is dat de kern splijt: de kleine grafiek rechtsboven tekent die treden, met jouw energie gemarkeerd. De motor berekent hoe vaak hij splijt, niet in welke brokstukken.</p>
  <div class="aside">In de code: <code>fission/wkb.py</code> (het pad van vervormingsenergie en de WKB-integralen), <code>fission/barriers.py</code> (Hill–Wheeler, overgangstoestanden, de niveaudichtheid op de barrière), <code>fission/transmission.py</code> (bulten in serie, T<sub>fis</sub> per spin en pariteit), <code>fission/chain.py</code> (barrières voor elke kern van de cascade).</div>
</div>`,
};
Object.assign(WT.L.labels, {
  // drop
  "surface tension pulls it round": "oppervlaktespanning trekt hem rond",
  "the protons push it apart": "de protonen duwen hem uit elkaar",
  "a charged drop, nearly round": "een geladen druppel, bijna rond",
  "stretched: more surface, charge further apart": "uitgerekt: meer oppervlak, lading verder uiteen",
  "a neck forms": "er vormt zich een hals",
  "two fragments, carrying about {#} MeV": "twee brokstukken, met ongeveer {#} MeV",
  "energy of the drop": "energie van de druppel",
  // landscape
  "ground state": "grondtoestand", "inner barrier": "binnenste barrière", "second well": "tweede put",
  "outer barrier": "buitenste barrière", "split (scission)": "gesplitst (scissie)", "one smooth hill": "één gladde heuvel",
  "shell effects carving the second well": "schileffecten kerven de tweede put uit",
  "round → stretched → necked → split": "rond → uitgerekt → met hals → gesplitst",
  "stretch (deformation) →": "uitrekking (vervorming) →",
  // tunnel
  "forbidden zone": "verboden zone",
  "excitation {#} MeV": "excitatie {#} MeV",
  "hilltop {#} MeV": "top {#} MeV",
  "parabola fit": "parabool-fit",
  "passes over the top": "gaat over de top",
  // gates
  "continuum: a density": "continuüm: een dichtheid",
  "continuum of gates: counted as a density": "continuüm van poorten: geteld als dichtheid",
  "gates: transition states": "poorten: overgangstoestanden",
  "E = {#} MeV": "E = {#} MeV",
  "all gates: total opening {#}": "alle poorten: totale opening {#}",
  "all gates: total opening {#} + {#} from the continuum": "alle poorten: totale opening {#} + {#} uit het continuüm",
  "{#}⁺ gates only: total opening {#}": "alleen {#}⁺-poorten: totale opening {#}",
  "{#}⁺ gates only: total opening {#} + {#} from the continuum": "alleen {#}⁺-poorten: totale opening {#} + {#} uit het continuüm",
  "{#}⁻ gates only: total opening {#}": "alleen {#}⁻-poorten: totale opening {#}",
  "{#}⁻ gates only: total opening {#} + {#} from the continuum": "alleen {#}⁻-poorten: totale opening {#} + {#} uit het continuüm",
  // series
  "nuclei arriving →": "aankomende kernen →",
  "trapped in the well": "gevangen in de put",
  "fission": "splijting",
  "so far: {#} through, {#} turned back": "tot nu toe: {#} erdoor, {#} teruggekeerd",
  // chance
  "²³⁹U*  E* = {#} MeV": "²³⁹U*  E* = {#} MeV", "²³⁸U*  E* = {#} MeV": "²³⁸U*  E* = {#} MeV", "²³⁷U*  E* = {#} MeV": "²³⁷U*  E* = {#} MeV",
  "↑ E* above the picture": "↑ E* boven de afbeelding",
  "fission!": "splijting!",
  "emits a neutron, cools, tries again": "zendt een neutron uit, koelt af, probeert opnieuw",
  "too cool to split: a photon, no fission": "te koel om te splijten: een foton, geen splijting",
  "attempt {#}: barrier {#} % open": "poging {#}: barrière {#} % open",
  "{#}st chance (n,f)": "{#}e kans (n,f)", "{#}nd chance (n,n′f)": "{#}e kans (n,n′f)", "{#}rd chance (n,{#}nf)": "{#}e kans (n,{#}nf)",
  "{#}st (n,f)": "{#}e (n,f)", "{#}nd (n,n′f)": "{#}e (n,n′f)", "{#}rd (n,{#}nf)": "{#}e (n,{#}nf)",
  "no fission": "geen splijting",
});
// labels carrying a transmission T, printed either as 0.12 or as 3.4·10⁻5 (two number shapes)
(function () {
  const L = WT.L.labels, F = ["{#}", "{#}·{#}⁻{#}"];
  for (const a of F) {
    L[`inner gate T ≈ ${a}`] = `binnenste poort T ≈ ${a}`;
    L[`outer gate T ≈ ${a}`] = `buitenste poort T ≈ ${a}`;
    L[`both hills: T ≈ ${a}, {#} % of what arrives gets through`] = `beide heuvels: T ≈ ${a}, {#} % van wat aankomt komt erdoor`;
    for (const b of F) {
      L[`T ≈ ${a} real shape · ${b} parabola`] = `T ≈ ${a} echte vorm · ${b} parabool`;
      L[`chance to tunnel T ≈ ${a} on the real shape, ${b} on the parabola`] = `tunnelkans T ≈ ${a} bij de echte vorm, ${b} bij de parabool`;
    }
  }
})();
Object.assign(WT.L.labels, {
  "chance to split vs neutron energy": "splijtingskans tegen neutronenergie",
  "{#}nd": "{#}e",
  "{#}rd": "{#}e",
});
