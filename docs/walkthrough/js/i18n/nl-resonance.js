/* Dutch (Nederlands): resonance (Hoofdstuk 15, scherpe pieken) */
WT.L.ch.resonance = {
  num: "Hoofdstuk 15", title: "Scherpe pieken", short: "Resonanties",
  lead: "Bij een laag genoeg energie ziet een neutron geen gladde, uitgemiddelde kern meer. Het ziet de afzonderlijke energieniveaus van de compoundkern, één voor één.",
  html: `
<div class="step">
  <p>Elke piek is één <b>resonantie</b>: een energieniveau van de compoundkern waarin een neutron van precies die energie kan vallen. De hoogte is de werkzame doorsnede voor <b>vangst</b> daar (neutron geabsorbeerd, fotonen eruit) op een logaritmische schaal; de breedte is de resonantiebreedte Γ, ongeveer honderd keer breder getekend dan ze is.</p>
  <div class="ctl"><label for="res-e">Neutronenergie (eV)</label><input id="res-e" type="range" data-bind="En" min="0.5" max="300" step="0.1" value="30"><output data-show="En" data-fmt="1"></output></div>
  <p>Het neutron hupt verder in energie; waar het landt, kan het worden ingevangen, in een flits van fotonen. Op een piek is de werkzame doorsnede duizenden barn en is vangst bijna zeker; tussen de pieken is ze een paar barn. Sleep de energie om het op een piek te parkeren, en daarna tussen twee pieken.</p>
</div>
<div class="step">
  <h3>Pieken houden afstand</h3>
  <p>De middelste rij toont hoe echte niveaus liggen: twee niveaus met dezelfde spin en pariteit stoten elkaar af, dus bijna-samenvallen is zeldzaam. De <b>theorie van stochastische matrices</b> beschrijft dit patroon. Echt willekeurige posities (bovenste rij) klonteren en laten gaten.</p>
  <div class="btns"><button class="btn" data-act="again">Opnieuw trekken</button></div>
  <p>Trek opnieuw voor een nieuwe steekproef. ⟨r̃⟩ vergelijkt elke afstand met de volgende: ongeveer 0,39 bij willekeurig, 0,53 bij elkaar afstotende niveaus; de code gebruikt het afstotende patroon. Het mengen van twee reeksen, bijvoorbeeld twee spins (onderste rij), verbergt de afstoting gedeeltelijk.</p>
</div>
<div class="step">
  <h3>Hoogten lopen wild uiteen</h3>
  <p>Nu is de hoogte van elke piek haar <b>neutronbreedte</b> Γ<sub>n</sub> op een lineaire schaal: hoe sterk het niveau aan een neutron koppelt. Het gele kapje is haar γ-breedte Γ<sub>γ</sub>, hoe snel ze fotonen uitzendt; die telt honderden fotonpaden bij elkaar op, dus ze is voor elk niveau bijna gelijk.</p>
  <div class="btns"><button class="btn" data-act="roll">Gooi een breedte</button><button class="btn ghost" data-act="equal">Gelijke breedten</button><button class="btn ghost" data-act="pt">Porter–Thomas</button></div>
  <p>Een niveau heeft maar één manier om uiteen te vallen in neutron plus trefkern, dus zijn breedte gedraagt zich als het kwadraat van één getal uit een klokkromme. Gooi er een: het balletje landt op <i>x</i>, <i>x</i>² wordt de hoogte van de volgende piek, en er valt een stip in de stapel. De stapel hoopt zich op bij nul met een lange staart, de wet van <b>Porter–Thomas</b>: de meeste niveaus zijn zwak, een paar enorm. Gelijke breedten toont in plaats daarvan een rij gemiddelde pieken.</p>
</div>
<div class="step">
  <h3>Een ladder uit vier getallen</h3>
  <p>De pieken komen nu uit vier gemiddelden die je kunt instellen. Voor een niet-gemeten kern kunnen alleen deze gemiddelden worden voorspeld: de gemiddelde afstand <i>D</i><sub>0</sub>; de <b>sterktefuncties</b> <i>S</i><sub>0</sub> en <i>S</i><sub>1</sub>, de gemiddelde neutronbreedte per eenheid afstand voor s-golf- (frontale) en p-golfneutronen (buiten het midden); en de gemiddelde γ-breedte. Hieruit bouwt de code een <b>resonantieladder</b>: één willekeurige verzameling niveaus met die gemiddelden.</p>
  <div class="ctl"><label for="res-d0">Afstand D₀ (eV)</label><input id="res-d0" type="range" data-bind="D0" min="3" max="60" step="0.5" value="20"><output data-show="D0" data-fmt="1"></output></div>
  <div class="ctl"><label for="res-s0">Sterkte S₀ (×10⁻⁴)</label><input id="res-s0" type="range" data-bind="S0" min="0.2" max="3" step="0.05" value="1"><output data-show="S0" data-fmt="2"></output></div>
  <div class="ctl"><label for="res-gg">γ-breedte ⟨Γγ⟩ (meV)</label><input id="res-gg" type="range" data-bind="Gg" min="10" max="80" step="1" value="23"><output data-show="Gg" data-fmt="0"></output></div>
  <p>Sleep <i>D</i><sub>0</sub> en de pieken spreiden zich uit of dringen samen. Dichte pieken zijn s-golfniveaus (positieve pariteit), omlijnde pieken p-golfniveaus (negatieve pariteit). Neutronbreedten groeien als √<i>E</i> voor s-golven en als <i>E</i><sup>3/2</sup> voor p-golven, dus de omlijnde pieken beginnen laag en groeien naar rechts.</p>
</div>
<div class="step">
  <h3>Omlaag tot thermisch</h3>
  <p>Dezelfde pieken op een logaritmische energieschaal, tot duizendsten van een eV. Reactorneutronen worden afgeremd door tegen lichte kernen te botsen, waarbij ze elke keer ongeveer dezelfde fractie van hun energie verliezen, dus elke sprong is hier even lang. Sommige worden onderweg door de pieken gevangen.</p>
  <div class="btns"><button class="btn" data-act="slow">Rem 10 neutronen af</button></div>
  <p>Wie erdoor komt, komt tot rust bij kamertemperatuur, 0,025 eV, de <b>thermische</b> energie, ver onder de eerste piek. Daar is de werkzame doorsnede, het oppervlak van de schijf, de som van de staarten van de resonanties, inclusief gebonden niveaus net onder nul; de staarten groeien als 1/<i>v</i> (<i>v</i> de snelheid van het neutron), dus de bodem stijgt naar links. De vangst onderweg omlaag wordt gemeten met de <b>resonantie-integraal</b>: de werkzame doorsnede boven 0,5 eV, waarbij elke energie met 1/<i>E</i> wordt gewogen.</p>
</div>
<div class="step">
  <h3>Alleen de statistiek is voorspelbaar</h3>
  <p>Elke rij is één ladder getrokken uit dezelfde vier getallen, met een schijf waarvan het oppervlak de werkzame doorsnede voor thermische vangst is. De haak reikt tot de piek die die waarde bepaalt, meestal de dichtstbijzijnde; de afstand ervan verschilt van ladder tot ladder, en de schijf schommelt met een factor tien of meer.</p>
  <div class="btns"><button class="btn" data-act="draw1">Trek een ladder</button><button class="btn ghost" data-act="more">Trek er 20</button></div>
  <p>Elke waarde valt in de stapel rechts. Voor een niet-gemeten kern is het antwoord een spreiding van waarden, geen enkel getal, en geen beter model kan die verkleinen. De resonantie-integraal, een som over veel pieken, spreidt minder. Waar niveaus meer dan ongeveer 10 keV uit elkaar liggen, zoals bij lichte kernen, ligt er geen dicht bij thermisch: vangst is daar direct, en de code weigert te antwoorden.</p>
  <div class="aside">In de code: <code>physics/resonance/ladder.py</code> (afstanden uit stochastische matrices, breedten volgens Porter–Thomas, werkzame doorsneden volgens Breit–Wigner, thermische vangst en resonantie-integraal over een ensemble), <code>ladder_statistics.py</code> (dezelfde wetten getoetst op gemeten ladders), <code>ensemble_runner.py</code>. Deze draaien naast de reactiemotor, niet erin.</div>
</div>`,
};
Object.assign(WT.L.labels, {
  // forest
  "{#} eV": "{#} eV", "+{#} eV": "+{#} eV",
  "height: peak capture (log) · width Γ ×{#}": "hoogte: piekvangst (log) · breedte Γ ×{#}",
  "peak height: capture cross section (log scale) · width: resonance width Γ, drawn {#}× wide": "piekhoogte: werkzame doorsnede voor vangst (log. schaal) · breedte: resonantiebreedte Γ, {#}× breder getekend",
  "D₀ {#} eV · S₀ {#}×{#}⁻⁴ · S₁ {#}×{#}⁻⁴ · ⟨Γγ⟩ {#} meV": "D₀ {#} eV · S₀ {#}×{#}⁻⁴ · S₁ {#}×{#}⁻⁴ · ⟨Γγ⟩ {#} meV",
  "s-wave (+ parity)": "s-golf (pariteit +)", "p-wave (− parity)": "p-golf (pariteit −)",
  "caught {#} times in {#} landings": "{#} keer ingevangen bij {#} landingen",
  "each peak: one level of the compound nucleus": "elke piek: één niveau van de compoundkern",
  "each peak: one level of the compound nucleus · about {#} eV apart": "elke piek: één niveau van de compoundkern · ongeveer {#} eV uit elkaar",
  // spacing
  "random positions (Poisson)": "willekeurige posities (Poisson)",
  "repelling levels (random-matrix)": "afstotende niveaus (stochastische matrices)",
  "two repelling sequences mixed": "twee afstotende reeksen gemengd",
  "clumps and gaps · ⟨r̃⟩ ≈ {#}": "klonten en gaten · ⟨r̃⟩ ≈ {#}",
  "evenly kept apart · ⟨r̃⟩ ≈ {#}": "gelijkmatig gescheiden · ⟨r̃⟩ ≈ {#}",
  "repulsion half hidden · ⟨r̃⟩ ≈ {#}": "afstoting half verborgen · ⟨r̃⟩ ≈ {#}",
  "clumps and gaps · spacing ratio ⟨r̃⟩ ≈ {#}": "klonten en gaten · afstandsverhouding ⟨r̃⟩ ≈ {#}",
  "evenly kept apart · spacing ratio ⟨r̃⟩ ≈ {#}": "gelijkmatig gescheiden · afstandsverhouding ⟨r̃⟩ ≈ {#}",
  "repulsion half hidden · spacing ratio ⟨r̃⟩ ≈ {#}": "afstoting half verborgen · afstandsverhouding ⟨r̃⟩ ≈ {#}",
  "⟨r̃⟩: {#} if random, {#} for random-matrix": "⟨r̃⟩: {#} bij willekeurig, {#} bij stochastische matrices",
  "same average spacing in every row · ⟨r̃⟩: {#} if random, {#} for random-matrix": "zelfde gemiddelde afstand in elke rij · ⟨r̃⟩: {#} bij willekeurig, {#} bij stochastische matrices",
  // Porter-Thomas
  "height: neutron width Γn (linear)": "hoogte: neutronbreedte Γn (lineair)",
  "peak height: neutron width Γn, linear scale": "piekhoogte: neutronbreedte Γn, lineaire schaal",
  "yellow: γ width": "geel: γ-breedte",
  "yellow cap: γ width, nearly the same on every peak": "geel kapje: γ-breedte, bijna gelijk op elke piek",
  "equal widths: every peak the average": "gelijke breedten: elke piek het gemiddelde",
  "rolled widths": "gegooide breedten", "pile of rolled widths": "stapel gegooide breedten",
  "× average": "× gemiddelde", "(in units of the average)": "(in eenheden van het gemiddelde)",
  "dashed: Porter–Thomas": "gestippeld: Porter–Thomas", "dashed: the Porter–Thomas law": "gestippeld: de wet van Porter–Thomas",
  "bell-curve number x": "klokkrommegetal x",
  "x = {#}  →  x² = {#}": "x = {#}  →  x² = {#}",
  "press Roll a width": "druk op Gooi een breedte",
  // thermal
  "bound level {#} eV": "gebonden niveau {#} eV",
  "a bound level at {#} eV: its tail lifts this end": "een gebonden niveau bij {#} eV: zijn staart tilt dit uiteinde op",
  "resonance integral ≈ {#} b": "resonantie-integraal ≈ {#} b",
  "resonance integral above {#} eV ≈ {#} b": "resonantie-integraal boven {#} eV ≈ {#} b",
  "{#}/v": "{#}/v",
  "caught by a peak on the way down: {#} · reached thermal: {#}": "onderweg door een piek gevangen: {#} · thermisch bereikt: {#}",
  "each hop: one bounce, the same fraction of energy lost": "elke sprong: één botsing, steeds dezelfde fractie energie kwijt",
  // ensemble
  "thermal neutron": "thermisch neutron",
  "σ disc": "σ-schijf", "disc area = σ at {#} eV": "schijfoppervlak = σ bij {#} eV",
  "{#}k": "{#}k",
  "thermal σ (b)": "thermische σ (b)", "thermal σ, barns": "thermische σ, barn",
  "{#} ladders · thermal ×{#} · res. integral ×{#}": "{#} ladders · thermisch ×{#} · res.-integraal ×{#}",
});
// labels that carry a cross section printed as "12 b" or "3.4k b"
(function () {
  const L = WT.L.labels;
  for (const b of ["{#} b", "{#}k b"]) {
    L[b] = b;
    L[`σ ≈ ${b} · caught on {#} % of landings`] = `σ ≈ ${b} · ingevangen bij {#} % van de landingen`;
    L[`σ ≈ ${b} · caught on <{#} % of landings`] = `σ ≈ ${b} · ingevangen bij <{#} % van de landingen`;
    L[`thermal, {#} eV: σ ≈ ${b}`] = `thermisch, {#} eV: σ ≈ ${b}`;
    L[`{#} ladders · thermal σ median ${b}, middle two thirds ×{#} · resonance integral only ×{#}`] =
      `{#} ladders · thermische σ mediaan ${b}, middelste twee derde ×{#} · resonantie-integraal slechts ×{#}`;
  }
})();
