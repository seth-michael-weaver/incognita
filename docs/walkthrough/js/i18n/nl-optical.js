/* Dutch (Nederlands): optical (Hoofdstuk 14, het optisch model, opgelost) */
WT.L.ch.optical = {
  num: "Hoofdstuk 14", title: "Het optisch model, opgelost", short: "Optisch model, opgelost",
  lead: "Hoofdstuk 2 tekende de optische potentiaal als een troebele glazen bol. Hier staat ze zoals de motor haar gebruikt: een globale parametrisatie, een radiale schrödingervergelijking die stap voor stap wordt geïntegreerd, en een aansluitvoorwaarde die de golf omzet in transmissiecoëfficiënten.",
  html: `
<div class="step">
  <h3>De potentiaal van Koning–Delaroche</h3>
  <p>Voor neutronen en protonen op sferische trefkernen is de standaard de potentiaal van <b>Koning–Delaroche</b> (KD03): Woods–Saxon-vormen waarvan de diepten glad veranderen met de energie en met de massa en het neutronenoverschot van de trefkern, volgens een globale formule of, voor de kernen die KD03 één voor één heeft gefit, zoals ijzer-56, volgens een lokale fit van dezelfde vorm. De afbeelding gebruikt de globale formule voor neutronen op ijzer-56. De reële put (blauw) bindt; de imaginaire delen (rood) absorberen, in het volume en, vooral bij lage energie, in een dunne schil aan het oppervlak.</p>
  <div class="ctl"><label for="op-e">Neutronenergie (MeV)</label><input id="op-e" type="range" data-bind="E" min="0.1" max="80" step="0.1" value="5"><output data-show="E" data-fmt="1"></output></div>
  <div class="formula">U(r) = −V<sub>V</sub> f(r) − iW<sub>V</sub> f(r) + 4i a<sub>D</sub>W<sub>D</sub> df<sub>D</sub>/dr + 2(V<sub>so</sub> + iW<sub>so</sub>) (1/r) df<sub>so</sub>/dr ⟨l·σ⟩</div>
  <p>De testneutronen steken over bij de energie die je instelt en vervagen waar de absorptie toeslaat: hun gemiddelde vrije weglengte is ħ<i>v</i>/2|<i>W</i>|. Elke diepte is een functie van <i>E</i> − <i>E</i><sub>F</sub>, gemeten vanaf de fermi-energie: de reële diepte daalt langzaam, de oppervlakte-absorptie <i>W</i><sub>D</sub> piekt rond 10 MeV, en de volume-absorptie <i>W</i><sub>V</sub> groeit gestaag tot ze het overneemt, hier boven ongeveer 45 MeV.</p>
</div>
<div class="step">
  <h3>De radiale vergelijking integreren</h3>
  <p>Elke partiële golf gehoorzaamt aan haar eigen radiale vergelijking. De motor integreert die vanaf <i>r</i> = 0 naar buiten met de <b>methode van Numerov</b>, een driepuntsregel die nauwkeurig is tot op de zesde macht van de stapgrootte, door de volledige complexe potentiaal heen.</p>
  <div class="formula">u″<sub>lj</sub>(r) = [ l(l+1)/r² + (2μ/ħ²) U<sub>lj</sub>(r) − k² ] u<sub>lj</sub>(r)</div>
  <div class="ctl"><label for="op-l">Partiële golf l</label><input id="op-l" type="range" data-bind="L" min="0" max="10" step="1" value="1" data-instant><output data-show="L" data-fmt="0"></output></div>
  <div class="ctl"><label for="op-e2">Neutronenergie (MeV)</label><input id="op-e2" type="range" data-bind="E" min="0.1" max="80" step="0.1" value="5"><output data-show="E" data-fmt="1"></output></div>
  <p>De doorgetrokken lijn is de golf in de tijd, Re[<i>u</i> e<sup>−iωt</sup>]; de gestippelde lijn is de vrije golf, alsof de kern er niet was. Binnen de put is de golf korter (het neutron is sneller) en kleiner (geabsorbeerd); erbuiten komt ze in fase verschoven terug.</p>
</div>
<div class="step">
  <h3>Van de golf naar S en T</h3>
  <p>Voorbij ongeveer 12 fm is de potentiaal verdwenen en moet de golf een mengsel zijn van een inkomende en een uitgaande vrije golf, <i>u</i> ∝ <i>H</i><sup>−</sup> − <i>S</i> <i>H</i><sup>+</sup>. Door de geïntegreerde <i>u</i> bij twee stralen aan te sluiten ligt het element <i>S<sub>lj</sub></i> van de <b>S-matrix</b> vast: de uitgaande amplitude, met haar fase.</p>
  <div class="btns"><button class="btn ghost" data-act="abs" aria-pressed="false">Zet absorptie uit</button></div>
  <div class="formula">S<sub>lj</sub> = η<sub>lj</sub> e<sup>2iδ<sub>lj</sub></sup> ,  T<sub>lj</sub> = 1 − |S<sub>lj</sub>|²</div>
  <p>De stip is <i>S</i> in het complexe vlak, binnen de eenheidscirkel; haar spoor is het pad dat ze aflegt terwijl de energie van 0,1 naar 40 MeV loopt. Zonder absorptie is |<i>S</i>| = 1: de stip loopt over de cirkel, de golf verandert alleen van fase, en <i>T</i> = 0. Hoe ver de stip binnen de cirkel ligt, is wat de compoundkern en elke andere reactie ontvangen.</p>
</div>
<div class="step">
  <h3>Spin-baan splitst j</h3>
  <p>De <b>spin-baanterm</b> is aantrekkend voor <i>j</i> = <i>l</i> + ½ en afstotend voor <i>j</i> = <i>l</i> − ½. Hij is klein, een paar MeV aan het oppervlak, maar hij drijft de twee transmissies van elke <i>l</i> uit elkaar, het sterkst bij de partiële golf die het oppervlak schampt.</p>
  <div class="ctl"><label for="op-e3">Neutronenergie (MeV)</label><input id="op-e3" type="range" data-bind="E" min="0.1" max="80" step="0.1" value="5"><output data-show="E" data-fmt="1"></output></div>
  <div class="btns"><button class="btn ghost" data-act="so" aria-pressed="false">Zet spin-baan uit</button></div>
  <p>Hauser–Feshbach (hoofdstuk 13) gebruikt de twee afzonderlijk; opgeteld met hun gewichten, (<i>l</i>+1)<i>T</i><sub>l,l+½</sub> + <i>l</i> <i>T</i><sub>l,l−½</sub>, geven ze een vrijwel ongewijzigde werkzame doorsnede voor reactie. Daarom leggen totale werkzame doorsneden de sterkte van de spin-baanterm nauwelijks vast en zijn polarisatiedata nodig.</p>
</div>
<div class="step">
  <h3>De werkzame doorsneden</h3>
  <p>Optellen over de partiële golven geeft de observabelen waaraan de potentiaal wordt gefit. De werkzame doorsnede voor reactie telt de verwijderde flux, de totale werkzame doorsnede volgt uit de voorwaartse amplitude, en hun verschil is de vormelastische verstrooiing (shape elastic).</p>
  <div class="formula">σ<sub>R</sub> = (π/k²) Σ<sub>l</sub> [(l+1)T<sub>l,l+½</sub> + l T<sub>l,l−½</sub>] ,  σ<sub>tot</sub> = (2π/k²) Σ<sub>lj</sub> (j+½)(1 − Re S<sub>lj</sub>)</div>
  <div class="ctl"><label for="op-e4">Neutronenergie (MeV)</label><input id="op-e4" type="range" data-bind="E" min="0.2" max="50" step="0.1" value="5"><output data-show="E" data-fmt="1"></output></div>
  <p>KD03 werd aan zulke data gefit voor veel kernen, van 1 keV tot 200 MeV; de totale werkzame doorsnede van ijzer, tussen 3,5 en 4 b bij een paar MeV en 2,5 b bij 14 MeV, komt eruit tot op ongeveer 5 procent zonder aanpassing aan deze kern, de brede maxima inbegrepen: die zijn de grootte van de kern, afgezet tegen de golflengte van het neutron.</p>
</div>
<div class="step">
  <h3>De kant van de lage energieën</h3>
  <p>Onder een paar keV telt alleen de s-golf, en <i>T</i><sub>0</sub> groeit als √<i>E</i>: een helling van een half in deze log-loggrafiek. De constante is de <b>sterktefunctie</b> <i>S</i><sub>0</sub> = <i>T</i><sub>0</sub>/(2π√<i>E</i>), met <i>E</i> in eV, dezelfde grootheid die resonantieanalyses meten als Σ Γ<sub>n</sub><sup>0</sup>/Δ<i>E</i>.</p>
  <p>Een globale potentiaal wordt vooral bij MeV-energieën gefit, en de kant van de lage energieën is zijn zwakste punt. Voor ijzer-56 geeft deze potentiaal <i>S</i><sub>0</sub> ≈ 5,5 × 10⁻⁴, en de lokale fit van KD03 bijna hetzelfde, terwijl de gemeten waarde (RIPL) 2,3 ± 0,6 × 10⁻⁴ is: ijzer ligt dicht bij de top van de 3s-grootteresonantie rond <i>A</i> ≈ 55, waar <i>S</i><sub>0</sub> het gevoeligst is voor de potentiaal. Daarom zijn de gemeten <i>S</i><sub>0</sub> en <i>S</i><sub>1</sub> een aparte, optionele invoer voor de motor.</p>
  <div class="aside">In de code: <code>omp/parameters.py</code> (KD03 en de andere globale potentialen), <code>omp/potential.py</code> (de radiale vormfactoren), <code>omp/schrodinger.py</code> (integratie volgens Numerov en aansluiting, met coulombfuncties volgens de methode van Steed voor geladen deeltjes; het vervangt ECIS voor sferische trefkernen en is getoetst aan de T<sub>lj</sub> van ECIS), <code>ecis/</code> (de port van gekoppelde kanalen voor vervormde trefkernen), <code>omp/sfunc.py</code> (optioneel: gemeten S₀, S₁). De afbeelding lost de vergelijking zelf op, niet-relativistisch, voor neutronen op ijzer-56.</div>
</div>`,
};
(function () {
  const L = {
    // scene 1: the potential
    "{#} fm": "{#} fm", "{#} MeV": "{#} MeV", "{#} keV": "{#} keV", "{#} eV": "{#} eV",
    "real well, depth {#} MeV": "reële put, diepte {#} MeV",
    "surface absorption, peak {#} MeV": "oppervlakte-absorptie, piek {#} MeV",
    "volume absorption {#} MeV": "volume-absorptie {#} MeV",
    "spin–orbit for l = {#}, j = {#}/{#}: {#} MeV": "spin-baan voor l = {#}, j = {#}/{#}: {#} MeV",
    "E = {#} MeV": "E = {#} MeV",
    "real": "reëel", "volume": "volume", "surface": "oppervlak",
    "depths (MeV) against energy (MeV)": "diepten (MeV) tegen energie (MeV)",
    // scene 2: the radial wave
    "potential: real (blue), imaginary (red)": "potentiaal: reëel (blauw), imaginair (rood)",
    "nuclear surface": "kernoppervlak",
    "l = {#}, j = {#}+½ · E = {#} MeV · |S| = {#} · δ = {#}° · T = {#}": "l = {#}, j = {#}+½ · E = {#} MeV · |S| = {#} · δ = {#}° · T = {#}",
    "solid: the wave now · shaded: its size |u| · dashed: free wave": "doorgetrokken: de golf nu · gearceerd: haar grootte |u| · gestippeld: vrije golf",
    // scene 3: S in the complex plane
    "Re S": "Re S", "Im S": "Im S",
    "|S| = {#}: nothing absorbed": "|S| = {#}: niets geabsorbeerd",
    "l = {#}, j = {#}+½ · E = {#} MeV": "l = {#}, j = {#}+½ · E = {#} MeV",
    "|S| = {#} · T = {#} − |S|² = {#}": "|S| = {#} · T = {#} − |S|² = {#}",
    "l = {#}, j = {#}+½": "l = {#}, j = {#}+½",
    "|S| = {#}": "|S| = {#}",
    "T = {#} − |S|² = {#}": "T = {#} − |S|² = {#}",
    "trail: S as E runs {#} → {#} MeV": "spoor: S voor E = {#} → {#} MeV",
    "no absorption: S stays on the circle": "geen absorptie: S blijft op de cirkel",
    // scene 4: spin-orbit
    "T = {#}": "T = {#}", "l": "l",
    "hollow: j = l − ½ · solid: j = l + ½": "hol: j = l − ½ · dicht: j = l + ½",
    "hollow (purple): j = l − ½ · solid (blue): j = l + ½": "hol (paars): j = l − ½ · dicht (blauw): j = l + ½",
    "grazing l ≈ kR = {#}": "schampend: l ≈ kR = {#}",
    // scene 5: the cross sections
    "n + ⁵⁶Fe, KD{#}, computed here": "n + ⁵⁶Fe, KD{#}, hier berekend",
    // scene 6: T0 at low energy
    "T₀ (s-wave)": "T₀ (s-golf)",
    "T₁ (p-wave, j = {#}/{#}): slope {#}/{#}": "T₁ (p-golf, j = {#}/{#}): helling {#}/{#}",
    "dashed: {#}πS₀√E, slope ½": "gestippeld: {#}πS₀√E, helling ½",
    "S₀ = {#} × {#}⁻⁴ from this potential": "S₀ = {#} × {#}⁻⁴ uit deze potentiaal",
  };
  // mean free path: each length is a number or "> 100"
  for (const a of ["{#}", "> {#}"]) for (const b of ["{#}", "> {#}"])
    L[`mean free path: ${a} fm at the surface, ${b} fm in the centre`] = `gemiddelde vrije weglengte: ${a} fm aan het oppervlak, ${b} fm in het midden`;
  // labels that carry a cross section printed as "12 b" or "3.4k b"
  for (const b of ["{#} b", "{#}k b"]) {
    L[b] = b;
    L[`total ${b}`] = `totaal ${b}`;
    L[`reaction ${b}`] = `reactie ${b}`;
    L[`shape elastic ${b}`] = `vormelastisch ${b}`;
    L[`reaction cross section ${b} (spin–orbit off)`] = `werkzame doorsnede voor reactie ${b} (spin-baan uit)`;
    for (const b2 of ["{#} b", "{#}k b"])
      L[`reaction cross section ${b} (without spin–orbit ${b2})`] = `werkzame doorsnede voor reactie ${b} (zonder spin-baan ${b2})`;
  }
  Object.assign(WT.L.labels, L);
})();
Object.assign(WT.L.glossary, {
  koningDelaroche: {
    term: "Potentiaal van Koning–Delaroche", aliases: ["Koning–Delaroche", "KD03"],
    short: "De globale optische potentiaal voor neutronen en protonen van A. J. Koning en J.-P. Delaroche (2003), van 1 keV tot 200 MeV en voor massa's van 24 tot 209.",
    more: "Diepten, stralen en diffusiteiten zijn gladde functies van energie, massa en neutronenoverschot, eenmalig gefit aan een grote verzameling gemeten werkzame doorsneden en hoekverdelingen. Ze is de standaard voor nucleonen in TALYS en in de motor.",
    chapter: "optical",
  },
  numerov: {
    term: "Methode van Numerov", aliases: ["methode van Numerov", "Numerov"],
    short: "Een driepuntsregel voor het integreren van tweede-ordevergelijkingen zonder term met de eerste afgeleide, zoals de radiale schrödingervergelijking, met een fout van de orde h⁶ per stap.",
    formula: "(1 − h²Q_n+1/12) u_n+1 = 2(1 + 5h²Q_n/12) u_n − (1 − h²Q_n−1/12) u_n−1",
    chapter: "optical",
  },
  sMatrix: {
    term: "S-matrix", aliases: ["S-matrix"],
    short: "De amplitudes die inkomende en uitgaande golven met elkaar verbinden; voor elastische verstrooiing in één partiële golf is dat één complex getal S = η e^(2iδ).",
    more: "|S| = 1 betekent dat er niets wordt geabsorbeerd en alleen de fase δ verandert; het tekort 1 − |S|² is de transmissiecoëfficiënt, de flux die in reacties verdwijnt.",
    chapter: "optical",
  },
  spinOrbit: {
    term: "Spin-baanterm", aliases: ["spin-baanterm", "spin-baankoppeling", "spin-baan"],
    short: "Het deel van de kernpotentiaal dat ervan afhangt of de spin van het nucleon parallel of antiparallel staat aan zijn baanimpulsmoment.",
    more: "Hij is aantrekkend voor j = l + ½ en afstotend voor j = l − ½, met een piek aan het kernoppervlak. Dezelfde wisselwerking levert de magische getallen van het schillenmodel.",
    chapter: "optical",
  },
});
